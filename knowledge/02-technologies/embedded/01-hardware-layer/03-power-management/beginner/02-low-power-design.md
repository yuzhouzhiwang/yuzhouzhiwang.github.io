---
# 基础信息
title: "低功耗设计技术入门"
description: "全面讲解嵌入式系统低功耗设计的基本原理和实践方法，包括睡眠模式、时钟门控、外设关闭、功耗测量和优化策略，帮助初学者掌握降低系统功耗的核心技术"
slug: "low-power-design-intro"

# 分类信息
domain: "01-hardware-layer"
module: "03-power-management"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 低功耗
  - 睡眠模式
  - 功耗优化
  - 时钟门控
  - 电池寿命
prerequisites:
  - "01-power-design-basics"
related_contents:
  - "03-battery-powered-system"
  - "04-power-monitoring"

# 学习信息
estimated_time: 60
difficulty_score: 3

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-03-07"
updated_at: "2026-03-07"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 低功耗设计
  - 睡眠模式
  - 功耗优化
  - 时钟管理
  - 电池寿命优化
cover_image: ""
---

# 低功耗设计技术入门

## 学习目标

完成本教程学习后，你将能够：

- [ ] 理解低功耗设计的基本原理和重要性
- [ ] 掌握MCU的各种睡眠模式及其应用场景
- [ ] 学会使用时钟门控技术降低功耗
- [ ] 能够正确关闭和管理外设以节省功耗
- [ ] 掌握功耗测量的方法和工具
- [ ] 能够制定和实施功耗优化策略
- [ ] 完成一个实际的低功耗应用项目


## 前置要求

在开始本教程学习之前，你需要：

**知识要求**：
- 了解嵌入式系统电源设计基础
- 熟悉MCU的基本工作原理
- 了解时钟系统和中断机制
- 掌握基本的C语言编程

**技能要求**：
- 能够使用开发环境编译和调试程序
- 会使用万用表测量电压和电流
- 了解示波器的基本使用方法

**硬件要求**：
- STM32开发板（或其他MCU开发板）
- USB转串口模块
- 万用表或电流表
- 面包板和杜邦线

**推荐但非必需**：
- 功率分析仪或电流探头
- 逻辑分析仪
- 有电池供电设备的使用经验

## 概述

低功耗设计是现代嵌入式系统，特别是电池供电设备的核心技术。随着物联网、可穿戴设备和移动设备的普及，低功耗设计变得越来越重要。

### 为什么需要低功耗设计

1. **延长电池寿命**：
   - 电池供电设备的核心需求
   - 减少充电频率，提升用户体验
   - 降低维护成本（如无线传感器网络）

2. **降低发热**：
   - 功耗直接转化为热量
   - 减少散热需求
   - 提高系统可靠性

3. **环保节能**：
   - 降低能源消耗
   - 减少碳排放
   - 符合绿色环保要求

4. **降低成本**：
   - 使用更小容量的电池
   - 减少散热器件
   - 降低电源系统成本

### 低功耗设计的基本原则

```
低功耗设计三大原则：
1. 不用的就关掉（Turn off what you don't use）
2. 降低工作频率（Slow down when possible）
3. 降低工作电压（Lower voltage when possible）

功耗公式：
P = C × V² × f
其中：
- P：功耗
- C：负载电容
- V：工作电压
- f：工作频率

可见：
- 电压降低一半，功耗降低75%
- 频率降低一半，功耗降低50%
```


## 第一部分：睡眠模式详解

### 什么是睡眠模式

睡眠模式是MCU的一种低功耗工作状态，通过关闭部分或全部功能模块来降低功耗。不同的睡眠模式提供不同程度的功耗降低和唤醒速度。

### STM32的睡眠模式

STM32系列MCU提供三种主要的低功耗模式：

#### 1. 睡眠模式（Sleep Mode）

**特点**：
- CPU停止运行
- 所有外设继续运行
- 所有寄存器和SRAM内容保持
- 唤醒速度最快

**功耗**：
- 典型值：几mA（取决于外设）
- 相比运行模式降低约30-50%

**适用场景**：
- 需要快速响应的应用
- 外设需要持续工作
- 短时间等待

**进入方式**：

```c
/**
 * @brief  进入睡眠模式
 * @note   使用WFI（Wait For Interrupt）指令
 */
void enter_sleep_mode(void) {
    printf("进入睡眠模式...\n");
    
    // 配置唤醒源（如外部中断、定时器等）
    // 这里以EXTI为例
    NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 进入睡眠模式
    __WFI();  // Wait For Interrupt
    
    // 被中断唤醒后，从这里继续执行
    printf("从睡眠模式唤醒！\n");
}

/**
 * @brief  外部中断处理函数（唤醒源）
 */
void EXTI0_IRQHandler(void) {
    if (EXTI_GetITStatus(EXTI_Line0) != RESET) {
        // 清除中断标志
        EXTI_ClearITPendingBit(EXTI_Line0);
        
        printf("外部中断触发，唤醒系统\n");
    }
}
```

#### 2. 停止模式（Stop Mode）

**特点**：
- CPU和大部分外设停止
- 1.2V域的时钟停止
- RTC、IWDG、唤醒单元继续工作
- 所有寄存器和SRAM内容保持
- 唤醒后需要重新配置时钟

**功耗**：
- 典型值：几十μA到几百μA
- 相比运行模式降低99%以上

**适用场景**：
- 长时间等待外部事件
- 需要保持数据
- 对唤醒时间要求不严格（ms级）

**进入方式**：

```c
/**
 * @brief  进入停止模式
 * @param  regulator: 稳压器模式
 *         @arg PWR_Regulator_ON: 稳压器开启
 *         @arg PWR_Regulator_LowPower: 稳压器低功耗模式
 */
void enter_stop_mode(uint32_t regulator) {
    printf("进入停止模式...\n");
    
    // 1. 配置唤醒源
    // 使用RTC闹钟唤醒（5秒后）
    RTC_AlarmTypeDef alarm;
    alarm.AlarmTime.Hours = 0;
    alarm.AlarmTime.Minutes = 0;
    alarm.AlarmTime.Seconds = 5;
    HAL_RTC_SetAlarm_IT(&hrtc, &alarm, RTC_FORMAT_BIN);
    
    // 2. 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // 3. 进入停止模式
    HAL_PWR_EnterSTOPMode(regulator, PWR_STOPENTRY_WFI);
    
    // 4. 唤醒后重新配置系统时钟
    SystemClock_Config();
    
    printf("从停止模式唤醒！\n");
}

/**
 * @brief  RTC闹钟中断处理函数
 */
void RTC_Alarm_IRQHandler(void) {
    HAL_RTC_AlarmIRQHandler(&hrtc);
}

/**
 * @brief  RTC闹钟回调函数
 */
void HAL_RTC_AlarmAEventCallback(RTC_HandleTypeDef *hrtc) {
    printf("RTC闹钟触发，唤醒系统\n");
}
```

#### 3. 待机模式（Standby Mode）

**特点**：
- 1.2V域断电
- 只有备份域和待机电路工作
- SRAM和寄存器内容丢失（除备份寄存器）
- 功耗最低
- 唤醒后相当于复位

**功耗**：
- 典型值：几μA
- 相比运行模式降低99.9%以上

**适用场景**：
- 长时间不工作
- 不需要保持数据（或使用备份寄存器）
- 对功耗要求极高

**进入方式**：

```c
/**
 * @brief  进入待机模式
 */
void enter_standby_mode(void) {
    printf("进入待机模式...\n");
    HAL_Delay(100);  // 等待串口发送完成
    
    // 1. 使能PWR时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    
    // 2. 配置唤醒引脚（PA0）
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // 3. 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // 4. 进入待机模式
    HAL_PWR_EnterSTANDBYMode();
    
    // 注意：唤醒后会从复位向量开始执行，不会返回这里
}

/**
 * @brief  检查是否从待机模式唤醒
 */
void check_standby_wakeup(void) {
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB) != RESET) {
        printf("从待机模式唤醒！\n");
        
        // 清除待机标志
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        
        // 清除唤醒标志
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    } else {
        printf("正常上电启动\n");
    }
}
```

### 睡眠模式对比

```c
/**
 * @brief  睡眠模式对比表
 */
typedef struct {
    char name[20];
    float current_ua;      // 电流（μA）
    float wakeup_time_us;  // 唤醒时间（μs）
    int keep_sram;         // 保持SRAM
    int keep_register;     // 保持寄存器
    char wakeup_source[50];
} SleepModeInfo;

void print_sleep_mode_comparison(void) {
    SleepModeInfo modes[] = {
        {"运行模式", 10000, 0, 1, 1, "N/A"},
        {"睡眠模式", 5000, 1, 1, 1, "任何中断"},
        {"停止模式", 50, 100, 1, 1, "EXTI, RTC, IWDG"},
        {"待机模式", 2, 1000, 0, 0, "WKUP引脚, RTC"}
    };
    
    printf("\n睡眠模式对比\n");
    printf("%-12s %10s %12s %8s %8s %20s\n",
           "模式", "电流(μA)", "唤醒(μs)", "SRAM", "寄存器", "唤醒源");
    printf("─────────────────────────────────────────────────────────────────────\n");
    
    for (int i = 0; i < 4; i++) {
        printf("%-12s %10.0f %12.0f %8s %8s %20s\n",
               modes[i].name,
               modes[i].current_ua,
               modes[i].wakeup_time_us,
               modes[i].keep_sram ? "保持" : "丢失",
               modes[i].keep_register ? "保持" : "丢失",
               modes[i].wakeup_source);
    }
}
```


## 第二部分：时钟门控技术

### 什么是时钟门控

时钟门控（Clock Gating）是一种通过关闭不使用的模块时钟来降低功耗的技术。由于动态功耗与时钟频率成正比，关闭时钟可以显著降低功耗。

**功耗公式**：
```
动态功耗 = C × V² × f × α
其中：
- C：负载电容
- V：工作电压
- f：时钟频率
- α：翻转率（0-1）

关闭时钟 → f = 0 → 功耗 = 0
```

### STM32时钟门控实现

#### 1. 外设时钟控制

**基本原理**：

```c
/**
 * @brief  外设时钟使能和关闭
 * @note   STM32通过RCC寄存器控制外设时钟
 */

// 使能外设时钟
void enable_peripheral_clock_example(void) {
    // 使能GPIOA时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 使能USART1时钟
    __HAL_RCC_USART1_CLK_ENABLE();
    
    // 使能TIM2时钟
    __HAL_RCC_TIM2_CLK_ENABLE();
    
    // 使能ADC1时钟
    __HAL_RCC_ADC1_CLK_ENABLE();
}

// 关闭外设时钟
void disable_peripheral_clock_example(void) {
    // 关闭USART1时钟（不使用时）
    __HAL_RCC_USART1_CLK_DISABLE();
    
    // 关闭TIM2时钟
    __HAL_RCC_TIM2_CLK_DISABLE();
    
    // 关闭ADC1时钟
    __HAL_RCC_ADC1_CLK_DISABLE();
    
    // 注意：GPIO时钟通常保持使能，因为可能有多个引脚在使用
}
```

#### 2. 动态时钟管理

**实现策略**：

```c
/**
 * @brief  外设时钟管理结构
 */
typedef struct {
    void (*enable_clock)(void);
    void (*disable_clock)(void);
    uint32_t usage_count;
    char name[20];
} PeripheralClock;

/**
 * @brief  USART1时钟管理
 */
PeripheralClock usart1_clock = {
    .enable_clock = __HAL_RCC_USART1_CLK_ENABLE,
    .disable_clock = __HAL_RCC_USART1_CLK_DISABLE,
    .usage_count = 0,
    .name = "USART1"
};

/**
 * @brief  请求使用外设（自动使能时钟）
 * @param  clk: 外设时钟结构
 */
void peripheral_clock_request(PeripheralClock *clk) {
    if (clk->usage_count == 0) {
        clk->enable_clock();
        printf("%s 时钟使能\n", clk->name);
    }
    clk->usage_count++;
}

/**
 * @brief  释放外设（自动关闭时钟）
 * @param  clk: 外设时钟结构
 */
void peripheral_clock_release(PeripheralClock *clk) {
    if (clk->usage_count > 0) {
        clk->usage_count--;
        if (clk->usage_count == 0) {
            clk->disable_clock();
            printf("%s 时钟关闭\n", clk->name);
        }
    }
}

// 使用示例
void clock_management_example(void) {
    // 模块A需要使用USART1
    peripheral_clock_request(&usart1_clock);
    // 使用USART1...
    
    // 模块B也需要使用USART1
    peripheral_clock_request(&usart1_clock);
    // 使用USART1...
    
    // 模块A使用完毕
    peripheral_clock_release(&usart1_clock);
    // USART1时钟仍然开启（模块B还在使用）
    
    // 模块B使用完毕
    peripheral_clock_release(&usart1_clock);
    // USART1时钟自动关闭（没有模块在使用）
}
```

#### 3. 时钟频率调整

**动态调频（DVFS）**：

```c
/**
 * @brief  系统时钟频率配置
 */
typedef enum {
    CLOCK_FREQ_LOW = 0,     // 低速：8MHz
    CLOCK_FREQ_MEDIUM = 1,  // 中速：36MHz
    CLOCK_FREQ_HIGH = 2     // 高速：72MHz
} ClockFrequency;

/**
 * @brief  设置系统时钟频率
 * @param  freq: 目标频率
 */
void set_system_clock_frequency(ClockFrequency freq) {
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    
    switch(freq) {
        case CLOCK_FREQ_LOW:
            printf("切换到低速模式：8MHz\n");
            // 配置为8MHz（HSI）
            RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
            RCC_OscInitStruct.HSIState = RCC_HSI_ON;
            RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
            
            RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | 
                                          RCC_CLOCKTYPE_SYSCLK |
                                          RCC_CLOCKTYPE_PCLK1 | 
                                          RCC_CLOCKTYPE_PCLK2;
            RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
            RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
            RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
            RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
            break;
            
        case CLOCK_FREQ_MEDIUM:
            printf("切换到中速模式：36MHz\n");
            // 配置为36MHz
            // ... 配置代码 ...
            break;
            
        case CLOCK_FREQ_HIGH:
            printf("切换到高速模式：72MHz\n");
            // 配置为72MHz
            // ... 配置代码 ...
            break;
    }
    
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0);
}

/**
 * @brief  根据负载动态调整频率
 * @param  load: 负载百分比（0-100）
 */
void dynamic_frequency_scaling(uint8_t load) {
    static ClockFrequency current_freq = CLOCK_FREQ_HIGH;
    ClockFrequency target_freq;
    
    // 根据负载选择频率
    if (load < 20) {
        target_freq = CLOCK_FREQ_LOW;
    } else if (load < 60) {
        target_freq = CLOCK_FREQ_MEDIUM;
    } else {
        target_freq = CLOCK_FREQ_HIGH;
    }
    
    // 如果频率需要改变
    if (target_freq != current_freq) {
        set_system_clock_frequency(target_freq);
        current_freq = target_freq;
        
        // 重新配置依赖时钟的外设（如UART波特率）
        reconfigure_peripherals();
    }
}
```

### 时钟门控最佳实践

```c
/**
 * @brief  低功耗时钟配置示例
 * @note   展示如何在不同场景下配置时钟
 */

// 场景1：初始化时只使能必要的时钟
void low_power_clock_init(void) {
    // 只使能必要的外设时钟
    __HAL_RCC_PWR_CLK_ENABLE();    // 电源控制
    __HAL_RCC_GPIOA_CLK_ENABLE();  // GPIO（按键、LED）
    __HAL_RCC_RTC_ENABLE();        // RTC（唤醒）
    
    // 不使能的外设：
    // - USART（需要时再使能）
    // - SPI（需要时再使能）
    // - ADC（需要时再使能）
    // - TIM（需要时再使能）
}

// 场景2：使用外设前使能时钟
void use_uart_with_clock_control(void) {
    // 使能UART时钟
    __HAL_RCC_USART1_CLK_ENABLE();
    
    // 初始化UART
    MX_USART1_UART_Init();
    
    // 发送数据
    HAL_UART_Transmit(&huart1, "Hello\n", 6, 100);
    
    // 使用完毕，关闭UART
    HAL_UART_DeInit(&huart1);
    
    // 关闭UART时钟
    __HAL_RCC_USART1_CLK_DISABLE();
}

// 场景3：进入睡眠前关闭所有可关闭的时钟
void prepare_for_sleep(void) {
    // 关闭所有外设时钟（除了唤醒源）
    __HAL_RCC_USART1_CLK_DISABLE();
    __HAL_RCC_SPI1_CLK_DISABLE();
    __HAL_RCC_TIM2_CLK_DISABLE();
    __HAL_RCC_ADC1_CLK_DISABLE();
    
    // 保持必要的时钟
    // - RTC（用于唤醒）
    // - GPIO（用于外部中断唤醒）
    
    printf("时钟已优化，准备进入睡眠\n");
}
```


## 第三部分：外设关闭策略

### 为什么要关闭外设

即使外设不工作，只要时钟使能，就会消耗功耗。正确关闭不使用的外设是低功耗设计的关键。

**功耗来源**：
```
外设功耗 = 静态功耗 + 动态功耗
- 静态功耗：漏电流（nA-μA级）
- 动态功耗：时钟翻转（μA-mA级）

关闭外设可以同时降低两种功耗
```

### 外设关闭方法

#### 1. GPIO配置

**低功耗GPIO配置**：

```c
/**
 * @brief  GPIO低功耗配置
 * @note   未使用的GPIO应配置为模拟输入模式
 */
void configure_gpio_for_low_power(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能所有GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // 配置所有未使用的GPIO为模拟输入模式（最低功耗）
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    
    // GPIOA未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // GPIOB未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    // GPIOC未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    printf("GPIO已配置为低功耗模式\n");
}

/**
 * @brief  配置使用中的GPIO
 * @note   只配置实际使用的引脚
 */
void configure_used_gpio(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // LED引脚（PA5）- 推挽输出
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;  // 低速以降低功耗
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 按键引脚（PA0）- 上拉输入
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿中断
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}
```

#### 2. 串口外设

**UART低功耗管理**：

```c
/**
 * @brief  UART外设低功耗管理
 */
typedef struct {
    UART_HandleTypeDef *huart;
    uint8_t is_active;
} UART_LowPower;

UART_LowPower uart1_lp = {
    .huart = &huart1,
    .is_active = 0
};

/**
 * @brief  使能UART（需要时）
 */
void uart_enable(UART_LowPower *uart_lp) {
    if (!uart_lp->is_active) {
        // 使能时钟
        __HAL_RCC_USART1_CLK_ENABLE();
        
        // 初始化UART
        HAL_UART_Init(uart_lp->huart);
        
        uart_lp->is_active = 1;
        printf("UART已使能\n");
    }
}

/**
 * @brief  关闭UART（不使用时）
 */
void uart_disable(UART_LowPower *uart_lp) {
    if (uart_lp->is_active) {
        // 等待发送完成
        while(__HAL_UART_GET_FLAG(uart_lp->huart, UART_FLAG_TC) == RESET);
        
        // 反初始化UART
        HAL_UART_DeInit(uart_lp->huart);
        
        // 关闭时钟
        __HAL_RCC_USART1_CLK_DISABLE();
        
        // 配置引脚为模拟模式
        GPIO_InitTypeDef GPIO_InitStruct = {0};
        GPIO_InitStruct.Pin = GPIO_PIN_9 | GPIO_PIN_10;  // TX, RX
        GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
        
        uart_lp->is_active = 0;
        // 注意：这里不能用printf，因为UART已关闭
    }
}

/**
 * @brief  使用UART发送数据（自动管理电源）
 */
void uart_send_with_power_management(const char *data, uint16_t len) {
    // 使能UART
    uart_enable(&uart1_lp);
    
    // 发送数据
    HAL_UART_Transmit(&huart1, (uint8_t*)data, len, 1000);
    
    // 关闭UART（可选：如果短时间内不再使用）
    // uart_disable(&uart1_lp);
}
```

#### 3. ADC外设

**ADC低功耗管理**：

```c
/**
 * @brief  ADC单次转换模式（低功耗）
 * @param  channel: ADC通道
 * @retval ADC转换结果
 */
uint16_t adc_single_conversion(uint32_t channel) {
    uint16_t adc_value;
    
    // 1. 使能ADC时钟
    __HAL_RCC_ADC1_CLK_ENABLE();
    
    // 2. 配置ADC
    ADC_HandleTypeDef hadc1;
    hadc1.Instance = ADC1;
    hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;  // 单次转换
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    HAL_ADC_Init(&hadc1);
    
    // 3. 配置通道
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = channel;
    sConfig.Rank = ADC_REGULAR_RANK_1;
    sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    
    // 4. 启动转换
    HAL_ADC_Start(&hadc1);
    
    // 5. 等待转换完成
    HAL_ADC_PollForConversion(&hadc1, 100);
    
    // 6. 读取结果
    adc_value = HAL_ADC_GetValue(&hadc1);
    
    // 7. 停止ADC
    HAL_ADC_Stop(&hadc1);
    
    // 8. 反初始化ADC
    HAL_ADC_DeInit(&hadc1);
    
    // 9. 关闭ADC时钟
    __HAL_RCC_ADC1_CLK_DISABLE();
    
    return adc_value;
}

/**
 * @brief  批量ADC转换（提高效率）
 * @param  channels: 通道数组
 * @param  count: 通道数量
 * @param  results: 结果数组
 */
void adc_batch_conversion(uint32_t *channels, uint8_t count, uint16_t *results) {
    // 使能ADC一次，转换多个通道
    __HAL_RCC_ADC1_CLK_ENABLE();
    
    // 初始化ADC
    ADC_HandleTypeDef hadc1;
    // ... 配置代码 ...
    
    // 转换所有通道
    for (uint8_t i = 0; i < count; i++) {
        // 配置通道
        ADC_ChannelConfTypeDef sConfig = {0};
        sConfig.Channel = channels[i];
        sConfig.Rank = ADC_REGULAR_RANK_1;
        sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;
        HAL_ADC_ConfigChannel(&hadc1, &sConfig);
        
        // 转换
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        results[i] = HAL_ADC_GetValue(&hadc1);
        HAL_ADC_Stop(&hadc1);
    }
    
    // 关闭ADC
    HAL_ADC_DeInit(&hadc1);
    __HAL_RCC_ADC1_CLK_DISABLE();
}
```

#### 4. 定时器外设

**定时器低功耗管理**：

```c
/**
 * @brief  定时器按需使用
 */

// 全局定时器句柄
TIM_HandleTypeDef htim2;
uint8_t tim2_active = 0;

/**
 * @brief  启动定时器
 * @param  period_ms: 定时周期（毫秒）
 */
void timer_start(uint32_t period_ms) {
    if (!tim2_active) {
        // 使能时钟
        __HAL_RCC_TIM2_CLK_ENABLE();
        
        // 配置定时器
        htim2.Instance = TIM2;
        htim2.Init.Prescaler = 7200 - 1;  // 72MHz / 7200 = 10kHz
        htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
        htim2.Init.Period = period_ms * 10 - 1;  // 10kHz * ms
        htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
        HAL_TIM_Base_Init(&htim2);
        
        // 启动定时器中断
        HAL_TIM_Base_Start_IT(&htim2);
        
        tim2_active = 1;
        printf("定时器已启动：%lu ms\n", period_ms);
    }
}

/**
 * @brief  停止定时器
 */
void timer_stop(void) {
    if (tim2_active) {
        // 停止定时器
        HAL_TIM_Base_Stop_IT(&htim2);
        
        // 反初始化
        HAL_TIM_Base_DeInit(&htim2);
        
        // 关闭时钟
        __HAL_RCC_TIM2_CLK_DISABLE();
        
        tim2_active = 0;
        printf("定时器已停止\n");
    }
}

/**
 * @brief  定时器中断回调
 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        // 定时任务
        printf("定时器触发\n");
        
        // 如果是一次性任务，可以停止定时器
        // timer_stop();
    }
}
```

### 外设关闭检查清单

```c
/**
 * @brief  进入低功耗模式前的外设检查
 * @retval 0: 可以进入低功耗，1: 有外设正在使用
 */
uint8_t check_peripherals_before_sleep(void) {
    uint8_t busy = 0;
    
    printf("\n外设状态检查：\n");
    
    // 检查UART
    if (__HAL_RCC_USART1_IS_CLK_ENABLED()) {
        if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC) == RESET) {
            printf("  [×] UART正在发送数据\n");
            busy = 1;
        } else {
            printf("  [√] UART空闲\n");
        }
    } else {
        printf("  [√] UART已关闭\n");
    }
    
    // 检查SPI
    if (__HAL_RCC_SPI1_IS_CLK_ENABLED()) {
        if (__HAL_SPI_GET_FLAG(&hspi1, SPI_FLAG_BSY)) {
            printf("  [×] SPI正在传输\n");
            busy = 1;
        } else {
            printf("  [√] SPI空闲\n");
        }
    } else {
        printf("  [√] SPI已关闭\n");
    }
    
    // 检查ADC
    if (__HAL_RCC_ADC1_IS_CLK_ENABLED()) {
        printf("  [!] ADC时钟使能（建议关闭）\n");
    } else {
        printf("  [√] ADC已关闭\n");
    }
    
    // 检查定时器
    if (__HAL_RCC_TIM2_IS_CLK_ENABLED()) {
        printf("  [!] TIM2时钟使能\n");
    } else {
        printf("  [√] TIM2已关闭\n");
    }
    
    return busy;
}
```


## 第四部分：功耗测量方法

### 为什么要测量功耗

"不能测量就不能改进"。功耗测量是低功耗设计的重要环节，可以：

1. **验证设计**：确认功耗是否达到目标
2. **发现问题**：找出功耗异常的模块
3. **优化指导**：为优化提供数据支持
4. **性能评估**：评估不同方案的效果

### 功耗测量工具

#### 1. 万用表测量

**适用场景**：
- 稳态功耗测量
- 平均功耗估算
- 简单快速的验证

**测量方法**：

```
测量步骤：
1. 断开电源
2. 将万用表串联在电源回路中
3. 选择合适的电流档位（mA或μA）
4. 上电，读取电流值
5. 计算功耗：P = V × I

注意事项：
- 万用表有内阻，会影响测量
- 无法测量瞬态电流
- 精度有限（通常±1%）
```

**实际操作**：

```c
/**
 * @brief  功耗测量辅助函数
 * @note   在不同状态下测量功耗
 */
void measure_power_consumption(void) {
    printf("\n=== 功耗测量 ===\n");
    printf("请使用万用表测量电流\n\n");
    
    // 测试1：运行模式
    printf("测试1：运行模式（全速运行）\n");
    printf("  - 系统时钟：72MHz\n");
    printf("  - 所有外设使能\n");
    printf("  - 请记录电流值：_____ mA\n");
    HAL_Delay(5000);  // 保持5秒以便测量
    
    // 测试2：空闲模式
    printf("\n测试2：空闲模式（降低时钟）\n");
    set_system_clock_frequency(CLOCK_FREQ_LOW);  // 8MHz
    printf("  - 系统时钟：8MHz\n");
    printf("  - 关闭不必要的外设\n");
    printf("  - 请记录电流值：_____ mA\n");
    HAL_Delay(5000);
    
    // 测试3：睡眠模式
    printf("\n测试3：睡眠模式\n");
    printf("  - CPU停止\n");
    printf("  - 外设运行\n");
    printf("  - 请记录电流值：_____ mA\n");
    printf("  - 5秒后自动唤醒\n");
    HAL_Delay(1000);
    // 配置定时器5秒后唤醒
    // ... 进入睡眠 ...
    
    // 测试4：停止模式
    printf("\n测试4：停止模式\n");
    printf("  - CPU和大部分外设停止\n");
    printf("  - 请记录电流值：_____ μA\n");
    printf("  - 10秒后自动唤醒\n");
    HAL_Delay(1000);
    // ... 进入停止模式 ...
    
    // 测试5：待机模式
    printf("\n测试5：待机模式\n");
    printf("  - 最低功耗模式\n");
    printf("  - 请记录电流值：_____ μA\n");
    printf("  - 按WKUP键唤醒\n");
    HAL_Delay(1000);
    // ... 进入待机模式 ...
}
```

#### 2. 示波器 + 电流探头

**适用场景**：
- 动态功耗测量
- 瞬态电流分析
- 功耗波形观察

**测量方法**：

```
测量步骤：
1. 使用电流探头夹在电源线上
2. 连接到示波器
3. 设置合适的时基和电流档位
4. 观察电流波形
5. 使用示波器的测量功能获取参数

可测量参数：
- 峰值电流
- 平均电流
- RMS电流
- 电流波形
- 瞬态响应
```

#### 3. 功率分析仪

**适用场景**：
- 精确功耗测量
- 长时间功耗记录
- 复杂功耗分析

**推荐设备**：
- Nordic PPK2（Power Profiler Kit II）
- Joulescope
- Keysight N6705C

**使用示例（Nordic PPK2）**：

```c
/**
 * @brief  使用PPK2进行功耗分析
 * @note   在代码中添加标记，便于在PPK2中识别
 */

// 使用GPIO输出标记不同的工作状态
#define MARKER_PIN GPIO_PIN_6

void power_profiling_with_markers(void) {
    // 标记1：运行模式开始
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_SET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_RESET);
    
    // 运行模式工作
    for (int i = 0; i < 1000; i++) {
        // 执行一些任务
    }
    HAL_Delay(1000);
    
    // 标记2：进入睡眠模式
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_SET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_RESET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_SET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(GPIOA, MARKER_PIN, GPIO_PIN_RESET);
    
    // 进入睡眠
    enter_sleep_mode();
}
```

### 功耗计算方法

#### 1. 平均功耗计算

```c
/**
 * @brief  计算平均功耗
 * @param  states: 工作状态数组
 * @param  count: 状态数量
 * @retval 平均功耗（W）
 */
typedef struct {
    char name[30];
    float current_ma;    // 电流（mA）
    float duration_s;    // 持续时间（s）
    float voltage_v;     // 电压（V）
} PowerState;

float calculate_average_power(PowerState *states, uint8_t count) {
    float total_energy = 0;  // 总能量（J）
    float total_time = 0;    // 总时间（s）
    
    printf("\n平均功耗计算\n");
    printf("%-20s %10s %10s %10s %12s\n",
           "状态", "电流(mA)", "时间(s)", "电压(V)", "能量(mJ)");
    printf("────────────────────────────────────────────────────────────\n");
    
    for (uint8_t i = 0; i < count; i++) {
        // 计算能量：E = P × t = V × I × t
        float energy = states[i].voltage_v * 
                      (states[i].current_ma / 1000.0) * 
                      states[i].duration_s;
        
        total_energy += energy;
        total_time += states[i].duration_s;
        
        printf("%-20s %10.2f %10.2f %10.2f %12.2f\n",
               states[i].name,
               states[i].current_ma,
               states[i].duration_s,
               states[i].voltage_v,
               energy * 1000);  // 转换为mJ
    }
    
    float avg_power = total_energy / total_time;
    float avg_current = (avg_power / states[0].voltage_v) * 1000;  // mA
    
    printf("────────────────────────────────────────────────────────────\n");
    printf("总时间: %.2f s\n", total_time);
    printf("总能量: %.2f mJ\n", total_energy * 1000);
    printf("平均功耗: %.3f W = %.2f mW\n", avg_power, avg_power * 1000);
    printf("平均电流: %.2f mA\n", avg_current);
    
    return avg_power;
}

// 使用示例
void power_calculation_example(void) {
    PowerState states[] = {
        {"深度睡眠", 0.002, 50.0, 3.3},   // 2μA, 50s
        {"待机", 0.010, 5.0, 3.3},         // 10μA, 5s
        {"工作", 50.0, 4.0, 3.3},          // 50mA, 4s
        {"峰值", 200.0, 1.0, 3.3}          // 200mA, 1s
    };
    
    float avg_power = calculate_average_power(states, 4);
    
    // 计算电池寿命
    float battery_capacity = 2000;  // mAh
    float avg_current = (avg_power / 3.3) * 1000;  // mA
    float battery_life_hours = battery_capacity / avg_current;
    
    printf("\n电池寿命估算（2000mAh电池）：\n");
    printf("  理论寿命: %.1f 小时 = %.1f 天\n",
           battery_life_hours, battery_life_hours / 24);
}
```

#### 2. 实时功耗监控

```c
/**
 * @brief  实时功耗监控（使用ADC测量电流）
 * @note   通过测量电流采样电阻上的压降计算电流
 */

#define SHUNT_RESISTOR 0.1  // 采样电阻：0.1Ω
#define ADC_VREF 3.3        // ADC参考电压：3.3V
#define ADC_RESOLUTION 4096 // 12位ADC

/**
 * @brief  读取当前电流
 * @retval 电流值（mA）
 */
float read_current(void) {
    // 读取ADC值
    uint16_t adc_value = adc_single_conversion(ADC_CHANNEL_0);
    
    // 计算电压
    float voltage = (float)adc_value * ADC_VREF / ADC_RESOLUTION;
    
    // 计算电流：I = V / R
    float current = voltage / SHUNT_RESISTOR;
    
    // 转换为mA
    return current * 1000;
}

/**
 * @brief  功耗监控任务
 */
void power_monitoring_task(void) {
    static uint32_t sample_count = 0;
    static float total_current = 0;
    
    // 读取当前电流
    float current = read_current();
    
    // 累加
    total_current += current;
    sample_count++;
    
    // 每10秒输出一次
    if (sample_count >= 1000) {  // 假设10ms采样一次
        float avg_current = total_current / sample_count;
        float power = avg_current * 3.3 / 1000;  // W
        
        printf("平均电流: %.2f mA, 功耗: %.2f mW\n",
               avg_current, power * 1000);
        
        // 重置
        total_current = 0;
        sample_count = 0;
    }
}
```

### 功耗测量最佳实践

```c
/**
 * @brief  功耗测量检查清单
 */
void power_measurement_checklist(void) {
    printf("\n功耗测量检查清单：\n\n");
    
    printf("测量前准备：\n");
    printf("  □ 确认测量工具精度满足要求\n");
    printf("  □ 校准测量设备\n");
    printf("  □ 准备记录表格\n");
    printf("  □ 了解预期功耗范围\n\n");
    
    printf("测量过程：\n");
    printf("  □ 断开调试器（避免额外功耗）\n");
    printf("  □ 使用稳定的电源\n");
    printf("  □ 等待系统稳定后测量\n");
    printf("  □ 多次测量取平均值\n");
    printf("  □ 记录环境温度\n\n");
    
    printf("测量内容：\n");
    printf("  □ 运行模式功耗\n");
    printf("  □ 睡眠模式功耗\n");
    printf("  □ 停止模式功耗\n");
    printf("  □ 待机模式功耗\n");
    printf("  □ 峰值电流\n");
    printf("  □ 平均电流\n\n");
    
    printf("数据分析：\n");
    printf("  □ 对比设计目标\n");
    printf("  □ 分析异常数据\n");
    printf("  □ 计算电池寿命\n");
    printf("  □ 识别优化空间\n");
}
```


## 第五部分：功耗优化策略

### 系统级优化策略

#### 1. 工作周期优化

**间歇工作模式**：

```c
/**
 * @brief  间歇工作模式实现
 * @note   工作一段时间，然后睡眠，周期性重复
 */

#define WORK_DURATION_MS 100    // 工作时间：100ms
#define SLEEP_DURATION_MS 9900  // 睡眠时间：9900ms
// 占空比：1%

void intermittent_work_mode(void) {
    while (1) {
        // 工作阶段
        printf("开始工作...\n");
        
        // 执行任务
        read_sensors();
        process_data();
        send_data();
        
        printf("工作完成，进入睡眠\n");
        
        // 睡眠阶段
        // 配置RTC在9.9秒后唤醒
        configure_rtc_wakeup(SLEEP_DURATION_MS);
        
        // 进入停止模式
        enter_stop_mode(PWR_Regulator_LowPower);
        
        // 被唤醒后继续下一个周期
        printf("唤醒，开始新周期\n");
    }
}

/**
 * @brief  计算间歇工作模式的功耗
 */
void calculate_intermittent_power(void) {
    float work_current = 50.0;    // 工作电流：50mA
    float sleep_current = 0.05;   // 睡眠电流：50μA
    float work_time = 0.1;        // 工作时间：0.1s
    float sleep_time = 9.9;       // 睡眠时间：9.9s
    float voltage = 3.3;          // 电压：3.3V
    
    // 计算平均电流
    float avg_current = (work_current * work_time + 
                        sleep_current * sleep_time) / 
                       (work_time + sleep_time);
    
    // 计算平均功耗
    float avg_power = avg_current * voltage / 1000;  // W
    
    printf("\n间歇工作模式功耗分析：\n");
    printf("工作电流: %.1f mA, 时间: %.1f s\n", work_current, work_time);
    printf("睡眠电流: %.2f mA, 时间: %.1f s\n", sleep_current, sleep_time);
    printf("占空比: %.1f%%\n", work_time / (work_time + sleep_time) * 100);
    printf("平均电流: %.2f mA\n", avg_current);
    printf("平均功耗: %.2f mW\n", avg_power * 1000);
    printf("节能: %.1f%%\n", (1 - avg_current / work_current) * 100);
    
    // 电池寿命
    float battery_capacity = 2000;  // mAh
    float battery_life = battery_capacity / avg_current / 24;  // 天
    printf("电池寿命: %.1f 天\n", battery_life);
}
```

#### 2. 事件驱动架构

**中断驱动 vs 轮询**：

```c
/**
 * @brief  轮询方式（高功耗）
 */
void polling_method(void) {
    while (1) {
        // 持续检查按键状态
        if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET) {
            printf("按键按下\n");
            handle_button_press();
        }
        
        // CPU一直运行，功耗高
        HAL_Delay(10);  // 10ms轮询间隔
    }
}

/**
 * @brief  中断驱动方式（低功耗）
 */
void interrupt_driven_method(void) {
    // 配置按键中断
    configure_button_interrupt();
    
    while (1) {
        // 进入睡眠，等待中断唤醒
        enter_sleep_mode();
        
        // 被中断唤醒后处理事件
        if (button_pressed_flag) {
            printf("按键按下\n");
            handle_button_press();
            button_pressed_flag = 0;
        }
    }
}

/**
 * @brief  按键中断处理函数
 */
void EXTI0_IRQHandler(void) {
    if (EXTI_GetITStatus(EXTI_Line0) != RESET) {
        button_pressed_flag = 1;
        EXTI_ClearITPendingBit(EXTI_Line0);
    }
}

/**
 * @brief  对比两种方法的功耗
 */
void compare_polling_vs_interrupt(void) {
    printf("\n轮询 vs 中断驱动功耗对比：\n\n");
    
    printf("轮询方式：\n");
    printf("  - CPU持续运行\n");
    printf("  - 电流：~50mA\n");
    printf("  - 响应延迟：10ms\n");
    printf("  - 功耗：165mW @ 3.3V\n\n");
    
    printf("中断驱动：\n");
    printf("  - CPU大部分时间睡眠\n");
    printf("  - 电流：~5mA（睡眠）+ 50mA（处理，<1%%时间）\n");
    printf("  - 平均电流：~5.5mA\n");
    printf("  - 响应延迟：<1ms\n");
    printf("  - 功耗：18mW @ 3.3V\n");
    printf("  - 节能：89%%\n");
}
```

#### 3. 数据缓存策略

**批量处理 vs 实时处理**：

```c
/**
 * @brief  数据缓存结构
 */
#define BUFFER_SIZE 100

typedef struct {
    uint16_t data[BUFFER_SIZE];
    uint16_t count;
    uint32_t timestamp[BUFFER_SIZE];
} DataBuffer;

DataBuffer sensor_buffer = {0};

/**
 * @brief  实时发送方式（高功耗）
 */
void realtime_send_method(void) {
    while (1) {
        // 读取传感器
        uint16_t data = read_sensor();
        
        // 立即发送
        uart_enable(&uart1_lp);
        send_data_via_uart(data);
        uart_disable(&uart1_lp);
        
        // 每次都要使能/关闭UART，开销大
        HAL_Delay(1000);
    }
}

/**
 * @brief  批量发送方式（低功耗）
 */
void batch_send_method(void) {
    while (1) {
        // 读取传感器并缓存
        uint16_t data = read_sensor();
        sensor_buffer.data[sensor_buffer.count] = data;
        sensor_buffer.timestamp[sensor_buffer.count] = HAL_GetTick();
        sensor_buffer.count++;
        
        // 缓存满了才发送
        if (sensor_buffer.count >= BUFFER_SIZE) {
            printf("缓存已满，批量发送\n");
            
            // 使能UART一次
            uart_enable(&uart1_lp);
            
            // 批量发送所有数据
            for (uint16_t i = 0; i < sensor_buffer.count; i++) {
                send_data_via_uart(sensor_buffer.data[i]);
            }
            
            // 关闭UART
            uart_disable(&uart1_lp);
            
            // 清空缓存
            sensor_buffer.count = 0;
            
            printf("发送完成\n");
        }
        
        HAL_Delay(1000);
    }
}

/**
 * @brief  对比两种方法
 */
void compare_realtime_vs_batch(void) {
    printf("\n实时发送 vs 批量发送功耗对比：\n\n");
    
    printf("实时发送（每秒1次）：\n");
    printf("  - UART使能/关闭：100次/100秒\n");
    printf("  - 每次开销：~10ms\n");
    printf("  - 总开销：1秒/100秒 = 1%%\n");
    printf("  - 额外功耗：~0.5mA\n\n");
    
    printf("批量发送（100秒1次）：\n");
    printf("  - UART使能/关闭：1次/100秒\n");
    printf("  - 每次开销：~1秒（发送100个数据）\n");
    printf("  - 总开销：1秒/100秒 = 1%%\n");
    printf("  - 额外功耗：~0.5mA\n");
    printf("  - 但减少了99次使能/关闭的开销\n");
    printf("  - 实际节能：~20%%\n");
}
```

### 硬件级优化策略

#### 1. 电压优化

```c
/**
 * @brief  动态电压调整（DVS）
 * @note   根据性能需求调整电压
 */

typedef enum {
    VOLTAGE_LOW = 0,     // 低电压：降低功耗
    VOLTAGE_NORMAL = 1,  // 正常电压
    VOLTAGE_HIGH = 2     // 高电压：提高性能
} VoltageLevel;

/**
 * @brief  设置工作电压
 * @param  level: 电压等级
 * @note   需要硬件支持（如PMIC）
 */
void set_voltage_level(VoltageLevel level) {
    switch(level) {
        case VOLTAGE_LOW:
            // 设置为1.8V（示例）
            printf("设置电压：1.8V（低功耗模式）\n");
            // 通过I2C配置PMIC
            // pmic_set_voltage(1.8);
            break;
            
        case VOLTAGE_NORMAL:
            // 设置为3.0V
            printf("设置电压：3.0V（正常模式）\n");
            // pmic_set_voltage(3.0);
            break;
            
        case VOLTAGE_HIGH:
            // 设置为3.3V
            printf("设置电压：3.3V（高性能模式）\n");
            // pmic_set_voltage(3.3);
            break;
    }
}

/**
 * @brief  电压对功耗的影响
 * @note   P = C × V² × f
 */
void voltage_power_relationship(void) {
    float capacitance = 100e-12;  // 100pF
    float frequency = 72e6;       // 72MHz
    
    printf("\n电压对功耗的影响（C=100pF, f=72MHz）：\n\n");
    
    float voltages[] = {1.8, 2.5, 3.0, 3.3};
    
    for (int i = 0; i < 4; i++) {
        float v = voltages[i];
        float power = capacitance * v * v * frequency;
        
        printf("电压 %.1fV: 功耗 %.2f mW\n", v, power * 1000);
        
        if (i > 0) {
            float saving = (1 - power / 
                          (capacitance * voltages[0] * voltages[0] * frequency)) * 100;
            printf("  相比%.1fV节能: %.1f%%\n", voltages[0], -saving);
        }
    }
}
```

#### 2. 外部器件优化

```c
/**
 * @brief  外部器件功耗优化建议
 */
void external_device_optimization(void) {
    printf("\n外部器件功耗优化建议：\n\n");
    
    printf("1. LED指示灯：\n");
    printf("   - 使用高效LED（低正向电压）\n");
    printf("   - 增大限流电阻（降低亮度）\n");
    printf("   - 使用PWM调光（降低平均功耗）\n");
    printf("   - 不使用时完全关闭\n");
    printf("   - 典型功耗：2-20mA → 优化后：0.5-5mA\n\n");
    
    printf("2. 上拉/下拉电阻：\n");
    printf("   - 使用MCU内部上拉（节省外部电阻）\n");
    printf("   - 增大电阻值（降低漏电流）\n");
    printf("   - 典型值：10kΩ → 优化：100kΩ\n");
    printf("   - 功耗降低：10倍\n\n");
    
    printf("3. 传感器：\n");
    printf("   - 选择低功耗传感器\n");
    printf("   - 使用电源控制引脚\n");
    printf("   - 不使用时完全断电\n");
    printf("   - 降低采样频率\n");
    printf("   - 典型功耗：1-10mA → 优化后：<100μA\n\n");
    
    printf("4. 无线模块：\n");
    printf("   - 使用低功耗模式\n");
    printf("   - 降低发射功率\n");
    printf("   - 减少通信频率\n");
    printf("   - 使用睡眠模式\n");
    printf("   - 典型功耗：50-200mA → 优化后：<1mA\n");
}
```

### 软件级优化策略

```c
/**
 * @brief  代码优化建议
 */
void code_optimization_tips(void) {
    printf("\n代码优化建议：\n\n");
    
    printf("1. 减少循环和计算：\n");
    printf("   - 避免不必要的循环\n");
    printf("   - 使用查表代替计算\n");
    printf("   - 优化算法复杂度\n");
    printf("   - 使用硬件加速（如DMA）\n\n");
    
    printf("2. 优化数据结构：\n");
    printf("   - 使用合适的数据类型\n");
    printf("   - 减少内存访问\n");
    printf("   - 利用缓存局部性\n");
    printf("   - 对齐数据结构\n\n");
    
    printf("3. 减少中断：\n");
    printf("   - 合并多个中断\n");
    printf("   - 使用DMA代替中断\n");
    printf("   - 降低中断优先级\n");
    printf("   - 批量处理中断\n\n");
    
    printf("4. 优化外设使用：\n");
    printf("   - 按需使能外设\n");
    printf("   - 使用低功耗模式\n");
    printf("   - 共享外设资源\n");
    printf("   - 及时关闭外设\n");
}

/**
 * @brief  低功耗编程模式
 */
void low_power_programming_pattern(void) {
    // 模式1：资源获取即初始化（RAII）
    void task_with_uart(void) {
        // 获取资源
        uart_enable(&uart1_lp);
        
        // 使用资源
        send_data("Hello");
        
        // 释放资源
        uart_disable(&uart1_lp);
    }
    
    // 模式2：作用域保护
    void task_with_scope_guard(void) {
        // 进入临界区
        __disable_irq();
        
        // 执行任务
        critical_section_code();
        
        // 退出临界区
        __enable_irq();
    }
    
    // 模式3：状态机
    typedef enum {
        STATE_SLEEP,
        STATE_WAKEUP,
        STATE_WORK,
        STATE_IDLE
    } SystemState;
    
    void state_machine(void) {
        static SystemState state = STATE_SLEEP;
        
        switch(state) {
            case STATE_SLEEP:
                enter_sleep_mode();
                state = STATE_WAKEUP;
                break;
                
            case STATE_WAKEUP:
                system_init();
                state = STATE_WORK;
                break;
                
            case STATE_WORK:
                do_work();
                state = STATE_IDLE;
                break;
                
            case STATE_IDLE:
                if (work_done()) {
                    state = STATE_SLEEP;
                }
                break;
        }
    }
}
```


## 第六部分：实战项目 - 低功耗温度记录器

### 项目需求

设计一个低功耗温度记录器，要求：

1. **功能需求**：
   - 每10分钟采集一次温度
   - 存储最近100个数据点
   - 通过按键可以查看数据
   - LED指示工作状态

2. **功耗需求**：
   - 使用2节AA电池（3V，2000mAh）
   - 目标寿命：6个月（180天）
   - 允许平均电流：≤0.46mA

### 项目设计

#### 1. 硬件选型

```c
/**
 * @brief  硬件清单
 */
void hardware_list(void) {
    printf("硬件清单：\n\n");
    
    printf("1. MCU: STM32L051（超低功耗）\n");
    printf("   - 运行：~1mA @ 2MHz\n");
    printf("   - 停止：~0.5μA\n");
    printf("   - 待机：~0.3μA\n\n");
    
    printf("2. 温度传感器: DS18B20\n");
    printf("   - 工作：~1mA\n");
    printf("   - 待机：~1μA\n");
    printf("   - 转换时间：750ms\n\n");
    
    printf("3. 存储: 内部Flash\n");
    printf("   - 无额外功耗\n\n");
    
    printf("4. 显示: 无（通过串口输出）\n\n");
    
    printf("5. 按键: 1个（外部中断唤醒）\n\n");
    
    printf("6. LED: 1个（可选，低功耗模式）\n");
}
```

#### 2. 功耗预算

```c
/**
 * @brief  功耗预算分析
 */
void power_budget_analysis(void) {
    printf("\n功耗预算分析：\n\n");
    
    // 工作周期：10分钟 = 600秒
    float cycle_time = 600.0;  // s
    
    // 各阶段功耗
    float sleep_current = 0.0005;  // 0.5μA
    float wakeup_current = 1.0;    // 1mA
    float measure_current = 2.0;   // 2mA（MCU + 传感器）
    float store_current = 5.0;     // 5mA（Flash写入）
    
    // 各阶段时间
    float sleep_time = 599.0;      // 599s
    float wakeup_time = 0.1;       // 0.1s
    float measure_time = 0.8;      // 0.8s（传感器转换）
    float store_time = 0.1;        // 0.1s
    
    // 计算平均电流
    float avg_current = (sleep_current * sleep_time +
                        wakeup_current * wakeup_time +
                        measure_current * measure_time +
                        store_current * store_time) / cycle_time;
    
    printf("工作周期：%.0f 秒\n\n", cycle_time);
    
    printf("%-15s %10s %10s %12s\n", "阶段", "电流(mA)", "时间(s)", "电荷(mAs)");
    printf("───────────────────────────────────────────────\n");
    printf("%-15s %10.4f %10.1f %12.4f\n", "睡眠", sleep_current, sleep_time, 
           sleep_current * sleep_time);
    printf("%-15s %10.2f %10.1f %12.2f\n", "唤醒", wakeup_current, wakeup_time,
           wakeup_current * wakeup_time);
    printf("%-15s %10.2f %10.1f %12.2f\n", "测量", measure_current, measure_time,
           measure_current * measure_time);
    printf("%-15s %10.2f %10.1f %12.2f\n", "存储", store_current, store_time,
           store_current * store_time);
    printf("───────────────────────────────────────────────\n");
    
    printf("\n平均电流：%.3f mA\n", avg_current);
    printf("目标电流：≤0.46 mA\n");
    
    if (avg_current <= 0.46) {
        printf("✓ 满足功耗要求！\n");
    } else {
        printf("✗ 超出功耗预算 %.2f%%\n", 
               (avg_current / 0.46 - 1) * 100);
    }
    
    // 计算电池寿命
    float battery_capacity = 2000;  // mAh
    float battery_life_hours = battery_capacity / avg_current;
    float battery_life_days = battery_life_hours / 24;
    
    printf("\n电池寿命：%.0f 小时 = %.0f 天\n",
           battery_life_hours, battery_life_days);
}
```

#### 3. 软件实现

```c
/**
 * @brief  温度数据结构
 */
#define MAX_RECORDS 100

typedef struct {
    uint16_t temperature;  // 温度 × 10（如25.6°C存储为256）
    uint32_t timestamp;    // 时间戳
} TempRecord;

typedef struct {
    TempRecord records[MAX_RECORDS];
    uint16_t count;
    uint16_t write_index;
} TempDataBuffer;

TempDataBuffer temp_buffer = {0};

/**
 * @brief  主程序
 */
int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();  // 配置为低功耗时钟
    
    // 外设初始化
    GPIO_Init();
    RTC_Init();
    
    // 配置GPIO为低功耗模式
    configure_gpio_for_low_power();
    
    // 配置唤醒源
    configure_wakeup_sources();
    
    printf("温度记录器启动\n");
    printf("目标：每10分钟记录一次温度\n");
    
    while (1) {
        // 采集温度
        float temperature = read_temperature();
        
        // 存储数据
        store_temperature(temperature);
        
        printf("温度：%.1f°C，已存储\n", temperature);
        
        // 配置RTC在10分钟后唤醒
        configure_rtc_wakeup(600);  // 600秒 = 10分钟
        
        // 进入停止模式
        printf("进入睡眠模式...\n");
        HAL_Delay(100);  // 等待串口发送完成
        
        enter_stop_mode(PWR_Regulator_LowPower);
        
        // 被唤醒
        SystemClock_Config();  // 恢复时钟
        printf("唤醒！\n");
    }
}

/**
 * @brief  读取温度
 * @retval 温度值（°C）
 */
float read_temperature(void) {
    // 使能传感器电源（如果有控制引脚）
    // HAL_GPIO_WritePin(SENSOR_PWR_GPIO, SENSOR_PWR_PIN, GPIO_PIN_SET);
    // HAL_Delay(10);  // 等待传感器稳定
    
    // 读取DS18B20
    float temperature = ds18b20_read_temperature();
    
    // 关闭传感器电源
    // HAL_GPIO_WritePin(SENSOR_PWR_GPIO, SENSOR_PWR_PIN, GPIO_PIN_RESET);
    
    return temperature;
}

/**
 * @brief  存储温度数据
 * @param  temperature: 温度值
 */
void store_temperature(float temperature) {
    // 转换为整数（×10）
    uint16_t temp_int = (uint16_t)(temperature * 10);
    
    // 存储到缓冲区
    temp_buffer.records[temp_buffer.write_index].temperature = temp_int;
    temp_buffer.records[temp_buffer.write_index].timestamp = HAL_GetTick();
    
    // 更新索引（循环缓冲区）
    temp_buffer.write_index = (temp_buffer.write_index + 1) % MAX_RECORDS;
    
    // 更新计数
    if (temp_buffer.count < MAX_RECORDS) {
        temp_buffer.count++;
    }
    
    // 每10个数据点写入Flash（减少Flash写入次数）
    if (temp_buffer.count % 10 == 0) {
        save_to_flash();
    }
}

/**
 * @brief  配置唤醒源
 */
void configure_wakeup_sources(void) {
    // 1. RTC唤醒（定时唤醒）
    // 已在main函数中配置
    
    // 2. 按键唤醒（外部中断）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI0_1_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_1_IRQn);
}

/**
 * @brief  按键中断处理（查看数据）
 */
void EXTI0_1_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 唤醒后显示数据
        display_temperature_data();
    }
}

/**
 * @brief  显示温度数据
 */
void display_temperature_data(void) {
    printf("\n=== 温度记录 ===\n");
    printf("共 %d 条记录\n\n", temp_buffer.count);
    
    printf("%-5s %-10s %-10s\n", "序号", "温度(°C)", "时间(s)");
    printf("────────────────────────────\n");
    
    // 显示最近10条记录
    uint16_t start = temp_buffer.count > 10 ? temp_buffer.count - 10 : 0;
    
    for (uint16_t i = start; i < temp_buffer.count; i++) {
        uint16_t index = (temp_buffer.write_index - temp_buffer.count + i) % MAX_RECORDS;
        float temp = temp_buffer.records[index].temperature / 10.0;
        uint32_t time = temp_buffer.records[index].timestamp / 1000;
        
        printf("%-5d %-10.1f %-10lu\n", i + 1, temp, time);
    }
    
    printf("\n");
}
```

### 项目测试

```c
/**
 * @brief  功耗测试程序
 */
void power_consumption_test(void) {
    printf("\n=== 功耗测试 ===\n\n");
    
    printf("测试1：睡眠模式功耗\n");
    printf("  1. 连接电流表\n");
    printf("  2. 进入睡眠模式\n");
    printf("  3. 记录电流值\n");
    printf("  4. 预期：<1μA\n");
    printf("  5. 按任意键继续...\n");
    getchar();
    
    // 进入睡眠
    configure_rtc_wakeup(60);  // 60秒后唤醒
    enter_stop_mode(PWR_Regulator_LowPower);
    
    printf("\n测试2：工作模式功耗\n");
    printf("  1. 测量温度采集时的电流\n");
    printf("  2. 预期：~2mA\n");
    printf("  3. 持续时间：~1秒\n");
    
    float temp = read_temperature();
    printf("  温度：%.1f°C\n", temp);
    
    printf("\n测试3：完整周期功耗\n");
    printf("  1. 运行完整的采集周期\n");
    printf("  2. 使用示波器 + 电流探头\n");
    printf("  3. 观察电流波形\n");
    printf("  4. 计算平均电流\n");
    
    printf("\n测试4：长期测试\n");
    printf("  1. 使用满电电池\n");
    printf("  2. 记录初始电压\n");
    printf("  3. 运行24小时\n");
    printf("  4. 记录最终电压\n");
    printf("  5. 估算电池寿命\n");
}
```

### 优化建议

```c
/**
 * @brief  进一步优化建议
 */
void optimization_suggestions(void) {
    printf("\n进一步优化建议：\n\n");
    
    printf("1. 硬件优化：\n");
    printf("   □ 使用更低功耗的MCU（如STM32L0系列）\n");
    printf("   □ 添加传感器电源控制开关\n");
    printf("   □ 使用低功耗稳压器\n");
    printf("   □ 优化PCB布局减少漏电流\n\n");
    
    printf("2. 软件优化：\n");
    printf("   □ 使用更低的时钟频率\n");
    printf("   □ 优化Flash写入策略\n");
    printf("   □ 减少串口调试输出\n");
    printf("   □ 使用更深的睡眠模式\n\n");
    
    printf("3. 算法优化：\n");
    printf("   □ 实现数据压缩\n");
    printf("   □ 智能采样（温度变化大时增加频率）\n");
    printf("   □ 异常检测（只记录异常数据）\n");
    printf("   □ 预测算法（减少不必要的采样）\n\n");
    
    printf("4. 系统优化：\n");
    printf("   □ 使用更大容量的电池\n");
    printf("   □ 添加能量收集（太阳能）\n");
    printf("   □ 实现电池电量监测\n");
    printf("   □ 低电量保护机制\n");
}
```

## 总结

本教程全面介绍了嵌入式系统低功耗设计的核心技术。

### 核心要点回顾

1. **睡眠模式**：
   - 睡眠模式：快速响应，中等功耗
   - 停止模式：低功耗，保持数据
   - 待机模式：最低功耗，数据丢失
   - 根据应用需求选择合适的模式

2. **时钟门控**：
   - 关闭不使用的外设时钟
   - 动态调整系统时钟频率
   - 实现智能时钟管理
   - 功耗与频率成正比

3. **外设管理**：
   - 按需使能外设
   - 使用完毕及时关闭
   - 配置GPIO为低功耗模式
   - 批量处理提高效率

4. **功耗测量**：
   - 使用合适的测量工具
   - 测量不同工作模式的功耗
   - 计算平均功耗和电池寿命
   - 持续监控和优化

5. **优化策略**：
   - 间歇工作模式
   - 事件驱动架构
   - 数据缓存策略
   - 硬件和软件协同优化

### 设计流程总结

```
1. 需求分析
   ├─ 功能需求
   ├─ 功耗目标
   ├─ 电池寿命要求
   └─ 性能要求

2. 功耗预算
   ├─ 列出所有功耗源
   ├─ 计算各模式功耗
   ├─ 估算平均功耗
   └─ 验证是否满足目标

3. 架构设计
   ├─ 选择低功耗MCU
   ├─ 设计工作模式
   ├─ 规划睡眠策略
   └─ 设计唤醒机制

4. 详细设计
   ├─ 实现睡眠模式
   ├─ 配置时钟门控
   ├─ 管理外设电源
   └─ 优化代码

5. 测试验证
   ├─ 测量实际功耗
   ├─ 对比设计目标
   ├─ 识别问题
   └─ 持续优化
```

### 最佳实践

1. **设计原则**：
   - 不用的就关掉
   - 能慢就不快
   - 能低压就不高压
   - 能睡就不醒

2. **常见错误**：
   - ❌ 忘记关闭外设时钟
   - ❌ GPIO配置不当
   - ❌ 睡眠模式选择不当
   - ❌ 唤醒源配置错误
   - ❌ 功耗测量不准确

3. **设计建议**：
   - ✅ 从一开始就考虑低功耗
   - ✅ 使用低功耗MCU和器件
   - ✅ 实现完善的电源管理
   - ✅ 持续测量和优化
   - ✅ 预留优化空间

## 延伸阅读

推荐进一步学习的内容：

1. **进阶主题**：
   - [电池供电系统设计要点](03-battery-powered-system.html)
   - [动态电源管理(DPM)技术](../intermediate/02-dynamic-power-management.html)
   - [超低功耗传感器节点设计](../advanced/01-ultra-low-power-sensor.html)

2. **相关知识**：
   - [嵌入式系统电源设计基础](01-power-design-basics.html)
   - [电源监控与保护电路设计](04-power-monitoring.html)
   - [电池管理系统(BMS)设计实战](../intermediate/01-bms-design.html)

3. **实践项目**：
   - 低功耗物联网节点
   - 可穿戴设备电源管理

## 参考资料

1. 《Ultra-Low-Power Wireless Technologies for Sensor Networks》
2. 《Low-Power Design Essentials》- Jan M. Rabaey
3. STM32L系列超低功耗应用笔记 - STMicroelectronics
4. 《嵌入式系统低功耗设计》- 清华大学出版社
5. ARM Cortex-M低功耗技术白皮书

---

**练习题**：

1. 计算平均功耗：
   - 工作：50mA，1秒
   - 睡眠：0.5mA，59秒
   - 计算平均电流和功耗（@3.3V）
   - 估算2000mAh电池的寿命

2. 设计睡眠策略：
   - 系统需要每小时采集一次数据
   - 采集时间约2秒
   - 选择合适的睡眠模式
   - 设计唤醒机制

3. 优化GPIO配置：
   - 有10个未使用的GPIO
   - 当前配置为浮空输入
   - 测量功耗并优化配置
   - 对比优化前后的功耗

4. 实现间歇工作模式：
   - 工作1秒，睡眠9秒
   - 使用RTC定时唤醒
   - 测量平均功耗
   - 计算节能比例

**实践任务**：

1. 测量开发板在不同模式下的功耗
2. 实现一个简单的低功耗应用
3. 优化现有项目的功耗
4. 设计一个电池供电的传感器节点
5. 使用功率分析仪分析功耗波形

**下一步**：建议学习 [电池供电系统设计要点](03-battery-powered-system.html)，深入了解电池管理和充电技术。

---

**常见问题解答**：

**Q: 如何选择合适的睡眠模式？**

A: 考虑以下因素：
- 唤醒时间要求：快速响应用睡眠模式
- 功耗要求：极低功耗用待机模式
- 数据保持：需要保持数据用停止模式
- 唤醒源：确认睡眠模式支持所需唤醒源

**Q: 为什么实际功耗比预期高？**

A: 常见原因：
- GPIO配置不当（浮空输入）
- 外设时钟未关闭
- 有外设仍在工作
- 漏电流（PCB设计问题）
- 测量方法不准确

**Q: 如何进一步降低功耗？**

A: 优化方向：
- 使用更低功耗的MCU
- 降低工作频率和电压
- 优化工作周期（减少工作时间）
- 使用更深的睡眠模式
- 关闭所有不必要的功能

**Q: 睡眠模式下如何调试？**

A: 调试方法：
- 使用LED指示状态
- 使用GPIO输出标记
- 唤醒后输出日志
- 使用低功耗调试模式
- 使用功率分析仪观察波形

**Q: 如何验证低功耗设计？**

A: 验证方法：
- 测量各模式功耗
- 计算平均功耗
- 长期运行测试
- 电池寿命测试
- 温度测试（不同温度下的功耗）
