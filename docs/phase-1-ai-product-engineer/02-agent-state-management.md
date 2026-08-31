---
layout: default
title: "Agent State Management"
---

# Agent State Management

## 学习状态

尚未学习。

## 当前理解

Agent 状态管理决定长任务能否稳定、可恢复、可观察。

[Workflow](./concepts/workflow-skill-tool.md#workflow-在-agent-系统中以什么形态存在) 在系统中通常由静态 Definition、持久化 Workflow Run 和推进状态的 Engine 共同构成。LLM 上下文不是 Workflow Run 的可靠存储。

## 核心概念

- Task state
- Conversation state
- Tool state
- Checkpoint
- Retry
- Idempotency
- Workflow definition version
- Event log / transition history
- Lease / next wakeup

## 实践记录

尚未开始。

## 复盘

尚未复盘。

## 下一步

用一个小任务设计状态字段和状态流转图。
