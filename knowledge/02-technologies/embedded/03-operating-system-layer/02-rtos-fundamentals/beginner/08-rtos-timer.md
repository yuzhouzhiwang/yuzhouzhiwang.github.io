---
title: "RTOS软件定时器使用：实现灵活的定时任务管理"
description: "深入学习RTOS软件定时器的核心概念和实践应用。掌握软件定时器创建、单次/周期定时、回调函数、定时器管理和应用场景，通过丰富的代码示例学会构建高效的定时任务系统。"
slug: "rtos-timer"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 软件定时器
  - 定时任务
  - 回调
  - FreeRTOS
  - 周期定时
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/06-message-queue.md"
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/01-rtos-memory.md"

# 学习信息
estimated_time: 55
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
  - RTOS软件定时器
  - 定时任务
  - FreeRTOS定时器
  - 回调函数
  - 周期定时器
  - 单次定时器
cover_image: ""
---


# RTOS软件定时器使用：实现灵活的定时任务管理

## 学习目标

完成本教程后，你将能够：

- 理解RTOS软件定时器的概念和工作原理
- 掌握软件定时器的创建和管理方法
- 学会使用单次和周期定时器
- 理解定时器回调函数的使用规则
- 掌握定时器在不同场景下的应用
- 能够解决常见的定时器使用问题


## 前置要求

### 知识要求

- 理解RTOS的基本概念
- 掌握任务创建和管理
- 了解任务调度机制
- 理解中断和任务的区别

### 技能要求

- 能够创建和管理RTOS任务
- 了解任务状态和状态转换
- 理解任务优先级的作用
- 掌握基本的同步机制

### 环境要求

- STM32开发板（或其他支持FreeRTOS的开发板）
- STM32CubeIDE或Keil MDK开发环境
- FreeRTOS源码或HAL库
- 串口调试工具

## 准备工作

### 硬件准备

| 硬件 | 数量 | 说明 |
|------|------|------|
| STM32开发板 | 1 | 如STM32F407、STM32F103等 |
| USB数据线 | 1 | 用于下载和供电 |
| LED灯 | 2-3个 | 用于状态指示（可选） |

### 软件准备

1. **安装开发环境**
   - STM32CubeIDE v1.10或更高版本
   - 或Keil MDK v5.30或更高版本

2. **配置FreeRTOS**
   - 在STM32CubeMX中启用FreeRTOS
   - 启用软件定时器功能


3. **配置串口**
   - 配置UART用于调试输出
   - 波特率：115200
   - 数据位：8，停止位：1，无校验

### 环境配置

```c
// FreeRTOSConfig.h 关键配置
#define configUSE_PREEMPTION                1  // 启用抢占式调度
#define configUSE_TIMERS                    1  // 启用软件定时器
#define configTIMER_TASK_PRIORITY           3  // 定时器任务优先级
#define configTIMER_QUEUE_LENGTH            10 // 定时器命令队列长度
#define configTIMER_TASK_STACK_DEPTH        256 // 定时器任务堆栈大小
#define configTICK_RATE_HZ                  1000  // 时钟节拍频率
```


## 概述

### 什么是RTOS软件定时器？

**RTOS软件定时器**是RTOS提供的一种定时机制，允许在指定时间后执行回调函数，而不需要创建专门的任务。

**生活中的类比**：

想象一个智能厨房定时器：
- 可以设置多个定时提醒（多个定时器）
- 有单次提醒（煮鸡蛋15分钟）
- 有重复提醒（每小时检查烤箱）
- 时间到了会响铃（回调函数）
- 不需要专人盯着（不占用任务资源）

### 为什么需要软件定时器？

在RTOS系统中，我们经常需要定时执行某些操作：

**问题场景：使用任务实现定时**
```c
// 方法1：使用任务+延时（不推荐）
void LED_Task(void *param) {
    while(1) {
        LED_Toggle();
        vTaskDelay(pdMS_TO_TICKS(500));  // 占用一个任务
    }
}

void Sensor_Task(void *param) {
    while(1) {
        ReadSensor();
        vTaskDelay(pdMS_TO_TICKS(1000));  // 又占用一个任务
    }
}

// 需要创建多个任务，每个任务占用堆栈内存
```

**使用软件定时器的优势**：
```c
// 方法2：使用软件定时器（推荐）
void LED_Timer_Callback(TimerHandle_t xTimer) {
    LED_Toggle();
}

void Sensor_Timer_Callback(TimerHandle_t xTimer) {
    ReadSensor();
}

// 只需要创建定时器，不需要额外的任务
// 节省内存，代码更简洁
```


### 软件定时器 vs 任务延时

| 特性 | 软件定时器 | 任务延时 |
|------|-----------|---------|
| **内存占用** | 小（只有定时器结构） | 大（需要任务堆栈） |
| **创建数量** | 可以很多 | 受任务数量限制 |
| **执行上下文** | 定时器任务 | 独立任务 |
| **适用场景** | 简单的周期性操作 | 复杂的任务逻辑 |
| **资源消耗** | 低 | 高 |

**选择建议**：
- 简单的定时操作（如LED闪烁、定时读取） → 使用软件定时器
- 复杂的任务逻辑（如数据处理、状态机） → 使用任务


## 核心概念

### 定时器类型

FreeRTOS支持两种类型的软件定时器：

**1. 单次定时器（One-Shot Timer）**
```
启动 → 计时 → 超时 → 执行回调 → 停止

时间轴：
0ms -------- 500ms -------- 1000ms
 |            |              |
启动         (计时中)      超时，执行回调，停止
```

**2. 周期定时器（Periodic Timer）**
```
启动 → 计时 → 超时 → 执行回调 → 重新计时 → 超时 → ...

时间轴：
0ms --- 500ms --- 1000ms --- 1500ms --- 2000ms
 |       |         |          |          |
启动    回调      回调       回调       回调
```

### 定时器工作原理

软件定时器的工作机制：

```
[用户任务] → 创建/启动定时器 → [定时器命令队列]
                                      ↓
                              [定时器服务任务]
                                      ↓
                              管理所有定时器
                                      ↓
                              检查超时 → 执行回调函数
```

**关键组件**：
- **定时器服务任务**：专门管理所有软件定时器的任务
- **定时器命令队列**：用于接收定时器操作命令
- **回调函数**：定时器超时时执行的函数

**重要特性**：
- 所有定时器回调函数在定时器服务任务中执行
- 回调函数不能阻塞或长时间运行
- 定时器服务任务优先级通常较高

### 定时器状态

定时器有两种状态：

```
[休眠状态] ←→ [运行状态]
  (Dormant)     (Running)
      ↑             ↓
   停止/删除    启动/重启
```

**状态说明**：
- **休眠状态**：定时器已创建但未启动，或已停止
- **运行状态**：定时器正在计时，会在超时后执行回调


## 基本操作

### 创建定时器

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

// 定时器回调函数
void Timer_Callback(TimerHandle_t xTimer) {
    printf("Timer expired!\n");
}

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 创建单次定时器
    TimerHandle_t one_shot_timer = xTimerCreate(
        "OneShot",              // 定时器名称
        pdMS_TO_TICKS(1000),    // 定时周期（1000ms）
        pdFALSE,                // 单次定时器
        (void *)0,              // 定时器ID
        Timer_Callback          // 回调函数
    );
    
    // 创建周期定时器
    TimerHandle_t periodic_timer = xTimerCreate(
        "Periodic",             // 定时器名称
        pdMS_TO_TICKS(500),     // 定时周期（500ms）
        pdTRUE,                 // 周期定时器
        (void *)1,              // 定时器ID
        Timer_Callback          // 回调函数
    );
    
    if(one_shot_timer != NULL && periodic_timer != NULL) {
        printf("Timers created successfully\n");
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    } else {
        printf("Failed to create timers\n");
    }
    
    while(1);
}
```

**参数说明**：
- **pcTimerName**：定时器名称，用于调试
- **xTimerPeriod**：定时周期，单位为tick
- **uxAutoReload**：pdTRUE为周期定时器，pdFALSE为单次定时器
- **pvTimerID**：定时器ID，可用于区分不同定时器
- **pxCallbackFunction**：超时时调用的回调函数

### 启动定时器

```c
// 启动定时器
BaseType_t xTimerStart(
    TimerHandle_t xTimer,
    TickType_t xBlockTime  // 命令队列满时的等待时间
);

// 示例：启动定时器
if(xTimerStart(one_shot_timer, 0) == pdPASS) {
    printf("Timer started\n");
} else {
    printf("Failed to start timer\n");
}

// 从中断中启动定时器
BaseType_t xTimerStartFromISR(
    TimerHandle_t xTimer,
    BaseType_t *pxHigherPriorityTaskWoken
);

// 中断服务函数示例
void Button_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 启动定时器
    xTimerStartFromISR(debounce_timer, &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```


### 停止定时器

```c
// 停止定时器
BaseType_t xTimerStop(
    TimerHandle_t xTimer,
    TickType_t xBlockTime
);

// 示例
if(xTimerStop(periodic_timer, 0) == pdPASS) {
    printf("Timer stopped\n");
}

// 从中断中停止定时器
BaseType_t xTimerStopFromISR(
    TimerHandle_t xTimer,
    BaseType_t *pxHigherPriorityTaskWoken
);
```

### 重置定时器

```c
// 重置定时器（重新开始计时）
BaseType_t xTimerReset(
    TimerHandle_t xTimer,
    TickType_t xBlockTime
);

// 示例：看门狗喂狗
void Watchdog_Feed(void) {
    // 重置看门狗定时器
    xTimerReset(watchdog_timer, 0);
}

// 从中断中重置定时器
BaseType_t xTimerResetFromISR(
    TimerHandle_t xTimer,
    BaseType_t *pxHigherPriorityTaskWoken
);
```

### 修改定时器周期

```c
// 修改定时器周期
BaseType_t xTimerChangePeriod(
    TimerHandle_t xTimer,
    TickType_t xNewPeriod,
    TickType_t xBlockTime
);

// 示例：动态调整LED闪烁速度
void SetBlinkSpeed(uint32_t period_ms) {
    xTimerChangePeriod(led_timer, pdMS_TO_TICKS(period_ms), 0);
}

// 从中断中修改周期
BaseType_t xTimerChangePeriodFromISR(
    TimerHandle_t xTimer,
    TickType_t xNewPeriod,
    BaseType_t *pxHigherPriorityTaskWoken
);
```

### 删除定时器

```c
// 删除定时器
BaseType_t xTimerDelete(
    TimerHandle_t xTimer,
    TickType_t xBlockTime
);

// 示例
if(xTimerDelete(one_shot_timer, 0) == pdPASS) {
    printf("Timer deleted\n");
}
```

### 查询定时器状态

```c
// 检查定时器是否处于活动状态
BaseType_t xTimerIsTimerActive(TimerHandle_t xTimer);

// 获取定时器名称
const char* pcTimerGetName(TimerHandle_t xTimer);

// 获取定时器周期
TickType_t xTimerGetPeriod(TimerHandle_t xTimer);

// 获取定时器到期时间
TickType_t xTimerGetExpiryTime(TimerHandle_t xTimer);

// 示例
if(xTimerIsTimerActive(led_timer)) {
    printf("Timer '%s' is running\n", pcTimerGetName(led_timer));
    printf("Period: %d ms\n", xTimerGetPeriod(led_timer));
}
```


## 实际应用场景

### 场景1：LED闪烁控制

使用周期定时器实现LED闪烁：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

// LED定时器句柄
TimerHandle_t led_timer;

// LED闪烁回调函数
void LED_Blink_Callback(TimerHandle_t xTimer) {
    static bool led_state = false;
    
    // 切换LED状态
    led_state = !led_state;
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, led_state ? GPIO_PIN_SET : GPIO_PIN_RESET);
    
    printf("[%d] LED: %s\n", xTaskGetTickCount(), led_state ? "ON" : "OFF");
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    
    // 创建LED闪烁定时器（周期500ms）
    led_timer = xTimerCreate(
        "LED_Blink",            // 名称
        pdMS_TO_TICKS(500),     // 500ms周期
        pdTRUE,                 // 周期定时器
        (void *)0,              // ID
        LED_Blink_Callback      // 回调函数
    );
    
    if(led_timer != NULL) {
        // 启动定时器
        xTimerStart(led_timer, 0);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[500] LED: ON
[1000] LED: OFF
[1500] LED: ON
[2000] LED: OFF
[2500] LED: ON
```

### 场景2：按键消抖

使用单次定时器实现按键消抖：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

// 消抖定时器
TimerHandle_t debounce_timer;

// 按键状态
typedef struct {
    uint8_t button_id;
    bool pressed;
} ButtonState_t;

ButtonState_t button_state;

// 消抖回调函数
void Debounce_Callback(TimerHandle_t xTimer) {
    // 再次读取按键状态
    bool current_state = HAL_GPIO_ReadPin(BUTTON_GPIO_Port, BUTTON_Pin) == GPIO_PIN_RESET;
    
    // 如果状态一致，确认按键事件
    if(current_state == button_state.pressed) {
        if(button_state.pressed) {
            printf("Button %d pressed (confirmed)\n", button_state.button_id);
            OnButtonPressed(button_state.button_id);
        } else {
            printf("Button %d released (confirmed)\n", button_state.button_id);
            OnButtonReleased(button_state.button_id);
        }
    } else {
        printf("Button state changed during debounce, ignored\n");
    }
}

// 按键中断处理
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    if(GPIO_Pin == BUTTON_Pin) {
        // 读取按键状态
        button_state.button_id = 1;
        button_state.pressed = (HAL_GPIO_ReadPin(BUTTON_GPIO_Port, BUTTON_Pin) == GPIO_PIN_RESET);
        
        // 重启消抖定时器（20ms）
        xTimerResetFromISR(debounce_timer, &xHigherPriorityTaskWoken);
        
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    
    // 创建消抖定时器（单次20ms）
    debounce_timer = xTimerCreate(
        "Debounce",
        pdMS_TO_TICKS(20),      // 20ms消抖时间
        pdFALSE,                // 单次定时器
        (void *)0,
        Debounce_Callback
    );
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```


### 场景3：周期性数据采集

使用定时器实现周期性传感器数据采集：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "queue.h"

// 传感器数据结构
typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
} SensorData_t;

// 数据队列
QueueHandle_t sensor_queue;

// 传感器定时器
TimerHandle_t sensor_timer;

// 传感器读取回调
void Sensor_Read_Callback(TimerHandle_t xTimer) {
    SensorData_t data;
    
    // 读取传感器数据
    data.temperature = ReadTemperatureSensor();
    data.humidity = ReadHumiditySensor();
    data.timestamp = xTaskGetTickCount();
    
    printf("[%d] Sensor: Temp=%.1f°C, Humidity=%.1f%%\n",
           data.timestamp, data.temperature, data.humidity);
    
    // 发送到队列供其他任务处理
    xQueueSend(sensor_queue, &data, 0);
}

// 数据处理任务
void Data_Process_Task(void *param) {
    SensorData_t data;
    
    while(1) {
        // 等待传感器数据
        if(xQueueReceive(sensor_queue, &data, portMAX_DELAY) == pdTRUE) {
            // 处理数据
            ProcessSensorData(&data);
            
            // 检查阈值
            if(data.temperature > 30.0f) {
                printf("Warning: High temperature!\n");
            }
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建数据队列
    sensor_queue = xQueueCreate(10, sizeof(SensorData_t));
    
    // 创建传感器定时器（周期1000ms）
    sensor_timer = xTimerCreate(
        "Sensor",
        pdMS_TO_TICKS(1000),    // 每秒读取一次
        pdTRUE,                 // 周期定时器
        (void *)0,
        Sensor_Read_Callback
    );
    
    // 创建数据处理任务
    xTaskCreate(Data_Process_Task, "DataProc", 256, NULL, 2, NULL);
    
    // 启动定时器
    xTimerStart(sensor_timer, 0);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[1000] Sensor: Temp=25.5°C, Humidity=60.0%
[2000] Sensor: Temp=25.6°C, Humidity=60.2%
[3000] Sensor: Temp=25.7°C, Humidity=60.1%
[4000] Sensor: Temp=31.2°C, Humidity=58.5%
Warning: High temperature!
```


### 场景4：超时保护

使用单次定时器实现操作超时保护：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

// 超时定时器
TimerHandle_t timeout_timer;

// 操作状态
typedef enum {
    OP_STATE_IDLE,
    OP_STATE_BUSY,
    OP_STATE_TIMEOUT,
    OP_STATE_COMPLETE
} OperationState_t;

volatile OperationState_t operation_state = OP_STATE_IDLE;

// 超时回调函数
void Timeout_Callback(TimerHandle_t xTimer) {
    if(operation_state == OP_STATE_BUSY) {
        printf("Operation timeout!\n");
        operation_state = OP_STATE_TIMEOUT;
        
        // 取消操作
        CancelOperation();
    }
}

// 开始操作
bool StartOperation(void) {
    if(operation_state != OP_STATE_IDLE) {
        return false;  // 操作正在进行
    }
    
    printf("Starting operation...\n");
    operation_state = OP_STATE_BUSY;
    
    // 启动超时定时器（5秒）
    xTimerStart(timeout_timer, 0);
    
    // 执行操作
    DoOperation();
    
    return true;
}

// 操作完成
void OperationComplete(void) {
    if(operation_state == OP_STATE_BUSY) {
        // 停止超时定时器
        xTimerStop(timeout_timer, 0);
        
        printf("Operation completed successfully\n");
        operation_state = OP_STATE_COMPLETE;
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建超时定时器（单次5000ms）
    timeout_timer = xTimerCreate(
        "Timeout",
        pdMS_TO_TICKS(5000),    // 5秒超时
        pdFALSE,                // 单次定时器
        (void *)0,
        Timeout_Callback
    );
    
    // 创建任务...
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

### 场景5：看门狗喂狗

使用周期定时器实现看门狗喂狗：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

// 看门狗定时器
TimerHandle_t watchdog_timer;

// 看门狗喂狗回调
void Watchdog_Feed_Callback(TimerHandle_t xTimer) {
    // 喂狗
    HAL_IWDG_Refresh(&hiwdg);
    
    printf("[%d] Watchdog fed\n", xTaskGetTickCount());
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化看门狗（超时时间1000ms）
    MX_IWDG_Init();
    
    // 创建喂狗定时器（周期500ms，小于看门狗超时时间）
    watchdog_timer = xTimerCreate(
        "Watchdog",
        pdMS_TO_TICKS(500),     // 每500ms喂一次狗
        pdTRUE,                 // 周期定时器
        (void *)0,
        Watchdog_Feed_Callback
    );
    
    // 启动喂狗定时器
    xTimerStart(watchdog_timer, 0);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```


## 使用技巧

### 技巧1：使用定时器ID区分多个定时器

```c
// 使用同一个回调函数处理多个定时器
void Multi_Timer_Callback(TimerHandle_t xTimer) {
    // 获取定时器ID
    uint32_t timer_id = (uint32_t)pvTimerGetTimerID(xTimer);
    
    switch(timer_id) {
        case 0:
            printf("Timer 0 expired\n");
            LED1_Toggle();
            break;
        case 1:
            printf("Timer 1 expired\n");
            LED2_Toggle();
            break;
        case 2:
            printf("Timer 2 expired\n");
            LED3_Toggle();
            break;
        default:
            break;
    }
}

// 创建多个定时器
TimerHandle_t timer1 = xTimerCreate("T1", pdMS_TO_TICKS(500), pdTRUE, (void *)0, Multi_Timer_Callback);
TimerHandle_t timer2 = xTimerCreate("T2", pdMS_TO_TICKS(1000), pdTRUE, (void *)1, Multi_Timer_Callback);
TimerHandle_t timer3 = xTimerCreate("T3", pdMS_TO_TICKS(1500), pdTRUE, (void *)2, Multi_Timer_Callback);
```

### 技巧2：在回调中设置标志，在任务中处理

```c
// 定时器标志
volatile bool timer_flag = false;

// 回调函数（快速返回）
void Timer_Callback(TimerHandle_t xTimer) {
    timer_flag = true;  // 只设置标志
}

// 任务中处理
void Process_Task(void *param) {
    while(1) {
        if(timer_flag) {
            timer_flag = false;
            
            // 在这里执行耗时操作
            ProcessComplexData();
            SaveToFlash();
            SendToNetwork();
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### 技巧3：动态调整定时器周期

```c
// 根据系统状态调整定时器周期
void AdjustTimerPeriod(SystemState_t state) {
    uint32_t new_period;
    
    switch(state) {
        case STATE_ACTIVE:
            new_period = 100;  // 活动状态：快速采样
            break;
        case STATE_IDLE:
            new_period = 1000;  // 空闲状态：慢速采样
            break;
        case STATE_SLEEP:
            new_period = 5000;  // 睡眠状态：极慢采样
            break;
        default:
            new_period = 1000;
            break;
    }
    
    // 修改定时器周期
    xTimerChangePeriod(sensor_timer, pdMS_TO_TICKS(new_period), 0);
    printf("Timer period changed to %d ms\n", new_period);
}
```

### 技巧4：使用定时器实现延迟执行

```c
// 延迟执行任务
typedef struct {
    void (*function)(void *);
    void *param;
} DelayedTask_t;

void Delayed_Callback(TimerHandle_t xTimer) {
    DelayedTask_t *task = (DelayedTask_t *)pvTimerGetTimerID(xTimer);
    
    // 执行延迟任务
    if(task != NULL && task->function != NULL) {
        task->function(task->param);
    }
    
    // 删除定时器
    xTimerDelete(xTimer, 0);
    
    // 释放内存
    free(task);
}

// 延迟执行函数
void ExecuteDelayed(void (*func)(void *), void *param, uint32_t delay_ms) {
    // 分配任务结构
    DelayedTask_t *task = (DelayedTask_t *)malloc(sizeof(DelayedTask_t));
    task->function = func;
    task->param = param;
    
    // 创建单次定时器
    TimerHandle_t timer = xTimerCreate(
        "Delayed",
        pdMS_TO_TICKS(delay_ms),
        pdFALSE,
        (void *)task,
        Delayed_Callback
    );
    
    // 启动定时器
    xTimerStart(timer, 0);
}

// 使用示例
void MyDelayedFunction(void *param) {
    printf("This function executed after delay\n");
}

// 延迟2秒执行
ExecuteDelayed(MyDelayedFunction, NULL, 2000);
```


## 常见问题

### Q1: 软件定时器和硬件定时器有什么区别？

**A**: 主要区别在于实现方式和精度：

**硬件定时器**：
- 由硬件实现，精度高
- 数量有限（通常2-4个）
- 可以产生中断
- 配置复杂
- 适合需要高精度的场景

**软件定时器**：
- 由软件实现，基于RTOS时钟节拍
- 数量不限（受内存限制）
- 在定时器任务中执行回调
- 使用简单
- 精度受时钟节拍影响（通常1ms）

**选择建议**：
- 需要高精度（微秒级） → 使用硬件定时器
- 一般应用（毫秒级） → 使用软件定时器

### Q2: 为什么回调函数不能阻塞？

**A**: 因为所有定时器回调函数都在定时器服务任务中执行：

**问题示例**：
```c
// ❌ 错误：回调函数中阻塞
void Bad_Callback(TimerHandle_t xTimer) {
    vTaskDelay(pdMS_TO_TICKS(1000));  // 阻塞1秒
    // 这会阻塞定时器服务任务，影响所有其他定时器！
}
```

**后果**：
- 定时器服务任务被阻塞
- 其他定时器无法及时执行
- 系统响应变慢

**正确做法**：
```c
// ✅ 正确：快速返回
void Good_Callback(TimerHandle_t xTimer) {
    timer_flag = true;  // 只设置标志
}

// 在任务中处理
void Task(void *param) {
    while(1) {
        if(timer_flag) {
            timer_flag = false;
            vTaskDelay(pdMS_TO_TICKS(1000));  // 在任务中可以阻塞
        }
    }
}
```

### Q3: 如何选择定时器服务任务的优先级？

**A**: 定时器服务任务优先级的选择很重要：

**配置参数**：
```c
// FreeRTOSConfig.h
#define configTIMER_TASK_PRIORITY  3  // 定时器任务优先级
```

**选择原则**：
- **太低**：定时器回调执行不及时
- **太高**：可能影响高优先级任务
- **推荐**：设置为中等偏高的优先级

**示例场景**：
```
优先级5：紧急中断处理任务
优先级4：实时控制任务
优先级3：定时器服务任务  ← 推荐
优先级2：数据处理任务
优先级1：后台任务
```

### Q4: 定时器命令队列满了怎么办？

**A**: 当定时器命令队列满时，定时器操作会失败：

**问题场景**：
```c
// 命令队列已满
if(xTimerStart(timer, 0) != pdPASS) {
    printf("Failed to start timer: queue full\n");
}
```

**解决方法**：

**方法1：增加队列长度**
```c
// FreeRTOSConfig.h
#define configTIMER_QUEUE_LENGTH  20  // 增加队列长度
```

**方法2：使用阻塞等待**
```c
// 等待队列有空间
if(xTimerStart(timer, pdMS_TO_TICKS(100)) != pdPASS) {
    printf("Failed to start timer after waiting\n");
}
```

**方法3：减少定时器操作频率**
```c
// 避免频繁启动/停止定时器
// 使用标志控制回调函数的行为
volatile bool timer_enabled = true;

void Timer_Callback(TimerHandle_t xTimer) {
    if(timer_enabled) {
        // 执行操作
    }
}

// 不需要频繁调用xTimerStart/xTimerStop
timer_enabled = false;  // 禁用
timer_enabled = true;   // 启用
```


### Q5: 定时器精度如何？

**A**: 软件定时器的精度受多个因素影响：

**影响因素**：

1. **时钟节拍频率**
```c
// FreeRTOSConfig.h
#define configTICK_RATE_HZ  1000  // 1ms节拍
// 定时器精度最高为1ms
```

2. **定时器服务任务调度**
- 如果定时器任务被高优先级任务抢占，会有延迟
- 回调函数执行时间也会影响其他定时器

3. **系统负载**
- 系统负载高时，定时器可能不够及时

**精度范围**：
- **理论精度**：等于时钟节拍周期（通常1ms）
- **实际精度**：1-10ms（取决于系统负载）

**提高精度的方法**：
```c
// 1. 提高时钟节拍频率
#define configTICK_RATE_HZ  10000  // 0.1ms节拍

// 2. 提高定时器任务优先级
#define configTIMER_TASK_PRIORITY  4

// 3. 保持回调函数简短
void Fast_Callback(TimerHandle_t xTimer) {
    flag = true;  // 快速返回
}
```

**注意**：
- 提高时钟节拍频率会增加系统开销
- 如果需要微秒级精度，应使用硬件定时器


## 故障排除

### 问题1：定时器创建失败

**现象**：
```c
TimerHandle_t timer = xTimerCreate(...);
if(timer == NULL) {
    printf("Failed to create timer\n");
}
```

**可能原因**：
1. 堆内存不足
2. 未启用软件定时器功能
3. 定时器服务任务创建失败

**解决方法**：

```c
// 1. 检查FreeRTOS配置
// FreeRTOSConfig.h
#define configUSE_TIMERS  1  // 必须启用

// 2. 增加堆大小
#define configTOTAL_HEAP_SIZE  ((size_t)(20 * 1024))

// 3. 检查剩余堆空间
size_t free_heap = xPortGetFreeHeapSize();
printf("Free heap: %d bytes\n", free_heap);

// 4. 检查定时器任务配置
#define configTIMER_TASK_STACK_DEPTH  256  // 增加堆栈
```

### 问题2：定时器不执行

**现象**：
```c
// 定时器已启动，但回调函数不执行
xTimerStart(timer, 0);
// 回调函数从未被调用
```

**可能原因**：
1. 定时器未正确启动
2. 调度器未启动
3. 定时器服务任务被阻塞

**解决方法**：

```c
// 1. 检查启动结果
if(xTimerStart(timer, 0) != pdPASS) {
    printf("Failed to start timer\n");
}

// 2. 确保调度器已启动
vTaskStartScheduler();  // 必须调用

// 3. 检查定时器状态
if(xTimerIsTimerActive(timer)) {
    printf("Timer is active\n");
} else {
    printf("Timer is not active\n");
}

// 4. 添加调试输出
void Debug_Callback(TimerHandle_t xTimer) {
    printf("Timer callback executed\n");
}
```


### 问题3：定时不准确

**现象**：
```c
// 设置500ms定时器，但实际执行间隔不稳定
// 有时490ms，有时510ms
```

**可能原因**：
1. 系统负载高
2. 回调函数执行时间长
3. 定时器任务优先级低

**解决方法**：

```c
// 1. 提高定时器任务优先级
#define configTIMER_TASK_PRIORITY  4

// 2. 简化回调函数
void Fast_Callback(TimerHandle_t xTimer) {
    flag = true;  // 只设置标志，快速返回
}

// 3. 监控定时器执行时间
void Monitor_Callback(TimerHandle_t xTimer) {
    static uint32_t last_time = 0;
    uint32_t current_time = xTaskGetTickCount();
    uint32_t interval = current_time - last_time;
    
    printf("Timer interval: %d ms\n", interval);
    last_time = current_time;
}

// 4. 减少系统负载
// 降低其他任务的优先级或减少任务数量
```

### 问题4：内存泄漏

**现象**：
```c
// 系统运行一段时间后，可用堆内存持续减少
```

**可能原因**：
1. 创建定时器后未删除
2. 在回调中分配内存未释放

**解决方法**：

```c
// 1. 及时删除不需要的定时器
void CleanupTimer(TimerHandle_t timer) {
    if(timer != NULL) {
        xTimerStop(timer, 0);
        xTimerDelete(timer, 0);
    }
}

// 2. 避免在回调中动态分配内存
// ❌ 错误
void Bad_Callback(TimerHandle_t xTimer) {
    char *buffer = (char *)malloc(100);
    // 忘记释放
}

// ✅ 正确
char static_buffer[100];
void Good_Callback(TimerHandle_t xTimer) {
    // 使用静态缓冲区
}

// 3. 监控堆内存
void Monitor_Heap(void) {
    size_t free_heap = xPortGetFreeHeapSize();
    size_t min_free_heap = xPortGetMinimumEverFreeHeapSize();
    
    printf("Free heap: %d bytes\n", free_heap);
    printf("Min free heap: %d bytes\n", min_free_heap);
}
```


## 总结

### 核心要点

1. **软件定时器概念**
   - 基于RTOS时钟节拍的定时机制
   - 不需要创建专门的任务
   - 所有回调在定时器服务任务中执行

2. **定时器类型**
   - 单次定时器：执行一次后停止
   - 周期定时器：自动重复执行

3. **基本操作**
   - `xTimerCreate()`：创建定时器
   - `xTimerStart()`：启动定时器
   - `xTimerStop()`：停止定时器
   - `xTimerReset()`：重置定时器
   - `xTimerDelete()`：删除定时器

4. **回调函数规则**
   - 必须快速返回，不能阻塞
   - 不能调用会阻塞的API
   - 可以设置标志，在任务中处理

5. **典型应用**
   - LED闪烁控制
   - 按键消抖
   - 周期性数据采集
   - 超时保护
   - 看门狗喂狗

6. **最佳实践**
   - 保持回调函数简短
   - 使用标志+任务处理复杂逻辑
   - 合理设置定时器任务优先级
   - 及时删除不需要的定时器
   - 监控系统资源使用

### 软件定时器 vs 其他机制

| 机制 | 内存占用 | 精度 | 适用场景 |
|------|---------|------|---------|
| **软件定时器** | 小 | 毫秒级 | 简单定时操作 |
| **任务+延时** | 大 | 毫秒级 | 复杂任务逻辑 |
| **硬件定时器** | 小 | 微秒级 | 高精度定时 |

### 学习检查

完成本文后，你应该能够：

- [ ] 理解软件定时器的概念和工作原理
- [ ] 掌握定时器的创建和管理方法
- [ ] 能够使用单次和周期定时器
- [ ] 理解回调函数的使用规则
- [ ] 知道何时使用软件定时器
- [ ] 能够解决常见的定时器问题


## 延伸阅读

### 相关主题

- [RTOS任务管理](02-rtos-task-management.html) - 了解任务的基本概念
- [RTOS调度算法](03-rtos-scheduling.html) - 理解任务调度机制
- [信号量使用](04-semaphore.html) - 学习任务同步方法
- [消息队列通信](06-message-queue.html) - 学习任务间数据传递
- [RTOS内存管理](../intermediate/01-rtos-memory.html) - 深入理解内存管理

### 参考资料

- [FreeRTOS官方文档 - Software Timers](https://www.freertos.org/RTOS-software-timer.html)
- [FreeRTOS Software Timer API](https://www.freertos.org/FreeRTOS-Software-Timer-API-Functions.html)
- [Mastering the FreeRTOS Real Time Kernel](https://www.freertos.org/Documentation/RTOS_book.html)

---

**文档版本**: 1.0  
**最后更新**: 2024-01-15  
**作者**: 嵌入式知识平台
