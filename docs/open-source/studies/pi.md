---
layout: default
title: "Pi Agent Harness 定位"
---

# Pi Agent Harness 定位

返回：[开源项目研读](../00-overview.md) / [通用研读路线](../roadmap.md) / [openai/codex](./openai-codex.md)

## 当前结论

Pi 不是只能二选一地归类为“Agent 工具”或“Agent 框架”。更准确的分层是：

```text
Pi CLI / interactive coding agent     = 面向用户的 Agent 工具
pi-coding-agent package + SDK         = 可嵌入的 coding-agent harness
pi-agent-core                         = 通用 Agent runtime / framework core
pi-ai                                 = 多模型 Provider 抽象
pi-tui                                = 终端 UI library
extensions / skills / packages        = 扩展生态
```

因此，如果必须给整个项目一个首要标签，应称为：

> **一个自扩展的 coding-agent harness / toolkit，同时交付可直接使用的终端 Agent。**

官方仓库也使用 `Pi Agent Harness` 和 `AI agent toolkit` 描述整体项目，并把 coding-agent CLI、agent runtime 和统一 LLM API 分成独立 package：[项目 README](https://github.com/earendil-works/pi)。

## 为什么看起来既像工具又像框架

### 作为工具

用户全局安装 `pi-coding-agent` 后直接运行 `pi`，获得交互式 terminal coding agent。官方文档将其定义为一个 minimal terminal coding harness，并提供认证、session、内建 coding tools、TUI、skills 和 extensions：[Pi 文档](https://pi.dev/docs/latest)。

从使用者角度，它和 Codex CLI、Claude Code 一样，首先是一个可以完成任务的 Agent 产品。

### 作为框架

开发者可以绕过默认 CLI，直接使用两层 API：

1. `pi-agent-core`：提供 stateful agent、agent loop、tool execution、state management 和 event streaming，是最纯粹的 Agent runtime 层；见 [`pi-agent-core`](https://github.com/earendil-works/pi/tree/main/packages/agent)。
2. `pi-coding-agent` SDK：通过 `createAgentSession()`、`AgentSession`、`SessionManager`、tools 和 `ResourceLoader` 嵌入完整 coding-agent 能力，构建自定义 UI、自动化流程或 sub-agent tool；见 [SDK 文档](https://pi.dev/docs/latest/sdk)。

所以从开发者角度，Pi 也可以作为 Agent framework 使用。

## 但它不属于哪类框架

Pi 的 `agent-core` 更接近一个小型、可组合的 **Agent loop runtime**，不应直接等同于 LangGraph 一类 workflow graph framework：

```text
Pi agent-core
  重点：message state、model streaming、tool loop、events

Workflow framework
  重点：显式 node/edge、durable step、distributed scheduling、workflow recovery
```

Pi 可以通过 SDK、tools 和 extensions 组装 sub-agent、审批、compaction 或工作流，但这些能力不意味着 core 默认提供一套固定的多 Agent 拓扑或 durable workflow engine。

## 判断时使用哪个名称

| 讨论对象 | 推荐称呼 |
| --- | --- |
| 用户在终端运行的 `pi` | Agent 工具 / terminal coding agent |
| `pi-coding-agent` | coding-agent harness；同时包含可嵌入 SDK |
| `pi-agent-core` | Agent runtime / 轻量 Agent 框架核心 |
| 整个 monorepo | Agent harness / toolkit |
| extensions、skills、packages | Pi 的插件与能力扩展系统 |

## 与 Codex 学习路线的对照

Codex 和 Pi 都同时有产品形态与可集成形态，但源码切分方式不同。读 Pi 时，不要从 CLI 功能列表直接推断 agent-core 的职责；应沿 package 依赖从下往上阅读：

```text
pi-ai
  ↓
pi-agent-core
  ↓
pi-coding-agent session / tools / resources
  ↓
interactive CLI / TUI / RPC or SDK integration
```

当前只把 Pi 作为 Codex 研读过程中的对照项目，还没有切换开源支线的 Current，也没有建立本地 revision 基线。

## 版本名称说明

旧资料和旧 checkout 中常见 `badlogic/pi-mono` 与 `@mariozechner/*`；当前官方文档与仓库使用 `earendil-works/pi` 和 `@earendil-works/*`。阅读旧版本时应优先按 package 职责对齐，而不要仅按 npm scope 判断架构变化。

