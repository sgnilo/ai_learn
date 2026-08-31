---
layout: default
title: "AI Workflow Design"
---

# AI Workflow Design

## 学习状态

尚未学习。

## 当前理解

AI workflow 是围绕稳定业务目标设计的流程，不是单次 prompt 或 demo。

[Workflow、Skill 与 Tool](./concepts/workflow-skill-tool.md) 属于不同层次：Skill 提供可复用方法，Tool 提供原子能力，Workflow 则通过状态与控制流保证一次业务实例按约束运行。

## 核心概念

- User goal
- Workflow boundary
- Input / output contract
- Tool usage
- State transition
- Failure recovery
- Human review

## 当前疑问澄清

- Skill 中的步骤是供模型采用的 playbook，不是强制执行边界。
- Workflow 中的步骤是 Runtime 根据 Durable State 强制执行的 control flow。
- 只影响结果质量的方法放 Skill；影响业务正确性、安全或恢复能力的约束进入 Workflow、Policy 或 Tool。

## 实践记录

尚未开始。

## 复盘

尚未复盘。

## 下一步

选一个真实业务场景，拆成可执行 workflow。
