---
layout: default
title: "Overview"
---

# Overview

这套文档用于沉淀从前端工程师转向 AI-native 产品、Agent 系统、模型训练与 AI 系统工程的学习计划和知识点。

## 文档定位

- `docs/`：学习路线、阶段笔记、项目说明、资源索引和复盘沉淀。
- `practice/`：代码练习、测试和 Python 工程配置。
- `docs/projects/`：项目型学习任务的目标、待完成事项和实践记录。
- `docs/resources/`：课程、论文、工具和术语表。

## 当前主线

当前优先级是先形成能落地的 AI 工程能力：

1. Phase 0：建立 LLM 基础直觉。
2. Phase 1：掌握 AI workflow 和 Agent 产品设计。
3. Phase 2：跑通 QLoRA / SFT 微调入门。
4. Phase 3：逐步补齐 eval、serving、memory、retrieval 和 agent orchestration。
5. Phase 4：作为研究方向储备，不作为当前最高优先级。

## 阅读方式

面向复习时，建议按这个顺序阅读：

1. [Roadmap](./roadmap.md)：确认整体目标和阶段顺序。
2. 阶段 `00-overview.md`：确认阶段目标、主题清单和当前进度。
3. 具体主题笔记：补充理解、实践记录、代码片段和踩坑。
4. [Practice](./practice/README.md)：用代码练习巩固概念。
5. [Sitemap](./sitemap.md)：按目录快速定位文档。

## 笔记规范

每篇主题笔记建议保持固定结构：

```text
# 标题

## 当前理解

## 核心概念

## 实践记录

## 关键代码

## 踩坑

## 复盘

## 下一步
```

## GitHub Pages 准备

这个目录按静态 Markdown 文档站点组织。`index.md` 作为 GitHub Pages 首页，`README.md` 作为仓库浏览入口，`roadmap.md` 作为完整路线，`sitemap.md` 作为目录索引。后续如果接入 MkDocs、Docsify 或 Docusaurus，目录结构不需要大改。
