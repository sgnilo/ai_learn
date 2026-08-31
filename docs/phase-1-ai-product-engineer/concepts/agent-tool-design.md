---
layout: default
title: "Agent Tool Design"
---

# Agent Tool Design

## 一句话定义

好的 Agent Tool 是一个**模型容易正确选择、Runtime 能确定性治理、执行后可以观察和恢复的能力 contract**，而不只是把已有 API 换成 function-calling schema。

可以用一句更工程化的话记忆：

> Tool 是概率决策与确定性世界之间的受控边界。

## 四层结构

一个生产级 Tool 通常应拆成四层：

```text
LLM / Workflow
    │ 选择 capability，生成 typed arguments
    ▼
1. Model-facing Tool Contract
   name / description / schema / result semantics
    ▼
2. Tool Runtime
   call id / dispatch / timeout / cancellation / concurrency / lifecycle
    ▼
3. Control Plane
   authentication / authorization / policy / approval / budget / sandbox
    ▼
4. Backend Adapter
   filesystem / shell / database / HTTP API / MCP server / another agent
    ▼
Structured Result + Evidence + Side-effect Receipt
    ▼
Context Manager / Workflow State
```

这四层可以存在于同一个进程，但职责不应混在一个 handler 中：

- Tool Contract 面向模型，解决“何时调用、参数怎么填”。
- Tool Runtime 面向 Agent loop，解决“这次调用如何执行与回流”。
- Control Plane 面向系统治理，解决“当前 actor 是否允许做”。
- Backend Adapter 面向真实系统，解决“动作如何落地”。

## 八项核心原则

### 1. 以稳定意图为边界，不直接暴露底层传输

Tool 应表达一个清楚的 capability：

```text
差：call_api(method, url, headers, body)
好：get_order(order_id)
    preview_refund(order_id, reason)
    issue_refund(order_id, amount, approval_id, idempotency_key)
```

通用 HTTP client 不是不能成为 Tool，但它把 endpoint、权限范围、参数组合和副作用判断全部交给模型，通常只适合受信开发环境或再包一层严格 Policy。

### 2. 粒度围绕“一次可判断的动作”

Tool 既不能万能，也不能碎到模型需要几十次调用才能形成一个有意义 observation。

可以区分三个层级：

| 层级 | 示例 | 适用场景 |
| --- | --- | --- |
| Primitive Tool | `read_file`、`run_command`、`query_rows` | Coding Agent、探索式任务，需要模型动态组合 |
| Capability Tool | `search_orders`、`calculate_refund` | 业务 Copilot，需要稳定领域语义 |
| Workflow Tool | `start_refund_workflow` | 高风险长流程，只允许 Agent 启动受控流程 |

选择原则是：Tool 内部可以封装确定性的机械步骤，但不应偷偷拥有一段模型不可见、不可观察的开放式业务 Workflow。

### 3. Schema 要缩小合法空间

好的输入 schema 应帮助模型避免生成无意义组合：

- 使用 enum、union、required field 和数值范围；
- 使用业务 ID，而不是让模型拼 URL 或数据库条件；
- 区分 mutually exclusive mode，避免十几个 nullable 字段；
- 明确时间、时区、金额单位、路径基准和分页语义；
- 不把认证 token、租户 ID 等可信上下文交给模型填写。

```ts
type RefundRequest =
  | { mode: "full"; orderId: string; approvalId: string }
  | { mode: "partial"; orderId: string; amountMinor: number; currency: "CNY"; approvalId: string };
```

Schema 验证只能证明 shape 合法，不能证明权限、资源状态或业务条件合法；这些仍需在 Policy 和 Backend 中复核。

### 4. 查询与副作用分离

只读 observation、预览和真正 commit 最好是不同能力：

```text
get_order             # read
preview_refund        # pure or reversible calculation
issue_refund          # irreversible side effect
```

这使 Runtime 能对不同类别配置并发、缓存、审批、sandbox 和重试策略，也让模型知道哪一步开始产生真实影响。

高风险 Tool 应尽量采用：

```text
prepare / preview
→ policy decision
→ human or system approval
→ commit with idempotency key
→ receipt
```

### 5. 副作用必须可识别、可幂等或可补偿

每次 mutation Tool 应有稳定的 `action_id` 或 `idempotency_key`，并返回外部系统 receipt。Runtime 重试时先查询已有执行记录，而不是再次盲目执行。

```text
tool_call_id: Agent Runtime 中的一次调用身份
action_id:    业务动作身份，跨重试保持稳定
receipt_id:   外部系统确认动作已发生的证据
```

三者不能混为一谈。模型重新规划可能产生新的 tool call，但若业务意图没变，应复用同一个 action identity。

若外部系统不支持幂等，必须定义补偿动作、人工 reconciliation 或明确的 at-least-once 风险，不能声称 exactly-once。

### 6. Result 是 observation contract，不是 stdout 垃圾桶

Tool result 至少要让 Agent 区分：

```text
status
summary for model
structured data
evidence / resource references
side-effect receipt
retryability
pagination or continuation handle
warnings / partial success
```

一个可用的内部结果 envelope 可以是：

```ts
type ToolResult<T> = {
  status: "ok" | "partial" | "denied" | "failed";
  summary: string;
  data?: T;
  evidence?: Array<{ kind: string; ref: string }>;
  sideEffect?: { actionId: string; receiptId: string };
  error?: { code: string; retryable: boolean; details?: unknown };
  nextCursor?: string;
};
```

最终是否以 JSON、content blocks 或 protocol-specific output 回灌模型，可以由 adapter 决定；内部语义不应只靠一段自然语言猜测。

### 7. 错误要告诉 Runtime 下一步能做什么

错误分类至少应覆盖：

| 错误 | Runtime 含义 |
| --- | --- |
| `invalid_input` | 让模型修正参数，不应原样重试 |
| `not_found` | 重新查询或向用户确认资源 |
| `approval_required` | 进入 approval wait，不是工具失败 |
| `denied` | Policy 终止该动作，不能提示注入绕过 |
| `conflict` | 资源版本已变化，应重新读取再决策 |
| `transient` | 可以按退避策略重试 |
| `timeout` | 结果可能未知；mutation 先按 action id 查账 |
| `partial_success` | 保存已完成子结果，再决定补偿或继续 |
| `cancelled` | 停止执行并报告已经发生的副作用 |

如果所有失败都只是 `"tool failed"`，Agent loop 无法安全恢复，只能碰运气重试。

### 8. 输出必须有界，并支持渐进暴露

Agent Tool 不应一次把整个数据库、仓库或日志塞回 context。常见机制包括：

- pagination / cursor；
- search → select → read 两阶段；
- summary + evidence reference；
- byte/token/row/time limit；
- 大结果保存为 artifact，只回传 URI 和摘要；
- 根据任务动态暴露少量 Tool，而不是把几百个 schema 全塞给模型。

这里同时优化模型选择准确率、context 成本、延迟与数据暴露面。

## 不同 Agent 系统中的侧重点

### Coding Agent

Coding Agent 需要保留探索能力，因此通常适合少量可组合 primitive tools：

```text
search / list / read
apply patch / edit
exec / process session
```

好的设计重点是路径边界、patch 可审计性、命令审批、sandbox、stdout 截断、进程 cancellation 和变更证据。Codex 的 ToolRouter / Registry / policy / approval / sandbox 分层属于这种形态。

### 业务 Copilot

应优先暴露领域 capability，而不是 SQL、HTTP 和任意脚本：

```text
find_customer
get_order
calculate_eligibility
draft_customer_reply
```

mutation 尽量交给确定性 Workflow，Agent 负责识别意图、补齐参数、解释结果和启动流程。

### Durable Workflow Agent

Tool 调用必须与 durable run state 对齐：

- action identity 持久化；
- attempt 与业务 action 分离；
- wait / approval 可以跨进程恢复；
- timeout 后先 reconciliation；
- result 与下一状态以事务、outbox 或可重放事件衔接。

这里“能否安全恢复”比“模型第一次参数是否完美”更重要。

### Multi-agent System

Sub-agent 作为 Tool 时，需要额外 contract：

```text
task objective
delegated capability / authority
input evidence and context boundary
budget / deadline / cancellation
expected deliverable schema
ownership of artifacts
completion / blocked semantics
```

不要只提供 `spawn_agent(prompt)`，否则模型很难判断职责、权限和结果何时可依赖。Sub-agent result 应像其他 ToolResult 一样进入父 Agent 的 context，并保留来源与 evidence。

### MCP / Plugin Ecosystem

可移植性和 provenance 更重要：

- server、tool、connector、account 和 resource identity 明确；
- Tool schema 自描述，错误协议稳定；
- host 保留认证和授权控制，不把 secret 暴露给模型；
- resource link 可追踪到来源；
- capability discovery 有界，支持按需加载。

MCP 统一的是能力交换协议，不会自动替 host 完成业务 Policy、审批、sandbox 和幂等设计。

### Code Mode

JavaScript/Python code 可以在一个 cell 中组织多个 Tool 调用，但 nested call 仍应经过同一 Tool Runtime 和 Control Plane：

```text
cell code
→ brokered tool call
→ router / policy / approval / sandbox
→ Promise result
→ cell continues
```

Code Mode 改善的是组合与数据处理表达力，不应成为绕过工具权限的第二条执行通道。

### Computer-use Agent

GUI 动作不容易天然幂等，所以 observation 与 evidence 很重要：

- 动作前确认窗口、页面、对象和坐标语义；
- 动作后重新观察，不仅相信 click 已成功；
- 保存 screenshot、DOM/accessibility target 或页面状态证据；
- 对付款、发送、删除等最终动作使用明确 commit gate；
- timeout 或画面变化后重新定位，不重复盲点。

## Tool Description 应回答什么

一个有效 description 应让模型快速回答：

1. 什么时候应该调用？
2. 什么时候不应该调用？
3. 调用会读取还是修改什么？
4. 返回什么，可能被截断吗？
5. 需要哪些前置条件或审批？
6. 是否可以并行、重试或取消？

不要把整个内部实现写进 description；只写影响模型选择和参数构造的语义。Runtime guarantee、密钥处理和安全校验属于确定性代码，不能只靠 description 提醒。

## 评估指标

Tool 设计需要用 trajectory 和故障场景验证，而不只测试 handler 单元函数：

| 指标 | 说明 |
| --- | --- |
| Tool selection accuracy | 应调用时能否选对，不应调用时能否克制 |
| Argument validity | Schema 与业务参数一次通过率 |
| Execution success | Backend 成功率与延迟 |
| Recovery success | transient/conflict/timeout 后能否正确恢复 |
| Unsafe action rate | 被 Policy 拦截或错误执行的高风险动作比例 |
| Duplicate side-effect rate | 重试、resume、steer 后重复动作比例 |
| Context cost | Tool schemas 和 results 占用的 token |
| Evidence completeness | 结论是否能追溯到 Tool result 或外部 receipt |

## 设计检查表

设计或 Review 一个 Tool 时依次检查：

1. 名称和描述是否对应一个稳定 capability？
2. 粒度是否与当前 Agent 的控制方式匹配？
3. Schema 是否排除了无意义参数组合？
4. 只读、预览和 commit 是否分开？
5. 谁提供可信身份、租户和授权上下文？
6. Policy、approval、sandbox 分别在哪里执行？
7. mutation 是否有 action id、幂等或补偿策略？
8. timeout 后是否知道动作有没有发生？
9. Result 是否结构化、有界并携带 evidence？
10. 错误是否区分修参、等待、禁止、冲突和可重试？
11. 调用、attempt、结果和副作用是否可观测？
12. Tool 升级后旧 session / workflow 能否继续解释历史记录？

## 常见误区

- 把所有后端 API 一比一暴露给模型，认为 schema 化就完成了 Agent Tool 设计。
- 认为 Tool 越原子越好，忽略模型规划成本、调用延迟和 context 噪声。
- 用一个 `action` 字段承载所有读写操作，导致权限与副作用无法静态分类。
- 把审批逻辑写在 prompt 中，而没有 Runtime gate。
- mutation timeout 后直接重试，没有 action identity 和 reconciliation。
- 把 stdout 或异常字符串当作完整 Tool result。
- 把 sub-agent 当作无类型的 `prompt → text` 函数。
- Code Mode、MCP 或插件拥有绕过主 Tool Runtime 的特殊权限路径。

## 相关链接

- [Memory and Tool Calling](../03-memory-and-tool-calling.md)
- [Workflow、Skill 与 Tool](./workflow-skill-tool.md)
- [Agent State Management](../02-agent-state-management.md)
- [Checkpoint](../../resources/concepts/checkpoint.md)
- [Codex 工具路由与执行回流](../../open-source/studies/openai-codex/04-tool-routing-and-dispatch.md)

