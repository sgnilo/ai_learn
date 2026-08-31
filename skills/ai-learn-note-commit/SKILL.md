---
name: ai-learn-note-commit
description: Update the ai_learn project notes from the current learning conversation and create a local git commit. Use when the user asks to end or wrap up a learning conversation, remember notes, record understanding, update the docs, save progress, or "记笔记并提交commit" in /Users/bytedance/mind/ai_learn.
---

# AI Learn Note Commit

## Workflow

Use this skill only inside `/Users/bytedance/mind/ai_learn`.

1. Inspect the current conversation and identify the learning topic.
2. Update the matching topic note under `docs/phase-*`, `docs/full-stack`, `docs/open-source/studies`, or `docs/projects`.
3. Preserve the matching note structure:
   - topic notes: `当前理解`, `核心概念`, `实践记录`, `关键代码`, `踩坑`, `复盘`, `下一步`
   - open-source studies: `研读目标与版本`, `仓库地图`, `核心调用链`, `设计取舍`, `验证实验`, `我的复述与纠偏`, `可迁移结论`, `未解决问题`, `下一步`
4. Put each new exercise under `实践记录` with:
   - date and title
   - short understanding summary
   - relevant code snippet if code was discussed or changed
   - relevant test or verification snippet when available
5. Update overview/progress files when the topic status changed:
   - the matching track or phase `00-overview.md`
   - the matching track `roadmap.md`
   - `docs/sitemap.md` only when files are added, removed, or renamed
6. Run cheap verification:
   - For Python practice changes: `cd practice && PYTHONPATH=src python3 -m unittest discover -s tests`
   - For docs-only changes: inspect the edited section with `sed` and check `git diff`
7. Review `git status --short` and avoid committing unrelated user changes unless they are part of the learning notes just updated.
8. Create a local commit for the completed note update.

## Note Style

Keep notes concise and cumulative. Prefer clarified understanding over transcript-style summaries.

Use concrete examples from the conversation. When the user corrected a misconception, record both the corrected concept and the pitfall.

For code snippets, include only the smallest useful snippet. Do not paste entire files unless the whole file is the exercise artifact.

For shape/math topics, record exact shapes and names. Example:

```text
embedding_matrix: [vocab_size, hidden_size]
sequence embeddings: [seq_len, hidden_size]
batch embeddings: [batch_size, seq_len, hidden_size]
```

## Commit Rules

Before committing:

1. Run `git diff --stat`.
2. Review the relevant diff.
3. Stage only intended files.
4. Commit with a concise message in this style:

```text
docs: record embedding learning notes
```

If the worktree contains unrelated modifications, leave them unstaged and mention them in the final response.

If verification cannot run, still commit only if the note changes are straightforward docs updates; mention the skipped verification in the final response.
