---
name: open-source-project-learning
description: Guide evidence-based learning from an open-source repository by mapping its architecture, tracing one source-level execution path, running a small verification, and recording durable notes. Use in the ai_learn repository when the user wants to study, read, or understand an open-source project rather than merely review it for a change.
---

# Open Source Project Learning

Use this skill only inside `/Users/bytedance/mind/ai_learn`.

## Outcome

Help the learner understand one bounded question about a real repository through source evidence and an observable experiment. Optimize for a reusable mental model, not repository coverage or a long summary.

## Start

Accept a repository URL/path and the learner's question when provided. If the project is not chosen, recommend a small set based on the current AI and full-stack `Next` items, then let the user choose before downloading or persisting external code.

For remote repositories, identify and record an immutable revision. Inspect remotely or use a temporary checkout unless the user asks to keep a clone. Do not modify the upstream checkout except for an explicitly agreed, reversible learning experiment.

Read the repository's own contributor or agent instructions before inspecting implementation.

## Learning Loop

1. Convert a broad request into one question that can be answered by a vertical execution path in one or two sessions.
2. Establish only the map needed for that question: entrypoint, relevant modules, state and I/O boundaries, tests, and the minimal run command.
3. Trace from external input to observable output. Cite concrete repository-relative files and symbols at every important hop; distinguish facts from hypotheses.
4. Ask the learner to predict a key behavior before revealing the implementation when that improves understanding.
5. Run at least one focused test, log/breakpoint observation, failure injection, or reversible change. Explain what the evidence proves and what it does not.
6. Ask for a short learner restatement, correct misconceptions, and identify one transferable design insight.
7. Update the matching note under `docs/open-source/studies/<owner>-<repo>.md` when the user asks to record progress or finish the session. Update `docs/open-source/00-overview.md` and `docs/progress.md` when Current or Next changes.

Do not walk every directory, translate source line by line, or treat README claims as proof. Do not spend the session on setup when static evidence can still advance the stated question; record setup blockers precisely.

## Study Note Contract

Create one cumulative note per repository with these sections:

```text
# owner/repo

## 研读目标与版本
## 仓库地图
## 核心调用链
## 设计取舍
## 验证实验
## 我的复述与纠偏
## 可迁移结论
## 未解决问题
## 下一步
```

For each studied path, record the date, revision, question, repository-relative file/symbol evidence, command and observed result. Link concepts back to the AI or full-stack notes instead of duplicating long explanations.

## Completion Check

A first-pass project study is complete only when the learner can explain the entrypoint, one end-to-end path, the important state transition, and one failure path, with at least one executed or otherwise observable verification. If runtime verification is blocked, label the result as partial rather than complete.

