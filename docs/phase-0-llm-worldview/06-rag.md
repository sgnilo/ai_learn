---
layout: default
title: "RAG"
---

# RAG

## 学习状态

尚未学习。

## 当前理解

RAG 通过检索外部知识，把相关上下文提供给模型，减少模型只依赖参数记忆。

## 核心概念

- Document chunking
- Embedding
- Vector DB
- Retrieval
- Rerank
- Context injection
- Grounded answer

## 为什么 RAG 通常不用单 token embedding 检索？

RAG 的目标通常是找出“哪段内容能回答用户问题”。因此检索单位一般不是单个 token，而是句子、段落或 chunk。

单 token 粒度的问题：

- Token 太碎，经常不是完整语义单元，例如 `"un"`, `"believ"`, `"able"` 或中文里的“的”“了”。
- LLM 的 token embedding 是为 next-token prediction 学出来的，不等于专门为语义检索训练的向量。
- 查询和文档的语义通常需要整体匹配，而不是只匹配若干词项。
- token 级索引会显著放大向量数量、检索候选和排序成本，同时引入很多噪音。

生产 RAG 更常见的折中方式：

```text
文档
-> 按标题、段落、语义边界切 chunk
-> 每个 chunk 做 text embedding
-> 检索 top-k chunk
-> rerank
-> 把相关 chunk 注入 LLM 上下文
```

常见 chunk 大小可能是：

```text
200~1000 tokens
```

这里 tokenizer 仍然有作用：它常用于控制 chunk 长度、context 长度和成本。但检索向量通常不是单个 token 的 embedding，而是 chunk / passage / text embedding。

也存在更细粒度的高级检索方案，例如：

- sentence-level embedding
- passage-level embedding
- hybrid search：BM25 词项检索 + dense embedding
- late interaction retrieval，例如 ColBERT
- reranker 对 query-document pair 重新打分

其中 late interaction 方法接近“保留 token 级表示做匹配”的思路，但它使用的是专门训练过的检索模型和上下文化 token 表示，不是简单拿 tokenizer 的 token id 或 LLM embedding matrix 做检索。

可以这样记：

```text
token 级：太碎，噪音大，成本高
整篇级：太粗，容易召回不准
chunk / passage 级：当前最常用折中
token-level late interaction：更复杂的高精度检索方案
```

## 待学习问题

- RAG 和 fine-tuning 的边界是什么？
- chunk size 和 overlap 如何选择？
- rerank 为什么重要？
- 如何评估 RAG 的召回率和答案质量？
- chunk embedding、sentence embedding、late interaction 分别适合什么场景？

## 实践记录

### 2026-05-18：RAG 检索粒度初步理解

本轮完成的理解：

- RAG 会用 tokenizer 控制 chunk 长度，但通常不会用单 token embedding 作为检索单位。
- 单 token 往往语义不完整，噪音和成本都高。
- text embedding 面向整体语义匹配，token embedding 主要服务于模型内部 next-token prediction。
- 生产 RAG 通常使用 chunk / passage 级 embedding，再配合 rerank。

练习代码段：

```text
documents
-> chunks
-> chunk_embeddings
-> vector_search(query_embedding)
-> top_k_chunks
-> rerank
-> context injection
```

## 关键代码

尚未开始。

## 踩坑

- 不要把 RAG 简化成“整篇文档一个 embedding”；生产系统通常会切 chunk。
- 不要以为粒度越细一定越好；token 级检索通常语义太碎、成本太高。
- 不要把 LLM token embedding 直接等同于检索 embedding；两者训练目标不同。

## 复盘

尚未复盘。

## 下一步

用一组本地 Markdown 文档做一个最小 RAG demo。
