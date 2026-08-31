---
layout: default
title: "数据库读写：内存、WAL 与磁盘"
---

# 数据库读写：内存、WAL 与磁盘

## 一句话定义

PostgreSQL、MySQL 这类持久化数据库同时使用内存和磁盘：**内存承担活跃计算与缓存，磁盘或其他稳定存储承担持久性，WAL / Redo Log 连接两者。**

这里的“磁盘”是稳定存储的简化说法，实际可能是本地 SSD、云块存储或带持久化保证的存储设备。

## 数据分别在哪里

| 内容 | 主要位置 | 作用 |
| --- | --- | --- |
| Data file | 磁盘 | 保存表和索引的持久数据页 |
| Buffer Pool / Shared Buffers | 数据库进程内存 | 缓存正在访问的数据页和索引页 |
| OS Page Cache | 操作系统内存 | 缓存文件 I/O；具体数据库可能使用或绕过它 |
| WAL / Redo Buffer | 内存 | 暂存即将写入事务日志的记录 |
| WAL / Redo Log | 磁盘 | 崩溃后重放尚未写回数据文件的修改 |
| Dirty Page | 内存 | 已被修改、尚未写回数据文件的数据页 |
| Query working memory | 内存，必要时溢写磁盘 | sort、hash、join、aggregation 等查询计算 |
| Lock / transaction runtime state | 内存 | 协调并发事务；必要事实通过日志和存储恢复 |

数据库通常按 **page** 而不是单行作为缓存和磁盘 I/O 的基本单位。

## 一次读取

```text
SQL
  ↓
Parser / Planner / Executor
  ↓
在 Buffer Pool 中查找目标 page
  ├─ 命中：直接从内存读取
  └─ 未命中：从数据文件读取 page → 放入内存 → 读取
  ↓
返回结果
```

因此：

- 热数据读取可能完全在内存完成；
- 冷数据第一次读取需要存储 I/O；
- 读到内存后，后续查询可能复用这个 page；
- 内存不足时，低价值 page 会被淘汰，之后访问还要重新加载。

这也是同一条 SQL 第一次慢、后续变快的常见原因之一，但 query plan、锁等待和连接等待也可能造成差异，不能只凭现象断定是缓存。

## 一次写入与提交

以常见的 WAL / Redo 架构简化说明：

```text
UPDATE
  ↓
把目标 data page 加载到 Buffer Pool
  ↓
在内存中产生修改，page 成为 dirty page
  ↓
生成 WAL / Redo record
  ↓
COMMIT 时把必要日志 flush 到稳定存储
  ↓
向客户端确认提交成功
  ↓
后台 checkpoint / writer 稍后把 dirty page 写回 data file
```

关键点是 **Write-Ahead Logging**：描述修改的日志必须先于对应数据页持久化。

所以正常配置下，`COMMIT` 成功通常意味着恢复这次事务所需的 WAL / Redo 已达到数据库承诺的持久化边界，不意味着所有被修改的数据页已经写回表文件。

这样做的原因是：事务日志主要是顺序追加，通常比每次提交都随机写回多个数据页更高效。

## Commit 是什么边界

可以把成功返回的 `COMMIT` 理解为服务端与数据库之间的 **事务结果与持久性责任交接点**，但它不是 DDD 意义上的领域边界，也不应与数据库术语 `checkpoint` 混用。

`COMMIT` 表达的是：

- 这组数据库修改作为一个事务整体生效；
- 在当前 isolation 和 durability 配置下，数据库接受了维护这些状态的责任；
- 之后即使数据库进程崩溃，也应通过 WAL / Redo 和恢复协议恢复已提交状态。

它不表达：

- 业务决策本身一定正确；
- 所有数据页已写回表文件；
- Redis、邮件、支付或消息系统的副作用也已完成；
- 任意硬件损坏、错误配置或超出承诺故障模型的事故都不会丢数据。

数据库只理解 SQL、constraint、transaction 和存储规则，不理解完整的服务领域语义。错误金额被合法提交后，数据库会可靠保存这个错误金额，而不会替业务纠正它。

## Commit 不等于 Database Checkpoint

两者都可能被宽泛地理解为“可恢复点”，但在数据库内部是不同事件：

| 概念 | 粒度 | 主要作用 |
| --- | --- | --- |
| Transaction Commit | 单个事务 | 决定事务是否对外生效，并持久化必要提交日志 |
| Database Checkpoint | 数据库实例的周期性过程 | 推进 dirty page 刷盘并记录恢复起点，限制崩溃恢复需要重放的日志范围 |

数据库不会为每个事务执行一次完整 checkpoint。大量事务可以先后 commit，数据页再由 writer 和 checkpoint 批量写回。

## 服务与数据库的责任并非简单按一刀切开

正常成功路径可以简化为：

```text
服务：验证业务规则、组织事务、决定是否提交
                     ↓ COMMIT
数据库：保证 DB 内原子性、隔离性和已确认事务的恢复
                     ↓ ACK
服务：继续组织响应和数据库之外的后续动作
```

但服务发送 `COMMIT` 到收到确认之间存在 **unknown commit outcome**：

```text
Service              Database
   │ ---- COMMIT ---->  │
   │                    │ 写入并持久化 commit record
   │                    │ 事务已经提交
   │        X connection lost
   │                    │
   │ 只看到网络错误，无法仅凭错误判断事务是否提交
```

此时数据库可能已经成功提交，只是确认响应丢失。如果服务直接重新执行整个业务动作，就可能重复扣款或重复创建订单。

因此服务仍需要：

- 使用稳定的业务 idempotency key 和唯一约束；
- 重连后按业务键查询最终状态；
- 只对明确可重试的事务错误自动重试；
- 对 serialization failure、deadlock 等按数据库语义重跑整个事务；
- 用 Outbox、Saga 或下游幂等处理数据库之外的副作用。

所以更准确的说法是：**数据库负责 DB 内已提交状态的物理恢复；服务负责业务意图、重试策略、提交结果不确定性和跨系统一致性。**

## 崩溃后为什么数据仍能恢复

假设事务已经提交，WAL 已持久化，但 dirty page 还没写回数据文件，此时机器崩溃：

1. 内存中的 Buffer Pool 消失；
2. 数据文件可能仍是旧版本；
3. 数据库重启时读取 WAL / Redo；
4. 重放已提交但尚未反映到数据文件的修改；
5. 恢复到一致状态。

这说明持久性来自“数据文件 + 事务日志 + 恢复协议”，而不是要求每次事务都立刻把全部数据页写完。

## `fsync` 的作用

普通 `write()` 返回可能只表示数据进入操作系统或设备缓存，不一定已经到达掉电后仍存在的介质。数据库通过 `fsync` 或等价机制要求存储栈把关键日志推进到承诺的持久化边界。

是否等待这个过程取决于数据库配置和存储设备保证。例如关闭同步提交可能降低延迟，但机器故障时可能丢失近期已向客户端确认的事务。因此讨论“commit 是否落盘”时必须同时说明 durability 配置。

## 特殊情况

### In-memory database

Redis 等系统可以把主要数据集放在内存，通过 AOF、snapshot 或 replication 提供不同程度的持久化。它们仍可能使用磁盘，但读写主路径和持久性承诺与 PostgreSQL/MySQL 不同。

### 临时计算与磁盘溢写

即使数据页已在内存，大型 sort、hash join 或 aggregation 超过 working memory 后也可能写临时文件。因此“数据缓存命中”不代表查询没有磁盘 I/O。

### Replica 与云存储

有些数据库通过同步副本、分布式日志或远程存储确认持久性，不一定等同于本机物理盘完成写入。真正应该问的是：**系统在什么故障模型下承诺数据不丢失？**

## 常见误区

- 数据库在磁盘上，所以每次 `SELECT` 都直接读取磁盘。
- `COMMIT` 成功表示所有数据页已经写回表文件。
- 数据在内存中被修改，所以数据库进程崩溃后一定丢失。
- SQL execution 很快就代表整个数据库访问链路没有等待。
- SSD 很快，所以不需要 Buffer Pool、WAL 或查询内存管理。
- Redis 是内存数据库，所以一定不使用磁盘，或者一定不会丢数据。

## 观察建议

后续实验应观察：

- Buffer cache hit ratio 和 physical read；
- dirty page、checkpoint 和 background writer；
- WAL 生成速率、flush latency 和 fsync；
- query temporary file / spill；
- 数据库重启后的冷缓存与热缓存差异。

## 相关链接

- [全栈学习路线：Module 3 数据库与 ORM](../roadmap.md#module-3数据库与-orm)
- [服务端全景图](../01-server-side-panorama.md)
