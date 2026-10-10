---
title: "RTOS中断管理与延迟处理：高效处理中断和任务协作"
description: "深入学习RTOS环境下的中断管理技术和延迟处理机制。掌握中断与RTOS的交互、中断服务函数的编写规范、中断安全API的使用、延迟处理的实现方法，以及中断优先级配置和性能优化技巧。"
slug: "rtos-interrupt"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 中断管理
  - 延迟处理
  - 中断安全
  - ISR
  - 中断优先级
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/06-message-queue.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/03-priority-inversion.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
  - "03-operating-system-layer/03-freertos/beginner/03-freertos-queue.md"

# 学习信息
estimated_time: 75
difficulty_score: 7

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
  - RTOS中断管理
  - 中断服务函数
  - 延迟处理
  - 中断安全API
  - FromISR函数
  - 中断优先级
cover_image: ""
---


# RTOS中断管理与延迟处理：高效处理中断和任务协作

## 学习目标

完成本教程后，你将能够：

- 理解RTOS环境下中断的工作机制
- 掌握中断服务函数(ISR)的编写规范
- 学会使用中断安全API（FromISR函数）
- 理解延迟处理的概念和实现方法
- 掌握中断优先级的配置和影响
- 学会使用信号量、队列和任务通知进行中断与任务通信
- 能够优化中断响应时间和系统性能
- 理解中断嵌套和临界区保护


## 前置要求

### 知识要求

- 理解RTOS任务管理和调度机制
- 掌握信号量和消息队列的使用
- 了解ARM Cortex-M中断系统
- 理解中断优先级和NVIC配置

### 技能要求

- 能够配置和使用外设中断
- 理解中断服务函数的基本概念
- 掌握RTOS任务间通信机制
- 具备基本的系统调试能力

### 环境要求

- STM32开发板（或其他支持FreeRTOS的开发板）
- STM32CubeIDE或Keil MDK开发环境
- FreeRTOS源码或HAL库
- 串口调试工具
- 逻辑分析仪或示波器（可选）


## 准备工作

### 硬件准备

| 硬件 | 数量 | 说明 |
|------|------|------|
| STM32开发板 | 1 | 如STM32F407、STM32F103等 |
| 按键 | 2个 | 用于触发外部中断 |
| LED灯 | 2个 | 用于状态指示 |
| USB数据线 | 1 | 用于下载和供电 |

### 软件准备

1. **安装开发环境**
   - STM32CubeIDE v1.10或更高版本
   - 或Keil MDK v5.30或更高版本

2. **配置FreeRTOS**
   - 在STM32CubeMX中启用FreeRTOS
   - 或手动添加FreeRTOS源码到项目

3. **配置串口**
   - 配置UART用于调试输出
   - 波特率：115200
   - 数据位：8，停止位：1，无校验



### 环境配置

```c
// FreeRTOSConfig.h 关键配置
#define configUSE_PREEMPTION                    1  // 启用抢占式调度
#define configUSE_TICK_HOOK                     0  // 不使用tick hook
#define configCPU_CLOCK_HZ                      72000000  // CPU频率
#define configTICK_RATE_HZ                      1000  // 时钟节拍频率
#define configMAX_PRIORITIES                    8  // 最大优先级数
#define configMINIMAL_STACK_SIZE                128  // 最小栈大小

// 中断优先级配置（重要！）
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY         15
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY    5
#define configKERNEL_INTERRUPT_PRIORITY                 (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << 4)
#define configMAX_SYSCALL_INTERRUPT_PRIORITY            (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << 4)
```


## 概述

### 什么是RTOS中断管理？

在RTOS环境下，中断管理不仅仅是响应硬件事件，还需要与RTOS调度器协调工作，确保系统的实时性和稳定性。

**RTOS中断的特点**：

1. **中断优先级分级**
   - 高于RTOS管理的中断：不能调用RTOS API
   - RTOS管理的中断：可以调用FromISR API
   - 低于RTOS管理的中断：完全由RTOS管理

2. **中断安全API**
   - 普通API：只能在任务中调用
   - FromISR API：只能在中断中调用
   - 两者不能混用

3. **延迟处理机制**
   - 中断中只做最少的工作
   - 复杂处理交给任务完成
   - 通过信号量、队列或任务通知通信

### 为什么需要延迟处理？

**中断服务函数(ISR)的限制**：

1. **执行时间要短**
   - ISR会阻塞其他中断和任务
   - 长时间ISR会影响系统实时性
   - 可能导致中断丢失

2. **功能受限**
   - 不能调用阻塞函数
   - 不能使用延时
   - 不能进行复杂计算

3. **资源限制**
   - 使用中断栈，空间有限
   - 不能使用任务栈上的资源

**延迟处理的优势**：

```
传统方式（不推荐）：
中断 → 完整处理（读取、计算、存储、显示）→ 返回
      ↑____________长时间阻塞____________↑

延迟处理方式（推荐）：
中断 → 快速读取 → 发送信号 → 返回
                      ↓
                   任务唤醒 → 完整处理
```



### 相关概念

**中断优先级分组**：
- ARM Cortex-M使用NVIC管理中断
- 优先级分为抢占优先级和子优先级
- FreeRTOS要求正确配置优先级分组

**临界区(Critical Section)**：
- 不可被中断打断的代码段
- 用于保护共享资源
- 在RTOS中有特殊的实现方式

**上下文切换(Context Switch)**：
- 从中断返回时可能切换任务
- 需要使用特殊的返回机制
- FromISR函数会设置切换标志


## 步骤1：理解RTOS中断优先级

### 1.1 中断优先级分组

ARM Cortex-M的中断优先级系统：

```
优先级寄存器（8位）：
┌─────────────┬─────────────┐
│ 抢占优先级  │  子优先级   │
└─────────────┴─────────────┘
     4位            4位

优先级分组（PRIGROUP）：
- 0: 0位抢占 + 4位子优先级
- 1: 1位抢占 + 3位子优先级
- 2: 2位抢占 + 2位子优先级
- 3: 3位抢占 + 1位子优先级
- 4: 4位抢占 + 0位子优先级
```

**FreeRTOS的优先级要求**：

```c
// 在system_stm32f1xx.c或main.c中设置
HAL_Init();  // 会调用HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4)

// FreeRTOS要求使用PRIGROUP = 4（4位抢占优先级）
// 这样可以有16个抢占优先级（0-15）
```

### 1.2 FreeRTOS中断优先级分级

FreeRTOS将中断分为三个级别：

```
优先级数值越小，优先级越高
┌─────────────────────────────────────────┐
│  0-4: 高优先级中断（不受RTOS管理）      │  ← 不能调用RTOS API
│       - 最高优先级                       │
│       - 不会被RTOS禁用                   │
│       - 延迟最小                         │
├─────────────────────────────────────────┤
│  5-14: RTOS管理的中断                   │  ← 可以调用FromISR API
│       - 可以调用RTOS API                 │
│       - 会被临界区禁用                   │
│       - 可以触发任务切换                 │
├─────────────────────────────────────────┤
│  15: 最低优先级（PendSV和SysTick）      │  ← RTOS内部使用
│       - 用于任务切换                     │
│       - 不应被用户使用                   │
└─────────────────────────────────────────┘
```

**配置示例**：

```c
// FreeRTOSConfig.h
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY    5

// 这意味着：
// - 优先级0-4：不能调用RTOS API
// - 优先级5-14：可以调用FromISR API
// - 优先级15：RTOS内部使用

// 配置中断优先级
void ConfigureInterrupts(void) {
    // 高优先级中断（不调用RTOS API）
    HAL_NVIC_SetPriority(TIM1_UP_IRQn, 2, 0);  // 优先级2，不能调用RTOS API
    
    // RTOS管理的中断（可以调用FromISR API）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 6, 0);    // 优先级6，可以调用FromISR API
    HAL_NVIC_SetPriority(USART1_IRQn, 7, 0);   // 优先级7，可以调用FromISR API
    
    // 启用中断
    HAL_NVIC_EnableIRQ(TIM1_UP_IRQn);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
}
```



### 1.3 中断优先级验证

```c
#include "FreeRTOS.h"
#include "task.h"

// 检查中断优先级配置是否正确
void CheckInterruptPriority(IRQn_Type IRQn) {
    uint32_t priority = NVIC_GetPriority(IRQn);
    uint32_t max_syscall_priority = configMAX_SYSCALL_INTERRUPT_PRIORITY >> 4;
    
    printf("IRQ %d priority: %d\n", IRQn, priority);
    
    if(priority < max_syscall_priority) {
        printf("  → Cannot call RTOS API (too high priority)\n");
    } else {
        printf("  → Can call FromISR API\n");
    }
}

// 在main函数中调用
int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 配置中断
    ConfigureInterrupts();
    
    // 检查配置
    printf("Checking interrupt priorities:\n");
    CheckInterruptPriority(TIM1_UP_IRQn);
    CheckInterruptPriority(EXTI0_IRQn);
    CheckInterruptPriority(USART1_IRQn);
    
    // 创建任务并启动调度器
    // ...
}
```


## 步骤2：中断安全API的使用

### 2.1 FromISR函数概述

FreeRTOS为中断环境提供了专门的API函数，这些函数以`FromISR`结尾：

**常用FromISR函数**：

| 任务API | 中断API | 功能 |
|---------|---------|------|
| `xSemaphoreGive()` | `xSemaphoreGiveFromISR()` | 释放信号量 |
| `xSemaphoreTake()` | `xSemaphoreTakeFromISR()` | 获取信号量 |
| `xQueueSend()` | `xQueueSendFromISR()` | 发送队列消息 |
| `xQueueReceive()` | `xQueueReceiveFromISR()` | 接收队列消息 |
| `xTaskNotifyGive()` | `vTaskNotifyGiveFromISR()` | 发送任务通知 |
| `xEventGroupSetBits()` | `xEventGroupSetBitsFromISR()` | 设置事件标志 |

**关键区别**：

```c
// ❌ 错误：在中断中调用普通API
void EXTI0_IRQHandler(void) {
    xSemaphoreGive(sem);  // 错误！会导致系统崩溃
}

// ✅ 正确：在中断中调用FromISR API
void EXTI0_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 2.2 使用信号量进行中断通知

**场景**：按键中断通知任务处理

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 信号量句柄
SemaphoreHandle_t button_sem;

// 按键中断服务函数
void EXTI0_IRQHandler(void) {
    // 清除中断标志
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 发送信号量通知任务
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(button_sem, &xHigherPriorityTaskWoken);
        
        // 如果有更高优先级任务被唤醒，进行任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 按键处理任务
void Button_Task(void *param) {
    while(1) {
        // 等待信号量（阻塞）
        if(xSemaphoreTake(button_sem, portMAX_DELAY) == pdTRUE) {
            printf("[%d] Button pressed!\n", xTaskGetTickCount());
            
            // 执行复杂的处理
            ProcessButtonPress();
            UpdateDisplay();
            SaveToFlash();
            
            printf("[%d] Button processing complete\n", xTaskGetTickCount());
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置按键GPIO和中断
    ConfigureButtonInterrupt();
    
    // 创建二值信号量
    button_sem = xSemaphoreCreateBinary();
    
    if(button_sem != NULL) {
        // 创建任务
        xTaskCreate(Button_Task, "Button", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**时序分析**：

```
时间轴：
0ms     中断发生     任务唤醒     处理完成
|----------|----------|----------|----------|
           ↓          ↓          ↓
中断：     ISR执行    返回
           (快速)
           
任务：     阻塞       运行       阻塞
                     (复杂处理)
```



### 2.3 使用队列传递中断数据

**场景**：串口接收中断传递数据到任务

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 接收数据结构
typedef struct {
    uint32_t timestamp;
    uint8_t data;
} UartData_t;

// 队列句柄
QueueHandle_t uart_queue;

// 串口接收中断
void USART1_IRQHandler(void) {
    if(__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        // 读取数据
        uint8_t received_data = (uint8_t)(huart1.Instance->DR & 0xFF);
        
        // 准备数据包
        UartData_t data_packet;
        data_packet.timestamp = xTaskGetTickCountFromISR();
        data_packet.data = received_data;
        
        // 发送到队列
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(uart_queue, &data_packet, &xHigherPriorityTaskWoken);
        
        // 任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 串口处理任务
void Uart_Task(void *param) {
    UartData_t received_packet;
    
    while(1) {
        // 从队列接收数据
        if(xQueueReceive(uart_queue, &received_packet, portMAX_DELAY) == pdTRUE) {
            printf("[%d] Received: 0x%02X\n", 
                   received_packet.timestamp, 
                   received_packet.data);
            
            // 处理数据
            ProcessUartData(received_packet.data);
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置串口
    MX_USART1_UART_Init();
    
    // 创建队列（可以存储10个数据包）
    uart_queue = xQueueCreate(10, sizeof(UartData_t));
    
    if(uart_queue != NULL) {
        // 创建任务
        xTaskCreate(Uart_Task, "UART", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**优势**：
- 中断中只做数据读取和入队（快速）
- 复杂处理在任务中完成（不阻塞中断）
- 队列提供缓冲，防止数据丢失
- 时间戳记录精确的接收时间

### 2.4 使用任务通知进行中断通知

**任务通知**是FreeRTOS提供的轻量级通信机制，比信号量和队列更快：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务句柄
TaskHandle_t sensor_task_handle;

// 定时器中断（每100ms触发一次）
void TIM2_IRQHandler(void) {
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 发送任务通知
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        vTaskNotifyGiveFromISR(sensor_task_handle, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 传感器任务
void Sensor_Task(void *param) {
    while(1) {
        // 等待任务通知
        uint32_t notification_value = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        if(notification_value > 0) {
            // 读取传感器
            float temperature = ReadTemperature();
            float humidity = ReadHumidity();
            
            printf("Temp: %.1f°C, Humidity: %.1f%%\n", temperature, humidity);
            
            // 处理数据
            ProcessSensorData(temperature, humidity);
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置定时器
    MX_TIM2_Init();
    HAL_TIM_Base_Start_IT(&htim2);
    
    // 创建任务
    xTaskCreate(Sensor_Task, "Sensor", 256, NULL, 2, &sensor_task_handle);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**任务通知 vs 信号量 vs 队列**：

| 特性 | 任务通知 | 信号量 | 队列 |
|------|---------|--------|------|
| **速度** | 最快 | 快 | 较慢 |
| **内存** | 无额外开销 | 需要信号量对象 | 需要队列对象和缓冲区 |
| **数据传递** | 32位值 | 无 | 任意大小 |
| **多任务等待** | 不支持 | 支持 | 支持 |
| **适用场景** | 简单通知 | 同步/计数 | 数据传递 |



## 步骤3：延迟处理的实现模式

### 3.1 延迟处理的基本原则

**中断中应该做什么**：
- ✅ 读取硬件寄存器
- ✅ 清除中断标志
- ✅ 读取简单数据
- ✅ 发送信号/数据到任务
- ✅ 更新简单的全局变量

**中断中不应该做什么**：
- ❌ 复杂计算
- ❌ 浮点运算（除非硬件支持）
- ❌ 字符串处理
- ❌ 文件操作
- ❌ 网络通信
- ❌ 显示更新
- ❌ 调用阻塞函数
- ❌ 使用延时

### 3.2 模式1：二值信号量模式

**适用场景**：简单的事件通知，不需要传递数据

```c
// 全局变量
SemaphoreHandle_t event_sem;
TaskHandle_t handler_task_handle;

// 中断服务函数
void Event_IRQHandler(void) {
    // 清除中断标志
    ClearInterruptFlag();
    
    // 发送信号量
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(event_sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 处理任务
void Handler_Task(void *param) {
    while(1) {
        // 等待事件
        if(xSemaphoreTake(event_sem, portMAX_DELAY) == pdTRUE) {
            // 处理事件
            HandleEvent();
        }
    }
}

// 初始化
void Init(void) {
    event_sem = xSemaphoreCreateBinary();
    xTaskCreate(Handler_Task, "Handler", 256, NULL, 3, &handler_task_handle);
}
```

**优点**：
- 实现简单
- 开销小
- 适合简单通知

**缺点**：
- 不能传递数据
- 不能计数（多次触发只记录一次）

### 3.3 模式2：计数信号量模式

**适用场景**：需要记录事件发生次数

```c
// 全局变量
SemaphoreHandle_t count_sem;

// 中断服务函数（可能快速连续触发）
void FastEvent_IRQHandler(void) {
    ClearInterruptFlag();
    
    // 每次中断增加计数
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(count_sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 处理任务
void Handler_Task(void *param) {
    while(1) {
        // 获取一个计数
        if(xSemaphoreTake(count_sem, portMAX_DELAY) == pdTRUE) {
            // 处理一个事件
            ProcessOneEvent();
        }
    }
}

// 初始化
void Init(void) {
    // 创建计数信号量（最大计数10）
    count_sem = xSemaphoreCreateCounting(10, 0);
    xTaskCreate(Handler_Task, "Handler", 256, NULL, 3, NULL);
}
```

**优点**：
- 可以记录多次事件
- 不会丢失事件（在计数范围内）

**缺点**：
- 仍然不能传递数据
- 计数上限有限制

### 3.4 模式3：队列模式

**适用场景**：需要传递数据，保持数据顺序

```c
// 数据结构
typedef struct {
    uint32_t timestamp;
    uint16_t adc_value;
    uint8_t channel;
} AdcData_t;

// 全局变量
QueueHandle_t adc_queue;

// ADC中断
void ADC_IRQHandler(void) {
    if(__HAL_ADC_GET_FLAG(&hadc1, ADC_FLAG_EOC)) {
        // 读取ADC值
        uint16_t adc_value = HAL_ADC_GetValue(&hadc1);
        
        // 准备数据包
        AdcData_t data;
        data.timestamp = xTaskGetTickCountFromISR();
        data.adc_value = adc_value;
        data.channel = 1;
        
        // 发送到队列
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(adc_queue, &data, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 处理任务
void Adc_Task(void *param) {
    AdcData_t received_data;
    
    while(1) {
        // 从队列接收数据
        if(xQueueReceive(adc_queue, &received_data, portMAX_DELAY) == pdTRUE) {
            // 处理ADC数据
            float voltage = (received_data.adc_value * 3.3f) / 4096.0f;
            
            printf("[%d] CH%d: %d (%.2fV)\n",
                   received_data.timestamp,
                   received_data.channel,
                   received_data.adc_value,
                   voltage);
            
            // 进一步处理
            ProcessAdcData(voltage);
        }
    }
}

// 初始化
void Init(void) {
    // 创建队列（可以存储20个数据包）
    adc_queue = xQueueCreate(20, sizeof(AdcData_t));
    xTaskCreate(Adc_Task, "ADC", 512, NULL, 3, NULL);
}
```

**优点**：
- 可以传递复杂数据
- 保持数据顺序
- 提供缓冲机制

**缺点**：
- 内存开销较大
- 速度相对较慢



### 3.5 模式4：任务通知模式

**适用场景**：单任务等待，需要传递简单数值

```c
// 任务句柄
TaskHandle_t encoder_task_handle;

// 编码器中断
void EXTI_IRQHandler(void) {
    static int32_t encoder_count = 0;
    
    // 读取编码器方向
    if(GPIO_ReadPin(ENCODER_A) == GPIO_ReadPin(ENCODER_B)) {
        encoder_count++;
    } else {
        encoder_count--;
    }
    
    // 发送任务通知（传递计数值）
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xTaskNotifyFromISR(encoder_task_handle, 
                       encoder_count, 
                       eSetValueWithOverwrite,
                       &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(ENCODER_PIN);
}

// 编码器任务
void Encoder_Task(void *param) {
    uint32_t notification_value;
    
    while(1) {
        // 等待任务通知
        if(xTaskNotifyWait(0, 0xFFFFFFFF, &notification_value, portMAX_DELAY) == pdTRUE) {
            int32_t count = (int32_t)notification_value;
            
            printf("Encoder count: %d\n", count);
            
            // 根据计数值更新显示或控制
            UpdateDisplay(count);
        }
    }
}

// 初始化
void Init(void) {
    xTaskCreate(Encoder_Task, "Encoder", 256, NULL, 3, &encoder_task_handle);
}
```

**任务通知的四种模式**：

```c
// 1. 不覆盖模式（如果有未读通知，不发送新的）
xTaskNotifyFromISR(task_handle, value, eNoAction, &xHigherPriorityTaskWoken);

// 2. 设置位模式（按位或）
xTaskNotifyFromISR(task_handle, 0x01, eSetBits, &xHigherPriorityTaskWoken);

// 3. 递增模式（计数）
xTaskNotifyFromISR(task_handle, 0, eIncrement, &xHigherPriorityTaskWoken);

// 4. 覆盖模式（总是更新为新值）
xTaskNotifyFromISR(task_handle, value, eSetValueWithOverwrite, &xHigherPriorityTaskWoken);
```

**优点**：
- 最快的通信方式
- 无额外内存开销
- 可以传递32位数值

**缺点**：
- 只能通知一个任务
- 数据可能被覆盖
- 不适合多生产者场景


## 步骤4：中断嵌套和临界区

### 4.1 中断嵌套

ARM Cortex-M支持中断嵌套，高优先级中断可以打断低优先级中断：

```
时间轴：
|------------|------------|------------|
低优先级中断：
|████████████████████████████|
     ↑                  ↑
     高优先级中断打断
     |████████|
```

**FreeRTOS中的中断嵌套**：

```c
// 配置中断优先级
void ConfigureNestedInterrupts(void) {
    // 高优先级中断（优先级2，不调用RTOS API）
    HAL_NVIC_SetPriority(TIM1_UP_IRQn, 2, 0);
    
    // 中优先级中断（优先级6，可以调用RTOS API）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 6, 0);
    
    // 低优先级中断（优先级8，可以调用RTOS API）
    HAL_NVIC_SetPriority(USART1_IRQn, 8, 0);
    
    // 启用中断
    HAL_NVIC_EnableIRQ(TIM1_UP_IRQn);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
}

// 高优先级中断（不调用RTOS API）
void TIM1_UP_IRQHandler(void) {
    if(__HAL_TIM_GET_FLAG(&htim1, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim1, TIM_FLAG_UPDATE);
        
        // 紧急处理，不调用RTOS API
        EmergencyHandler();
    }
}

// 中优先级中断（可以调用RTOS API）
void EXTI0_IRQHandler(void) {
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 可以被TIM1中断打断
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(button_sem, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 低优先级中断（可以调用RTOS API）
void USART1_IRQHandler(void) {
    if(__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        
        // 可以被TIM1和EXTI0中断打断
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(uart_queue, &data, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```



### 4.2 临界区保护

**临界区**是不能被中断打断的代码段，用于保护共享资源：

```c
// 方法1：禁用所有中断（不推荐）
void CriticalSection_Method1(void) {
    __disable_irq();  // 禁用所有中断
    
    // 临界区代码
    shared_variable++;
    
    __enable_irq();   // 恢复中断
}

// 方法2：使用FreeRTOS临界区（推荐）
void CriticalSection_Method2(void) {
    taskENTER_CRITICAL();  // 禁用RTOS管理的中断
    
    // 临界区代码
    shared_variable++;
    
    taskEXIT_CRITICAL();   // 恢复中断
}

// 方法3：在中断中使用临界区
void ISR_CriticalSection(void) {
    UBaseType_t uxSavedInterruptStatus;
    
    uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
    
    // 临界区代码
    shared_variable++;
    
    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);
}
```

**临界区的工作原理**：

```c
// taskENTER_CRITICAL() 的实现（简化版）
#define taskENTER_CRITICAL()  \
    portDISABLE_INTERRUPTS(); \
    uxCriticalNesting++;

// 它会：
// 1. 禁用优先级 >= configMAX_SYSCALL_INTERRUPT_PRIORITY 的中断
// 2. 高优先级中断（< configMAX_SYSCALL_INTERRUPT_PRIORITY）仍然可以响应
// 3. 支持嵌套（通过计数器）
```

**使用示例**：

```c
// 共享变量
volatile uint32_t shared_counter = 0;

// 任务1
void Task1(void *param) {
    while(1) {
        taskENTER_CRITICAL();
        shared_counter++;
        uint32_t local_copy = shared_counter;
        taskEXIT_CRITICAL();
        
        printf("Task1: %d\n", local_copy);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 任务2
void Task2(void *param) {
    while(1) {
        taskENTER_CRITICAL();
        shared_counter += 10;
        uint32_t local_copy = shared_counter;
        taskEXIT_CRITICAL();
        
        printf("Task2: %d\n", local_copy);
        vTaskDelay(pdMS_TO_TICKS(150));
    }
}

// 中断
void EXTI_IRQHandler(void) {
    UBaseType_t uxSavedInterruptStatus;
    
    uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
    shared_counter += 100;
    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}
```

**注意事项**：

```c
// ❌ 错误：临界区太长
taskENTER_CRITICAL();
ReadSensor();        // 耗时操作
ProcessData();       // 耗时操作
WriteToFlash();      // 耗时操作
taskEXIT_CRITICAL();

// ✅ 正确：临界区尽可能短
ReadSensor();        // 在临界区外
ProcessData();       // 在临界区外

taskENTER_CRITICAL();
UpdateSharedData();  // 只保护必要的操作
taskEXIT_CRITICAL();

WriteToFlash();      // 在临界区外

// ❌ 错误：在临界区中调用阻塞函数
taskENTER_CRITICAL();
vTaskDelay(100);     // 错误！会导致死锁
taskEXIT_CRITICAL();

// ❌ 错误：忘记退出临界区
taskENTER_CRITICAL();
if(error) {
    return;          // 错误！没有退出临界区
}
taskEXIT_CRITICAL();

// ✅ 正确：确保总是退出
taskENTER_CRITICAL();
if(error) {
    taskEXIT_CRITICAL();
    return;
}
taskEXIT_CRITICAL();
```


## 步骤5：性能优化

### 5.1 减少中断延迟

**中断延迟的组成**：

```
中断发生 → 硬件响应 → 保存上下文 → ISR执行 → 恢复上下文 → 返回
         ↑_______↑   ↑________↑   ↑_____↑   ↑________↑
         硬件延迟    软件延迟      ISR时间   软件延迟
```

**优化方法**：

1. **缩短ISR执行时间**

```c
// ❌ 不好：ISR中做太多事情
void EXTI_IRQHandler(void) {
    uint8_t data = ReadSensor();
    float result = ComplexCalculation(data);  // 耗时
    UpdateDisplay(result);                    // 耗时
    SaveToFlash(result);                      // 耗时
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}

// ✅ 更好：只做必要的工作
void EXTI_IRQHandler(void) {
    uint8_t data = ReadSensor();  // 快速读取
    
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(data_queue, &data, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}
```

2. **使用DMA减少中断频率**

```c
// ❌ 不好：每个字节触发一次中断
void USART_IRQHandler(void) {
    if(__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        ProcessByte(data);  // 每个字节都中断一次
    }
}

// ✅ 更好：使用DMA，只在传输完成时中断
uint8_t rx_buffer[256];

void DMA_IRQHandler(void) {
    if(__HAL_DMA_GET_FLAG(&hdma_usart1_rx, DMA_FLAG_TC)) {
        __HAL_DMA_CLEAR_FLAG(&hdma_usart1_rx, DMA_FLAG_TC);
        
        // 一次处理整个缓冲区
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(data_queue, rx_buffer, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```



3. **合理配置中断优先级**

```c
// 根据实时性要求配置优先级
void ConfigureOptimalPriorities(void) {
    // 最高优先级：紧急事件（不调用RTOS API）
    HAL_NVIC_SetPriority(EMERGENCY_IRQn, 2, 0);
    
    // 高优先级：实时数据采集
    HAL_NVIC_SetPriority(ADC_IRQn, 6, 0);
    
    // 中优先级：通信接口
    HAL_NVIC_SetPriority(USART1_IRQn, 7, 0);
    
    // 低优先级：非关键事件
    HAL_NVIC_SetPriority(BUTTON_IRQn, 9, 0);
}
```

### 5.2 测量中断性能

```c
// 测量ISR执行时间
void EXTI_IRQHandler(void) {
    // 设置GPIO高电平（用示波器测量）
    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_SET);
    
    // ISR代码
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 设置GPIO低电平
    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_RESET);
}

// 测量中断频率和响应时间
volatile uint32_t interrupt_count = 0;
volatile uint32_t max_response_time = 0;

void EXTI_IRQHandler(void) {
    uint32_t entry_time = DWT->CYCCNT;  // 使用DWT计数器
    
    interrupt_count++;
    
    // ISR代码
    ProcessInterrupt();
    
    uint32_t exit_time = DWT->CYCCNT;
    uint32_t execution_time = exit_time - entry_time;
    
    if(execution_time > max_response_time) {
        max_response_time = execution_time;
    }
    
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}

// 监控任务
void Monitor_Task(void *param) {
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        
        printf("Interrupt statistics:\n");
        printf("  Count: %d\n", interrupt_count);
        printf("  Max execution time: %d cycles (%.2f us)\n",
               max_response_time,
               (float)max_response_time / (SystemCoreClock / 1000000));
        
        // 重置统计
        interrupt_count = 0;
        max_response_time = 0;
    }
}
```

### 5.3 避免中断风暴

**中断风暴**：中断触发频率过高，导致系统无法正常工作

```c
// ❌ 问题：高频中断导致系统卡死
void HighFrequency_IRQHandler(void) {
    // 每1ms触发一次，ISR需要0.5ms
    // 结果：CPU 50%时间在ISR中，系统响应变慢
    ProcessData();  // 耗时0.5ms
    __HAL_TIM_CLEAR_FLAG(&htim, TIM_FLAG_UPDATE);
}

// ✅ 解决方案1：降低中断频率
void LowerFrequency_IRQHandler(void) {
    // 改为每10ms触发一次
    // CPU占用降低到5%
    ProcessData();
    __HAL_TIM_CLEAR_FLAG(&htim, TIM_FLAG_UPDATE);
}

// ✅ 解决方案2：使用DMA
void DMA_Solution(void) {
    // 使用DMA自动传输数据
    // 只在传输完成时中断一次
    HAL_ADC_Start_DMA(&hadc1, adc_buffer, BUFFER_SIZE);
}

// ✅ 解决方案3：批量处理
#define BATCH_SIZE 10
uint8_t batch_buffer[BATCH_SIZE];
uint8_t batch_index = 0;

void Batch_IRQHandler(void) {
    // 收集数据到缓冲区
    batch_buffer[batch_index++] = ReadData();
    
    // 只在缓冲区满时通知任务
    if(batch_index >= BATCH_SIZE) {
        batch_index = 0;
        
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(data_queue, batch_buffer, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
    
    __HAL_UART_CLEAR_FLAG(&huart1, UART_FLAG_RXNE);
}
```


## 实践示例

### 示例1：完整的中断延迟处理系统

创建一个多传感器数据采集系统，演示中断与任务的协作：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"

// 传感器数据结构
typedef struct {
    uint32_t timestamp;
    uint8_t sensor_id;
    float value;
} SensorData_t;

// 全局变量
QueueHandle_t sensor_queue;
TaskHandle_t process_task_handle;
TaskHandle_t display_task_handle;

// ADC中断（传感器1）
void ADC1_IRQHandler(void) {
    if(__HAL_ADC_GET_FLAG(&hadc1, ADC_FLAG_EOC)) {
        // 快速读取ADC值
        uint16_t adc_raw = HAL_ADC_GetValue(&hadc1);
        
        // 准备数据包
        SensorData_t data;
        data.timestamp = xTaskGetTickCountFromISR();
        data.sensor_id = 1;
        data.value = (float)adc_raw * 3.3f / 4096.0f;
        
        // 发送到队列
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(sensor_queue, &data, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 定时器中断（传感器2）
void TIM2_IRQHandler(void) {
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 读取温度传感器
        float temperature = ReadTemperatureSensor();
        
        // 准备数据包
        SensorData_t data;
        data.timestamp = xTaskGetTickCountFromISR();
        data.sensor_id = 2;
        data.value = temperature;
        
        // 发送到队列
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(sensor_queue, &data, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 外部中断（传感器3）
void EXTI0_IRQHandler(void) {
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 读取数字传感器
        uint8_t digital_value = ReadDigitalSensor();
        
        // 准备数据包
        SensorData_t data;
        data.timestamp = xTaskGetTickCountFromISR();
        data.sensor_id = 3;
        data.value = (float)digital_value;
        
        // 发送到队列
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(sensor_queue, &data, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 数据处理任务（高优先级）
void Process_Task(void *param) {
    SensorData_t received_data;
    
    while(1) {
        // 从队列接收数据
        if(xQueueReceive(sensor_queue, &received_data, portMAX_DELAY) == pdTRUE) {
            printf("[%d] Sensor %d: %.2f\n",
                   received_data.timestamp,
                   received_data.sensor_id,
                   received_data.value);
            
            // 数据处理
            ProcessSensorData(&received_data);
            
            // 检查阈值
            if(received_data.value > THRESHOLD) {
                printf("Warning: Sensor %d exceeded threshold!\n", 
                       received_data.sensor_id);
                TriggerAlarm();
            }
            
            // 保存到存储
            SaveToStorage(&received_data);
        }
    }
}

// 显示任务（低优先级）
void Display_Task(void *param) {
    while(1) {
        // 更新显示
        UpdateLCD();
        
        // 每500ms更新一次
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 监控任务
void Monitor_Task(void *param) {
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(10000));
        
        // 检查队列状态
        UBaseType_t queue_items = uxQueueMessagesWaiting(sensor_queue);
        UBaseType_t queue_spaces = uxQueueSpacesAvailable(sensor_queue);
        
        printf("\n=== System Status ===\n");
        printf("Queue: %d/%d items\n", queue_items, queue_items + queue_spaces);
        printf("Free heap: %d bytes\n", xPortGetFreeHeapSize());
        
        // 检查任务栈
        printf("Process task stack: %d words free\n",
               uxTaskGetStackHighWaterMark(process_task_handle));
        printf("Display task stack: %d words free\n",
               uxTaskGetStackHighWaterMark(display_task_handle));
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置外设和中断
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_TIM2_Init();
    
    // 配置中断优先级
    HAL_NVIC_SetPriority(ADC1_IRQn, 6, 0);
    HAL_NVIC_SetPriority(TIM2_IRQn, 7, 0);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 8, 0);
    
    // 启用中断
    HAL_NVIC_EnableIRQ(ADC1_IRQn);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 创建队列（可以存储50个数据包）
    sensor_queue = xQueueCreate(50, sizeof(SensorData_t));
    
    if(sensor_queue != NULL) {
        // 创建任务
        xTaskCreate(Process_Task, "Process", 512, NULL, 4, &process_task_handle);
        xTaskCreate(Display_Task, "Display", 256, NULL, 2, &display_task_handle);
        xTaskCreate(Monitor_Task, "Monitor", 256, NULL, 1, NULL);
        
        // 启动外设
        HAL_ADC_Start_IT(&hadc1);
        HAL_TIM_Base_Start_IT(&htim2);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```



### 示例2：高频中断优化

演示如何处理高频中断，避免系统过载：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 使用双缓冲技术
#define BUFFER_SIZE 128
uint16_t buffer_a[BUFFER_SIZE];
uint16_t buffer_b[BUFFER_SIZE];
uint16_t *active_buffer = buffer_a;
uint16_t *process_buffer = buffer_b;
volatile uint16_t buffer_index = 0;

// 信号量
SemaphoreHandle_t buffer_ready_sem;

// 高频ADC中断（每100us触发一次）
void ADC_IRQHandler(void) {
    if(__HAL_ADC_GET_FLAG(&hadc1, ADC_FLAG_EOC)) {
        // 快速读取并存储
        active_buffer[buffer_index++] = HAL_ADC_GetValue(&hadc1);
        
        // 缓冲区满时切换
        if(buffer_index >= BUFFER_SIZE) {
            buffer_index = 0;
            
            // 交换缓冲区
            uint16_t *temp = active_buffer;
            active_buffer = process_buffer;
            process_buffer = temp;
            
            // 通知处理任务
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            xSemaphoreGiveFromISR(buffer_ready_sem, &xHigherPriorityTaskWoken);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
    }
}

// 数据处理任务
void Process_Task(void *param) {
    while(1) {
        // 等待缓冲区就绪
        if(xSemaphoreTake(buffer_ready_sem, portMAX_DELAY) == pdTRUE) {
            uint32_t start_time = xTaskGetTickCount();
            
            // 处理整个缓冲区
            float average = 0;
            float max_value = 0;
            float min_value = 4095;
            
            for(uint16_t i = 0; i < BUFFER_SIZE; i++) {
                float value = (float)process_buffer[i] * 3.3f / 4096.0f;
                average += value;
                
                if(value > max_value) max_value = value;
                if(value < min_value) min_value = value;
            }
            
            average /= BUFFER_SIZE;
            
            uint32_t process_time = xTaskGetTickCount() - start_time;
            
            printf("Processed %d samples in %d ms\n", BUFFER_SIZE, process_time);
            printf("  Average: %.3fV, Max: %.3fV, Min: %.3fV\n",
                   average, max_value, min_value);
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置ADC（100kHz采样率）
    MX_ADC1_Init();
    
    // 配置中断优先级
    HAL_NVIC_SetPriority(ADC1_IRQn, 6, 0);
    HAL_NVIC_EnableIRQ(ADC1_IRQn);
    
    // 创建信号量
    buffer_ready_sem = xSemaphoreCreateBinary();
    
    if(buffer_ready_sem != NULL) {
        // 创建处理任务
        xTaskCreate(Process_Task, "Process", 512, NULL, 3, NULL);
        
        // 启动ADC
        HAL_ADC_Start_IT(&hadc1);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**优化效果**：
- 中断频率：10,000次/秒
- 每次中断时间：~2us（只做读取和存储）
- CPU占用：2us × 10,000 = 20ms/s = 2%
- 批量处理：每12.8ms处理一次（128个样本）


## 验证

### 验证方法

1. **编译项目**
   ```bash
   # 在STM32CubeIDE中
   Project → Build Project
   
   # 或使用命令行
   make
   ```

2. **下载到开发板**
   - 连接开发板
   - 点击"Debug"或"Run"按钮
   - 程序自动下载并运行

3. **测试中断响应**
   - 触发按键中断
   - 观察串口输出
   - 检查LED状态变化

4. **测量性能**
   - 使用示波器测量中断响应时间
   - 使用逻辑分析仪观察任务切换
   - 检查系统CPU占用率

### 预期结果

**正常工作**：
- 中断能够正确触发
- 任务能够及时响应中断
- 数据传递正确无误
- 系统运行稳定

**性能指标**：
- 中断响应时间：< 10us
- ISR执行时间：< 50us
- 任务唤醒延迟：< 1ms
- CPU占用率：< 50%

### 测试要点

1. **功能测试**
   - [ ] 中断能够正确触发
   - [ ] FromISR函数工作正常
   - [ ] 任务能够接收中断通知
   - [ ] 数据传递完整准确

2. **性能测试**
   - [ ] 测量中断响应时间
   - [ ] 测量ISR执行时间
   - [ ] 测量任务唤醒延迟
   - [ ] 检查CPU占用率

3. **压力测试**
   - [ ] 高频中断下系统稳定性
   - [ ] 多个中断同时触发
   - [ ] 队列满时的处理
   - [ ] 长时间运行稳定性


## 故障排除

### 问题1：系统崩溃或死机

**现象**：
- 系统运行一段时间后死机
- 触发中断后系统崩溃
- 串口输出乱码或停止

**可能原因**：
1. 在中断中调用了普通API（非FromISR）
2. 中断优先级配置错误
3. 栈溢出

**解决方法**：

```c
// 1. 检查是否使用了FromISR函数
// ❌ 错误
void EXTI_IRQHandler(void) {
    xSemaphoreGive(sem);  // 错误！应该用FromISR版本
}

// ✅ 正确
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 2. 检查中断优先级
void CheckPriority(void) {
    uint32_t priority = NVIC_GetPriority(EXTI0_IRQn);
    uint32_t max_syscall = configMAX_SYSCALL_INTERRUPT_PRIORITY >> 4;
    
    if(priority < max_syscall) {
        printf("ERROR: Priority too high to call RTOS API!\n");
        printf("Current: %d, Required: >= %d\n", priority, max_syscall);
    }
}

// 3. 启用栈溢出检测
// FreeRTOSConfig.h
#define configCHECK_FOR_STACK_OVERFLOW  2

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    printf("Stack overflow in task: %s\n", pcTaskName);
    while(1);  // 停止系统
}
```



### 问题2：任务无法被中断唤醒

**现象**：
- 中断触发了，但任务没有响应
- 任务一直处于阻塞状态
- 数据没有传递到任务

**可能原因**：
1. 忘记调用portYIELD_FROM_ISR()
2. 信号量或队列未创建
3. 任务优先级太低

**解决方法**：

```c
// 1. 确保调用portYIELD_FROM_ISR()
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    
    // 必须调用！否则任务不会立即切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}

// 2. 检查信号量是否创建成功
SemaphoreHandle_t sem = xSemaphoreCreateBinary();
if(sem == NULL) {
    printf("ERROR: Failed to create semaphore!\n");
    printf("Free heap: %d bytes\n", xPortGetFreeHeapSize());
}

// 3. 提高任务优先级
// 确保处理任务的优先级高于其他任务
xTaskCreate(Handler_Task, "Handler", 256, NULL, 5, NULL);  // 高优先级
```

### 问题3：中断响应慢

**现象**：
- 中断延迟很大
- 实时性不满足要求
- 系统响应迟钝

**可能原因**：
1. ISR执行时间太长
2. 中断优先级太低
3. 临界区太长

**解决方法**：

```c
// 1. 缩短ISR执行时间
// ❌ 不好
void EXTI_IRQHandler(void) {
    float result = ComplexCalculation();  // 耗时
    UpdateDisplay(result);                // 耗时
    SaveToFlash(result);                  // 耗时
}

// ✅ 更好
void EXTI_IRQHandler(void) {
    uint8_t data = ReadData();  // 快速读取
    
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(queue, &data, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 2. 提高中断优先级
HAL_NVIC_SetPriority(EXTI0_IRQn, 6, 0);  // 较高优先级

// 3. 缩短临界区
// ❌ 不好
taskENTER_CRITICAL();
ReadSensor();
ProcessData();
WriteToFlash();
taskEXIT_CRITICAL();

// ✅ 更好
ReadSensor();
ProcessData();

taskENTER_CRITICAL();
UpdateSharedData();  // 只保护必要的操作
taskEXIT_CRITICAL();

WriteToFlash();
```

### 问题4：数据丢失

**现象**：
- 队列满，数据被丢弃
- 中断触发但数据没有处理
- 数据不完整

**可能原因**：
1. 队列太小
2. 处理任务太慢
3. 中断频率太高

**解决方法**：

```c
// 1. 增大队列
// ❌ 太小
QueueHandle_t queue = xQueueCreate(5, sizeof(Data_t));

// ✅ 更大
QueueHandle_t queue = xQueueCreate(50, sizeof(Data_t));

// 2. 检查队列状态
void Monitor_Task(void *param) {
    while(1) {
        UBaseType_t items = uxQueueMessagesWaiting(queue);
        UBaseType_t spaces = uxQueueSpacesAvailable(queue);
        
        if(spaces < 5) {
            printf("WARNING: Queue almost full! (%d/%d)\n", 
                   items, items + spaces);
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 3. 使用覆盖队列（只保留最新数据）
QueueHandle_t queue = xQueueCreate(1, sizeof(Data_t));

void EXTI_IRQHandler(void) {
    Data_t data = ReadData();
    
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    // 覆盖旧数据
    xQueueOverwriteFromISR(queue, &data, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 4. 使用批量处理
#define BATCH_SIZE 10
Data_t batch[BATCH_SIZE];
uint8_t batch_count = 0;

void EXTI_IRQHandler(void) {
    batch[batch_count++] = ReadData();
    
    if(batch_count >= BATCH_SIZE) {
        batch_count = 0;
        
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(queue, batch, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```


## 最佳实践

### 1. 中断服务函数设计原则

```c
// ✅ 好的ISR设计
void Good_IRQHandler(void) {
    // 1. 快速读取硬件
    uint8_t data = ReadHardwareRegister();
    
    // 2. 清除中断标志
    ClearInterruptFlag();
    
    // 3. 发送数据到任务
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(queue, &data, &xHigherPriorityTaskWoken);
    
    // 4. 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// ❌ 不好的ISR设计
void Bad_IRQHandler(void) {
    // 1. 复杂计算
    float result = sqrt(data * 3.14159);
    
    // 2. 字符串处理
    sprintf(buffer, "Result: %.2f", result);
    
    // 3. 文件操作
    WriteToFile(buffer);
    
    // 4. 延时
    HAL_Delay(100);
    
    // 5. 忘记清除中断标志
    // ClearInterruptFlag();  // 忘记了！
}
```

### 2. 选择合适的通信机制

```c
// 场景1：简单通知，不需要数据
// 使用：任务通知（最快）
vTaskNotifyGiveFromISR(task_handle, &xHigherPriorityTaskWoken);

// 场景2：简单通知，需要计数
// 使用：计数信号量
xSemaphoreGiveFromISR(count_sem, &xHigherPriorityTaskWoken);

// 场景3：传递数据，保持顺序
// 使用：队列
xQueueSendFromISR(queue, &data, &xHigherPriorityTaskWoken);

// 场景4：传递简单数值
// 使用：任务通知（带值）
xTaskNotifyFromISR(task_handle, value, eSetValueWithOverwrite, &xHigherPriorityTaskWoken);

// 场景5：多个事件标志
// 使用：事件标志组
xEventGroupSetBitsFromISR(event_group, EVENT_BIT, &xHigherPriorityTaskWoken);
```

### 3. 中断优先级配置指南

```c
// 优先级配置建议
void ConfigureInterruptPriorities(void) {
    // 0-4: 最高优先级（不调用RTOS API）
    // 用于：紧急事件、安全关键功能
    HAL_NVIC_SetPriority(EMERGENCY_IRQn, 2, 0);
    
    // 5-7: 高优先级（可以调用RTOS API）
    // 用于：实时数据采集、高速通信
    HAL_NVIC_SetPriority(ADC_IRQn, 6, 0);
    HAL_NVIC_SetPriority(SPI_IRQn, 7, 0);
    
    // 8-11: 中优先级（可以调用RTOS API）
    // 用于：普通通信、定时器
    HAL_NVIC_SetPriority(USART_IRQn, 9, 0);
    HAL_NVIC_SetPriority(TIM_IRQn, 10, 0);
    
    // 12-14: 低优先级（可以调用RTOS API）
    // 用于：非关键事件、按键
    HAL_NVIC_SetPriority(BUTTON_IRQn, 13, 0);
    
    // 15: 最低优先级（RTOS内部使用）
    // 不要使用！
}
```

### 4. 性能优化检查清单

- [ ] ISR执行时间 < 50us
- [ ] 使用FromISR函数
- [ ] 正确调用portYIELD_FROM_ISR()
- [ ] 中断优先级配置正确
- [ ] 队列大小足够
- [ ] 临界区尽可能短
- [ ] 避免在ISR中使用浮点运算
- [ ] 使用DMA减少中断频率
- [ ] 批量处理高频数据
- [ ] 定期监控系统性能


## 总结

本教程深入讲解了RTOS环境下的中断管理和延迟处理技术。关键要点：

1. **中断优先级**：正确配置中断优先级，区分RTOS管理和非管理的中断
2. **FromISR函数**：在中断中必须使用FromISR版本的API
3. **延迟处理**：中断中只做最少的工作，复杂处理交给任务
4. **通信机制**：根据场景选择合适的通信方式（信号量、队列、任务通知）
5. **性能优化**：缩短ISR时间，使用DMA，批量处理

掌握这些技术后，你就能构建高效、稳定的实时嵌入式系统。


## 扩展阅读

- [RTOS任务管理基础](../beginner/02-rtos-task-management.html)
- [RTOS调度算法详解](../beginner/03-rtos-scheduling.html)
- [优先级反转问题与解决](./03-priority-inversion.html)
- [FreeRTOS官方文档 - 中断管理](https://www.freertos.org/RTOS-interrupt-service-routines.html)
- ARM Cortex-M中断系统参考手册


## 练习题

1. 解释为什么在中断中不能调用普通的RTOS API函数？
2. 什么是延迟处理？为什么需要延迟处理？
3. 比较信号量、队列和任务通知的优缺点，说明各自的适用场景。
4. 如何配置中断优先级才能在ISR中调用FromISR函数？
5. 设计一个高频ADC采集系统，要求采样率100kHz，如何优化以减少CPU占用？

