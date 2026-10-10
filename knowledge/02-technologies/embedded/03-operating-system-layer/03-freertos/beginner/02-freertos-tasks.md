---
title: "FreeRTOS任务创建与管理：深入理解多任务编程"
description: "全面学习FreeRTOS任务管理的核心技术，包括任务创建API、任务优先级配置、任务堆栈管理、任务删除和挂起恢复操作，通过丰富的代码示例掌握多任务系统开发"
slug: "freertos-tasks"

# 分类信息
domain: "操作系统层"
module: "FreeRTOS"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - FreeRTOS任务
  - 任务管理
  - API使用
  - 多任务编程
  - 任务优先级
prerequisites:
  - "03-operating-system-layer/03-freertos/beginner/01-freertos-quickstart"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/02-rtos-task-management"
related_contents:
  - "03-operating-system-layer/03-freertos/beginner/03-freertos-queue"
  - "03-operating-system-layer/03-freertos/beginner/04-freertos-semaphore"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling"

# 学习信息
estimated_time: 70
difficulty_score: 3

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
  - FreeRTOS任务创建
  - xTaskCreate
  - 任务优先级
  - 任务堆栈
  - 任务管理API
cover_image: ""
---

# FreeRTOS任务创建与管理：深入理解多任务编程

## 学习目标

完成本教程后，你将能够：

- [ ] 掌握FreeRTOS任务创建的两种方法（动态和静态）
- [ ] 理解任务创建API的所有参数及其作用
- [ ] 熟练配置任务优先级和堆栈大小
- [ ] 掌握任务删除、挂起和恢复操作
- [ ] 理解任务句柄的使用和管理
- [ ] 学会任务状态查询和监控
- [ ] 掌握任务参数传递的多种方法

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 完成FreeRTOS快速入门教程
- 理解RTOS任务管理的基本概念
- 熟悉C语言指针和结构体
- 了解任务状态和调度原理

**技能要求**：
- 能够使用STM32CubeIDE创建FreeRTOS项目
- 会使用基本的调试工具
- 了解如何编译和下载程序

**硬件准备**：
- STM32开发板（如STM32F4 Discovery）
- ST-Link调试器
- USB数据线

## 准备工作

### 环境配置

本教程基于以下环境：

**软件环境**：
- STM32CubeIDE v1.10+
- FreeRTOS V10.3.1+
- HAL库 v1.27+

**硬件环境**：
- STM32F407VGT6开发板
- 板载LED（用于演示）
- 串口调试工具

### 创建基础项目


1. 打开STM32CubeIDE，创建新的STM32项目
2. 在CubeMX中启用FreeRTOS（CMSIS_V1接口）
3. 配置系统时钟和串口（用于调试输出）
4. 生成代码并打开项目

如果你已经完成了快速入门教程，可以直接使用之前的项目。

## 核心内容

### 任务创建API详解

FreeRTOS提供了两种任务创建方法：动态创建和静态创建。

#### 动态任务创建 - xTaskCreate()

动态创建是最常用的方法，内存从堆中自动分配。

**函数原型**：

```c
BaseType_t xTaskCreate(
    TaskFunction_t pvTaskCode,      // 任务函数指针
    const char * const pcName,      // 任务名称
    uint16_t usStackDepth,          // 栈大小（字）
    void *pvParameters,             // 任务参数
    UBaseType_t uxPriority,         // 任务优先级
    TaskHandle_t *pxCreatedTask     // 任务句柄（可选）
);
```

**返回值**：
- `pdPASS`：任务创建成功
- `errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY`：内存不足，创建失败

**完整示例**：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务句柄
TaskHandle_t myTaskHandle = NULL;

// 任务函数
void MyTask(void *pvParameters)
{
    // 任务初始化代码
    uint32_t counter = 0;
    
    // 任务主循环（永不退出）
    while(1)
    {
        // 执行任务工作
        printf("Task running, counter = %lu\n", counter++);
        
        // 延时，让出CPU
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 创建任务
    BaseType_t result = xTaskCreate(
        MyTask,              // 任务函数
        "MyTask",            // 任务名称
        128,                 // 栈大小：128字（512字节）
        NULL,                // 任务参数
        2,                   // 优先级：2
        &myTaskHandle        // 保存任务句柄
    );
    
    // 检查创建结果
    if(result == pdPASS)
    {
        printf("Task created successfully\n");
        
        // 启动调度器
        vTaskStartScheduler();
    }
    else
    {
        printf("Task creation failed\n");
    }
    
    // 永远不会执行到这里
    while(1);
}
```


#### 参数详细说明

##### 1. 任务函数 (pvTaskCode)

任务函数必须符合以下要求：

```c
// 任务函数签名
void TaskFunction(void *pvParameters);

// 任务函数必须是无限循环
void MyTask(void *pvParameters)
{
    // 初始化代码（只执行一次）
    InitializeHardware();
    
    // 主循环（永远执行）
    while(1)
    {
        // 任务代码
        DoWork();
        
        // 必须有延时或阻塞，否则会一直占用CPU
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    // 如果任务需要退出，应该删除自己
    // vTaskDelete(NULL);
}
```

**重要规则**：
- 任务函数永远不应该返回
- 必须包含延时或阻塞调用
- 如果需要退出，调用`vTaskDelete(NULL)`

##### 2. 任务名称 (pcName)

任务名称用于调试和监控：

```c
// 好的命名：描述性强
xTaskCreate(SensorTask, "Sensor", 128, NULL, 2, NULL);
xTaskCreate(DisplayTask, "Display", 128, NULL, 1, NULL);
xTaskCreate(NetworkTask, "Network", 256, NULL, 3, NULL);

// 不好的命名：不够清晰
xTaskCreate(Task1, "T1", 128, NULL, 2, NULL);
xTaskCreate(Task2, "T2", 128, NULL, 1, NULL);
```

**命名规范**：
- 最大长度由`configMAX_TASK_NAME_LEN`定义（默认16字符）
- 使用有意义的名称
- 避免使用特殊字符
- 名称可以重复（但不推荐）

##### 3. 栈大小 (usStackDepth)

栈大小以"字"为单位，不是字节：

```c
// Cortex-M系列：1字 = 4字节
// 栈大小（字节） = usStackDepth × 4

// 示例
xTaskCreate(Task, "Task", 128, NULL, 1, NULL);  // 128字 = 512字节
xTaskCreate(Task, "Task", 256, NULL, 1, NULL);  // 256字 = 1024字节
xTaskCreate(Task, "Task", 512, NULL, 1, NULL);  // 512字 = 2048字节
```

**栈大小建议**：

| 任务类型 | 栈大小（字） | 栈大小（字节） | 说明 |
|---------|------------|--------------|------|
| 最小任务 | 64-128 | 256-512 | 简单循环，无函数调用 |
| 小任务 | 128-256 | 512-1024 | LED控制，简单IO |
| 中等任务 | 256-512 | 1024-2048 | 数据处理，串口通信 |
| 大任务 | 512-1024 | 2048-4096 | 网络通信，文件操作 |
| 超大任务 | 1024+ | 4096+ | 复杂算法，大缓冲区 |

**影响栈大小的因素**：

```c
void TaskWithLargeStack(void *pvParameters)
{
    // 1. 局部变量占用栈空间
    char buffer[1024];  // 需要1KB栈空间
    uint32_t array[100]; // 需要400字节
    
    // 2. 函数调用深度
    Function1();  // 每次调用需要额外栈空间
    
    // 3. 中断嵌套
    // 中断发生时会使用任务栈保存上下文
    
    while(1)
    {
        vTaskDelay(100);
    }
}
```


##### 4. 任务参数 (pvParameters)

可以向任务传递任何类型的参数：

**方法1：传递简单值**

```c
// 传递整数
xTaskCreate(Task, "Task", 128, (void *)100, 1, NULL);

// 在任务中接收
void Task(void *pvParameters)
{
    uint32_t value = (uint32_t)pvParameters;
    printf("Received value: %lu\n", value);
    
    while(1)
    {
        vTaskDelay(value);  // 使用传入的延时值
    }
}
```

**方法2：传递指针**

```c
// 定义参数结构体
typedef struct
{
    uint32_t sensor_id;
    uint32_t sample_rate;
    GPIO_TypeDef *gpio_port;
    uint16_t gpio_pin;
} TaskParams_t;

// 创建参数实例
TaskParams_t params = {
    .sensor_id = 1,
    .sample_rate = 1000,
    .gpio_port = GPIOA,
    .gpio_pin = GPIO_PIN_5
};

// 传递参数指针
xTaskCreate(SensorTask, "Sensor", 256, &params, 2, NULL);

// 在任务中接收
void SensorTask(void *pvParameters)
{
    // 转换参数类型
    TaskParams_t *p = (TaskParams_t *)pvParameters;
    
    printf("Sensor ID: %lu\n", p->sensor_id);
    printf("Sample Rate: %lu Hz\n", p->sample_rate);
    
    while(1)
    {
        // 使用参数
        HAL_GPIO_TogglePin(p->gpio_port, p->gpio_pin);
        vTaskDelay(pdMS_TO_TICKS(1000 / p->sample_rate));
    }
}
```

**方法3：传递多个任务共享的参数**

```c
// 为每个任务创建独立的参数
typedef struct
{
    uint32_t task_id;
    uint32_t delay_ms;
} TaskConfig_t;

// 创建多个参数实例（必须是静态或全局变量）
static TaskConfig_t task1_config = {.task_id = 1, .delay_ms = 500};
static TaskConfig_t task2_config = {.task_id = 2, .delay_ms = 1000};
static TaskConfig_t task3_config = {.task_id = 3, .delay_ms = 2000};

// 创建多个任务，使用相同的任务函数
xTaskCreate(GenericTask, "Task1", 128, &task1_config, 1, NULL);
xTaskCreate(GenericTask, "Task2", 128, &task2_config, 1, NULL);
xTaskCreate(GenericTask, "Task3", 128, &task3_config, 1, NULL);

// 通用任务函数
void GenericTask(void *pvParameters)
{
    TaskConfig_t *config = (TaskConfig_t *)pvParameters;
    
    while(1)
    {
        printf("Task %lu running\n", config->task_id);
        vTaskDelay(pdMS_TO_TICKS(config->delay_ms));
    }
}
```

**⚠️ 重要注意事项**：

```c
// ❌ 错误：传递局部变量的地址
void CreateTask(void)
{
    TaskParams_t params;  // 局部变量
    params.value = 100;
    
    // 错误！params在函数返回后会被销毁
    xTaskCreate(Task, "Task", 128, &params, 1, NULL);
}

// ✅ 正确：使用静态或全局变量
static TaskParams_t params;  // 静态变量

void CreateTask(void)
{
    params.value = 100;
    xTaskCreate(Task, "Task", 128, &params, 1, NULL);  // 正确
}

// ✅ 正确：使用动态分配的内存
void CreateTask(void)
{
    TaskParams_t *params = pvPortMalloc(sizeof(TaskParams_t));
    params->value = 100;
    xTaskCreate(Task, "Task", 128, params, 1, NULL);  // 正确
}
```


##### 5. 任务优先级 (uxPriority)

优先级决定任务的调度顺序：

```c
// 优先级范围：0 到 (configMAX_PRIORITIES - 1)
// 数字越大，优先级越高

// 典型优先级定义
#define PRIORITY_IDLE       0  // 空闲任务（系统保留）
#define PRIORITY_LOW        1  // 低优先级
#define PRIORITY_BELOW_NORMAL 2
#define PRIORITY_NORMAL     3  // 普通优先级
#define PRIORITY_ABOVE_NORMAL 4
#define PRIORITY_HIGH       5  // 高优先级
#define PRIORITY_REALTIME   6  // 实时任务

// 创建不同优先级的任务
xTaskCreate(BackgroundTask, "Background", 128, NULL, PRIORITY_LOW, NULL);
xTaskCreate(NormalTask, "Normal", 256, NULL, PRIORITY_NORMAL, NULL);
xTaskCreate(CriticalTask, "Critical", 512, NULL, PRIORITY_HIGH, NULL);
```

**优先级分配原则**：

| 任务类型 | 优先级 | 示例 |
|---------|-------|------|
| 实时响应任务 | 最高 | 中断后处理、紧急控制 |
| 周期性任务 | 高 | 传感器采集、数据处理 |
| 用户交互任务 | 中 | 按键检测、显示更新 |
| 后台任务 | 低 | 日志记录、统计分析 |
| 空闲任务 | 最低 | 系统空闲时执行 |

**优先级调度示例**：

```c
// 高优先级任务
void HighPriorityTask(void *pvParameters)
{
    while(1)
    {
        printf("High priority task running\n");
        // 高优先级任务运行时，低优先级任务无法运行
        vTaskDelay(pdMS_TO_TICKS(1000));
        // 延时期间，低优先级任务可以运行
    }
}

// 低优先级任务
void LowPriorityTask(void *pvParameters)
{
    while(1)
    {
        printf("Low priority task running\n");
        // 只有在高优先级任务阻塞时才能运行
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

int main(void)
{
    SystemInit();
    
    // 创建任务
    xTaskCreate(HighPriorityTask, "High", 128, NULL, 3, NULL);
    xTaskCreate(LowPriorityTask, "Low", 128, NULL, 1, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

##### 6. 任务句柄 (pxCreatedTask)

任务句柄是任务的唯一标识符：

```c
// 定义任务句柄
TaskHandle_t task1Handle = NULL;
TaskHandle_t task2Handle = NULL;

// 创建任务并保存句柄
xTaskCreate(Task1, "Task1", 128, NULL, 1, &task1Handle);
xTaskCreate(Task2, "Task2", 128, NULL, 1, &task2Handle);

// 使用句柄操作任务
vTaskSuspend(task1Handle);   // 挂起任务1
vTaskResume(task1Handle);    // 恢复任务1
vTaskDelete(task2Handle);    // 删除任务2

// 如果不需要句柄，可以传NULL
xTaskCreate(Task3, "Task3", 128, NULL, 1, NULL);
```

**句柄的用途**：
- 挂起和恢复任务
- 删除任务
- 修改任务优先级
- 查询任务状态
- 向任务发送通知


#### 静态任务创建 - xTaskCreateStatic()

静态创建使用预分配的内存，适合安全关键应用：

```c
// 需要在FreeRTOSConfig.h中启用
#define configSUPPORT_STATIC_ALLOCATION  1

// 定义任务栈（静态分配）
#define TASK_STACK_SIZE  128
static StackType_t taskStack[TASK_STACK_SIZE];

// 定义任务控制块（静态分配）
static StaticTask_t taskTCB;

// 任务函数
void MyTask(void *pvParameters)
{
    while(1)
    {
        printf("Static task running\n");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    SystemInit();
    
    // 静态创建任务
    TaskHandle_t taskHandle = xTaskCreateStatic(
        MyTask,              // 任务函数
        "MyTask",            // 任务名称
        TASK_STACK_SIZE,     // 栈大小
        NULL,                // 参数
        2,                   // 优先级
        taskStack,           // 栈数组
        &taskTCB             // TCB
    );
    
    if(taskHandle != NULL)
    {
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**动态 vs 静态创建对比**：

| 特性 | 动态创建 | 静态创建 |
|------|---------|---------|
| 内存分配 | 从堆中分配 | 使用预定义的静态内存 |
| 灵活性 | 高（运行时创建） | 低（编译时确定） |
| 内存碎片 | 可能产生碎片 | 无碎片问题 |
| 内存使用 | 需要堆空间 | 不需要堆 |
| 适用场景 | 一般应用 | 安全关键应用 |
| 代码复杂度 | 简单 | 稍复杂 |
| 配置要求 | 默认启用 | 需要启用配置 |

### 任务删除

#### 删除自己

任务可以删除自己，通常用于一次性任务：

```c
void TemporaryTask(void *pvParameters)
{
    // 执行一次性初始化
    printf("Initializing system...\n");
    InitializeSystem();
    printf("Initialization complete\n");
    
    // 任务完成后删除自己
    vTaskDelete(NULL);  // NULL表示删除当前任务
    
    // 永远不会执行到这里
    printf("This will never print\n");
}

int main(void)
{
    SystemInit();
    
    // 创建临时任务
    xTaskCreate(TemporaryTask, "Init", 256, NULL, 1, NULL);
    
    // 创建其他任务
    xTaskCreate(MainTask, "Main", 256, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

#### 删除其他任务

可以通过任务句柄删除其他任务：

```c
TaskHandle_t workerTaskHandle = NULL;

void WorkerTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    while(1)
    {
        printf("Worker task: %lu\n", counter++);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void ManagerTask(void *pvParameters)
{
    while(1)
    {
        // 检查是否需要停止工作任务
        if(WorkCompleted())
        {
            if(workerTaskHandle != NULL)
            {
                // 删除工作任务
                vTaskDelete(workerTaskHandle);
                workerTaskHandle = NULL;
                printf("Worker task deleted\n");
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    SystemInit();
    
    // 创建任务
    xTaskCreate(WorkerTask, "Worker", 256, NULL, 1, &workerTaskHandle);
    xTaskCreate(ManagerTask, "Manager", 256, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**⚠️ 删除任务的注意事项**：

```c
// ❌ 错误：删除后继续使用句柄
vTaskDelete(taskHandle);
vTaskResume(taskHandle);  // 错误！任务已被删除

// ✅ 正确：删除后清空句柄
vTaskDelete(taskHandle);
taskHandle = NULL;

// ✅ 正确：删除前检查句柄
if(taskHandle != NULL)
{
    vTaskDelete(taskHandle);
    taskHandle = NULL;
}

// ✅ 正确：删除前释放资源
void TaskWithResources(void *pvParameters)
{
    // 分配资源
    uint8_t *buffer = pvPortMalloc(1024);
    
    while(1)
    {
        if(ShouldExit())
        {
            // 释放资源
            vPortFree(buffer);
            
            // 删除自己
            vTaskDelete(NULL);
        }
        
        vTaskDelay(100);
    }
}
```


### 任务挂起和恢复

#### 挂起任务 - vTaskSuspend()

挂起任务会使任务进入挂起态，不参与调度：

```c
TaskHandle_t taskHandle;

// 挂起指定任务
vTaskSuspend(taskHandle);

// 挂起自己
vTaskSuspend(NULL);
```

**完整示例**：

```c
TaskHandle_t dataTaskHandle = NULL;

void DataTask(void *pvParameters)
{
    while(1)
    {
        printf("Processing data...\n");
        ProcessData();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void ControlTask(void *pvParameters)
{
    bool taskActive = true;
    
    while(1)
    {
        if(Button_Pressed())
        {
            taskActive = !taskActive;
            
            if(taskActive)
            {
                // 恢复任务
                vTaskResume(dataTaskHandle);
                printf("Data task resumed\n");
            }
            else
            {
                // 挂起任务
                vTaskSuspend(dataTaskHandle);
                printf("Data task suspended\n");
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

int main(void)
{
    SystemInit();
    
    xTaskCreate(DataTask, "Data", 256, NULL, 2, &dataTaskHandle);
    xTaskCreate(ControlTask, "Control", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

#### 恢复任务 - vTaskResume()

恢复被挂起的任务：

```c
// 从任务中恢复
vTaskResume(taskHandle);

// 从中断中恢复（ISR安全版本）
BaseType_t xHigherPriorityTaskWoken = pdFALSE;
xTaskResumeFromISR(taskHandle);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
```

**中断中恢复任务示例**：

```c
TaskHandle_t urgentTaskHandle = NULL;

void UrgentTask(void *pvParameters)
{
    while(1)
    {
        printf("Handling urgent event\n");
        HandleUrgentEvent();
        
        // 处理完后挂起自己，等待下次中断唤醒
        vTaskSuspend(NULL);
    }
}

// 外部中断服务函数
void EXTI0_IRQHandler(void)
{
    if(__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET)
    {
        // 清除中断标志
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 从中断中恢复任务
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xTaskResumeFromISR(urgentTaskHandle);
        
        // 如果恢复的任务优先级更高，立即切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```

**挂起和恢复的应用场景**：

1. **省电模式**：挂起不需要的任务以降低功耗
2. **条件执行**：根据系统状态动态启停任务
3. **中断驱动**：任务在中断中被唤醒执行
4. **资源管理**：暂停某些任务以释放资源

### 任务优先级管理

#### 获取任务优先级

```c
TaskHandle_t taskHandle;

// 获取指定任务的优先级
UBaseType_t priority = uxTaskPriorityGet(taskHandle);
printf("Task priority: %u\n", priority);

// 获取当前任务的优先级
UBaseType_t myPriority = uxTaskPriorityGet(NULL);
printf("My priority: %u\n", myPriority);
```

#### 设置任务优先级

```c
TaskHandle_t taskHandle;

// 设置指定任务的优先级
vTaskPrioritySet(taskHandle, 5);

// 设置当前任务的优先级
vTaskPrioritySet(NULL, 3);

// 提升自己的优先级
UBaseType_t currentPriority = uxTaskPriorityGet(NULL);
vTaskPrioritySet(NULL, currentPriority + 1);

// 降低自己的优先级
vTaskPrioritySet(NULL, currentPriority - 1);
```

#### 动态优先级调整示例

```c
TaskHandle_t workerTaskHandle = NULL;

void WorkerTask(void *pvParameters)
{
    while(1)
    {
        // 执行工作
        DoWork();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void ManagerTask(void *pvParameters)
{
    while(1)
    {
        if(EmergencyDetected())
        {
            // 紧急情况：提升工作任务优先级
            vTaskPrioritySet(workerTaskHandle, 5);
            printf("Priority elevated to 5\n");
        }
        else if(NormalOperation())
        {
            // 正常情况：恢复普通优先级
            vTaskPrioritySet(workerTaskHandle, 2);
            printf("Priority restored to 2\n");
        }
        else if(LowPowerMode())
        {
            // 低功耗模式：降低优先级
            vTaskPrioritySet(workerTaskHandle, 1);
            printf("Priority lowered to 1\n");
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void)
{
    SystemInit();
    
    xTaskCreate(WorkerTask, "Worker", 256, NULL, 2, &workerTaskHandle);
    xTaskCreate(ManagerTask, "Manager", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


### 任务状态查询

#### 获取任务句柄

```c
// 通过任务名称获取句柄
TaskHandle_t handle = xTaskGetHandle("TaskName");

if(handle != NULL)
{
    printf("Task found\n");
}
else
{
    printf("Task not found\n");
}

// 获取当前任务句柄
TaskHandle_t currentHandle = xTaskGetCurrentTaskHandle();
```

#### 获取任务名称

```c
TaskHandle_t taskHandle;

// 获取任务名称
char *taskName = pcTaskGetName(taskHandle);
printf("Task name: %s\n", taskName);

// 获取当前任务名称
char *myName = pcTaskGetName(NULL);
printf("My name: %s\n", myName);
```

#### 获取任务状态

```c
TaskHandle_t taskHandle;

// 获取任务状态
eTaskState state = eTaskGetState(taskHandle);

switch(state)
{
    case eRunning:
        printf("Task is running\n");
        break;
    case eReady:
        printf("Task is ready\n");
        break;
    case eBlocked:
        printf("Task is blocked\n");
        break;
    case eSuspended:
        printf("Task is suspended\n");
        break;
    case eDeleted:
        printf("Task is deleted\n");
        break;
    default:
        printf("Unknown state\n");
        break;
}
```

#### 获取栈使用情况

```c
TaskHandle_t taskHandle;

// 获取栈水位（最小剩余栈空间）
UBaseType_t stackHighWaterMark = uxTaskGetStackHighWaterMark(taskHandle);
printf("Minimum free stack: %u words (%u bytes)\n", 
       stackHighWaterMark, 
       stackHighWaterMark * 4);

// 获取当前任务的栈水位
UBaseType_t myStackMark = uxTaskGetStackHighWaterMark(NULL);
printf("My stack free: %u words\n", myStackMark);

// 检查栈是否充足
if(stackHighWaterMark < 32)  // 少于128字节
{
    printf("Warning: Stack space is low!\n");
}
```

#### 任务监控示例

```c
void MonitorTask(void *pvParameters)
{
    TaskHandle_t task1 = xTaskGetHandle("Task1");
    TaskHandle_t task2 = xTaskGetHandle("Task2");
    TaskHandle_t task3 = xTaskGetHandle("Task3");
    
    while(1)
    {
        printf("\n=== Task Monitor ===\n");
        
        // 监控Task1
        if(task1 != NULL)
        {
            printf("Task1:\n");
            printf("  State: %d\n", eTaskGetState(task1));
            printf("  Priority: %u\n", uxTaskPriorityGet(task1));
            printf("  Stack free: %u words\n", 
                   uxTaskGetStackHighWaterMark(task1));
        }
        
        // 监控Task2
        if(task2 != NULL)
        {
            printf("Task2:\n");
            printf("  State: %d\n", eTaskGetState(task2));
            printf("  Priority: %u\n", uxTaskPriorityGet(task2));
            printf("  Stack free: %u words\n", 
                   uxTaskGetStackHighWaterMark(task2));
        }
        
        // 监控Task3
        if(task3 != NULL)
        {
            printf("Task3:\n");
            printf("  State: %d\n", eTaskGetState(task3));
            printf("  Priority: %u\n", uxTaskPriorityGet(task3));
            printf("  Stack free: %u words\n", 
                   uxTaskGetStackHighWaterMark(task3));
        }
        
        // 系统信息
        printf("\nSystem:\n");
        printf("  Free heap: %u bytes\n", xPortGetFreeHeapSize());
        printf("  Task count: %u\n", uxTaskGetNumberOfTasks());
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
```

### 任务延时

#### 相对延时 - vTaskDelay()

从调用时刻开始计时：

```c
void Task(void *pvParameters)
{
    while(1)
    {
        printf("Task running\n");
        
        // 延时1000个时钟节拍（1秒）
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // 或直接使用节拍数
        // vTaskDelay(1000);
    }
}
```

**相对延时的问题**：

```c
void Task(void *pvParameters)
{
    while(1)
    {
        // 执行工作（假设需要50ms）
        DoWork();  // 50ms
        
        // 延时1000ms
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // 实际周期 = 50ms + 1000ms = 1050ms
        // 不是精确的1000ms周期
    }
}
```

#### 绝对延时 - vTaskDelayUntil()

实现精确的周期性延时：

```c
void Task(void *pvParameters)
{
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(1000);  // 1秒周期
    
    // 初始化上次唤醒时间
    xLastWakeTime = xTaskGetTickCount();
    
    while(1)
    {
        // 执行工作（无论需要多长时间）
        DoWork();
        
        // 精确的周期性延时
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        // 保证精确的1000ms周期
    }
}
```

**vTaskDelay vs vTaskDelayUntil 对比**：

| 特性 | vTaskDelay | vTaskDelayUntil |
|------|-----------|----------------|
| 延时类型 | 相对延时 | 绝对延时 |
| 周期精度 | 不精确 | 精确 |
| 使用场景 | 一般延时 | 周期性任务 |
| 代码复杂度 | 简单 | 稍复杂 |
| CPU占用 | 相同 | 相同 |


## 实践示例

### 示例1：多LED控制系统

创建多个任务，以不同频率控制LED：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "stm32f4xx_hal.h"

// LED配置结构体
typedef struct
{
    GPIO_TypeDef *port;
    uint16_t pin;
    uint32_t delay_ms;
    const char *name;
} LED_Config_t;

// LED任务函数
void LED_Task(void *pvParameters)
{
    LED_Config_t *config = (LED_Config_t *)pvParameters;
    
    printf("%s task started\n", config->name);
    
    while(1)
    {
        // 切换LED状态
        HAL_GPIO_TogglePin(config->port, config->pin);
        printf("%s toggled\n", config->name);
        
        // 延时
        vTaskDelay(pdMS_TO_TICKS(config->delay_ms));
    }
}

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化GPIO
    __HAL_RCC_GPIOD_CLK_ENABLE();
    
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    
    // 配置LED引脚
    GPIO_InitStruct.Pin = GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
    HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);
    
    // LED配置（静态变量，生命周期持续整个程序）
    static LED_Config_t led_green = {
        .port = GPIOD,
        .pin = GPIO_PIN_12,
        .delay_ms = 500,
        .name = "LED_Green"
    };
    
    static LED_Config_t led_orange = {
        .port = GPIOD,
        .pin = GPIO_PIN_13,
        .delay_ms = 1000,
        .name = "LED_Orange"
    };
    
    static LED_Config_t led_red = {
        .port = GPIOD,
        .pin = GPIO_PIN_14,
        .delay_ms = 2000,
        .name = "LED_Red"
    };
    
    static LED_Config_t led_blue = {
        .port = GPIOD,
        .pin = GPIO_PIN_15,
        .delay_ms = 3000,
        .name = "LED_Blue"
    };
    
    // 创建LED任务
    xTaskCreate(LED_Task, "LED_Green", 128, &led_green, 1, NULL);
    xTaskCreate(LED_Task, "LED_Orange", 128, &led_orange, 1, NULL);
    xTaskCreate(LED_Task, "LED_Red", 128, &led_red, 1, NULL);
    xTaskCreate(LED_Task, "LED_Blue", 128, &led_blue, 1, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行效果**：
- 绿色LED每500ms闪烁
- 橙色LED每1秒闪烁
- 红色LED每2秒闪烁
- 蓝色LED每3秒闪烁

### 示例2：任务动态管理

演示任务的创建、挂起、恢复和删除：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务句柄
TaskHandle_t workerTaskHandle = NULL;
TaskHandle_t monitorTaskHandle = NULL;

// 工作任务
void WorkerTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    printf("Worker task started\n");
    
    while(1)
    {
        printf("Worker: %lu\n", counter++);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 监控任务
void MonitorTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    printf("Monitor task started\n");
    
    while(1)
    {
        printf("Monitor: %lu\n", counter++);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 控制任务
void ControlTask(void *pvParameters)
{
    uint32_t state = 0;
    
    printf("Control task started\n");
    
    while(1)
    {
        switch(state)
        {
            case 0:
                // 创建工作任务
                printf("\n[Control] Creating worker task...\n");
                xTaskCreate(WorkerTask, "Worker", 256, NULL, 2, &workerTaskHandle);
                state = 1;
                break;
                
            case 1:
                // 运行5秒
                printf("[Control] Worker task running...\n");
                vTaskDelay(pdMS_TO_TICKS(5000));
                state = 2;
                break;
                
            case 2:
                // 挂起工作任务
                printf("\n[Control] Suspending worker task...\n");
                vTaskSuspend(workerTaskHandle);
                state = 3;
                break;
                
            case 3:
                // 挂起3秒
                printf("[Control] Worker task suspended...\n");
                vTaskDelay(pdMS_TO_TICKS(3000));
                state = 4;
                break;
                
            case 4:
                // 恢复工作任务
                printf("\n[Control] Resuming worker task...\n");
                vTaskResume(workerTaskHandle);
                state = 5;
                break;
                
            case 5:
                // 运行3秒
                printf("[Control] Worker task resumed...\n");
                vTaskDelay(pdMS_TO_TICKS(3000));
                state = 6;
                break;
                
            case 6:
                // 删除工作任务
                printf("\n[Control] Deleting worker task...\n");
                vTaskDelete(workerTaskHandle);
                workerTaskHandle = NULL;
                state = 7;
                break;
                
            case 7:
                // 等待5秒后重新开始
                printf("[Control] Worker task deleted, restarting in 5s...\n");
                vTaskDelay(pdMS_TO_TICKS(5000));
                state = 0;
                break;
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

int main(void)
{
    SystemInit();
    
    // 创建监控任务（一直运行）
    xTaskCreate(MonitorTask, "Monitor", 256, NULL, 1, &monitorTaskHandle);
    
    // 创建控制任务
    xTaskCreate(ControlTask, "Control", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


### 示例3：优先级调度演示

演示不同优先级任务的调度行为：

```c
#include "FreeRTOS.h"
#include "task.h"

// 高优先级任务
void HighPriorityTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    while(1)
    {
        printf("[HIGH] Running: %lu\n", counter++);
        
        // 执行一些工作
        for(volatile uint32_t i = 0; i < 1000000; i++);
        
        // 延时，让出CPU
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 中优先级任务
void MediumPriorityTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    while(1)
    {
        printf("[MEDIUM] Running: %lu\n", counter++);
        
        // 执行一些工作
        for(volatile uint32_t i = 0; i < 500000; i++);
        
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 低优先级任务
void LowPriorityTask(void *pvParameters)
{
    uint32_t counter = 0;
    
    while(1)
    {
        printf("[LOW] Running: %lu\n", counter++);
        
        // 执行一些工作
        for(volatile uint32_t i = 0; i < 100000; i++);
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

int main(void)
{
    SystemInit();
    
    printf("Creating tasks with different priorities...\n");
    
    // 创建不同优先级的任务
    xTaskCreate(HighPriorityTask, "High", 256, NULL, 3, NULL);
    xTaskCreate(MediumPriorityTask, "Medium", 256, NULL, 2, NULL);
    xTaskCreate(LowPriorityTask, "Low", 256, NULL, 1, NULL);
    
    printf("Starting scheduler...\n");
    vTaskStartScheduler();
    
    while(1);
}
```

**观察要点**：
- 高优先级任务优先执行
- 中优先级任务在高优先级任务阻塞时执行
- 低优先级任务在其他任务都阻塞时才执行
- 高优先级任务就绪时会抢占低优先级任务

### 示例4：精确周期任务

使用`vTaskDelayUntil()`实现精确的周期性任务：

```c
#include "FreeRTOS.h"
#include "task.h"

// 传感器采集任务（精确10Hz）
void SensorTask(void *pvParameters)
{
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(100);  // 100ms = 10Hz
    
    // 初始化上次唤醒时间
    xLastWakeTime = xTaskGetTickCount();
    
    uint32_t counter = 0;
    
    while(1)
    {
        // 记录开始时间
        TickType_t startTime = xTaskGetTickCount();
        
        // 读取传感器（模拟，可能需要不同时间）
        float value = ReadSensor();
        
        // 处理数据
        ProcessData(value);
        
        // 记录结束时间
        TickType_t endTime = xTaskGetTickCount();
        TickType_t elapsed = endTime - startTime;
        
        printf("Sample %lu: value=%.2f, time=%lu ms\n", 
               counter++, value, elapsed);
        
        // 精确的周期性延时
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        // 无论处理需要多长时间，都保证100ms的周期
    }
}

// 显示任务（精确1Hz）
void DisplayTask(void *pvParameters)
{
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(1000);  // 1000ms = 1Hz
    
    xLastWakeTime = xTaskGetTickCount();
    
    while(1)
    {
        // 更新显示
        UpdateDisplay();
        
        printf("Display updated at %lu ms\n", xTaskGetTickCount());
        
        // 精确的1秒周期
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

int main(void)
{
    SystemInit();
    
    xTaskCreate(SensorTask, "Sensor", 256, NULL, 2, NULL);
    xTaskCreate(DisplayTask, "Display", 256, NULL, 1, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

## 故障排除

### 问题1：任务创建失败

**现象**：
- `xTaskCreate()`返回`errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY`
- 任务无法创建

**可能原因**：
1. 堆内存不足
2. 栈大小设置过大
3. 创建了太多任务

**解决方法**：

```c
// 1. 增加堆大小
// 在FreeRTOSConfig.h中
#define configTOTAL_HEAP_SIZE  (20 * 1024)  // 增加到20KB

// 2. 减小任务栈大小
xTaskCreate(Task, "Task", 128, NULL, 1, NULL);  // 从256减到128

// 3. 检查堆使用情况
size_t freeHeap = xPortGetFreeHeapSize();
printf("Free heap: %u bytes\n", freeHeap);

// 4. 使用静态创建（不需要堆）
static StackType_t taskStack[128];
static StaticTask_t taskTCB;
xTaskCreateStatic(Task, "Task", 128, NULL, 1, taskStack, &taskTCB);
```

### 问题2：栈溢出

**现象**：
- 系统崩溃或死机
- 任务行为异常
- 数据损坏

**可能原因**：
1. 栈大小不足
2. 局部变量过大
3. 函数调用层次过深
4. 递归调用

**解决方法**：

```c
// 1. 启用栈溢出检测
// 在FreeRTOSConfig.h中
#define configCHECK_FOR_STACK_OVERFLOW  2

// 2. 实现栈溢出钩子函数
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    printf("Stack overflow in task: %s\n", pcTaskName);
    while(1);  // 停止系统
}

// 3. 检查栈使用情况
UBaseType_t stackMark = uxTaskGetStackHighWaterMark(taskHandle);
printf("Stack free: %u words (%u bytes)\n", stackMark, stackMark * 4);

// 4. 增加栈大小
xTaskCreate(Task, "Task", 256, NULL, 1, NULL);  // 从128增加到256

// 5. 减少局部变量
// ❌ 不好：大数组在栈上
void Task(void *pvParameters)
{
    char buffer[2048];  // 占用2KB栈空间
}

// ✅ 更好：使用动态分配
void Task(void *pvParameters)
{
    char *buffer = pvPortMalloc(2048);
    // 使用buffer
    vPortFree(buffer);
}
```


### 问题3：任务无法运行

**现象**：
- 某个任务从不执行
- 任务创建成功但不运行

**可能原因**：
1. 优先级设置不当
2. 任务被挂起
3. 任务在等待事件
4. 高优先级任务占用CPU

**解决方法**：

```c
// 1. 检查任务状态
eTaskState state = eTaskGetState(taskHandle);
if(state == eSuspended)
{
    printf("Task is suspended\n");
    vTaskResume(taskHandle);
}

// 2. 检查优先级
UBaseType_t priority = uxTaskPriorityGet(taskHandle);
printf("Task priority: %u\n", priority);

// 3. 确保高优先级任务有延时
void HighPriorityTask(void *pvParameters)
{
    while(1)
    {
        DoWork();
        // 必须有延时，否则低优先级任务无法运行
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// 4. 使用任务通知或信号量唤醒任务
// 而不是让任务一直轮询
```

### 问题4：任务删除后系统异常

**现象**：
- 删除任务后系统崩溃
- 出现硬件错误

**可能原因**：
1. 删除后继续使用句柄
2. 未释放任务占用的资源
3. 其他任务仍在访问被删除任务的数据

**解决方法**：

```c
// 1. 删除后清空句柄
vTaskDelete(taskHandle);
taskHandle = NULL;

// 2. 删除前释放资源
void TaskWithResources(void *pvParameters)
{
    uint8_t *buffer = pvPortMalloc(1024);
    SemaphoreHandle_t sem = xSemaphoreCreateBinary();
    
    while(1)
    {
        if(ShouldExit())
        {
            // 释放所有资源
            vPortFree(buffer);
            vSemaphoreDelete(sem);
            
            // 删除自己
            vTaskDelete(NULL);
        }
        
        vTaskDelay(100);
    }
}

// 3. 使用标志位通知其他任务
volatile bool taskRunning = true;

void Task1(void *pvParameters)
{
    while(1)
    {
        if(ShouldExit())
        {
            taskRunning = false;  // 通知其他任务
            vTaskDelay(100);      // 等待其他任务响应
            vTaskDelete(NULL);
        }
        vTaskDelay(100);
    }
}

void Task2(void *pvParameters)
{
    while(1)
    {
        if(taskRunning)
        {
            // 访问Task1的数据
        }
        vTaskDelay(100);
    }
}
```

## 最佳实践

### 任务设计原则

1. **单一职责**：每个任务只负责一个功能模块
2. **合理优先级**：根据实时性要求分配优先级
3. **适当延时**：任务必须有延时或阻塞，避免占用CPU
4. **资源管理**：及时释放不再使用的资源
5. **错误处理**：检查API返回值，处理错误情况

### 栈大小配置建议

```c
// 开发阶段：使用较大的栈，启用栈溢出检测
#define configCHECK_FOR_STACK_OVERFLOW  2
xTaskCreate(Task, "Task", 512, NULL, 1, NULL);  // 较大的栈

// 测试阶段：监控栈使用情况
UBaseType_t stackMark = uxTaskGetStackHighWaterMark(taskHandle);
printf("Stack usage: %u words\n", 512 - stackMark);

// 发布阶段：根据实际使用情况优化栈大小
// 栈大小 = 实际使用 + 20%余量
xTaskCreate(Task, "Task", 256, NULL, 1, NULL);  // 优化后的栈
```

### 优先级分配建议

```c
// 优先级分配示例
#define PRIORITY_IDLE       0  // 空闲任务（系统保留）
#define PRIORITY_BACKGROUND 1  // 后台任务（日志、统计）
#define PRIORITY_LOW        2  // 低优先级（显示更新）
#define PRIORITY_NORMAL     3  // 普通优先级（数据处理）
#define PRIORITY_HIGH       4  // 高优先级（传感器采集）
#define PRIORITY_REALTIME   5  // 实时任务（中断后处理）

// 创建任务
xTaskCreate(LogTask, "Log", 256, NULL, PRIORITY_BACKGROUND, NULL);
xTaskCreate(DisplayTask, "Display", 256, NULL, PRIORITY_LOW, NULL);
xTaskCreate(ProcessTask, "Process", 512, NULL, PRIORITY_NORMAL, NULL);
xTaskCreate(SensorTask, "Sensor", 256, NULL, PRIORITY_HIGH, NULL);
xTaskCreate(UrgentTask, "Urgent", 256, NULL, PRIORITY_REALTIME, NULL);
```

### 任务命名建议

```c
// 好的命名：描述性强，易于理解
xTaskCreate(SensorReadTask, "SensorRead", 256, NULL, 2, NULL);
xTaskCreate(DataProcessTask, "DataProcess", 512, NULL, 3, NULL);
xTaskCreate(DisplayUpdateTask, "DisplayUpdate", 256, NULL, 1, NULL);
xTaskCreate(NetworkCommTask, "NetworkComm", 512, NULL, 4, NULL);

// 不好的命名：不够清晰
xTaskCreate(Task1, "T1", 256, NULL, 2, NULL);
xTaskCreate(Task2, "T2", 512, NULL, 3, NULL);
xTaskCreate(Task3, "T3", 256, NULL, 1, NULL);
```

## 总结

通过本教程，你学习了：

- ✅ FreeRTOS任务创建的两种方法（动态和静态）
- ✅ 任务创建API的所有参数及其详细用法
- ✅ 任务优先级的配置和动态调整
- ✅ 任务堆栈的管理和监控
- ✅ 任务的删除、挂起和恢复操作
- ✅ 任务状态查询和监控方法
- ✅ 任务参数传递的多种技巧
- ✅ 相对延时和绝对延时的区别
- ✅ 常见问题的排查和解决方法

### 关键要点

1. **任务创建**
   - 动态创建简单方便，适合一般应用
   - 静态创建无内存碎片，适合安全关键应用
   - 栈大小以"字"为单位，需要根据实际使用情况配置

2. **任务管理**
   - 任务可以删除自己或其他任务
   - 挂起的任务必须手动恢复
   - 优先级可以动态调整

3. **任务调度**
   - 高优先级任务优先执行
   - 相同优先级任务时间片轮转
   - 任务必须有延时或阻塞

4. **调试技巧**
   - 启用栈溢出检测
   - 监控栈使用情况
   - 使用任务状态查询API
   - 合理命名任务便于调试

## 下一步学习

建议按以下顺序继续学习：

### 1. 任务间通信
- [FreeRTOS队列通信实战](03-freertos-queue.html)
- 学习使用队列在任务间传递数据
- 理解阻塞和非阻塞通信

### 2. 同步机制
- [FreeRTOS信号量应用](04-freertos-semaphore.html)
- 学习二值信号量和计数信号量
- 理解互斥量和临界区保护

### 3. 高级特性
- [FreeRTOS软件定时器](../intermediate/01-freertos-timer.html)
- [FreeRTOS事件标志组](../intermediate/02-freertos-event-group.html)
- [FreeRTOS任务通知](../intermediate/03-freertos-notification.html)

### 4. 系统设计
- [基于FreeRTOS的多任务系统设计](../advanced/01-freertos-system-design.html)
- 学习完整的系统架构设计
- 掌握任务划分和资源管理


## 参考资料

### 官方文档

1. **FreeRTOS官方网站**
   - https://www.freertos.org/
   - 完整的API文档和参考手册

2. **FreeRTOS任务管理API**
   - https://www.freertos.org/a00019.html
   - 所有任务管理函数的详细说明

3. **FreeRTOS参考手册**
   - https://www.freertos.org/Documentation/RTOS_book.html
   - 《Mastering the FreeRTOS Real Time Kernel》免费下载

### 推荐书籍

1. **《Mastering the FreeRTOS Real Time Kernel》**
   - FreeRTOS作者Richard Barry编写
   - 详细讲解任务管理和调度原理
   - 免费下载：https://www.freertos.org/Documentation/RTOS_book.html

2. **《嵌入式实时操作系统FreeRTOS原理与实践》**
   - 中文书籍，适合入门
   - 包含大量实例和项目

### 在线资源

1. **FreeRTOS论坛**
   - https://forums.freertos.org/
   - 活跃的社区支持
   - 可以提问和交流

2. **STM32社区**
   - https://community.st.com/
   - ST官方技术支持
   - FreeRTOS相关讨论

3. **GitHub示例代码**
   - https://github.com/FreeRTOS/FreeRTOS
   - 官方示例和Demo
   - 各种平台的移植代码

### API快速参考

**任务创建和删除**：
```c
BaseType_t xTaskCreate(TaskFunction_t, const char*, uint16_t, void*, UBaseType_t, TaskHandle_t*);
TaskHandle_t xTaskCreateStatic(TaskFunction_t, const char*, uint32_t, void*, UBaseType_t, StackType_t*, StaticTask_t*);
void vTaskDelete(TaskHandle_t);
```

**任务挂起和恢复**：
```c
void vTaskSuspend(TaskHandle_t);
void vTaskResume(TaskHandle_t);
BaseType_t xTaskResumeFromISR(TaskHandle_t);
```

**任务优先级**：
```c
UBaseType_t uxTaskPriorityGet(TaskHandle_t);
void vTaskPrioritySet(TaskHandle_t, UBaseType_t);
```

**任务延时**：
```c
void vTaskDelay(TickType_t);
void vTaskDelayUntil(TickType_t*, TickType_t);
```

**任务信息查询**：
```c
TaskHandle_t xTaskGetHandle(const char*);
TaskHandle_t xTaskGetCurrentTaskHandle(void);
char* pcTaskGetName(TaskHandle_t);
eTaskState eTaskGetState(TaskHandle_t);
UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t);
```

## 常见问题解答

### Q1: 任务栈大小应该设置多大？

**A**: 栈大小取决于任务的复杂度：
- 简单任务（LED闪烁）：128-256字（512-1024字节）
- 中等任务（数据处理）：256-512字（1024-2048字节）
- 复杂任务（网络通信）：512-1024字（2048-4096字节）

建议：
1. 开发阶段使用较大的栈
2. 启用栈溢出检测
3. 使用`uxTaskGetStackHighWaterMark()`监控栈使用
4. 根据实际使用情况优化

### Q2: 如何选择合适的任务优先级？

**A**: 优先级分配原则：
1. 实时性要求高的任务：高优先级
2. 周期性任务：中等优先级
3. 后台任务：低优先级
4. 避免过多任务使用相同优先级

示例：
- 中断后处理：优先级5
- 传感器采集：优先级4
- 数据处理：优先级3
- 显示更新：优先级2
- 日志记录：优先级1

### Q3: 任务函数可以返回吗？

**A**: 不可以。任务函数必须是无限循环，永远不应该返回。

```c
// ❌ 错误：任务函数返回
void Task(void *pvParameters)
{
    DoWork();
    return;  // 错误！
}

// ✅ 正确：无限循环
void Task(void *pvParameters)
{
    while(1)
    {
        DoWork();
        vTaskDelay(100);
    }
}

// ✅ 正确：需要退出时删除自己
void Task(void *pvParameters)
{
    DoWork();
    vTaskDelete(NULL);  // 删除自己
}
```

### Q4: 动态创建和静态创建有什么区别？

**A**: 主要区别：

| 特性 | 动态创建 | 静态创建 |
|------|---------|---------|
| 内存分配 | 从堆中分配 | 使用预定义内存 |
| 内存碎片 | 可能产生 | 不会产生 |
| 灵活性 | 高 | 低 |
| 适用场景 | 一般应用 | 安全关键应用 |

建议：
- 一般应用使用动态创建
- 安全关键应用使用静态创建
- 资源受限系统使用静态创建

### Q5: 如何调试任务栈溢出？

**A**: 步骤：

1. 启用栈溢出检测：
```c
#define configCHECK_FOR_STACK_OVERFLOW  2
```

2. 实现钩子函数：
```c
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    printf("Stack overflow: %s\n", pcTaskName);
    while(1);
}
```

3. 监控栈使用：
```c
UBaseType_t mark = uxTaskGetStackHighWaterMark(taskHandle);
printf("Stack free: %u words\n", mark);
```

4. 增加栈大小或优化代码

### Q6: 任务之间如何通信？

**A**: FreeRTOS提供多种通信机制：
- **队列**：传递数据
- **信号量**：同步和互斥
- **事件标志组**：多事件同步
- **任务通知**：轻量级通信
- **互斥量**：保护共享资源

详见后续教程：
- [FreeRTOS队列通信](03-freertos-queue.html)
- [FreeRTOS信号量应用](04-freertos-semaphore.html)

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

