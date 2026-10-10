---
title: "状态机设计与应用：构建可靠的嵌入式系统控制逻辑"
description: "深入学习状态机设计模式，掌握状态转换、事件处理和代码实现技术，通过实战案例构建智能LED控制系统"
slug: "state-machine-design"

# 分类信息
domain: "应用层"
module: "应用框架"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 状态机
  - 设计模式
  - 状态管理
  - 事件驱动
  - 控制逻辑
prerequisites:
  - "10-cross-cutting-concerns/01-programming-languages/beginner/01-c-basics"
  - "02-driver-bsp-layer/02-device-driver-development/beginner/01-gpio-basics"
related_contents:
  - "05-application-layer/03-application-frameworks/beginner/01-software-architecture"
  - "05-application-layer/03-application-frameworks/intermediate/01-cli-framework"

# 学习信息
estimated_time: 75
difficulty_score: 2

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
  - 状态机设计
  - 有限状态机
  - FSM
  - 嵌入式状态机
  - 事件驱动编程
cover_image: ""
---

# 状态机设计与应用：构建可靠的嵌入式系统控制逻辑


## 学习目标

完成本教程后，你将能够：

- [ ] 理解状态机的基本概念和工作原理
- [ ] 掌握有限状态机（FSM）的设计方法
- [ ] 学会使用状态图描述系统行为
- [ ] 实现基于表驱动和嵌套switch的状态机
- [ ] 掌握状态转换和事件处理技术
- [ ] 理解状态机在嵌入式系统中的应用场景
- [ ] 能够设计和实现一个完整的状态机系统
- [ ] 掌握状态机的调试和测试方法

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言基础（结构体、指针、函数指针）
- 了解基本的GPIO操作
- 理解事件驱动编程概念
- 掌握基本的软件设计思想

**技能要求**：
- 能够使用开发环境编写和调试代码
- 会使用基本的调试工具
- 了解如何绘制流程图

**开发环境**：
- 任何支持C语言的嵌入式开发板
- 开发IDE（Arduino IDE、STM32CubeIDE等）
- LED灯和按键（用于演示）


## 状态机概述

### 什么是状态机

状态机（State Machine）是一种数学模型，用于描述系统在不同状态之间的转换行为。在嵌入式系统中，状态机是一种强大的设计模式，能够清晰地表达复杂的控制逻辑。

**核心概念**：

1. **状态（State）**
   - 系统在某一时刻的工作模式
   - 每个状态代表一种特定的行为
   - 系统在任意时刻只能处于一个状态

2. **事件（Event）**
   - 触发状态转换的条件
   - 可以是外部输入、定时器超时、内部条件等
   - 事件驱动状态机的运行

3. **转换（Transition）**
   - 从一个状态切换到另一个状态
   - 由特定事件触发
   - 可以伴随动作（Action）的执行

4. **动作（Action）**
   - 状态转换时执行的操作
   - 可以是进入动作、退出动作或转换动作


### 状态机的类型

**1. 有限状态机（FSM - Finite State Machine）**

最基本的状态机类型，具有有限数量的状态。

```
特点：
- 状态数量有限且确定
- 转换规则明确
- 易于实现和理解
- 适合大多数嵌入式应用
```

**2. 分层状态机（HSM - Hierarchical State Machine）**

支持状态嵌套的高级状态机。

```
特点：
- 状态可以包含子状态
- 支持状态继承
- 减少状态转换的复杂度
- 适合复杂系统
```

**3. 并发状态机（Concurrent State Machine）**

多个状态机并行运行。

```
特点：
- 多个独立的状态机
- 可以相互通信
- 适合多任务系统
```

本教程主要关注有限状态机（FSM），它是最常用且最实用的类型。


### 状态机的优势

**为什么要使用状态机？**

1. **清晰的逻辑结构**
   - 系统行为一目了然
   - 易于理解和维护
   - 减少代码复杂度

2. **可靠性高**
   - 明确的状态转换规则
   - 避免意外的状态组合
   - 易于测试和验证

3. **易于扩展**
   - 添加新状态不影响现有逻辑
   - 修改转换规则简单
   - 支持模块化设计

4. **便于调试**
   - 状态可视化
   - 转换过程可追踪
   - 问题定位快速

5. **代码复用**
   - 状态机框架可重用
   - 设计模式标准化
   - 降低开发成本


### 状态机的应用场景

状态机在嵌入式系统中有广泛的应用：

| 应用领域 | 典型场景 | 状态示例 |
|---------|---------|---------|
| 通信协议 | UART、SPI、I2C | 空闲、发送、接收、错误 |
| 用户界面 | 菜单系统、按键处理 | 主菜单、子菜单、设置、确认 |
| 电源管理 | 低功耗控制 | 运行、睡眠、深度睡眠、关机 |
| 设备控制 | 电机、LED、传感器 | 停止、启动、运行、故障 |
| 任务调度 | 系统初始化、运行 | 初始化、就绪、运行、挂起 |


## 状态图设计

### 状态图符号

使用UML状态图来描述状态机：

```
┌─────────────────────────────────────────┐
│  状态图基本符号                          │
├─────────────────────────────────────────┤
│                                         │
│  ●  初始状态（黑色实心圆）               │
│                                         │
│  ┌──────────┐                          │
│  │  状态名   │  状态（圆角矩形）          │
│  └──────────┘                          │
│                                         │
│  ────────>  转换（带箭头的线）           │
│                                         │
│  事件[条件]/动作  转换标签               │
│                                         │
│  ◎  终止状态（带圈的黑点）               │
│                                         │
└─────────────────────────────────────────┘
```

### 简单示例：LED控制

让我们从一个简单的LED控制系统开始：

**需求**：
- 按键按下：LED切换状态
- 两种状态：开（ON）和关（OFF）

**状态图**：

```
        ┌─────────────────────────────┐
        │                             │
        ●  初始状态                    │
        │                             │
        ↓                             │
   ┌─────────┐   按键按下        ┌─────────┐
   │   OFF   │ ──────────────>  │   ON    │
   │ LED熄灭  │                  │ LED点亮  │
   └─────────┘  <──────────────  └─────────┘
                    按键按下
```

**状态转换表**：

| 当前状态 | 事件 | 下一状态 | 动作 |
|---------|------|---------|------|
| OFF | 按键按下 | ON | 点亮LED |
| ON | 按键按下 | OFF | 熄灭LED |


### 复杂示例：智能LED系统

**需求**：
- 支持多种工作模式：关闭、常亮、闪烁、呼吸
- 按键短按：切换模式
- 按键长按：进入设置模式
- 设置模式下可调整参数

**状态图**：

```
                    ●  初始状态
                    │
                    ↓
              ┌──────────┐
              │   OFF    │ ◄────────────┐
              │  LED关闭  │              │
              └──────────┘              │
                    │                   │
              短按  │                   │ 长按3秒
                    ↓                   │
              ┌──────────┐              │
              │   ON     │              │
              │  LED常亮  │              │
              └──────────┘              │
                    │                   │
              短按  │                   │
                    ↓                   │
              ┌──────────┐              │
              │  BLINK   │              │
              │  LED闪烁  │              │
              └──────────┘              │
                    │                   │
              短按  │                   │
                    ↓                   │
              ┌──────────┐              │
              │ BREATHE  │              │
              │  LED呼吸  │              │
              └──────────┘              │
                    │                   │
              短按  │                   │
                    └───────────────────┘
                    
              长按  │
                    ↓
              ┌──────────┐
              │  SETUP   │
              │  设置模式 │
              └──────────┘
                    │
              短按  │
                    ↓
              返回之前状态
```


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | 任意MCU开发板 | Arduino Uno, ESP32, STM32 |
| LED灯 | 3 | 红、绿、蓝各一个 | 5mm LED |
| 电阻 | 3 | 220Ω限流电阻 | 1/4W |
| 按键 | 2 | 轻触开关 | 6x6mm |
| 面包板 | 1 | 用于搭建电路 | - |
| 杜邦线 | 若干 | 连接线 | - |

### 软件准备

**开发环境**：
- Arduino IDE 2.0+ 或
- PlatformIO 或
- STM32CubeIDE

**必需的库**：
- 无需额外库（使用标准C语言）

### 电路连接

**连接图**：

```
Arduino/MCU          LED电路
┌─────────┐
│         │
│  Pin 9  ├──────┬─── 220Ω ───┬─── LED红 ───┬─── GND
│         │      │             │             │
│  Pin 10 ├──────┼─── 220Ω ───┼─── LED绿 ───┤
│         │      │             │             │
│  Pin 11 ├──────┴─── 220Ω ───┴─── LED蓝 ───┘
│         │
│  Pin 2  ├────── 按键1 ────── GND
│         │      (模式切换)
│  Pin 3  ├────── 按键2 ────── GND
│         │      (设置)
│   GND   ├──────────────────── GND
│         │
└─────────┘
```

**连接说明**：

| 开发板引脚 | 连接到 | 说明 |
|-----------|--------|------|
| Pin 9 | LED红正极 | 通过220Ω电阻 |
| Pin 10 | LED绿正极 | 通过220Ω电阻 |
| Pin 11 | LED蓝正极 | 通过220Ω电阻 |
| Pin 2 | 按键1 | 使用内部上拉 |
| Pin 3 | 按键2 | 使用内部上拉 |
| GND | LED负极、按键 | 共地 |

⚠️ **注意事项**：
- 确保LED极性正确（长脚为正极）
- 电阻不要遗漏，否则可能烧坏LED
- 按键使用内部上拉电阻，按下时为低电平


## 步骤1：实现简单的双状态机

### 1.1 定义状态和事件

首先实现最简单的LED开关状态机：

```c
// simple_state_machine.ino

// 定义LED引脚
#define LED_PIN 9
#define BUTTON_PIN 2

// 定义状态枚举
typedef enum {
    STATE_OFF,    // LED关闭状态
    STATE_ON      // LED开启状态
} LedState_t;

// 定义事件枚举
typedef enum {
    EVENT_NONE,        // 无事件
    EVENT_BUTTON_PRESS // 按键按下事件
} Event_t;

// 全局变量
LedState_t current_state = STATE_OFF;  // 当前状态
Event_t current_event = EVENT_NONE;     // 当前事件

// 按键去抖动变量
unsigned long last_button_time = 0;
const unsigned long DEBOUNCE_DELAY = 50;  // 50ms去抖动
```

**代码说明**：
- 使用枚举定义状态和事件，提高代码可读性
- `current_state`保存当前状态
- `current_event`保存待处理的事件
- 添加去抖动机制避免误触发


### 1.2 实现状态机逻辑

使用switch-case实现状态转换：

```c
// 状态机处理函数
void state_machine_run(Event_t event) {
    // 根据当前状态和事件进行处理
    switch (current_state) {
        case STATE_OFF:
            // 在OFF状态下的处理
            if (event == EVENT_BUTTON_PRESS) {
                // 转换到ON状态
                Serial.println("State: OFF -> ON");
                digitalWrite(LED_PIN, HIGH);  // 点亮LED
                current_state = STATE_ON;     // 更新状态
            }
            break;
            
        case STATE_ON:
            // 在ON状态下的处理
            if (event == EVENT_BUTTON_PRESS) {
                // 转换到OFF状态
                Serial.println("State: ON -> OFF");
                digitalWrite(LED_PIN, LOW);   // 熄灭LED
                current_state = STATE_OFF;    // 更新状态
            }
            break;
            
        default:
            // 未知状态，重置到OFF
            Serial.println("Error: Unknown state, reset to OFF");
            current_state = STATE_OFF;
            digitalWrite(LED_PIN, LOW);
            break;
    }
}

// 事件检测函数
Event_t detect_event() {
    // 读取按键状态（低电平表示按下）
    if (digitalRead(BUTTON_PIN) == LOW) {
        // 去抖动处理
        unsigned long current_time = millis();
        if (current_time - last_button_time > DEBOUNCE_DELAY) {
            last_button_time = current_time;
            
            // 等待按键释放
            while (digitalRead(BUTTON_PIN) == LOW) {
                delay(10);
            }
            
            return EVENT_BUTTON_PRESS;
        }
    }
    
    return EVENT_NONE;
}
```

**代码说明**：
- `state_machine_run()`：状态机核心函数，处理状态转换
- `detect_event()`：事件检测函数，识别按键按下
- 使用switch-case结构清晰地表达状态转换逻辑
- 包含去抖动和按键释放检测

### 1.3 主程序框架

```c
void setup() {
    // 初始化串口
    Serial.begin(115200);
    Serial.println("Simple State Machine Demo");
    Serial.println("=========================");
    
    // 配置引脚
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);  // 使用内部上拉
    
    // 初始化LED状态
    digitalWrite(LED_PIN, LOW);
    
    // 打印初始状态
    Serial.println("Initial State: OFF");
    Serial.println("Press button to toggle LED\n");
}

void loop() {
    // 1. 检测事件
    Event_t event = detect_event();
    
    // 2. 如果有事件，运行状态机
    if (event != EVENT_NONE) {
        state_machine_run(event);
    }
    
    // 3. 其他任务...
    delay(10);  // 小延时，降低CPU占用
}
```

**预期运行结果**：

```
Simple State Machine Demo
=========================
Initial State: OFF
Press button to toggle LED

State: OFF -> ON
State: ON -> OFF
State: OFF -> ON
State: ON -> OFF
```


## 步骤2：实现多状态LED控制系统

### 2.1 扩展状态定义

现在实现一个更复杂的系统，支持多种LED模式：

```c
// multi_state_machine.ino

// LED引脚定义
#define LED_RED_PIN   9
#define LED_GREEN_PIN 10
#define LED_BLUE_PIN  11
#define BUTTON_PIN    2

// 状态定义
typedef enum {
    STATE_OFF,      // 关闭
    STATE_RED,      // 红色常亮
    STATE_GREEN,    // 绿色常亮
    STATE_BLUE,     // 蓝色常亮
    STATE_BLINK,    // 闪烁模式
    STATE_RAINBOW   // 彩虹模式
} SystemState_t;

// 事件定义
typedef enum {
    EVENT_NONE,
    EVENT_BUTTON_SHORT,  // 短按
    EVENT_BUTTON_LONG,   // 长按
    EVENT_TIMEOUT        // 超时事件
} SystemEvent_t;

// 全局变量
SystemState_t current_state = STATE_OFF;
unsigned long state_enter_time = 0;  // 进入当前状态的时间
unsigned long last_blink_time = 0;   // 上次闪烁切换时间
bool blink_state = false;            // 闪烁状态

// 按键检测变量
unsigned long button_press_time = 0;
bool button_pressed = false;
const unsigned long LONG_PRESS_TIME = 1000;  // 长按时间阈值（1秒）
```


### 2.2 实现状态动作函数

为每个状态定义进入和退出动作：

```c
// LED控制辅助函数
void set_led_color(uint8_t red, uint8_t green, uint8_t blue) {
    analogWrite(LED_RED_PIN, red);
    analogWrite(LED_GREEN_PIN, green);
    analogWrite(LED_BLUE_PIN, blue);
}

void turn_off_all_leds() {
    set_led_color(0, 0, 0);
}

// 状态进入动作
void state_enter_action(SystemState_t state) {
    state_enter_time = millis();  // 记录进入时间
    
    switch (state) {
        case STATE_OFF:
            Serial.println("Enter: OFF");
            turn_off_all_leds();
            break;
            
        case STATE_RED:
            Serial.println("Enter: RED");
            set_led_color(255, 0, 0);
            break;
            
        case STATE_GREEN:
            Serial.println("Enter: GREEN");
            set_led_color(0, 255, 0);
            break;
            
        case STATE_BLUE:
            Serial.println("Enter: BLUE");
            set_led_color(0, 0, 255);
            break;
            
        case STATE_BLINK:
            Serial.println("Enter: BLINK");
            last_blink_time = millis();
            blink_state = false;
            turn_off_all_leds();
            break;
            
        case STATE_RAINBOW:
            Serial.println("Enter: RAINBOW");
            break;
    }
}

// 状态退出动作
void state_exit_action(SystemState_t state) {
    // 可以在这里添加退出时的清理工作
    Serial.print("Exit: ");
    Serial.println(state);
}

// 状态执行动作（在状态内持续执行）
void state_do_action(SystemState_t state) {
    switch (state) {
        case STATE_BLINK:
            // 闪烁逻辑：每500ms切换一次
            if (millis() - last_blink_time >= 500) {
                last_blink_time = millis();
                blink_state = !blink_state;
                
                if (blink_state) {
                    set_led_color(255, 255, 255);  // 白色
                } else {
                    turn_off_all_leds();
                }
            }
            break;
            
        case STATE_RAINBOW:
            // 彩虹效果：循环显示不同颜色
            {
                unsigned long elapsed = millis() - state_enter_time;
                uint8_t phase = (elapsed / 100) % 6;  // 每100ms切换颜色
                
                switch (phase) {
                    case 0: set_led_color(255, 0, 0); break;    // 红
                    case 1: set_led_color(255, 255, 0); break;  // 黄
                    case 2: set_led_color(0, 255, 0); break;    // 绿
                    case 3: set_led_color(0, 255, 255); break;  // 青
                    case 4: set_led_color(0, 0, 255); break;    // 蓝
                    case 5: set_led_color(255, 0, 255); break;  // 紫
                }
            }
            break;
            
        default:
            // 其他状态不需要持续动作
            break;
    }
}
```

**代码说明**：
- `state_enter_action()`：状态进入时执行一次
- `state_exit_action()`：状态退出时执行一次
- `state_do_action()`：在状态内持续执行
- 分离动作函数使代码更清晰、易维护

### 2.3 实现状态转换逻辑

```c
// 状态转换函数
void state_transition(SystemState_t new_state) {
    if (new_state != current_state) {
        // 执行退出动作
        state_exit_action(current_state);
        
        // 更新状态
        SystemState_t old_state = current_state;
        current_state = new_state;
        
        // 执行进入动作
        state_enter_action(current_state);
        
        // 打印状态转换信息
        Serial.print("Transition: ");
        Serial.print(old_state);
        Serial.print(" -> ");
        Serial.println(new_state);
    }
}

// 状态机主函数
void state_machine_run(SystemEvent_t event) {
    // 首先执行当前状态的持续动作
    state_do_action(current_state);
    
    // 然后根据事件处理状态转换
    switch (current_state) {
        case STATE_OFF:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_RED);
            }
            break;
            
        case STATE_RED:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_GREEN);
            } else if (event == EVENT_BUTTON_LONG) {
                state_transition(STATE_OFF);
            }
            break;
            
        case STATE_GREEN:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_BLUE);
            } else if (event == EVENT_BUTTON_LONG) {
                state_transition(STATE_OFF);
            }
            break;
            
        case STATE_BLUE:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_BLINK);
            } else if (event == EVENT_BUTTON_LONG) {
                state_transition(STATE_OFF);
            }
            break;
            
        case STATE_BLINK:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_RAINBOW);
            } else if (event == EVENT_BUTTON_LONG) {
                state_transition(STATE_OFF);
            }
            break;
            
        case STATE_RAINBOW:
            if (event == EVENT_BUTTON_SHORT) {
                state_transition(STATE_OFF);
            } else if (event == EVENT_BUTTON_LONG) {
                state_transition(STATE_OFF);
            }
            break;
            
        default:
            // 未知状态，重置
            state_transition(STATE_OFF);
            break;
    }
}
```

**状态转换规则**：
- 短按：循环切换模式（OFF → RED → GREEN → BLUE → BLINK → RAINBOW → OFF）
- 长按：任何状态都返回OFF


### 2.4 实现事件检测

```c
// 事件检测函数
SystemEvent_t detect_event() {
    static bool last_button_state = HIGH;
    bool current_button_state = digitalRead(BUTTON_PIN);
    
    // 检测按键按下（下降沿）
    if (last_button_state == HIGH && current_button_state == LOW) {
        button_pressed = true;
        button_press_time = millis();
    }
    
    // 检测按键释放（上升沿）
    if (last_button_state == LOW && current_button_state == HIGH) {
        if (button_pressed) {
            button_pressed = false;
            unsigned long press_duration = millis() - button_press_time;
            
            // 判断短按还是长按
            if (press_duration >= LONG_PRESS_TIME) {
                Serial.println("Event: LONG PRESS");
                last_button_state = current_button_state;
                return EVENT_BUTTON_LONG;
            } else {
                Serial.println("Event: SHORT PRESS");
                last_button_state = current_button_state;
                return EVENT_BUTTON_SHORT;
            }
        }
    }
    
    last_button_state = current_button_state;
    return EVENT_NONE;
}

// 主程序
void setup() {
    Serial.begin(115200);
    Serial.println("Multi-State LED Controller");
    Serial.println("==========================");
    Serial.println("Short press: Next mode");
    Serial.println("Long press: Turn off\n");
    
    // 配置引脚
    pinMode(LED_RED_PIN, OUTPUT);
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(LED_BLUE_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    // 初始化状态
    state_enter_action(STATE_OFF);
}

void loop() {
    // 检测事件
    SystemEvent_t event = detect_event();
    
    // 运行状态机
    state_machine_run(event);
    
    // 小延时
    delay(10);
}
```

**预期运行结果**：

```
Multi-State LED Controller
==========================
Short press: Next mode
Long press: Turn off

Enter: OFF
Event: SHORT PRESS
Exit: 0
Enter: RED
Transition: 0 -> 1

Event: SHORT PRESS
Exit: 1
Enter: GREEN
Transition: 1 -> 2

Event: LONG PRESS
Exit: 2
Enter: OFF
Transition: 2 -> 0
```


## 步骤3：使用表驱动方法

### 3.1 状态转换表设计

表驱动方法将状态转换规则存储在数据结构中，使代码更加灵活：

```c
// table_driven_fsm.ino

// 状态和事件定义（同前）
typedef enum {
    STATE_OFF,
    STATE_RED,
    STATE_GREEN,
    STATE_BLUE,
    STATE_BLINK,
    STATE_RAINBOW,
    STATE_MAX  // 状态总数
} State_t;

typedef enum {
    EVENT_NONE,
    EVENT_SHORT_PRESS,
    EVENT_LONG_PRESS,
    EVENT_MAX  // 事件总数
} Event_t;

// 动作函数指针类型
typedef void (*ActionFunc_t)(void);

// 状态转换表项
typedef struct {
    State_t current_state;   // 当前状态
    Event_t event;           // 触发事件
    State_t next_state;      // 下一状态
    ActionFunc_t action;     // 转换时执行的动作
} StateTransition_t;

// 动作函数声明
void action_turn_on_red(void);
void action_turn_on_green(void);
void action_turn_on_blue(void);
void action_start_blink(void);
void action_start_rainbow(void);
void action_turn_off(void);

// 状态转换表
const StateTransition_t state_table[] = {
    // 当前状态      事件              下一状态        动作函数
    {STATE_OFF,      EVENT_SHORT_PRESS, STATE_RED,      action_turn_on_red},
    {STATE_RED,      EVENT_SHORT_PRESS, STATE_GREEN,    action_turn_on_green},
    {STATE_RED,      EVENT_LONG_PRESS,  STATE_OFF,      action_turn_off},
    {STATE_GREEN,    EVENT_SHORT_PRESS, STATE_BLUE,     action_turn_on_blue},
    {STATE_GREEN,    EVENT_LONG_PRESS,  STATE_OFF,      action_turn_off},
    {STATE_BLUE,     EVENT_SHORT_PRESS, STATE_BLINK,    action_start_blink},
    {STATE_BLUE,     EVENT_LONG_PRESS,  STATE_OFF,      action_turn_off},
    {STATE_BLINK,    EVENT_SHORT_PRESS, STATE_RAINBOW,  action_start_rainbow},
    {STATE_BLINK,    EVENT_LONG_PRESS,  STATE_OFF,      action_turn_off},
    {STATE_RAINBOW,  EVENT_SHORT_PRESS, STATE_OFF,      action_turn_off},
    {STATE_RAINBOW,  EVENT_LONG_PRESS,  STATE_OFF,      action_turn_off},
};

const int state_table_size = sizeof(state_table) / sizeof(StateTransition_t);

// 当前状态
State_t current_state = STATE_OFF;
```

**表驱动方法的优势**：
- 状态转换规则一目了然
- 易于修改和扩展
- 可以从配置文件加载
- 便于自动化测试


### 3.2 实现动作函数

```c
// 动作函数实现
void action_turn_on_red(void) {
    Serial.println("Action: Turn on RED LED");
    set_led_color(255, 0, 0);
}

void action_turn_on_green(void) {
    Serial.println("Action: Turn on GREEN LED");
    set_led_color(0, 255, 0);
}

void action_turn_on_blue(void) {
    Serial.println("Action: Turn on BLUE LED");
    set_led_color(0, 0, 255);
}

void action_start_blink(void) {
    Serial.println("Action: Start BLINK mode");
    // 闪烁模式的初始化在state_do_action中处理
}

void action_start_rainbow(void) {
    Serial.println("Action: Start RAINBOW mode");
    // 彩虹模式的初始化在state_do_action中处理
}

void action_turn_off(void) {
    Serial.println("Action: Turn off all LEDs");
    turn_off_all_leds();
}
```

### 3.3 实现表驱动状态机

```c
// 表驱动状态机处理函数
void table_driven_fsm(Event_t event) {
    // 如果没有事件，只执行当前状态的持续动作
    if (event == EVENT_NONE) {
        state_do_action(current_state);
        return;
    }
    
    // 在状态转换表中查找匹配项
    for (int i = 0; i < state_table_size; i++) {
        if (state_table[i].current_state == current_state &&
            state_table[i].event == event) {
            
            // 找到匹配的转换
            State_t next_state = state_table[i].next_state;
            
            Serial.print("State transition: ");
            Serial.print(current_state);
            Serial.print(" -> ");
            Serial.println(next_state);
            
            // 执行转换动作
            if (state_table[i].action != NULL) {
                state_table[i].action();
            }
            
            // 更新状态
            current_state = next_state;
            
            return;  // 找到并处理了，退出
        }
    }
    
    // 如果没有找到匹配的转换，保持当前状态
    Serial.println("Warning: No transition found for current state and event");
}

// 主程序
void setup() {
    Serial.begin(115200);
    Serial.println("Table-Driven State Machine");
    Serial.println("==========================\n");
    
    // 配置引脚
    pinMode(LED_RED_PIN, OUTPUT);
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(LED_BLUE_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    // 初始化
    turn_off_all_leds();
    
    // 打印状态转换表
    Serial.println("State Transition Table:");
    Serial.println("Current | Event | Next | Action");
    Serial.println("--------|-------|------|-------");
    for (int i = 0; i < state_table_size; i++) {
        Serial.print(state_table[i].current_state);
        Serial.print("       | ");
        Serial.print(state_table[i].event);
        Serial.print("     | ");
        Serial.print(state_table[i].next_state);
        Serial.println();
    }
    Serial.println();
}

void loop() {
    // 检测事件
    Event_t event = detect_event();
    
    // 运行表驱动状态机
    table_driven_fsm(event);
    
    delay(10);
}
```

**表驱动方法的特点**：
- 数据和逻辑分离
- 易于维护和扩展
- 可以动态修改转换规则
- 适合复杂的状态机


## 步骤4：添加状态机调试功能

### 4.1 状态历史记录

```c
// 状态历史记录
#define HISTORY_SIZE 10

typedef struct {
    State_t state;
    Event_t event;
    unsigned long timestamp;
} StateHistory_t;

StateHistory_t state_history[HISTORY_SIZE];
int history_index = 0;

// 记录状态转换
void record_state_transition(State_t old_state, Event_t event, State_t new_state) {
    state_history[history_index].state = old_state;
    state_history[history_index].event = event;
    state_history[history_index].timestamp = millis();
    
    history_index = (history_index + 1) % HISTORY_SIZE;
}

// 打印状态历史
void print_state_history() {
    Serial.println("\n=== State History ===");
    Serial.println("Time(ms) | State | Event");
    Serial.println("---------|-------|------");
    
    for (int i = 0; i < HISTORY_SIZE; i++) {
        int idx = (history_index + i) % HISTORY_SIZE;
        if (state_history[idx].timestamp > 0) {
            Serial.print(state_history[idx].timestamp);
            Serial.print("    | ");
            Serial.print(state_history[idx].state);
            Serial.print("     | ");
            Serial.println(state_history[idx].event);
        }
    }
    Serial.println("====================\n");
}
```

### 4.2 状态机统计信息

```c
// 状态统计
typedef struct {
    unsigned long enter_count;    // 进入次数
    unsigned long total_time;     // 总停留时间
    unsigned long last_enter_time; // 最后进入时间
} StateStats_t;

StateStats_t state_stats[STATE_MAX];

// 更新统计信息
void update_state_stats(State_t state, bool entering) {
    if (entering) {
        state_stats[state].enter_count++;
        state_stats[state].last_enter_time = millis();
    } else {
        unsigned long duration = millis() - state_stats[state].last_enter_time;
        state_stats[state].total_time += duration;
    }
}

// 打印统计信息
void print_state_stats() {
    Serial.println("\n=== State Statistics ===");
    Serial.println("State | Enters | Total Time(ms) | Avg Time(ms)");
    Serial.println("------|--------|----------------|-------------");
    
    for (int i = 0; i < STATE_MAX; i++) {
        if (state_stats[i].enter_count > 0) {
            unsigned long avg_time = state_stats[i].total_time / 
                                    state_stats[i].enter_count;
            
            Serial.print(i);
            Serial.print("     | ");
            Serial.print(state_stats[i].enter_count);
            Serial.print("      | ");
            Serial.print(state_stats[i].total_time);
            Serial.print("           | ");
            Serial.println(avg_time);
        }
    }
    Serial.println("=======================\n");
}
```

### 4.3 状态机可视化

```c
// 状态名称字符串（用于调试输出）
const char* state_names[] = {
    "OFF",
    "RED",
    "GREEN",
    "BLUE",
    "BLINK",
    "RAINBOW"
};

const char* event_names[] = {
    "NONE",
    "SHORT_PRESS",
    "LONG_PRESS"
};

// 打印当前状态
void print_current_state() {
    Serial.print("[");
    Serial.print(millis());
    Serial.print("ms] Current State: ");
    Serial.println(state_names[current_state]);
}

// 打印状态转换
void print_state_transition(State_t from, Event_t event, State_t to) {
    Serial.print("[");
    Serial.print(millis());
    Serial.print("ms] ");
    Serial.print(state_names[from]);
    Serial.print(" --[");
    Serial.print(event_names[event]);
    Serial.print("]--> ");
    Serial.println(state_names[to]);
}
```


## 步骤5：高级特性实现

### 5.1 状态超时处理

有些状态需要在一定时间后自动转换：

```c
// 超时配置
typedef struct {
    State_t state;
    unsigned long timeout_ms;
    State_t timeout_next_state;
} StateTimeout_t;

// 超时配置表
const StateTimeout_t timeout_table[] = {
    {STATE_BLINK, 10000, STATE_OFF},    // 闪烁10秒后自动关闭
    {STATE_RAINBOW, 15000, STATE_OFF},  // 彩虹15秒后自动关闭
};

const int timeout_table_size = sizeof(timeout_table) / sizeof(StateTimeout_t);

// 检查超时
Event_t check_timeout() {
    unsigned long current_time = millis();
    unsigned long elapsed = current_time - state_enter_time;
    
    // 查找当前状态的超时配置
    for (int i = 0; i < timeout_table_size; i++) {
        if (timeout_table[i].state == current_state) {
            if (elapsed >= timeout_table[i].timeout_ms) {
                Serial.println("Event: TIMEOUT");
                // 直接转换到超时目标状态
                state_transition(timeout_table[i].timeout_next_state);
                return EVENT_TIMEOUT;
            }
        }
    }
    
    return EVENT_NONE;
}

// 在loop中调用
void loop() {
    // 1. 检查超时
    Event_t timeout_event = check_timeout();
    
    // 2. 检测按键事件
    Event_t button_event = detect_event();
    
    // 3. 优先处理按键事件
    Event_t event = (button_event != EVENT_NONE) ? button_event : timeout_event;
    
    // 4. 运行状态机
    state_machine_run(event);
    
    delay(10);
}
```

### 5.2 状态守卫条件

有时状态转换需要满足特定条件：

```c
// 守卫条件函数类型
typedef bool (*GuardFunc_t)(void);

// 扩展的状态转换表项
typedef struct {
    State_t current_state;
    Event_t event;
    GuardFunc_t guard;        // 守卫条件
    State_t next_state;
    ActionFunc_t action;
} StateTransitionEx_t;

// 守卫条件函数示例
bool guard_battery_ok(void) {
    // 检查电池电量是否足够
    // 这里简化为随机返回
    return true;  // 实际应用中读取电池电压
}

bool guard_temperature_ok(void) {
    // 检查温度是否正常
    return true;  // 实际应用中读取温度传感器
}

// 带守卫条件的状态转换表
const StateTransitionEx_t state_table_ex[] = {
    // 只有电池电量足够才能进入RAINBOW模式
    {STATE_BLINK, EVENT_SHORT_PRESS, guard_battery_ok, STATE_RAINBOW, action_start_rainbow},
    // 其他转换...
};

// 带守卫条件的状态机处理
void fsm_with_guard(Event_t event) {
    for (int i = 0; i < state_table_ex_size; i++) {
        if (state_table_ex[i].current_state == current_state &&
            state_table_ex[i].event == event) {
            
            // 检查守卫条件
            if (state_table_ex[i].guard == NULL || 
                state_table_ex[i].guard()) {
                
                // 条件满足，执行转换
                State_t next_state = state_table_ex[i].next_state;
                
                if (state_table_ex[i].action != NULL) {
                    state_table_ex[i].action();
                }
                
                current_state = next_state;
                return;
            } else {
                Serial.println("Guard condition failed, transition blocked");
                return;
            }
        }
    }
}
```

### 5.3 分层状态机

对于复杂系统，可以使用分层状态机：

```c
// 父状态和子状态
typedef enum {
    // 顶层状态
    STATE_SYSTEM_OFF,
    STATE_SYSTEM_ON,
    
    // ON状态的子状态
    STATE_ON_NORMAL,
    STATE_ON_SETUP,
    STATE_ON_ERROR,
} HierarchicalState_t;

// 状态层次结构
typedef struct {
    HierarchicalState_t state;
    HierarchicalState_t parent;  // 父状态
} StateHierarchy_t;

const StateHierarchy_t hierarchy[] = {
    {STATE_SYSTEM_OFF, STATE_SYSTEM_OFF},      // 顶层状态
    {STATE_SYSTEM_ON, STATE_SYSTEM_ON},        // 顶层状态
    {STATE_ON_NORMAL, STATE_SYSTEM_ON},        // ON的子状态
    {STATE_ON_SETUP, STATE_SYSTEM_ON},         // ON的子状态
    {STATE_ON_ERROR, STATE_SYSTEM_ON},         // ON的子状态
};

// 检查状态是否在某个父状态下
bool is_in_parent_state(HierarchicalState_t state, HierarchicalState_t parent) {
    for (int i = 0; i < sizeof(hierarchy)/sizeof(StateHierarchy_t); i++) {
        if (hierarchy[i].state == state) {
            return hierarchy[i].parent == parent || 
                   hierarchy[i].state == parent;
        }
    }
    return false;
}

// 分层状态机处理
void hierarchical_fsm(Event_t event) {
    // 首先尝试在当前状态处理事件
    // 如果当前状态不处理，则传递给父状态
    
    if (current_state == STATE_ON_NORMAL) {
        if (event == EVENT_SHORT_PRESS) {
            state_transition(STATE_ON_SETUP);
            return;
        }
    }
    
    // 如果子状态不处理，检查父状态
    if (is_in_parent_state(current_state, STATE_SYSTEM_ON)) {
        if (event == EVENT_LONG_PRESS) {
            // 所有ON子状态的长按都返回OFF
            state_transition(STATE_SYSTEM_OFF);
            return;
        }
    }
}
```


## 测试和验证

### 测试用例设计

**基本功能测试**：

```c
void test_basic_transitions() {
    Serial.println("\n=== Test: Basic Transitions ===");
    
    // 测试1：OFF -> RED
    current_state = STATE_OFF;
    state_machine_run(EVENT_SHORT_PRESS);
    assert(current_state == STATE_RED);
    Serial.println("✓ Test 1 passed: OFF -> RED");
    
    // 测试2：RED -> GREEN
    state_machine_run(EVENT_SHORT_PRESS);
    assert(current_state == STATE_GREEN);
    Serial.println("✓ Test 2 passed: RED -> GREEN");
    
    // 测试3：GREEN -> OFF (long press)
    state_machine_run(EVENT_LONG_PRESS);
    assert(current_state == STATE_OFF);
    Serial.println("✓ Test 3 passed: GREEN -> OFF");
    
    Serial.println("=== All basic tests passed ===\n");
}

void test_timeout() {
    Serial.println("\n=== Test: Timeout ===");
    
    // 进入BLINK状态
    current_state = STATE_OFF;
    state_machine_run(EVENT_SHORT_PRESS);  // -> RED
    state_machine_run(EVENT_SHORT_PRESS);  // -> GREEN
    state_machine_run(EVENT_SHORT_PRESS);  // -> BLUE
    state_machine_run(EVENT_SHORT_PRESS);  // -> BLINK
    
    // 等待超时
    delay(11000);  // 等待超过10秒
    check_timeout();
    
    assert(current_state == STATE_OFF);
    Serial.println("✓ Timeout test passed");
    
    Serial.println("=== Timeout test passed ===\n");
}
```

### 调试技巧

**1. 使用串口监视器**：

```c
// 详细的调试输出
#define DEBUG_FSM 1

#if DEBUG_FSM
    #define FSM_DEBUG(x) Serial.println(x)
    #define FSM_DEBUG_VAR(name, value) \
        Serial.print(name); \
        Serial.print(": "); \
        Serial.println(value)
#else
    #define FSM_DEBUG(x)
    #define FSM_DEBUG_VAR(name, value)
#endif

// 使用示例
void state_machine_run(Event_t event) {
    FSM_DEBUG("=== FSM Run ===");
    FSM_DEBUG_VAR("Current State", current_state);
    FSM_DEBUG_VAR("Event", event);
    
    // 状态机逻辑...
    
    FSM_DEBUG_VAR("Next State", current_state);
    FSM_DEBUG("===============");
}
```

**2. 状态机可视化工具**：

可以输出PlantUML格式的状态图：

```c
void export_state_diagram() {
    Serial.println("@startuml");
    Serial.println("[*] --> OFF");
    
    for (int i = 0; i < state_table_size; i++) {
        Serial.print(state_names[state_table[i].current_state]);
        Serial.print(" --> ");
        Serial.print(state_names[state_table[i].next_state]);
        Serial.print(" : ");
        Serial.println(event_names[state_table[i].event]);
    }
    
    Serial.println("@enduml");
}
```


## 故障排除

### 问题1：状态转换不正常

**现象**：
- 状态没有按预期转换
- 某些转换被跳过

**可能原因**：
1. 事件检测逻辑错误
2. 状态转换表配置错误
3. 守卫条件不满足

**解决方法**：

```c
// 添加详细的调试输出
void debug_state_transition(State_t from, Event_t event, State_t to) {
    Serial.println("\n--- State Transition Debug ---");
    Serial.print("From: ");
    Serial.println(state_names[from]);
    Serial.print("Event: ");
    Serial.println(event_names[event]);
    Serial.print("To: ");
    Serial.println(state_names[to]);
    Serial.println("-----------------------------\n");
}

// 检查转换表
void verify_transition_table() {
    Serial.println("Verifying transition table...");
    
    for (int i = 0; i < state_table_size; i++) {
        // 检查状态值是否有效
        if (state_table[i].current_state >= STATE_MAX) {
            Serial.print("Error: Invalid current_state at index ");
            Serial.println(i);
        }
        
        if (state_table[i].next_state >= STATE_MAX) {
            Serial.print("Error: Invalid next_state at index ");
            Serial.println(i);
        }
        
        // 检查事件值是否有效
        if (state_table[i].event >= EVENT_MAX) {
            Serial.print("Error: Invalid event at index ");
            Serial.println(i);
        }
    }
    
    Serial.println("Verification complete");
}
```

### 问题2：按键响应不灵敏

**现象**：
- 需要多次按键才响应
- 有时按键无效

**可能原因**：
1. 去抖动时间设置不当
2. 按键检测逻辑有问题
3. 主循环延时过长

**解决方法**：

```c
// 改进的按键检测
Event_t detect_event_improved() {
    static uint8_t button_state = 0;
    static unsigned long last_change_time = 0;
    const unsigned long DEBOUNCE_TIME = 50;
    
    bool current_reading = (digitalRead(BUTTON_PIN) == LOW);
    
    // 状态机式去抖动
    switch (button_state) {
        case 0:  // 等待按下
            if (current_reading) {
                button_state = 1;
                last_change_time = millis();
            }
            break;
            
        case 1:  // 去抖动
            if (millis() - last_change_time >= DEBOUNCE_TIME) {
                if (current_reading) {
                    button_state = 2;
                    button_press_time = millis();
                } else {
                    button_state = 0;
                }
            }
            break;
            
        case 2:  // 等待释放
            if (!current_reading) {
                button_state = 3;
                last_change_time = millis();
            }
            break;
            
        case 3:  // 去抖动
            if (millis() - last_change_time >= DEBOUNCE_TIME) {
                if (!current_reading) {
                    button_state = 0;
                    
                    // 判断按键类型
                    unsigned long duration = millis() - button_press_time;
                    if (duration >= LONG_PRESS_TIME) {
                        return EVENT_LONG_PRESS;
                    } else {
                        return EVENT_SHORT_PRESS;
                    }
                } else {
                    button_state = 2;
                }
            }
            break;
    }
    
    return EVENT_NONE;
}
```

### 问题3：内存不足

**现象**：
- 程序运行一段时间后崩溃
- 状态转换异常

**可能原因**：
1. 状态历史记录占用过多内存
2. 字符串常量占用RAM
3. 栈溢出

**解决方法**：

```c
// 1. 使用PROGMEM存储字符串常量
const char state_name_0[] PROGMEM = "OFF";
const char state_name_1[] PROGMEM = "RED";
const char state_name_2[] PROGMEM = "GREEN";
// ...

const char* const state_names_progmem[] PROGMEM = {
    state_name_0,
    state_name_1,
    state_name_2,
    // ...
};

// 读取PROGMEM中的字符串
void print_state_name(State_t state) {
    char buffer[20];
    strcpy_P(buffer, (char*)pgm_read_word(&(state_names_progmem[state])));
    Serial.println(buffer);
}

// 2. 减少历史记录大小
#define HISTORY_SIZE 5  // 从10减少到5

// 3. 监控内存使用
void print_memory_usage() {
    extern int __heap_start, *__brkval;
    int free_memory;
    
    if ((int)__brkval == 0) {
        free_memory = ((int)&free_memory) - ((int)&__heap_start);
    } else {
        free_memory = ((int)&free_memory) - ((int)__brkval);
    }
    
    Serial.print("Free memory: ");
    Serial.print(free_memory);
    Serial.println(" bytes");
}
```

### 问题4：状态机性能问题

**现象**：
- 响应延迟明显
- CPU占用率高

**可能原因**：
1. 状态转换表查找效率低
2. 状态动作函数执行时间长
3. 主循环延时不当

**解决方法**：

```c
// 1. 使用哈希表加速查找
#define HASH_TABLE_SIZE 32

typedef struct {
    uint16_t key;  // (state << 8) | event
    int table_index;
} HashEntry_t;

HashEntry_t hash_table[HASH_TABLE_SIZE];

// 初始化哈希表
void init_hash_table() {
    for (int i = 0; i < state_table_size; i++) {
        uint16_t key = (state_table[i].current_state << 8) | 
                       state_table[i].event;
        int hash = key % HASH_TABLE_SIZE;
        
        // 简单的线性探测
        while (hash_table[hash].key != 0) {
            hash = (hash + 1) % HASH_TABLE_SIZE;
        }
        
        hash_table[hash].key = key;
        hash_table[hash].table_index = i;
    }
}

// 快速查找
int find_transition(State_t state, Event_t event) {
    uint16_t key = (state << 8) | event;
    int hash = key % HASH_TABLE_SIZE;
    
    while (hash_table[hash].key != 0) {
        if (hash_table[hash].key == key) {
            return hash_table[hash].table_index;
        }
        hash = (hash + 1) % HASH_TABLE_SIZE;
    }
    
    return -1;  // 未找到
}

// 2. 性能测量
void measure_fsm_performance() {
    unsigned long start = micros();
    
    // 执行状态机
    state_machine_run(EVENT_SHORT_PRESS);
    
    unsigned long elapsed = micros() - start;
    
    Serial.print("FSM execution time: ");
    Serial.print(elapsed);
    Serial.println(" us");
}
```


## 最佳实践

### 设计原则

1. **单一职责**
   - 每个状态只负责一种行为
   - 状态转换逻辑清晰明确
   - 避免状态职责重叠

2. **开闭原则**
   - 对扩展开放：易于添加新状态
   - 对修改封闭：不影响现有状态
   - 使用表驱动方法提高灵活性

3. **最小化状态数量**
   - 合并相似状态
   - 使用参数区分细微差异
   - 避免状态爆炸

4. **明确的进入/退出动作**
   - 每个状态有清晰的初始化
   - 退出时清理资源
   - 避免状态间的隐式依赖

### 代码组织

**推荐的文件结构**：

```
project/
├── main.ino              # 主程序
├── state_machine.h       # 状态机接口
├── state_machine.c       # 状态机实现
├── state_actions.h       # 动作函数声明
├── state_actions.c       # 动作函数实现
├── events.h              # 事件定义和检测
└── config.h              # 配置参数
```

**头文件示例（state_machine.h）**：

```c
#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <stdint.h>
#include <stdbool.h>

// 状态定义
typedef enum {
    STATE_OFF,
    STATE_RED,
    STATE_GREEN,
    STATE_BLUE,
    STATE_BLINK,
    STATE_RAINBOW,
    STATE_MAX
} State_t;

// 事件定义
typedef enum {
    EVENT_NONE,
    EVENT_SHORT_PRESS,
    EVENT_LONG_PRESS,
    EVENT_TIMEOUT,
    EVENT_MAX
} Event_t;

// 公共接口
void fsm_init(void);
void fsm_run(Event_t event);
State_t fsm_get_current_state(void);
void fsm_reset(void);

// 调试接口
void fsm_print_state(void);
void fsm_print_statistics(void);

#endif // STATE_MACHINE_H
```

### 性能优化

**1. 减少状态转换开销**：

```c
// 只在状态真正改变时执行动作
void optimized_state_transition(State_t new_state) {
    if (new_state == current_state) {
        return;  // 状态未改变，直接返回
    }
    
    // 执行转换...
}
```

**2. 批量处理事件**：

```c
// 事件队列
#define EVENT_QUEUE_SIZE 8
Event_t event_queue[EVENT_QUEUE_SIZE];
int queue_head = 0;
int queue_tail = 0;

// 入队
bool enqueue_event(Event_t event) {
    int next = (queue_tail + 1) % EVENT_QUEUE_SIZE;
    if (next == queue_head) {
        return false;  // 队列满
    }
    
    event_queue[queue_tail] = event;
    queue_tail = next;
    return true;
}

// 出队
Event_t dequeue_event() {
    if (queue_head == queue_tail) {
        return EVENT_NONE;  // 队列空
    }
    
    Event_t event = event_queue[queue_head];
    queue_head = (queue_head + 1) % EVENT_QUEUE_SIZE;
    return event;
}

// 批量处理
void process_event_queue() {
    while (queue_head != queue_tail) {
        Event_t event = dequeue_event();
        state_machine_run(event);
    }
}
```


## 实战案例：智能交通灯系统

### 案例需求

设计一个智能交通灯控制系统：

**基本功能**：
- 正常模式：红灯(30s) → 绿灯(25s) → 黄灯(5s) → 循环
- 夜间模式：黄灯闪烁
- 维护模式：全红灯
- 紧急模式：全红灯闪烁

**控制方式**：
- 按键1：模式切换
- 按键2：紧急模式
- 自动检测：夜间自动切换

### 完整实现

```c
// traffic_light_fsm.ino

// 硬件定义
#define LED_RED    9
#define LED_YELLOW 10
#define LED_GREEN  11
#define BUTTON_MODE 2
#define BUTTON_EMERGENCY 3

// 状态定义
typedef enum {
    STATE_NORMAL_RED,
    STATE_NORMAL_GREEN,
    STATE_NORMAL_YELLOW,
    STATE_NIGHT_BLINK,
    STATE_MAINTENANCE,
    STATE_EMERGENCY
} TrafficState_t;

// 事件定义
typedef enum {
    EVENT_NONE,
    EVENT_TIMEOUT,
    EVENT_MODE_SWITCH,
    EVENT_EMERGENCY,
    EVENT_NIGHT_DETECTED,
    EVENT_DAY_DETECTED
} TrafficEvent_t;

// 全局变量
TrafficState_t current_state = STATE_NORMAL_RED;
unsigned long state_enter_time = 0;
bool emergency_active = false;

// 状态超时配置
typedef struct {
    TrafficState_t state;
    unsigned long timeout_ms;
    TrafficState_t next_state;
} StateTimeout_t;

const StateTimeout_t timeout_config[] = {
    {STATE_NORMAL_RED, 30000, STATE_NORMAL_GREEN},      // 红灯30秒
    {STATE_NORMAL_GREEN, 25000, STATE_NORMAL_YELLOW},   // 绿灯25秒
    {STATE_NORMAL_YELLOW, 5000, STATE_NORMAL_RED},      // 黄灯5秒
};

// LED控制函数
void set_traffic_light(bool red, bool yellow, bool green) {
    digitalWrite(LED_RED, red ? HIGH : LOW);
    digitalWrite(LED_YELLOW, yellow ? HIGH : LOW);
    digitalWrite(LED_GREEN, green ? HIGH : LOW);
}

// 状态进入动作
void state_enter_action(TrafficState_t state) {
    state_enter_time = millis();
    
    Serial.print("Enter state: ");
    
    switch (state) {
        case STATE_NORMAL_RED:
            Serial.println("NORMAL_RED (30s)");
            set_traffic_light(true, false, false);
            break;
            
        case STATE_NORMAL_GREEN:
            Serial.println("NORMAL_GREEN (25s)");
            set_traffic_light(false, false, true);
            break;
            
        case STATE_NORMAL_YELLOW:
            Serial.println("NORMAL_YELLOW (5s)");
            set_traffic_light(false, true, false);
            break;
            
        case STATE_NIGHT_BLINK:
            Serial.println("NIGHT_BLINK");
            set_traffic_light(false, false, false);
            break;
            
        case STATE_MAINTENANCE:
            Serial.println("MAINTENANCE");
            set_traffic_light(true, false, false);
            break;
            
        case STATE_EMERGENCY:
            Serial.println("EMERGENCY");
            emergency_active = true;
            break;
    }
}

// 状态持续动作
void state_do_action(TrafficState_t state) {
    static unsigned long last_blink = 0;
    static bool blink_on = false;
    
    switch (state) {
        case STATE_NIGHT_BLINK:
            // 黄灯闪烁（每500ms）
            if (millis() - last_blink >= 500) {
                last_blink = millis();
                blink_on = !blink_on;
                set_traffic_light(false, blink_on, false);
            }
            break;
            
        case STATE_EMERGENCY:
            // 红灯快速闪烁（每200ms）
            if (millis() - last_blink >= 200) {
                last_blink = millis();
                blink_on = !blink_on;
                set_traffic_light(blink_on, false, false);
            }
            break;
            
        default:
            // 其他状态不需要持续动作
            break;
    }
}

// 检查超时
TrafficEvent_t check_timeout() {
    unsigned long elapsed = millis() - state_enter_time;
    
    for (int i = 0; i < sizeof(timeout_config)/sizeof(StateTimeout_t); i++) {
        if (timeout_config[i].state == current_state) {
            if (elapsed >= timeout_config[i].timeout_ms) {
                return EVENT_TIMEOUT;
            }
        }
    }
    
    return EVENT_NONE;
}

// 状态机处理
void traffic_fsm(TrafficEvent_t event) {
    // 执行当前状态的持续动作
    state_do_action(current_state);
    
    // 处理事件和状态转换
    TrafficState_t next_state = current_state;
    
    switch (current_state) {
        case STATE_NORMAL_RED:
            if (event == EVENT_TIMEOUT) {
                next_state = STATE_NORMAL_GREEN;
            } else if (event == EVENT_MODE_SWITCH) {
                next_state = STATE_MAINTENANCE;
            } else if (event == EVENT_EMERGENCY) {
                next_state = STATE_EMERGENCY;
            } else if (event == EVENT_NIGHT_DETECTED) {
                next_state = STATE_NIGHT_BLINK;
            }
            break;
            
        case STATE_NORMAL_GREEN:
            if (event == EVENT_TIMEOUT) {
                next_state = STATE_NORMAL_YELLOW;
            } else if (event == EVENT_EMERGENCY) {
                next_state = STATE_EMERGENCY;
            }
            break;
            
        case STATE_NORMAL_YELLOW:
            if (event == EVENT_TIMEOUT) {
                next_state = STATE_NORMAL_RED;
            } else if (event == EVENT_EMERGENCY) {
                next_state = STATE_EMERGENCY;
            }
            break;
            
        case STATE_NIGHT_BLINK:
            if (event == EVENT_DAY_DETECTED) {
                next_state = STATE_NORMAL_RED;
            } else if (event == EVENT_MODE_SWITCH) {
                next_state = STATE_MAINTENANCE;
            } else if (event == EVENT_EMERGENCY) {
                next_state = STATE_EMERGENCY;
            }
            break;
            
        case STATE_MAINTENANCE:
            if (event == EVENT_MODE_SWITCH) {
                next_state = STATE_NORMAL_RED;
            } else if (event == EVENT_EMERGENCY) {
                next_state = STATE_EMERGENCY;
            }
            break;
            
        case STATE_EMERGENCY:
            if (event == EVENT_EMERGENCY) {
                // 再次按紧急按钮退出紧急模式
                emergency_active = false;
                next_state = STATE_NORMAL_RED;
            }
            break;
    }
    
    // 执行状态转换
    if (next_state != current_state) {
        current_state = next_state;
        state_enter_action(current_state);
    }
}

// 事件检测
TrafficEvent_t detect_event() {
    static bool last_mode_button = HIGH;
    static bool last_emergency_button = HIGH;
    
    // 检测模式切换按钮
    bool mode_button = digitalRead(BUTTON_MODE);
    if (last_mode_button == HIGH && mode_button == LOW) {
        delay(50);  // 去抖动
        while (digitalRead(BUTTON_MODE) == LOW);  // 等待释放
        last_mode_button = HIGH;
        return EVENT_MODE_SWITCH;
    }
    last_mode_button = mode_button;
    
    // 检测紧急按钮
    bool emergency_button = digitalRead(BUTTON_EMERGENCY);
    if (last_emergency_button == HIGH && emergency_button == LOW) {
        delay(50);
        while (digitalRead(BUTTON_EMERGENCY) == LOW);
        last_emergency_button = HIGH;
        return EVENT_EMERGENCY;
    }
    last_emergency_button = emergency_button;
    
    // 检查超时
    TrafficEvent_t timeout = check_timeout();
    if (timeout != EVENT_NONE) {
        return timeout;
    }
    
    return EVENT_NONE;
}

void setup() {
    Serial.begin(115200);
    Serial.println("Smart Traffic Light System");
    Serial.println("==========================");
    Serial.println("Button 1: Mode switch");
    Serial.println("Button 2: Emergency\n");
    
    // 配置引脚
    pinMode(LED_RED, OUTPUT);
    pinMode(LED_YELLOW, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(BUTTON_MODE, INPUT_PULLUP);
    pinMode(BUTTON_EMERGENCY, INPUT_PULLUP);
    
    // 初始化状态
    state_enter_action(STATE_NORMAL_RED);
}

void loop() {
    // 检测事件
    TrafficEvent_t event = detect_event();
    
    // 运行状态机
    traffic_fsm(event);
    
    // 显示状态信息（每5秒）
    static unsigned long last_info = 0;
    if (millis() - last_info >= 5000) {
        last_info = millis();
        unsigned long elapsed = (millis() - state_enter_time) / 1000;
        Serial.print("Current state: ");
        Serial.print(current_state);
        Serial.print(", Time: ");
        Serial.print(elapsed);
        Serial.println("s");
    }
    
    delay(10);
}
```

**运行效果**：

```
Smart Traffic Light System
==========================
Button 1: Mode switch
Button 2: Emergency

Enter state: NORMAL_RED (30s)
Current state: 0, Time: 5s
Current state: 0, Time: 10s
...
Current state: 0, Time: 30s
Enter state: NORMAL_GREEN (25s)
Current state: 1, Time: 5s
...
```


## 总结

通过本教程，你学习了：

- ✅ 状态机的基本概念和工作原理
- ✅ 如何设计状态图和状态转换表
- ✅ 使用switch-case实现简单状态机
- ✅ 使用表驱动方法实现灵活的状态机
- ✅ 状态进入/退出/持续动作的实现
- ✅ 事件检测和处理技术
- ✅ 超时处理和守卫条件
- ✅ 状态机的调试和测试方法
- ✅ 实际项目中的应用案例

**关键要点**：

1. **状态机是管理复杂控制逻辑的有效工具**
   - 清晰的状态定义
   - 明确的转换规则
   - 易于理解和维护

2. **选择合适的实现方法**
   - 简单系统：switch-case
   - 复杂系统：表驱动
   - 超大系统：分层状态机

3. **注重代码质量**
   - 模块化设计
   - 充分的注释
   - 完善的测试

4. **性能和资源平衡**
   - 合理使用内存
   - 优化执行效率
   - 考虑实时性要求


## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1：电梯控制系统**
   - 实现多楼层电梯控制
   - 支持上行、下行、停止状态
   - 处理多个呼叫请求
   - 实现最优调度算法

2. **挑战2：洗衣机控制器**
   - 多种洗涤程序（标准、快洗、羊毛等）
   - 每个程序包含多个阶段
   - 支持暂停和恢复
   - 显示剩余时间

3. **挑战3：游戏状态管理**
   - 菜单、游戏、暂停、结束状态
   - 状态间的平滑过渡
   - 保存和加载游戏状态
   - 实现状态栈（支持返回）

4. **挑战4：通信协议实现**
   - 实现UART通信协议状态机
   - 处理帧头、数据、校验、帧尾
   - 错误检测和重传
   - 超时处理


## 延伸阅读

**推荐资源**：

1. **书籍**
   - 《设计模式：可复用面向对象软件的基础》- 状态模式章节
   - 《嵌入式系统设计模式》
   - 《实用状态图：C/C++事件驱动编程》

2. **在线资源**
   - [UML状态图教程](https://www.uml-diagrams.org/state-machine-diagrams.html)
   - [Quantum Leaps - 状态机框架](https://www.state-machine.com/)
   - [PlantUML状态图语法](https://plantuml.com/state-diagram)

3. **开源项目**
   - TinyFSM - 轻量级C++状态机库
   - SMC (State Machine Compiler) - 状态机代码生成器
   - QP/C - 专业的嵌入式状态机框架

**下一步学习**：

- [CLI框架开发](../intermediate/01-cli-framework.html) - 学习命令行接口设计
- [日志系统架构](../intermediate/02-logging-architecture.html) - 学习系统日志设计
- [完整应用框架](../advanced/01-application-framework.html) - 构建完整的应用框架


## 参考资料

1. UML 2.5 Specification - State Machine Diagrams
2. "Practical Statecharts in C/C++" by Miro Samek
3. "Design Patterns" by Gang of Four
4. IEEE Std 1016-2009 - Software Design Descriptions

---

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言！

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。
