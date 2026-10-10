---
title: "FreeRTOS事件标志组实战：实现高效的多任务同步"
description: "深入学习FreeRTOS事件标志组的实战应用。掌握事件组创建、位设置清除、等待事件、同步应用和实例代码，通过丰富的示例学会构建复杂的多任务同步系统。"
slug: "freertos-event-group"

# 分类信息
domain: "操作系统层"
module: "FreeRTOS"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - FreeRTOS事件组
  - 事件同步
  - 多任务同步
  - 位标志操作
  - 任务协调
prerequisites:
  - "03-operating-system-layer/03-freertos/beginner/01-freertos-quickstart"
  - "03-operating-system-layer/03-freertos/beginner/02-freertos-tasks"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/07-event-group"
related_contents:
  - "03-operating-system-layer/03-freertos/intermediate/01-freertos-timer"
  - "03-operating-system-layer/03-freertos/intermediate/03-freertos-notification"
  - "03-operating-system-layer/03-freertos/intermediate/04-freertos-memory"

# 学习信息
estimated_time: 65
difficulty_score: 5

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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - FreeRTOS事件标志组
  - 事件组实战
  - 多任务同步
  - 位标志操作
  - 事件等待机制
  - 任务协调
cover_image: ""
---

# FreeRTOS事件标志组实战：实现高效的多任务同步

## 学习目标

完成本教程后，你将能够：

- [ ] 深入理解FreeRTOS事件标志组的工作原理和应用场景
- [ ] 掌握事件组的创建、删除和管理方法
- [ ] 熟练使用位操作设置和清除事件标志
- [ ] 理解AND和OR等待模式的区别和应用
- [ ] 掌握从任务和中断中操作事件组的方法
- [ ] 能够使用事件组实现复杂的多任务同步
- [ ] 解决事件组使用中的常见问题和陷阱

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉FreeRTOS的基本概念和任务管理
- 了解RTOS事件标志组的基础知识
- 理解位操作和位掩码的概念
- 掌握FreeRTOS的基本API使用

**技能要求**：
- 能够创建和管理FreeRTOS任务
- 会使用队列和信号量等同步机制
- 了解任务调度和优先级机制
- 掌握基本的调试方法


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| STM32开发板 | 1 | STM32F4 Discovery或类似 | - |
| ST-Link调试器 | 1 | 通常开发板自带 | - |
| USB数据线 | 1 | 用于连接开发板 | - |
| LED灯 | 3-4个 | 用于演示事件效果（可选） | - |
| 按键 | 2-3个 | 用于触发事件（可选） | - |

### 软件准备

- **开发环境**：STM32CubeIDE v1.10+ 或 Keil MDK v5.30+
- **FreeRTOS版本**：V10.3.1+（通过CubeMX自动集成）
- **HAL库版本**：根据芯片型号选择对应版本
- **辅助工具**：串口调试助手（用于查看输出）

### 环境配置

在FreeRTOSConfig.h中确保以下配置：

```c
// 启用事件标志组功能
#define configUSE_16_BIT_TICKS              0

// 时钟节拍频率（1ms）
#define configTICK_RATE_HZ                  1000

// 启用任务通知（可选，用于对比）
#define configUSE_TASK_NOTIFICATIONS        1

// 堆内存大小（确保足够）
#define configTOTAL_HEAP_SIZE               ((size_t)(15 * 1024))
```


## FreeRTOS事件标志组深入理解

### 事件标志组的内部结构

FreeRTOS事件标志组使用一个整数来存储多个事件位：

```
事件标志组（EventBits_t）：
位23 位22 ... 位2  位1  位0
 0    1   ...  1    0    1

- 可用位：位0-23（24位）
- 保留位：位24-31（系统使用）
- 每个位独立表示一个事件状态
```

**数据类型定义**：
```c
// FreeRTOS事件标志组类型
typedef TickType_t EventBits_t;

// 在32位系统上
// EventBits_t = uint32_t
// 可用24位（0x00FFFFFF）
```

### 事件标志组 vs 其他同步机制

| 特性 | 事件标志组 | 信号量 | 队列 | 任务通知 |
|------|-----------|--------|------|---------|
| **事件数量** | 24个 | 1个 | 多个消息 | 1个值 |
| **等待条件** | AND/OR组合 | 单一 | 单一 | 单一 |
| **内存占用** | 中等 | 小 | 大 | 最小 |
| **速度** | 快 | 快 | 中 | 最快 |
| **适用场景** | 多条件同步 | 简单通知 | 数据传递 | 简单通知 |

**选择建议**：
- 需要等待多个事件的组合 → 事件标志组
- 简单的事件通知 → 任务通知或信号量
- 需要传递数据 → 队列
- 多个任务等待同一事件 → 事件标志组或信号量

### 工作原理

```
[任务A] ─────┐
             │
[任务B] ─────┼──→ 设置事件位 ──→ [事件标志组]
             │                      ↓
[中断] ──────┘                   检查等待条件
                                    ↓
                              唤醒等待的任务
                                    ↓
                              [任务C] [任务D]
```

**关键特性**：
- 多个任务可以同时等待同一个事件标志组
- 支持AND模式（所有事件）和OR模式（任一事件）
- 事件位可以自动清除或手动清除
- 支持从中断中设置事件位


## 基本操作

### 创建和删除事件标志组

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 声明事件标志组句柄
EventGroupHandle_t system_events;

// 创建事件标志组
void Create_Event_Group(void) {
    // 动态创建事件标志组
    system_events = xEventGroupCreate();
    
    if(system_events != NULL) {
        printf("Event group created successfully\n");
    } else {
        printf("Failed to create event group\n");
    }
}

// 删除事件标志组
void Delete_Event_Group(void) {
    if(system_events != NULL) {
        vEventGroupDelete(system_events);
        system_events = NULL;
        printf("Event group deleted\n");
    }
}
```

**静态创建方式**（需要启用configSUPPORT_STATIC_ALLOCATION）：
```c
// 静态分配内存
StaticEventGroup_t event_group_buffer;

// 静态创建事件标志组
EventGroupHandle_t static_events = xEventGroupCreateStatic(&event_group_buffer);
```

### 定义事件位

```c
// 使用位移操作定义事件位
#define EVENT_BIT_0     (1 << 0)    // 0x01
#define EVENT_BIT_1     (1 << 1)    // 0x02
#define EVENT_BIT_2     (1 << 2)    // 0x04
#define EVENT_BIT_3     (1 << 3)    // 0x08

// 实际应用中的事件定义
#define SENSOR_DATA_READY       (1 << 0)    // 传感器数据就绪
#define NETWORK_CONNECTED       (1 << 1)    // 网络连接成功
#define STORAGE_AVAILABLE       (1 << 2)    // 存储空间充足
#define BATTERY_OK              (1 << 3)    // 电池电量正常
#define USER_INPUT_RECEIVED     (1 << 4)    // 用户输入接收
#define CALIBRATION_DONE        (1 << 5)    // 校准完成

// 组合多个事件
#define ALL_INIT_EVENTS         (SENSOR_DATA_READY | \
                                 NETWORK_CONNECTED | \
                                 STORAGE_AVAILABLE)

#define SYSTEM_READY            (ALL_INIT_EVENTS | BATTERY_OK)
```

### 设置事件位

```c
// 在任务中设置事件位
void Task_Set_Events(void *param) {
    while(1) {
        // 模拟传感器数据就绪
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // 设置单个事件位
        EventBits_t bits = xEventGroupSetBits(
            system_events,
            SENSOR_DATA_READY
        );
        
        printf("[Task] Set SENSOR_DATA_READY, current bits: 0x%02X\n", bits);
        
        // 设置多个事件位
        bits = xEventGroupSetBits(
            system_events,
            NETWORK_CONNECTED | STORAGE_AVAILABLE
        );
        
        printf("[Task] Set multiple bits, current bits: 0x%02X\n", bits);
    }
}
```

**从中断中设置事件位**：
```c
// 中断服务函数
void EXTI0_IRQHandler(void) {
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        
        // 从中断中设置事件位
        xEventGroupSetBitsFromISR(
            system_events,
            USER_INPUT_RECEIVED,
            &xHigherPriorityTaskWoken
        );
        
        // 如果需要任务切换，触发PendSV
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```

**注意事项**：
- `xEventGroupSetBits()` 返回设置后的事件位值
- `xEventGroupSetBitsFromISR()` 不能在中断中阻塞
- 设置事件位会唤醒所有等待该事件的任务


### 等待事件位

```c
// 等待事件位（AND模式）
void Task_Wait_All_Events(void *param) {
    printf("[WaitAll] Waiting for all initialization events...\n");
    
    // 等待所有初始化事件完成
    EventBits_t bits = xEventGroupWaitBits(
        system_events,
        ALL_INIT_EVENTS,        // 等待这些位
        pdTRUE,                 // 等待成功后清除这些位
        pdTRUE,                 // AND模式：所有位都必须为1
        portMAX_DELAY           // 永久等待
    );
    
    printf("[WaitAll] All events occurred! bits=0x%02X\n", bits);
    
    // 继续执行后续操作
    while(1) {
        printf("[WaitAll] System running...\n");
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

// 等待事件位（OR模式）
void Task_Wait_Any_Event(void *param) {
    while(1) {
        printf("[WaitAny] Waiting for any input event...\n");
        
        // 等待任意一个输入事件
        EventBits_t bits = xEventGroupWaitBits(
            system_events,
            USER_INPUT_RECEIVED | NETWORK_CONNECTED,  // 等待这些位
            pdTRUE,             // 等待成功后清除这些位
            pdFALSE,            // OR模式：任一位为1即可
            portMAX_DELAY       // 永久等待
        );
        
        // 检查是哪个事件发生了
        if(bits & USER_INPUT_RECEIVED) {
            printf("[WaitAny] User input received\n");
        }
        
        if(bits & NETWORK_CONNECTED) {
            printf("[WaitAny] Network connected\n");
        }
    }
}

// 带超时的等待
void Task_Wait_With_Timeout(void *param) {
    while(1) {
        printf("[Timeout] Waiting for events (5s timeout)...\n");
        
        // 等待事件，最多等待5秒
        EventBits_t bits = xEventGroupWaitBits(
            system_events,
            SENSOR_DATA_READY,
            pdTRUE,
            pdTRUE,
            pdMS_TO_TICKS(5000)  // 5秒超时
        );
        
        // 检查是否超时
        if(bits & SENSOR_DATA_READY) {
            printf("[Timeout] Event occurred within timeout\n");
        } else {
            printf("[Timeout] Timeout! No event occurred\n");
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

**xEventGroupWaitBits参数说明**：
```c
EventBits_t xEventGroupWaitBits(
    EventGroupHandle_t xEventGroup,     // 事件标志组句柄
    const EventBits_t uxBitsToWaitFor,  // 要等待的位掩码
    const BaseType_t xClearOnExit,      // 成功后是否清除位
    const BaseType_t xWaitForAllBits,   // AND(pdTRUE)或OR(pdFALSE)
    TickType_t xTicksToWait             // 等待时间（ticks）
);
```

**返回值**：
- 返回等待成功时的事件位值
- 如果超时，返回超时时的事件位值
- 如果xClearOnExit=pdTRUE，返回清除前的值

### 清除事件位

```c
// 清除事件位
void Clear_Event_Bits_Example(void) {
    // 清除单个事件位
    EventBits_t bits = xEventGroupClearBits(
        system_events,
        SENSOR_DATA_READY
    );
    printf("Cleared SENSOR_DATA_READY, remaining bits: 0x%02X\n", bits);
    
    // 清除多个事件位
    bits = xEventGroupClearBits(
        system_events,
        NETWORK_CONNECTED | STORAGE_AVAILABLE
    );
    printf("Cleared multiple bits, remaining bits: 0x%02X\n", bits);
    
    // 清除所有事件位
    bits = xEventGroupClearBits(
        system_events,
        0x00FFFFFF  // 清除所有24位
    );
    printf("Cleared all bits, remaining bits: 0x%02X\n", bits);
}

// 从中断中清除事件位
void UART_IRQHandler(void) {
    if(__HAL_UART_GET_FLAG(&huart2, UART_FLAG_RXNE)) {
        // 读取数据
        uint8_t data = (uint8_t)(huart2.Instance->DR & 0xFF);
        
        // 从中断中清除事件位
        xEventGroupClearBitsFromISR(
            system_events,
            USER_INPUT_RECEIVED
        );
    }
}
```

### 获取事件位状态

```c
// 获取当前事件位状态
void Check_Event_Status(void) {
    // 获取当前事件位
    EventBits_t current_bits = xEventGroupGetBits(system_events);
    
    printf("Current event bits: 0x%02X\n", current_bits);
    
    // 检查特定事件是否设置
    if(current_bits & SENSOR_DATA_READY) {
        printf("  - Sensor data is ready\n");
    }
    
    if(current_bits & NETWORK_CONNECTED) {
        printf("  - Network is connected\n");
    }
    
    if(current_bits & STORAGE_AVAILABLE) {
        printf("  - Storage is available\n");
    }
    
    // 检查多个事件是否都设置
    if((current_bits & ALL_INIT_EVENTS) == ALL_INIT_EVENTS) {
        printf("  - All initialization events are set\n");
    }
}

// 从中断中获取事件位状态
void TIM2_IRQHandler(void) {
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 从中断中获取事件位
        EventBits_t bits = xEventGroupGetBitsFromISR(system_events);
        
        // 根据事件位状态执行操作
        if(bits & SENSOR_DATA_READY) {
            // 处理传感器数据
        }
    }
}
```


## 实际应用场景

### 场景1：系统启动同步

等待多个子系统初始化完成后再启动主应用：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义初始化事件
#define INIT_HARDWARE       (1 << 0)
#define INIT_NETWORK        (1 << 1)
#define INIT_FILESYSTEM     (1 << 2)
#define INIT_SENSORS        (1 << 3)
#define INIT_DISPLAY        (1 << 4)

#define ALL_INIT_COMPLETE   (INIT_HARDWARE | INIT_NETWORK | \
                             INIT_FILESYSTEM | INIT_SENSORS | \
                             INIT_DISPLAY)

// 事件标志组句柄
EventGroupHandle_t startup_events;

// 硬件初始化任务
void Hardware_Init_Task(void *param) {
    printf("[Hardware] Initializing...\n");
    
    // 模拟硬件初始化
    HAL_GPIO_Init();
    HAL_UART_Init();
    vTaskDelay(pdMS_TO_TICKS(300));
    
    // 设置初始化完成事件
    xEventGroupSetBits(startup_events, INIT_HARDWARE);
    printf("[Hardware] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 网络初始化任务
void Network_Init_Task(void *param) {
    printf("[Network] Initializing...\n");
    
    // 模拟网络初始化
    vTaskDelay(pdMS_TO_TICKS(800));
    
    xEventGroupSetBits(startup_events, INIT_NETWORK);
    printf("[Network] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 文件系统初始化任务
void Filesystem_Init_Task(void *param) {
    printf("[Filesystem] Initializing...\n");
    
    // 模拟文件系统初始化
    vTaskDelay(pdMS_TO_TICKS(500));
    
    xEventGroupSetBits(startup_events, INIT_FILESYSTEM);
    printf("[Filesystem] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 传感器初始化任务
void Sensors_Init_Task(void *param) {
    printf("[Sensors] Initializing...\n");
    
    // 模拟传感器初始化
    vTaskDelay(pdMS_TO_TICKS(400));
    
    xEventGroupSetBits(startup_events, INIT_SENSORS);
    printf("[Sensors] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 显示初始化任务
void Display_Init_Task(void *param) {
    printf("[Display] Initializing...\n");
    
    // 模拟显示初始化
    vTaskDelay(pdMS_TO_TICKS(600));
    
    xEventGroupSetBits(startup_events, INIT_DISPLAY);
    printf("[Display] Initialization complete\n");
    
    vTaskDelete(NULL);
}

// 主应用任务
void Main_Application_Task(void *param) {
    printf("[MainApp] Waiting for all subsystems to initialize...\n");
    
    // 等待所有初始化完成（AND模式）
    EventBits_t bits = xEventGroupWaitBits(
        startup_events,
        ALL_INIT_COMPLETE,  // 等待所有初始化事件
        pdFALSE,            // 不清除事件位（其他任务可能也需要检查）
        pdTRUE,             // AND模式：所有事件都必须完成
        portMAX_DELAY       // 永久等待
    );
    
    printf("[MainApp] All subsystems initialized! (bits=0x%02X)\n", bits);
    printf("[MainApp] Starting main application...\n");
    
    while(1) {
        // 主应用逻辑
        printf("[MainApp] Running...\n");
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}

// 系统启动函数
void System_Startup(void) {
    // 创建事件标志组
    startup_events = xEventGroupCreate();
    
    if(startup_events != NULL) {
        // 创建初始化任务
        xTaskCreate(Hardware_Init_Task, "HW_Init", 256, NULL, 3, NULL);
        xTaskCreate(Network_Init_Task, "Net_Init", 256, NULL, 3, NULL);
        xTaskCreate(Filesystem_Init_Task, "FS_Init", 256, NULL, 3, NULL);
        xTaskCreate(Sensors_Init_Task, "Sensor_Init", 256, NULL, 3, NULL);
        xTaskCreate(Display_Init_Task, "Display_Init", 256, NULL, 3, NULL);
        
        // 创建主应用任务（优先级较低，等待初始化完成）
        xTaskCreate(Main_Application_Task, "MainApp", 512, NULL, 2, NULL);
    }
}
```

**运行结果**：
```
[MainApp] Waiting for all subsystems to initialize...
[Hardware] Initializing...
[Network] Initializing...
[Filesystem] Initializing...
[Sensors] Initializing...
[Display] Initializing...
[Hardware] Initialization complete
[Sensors] Initialization complete
[Filesystem] Initialization complete
[Display] Initialization complete
[Network] Initialization complete
[MainApp] All subsystems initialized! (bits=0x1F)
[MainApp] Starting main application...
[MainApp] Running...
```


### 场景2：多传感器数据采集同步

等待所有传感器数据就绪后进行数据处理：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义传感器事件
#define TEMP_SENSOR_READY       (1 << 0)
#define HUMIDITY_SENSOR_READY   (1 << 1)
#define PRESSURE_SENSOR_READY   (1 << 2)
#define LIGHT_SENSOR_READY      (1 << 3)

#define ALL_SENSORS_READY       (TEMP_SENSOR_READY | \
                                 HUMIDITY_SENSOR_READY | \
                                 PRESSURE_SENSOR_READY | \
                                 LIGHT_SENSOR_READY)

// 事件标志组
EventGroupHandle_t sensor_events;

// 传感器数据结构
typedef struct {
    float temperature;
    float humidity;
    float pressure;
    float light;
    uint32_t timestamp;
} SensorData_t;

SensorData_t sensor_data;

// 温度传感器任务
void Temperature_Sensor_Task(void *param) {
    while(1) {
        // 读取温度传感器（模拟）
        vTaskDelay(pdMS_TO_TICKS(950));
        sensor_data.temperature = 25.5f + (rand() % 100) / 10.0f;
        
        printf("[Temp] Data ready: %.1f°C\n", sensor_data.temperature);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, TEMP_SENSOR_READY);
    }
}

// 湿度传感器任务
void Humidity_Sensor_Task(void *param) {
    while(1) {
        // 读取湿度传感器（模拟）
        vTaskDelay(pdMS_TO_TICKS(1050));
        sensor_data.humidity = 60.0f + (rand() % 200) / 10.0f;
        
        printf("[Humidity] Data ready: %.1f%%\n", sensor_data.humidity);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, HUMIDITY_SENSOR_READY);
    }
}

// 气压传感器任务
void Pressure_Sensor_Task(void *param) {
    while(1) {
        // 读取气压传感器（模拟）
        vTaskDelay(pdMS_TO_TICKS(900));
        sensor_data.pressure = 1013.25f + (rand() % 100) / 10.0f;
        
        printf("[Pressure] Data ready: %.2f hPa\n", sensor_data.pressure);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, PRESSURE_SENSOR_READY);
    }
}

// 光照传感器任务
void Light_Sensor_Task(void *param) {
    while(1) {
        // 读取光照传感器（模拟）
        vTaskDelay(pdMS_TO_TICKS(1100));
        sensor_data.light = 500.0f + (rand() % 1000);
        
        printf("[Light] Data ready: %.0f lux\n", sensor_data.light);
        
        // 设置事件位
        xEventGroupSetBits(sensor_events, LIGHT_SENSOR_READY);
    }
}

// 数据处理任务
void Data_Process_Task(void *param) {
    uint32_t sample_count = 0;
    
    while(1) {
        printf("\n[Process] Waiting for all sensor data (sample #%lu)...\n", 
               ++sample_count);
        
        // 等待所有传感器数据就绪
        EventBits_t bits = xEventGroupWaitBits(
            sensor_events,
            ALL_SENSORS_READY,  // 等待所有传感器
            pdTRUE,             // 等待成功后清除事件位
            pdTRUE,             // AND模式：所有传感器都必须就绪
            portMAX_DELAY       // 永久等待
        );
        
        // 所有数据就绪，记录时间戳
        sensor_data.timestamp = xTaskGetTickCount();
        
        // 处理数据
        printf("[Process] All data ready! Processing...\n");
        printf("[Process] Temperature: %.1f°C\n", sensor_data.temperature);
        printf("[Process] Humidity: %.1f%%\n", sensor_data.humidity);
        printf("[Process] Pressure: %.2f hPa\n", sensor_data.pressure);
        printf("[Process] Light: %.0f lux\n", sensor_data.light);
        printf("[Process] Timestamp: %lu ms\n", sensor_data.timestamp);
        
        // 计算舒适度指数（示例）
        float comfort_index = (sensor_data.temperature * 0.4f + 
                               sensor_data.humidity * 0.3f + 
                               sensor_data.light / 10.0f * 0.3f);
        printf("[Process] Comfort Index: %.1f\n", comfort_index);
        
        // 数据存储或上传
        // SaveToFlash(&sensor_data);
        // UploadToCloud(&sensor_data);
        
        printf("[Process] Processing complete\n\n");
    }
}

// 初始化传感器系统
void Sensor_System_Init(void) {
    // 创建事件标志组
    sensor_events = xEventGroupCreate();
    
    if(sensor_events != NULL) {
        // 创建传感器任务
        xTaskCreate(Temperature_Sensor_Task, "Temp", 256, NULL, 2, NULL);
        xTaskCreate(Humidity_Sensor_Task, "Humidity", 256, NULL, 2, NULL);
        xTaskCreate(Pressure_Sensor_Task, "Pressure", 256, NULL, 2, NULL);
        xTaskCreate(Light_Sensor_Task, "Light", 256, NULL, 2, NULL);
        
        // 创建数据处理任务
        xTaskCreate(Data_Process_Task, "Process", 512, NULL, 3, NULL);
        
        printf("Sensor system initialized\n");
    }
}
```


### 场景3：多输入源事件处理（OR模式）

等待任意一个输入事件发生并处理：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义输入事件
#define BUTTON_PRESSED      (1 << 0)
#define UART_DATA_RX        (1 << 1)
#define TIMER_EXPIRED       (1 << 2)
#define NETWORK_DATA_RX     (1 << 3)
#define USB_CONNECTED       (1 << 4)

#define ANY_INPUT_EVENT     (BUTTON_PRESSED | UART_DATA_RX | \
                             TIMER_EXPIRED | NETWORK_DATA_RX | \
                             USB_CONNECTED)

// 事件标志组
EventGroupHandle_t input_events;

// 按键任务
void Button_Task(void *param) {
    while(1) {
        // 模拟按键检测
        vTaskDelay(pdMS_TO_TICKS(3000));
        
        printf("[Button] Button pressed!\n");
        xEventGroupSetBits(input_events, BUTTON_PRESSED);
    }
}

// UART接收任务
void UART_Task(void *param) {
    while(1) {
        // 模拟UART数据接收
        vTaskDelay(pdMS_TO_TICKS(5000));
        
        printf("[UART] Data received!\n");
        xEventGroupSetBits(input_events, UART_DATA_RX);
    }
}

// 定时器任务
void Timer_Task(void *param) {
    while(1) {
        // 模拟定时器超时
        vTaskDelay(pdMS_TO_TICKS(7000));
        
        printf("[Timer] Timer expired!\n");
        xEventGroupSetBits(input_events, TIMER_EXPIRED);
    }
}

// 网络接收任务
void Network_Task(void *param) {
    while(1) {
        // 模拟网络数据接收
        vTaskDelay(pdMS_TO_TICKS(4000));
        
        printf("[Network] Data received!\n");
        xEventGroupSetBits(input_events, NETWORK_DATA_RX);
    }
}

// USB检测任务
void USB_Task(void *param) {
    while(1) {
        // 模拟USB连接检测
        vTaskDelay(pdMS_TO_TICKS(10000));
        
        printf("[USB] USB connected!\n");
        xEventGroupSetBits(input_events, USB_CONNECTED);
    }
}

// 事件处理任务
void Event_Handler_Task(void *param) {
    uint32_t event_count = 0;
    
    while(1) {
        printf("\n[Handler] Waiting for any input event (#%lu)...\n", 
               ++event_count);
        
        // 等待任意一个事件发生（OR模式）
        EventBits_t bits = xEventGroupWaitBits(
            input_events,
            ANY_INPUT_EVENT,    // 等待任意输入事件
            pdTRUE,             // 等待成功后清除事件位
            pdFALSE,            // OR模式：任一事件发生即可
            portMAX_DELAY       // 永久等待
        );
        
        printf("[Handler] Event occurred! bits=0x%02X\n", bits);
        
        // 检查并处理具体的事件
        if(bits & BUTTON_PRESSED) {
            printf("[Handler] Handling button press event\n");
            // 处理按键事件
            HandleButtonPress();
        }
        
        if(bits & UART_DATA_RX) {
            printf("[Handler] Handling UART data event\n");
            // 处理UART数据
            HandleUARTData();
        }
        
        if(bits & TIMER_EXPIRED) {
            printf("[Handler] Handling timer event\n");
            // 处理定时器事件
            HandleTimerExpired();
        }
        
        if(bits & NETWORK_DATA_RX) {
            printf("[Handler] Handling network data event\n");
            // 处理网络数据
            HandleNetworkData();
        }
        
        if(bits & USB_CONNECTED) {
            printf("[Handler] Handling USB connection event\n");
            // 处理USB连接
            HandleUSBConnection();
        }
        
        printf("[Handler] Event handled\n\n");
    }
}

// 事件处理函数（示例）
void HandleButtonPress(void) {
    printf("  -> Button action executed\n");
}

void HandleUARTData(void) {
    printf("  -> UART data processed\n");
}

void HandleTimerExpired(void) {
    printf("  -> Timer action executed\n");
}

void HandleNetworkData(void) {
    printf("  -> Network data processed\n");
}

void HandleUSBConnection(void) {
    printf("  -> USB device enumerated\n");
}

// 初始化输入系统
void Input_System_Init(void) {
    // 创建事件标志组
    input_events = xEventGroupCreate();
    
    if(input_events != NULL) {
        // 创建输入任务
        xTaskCreate(Button_Task, "Button", 256, NULL, 2, NULL);
        xTaskCreate(UART_Task, "UART", 256, NULL, 2, NULL);
        xTaskCreate(Timer_Task, "Timer", 256, NULL, 2, NULL);
        xTaskCreate(Network_Task, "Network", 256, NULL, 2, NULL);
        xTaskCreate(USB_Task, "USB", 256, NULL, 2, NULL);
        
        // 创建事件处理任务
        xTaskCreate(Event_Handler_Task, "Handler", 512, NULL, 3, NULL);
        
        printf("Input system initialized\n");
    }
}
```


### 场景4：任务同步点

实现多个任务在特定点同步：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"

// 定义同步事件
#define TASK1_READY     (1 << 0)
#define TASK2_READY     (1 << 1)
#define TASK3_READY     (1 << 2)

#define ALL_TASKS_READY (TASK1_READY | TASK2_READY | TASK3_READY)

// 事件标志组
EventGroupHandle_t sync_events;

// 任务1
void Sync_Task1(void *param) {
    uint32_t cycle = 0;
    
    while(1) {
        cycle++;
        printf("[Task1] Cycle %lu: Working...\n", cycle);
        
        // 执行任务1的工作
        vTaskDelay(pdMS_TO_TICKS(100 + rand() % 200));
        
        printf("[Task1] Cycle %lu: Work done, waiting at sync point\n", cycle);
        
        // 设置自己的就绪标志
        xEventGroupSetBits(sync_events, TASK1_READY);
        
        // 等待所有任务到达同步点
        xEventGroupWaitBits(
            sync_events,
            ALL_TASKS_READY,
            pdTRUE,         // 清除所有标志，准备下一轮
            pdTRUE,         // AND模式：等待所有任务
            portMAX_DELAY
        );
        
        printf("[Task1] Cycle %lu: All tasks synchronized, continuing\n", cycle);
    }
}

// 任务2
void Sync_Task2(void *param) {
    uint32_t cycle = 0;
    
    while(1) {
        cycle++;
        printf("[Task2] Cycle %lu: Working...\n", cycle);
        
        // 执行任务2的工作
        vTaskDelay(pdMS_TO_TICKS(150 + rand() % 200));
        
        printf("[Task2] Cycle %lu: Work done, waiting at sync point\n", cycle);
        
        // 设置自己的就绪标志
        xEventGroupSetBits(sync_events, TASK2_READY);
        
        // 等待所有任务到达同步点
        xEventGroupWaitBits(
            sync_events,
            ALL_TASKS_READY,
            pdTRUE,
            pdTRUE,
            portMAX_DELAY
        );
        
        printf("[Task2] Cycle %lu: All tasks synchronized, continuing\n", cycle);
    }
}

// 任务3
void Sync_Task3(void *param) {
    uint32_t cycle = 0;
    
    while(1) {
        cycle++;
        printf("[Task3] Cycle %lu: Working...\n", cycle);
        
        // 执行任务3的工作
        vTaskDelay(pdMS_TO_TICKS(200 + rand() % 200));
        
        printf("[Task3] Cycle %lu: Work done, waiting at sync point\n", cycle);
        
        // 设置自己的就绪标志
        xEventGroupSetBits(sync_events, TASK3_READY);
        
        // 等待所有任务到达同步点
        xEventGroupWaitBits(
            sync_events,
            ALL_TASKS_READY,
            pdTRUE,
            pdTRUE,
            portMAX_DELAY
        );
        
        printf("[Task3] Cycle %lu: All tasks synchronized, continuing\n", cycle);
    }
}

// 初始化同步系统
void Sync_System_Init(void) {
    // 创建事件标志组
    sync_events = xEventGroupCreate();
    
    if(sync_events != NULL) {
        // 创建同步任务
        xTaskCreate(Sync_Task1, "SyncTask1", 256, NULL, 2, NULL);
        xTaskCreate(Sync_Task2, "SyncTask2", 256, NULL, 2, NULL);
        xTaskCreate(Sync_Task3, "SyncTask3", 256, NULL, 2, NULL);
        
        printf("Sync system initialized\n");
    }
}
```


## 高级技巧和最佳实践

### 技巧1：使用事件位组合

```c
// 定义基本事件
#define EVENT_SENSOR_1      (1 << 0)
#define EVENT_SENSOR_2      (1 << 1)
#define EVENT_SENSOR_3      (1 << 2)
#define EVENT_NETWORK       (1 << 3)
#define EVENT_STORAGE       (1 << 4)

// 定义组合事件
#define ALL_SENSORS         (EVENT_SENSOR_1 | EVENT_SENSOR_2 | EVENT_SENSOR_3)
#define SYSTEM_READY        (ALL_SENSORS | EVENT_NETWORK | EVENT_STORAGE)
#define MINIMAL_READY       (EVENT_SENSOR_1 | EVENT_NETWORK)

// 使用组合事件
void Wait_For_System_Ready(void) {
    // 等待完整系统就绪
    xEventGroupWaitBits(events, SYSTEM_READY, pdFALSE, pdTRUE, portMAX_DELAY);
}

void Wait_For_Minimal_Ready(void) {
    // 等待最小系统就绪
    xEventGroupWaitBits(events, MINIMAL_READY, pdFALSE, pdTRUE, portMAX_DELAY);
}
```

### 技巧2：事件位状态机

```c
// 定义状态事件
#define STATE_IDLE          (1 << 0)
#define STATE_RUNNING       (1 << 1)
#define STATE_PAUSED        (1 << 2)
#define STATE_ERROR         (1 << 3)

// 状态转换函数
void Change_State(EventGroupHandle_t events, EventBits_t new_state) {
    // 清除所有状态位
    xEventGroupClearBits(events, 
                         STATE_IDLE | STATE_RUNNING | 
                         STATE_PAUSED | STATE_ERROR);
    
    // 设置新状态
    xEventGroupSetBits(events, new_state);
    
    printf("State changed to: 0x%02X\n", new_state);
}

// 获取当前状态
EventBits_t Get_Current_State(EventGroupHandle_t events) {
    EventBits_t bits = xEventGroupGetBits(events);
    return bits & (STATE_IDLE | STATE_RUNNING | STATE_PAUSED | STATE_ERROR);
}

// 状态检查
bool Is_In_State(EventGroupHandle_t events, EventBits_t state) {
    EventBits_t current = xEventGroupGetBits(events);
    return (current & state) != 0;
}
```

### 技巧3：超时重试机制

```c
// 带重试的事件等待
bool Wait_Event_With_Retry(EventGroupHandle_t events, 
                           EventBits_t bits_to_wait,
                           uint32_t timeout_ms,
                           uint32_t max_retries) {
    uint32_t retry_count = 0;
    
    while(retry_count < max_retries) {
        printf("Waiting for events (attempt %lu/%lu)...\n", 
               retry_count + 1, max_retries);
        
        EventBits_t result = xEventGroupWaitBits(
            events,
            bits_to_wait,
            pdTRUE,
            pdTRUE,
            pdMS_TO_TICKS(timeout_ms)
        );
        
        // 检查是否成功
        if((result & bits_to_wait) == bits_to_wait) {
            printf("Events occurred successfully\n");
            return true;
        }
        
        // 超时，重试
        retry_count++;
        printf("Timeout, retrying...\n");
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    printf("Failed after %lu retries\n", max_retries);
    return false;
}
```

### 技巧4：事件位计数器

```c
// 使用多个位实现计数器
#define COUNTER_BIT_0       (1 << 0)
#define COUNTER_BIT_1       (1 << 1)
#define COUNTER_BIT_2       (1 << 2)
#define COUNTER_MASK        (COUNTER_BIT_0 | COUNTER_BIT_1 | COUNTER_BIT_2)

// 增加计数器
void Increment_Counter(EventGroupHandle_t events) {
    EventBits_t current = xEventGroupGetBits(events);
    uint32_t counter = (current & COUNTER_MASK);
    
    counter = (counter + 1) & 0x07;  // 0-7循环
    
    // 清除旧值，设置新值
    xEventGroupClearBits(events, COUNTER_MASK);
    xEventGroupSetBits(events, counter);
    
    printf("Counter: %lu\n", counter);
}

// 读取计数器
uint32_t Read_Counter(EventGroupHandle_t events) {
    EventBits_t bits = xEventGroupGetBits(events);
    return (bits & COUNTER_MASK);
}
```

### 技巧5：事件位优先级

```c
// 定义优先级事件
#define EVENT_CRITICAL      (1 << 0)    // 最高优先级
#define EVENT_HIGH          (1 << 1)
#define EVENT_NORMAL        (1 << 2)
#define EVENT_LOW           (1 << 3)    // 最低优先级

// 按优先级处理事件
void Process_Events_By_Priority(EventGroupHandle_t events) {
    EventBits_t bits = xEventGroupGetBits(events);
    
    // 按优先级顺序检查和处理
    if(bits & EVENT_CRITICAL) {
        printf("Processing CRITICAL event\n");
        xEventGroupClearBits(events, EVENT_CRITICAL);
        Handle_Critical_Event();
        return;
    }
    
    if(bits & EVENT_HIGH) {
        printf("Processing HIGH priority event\n");
        xEventGroupClearBits(events, EVENT_HIGH);
        Handle_High_Event();
        return;
    }
    
    if(bits & EVENT_NORMAL) {
        printf("Processing NORMAL priority event\n");
        xEventGroupClearBits(events, EVENT_NORMAL);
        Handle_Normal_Event();
        return;
    }
    
    if(bits & EVENT_LOW) {
        printf("Processing LOW priority event\n");
        xEventGroupClearBits(events, EVENT_LOW);
        Handle_Low_Event();
        return;
    }
}
```


## 常见问题和解决方案

### 问题1：事件位不够用

**现象**：
```c
// 需要超过24个事件
#define EVENT_25    (1 << 24)  // ❌ 超出范围
```

**解决方案**：

**方案1：使用多个事件标志组**
```c
// 创建多个事件标志组
EventGroupHandle_t events_group1;  // 事件0-23
EventGroupHandle_t events_group2;  // 事件24-47

// 初始化
events_group1 = xEventGroupCreate();
events_group2 = xEventGroupCreate();

// 使用
xEventGroupSetBits(events_group1, EVENT_0);
xEventGroupSetBits(events_group2, EVENT_25);
```

**方案2：重新设计事件结构**
```c
// 使用组合事件减少位数
#define SENSOR_TYPE_MASK    (0x07)  // 位0-2：传感器类型
#define SENSOR_STATUS_MASK  (0x18)  // 位3-4：传感器状态
#define NETWORK_STATUS_MASK (0xE0)  // 位5-7：网络状态

// 设置组合事件
void Set_Sensor_Event(uint8_t type, uint8_t status) {
    EventBits_t bits = (type & 0x07) | ((status & 0x03) << 3);
    xEventGroupSetBits(events, bits);
}
```

**方案3：使用队列传递复杂事件**
```c
// 对于复杂事件，使用队列
typedef struct {
    uint32_t event_id;
    uint32_t event_data;
    uint32_t timestamp;
} ComplexEvent_t;

QueueHandle_t event_queue;

// 发送复杂事件
void Send_Complex_Event(uint32_t id, uint32_t data) {
    ComplexEvent_t event = {
        .event_id = id,
        .event_data = data,
        .timestamp = xTaskGetTickCount()
    };
    xQueueSend(event_queue, &event, 0);
}
```


### 问题2：事件位被意外清除

**现象**：
```c
// 任务A设置事件
xEventGroupSetBits(events, EVENT_A);

// 任务B等待并清除
xEventGroupWaitBits(events, EVENT_A, pdTRUE, pdTRUE, portMAX_DELAY);

// 任务C再次检查时，事件已被清除
EventBits_t bits = xEventGroupGetBits(events);
if(bits & EVENT_A) {  // ❌ 条件不成立
    // 不会执行
}
```

**解决方案**：

**方案1：不自动清除事件位**
```c
// 等待但不清除
xEventGroupWaitBits(events, EVENT_A, pdFALSE, pdTRUE, portMAX_DELAY);

// 所有任务处理完后，手动清除
xEventGroupClearBits(events, EVENT_A);
```

**方案2：使用引用计数**
```c
// 事件引用计数
typedef struct {
    EventGroupHandle_t events;
    uint8_t ref_count[24];  // 每个位的引用计数
} EventGroupWithRef_t;

// 等待事件（增加引用）
void Wait_Event_With_Ref(EventGroupWithRef_t *eg, EventBits_t bits) {
    xEventGroupWaitBits(eg->events, bits, pdFALSE, pdTRUE, portMAX_DELAY);
    
    // 增加引用计数
    for(int i = 0; i < 24; i++) {
        if(bits & (1 << i)) {
            eg->ref_count[i]++;
        }
    }
}

// 释放事件（减少引用）
void Release_Event_With_Ref(EventGroupWithRef_t *eg, EventBits_t bits) {
    for(int i = 0; i < 24; i++) {
        if(bits & (1 << i)) {
            if(eg->ref_count[i] > 0) {
                eg->ref_count[i]--;
                
                // 引用计数为0时清除事件位
                if(eg->ref_count[i] == 0) {
                    xEventGroupClearBits(eg->events, (1 << i));
                }
            }
        }
    }
}
```


### 问题3：等待超时但事件已发生

**现象**：
```c
// 任务A在等待前，事件已经被设置
xEventGroupSetBits(events, EVENT_A);  // 事件已设置

// 任务B稍后才开始等待
vTaskDelay(pdMS_TO_TICKS(100));
EventBits_t bits = xEventGroupWaitBits(
    events, EVENT_A, pdTRUE, pdTRUE, 
    pdMS_TO_TICKS(50)  // 50ms超时
);
// 立即返回，因为事件已经设置
```

**这不是问题，而是特性**：
- 事件标志组会保持事件位状态
- 即使事件在等待前发生，等待也会立即成功
- 这与信号量不同（信号量会被消耗）

**如果需要"新鲜"事件**：
```c
// 清除旧事件，只等待新事件
xEventGroupClearBits(events, EVENT_A);

// 现在等待新的事件
EventBits_t bits = xEventGroupWaitBits(
    events, EVENT_A, pdTRUE, pdTRUE, portMAX_DELAY
);
```


### 问题4：从中断设置事件失败

**现象**：
```c
void EXTI_IRQHandler(void) {
    // ❌ 错误：在中断中使用任务版本API
    xEventGroupSetBits(events, EVENT_A);  // 可能失败
}
```

**解决方案**：
```c
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // ✅ 正确：使用FromISR版本
    xEventGroupSetBitsFromISR(
        events,
        EVENT_A,
        &xHigherPriorityTaskWoken
    );
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

**注意事项**：
- 必须使用FromISR版本的API
- 必须传递xHigherPriorityTaskWoken参数
- 必须在中断结束时调用portYIELD_FROM_ISR


### 问题5：多任务竞争条件

**现象**：
```c
// 任务A
EventBits_t bits = xEventGroupGetBits(events);
if(bits & EVENT_A) {
    // 在这里，任务B可能清除了EVENT_A
    xEventGroupClearBits(events, EVENT_A);  // 可能清除了不存在的位
}

// 任务B
xEventGroupClearBits(events, EVENT_A);  // 同时清除
```

**解决方案**：

**方案1：使用原子操作**
```c
// 使用WaitBits原子地检查和清除
EventBits_t bits = xEventGroupWaitBits(
    events,
    EVENT_A,
    pdTRUE,     // 原子地清除
    pdTRUE,
    0           // 不等待，立即返回
);

if(bits & EVENT_A) {
    // 事件已被原子地清除
    ProcessEvent();
}
```

**方案2：使用互斥量保护**
```c
SemaphoreHandle_t event_mutex;

// 任务A
xSemaphoreTake(event_mutex, portMAX_DELAY);
EventBits_t bits = xEventGroupGetBits(events);
if(bits & EVENT_A) {
    xEventGroupClearBits(events, EVENT_A);
    ProcessEvent();
}
xSemaphoreGive(event_mutex);
```


## 性能优化和调试

### 性能优化建议

**1. 减少不必要的等待**：
```c
// ❌ 不好：频繁轮询
while(1) {
    EventBits_t bits = xEventGroupWaitBits(events, EVENT_A, 
                                           pdFALSE, pdTRUE, 
                                           pdMS_TO_TICKS(10));
    if(bits & EVENT_A) {
        ProcessEvent();
    }
}

// ✅ 更好：阻塞等待
while(1) {
    xEventGroupWaitBits(events, EVENT_A, pdTRUE, pdTRUE, portMAX_DELAY);
    ProcessEvent();
}
```

**2. 合理使用清除标志**：
```c
// 如果多个任务需要同一事件，不要自动清除
xEventGroupWaitBits(events, EVENT_A, pdFALSE, pdTRUE, portMAX_DELAY);

// 最后一个任务手动清除
xEventGroupClearBits(events, EVENT_A);
```

**3. 避免过度使用事件组**：
```c
// ❌ 不好：简单通知使用事件组
xEventGroupSetBits(events, SIMPLE_EVENT);

// ✅ 更好：使用任务通知（更快，更省内存）
xTaskNotifyGive(task_handle);
```

### 调试技巧

**1. 事件位状态监控**：
```c
// 监控任务
void Event_Monitor_Task(void *param) {
    while(1) {
        EventBits_t bits = xEventGroupGetBits(system_events);
        
        printf("\n=== Event Status ===\n");
        printf("Current bits: 0x%06X\n", bits);
        
        // 显示每个事件的状态
        for(int i = 0; i < 24; i++) {
            if(bits & (1 << i)) {
                printf("  Bit %d: SET\n", i);
            }
        }
        printf("===================\n\n");
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
```

**2. 事件历史记录**：
```c
// 事件历史记录
#define EVENT_HISTORY_SIZE 100

typedef struct {
    EventBits_t bits;
    uint32_t timestamp;
    const char *source;
} EventHistory_t;

EventHistory_t event_history[EVENT_HISTORY_SIZE];
uint32_t history_index = 0;

// 记录事件
void Log_Event(EventBits_t bits, const char *source) {
    event_history[history_index].bits = bits;
    event_history[history_index].timestamp = xTaskGetTickCount();
    event_history[history_index].source = source;
    
    history_index = (history_index + 1) % EVENT_HISTORY_SIZE;
}

// 打印历史
void Print_Event_History(void) {
    printf("\n=== Event History ===\n");
    for(int i = 0; i < EVENT_HISTORY_SIZE; i++) {
        uint32_t idx = (history_index + i) % EVENT_HISTORY_SIZE;
        if(event_history[idx].timestamp > 0) {
            printf("[%lu] %s: 0x%06X\n",
                   event_history[idx].timestamp,
                   event_history[idx].source,
                   event_history[idx].bits);
        }
    }
    printf("====================\n\n");
}
```

**3. 断言检查**：
```c
// 使用断言检查事件组状态
void Check_Event_Group_State(EventGroupHandle_t events, 
                             EventBits_t expected_bits) {
    EventBits_t current_bits = xEventGroupGetBits(events);
    
    configASSERT((current_bits & expected_bits) == expected_bits);
}

// 使用示例
Check_Event_Group_State(system_events, INIT_HARDWARE | INIT_NETWORK);
```


## 完整示例项目

### 项目：智能家居控制系统

实现一个使用事件标志组的智能家居控制系统：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "event_groups.h"
#include "queue.h"

// 系统事件定义
#define EVENT_MOTION_DETECTED       (1 << 0)
#define EVENT_DOOR_OPENED           (1 << 1)
#define EVENT_WINDOW_OPENED         (1 << 2)
#define EVENT_TEMP_HIGH             (1 << 3)
#define EVENT_TEMP_LOW              (1 << 4)
#define EVENT_LIGHT_LOW             (1 << 5)
#define EVENT_SMOKE_DETECTED        (1 << 6)
#define EVENT_WATER_LEAK            (1 << 7)
#define EVENT_USER_HOME             (1 << 8)
#define EVENT_USER_AWAY             (1 << 9)
#define EVENT_NIGHT_MODE            (1 << 10)
#define EVENT_DAY_MODE              (1 << 11)

// 报警事件
#define ALARM_EVENTS                (EVENT_SMOKE_DETECTED | EVENT_WATER_LEAK)

// 安防事件
#define SECURITY_EVENTS             (EVENT_MOTION_DETECTED | \
                                     EVENT_DOOR_OPENED | \
                                     EVENT_WINDOW_OPENED)

// 舒适度事件
#define COMFORT_EVENTS              (EVENT_TEMP_HIGH | EVENT_TEMP_LOW | \
                                     EVENT_LIGHT_LOW)

// 事件标志组
EventGroupHandle_t home_events;

// 系统状态
typedef enum {
    MODE_HOME,
    MODE_AWAY,
    MODE_NIGHT,
    MODE_VACATION
} SystemMode_t;

SystemMode_t current_mode = MODE_HOME;

// 传感器监控任务
void Sensor_Monitor_Task(void *param) {
    while(1) {
        // 模拟传感器读取
        float temperature = 22.0f + (rand() % 100) / 10.0f;
        float light_level = 300.0f + (rand() % 500);
        bool motion = (rand() % 100) < 10;  // 10%概率检测到运动
        bool door_open = (rand() % 100) < 5;  // 5%概率门打开
        
        // 温度检查
        if(temperature > 28.0f) {
            xEventGroupSetBits(home_events, EVENT_TEMP_HIGH);
            printf("[Sensor] High temperature: %.1f°C\n", temperature);
        } else if(temperature < 18.0f) {
            xEventGroupSetBits(home_events, EVENT_TEMP_LOW);
            printf("[Sensor] Low temperature: %.1f°C\n", temperature);
        }
        
        // 光照检查
        if(light_level < 200.0f) {
            xEventGroupSetBits(home_events, EVENT_LIGHT_LOW);
            printf("[Sensor] Low light: %.0f lux\n", light_level);
        }
        
        // 运动检测
        if(motion) {
            xEventGroupSetBits(home_events, EVENT_MOTION_DETECTED);
            printf("[Sensor] Motion detected\n");
        }
        
        // 门状态
        if(door_open) {
            xEventGroupSetBits(home_events, EVENT_DOOR_OPENED);
            printf("[Sensor] Door opened\n");
        }
        
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

// 安防监控任务
void Security_Task(void *param) {
    while(1) {
        // 等待安防事件（OR模式）
        EventBits_t bits = xEventGroupWaitBits(
            home_events,
            SECURITY_EVENTS,
            pdTRUE,         // 清除事件
            pdFALSE,        // OR模式：任一事件
            portMAX_DELAY
        );
        
        printf("\n[Security] Security event detected! bits=0x%03X\n", bits);
        
        // 根据模式处理
        if(current_mode == MODE_AWAY || current_mode == MODE_VACATION) {
            // 离家模式：触发报警
            if(bits & EVENT_MOTION_DETECTED) {
                printf("[Security] ALARM! Motion detected while away\n");
                TriggerAlarm();
                SendNotification("Motion detected at home");
            }
            
            if(bits & EVENT_DOOR_OPENED) {
                printf("[Security] ALARM! Door opened while away\n");
                TriggerAlarm();
                SendNotification("Door opened at home");
            }
            
            if(bits & EVENT_WINDOW_OPENED) {
                printf("[Security] ALARM! Window opened while away\n");
                TriggerAlarm();
                SendNotification("Window opened at home");
            }
        } else {
            // 在家模式：只记录
            printf("[Security] Event logged (home mode)\n");
        }
    }
}

// 舒适度控制任务
void Comfort_Task(void *param) {
    while(1) {
        // 等待舒适度事件（OR模式）
        EventBits_t bits = xEventGroupWaitBits(
            home_events,
            COMFORT_EVENTS,
            pdTRUE,
            pdFALSE,
            portMAX_DELAY
        );
        
        printf("\n[Comfort] Comfort event detected! bits=0x%03X\n", bits);
        
        // 温度控制
        if(bits & EVENT_TEMP_HIGH) {
            printf("[Comfort] Turning on air conditioning\n");
            TurnOnAC();
        }
        
        if(bits & EVENT_TEMP_LOW) {
            printf("[Comfort] Turning on heating\n");
            TurnOnHeating();
        }
        
        // 照明控制
        if(bits & EVENT_LIGHT_LOW) {
            // 根据模式决定是否开灯
            EventBits_t mode_bits = xEventGroupGetBits(home_events);
            
            if(mode_bits & EVENT_USER_HOME) {
                printf("[Comfort] Turning on lights\n");
                TurnOnLights();
            } else {
                printf("[Comfort] Low light detected, but user is away\n");
            }
        }
    }
}

// 紧急报警任务
void Emergency_Task(void *param) {
    while(1) {
        // 等待紧急事件（OR模式，高优先级）
        EventBits_t bits = xEventGroupWaitBits(
            home_events,
            ALARM_EVENTS,
            pdTRUE,
            pdFALSE,
            portMAX_DELAY
        );
        
        printf("\n[EMERGENCY] Critical event! bits=0x%03X\n", bits);
        
        // 烟雾报警
        if(bits & EVENT_SMOKE_DETECTED) {
            printf("[EMERGENCY] FIRE ALARM! Smoke detected\n");
            TriggerFireAlarm();
            CallFireDepartment();
            SendNotification("FIRE ALARM - Smoke detected");
        }
        
        // 漏水报警
        if(bits & EVENT_WATER_LEAK) {
            printf("[EMERGENCY] WATER LEAK! Shutting off water\n");
            ShutOffWater();
            SendNotification("Water leak detected");
        }
    }
}

// 模式控制任务
void Mode_Control_Task(void *param) {
    while(1) {
        // 等待模式切换事件
        EventBits_t bits = xEventGroupWaitBits(
            home_events,
            EVENT_USER_HOME | EVENT_USER_AWAY | 
            EVENT_NIGHT_MODE | EVENT_DAY_MODE,
            pdTRUE,
            pdFALSE,
            portMAX_DELAY
        );
        
        printf("\n[Mode] Mode change event! bits=0x%03X\n", bits);
        
        // 用户回家
        if(bits & EVENT_USER_HOME) {
            current_mode = MODE_HOME;
            printf("[Mode] Switched to HOME mode\n");
            DisableAlarm();
            TurnOnWelcomeLights();
        }
        
        // 用户离开
        if(bits & EVENT_USER_AWAY) {
            current_mode = MODE_AWAY;
            printf("[Mode] Switched to AWAY mode\n");
            EnableAlarm();
            TurnOffAllLights();
            AdjustTemperature(20.0f);
        }
        
        // 夜间模式
        if(bits & EVENT_NIGHT_MODE) {
            current_mode = MODE_NIGHT;
            printf("[Mode] Switched to NIGHT mode\n");
            DimLights();
            EnableNightSecurity();
        }
        
        // 白天模式
        if(bits & EVENT_DAY_MODE) {
            current_mode = MODE_HOME;
            printf("[Mode] Switched to DAY mode\n");
            RestoreNormalLighting();
        }
    }
}

// 控制函数（示例实现）
void TriggerAlarm(void) {
    printf("  -> Alarm triggered!\n");
}

void SendNotification(const char *message) {
    printf("  -> Notification: %s\n", message);
}

void TurnOnAC(void) {
    printf("  -> Air conditioning ON\n");
}

void TurnOnHeating(void) {
    printf("  -> Heating ON\n");
}

void TurnOnLights(void) {
    printf("  -> Lights ON\n");
}

void TriggerFireAlarm(void) {
    printf("  -> FIRE ALARM ACTIVATED!\n");
}

void CallFireDepartment(void) {
    printf("  -> Calling fire department...\n");
}

void ShutOffWater(void) {
    printf("  -> Water main shut off\n");
}

void DisableAlarm(void) {
    printf("  -> Security alarm disabled\n");
}

void TurnOnWelcomeLights(void) {
    printf("  -> Welcome lights ON\n");
}

void EnableAlarm(void) {
    printf("  -> Security alarm enabled\n");
}

void TurnOffAllLights(void) {
    printf("  -> All lights OFF\n");
}

void AdjustTemperature(float temp) {
    printf("  -> Temperature set to %.1f°C\n", temp);
}

void DimLights(void) {
    printf("  -> Lights dimmed\n");
}

void EnableNightSecurity(void) {
    printf("  -> Night security enabled\n");
}

void RestoreNormalLighting(void) {
    printf("  -> Normal lighting restored\n");
}

// 系统初始化
void Smart_Home_System_Init(void) {
    // 创建事件标志组
    home_events = xEventGroupCreate();
    
    if(home_events != NULL) {
        // 设置初始模式
        xEventGroupSetBits(home_events, EVENT_USER_HOME | EVENT_DAY_MODE);
        
        // 创建任务（优先级从高到低）
        xTaskCreate(Emergency_Task, "Emergency", 512, NULL, 5, NULL);
        xTaskCreate(Security_Task, "Security", 512, NULL, 4, NULL);
        xTaskCreate(Comfort_Task, "Comfort", 512, NULL, 3, NULL);
        xTaskCreate(Mode_Control_Task, "ModeCtrl", 512, NULL, 3, NULL);
        xTaskCreate(Sensor_Monitor_Task, "Sensors", 512, NULL, 2, NULL);
        
        printf("Smart home system initialized\n");
        printf("Current mode: HOME\n\n");
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    
    // 初始化智能家居系统
    Smart_Home_System_Init();
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```


## 总结

### 核心要点

1. **事件标志组概念**
   - 使用位标志表示多个事件状态
   - 24位可用（位0-23）
   - 支持AND和OR等待模式
   - 事件状态持久保存

2. **基本操作**
   - `xEventGroupCreate()`：创建事件标志组
   - `xEventGroupSetBits()`：设置事件位
   - `xEventGroupWaitBits()`：等待事件位
   - `xEventGroupClearBits()`：清除事件位
   - `xEventGroupGetBits()`：获取事件位状态

3. **等待模式**
   - AND模式（pdTRUE）：等待所有指定事件都发生
   - OR模式（pdFALSE）：等待任意一个事件发生
   - 支持超时机制
   - 可选择是否自动清除事件位

4. **中断支持**
   - `xEventGroupSetBitsFromISR()`：从中断设置事件位
   - `xEventGroupGetBitsFromISR()`：从中断获取事件位
   - `xEventGroupClearBitsFromISR()`：从中断清除事件位
   - 必须使用FromISR版本的API

5. **典型应用**
   - 系统初始化同步
   - 多传感器数据采集
   - 多输入源事件处理
   - 任务同步点
   - 状态机实现

6. **最佳实践**
   - 使用描述性的事件位名称
   - 根据场景选择AND/OR模式
   - 合理设置超时时间
   - 注意事件位清除时机
   - 避免竞争条件

### 事件标志组 vs 其他机制

| 特性 | 事件标志组 | 信号量 | 队列 | 任务通知 |
|------|-----------|--------|------|---------|
| **事件数量** | 24个 | 1个 | 多个消息 | 1个值 |
| **等待条件** | AND/OR组合 | 单一 | 单一 | 单一 |
| **内存占用** | 中等 | 小 | 大 | 最小 |
| **速度** | 快 | 快 | 中 | 最快 |
| **多任务等待** | 支持 | 支持 | 不支持 | 不支持 |
| **数据传递** | 不支持 | 不支持 | 支持 | 有限支持 |

### 学习检查清单

完成本教程后，你应该能够：

- [ ] 理解FreeRTOS事件标志组的工作原理和内部结构
- [ ] 掌握事件组的创建、删除和管理方法
- [ ] 熟练使用位操作定义和组合事件
- [ ] 理解AND和OR等待模式的区别和应用场景
- [ ] 能够从任务和中断中正确操作事件组
- [ ] 掌握事件位的设置、清除和查询方法
- [ ] 能够使用事件组实现复杂的多任务同步
- [ ] 解决事件组使用中的常见问题
- [ ] 在实际项目中合理选择同步机制


## 进阶挑战

尝试以下挑战来巩固学习：

### 挑战1：实现事件组管理器

创建一个事件组管理器，提供以下功能：
- 事件组池管理（创建、分配、释放）
- 事件历史记录和回放
- 事件统计（触发次数、等待时间）
- 事件依赖关系管理

**提示**：使用结构体封装事件组和元数据

### 挑战2：实现复杂状态机

使用事件标志组实现一个复杂的状态机：
- 支持多个状态（使用不同的位组合）
- 支持状态转换条件检查
- 支持状态进入/退出回调
- 支持状态历史记录

**提示**：使用位组合表示状态，使用事件触发状态转换

### 挑战3：实现事件优先级队列

基于事件标志组实现一个优先级事件队列：
- 支持多个优先级级别
- 高优先级事件优先处理
- 支持事件超时
- 支持事件取消

**提示**：使用不同的位表示不同优先级

### 挑战4：实现分布式事件系统

实现一个跨任务的分布式事件系统：
- 支持事件订阅和发布
- 支持事件过滤
- 支持事件广播
- 支持事件持久化

**提示**：结合事件组和队列实现


## 延伸阅读

### 相关教程

- [FreeRTOS快速入门](../beginner/01-freertos-quickstart.html) - 了解FreeRTOS基础
- [FreeRTOS任务管理](../beginner/02-freertos-tasks.html) - 深入理解任务机制
- [FreeRTOS队列通信](../beginner/03-freertos-queue.html) - 学习任务间通信
- [FreeRTOS软件定时器](01-freertos-timer.html) - 学习定时器应用
- [FreeRTOS任务通知](03-freertos-notification.html) - 学习轻量级通信
- [RTOS事件标志组基础](../../02-rtos-fundamentals/beginner/07-event-group.html) - 理论基础

### 官方文档

- [FreeRTOS Event Groups](https://www.freertos.org/event-groups-API.html)
- [FreeRTOS API Reference](https://www.freertos.org/a00106.html)
- [FreeRTOS Configuration](https://www.freertos.org/a00110.html)

### 推荐书籍

- **《Mastering the FreeRTOS Real Time Kernel》**
  - FreeRTOS作者编写
  - 详细讲解事件标志组实现
  - 免费下载：https://www.freertos.org/Documentation/RTOS_book.html

- **《FreeRTOS Reference Manual》**
  - 完整的API参考手册
  - 包含所有事件组API详细说明

### 测试环境

**本教程测试环境**：
- 开发板：STM32F407 Discovery
- IDE：STM32CubeIDE v1.10.1
- HAL库版本：v1.27.1
- FreeRTOS版本：V10.3.1
- 编译器：GCC ARM 10.3

---

**反馈与支持**：

如果你在学习过程中遇到问题：
- 💬 在评论区留言讨论
- 📧 发送邮件到：support@embedded-platform.com
- 🐛 报告问题：[GitHub Issues](https://github.com/your-repo/issues)

**贡献代码**：
欢迎提交改进建议和示例代码！

---

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**最后更新**：2024-01-15  
**文档版本**：1.0
