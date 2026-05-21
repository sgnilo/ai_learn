---
layout: default
title: "Progress"
---

# Progress

## Current

| Item | Value |
| --- | --- |
| Active phase | Phase 0：建立 AI / LLM 世界观 |
| Active topics | Tokenizer, Embedding, Transformer, LM Head / Logits / Loss |
| Practice policy | 练习代码不作为公开入口；整理后以代码块进入主题笔记 |
| Next review | 学习 LM head 与 logits：hidden_states 如何映射到 vocab_size 候选分数 |

## Phase Status

| Phase | Status | Notes |
| --- | --- | --- |
| [Phase 0](./phase-0-llm-worldview/00-overview.md) | In progress | Tokenizer 第一轮完成；Embedding 已完成 text similarity 练习；Transformer 第一轮完成；当前进入 LM Head / Logits / Loss |
| [Phase 1](./phase-1-ai-product-engineer/00-overview.md) | Not started | AI workflow 和 Agent 产品 |
| [Phase 2](./phase-2-model-fine-tuning/00-overview.md) | Not started | QLoRA / SFT 微调 |
| [Phase 3](./phase-3-ai-system-engineering/00-overview.md) | Not started | Eval、serving、memory、retrieval |
| [Phase 4](./phase-4-research-optional/00-overview.md) | Deferred | 研究主题储备 |

## Log

| Date | Area | What changed | Output | Next |
| --- | --- | --- | --- | --- |
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
