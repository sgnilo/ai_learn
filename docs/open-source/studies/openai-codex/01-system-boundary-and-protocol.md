---
layout: default
title: "openai/codex 01 · 系统边界与协议骨架"
---

# openai/codex 01 · 系统边界与协议骨架

返回：[openai/codex 源码学习路线](../openai-codex.md) / [开源项目研读](../../00-overview.md) / [Progress](../../../progress.md)

全景图：[openai/codex 真实架构全景图](./00-real-architecture-map.md)

## 本单元目标

沿当前 TUI 中一次普通文本输入，解释它如何从界面进入 App Server、转换成 Core command、启动异步 turn，并最终以事件流返回界面。

- 本地源码 revision：`2df67054232090af8d2fa197c46b994bc2b0dda1`
- 官方边界：[Codex Open Source](https://developers.openai.com/codex/open-source)
- 本单元终点：进入 `run_turn`，不在这里展开模型 sampling 和工具闭环。

## 先给结论

Codex 的一次用户输入不是“UI 调用一个阻塞函数，等模型答案返回”，而是三条相互关联、生命周期不同的路径：

| 路径 | 主要类型 | 结束条件 |
| --- | --- | --- |
| 宿主请求路径 | `turn/start` → `TurnStartParams` | App Server 返回 `TurnStartResponse`，表示输入已被 Core 接受并路由 |
| Core command 路径 | `Submission<Op::TurnInput>` | `TurnInputSubmission::{Started, Steered, NotSubmitted}` 通过 oneshot 返回 |
| 异步事件路径 | `Event<EventMsg>` → App Server notification | `TurnComplete` 或 `TurnAborted` 表示 turn 真正结束 |

最重要的区别是：**请求成功只表示 Core 接受了输入，不表示 Agent 已完成。** 真正的进度、模型输出、工具调用和完成状态都走异步事件流。

## 一张完整时序图

```text
User
  │ 输入文本
  ▼
TUI thread_routing
  │ AppServerSession::turn_start(TurnStartParams)
  ▼
App Server TurnRequestProcessor
  │ 校验 + v2 UserInput → core UserInput
  │ CodexThread::start_or_steer_turn(TurnInputRequest)
  ▼
SessionIo::submit_turn_input
  │ 生成 submission_id / turn_id
  │ tx_sub.send(Submission { Op::TurnInput, reply })
  ▼
submission_loop
  │ turn_input::handle(StartOrSteer)
  ├─ active regular turn ──→ steer_input ──→ Steered
  ├─ no active turn ───────→ spawn_task ──→ Started
  └─ incompatible state ──→ NotSubmitted
                                │
                                ▼
                     RegularTask::run
                       │ EventMsg::TurnStarted
                       │ run_turn(...)
                       │ EventMsg::Item*/Delta/...
                       ▼
                     on_task_finished
                       │ EventMsg::TurnComplete / TurnAborted
                       ▼
Session::send_event → rollout persistence → tx_event
                       │
                       ▼
App Server thread listener → bespoke event translation
                       │ ServerNotification::TurnStarted / TurnCompleted / ...
                       ▼
TUI event dispatch → ChatWidget 状态和渲染
```

图中有两个容易忽略的并发点：`submission_loop` 是 session 级后台 task；真正执行 turn 的 `RegularTask` 又是另一个 Tokio task。因此 Core 可以继续接收 interrupt、approval response 或 steer input，而不必等当前模型请求结束。

## 第 1 步：CLI 只负责选择宿主形态

入口是 [`main()`](/Users/bytedance/mind/codex/codex-rs/cli/src/main.rs:1040)。它通过 `clap` 解析顶层命令，再在 `cli_main` 中分流：

- 无子命令时进入 interactive TUI。
- `codex exec` 进入非交互 adapter。
- `codex app-server` 启动 JSON-RPC server。

默认交互路径最后调用 [`codex_tui::run_main`](/Users/bytedance/mind/codex/codex-rs/cli/src/main.rs:2612)。这里的架构含义不是“CLI 就是 Agent”，而是 CLI 负责选择哪个宿主 adapter；Agent 的 Thread、Session、Turn 和工具逻辑位于共享的 core。

## 第 2 步：当前 TUI 先构造 App Server 请求

当 TUI 判断这次输入应该启动新 turn 时，[`thread_routing.rs`](/Users/bytedance/mind/codex/codex-rs/tui/src/app/thread_routing.rs:741) 调用 `AppServerSession::turn_start`。

[`AppServerSession::turn_start`](/Users/bytedance/mind/codex/codex-rs/tui/src/app_server_session.rs:1179) 构造 `TurnStartParams`，其中不只有文本：

- `thread_id`：输入属于哪个长期 thread。
- `input`：文本、图片、skill mention 等用户输入项。
- `cwd`、workspace roots：本轮在哪个工作区执行。
- approval、sandbox、permissions：本轮安全边界。
- model、effort、collaboration mode：本轮及后续 turn 的 sticky settings。
- output schema：是否要求结构化最终输出。

这说明 `turn/start` 不是一个简单的 `prompt: String` API。它是宿主向 Agent runtime 提交的“输入 + 执行环境 + 策略快照”。

## 第 3 步：App Server 把外部协议转换为 Core 请求

[`TurnRequestProcessor::turn_start_inner`](/Users/bytedance/mind/codex/codex-rs/app-server/src/request_processors/turn_processor.rs:478) 主要完成五件事：

1. 通过 `thread_id` 找到 live `CodexThread`。
2. 校验输入长度与当前 thread 是否允许直接输入。
3. 把 App Server v2 的 `UserInput` 转成 Core `UserInput`。
4. 将 cwd、environment、permission、model 等字段整理成 `ThreadSettingsOverrides`。
5. 构造 `TurnInputRequest`，调用 [`CodexThread::start_or_steer_turn`](/Users/bytedance/mind/codex/codex-rs/core/src/codex_thread.rs:338)。

这里存在第一个稳定性边界：App Server v2 是外部 JSON-RPC wire contract，Core `TurnInputRequest` 是进程内协议。二者不直接复用同一类型，使外部兼容性不会反向绑死 Core 的内部组织。

## 第 4 步：`CodexThread` 是 façade，不是 Agent loop 本身

[`CodexThread`](/Users/bytedance/mind/codex/codex-rs/core/src/codex_thread.rs:202) 持有两部分：

- `Arc<Session>`：该 thread 的运行时状态和服务。
- `SessionIo`：command sender、event receiver 和 session-loop completion future。

`start_or_steer_turn` 先检查多 Agent 执行容量，再交给 `SessionIo::submit_turn_input`。因此 `CodexThread` 的主要作用是给宿主提供一个受控 façade：宿主不需要直接拿 `Session` 锁、active task 或 rollout writer。

把 TUI 换成 App Server client、SDK 或测试 harness 时，替换的是 `CodexThread` 上方的 adapter；`Session` 下方的 Agent runtime 可以继续复用。

## 第 5 步：一次提交同时使用 channel 和 oneshot

[`SessionIo::submit_turn_input`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:848) 做了几件关键的事：

```text
new_submission_id()              // UUIDv7
oneshot::channel()               // 只返回路由决定
Submission {
  id,
  op: Op::TurnInput { request, mode, reply },
  trace,
}
tx_sub.send(submission)
reply_rx.await
```

这里组合了两种通信机制：

- `tx_sub` 是多生产者到单 session loop 的有序 command channel。
- `oneshot` 只回答这条输入是 `Started`、`Steered` 还是 `NotSubmitted`。

oneshot 不承载最终 Agent 答案。源码中的 [`TurnInputSubmission`](/Users/bytedance/mind/codex/codex-rs/protocol/src/turn_input.rs:161) 明确说明，`Started/Steered` 甚至不等待 prompt hook、历史更新、rollout persistence 或 sampling。

这是一种“两阶段语义”：

1. **admission / routing**：Core 是否接受输入，以及它属于哪个 turn。
2. **execution / lifecycle**：接受后发生了什么，最终是否完成。

## 第 6 步：`Op` 是 Session 的 command vocabulary

[`Op`](/Users/bytedance/mind/codex/codex-rs/protocol/src/protocol.rs:545) 是提交给一个 live Session 的命令集合。普通文本最终成为：

```text
Op::TurnInput {
  request: TurnInputRequest,
  mode: StartOrSteer,
  reply: oneshot sender,
}
```

同一个队列中还有 `Interrupt`、approval response、`Compact`、`ThreadRollback` 和 `Shutdown` 等 command。这一点很重要：Agent 运行期间的用户决策不是旁路修改共享状态，而是继续通过同一个 session command boundary 进入。

`Op` 不等于用户动作，也不等于 JSON-RPC method。它是 Core 为 Session 定义的进程内 command vocabulary。

## 第 7 步：`submission_loop` 串行决定如何处理 command

`Session::spawn` 会把 [`submission_loop`](/Users/bytedance/mind/codex/codex-rs/core/src/session/handlers.rs:514) 启动为独立 Tokio task。它持续从 `rx_sub` 读取 `Submission`，再对 `Op` 做 dispatch。

对于 `Op::TurnInput`，它调用 [`turn_input::handle`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn_input.rs:140)，然后把 typed result 发回 oneshot。

command dispatch 是串行的，因此“是否已有 active turn”“本次是 start 还是 steer”等状态转换有一个明确的裁决点。真正耗时的模型和工具执行不会阻塞这个 loop，而是在下一层独立 task 中运行。

## 第 8 步：`StartOrSteer` 是并发输入的核心语义

[`start_or_steer`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn_input.rs:166) 先尝试把输入注入 active turn：

- 存在可 steer 的 regular turn：输入进入 pending-input queue，返回同一个 active `turn_id`。
- 没有 active turn：创建 `TurnContext`，以本次 `submission_id` 作为 `turn_id`，再启动 `RegularTask`。
- active turn 是 review/compact、schema 不兼容或输入为空：返回带原因的 `NotSubmitted`。

[`steer_input`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn_input.rs:477) 在持有 active-turn 锁时检查 turn 类型、expected turn ID、output schema 和输入内容，从而避免并发输入同时误判为“应该新建 turn”。

现有集成测试 [`turn_input_submission_reports_started_and_steered_for_concurrent_submissions`](/Users/bytedance/mind/codex/codex-rs/core/tests/suite/turn_input_submission.rs:153) 同时提交两条消息，断言结果必须恰好是：一条 `Started`，另一条 `Steered`，而且二者指向同一 `turn_id`。随后测试确认第二次模型请求同时包含两条消息。

## 第 9 步：routing ack 先返回，turn task 在后台继续

新 turn 会进入 [`Session::spawn_task`](/Users/bytedance/mind/codex/codex-rs/core/src/tasks/mod.rs:272) 和 [`start_task`](/Users/bytedance/mind/codex/codex-rs/core/src/tasks/mod.rs:284)：

1. 建立 cancellation token 和 active-turn state。
2. 记录 turn start timing、token baseline 和 lineage。
3. 创建覆盖整个 turn 生命周期的 tracing span。
4. `tokio::spawn` 一个真正运行 `SessionTask` 的 task。
5. 把 `RunningTask` 放进 `active_turn`。

`start_or_steer` 随后就能返回 `Started`，App Server 也会立即返回一个 `status = InProgress` 的 `TurnStartResponse`。此时模型可能还没有开始 sampling。

## 第 10 步：`TurnStarted` 与 `run_turn` 的顺序

[`RegularTask::run`](/Users/bytedance/mind/codex/codex-rs/core/src/tasks/regular.rs:39) 先发送 `EventMsg::TurnStarted`，然后解析 startup prewarm，最后调用 [`run_turn`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:153)。

测试 [`regular_turn_emits_turn_started_with_trace_id_without_waiting_for_startup_prewarm`](/Users/bytedance/mind/codex/codex-rs/core/src/session/tests.rs:532) 刻意让 prewarm 一直等待，却要求客户端仍能先收到 `TurnStarted`。这保证 UI 可以及时进入“执行中”，不会因为模型连接预热而看起来卡死。

从这里开始，`run_turn` 才会处理上下文、hooks、skills/plugins、Responses sampling 和工具 follow-up；这是后续主题 2～4 的范围。

## 第 11 步：`EventMsg` 是 Core 的事实流

[`EventMsg`](/Users/bytedance/mind/codex/codex-rs/protocol/src/protocol.rs:1296) 描述 Core 已经发生或正在等待的事实，例如：

- 生命周期：`TurnStarted`、`TurnComplete`、`TurnAborted`。
- 输出：item started/completed、agent-message delta、reasoning delta。
- 工具：exec begin/output/end、MCP call、patch、image 等。
- 人机协作：approval request、request-user-input、permissions request。
- 状态：token count、context compacted、warning/error。

command 与 event 的方向相反：`Op::ExecApproval` 是宿主把审批结果送回 Core；`EventMsg::ExecApprovalRequest` 一类事件则是 Core 请求宿主做决定。这种成对设计允许 Agent 在一个 turn 中暂停等待外部输入，而不破坏主循环。

## 第 12 步：事件先持久化，再投递给宿主

[`Session::send_event`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:1917) 用当前 `turn_context.sub_id` 构造 `Event.id`，并处理 tracing、legacy event 和 parent-agent notification。

随后 [`send_event_raw_with_persistence`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:2152)：

1. 让 MCP runtime 观察事件。
2. 将 `EventMsg` 作为 rollout item 持久化。
3. 更新 protocol trace。
4. 通过 `tx_event` 投递。

[`deliver_event_raw`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:2165) 还会更新 watch channel 中的 `AgentStatus`。所以事件流同时服务于 UI、持久化、恢复、状态观察和多 Agent 协作，不只是打印日志。

## 第 13 步：App Server 再做一次事件协议转换

App Server 的 thread listener 在 [`thread_lifecycle.rs`](/Users/bytedance/mind/codex/codex-rs/app-server/src/request_processors/thread_lifecycle.rs:307) 持续调用 `conversation.next_event()`。

Core event 随后进入 [`apply_bespoke_event_handling`](/Users/bytedance/mind/codex/codex-rs/app-server/src/bespoke_event_handling.rs:143)：

- [`EventMsg::TurnStarted`](/Users/bytedance/mind/codex/codex-rs/app-server/src/bespoke_event_handling.rs:159) 转成 App Server v2 `TurnStartedNotification`。
- [`EventMsg::TurnComplete`](/Users/bytedance/mind/codex/codex-rs/app-server/src/bespoke_event_handling.rs:189) 汇总 turn status、error、items，再转成 `TurnCompletedNotification`。
- Core 的细粒度 item/delta/tool events 也分别转成稳定的 v2 notification。

因此不能把 `EventMsg` 直接等同于所有客户端看到的 wire format。App Server 是 anti-corruption layer：它把 Core 内部事件重组为面向宿主的 Thread / Turn / Item API。

TUI 最后在 [`chatwidget/protocol.rs`](/Users/bytedance/mind/codex/codex-rs/tui/src/chatwidget/protocol.rs:62) 消费 `TurnStarted` / `TurnCompleted` 等 notification，更新 ChatWidget 状态并触发渲染。

## 四种 ID 不要混淆

| ID | 产生位置 | 作用 |
| --- | --- | --- |
| JSON-RPC `request_id` | App Server client | 匹配一次 `turn/start` 请求与响应 |
| `thread_id` | Thread 创建时 | 标识跨多个 turn 的长期会话 |
| `submission_id` | `SessionIo` | 标识进入 session command queue 的一次提交 |
| `turn_id` | Core routing | 新 turn 通常复用启动它的 `submission_id`；steer 则返回已有 active turn ID |

`Event.id` 使用 `turn_context.sub_id`，所以 turn 内的异步事件能够关联到同一 turn。App Server notification 通常再同时携带 `thread_id`，让多 thread 客户端正确路由。

## 为什么不直接调用 `run_turn`

如果 UI 直接 `await run_turn(prompt)`，会立刻遇到这些问题：

- 无法在模型执行期间有序处理 interrupt、approval 和 steer。
- UI、exec、App Server、SDK 都要理解 Core 内部状态与锁。
- 请求返回值无法同时表达“已接受”“持续输出”“等待用户”“已完成”。
- turn 中途崩溃时，事件、持久化记录和 UI 状态难以对齐。
- 多个并发输入会竞争 active-turn 状态，缺少统一裁决点。

Codex 用 command queue + task + event stream 把这些职责拆开：submission loop 决定状态转换，turn task 执行长耗时工作，event stream 发布事实。

## 一次无工具 turn 的最小事件序列

忽略 session 初始化和兼容事件后，可以先记成：

```text
turn/start response: InProgress       // 请求确认，不是完成
turn/started notification
item/started: user message
item/completed: user message
item/started: agent message
agentMessage/delta: ...               // 可能多次
item/completed: agent message
turn/completed notification
```

如果中间出现工具调用，这个序列会插入 tool item、approval 和命令输出事件，并可能触发多次模型 sampling，但 turn ID 不变。

## 设计取舍

### 1. 双协议层换取边界稳定性

Core `Op/EventMsg` 与 App Server v2 protocol 有转换成本，但避免了内部实现变动直接破坏外部 SDK/UI。

### 2. admission ack 换取低耦合

调用方需要同时管理 request response 和 notification stream，复杂度更高；收益是长 turn 不占用一个“最终答案 RPC”，并且能够 steer、interrupt、审批和流式展示。

### 3. session command 串行、turn 执行并发

串行 command loop 让 active-turn 状态转换更容易推理；独立 turn task 又避免长耗时工作阻塞控制命令。

### 4. event 先持久化再投递

这增加 I/O 和 store 设计复杂度，但让 resume、审计和 UI 重放共享同一条事实来源。

## 常见误区

- `CodexThread::submit` 成功，不代表 turn 成功完成。
- `TurnStartResponse.status = InProgress` 不是 `TurnStarted` 事件的替代品。
- `Op` 是 Core command，不是 App Server JSON-RPC method。
- `EventMsg` 是 Core event，不一定是客户端最终看到的 notification shape。
- 第二条用户输入不一定创建第二个 turn；`StartOrSteer` 可能把它注入当前 turn。
- `CodexThread` 是受控 façade；真正的 mutable runtime state 在 `Session`，长任务在 `SessionTask`。

## 源码验证建议

先做两个聚焦验证，不编译整个 workspace：

1. 运行 `codex-core` 中 concurrent turn-input submission 测试，验证“一条 Started、一条 Steered、相同 turn ID”。
2. 运行 regular-turn startup 测试，验证 `TurnStarted` 不等待模型 prewarm。

对应证据：

- [`turn_input_submission.rs:153`](/Users/bytedance/mind/codex/codex-rs/core/tests/suite/turn_input_submission.rs:153)
- [`session/tests.rs:532`](/Users/bytedance/mind/codex/codex-rs/core/src/session/tests.rs:532)

## 复述检查

完成本单元后，应能不看源码回答：

1. 为什么 `turn/start` 返回成功时模型可能还没开始请求？
2. `tx_sub`、oneshot reply 和 `tx_event` 分别承载什么？
3. 两条并发用户输入为什么不会同时创建两个 turn？
4. 为什么 App Server 不直接把 `EventMsg` 原样暴露给 SDK？
5. `submission_id` 在 Started 和 Steered 两条分支中的命运有何不同？

## 下一步

运行两个聚焦测试并记录观察，然后进入主题 2，继续拆解 `Thread → Session → Turn → sampling request` 四层生命周期。
