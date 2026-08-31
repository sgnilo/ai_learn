---
layout: default
title: "工程学习笔记"
---

# 工程学习笔记

个人工程学习 wiki。AI、全栈与开源项目研读是三条独立分类、同步推进的学习线。

## 索引

| 页面 | 内容 |
| --- | --- |
| [AI Roadmap](./roadmap.md) | AI 学习路线、阶段目标、主题顺序 |
| [Full-stack Roadmap](./full-stack/roadmap.md) | 全栈学习路线、模块目标、实践顺序 |
| [Open-source Roadmap](./open-source/roadmap.md) | 用真实项目训练源码追踪、验证和设计迁移 |
| [Progress](./progress.md) | 学习记录、当前状态、下一步 |
| [Sitemap](./sitemap.md) | 全部页面目录 |

## 学习大类

| 大类 | 目标 | 状态 | 入口 |
| --- | --- | --- | --- |
| AI 学习 | LLM 基础、AI 产品、模型训练与 AI 系统工程 | 进行中 | [AI 学习](./ai/00-overview.md) |
| 全栈学习 | 从前端能力扩展到后端、数据、交付与系统闭环 | 进行中 | [全栈学习](./full-stack/00-overview.md) |
| 开源项目研读 | 沿真实调用链读源码、运行验证并提炼工程取舍 | 进行中 | [开源项目研读](./open-source/00-overview.md) |

## AI 学习阶段

| 阶段 | 主题 | 入口 |
| --- | --- | --- |
| Phase 0 | 建立 AI / LLM 世界观 | [phase-0-llm-worldview](./phase-0-llm-worldview/00-overview.md) |
| Phase 1 | AI Product Engineer | [phase-1-ai-product-engineer](./phase-1-ai-product-engineer/00-overview.md) |
| Phase 2 | 模型微调与训练 | [phase-2-model-fine-tuning](./phase-2-model-fine-tuning/00-overview.md) |
| Phase 3 | AI 系统工程 | [phase-3-ai-system-engineering](./phase-3-ai-system-engineering/00-overview.md) |
| Phase 4 | 研究方向（可选） | [phase-4-research-optional](./phase-4-research-optional/00-overview.md) |

## 当前进度

| 大类 | 当前模块 | 下一步 |
| --- | --- | --- |
| AI | Phase 0 · LM Head / Logits / Loss | Optimizer：SGD / AdamW 如何更新参数 |
| 全栈 | Module 0 · [后端运行时与 HTTP 基础](./full-stack/02-backend-http-foundations.md) | 拆解 `server.listen()` 背后的进程、文件描述符与 socket |
| 开源项目 | [openai/codex · 系统边界与协议骨架](./open-source/studies/openai-codex.md) | 建立 CLI、`Op / EventMsg` 与 `CodexThread` 调用图 |

## 复习方式

先选择 [AI 学习](./ai/00-overview.md)、[全栈学习](./full-stack/00-overview.md) 或 [开源项目研读](./open-source/00-overview.md)，再进入对应阶段、模块或项目。三条学习线共享 [Progress](./progress.md)，但各自维护路线和主题笔记。
