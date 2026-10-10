---
title: "RT-Thread线程管理：掌握多任务编程核心技术"
description: "深入学习RT-Thread线程管理，包括动态/静态线程创建、线程调度、线程同步、线程状态管理等核心概念，通过实战案例掌握多任务编程"
slug: "rtthread-thread-management"

# 分类信息
domain: "操作系统层"
module: "RT-Thread"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - RT-Thread线程
  - 线程管理
  - 多任务编程
  - 线程调度
  - 线程同步
prerequisites:
  - "03-operating-system-layer/04-rt-thread/beginner/01-rtthread-quickstart"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management"
related_contents:
  - "03-operating-system-layer/04-rt-thread/intermediate/01-rtthread-device-framework"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling"

# 学习信息
estimated_time: 70
difficulty_score: 2

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
  - RT-Thread线程
  - 线程创建
  - 线程调度
  - 多任务编程
  - RTOS线程管理
cover_image: ""
---

# RT-Thread线程管理：掌握多任务编程核心技术

## 学习目标

完成本教程后，你将能够：

- [ ] 理解RT-Thread线程的基本概念和特点
- [ ] 掌握动态线程和静态线程的创建方法
- [ ] 理解线程的状态转换和生命周期
- [ ] 掌握线程的优先级和调度机制
- [ ] 学会线程的挂起、恢复和删除操作
- [ ] 理解线程栈的作用和配置方法
- [ ] 掌握线程间的同步和通信基础

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 完成RT-Thread快速入门教程
- 了解RTOS任务管理的基本概念
- 熟悉C语言指针和结构体
- 理解函数指针的使用

**技能要求**：
- 能够使用ENV工具配置RT-Thread
- 会编译和下载RT-Thread程序
- 能够使用FinSH shell调试
- 了解基本的调试方法

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| STM32开发板 | 1 | STM32F4系列推荐 | - |
| ST-Link调试器 | 1 | 用于程序下载和调试 | - |
| USB数据线 | 1 | 连接开发板 | - |
| LED灯 | 2-3个 | 用于演示（可选） | - |

### 软件准备

- **开发环境**：Keil MDK v5.30+ 或 RT-Thread Studio
- **RT-Thread版本**：v4.1.0+
- **ENV工具**：v1.3+
- **串口工具**：用于查看输出

### 环境配置

确保已完成RT-Thread快速入门教程中的环境配置：
- ENV工具已安装并配置
- RT-Thread BSP已准备就绪
- 开发板能够正常运行RT-Thread

## RT-Thread线程基础概念

### 什么是线程？

在RT-Thread中，线程是系统调度的最小单位，每个线程都有：


- **独立的栈空间**：用于保存局部变量和函数调用
- **线程控制块（TCB）**：保存线程的状态信息
- **优先级**：决定线程的调度顺序
- **入口函数**：线程的执行代码

**线程 vs 进程**：
- 线程是轻量级的执行单元
- 线程共享系统资源（内存、设备等）
- 线程切换开销小，适合嵌入式系统

### 线程的特点

RT-Thread的线程具有以下特点：

1. **支持256个优先级**
   - 0-255，数字越小优先级越高
   - 0为最高优先级，255为最低优先级

2. **支持相同优先级的时间片轮转**
   - 同优先级线程按时间片轮流执行
   - 时间片大小可配置

3. **支持动态和静态创建**
   - 动态创建：从堆中分配内存
   - 静态创建：使用预定义的内存

4. **完善的线程管理**
   - 创建、删除、挂起、恢复
   - 延时、让出CPU等操作

### 线程状态

RT-Thread线程有5种状态：

```
┌─────────┐
│  初始化  │ (RT_THREAD_INIT)
└────┬────┘
     │ rt_thread_startup()
     ↓
┌─────────┐
│  就绪   │ (RT_THREAD_READY)
└────┬────┘
     │ 调度器选中
     ↓
┌─────────┐  ←──────────────┐
│  运行   │ (RT_THREAD_RUNNING) │
└────┬────┘                  │
     │                       │
     ├→ 延时/等待 → 挂起     │
     ├→ 主动让出 → 就绪     │
     └→ 删除 → 关闭         │
                            │
┌─────────┐                 │
│  挂起   │ (RT_THREAD_SUSPEND)
└────┬────┘                 │
     │ 恢复/超时            │
     └──────────────────────┘
     
┌─────────┐
│  关闭   │ (RT_THREAD_CLOSE)
└─────────┘
```

**状态说明**：
- **初始化**：线程已创建但未启动
- **就绪**：等待CPU执行
- **运行**：正在CPU上执行
- **挂起**：等待事件或延时
- **关闭**：线程已删除


### 线程控制块

每个线程都有一个线程控制块（TCB），定义如下：

```c
struct rt_thread
{
    /* RT-Thread对象 */
    char        name[RT_NAME_MAX];    /* 线程名称 */
    rt_uint8_t  type;                 /* 对象类型 */
    rt_uint8_t  flags;                /* 标志位 */
    
    /* 线程状态 */
    rt_uint8_t  stat;                 /* 线程状态 */
    rt_uint8_t  current_priority;     /* 当前优先级 */
    rt_uint8_t  init_priority;        /* 初始优先级 */
    
    /* 线程栈 */
    void       *stack_addr;           /* 栈地址 */
    rt_uint32_t stack_size;           /* 栈大小 */
    void       *sp;                   /* 栈指针 */
    
    /* 线程入口 */
    void (*entry)(void *parameter);   /* 入口函数 */
    void *parameter;                  /* 入口参数 */
    
    /* 错误代码 */
    rt_err_t error;                   /* 错误码 */
    
    /* 时间片 */
    rt_uint32_t init_tick;            /* 初始时间片 */
    rt_uint32_t remaining_tick;       /* 剩余时间片 */
    
    /* 其他字段... */
};
typedef struct rt_thread *rt_thread_t;
```

**关键字段说明**：
- `name`：线程名称，用于标识和调试
- `stat`：线程当前状态
- `current_priority`：当前优先级
- `stack_addr`：栈起始地址
- `stack_size`：栈大小（字节）
- `entry`：线程入口函数
- `init_tick`：时间片大小

## 步骤1：动态创建线程

### 1.1 动态创建API

动态创建线程使用 `rt_thread_create()` 函数：

```c
rt_thread_t rt_thread_create(const char *name,
                             void (*entry)(void *parameter),
                             void       *parameter,
                             rt_uint32_t stack_size,
                             rt_uint8_t  priority,
                             rt_uint32_t tick);
```

**参数说明**：
- `name`：线程名称，最长RT_NAME_MAX字符
- `entry`：线程入口函数
- `parameter`：传递给入口函数的参数
- `stack_size`：栈大小（字节）
- `priority`：优先级（0-255）
- `tick`：时间片大小

**返回值**：
- 成功：返回线程句柄
- 失败：返回RT_NULL


### 1.2 创建简单线程

创建一个简单的LED闪烁线程：

```c
#include <rtthread.h>
#include <rtdevice.h>
#include <board.h>

#define LED_PIN    GET_PIN(F, 9)

/* 线程句柄 */
static rt_thread_t led_thread = RT_NULL;

/* LED线程入口函数 */
static void led_thread_entry(void *parameter)
{
    /* 配置LED引脚 */
    rt_pin_mode(LED_PIN, PIN_MODE_OUTPUT);
    
    while (1)
    {
        /* LED翻转 */
        rt_pin_write(LED_PIN, PIN_HIGH);
        rt_thread_mdelay(500);
        
        rt_pin_write(LED_PIN, PIN_LOW);
        rt_thread_mdelay(500);
    }
}

/* 创建LED线程 */
int led_thread_init(void)
{
    /* 创建线程 */
    led_thread = rt_thread_create("led",           /* 线程名称 */
                                  led_thread_entry, /* 入口函数 */
                                  RT_NULL,          /* 参数 */
                                  512,              /* 栈大小 */
                                  25,               /* 优先级 */
                                  10);              /* 时间片 */
    
    /* 检查创建结果 */
    if (led_thread != RT_NULL)
    {
        /* 启动线程 */
        rt_thread_startup(led_thread);
        rt_kprintf("LED thread created successfully\n");
    }
    else
    {
        rt_kprintf("LED thread create failed\n");
        return -RT_ERROR;
    }
    
    return RT_EOK;
}

/* 导出到msh命令 */
MSH_CMD_EXPORT(led_thread_init, create led thread);
```

**代码说明**：
1. 定义线程句柄 `led_thread`
2. 实现线程入口函数 `led_thread_entry()`
3. 使用 `rt_thread_create()` 创建线程
4. 使用 `rt_thread_startup()` 启动线程
5. 导出为msh命令，方便测试


### 1.3 带参数的线程

创建带参数的线程：

```c
/* 线程参数结构体 */
struct thread_param
{
    rt_uint32_t led_pin;
    rt_uint32_t delay_ms;
};

/* 带参数的LED线程 */
static void led_param_thread_entry(void *parameter)
{
    struct thread_param *param = (struct thread_param *)parameter;
    
    /* 配置LED引脚 */
    rt_pin_mode(param->led_pin, PIN_MODE_OUTPUT);
    
    while (1)
    {
        rt_pin_write(param->led_pin, PIN_HIGH);
        rt_thread_mdelay(param->delay_ms);
        
        rt_pin_write(param->led_pin, PIN_LOW);
        rt_thread_mdelay(param->delay_ms);
    }
}

/* 创建带参数的线程 */
int led_param_thread_init(void)
{
    static struct thread_param param;
    rt_thread_t thread;
    
    /* 设置参数 */
    param.led_pin = GET_PIN(F, 10);
    param.delay_ms = 1000;
    
    /* 创建线程，传递参数 */
    thread = rt_thread_create("led_param",
                              led_param_thread_entry,
                              &param,        /* 传递参数指针 */
                              512,
                              25,
                              10);
    
    if (thread != RT_NULL)
    {
        rt_thread_startup(thread);
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(led_param_thread_init, create led thread with parameter);
```

**注意事项**：
- 参数必须在线程生命周期内有效
- 使用static或动态分配的内存
- 避免使用局部变量作为参数

### 1.4 删除动态线程

删除不再需要的线程：

```c
/* 删除线程 */
rt_err_t rt_thread_delete(rt_thread_t thread);
```

**示例**：

```c
/* 删除LED线程 */
int led_thread_delete(void)
{
    if (led_thread != RT_NULL)
    {
        rt_thread_delete(led_thread);
        led_thread = RT_NULL;
        rt_kprintf("LED thread deleted\n");
        return RT_EOK;
    }
    
    rt_kprintf("LED thread not exist\n");
    return -RT_ERROR;
}
MSH_CMD_EXPORT(led_thread_delete, delete led thread);
```

**注意事项**：
- 只能删除动态创建的线程
- 删除后线程句柄无效
- 系统会自动回收线程资源


## 步骤2：静态创建线程

### 2.1 静态创建API

静态创建线程使用 `rt_thread_init()` 函数：

```c
rt_err_t rt_thread_init(struct rt_thread *thread,
                       const char       *name,
                       void (*entry)(void *parameter),
                       void             *parameter,
                       void             *stack_start,
                       rt_uint32_t       stack_size,
                       rt_uint8_t        priority,
                       rt_uint32_t       tick);
```

**参数说明**：
- `thread`：线程控制块指针
- `name`：线程名称
- `entry`：入口函数
- `parameter`：参数
- `stack_start`：栈起始地址
- `stack_size`：栈大小
- `priority`：优先级
- `tick`：时间片

**返回值**：
- RT_EOK：成功
- -RT_ERROR：失败

### 2.2 创建静态线程

```c
/* 定义线程控制块 */
static struct rt_thread static_thread;

/* 定义线程栈 */
ALIGN(RT_ALIGN_SIZE)
static rt_uint8_t static_thread_stack[1024];

/* 静态线程入口函数 */
static void static_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Static thread count: %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

/* 初始化静态线程 */
int static_thread_init(void)
{
    rt_err_t result;
    
    /* 初始化线程 */
    result = rt_thread_init(&static_thread,
                           "static",
                           static_thread_entry,
                           RT_NULL,
                           &static_thread_stack[0],
                           sizeof(static_thread_stack),
                           20,
                           10);
    
    if (result == RT_EOK)
    {
        /* 启动线程 */
        rt_thread_startup(&static_thread);
        rt_kprintf("Static thread initialized\n");
    }
    else
    {
        rt_kprintf("Static thread init failed\n");
    }
    
    return result;
}
MSH_CMD_EXPORT(static_thread_init, init static thread);
```

**代码说明**：
1. 定义线程控制块（全局或静态变量）
2. 定义线程栈（使用ALIGN宏对齐）
3. 使用 `rt_thread_init()` 初始化线程
4. 使用 `rt_thread_startup()` 启动线程


### 2.3 脱离静态线程

静态线程使用 `rt_thread_detach()` 脱离：

```c
/* 脱离线程 */
rt_err_t rt_thread_detach(rt_thread_t thread);
```

**示例**：

```c
/* 脱离静态线程 */
int static_thread_detach(void)
{
    rt_err_t result;
    
    result = rt_thread_detach(&static_thread);
    
    if (result == RT_EOK)
    {
        rt_kprintf("Static thread detached\n");
    }
    else
    {
        rt_kprintf("Static thread detach failed\n");
    }
    
    return result;
}
MSH_CMD_EXPORT(static_thread_detach, detach static thread);
```

**注意事项**：
- 只能脱离静态创建的线程
- 脱离后线程控制块和栈仍然存在
- 可以重新初始化使用

### 2.4 动态 vs 静态

| 特性 | 动态创建 | 静态创建 |
|------|----------|----------|
| 内存分配 | 从堆中分配 | 使用预定义内存 |
| 创建函数 | rt_thread_create() | rt_thread_init() |
| 删除函数 | rt_thread_delete() | rt_thread_detach() |
| 内存回收 | 自动回收 | 不回收 |
| 使用场景 | 临时任务 | 长期运行任务 |
| 内存碎片 | 可能产生 | 不产生 |

**选择建议**：
- 系统初始化时创建的线程 → 静态创建
- 运行时动态创建的线程 → 动态创建
- 内存受限的系统 → 静态创建
- 需要频繁创建删除 → 动态创建

## 步骤3：线程调度和优先级

### 3.1 优先级设置

RT-Thread支持256个优先级（0-255）：

```c
/* 优先级范围 */
#define RT_THREAD_PRIORITY_MAX    256

/* 常用优先级定义 */
#define THREAD_PRIORITY_HIGH      10
#define THREAD_PRIORITY_NORMAL    20
#define THREAD_PRIORITY_LOW       30
```

**优先级分配原则**：
- 0-7：系统保留（不建议使用）
- 8-31：高优先级任务（实时性要求高）
- 32-127：普通任务
- 128-255：低优先级任务（后台任务）


### 3.2 优先级调度示例

创建不同优先级的线程：

```c
/* 高优先级线程 */
static void high_priority_thread(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("[HIGH] count: %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

/* 低优先级线程 */
static void low_priority_thread(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("[LOW] count: %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

/* 创建优先级测试线程 */
int priority_test(void)
{
    rt_thread_t thread1, thread2;
    
    /* 创建高优先级线程 */
    thread1 = rt_thread_create("high",
                               high_priority_thread,
                               RT_NULL,
                               512,
                               10,    /* 高优先级 */
                               10);
    
    /* 创建低优先级线程 */
    thread2 = rt_thread_create("low",
                               low_priority_thread,
                               RT_NULL,
                               512,
                               30,    /* 低优先级 */
                               10);
    
    if (thread1 != RT_NULL)
        rt_thread_startup(thread1);
    
    if (thread2 != RT_NULL)
        rt_thread_startup(thread2);
    
    return RT_EOK;
}
MSH_CMD_EXPORT(priority_test, test thread priority);
```

**观察结果**：
- 高优先级线程优先执行
- 低优先级线程在高优先级线程延时时执行
- 体现抢占式调度特性

### 3.3 时间片轮转

相同优先级的线程按时间片轮转：

```c
/* 线程1 */
static void thread1_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Thread1: %d\n", count++);
        /* 不延时，持续运行 */
    }
}

/* 线程2 */
static void thread2_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Thread2: %d\n", count++);
        /* 不延时，持续运行 */
    }
}

/* 时间片测试 */
int timeslice_test(void)
{
    rt_thread_t thread1, thread2;
    
    /* 创建相同优先级的线程 */
    thread1 = rt_thread_create("t1",
                               thread1_entry,
                               RT_NULL,
                               512,
                               25,    /* 相同优先级 */
                               5);    /* 时间片：5个tick */
    
    thread2 = rt_thread_create("t2",
                               thread2_entry,
                               RT_NULL,
                               512,
                               25,    /* 相同优先级 */
                               10);   /* 时间片：10个tick */
    
    if (thread1 != RT_NULL)
        rt_thread_startup(thread1);
    
    if (thread2 != RT_NULL)
        rt_thread_startup(thread2);
    
    return RT_EOK;
}
MSH_CMD_EXPORT(timeslice_test, test time slice);
```

**观察结果**：
- 两个线程交替执行
- thread2的执行时间是thread1的2倍
- 体现时间片轮转调度


## 步骤4：线程控制操作

### 4.1 线程延时

RT-Thread提供两种延时方式：

```c
/* 延时指定tick数 */
rt_err_t rt_thread_delay(rt_tick_t tick);

/* 延时指定毫秒数 */
rt_err_t rt_thread_mdelay(rt_int32_t ms);
```

**示例**：

```c
static void delay_thread_entry(void *parameter)
{
    while (1)
    {
        rt_kprintf("Delay 1000ms\n");
        rt_thread_mdelay(1000);    /* 延时1秒 */
        
        rt_kprintf("Delay 10 ticks\n");
        rt_thread_delay(10);       /* 延时10个tick */
    }
}
```

**注意事项**：
- `rt_thread_delay()` 以tick为单位
- `rt_thread_mdelay()` 以毫秒为单位
- 延时期间线程进入挂起状态
- 其他线程可以运行

### 4.2 线程让出CPU

主动让出CPU给其他线程：

```c
/* 让出CPU */
rt_err_t rt_thread_yield(void);
```

**示例**：

```c
static void yield_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Count: %d\n", count++);
        
        /* 主动让出CPU */
        rt_thread_yield();
        
        /* 让同优先级的其他线程运行 */
    }
}
```

**使用场景**：
- 同优先级线程协作
- 避免长时间占用CPU
- 提高系统响应性

### 4.3 线程挂起和恢复

手动挂起和恢复线程：

```c
/* 挂起线程 */
rt_err_t rt_thread_suspend(rt_thread_t thread);

/* 恢复线程 */
rt_err_t rt_thread_resume(rt_thread_t thread);
```

**示例**：

```c
static rt_thread_t test_thread = RT_NULL;

/* 测试线程 */
static void test_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Running: %d\n", count++);
        rt_thread_mdelay(500);
    }
}

/* 创建测试线程 */
int suspend_test_init(void)
{
    test_thread = rt_thread_create("test",
                                   test_thread_entry,
                                   RT_NULL,
                                   512,
                                   25,
                                   10);
    
    if (test_thread != RT_NULL)
    {
        rt_thread_startup(test_thread);
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(suspend_test_init, create suspend test thread);

/* 挂起线程 */
int suspend_thread(void)
{
    if (test_thread != RT_NULL)
    {
        rt_thread_suspend(test_thread);
        rt_kprintf("Thread suspended\n");
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(suspend_thread, suspend test thread);

/* 恢复线程 */
int resume_thread(void)
{
    if (test_thread != RT_NULL)
    {
        rt_thread_resume(test_thread);
        rt_kprintf("Thread resumed\n");
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(resume_thread, resume test thread);
```

**注意事项**：
- 挂起后线程停止运行
- 必须手动恢复才能继续
- 不要在中断中挂起线程
- 避免死锁情况


## 步骤5：线程栈管理

### 5.1 栈大小配置

线程栈用于保存：
- 局部变量
- 函数调用信息
- 中断上下文

**栈大小计算**：

```c
/* 栈大小 = 局部变量 + 函数调用深度 + 中断嵌套 + 安全余量 */

/* 示例：简单线程 */
#define SIMPLE_THREAD_STACK    512    /* 512字节 */

/* 示例：复杂线程 */
#define COMPLEX_THREAD_STACK   2048   /* 2KB */

/* 示例：网络线程 */
#define NETWORK_THREAD_STACK   4096   /* 4KB */
```

**配置建议**：
- 最小栈：256字节（简单任务）
- 普通栈：512-1024字节
- 大栈：2048-4096字节（复杂任务）
- 根据实际需求调整

### 5.2 栈溢出检测

RT-Thread提供栈溢出检测功能：

**在menuconfig中启用**：

```
RT-Thread Kernel
  → Kernel Device Object
    [*] Enable thread stack overflow checking
```

**或在rtconfig.h中定义**：

```c
#define RT_USING_OVERFLOW_CHECK
```

**检测原理**：
- 在栈底部设置魔术数字
- 定期检查魔术数字是否被破坏
- 发现溢出时触发断言

### 5.3 查看栈使用情况

使用FinSH命令查看：

```bash
msh > list_thread
thread   pri  status      sp     stack size max used left tick  error
-------- ---  ------- ---------- ----------  ------  ---------- ---
led       25  suspend 0x000000a8 0x00000200    32%   0x00000005 000
test      25  ready   0x00000118 0x00000200    56%   0x00000003 000
tshell    20  ready   0x00000118 0x00001000    28%   0x00000003 000
tidle0    31  ready   0x00000070 0x00000100    43%   0x0000000a 000
```

**字段说明**：
- `stack size`：栈总大小
- `max used`：最大使用百分比
- `sp`：当前栈指针

**优化建议**：
- max used < 50%：栈过大，可以减小
- max used > 80%：栈不足，需要增大
- max used 50-80%：合适

### 5.4 栈溢出示例

演示栈溢出：

```c
/* 故意制造栈溢出 */
static void stack_overflow_thread(void *parameter)
{
    /* 定义大数组，超过栈大小 */
    char buffer[2048];  /* 栈只有512字节 */
    
    rt_kprintf("This will cause stack overflow\n");
    
    /* 使用数组 */
    for (int i = 0; i < sizeof(buffer); i++)
    {
        buffer[i] = i;
    }
    
    while (1)
    {
        rt_thread_mdelay(1000);
    }
}

/* 创建栈溢出测试线程 */
int stack_overflow_test(void)
{
    rt_thread_t thread;
    
    thread = rt_thread_create("overflow",
                              stack_overflow_thread,
                              RT_NULL,
                              512,    /* 栈太小 */
                              25,
                              10);
    
    if (thread != RT_NULL)
    {
        rt_thread_startup(thread);
    }
    
    return RT_EOK;
}
MSH_CMD_EXPORT(stack_overflow_test, test stack overflow);
```

**预期结果**：
- 系统检测到栈溢出
- 触发断言或错误提示
- 线程被终止


## 步骤6：线程同步基础

### 6.1 空闲线程钩子

空闲线程在系统空闲时运行，可以设置钩子函数：

```c
/* 设置空闲线程钩子 */
void rt_thread_idle_sethook(void (*hook)(void));

/* 删除空闲线程钩子 */
void rt_thread_idle_delhook(void (*hook)(void));
```

**示例**：

```c
/* 空闲钩子函数 */
static void idle_hook(void)
{
    /* 在空闲时执行 */
    /* 可以进入低功耗模式 */
    rt_kprintf("System idle\n");
}

/* 设置空闲钩子 */
int set_idle_hook(void)
{
    rt_thread_idle_sethook(idle_hook);
    rt_kprintf("Idle hook set\n");
    return RT_EOK;
}
MSH_CMD_EXPORT(set_idle_hook, set idle thread hook);

/* 删除空闲钩子 */
int del_idle_hook(void)
{
    rt_thread_idle_delhook(idle_hook);
    rt_kprintf("Idle hook deleted\n");
    return RT_EOK;
}
MSH_CMD_EXPORT(del_idle_hook, delete idle thread hook);
```

**使用场景**：
- 系统空闲时进入低功耗
- 统计CPU使用率
- 后台任务处理

### 6.2 调度器钩子

在线程切换时调用钩子函数：

```c
/* 设置调度器钩子 */
void rt_scheduler_sethook(void (*hook)(struct rt_thread *from, struct rt_thread *to));
```

**示例**：

```c
/* 调度器钩子函数 */
static void scheduler_hook(struct rt_thread *from, struct rt_thread *to)
{
    rt_kprintf("Switch: %s -> %s\n", from->name, to->name);
}

/* 设置调度器钩子 */
int set_scheduler_hook(void)
{
    rt_scheduler_sethook(scheduler_hook);
    rt_kprintf("Scheduler hook set\n");
    return RT_EOK;
}
MSH_CMD_EXPORT(set_scheduler_hook, set scheduler hook);
```

**注意事项**：
- 钩子函数要尽量简短
- 不要在钩子中调用可能阻塞的函数
- 避免影响系统性能

### 6.3 线程查找

通过名称查找线程：

```c
/* 查找线程 */
rt_thread_t rt_thread_find(const char *name);
```

**示例**：

```c
/* 查找并操作线程 */
int find_and_suspend(const char *name)
{
    rt_thread_t thread;
    
    /* 查找线程 */
    thread = rt_thread_find(name);
    
    if (thread != RT_NULL)
    {
        /* 挂起线程 */
        rt_thread_suspend(thread);
        rt_kprintf("Thread %s suspended\n", name);
        return RT_EOK;
    }
    
    rt_kprintf("Thread %s not found\n", name);
    return -RT_ERROR;
}
MSH_CMD_EXPORT(find_and_suspend, find and suspend thread);
```

**使用场景**：
- 动态控制其他线程
- 调试和监控
- 线程间协作


## 步骤7：综合实战案例

### 7.1 多线程LED控制系统

创建一个完整的多线程LED控制系统：

```c
#include <rtthread.h>
#include <rtdevice.h>
#include <board.h>

/* LED引脚定义 */
#define LED1_PIN    GET_PIN(F, 9)
#define LED2_PIN    GET_PIN(F, 10)
#define LED3_PIN    GET_PIN(E, 13)

/* 线程句柄 */
static rt_thread_t led1_thread = RT_NULL;
static rt_thread_t led2_thread = RT_NULL;
static rt_thread_t led3_thread = RT_NULL;
static rt_thread_t control_thread = RT_NULL;

/* LED控制标志 */
static rt_bool_t led1_enable = RT_TRUE;
static rt_bool_t led2_enable = RT_TRUE;
static rt_bool_t led3_enable = RT_TRUE;

/* LED1线程：快速闪烁 */
static void led1_thread_entry(void *parameter)
{
    rt_pin_mode(LED1_PIN, PIN_MODE_OUTPUT);
    
    while (1)
    {
        if (led1_enable)
        {
            rt_pin_write(LED1_PIN, PIN_HIGH);
            rt_thread_mdelay(200);
            rt_pin_write(LED1_PIN, PIN_LOW);
            rt_thread_mdelay(200);
        }
        else
        {
            rt_pin_write(LED1_PIN, PIN_LOW);
            rt_thread_mdelay(100);
        }
    }
}

/* LED2线程：中速闪烁 */
static void led2_thread_entry(void *parameter)
{
    rt_pin_mode(LED2_PIN, PIN_MODE_OUTPUT);
    
    while (1)
    {
        if (led2_enable)
        {
            rt_pin_write(LED2_PIN, PIN_HIGH);
            rt_thread_mdelay(500);
            rt_pin_write(LED2_PIN, PIN_LOW);
            rt_thread_mdelay(500);
        }
        else
        {
            rt_pin_write(LED2_PIN, PIN_LOW);
            rt_thread_mdelay(100);
        }
    }
}

/* LED3线程：慢速闪烁 */
static void led3_thread_entry(void *parameter)
{
    rt_pin_mode(LED3_PIN, PIN_MODE_OUTPUT);
    
    while (1)
    {
        if (led3_enable)
        {
            rt_pin_write(LED3_PIN, PIN_HIGH);
            rt_thread_mdelay(1000);
            rt_pin_write(LED3_PIN, PIN_LOW);
            rt_thread_mdelay(1000);
        }
        else
        {
            rt_pin_write(LED3_PIN, PIN_LOW);
            rt_thread_mdelay(100);
        }
    }
}

/* 控制线程：定期切换LED状态 */
static void control_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        count++;
        
        /* 每5秒切换一次LED状态 */
        if (count % 5 == 0)
        {
            led1_enable = !led1_enable;
            rt_kprintf("LED1: %s\n", led1_enable ? "ON" : "OFF");
        }
        
        if (count % 7 == 0)
        {
            led2_enable = !led2_enable;
            rt_kprintf("LED2: %s\n", led2_enable ? "ON" : "OFF");
        }
        
        if (count % 10 == 0)
        {
            led3_enable = !led3_enable;
            rt_kprintf("LED3: %s\n", led3_enable ? "ON" : "OFF");
        }
        
        rt_thread_mdelay(1000);
    }
}

/* 初始化LED系统 */
int led_system_init(void)
{
    /* 创建LED1线程 */
    led1_thread = rt_thread_create("led1",
                                   led1_thread_entry,
                                   RT_NULL,
                                   512,
                                   25,
                                   10);
    
    /* 创建LED2线程 */
    led2_thread = rt_thread_create("led2",
                                   led2_thread_entry,
                                   RT_NULL,
                                   512,
                                   25,
                                   10);
    
    /* 创建LED3线程 */
    led3_thread = rt_thread_create("led3",
                                   led3_thread_entry,
                                   RT_NULL,
                                   512,
                                   25,
                                   10);
    
    /* 创建控制线程 */
    control_thread = rt_thread_create("control",
                                      control_thread_entry,
                                      RT_NULL,
                                      512,
                                      20,
                                      10);
    
    /* 启动所有线程 */
    if (led1_thread != RT_NULL)
        rt_thread_startup(led1_thread);
    
    if (led2_thread != RT_NULL)
        rt_thread_startup(led2_thread);
    
    if (led3_thread != RT_NULL)
        rt_thread_startup(led3_thread);
    
    if (control_thread != RT_NULL)
        rt_thread_startup(control_thread);
    
    rt_kprintf("LED system initialized\n");
    
    return RT_EOK;
}
MSH_CMD_EXPORT(led_system_init, initialize LED control system);
```

**系统特点**：
- 4个线程协同工作
- 独立控制3个LED
- 动态调整LED状态
- 展示多线程协作


### 7.2 测试和验证

**编译和下载**：

1. 编译工程
2. 下载到开发板
3. 打开串口终端

**运行测试**：

```bash
# 初始化LED系统
msh > led_system_init
LED system initialized

# 查看线程状态
msh > list_thread
thread   pri  status      sp     stack size max used left tick  error
-------- ---  ------- ---------- ----------  ------  ---------- ---
control   20  suspend 0x000000a8 0x00000200    32%   0x00000005 000
led3      25  suspend 0x000000a8 0x00000200    32%   0x00000005 000
led2      25  suspend 0x000000a8 0x00000200    32%   0x00000005 000
led1      25  suspend 0x000000a8 0x00000200    32%   0x00000005 000
tshell    20  ready   0x00000118 0x00001000    28%   0x00000003 000
tidle0    31  ready   0x00000070 0x00000100    43%   0x0000000a 000
```

**观察现象**：
- LED1快速闪烁（200ms）
- LED2中速闪烁（500ms）
- LED3慢速闪烁（1000ms）
- 定期自动切换LED状态

## 故障排除

### 问题1：线程创建失败

**现象**：
- `rt_thread_create()` 返回NULL
- 线程无法启动

**可能原因**：
- 堆内存不足
- 栈大小设置过大
- 系统资源耗尽

**解决方法**：

1. **增加堆大小**：

在rtconfig.h中：
```c
#define RT_HEAP_SIZE    (1024*16)  /* 增加到16KB */
```

2. **减小栈大小**：
```c
/* 从2048减小到512 */
thread = rt_thread_create("test",
                          entry,
                          RT_NULL,
                          512,    /* 减小栈 */
                          25,
                          10);
```

3. **使用静态创建**：
```c
/* 改用静态创建 */
static struct rt_thread thread;
static rt_uint8_t thread_stack[512];

rt_thread_init(&thread, "test", entry, RT_NULL,
               thread_stack, sizeof(thread_stack),
               25, 10);
```

### 问题2：栈溢出

**现象**：
- 系统崩溃或重启
- 出现断言错误
- 线程行为异常

**可能原因**：
- 栈大小不足
- 局部变量过大
- 函数调用层次太深
- 递归调用

**解决方法**：

1. **增加栈大小**：
```c
/* 从512增加到1024 */
thread = rt_thread_create("test",
                          entry,
                          RT_NULL,
                          1024,   /* 增加栈 */
                          25,
                          10);
```

2. **减少局部变量**：
```c
/* 错误：局部变量过大 */
void thread_entry(void *parameter)
{
    char buffer[2048];  /* 太大 */
    // ...
}

/* 正确：使用动态分配或全局变量 */
static char buffer[2048];  /* 全局变量 */

void thread_entry(void *parameter)
{
    char *buffer = rt_malloc(2048);  /* 动态分配 */
    // ...
    rt_free(buffer);
}
```

3. **启用栈检测**：
```c
#define RT_USING_OVERFLOW_CHECK
```


### 问题3：线程无法运行

**现象**：
- 线程创建成功但不执行
- 串口无输出

**可能原因**：
- 忘记调用 `rt_thread_startup()`
- 线程优先级设置不当
- 线程被挂起

**解决方法**：

1. **确保启动线程**：
```c
thread = rt_thread_create(...);
if (thread != RT_NULL)
{
    rt_thread_startup(thread);  /* 必须调用 */
}
```

2. **检查优先级**：
```c
/* 确保优先级合理 */
thread = rt_thread_create("test",
                          entry,
                          RT_NULL,
                          512,
                          25,    /* 不要太低 */
                          10);
```

3. **检查线程状态**：
```bash
msh > list_thread
# 查看线程是否在运行
```

### 问题4：线程切换异常

**现象**：
- 系统卡死
- 线程无法切换
- 调度异常

**可能原因**：
- 在中断中调用了阻塞函数
- 关闭了中断太长时间
- 调度器被锁定

**解决方法**：

1. **避免在中断中阻塞**：
```c
/* 错误：在中断中延时 */
void interrupt_handler(void)
{
    rt_thread_mdelay(100);  /* 错误！ */
}

/* 正确：使用信号量通知 */
void interrupt_handler(void)
{
    rt_sem_release(sem);  /* 正确 */
}
```

2. **检查调度器状态**：
```c
/* 确保调度器未被锁定 */
rt_enter_critical();  /* 进入临界区 */
// 临界区代码要尽量短
rt_exit_critical();   /* 退出临界区 */
```

## 总结

通过本教程，你学习了：

- ✅ RT-Thread线程的基本概念和特点
- ✅ 动态和静态线程的创建方法
- ✅ 线程的状态转换和生命周期
- ✅ 线程优先级和调度机制
- ✅ 线程的控制操作（延时、挂起、恢复）
- ✅ 线程栈的管理和优化
- ✅ 多线程协作的实战案例

### 关键要点

1. **线程创建方式**
   - 动态创建：灵活，适合临时任务
   - 静态创建：高效，适合长期任务

2. **优先级管理**
   - 256个优先级，数字越小优先级越高
   - 合理分配优先级避免饥饿
   - 相同优先级按时间片轮转

3. **栈管理**
   - 根据需求合理配置栈大小
   - 启用栈溢出检测
   - 定期检查栈使用情况

4. **线程控制**
   - 使用延时避免空转
   - 适时让出CPU
   - 谨慎使用挂起和恢复

## 进阶挑战

尝试以下挑战来巩固学习：

### 挑战1：优先级反转演示

创建3个线程，演示优先级反转问题：
- 高优先级线程等待低优先级线程释放资源
- 中优先级线程抢占低优先级线程
- 导致高优先级线程长时间等待

**提示**：使用互斥量和不同优先级的线程

### 挑战2：CPU使用率统计

实现一个CPU使用率统计功能：
- 统计每个线程的运行时间
- 计算CPU总使用率
- 定期输出统计信息

**提示**：使用空闲线程钩子和调度器钩子

### 挑战3：线程池实现

实现一个简单的线程池：
- 预创建多个工作线程
- 通过队列分配任务
- 动态调整线程数量

**提示**：使用消息队列和线程管理API


## 完整代码示例

### main.c 完整代码

```c
/*
 * Copyright (c) 2006-2024, RT-Thread Development Team
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <rtthread.h>
#include <rtdevice.h>
#include <board.h>

/* LED引脚定义 */
#define LED1_PIN    GET_PIN(F, 9)
#define LED2_PIN    GET_PIN(F, 10)

/* ========== 示例1：动态创建线程 ========== */

static rt_thread_t dynamic_thread = RT_NULL;

static void dynamic_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Dynamic thread: %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

int dynamic_thread_create(void)
{
    dynamic_thread = rt_thread_create("dynamic",
                                      dynamic_thread_entry,
                                      RT_NULL,
                                      512,
                                      25,
                                      10);
    
    if (dynamic_thread != RT_NULL)
    {
        rt_thread_startup(dynamic_thread);
        rt_kprintf("Dynamic thread created\n");
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(dynamic_thread_create, create dynamic thread);

/* ========== 示例2：静态创建线程 ========== */

static struct rt_thread static_thread;
ALIGN(RT_ALIGN_SIZE)
static rt_uint8_t static_thread_stack[1024];

static void static_thread_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Static thread: %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

int static_thread_init(void)
{
    rt_err_t result;
    
    result = rt_thread_init(&static_thread,
                           "static",
                           static_thread_entry,
                           RT_NULL,
                           &static_thread_stack[0],
                           sizeof(static_thread_stack),
                           20,
                           10);
    
    if (result == RT_EOK)
    {
        rt_thread_startup(&static_thread);
        rt_kprintf("Static thread initialized\n");
    }
    
    return result;
}
MSH_CMD_EXPORT(static_thread_init, init static thread);

/* ========== 示例3：优先级测试 ========== */

static void high_priority_thread(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("[HIGH] %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

static void low_priority_thread(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("[LOW] %d\n", count++);
        rt_thread_mdelay(1000);
    }
}

int priority_test(void)
{
    rt_thread_t thread1, thread2;
    
    thread1 = rt_thread_create("high",
                               high_priority_thread,
                               RT_NULL,
                               512,
                               10,
                               10);
    
    thread2 = rt_thread_create("low",
                               low_priority_thread,
                               RT_NULL,
                               512,
                               30,
                               10);
    
    if (thread1 != RT_NULL)
        rt_thread_startup(thread1);
    
    if (thread2 != RT_NULL)
        rt_thread_startup(thread2);
    
    return RT_EOK;
}
MSH_CMD_EXPORT(priority_test, test thread priority);

/* ========== 示例4：线程控制 ========== */

static rt_thread_t control_test_thread = RT_NULL;

static void control_test_entry(void *parameter)
{
    rt_uint32_t count = 0;
    
    while (1)
    {
        rt_kprintf("Control test: %d\n", count++);
        rt_thread_mdelay(500);
    }
}

int control_test_create(void)
{
    control_test_thread = rt_thread_create("ctrl_test",
                                           control_test_entry,
                                           RT_NULL,
                                           512,
                                           25,
                                           10);
    
    if (control_test_thread != RT_NULL)
    {
        rt_thread_startup(control_test_thread);
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(control_test_create, create control test thread);

int control_test_suspend(void)
{
    if (control_test_thread != RT_NULL)
    {
        rt_thread_suspend(control_test_thread);
        rt_kprintf("Thread suspended\n");
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(control_test_suspend, suspend control test thread);

int control_test_resume(void)
{
    if (control_test_thread != RT_NULL)
    {
        rt_thread_resume(control_test_thread);
        rt_kprintf("Thread resumed\n");
        return RT_EOK;
    }
    
    return -RT_ERROR;
}
MSH_CMD_EXPORT(control_test_resume, resume control test thread);

/* ========== 主函数 ========== */

int main(void)
{
    rt_pin_mode(LED1_PIN, PIN_MODE_OUTPUT);
    
    rt_kprintf("\n");
    rt_kprintf("RT-Thread Thread Management Tutorial\n");
    rt_kprintf("=====================================\n");
    rt_kprintf("Available commands:\n");
    rt_kprintf("  dynamic_thread_create  - Create dynamic thread\n");
    rt_kprintf("  static_thread_init     - Init static thread\n");
    rt_kprintf("  priority_test          - Test thread priority\n");
    rt_kprintf("  control_test_create    - Create control test thread\n");
    rt_kprintf("  control_test_suspend   - Suspend control test thread\n");
    rt_kprintf("  control_test_resume    - Resume control test thread\n");
    rt_kprintf("  list_thread            - List all threads\n");
    rt_kprintf("\n");
    
    while (1)
    {
        rt_pin_write(LED1_PIN, PIN_HIGH);
        rt_thread_mdelay(500);
        rt_pin_write(LED1_PIN, PIN_LOW);
        rt_thread_mdelay(500);
    }
    
    return RT_EOK;
}
```

### 测试环境

**硬件环境**：
- 开发板：正点原子探索者STM32F407
- 调试器：ST-Link V2
- LED：板载LED（PF9、PF10）

**软件环境**：
- IDE：Keil MDK v5.36
- RT-Thread版本：v4.1.1
- ENV工具版本：v1.3.5


## 下一步学习

建议按以下顺序继续学习：

### 1. RT-Thread设备驱动框架
- [RT-Thread设备驱动框架](../intermediate/01-rtthread-device-framework.html)
- 学习统一的设备访问接口
- 掌握驱动开发方法

### 2. RT-Thread IPC机制
- 学习信号量、互斥量、消息队列
- 掌握线程间通信方法
- 理解同步和互斥

### 3. RT-Thread内存管理
- 学习内存分配策略
- 掌握内存池使用
- 优化内存使用

### 4. 实战项目
- [基于RT-Thread的IoT项目](../advanced/01-rtthread-iot-project.html)
- 综合运用所学知识
- 完成完整项目

## 参考资料

### 官方文档

1. **RT-Thread线程管理文档**
   - https://www.rt-thread.org/document/site/programming-manual/thread/thread/
   - 详细的API文档和使用说明

2. **RT-Thread编程指南**
   - https://www.rt-thread.org/document/site/programming-manual/
   - 完整的编程手册

3. **RT-Thread源码**
   - GitHub: https://github.com/RT-Thread/rt-thread
   - 查看线程管理实现

### 推荐阅读

1. **《RT-Thread内核实现与应用开发实战》**
   - 第3章：线程管理
   - 深入讲解线程原理

2. **《嵌入式实时操作系统RT-Thread设计与实现》**
   - 第4章：任务调度
   - 详细的调度算法分析

### 在线资源

1. **RT-Thread社区论坛**
   - https://club.rt-thread.org/
   - 线程管理相关讨论

2. **RT-Thread问答社区**
   - https://www.rt-thread.org/qa/
   - 技术问题解答

## 常见问题解答

### Q1: 动态创建和静态创建如何选择？

**A**: 选择依据：

**动态创建**适用于：
- 运行时创建的临时任务
- 任务数量不确定
- 内存充足的系统

**静态创建**适用于：
- 系统初始化时创建的任务
- 长期运行的任务
- 内存受限的系统
- 需要避免内存碎片

**建议**：
- 核心任务使用静态创建
- 临时任务使用动态创建
- 根据实际需求灵活选择

### Q2: 如何确定合适的栈大小？

**A**: 确定方法：

1. **初始估算**：
   - 简单任务：512字节
   - 普通任务：1024字节
   - 复杂任务：2048字节

2. **实际测试**：
```bash
msh > list_thread
# 查看max used列
# 如果>80%，需要增大
# 如果<50%，可以减小
```

3. **计算方法**：
```
栈大小 = 局部变量 + 函数调用 + 中断嵌套 + 安全余量(20%)
```

4. **启用检测**：
```c
#define RT_USING_OVERFLOW_CHECK
```

### Q3: 线程优先级如何分配？

**A**: 分配原则：

**优先级范围**：
- 0-7：系统保留
- 8-15：高优先级（实时任务）
- 16-31：中高优先级（重要任务）
- 32-127：普通优先级（一般任务）
- 128-255：低优先级（后台任务）

**分配建议**：
- 中断处理线程：10-15
- 通信任务：16-20
- 控制任务：21-25
- 显示任务：26-30
- 后台任务：100+

**注意事项**：
- 避免过多相同优先级
- 预留优先级空间
- 定期review优先级分配

### Q4: 如何避免线程饥饿？

**A**: 避免方法：

1. **合理分配优先级**：
   - 不要让低优先级任务永远得不到执行
   - 使用优先级继承机制

2. **使用时间片轮转**：
```c
/* 相同优先级的线程会轮流执行 */
thread1 = rt_thread_create("t1", entry1, NULL, 512, 25, 10);
thread2 = rt_thread_create("t2", entry2, NULL, 512, 25, 10);
```

3. **主动让出CPU**：
```c
void high_priority_thread(void *parameter)
{
    while (1)
    {
        // 处理任务
        
        /* 主动让出CPU */
        rt_thread_yield();
    }
}
```

4. **使用延时**：
```c
/* 高优先级任务也要适当延时 */
rt_thread_mdelay(10);
```

### Q5: 线程删除后资源会自动回收吗？

**A**: 资源回收说明：

**动态创建的线程**：
```c
rt_thread_delete(thread);
/* 会自动回收：
 * - 线程控制块
 * - 线程栈
 * - 其他系统资源
 */
```

**静态创建的线程**：
```c
rt_thread_detach(&thread);
/* 不会回收：
 * - 线程控制块仍存在
 * - 栈空间仍存在
 * - 可以重新初始化
 */
```

**注意事项**：
- 线程自己分配的资源需要手动释放
- 如动态分配的内存、打开的文件等
- 建议在线程退出前清理资源

---

**反馈与支持**：

如果你在学习过程中遇到问题：
- 💬 在评论区留言讨论
- 🌐 访问RT-Thread社区论坛
- 📧 发送邮件到：support@embedded-platform.com
- 🐛 报告问题：[GitHub Issues](https://github.com/RT-Thread/rt-thread/issues)

**贡献代码**：
欢迎提交改进建议和示例代码！

---

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**最后更新**：2024-01-15  
**文档版本**：1.0
