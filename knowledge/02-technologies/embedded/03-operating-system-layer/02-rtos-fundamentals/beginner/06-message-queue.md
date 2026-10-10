---
title: "消息队列(Queue)通信机制：实现RTOS任务间高效数据传递"
description: "深入学习RTOS消息队列的核心概念和实践应用。掌握队列原理、消息传递机制、阻塞策略和队列管理方法，通过丰富的代码示例学会构建高效的任务间通信系统。"
slug: "message-queue"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 消息队列
  - 任务通信
  - 数据传递
  - 阻塞机制
  - FreeRTOS
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/05-mutex.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/07-event-group.md"
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/02-ipc-comparison.md"

# 学习信息
estimated_time: 70
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
  - RTOS消息队列
  - 任务通信
  - 数据传递
  - 队列管理
  - FreeRTOS队列
  - 阻塞机制
cover_image: ""
---


# 消息队列(Queue)通信机制：实现RTOS任务间高效数据传递

## 学习目标

完成本教程后，你将能够：

- 理解消息队列的概念和工作原理
- 掌握队列的创建和管理方法
- 学会使用队列实现任务间数据传递
- 理解队列的阻塞机制和超时处理
- 掌握队列在不同场景下的应用
- 能够解决常见的队列使用问题


## 前置要求

### 知识要求

- 理解RTOS的基本概念
- 掌握任务创建和管理
- 了解任务调度机制
- 理解信号量的基本使用

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
| 按键 | 1-2个 | 用于触发事件（可选） |

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
#define configUSE_PREEMPTION                1  // 启用抢占式调度
#define configUSE_QUEUE_SETS                1  // 启用队列集（可选）
#define configMAX_PRIORITIES                5  // 最大优先级数
#define configTICK_RATE_HZ                  1000  // 时钟节拍频率
```


## 概述

### 什么是消息队列？

**消息队列(Message Queue)**是RTOS中用于任务间数据传递的重要机制。它是一个先进先出(FIFO)的数据结构，允许任务之间安全地传递数据。

**生活中的类比**：

想象一个邮局的邮箱：
- 发件人投递信件（发送消息）
- 信件按顺序排列（FIFO队列）
- 收件人取出信件（接收消息）
- 邮箱有容量限制（队列长度）
- 邮箱满时需要等待（阻塞发送）
- 邮箱空时需要等待（阻塞接收）

### 为什么需要消息队列？

在多任务系统中，任务之间经常需要传递数据：

**问题1：数据传递**
```c
// 任务A：采集传感器数据
void SensorTask(void *param) {
    while(1) {
        float temperature = ReadTemperature();
        // 如何将温度数据传递给任务B？
    }
}

// 任务B：处理数据
void ProcessTask(void *param) {
    while(1) {
        // 如何接收任务A的温度数据？
        ProcessTemperature(temperature);
    }
}
```

**问题2：数据缓冲**
```c
// 中断产生数据很快，任务处理较慢
void UART_IRQHandler(void) {
    uint8_t data = UART_ReceiveData();
    // 如何缓存数据，避免丢失？
}
```

消息队列可以优雅地解决这些问题。

### 消息队列 vs 信号量

| 特性 | 消息队列 | 信号量 |
|------|---------|--------|
| **数据传递** | 传递数据 | 不传递数据 |
| **用途** | 任务间通信 | 任务同步 |
| **容量** | 可存储多个消息 | 只有计数值 |
| **FIFO** | 先进先出 | 无顺序概念 |
| **典型场景** | 数据传递、缓冲 | 事件通知、资源管理 |

**选择建议**：
- 需要传递数据 → 使用消息队列
- 只需要通知事件 → 使用信号量


## 步骤1：创建和使用队列

### 1.1 队列的基本概念

**队列结构**：

```
队列头 → [消息1] [消息2] [消息3] [空] [空] ← 队列尾
         ↑                              ↑
       读取位置                      写入位置
```

**关键参数**：
- **队列长度**：可以存储的消息数量
- **消息大小**：每个消息的字节数
- **阻塞时间**：发送/接收时的等待时间

### 1.2 创建队列

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 声明队列句柄
QueueHandle_t data_queue;

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 创建队列
    // 参数1：队列长度（可存储的消息数量）
    // 参数2：每个消息的大小（字节）
    data_queue = xQueueCreate(10, sizeof(uint32_t));
    
    if(data_queue != NULL) {
        printf("Queue created successfully\n");
        printf("Queue length: 10, Item size: %d bytes\n", sizeof(uint32_t));
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    } else {
        printf("Failed to create queue\n");
    }
    
    while(1);
}
```

**代码说明**：
- `xQueueCreate()`：创建队列
- 第一个参数：队列长度（消息数量）
- 第二个参数：每个消息的大小（字节）
- 返回值：队列句柄，失败返回NULL

### 1.3 发送消息

#### 发送到队列尾部（Send）

```c
// 发送消息到队列尾部
BaseType_t xQueueSend(
    QueueHandle_t xQueue,
    const void *pvItemToQueue,  // 要发送的数据指针
    TickType_t xTicksToWait     // 等待时间
);

// 示例
uint32_t data = 100;
if(xQueueSend(data_queue, &data, pdMS_TO_TICKS(1000)) == pdTRUE) {
    printf("Data sent successfully\n");
} else {
    printf("Queue full, send failed\n");
}
```

#### 发送到队列头部（SendToFront）

```c
// 发送消息到队列头部（插队）
BaseType_t xQueueSendToFront(
    QueueHandle_t xQueue,
    const void *pvItemToQueue,
    TickType_t xTicksToWait
);

// 用于紧急消息
uint32_t urgent_data = 999;
xQueueSendToFront(data_queue, &urgent_data, 0);
```

#### 在中断中发送（SendFromISR）

```c
// 在中断中发送消息
BaseType_t xQueueSendFromISR(
    QueueHandle_t xQueue,
    const void *pvItemToQueue,
    BaseType_t *pxHigherPriorityTaskWoken
);

// 中断服务函数示例
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    uint8_t data = UART_ReceiveData();
    
    // 发送到队列
    xQueueSendFromISR(data_queue, &data, &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 1.4 接收消息

```c
// 接收消息（从队列头部）
BaseType_t xQueueReceive(
    QueueHandle_t xQueue,
    void *pvBuffer,          // 接收缓冲区指针
    TickType_t xTicksToWait  // 等待时间
);

// 示例
uint32_t received_data;
if(xQueueReceive(data_queue, &received_data, portMAX_DELAY) == pdTRUE) {
    printf("Received data: %d\n", received_data);
}
```

**参数说明**：
- `xTicksToWait = 0`：不等待，立即返回
- `xTicksToWait = portMAX_DELAY`：永久等待
- `xTicksToWait = pdMS_TO_TICKS(1000)`：等待1000ms

### 1.5 完整示例：基本队列通信

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 队列句柄
QueueHandle_t data_queue;

// 发送任务
void SenderTask(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        counter++;
        
        printf("[Sender] Sending data: %d\n", counter);
        
        // 发送数据到队列
        if(xQueueSend(data_queue, &counter, pdMS_TO_TICKS(1000)) == pdTRUE) {
            printf("[Sender] Data sent successfully\n");
        } else {
            printf("[Sender] Queue full, send failed\n");
        }
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 接收任务
void ReceiverTask(void *param) {
    uint32_t received_data;
    
    while(1) {
        // 等待接收数据
        if(xQueueReceive(data_queue, &received_data, portMAX_DELAY) == pdTRUE) {
            printf("[Receiver] Received data: %d\n", received_data);
            
            // 处理数据
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建队列（长度10，每个消息4字节）
    data_queue = xQueueCreate(10, sizeof(uint32_t));
    
    if(data_queue != NULL) {
        // 创建任务
        xTaskCreate(SenderTask, "Sender", 256, NULL, 2, NULL);
        xTaskCreate(ReceiverTask, "Receiver", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[Sender] Sending data: 1
[Sender] Data sent successfully
[Receiver] Received data: 1
[Sender] Sending data: 2
[Sender] Data sent successfully
[Sender] Sending data: 3
[Sender] Data sent successfully
[Receiver] Received data: 2
[Sender] Sending data: 4
[Sender] Data sent successfully
[Receiver] Received data: 3
```

**代码说明**：
- 发送任务每500ms发送一个数据
- 接收任务每1000ms处理一个数据
- 队列自动缓存未处理的数据


## 步骤2：传递复杂数据结构

### 2.1 传递结构体

队列可以传递任意类型的数据，包括结构体：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 定义传感器数据结构
typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
    uint8_t sensor_id;
} SensorData_t;

// 队列句柄
QueueHandle_t sensor_queue;

// 传感器任务
void SensorTask(void *param) {
    uint8_t sensor_id = (uint8_t)(uint32_t)param;
    
    while(1) {
        // 准备数据
        SensorData_t data;
        data.temperature = 25.5f + (sensor_id * 0.5f);
        data.humidity = 60.0f + (sensor_id * 2.0f);
        data.timestamp = xTaskGetTickCount();
        data.sensor_id = sensor_id;
        
        printf("[Sensor %d] Reading: Temp=%.1f°C, Humidity=%.1f%%\n",
               sensor_id, data.temperature, data.humidity);
        
        // 发送结构体到队列
        if(xQueueSend(sensor_queue, &data, pdMS_TO_TICKS(100)) == pdTRUE) {
            printf("[Sensor %d] Data sent to queue\n", sensor_id);
        } else {
            printf("[Sensor %d] Queue full!\n", sensor_id);
        }
        
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

// 数据处理任务
void ProcessTask(void *param) {
    SensorData_t received_data;
    
    while(1) {
        // 接收数据
        if(xQueueReceive(sensor_queue, &received_data, portMAX_DELAY) == pdTRUE) {
            printf("[Process] Received from Sensor %d:\n", received_data.sensor_id);
            printf("          Temperature: %.1f°C\n", received_data.temperature);
            printf("          Humidity: %.1f%%\n", received_data.humidity);
            printf("          Timestamp: %d ms\n\n", received_data.timestamp);
            
            // 处理数据
            vTaskDelay(pdMS_TO_TICKS(500));
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建队列（传递结构体）
    sensor_queue = xQueueCreate(5, sizeof(SensorData_t));
    
    if(sensor_queue != NULL) {
        // 创建多个传感器任务
        xTaskCreate(SensorTask, "Sensor1", 256, (void *)1, 2, NULL);
        xTaskCreate(SensorTask, "Sensor2", 256, (void *)2, 2, NULL);
        xTaskCreate(SensorTask, "Sensor3", 256, (void *)3, 2, NULL);
        
        // 创建处理任务
        xTaskCreate(ProcessTask, "Process", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**：
```
[Sensor 1] Reading: Temp=26.0°C, Humidity=62.0%
[Sensor 1] Data sent to queue
[Process] Received from Sensor 1:
          Temperature: 26.0°C
          Humidity: 62.0%
          Timestamp: 1000 ms

[Sensor 2] Reading: Temp=26.5°C, Humidity=64.0%
[Sensor 2] Data sent to queue
[Sensor 3] Reading: Temp=27.0°C, Humidity=66.0%
[Sensor 3] Data sent to queue
[Process] Received from Sensor 2:
          Temperature: 26.5°C
          Humidity: 64.0%
          Timestamp: 1000 ms
```

**代码说明**：
- 定义传感器数据结构体
- 多个传感器任务发送数据到同一个队列
- 处理任务按顺序接收和处理数据
- 队列自动管理数据的存储和顺序

### 2.2 传递指针（注意事项）

⚠️ **重要提示**：传递指针时要特别小心！

**错误示例**：
```c
// ❌ 错误：传递局部变量的指针
void BadSenderTask(void *param) {
    while(1) {
        uint32_t data = 100;  // 局部变量
        uint32_t *ptr = &data;
        
        // 危险！data在函数返回后失效
        xQueueSend(ptr_queue, &ptr, 0);
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

**正确示例1：传递动态分配的内存**
```c
// ✅ 正确：传递动态分配的内存指针
void GoodSenderTask(void *param) {
    while(1) {
        // 动态分配内存
        uint32_t *data = (uint32_t *)pvPortMalloc(sizeof(uint32_t));
        
        if(data != NULL) {
            *data = 100;
            
            // 发送指针
            xQueueSend(ptr_queue, &data, 0);
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void ReceiverTask(void *param) {
    uint32_t *received_ptr;
    
    while(1) {
        if(xQueueReceive(ptr_queue, &received_ptr, portMAX_DELAY) == pdTRUE) {
            // 使用数据
            printf("Received: %d\n", *received_ptr);
            
            // 释放内存
            vPortFree(received_ptr);
        }
    }
}
```

**正确示例2：传递静态或全局变量的指针**
```c
// ✅ 正确：传递静态缓冲区的指针
#define BUFFER_COUNT 5
static uint8_t buffers[BUFFER_COUNT][256];

void SenderTask(void *param) {
    static uint8_t buffer_index = 0;
    
    while(1) {
        // 使用静态缓冲区
        uint8_t *buffer = buffers[buffer_index];
        buffer_index = (buffer_index + 1) % BUFFER_COUNT;
        
        // 填充数据
        sprintf((char *)buffer, "Message %d", buffer_index);
        
        // 发送指针
        xQueueSend(ptr_queue, &buffer, 0);
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```


## 步骤3：队列管理和查询

### 3.1 查询队列状态

```c
// 获取队列中等待的消息数量
UBaseType_t uxQueueMessagesWaiting(QueueHandle_t xQueue);

// 获取队列中可用空间数量
UBaseType_t uxQueueSpacesAvailable(QueueHandle_t xQueue);

// 检查队列是否为空
BaseType_t xQueueIsQueueEmptyFromISR(QueueHandle_t xQueue);

// 检查队列是否已满
BaseType_t xQueueIsQueueFullFromISR(QueueHandle_t xQueue);

// 示例
void MonitorTask(void *param) {
    while(1) {
        UBaseType_t waiting = uxQueueMessagesWaiting(data_queue);
        UBaseType_t available = uxQueueSpacesAvailable(data_queue);
        
        printf("[Monitor] Queue status:\n");
        printf("          Messages waiting: %d\n", waiting);
        printf("          Spaces available: %d\n\n", available);
        
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}
```

### 3.2 窥视队列（Peek）

```c
// 查看队列头部的消息，但不移除
BaseType_t xQueuePeek(
    QueueHandle_t xQueue,
    void *pvBuffer,
    TickType_t xTicksToWait
);

// 示例：查看但不取出消息
void PeekTask(void *param) {
    uint32_t peeked_data;
    
    while(1) {
        // 窥视队列
        if(xQueuePeek(data_queue, &peeked_data, 0) == pdTRUE) {
            printf("[Peek] Next message: %d (not removed)\n", peeked_data);
        } else {
            printf("[Peek] Queue is empty\n");
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

### 3.3 重置队列

```c
// 清空队列中的所有消息
BaseType_t xQueueReset(QueueHandle_t xQueue);

// 示例
void ResetTask(void *param) {
    while(1) {
        // 等待某个条件
        vTaskDelay(pdMS_TO_TICKS(10000));
        
        // 清空队列
        xQueueReset(data_queue);
        printf("[Reset] Queue cleared\n");
    }
}
```

### 3.4 删除队列

```c
// 删除队列，释放内存
void vQueueDelete(QueueHandle_t xQueue);

// 示例
void CleanupTask(void *param) {
    // 使用队列...
    
    // 不再需要时删除
    vQueueDelete(data_queue);
    printf("Queue deleted\n");
    
    vTaskDelete(NULL);
}
```


## 步骤4：阻塞机制和超时处理

### 4.1 理解阻塞机制

**发送阻塞**：
```
队列状态：[满] [满] [满] [满] [满]

任务A尝试发送 → 队列已满 → 任务A阻塞等待
任务B接收消息 → 队列有空间 → 任务A被唤醒 → 发送成功
```

**接收阻塞**：
```
队列状态：[空] [空] [空] [空] [空]

任务A尝试接收 → 队列为空 → 任务A阻塞等待
任务B发送消息 → 队列有数据 → 任务A被唤醒 → 接收成功
```

### 4.2 超时处理示例

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

QueueHandle_t data_queue;

// 发送任务（带超时处理）
void SenderTask(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        counter++;
        
        // 尝试发送，超时1秒
        BaseType_t result = xQueueSend(data_queue, &counter, pdMS_TO_TICKS(1000));
        
        if(result == pdTRUE) {
            printf("[Sender] Data %d sent successfully\n", counter);
        } else {
            printf("[Sender] Timeout! Queue full for 1 second\n");
            printf("[Sender] Discarding data %d\n", counter);
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 接收任务（带超时处理）
void ReceiverTask(void *param) {
    uint32_t received_data;
    
    while(1) {
        // 尝试接收，超时2秒
        BaseType_t result = xQueueReceive(data_queue, &received_data, pdMS_TO_TICKS(2000));
        
        if(result == pdTRUE) {
            printf("[Receiver] Received data: %d\n", received_data);
            
            // 处理数据
            vTaskDelay(pdMS_TO_TICKS(500));
        } else {
            printf("[Receiver] Timeout! No data for 2 seconds\n");
            printf("[Receiver] Performing idle task...\n");
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建小容量队列（容易满）
    data_queue = xQueueCreate(3, sizeof(uint32_t));
    
    // 创建任务
    xTaskCreate(SenderTask, "Sender", 256, NULL, 2, NULL);
    xTaskCreate(ReceiverTask, "Receiver", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Sender] Data 1 sent successfully
[Sender] Data 2 sent successfully
[Sender] Data 3 sent successfully
[Sender] Timeout! Queue full for 1 second
[Sender] Discarding data 4
[Receiver] Received data: 1
[Sender] Data 5 sent successfully
[Receiver] Received data: 2
```

### 4.3 非阻塞操作

```c
// 非阻塞发送（立即返回）
if(xQueueSend(data_queue, &data, 0) == pdTRUE) {
    printf("Sent immediately\n");
} else {
    printf("Queue full, not sent\n");
}

// 非阻塞接收（立即返回）
if(xQueueReceive(data_queue, &data, 0) == pdTRUE) {
    printf("Received immediately\n");
} else {
    printf("Queue empty, nothing received\n");
}
```


## 步骤5：实际应用场景

### 5.1 中断与任务通信

使用队列实现中断服务函数与任务之间的数据传递：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 队列句柄
QueueHandle_t uart_queue;

// UART中断服务函数
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 检查接收中断
    if(__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        // 读取数据
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        
        // 发送到队列
        xQueueSendFromISR(uart_queue, &data, &xHigherPriorityTaskWoken);
        
        // 触发任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// UART处理任务
void UARTProcessTask(void *param) {
    uint8_t received_byte;
    uint8_t buffer[256];
    uint8_t index = 0;
    
    while(1) {
        // 接收数据
        if(xQueueReceive(uart_queue, &received_byte, portMAX_DELAY) == pdTRUE) {
            // 处理接收到的字节
            if(received_byte == '\n' || received_byte == '\r') {
                // 收到换行符，处理完整命令
                buffer[index] = '\0';
                printf("[UART] Received command: %s\n", buffer);
                
                // 处理命令
                ProcessCommand((char *)buffer);
                
                // 重置缓冲区
                index = 0;
            } else if(index < sizeof(buffer) - 1) {
                // 添加到缓冲区
                buffer[index++] = received_byte;
            }
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化UART
    MX_UART_Init();
    
    // 创建队列（缓存64个字节）
    uart_queue = xQueueCreate(64, sizeof(uint8_t));
    
    // 创建处理任务
    xTaskCreate(UARTProcessTask, "UART", 512, NULL, 3, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**代码说明**：
- 中断服务函数快速将数据放入队列
- 任务从队列中取出数据进行处理
- 避免在中断中进行复杂处理
- 提高系统响应性和可靠性

### 5.2 生产者-消费者模式

实现经典的生产者-消费者模式：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 数据结构
typedef struct {
    uint32_t id;
    uint32_t value;
    uint32_t timestamp;
} DataItem_t;

// 队列句柄
QueueHandle_t production_queue;

// 生产者任务
void ProducerTask(void *param) {
    uint32_t producer_id = (uint32_t)param;
    uint32_t item_count = 0;
    
    while(1) {
        // 生产数据
        DataItem_t item;
        item.id = producer_id;
        item.value = item_count++;
        item.timestamp = xTaskGetTickCount();
        
        printf("[Producer %d] Producing item %d\n", producer_id, item.value);
        
        // 发送到队列
        if(xQueueSend(production_queue, &item, pdMS_TO_TICKS(1000)) == pdTRUE) {
            printf("[Producer %d] Item %d sent to queue\n", producer_id, item.value);
        } else {
            printf("[Producer %d] Queue full, item %d discarded\n", producer_id, item.value);
        }
        
        // 生产速度
        vTaskDelay(pdMS_TO_TICKS(300 + (producer_id * 100)));
    }
}

// 消费者任务
void ConsumerTask(void *param) {
    uint32_t consumer_id = (uint32_t)param;
    DataItem_t item;
    
    while(1) {
        // 从队列获取数据
        if(xQueueReceive(production_queue, &item, portMAX_DELAY) == pdTRUE) {
            printf("[Consumer %d] Consuming item from Producer %d: value=%d, time=%d\n",
                   consumer_id, item.id, item.value, item.timestamp);
            
            // 模拟消费处理
            vTaskDelay(pdMS_TO_TICKS(500));
            
            printf("[Consumer %d] Item processed\n\n", consumer_id);
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建队列
    production_queue = xQueueCreate(10, sizeof(DataItem_t));
    
    // 创建3个生产者任务
    xTaskCreate(ProducerTask, "Producer1", 256, (void *)1, 2, NULL);
    xTaskCreate(ProducerTask, "Producer2", 256, (void *)2, 2, NULL);
    xTaskCreate(ProducerTask, "Producer3", 256, (void *)3, 2, NULL);
    
    // 创建2个消费者任务
    xTaskCreate(ConsumerTask, "Consumer1", 256, (void *)1, 2, NULL);
    xTaskCreate(ConsumerTask, "Consumer2", 256, (void *)2, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Producer 1] Producing item 0
[Producer 1] Item 0 sent to queue
[Consumer 1] Consuming item from Producer 1: value=0, time=400
[Producer 2] Producing item 0
[Producer 2] Item 0 sent to queue
[Producer 3] Producing item 0
[Producer 3] Item 0 sent to queue
[Consumer 1] Item processed

[Consumer 2] Consuming item from Producer 2: value=0, time=500
[Producer 1] Producing item 1
[Producer 1] Item 1 sent to queue
```

**代码说明**：
- 多个生产者任务生产数据
- 多个消费者任务消费数据
- 队列自动管理数据的缓冲和同步
- 实现了解耦和负载均衡

### 5.3 数据流水线处理

实现多阶段数据处理流水线：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 数据结构
typedef struct {
    uint32_t raw_value;
    uint32_t processed_value;
    uint8_t stage;
} PipelineData_t;

// 队列句柄
QueueHandle_t stage1_queue;  // 采集 → 预处理
QueueHandle_t stage2_queue;  // 预处理 → 分析
QueueHandle_t stage3_queue;  // 分析 → 输出

// 阶段1：数据采集
void Stage1_AcquisitionTask(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        PipelineData_t data;
        data.raw_value = counter++;
        data.processed_value = 0;
        data.stage = 1;
        
        printf("[Stage1] Acquired data: %d\n", data.raw_value);
        
        // 发送到下一阶段
        xQueueSend(stage1_queue, &data, portMAX_DELAY);
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 阶段2：数据预处理
void Stage2_PreprocessTask(void *param) {
    PipelineData_t data;
    
    while(1) {
        // 接收上一阶段的数据
        if(xQueueReceive(stage1_queue, &data, portMAX_DELAY) == pdTRUE) {
            printf("[Stage2] Preprocessing data: %d\n", data.raw_value);
            
            // 预处理（滤波、校准等）
            data.processed_value = data.raw_value * 2;
            data.stage = 2;
            
            vTaskDelay(pdMS_TO_TICKS(200));
            
            // 发送到下一阶段
            xQueueSend(stage2_queue, &data, portMAX_DELAY);
        }
    }
}

// 阶段3：数据分析
void Stage3_AnalysisTask(void *param) {
    PipelineData_t data;
    
    while(1) {
        // 接收上一阶段的数据
        if(xQueueReceive(stage2_queue, &data, portMAX_DELAY) == pdTRUE) {
            printf("[Stage3] Analyzing data: %d\n", data.processed_value);
            
            // 分析处理
            data.processed_value = data.processed_value + 100;
            data.stage = 3;
            
            vTaskDelay(pdMS_TO_TICKS(300));
            
            // 发送到下一阶段
            xQueueSend(stage3_queue, &data, portMAX_DELAY);
        }
    }
}

// 阶段4：数据输出
void Stage4_OutputTask(void *param) {
    PipelineData_t data;
    
    while(1) {
        // 接收上一阶段的数据
        if(xQueueReceive(stage3_queue, &data, portMAX_DELAY) == pdTRUE) {
            printf("[Stage4] Final output: raw=%d, processed=%d\n\n",
                   data.raw_value, data.processed_value);
            
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建流水线队列
    stage1_queue = xQueueCreate(5, sizeof(PipelineData_t));
    stage2_queue = xQueueCreate(5, sizeof(PipelineData_t));
    stage3_queue = xQueueCreate(5, sizeof(PipelineData_t));
    
    // 创建流水线任务
    xTaskCreate(Stage1_AcquisitionTask, "Stage1", 256, NULL, 2, NULL);
    xTaskCreate(Stage2_PreprocessTask, "Stage2", 256, NULL, 2, NULL);
    xTaskCreate(Stage3_AnalysisTask, "Stage3", 256, NULL, 2, NULL);
    xTaskCreate(Stage4_OutputTask, "Stage4", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Stage1] Acquired data: 0
[Stage2] Preprocessing data: 0
[Stage3] Analyzing data: 0
[Stage4] Final output: raw=0, processed=100

[Stage1] Acquired data: 1
[Stage2] Preprocessing data: 1
[Stage3] Analyzing data: 2
[Stage4] Final output: raw=1, processed=102
```

**代码说明**：
- 数据按照固定流程处理：采集→预处理→分析→输出
- 每个阶段独立运行，通过队列连接
- 实现了流水线并行处理
- 提高了系统吞吐量


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

3. **查看串口输出**
   - 打开串口调试工具
   - 配置：115200, 8N1
   - 观察任务执行和队列操作的输出

### 预期结果

**基本队列通信**：
- 发送任务成功发送数据
- 接收任务按顺序接收数据
- 队列自动缓存数据

**结构体传递**：
- 多个传感器任务发送数据
- 处理任务正确接收完整结构体
- 数据内容完整无误

**中断通信**：
- 中断快速将数据放入队列
- 任务从队列取出数据处理
- 系统响应及时

**流水线处理**：
- 数据按阶段依次处理
- 各阶段并行运行
- 输出结果正确

### 测试要点

1. **功能测试**
   - [ ] 队列创建成功
   - [ ] 发送和接收工作正常
   - [ ] 数据传递正确
   - [ ] 阻塞机制工作正常

2. **边界测试**
   - [ ] 队列满时发送阻塞
   - [ ] 队列空时接收阻塞
   - [ ] 超时机制工作正常
   - [ ] 队列重置正确

3. **性能测试**
   - [ ] 数据传递及时
   - [ ] 无数据丢失
   - [ ] 系统响应流畅


## 故障排除

### 问题1：队列创建失败

**现象**：
```c
data_queue = xQueueCreate(10, sizeof(uint32_t));
if(data_queue == NULL) {
    printf("Failed to create queue\n");
}
```

**可能原因**：
1. 堆内存不足
2. 队列长度或消息大小过大
3. FreeRTOS配置错误

**解决方法**：

```c
// 1. 增加堆大小（FreeRTOSConfig.h）
#define configTOTAL_HEAP_SIZE  ((size_t)(20 * 1024))  // 增加到20KB

// 2. 减小队列大小
data_queue = xQueueCreate(5, sizeof(uint32_t));  // 减小长度

// 3. 检查剩余堆空间
size_t free_heap = xPortGetFreeHeapSize();
printf("Free heap: %d bytes\n", free_heap);

// 4. 计算队列所需内存
size_t queue_size = 10 * sizeof(uint32_t) + sizeof(StaticQueue_t);
printf("Queue needs: %d bytes\n", queue_size);
```

### 问题2：数据接收不正确

**现象**：
```c
// 发送的数据和接收的数据不一致
uint32_t sent = 100;
xQueueSend(queue, &sent, 0);

uint32_t received;
xQueueReceive(queue, &received, 0);
printf("Received: %d\n", received);  // 输出错误的值
```

**可能原因**：
1. 队列消息大小设置错误
2. 数据类型不匹配
3. 指针使用错误

**解决方法**：

```c
// 1. 确保消息大小正确
// ❌ 错误
queue = xQueueCreate(10, sizeof(uint32_t *));  // 指针大小
// ✅ 正确
queue = xQueueCreate(10, sizeof(uint32_t));    // 数据大小

// 2. 确保数据类型匹配
typedef struct {
    uint32_t value;
    float data;
} MyData_t;

MyData_t send_data = {100, 25.5f};
MyData_t recv_data;

xQueueSend(queue, &send_data, 0);
xQueueReceive(queue, &recv_data, 0);

// 3. 正确使用指针
// ❌ 错误：传递局部变量指针
void BadFunction(void) {
    uint32_t data = 100;
    xQueueSend(queue, &data, 0);  // data在函数返回后失效
}

// ✅ 正确：传递数据本身
void GoodFunction(void) {
    uint32_t data = 100;
    xQueueSend(queue, &data, 0);  // 队列复制数据
}
```

### 问题3：任务永久阻塞

**现象**：
```c
// 任务一直等待，永不返回
xQueueReceive(queue, &data, portMAX_DELAY);
printf("This never prints\n");
```

**可能原因**：
1. 没有任务发送数据
2. 队列句柄错误
3. 死锁情况

**解决方法**：

```c
// 1. 使用超时等待
if(xQueueReceive(queue, &data, pdMS_TO_TICKS(5000)) == pdTRUE) {
    printf("Received: %d\n", data);
} else {
    printf("Timeout waiting for data\n");
    // 错误处理
}

// 2. 检查队列句柄
if(queue == NULL) {
    printf("Queue handle is NULL!\n");
    return;
}

// 3. 添加调试输出
printf("Waiting for data...\n");
xQueueReceive(queue, &data, portMAX_DELAY);
printf("Data received\n");

// 4. 检查队列状态
UBaseType_t waiting = uxQueueMessagesWaiting(queue);
printf("Messages in queue: %d\n", waiting);
```

### 问题4：数据丢失

**现象**：
```c
// 发送了10个数据，但只接收到5个
for(int i = 0; i < 10; i++) {
    xQueueSend(queue, &i, 0);  // 部分发送失败
}
```

**可能原因**：
1. 队列容量不足
2. 发送超时时间为0
3. 接收速度慢于发送速度

**解决方法**：

```c
// 1. 增加队列容量
queue = xQueueCreate(20, sizeof(uint32_t));  // 增加容量

// 2. 使用超时等待
for(int i = 0; i < 10; i++) {
    if(xQueueSend(queue, &i, pdMS_TO_TICKS(1000)) != pdTRUE) {
        printf("Failed to send data %d\n", i);
    }
}

// 3. 检查发送结果
BaseType_t result = xQueueSend(queue, &data, 0);
if(result != pdTRUE) {
    printf("Queue full, data lost\n");
    // 记录丢失的数据
}

// 4. 监控队列状态
UBaseType_t available = uxQueueSpacesAvailable(queue);
if(available == 0) {
    printf("Warning: Queue is full!\n");
}
```

### 问题5：中断中使用错误的API

**现象**：
```c
// 在中断中使用普通API（错误）
void UART_IRQHandler(void) {
    uint8_t data = UART_ReceiveData();
    xQueueSend(queue, &data, 0);  // ❌ 错误！
}
```

**解决方法**：

```c
// 在中断中必须使用FromISR版本的API
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint8_t data = UART_ReceiveData();
    
    // ✅ 正确：使用FromISR版本
    xQueueSendFromISR(queue, &data, &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```


## 常见问题

### Q1: 队列和信号量有什么区别？

**A**: 主要区别在于数据传递：

| 特性 | 消息队列 | 信号量 |
|------|---------|--------|
| **数据传递** | 传递数据 | 不传递数据 |
| **用途** | 任务间通信 | 任务同步 |
| **容量** | 可存储多个消息 | 只有计数值 |
| **FIFO** | 先进先出 | 无顺序概念 |
| **开销** | 较大（需要复制数据） | 小 |

**选择建议**：
- 需要传递数据 → 使用消息队列
- 只需要通知事件 → 使用信号量

**示例**：
```c
// 队列：传递具体数据
SensorData_t data = {.temp = 25.5, .humidity = 60};
xQueueSend(data_queue, &data, 0);

// 信号量：只通知事件发生
xSemaphoreGive(event_sem);
```

### Q2: 队列应该设置多大？

**A**: 根据应用场景确定：

**考虑因素**：
1. **数据产生速度 vs 处理速度**
   - 产生快，处理慢 → 需要较大队列
   - 产生慢，处理快 → 较小队列即可

2. **内存限制**
   - 队列占用内存 = 队列长度 × 消息大小 + 控制开销
   - 需要在功能和内存之间平衡

3. **实时性要求**
   - 实时性要求高 → 较小队列，避免延迟
   - 可以容忍延迟 → 较大队列，提高吞吐量

**经验值**：
```c
// 中断缓冲：根据中断频率和处理速度
uart_queue = xQueueCreate(64, sizeof(uint8_t));  // UART接收缓冲

// 任务通信：一般5-20个消息
data_queue = xQueueCreate(10, sizeof(DataStruct_t));

// 事件队列：较小即可
event_queue = xQueueCreate(5, sizeof(EventType_t));
```

### Q3: 如何传递大数据？

**A**: 有三种方法：

**方法1：传递指针（推荐）**
```c
// 定义数据结构
typedef struct {
    uint8_t data[1024];  // 大数据
    uint32_t size;
} LargeData_t;

// 动态分配内存
LargeData_t *pData = (LargeData_t *)pvPortMalloc(sizeof(LargeData_t));
// 填充数据...

// 发送指针（只复制4字节指针）
xQueueSend(ptr_queue, &pData, 0);

// 接收端
LargeData_t *pReceived;
xQueueReceive(ptr_queue, &pReceived, portMAX_DELAY);
// 使用数据...
vPortFree(pReceived);  // 释放内存
```

**方法2：使用静态缓冲区**
```c
// 定义缓冲区池
#define BUFFER_COUNT 5
static uint8_t buffers[BUFFER_COUNT][1024];
static uint8_t buffer_index = 0;

// 获取缓冲区指针
uint8_t *pBuffer = buffers[buffer_index];
buffer_index = (buffer_index + 1) % BUFFER_COUNT;

// 发送指针
xQueueSend(ptr_queue, &pBuffer, 0);
```

**方法3：分块传输**
```c
// 将大数据分成小块传输
#define CHUNK_SIZE 64
for(int i = 0; i < total_size; i += CHUNK_SIZE) {
    uint8_t chunk[CHUNK_SIZE];
    memcpy(chunk, &large_data[i], CHUNK_SIZE);
    xQueueSend(chunk_queue, chunk, portMAX_DELAY);
}
```

### Q4: 队列满了怎么办？

**A**: 有几种处理策略：

**策略1：阻塞等待**
```c
// 等待队列有空间
xQueueSend(queue, &data, portMAX_DELAY);
```

**策略2：超时放弃**
```c
// 等待一段时间，超时则放弃
if(xQueueSend(queue, &data, pdMS_TO_TICKS(1000)) != pdTRUE) {
    printf("Queue full, data discarded\n");
    // 记录丢失的数据
}
```

**策略3：覆盖旧数据**
```c
// 使用xQueueOverwrite（仅适用于长度为1的队列）
xQueueOverwrite(queue, &data);
```

**策略4：动态调整**
```c
// 检查队列状态，动态调整发送速度
UBaseType_t available = uxQueueSpacesAvailable(queue);
if(available < 2) {
    printf("Queue almost full, slowing down\n");
    vTaskDelay(pdMS_TO_TICKS(100));
}
```

### Q5: 如何确保数据的顺序？

**A**: 队列天然保证FIFO顺序：

**单发送者-单接收者**：
```c
// 发送顺序：1, 2, 3
xQueueSend(queue, &data1, 0);
xQueueSend(queue, &data2, 0);
xQueueSend(queue, &data3, 0);

// 接收顺序：1, 2, 3（保证顺序）
xQueueReceive(queue, &recv1, portMAX_DELAY);
xQueueReceive(queue, &recv2, portMAX_DELAY);
xQueueReceive(queue, &recv3, portMAX_DELAY);
```

**多发送者-单接收者**：
```c
// 任务A发送：1, 2
// 任务B发送：3, 4
// 接收顺序可能是：1, 3, 2, 4（取决于任务调度）
// 但每个任务的数据顺序保持不变
```

**需要严格顺序时**：
```c
// 在数据中添加序号
typedef struct {
    uint32_t sequence;
    uint32_t data;
} OrderedData_t;

// 发送时添加序号
OrderedData_t item;
item.sequence = seq_number++;
item.data = value;
xQueueSend(queue, &item, 0);

// 接收时检查序号
OrderedData_t received;
xQueueReceive(queue, &received, portMAX_DELAY);
if(received.sequence != expected_seq) {
    printf("Sequence error!\n");
}
```

### Q6: 队列的性能开销有多大？

**A**: 性能开销分析：

**时间开销**：
- 发送/接收操作：约20-50个CPU周期
- 数据复制：取决于消息大小
- 任务切换（如果阻塞）：约100-500个CPU周期

**内存开销**：
- 队列控制块：约80-120字节
- 消息存储：队列长度 × 消息大小
- 总内存 = 控制块 + (长度 × 消息大小)

**示例计算**：
```c
// 队列：长度10，消息大小16字节
// 内存占用 ≈ 100 + (10 × 16) = 260字节

// 队列：长度100，消息大小4字节
// 内存占用 ≈ 100 + (100 × 4) = 500字节
```

**优化建议**：
- 传递小数据：直接传递值
- 传递大数据：传递指针
- 合理设置队列长度
- 避免频繁的阻塞操作


## 总结

### 核心要点

1. **消息队列概念**
   - 用于任务间数据传递的FIFO结构
   - 可以存储多个消息
   - 支持阻塞和超时机制

2. **基本操作**
   - `xQueueCreate()`：创建队列
   - `xQueueSend()`：发送消息
   - `xQueueReceive()`：接收消息
   - `xQueueSendFromISR()`：中断中发送

3. **主要应用**
   - 任务间数据传递
   - 中断与任务通信
   - 生产者-消费者模式
   - 数据流水线处理

4. **最佳实践**
   - 根据需求选择合适的队列大小
   - 传递大数据时使用指针
   - 使用超时避免永久阻塞
   - 中断中使用FromISR版本API
   - 合理处理队列满和队列空的情况

### 学习检查

完成本教程后，你应该能够：

- [ ] 理解消息队列的工作原理
- [ ] 创建和管理消息队列
- [ ] 使用队列实现任务间数据传递
- [ ] 传递不同类型的数据（基本类型、结构体、指针）
- [ ] 理解和使用阻塞机制
- [ ] 处理队列满和队列空的情况
- [ ] 在中断中正确使用队列
- [ ] 应用队列解决实际问题

### 实践建议

1. **动手实践**
   - 在开发板上运行本教程的所有示例
   - 修改队列大小，观察不同的行为
   - 尝试传递不同类型的数据

2. **深入学习**
   - 学习事件标志组和其他通信机制
   - 了解任务间通信方式的对比
   - 研究队列集(Queue Set)的使用

3. **项目应用**
   - 在实际项目中使用队列
   - 设计合理的任务通信方案
   - 优化系统性能和内存使用


## 下一步

### 推荐学习路径

1. **事件标志组应用**
   - 学习事件标志组的概念
   - 掌握多事件同步方法
   - 理解位操作和等待机制
   - 参考：[事件标志组应用](07-event-group.html)

2. **RTOS软件定时器使用**
   - 学习软件定时器的创建和使用
   - 掌握单次和周期定时
   - 理解定时器回调函数
   - 参考：[RTOS软件定时器使用](08-rtos-timer.html)

3. **任务间通信方式对比**
   - 对比不同通信机制的特点
   - 学习如何选择合适的方式
   - 掌握性能优化技巧
   - 参考：[任务间通信方式对比](../intermediate/02-ipc-comparison.html)

4. **RTOS内存管理策略**
   - 学习FreeRTOS的内存管理方案
   - 掌握内存池和堆管理
   - 理解内存碎片问题
   - 参考：[RTOS内存管理策略](../intermediate/01-rtos-memory.html)

### 进阶主题

- **队列集(Queue Set)**：同时等待多个队列
- **邮箱(Mailbox)**：长度为1的队列，用于最新值传递
- **流缓冲区(Stream Buffer)**：字节流传输
- **消息缓冲区(Message Buffer)**：变长消息传输

### 实践项目

尝试以下项目来巩固所学知识：

1. **多传感器数据采集系统**
   - 使用队列收集多个传感器的数据
   - 实现数据缓冲和批处理
   - 支持数据记录和实时显示

2. **串口命令解析器**
   - 使用队列缓存串口接收的数据
   - 实现命令解析和执行
   - 支持多种命令和参数

3. **数据处理流水线**
   - 实现多阶段数据处理
   - 使用队列连接各个处理阶段
   - 优化流水线性能和吞吐量

## 参考资料

### 官方文档

- [FreeRTOS官方文档](https://www.freertos.org/Documentation/RTOS_book.html)
- [FreeRTOS API参考](https://www.freertos.org/a00106.html)
- [队列API文档](https://www.freertos.org/a00018.html)

### 推荐阅读

- 《FreeRTOS实时内核实用指南》
- 《嵌入式实时操作系统》
- 《RTOS任务间通信机制详解》

### 在线资源

- [FreeRTOS官方示例](https://www.freertos.org/FreeRTOS-quick-start-guide.html)
- [STM32 FreeRTOS教程](https://www.st.com/resource/en/user_manual/dm00105262.pdf)
- [队列使用最佳实践](https://www.freertos.org/Embedded-RTOS-Queues.html)

### 相关内容

- [RTOS任务管理基础](02-rtos-task-management.html)
- [信号量使用实战](04-semaphore.html)
- [互斥量与临界区保护](05-mutex.html)
- [事件标志组应用](07-event-group.html)
- [任务间通信方式对比](../intermediate/02-ipc-comparison.html)

---

**版权声明**: 本文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**反馈与建议**: 如有问题或建议，请通过平台反馈系统联系我们。

**最后更新**: 2024-01-15
