---
title: "时间片轮询调度算法：实现简单的多任务调度"
description: "深入学习时间片轮询调度算法的原理和实现方法。通过本文，你将理解时间片的概念、轮询调度的工作机制、任务切换的实现方式，以及如何在裸机环境下构建一个简单但实用的多任务调度系统。"
slug: "time-slice-scheduling"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 时间片
  - 任务调度
  - 轮询
  - 多任务
  - 调度算法
prerequisites:
  - "bare-metal-programming-basics"
  - "super-loop-programming"
related_contents: []

# 学习信息
estimated_time: 40
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
  - 时间片调度
  - Time Slice
  - 轮询调度
  - Round Robin
  - 任务切换
  - 多任务调度
cover_image: ""
---

# 时间片轮询调度算法：实现简单的多任务调度

## 概述

时间片轮询调度（Time Slice Round-Robin Scheduling）是一种简单而有效的任务调度算法，它为每个任务分配固定的执行时间，让多个任务轮流执行，从而在裸机环境下实现"多任务"的效果。完成本文学习后，你将能够：

- 理解时间片调度的基本概念和工作原理
- 掌握轮询调度算法的实现方法
- 学会设计和实现任务切换机制
- 了解如何处理任务优先级
- 能够分析调度系统的性能特征

## 背景知识

### 什么是时间片？

**时间片（Time Slice）** 是分配给每个任务的固定执行时间。就像轮流使用操场，每个班级有固定的时间段，时间到了就换下一个班级。

**核心概念**：
- **时间片长度**：每个任务连续执行的时间，通常为1-100ms
- **时间片用完**：当前任务的时间片耗尽，需要切换到下一个任务
- **任务轮转**：所有任务按顺序轮流获得CPU时间

### 为什么需要时间片调度？

在裸机程序中，我们经常遇到需要"同时"执行多个任务的情况：

**问题场景**：
```c
// 没有调度的代码：任务阻塞
while(1) {
    ReadSensor();      // 可能需要100ms
    UpdateDisplay();   // 可能需要50ms
    CheckButton();     // 需要及时响应
    ProcessData();     // 可能需要200ms
}
```

**问题分析**：
- 如果ReadSensor()阻塞100ms，其他任务都要等待
- CheckButton()无法及时响应用户操作
- 任务执行时间不均衡，影响系统响应性

**使用时间片调度后**：
```c
// 每个任务最多执行10ms
Task1() { ReadSensor(); }      // 分多次完成
Task2() { UpdateDisplay(); }   // 分多次完成
Task3() { CheckButton(); }     // 快速响应
Task4() { ProcessData(); }     // 分多次完成

// 调度器每10ms切换一次任务
// Task1 → Task2 → Task3 → Task4 → Task1 → ...
```

### 轮询调度的特点

**优点**：
- 简单易实现，代码量小
- 公平性好，每个任务都能获得执行机会
- 响应性可预测，最大延迟 = 任务数 × 时间片长度
- 不需要复杂的优先级管理

**缺点**：
- 所有任务优先级相同，无法区分重要性
- 时间片固定，不够灵活
- 任务切换有开销
- 不适合实时性要求极高的场景

## 核心内容

### 时间片调度的基本原理

时间片调度的核心思想是：**将CPU时间分成固定长度的时间片，让每个任务轮流执行一个时间片**。

#### 调度流程

```
[任务1执行] → 时间片到 → [任务2执行] → 时间片到 → [任务3执行] → 时间片到 → [任务1执行] → ...
    10ms                      10ms                      10ms                      10ms
```

**关键步骤**：
1. **初始化**：设置时间片长度，创建任务列表
2. **启动调度**：从第一个任务开始执行
3. **时间片计时**：使用定时器跟踪当前任务的执行时间
4. **任务切换**：时间片到期时，保存当前任务状态，切换到下一个任务
5. **循环执行**：重复步骤3-4

### 基础实现：简单的时间片调度器

让我们从最简单的实现开始，逐步构建一个完整的调度系统。

#### 方法1：函数指针数组实现

这是最简单的实现方式，适合任务数量固定的场景：

```c
#include <stdint.h>
#include <stdbool.h>

// 任务函数类型定义
typedef void (*TaskFunction_t)(void);

// 任务定义
#define MAX_TASKS 4
#define TIME_SLICE_MS 10  // 时间片长度：10ms

// 任务函数数组
TaskFunction_t task_list[MAX_TASKS];
uint8_t task_count = 0;
uint8_t current_task = 0;

// 时间片计数器
volatile uint32_t time_slice_counter = 0;

// 注册任务
void Scheduler_RegisterTask(TaskFunction_t task) {
    if(task_count < MAX_TASKS) {
        task_list[task_count++] = task;
    }
}

// SysTick中断（1ms）
void SysTick_Handler(void) {
    time_slice_counter++;
}

// 调度器主循环
void Scheduler_Run(void) {
    uint32_t last_switch_time = 0;
    
    while(1) {
        // 检查是否需要切换任务
        if((time_slice_counter - last_switch_time) >= TIME_SLICE_MS) {
            last_switch_time = time_slice_counter;
            
            // 切换到下一个任务
            current_task = (current_task + 1) % task_count;
        }
        
        // 执行当前任务
        if(task_count > 0) {
            task_list[current_task]();
        }
    }
}

// 示例任务
void Task_LED(void) {
    static uint32_t counter = 0;
    counter++;
    if(counter >= 50) {  // 500ms
        counter = 0;
        LED_Toggle();
    }
}

void Task_Button(void) {
    if(Button_IsPressed()) {
        HandleButtonPress();
    }
}

void Task_Sensor(void) {
    static uint32_t counter = 0;
    counter++;
    if(counter >= 100) {  // 1000ms
        counter = 0;
        ReadSensor();
    }
}

void Task_Display(void) {
    UpdateDisplay();
}

// 主函数
int main(void) {
    SystemInit();
    SysTick_Init();  // 配置1ms中断
    
    // 注册任务
    Scheduler_RegisterTask(Task_LED);
    Scheduler_RegisterTask(Task_Button);
    Scheduler_RegisterTask(Task_Sensor);
    Scheduler_RegisterTask(Task_Display);
    
    // 启动调度器
    Scheduler_Run();
    
    return 0;
}
```

**代码说明**：
- **任务注册**：使用函数指针数组存储任务
- **时间片计时**：使用SysTick中断提供1ms时基
- **任务切换**：时间片到期时，切换到下一个任务
- **任务执行**：每次循环执行当前任务一次

**关键点**：
- 每个任务函数应该快速返回，不能阻塞
- 任务内部使用计数器实现定时功能
- 时间片长度影响系统响应性和开销

#### 方法2：任务控制块（TCB）实现

使用任务控制块可以存储更多任务信息，实现更灵活的调度：

```c
#include <stdint.h>
#include <stdbool.h>

// 任务状态
typedef enum {
    TASK_STATE_READY,      // 就绪
    TASK_STATE_RUNNING,    // 运行
    TASK_STATE_SUSPENDED   // 挂起
} TaskState_t;

// 任务控制块
typedef struct {
    TaskFunction_t function;    // 任务函数
    TaskState_t state;          // 任务状态
    uint32_t time_slice;        // 时间片长度（ms）
    uint32_t elapsed_time;      // 已执行时间（ms）
    uint32_t total_time;        // 总执行时间（统计）
    uint32_t run_count;         // 运行次数（统计）
    char name[16];              // 任务名称
} TaskControlBlock_t;

// 任务列表
#define MAX_TASKS 8
TaskControlBlock_t task_table[MAX_TASKS];
uint8_t task_count = 0;
uint8_t current_task_index = 0;

// 系统时钟（1ms）
volatile uint32_t system_ticks = 0;

// SysTick中断
void SysTick_Handler(void) {
    system_ticks++;
}

// 创建任务
bool Scheduler_CreateTask(TaskFunction_t function, 
                          uint32_t time_slice,
                          const char *name) {
    if(task_count >= MAX_TASKS) {
        return false;
    }
    
    TaskControlBlock_t *task = &task_table[task_count];
    task->function = function;
    task->state = TASK_STATE_READY;
    task->time_slice = time_slice;
    task->elapsed_time = 0;
    task->total_time = 0;
    task->run_count = 0;
    strncpy(task->name, name, sizeof(task->name) - 1);
    
    task_count++;
    return true;
}

// 挂起任务
void Scheduler_SuspendTask(uint8_t task_id) {
    if(task_id < task_count) {
        task_table[task_id].state = TASK_STATE_SUSPENDED;
    }
}

// 恢复任务
void Scheduler_ResumeTask(uint8_t task_id) {
    if(task_id < task_count) {
        task_table[task_id].state = TASK_STATE_READY;
    }
}

// 获取下一个就绪任务
uint8_t Scheduler_GetNextTask(void) {
    uint8_t start = current_task_index;
    
    do {
        current_task_index = (current_task_index + 1) % task_count;
        
        if(task_table[current_task_index].state == TASK_STATE_READY) {
            return current_task_index;
        }
    } while(current_task_index != start);
    
    return 0xFF;  // 没有就绪任务
}

// 调度器运行
void Scheduler_Run(void) {
    uint32_t last_tick = system_ticks;
    
    while(1) {
        // 计算时间增量
        uint32_t current_tick = system_ticks;
        uint32_t delta = current_tick - last_tick;
        last_tick = current_tick;
        
        if(task_count == 0) {
            continue;
        }
        
        TaskControlBlock_t *current_task = &task_table[current_task_index];
        
        // 更新当前任务的执行时间
        current_task->elapsed_time += delta;
        current_task->total_time += delta;
        
        // 检查时间片是否用完
        if(current_task->elapsed_time >= current_task->time_slice) {
            // 时间片用完，切换任务
            current_task->elapsed_time = 0;
            current_task->state = TASK_STATE_READY;
            
            // 获取下一个任务
            uint8_t next_task = Scheduler_GetNextTask();
            if(next_task != 0xFF) {
                current_task_index = next_task;
                current_task = &task_table[current_task_index];
            }
        }
        
        // 执行当前任务
        if(current_task->state == TASK_STATE_READY) {
            current_task->state = TASK_STATE_RUNNING;
            current_task->run_count++;
            
            // 调用任务函数
            current_task->function();
            
            // 任务执行完毕，恢复就绪状态
            if(current_task->state == TASK_STATE_RUNNING) {
                current_task->state = TASK_STATE_READY;
            }
        }
    }
}

// 打印任务统计信息
void Scheduler_PrintStats(void) {
    printf("Task Statistics:\n");
    printf("%-16s %8s %12s %10s\n", "Name", "State", "Total Time", "Run Count");
    
    for(uint8_t i = 0; i < task_count; i++) {
        TaskControlBlock_t *task = &task_table[i];
        printf("%-16s %8d %12lu %10lu\n",
               task->name,
               task->state,
               task->total_time,
               task->run_count);
    }
}
```

**改进说明**：
- **任务控制块**：存储任务的完整信息
- **任务状态管理**：支持就绪、运行、挂起状态
- **灵活的时间片**：每个任务可以有不同的时间片长度
- **统计功能**：记录任务执行时间和次数
- **任务挂起/恢复**：可以动态控制任务的执行

### 任务切换机制

任务切换是调度器的核心功能，需要考虑以下几个方面：

#### 1. 时间片到期检测

```c
// 方法1：轮询检测
void Scheduler_Loop(void) {
    while(1) {
        if(IsTimeSliceExpired()) {
            SwitchToNextTask();
        }
        ExecuteCurrentTask();
    }
}

// 方法2：中断驱动
void Timer_IRQHandler(void) {
    // 时间片到期中断
    time_slice_expired = true;
}

void Scheduler_Loop(void) {
    while(1) {
        if(time_slice_expired) {
            time_slice_expired = false;
            SwitchToNextTask();
        }
        ExecuteCurrentTask();
    }
}
```

#### 2. 任务上下文保存

在简单的协作式调度中，任务主动返回，不需要保存上下文：

```c
// 协作式任务（主动返回）
void Task_Example(void) {
    // 执行一小段工作
    DoSomeWork();
    
    // 主动返回，让出CPU
    return;
}
```

在抢占式调度中，需要保存任务的执行状态（寄存器、栈指针等）。这在裸机环境下较为复杂，通常需要汇编代码支持。

#### 3. 任务选择策略

```c
// 轮询选择（Round-Robin）
uint8_t SelectNextTask_RoundRobin(void) {
    uint8_t next = (current_task + 1) % task_count;
    
    // 跳过挂起的任务
    while(task_table[next].state == TASK_STATE_SUSPENDED) {
        next = (next + 1) % task_count;
    }
    
    return next;
}

// 优先级选择（带优先级的轮询）
uint8_t SelectNextTask_Priority(void) {
    // 首先查找高优先级任务
    for(uint8_t i = 0; i < task_count; i++) {
        if(task_table[i].priority == PRIORITY_HIGH &&
           task_table[i].state == TASK_STATE_READY) {
            return i;
        }
    }
    
    // 然后查找普通优先级任务
    for(uint8_t i = 0; i < task_count; i++) {
        if(task_table[i].priority == PRIORITY_NORMAL &&
           task_table[i].state == TASK_STATE_READY) {
            return i;
        }
    }
    
    return 0;  // 默认返回空闲任务
}
```

### 优先级处理

虽然基本的时间片调度不考虑优先级，但我们可以通过以下方法引入优先级：

#### 方法1：不同的时间片长度

```c
// 高优先级任务获得更长的时间片
Scheduler_CreateTask(Task_Important, 20, "Important");  // 20ms
Scheduler_CreateTask(Task_Normal, 10, "Normal");        // 10ms
Scheduler_CreateTask(Task_Low, 5, "Low");               // 5ms
```

#### 方法2：优先级队列

```c
typedef enum {
    PRIORITY_HIGH = 0,
    PRIORITY_NORMAL = 1,
    PRIORITY_LOW = 2,
    PRIORITY_LEVELS = 3
} TaskPriority_t;

// 每个优先级一个任务队列
TaskControlBlock_t *priority_queues[PRIORITY_LEVELS][MAX_TASKS];
uint8_t queue_sizes[PRIORITY_LEVELS] = {0};

// 调度时优先选择高优先级队列
uint8_t SelectNextTask_WithPriority(void) {
    // 从高到低遍历优先级
    for(uint8_t prio = 0; prio < PRIORITY_LEVELS; prio++) {
        if(queue_sizes[prio] > 0) {
            // 在该优先级队列中轮询
            return GetNextTaskFromQueue(prio);
        }
    }
    return 0xFF;  // 无任务
}
```

#### 方法3：动态优先级调整

```c
// 防止低优先级任务饥饿
void Scheduler_AdjustPriority(void) {
    for(uint8_t i = 0; i < task_count; i++) {
        TaskControlBlock_t *task = &task_table[i];
        
        // 如果任务长时间未执行，提升优先级
        if(task->wait_time > STARVATION_THRESHOLD) {
            if(task->priority < PRIORITY_HIGH) {
                task->priority--;  // 提升优先级
            }
        }
        
        // 任务执行后，恢复原始优先级
        if(task->state == TASK_STATE_RUNNING) {
            task->priority = task->base_priority;
            task->wait_time = 0;
        } else {
            task->wait_time++;
        }
    }
}
```

### 性能分析

理解调度系统的性能特征对于优化设计非常重要。

#### 1. 响应时间分析

**最坏情况响应时间**：
```
最大响应延迟 = (任务数 - 1) × 时间片长度
```

**示例**：
- 4个任务，每个时间片10ms
- 最坏情况：某个任务刚执行完，需要等待其他3个任务
- 最大延迟 = 3 × 10ms = 30ms

**优化方法**：
- 减少任务数量
- 缩短时间片长度
- 使用优先级调度

#### 2. CPU利用率

```c
// 计算CPU利用率
typedef struct {
    uint32_t total_time;      // 总时间
    uint32_t idle_time;       // 空闲时间
    uint32_t task_time;       // 任务执行时间
    uint32_t switch_time;     // 切换开销时间
} CPUStats_t;

CPUStats_t cpu_stats = {0};

float GetCPUUtilization(void) {
    if(cpu_stats.total_time == 0) {
        return 0.0f;
    }
    
    float utilization = (float)(cpu_stats.task_time) / cpu_stats.total_time * 100.0f;
    return utilization;
}

float GetSwitchOverhead(void) {
    if(cpu_stats.total_time == 0) {
        return 0.0f;
    }
    
    float overhead = (float)(cpu_stats.switch_time) / cpu_stats.total_time * 100.0f;
    return overhead;
}
```

#### 3. 时间片长度选择

时间片长度的选择需要权衡：

**时间片太短**：
- 优点：响应快，任务切换频繁
- 缺点：切换开销大，CPU利用率低

**时间片太长**：
- 优点：切换开销小，CPU利用率高
- 缺点：响应慢，类似超级循环

**推荐值**：
- 简单系统：10-50ms
- 中等复杂度：5-20ms
- 高响应要求：1-10ms

**计算公式**：
```
时间片长度 = 最大可接受延迟 / 任务数
```

## 实践示例

### 示例1：LED和按键的多任务系统

实现一个包含LED闪烁、按键检测和串口通信的多任务系统：

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// 系统配置
#define TIME_SLICE_MS 10
#define MAX_TASKS 4

// 全局变量
volatile uint32_t system_ticks = 0;
TaskControlBlock_t task_table[MAX_TASKS];
uint8_t task_count = 0;
uint8_t current_task = 0;

// SysTick中断（1ms）
void SysTick_Handler(void) {
    system_ticks++;
}

// 任务1：LED闪烁
void Task_LED_Blink(void) {
    static uint32_t last_toggle = 0;
    
    if((system_ticks - last_toggle) >= 500) {
        last_toggle = system_ticks;
        LED_Toggle();
    }
}

// 任务2：按键检测
void Task_Button_Check(void) {
    static uint8_t button_state = 0;
    static uint32_t debounce_timer = 0;
    
    bool button_pressed = Button_Read();
    
    switch(button_state) {
        case 0:  // 空闲
            if(button_pressed) {
                debounce_timer = system_ticks;
                button_state = 1;
            }
            break;
            
        case 1:  // 消抖
            if((system_ticks - debounce_timer) >= 20) {
                if(button_pressed) {
                    // 按键确认
                    OnButtonPressed();
                    button_state = 2;
                } else {
                    button_state = 0;
                }
            }
            break;
            
        case 2:  // 等待释放
            if(!button_pressed) {
                debounce_timer = system_ticks;
                button_state = 3;
            }
            break;
            
        case 3:  // 释放消抖
            if((system_ticks - debounce_timer) >= 20) {
                if(!button_pressed) {
                    button_state = 0;
                }
            }
            break;
    }
}

// 任务3：串口通信
void Task_UART_Process(void) {
    // 检查接收缓冲区
    if(UART_DataAvailable()) {
        uint8_t data = UART_ReadByte();
        ProcessReceivedData(data);
    }
    
    // 检查发送缓冲区
    if(UART_TxReady() && HasDataToSend()) {
        uint8_t data = GetNextByteToSend();
        UART_SendByte(data);
    }
}

// 任务4：系统监控
void Task_System_Monitor(void) {
    static uint32_t last_report = 0;
    
    if((system_ticks - last_report) >= 1000) {
        last_report = system_ticks;
        
        // 打印系统状态
        printf("System uptime: %lu s\n", system_ticks / 1000);
        printf("CPU usage: %.1f%%\n", GetCPUUtilization());
        
        // 打印任务统计
        Scheduler_PrintStats();
    }
}

// 主函数
int main(void) {
    // 硬件初始化
    SystemInit();
    LED_Init();
    Button_Init();
    UART_Init();
    SysTick_Init();
    
    // 创建任务
    Scheduler_CreateTask(Task_LED_Blink, 10, "LED");
    Scheduler_CreateTask(Task_Button_Check, 10, "Button");
    Scheduler_CreateTask(Task_UART_Process, 10, "UART");
    Scheduler_CreateTask(Task_System_Monitor, 10, "Monitor");
    
    // 启动调度器
    printf("Scheduler started\n");
    Scheduler_Run();
    
    return 0;
}
```

**示例说明**：
- **任务1**：LED每500ms闪烁一次
- **任务2**：按键检测，包含消抖处理
- **任务3**：串口数据收发
- **任务4**：系统监控，每秒打印统计信息

**运行效果**：
- 所有任务"同时"运行
- LED稳定闪烁
- 按键响应及时（最大延迟40ms）
- 串口通信流畅
- 定期输出系统状态

### 示例2：带优先级的数据采集系统

实现一个数据采集系统，包含高优先级的实时采集和低优先级的数据处理：

```c
#include <stdint.h>
#include <stdbool.h>

// 优先级定义
typedef enum {
    PRIORITY_HIGH = 0,
    PRIORITY_NORMAL = 1,
    PRIORITY_LOW = 2
} Priority_t;

// 扩展的任务控制块
typedef struct {
    TaskFunction_t function;
    TaskState_t state;
    Priority_t priority;
    uint32_t time_slice;
    uint32_t elapsed_time;
    char name[16];
} TaskControlBlock_Ex_t;

// 数据缓冲区
#define BUFFER_SIZE 128
uint16_t data_buffer[BUFFER_SIZE];
volatile uint8_t write_index = 0;
volatile uint8_t read_index = 0;

// 任务1：高优先级 - ADC采样
void Task_ADC_Sample(void) {
    // 读取ADC
    uint16_t adc_value = ADC_Read();
    
    // 写入缓冲区
    data_buffer[write_index] = adc_value;
    write_index = (write_index + 1) % BUFFER_SIZE;
    
    // 检查缓冲区溢出
    if(write_index == read_index) {
        // 缓冲区满，记录错误
        LogError("Buffer overflow");
    }
}

// 任务2：普通优先级 - 数据处理
void Task_Data_Process(void) {
    // 检查是否有数据
    if(read_index != write_index) {
        // 读取数据
        uint16_t data = data_buffer[read_index];
        read_index = (read_index + 1) % BUFFER_SIZE;
        
        // 处理数据（滤波、计算等）
        float filtered = ApplyFilter(data);
        float result = CalculateResult(filtered);
        
        // 存储结果
        StoreResult(result);
    }
}

// 任务3：低优先级 - 数据上传
void Task_Data_Upload(void) {
    static uint32_t last_upload = 0;
    
    // 每5秒上传一次
    if((system_ticks - last_upload) >= 5000) {
        last_upload = system_ticks;
        
        // 上传数据到云端
        if(HasDataToUpload()) {
            UploadData();
        }
    }
}

// 任务4：低优先级 - 显示更新
void Task_Display_Update(void) {
    static uint32_t last_update = 0;
    
    // 每100ms更新一次显示
    if((system_ticks - last_update) >= 100) {
        last_update = system_ticks;
        UpdateDisplay();
    }
}

// 带优先级的调度器
void Scheduler_Run_WithPriority(void) {
    uint32_t last_tick = system_ticks;
    
    while(1) {
        uint32_t current_tick = system_ticks;
        uint32_t delta = current_tick - last_tick;
        last_tick = current_tick;
        
        // 查找最高优先级的就绪任务
        int8_t next_task = -1;
        Priority_t highest_priority = PRIORITY_LOW + 1;
        
        for(uint8_t i = 0; i < task_count; i++) {
            TaskControlBlock_Ex_t *task = &task_table_ex[i];
            
            if(task->state == TASK_STATE_READY &&
               task->priority < highest_priority) {
                highest_priority = task->priority;
                next_task = i;
            }
        }
        
        if(next_task >= 0) {
            TaskControlBlock_Ex_t *task = &task_table_ex[next_task];
            
            // 更新时间
            task->elapsed_time += delta;
            
            // 检查时间片
            if(task->elapsed_time >= task->time_slice) {
                task->elapsed_time = 0;
                
                // 执行任务
                task->state = TASK_STATE_RUNNING;
                task->function();
                task->state = TASK_STATE_READY;
            }
        }
    }
}

// 主函数
int main(void) {
    SystemInit();
    ADC_Init();
    Display_Init();
    Network_Init();
    SysTick_Init();
    
    // 创建任务（优先级不同）
    Scheduler_CreateTask_Ex(Task_ADC_Sample, 5, PRIORITY_HIGH, "ADC");
    Scheduler_CreateTask_Ex(Task_Data_Process, 10, PRIORITY_NORMAL, "Process");
    Scheduler_CreateTask_Ex(Task_Data_Upload, 20, PRIORITY_LOW, "Upload");
    Scheduler_CreateTask_Ex(Task_Display_Update, 20, PRIORITY_LOW, "Display");
    
    // 启动调度器
    Scheduler_Run_WithPriority();
    
    return 0;
}
```

**示例说明**：
- **高优先级任务**：ADC采样，确保数据不丢失
- **普通优先级任务**：数据处理，及时处理采集的数据
- **低优先级任务**：数据上传和显示更新，不影响关键任务

**优先级效果**：
- ADC采样任务优先执行，保证实时性
- 数据处理任务在采样间隙执行
- 上传和显示任务在系统空闲时执行

## 深入理解

### 调度开销分析

任务切换会带来一定的开销，主要包括：

1. **时间开销**：
   - 保存当前任务状态：几微秒到几十微秒
   - 选择下一个任务：取决于任务数量和算法
   - 恢复新任务状态：几微秒到几十微秒

2. **空间开销**：
   - 任务控制块：每个任务约20-100字节
   - 任务栈：每个任务几百字节到几KB

**测量切换开销**：
```c
void MeasureSwitchOverhead(void) {
    uint32_t start, end;
    
    // 测量切换时间
    start = GetCycleCount();
    SwitchToNextTask();
    end = GetCycleCount();
    
    uint32_t cycles = end - start;
    float time_us = (float)cycles / (CPU_FREQ_MHZ);
    
    printf("Task switch overhead: %.2f us\n", time_us);
}
```

### 与RTOS的对比

时间片调度器是RTOS的简化版本，主要区别：

| 特性 | 时间片调度器 | RTOS |
|-----|------------|------|
| 任务切换 | 协作式或简单抢占 | 完全抢占式 |
| 上下文保存 | 简单或无 | 完整的寄存器保存 |
| 优先级 | 简单或无 | 多级优先级 |
| 同步机制 | 无或简单 | 信号量、互斥量、消息队列 |
| 内存管理 | 静态分配 | 动态内存管理 |
| 代码复杂度 | 低 | 高 |
| 资源占用 | 小（<1KB） | 大（几KB到几十KB） |

**何时升级到RTOS**：
- 任务数量超过5-10个
- 需要复杂的任务间通信
- 需要严格的实时性保证
- 需要使用第三方中间件

### 常见陷阱和最佳实践

#### 陷阱1：任务阻塞

**错误示例**：
```c
void Task_Bad(void) {
    // 错误：阻塞等待
    while(!DataReady()) {
        // 等待数据
    }
    ProcessData();
}
```

**正确做法**：
```c
void Task_Good(void) {
    // 使用状态机，不阻塞
    static uint8_t state = 0;
    
    switch(state) {
        case 0:
            if(DataReady()) {
                state = 1;
            }
            break;
        case 1:
            ProcessData();
            state = 0;
            break;
    }
}
```

#### 陷阱2：共享资源竞争

**错误示例**：
```c
// 全局变量，多个任务访问
uint32_t shared_counter = 0;

void Task1(void) {
    shared_counter++;  // 不安全
}

void Task2(void) {
    shared_counter++;  // 不安全
}
```

**正确做法**：
```c
// 方法1：关中断保护
void Task1(void) {
    __disable_irq();
    shared_counter++;
    __enable_irq();
}

// 方法2：使用标志位
volatile bool resource_locked = false;

void Task1(void) {
    if(!resource_locked) {
        resource_locked = true;
        shared_counter++;
        resource_locked = false;
    }
}
```

#### 陷阱3：时间片过短

**问题**：
```c
// 时间片太短（1ms），切换开销大
#define TIME_SLICE_MS 1

// 如果切换开销为100us，则：
// 开销比例 = 100us / 1000us = 10%
```

**解决方案**：
```c
// 根据任务特性选择合适的时间片
#define TIME_SLICE_MS 10  // 10ms，开销比例降至1%
```

#### 最佳实践

1. **任务设计原则**：
   - 任务函数应该快速返回
   - 使用状态机处理复杂逻辑
   - 避免长时间循环和阻塞

2. **时间片选择**：
   - 根据响应要求选择
   - 考虑切换开销
   - 不同任务可以有不同时间片

3. **优先级设置**：
   - 实时任务高优先级
   - 后台任务低优先级
   - 避免优先级反转

4. **资源保护**：
   - 关中断保护临界区
   - 使用标志位同步
   - 最小化临界区长度

5. **性能监控**：
   - 记录任务执行时间
   - 监控CPU利用率
   - 检测任务饥饿

## 常见问题

### Q1: 时间片调度和超级循环有什么区别？

**A**: 主要区别在于任务执行的公平性和可预测性：

**超级循环**：
- 任务顺序执行，一个任务执行完才执行下一个
- 如果某个任务耗时长，其他任务等待时间不确定
- 响应时间取决于所有任务的总执行时间

**时间片调度**：
- 每个任务最多执行固定时间
- 所有任务轮流获得执行机会
- 响应时间可预测：最大延迟 = (任务数-1) × 时间片

### Q2: 如何选择合适的时间片长度？

**A**: 考虑以下因素：

1. **响应要求**：
   - 如果需要快速响应，选择较短的时间片（1-5ms）
   - 如果响应要求不高，可以选择较长的时间片（20-50ms）

2. **切换开销**：
   - 切换开销通常为几十微秒
   - 时间片应该远大于切换开销（至少100倍）
   - 推荐：时间片 > 100 × 切换时间

3. **任务特性**：
   - 如果任务执行时间短，时间片可以短一些
   - 如果任务需要连续执行，时间片应该长一些

**经验公式**：
```
时间片长度 = 最大可接受延迟 / 任务数量
```

### Q3: 时间片调度能实现真正的多任务吗？

**A**: 不能。时间片调度只是模拟多任务：

- **单核CPU**：同一时刻只有一个任务在执行
- **时间分片**：通过快速切换造成"同时"执行的假象
- **并发不是并行**：任务是交替执行，不是真正的同时执行

真正的多任务需要：
- 多核CPU（硬件并行）
- 或者使用RTOS（软件多任务）

### Q4: 如何调试时间片调度系统？

**A**: 常用的调试方法：

1. **任务执行跟踪**：
```c
void Task_Example(void) {
    GPIO_Set(DEBUG_PIN);  // 任务开始
    
    // 任务代码
    DoWork();
    
    GPIO_Clear(DEBUG_PIN);  // 任务结束
}
// 使用逻辑分析仪观察DEBUG_PIN
```

2. **串口日志**：
```c
void Scheduler_Log(void) {
    printf("[%lu] Task %s running\n", 
           system_ticks, 
           task_table[current_task].name);
}
```

3. **统计信息**：
```c
void PrintTaskStats(void) {
    for(uint8_t i = 0; i < task_count; i++) {
        printf("Task %s: %lu ms, %lu runs\n",
               task_table[i].name,
               task_table[i].total_time,
               task_table[i].run_count);
    }
}
```

4. **断言检查**：
```c
void Scheduler_Check(void) {
    // 检查任务是否超时
    if(task_table[current_task].elapsed_time > MAX_TASK_TIME) {
        ASSERT(0);  // 任务超时
    }
}
```

## 总结

时间片轮询调度是一种简单而实用的任务调度方法，适合在裸机环境下实现基本的多任务功能：

**核心要点**：
- **时间片**：为每个任务分配固定的执行时间
- **轮询调度**：任务按顺序轮流执行
- **任务切换**：时间片到期时切换到下一个任务
- **优先级**：可以通过不同的时间片长度或优先级队列实现

**适用场景**：
- 3-10个简单任务
- 响应要求不是特别严格（几十毫秒级）
- 资源受限，无法使用RTOS
- 学习操作系统原理

**优势**：
- 实现简单，代码量小（<500行）
- 资源占用少（<1KB）
- 响应时间可预测
- 易于理解和调试

**局限**：
- 不支持复杂的任务间通信
- 优先级支持有限
- 不适合大规模应用
- 实时性不如RTOS

**下一步学习**：
- 如果需要更强大的功能，学习RTOS（如FreeRTOS）
- 如果需要更好的任务管理，学习协作式调度器
- 如果需要更精确的时序控制，学习中断驱动架构

## 延伸阅读

推荐进一步学习的资源：

- [协作式多任务调度器实现](../intermediate/01-cooperative-scheduler.html) - 学习更高级的调度方法
- [RTOS基础](../../02-rtos-fundamentals/beginner/01-rtos-overview.html) - 了解专业的实时操作系统
- [软件定时器实现](05-software-timer.html) - 实现精确的时间管理
- [状态机设计模式实战](03-state-machine.html) - 优化任务内部逻辑

## 参考资料

1. "Operating Systems: Three Easy Pieces" - Remzi H. Arpaci-Dusseau
2. "Real-Time Systems" - Jane W. S. Liu
3. "Embedded Systems Architecture" - Tammy Noergaard
4. FreeRTOS Documentation - https://www.freertos.org/

---

**练习题**：

1. 实现一个包含3个任务的时间片调度系统：LED闪烁、按键检测、串口通信
2. 为调度器添加任务挂起和恢复功能
3. 实现一个带优先级的调度器，支持高、中、低三个优先级
4. 测量你的调度器的任务切换开销，并计算CPU利用率

**下一步**：建议学习 [软件定时器实现](05-software-timer.html)，为调度系统添加更精确的时间管理功能。

