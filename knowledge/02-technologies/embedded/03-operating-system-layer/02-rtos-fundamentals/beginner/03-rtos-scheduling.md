---
title: "RTOS调度算法详解：理解任务如何被调度执行"
description: "深入解析RTOS调度算法的核心原理，包括抢占式调度、时间片轮转、优先级调度等关键概念。通过本文学习，你将理解RTOS如何决定任务执行顺序，掌握不同调度策略的特点和应用场景，为优化系统性能打下坚实基础。"
slug: "rtos-scheduling"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 调度算法
  - 抢占式
  - 优先级
  - 时间片
  - 任务调度
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/01-rtos-memory.md"
  - "03-operating-system-layer/02-rtos-fundamentals/advanced/01-real-time-schedulability.md"

# 学习信息
estimated_time: 45
difficulty_score: 4

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
  - RTOS调度
  - 调度算法
  - 抢占式调度
  - 优先级调度
  - 时间片轮转
  - 任务切换
cover_image: ""
---


# RTOS调度算法详解：理解任务如何被调度执行

## 概述

调度器(Scheduler)是RTOS的核心组件，它决定了在任何给定时刻哪个任务应该运行。理解调度算法是掌握RTOS的关键。完成本文学习后，你将能够：

- 理解RTOS调度器的工作原理
- 掌握抢占式调度和协作式调度的区别
- 理解优先级调度的机制和策略
- 掌握时间片轮转调度的原理
- 了解不同调度策略的性能特点
- 学会根据应用需求选择合适的调度策略

## 背景知识

### 什么是调度？

**调度(Scheduling)**是指操作系统决定哪个任务在何时运行的过程。

想象一个场景：
- 你有3个任务要完成：写报告、回邮件、开会
- 如何安排这些任务的执行顺序？
- 如果有紧急任务，是否要中断当前任务？
- 如果任务优先级相同，如何公平分配时间？

这就是调度器要解决的问题。

### 为什么需要调度算法？

在多任务系统中，通常有多个任务需要执行，但CPU只有一个（或有限个）。调度算法的目标是：

1. **保证实时性**：高优先级任务能及时响应
2. **提高效率**：充分利用CPU资源
3. **保证公平性**：相同优先级任务公平分配时间
4. **避免饥饿**：低优先级任务也能得到执行机会


### 相关概念

**就绪队列(Ready Queue)**：存储所有就绪态任务的数据结构，调度器从中选择任务执行。

**上下文切换(Context Switch)**：保存当前任务的状态并恢复另一个任务状态的过程。

**时间片(Time Slice)**：分配给任务的CPU时间单位，也称为时间量子(Time Quantum)。

**调度点(Scheduling Point)**：触发调度器重新选择任务的时刻。


## 核心内容

### 调度器的基本工作流程

调度器的核心工作可以概括为三个步骤：

```
1. 选择任务 → 2. 上下文切换 → 3. 执行任务
     ↑                                    ↓
     └────────────── 调度触发 ←───────────┘
```

**详细流程**：

```c
// 调度器伪代码
void Scheduler(void) {
    while(1) {
        // 1. 从就绪队列中选择最高优先级任务
        Task *next_task = SelectHighestPriorityTask();
        
        // 2. 如果选中的任务不是当前任务，进行切换
        if(next_task != current_task) {
            // 保存当前任务上下文
            SaveContext(current_task);
            
            // 恢复新任务上下文
            RestoreContext(next_task);
            
            // 更新当前任务指针
            current_task = next_task;
        }
        
        // 3. 执行选中的任务
        // （实际上是返回到任务代码继续执行）
    }
}
```


### 抢占式调度 vs 协作式调度

RTOS的调度方式主要分为两大类：抢占式调度和协作式调度。

#### 抢占式调度(Preemptive Scheduling)

**定义**：高优先级任务可以随时中断低优先级任务的执行。

**特点**：
- 实时性好：高优先级任务能立即响应
- 系统响应快：不需要等待当前任务主动让出CPU
- 复杂度高：需要处理任务切换和资源保护
- 适合硬实时系统

**工作原理**：

```
时间轴：
0ms    10ms   20ms   30ms   40ms   50ms
|------|------|------|------|------|
低优先级任务运行
|████████|
        ↑ 高优先级任务就绪
        |██████|  ← 立即抢占
              ↑ 高优先级任务完成
              |████████████████|  ← 恢复低优先级
```

**代码示例**：

```c
// 低优先级任务
void LowPriorityTask(void *param) {
    while(1) {
        printf("Low priority task running\n");
        // 正在执行时可能被高优先级任务抢占
        DoLongWork();  // 长时间工作
        vTaskDelay(100);
    }
}

// 高优先级任务
void HighPriorityTask(void *param) {
    while(1) {
        // 等待事件
        xSemaphoreTake(event_sem, portMAX_DELAY);
        
        // 事件发生时立即抢占低优先级任务
        printf("High priority task running\n");
        HandleCriticalEvent();
        
        // 完成后，低优先级任务继续执行
    }
}

int main(void) {
    // 创建不同优先级的任务
    xTaskCreate(LowPriorityTask, "Low", 128, NULL, 1, NULL);
    xTaskCreate(HighPriorityTask, "High", 128, NULL, 5, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


#### 协作式调度(Cooperative Scheduling)

**定义**：任务必须主动让出CPU，其他任务才能运行。

**特点**：
- 实现简单：不需要复杂的任务切换机制
- 资源保护简单：任务不会被意外中断
- 实时性差：高优先级任务需要等待当前任务让出CPU
- 适合软实时或非实时系统

**工作原理**：

```
时间轴：
0ms    10ms   20ms   30ms   40ms   50ms
|------|------|------|------|------|
任务1运行
|████████████████|
                ↑ 主动让出CPU
                |████████████████|  ← 任务2运行
                                ↑ 主动让出CPU
```

**代码示例**：

```c
// 协作式调度示例
void Task1(void *param) {
    while(1) {
        printf("Task1 running\n");
        DoWork1();
        
        // 主动让出CPU
        taskYIELD();  // 或 vTaskDelay(0)
    }
}

void Task2(void *param) {
    while(1) {
        printf("Task2 running\n");
        DoWork2();
        
        // 主动让出CPU
        taskYIELD();
    }
}

// 注意：如果Task1不调用taskYIELD()，Task2永远无法运行
```

**对比总结**：

| 特性 | 抢占式调度 | 协作式调度 |
|------|-----------|-----------|
| **任务切换** | 自动切换 | 手动切换 |
| **实时性** | 好 | 差 |
| **响应时间** | 短 | 长 |
| **实现复杂度** | 高 | 低 |
| **资源保护** | 需要互斥机制 | 相对简单 |
| **适用场景** | 硬实时系统 | 软实时/非实时系统 |
| **典型应用** | FreeRTOS、RT-Thread | 早期嵌入式系统 |


### 优先级调度

优先级调度是RTOS最常用的调度策略，它根据任务的优先级决定执行顺序。

#### 固定优先级调度(Fixed Priority Scheduling)

**原理**：每个任务在创建时分配一个固定的优先级，调度器总是选择就绪队列中优先级最高的任务执行。

**调度规则**：
1. 高优先级任务优先执行
2. 相同优先级任务按照FIFO或时间片轮转
3. 低优先级任务只有在高优先级任务阻塞时才能运行

**示例场景**：

```c
// 定义优先级
#define PRIORITY_CRITICAL   5  // 关键任务（最高）
#define PRIORITY_HIGH       4  // 高优先级
#define PRIORITY_NORMAL     3  // 普通优先级
#define PRIORITY_LOW        2  // 低优先级
#define PRIORITY_IDLE       1  // 空闲任务（最低）

// 关键任务：安全监控（最高优先级）
void SafetyTask(void *param) {
    while(1) {
        // 监控系统安全状态
        if(CheckSafetyCondition()) {
            // 发现异常，立即处理
            HandleSafetyIssue();
        }
        vTaskDelay(10);  // 每10ms检查一次
    }
}

// 高优先级任务：数据采集
void DataAcquisitionTask(void *param) {
    while(1) {
        // 采集传感器数据
        float sensor_data = ReadSensor();
        
        // 发送到处理队列
        xQueueSend(data_queue, &sensor_data, 0);
        
        vTaskDelay(100);  // 每100ms采集一次
    }
}

// 普通优先级任务：数据处理
void DataProcessingTask(void *param) {
    float data;
    while(1) {
        // 从队列接收数据
        if(xQueueReceive(data_queue, &data, portMAX_DELAY)) {
            // 处理数据
            ProcessData(data);
        }
    }
}

// 低优先级任务：日志记录
void LoggingTask(void *param) {
    while(1) {
        // 记录系统日志
        WriteLog();
        vTaskDelay(1000);  // 每秒记录一次
    }
}

int main(void) {
    // 创建不同优先级的任务
    xTaskCreate(SafetyTask, "Safety", 256, NULL, PRIORITY_CRITICAL, NULL);
    xTaskCreate(DataAcquisitionTask, "DataAcq", 256, NULL, PRIORITY_HIGH, NULL);
    xTaskCreate(DataProcessingTask, "DataProc", 512, NULL, PRIORITY_NORMAL, NULL);
    xTaskCreate(LoggingTask, "Logging", 256, NULL, PRIORITY_LOW, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


**执行时序图**：

```
时间轴：
0ms    10ms   20ms   30ms   40ms   50ms   60ms
|------|------|------|------|------|------|

优先级5（Safety）：
|██|      |██|      |██|      |██|

优先级4（DataAcq）：
  |████|      |████|      |████|

优先级3（DataProc）：
      |██████|      |██████|

优先级2（Logging）：
            |████████████████████|

说明：
- Safety任务每10ms运行一次，立即抢占其他任务
- DataAcq任务在Safety空闲时运行
- DataProc任务在更高优先级任务空闲时运行
- Logging任务优先级最低，只在所有高优先级任务空闲时运行
```

#### 动态优先级调度(Dynamic Priority Scheduling)

**原理**：任务的优先级可以在运行时动态调整。

**应用场景**：
- 避免优先级反转
- 实现优先级继承
- 根据系统状态调整任务重要性

**代码示例**：

```c
TaskHandle_t worker_task_handle;

// 工作任务
void WorkerTask(void *param) {
    while(1) {
        UBaseType_t current_priority = uxTaskPriorityGet(NULL);
        printf("Worker task priority: %d\n", current_priority);
        
        DoWork();
        vTaskDelay(100);
    }
}

// 管理任务
void ManagerTask(void *param) {
    bool emergency_mode = false;
    
    while(1) {
        // 检测系统状态
        if(DetectEmergency()) {
            if(!emergency_mode) {
                // 进入紧急模式：提升工作任务优先级
                printf("Emergency detected! Boosting priority\n");
                vTaskPrioritySet(worker_task_handle, 5);
                emergency_mode = true;
            }
        } else {
            if(emergency_mode) {
                // 恢复正常模式：降低工作任务优先级
                printf("Emergency cleared! Restoring priority\n");
                vTaskPrioritySet(worker_task_handle, 2);
                emergency_mode = false;
            }
        }
        
        vTaskDelay(50);
    }
}

int main(void) {
    // 创建任务
    xTaskCreate(WorkerTask, "Worker", 256, NULL, 2, &worker_task_handle);
    xTaskCreate(ManagerTask, "Manager", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


### 时间片轮转调度

当多个任务具有相同优先级时，RTOS使用时间片轮转(Round-Robin)策略公平分配CPU时间。

#### 工作原理

**基本概念**：
- 每个任务分配一个固定的时间片（如10ms）
- 任务运行完一个时间片后，切换到下一个相同优先级的任务
- 所有相同优先级的任务轮流执行

**时序图**：

```
时间片 = 10ms

时间轴：
0ms    10ms   20ms   30ms   40ms   50ms   60ms
|------|------|------|------|------|------|

任务A（优先级2）：
|██████|            |██████|            |██████|

任务B（优先级2）：
      |██████|            |██████|

任务C（优先级2）：
            |██████|            |██████|

说明：
- 三个任务优先级相同，轮流执行
- 每个任务运行一个时间片（10ms）
- 按照A→B→C→A的顺序循环
```

#### 配置时间片

```c
// FreeRTOSConfig.h 配置文件

// 1. 启用时间片轮转
#define configUSE_TIME_SLICING  1

// 2. 配置时钟节拍频率（影响时间片精度）
#define configTICK_RATE_HZ  1000  // 1ms一个节拍

// 时间片大小 = 1个时钟节拍
// 如果需要更大的时间片，可以在任务中使用延时
```

#### 代码示例

```c
// 三个相同优先级的任务
void Task1(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task1: %d\n", counter++);
        // 不使用延时，让时间片轮转生效
        // 每个时间片后自动切换到Task2
    }
}

void Task2(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task2: %d\n", counter++);
        // 不使用延时
    }
}

void Task3(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task3: %d\n", counter++);
        // 不使用延时
    }
}

int main(void) {
    // 创建三个相同优先级的任务
    xTaskCreate(Task1, "Task1", 128, NULL, 2, NULL);
    xTaskCreate(Task2, "Task2", 128, NULL, 2, NULL);
    xTaskCreate(Task3, "Task3", 128, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**运行结果**：

```
Task1: 0
Task1: 1
Task1: 2
...（运行一个时间片）
Task2: 0
Task2: 1
Task2: 2
...（运行一个时间片）
Task3: 0
Task3: 1
Task3: 2
...（运行一个时间片）
Task1: 3
Task1: 4
...（循环继续）
```


#### 时间片大小的影响

**时间片太小**：
- 优点：任务响应快，看起来更"并发"
- 缺点：上下文切换频繁，CPU开销大

**时间片太大**：
- 优点：上下文切换少，CPU效率高
- 缺点：任务响应慢，用户体验差

**选择建议**：
```c
// 典型配置
#define configTICK_RATE_HZ  1000  // 1ms时钟节拍

// 对于不同应用：
// - 实时性要求高：1-5ms时间片
// - 一般应用：10-20ms时间片
// - 后台任务：50-100ms时间片
```


### 调度策略对比

#### 常见调度策略总结

| 调度策略 | 特点 | 优点 | 缺点 | 适用场景 |
|---------|------|------|------|---------|
| **固定优先级抢占** | 高优先级立即抢占 | 实时性好 | 低优先级可能饥饿 | 硬实时系统 |
| **时间片轮转** | 相同优先级轮流执行 | 公平性好 | 实时性一般 | 多任务公平调度 |
| **协作式调度** | 任务主动让出CPU | 实现简单 | 实时性差 | 简单系统 |
| **动态优先级** | 运行时调整优先级 | 灵活性高 | 复杂度高 | 复杂系统 |

#### 混合调度策略

实际的RTOS通常结合多种策略：

```c
// FreeRTOS的调度策略：
// 1. 优先级抢占式调度（主要策略）
// 2. 相同优先级使用时间片轮转
// 3. 支持动态优先级调整

// 示例：混合调度
void HighPriorityTask(void *param) {
    while(1) {
        // 高优先级任务，抢占式执行
        HandleCriticalEvent();
        vTaskDelay(100);
    }
}

void NormalTask1(void *param) {
    while(1) {
        // 相同优先级任务1，时间片轮转
        DoWork1();
        // 不延时，让时间片轮转生效
    }
}

void NormalTask2(void *param) {
    while(1) {
        // 相同优先级任务2，时间片轮转
        DoWork2();
        // 不延时，让时间片轮转生效
    }
}

int main(void) {
    // 高优先级任务（抢占式）
    xTaskCreate(HighPriorityTask, "High", 256, NULL, 5, NULL);
    
    // 相同优先级任务（时间片轮转）
    xTaskCreate(NormalTask1, "Normal1", 256, NULL, 2, NULL);
    xTaskCreate(NormalTask2, "Normal2", 256, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


### 调度触发时机

调度器在以下情况下会重新选择任务：

#### 1. 时钟节拍中断(Tick Interrupt)

**原理**：每个时钟节拍都会触发调度器检查是否需要切换任务。

```c
// 时钟节拍中断处理函数（简化版）
void SysTick_Handler(void) {
    // 1. 更新系统时钟计数
    system_tick_count++;
    
    // 2. 检查延时任务是否到期
    CheckDelayedTasks();
    
    // 3. 时间片轮转：切换到下一个相同优先级任务
    if(configUSE_TIME_SLICING) {
        RotateReadyList();
    }
    
    // 4. 触发任务调度
    if(NeedReschedule()) {
        TriggerPendSV();  // 触发上下文切换
    }
}
```

**配置**：

```c
// FreeRTOSConfig.h
#define configTICK_RATE_HZ  1000  // 1000Hz = 1ms一次中断

// 时钟节拍频率的影响：
// - 频率高：时间精度高，但中断开销大
// - 频率低：中断开销小，但时间精度低
// 典型值：100Hz-1000Hz
```

#### 2. 任务主动让出CPU

**场景**：
- 调用延时函数：`vTaskDelay()`
- 等待信号量：`xSemaphoreTake()`
- 等待队列：`xQueueReceive()`
- 主动让出：`taskYIELD()`

```c
void Task1(void *param) {
    while(1) {
        DoWork();
        
        // 主动让出CPU，触发调度
        vTaskDelay(100);  // 延时100ms
        // 或
        taskYIELD();      // 立即让出
    }
}
```

#### 3. 高优先级任务就绪

**场景**：
- 中断中释放信号量
- 中断中发送队列消息
- 中断中设置事件标志

```c
// 中断服务函数
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 释放信号量，可能唤醒高优先级任务
    xSemaphoreGiveFromISR(event_sem, &xHigherPriorityTaskWoken);
    
    // 如果唤醒了更高优先级的任务，触发调度
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 高优先级任务
void HighPriorityTask(void *param) {
    while(1) {
        // 等待信号量
        xSemaphoreTake(event_sem, portMAX_DELAY);
        
        // 信号量到来时，立即抢占低优先级任务
        HandleEvent();
    }
}
```

#### 4. 任务优先级改变

```c
void ManagerTask(void *param) {
    while(1) {
        if(NeedBoost()) {
            // 提升任务优先级，触发调度
            vTaskPrioritySet(worker_handle, 5);
            // 如果新优先级高于当前任务，立即切换
        }
        
        vTaskDelay(100);
    }
}
```


### 上下文切换

上下文切换是调度的核心操作，它保存当前任务的状态并恢复新任务的状态。

#### 上下文包含的内容

```c
// 任务上下文（ARM Cortex-M为例）
typedef struct {
    // 1. 通用寄存器
    uint32_t R0;
    uint32_t R1;
    uint32_t R2;
    uint32_t R3;
    uint32_t R4;
    uint32_t R5;
    uint32_t R6;
    uint32_t R7;
    uint32_t R8;
    uint32_t R9;
    uint32_t R10;
    uint32_t R11;
    uint32_t R12;
    
    // 2. 特殊寄存器
    uint32_t SP;   // 栈指针
    uint32_t LR;   // 链接寄存器
    uint32_t PC;   // 程序计数器
    uint32_t PSR;  // 程序状态寄存器
    
    // 3. 浮点寄存器（如果使用FPU）
    float S0_S31[32];
    uint32_t FPSCR;
} TaskContext_t;
```

#### 上下文切换过程

```c
// 上下文切换伪代码
void ContextSwitch(Task *old_task, Task *new_task) {
    // 1. 保存当前任务上下文
    old_task->SP = GetCurrentSP();
    SaveRegisters(old_task);
    
    // 2. 恢复新任务上下文
    RestoreRegisters(new_task);
    SetCurrentSP(new_task->SP);
    
    // 3. 返回到新任务继续执行
    // （通过修改PC寄存器实现）
}
```

**实际实现（ARM Cortex-M）**：

```c
// PendSV中断处理函数（上下文切换）
__asm void PendSV_Handler(void) {
    // 1. 保存当前任务上下文
    MRS     R0, PSP         // 获取任务栈指针
    STMDB   R0!, {R4-R11}   // 保存R4-R11到栈
    
    // 2. 保存栈指针到TCB
    LDR     R1, =pxCurrentTCB
    LDR     R2, [R1]
    STR     R0, [R2]        // 保存SP到TCB
    
    // 3. 选择新任务
    BL      vTaskSwitchContext
    
    // 4. 恢复新任务上下文
    LDR     R1, =pxCurrentTCB
    LDR     R2, [R1]
    LDR     R0, [R2]        // 从TCB加载SP
    
    LDMIA   R0!, {R4-R11}   // 从栈恢复R4-R11
    MSR     PSP, R0         // 恢复任务栈指针
    
    // 5. 返回到新任务
    BX      LR
}
```

#### 上下文切换的开销

**时间开销**：
- Cortex-M3/M4：约1-3微秒
- Cortex-M0：约5-10微秒
- 包含FPU：增加50%-100%

**影响因素**：
- CPU频率
- 是否使用FPU
- 中断嵌套深度
- 缓存命中率

**优化建议**：

```c
// 1. 减少不必要的任务切换
void Task(void *param) {
    while(1) {
        DoWork();
        
        // ❌ 不好：频繁切换
        vTaskDelay(1);  // 每1ms切换一次
        
        // ✅ 更好：减少切换频率
        vTaskDelay(100);  // 每100ms切换一次
    }
}

// 2. 合理设置优先级，避免不必要的抢占
// 3. 使用任务通知代替信号量（更快）
// 4. 禁用FPU（如果不需要浮点运算）
```


## 适用场景分析

### 如何选择调度策略？

根据应用需求选择合适的调度策略：

#### 硬实时系统

**需求**：
- 严格的时间约束
- 高优先级任务必须立即响应
- 可预测的响应时间

**推荐策略**：
- 固定优先级抢占式调度
- 禁用时间片轮转（避免不确定性）
- 精心设计任务优先级

```c
// 硬实时系统配置
#define configUSE_PREEMPTION        1  // 启用抢占
#define configUSE_TIME_SLICING      0  // 禁用时间片
#define configMAX_PRIORITIES        8  // 足够的优先级级别

// 任务优先级分配
#define PRIORITY_SAFETY     7  // 安全关键任务
#define PRIORITY_CONTROL    5  // 控制任务
#define PRIORITY_DATA       3  // 数据处理
#define PRIORITY_LOG        1  // 日志记录
```

#### 软实时系统

**需求**：
- 一般的时间约束
- 偶尔超时可以接受
- 需要公平性

**推荐策略**：
- 优先级抢占式调度
- 启用时间片轮转
- 适度的优先级级别

```c
// 软实时系统配置
#define configUSE_PREEMPTION        1  // 启用抢占
#define configUSE_TIME_SLICING      1  // 启用时间片
#define configMAX_PRIORITIES        5  // 适度的优先级

// 任务优先级分配
#define PRIORITY_HIGH       4  // 重要任务
#define PRIORITY_NORMAL     2  // 普通任务
#define PRIORITY_LOW        1  // 后台任务
```

#### 多任务公平调度

**需求**：
- 多个任务需要公平分配CPU
- 没有严格的实时性要求
- 避免任务饥饿

**推荐策略**：
- 所有任务使用相同优先级
- 启用时间片轮转
- 较大的时间片

```c
// 公平调度配置
#define configUSE_PREEMPTION        1
#define configUSE_TIME_SLICING      1
#define configTICK_RATE_HZ          100  // 10ms时间片

// 所有任务相同优先级
xTaskCreate(Task1, "Task1", 256, NULL, 2, NULL);
xTaskCreate(Task2, "Task2", 256, NULL, 2, NULL);
xTaskCreate(Task3, "Task3", 256, NULL, 2, NULL);
```


## 深入理解

### 调度器的实现原理

#### 就绪队列的数据结构

RTOS通常使用多级队列存储不同优先级的任务：

```c
// 就绪队列结构（简化版）
typedef struct {
    List_t ready_lists[configMAX_PRIORITIES];  // 每个优先级一个链表
    uint32_t ready_bitmap;                      // 位图标记哪些优先级有就绪任务
} ReadyQueue_t;

// 查找最高优先级任务（O(1)时间复杂度）
Task* GetHighestPriorityTask(ReadyQueue_t *queue) {
    // 1. 从位图中找到最高优先级
    int highest_priority = FindHighestBit(queue->ready_bitmap);
    
    // 2. 从对应链表中取出第一个任务
    Task *task = GetFirstTask(&queue->ready_lists[highest_priority]);
    
    return task;
}

// 使用位操作快速查找
int FindHighestBit(uint32_t bitmap) {
    // ARM Cortex-M提供CLZ指令（Count Leading Zeros）
    // 可以在1个时钟周期内完成
    return 31 - __CLZ(bitmap);
}
```

**优势**：
- 查找最高优先级任务：O(1)时间复杂度
- 添加/删除任务：O(1)时间复杂度
- 内存占用小

#### 调度器的状态机

```c
// 调度器状态
typedef enum {
    SCHEDULER_NOT_STARTED,  // 未启动
    SCHEDULER_RUNNING,      // 运行中
    SCHEDULER_SUSPENDED     // 挂起
} SchedulerState_t;

// 调度器控制
void vTaskStartScheduler(void) {
    // 1. 创建空闲任务
    CreateIdleTask();
    
    // 2. 启动时钟节拍
    StartSysTick();
    
    // 3. 选择第一个任务
    Task *first_task = GetHighestPriorityTask();
    
    // 4. 启动第一个任务
    StartFirstTask(first_task);
    
    // 永远不会返回
}

void vTaskSuspendAll(void) {
    // 挂起调度器（不会切换任务）
    scheduler_state = SCHEDULER_SUSPENDED;
}

void xTaskResumeAll(void) {
    // 恢复调度器
    scheduler_state = SCHEDULER_RUNNING;
    
    // 检查是否需要调度
    if(NeedReschedule()) {
        TriggerPendSV();
    }
}
```

### 调度延迟分析

**调度延迟**是指从事件发生到任务开始执行的时间，包括：

```
总延迟 = 中断延迟 + 调度延迟 + 上下文切换时间

中断延迟：从中断发生到ISR开始执行
调度延迟：ISR执行时间 + 调度器选择任务时间
上下文切换：保存/恢复上下文的时间
```

**典型值（Cortex-M4 @ 168MHz）**：

```c
// 中断延迟：12个时钟周期（硬件固定）
// = 12 / 168MHz ≈ 0.07微秒

// 调度延迟：取决于ISR复杂度
// 简单ISR：1-5微秒
// 复杂ISR：10-50微秒

// 上下文切换：约2微秒

// 总延迟：3-57微秒
```

**优化方法**：

```c
// 1. 简化ISR
void EXTI_IRQHandler(void) {
    // ✅ 好：只做必要的操作
    xSemaphoreGiveFromISR(event_sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void EXTI_IRQHandler_Bad(void) {
    // ❌ 不好：在ISR中做复杂处理
    ProcessData();  // 耗时操作
    UpdateDisplay();
    WriteLog();
}

// 2. 使用任务通知代替信号量（更快）
void EXTI_IRQHandler(void) {
    vTaskNotifyGiveFromISR(task_handle, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 3. 降低中断优先级（减少中断嵌套）
NVIC_SetPriority(EXTI0_IRQn, 5);  // 较低的中断优先级
```


### 空闲任务

RTOS会自动创建一个空闲任务(Idle Task)，它在所有其他任务都阻塞时运行。

**空闲任务的作用**：

```c
// 空闲任务伪代码
void IdleTask(void *param) {
    while(1) {
        // 1. 清理被删除任务的资源
        CleanupDeletedTasks();
        
        // 2. 执行用户定义的钩子函数
        if(configUSE_IDLE_HOOK) {
            vApplicationIdleHook();
        }
        
        // 3. 进入低功耗模式（可选）
        if(configUSE_TICKLESS_IDLE) {
            EnterLowPowerMode();
        }
    }
}
```

**空闲任务钩子函数**：

```c
// 在FreeRTOSConfig.h中启用
#define configUSE_IDLE_HOOK  1

// 实现钩子函数
void vApplicationIdleHook(void) {
    // 在空闲任务中执行的代码
    // 注意：不能阻塞或挂起
    
    // 示例1：进入低功耗模式
    __WFI();  // 等待中断
    
    // 示例2：执行后台任务
    CheckSystemHealth();
    
    // 示例3：喂看门狗
    FeedWatchdog();
    
    // 示例4：统计CPU使用率
    UpdateCPUUsage();
}
```

**注意事项**：
- 空闲任务优先级最低（通常为0）
- 空闲任务永远不能阻塞或挂起
- 空闲任务钩子函数必须快速返回
- 如果所有任务都阻塞，空闲任务会一直运行


## 常见问题

### Q1: 为什么高优先级任务会"饿死"低优先级任务？

**A**: 这是优先级调度的固有特性。

**问题场景**：

```c
// 高优先级任务一直运行
void HighPriorityTask(void *param) {
    while(1) {
        DoWork();
        // 没有延时，一直占用CPU
    }
}

// 低优先级任务永远无法运行
void LowPriorityTask(void *param) {
    while(1) {
        DoWork();  // 永远不会执行
        vTaskDelay(100);
    }
}
```

**解决方法**：

```c
// 方法1：高优先级任务添加延时
void HighPriorityTask(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(10);  // 让出CPU
    }
}

// 方法2：使用相同优先级 + 时间片轮转
xTaskCreate(Task1, "Task1", 256, NULL, 2, NULL);
xTaskCreate(Task2, "Task2", 256, NULL, 2, NULL);

// 方法3：动态调整优先级
void ManagerTask(void *param) {
    while(1) {
        // 定期提升低优先级任务
        vTaskPrioritySet(low_task_handle, 5);
        vTaskDelay(100);
        vTaskPrioritySet(low_task_handle, 1);
        vTaskDelay(1000);
    }
}
```

### Q2: 时间片轮转何时生效？

**A**: 只有在以下条件同时满足时才生效：

1. 启用时间片轮转：`configUSE_TIME_SLICING = 1`
2. 有多个相同优先级的就绪任务
3. 任务不主动让出CPU（不调用延时函数）

```c
// ✅ 时间片轮转生效
void Task1(void *param) {
    while(1) {
        DoWork();
        // 不延时，让时间片轮转生效
    }
}

// ❌ 时间片轮转不生效
void Task2(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);  // 主动让出CPU，不需要时间片
    }
}
```


### Q3: 如何确定任务的优先级？

**A**: 根据以下原则分配优先级：

**原则1：根据实时性要求**
```c
// 硬实时任务：最高优先级
#define PRIORITY_SAFETY     7  // 安全关键
#define PRIORITY_CONTROL    5  // 实时控制

// 软实时任务：中等优先级
#define PRIORITY_DATA       3  // 数据处理

// 非实时任务：低优先级
#define PRIORITY_LOG        1  // 日志记录
```

**原则2：根据响应时间要求**
```c
// 需要快速响应：高优先级
xTaskCreate(InterruptHandler, "IRQ", 256, NULL, 6, NULL);

// 周期性任务：中等优先级
xTaskCreate(PeriodicTask, "Periodic", 256, NULL, 3, NULL);

// 后台任务：低优先级
xTaskCreate(BackgroundTask, "BG", 256, NULL, 1, NULL);
```

**原则3：避免过多优先级级别**
```c
// ✅ 好：3-5个优先级级别
#define PRIORITY_CRITICAL   5
#define PRIORITY_HIGH       4
#define PRIORITY_NORMAL     3
#define PRIORITY_LOW        2
#define PRIORITY_IDLE       1

// ❌ 不好：过多的优先级级别
// 难以管理，容易出错
```

### Q4: 上下文切换的开销有多大？

**A**: 上下文切换的开销取决于多个因素：

**典型值**：
```c
// Cortex-M3/M4 @ 168MHz
// 不使用FPU：约2微秒
// 使用FPU：约3-4微秒

// Cortex-M0 @ 48MHz
// 约5-10微秒
```

**测量方法**：

```c
void MeasureContextSwitchTime(void) {
    uint32_t start, end;
    
    // 创建两个高优先级任务
    xTaskCreate(Task1, "Task1", 128, NULL, 5, NULL);
    xTaskCreate(Task2, "Task2", 128, NULL, 5, NULL);
    
    // 在任务中测量
    void Task1(void *param) {
        while(1) {
            start = GetCycleCount();
            taskYIELD();  // 触发切换
        }
    }
    
    void Task2(void *param) {
        while(1) {
            end = GetCycleCount();
            uint32_t cycles = end - start;
            uint32_t time_us = cycles / (CPU_FREQ_MHZ);
            printf("Context switch time: %d us\n", time_us);
            taskYIELD();
        }
    }
}
```

**优化建议**：
- 减少任务切换频率
- 禁用FPU（如果不需要）
- 使用任务通知代替信号量
- 合理设置任务优先级

### Q5: 如何避免优先级反转？

**A**: 优先级反转是指低优先级任务持有高优先级任务需要的资源，导致高优先级任务被阻塞。

**问题场景**：

```c
// 低优先级任务持有互斥量
void LowPriorityTask(void *param) {
    while(1) {
        xSemaphoreTake(mutex, portMAX_DELAY);
        // 持有互斥量，执行长时间操作
        DoLongWork();
        xSemaphoreGive(mutex);
        vTaskDelay(100);
    }
}

// 高优先级任务等待互斥量
void HighPriorityTask(void *param) {
    while(1) {
        // 被低优先级任务阻塞！
        xSemaphoreTake(mutex, portMAX_DELAY);
        DoWork();
        xSemaphoreGive(mutex);
    }
}
```

**解决方法：使用优先级继承互斥量**

```c
// 创建支持优先级继承的互斥量
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

// 当低优先级任务持有互斥量时
// 如果高优先级任务请求该互斥量
// 低优先级任务的优先级会临时提升到高优先级
// 避免被中等优先级任务抢占
```

详细内容请参考：[优先级反转问题与解决](../intermediate/03-priority-inversion.html)


## 性能分析

### 调度器性能指标

#### 1. 调度延迟(Scheduling Latency)

**定义**：从任务就绪到开始执行的时间。

**影响因素**：
- 中断延迟
- 当前任务的剩余时间片
- 调度器算法复杂度
- 上下文切换时间

**测量方法**：

```c
void MeasureSchedulingLatency(void) {
    uint32_t event_time, start_time;
    
    // 在中断中记录事件时间
    void ISR_Handler(void) {
        event_time = GetTimestamp();
        xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
    
    // 在任务中记录开始时间
    void Task(void *param) {
        while(1) {
            xSemaphoreTake(sem, portMAX_DELAY);
            start_time = GetTimestamp();
            
            uint32_t latency = start_time - event_time;
            printf("Scheduling latency: %d us\n", latency);
        }
    }
}
```

#### 2. 吞吐量(Throughput)

**定义**：单位时间内完成的任务数量。

**影响因素**：
- 上下文切换频率
- 任务执行效率
- 调度策略

**优化方法**：
```c
// 减少上下文切换
// 方法1：增加任务延时
vTaskDelay(100);  // 而不是 vTaskDelay(1)

// 方法2：批量处理
void Task(void *param) {
    while(1) {
        // 一次处理多个数据
        for(int i = 0; i < 10; i++) {
            ProcessData();
        }
        vTaskDelay(100);
    }
}
```

#### 3. CPU利用率

**定义**：CPU实际工作时间占总时间的百分比。

**测量方法**：

```c
// 使用空闲任务钩子统计
uint32_t idle_count = 0;
uint32_t total_count = 0;

void vApplicationIdleHook(void) {
    idle_count++;
}

void MonitorTask(void *param) {
    while(1) {
        vTaskDelay(1000);  // 每秒统计一次
        
        total_count = GetTotalTicks();
        float cpu_usage = (1.0f - (float)idle_count / total_count) * 100;
        
        printf("CPU Usage: %.1f%%\n", cpu_usage);
        
        idle_count = 0;
        total_count = 0;
    }
}
```

### 调度策略性能对比

| 策略 | 调度延迟 | 吞吐量 | CPU利用率 | 公平性 | 实时性 |
|------|---------|--------|----------|--------|--------|
| **固定优先级抢占** | 低 | 高 | 高 | 差 | 好 |
| **时间片轮转** | 中 | 中 | 中 | 好 | 中 |
| **协作式调度** | 高 | 低 | 高 | 差 | 差 |
| **动态优先级** | 中 | 中 | 中 | 好 | 好 |

**选择建议**：
- 硬实时系统：固定优先级抢占
- 软实时系统：优先级抢占 + 时间片轮转
- 公平调度：时间片轮转
- 简单系统：协作式调度


## 实践示例

### 示例1：多优先级任务系统

创建一个包含不同优先级任务的完整系统：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 定义优先级
#define PRIORITY_CRITICAL   5
#define PRIORITY_HIGH       4
#define PRIORITY_NORMAL     3
#define PRIORITY_LOW        2

// 全局变量
SemaphoreHandle_t event_sem;
uint32_t critical_counter = 0;
uint32_t high_counter = 0;
uint32_t normal_counter = 0;
uint32_t low_counter = 0;

// 关键任务（最高优先级）
void CriticalTask(void *param) {
    while(1) {
        // 等待紧急事件
        xSemaphoreTake(event_sem, portMAX_DELAY);
        
        // 立即处理
        printf("[CRITICAL] Handling emergency event %d\n", critical_counter++);
        HAL_GPIO_TogglePin(LED_CRITICAL_GPIO_Port, LED_CRITICAL_Pin);
        
        // 快速完成
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// 高优先级任务
void HighPriorityTask(void *param) {
    while(1) {
        printf("[HIGH] Processing data %d\n", high_counter++);
        
        // 模拟数据处理
        for(volatile int i = 0; i < 10000; i++);
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 普通优先级任务
void NormalPriorityTask(void *param) {
    while(1) {
        printf("[NORMAL] Running task %d\n", normal_counter++);
        
        // 模拟工作
        for(volatile int i = 0; i < 5000; i++);
        
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

// 低优先级任务
void LowPriorityTask(void *param) {
    while(1) {
        printf("[LOW] Background task %d\n", low_counter++);
        
        // 后台工作
        for(volatile int i = 0; i < 1000; i++);
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 模拟事件触发
void EventSimulatorTask(void *param) {
    while(1) {
        // 每3秒触发一次紧急事件
        vTaskDelay(pdMS_TO_TICKS(3000));
        
        printf("\n*** Emergency Event Triggered ***\n");
        xSemaphoreGive(event_sem);
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建信号量
    event_sem = xSemaphoreCreateBinary();
    
    // 创建任务（按优先级从高到低）
    xTaskCreate(CriticalTask, "Critical", 256, NULL, PRIORITY_CRITICAL, NULL);
    xTaskCreate(HighPriorityTask, "High", 256, NULL, PRIORITY_HIGH, NULL);
    xTaskCreate(NormalPriorityTask, "Normal", 256, NULL, PRIORITY_NORMAL, NULL);
    xTaskCreate(LowPriorityTask, "Low", 256, NULL, PRIORITY_LOW, NULL);
    xTaskCreate(EventSimulatorTask, "EventSim", 256, NULL, PRIORITY_NORMAL, NULL);
    
    // 启动调度器
    printf("Starting scheduler...\n");
    vTaskStartScheduler();
    
    // 永远不会执行到这里
    while(1);
}
```

**运行效果**：
```
[HIGH] Processing data 0
[NORMAL] Running task 0
[LOW] Background task 0
[HIGH] Processing data 1
[NORMAL] Running task 1

*** Emergency Event Triggered ***
[CRITICAL] Handling emergency event 0  ← 立即抢占
[HIGH] Processing data 2
[NORMAL] Running task 2
...
```


### 示例2：时间片轮转演示

演示相同优先级任务的时间片轮转：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务1
void Task1(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task1: %d\n", counter++);
        
        // 不使用延时，让时间片轮转生效
        // 每个时间片后会自动切换到Task2
        
        // 模拟工作负载
        for(volatile int i = 0; i < 100000; i++);
    }
}

// 任务2
void Task2(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task2: %d\n", counter++);
        
        // 不使用延时
        for(volatile int i = 0; i < 100000; i++);
    }
}

// 任务3
void Task3(void *param) {
    uint32_t counter = 0;
    while(1) {
        printf("Task3: %d\n", counter++);
        
        // 不使用延时
        for(volatile int i = 0; i < 100000; i++);
    }
}

// 监控任务（高优先级）
void MonitorTask(void *param) {
    while(1) {
        printf("\n=== Monitor Report ===\n");
        printf("Free heap: %d bytes\n", xPortGetFreeHeapSize());
        printf("Tick count: %d\n", xTaskGetTickCount());
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}

int main(void) {
    SystemInit();
    
    // 创建三个相同优先级的任务（时间片轮转）
    xTaskCreate(Task1, "Task1", 128, NULL, 2, NULL);
    xTaskCreate(Task2, "Task2", 128, NULL, 2, NULL);
    xTaskCreate(Task3, "Task3", 128, NULL, 2, NULL);
    
    // 创建监控任务（高优先级）
    xTaskCreate(MonitorTask, "Monitor", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**运行效果**：
```
Task1: 0
Task1: 1
Task1: 2
...（运行一个时间片）
Task2: 0
Task2: 1
Task2: 2
...（运行一个时间片）
Task3: 0
Task3: 1
Task3: 2
...（运行一个时间片）
Task1: 3
Task1: 4
...（循环继续）

=== Monitor Report ===  ← 高优先级任务抢占
Free heap: 15360 bytes
Tick count: 5000
```

### 示例3：动态优先级调整

演示根据系统状态动态调整任务优先级：

```c
#include "FreeRTOS.h"
#include "task.h"

TaskHandle_t sensor_task_handle;
TaskHandle_t process_task_handle;

// 传感器任务
void SensorTask(void *param) {
    uint32_t counter = 0;
    while(1) {
        UBaseType_t priority = uxTaskPriorityGet(NULL);
        printf("Sensor task (priority %d): reading %d\n", priority, counter++);
        
        // 模拟传感器读取
        float sensor_value = ReadSensor();
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 数据处理任务
void ProcessTask(void *param) {
    uint32_t counter = 0;
    while(1) {
        UBaseType_t priority = uxTaskPriorityGet(NULL);
        printf("Process task (priority %d): processing %d\n", priority, counter++);
        
        // 模拟数据处理
        ProcessData();
        
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

// 系统管理任务
void SystemManagerTask(void *param) {
    typedef enum {
        MODE_NORMAL,
        MODE_HIGH_SPEED,
        MODE_LOW_POWER
    } SystemMode_t;
    
    SystemMode_t current_mode = MODE_NORMAL;
    uint32_t cycle = 0;
    
    while(1) {
        cycle++;
        
        // 每5秒切换一次模式
        if(cycle % 5 == 0) {
            current_mode = (current_mode + 1) % 3;
            
            switch(current_mode) {
                case MODE_NORMAL:
                    printf("\n*** NORMAL MODE ***\n");
                    vTaskPrioritySet(sensor_task_handle, 2);
                    vTaskPrioritySet(process_task_handle, 2);
                    break;
                    
                case MODE_HIGH_SPEED:
                    printf("\n*** HIGH SPEED MODE ***\n");
                    // 提升传感器任务优先级
                    vTaskPrioritySet(sensor_task_handle, 5);
                    vTaskPrioritySet(process_task_handle, 4);
                    break;
                    
                case MODE_LOW_POWER:
                    printf("\n*** LOW POWER MODE ***\n");
                    // 降低所有任务优先级
                    vTaskPrioritySet(sensor_task_handle, 1);
                    vTaskPrioritySet(process_task_handle, 1);
                    break;
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void) {
    SystemInit();
    
    // 创建任务
    xTaskCreate(SensorTask, "Sensor", 256, NULL, 2, &sensor_task_handle);
    xTaskCreate(ProcessTask, "Process", 256, NULL, 2, &process_task_handle);
    xTaskCreate(SystemManagerTask, "Manager", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


## 总结

调度算法是RTOS的核心，理解调度原理对于开发高效的嵌入式系统至关重要。

**核心要点**：

1. **调度方式**：
   - 抢占式调度：高优先级任务可以随时抢占低优先级任务
   - 协作式调度：任务必须主动让出CPU
   - 现代RTOS主要使用抢占式调度

2. **优先级调度**：
   - 固定优先级：任务优先级在创建时确定
   - 动态优先级：运行时可以调整任务优先级
   - 高优先级任务优先执行

3. **时间片轮转**：
   - 相同优先级任务公平分配CPU时间
   - 每个任务运行一个时间片后切换
   - 需要启用配置：`configUSE_TIME_SLICING = 1`

4. **调度触发时机**：
   - 时钟节拍中断
   - 任务主动让出CPU
   - 高优先级任务就绪
   - 任务优先级改变

5. **上下文切换**：
   - 保存当前任务状态
   - 恢复新任务状态
   - 开销：1-10微秒（取决于CPU和配置）

**最佳实践**：

- 根据实时性要求选择调度策略
- 合理分配任务优先级（3-5个级别）
- 避免高优先级任务长时间占用CPU
- 使用时间片轮转实现公平调度
- 定期检查系统性能指标
- 使用优先级继承避免优先级反转

**配置建议**：

```c
// FreeRTOSConfig.h 推荐配置

// 启用抢占式调度
#define configUSE_PREEMPTION        1

// 启用时间片轮转
#define configUSE_TIME_SLICING      1

// 时钟节拍频率（1ms）
#define configTICK_RATE_HZ          1000

// 优先级级别（5个足够）
#define configMAX_PRIORITIES        5

// 启用空闲任务钩子
#define configUSE_IDLE_HOOK         1

// 启用任务统计
#define configGENERATE_RUN_TIME_STATS  1
```

**性能优化**：

- 减少任务切换频率
- 简化中断服务函数
- 使用任务通知代替信号量
- 合理配置时间片大小
- 避免不必要的优先级调整

**下一步学习**：

- 学习任务间通信机制（信号量、队列、事件组）
- 理解优先级反转问题及解决方案
- 学习实时性分析和可调度性理论
- 实践完整的多任务项目

## 延伸阅读

推荐进一步学习的资源：

- [信号量使用实战](04-semaphore.html) - 学习任务同步机制
- [互斥量与临界区保护](05-mutex.html) - 保护共享资源
- [优先级反转问题与解决](../intermediate/03-priority-inversion.html) - 深入理解调度问题
- [实时性分析与调度可行性](../advanced/01-real-time-schedulability.html) - 理论分析
- [RTOS中断管理与延迟处理](../intermediate/04-rtos-interrupt.html) - 中断与调度的配合

## 参考资料

1. "Real-Time Systems" - Jane W. S. Liu
2. "Mastering the FreeRTOS Real Time Kernel" - Richard Barry
3. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" - Joseph Yiu
4. FreeRTOS官方文档 - https://www.freertos.org/
5. "Operating System Concepts" - Abraham Silberschatz
6. "Real-Time Concepts for Embedded Systems" - Qing Li, Caroline Yao

---

**练习题**：

1. **基础练习**：
   - 创建三个不同优先级的任务，观察它们的执行顺序
   - 实现时间片轮转，让三个相同优先级的任务轮流执行

2. **进阶练习**：
   - 测量上下文切换的时间开销
   - 实现一个动态优先级调整系统
   - 分析不同调度策略对系统性能的影响

3. **综合练习**：
   - 设计一个多任务系统，包含不同优先级的任务
   - 实现CPU使用率统计功能
   - 优化系统性能，减少上下文切换开销

4. **调试练习**：
   - 故意制造优先级反转问题，观察系统行为
   - 使用调试工具分析任务调度情况
   - 测量和优化系统的调度延迟

**下一步**：建议学习 [信号量使用实战](04-semaphore.html)，掌握任务间同步和通信机制。
