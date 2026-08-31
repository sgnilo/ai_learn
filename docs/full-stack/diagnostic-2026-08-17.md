---
layout: default
title: "全栈摸底评估（2026-08-17）"
---

# 全栈摸底评估（2026-08-17）

返回：[全栈学习](./00-overview.md) / [Full-stack Roadmap](./roadmap.md) / [Progress](../progress.md)

## 评估方式

使用开放场景题，不考名词记忆。每题观察五个维度：

1. 能否解释机制与状态变化。
2. 能否区分相邻组件的责任边界。
3. 能否预测并发、超时和部分失败的结果。
4. 能否提出证据驱动的诊断方法。
5. 能否根据业务风险做设计取舍。

## 总体结论

当前不是全栈初学者，已经具备较完整的组件认知和 demo 经验。多数模块位于 L1 到 L2：正常路径会用，能够推导一部分故障结果，但底层机制、并发控制和生产诊断还不稳定。

```text
优势：业务直觉、风险排序、跨层串联、吸收纠正速度
主要缺口：OS / Runtime、数据库并发、安全边界、容器机制、取消与重试
路线目标：核心模块稳定达到 L3，关键模块逐步达到 L4
```

## 分模块基线

| 模块 | 当前基线 | 已表现出的能力 | 主要知识缺口 |
| --- | --- | --- | --- |
| Runtime / HTTP | L1-L2 | 能区分 TCP connection 与 HTTP request；理解 keep-alive 复用连接 | socket 不是协议；listening / connected fd；Node 不为每个请求开进程；event loop、async I/O 与 cancellation |
| Gateway / Request Pipeline | L2 | 已建立 500 与 502 的响应所有权边界；理解 504 是 upstream timeout | 尚需用 connect/header/response timing、request id 和依赖指标完成证据化定位 |
| Application Architecture | L1-L2 | 能识别 token、body validation、库存与邮件的大致职责边界 | authentication / authorization、transport / business validation、transaction 与 side effect 的精确边界仍需实验验证 |
| Database / ORM | L1-L2 | 能预测并发扣库存可能得到 `stock = -1`；知道库存与订单需要原子提交 | transaction 不等于串行；row lock、conditional update、isolation；unique constraint 与 check-then-insert；Prisma I/O 与 microtask |
| Cache / Queue / Consistency | L2 | 能判断 cache invalidation 失败会读到旧值；理解“漏发比偶发重复更严重”和数据库无法覆盖外部副作用 | stale-while-revalidate 不等于强一致；consumer 与外部 provider 的幂等；exactly-once 边界 |
| Security | L1-L2 | 经过场景纠正后能判断 SameSite、CORS 和跨站 POST 的行为；选型倾向合理 | 初始混淆 XSS token stealing 与 CSRF；session / JWT 的撤销和设备管理边界需巩固 |
| Container / Deployment | L1-L2 | 理解 port mapping 需要宿主机地址；能设计 expand / backfill / switch / contract schema migration | container 不是 VM；network namespace、wildcard bind、PID 1、signal forwarding 与 graceful shutdown |
| Observability / Reliability | L2 | 能从 pool acquire latency 定位尾延迟；能计算 retry amplification | 连接持有原因和 DB 容量判断；上游超时不会自动取消下游；deadline propagation、retry owner 与 backpressure |

这些等级是本轮诊断基线，不是固定能力标签。未直接覆盖的细节不按“已掌握”处理。

## 已确认的优势

- 能从业务后果判断工程策略，例如通知“少量重复”通常优于“永久漏发”。
- 对版本共存有正确直觉，能够推导 rolling update 下的 schema compatibility。
- 遇到纠正后能快速把模型迁移到下一道题，而不是只记答案。
- 已具备 transaction、cache、gateway、container 等组件的使用经验，适合直接做机制与故障实验。

## 优先纠正的心智模型

### 1. 异步不等于 JavaScript 并行

`async` 只允许使用 `await` 并让函数返回 Promise。JavaScript 会同步执行到 pending `await`；CPU loop 仍会阻塞 event loop。上游 timeout 也不会自动停止正在运行的 application / database work，必须显式传播 deadline 与 cancellation。

### 2. Transaction 不等于业务串行

Transaction 提供数据库原子性和隔离语义，但是否防止超卖取决于 isolation、lock 和 SQL 条件。业务不变量应使用 conditional update、row lock、constraint 和幂等 key 落到数据库可原子执行的边界。

### 3. Container 不等于虚拟机

Container 是共享宿主机 kernel 的隔离进程。`127.0.0.1`、`0.0.0.0`、port publishing 和 PID 1 都必须从 namespace、socket bind 与 process signal 理解。

### 4. 跨系统副作用通常不是 exactly-once

数据库、Redis、Broker、邮件服务不是同一个 transaction。可靠设计通常使用 Outbox、at-least-once delivery、idempotent consumer、provider idempotency key 和补偿，而不是假设一次执行。

### 5. Timeout 不等于 Cancellation

Client 或 Gateway 放弃等待，只说明这一层不再接收结果。Application 与 DB 默认可能继续工作。合理系统需要逐层递减的 deadline、显式 cancellation、单一 retry owner、retry budget、backoff / jitter 与幂等保护。

## 学习优先级

### P0：Runtime 与请求执行模型

按 [后端运行时与 HTTP 基础](./02-backend-http-foundations.md) 推进：

1. `process -> file descriptor -> listening socket -> connection socket`。
2. Event loop、async I/O、Promise continuation 与 CPU-bound work。
3. Timeout、disconnect、AbortSignal、backpressure 与 graceful shutdown。

### P1：数据库正确性

- Conditional update 与 affected rows。
- `SELECT ... FOR UPDATE`、MVCC、isolation 和 deadlock。
- Unique constraint、幂等请求和 transaction boundary。
- ORM 生成 SQL、connection pool 与 transaction 持有时间。

### P2：容器与部署机制

- Namespace、cgroup、container network 与 port publishing。
- PID 1、signal forwarding、readiness 与优雅退出。
- Compatible migration、rolling update 与 rollback window。

### P3：生产可靠性

- Gateway timing、request id、logs / metrics / traces。
- Cache invalidation、Outbox、重复消费与 provider idempotency。
- Security trust boundary、deadline propagation 和 retry amplification。

## 第一阶段完成标志

完成 Module 0 时，不以“Node HTTP demo 跑通”为标准，而要求：

- 能准确解释 `server.listen()` 到 handler 的内核与 runtime 链路。
- 能用实验区分 CPU blocking 和 async I/O waiting。
- 能观察 socket、连接、event loop lag 和进程 signal。
- 能复现并修复 timeout 不取消、慢客户端 backpressure 和不完整 shutdown。
- 能用自己的语言解释为什么修复有效。
