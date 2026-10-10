---
title: "Linux系统调用与应用开发"
description: "深入讲解Linux系统调用的概念、常用系统调用API、文件操作、进程管理和网络编程基础，帮助开发者掌握Linux应用程序开发的核心技能"
slug: "linux-system-call-application-development"

# 分类信息
domain: "操作系统层"
module: "嵌入式Linux"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - Linux系统调用
  - 应用开发
  - 文件操作
  - 进程管理
  - 网络编程
prerequisites:
  - "03-process-thread"
related_contents: []

# 学习信息
estimated_time: 55
difficulty_score: 3

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2024-01-15"
updated_at: "2024-01-15"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - Linux系统调用
  - 系统编程
  - POSIX API
  - 文件IO
  - 网络编程
cover_image: ""
---

# Linux系统调用与应用开发

## 概述


系统调用(System Call)是应用程序与操作系统内核之间的接口，是用户空间程序请求内核服务的唯一途径。理解和掌握系统调用是Linux应用开发的基础。

完成本文学习后，你将能够：

- 理解系统调用的概念和工作原理
- 掌握常用的文件操作系统调用
- 了解进程管理相关的系统调用
- 掌握基本的网络编程接口
- 能够开发基本的Linux应用程序

## 背景知识

### 用户空间与内核空间

Linux系统将内存分为两个区域：

- **用户空间(User Space)**: 应用程序运行的区域，权限受限
- **内核空间(Kernel Space)**: 操作系统内核运行的区域，拥有最高权限

应用程序不能直接访问内核空间，必须通过系统调用来请求内核服务。

### 系统调用的特点

1. **安全性**: 通过特权级别切换保护内核
2. **标准化**: 提供统一的编程接口
3. **性能开销**: 涉及上下文切换，有一定性能开销
4. **可移植性**: POSIX标准保证跨平台兼容性

## 核心内容

### 系统调用的工作原理

#### 调用流程

```
应用程序 → C库函数 → 系统调用接口 → 内核处理 → 返回结果
```


#### 特权级别切换

1. **用户态**: 应用程序正常运行
2. **陷入内核**: 通过软中断(如x86的int 0x80或syscall指令)
3. **内核态**: 内核处理请求
4. **返回用户态**: 将结果返回给应用程序

#### 系统调用号

每个系统调用都有一个唯一的编号，内核通过这个编号来识别要执行的操作。

```c
// 系统调用号示例(x86_64)
#define __NR_read    0
#define __NR_write   1
#define __NR_open    2
#define __NR_close   3
```

### 文件操作系统调用

#### 文件描述符

文件描述符(File Descriptor)是一个非负整数，用于标识打开的文件。

- **0**: 标准输入(stdin)
- **1**: 标准输出(stdout)
- **2**: 标准错误(stderr)

#### open - 打开文件

```c
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

int open(const char *pathname, int flags);
int open(const char *pathname, int flags, mode_t mode);
```

**参数说明**:
- `pathname`: 文件路径
- `flags`: 打开标志(O_RDONLY, O_WRONLY, O_RDWR等)
- `mode`: 文件权限(创建文件时使用)

**返回值**: 成功返回文件描述符，失败返回-1


**示例**:

```c
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int fd;
    
    // 以只读方式打开文件
    fd = open("/tmp/test.txt", O_RDONLY);
    if (fd == -1) {
        perror("open");
        return 1;
    }
    
    printf("文件描述符: %d\n", fd);
    
    // 关闭文件
    close(fd);
    
    return 0;
}
```

#### read - 读取文件

```c
#include <unistd.h>

ssize_t read(int fd, void *buf, size_t count);
```

**参数说明**:
- `fd`: 文件描述符
- `buf`: 读取数据的缓冲区
- `count`: 要读取的字节数

**返回值**: 实际读取的字节数，0表示EOF，-1表示错误

**示例**:

```c
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    int fd;
    char buffer[128];
    ssize_t bytes_read;
    
    // 打开文件
    fd = open("/tmp/test.txt", O_RDONLY);
    if (fd == -1) {
        perror("open");
        return 1;
    }
    
    // 读取文件内容
    bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    if (bytes_read == -1) {
        perror("read");
        close(fd);
        return 1;
    }
    
    // 添加字符串结束符
    buffer[bytes_read] = '\0';
    printf("读取了 %zd 字节: %s\n", bytes_read, buffer);
    
    close(fd);
    return 0;
}
```


#### write - 写入文件

```c
#include <unistd.h>

ssize_t write(int fd, const void *buf, size_t count);
```

**参数说明**:
- `fd`: 文件描述符
- `buf`: 要写入的数据缓冲区
- `count`: 要写入的字节数

**返回值**: 实际写入的字节数，-1表示错误

**示例**:

```c
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    int fd;
    const char *text = "Hello, Linux System Call!\n";
    ssize_t bytes_written;
    
    // 创建或打开文件(如果存在则截断)
    fd = open("/tmp/output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1) {
        perror("open");
        return 1;
    }
    
    // 写入数据
    bytes_written = write(fd, text, strlen(text));
    if (bytes_written == -1) {
        perror("write");
        close(fd);
        return 1;
    }
    
    printf("写入了 %zd 字节\n", bytes_written);
    
    close(fd);
    return 0;
}
```

#### lseek - 文件定位

```c
#include <unistd.h>
#include <sys/types.h>

off_t lseek(int fd, off_t offset, int whence);
```

**参数说明**:
- `fd`: 文件描述符
- `offset`: 偏移量
- `whence`: 起始位置(SEEK_SET, SEEK_CUR, SEEK_END)

**返回值**: 新的文件偏移量，-1表示错误


**示例**:

```c
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    int fd;
    off_t offset;
    char buffer[32];
    
    fd = open("/tmp/test.txt", O_RDONLY);
    if (fd == -1) {
        perror("open");
        return 1;
    }
    
    // 移动到文件末尾
    offset = lseek(fd, 0, SEEK_END);
    printf("文件大小: %ld 字节\n", offset);
    
    // 移动到文件开头
    lseek(fd, 0, SEEK_SET);
    
    // 跳过前10个字节
    lseek(fd, 10, SEEK_CUR);
    read(fd, buffer, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    printf("从第10字节开始: %s\n", buffer);
    
    close(fd);
    return 0;
}
```

#### close - 关闭文件

```c
#include <unistd.h>

int close(int fd);
```

**返回值**: 成功返回0，失败返回-1

### 进程管理系统调用

#### fork - 创建子进程

```c
#include <unistd.h>

pid_t fork(void);
```

**返回值**:
- 父进程中返回子进程PID
- 子进程中返回0
- 失败返回-1


**示例**:

```c
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>

int main(void) {
    pid_t pid;
    
    printf("父进程开始, PID: %d\n", getpid());
    
    // 创建子进程
    pid = fork();
    
    if (pid == -1) {
        perror("fork");
        return 1;
    } else if (pid == 0) {
        // 子进程代码
        printf("子进程, PID: %d, 父PID: %d\n", getpid(), getppid());
        sleep(2);
        printf("子进程结束\n");
    } else {
        // 父进程代码
        printf("父进程, 子进程PID: %d\n", pid);
        sleep(3);
        printf("父进程结束\n");
    }
    
    return 0;
}
```

#### exec系列 - 执行新程序

```c
#include <unistd.h>

int execl(const char *path, const char *arg, ...);
int execlp(const char *file, const char *arg, ...);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
```

**示例**:

```c
#include <unistd.h>
#include <stdio.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid;
    
    pid = fork();
    
    if (pid == 0) {
        // 子进程执行ls命令
        printf("执行ls命令:\n");
        execl("/bin/ls", "ls", "-l", "/tmp", NULL);
        // 如果exec成功，下面的代码不会执行
        perror("execl");
        return 1;
    } else {
        // 父进程等待子进程结束
        wait(NULL);
        printf("子进程执行完毕\n");
    }
    
    return 0;
}
```


#### wait/waitpid - 等待子进程

```c
#include <sys/types.h>
#include <sys/wait.h>

pid_t wait(int *status);
pid_t waitpid(pid_t pid, int *status, int options);
```

**参数说明**:
- `status`: 子进程退出状态
- `pid`: 要等待的子进程PID(-1表示任意子进程)
- `options`: 选项(0或WNOHANG)

**示例**:

```c
#include <unistd.h>
#include <stdio.h>
#include <sys/wait.h>
#include <stdlib.h>

int main(void) {
    pid_t pid, wpid;
    int status;
    
    pid = fork();
    
    if (pid == 0) {
        // 子进程
        printf("子进程开始工作\n");
        sleep(2);
        printf("子进程结束\n");
        exit(42);  // 返回退出码42
    } else {
        // 父进程等待子进程
        printf("父进程等待子进程...\n");
        wpid = waitpid(pid, &status, 0);
        
        if (WIFEXITED(status)) {
            printf("子进程正常退出, 退出码: %d\n", WEXITSTATUS(status));
        }
    }
    
    return 0;
}
```

### 信号处理系统调用

#### signal - 设置信号处理函数

```c
#include <signal.h>

typedef void (*sighandler_t)(int);
sighandler_t signal(int signum, sighandler_t handler);
```

**示例**:

```c
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

void signal_handler(int signum) {
    printf("收到信号 %d\n", signum);
}

int main(void) {
    // 设置SIGINT(Ctrl+C)的处理函数
    signal(SIGINT, signal_handler);
    
    printf("按Ctrl+C测试信号处理...\n");
    
    while(1) {
        printf("程序运行中...\n");
        sleep(2);
    }
    
    return 0;
}
```


#### kill - 发送信号

```c
#include <signal.h>
#include <sys/types.h>

int kill(pid_t pid, int sig);
```

**示例**:

```c
#include <signal.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid;
    
    pid = fork();
    
    if (pid == 0) {
        // 子进程
        while(1) {
            printf("子进程运行中...\n");
            sleep(1);
        }
    } else {
        // 父进程
        sleep(3);
        printf("父进程发送SIGTERM信号给子进程\n");
        kill(pid, SIGTERM);
        wait(NULL);
        printf("子进程已终止\n");
    }
    
    return 0;
}
```

### 网络编程基础

#### socket - 创建套接字

```c
#include <sys/types.h>
#include <sys/socket.h>

int socket(int domain, int type, int protocol);
```

**参数说明**:
- `domain`: 协议族(AF_INET, AF_INET6, AF_UNIX)
- `type`: 套接字类型(SOCK_STREAM, SOCK_DGRAM)
- `protocol`: 协议(通常为0)

**返回值**: 成功返回套接字描述符，失败返回-1

#### TCP服务器示例

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(void) {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    char buffer[BUFFER_SIZE];
    
    // 创建套接字
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        return 1;
    }
    
    // 设置服务器地址
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    
    // 绑定地址
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        close(server_fd);
        return 1;
    }
    
    // 监听连接
    if (listen(server_fd, 5) == -1) {
        perror("listen");
        close(server_fd);
        return 1;
    }
    
    printf("服务器监听端口 %d...\n", PORT);
    
    // 接受客户端连接
    client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
    if (client_fd == -1) {
        perror("accept");
        close(server_fd);
        return 1;
    }
    
    printf("客户端已连接\n");
    
    // 接收数据
    ssize_t bytes_read = read(client_fd, buffer, BUFFER_SIZE - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("收到: %s\n", buffer);
        
        // 发送响应
        const char *response = "Hello from server!";
        write(client_fd, response, strlen(response));
    }
    
    close(client_fd);
    close(server_fd);
    
    return 0;
}
```


#### TCP客户端示例

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define SERVER_IP "127.0.0.1"
#define PORT 8080
#define BUFFER_SIZE 1024

int main(void) {
    int sock_fd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    const char *message = "Hello from client!";
    
    // 创建套接字
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (sock_fd == -1) {
        perror("socket");
        return 1;
    }
    
    // 设置服务器地址
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("inet_pton");
        close(sock_fd);
        return 1;
    }
    
    // 连接服务器
    if (connect(sock_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("connect");
        close(sock_fd);
        return 1;
    }
    
    printf("已连接到服务器\n");
    
    // 发送数据
    write(sock_fd, message, strlen(message));
    
    // 接收响应
    ssize_t bytes_read = read(sock_fd, buffer, BUFFER_SIZE - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("收到响应: %s\n", buffer);
    }
    
    close(sock_fd);
    
    return 0;
}
```

### 内存管理系统调用

#### mmap - 内存映射

```c
#include <sys/mman.h>

void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
int munmap(void *addr, size_t length);
```

**参数说明**:
- `addr`: 映射的起始地址(通常为NULL)
- `length`: 映射的长度
- `prot`: 内存保护标志(PROT_READ, PROT_WRITE, PROT_EXEC)
- `flags`: 映射标志(MAP_SHARED, MAP_PRIVATE)
- `fd`: 文件描述符
- `offset`: 文件偏移量


**示例 - 文件映射**:

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string.h>

int main(void) {
    int fd;
    struct stat sb;
    char *mapped;
    
    // 打开文件
    fd = open("/tmp/test.txt", O_RDWR);
    if (fd == -1) {
        perror("open");
        return 1;
    }
    
    // 获取文件大小
    if (fstat(fd, &sb) == -1) {
        perror("fstat");
        close(fd);
        return 1;
    }
    
    // 映射文件到内存
    mapped = mmap(NULL, sb.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (mapped == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return 1;
    }
    
    // 可以像访问内存一样访问文件内容
    printf("文件内容: %.*s\n", (int)sb.st_size, mapped);
    
    // 修改内容(会自动同步到文件)
    if (sb.st_size > 0) {
        mapped[0] = 'X';
    }
    
    // 解除映射
    munmap(mapped, sb.st_size);
    close(fd);
    
    return 0;
}
```

## 深入理解

### 系统调用的性能考虑

#### 上下文切换开销

每次系统调用都涉及：
1. 保存用户态寄存器
2. 切换到内核态
3. 执行内核代码
4. 切换回用户态
5. 恢复用户态寄存器

这个过程有一定的性能开销，因此应该：
- 减少系统调用次数
- 使用缓冲I/O
- 批量处理数据


#### 缓冲I/O vs 直接I/O

**标准I/O库(缓冲I/O)**:
```c
FILE *fp = fopen("file.txt", "r");
fread(buffer, size, count, fp);
fclose(fp);
```

优点：
- 减少系统调用次数
- 自动缓冲管理
- 更高的性能

**系统调用(直接I/O)**:
```c
int fd = open("file.txt", O_RDONLY);
read(fd, buffer, size);
close(fd);
```

优点：
- 更精确的控制
- 适合特殊需求
- 无额外缓冲开销

### 错误处理

#### errno变量

系统调用失败时会设置全局变量`errno`：

```c
#include <errno.h>
#include <string.h>
#include <stdio.h>

int fd = open("nonexistent.txt", O_RDONLY);
if (fd == -1) {
    printf("错误码: %d\n", errno);
    printf("错误信息: %s\n", strerror(errno));
    perror("open");  // 更简便的方式
}
```

#### 常见错误码

- `EACCES`: 权限不足
- `ENOENT`: 文件不存在
- `EINTR`: 被信号中断
- `EAGAIN`: 资源暂时不可用
- `ENOMEM`: 内存不足

### 最佳实践

#### 1. 始终检查返回值

```c
// 错误示例
int fd = open("file.txt", O_RDONLY);
read(fd, buffer, size);  // 如果open失败，fd为-1

// 正确示例
int fd = open("file.txt", O_RDONLY);
if (fd == -1) {
    perror("open");
    return 1;
}
ssize_t n = read(fd, buffer, size);
if (n == -1) {
    perror("read");
    close(fd);
    return 1;
}
```


#### 2. 正确处理部分读写

```c
// read/write可能不会一次完成所有数据传输
ssize_t read_all(int fd, void *buf, size_t count) {
    size_t total = 0;
    ssize_t n;
    char *ptr = buf;
    
    while (total < count) {
        n = read(fd, ptr + total, count - total);
        if (n == -1) {
            if (errno == EINTR) {
                continue;  // 被信号中断，重试
            }
            return -1;
        }
        if (n == 0) {
            break;  // EOF
        }
        total += n;
    }
    
    return total;
}
```

#### 3. 及时关闭文件描述符

```c
int fd = open("file.txt", O_RDONLY);
if (fd == -1) {
    return -1;
}

// 使用文件...

// 确保关闭
close(fd);

// 或使用goto处理多个退出点
int process_file(void) {
    int fd = -1;
    int ret = -1;
    
    fd = open("file.txt", O_RDONLY);
    if (fd == -1) {
        goto cleanup;
    }
    
    // 处理文件...
    
    ret = 0;  // 成功
    
cleanup:
    if (fd != -1) {
        close(fd);
    }
    return ret;
}
```

#### 4. 使用O_CLOEXEC标志

```c
// 防止文件描述符泄漏到子进程
int fd = open("file.txt", O_RDONLY | O_CLOEXEC);
```

## 实践示例

### 完整示例：简单的文件复制程序

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define BUFFER_SIZE 4096

int copy_file(const char *src, const char *dst) {
    int src_fd = -1, dst_fd = -1;
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read, bytes_written;
    int ret = -1;
    
    // 打开源文件
    src_fd = open(src, O_RDONLY);
    if (src_fd == -1) {
        fprintf(stderr, "无法打开源文件 %s: %s\n", src, strerror(errno));
        goto cleanup;
    }
    
    // 创建目标文件
    dst_fd = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (dst_fd == -1) {
        fprintf(stderr, "无法创建目标文件 %s: %s\n", dst, strerror(errno));
        goto cleanup;
    }
    
    // 复制数据
    while ((bytes_read = read(src_fd, buffer, BUFFER_SIZE)) > 0) {
        char *ptr = buffer;
        while (bytes_read > 0) {
            bytes_written = write(dst_fd, ptr, bytes_read);
            if (bytes_written == -1) {
                if (errno == EINTR) {
                    continue;
                }
                fprintf(stderr, "写入错误: %s\n", strerror(errno));
                goto cleanup;
            }
            bytes_read -= bytes_written;
            ptr += bytes_written;
        }
    }
    
    if (bytes_read == -1) {
        fprintf(stderr, "读取错误: %s\n", strerror(errno));
        goto cleanup;
    }
    
    ret = 0;  // 成功
    printf("文件复制成功\n");
    
cleanup:
    if (src_fd != -1) close(src_fd);
    if (dst_fd != -1) close(dst_fd);
    return ret;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "用法: %s <源文件> <目标文件>\n", argv[0]);
        return 1;
    }
    
    return copy_file(argv[1], argv[2]);
}
```


**编译和运行**:

```bash
gcc -o copy copy.c
./copy source.txt destination.txt
```

### 完整示例：多进程并发服务器

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

void handle_client(int client_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;
    
    // 读取客户端请求
    bytes_read = read(client_fd, buffer, BUFFER_SIZE - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("[PID %d] 收到: %s\n", getpid(), buffer);
        
        // 发送响应
        snprintf(buffer, BUFFER_SIZE, "Hello from server (PID %d)", getpid());
        write(client_fd, buffer, strlen(buffer));
    }
    
    close(client_fd);
}

void sigchld_handler(int sig) {
    // 回收子进程，防止僵尸进程
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

int main(void) {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    pid_t pid;
    
    // 设置SIGCHLD信号处理
    signal(SIGCHLD, sigchld_handler);
    
    // 创建套接字
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        return 1;
    }
    
    // 设置地址重用
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // 绑定地址
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        close(server_fd);
        return 1;
    }
    
    // 监听
    if (listen(server_fd, 10) == -1) {
        perror("listen");
        close(server_fd);
        return 1;
    }
    
    printf("服务器监听端口 %d...\n", PORT);
    
    // 主循环
    while (1) {
        client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd == -1) {
            perror("accept");
            continue;
        }
        
        printf("客户端连接: %s:%d\n", 
               inet_ntoa(client_addr.sin_addr), 
               ntohs(client_addr.sin_port));
        
        // 创建子进程处理客户端
        pid = fork();
        if (pid == 0) {
            // 子进程
            close(server_fd);  // 子进程不需要监听套接字
            handle_client(client_fd);
            exit(0);
        } else if (pid > 0) {
            // 父进程
            close(client_fd);  // 父进程不需要客户端套接字
        } else {
            perror("fork");
        }
    }
    
    close(server_fd);
    return 0;
}
```


## 常见问题

### Q1: 系统调用和库函数有什么区别？

**A**: 
- **系统调用**: 内核提供的服务接口，直接陷入内核执行，如`open()`, `read()`, `write()`
- **库函数**: 用户空间的函数，可能封装了系统调用，如`fopen()`, `fread()`, `printf()`

库函数通常提供更高级的功能和缓冲机制，但系统调用提供更底层的控制。

### Q2: 为什么read/write可能返回的字节数少于请求的数量？

**A**: 有多种原因：
- 到达文件末尾
- 网络套接字的数据包边界
- 被信号中断(返回EINTR)
- 管道或FIFO的缓冲区限制

因此，应该在循环中调用read/write，直到完成所有数据传输。

### Q3: 什么时候应该使用fork()，什么时候使用线程？

**A**: 
**使用fork()的场景**:
- 需要完全独立的进程空间
- 需要更好的隔离性和安全性
- 子进程可能执行不同的程序(exec)

**使用线程的场景**:
- 需要共享内存和数据
- 需要更轻量级的并发
- 需要更快的创建和切换速度

### Q4: 如何避免僵尸进程？

**A**: 有几种方法：
1. 父进程调用`wait()`或`waitpid()`回收子进程
2. 设置SIGCHLD信号处理函数
3. 使用`signal(SIGCHLD, SIG_IGN)`忽略子进程退出信号
4. 使用双重fork技巧

```c
// 方法2示例
void sigchld_handler(int sig) {
    while (waitpid(-1, NULL, WNOHANG) > 0);
}
signal(SIGCHLD, sigchld_handler);
```

### Q5: 文件描述符会用完吗？

**A**: 会的。每个进程有文件描述符数量限制：
- 查看限制: `ulimit -n`
- 修改限制: `ulimit -n 4096`
- 系统级限制: `/proc/sys/fs/file-max`

因此要及时关闭不用的文件描述符。


### Q6: 如何处理EINTR错误？

**A**: 当系统调用被信号中断时会返回EINTR错误。通常的处理方式是重试：

```c
ssize_t safe_read(int fd, void *buf, size_t count) {
    ssize_t n;
    
    do {
        n = read(fd, buf, count);
    } while (n == -1 && errno == EINTR);
    
    return n;
}
```

某些系统调用(如`accept()`, `read()`, `write()`)可以设置`SA_RESTART`标志自动重启：

```c
struct sigaction sa;
sa.sa_handler = signal_handler;
sa.sa_flags = SA_RESTART;  // 自动重启被中断的系统调用
sigaction(SIGINT, &sa, NULL);
```

## 总结

本文介绍了Linux系统调用的核心概念和常用API：

**文件操作**:
- `open()`, `read()`, `write()`, `close()` - 基本文件I/O
- `lseek()` - 文件定位
- `mmap()` - 内存映射

**进程管理**:
- `fork()` - 创建子进程
- `exec系列` - 执行新程序
- `wait()/waitpid()` - 等待子进程

**信号处理**:
- `signal()` - 设置信号处理函数
- `kill()` - 发送信号

**网络编程**:
- `socket()`, `bind()`, `listen()`, `accept()` - TCP服务器
- `connect()` - TCP客户端

**最佳实践**:
- 始终检查返回值
- 正确处理部分读写
- 及时关闭文件描述符
- 处理EINTR错误

掌握这些系统调用是Linux应用开发的基础，为后续学习高级主题打下坚实基础。


## 延伸阅读

推荐进一步学习的资源：

- [Linux进程与线程编程](03-process-thread.html) - 深入学习多进程和多线程编程
- [Linux驱动开发入门](01-linux-driver-basics.html) - 了解内核空间编程
- [文件系统与根文件系统制作](02-rootfs.html) - 理解Linux文件系统

**推荐书籍**:
- 《UNIX环境高级编程》(APUE) - 系统调用和UNIX编程的经典教材
- 《Linux系统编程》 - 专注于Linux系统调用的实用指南
- 《Linux/UNIX系统编程手册》 - 全面深入的系统编程参考

**在线资源**:
- [Linux Man Pages](https://man7.org/linux/man-pages/) - 官方系统调用文档
- [The Linux Programming Interface](http://man7.org/tlpi/) - 在线教程和示例

## 参考资料

1. Linux Man Pages - 官方系统调用文档
2. POSIX.1-2008标准 - 系统调用标准规范
3. 《UNIX环境高级编程》第3版 - W. Richard Stevens
4. Linux内核源码 - 系统调用实现参考

---

**练习题**：

1. 编写一个程序，使用`open()`, `read()`, `write()`实现文件内容的大小写转换
2. 使用`fork()`创建多个子进程，每个子进程计算一部分数据，父进程汇总结果
3. 实现一个简单的echo服务器，能够同时处理多个客户端连接
4. 使用`mmap()`实现两个进程之间的共享内存通信
5. 编写一个程序，捕获SIGINT信号，在退出前保存程序状态

**下一步**：建议学习 [嵌入式Linux完整系统构建](../advanced/01-complete-linux-system.html)，将所学知识应用到实际项目中。
