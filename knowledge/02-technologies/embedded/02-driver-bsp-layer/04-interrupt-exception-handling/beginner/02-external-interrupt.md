---
title: "外部中断配置与使用"
description: "深入学习嵌入式系统外部中断(EXTI)的配置方法和实际应用，包括触发方式、中断服务函数编写、按键中断处理和防抖技术，通过实战项目掌握外部中断开发技能"
slug: "external-interrupt"

# 分类信息
domain: "驱动与BSP层"
module: "中断与异常处理"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 外部中断
  - EXTI
  - 按键中断
  - 防抖处理
  - GPIO中断
prerequisites:
  - "interrupt-basics"
related_contents:
  - "timer-interrupt"
  - "interrupt-debugging"

# 学习信息
estimated_time: 60
difficulty_score: 3

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
  - 外部中断
  - EXTI配置
  - 按键中断
  - 中断防抖
  - GPIO中断
cover_image: ""
---

# 外部中断配置与使用

## 概述

外部中断(EXTI - External Interrupt)是嵌入式系统中最常用的中断类型之一，它允许系统响应来自GPIO引脚的外部信号变化。通过本教程，你将学会：

- 理解EXTI的工作原理和硬件结构
- 掌握不同触发方式的配置方法
- 编写规范的中断服务函数
- 实现按键中断并处理防抖问题
- 调试和优化外部中断应用

## 学习目标

完成本教程后，你将能够：

1. 配置GPIO引脚为外部中断模式
2. 选择合适的触发方式（上升沿/下降沿/双边沿）
3. 编写高效的中断服务函数
4. 实现按键防抖的软件和硬件方案
5. 处理多个外部中断源
6. 调试外部中断相关问题

## 背景知识

### EXTI系统架构

STM32的EXTI控制器提供了23条外部中断/事件线（不同型号可能有差异）：

- **EXTI0-EXTI15**：连接到GPIO引脚
- **EXTI16**：连接到PVD输出
- **EXTI17**：连接到RTC闹钟事件
- **EXTI18**：连接到USB唤醒事件
- **EXTI19**：连接到以太网唤醒事件
- **EXTI20-EXTI22**：其他内部事件

**EXTI线路映射规则**：
```
EXTI0 可以连接到：PA0, PB0, PC0, PD0, PE0, PF0, PG0
EXTI1 可以连接到：PA1, PB1, PC1, PD1, PE1, PF1, PG1
...
EXTI15 可以连接到：PA15, PB15, PC15, PD15, PE15, PF15, PG15
```

**重要限制**：同一时刻，每条EXTI线只能连接到一个GPIO端口的对应引脚。例如，不能同时使用PA0和PB0作为中断源。

### EXTI工作流程

```
GPIO引脚电平变化
    ↓
边沿检测电路（上升沿/下降沿/双边沿）
    ↓
触发条件满足
    ↓
设置挂起寄存器标志位
    ↓
中断使能？ → 是 → 产生中断请求 → NVIC → CPU执行ISR
    ↓
   否
    ↓
事件使能？ → 是 → 产生事件脉冲（用于DMA等）
```


## 核心内容

### 1. EXTI配置步骤

配置外部中断需要以下几个步骤：

#### 步骤1：使能GPIO时钟

```c
// 使能GPIOA时钟
__HAL_RCC_GPIOA_CLK_ENABLE();
```

#### 步骤2：配置GPIO为中断模式

```c
GPIO_InitTypeDef GPIO_InitStruct = {0};

GPIO_InitStruct.Pin = GPIO_PIN_0;           // 选择引脚
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING; // 中断模式，上升沿触发
GPIO_InitStruct.Pull = GPIO_PULLDOWN;       // 下拉电阻
GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;

HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
```

**GPIO模式选项**：
- `GPIO_MODE_IT_RISING`：上升沿触发中断
- `GPIO_MODE_IT_FALLING`：下降沿触发中断
- `GPIO_MODE_IT_RISING_FALLING`：双边沿触发中断
- `GPIO_MODE_EVT_RISING`：上升沿触发事件（不产生中断）
- `GPIO_MODE_EVT_FALLING`：下降沿触发事件
- `GPIO_MODE_EVT_RISING_FALLING`：双边沿触发事件

#### 步骤3：配置NVIC优先级

```c
// 设置中断优先级
HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);

// 使能NVIC中断
HAL_NVIC_EnableIRQ(EXTI0_IRQn);
```

**EXTI中断号映射**：
```
EXTI0_IRQn      → EXTI线0
EXTI1_IRQn      → EXTI线1
EXTI2_IRQn      → EXTI线2
EXTI3_IRQn      → EXTI线3
EXTI4_IRQn      → EXTI线4
EXTI9_5_IRQn    → EXTI线5-9（共享）
EXTI15_10_IRQn  → EXTI线10-15（共享）
```

#### 步骤4：编写中断服务函数

```c
void EXTI0_IRQHandler(void)
{
    // 检查中断标志
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET)
    {
        // 清除中断标志（必须！）
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 调用用户回调函数
        HAL_GPIO_EXTI_Callback(GPIO_PIN_0);
    }
}

// 用户回调函数
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == GPIO_PIN_0)
    {
        // 处理PA0的中断
        // 例如：翻转LED状态
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
    }
}
```


### 2. 触发方式详解

#### 2.1 上升沿触发

当GPIO引脚从低电平变为高电平时触发中断。

**应用场景**：
- 按键按下检测（按键接VCC，引脚下拉）
- 传感器信号上升沿检测
- 脉冲信号计数

```c
// 配置上升沿触发
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
GPIO_InitStruct.Pull = GPIO_PULLDOWN;  // 下拉，确保默认低电平
```

**时序图**：
```
GPIO引脚电平：
    ___________
   |           |
___|           |___
   ↑
   触发中断
```

#### 2.2 下降沿触发

当GPIO引脚从高电平变为低电平时触发中断。

**应用场景**：
- 按键释放检测
- 传感器信号下降沿检测
- 负脉冲检测

```c
// 配置下降沿触发
GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
GPIO_InitStruct.Pull = GPIO_PULLUP;  // 上拉，确保默认高电平
```

**时序图**：
```
GPIO引脚电平：
___         ___
   |       |
   |_______|
         ↑
      触发中断
```

#### 2.3 双边沿触发

当GPIO引脚电平发生任何变化时都触发中断。

**应用场景**：
- 编码器信号检测
- 脉宽测量
- 频率测量
- 状态变化监测

```c
// 配置双边沿触发
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING_FALLING;
GPIO_InitStruct.Pull = GPIO_NOPULL;  // 根据实际情况选择
```

**时序图**：
```
GPIO引脚电平：
    ___     ___
   |   |   |   |
___|   |___|   |___
   ↑   ↑   ↑   ↑
   触发中断（每次边沿都触发）
```

#### 2.4 触发方式选择建议

| 应用场景 | 推荐触发方式 | 上拉/下拉配置 | 原因 |
|---------|------------|-------------|------|
| 按键按下检测 | 上升沿 | 下拉 | 按键按下时产生上升沿 |
| 按键释放检测 | 下降沿 | 上拉 | 按键释放时产生下降沿 |
| 按键按下和释放 | 双边沿 | 根据电路 | 检测所有状态变化 |
| 脉冲计数 | 上升沿或下降沿 | 根据信号 | 只计数一个边沿 |
| 频率测量 | 双边沿 | 根据信号 | 需要测量完整周期 |
| 编码器 | 双边沿 | 根据编码器 | 需要检测所有变化 |


### 3. 按键中断实现

#### 3.1 基本按键中断

最简单的按键中断实现：

```c
#include "stm32f4xx_hal.h"

// 按键连接到PA0，LED连接到PD12
#define BUTTON_PIN       GPIO_PIN_0
#define BUTTON_PORT      GPIOA
#define LED_PIN          GPIO_PIN_12
#define LED_PORT         GPIOD

// 初始化LED
void LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOD_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = LED_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    
    HAL_GPIO_Init(LED_PORT, &GPIO_InitStruct);
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
}

// 初始化按键中断
void Button_EXTI_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 1. 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 2. 配置GPIO为中断模式
    GPIO_InitStruct.Pin = BUTTON_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;  // 上升沿触发
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;        // 下拉
    
    HAL_GPIO_Init(BUTTON_PORT, &GPIO_InitStruct);
    
    // 3. 配置NVIC
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

// 中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 翻转LED
        HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    LED_Init();
    Button_EXTI_Init();
    
    while (1)
    {
        // 主循环可以执行其他任务
    }
}
```

**问题**：这个简单实现存在按键抖动问题，一次按键可能触发多次中断。


#### 3.2 按键抖动问题

**什么是按键抖动？**

机械按键在按下或释放时，触点会产生多次弹跳，导致电平在短时间内多次变化。

```
理想的按键信号：
    _______________
   |
___|

实际的按键信号（有抖动）：
    ___ _ ________
   | | | |
___|_|_|_|
   ↑↑↑↑
   多次触发中断
```

**抖动持续时间**：通常为5-20ms

**影响**：
- 一次按键触发多次中断
- 计数不准确
- 状态切换混乱

#### 3.3 软件防抖方案

**方案1：延时防抖**

最简单的防抖方法，在中断中延时一段时间。

```c
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 延时防抖（不推荐在ISR中使用长延时）
        HAL_Delay(20);
        
        // 再次检查按键状态
        if (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN) == GPIO_PIN_SET)
        {
            // 确认按键按下
            Button_Pressed_Handler();
        }
    }
}
```

**缺点**：
- 在ISR中延时会阻塞其他中断
- 不符合ISR应该快速返回的原则

**方案2：标志位+定时器防抖（推荐）**

使用标志位和定时器实现防抖，ISR快速返回。

```c
// 全局变量
volatile uint8_t button_event = 0;
volatile uint32_t button_press_time = 0;

#define DEBOUNCE_TIME_MS  20  // 防抖时间

// 中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 记录按键事件和时间
        button_event = 1;
        button_press_time = HAL_GetTick();
    }
}

// 在主循环中处理
void Button_Process(void)
{
    if (button_event)
    {
        // 检查是否过了防抖时间
        if ((HAL_GetTick() - button_press_time) >= DEBOUNCE_TIME_MS)
        {
            // 再次检查按键状态
            if (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN) == GPIO_PIN_SET)
            {
                // 确认按键按下
                Button_Pressed_Handler();
            }
            
            button_event = 0;  // 清除标志
        }
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    LED_Init();
    Button_EXTI_Init();
    
    while (1)
    {
        Button_Process();  // 处理按键事件
        
        // 其他任务
    }
}
```

**方案3：状态机防抖（最佳）**

使用状态机实现更可靠的防抖。

```c
typedef enum {
    BUTTON_STATE_IDLE,
    BUTTON_STATE_PRESSED,
    BUTTON_STATE_DEBOUNCE,
    BUTTON_STATE_RELEASED
} ButtonState_t;

typedef struct {
    GPIO_TypeDef* port;
    uint16_t pin;
    ButtonState_t state;
    uint32_t press_time;
    uint32_t release_time;
    uint8_t press_count;
} Button_t;

Button_t button = {
    .port = GPIOA,
    .pin = GPIO_PIN_0,
    .state = BUTTON_STATE_IDLE,
    .press_count = 0
};

#define DEBOUNCE_TIME_MS  20

// 中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(button.pin) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(button.pin);
        
        // 只记录时间，不做处理
        if (button.state == BUTTON_STATE_IDLE)
        {
            button.press_time = HAL_GetTick();
            button.state = BUTTON_STATE_PRESSED;
        }
    }
}

// 按键状态机处理
void Button_StateMachine(void)
{
    uint32_t current_time = HAL_GetTick();
    uint8_t pin_state = HAL_GPIO_ReadPin(button.port, button.pin);
    
    switch (button.state)
    {
        case BUTTON_STATE_IDLE:
            // 等待按键按下
            break;
            
        case BUTTON_STATE_PRESSED:
            // 等待防抖时间
            if ((current_time - button.press_time) >= DEBOUNCE_TIME_MS)
            {
                if (pin_state == GPIO_PIN_SET)
                {
                    // 确认按键按下
                    button.state = BUTTON_STATE_DEBOUNCE;
                    button.press_count++;
                    
                    // 执行按键按下的动作
                    Button_Pressed_Handler();
                }
                else
                {
                    // 误触发，返回空闲状态
                    button.state = BUTTON_STATE_IDLE;
                }
            }
            break;
            
        case BUTTON_STATE_DEBOUNCE:
            // 等待按键释放
            if (pin_state == GPIO_PIN_RESET)
            {
                button.release_time = current_time;
                button.state = BUTTON_STATE_RELEASED;
            }
            break;
            
        case BUTTON_STATE_RELEASED:
            // 释放防抖
            if ((current_time - button.release_time) >= DEBOUNCE_TIME_MS)
            {
                if (pin_state == GPIO_PIN_RESET)
                {
                    // 确认按键释放
                    button.state = BUTTON_STATE_IDLE;
                    
                    // 执行按键释放的动作
                    Button_Released_Handler();
                }
                else
                {
                    // 还在按下状态
                    button.state = BUTTON_STATE_DEBOUNCE;
                }
            }
            break;
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    LED_Init();
    Button_EXTI_Init();
    
    while (1)
    {
        Button_StateMachine();  // 周期性调用状态机
        
        // 其他任务
        HAL_Delay(1);  // 1ms轮询一次
    }
}
```


#### 3.4 硬件防抖方案

**方案1：RC滤波电路**

使用电阻和电容组成低通滤波器，滤除高频抖动信号。

```
VCC
 |
 R (10kΩ)
 |
 +-------- 到MCU引脚
 |
 C (0.1μF)
 |
GND

时间常数 τ = R × C = 10kΩ × 0.1μF = 1ms
```

**方案2：施密特触发器**

使用施密特触发器芯片（如74HC14）整形信号。

**优点**：
- 不占用CPU时间
- 防抖效果稳定
- 适合高频按键

**缺点**：
- 增加硬件成本
- 需要额外的PCB空间


### 4. 多个外部中断处理

#### 4.1 独立中断线（EXTI0-EXTI4）

EXTI0到EXTI4各有独立的中断向量，配置简单。

```c
// 配置多个独立中断
void Multi_Button_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    // 按键1：PA0 -> EXTI0
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 按键2：PB1 -> EXTI1
    GPIO_InitStruct.Pin = GPIO_PIN_1;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI1_IRQn, 2, 1);
    HAL_NVIC_EnableIRQ(EXTI1_IRQn);
    
    // 按键3：PA2 -> EXTI2
    GPIO_InitStruct.Pin = GPIO_PIN_2;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI2_IRQn, 2, 2);
    HAL_NVIC_EnableIRQ(EXTI2_IRQn);
}

// 各自的中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        Button1_Handler();
    }
}

void EXTI1_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_1))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_1);
        Button2_Handler();
    }
}

void EXTI2_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_2))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_2);
        Button3_Handler();
    }
}
```

#### 4.2 共享中断线（EXTI5-9和EXTI10-15）

EXTI5-9共享一个中断向量，EXTI10-15共享另一个中断向量。

```c
// 配置共享中断线
void Shared_EXTI_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    // 按键1：PA5 -> EXTI5
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 按键2：PB6 -> EXTI6
    GPIO_InitStruct.Pin = GPIO_PIN_6;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    // 按键3：PA7 -> EXTI7
    GPIO_InitStruct.Pin = GPIO_PIN_7;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 配置共享中断向量
    HAL_NVIC_SetPriority(EXTI9_5_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
}

// 共享中断服务函数 - 需要判断具体是哪个引脚
void EXTI9_5_IRQHandler(void)
{
    // 检查EXTI5
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_5))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_5);
        Button1_Handler();
    }
    
    // 检查EXTI6
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_6))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_6);
        Button2_Handler();
    }
    
    // 检查EXTI7
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_7))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_7);
        Button3_Handler();
    }
}

// EXTI10-15的共享中断
void EXTI15_10_IRQHandler(void)
{
    // 检查EXTI10
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_10))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_10);
        Button4_Handler();
    }
    
    // 检查EXTI11
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_11))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_11);
        Button5_Handler();
    }
    
    // ... 其他引脚
}
```


## 实践项目

### 项目：多功能按键系统

实现一个支持单击、双击、长按的按键系统。

#### 项目需求

1. 单击：快速按下并释放，LED1翻转
2. 双击：在500ms内按下两次，LED2翻转
3. 长按：按住超过2秒，LED3翻转
4. 支持防抖
5. 显示按键统计信息

#### 完整代码实现

```c
#include "stm32f4xx_hal.h"
#include <stdio.h>

// 按键状态定义
typedef enum {
    BUTTON_EVENT_NONE,
    BUTTON_EVENT_SINGLE_CLICK,
    BUTTON_EVENT_DOUBLE_CLICK,
    BUTTON_EVENT_LONG_PRESS
} ButtonEvent_t;

// 按键结构体
typedef struct {
    GPIO_TypeDef* port;
    uint16_t pin;
    
    uint32_t press_time;
    uint32_t release_time;
    uint32_t last_click_time;
    
    uint8_t is_pressed;
    uint8_t click_count;
    uint8_t long_press_triggered;
    
    ButtonEvent_t event;
    
    // 统计信息
    uint32_t single_click_count;
    uint32_t double_click_count;
    uint32_t long_press_count;
} Button_t;

// 时间参数配置
#define DEBOUNCE_TIME_MS      20    // 防抖时间
#define DOUBLE_CLICK_TIME_MS  500   // 双击间隔时间
#define LONG_PRESS_TIME_MS    2000  // 长按时间

// 全局按键对象
Button_t button = {
    .port = GPIOA,
    .pin = GPIO_PIN_0,
    .is_pressed = 0,
    .click_count = 0,
    .event = BUTTON_EVENT_NONE
};

// LED引脚定义
#define LED1_PIN  GPIO_PIN_12
#define LED2_PIN  GPIO_PIN_13
#define LED3_PIN  GPIO_PIN_14
#define LED_PORT  GPIOD

// LED初始化
void LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOD_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = LED1_PIN | LED2_PIN | LED3_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    
    HAL_GPIO_Init(LED_PORT, &GPIO_InitStruct);
    
    // 初始状态全部关闭
    HAL_GPIO_WritePin(LED_PORT, LED1_PIN | LED2_PIN | LED3_PIN, GPIO_PIN_RESET);
}

// 按键初始化
void Button_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 配置为双边沿触发（检测按下和释放）
    GPIO_InitStruct.Pin = button.pin;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING_FALLING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    
    HAL_GPIO_Init(button.port, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

// 中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(button.pin) != RESET)
    {
        __HAL_GPIO_EXTI_CLEAR_IT(button.pin);
        
        uint32_t current_time = HAL_GetTick();
        uint8_t pin_state = HAL_GPIO_ReadPin(button.port, button.pin);
        
        if (pin_state == GPIO_PIN_SET && !button.is_pressed)
        {
            // 按键按下
            button.press_time = current_time;
            button.is_pressed = 1;
            button.long_press_triggered = 0;
        }
        else if (pin_state == GPIO_PIN_RESET && button.is_pressed)
        {
            // 按键释放
            button.release_time = current_time;
            button.is_pressed = 0;
            
            // 检查是否是有效按键（防抖）
            uint32_t press_duration = button.release_time - button.press_time;
            if (press_duration >= DEBOUNCE_TIME_MS && 
                press_duration < LONG_PRESS_TIME_MS)
            {
                // 有效的短按
                button.click_count++;
                button.last_click_time = current_time;
            }
        }
    }
}

// 按键处理函数
void Button_Process(void)
{
    uint32_t current_time = HAL_GetTick();
    
    // 检查长按
    if (button.is_pressed && !button.long_press_triggered)
    {
        uint32_t press_duration = current_time - button.press_time;
        if (press_duration >= LONG_PRESS_TIME_MS)
        {
            button.long_press_triggered = 1;
            button.event = BUTTON_EVENT_LONG_PRESS;
            button.long_press_count++;
            button.click_count = 0;  // 清除点击计数
        }
    }
    
    // 检查单击和双击
    if (button.click_count > 0 && !button.is_pressed)
    {
        uint32_t time_since_last_click = current_time - button.last_click_time;
        
        if (time_since_last_click >= DOUBLE_CLICK_TIME_MS)
        {
            // 超时，判定为单击或双击
            if (button.click_count == 1)
            {
                button.event = BUTTON_EVENT_SINGLE_CLICK;
                button.single_click_count++;
            }
            else if (button.click_count >= 2)
            {
                button.event = BUTTON_EVENT_DOUBLE_CLICK;
                button.double_click_count++;
            }
            
            button.click_count = 0;
        }
    }
}

// 事件处理函数
void Button_Event_Handler(void)
{
    switch (button.event)
    {
        case BUTTON_EVENT_SINGLE_CLICK:
            printf("Single Click! (Total: %lu)\n", button.single_click_count);
            HAL_GPIO_TogglePin(LED_PORT, LED1_PIN);
            break;
            
        case BUTTON_EVENT_DOUBLE_CLICK:
            printf("Double Click! (Total: %lu)\n", button.double_click_count);
            HAL_GPIO_TogglePin(LED_PORT, LED2_PIN);
            break;
            
        case BUTTON_EVENT_LONG_PRESS:
            printf("Long Press! (Total: %lu)\n", button.long_press_count);
            HAL_GPIO_TogglePin(LED_PORT, LED3_PIN);
            break;
            
        default:
            break;
    }
    
    button.event = BUTTON_EVENT_NONE;
}

// 打印统计信息
void Button_Print_Statistics(void)
{
    printf("\n=== Button Statistics ===\n");
    printf("Single Clicks: %lu\n", button.single_click_count);
    printf("Double Clicks: %lu\n", button.double_click_count);
    printf("Long Presses:  %lu\n", button.long_press_count);
    printf("========================\n\n");
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    LED_Init();
    Button_Init();
    
    printf("Multi-Function Button System Started\n");
    printf("- Single Click: Toggle LED1\n");
    printf("- Double Click: Toggle LED2\n");
    printf("- Long Press:   Toggle LED3\n\n");
    
    uint32_t last_stats_time = 0;
    
    while (1)
    {
        // 处理按键
        Button_Process();
        Button_Event_Handler();
        
        // 每10秒打印一次统计信息
        if ((HAL_GetTick() - last_stats_time) >= 10000)
        {
            Button_Print_Statistics();
            last_stats_time = HAL_GetTick();
        }
        
        HAL_Delay(1);  // 1ms轮询
    }
}
```


#### 项目测试

**测试步骤**：

1. 编译并下载程序到开发板
2. 打开串口终端（115200波特率）
3. 测试单击：快速按下并释放按键，观察LED1和串口输出
4. 测试双击：在500ms内快速按两次，观察LED2和串口输出
5. 测试长按：按住按键超过2秒，观察LED3和串口输出
6. 观察10秒后的统计信息输出

**预期输出**：
```
Multi-Function Button System Started
- Single Click: Toggle LED1
- Double Click: Toggle LED2
- Long Press:   Toggle LED3

Single Click! (Total: 1)
Single Click! (Total: 2)
Double Click! (Total: 1)
Long Press! (Total: 1)

=== Button Statistics ===
Single Clicks: 2
Double Clicks: 1
Long Presses:  1
========================
```


## 调试技巧

### 1. 中断未触发

**可能原因**：

1. **GPIO时钟未使能**
   ```c
   // 检查是否使能了GPIO时钟
   __HAL_RCC_GPIOA_CLK_ENABLE();
   ```

2. **NVIC未使能**
   ```c
   // 检查NVIC配置
   HAL_NVIC_EnableIRQ(EXTI0_IRQn);
   ```

3. **中断标志未清除**
   ```c
   // 必须清除中断标志
   __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
   ```

4. **触发方式配置错误**
   ```c
   // 检查触发方式是否匹配实际信号
   GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;  // 上升沿
   ```

**调试方法**：

```c
// 在中断服务函数中翻转LED
void EXTI0_IRQHandler(void)
{
    // 立即翻转LED，确认中断是否触发
    HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
    
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        // 处理中断
    }
}
```

### 2. 中断频繁触发

**可能原因**：

1. **按键抖动**
   - 解决：添加软件或硬件防抖

2. **中断标志未清除**
   ```c
   // 错误：忘记清除标志
   void EXTI0_IRQHandler(void)
   {
       // 处理中断
       // 忘记清除标志，导致重复触发
   }
   
   // 正确：及时清除标志
   void EXTI0_IRQHandler(void)
   {
       if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
       {
           __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);  // 清除标志
           // 处理中断
       }
   }
   ```

3. **信号不稳定**
   - 检查硬件连接
   - 添加上拉/下拉电阻
   - 使用RC滤波

### 3. 使用逻辑分析仪调试

```c
// 在关键位置翻转调试引脚
#define DEBUG_PIN  GPIO_PIN_15
#define DEBUG_PORT GPIOD

void EXTI0_IRQHandler(void)
{
    HAL_GPIO_WritePin(DEBUG_PORT, DEBUG_PIN, GPIO_PIN_SET);  // 标记进入ISR
    
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 处理中断
        Button_Handler();
    }
    
    HAL_GPIO_WritePin(DEBUG_PORT, DEBUG_PIN, GPIO_PIN_RESET);  // 标记退出ISR
}
```

使用逻辑分析仪可以观察：
- 中断触发时机
- ISR执行时间
- 中断频率
- 信号抖动情况

### 4. 统计中断信息

```c
// 中断统计结构
typedef struct {
    uint32_t total_count;
    uint32_t max_interval_ms;
    uint32_t min_interval_ms;
    uint32_t last_trigger_time;
} InterruptStats_t;

InterruptStats_t irq_stats = {
    .total_count = 0,
    .max_interval_ms = 0,
    .min_interval_ms = 0xFFFFFFFF,
    .last_trigger_time = 0
};

void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        uint32_t current_time = HAL_GetTick();
        
        // 更新统计信息
        irq_stats.total_count++;
        
        if (irq_stats.last_trigger_time > 0)
        {
            uint32_t interval = current_time - irq_stats.last_trigger_time;
            
            if (interval > irq_stats.max_interval_ms)
                irq_stats.max_interval_ms = interval;
                
            if (interval < irq_stats.min_interval_ms)
                irq_stats.min_interval_ms = interval;
        }
        
        irq_stats.last_trigger_time = current_time;
        
        // 处理中断
        Button_Handler();
    }
}

// 打印统计信息
void Print_IRQ_Statistics(void)
{
    printf("=== Interrupt Statistics ===\n");
    printf("Total Count: %lu\n", irq_stats.total_count);
    printf("Max Interval: %lu ms\n", irq_stats.max_interval_ms);
    printf("Min Interval: %lu ms\n", irq_stats.min_interval_ms);
    printf("===========================\n");
}
```


## 最佳实践

### 1. ISR设计原则

**原则1：快速返回**

```c
// 不好的做法
void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 在ISR中执行耗时操作
    HAL_Delay(100);
    process_complex_data();
    printf("Long message...\n");
}

// 好的做法
volatile uint8_t button_flag = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 只设置标志，快速返回
    button_flag = 1;
}

void main_loop(void)
{
    if (button_flag)
    {
        button_flag = 0;
        // 在主循环中处理
        process_complex_data();
    }
}
```

**原则2：避免阻塞函数**

不要在ISR中使用：
- `HAL_Delay()`
- `printf()`（除非用于调试）
- `malloc()`/`free()`
- 长时间的循环

**原则3：使用volatile关键字**

```c
// ISR和主程序共享的变量必须使用volatile
volatile uint8_t button_pressed = 0;
volatile uint32_t button_count = 0;
```

### 2. 优先级配置建议

```c
// 按重要性和紧急程度配置优先级
void Configure_Interrupt_Priorities(void)
{
    // 设置优先级分组
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 紧急按键（如急停）- 最高优先级
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    
    // 重要传感器信号 - 高优先级
    HAL_NVIC_SetPriority(EXTI1_IRQn, 1, 0);
    
    // 普通按键 - 中等优先级
    HAL_NVIC_SetPriority(EXTI2_IRQn, 2, 0);
    
    // 低优先级事件
    HAL_NVIC_SetPriority(EXTI3_IRQn, 3, 0);
}
```

### 3. 防抖参数选择

| 应用场景 | 推荐防抖时间 | 说明 |
|---------|------------|------|
| 普通按键 | 20-50ms | 机械按键典型抖动时间 |
| 高质量按键 | 10-20ms | 抖动较小 |
| 旋转编码器 | 5-10ms | 需要快速响应 |
| 继电器 | 50-100ms | 抖动时间较长 |
| 传感器信号 | 根据实际测试 | 不同传感器差异大 |

### 4. 代码组织建议

```c
// button.h - 按键驱动头文件
#ifndef __BUTTON_H
#define __BUTTON_H

#include "stm32f4xx_hal.h"

// 按键事件类型
typedef enum {
    BUTTON_EVENT_NONE,
    BUTTON_EVENT_PRESSED,
    BUTTON_EVENT_RELEASED,
    BUTTON_EVENT_SINGLE_CLICK,
    BUTTON_EVENT_DOUBLE_CLICK,
    BUTTON_EVENT_LONG_PRESS
} ButtonEvent_t;

// 按键回调函数类型
typedef void (*ButtonCallback_t)(ButtonEvent_t event);

// 按键初始化
void Button_Init(GPIO_TypeDef* port, uint16_t pin, ButtonCallback_t callback);

// 按键处理（在主循环中调用）
void Button_Process(void);

// 获取按键事件
ButtonEvent_t Button_GetEvent(void);

#endif
```

```c
// button.c - 按键驱动实现
#include "button.h"

// 按键对象（可以扩展为数组支持多个按键）
static struct {
    GPIO_TypeDef* port;
    uint16_t pin;
    ButtonCallback_t callback;
    // ... 其他状态变量
} button;

void Button_Init(GPIO_TypeDef* port, uint16_t pin, ButtonCallback_t callback)
{
    button.port = port;
    button.pin = pin;
    button.callback = callback;
    
    // GPIO配置
    // NVIC配置
}

void Button_Process(void)
{
    // 状态机处理
    // 防抖处理
    // 事件检测
    
    if (button.callback && event_detected)
    {
        button.callback(event);
    }
}
```

```c
// main.c - 应用层
#include "button.h"

void Button_Event_Handler(ButtonEvent_t event)
{
    switch (event)
    {
        case BUTTON_EVENT_SINGLE_CLICK:
            // 处理单击
            break;
        case BUTTON_EVENT_DOUBLE_CLICK:
            // 处理双击
            break;
        case BUTTON_EVENT_LONG_PRESS:
            // 处理长按
            break;
        default:
            break;
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    // 初始化按键，注册回调函数
    Button_Init(GPIOA, GPIO_PIN_0, Button_Event_Handler);
    
    while (1)
    {
        Button_Process();
        // 其他任务
    }
}
```


## 常见问题

### Q1: 为什么按键按一次会触发多次中断？

**A**: 这是按键抖动导致的。机械按键在按下或释放时，触点会产生多次弹跳，每次弹跳都会触发中断。

**解决方案**：
1. 软件防抖：在中断后延时一段时间再检查按键状态
2. 硬件防抖：使用RC滤波电路或施密特触发器
3. 状态机防抖：使用状态机管理按键状态

参考本文"按键抖动问题"章节的详细实现。

### Q2: 同一个EXTI线可以连接多个GPIO引脚吗？

**A**: 不可以。每条EXTI线在同一时刻只能连接到一个GPIO端口的对应引脚。

例如：
- ✅ 可以：PA0使用EXTI0，PB1使用EXTI1
- ❌ 不可以：PA0和PB0同时使用EXTI0

如果需要多个按键，应该使用不同的引脚号，或者使用轮询方式检测其他按键。

### Q3: 上升沿触发和下降沿触发应该如何选择？

**A**: 选择依据：

**上升沿触发**：
- 按键接VCC，引脚配置下拉
- 检测信号从低到高的变化
- 适合检测按键按下

**下降沿触发**：
- 按键接GND，引脚配置上拉
- 检测信号从高到低的变化
- 适合检测按键释放

**双边沿触发**：
- 需要检测所有状态变化
- 适合编码器、频率测量等

**示例**：
```c
// 按键接VCC的配置
GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;   // 上升沿
GPIO_InitStruct.Pull = GPIO_PULLDOWN;         // 下拉

// 按键接GND的配置
GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿
GPIO_InitStruct.Pull = GPIO_PULLUP;           // 上拉
```

### Q4: 为什么必须清除中断标志？

**A**: 如果不清除中断标志，中断会持续触发。

**原理**：
1. 中断发生时，硬件自动设置挂起寄存器的标志位
2. CPU响应中断，执行ISR
3. 如果不清除标志位，退出ISR后会立即再次进入
4. 导致无限循环，系统卡死

**正确做法**：
```c
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0))
    {
        // 必须清除标志
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 处理中断
        Button_Handler();
    }
}
```

### Q5: 如何实现按键长按检测？

**A**: 有两种方法：

**方法1：在主循环中检测**（推荐）

```c
volatile uint8_t button_pressed = 0;
volatile uint32_t press_start_time = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_SET)
    {
        button_pressed = 1;
        press_start_time = HAL_GetTick();
    }
    else
    {
        button_pressed = 0;
    }
}

void main_loop(void)
{
    if (button_pressed)
    {
        uint32_t press_duration = HAL_GetTick() - press_start_time;
        if (press_duration >= 2000)  // 2秒
        {
            // 长按检测到
            Long_Press_Handler();
            button_pressed = 0;  // 防止重复触发
        }
    }
}
```

**方法2：使用定时器**

```c
void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_SET)
    {
        // 按键按下，启动定时器
        HAL_TIM_Base_Start_IT(&htim2);
    }
    else
    {
        // 按键释放，停止定时器
        HAL_TIM_Base_Stop_IT(&htim2);
    }
}

void TIM2_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE))
    {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 定时器溢出，说明长按时间到
        Long_Press_Handler();
        HAL_TIM_Base_Stop_IT(&htim2);
    }
}
```

### Q6: 中断优先级应该如何设置？

**A**: 优先级设置原则：

1. **按紧急程度**：
   - 安全相关（急停、故障）→ 最高优先级
   - 实时性要求高（通信、定时）→ 高优先级
   - 普通事件（按键、传感器）→ 中等优先级
   - 后台任务 → 低优先级

2. **按执行时间**：
   - 执行时间短的可以用高优先级
   - 执行时间长的应该用低优先级

3. **避免优先级反转**：
   - 不要让低优先级任务持有高优先级任务需要的资源

**示例**：
```c
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);

// 急停按键 - 最高优先级
HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);

// 通信中断 - 高优先级
HAL_NVIC_SetPriority(USART1_IRQn, 1, 0);

// 普通按键 - 中等优先级
HAL_NVIC_SetPriority(EXTI1_IRQn, 2, 0);

// 定时器 - 低优先级
HAL_NVIC_SetPriority(TIM2_IRQn, 3, 0);
```


## 性能优化

### 1. 减少中断延迟

**优化1：使用内联函数**

```c
// 将简单的处理函数声明为内联
static inline void Button_Quick_Handler(void)
{
    // 快速处理
    HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
}

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    Button_Quick_Handler();  // 内联，减少函数调用开销
}
```

**优化2：减少ISR中的代码量**

```c
// 不好的做法
void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 复杂的处理逻辑
    if (condition1) {
        // ...
    } else if (condition2) {
        // ...
    }
    // 更多代码...
}

// 好的做法
volatile uint8_t event_flag = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    event_flag = 1;  // 只设置标志
}

void main_loop(void)
{
    if (event_flag) {
        event_flag = 0;
        // 在主循环中处理复杂逻辑
        Complex_Handler();
    }
}
```

### 2. 降低中断频率

**方法1：硬件滤波**

使用RC滤波电路过滤高频噪声。

**方法2：软件限流**

```c
#define MIN_INTERVAL_MS  100  // 最小间隔时间

volatile uint32_t last_trigger_time = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    uint32_t current_time = HAL_GetTick();
    
    // 限制触发频率
    if ((current_time - last_trigger_time) >= MIN_INTERVAL_MS)
    {
        last_trigger_time = current_time;
        Button_Handler();
    }
}
```

### 3. 批量处理

对于高频中断，可以批量处理以减少开销。

```c
#define BUFFER_SIZE  16

volatile uint8_t event_buffer[BUFFER_SIZE];
volatile uint8_t write_index = 0;
volatile uint8_t read_index = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 将事件放入缓冲区
    event_buffer[write_index] = 1;
    write_index = (write_index + 1) % BUFFER_SIZE;
}

void main_loop(void)
{
    // 批量处理缓冲区中的事件
    while (read_index != write_index)
    {
        uint8_t event = event_buffer[read_index];
        read_index = (read_index + 1) % BUFFER_SIZE;
        
        Process_Event(event);
    }
}
```


## 总结

本教程详细介绍了外部中断的配置和使用方法，核心要点包括：

### 关键知识点

1. **EXTI系统架构**
   - 23条中断/事件线
   - EXTI0-15连接GPIO引脚
   - 同一EXTI线只能连接一个端口的对应引脚

2. **配置步骤**
   - 使能GPIO时钟
   - 配置GPIO为中断模式
   - 配置NVIC优先级
   - 编写中断服务函数

3. **触发方式**
   - 上升沿：低→高变化时触发
   - 下降沿：高→低变化时触发
   - 双边沿：任何变化都触发

4. **按键防抖**
   - 软件防抖：延时检测、状态机
   - 硬件防抖：RC滤波、施密特触发器
   - 推荐使用状态机方案

5. **最佳实践**
   - ISR应该快速返回
   - 避免在ISR中使用阻塞函数
   - 使用volatile关键字
   - 合理配置中断优先级
   - 及时清除中断标志

### 实践建议

1. **从简单开始**：先实现基本的按键中断，再逐步添加防抖和高级功能
2. **充分测试**：测试各种边界情况，如快速连续按键、长按等
3. **使用调试工具**：利用LED、串口、逻辑分析仪辅助调试
4. **代码模块化**：将按键驱动封装成独立模块，便于复用

### 下一步学习

掌握外部中断后，建议继续学习：
- [定时器中断实现精确延时](03-timer-interrupt.html) - 学习定时器中断
- [中断调试技巧与常见问题](04-interrupt-debugging.html) - 深入调试技巧
- [中断优先级配置与抢占机制](../intermediate/01-interrupt-priority.html) - 高级优先级管理

## 练习题

### 基础练习

1. **单按键控制LED**
   - 配置PA0为外部中断
   - 按键按下时翻转LED状态
   - 添加基本的延时防抖

2. **多按键系统**
   - 配置3个按键（PA0, PB1, PA2）
   - 每个按键控制不同的LED
   - 实现独立的中断处理

3. **按键计数器**
   - 统计按键按下次数
   - 通过串口输出计数值
   - 实现计数清零功能

### 进阶练习

4. **单击/双击检测**
   - 实现单击和双击识别
   - 单击翻转LED1，双击翻转LED2
   - 双击间隔时间可配置

5. **长按功能**
   - 检测按键长按（2秒）
   - 长按时LED闪烁
   - 释放后LED停止闪烁

6. **组合按键**
   - 实现两个按键的组合检测
   - 单独按键1：功能A
   - 单独按键2：功能B
   - 同时按下：功能C

### 挑战练习

7. **完整的按键驱动**
   - 支持单击、双击、长按、超长按
   - 可配置的防抖时间和长按时间
   - 回调函数机制
   - 支持多个按键实例

8. **旋转编码器**
   - 使用两个外部中断检测编码器
   - 识别旋转方向（顺时针/逆时针）
   - 计算旋转速度
   - 实现菜单导航功能

## 参考资料

1. **官方文档**
   - STM32F4xx Reference Manual - EXTI章节
   - STM32F4xx HAL Driver User Manual
   - ARM Cortex-M4 Generic User Guide

2. **应用笔记**
   - AN4013: STM32 Cross-series Timer Overview
   - AN4899: STM32 GPIO Configuration for Hardware Settings

3. **推荐阅读**
   - "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" by Joseph Yiu
   - "Mastering STM32" by Carmine Noviello

4. **在线资源**
   - STM32 Community Forum
   - Stack Overflow - STM32 Tag
   - GitHub - STM32 Example Projects

---

**恭喜你完成本教程！** 你现在已经掌握了外部中断的配置和使用方法。继续练习和实践，你将能够开发出更复杂的嵌入式应用。

**下一步**：建议学习 [定时器中断实现精确延时](03-timer-interrupt.html)，进一步提升中断系统的应用能力。

