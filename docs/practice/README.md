---
layout: default
title: "AI Code Practice"
---

# AI Code Practice

这个目录用于放 AI / LLM 学习过程中的代码练习。

当前选择 Python 作为主语言，原因是 AI 工程、模型训练、数据处理、评估、RAG、Agent 生态的社区主流工具链都以 Python 为中心。TypeScript 更适合后续做产品界面、MCP 服务或前端集成时再引入。

## 目录结构

```text
practice/
  pyproject.toml
  src/
    ai_practice/
      __init__.py
      tokenizer.py
  tests/
    test_tokenizer.py
```

## 本地运行

不安装额外依赖时，可以直接运行标准库测试：

```bash
cd practice
PYTHONPATH=src python3 -m unittest discover -s tests
```

如果后续需要更完整的 Python 工程体验，可以再安装开发工具：

```bash
cd practice
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
pytest
ruff check .
```

## 练习建议

- `tokenizer.py`：从字符级 tokenizer 开始，理解 encode / decode。
- `embedding.py`：实现简单向量相似度和检索。
- `rag/`：做一个最小 RAG pipeline。
- `agents/`：练习工具调用、状态管理和工作流。
- `training/`：放 PyTorch、LoRA、SFT 相关实验。
