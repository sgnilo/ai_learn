---
layout: default
title: "Progress"
---

# Progress

## Current

| Item | Value |
| --- | --- |
| Active phase | Phase 0：建立 AI / LLM 世界观 |
| Active topics | Tokenizer, Embedding, Transformer |
| Practice policy | 练习代码不作为公开入口；整理后以代码块进入主题笔记 |
| Next review | 接入真实 embedding 模型观察相似度；深入学习 Transformer 的 Q/K/V 和 attention 公式 |

## Phase Status

| Phase | Status | Notes |
| --- | --- | --- |
| [Phase 0](./phase-0-llm-worldview/00-overview.md) | In progress | Tokenizer 第一轮完成；Embedding 已完成 text similarity 练习；Transformer 已建立 attention 与共享参数边界 |
| [Phase 1](./phase-1-ai-product-engineer/00-overview.md) | Not started | AI workflow 和 Agent 产品 |
| [Phase 2](./phase-2-model-fine-tuning/00-overview.md) | Not started | QLoRA / SFT 微调 |
| [Phase 3](./phase-3-ai-system-engineering/00-overview.md) | Not started | Eval、serving、memory、retrieval |
| [Phase 4](./phase-4-research-optional/00-overview.md) | Deferred | 研究主题储备 |

## Log

| Date | Area | What changed | Output | Next |
| --- | --- | --- | --- | --- |
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
