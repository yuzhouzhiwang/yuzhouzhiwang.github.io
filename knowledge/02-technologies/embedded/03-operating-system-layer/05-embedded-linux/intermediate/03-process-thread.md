---
title: "Linux进程与线程编程：掌握多任务并发编程"
description: "深入讲解Linux进程创建、线程编程、进程间通信(IPC)、同步机制和应用开发，帮助你掌握嵌入式Linux多任务编程的核心技能"
slug: "process-thread"

# 分类信息
domain: "操作系统层"
module: "嵌入式Linux"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Linux进程
  - 线程编程
  - IPC
  - 进程间通信
  - 同步机制
  - 多任务编程
prerequisites:
  - "03-operating-system-layer/05-embedded-linux/beginner/01-embedded-linux-overview"
  - "03-operating-system-layer/05-embedded-linux/beginner/02-kernel-configuration"
  - "03-operating-system-layer/05-embedded-linux/intermediate/01-linux-driver-basics"
related_contents:
  - "03-operating-system-layer/05-embedded-linux/intermediate/02-rootfs"
  - "03-operating-system-layer/05-embedded-linux/intermediate/04-system-call"

# 学习信息
estimated_time: 80
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: "embedded-platform"
created_at: "2024-01-15"
updated_at: "2024-01-15"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - Linux进程编程
  - 线程编程
  - 进程间通信
  - IPC机制
  - 多任务编程
  - pthread
  - fork
cover_image: ""
---

# Linux进程与线程编程：掌握多任务并发编程



## 学习目标

完成本教程后，你将能够：

- [ ] 理解Linux进程和线程的概念与区别
- [ ] 掌握进程创建和管理的方法
- [ ] 熟练使用POSIX线程(pthread)编程
- [ ] 实现多种进程间通信(IPC)机制
- [ ] 掌握线程同步和互斥技术
- [ ] 处理并发编程中的常见问题
- [ ] 开发实际的多任务应用程序
- [ ] 调试和优化多任务程序

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟练掌握C语言编程
- 了解Linux系统编程基础
- 理解操作系统基本概念
- 掌握指针和内存管理
- 了解文件I/O操作

**技能要求**：
- 能够使用GCC编译器
- 会使用Makefile构建项目
- 熟悉Linux命令行操作
- 了解调试工具(gdb)的使用

**硬件和软件准备**：
- Linux开发环境（Ubuntu 20.04+推荐）
- GCC编译器（支持pthread）
- 开发板或QEMU模拟器（可选）
- 文本编辑器或IDE

## 进程与线程概述

### 进程的概念

**进程(Process)**是操作系统进行资源分配和调度的基本单位。

```
┌─────────────────────────────────────────┐
│         进程 (Process)                   │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    代码段 (Text Segment)          │  │
│  │    - 可执行指令                   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    数据段 (Data Segment)          │  │
│  │    - 全局变量                     │  │
│  │    - 静态变量                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    堆 (Heap)                      │  │
│  │    - 动态分配内存                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    栈 (Stack)                     │  │
│  │    - 局部变量                     │  │
│  │    - 函数调用                     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    进程控制块 (PCB)               │  │
│  │    - 进程ID                       │  │
│  │    - 进程状态                     │  │
│  │    - 寄存器信息                   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**进程特点**：
- 独立的地址空间
- 拥有独立的资源
- 进程间相互隔离
- 创建开销较大
- 切换开销较大

### 线程的概念

**线程(Thread)**是进程内的执行单元，是CPU调度的基本单位。

```
┌─────────────────────────────────────────┐
│         进程 (Process)                   │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    共享资源                       │  │
│  │    - 代码段                       │  │
│  │    - 数据段                       │  │
│  │    - 堆                           │  │
│  │    - 文件描述符                   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌────────┐  ┌────────┐  ┌────────┐  │
│  │ 线程1   │  │ 线程2   │  │ 线程3   │  │
│  │        │  │        │  │        │  │
│  │ 栈     │  │ 栈     │  │ 栈     │  │
│  │ 寄存器 │  │ 寄存器 │  │ 寄存器 │  │
│  │ 程序计数│  │ 程序计数│  │ 程序计数│  │
│  └────────┘  └────────┘  └────────┘  │
└─────────────────────────────────────────┘
```

**线程特点**：
- 共享进程地址空间
- 共享进程资源
- 拥有独立的栈
- 创建开销较小
- 切换开销较小

### 进程与线程对比

| 特性 | 进程 | 线程 |
|------|------|------|
| 地址空间 | 独立 | 共享 |
| 资源拥有 | 独立 | 共享 |
| 创建开销 | 大 | 小 |
| 切换开销 | 大 | 小 |
| 通信方式 | IPC | 共享内存 |
| 安全性 | 高（隔离） | 低（共享） |
| 适用场景 | 独立任务 | 协作任务 |



## 进程编程

### 进程创建 - fork()

**fork()系统调用**用于创建新进程。

**函数原型**：

```c
#include <unistd.h>

pid_t fork(void);
```

**返回值**：
- 父进程：返回子进程的PID
- 子进程：返回0
- 失败：返回-1

**基本示例**：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main(void)
{
    pid_t pid;
    
    printf("Before fork: PID = %d\n", getpid());
    
    // 创建子进程
    pid = fork();
    
    if (pid < 0) {
        // fork失败
        perror("fork failed");
        return 1;
    }
    else if (pid == 0) {
        // 子进程代码
        printf("Child process: PID = %d, Parent PID = %d\n",
               getpid(), getppid());
    }
    else {
        // 父进程代码
        printf("Parent process: PID = %d, Child PID = %d\n",
               getpid(), pid);
    }
    
    printf("Process %d: Exiting\n", getpid());
    
    return 0;
}
```

**编译和运行**：

```bash
gcc -o fork_demo fork_demo.c
./fork_demo
```

**输出示例**：

```
Before fork: PID = 1234
Parent process: PID = 1234, Child PID = 1235
Process 1234: Exiting
Child process: PID = 1235, Parent PID = 1234
Process 1235: Exiting
```

**代码说明**：
- fork()后，父子进程从fork()返回处继续执行
- 父子进程拥有独立的地址空间
- 子进程复制父进程的数据段、堆和栈
- 父子进程共享代码段

### 进程等待 - wait()和waitpid()

**wait()函数**用于等待子进程结束。

**函数原型**：

```c
#include <sys/wait.h>

pid_t wait(int *status);
pid_t waitpid(pid_t pid, int *status, int options);
```

**示例：父进程等待子进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    pid_t pid, wpid;
    int status;
    
    pid = fork();
    
    if (pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (pid == 0) {
        // 子进程
        printf("Child: PID = %d, sleeping for 2 seconds\n", getpid());
        sleep(2);
        printf("Child: Exiting with status 42\n");
        exit(42);
    }
    else {
        // 父进程
        printf("Parent: Waiting for child %d\n", pid);
        
        // 等待子进程结束
        wpid = wait(&status);
        
        if (wpid == -1) {
            perror("wait failed");
            return 1;
        }
        
        printf("Parent: Child %d terminated\n", wpid);
        
        // 检查退出状态
        if (WIFEXITED(status)) {
            printf("Parent: Child exited with status %d\n",
                   WEXITSTATUS(status));
        }
        else if (WIFSIGNALED(status)) {
            printf("Parent: Child killed by signal %d\n",
                   WTERMSIG(status));
        }
    }
    
    return 0;
}
```

**状态宏说明**：

| 宏 | 说明 |
|---|---|
| WIFEXITED(status) | 子进程正常退出返回true |
| WEXITSTATUS(status) | 获取退出状态码 |
| WIFSIGNALED(status) | 子进程被信号终止返回true |
| WTERMSIG(status) | 获取终止信号编号 |
| WIFSTOPPED(status) | 子进程被停止返回true |
| WSTOPSIG(status) | 获取停止信号编号 |

**waitpid()高级用法**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    pid_t pid1, pid2;
    int status;
    
    // 创建两个子进程
    pid1 = fork();
    if (pid1 == 0) {
        printf("Child 1: PID = %d\n", getpid());
        sleep(2);
        exit(1);
    }
    
    pid2 = fork();
    if (pid2 == 0) {
        printf("Child 2: PID = %d\n", getpid());
        sleep(1);
        exit(2);
    }
    
    // 父进程等待特定子进程
    printf("Parent: Waiting for child %d\n", pid2);
    waitpid(pid2, &status, 0);
    printf("Parent: Child %d exited with status %d\n",
           pid2, WEXITSTATUS(status));
    
    // 等待任意子进程（非阻塞）
    pid_t wpid;
    while ((wpid = waitpid(-1, &status, WNOHANG)) > 0) {
        printf("Parent: Child %d exited with status %d\n",
               wpid, WEXITSTATUS(status));
    }
    
    // 等待所有子进程
    while (wait(NULL) > 0);
    
    printf("Parent: All children terminated\n");
    
    return 0;
}
```

**waitpid()参数说明**：

**pid参数**：
- `pid > 0`: 等待指定PID的子进程
- `pid = -1`: 等待任意子进程
- `pid = 0`: 等待同组的任意子进程
- `pid < -1`: 等待进程组ID为|pid|的任意子进程

**options参数**：
- `0`: 阻塞等待
- `WNOHANG`: 非阻塞，立即返回
- `WUNTRACED`: 报告停止的子进程
- `WCONTINUED`: 报告继续运行的子进程

### 进程替换 - exec系列函数

**exec系列函数**用于在当前进程中执行新程序。

**函数族**：

```c
#include <unistd.h>

int execl(const char *path, const char *arg, ...);
int execlp(const char *file, const char *arg, ...);
int execle(const char *path, const char *arg, ..., char *const envp[]);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execve(const char *path, char *const argv[], char *const envp[]);
```

**命名规则**：
- `l`: 参数列表(list)
- `v`: 参数数组(vector)
- `p`: 使用PATH环境变量搜索
- `e`: 指定环境变量

**示例：使用exec执行新程序**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    pid_t pid;
    
    pid = fork();
    
    if (pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (pid == 0) {
        // 子进程：执行ls命令
        printf("Child: Executing ls command\n");
        
        // 方法1：使用execl
        execl("/bin/ls", "ls", "-l", "/tmp", NULL);
        
        // 如果exec成功，下面的代码不会执行
        perror("execl failed");
        exit(1);
    }
    else {
        // 父进程：等待子进程
        int status;
        wait(&status);
        printf("Parent: Child completed\n");
    }
    
    return 0;
}
```

**示例：使用execv**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    pid_t pid;
    
    pid = fork();
    
    if (pid == 0) {
        // 子进程
        char *args[] = {
            "ls",
            "-l",
            "-a",
            "/home",
            NULL  // 必须以NULL结尾
        };
        
        execv("/bin/ls", args);
        
        // 如果到达这里，说明exec失败
        perror("execv failed");
        exit(1);
    }
    else {
        // 父进程
        wait(NULL);
    }
    
    return 0;
}
```

**示例：实现简单的shell**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_CMD_LEN 1024
#define MAX_ARGS 64

int main(void)
{
    char cmd[MAX_CMD_LEN];
    char *args[MAX_ARGS];
    pid_t pid;
    
    while (1) {
        // 显示提示符
        printf("myshell> ");
        fflush(stdout);
        
        // 读取命令
        if (fgets(cmd, sizeof(cmd), stdin) == NULL) {
            break;
        }
        
        // 移除换行符
        cmd[strcspn(cmd, "\n")] = 0;
        
        // 检查退出命令
        if (strcmp(cmd, "exit") == 0) {
            break;
        }
        
        // 解析命令
        int argc = 0;
        char *token = strtok(cmd, " ");
        while (token != NULL && argc < MAX_ARGS - 1) {
            args[argc++] = token;
            token = strtok(NULL, " ");
        }
        args[argc] = NULL;
        
        if (argc == 0) {
            continue;
        }
        
        // 创建子进程执行命令
        pid = fork();
        
        if (pid < 0) {
            perror("fork failed");
            continue;
        }
        else if (pid == 0) {
            // 子进程：执行命令
            execvp(args[0], args);
            
            // 如果到达这里，说明exec失败
            perror("exec failed");
            exit(1);
        }
        else {
            // 父进程：等待子进程
            wait(NULL);
        }
    }
    
    printf("Goodbye!\n");
    return 0;
}
```

**编译和测试**：

```bash
gcc -o myshell myshell.c
./myshell

# 在shell中测试
myshell> ls -l
myshell> pwd
myshell> echo "Hello World"
myshell> exit
```



## 线程编程

### POSIX线程(pthread)基础

**pthread库**是Linux下的标准线程库。

**编译时需要链接pthread库**：

```bash
gcc -o program program.c -lpthread
```

### 线程创建和终止

**函数原型**：

```c
#include <pthread.h>

int pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                   void *(*start_routine)(void *), void *arg);
void pthread_exit(void *retval);
int pthread_join(pthread_t thread, void **retval);
int pthread_detach(pthread_t thread);
```

**基本示例**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

// 线程函数
void *thread_function(void *arg)
{
    int thread_id = *(int *)arg;
    
    printf("Thread %d: Started\n", thread_id);
    
    // 模拟工作
    sleep(2);
    
    printf("Thread %d: Finished\n", thread_id);
    
    // 返回值
    int *result = malloc(sizeof(int));
    *result = thread_id * 10;
    
    pthread_exit(result);
}

int main(void)
{
    pthread_t threads[3];
    int thread_ids[3] = {1, 2, 3};
    int i;
    
    // 创建线程
    for (i = 0; i < 3; i++) {
        if (pthread_create(&threads[i], NULL, thread_function,
                          &thread_ids[i]) != 0) {
            perror("pthread_create failed");
            return 1;
        }
        printf("Main: Created thread %d\n", i + 1);
    }
    
    // 等待线程结束
    for (i = 0; i < 3; i++) {
        void *result;
        if (pthread_join(threads[i], &result) != 0) {
            perror("pthread_join failed");
            continue;
        }
        
        printf("Main: Thread %d returned %d\n", i + 1, *(int *)result);
        free(result);
    }
    
    printf("Main: All threads completed\n");
    
    return 0;
}
```

**编译和运行**：

```bash
gcc -o pthread_demo pthread_demo.c -lpthread
./pthread_demo
```

**输出示例**：

```
Main: Created thread 1
Main: Created thread 2
Main: Created thread 3
Thread 1: Started
Thread 2: Started
Thread 3: Started
Thread 1: Finished
Thread 2: Finished
Thread 3: Finished
Main: Thread 1 returned 10
Main: Thread 2 returned 20
Main: Thread 3 returned 30
Main: All threads completed
```

### 线程分离

**分离线程**不需要pthread_join()，资源自动回收。

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *detached_thread(void *arg)
{
    printf("Detached thread: Running\n");
    sleep(1);
    printf("Detached thread: Exiting\n");
    return NULL;
}

int main(void)
{
    pthread_t thread;
    
    // 创建线程
    pthread_create(&thread, NULL, detached_thread, NULL);
    
    // 分离线程
    pthread_detach(thread);
    
    printf("Main: Thread detached\n");
    
    // 主线程继续运行
    sleep(2);
    
    printf("Main: Exiting\n");
    
    return 0;
}
```

**或者在创建时设置分离属性**：

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *detached_thread(void *arg)
{
    printf("Detached thread: Running\n");
    sleep(1);
    printf("Detached thread: Exiting\n");
    return NULL;
}

int main(void)
{
    pthread_t thread;
    pthread_attr_t attr;
    
    // 初始化线程属性
    pthread_attr_init(&attr);
    
    // 设置分离状态
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
    
    // 创建分离线程
    pthread_create(&thread, &attr, detached_thread, NULL);
    
    // 销毁属性对象
    pthread_attr_destroy(&attr);
    
    printf("Main: Thread created as detached\n");
    
    sleep(2);
    
    return 0;
}
```

### 线程同步 - 互斥锁(Mutex)

**互斥锁**用于保护共享资源，防止竞态条件。

**函数原型**：

```c
#include <pthread.h>

int pthread_mutex_init(pthread_mutex_t *mutex,
                       const pthread_mutexattr_t *attr);
int pthread_mutex_destroy(pthread_mutex_t *mutex);
int pthread_mutex_lock(pthread_mutex_t *mutex);
int pthread_mutex_trylock(pthread_mutex_t *mutex);
int pthread_mutex_unlock(pthread_mutex_t *mutex);
```

**示例：使用互斥锁保护共享变量**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 5
#define NUM_INCREMENTS 100000

// 共享变量
int counter = 0;

// 互斥锁
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// 不使用互斥锁的线程函数
void *unsafe_increment(void *arg)
{
    int i;
    for (i = 0; i < NUM_INCREMENTS; i++) {
        counter++;  // 竞态条件！
    }
    return NULL;
}

// 使用互斥锁的线程函数
void *safe_increment(void *arg)
{
    int i;
    for (i = 0; i < NUM_INCREMENTS; i++) {
        pthread_mutex_lock(&mutex);
        counter++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main(void)
{
    pthread_t threads[NUM_THREADS];
    int i;
    
    // 测试不安全的版本
    printf("Testing unsafe increment:\n");
    counter = 0;
    
    for (i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, unsafe_increment, NULL);
    }
    
    for (i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Expected: %d, Actual: %d\n",
           NUM_THREADS * NUM_INCREMENTS, counter);
    
    // 测试安全的版本
    printf("\nTesting safe increment:\n");
    counter = 0;
    
    for (i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, safe_increment, NULL);
    }
    
    for (i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Expected: %d, Actual: %d\n",
           NUM_THREADS * NUM_INCREMENTS, counter);
    
    pthread_mutex_destroy(&mutex);
    
    return 0;
}
```

**输出示例**：

```
Testing unsafe increment:
Expected: 500000, Actual: 387654  # 结果不正确！

Testing safe increment:
Expected: 500000, Actual: 500000  # 结果正确
```

**互斥锁的使用模式**：

```c
// 模式1：基本使用
pthread_mutex_lock(&mutex);
// 临界区代码
pthread_mutex_unlock(&mutex);

// 模式2：尝试加锁
if (pthread_mutex_trylock(&mutex) == 0) {
    // 获得锁，执行临界区代码
    pthread_mutex_unlock(&mutex);
} else {
    // 未获得锁，执行其他操作
}

// 模式3：带超时的加锁（需要POSIX.1-2001）
struct timespec timeout;
clock_gettime(CLOCK_REALTIME, &timeout);
timeout.tv_sec += 5;  // 5秒超时

if (pthread_mutex_timedlock(&mutex, &timeout) == 0) {
    // 获得锁
    pthread_mutex_unlock(&mutex);
} else {
    // 超时或错误
}
```

### 线程同步 - 条件变量

**条件变量**用于线程间的同步，等待某个条件成立。

**函数原型**：

```c
#include <pthread.h>

int pthread_cond_init(pthread_cond_t *cond,
                      const pthread_condattr_t *attr);
int pthread_cond_destroy(pthread_cond_t *cond);
int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex);
int pthread_cond_timedwait(pthread_cond_t *cond, pthread_mutex_t *mutex,
                           const struct timespec *abstime);
int pthread_cond_signal(pthread_cond_t *cond);
int pthread_cond_broadcast(pthread_cond_t *cond);
```

**示例：生产者-消费者模型**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 10

// 共享缓冲区
int buffer[BUFFER_SIZE];
int count = 0;  // 缓冲区中的数据数量

// 同步原语
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t not_full = PTHREAD_COND_INITIALIZER;
pthread_cond_t not_empty = PTHREAD_COND_INITIALIZER;

// 生产者线程
void *producer(void *arg)
{
    int id = *(int *)arg;
    int item;
    
    for (item = 0; item < 20; item++) {
        // 加锁
        pthread_mutex_lock(&mutex);
        
        // 等待缓冲区不满
        while (count == BUFFER_SIZE) {
            printf("Producer %d: Buffer full, waiting...\n", id);
            pthread_cond_wait(&not_full, &mutex);
        }
        
        // 生产数据
        buffer[count] = item;
        count++;
        printf("Producer %d: Produced item %d (count = %d)\n",
               id, item, count);
        
        // 通知消费者
        pthread_cond_signal(&not_empty);
        
        // 解锁
        pthread_mutex_unlock(&mutex);
        
        // 模拟生产时间
        usleep(100000);  // 100ms
    }
    
    return NULL;
}

// 消费者线程
void *consumer(void *arg)
{
    int id = *(int *)arg;
    int item;
    
    for (int i = 0; i < 20; i++) {
        // 加锁
        pthread_mutex_lock(&mutex);
        
        // 等待缓冲区不空
        while (count == 0) {
            printf("Consumer %d: Buffer empty, waiting...\n", id);
            pthread_cond_wait(&not_empty, &mutex);
        }
        
        // 消费数据
        count--;
        item = buffer[count];
        printf("Consumer %d: Consumed item %d (count = %d)\n",
               id, item, count);
        
        // 通知生产者
        pthread_cond_signal(&not_full);
        
        // 解锁
        pthread_mutex_unlock(&mutex);
        
        // 模拟消费时间
        usleep(150000);  // 150ms
    }
    
    return NULL;
}

int main(void)
{
    pthread_t prod_thread, cons_thread;
    int prod_id = 1, cons_id = 1;
    
    // 创建生产者和消费者线程
    pthread_create(&prod_thread, NULL, producer, &prod_id);
    pthread_create(&cons_thread, NULL, consumer, &cons_id);
    
    // 等待线程结束
    pthread_join(prod_thread, NULL);
    pthread_join(cons_thread, NULL);
    
    // 清理
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&not_full);
    pthread_cond_destroy(&not_empty);
    
    printf("Main: All threads completed\n");
    
    return 0;
}
```

**条件变量使用要点**：

1. **必须与互斥锁配合使用**
2. **等待前必须持有锁**
3. **使用while循环检查条件**（防止虚假唤醒）
4. **signal唤醒一个线程，broadcast唤醒所有线程**



## 进程间通信(IPC)

### 管道(Pipe)

**管道**是最简单的IPC机制，用于父子进程间通信。

**函数原型**：

```c
#include <unistd.h>

int pipe(int pipefd[2]);
```

**参数说明**：
- `pipefd[0]`: 读端
- `pipefd[1]`: 写端

**示例：父子进程通过管道通信**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    int pipefd[2];
    pid_t pid;
    char write_msg[] = "Hello from parent!";
    char read_msg[100];
    
    // 创建管道
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }
    
    // 创建子进程
    pid = fork();
    
    if (pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (pid == 0) {
        // 子进程：读取数据
        close(pipefd[1]);  // 关闭写端
        
        ssize_t n = read(pipefd[0], read_msg, sizeof(read_msg));
        if (n > 0) {
            read_msg[n] = '\0';
            printf("Child: Received: %s\n", read_msg);
        }
        
        close(pipefd[0]);
        exit(0);
    }
    else {
        // 父进程：写入数据
        close(pipefd[0]);  // 关闭读端
        
        printf("Parent: Sending: %s\n", write_msg);
        write(pipefd[1], write_msg, strlen(write_msg));
        
        close(pipefd[1]);
        wait(NULL);
    }
    
    return 0;
}
```

**示例：实现简单的管道命令**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

// 实现: ls | wc -l
int main(void)
{
    int pipefd[2];
    pid_t pid1, pid2;
    
    // 创建管道
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }
    
    // 创建第一个子进程（ls）
    pid1 = fork();
    if (pid1 == 0) {
        // 重定向stdout到管道写端
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        
        // 执行ls命令
        execlp("ls", "ls", NULL);
        perror("execlp ls failed");
        exit(1);
    }
    
    // 创建第二个子进程（wc）
    pid2 = fork();
    if (pid2 == 0) {
        // 重定向stdin到管道读端
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        
        // 执行wc命令
        execlp("wc", "wc", "-l", NULL);
        perror("execlp wc failed");
        exit(1);
    }
    
    // 父进程关闭管道
    close(pipefd[0]);
    close(pipefd[1]);
    
    // 等待子进程
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);
    
    return 0;
}
```

### 命名管道(FIFO)

**命名管道**可用于无亲缘关系的进程间通信。

**函数原型**：

```c
#include <sys/types.h>
#include <sys/stat.h>

int mkfifo(const char *pathname, mode_t mode);
```

**示例：写进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

#define FIFO_NAME "/tmp/myfifo"

int main(void)
{
    int fd;
    char message[] = "Hello from writer!";
    
    // 创建FIFO
    if (mkfifo(FIFO_NAME, 0666) == -1) {
        perror("mkfifo failed");
        // 如果FIFO已存在，继续
    }
    
    printf("Writer: Opening FIFO...\n");
    
    // 打开FIFO（阻塞直到有读者）
    fd = open(FIFO_NAME, O_WRONLY);
    if (fd == -1) {
        perror("open failed");
        return 1;
    }
    
    printf("Writer: Writing message...\n");
    
    // 写入数据
    write(fd, message, strlen(message));
    
    printf("Writer: Message sent\n");
    
    close(fd);
    
    return 0;
}
```

**示例：读进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

#define FIFO_NAME "/tmp/myfifo"

int main(void)
{
    int fd;
    char buffer[100];
    ssize_t n;
    
    printf("Reader: Opening FIFO...\n");
    
    // 打开FIFO（阻塞直到有写者）
    fd = open(FIFO_NAME, O_RDONLY);
    if (fd == -1) {
        perror("open failed");
        return 1;
    }
    
    printf("Reader: Reading message...\n");
    
    // 读取数据
    n = read(fd, buffer, sizeof(buffer) - 1);
    if (n > 0) {
        buffer[n] = '\0';
        printf("Reader: Received: %s\n", buffer);
    }
    
    close(fd);
    
    // 删除FIFO
    unlink(FIFO_NAME);
    
    return 0;
}
```

**编译和测试**：

```bash
# 编译
gcc -o fifo_writer fifo_writer.c
gcc -o fifo_reader fifo_reader.c

# 在两个终端中运行
# 终端1
./fifo_reader

# 终端2
./fifo_writer
```

### 共享内存(Shared Memory)

**共享内存**是最快的IPC机制，多个进程可以访问同一块内存。

**函数原型**：

```c
#include <sys/shm.h>

int shmget(key_t key, size_t size, int shmflg);
void *shmat(int shmid, const void *shmaddr, int shmflg);
int shmdt(const void *shmaddr);
int shmctl(int shmid, int cmd, struct shmid_ds *buf);
```

**示例：写进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/shm.h>
#include <sys/ipc.h>

#define SHM_SIZE 1024
#define SHM_KEY 1234

int main(void)
{
    int shmid;
    char *shmaddr;
    char message[] = "Hello from shared memory!";
    
    // 创建共享内存
    shmid = shmget(SHM_KEY, SHM_SIZE, IPC_CREAT | 0666);
    if (shmid == -1) {
        perror("shmget failed");
        return 1;
    }
    
    printf("Writer: Shared memory created (ID: %d)\n", shmid);
    
    // 连接共享内存
    shmaddr = shmat(shmid, NULL, 0);
    if (shmaddr == (char *)-1) {
        perror("shmat failed");
        return 1;
    }
    
    printf("Writer: Writing to shared memory...\n");
    
    // 写入数据
    strcpy(shmaddr, message);
    
    printf("Writer: Message written\n");
    printf("Writer: Press Enter to detach...\n");
    getchar();
    
    // 分离共享内存
    shmdt(shmaddr);
    
    return 0;
}
```

**示例：读进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/ipc.h>

#define SHM_SIZE 1024
#define SHM_KEY 1234

int main(void)
{
    int shmid;
    char *shmaddr;
    
    // 获取共享内存
    shmid = shmget(SHM_KEY, SHM_SIZE, 0666);
    if (shmid == -1) {
        perror("shmget failed");
        return 1;
    }
    
    printf("Reader: Shared memory found (ID: %d)\n", shmid);
    
    // 连接共享内存
    shmaddr = shmat(shmid, NULL, 0);
    if (shmaddr == (char *)-1) {
        perror("shmat failed");
        return 1;
    }
    
    printf("Reader: Reading from shared memory...\n");
    
    // 读取数据
    printf("Reader: Message: %s\n", shmaddr);
    
    // 分离共享内存
    shmdt(shmaddr);
    
    // 删除共享内存
    shmctl(shmid, IPC_RMID, NULL);
    printf("Reader: Shared memory deleted\n");
    
    return 0;
}
```

**编译和测试**：

```bash
# 编译
gcc -o shm_writer shm_writer.c
gcc -o shm_reader shm_reader.c

# 运行
# 终端1
./shm_writer

# 终端2
./shm_reader

# 查看共享内存
ipcs -m

# 删除共享内存（如果需要）
ipcrm -m <shmid>
```

### 消息队列(Message Queue)

**消息队列**允许进程以消息的形式交换数据。

**函数原型**：

```c
#include <sys/msg.h>

int msgget(key_t key, int msgflg);
int msgsnd(int msqid, const void *msgp, size_t msgsz, int msgflg);
ssize_t msgrcv(int msqid, void *msgp, size_t msgsz, long msgtyp, int msgflg);
int msgctl(int msqid, int cmd, struct msqid_ds *buf);
```

**示例：发送进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/msg.h>
#include <sys/ipc.h>

#define MSG_KEY 5678

// 消息结构
struct message {
    long msg_type;
    char msg_text[100];
};

int main(void)
{
    int msqid;
    struct message msg;
    
    // 创建消息队列
    msqid = msgget(MSG_KEY, IPC_CREAT | 0666);
    if (msqid == -1) {
        perror("msgget failed");
        return 1;
    }
    
    printf("Sender: Message queue created (ID: %d)\n", msqid);
    
    // 发送消息
    msg.msg_type = 1;
    strcpy(msg.msg_text, "Hello from message queue!");
    
    if (msgsnd(msqid, &msg, strlen(msg.msg_text) + 1, 0) == -1) {
        perror("msgsnd failed");
        return 1;
    }
    
    printf("Sender: Message sent: %s\n", msg.msg_text);
    
    return 0;
}
```

**示例：接收进程**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/msg.h>
#include <sys/ipc.h>

#define MSG_KEY 5678

// 消息结构
struct message {
    long msg_type;
    char msg_text[100];
};

int main(void)
{
    int msqid;
    struct message msg;
    
    // 获取消息队列
    msqid = msgget(MSG_KEY, 0666);
    if (msqid == -1) {
        perror("msgget failed");
        return 1;
    }
    
    printf("Receiver: Message queue found (ID: %d)\n", msqid);
    
    // 接收消息
    if (msgrcv(msqid, &msg, sizeof(msg.msg_text), 1, 0) == -1) {
        perror("msgrcv failed");
        return 1;
    }
    
    printf("Receiver: Message received: %s\n", msg.msg_text);
    
    // 删除消息队列
    msgctl(msqid, IPC_RMID, NULL);
    printf("Receiver: Message queue deleted\n");
    
    return 0;
}
```

### 信号量(Semaphore)

**信号量**用于进程间同步和互斥。

**函数原型**：

```c
#include <sys/sem.h>

int semget(key_t key, int nsems, int semflg);
int semop(int semid, struct sembuf *sops, size_t nsops);
int semctl(int semid, int semnum, int cmd, ...);
```

**示例：使用信号量保护共享资源**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/sem.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>

#define SEM_KEY 9999
#define SHM_KEY 8888

// 信号量操作
union semun {
    int val;
    struct semid_ds *buf;
    unsigned short *array;
};

// P操作（等待）
void sem_wait(int semid)
{
    struct sembuf sb = {0, -1, 0};
    semop(semid, &sb, 1);
}

// V操作（信号）
void sem_signal(int semid)
{
    struct sembuf sb = {0, 1, 0};
    semop(semid, &sb, 1);
}

int main(void)
{
    int semid, shmid;
    int *counter;
    union semun arg;
    pid_t pid;
    
    // 创建信号量
    semid = semget(SEM_KEY, 1, IPC_CREAT | 0666);
    if (semid == -1) {
        perror("semget failed");
        return 1;
    }
    
    // 初始化信号量为1（互斥锁）
    arg.val = 1;
    semctl(semid, 0, SETVAL, arg);
    
    // 创建共享内存
    shmid = shmget(SHM_KEY, sizeof(int), IPC_CREAT | 0666);
    counter = shmat(shmid, NULL, 0);
    *counter = 0;
    
    // 创建多个子进程
    for (int i = 0; i < 5; i++) {
        pid = fork();
        if (pid == 0) {
            // 子进程
            for (int j = 0; j < 1000; j++) {
                sem_wait(semid);  // P操作
                (*counter)++;
                sem_signal(semid);  // V操作
            }
            exit(0);
        }
    }
    
    // 等待所有子进程
    for (int i = 0; i < 5; i++) {
        wait(NULL);
    }
    
    printf("Final counter value: %d (expected: 5000)\n", *counter);
    
    // 清理
    shmdt(counter);
    shmctl(shmid, IPC_RMID, NULL);
    semctl(semid, 0, IPC_RMID);
    
    return 0;
}
```

### IPC机制对比

| IPC机制 | 速度 | 使用难度 | 适用场景 |
|---------|------|---------|---------|
| 管道 | 中 | 简单 | 父子进程通信 |
| 命名管道 | 中 | 简单 | 无亲缘关系进程 |
| 共享内存 | 快 | 复杂 | 大量数据交换 |
| 消息队列 | 中 | 中等 | 消息传递 |
| 信号量 | 快 | 中等 | 同步和互斥 |
| 套接字 | 慢 | 复杂 | 网络通信 |



## 实战项目：多任务数据采集系统

### 项目概述

实现一个多任务数据采集系统，包含：
- 数据采集线程（模拟传感器读取）
- 数据处理线程（数据分析）
- 数据存储线程（写入文件）
- 监控线程（系统状态监控）

### 项目架构

```
┌─────────────────────────────────────────┐
│         主进程                           │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │ 采集线程  │  │ 处理线程  │           │
│  │          │  │          │           │
│  │ 读取数据  │→│ 分析数据  │           │
│  └──────────┘  └──────────┘           │
│       ↓             ↓                  │
│  ┌──────────┐  ┌──────────┐           │
│  │ 存储线程  │  │ 监控线程  │           │
│  │          │  │          │           │
│  │ 写入文件  │  │ 状态监控  │           │
│  └──────────┘  └──────────┘           │
└─────────────────────────────────────────┘
```

### 完整代码实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

#define BUFFER_SIZE 100
#define MAX_SAMPLES 1000

// 数据结构
typedef struct {
    int id;
    double value;
    time_t timestamp;
} SensorData;

// 循环缓冲区
typedef struct {
    SensorData data[BUFFER_SIZE];
    int read_pos;
    int write_pos;
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t not_full;
    pthread_cond_t not_empty;
} CircularBuffer;

// 统计信息
typedef struct {
    int samples_collected;
    int samples_processed;
    int samples_stored;
    double avg_value;
    pthread_mutex_t mutex;
} Statistics;

// 全局变量
CircularBuffer buffer;
Statistics stats;
int running = 1;

// 初始化缓冲区
void buffer_init(CircularBuffer *buf)
{
    buf->read_pos = 0;
    buf->write_pos = 0;
    buf->count = 0;
    pthread_mutex_init(&buf->mutex, NULL);
    pthread_cond_init(&buf->not_full, NULL);
    pthread_cond_init(&buf->not_empty, NULL);
}

// 写入缓冲区
void buffer_write(CircularBuffer *buf, SensorData *data)
{
    pthread_mutex_lock(&buf->mutex);
    
    // 等待缓冲区不满
    while (buf->count == BUFFER_SIZE) {
        pthread_cond_wait(&buf->not_full, &buf->mutex);
    }
    
    // 写入数据
    buf->data[buf->write_pos] = *data;
    buf->write_pos = (buf->write_pos + 1) % BUFFER_SIZE;
    buf->count++;
    
    // 通知读者
    pthread_cond_signal(&buf->not_empty);
    
    pthread_mutex_unlock(&buf->mutex);
}

// 读取缓冲区
int buffer_read(CircularBuffer *buf, SensorData *data)
{
    pthread_mutex_lock(&buf->mutex);
    
    // 等待缓冲区不空
    while (buf->count == 0 && running) {
        pthread_cond_wait(&buf->not_empty, &buf->mutex);
    }
    
    if (buf->count == 0) {
        pthread_mutex_unlock(&buf->mutex);
        return 0;  // 缓冲区空且系统停止
    }
    
    // 读取数据
    *data = buf->data[buf->read_pos];
    buf->read_pos = (buf->read_pos + 1) % BUFFER_SIZE;
    buf->count--;
    
    // 通知写者
    pthread_cond_signal(&buf->not_full);
    
    pthread_mutex_unlock(&buf->mutex);
    return 1;
}

// 数据采集线程
void *collector_thread(void *arg)
{
    SensorData data;
    int id = 0;
    
    printf("Collector: Started\n");
    
    while (running && id < MAX_SAMPLES) {
        // 模拟传感器读取
        data.id = id++;
        data.value = 20.0 + (rand() % 100) / 10.0;  // 20.0-30.0
        data.timestamp = time(NULL);
        
        // 写入缓冲区
        buffer_write(&buffer, &data);
        
        // 更新统计
        pthread_mutex_lock(&stats.mutex);
        stats.samples_collected++;
        pthread_mutex_unlock(&stats.mutex);
        
        // 模拟采集间隔
        usleep(10000);  // 10ms
    }
    
    printf("Collector: Finished (%d samples)\n", id);
    return NULL;
}

// 数据处理线程
void *processor_thread(void *arg)
{
    SensorData data;
    double sum = 0;
    int count = 0;
    
    printf("Processor: Started\n");
    
    while (running || buffer.count > 0) {
        // 从缓冲区读取
        if (!buffer_read(&buffer, &data)) {
            break;
        }
        
        // 处理数据（计算平均值）
        sum += data.value;
        count++;
        
        // 更新统计
        pthread_mutex_lock(&stats.mutex);
        stats.samples_processed++;
        stats.avg_value = sum / count;
        pthread_mutex_unlock(&stats.mutex);
        
        // 模拟处理时间
        usleep(5000);  // 5ms
    }
    
    printf("Processor: Finished (%d samples, avg=%.2f)\n",
           count, sum / count);
    return NULL;
}

// 数据存储线程
void *storage_thread(void *arg)
{
    FILE *fp;
    SensorData data;
    
    printf("Storage: Started\n");
    
    // 打开文件
    fp = fopen("sensor_data.txt", "w");
    if (!fp) {
        perror("fopen failed");
        return NULL;
    }
    
    fprintf(fp, "ID,Value,Timestamp\n");
    
    while (running || buffer.count > 0) {
        // 从缓冲区读取
        if (!buffer_read(&buffer, &data)) {
            break;
        }
        
        // 写入文件
        fprintf(fp, "%d,%.2f,%ld\n",
                data.id, data.value, data.timestamp);
        
        // 更新统计
        pthread_mutex_lock(&stats.mutex);
        stats.samples_stored++;
        pthread_mutex_unlock(&stats.mutex);
        
        // 定期刷新
        if (stats.samples_stored % 100 == 0) {
            fflush(fp);
        }
    }
    
    fclose(fp);
    printf("Storage: Finished (%d samples)\n", stats.samples_stored);
    return NULL;
}

// 监控线程
void *monitor_thread(void *arg)
{
    printf("Monitor: Started\n");
    
    while (running) {
        sleep(1);
        
        pthread_mutex_lock(&stats.mutex);
        printf("Monitor: Collected=%d, Processed=%d, Stored=%d, "
               "Avg=%.2f, Buffer=%d\n",
               stats.samples_collected,
               stats.samples_processed,
               stats.samples_stored,
               stats.avg_value,
               buffer.count);
        pthread_mutex_unlock(&stats.mutex);
    }
    
    printf("Monitor: Finished\n");
    return NULL;
}

int main(void)
{
    pthread_t collector, processor, storage, monitor;
    
    // 初始化
    buffer_init(&buffer);
    memset(&stats, 0, sizeof(stats));
    pthread_mutex_init(&stats.mutex, NULL);
    srand(time(NULL));
    
    printf("Main: Starting data acquisition system\n");
    
    // 创建线程
    pthread_create(&collector, NULL, collector_thread, NULL);
    pthread_create(&processor, NULL, processor_thread, NULL);
    pthread_create(&storage, NULL, storage_thread, NULL);
    pthread_create(&monitor, NULL, monitor_thread, NULL);
    
    // 运行10秒
    sleep(10);
    
    // 停止系统
    printf("\nMain: Stopping system...\n");
    running = 0;
    
    // 唤醒所有等待的线程
    pthread_cond_broadcast(&buffer.not_empty);
    pthread_cond_broadcast(&buffer.not_full);
    
    // 等待线程结束
    pthread_join(collector, NULL);
    pthread_join(processor, NULL);
    pthread_join(storage, NULL);
    pthread_join(monitor, NULL);
    
    // 清理
    pthread_mutex_destroy(&buffer.mutex);
    pthread_cond_destroy(&buffer.not_full);
    pthread_cond_destroy(&buffer.not_empty);
    pthread_mutex_destroy(&stats.mutex);
    
    printf("\nMain: System stopped\n");
    printf("Final statistics:\n");
    printf("  Collected: %d samples\n", stats.samples_collected);
    printf("  Processed: %d samples\n", stats.samples_processed);
    printf("  Stored: %d samples\n", stats.samples_stored);
    printf("  Average value: %.2f\n", stats.avg_value);
    
    return 0;
}
```

**编译和运行**：

```bash
gcc -o data_acquisition data_acquisition.c -lpthread
./data_acquisition
```

**输出示例**：

```
Main: Starting data acquisition system
Collector: Started
Processor: Started
Storage: Started
Monitor: Started
Monitor: Collected=100, Processed=95, Stored=90, Avg=25.34, Buffer=5
Monitor: Collected=200, Processed=195, Stored=190, Avg=25.12, Buffer=5
...
Main: Stopping system...
Collector: Finished (1000 samples)
Processor: Finished (1000 samples, avg=25.23)
Storage: Finished (1000 samples)
Monitor: Finished

Main: System stopped
Final statistics:
  Collected: 1000 samples
  Processed: 1000 samples
  Stored: 1000 samples
  Average value: 25.23
```

### 项目要点

**1. 线程同步**：
- 使用互斥锁保护共享数据
- 使用条件变量实现生产者-消费者模型
- 避免死锁和竞态条件

**2. 资源管理**：
- 正确初始化和销毁同步原语
- 及时释放资源
- 处理异常情况

**3. 性能优化**：
- 使用循环缓冲区减少内存分配
- 批量写入文件减少I/O次数
- 合理设置线程优先级

**4. 错误处理**：
- 检查所有系统调用返回值
- 提供清晰的错误信息
- 优雅地处理异常



## 调试和优化

### 调试技巧

#### 使用GDB调试多线程程序

```bash
# 编译时加入调试信息
gcc -g -o program program.c -lpthread

# 启动GDB
gdb ./program

# GDB命令
(gdb) break main              # 设置断点
(gdb) run                     # 运行程序
(gdb) info threads            # 查看所有线程
(gdb) thread 2                # 切换到线程2
(gdb) bt                      # 查看调用栈
(gdb) print variable          # 打印变量
(gdb) continue                # 继续执行
```

#### 检测死锁

**示例：死锁场景**：

```c
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex2 = PTHREAD_MUTEX_INITIALIZER;

void *thread1_func(void *arg)
{
    pthread_mutex_lock(&mutex1);
    printf("Thread 1: Locked mutex1\n");
    sleep(1);
    
    printf("Thread 1: Waiting for mutex2...\n");
    pthread_mutex_lock(&mutex2);  // 死锁！
    printf("Thread 1: Locked mutex2\n");
    
    pthread_mutex_unlock(&mutex2);
    pthread_mutex_unlock(&mutex1);
    return NULL;
}

void *thread2_func(void *arg)
{
    pthread_mutex_lock(&mutex2);
    printf("Thread 2: Locked mutex2\n");
    sleep(1);
    
    printf("Thread 2: Waiting for mutex1...\n");
    pthread_mutex_lock(&mutex1);  // 死锁！
    printf("Thread 2: Locked mutex1\n");
    
    pthread_mutex_unlock(&mutex1);
    pthread_mutex_unlock(&mutex2);
    return NULL;
}

int main(void)
{
    pthread_t t1, t2;
    
    pthread_create(&t1, NULL, thread1_func, NULL);
    pthread_create(&t2, NULL, thread2_func, NULL);
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    return 0;
}
```

**避免死锁的方法**：

1. **按固定顺序获取锁**：

```c
// 总是先锁mutex1，再锁mutex2
void *thread_func(void *arg)
{
    pthread_mutex_lock(&mutex1);
    pthread_mutex_lock(&mutex2);
    
    // 临界区代码
    
    pthread_mutex_unlock(&mutex2);
    pthread_mutex_unlock(&mutex1);
    return NULL;
}
```

2. **使用trylock**：

```c
void *thread_func(void *arg)
{
    while (1) {
        pthread_mutex_lock(&mutex1);
        
        if (pthread_mutex_trylock(&mutex2) == 0) {
            // 成功获取两个锁
            // 临界区代码
            pthread_mutex_unlock(&mutex2);
            pthread_mutex_unlock(&mutex1);
            break;
        }
        
        // 未获取mutex2，释放mutex1重试
        pthread_mutex_unlock(&mutex1);
        usleep(1000);
    }
    return NULL;
}
```

#### 使用Valgrind检测内存问题

```bash
# 安装Valgrind
sudo apt install valgrind

# 检测内存泄漏
valgrind --leak-check=full ./program

# 检测线程错误
valgrind --tool=helgrind ./program

# 检测数据竞争
valgrind --tool=drd ./program
```

### 性能优化

#### 减少锁竞争

**1. 减小临界区**：

```c
// 不好的做法
pthread_mutex_lock(&mutex);
// 大量非共享数据的操作
int result = complex_calculation();
shared_data = result;
pthread_mutex_unlock(&mutex);

// 好的做法
int result = complex_calculation();  // 在锁外计算
pthread_mutex_lock(&mutex);
shared_data = result;  // 只在必要时加锁
pthread_mutex_unlock(&mutex);
```

**2. 使用读写锁**：

```c
#include <pthread.h>

pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;

// 读操作（可以并发）
void *reader_thread(void *arg)
{
    pthread_rwlock_rdlock(&rwlock);
    // 读取共享数据
    pthread_rwlock_unlock(&rwlock);
    return NULL;
}

// 写操作（独占）
void *writer_thread(void *arg)
{
    pthread_rwlock_wrlock(&rwlock);
    // 修改共享数据
    pthread_rwlock_unlock(&rwlock);
    return NULL;
}
```

**3. 使用原子操作**：

```c
#include <stdatomic.h>

atomic_int counter = 0;

void *thread_func(void *arg)
{
    for (int i = 0; i < 10000; i++) {
        atomic_fetch_add(&counter, 1);  // 原子递增
    }
    return NULL;
}
```

#### 线程池

**实现简单的线程池**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define THREAD_POOL_SIZE 4
#define TASK_QUEUE_SIZE 100

// 任务结构
typedef struct {
    void (*function)(void *);
    void *argument;
} Task;

// 线程池结构
typedef struct {
    pthread_t threads[THREAD_POOL_SIZE];
    Task task_queue[TASK_QUEUE_SIZE];
    int queue_front;
    int queue_rear;
    int queue_count;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    int shutdown;
} ThreadPool;

ThreadPool pool;

// 工作线程函数
void *worker_thread(void *arg)
{
    while (1) {
        pthread_mutex_lock(&pool.mutex);
        
        // 等待任务
        while (pool.queue_count == 0 && !pool.shutdown) {
            pthread_cond_wait(&pool.not_empty, &pool.mutex);
        }
        
        if (pool.shutdown) {
            pthread_mutex_unlock(&pool.mutex);
            break;
        }
        
        // 取出任务
        Task task = pool.task_queue[pool.queue_front];
        pool.queue_front = (pool.queue_front + 1) % TASK_QUEUE_SIZE;
        pool.queue_count--;
        
        pthread_cond_signal(&pool.not_full);
        pthread_mutex_unlock(&pool.mutex);
        
        // 执行任务
        task.function(task.argument);
    }
    
    return NULL;
}

// 初始化线程池
void threadpool_init(void)
{
    pool.queue_front = 0;
    pool.queue_rear = 0;
    pool.queue_count = 0;
    pool.shutdown = 0;
    
    pthread_mutex_init(&pool.mutex, NULL);
    pthread_cond_init(&pool.not_empty, NULL);
    pthread_cond_init(&pool.not_full, NULL);
    
    // 创建工作线程
    for (int i = 0; i < THREAD_POOL_SIZE; i++) {
        pthread_create(&pool.threads[i], NULL, worker_thread, NULL);
    }
}

// 添加任务
void threadpool_add_task(void (*function)(void *), void *argument)
{
    pthread_mutex_lock(&pool.mutex);
    
    // 等待队列不满
    while (pool.queue_count == TASK_QUEUE_SIZE) {
        pthread_cond_wait(&pool.not_full, &pool.mutex);
    }
    
    // 添加任务
    pool.task_queue[pool.queue_rear].function = function;
    pool.task_queue[pool.queue_rear].argument = argument;
    pool.queue_rear = (pool.queue_rear + 1) % TASK_QUEUE_SIZE;
    pool.queue_count++;
    
    pthread_cond_signal(&pool.not_empty);
    pthread_mutex_unlock(&pool.mutex);
}

// 销毁线程池
void threadpool_destroy(void)
{
    pthread_mutex_lock(&pool.mutex);
    pool.shutdown = 1;
    pthread_cond_broadcast(&pool.not_empty);
    pthread_mutex_unlock(&pool.mutex);
    
    // 等待所有线程结束
    for (int i = 0; i < THREAD_POOL_SIZE; i++) {
        pthread_join(pool.threads[i], NULL);
    }
    
    pthread_mutex_destroy(&pool.mutex);
    pthread_cond_destroy(&pool.not_empty);
    pthread_cond_destroy(&pool.not_full);
}

// 示例任务函数
void task_function(void *arg)
{
    int task_id = *(int *)arg;
    printf("Task %d: Processing...\n", task_id);
    sleep(1);
    printf("Task %d: Done\n", task_id);
    free(arg);
}

int main(void)
{
    // 初始化线程池
    threadpool_init();
    
    // 添加任务
    for (int i = 0; i < 10; i++) {
        int *task_id = malloc(sizeof(int));
        *task_id = i;
        threadpool_add_task(task_function, task_id);
    }
    
    // 等待任务完成
    sleep(5);
    
    // 销毁线程池
    threadpool_destroy();
    
    printf("All tasks completed\n");
    
    return 0;
}
```

## 常见问题和解决方案

### 问题1：僵尸进程

**现象**：子进程结束后，父进程未调用wait()，导致子进程成为僵尸进程。

**解决方法**：

```c
#include <signal.h>
#include <sys/wait.h>

// 信号处理函数
void sigchld_handler(int sig)
{
    // 回收所有已结束的子进程
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

int main(void)
{
    // 注册SIGCHLD信号处理函数
    signal(SIGCHLD, sigchld_handler);
    
    // 创建子进程
    if (fork() == 0) {
        // 子进程
        exit(0);
    }
    
    // 父进程继续运行
    while (1) {
        sleep(1);
    }
    
    return 0;
}
```

### 问题2：线程安全

**现象**：多个线程访问共享资源导致数据不一致。

**解决方法**：

```c
// 使用线程局部存储
__thread int thread_local_var = 0;

// 或使用pthread_key
pthread_key_t key;

void destructor(void *value)
{
    free(value);
}

void init_thread_specific(void)
{
    pthread_key_create(&key, destructor);
}

void set_thread_specific(int value)
{
    int *ptr = malloc(sizeof(int));
    *ptr = value;
    pthread_setspecific(key, ptr);
}

int get_thread_specific(void)
{
    int *ptr = pthread_getspecific(key);
    return ptr ? *ptr : 0;
}
```

### 问题3：优先级反转

**现象**：高优先级线程等待低优先级线程释放锁。

**解决方法**：

```c
// 使用优先级继承互斥锁
pthread_mutexattr_t attr;
pthread_mutex_t mutex;

pthread_mutexattr_init(&attr);
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
pthread_mutex_init(&mutex, &attr);
```

## 总结

本教程介绍了Linux进程和线程编程的核心概念和实践技巧：

**进程编程**：
- 使用fork()创建进程
- 使用wait()等待子进程
- 使用exec系列函数执行新程序

**线程编程**：
- 使用pthread创建和管理线程
- 使用互斥锁保护共享资源
- 使用条件变量实现线程同步

**进程间通信**：
- 管道和命名管道
- 共享内存
- 消息队列
- 信号量

**调试和优化**：
- 使用GDB调试多线程程序
- 避免死锁和竞态条件
- 使用线程池提高性能

## 延伸阅读

**推荐书籍**：
- 《Unix环境高级编程》(APUE)
- 《Linux系统编程》
- 《POSIX多线程程序设计》

**在线资源**：
- [Linux man pages](https://man7.org/linux/man-pages/)
- [POSIX Threads Programming](https://computing.llnl.gov/tutorials/pthreads/)
- [The Linux Programming Interface](http://man7.org/tlpi/)

**相关主题**：
- 信号处理
- 网络编程(Socket)
- 异步I/O
- 实时调度

## 练习题

1. **基础练习**：
   - 编写程序创建5个子进程，每个子进程打印自己的PID
   - 实现一个简单的命令行解释器
   - 使用管道实现两个进程间的双向通信

2. **进阶练习**：
   - 实现一个多线程的文件搜索工具
   - 使用共享内存实现进程间的大数据传输
   - 实现一个生产者-消费者模型，支持多个生产者和消费者

3. **项目练习**：
   - 实现一个多线程的Web服务器
   - 开发一个多进程的任务调度系统
   - 创建一个实时数据采集和分析系统

---

**文档版本**: 1.0  
**最后更新**: 2024-01-15  
**作者**: 嵌入式知识平台

