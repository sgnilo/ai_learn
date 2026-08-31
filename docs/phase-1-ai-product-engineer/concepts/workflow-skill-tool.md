---
layout: default
title: "Workflow、Skill 与 Tool"
---

# Workflow、Skill 与 Tool

## 一句话定义

- **Tool**：系统暴露给模型或 Workflow 的一项可执行能力，回答“能做什么”。
- **Skill**：帮助模型完成某类任务的可复用知识与操作方法，回答“通常应该怎么做”。
- **Workflow**：控制一次业务实例如何从开始走到结束的运行结构，回答“这一次必须按什么状态和顺序执行”。

三者的核心区别不是代码量，而是各自拥有的控制权：

> Tool 拥有动作实现，Skill 影响模型决策，Workflow 拥有运行时流程状态。

## 对比

| 维度 | Tool | Skill | Workflow |
| --- | --- | --- | --- |
| 本质 | 能力接口 | 方法与知识包 | 运行时控制结构 |
| 典型内容 | Schema、执行代码、返回值 | Instructions、示例、检查清单、脚本与工具使用方法 | 状态机、DAG、分支、等待、重试、补偿 |
| 主要回答 | 能不能执行这个动作 | 这类问题通常怎么处理 | 当前实例下一步允许做什么 |
| 是否持有业务状态 | 通常不持有；只读取或修改目标资源 | 不应作为真实业务状态来源 | 应持有或引用 Durable State |
| 是否执行副作用 | 可以 | 通常通过 Tool 间接执行 | 编排 Tool 产生副作用 |
| 是否保证执行顺序 | 不负责跨动作顺序 | 可以建议顺序，但不能作为硬保证 | 负责强制顺序和状态转换 |
| 是否负责重试恢复 | 单次调用可做局部重试 | 可以提供处理方法 | 负责跨步骤恢复、超时和补偿 |
| 是否是安全边界 | Tool 内必须复核参数和权限 | 不是，模型可以误解或忽略 | 可调用 Policy 强制约束流程 |
| 生命周期 | 一次调用 | 被加载或适用的一类任务 | 一次可暂停、恢复的业务实例 |

## 为什么 Skill 和 Workflow 看起来重合

两者都可能出现“先查询，再判断，最后执行”这样的步骤描述，但约束强度不同。

Skill 中的步骤是 **playbook**：它告诉模型一个推荐方法，使模型在开放问题上表现得更稳定。模型仍可能根据上下文调整步骤，也可能误解或漏掉某一步。

Workflow 中的步骤是 **control flow**：它根据真实状态决定下一步，未满足前置条件就不能迁移状态。即使模型要求跳过审批，Runtime 也不会允许执行。

因此可以用一个检验问题区分：

> 如果模型没有遵守这条内容，系统只是“结果可能变差”，还是会“破坏业务正确性或安全性”？

- 只是结果可能变差：通常适合放在 Skill。
- 会破坏业务正确性、安全性或可恢复性：必须进入 Workflow、Policy 或 Tool 的确定性代码。

## “Skill 组织 Tool 调用”哪里对，哪里不完整

这个理解部分正确：Skill 可以告诉模型何时选择哪个 Tool、如何准备参数、如何解释结果，也可以附带脚本封装一组常用操作。

但 Skill 不等同于 Tool orchestration engine：

- Skill 可以完全不调用 Tool，例如提供代码审查方法或写作规范。
- Skill 描述的多步调用通常是建议，不自动产生持久化状态和恢复能力。
- Tool 可以由固定代码、Workflow 或用户直接触发，不一定经过 Skill。
- Workflow 可以只有确定性代码和 Tool，完全不需要 LLM 或 Skill。
- 某些框架把“多步 Tool 封装”命名为 Skill，这只是产品术语，仍需检查它是否实际拥有状态与运行时控制权。

在 Codex 一类 Agent Runtime 中，Skill 更接近任务开始时按需加载的专业说明包。它会影响模型随后怎样分析和使用工具，但真正的 Tool 调用仍由 Runtime 执行。

## Workflow 在 Agent 系统中以什么形态存在

生产系统中的 Workflow 通常不是一个单独对象，而是 **Definition、Run State 和 Engine** 三部分共同构成。

### 1. Workflow Definition：静态流程定义

Definition 描述允许有哪些节点、状态和转换，一般存在于代码仓库中，也可能使用 JSON、YAML、DAG 或状态机 DSL 表达。

```ts
const refundWorkflow = defineWorkflow({
  version: 3,
  initial: "received",
  states: {
    received: { run: classifyIntent },
    waiting_for_user: { waitFor: "user_message" },
    checking: { run: checkEligibility },
    waiting_for_approval: { waitFor: "approval_decision" },
    refunding: { run: issueRefund },
    notifying: { run: notifyCustomer },
    completed: { terminal: true },
  },
});
```

节点可以是确定性函数、LLM 调用、Tool 调用、人工审批或定时器。Definition 还应有版本号，因为旧的运行实例可能需要继续使用创建时的流程版本。

### 2. Workflow Run：一次任务的持久化实例

同一个 Definition 每运行一次，就产生一个 Workflow Run。它通常以数据库记录、事件日志和 Tool execution records 的形式存在。

```text
workflow_run
  id: run_123
  definition: refund_workflow
  definition_version: 3
  status: waiting
  current_state: waiting_for_approval
  durable_context: { order_id, calculated_amount, actor_id }
  waiting_for: approval_456
  next_wakeup_at: null
  version: 12
```

常见持久化数据包括：

- 当前状态和 Workflow 版本；
- 经过校验的业务引用和中间结果；
- 等待的外部事件、审批或定时器；
- checkpoint、event log 和 transition history；
- Tool execution id、幂等键、结果或错误；
- lease、重试次数和下次唤醒时间。

因此“Workflow 当前执行到哪里”不能只存在于 LLM 上下文或进程内存中。

### 3. Workflow Engine：推进实例的 Runtime

Engine 是执行 Workflow Definition 的解释器或调度器。它被用户消息、Tool 结果、审批、定时器和队列事件唤醒，然后：

1. 读取 Workflow Run 和对应 Definition 版本；
2. 校验事件是否属于当前等待状态；
3. 执行当前节点；
4. 调用 Policy 检查即将发生的动作；
5. 持久化结果、事件和下一状态；
6. 继续推进，或释放执行权等待下一事件。

```text
User / Timer / Approval / Tool Result
                  │
                  ▼
         Workflow Runtime / Engine
                  │ load run + definition
                  ▼
       ┌── deterministic node
       ├── LLM node → proposed action
       ├── Tool node → Policy → Tool
       └── wait node → persist and yield
                  │
                  ▼
          next state / completed
```

这里的关键是：LLM 可以在一个节点内判断意图、抽取信息、制定候选计划或解释结果，但状态迁移最终由 Runtime 根据结构化结果和确定性约束提交。

## 常见实现形态

Workflow 可以根据问题复杂度采用不同实现，不一定一开始就引入专门框架。

| 形态 | 适用情况 | 局限 |
| --- | --- | --- |
| 普通业务代码 / coordinator function | 短小、同步、失败后可整体重做 | 长等待和进程重启恢复较弱 |
| 状态机 | 审批、订单、退款等状态边界明确 | 大量并行依赖表达较繁琐 |
| DAG / graph | 多步骤依赖、并行 fan-out/fan-in | 动态开放式任务需要额外机制 |
| 事件驱动 Workflow / Saga | 跨服务、长事务、补偿和异步事件 | 基础设施和一致性设计成本较高 |
| Durable execution engine | 长任务、暂停恢复、定时器和自动重试 | 引入框架语义与运维成本 |
| 开放式 Agent loop | Research、探索和动态 Tool 选择 | 边界弱，不适合独自控制高风险副作用 |

开放式 Agent loop 也可以是某个 Workflow 节点，或者被一个外层 Workflow 包住。例如 `researching` 节点允许模型循环调用只读 Tool，但进入 `purchasing` 之前必须回到确定性 Workflow 接受审批和参数校验。

## Plan 不等于 Workflow

LLM 输出的计划，例如“先搜索竞品，再比较价格，最后生成报告”，只是候选 Plan。它只有经过 Runtime 校验、转成允许的节点和依赖、获得 run id 并持久化状态之后，才成为可执行 Workflow 的一部分。

可以用下面的等式记忆：

```text
Workflow = Definition + Durable Run State + Engine
Agentic Workflow = Workflow + 某些由 LLM 执行或选择的节点
```

## Workflow 与通用 Agent 的关系

可以把两者理解为两种不同的控制模式，但 Workflow 不是专属于 LLM 的能力编排形式。

- **通用 Agent**：目标驱动。Runtime 将目标、上下文和 Tool 提供给模型，模型在循环中动态决定下一步。
- **Workflow**：流程驱动。Definition 和当前状态决定允许的下一步，LLM 只在指定节点内提供概率能力。

```text
通用 Agent：Goal → LLM → Tool → Observation → LLM → ... → Final

Workflow：Event → State A → Node → State B → Wait/Tool/LLM → ... → Terminal
```

因此两者不是互斥的产品类型，而是可以嵌套和组合的控制结构：

1. **纯 Workflow**：没有 LLM，例如传统订单审批状态机。
2. **LLM-powered Workflow**：固定流程中的部分节点由 LLM 完成，例如合同抽取后进入确定性审核。
3. **Workflow-wrapped Agent**：外层 Workflow 控制阶段、预算和审批，某个 Research 节点内部运行通用 Agent loop。
4. **Agent-selected Workflow**：通用 Agent 判断用户意图后，只能从白名单中启动退款、下单等预定义 Workflow。
5. **Agent-only loop**：模型自由选择下一步，适合低风险、开放式和可逆任务。

在生产系统中，常见做法不是在 Agent 和 Workflow 之间二选一，而是采用：

> 外层 Workflow 保证边界和可恢复性，内层 Agent 处理开放性与不确定性。

“通用 Agent”本身也需要一个最小 Runtime loop 才能运行，从广义上看这也是一种 Workflow；但工程讨论里通常把下一步主要由模型决定的称为 Agent loop，把下一步主要由代码和状态决定的称为 Workflow。

## 退款案例

### Tool

```text
get_order(order_id)
calculate_refundable_amount(order_id)
issue_refund(order_id, amount, idempotency_key)
send_customer_message(order_id, template_id)
```

每个 Tool 都有明确输入输出。`issue_refund` 会产生外部副作用，因此必须在实现内部再次检查调用身份、订单、金额和幂等键。

### Skill

```text
退款诉求处理方法：
1. 先判断用户意图是否明确。
2. 信息不足时询问原因和订单。
3. 查询订单与退款政策。
4. 向用户清楚解释可退范围。
5. 高风险或例外情况转人工。
6. 不要自行猜测退款金额。
```

它提高模型处理退款问题的稳定性，但不是退款权限本身，也不能保证步骤一定执行。

### Workflow

```text
RECEIVED
  -> INTENT_CONFIRMED
  -> ELIGIBILITY_CHECKED
  -> AMOUNT_CALCULATED
  -> AWAITING_APPROVAL
  -> REFUNDING
  -> REFUNDED
  -> NOTIFICATION_PENDING
  -> COMPLETED
```

Workflow 持久化当前状态，强制只有审批通过才能进入 `REFUNDING`，负责超时、重复事件、崩溃恢复和通知失败后的重试。

模型可以帮助判断意图和解释结果，但不能自行把状态从 `AWAITING_APPROVAL` 改成 `REFUNDING`。

## Policy 是第四个独立角色

Policy 回答的是“这个 actor 在当前上下文中是否允许执行这个 action”。例如：

- 退款金额不得超过可退余额；
- 客服只能操作所属租户订单；
- 超过 1,000 元必须由主管审批；
- CRM 数据不得发送到外部邮箱。

Skill 可以提醒模型遵守这些规则，但不能作为安全边界。Workflow 在状态迁移前调用 Policy，Tool 在真正产生副作用前再做防御性复核。

可以简化为：

```text
Skill 建议模型如何完成任务
              ↓
Workflow 根据 Durable State 控制下一步
              ↓
Policy 判断当前动作是否允许
              ↓
Tool 校验参数并执行动作
```

## 如何决定放在哪里

面对一条新逻辑，依次问：

1. 它是在定义一个外部可执行动作吗？放 Tool。
2. 它是在总结一类任务的专业方法吗？放 Skill。
3. 它涉及跨步骤状态、硬顺序、等待、恢复或补偿吗？放 Workflow。
4. 它涉及身份、权限、额度、数据流或合规吗？放 Policy，并在 Tool 内复核。

同一条业务要求可能同时出现在多个层次，但职责不同。例如“高额退款需审批”：

- Skill 提醒模型提前向用户解释审批要求；
- Workflow 表达 `AWAITING_APPROVAL` 状态；
- Policy 根据金额判断是否需要审批；
- Tool 验证有效 approval id 后才执行退款。

这不是重复实现，而是用户体验、流程控制、安全决策和最终执行的分层防御。

## 常见误区

- 把一段长 Prompt 称为 Workflow：它没有持久化状态，也无法强制迁移规则。
- 把 Tool 做成一个无边界的万能函数：模型获得了过大的参数空间和副作用能力。
- 认为 Skill 能保证安全：Skill 属于模型上下文的一部分，不是确定性执行边界。
- 所有多步骤任务都上 Workflow：开放式 research 可能只需要 Skill 和若干只读 Tool。
- 所有 Tool 调用都让模型自由编排：退款、下单等高风险流程需要确定性 Workflow。

## 相关链接

- [AI Workflow Design](../01-ai-workflow-design.md)
- [Memory and Tool Calling](../03-memory-and-tool-calling.md)
- [Agent Workflow](../../phase-0-llm-worldview/09-agent-workflow.md)
