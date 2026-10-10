---
title: "GUI设计模式与架构：构建可维护的嵌入式图形界面"
description: "本文深入讲解嵌入式GUI开发中的核心设计模式，包括MVC模式、事件驱动架构、界面分层设计和状态管理，帮助你构建结构清晰、易于维护的图形界面系统"
slug: "gui-design-patterns-architecture"

# 分类信息
domain: "中间件层"
module: "图形与显示"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - GUI设计
  - 设计模式
  - 界面架构
  - MVC模式
  - 事件驱动
  - 状态管理
prerequisites:
  - "04-middleware-layer/03-graphics-display/beginner/01-lvgl-quickstart"
  - "04-middleware-layer/03-graphics-display/beginner/03-display-driver"
related_contents:
  - "04-middleware-layer/03-graphics-display/intermediate/02-graphics-optimization"
  - "04-middleware-layer/03-graphics-display/advanced/01-smart-home-panel"

# 学习信息
estimated_time: 50
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
  - GUI设计模式
  - 嵌入式界面架构
  - MVC模式
  - 事件驱动设计
  - 状态管理
  - 界面分层
cover_image: ""
---

# GUI设计模式与架构：构建可维护的嵌入式图形界面

## 概述

在嵌入式系统中开发图形用户界面(GUI)时，良好的架构设计至关重要。随着功能的增加和需求的变化，没有清晰架构的GUI代码会变得难以维护和扩展。本文将介绍嵌入式GUI开发中常用的设计模式和架构原则，帮助你构建结构清晰、易于维护的图形界面系统。

### 为什么需要GUI设计模式？

**常见问题**：
- 界面逻辑和业务逻辑混杂在一起
- 代码耦合度高，修改一处影响多处
- 难以进行单元测试
- 团队协作困难
- 功能扩展时需要大量重构

**设计模式的价值**：
- ✅ 分离关注点，降低耦合度
- ✅ 提高代码可读性和可维护性
- ✅ 便于单元测试和调试
- ✅ 支持团队协作开发
- ✅ 易于功能扩展和修改

### 学习目标

完成本文学习后，你将能够：

- [ ] 理解GUI架构设计的核心原则
- [ ] 掌握MVC设计模式及其在嵌入式系统中的应用
- [ ] 理解事件驱动架构的工作机制
- [ ] 掌握界面分层设计方法
- [ ] 实现有效的状态管理机制
- [ ] 选择适合项目的GUI架构方案

## 背景知识

### GUI架构的核心原则

#### 1. 关注点分离 (Separation of Concerns)

将不同职责的代码分离到不同的模块中：

```
界面显示 ← → 业务逻辑 ← → 数据管理
```

**好处**：
- 每个模块职责单一，易于理解
- 修改一个模块不影响其他模块
- 可以独立测试每个模块

#### 2. 低耦合高内聚 (Low Coupling, High Cohesion)

**低耦合**：模块之间的依赖关系尽可能少
**高内聚**：模块内部的功能紧密相关

```c
// 低耦合示例：通过接口通信
typedef struct {
    void (*update)(void* data);
    void (*render)(void);
} View_Interface_t;

// 高内聚示例：相关功能组织在一起
typedef struct {
    void (*init)(void);
    void (*start)(void);
    void (*stop)(void);
    void (*update)(void);
} Timer_Module_t;
```

#### 3. 单一职责原则 (Single Responsibility Principle)

每个模块或类只负责一个功能：

```c
// ❌ 不好的设计：一个函数做太多事情
void button_handler(void) {
    read_sensor();      // 读传感器
    update_display();   // 更新显示
    save_to_flash();    // 保存数据
    send_to_cloud();    // 发送到云端
}

// ✅ 好的设计：职责分离
void button_handler(void) {
    trigger_event(EVENT_BUTTON_PRESSED);
}

void on_button_pressed(void) {
    controller_handle_button();
}
```



## MVC设计模式

### MVC模式概述

MVC (Model-View-Controller) 是最经典的GUI架构模式，将应用分为三个核心组件：

```
┌─────────────┐
│    View     │ ← 显示界面
│  (视图层)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Controller  │ ← 处理交互
│  (控制器)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│    Model    │ ← 管理数据
│  (模型层)    │
└─────────────┘
```

**三层职责**：

1. **Model (模型层)**
   - 管理应用数据和业务逻辑
   - 不依赖于界面实现
   - 数据变化时通知观察者

2. **View (视图层)**
   - 负责界面显示
   - 从Model获取数据并展示
   - 将用户操作传递给Controller

3. **Controller (控制器)**
   - 处理用户输入
   - 更新Model数据
   - 协调Model和View

### MVC在嵌入式系统中的实现

#### 示例：温度监控系统

**Model层实现**：

```c
/* temperature_model.h */
#ifndef TEMPERATURE_MODEL_H
#define TEMPERATURE_MODEL_H

#include <stdint.h>
#include <stdbool.h>

/* 温度数据模型 */
typedef struct {
    float current_temp;      // 当前温度
    float max_temp;          // 最高温度
    float min_temp;          // 最低温度
    float threshold;         // 阈值
    bool alarm_active;       // 报警状态
} Temperature_Model_t;

/* 观察者回调函数类型 */
typedef void (*Model_Observer_t)(Temperature_Model_t* model);

/* Model接口函数 */
void Temperature_Model_Init(void);
void Temperature_Model_SetTemperature(float temp);
void Temperature_Model_SetThreshold(float threshold);
float Temperature_Model_GetCurrent(void);
float Temperature_Model_GetThreshold(void);
bool Temperature_Model_IsAlarmActive(void);
void Temperature_Model_RegisterObserver(Model_Observer_t observer);

#endif
```

```c
/* temperature_model.c */
#include "temperature_model.h"
#include <string.h>

/* 私有数据 */
static Temperature_Model_t model_data;
static Model_Observer_t observers[5];
static uint8_t observer_count = 0;

/**
 * @brief  初始化温度模型
 */
void Temperature_Model_Init(void)
{
    memset(&model_data, 0, sizeof(model_data));
    model_data.threshold = 30.0f;  // 默认阈值30度
    model_data.min_temp = 100.0f;  // 初始化最小值
    observer_count = 0;
}

/**
 * @brief  设置当前温度
 * @param  temp: 温度值
 */
void Temperature_Model_SetTemperature(float temp)
{
    model_data.current_temp = temp;
    
    /* 更新最大最小值 */
    if (temp > model_data.max_temp) {
        model_data.max_temp = temp;
    }
    if (temp < model_data.min_temp) {
        model_data.min_temp = temp;
    }
    
    /* 检查报警条件 */
    model_data.alarm_active = (temp > model_data.threshold);
    
    /* 通知所有观察者 */
    for (uint8_t i = 0; i < observer_count; i++) {
        if (observers[i] != NULL) {
            observers[i](&model_data);
        }
    }
}

/**
 * @brief  设置温度阈值
 * @param  threshold: 阈值
 */
void Temperature_Model_SetThreshold(float threshold)
{
    model_data.threshold = threshold;
    
    /* 重新检查报警状态 */
    model_data.alarm_active = (model_data.current_temp > threshold);
    
    /* 通知观察者 */
    for (uint8_t i = 0; i < observer_count; i++) {
        if (observers[i] != NULL) {
            observers[i](&model_data);
        }
    }
}

/**
 * @brief  注册观察者
 * @param  observer: 观察者回调函数
 */
void Temperature_Model_RegisterObserver(Model_Observer_t observer)
{
    if (observer_count < 5) {
        observers[observer_count++] = observer;
    }
}

/* Getter函数 */
float Temperature_Model_GetCurrent(void) {
    return model_data.current_temp;
}

float Temperature_Model_GetThreshold(void) {
    return model_data.threshold;
}

bool Temperature_Model_IsAlarmActive(void) {
    return model_data.alarm_active;
}
```

**View层实现**：

```c
/* temperature_view.h */
#ifndef TEMPERATURE_VIEW_H
#define TEMPERATURE_VIEW_H

#include "lvgl.h"
#include "temperature_model.h"

/* View接口函数 */
void Temperature_View_Init(void);
void Temperature_View_Update(Temperature_Model_t* model);
void Temperature_View_SetEventCallback(void (*callback)(lv_event_t*));

#endif
```

```c
/* temperature_view.c */
#include "temperature_view.h"

/* UI对象 */
static lv_obj_t* temp_label;
static lv_obj_t* threshold_slider;
static lv_obj_t* alarm_indicator;
static lv_obj_t* chart;
static lv_chart_series_t* temp_series;

/* 事件回调 */
static void (*event_callback)(lv_event_t*) = NULL;

/**
 * @brief  滑块值改变事件
 */
static void slider_event_handler(lv_event_t* e)
{
    if (event_callback != NULL) {
        event_callback(e);
    }
}

/**
 * @brief  初始化视图
 */
void Temperature_View_Init(void)
{
    /* 创建温度显示标签 */
    temp_label = lv_label_create(lv_scr_act());
    lv_label_set_text(temp_label, "25.0°C");
    lv_obj_align(temp_label, LV_ALIGN_TOP_MID, 0, 20);
    lv_obj_set_style_text_font(temp_label, &lv_font_montserrat_32, 0);
    
    /* 创建阈值滑块 */
    threshold_slider = lv_slider_create(lv_scr_act());
    lv_obj_set_width(threshold_slider, 200);
    lv_obj_align(threshold_slider, LV_ALIGN_CENTER, 0, 0);
    lv_slider_set_range(threshold_slider, 20, 40);
    lv_slider_set_value(threshold_slider, 30, LV_ANIM_OFF);
    lv_obj_add_event_cb(threshold_slider, slider_event_handler, 
                        LV_EVENT_VALUE_CHANGED, NULL);
    
    /* 创建报警指示器 */
    alarm_indicator = lv_led_create(lv_scr_act());
    lv_obj_align(alarm_indicator, LV_ALIGN_TOP_RIGHT, -20, 20);
    lv_led_off(alarm_indicator);
    
    /* 创建温度曲线图 */
    chart = lv_chart_create(lv_scr_act());
    lv_obj_set_size(chart, 200, 100);
    lv_obj_align(chart, LV_ALIGN_BOTTOM_MID, 0, -20);
    lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
    lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, 0, 50);
    lv_chart_set_point_count(chart, 20);
    
    temp_series = lv_chart_add_series(chart, 
                                      lv_palette_main(LV_PALETTE_RED),
                                      LV_CHART_AXIS_PRIMARY_Y);
}

/**
 * @brief  更新视图显示
 * @param  model: 数据模型
 */
void Temperature_View_Update(Temperature_Model_t* model)
{
    /* 更新温度显示 */
    lv_label_set_text_fmt(temp_label, "%.1f°C", model->current_temp);
    
    /* 更新报警指示器 */
    if (model->alarm_active) {
        lv_led_on(alarm_indicator);
        lv_led_set_color(alarm_indicator, lv_palette_main(LV_PALETTE_RED));
    } else {
        lv_led_off(alarm_indicator);
    }
    
    /* 更新曲线图 */
    lv_chart_set_next_value(chart, temp_series, (int32_t)model->current_temp);
}

/**
 * @brief  设置事件回调
 * @param  callback: 回调函数
 */
void Temperature_View_SetEventCallback(void (*callback)(lv_event_t*))
{
    event_callback = callback;
}
```



**Controller层实现**：

```c
/* temperature_controller.h */
#ifndef TEMPERATURE_CONTROLLER_H
#define TEMPERATURE_CONTROLLER_H

#include "lvgl.h"

/* Controller接口函数 */
void Temperature_Controller_Init(void);
void Temperature_Controller_UpdateTemperature(float temp);

#endif
```

```c
/* temperature_controller.c */
#include "temperature_controller.h"
#include "temperature_model.h"
#include "temperature_view.h"

/**
 * @brief  Model数据变化观察者
 * @param  model: 数据模型
 */
static void model_changed_observer(Temperature_Model_t* model)
{
    /* Model变化时更新View */
    Temperature_View_Update(model);
}

/**
 * @brief  View事件处理
 * @param  e: 事件对象
 */
static void view_event_handler(lv_event_t* e)
{
    lv_obj_t* slider = lv_event_get_target(e);
    
    /* 获取滑块值 */
    int32_t value = lv_slider_get_value(slider);
    
    /* 更新Model */
    Temperature_Model_SetThreshold((float)value);
}

/**
 * @brief  初始化控制器
 */
void Temperature_Controller_Init(void)
{
    /* 初始化Model */
    Temperature_Model_Init();
    
    /* 初始化View */
    Temperature_View_Init();
    
    /* 注册Model观察者 */
    Temperature_Model_RegisterObserver(model_changed_observer);
    
    /* 设置View事件回调 */
    Temperature_View_SetEventCallback(view_event_handler);
}

/**
 * @brief  更新温度数据
 * @param  temp: 温度值
 */
void Temperature_Controller_UpdateTemperature(float temp)
{
    /* 更新Model，Model会自动通知View */
    Temperature_Model_SetTemperature(temp);
}
```

**主程序使用**：

```c
/* main.c */
#include "temperature_controller.h"

int main(void)
{
    /* 系统初始化 */
    HAL_Init();
    SystemClock_Config();
    
    /* 初始化LVGL */
    lv_init();
    lv_port_disp_init();
    lv_port_indev_init();
    
    /* 初始化温度监控系统 */
    Temperature_Controller_Init();
    
    /* 主循环 */
    while (1)
    {
        /* 读取温度传感器 */
        float temp = read_temperature_sensor();
        
        /* 更新温度 */
        Temperature_Controller_UpdateTemperature(temp);
        
        /* 处理LVGL任务 */
        lv_timer_handler();
        
        HAL_Delay(100);
    }
}
```

### MVC模式的优势

**代码组织清晰**：
- Model专注于数据和业务逻辑
- View专注于界面显示
- Controller协调两者

**易于测试**：
```c
/* 可以独立测试Model */
void test_temperature_model(void)
{
    Temperature_Model_Init();
    Temperature_Model_SetTemperature(35.0f);
    assert(Temperature_Model_IsAlarmActive() == true);
}
```

**易于扩展**：
```c
/* 可以轻松添加新的View */
void Temperature_View_LCD_Init(void);  // LCD显示
void Temperature_View_OLED_Init(void); // OLED显示
void Temperature_View_Web_Init(void);  // Web界面
```



## 事件驱动架构

### 事件驱动模式概述

事件驱动架构通过事件来解耦组件之间的依赖关系：

```
┌──────────┐    Event    ┌──────────┐
│ Producer │ ─────────→  │ Event    │
│  (生产者) │             │  Queue   │
└──────────┘             └────┬─────┘
                              │
                              ↓
                         ┌──────────┐
                         │ Consumer │
                         │  (消费者) │
                         └──────────┘
```

**核心概念**：

1. **事件 (Event)**：表示发生的动作或状态变化
2. **事件源 (Event Source)**：产生事件的组件
3. **事件处理器 (Event Handler)**：响应事件的函数
4. **事件分发器 (Event Dispatcher)**：将事件路由到处理器

### 事件系统实现

**事件定义**：

```c
/* event_system.h */
#ifndef EVENT_SYSTEM_H
#define EVENT_SYSTEM_H

#include <stdint.h>
#include <stdbool.h>

/* 事件类型 */
typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESSED,
    EVENT_BUTTON_RELEASED,
    EVENT_BUTTON_LONG_PRESS,
    EVENT_TEMPERATURE_CHANGED,
    EVENT_ALARM_TRIGGERED,
    EVENT_THRESHOLD_CHANGED,
    EVENT_MAX
} Event_Type_t;

/* 事件数据结构 */
typedef struct {
    Event_Type_t type;      // 事件类型
    uint32_t timestamp;     // 时间戳
    void* data;             // 事件数据
    uint32_t data_size;     // 数据大小
} Event_t;

/* 事件处理器类型 */
typedef void (*Event_Handler_t)(Event_t* event);

/* 事件系统接口 */
void Event_System_Init(void);
bool Event_Post(Event_Type_t type, void* data, uint32_t size);
void Event_Subscribe(Event_Type_t type, Event_Handler_t handler);
void Event_Unsubscribe(Event_Type_t type, Event_Handler_t handler);
void Event_Process(void);

#endif
```

**事件系统实现**：

```c
/* event_system.c */
#include "event_system.h"
#include <string.h>

/* 事件队列大小 */
#define EVENT_QUEUE_SIZE 32

/* 最大订阅者数量 */
#define MAX_SUBSCRIBERS 10

/* 事件队列 */
static Event_t event_queue[EVENT_QUEUE_SIZE];
static uint8_t queue_head = 0;
static uint8_t queue_tail = 0;
static uint8_t queue_count = 0;

/* 订阅者列表 */
typedef struct {
    Event_Type_t type;
    Event_Handler_t handlers[MAX_SUBSCRIBERS];
    uint8_t handler_count;
} Subscriber_List_t;

static Subscriber_List_t subscribers[EVENT_MAX];

/**
 * @brief  初始化事件系统
 */
void Event_System_Init(void)
{
    memset(event_queue, 0, sizeof(event_queue));
    memset(subscribers, 0, sizeof(subscribers));
    queue_head = 0;
    queue_tail = 0;
    queue_count = 0;
}

/**
 * @brief  发送事件
 * @param  type: 事件类型
 * @param  data: 事件数据
 * @param  size: 数据大小
 * @retval true=成功, false=队列满
 */
bool Event_Post(Event_Type_t type, void* data, uint32_t size)
{
    if (queue_count >= EVENT_QUEUE_SIZE) {
        return false;  // 队列满
    }
    
    /* 添加事件到队列 */
    Event_t* event = &event_queue[queue_tail];
    event->type = type;
    event->timestamp = HAL_GetTick();
    event->data = data;
    event->data_size = size;
    
    /* 更新队列指针 */
    queue_tail = (queue_tail + 1) % EVENT_QUEUE_SIZE;
    queue_count++;
    
    return true;
}

/**
 * @brief  订阅事件
 * @param  type: 事件类型
 * @param  handler: 处理函数
 */
void Event_Subscribe(Event_Type_t type, Event_Handler_t handler)
{
    if (type >= EVENT_MAX || handler == NULL) {
        return;
    }
    
    Subscriber_List_t* list = &subscribers[type];
    
    /* 检查是否已订阅 */
    for (uint8_t i = 0; i < list->handler_count; i++) {
        if (list->handlers[i] == handler) {
            return;  // 已经订阅
        }
    }
    
    /* 添加订阅者 */
    if (list->handler_count < MAX_SUBSCRIBERS) {
        list->handlers[list->handler_count++] = handler;
        list->type = type;
    }
}

/**
 * @brief  取消订阅
 * @param  type: 事件类型
 * @param  handler: 处理函数
 */
void Event_Unsubscribe(Event_Type_t type, Event_Handler_t handler)
{
    if (type >= EVENT_MAX || handler == NULL) {
        return;
    }
    
    Subscriber_List_t* list = &subscribers[type];
    
    /* 查找并移除订阅者 */
    for (uint8_t i = 0; i < list->handler_count; i++) {
        if (list->handlers[i] == handler) {
            /* 移动后续元素 */
            for (uint8_t j = i; j < list->handler_count - 1; j++) {
                list->handlers[j] = list->handlers[j + 1];
            }
            list->handler_count--;
            break;
        }
    }
}

/**
 * @brief  处理事件队列
 */
void Event_Process(void)
{
    while (queue_count > 0) {
        /* 获取队列头部事件 */
        Event_t* event = &event_queue[queue_head];
        
        /* 分发事件给订阅者 */
        if (event->type < EVENT_MAX) {
            Subscriber_List_t* list = &subscribers[event->type];
            for (uint8_t i = 0; i < list->handler_count; i++) {
                if (list->handlers[i] != NULL) {
                    list->handlers[i](event);
                }
            }
        }
        
        /* 更新队列指针 */
        queue_head = (queue_head + 1) % EVENT_QUEUE_SIZE;
        queue_count--;
    }
}
```

**使用事件系统**：

```c
/* 按钮事件处理器 */
void on_button_pressed(Event_t* event)
{
    printf("Button pressed at %lu ms\n", event->timestamp);
    
    /* 触发其他事件 */
    Event_Post(EVENT_TEMPERATURE_CHANGED, NULL, 0);
}

/* 温度变化处理器 */
void on_temperature_changed(Event_t* event)
{
    float* temp = (float*)event->data;
    printf("Temperature changed: %.1f°C\n", *temp);
    
    /* 更新界面 */
    update_temperature_display(*temp);
}

/* 报警处理器 */
void on_alarm_triggered(Event_t* event)
{
    printf("Alarm triggered!\n");
    
    /* 播放报警音 */
    play_alarm_sound();
    
    /* 发送通知 */
    send_notification();
}

/* 初始化 */
void app_init(void)
{
    /* 初始化事件系统 */
    Event_System_Init();
    
    /* 订阅事件 */
    Event_Subscribe(EVENT_BUTTON_PRESSED, on_button_pressed);
    Event_Subscribe(EVENT_TEMPERATURE_CHANGED, on_temperature_changed);
    Event_Subscribe(EVENT_ALARM_TRIGGERED, on_alarm_triggered);
}

/* 主循环 */
void app_main(void)
{
    while (1) {
        /* 处理事件 */
        Event_Process();
        
        /* 其他任务 */
        lv_timer_handler();
        
        HAL_Delay(10);
    }
}

/* 按钮中断 */
void button_interrupt_handler(void)
{
    /* 发送按钮事件 */
    Event_Post(EVENT_BUTTON_PRESSED, NULL, 0);
}

/* 温度传感器任务 */
void temperature_task(void)
{
    static float last_temp = 0.0f;
    float current_temp = read_temperature();
    
    /* 温度变化超过0.5度时发送事件 */
    if (fabs(current_temp - last_temp) > 0.5f) {
        Event_Post(EVENT_TEMPERATURE_CHANGED, &current_temp, sizeof(float));
        last_temp = current_temp;
    }
}
```

### 事件驱动的优势

**解耦组件**：
- 事件源不需要知道谁在监听
- 监听者不需要知道事件来自哪里
- 可以动态添加/移除监听者

**异步处理**：
- 事件可以延迟处理
- 不阻塞事件源的执行
- 支持优先级处理

**易于扩展**：
```c
/* 添加新的事件处理器很简单 */
void on_new_event(Event_t* event) {
    // 处理逻辑
}

Event_Subscribe(EVENT_BUTTON_PRESSED, on_new_event);
```



## 界面分层设计

### 分层架构概述

将GUI系统分为多个层次，每层有明确的职责：

```
┌─────────────────────────────┐
│   Application Layer         │ ← 应用逻辑层
│   (业务逻辑)                 │
├─────────────────────────────┤
│   Presentation Layer        │ ← 表示层
│   (界面控制)                 │
├─────────────────────────────┤
│   Widget Layer              │ ← 控件层
│   (UI组件)                   │
├─────────────────────────────┤
│   Graphics Layer            │ ← 图形层
│   (绘图引擎)                 │
├─────────────────────────────┤
│   Driver Layer              │ ← 驱动层
│   (硬件驱动)                 │
└─────────────────────────────┘
```

### 各层职责

#### 1. 驱动层 (Driver Layer)

负责与硬件交互：

```c
/* display_driver.h */
typedef struct {
    void (*init)(void);
    void (*set_pixel)(uint16_t x, uint16_t y, uint16_t color);
    void (*fill_rect)(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
    void (*flush)(void);
} Display_Driver_t;

/* 具体驱动实现 */
Display_Driver_t ili9341_driver = {
    .init = ili9341_init,
    .set_pixel = ili9341_set_pixel,
    .fill_rect = ili9341_fill_rect,
    .flush = ili9341_flush
};
```

#### 2. 图形层 (Graphics Layer)

提供基本绘图功能：

```c
/* graphics.h */
typedef struct {
    Display_Driver_t* driver;
    uint16_t width;
    uint16_t height;
} Graphics_Context_t;

/* 图形API */
void Graphics_Init(Graphics_Context_t* ctx, Display_Driver_t* driver);
void Graphics_DrawLine(Graphics_Context_t* ctx, int x1, int y1, int x2, int y2, uint16_t color);
void Graphics_DrawRect(Graphics_Context_t* ctx, int x, int y, int w, int h, uint16_t color);
void Graphics_DrawCircle(Graphics_Context_t* ctx, int x, int y, int r, uint16_t color);
void Graphics_DrawText(Graphics_Context_t* ctx, int x, int y, const char* text, uint16_t color);
```

#### 3. 控件层 (Widget Layer)

实现可复用的UI组件：

```c
/* widget.h */
typedef struct Widget Widget_t;

/* 控件基类 */
struct Widget {
    int x, y;
    int width, height;
    bool visible;
    bool enabled;
    
    /* 虚函数表 */
    void (*draw)(Widget_t* self, Graphics_Context_t* ctx);
    void (*on_event)(Widget_t* self, Event_t* event);
    void (*destroy)(Widget_t* self);
};

/* 按钮控件 */
typedef struct {
    Widget_t base;          // 继承基类
    char* text;
    uint16_t bg_color;
    uint16_t text_color;
    void (*on_click)(void);
} Button_Widget_t;

/* 标签控件 */
typedef struct {
    Widget_t base;
    char* text;
    uint16_t color;
} Label_Widget_t;
```

**控件实现示例**：

```c
/* button_widget.c */
#include "widget.h"

/**
 * @brief  绘制按钮
 */
static void button_draw(Widget_t* self, Graphics_Context_t* ctx)
{
    Button_Widget_t* btn = (Button_Widget_t*)self;
    
    if (!self->visible) return;
    
    /* 绘制背景 */
    Graphics_FillRect(ctx, self->x, self->y, self->width, self->height, btn->bg_color);
    
    /* 绘制边框 */
    Graphics_DrawRect(ctx, self->x, self->y, self->width, self->height, 0x0000);
    
    /* 绘制文本 */
    int text_x = self->x + (self->width - strlen(btn->text) * 8) / 2;
    int text_y = self->y + (self->height - 16) / 2;
    Graphics_DrawText(ctx, text_x, text_y, btn->text, btn->text_color);
}

/**
 * @brief  处理按钮事件
 */
static void button_on_event(Widget_t* self, Event_t* event)
{
    Button_Widget_t* btn = (Button_Widget_t*)self;
    
    if (!self->enabled) return;
    
    if (event->type == EVENT_TOUCH_PRESSED) {
        Touch_Event_t* touch = (Touch_Event_t*)event->data;
        
        /* 检查触摸点是否在按钮范围内 */
        if (touch->x >= self->x && touch->x < self->x + self->width &&
            touch->y >= self->y && touch->y < self->y + self->height) {
            
            /* 触发点击回调 */
            if (btn->on_click != NULL) {
                btn->on_click();
            }
        }
    }
}

/**
 * @brief  创建按钮控件
 */
Button_Widget_t* Button_Create(int x, int y, int width, int height, const char* text)
{
    Button_Widget_t* btn = malloc(sizeof(Button_Widget_t));
    
    /* 初始化基类 */
    btn->base.x = x;
    btn->base.y = y;
    btn->base.width = width;
    btn->base.height = height;
    btn->base.visible = true;
    btn->base.enabled = true;
    btn->base.draw = button_draw;
    btn->base.on_event = button_on_event;
    
    /* 初始化按钮属性 */
    btn->text = strdup(text);
    btn->bg_color = 0x001F;  // 蓝色
    btn->text_color = 0xFFFF; // 白色
    btn->on_click = NULL;
    
    return btn;
}
```

#### 4. 表示层 (Presentation Layer)

管理界面和控件：

```c
/* screen.h */
typedef struct {
    Widget_t** widgets;     // 控件列表
    uint16_t widget_count;
    uint16_t widget_capacity;
    bool needs_redraw;
} Screen_t;

/* 屏幕管理 */
Screen_t* Screen_Create(void);
void Screen_AddWidget(Screen_t* screen, Widget_t* widget);
void Screen_RemoveWidget(Screen_t* screen, Widget_t* widget);
void Screen_Draw(Screen_t* screen, Graphics_Context_t* ctx);
void Screen_HandleEvent(Screen_t* screen, Event_t* event);
```

```c
/* screen.c */
#include "screen.h"

/**
 * @brief  创建屏幕
 */
Screen_t* Screen_Create(void)
{
    Screen_t* screen = malloc(sizeof(Screen_t));
    screen->widget_capacity = 10;
    screen->widgets = malloc(sizeof(Widget_t*) * screen->widget_capacity);
    screen->widget_count = 0;
    screen->needs_redraw = true;
    return screen;
}

/**
 * @brief  添加控件
 */
void Screen_AddWidget(Screen_t* screen, Widget_t* widget)
{
    if (screen->widget_count >= screen->widget_capacity) {
        /* 扩容 */
        screen->widget_capacity *= 2;
        screen->widgets = realloc(screen->widgets, 
                                  sizeof(Widget_t*) * screen->widget_capacity);
    }
    
    screen->widgets[screen->widget_count++] = widget;
    screen->needs_redraw = true;
}

/**
 * @brief  绘制屏幕
 */
void Screen_Draw(Screen_t* screen, Graphics_Context_t* ctx)
{
    if (!screen->needs_redraw) return;
    
    /* 清屏 */
    Graphics_Clear(ctx, 0x0000);
    
    /* 绘制所有控件 */
    for (uint16_t i = 0; i < screen->widget_count; i++) {
        Widget_t* widget = screen->widgets[i];
        if (widget->draw != NULL) {
            widget->draw(widget, ctx);
        }
    }
    
    screen->needs_redraw = false;
}

/**
 * @brief  处理事件
 */
void Screen_HandleEvent(Screen_t* screen, Event_t* event)
{
    /* 将事件分发给所有控件 */
    for (uint16_t i = 0; i < screen->widget_count; i++) {
        Widget_t* widget = screen->widgets[i];
        if (widget->on_event != NULL) {
            widget->on_event(widget, event);
        }
    }
    
    screen->needs_redraw = true;
}
```

#### 5. 应用层 (Application Layer)

实现具体的业务逻辑：

```c
/* app_main.c */
#include "screen.h"
#include "button_widget.h"
#include "label_widget.h"

static Screen_t* main_screen;
static Label_Widget_t* temp_label;
static Button_Widget_t* start_btn;
static Button_Widget_t* stop_btn;

/* 按钮点击回调 */
void on_start_clicked(void)
{
    printf("Start button clicked\n");
    start_monitoring();
}

void on_stop_clicked(void)
{
    printf("Stop button clicked\n");
    stop_monitoring();
}

/**
 * @brief  创建主界面
 */
void create_main_screen(void)
{
    /* 创建屏幕 */
    main_screen = Screen_Create();
    
    /* 创建温度标签 */
    temp_label = Label_Create(60, 20, "Temperature: --°C");
    Screen_AddWidget(main_screen, (Widget_t*)temp_label);
    
    /* 创建开始按钮 */
    start_btn = Button_Create(40, 100, 80, 40, "Start");
    start_btn->on_click = on_start_clicked;
    Screen_AddWidget(main_screen, (Widget_t*)start_btn);
    
    /* 创建停止按钮 */
    stop_btn = Button_Create(140, 100, 80, 40, "Stop");
    stop_btn->on_click = on_stop_clicked;
    Screen_AddWidget(main_screen, (Widget_t*)stop_btn);
}

/**
 * @brief  更新温度显示
 */
void update_temperature(float temp)
{
    char buf[32];
    snprintf(buf, sizeof(buf), "Temperature: %.1f°C", temp);
    Label_SetText(temp_label, buf);
    main_screen->needs_redraw = true;
}
```

### 分层设计的优势

**职责清晰**：
- 每层只关注自己的职责
- 降低复杂度
- 易于理解和维护

**易于替换**：
```c
/* 可以轻松切换不同的驱动 */
Graphics_Init(&ctx, &ili9341_driver);  // 使用ILI9341
Graphics_Init(&ctx, &st7789_driver);   // 切换到ST7789
```

**便于测试**：
```c
/* 可以使用模拟驱动进行测试 */
Display_Driver_t mock_driver = {
    .init = mock_init,
    .set_pixel = mock_set_pixel,
    // ...
};
```



## 状态管理

### 状态机模式

使用状态机管理复杂的界面状态：

```
        ┌─────────┐
        │  Idle   │
        └────┬────┘
             │ start
             ↓
        ┌─────────┐
        │ Running │
        └────┬────┘
             │ pause
             ↓
        ┌─────────┐
        │ Paused  │
        └────┬────┘
             │ resume
             ↑
             │ stop
        ┌─────────┐
        │ Stopped │
        └─────────┘
```

**状态机实现**：

```c
/* state_machine.h */
#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <stdint.h>

/* 状态定义 */
typedef enum {
    STATE_IDLE,
    STATE_RUNNING,
    STATE_PAUSED,
    STATE_STOPPED,
    STATE_MAX
} App_State_t;

/* 事件定义 */
typedef enum {
    EVENT_START,
    EVENT_PAUSE,
    EVENT_RESUME,
    EVENT_STOP,
    EVENT_MAX
} State_Event_t;

/* 状态机接口 */
void StateMachine_Init(void);
void StateMachine_HandleEvent(State_Event_t event);
App_State_t StateMachine_GetCurrentState(void);

#endif
```

```c
/* state_machine.c */
#include "state_machine.h"
#include <stdio.h>

/* 当前状态 */
static App_State_t current_state = STATE_IDLE;

/* 状态进入回调 */
typedef void (*State_Enter_Callback_t)(void);

/* 状态退出回调 */
typedef void (*State_Exit_Callback_t)(void);

/* 状态转换表 */
typedef struct {
    App_State_t from_state;
    State_Event_t event;
    App_State_t to_state;
    State_Exit_Callback_t on_exit;
    State_Enter_Callback_t on_enter;
} State_Transition_t;

/* 状态回调函数 */
static void on_enter_idle(void) {
    printf("Enter IDLE state\n");
    update_ui_for_idle();
}

static void on_exit_idle(void) {
    printf("Exit IDLE state\n");
}

static void on_enter_running(void) {
    printf("Enter RUNNING state\n");
    start_timer();
    update_ui_for_running();
}

static void on_exit_running(void) {
    printf("Exit RUNNING state\n");
}

static void on_enter_paused(void) {
    printf("Enter PAUSED state\n");
    pause_timer();
    update_ui_for_paused();
}

static void on_exit_paused(void) {
    printf("Exit PAUSED state\n");
}

static void on_enter_stopped(void) {
    printf("Enter STOPPED state\n");
    stop_timer();
    update_ui_for_stopped();
}

/* 状态转换表 */
static const State_Transition_t transitions[] = {
    /* 从IDLE状态 */
    {STATE_IDLE, EVENT_START, STATE_RUNNING, on_exit_idle, on_enter_running},
    
    /* 从RUNNING状态 */
    {STATE_RUNNING, EVENT_PAUSE, STATE_PAUSED, on_exit_running, on_enter_paused},
    {STATE_RUNNING, EVENT_STOP, STATE_STOPPED, on_exit_running, on_enter_stopped},
    
    /* 从PAUSED状态 */
    {STATE_PAUSED, EVENT_RESUME, STATE_RUNNING, on_exit_paused, on_enter_running},
    {STATE_PAUSED, EVENT_STOP, STATE_STOPPED, on_exit_paused, on_enter_stopped},
    
    /* 从STOPPED状态 */
    {STATE_STOPPED, EVENT_START, STATE_IDLE, NULL, on_enter_idle},
};

#define TRANSITION_COUNT (sizeof(transitions) / sizeof(State_Transition_t))

/**
 * @brief  初始化状态机
 */
void StateMachine_Init(void)
{
    current_state = STATE_IDLE;
    on_enter_idle();
}

/**
 * @brief  处理状态事件
 * @param  event: 事件
 */
void StateMachine_HandleEvent(State_Event_t event)
{
    /* 查找匹配的转换 */
    for (uint8_t i = 0; i < TRANSITION_COUNT; i++) {
        const State_Transition_t* trans = &transitions[i];
        
        if (trans->from_state == current_state && trans->event == event) {
            /* 执行退出回调 */
            if (trans->on_exit != NULL) {
                trans->on_exit();
            }
            
            /* 切换状态 */
            current_state = trans->to_state;
            
            /* 执行进入回调 */
            if (trans->on_enter != NULL) {
                trans->on_enter();
            }
            
            return;
        }
    }
    
    /* 无效的状态转换 */
    printf("Invalid transition: state=%d, event=%d\n", current_state, event);
}

/**
 * @brief  获取当前状态
 */
App_State_t StateMachine_GetCurrentState(void)
{
    return current_state;
}
```

**使用状态机**：

```c
/* 按钮事件处理 */
void on_start_button_clicked(void)
{
    StateMachine_HandleEvent(EVENT_START);
}

void on_pause_button_clicked(void)
{
    StateMachine_HandleEvent(EVENT_PAUSE);
}

void on_resume_button_clicked(void)
{
    StateMachine_HandleEvent(EVENT_RESUME);
}

void on_stop_button_clicked(void)
{
    StateMachine_HandleEvent(EVENT_STOP);
}

/* 根据状态更新UI */
void update_ui_for_state(void)
{
    App_State_t state = StateMachine_GetCurrentState();
    
    switch (state) {
        case STATE_IDLE:
            Button_SetEnabled(start_btn, true);
            Button_SetEnabled(pause_btn, false);
            Button_SetEnabled(stop_btn, false);
            Label_SetText(status_label, "Ready");
            break;
            
        case STATE_RUNNING:
            Button_SetEnabled(start_btn, false);
            Button_SetEnabled(pause_btn, true);
            Button_SetEnabled(stop_btn, true);
            Label_SetText(status_label, "Running");
            break;
            
        case STATE_PAUSED:
            Button_SetEnabled(start_btn, false);
            Button_SetEnabled(pause_btn, false);
            Button_SetEnabled(resume_btn, true);
            Button_SetEnabled(stop_btn, true);
            Label_SetText(status_label, "Paused");
            break;
            
        case STATE_STOPPED:
            Button_SetEnabled(start_btn, true);
            Button_SetEnabled(pause_btn, false);
            Button_SetEnabled(stop_btn, false);
            Label_SetText(status_label, "Stopped");
            break;
    }
}
```

### 状态管理的优势

**清晰的状态转换**：
- 所有可能的状态和转换一目了然
- 避免非法的状态转换
- 易于调试和测试

**集中管理**：
- 状态逻辑集中在一处
- 避免状态散落在各处
- 便于维护和修改

**可扩展性**：
```c
/* 添加新状态很简单 */
typedef enum {
    STATE_IDLE,
    STATE_RUNNING,
    STATE_PAUSED,
    STATE_STOPPED,
    STATE_ERROR,      // 新增错误状态
    STATE_MAX
} App_State_t;

/* 添加新的转换 */
{STATE_RUNNING, EVENT_ERROR, STATE_ERROR, on_exit_running, on_enter_error},
```



## 架构选择指南

### 不同场景的架构选择

#### 1. 简单应用 (单屏幕，少量控件)

**推荐架构**：简化的MVC或直接编程

```c
/* 简单的温度显示应用 */
void simple_app_init(void)
{
    /* 直接创建UI */
    lv_obj_t* label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "25.0°C");
    lv_obj_center(label);
}

void simple_app_update(float temp)
{
    /* 直接更新 */
    lv_label_set_text_fmt(label, "%.1f°C", temp);
}
```

**特点**：
- 代码简单直接
- 开发速度快
- 适合原型开发

#### 2. 中等复杂度应用 (多屏幕，中等交互)

**推荐架构**：MVC + 事件驱动

```c
/* 使用MVC组织代码 */
typedef struct {
    Screen_t* home_screen;
    Screen_t* settings_screen;
    Screen_t* current_screen;
} App_Context_t;

void app_init(App_Context_t* ctx)
{
    /* 初始化事件系统 */
    Event_System_Init();
    
    /* 创建屏幕 */
    ctx->home_screen = create_home_screen();
    ctx->settings_screen = create_settings_screen();
    ctx->current_screen = ctx->home_screen;
    
    /* 订阅事件 */
    Event_Subscribe(EVENT_SWITCH_SCREEN, on_switch_screen);
}
```

**特点**：
- 结构清晰
- 易于维护
- 支持多屏幕切换

#### 3. 复杂应用 (多屏幕，复杂交互，状态管理)

**推荐架构**：MVC + 事件驱动 + 状态机 + 分层设计

```c
/* 完整的架构 */
typedef struct {
    /* 状态管理 */
    StateMachine_t* state_machine;
    
    /* 事件系统 */
    EventSystem_t* event_system;
    
    /* 屏幕管理 */
    ScreenManager_t* screen_manager;
    
    /* 数据模型 */
    DataModel_t* data_model;
    
    /* 服务层 */
    ServiceLayer_t* services;
} Application_t;

void application_init(Application_t* app)
{
    /* 初始化各个子系统 */
    app->state_machine = StateMachine_Create();
    app->event_system = EventSystem_Create();
    app->screen_manager = ScreenManager_Create();
    app->data_model = DataModel_Create();
    app->services = ServiceLayer_Create();
    
    /* 连接各个组件 */
    connect_components(app);
}
```

**特点**：
- 高度模块化
- 易于团队协作
- 支持复杂业务逻辑
- 便于测试和维护

### 架构对比

| 特性 | 简单架构 | MVC | MVC+事件驱动 | 完整架构 |
|------|---------|-----|-------------|---------|
| 代码复杂度 | 低 | 中 | 中高 | 高 |
| 开发速度 | 快 | 中 | 中 | 慢 |
| 可维护性 | 低 | 中 | 高 | 很高 |
| 可扩展性 | 低 | 中 | 高 | 很高 |
| 适用规模 | 小 | 中 | 中大 | 大 |
| 学习曲线 | 平缓 | 中等 | 陡峭 | 很陡 |

### 选择建议

**选择简单架构，如果**：
- 项目规模小（<1000行代码）
- 功能简单，交互少
- 开发时间紧张
- 团队规模小（1-2人）

**选择MVC架构，如果**：
- 项目规模中等（1000-5000行）
- 需要清晰的代码组织
- 有一定的维护需求
- 团队规模中等（2-5人）

**选择MVC+事件驱动，如果**：
- 项目规模较大（5000-10000行）
- 组件间交互复杂
- 需要高度解耦
- 团队规模较大（5-10人）

**选择完整架构，如果**：
- 项目规模大（>10000行）
- 业务逻辑复杂
- 需要长期维护
- 团队规模大（>10人）

## 最佳实践

### 1. 保持简单

**原则**：不要过度设计

```c
// ❌ 过度设计
typedef struct {
    AbstractFactory* factory;
    Singleton* singleton;
    Observer* observer;
    Strategy* strategy;
} OverEngineered_t;

// ✅ 简单实用
typedef struct {
    Screen_t* screen;
    Model_t* model;
} Simple_t;
```

### 2. 渐进式架构

从简单开始，根据需要逐步演进：

```
第一版：直接编程
    ↓
第二版：添加MVC分层
    ↓
第三版：引入事件系统
    ↓
第四版：添加状态管理
```

### 3. 接口优于实现

使用接口隔离具体实现：

```c
/* 定义接口 */
typedef struct {
    void (*init)(void);
    void (*update)(void* data);
    void (*destroy)(void);
} Component_Interface_t;

/* 具体实现可以随时替换 */
Component_Interface_t* component = get_lcd_component();
component = get_oled_component();  // 切换实现
```

### 4. 单元测试

为关键组件编写单元测试：

```c
/* 测试Model */
void test_temperature_model(void)
{
    Temperature_Model_Init();
    
    /* 测试设置温度 */
    Temperature_Model_SetTemperature(35.0f);
    assert(Temperature_Model_GetCurrent() == 35.0f);
    
    /* 测试报警 */
    Temperature_Model_SetThreshold(30.0f);
    assert(Temperature_Model_IsAlarmActive() == true);
}

/* 测试状态机 */
void test_state_machine(void)
{
    StateMachine_Init();
    assert(StateMachine_GetCurrentState() == STATE_IDLE);
    
    StateMachine_HandleEvent(EVENT_START);
    assert(StateMachine_GetCurrentState() == STATE_RUNNING);
}
```

### 5. 文档和注释

为架构和关键组件编写文档：

```c
/**
 * @brief  温度监控系统架构
 * 
 * 系统采用MVC架构：
 * - Model: Temperature_Model - 管理温度数据
 * - View: Temperature_View - 显示界面
 * - Controller: Temperature_Controller - 协调Model和View
 * 
 * 数据流：
 * 传感器 → Controller → Model → Observer → View
 * 
 * 事件流：
 * 用户输入 → View → Controller → Model
 */
```

### 6. 代码审查

定期进行代码审查，检查：
- 架构是否合理
- 职责是否清晰
- 耦合度是否过高
- 是否有重复代码
- 是否符合编码规范

## 总结

### 核心要点

1. **MVC模式**
   - 分离Model、View、Controller
   - 降低耦合，提高可维护性
   - 适合中等复杂度的应用

2. **事件驱动架构**
   - 通过事件解耦组件
   - 支持异步处理
   - 易于扩展和修改

3. **界面分层设计**
   - 驱动层、图形层、控件层、表示层、应用层
   - 每层职责清晰
   - 易于替换和测试

4. **状态管理**
   - 使用状态机管理复杂状态
   - 清晰的状态转换
   - 避免非法状态

### 架构选择原则

- 根据项目规模选择合适的架构
- 从简单开始，逐步演进
- 不要过度设计
- 保持代码简洁清晰

### 实践建议

- 使用接口隔离实现
- 编写单元测试
- 保持文档更新
- 定期代码审查
- 持续重构优化

## 延伸阅读

### 推荐资源

1. **设计模式**
   - 《设计模式：可复用面向对象软件的基础》
   - 《Head First设计模式》

2. **GUI架构**
   - LVGL官方文档
   - Qt架构设计
   - Android UI架构

3. **嵌入式软件架构**
   - 《嵌入式软件设计与实现》
   - 《嵌入式系统架构》

### 相关文章

- [LVGL图形库快速入门](../beginner/01-lvgl-quickstart.html)
- [图形性能优化技术](02-graphics-optimization.html)
- [智能家居控制面板项目](../advanced/01-smart-home-panel.html)

### 开源项目参考

- **LVGL**: https://github.com/lvgl/lvgl
- **TouchGFX**: https://www.st.com/en/development-tools/touchgfxdesigner.html
- **emWin**: https://www.segger.com/products/user-interface/emwin/

---

**反馈与支持**：

如果你在学习过程中遇到问题，欢迎通过以下方式获取帮助：

- 💬 在评论区留言
- 📧 发送邮件至 support@embedded-platform.com
- 🐛 在GitHub提交Issue
- 💡 在论坛发起讨论

---

**版权声明**：本文采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**最后更新**: 2024-01-15  
**文章版本**: 1.0  
**作者**: 嵌入式知识平台

