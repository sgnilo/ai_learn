# Embedding

## 学习状态

尚未学习。

## 当前理解

Embedding 可以理解为把 token 转成有语义关系的高维向量坐标。

## 核心概念

- Token id 本身没有语义，需要通过 embedding 转成向量。
- 相似语义通常会在向量空间中距离更近。
- LLM 内部使用 token embedding，RAG 常用 text embedding。
- Embedding 是训练出来的，不是人工规则。

## 待学习问题

- Token embedding 和 text embedding 有什么区别？
- Embedding 维度代表什么？
- 为什么向量相似度可以用于语义检索？
- cosine similarity、dot product、L2 distance 的使用场景是什么？

## 实践记录

尚未开始。

## 关键代码

尚未开始。

## 踩坑

暂无。

## 复盘

尚未复盘。

## 下一步

用一个 embedding 模型计算几组文本向量，观察相似度。
