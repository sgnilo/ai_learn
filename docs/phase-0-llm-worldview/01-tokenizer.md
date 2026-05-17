---
layout: default
title: "Tokenizer"
---

# Tokenizer

## 学习状态

已完成第一轮概念学习和字符级 tokenizer 实践。

## 当前理解

Tokenizer 的作用是把人类文本转换成模型能处理的 token id 序列。

更完整的链路是：

```text
用户输入文本
-> tokenizer.encode
-> token ids
-> embedding
-> 模型计算
-> 输出 token id 序列
-> tokenizer.decode
-> 模型回答文本
```

模型概念上是在预测下一个 token，工程上通常表现为预测下一个 token id。最后一层输出的是长度等于 `vocab_size` 的 logits，每个位置对应词表中的一个 token id。

## 核心概念

- Token 不一定等于单词，可能是字、词、子词、符号或字节片段。
- LLM 不直接处理文字，而是处理 token id 经过 embedding 后得到的向量。
- Tokenizer 会影响 context window、推理成本、多语言能力、代码能力和训练效果。
- `vocab` 是 token 词表，定义了有哪些 token、token 到 id 的映射、id 到 token 的反向映射。
- `encode` 把真实文本映射到 tokenizer 定义的 token id 空间。
- `decode` 把 token id 序列映射回人类可读文本。
- Special token 是词表中的正式 token，例如 `<unk>`、`<pad>`、`<eos>`，也应该有自己的整数 token id。

## 字符级 tokenizer 实践理解

当前练习实现的是教学版 `CharTokenizer`。它把每个字符当作一个 token，用 `corpus` 构建初始词表。

`__init__` 负责构建和维护：

- 有序 token 列表，例如 `(" ", "d", "e", "h", "l", "o", "r", "w")`
- token 到 token id 的映射，例如 `"h" -> 3`
- token id 到 token 的反向映射，例如 `3 -> "h"`

`encode` 负责：

```text
"hello" -> ["h", "e", "l", "l", "o"] -> [id_h, id_e, id_l, id_l, id_o]
```

`decode` 负责：

```text
[id_h, id_e, id_l, id_l, id_o] -> ["h", "e", "l", "l", "o"] -> "hello"
```

这里需要保持一个重要边界：

```text
encode 永远返回 list[int]
decode 永远接收 list[int]
```

因此 `<unk>` 不应该作为字符串混进 token id 序列，而应该先进入 vocab，拥有自己的整数 id。未知字符在 `encode` 时映射到 `<unk>` 对应的 id；`decode` 时再把这个 id 还原成字符串 `<unk>`。

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

- BOS、EOS、PAD 等 special token 分别做什么？
- truncation 和 padding 为什么会影响训练？
- 中文、英文、代码在 tokenizer 上有什么差异？
- 真实 byte-level BPE 如何避免大多数 OOV 问题？

## 实践记录

### 2026-05-17：字符级 tokenizer 与 `<unk>` 练习

实践目录：

- 代码：`practice/src/ai_practice/tokenizer.py`
- 测试：`practice/tests/test_tokenizer.py`

本轮完成的理解：

- `vocab_size` 是 token 词表大小，不是语料长度。
- `encode` 是从文本到 token id 空间的映射。
- `decode` 是从 token id 序列到文本的反向映射。
- 模型输出通常也是 token id 序列，最后靠 tokenizer decode 成人类可读文本。
- 词表外字符属于 OOV。教学实现可以报错，也可以通过 `<unk>` 兜底。
- `<unk>` 要作为正式 token 加入词表，而不是把字符串 `"<unk>"` 直接塞进 `list[int]`。

当前测试覆盖：

- round trip：编码后再解码可以回到预期文本。
- 未知字符：可以映射到 `<unk>`。
- 未知 token id：当前设计选择解码为 `<unk>`。

练习代码段：

```python
class CharTokenizer:
    """Encode text as character ids and decode ids back to text."""

    def __init__(self, corpus: str) -> None:
        if not corpus:
            raise ValueError("corpus must not be empty")

        UNKNOWN_TOKEN = "<unk>"
        self._chars = tuple(sorted(set(corpus))) + (UNKNOWN_TOKEN,)
        self._char_to_id = {char: index for index, char in enumerate(self._chars)}
        self._id_to_char = {index: char for index, char in enumerate(self._chars)}
        self.UNKNOWN_TOKEN = UNKNOWN_TOKEN
        self.UNKNOWN_TOKEN_ID = self._char_to_id[UNKNOWN_TOKEN]

    @property
    def vocab_size(self) -> int:
        return len(self._chars)

    def encode(self, text: str) -> list[int]:
        result = []
        for char in text:
            result.append(self._char_to_id.get(char, self.UNKNOWN_TOKEN_ID))
        return result

    def decode(self, token_ids: list[int]) -> str:
        raw = []
        for token_id in token_ids:
            if token_id not in self._id_to_char:
                raw.append(self._id_to_char[self.UNKNOWN_TOKEN_ID])
            else:
                raw.append(self._id_to_char[token_id])
        return "".join(raw)
```

练习测试段：

```python
def test_round_trip(self) -> None:
    tokenizer = CharTokenizer("hello world")

    token_ids = tokenizer.encode("hei")

    self.assertEqual(tokenizer.decode(token_ids), "he<unk>")
    self.assertEqual(tokenizer.vocab_size, len(set("hello world")) + 1)


def test_rejects_unknown_character(self) -> None:
    tokenizer = CharTokenizer("abc")
    token_ids = tokenizer.encode("hei")

    self.assertEqual(tokenizer.decode(token_ids), "<unk><unk><unk>")


def test_rejects_unknown_token_id(self) -> None:
    tokenizer = CharTokenizer("abc")

    self.assertEqual(tokenizer.decode([0, 99]), "a<unk>")
```

## 关键代码

本节作为实践记录里的代码索引。后续每次练习都直接在对应实践条目下附上实现片段和测试片段。

本轮核心结构：

```python
self._chars = tuple(sorted(set(corpus))) + (UNKNOWN_TOKEN,)
self._char_to_id = {char: index for index, char in enumerate(self._chars)}
self._id_to_char = {index: char for index, char in enumerate(self._chars)}
self.UNKNOWN_TOKEN_ID = self._char_to_id[UNKNOWN_TOKEN]
```

编码边界：

```python
result.append(self._char_to_id.get(char, self.UNKNOWN_TOKEN_ID))
```

解码边界：

```python
if token_id not in self._id_to_char:
    raw.append(self._id_to_char[self.UNKNOWN_TOKEN_ID])
else:
    raw.append(self._id_to_char[token_id])
```

## 踩坑

- 不要让 `encode` 返回混合类型，例如 `[3, 2, "<unk>"]`。token id 序列应该保持纯整数。
- 临时 `print` 可以帮助观察词表，但不应该长期留在 tokenizer 实现里。
- 如果已经用 `.get(...)` 或 `if token_id not in ...` 做了显式兜底，外层 `try/except KeyError` 往往就没有意义。
- `decode` 遇到未知 id 时是报错还是映射到 `<unk>` 是设计选择，但输入类型仍应保持为 `list[int]`。

## 复盘

第一轮 tokenizer 练习的重点不是追求真实 LLM tokenizer 的复杂度，而是建立几个稳定直觉：

```text
文本不是直接进入模型
模型处理的是 token id 对应的 embedding
模型预测的是词表位置上的概率分布
decode 是把 token id 序列重新序列化为文本
```

字符级 tokenizer 足够暴露核心机制，但它不是现代 LLM 的主流方案。后续要继续理解 BPE、byte-level BPE 和 SentencePiece 如何在词表大小、序列长度和 OOV 覆盖之间做工程平衡。

## 下一步

1. 清理当前 `CharTokenizer` 实现里的调试输出和无效异常处理。
2. 使用 Hugging Face tokenizer 对中文、英文、代码分别编码，观察 token 切分结果。
3. 对比字符级 tokenizer 和真实 BPE tokenizer 在同一句文本上的 token 数差异。
