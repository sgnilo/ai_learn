---
layout: default
title: "AI 学习"
---

# AI 学习

AI 学习是独立的知识主线，覆盖 LLM 基础、AI 产品工程、模型训练、AI 系统工程与可选研究方向。

返回：[学习首页](../README.md) / [AI Roadmap](../roadmap.md) / [Progress](../progress.md)

## 当前状态

进行中。当前位于 Phase 0，正在补齐 `hidden_states -> logits -> loss -> backpropagation -> optimizer update` 的训练闭环。

## 阶段入口

| 阶段 | 目标 | 状态 | 入口 |
| --- | --- | --- | --- |
| Phase 0 | 建立 AI / LLM 世界观 | 进行中 | [Overview](../phase-0-llm-worldview/00-overview.md) |
| Phase 1 | AI Product Engineer | 摸底完成，路线待开始 | [Overview](../phase-1-ai-product-engineer/00-overview.md) |
| Phase 2 | 模型微调与训练 | 未开始 | [Overview](../phase-2-model-fine-tuning/00-overview.md) |
| Phase 3 | AI 系统工程 | 未开始 | [Overview](../phase-3-ai-system-engineering/00-overview.md) |
| Phase 4 | 研究方向 | 暂缓 | [Overview](../phase-4-research-optional/00-overview.md) |

## 当前学习单元

- 当前笔记：[LM Head、Logits、Loss 与训练循环](../phase-0-llm-worldview/04-lm-head-logits-loss.md)
- 下一步：理解 SGD / AdamW 如何根据梯度更新参数。
- Agent 基线：[Agent 工程摸底评估（2026-08-24）](../phase-1-ai-product-engineer/diagnostic-agent-2026-08-24.md)
- 并行主线：[全栈学习](../full-stack/00-overview.md)
- 实战支线：[开源项目研读](../open-source/00-overview.md)

## 分类边界

- LLM、Agent、RAG、模型训练、推理与评估放在 AI 类。
- 通用后端、数据库、鉴权、测试、部署与可观测性放在全栈类。
- 对真实仓库的调用链追踪、运行验证和设计取舍记录放在开源项目研读类。
- 同时涉及多条路线的项目按主要学习目标归档，并在其他路线中建立链接，不重复维护同一份笔记。
