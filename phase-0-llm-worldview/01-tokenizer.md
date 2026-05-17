# Tokenizer

## 学习状态

学习中。

## 当前理解

Tokenizer 的作用是把人类文本转换成模型能处理的 token id 序列。

## 核心概念

- Token 不一定等于单词，可能是字、词、子词、符号或字节片段。
- LLM 不直接处理文字，而是处理 token id 经过 embedding 后得到的向量。
- Tokenizer 会影响 context window、推理成本、多语言能力、代码能力和训练效果。

## 主流方案

### 1. Word-level tokenizer

按词切分，比如把：

```text
I love machine learning
```

切成：

```text
["I", "love", "machine", "learning"]
```

优点：

- 直觉简单
- 对空格分词语言容易理解

缺点：

- 词表会非常大
- 遇到新词容易 OOV，也就是 out of vocabulary
- 对中文、日文、代码、emoji、多语言场景不友好

现在大模型一般不会只用纯 word-level tokenizer。

### 2. Character-level tokenizer

按字符切分，比如：

```text
hello
```

切成：

```text
["h", "e", "l", "l", "o"]
```

优点：

- 词表很小
- 几乎没有 OOV 问题

缺点：

- token 序列太长
- 训练和推理成本高
- 单个 token 的语义密度低

纯字符级 tokenizer 更适合教学和小模型实验，不是现代 LLM 的主流选择。

### 3. BPE：Byte Pair Encoding

BPE 是 GPT 系、RoBERTa 等模型常见的子词切分方法。

核心思想：

```text
从最小单位开始
→ 统计最常见的相邻 token pair
→ 把高频 pair 合并成新 token
→ 重复直到达到词表大小
```

例子：

```text
l o w
l o w e r
n e w e s t
```

如果 `l + o` 经常一起出现，就合并成 `lo`；如果 `lo + w` 又经常出现，就继续合并成 `low`。

优点：

- 常见词可以变成较短 token
- 罕见词可以拆成子词
- 词表大小和序列长度之间取得平衡
- 工程实现成熟

缺点：

- merge 规则是贪心的
- 对空格、大小写、Unicode 的处理依赖具体实现
- 对某些非拉丁语言可能 token 效率不如理想状态

### 4. Byte-level BPE

Byte-level BPE 是 BPE 的重要变体，GPT-2、RoBERTa、OpenAI tiktoken 相关编码都属于这一类思路。

核心区别：

```text
普通 BPE：从字符或预分词后的子词开始
Byte-level BPE：从 UTF-8 byte 开始
```

优点：

- 可以覆盖几乎所有 Unicode 文本
- 不容易出现真正的 OOV
- 对 emoji、特殊符号、混合语言、代码更稳

缺点：

- 对中文、日文等字符，可能因为 UTF-8 多字节表示导致 token 数偏多
- token 可读性更差

现在很多 GPT 类模型会选择 byte-level BPE，因为它在开放文本环境里非常稳。

### 5. WordPiece

WordPiece 是 BERT 系列常见的子词算法。

它和 BPE 很像，也会从小单位逐步构建子词词表，但合并标准不同。

BPE 更偏向：

```text
合并出现频率最高的 pair
```

WordPiece 更偏向：

```text
选择能最大化训练语料似然的子词组合
```

直觉上，WordPiece 不只是看 pair 高频不高，还会考虑这个合并是否让整体语言建模更合理。

常见形式：

```text
unaffable → ["un", "##aff", "##able"]
```

其中 `##` 表示这个 token 是接在词内部的子词。

优点：

- BERT 生态成熟
- 对 mask language modeling 任务很常见
- 子词边界表达清晰

缺点：

- 相比 byte-level BPE，对未知字符和多语言开放文本的鲁棒性取决于实现和词表
- 现在 GPT 类生成模型里不如 BPE / SentencePiece 常见

### 6. Unigram Language Model

Unigram 是 SentencePiece 常用的一种算法，T5、ALBERT、部分 LLaMA 系 tokenizer 背后会涉及 SentencePiece / Unigram 路线。

核心思想和 BPE 相反。

BPE 是：

```text
从小词表开始，不断合并
```

Unigram 是：

```text
先准备一个较大的候选子词词表
→ 用概率模型评估每个子词的重要性
→ 删除贡献较低的子词
→ 保留能最好解释语料的词表
```

同一句话可能有多种切法，Unigram 会选择概率最高的切分，也可以在训练时采样不同切分增强鲁棒性。

优点：

- 概率模型清晰
- 支持 subword regularization
- 对多种可能切分更灵活

缺点：

- 原理比 BPE 稍复杂
- 工程调试时不如 BPE merge 规则直观

### 7. SentencePiece

SentencePiece 严格来说不是单一算法，而是一个 tokenizer 框架。它可以使用：

- BPE
- Unigram
- character
- word

它最重要的特点是：

```text
直接从原始文本训练，不强依赖空格预分词
```

这对中文、日文、韩文等没有天然空格分词的语言很重要。

SentencePiece 常用 `▁` 表示空格，例如：

```text
Hello world → ["▁Hello", "▁world"]
```

优点：

- 语言无关
- 不依赖传统分词器
- 适合多语言模型
- 支持 BPE 和 Unigram

缺点：

- 输出 token 可读性和具体模型配置有关
- 需要理解 `▁` 这类空格标记

## 核心区别对比

| 方案 | 基本单位 | 训练方式 | 代表模型 / 生态 | 优点 | 缺点 |
| --- | --- | --- | --- | --- | --- |
| Word-level | 词 | 统计词表 | 早期 NLP | 简单直观 | 词表大，OOV 严重 |
| Character-level | 字符 | 固定字符表 | 教学、小模型 | 词表小，无新词问题 | 序列长，语义密度低 |
| BPE | 字符 / 子词 | 高频 pair 合并 | GPT、RoBERTa | 平衡词表和长度，成熟 | 贪心规则，多语言效率依赖实现 |
| Byte-level BPE | byte | 高频 byte/subword pair 合并 | GPT-2、tiktoken、RoBERTa | Unicode 覆盖强，开放文本稳 | CJK 可能 token 偏多 |
| WordPiece | 子词 | 近似最大化语料似然 | BERT | BERT 生态成熟 | 生成模型里不是最主流 |
| Unigram | 子词 | 概率模型剪枝 | T5、SentencePiece 生态 | 切分灵活，可采样 | 原理和调试更复杂 |
| SentencePiece | 原始文本 | BPE / Unigram 等 | LLaMA、T5、多语言模型 | 不依赖空格，适合多语言 | 不是单一算法，需要看具体配置 |

## 怎么记

最实用的记法：

```text
BPE：从小到大合并
WordPiece：像 BPE，但合并标准更偏语言模型似然
Unigram：从大候选词表往下删
SentencePiece：语言无关的 tokenizer 框架，可用 BPE 或 Unigram
Byte-level BPE：从 byte 开始的 BPE，覆盖所有文本更稳
```

## 关键辨析：Tokenizer 是不是在找“最小语义单元”？

可以把 tokenizer 直觉理解为：

```text
把文本切成模型可处理的相对稳定单元
```

但要注意，它不是严格在寻找语言学意义上的“最小语义单元”。

更准确地说，tokenizer 在做工程平衡：

```text
词表大小
+
序列长度
+
未知文本覆盖率
+
训练语料里的统计规律
+
推理和训练成本
```

它会倾向于让高频、稳定、可复用的片段成为 token。这个片段可能有明确语义，比如：

```text
cat
token
function
```

也可能只是统计上常见但语义不完整的片段，比如：

```text
ing
tion
##able
```

所以不能简单说：

```text
token = 最小语义单元
```

更应该说：

```text
token = 训练语料中统计上有价值、可复用、成本合适的文本片段
```

## 长 token 和短 token 的权衡

你的直觉是对的：token 太短和太长都有问题。

如果 token 太短：

- 序列会变长
- attention 成本上升
- 推理更慢
- 单个 token 信息密度低

如果 token 太长：

- 词表会变大
- 罕见表达更容易匹配不到
- 泛化能力变差
- 新词、拼写变化、代码变量名更难处理

例如：

```text
getUserProfileById
```

如果整个都作为一个 token，语义完整，但遇到：

```text
getUserProfileByEmail
```

就无法复用前面的结构。

如果切成：

```text
get / User / Profile / By / Id
```

虽然单个 token 更短，但复用性更强。

所以 tokenizer 本质上是在找平衡：

```text
高频片段尽量合并，降低序列长度
低频片段保持可拆，提升覆盖和泛化
```

## BPE 和 Unigram 的方向差异

你的理解基本可以作为直觉，但需要稍微修正措辞。

BPE 可以理解为：

```text
从小到大
从字符 / byte / 子词开始
不断合并高频相邻片段
```

它的核心不是直接“聚合语义”，而是：

```text
聚合训练语料中高频共现的片段
```

这些高频片段经常对应更完整的语义，但不是必然。

Unigram 可以理解为：

```text
从大候选词表开始
用概率模型判断哪些子词有价值
逐步删除贡献低的片段
```

它也不是先保证完整语义再拆无关部分，而是：

```text
从多个可能切分里，保留最能解释训练语料的子词集合
```

所以更准确的对比是：

| 方案 | 方向 | 核心标准 |
| --- | --- | --- |
| BPE | 从小到大合并 | 高频相邻 pair |
| Unigram | 从大候选集合往下删 | 哪些子词组合最能用概率解释语料 |

直觉总结：

```text
BPE：看到哪些片段总一起出现，就把它们合起来
Unigram：先给很多候选切法，再保留整体概率最好的那批子词
```

## 现在大模型常见选择

- GPT 类模型：常见 BPE / byte-level BPE，例如 OpenAI tiktoken
- BERT 类模型：常见 WordPiece
- T5 / LLaMA / 多语言模型：常见 SentencePiece，具体可能是 BPE 或 Unigram
- 教学和从零实验：可能用 character-level 或简单 BPE

工程上不能只看“模型名称”，要看该模型目录里的 tokenizer 配置文件，例如：

- `tokenizer.json`
- `tokenizer.model`
- `vocab.json`
- `merges.txt`
- `tokenizer_config.json`

## 待学习问题

- BPE、SentencePiece、WordPiece 的区别是什么？
- BOS、EOS、PAD、UNK 等 special token 分别做什么？
- truncation 和 padding 为什么会影响训练？
- 中文、英文、代码在 tokenizer 上有什么差异？

## 实践记录

尚未开始。

## 关键代码

尚未开始。

## 踩坑

暂无。

## 复盘

尚未复盘。

## 下一步

使用 Hugging Face tokenizer 对中文、英文、代码分别编码，观察 token 切分结果。
