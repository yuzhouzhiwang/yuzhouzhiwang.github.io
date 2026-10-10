---
title: "协作式多任务调度器实现：从零构建轻量级任务管理系统"
description: "深入学习协作式调度器的设计与实现，掌握任务切换、上下文保存、调度算法等核心技术。通过完整的代码实现，理解RTOS的基本原理，为学习抢占式调度和复杂操作系统打下坚实基础。本教程包含完整的可运行代码和详细的实现步骤。"
slug: "cooperative-scheduler-implementation"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 协作式调度
  - 多任务
  - 调度器
  - 任务切换
  - 上下文保存
  - RTOS原理
prerequisites:
  - "beginner/01-bare-metal-basics.md"
  - "beginner/02-super-loop.md"
  - "beginner/03-state-machine.md"
related_contents:
  - "beginner/04-time-slice-scheduling.md"
  - "advanced/01-lightweight-scheduler.md"

# 学习信息
estimated_time: 90
difficulty_score: 6

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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - 协作式调度
  - 任务调度器
  - 多任务系统
  - 上下文切换
  - 任务管理
  - RTOS基础
cover_image: ""
---

# 协作式多任务调度器实现：从零构建轻量级任务管理系统

## 概述

协作式调度器（Cooperative Scheduler）是介于简单超级循环和复杂RTOS之间的一种任务管理方案。它允许多个任务"看似"并发执行，但任务切换由任务自己主动发起，而不是被强制中断。

完成本教程后，你将能够：

- 理解协作式调度的核心原理和工作机制
- 掌握任务上下文保存和恢复的实现方法
- 实现一个完整的协作式调度器
- 理解协作式调度与抢占式调度的区别
- 为学习RTOS打下坚实的理论和实践基础

## 背景知识

### 什么是协作式调度？

**协作式调度**（Cooperative Scheduling）是一种多任务调度方式，其中：
- 任务主动让出CPU控制权（yield）
- 调度器在任务让出时进行任务切换
- 任务执行期间不会被强制中断
- 任务之间需要"协作"才能实现多任务

**类比理解**：
- **协作式调度**：像是一群人轮流使用一台电脑，每个人用完后主动让给下一个人
- **抢占式调度**：像是有个管理员，到时间就强制切换使用者

### 核心概念

**任务（Task）**：一个独立的执行单元，有自己的代码和数据。

**上下文（Context）**：任务的执行状态，包括寄存器值、栈指针等。

**调度（Scheduling）**：决定下一个运行哪个任务的过程。

**让出（Yield）**：任务主动放弃CPU，让调度器选择下一个任务。


**任务状态**：
- **就绪（Ready）**：任务准备好运行，等待调度
- **运行（Running）**：任务正在执行
- **阻塞（Blocked）**：任务等待某个事件（在协作式调度中较少使用）

### 协作式 vs 抢占式

| 特性 | 协作式调度 | 抢占式调度 |
|------|-----------|-----------|
| 任务切换 | 任务主动让出 | 定时器强制切换 |
| 实时性 | 较差，依赖任务配合 | 好，可保证响应时间 |
| 实现复杂度 | 简单 | 复杂 |
| 资源开销 | 小 | 较大 |
| 任务编写 | 需要主动yield | 可以无限循环 |
| 死锁风险 | 低 | 需要注意 |

## 核心内容

### 调度器架构设计

一个完整的协作式调度器包含以下核心组件：

```
┌─────────────────────────────────────┐
│        应用任务层                    │
│  Task1   Task2   Task3   Task4      │
└──────────┬──────────────────────────┘
           │ yield()
┌──────────▼──────────────────────────┐
│        调度器核心                    │
│  - 任务管理                          │
│  - 调度算法                          │
│  - 上下文切换                        │
└──────────┬──────────────────────────┘
           │
┌──────────▼──────────────────────────┐
│        硬件抽象层                    │
│  - 栈操作                            │
│  - 寄存器操作                        │
└─────────────────────────────────────┘
```

### 数据结构设计

#### 任务控制块（TCB）

任务控制块存储任务的所有信息：

```c
// 任务状态枚举
typedef enum {
    TASK_STATE_READY,      // 就绪
    TASK_STATE_RUNNING,    // 运行
    TASK_STATE_BLOCKED,    // 阻塞
    TASK_STATE_SUSPENDED   // 挂起
} TaskState_t;

// 任务控制块
typedef struct TaskControlBlock {
    uint32_t *stack_ptr;              // 栈指针
    uint32_t stack_size;              // 栈大小
    TaskState_t state;                // 任务状态
    uint8_t priority;                 // 优先级（0最高）
    char name[16];                    // 任务名称
    void (*task_func)(void *);        // 任务函数
    void *param;                      // 任务参数
    struct TaskControlBlock *next;    // 链表指针
} TCB_t;
```


#### 调度器结构

```c
// 调度器配置
#define MAX_TASKS           8
#define IDLE_TASK_STACK     128

// 调度器结构
typedef struct {
    TCB_t *task_list;          // 任务链表头
    TCB_t *current_task;       // 当前运行任务
    uint8_t task_count;        // 任务数量
    uint8_t is_running;        // 调度器运行标志
} Scheduler_t;

// 全局调度器实例
static Scheduler_t g_scheduler = {0};
```

### 核心功能实现

#### 1. 调度器初始化

```c
/**
 * @brief 初始化调度器
 */
void Scheduler_Init(void) {
    g_scheduler.task_list = NULL;
    g_scheduler.current_task = NULL;
    g_scheduler.task_count = 0;
    g_scheduler.is_running = 0;
}
```

#### 2. 任务创建

任务创建是调度器的核心功能之一，需要：
- 分配任务控制块
- 初始化任务栈
- 将任务加入就绪队列

```c
/**
 * @brief 创建新任务
 * @param task_func 任务函数指针
 * @param param 任务参数
 * @param stack 任务栈空间
 * @param stack_size 栈大小（字节）
 * @param priority 优先级（0最高）
 * @param name 任务名称
 * @return 任务控制块指针，失败返回NULL
 */
TCB_t* Task_Create(void (*task_func)(void *),
                   void *param,
                   uint32_t *stack,
                   uint32_t stack_size,
                   uint8_t priority,
                   const char *name) {
    
    // 检查参数
    if (task_func == NULL || stack == NULL || stack_size < 64) {
        return NULL;
    }
    
    // 检查任务数量
    if (g_scheduler.task_count >= MAX_TASKS) {
        return NULL;
    }
    
    // 分配TCB（这里使用静态分配）
    static TCB_t tcb_pool[MAX_TASKS];
    TCB_t *tcb = &tcb_pool[g_scheduler.task_count];
    
    // 初始化TCB
    tcb->task_func = task_func;
    tcb->param = param;
    tcb->stack_size = stack_size;
    tcb->priority = priority;
    tcb->state = TASK_STATE_READY;
    tcb->next = NULL;
    
    // 复制任务名称
    strncpy(tcb->name, name, sizeof(tcb->name) - 1);
    tcb->name[sizeof(tcb->name) - 1] = '\0';
    
    // 初始化任务栈
    tcb->stack_ptr = Task_InitStack(stack, stack_size, task_func, param);
    
    // 将任务加入链表
    Task_AddToList(tcb);
    
    g_scheduler.task_count++;
    
    return tcb;
}
```


#### 3. 任务栈初始化

这是最关键的部分，需要在栈中构造一个"假的"上下文，让任务第一次被调度时能正确启动。

```c
/**
 * @brief 初始化任务栈
 * @param stack 栈空间指针
 * @param stack_size 栈大小
 * @param task_func 任务函数
 * @param param 任务参数
 * @return 初始化后的栈指针
 */
uint32_t* Task_InitStack(uint32_t *stack,
                         uint32_t stack_size,
                         void (*task_func)(void *),
                         void *param) {
    
    uint32_t *stack_top;
    
    // 栈从高地址向低地址增长
    // 计算栈顶地址（字对齐）
    stack_top = stack + (stack_size / sizeof(uint32_t));
    
    // ARM Cortex-M 异常栈帧（硬件自动保存）
    *(--stack_top) = 0x01000000;           // xPSR (Thumb bit set)
    *(--stack_top) = (uint32_t)task_func;  // PC (任务入口地址)
    *(--stack_top) = (uint32_t)Task_Exit;  // LR (任务退出函数)
    *(--stack_top) = 0x12121212;           // R12
    *(--stack_top) = 0x03030303;           // R3
    *(--stack_top) = 0x02020202;           // R2
    *(--stack_top) = 0x01010101;           // R1
    *(--stack_top) = (uint32_t)param;      // R0 (任务参数)
    
    // 软件保存的寄存器
    *(--stack_top) = 0x11111111;           // R11
    *(--stack_top) = 0x10101010;           // R10
    *(--stack_top) = 0x09090909;           // R9
    *(--stack_top) = 0x08080808;           // R8
    *(--stack_top) = 0x07070707;           // R7
    *(--stack_top) = 0x06060606;           // R6
    *(--stack_top) = 0x05050505;           // R5
    *(--stack_top) = 0x04040404;           // R4
    
    return stack_top;
}

/**
 * @brief 任务退出函数
 * 如果任务函数返回，会调用此函数
 */
void Task_Exit(void) {
    // 任务不应该返回，如果返回则进入死循环
    while(1) {
        // 可以在这里添加错误处理
    }
}
```

**栈布局说明**：

```
高地址
  ↓
┌──────────────┐
│   xPSR       │  ← 程序状态寄存器
├──────────────┤
│   PC (R15)   │  ← 程序计数器（任务入口）
├──────────────┤
│   LR (R14)   │  ← 链接寄存器（返回地址）
├──────────────┤
│   R12        │
├──────────────┤
│   R3         │
├──────────────┤
│   R2         │
├──────────────┤
│   R1         │
├──────────────┤
│   R0         │  ← 任务参数
├──────────────┤  ← 硬件自动保存/恢复分界线
│   R11        │
├──────────────┤
│   R10        │
├──────────────┤
│   R9         │
├──────────────┤
│   R8         │
├──────────────┤
│   R7         │
├──────────────┤
│   R6         │
├──────────────┤
│   R5         │
├──────────────┤
│   R4         │  ← 软件需要保存/恢复
└──────────────┘  ← stack_ptr 指向这里
  ↓
低地址
```


#### 4. 任务链表管理

```c
/**
 * @brief 将任务加入就绪链表
 * @param tcb 任务控制块
 */
void Task_AddToList(TCB_t *tcb) {
    if (g_scheduler.task_list == NULL) {
        // 第一个任务
        g_scheduler.task_list = tcb;
        tcb->next = tcb;  // 循环链表
    } else {
        // 插入到链表尾部
        TCB_t *current = g_scheduler.task_list;
        while (current->next != g_scheduler.task_list) {
            current = current->next;
        }
        current->next = tcb;
        tcb->next = g_scheduler.task_list;
    }
}

/**
 * @brief 从链表中移除任务
 * @param tcb 任务控制块
 */
void Task_RemoveFromList(TCB_t *tcb) {
    if (g_scheduler.task_list == NULL || tcb == NULL) {
        return;
    }
    
    // 只有一个任务
    if (g_scheduler.task_list == tcb && tcb->next == tcb) {
        g_scheduler.task_list = NULL;
        return;
    }
    
    // 找到前一个任务
    TCB_t *prev = g_scheduler.task_list;
    while (prev->next != tcb) {
        prev = prev->next;
        if (prev == g_scheduler.task_list) {
            return;  // 未找到
        }
    }
    
    // 移除任务
    prev->next = tcb->next;
    
    // 如果移除的是链表头
    if (g_scheduler.task_list == tcb) {
        g_scheduler.task_list = tcb->next;
    }
}
```

#### 5. 调度算法实现

这里实现简单的轮转调度（Round-Robin）：

```c
/**
 * @brief 选择下一个要运行的任务
 * @return 下一个任务的TCB指针
 */
TCB_t* Scheduler_SelectNext(void) {
    if (g_scheduler.task_list == NULL) {
        return NULL;
    }
    
    TCB_t *next_task;
    
    if (g_scheduler.current_task == NULL) {
        // 第一次调度
        next_task = g_scheduler.task_list;
    } else {
        // 选择下一个就绪任务
        next_task = g_scheduler.current_task->next;
        
        // 跳过非就绪任务
        TCB_t *start = next_task;
        while (next_task->state != TASK_STATE_READY) {
            next_task = next_task->next;
            
            // 如果遍历一圈都没有就绪任务
            if (next_task == start) {
                return NULL;
            }
        }
    }
    
    return next_task;
}
```


#### 6. 上下文切换

这是调度器的核心，需要使用汇编实现：

```c
/**
 * @brief 任务让出CPU（协作式调度的关键）
 * 保存当前任务上下文，切换到下一个任务
 */
void Task_Yield(void) {
    // 触发PendSV异常进行上下文切换
    SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
    
    // 等待PendSV执行
    __DSB();
    __ISB();
}

/**
 * @brief PendSV中断处理函数（汇编实现）
 * 执行实际的上下文切换
 */
__asm void PendSV_Handler(void) {
    IMPORT g_scheduler
    
    // 禁用中断
    CPSID   I
    
    // 保存当前任务上下文
    MRS     R0, PSP                 // 获取进程栈指针
    
    // 检查是否是第一次调度
    LDR     R3, =g_scheduler
    LDR     R2, [R3]                // R2 = g_scheduler.task_list
    CBZ     R2, PendSV_nosave       // 如果为NULL，跳过保存
    
    LDR     R1, [R3, #4]            // R1 = g_scheduler.current_task
    CBZ     R1, PendSV_nosave       // 如果为NULL，跳过保存
    
    // 保存R4-R11到任务栈
    STMDB   R0!, {R4-R11}
    
    // 保存新的栈指针到TCB
    STR     R0, [R1]                // tcb->stack_ptr = SP
    
PendSV_nosave
    // 选择下一个任务
    PUSH    {R3, R14}
    BL      Scheduler_SelectNext    // 调用C函数
    POP     {R3, R14}
    
    // 更新当前任务指针
    STR     R0, [R3, #4]            // g_scheduler.current_task = next_task
    
    // 恢复新任务的上下文
    LDR     R0, [R0]                // R0 = next_task->stack_ptr
    
    // 恢复R4-R11
    LDMIA   R0!, {R4-R11}
    
    // 更新PSP
    MSR     PSP, R0
    
    // 确保使用进程栈
    ORR     LR, LR, #0x04
    
    // 使能中断
    CPSIE   I
    
    // 返回，硬件自动恢复R0-R3, R12, LR, PC, xPSR
    BX      LR
}
```

**上下文切换流程**：

```
1. 任务调用 Task_Yield()
   ↓
2. 触发 PendSV 异常
   ↓
3. 硬件自动保存 R0-R3, R12, LR, PC, xPSR
   ↓
4. 进入 PendSV_Handler
   ↓
5. 软件保存 R4-R11 到当前任务栈
   ↓
6. 保存栈指针到 TCB
   ↓
7. 调用调度算法选择下一个任务
   ↓
8. 从新任务 TCB 加载栈指针
   ↓
9. 恢复 R4-R11 从新任务栈
   ↓
10. 返回，硬件自动恢复 R0-R3, R12, LR, PC, xPSR
   ↓
11. 新任务继续执行
```


#### 7. 启动调度器

```c
/**
 * @brief 启动调度器
 * 此函数不会返回
 */
void Scheduler_Start(void) {
    if (g_scheduler.task_list == NULL) {
        return;  // 没有任务
    }
    
    // 设置PendSV为最低优先级
    NVIC_SetPriority(PendSV_IRQn, 0xFF);
    
    // 选择第一个任务
    g_scheduler.current_task = g_scheduler.task_list;
    g_scheduler.current_task->state = TASK_STATE_RUNNING;
    
    // 标记调度器已启动
    g_scheduler.is_running = 1;
    
    // 启动第一个任务
    Start_FirstTask();
}

/**
 * @brief 启动第一个任务（汇编实现）
 */
__asm void Start_FirstTask(void) {
    IMPORT g_scheduler
    
    // 加载第一个任务的栈指针
    LDR     R0, =g_scheduler
    LDR     R0, [R0, #4]            // R0 = g_scheduler.current_task
    LDR     R0, [R0]                // R0 = current_task->stack_ptr
    
    // 恢复R4-R11
    LDMIA   R0!, {R4-R11}
    
    // 恢复R0-R3, R12
    LDMIA   R0!, {R0-R3, R12}
    
    // 跳过LR
    ADD     R0, R0, #4
    
    // 恢复PC
    LDR     LR, [R0]
    
    // 设置PSP
    LDR     R0, =g_scheduler
    LDR     R0, [R0, #4]
    LDR     R0, [R0]
    MSR     PSP, R0
    
    // 切换到进程栈
    MRS     R0, CONTROL
    ORR     R0, R0, #2
    MSR     CONTROL, R0
    ISB
    
    // 使能中断
    CPSIE   I
    
    // 跳转到任务
    BX      LR
}
```

### 完整示例代码

现在让我们把所有部分组合起来，创建一个完整的示例：

```c
#include <stdint.h>
#include <string.h>

// ============ 配置参数 ============
#define MAX_TASKS           8
#define IDLE_TASK_STACK     128

// ============ 数据结构 ============
typedef enum {
    TASK_STATE_READY,
    TASK_STATE_RUNNING,
    TASK_STATE_BLOCKED,
    TASK_STATE_SUSPENDED
} TaskState_t;

typedef struct TaskControlBlock {
    uint32_t *stack_ptr;
    uint32_t stack_size;
    TaskState_t state;
    uint8_t priority;
    char name[16];
    void (*task_func)(void *);
    void *param;
    struct TaskControlBlock *next;
} TCB_t;

typedef struct {
    TCB_t *task_list;
    TCB_t *current_task;
    uint8_t task_count;
    uint8_t is_running;
} Scheduler_t;

// ============ 全局变量 ============
static Scheduler_t g_scheduler = {0};
static TCB_t tcb_pool[MAX_TASKS];

// ============ 函数声明 ============
void Scheduler_Init(void);
TCB_t* Task_Create(void (*task_func)(void *), void *param,
                   uint32_t *stack, uint32_t stack_size,
                   uint8_t priority, const char *name);
void Scheduler_Start(void);
void Task_Yield(void);
TCB_t* Scheduler_SelectNext(void);

// ============ 实现代码 ============
// （前面已经展示的函数实现）
```


## 实践示例

### 示例1：三个LED闪烁任务

这个示例创建三个任务，每个任务控制一个LED以不同频率闪烁：

```c
#include "scheduler.h"

// GPIO寄存器定义（以STM32为例）
#define GPIOA_ODR   (*(volatile uint32_t *)0x40020014)

// 任务栈定义
#define TASK_STACK_SIZE  256
uint32_t task1_stack[TASK_STACK_SIZE];
uint32_t task2_stack[TASK_STACK_SIZE];
uint32_t task3_stack[TASK_STACK_SIZE];

// 任务1：LED1闪烁（快速）
void Task_LED1(void *param) {
    uint32_t count = 0;
    
    while(1) {
        GPIOA_ODR ^= (1 << 5);  // 翻转PA5
        
        // 延时（通过计数实现）
        for(uint32_t i = 0; i < 100000; i++) {
            __NOP();
        }
        
        count++;
        
        // 每执行10次让出CPU
        if(count % 10 == 0) {
            Task_Yield();
        }
    }
}

// 任务2：LED2闪烁（中速）
void Task_LED2(void *param) {
    uint32_t count = 0;
    
    while(1) {
        GPIOA_ODR ^= (1 << 6);  // 翻转PA6
        
        for(uint32_t i = 0; i < 200000; i++) {
            __NOP();
        }
        
        count++;
        
        if(count % 5 == 0) {
            Task_Yield();
        }
    }
}

// 任务3：LED3闪烁（慢速）
void Task_LED3(void *param) {
    uint32_t count = 0;
    
    while(1) {
        GPIOA_ODR ^= (1 << 7);  // 翻转PA7
        
        for(uint32_t i = 0; i < 500000; i++) {
            __NOP();
        }
        
        count++;
        
        if(count % 2 == 0) {
            Task_Yield();
        }
    }
}

int main(void) {
    // 系统初始化
    SystemInit();
    GPIO_Init();
    
    // 初始化调度器
    Scheduler_Init();
    
    // 创建任务
    Task_Create(Task_LED1, NULL, task1_stack, 
                TASK_STACK_SIZE * sizeof(uint32_t), 1, "LED1");
    Task_Create(Task_LED2, NULL, task2_stack, 
                TASK_STACK_SIZE * sizeof(uint32_t), 1, "LED2");
    Task_Create(Task_LED3, NULL, task3_stack, 
                TASK_STACK_SIZE * sizeof(uint32_t), 1, "LED3");
    
    // 启动调度器
    Scheduler_Start();
    
    // 永远不会执行到这里
    while(1);
    
    return 0;
}
```

**运行效果**：
- LED1快速闪烁
- LED2中速闪烁
- LED3慢速闪烁
- 三个LED看起来"同时"运行

**关键点**：
- 每个任务必须定期调用`Task_Yield()`
- 如果某个任务不调用yield，其他任务将无法运行
- 这就是"协作式"的含义


### 示例2：生产者-消费者模式

这个示例展示任务间的协作：

```c
// 共享缓冲区
#define BUFFER_SIZE  10
volatile uint32_t buffer[BUFFER_SIZE];
volatile uint32_t write_index = 0;
volatile uint32_t read_index = 0;
volatile uint32_t count = 0;

// 生产者任务
void Task_Producer(void *param) {
    uint32_t data = 0;
    
    while(1) {
        // 如果缓冲区未满，生产数据
        if(count < BUFFER_SIZE) {
            buffer[write_index] = data++;
            write_index = (write_index + 1) % BUFFER_SIZE;
            count++;
            
            // 模拟生产耗时
            for(uint32_t i = 0; i < 50000; i++) {
                __NOP();
            }
        }
        
        // 让出CPU给消费者
        Task_Yield();
    }
}

// 消费者任务
void Task_Consumer(void *param) {
    uint32_t data;
    
    while(1) {
        // 如果缓冲区不为空，消费数据
        if(count > 0) {
            data = buffer[read_index];
            read_index = (read_index + 1) % BUFFER_SIZE;
            count--;
            
            // 处理数据（这里只是打印）
            printf("Consumed: %lu\n", data);
            
            // 模拟消费耗时
            for(uint32_t i = 0; i < 100000; i++) {
                __NOP();
            }
        }
        
        // 让出CPU给生产者
        Task_Yield();
    }
}

// 监控任务
void Task_Monitor(void *param) {
    while(1) {
        // 打印缓冲区状态
        printf("Buffer count: %lu\n", count);
        
        // 延时
        for(uint32_t i = 0; i < 1000000; i++) {
            __NOP();
        }
        
        Task_Yield();
    }
}

int main(void) {
    SystemInit();
    
    Scheduler_Init();
    
    // 创建任务
    Task_Create(Task_Producer, NULL, producer_stack, 
                STACK_SIZE, 1, "Producer");
    Task_Create(Task_Consumer, NULL, consumer_stack, 
                STACK_SIZE, 1, "Consumer");
    Task_Create(Task_Monitor, NULL, monitor_stack, 
                STACK_SIZE, 2, "Monitor");
    
    Scheduler_Start();
    
    while(1);
    return 0;
}
```

**运行效果**：
- 生产者不断生产数据
- 消费者不断消费数据
- 监控任务定期显示缓冲区状态
- 三个任务协作完成生产-消费流程


### 示例3：带延时功能的调度器

为了让任务能够精确延时而不占用CPU，我们可以添加延时功能：

```c
// 在TCB中添加延时字段
typedef struct TaskControlBlock {
    // ... 其他字段
    uint32_t delay_ticks;  // 延时计数
} TCB_t;

// 系统tick计数器
volatile uint32_t system_ticks = 0;

// SysTick中断处理
void SysTick_Handler(void) {
    system_ticks++;
    
    // 更新所有任务的延时计数
    TCB_t *task = g_scheduler.task_list;
    if(task != NULL) {
        do {
            if(task->delay_ticks > 0) {
                task->delay_ticks--;
                if(task->delay_ticks == 0) {
                    task->state = TASK_STATE_READY;
                }
            }
            task = task->next;
        } while(task != g_scheduler.task_list);
    }
}

/**
 * @brief 任务延时（毫秒）
 * @param ms 延时时间（毫秒）
 */
void Task_Delay(uint32_t ms) {
    if(g_scheduler.current_task == NULL) {
        return;
    }
    
    // 设置延时计数
    g_scheduler.current_task->delay_ticks = ms;
    g_scheduler.current_task->state = TASK_STATE_BLOCKED;
    
    // 让出CPU
    Task_Yield();
}

// 使用延时的任务示例
void Task_LED_WithDelay(void *param) {
    while(1) {
        GPIOA_ODR ^= (1 << 5);  // 翻转LED
        Task_Delay(500);         // 延时500ms
    }
}
```

**改进说明**：
- 使用SysTick定时器提供时间基准
- 任务可以精确延时而不占用CPU
- 延时期间其他任务可以运行
- 更接近真实RTOS的行为

## 深入理解

### 协作式调度的优缺点

#### 优点

1. **实现简单**
   - 不需要复杂的中断管理
   - 上下文切换开销小
   - 代码量少，易于理解

2. **资源占用小**
   - 内存占用少
   - CPU开销小
   - 适合资源受限的MCU

3. **确定性好**
   - 任务切换点明确
   - 便于分析和调试
   - 不会出现意外的任务切换

4. **无需互斥保护**
   - 任务不会被抢占
   - 共享资源访问简单
   - 不需要复杂的同步机制

#### 缺点

1. **依赖任务配合**
   - 任务必须主动yield
   - 一个任务卡死会影响所有任务
   - 需要程序员自律

2. **实时性差**
   - 响应时间不确定
   - 取决于其他任务的yield频率
   - 不适合硬实时应用

3. **任务编写复杂**
   - 需要在合适的位置yield
   - 不能有长时间的阻塞操作
   - 需要将任务分解为小步骤

4. **扩展性受限**
   - 任务数量增加时难以管理
   - 难以保证公平性
   - 不适合大型系统


### 调度算法对比

| 算法 | 描述 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| 轮转调度 | 按顺序轮流执行 | 简单公平 | 无优先级 | 任务重要性相同 |
| 优先级调度 | 高优先级先执行 | 响应快 | 可能饿死 | 有优先级需求 |
| 最短任务优先 | 执行时间短的先执行 | 平均等待短 | 需要预知时间 | 批处理系统 |
| 公平调度 | 保证每个任务公平 | 公平性好 | 实现复杂 | 多用户系统 |

### 性能优化技巧

#### 1. 减少上下文切换开销

```c
// 使用内联汇编优化关键路径
__forceinline void Context_Switch(void) {
    // 最小化指令数量
    // 使用寄存器传递参数
    // 避免不必要的内存访问
}
```

#### 2. 优化任务栈大小

```c
// 分析任务的实际栈使用
#define TASK_STACK_PATTERN  0xDEADBEEF

void Task_FillStack(uint32_t *stack, uint32_t size) {
    for(uint32_t i = 0; i < size; i++) {
        stack[i] = TASK_STACK_PATTERN;
    }
}

uint32_t Task_GetStackUsage(uint32_t *stack, uint32_t size) {
    uint32_t unused = 0;
    for(uint32_t i = 0; i < size; i++) {
        if(stack[i] == TASK_STACK_PATTERN) {
            unused++;
        } else {
            break;
        }
    }
    return size - unused;
}
```

#### 3. 智能yield策略

```c
// 根据任务状态决定是否yield
void Task_SmartYield(void) {
    static uint32_t yield_count = 0;
    
    yield_count++;
    
    // 每N次循环才yield一次
    if(yield_count >= YIELD_THRESHOLD) {
        yield_count = 0;
        Task_Yield();
    }
}
```

### 调试技巧

#### 1. 任务状态监控

```c
// 任务状态打印
void Scheduler_PrintStatus(void) {
    printf("=== Scheduler Status ===\n");
    printf("Task Count: %d\n", g_scheduler.task_count);
    printf("Running: %s\n", 
           g_scheduler.current_task ? 
           g_scheduler.current_task->name : "None");
    
    TCB_t *task = g_scheduler.task_list;
    if(task != NULL) {
        do {
            printf("Task: %s, State: %d, Priority: %d\n",
                   task->name, task->state, task->priority);
            task = task->next;
        } while(task != g_scheduler.task_list);
    }
}
```

#### 2. 栈溢出检测

```c
// 在栈底放置魔数
#define STACK_CANARY  0xCAFEBABE

void Task_SetStackCanary(TCB_t *tcb) {
    uint32_t *stack_bottom = (uint32_t *)
        ((uint8_t *)tcb->stack_ptr - tcb->stack_size);
    *stack_bottom = STACK_CANARY;
}

uint8_t Task_CheckStackOverflow(TCB_t *tcb) {
    uint32_t *stack_bottom = (uint32_t *)
        ((uint8_t *)tcb->stack_ptr - tcb->stack_size);
    return (*stack_bottom != STACK_CANARY);
}
```

#### 3. 任务执行时间统计

```c
// 在TCB中添加统计字段
typedef struct TaskControlBlock {
    // ... 其他字段
    uint32_t run_time;      // 累计运行时间
    uint32_t switch_count;  // 切换次数
} TCB_t;

// 在上下文切换时更新统计
void Update_TaskStats(void) {
    if(g_scheduler.current_task != NULL) {
        g_scheduler.current_task->switch_count++;
        // 更新运行时间
    }
}
```


## 常见问题

### Q1: 协作式调度器和抢占式调度器的主要区别是什么？

**A**: 核心区别在于任务切换的触发方式：

**协作式调度器**：
- 任务主动调用yield()让出CPU
- 任务执行期间不会被打断
- 实现简单，开销小
- 依赖任务配合

**抢占式调度器**：
- 定时器中断强制切换任务
- 任务可以在任何时刻被打断
- 实时性好，响应快
- 实现复杂，需要互斥保护

**选择建议**：
- 简单应用、资源受限 → 协作式
- 实时性要求高、任务复杂 → 抢占式

### Q2: 为什么要使用PendSV而不是直接在yield函数中切换？

**A**: 使用PendSV有以下优势：

1. **统一的切换点**：所有上下文切换都在PendSV中进行，代码集中
2. **中断安全**：PendSV是最低优先级，不会打断其他中断
3. **硬件支持**：Cortex-M的PendSV专为任务切换设计
4. **延迟切换**：可以在中断中触发切换，但实际切换延迟到中断结束

```c
// 在中断中触发任务切换
void UART_IRQHandler(void) {
    // 处理中断
    // ...
    
    // 触发任务切换（不会立即执行）
    SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
    
    // 中断返回后才执行PendSV
}
```

### Q3: 如何确定任务栈的大小？

**A**: 确定栈大小的方法：

1. **静态分析**：
   - 分析函数调用深度
   - 计算局部变量大小
   - 考虑中断嵌套

2. **运行时测量**：
```c
// 填充栈空间
void Task_FillStack(uint32_t *stack, uint32_t size) {
    for(uint32_t i = 0; i < size; i++) {
        stack[i] = 0xDEADBEEF;
    }
}

// 测量实际使用
uint32_t Task_MeasureStackUsage(uint32_t *stack, uint32_t size) {
    uint32_t used = 0;
    for(uint32_t i = size - 1; i >= 0; i--) {
        if(stack[i] != 0xDEADBEEF) {
            used = size - i;
            break;
        }
    }
    return used;
}
```

3. **经验值**：
   - 简单任务：128-256字节
   - 中等任务：512-1024字节
   - 复杂任务：2048-4096字节
   - 留20-30%余量

### Q4: 任务应该在哪里调用yield？

**A**: yield的调用位置很关键：

**好的做法**：
```c
void Task_Example(void *param) {
    while(1) {
        // 1. 执行一小段工作
        DoSomeWork();
        
        // 2. 主动让出CPU
        Task_Yield();
        
        // 3. 继续下一段工作
        DoMoreWork();
        
        Task_Yield();
    }
}
```

**不好的做法**：
```c
void Task_Bad(void *param) {
    while(1) {
        // 长时间循环，不yield
        for(uint32_t i = 0; i < 1000000; i++) {
            DoWork();
        }
        // 其他任务长时间得不到执行
    }
}
```

**原则**：
- 定期yield（如每10-100ms）
- 在等待事件时yield
- 在长循环中yield
- 避免长时间占用CPU

### Q5: 如何处理任务间的数据共享？

**A**: 协作式调度中数据共享相对简单：

```c
// 共享数据
volatile uint32_t shared_data = 0;

// 任务1：写数据
void Task_Writer(void *param) {
    while(1) {
        // 协作式调度中，这段代码不会被打断
        shared_data++;
        
        // 完成后再yield
        Task_Yield();
    }
}

// 任务2：读数据
void Task_Reader(void *param) {
    while(1) {
        uint32_t data = shared_data;
        printf("Data: %lu\n", data);
        
        Task_Yield();
    }
}
```

**注意事项**：
- 在yield之前完成数据操作
- 使用volatile关键字
- 如果有中断访问，仍需要保护
- 复杂情况考虑使用标志位


## 进阶扩展

### 添加优先级调度

虽然基础版本使用轮转调度，但我们可以添加优先级支持：

```c
/**
 * @brief 优先级调度算法
 * @return 最高优先级的就绪任务
 */
TCB_t* Scheduler_SelectNextPriority(void) {
    if (g_scheduler.task_list == NULL) {
        return NULL;
    }
    
    TCB_t *highest_priority_task = NULL;
    uint8_t highest_priority = 0xFF;  // 最低优先级
    
    TCB_t *task = g_scheduler.task_list;
    do {
        if (task->state == TASK_STATE_READY) {
            if (task->priority < highest_priority) {
                highest_priority = task->priority;
                highest_priority_task = task;
            }
        }
        task = task->next;
    } while (task != g_scheduler.task_list);
    
    return highest_priority_task;
}
```

### 添加任务挂起/恢复

```c
/**
 * @brief 挂起任务
 * @param tcb 任务控制块
 */
void Task_Suspend(TCB_t *tcb) {
    if (tcb == NULL) {
        return;
    }
    
    tcb->state = TASK_STATE_SUSPENDED;
    
    // 如果挂起的是当前任务，立即切换
    if (tcb == g_scheduler.current_task) {
        Task_Yield();
    }
}

/**
 * @brief 恢复任务
 * @param tcb 任务控制块
 */
void Task_Resume(TCB_t *tcb) {
    if (tcb == NULL) {
        return;
    }
    
    if (tcb->state == TASK_STATE_SUSPENDED) {
        tcb->state = TASK_STATE_READY;
    }
}
```

### 添加任务删除

```c
/**
 * @brief 删除任务
 * @param tcb 任务控制块
 */
void Task_Delete(TCB_t *tcb) {
    if (tcb == NULL) {
        return;
    }
    
    // 从链表中移除
    Task_RemoveFromList(tcb);
    
    // 如果删除的是当前任务
    if (tcb == g_scheduler.current_task) {
        g_scheduler.current_task = NULL;
        Task_Yield();  // 立即切换到其他任务
    }
    
    g_scheduler.task_count--;
}
```

### 添加空闲任务

空闲任务在没有其他任务就绪时运行，可以用于低功耗模式：

```c
// 空闲任务栈
uint32_t idle_task_stack[IDLE_TASK_STACK];

/**
 * @brief 空闲任务
 * 在没有其他任务就绪时运行
 */
void Task_Idle(void *param) {
    while(1) {
        // 进入低功耗模式
        __WFI();  // Wait For Interrupt
        
        // 或者执行后台任务
        // BackgroundWork();
        
        Task_Yield();
    }
}

/**
 * @brief 创建空闲任务
 */
void Scheduler_CreateIdleTask(void) {
    Task_Create(Task_Idle, NULL, idle_task_stack,
                sizeof(idle_task_stack), 0xFF, "Idle");
}
```

## 项目实战

### 完整项目：多功能数据采集系统

这个项目展示如何使用协作式调度器构建一个实用的系统：

```c
// ============ 系统配置 ============
#define SAMPLE_RATE     100   // 采样率 100Hz
#define BUFFER_SIZE     64    // 缓冲区大小

// ============ 全局变量 ============
volatile uint16_t adc_buffer[BUFFER_SIZE];
volatile uint8_t buffer_index = 0;
volatile uint8_t data_ready = 0;

// ============ 任务1：数据采集 ============
void Task_DataAcquisition(void *param) {
    uint32_t last_sample_time = 0;
    
    while(1) {
        uint32_t current_time = system_ticks;
        
        // 每10ms采样一次（100Hz）
        if(current_time - last_sample_time >= 10) {
            last_sample_time = current_time;
            
            // 读取ADC
            uint16_t value = ADC_Read();
            
            // 存入缓冲区
            adc_buffer[buffer_index++] = value;
            
            // 缓冲区满
            if(buffer_index >= BUFFER_SIZE) {
                buffer_index = 0;
                data_ready = 1;
            }
        }
        
        Task_Yield();
    }
}

// ============ 任务2：数据处理 ============
void Task_DataProcessing(void *param) {
    uint16_t local_buffer[BUFFER_SIZE];
    
    while(1) {
        // 等待数据就绪
        if(data_ready) {
            // 复制数据
            memcpy(local_buffer, (void *)adc_buffer, 
                   sizeof(adc_buffer));
            data_ready = 0;
            
            // 处理数据
            uint32_t sum = 0;
            for(uint8_t i = 0; i < BUFFER_SIZE; i++) {
                sum += local_buffer[i];
            }
            uint16_t average = sum / BUFFER_SIZE;
            
            // 发送结果
            printf("Average: %u\n", average);
        }
        
        Task_Yield();
    }
}

// ============ 任务3：LED指示 ============
void Task_LEDIndicator(void *param) {
    while(1) {
        // 系统运行指示
        GPIOA_ODR ^= (1 << 5);
        
        Task_Delay(500);  // 延时500ms
    }
}

// ============ 任务4：按键检测 ============
void Task_KeyScan(void *param) {
    uint8_t key_state = 0;
    uint8_t key_count = 0;
    
    while(1) {
        // 读取按键
        uint8_t current = (GPIOA_IDR & (1 << 0)) ? 1 : 0;
        
        // 消抖
        if(current == key_state) {
            key_count = 0;
        } else {
            key_count++;
            if(key_count >= 3) {  // 连续3次相同
                key_state = current;
                key_count = 0;
                
                // 按键按下
                if(key_state == 1) {
                    printf("Key pressed!\n");
                    // 执行相应操作
                }
            }
        }
        
        Task_Delay(10);  // 10ms扫描一次
    }
}

// ============ 主函数 ============
int main(void) {
    // 系统初始化
    SystemInit();
    GPIO_Init();
    ADC_Init();
    UART_Init();
    SysTick_Init();
    
    // 初始化调度器
    Scheduler_Init();
    
    // 创建任务
    Task_Create(Task_DataAcquisition, NULL, 
                task1_stack, STACK_SIZE, 1, "Acquisition");
    Task_Create(Task_DataProcessing, NULL, 
                task2_stack, STACK_SIZE, 2, "Processing");
    Task_Create(Task_LEDIndicator, NULL, 
                task3_stack, STACK_SIZE, 3, "LED");
    Task_Create(Task_KeyScan, NULL, 
                task4_stack, STACK_SIZE, 3, "KeyScan");
    
    // 创建空闲任务
    Scheduler_CreateIdleTask();
    
    // 启动调度器
    Scheduler_Start();
    
    // 永远不会执行到这里
    while(1);
    
    return 0;
}
```

**项目特点**：
- 多任务并发执行
- 实时数据采集和处理
- 用户交互（按键、LED）
- 完整的系统架构


## 总结

协作式调度器是学习RTOS的重要一步，通过本教程你应该掌握了：

### 核心知识点

1. **调度器原理**
   - 任务管理和调度
   - 上下文保存和恢复
   - 任务切换机制

2. **实现技术**
   - 任务控制块设计
   - 栈初始化方法
   - 汇编级上下文切换
   - 调度算法实现

3. **实践技能**
   - 创建和管理任务
   - 实现任务间协作
   - 调试和优化技巧
   - 完整系统设计

### 关键要点

- **协作式调度**：任务主动让出CPU，需要程序员配合
- **上下文切换**：保存和恢复任务状态的核心机制
- **任务栈**：每个任务独立的栈空间，需要合理规划
- **调度算法**：决定任务执行顺序的策略
- **实时性**：协作式调度的实时性依赖任务配合

### 适用场景

协作式调度器适合：
- 中等复杂度的应用（3-10个任务）
- 资源受限的MCU
- 实时性要求不高的场景
- 学习RTOS原理

不适合：
- 硬实时应用
- 大型复杂系统
- 任务数量很多
- 需要严格优先级保证

### 下一步学习

掌握协作式调度器后，建议继续学习：

1. **抢占式调度**：理解定时器中断驱动的任务切换
2. **任务同步**：信号量、互斥量、消息队列
3. **内存管理**：动态内存分配和管理
4. **实时RTOS**：FreeRTOS、RT-Thread等

## 延伸阅读

推荐进一步学习的资源：

- [轻量级任务调度器设计](../advanced/01-lightweight-scheduler.html) - 更完善的调度器实现
- [RTOS基础](../../02-rtos-fundamentals/beginner/01-rtos-overview.html) - 深入学习RTOS
- [FreeRTOS快速入门](../../03-freertos/beginner/01-freertos-quickstart.html) - 学习成熟的RTOS
- [时间片轮询调度算法](../beginner/04-time-slice-scheduling.html) - 另一种调度方式

## 参考资料

1. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" - Joseph Yiu
2. "FreeRTOS Reference Manual" - Real Time Engineers Ltd.
3. "Embedded Systems: Real-Time Operating Systems" - Jonathan Valvano
4. ARM Cortex-M Programming Guide to Memory Barrier Instructions
5. "Operating Systems: Three Easy Pieces" - Remzi H. Arpaci-Dusseau

## 练习题

### 基础练习

1. **任务创建**：创建3个任务，分别以不同频率打印消息
2. **栈分析**：实现栈使用情况监控功能
3. **延时功能**：为调度器添加精确延时功能

### 进阶练习

4. **优先级调度**：实现基于优先级的调度算法
5. **任务统计**：添加任务运行时间统计功能
6. **事件机制**：实现简单的事件等待和通知机制

### 项目练习

7. **温度监控系统**：
   - 任务1：读取温度传感器
   - 任务2：处理和显示数据
   - 任务3：超温报警
   - 任务4：按键控制

8. **串口通信系统**：
   - 任务1：接收串口数据
   - 任务2：解析命令
   - 任务3：执行命令
   - 任务4：发送响应

### 挑战练习

9. **实现一个完整的协作式RTOS**，包括：
   - 任务管理（创建、删除、挂起、恢复）
   - 时间管理（延时、定时器）
   - 任务间通信（消息队列）
   - 同步机制（信号量）

10. **性能对比**：
    - 实现协作式和抢占式两种调度器
    - 对比性能和资源占用
    - 分析各自的优缺点

## 附录

### A. 完整代码清单

完整的调度器代码可以在以下位置找到：
- GitHub: [cooperative-scheduler-example](https://github.com/embedded-knowledge/scheduler-examples)
- 本地路径: `/examples/scheduler/cooperative/`

### B. 常用宏定义

```c
// 任务优先级
#define TASK_PRIORITY_HIGHEST   0
#define TASK_PRIORITY_HIGH      1
#define TASK_PRIORITY_NORMAL    2
#define TASK_PRIORITY_LOW       3
#define TASK_PRIORITY_LOWEST    4

// 任务栈大小
#define TASK_STACK_TINY         128
#define TASK_STACK_SMALL        256
#define TASK_STACK_MEDIUM       512
#define TASK_STACK_LARGE        1024

// 系统配置
#define SYSTEM_TICK_FREQ        1000  // 1ms
#define MAX_TASK_NAME_LEN       16
```

### C. 调试宏

```c
// 调试输出
#ifdef DEBUG
    #define DEBUG_PRINT(fmt, ...) \
        printf("[%s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
#else
    #define DEBUG_PRINT(fmt, ...)
#endif

// 断言
#define ASSERT(expr) \
    if(!(expr)) { \
        printf("Assertion failed: %s, file %s, line %d\n", \
               #expr, __FILE__, __LINE__); \
        while(1); \
    }
```

---

**下一步**：建议学习 [轻量级任务调度器设计](../advanced/01-lightweight-scheduler.html)，了解更完善的调度器实现，或者直接学习 [RTOS基础](../../02-rtos-fundamentals/beginner/01-rtos-overview.html)，深入理解实时操作系统。

**反馈**：如果你在学习过程中遇到问题，欢迎在讨论区提问，或者通过邮件联系我们。

**版权声明**：本教程采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
