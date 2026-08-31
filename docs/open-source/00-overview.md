---
layout: default
title: "开源项目研读"
---

# 开源项目研读

这条支线通过阅读、运行和改动真实开源项目，把 AI 与全栈主线中的抽象知识连接到生产代码。重点不是统计读过多少文件，而是能沿一条真实调用链解释设计、验证判断，并提炼可迁移的工程方法。

返回：[学习首页](../README.md) / [研读路线](./roadmap.md) / [Progress](../progress.md)

## 学习状态

首个项目已选择为 [openai/codex](./studies/openai-codex.md)，源码使用本地 [`/Users/bytedance/mind/codex`](/Users/bytedance/mind/codex/README.md) checkout，当前从系统边界与 `Op / EventMsg` 协议骨架开始。

对照项目：[Pi Agent Harness 定位](./studies/pi.md)。Pi 暂用于比较“终端 Agent 产品、可嵌入 harness 与 agent-core runtime”的分层，不改变当前仍以 Codex 为主的学习顺序。

## Agent 的角色

开源项目学习 Agent 负责：

1. 根据当前学习目标筛选项目或接受指定仓库。
2. 快速建立仓库地图，定位入口、核心抽象、状态、I/O 和测试。
3. 每轮只选择一条高价值调用链，提供带文件与符号依据的讲解。
4. 设计可运行的验证，让阅读结论经过测试、日志、断点或最小改动检验。
5. 用提问和复述检查理解，并把结论沉淀为项目研读笔记。

Agent 不用 README 摘要代替源码阅读，也不把目录逐文件翻译成中文。

## 与两条主线的关系

- AI 项目优先服务于当前 AI 主题，例如 Agent runtime、tool calling、eval 或推理。
- Web、数据库与基础设施项目优先服务于当前全栈主题。
- 研读结论记录在本支线；可迁移的概念再链接回 AI 或全栈主题笔记，避免复制维护。
- 三条支线各自只保留一个明确的 `Next`，互不阻塞。

## 研读产物

每个项目在 `docs/open-source/studies/` 下维护一份累计笔记，至少包含：

- 研读目标与版本基线
- 仓库地图与运行方式
- 核心调用链（文件、符号、数据/状态变化）
- 关键设计选择及其 trade-off
- 验证实验与观察证据
- 可迁移结论、仍未解决的问题与下一步

## 当前学习单元

- Current：[openai/codex · 主题 1：系统边界与协议骨架](./studies/openai-codex.md)。
- Next：沿 `cli/src/main.rs → protocol::Op/EventMsg → core::CodexThread` 建立第一张带符号证据的调用图。
