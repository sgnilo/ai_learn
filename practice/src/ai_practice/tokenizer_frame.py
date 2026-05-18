import tiktoken

enc = tiktoken.get_encoding('cl100k_base')

text = 'hello world, 我是中国人，我叫徐江平，你叫什么？是机器人吗？哈哈哈哈哈哈哈哈天真烂漫getPerformance.now()'

ids = enc.encode(text)

print(ids)
print(enc.decode(ids))
print([enc.decode([id]) for id in ids])
