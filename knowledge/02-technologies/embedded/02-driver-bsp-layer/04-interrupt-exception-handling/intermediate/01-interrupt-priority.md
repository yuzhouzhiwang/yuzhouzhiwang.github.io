---
title: "中断优先级配置与抢占机制"
description: "深入学习ARM Cortex-M系列微控制器的中断优先级配置方法和抢占机制，掌握NVIC优先级分组、抢占优先级与响应优先级的区别、中断嵌套的实现与控制，通过实战项目理解优先级设计原则"
slug: "interrupt-priority"

# 分类信息
domain: "驱动与BSP层"
module: "中断与异常处理"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 中断优先级
  - 抢占机制
  - NVIC配置
  - 中断嵌套
  - 优先级分组
prerequisites:
  - "interrupt-basics"
  - "external-interrupt"
related_contents:
  - "interrupt-vs-polling"
  - "interrupt-safety"

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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 中断优先级
  - NVIC配置
  - 抢占优先级
  - 响应优先级
  - 中断嵌套
cover_image: ""
---

# 中断优先级配置与抢占机制

## 概述

中断优先级管理是嵌入式系统设计的核心技能之一。合理的优先级配置可以确保系统的实时性和可靠性，而错误的配置可能导致系统响应延迟甚至死锁。本教程将深入讲解ARM Cortex-M系列微控制器的中断优先级机制。

完成本教程后，你将能够：

- 理解NVIC的优先级管理机制
- 掌握优先级分组的配置方法
- 区分抢占优先级和响应优先级
- 实现和控制中断嵌套
- 设计合理的优先级方案
- 调试优先级相关问题

## 学习目标

1. 深入理解NVIC优先级寄存器的工作原理
2. 掌握5种优先级分组模式的配置和应用
3. 理解抢占优先级和响应优先级的区别和作用
4. 实现多级中断嵌套并控制嵌套深度
5. 学会使用BASEPRI寄存器进行优先级屏蔽
6. 掌握优先级设计的最佳实践

## 前置要求

### 知识要求

- 理解中断的基本概念和工作流程
- 熟悉外部中断的配置方法
- 了解ARM Cortex-M架构基础
- 掌握C语言编程

### 硬件要求

- STM32开发板（F1/F4/F7系列均可）
- 3个LED灯
- 3个按键
- USB转串口模块（用于调试输出）
- 逻辑分析仪（可选，用于时序分析）

### 软件要求

- STM32CubeIDE或Keil MDK
- STM32 HAL库
- 串口终端软件（如PuTTY、Tera Term）

## 背景知识

### NVIC简介

NVIC（Nested Vectored Interrupt Controller，嵌套向量中断控制器）是ARM Cortex-M系列处理器的核心组件，负责管理所有的中断和异常。

**NVIC的主要特性**：

- 支持多达240个外部中断（具体数量取决于芯片）
- 可配置的优先级级别（8-256级）
- 支持中断嵌套
- 自动保存和恢复上下文
- 尾链优化（Tail-chaining）
- 延迟到达（Late-arriving）优化

### 优先级表示

ARM Cortex-M使用8位寄存器表示优先级，但实际实现的位数取决于具体芯片：

- **Cortex-M0/M0+**: 通常实现2位（4个优先级）
- **Cortex-M3/M4/M7**: 通常实现4位（16个优先级）
- **某些高端芯片**: 实现8位（256个优先级）

**重要概念**：
- 优先级数值越小，优先级越高
- 0是最高优先级
- 未使用的低位自动填充为0


### STM32的优先级实现

以STM32F4为例，使用4位表示优先级：

```
优先级寄存器（8位）：
┌─────────┬─────────┐
│ 7 6 5 4 │ 3 2 1 0 │
│ 实现位  │ 未实现  │
└─────────┴─────────┘
    ↓          ↓
  有效位    自动填0

实际优先级值：
0x00 = 0  (最高优先级)
0x10 = 1
0x20 = 2
...
0xF0 = 15 (最低优先级)
```

## 核心内容

### 1. 优先级分组

#### 1.1 分组概念

STM32将4位优先级分为两部分：
- **抢占优先级（Preemption Priority）**：决定是否可以中断当前ISR
- **响应优先级（Sub Priority）**：当抢占优先级相同时，决定响应顺序

**分组寄存器**：AIRCR（Application Interrupt and Reset Control Register）

```c
// AIRCR寄存器结构
SCB->AIRCR = (0x05FA << 16) |  // VECTKEY（写保护密钥）
             (priority_group);  // PRIGROUP（优先级分组）
```

#### 1.2 五种分组模式

STM32提供5种优先级分组模式：

| 分组 | PRIGROUP | 抢占优先级位数 | 响应优先级位数 | 抢占级别数 | 响应级别数 |
|------|----------|--------------|--------------|----------|----------|
| 0 | 0x07 | 0位 | 4位 | 1 | 16 |
| 1 | 0x06 | 1位 | 3位 | 2 | 8 |
| 2 | 0x05 | 2位 | 2位 | 4 | 4 |
| 3 | 0x04 | 3位 | 1位 | 8 | 2 |
| 4 | 0x03 | 4位 | 0位 | 16 | 1 |

**HAL库定义**：

```c
#define NVIC_PRIORITYGROUP_0   0x07  // 0位抢占，4位响应
#define NVIC_PRIORITYGROUP_1   0x06  // 1位抢占，3位响应
#define NVIC_PRIORITYGROUP_2   0x05  // 2位抢占，2位响应
#define NVIC_PRIORITYGROUP_3   0x04  // 3位抢占，1位响应
#define NVIC_PRIORITYGROUP_4   0x03  // 4位抢占，0位响应
```

#### 1.3 分组模式详解

**分组0（0位抢占，4位响应）**：

```
4位优先级：[响应3][响应2][响应1][响应0]

特点：
- 不支持中断嵌套（所有中断同级）
- 16个响应优先级
- 适合不需要嵌套的简单系统
```

**分组2（2位抢占，2位响应）**：

```
4位优先级：[抢占1][抢占0][响应1][响应0]

特点：
- 4个抢占优先级（0-3）
- 每个抢占级别有4个响应优先级（0-3）
- 平衡的配置，最常用
```

**分组4（4位抢占，0位响应）**：

```
4位优先级：[抢占3][抢占2][抢占1][抢占0]

特点：
- 16个抢占优先级
- 不区分响应优先级
- 适合需要多级嵌套的复杂系统
```

#### 1.4 配置优先级分组

```c
/**
 * @brief  配置NVIC优先级分组
 * @param  PriorityGroup: 优先级分组
 * @retval None
 */
void NVIC_Config(void)
{
    // 设置优先级分组为2（2位抢占，2位响应）
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 注意：整个系统只能设置一次优先级分组
    // 所有中断必须使用相同的分组方式
}
```

**重要提示**：
- 优先级分组是全局设置，影响所有中断
- 通常在系统初始化时设置一次
- 不要在运行时改变分组方式


### 2. 抢占优先级与响应优先级

#### 2.1 抢占优先级（Preemption Priority）

**定义**：决定一个中断是否可以打断另一个正在执行的中断服务程序。

**特性**：
- 数值越小，优先级越高
- 高抢占优先级可以打断低抢占优先级的ISR
- 产生中断嵌套

**示例**（分组2）：

```c
// 配置三个中断的抢占优先级
HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);  // 抢占优先级0（最高）
HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);   // 抢占优先级1
HAL_NVIC_SetPriority(USART1_IRQn, 2, 0); // 抢占优先级2（最低）

// 执行顺序示例：
// 1. USART1中断正在执行
// 2. TIM2中断发生 → 可以打断USART1（抢占优先级更高）
// 3. EXTI0中断发生 → 可以打断TIM2（抢占优先级更高）
```

**中断嵌套流程**：

```
主程序执行
    ↓
USART1_IRQHandler开始（抢占优先级2）
    ↓
TIM2中断发生（抢占优先级1）
    ↓
暂停USART1_IRQHandler
    ↓
TIM2_IRQHandler开始
    ↓
EXTI0中断发生（抢占优先级0）
    ↓
暂停TIM2_IRQHandler
    ↓
EXTI0_IRQHandler开始
    ↓
EXTI0_IRQHandler结束
    ↓
恢复TIM2_IRQHandler
    ↓
TIM2_IRQHandler结束
    ↓
恢复USART1_IRQHandler
    ↓
USART1_IRQHandler结束
    ↓
返回主程序
```

#### 2.2 响应优先级（Sub Priority）

**定义**：当多个中断同时发生且抢占优先级相同时，决定哪个中断先响应。

**特性**：
- 数值越小，优先级越高
- 不能产生中断嵌套
- 只影响响应顺序

**示例**（分组2）：

```c
// 配置三个中断，抢占优先级相同，响应优先级不同
HAL_NVIC_SetPriority(EXTI0_IRQn, 1, 0);  // 抢占1，响应0（最先响应）
HAL_NVIC_SetPriority(EXTI1_IRQn, 1, 1);  // 抢占1，响应1
HAL_NVIC_SetPriority(EXTI2_IRQn, 1, 2);  // 抢占1，响应2（最后响应）

// 如果三个中断同时发生：
// 1. EXTI0先响应（响应优先级最高）
// 2. EXTI0执行完后，EXTI1响应
// 3. EXTI1执行完后，EXTI2响应
// 注意：它们不会相互打断
```


#### 2.3 优先级判决规则

当多个中断同时发生时，NVIC按以下规则判决：

```
1. 比较抢占优先级
   ├─ 抢占优先级不同 → 抢占优先级高的先响应
   └─ 抢占优先级相同 → 进入步骤2

2. 比较响应优先级
   ├─ 响应优先级不同 → 响应优先级高的先响应
   └─ 响应优先级相同 → 进入步骤3

3. 比较中断号
   └─ 中断号小的先响应
```

**示例代码**：

```c
// 优先级配置（分组2）
void Priority_Config_Example(void)
{
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 中断A：抢占0，响应0
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    
    // 中断B：抢占0，响应1
    HAL_NVIC_SetPriority(EXTI1_IRQn, 0, 1);
    
    // 中断C：抢占1，响应0
    HAL_NVIC_SetPriority(EXTI2_IRQn, 1, 0);
    
    // 中断D：抢占1，响应1
    HAL_NVIC_SetPriority(EXTI3_IRQn, 1, 1);
    
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    HAL_NVIC_EnableIRQ(EXTI1_IRQn);
    HAL_NVIC_EnableIRQ(EXTI2_IRQn);
    HAL_NVIC_EnableIRQ(EXTI3_IRQn);
}

// 场景1：A和B同时发生
// 结果：A先响应（抢占相同，响应A更高）

// 场景2：C正在执行，A发生
// 结果：A打断C（抢占A更高）

// 场景3：A正在执行，B发生
// 结果：B等待A执行完（抢占相同，不能打断）

// 场景4：C和D同时发生
// 结果：C先响应（抢占相同，响应C更高）
```

### 3. 中断嵌套实现

#### 3.1 嵌套的条件

中断嵌套需要满足以下条件：

1. **抢占优先级不同**：新中断的抢占优先级必须高于当前ISR
2. **中断使能**：新中断必须被使能
3. **全局中断开启**：CPU的全局中断必须开启

#### 3.2 嵌套深度

**理论深度**：取决于抢占优先级的级别数
- 分组0：不支持嵌套（深度0）
- 分组1：最多2层嵌套
- 分组2：最多4层嵌套
- 分组3：最多8层嵌套
- 分组4：最多16层嵌套

**实际限制**：
- 栈空间限制
- 实时性要求
- 系统复杂度

**建议**：嵌套深度不超过3-4层


#### 3.3 嵌套示例代码

```c
#include "stm32f4xx_hal.h"
#include <stdio.h>

// 嵌套深度计数器
volatile uint32_t nest_depth = 0;
volatile uint32_t max_nest_depth = 0;

// 低优先级中断（抢占优先级2）
void TIM3_IRQHandler(void)
{
    nest_depth++;
    if (nest_depth > max_nest_depth) {
        max_nest_depth = nest_depth;
    }
    
    printf("[Depth %lu] TIM3 ISR Start (Preempt=2)\n", nest_depth);
    
    // 清除中断标志
    __HAL_TIM_CLEAR_FLAG(&htim3, TIM_FLAG_UPDATE);
    
    // 模拟较长的处理时间
    for (volatile uint32_t i = 0; i < 1000000; i++);
    
    printf("[Depth %lu] TIM3 ISR End\n", nest_depth);
    nest_depth--;
}

// 中等优先级中断（抢占优先级1）
void TIM2_IRQHandler(void)
{
    nest_depth++;
    if (nest_depth > max_nest_depth) {
        max_nest_depth = nest_depth;
    }
    
    printf("[Depth %lu] TIM2 ISR Start (Preempt=1) - Preempted TIM3\n", nest_depth);
    
    // 清除中断标志
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    
    // 模拟中等处理时间
    for (volatile uint32_t i = 0; i < 500000; i++);
    
    printf("[Depth %lu] TIM2 ISR End\n", nest_depth);
    nest_depth--;
}

// 高优先级中断（抢占优先级0）
void EXTI0_IRQHandler(void)
{
    nest_depth++;
    if (nest_depth > max_nest_depth) {
        max_nest_depth = nest_depth;
    }
    
    printf("[Depth %lu] EXTI0 ISR Start (Preempt=0) - Preempted All\n", nest_depth);
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 快速处理
    HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
    
    printf("[Depth %lu] EXTI0 ISR End\n", nest_depth);
    nest_depth--;
}

// 初始化函数
void Nested_Interrupt_Init(void)
{
    // 设置优先级分组为2
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 配置EXTI0：抢占0，响应0（最高优先级）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 配置TIM2：抢占1，响应0
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    
    // 配置TIM3：抢占2，响应0（最低优先级）
    HAL_NVIC_SetPriority(TIM3_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(TIM3_IRQn);
    
    printf("Nested Interrupt System Initialized\n");
    printf("Priority Group: 2 (2-bit preemption, 2-bit sub)\n");
    printf("EXTI0: Preempt=0, Sub=0\n");
    printf("TIM2:  Preempt=1, Sub=0\n");
    printf("TIM3:  Preempt=2, Sub=0\n\n");
}
```

**预期输出**：

```
Nested Interrupt System Initialized
Priority Group: 2 (2-bit preemption, 2-bit sub)
EXTI0: Preempt=0, Sub=0
TIM2:  Preempt=1, Sub=0
TIM3:  Preempt=2, Sub=0

[Depth 1] TIM3 ISR Start (Preempt=2)
[Depth 2] TIM2 ISR Start (Preempt=1) - Preempted TIM3
[Depth 3] EXTI0 ISR Start (Preempt=0) - Preempted All
[Depth 3] EXTI0 ISR End
[Depth 2] TIM2 ISR End
[Depth 1] TIM3 ISR End

Maximum Nesting Depth: 3
```


### 4. 优先级屏蔽

#### 4.1 BASEPRI寄存器

BASEPRI（Base Priority Register）可以屏蔽优先级低于某个值的所有中断。

**特性**：
- 只影响可配置优先级的中断
- 不影响NMI、HardFault等系统异常
- 可以在运行时动态修改

**寄存器值**：
- 0：不屏蔽任何中断（默认值）
- 非0：屏蔽优先级数值 ≥ BASEPRI的中断

#### 4.2 使用BASEPRI

```c
/**
 * @brief  设置BASEPRI寄存器
 * @param  priority: 优先级阈值（0-255）
 * @retval None
 */
void Set_BASEPRI(uint32_t priority)
{
    __set_BASEPRI(priority);
}

/**
 * @brief  获取BASEPRI寄存器值
 * @retval 当前BASEPRI值
 */
uint32_t Get_BASEPRI(void)
{
    return __get_BASEPRI();
}

// 示例：临界区保护
void Critical_Section_Example(void)
{
    uint32_t basepri_save;
    
    // 保存当前BASEPRI
    basepri_save = __get_BASEPRI();
    
    // 屏蔽优先级低于4的中断（4位系统中为0x40）
    __set_BASEPRI(0x40);
    
    // 临界区代码
    // 只有优先级0-3的中断可以打断
    critical_operation();
    
    // 恢复BASEPRI
    __set_BASEPRI(basepri_save);
}
```

#### 4.3 PRIMASK vs BASEPRI

| 特性 | PRIMASK | BASEPRI |
|------|---------|---------|
| 屏蔽范围 | 所有可屏蔽中断 | 优先级低于阈值的中断 |
| 粒度 | 全部或无 | 可选择性屏蔽 |
| 影响NMI | 否 | 否 |
| 影响HardFault | 否 | 否 |
| 使用场景 | 短临界区 | 需要保留高优先级中断 |

```c
// PRIMASK示例：屏蔽所有中断
void PRIMASK_Example(void)
{
    __disable_irq();  // 设置PRIMASK=1，屏蔽所有中断
    
    // 临界区代码
    critical_operation();
    
    __enable_irq();   // 清除PRIMASK，恢复中断
}

// BASEPRI示例：选择性屏蔽
void BASEPRI_Example(void)
{
    __set_BASEPRI(0x40);  // 屏蔽优先级4-15的中断
    
    // 临界区代码
    // 优先级0-3的中断仍然可以响应
    critical_operation();
    
    __set_BASEPRI(0);  // 恢复所有中断
}
```

### 5. 优先级设计原则

#### 5.1 设计步骤

1. **识别所有中断源**
   - 列出系统中所有的中断
   - 确定每个中断的功能

2. **分析实时性要求**
   - 确定哪些中断需要快速响应
   - 确定可接受的最大延迟

3. **确定嵌套需求**
   - 是否需要中断嵌套
   - 需要几层嵌套

4. **选择分组模式**
   - 根据嵌套需求选择分组
   - 平衡抢占级别和响应级别

5. **分配优先级**
   - 按重要性和紧急程度分配
   - 预留优先级空间


#### 5.2 优先级分配建议

**按功能分类**：

```
最高优先级（抢占0-1）：
- 安全相关：紧急停止、故障检测
- 硬实时：精确定时、关键控制

高优先级（抢占2-3）：
- 通信接口：UART、SPI、I2C
- 重要传感器：编码器、位置传感器

中等优先级（抢占4-7）：
- 定时器：周期任务
- ADC：数据采集
- 普通外设

低优先级（抢占8-15）：
- 后台任务：日志、统计
- 非紧急事件：按键、LED
```

**按执行时间分配**：

```
执行时间短（<10μs）：
- 可以使用高优先级
- 对系统影响小

执行时间中等（10-100μs）：
- 使用中等优先级
- 注意对其他中断的影响

执行时间长（>100μs）：
- 使用低优先级
- 考虑分解为多个步骤
- 使用标志位延迟处理
```

#### 5.3 常见错误

**错误1：所有中断使用相同优先级**

```c
// ❌ 错误做法
HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
HAL_NVIC_SetPriority(TIM2_IRQn, 2, 0);
HAL_NVIC_SetPriority(USART1_IRQn, 2, 0);

// 问题：无法保证重要中断的实时性
```

**错误2：高优先级中断执行时间过长**

```c
// ❌ 错误做法
void EXTI0_IRQHandler(void)  // 高优先级
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 长时间处理，阻塞其他中断
    for (int i = 0; i < 10000; i++) {
        complex_calculation();
    }
}

// ✅ 正确做法
volatile uint8_t data_ready = 0;

void EXTI0_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    data_ready = 1;  // 快速设置标志
}

void main_loop(void)
{
    if (data_ready) {
        data_ready = 0;
        // 在主循环中处理
        complex_calculation();
    }
}
```

**错误3：忽略优先级反转**

```c
// ❌ 可能导致优先级反转
// 高优先级任务等待低优先级任务持有的资源
// 中优先级任务抢占低优先级任务
// 结果：高优先级任务被中优先级任务间接阻塞

// ✅ 解决方案：
// 1. 使用优先级继承
// 2. 使用优先级天花板
// 3. 避免在ISR中等待资源
```

## 实践项目

### 项目：多优先级中断管理系统

实现一个完整的多优先级中断系统，包含紧急按键、定时任务和串口通信。

#### 项目需求

1. **紧急停止按键**（最高优先级）
   - 立即停止所有运动
   - 可以打断任何其他中断
   - LED1闪烁表示紧急状态

2. **定时控制任务**（中等优先级）
   - 每100ms执行一次
   - 控制LED2闪烁
   - 可以被紧急按键打断

3. **串口数据接收**（中等优先级）
   - 接收并处理串口数据
   - 与定时任务同级，不能相互打断
   - LED3表示数据接收

4. **状态显示**（低优先级）
   - 每1秒更新一次系统状态
   - 可以被所有其他中断打断


#### 完整代码实现

```c
#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>

// ==================== 全局变量 ====================

// 系统状态
typedef enum {
    SYS_STATE_NORMAL,
    SYS_STATE_EMERGENCY,
    SYS_STATE_PAUSED
} SystemState_t;

volatile SystemState_t system_state = SYS_STATE_NORMAL;

// 中断统计
typedef struct {
    uint32_t emergency_count;
    uint32_t timer_count;
    uint32_t uart_count;
    uint32_t status_count;
    uint32_t max_nest_depth;
} InterruptStats_t;

volatile InterruptStats_t irq_stats = {0};
volatile uint32_t nest_depth = 0;

// LED引脚定义
#define LED1_PIN  GPIO_PIN_12  // 紧急状态
#define LED2_PIN  GPIO_PIN_13  // 定时任务
#define LED3_PIN  GPIO_PIN_14  // 串口接收
#define LED_PORT  GPIOD

// 按键引脚定义
#define EMERGENCY_BTN_PIN  GPIO_PIN_0
#define EMERGENCY_BTN_PORT GPIOA

// ==================== 硬件初始化 ====================

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

void Emergency_Button_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = EMERGENCY_BTN_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    
    HAL_GPIO_Init(EMERGENCY_BTN_PORT, &GPIO_InitStruct);
}

// ==================== 优先级配置 ====================

void Priority_System_Init(void)
{
    // 设置优先级分组为2（2位抢占，2位响应）
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 紧急按键：抢占0，响应0（最高优先级）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 定时控制：抢占1，响应0
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    
    // 串口接收：抢占1，响应1（与定时同级，但响应优先级低）
    HAL_NVIC_SetPriority(USART1_IRQn, 1, 1);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
    
    // 状态显示：抢占2，响应0（最低优先级）
    HAL_NVIC_SetPriority(TIM3_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(TIM3_IRQn);
    
    printf("\n=== Priority System Initialized ===\n");
    printf("Priority Group: 2 (2-bit preemption, 2-bit sub)\n");
    printf("Emergency Button: Preempt=0, Sub=0 (Highest)\n");
    printf("Timer Control:    Preempt=1, Sub=0\n");
    printf("UART Receive:     Preempt=1, Sub=1\n");
    printf("Status Display:   Preempt=2, Sub=0 (Lowest)\n");
    printf("===================================\n\n");
}

// ==================== 中断服务函数 ====================

// 1. 紧急停止按键（最高优先级）
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(EMERGENCY_BTN_PIN))
    {
        __HAL_GPIO_EXTI_CLEAR_IT(EMERGENCY_BTN_PIN);
        
        nest_depth++;
        if (nest_depth > irq_stats.max_nest_depth) {
            irq_stats.max_nest_depth = nest_depth;
        }
        
        // 紧急处理
        system_state = SYS_STATE_EMERGENCY;
        irq_stats.emergency_count++;
        
        // LED1快速闪烁表示紧急状态
        for (int i = 0; i < 5; i++) {
            HAL_GPIO_TogglePin(LED_PORT, LED1_PIN);
            for (volatile uint32_t j = 0; j < 100000; j++);
        }
        
        printf("[Depth %lu] EMERGENCY! Count: %lu\n", 
               nest_depth, irq_stats.emergency_count);
        
        nest_depth--;
    }
}

// 2. 定时控制任务（中等优先级）
void TIM2_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE))
    {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        nest_depth++;
        if (nest_depth > irq_stats.max_nest_depth) {
            irq_stats.max_nest_depth = nest_depth;
        }
        
        irq_stats.timer_count++;
        
        // 只在正常状态下执行
        if (system_state == SYS_STATE_NORMAL) {
            HAL_GPIO_TogglePin(LED_PORT, LED2_PIN);
        }
        
        // 每100次打印一次
        if (irq_stats.timer_count % 100 == 0) {
            printf("[Depth %lu] Timer: %lu\n", 
                   nest_depth, irq_stats.timer_count);
        }
        
        nest_depth--;
    }
}

// 3. 串口数据接收（中等优先级）
void USART1_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE))
    {
        nest_depth++;
        if (nest_depth > irq_stats.max_nest_depth) {
            irq_stats.max_nest_depth = nest_depth;
        }
        
        irq_stats.uart_count++;
        
        // 读取数据
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        
        // LED3闪烁表示接收
        HAL_GPIO_TogglePin(LED_PORT, LED3_PIN);
        
        // 处理命令
        if (data == 'R' || data == 'r') {
            system_state = SYS_STATE_NORMAL;
            printf("[Depth %lu] UART: Resume command received\n", nest_depth);
        }
        
        nest_depth--;
    }
}

// 4. 状态显示（最低优先级）
void TIM3_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim3, TIM_FLAG_UPDATE))
    {
        __HAL_TIM_CLEAR_FLAG(&htim3, TIM_FLAG_UPDATE);
        
        nest_depth++;
        if (nest_depth > irq_stats.max_nest_depth) {
            irq_stats.max_nest_depth = nest_depth;
        }
        
        irq_stats.status_count++;
        
        // 打印系统状态
        printf("\n[Depth %lu] === System Status ===\n", nest_depth);
        printf("State: %s\n", 
               system_state == SYS_STATE_NORMAL ? "NORMAL" :
               system_state == SYS_STATE_EMERGENCY ? "EMERGENCY" : "PAUSED");
        printf("Emergency: %lu, Timer: %lu, UART: %lu\n",
               irq_stats.emergency_count,
               irq_stats.timer_count,
               irq_stats.uart_count);
        printf("Max Nesting Depth: %lu\n", irq_stats.max_nest_depth);
        printf("====================\n\n");
        
        nest_depth--;
    }
}

// ==================== 主程序 ====================

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    
    // 初始化硬件
    LED_Init();
    Emergency_Button_Init();
    UART_Init();
    Timer_Init();
    
    // 配置优先级系统
    Priority_System_Init();
    
    printf("Multi-Priority Interrupt System Started\n");
    printf("Press emergency button to trigger highest priority interrupt\n");
    printf("Send 'R' via UART to resume normal operation\n\n");
    
    while (1)
    {
        // 主循环可以执行低优先级任务
        HAL_Delay(1000);
    }
}
```


#### 项目测试

**测试步骤**：

1. **正常运行测试**
   - 观察LED2每100ms闪烁一次
   - 每1秒打印系统状态
   - 验证定时任务正常执行

2. **紧急中断测试**
   - 按下紧急按键
   - 观察LED1快速闪烁
   - 验证可以打断定时任务
   - 检查嵌套深度

3. **串口通信测试**
   - 发送数据到串口
   - 观察LED3闪烁
   - 验证与定时任务的响应顺序

4. **嵌套测试**
   - 在定时任务执行时按紧急按键
   - 观察中断嵌套情况
   - 检查最大嵌套深度

**预期输出**：

```
=== Priority System Initialized ===
Priority Group: 2 (2-bit preemption, 2-bit sub)
Emergency Button: Preempt=0, Sub=0 (Highest)
Timer Control:    Preempt=1, Sub=0
UART Receive:     Preempt=1, Sub=1
Status Display:   Preempt=2, Sub=0 (Lowest)
===================================

Multi-Priority Interrupt System Started
Press emergency button to trigger highest priority interrupt
Send 'R' via UART to resume normal operation

[Depth 1] Timer: 100
[Depth 1] Timer: 200

[Depth 1] === System Status ===
State: NORMAL
Emergency: 0, Timer: 250, UART: 0
Max Nesting Depth: 1
====================

[Depth 1] Timer: 300
[Depth 2] EMERGENCY! Count: 1
[Depth 1] Timer: 400

[Depth 1] === System Status ===
State: EMERGENCY
Emergency: 1, Timer: 450, UART: 0
Max Nesting Depth: 2
====================

[Depth 1] UART: Resume command received
[Depth 1] Timer: 500
```

## 调试技巧

### 1. 使用嵌套深度计数器

```c
volatile uint32_t nest_depth = 0;
volatile uint32_t max_nest_depth = 0;

void Any_IRQHandler(void)
{
    nest_depth++;
    if (nest_depth > max_nest_depth) {
        max_nest_depth = nest_depth;
    }
    
    // 中断处理代码
    
    nest_depth--;
}

// 在主循环中监控
void main_loop(void)
{
    printf("Max nesting depth: %lu\n", max_nest_depth);
}
```

### 2. 使用GPIO标记中断

```c
#define DEBUG_PIN1  GPIO_PIN_8   // 标记中断1
#define DEBUG_PIN2  GPIO_PIN_9   // 标记中断2
#define DEBUG_PIN3  GPIO_PIN_10  // 标记中断3

void IRQ1_Handler(void)
{
    HAL_GPIO_WritePin(GPIOD, DEBUG_PIN1, GPIO_PIN_SET);
    
    // 中断处理
    
    HAL_GPIO_WritePin(GPIOD, DEBUG_PIN1, GPIO_PIN_RESET);
}

// 使用逻辑分析仪观察：
// - 中断触发时机
// - 中断执行时间
// - 中断嵌套关系
```

### 3. 优先级冲突检测

```c
void Check_Priority_Conflicts(void)
{
    uint32_t priority1, priority2;
    
    // 读取两个中断的优先级
    priority1 = NVIC_GetPriority(EXTI0_IRQn);
    priority2 = NVIC_GetPriority(EXTI1_IRQn);
    
    if (priority1 == priority2) {
        printf("Warning: EXTI0 and EXTI1 have same priority!\n");
        printf("Priority: 0x%02lX\n", priority1);
    }
}
```

### 4. 中断延迟测量

```c
volatile uint32_t irq_trigger_time = 0;
volatile uint32_t irq_response_time = 0;
volatile uint32_t irq_latency = 0;

void Trigger_Interrupt(void)
{
    irq_trigger_time = DWT->CYCCNT;  // 使用DWT计数器
    // 触发中断
}

void IRQHandler(void)
{
    irq_response_time = DWT->CYCCNT;
    irq_latency = irq_response_time - irq_trigger_time;
    
    // 中断处理
}

// 打印延迟（以时钟周期为单位）
printf("Interrupt latency: %lu cycles\n", irq_latency);
```


## 深入理解

### 优先级位的实际含义

在4位优先级系统中（如STM32F4），优先级寄存器的高4位有效：

```
8位寄存器：[7][6][5][4][3][2][1][0]
           └─有效位─┘ └─填充0─┘

分组2示例（2位抢占，2位响应）：
[7][6] = 抢占优先级
[5][4] = 响应优先级
[3-0] = 自动填0

优先级值计算：
抢占=1, 响应=2 → 0b01_10_0000 = 0x60
```

### 中断延迟的组成

```
总延迟 = 硬件延迟 + 软件延迟 + 等待延迟

硬件延迟：
- 中断信号同步：1-2个时钟周期
- 中断识别：1-2个时钟周期

软件延迟：
- 保存上下文：12个时钟周期（自动）
- 跳转到ISR：2-3个时钟周期

等待延迟：
- 当前指令完成：0-N个时钟周期
- 高优先级中断执行：0-N个时钟周期
- 临界区屏蔽：0-N个时钟周期
```

### 尾链优化（Tail-chaining）

当一个ISR结束时，如果有另一个待处理的中断，处理器可以直接跳转而不需要恢复和重新保存上下文。

```
传统方式：
ISR1结束 → 恢复上下文(12周期) → 保存上下文(12周期) → ISR2开始
总开销：24个时钟周期

尾链优化：
ISR1结束 → 直接跳转(6周期) → ISR2开始
总开销：6个时钟周期

节省：18个时钟周期（75%）
```

### 延迟到达优化（Late-arriving）

如果在保存上下文期间，有更高优先级的中断到达，处理器会：
1. 完成当前的上下文保存
2. 直接跳转到高优先级ISR
3. 避免重复保存上下文

```
无优化：
开始保存上下文 → 完成保存 → 执行低优先级ISR → 
高优先级中断到达 → 保存上下文 → 执行高优先级ISR

有优化：
开始保存上下文 → 高优先级中断到达 → 完成保存 → 
直接执行高优先级ISR
```

## 最佳实践

### 1. 优先级分配策略

```c
// 推荐的优先级分配方案（分组2）

// 抢占优先级0：紧急和安全相关
#define PRIORITY_EMERGENCY    0, 0  // 紧急停止
#define PRIORITY_FAULT        0, 1  // 故障检测

// 抢占优先级1：硬实时任务
#define PRIORITY_ENCODER      1, 0  // 编码器
#define PRIORITY_PWM          1, 1  // PWM控制

// 抢占优先级2：通信和数据采集
#define PRIORITY_UART         2, 0  // 串口
#define PRIORITY_ADC          2, 1  // ADC
#define PRIORITY_TIMER        2, 2  // 定时器

// 抢占优先级3：低优先级任务
#define PRIORITY_BUTTON       3, 0  // 按键
#define PRIORITY_LED          3, 1  // LED
#define PRIORITY_LOG          3, 2  // 日志

// 使用示例
HAL_NVIC_SetPriority(EXTI0_IRQn, PRIORITY_EMERGENCY);
HAL_NVIC_SetPriority(TIM1_IRQn, PRIORITY_PWM);
```

### 2. ISR设计原则

```c
// ✅ 好的ISR设计
void GOOD_IRQHandler(void)
{
    // 1. 快速清除标志
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    
    // 2. 最小化处理
    flag = 1;
    counter++;
    
    // 3. 快速返回
}

// ❌ 不好的ISR设计
void BAD_IRQHandler(void)
{
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    
    // ❌ 长时间循环
    for (int i = 0; i < 10000; i++) {
        process_data();
    }
    
    // ❌ 阻塞函数
    HAL_Delay(100);
    
    // ❌ 复杂计算
    float result = sqrt(complex_calculation());
}
```

### 3. 临界区保护

```c
// 方法1：使用PRIMASK（短临界区）
void Short_Critical_Section(void)
{
    __disable_irq();
    
    // 临界区代码（<10μs）
    shared_variable++;
    
    __enable_irq();
}

// 方法2：使用BASEPRI（保留高优先级中断）
void Selective_Critical_Section(void)
{
    uint32_t basepri_save = __get_BASEPRI();
    __set_BASEPRI(0x40);  // 屏蔽优先级4-15
    
    // 临界区代码
    // 优先级0-3的中断仍可响应
    shared_data_operation();
    
    __set_BASEPRI(basepri_save);
}

// 方法3：使用互斥锁（RTOS环境）
void RTOS_Critical_Section(void)
{
    osMutexAcquire(mutex_id, osWaitForever);
    
    // 临界区代码
    shared_resource_access();
    
    osMutexRelease(mutex_id);
}
```

### 4. 避免优先级反转

```c
// 场景：优先级反转问题
// 高优先级任务等待低优先级任务持有的资源
// 中优先级任务抢占低优先级任务
// 结果：高优先级任务被间接阻塞

// 解决方案1：优先级继承
// 当高优先级任务等待资源时，
// 临时提升持有资源的低优先级任务的优先级

// 解决方案2：优先级天花板
// 持有资源的任务自动获得最高优先级

// 解决方案3：避免在ISR中等待
void High_Priority_ISR(void)
{
    // ❌ 不要在ISR中等待资源
    // wait_for_resource();
    
    // ✅ 使用标志位，在主循环中处理
    resource_needed = 1;
}
```


## 常见问题

### Q1: 如何选择合适的优先级分组？

**A**: 根据系统需求选择：

**分组0（0位抢占，4位响应）**：
- 适合：不需要中断嵌套的简单系统
- 优点：16个响应级别，配置灵活
- 缺点：无法实现中断嵌套

**分组2（2位抢占，2位响应）**：
- 适合：大多数应用（推荐）
- 优点：平衡的配置，4级嵌套，每级4个响应优先级
- 缺点：嵌套级别有限

**分组4（4位抢占，0位响应）**：
- 适合：需要多级嵌套的复杂系统
- 优点：16级嵌套
- 缺点：同级中断无法区分响应顺序

**选择建议**：
- 简单系统：分组0或1
- 一般系统：分组2（最常用）
- 复杂系统：分组3或4

### Q2: 抢占优先级和响应优先级有什么区别？

**A**: 核心区别：

| 特性 | 抢占优先级 | 响应优先级 |
|------|----------|----------|
| 作用 | 决定是否可以打断 | 决定响应顺序 |
| 嵌套 | 可以产生嵌套 | 不能产生嵌套 |
| 比较时机 | ISR执行期间 | 中断同时发生时 |
| 影响范围 | 所有中断 | 同抢占级别的中断 |

**示例**：

```c
// 配置（分组2）
HAL_NVIC_SetPriority(EXTI0_IRQn, 1, 0);  // 抢占1，响应0
HAL_NVIC_SetPriority(EXTI1_IRQn, 1, 1);  // 抢占1，响应1
HAL_NVIC_SetPriority(EXTI2_IRQn, 0, 0);  // 抢占0，响应0

// 场景1：EXTI0正在执行，EXTI1发生
// 结果：EXTI1等待（抢占相同，不能打断）

// 场景2：EXTI0正在执行，EXTI2发生
// 结果：EXTI2打断EXTI0（抢占更高）

// 场景3：EXTI0和EXTI1同时发生
// 结果：EXTI0先响应（响应优先级更高）
```

### Q3: 为什么中断嵌套深度不宜过深？

**A**: 主要原因：

1. **栈空间消耗**
   ```
   每次嵌套需要保存上下文：
   - 8个寄存器 × 4字节 = 32字节
   - 嵌套3层 = 96字节
   - 嵌套10层 = 320字节
   
   可能导致栈溢出！
   ```

2. **实时性下降**
   ```
   嵌套越深，低优先级中断等待时间越长
   可能导致中断丢失或响应超时
   ```

3. **系统复杂度增加**
   ```
   难以分析和调试
   容易出现优先级反转
   增加死锁风险
   ```

**建议**：
- 嵌套深度不超过3-4层
- 高优先级ISR尽可能短
- 使用标志位延迟处理

### Q4: 如何避免优先级配置错误？

**A**: 最佳实践：

1. **集中管理优先级**
   ```c
   // priority_config.h
   #define PRIORITY_EMERGENCY    0, 0
   #define PRIORITY_TIMER        1, 0
   #define PRIORITY_UART         1, 1
   #define PRIORITY_BUTTON       2, 0
   
   // 使用时
   HAL_NVIC_SetPriority(EXTI0_IRQn, PRIORITY_EMERGENCY);
   ```

2. **文档化优先级方案**
   ```c
   /**
    * 优先级分配方案（分组2）
    * 
    * 抢占0：紧急和安全
    *   - EXTI0: 紧急停止 (0,0)
    * 
    * 抢占1：实时控制
    *   - TIM2: 定时控制 (1,0)
    *   - UART1: 串口通信 (1,1)
    * 
    * 抢占2：低优先级
    *   - TIM3: 状态显示 (2,0)
    */
   ```

3. **运行时检查**
   ```c
   void Verify_Priority_Config(void)
   {
       uint32_t p1 = NVIC_GetPriority(EXTI0_IRQn);
       uint32_t p2 = NVIC_GetPriority(TIM2_IRQn);
       
       if (p1 >= p2) {
           printf("ERROR: EXTI0 priority should be higher than TIM2!\n");
       }
   }
   ```

### Q5: BASEPRI和PRIMASK应该如何选择？

**A**: 选择依据：

**使用PRIMASK的场景**：
- 临界区非常短（<10μs）
- 需要完全禁止中断
- 不需要保留任何中断

```c
void Use_PRIMASK(void)
{
    __disable_irq();
    
    // 极短的临界区
    counter++;
    
    __enable_irq();
}
```

**使用BASEPRI的场景**：
- 临界区较长
- 需要保留高优先级中断
- 需要选择性屏蔽

```c
void Use_BASEPRI(void)
{
    __set_BASEPRI(0x40);  // 屏蔽优先级4-15
    
    // 较长的临界区
    // 优先级0-3的中断仍可响应
    complex_operation();
    
    __set_BASEPRI(0);
}
```

**对比表**：

| 特性 | PRIMASK | BASEPRI |
|------|---------|---------|
| 屏蔽范围 | 所有可屏蔽中断 | 选择性屏蔽 |
| 实时性 | 影响所有中断 | 保留高优先级 |
| 使用场景 | 短临界区 | 长临界区 |
| 复杂度 | 简单 | 稍复杂 |

## 总结

本教程深入讲解了ARM Cortex-M系列微控制器的中断优先级配置和抢占机制，核心要点包括：

1. **NVIC优先级管理**
   - 使用4位表示优先级（STM32F4）
   - 数值越小，优先级越高
   - 支持5种优先级分组模式

2. **优先级分组**
   - 分为抢占优先级和响应优先级
   - 分组2（2位抢占，2位响应）最常用
   - 全局设置，影响所有中断

3. **抢占优先级**
   - 决定是否可以打断当前ISR
   - 产生中断嵌套
   - 高抢占优先级可以打断低抢占优先级

4. **响应优先级**
   - 决定同时发生时的响应顺序
   - 不能产生中断嵌套
   - 只在抢占优先级相同时有效

5. **中断嵌套**
   - 需要抢占优先级不同
   - 建议嵌套深度不超过3-4层
   - 注意栈空间消耗

6. **优先级屏蔽**
   - PRIMASK：屏蔽所有可屏蔽中断
   - BASEPRI：选择性屏蔽低优先级中断
   - 用于临界区保护

7. **设计原则**
   - 按重要性和紧急程度分配优先级
   - 高优先级ISR应该尽可能短
   - 避免优先级反转
   - 预留优先级空间

掌握这些知识后，你就可以设计出高效、可靠的中断优先级方案，确保系统的实时性和稳定性。

## 延伸阅读

- [中断与轮询的选择策略](02-interrupt-vs-polling.html) - 学习何时使用中断
- [中断安全与临界区保护](03-interrupt-safety.html) - 深入理解临界区
- [中断性能优化与延迟分析](../advanced/01-interrupt-optimization.html) - 优化中断性能

## 参考资料

1. ARM Cortex-M4 Technical Reference Manual - ARM官方文档
2. STM32F4xx Reference Manual - ST官方参考手册
3. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" by Joseph Yiu
4. ARM Application Note: Cortex-M Programming Guide to Memory Barrier Instructions

---

**练习题**：

1. 在分组2的配置下，如果有4个中断的优先级分别为(0,0)、(0,1)、(1,0)、(1,1)，当它们同时发生时，响应顺序是什么？

2. 编写一个程序，配置3个不同优先级的中断，并演示中断嵌套的效果。要求打印嵌套深度和执行顺序。

3. 设计一个电机控制系统的优先级方案，包含：紧急停止、位置控制、速度采样、串口通信、状态显示。

4. 解释为什么在ISR中不应该使用HAL_Delay()函数，并提供替代方案。

5. 实现一个使用BASEPRI的临界区保护函数，要求保留优先级0-2的中断响应能力。

**下一步**：建议学习 [中断与轮询的选择策略](02-interrupt-vs-polling.html)，了解何时使用中断，何时使用轮询。

