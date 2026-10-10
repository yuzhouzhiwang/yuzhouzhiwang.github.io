---
title: "软件定时器实现：构建灵活的时间管理系统"
description: "深入学习软件定时器的设计与实现方法。通过本教程，你将掌握定时器的数据结构设计、链表管理技术、超时处理机制、周期任务实现，以及如何优化定时器精度，为裸机程序构建一个完整的时间管理系统。"
slug: "software-timer-implementation"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 软件定时器
  - 定时任务
  - 链表
  - 时间管理
  - 超时处理
prerequisites:
  - "bare-metal-programming-basics"
  - "super-loop-programming"
  - "time-slice-scheduling"
related_contents: []

# 学习信息
estimated_time: 65
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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 软件定时器
  - Software Timer
  - 定时器链表
  - 超时管理
  - 周期任务
  - 时间管理
cover_image: ""
---

# 软件定时器实现：构建灵活的时间管理系统

## 概述

软件定时器（Software Timer）是嵌入式系统中非常重要的组件，它允许我们在指定的时间后执行特定的操作，而不需要占用硬件定时器资源。通过本教程，你将学会：

- 理解软件定时器的工作原理和应用场景
- 掌握基于链表的定时器管理方法
- 实现单次和周期性定时器
- 处理定时器超时和回调函数
- 优化定时器精度和性能

## 背景知识

### 什么是软件定时器？

**软件定时器**是通过软件方式实现的定时功能，它依赖于一个硬件定时器（通常是SysTick）提供的时基，但可以创建多个独立的定时器实例。

**类比理解**：
- **硬件定时器**：像一个闹钟，只能设置一个时间
- **软件定时器**：像手机上的多个提醒事项，可以设置很多个不同的时间

**核心概念**：
- **时基（Time Base）**：提供基准时钟，通常为1ms
- **定时器实例**：每个定时器有自己的超时时间和回调函数
- **定时器链表**：管理多个定时器实例
- **超时处理**：时间到达时执行回调函数

### 为什么需要软件定时器？

在嵌入式系统中，我们经常需要在不同的时间点执行不同的任务：

**问题场景**：
```c
// 需要多个定时功能
void main_loop(void) {
    // LED每500ms闪烁
    // 按键每20ms检测
    // 传感器每1000ms读取
    // 显示每100ms更新
    // 通信每5000ms发送心跳
}
```

**硬件定时器的限制**：
- 数量有限（通常只有2-4个）
- 配置复杂
- 不够灵活

**软件定时器的优势**：
- 可以创建任意数量的定时器
- 使用简单，接口统一
- 灵活的超时处理
- 支持单次和周期定时


### 软件定时器的工作原理

软件定时器的基本工作流程：

```
[硬件定时器] → 1ms中断 → [更新所有定时器] → [检查超时] → [执行回调]
     ↓                          ↓                    ↓              ↓
  SysTick              减少剩余时间          时间到达？      调用回调函数
```

**关键步骤**：
1. **初始化**：创建定时器，设置超时时间和回调函数
2. **启动定时器**：将定时器加入活动链表
3. **时基更新**：每1ms更新所有活动定时器
4. **超时检测**：检查哪些定时器已经超时
5. **回调执行**：执行超时定时器的回调函数
6. **周期处理**：如果是周期定时器，重新启动

## 核心内容

### 定时器数据结构设计

一个完整的软件定时器需要包含以下信息：

```c
#include <stdint.h>
#include <stdbool.h>

// 定时器类型
typedef enum {
    TIMER_TYPE_ONE_SHOT,    // 单次定时器
    TIMER_TYPE_PERIODIC     // 周期定时器
} TimerType_t;

// 定时器状态
typedef enum {
    TIMER_STATE_STOPPED,    // 停止
    TIMER_STATE_RUNNING,    // 运行中
    TIMER_STATE_EXPIRED     // 已超时
} TimerState_t;

// 定时器回调函数类型
typedef void (*TimerCallback_t)(void *arg);

// 软件定时器结构体
typedef struct SoftwareTimer {
    uint32_t timeout;           // 超时时间（ms）
    uint32_t remaining;         // 剩余时间（ms）
    TimerType_t type;           // 定时器类型
    TimerState_t state;         // 定时器状态
    TimerCallback_t callback;   // 回调函数
    void *callback_arg;         // 回调函数参数
    struct SoftwareTimer *next; // 链表指针
    char name[16];              // 定时器名称（调试用）
} SoftwareTimer_t;
```

**字段说明**：
- **timeout**：定时器的超时时间，单位为毫秒
- **remaining**：剩余时间，每次时基更新时递减
- **type**：单次定时器超时后停止，周期定时器自动重启
- **state**：定时器当前状态
- **callback**：超时时调用的函数
- **callback_arg**：传递给回调函数的参数
- **next**：链表指针，用于管理多个定时器
- **name**：定时器名称，方便调试

### 基础实现：简单的定时器管理

让我们从最简单的实现开始：

#### 方法1：数组管理（固定数量）

适合定时器数量固定的场景：

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 配置
#define MAX_TIMERS 10

// 定时器池
SoftwareTimer_t timer_pool[MAX_TIMERS];
uint8_t timer_count = 0;

// 系统时钟（1ms）
volatile uint32_t system_ticks = 0;

// SysTick中断（1ms）
void SysTick_Handler(void) {
    system_ticks++;
    Timer_Update();  // 更新所有定时器
}

// 创建定时器
SoftwareTimer_t* Timer_Create(uint32_t timeout_ms,
                               TimerType_t type,
                               TimerCallback_t callback,
                               void *arg,
                               const char *name) {
    if(timer_count >= MAX_TIMERS) {
        return NULL;  // 定时器池已满
    }
    
    SoftwareTimer_t *timer = &timer_pool[timer_count++];
    
    timer->timeout = timeout_ms;
    timer->remaining = timeout_ms;
    timer->type = type;
    timer->state = TIMER_STATE_STOPPED;
    timer->callback = callback;
    timer->callback_arg = arg;
    timer->next = NULL;
    strncpy(timer->name, name, sizeof(timer->name) - 1);
    
    return timer;
}

// 启动定时器
void Timer_Start(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    timer->remaining = timer->timeout;
    timer->state = TIMER_STATE_RUNNING;
}

// 停止定时器
void Timer_Stop(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    timer->state = TIMER_STATE_STOPPED;
}

// 更新所有定时器（在SysTick中断中调用）
void Timer_Update(void) {
    for(uint8_t i = 0; i < timer_count; i++) {
        SoftwareTimer_t *timer = &timer_pool[i];
        
        // 只更新运行中的定时器
        if(timer->state != TIMER_STATE_RUNNING) {
            continue;
        }
        
        // 递减剩余时间
        if(timer->remaining > 0) {
            timer->remaining--;
        }
        
        // 检查是否超时
        if(timer->remaining == 0) {
            timer->state = TIMER_STATE_EXPIRED;
            
            // 执行回调函数
            if(timer->callback != NULL) {
                timer->callback(timer->callback_arg);
            }
            
            // 处理周期定时器
            if(timer->type == TIMER_TYPE_PERIODIC) {
                timer->remaining = timer->timeout;
                timer->state = TIMER_STATE_RUNNING;
            } else {
                timer->state = TIMER_STATE_STOPPED;
            }
        }
    }
}

// 示例：LED闪烁定时器
void LED_Toggle_Callback(void *arg) {
    LED_Toggle();
}

// 示例：传感器读取定时器
void Sensor_Read_Callback(void *arg) {
    uint16_t value = ReadSensor();
    printf("Sensor value: %u\n", value);
}

// 使用示例
int main(void) {
    SystemInit();
    SysTick_Init();  // 配置1ms中断
    
    // 创建LED闪烁定时器（周期500ms）
    SoftwareTimer_t *led_timer = Timer_Create(
        500,                      // 500ms
        TIMER_TYPE_PERIODIC,      // 周期定时器
        LED_Toggle_Callback,      // 回调函数
        NULL,                     // 无参数
        "LED"                     // 名称
    );
    
    // 创建传感器读取定时器（周期1000ms）
    SoftwareTimer_t *sensor_timer = Timer_Create(
        1000,
        TIMER_TYPE_PERIODIC,
        Sensor_Read_Callback,
        NULL,
        "Sensor"
    );
    
    // 启动定时器
    Timer_Start(led_timer);
    Timer_Start(sensor_timer);
    
    // 主循环
    while(1) {
        // 其他任务
    }
    
    return 0;
}
```

**代码说明**：
- **定时器池**：使用数组存储所有定时器
- **时基更新**：SysTick中断每1ms调用Timer_Update()
- **超时检测**：遍历所有定时器，检查剩余时间
- **回调执行**：超时时调用回调函数
- **周期处理**：周期定时器自动重启

**优点**：
- 实现简单
- 内存占用固定
- 适合定时器数量少的场景

**缺点**：
- 定时器数量固定
- 每次更新需要遍历所有定时器（包括停止的）
- 效率较低


#### 方法2：链表管理（动态数量）

使用链表可以更灵活地管理定时器：

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

// 活动定时器链表头
SoftwareTimer_t *active_timer_list = NULL;

// 系统时钟
volatile uint32_t system_ticks = 0;

// SysTick中断
void SysTick_Handler(void) {
    system_ticks++;
    Timer_UpdateList();
}

// 创建定时器（动态分配）
SoftwareTimer_t* Timer_Create(uint32_t timeout_ms,
                               TimerType_t type,
                               TimerCallback_t callback,
                               void *arg,
                               const char *name) {
    // 分配内存
    SoftwareTimer_t *timer = (SoftwareTimer_t*)malloc(sizeof(SoftwareTimer_t));
    if(timer == NULL) {
        return NULL;
    }
    
    // 初始化
    timer->timeout = timeout_ms;
    timer->remaining = timeout_ms;
    timer->type = type;
    timer->state = TIMER_STATE_STOPPED;
    timer->callback = callback;
    timer->callback_arg = arg;
    timer->next = NULL;
    strncpy(timer->name, name, sizeof(timer->name) - 1);
    
    return timer;
}

// 启动定时器（加入活动链表）
void Timer_Start(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    // 如果已经在链表中，先移除
    Timer_Stop(timer);
    
    // 重置剩余时间
    timer->remaining = timer->timeout;
    timer->state = TIMER_STATE_RUNNING;
    
    // 加入链表头部
    timer->next = active_timer_list;
    active_timer_list = timer;
}

// 停止定时器（从活动链表移除）
void Timer_Stop(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    timer->state = TIMER_STATE_STOPPED;
    
    // 从链表中移除
    SoftwareTimer_t **current = &active_timer_list;
    while(*current != NULL) {
        if(*current == timer) {
            *current = timer->next;
            timer->next = NULL;
            break;
        }
        current = &((*current)->next);
    }
}

// 删除定时器（释放内存）
void Timer_Delete(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    // 先停止
    Timer_Stop(timer);
    
    // 释放内存
    free(timer);
}

// 更新活动定时器链表
void Timer_UpdateList(void) {
    SoftwareTimer_t *current = active_timer_list;
    SoftwareTimer_t *prev = NULL;
    
    while(current != NULL) {
        SoftwareTimer_t *next = current->next;
        
        // 递减剩余时间
        if(current->remaining > 0) {
            current->remaining--;
        }
        
        // 检查超时
        if(current->remaining == 0) {
            current->state = TIMER_STATE_EXPIRED;
            
            // 执行回调
            if(current->callback != NULL) {
                current->callback(current->callback_arg);
            }
            
            // 处理周期定时器
            if(current->type == TIMER_TYPE_PERIODIC) {
                current->remaining = current->timeout;
                current->state = TIMER_STATE_RUNNING;
                prev = current;
            } else {
                // 单次定时器，从链表移除
                if(prev == NULL) {
                    active_timer_list = next;
                } else {
                    prev->next = next;
                }
                current->state = TIMER_STATE_STOPPED;
                current->next = NULL;
            }
        } else {
            prev = current;
        }
        
        current = next;
    }
}

// 获取活动定时器数量
uint32_t Timer_GetActiveCount(void) {
    uint32_t count = 0;
    SoftwareTimer_t *current = active_timer_list;
    
    while(current != NULL) {
        count++;
        current = current->next;
    }
    
    return count;
}

// 打印所有活动定时器
void Timer_PrintActive(void) {
    printf("Active Timers:\n");
    printf("%-16s %10s %10s\n", "Name", "Timeout", "Remaining");
    
    SoftwareTimer_t *current = active_timer_list;
    while(current != NULL) {
        printf("%-16s %10lu %10lu\n",
               current->name,
               current->timeout,
               current->remaining);
        current = current->next;
    }
}
```

**改进说明**：
- **动态分配**：使用malloc/free管理内存
- **链表管理**：只遍历活动的定时器
- **自动移除**：单次定时器超时后自动从链表移除
- **效率提升**：不需要遍历停止的定时器

**优点**：
- 定时器数量灵活
- 只更新活动定时器，效率高
- 内存按需分配

**缺点**：
- 需要动态内存管理
- 代码稍复杂
- 可能有内存碎片

### 链表管理优化

为了提高效率，我们可以使用有序链表：

```c
// 按剩余时间排序的链表
// 最快超时的定时器在链表头部

void Timer_Start_Sorted(SoftwareTimer_t *timer) {
    if(timer == NULL) return;
    
    timer->remaining = timer->timeout;
    timer->state = TIMER_STATE_RUNNING;
    
    // 插入到有序链表中
    SoftwareTimer_t **current = &active_timer_list;
    
    while(*current != NULL && (*current)->remaining < timer->remaining) {
        current = &((*current)->next);
    }
    
    timer->next = *current;
    *current = timer;
}

// 优化的更新函数
void Timer_UpdateList_Optimized(void) {
    SoftwareTimer_t *current = active_timer_list;
    SoftwareTimer_t *prev = NULL;
    
    while(current != NULL) {
        // 递减剩余时间
        if(current->remaining > 0) {
            current->remaining--;
        }
        
        // 如果第一个定时器还没超时，后面的都不会超时
        if(current->remaining > 0) {
            break;
        }
        
        // 处理超时
        SoftwareTimer_t *next = current->next;
        
        current->state = TIMER_STATE_EXPIRED;
        
        if(current->callback != NULL) {
            current->callback(current->callback_arg);
        }
        
        if(current->type == TIMER_TYPE_PERIODIC) {
            // 周期定时器，重新插入
            if(prev == NULL) {
                active_timer_list = next;
            } else {
                prev->next = next;
            }
            Timer_Start_Sorted(current);
        } else {
            // 单次定时器，移除
            if(prev == NULL) {
                active_timer_list = next;
            } else {
                prev->next = next;
            }
            current->state = TIMER_STATE_STOPPED;
            current->next = NULL;
        }
        
        current = next;
    }
}
```

**优化效果**：
- 链表按剩余时间排序
- 只需检查链表头部
- 如果头部未超时，后面的都不会超时
- 大幅减少检查次数


### 超时处理机制

超时处理是定时器的核心功能，需要考虑以下几个方面：

#### 1. 回调函数设计

```c
// 简单回调（无参数）
void SimpleCallback(void *arg) {
    LED_Toggle();
}

// 带参数回调
typedef struct {
    uint8_t led_id;
    bool state;
} LEDControl_t;

void LEDCallback(void *arg) {
    LEDControl_t *ctrl = (LEDControl_t*)arg;
    LED_Set(ctrl->led_id, ctrl->state);
}

// 使用示例
LEDControl_t led_ctrl = {.led_id = 1, .state = true};
SoftwareTimer_t *timer = Timer_Create(1000, TIMER_TYPE_ONE_SHOT,
                                      LEDCallback, &led_ctrl, "LED1");
```

#### 2. 中断安全性

回调函数在中断上下文中执行，需要注意：

```c
// 不安全的回调（可能阻塞）
void BadCallback(void *arg) {
    printf("Timer expired\n");  // printf可能很慢
    Delay_ms(100);              // 绝对不能在中断中延时！
}

// 安全的回调（快速返回）
volatile bool timer_flag = false;

void GoodCallback(void *arg) {
    timer_flag = true;  // 只设置标志
}

// 在主循环中处理
void main_loop(void) {
    while(1) {
        if(timer_flag) {
            timer_flag = false;
            // 在这里执行耗时操作
            ProcessTimerEvent();
        }
    }
}
```

#### 3. 延迟执行队列

对于复杂的超时处理，可以使用延迟执行队列：

```c
// 延迟执行队列
#define DEFERRED_QUEUE_SIZE 16

typedef struct {
    TimerCallback_t callback;
    void *arg;
} DeferredTask_t;

DeferredTask_t deferred_queue[DEFERRED_QUEUE_SIZE];
volatile uint8_t queue_write = 0;
volatile uint8_t queue_read = 0;

// 在中断中添加到队列
void Timer_DeferredCallback(void *arg) {
    uint8_t next_write = (queue_write + 1) % DEFERRED_QUEUE_SIZE;
    
    if(next_write != queue_read) {
        deferred_queue[queue_write].callback = (TimerCallback_t)arg;
        deferred_queue[queue_write].arg = NULL;
        queue_write = next_write;
    }
}

// 在主循环中处理队列
void Timer_ProcessDeferred(void) {
    while(queue_read != queue_write) {
        DeferredTask_t *task = &deferred_queue[queue_read];
        
        if(task->callback != NULL) {
            task->callback(task->arg);
        }
        
        queue_read = (queue_read + 1) % DEFERRED_QUEUE_SIZE;
    }
}
```

### 周期任务实现

周期定时器是最常用的功能之一：

```c
// 示例1：周期性LED闪烁
void LED_Blink_Callback(void *arg) {
    static bool state = false;
    state = !state;
    LED_Set(state);
}

SoftwareTimer_t *blink_timer = Timer_Create(
    500,                    // 500ms周期
    TIMER_TYPE_PERIODIC,    // 周期定时器
    LED_Blink_Callback,
    NULL,
    "Blink"
);
Timer_Start(blink_timer);

// 示例2：周期性数据采集
typedef struct {
    uint16_t *buffer;
    uint8_t index;
    uint8_t size;
} SampleBuffer_t;

void Sample_Callback(void *arg) {
    SampleBuffer_t *buf = (SampleBuffer_t*)arg;
    
    // 读取ADC
    buf->buffer[buf->index] = ADC_Read();
    buf->index = (buf->index + 1) % buf->size;
}

uint16_t sample_buffer[100];
SampleBuffer_t sample_buf = {
    .buffer = sample_buffer,
    .index = 0,
    .size = 100
};

SoftwareTimer_t *sample_timer = Timer_Create(
    10,                     // 10ms采样周期
    TIMER_TYPE_PERIODIC,
    Sample_Callback,
    &sample_buf,
    "Sample"
);
Timer_Start(sample_timer);

// 示例3：看门狗喂狗
void Watchdog_Feed_Callback(void *arg) {
    Watchdog_Refresh();
}

SoftwareTimer_t *wdt_timer = Timer_Create(
    500,                    // 每500ms喂狗
    TIMER_TYPE_PERIODIC,
    Watchdog_Feed_Callback,
    NULL,
    "Watchdog"
);
Timer_Start(wdt_timer);
```

### 精度优化

软件定时器的精度受多种因素影响：

#### 1. 时基精度

```c
// 使用高精度时基
// 方法1：使用更快的中断（0.1ms）
void SysTick_Init_HighPrecision(void) {
    // 配置100us中断
    SysTick_Config(SystemCoreClock / 10000);
}

// 定时器使用0.1ms单位
SoftwareTimer_t *timer = Timer_Create(
    5000,  // 500ms = 5000 * 0.1ms
    TIMER_TYPE_PERIODIC,
    Callback,
    NULL,
    "Timer"
);

// 方法2：使用硬件定时器的计数值
uint32_t GetHighResolutionTicks(void) {
    // 读取硬件定时器计数值
    uint32_t ticks = system_ticks;
    uint32_t counter = SysTick->VAL;
    uint32_t reload = SysTick->LOAD;
    
    // 计算精确时间（微秒）
    return ticks * 1000 + (reload - counter) * 1000 / reload;
}
```

#### 2. 中断延迟补偿

```c
// 记录上次更新时间
volatile uint32_t last_update_time = 0;

void Timer_UpdateList_Compensated(void) {
    uint32_t current_time = system_ticks;
    uint32_t elapsed = current_time - last_update_time;
    last_update_time = current_time;
    
    // 如果中断延迟，elapsed可能大于1
    SoftwareTimer_t *current = active_timer_list;
    
    while(current != NULL) {
        if(current->remaining > elapsed) {
            current->remaining -= elapsed;
        } else {
            current->remaining = 0;
        }
        
        // 处理超时...
        current = current->next;
    }
}
```

#### 3. 累积误差处理

```c
// 使用绝对时间而不是相对时间
typedef struct {
    uint32_t start_time;    // 启动时的系统时间
    uint32_t timeout;       // 超时时间
    // ... 其他字段
} SoftwareTimer_Absolute_t;

void Timer_Start_Absolute(SoftwareTimer_Absolute_t *timer) {
    timer->start_time = system_ticks;
    timer->state = TIMER_STATE_RUNNING;
}

void Timer_Update_Absolute(void) {
    SoftwareTimer_Absolute_t *current = active_timer_list;
    
    while(current != NULL) {
        uint32_t elapsed = system_ticks - current->start_time;
        
        if(elapsed >= current->timeout) {
            // 超时处理
            if(current->callback != NULL) {
                current->callback(current->callback_arg);
            }
            
            if(current->type == TIMER_TYPE_PERIODIC) {
                // 使用绝对时间，避免累积误差
                current->start_time += current->timeout;
            }
        }
        
        current = current->next;
    }
}
```

## 实践示例

### 示例1：多功能定时器系统

实现一个包含多种定时功能的完整系统：

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// 全局变量
volatile uint32_t system_ticks = 0;
SoftwareTimer_t *active_timer_list = NULL;

// SysTick中断
void SysTick_Handler(void) {
    system_ticks++;
    Timer_UpdateList();
}

// 任务1：LED闪烁（500ms周期）
void LED_Blink_Callback(void *arg) {
    static bool state = false;
    state = !state;
    LED_Set(state);
    printf("[%lu] LED: %s\n", system_ticks, state ? "ON" : "OFF");
}

// 任务2：按键消抖（20ms单次）
typedef struct {
    uint8_t button_id;
    bool pressed;
} ButtonEvent_t;

ButtonEvent_t button_event;
SoftwareTimer_t *debounce_timer = NULL;

void Button_Debounce_Callback(void *arg) {
    ButtonEvent_t *event = (ButtonEvent_t*)arg;
    
    // 再次检查按键状态
    if(Button_Read(event->button_id) == event->pressed) {
        // 状态确认，处理按键事件
        if(event->pressed) {
            printf("[%lu] Button %d pressed\n", system_ticks, event->button_id);
            OnButtonPressed(event->button_id);
        } else {
            printf("[%lu] Button %d released\n", system_ticks, event->button_id);
        }
    }
}

void Button_IRQ_Handler(uint8_t button_id, bool pressed) {
    // 停止之前的消抖定时器
    if(debounce_timer != NULL) {
        Timer_Stop(debounce_timer);
    }
    
    // 记录按键事件
    button_event.button_id = button_id;
    button_event.pressed = pressed;
    
    // 启动消抖定时器
    if(debounce_timer == NULL) {
        debounce_timer = Timer_Create(20, TIMER_TYPE_ONE_SHOT,
                                      Button_Debounce_Callback,
                                      &button_event, "Debounce");
    }
    Timer_Start(debounce_timer);
}

// 任务3：传感器读取（1000ms周期）
void Sensor_Read_Callback(void *arg) {
    uint16_t temperature = ReadTemperature();
    uint16_t humidity = ReadHumidity();
    
    printf("[%lu] Temp: %u.%u°C, Humidity: %u%%\n",
           system_ticks,
           temperature / 10, temperature % 10,
           humidity);
}

// 任务4：数据上传（5000ms周期）
void Data_Upload_Callback(void *arg) {
    printf("[%lu] Uploading data...\n", system_ticks);
    
    // 模拟数据上传
    if(Network_IsConnected()) {
        UploadSensorData();
        printf("[%lu] Upload complete\n", system_ticks);
    } else {
        printf("[%lu] Network not available\n", system_ticks);
    }
}

// 任务5：超时保护（10000ms单次）
void Timeout_Callback(void *arg) {
    printf("[%lu] Operation timeout!\n", system_ticks);
    CancelOperation();
}

// 主函数
int main(void) {
    // 硬件初始化
    SystemInit();
    LED_Init();
    Button_Init();
    Sensor_Init();
    Network_Init();
    SysTick_Init();
    
    printf("Software Timer System Started\n");
    
    // 创建周期定时器
    SoftwareTimer_t *led_timer = Timer_Create(
        500, TIMER_TYPE_PERIODIC,
        LED_Blink_Callback, NULL, "LED"
    );
    
    SoftwareTimer_t *sensor_timer = Timer_Create(
        1000, TIMER_TYPE_PERIODIC,
        Sensor_Read_Callback, NULL, "Sensor"
    );
    
    SoftwareTimer_t *upload_timer = Timer_Create(
        5000, TIMER_TYPE_PERIODIC,
        Data_Upload_Callback, NULL, "Upload"
    );
    
    // 启动定时器
    Timer_Start(led_timer);
    Timer_Start(sensor_timer);
    Timer_Start(upload_timer);
    
    // 主循环
    while(1) {
        // 处理延迟任务
        Timer_ProcessDeferred();
        
        // 其他任务
        __WFI();  // 等待中断
    }
    
    return 0;
}
```


### 示例2：状态机超时控制

使用定时器控制状态机的超时：

```c
#include <stdint.h>
#include <stdbool.h>

// 通信状态机
typedef enum {
    COMM_STATE_IDLE,
    COMM_STATE_SENDING,
    COMM_STATE_WAITING_ACK,
    COMM_STATE_TIMEOUT,
    COMM_STATE_ERROR
} CommState_t;

typedef struct {
    CommState_t state;
    uint8_t retry_count;
    uint8_t *data;
    uint16_t data_len;
    SoftwareTimer_t *timeout_timer;
} CommContext_t;

CommContext_t comm_ctx = {0};

// 超时回调
void Comm_Timeout_Callback(void *arg) {
    CommContext_t *ctx = (CommContext_t*)arg;
    
    printf("Communication timeout in state %d\n", ctx->state);
    
    if(ctx->retry_count < 3) {
        // 重试
        ctx->retry_count++;
        printf("Retry %d/3\n", ctx->retry_count);
        
        // 重新发送
        ctx->state = COMM_STATE_SENDING;
        SendData(ctx->data, ctx->data_len);
        
        // 重启超时定时器
        Timer_Start(ctx->timeout_timer);
    } else {
        // 超过重试次数
        ctx->state = COMM_STATE_TIMEOUT;
        printf("Communication failed after 3 retries\n");
    }
}

// 发送数据
bool Comm_SendData(uint8_t *data, uint16_t len) {
    if(comm_ctx.state != COMM_STATE_IDLE) {
        return false;  // 忙碌
    }
    
    // 保存数据
    comm_ctx.data = data;
    comm_ctx.data_len = len;
    comm_ctx.retry_count = 0;
    
    // 创建超时定时器（如果还没有）
    if(comm_ctx.timeout_timer == NULL) {
        comm_ctx.timeout_timer = Timer_Create(
            1000,  // 1秒超时
            TIMER_TYPE_ONE_SHOT,
            Comm_Timeout_Callback,
            &comm_ctx,
            "CommTimeout"
        );
    }
    
    // 发送数据
    comm_ctx.state = COMM_STATE_SENDING;
    SendData(data, len);
    
    // 启动超时定时器
    comm_ctx.state = COMM_STATE_WAITING_ACK;
    Timer_Start(comm_ctx.timeout_timer);
    
    return true;
}

// 接收到ACK
void Comm_OnAckReceived(void) {
    if(comm_ctx.state == COMM_STATE_WAITING_ACK) {
        // 停止超时定时器
        Timer_Stop(comm_ctx.timeout_timer);
        
        // 通信成功
        comm_ctx.state = COMM_STATE_IDLE;
        printf("Communication successful\n");
    }
}

// 使用示例
void Example_StateMachine(void) {
    uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
    
    if(Comm_SendData(data, sizeof(data))) {
        printf("Data sent, waiting for ACK...\n");
    }
    
    // 在主循环或中断中调用
    // Comm_OnAckReceived();  // 收到ACK时调用
}
```

### 示例3：定时器组管理

管理一组相关的定时器：

```c
// 定时器组
typedef struct {
    SoftwareTimer_t *timers[10];
    uint8_t count;
    char group_name[16];
} TimerGroup_t;

// 创建定时器组
TimerGroup_t* TimerGroup_Create(const char *name) {
    TimerGroup_t *group = (TimerGroup_t*)malloc(sizeof(TimerGroup_t));
    if(group != NULL) {
        group->count = 0;
        strncpy(group->group_name, name, sizeof(group->group_name) - 1);
    }
    return group;
}

// 添加定时器到组
bool TimerGroup_Add(TimerGroup_t *group, SoftwareTimer_t *timer) {
    if(group == NULL || timer == NULL || group->count >= 10) {
        return false;
    }
    
    group->timers[group->count++] = timer;
    return true;
}

// 启动组内所有定时器
void TimerGroup_StartAll(TimerGroup_t *group) {
    if(group == NULL) return;
    
    for(uint8_t i = 0; i < group->count; i++) {
        Timer_Start(group->timers[i]);
    }
    printf("Started %d timers in group '%s'\n", 
           group->count, group->group_name);
}

// 停止组内所有定时器
void TimerGroup_StopAll(TimerGroup_t *group) {
    if(group == NULL) return;
    
    for(uint8_t i = 0; i < group->count; i++) {
        Timer_Stop(group->timers[i]);
    }
    printf("Stopped %d timers in group '%s'\n",
           group->count, group->group_name);
}

// 使用示例：传感器采集组
void Example_TimerGroup(void) {
    // 创建传感器组
    TimerGroup_t *sensor_group = TimerGroup_Create("Sensors");
    
    // 创建多个传感器定时器
    SoftwareTimer_t *temp_timer = Timer_Create(
        1000, TIMER_TYPE_PERIODIC,
        ReadTemperature_Callback, NULL, "Temp"
    );
    
    SoftwareTimer_t *humidity_timer = Timer_Create(
        1000, TIMER_TYPE_PERIODIC,
        ReadHumidity_Callback, NULL, "Humidity"
    );
    
    SoftwareTimer_t *pressure_timer = Timer_Create(
        1000, TIMER_TYPE_PERIODIC,
        ReadPressure_Callback, NULL, "Pressure"
    );
    
    // 添加到组
    TimerGroup_Add(sensor_group, temp_timer);
    TimerGroup_Add(sensor_group, humidity_timer);
    TimerGroup_Add(sensor_group, pressure_timer);
    
    // 统一启动
    TimerGroup_StartAll(sensor_group);
    
    // 需要时统一停止
    // TimerGroup_StopAll(sensor_group);
}
```

## 深入理解

### 内存管理策略

软件定时器的内存管理有多种方式：

#### 1. 静态分配（内存池）

```c
#define TIMER_POOL_SIZE 20

SoftwareTimer_t timer_pool[TIMER_POOL_SIZE];
bool timer_used[TIMER_POOL_SIZE] = {false};

SoftwareTimer_t* Timer_Alloc(void) {
    for(uint8_t i = 0; i < TIMER_POOL_SIZE; i++) {
        if(!timer_used[i]) {
            timer_used[i] = true;
            memset(&timer_pool[i], 0, sizeof(SoftwareTimer_t));
            return &timer_pool[i];
        }
    }
    return NULL;  // 池已满
}

void Timer_Free(SoftwareTimer_t *timer) {
    for(uint8_t i = 0; i < TIMER_POOL_SIZE; i++) {
        if(&timer_pool[i] == timer) {
            timer_used[i] = false;
            break;
        }
    }
}
```

**优点**：
- 无内存碎片
- 分配速度快
- 适合实时系统

**缺点**：
- 内存占用固定
- 可能浪费内存

#### 2. 动态分配

```c
SoftwareTimer_t* Timer_Alloc(void) {
    return (SoftwareTimer_t*)malloc(sizeof(SoftwareTimer_t));
}

void Timer_Free(SoftwareTimer_t *timer) {
    free(timer);
}
```

**优点**：
- 内存按需分配
- 灵活性高

**缺点**：
- 可能有内存碎片
- 分配速度较慢
- 不适合实时系统

### 性能分析

#### 1. 时间复杂度

不同实现方式的时间复杂度：

| 实现方式 | 插入 | 删除 | 更新 |
|---------|------|------|------|
| 数组遍历 | O(1) | O(n) | O(n) |
| 无序链表 | O(1) | O(n) | O(n) |
| 有序链表 | O(n) | O(n) | O(1) |
| 时间轮 | O(1) | O(1) | O(1) |

**时间轮算法**（高级）：
```c
// 时间轮：将时间分成多个槽位
#define WHEEL_SIZE 256
#define WHEEL_MASK (WHEEL_SIZE - 1)

SoftwareTimer_t *time_wheel[WHEEL_SIZE];
uint8_t current_slot = 0;

void Timer_Start_Wheel(SoftwareTimer_t *timer) {
    uint8_t slot = (current_slot + timer->timeout) & WHEEL_MASK;
    
    // 插入到对应槽位
    timer->next = time_wheel[slot];
    time_wheel[slot] = timer;
}

void Timer_Update_Wheel(void) {
    current_slot = (current_slot + 1) & WHEEL_MASK;
    
    // 只处理当前槽位的定时器
    SoftwareTimer_t *timer = time_wheel[current_slot];
    time_wheel[current_slot] = NULL;
    
    while(timer != NULL) {
        SoftwareTimer_t *next = timer->next;
        
        // 执行回调
        if(timer->callback != NULL) {
            timer->callback(timer->callback_arg);
        }
        
        // 处理周期定时器
        if(timer->type == TIMER_TYPE_PERIODIC) {
            Timer_Start_Wheel(timer);
        }
        
        timer = next;
    }
}
```

#### 2. 内存占用

```c
// 计算内存占用
size_t Timer_GetMemoryUsage(void) {
    size_t total = 0;
    
    // 定时器结构体大小
    total += sizeof(SoftwareTimer_t) * timer_count;
    
    // 链表指针开销
    total += sizeof(void*) * timer_count;
    
    return total;
}

// 打印内存统计
void Timer_PrintMemoryStats(void) {
    printf("Timer Memory Usage:\n");
    printf("  Timer count: %u\n", timer_count);
    printf("  Size per timer: %u bytes\n", sizeof(SoftwareTimer_t));
    printf("  Total memory: %u bytes\n", Timer_GetMemoryUsage());
}
```

### 常见陷阱和最佳实践

#### 陷阱1：回调函数中操作定时器

**错误示例**：
```c
void BadCallback(void *arg) {
    SoftwareTimer_t *timer = (SoftwareTimer_t*)arg;
    
    // 危险：在回调中删除自己
    Timer_Delete(timer);  // 可能导致链表损坏
}
```

**正确做法**：
```c
// 方法1：标记删除，延迟处理
volatile bool timer_delete_pending = false;
SoftwareTimer_t *timer_to_delete = NULL;

void GoodCallback(void *arg) {
    timer_to_delete = (SoftwareTimer_t*)arg;
    timer_delete_pending = true;
}

void main_loop(void) {
    if(timer_delete_pending) {
        timer_delete_pending = false;
        Timer_Delete(timer_to_delete);
    }
}

// 方法2：使用单次定时器，自动删除
SoftwareTimer_t *timer = Timer_Create(
    1000,
    TIMER_TYPE_ONE_SHOT,  // 单次定时器会自动停止
    Callback,
    NULL,
    "OneShot"
);
```

#### 陷阱2：定时器精度问题

**问题**：
```c
// 期望每1000ms执行一次
// 但实际可能是1000ms + 回调执行时间
void SlowCallback(void *arg) {
    ProcessData();  // 可能需要50ms
}
```

**解决方案**：
```c
// 使用绝对时间
typedef struct {
    uint32_t next_trigger_time;
    uint32_t period;
} AccurateTimer_t;

void AccurateCallback(void *arg) {
    AccurateTimer_t *timer = (AccurateTimer_t*)arg;
    
    // 计算下次触发时间（基于绝对时间）
    timer->next_trigger_time += timer->period;
    
    // 执行任务
    ProcessData();
}
```

#### 陷阱3：定时器泄漏

**问题**：
```c
void CreateTimer(void) {
    // 每次调用都创建新定时器，但从不删除
    SoftwareTimer_t *timer = Timer_Create(...);
    Timer_Start(timer);
    // 忘记保存timer指针，无法删除
}
```

**解决方案**：
```c
// 方法1：使用全局变量或静态变量
static SoftwareTimer_t *my_timer = NULL;

void CreateTimer(void) {
    if(my_timer == NULL) {
        my_timer = Timer_Create(...);
    }
    Timer_Start(my_timer);
}

// 方法2：使用定时器池
SoftwareTimer_t* GetOrCreateTimer(const char *name) {
    // 先查找是否已存在
    SoftwareTimer_t *timer = Timer_FindByName(name);
    if(timer == NULL) {
        timer = Timer_Create(...);
    }
    return timer;
}
```

#### 最佳实践

1. **回调函数设计**：
   - 保持回调函数简短快速
   - 避免在回调中阻塞或延时
   - 使用标志位通知主循环

2. **定时器生命周期**：
   - 明确定时器的创建和销毁时机
   - 使用静态分配避免内存泄漏
   - 单次定时器用完即删除

3. **精度要求**：
   - 根据需求选择合适的时基
   - 关键任务使用硬件定时器
   - 非关键任务使用软件定时器

4. **资源管理**：
   - 限制定时器数量
   - 监控内存使用
   - 定期检查定时器状态

5. **调试支持**：
   - 为定时器命名
   - 记录创建和销毁
   - 提供统计信息接口


## 常见问题

### Q1: 软件定时器和硬件定时器有什么区别？

**A**: 主要区别在于实现方式和资源占用：

**硬件定时器**：
- 由硬件电路实现，独立于CPU运行
- 精度高，不受软件影响
- 数量有限（通常2-4个）
- 配置复杂，需要设置寄存器
- 适合高精度、实时性要求高的场景

**软件定时器**：
- 由软件实现，依赖硬件时基
- 精度受软件影响（中断延迟、回调执行时间）
- 数量灵活，可以创建很多个
- 使用简单，接口统一
- 适合一般精度要求的场景

**选择建议**：
- PWM输出、精确延时 → 使用硬件定时器
- LED闪烁、周期任务 → 使用软件定时器
- 系统时基 → 使用硬件定时器（SysTick）
- 超时保护、状态机 → 使用软件定时器

### Q2: 如何选择合适的时基频率？

**A**: 时基频率的选择需要权衡精度和开销：

**常用时基频率**：
- **1ms（1kHz）**：最常用，适合大多数场景
- **100us（10kHz）**：高精度场景
- **10ms（100Hz）**：低功耗场景

**选择依据**：

1. **精度要求**：
   - 如果最小定时单位是10ms，时基可以是1ms
   - 如果需要1ms精度，时基应该是100us或更快

2. **中断开销**：
   - 时基越快，中断越频繁
   - 中断开销 = 中断频率 × 单次中断时间
   - 建议中断开销 < 5% CPU时间

3. **定时器数量**：
   - 定时器越多，每次中断处理时间越长
   - 需要确保能在下次中断前处理完

**计算公式**：
```
最大中断处理时间 = 1 / 时基频率
例如：1ms时基 → 最大处理时间 = 1ms
```

**示例**：
```c
// 场景1：10个定时器，每个处理10us
// 总处理时间 = 10 × 10us = 100us
// 可以使用1ms时基（1000us > 100us）

// 场景2：50个定时器，每个处理10us
// 总处理时间 = 50 × 10us = 500us
// 1ms时基可能不够，考虑优化或使用10ms时基
```

### Q3: 定时器回调函数可以做什么？

**A**: 回调函数应该遵循以下原则：

**可以做的**：
```c
void GoodCallback(void *arg) {
    // 1. 设置标志位
    flag = true;
    
    // 2. 简单的GPIO操作
    LED_Toggle();
    
    // 3. 读取硬件寄存器
    uint16_t value = ADC->DR;
    
    // 4. 写入缓冲区
    buffer[index++] = value;
    
    // 5. 启动/停止其他定时器
    Timer_Start(another_timer);
}
```

**不能做的**：
```c
void BadCallback(void *arg) {
    // 1. 延时函数
    Delay_ms(100);  // 绝对禁止！
    
    // 2. 阻塞等待
    while(!DataReady());  // 会卡死系统
    
    // 3. 复杂计算
    float result = ComplexCalculation();  // 太慢
    
    // 4. 打印输出
    printf("Timer expired\n");  // printf很慢
    
    // 5. 动态内存分配
    void *ptr = malloc(100);  // 不安全
}
```

**推荐模式**：
```c
// 在回调中设置标志，在主循环中处理
volatile bool timer_event = false;

void TimerCallback(void *arg) {
    timer_event = true;  // 只设置标志
}

void main_loop(void) {
    while(1) {
        if(timer_event) {
            timer_event = false;
            
            // 在这里执行复杂操作
            ProcessTimerEvent();
        }
    }
}
```

### Q4: 如何调试软件定时器？

**A**: 常用的调试方法：

1. **添加调试输出**：
```c
void Timer_Start_Debug(SoftwareTimer_t *timer) {
    printf("[DEBUG] Start timer '%s', timeout=%lu ms\n",
           timer->name, timer->timeout);
    Timer_Start(timer);
}

void Timer_Callback_Debug(void *arg) {
    SoftwareTimer_t *timer = (SoftwareTimer_t*)arg;
    printf("[DEBUG] Timer '%s' expired at %lu ms\n",
           timer->name, system_ticks);
    
    // 原始回调
    if(timer->callback != NULL) {
        timer->callback(timer->callback_arg);
    }
}
```

2. **使用GPIO跟踪**：
```c
void TimerCallback(void *arg) {
    GPIO_Set(DEBUG_PIN);  // 回调开始
    
    // 执行任务
    DoWork();
    
    GPIO_Clear(DEBUG_PIN);  // 回调结束
}
// 使用逻辑分析仪观察DEBUG_PIN
```

3. **统计信息**：
```c
typedef struct {
    uint32_t callback_count;
    uint32_t max_callback_time;
    uint32_t total_callback_time;
} TimerStats_t;

TimerStats_t timer_stats[MAX_TIMERS];

void Timer_Callback_Wrapper(void *arg) {
    uint32_t start = GetCycleCount();
    
    // 执行回调
    timer->callback(timer->callback_arg);
    
    uint32_t end = GetCycleCount();
    uint32_t elapsed = end - start;
    
    // 更新统计
    timer_stats[timer_id].callback_count++;
    timer_stats[timer_id].total_callback_time += elapsed;
    if(elapsed > timer_stats[timer_id].max_callback_time) {
        timer_stats[timer_id].max_callback_time = elapsed;
    }
}
```

4. **断言检查**：
```c
void Timer_Update(void) {
    // 检查是否有定时器超时太久
    for(uint8_t i = 0; i < timer_count; i++) {
        if(timer_pool[i].state == TIMER_STATE_EXPIRED) {
            uint32_t overdue = system_ticks - timer_pool[i].expire_time;
            ASSERT(overdue < 10);  // 超时不应超过10ms
        }
    }
}
```

### Q5: 软件定时器会影响系统性能吗？

**A**: 会有一定影响，但可以优化：

**性能影响因素**：

1. **中断频率**：
   - 1ms时基 → 每秒1000次中断
   - 每次中断有进入/退出开销（几微秒）

2. **定时器数量**：
   - 每个定时器需要检查和更新
   - 数量越多，处理时间越长

3. **回调执行时间**：
   - 回调在中断中执行
   - 会阻塞其他中断

**性能测量**：
```c
void MeasureTimerOverhead(void) {
    uint32_t start, end;
    
    // 测量更新时间
    start = GetCycleCount();
    Timer_Update();
    end = GetCycleCount();
    
    uint32_t cycles = end - start;
    float time_us = (float)cycles / CPU_FREQ_MHZ;
    float overhead = time_us / 1000.0f * 100.0f;  // 占1ms的百分比
    
    printf("Timer update: %.2f us (%.1f%% of 1ms)\n", time_us, overhead);
}
```

**优化方法**：

1. **使用有序链表**：
   - 只检查最近要超时的定时器
   - 减少不必要的检查

2. **延迟回调执行**：
   - 在中断中只设置标志
   - 在主循环中执行回调

3. **减少定时器数量**：
   - 合并相似的定时器
   - 使用状态机代替多个定时器

4. **选择合适的时基**：
   - 不需要高精度时使用较慢的时基
   - 减少中断频率

**性能基准**：
- 良好：定时器开销 < 5% CPU时间
- 可接受：定时器开销 < 10% CPU时间
- 需要优化：定时器开销 > 10% CPU时间

## 总结

软件定时器是嵌入式系统中非常实用的组件，它让我们能够灵活地管理多个定时任务：

**核心要点**：
- **数据结构**：使用结构体存储定时器信息，链表管理多个定时器
- **时基更新**：依赖硬件定时器提供1ms时基
- **超时处理**：检测超时并执行回调函数
- **周期任务**：支持单次和周期两种模式
- **精度优化**：使用绝对时间、补偿中断延迟

**适用场景**：
- LED闪烁、按键消抖
- 周期性数据采集
- 超时保护、看门狗
- 状态机超时控制
- 延迟任务执行

**优势**：
- 使用简单，接口统一
- 数量灵活，可创建多个
- 资源占用小（每个定时器约50字节）
- 易于维护和调试

**局限**：
- 精度受软件影响
- 回调在中断中执行，需要快速返回
- 不适合微秒级精度要求
- 定时器过多会影响性能

**下一步学习**：
- 如果需要更复杂的数据管理，学习环形缓冲区
- 如果需要更好的任务调度，学习协作式调度器
- 如果需要更强大的功能，学习RTOS定时器
- 如果需要高精度定时，学习硬件定时器编程

## 延伸阅读

推荐进一步学习的资源：

- [环形缓冲区设计与实现](06-ring-buffer.html) - 学习高效的数据缓冲技术
- [协作式多任务调度器实现](../intermediate/01-cooperative-scheduler.html) - 构建完整的任务调度系统
- [RTOS软件定时器使用](../../02-rtos-fundamentals/beginner/08-rtos-timer.html) - 了解专业RTOS的定时器实现
- [时间片轮询调度算法](04-time-slice-scheduling.html) - 理解任务调度的基础

## 参考资料

1. "Embedded Systems Architecture" - Tammy Noergaard
2. "Making Embedded Systems" - Elecia White
3. "Real-Time Concepts for Embedded Systems" - Qing Li
4. FreeRTOS Software Timer Documentation

---

**练习题**：

1. 实现一个基于数组的软件定时器系统，支持5个定时器
2. 为定时器系统添加暂停和恢复功能
3. 实现一个基于链表的定时器系统，支持动态创建和删除
4. 使用软件定时器实现一个按键消抖功能
5. 测量你的定时器系统的性能开销，并尝试优化

**实践项目**：

设计一个完整的定时器管理系统，包含以下功能：
- 支持单次和周期定时器
- 使用链表管理定时器
- 提供创建、启动、停止、删除接口
- 实现定时器统计和调试功能
- 编写测试程序验证功能

**下一步**：建议学习 [环形缓冲区设计与实现](06-ring-buffer.html)，掌握另一个重要的数据结构。
