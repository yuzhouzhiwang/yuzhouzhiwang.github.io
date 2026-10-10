---
title: "信号量(Semaphore)使用实战：掌握RTOS任务同步机制"
description: "深入学习RTOS信号量的核心概念和实践应用。掌握二值信号量、计数信号量的使用方法，理解信号量在任务同步和资源管理中的作用，通过丰富的代码示例学会构建可靠的多任务同步系统。"
slug: "semaphore"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 信号量
  - 同步机制
  - 资源管理
  - 任务通信
  - FreeRTOS
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/05-mutex.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/06-message-queue.md"
  - "03-operating-system-layer/02-rtos-fundamentals/intermediate/02-ipc-comparison.md"

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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - RTOS信号量
  - 二值信号量
  - 计数信号量
  - 任务同步
  - 资源管理
  - FreeRTOS信号量
cover_image: ""
---


# 信号量(Semaphore)使用实战：掌握RTOS任务同步机制

## 学习目标

完成本教程后，你将能够：

- 理解信号量的概念和工作原理
- 掌握二值信号量和计数信号量的区别
- 学会使用信号量实现任务同步
- 掌握信号量在资源管理中的应用
- 理解信号量的使用场景和最佳实践
- 能够解决常见的信号量使用问题


## 前置要求

### 知识要求

- 理解RTOS的基本概念
- 掌握任务创建和管理
- 了解任务调度机制
- 熟悉C语言编程

### 技能要求

- 能够创建和管理RTOS任务
- 了解任务状态和状态转换
- 理解任务优先级的作用

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
#define configUSE_COUNTING_SEMAPHORES       1  // 启用计数信号量
#define configUSE_MUTEXES                   1  // 启用互斥量
#define configMAX_PRIORITIES                5  // 最大优先级数
#define configTICK_RATE_HZ                  1000  // 时钟节拍频率
```


## 概述

### 什么是信号量？

**信号量(Semaphore)**是RTOS中用于任务同步和资源管理的重要机制。它本质上是一个计数器，用于控制对共享资源的访问。

**生活中的类比**：

想象一个停车场：
- 停车场有10个车位（信号量初始值=10）
- 每进入一辆车，可用车位减1（获取信号量）
- 每离开一辆车，可用车位加1（释放信号量）
- 当车位满时，新车必须等待（任务阻塞）

### 为什么需要信号量？

在多任务系统中，经常遇到以下问题：

**问题1：任务同步**
```c
// 任务A：采集传感器数据
void SensorTask(void *param) {
    while(1) {
        ReadSensor();  // 读取数据
        // 如何通知任务B数据已准备好？
    }
}

// 任务B：处理数据
void ProcessTask(void *param) {
    while(1) {
        // 如何等待任务A的数据？
        ProcessData();
    }
}
```

**问题2：资源管理**
```c
// 多个任务访问同一个串口
void Task1(void *param) {
    while(1) {
        UART_Send("Task1\n");  // 可能与Task2冲突
    }
}

void Task2(void *param) {
    while(1) {
        UART_Send("Task2\n");  // 可能与Task1冲突
    }
}
```

信号量可以优雅地解决这些问题。

### 信号量的类型

RTOS中主要有两种信号量：

1. **二值信号量(Binary Semaphore)**
   - 值只能是0或1
   - 类似于开关：开(1)或关(0)
   - 用于任务同步和事件通知

2. **计数信号量(Counting Semaphore)**
   - 值可以是0到N的任意整数
   - 类似于计数器
   - 用于资源管理和限流控制


## 步骤1：理解二值信号量

### 1.1 二值信号量的概念

**二值信号量(Binary Semaphore)**的值只能是0或1：
- **0**：信号量不可用，任务获取时会阻塞
- **1**：信号量可用，任务可以获取

**工作原理**：

```
初始状态：信号量 = 0

任务A调用Give()：信号量 = 1（释放信号量）
任务B调用Take()：信号量 = 0（获取信号量，成功）
任务C调用Take()：阻塞等待（信号量为0）
任务A调用Give()：信号量 = 1（释放信号量）
任务C被唤醒：信号量 = 0（获取信号量，成功）
```

### 1.2 创建二值信号量

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 声明信号量句柄
SemaphoreHandle_t binary_sem;

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 创建二值信号量
    binary_sem = xSemaphoreCreateBinary();
    
    if(binary_sem != NULL) {
        printf("Binary semaphore created successfully\n");
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    } else {
        printf("Failed to create binary semaphore\n");
    }
    
    while(1);
}
```

**代码说明**：
- `xSemaphoreCreateBinary()`：创建二值信号量
- 返回值：信号量句柄，失败返回NULL
- 初始状态：信号量值为0（不可用）

### 1.3 使用二值信号量

#### 释放信号量（Give）

```c
// 在任务中释放信号量
BaseType_t xSemaphoreGive(SemaphoreHandle_t xSemaphore);

// 在中断中释放信号量
BaseType_t xSemaphoreGiveFromISR(
    SemaphoreHandle_t xSemaphore,
    BaseType_t *pxHigherPriorityTaskWoken
);
```

#### 获取信号量（Take）

```c
// 获取信号量（带超时）
BaseType_t xSemaphoreTake(
    SemaphoreHandle_t xSemaphore,
    TickType_t xTicksToWait  // 等待时间
);

// 参数说明：
// xTicksToWait = 0：不等待，立即返回
// xTicksToWait = portMAX_DELAY：永久等待
// xTicksToWait = pdMS_TO_TICKS(1000)：等待1000ms
```

### 1.4 完整示例：中断与任务同步

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 信号量句柄
SemaphoreHandle_t button_sem;

// 按键中断服务函数
void EXTI0_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 清除中断标志
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 释放信号量，通知任务
        xSemaphoreGiveFromISR(button_sem, &xHigherPriorityTaskWoken);
        
        // 如果唤醒了更高优先级的任务，触发任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 按键处理任务
void ButtonTask(void *param) {
    while(1) {
        // 等待信号量（永久等待）
        if(xSemaphoreTake(button_sem, portMAX_DELAY) == pdTRUE) {
            printf("Button pressed!\n");
            
            // 处理按键事件
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            
            // 防抖延时
            vTaskDelay(pdMS_TO_TICKS(200));
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 配置按键GPIO和中断
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿触发
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 使能中断
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 创建二值信号量
    button_sem = xSemaphoreCreateBinary();
    
    // 创建任务
    xTaskCreate(ButtonTask, "Button", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**代码说明**：
- 按键按下时，中断服务函数释放信号量
- 任务等待信号量，收到信号后处理按键事件
- 使用`xSemaphoreGiveFromISR()`在中断中释放信号量
- 使用`portYIELD_FROM_ISR()`触发任务切换

**运行结果**：
```
Button pressed!
Button pressed!
Button pressed!
```


## 步骤2：理解计数信号量

### 2.1 计数信号量的概念

**计数信号量(Counting Semaphore)**的值可以是0到N的任意整数：
- **0**：没有可用资源，任务获取时会阻塞
- **N**：有N个可用资源

**工作原理**：

```
初始状态：信号量 = 3（有3个资源）

任务A调用Take()：信号量 = 2（获取1个资源）
任务B调用Take()：信号量 = 1（获取1个资源）
任务C调用Take()：信号量 = 0（获取1个资源）
任务D调用Take()：阻塞等待（没有可用资源）
任务A调用Give()：信号量 = 1（释放1个资源）
任务D被唤醒：信号量 = 0（获取1个资源）
```

### 2.2 创建计数信号量

```c
// 创建计数信号量
SemaphoreHandle_t xSemaphoreCreateCounting(
    UBaseType_t uxMaxCount,      // 最大计数值
    UBaseType_t uxInitialCount   // 初始计数值
);

// 示例
SemaphoreHandle_t counting_sem;

// 创建最大值为5，初始值为3的计数信号量
counting_sem = xSemaphoreCreateCounting(5, 3);

if(counting_sem != NULL) {
    printf("Counting semaphore created\n");
    printf("Max count: 5, Initial count: 3\n");
}
```

**参数说明**：
- `uxMaxCount`：信号量的最大值（资源总数）
- `uxInitialCount`：信号量的初始值（初始可用资源数）
- 返回值：信号量句柄，失败返回NULL

### 2.3 使用计数信号量

计数信号量的使用方法与二值信号量相同：

```c
// 获取信号量（消耗一个资源）
xSemaphoreTake(counting_sem, pdMS_TO_TICKS(1000));

// 释放信号量（归还一个资源）
xSemaphoreGive(counting_sem);
```

### 2.4 完整示例：资源池管理

模拟一个有3个缓冲区的资源池：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 计数信号量句柄
SemaphoreHandle_t buffer_sem;

// 缓冲区数组
#define BUFFER_COUNT 3
uint8_t buffers[BUFFER_COUNT][256];
uint8_t buffer_used[BUFFER_COUNT] = {0};

// 分配缓冲区
uint8_t* AllocateBuffer(void) {
    // 尝试获取信号量（等待1秒）
    if(xSemaphoreTake(buffer_sem, pdMS_TO_TICKS(1000)) == pdTRUE) {
        // 查找空闲缓冲区
        for(int i = 0; i < BUFFER_COUNT; i++) {
            if(buffer_used[i] == 0) {
                buffer_used[i] = 1;
                printf("Buffer %d allocated\n", i);
                return buffers[i];
            }
        }
    }
    
    printf("No buffer available\n");
    return NULL;
}

// 释放缓冲区
void FreeBuffer(uint8_t *buffer) {
    // 查找缓冲区索引
    for(int i = 0; i < BUFFER_COUNT; i++) {
        if(buffers[i] == buffer) {
            buffer_used[i] = 0;
            printf("Buffer %d freed\n", i);
            
            // 释放信号量
            xSemaphoreGive(buffer_sem);
            return;
        }
    }
}

// 生产者任务
void ProducerTask(void *param) {
    uint32_t task_id = (uint32_t)param;
    
    while(1) {
        printf("[Producer %d] Requesting buffer...\n", task_id);
        
        // 分配缓冲区
        uint8_t *buffer = AllocateBuffer();
        
        if(buffer != NULL) {
            // 使用缓冲区（模拟数据处理）
            printf("[Producer %d] Using buffer\n", task_id);
            vTaskDelay(pdMS_TO_TICKS(2000));
            
            // 释放缓冲区
            FreeBuffer(buffer);
            printf("[Producer %d] Buffer released\n", task_id);
        }
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建计数信号量（3个缓冲区，初始全部可用）
    buffer_sem = xSemaphoreCreateCounting(BUFFER_COUNT, BUFFER_COUNT);
    
    if(buffer_sem != NULL) {
        printf("Buffer pool created: %d buffers\n", BUFFER_COUNT);
        
        // 创建4个生产者任务（竞争3个缓冲区）
        xTaskCreate(ProducerTask, "Producer1", 256, (void *)1, 2, NULL);
        xTaskCreate(ProducerTask, "Producer2", 256, (void *)2, 2, NULL);
        xTaskCreate(ProducerTask, "Producer3", 256, (void *)3, 2, NULL);
        xTaskCreate(ProducerTask, "Producer4", 256, (void *)4, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**代码说明**：
- 创建3个缓冲区的资源池
- 使用计数信号量管理缓冲区的分配和释放
- 4个任务竞争3个缓冲区
- 当缓冲区用完时，任务会阻塞等待

**运行结果**：
```
Buffer pool created: 3 buffers
[Producer 1] Requesting buffer...
Buffer 0 allocated
[Producer 1] Using buffer
[Producer 2] Requesting buffer...
Buffer 1 allocated
[Producer 2] Using buffer
[Producer 3] Requesting buffer...
Buffer 2 allocated
[Producer 3] Using buffer
[Producer 4] Requesting buffer...
No buffer available  ← 第4个任务等待
[Producer 1] Buffer released
Buffer 0 freed
[Producer 4] Requesting buffer...
Buffer 0 allocated  ← 获得释放的缓冲区
```


## 步骤3：任务同步应用

### 3.1 生产者-消费者模式

使用信号量实现经典的生产者-消费者模式：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 信号量句柄
SemaphoreHandle_t data_ready_sem;  // 数据就绪信号

// 共享数据
#define BUFFER_SIZE 10
uint32_t data_buffer[BUFFER_SIZE];
uint32_t write_index = 0;
uint32_t read_index = 0;

// 生产者任务
void ProducerTask(void *param) {
    uint32_t data = 0;
    
    while(1) {
        // 生产数据
        data++;
        data_buffer[write_index] = data;
        write_index = (write_index + 1) % BUFFER_SIZE;
        
        printf("[Producer] Produced data: %d\n", data);
        
        // 释放信号量，通知消费者
        xSemaphoreGive(data_ready_sem);
        
        // 延时模拟生产过程
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 消费者任务
void ConsumerTask(void *param) {
    uint32_t data;
    
    while(1) {
        // 等待数据就绪信号
        if(xSemaphoreTake(data_ready_sem, portMAX_DELAY) == pdTRUE) {
            // 消费数据
            data = data_buffer[read_index];
            read_index = (read_index + 1) % BUFFER_SIZE;
            
            printf("[Consumer] Consumed data: %d\n", data);
            
            // 延时模拟消费过程
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建二值信号量（初始值为0）
    data_ready_sem = xSemaphoreCreateBinary();
    
    // 创建任务
    xTaskCreate(ProducerTask, "Producer", 256, NULL, 2, NULL);
    xTaskCreate(ConsumerTask, "Consumer", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Producer] Produced data: 1
[Consumer] Consumed data: 1
[Producer] Produced data: 2
[Producer] Produced data: 3
[Consumer] Consumed data: 2
[Producer] Produced data: 4
[Consumer] Consumed data: 3
```

### 3.2 多任务协作

使用信号量实现多个任务的协作：

```c
// 信号量句柄
SemaphoreHandle_t task1_sem;
SemaphoreHandle_t task2_sem;
SemaphoreHandle_t task3_sem;

// 任务1：数据采集
void Task1_DataAcquisition(void *param) {
    while(1) {
        printf("[Task1] Acquiring data...\n");
        
        // 模拟数据采集
        vTaskDelay(pdMS_TO_TICKS(100));
        
        printf("[Task1] Data acquired\n");
        
        // 通知任务2开始处理
        xSemaphoreGive(task2_sem);
        
        // 等待任务3完成
        xSemaphoreTake(task1_sem, portMAX_DELAY);
    }
}

// 任务2：数据处理
void Task2_DataProcessing(void *param) {
    while(1) {
        // 等待任务1的数据
        xSemaphoreTake(task2_sem, portMAX_DELAY);
        
        printf("[Task2] Processing data...\n");
        
        // 模拟数据处理
        vTaskDelay(pdMS_TO_TICKS(200));
        
        printf("[Task2] Data processed\n");
        
        // 通知任务3开始显示
        xSemaphoreGive(task3_sem);
    }
}

// 任务3：数据显示
void Task3_DataDisplay(void *param) {
    while(1) {
        // 等待任务2的处理结果
        xSemaphoreTake(task3_sem, portMAX_DELAY);
        
        printf("[Task3] Displaying data...\n");
        
        // 模拟数据显示
        vTaskDelay(pdMS_TO_TICKS(150));
        
        printf("[Task3] Data displayed\n\n");
        
        // 通知任务1开始下一轮
        xSemaphoreGive(task1_sem);
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建信号量
    task1_sem = xSemaphoreCreateBinary();
    task2_sem = xSemaphoreCreateBinary();
    task3_sem = xSemaphoreCreateBinary();
    
    // 给task1_sem一个初始信号，启动流程
    xSemaphoreGive(task1_sem);
    
    // 创建任务
    xTaskCreate(Task1_DataAcquisition, "Task1", 256, NULL, 2, NULL);
    xTaskCreate(Task2_DataProcessing, "Task2", 256, NULL, 2, NULL);
    xTaskCreate(Task3_DataDisplay, "Task3", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Task1] Acquiring data...
[Task1] Data acquired
[Task2] Processing data...
[Task2] Data processed
[Task3] Displaying data...
[Task3] Data displayed

[Task1] Acquiring data...
[Task1] Data acquired
[Task2] Processing data...
[Task2] Data processed
[Task3] Displaying data...
[Task3] Data displayed
```

**代码说明**：
- 三个任务按照固定顺序执行：采集→处理→显示
- 使用信号量实现任务间的同步
- 形成一个完整的数据处理流水线


## 步骤4：资源管理应用

### 4.1 限制并发访问

使用计数信号量限制同时访问资源的任务数量：

```c
// 限制最多3个任务同时访问资源
#define MAX_CONCURRENT_ACCESS 3

SemaphoreHandle_t resource_sem;

// 访问共享资源的任务
void ResourceAccessTask(void *param) {
    uint32_t task_id = (uint32_t)param;
    
    while(1) {
        printf("[Task %d] Requesting resource access...\n", task_id);
        
        // 获取访问权限
        if(xSemaphoreTake(resource_sem, pdMS_TO_TICKS(5000)) == pdTRUE) {
            printf("[Task %d] Accessing resource\n", task_id);
            
            // 使用资源（模拟耗时操作）
            vTaskDelay(pdMS_TO_TICKS(2000));
            
            printf("[Task %d] Resource access complete\n", task_id);
            
            // 释放访问权限
            xSemaphoreGive(resource_sem);
        } else {
            printf("[Task %d] Timeout waiting for resource\n", task_id);
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建计数信号量（最多3个任务同时访问）
    resource_sem = xSemaphoreCreateCounting(
        MAX_CONCURRENT_ACCESS,  // 最大值
        MAX_CONCURRENT_ACCESS   // 初始值
    );
    
    // 创建5个任务（竞争3个访问权限）
    for(uint32_t i = 1; i <= 5; i++) {
        xTaskCreate(ResourceAccessTask, "Task", 256, (void *)i, 2, NULL);
    }
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Task 1] Requesting resource access...
[Task 1] Accessing resource
[Task 2] Requesting resource access...
[Task 2] Accessing resource
[Task 3] Requesting resource access...
[Task 3] Accessing resource
[Task 4] Requesting resource access...  ← 等待
[Task 5] Requesting resource access...  ← 等待
[Task 1] Resource access complete
[Task 4] Accessing resource  ← 获得访问权限
```

### 4.2 事件计数

使用计数信号量统计事件发生次数：

```c
// 事件计数信号量
SemaphoreHandle_t event_counter_sem;

// 事件产生任务（中断模拟）
void EventGeneratorTask(void *param) {
    uint32_t event_count = 0;
    
    while(1) {
        // 模拟事件发生
        vTaskDelay(pdMS_TO_TICKS(500));
        
        event_count++;
        printf("[Generator] Event %d occurred\n", event_count);
        
        // 增加事件计数
        xSemaphoreGive(event_counter_sem);
    }
}

// 事件处理任务
void EventHandlerTask(void *param) {
    uint32_t handled_count = 0;
    
    while(1) {
        // 等待事件
        if(xSemaphoreTake(event_counter_sem, portMAX_DELAY) == pdTRUE) {
            handled_count++;
            printf("[Handler] Processing event %d\n", handled_count);
            
            // 处理事件（耗时操作）
            vTaskDelay(pdMS_TO_TICKS(1000));
            
            printf("[Handler] Event %d processed\n", handled_count);
        }
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建计数信号量（最大值10，初始值0）
    event_counter_sem = xSemaphoreCreateCounting(10, 0);
    
    // 创建任务
    xTaskCreate(EventGeneratorTask, "Generator", 256, NULL, 3, NULL);
    xTaskCreate(EventHandlerTask, "Handler", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**：
```
[Generator] Event 1 occurred
[Handler] Processing event 1
[Generator] Event 2 occurred
[Generator] Event 3 occurred
[Handler] Event 1 processed
[Handler] Processing event 2
[Generator] Event 4 occurred
[Handler] Event 2 processed
[Handler] Processing event 3
```

**代码说明**：
- 事件产生速度快于处理速度
- 计数信号量累积未处理的事件
- 处理任务按顺序处理所有事件


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
   - 观察任务执行和信号量操作的输出

### 预期结果

**二值信号量示例**：
- 按键按下时，任务立即响应
- 串口输出"Button pressed!"
- LED状态切换

**计数信号量示例**：
- 最多3个任务同时使用缓冲区
- 第4个任务等待缓冲区释放
- 缓冲区正确分配和释放

**任务同步示例**：
- 任务按照固定顺序执行
- 数据采集→处理→显示
- 形成完整的处理流水线

### 测试要点

1. **功能测试**
   - [ ] 信号量创建成功
   - [ ] 任务能够获取和释放信号量
   - [ ] 任务同步工作正常
   - [ ] 资源管理正确

2. **边界测试**
   - [ ] 信号量值为0时，任务正确阻塞
   - [ ] 信号量达到最大值时，Give操作正确处理
   - [ ] 超时机制工作正常

3. **性能测试**
   - [ ] 信号量操作响应及时
   - [ ] 任务切换流畅
   - [ ] 无死锁或饥饿现象


## 故障排除

### 问题1：信号量创建失败

**现象**：
```c
binary_sem = xSemaphoreCreateBinary();
if(binary_sem == NULL) {
    printf("Failed to create semaphore\n");
}
```

**可能原因**：
1. 堆内存不足
2. FreeRTOS配置错误
3. 未启用信号量功能

**解决方法**：

```c
// 1. 增加堆大小（FreeRTOSConfig.h）
#define configTOTAL_HEAP_SIZE  ((size_t)(20 * 1024))  // 增加到20KB

// 2. 启用信号量功能
#define configUSE_COUNTING_SEMAPHORES  1

// 3. 检查剩余堆空间
size_t free_heap = xPortGetFreeHeapSize();
printf("Free heap: %d bytes\n", free_heap);
```

### 问题2：任务永久阻塞

**现象**：
```c
// 任务一直等待，永不返回
xSemaphoreTake(sem, portMAX_DELAY);
printf("This never prints\n");
```

**可能原因**：
1. 没有任务释放信号量
2. 信号量初始值为0且无人Give
3. 死锁情况

**解决方法**：

```c
// 1. 使用超时等待，避免永久阻塞
if(xSemaphoreTake(sem, pdMS_TO_TICKS(5000)) == pdTRUE) {
    // 成功获取
} else {
    printf("Timeout waiting for semaphore\n");
}

// 2. 检查是否有任务释放信号量
// 3. 添加调试输出，跟踪信号量状态
printf("Waiting for semaphore...\n");
xSemaphoreTake(sem, portMAX_DELAY);
printf("Semaphore acquired\n");
```

### 问题3：中断中使用错误的API

**现象**：
```c
// 在中断中使用普通API（错误）
void EXTI_IRQHandler(void) {
    xSemaphoreGive(sem);  // ❌ 错误！
}
```

**解决方法**：

```c
// 在中断中必须使用FromISR版本的API
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // ✅ 正确：使用FromISR版本
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 问题4：信号量值溢出

**现象**：
```c
// 计数信号量超过最大值
for(int i = 0; i < 10; i++) {
    xSemaphoreGive(counting_sem);  // 可能超过最大值
}
```

**解决方法**：

```c
// 1. 创建时设置合适的最大值
counting_sem = xSemaphoreCreateCounting(10, 0);

// 2. Give前检查是否会溢出
UBaseType_t count = uxSemaphoreGetCount(counting_sem);
if(count < MAX_COUNT) {
    xSemaphoreGive(counting_sem);
} else {
    printf("Semaphore at maximum value\n");
}
```

### 问题5：优先级反转

**现象**：
- 高优先级任务等待低优先级任务释放信号量
- 中优先级任务抢占低优先级任务
- 导致高优先级任务长时间等待

**解决方法**：

```c
// 使用互斥量代替信号量（互斥量支持优先级继承）
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

// 或者调整任务优先级，避免优先级反转
```

详细内容请参考：[互斥量与临界区保护](05-mutex.html)


## 常见问题

### Q1: 二值信号量和互斥量有什么区别？

**A**: 主要区别：

| 特性 | 二值信号量 | 互斥量 |
|------|-----------|--------|
| **用途** | 任务同步、事件通知 | 资源互斥访问 |
| **所有权** | 无所有权概念 | 有所有权，谁获取谁释放 |
| **优先级继承** | 不支持 | 支持，防止优先级反转 |
| **递归获取** | 不支持 | 支持递归互斥量 |
| **中断使用** | 可以在中断中Give | 不能在中断中使用 |

**使用建议**：
- 任务同步 → 使用二值信号量
- 资源保护 → 使用互斥量

### Q2: 什么时候使用二值信号量，什么时候使用计数信号量？

**A**: 选择依据：

**二值信号量**：
- 事件通知（中断→任务）
- 简单的任务同步
- 只有"有"和"无"两种状态

**计数信号量**：
- 管理多个相同资源
- 限制并发访问数量
- 事件计数
- 需要跟踪资源数量

**示例**：
```c
// 二值信号量：按键事件通知
binary_sem = xSemaphoreCreateBinary();

// 计数信号量：管理3个缓冲区
counting_sem = xSemaphoreCreateCounting(3, 3);
```

### Q3: 信号量的初始值应该设置为多少？

**A**: 根据使用场景决定：

**二值信号量**：
```c
// 场景1：事件通知（初始值=0）
binary_sem = xSemaphoreCreateBinary();  // 初始值0
// 等待事件发生后才能获取

// 场景2：资源可用（初始值=1）
binary_sem = xSemaphoreCreateBinary();
xSemaphoreGive(binary_sem);  // 手动设置为1
// 资源初始可用
```

**计数信号量**：
```c
// 场景1：资源池（初始值=资源总数）
counting_sem = xSemaphoreCreateCounting(5, 5);
// 5个资源全部可用

// 场景2：事件计数（初始值=0）
counting_sem = xSemaphoreCreateCounting(10, 0);
// 等待事件发生
```

### Q4: 如何避免信号量导致的死锁？

**A**: 死锁预防策略：

1. **使用超时机制**
```c
// ❌ 可能死锁
xSemaphoreTake(sem, portMAX_DELAY);

// ✅ 使用超时
if(xSemaphoreTake(sem, pdMS_TO_TICKS(5000)) != pdTRUE) {
    printf("Timeout, avoiding deadlock\n");
    // 错误处理
}
```

2. **固定获取顺序**
```c
// 多个信号量时，按固定顺序获取
xSemaphoreTake(sem1, timeout);
xSemaphoreTake(sem2, timeout);
// 使用资源
xSemaphoreGive(sem2);
xSemaphoreGive(sem1);
```

3. **避免嵌套获取**
```c
// ❌ 避免这种情况
xSemaphoreTake(sem1, portMAX_DELAY);
xSemaphoreTake(sem2, portMAX_DELAY);  // 可能死锁
```

### Q5: 信号量和队列有什么区别？

**A**: 主要区别：

| 特性 | 信号量 | 队列 |
|------|--------|------|
| **数据传递** | 不传递数据 | 传递数据 |
| **用途** | 同步和计数 | 数据通信 |
| **大小** | 只有计数值 | 可以存储多个数据 |
| **开销** | 小 | 较大 |

**选择建议**：
- 只需要通知 → 使用信号量
- 需要传递数据 → 使用队列

```c
// 信号量：只通知事件发生
xSemaphoreGive(event_sem);

// 队列：传递具体数据
SensorData_t data = {.temp = 25.5, .humidity = 60};
xQueueSend(data_queue, &data, 0);
```

### Q6: 如何查看信号量的当前值？

**A**: 使用`uxSemaphoreGetCount()`：

```c
// 获取信号量当前值
UBaseType_t count = uxSemaphoreGetCount(counting_sem);
printf("Semaphore count: %d\n", count);

// 示例：检查资源可用性
if(uxSemaphoreGetCount(resource_sem) > 0) {
    printf("Resources available\n");
} else {
    printf("No resources available\n");
}
```

**注意**：
- 二值信号量：返回0或1
- 计数信号量：返回0到最大值
- 此函数不会阻塞任务


## 总结

### 核心要点

1. **信号量类型**
   - 二值信号量：值为0或1，用于任务同步
   - 计数信号量：值为0到N，用于资源管理

2. **基本操作**
   - `xSemaphoreGive()`：释放信号量（值+1）
   - `xSemaphoreTake()`：获取信号量（值-1）
   - 中断中使用`FromISR`版本

3. **主要应用**
   - 任务同步：生产者-消费者模式
   - 事件通知：中断→任务通信
   - 资源管理：限制并发访问
   - 事件计数：统计事件次数

4. **最佳实践**
   - 使用超时避免永久阻塞
   - 中断中使用FromISR版本API
   - 根据场景选择合适的信号量类型
   - 注意优先级反转问题

### 学习检查

完成本教程后，你应该能够：

- [ ] 理解信号量的工作原理
- [ ] 创建和使用二值信号量
- [ ] 创建和使用计数信号量
- [ ] 实现任务间的同步
- [ ] 使用信号量管理资源
- [ ] 处理常见的信号量问题
- [ ] 选择合适的同步机制

### 实践建议

1. **动手实践**
   - 在开发板上运行本教程的所有示例
   - 修改参数，观察不同的行为
   - 尝试组合多个信号量

2. **深入学习**
   - 学习互斥量和临界区保护
   - 了解消息队列和事件标志组
   - 研究任务间通信的最佳实践

3. **项目应用**
   - 在实际项目中使用信号量
   - 设计合理的任务同步方案
   - 优化系统性能和响应时间


## 下一步

### 推荐学习路径

1. **互斥量与临界区保护**
   - 学习互斥量的使用
   - 理解优先级继承机制
   - 掌握临界区保护方法
   - 参考：[互斥量与临界区保护](05-mutex.html)

2. **消息队列通信机制**
   - 学习队列的创建和使用
   - 掌握任务间数据传递
   - 理解队列的阻塞机制
   - 参考：[消息队列通信机制](06-message-queue.html)

3. **事件标志组应用**
   - 学习事件标志组的概念
   - 掌握多事件同步方法
   - 理解位操作和等待机制
   - 参考：[事件标志组应用](07-event-group.html)

4. **任务间通信方式对比**
   - 对比不同通信机制的特点
   - 学习如何选择合适的方式
   - 掌握性能优化技巧
   - 参考：[任务间通信方式对比](../intermediate/02-ipc-comparison.html)

### 进阶主题

- **优先级反转问题与解决**：深入理解优先级反转及其解决方案
- **RTOS中断管理与延迟处理**：学习中断与RTOS的配合使用
- **实时性分析与调度可行性**：掌握实时系统的分析方法

### 实践项目

尝试以下项目来巩固所学知识：

1. **多传感器数据采集系统**
   - 使用信号量同步多个传感器任务
   - 实现数据采集、处理和显示流水线
   - 管理有限的缓冲区资源

2. **按键消抖与事件处理**
   - 使用中断和信号量处理按键
   - 实现可靠的按键消抖
   - 支持多个按键的独立处理

3. **资源池管理系统**
   - 使用计数信号量管理资源池
   - 实现资源的分配和回收
   - 支持超时和错误处理

## 参考资料

### 官方文档

- [FreeRTOS官方文档](https://www.freertos.org/Documentation/RTOS_book.html)
- [FreeRTOS API参考](https://www.freertos.org/a00106.html)
- [信号量API文档](https://www.freertos.org/a00113.html)

### 推荐阅读

- 《FreeRTOS实时内核实用指南》
- 《嵌入式实时操作系统》
- 《RTOS任务间通信机制详解》

### 在线资源

- [FreeRTOS官方示例](https://www.freertos.org/FreeRTOS-quick-start-guide.html)
- [STM32 FreeRTOS教程](https://www.st.com/resource/en/user_manual/dm00105262.pdf)
- [嵌入式系统设计模式](https://www.embedded.com/design-patterns-for-embedded-systems/)

### 相关内容

- [RTOS任务管理基础](02-rtos-task-management.html)
- [RTOS调度算法详解](03-rtos-scheduling.html)
- [互斥量与临界区保护](05-mutex.html)
- [消息队列通信机制](06-message-queue.html)
- [优先级反转问题与解决](../intermediate/03-priority-inversion.html)

---

**版权声明**: 本文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**反馈与建议**: 如有问题或建议，请通过平台反馈系统联系我们。

**最后更新**: 2024-01-15
