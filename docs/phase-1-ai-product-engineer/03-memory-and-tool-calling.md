---
layout: default
title: "Memory and Tool Calling"
---

# Memory and Tool Calling

## 学习状态

进行中：已建立跨 Coding Agent、业务 Copilot、Durable Workflow、Multi-agent、MCP 与 Code Mode 的 Tool 设计框架。

## 当前理解

Memory 负责保留对任务有价值的信息，Tool calling 负责把模型连接到外部能力。

在 [Workflow、Skill 与 Tool](./concepts/workflow-skill-tool.md) 的分工中，Tool 是带输入输出 contract 的可执行能力；Skill 可以指导模型选择 Tool，而 Workflow 负责跨调用的状态、顺序、等待与恢复。

好的 [Agent Tool Design](./concepts/agent-tool-design.md) 需要同时服务三个对象：让模型容易正确选择，让 Runtime 可以实施 Policy、审批、超时和取消，让真实系统能够审计副作用并在重试或恢复时避免重复执行。

## 核心概念

- Short-term memory
- Long-term memory
- Retrieval memory
- Tool schema
- Tool result
- Permission boundary
- Tool runtime and control plane
- Action identity and idempotency
- Structured error and evidence

## 实践记录

已完成 Tool 设计检查表，下一步选择一个只读 Tool 和一个 mutation Tool，分别设计 schema、result、Policy、错误分类与恢复策略。

## 复盘

尚未复盘。

## 下一步

实现一个带长期记忆和工具调用的最小 Agent；先从 `search_records` 与具备 preview/commit/idempotency 的 mutation Tool 开始。
