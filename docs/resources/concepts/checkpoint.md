---
layout: default
title: "Checkpoint"
---

# Checkpoint

## 一句话定义

Checkpoint 是系统主动建立的一个**已知边界**，使它可以在这里安全地调度、协调、观察、恢复或继续；具体是否保存状态、是否持久化、能否回滚，取决于所在领域。

## 共同心智模型

不同 checkpoint 的共同结构是：

```text
持续变化的系统
→ 到达一个定义明确的边界
→ 建立当前状态的某种“可依赖事实”
→ 允许下一阶段调度、检查、恢复或交接
```

“可依赖事实”可能只是一条调度规则，也可能是磁盘上的完整快照。因此不能只看名字，必须继续问：

1. checkpoint 为了解决什么问题？
2. 它捕获或确认了哪些状态？
3. 状态保存在哪里，是否 durable？
4. 它保证一致性、可恢复性、原子性还是仅保证调度顺序？
5. 从 checkpoint 恢复后，外部副作用会不会重复？

## 常见领域

| 领域 | Checkpoint 做什么 | 是否持久化 | 主要保证 |
| --- | --- | --- | --- |
| JavaScript / V8 microtask | 清空已就绪的 Promise callback 与 `await` continuation | 否 | 明确的调度与控制权交接 |
| GC safepoint | 让线程到达 GC 可检查栈、对象引用和寄存器的已知位置 | 通常否 | Runtime 能安全协调线程和扫描内存 |
| 数据库 | 把 WAL 对应的脏页推进到持久存储，缩短崩溃恢复扫描范围 | 是 | 建立恢复起点；不等于每个事务在此才提交 |
| 流处理 / 分布式计算 | 对 operator state、消息位置或 offset 建立一致快照 | 是 | 失败后从一致位置重放；可能参与 exactly-once |
| 模型训练 | 保存权重、optimizer、scheduler、step、RNG 等训练状态 | 是 | 中断后继续训练或选择某个模型版本 |
| Durable workflow / Agent | 保存任务状态、已完成 action、pending wait 和幂等标识 | 是 | 进程重启后继续，而不重复已确认的副作用 |
| VM / Filesystem snapshot | 保存某一时刻的磁盘或内存视图 | 是 | point-in-time 恢复；应用一致性需要额外协调 |
| Git / 人工工作流 | 用 commit 或阶段产物标记一个可回退的工作点 | 是 | 人工可比较、回退和继续，不是 Runtime 事务保证 |

## Codex 源码里的 Checkpoint 谱系

以本地 `openai/codex` revision `2df6705` 为准，源码中可以找到 **7 类明确使用 checkpoint 语义的机制**。它们并不是同一种“存档”：最接近游戏存档的是 compaction checkpoint；真正承载崩溃后恢复事实的是更底层的 rollout / ThreadStore 持久化日志。

| 机制 | 保存或确认的对象 | 是否持久化 | 主要用途 | 像游戏存档吗 |
| --- | --- | --- | --- | --- |
| Conversation compaction checkpoint | 压缩后的 `replacement_history`、history window 元数据，以及关联的上下文基线 | 是 | 用新 history window 替换旧模型上下文，并作为 resume 的完整 history base | **最像，但只保存模型上下文，不保存整个 Runtime** |
| MCP resource-origin checkpoint | app/widget resource 的 connector、tool、URI、turn provenance | 随 compaction 持久化 | compaction 后仍能判断资源来源和授权上下文 | 像主存档中的一小块附加状态 |
| Rollout projection checkpoint | JSONL 的 `next_byte_offset` 与 `next_ordinal` | 是，SQLite | 让可重建的 SQLite 视图知道已经物化到 canonical rollout 的哪里 | 像数据库索引器的消费游标 |
| External-agent import checkpoint | 已导入源 session 的 content hash、mtime 与目标 thread | 是，migration ledger | 以 compare-and-swap 方式确认增量导入已完成，避免丢更新 | 像同步任务进度点 |
| Metadata backfill checkpoint | 已扫描 rollout 的 watermark | 是，SQLite state | 后台 backfill 中断后从 watermark 继续 | 像批处理断点续跑 |
| SQLite WAL checkpoint | logs DB 中可写回主库的 WAL frames | 是，SQLite | 启动维护、缩短 WAL；`PASSIVE` 模式不阻塞活跃读写 | 是数据库意义的恢复维护点 |
| V8 microtask checkpoint | 当前已就绪的 Promise reaction / `await` continuation | 否 | Host command 后推进 JavaScript microtask queue | **不像**；只是调度边界 |

### 0. 真正的“存档介质”：Rollout / ThreadStore

Codex 的 durable 基础不是一个名为 `CheckpointManager` 的大快照，而是一条可重放日志：

```text
Session 产生 ResponseItem / EventMsg / TurnContext / WorldState
→ ThreadStore::append_items
→ RolloutRecorder 写 canonical JSONL
→ flush durability barrier
→ SQLite 只物化为可重建查询视图
```

[`ThreadStore`](/Users/bytedance/mind/codex/codex-rs/thread-store/src/store.rs:68) 明确把自己定义为 storage-neutral persistence boundary，并区分：

- `append_items`：把 rollout item 排入 thread 的持久化序列；
- `persist_thread`：物化 lazy thread 并持久化 queued items；
- `flush_thread`：等待 queued items durable/readable；
- `load_history` / `load_latest_model_context`：为 resume、fork、rollback 和 memory job 提供重放输入。

本地实现先通过 [`durable_write`](/Users/bytedance/mind/codex/codex-rs/thread-store/src/local/live_writer.rs:354) 写入并 flush JSONL，再尝试把它投影到 SQLite；注释明确要求 SQLite 可以落后，但不能领先 canonical history。因此：

> JSONL rollout 是存档事实，SQLite 是可以重建的目录与查询视图。

### 1. Conversation Compaction Checkpoint

这是 Codex 中最重要、也最接近“换盘存档点”的 checkpoint。

[`CompactedItem`](/Users/bytedance/mind/codex/codex-rs/history/src/lib.rs:142) 保存：

```text
replacement_history
mcp_resource_origins
window_number
first / previous / current window id
```

[`Session::replace_compacted_history`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:3395) 先把内存中的 live history 替换成压缩后的 history，再把 `RolloutItem::Compacted` 写入 rollout；需要时随后写入完整 `WorldState` baseline 和 `TurnContext`。在恢复时，[`load_latest_model_context`](/Users/bytedance/mind/codex/codex-rs/thread-store/src/local/model_context.rs:30) 从尾部反向扫描，找到最新可用的 replacement-history checkpoint 和必要的 completed-turn metadata 后即可停止继续向前读。随后 [`reconstruct_history_from_rollout`](/Users/bytedance/mind/codex/codex-rs/core/src/session/rollout_reconstruction.rs:112) 把它当作完整 history base，只重放 checkpoint 之后仍然存活的 suffix。

它的精确含义是：

```text
旧的 model-visible history
→ compaction request
→ 安装 replacement_history
→ 从此未来 prompt 以 replacement_history 为历史基座
```

`rollout-trace` 还会把“replacement history 真正成为 live history 的时刻”记录成 [`CompactionCheckpointTracePayload`](/Users/bytedance/mind/codex/codex-rs/rollout-trace/src/compaction.rs:84)。这是同一个语义 checkpoint 的可观测性记录，不是另一份 canonical thread 存档。

它不保存 Tokio task stack、channel、pending oneshot、正在运行的 shell process handle 或 V8 heap，所以它不是整机/整进程快照。

### 2. MCP Resource-Origin Checkpoint

Compaction 会丢弃大量旧 conversation items，但后续 widget resource read 仍需知道某个 URI 来自哪个 app、account、tool 和 turn。为此 [`ResourceOrigins::checkpoint`](/Users/bytedance/mind/codex/codex-rs/codex-mcp/src/resource_origin.rs:42) 截取一个有界 provenance 集合，放进 `CompactedItem`；resume 时 [`restore_checkpoint`](/Users/bytedance/mind/codex/codex-rs/codex-mcp/src/resource_origin.rs:62) 恢复它。

这是“主 checkpoint 中的安全相关附属状态”，不是独立的 thread 恢复点。它还有数量和字节大小限制；无效或超限数据会清空，而不是盲目恢复。

### 3. Rollout Projection Checkpoint

[`RolloutProjectionState`](/Users/bytedance/mind/codex/codex-rs/thread-store/src/local/thread_history.rs:44) 用两个游标描述 SQLite 已经消费的 durable JSONL prefix：

```text
next_rollout_byte_offset
next_rollout_ordinal
```

投影 rows 与这两个游标在同一个 `BEGIN IMMEDIATE` transaction 中提交。这样失败时 projection 只会落后；不会声称自己已经消费了尚未成功物化的 rollout 数据。它解决的是 **派生视图增量物化的一致性**，不是 Agent 会话恢复。

### 4. External-Agent Import Checkpoint

[`checkpoint_existing_session_import`](/Users/bytedance/mind/codex/codex-rs/external-agent-migration/src/sessions/ledger.rs:125) 在把外部 Agent session 的缺失 suffix 追加到 Codex thread 后，更新 import ledger。更新前会重新核对 source content hash、mtime、目标 thread 和 expected old hash，因此本质上是一个文件级 compare-and-swap checkpoint。

它确认的是“这个源文件版本已经同步到目标 thread”，而不是保存 thread runtime。

### 5. Metadata Backfill Checkpoint

[`checkpoint_backfill`](/Users/bytedance/mind/codex/codex-rs/state/src/runtime/backfill.rs:64) 把批处理当前 `last_watermark` 写进 `backfill_state`。后台扫描 rollout metadata 时，每完成一批就推进 watermark；进程中断后无需从头遍历。

这是典型的 batch-job progress checkpoint。

### 6. SQLite WAL Checkpoint

日志库启动维护时，[`PRAGMA wal_checkpoint(PASSIVE)`](/Users/bytedance/mind/codex/codex-rs/state/src/runtime/logs.rs:306) 会把当前不需要等待活跃 reader/writer 的 WAL frames 尽量推进主数据库。它属于 SQLite 存储引擎语义，与 conversation checkpoint 没有直接关系。

### 7. V8 Microtask Checkpoint

Code Mode 的 [`perform_microtask_checkpoint`](/Users/bytedance/mind/codex/codex-rs/code-mode-runtime/src/runtime/mod.rs:259) 只负责在 Host 写入 tool result、tool error 或 timer callback 后执行已就绪 microtasks，再检查顶层 Promise 是否完成。它不写 rollout，也不提供进程重启恢复。

### Rollback / Revert 与 Checkpoint 的关系

Codex 的 rollback / revert 不是创建 checkpoint，而是**消费已有持久化历史并改变哪一段仍然有效**：

- live session rollback 追加 `ThreadRolledBack` marker，然后在 replay 时丢弃最新 N 个 user-turn segment；见 [`handlers.rs`](/Users/bytedance/mind/codex/codex-rs/core/src/session/handlers.rs:343) 与 [`rollout_reconstruction.rs`](/Users/bytedance/mind/codex/codex-rs/core/src/session/rollout_reconstruction.rs:142)；
- unloaded paginated thread revert 不修改旧 rollout，而是创建一个引用 retained prefix 的新 immutable rollout，再用 CAS 切换当前 rollout path；见 [`revert_thread.rs`](/Users/bytedance/mind/codex/codex-rs/thread-store/src/local/revert_thread.rs:13)。

因此最准确的游戏比喻是：

```text
rollout JSONL             = 持续自动保存的事件日志
compaction checkpoint     = 一份可接续的新章节存档基座
resume                    = 载入基座并重放后续事件
rollback / revert         = 选择较早边界并让后续章节失效/分叉
SQLite projection cursor  = 存档目录已经索引到哪里
V8 microtask checkpoint   = 当前帧末尾处理 Promise 队列
```

## 1. V8 Microtask Checkpoint

在 Codex Code Mode 中，[`perform_microtask_checkpoint`](/Users/bytedance/mind/codex/codex-rs/code-mode-runtime/src/runtime/mod.rs:259) 发生在 Rust Host 处理 tool response、tool error 或 timer callback 之后：

```text
Host 更新 Promise 状态
→ microtask checkpoint
→ 执行 Promise reaction / await continuation
→ 检查主模块是否完成
```

它不保存状态，只表示“现在允许 V8 推进一轮已经就绪的微任务”。这里的 checkpoint 更接近 **controlled scheduling boundary**。

## 2. GC Safepoint

垃圾回收器不能在线程任意执行到一半时可靠扫描所有对象引用。Runtime 会让线程运行到一组已知位置，再暂停或协调：

```text
application threads
→ safepoint
→ GC 知道引用位于哪些 stack/register slots
→ mark / relocate / compact
→ threads resume
```

它与“稳定且受控的交接点”最接近，但仍不是持久化快照。并且 safepoint 与 checkpoint 在具体 Runtime 中可能是不同术语，不应默认完全等价。

## 3. Database Checkpoint

采用 WAL 的数据库通常先写日志，再延迟写回数据页。Database checkpoint 会记录或推进一个恢复边界：

```text
WAL 已持久化
+ 部分脏页刷盘
+ checkpoint metadata
→ 崩溃恢复不必从最早日志开始重放
```

它主要优化和约束 recovery，不等于 transaction commit：事务能否提交通常由 WAL durability 等规则决定，而不是等待整个数据库 checkpoint。

## 4. Distributed / Stream Checkpoint

Flink、Spark Streaming 等系统需要同时考虑多个 operator、channel 和 input offset：

```text
source offset
+ operator state
+ in-flight message boundary
+ sink commit state
→ consistent distributed checkpoint
```

这里最难的不是“把内存写盘”，而是捕获全局一致切面。若外部 sink 也参与 two-phase commit，checkpoint 才可能支撑 end-to-end exactly-once；只保存内部状态不能自动消除外部重复副作用。

## 5. Model Training Checkpoint

训练 checkpoint 不应只保存 model weights。为了真正 resume，通常还需要：

```text
model parameters
optimizer states
learning-rate scheduler
global step / epoch
random-number-generator states
mixed-precision scaler
data-loader position（视框架而定）
```

只保存权重通常足够 inference 或重新开始 fine-tuning，但不能保证从完全相同的训练轨迹继续。

Checkpoint 也不等于 best model：`checkpoint-1000` 只表示训练到某个 step 保存，是否最好需要 eval metric 判断。

## 6. Durable Workflow / Agent Checkpoint

长时间 Agent 任务最接近分布式 workflow：进程可能退出，工具可能已经产生外部副作用。一个有用的 checkpoint 需要同时记录：

```text
当前 workflow state
已完成 action IDs
输入输出或证据引用
pending approval / wait
重试次数
idempotency key / external receipt
下一可运行节点
```

恢复时不能只把 prompt 重新发送给模型，否则可能重复付款、发消息或修改文件。这里 checkpoint 的关键保证是 **durability + idempotent resume**。

Codex 的 rollout / ThreadStore 提供可重放历史，但 Tokio task、channel、pending oneshot 或进程句柄不会原样成为 durable checkpoint；恢复逻辑仍需从持久化 facts 重建 runtime state。

## 如何快速判断一个 Checkpoint

看到 checkpoint 时，可以用下面的模板：

```text
这是 ______ 的 checkpoint。
它发生在 ______ 边界。
它捕获/确认 ______ 状态。
状态保存于 ______。
它保证 ______。
它不保证 ______。
恢复或继续时，外部副作用通过 ______ 避免重复。
```

套到 Code Mode：

```text
这是 V8 microtask scheduling checkpoint。
它发生在 Host command 处理完成之后。
它确认 Promise 状态已更新，并执行已就绪 microtasks。
它不把状态写入持久化存储。
它保证受控调度顺序。
它不保证事务、回滚、权限或崩溃恢复。
```

## 常见误区

- checkpoint 不一定是 snapshot；V8 microtask checkpoint 就不保存快照。
- checkpoint 不一定 durable；GC safepoint 通常只存在于进程内。
- checkpoint 不一定意味着 transaction commit。
- 有 checkpoint 不代表能 exactly-once；还必须处理输入位置、外部 sink 和幂等。
- 能加载 model weights 不代表能精确恢复训练。
- “安全点”通常只对特定不变量安全，不表示该点之后不会报错或产生副作用。

## 相关链接

- [Codex 工具路由与 Code Mode](../../open-source/studies/openai-codex/04-tool-routing-and-dispatch.md)
- [Agent State Management](../../phase-1-ai-product-engineer/02-agent-state-management.md)
- [Eval / Checkpoint / Deploy](../../phase-2-model-fine-tuning/10-eval-checkpoint-deploy.md)
- [Persistent Memory](../../phase-3-ai-system-engineering/09-persistent-memory.md)
