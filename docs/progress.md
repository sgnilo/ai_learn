---
layout: default
title: "Progress"
---

# Progress

## Current

| Item | Value |
| --- | --- |
| Active tracks | AI 学习、全栈学习、开源项目研读 |
| AI current | Phase 0：LM Head / Logits / Loss |
| AI next | 学习 optimizer：SGD / AdamW 如何基于梯度更新参数 |
| Full-stack current | Module 0：[后端运行时与 HTTP 基础](./full-stack/02-backend-http-foundations.md) |
| Full-stack next | 单元 0.1：拆解 `server.listen()` 背后的 process、file descriptor 与 socket |
| Open-source current | [openai/codex · 主题 4：工具路由与执行回流](./open-source/studies/openai-codex/04-tool-routing-and-dispatch.md) |
| Open-source next | 对照一个无副作用 handler 与 `exec_command`，验证 Registry middleware 和安全执行面的边界 |
| Practice policy | 练习代码不作为公开入口；整理后以代码块进入主题笔记 |

## AI Phase Status

| Phase | Status | Notes |
| --- | --- | --- |
| [Phase 0](./phase-0-llm-worldview/00-overview.md) | In progress | Tokenizer 第一轮完成；Embedding 已完成 text similarity 练习；Transformer 第一轮完成；当前进入 LM Head / Logits / Loss |
| [Phase 1](./phase-1-ai-product-engineer/00-overview.md) | Baseline assessed | Agent 工程约 L2+；路线尚未正式开始 |
| [Phase 2](./phase-2-model-fine-tuning/00-overview.md) | Not started | QLoRA / SFT 微调 |
| [Phase 3](./phase-3-ai-system-engineering/00-overview.md) | Not started | Eval、serving、memory、retrieval |
| [Phase 4](./phase-4-research-optional/00-overview.md) | Deferred | 研究主题储备 |

## Full-stack Module Status

| Module | Status | Notes |
| --- | --- | --- |
| [Baseline](./full-stack/01-server-side-panorama.md) | First pass complete | 服务端全景作为导航图 |
| [Module 0](./full-stack/02-backend-http-foundations.md) | In progress | Runtime、进程、Socket、网络与 HTTP |
| Module 1 | Not started | 流量入口与请求管线 |
| Module 2 | Not started | API 语义与应用架构 |
| Module 3 | Not started | 数据库、Transaction 与 ORM |
| Module 4 | Not started | Cache、Queue 与一致性 |
| Module 5 | Not started | Authentication、Authorization 与安全 |
| Module 6 | Not started | Container、部署与 CI/CD |
| Module 7 | Not started | 可观测性、性能与可靠性 |
| Module 8 | Not started | 产品化全栈项目 |

## Open-source Study Status

| Item | Status | Notes |
| --- | --- | --- |
| [研读方法](./open-source/roadmap.md) | Ready | 以问题、调用链、运行证据和复述形成闭环 |
| [openai/codex](./open-source/studies/openai-codex.md) | In progress | 本地 revision `2df6705`；主题 1 调用图已完成，待运行两个聚焦测试 |

## Log

| Date | Area | What changed | Output | Next |
| --- | --- | --- | --- | --- |
| 2026-08-27 | Phase 1 / Agent Tool Design | 建立跨 Agent 系统的 Tool 四层模型与设计准则，覆盖 capability 粒度、schema、读写分离、Policy/approval/sandbox、action identity、结构化错误、证据、有界输出，以及 Coding Agent、Workflow、Multi-agent、MCP、Code Mode 的差异 | [Agent Tool Design](./phase-1-ai-product-engineer/concepts/agent-tool-design.md), [Memory and Tool Calling](./phase-1-ai-product-engineer/03-memory-and-tool-calling.md) | 选择一个只读 Tool 和一个 mutation Tool，完成 contract 与故障恢复练习 |
| 2026-08-25 | Open-source / Pi | 区分 Pi 的多层身份：终端 coding-agent 工具、可嵌入 coding-agent harness/SDK、agent-core runtime，以及 LLM/TUI/extension 支撑包；作为 Codex 的对照项目，不切换当前主线 | [Pi Agent Harness 定位](./open-source/studies/pi.md) | 若正式研读，先拉取本地仓库并锁定 revision，再追踪 `AgentSession → Agent → agent loop → tool execution` |
| 2026-08-25 | Open-source / openai/codex | 梳理 checkpoint 谱系：compaction history base、MCP provenance、rollout projection cursor、external import CAS、metadata backfill watermark、SQLite WAL 与 V8 microtask；区分 durable rollout substrate 和整 Runtime 快照 | [Checkpoint](./resources/concepts/checkpoint.md) | 沿 resume 调用链验证 compaction checkpoint、suffix replay 与 rollback survival semantics |
| 2026-08-25 | Open-source / openai/codex | 补齐 Code Mode：ToolMode exposure、外层 `exec/wait`、thread-owned CodeModeSession、V8 cell、nested-tool delegate 回环、yield/wait 与原安全执行路径复用 | [真实架构全景图](./open-source/studies/openai-codex/00-real-architecture-map.md), [工具路由与执行回流](./open-source/studies/openai-codex/04-tool-routing-and-dispatch.md) | 对照集成测试验证 nested `exec_command` 与 `wait` 回流 |
| 2026-08-24 | Open-source / openai/codex | 拆解工具的双向路由：step 构建时的 exposure/spec、Responses item 归一化、并发调度、Registry middleware、ToolOutput 回灌与 follow-up sampling | [工具路由与执行回流](./open-source/studies/openai-codex/04-tool-routing-and-dispatch.md) | 对比无副作用 handler 与 `exec_command` 的执行路径 |
| 2026-08-24 | Open-source / openai/codex | 基于本地 revision 绘制完整 runtime 架构图，覆盖宿主适配、App Server、Core command loop、模型/工具闭环、安全执行、扩展、多 Agent、持久化和事件回传 | [真实架构全景图](./open-source/studies/openai-codex/00-real-architecture-map.md) | 用两个聚焦测试验证图中的 start/steer 与异步事件边界 |
| 2026-08-24 | Open-source / openai/codex | 细化一次 TUI 输入的三条路径：App Server request、Core command admission 与异步 event lifecycle；标注 start/steer 并发分支、ID 关联和测试证据 | [系统边界与协议骨架](./open-source/studies/openai-codex/01-system-boundary-and-protocol.md) | 运行 concurrent submission 与 `TurnStarted` prewarm 聚焦测试 |
| 2026-08-24 | Open-source / openai/codex | 以当前源码 revision 为基线，将大型 monorepo 拆为协议、turn loop、模型、工具、安全、持久化、扩展、多 Agent、App Server/SDK 和测试九个主题 | [openai/codex 源码学习路线](./open-source/studies/openai-codex.md) | 从 CLI、`Op / EventMsg` 与 `CodexThread` 建立第一张调用图 |
| 2026-08-24 | Open-source Learning | 新增开源项目研读支线和学习 Agent，建立选题、仓库地图、调用链、验证、复述与迁移闭环 | [开源项目研读](./open-source/00-overview.md), [研读路线](./open-source/roadmap.md) | 选择首个项目和一个可验证的源码问题 |
| 2026-08-24 | Phase 1 / Agent Diagnostic | 完成 Agent Runtime、状态、审批、Tool Security、Eval 与 Multi-agent 的开放式摸底，基线为 L2+，部分维度接近 L3 | [Agent 工程摸底评估](./phase-1-ai-product-engineer/diagnostic-agent-2026-08-24.md) | 深化 durable action、跨系统幂等、Capability Policy 和 trajectory eval |
| 2026-08-17 | Full-stack / Diagnostic | 完成第一轮开放场景摸底，记录 Runtime、数据库并发、安全、容器与可靠性等模块的 L1-L2 基线和优先缺口 | [全栈摸底评估](./full-stack/diagnostic-2026-08-17.md) | 从 `server.listen()` 背后的 process、file descriptor 与 socket 开始深挖 |
| 2026-08-17 | Full-stack / Depth Roadmap | 将全栈路线从组件覆盖型重构为 L0-L4 深度型路线，要求机制、观察、故障注入、取舍与复述闭环 | [Full-stack Roadmap](./full-stack/roadmap.md), [后端运行时与 HTTP 基础](./full-stack/02-backend-http-foundations.md) | 从 `server.listen()` 背后的 process、file descriptor 与 socket 开始 |
| 2026-08-17 | Full-stack / Server-side Panorama | 从请求、数据、交付三条路径串起网关、中间件、路由、View、ORM、数据库、容器化与部署 | [服务端全景图](./full-stack/01-server-side-panorama.md) | 进入后端运行时与 HTTP 基础，用最小服务验证请求链路 |
| 2026-08-17 | Learning Structure | 新增全栈学习大类，与 AI 学习分轨并同步推进 | [AI 学习](./ai/00-overview.md), [全栈学习](./full-stack/00-overview.md), [Full-stack Roadmap](./full-stack/roadmap.md) | 全栈先学习后端运行时与 HTTP 请求链路；AI 继续 optimizer |
| 2026-05-22 | Phase 0 / Backpropagation Practice | 搭建 gradient / backprop 练习测试，覆盖单参数梯度、输入梯度、两层链式法则和 LM head backward | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/tests/test_gradient_backprop.py` | 实现 `practice/src/ai_practice/gradient_backprop.py` 到测试通过 |
| 2026-05-21 | Phase 0 / Backpropagation | 记录导数、链式法则、输入梯度传递、矩阵乘法梯度和参数更新不会重复叠加的心智模型 | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md) | 学习 optimizer 与 AdamW |
| 2026-05-21 | Phase 0 / LM Head Practice | 完成 next-token loss 练习实现，串起 logits/labels shift、softmax、NLL 和 shifted cross entropy 平均 loss | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/src/ai_practice/next_token_loss.py` | 学习反向传播与梯度更新 |
| 2026-05-21 | Phase 0 / LM Head Practice | 完成 logits softmax 练习实现，理解每个位置独立得到 vocab probability distribution | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/src/ai_practice/softmax_logits.py` | 学习 label shifting |
| 2026-05-21 | Phase 0 / LM Head Practice | 搭建 logits softmax 练习测试，覆盖单行 logits 到概率，以及按位置逐行 softmax | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/tests/test_softmax_logits.py` | 实现 `practice/src/ai_practice/softmax_logits.py` 到测试通过 |
| 2026-05-21 | Phase 0 / LM Head Practice | 完成 LM Head 练习实现，手写 hidden_states 到 vocab logits 的矩阵投影 | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/src/ai_practice/lm_head.py` | 学习 logits 到 softmax probability |
| 2026-05-21 | Phase 0 / LM Head Practice | 搭建 LM Head 练习测试，覆盖 hidden_states 到 vocab logits 的矩阵投影和输出 shape | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md), `practice/tests/test_lm_head.py` | 实现 `practice/src/ai_practice/lm_head.py` 到测试通过 |
| 2026-05-21 | Phase 0 / LM Head | 记录训练主链路总览，串起 hidden_states、LM head、logits、labels、loss、backpropagation 和 optimizer update | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md) | 学习 LM head 与 logits |
| 2026-05-21 | Phase 0 / Curriculum | 纠正 Transformer 后的学习顺序，新增 LM Head / Logits / Loss 章节，将 Context Window / KV Cache 顺延到训练闭环之后 | [LM Head、Logits、Loss 与训练循环](./phase-0-llm-worldview/04-lm-head-logits-loss.md) | 学习 LM head 与 logits |
| 2026-05-21 | Phase 0 / Transformer | 完成 Transformer 与 Attention 章节复盘，串起 token ids、embedding、Q/K/V、causal mask、FFN、residual、LM head 到 next token | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 补齐 LM Head / Logits / Loss |
| 2026-05-21 | Phase 0 / Transformer Practice | 完成 Self-Attention 与 TransformerBlock 练习，串起 QK score、causal attention 和 Pre-Norm residual forward | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md), `practice/src/ai_practice/self_attention.py`, `practice/src/ai_practice/transformer_block.py` | 阅读真实 causal self-attention 实现 |
| 2026-05-19 | Phase 0 / Transformer | 记录 Multi-Head Attention 的动机：多套相似度空间、多张 attention 图，而不是单纯增加参数 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 完成 self-attention 与 TransformerBlock 练习 |
| 2026-05-19 | Phase 0 / Transformer Practice | 搭建 Self-Attention 与 TransformerBlock 巩固练习，覆盖 Q/K score、causal self-attention 和 Pre-Norm forward 顺序 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md), `practice/tests/test_self_attention.py`, `practice/tests/test_transformer_block.py` | 实现两个练习到测试通过 |
| 2026-05-19 | Phase 0 / Transformer Practice | 完成 Causal Mask 练习实现，串起下三角 mask、masked softmax 和 value 加权求和 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md), `practice/src/ai_practice/causal_mask.py` | 阅读真实 causal self-attention 实现 |
| 2026-05-19 | Phase 0 / Transformer Practice | 搭建 Causal Mask 练习测试，覆盖下三角 mask、masked scores、softmax、weighted sum 和 masked attention | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md), `practice/tests/test_causal_mask.py` | 实现 `practice/src/ai_practice/causal_mask.py` 到测试通过 |
| 2026-05-19 | Phase 0 / Transformer | 记录 Causal Mask 的下三角实现，以及 decoder-only LLM 与 encoder-only、encoder-decoder 的区别 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 阅读真实 causal self-attention 实现 |
| 2026-05-19 | Phase 0 / Transformer | 记录 FFN 升维、`W_up` 中间特征通道和 activation 非线性筛选机制 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 深入 ReLU、GELU、SiLU、SwiGLU |
| 2026-05-19 | Phase 0 / Embedding Practice | 完成 text embedding 相似度练习，拆分 embedding backend、cosine 计算和候选排序逻辑 | [Embedding](./phase-0-llm-worldview/02-embedding.md), `practice/src/ai_practice/text_embedding.py` | 接入真实 embedding 模型观察相似度 |
| 2026-05-18 | Phase 0 / Embedding | 记录 L2、cosine、dot product 的区别，以及 text embedding 常用 cosine/归一化点积的原因 | [Embedding](./phase-0-llm-worldview/02-embedding.md) | 完成 text embedding 相似度练习实现 |
| 2026-05-18 | Phase 0 / Transformer | 记录 self-attention 只作用于当前上下文，跨上下文规律通过共享参数沉淀 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 深入 Q/K/V 和 attention 公式 |
| 2026-05-18 | Phase 0 / Transformer | 建立 Transformer block 总览，串起 attention、FFN、residual、norm 和 shape 不变性 | [Transformer 与 Attention](./phase-0-llm-worldview/03-transformer-attention.md) | 逐个拆 Q/K/V 和 attention 公式 |
| 2026-05-18 | Phase 0 / Embedding | 记录参数规模、embedding/Transformer 参数职责、数据质量和能力上限关系 | [Embedding](./phase-0-llm-worldview/02-embedding.md) | 用真实 embedding 模型观察语义相似度 |
| 2026-05-18 | Phase 0 / Embedding | 串起 LLM 训练与推理主链路，区分训练更新权重和推理固定权重生成 | [Embedding](./phase-0-llm-worldview/02-embedding.md) | 学习 text embedding 相似度和生成采样参数 |
| 2026-05-18 | Phase 0 / Embedding Practice | 完成最小 embedding lookup 练习，串起 token、sequence、batch 三层索引和 shape | [Embedding](./phase-0-llm-worldview/02-embedding.md), `practice/src/ai_practice/embedding.py` | 继续学习 text embedding 和向量相似度 |
| 2026-05-18 | Phase 0 / Embedding | 更新待学习项，沉淀 embedding matrix、batch tensor、padding mask、语义训练写入机制 | [Embedding](./phase-0-llm-worldview/02-embedding.md) | 做最小 embedding lookup coding 练习 |
| 2026-05-17 | Phase 0 / Tokenizer | 完成字符级 tokenizer 第一轮实践，理解 vocab、token id、encode/decode、OOV 和 `<unk>` | [Tokenizer](./phase-0-llm-worldview/01-tokenizer.md) | 清理练习代码后，对比真实 BPE tokenizer 的中文、英文、代码切分 |
| 2026-05-17 | Docs | 创建分阶段文档集合并迁入 `docs/` | [Roadmap](./roadmap.md), [Sitemap](./sitemap.md) | 继续按阶段维护主题笔记 |
