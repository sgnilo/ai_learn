---
layout: default
title: "openai/codex 源码学习路线"
---

# openai/codex 源码学习路线

返回：[开源项目研读](../00-overview.md) / [通用研读路线](../roadmap.md) / [Progress](../../progress.md)

## 研读目标与版本

- 项目：[openai/codex](https://github.com/openai/codex)
- 官方定位：[Codex Open Source](https://developers.openai.com/codex/open-source)
- 本地仓库：[`/Users/bytedance/mind/codex`](/Users/bytedance/mind/codex/README.md)
- 本地基线 revision：`2df67054232090af8d2fa197c46b994bc2b0dda1`（工作区干净，2026-08-24）
- 在线源码镜像：[`40b7560169c7274147a47f9b0c75db89fe016d34`](https://github.com/openai/codex/tree/40b7560169c7274147a47f9b0c75db89fe016d34)（比本地基线多 1 个提交，仅用于分享链接）
- 固定日期：2026-08-24
- 首轮目标：读通本地 Codex agent harness 的一条完整纵向链路，并理解工具、安全和持久化如何嵌入 agent loop。

官方开源范围包括 Codex CLI、Codex SDK 和 Codex App Server；IDE extension 与 Codex cloud 不开源。因此本路线只解释能够从仓库源码验证的本地 runtime，不尝试反推云端调度或闭源 UI。

### 本地源码标注约定

- 每个主题先给出可点击的本地文件与关键符号行；它们是本路线的主要证据。
- 行号锁定到本地 revision `2df6705`。仓库更新后若跳转偏移，以符号名重新搜索，不把旧行号当作接口契约。
- 在线 GitHub 链接用于跨设备分享；如果在线快照和本地实现有差异，以本地 revision 的代码与测试为准。
- 阅读顺序遵循“调用方 → 协议/trait → 实现 → 测试”，不要把目录列表当作架构。

## 为什么按架构主干学习

当前仓库是大型 monorepo，`codex-rs/` 下包含大量 Rust crate。按目录逐个阅读会失去控制流，也很难判断哪些模块属于核心 Agent、哪些只是平台适配。

首轮以这条主干作为阅读坐标：

```text
CLI / TUI / App Server / SDK
            │
            ▼
      Op / EventMsg protocol
            │
            ▼
CodexThread → Session → submission_loop → run_turn
                                      │
                                      ▼
                           ModelClientSession::stream
                                      │
                         ResponseEvent / ResponseItem
                                      │
                                      ▼
                    ToolRouter → ToolRegistry → Handler
                                      │
                    approval → policy → sandbox → process
                                      │
                                      ▼
                       tool result 回灌模型，继续采样
                                      │
                    rollout / thread-store / SQLite state
```

这是一张需要用源码逐步验证的学习地图，不代替真实调用链证据。

完整版本：[openai/codex 真实架构全景图](./openai-codex/00-real-architecture-map.md)。

## 阅读边界

首轮重点：

- `codex-rs/cli`、`protocol`、`core`
- `tools`、`sandboxing`、`rollout`、`thread-store`、`state`
- `app-server`、`app-server-protocol`
- `sdk/typescript`，再对照 `sdk/python`

首轮暂缓：

- TUI 的渲染、主题、Markdown 排版和快捷键细节
- 登录、模型 catalog、云任务和各平台安装器的完整实现
- 所有 MCP、plugin 和 remote environment 变体
- Bazel 与跨平台发布流水线的全部细节

`codex-cli/` 主要承担 npm 分发与启动包装；Agent 核心以 `codex-rs/` 为主，不应从旧名称或包装目录开始深挖。

## Rust 最小前置

不先独立学完整 Rust，只在源码中补齐这些概念：

- `enum` + `match`：理解 `Op`、`EventMsg`、`ResponseEvent`
- `Result` / `?`：理解错误传播与失败边界
- `Arc`、channel、`tokio::spawn`：理解共享 session 与异步事件循环
- `async fn`、stream、future：理解模型流式响应与并行 tool call
- trait：理解工具 handler、store 和 sandbox runtime 的可替换接口
- `serde`：理解内部类型与 JSON-RPC / Responses API wire format 的映射

判断标准不是会写复杂 Rust，而是能准确追踪所有权、并发任务和消息边界。

## 主题路线总览

| 主题 | 核心问题 | 建议会话 | 产出 |
| --- | --- | ---: | --- |
| 1. 系统边界与协议骨架 | 谁向 Agent 提交操作，Agent 如何回传事件？ | 1 | 仓库地图、`Op → EventMsg` 图 |
| 2. Thread / Session / Turn 生命周期 | 一次用户输入如何启动并结束一个 turn？ | 2 | 第一条核心调用链 |
| 3. 模型边界与上下文 | Prompt 怎样构造，Responses stream 怎样变成内部事件？ | 2 | 请求/响应数据流与上下文清单 |
| 4. 工具运行时 | 模型 tool call 怎样找到 handler、执行并回灌？ | 2 | 一条完整工具闭环 |
| 5. 权限、审批与 Sandbox | 为什么工具 handler 不能直接裸跑命令？ | 2 | 安全决策顺序和失败路径 |
| 6. 持久化、恢复与 Compaction | Thread 如何跨进程恢复，模型上下文与 durable history 如何区分？ | 2 | 状态所有权图、resume/fork 路径 |
| 7. 指令、Skills、MCP 与 Multi-agent | 外部能力如何接入，子 Agent 如何复用核心 runtime？ | 2～3 | 扩展点地图与一次子 Agent 路径 |
| 8. App Server 与 SDK | 同一个 core 如何服务 TUI、IDE 类客户端和 SDK？ | 2 | JSON-RPC 到 core 的映射 |
| 9. 测试体系与综合实践 | 如何用证据验证 Agent 行为而非只读实现？ | 2 | 集成测试、复述和最小改动 |

预计首轮 17～20 小时。每次只推进一个问题，不要求连续按周完成。

## 主题 1：系统边界与协议骨架

### 要回答的问题

- 为什么 Codex 同时有 CLI、TUI、App Server 和 SDK？
- 哪些模块是交互适配层，哪些模块是 Agent runtime？
- `Op` 与 `EventMsg` 为什么比直接调用一组方法更适合异步 Agent？

### 源码入口

- [`main()` 与命令分发](/Users/bytedance/mind/codex/codex-rs/cli/src/main.rs:1040)：解析顶层子命令；重点观察 `exec`、`app-server` 和默认 TUI 最终进入不同 adapter，却共享 core。
- [`Op`](/Users/bytedance/mind/codex/codex-rs/protocol/src/protocol.rs:545)：调用方向 core 提交的 command；[`Event`](/Users/bytedance/mind/codex/codex-rs/protocol/src/protocol.rs:1278) 包装序号与 [`EventMsg`](/Users/bytedance/mind/codex/codex-rs/protocol/src/protocol.rs:1296)，构成反向事件流。
- [`CodexThread`](/Users/bytedance/mind/codex/codex-rs/core/src/codex_thread.rs:202) 与 [`submit`](/Users/bytedance/mind/codex/codex-rs/core/src/codex_thread.rs:247)：向 submission channel 写入 `Op`，同时向宿主暴露事件接收边界。
- 在线对照：[`protocol.rs`](https://github.com/openai/codex/blob/40b7560169c7274147a47f9b0c75db89fe016d34/codex-rs/protocol/src/protocol.rs)。

### 深入讲解

- [主题 1：从 TUI `turn/start` 到 Core `Op / EventMsg` 的完整逻辑](./openai-codex/01-system-boundary-and-protocol.md)

### 验证任务

选择一次普通文本输入，分别列出提交侧可能发送的 `Op` 和 UI 侧必须处理的关键 `EventMsg`。用源码确认字段，不凭产品界面猜测。

### 完成标准

能解释为什么 `CodexThread` 是交互层与 Agent core 的边界，以及 TUI 被替换后哪些核心代码无需变化。

## 主题 2：Thread / Session / Turn 生命周期

### 要回答的问题

- Thread、Session、Turn 和一次 sampling request 分别是什么生命周期？
- 一个 turn 为什么可能包含多次模型采样？
- interrupt、suspend、shutdown 的语义为什么不能混为一谈？

### 核心调用链

1. `CodexThread::submit(Op::TurnInput)` 将操作写入 submission channel。
2. `submission_loop` 消费 `Submission` 并分发操作。
3. `run_turn` 组织本轮上下文、状态和循环。
4. `run_sampling_request` 发起一次或多次模型请求。
5. turn 完成后通过 `EventMsg` 将状态发回调用方。

### 源码入口

- [`Session`](/Users/bytedance/mind/codex/codex-rs/core/src/session/session.rs:40)：一个 live thread 的可变运行时状态；[`Session::spawn`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:471) 负责初始化 channel、store、MCP 等依赖。
- [`session_loop` 的启动点](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:788)：把 `submission_loop` 放入独立 Tokio task，明确宿主提交与 Agent 消费是异步边界。
- [`submission_loop`](/Users/bytedance/mind/codex/codex-rs/core/src/session/handlers.rs:514)：按 `Op` 类型选择 handler，并管理 interrupt / shutdown 等 session 级控制。
- [`run_turn`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:153)：turn 级编排入口；[`run_sampling_request`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:1340) 管重试/采样循环；[`try_run_sampling_request`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:2179) 消费一次模型 stream。

### 验证任务

从 `core/tests/suite/agent_execution.rs` 选择一个最小集成测试，记录 mock Responses stream、提交的 `Op` 和最终事件。给调用链上的每一步标注“同步调用 / channel / spawned task / stream”。

### 完成标准

能脱离源码画出一次无工具 turn 的时序，并解释多个异步 task 如何通过 channel 和 cancellation token 协作。

## 主题 3：模型边界与上下文

### 要回答的问题

- system/developer/user 指令、历史和工具定义在哪里合成请求？
- Responses API 的流式事件怎样转为 `ResponseItem` 和 UI 事件？
- 为什么模型上下文不能等同于 durable thread history？
- retry、token budget 和 compaction 分别解决什么问题？

### 源码入口

- [`ModelClientSession`](/Users/bytedance/mind/codex/codex-rs/core/src/client.rs:276)：每个 turn 新建的模型连接状态；[`stream`](/Users/bytedance/mind/codex/codex-rs/core/src/client.rs:1878) 是 Responses 请求的统一流式边界。
- [`try_run_sampling_request`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:2179)：组装 prompt/tools、消费 `ResponseEvent`，并决定是否需要 follow-up sampling。
- [`context/mod.rs`](/Users/bytedance/mind/codex/codex-rs/core/src/context/mod.rs)：模型可见上下文 fragment 的入口；结合本仓库 `AGENTS.md` 中“有界、增量、cache-friendly”的上下文不变量阅读。
- [`run_compact_task`](/Users/bytedance/mind/codex/codex-rs/core/src/compact.rs:148)：显式 compaction 任务入口；远端策略再沿 `compact_remote*.rs` 展开。

### 验证任务

使用 `core/tests/common/responses.rs` 提供的 mock，检查一次 outbound Responses request 的 `input` 和 tools；再让 mock 返回文本 delta 与 completed，确认内部发出的事件顺序。

### 完成标准

能区分四种状态：持久化历史、当前 prompt、流式中的 active item、UI 已接收事件。

## 主题 4：工具运行时

### 要回答的问题

- 模型返回 `FunctionCall` 后，Codex 如何找到正确 handler？
- Tool spec、Tool call、Tool invocation 和 Tool output 的职责是什么？
- 为什么工具完成后 Agent 通常要再次采样？
- 并行 tool call、hook 和错误回灌在哪里发生？

### 核心调用链

```text
ResponseEvent::OutputItemDone
→ handle_output_item_done
→ ToolRouter::build_tool_call
→ ToolCallRuntime
→ ToolRouter::dispatch_tool_call_*
→ ToolRegistry::dispatch_any_*
→ CoreToolRuntime handler
→ ResponseInputItem::*CallOutput
→ follow-up sampling
```

### 源码入口

- [`handle_output_item_done`](/Users/bytedance/mind/codex/codex-rs/core/src/stream_events_utils.rs:289)：把完成的模型 item 分成普通输出、工具调用或需要直接回灌模型的解析错误。
- [`ToolRouter`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/router.rs:68) 与 [`build_tool_call`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/router.rs:148)：把不同 wire item 归一化为内部 `ToolCall`，再选择 dispatch 路径。
- [`ToolRegistry`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/registry.rs:271)：维护 tool name → handler 映射，并统一包裹 hook、telemetry、成功/失败终态。
- [`ExecCommandHandler`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs:59)：一个具体 built-in handler，可用来反推 spec、参数解析和执行 runtime 如何衔接。

### 深入讲解

- [主题 4：工具暴露、路由、Registry middleware 与结果回流](./openai-codex/04-tool-routing-and-dispatch.md)

### 验证任务

先追踪一个无副作用工具，再追踪 `exec_command`。运行 `tool_lifecycle` 或 `tool_parallelism` 中的一个聚焦测试，观察哪些不变量由 registry 统一保证，而不是每个 handler 自己实现。

### 完成标准

能解释新增一个 built-in tool 至少要接入哪些层，以及解析失败、未知工具和 handler 失败分别怎样反馈给模型。

## 主题 5：权限、审批与 Sandbox

### 要回答的问题

- Tool handler、policy、approval 和 OS sandbox 各自防什么？
- 为什么“模型决定调用工具”不等于“模型获得执行权限”？
- 首次 sandbox 执行失败后，何时允许升级或重试？
- macOS Seatbelt、Linux Landlock/bubblewrap 和 Windows sandbox 如何共享上层语义？

### 源码入口

- [`ExecCommandHandler::handle_call`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs:108)：解析 unified exec 请求并把执行交给更底层 runtime，而不是直接裸跑进程。
- [`ToolOrchestrator::run`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/orchestrator.rs:125)：集中实现 approval → sandbox 选择 → attempt → denial 后升级重试。
- [`SandboxManager`](/Users/bytedance/mind/codex/codex-rs/sandboxing/src/manager.rs:275)：把跨平台 sandbox 选择封装到 core tool 之外。
- [`execpolicy` crate 入口](/Users/bytedance/mind/codex/codex-rs/execpolicy/src/lib.rs) 定义命令策略；[`permissions.rs`](/Users/bytedance/mind/codex/codex-rs/protocol/src/permissions.rs) 与 [`approvals.rs`](/Users/bytedance/mind/codex/codex-rs/protocol/src/approvals.rs) 定义跨层传递的数据模型。

### 验证任务

用现有 `approvals.rs`、`exec_policy.rs` 或 `network_approval.rs` 测试构造三种命令：只读允许、需要审批、策略禁止。记录每一种在哪一层停止，以及是否真正启动进程。

### 完成标准

能画出安全决策顺序，并解释 policy 拒绝、用户拒绝、sandbox denial 和进程非零退出为什么是四类不同失败。

## 主题 6：持久化、恢复与 Compaction

### 要回答的问题

- JSONL rollout、SQLite state 和 `ThreadStore` 各自保存什么？
- resume、fork、rollback 和 compact 对历史的变换有什么不同？
- 为什么 live thread 和 cold thread 的读取路径不同？
- 崩溃恢复需要哪些已落盘边界？

### 源码入口

- [`RolloutRecorder`](/Users/bytedance/mind/codex/codex-rs/rollout/src/recorder.rs:86)：管理 JSONL rollout writer 与追加/flush 生命周期；[`rollout/lib.rs`](/Users/bytedance/mind/codex/codex-rs/rollout/src/lib.rs) 提供发现与读取入口。
- [`ThreadStore` trait](/Users/bytedance/mind/codex/codex-rs/thread-store/src/store.rs:68)：storage-neutral durable boundary，明确 create/resume/append/persist/load/fork 的语义；先读 [`README`](/Users/bytedance/mind/codex/codex-rs/thread-store/README.md) 再读 trait。
- [`StateRuntime`](/Users/bytedance/mind/codex/codex-rs/state/src/runtime.rs:88)：SQLite 状态层入口；migration 与 query 是投影/索引实现，不等同于模型 prompt。
- [`ThreadManager`](/Users/bytedance/mind/codex/codex-rs/core/src/thread_manager.rs:218)：管理 live thread；从 [`start_thread`](/Users/bytedance/mind/codex/codex-rs/core/src/thread_manager.rs:905)、[`resume_thread_from_rollout`](/Users/bytedance/mind/codex/codex-rs/core/src/thread_manager.rs:996)、[`fork_thread`](/Users/bytedance/mind/codex/codex-rs/core/src/thread_manager.rs:1176) 对比三条路径。
- [`run_compact_task`](/Users/bytedance/mind/codex/codex-rs/core/src/compact.rs:148)：改变模型可见上下文；它与 durable thread 的存储变换要分开理解。

### 验证任务

运行一个使用临时 `CODEX_HOME` 的 resume 或 fork 集成测试，检查落盘文件/记录在恢复前后的变化。不要用个人真实 `~/.codex` 做实验。

### 完成标准

能解释“上下文被 compact 后仍可恢复完整 thread”是否成立、依赖哪些存储，以及 durable state 为什么不能只存在于 prompt。

## 主题 7：指令、Skills、MCP 与 Multi-agent

### 要回答的问题

- `AGENTS.md`、Skill、Plugin、Hook 和 MCP 分别在什么阶段进入系统？
- MCP 工具怎样变成 registry 中的 runtime？
- 子 Agent 是新的 prompt，还是拥有独立 Session/Thread 的执行单元？
- fork history、parent/child lineage 和 inter-agent message 如何表示？

### 源码入口

- [`AgentsMdManager`](/Users/bytedance/mind/codex/codex-rs/core/src/agents_md_manager.rs:14)：加载并缓存项目指令；[`skills.rs`](/Users/bytedance/mind/codex/codex-rs/core/src/skills.rs:83) 还能观察 implicit skill invocation 何时被记录。
- [`McpHandlerCache`](/Users/bytedance/mind/codex/codex-rs/core/src/mcp_tool_exposure.rs:27)：把 MCP catalog 转成 core 可 dispatch 的 handler；[`McpConnectionSet`](/Users/bytedance/mind/codex/codex-rs/codex-mcp/src/connection_manager.rs:181) 管连接、工具/资源聚合与调用。
- [`usage_hint_text`](/Users/bytedance/mind/codex/codex-rs/core/src/session/multi_agents.rs:67)：为 root/subagent 注入角色与协作约束；[`create_spawn_agent_tool_v2`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/multi_agents_spec.rs:102) 定义模型实际看到的工具 schema。
- [`ThreadManager::spawn_subagent`](/Users/bytedance/mind/codex/codex-rs/core/src/thread_manager.rs:961)：先 flush 父 thread 的 rollout、读取持久化快照并构造 fork history，再启动带 lineage 的独立 thread；这不是简单生成一个新 prompt。

### 验证任务

先用一个 mock MCP tool 验证“发现 → 暴露 → 调用 → 回灌”；再读 `multi_agent_mode.rs` 或 `multi_agent_resume.rs`，画出 parent thread spawn child thread 的状态和消息路径。

### 完成标准

能区分能力扩展与执行单元扩展：MCP/Skill 改变“能做什么或怎样做”，subagent 改变“由哪个独立上下文执行”。

## 主题 8：App Server 与 SDK

### 要回答的问题

- App Server 为什么使用双向 JSON-RPC，而不是把 core 直接暴露给 UI？
- `thread/start`、`turn/start` 和 notifications 如何映射到 core protocol？
- TypeScript SDK 与 Python SDK 为什么采用不同集成层？
- 哪些 API 是稳定边界，哪些只是内部类型？

### 源码入口

- [`App Server README`](/Users/bytedance/mind/codex/codex-rs/app-server/README.md)：先建立 Thread / Turn / Item 与双向 JSON-RPC 生命周期词汇。
- [`MessageProcessor::process_request`](/Users/bytedance/mind/codex/codex-rs/app-server/src/message_processor.rs:596)：顶层 JSON-RPC 方法分发；随后进入 [`ThreadRequestProcessor::thread_start`](/Users/bytedance/mind/codex/codex-rs/app-server/src/request_processors/thread_processor.rs:500) 或 [`TurnRequestProcessor::turn_start`](/Users/bytedance/mind/codex/codex-rs/app-server/src/request_processors/turn_processor.rs:179)。
- [`protocol/v2/mod.rs`](/Users/bytedance/mind/codex/codex-rs/app-server-protocol/src/protocol/v2/mod.rs)：宿主可见的 wire types，应与 core 内部 `Op/EventMsg` 分层理解。
- [`Codex`](/Users/bytedance/mind/codex/sdk/typescript/src/codex.ts:11) 与 [`Thread`](/Users/bytedance/mind/codex/sdk/typescript/src/thread.ts:41)：TypeScript public API；[`CodexExec`](/Users/bytedance/mind/codex/sdk/typescript/src/exec.ts:65) 在第 92 行构造 `codex exec --experimental-json`，第 196 行启动子进程。
- [`Python SDK getting started`](/Users/bytedance/mind/codex/sdk/python/docs/getting-started.md)：对照它围绕 App Server lifecycle 的封装边界。

### 验证任务

手工启动一个临时 App Server，完成 `initialize → thread/start → turn/start → turn/completed`；随后用 TypeScript SDK 运行等价 turn，比较两个客户端边界和事件格式。

### 完成标准

能解释 core、App Server protocol、SDK public API 三层为什么不应共享同一套类型稳定性承诺。

## 主题 9：测试体系与综合实践

### 要回答的问题

- 如何在不调用真实模型的情况下测试 Agent loop？
- 哪些行为适合 unit test、integration test、snapshot test？
- 怎样验证 outbound request、stream event、tool side effect 和最终 history 是同一条因果链？

### 源码入口

- [`ResponseMock`](/Users/bytedance/mind/codex/codex-rs/core/tests/common/responses.rs:39) 与 [`mount_sse_once_match`](/Users/bytedance/mind/codex/codex-rs/core/tests/common/responses.rs:1102)：伪造 Responses stream，同时捕获 outbound request 做断言。
- [`TestCodexBuilder`](/Users/bytedance/mind/codex/codex-rs/core/tests/common/test_codex.rs:325) 与 [`TestCodex`](/Users/bytedance/mind/codex/codex-rs/core/tests/common/test_codex.rs:886)：搭建隔离 session 与临时 home。
- [`agent_execution.rs`](/Users/bytedance/mind/codex/codex-rs/core/tests/suite/agent_execution.rs:54)：从最小 mock turn 开始，再扩展到 `tool_lifecycle.rs`、`approvals.rs`、`compact_resume_fork.rs` 和 multi-agent tests。
- [`schema_fixtures_tests.rs`](/Users/bytedance/mind/codex/codex-rs/app-server-protocol/src/schema_fixtures_tests.rs)：验证 wire schema 稳定性；TUI snapshots 只用于理解 UI 侧回归策略。

### 综合实践

在临时 Codex checkout 中增加一个低风险、只读的最小 built-in tool，并完成：

1. Tool spec 与 handler。
2. Registry 接入。
3. 模型发起 tool call 的 mock response。
4. Tool output 被回灌到下一次 sampling request 的断言。
5. 失败输入与未知工具的对照测试。
6. 一页设计说明：为什么该逻辑属于 core tool、MCP tool 或外层 workflow。

不以向上游提交 PR 为首轮目标。先证明能够安全修改并用集成测试守住 Agent 不变量。

## 第一轮推荐节奏

### Pass A：先通主链（主题 1～4）

只追踪一条文本输入触发工具再返回答案的路径。暂时把登录、TUI 渲染、跨平台 sandbox 细节视为黑盒。完成后应能回答“Codex 为什么是 Agent，而不只是 API CLI”。

### Pass B：补生产不变量（主题 5～6）

把权限、审批、持久化、resume 和 compaction 挂回主链。完成后应能回答“为什么 demo loop 很短，而生产 Agent runtime 很复杂”。

### Pass C：理解平台化（主题 7～9）

研究能力扩展、多 Agent、App Server、SDK 和测试体系。完成后应能判断一项新能力应该进入 core、外部 MCP、Skill、App Server 还是 SDK。

## 当前学习单元

- Current：主题 1——系统边界与 `Op / EventMsg` 协议骨架。
- 本轮问题：一次普通用户输入跨越了哪些进程内边界，哪些数据属于 command，哪些属于 event？
- 已完成：建立 `TUI → App Server → CodexThread → submission_loop → RegularTask → EventMsg → TUI` 的带符号调用图。
- Next：运行 concurrent submission 与 `TurnStarted` prewarm 两个聚焦测试，验证 start/steer 和请求确认/异步完成语义。

## 设计取舍

待研读后累计记录。

## 验证实验

待主题 1 开始后记录命令、结果和源码证据。

## 我的复述与纠偏

待学习会话中累计记录。

## 可迁移结论

待学习会话中累计记录，并链接回 [Agent State Management](../../phase-1-ai-product-engineer/02-agent-state-management.md)、[Memory and Tool Calling](../../phase-1-ai-product-engineer/03-memory-and-tool-calling.md) 与 [Multi-agent System](../../phase-3-ai-system-engineering/10-multi-agent-system.md)。

## 未解决问题

- 第一轮结束后，哪些模块值得进入第二轮专题深挖？
- 当前 runtime 中哪些边界来自产品兼容性，哪些是可迁移的通用 Agent 架构？

## 下一步

开始主题 1，不先编译整个 workspace；先用静态调用关系和一个协议层聚焦测试建立可验证的系统骨架。
