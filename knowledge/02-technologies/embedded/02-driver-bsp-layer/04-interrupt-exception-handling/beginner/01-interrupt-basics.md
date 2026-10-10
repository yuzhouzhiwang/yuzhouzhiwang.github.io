---
title: "中断系统基础概念"
description: "全面介绍嵌入式系统的中断机制基础知识，包括中断原理、中断类型、中断向量、优先级管理和中断嵌套，帮助初学者建立完整的中断系统概念体系"
slug: "interrupt-basics"

# 分类信息
domain: "驱动与BSP层"
module: "中断与异常处理"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 中断系统
  - 中断原理
  - NVIC
  - 中断优先级
  - 中断向量
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 35
difficulty_score: 2

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
  - 中断系统
  - 中断处理
  - NVIC
  - 中断优先级
  - 嵌入式中断
cover_image: ""
---

# 中断系统基础概念

## 概述

中断是嵌入式系统中最重要的机制之一，它允许处理器响应外部事件而暂停当前任务，转而执行特定的处理程序。理解中断机制是掌握嵌入式系统开发的关键。完成本文学习后，你将能够：

- 理解中断的基本概念和工作原理
- 掌握不同类型的中断及其应用场景
- 了解中断向量表的组织和作用
- 理解中断优先级的配置和管理
- 认识中断嵌套的机制和注意事项

## 背景知识

### 为什么需要中断？

在没有中断的系统中，处理器需要不断轮询（polling）来检查外部事件是否发生。这种方式存在明显的缺点：

- **效率低下**：处理器大量时间浪费在轮询上
- **响应延迟**：事件发生到被检测到之间有延迟
- **资源浪费**：无法充分利用处理器性能

中断机制解决了这些问题：
- **事件驱动**：事件发生时主动通知处理器
- **快速响应**：可以在微秒级别响应事件
- **高效利用**：处理器可以执行其他任务

### 中断与轮询的对比

```c
// 轮询方式 - 效率低
void polling_example(void) {
    while(1) {
        if (button_pressed()) {  // 不断检查
            handle_button();
        }
        // 大量CPU时间浪费在检查上
    }
}

// 中断方式 - 高效
void interrupt_example(void) {
    enable_button_interrupt();  // 配置中断
    
    while(1) {
        // CPU可以执行其他任务
        do_other_work();
    }
}

// 中断服务函数 - 事件发生时自动调用
void EXTI_IRQHandler(void) {
    if (button_interrupt_flag()) {
        handle_button();
        clear_interrupt_flag();
    }
}
```

## 核心内容

### 1. 中断的基本原理

#### 1.1 中断处理流程

中断处理包含以下几个关键步骤：

```
事件发生 → 中断请求 → 保存现场 → 执行ISR → 恢复现场 → 返回主程序
```

**详细流程**：

1. **事件发生**：外部设备或内部事件触发中断信号
2. **中断请求**：中断控制器接收中断请求
3. **中断判决**：检查中断使能和优先级
4. **保存现场**：自动保存当前执行状态（寄存器）
5. **执行ISR**：跳转到中断服务程序执行
6. **恢复现场**：恢复之前保存的状态
7. **返回主程序**：继续执行被中断的程序


#### 1.2 中断延迟

中断延迟是从中断请求发生到中断服务程序开始执行的时间。

**延迟组成**：
- **硬件延迟**：中断信号传播和识别时间（几个时钟周期）
- **软件延迟**：保存现场和跳转时间（10-20个时钟周期）
- **等待延迟**：如果有更高优先级中断正在执行

```
典型的ARM Cortex-M3中断延迟：
- 最小延迟：12个时钟周期
- 典型延迟：15-20个时钟周期
- 在72MHz系统中约为200-300ns
```

### 2. 中断类型

#### 2.1 按来源分类

**外部中断（External Interrupt）**：
- 来自外部设备或引脚
- 例如：按键、传感器、通信接口

**内部中断（Internal Interrupt）**：
- 来自内部外设
- 例如：定时器、ADC、DMA

**软件中断（Software Interrupt）**：
- 由软件指令触发
- 例如：系统调用、调试断点

#### 2.2 按触发方式分类

**电平触发（Level-triggered）**：
- 高电平触发或低电平触发
- 只要电平保持，中断请求就存在
- 需要在ISR中清除中断源

**边沿触发（Edge-triggered）**：
- 上升沿触发或下降沿触发
- 只在电平变化时产生中断请求
- 可能丢失快速连续的事件

```c
// 配置外部中断触发方式
void EXTI_Config(void) {
    EXTI_InitTypeDef EXTI_InitStruct = {0};
    
    EXTI_InitStruct.Line = EXTI_LINE_0;
    EXTI_InitStruct.Mode = EXTI_MODE_INTERRUPT;
    
    // 选择触发方式
    EXTI_InitStruct.Trigger = EXTI_TRIGGER_RISING;   // 上升沿触发
    // EXTI_InitStruct.Trigger = EXTI_TRIGGER_FALLING; // 下降沿触发
    // EXTI_InitStruct.Trigger = EXTI_TRIGGER_BOTH;    // 双边沿触发
    
    HAL_EXTI_SetConfigLine(&hexti, &EXTI_InitStruct);
}
```

### 3. 中断向量表

#### 3.1 向量表的概念

中断向量表是一个存储中断服务程序入口地址的数组，每个中断源对应一个向量。

**ARM Cortex-M的向量表结构**：

```
地址偏移    中断源              说明
0x0000      初始栈指针          系统启动时的栈顶地址
0x0004      Reset_Handler       复位中断
0x0008      NMI_Handler         不可屏蔽中断
0x000C      HardFault_Handler   硬件错误
0x0010      MemManage_Handler   内存管理错误
0x0014      BusFault_Handler    总线错误
0x0018      UsageFault_Handler  使用错误
0x001C-0x002C  保留
0x0030      SVC_Handler         系统服务调用
0x0034      DebugMon_Handler    调试监视器
0x0038      保留
0x003C      PendSV_Handler      可挂起的系统调用
0x0040      SysTick_Handler     系统滴答定时器
0x0044+     外部中断0-N         外设中断
```


#### 3.2 向量表定义示例

```c
// 启动文件中的向量表定义（startup_stm32f4xx.s）
__attribute__((section(".isr_vector")))
const uint32_t vector_table[] = {
    (uint32_t)&_estack,              // 初始栈指针
    (uint32_t)Reset_Handler,         // 复位处理
    (uint32_t)NMI_Handler,           // NMI处理
    (uint32_t)HardFault_Handler,     // 硬件错误处理
    (uint32_t)MemManage_Handler,     // 内存管理错误
    (uint32_t)BusFault_Handler,      // 总线错误
    (uint32_t)UsageFault_Handler,    // 使用错误
    0,                                // 保留
    0,                                // 保留
    0,                                // 保留
    0,                                // 保留
    (uint32_t)SVC_Handler,           // SVC处理
    (uint32_t)DebugMon_Handler,      // 调试监视器
    0,                                // 保留
    (uint32_t)PendSV_Handler,        // PendSV处理
    (uint32_t)SysTick_Handler,       // SysTick处理
    
    // 外部中断
    (uint32_t)WWDG_IRQHandler,       // 窗口看门狗
    (uint32_t)PVD_IRQHandler,        // PVD
    (uint32_t)TAMP_STAMP_IRQHandler, // 时间戳
    // ... 更多外部中断
};
```

#### 3.3 向量表重定位

在某些应用中（如Bootloader），需要重定位向量表：

```c
// 重定位向量表到RAM
#define VECT_TAB_SRAM
#define VECT_TAB_OFFSET  0x00000000

void SystemInit(void) {
    #ifdef VECT_TAB_SRAM
        // 向量表在SRAM中
        SCB->VTOR = SRAM_BASE | VECT_TAB_OFFSET;
    #else
        // 向量表在Flash中
        SCB->VTOR = FLASH_BASE | VECT_TAB_OFFSET;
    #endif
}
```

### 4. 中断优先级

#### 4.1 NVIC（嵌套向量中断控制器）

ARM Cortex-M系列使用NVIC来管理中断，提供灵活的优先级配置。

**NVIC的主要特性**：
- 支持多达240个外部中断
- 可配置的优先级级别（8-256级）
- 支持中断嵌套
- 自动保存和恢复上下文
- 尾链优化（Tail-chaining）

#### 4.2 优先级分组

STM32使用4位来表示优先级，可以分为抢占优先级和响应优先级。

**优先级分组方式**：

```c
// NVIC优先级分组
#define NVIC_PRIORITYGROUP_0   0x7  // 0位抢占，4位响应
#define NVIC_PRIORITYGROUP_1   0x6  // 1位抢占，3位响应
#define NVIC_PRIORITYGROUP_2   0x5  // 2位抢占，2位响应
#define NVIC_PRIORITYGROUP_3   0x4  // 3位抢占，1位响应
#define NVIC_PRIORITYGROUP_4   0x3  // 4位抢占，0位响应

// 配置优先级分组
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
```

**优先级分组示例（分组2）**：

```
4位优先级 = 2位抢占 + 2位响应

抢占优先级  响应优先级  说明
    0          0       最高优先级
    0          1       
    0          2       
    0          3       
    1          0       
    1          1       
    1          2       
    1          3       
    2          0       
    2          1       
    2          2       
    2          3       
    3          0       
    3          1       
    3          2       
    3          3       最低优先级
```


#### 4.3 抢占优先级 vs 响应优先级

**抢占优先级（Preemption Priority）**：
- 决定是否可以中断当前正在执行的ISR
- 数值越小，优先级越高
- 高抢占优先级可以打断低抢占优先级的ISR

**响应优先级（Sub Priority）**：
- 当抢占优先级相同时，决定响应顺序
- 数值越小，优先级越高
- 不能相互打断，按顺序执行

```c
// 配置中断优先级示例
void Interrupt_Priority_Config(void) {
    // 设置优先级分组为2（2位抢占，2位响应）
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 配置EXTI0中断：抢占优先级0，响应优先级0（最高）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 配置TIM2中断：抢占优先级1，响应优先级0
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    
    // 配置USART1中断：抢占优先级1，响应优先级1
    HAL_NVIC_SetPriority(USART1_IRQn, 1, 1);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
}
```

**优先级规则**：
1. 抢占优先级高的可以打断抢占优先级低的
2. 抢占优先级相同时，不能相互打断
3. 抢占优先级相同时，响应优先级高的先响应
4. 两个优先级都相同时，中断号小的先响应

### 5. 中断嵌套

#### 5.1 嵌套的概念

中断嵌套是指在执行一个中断服务程序时，又被更高优先级的中断打断。

```
主程序执行
    ↓
低优先级中断发生 → 执行ISR_Low
    ↓
高优先级中断发生 → 暂停ISR_Low → 执行ISR_High
    ↓
ISR_High执行完成 → 恢复ISR_Low
    ↓
ISR_Low执行完成 → 返回主程序
```

#### 5.2 嵌套示例

```c
// 低优先级中断（抢占优先级2）
void TIM2_IRQHandler(void) {
    printf("TIM2 ISR Start\n");
    
    // 执行较长时间的处理
    for (int i = 0; i < 1000; i++) {
        // 处理数据
    }
    
    printf("TIM2 ISR End\n");
    HAL_TIM_IRQHandler(&htim2);
}

// 高优先级中断（抢占优先级0）
void EXTI0_IRQHandler(void) {
    printf("EXTI0 ISR Start\n");  // 可以打断TIM2_IRQHandler
    
    // 快速处理紧急事件
    handle_urgent_event();
    
    printf("EXTI0 ISR End\n");
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}
```

**输出示例**：
```
TIM2 ISR Start
EXTI0 ISR Start    ← 高优先级中断打断
EXTI0 ISR End
TIM2 ISR End       ← 继续执行低优先级中断
```

#### 5.3 嵌套深度限制

虽然理论上可以无限嵌套，但实际应用中需要控制嵌套深度：

- **栈空间限制**：每次嵌套需要保存上下文到栈
- **实时性要求**：过深的嵌套影响响应时间
- **系统稳定性**：建议嵌套深度不超过3-4层

```c
// 禁止中断嵌套的方法
void Critical_ISR(void) {
    // 方法1：临时禁止所有中断
    __disable_irq();
    
    // 执行关键代码
    critical_operation();
    
    __enable_irq();
}

// 方法2：提高BASEPRI，屏蔽低优先级中断
void Partial_Critical_ISR(void) {
    uint32_t basepri_save = __get_BASEPRI();
    __set_BASEPRI(0x40);  // 屏蔽优先级低于4的中断
    
    // 执行关键代码
    critical_operation();
    
    __set_BASEPRI(basepri_save);
}
```


## 实践示例

### 示例1：基本的外部中断配置

让我们实现一个完整的按键中断示例：

```c
#include "stm32f4xx_hal.h"

// 按键连接到PA0引脚
#define BUTTON_PIN GPIO_PIN_0
#define BUTTON_PORT GPIOA

// 初始化按键中断
void Button_Interrupt_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 1. 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 2. 配置GPIO为输入模式
    GPIO_InitStruct.Pin = BUTTON_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;  // 上升沿触发中断
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;        // 下拉
    HAL_GPIO_Init(BUTTON_PORT, &GPIO_InitStruct);
    
    // 3. 配置NVIC优先级
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    
    // 4. 使能EXTI中断
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

// 中断服务函数
void EXTI0_IRQHandler(void) {
    // 检查中断标志
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN) != RESET) {
        // 清除中断标志
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 处理按键事件
        Button_Callback();
    }
}

// 按键回调函数
void Button_Callback(void) {
    static uint32_t press_count = 0;
    press_count++;
    
    printf("Button pressed! Count: %lu\n", press_count);
    
    // 翻转LED状态
    HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
}

int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化LED
    LED_Init();
    
    // 初始化按键中断
    Button_Interrupt_Init();
    
    printf("Button interrupt example started\n");
    
    while(1) {
        // 主循环可以执行其他任务
        HAL_Delay(1000);
        printf("Main loop running...\n");
    }
}
```

**代码说明**：
- 第10-22行：配置GPIO为中断模式，上升沿触发
- 第24-26行：配置NVIC优先级和使能中断
- 第30-39行：中断服务函数，检查并清除中断标志
- 第42-50行：按键回调函数，处理实际的按键逻辑

**运行结果**：
```
Button interrupt example started
Main loop running...
Button pressed! Count: 1
Main loop running...
Button pressed! Count: 2
Main loop running...
```

### 示例2：多个中断源的优先级管理

演示如何配置和管理多个中断源：

```c
// 中断优先级配置
void Multi_Interrupt_Config(void) {
    // 设置优先级分组
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    // 紧急按键中断 - 最高优先级（抢占0，响应0）
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 定时器中断 - 中等优先级（抢占1，响应0）
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    
    // 串口接收中断 - 中等优先级（抢占1，响应1）
    HAL_NVIC_SetPriority(USART1_IRQn, 1, 1);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
    
    // ADC转换完成中断 - 低优先级（抢占2，响应0）
    HAL_NVIC_SetPriority(ADC_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(ADC_IRQn);
}

// 紧急按键中断 - 可以打断所有其他中断
void EXTI0_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0)) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 处理紧急事件（如紧急停止）
        Emergency_Stop();
    }
}

// 定时器中断 - 可以打断ADC中断
void TIM2_IRQHandler(void) {
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 定时任务处理
        Timer_Task();
    }
}

// 串口中断 - 与定时器中断同级，不能相互打断
void USART1_IRQHandler(void) {
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        // 接收数据
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        UART_Receive_Callback(data);
    }
}

// ADC中断 - 最低优先级，可被所有其他中断打断
void ADC_IRQHandler(void) {
    if (__HAL_ADC_GET_FLAG(&hadc1, ADC_FLAG_EOC)) {
        __HAL_ADC_CLEAR_FLAG(&hadc1, ADC_FLAG_EOC);
        
        // 读取ADC值
        uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
        ADC_Conversion_Callback(adc_value);
    }
}
```


### 示例3：中断嵌套演示

演示中断嵌套的实际效果：

```c
#include <stdio.h>

volatile uint32_t interrupt_depth = 0;  // 记录嵌套深度

// 低优先级中断（抢占优先级2）
void TIM3_IRQHandler(void) {
    interrupt_depth++;
    printf("[Depth %lu] TIM3 ISR Start\n", interrupt_depth);
    
    // 模拟较长的处理时间
    HAL_Delay(100);
    
    printf("[Depth %lu] TIM3 ISR End\n", interrupt_depth);
    interrupt_depth--;
    
    __HAL_TIM_CLEAR_FLAG(&htim3, TIM_FLAG_UPDATE);
}

// 中等优先级中断（抢占优先级1）
void TIM2_IRQHandler(void) {
    interrupt_depth++;
    printf("[Depth %lu] TIM2 ISR Start (preempted TIM3)\n", interrupt_depth);
    
    // 模拟中等处理时间
    HAL_Delay(50);
    
    printf("[Depth %lu] TIM2 ISR End\n", interrupt_depth);
    interrupt_depth--;
    
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
}

// 高优先级中断（抢占优先级0）
void EXTI0_IRQHandler(void) {
    interrupt_depth++;
    printf("[Depth %lu] EXTI0 ISR Start (preempted all)\n", interrupt_depth);
    
    // 快速处理
    HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
    
    printf("[Depth %lu] EXTI0 ISR End\n", interrupt_depth);
    interrupt_depth--;
    
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
}
```

**可能的输出**：
```
[Depth 1] TIM3 ISR Start
[Depth 2] TIM2 ISR Start (preempted TIM3)
[Depth 3] EXTI0 ISR Start (preempted all)
[Depth 3] EXTI0 ISR End
[Depth 2] TIM2 ISR End
[Depth 1] TIM3 ISR End
```

## 深入理解

### 中断上下文切换

当中断发生时，处理器需要保存当前状态并切换到中断处理程序。

**自动保存的寄存器**（硬件自动完成）：
- R0-R3：参数和临时寄存器
- R12：临时寄存器
- LR：链接寄存器
- PC：程序计数器
- xPSR：程序状态寄存器

**手动保存的寄存器**（如果ISR使用）：
- R4-R11：需要保存的寄存器

```
栈的变化：

中断前：
    ┌─────────┐
    │  主程序  │ ← SP
    └─────────┘

中断后（自动压栈）：
    ┌─────────┐
    │  xPSR   │
    ├─────────┤
    │   PC    │
    ├─────────┤
    │   LR    │
    ├─────────┤
    │   R12   │
    ├─────────┤
    │   R3    │
    ├─────────┤
    │   R2    │
    ├─────────┤
    │   R1    │
    ├─────────┤
    │   R0    │ ← SP
    └─────────┘
```

### 尾链优化（Tail-chaining）

当一个中断服务程序结束时，如果有另一个待处理的中断，处理器可以直接跳转到新的ISR，而不需要恢复和重新保存上下文。

```
传统方式：
ISR1 → 恢复上下文 → 保存上下文 → ISR2
耗时：约25个时钟周期

尾链优化：
ISR1 → 直接跳转 → ISR2
耗时：约6个时钟周期
```

### 中断延迟抖动（Jitter）

中断延迟抖动是指中断响应时间的变化范围。

**影响因素**：
- 当前指令的执行状态
- 其他高优先级中断的执行
- 中断禁止状态
- 总线仲裁延迟

**减少抖动的方法**：
- 使用高优先级
- 减少临界区时间
- 避免长时间禁止中断
- 使用DMA减少CPU干预

### 最佳实践

1. **ISR应该尽可能短**
   ```c
   // 不好的做法
   void BAD_IRQHandler(void) {
       // 在ISR中执行复杂计算
       for (int i = 0; i < 10000; i++) {
           complex_calculation();
       }
   }
   
   // 好的做法
   volatile uint8_t data_ready = 0;
   
   void GOOD_IRQHandler(void) {
       // 只设置标志，快速返回
       data_ready = 1;
       __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
   }
   
   void main_loop(void) {
       if (data_ready) {
           data_ready = 0;
           // 在主循环中处理
           process_data();
       }
   }
   ```

2. **合理设置优先级**
   - 紧急事件使用高优先级
   - 常规事件使用中等优先级
   - 后台任务使用低优先级
   - 避免所有中断使用相同优先级

3. **避免在ISR中调用阻塞函数**
   ```c
   // 不要在ISR中使用
   void BAD_IRQHandler(void) {
       HAL_Delay(100);        // ❌ 阻塞延时
       printf("Long text");   // ❌ 可能很慢
       malloc(1024);          // ❌ 动态分配
   }
   ```

4. **正确清除中断标志**
   ```c
   void IRQHandler(void) {
       // 先检查标志
       if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
           // 处理中断
           handle_interrupt();
           
           // 最后清除标志
           __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
       }
   }
   ```

5. **使用volatile关键字**
   ```c
   // ISR和主程序共享的变量必须使用volatile
   volatile uint32_t interrupt_count = 0;
   volatile uint8_t data_buffer[256];
   
   void IRQHandler(void) {
       interrupt_count++;  // 编译器不会优化掉
   }
   ```


## 常见问题

### Q1: 中断和轮询应该如何选择？

**A**: 选择依据：

**使用中断的场景**：
- 事件发生频率低且不可预测
- 需要快速响应（微秒级）
- CPU需要执行其他任务
- 例如：按键输入、外部信号、通信接收

**使用轮询的场景**：
- 事件发生频率高且可预测
- 响应时间要求不严格
- 系统简单，中断开销大
- 例如：高速ADC采样、简单的状态机

**混合使用**：
```c
// 中断触发数据采集
void ADC_IRQHandler(void) {
    data_ready = 1;
}

// 主循环轮询处理
void main_loop(void) {
    if (data_ready) {
        data_ready = 0;
        // 轮询处理多个数据
        while (has_more_data()) {
            process_data();
        }
    }
}
```

### Q2: 为什么中断服务函数要尽可能短？

**A**: 主要原因：

1. **影响系统响应性**
   - 长时间的ISR会阻塞其他中断
   - 降低系统的实时性

2. **增加中断延迟**
   - 其他中断需要等待当前ISR完成
   - 可能导致中断丢失

3. **栈空间消耗**
   - 嵌套中断会消耗更多栈空间
   - 可能导致栈溢出

**解决方案**：
```c
// 使用标志位延迟处理
volatile uint8_t event_flag = 0;

void Quick_IRQHandler(void) {
    event_flag = 1;  // 快速设置标志
    clear_interrupt_flag();
}

void main_loop(void) {
    if (event_flag) {
        event_flag = 0;
        // 在主循环中处理耗时操作
        time_consuming_task();
    }
}
```

### Q3: 什么是中断重入问题？

**A**: 中断重入是指同一个中断服务函数被多次进入。

**问题场景**：
```c
volatile uint32_t counter = 0;

void TIM_IRQHandler(void) {
    counter++;  // 非原子操作
    
    // 如果此时发生同一中断（重入）
    // counter的值可能不正确
    
    clear_interrupt_flag();
}
```

**解决方法**：

1. **硬件层面**：同一中断源不会重入（NVIC自动处理）
2. **软件层面**：使用原子操作或临界区

```c
// 方法1：使用原子操作
void TIM_IRQHandler(void) {
    __atomic_fetch_add(&counter, 1, __ATOMIC_SEQ_CST);
    clear_interrupt_flag();
}

// 方法2：临时禁止中断
void TIM_IRQHandler(void) {
    __disable_irq();
    counter++;
    __enable_irq();
    clear_interrupt_flag();
}
```

### Q4: 如何调试中断问题？

**A**: 常用调试方法：

1. **使用LED指示**
   ```c
   void IRQHandler(void) {
       HAL_GPIO_WritePin(DEBUG_LED_PORT, DEBUG_LED_PIN, GPIO_PIN_SET);
       
       // 中断处理代码
       
       HAL_GPIO_WritePin(DEBUG_LED_PORT, DEBUG_LED_PIN, GPIO_PIN_RESET);
   }
   ```

2. **使用计数器**
   ```c
   volatile uint32_t irq_count = 0;
   
   void IRQHandler(void) {
       irq_count++;  // 统计中断次数
       // 处理中断
   }
   ```

3. **使用串口输出**
   ```c
   void IRQHandler(void) {
       printf("IRQ triggered at %lu ms\n", HAL_GetTick());
       // 注意：printf可能很慢，仅用于调试
   }
   ```

4. **使用逻辑分析仪**
   - 在ISR入口和出口翻转GPIO
   - 使用逻辑分析仪观察时序

5. **使用调试器断点**
   - 在ISR中设置断点
   - 查看寄存器和变量值
   - 注意：断点会影响实时性

### Q5: 中断优先级应该如何分配？

**A**: 优先级分配原则：

1. **按紧急程度分配**
   ```
   最高优先级：安全相关（紧急停止、故障检测）
   高优先级：  实时性要求高（通信、定时器）
   中优先级：  常规外设（ADC、按键）
   低优先级：  后台任务（日志、统计）
   ```

2. **按执行时间分配**
   - 执行时间短的可以用高优先级
   - 执行时间长的应该用低优先级

3. **避免优先级反转**
   ```c
   // 不好的设计
   高优先级任务 → 等待 → 低优先级任务持有的资源
   中优先级任务 → 抢占 → 低优先级任务
   // 结果：高优先级任务被中优先级任务间接阻塞
   ```

4. **预留优先级空间**
   - 不要把所有优先级都用满
   - 为将来扩展留出空间

## 总结

本文介绍了嵌入式系统中断机制的基础知识，核心要点包括：

- **中断原理**：事件驱动的异步处理机制，提高系统效率
- **中断类型**：外部中断、内部中断、软件中断，电平触发和边沿触发
- **中断向量**：存储ISR入口地址的表，支持向量表重定位
- **优先级管理**：NVIC提供灵活的优先级配置，支持抢占和响应优先级
- **中断嵌套**：高优先级可以打断低优先级，需要控制嵌套深度

掌握这些基础知识后，你就可以正确配置和使用中断系统，编写高效的嵌入式应用程序。

## 延伸阅读

- [外部中断配置与使用](02-external-interrupt.html) - 详细学习EXTI配置
- [定时器中断实现精确延时](03-timer-interrupt.html) - 使用定时器中断
- [中断优先级配置与抢占机制](../intermediate/01-interrupt-priority.html) - 深入理解优先级

## 参考资料

1. ARM Cortex-M3 Technical Reference Manual - ARM官方文档
2. STM32F4xx Reference Manual - ST官方参考手册
3. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" by Joseph Yiu
4. NVIC and Interrupt Management - ARM Application Note

---

**练习题**：

1. 解释中断和轮询的区别，并说明各自的适用场景。
2. 在优先级分组为2的情况下，如果同时发生抢占优先级为1的两个中断，系统如何决定先响应哪个？
3. 编写一个程序，配置三个不同优先级的中断，并演示中断嵌套的效果。
4. 为什么在中断服务函数中要避免使用printf和malloc等函数？

**下一步**：建议学习 [外部中断配置与使用](02-external-interrupt.html)，通过实践掌握EXTI的配置方法。
