---
layout: default
title: "Context Window 与 KV Cache"
---

# Context Window 与 KV Cache

## 学习状态

准备开始。

## 当前理解

Context window 决定模型一次能处理多少 token，KV cache 用于加速自回归推理。

## 核心概念

- Context length
- Attention complexity
- Prefill
- Decode
- KV cache
- Long context

## 待学习问题

- 为什么 context 越长显存越高？
- Attention 的计算复杂度为什么和 token 数相关？
- KV cache 为什么能加速生成？
- Prefill 和 decode 阶段有什么区别？

## 实践记录

尚未开始。

## 关键代码

尚未开始。

## 踩坑

暂无。

## 复盘

尚未复盘。

## 下一步

本地部署模型后观察不同上下文长度下的显存和速度变化。
