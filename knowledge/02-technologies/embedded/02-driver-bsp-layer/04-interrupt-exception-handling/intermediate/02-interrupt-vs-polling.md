---
title: "中断与轮询的选择策略"
description: "深入分析中断和轮询两种事件处理机制的优缺点、适用场景和性能特征，掌握在不同应用场景下选择合适机制的方法，学习混合策略的设计与实现，通过实战案例理解如何权衡系统资源和响应性能"
slug: "interrupt-vs-polling"

# 分类信息
domain: "驱动与BSP层"
module: "中断与异常处理"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 中断
  - 轮询
  - 设计策略
  - 性能分析
  - 事件处理
prerequisites:
  - "interrupt-basics"
  - "interrupt-priority"
related_contents:
  - "external-interrupt"
  - "interrupt-safety"

# 学习信息
estimated_time: 40
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
  - 中断机制
  - 轮询机制
  - 事件处理
  - 性能优化
  - 设计模式
cover_image: ""
---

# 中断与轮询的选择策略

## 概述

在嵌入式系统开发中，处理外部事件有两种基本机制：中断（Interrupt）和轮询（Polling）。选择合适的机制对系统的性能、功耗和实时性有重要影响。本文将深入分析这两种机制的特点、优缺点和适用场景，帮助你做出正确的设计决策。

完成本文学习后，你将能够：

- 理解中断和轮询的工作原理和特点
- 掌握两种机制的优缺点和性能特征
- 学会根据应用场景选择合适的机制
- 理解混合策略的设计方法
- 掌握性能分析和优化技巧

## 背景知识

### 什么是轮询？

轮询是一种主动检查机制，处理器周期性地检查某个条件或状态，直到满足特定条件后执行相应操作。

**轮询的基本流程**：

```
主程序循环
    ↓
检查事件标志
    ↓
事件发生？
    ├─ 是 → 处理事件 → 继续循环
    └─ 否 → 继续循环
```

### 什么是中断？

中断是一种被动响应机制，当事件发生时，硬件自动通知处理器，处理器暂停当前任务，转而执行中断服务程序。

**中断的基本流程**：

```
主程序执行
    ↓
事件发生（硬件信号）
    ↓
自动保存现场
    ↓
执行中断服务程序
    ↓
恢复现场
    ↓
返回主程序
```

## 核心内容

### 1. 轮询机制详解

#### 1.1 轮询的实现方式

**简单轮询**：

```c
// 最基本的轮询实现
void simple_polling(void)
{
    while (1) {
        // 检查按键状态
        if (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN) == GPIO_PIN_SET) {
            // 处理按键事件
            handle_button_press();
            
            // 等待按键释放
            while (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN) == GPIO_PIN_SET);
        }
    }
}
```

**多事件轮询**：

```c
// 轮询多个事件源
void multi_event_polling(void)
{
    while (1) {
        // 检查按键
        if (button_pressed()) {
            handle_button();
        }
        
        // 检查串口数据
        if (uart_data_available()) {
            handle_uart_data();
        }
        
        // 检查定时器
        if (timer_expired()) {
            handle_timer();
        }
        
        // 检查ADC转换完成
        if (adc_conversion_complete()) {
            handle_adc_data();
        }
    }
}
```

**定时轮询**：

```c
// 使用定时器控制轮询频率
void timed_polling(void)
{
    uint32_t last_check_time = 0;
    const uint32_t POLL_INTERVAL = 10;  // 10ms轮询间隔
    
    while (1) {
        uint32_t current_time = HAL_GetTick();
        
        if (current_time - last_check_time >= POLL_INTERVAL) {
            last_check_time = current_time;
            
            // 执行轮询检查
            check_all_events();
        }
        
        // 执行其他任务
        do_other_work();
    }
}
```

#### 1.2 轮询的优点

**1. 实现简单**
- 代码逻辑清晰，易于理解
- 不需要配置中断控制器
- 调试方便，流程可预测

**2. 无中断开销**
- 没有上下文切换
- 没有中断延迟
- 没有中断嵌套问题

**3. 时序可控**
- 检查顺序固定
- 响应时间可预测
- 适合简单的状态机

**4. 资源占用少**
- 不需要中断向量表
- 不需要额外的栈空间
- 适合资源受限的系统

#### 1.3 轮询的缺点

**1. CPU利用率低**
- 大量时间浪费在检查上
- 即使没有事件也要不断检查
- 功耗较高

**2. 响应延迟**
- 事件发生到被检测之间有延迟
- 延迟取决于轮询周期
- 可能错过快速事件

**3. 实时性差**
- 无法保证及时响应
- 多个事件时响应时间不确定
- 不适合硬实时系统

**4. 可扩展性差**
- 事件源增多时效率下降
- 轮询周期难以平衡
- 代码复杂度增加

### 2. 中断机制详解

#### 2.1 中断的实现方式

**外部中断**：

```c
// 配置外部中断
void external_interrupt_init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 配置GPIO为中断模式
    GPIO_InitStruct.Pin = BUTTON_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(BUTTON_PORT, &GPIO_InitStruct);
    
    // 配置NVIC
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

// 中断服务函数
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN)) {
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 快速处理或设置标志
        button_event_flag = 1;
    }
}

// 主循环
void main_loop(void)
{
    while (1) {
        if (button_event_flag) {
            button_event_flag = 0;
            // 处理按键事件
            handle_button_event();
        }
        
        // 执行其他任务
        do_other_work();
    }
}
```

**定时器中断**：

```c
// 配置定时器中断
void timer_interrupt_init(void)
{
    // 配置定时器为1ms中断
    htim2.Instance = TIM2;
    htim2.Init.Period = 1000 - 1;  // 1ms
    htim2.Init.Prescaler = 72 - 1;  // 72MHz / 72 = 1MHz
    HAL_TIM_Base_Init(&htim2);
    
    // 使能中断
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    
    HAL_TIM_Base_Start_IT(&htim2);
}

// 定时器中断服务函数
void TIM2_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 周期性任务
        system_tick++;
        
        // 触发周期任务标志
        if (system_tick % 100 == 0) {
            periodic_task_flag = 1;
        }
    }
}
```

#### 2.2 中断的优点

**1. 响应快速**
- 微秒级响应时间
- 事件驱动，无需等待
- 适合实时系统

**2. CPU利用率高**
- 只在事件发生时处理
- 空闲时可以执行其他任务
- 可以进入低功耗模式

**3. 实时性好**
- 可以保证响应时间
- 支持优先级管理
- 适合硬实时应用

**4. 可扩展性好**
- 多个中断源独立处理
- 不影响主程序流程
- 易于添加新的事件源

#### 2.3 中断的缺点

**1. 实现复杂**
- 需要配置中断控制器
- 需要管理优先级
- 调试相对困难

**2. 有中断开销**
- 上下文切换需要时间
- 保存和恢复寄存器
- 中断延迟和抖动

**3. 可能有竞态条件**
- 需要保护共享资源
- 可能发生优先级反转
- 需要考虑中断嵌套

**4. 资源占用**
- 需要中断向量表
- 需要额外的栈空间
- 可能增加功耗（频繁中断）

### 3. 性能对比分析

#### 3.1 响应时间对比

**轮询的响应时间**：

```
最小响应时间 = 0（刚好检查到）
最大响应时间 = 轮询周期
平均响应时间 = 轮询周期 / 2

示例：轮询周期 = 10ms
- 最小响应：0ms
- 最大响应：10ms
- 平均响应：5ms
```

**中断的响应时间**：

```
响应时间 = 中断延迟 + ISR执行时间

中断延迟组成：
- 硬件延迟：1-2个时钟周期
- 保存上下文：12个时钟周期
- 跳转到ISR：2-3个时钟周期

示例：72MHz系统
- 中断延迟：约15-20个时钟周期 = 0.2-0.3μs
- ISR执行：取决于代码（通常<10μs）
- 总响应时间：<10μs
```

**对比表**：

| 特性 | 轮询 | 中断 |
|------|------|------|
| 最小响应时间 | 0 | 0.2-0.3μs |
| 典型响应时间 | 毫秒级 | 微秒级 |
| 响应时间确定性 | 较差 | 很好 |
| 适合实时系统 | 否 | 是 |

#### 3.2 CPU利用率对比

**轮询的CPU利用率**：

```c
// 测量轮询的CPU占用
void measure_polling_cpu_usage(void)
{
    uint32_t idle_count = 0;
    uint32_t total_count = 0;
    uint32_t start_time = HAL_GetTick();
    
    while (HAL_GetTick() - start_time < 1000) {  // 测量1秒
        total_count++;
        
        // 轮询检查
        if (check_event()) {
            handle_event();
        } else {
            idle_count++;
        }
    }
    
    float cpu_usage = (1.0f - (float)idle_count / total_count) * 100;
    printf("Polling CPU Usage: %.2f%%\n", cpu_usage);
}

// 典型结果：
// 事件频率低时：CPU利用率 > 90%（大部分时间在空转）
// 事件频率高时：CPU利用率接近100%
```

**中断的CPU利用率**：

```c
// 测量中断的CPU占用
volatile uint32_t isr_entry_count = 0;
volatile uint32_t isr_total_cycles = 0;

void IRQHandler(void)
{
    uint32_t start = DWT->CYCCNT;
    
    // 中断处理
    handle_interrupt();
    
    uint32_t end = DWT->CYCCNT;
    isr_total_cycles += (end - start);
    isr_entry_count++;
}

void measure_interrupt_cpu_usage(void)
{
    uint32_t start_time = HAL_GetTick();
    uint32_t start_cycles = DWT->CYCCNT;
    
    HAL_Delay(1000);  // 测量1秒
    
    uint32_t total_cycles = DWT->CYCCNT - start_cycles;
    float cpu_usage = ((float)isr_total_cycles / total_cycles) * 100;
    
    printf("Interrupt CPU Usage: %.2f%%\n", cpu_usage);
    printf("Interrupt Count: %lu\n", isr_entry_count);
}

// 典型结果：
// 事件频率低时：CPU利用率 < 1%
// 事件频率高时：取决于ISR执行时间
```

#### 3.3 功耗对比

**轮询的功耗特征**：

```c
// 轮询模式 - 高功耗
void polling_mode(void)
{
    while (1) {
        // CPU持续运行，无法进入低功耗模式
        if (check_event()) {
            handle_event();
        }
        // CPU一直处于活动状态
    }
}

// 功耗特点：
// - CPU持续运行：高功耗
// - 无法进入睡眠模式
// - 不适合电池供电设备
```

**中断的功耗特征**：

```c
// 中断模式 - 低功耗
void interrupt_mode(void)
{
    // 配置中断
    configure_interrupts();
    
    while (1) {
        // 处理标志位
        if (event_flag) {
            event_flag = 0;
            handle_event();
        }
        
        // 进入低功耗模式，等待中断唤醒
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    }
}

// 功耗特点：
// - 空闲时进入睡眠：低功耗
// - 中断唤醒：快速响应
// - 适合电池供电设备
```

**功耗对比表**：

| 模式 | 活动电流 | 睡眠电流 | 平均功耗（事件少） |
|------|---------|---------|------------------|
| 轮询 | 50mA | N/A | 50mA |
| 中断 | 50mA | 2mA | 2-5mA |

### 4. 选择策略

#### 4.1 使用轮询的场景

**1. 事件频率高且可预测**

```c
// 示例：高速ADC采样
void high_speed_adc_polling(void)
{
    while (1) {
        // 启动转换
        HAL_ADC_Start(&hadc1);
        
        // 轮询等待转换完成（很快，几微秒）
        while (HAL_ADC_PollForConversion(&hadc1, 1) != HAL_OK);
        
        // 读取数据
        uint32_t value = HAL_ADC_GetValue(&hadc1);
        process_adc_data(value);
    }
}

// 适用原因：
// - 转换频率高（kHz级别）
// - 转换时间短且可预测
// - 使用中断反而增加开销
```

**2. 系统简单，资源受限**

```c
// 示例：简单的LED闪烁控制
void simple_led_control(void)
{
    while (1) {
        // 检查按键
        if (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN) == GPIO_PIN_SET) {
            HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
            HAL_Delay(200);  // 防抖
        }
    }
}

// 适用原因：
// - 功能简单
// - 不需要复杂的中断配置
// - 代码易于理解和维护
```

**3. 响应时间要求不严格**

```c
// 示例：状态监控
void status_monitor(void)
{
    while (1) {
        // 每秒检查一次温度
        HAL_Delay(1000);
        
        float temperature = read_temperature();
        if (temperature > THRESHOLD) {
            trigger_alarm();
        }
    }
}

// 适用原因：
// - 1秒的响应延迟可以接受
// - 不需要实时响应
// - 轮询更简单
```

**4. 调试和测试阶段**

```c
// 示例：功能验证
void function_test(void)
{
    while (1) {
        // 轮询方式便于单步调试
        if (sensor_ready()) {
            uint32_t data = read_sensor();
            printf("Sensor data: %lu\n", data);
        }
        
        HAL_Delay(100);
    }
}

// 适用原因：
// - 流程清晰，易于调试
// - 可以单步跟踪
// - 验证功能正确性
```

#### 4.2 使用中断的场景

**1. 事件频率低且不可预测**

```c
// 示例：按键输入
void button_interrupt_mode(void)
{
    // 配置按键中断
    configure_button_interrupt();
    
    while (1) {
        // CPU可以执行其他任务或进入睡眠
        do_other_work();
        
        // 或进入低功耗模式
        // HAL_PWR_EnterSLEEPMode(...);
    }
}

void EXTI_IRQHandler(void)
{
    // 按键按下时才响应
    button_pressed_flag = 1;
}

// 适用原因：
// - 按键事件不频繁
// - 发生时间不可预测
// - 轮询会浪费CPU资源
```

**2. 需要快速响应**

```c
// 示例：紧急停止
void emergency_stop_interrupt(void)
{
    // 配置最高优先级中断
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

void EXTI0_IRQHandler(void)
{
    // 微秒级响应
    __HAL_GPIO_EXTI_CLEAR_IT(EMERGENCY_PIN);
    
    // 立即停止所有运动
    stop_all_motors();
    system_state = EMERGENCY_STOP;
}

// 适用原因：
// - 需要微秒级响应
// - 安全关键应用
// - 轮询延迟不可接受
```

**3. 多任务并发处理**

```c
// 示例：多个独立事件源
void multi_source_interrupt(void)
{
    // 配置多个中断源
    configure_uart_interrupt();    // 串口接收
    configure_timer_interrupt();   // 定时任务
    configure_adc_interrupt();     // ADC转换完成
    configure_dma_interrupt();     // DMA传输完成
    
    while (1) {
        // 主循环处理后台任务
        background_tasks();
    }
}

// 各个中断独立处理
void UART_IRQHandler(void) { /* 处理串口 */ }
void TIM_IRQHandler(void) { /* 处理定时器 */ }
void ADC_IRQHandler(void) { /* 处理ADC */ }
void DMA_IRQHandler(void) { /* 处理DMA */ }

// 适用原因：
// - 多个事件源独立处理
// - 不相互干扰
// - 轮询难以管理多个源
```

**4. 低功耗应用**

```c
// 示例：电池供电设备
void low_power_application(void)
{
    // 配置唤醒中断
    configure_wakeup_interrupts();
    
    while (1) {
        // 处理事件
        if (event_flag) {
            event_flag = 0;
            handle_event();
        }
        
        // 进入深度睡眠，等待中断唤醒
        enter_deep_sleep();
    }
}

void EXTI_IRQHandler(void)
{
    // 中断唤醒系统
    event_flag = 1;
}

// 适用原因：
// - 大部分时间处于睡眠
// - 中断唤醒快速响应
// - 延长电池寿命
```

### 5. 混合策略

#### 5.1 中断触发 + 轮询处理

这是最常用的混合策略：中断快速响应事件，轮询处理复杂逻辑。

```c
// 中断设置标志
volatile uint8_t data_ready = 0;
volatile uint8_t uart_buffer[256];
volatile uint16_t uart_index = 0;

void UART_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        // 快速读取数据
        uart_buffer[uart_index++] = huart1.Instance->DR;
        
        // 接收完整帧
        if (uart_index >= FRAME_SIZE) {
            data_ready = 1;
            uart_index = 0;
        }
    }
}

// 主循环轮询处理
void main_loop(void)
{
    while (1) {
        // 轮询检查标志
        if (data_ready) {
            data_ready = 0;
            
            // 复杂的数据处理（在主循环中）
            parse_protocol(uart_buffer);
            process_command(uart_buffer);
            send_response();
        }
        
        // 执行其他任务
        do_other_work();
    }
}

// 优点：
// - 中断快速响应，不丢失数据
// - 复杂处理在主循环，不阻塞中断
// - 平衡了响应性和系统复杂度
```

#### 5.2 定时中断 + 轮询检查

使用定时器中断控制轮询频率，既保证了响应时间，又降低了CPU占用。

```c
// 定时器中断设置轮询标志
volatile uint8_t poll_flag = 0;

void TIM_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        // 每10ms设置一次轮询标志
        poll_flag = 1;
    }
}

// 主循环按标志轮询
void main_loop(void)
{
    while (1) {
        if (poll_flag) {
            poll_flag = 0;
            
            // 轮询检查多个事件
            check_button_state();
            check_sensor_data();
            update_display();
        }
        
        // 空闲时可以进入低功耗模式
        __WFI();  // 等待中断
    }
}

// 优点：
// - 精确控制轮询频率
// - 降低CPU占用
// - 可以进入低功耗模式
```

#### 5.3 优先级分层策略

根据事件的重要性和实时性要求，采用不同的处理方式。

```c
// 高优先级事件：使用中断
void configure_high_priority_events(void)
{
    // 紧急停止 - 最高优先级中断
    HAL_NVIC_SetPriority(EMERGENCY_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EMERGENCY_IRQn);
    
    // 编码器 - 高优先级中断
    HAL_NVIC_SetPriority(ENCODER_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(ENCODER_IRQn);
}

// 中优先级事件：中断触发 + 标志处理
volatile uint8_t uart_flag = 0;
volatile uint8_t adc_flag = 0;

void UART_IRQHandler(void) { uart_flag = 1; }
void ADC_IRQHandler(void) { adc_flag = 1; }

// 低优先级事件：定时轮询
void main_loop(void)
{
    uint32_t last_poll_time = 0;
    
    while (1) {
        // 处理中优先级事件标志
        if (uart_flag) {
            uart_flag = 0;
            handle_uart_data();
        }
        
        if (adc_flag) {
            adc_flag = 0;
            handle_adc_data();
        }
        
        // 定时轮询低优先级事件
        if (HAL_GetTick() - last_poll_time >= 100) {
            last_poll_time = HAL_GetTick();
            
            check_button();
            update_led();
            check_temperature();
        }
    }
}

// 优点：
// - 关键事件快速响应
// - 一般事件及时处理
// - 低优先级事件不影响系统
```

### 6. 实战案例分析

#### 案例1：串口通信

**场景**：接收不定长的串口数据包

**方案A：纯轮询**

```c
// ❌ 不推荐：纯轮询方式
void uart_polling_receive(void)
{
    uint8_t buffer[256];
    uint16_t index = 0;
    
    while (1) {
        // 不断检查是否有数据
        if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
            buffer[index++] = huart1.Instance->DR;
            
            if (index >= 256 || buffer[index-1] == '\n') {
                process_data(buffer, index);
                index = 0;
            }
        }
        
        // 问题：
        // 1. CPU一直在检查，利用率高
        // 2. 高波特率时可能丢失数据
        // 3. 无法执行其他任务
    }
}
```

**方案B：中断接收**

```c
// ✅ 推荐：中断方式
volatile uint8_t rx_buffer[256];
volatile uint16_t rx_index = 0;
volatile uint8_t rx_complete = 0;

void UART_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        uint8_t data = huart1.Instance->DR;
        
        rx_buffer[rx_index++] = data;
        
        if (data == '\n' || rx_index >= 256) {
            rx_complete = 1;
            rx_index = 0;
        }
    }
}

void main_loop(void)
{
    while (1) {
        if (rx_complete) {
            rx_complete = 0;
            process_data(rx_buffer, rx_index);
        }
        
        // 可以执行其他任务
        do_other_work();
    }
}

// 优点：
// 1. 不会丢失数据
// 2. CPU利用率低
// 3. 可以执行其他任务
```

#### 案例2：按键检测

**场景**：检测按键按下并防抖

**方案A：纯轮询**

```c
// ✅ 适合：简单应用的轮询方式
void button_polling(void)
{
    uint8_t last_state = 0;
    uint32_t press_time = 0;
    
    while (1) {
        uint8_t current_state = HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN);
        
        // 检测按下
        if (current_state && !last_state) {
            press_time = HAL_GetTick();
        }
        
        // 检测释放（防抖）
        if (!current_state && last_state) {
            if (HAL_GetTick() - press_time > 50) {  // 50ms防抖
                handle_button_press();
            }
        }
        
        last_state = current_state;
        HAL_Delay(10);  // 10ms轮询间隔
    }
}

// 适用原因：
// 1. 按键响应延迟10-20ms可接受
// 2. 代码简单，易于理解
// 3. 防抖逻辑清晰
```

**方案B：中断方式**

```c
// ✅ 适合：低功耗应用的中断方式
volatile uint32_t button_press_time = 0;
volatile uint8_t button_event = 0;

void EXTI_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(BUTTON_PIN)) {
        __HAL_GPIO_EXTI_CLEAR_IT(BUTTON_PIN);
        
        // 记录按下时间
        button_press_time = HAL_GetTick();
        button_event = 1;
    }
}

void main_loop(void)
{
    while (1) {
        if (button_event) {
            button_event = 0;
            
            // 软件防抖
            HAL_Delay(50);
            
            // 确认仍然按下
            if (HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN)) {
                handle_button_press();
            }
        }
        
        // 进入低功耗模式
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    }
}

// 适用原因：
// 1. 低功耗应用
// 2. 按键事件不频繁
// 3. 可以进入睡眠模式
```

#### 案例3：ADC数据采集

**场景**：周期性采集多通道ADC数据

**方案A：轮询方式**

```c
// ✅ 适合：高速连续采样
void adc_polling_mode(void)
{
    uint32_t adc_values[8];
    
    while (1) {
        for (int i = 0; i < 8; i++) {
            // 选择通道
            select_adc_channel(i);
            
            // 启动转换
            HAL_ADC_Start(&hadc1);
            
            // 轮询等待转换完成（很快，几微秒）
            HAL_ADC_PollForConversion(&hadc1, 10);
            
            // 读取数据
            adc_values[i] = HAL_ADC_GetValue(&hadc1);
        }
        
        // 处理数据
        process_adc_data(adc_values, 8);
    }
}

// 适用原因：
// 1. 需要连续高速采样
// 2. 转换时间短且可预测
// 3. 中断开销反而降低效率
```

**方案B：中断 + DMA方式**

```c
// ✅ 适合：周期性采样 + 其他任务
uint32_t adc_buffer[8];
volatile uint8_t adc_complete = 0;

void ADC_DMA_Init(void)
{
    // 配置ADC为DMA模式
    HAL_ADC_Start_DMA(&hadc1, adc_buffer, 8);
}

void DMA_IRQHandler(void)
{
    if (__HAL_DMA_GET_FLAG(DMA_FLAG_TC)) {
        __HAL_DMA_CLEAR_FLAG(DMA_FLAG_TC);
        
        adc_complete = 1;
        
        // 重新启动DMA
        HAL_ADC_Start_DMA(&hadc1, adc_buffer, 8);
    }
}

void main_loop(void)
{
    while (1) {
        if (adc_complete) {
            adc_complete = 0;
            process_adc_data(adc_buffer, 8);
        }
        
        // 执行其他任务
        do_other_work();
    }
}

// 适用原因：
// 1. 周期性采样（不是连续）
// 2. 需要执行其他任务
// 3. DMA自动传输，CPU占用低
```

### 7. 决策流程图

选择中断还是轮询，可以按照以下流程决策：

```
开始
  ↓
事件频率高且可预测？
  ├─ 是 → 使用轮询
  └─ 否 ↓
需要微秒级响应？
  ├─ 是 → 使用中断
  └─ 否 ↓
需要低功耗？
  ├─ 是 → 使用中断
  └─ 否 ↓
系统简单，资源受限？
  ├─ 是 → 使用轮询
  └─ 否 ↓
多个独立事件源？
  ├─ 是 → 使用中断
  └─ 否 ↓
考虑混合策略
```

### 8. 性能优化技巧

#### 8.1 轮询优化

**1. 降低轮询频率**

```c
// ❌ 不好：过高的轮询频率
void bad_polling(void)
{
    while (1) {
        check_event();  // 每次循环都检查
    }
}

// ✅ 好：合理的轮询频率
void good_polling(void)
{
    uint32_t last_check = 0;
    
    while (1) {
        if (HAL_GetTick() - last_check >= 10) {  // 10ms检查一次
            last_check = HAL_GetTick();
            check_event();
        }
        
        do_other_work();
    }
}
```

**2. 优先级轮询**

```c
// 按优先级顺序轮询
void priority_polling(void)
{
    while (1) {
        // 高优先级事件：每次都检查
        if (check_critical_event()) {
            handle_critical_event();
        }
        
        // 中优先级事件：每10ms检查
        static uint32_t mid_last = 0;
        if (HAL_GetTick() - mid_last >= 10) {
            mid_last = HAL_GetTick();
            if (check_normal_event()) {
                handle_normal_event();
            }
        }
        
        // 低优先级事件：每100ms检查
        static uint32_t low_last = 0;
        if (HAL_GetTick() - low_last >= 100) {
            low_last = HAL_GetTick();
            if (check_low_priority_event()) {
                handle_low_priority_event();
            }
        }
    }
}
```

#### 8.2 中断优化

**1. 缩短ISR执行时间**

```c
// ❌ 不好：ISR中执行复杂处理
void BAD_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(PIN);
    
    // 复杂处理（阻塞其他中断）
    for (int i = 0; i < 1000; i++) {
        complex_calculation();
    }
}

// ✅ 好：ISR只设置标志
volatile uint8_t event_flag = 0;

void GOOD_IRQHandler(void)
{
    __HAL_GPIO_EXTI_CLEAR_IT(PIN);
    event_flag = 1;  // 快速返回
}

void main_loop(void)
{
    if (event_flag) {
        event_flag = 0;
        // 在主循环中处理
        complex_calculation();
    }
}
```

**2. 使用DMA减少中断频率**

```c
// ❌ 不好：每个字节触发一次中断
void byte_by_byte_interrupt(void)
{
    HAL_UART_Receive_IT(&huart1, &rx_byte, 1);
}

void UART_IRQHandler(void)
{
    // 每接收一个字节就中断一次
    buffer[index++] = rx_byte;
    HAL_UART_Receive_IT(&huart1, &rx_byte, 1);
}

// ✅ 好：使用DMA批量传输
void dma_transfer(void)
{
    HAL_UART_Receive_DMA(&huart1, rx_buffer, 256);
}

void DMA_IRQHandler(void)
{
    // 传输完256字节才中断一次
    process_buffer(rx_buffer, 256);
}
```

## 深入理解

### 中断开销分析

中断的总开销包括：

```
总开销 = 中断延迟 + ISR执行时间 + 恢复时间

详细分解（ARM Cortex-M3，72MHz）：
1. 中断延迟：15-20个时钟周期（0.2-0.3μs）
   - 硬件识别：1-2周期
   - 保存上下文：12周期
   - 跳转到ISR：2-3周期

2. ISR执行时间：取决于代码
   - 简单标志设置：5-10周期（<0.1μs）
   - 数据读取：20-50周期（0.3-0.7μs）
   - 复杂处理：>1000周期（>14μs）

3. 恢复时间：12个时钟周期（0.17μs）
   - 恢复上下文：12周期

最小总开销：约32个时钟周期（0.4μs）
```

### 轮询的隐藏成本

轮询看似简单，但有隐藏成本：

```
1. CPU占用成本
   - 即使没有事件，CPU也在运行
   - 无法进入低功耗模式
   - 功耗增加

2. 响应延迟成本
   - 平均延迟 = 轮询周期 / 2
   - 可能错过快速事件
   - 实时性差

3. 可扩展性成本
   - 事件源增多时，轮询周期变长
   - 或者需要提高轮询频率，增加CPU占用
   - 难以平衡

4. 代码复杂度成本
   - 多个事件源的轮询逻辑复杂
   - 状态管理困难
   - 维护成本高
```

### 混合策略的优势

混合策略结合了两种机制的优点：

```
中断部分：
- 快速响应事件
- 不丢失数据
- 低功耗

轮询部分：
- 复杂处理在主循环
- 不阻塞中断
- 易于调试

结果：
- 响应快速
- CPU利用率高
- 系统稳定
- 易于维护
```

## 最佳实践

### 1. 选择原则

```c
// 决策矩阵
typedef struct {
    uint32_t event_frequency;    // 事件频率（Hz）
    uint32_t response_time;      // 响应时间要求（μs）
    uint8_t  low_power_required; // 是否需要低功耗
    uint8_t  system_complexity;  // 系统复杂度（1-10）
} EventCharacteristics;

MechanismType select_mechanism(EventCharacteristics *event)
{
    // 规则1：高频率事件使用轮询
    if (event->event_frequency > 1000) {  // >1kHz
        return POLLING;
    }
    
    // 规则2：需要快速响应使用中断
    if (event->response_time < 100) {  // <100μs
        return INTERRUPT;
    }
    
    // 规则3：低功耗应用使用中断
    if (event->low_power_required) {
        return INTERRUPT;
    }
    
    // 规则4：简单系统可以使用轮询
    if (event->system_complexity < 3) {
        return POLLING;
    }
    
    // 默认：使用混合策略
    return HYBRID;
}
```

### 2. 实现建议

**轮询实现建议**：

```c
// ✅ 好的轮询实现
void good_polling_implementation(void)
{
    uint32_t last_poll_time = 0;
    const uint32_t POLL_INTERVAL = 10;  // 明确的轮询间隔
    
    while (1) {
        uint32_t current_time = HAL_GetTick();
        
        // 定时轮询
        if (current_time - last_poll_time >= POLL_INTERVAL) {
            last_poll_time = current_time;
            
            // 按优先级检查
            if (check_high_priority_event()) {
                handle_high_priority_event();
            }
            
            if (check_normal_event()) {
                handle_normal_event();
            }
        }
        
        // 执行其他任务
        do_background_work();
        
        // 可选：短暂睡眠降低功耗
        // HAL_Delay(1);
    }
}
```

**中断实现建议**：

```c
// ✅ 好的中断实现
volatile uint8_t event_flags = 0;
#define FLAG_UART    (1 << 0)
#define FLAG_TIMER   (1 << 1)
#define FLAG_ADC     (1 << 2)

// ISR只设置标志
void UART_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        rx_buffer[rx_index++] = huart1.Instance->DR;
        event_flags |= FLAG_UART;
    }
}

void TIM_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        event_flags |= FLAG_TIMER;
    }
}

// 主循环处理
void main_loop(void)
{
    while (1) {
        // 原子读取并清除标志
        uint8_t flags = __disable_irq_and_read(&event_flags);
        event_flags = 0;
        __enable_irq();
        
        // 按优先级处理
        if (flags & FLAG_UART) {
            handle_uart_event();
        }
        
        if (flags & FLAG_TIMER) {
            handle_timer_event();
        }
        
        if (flags & FLAG_ADC) {
            handle_adc_event();
        }
        
        // 空闲时进入低功耗
        if (event_flags == 0) {
            __WFI();
        }
    }
}
```

### 3. 常见陷阱

**陷阱1：轮询频率过高**

```c
// ❌ 错误：无意义的高频轮询
void bad_high_frequency_polling(void)
{
    while (1) {
        // 检查按键（人类反应时间>100ms）
        if (button_pressed()) {
            handle_button();
        }
        // 每次循环都检查，浪费CPU
    }
}

// ✅ 正确：合理的轮询频率
void good_polling_frequency(void)
{
    while (1) {
        // 10ms检查一次足够
        HAL_Delay(10);
        if (button_pressed()) {
            handle_button();
        }
    }
}
```

**陷阱2：ISR执行时间过长**

```c
// ❌ 错误：ISR中执行复杂操作
void BAD_IRQHandler(void)
{
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    
    // 复杂的浮点运算
    float result = sqrt(pow(x, 2) + pow(y, 2));
    
    // 长时间循环
    for (int i = 0; i < 10000; i++) {
        process_data(i);
    }
    
    // 阻塞延时
    HAL_Delay(100);
}

// ✅ 正确：ISR快速返回
volatile uint8_t data_ready = 0;

void GOOD_IRQHandler(void)
{
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
    data_ready = 1;  // 只设置标志
}
```

**陷阱3：忽略中断优先级**

```c
// ❌ 错误：所有中断使用相同优先级
void bad_priority_config(void)
{
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_SetPriority(TIM2_IRQn, 2, 0);
    HAL_NVIC_SetPriority(UART1_IRQn, 2, 0);
    // 无法保证重要中断的实时性
}

// ✅ 正确：合理分配优先级
void good_priority_config(void)
{
    // 紧急事件：最高优先级
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    
    // 实时控制：高优先级
    HAL_NVIC_SetPriority(TIM2_IRQn, 1, 0);
    
    // 通信：中等优先级
    HAL_NVIC_SetPriority(UART1_IRQn, 2, 0);
}
```

## 常见问题

### Q1: 什么时候应该使用轮询而不是中断？

**A**: 以下场景适合使用轮询：

1. **事件频率非常高**（>1kHz）
   - 中断开销会降低效率
   - 例如：高速ADC连续采样

2. **系统非常简单**
   - 只有1-2个事件源
   - 不需要复杂的中断配置
   - 例如：简单的LED闪烁控制

3. **响应时间要求不严格**
   - 毫秒级延迟可以接受
   - 例如：温度监控（每秒检查一次）

4. **调试和原型阶段**
   - 轮询代码更容易调试
   - 流程清晰，便于验证功能

### Q2: 中断会增加多少系统开销？

**A**: 中断开销取决于多个因素：

**单次中断开销**：
```
最小开销（只设置标志）：
- 中断延迟：0.2-0.3μs
- ISR执行：<0.1μs
- 恢复时间：0.17μs
- 总计：<0.5μs

典型开销（读取数据）：
- 中断延迟：0.2-0.3μs
- ISR执行：0.5-1μs
- 恢复时间：0.17μs
- 总计：1-1.5μs
```

**频繁中断的影响**：
```
中断频率：1kHz
单次开销：1μs
总开销：1ms/s = 0.1% CPU占用

中断频率：10kHz
单次开销：1μs
总开销：10ms/s = 1% CPU占用

中断频率：100kHz
单次开销：1μs
总开销：100ms/s = 10% CPU占用
```

**建议**：
- 中断频率<10kHz：开销可忽略
- 中断频率10-100kHz：需要优化ISR
- 中断频率>100kHz：考虑使用DMA或轮询

### Q3: 如何在轮询和中断之间做出选择？

**A**: 使用以下决策树：

```
1. 事件频率是否>1kHz？
   是 → 使用轮询
   否 → 继续

2. 是否需要微秒级响应？
   是 → 使用中断
   否 → 继续

3. 是否需要低功耗？
   是 → 使用中断
   否 → 继续

4. 系统是否非常简单（<3个事件源）？
   是 → 可以使用轮询
   否 → 使用中断或混合策略

5. 是否有多个独立事件源？
   是 → 使用中断
   否 → 考虑混合策略
```

**实际应用示例**：

| 应用场景 | 推荐方案 | 原因 |
|---------|---------|------|
| 按键输入 | 轮询或中断 | 简单系统用轮询，低功耗用中断 |
| 串口通信 | 中断 | 不可预测，需要快速响应 |
| 高速ADC | 轮询或DMA | 频率高，中断开销大 |
| 定时任务 | 中断 | 精确定时，事件驱动 |
| 传感器读取 | 混合 | 中断触发，轮询处理 |
| 紧急停止 | 中断 | 需要最快响应 |

### Q4: 混合策略如何实现？

**A**: 混合策略的典型实现模式：

**模式1：中断触发 + 轮询处理**

```c
// 中断快速响应
volatile uint8_t event_pending = 0;

void IRQHandler(void)
{
    // 快速设置标志
    event_pending = 1;
}

// 主循环轮询处理
void main_loop(void)
{
    while (1) {
        if (event_pending) {
            event_pending = 0;
            // 复杂处理
            handle_event();
        }
        
        do_other_work();
    }
}
```

**模式2：定时中断 + 轮询检查**

```c
// 定时器控制轮询频率
volatile uint8_t poll_flag = 0;

void TIM_IRQHandler(void)
{
    poll_flag = 1;  // 每10ms设置一次
}

void main_loop(void)
{
    while (1) {
        if (poll_flag) {
            poll_flag = 0;
            // 轮询检查多个事件
            check_all_events();
        }
    }
}
```

**模式3：分层处理**

```c
// 高优先级：中断
void HIGH_PRIORITY_IRQHandler(void) {
    handle_critical_event();
}

// 中优先级：中断触发 + 标志
volatile uint8_t mid_flag = 0;
void MID_PRIORITY_IRQHandler(void) {
    mid_flag = 1;
}

// 低优先级：定时轮询
void main_loop(void)
{
    uint32_t last_poll = 0;
    
    while (1) {
        // 处理中优先级标志
        if (mid_flag) {
            mid_flag = 0;
            handle_mid_priority();
        }
        
        // 定时轮询低优先级
        if (HAL_GetTick() - last_poll >= 100) {
            last_poll = HAL_GetTick();
            check_low_priority();
        }
    }
}
```

### Q5: 如何测量和优化性能？

**A**: 性能测量和优化方法：

**1. 测量响应时间**

```c
// 使用GPIO标记
void measure_response_time(void)
{
    // 事件发生时拉高GPIO
    HAL_GPIO_WritePin(DEBUG_PORT, DEBUG_PIN, GPIO_PIN_SET);
}

void IRQHandler(void)
{
    // 响应时拉低GPIO
    HAL_GPIO_WritePin(DEBUG_PORT, DEBUG_PIN, GPIO_PIN_RESET);
    
    // 使用逻辑分析仪测量高电平持续时间
    // = 响应延迟
}
```

**2. 测量CPU占用**

```c
// 使用DWT计数器
void measure_cpu_usage(void)
{
    uint32_t start_cycles = DWT->CYCCNT;
    uint32_t start_time = HAL_GetTick();
    
    // 运行1秒
    while (HAL_GetTick() - start_time < 1000);
    
    uint32_t total_cycles = DWT->CYCCNT - start_cycles;
    uint32_t isr_cycles = get_isr_cycles();  // 累计ISR周期数
    
    float cpu_usage = ((float)isr_cycles / total_cycles) * 100;
    printf("CPU Usage: %.2f%%\n", cpu_usage);
}
```

**3. 优化建议**

```c
// 优化1：减少轮询频率
// 从1ms改为10ms，CPU占用降低10倍

// 优化2：使用DMA
// 减少中断频率，降低CPU占用

// 优化3：批量处理
// 累积多个事件后一次处理

// 优化4：缩短ISR
// 只在ISR中设置标志，主循环处理
```

## 总结

本文深入分析了中断和轮询两种事件处理机制，核心要点包括：

1. **轮询机制**
   - 主动检查，实现简单
   - CPU占用高，响应延迟大
   - 适合高频事件和简单系统

2. **中断机制**
   - 被动响应，快速高效
   - 实现复杂，有中断开销
   - 适合低频事件和实时系统

3. **性能对比**
   - 响应时间：中断微秒级，轮询毫秒级
   - CPU利用率：中断低，轮询高
   - 功耗：中断低，轮询高

4. **选择策略**
   - 根据事件频率、响应时间、功耗要求选择
   - 高频事件用轮询
   - 低频事件用中断
   - 复杂系统用混合策略

5. **混合策略**
   - 中断触发 + 轮询处理
   - 定时中断 + 轮询检查
   - 分层处理不同优先级事件

6. **最佳实践**
   - 合理设置轮询频率
   - 缩短ISR执行时间
   - 正确配置中断优先级
   - 使用DMA减少中断频率

掌握这些知识后，你就可以根据具体应用场景，选择最合适的事件处理机制，设计出高效、可靠的嵌入式系统。

## 延伸阅读

- [中断系统基础概念](../beginner/01-interrupt-basics.html) - 深入理解中断原理
- [中断优先级配置与抢占机制](01-interrupt-priority.html) - 学习优先级管理
- [中断安全与临界区保护](03-interrupt-safety.html) - 掌握中断安全编程

## 参考资料

1. "Embedded Systems Design" by Steve Heath
2. "Real-Time Systems Design and Analysis" by Phillip A. Laplante
3. ARM Cortex-M Programming Guide - ARM官方文档
4. "Making Embedded Systems" by Elecia White

---

**练习题**：

1. 分析你当前项目中的事件处理方式，是否可以优化？

2. 设计一个混合策略系统，包含：紧急按键（中断）、定时任务（中断）、温度监控（轮询）。

3. 测量你的系统中中断的CPU占用率，如果超过10%，如何优化？

4. 实现一个自适应轮询系统，根据事件频率动态调整轮询间隔。

5. 比较以下场景应该使用中断还是轮询：
   - 100Hz的ADC采样
   - 不定时的串口数据接收
   - 每秒一次的温度读取
   - 紧急停止按键
   - 1kHz的PWM更新

**下一步**：建议学习 [中断安全与临界区保护](03-interrupt-safety.html)，了解如何在中断环境下安全地访问共享资源。
