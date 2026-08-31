---
layout: default
title: "openai/codex 04 · 工具路由与执行回流"
---

# openai/codex 04 · 工具路由与执行回流

返回：[openai/codex 源码学习路线](../openai-codex.md) / [真实架构全景图](./00-real-architecture-map.md) / [Progress](../../../progress.md)

## 先给结论

`ToolRouter` 不只是“LLM 产生工具名以后，查表转发到 handler”。它位于模型协议与工具 runtime 的双向边界，至少承担五类责任：

1. 持有本 step 真正可执行的 `ToolRegistry`。
2. 持有并向模型提供经过 exposure policy 过滤的 `model_visible_specs`。
3. 把 Responses API 的多种 wire item 归一化为内部 `ToolCall`。
4. 查询工具的并行能力、argument diff consumer、readiness 和 runtime。
5. 将 `ToolCall` 与 Session、Turn、StepContext、cancellation 等执行上下文组合为 `ToolInvocation`，再交给 Registry 统一分派。

真正的“按名字找 handler”发生在 [`ToolRegistry::dispatch_any_with_terminal_outcome`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/registry.rs:479) 内，但 Registry 在调用 handler 前后还统一处理 hook、telemetry、生命周期事件、错误和结果接纳。

## 一条完整调用链

```text
Step 开始
  → built_tools / build_tool_router
  → 注册 built-in、MCP、extension、dynamic、collaboration runtimes
  → exposure / collision / code-mode / tool-search policy
  → ToolRouter { registry, model_visible_specs }

请求模型
  → build_prompt(tools = model_visible_specs)
  → Responses API

模型返回
  → ResponseEvent::OutputItemDone
  → handle_output_item_done
  → ToolRouter::build_tool_call(ResponseItem)
  → ToolCallRuntime::handle_tool_call
  → ToolRouter::dispatch_tool_call_*
  → ToolInvocation
  → ToolRegistry::dispatch_any_*
  → CoreToolRuntime::handle
  → ToolOutput
  → ResponseInputItem::*CallOutput
  → record_conversation_items
  → needs_follow_up = true
  → 下一次 sampling
```

这条链中，Router 是协议与 runtime 的边界；Registry 是统一执行 middleware；具体 handler 才拥有工具本身的业务语义。

## 阶段 1：先决定模型能看到什么工具

工具路由在 LLM 返回 function call 之前就已经开始作用。

[`built_tools`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:1494) 为当前 turn/step 构造一个 `ToolRouter`。[`build_tool_router`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:117) 会依次聚合：

- built-in shell、patch、view、plan、user input 等工具；
- collaboration / subagent 工具；
- MCP tools 与 MCP resource tools；
- extension tools；
- host 传入的 dynamic tools；
- provider hosted tools，例如满足条件时的 hosted web search。

[`finalize_tool_router`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:314) 随后处理：

- 重名与保留名字冲突；
- direct、deferred、code mode、hidden 等 exposure；
- tool search 与 namespace 冲突；
- code mode executor 注册；
- 当前模型、feature、permission 和 session source 对工具表的影响。

最后形成两份相关但不同的数据：

| 数据 | 含义 |
| --- | --- |
| `ToolRegistry` | 当前 step 已注册、可由 runtime 分派的工具及其 exposure |
| `model_visible_specs` | 这一次请求真正发送给模型的 tool schemas |

[`build_model_visible_specs`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:484) 只选择 direct exposure 的工具，再合并 hosted specs。Deferred、CodeModeOnly 或 Hidden 工具可以存在于 Registry，却不一定出现在模型最初看到的工具列表中。

[`build_prompt`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:1312) 最终设置：

```text
Prompt.tools = step_context.tool_router.model_visible_specs()
Prompt.parallel_tool_calls = true
```

因此 Router 的第一项职责是 **capability exposure**：限制模型可以提出哪些调用，而不是等模型随便生成名字后才开始检查。

## 当前 Step 的工具计划怎样形成

工具集合不是根据用户自然语言“猜一批可能有用的工具”，而是对当前运行条件做确定性规划。可以把输入理解为三个维度的共同约束：

```text
系统 / Runtime 资格
∩ 工具自身 Exposure
∩ 用户或 Host 的显式选择
→ 当前 Step 的 Tool Plan
→ model_visible_specs
→ Prompt.tools
```

三个维度不是严格的覆盖顺序，更接近共同参与构建和求交集：

| 维度 | 典型输入 | 影响 |
| --- | --- | --- |
| 系统资格 | model/provider capability、feature flags、environment readiness、MCP 连接状态、root/subagent/guardian 身份、multi-agent 深度 | 工具能否注册、是否有成立的执行环境 |
| 工具 Exposure | `Direct`、`Deferred`、`DirectModelOnly`、`DeferredModelOnly`、`CodeModeOnly`、`Hidden` | 工具通过哪一个模型表面出现 |
| 用户 / Host 选择 | plugin、app、MCP 或 skill mention，selected capability roots，App Server dynamic tools | 本次需要加载、启动或纳入计划的外部能力 |

用户显式指定不是最高权限的强制覆盖。例如用户 mention 一个 MCP server，只会让 Codex 尝试把它作为 required server 纳入当前 step；它仍须满足 server ready、模型/provider 支持和 exposure policy。

### 为什么准确单位是 Step，而不是 Turn

[`Session::capture_step_context`](/Users/bytedance/mind/codex/codex-rs/core/src/session/mod.rs:3173) 在模型 sampling 前捕获一次 request-scoped snapshot：

```text
refresh environment readiness
→ refresh AGENTS.md
→ resolve selected capability roots
→ capture MCP binding / required servers
→ prepare plugin recommendations
→ built_tools
→ StepContext { environments, mcp, tool_router, model_info, ... }
```

[`run_turn`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:311) 在 follow-up sampling 前可以重新捕获 `StepContext`。因此同一个 turn 中，后续请求的工具计划可能因为 environment readiness、MCP server、pending user input 或 model switch 而改变。

### Built-in 的条件式注册示例

[`add_shell_tools`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:958) 只有在以下条件同时成立时才注册 `exec_command` 和 `write_stdin`：

```text
存在可执行 environment
AND ShellTool feature enabled
AND UnifiedExec feature enabled
AND 当前模型 shell_type != Disabled
```

其他例子：

- `apply_patch`：需要 environment，且当前模型配置了 `apply_patch_tool_type`。
- `view_image`：需要 environment 和 `ViewImage` feature。
- MCP resource tools：需要当前 MCP binding 中存在 server。
- collaboration tools：需要 multi-agent 启用，同时满足 agent 身份、版本和最大 spawn depth。

这一步解决“Runtime 能不能提供”；approval、policy 与 sandbox 解决的是“具体调用能不能执行”。工具出现在模型上下文中，不代表模型自动获得执行权限。

## Deferred 工具怎样被发现

Deferred 的准确含义是：**执行 Runtime 已注册，但完整 ToolSpec 暂时不发送给模型。**

```text
执行层：Deferred Runtime 已在 ToolRegistry
模型层：只暴露 tool_search，ToolSpec 按需加载
```

### 1. 为 Deferred Runtime 建立搜索材料

[`ToolSearchHandlerCache::get_or_build`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/tool_search.rs:50) 遍历 Registry，只选择：

```text
tool.exposure.is_deferred()
AND tool.runtime.search_info().is_some()
```

每个工具提供一个 `ToolSearchInfo`：

```text
ToolSearchInfo
├─ search_text：用于检索
├─ LoadableToolSpec：命中后返回给模型的 schema
└─ source_info：MCP / plugin 等来源描述
```

默认 [`search_text`](/Users/bytedance/mind/codex/codex-rs/tools/src/tool_search.rs:87) 由这些字段拼接：

- tool / namespace name；
- 下划线替换为空格后的名字；
- tool / namespace description；
- JSON Schema 中的参数名和参数 description；
- custom tool 的 grammar syntax。

### 2. 只把 `tool_search` 直接暴露给模型

当当前模型支持 search tool、provider 支持 namespace tools，且存在至少一个可检索的 Deferred Runtime 时，[`finalize_tool_router`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:314) 注册一个 direct `tool_search` handler。

初次请求可能是：

```text
Prompt.tools
├─ exec_command
├─ apply_patch
└─ tool_search

ToolRegistry only
├─ calendar.create_event   [Deferred]
├─ drive.search_files      [Deferred]
└─ collaboration.wait      [Deferred]
```

模型根据任务调用：

```json
{
  "query": "create a calendar event",
  "limit": 5
}
```

### 3. 返回可加载 ToolSpec，而不是普通文本

[`ToolSearchHandler::search`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/tool_search.rs:229) 返回匹配的 `LoadableToolSpec`，并通过 [`ToolSearchOutput`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/context.rs:149) 形成特殊协议项：

```text
ToolSearchOutput {
  call_id,
  status: completed,
  execution: client,
  tools: [matched ToolSpecs]
}
```

Turn Loop 把该输出记录进 conversation history。后续请求不会把命中的工具重新加入顶层 `Prompt.tools`；Responses 协议根据历史中的 `ToolSearchOutput.tools` 让模型获得这些动态 schema。

模型随后产生具体 `FunctionCall` 时，Router 仍从原来的 Registry 找到早已注册的 Runtime：

```text
tool_search(query)
→ ToolSearchOutput { calendar.create_event spec }
→ 下一次 sampling
→ FunctionCall(calendar.create_event)
→ ToolRegistry 中原有 MCP / extension runtime
```

## BM25 检索的实际实现

Codex 没有自行实现搜索算法，而是依赖 [`bm25 = 2.3.2`](/Users/bytedance/mind/codex/codex-rs/Cargo.toml:304)，构建一个本地、内存中的 lexical search engine。

### 1. 一个 Tool 对应一篇 Document

[`ToolSearchHandler::new`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/handlers/tool_search.rs:132) 把每个 `search_text` 转成 `Document<usize>`：

```text
Document {
  id: search_infos 数组下标,
  contents: 工具 search_text,
}
```

再创建：

```rust
SearchEngineBuilder::<usize>::with_documents(
    Language::English,
    documents,
).build()
```

搜索命中后，document id 被映射回 `search_infos[id]`，从而取得对应 `LoadableToolSpec`。

### 2. English tokenizer

`bm25` 默认 tokenizer 的处理顺序是：

```text
Unicode normalization
→ lowercase
→ Unicode word-boundary split
→ remove English stop words
→ English stemming
```

例如：

```text
"Creating calendar events"
→ ["creat", "calendar", "event"]
```

实现可对照 [`bm25/default_tokenizer.rs`](https://docs.rs/crate/bm25/2.3.2/source/src/default_tokenizer.rs)。这里不是模型 embedding：token 被 hash 到稀疏整数维度，检索仍是关键词匹配。

### 3. TF 饱和与长度归一化

Codex 没有覆盖 crate 的默认参数：

```text
k1 = 1.2
b = 0.75
avgdl = 所有工具 search_text 的平均 token 数
```

文档中 token 的权重为：

```text
TFWeight(t, d) =
  tf × (k1 + 1)
  ─────────────────────────────────────────
  tf + k1 × (1 - b + b × doc_len / avgdl)
```

这使重复关键词的收益逐渐饱和，并对特别长的工具描述做归一化。对应实现见 [`bm25/embedder.rs`](https://docs.rs/crate/bm25/2.3.2/source/src/embedder.rs)。

### 4. IDF 与总分

倒排索引记录每个 token 出现在哪些文档中。IDF 为：

```text
IDF(t) = ln(1 + (N - n(t) + 0.5) / (n(t) + 0.5))
```

- `N`：Deferred document 总数；
- `n(t)`：包含 token `t` 的 document 数量。

工具描述中到处出现的 `tool` 权重较低；只出现在少量工具中的 `calendar` 权重更高。一个 document 的分数是查询 token 的 `IDF × TFWeight` 之和。具体倒排索引、IDF 与排序逻辑见 [`bm25/scorer.rs`](https://docs.rs/crate/bm25/2.3.2/source/src/scorer.rs)。

搜索时先通过倒排索引取“至少命中一个 query token”的候选，再按 BM25 score 降序排列并截断到 `limit`。最后 `coalesce_loadable_tool_specs` 将同 namespace 的结果合并后返回。

### 5. 这个选择的边界

- 优点：本地、确定性、无额外模型请求、无需 embedding service 或 vector database。
- 工具规模变化时，`ToolSearchHandlerCache` 比较 immutable runtime identity 或 dynamic `ToolSearchInfo`；来源没有变化则复用索引，变化时重建。
- 它是 lexical retrieval，不理解同义词；模型生成更贴近 tool metadata 的 query 可以缓解这一点。
- Codex 固定使用 `Language::English`，因此英文 tool name、description 和参数描述质量直接影响召回；中文 query 或中文-only metadata 的效果可能不稳定。

## Code Mode：覆盖在 Tool Router 上的代码编排层

Code Mode 之所以容易从简化架构图中消失，是因为它最终仍复用 `ToolCallRuntime → ToolRouter → ToolRegistry`。它不是第四种底层工具，而是让模型用一段 JavaScript 在一次外层 tool call 中组织多个原有工具调用。

### 三种 ToolMode

[`ToolMode`](/Users/bytedance/mind/codex/codex-rs/protocol/src/openai_models.rs:331) 有三种模式：

| 模式 | 模型表面 |
| --- | --- |
| `Direct` | 模型直接看到普通 tools，并逐个发出 function call |
| `CodeMode` | 模型看到 Code Mode 的 `exec` / `wait`，同时仍可直接看到符合 exposure 的普通 tools |
| `CodeModeOnly` | 可嵌套的普通 tools 从顶层列表隐藏，模型主要通过 `exec` 中的 `tools.*` 调用 |

[`effective_tool_mode`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/mod.rs:79) 综合 model metadata、feature flags 和 Code Mode host availability 得到当前有效模式。普通 `CodeMode` 在 runtime 不可用且允许退化时可以回到 `Direct`；`CodeModeOnly` 则保持 fail-closed 语义。

### Step 构建时：把普通工具变成 nested tools

[`register_code_mode_executors`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/spec_plan.rs:706) 在 Registry 已经收集 built-in、MCP、extension 和 collaboration runtimes 之后运行：

```text
遍历 Registry
→ 选择 exposure.is_available_in_code_mode()
→ 排除 configured namespaces
→ 规范化工具名，解决 Code Mode global-name collision
→ 收集 nested tool definitions
→ 生成外层 exec freeform ToolSpec
→ 把 CodeModeExecuteHandler 和 CodeModeWaitHandler prepend 回 Registry
```

最终模型看到的外层 [`exec`](/Users/bytedance/mind/codex/codex-rs/code-mode-protocol/src/lib.rs:50) 不是 shell exec，而是接收 raw JavaScript 的 freeform custom tool。它的 description 会告诉模型：

```javascript
const result = await tools.exec_command({ cmd: "rg -n TODO src" });
text(result.output);
```

工具名经过归一化后暴露在 V8 的 `tools` object 上，完整元数据还可以通过 `ALL_TOOLS` 查找。Deferred tools 也可以成为 nested tools，而不必全部占用顶层 `Prompt.tools`。

### 外层执行：JavaScript source 进入 CodeModeService

模型返回 `CustomToolCall(name = "exec", input = raw JavaScript)` 后，仍先经过普通 Router 和 Registry，最后到达 [`CodeModeExecuteHandler`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/code_mode/execute_handler.rs:20)。Handler 会：

1. 解析可选的 `// @exec: {...}` pragma。
2. 从产生该调用的工具 snapshot 建立 `enabled_tools`。
3. 调用 thread-owned [`CodeModeService`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/code_mode/mod.rs:69)。
4. 通过 `CodeModeSessionProvider` 创建或复用 Code Mode session。
5. 启动一个 cell，等待 `Result`、`Yielded` 或 `Terminated`。

[`CodeModeSession`](/Users/bytedance/mind/codex/codex-rs/code-mode-protocol/src/session.rs:151) 归属于一个 Codex thread。每个 exec cell 使用新的 V8 isolate 执行 async JavaScript module；同一 session 内的多个 cells 可以通过 `store/load` 共享序列化值。

Provider contract 允许不同承载方式：独立 process host、WebSocket、gRPC 或 in-process runtime。Core 依赖 `CodeModeSessionProvider` trait，不依赖某一种传输。

### V8 不是 shell，也不是权限逃逸口

[`install_globals`](/Users/bytedance/mind/codex/codex-rs/code-mode-runtime/src/runtime/globals.rs:15) 给 cell 安装：

- `tools`、`ALL_TOOLS`；
- `text`、`image`、`audio`、`generatedImage`；
- `store/load`、`notify`、`yield_control`、`exit`；
- timers。

同时移除 `console`、`Atomics`、`SharedArrayBuffer` 和 `WebAssembly`。执行环境没有 Node、filesystem 或 network API。

这意味着 JavaScript 自己不能直接读取文件或联网。它只能调用：

```text
tools.exec_command(...)
tools.apply_patch(...)
tools.mcp__server__tool(...)
tools.collaboration__spawn_agent(...)
```

真正的副作用仍由原 handler 完成，因而原来的 hook、policy、approval、sandbox 和 telemetry 继续生效。V8 isolate 是受限的代码运行环境，但不应把它等同于 OS sandbox；真正的 OS 权限边界仍位于 nested tool 的执行路径。

### [`perform_microtask_checkpoint`](../../../resources/concepts/checkpoint.md) 是什么

这里的 checkpoint 不是模型训练权重快照，也不是 ThreadStore persistence。它是 V8 的 **microtask queue drain point**：在一个明确时点执行已经具备运行条件的 Promise callback 和 `async/await` continuation。

Code Mode 没有浏览器或 Node event loop，外围是 Codex 自己写的 Rust runtime loop。假设 cell 执行：

```javascript
const result = await tools.exec_command({ cmd: "pwd" });
text(result.output);
```

实际过程是：

```text
V8 调用 tools.exec_command
→ 创建 pending Promise，JavaScript async module 暂停
→ Rust delegate 执行 nested tool
→ RuntimeCommand::ToolResponse 回到 V8 runtime
→ resolve_tool_response 把 Promise 标记为 fulfilled
→ perform_microtask_checkpoint()
→ 执行 await continuation
→ text(result.output)
→ 再检查 main module Promise 是否完成
```

[`perform_microtask_checkpoint`](/Users/bytedance/mind/codex/codex-rs/code-mode-runtime/src/runtime/mod.rs:259) 同样位于 tool response、tool error 或 timer callback 处理之后。没有这一步，Promise 虽然已经 fulfilled，排队等待的 continuation 却可能一直没有机会运行，cell 会表现得像卡在 `await`。

可以把它理解成：

```text
checkpoint ≠ 保存现场
checkpoint = “现在把已就绪的 Promise 后续代码跑一遍”
```

### Nested tool 如何重新进入原工具系统

每次 `await tools.some_tool(...)` 会在 V8 runtime 中产生一个 nested-tool callback：

```text
V8 RuntimeEvent::ToolCall
→ CodeModeSessionDelegate
→ CodeModeDispatchBroker
→ turn-scoped CodeModeDispatchWorker
→ call_nested_tool
→ ToolCallSource::CodeMode { cell_id, runtime_tool_call_id }
→ ToolCallRuntime
→ ToolRouter / ToolRegistry
→ 原 CoreToolRuntime handler
→ code_mode_result()
→ resolve JavaScript Promise
```

桥接入口是 [`CodeModeDispatchBroker`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/code_mode/delegate.rs:24)，回到原工具 runtime 的位置是 [`call_nested_tool`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/code_mode/mod.rs:327)。代码明确禁止 Code Mode `exec` 自己递归调用自己。

因此 Code Mode 的关键结构是一个回环：

```text
Registry → CodeModeExecuteHandler → V8 cell
                              │
                              └→ nested callback → ToolCallRuntime → Registry
```

### Yield / wait 与结果回流

如果 JavaScript 在 `yield_time_ms` 内结束，cell 直接返回 `Result`；如果仍在执行，则外层 exec 返回：

```text
Script running with cell ID ...
```

模型随后调用 [`CodeModeWaitHandler`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/code_mode/wait_handler.rs:22)，可以继续等待或 `terminate`。最终 JavaScript 通过 `text/image/audio` 组装的内容被转换成外层 `CustomToolCallOutput`，再由正常 Turn Loop 记录并触发 follow-up sampling。

从架构效果看，Code Mode 把：

```text
模型 → 工具 A → 模型 → 工具 B → 模型 → 工具 C → 模型
```

变为：

```text
模型 → 一段 JavaScript
       ├─ await 工具 A
       ├─ 分支 / 循环 / 并行
       ├─ await 工具 B、C
       └─ 聚合少量结果
     → 模型
```

它减少的是工具编排所需的外层模型往返和中间结果占用；底层能力、安全策略与最终 Agent loop 都没有被替换。

## 阶段 2：把 wire item 归一化为内部 ToolCall

模型 stream 出现 `ResponseEvent::OutputItemDone` 后，[`handle_output_item_done`](/Users/bytedance/mind/codex/codex-rs/core/src/stream_events_utils.rs:289) 调用 [`ToolRouter::build_tool_call`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/router.rs:148)。

这个函数不是简单读取 `name`，而是在协议层做归一化：

| Responses item | 内部 payload | 处理 |
| --- | --- | --- |
| `FunctionCall` | `ToolPayload::Function` | 保留 namespace、name、arguments、call_id 和 encrypted args |
| client-executed `ToolSearchCall` | `ToolPayload::ToolSearch` | 反序列化 search 参数并路由到本地 `tool_search` |
| `CustomToolCall` | `ToolPayload::Custom` | 保留 freeform input |
| hosted `ToolSearchCall` 或普通 message/reasoning | 无 | 返回 `None`，不进入 client tool runtime |

归一化后的 [`ToolCall`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/router.rs:28) 只保留稳定的内部字段：

```text
ToolCall {
  tool_name,
  call_id,
  payload,
  encrypted_function_args,
}
```

这一步隔离了 Responses wire format 和 Core 工具执行接口。以后 wire item 增加变体时，具体 handler 不需要理解整个 Responses 协议。

## 阶段 3：调用并不会立刻阻塞 stream 消费

识别出工具调用后，`handle_output_item_done` 会先：

1. 记录模型产生的原始 tool-call item，使 history 与 rollout 先保持一致。
2. 创建一个 tool future，放进 `in_flight`。
3. 设置 `needs_follow_up = true`。

[`ToolCallRuntime`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/parallel.rs:41) 负责调用级调度：

- 保留产生该调用时的 `StepContext`，避免工具表在未来 step 改变后错误路由旧调用；
- 等待 MCP 等 runtime readiness；
- 处理 cancellation 和 aborted output；
- 根据 handler 的 `supports_parallel_tool_calls()` 决定并行或独占执行；
- 把 fatal error 与可回灌模型的失败转换为不同结果。

并行控制使用一把异步读写锁：支持并行的工具拿 read lock，不支持并行的工具拿 write lock。因此多个 parallel-safe 工具可以同时执行，而一个 non-parallel 工具会与其他工具互斥。

工具 future 用 `FuturesOrdered` 收集。执行可以并行，但 [`drain_in_flight`](/Users/bytedance/mind/codex/codex-rs/core/src/session/turn.rs:2130) 按模型调用顺序把结果写回 conversation，避免并发完成顺序造成 transcript 不稳定。

## 阶段 4：Router 组装 ToolInvocation

[`dispatch_tool_call_with_code_mode_result_inner`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/router.rs:250) 把轻量的 `ToolCall` 扩展成执行需要的 [`ToolInvocation`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/context.rs)：

```text
ToolInvocation {
  session,
  turn,
  step_context,
  cancellation_token,
  tracker,
  call_id,
  tool_name,
  source,
  payload,
}
```

这意味着 handler 不只是收到 JSON arguments。它还能访问：

- 当前 Session 与 TurnContext；
- 当前 step 的 model、permission、environment 和 tool snapshot；
- cancellation token；
- turn diff tracker；
- 调用来源，例如 direct、code mode 或 collaboration plaintext message。

Router 在这里完成 **context binding**，随后才把 invocation 交给 Registry。

## 阶段 5：Registry 不只是 Map

[`ToolRegistry`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/registry.rs:271) 内部确实以 `ToolName → RegisteredTool` 保存 runtime，但 `dispatch_any_with_terminal_outcome` 还提供一层统一 middleware：

```text
统计 active turn tool-call 数量
→ 按 ToolName 查找 runtime
→ 校验 payload kind
→ PreToolUse hook：允许、阻止或重写 input
→ 发出 tool-start lifecycle event
→ telemetry / trace
→ CoreToolRuntime::handle(invocation)
→ PostToolUse hook：接受、阻止或替换 model-visible feedback
→ 记录 additional context
→ 发出 tool-finish lifecycle event
→ 接纳结果并返回 AnyToolResult
```

注册本身也包含规则：trusted built-in 重名通常是实现错误；external tool 遇到保留名字或重复名字会被跳过并记录 collision。`exec_command` 和 `shell_command` 不能被外部默认 namespace 工具覆盖。

所有具体能力最终实现共享的 [`ToolExecutor`](/Users/bytedance/mind/codex/codex-rs/tools/src/tool_executor.rs:106) contract：

```text
tool_name()
spec()
exposure()
supports_parallel_tool_calls()
handle(invocation) → ToolOutput
```

Built-in、MCP、dynamic tool 和 collaboration handler 的执行细节不同，但对 Router / Registry 来说都是 `CoreToolRuntime`。

## 阶段 6：工具结果怎样回到 Agent loop

handler 返回 `ToolOutput` 后，Registry 包装成 `AnyToolResult`；[`AnyToolResult::into_response`](/Users/bytedance/mind/codex/codex-rs/core/src/tools/registry.rs:194) 再按原始 payload 转成模型协议需要的结果：

- `FunctionCallOutput`
- `CustomToolCallOutput`
- `ToolSearchOutput`

`ToolCallRuntime` 还会把可恢复的工具错误转换成 `success = false` 的输出，而不是直接结束整个 turn。只有 `Fatal` 类型错误才向上终止。

工具 future 全部完成后，`drain_in_flight` 调用 `Session::record_conversation_items`，把结果写入 ContextManager 和 rollout。因为 `needs_follow_up` 已经是 `true`，`run_turn` 会用更新后的 history 发起下一次 sampling：

```text
assistant FunctionCall
→ FunctionCallOutput
→ 下一次 Responses request
→ assistant 根据结果继续推理或给出最终答案
```

所以“工具结果回到 ContextManager”不是 Router 自己直接完成的。Router/Registry 产出 protocol-shaped result，Turn Loop 才负责记录它并决定 follow-up sampling。

## 三层职责边界

| 层 | 核心职责 | 不负责什么 |
| --- | --- | --- |
| `ToolRouter` | tool exposure、wire normalization、runtime capability query、context binding、进入 Registry | 不实现具体工具业务，不直接决定 shell 权限 |
| `ToolRegistry` | 注册与冲突、name lookup、hook、telemetry、lifecycle、统一错误/结果边界 | 不实现每种工具的领域行为 |
| `CoreToolRuntime` handler | 参数语义、调用 MCP/子 Agent/内建 runtime、产生 ToolOutput | 不自行组织整个 Agent follow-up loop |

对于 `exec_command`，handler 之后还会进入 `ToolOrchestrator`，继续处理 policy、approval、sandbox、attempt 和 retry。这个安全执行面位于通用工具路由之后，并不是 Router 本身的职责。

## 对问题的精确回答

> 工具路由只负责把 LLM 工具调用转发到注册工具吗？

不只。**最窄意义上的 dispatch 确实是按 `ToolName` 找到 Registry 中的 runtime，但 Codex 的 ToolRouter 同时管理“模型能看到什么”“模型输出怎样被解释”“调用携带什么运行上下文”“能否并行/如何取消”，并把调用交给 Registry 的统一 middleware。** 工具结果的持久化和下一轮 sampling 则由 Turn Loop 完成。
