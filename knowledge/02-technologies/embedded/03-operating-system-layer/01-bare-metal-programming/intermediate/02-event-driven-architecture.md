---
title: "事件驱动架构设计：构建高效响应的嵌入式系统"
description: "深入学习事件驱动架构的设计原理和实现方法。掌握事件驱动模型、事件队列、订阅发布模式、异步处理等核心技术，学会构建高响应性、低耦合的嵌入式系统架构。"
slug: "event-driven-architecture"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 事件驱动
  - 架构设计
  - 异步处理
  - 事件队列
  - 订阅发布
  - 解耦设计
prerequisites:
  - "beginner/01-bare-metal-basics.md"
  - "beginner/02-super-loop.md"
  - "beginner/03-state-machine.md"
related_contents:
  - "intermediate/01-cooperative-scheduler.md"
  - "beginner/06-ring-buffer.md"

# 学习信息
estimated_time: 50
difficulty_score: 5

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
  - 事件驱动架构
  - Event-Driven Architecture
  - 事件队列
  - 异步编程
  - 发布订阅
  - 解耦设计
cover_image: ""
---

# 事件驱动架构设计：构建高效响应的嵌入式系统

## 概述

事件驱动架构（Event-Driven Architecture, EDA）是一种以事件为核心的软件设计模式，系统的行为由事件的产生和处理驱动。在嵌入式系统中，事件驱动架构能够有效处理异步事件、提高系统响应性、降低模块耦合度。

完成本文学习后，你将能够：

- 理解事件驱动架构的核心概念和设计原则
- 掌握事件队列的设计和实现方法
- 学会使用订阅发布模式解耦系统模块
- 实现高效的异步事件处理机制
- 设计可扩展、易维护的嵌入式系统架构

## 背景知识

### 什么是事件驱动架构？

**事件驱动架构**是一种软件设计模式，系统的执行流程由事件的发生和处理决定，而不是按照预定的顺序执行。

**核心概念**：
- **事件（Event）**：系统中发生的有意义的状态变化或动作
- **事件源（Event Source）**：产生事件的组件或模块
- **事件处理器（Event Handler）**：响应和处理事件的函数或模块
- **事件队列（Event Queue）**：存储待处理事件的缓冲区
- **事件分发器（Event Dispatcher）**：将事件分发给相应处理器的组件

### 传统架构 vs 事件驱动架构

**传统轮询架构**：
```c
// 主循环不断轮询各个模块
while(1) {
    if(Button_IsPressed()) {
        HandleButton();
    }
    if(UART_HasData()) {
        HandleUART();
    }
    if(Timer_Expired()) {
        HandleTimer();
    }
    // ... 更多轮询
}
```

**问题**：
- 紧耦合：主循环需要知道所有模块
- 低效率：不断轮询浪费CPU
- 难扩展：添加新功能需要修改主循环
- 响应慢：事件可能要等待轮询周期

**事件驱动架构**：
```c
// 事件产生时加入队列
void Button_IRQHandler(void) {
    Event_Post(EVENT_BUTTON_PRESSED, NULL);
}

void UART_IRQHandler(void) {
    Event_Post(EVENT_UART_DATA, &data);
}

// 主循环只处理事件
while(1) {
    Event_t event;
    if(Event_Get(&event)) {
        Event_Dispatch(&event);
    }
}
```

**优势**：
- 解耦：模块之间通过事件通信
- 高效：事件驱动，无需轮询
- 易扩展：添加新事件处理器即可
- 响应快：事件立即处理


### 事件驱动架构的应用场景

**适合使用事件驱动的场景**：
- 用户界面交互（按键、触摸屏）
- 通信协议处理（UART、SPI、I2C）
- 传感器数据采集（中断触发）
- 定时器事件处理
- 状态机驱动
- 多模块协作系统

**不适合的场景**：
- 简单的顺序执行任务
- 实时性要求极高的控制回路
- 资源极度受限的系统（<1KB RAM）

## 核心内容

### 事件驱动架构的核心组件

一个完整的事件驱动系统包含以下核心组件：

```
┌─────────────────────────────────────────┐
│          事件源（Event Sources）         │
│  按键  │  定时器  │  UART  │  传感器    │
└────┬────────┬────────┬────────┬─────────┘
     │        │        │        │
     └────────┴────────┴────────┘
              │ Post Event
     ┌────────▼────────────────┐
     │   事件队列（Event Queue） │
     │   [E1][E2][E3][E4]...   │
     └────────┬────────────────┘
              │ Get Event
     ┌────────▼────────────────┐
     │ 事件分发器（Dispatcher）  │
     │   根据事件类型分发       │
     └────┬────────┬───────────┘
          │        │
     ┌────▼───┐ ┌──▼────┐
     │Handler1│ │Handler2│ ...
     └────────┘ └───────┘
```

### 数据结构设计

#### 事件定义

```c
// 事件类型枚举
typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESSED,
    EVENT_BUTTON_RELEASED,
    EVENT_TIMER_EXPIRED,
    EVENT_UART_RX,
    EVENT_UART_TX_COMPLETE,
    EVENT_ADC_COMPLETE,
    EVENT_SENSOR_DATA,
    EVENT_USER_DEFINED,
    EVENT_MAX
} EventType_t;

// 事件结构
typedef struct {
    EventType_t type;           // 事件类型
    uint32_t timestamp;         // 时间戳
    void *data;                 // 事件数据指针
    uint16_t data_size;         // 数据大小
} Event_t;

// 事件处理器函数类型
typedef void (*EventHandler_t)(Event_t *event);
```

#### 事件队列

使用环形缓冲区实现事件队列：

```c
// 事件队列配置
#define EVENT_QUEUE_SIZE 32

// 事件队列结构
typedef struct {
    Event_t buffer[EVENT_QUEUE_SIZE];
    volatile uint16_t head;     // 写指针
    volatile uint16_t tail;     // 读指针
    volatile uint16_t count;    // 当前事件数
} EventQueue_t;

// 全局事件队列
static EventQueue_t g_event_queue = {0};
```


### 事件队列实现

#### 初始化事件队列

```c
/**
 * @brief 初始化事件队列
 */
void EventQueue_Init(void) {
    g_event_queue.head = 0;
    g_event_queue.tail = 0;
    g_event_queue.count = 0;
}

/**
 * @brief 检查队列是否为空
 * @return true: 空, false: 非空
 */
bool EventQueue_IsEmpty(void) {
    return (g_event_queue.count == 0);
}

/**
 * @brief 检查队列是否已满
 * @return true: 满, false: 未满
 */
bool EventQueue_IsFull(void) {
    return (g_event_queue.count >= EVENT_QUEUE_SIZE);
}

/**
 * @brief 获取队列中的事件数量
 * @return 事件数量
 */
uint16_t EventQueue_GetCount(void) {
    return g_event_queue.count;
}
```

#### 发布事件（Post）

```c
/**
 * @brief 发布事件到队列
 * @param type 事件类型
 * @param data 事件数据指针
 * @param data_size 数据大小
 * @return true: 成功, false: 队列已满
 */
bool Event_Post(EventType_t type, void *data, uint16_t data_size) {
    // 检查队列是否已满
    if(EventQueue_IsFull()) {
        return false;
    }
    
    // 关中断保护临界区
    __disable_irq();
    
    // 获取当前写位置
    Event_t *event = &g_event_queue.buffer[g_event_queue.head];
    
    // 填充事件信息
    event->type = type;
    event->timestamp = GetSystemTick();
    event->data = data;
    event->data_size = data_size;
    
    // 更新写指针
    g_event_queue.head = (g_event_queue.head + 1) % EVENT_QUEUE_SIZE;
    g_event_queue.count++;
    
    // 恢复中断
    __enable_irq();
    
    return true;
}

/**
 * @brief 发布简单事件（无数据）
 * @param type 事件类型
 * @return true: 成功, false: 失败
 */
bool Event_PostSimple(EventType_t type) {
    return Event_Post(type, NULL, 0);
}
```

#### 获取事件（Get）

```c
/**
 * @brief 从队列获取事件
 * @param event 事件结构指针（输出）
 * @return true: 成功, false: 队列为空
 */
bool Event_Get(Event_t *event) {
    // 检查队列是否为空
    if(EventQueue_IsEmpty()) {
        return false;
    }
    
    // 关中断保护临界区
    __disable_irq();
    
    // 获取当前读位置
    Event_t *src = &g_event_queue.buffer[g_event_queue.tail];
    
    // 复制事件数据
    event->type = src->type;
    event->timestamp = src->timestamp;
    event->data = src->data;
    event->data_size = src->data_size;
    
    // 更新读指针
    g_event_queue.tail = (g_event_queue.tail + 1) % EVENT_QUEUE_SIZE;
    g_event_queue.count--;
    
    // 恢复中断
    __enable_irq();
    
    return true;
}

/**
 * @brief 查看队列头部事件（不移除）
 * @param event 事件结构指针（输出）
 * @return true: 成功, false: 队列为空
 */
bool Event_Peek(Event_t *event) {
    if(EventQueue_IsEmpty()) {
        return false;
    }
    
    __disable_irq();
    Event_t *src = &g_event_queue.buffer[g_event_queue.tail];
    event->type = src->type;
    event->timestamp = src->timestamp;
    event->data = src->data;
    event->data_size = src->data_size;
    __enable_irq();
    
    return true;
}
```


### 事件分发机制

#### 方法1：简单的switch-case分发

最直接的实现方式，适合事件类型较少的场景：

```c
/**
 * @brief 事件分发器（简单版本）
 * @param event 事件指针
 */
void Event_Dispatch(Event_t *event) {
    switch(event->type) {
        case EVENT_BUTTON_PRESSED:
            OnButtonPressed(event);
            break;
            
        case EVENT_BUTTON_RELEASED:
            OnButtonReleased(event);
            break;
            
        case EVENT_TIMER_EXPIRED:
            OnTimerExpired(event);
            break;
            
        case EVENT_UART_RX:
            OnUARTReceive(event);
            break;
            
        case EVENT_ADC_COMPLETE:
            OnADCComplete(event);
            break;
            
        default:
            // 未知事件
            break;
    }
}

// 事件处理函数示例
void OnButtonPressed(Event_t *event) {
    printf("Button pressed at %lu ms\n", event->timestamp);
    // 处理按键按下事件
}

void OnTimerExpired(Event_t *event) {
    uint32_t timer_id = *(uint32_t *)event->data;
    printf("Timer %lu expired\n", timer_id);
    // 处理定时器超时事件
}
```

#### 方法2：函数指针表分发

使用函数指针表实现更灵活的分发机制：

```c
// 事件处理器注册表
static EventHandler_t g_event_handlers[EVENT_MAX] = {NULL};

/**
 * @brief 注册事件处理器
 * @param type 事件类型
 * @param handler 处理函数指针
 */
void Event_RegisterHandler(EventType_t type, EventHandler_t handler) {
    if(type < EVENT_MAX) {
        g_event_handlers[type] = handler;
    }
}

/**
 * @brief 注销事件处理器
 * @param type 事件类型
 */
void Event_UnregisterHandler(EventType_t type) {
    if(type < EVENT_MAX) {
        g_event_handlers[type] = NULL;
    }
}

/**
 * @brief 事件分发器（函数指针表版本）
 * @param event 事件指针
 */
void Event_Dispatch(Event_t *event) {
    if(event->type < EVENT_MAX) {
        EventHandler_t handler = g_event_handlers[event->type];
        if(handler != NULL) {
            handler(event);
        }
    }
}

// 使用示例
void Setup_EventHandlers(void) {
    Event_RegisterHandler(EVENT_BUTTON_PRESSED, OnButtonPressed);
    Event_RegisterHandler(EVENT_BUTTON_RELEASED, OnButtonReleased);
    Event_RegisterHandler(EVENT_TIMER_EXPIRED, OnTimerExpired);
    Event_RegisterHandler(EVENT_UART_RX, OnUARTReceive);
}
```

#### 方法3：订阅发布模式

支持多个处理器订阅同一事件：

```c
// 订阅者列表节点
typedef struct SubscriberNode {
    EventHandler_t handler;
    struct SubscriberNode *next;
} SubscriberNode_t;

// 订阅者列表（每个事件类型一个链表）
static SubscriberNode_t *g_subscribers[EVENT_MAX] = {NULL};

/**
 * @brief 订阅事件
 * @param type 事件类型
 * @param handler 处理函数
 * @return true: 成功, false: 失败
 */
bool Event_Subscribe(EventType_t type, EventHandler_t handler) {
    if(type >= EVENT_MAX || handler == NULL) {
        return false;
    }
    
    // 分配订阅者节点
    SubscriberNode_t *node = (SubscriberNode_t *)malloc(sizeof(SubscriberNode_t));
    if(node == NULL) {
        return false;
    }
    
    node->handler = handler;
    node->next = g_subscribers[type];
    g_subscribers[type] = node;
    
    return true;
}

/**
 * @brief 取消订阅
 * @param type 事件类型
 * @param handler 处理函数
 */
void Event_Unsubscribe(EventType_t type, EventHandler_t handler) {
    if(type >= EVENT_MAX) {
        return;
    }
    
    SubscriberNode_t **current = &g_subscribers[type];
    while(*current != NULL) {
        if((*current)->handler == handler) {
            SubscriberNode_t *to_free = *current;
            *current = (*current)->next;
            free(to_free);
            return;
        }
        current = &((*current)->next);
    }
}

/**
 * @brief 事件分发器（订阅发布版本）
 * @param event 事件指针
 */
void Event_Dispatch(Event_t *event) {
    if(event->type >= EVENT_MAX) {
        return;
    }
    
    // 遍历订阅者链表，调用所有处理器
    SubscriberNode_t *subscriber = g_subscribers[event->type];
    while(subscriber != NULL) {
        if(subscriber->handler != NULL) {
            subscriber->handler(event);
        }
        subscriber = subscriber->next;
    }
}

// 使用示例：多个模块订阅同一事件
void Module1_OnButton(Event_t *event) {
    printf("Module1: Button event\n");
}

void Module2_OnButton(Event_t *event) {
    printf("Module2: Button event\n");
}

void Setup_Subscriptions(void) {
    Event_Subscribe(EVENT_BUTTON_PRESSED, Module1_OnButton);
    Event_Subscribe(EVENT_BUTTON_PRESSED, Module2_OnButton);
}
```


### 事件循环（Event Loop）

事件循环是事件驱动系统的核心，负责不断获取和处理事件：

```c
/**
 * @brief 基本事件循环
 */
void EventLoop_Run(void) {
    Event_t event;
    
    while(1) {
        // 获取事件
        if(Event_Get(&event)) {
            // 分发事件
            Event_Dispatch(&event);
        } else {
            // 队列为空，可以进入低功耗模式
            __WFI();  // Wait For Interrupt
        }
    }
}

/**
 * @brief 带超时的事件循环
 * @param timeout_ms 超时时间（毫秒）
 */
void EventLoop_RunWithTimeout(uint32_t timeout_ms) {
    Event_t event;
    uint32_t start_time = GetSystemTick();
    
    while(1) {
        if(Event_Get(&event)) {
            Event_Dispatch(&event);
            start_time = GetSystemTick();  // 重置超时
        } else {
            // 检查超时
            if((GetSystemTick() - start_time) >= timeout_ms) {
                // 超时处理
                OnEventLoopTimeout();
                start_time = GetSystemTick();
            }
            __WFI();
        }
    }
}

/**
 * @brief 带优先级的事件循环
 */
void EventLoop_RunWithPriority(void) {
    Event_t event;
    
    while(1) {
        if(Event_Get(&event)) {
            // 检查是否有高优先级事件
            if(IsHighPriorityEvent(event.type)) {
                // 立即处理高优先级事件
                Event_Dispatch(&event);
            } else {
                // 低优先级事件可以延迟处理
                if(CanProcessLowPriorityEvent()) {
                    Event_Dispatch(&event);
                } else {
                    // 重新放回队列
                    Event_Post(event.type, event.data, event.data_size);
                }
            }
        } else {
            __WFI();
        }
    }
}
```

### 异步处理机制

事件驱动架构的一个重要特性是支持异步处理：

```c
// 异步操作状态
typedef enum {
    ASYNC_STATE_IDLE,
    ASYNC_STATE_PENDING,
    ASYNC_STATE_COMPLETE,
    ASYNC_STATE_ERROR
} AsyncState_t;

// 异步操作结构
typedef struct {
    AsyncState_t state;
    void *result;
    EventHandler_t callback;
} AsyncOperation_t;

/**
 * @brief 启动异步操作
 * @param operation 异步操作结构
 * @param callback 完成回调函数
 */
void Async_Start(AsyncOperation_t *operation, EventHandler_t callback) {
    operation->state = ASYNC_STATE_PENDING;
    operation->callback = callback;
    
    // 启动硬件操作（如DMA、ADC等）
    StartHardwareOperation();
}

/**
 * @brief 异步操作完成（在中断中调用）
 * @param operation 异步操作结构
 * @param result 操作结果
 */
void Async_Complete(AsyncOperation_t *operation, void *result) {
    operation->state = ASYNC_STATE_COMPLETE;
    operation->result = result;
    
    // 发布完成事件
    Event_Post(EVENT_ASYNC_COMPLETE, operation, sizeof(AsyncOperation_t));
}

/**
 * @brief 异步完成事件处理器
 * @param event 事件指针
 */
void OnAsyncComplete(Event_t *event) {
    AsyncOperation_t *operation = (AsyncOperation_t *)event->data;
    
    if(operation->callback != NULL) {
        operation->callback(event);
    }
    
    operation->state = ASYNC_STATE_IDLE;
}

// 使用示例：异步ADC读取
void ReadADC_Async(EventHandler_t callback) {
    static AsyncOperation_t adc_operation;
    Async_Start(&adc_operation, callback);
}

void OnADCReadComplete(Event_t *event) {
    AsyncOperation_t *op = (AsyncOperation_t *)event->data;
    uint16_t adc_value = *(uint16_t *)op->result;
    printf("ADC value: %u\n", adc_value);
}
```


## 实践示例

### 示例1：按键事件处理系统

实现一个完整的按键事件处理系统，包括消抖、长按检测等功能：

```c
#include <stdint.h>
#include <stdbool.h>

// 按键事件类型
typedef enum {
    BUTTON_EVENT_PRESSED,
    BUTTON_EVENT_RELEASED,
    BUTTON_EVENT_CLICK,
    BUTTON_EVENT_DOUBLE_CLICK,
    BUTTON_EVENT_LONG_PRESS
} ButtonEventType_t;

// 按键状态机
typedef enum {
    BUTTON_STATE_IDLE,
    BUTTON_STATE_DEBOUNCE,
    BUTTON_STATE_PRESSED,
    BUTTON_STATE_WAIT_RELEASE,
    BUTTON_STATE_WAIT_DOUBLE
} ButtonState_t;

// 按键配置
#define DEBOUNCE_TIME_MS    20
#define LONG_PRESS_TIME_MS  1000
#define DOUBLE_CLICK_TIME_MS 300

// 按键状态
typedef struct {
    ButtonState_t state;
    uint32_t press_time;
    uint32_t release_time;
    uint8_t click_count;
} ButtonContext_t;

static ButtonContext_t button_ctx = {BUTTON_STATE_IDLE, 0, 0, 0};

/**
 * @brief 按键GPIO中断处理
 */
void BUTTON_IRQHandler(void) {
    bool pressed = Button_Read();
    
    if(pressed) {
        button_ctx.press_time = GetSystemTick();
        button_ctx.state = BUTTON_STATE_DEBOUNCE;
    } else {
        button_ctx.release_time = GetSystemTick();
    }
}

/**
 * @brief 按键状态机处理（在主循环或定时器中调用）
 */
void Button_Process(void) {
    uint32_t current_time = GetSystemTick();
    bool pressed = Button_Read();
    
    switch(button_ctx.state) {
        case BUTTON_STATE_IDLE:
            // 等待按键按下
            break;
            
        case BUTTON_STATE_DEBOUNCE:
            // 消抖延时
            if((current_time - button_ctx.press_time) >= DEBOUNCE_TIME_MS) {
                if(pressed) {
                    // 确认按下
                    button_ctx.state = BUTTON_STATE_PRESSED;
                    Event_PostSimple(EVENT_BUTTON_PRESSED);
                } else {
                    button_ctx.state = BUTTON_STATE_IDLE;
                }
            }
            break;
            
        case BUTTON_STATE_PRESSED:
            if(!pressed) {
                // 按键释放
                button_ctx.state = BUTTON_STATE_WAIT_RELEASE;
            } else if((current_time - button_ctx.press_time) >= LONG_PRESS_TIME_MS) {
                // 长按检测
                Event_PostSimple(EVENT_BUTTON_LONG_PRESS);
                button_ctx.state = BUTTON_STATE_WAIT_RELEASE;
            }
            break;
            
        case BUTTON_STATE_WAIT_RELEASE:
            if(!pressed) {
                Event_PostSimple(EVENT_BUTTON_RELEASED);
                button_ctx.click_count++;
                button_ctx.state = BUTTON_STATE_WAIT_DOUBLE;
            }
            break;
            
        case BUTTON_STATE_WAIT_DOUBLE:
            if(pressed) {
                // 检测到第二次按下
                if((current_time - button_ctx.release_time) < DOUBLE_CLICK_TIME_MS) {
                    Event_PostSimple(EVENT_BUTTON_DOUBLE_CLICK);
                    button_ctx.click_count = 0;
                    button_ctx.state = BUTTON_STATE_WAIT_RELEASE;
                }
            } else if((current_time - button_ctx.release_time) >= DOUBLE_CLICK_TIME_MS) {
                // 超时，确认为单击
                Event_PostSimple(EVENT_BUTTON_CLICK);
                button_ctx.click_count = 0;
                button_ctx.state = BUTTON_STATE_IDLE;
            }
            break;
    }
}

// 事件处理器
void OnButtonPressed(Event_t *event) {
    printf("Button pressed\n");
    LED_On();
}

void OnButtonReleased(Event_t *event) {
    printf("Button released\n");
    LED_Off();
}

void OnButtonClick(Event_t *event) {
    printf("Button clicked\n");
    ToggleMode();
}

void OnButtonDoubleClick(Event_t *event) {
    printf("Button double-clicked\n");
    EnterSpecialMode();
}

void OnButtonLongPress(Event_t *event) {
    printf("Button long-pressed\n");
    EnterConfigMode();
}

// 主函数
int main(void) {
    SystemInit();
    Button_Init();
    EventQueue_Init();
    
    // 注册事件处理器
    Event_RegisterHandler(EVENT_BUTTON_PRESSED, OnButtonPressed);
    Event_RegisterHandler(EVENT_BUTTON_RELEASED, OnButtonReleased);
    Event_RegisterHandler(EVENT_BUTTON_CLICK, OnButtonClick);
    Event_RegisterHandler(EVENT_BUTTON_DOUBLE_CLICK, OnButtonDoubleClick);
    Event_RegisterHandler(EVENT_BUTTON_LONG_PRESS, OnButtonLongPress);
    
    // 主循环
    while(1) {
        // 处理按键状态机
        Button_Process();
        
        // 处理事件
        Event_t event;
        if(Event_Get(&event)) {
            Event_Dispatch(&event);
        }
    }
    
    return 0;
}
```


### 示例2：多模块通信系统

实现一个包含UART、传感器和显示模块的通信系统：

```c
// 系统事件定义
typedef enum {
    EVENT_UART_RX_COMPLETE,
    EVENT_SENSOR_DATA_READY,
    EVENT_DISPLAY_UPDATE,
    EVENT_COMMAND_RECEIVED,
    EVENT_DATA_PROCESSED
} SystemEvent_t;

// 传感器数据结构
typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
} SensorData_t;

// 命令结构
typedef struct {
    uint8_t cmd_id;
    uint8_t param[8];
    uint8_t param_len;
} Command_t;

// ========== 模块1：UART通信模块 ==========
void UART_RxComplete_IRQHandler(void) {
    static uint8_t rx_buffer[64];
    static uint8_t rx_index = 0;
    
    uint8_t data = UART_ReadByte();
    rx_buffer[rx_index++] = data;
    
    // 检测命令结束符
    if(data == '\n' || rx_index >= sizeof(rx_buffer)) {
        // 发布接收完成事件
        Event_Post(EVENT_UART_RX_COMPLETE, rx_buffer, rx_index);
        rx_index = 0;
    }
}

void OnUARTRxComplete(Event_t *event) {
    uint8_t *data = (uint8_t *)event->data;
    uint16_t len = event->data_size;
    
    // 解析命令
    Command_t cmd;
    if(ParseCommand(data, len, &cmd)) {
        // 发布命令事件
        Event_Post(EVENT_COMMAND_RECEIVED, &cmd, sizeof(Command_t));
    }
}

// ========== 模块2：传感器模块 ==========
void Sensor_ReadData(void) {
    static SensorData_t sensor_data;
    
    // 读取传感器
    sensor_data.temperature = ReadTemperature();
    sensor_data.humidity = ReadHumidity();
    sensor_data.timestamp = GetSystemTick();
    
    // 发布数据就绪事件
    Event_Post(EVENT_SENSOR_DATA_READY, &sensor_data, sizeof(SensorData_t));
}

void OnSensorDataReady(Event_t *event) {
    SensorData_t *data = (SensorData_t *)event->data;
    
    printf("Temperature: %.1f°C, Humidity: %.1f%%\n", 
           data->temperature, data->humidity);
    
    // 触发显示更新
    Event_PostSimple(EVENT_DISPLAY_UPDATE);
    
    // 通过UART发送数据
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "T:%.1f,H:%.1f\n",
             data->temperature, data->humidity);
    UART_SendString(buffer);
}

// ========== 模块3：命令处理模块 ==========
void OnCommandReceived(Event_t *event) {
    Command_t *cmd = (Command_t *)event->data;
    
    switch(cmd->cmd_id) {
        case CMD_READ_SENSOR:
            // 触发传感器读取
            Sensor_ReadData();
            break;
            
        case CMD_SET_INTERVAL:
            // 设置采样间隔
            uint32_t interval = *(uint32_t *)cmd->param;
            SetSamplingInterval(interval);
            break;
            
        case CMD_GET_STATUS:
            // 发送状态信息
            SendSystemStatus();
            break;
            
        default:
            printf("Unknown command: %d\n", cmd->cmd_id);
            break;
    }
}

// ========== 模块4：显示模块 ==========
void OnDisplayUpdate(Event_t *event) {
    // 更新显示内容
    Display_Clear();
    Display_ShowTemperature(g_current_temperature);
    Display_ShowHumidity(g_current_humidity);
    Display_Refresh();
}

// ========== 主程序 ==========
int main(void) {
    SystemInit();
    UART_Init();
    Sensor_Init();
    Display_Init();
    EventQueue_Init();
    
    // 注册事件处理器
    Event_RegisterHandler(EVENT_UART_RX_COMPLETE, OnUARTRxComplete);
    Event_RegisterHandler(EVENT_SENSOR_DATA_READY, OnSensorDataReady);
    Event_RegisterHandler(EVENT_COMMAND_RECEIVED, OnCommandReceived);
    Event_RegisterHandler(EVENT_DISPLAY_UPDATE, OnDisplayUpdate);
    
    // 启动定时器，定期读取传感器
    Timer_Start(1000, Sensor_ReadData);  // 每秒读取一次
    
    // 事件循环
    EventLoop_Run();
    
    return 0;
}
```

**系统工作流程**：
1. UART接收到命令 → 发布`EVENT_UART_RX_COMPLETE`
2. 命令解析完成 → 发布`EVENT_COMMAND_RECEIVED`
3. 命令处理器触发传感器读取
4. 传感器读取完成 → 发布`EVENT_SENSOR_DATA_READY`
5. 数据处理完成 → 发布`EVENT_DISPLAY_UPDATE`
6. 显示模块更新界面

**优势**：
- 模块解耦：各模块通过事件通信，互不依赖
- 易扩展：添加新模块只需订阅相关事件
- 易测试：可以单独测试每个模块
- 易维护：修改一个模块不影响其他模块


### 示例3：状态机与事件驱动结合

将状态机与事件驱动架构结合，实现复杂的系统行为：

```c
// 系统状态定义
typedef enum {
    STATE_INIT,
    STATE_IDLE,
    STATE_MEASURING,
    STATE_PROCESSING,
    STATE_SENDING,
    STATE_ERROR
} SystemState_t;

// 状态机上下文
typedef struct {
    SystemState_t current_state;
    SystemState_t previous_state;
    uint32_t state_entry_time;
} StateMachine_t;

static StateMachine_t g_state_machine = {STATE_INIT, STATE_INIT, 0};

/**
 * @brief 状态转换
 * @param new_state 新状态
 */
void StateMachine_Transition(SystemState_t new_state) {
    if(g_state_machine.current_state != new_state) {
        printf("State: %d -> %d\n", g_state_machine.current_state, new_state);
        
        g_state_machine.previous_state = g_state_machine.current_state;
        g_state_machine.current_state = new_state;
        g_state_machine.state_entry_time = GetSystemTick();
        
        // 发布状态改变事件
        Event_Post(EVENT_STATE_CHANGED, &new_state, sizeof(SystemState_t));
    }
}

/**
 * @brief 状态机事件处理
 * @param event 事件指针
 */
void StateMachine_HandleEvent(Event_t *event) {
    switch(g_state_machine.current_state) {
        case STATE_INIT:
            if(event->type == EVENT_SYSTEM_READY) {
                StateMachine_Transition(STATE_IDLE);
            }
            break;
            
        case STATE_IDLE:
            if(event->type == EVENT_START_MEASURE) {
                StateMachine_Transition(STATE_MEASURING);
                StartMeasurement();
            } else if(event->type == EVENT_ERROR_DETECTED) {
                StateMachine_Transition(STATE_ERROR);
            }
            break;
            
        case STATE_MEASURING:
            if(event->type == EVENT_MEASURE_COMPLETE) {
                StateMachine_Transition(STATE_PROCESSING);
                ProcessData();
            } else if(event->type == EVENT_MEASURE_TIMEOUT) {
                StateMachine_Transition(STATE_ERROR);
            }
            break;
            
        case STATE_PROCESSING:
            if(event->type == EVENT_PROCESS_COMPLETE) {
                StateMachine_Transition(STATE_SENDING);
                SendData();
            } else if(event->type == EVENT_PROCESS_ERROR) {
                StateMachine_Transition(STATE_ERROR);
            }
            break;
            
        case STATE_SENDING:
            if(event->type == EVENT_SEND_COMPLETE) {
                StateMachine_Transition(STATE_IDLE);
            } else if(event->type == EVENT_SEND_FAILED) {
                // 重试或进入错误状态
                StateMachine_Transition(STATE_ERROR);
            }
            break;
            
        case STATE_ERROR:
            if(event->type == EVENT_ERROR_CLEARED) {
                StateMachine_Transition(STATE_IDLE);
            }
            break;
    }
}

/**
 * @brief 状态超时检测
 */
void StateMachine_CheckTimeout(void) {
    uint32_t elapsed = GetSystemTick() - g_state_machine.state_entry_time;
    
    switch(g_state_machine.current_state) {
        case STATE_MEASURING:
            if(elapsed > MEASURE_TIMEOUT_MS) {
                Event_PostSimple(EVENT_MEASURE_TIMEOUT);
            }
            break;
            
        case STATE_PROCESSING:
            if(elapsed > PROCESS_TIMEOUT_MS) {
                Event_PostSimple(EVENT_PROCESS_ERROR);
            }
            break;
            
        case STATE_SENDING:
            if(elapsed > SEND_TIMEOUT_MS) {
                Event_PostSimple(EVENT_SEND_FAILED);
            }
            break;
    }
}

// 主循环
int main(void) {
    SystemInit();
    EventQueue_Init();
    
    // 注册状态机事件处理器
    Event_RegisterHandler(EVENT_SYSTEM_READY, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_START_MEASURE, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_MEASURE_COMPLETE, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_MEASURE_TIMEOUT, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_PROCESS_COMPLETE, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_PROCESS_ERROR, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_SEND_COMPLETE, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_SEND_FAILED, StateMachine_HandleEvent);
    Event_RegisterHandler(EVENT_ERROR_CLEARED, StateMachine_HandleEvent);
    
    // 发布系统就绪事件
    Event_PostSimple(EVENT_SYSTEM_READY);
    
    while(1) {
        // 检查状态超时
        StateMachine_CheckTimeout();
        
        // 处理事件
        Event_t event;
        if(Event_Get(&event)) {
            Event_Dispatch(&event);
        }
    }
    
    return 0;
}
```


## 深入理解

### 事件驱动 vs 其他架构模式

#### 对比表

| 特性 | 超级循环 | 时间片调度 | 事件驱动 | RTOS |
|------|---------|-----------|---------|------|
| 响应性 | 差 | 中 | 好 | 优 |
| 耦合度 | 高 | 中 | 低 | 低 |
| 复杂度 | 低 | 中 | 中 | 高 |
| 资源占用 | 最小 | 小 | 小 | 大 |
| 扩展性 | 差 | 中 | 好 | 优 |
| 学习曲线 | 平缓 | 中等 | 中等 | 陡峭 |

#### 选择建议

**使用超级循环**：
- 简单的顺序任务
- 资源极度受限（<512B RAM）
- 不需要快速响应

**使用时间片调度**：
- 3-10个简单任务
- 需要基本的多任务
- 响应要求不高（几十毫秒）

**使用事件驱动**：
- 异步事件处理
- 模块解耦需求
- 中等复杂度系统
- 响应要求较高（几毫秒）

**使用RTOS**：
- 复杂的多任务系统
- 严格的实时性要求
- 需要完整的同步机制
- 大型项目

### 性能优化技巧

#### 1. 事件队列优化

```c
// 使用优先级队列
typedef struct {
    Event_t buffer[EVENT_QUEUE_SIZE];
    uint8_t priority[EVENT_QUEUE_SIZE];
    volatile uint16_t count;
} PriorityEventQueue_t;

/**
 * @brief 按优先级插入事件
 */
bool Event_PostWithPriority(EventType_t type, void *data, 
                             uint16_t data_size, uint8_t priority) {
    if(EventQueue_IsFull()) {
        return false;
    }
    
    __disable_irq();
    
    // 找到插入位置（按优先级排序）
    uint16_t insert_pos = 0;
    for(uint16_t i = 0; i < g_priority_queue.count; i++) {
        if(priority > g_priority_queue.priority[i]) {
            insert_pos = i;
            break;
        }
        insert_pos = i + 1;
    }
    
    // 移动后续元素
    for(uint16_t i = g_priority_queue.count; i > insert_pos; i--) {
        g_priority_queue.buffer[i] = g_priority_queue.buffer[i-1];
        g_priority_queue.priority[i] = g_priority_queue.priority[i-1];
    }
    
    // 插入新事件
    Event_t *event = &g_priority_queue.buffer[insert_pos];
    event->type = type;
    event->timestamp = GetSystemTick();
    event->data = data;
    event->data_size = data_size;
    g_priority_queue.priority[insert_pos] = priority;
    
    g_priority_queue.count++;
    
    __enable_irq();
    
    return true;
}
```

#### 2. 事件合并

避免重复事件占用队列空间：

```c
/**
 * @brief 发布事件（自动合并重复事件）
 */
bool Event_PostMerge(EventType_t type, void *data, uint16_t data_size) {
    __disable_irq();
    
    // 检查队列中是否已有相同类型的事件
    for(uint16_t i = 0; i < g_event_queue.count; i++) {
        uint16_t index = (g_event_queue.tail + i) % EVENT_QUEUE_SIZE;
        if(g_event_queue.buffer[index].type == type) {
            // 更新现有事件的数据
            g_event_queue.buffer[index].timestamp = GetSystemTick();
            g_event_queue.buffer[index].data = data;
            g_event_queue.buffer[index].data_size = data_size;
            __enable_irq();
            return true;
        }
    }
    
    __enable_irq();
    
    // 没有重复事件，正常添加
    return Event_Post(type, data, data_size);
}
```

#### 3. 内存池管理

避免频繁的动态内存分配：

```c
// 事件数据内存池
#define EVENT_DATA_POOL_SIZE 16
#define EVENT_DATA_MAX_SIZE  64

typedef struct {
    uint8_t data[EVENT_DATA_MAX_SIZE];
    bool in_use;
} EventDataBlock_t;

static EventDataBlock_t g_event_data_pool[EVENT_DATA_POOL_SIZE];

/**
 * @brief 从内存池分配事件数据空间
 */
void* EventData_Alloc(uint16_t size) {
    if(size > EVENT_DATA_MAX_SIZE) {
        return NULL;
    }
    
    for(uint8_t i = 0; i < EVENT_DATA_POOL_SIZE; i++) {
        if(!g_event_data_pool[i].in_use) {
            g_event_data_pool[i].in_use = true;
            return g_event_data_pool[i].data;
        }
    }
    
    return NULL;  // 内存池已满
}

/**
 * @brief 释放事件数据空间
 */
void EventData_Free(void *data) {
    for(uint8_t i = 0; i < EVENT_DATA_POOL_SIZE; i++) {
        if(g_event_data_pool[i].data == data) {
            g_event_data_pool[i].in_use = false;
            return;
        }
    }
}

// 使用示例
void PostSensorData(float temperature, float humidity) {
    SensorData_t *data = (SensorData_t *)EventData_Alloc(sizeof(SensorData_t));
    if(data != NULL) {
        data->temperature = temperature;
        data->humidity = humidity;
        Event_Post(EVENT_SENSOR_DATA, data, sizeof(SensorData_t));
    }
}

void OnSensorData(Event_t *event) {
    SensorData_t *data = (SensorData_t *)event->data;
    ProcessSensorData(data);
    EventData_Free(event->data);  // 处理完后释放
}
```


### 常见陷阱和最佳实践

#### 陷阱1：事件队列溢出

**问题**：
```c
// 错误：没有检查返回值
Event_Post(EVENT_DATA, &data, sizeof(data));
// 如果队列满了，事件会丢失
```

**解决方案**：
```c
// 正确：检查返回值并处理失败情况
if(!Event_Post(EVENT_DATA, &data, sizeof(data))) {
    // 队列满，记录错误或采取其他措施
    LogError("Event queue full");
    
    // 可选：丢弃旧事件为新事件腾出空间
    Event_t dummy;
    Event_Get(&dummy);
    Event_Post(EVENT_DATA, &data, sizeof(data));
}
```

#### 陷阱2：事件处理器中阻塞

**问题**：
```c
void OnUARTReceive(Event_t *event) {
    // 错误：在事件处理器中阻塞
    while(!UART_TxReady()) {
        // 等待发送完成
    }
    UART_Send(response);
}
```

**解决方案**：
```c
void OnUARTReceive(Event_t *event) {
    // 正确：使用异步方式
    if(UART_TxReady()) {
        UART_Send(response);
    } else {
        // 稍后重试或发布新事件
        Event_Post(EVENT_UART_TX_PENDING, response, size);
    }
}
```

#### 陷阱3：事件数据生命周期

**问题**：
```c
void PostTemperature(void) {
    float temp = ReadTemperature();
    // 错误：传递栈变量地址
    Event_Post(EVENT_TEMP, &temp, sizeof(temp));
    // temp在函数返回后失效
}
```

**解决方案**：
```c
// 方法1：使用静态变量
void PostTemperature(void) {
    static float temp;
    temp = ReadTemperature();
    Event_Post(EVENT_TEMP, &temp, sizeof(temp));
}

// 方法2：使用内存池
void PostTemperature(void) {
    float *temp = (float *)EventData_Alloc(sizeof(float));
    *temp = ReadTemperature();
    Event_Post(EVENT_TEMP, temp, sizeof(float));
}

// 方法3：在事件结构中直接存储小数据
typedef struct {
    EventType_t type;
    uint32_t timestamp;
    union {
        void *ptr;
        uint32_t value;
        float float_value;
    } data;
} Event_t;
```

#### 最佳实践

**1. 事件命名规范**：
```c
// 使用清晰的命名
EVENT_BUTTON_PRESSED      // 好
EVENT_BTN_P              // 差

EVENT_UART_RX_COMPLETE   // 好
EVENT_U_R_C              // 差
```

**2. 事件处理器设计原则**：
```c
void OnEvent(Event_t *event) {
    // 1. 快速返回：处理器应该尽快完成
    // 2. 不阻塞：避免长时间等待
    // 3. 不递归：避免在处理器中发布同类事件
    // 4. 异常安全：处理所有可能的错误情况
}
```

**3. 事件优先级设计**：
```c
// 定义清晰的优先级层次
#define EVENT_PRIORITY_CRITICAL  0  // 关键事件（错误、安全）
#define EVENT_PRIORITY_HIGH      1  // 高优先级（实时数据）
#define EVENT_PRIORITY_NORMAL    2  // 普通优先级（用户交互）
#define EVENT_PRIORITY_LOW       3  // 低优先级（后台任务）
```

**4. 调试支持**：
```c
// 添加事件跟踪功能
#ifdef DEBUG_EVENTS
void Event_Trace(Event_t *event) {
    printf("[%lu] Event: %d, Data: %p\n",
           event->timestamp, event->type, event->data);
}
#endif

// 统计事件处理情况
typedef struct {
    uint32_t posted;
    uint32_t processed;
    uint32_t dropped;
    uint32_t max_queue_size;
} EventStats_t;

void Event_PrintStats(void) {
    printf("Events Posted: %lu\n", g_stats.posted);
    printf("Events Processed: %lu\n", g_stats.processed);
    printf("Events Dropped: %lu\n", g_stats.dropped);
    printf("Max Queue Size: %lu\n", g_stats.max_queue_size);
}
```


## 常见问题

### Q1: 事件驱动架构和中断有什么区别？

**A**: 两者是互补的，不是替代关系：

**中断**：
- 硬件层面的异步机制
- 由硬件事件触发（GPIO、定时器等）
- 中断服务程序（ISR）应该尽快返回
- 优先级由硬件决定

**事件驱动**：
- 软件层面的架构模式
- 由软件事件触发（可以来自中断）
- 事件处理器在主循环中执行
- 优先级由软件决定

**典型配合方式**：
```c
// 中断中发布事件
void UART_IRQHandler(void) {
    uint8_t data = UART_ReadByte();
    Event_Post(EVENT_UART_RX, &data, sizeof(data));
    // ISR快速返回
}

// 主循环中处理事件
void main(void) {
    while(1) {
        Event_t event;
        if(Event_Get(&event)) {
            Event_Dispatch(&event);  // 详细处理
        }
    }
}
```

### Q2: 事件队列应该设置多大？

**A**: 队列大小取决于多个因素：

**计算公式**：
```
队列大小 >= (事件产生速率 × 最大处理延迟) + 安全余量
```

**考虑因素**：
1. **事件产生速率**：每秒产生多少事件
2. **处理速度**：每秒能处理多少事件
3. **突发情况**：短时间内可能产生的最大事件数
4. **内存限制**：可用RAM大小

**经验值**：
- 简单系统：8-16个事件
- 中等系统：32-64个事件
- 复杂系统：128-256个事件

**动态调整**：
```c
// 监控队列使用情况
void MonitorQueueUsage(void) {
    static uint16_t max_usage = 0;
    uint16_t current = EventQueue_GetCount();
    
    if(current > max_usage) {
        max_usage = current;
        printf("Queue max usage: %u/%u\n", max_usage, EVENT_QUEUE_SIZE);
    }
    
    // 如果经常接近满，考虑增加队列大小
    if(current > EVENT_QUEUE_SIZE * 0.8) {
        printf("Warning: Queue nearly full!\n");
    }
}
```

### Q3: 如何处理事件的优先级？

**A**: 有多种方法实现事件优先级：

**方法1：多个队列**
```c
// 为每个优先级创建独立队列
EventQueue_t high_priority_queue;
EventQueue_t normal_priority_queue;
EventQueue_t low_priority_queue;

void EventLoop_WithPriority(void) {
    Event_t event;
    
    while(1) {
        // 优先处理高优先级队列
        if(Event_GetFrom(&high_priority_queue, &event)) {
            Event_Dispatch(&event);
        } else if(Event_GetFrom(&normal_priority_queue, &event)) {
            Event_Dispatch(&event);
        } else if(Event_GetFrom(&low_priority_queue, &event)) {
            Event_Dispatch(&event);
        } else {
            __WFI();
        }
    }
}
```

**方法2：优先级标记**
```c
// 在事件结构中添加优先级字段
typedef struct {
    EventType_t type;
    uint8_t priority;
    uint32_t timestamp;
    void *data;
} Event_t;

// 获取最高优先级事件
bool Event_GetHighestPriority(Event_t *event) {
    if(EventQueue_IsEmpty()) {
        return false;
    }
    
    // 遍历队列找到最高优先级事件
    uint16_t highest_index = g_event_queue.tail;
    uint8_t highest_priority = 0xFF;
    
    for(uint16_t i = 0; i < g_event_queue.count; i++) {
        uint16_t index = (g_event_queue.tail + i) % EVENT_QUEUE_SIZE;
        if(g_event_queue.buffer[index].priority < highest_priority) {
            highest_priority = g_event_queue.buffer[index].priority;
            highest_index = index;
        }
    }
    
    // 获取并移除该事件
    *event = g_event_queue.buffer[highest_index];
    RemoveEventAt(highest_index);
    
    return true;
}
```

### Q4: 事件驱动架构如何调试？

**A**: 常用的调试方法：

**1. 事件日志**：
```c
#define EVENT_LOG_SIZE 100

typedef struct {
    EventType_t type;
    uint32_t timestamp;
    const char *handler_name;
} EventLogEntry_t;

EventLogEntry_t g_event_log[EVENT_LOG_SIZE];
uint16_t g_log_index = 0;

void Event_Log(EventType_t type, const char *handler) {
    EventLogEntry_t *entry = &g_event_log[g_log_index];
    entry->type = type;
    entry->timestamp = GetSystemTick();
    entry->handler_name = handler;
    
    g_log_index = (g_log_index + 1) % EVENT_LOG_SIZE;
}

void Event_PrintLog(void) {
    printf("Event Log:\n");
    for(uint16_t i = 0; i < EVENT_LOG_SIZE; i++) {
        EventLogEntry_t *entry = &g_event_log[i];
        if(entry->type != EVENT_NONE) {
            printf("[%lu] Event %d -> %s\n",
                   entry->timestamp, entry->type, entry->handler_name);
        }
    }
}
```

**2. 断点调试**：
```c
// 在关键位置设置断点
void Event_Dispatch(Event_t *event) {
    if(event->type == EVENT_DEBUG_BREAK) {
        __BKPT(0);  // 触发断点
    }
    // 正常分发
}
```

**3. 性能分析**：
```c
void Event_Dispatch(Event_t *event) {
    uint32_t start = GetCycleCount();
    
    // 调用处理器
    EventHandler_t handler = g_event_handlers[event->type];
    if(handler != NULL) {
        handler(event);
    }
    
    uint32_t elapsed = GetCycleCount() - start;
    
    // 记录处理时间
    if(elapsed > MAX_HANDLER_TIME) {
        printf("Warning: Handler %d took %lu cycles\n",
               event->type, elapsed);
    }
}
```


## 总结

事件驱动架构是构建高响应性、低耦合嵌入式系统的有效方法。通过本文学习，你应该掌握了：

### 核心知识点

1. **事件驱动概念**
   - 事件、事件源、事件处理器
   - 事件队列和事件分发
   - 异步处理机制

2. **实现技术**
   - 环形缓冲区实现事件队列
   - 多种事件分发机制（switch-case、函数指针表、订阅发布）
   - 事件循环设计
   - 与状态机结合

3. **设计原则**
   - 模块解耦
   - 快速响应
   - 易于扩展
   - 资源高效

### 关键要点

- **解耦设计**：模块通过事件通信，降低耦合度
- **异步处理**：事件驱动天然支持异步操作
- **响应性**：事件立即处理，无需轮询等待
- **可扩展**：添加新功能只需注册新的事件处理器
- **资源管理**：注意事件队列大小和数据生命周期

### 适用场景

事件驱动架构特别适合：
- 用户界面交互系统
- 通信协议处理
- 传感器数据采集
- 多模块协作系统
- 需要快速响应的应用

不适合：
- 简单的顺序任务
- 资源极度受限的系统
- 硬实时控制回路

### 与其他架构的关系

- **超级循环**：事件驱动是超级循环的改进，解决了轮询效率问题
- **时间片调度**：可以结合使用，事件处理器作为任务运行
- **状态机**：完美配合，事件驱动状态转换
- **RTOS**：事件驱动是RTOS的简化版，适合中等复杂度系统

### 下一步学习

掌握事件驱动架构后，建议继续学习：

1. **协作式调度器**：结合事件驱动和多任务
2. **RTOS基础**：学习完整的实时操作系统
3. **设计模式**：观察者模式、命令模式等
4. **异步编程**：深入理解异步处理机制

## 延伸阅读

推荐进一步学习的资源：

- [协作式多任务调度器实现](01-cooperative-scheduler.html) - 结合事件驱动和任务调度
- [状态机设计模式实战](../beginner/03-state-machine.html) - 事件驱动状态机
- [环形缓冲区设计与实现](../beginner/06-ring-buffer.html) - 事件队列的基础
- [RTOS基础](../../02-rtos-fundamentals/beginner/01-rtos-overview.html) - 学习专业的事件处理机制

## 参考资料

1. "Design Patterns: Elements of Reusable Object-Oriented Software" - Gang of Four
2. "Event-Driven Architecture: How SOA Enables the Real-Time Enterprise" - Hugh Taylor
3. "Patterns in C" - Adam Tornhill
4. "Embedded Systems Architecture" - Tammy Noergaard
5. "Real-Time C++: Efficient Object-Oriented and Template Microcontroller Programming" - Christopher Kormanyos

## 练习题

### 基础练习

1. **简单事件系统**：实现一个包含按键和LED的事件驱动系统
   - 按键按下发布事件
   - LED处理器响应事件
   - 使用环形缓冲区实现事件队列

2. **事件统计**：为事件系统添加统计功能
   - 记录每种事件的发布次数
   - 记录事件处理时间
   - 检测队列溢出情况

3. **订阅发布**：实现订阅发布模式
   - 支持多个处理器订阅同一事件
   - 实现订阅和取消订阅功能
   - 测试多个模块协作

### 进阶练习

4. **优先级事件队列**：实现带优先级的事件队列
   - 高优先级事件优先处理
   - 防止低优先级事件饥饿
   - 性能对比测试

5. **异步操作框架**：实现异步操作支持
   - 异步ADC读取
   - 异步UART通信
   - 回调函数机制

6. **事件驱动状态机**：结合状态机和事件驱动
   - 实现一个完整的状态机
   - 事件驱动状态转换
   - 超时检测和错误处理

### 项目练习

7. **智能家居控制器**：
   - 按键控制（开关、调节）
   - 传感器监控（温度、湿度）
   - 显示更新
   - 无线通信（WiFi/蓝牙）
   - 所有模块通过事件通信

8. **数据采集系统**：
   - 多路传感器采集
   - 数据处理和存储
   - 实时显示
   - 远程上传
   - 使用事件驱动架构解耦各模块

### 挑战练习

9. **性能对比**：
   - 实现超级循环、时间片调度、事件驱动三种架构
   - 对比响应时间、CPU利用率、内存占用
   - 分析各自的优缺点

10. **完整框架**：
    - 设计一个通用的事件驱动框架
    - 支持优先级、订阅发布、异步操作
    - 提供调试和性能分析工具
    - 编写完整的文档和示例

---

**下一步**：建议学习 [协作式多任务调度器实现](01-cooperative-scheduler.html)，了解如何将事件驱动与任务调度结合，或者学习 [命令行接口(CLI)实现](03-cli-implementation.html)，实践事件驱动在交互系统中的应用。

**反馈**：如果你在学习过程中遇到问题，欢迎在讨论区提问，或者通过邮件联系我们。

**版权声明**：本教程采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
