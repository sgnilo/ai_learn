---
layout: default
title: "File Descriptor、Socket 与系统调用"
---

# File Descriptor、Socket 与系统调用

## 一句话定义

File descriptor（FD）是进程局部的整数句柄。进程通过自己的 FD table，把这个整数间接映射到由内核管理的文件、socket、pipe、终端等资源抽象对象，再通过系统调用操作它们。

## JavaScript 心智模型

可以先把进程与 FD table 类比成：

```js
const process = {
  fdTable: new Map([
    [0, refToStdinResource],
    [1, refToStdoutResource],
    [21, refToListeningSocket],
    [22, refToConnectionSocket],
  ]),
};
```

对应关系：

```text
process       ≈ 拥有这张 Map 的对象
FD table      ≈ Map
fd            ≈ Map 的整数 key
FD table[fd]  ≈ 指向内核资源抽象对象的引用
socket 等     ≈ 内核管理的具体资源对象
```

这个类比只用于建立索引关系。FD table 实际由内核为进程维护，用户程序不能像读取普通 JavaScript `Map` 那样直接取得内核对象，只能通过系统调用请求内核操作它。

## 精确关系

```text
process
→ 拥有自己的 FD table
→ fd 是表内的整数索引
→ 表项间接引用内核资源抽象对象
→ 抽象对象维护状态，并连接到具体文件、socket、pipe 或设备
```

因此 FD 本身不是 socket，也不包含资源数据。它只是当前进程用来指认某个已打开资源的句柄。

同一个整数在不同进程中可以指向完全不同的资源：

```js
processA.fdTable.get(22); // connection socket
processB.fdTable.get(22); // ordinary file
```

一个内核资源也可能因为 `dup`、`fork` 等机制被多个 FD 或进程间接引用。关闭一个 FD 是移除一个引用；只有没有其他引用且生命周期允许结束时，底层资源才会被释放。

## 为什么叫 File Descriptor

FD 最初用于描述已经打开的文件。Unix 后来把许多拥有相似生命周期的 I/O 资源统一到“文件式接口”下：

```text
打开或创建
→ 读取 / 写入
→ 等待事件
→ 关闭
```

因此一张 FD table 中可能同时存在：

```text
fd 3 → ordinary file
fd 4 → TCP socket
fd 5 → pipe
fd 6 → terminal
```

“Everything is a file”不表示这些资源都是磁盘文件，更准确的意思是：**Unix 让很多 I/O 资源共享类似文件的访问接口和生命周期模型。**

`stdin` 也不是一种独立的底层资源类型，而是约定使用 `fd 0` 的标准输入入口。根据进程启动方式，它可以指向终端、文件、pipe，甚至 socket。

## 系统调用是访问入口

高级语言通常先经过标准库或运行时，再通过系统调用进入内核：

```text
JavaScript API
→ Node.js / libuv
→ system call
→ 根据当前 process 与 fd 查 FD table
→ 找到内核资源抽象对象
→ 分派到该资源类型的操作实现
```

可以用伪代码理解这种分派：

```js
function systemRead(process, fd, buffer) {
  const resource = process.fdTable.get(fd);
  return resource.operations.read(resource, buffer);
}
```

不同资源可以提供同名但行为不同的实现：

```text
file.read   → 从文件系统读取
socket.read → 从 socket 接收缓冲区读取
pipe.read   → 从 pipe 缓冲区读取
```

系统调用并不是“装在 FD 或资源里面”的方法。`read()`、`write()` 等是进入内核的统一入口；内核找到资源对象后，再调用适用于该资源的内部操作实现。

## 不只有 `read`、`write`、`close`

统一接口不代表所有资源只有三种操作。Socket 还需要：

```text
socket()  → 创建 socket
bind()    → 绑定本地地址
listen()  → 进入监听状态
accept()  → 取出一个已建立连接
connect() → 主动建立连接
send() / recv() → 传输数据
close()   → 关闭描述符
```

其他内核能力也使用不同的系统调用，例如 `mmap`、`clone`、`execve`、`futex` 和信号相关调用。因此，更准确的结论是：

> 高级语言通过系统调用访问内核；Unix 只是把大量 I/O 资源统一成可以由 FD 指认的文件式接口。

## `server.listen()` 中的两类 Socket

Node.js 执行 `server.listen(3000, "0.0.0.0")` 后，内核侧可以简化为：

```text
Node.js process
└── fd 21
    └── listening socket
        └── bind 0.0.0.0:3000
```

这条关系不能简化成“进程直接绑定 IP 和端口”。更准确的链路是：

```text
process
→ FD table
→ fd
→ 内核 socket 对象
→ socket 记录绑定的 local endpoint（IP:port）
```

Socket 刚创建时可以尚未绑定地址：

```text
socket()
→ unbound socket
→ bind(0.0.0.0:3000)
→ bound socket
→ listen()
→ listening socket
```

其中 [`0.0.0.0` 是 wildcard address](./ip-address-and-interface.md)，表示监听本机所有合适的 IPv4 local address，不是客户端实际连接的目标 IP。IP 是协议定义的逻辑地址，通常配置在 network interface 上；它不是机器的物理位置，也不等同于网卡本身。

Listening socket 只负责接收新 TCP connection。当一个连接完成握手后，运行时对监听 FD 执行 `accept()`，得到新的 connection socket 和 FD：

```text
fd 21 → listening socket，继续等待新连接
fd 22 → connection socket A，传输客户端 A 的字节
fd 23 → connection socket B，传输客户端 B 的字节
```

`accept()` 不会把 listening socket 变成 connection socket，也不会因为接收一个连接而停止监听。

Connection socket 不只记录本地 endpoint，还与一个远端 endpoint 对应：

```text
process
→ fd 22
→ connection socket
   ├── local  = 192.168.1.20:3000
   └── remote = 192.168.1.50:51820
```

一条 TCP connection 通常由 `local IP`、`local port`、`remote IP`、`remote port` 四元组区分。因此大量连接可以共享服务端的本地监听端口，只要完整四元组不同。

## TCP Connection 与 HTTP Request

TCP connection 是持续传输字节的通道，HTTP request 是这个字节流中由 HTTP 协议划分出来的一条消息。

在 HTTP/1.1 keep-alive 下：

```text
connection socket / fd 22
├── HTTP request 1 → HTTP response 1
└── HTTP request 2 → HTTP response 2
```

第二个 HTTP request 到来时，变得可读的是 `fd 22`，而不是监听用的 `fd 21`。Node.js 从同一个 connection socket 读取新字节，由 HTTP parser 创建新的请求/响应对象并再次执行 handler，不需要再次调用 `accept()`。

只有建立新的 TCP connection 时，listening socket 才会再次产生可接受连接的事件。

## 资源访问与调度不是一回事

FD 主要回答：

```text
当前进程要操作哪个内核资源？
```

`epoll`、`kqueue` 等 I/O 事件机制回答：

```text
哪些 FD 对应的资源现在可以继续读写？
```

CPU scheduler 回答：

```text
现在应该让哪个线程使用 CPU？
```

以非阻塞 socket 为例：

```text
read(fd 22)，当前没有数据
→ 内核返回 EAGAIN
→ libuv 通过 epoll / kqueue 关注 fd 22
→ event loop 继续处理其他任务
→ 网络数据到达，fd 22 变为 readable
→ event loop 收到通知后再次读取
```

因此，FD 负责资源身份，系统调用负责访问入口，I/O readiness 机制负责事件通知，CPU scheduler 负责线程运行；它们彼此协作，但不是同一个概念。

## 常见误区

- FD 就是 socket 或文件本身。
- FD table 存放了资源的完整数据，而不是对内核对象的间接引用。
- `read()` / `write()` 只能读写磁盘文件。
- 所有内核能力都通过 `read()` / `write()` 完成。
- `accept()` 会把 listening socket 转换成 connection socket。
- 每个 HTTP request 都需要新建一条 TCP connection。
- `stdin` 一定连接终端。

## 相关链接

- [IP Address、Network Interface 与 Wildcard Bind](./ip-address-and-interface.md)
- [后端运行时与 HTTP 基础](../02-backend-http-foundations.md)
- [全栈学习路线：Module 0](../roadmap.md#module-0runtime网络与-http)
