---
layout: default
title: "全栈学习路线 Roadmap"
---

# 全栈学习路线 Roadmap

返回：[全栈学习](./00-overview.md) / [AI 学习](../ai/00-overview.md) / [Progress](../progress.md)

## 总目标

从“知道组件、能按教程使用”深化到“理解机制、能诊断问题、能做工程取舍”，最终能够对一个产品从浏览器到生产环境负责：

```text
UI 与交互
-> HTTP 与 API
-> 业务逻辑
-> 数据与事务
-> 安全与异步系统
-> 测试与可观测性
-> 部署与运维
```

起步阶段优先使用熟悉的 TypeScript / Node.js 降低语言切换成本，但学习目标是可迁移的后端与系统概念，不绑定单一框架。全景图只负责定位，真正的学习成果来自对关键路径的逐层下钻。

## 掌握深度标准

| Level | 状态 | 判断标准 |
| --- | --- | --- |
| L0 · 听过 | 知道名词 | 能认出组件，但不能稳定说明边界 |
| L1 · 会用 | 能完成 demo | 能按文档配置或调用，正常路径可以工作 |
| L2 · 理解 | 能解释机制 | 能从输入到输出解释内部关键步骤和状态变化 |
| L3 · 能诊断 | 能处理失败 | 能观察运行状态、构造故障、定位根因并验证修复 |
| L4 · 能设计 | 能做取舍 | 能根据流量、一致性、复杂度和运维成本选择方案 |

当前多数已接触组件位于 L1 到 L2。路线目标是：所有核心模块至少达到 L3，数据库、请求链路、部署与可靠性逐步达到 L4。

## 路线总览

| 模块 | 深挖主题 | 目标深度 | 状态 |
| --- | --- | --- | --- |
| Baseline | [服务端全景图](./01-server-side-panorama.md) | 定位各组件，不作为深度终点 | 第一轮完成 |
| Module 0 | Runtime、进程、Socket、TCP / TLS / HTTP、并发与 backpressure | L3 | 进行中 |
| Module 1 | DNS、CDN、Reverse Proxy、Gateway、Load Balancer、Middleware、Router | L3 | 未开始 |
| Module 2 | API 语义、Controller、Use Case、Domain、Repository、错误与测试边界 | L3-L4 | 未开始 |
| Module 3 | SQL、schema、index、query plan、MVCC、transaction、lock、ORM | L4 | 未开始 |
| Module 4 | Cache、Queue、幂等、重试、Outbox 与分布式一致性 | L3-L4 | 未开始 |
| Module 5 | Session、Cookie、JWT、OAuth、RBAC 与 Web 安全 | L3 | 未开始 |
| Module 6 | Container、Linux 隔离、网络、CI/CD、健康检查、发布与回滚 | L4 | 未开始 |
| Module 7 | Logs、Metrics、Traces、SLI / SLO、容量、超时与故障恢复 | L4 | 未开始 |
| Module 8 | 产品化全栈项目 | 综合验证 | 未开始 |

## 深度学习闭环

每个模块都必须完成下面六步，不能以“demo 跑通”作为结束：

1. **Mechanism**：从输入、状态变化、输出解释底层机制。
2. **Minimal Build**：绕开重框架，手写最小实现理解抽象从何而来。
3. **Inspection**：使用日志、命令、SQL plan、metric 或 trace 观察真实行为。
4. **Failure Injection**：主动制造超时、断连、并发冲突、进程退出和依赖故障。
5. **Trade-off**：比较两种以上方案的收益、代价和适用边界。
6. **Teach Back**：用自己的语言画图、写笔记，并回答“为什么不是另一种设计”。

每个模块的最低交付物：

- 一张机制图或时序图。
- 一个最小实验和一个真实框架实现。
- 至少两个失败场景及诊断记录。
- 一份设计取舍说明。
- 覆盖关键行为的自动化测试。

## Module 0：Runtime、网络与 HTTP

### 需要理解

- Linux process、thread、file descriptor、socket 与 listening port 的关系。
- DNS、TCP、TLS、HTTP/1.1、HTTP/2 在请求链路中的分层。
- Node.js event loop、libuv、async I/O、thread pool 与 CPU-bound task。
- connection reuse、stream、buffer、backpressure、timeout 与 cancellation。
- process signal、in-flight request、graceful shutdown 与资源释放。

### 必做实验

- 用 Node.js 原生 `http` 模块实现服务，不先依赖 Express / NestJS。
- 用 `curl -v`、连接查看工具和请求日志对应客户端与服务端事件。
- 同时运行快请求、慢 I/O 和 CPU 密集请求，观察它们如何相互影响。
- 制造客户端中断、服务端超时、连接耗尽和进程退出。
- 实现 request timeout、stream backpressure、health check 与 graceful shutdown。

### 过关标准

- 能从进程、socket 和协议三个层面解释 `server.listen(port)` 后发生了什么。
- 能解释 Node.js 为什么可以处理并发 I/O，以及 CPU 密集任务为什么会阻塞其他请求。
- 面对连接失败、请求超时和进程退出，能判断故障发生在哪一层。

当前笔记：[后端运行时与 HTTP 基础](./02-backend-http-foundations.md)

## Module 1：流量入口与请求管线

### 需要理解

- DNS、CDN、WAF、Reverse Proxy、Gateway、Ingress 与 Load Balancer 的职责重叠和边界。
- L4 / L7 load balancing、TLS termination、upstream connection 与 forwarded headers。
- Middleware 的 onion model、执行顺序、错误传播与 context 生命周期。
- Router 的匹配、参数解析，以及 `404`、`405`、`502`、`503`、`504` 的来源。
- Cookie、CORS、HTTP cache、compression、streaming 等前后端协议边界。

### 必做实验

- 用 Nginx / Caddy 代理两个应用实例并观察负载分发。
- 给整条链路注入 request id，确认 gateway 与应用日志能够关联。
- 制造 upstream down、连接超时、响应超时和错误代理头。
- 手写最小 middleware compose 与 router matcher，再与框架行为对比。

### 过关标准

- 遇到 404、502、504 时能快速判断是 router、gateway 还是 upstream 的问题。
- 能说明某项鉴权、限流、缓存或重试策略应该放在 gateway 还是应用内。

## Module 2：应用架构与 API 语义

### 需要理解

- HTTP method、status、idempotency、pagination、versioning 与错误模型。
- Controller / Handler、Application Service、Domain、Repository 的变化原因和依赖方向。
- validation、authorization、transaction、side effect 应分别位于什么边界。
- Unit、integration、contract、E2E test 各自保护什么。

### 必做实验

- 完成一个业务 vertical slice，并让 transport、use case、repository 可以独立替换测试。
- 对同一业务分别实现贫血 CRUD 和显式 use case，比较复杂度与可测试性。
- 制造 validation error、domain conflict、dependency failure，并设计稳定错误响应。

### 过关标准

- 不依赖框架目录名，也能解释每段代码的职责和变化原因。
- 能避免 controller 直连 ORM、业务规则散落以及无意义的空壳分层。

## Module 3：数据库与 ORM

### 需要理解

- [数据库读写中的内存、WAL 与磁盘](./concepts/database-memory-and-disk.md)：Buffer Pool、dirty page、日志先行与 checkpoint。
- relational model、normalization、constraint 与 schema migration。
- B-tree index、composite index、selectivity 与 query planner。
- transaction、ACID、MVCC、isolation level、lock、deadlock 与 WAL。
- connection pool、prepared statement、N+1、lazy / eager loading。
- ORM 如何生成 SQL，以及 ORM abstraction 泄漏的边界。

### 必做实验

- 使用 `EXPLAIN ANALYZE` 比较有无索引、不同索引顺序和不同查询写法。
- 并发运行两个 transaction，复现 dirty/non-repeatable/phantom read 或 lock wait。
- 复现 N+1、连接池耗尽、deadlock 和失败 migration。
- 对同一查询比较 ORM、query builder 和 raw SQL。

### 过关标准

- 能从 SQL、query plan、index、lock 和 transaction 解释查询慢或写入失败的原因。
- 能决定何时使用 ORM，何时下沉到显式 SQL，并说清维护成本。

## Module 4：Cache、Queue 与一致性

### 需要理解

- cache-aside、write-through、TTL、eviction、cache stampede 与 invalidation。
- queue 的 ack、visibility timeout、at-least-once delivery、retry 与 dead-letter queue。
- idempotency key、optimistic concurrency、Outbox pattern 与最终一致性。

### 必做实验

- 为读接口增加 Redis cache，并复现脏缓存、缓存击穿和热点 key。
- 在 worker 处理一半时终止进程，观察 message redelivery。
- 实现可重复提交的写接口和幂等 consumer。
- 模拟数据库提交成功但消息发送失败，并用 Outbox 修复。

### 过关标准

- 能在重复、乱序、延迟和部分失败存在时保护业务不变量。
- 能解释强一致、最终一致与系统复杂度之间的取舍。

## Module 5：身份、安全与信任边界

### 需要理解

- Authentication 与 Authorization；Session、Cookie、JWT、OAuth / OIDC。
- password hashing、credential lifecycle、RBAC / ABAC 与 tenant isolation。
- XSS、CSRF、SQL injection、SSRF、CORS、rate limiting 与 secret management。

### 必做实验

- 实现基于 secure cookie 的 session login 和最小 RBAC。
- 为状态修改接口验证 CSRF 与权限边界。
- 对输入、URL fetch、数据库查询和日志内容设计攻击用例。
- 实现 credential rotation、logout / revoke 和审计记录。

### 过关标准

- 能画出每种 credential 的产生、传输、验证、过期和撤销路径。
- 能根据威胁模型决定控制措施，而不是机械堆安全库。

## Module 6：容器与部署

### 需要理解

- image layer、container process、namespace、cgroup、filesystem 与 network namespace。
- PID 1、signal、volume、container network、port publishing 与 service discovery。
- build artifact、registry、configuration、secret、migration 与环境差异。
- readiness / liveness、rolling update、rollback、blue-green / canary deployment。
- Kubernetes 只作为这些机制的编排实现，不作为起点。

### 必做实验

- 编写 multi-stage image，检查 layer、进程、文件系统和镜像体积。
- 用 Docker Compose 运行 gateway、两个 app replica 和 PostgreSQL。
- 观察容器 DNS、network、volume、signal 与 restart policy。
- 实现版本发布、数据库 migration、健康检查和可恢复回滚。

### 过关标准

- 能解释从 source commit 到用户请求命中新版本实例的全过程。
- 容器启动失败、健康检查失败或发布异常时，能定位并安全回滚。

## Module 7：可观测性、性能与可靠性

### 需要理解

- structured log、metric、trace 的信息差异与 correlation。
- latency、throughput、error rate、saturation，以及 percentile 而非只看 average。
- SLI、SLO、error budget、capacity planning 与 load testing。
- timeout、retry、exponential backoff、jitter、circuit breaker 与 bulkhead。

### 必做实验

- 为一条请求建立跨 gateway、app、database、worker 的关联信息。
- 用 load test 找到 CPU、event loop、connection pool 或 database bottleneck。
- 注入慢依赖、错误响应和实例退出，观察 metric 与 trace。
- 比较无界重试与有预算重试对系统的影响。

### 过关标准

- 能从用户症状出发，通过 signals 缩小范围并验证根因。
- 能基于 SLO 和失败预算设计 timeout、retry、容量与降级策略。

## Module 8：产品化全栈项目

使用一个 modular monolith 串起全部模块，先避免用微服务和 Kubernetes 掩盖基础机制。

项目必须包含：

- 一条包含 transaction 的核心写路径。
- 一个 cache 和一个异步 worker。
- 明确的 authentication / authorization。
- gateway、容器化、CI/CD、健康检查和回滚。
- logs、metrics、traces、load test 与故障演练。
- 一份架构决策记录，解释哪些复杂度被刻意推迟。

## 同步节奏

AI、全栈和开源项目研读各自维护当前学习单元，不把一条路线的阶段完成作为另一条路线的启动条件。

| 主线 | 当前学习单元 | 本单元结束条件 |
| --- | --- | --- |
| AI | Optimizer：SGD / AdamW | 能解释 gradient 如何变成参数更新 |
| 全栈 | [后端运行时与 HTTP 基础](./02-backend-http-foundations.md) | 能解释 process、socket、event loop 与一次 HTTP 请求的关系 |
| 开源项目 | [openai/codex · 系统边界与协议骨架](../open-source/studies/openai-codex.md) | 建立 CLI、`Op / EventMsg` 与 `CodexThread` 调用图 |

每次只为三条学习线各保留一个明确的 `Next`，统一更新到 [Progress](../progress.md)，避免并行学习变成同时铺开大量未完成主题。

## 项目方向

最终项目优先选择一项能连接三条路线的真实产品，例如带 AI 能力的知识工具或运营助手。项目中的通用 Web 系统能力归档到全栈类，模型与 Agent 能力归档到 AI 类；开源项目支线为两类知识提供真实实现证据，并通过链接形成一条完整产品链路。

路线推进原则：先用单体把机制学深，再引入分布式复杂度；先能观察和诊断，再追求抽象与规模。
