---
title: "RTOS任务管理基础：创建和管理多任务系统"
description: "深入学习RTOS任务管理的核心概念和实践技巧。掌握任务创建、任务状态转换、任务优先级、任务删除和挂起恢复等关键技术，通过丰富的代码示例学会构建稳定可靠的多任务嵌入式系统。"
slug: "rtos-task-management"

# 分类信息
domain: "操作系统层"
module: "RTOS基础"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 任务管理
  - RTOS任务
  - 多任务
  - 任务调度
  - FreeRTOS
prerequisites:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/01-rtos-overview.md"
  - "03-operating-system-layer/01-bare-metal-programming/beginner/01-bare-metal-basics.md"
related_contents:
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/03-rtos-scheduling.md"
  - "03-operating-system-layer/02-rtos-fundamentals/beginner/04-semaphore.md"
  - "03-operating-system-layer/03-freertos/beginner/02-freertos-tasks.md"

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
  - RTOS任务管理
  - 任务创建
  - 任务状态
  - 任务优先级
  - 多任务编程
cover_image: ""
---


# RTOS任务管理基础：创建和管理多任务系统

## 概述

任务(Task)是RTOS中最基本的执行单元，理解任务管理是掌握RTOS的关键。本教程将带你深入学习RTOS任务管理的核心概念和实践技巧。完成本教程后，你将能够：

- 理解任务的概念和特点
- 掌握任务创建的方法和参数配置
- 理解任务的五种状态及其转换关系
- 学会使用任务管理API进行任务控制
- 掌握任务优先级的设置和影响
- 学会任务的删除、挂起和恢复操作
- 理解任务栈的作用和配置方法

## 背景知识

### 什么是任务？

在RTOS中，**任务(Task)**是一个独立的执行单元，类似于一个"小程序"，它有自己的执行流程和栈空间。

**任务的特点**：
- **独立性**：每个任务有独立的栈空间和上下文
- **并发性**：多个任务可以"同时"运行（实际是快速切换）
- **优先级**：每个任务有优先级，高优先级任务优先执行
- **状态**：任务在不同状态间转换（运行、就绪、阻塞等）

**任务 vs 函数**：

```c
// 普通函数：执行完就返回
void LED_Blink(void) {
    GPIO_Toggle(LED_PIN);
    Delay_ms(500);
}

// RTOS任务：永不返回的无限循环
void LED_Task(void *param) {
    while(1) {  // 永不退出的循环
        GPIO_Toggle(LED_PIN);
        vTaskDelay(pdMS_TO_TICKS(500));  // RTOS延时
    }
}
```

### 为什么需要任务管理？

在复杂的嵌入式系统中，通常需要同时处理多个功能：

**示例场景**：智能温控系统
- **任务1**：每秒读取温度传感器
- **任务2**：每100ms检测按键输入
- **任务3**：每500ms更新LCD显示
- **任务4**：实时响应报警事件

如果用裸机编程，需要手动管理这些任务的时序和切换，非常复杂。而RTOS的任务管理机制可以自动处理这些问题。

### 相关概念

**任务控制块(TCB - Task Control Block)**：
- 存储任务的所有信息（栈指针、优先级、状态等）
- 由RTOS内核自动管理

**任务栈(Task Stack)**：
- 每个任务独立的栈空间
- 用于保存局部变量、函数调用和上下文

**任务句柄(Task Handle)**：
- 任务的唯一标识符
- 用于操作和控制任务

**调度器(Scheduler)**：
- RTOS的核心组件
- 决定哪个任务应该运行


## 核心内容

### 任务的五种状态

RTOS中的任务在生命周期内会经历不同的状态：


#### 1. 运行态(Running)

**定义**：任务正在CPU上执行。

**特点**：
- 在单核系统中，同一时刻只有一个任务处于运行态
- 任务正在执行其代码
- 占用CPU资源

```c
void Task_Example(void *param) {
    while(1) {
        // 此时任务处于运行态
        int result = Calculate();  // 正在执行
        printf("Result: %d\n", result);
        
        vTaskDelay(100);  // 主动让出CPU，进入阻塞态
    }
}
```

#### 2. 就绪态(Ready)

**定义**：任务准备好运行，等待调度器分配CPU。

**特点**：
- 任务具备运行条件，但CPU被其他任务占用
- 在就绪队列中等待
- 调度器会选择最高优先级的就绪任务运行

```c
// 场景：两个相同优先级的任务
void Task1(void *param) {
    while(1) {
        printf("Task1 running\n");  // Task1运行态
        // Task2此时处于就绪态
        vTaskDelay(100);
    }
}

void Task2(void *param) {
    while(1) {
        printf("Task2 running\n");  // Task2运行态
        // Task1此时处于就绪态
        vTaskDelay(100);
    }
}
```

#### 3. 阻塞态(Blocked)

**定义**：任务等待某个事件或时间，暂时不能运行。

**常见阻塞原因**：
- 延时等待（`vTaskDelay()`）
- 等待信号量（`xSemaphoreTake()`）
- 等待队列数据（`xQueueReceive()`）
- 等待事件标志（`xEventGroupWaitBits()`）

```c
void Sensor_Task(void *param) {
    while(1) {
        // 等待信号量，进入阻塞态
        if(xSemaphoreTake(sensor_sem, pdMS_TO_TICKS(1000)) == pdTRUE) {
            // 获得信号量，返回就绪态/运行态
            ReadSensor();
        }
    }
}

void Display_Task(void *param) {
    while(1) {
        UpdateDisplay();
        // 延时500ms，进入阻塞态
        vTaskDelay(pdMS_TO_TICKS(500));
        // 延时结束，返回就绪态
    }
}
```

#### 4. 挂起态(Suspended)

**定义**：任务被显式挂起，不参与调度。

**特点**：
- 通过`vTaskSuspend()`挂起
- 通过`vTaskResume()`恢复
- 不会自动恢复，必须手动恢复

```c
TaskHandle_t task_handle;

void Worker_Task(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);
    }
}

void Control_Task(void *param) {
    while(1) {
        if(Button_Pressed()) {
            // 挂起工作任务
            vTaskSuspend(task_handle);
            printf("Task suspended\n");
        }
        
        if(Button_Released()) {
            // 恢复工作任务
            vTaskResume(task_handle);
            printf("Task resumed\n");
        }
        
        vTaskDelay(10);
    }
}
```

#### 5. 删除态(Deleted)

**定义**：任务被删除，不再存在。

**特点**：
- 任务的TCB和栈被释放
- 任务永久消失，无法恢复
- 可以删除自己或其他任务

```c
void Temporary_Task(void *param) {
    // 执行一次性任务
    InitializeSystem();
    
    // 任务完成后删除自己
    vTaskDelete(NULL);  // NULL表示删除当前任务
    
    // 永远不会执行到这里
    while(1);
}
```

#### 任务状态转换图

```
        创建
         ↓
    ┌─────────┐
    │ 就绪态  │←──────────────┐
    │ Ready   │                │
    └─────────┘                │
         ↓ 调度器选中          │ 事件发生/延时到期
         ↓                     │
    ┌─────────┐                │
    │ 运行态  │                │
    │ Running │                │
    └─────────┘                │
         ↓ 等待事件/延时       │
         ↓                     │
    ┌─────────┐                │
    │ 阻塞态  │────────────────┘
    │ Blocked │
    └─────────┘
         ↓ vTaskSuspend()
         ↓
    ┌─────────┐
    │ 挂起态  │
    │Suspended│
    └─────────┘
         ↓ vTaskDelete()
         ↓
    ┌─────────┐
    │ 删除态  │
    │ Deleted │
    └─────────┘
```

### 任务创建

#### 动态创建任务

使用`xTaskCreate()`动态创建任务（从堆中分配内存）：

```c
BaseType_t xTaskCreate(
    TaskFunction_t pvTaskCode,      // 任务函数指针
    const char * const pcName,      // 任务名称（用于调试）
    uint16_t usStackDepth,          // 栈大小（字为单位）
    void *pvParameters,             // 传递给任务的参数
    UBaseType_t uxPriority,         // 任务优先级
    TaskHandle_t *pxCreatedTask     // 任务句柄（可选）
);
```

**完整示例**：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务句柄
TaskHandle_t led_task_handle = NULL;

// LED任务函数
void LED_Task(void *param) {
    // param是传入的参数
    uint32_t delay_ms = (uint32_t)param;
    
    while(1) {
        GPIO_Toggle(LED_PIN);
        printf("LED Task running\n");
        vTaskDelay(pdMS_TO_TICKS(delay_ms));
    }
}

int main(void) {
    SystemInit();
    
    // 创建LED任务
    BaseType_t result = xTaskCreate(
        LED_Task,              // 任务函数
        "LED",                 // 任务名称
        128,                   // 栈大小：128字（512字节）
        (void *)500,           // 参数：延时500ms
        2,                     // 优先级：2
        &led_task_handle       // 保存任务句柄
    );
    
    if(result == pdPASS) {
        printf("Task created successfully\n");
        
        // 启动调度器
        vTaskStartScheduler();
    } else {
        printf("Task creation failed\n");
    }
    
    // 永远不会执行到这里
    while(1);
}
```


**参数详解**：

1. **任务函数(pvTaskCode)**：
```c
// 任务函数必须是无限循环，永不返回
void Task_Function(void *param) {
    // 初始化代码（只执行一次）
    InitializeHardware();
    
    // 主循环（永远执行）
    while(1) {
        // 任务代码
        DoWork();
        
        // 必须有延时或阻塞，否则会一直占用CPU
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    // 如果任务需要退出，应该删除自己
    // vTaskDelete(NULL);
}
```

2. **任务名称(pcName)**：
```c
// 任务名称用于调试，最大长度由configMAX_TASK_NAME_LEN定义
xTaskCreate(Task1, "Sensor", 128, NULL, 1, NULL);    // 好的命名
xTaskCreate(Task2, "T2", 128, NULL, 1, NULL);        // 不推荐
```

3. **栈大小(usStackDepth)**：
```c
// 单位是字(word)，不是字节
// Cortex-M系列：1字 = 4字节
// 栈大小 = usStackDepth × 4 字节

xTaskCreate(Task, "Task", 128, NULL, 1, NULL);  // 128字 = 512字节
xTaskCreate(Task, "Task", 256, NULL, 1, NULL);  // 256字 = 1024字节

// 栈大小建议：
// 简单任务（LED闪烁）：128-256字（512-1024字节）
// 普通任务（数据处理）：256-512字（1024-2048字节）
// 复杂任务（网络通信）：512-1024字（2048-4096字节）
```

4. **任务参数(pvParameters)**：
```c
// 可以传递任何类型的参数
// 方法1：传递简单值
xTaskCreate(Task, "Task", 128, (void *)100, 1, NULL);  // 传递整数

// 方法2：传递指针
typedef struct {
    uint32_t sensor_id;
    uint32_t interval;
} TaskParam_t;

TaskParam_t param = {.sensor_id = 1, .interval = 1000};
xTaskCreate(Task, "Task", 128, &param, 1, NULL);  // 传递结构体指针

// 在任务中接收参数
void Task(void *param) {
    TaskParam_t *p = (TaskParam_t *)param;
    printf("Sensor ID: %d, Interval: %d\n", p->sensor_id, p->interval);
    while(1) {
        vTaskDelay(p->interval);
    }
}
```

5. **任务优先级(uxPriority)**：
```c
// 优先级范围：0 到 (configMAX_PRIORITIES - 1)
// 数字越大，优先级越高
// 0是最低优先级，通常保留给空闲任务

#define PRIORITY_IDLE       0  // 空闲任务（系统保留）
#define PRIORITY_LOW        1  // 低优先级
#define PRIORITY_NORMAL     2  // 普通优先级
#define PRIORITY_HIGH       3  // 高优先级
#define PRIORITY_CRITICAL   4  // 关键任务

xTaskCreate(BackgroundTask, "BG", 128, NULL, PRIORITY_LOW, NULL);
xTaskCreate(NormalTask, "Normal", 256, NULL, PRIORITY_NORMAL, NULL);
xTaskCreate(CriticalTask, "Critical", 512, NULL, PRIORITY_CRITICAL, NULL);
```

6. **任务句柄(pxCreatedTask)**：
```c
// 保存任务句柄，用于后续操作任务
TaskHandle_t task_handle;

xTaskCreate(Task, "Task", 128, NULL, 1, &task_handle);

// 使用句柄操作任务
vTaskSuspend(task_handle);   // 挂起任务
vTaskResume(task_handle);    // 恢复任务
vTaskDelete(task_handle);    // 删除任务
```

#### 静态创建任务

使用`xTaskCreateStatic()`静态创建任务（使用预分配的内存）：

```c
// 需要在FreeRTOSConfig.h中启用
#define configSUPPORT_STATIC_ALLOCATION  1

// 定义任务栈（静态分配）
#define TASK_STACK_SIZE  128
static StackType_t task_stack[TASK_STACK_SIZE];

// 定义任务控制块（静态分配）
static StaticTask_t task_tcb;

void Task_Function(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);
    }
}

int main(void) {
    // 静态创建任务
    TaskHandle_t task_handle = xTaskCreateStatic(
        Task_Function,      // 任务函数
        "Task",             // 任务名称
        TASK_STACK_SIZE,    // 栈大小
        NULL,               // 参数
        2,                  // 优先级
        task_stack,         // 栈数组
        &task_tcb           // TCB
    );
    
    if(task_handle != NULL) {
        vTaskStartScheduler();
    }
    
    while(1);
}
```

**动态 vs 静态创建对比**：

| 特性 | 动态创建 | 静态创建 |
|------|---------|---------|
| **内存分配** | 从堆中分配 | 使用预定义的静态内存 |
| **灵活性** | 高（运行时创建） | 低（编译时确定） |
| **内存碎片** | 可能产生碎片 | 无碎片问题 |
| **内存使用** | 需要堆空间 | 不需要堆 |
| **适用场景** | 一般应用 | 安全关键应用 |
| **代码复杂度** | 简单 | 稍复杂 |

### 任务删除

#### 删除自己

```c
void Temporary_Task(void *param) {
    // 执行一次性初始化
    printf("Initializing...\n");
    InitializeSystem();
    printf("Initialization complete\n");
    
    // 删除自己
    vTaskDelete(NULL);  // NULL表示删除当前任务
    
    // 永远不会执行到这里
    printf("This will never print\n");
}

int main(void) {
    // 创建临时任务
    xTaskCreate(Temporary_Task, "Init", 256, NULL, 1, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

#### 删除其他任务

```c
TaskHandle_t worker_task_handle;

void Worker_Task(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);
    }
}

void Manager_Task(void *param) {
    while(1) {
        if(WorkCompleted()) {
            // 删除工作任务
            vTaskDelete(worker_task_handle);
            worker_task_handle = NULL;
            printf("Worker task deleted\n");
        }
        
        vTaskDelay(1000);
    }
}

int main(void) {
    // 创建工作任务
    xTaskCreate(Worker_Task, "Worker", 256, NULL, 1, &worker_task_handle);
    
    // 创建管理任务
    xTaskCreate(Manager_Task, "Manager", 256, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**注意事项**：

```c
// ❌ 错误：删除后继续使用句柄
vTaskDelete(task_handle);
vTaskResume(task_handle);  // 错误！任务已被删除

// ✅ 正确：删除后清空句柄
vTaskDelete(task_handle);
task_handle = NULL;

// ✅ 正确：删除前检查句柄
if(task_handle != NULL) {
    vTaskDelete(task_handle);
    task_handle = NULL;
}
```

### 任务挂起和恢复

#### 挂起任务

```c
TaskHandle_t task_handle;

// 挂起指定任务
vTaskSuspend(task_handle);

// 挂起自己
vTaskSuspend(NULL);
```

#### 恢复任务

```c
// 从任务中恢复
vTaskResume(task_handle);

// 从中断中恢复（ISR安全版本）
BaseType_t xHigherPriorityTaskWoken = pdFALSE;
xTaskResumeFromISR(task_handle);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
```

#### 实际应用示例

```c
TaskHandle_t data_task_handle;
TaskHandle_t display_task_handle;

// 数据处理任务
void Data_Task(void *param) {
    while(1) {
        ProcessData();
        vTaskDelay(100);
    }
}

// 显示任务
void Display_Task(void *param) {
    while(1) {
        UpdateDisplay();
        vTaskDelay(500);
    }
}

// 控制任务
void Control_Task(void *param) {
    bool system_active = true;
    
    while(1) {
        if(Button_Pressed()) {
            system_active = !system_active;
            
            if(system_active) {
                // 恢复所有任务
                vTaskResume(data_task_handle);
                vTaskResume(display_task_handle);
                printf("System resumed\n");
            } else {
                // 挂起所有任务
                vTaskSuspend(data_task_handle);
                vTaskSuspend(display_task_handle);
                printf("System suspended\n");
            }
        }
        
        vTaskDelay(10);
    }
}

int main(void) {
    SystemInit();
    
    // 创建任务
    xTaskCreate(Data_Task, "Data", 256, NULL, 2, &data_task_handle);
    xTaskCreate(Display_Task, "Display", 256, NULL, 1, &display_task_handle);
    xTaskCreate(Control_Task, "Control", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```


### 任务优先级

#### 优先级的作用

RTOS根据任务优先级进行调度：
- **高优先级任务**优先获得CPU
- **相同优先级任务**轮流执行（时间片轮转）
- **低优先级任务**在高优先级任务阻塞时才能运行

```c
// 优先级示例
#define PRIORITY_CRITICAL   5  // 最高优先级
#define PRIORITY_HIGH       4
#define PRIORITY_NORMAL     3
#define PRIORITY_LOW        2
#define PRIORITY_IDLE       1  // 最低优先级

// 创建不同优先级的任务
xTaskCreate(CriticalTask, "Critical", 256, NULL, PRIORITY_CRITICAL, NULL);
xTaskCreate(HighTask, "High", 256, NULL, PRIORITY_HIGH, NULL);
xTaskCreate(NormalTask, "Normal", 256, NULL, PRIORITY_NORMAL, NULL);
xTaskCreate(LowTask, "Low", 256, NULL, PRIORITY_LOW, NULL);
```

#### 优先级调度示例

```c
// 高优先级任务
void High_Priority_Task(void *param) {
    while(1) {
        printf("High priority task running\n");
        // 高优先级任务运行时，低优先级任务无法运行
        vTaskDelay(pdMS_TO_TICKS(1000));
        // 延时期间，低优先级任务可以运行
    }
}

// 低优先级任务
void Low_Priority_Task(void *param) {
    while(1) {
        printf("Low priority task running\n");
        // 只有在高优先级任务阻塞时才能运行
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

int main(void) {
    xTaskCreate(High_Priority_Task, "High", 128, NULL, 3, NULL);
    xTaskCreate(Low_Priority_Task, "Low", 128, NULL, 1, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**执行时序**：
```
时间轴：
0ms    1000ms  1100ms  2000ms  2100ms  3000ms
|------|------|------|------|------|------|
高优先级任务运行
|██████|      |██████|      |██████|
      ↓ 延时  ↓      ↓ 延时  ↓      ↓ 延时
      低优先级任务运行
      |██████|      |██████|      |██████|
```

#### 动态修改优先级

```c
TaskHandle_t task_handle;

// 获取任务优先级
UBaseType_t priority = uxTaskPriorityGet(task_handle);
printf("Current priority: %d\n", priority);

// 设置任务优先级
vTaskPrioritySet(task_handle, 5);  // 设置为优先级5

// 提升自己的优先级
vTaskPrioritySet(NULL, uxTaskPriorityGet(NULL) + 1);

// 降低自己的优先级
vTaskPrioritySet(NULL, uxTaskPriorityGet(NULL) - 1);
```

**实际应用**：

```c
TaskHandle_t worker_task_handle;

void Worker_Task(void *param) {
    while(1) {
        // 普通工作
        DoNormalWork();
        vTaskDelay(100);
    }
}

void Manager_Task(void *param) {
    while(1) {
        if(EmergencyDetected()) {
            // 紧急情况：提升工作任务优先级
            vTaskPrioritySet(worker_task_handle, PRIORITY_CRITICAL);
            printf("Priority elevated to critical\n");
        }
        
        if(EmergencyCleared()) {
            // 恢复正常优先级
            vTaskPrioritySet(worker_task_handle, PRIORITY_NORMAL);
            printf("Priority restored to normal\n");
        }
        
        vTaskDelay(10);
    }
}
```

### 任务栈管理

#### 栈的作用

每个任务都有独立的栈空间，用于：
- 保存局部变量
- 保存函数调用信息
- 保存任务上下文（寄存器）

```c
void Task_Example(void *param) {
    // 这些局部变量存储在任务栈中
    uint32_t counter = 0;
    char buffer[64];
    float temperature;
    
    while(1) {
        // 函数调用也使用栈空间
        ReadSensor(&temperature);
        sprintf(buffer, "Temp: %.1f", temperature);
        
        counter++;
        vTaskDelay(1000);
    }
}
```

#### 栈大小配置

```c
// 栈大小建议（单位：字，1字=4字节）

// 最小任务（只有简单循环）
xTaskCreate(Task, "Task", 64, NULL, 1, NULL);   // 64字 = 256字节

// 小任务（LED闪烁、简单IO）
xTaskCreate(Task, "Task", 128, NULL, 1, NULL);  // 128字 = 512字节

// 中等任务（数据处理、串口通信）
xTaskCreate(Task, "Task", 256, NULL, 1, NULL);  // 256字 = 1024字节

// 大任务（网络通信、文件操作）
xTaskCreate(Task, "Task", 512, NULL, 1, NULL);  // 512字 = 2048字节

// 超大任务（复杂算法、大缓冲区）
xTaskCreate(Task, "Task", 1024, NULL, 1, NULL); // 1024字 = 4096字节
```

**影响栈大小的因素**：

```c
void Task_With_Large_Stack(void *param) {
    // 1. 局部变量
    char large_buffer[1024];  // 需要1KB栈空间
    
    // 2. 函数调用深度
    Function1();  // 每次调用需要额外栈空间
    
    // 3. 中断嵌套
    // 中断发生时会使用任务栈保存上下文
    
    while(1) {
        vTaskDelay(100);
    }
}

void Function1(void) {
    char buffer[256];  // 额外256字节
    Function2();       // 更深的调用
}

void Function2(void) {
    char buffer[128];  // 再额外128字节
    DoWork();
}
```

#### 栈溢出检测

FreeRTOS提供栈溢出检测机制：

```c
// 在FreeRTOSConfig.h中配置
#define configCHECK_FOR_STACK_OVERFLOW  2  // 启用栈溢出检测

// 栈溢出钩子函数（必须实现）
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // 栈溢出时会调用此函数
    printf("Stack overflow in task: %s\n", pcTaskName);
    
    // 处理栈溢出
    // 1. 记录错误
    // 2. 重启系统
    // 3. 进入安全模式
    
    while(1) {
        // 停止系统
    }
}
```

**检测方法**：

```c
// 方法1：检查栈水位（最小剩余栈空间）
UBaseType_t stack_high_water_mark = uxTaskGetStackHighWaterMark(task_handle);
printf("Minimum free stack: %d words (%d bytes)\n", 
       stack_high_water_mark, 
       stack_high_water_mark * 4);

// 如果水位太低，说明栈空间不足
if(stack_high_water_mark < 32) {  // 少于128字节
    printf("Warning: Stack space is low!\n");
}

// 方法2：在任务中定期检查
void Monitor_Task(void *param) {
    while(1) {
        // 检查所有任务的栈使用情况
        UBaseType_t stack_mark = uxTaskGetStackHighWaterMark(NULL);
        printf("Current task stack free: %d words\n", stack_mark);
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
```

### 任务管理API总结

#### 创建和删除

```c
// 动态创建任务
BaseType_t xTaskCreate(TaskFunction_t pvTaskCode,
                       const char * const pcName,
                       uint16_t usStackDepth,
                       void *pvParameters,
                       UBaseType_t uxPriority,
                       TaskHandle_t *pxCreatedTask);

// 静态创建任务
TaskHandle_t xTaskCreateStatic(TaskFunction_t pvTaskCode,
                               const char * const pcName,
                               uint32_t ulStackDepth,
                               void *pvParameters,
                               UBaseType_t uxPriority,
                               StackType_t * const puxStackBuffer,
                               StaticTask_t * const pxTaskBuffer);

// 删除任务
void vTaskDelete(TaskHandle_t xTask);  // NULL表示删除自己
```

#### 挂起和恢复

```c
// 挂起任务
void vTaskSuspend(TaskHandle_t xTaskToSuspend);  // NULL表示挂起自己

// 恢复任务
void vTaskResume(TaskHandle_t xTaskToResume);

// 从中断中恢复任务
BaseType_t xTaskResumeFromISR(TaskHandle_t xTaskToResume);
```

#### 优先级管理

```c
// 获取任务优先级
UBaseType_t uxTaskPriorityGet(TaskHandle_t xTask);  // NULL表示当前任务

// 设置任务优先级
void vTaskPrioritySet(TaskHandle_t xTask, UBaseType_t uxNewPriority);
```

#### 延时函数

```c
// 相对延时（从调用时刻开始计时）
void vTaskDelay(TickType_t xTicksToDelay);

// 绝对延时（精确的周期性延时）
void vTaskDelayUntil(TickType_t *pxPreviousWakeTime, TickType_t xTimeIncrement);
```

#### 任务信息查询

```c
// 获取任务句柄（通过名称）
TaskHandle_t xTaskGetHandle(const char *pcNameToQuery);

// 获取当前任务句柄
TaskHandle_t xTaskGetCurrentTaskHandle(void);

// 获取任务名称
char *pcTaskGetName(TaskHandle_t xTaskToQuery);

// 获取任务状态
eTaskState eTaskGetState(TaskHandle_t xTask);

// 获取栈水位（最小剩余栈空间）
UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t xTask);
```

## 适用场景分析

### 何时创建新任务？

**推荐创建新任务的场景**：

1. **独立的功能模块**
```c
// 每个功能模块一个任务
xTaskCreate(Sensor_Task, "Sensor", 256, NULL, 2, NULL);      // 传感器采集
xTaskCreate(Display_Task, "Display", 256, NULL, 1, NULL);    // 显示更新
xTaskCreate(Network_Task, "Network", 512, NULL, 3, NULL);    // 网络通信
```

2. **不同的时序要求**
```c
// 不同更新频率的任务
xTaskCreate(Fast_Task, "Fast", 128, NULL, 3, NULL);    // 10ms更新
xTaskCreate(Medium_Task, "Medium", 256, NULL, 2, NULL); // 100ms更新
xTaskCreate(Slow_Task, "Slow", 256, NULL, 1, NULL);     // 1s更新
```

3. **不同的优先级需求**
```c
// 关键任务需要高优先级
xTaskCreate(Critical_Task, "Critical", 256, NULL, 5, NULL);  // 紧急响应
xTaskCreate(Normal_Task, "Normal", 256, NULL, 2, NULL);      // 普通处理
xTaskCreate(Background_Task, "BG", 256, NULL, 1, NULL);      // 后台任务
```

**不推荐创建新任务的场景**：

1. **简单的周期性操作**
```c
// ❌ 不好：为简单操作创建任务
void LED_Task(void *param) {
    while(1) {
        GPIO_Toggle(LED_PIN);
        vTaskDelay(500);
    }
}

// ✅ 更好：在现有任务中处理
void Main_Task(void *param) {
    uint32_t led_counter = 0;
    while(1) {
        // 主要工作
        DoMainWork();
        
        // 顺便处理LED
        if(++led_counter >= 5) {  // 每5次循环切换一次
            led_counter = 0;
            GPIO_Toggle(LED_PIN);
        }
        
        vTaskDelay(100);
    }
}
```

2. **资源受限的系统**
```c
// 每个任务需要栈空间和TCB
// 如果RAM不足，应该减少任务数量
// 使用状态机或事件驱动代替多任务
```


## 实践示例

### 示例1：多任务LED控制系统

创建一个系统，同时控制三个LED以不同频率闪烁：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "stm32f1xx_hal.h"

// LED任务函数
void LED_Task(void *param) {
    // 从参数中获取LED配置
    typedef struct {
        GPIO_TypeDef *port;
        uint16_t pin;
        uint32_t delay_ms;
    } LED_Config_t;
    
    LED_Config_t *config = (LED_Config_t *)param;
    
    while(1) {
        // 切换LED状态
        HAL_GPIO_TogglePin(config->port, config->pin);
        
        // 延时
        vTaskDelay(pdMS_TO_TICKS(config->delay_ms));
    }
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化GPIO
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    
    // LED1 - PC13
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // LED2 - PC14
    GPIO_InitStruct.Pin = GPIO_PIN_14;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // LED3 - PC15
    GPIO_InitStruct.Pin = GPIO_PIN_15;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // LED配置
    static LED_Config_t led1_config = {GPIOC, GPIO_PIN_13, 500};   // 500ms
    static LED_Config_t led2_config = {GPIOC, GPIO_PIN_14, 1000};  // 1s
    static LED_Config_t led3_config = {GPIOC, GPIO_PIN_15, 2000};  // 2s
    
    // 创建三个LED任务
    xTaskCreate(LED_Task, "LED1", 128, &led1_config, 1, NULL);
    xTaskCreate(LED_Task, "LED2", 128, &led2_config, 1, NULL);
    xTaskCreate(LED_Task, "LED3", 128, &led3_config, 1, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    // 永远不会执行到这里
    while(1);
}
```

**运行效果**：
- LED1每500ms闪烁一次
- LED2每1秒闪烁一次
- LED3每2秒闪烁一次
- 三个LED独立运行，互不干扰

### 示例2：传感器数据采集系统

创建一个多任务传感器系统，包含采集、处理和显示任务：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 传感器数据结构
typedef struct {
    uint32_t timestamp;
    float temperature;
    float humidity;
} SensorData_t;

// 队列句柄
QueueHandle_t sensor_queue;

// 传感器采集任务（高优先级）
void Sensor_Task(void *param) {
    SensorData_t data;
    
    while(1) {
        // 读取传感器
        data.timestamp = HAL_GetTick();
        data.temperature = ReadTemperatureSensor();
        data.humidity = ReadHumiditySensor();
        
        // 发送到队列
        if(xQueueSend(sensor_queue, &data, pdMS_TO_TICKS(100)) != pdPASS) {
            printf("Queue full, data lost!\n");
        }
        
        // 每秒采集一次
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 数据处理任务（中优先级）
void Process_Task(void *param) {
    SensorData_t received_data;
    
    while(1) {
        // 从队列接收数据
        if(xQueueReceive(sensor_queue, &received_data, portMAX_DELAY) == pdPASS) {
            // 处理数据
            printf("[%d] Temp: %.1f°C, Humidity: %.1f%%\n",
                   received_data.timestamp,
                   received_data.temperature,
                   received_data.humidity);
            
            // 检查异常
            if(received_data.temperature > 30.0f) {
                printf("Warning: High temperature!\n");
            }
            
            if(received_data.humidity > 80.0f) {
                printf("Warning: High humidity!\n");
            }
            
            // 保存到存储器
            SaveToStorage(&received_data);
        }
    }
}

// 显示任务（低优先级）
void Display_Task(void *param) {
    while(1) {
        // 更新LCD显示
        UpdateLCD();
        
        // 每500ms更新一次
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 监控任务（最低优先级）
void Monitor_Task(void *param) {
    while(1) {
        // 检查系统状态
        printf("\n=== System Status ===\n");
        printf("Free heap: %d bytes\n", xPortGetFreeHeapSize());
        
        // 检查各任务栈使用情况
        TaskHandle_t sensor_handle = xTaskGetHandle("Sensor");
        TaskHandle_t process_handle = xTaskGetHandle("Process");
        TaskHandle_t display_handle = xTaskGetHandle("Display");
        
        printf("Sensor task stack: %d words free\n", 
               uxTaskGetStackHighWaterMark(sensor_handle));
        printf("Process task stack: %d words free\n", 
               uxTaskGetStackHighWaterMark(process_handle));
        printf("Display task stack: %d words free\n", 
               uxTaskGetStackHighWaterMark(display_handle));
        
        // 每10秒检查一次
        vTaskDelay(pdMS_TO_TICKS(10000));
    }
}

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 创建队列（可以存储10个数据）
    sensor_queue = xQueueCreate(10, sizeof(SensorData_t));
    
    if(sensor_queue != NULL) {
        // 创建任务（优先级从高到低）
        xTaskCreate(Sensor_Task, "Sensor", 256, NULL, 4, NULL);   // 最高优先级
        xTaskCreate(Process_Task, "Process", 512, NULL, 3, NULL); // 高优先级
        xTaskCreate(Display_Task, "Display", 256, NULL, 2, NULL); // 中优先级
        xTaskCreate(Monitor_Task, "Monitor", 256, NULL, 1, NULL); // 低优先级
        
        // 启动调度器
        vTaskStartScheduler();
    }
    
    while(1);
}
```

### 示例3：任务动态管理

演示任务的创建、挂起、恢复和删除：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务句柄
TaskHandle_t worker_task_handle = NULL;
TaskHandle_t monitor_task_handle = NULL;

// 工作任务
void Worker_Task(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        printf("Worker task running, counter = %d\n", counter++);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 监控任务
void Monitor_Task(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        printf("Monitor task running, counter = %d\n", counter++);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 控制任务
void Control_Task(void *param) {
    uint32_t state = 0;
    
    while(1) {
        switch(state) {
            case 0:
                // 创建工作任务
                printf("\n[Control] Creating worker task...\n");
                xTaskCreate(Worker_Task, "Worker", 256, NULL, 2, &worker_task_handle);
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
                vTaskSuspend(worker_task_handle);
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
                vTaskResume(worker_task_handle);
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
                vTaskDelete(worker_task_handle);
                worker_task_handle = NULL;
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

int main(void) {
    SystemInit();
    
    // 创建监控任务（一直运行）
    xTaskCreate(Monitor_Task, "Monitor", 256, NULL, 1, &monitor_task_handle);
    
    // 创建控制任务
    xTaskCreate(Control_Task, "Control", 256, NULL, 3, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
    
    while(1);
}
```

**运行效果**：
```
[Control] Creating worker task...
Worker task running, counter = 0
Monitor task running, counter = 0
Worker task running, counter = 1
Worker task running, counter = 2
Monitor task running, counter = 1
...

[Control] Suspending worker task...
Monitor task running, counter = 5
Monitor task running, counter = 6
Monitor task running, counter = 7

[Control] Resuming worker task...
Worker task running, counter = 10
Monitor task running, counter = 8
...

[Control] Deleting worker task...
Monitor task running, counter = 11
Monitor task running, counter = 12
...
```

### 示例4：优先级动态调整

演示根据系统状态动态调整任务优先级：

```c
#include "FreeRTOS.h"
#include "task.h"

TaskHandle_t data_task_handle;
TaskHandle_t display_task_handle;

// 数据处理任务
void Data_Task(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        UBaseType_t priority = uxTaskPriorityGet(NULL);
        printf("Data task (priority %d): processing %d\n", priority, counter++);
        
        // 模拟数据处理
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

// 显示任务
void Display_Task(void *param) {
    uint32_t counter = 0;
    
    while(1) {
        UBaseType_t priority = uxTaskPriorityGet(NULL);
        printf("Display task (priority %d): updating %d\n", priority, counter++);
        
        // 模拟显示更新
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// 管理任务
void Manager_Task(void *param) {
    bool emergency_mode = false;
    uint32_t cycle = 0;
    
    while(1) {
        cycle++;
        
        // 每5秒切换一次模式
        if(cycle % 5 == 0) {
            emergency_mode = !emergency_mode;
            
            if(emergency_mode) {
                // 进入紧急模式：提升数据任务优先级
                printf("\n*** EMERGENCY MODE: Boosting data task priority ***\n");
                vTaskPrioritySet(data_task_handle, 5);
                vTaskPrioritySet(display_task_handle, 1);
            } else {
                // 恢复正常模式
                printf("\n*** NORMAL MODE: Restoring priorities ***\n");
                vTaskPrioritySet(data_task_handle, 2);
                vTaskPrioritySet(display_task_handle, 2);
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void) {
    SystemInit();
    
    // 创建任务（初始优先级相同）
    xTaskCreate(Data_Task, "Data", 256, NULL, 2, &data_task_handle);
    xTaskCreate(Display_Task, "Display", 256, NULL, 2, &display_task_handle);
    xTaskCreate(Manager_Task, "Manager", 256, NULL, 3, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

## 深入理解

### 任务切换的开销

任务切换需要保存和恢复上下文，这会带来一定的开销：

**上下文包含**：
- 通用寄存器（R0-R12）
- 程序计数器（PC）
- 栈指针（SP）
- 链接寄存器（LR）
- 程序状态寄存器（PSR）
- 浮点寄存器（如果使用FPU）

**切换时间**：
- Cortex-M3/M4：约1-3微秒
- Cortex-M0：约5-10微秒

**优化建议**：
```c
// ❌ 不好：频繁切换
void Task1(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(1);  // 每1ms切换一次
    }
}

// ✅ 更好：减少切换频率
void Task1(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);  // 每100ms切换一次
    }
}
```

### 任务栈的内存布局

```
高地址
┌─────────────────┐
│  未使用空间     │
├─────────────────┤
│  局部变量       │
├─────────────────┤
│  函数调用栈帧   │
├─────────────────┤
│  保存的寄存器   │
├─────────────────┤
│  任务上下文     │
├─────────────────┤ ← 栈指针(SP)
│  已使用空间     │
└─────────────────┘
低地址
```

**栈增长方向**：
- ARM Cortex-M：栈向下增长（从高地址到低地址）
- 栈指针指向最后压入的数据


### 任务调度时机

RTOS在以下情况下会进行任务调度：

1. **时钟节拍中断**
```c
// 每个时钟节拍都会检查是否需要切换任务
// 配置：configTICK_RATE_HZ = 1000 (1ms一次)
```

2. **任务主动让出CPU**
```c
void Task(void *param) {
    while(1) {
        DoWork();
        vTaskDelay(100);  // 主动让出CPU
        // 或
        taskYIELD();      // 立即让出CPU
    }
}
```

3. **任务阻塞**
```c
// 等待信号量时阻塞
xSemaphoreTake(sem, portMAX_DELAY);

// 等待队列数据时阻塞
xQueueReceive(queue, &data, portMAX_DELAY);
```

4. **高优先级任务就绪**
```c
// 中断中唤醒高优先级任务
void EXTI_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 释放信号量，可能唤醒高优先级任务
    xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
    
    // 如果唤醒了更高优先级的任务，立即切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 空闲任务

RTOS会自动创建一个空闲任务（Idle Task）：

**特点**：
- 优先级最低（通常为0）
- 当没有其他任务就绪时运行
- 负责清理被删除任务的资源
- 可以添加钩子函数执行后台任务

```c
// 空闲任务钩子函数
void vApplicationIdleHook(void) {
    // 在空闲任务中执行的代码
    // 注意：不能阻塞或挂起
    
    // 示例：进入低功耗模式
    __WFI();  // 等待中断
    
    // 示例：执行后台任务
    CheckSystemHealth();
}

// 在FreeRTOSConfig.h中启用
#define configUSE_IDLE_HOOK  1
```

## 常见问题

### Q1: 任务函数为什么必须是无限循环？

**A**: 任务函数不应该返回，原因如下：

```c
// ❌ 错误：任务函数返回
void Bad_Task(void *param) {
    DoSomething();
    return;  // 错误！任务函数不应该返回
}

// ✅ 正确：无限循环
void Good_Task(void *param) {
    while(1) {
        DoSomething();
        vTaskDelay(100);
    }
}

// ✅ 正确：如果任务需要结束，应该删除自己
void Temporary_Task(void *param) {
    DoOnceTask();
    vTaskDelete(NULL);  // 删除自己
    // 永远不会执行到这里
}
```

**原因**：
- 任务返回后，栈空间仍然被占用
- 任务控制块仍然存在
- 可能导致系统异常
- 正确的做法是删除任务

### Q2: 如何确定任务的栈大小？

**A**: 确定栈大小的方法：

**方法1：经验值**
```c
// 根据任务复杂度选择
xTaskCreate(SimpleTask, "Simple", 128, NULL, 1, NULL);    // 简单任务
xTaskCreate(NormalTask, "Normal", 256, NULL, 1, NULL);    // 普通任务
xTaskCreate(ComplexTask, "Complex", 512, NULL, 1, NULL);  // 复杂任务
```

**方法2：运行时检测**
```c
void Task(void *param) {
    while(1) {
        DoWork();
        
        // 检查栈使用情况
        UBaseType_t stack_free = uxTaskGetStackHighWaterMark(NULL);
        printf("Stack free: %d words (%d bytes)\n", stack_free, stack_free * 4);
        
        // 如果剩余空间太少，需要增加栈大小
        if(stack_free < 32) {
            printf("Warning: Stack space is low!\n");
        }
        
        vTaskDelay(1000);
    }
}
```

**方法3：启用栈溢出检测**
```c
// FreeRTOSConfig.h
#define configCHECK_FOR_STACK_OVERFLOW  2

// 实现钩子函数
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    printf("Stack overflow in task: %s\n", pcTaskName);
    // 增加该任务的栈大小
}
```

**建议**：
- 从较大的值开始（如512字）
- 运行一段时间后检查栈水位
- 根据实际使用情况调整
- 留有一定余量（至少20%）

### Q3: 相同优先级的任务如何调度？

**A**: 相同优先级的任务采用时间片轮转：

```c
// 两个相同优先级的任务
void Task1(void *param) {
    while(1) {
        printf("Task1 running\n");
        // 不主动延时，运行一个时间片后被切换
    }
}

void Task2(void *param) {
    while(1) {
        printf("Task2 running\n");
        // 不主动延时，运行一个时间片后被切换
    }
}

int main(void) {
    // 创建相同优先级的任务
    xTaskCreate(Task1, "Task1", 128, NULL, 2, NULL);
    xTaskCreate(Task2, "Task2", 128, NULL, 2, NULL);
    
    vTaskStartScheduler();
    while(1);
}
```

**时间片配置**：
```c
// FreeRTOSConfig.h
#define configUSE_TIME_SLICING  1  // 启用时间片轮转
```

**执行顺序**：
```
时间片1: Task1运行
时间片2: Task2运行
时间片3: Task1运行
时间片4: Task2运行
...
```

### Q4: 任务优先级应该如何分配？

**A**: 优先级分配原则：

**1. 根据实时性要求**
```c
// 硬实时任务：最高优先级
xTaskCreate(SafetyTask, "Safety", 256, NULL, 5, NULL);

// 软实时任务：中等优先级
xTaskCreate(ControlTask, "Control", 256, NULL, 3, NULL);

// 非实时任务：低优先级
xTaskCreate(LogTask, "Log", 256, NULL, 1, NULL);
```

**2. 根据响应时间要求**
```c
// 需要快速响应：高优先级
xTaskCreate(InterruptHandler, "IRQ", 256, NULL, 4, NULL);

// 周期性任务：中等优先级
xTaskCreate(PeriodicTask, "Periodic", 256, NULL, 2, NULL);

// 后台任务：低优先级
xTaskCreate(BackgroundTask, "BG", 256, NULL, 1, NULL);
```

**3. 避免优先级反转**
```c
// 如果低优先级任务持有高优先级任务需要的资源
// 应该使用优先级继承的互斥量
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();
```

**建议**：
- 不要使用太多不同的优先级（3-5个级别足够）
- 相似功能的任务使用相同优先级
- 关键任务使用高优先级
- 后台任务使用低优先级

### Q5: 任务删除后资源会被释放吗？

**A**: 任务删除后的资源释放：

**动态创建的任务**：
```c
TaskHandle_t task_handle;

// 创建任务（从堆中分配）
xTaskCreate(Task, "Task", 256, NULL, 1, &task_handle);

// 删除任务
vTaskDelete(task_handle);

// 资源释放：
// 1. TCB会被立即标记为删除
// 2. 栈空间会在空闲任务中释放
// 3. 需要等待空闲任务运行
```

**静态创建的任务**：
```c
static StackType_t task_stack[256];
static StaticTask_t task_tcb;

TaskHandle_t task_handle = xTaskCreateStatic(
    Task, "Task", 256, NULL, 1, task_stack, &task_tcb
);

// 删除任务
vTaskDelete(task_handle);

// 资源释放：
// 1. TCB被标记为删除
// 2. 静态分配的内存不会被释放
// 3. 可以重新使用这些内存创建新任务
```

**注意事项**：
```c
// ❌ 错误：删除后立即创建同名任务可能失败
vTaskDelete(task_handle);
xTaskCreate(Task, "Task", 256, NULL, 1, &task_handle);  // 可能失败

// ✅ 正确：等待空闲任务清理
vTaskDelete(task_handle);
vTaskDelay(10);  // 给空闲任务时间清理
xTaskCreate(Task, "Task", 256, NULL, 1, &task_handle);  // 成功
```

## 总结

任务管理是RTOS的核心功能，掌握任务管理是使用RTOS的基础：

**核心要点**：
- **任务状态**：运行、就绪、阻塞、挂起、删除五种状态
- **任务创建**：动态创建（xTaskCreate）和静态创建（xTaskCreateStatic）
- **任务控制**：删除（vTaskDelete）、挂起（vTaskSuspend）、恢复（vTaskResume）
- **优先级**：数字越大优先级越高，高优先级任务优先执行
- **任务栈**：每个任务独立的栈空间，需要合理配置大小

**最佳实践**：
- 任务函数必须是无限循环或删除自己
- 合理分配任务优先级（3-5个级别）
- 根据任务复杂度配置栈大小
- 启用栈溢出检测
- 定期检查栈使用情况
- 避免创建过多任务

**常见API**：
```c
// 创建和删除
xTaskCreate() / xTaskCreateStatic()
vTaskDelete()

// 挂起和恢复
vTaskSuspend() / vTaskResume()

// 优先级管理
uxTaskPriorityGet() / vTaskPrioritySet()

// 延时
vTaskDelay() / vTaskDelayUntil()

// 信息查询
uxTaskGetStackHighWaterMark()
xTaskGetHandle()
```

**下一步学习**：
- 学习RTOS调度算法，理解任务如何被调度
- 学习任务间通信机制（信号量、队列、事件组）
- 学习中断与RTOS的配合
- 实践完整的多任务项目

## 延伸阅读

推荐进一步学习的资源：

- [RTOS调度算法详解](03-rtos-scheduling.html) - 深入理解调度原理
- [信号量使用实战](04-semaphore.html) - 学习任务同步机制
- [互斥量与临界区保护](05-mutex.html) - 保护共享资源
- FreeRTOS任务创建与管理 - FreeRTOS具体实现

## 参考资料

1. "Mastering the FreeRTOS Real Time Kernel" - Richard Barry
2. "FreeRTOS Reference Manual" - Real Time Engineers Ltd.
3. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" - Joseph Yiu
4. FreeRTOS官方文档 - https://www.freertos.org/
5. ARM CMSIS-RTOS API文档
6. "Real-Time Systems Design and Analysis" - Phillip A. Laplante

---

**练习题**：

1. **基础练习**：
   - 创建三个任务，分别控制三个LED以不同频率闪烁
   - 实现一个任务监控系统，显示所有任务的栈使用情况

2. **进阶练习**：
   - 创建一个传感器采集系统，包含采集、处理、显示三个任务
   - 实现任务的动态创建和删除，根据系统负载调整任务数量

3. **综合练习**：
   - 设计一个智能温控系统，包含温度采集、PID控制、显示、报警等任务
   - 根据温度变化动态调整任务优先级

4. **调试练习**：
   - 故意创建栈溢出，观察系统行为
   - 实现一个任务监控工具，实时显示任务状态和CPU使用率

**下一步**：建议学习 [RTOS调度算法详解](03-rtos-scheduling.html)，深入理解任务调度的原理和策略。
