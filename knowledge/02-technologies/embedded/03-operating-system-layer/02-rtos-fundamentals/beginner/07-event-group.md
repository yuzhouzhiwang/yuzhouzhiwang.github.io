---
title: "事件标志组(Event Group)应用：实现RTOS多任务高效同步"
description: "深入学习RTOS事件标志组的核心概念和实践应用。掌握事件标志组原理、位操作技巧、等待机制和同步应用方法，通过丰富的代码示例学会构建高效的多任务同步系统。"
slug: "event-group"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 事件标志组
  - 事件同步
  - 位标志
  - 多任务同步
  - FreeRTOS
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/05-mutex.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/06-message-queue.md"
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/02-ipc-comparison.md"

# 学习信息
estimated_time: 35
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
  - RTOS事件标志组
  - 事件同步
  - 位标志操作
  - 多任务同步
  - FreeRTOS事件组
  - 任务协调
cover_image: ""
---


# 事件标志组(Event Group)应用：实现RTOS多任务高效同步

## 概述

### 什么是事件标志组？

**事件标志组(Event Group)**是RTOS中用于多任务同步的机制，它使用位标志来表示多个事件的状态。每个事件标志组包含一组事件位，每个位代表一个独立的事件。

**生活中的类比**：

想象一个项目团队的任务看板：
- 看板上有多个任务状态灯（事件位）
- 每个灯可以是亮（事件发生）或灭（事件未发生）
- 项目经理可以等待某些灯全部亮起（所有事件完成）
- 或者等待任意一个灯亮起（任一事件完成）
- 查看看板后可以选择清除某些灯（清除事件标志）

### 为什么需要事件标志组？

在多任务系统中，经常需要等待多个事件的组合：

**问题场景：多条件等待**
```c
// 任务需要等待多个条件同时满足
void SystemTask(void *param) {
    while(1) {
        // 需要等待：
        // 1. 传感器数据就绪
        // 2. 网络连接成功
        // 3. 存储空间充足
        
        // 如何优雅地等待这些条件？
    }
}
```

**传统方法的问题**：
- 使用多个信号量：代码复杂，难以维护
- 轮询检查：浪费CPU资源
- 全局变量：不安全，容易出错

**事件标志组的优势**：
- 一个对象管理多个事件
- 支持灵活的等待条件（AND/OR）
- 代码简洁，逻辑清晰
- 高效的任务同步

### 事件标志组 vs 信号量

| 特性 | 事件标志组 | 信号量 |
|------|-----------|--------|
| **事件数量** | 多个事件（24位或更多） | 单个事件 |
| **等待条件** | 支持AND/OR组合 | 单一条件 |
| **事件状态** | 持久保存，需手动清除 | 自动清除 |
| **典型场景** | 多条件同步 | 单一事件通知 |
| **复杂度** | 较高 | 较低 |

**选择建议**：
- 需要等待多个事件的组合 → 使用事件标志组
- 只需要单一事件通知 → 使用信号量


## 核心概念

### 事件位结构

事件标志组使用位来表示事件状态：

```
事件标志组（24位）：
位23 位22 ... 位2  位1  位0
 0    1   ...  1    0    1

每个位代表一个事件：
- 0：事件未发生
- 1：事件已发生
```

**FreeRTOS事件标志组**：
- 标准版本：24位可用（位0-23）
- 位24-31保留给系统使用
- 每个位独立表示一个事件

### 位操作基础

```c
// 定义事件位
#define EVENT_BIT_0  (1 << 0)  // 0x01
#define EVENT_BIT_1  (1 << 1)  // 0x02
#define EVENT_BIT_2  (1 << 2)  // 0x04
#define EVENT_BIT_3  (1 << 3)  // 0x08

// 组合多个事件位
#define ALL_EVENTS   (EVENT_BIT_0 | EVENT_BIT_1 | EVENT_BIT_2)

// 示例：传感器系统事件定义
#define SENSOR_DATA_READY    (1 << 0)  // 传感器数据就绪
#define NETWORK_CONNECTED    (1 << 1)  // 网络连接成功
#define STORAGE_AVAILABLE    (1 << 2)  // 存储空间充足
#define BATTERY_OK           (1 << 3)  // 电池电量正常
```

### 等待模式

事件标志组支持两种等待模式：

**1. AND模式（所有事件）**
```c
// 等待所有指定事件都发生
xEventGroupWaitBits(
    event_group,
    EVENT_BIT_0 | EVENT_BIT_1 | EVENT_BIT_2,  // 等待这些位
    pdTRUE,   // 等待成功后清除这些位
    pdTRUE,   // AND模式：所有位都必须为1
    portMAX_DELAY
);
```

**2. OR模式（任一事件）**
```c
// 等待任意一个事件发生
xEventGroupWaitBits(
    event_group,
    EVENT_BIT_0 | EVENT_BIT_1 | EVENT_BIT_2,  // 等待这些位
    pdTRUE,   // 等待成功后清除这些位
    pdFALSE,  // OR模式：任意一位为1即可
    portMAX_DELAY
);
```


## 基本操作

### 创建事件标志组

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 声明事件标志组句柄
EventGroupHandle_t system_events;

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 创建事件标志组
    system_events = xEventGroupCreate();
    
    if(system_events != NULL) {
        printf("Event group created successfully\n");
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    } else {
        printf("Failed to create event group\n");
    }
    
    while(1);
}
```

### 设置事件位

```c
// 在任务中设置事件位
EventBits_t xEventGroupSetBits(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToSet  // 要设置的位
);

// 示例：设置单个事件
xEventGroupSetBits(system_events, SENSOR_DATA_READY);

// 示例：同时设置多个事件
xEventGroupSetBits(system_events, 
                   SENSOR_DATA_READY | NETWORK_CONNECTED);
```

```c
// 在中断中设置事件位
BaseType_t xEventGroupSetBitsFromISR(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToSet,
    BaseType_t *pxHigherPriorityTaskWoken
);

// 中断服务函数示例
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 设置事件位
    xEventGroupSetBitsFromISR(system_events, 
                              SENSOR_DATA_READY,
                              &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 等待事件位

```c
// 等待事件位
EventBits_t xEventGroupWaitBits(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToWaitFor,  // 要等待的位
    const BaseType_t xClearOnExit,      // 成功后是否清除
    const BaseType_t xWaitForAllBits,   // AND(pdTRUE)或OR(pdFALSE)
    TickType_t xTicksToWait             // 等待时间
);

// 示例：等待所有事件（AND模式）
EventBits_t bits = xEventGroupWaitBits(
    system_events,
    SENSOR_DATA_READY | NETWORK_CONNECTED,  // 等待这两个事件
    pdTRUE,        // 等待成功后清除这些位
    pdTRUE,        // AND模式：两个事件都必须发生
    portMAX_DELAY  // 永久等待
);

// 示例：等待任一事件（OR模式）
EventBits_t bits = xEventGroupWaitBits(
    system_events,
    SENSOR_DATA_READY | NETWORK_CONNECTED,  // 等待这两个事件
    pdTRUE,        // 等待成功后清除这些位
    pdFALSE,       // OR模式：任一事件发生即可
    portMAX_DELAY  // 永久等待
);
```

### 清除事件位

```c
// 清除事件位
EventBits_t xEventGroupClearBits(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToClear  // 要清除的位
);

// 示例：清除单个事件
xEventGroupClearBits(system_events, SENSOR_DATA_READY);

// 示例：清除多个事件
xEventGroupClearBits(system_events, 
                     SENSOR_DATA_READY | NETWORK_CONNECTED);
```

### 获取事件位状态

```c
// 获取当前事件位状态
EventBits_t xEventGroupGetBits(EventGroupHandle_t xEventGroup);

// 示例：检查事件状态
EventBits_t current_bits = xEventGroupGetBits(system_events);

if(current_bits & SENSOR_DATA_READY) {
    printf("Sensor data is ready\n");
}

if(current_bits & NETWORK_CONNECTED) {
    printf("Network is connected\n");
}
```


## 实际应用场景

### 场景1：系统初始化同步

等待多个子系统初始化完成：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义初始化事件
#define INIT_HARDWARE    (1 << 0)
#define INIT_NETWORK     (1 << 1)
#define INIT_FILESYSTEM  (1 << 2)
#define INIT_SENSORS     (1 << 3)

#define ALL_INIT_DONE    (INIT_HARDWARE | INIT_NETWORK | \
                          INIT_FILESYSTEM | INIT_SENSORS)

// 事件标志组句柄
EventGroupHandle_t init_events;

// 硬件初始化任务
void HardwareInitTask(void *param) {
    printf("[Hardware] Initializing...\n");
    vTaskDelay(pdMS_TO_TICKS(500));
    
    // 初始化完成，设置事件位
    xEventGroupSetBits(init_events, INIT_HARDWARE);
    printf("[Hardware] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 网络初始化任务
void NetworkInitTask(void *param) {
    printf("[Network] Initializing...\n");
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    xEventGroupSetBits(init_events, INIT_NETWORK);
    printf("[Network] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 文件系统初始化任务
void FilesystemInitTask(void *param) {
    printf("[Filesystem] Initializing...\n");
    vTaskDelay(pdMS_TO_TICKS(800));
    
    xEventGroupSetBits(init_events, INIT_FILESYSTEM);
    printf("[Filesystem] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 传感器初始化任务
void SensorsInitTask(void *param) {
    printf("[Sensors] Initializing...\n");
    vTaskDelay(pdMS_TO_TICKS(600));
    
    xEventGroupSetBits(init_events, INIT_SENSORS);
    printf("[Sensors] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 主应用任务
void MainAppTask(void *param) {
    printf("[MainApp] Waiting for all subsystems to initialize...\n");
    
    // 等待所有初始化完成（AND模式）
    EventBits_t bits = xEventGroupWaitBits(
        init_events,
        ALL_INIT_DONE,  // 等待所有初始化事件
        pdFALSE,        // 不清除事件位
        pdTRUE,         // AND模式：所有事件都必须完成
        portMAX_DELAY   // 永久等待
    );
    
    printf("[MainApp] All subsystems initialized!\n");
    printf("[MainApp] Starting main application...\n");
    
    while(1) {
        // 主应用逻辑
        printf("[MainApp] Running...\n");
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建事件标志组
    init_events = xEventGroupCreate();
    
    if(init_events != NULL) {
        // 创建初始化任务
        xTaskCreate(HardwareInitTask, "HW_Init", 256, NULL, 2, NULL);
        xTaskCreate(NetworkInitTask, "Net_Init", 256, NULL, 2, NULL);
        xTaskCreate(FilesystemInitTask, "FS_Init", 256, NULL, 2, NULL);
        xTaskCreate(SensorsInitTask, "Sensor_Init", 256, NULL, 2, NULL);
        
        // 创建主应用任务
        xTaskCreate(MainAppTask, "MainApp", 256, NULL, 1, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[MainApp] Waiting for all subsystems to initialize...
[Hardware] Initializing...
[Network] Initializing...
[Filesystem] Initializing...
[Sensors] Initializing...
[Hardware] Initialization complete
[Sensors] Initialization complete
[Filesystem] Initialization complete
[Network] Initialization complete
[MainApp] All subsystems initialized!
[MainApp] Starting main application...
[MainApp] Running...
```



### 场景2：数据采集系统

等待多个传感器数据就绪：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义传感器事件
#define TEMP_SENSOR_READY     (1 << 0)
#define HUMIDITY_SENSOR_READY (1 << 1)
#define PRESSURE_SENSOR_READY (1 << 2)

#define ALL_SENSORS_READY     (TEMP_SENSOR_READY | \
                               HUMIDITY_SENSOR_READY | \
                               PRESSURE_SENSOR_READY)

// 事件标志组
EventGroupHandle_t sensor_events;

// 传感器数据结构
typedef struct {
    float temperature;
    float humidity;
    float pressure;
    uint32_t timestamp;
} SensorData_t;

SensorData_t sensor_data;

// 温度传感器任务
void TemperatureSensorTask(void *param) {
    while(1) {
        // 读取温度传感器
        sensor_data.temperature = 25.5f;  // 模拟读取
        
        printf("[Temp] Data ready: %.1f°C\n", sensor_data.temperature);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, TEMP_SENSOR_READY);
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 湿度传感器任务
void HumiditySensorTask(void *param) {
    while(1) {
        // 读取湿度传感器
        sensor_data.humidity = 60.0f;  // 模拟读取
        
        printf("[Humidity] Data ready: %.1f%%\n", sensor_data.humidity);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, HUMIDITY_SENSOR_READY);
        
        vTaskDelay(pdMS_TO_TICKS(1100));
    }
}

// 气压传感器任务
void PressureSensorTask(void *param) {
    while(1) {
        // 读取气压传感器
        sensor_data.pressure = 1013.25f;  // 模拟读取
        
        printf("[Pressure] Data ready: %.2f hPa\n", sensor_data.pressure);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, PRESSURE_SENSOR_READY);
        
        vTaskDelay(pdMS_TO_TICKS(900));
    }
}

// 数据处理任务
void DataProcessTask(void *param) {
    while(1) {
        printf("\n[Process] Waiting for all sensor data...\n");
        
        // 等待所有传感器数据就绪
        EventBits_t bits = xEventGroupWaitBits(
            sensor_events,
            ALL_SENSORS_READY,  // 等待所有传感器
            pdTRUE,             // 等待成功后清除事件位
            pdTRUE,             // AND模式：所有传感器都必须就绪
            portMAX_DELAY       // 永久等待
        );
        
        // 所有数据就绪，进行处理
        sensor_data.timestamp = xTaskGetTickCount();
        
        printf("[Process] All data ready!\n");
        printf("[Process] Temperature: %.1f°C\n", sensor_data.temperature);
        printf("[Process] Humidity: %.1f%%\n", sensor_data.humidity);
        printf("[Process] Pressure: %.2f hPa\n", sensor_data.pressure);
        printf("[Process] Timestamp: %d ms\n\n", sensor_data.timestamp);
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建事件标志组
    sensor_events = xEventGroupCreate();
    
    if(sensor_events != NULL) {
        // 创建传感器任务
        xTaskCreate(TemperatureSensorTask, "Temp", 256, NULL, 2, NULL);
        xTaskCreate(HumiditySensorTask, "Humidity", 256, NULL, 2, NULL);
        xTaskCreate(PressureSensorTask, "Pressure", 256, NULL, 2, NULL);
        
        // 创建数据处理任务
        xTaskCreate(DataProcessTask, "Process", 256, NULL, 3, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[Process] Waiting for all sensor data...
[Temp] Data ready: 25.5°C
[Pressure] Data ready: 1013.25 hPa
[Humidity] Data ready: 60.0%
[Process] All data ready!
[Process] Temperature: 25.5°C
[Process] Humidity: 60.0%
[Process] Pressure: 1013.25 hPa
[Process] Timestamp: 1100 ms

[Process] Waiting for all sensor data...
[Temp] Data ready: 25.5°C
[Pressure] Data ready: 1013.25 hPa
[Humidity] Data ready: 60.0%
[Process] All data ready!
```


### 场景3：任务协调（OR模式）

等待任意一个事件发生：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义输入事件
#define BUTTON_PRESSED    (1 << 0)
#define UART_DATA_RX      (1 << 1)
#define TIMER_EXPIRED     (1 << 2)

#define ANY_INPUT_EVENT   (BUTTON_PRESSED | UART_DATA_RX | TIMER_EXPIRED)

// 事件标志组
EventGroupHandle_t input_events;

// 按键任务
void ButtonTask(void *param) {
    while(1) {
        // 模拟按键检测
        vTaskDelay(pdMS_TO_TICKS(3000));
        
        printf("[Button] Button pressed!\n");
        xEventGroupSetBits(input_events, BUTTON_PRESSED);
    }
}

// UART接收任务
void UARTTask(void *param) {
    while(1) {
        // 模拟UART数据接收
        vTaskDelay(pdMS_TO_TICKS(5000));
        
        printf("[UART] Data received!\n");
        xEventGroupSetBits(input_events, UART_DATA_RX);
    }
}

// 定时器任务
void TimerTask(void *param) {
    while(1) {
        // 模拟定时器超时
        vTaskDelay(pdMS_TO_TICKS(7000));
        
        printf("[Timer] Timer expired!\n");
        xEventGroupSetBits(input_events, TIMER_EXPIRED);
    }
}

// 事件处理任务
void EventHandlerTask(void *param) {
    while(1) {
        printf("\n[Handler] Waiting for any input event...\n");
        
        // 等待任意一个事件发生（OR模式）
        EventBits_t bits = xEventGroupWaitBits(
            input_events,
            ANY_INPUT_EVENT,  // 等待任意输入事件
            pdTRUE,           // 等待成功后清除事件位
            pdFALSE,          // OR模式：任一事件发生即可
            portMAX_DELAY     // 永久等待
        );
        
        // 检查是哪个事件发生了
        if(bits & BUTTON_PRESSED) {
            printf("[Handler] Handling button press event\n");
        }
        
        if(bits & UART_DATA_RX) {
            printf("[Handler] Handling UART data event\n");
        }
        
        if(bits & TIMER_EXPIRED) {
            printf("[Handler] Handling timer event\n");
        }
        
        printf("[Handler] Event handled\n\n");
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建事件标志组
    input_events = xEventGroupCreate();
    
    if(input_events != NULL) {
        // 创建输入任务
        xTaskCreate(ButtonTask, "Button", 256, NULL, 2, NULL);
        xTaskCreate(UARTTask, "UART", 256, NULL, 2, NULL);
        xTaskCreate(TimerTask, "Timer", 256, NULL, 2, NULL);
        
        // 创建事件处理任务
        xTaskCreate(EventHandlerTask, "Handler", 256, NULL, 3, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[Handler] Waiting for any input event...
[Button] Button pressed!
[Handler] Handling button press event
[Handler] Event handled

[Handler] Waiting for any input event...
[UART] Data received!
[Handler] Handling UART data event
[Handler] Event handled

[Handler] Waiting for any input event...
[Timer] Timer expired!
[Handler] Handling timer event
[Handler] Event handled
```


## 使用技巧

### 技巧1：事件位命名规范

使用清晰的命名约定：

```c
// 推荐：使用描述性名称
#define SENSOR_TEMP_READY      (1 << 0)
#define SENSOR_HUMIDITY_READY  (1 << 1)
#define NETWORK_CONNECTED      (1 << 2)
#define STORAGE_AVAILABLE      (1 << 3)

// 不推荐：使用通用名称
#define BIT_0  (1 << 0)
#define BIT_1  (1 << 1)
#define BIT_2  (1 << 2)
```

### 技巧2：检查返回值

```c
// 检查等待结果
EventBits_t bits = xEventGroupWaitBits(
    event_group,
    REQUIRED_EVENTS,
    pdTRUE,
    pdTRUE,
    pdMS_TO_TICKS(5000)  // 超时5秒
);

// 检查是否超时
if((bits & REQUIRED_EVENTS) == REQUIRED_EVENTS) {
    printf("All events occurred\n");
} else {
    printf("Timeout! Events: 0x%02X\n", bits);
}
```

### 技巧3：选择性清除事件位

```c
// 等待事件但不清除（用于多个任务等待同一事件）
EventBits_t bits = xEventGroupWaitBits(
    event_group,
    EVENT_BIT_0,
    pdFALSE,  // 不清除事件位
    pdTRUE,
    portMAX_DELAY
);

// 手动清除特定事件位
xEventGroupClearBits(event_group, EVENT_BIT_0);
```

### 技巧4：同步多个任务

```c
// 定义同步点事件
#define SYNC_POINT  (1 << 0)

// 任务1
void Task1(void *param) {
    while(1) {
        // 执行任务1的工作
        DoWork1();
        
        // 到达同步点
        xEventGroupSetBits(sync_events, SYNC_POINT);
        
        // 等待其他任务到达同步点
        xEventGroupWaitBits(sync_events, SYNC_POINT, pdFALSE, pdTRUE, portMAX_DELAY);
        
        // 继续执行
    }
}

// 任务2
void Task2(void *param) {
    while(1) {
        // 执行任务2的工作
        DoWork2();
        
        // 到达同步点
        xEventGroupSetBits(sync_events, SYNC_POINT);
        
        // 等待其他任务到达同步点
        xEventGroupWaitBits(sync_events, SYNC_POINT, pdFALSE, pdTRUE, portMAX_DELAY);
        
        // 继续执行
    }
}
```


## 常见问题

### Q1: 事件标志组和信号量有什么区别？

**A**: 主要区别在于事件数量和等待条件：

**事件标志组**：
- 可以表示多个事件（24位）
- 支持AND/OR组合等待
- 事件状态持久保存
- 适用于多条件同步

**信号量**：
- 只能表示单个事件
- 只支持单一条件等待
- 自动清除状态
- 适用于简单的事件通知

**示例对比**：
```c
// 信号量：等待单个事件
xSemaphoreTake(sem, portMAX_DELAY);

// 事件标志组：等待多个事件组合
xEventGroupWaitBits(events, 
                    EVENT_A | EVENT_B | EVENT_C,
                    pdTRUE, pdTRUE, portMAX_DELAY);
```

### Q2: 什么时候使用AND模式，什么时候使用OR模式？

**A**: 根据业务逻辑选择：

**AND模式（所有事件）**：
- 需要所有条件都满足才能继续
- 示例：系统初始化（所有子系统都就绪）
- 示例：数据采集（所有传感器都有数据）

**OR模式（任一事件）**：
- 任意一个条件满足就可以继续
- 示例：输入处理（按键、UART、定时器任一触发）
- 示例：错误处理（任一错误发生）

```c
// AND模式：等待所有传感器就绪
xEventGroupWaitBits(events, ALL_SENSORS, pdTRUE, pdTRUE, timeout);

// OR模式：等待任一输入事件
xEventGroupWaitBits(events, ANY_INPUT, pdTRUE, pdFALSE, timeout);
```

### Q3: 是否应该在等待后清除事件位？

**A**: 取决于使用场景：

**应该清除（xClearOnExit = pdTRUE）**：
- 事件是一次性的（如按键按下）
- 避免重复处理同一事件
- 大多数情况下推荐

**不应该清除（xClearOnExit = pdFALSE）**：
- 多个任务需要等待同一事件
- 事件状态需要持久保存
- 需要手动控制清除时机

```c
// 清除事件位（推荐）
xEventGroupWaitBits(events, EVENT_BIT, pdTRUE, pdTRUE, timeout);

// 不清除事件位（多任务等待）
xEventGroupWaitBits(events, EVENT_BIT, pdFALSE, pdTRUE, timeout);
// 稍后手动清除
xEventGroupClearBits(events, EVENT_BIT);
```

### Q4: 事件标志组有多少个可用位？

**A**: FreeRTOS事件标志组：

- **可用位数**：24位（位0-23）
- **保留位**：8位（位24-31）系统使用
- **总共**：32位

```c
// 可以使用的位
#define EVENT_BIT_0   (1 << 0)   // ✅ 可用
#define EVENT_BIT_23  (1 << 23)  // ✅ 可用

// 不能使用的位
#define EVENT_BIT_24  (1 << 24)  // ❌ 保留给系统
#define EVENT_BIT_31  (1 << 31)  // ❌ 保留给系统
```

**建议**：
- 24位对大多数应用足够
- 如果需要更多事件，考虑使用多个事件标志组
- 或者重新设计事件结构

### Q5: 如何调试事件标志组问题？

**A**: 调试技巧：

**1. 打印事件位状态**
```c
EventBits_t bits = xEventGroupGetBits(event_group);
printf("Current events: 0x%06X\n", bits);

// 检查特定位
if(bits & EVENT_BIT_0) {
    printf("Event 0 is set\n");
}
```

**2. 添加超时检测**
```c
EventBits_t bits = xEventGroupWaitBits(
    event_group,
    REQUIRED_EVENTS,
    pdTRUE,
    pdTRUE,
    pdMS_TO_TICKS(5000)  // 5秒超时
);

if((bits & REQUIRED_EVENTS) != REQUIRED_EVENTS) {
    printf("Timeout! Missing events: 0x%06X\n", 
           REQUIRED_EVENTS & ~bits);
}
```

**3. 记录事件设置**
```c
void SetEventWithLog(EventGroupHandle_t events, EventBits_t bits) {
    printf("[%s] Setting events: 0x%06X\n", 
           pcTaskGetName(NULL), bits);
    xEventGroupSetBits(events, bits);
}
```


## 总结

### 核心要点

1. **事件标志组概念**
   - 使用位标志表示多个事件状态
   - 每个位独立表示一个事件
   - 支持灵活的等待条件组合

2. **基本操作**
   - `xEventGroupCreate()`：创建事件标志组
   - `xEventGroupSetBits()`：设置事件位
   - `xEventGroupWaitBits()`：等待事件位
   - `xEventGroupClearBits()`：清除事件位

3. **等待模式**
   - AND模式：等待所有指定事件都发生
   - OR模式：等待任意一个事件发生
   - 支持超时机制

4. **典型应用**
   - 系统初始化同步
   - 多传感器数据采集
   - 多输入源事件处理
   - 任务协调和同步

5. **最佳实践**
   - 使用描述性的事件位名称
   - 根据场景选择AND/OR模式
   - 合理设置超时时间
   - 检查等待返回值
   - 适当清除事件位

### 与其他同步机制对比

| 机制 | 事件数量 | 等待条件 | 典型场景 |
|------|---------|---------|---------|
| **事件标志组** | 多个（24位） | AND/OR组合 | 多条件同步 |
| **信号量** | 单个 | 单一条件 | 简单通知 |
| **互斥量** | 单个 | 资源保护 | 共享资源 |
| **消息队列** | 多个消息 | 数据传递 | 任务通信 |

### 学习检查

完成本文后，你应该能够：

- [ ] 理解事件标志组的概念和工作原理
- [ ] 掌握事件位的定义和操作方法
- [ ] 理解AND和OR等待模式的区别
- [ ] 能够使用事件标志组实现多任务同步
- [ ] 知道何时使用事件标志组而不是其他机制
- [ ] 能够调试事件标志组相关问题


## 延伸阅读

### 相关主题

- [RTOS任务管理](02-rtos-task-management.html) - 了解任务的基本概念
- [信号量使用](04-semaphore.html) - 学习信号量的使用方法
- [互斥量与临界区](05-mutex.html) - 掌握资源保护机制
- [消息队列通信](06-message-queue.html) - 学习任务间数据传递
- [任务间通信对比](../intermediate/02-ipc-comparison.html) - 深入理解各种通信机制

### 参考资料

- [FreeRTOS官方文档 - Event Groups](https://www.freertos.org/event-groups-API.html)
- [FreeRTOS Event Groups Tutorial](https://www.freertos.org/FreeRTOS-Event-Groups.html)
- [Mastering the FreeRTOS Real Time Kernel](https://www.freertos.org/Documentation/RTOS_book.html)

---

**文档版本**: 1.0  
**最后更新**: 2024-01-15  
**作者**: 嵌入式知识平台

