---
title: "FreeRTOS信号量应用：掌握任务同步与资源管理的核心技术"
description: "深入学习FreeRTOS信号量机制，掌握二值信号量、计数信号量、互斥量和递归互斥量的使用方法，通过丰富的实战示例学会构建高效可靠的任务同步和资源管理系统"
slug: "freertos-semaphore"

# 分类信息
domain: "操作系统层"
module: "FreeRTOS"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - FreeRTOS信号量
  - 同步
  - 互斥
  - 二值信号量
  - 计数信号量
prerequisites:
  - "03-operating-system-layer/03-freertos/beginner/01-freertos-quickstart"
  - "03-operating-system-layer/03-freertos/beginner/02-freertos-tasks"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore"
related_contents:
  - "03-operating-system-layer/03-freertos/beginner/03-freertos-queue"
  - "03-operating-system-layer/03-freertos/beginner/05-freertos-config"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/05-mutex"

# 学习信息
estimated_time: 65
difficulty_score: 4

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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - FreeRTOS信号量
  - xSemaphoreCreateBinary
  - xSemaphoreCreateCounting
  - xSemaphoreCreateMutex
  - 任务同步
  - 资源管理
cover_image: ""
---

# FreeRTOS信号量应用：掌握任务同步与资源管理的核心技术

## 学习目标

完成本教程后，你将能够：

- [ ] 理解FreeRTOS信号量的工作原理和应用场景
- [ ] 掌握二值信号量的创建和使用方法
- [ ] 熟练使用计数信号量管理多个资源
- [ ] 理解互斥量与二值信号量的区别
- [ ] 掌握递归互斥量的使用场景
- [ ] 学会在中断中使用信号量
- [ ] 能够在实际项目中应用信号量解决同步问题

## 前置要求

在开始本教程之前，你需要：

**知识要求**:
- 完成FreeRTOS快速入门和任务管理教程
- 理解RTOS任务调度和状态转换
- 了解信号量的基本概念
- 熟悉C语言指针和结构体

**技能要求**:
- 能够创建和管理FreeRTOS任务
- 会使用STM32CubeIDE或Keil MDK
- 了解如何编译和调试程序
- 理解中断的基本概念

**硬件准备**:
- STM32开发板(如STM32F4 Discovery)
- ST-Link调试器
- USB数据线
- LED灯和按键(用于演示,可选)

## 准备工作

### 环境配置

本教程基于以下环境:

**软件环境**:
- STM32CubeIDE v1.10+
- FreeRTOS V10.3.1+
- HAL库 v1.27+

**硬件环境**:
- STM32F407VGT6开发板
- 板载LED和按键
- 串口调试工具

### FreeRTOS配置

确保在`FreeRTOSConfig.h`中启用信号量相关配置:

```c
// 启用信号量功能
#define configUSE_MUTEXES                   1
#define configUSE_RECURSIVE_MUTEXES         1
#define configUSE_COUNTING_SEMAPHORES       1

// 基本配置
#define configUSE_PREEMPTION                1
#define configTICK_RATE_HZ                  1000
#define configMAX_PRIORITIES                5
#define configTOTAL_HEAP_SIZE               15360
```


### 创建基础项目

如果你已经完成了前面的教程,可以直接使用之前的项目。否则:

1. 打开STM32CubeIDE,创建新的STM32项目
2. 在CubeMX中启用FreeRTOS(CMSIS_V1接口)
3. 配置系统时钟和串口(用于调试输出)
4. 生成代码并打开项目

## 核心内容

### 信号量的基本概念

**什么是信号量?**

信号量(Semaphore)是FreeRTOS中用于任务同步和资源管理的核心机制。它本质上是一个计数器,用于控制对共享资源的访问或实现任务间的同步。

**FreeRTOS信号量的类型**:

1. **二值信号量(Binary Semaphore)**: 值只能是0或1,用于任务同步和事件通知
2. **计数信号量(Counting Semaphore)**: 值可以是0到N,用于管理多个相同资源
3. **互斥量(Mutex)**: 特殊的二值信号量,支持优先级继承,用于资源互斥访问
4. **递归互斥量(Recursive Mutex)**: 允许同一任务多次获取的互斥量

**生活中的类比**:

想象一个图书馆的借阅系统:
- **二值信号量**: 像一个单人阅览室的钥匙,只有一把,有人使用时其他人必须等待
- **计数信号量**: 像多个相同的图书,有10本时可以借给10个人
- **互斥量**: 像带有借阅记录的钥匙,只有借出者才能归还
- **递归互斥量**: 像允许同一人多次进入的阅览室钥匙

**信号量操作**:

```
Give (释放/发送):
- 二值信号量: 0 → 1
- 计数信号量: N → N+1 (不超过最大值)
- 互斥量: 只能由持有者释放

Take (获取/接收):
- 二值信号量: 1 → 0 (如果为0则阻塞)
- 计数信号量: N → N-1 (如果为0则阻塞)
- 互斥量: 获取所有权 (如果已被占用则阻塞)
```


## 步骤1: 二值信号量的使用

### 1.1 创建二值信号量

FreeRTOS提供了两种创建二值信号量的方法:

**动态创建 - xSemaphoreCreateBinary()**

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 声明信号量句柄
SemaphoreHandle_t xBinarySemaphore;

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建二值信号量
    xBinarySemaphore = xSemaphoreCreateBinary();
    
    if(xBinarySemaphore != NULL)
    {
        printf("Binary semaphore created successfully\n");
        
        // 创建任务...
        xTaskCreate(SenderTask, "Sender", 256, NULL, 2, NULL);
        xTaskCreate(ReceiverTask, "Receiver", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    else
    {
        printf("Failed to create binary semaphore\n");
    }
    
    while(1);
}
```

**代码说明**:
- `xSemaphoreCreateBinary()`从堆中分配内存创建信号量
- 返回值为信号量句柄,失败返回NULL
- 初始状态:信号量值为0(不可用)

**静态创建 - xSemaphoreCreateBinaryStatic()**

```c
// 静态分配信号量控制块
StaticSemaphore_t xSemaphoreBuffer;
SemaphoreHandle_t xBinarySemaphore;

// 创建静态二值信号量
xBinarySemaphore = xSemaphoreCreateBinaryStatic(&xSemaphoreBuffer);
```

**代码说明**:
- 使用静态内存,不依赖堆分配
- 需要提供`StaticSemaphore_t`类型的缓冲区
- 适合对内存分配有严格要求的场景


### 1.2 二值信号量的基本操作

**释放信号量 - xSemaphoreGive()**

```c
// 在任务中释放信号量
BaseType_t xSemaphoreGive(SemaphoreHandle_t xSemaphore);

// 返回值:
// pdTRUE: 释放成功
// pdFALSE: 释放失败

// 示例
void SenderTask(void *pvParameters)
{
    while(1)
    {
        // 执行某些操作
        printf("[Sender] Performing operation...\n");
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // 释放信号量,通知接收任务
        if(xSemaphoreGive(xBinarySemaphore) == pdTRUE)
        {
            printf("[Sender] Semaphore given\n");
        }
        else
        {
            printf("[Sender] Failed to give semaphore\n");
        }
    }
}
```

**获取信号量 - xSemaphoreTake()**

```c
// 获取信号量(带超时)
BaseType_t xSemaphoreTake(
    SemaphoreHandle_t xSemaphore,
    TickType_t xTicksToWait  // 等待时间
);

// 返回值:
// pdTRUE: 获取成功
// pdFALSE: 获取失败(超时)

// 等待时间参数:
// 0: 不等待,立即返回
// portMAX_DELAY: 永久等待
// pdMS_TO_TICKS(1000): 等待1000ms

// 示例
void ReceiverTask(void *pvParameters)
{
    while(1)
    {
        printf("[Receiver] Waiting for semaphore...\n");
        
        // 等待信号量(永久等待)
        if(xSemaphoreTake(xBinarySemaphore, portMAX_DELAY) == pdTRUE)
        {
            printf("[Receiver] Semaphore received\n");
            
            // 处理事件
            printf("[Receiver] Processing event\n");
            vTaskDelay(pdMS_TO_TICKS(500));
        }
    }
}
```

### 1.3 完整示例:中断与任务同步

使用二值信号量实现按键中断与任务的同步:

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 信号量句柄
SemaphoreHandle_t xButtonSemaphore;

// 按键中断服务函数
void EXTI0_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 清除中断标志
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 在中断中释放信号量
        xSemaphoreGiveFromISR(xButtonSemaphore, &xHigherPriorityTaskWoken);
        
        // 如果唤醒了更高优先级的任务,触发任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// 按键处理任务
void vButtonTask(void *pvParameters)
{
    uint32_t ulPressCount = 0;
    
    printf("[Button Task] Started\n");
    
    while(1)
    {
        // 等待按键信号量
        if(xSemaphoreTake(xButtonSemaphore, portMAX_DELAY) == pdTRUE)
        {
            ulPressCount++;
            printf("[Button Task] Button pressed! Count: %lu\n", ulPressCount);
            
            // 切换LED状态
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            
            // 防抖延时
            vTaskDelay(pdMS_TO_TICKS(200));
        }
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    
    printf("\n=== FreeRTOS Binary Semaphore Example ===\n\n");
    
    // 创建二值信号量
    xButtonSemaphore = xSemaphoreCreateBinary();
    
    if(xButtonSemaphore != NULL)
    {
        printf("Binary semaphore created\n\n");
        
        // 创建按键处理任务
        xTaskCreate(vButtonTask, "Button", 256, NULL, 3, NULL);
        
        // 启动调度器
        printf("Starting scheduler...\n\n");
        vTaskStartScheduler();
    }
    else
    {
        printf("Failed to create semaphore\n");
    }
    
    while(1);
}
```

**运行结果**:

```
=== FreeRTOS Binary Semaphore Example ===

Binary semaphore created

Starting scheduler...

[Button Task] Started
[Button Task] Button pressed! Count: 1
[Button Task] Button pressed! Count: 2
[Button Task] Button pressed! Count: 3
```

**代码说明**:
- 按键按下时,中断服务函数释放信号量
- 任务等待信号量,收到信号后处理按键事件
- 使用`xSemaphoreGiveFromISR()`在中断中释放信号量
- 使用`portYIELD_FROM_ISR()`触发任务切换,提高响应速度



## 步骤2: 计数信号量的使用

### 2.1 创建计数信号量

**动态创建 - xSemaphoreCreateCounting()**

```c
// 创建计数信号量
SemaphoreHandle_t xSemaphoreCreateCounting(
    UBaseType_t uxMaxCount,      // 最大计数值
    UBaseType_t uxInitialCount   // 初始计数值
);

// 示例
SemaphoreHandle_t xCountingSemaphore;

// 创建最大值为5,初始值为3的计数信号量
xCountingSemaphore = xSemaphoreCreateCounting(5, 3);

if(xCountingSemaphore != NULL)
{
    printf("Counting semaphore created\n");
    printf("Max count: 5, Initial count: 3\n");
}
```

**参数说明**:
- `uxMaxCount`: 信号量的最大值(资源总数)
- `uxInitialCount`: 信号量的初始值(初始可用资源数)
- 返回值: 信号量句柄,失败返回NULL

**静态创建 - xSemaphoreCreateCountingStatic()**

```c
// 静态分配信号量控制块
StaticSemaphore_t xSemaphoreBuffer;
SemaphoreHandle_t xCountingSemaphore;

// 创建静态计数信号量
xCountingSemaphore = xSemaphoreCreateCountingStatic(
    5,                    // 最大值
    3,                    // 初始值
    &xSemaphoreBuffer     // 缓冲区
);
```

### 2.2 计数信号量的应用场景

**场景1: 资源池管理**

管理有限数量的相同资源:

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 计数信号量句柄
SemaphoreHandle_t xBufferSemaphore;

// 缓冲区数组
#define BUFFER_COUNT 3
uint8_t buffers[BUFFER_COUNT][256];
uint8_t buffer_used[BUFFER_COUNT] = {0};

// 分配缓冲区
uint8_t* AllocateBuffer(void)
{
    // 尝试获取信号量(等待1秒)
    if(xSemaphoreTake(xBufferSemaphore, pdMS_TO_TICKS(1000)) == pdTRUE)
    {
        // 查找空闲缓冲区
        for(int i = 0; i < BUFFER_COUNT; i++)
        {
            if(buffer_used[i] == 0)
            {
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
void FreeBuffer(uint8_t *buffer)
{
    // 查找缓冲区索引
    for(int i = 0; i < BUFFER_COUNT; i++)
    {
        if(buffers[i] == buffer)
        {
            buffer_used[i] = 0;
            printf("Buffer %d freed\n", i);
            
            // 释放信号量
            xSemaphoreGive(xBufferSemaphore);
            return;
        }
    }
}

// 工作任务
void vWorkerTask(void *pvParameters)
{
    uint32_t ulTaskID = (uint32_t)pvParameters;
    
    while(1)
    {
        printf("[Task %lu] Requesting buffer...\n", ulTaskID);
        
        // 分配缓冲区
        uint8_t *pBuffer = AllocateBuffer();
        
        if(pBuffer != NULL)
        {
            // 使用缓冲区
            printf("[Task %lu] Using buffer\n", ulTaskID);
            sprintf((char *)pBuffer, "Data from Task %lu", ulTaskID);
            
            // 模拟处理时间
            vTaskDelay(pdMS_TO_TICKS(2000));
            
            // 释放缓冲区
            FreeBuffer(pBuffer);
            printf("[Task %lu] Buffer released\n\n", ulTaskID);
        }
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    printf("\n=== FreeRTOS Counting Semaphore Example ===\n\n");
    
    // 创建计数信号量(3个缓冲区,初始全部可用)
    xBufferSemaphore = xSemaphoreCreateCounting(BUFFER_COUNT, BUFFER_COUNT);
    
    if(xBufferSemaphore != NULL)
    {
        printf("Buffer pool created: %d buffers\n\n", BUFFER_COUNT);
        
        // 创建4个工作任务(竞争3个缓冲区)
        xTaskCreate(vWorkerTask, "Worker1", 256, (void *)1, 2, NULL);
        xTaskCreate(vWorkerTask, "Worker2", 256, (void *)2, 2, NULL);
        xTaskCreate(vWorkerTask, "Worker3", 256, (void *)3, 2, NULL);
        xTaskCreate(vWorkerTask, "Worker4", 256, (void *)4, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**:

```
=== FreeRTOS Counting Semaphore Example ===

Buffer pool created: 3 buffers

[Task 1] Requesting buffer...
Buffer 0 allocated
[Task 1] Using buffer
[Task 2] Requesting buffer...
Buffer 1 allocated
[Task 2] Using buffer
[Task 3] Requesting buffer...
Buffer 2 allocated
[Task 3] Using buffer
[Task 4] Requesting buffer...
No buffer available  ← 第4个任务等待
[Task 1] Buffer released
Buffer 0 freed

[Task 4] Requesting buffer...
Buffer 0 allocated  ← 获得释放的缓冲区
[Task 4] Using buffer
```

**代码说明**:
- 创建3个缓冲区的资源池
- 使用计数信号量管理缓冲区的分配和释放
- 4个任务竞争3个缓冲区
- 当缓冲区用完时,任务会阻塞等待


**场景2: 限制并发访问**

限制同时访问资源的任务数量:

```c
// 限制最多3个任务同时访问资源
#define MAX_CONCURRENT_ACCESS 3

SemaphoreHandle_t xResourceSemaphore;

// 访问共享资源的任务
void vResourceAccessTask(void *pvParameters)
{
    uint32_t ulTaskID = (uint32_t)pvParameters;
    
    while(1)
    {
        printf("[Task %lu] Requesting resource access...\n", ulTaskID);
        
        // 获取访问权限
        if(xSemaphoreTake(xResourceSemaphore, pdMS_TO_TICKS(5000)) == pdTRUE)
        {
            printf("[Task %lu] Accessing resource\n", ulTaskID);
            
            // 使用资源(模拟耗时操作)
            vTaskDelay(pdMS_TO_TICKS(2000));
            
            printf("[Task %lu] Resource access complete\n", ulTaskID);
            
            // 释放访问权限
            xSemaphoreGive(xResourceSemaphore);
        }
        else
        {
            printf("[Task %lu] Timeout waiting for resource\n", ulTaskID);
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建计数信号量(最多3个任务同时访问)
    xResourceSemaphore = xSemaphoreCreateCounting(
        MAX_CONCURRENT_ACCESS,  // 最大值
        MAX_CONCURRENT_ACCESS   // 初始值
    );
    
    // 创建5个任务(竞争3个访问权限)
    for(uint32_t i = 1; i <= 5; i++)
    {
        xTaskCreate(vResourceAccessTask, "Task", 256, (void *)i, 2, NULL);
    }
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**场景3: 事件计数**

使用计数信号量统计事件发生次数:

```c
// 事件计数信号量
SemaphoreHandle_t xEventCounterSemaphore;

// 事件产生任务(模拟中断)
void vEventGeneratorTask(void *pvParameters)
{
    uint32_t ulEventCount = 0;
    
    while(1)
    {
        // 模拟事件发生
        vTaskDelay(pdMS_TO_TICKS(500));
        
        ulEventCount++;
        printf("[Generator] Event %lu occurred\n", ulEventCount);
        
        // 增加事件计数
        xSemaphoreGive(xEventCounterSemaphore);
    }
}

// 事件处理任务
void vEventHandlerTask(void *pvParameters)
{
    uint32_t ulHandledCount = 0;
    
    while(1)
    {
        // 等待事件
        if(xSemaphoreTake(xEventCounterSemaphore, portMAX_DELAY) == pdTRUE)
        {
            ulHandledCount++;
            printf("[Handler] Processing event %lu\n", ulHandledCount);
            
            // 处理事件(耗时操作)
            vTaskDelay(pdMS_TO_TICKS(1000));
            
            printf("[Handler] Event %lu processed\n\n", ulHandledCount);
        }
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建计数信号量(最大值10,初始值0)
    xEventCounterSemaphore = xSemaphoreCreateCounting(10, 0);
    
    // 创建任务
    xTaskCreate(vEventGeneratorTask, "Generator", 256, NULL, 3, NULL);
    xTaskCreate(vEventHandlerTask, "Handler", 256, NULL, 2, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行结果**:

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

**代码说明**:
- 事件产生速度快于处理速度
- 计数信号量累积未处理的事件
- 处理任务按顺序处理所有事件
- 最大值限制了可以累积的事件数量


## 步骤3: 互斥量的使用

### 3.1 互斥量与二值信号量的区别

**互斥量(Mutex)**是一种特殊的二值信号量,专门用于资源的互斥访问:

| 特性 | 二值信号量 | 互斥量 |
|------|-----------|--------|
| **用途** | 任务同步、事件通知 | 资源互斥访问 |
| **所有权** | 无所有权概念 | 有所有权,谁获取谁释放 |
| **优先级继承** | 不支持 | 支持,防止优先级反转 |
| **递归获取** | 不支持 | 递归互斥量支持 |
| **中断使用** | 可以在中断中Give | 不能在中断中使用 |
| **典型场景** | 中断→任务通信 | 保护共享资源 |

**优先级继承机制**:

```
场景: 高优先级任务等待低优先级任务释放互斥量

使用二值信号量:
- 低优先级任务持有信号量
- 中优先级任务抢占低优先级任务
- 高优先级任务等待信号量,但被中优先级任务阻塞
- 结果: 优先级反转

使用互斥量:
- 低优先级任务持有互斥量
- 高优先级任务等待互斥量
- 低优先级任务优先级临时提升到高优先级
- 低优先级任务快速完成并释放互斥量
- 结果: 避免优先级反转
```


### 3.2 创建互斥量

**动态创建 - xSemaphoreCreateMutex()**

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 声明互斥量句柄
SemaphoreHandle_t xMutex;

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建互斥量
    xMutex = xSemaphoreCreateMutex();
    
    if(xMutex != NULL)
    {
        printf("Mutex created successfully\n");
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    }
    else
    {
        printf("Failed to create mutex\n");
    }
    
    while(1);
}
```

**静态创建 - xSemaphoreCreateMutexStatic()**

```c
// 静态分配互斥量控制块
StaticSemaphore_t xMutexBuffer;
SemaphoreHandle_t xMutex;

// 创建静态互斥量
xMutex = xSemaphoreCreateMutexStatic(&xMutexBuffer);
```

### 3.3 互斥量的使用

互斥量的使用方法与二值信号量类似,但有重要区别:

```c
// 获取互斥量
xSemaphoreTake(xMutex, portMAX_DELAY);

// 访问共享资源
// ...

// 释放互斥量(必须由获取者释放)
xSemaphoreGive(xMutex);
```

**重要规则**:
- ⚠️ 互斥量必须由获取它的任务释放
- ⚠️ 不能在中断中使用互斥量
- ⚠️ 不能在中断中调用`xSemaphoreTake()`或`xSemaphoreGive()`

### 3.4 完整示例:保护共享资源

使用互斥量保护串口资源:

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 互斥量句柄
SemaphoreHandle_t xUartMutex;

// 安全的串口打印函数
void SafePrintf(const char *format, ...)
{
    va_list args;
    
    // 获取互斥量
    if(xSemaphoreTake(xUartMutex, portMAX_DELAY) == pdTRUE)
    {
        // 访问串口资源
        va_start(args, format);
        vprintf(format, args);
        va_end(args);
        
        // 释放互斥量
        xSemaphoreGive(xUartMutex);
    }
}

// 任务1
void vTask1(void *pvParameters)
{
    uint32_t ulCounter = 0;
    
    while(1)
    {
        ulCounter++;
        
        // 使用互斥量保护的打印
        SafePrintf("[Task1] Counter: %lu\n", ulCounter);
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 任务2
void vTask2(void *pvParameters)
{
    uint32_t ulCounter = 0;
    
    while(1)
    {
        ulCounter++;
        
        // 使用互斥量保护的打印
        SafePrintf("[Task2] Counter: %lu\n", ulCounter);
        
        vTaskDelay(pdMS_TO_TICKS(700));
    }
}

// 任务3
void vTask3(void *pvParameters)
{
    uint32_t ulCounter = 0;
    
    while(1)
    {
        ulCounter++;
        
        // 使用互斥量保护的打印
        SafePrintf("[Task3] Counter: %lu\n", ulCounter);
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_USART2_UART_Init();
    
    printf("\n=== FreeRTOS Mutex Example ===\n\n");
    
    // 创建互斥量
    xUartMutex = xSemaphoreCreateMutex();
    
    if(xUartMutex != NULL)
    {
        printf("Mutex created\n\n");
        
        // 创建多个任务
        xTaskCreate(vTask1, "Task1", 256, NULL, 2, NULL);
        xTaskCreate(vTask2, "Task2", 256, NULL, 2, NULL);
        xTaskCreate(vTask3, "Task3", 256, NULL, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**:

```
=== FreeRTOS Mutex Example ===

Mutex created

[Task1] Counter: 1
[Task2] Counter: 1
[Task1] Counter: 2
[Task3] Counter: 1
[Task1] Counter: 3
[Task2] Counter: 2
[Task1] Counter: 4
[Task1] Counter: 5
[Task2] Counter: 3
[Task3] Counter: 2
```

**代码说明**:
- 创建互斥量保护串口资源
- 多个任务通过互斥量安全地访问串口
- 避免了串口输出混乱的问题
- 每个任务的输出都是完整的,不会被打断



## 步骤4: 递归互斥量的使用

### 4.1 什么是递归互斥量?

**递归互斥量(Recursive Mutex)**允许同一个任务多次获取同一个互斥量,而不会造成死锁。

**使用场景**:
- 递归函数需要访问共享资源
- 函数调用链中多次需要获取同一个互斥量
- 复杂的函数调用关系

**工作原理**:

```
普通互斥量:
任务A获取互斥量 → 成功
任务A再次获取互斥量 → 死锁! (等待自己释放)

递归互斥量:
任务A获取互斥量 → 成功 (计数=1)
任务A再次获取互斥量 → 成功 (计数=2)
任务A释放互斥量 → 计数=1 (仍被持有)
任务A再次释放互斥量 → 计数=0 (完全释放)
```

### 4.2 创建递归互斥量

**动态创建 - xSemaphoreCreateRecursiveMutex()**

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 声明递归互斥量句柄
SemaphoreHandle_t xRecursiveMutex;

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建递归互斥量
    xRecursiveMutex = xSemaphoreCreateRecursiveMutex();
    
    if(xRecursiveMutex != NULL)
    {
        printf("Recursive mutex created successfully\n");
        
        // 创建任务...
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**静态创建 - xSemaphoreCreateRecursiveMutexStatic()**

```c
// 静态分配递归互斥量控制块
StaticSemaphore_t xMutexBuffer;
SemaphoreHandle_t xRecursiveMutex;

// 创建静态递归互斥量
xRecursiveMutex = xSemaphoreCreateRecursiveMutexStatic(&xMutexBuffer);
```

### 4.3 递归互斥量的使用

**重要**: 递归互斥量必须使用专用的API:

```c
// 获取递归互斥量
BaseType_t xSemaphoreTakeRecursive(
    SemaphoreHandle_t xMutex,
    TickType_t xTicksToWait
);

// 释放递归互斥量
BaseType_t xSemaphoreGiveRecursive(
    SemaphoreHandle_t xMutex
);
```

⚠️ **注意**: 不能使用普通的`xSemaphoreTake()`和`xSemaphoreGive()`!

### 4.4 完整示例:递归函数访问共享资源

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 递归互斥量句柄
SemaphoreHandle_t xRecursiveMutex;

// 共享数据结构
typedef struct
{
    uint32_t ulValue;
    uint32_t ulDepth;
} SharedData_t;

SharedData_t xSharedData = {0, 0};

// 递归函数:计算阶乘
uint32_t CalculateFactorial(uint32_t n)
{
    uint32_t ulResult;
    
    // 获取递归互斥量
    xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY);
    
    // 访问共享数据
    xSharedData.ulDepth++;
    printf("  [Depth %lu] Calculating factorial of %lu\n", 
           xSharedData.ulDepth, n);
    
    // 递归计算
    if(n <= 1)
    {
        ulResult = 1;
    }
    else
    {
        // 递归调用(会再次获取互斥量)
        ulResult = n * CalculateFactorial(n - 1);
    }
    
    printf("  [Depth %lu] Result: %lu\n", xSharedData.ulDepth, ulResult);
    xSharedData.ulDepth--;
    
    // 释放递归互斥量
    xSemaphoreGiveRecursive(xRecursiveMutex);
    
    return ulResult;
}

// 计算任务
void vCalculateTask(void *pvParameters)
{
    uint32_t ulTaskID = (uint32_t)pvParameters;
    uint32_t ulNumber = 3 + ulTaskID;
    
    while(1)
    {
        printf("\n[Task %lu] Starting calculation of %lu!\n", ulTaskID, ulNumber);
        
        uint32_t ulResult = CalculateFactorial(ulNumber);
        
        printf("[Task %lu] %lu! = %lu\n", ulTaskID, ulNumber, ulResult);
        
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_USART2_UART_Init();
    
    printf("\n=== FreeRTOS Recursive Mutex Example ===\n\n");
    
    // 创建递归互斥量
    xRecursiveMutex = xSemaphoreCreateRecursiveMutex();
    
    if(xRecursiveMutex != NULL)
    {
        printf("Recursive mutex created\n");
        
        // 创建两个计算任务
        xTaskCreate(vCalculateTask, "Calc1", 512, (void *)1, 2, NULL);
        xTaskCreate(vCalculateTask, "Calc2", 512, (void *)2, 2, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**运行结果**:

```
=== FreeRTOS Recursive Mutex Example ===

Recursive mutex created

[Task 1] Starting calculation of 4!
  [Depth 1] Calculating factorial of 4
  [Depth 2] Calculating factorial of 3
  [Depth 3] Calculating factorial of 2
  [Depth 4] Calculating factorial of 1
  [Depth 4] Result: 1
  [Depth 3] Result: 2
  [Depth 2] Result: 6
  [Depth 1] Result: 24
[Task 1] 4! = 24

[Task 2] Starting calculation of 5!
  [Depth 1] Calculating factorial of 5
  [Depth 2] Calculating factorial of 4
  [Depth 3] Calculating factorial of 3
  [Depth 4] Calculating factorial of 2
  [Depth 5] Calculating factorial of 1
  [Depth 5] Result: 1
  [Depth 4] Result: 2
  [Depth 3] Result: 6
  [Depth 2] Result: 24
  [Depth 1] Result: 120
[Task 2] 5! = 120
```

**代码说明**:
- 递归函数在每次调用时都获取互斥量
- 使用递归互斥量避免了死锁
- 每次获取都会增加计数,每次释放都会减少计数
- 只有当计数归零时,互斥量才真正被释放
- 其他任务才能获取互斥量



## 验证

### 验证方法

1. **编译项目**
   ```bash
   # 在STM32CubeIDE中
   Project → Build Project
   
   # 检查编译输出
   Build Finished. 0 errors, 0 warnings.
   ```

2. **下载到开发板**
   - 连接开发板到电脑
   - 点击"Debug"或"Run"按钮
   - 程序自动下载并运行

3. **查看串口输出**
   - 打开串口调试工具
   - 配置: 115200, 8N1
   - 观察任务执行和信号量操作的输出

### 预期结果

**二值信号量示例**:
- ✅ 按键按下时,任务立即响应
- ✅ 串口输出"Button pressed!"
- ✅ LED状态正确切换
- ✅ 防抖机制工作正常

**计数信号量示例**:
- ✅ 最多3个任务同时使用缓冲区
- ✅ 第4个任务等待缓冲区释放
- ✅ 缓冲区正确分配和释放
- ✅ 无资源泄漏

**互斥量示例**:
- ✅ 串口输出完整,不混乱
- ✅ 多任务安全访问共享资源
- ✅ 无优先级反转问题

**递归互斥量示例**:
- ✅ 递归函数正确执行
- ✅ 无死锁现象
- ✅ 计算结果正确
- ✅ 任务间正确切换

### 测试要点

1. **功能测试**
   - [ ] 信号量创建成功
   - [ ] 任务能够获取和释放信号量
   - [ ] 任务同步工作正常
   - [ ] 资源管理正确
   - [ ] 互斥访问有效

2. **边界测试**
   - [ ] 信号量值为0时,任务正确阻塞
   - [ ] 计数信号量达到最大值时正确处理
   - [ ] 超时机制工作正常
   - [ ] 递归深度测试

3. **性能测试**
   - [ ] 信号量操作响应及时
   - [ ] 任务切换流畅
   - [ ] 无死锁或饥饿现象
   - [ ] 优先级继承机制有效


## 故障排除

### 问题1: 信号量创建失败

**现象**:
```c
xBinarySemaphore = xSemaphoreCreateBinary();
if(xBinarySemaphore == NULL) {
    printf("Failed to create semaphore\n");
}
```

**可能原因**:
1. 堆内存不足
2. FreeRTOS配置错误
3. 未启用信号量功能

**解决方法**:

```c
// 1. 增加堆大小(FreeRTOSConfig.h)
#define configTOTAL_HEAP_SIZE  ((size_t)(20 * 1024))  // 增加到20KB

// 2. 启用信号量功能
#define configUSE_MUTEXES                   1
#define configUSE_RECURSIVE_MUTEXES         1
#define configUSE_COUNTING_SEMAPHORES       1

// 3. 检查剩余堆空间
size_t xFreeHeap = xPortGetFreeHeapSize();
printf("Free heap: %d bytes\n", xFreeHeap);
```

### 问题2: 任务永久阻塞

**现象**:
```c
// 任务一直等待,永不返回
xSemaphoreTake(xSemaphore, portMAX_DELAY);
printf("This never prints\n");
```

**可能原因**:
1. 没有任务释放信号量
2. 信号量初始值为0且无人Give
3. 死锁情况

**解决方法**:

```c
// 1. 使用超时等待,避免永久阻塞
if(xSemaphoreTake(xSemaphore, pdMS_TO_TICKS(5000)) == pdTRUE)
{
    // 成功获取
}
else
{
    printf("Timeout waiting for semaphore\n");
}

// 2. 检查是否有任务释放信号量
// 3. 添加调试输出,跟踪信号量状态
printf("Waiting for semaphore...\n");
xSemaphoreTake(xSemaphore, portMAX_DELAY);
printf("Semaphore acquired\n");
```

### 问题3: 中断中使用错误的API

**现象**:
```c
// 在中断中使用普通API(错误)
void EXTI_IRQHandler(void)
{
    xSemaphoreGive(xSemaphore);  // ❌ 错误!
}
```

**解决方法**:

```c
// 在中断中必须使用FromISR版本的API
void EXTI_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // ✅ 正确:使用FromISR版本
    xSemaphoreGiveFromISR(xSemaphore, &xHigherPriorityTaskWoken);
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 问题4: 互斥量使用错误

**现象**:
```c
// 任务A获取互斥量
xSemaphoreTake(xMutex, portMAX_DELAY);

// 任务B尝试释放互斥量(错误!)
xSemaphoreGive(xMutex);  // ❌ 失败!
```

**解决方法**:

```c
// ✅ 正确:互斥量必须由获取者释放
void vTaskA(void *pvParameters)
{
    // 获取互斥量
    xSemaphoreTake(xMutex, portMAX_DELAY);
    
    // 访问共享资源
    // ...
    
    // 由同一任务释放
    xSemaphoreGive(xMutex);
}
```

### 问题5: 递归互斥量使用普通API

**现象**:
```c
// 创建递归互斥量
xRecursiveMutex = xSemaphoreCreateRecursiveMutex();

// 使用普通API(错误!)
xSemaphoreTake(xRecursiveMutex, portMAX_DELAY);  // ❌ 错误!
```

**解决方法**:

```c
// ✅ 正确:递归互斥量必须使用专用API
xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY);

// 访问共享资源
// ...

xSemaphoreGiveRecursive(xRecursiveMutex);
```



## 常见问题

### Q1: 二值信号量、互斥量和递归互斥量应该如何选择?

**A**: 根据使用场景选择:

**二值信号量**:
- ✅ 任务同步(如中断→任务通信)
- ✅ 事件通知
- ✅ 简单的任务间信号传递
- ❌ 不适合保护共享资源(无优先级继承)

**互斥量**:
- ✅ 保护共享资源
- ✅ 需要优先级继承机制
- ✅ 短时间持有的资源
- ❌ 不能在中断中使用
- ❌ 不支持递归获取

**递归互斥量**:
- ✅ 递归函数访问共享资源
- ✅ 复杂的函数调用链
- ✅ 同一任务需要多次获取
- ❌ 不能在中断中使用
- ❌ 开销比普通互斥量大

**选择建议**:
```c
// 中断→任务通信
xBinarySemaphore = xSemaphoreCreateBinary();

// 保护共享资源
xMutex = xSemaphoreCreateMutex();

// 递归函数访问共享资源
xRecursiveMutex = xSemaphoreCreateRecursiveMutex();

// 管理多个相同资源
xCountingSemaphore = xSemaphoreCreateCounting(5, 5);
```

### Q2: 为什么互斥量不能在中断中使用?

**A**: 主要原因:

1. **优先级继承机制**: 互斥量支持优先级继承,这个机制在中断上下文中没有意义
2. **阻塞等待**: 中断服务函数不能阻塞等待
3. **所有权概念**: 中断没有任务上下文,无法持有互斥量

**正确做法**:
```c
// ❌ 错误:在中断中使用互斥量
void EXTI_IRQHandler(void)
{
    xSemaphoreTake(xMutex, 0);  // 错误!
}

// ✅ 正确:在中断中使用二值信号量
void EXTI_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(xBinarySemaphore, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### Q3: 计数信号量的初始值应该设置为多少?

**A**: 根据使用场景决定:

**场景1: 资源池管理(初始值=资源总数)**
```c
// 有5个缓冲区,初始全部可用
xBufferSemaphore = xSemaphoreCreateCounting(5, 5);
```

**场景2: 事件计数(初始值=0)**
```c
// 等待事件发生
xEventSemaphore = xSemaphoreCreateCounting(10, 0);
```

**场景3: 限流控制(初始值=最大并发数)**
```c
// 最多3个任务同时访问
xAccessSemaphore = xSemaphoreCreateCounting(3, 3);
```

### Q4: 如何避免优先级反转?

**A**: 使用互斥量而不是二值信号量:

**问题场景**:
```
低优先级任务L持有资源
高优先级任务H等待资源
中优先级任务M抢占任务L
结果: 任务H被任务M间接阻塞
```

**解决方案**:
```c
// ❌ 使用二值信号量:可能发生优先级反转
xBinarySemaphore = xSemaphoreCreateBinary();

// ✅ 使用互斥量:自动优先级继承
xMutex = xSemaphoreCreateMutex();

// 当高优先级任务等待互斥量时:
// 1. 持有互斥量的低优先级任务优先级临时提升
// 2. 低优先级任务快速完成并释放互斥量
// 3. 高优先级任务获得互斥量
// 4. 低优先级任务恢复原优先级
```

### Q5: 信号量和队列有什么区别?

**A**: 主要区别:

| 特性 | 信号量 | 队列 |
|------|--------|------|
| **数据传递** | 不传递数据 | 传递数据 |
| **用途** | 同步和计数 | 数据通信 |
| **大小** | 只有计数值 | 可以存储多个数据 |
| **开销** | 小 | 较大 |
| **典型场景** | 事件通知、资源管理 | 任务间数据传递 |

**选择建议**:
```c
// 只需要通知事件发生 → 使用信号量
xSemaphoreGive(xEventSemaphore);

// 需要传递具体数据 → 使用队列
SensorData_t xData = {.temp = 25.5, .humidity = 60};
xQueueSend(xDataQueue, &xData, 0);
```

### Q6: 如何查看信号量的当前值?

**A**: 使用`uxSemaphoreGetCount()`:

```c
// 获取信号量当前值
UBaseType_t uxCount = uxSemaphoreGetCount(xCountingSemaphore);
printf("Semaphore count: %u\n", uxCount);

// 示例:检查资源可用性
if(uxSemaphoreGetCount(xResourceSemaphore) > 0)
{
    printf("Resources available: %u\n", uxCount);
}
else
{
    printf("No resources available\n");
}

// 注意:
// - 二值信号量:返回0或1
// - 计数信号量:返回0到最大值
// - 互斥量:返回0或1
// - 此函数不会阻塞任务
```


## 总结

### 核心要点

1. **信号量类型**
   - 二值信号量:值为0或1,用于任务同步和事件通知
   - 计数信号量:值为0到N,用于资源管理和限流
   - 互斥量:特殊的二值信号量,支持优先级继承
   - 递归互斥量:允许同一任务多次获取

2. **基本操作**
   - `xSemaphoreGive()`:释放信号量(值+1)
   - `xSemaphoreTake()`:获取信号量(值-1)
   - 中断中使用`FromISR`版本
   - 递归互斥量使用专用API

3. **主要应用**
   - 任务同步:中断→任务通信
   - 事件通知:生产者-消费者模式
   - 资源管理:缓冲区池、限流控制
   - 互斥访问:保护共享资源

4. **最佳实践**
   - 根据场景选择合适的信号量类型
   - 使用超时避免永久阻塞
   - 中断中使用FromISR版本API
   - 互斥量必须由获取者释放
   - 使用互斥量避免优先级反转

### 学习检查

完成本教程后,你应该能够:

- [ ] 理解FreeRTOS信号量的工作原理
- [ ] 创建和使用二值信号量
- [ ] 创建和使用计数信号量
- [ ] 理解互斥量与二值信号量的区别
- [ ] 正确使用互斥量保护共享资源
- [ ] 使用递归互斥量处理递归场景
- [ ] 在中断中正确使用信号量
- [ ] 选择合适的信号量类型解决实际问题

### 实践建议

1. **动手实践**
   - 在开发板上运行本教程的所有示例
   - 修改参数,观察不同的行为
   - 尝试组合多个信号量

2. **深入学习**
   - 学习FreeRTOS配置选项
   - 了解软件定时器和事件标志组
   - 研究任务间通信的最佳实践

3. **项目应用**
   - 在实际项目中使用信号量
   - 设计合理的任务同步方案
   - 优化系统性能和响应时间


## 下一步

### 推荐学习路径

1. **FreeRTOS配置选项详解**
   - 学习FreeRTOSConfig.h配置
   - 掌握内存管理方案选择
   - 理解调度策略和功能裁剪
   - 参考:[FreeRTOS配置选项详解](05-freertos-config.html)

2. **FreeRTOS软件定时器高级应用**
   - 学习软件定时器的创建和使用
   - 掌握单次和周期定时器
   - 理解定时器命令队列
   - 参考:[FreeRTOS软件定时器](../intermediate/01-freertos-timer.html)

3. **FreeRTOS事件标志组实战**
   - 学习事件标志组的概念
   - 掌握多事件同步方法
   - 理解位操作和等待机制
   - 参考:[FreeRTOS事件标志组](../intermediate/02-freertos-event-group.html)

4. **任务间通信方式对比**
   - 对比不同通信机制的特点
   - 学习如何选择合适的方式
   - 掌握性能优化技巧
   - 参考:[任务间通信方式对比](../../02-rtos-fundamentals/intermediate/02-ipc-comparison.html)

### 进阶主题

- **优先级反转问题与解决**:深入理解优先级反转及其解决方案
- **RTOS中断管理与延迟处理**:学习中断与RTOS的配合使用
- **FreeRTOS内存管理方案选择**:掌握不同内存管理方案的特点

### 实践项目

尝试以下项目来巩固所学知识:

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
- [互斥量API文档](https://www.freertos.org/a00113.html#xSemaphoreCreateMutex)

### 推荐阅读

- 《FreeRTOS实时内核实用指南》
- 《嵌入式实时操作系统》
- 《RTOS任务间通信机制详解》

### 在线资源

- [FreeRTOS官方示例](https://www.freertos.org/FreeRTOS-quick-start-guide.html)
- [STM32 FreeRTOS教程](https://www.st.com/resource/en/user_manual/dm00105262.pdf)
- [嵌入式系统设计模式](https://www.embedded.com/design-patterns-for-embedded-systems/)

### 相关内容

- [FreeRTOS快速入门](01-freertos-quickstart.html)
- [FreeRTOS任务创建与管理](02-freertos-tasks.html)
- [FreeRTOS队列通信实战](03-freertos-queue.html)
- [RTOS信号量使用实战](../../02-rtos-fundamentals/beginner/04-semaphore.html)
- [优先级反转问题与解决](../../02-rtos-fundamentals/intermediate/03-priority-inversion.html)

---

**版权声明**: 本文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**反馈与建议**: 如有问题或建议,请通过平台反馈系统联系我们。

**最后更新**: 2024-01-15
