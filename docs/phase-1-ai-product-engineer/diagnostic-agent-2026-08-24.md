---
layout: default
title: "Agent 工程摸底评估（2026-08-24）"
---

# Agent 工程摸底评估（2026-08-24）

## 评估范围

本轮采用开放式系统设计题，覆盖 Agent loop、持久化状态、暂停与恢复、人工审批、工具幂等、Prompt Injection、上下文与记忆、Agent 与确定性 Workflow 的边界、评估体系和 Multi-agent 编排。

## 总体结论

当前 Agent 产品工程能力约为 **L2+，部分维度接近 L3**。

这不是“会接模型 API、会配置工具”的初级水平。已经能够从 Runtime、Policy、Durable State、Evidence、Approval、Idempotency 和 Eval 等产品级约束出发设计 Agent 系统，并能主动把高风险决策从模型移回确定性代码。

若映射到招聘语境，更接近：

- Agent 产品工程方向的强初级到中级早期；
- 约有 1～2 年 Agent 系统实践者应具备的系统设计意识；
- 结合 5 年前端经验，可胜任偏产品交付的中级 AI Product Engineer / Agent Engineer；
- 暂不等同于高级 Agent 基础设施工程师：跨系统 exactly-once、安全能力模型和严谨评估体系仍需要深化。

这里的“年限”只表示能力结构，不推断真实工作年限。

## 跨岗位面试定位（2026-08-28）

以下判断区分“建议投递档位”和“目前已有证据能稳定支撑的档位”。公司职级名称差异很大，因此只使用初级、中级、高级和资深等通用称谓，不直接映射某家公司的数字等级。

| 岗位方向 | 建议主投 | 可以冲刺 | 当前主要限制 |
| --- | --- | --- | --- |
| 前端工程师 | 高级前端 | 资深前端 / 前端负责人早期 | 本轮未专项验证框架原理、性能、工程治理和组织影响力，主要依据 5 年经验与跨层思维 |
| 全栈工程师（偏前端） | 中级全栈；或高级前端兼全栈 | 前端占比高的高级全栈 | 后端基线多数为 L1-L2，生产机制和故障诊断尚未稳定到高级全栈标准 |
| Agent 开发工程师 | 中级 Agent / AI Application / AI Product Engineer | 偏产品交付的高级 AI 应用工程师 | 需要用可运行项目证明 durable execution、幂等、安全、Eval 与线上运营能力 |

更细的角色边界：

- **前端**：5 年经验使高级前端成为合理主投档位，但“资深”通常还要求复杂系统 ownership、性能和工程治理、跨团队影响力。本轮没有直接证据，置信度最低。
- **全栈偏前端**：如果岗位约 60%～80% 是前端，后端以 Node.js、BFF 和业务 API 为主，可以按中高级候选人竞争；如果数据库、分布式系统和生产运维占一半以上，应按中级或中级早期评估，暂不建议以高级后端型全栈自我定位。
- **Agent 产品工程**：Agent Runtime、状态、审批、安全边界与业务风险意识明显强于只会接模型 API 的候选人，适合中级岗位。若能交付一个带恢复、幂等、Eval 和可观测性的生产级项目，可冲击偏产品侧的高级；Agent Platform、模型基础设施和训练方向尚不支持高级定级。

最匹配的个人叙事不是“三个方向各自从头竞争”，而是：

> 5 年前端产品工程能力 + Agent Workflow 产品化能力 + 正在补深的服务端系统能力。

对应的优先定位是 **Agent / AI Product Engineer（前端或全栈偏重）**。它能复用既有前端 seniority，又让 Agent 系统能力成为差异化；其次是前端占比较高的全栈岗位，纯前端高级岗位则作为成熟能力线保留。

最终定级还需要四类尚未完全验证的证据：现场编码质量、真实项目复杂度、生产事故与性能治理、跨团队或业务影响。没有生产项目时，Agent 方向通常会被下调一档；有可验证项目和指标时，系统设计能力才能转化为正式职级。

## 分项结果

| 维度 | 当前判断 | 主要证据 | 下一层缺口 |
| --- | --- | --- | --- |
| Agent Runtime 与 Workflow | L3- | 能设计 loop、checkpoint、挂起、恢复与任务状态机 | 明确 Runtime、Policy、Tool 各自的强制边界 |
| Durable State 与 Memory | L3- | 能区分 authoritative、durable、working context、memory、artifact | 把 summary 始终视为可丢弃的派生视图，并建立确定性校验 |
| Approval 与 Idempotency | L2+ | 能使用 approval id、版本和执行 id 约束恢复与重放 | canonical action、下游幂等键、崩溃窗口与结果复用 |
| Tool Security / Prompt Injection | L2+ | 明确低信任 Tool Output 和确定性硬拦截 | capability、数据流策略，以及“不可审批越权”边界 |
| Agent 与确定性 Workflow 边界 | L3- | 意图和解释交给模型，规则、金额、顺序交给代码 | 将审批放在 Policy/Runtime，Tool 内只做防御性复核 |
| Eval 与发布 | L2+ | 能区分确定性指标和 LLM Judge，并考虑边界用例与线上 trace | 风险切片、标注集、Judge 校准、置信区间、Canary 与自动回滚 |
| Multi-agent 系统 | L2+ / L3- | 能设计 fan-out、领取任务、统一 contract、质量门槛与有限重试 | 证明 Multi-agent 必要性、冲突裁决和成本受控实验 |

## 已经形成的关键能力

### 1. 把 Agent 看成可恢复系统

已经超越“模型反复调用工具”的简单 loop，能够用持久化 session、task state、approval record 和 evidence store 表达暂停、恢复、重试与审计。这是长任务 Agent 的核心工程心智。

### 2. 能区分概率判断与确定性约束

能够让模型负责用户意图、信息抽取、分析和解释，同时把预算、权限、退款金额、步骤顺序和幂等边界交给确定性 Workflow 或 Policy。这是生产 Agent 与 Demo Agent 的分水岭。

### 3. 对业务风险有正确敏感度

能按副作用严重度设计审批，理解数据库事务不能覆盖邮件、支付等外部系统，也知道最终回答正确并不代表执行轨迹安全。

### 4. 具备 Multi-agent 的编排意识

能够想到固定分片、任务领取、占用状态、统一输出 Schema、证据引用、质量准入和有限重试。这已经是分布式任务系统视角，而不是让多个角色自由聊天。

## 需要校准的关键心智模型

### 1. Approval 证明“允许执行什么”，不保证 exactly-once

审批记录应绑定 `tenant / actor / run / action / tool / resource / canonical arguments / version / expiry`。可使用 SHA-256 或 HMAC 指纹保护 canonical payload，但指纹只证明获批内容没有变化。

要尽量实现一次副作用，还需要：

- 持久化 action 状态机和唯一约束；
- 稳定的业务 `idempotency_key`；
- 将同一个已完成 action 的历史结果直接返回；
- 向支付、邮件等下游继续传递同一个幂等键；
- 对“外部执行成功、内部落库前崩溃”的窗口设计查询与对账。

参数或版本发生变化时应强制重新审批。LLM 可以解释 diff，不能决定旧审批是否仍有效。

### 2. Prompt Injection 不是字符串转义问题

网页、邮件和 Tool Output 都应视为不可信数据，但自然语言中的恶意指令无法仅靠过滤、转义或 system prompt 消除。真正的安全边界来自最小能力、结构化输入、数据流策略、参数校验、调用授权和 Tool 内复核。

无权访问或外传的数据应直接拒绝，不能通过一次用户点击把越权行为变成合法行为。审批只适用于“本来有权，但后果重大”的动作。

### 3. Summary 是派生缓存，不是事实来源

模型生成的 summary 可以帮助压缩 Working Context，但不能直接修改 Durable State。涉及订单状态、预算、审批版本和执行结果时，应由确定性代码读取真实业务状态并比较结构化字段；模型只负责解释差异和重新规划。

### 4. 页面复杂并不自动证明需要 Multi-agent

页面高度异构时，模型确实更适合做语义 research；但常见的最佳形态仍可能是：确定性调度器并发调用同一种 Model Worker，再由确定性或受约束的 Reducer 聚合。这属于 model-powered map/reduce，不必包装成自治 Multi-agent。

只有出现角色专门化、独立上下文预算、跨角色迭代协作，或简单 fan-out/fan-in 无法表达的动态计划时，Multi-agent 才更可能值得增加的复杂度。

处理 200 个页面时，建议使用唯一 page id、content hash、队列 lease/visibility timeout、幂等写入和失败队列，而不是只依赖长期持有的锁。Research 输出至少应包含 URL、抓取时间、内容哈希、提取器版本、规范化字段、claim、精确证据位置、置信度、未知项和错误信息。

多个结果冲突时，不应简单地“不置信并重跑”。应先区分：

- 来源本身互相矛盾；
- 同一来源的抽取结果矛盾；
- 数据版本或时间点不同；
- 证据不足。

然后采用定向重读、权威源优先、独立裁决器或人工复核，并保留双方证据。使用相同模型和输入盲目重跑，往往会稳定复现同一个错误。

### 5. Eval 必须同时评估结果、轨迹和副作用

上线标准不能只看答案观感。至少要覆盖：任务成功率、业务最终状态、工具参数、权限与审批、重复/漏执行、证据正确性、延迟、Token/成本和不同风险切片。

比较单 Agent 与 Multi-agent 时，应在相同模型能力、质量目标和并发资源约束下比较覆盖率、抽取准确率、引用正确率、重复/遗漏率、端到端延迟、成本与结果方差。独立上下文可能提升局部专注度，也可能损害全局一致性，必须用实验而不是直觉证明。

## 建议学习顺序

1. [Agent State Management](./02-agent-state-management.md)：实现 durable action state machine、checkpoint、lease、resume 与 replay。
2. [Memory and Tool Calling](./03-memory-and-tool-calling.md)：实现 canonical tool call、capability check、approval binding 与下游 idempotency。
3. [AI Workflow Design](./01-ai-workflow-design.md)：比较 deterministic workflow、model-powered workflow 与开放式 Agent loop。
4. [Product Evaluation](./07-product-evaluation.md)：建立 trajectory、side effect、安全和成本的分层评估集。
5. [Long Horizon Task](./04-long-horizon-task.md)：加入崩溃恢复、超时、重试、补偿与人工介入。
6. [Multi-agent System](../phase-3-ai-system-engineering/10-multi-agent-system.md)：通过受控实验判断何时多 Agent 真正优于单 Agent。

## 第一阶段验收项目

建议用“补货审批 Agent”作为纵向项目，但验收重点不是聊天界面，而是系统不变量：

- 任意时刻重启 Runtime 都能继续执行；
- 同一审批事件和工具动作被重复投递不会重复下单；
- 参数或库存版本变化会使旧审批失效；
- 网页中的指令无法扩大工具权限或泄露 CRM 数据；
- 每次结论都能定位到原始证据；
- 单 Agent、确定性 fan-out 和 Multi-agent 三种实现能在统一 Eval 上比较。

完成这些条件，才算从 L2+ 稳定进入 L3。
