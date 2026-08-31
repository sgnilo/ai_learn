---
layout: default
title: "全栈学习"
---

# 全栈学习

全栈学习是独立的知识主线，目标是从已有前端能力出发，补齐后端、数据、系统交付与生产工程能力。

返回：[学习首页](../README.md) / [Full-stack Roadmap](./roadmap.md) / [Progress](../progress.md)

## 当前状态

进行中。[服务端全景图](./01-server-side-panorama.md) 已作为知识导航建立，当前进入 [后端运行时与 HTTP 基础](./02-backend-http-foundations.md)，从“会用”下钻到机制、诊断与设计取舍。

当前基线：[全栈摸底评估（2026-08-17）](./diagnostic-2026-08-17.md)

## 学习目标

- 核心主题不只会配置和调用，还能解释内部机制与状态变化。
- 能通过日志、metric、trace、query plan 和系统工具观察真实行为。
- 能主动制造超时、断连、并发冲突和依赖故障，并定位根因。
- 能从一致性、性能、复杂度和运维成本解释设计取舍。
- 能独立完成一个可上线、可诊断、可恢复的全栈产品闭环。

## 模块总览

| 模块 | 主题 | 状态 |
| --- | --- | --- |
| Baseline | 服务端全景图 | 第一轮完成 |
| Module 0 | Runtime、进程、Socket、网络与 HTTP | 进行中 |
| Module 1 | 流量入口与请求管线 | 未开始 |
| Module 2 | API 语义与应用架构 | 未开始 |
| Module 3 | 数据库、Transaction 与 ORM | 未开始 |
| Module 4 | Cache、Queue 与一致性 | 未开始 |
| Module 5 | Authentication、Authorization 与安全 | 未开始 |
| Module 6 | Container、部署与 CI/CD | 未开始 |
| Module 7 | 可观测性、性能与可靠性 | 未开始 |
| Module 8 | 产品化全栈项目 | 未开始 |

详细顺序和完成标准见 [Full-stack Roadmap](./roadmap.md)。

## 与其他学习线同步推进

同步推进不要求三条路线学习时长完全相等，而是让每条线始终只有一个清晰的当前单元：

```text
AI：一个概念或一次练习
↕
全栈：一个概念或一次练习
↕
开源项目：一条调用链和一次验证
↕
Progress：统一记录下一步
```

当前配对单元：

- AI：[LM Head、Logits、Loss 与训练循环](../phase-0-llm-worldview/04-lm-head-logits-loss.md)
- 全栈：[后端运行时与 HTTP 基础](./02-backend-http-foundations.md)
- 开源项目：[openai/codex · 系统边界与协议骨架](../open-source/studies/openai-codex.md)
