---
title: "PWM驱动开发：电机调速控制"
description: "深入学习PWM驱动开发，掌握PWM配置、占空比调节、频率设置、互补输出和死区时间等核心技术，实现精确的电机调速和LED调光控制"
slug: "pwm-driver-motor-control"

# 分类信息
domain: "驱动与BSP层"
module: "设备驱动开发"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - PWM驱动
  - 电机控制
  - 调速
  - LED调光
  - 定时器PWM
prerequisites:
  - "C语言基础"
  - "GPIO驱动开发"
  - "定时器驱动基础"
related_contents:
  - "01-gpio-driver.md"
  - "05-timer-driver.md"
  - "../intermediate/01-dma-driver.md"

# 学习信息
estimated_time: 70
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
  - PWM驱动开发
  - 电机调速
  - STM32 PWM
  - 占空比控制
  - 定时器PWM
cover_image: ""
---

# PWM驱动开发：电机调速控制

## 概述

PWM（Pulse Width Modulation，脉宽调制）是嵌入式系统中最常用的控制技术之一。通过改变脉冲信号的占空比，PWM可以实现对电机速度、LED亮度、舵机角度等的精确控制。掌握PWM驱动开发是实现各种控制应用的基础。

本教程将通过实战项目，带你深入理解PWM的工作原理和驱动开发方法，包括PWM配置、占空比调节、频率设置、多通道控制和高级应用等核心技术。

完成本教程后，你将能够：

- 理解PWM的工作原理和关键参数
- 掌握定时器PWM模式的配置方法
- 实现单通道和多通道PWM输出
- 控制直流电机的转速和方向
- 实现LED呼吸灯和RGB调色
- 理解互补PWM和死区时间的应用
- 设计可靠的PWM驱动程序

## 背景知识

### PWM的工作原理

PWM通过快速开关信号来模拟模拟电压输出，其核心思想是通过改变高电平持续时间来控制平均功率。

**PWM基本概念**：

```
PWM信号波形：
    _____       _____       _____
___|     |_____|     |_____|     |_____
   |<-T->|     |<-T->|     |<-T->|
   |<Th>|      |<Th>|      |<Th>|
   
T  = 周期（Period）
Th = 高电平时间（High Time）
Tl = 低电平时间（Low Time）
f  = 频率 = 1/T
D  = 占空比 = Th/T × 100%
```

**占空比与输出功率**：

```
占空比 0%：   ___________________  → 输出 0V
占空比 25%：  ___   ___   ___   _  → 输出 0.825V (3.3V × 25%)
占空比 50%：  _____   _____   ___  → 输出 1.65V (3.3V × 50%)
占空比 75%：  _______   _______    → 输出 2.475V (3.3V × 75%)
占空比 100%： ___________________  → 输出 3.3V
```

**PWM的优势**：

1. **效率高**：开关状态功耗低，能量损失小
2. **控制精确**：可以实现精细的功率调节
3. **实现简单**：只需要数字信号，不需要DAC
4. **抗干扰强**：数字信号比模拟信号更稳定
5. **成本低**：不需要额外的模拟电路

### STM32定时器PWM功能

STM32的定时器可以产生PWM信号，每个定时器通道都可以独立配置为PWM输出。

**PWM相关寄存器**：

| 寄存器 | 功能 | 说明 |
|--------|------|------|
| ARR | 自动重载寄存器 | 决定PWM周期 |
| CCRx | 捕获/比较寄存器 | 决定占空比 |
| CCMRx | 捕获/比较模式寄存器 | 配置PWM模式 |
| CCER | 捕获/比较使能寄存器 | 使能输出 |
| BDTR | 刹车和死区寄存器 | 高级定时器专用 |

**PWM模式**：

STM32定时器支持两种PWM模式：


**PWM模式1（Mode 1）**：
- 向上计数时：CNT < CCR时输出高电平，CNT ≥ CCR时输出低电平
- 向下计数时：CNT > CCR时输出低电平，CNT ≤ CCR时输出高电平
- 最常用的模式

**PWM模式2（Mode 2）**：
- 与模式1相反
- 向上计数时：CNT < CCR时输出低电平，CNT ≥ CCR时输出高电平

**PWM模式1波形示意**：

```
向上计数模式：
CNT:  0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 0 ...
ARR = 9, CCR = 3

PWM:  ___     _______________________________
         |___|
      高  低电平（CNT ≥ CCR）
      
占空比 = 3/10 = 30%
```

### PWM频率和分辨率

PWM的频率和分辨率是相互制约的，需要根据应用场景进行权衡。

**频率计算公式**：

```
PWM频率 = 定时器时钟频率 / [(PSC + 1) × (ARR + 1)]

占空比分辨率 = ARR + 1

例如：定时器时钟 = 84MHz
PSC = 83, ARR = 999
PWM频率 = 84MHz / (84 × 1000) = 1kHz
分辨率 = 1000 (0.1%精度)
```

**频率与分辨率的权衡**：

| 应用 | 推荐频率 | 分辨率要求 | ARR设置 |
|------|---------|-----------|---------|
| LED调光 | 1-10kHz | 8-10位 | 255-1023 |
| 直流电机 | 10-20kHz | 8-10位 | 255-1023 |
| 舵机控制 | 50Hz | 高精度 | 19999 |
| 开关电源 | 50-500kHz | 较低 | 100-255 |
| 音频输出 | 44.1kHz | 8位 | 255 |

**频率选择原则**：

1. **LED调光**：
   - 频率 > 100Hz：避免人眼感知闪烁
   - 推荐1-10kHz：平衡效果和EMI

2. **电机控制**：
   - 频率 > 20kHz：超出人耳听觉范围
   - 推荐10-20kHz：减少噪音和发热

3. **舵机控制**：
   - 频率 = 50Hz：标准舵机频率
   - 脉宽范围：0.5ms-2.5ms

4. **开关电源**：
   - 频率越高，滤波电容越小
   - 但开关损耗也越大

### PWM占空比计算

占空比决定了输出的平均功率，是PWM控制的核心参数。

**占空比计算公式**：

```
占空比 = CCR / (ARR + 1) × 100%

反向计算CCR：
CCR = 占空比 × (ARR + 1) / 100

例如：ARR = 999
设置50%占空比：CCR = 0.5 × 1000 = 500
设置75%占空比：CCR = 0.75 × 1000 = 750
```

**占空比与输出电压**：

```
假设电源电压为3.3V：

占空比 0%   → 平均电压 0V    → 电机停止 / LED熄灭
占空比 25%  → 平均电压 0.825V → 电机慢速 / LED暗
占空比 50%  → 平均电压 1.65V  → 电机中速 / LED中等亮度
占空比 75%  → 平均电压 2.475V → 电机快速 / LED亮
占空比 100% → 平均电压 3.3V   → 电机全速 / LED最亮
```

### 定时器通道与GPIO映射

STM32的定时器通道需要映射到特定的GPIO引脚。

**TIM3通道映射（常用）**：

| 通道 | 默认引脚 | 重映射引脚 | 说明 |
|------|---------|-----------|------|
| CH1 | PA6 | PB4, PC6 | 通道1 |
| CH2 | PA7 | PB5, PC7 | 通道2 |
| CH3 | PB0 | PC8 | 通道3 |
| CH4 | PB1 | PC9 | 通道4 |

**TIM2通道映射**：

| 通道 | 默认引脚 | 重映射引脚 |
|------|---------|-----------|
| CH1 | PA0 | PA15, PA5 |
| CH2 | PA1 | PB3 |
| CH3 | PA2 | PB10 |
| CH4 | PA3 | PB11 |

**TIM1通道映射（高级定时器）**：

| 通道 | 默认引脚 | 互补输出 |
|------|---------|---------|
| CH1 | PA8 | PB13 (CH1N) |
| CH2 | PA9 | PB14 (CH2N) |
| CH3 | PA10 | PB15 (CH3N) |
| CH4 | PA11 | - |

## 环境准备

### 硬件要求

- STM32F4系列开发板（如STM32F407VET6）
- 直流电机（3-6V）+ L298N电机驱动模块
- LED灯（若干）+ 限流电阻（220Ω）
- 舵机（SG90或MG996R）
- 示波器或逻辑分析仪（用于观察PWM波形）
- 面包板和杜邦线

### 软件要求

- Keil MDK 5.x 或 STM32CubeIDE
- STM32F4 HAL库或标准外设库
- 串口调试工具

### 硬件连接

```
基本PWM输出（LED控制）：
- PA6（TIM3_CH1） -> LED1正极 -> 220Ω电阻 -> GND
- PA7（TIM3_CH2） -> LED2正极 -> 220Ω电阻 -> GND
- PB0（TIM3_CH3） -> LED3正极 -> 220Ω电阻 -> GND
- PB1（TIM3_CH4） -> LED4正极 -> 220Ω电阻 -> GND

电机控制（L298N驱动）：
- PA6（TIM3_CH1） -> L298N IN1（速度控制）
- PA7（TIM3_CH2） -> L298N IN2（速度控制）
- PC0（GPIO）     -> L298N IN3（方向控制）
- PC1（GPIO）     -> L298N IN4（方向控制）
- L298N OUT1/OUT2 -> 电机M1
- L298N OUT3/OUT4 -> 电机M2
- L298N +12V      -> 电源正极（根据电机电压）
- L298N GND       -> 电源负极和STM32 GND

舵机控制：
- PA6（TIM3_CH1） -> 舵机信号线（橙色/黄色）
- 5V              -> 舵机电源线（红色）
- GND             -> 舵机地线（棕色/黑色）

注意：
1. LED需要串联限流电阻
2. 电机驱动模块需要独立供电
3. 舵机电源和STM32共地
4. 大功率负载需要使用外部驱动电路
```

## 核心内容

### 步骤1：GPIO和定时器时钟配置

首先需要配置GPIO为复用功能，并使能定时器时钟。

```c
#include "stm32f4xx.h"

/**
 * @brief  配置TIM3的GPIO引脚
 * @param  无
 * @retval 无
 */
void TIM3_GPIO_Init(void) {
    // 1. 使能GPIOA和GPIOB时钟
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    
    // 2. 配置PA6和PA7为复用功能
    // MODER: 10 = 复用功能
    GPIOA->MODER &= ~((0x03 << (6 * 2)) | (0x03 << (7 * 2)));
    GPIOA->MODER |= (0x02 << (6 * 2)) | (0x02 << (7 * 2));
    
    // 3. 配置PB0和PB1为复用功能
    GPIOB->MODER &= ~((0x03 << (0 * 2)) | (0x03 << (1 * 2)));
    GPIOB->MODER |= (0x02 << (0 * 2)) | (0x02 << (1 * 2));
    
    // 4. 配置输出类型为推挽输出
    GPIOA->OTYPER &= ~((1 << 6) | (1 << 7));
    GPIOB->OTYPER &= ~((1 << 0) | (1 << 1));
    
    // 5. 配置输出速度为高速
    GPIOA->OSPEEDR |= (0x03 << (6 * 2)) | (0x03 << (7 * 2));
    GPIOB->OSPEEDR |= (0x03 << (0 * 2)) | (0x03 << (1 * 2));
    
    // 6. 配置为无上拉下拉
    GPIOA->PUPDR &= ~((0x03 << (6 * 2)) | (0x03 << (7 * 2)));
    GPIOB->PUPDR &= ~((0x03 << (0 * 2)) | (0x03 << (1 * 2)));
    
    // 7. 配置复用功能为TIM3（AF2）
    // AFR[0]控制引脚0-7，AFR[1]控制引脚8-15
    GPIOA->AFR[0] &= ~((0x0F << (6 * 4)) | (0x0F << (7 * 4)));
    GPIOA->AFR[0] |= (0x02 << (6 * 4)) | (0x02 << (7 * 4));  // AF2 = TIM3
    
    GPIOB->AFR[0] &= ~((0x0F << (0 * 4)) | (0x0F << (1 * 4)));
    GPIOB->AFR[0] |= (0x02 << (0 * 4)) | (0x02 << (1 * 4));  // AF2 = TIM3
}
```

**代码说明**：

1. **复用功能配置**：
   - MODER = 10：配置为复用功能模式
   - AFR：选择具体的复用功能（TIM3 = AF2）

2. **输出特性配置**：
   - OTYPER = 0：推挽输出（驱动能力强）
   - OSPEEDR = 11：高速输出（减少边沿抖动）

3. **复用功能编号**：
   - 不同引脚的复用功能编号可能不同
   - 需要查阅数据手册确认

### 步骤2：定时器PWM基本配置

配置定时器的基本参数和PWM模式。

```c
/**
 * @brief  配置TIM3为PWM模式
 * @param  freq: PWM频率（Hz）
 * @param  resolution: 占空比分辨率（ARR+1）
 * @retval 无
 */
void TIM3_PWM_Init(uint32_t freq, uint16_t resolution) {
    // 1. 使能TIM3时钟（APB1总线）
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    
    // 2. 配置GPIO
    TIM3_GPIO_Init();
    
    // 3. 计算预分频器值
    // TIM3时钟 = APB1时钟 × 2 = 84MHz（当APB1分频系数≠1时）
    // PWM频率 = TIM3时钟 / [(PSC+1) × (ARR+1)]
    uint32_t tim_clk = 84000000;  // 84MHz
    uint32_t psc = tim_clk / (freq * resolution) - 1;
    
    // 4. 配置定时器基本参数
    TIM3->PSC = psc;              // 预分频器
    TIM3->ARR = resolution - 1;   // 自动重载值
    TIM3->CR1 = 0;                // 清除控制寄存器
    TIM3->CR1 |= TIM_CR1_ARPE;    // 使能自动重载预装载
    
    // 5. 配置计数模式：向上计数
    TIM3->CR1 &= ~TIM_CR1_DIR;
    TIM3->CR1 &= ~TIM_CR1_CMS;
    
    // 6. 配置通道1为PWM模式1
    TIM3->CCMR1 &= ~TIM_CCMR1_OC1M;
    TIM3->CCMR1 |= (0x06 << 4);   // 110 = PWM模式1
    TIM3->CCMR1 |= TIM_CCMR1_OC1PE;  // 使能预装载
    
    // 7. 配置通道2为PWM模式1
    TIM3->CCMR1 &= ~TIM_CCMR1_OC2M;
    TIM3->CCMR1 |= (0x06 << 12);  // 110 = PWM模式1
    TIM3->CCMR1 |= TIM_CCMR1_OC2PE;
    
    // 8. 配置通道3为PWM模式1
    TIM3->CCMR2 &= ~TIM_CCMR2_OC3M;
    TIM3->CCMR2 |= (0x06 << 4);   // 110 = PWM模式1
    TIM3->CCMR2 |= TIM_CCMR2_OC3PE;
    
    // 9. 配置通道4为PWM模式1
    TIM3->CCMR2 &= ~TIM_CCMR2_OC4M;
    TIM3->CCMR2 |= (0x06 << 12);  // 110 = PWM模式1
    TIM3->CCMR2 |= TIM_CCMR2_OC4PE;
    
    // 10. 使能通道输出
    TIM3->CCER |= TIM_CCER_CC1E;  // 使能通道1输出
    TIM3->CCER |= TIM_CCER_CC2E;  // 使能通道2输出
    TIM3->CCER |= TIM_CCER_CC3E;  // 使能通道3输出
    TIM3->CCER |= TIM_CCER_CC4E;  // 使能通道4输出
    
    // 11. 初始化CCR为0（占空比0%）
    TIM3->CCR1 = 0;
    TIM3->CCR2 = 0;
    TIM3->CCR3 = 0;
    TIM3->CCR4 = 0;
    
    // 12. 生成更新事件，加载预装载值
    TIM3->EGR |= TIM_EGR_UG;
    
    // 13. 启动定时器
    TIM3->CR1 |= TIM_CR1_CEN;
}
```

**配置要点**：

1. **PWM模式选择**：
   - 110 = PWM模式1（最常用）
   - 111 = PWM模式2

2. **预装载使能**：
   - ARPE：ARR预装载
   - OCxPE：CCR预装载
   - 防止更新时产生毛刺

3. **通道使能**：
   - CCxE：使能通道输出
   - CCxP：配置输出极性（0=高电平有效）

### 步骤3：PWM占空比控制函数

实现设置PWM占空比的函数。

```c
/**
 * @brief  设置PWM占空比
 * @param  channel: 通道号（1-4）
 * @param  duty: 占空比（0-100）
 * @retval 无
 */
void TIM3_SetPWM(uint8_t channel, uint8_t duty) {
    // 参数检查
    if (channel < 1 || channel > 4) return;
    if (duty > 100) duty = 100;
    
    // 计算CCR值
    uint16_t ccr = (TIM3->ARR + 1) * duty / 100;
    
    // 设置对应通道的CCR
    switch (channel) {
        case 1: TIM3->CCR1 = ccr; break;
        case 2: TIM3->CCR2 = ccr; break;
        case 3: TIM3->CCR3 = ccr; break;
        case 4: TIM3->CCR4 = ccr; break;
    }
}

/**
 * @brief  设置PWM占空比（高精度）
 * @param  channel: 通道号（1-4）
 * @param  ccr: CCR值（0-ARR）
 * @retval 无
 */
void TIM3_SetPWM_Raw(uint8_t channel, uint16_t ccr) {
    // 参数检查
    if (channel < 1 || channel > 4) return;
    if (ccr > TIM3->ARR) ccr = TIM3->ARR;
    
    // 设置CCR
    switch (channel) {
        case 1: TIM3->CCR1 = ccr; break;
        case 2: TIM3->CCR2 = ccr; break;
        case 3: TIM3->CCR3 = ccr; break;
        case 4: TIM3->CCR4 = ccr; break;
    }
}

/**
 * @brief  获取当前占空比
 * @param  channel: 通道号（1-4）
 * @retval 占空比（0-100）
 */
uint8_t TIM3_GetPWM(uint8_t channel) {
    uint16_t ccr = 0;
    
    // 读取CCR值
    switch (channel) {
        case 1: ccr = TIM3->CCR1; break;
        case 2: ccr = TIM3->CCR2; break;
        case 3: ccr = TIM3->CCR3; break;
        case 4: ccr = TIM3->CCR4; break;
        default: return 0;
    }
    
    // 计算占空比
    return (uint8_t)(ccr * 100 / (TIM3->ARR + 1));
}
```

### 步骤4：LED呼吸灯效果

使用PWM实现LED呼吸灯效果。

```c
/**
 * @brief  LED呼吸灯效果
 * @param  channel: PWM通道
 * @param  speed: 呼吸速度（1-10，越大越快）
 * @retval 无
 */
void LED_Breathing(uint8_t channel, uint8_t speed) {
    static uint8_t duty = 0;
    static int8_t direction = 1;  // 1=增加，-1=减少
    
    // 更新占空比
    duty += direction * speed;
    
    // 反转方向
    if (duty >= 100) {
        duty = 100;
        direction = -1;
    } else if (duty <= 0) {
        duty = 0;
        direction = 1;
    }
    
    // 设置PWM
    TIM3_SetPWM(channel, duty);
}

/**
 * @brief  主函数 - 呼吸灯示例
 */
int main(void) {
    SystemInit();
    
    // 初始化PWM：1kHz频率，1000级分辨率
    TIM3_PWM_Init(1000, 1000);
    
    while (1) {
        // 通道1呼吸灯
        LED_Breathing(1, 1);
        
        // 延时10ms
        for (volatile int i = 0; i < 21000; i++);
    }
}
```


### 步骤5：直流电机速度控制

使用PWM控制直流电机的转速和方向。

```c
/**
 * @brief  电机方向控制GPIO初始化
 * @param  无
 * @retval 无
 */
void Motor_GPIO_Init(void) {
    // 使能GPIOC时钟
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
    
    // 配置PC0和PC1为输出模式
    GPIOC->MODER &= ~((0x03 << 0) | (0x03 << 2));
    GPIOC->MODER |= (0x01 << 0) | (0x01 << 2);
    
    // 推挽输出
    GPIOC->OTYPER &= ~((1 << 0) | (1 << 1));
    
    // 初始化为低电平
    GPIOC->ODR &= ~((1 << 0) | (1 << 1));
}

/**
 * @brief  设置电机速度和方向
 * @param  motor: 电机编号（1或2）
 * @param  speed: 速度（-100到100，负数表示反转）
 * @retval 无
 */
void Motor_SetSpeed(uint8_t motor, int8_t speed) {
    uint8_t pwm_channel;
    uint8_t dir_pin1, dir_pin2;
    
    // 选择电机
    if (motor == 1) {
        pwm_channel = 1;  // TIM3_CH1
        dir_pin1 = 0;     // PC0
        dir_pin2 = 1;     // PC1
    } else if (motor == 2) {
        pwm_channel = 2;  // TIM3_CH2
        dir_pin1 = 2;     // PC2
        dir_pin2 = 3;     // PC3
    } else {
        return;
    }
    
    // 设置方向和速度
    if (speed > 0) {
        // 正转
        GPIOC->BSRR = (1 << dir_pin1);        // 设置为高
        GPIOC->BSRR = (1 << (dir_pin2 + 16)); // 设置为低
        TIM3_SetPWM(pwm_channel, speed);
    } else if (speed < 0) {
        // 反转
        GPIOC->BSRR = (1 << (dir_pin1 + 16)); // 设置为低
        GPIOC->BSRR = (1 << dir_pin2);        // 设置为高
        TIM3_SetPWM(pwm_channel, -speed);
    } else {
        // 停止
        GPIOC->BSRR = (1 << (dir_pin1 + 16)); // 设置为低
        GPIOC->BSRR = (1 << (dir_pin2 + 16)); // 设置为低
        TIM3_SetPWM(pwm_channel, 0);
    }
}

/**
 * @brief  电机刹车
 * @param  motor: 电机编号
 * @retval 无
 */
void Motor_Brake(uint8_t motor) {
    uint8_t dir_pin1, dir_pin2;
    
    if (motor == 1) {
        dir_pin1 = 0;
        dir_pin2 = 1;
    } else {
        dir_pin1 = 2;
        dir_pin2 = 3;
    }
    
    // 两个方向引脚都设为高，实现刹车
    GPIOC->BSRR = (1 << dir_pin1) | (1 << dir_pin2);
}
```

**使用示例**：

```c
int main(void) {
    SystemInit();
    
    // 初始化PWM和电机控制
    TIM3_PWM_Init(20000, 1000);  // 20kHz PWM
    Motor_GPIO_Init();
    
    while (1) {
        // 电机1正转，速度50%
        Motor_SetSpeed(1, 50);
        Delay_ms(2000);
        
        // 电机1反转，速度75%
        Motor_SetSpeed(1, -75);
        Delay_ms(2000);
        
        // 电机1刹车
        Motor_Brake(1);
        Delay_ms(1000);
        
        // 电机1停止
        Motor_SetSpeed(1, 0);
        Delay_ms(1000);
    }
}
```

### 步骤6：舵机角度控制

舵机需要50Hz的PWM信号，脉宽0.5ms-2.5ms对应0-180度。

```c
/**
 * @brief  初始化舵机PWM（50Hz）
 * @param  无
 * @retval 无
 */
void Servo_Init(void) {
    // 50Hz PWM，周期20ms
    // TIM3时钟84MHz，PSC=83，ARR=19999
    // PWM频率 = 84MHz / (84 × 20000) = 50Hz
    TIM3_PWM_Init(50, 20000);
}

/**
 * @brief  设置舵机角度
 * @param  channel: PWM通道（1-4）
 * @param  angle: 角度（0-180度）
 * @retval 无
 */
void Servo_SetAngle(uint8_t channel, uint8_t angle) {
    // 限制角度范围
    if (angle > 180) angle = 180;
    
    // 计算脉宽
    // 0度 = 0.5ms = 1000 CCR
    // 90度 = 1.5ms = 3000 CCR
    // 180度 = 2.5ms = 5000 CCR
    // CCR = 1000 + angle × (5000 - 1000) / 180
    uint16_t ccr = 1000 + (uint32_t)angle * 4000 / 180;
    
    // 设置PWM
    TIM3_SetPWM_Raw(channel, ccr);
}

/**
 * @brief  舵机扫描测试
 * @param  channel: PWM通道
 * @retval 无
 */
void Servo_Sweep(uint8_t channel) {
    uint8_t angle;
    
    // 0度到180度
    for (angle = 0; angle <= 180; angle += 5) {
        Servo_SetAngle(channel, angle);
        Delay_ms(50);
    }
    
    // 180度到0度
    for (angle = 180; angle > 0; angle -= 5) {
        Servo_SetAngle(channel, angle);
        Delay_ms(50);
    }
}
```


## 实践示例

### 示例1：RGB LED调色

使用3个PWM通道控制RGB LED实现全彩调色。

```c
/**
 * @brief  设置RGB颜色
 * @param  red: 红色亮度（0-100）
 * @param  green: 绿色亮度（0-100）
 * @param  blue: 蓝色亮度（0-100）
 * @retval 无
 */
void RGB_SetColor(uint8_t red, uint8_t green, uint8_t blue) {
    TIM3_SetPWM(1, red);    // 红色 -> CH1
    TIM3_SetPWM(2, green);  // 绿色 -> CH2
    TIM3_SetPWM(3, blue);   // 蓝色 -> CH3
}

/**
 * @brief  RGB颜色渐变
 * @param  无
 * @retval 无
 */
void RGB_ColorFade(void) {
    uint8_t i;
    
    // 红色渐变到绿色
    for (i = 0; i <= 100; i++) {
        RGB_SetColor(100 - i, i, 0);
        Delay_ms(20);
    }
    
    // 绿色渐变到蓝色
    for (i = 0; i <= 100; i++) {
        RGB_SetColor(0, 100 - i, i);
        Delay_ms(20);
    }
    
    // 蓝色渐变到红色
    for (i = 0; i <= 100; i++) {
        RGB_SetColor(i, 0, 100 - i);
        Delay_ms(20);
    }
}

/**
 * @brief  主函数 - RGB调色示例
 */
int main(void) {
    SystemInit();
    TIM3_PWM_Init(1000, 1000);
    
    while (1) {
        // 彩虹渐变效果
        RGB_ColorFade();
        
        // 预设颜色显示
        RGB_SetColor(100, 0, 0);    // 红色
        Delay_ms(1000);
        RGB_SetColor(0, 100, 0);    // 绿色
        Delay_ms(1000);
        RGB_SetColor(0, 0, 100);    // 蓝色
        Delay_ms(1000);
        RGB_SetColor(100, 100, 0);  // 黄色
        Delay_ms(1000);
        RGB_SetColor(100, 0, 100);  // 紫色
        Delay_ms(1000);
        RGB_SetColor(0, 100, 100);  // 青色
        Delay_ms(1000);
        RGB_SetColor(100, 100, 100);// 白色
        Delay_ms(1000);
    }
}
```

### 示例2：小车运动控制

使用PWM控制双电机小车的运动。

```c
/**
 * @brief  小车前进
 * @param  speed: 速度（0-100）
 * @retval 无
 */
void Car_Forward(uint8_t speed) {
    Motor_SetSpeed(1, speed);   // 左电机正转
    Motor_SetSpeed(2, speed);   // 右电机正转
}

/**
 * @brief  小车后退
 * @param  speed: 速度（0-100）
 * @retval 无
 */
void Car_Backward(uint8_t speed) {
    Motor_SetSpeed(1, -speed);  // 左电机反转
    Motor_SetSpeed(2, -speed);  // 右电机反转
}

/**
 * @brief  小车左转
 * @param  speed: 速度（0-100）
 * @retval 无
 */
void Car_TurnLeft(uint8_t speed) {
    Motor_SetSpeed(1, -speed);  // 左电机反转
    Motor_SetSpeed(2, speed);   // 右电机正转
}

/**
 * @brief  小车右转
 * @param  speed: 速度（0-100）
 * @retval 无
 */
void Car_TurnRight(uint8_t speed) {
    Motor_SetSpeed(1, speed);   // 左电机正转
    Motor_SetSpeed(2, -speed);  // 右电机反转
}

/**
 * @brief  小车停止
 * @param  无
 * @retval 无
 */
void Car_Stop(void) {
    Motor_SetSpeed(1, 0);
    Motor_SetSpeed(2, 0);
}

/**
 * @brief  主函数 - 小车运动示例
 */
int main(void) {
    SystemInit();
    TIM3_PWM_Init(20000, 1000);
    Motor_GPIO_Init();
    
    while (1) {
        // 前进2秒
        Car_Forward(60);
        Delay_ms(2000);
        
        // 停止1秒
        Car_Stop();
        Delay_ms(1000);
        
        // 后退2秒
        Car_Backward(60);
        Delay_ms(2000);
        
        // 停止1秒
        Car_Stop();
        Delay_ms(1000);
        
        // 左转1秒
        Car_TurnLeft(50);
        Delay_ms(1000);
        
        // 右转1秒
        Car_TurnRight(50);
        Delay_ms(1000);
        
        // 停止
        Car_Stop();
        Delay_ms(2000);
    }
}
```

### 示例3：PWM频率测量

使用示波器或逻辑分析仪测量PWM频率和占空比。

```c
/**
 * @brief  PWM测试信号生成
 * @param  无
 * @retval 无
 */
void PWM_TestSignal(void) {
    // 生成不同频率和占空比的测试信号
    
    // 测试1：1kHz, 50%占空比
    TIM3_PWM_Init(1000, 1000);
    TIM3_SetPWM(1, 50);
    Delay_ms(5000);
    
    // 测试2：10kHz, 25%占空比
    TIM3_PWM_Init(10000, 1000);
    TIM3_SetPWM(1, 25);
    Delay_ms(5000);
    
    // 测试3：20kHz, 75%占空比
    TIM3_PWM_Init(20000, 1000);
    TIM3_SetPWM(1, 75);
    Delay_ms(5000);
}
```

### 示例4：PWM软启动

实现电机的软启动，避免启动电流过大。

```c
/**
 * @brief  电机软启动
 * @param  motor: 电机编号
 * @param  target_speed: 目标速度（0-100）
 * @param  ramp_time: 加速时间（ms）
 * @retval 无
 */
void Motor_SoftStart(uint8_t motor, uint8_t target_speed, uint16_t ramp_time) {
    uint8_t current_speed = 0;
    uint16_t step_delay = ramp_time / target_speed;
    
    // 逐步增加速度
    while (current_speed < target_speed) {
        current_speed++;
        Motor_SetSpeed(motor, current_speed);
        Delay_ms(step_delay);
    }
}

/**
 * @brief  电机软停止
 * @param  motor: 电机编号
 * @param  ramp_time: 减速时间（ms）
 * @retval 无
 */
void Motor_SoftStop(uint8_t motor, uint16_t ramp_time) {
    int8_t current_speed = Motor_GetSpeed(motor);
    uint16_t step_delay = ramp_time / abs(current_speed);
    
    // 逐步减少速度
    while (current_speed != 0) {
        if (current_speed > 0) {
            current_speed--;
        } else {
            current_speed++;
        }
        Motor_SetSpeed(motor, current_speed);
        Delay_ms(step_delay);
    }
}
```

## 深入理解

### 互补PWM输出

高级定时器（TIM1/TIM8）支持互补PWM输出，用于H桥电机驱动。

```c
/**
 * @brief  配置TIM1互补PWM输出
 * @param  无
 * @retval 无
 */
void TIM1_ComplementaryPWM_Init(void) {
    // 1. GPIO配置
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    
    // PA8: TIM1_CH1, PB13: TIM1_CH1N
    GPIOA->MODER |= (0x02 << 16);  // PA8复用
    GPIOB->MODER |= (0x02 << 26);  // PB13复用
    GPIOA->AFR[1] |= (0x01 << 0);  // AF1 = TIM1
    GPIOB->AFR[1] |= (0x01 << 20); // AF1 = TIM1
    
    // 2. 使能TIM1时钟
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;
    
    // 3. 配置定时器
    TIM1->PSC = 83;
    TIM1->ARR = 999;
    TIM1->CR1 |= TIM_CR1_ARPE;
    
    // 4. 配置PWM模式
    TIM1->CCMR1 |= (0x06 << 4);    // PWM模式1
    TIM1->CCMR1 |= TIM_CCMR1_OC1PE;
    
    // 5. 使能主输出和互补输出
    TIM1->CCER |= TIM_CCER_CC1E;   // 使能CH1
    TIM1->CCER |= TIM_CCER_CC1NE;  // 使能CH1N
    
    // 6. 配置死区时间
    // DTG = 72，死区时间 = 72 × (1/84MHz) ≈ 0.86μs
    TIM1->BDTR |= (72 << 0);
    
    // 7. 使能主输出
    TIM1->BDTR |= TIM_BDTR_MOE;
    
    // 8. 启动定时器
    TIM1->CR1 |= TIM_CR1_CEN;
}
```

**死区时间说明**：

```
死区时间是为了防止H桥上下桥臂同时导通造成短路。

无死区：
CH1:  _____|‾‾‾‾‾|_____
CH1N: ‾‾‾‾‾|_____|‾‾‾‾‾
      ↑ 可能同时导通

有死区：
CH1:  _____|‾‾‾‾‾|_____
CH1N: ‾‾‾‾‾‾|___|‾‾‾‾‾‾
         ↑死区↑
```

### PWM DMA更新

使用DMA可以实现PWM波形表输出，用于音频播放等应用。

```c
#define WAVE_SIZE 100
uint16_t wave_table[WAVE_SIZE];

/**
 * @brief  生成正弦波表
 * @param  无
 * @retval 无
 */
void Generate_SineWave(void) {
    for (uint16_t i = 0; i < WAVE_SIZE; i++) {
        // 生成0-ARR范围的正弦波
        float angle = 2.0f * 3.14159f * i / WAVE_SIZE;
        wave_table[i] = (uint16_t)((sin(angle) + 1.0f) * TIM3->ARR / 2.0f);
    }
}

/**
 * @brief  配置PWM DMA更新
 * @param  无
 * @retval 无
 */
void PWM_DMA_Init(void) {
    // 1. 生成波形表
    Generate_SineWave();
    
    // 2. 配置DMA
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA1EN;
    
    DMA1_Stream5->CR = 0;
    while (DMA1_Stream5->CR & DMA_SxCR_EN);
    
    DMA1_Stream5->PAR = (uint32_t)&TIM3->CCR1;
    DMA1_Stream5->M0AR = (uint32_t)wave_table;
    DMA1_Stream5->NDTR = WAVE_SIZE;
    
    DMA1_Stream5->CR = (5 << 25) |  // Channel 5
                       (1 << 16) |  // 优先级中
                       (1 << 13) |  // 内存半字
                       (1 << 11) |  // 外设半字
                       (1 << 10) |  // 内存递增
                       (1 << 8) |   // 循环模式
                       (1 << 6);    // 内存到外设
    
    DMA1_Stream5->CR |= DMA_SxCR_EN;
    
    // 3. 使能TIM3 DMA请求
    TIM3->DIER |= TIM_DIER_CC1DE;
}
```

### PWM输入捕获模式

定时器可以配置为PWM输入模式，用于测量外部PWM信号。

```c
/**
 * @brief  配置PWM输入捕获
 * @param  无
 * @retval 无
 */
void PWM_Input_Init(void) {
    // 配置TIM3_CH1为PWM输入模式
    // 可以同时测量频率和占空比
    
    // 1. GPIO配置（PA6）
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    GPIOA->MODER |= (0x02 << 12);
    GPIOA->AFR[0] |= (0x02 << 24);
    
    // 2. 定时器配置
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    TIM3->PSC = 83;  // 1MHz计数频率
    TIM3->ARR = 0xFFFF;
    
    // 3. 配置CH1为输入，直接映射到TI1
    TIM3->CCMR1 |= (0x01 << 0);  // CC1S = 01
    
    // 4. 配置CH2为输入，交叉映射到TI1
    TIM3->CCMR1 |= (0x02 << 8);  // CC2S = 10
    
    // 5. 配置触发源为TI1FP1
    TIM3->SMCR |= (0x05 << 4);   // TS = 101
    
    // 6. 配置从模式为复位模式
    TIM3->SMCR |= (0x04 << 0);   // SMS = 100
    
    // 7. 使能捕获
    TIM3->CCER |= TIM_CCER_CC1E | TIM_CCER_CC2E;
    
    // 8. 启动定时器
    TIM3->CR1 |= TIM_CR1_CEN;
}

/**
 * @brief  读取PWM输入参数
 * @param  freq: 频率指针（Hz）
 * @param  duty: 占空比指针（0-100）
 * @retval 无
 */
void PWM_Input_Read(uint32_t *freq, uint8_t *duty) {
    uint16_t period = TIM3->CCR1;  // 周期
    uint16_t pulse = TIM3->CCR2;   // 脉宽
    
    if (period > 0) {
        *freq = 1000000 / period;  // 频率
        *duty = (uint8_t)(pulse * 100 / period);  // 占空比
    }
}
```

## 常见问题

### Q1: PWM输出没有波形？

**可能原因**：
1. GPIO未配置为复用功能
2. 复用功能编号错误
3. 通道未使能
4. 定时器未启动
5. CCR值为0或等于ARR

**排查步骤**：

```c
// 1. 检查GPIO配置
printf("GPIOA MODER: 0x%08X\r\n", GPIOA->MODER);
printf("GPIOA AFR[0]: 0x%08X\r\n", GPIOA->AFR[0]);

// 2. 检查定时器配置
printf("TIM3 CR1: 0x%04X\r\n", TIM3->CR1);
printf("TIM3 PSC: %d\r\n", TIM3->PSC);
printf("TIM3 ARR: %d\r\n", TIM3->ARR);
printf("TIM3 CCR1: %d\r\n", TIM3->CCR1);

// 3. 检查通道使能
printf("TIM3 CCER: 0x%04X\r\n", TIM3->CCER);

// 4. 检查定时器是否运行
printf("TIM3 CNT: %d\r\n", TIM3->CNT);
```

### Q2: PWM频率不准确？

**可能原因**：
1. 时钟频率计算错误
2. PSC或ARR设置不当
3. 系统时钟配置错误

**解决方案**：

```c
// 重新计算并验证
uint32_t tim_clk = 84000000;  // 确认定时器时钟
uint32_t target_freq = 1000;  // 目标频率
uint16_t resolution = 1000;   // 分辨率

uint32_t psc = tim_clk / (target_freq * resolution) - 1;
printf("PSC should be: %d\r\n", psc);

// 实际频率
uint32_t actual_freq = tim_clk / ((psc + 1) * (TIM3->ARR + 1));
printf("Actual frequency: %d Hz\r\n", actual_freq);
```

### Q3: 电机运行不平稳，有抖动？

**可能原因**：
1. PWM频率过低
2. 电源电压不稳定
3. 驱动电路问题
4. 负载过大

**解决方案**：

```c
// 1. 提高PWM频率到20kHz
TIM3_PWM_Init(20000, 1000);

// 2. 添加软启动
Motor_SoftStart(1, 60, 1000);

// 3. 添加滤波电容（硬件）
// 在电机两端并联0.1μF电容

// 4. 检查电源电压
// 使用示波器观察电源纹波
```


### Q4: 舵机抖动或不响应？

**可能原因**：
1. PWM频率不是50Hz
2. 脉宽范围不正确
3. 电源电流不足
4. 信号线干扰

**解决方案**：

```c
// 1. 确认PWM频率为50Hz
// ARR = 19999时，周期 = 20ms = 50Hz
TIM3_PWM_Init(50, 20000);

// 2. 调整脉宽范围
// 不同舵机的脉宽范围可能不同
// 标准：0.5ms-2.5ms
// 有些舵机：1ms-2ms
void Servo_SetAngle_Custom(uint8_t channel, uint8_t angle) {
    // 调整这些值以适应你的舵机
    uint16_t min_pulse = 1000;  // 0度脉宽
    uint16_t max_pulse = 5000;  // 180度脉宽
    
    uint16_t ccr = min_pulse + (uint32_t)angle * (max_pulse - min_pulse) / 180;
    TIM3_SetPWM_Raw(channel, ccr);
}

// 3. 使用独立电源供电
// 舵机电流较大，不要与MCU共用电源
```

### Q5: 多通道PWM占空比不一致？

**可能原因**：
1. 各通道CCR设置不同
2. 输出极性配置不同
3. 硬件负载不同

**排查方法**：

```c
// 检查所有通道配置
void PWM_CheckChannels(void) {
    printf("Channel 1: CCR=%d, CCER=0x%04X\r\n", 
           TIM3->CCR1, TIM3->CCER & 0x000F);
    printf("Channel 2: CCR=%d, CCER=0x%04X\r\n", 
           TIM3->CCR2, (TIM3->CCER & 0x00F0) >> 4);
    printf("Channel 3: CCR=%d, CCER=0x%04X\r\n", 
           TIM3->CCR3, (TIM3->CCER & 0x0F00) >> 8);
    printf("Channel 4: CCR=%d, CCER=0x%04X\r\n", 
           TIM3->CCR4, (TIM3->CCER & 0xF000) >> 12);
}

// 统一设置所有通道
void PWM_SetAll(uint8_t duty) {
    uint16_t ccr = (TIM3->ARR + 1) * duty / 100;
    TIM3->CCR1 = ccr;
    TIM3->CCR2 = ccr;
    TIM3->CCR3 = ccr;
    TIM3->CCR4 = ccr;
}
```

## 最佳实践

### 1. 代码模块化

将PWM驱动封装成独立模块：

```c
// pwm_driver.h
#ifndef __PWM_DRIVER_H
#define __PWM_DRIVER_H

#include "stm32f4xx.h"

// PWM初始化
void PWM_Init(TIM_TypeDef *TIMx, uint32_t freq, uint16_t resolution);

// 设置占空比
void PWM_SetDuty(TIM_TypeDef *TIMx, uint8_t channel, uint8_t duty);

// 设置CCR值
void PWM_SetCCR(TIM_TypeDef *TIMx, uint8_t channel, uint16_t ccr);

// 获取占空比
uint8_t PWM_GetDuty(TIM_TypeDef *TIMx, uint8_t channel);

// 启动/停止PWM
void PWM_Start(TIM_TypeDef *TIMx, uint8_t channel);
void PWM_Stop(TIM_TypeDef *TIMx, uint8_t channel);

#endif
```

### 2. 参数验证

在函数中添加参数检查：

```c
void PWM_SetDuty(TIM_TypeDef *TIMx, uint8_t channel, uint8_t duty) {
    // 参数检查
    if (TIMx == NULL) return;
    if (channel < 1 || channel > 4) return;
    if (duty > 100) duty = 100;
    
    // 计算CCR
    uint16_t ccr = (TIMx->ARR + 1) * duty / 100;
    
    // 设置CCR
    switch (channel) {
        case 1: TIMx->CCR1 = ccr; break;
        case 2: TIMx->CCR2 = ccr; break;
        case 3: TIMx->CCR3 = ccr; break;
        case 4: TIMx->CCR4 = ccr; break;
    }
}
```

### 3. 使用宏定义

提高代码可读性和可维护性：

```c
// PWM通道定义
#define PWM_CH1  1
#define PWM_CH2  2
#define PWM_CH3  3
#define PWM_CH4  4

// 电机定义
#define MOTOR_LEFT   1
#define MOTOR_RIGHT  2

// 舵机角度定义
#define SERVO_MIN_ANGLE  0
#define SERVO_MAX_ANGLE  180
#define SERVO_CENTER     90

// 使用示例
Motor_SetSpeed(MOTOR_LEFT, 60);
Servo_SetAngle(PWM_CH1, SERVO_CENTER);
```

### 4. 添加调试功能

```c
/**
 * @brief  打印PWM配置信息
 * @param  TIMx: 定时器
 * @retval 无
 */
void PWM_PrintConfig(TIM_TypeDef *TIMx) {
    printf("=== PWM Configuration ===\r\n");
    printf("PSC: %d\r\n", TIMx->PSC);
    printf("ARR: %d\r\n", TIMx->ARR);
    printf("Frequency: %d Hz\r\n", 
           84000000 / ((TIMx->PSC + 1) * (TIMx->ARR + 1)));
    printf("Resolution: %d\r\n", TIMx->ARR + 1);
    printf("\r\n");
    printf("Channel 1: CCR=%d, Duty=%d%%\r\n", 
           TIMx->CCR1, TIMx->CCR1 * 100 / (TIMx->ARR + 1));
    printf("Channel 2: CCR=%d, Duty=%d%%\r\n", 
           TIMx->CCR2, TIMx->CCR2 * 100 / (TIMx->ARR + 1));
    printf("Channel 3: CCR=%d, Duty=%d%%\r\n", 
           TIMx->CCR3, TIMx->CCR3 * 100 / (TIMx->ARR + 1));
    printf("Channel 4: CCR=%d, Duty=%d%%\r\n", 
           TIMx->CCR4, TIMx->CCR4 * 100 / (TIMx->ARR + 1));
}
```

### 5. 安全保护

添加必要的安全保护机制：

```c
/**
 * @brief  电机安全控制
 * @param  motor: 电机编号
 * @param  speed: 速度
 * @retval 无
 */
void Motor_SetSpeed_Safe(uint8_t motor, int8_t speed) {
    // 限制最大速度
    #define MAX_SPEED 80
    if (speed > MAX_SPEED) speed = MAX_SPEED;
    if (speed < -MAX_SPEED) speed = -MAX_SPEED;
    
    // 检查过流保护
    if (Motor_IsOverCurrent(motor)) {
        Motor_SetSpeed(motor, 0);
        printf("Motor %d overcurrent!\r\n", motor);
        return;
    }
    
    // 正常设置速度
    Motor_SetSpeed(motor, speed);
}

/**
 * @brief  PWM输出限制
 * @param  channel: 通道
 * @param  duty: 占空比
 * @param  min: 最小占空比
 * @param  max: 最大占空比
 * @retval 无
 */
void PWM_SetDuty_Limited(uint8_t channel, uint8_t duty, 
                         uint8_t min, uint8_t max) {
    if (duty < min) duty = min;
    if (duty > max) duty = max;
    TIM3_SetPWM(channel, duty);
}
```

## 进阶学习

### 1. 高级PWM技术

**相位移PWM**：
- 多相电机控制
- 降低EMI干扰
- 提高效率

**中心对齐PWM**：
- 对称波形
- 减少谐波
- 适合电机控制

### 2. PWM与其他外设配合

**PWM + ADC**：
- 电机电流检测
- 闭环速度控制
- 功率监测

**PWM + 编码器**：
- 精确位置控制
- 速度反馈
- PID控制

**PWM + DMA**：
- 波形表输出
- 音频播放
- 复杂时序生成

### 3. 电机控制算法

**PID控制**：
- 速度闭环控制
- 位置闭环控制
- 参数整定

**FOC控制**：
- 无刷电机控制
- 高效率
- 低噪音

### 4. PWM应用扩展

**WS2812 LED驱动**：
- 使用PWM+DMA
- 时序精确控制
- 彩色LED灯带

**红外遥控发射**：
- 38kHz载波
- 编码调制
- 遥控协议

**音频输出**：
- PWM DAC
- 音频播放
- 音调生成

## 学习资源

### 官方文档

1. **STM32参考手册**
   - 定时器PWM章节
   - 寄存器详细说明
   - 时序图和波形

2. **应用笔记**
   - AN4013: STM32定时器概述
   - AN4776: 通用定时器手册
   - AN3116: STM32电机控制

### 推荐工具

1. **示波器**
   - 观察PWM波形
   - 测量频率和占空比
   - 分析信号质量

2. **逻辑分析仪**
   - 多通道同时观察
   - 时序分析
   - 协议解码

3. **电机测试平台**
   - 测试电机性能
   - 调试控制算法
   - 验证驱动电路

### 实践项目

1. **智能风扇**
   - PWM调速
   - 温度控制
   - 难度：⭐⭐

2. **RGB氛围灯**
   - 多通道PWM
   - 颜色渐变
   - 难度：⭐⭐

3. **遥控小车**
   - 双电机控制
   - 无线遥控
   - 难度：⭐⭐⭐

4. **云台控制**
   - 双轴舵机
   - 姿态控制
   - 难度：⭐⭐⭐

5. **无刷电机控制**
   - 三相PWM
   - FOC算法
   - 难度：⭐⭐⭐⭐⭐

## 总结

本教程全面介绍了PWM驱动开发的核心知识和实践技能。

**核心要点回顾**：

1. **PWM原理**：通过改变占空比控制平均功率
2. **频率选择**：根据应用场景选择合适的PWM频率
3. **占空比计算**：CCR = 占空比 × (ARR + 1) / 100
4. **GPIO配置**：配置为复用功能，选择正确的AF编号
5. **定时器配置**：设置PSC、ARR、PWM模式和通道使能
6. **应用场景**：LED调光、电机控制、舵机控制

**实践技能**：
- 单通道和多通道PWM输出
- LED呼吸灯和RGB调色
- 直流电机速度和方向控制
- 舵机角度控制
- 小车运动控制

**最佳实践**：
- 代码模块化，提高可维护性
- 添加参数验证，增强健壮性
- 使用宏定义，提高可读性
- 添加调试功能，方便问题排查
- 实现安全保护，避免硬件损坏

**调试技巧**：
- 使用示波器观察PWM波形
- 检查GPIO和定时器配置
- 验证频率和占空比计算
- 逐步测试各个功能模块

PWM是嵌入式系统中最实用的控制技术之一，掌握PWM驱动开发将为你的项目提供强大的控制能力。

## 延伸阅读

推荐进一步学习的内容：

**同模块内容**：
- [GPIO驱动开发：LED控制实战](01-gpio-driver.html) - GPIO基础
- [定时器驱动基础与应用](05-timer-driver.html) - 定时器原理
- [DMA驱动开发：高效数据传输](../intermediate/01-dma-driver.html) - PWM+DMA

**相关主题**：
- [中断系统基础概念](../../04-interrupt-exception-handling/beginner/01-interrupt-basics.html)
- [通用定时器高级应用](../../05-clock-timer-management/intermediate/01-advanced-timer.html)

**官方文档**：
- [STM32F4xx参考手册](https://www.st.com/resource/en/reference_manual/dm00031020.pdf)
- [AN4013: STM32定时器概述](https://www.st.com/resource/en/application_note/cd00258017.pdf)

## 参考资料

1. STM32F4xx参考手册 - STMicroelectronics
2. ARM Cortex-M4权威指南 - Joseph Yiu
3. 电机控制技术 - 刘和平
4. PWM技术及其应用 - 王兆安
5. 嵌入式系统设计与实践 - Elecia White

## 练习题

### 基础练习

1. **LED调光练习**：
   - 使用PWM实现LED亮度调节
   - 通过按键控制亮度增减
   - 显示当前亮度百分比

2. **呼吸灯练习**：
   - 实现单色LED呼吸灯
   - 可调节呼吸速度
   - 添加暂停/继续功能

3. **RGB调色练习**：
   - 使用3个PWM通道控制RGB LED
   - 实现彩虹渐变效果
   - 预设多种颜色

### 进阶练习

4. **电机控制练习**：
   - 控制直流电机转速
   - 实现正转、反转、停止
   - 添加软启动功能

5. **舵机控制练习**：
   - 控制舵机角度
   - 实现0-180度扫描
   - 添加角度限位保护

6. **小车控制练习**：
   - 双电机小车控制
   - 实现前进、后退、转弯
   - 添加速度调节功能

### 综合练习

7. **智能风扇**：
   - PWM调速控制
   - 温度传感器反馈
   - 自动调节转速
   - LCD显示状态

8. **RGB氛围灯**：
   - 多种灯光效果
   - 颜色渐变和跳变
   - 音乐律动模式
   - 遥控器控制

### 思考题

1. 为什么电机控制的PWM频率要选择20kHz左右？

2. 如何选择合适的PWM频率和分辨率？

3. 互补PWM输出中死区时间的作用是什么？如何计算？

4. PWM控制电机时，如何实现平滑的加减速？

5. 如何使用PWM实现音频输出？需要注意什么？

## 实验任务

### 任务1：LED调光器（必做）

**要求**：
- 使用PWM控制LED亮度
- 通过按键调节亮度（0-100%）
- 串口显示当前亮度
- 实现呼吸灯模式

### 任务2：电机调速器（必做）

**要求**：
- 控制直流电机转速
- 支持正转和反转
- 速度可调（0-100%）
- 实现软启动和软停止

### 任务3：舵机控制器（选做）

**要求**：
- 控制舵机角度（0-180度）
- 通过串口输入角度值
- 实现角度扫描功能
- 添加角度限位保护

### 任务4：智能小车（选做）

**要求**：
- 双电机差速控制
- 实现前进、后退、左转、右转
- 速度可调
- 蓝牙遥控

**评分标准**：
- 代码规范性（20分）
- 功能完整性（30分）
- 控制精度（30分）
- 创新性和扩展性（20分）

---

**下一步学习建议**：

完成本教程后，建议按以下顺序继续学习：

1. [看门狗驱动与系统可靠性](08-watchdog-driver.html) - 系统保护
2. [DMA驱动开发：高效数据传输](../intermediate/01-dma-driver.html) - PWM+DMA应用
3. [通用定时器高级应用](../../05-clock-timer-management/intermediate/01-advanced-timer.html) - 高级PWM技术

**学习路线图**：

```
PWM驱动 → LED控制 → 电机控制 → 舵机控制 → 复杂控制系统
         ↓
      RGB调色 → 氛围灯 → 显示系统
         ↓
      音频输出 → 音乐播放 → 语音合成
```

祝你学习顺利！如有问题，欢迎在社区讨论。

---

**文档信息**：
- 最后更新：2024-01-15
- 版本：v1.0
- 作者：嵌入式知识平台
- 许可：CC BY-NC-SA 4.0
