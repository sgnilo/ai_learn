---
layout: default
title: "后端运行时与 HTTP 基础"
---

# 后端运行时与 HTTP 基础

返回：[服务端全景图](./01-server-side-panorama.md) / [全栈学习](./00-overview.md)

## 学习状态

进行中。目标深度：L3，能够解释机制、观察运行状态并诊断常见故障。

## 当前学习单元

从下面这个问题开始：

> 执行 `server.listen(port)` 之后，操作系统、进程、file descriptor、socket 和端口之间分别发生了什么？

这一问题是 HTTP server、容器端口、反向代理和负载均衡共同依赖的底层起点。

## 当前理解

前端调用 `fetch()` 时，服务端看到的不是一次普通函数调用，而是一条跨越网络、协议、运行时和业务代码的请求链路：

```text
browser
-> DNS / connection / TLS
-> HTTP request
-> server runtime
-> router / middleware / handler
-> business logic
-> HTTP response
-> browser
```

本模块先建立这条主链路，再逐步补充并发、超时、错误和资源生命周期。

## 深挖顺序

| 单元 | 主题 | 深度目标 |
| --- | --- | --- |
| 0.1 | Process、file descriptor、socket、bind、listen、accept | 能解释端口如何对应监听 socket，连接如何进入进程 |
| 0.2 | DNS、TCP、TLS 与 HTTP message | 能区分各层建立了什么状态、失败如何表现 |
| 0.3 | Node.js event loop、libuv、async I/O、thread pool | 能解释并发 I/O 与 CPU 阻塞 |
| 0.4 | Stream、buffer 与 backpressure | 能解释慢客户端和大响应如何影响内存与吞吐 |
| 0.5 | Timeout、cancellation 与 disconnect | 能设计超时预算并正确停止无效工作 |
| 0.6 | Signal、health check 与 graceful shutdown | 能安全停止接流量并完成或终止在途请求 |

## 核心概念

- Process 与 thread
- Event loop 与 async I/O
- TCP、TLS 与 HTTP 的分层关系
- HTTP method、status code、header 与 body
- Server、router、middleware 与 handler
- Timeout、connection reuse 与 graceful shutdown
- Stateless request 与进程内状态

## 待学习问题

- Node.js 如何在单个 JavaScript 主线程上处理多个并发请求？
- `async/await` 等待 I/O 时，运行时在做什么？
- HTTP keep-alive 复用了什么，为什么能减少请求成本？
- 请求超时应该由浏览器、网关还是应用服务控制？
- 为什么不能把关键业务状态只保存在服务进程内存中？
- 服务收到终止信号后，如何停止接收新请求并完成在途请求？

## 实践计划

1. 使用 Node.js 原生 `http` 模块实现最小服务。
2. 记录 method、path、headers 和请求耗时。
3. 增加 JSON body 解析、统一错误响应和请求超时。
4. 并发发起多个快请求与慢请求，观察 event loop 行为。
5. 实现 health check 与 graceful shutdown。

## 完成标志

- 能从进程、socket、协议和应用 runtime 四个层面解释一次 HTTP 请求。
- 能区分 event loop、异步 I/O、worker thread 与 CPU-bound work 的职责。
- 能通过观察连接、进程、日志和时序定位连接失败、请求超时与客户端断开。
- 能复现 event loop blocking、backpressure 和不完整 shutdown，并解释修复原理。
- 能独立实现一个具备超时、流控制、健康检查和优雅退出的最小 HTTP 服务。

## 下一步

先学单元 0.1：拆解 `server.listen(port)`，建立 `process -> file descriptor -> listening socket -> connection socket` 的心智模型，再用最小 Node.js 服务和系统观察工具验证。
