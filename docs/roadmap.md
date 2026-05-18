---
layout: default
title: "AI 学习路线 Roadmap"
---

# Roadmap

返回：[首页](./README.md) / [Progress](./progress.md) / [Sitemap](./sitemap.md)

从前端工程转向 AI 产品、Agent 系统与模型训练的学习路线。每个主题单独维护笔记，学习过程记录在 [Progress](./progress.md)。

原始路线来源：[ChatGPT 共享路线](https://chatgpt.com/share/6a0972b0-4854-839a-9c2b-ef2c0d8f1de0)

## 总目标

长期目标不是直接走纯模型研究员路线，而是形成下面这条更适合工程背景的成长路径：

```text
AI Product Engineer
→ AI System Engineer
→ AI Workflow Architect
```

核心能力组合：

- 懂真实业务
- 懂工程实现
- 懂 LLM 能力边界
- 能设计 AI workflow
- 能构建 Agent 系统
- 能做数据、训练、评估与部署闭环

## 路线总览

| 阶段 | 时间 | 目标 | 关键产出 |
| --- | --- | --- | --- |
| Phase 0 | 现在 ~ 2 周 | 建立 AI / LLM 世界观 | 能解释 tokenizer、embedding、attention、transformer、inference、RAG、agent workflow |
| Phase 1 | 1 ~ 2 个月 | 成为 AI Product Engineer | 做出一个可长期使用的 AI workflow 产品 |
| Phase 2 | 2 ~ 4 个月 | 进入真正模型训练 | 跑通 QLoRA / SFT 微调、eval、checkpoint、inference、deploy |
| Phase 3 | 4 ~ 8 个月 | 进入 AI 系统层 | 理解 eval、inference serving、memory、retrieval、agent orchestration |
| Phase 4 | 可选 | 进入研究方向 | 学习 RLHF、RLVR、MoE、scaling law、multimodal、pretraining |

## 文档结构

学习计划、知识沉淀、项目说明和资源索引统一放在 `docs/` 目录下；代码练习、测试和工程配置放在根目录的 `practice/` 目录下。

```text
README.md
docs/
  README.md
  phase-0-llm-worldview/
    00-overview.md
    01-tokenizer.md
    02-embedding.md
    03-transformer-attention.md
    04-context-window-kv-cache.md
    05-inference.md
    06-rag.md
    07-function-calling.md
    08-agent-workflow.md
    09-local-model-deployment.md
  phase-1-ai-product-engineer/
    00-overview.md
    01-ai-workflow-design.md
    02-agent-state-management.md
    03-memory-and-tool-calling.md
    04-long-horizon-task.md
    05-merchant-copilot-project.md
    06-ai-sql-assistant-project.md
    07-product-evaluation.md
  phase-2-model-fine-tuning/
    00-overview.md
    01-training-pipeline.md
    02-dataset-design.md
    03-tokenize-padding-truncation.md
    04-pytorch-basics.md
    05-transformers-trainer.md
    06-lora-and-qlora.md
    07-unsloth-practice.md
    08-trl-and-sft.md
    09-axolotl-practice.md
    10-eval-checkpoint-deploy.md
    11-domain-ai-worker-project.md
  phase-3-ai-system-engineering/
    00-overview.md
    01-eval-system.md
    02-rag-eval.md
    03-agent-eval.md
    04-reward-modeling.md
    05-preference-tuning.md
    06-inference-serving.md
    07-batching-kv-cache.md
    08-speculative-decoding.md
    09-persistent-memory.md
    10-multi-agent-system.md
  phase-4-research-optional/
    00-overview.md
    01-rlhf.md
    02-rlvr.md
    03-scaling-law.md
    04-moe.md
    05-diffusion.md
    06-multimodal.md
    07-pretraining.md
    08-alignment-research.md
  projects/
    mini-gpt/
    local-model-lab/
    merchant-copilot/
    qlora-domain-worker/
    eval-system/
  practice/
    README.md
  resources/
    books-and-courses.md
    papers.md
    tools.md
    glossary.md
practice/
  pyproject.toml
  src/
  tests/
```

## Phase 0：建立 AI 世界观

目标：建立真正的 LLM 直觉，而不是只停留在会调 API。

重点主题：

- Tokenizer：文本如何变成 token id
- Embedding：token 如何变成语义向量
- Transformer：模型如何处理上下文
- Attention：模型如何在上下文中建立关联
- Context Window：上下文长度为什么受限
- KV Cache：推理为什么能加速
- Inference：模型生成 token 的过程
- RAG：如何把外部知识接入模型
- Function Calling：模型如何调用工具
- Agent Workflow：agent 与 workflow 的关系

必做实践：

- 手搓 mini GPT：推荐 nanoGPT / minGPT
- 本地部署模型：Ollama、vLLM、LM Studio
- 观察推理指标：显存、token/s、context 长度、量化效果

阶段完成标志：

- 能解释 transformer 的基本工作机制
- 能独立本地部署一个模型
- 理解 inference 的性能瓶颈
- 能区分 agent 与 workflow

## Phase 1：AI Product Engineer

目标：从“会用 AI”进入“能设计 AI workflow”。

重点主题：

- AI workflow 设计
- Agent planning
- Memory
- Tool calling
- Workflow orchestration
- Reflection
- Long-horizon task
- 产品级 AI 体验与质量控制

推荐项目方向：

- 商家经营 AI Copilot
- AI onboarding assistant
- AI 数据分析 agent
- AI SQL assistant
- AI 自动运营建议系统
- AI 客服系统

推荐技术栈：

- LangGraph
- PydanticAI
- OpenAI SDK
- MCP
- Vector DB
- Workflow engine

阶段完成标志：

- 能独立设计 AI workflow
- 能做 agent 状态管理
- 能理解 long-horizon task
- 能完成一个真实 AI 产品闭环

## Phase 2：模型微调与训练

目标：第一次真正训练模型。这里的训练重点不是从零训练 GPT，而是面向实际业务的 fine-tuning。

重点主题：

- LoRA
- QLoRA
- SFT
- Instruction tuning
- Dataset design
- Tokenize
- Eval
- Checkpoint
- Inference
- Deploy

完整链路：

```text
dataset
→ tokenize
→ train
→ eval
→ checkpoint
→ inference
→ deploy
```

推荐工具链：

- [PyTorch](https://pytorch.org)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [TRL](https://huggingface.co/docs/trl/index)
- [Unsloth](https://unsloth.ai)
- [Axolotl](https://axolotl.ai)

最推荐起步路线：

```text
Unsloth + QLoRA
```

推荐训练项目：

- Shopify assistant
- 商家经营模型
- SQL agent
- 商品优化模型
- AI onboarding worker
- 领域 AI Worker

阶段完成标志：

- 能独立准备数据集
- 能完成一次 QLoRA / SFT 微调
- 能做基础 eval
- 能部署自己的微调模型
- 能理解 loss、overfit、hallucination 的关系

## Phase 3：AI 系统工程

目标：理解真正的大模型系统。训练只是 AI 系统中的一部分，更长期的价值在 eval、inference、retrieval、memory、workflow 和 serving。

重点主题：

- Benchmark
- Hallucination eval
- Agent eval
- RAG eval
- Reward modeling
- Preference tuning
- Batching
- KV cache
- Speculative decoding
- Serving
- Distributed inference
- Persistent memory
- Multi-agent system

阶段完成标志：

- 能为 AI 产品设计 eval 体系
- 能评估 RAG / agent 的真实效果
- 能理解 inference serving 的核心瓶颈
- 能设计更稳定的 AI 系统架构

## Phase 4：研究方向（可选）

目标：如果后续确实要进入模型研究，再学习更偏研究的主题。

可选主题：

- RLHF
- RLVR
- Scaling law
- MoE
- Diffusion
- Multimodal
- Pretraining
- Alignment research

当前建议：这一阶段不是现在的最高优先级。更现实的策略是先把 AI workflow 产品、agent 系统、本地模型和 QLoRA 微调跑通。

## 笔记结构

主题笔记保持固定结构：

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

每个阶段的 `00-overview.md` 用来记录：

- 阶段目标
- 当前进度
- 已完成主题
- 未完成主题
- 阶段项目
- 阶段复盘

## 当前优先级

现在优先推进：

1. Phase 0：LLM 基础直觉
2. Phase 1：AI workflow 产品能力
3. Phase 2：QLoRA 微调入门

不建议现在把大量时间投入纯研究主题。当前最有转化价值的是：

```text
AI workflow 产品
+
Agent 系统
+
本地模型
+
QLoRA 微调
+
Eval
```

进度记录维护在 [Progress](./progress.md)。
