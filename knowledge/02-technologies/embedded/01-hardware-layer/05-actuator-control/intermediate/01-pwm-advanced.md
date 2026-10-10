---
title: "PWM技术深入解析"
description: "深入理解PWM脉宽调制技术的工作原理、频率选择、死区时间配置、互补PWM生成，掌握电机控制、LED调光等高级应用"
slug: "pwm-advanced-techniques"

# 分类信息
domain: "底层硬件层"
module: "执行器控制"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - PWM
  - 脉宽调制
  - 电机控制
  - 死区时间
  - 互补PWM
  - 定时器
prerequisites:
  - "dc-motor-control-tutorial"
related_contents:
  - "bldc-motor-control"
  - "pid-control"

# 学习信息
estimated_time: 50
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
  - PWM原理
  - 脉宽调制技术
  - 死区时间
  - 互补PWM
  - 电机驱动
  - 定时器配置
cover_image: ""
---

# PWM技术深入解析


## 概述

PWM（Pulse Width Modulation，脉宽调制）是嵌入式系统中最常用的控制技术之一。通过改变脉冲信号的占空比，可以实现对电机速度、LED亮度、电源电压等的精确控制。本文将深入探讨PWM的工作原理、关键参数、高级应用技术。

### 为什么需要深入理解PWM？

- **电机控制**：无刷电机、步进电机需要精确的PWM控制
- **功率调节**：开关电源、DC-DC转换器依赖PWM技术
- **信号生成**：伺服控制、通信协议需要特定的PWM波形
- **性能优化**：合理的PWM参数可以提高效率、降低噪声
- **故障排查**：理解PWM原理有助于快速定位问题

### 学习目标

完成本文学习后，你将能够：

- [ ] 深入理解PWM的工作原理和数学模型
- [ ] 掌握PWM频率选择的原则和影响因素
- [ ] 理解死区时间的作用和配置方法
- [ ] 实现互补PWM信号生成
- [ ] 应用PWM技术解决实际工程问题
- [ ] 优化PWM参数以提高系统性能

## PWM基础原理回顾

### 什么是PWM？

PWM是一种通过改变脉冲宽度来调节输出功率的技术。信号在高电平和低电平之间快速切换，通过控制高电平持续时间的比例（占空比）来实现模拟输出效果。

**核心概念**：

```
     ┌─────┐     ┌─────┐     ┌─────┐
     │     │     │     │     │     │
─────┘     └─────┘     └─────┘     └─────
|<─ T_on ─>|<─ T_off ─>|
|<────── T (周期) ─────>|

占空比 D = T_on / T × 100%
频率 f = 1 / T
平均电压 V_avg = V_cc × D
```

### 关键参数

1. **占空比（Duty Cycle）**
   - 定义：高电平时间占整个周期的百分比
   - 范围：0% ~ 100%
   - 计算：D = (T_on / T) × 100%
   - 影响：直接决定输出功率

2. **频率（Frequency）**
   - 定义：每秒钟脉冲的次数
   - 单位：Hz（赫兹）
   - 计算：f = 1 / T
   - 影响：决定响应速度和效率

3. **分辨率（Resolution）**
   - 定义：占空比可调节的最小步进
   - 表示：通常用位数表示（如8位、10位、16位）
   - 计算：步进 = 100% / (2^n)
   - 影响：控制精度


## PWM工作原理深入分析

### 数学模型

PWM信号可以用傅里叶级数表示：

```
V(t) = V_avg + Σ [A_n × sin(2πnft + φ_n)]
       n=1,∞

其中：
V_avg = V_cc × D  (直流分量)
A_n = 谐波幅度
f = 基频
φ_n = 相位
```

**关键理解**：
- PWM信号包含直流分量和高频谐波分量
- 直流分量等于平均电压，由占空比决定
- 谐波分量可通过滤波器去除
- 频率越高，滤波越容易

### 平均电压与有效值

**平均电压**（用于电机速度控制）：
```
V_avg = V_cc × D

示例：
- V_cc = 12V, D = 50% → V_avg = 6V
- V_cc = 12V, D = 75% → V_avg = 9V
```

**有效值**（用于功率计算）：
```
V_rms = V_cc × √D

示例：
- V_cc = 12V, D = 50% → V_rms = 8.49V
- V_cc = 12V, D = 75% → V_rms = 10.39V
```

### 能量传递机制

PWM通过快速开关实现能量传递：

1. **导通期间（T_on）**：
   - 能量从电源传递到负载
   - 电流上升（感性负载）
   - 磁场能量增加

2. **关断期间（T_off）**：
   - 续流二极管提供电流路径
   - 电流下降
   - 磁场能量释放

3. **平均效果**：
   - 负载获得的平均功率 = V_avg × I_avg
   - 开关损耗远小于线性调节

## PWM频率选择

### 频率选择原则

选择合适的PWM频率需要权衡多个因素：

| 频率范围 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| 100Hz-1kHz | 开关损耗低 | 噪声大、纹波大 | 大功率应用 |
| 1kHz-20kHz | 平衡性能 | 适中 | 电机控制、LED调光 |
| 20kHz-100kHz | 噪声小、纹波小 | 开关损耗高、EMI | 音频应用、精密控制 |
| >100kHz | 超静音、易滤波 | 损耗很高、驱动困难 | 开关电源 |

### 不同应用的频率推荐

**1. 直流电机控制**
- 推荐频率：1kHz - 20kHz
- 原因：
  - 低于1kHz：电机产生明显啸叫
  - 高于20kHz：开关损耗增加，效率降低
  - 最佳：4kHz - 16kHz

**2. 无刷电机（BLDC）**
- 推荐频率：8kHz - 32kHz
- 原因：
  - 需要更高的控制精度
  - 减少转矩脉动
  - 降低电磁噪声

**3. LED调光**
- 推荐频率：100Hz - 10kHz
- 原因：
  - 高于100Hz：避免闪烁
  - 低于10kHz：降低功耗
  - 最佳：200Hz - 1kHz

**4. 舵机控制**
- 固定频率：50Hz（周期20ms）
- 原因：
  - 舵机协议标准
  - 脉宽1-2ms对应角度0-180°

**5. 开关电源**
- 推荐频率：50kHz - 500kHz
- 原因：
  - 减小磁性元件体积
  - 提高功率密度
  - 改善动态响应


### 频率与分辨率的关系

定时器时钟频率固定时，PWM频率和分辨率存在制约关系：

```
PWM频率 = 定时器时钟频率 / (预分频器 × 自动重装载值)
分辨率 = 自动重装载值

示例（STM32，定时器时钟72MHz）：
- 要求：10位分辨率（1024级）
- ARR = 1024
- 预分频器 = 1
- PWM频率 = 72MHz / (1 × 1024) = 70.3kHz

- 要求：16位分辨率（65536级）
- ARR = 65536
- 预分频器 = 1
- PWM频率 = 72MHz / (1 × 65536) = 1.1kHz
```

**权衡策略**：
- 高频率 → 低分辨率
- 高分辨率 → 低频率
- 实际应用中，10-12位分辨率通常足够

### 频率对系统的影响

**1. 对电机的影响**
```
频率过低（<1kHz）：
- 电流纹波大
- 转矩脉动明显
- 产生可听噪声
- 效率降低

频率适中（1-20kHz）：
- 电流纹波适中
- 运行平稳
- 效率最优

频率过高（>50kHz）：
- 开关损耗增加
- 驱动电路复杂
- EMI问题严重
```

**2. 对开关器件的影响**
```
开关损耗 = (开通损耗 + 关断损耗) × 频率

示例：
- 单次开关损耗：1mJ
- 频率1kHz：损耗 = 1mJ × 1000 = 1W
- 频率10kHz：损耗 = 1mJ × 10000 = 10W
- 频率100kHz：损耗 = 1mJ × 100000 = 100W
```

**3. 对滤波的影响**
```
截止频率 fc = 1 / (2π × R × C)

PWM频率越高：
- 所需滤波电容越小
- 纹波电压越小
- 响应速度越快
```

## 死区时间（Dead Time）

### 什么是死区时间？

在H桥或半桥电路中，上下桥臂不能同时导通，否则会造成电源短路（直通）。死区时间是在一个开关关断和另一个开关开通之间插入的延迟时间。

```
上桥臂PWM:  ┌────┐        ┌────┐
            │    │        │    │
         ───┘    └────────┘    └───
                 |<-死区->|

下桥臂PWM:       ┌────────┐
                 │        │
         ────────┘        └────────
```

### 死区时间的作用

**1. 防止直通**
- 上桥臂关断需要时间（关断延迟）
- 下桥臂开通也需要时间（开通延迟）
- 死区时间 > 关断延迟 + 开通延迟

**2. 保护功率器件**
- MOSFET/IGBT的开关速度有限
- 寄生电容需要充放电时间
- 死区时间提供安全裕量

### 死区时间计算

**基本公式**：
```
T_deadtime ≥ T_fall + T_rise + T_margin

其中：
T_fall = 关断时间（器件数据手册）
T_rise = 开通时间（器件数据手册）
T_margin = 安全裕量（通常20-50%）

示例（IRF540 MOSFET）：
T_fall = 50ns
T_rise = 30ns
T_margin = 30ns
T_deadtime ≥ 110ns，实际设置150ns
```

### 死区时间的影响

**死区时间过短**：
- 可能发生直通
- 器件损坏风险
- 效率降低

**死区时间过长**：
- 输出波形失真
- 有效占空比减小
- 低速时影响明显

**占空比补偿**：
```
实际占空比 = 设定占空比 + (T_deadtime / T_period)

示例：
- 设定占空比：50%
- 死区时间：2μs
- PWM周期：100μs（10kHz）
- 实际占空比 = 50% + (2/100) = 52%
```


### STM32死区时间配置

```c
// STM32 HAL库配置死区时间
TIM_HandleTypeDef htim1;
TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

void PWM_DeadTime_Init(void) {
    // 基本定时器配置
    htim1.Instance = TIM1;
    htim1.Init.Prescaler = 0;
    htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim1.Init.Period = 1000;  // ARR
    htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim1.Init.RepetitionCounter = 0;
    HAL_TIM_PWM_Init(&htim1);
    
    // 死区时间配置
    sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
    sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
    sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
    sBreakDeadTimeConfig.DeadTime = 100;  // 死区时间值
    sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
    sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
    sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
    
    HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
}

// 死区时间计算
// T_deadtime = (DeadTime × T_dtg)
// T_dtg取决于时钟频率和DeadTime值的范围
// 详见参考手册
```

### Arduino死区时间实现

Arduino标准库不直接支持死区时间，需要手动实现：

```cpp
// 软件实现死区时间
const int PWM_HIGH = 9;
const int PWM_LOW = 10;
const int DEAD_TIME_US = 2;  // 2微秒死区

void setPWMWithDeadTime(int duty) {
    // 上桥臂PWM
    if (duty > 0) {
        digitalWrite(PWM_HIGH, HIGH);
        delayMicroseconds(duty * 10);
        digitalWrite(PWM_HIGH, LOW);
        
        // 死区时间
        delayMicroseconds(DEAD_TIME_US);
        
        // 下桥臂PWM
        digitalWrite(PWM_LOW, HIGH);
        delayMicroseconds((100 - duty) * 10);
        digitalWrite(PWM_LOW, LOW);
        
        // 死区时间
        delayMicroseconds(DEAD_TIME_US);
    }
}

// 注意：这种方法占用CPU，不适合高频PWM
// 建议使用硬件定时器或专用PWM芯片
```

## 互补PWM（Complementary PWM）

### 什么是互补PWM？

互补PWM是指两路PWM信号互为反相，且之间插入死区时间。主要用于H桥、半桥等推挽式驱动电路。

```
PWM1:  ┌─────┐   DT   ┌─────┐   DT
       │     │        │     │
    ───┘     └────────┘     └──────

PWM2:        ┌────────┐
             │        │
    ─────────┘        └────────────

DT = 死区时间
```

### 互补PWM的应用

**1. 无刷电机驱动**
- 三相六路互补PWM
- 每相上下桥臂互补
- 精确的死区控制

**2. 开关电源**
- 全桥/半桥拓扑
- 提高效率
- 减小纹波

**3. 逆变器**
- DC-AC转换
- 正弦波生成
- 功率控制

### STM32互补PWM配置

```c
// 配置互补PWM输出
void Complementary_PWM_Init(void) {
    TIM_HandleTypeDef htim1;
    TIM_OC_InitTypeDef sConfigOC = {0};
    TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};
    
    // 定时器基本配置
    htim1.Instance = TIM1;
    htim1.Init.Prescaler = 0;
    htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim1.Init.Period = 1000;
    htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim1.Init.RepetitionCounter = 0;
    HAL_TIM_PWM_Init(&htim1);
    
    // PWM通道配置
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 500;  // 50%占空比
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;  // 互补输出极性
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
    sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
    
    HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1);
    
    // 死区时间配置
    sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
    sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
    sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
    sBreakDeadTimeConfig.DeadTime = 100;  // 死区时间
    sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
    sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
    sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
    
    HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
    
    // 启动PWM和互补PWM
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);  // 互补输出
}

// 动态调整占空比
void Set_Complementary_PWM_Duty(uint16_t duty) {
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, duty);
}
```


## PWM高级应用

### 1. 多相PWM控制

用于三相无刷电机（BLDC）控制：

```c
// 三相PWM配置（120度相位差）
void Three_Phase_PWM_Init(void) {
    // 通道1：0度相位
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);
    
    // 通道2：120度相位
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
    HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_2);
    
    // 通道3：240度相位
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);
    HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_3);
}

// SVPWM（空间矢量PWM）算法
void SVPWM_Calculate(float Vd, float Vq, float theta, 
                     uint16_t* duty_a, uint16_t* duty_b, uint16_t* duty_c) {
    // 计算三相占空比
    float Va = Vd * cos(theta) - Vq * sin(theta);
    float Vb = Vd * cos(theta - 2*PI/3) - Vq * sin(theta - 2*PI/3);
    float Vc = Vd * cos(theta + 2*PI/3) - Vq * sin(theta + 2*PI/3);
    
    // 归一化到PWM范围
    *duty_a = (uint16_t)((Va + 1.0) * ARR / 2);
    *duty_b = (uint16_t)((Vb + 1.0) * ARR / 2);
    *duty_c = (uint16_t)((Vc + 1.0) * ARR / 2);
}
```

### 2. PWM输入捕获

测量外部PWM信号的频率和占空比：

```c
// PWM输入模式配置
TIM_HandleTypeDef htim2;
TIM_IC_InitTypeDef sConfigIC = {0};

void PWM_Input_Init(void) {
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 72-1;  // 1MHz计数频率
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 0xFFFF;
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_IC_Init(&htim2);
    
    // 配置输入捕获
    sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
    sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
    sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
    sConfigIC.ICFilter = 0;
    HAL_TIM_IC_ConfigChannel(&htim2, &sConfigIC, TIM_CHANNEL_1);
    
    // 配置间接通道（测量占空比）
    sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_FALLING;
    sConfigIC.ICSelection = TIM_ICSELECTION_INDIRECTTI;
    HAL_TIM_IC_ConfigChannel(&htim2, &sConfigIC, TIM_CHANNEL_2);
    
    // 启动输入捕获
    HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);
    HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_2);
}

// 中断回调函数
uint32_t period = 0;
uint32_t pulse_width = 0;
float frequency = 0;
float duty_cycle = 0;

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    if (htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1) {
        // 捕获周期
        period = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
        
        // 捕获脉宽
        pulse_width = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_2);
        
        // 计算频率和占空比
        if (period != 0) {
            frequency = 1000000.0 / period;  // Hz
            duty_cycle = (float)pulse_width / period * 100.0;  // %
        }
    }
}
```

### 3. 软件PWM实现

当硬件PWM通道不足时，可以使用定时器中断实现软件PWM：

```cpp
// Arduino软件PWM实现
const int NUM_CHANNELS = 8;
int pwm_pins[NUM_CHANNELS] = {2, 3, 4, 5, 6, 7, 8, 9};
int pwm_duty[NUM_CHANNELS] = {0};  // 0-255
int pwm_counter = 0;

void setup() {
    // 配置引脚
    for (int i = 0; i < NUM_CHANNELS; i++) {
        pinMode(pwm_pins[i], OUTPUT);
    }
    
    // 配置定时器中断（1kHz，每1ms触发）
    Timer1.initialize(1000);  // 1000微秒 = 1ms
    Timer1.attachInterrupt(softwarePWM);
}

void softwarePWM() {
    pwm_counter++;
    if (pwm_counter >= 256) {
        pwm_counter = 0;
    }
    
    // 更新所有通道
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (pwm_counter < pwm_duty[i]) {
            digitalWrite(pwm_pins[i], HIGH);
        } else {
            digitalWrite(pwm_pins[i], LOW);
        }
    }
}

// 设置占空比
void setPWM(int channel, int duty) {
    if (channel >= 0 && channel < NUM_CHANNELS) {
        pwm_duty[channel] = constrain(duty, 0, 255);
    }
}
```

**软件PWM的限制**：
- 占用CPU资源
- 频率受限（通常<10kHz）
- 精度较低
- 通道间可能有抖动

### 4. PWM DAC（数模转换）

使用PWM和RC滤波器实现简单的DAC：

```cpp
// PWM DAC实现
const int PWM_PIN = 9;
const int PWM_FREQ = 31250;  // Hz
const int PWM_RESOLUTION = 8;  // 8位

void setup() {
    pinMode(PWM_PIN, OUTPUT);
    
    // 设置PWM频率（Arduino Uno）
    TCCR1B = TCCR1B & 0b11111000 | 0x01;  // 31.25kHz
}

// 输出模拟电压
void analogOutput(float voltage) {
    // 假设参考电压5V
    int duty = (int)(voltage / 5.0 * 255);
    duty = constrain(duty, 0, 255);
    analogWrite(PWM_PIN, duty);
}

// 生成正弦波
void generateSineWave(float frequency) {
    float phase = 0;
    float phase_increment = 2 * PI * frequency / 1000;  // 假设1kHz采样率
    
    while (true) {
        float voltage = 2.5 + 2.5 * sin(phase);  // 0-5V正弦波
        analogOutput(voltage);
        
        phase += phase_increment;
        if (phase >= 2 * PI) {
            phase -= 2 * PI;
        }
        
        delay(1);  // 1ms延迟
    }
}
```

**RC滤波器设计**：
```
PWM输出 ──┬── R ──┬── 模拟输出
          │       │
          └─ C ───┴── GND

截止频率：fc = 1 / (2π × R × C)

推荐：fc = PWM频率 / 10

示例（31.25kHz PWM）：
fc = 3.125kHz
选择 R = 1kΩ, C = 47nF
实际 fc = 3.39kHz
```


## PWM性能优化

### 1. 减少开关损耗

**软开关技术**：
- 零电压开关（ZVS）
- 零电流开关（ZCS）
- 谐振转换

**优化策略**：
```c
// 自适应死区时间
void adaptive_deadtime(float load_current) {
    uint16_t deadtime;
    
    if (load_current < 1.0) {
        deadtime = 50;   // 轻载：短死区
    } else if (load_current < 5.0) {
        deadtime = 100;  // 中载：标准死区
    } else {
        deadtime = 150;  // 重载：长死区
    }
    
    // 更新死区时间配置
    sBreakDeadTimeConfig.DeadTime = deadtime;
    HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
}
```

### 2. 降低EMI

**频率抖动（Spread Spectrum）**：
```c
// 频率抖动减少EMI
void frequency_dithering(void) {
    static uint16_t base_period = 1000;
    static int8_t dither = 0;
    static int8_t direction = 1;
    
    // 在±5%范围内抖动
    dither += direction;
    if (dither >= 50 || dither <= -50) {
        direction = -direction;
    }
    
    uint16_t new_period = base_period + dither;
    __HAL_TIM_SET_AUTORELOAD(&htim1, new_period);
}
```

**滤波优化**：
- 输出端添加LC滤波器
- 电源端添加共模扼流圈
- PCB布局优化（减小环路面积）

### 3. 提高效率

**同步整流**：
```c
// 同步整流控制
void synchronous_rectification(int direction) {
    if (direction > 0) {
        // 正向：上桥臂PWM，下桥臂同步整流
        HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
        HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);
    } else {
        // 反向：下桥臂PWM，上桥臂同步整流
        HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);
        HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    }
}
```

**功率因数校正**：
- 对于AC-DC应用
- 提高输入功率因数
- 减少谐波污染

### 4. 精度优化

**占空比线性化**：
```c
// 补偿死区时间影响
float compensate_duty(float desired_duty, float deadtime_us, float period_us) {
    float deadtime_ratio = deadtime_us / period_us;
    float compensated_duty = desired_duty + deadtime_ratio;
    
    // 限制范围
    if (compensated_duty > 0.95) compensated_duty = 0.95;
    if (compensated_duty < 0.05) compensated_duty = 0.05;
    
    return compensated_duty;
}

// 使用示例
void set_motor_speed(float speed_percent) {
    float period_us = 100;  // 10kHz
    float deadtime_us = 2;
    
    float duty = speed_percent / 100.0;
    float compensated = compensate_duty(duty, deadtime_us, period_us);
    
    uint16_t ccr = (uint16_t)(compensated * ARR);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, ccr);
}
```

**温度补偿**：
```c
// 根据温度调整PWM参数
void temperature_compensation(float temperature) {
    // MOSFET导通电阻随温度增加
    // 需要增加占空比补偿
    
    float temp_coefficient = 0.001;  // 每度0.1%
    float compensation = (temperature - 25.0) * temp_coefficient;
    
    // 应用补偿
    current_duty += compensation;
}
```

## 常见问题与解决方案

### 问题1：PWM输出不稳定

**症状**：
- 占空比波动
- 频率不稳定
- 输出有毛刺

**可能原因**：
1. 电源噪声干扰
2. 定时器时钟不稳定
3. 中断优先级冲突
4. 负载变化影响

**解决方案**：
```c
// 1. 使用DMA更新PWM，避免中断延迟
void PWM_DMA_Init(void) {
    // 配置DMA传输PWM占空比
    HAL_TIM_PWM_Start_DMA(&htim1, TIM_CHANNEL_1, 
                          (uint32_t*)pwm_buffer, BUFFER_SIZE);
}

// 2. 提高定时器中断优先级
HAL_NVIC_SetPriority(TIM1_UP_TIM10_IRQn, 0, 0);

// 3. 添加软件滤波
uint16_t filter_pwm_duty(uint16_t new_duty) {
    static uint16_t filtered = 0;
    const float alpha = 0.1;  // 滤波系数
    
    filtered = (uint16_t)(alpha * new_duty + (1 - alpha) * filtered);
    return filtered;
}
```

### 问题2：电机低速抖动

**症状**：
- 低速时电机不平稳
- 有明显的顿挫感
- 噪声增大

**原因分析**：
- PWM分辨率不足
- 死区时间影响大
- 电流纹波大

**解决方案**：
```c
// 1. 提高PWM分辨率
// 降低频率以获得更高分辨率
htim1.Init.Period = 4000;  // 从1000提高到4000

// 2. 低速时使用更高频率
void adaptive_pwm_frequency(float speed) {
    if (speed < 0.2) {
        // 低速：高频率，低分辨率
        htim1.Init.Period = 500;
        htim1.Init.Prescaler = 0;
    } else {
        // 高速：低频率，高分辨率
        htim1.Init.Period = 2000;
        htim1.Init.Prescaler = 0;
    }
    HAL_TIM_PWM_Init(&htim1);
}

// 3. 添加电流环控制
void current_loop_control(float target_current) {
    float measured_current = read_current();
    float error = target_current - measured_current;
    
    // PI控制器
    static float integral = 0;
    integral += error * 0.01;  // Ki = 0.01
    
    float output = 2.0 * error + integral;  // Kp = 2.0
    
    // 转换为PWM占空比
    uint16_t duty = (uint16_t)(output * ARR);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, duty);
}
```

### 问题3：高频噪声

**症状**：
- 电机或电路产生高频啸叫
- EMI测试不通过
- 干扰其他电路

**解决方案**：
```c
// 1. 调整PWM频率到超声波范围
htim1.Init.Prescaler = 0;
htim1.Init.Period = 3600;  // 20kHz @ 72MHz

// 2. 添加软启动斜坡
void soft_start_ramp(uint16_t target_duty) {
    static uint16_t current_duty = 0;
    const uint16_t ramp_step = 10;
    
    if (current_duty < target_duty) {
        current_duty += ramp_step;
        if (current_duty > target_duty) {
            current_duty = target_duty;
        }
    } else if (current_duty > target_duty) {
        current_duty -= ramp_step;
        if (current_duty < target_duty) {
            current_duty = target_duty;
        }
    }
    
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, current_duty);
}

// 3. 硬件滤波
// 在电机端添加RC滤波器
// R = 10Ω, C = 100nF
```


### 问题4：功率器件过热

**症状**：
- MOSFET/IGBT温度过高
- 驱动芯片发烫
- 系统效率低

**原因分析**：
- 开关损耗过大
- 导通损耗过大
- 死区时间不当
- 散热不良

**解决方案**：
```c
// 1. 优化开关频率
// 降低频率减少开关损耗
htim1.Init.Period = 7200;  // 10kHz @ 72MHz

// 2. 选择合适的MOSFET
// 低Rds(on)：减少导通损耗
// 低Qg：减少开关损耗

// 3. 动态调整死区时间
void optimize_deadtime_for_efficiency(float load_current) {
    // 轻载时可以使用较短死区
    // 重载时需要较长死区保证安全
    uint16_t deadtime = 50 + (uint16_t)(load_current * 10);
    
    sBreakDeadTimeConfig.DeadTime = deadtime;
    HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
}

// 4. 添加过温保护
void thermal_protection(void) {
    float temperature = read_temperature();
    
    if (temperature > 85.0) {
        // 降低功率
        current_max_duty *= 0.8;
    } else if (temperature > 100.0) {
        // 紧急停机
        HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);
        HAL_TIMEx_PWMN_Stop(&htim1, TIM_CHANNEL_1);
    }
}
```

## 实际应用案例

### 案例1：LED调光系统

```c
// 高质量LED调光（无闪烁）
#define LED_PWM_FREQ 1000  // 1kHz，避免闪烁
#define LED_CHANNELS 16

typedef struct {
    TIM_HandleTypeDef *htim;
    uint32_t channel;
    uint16_t current_brightness;
    uint16_t target_brightness;
} LED_Channel_t;

LED_Channel_t led_channels[LED_CHANNELS];

// 初始化LED PWM
void LED_PWM_Init(void) {
    // 配置定时器为1kHz
    htim1.Init.Prescaler = 72-1;  // 1MHz
    htim1.Init.Period = 1000-1;   // 1kHz
    HAL_TIM_PWM_Init(&htim1);
    
    // 启动所有通道
    for (int i = 0; i < LED_CHANNELS; i++) {
        HAL_TIM_PWM_Start(led_channels[i].htim, led_channels[i].channel);
    }
}

// 设置LED亮度（带渐变）
void LED_Set_Brightness(uint8_t channel, uint16_t brightness) {
    if (channel < LED_CHANNELS) {
        led_channels[channel].target_brightness = brightness;
    }
}

// 渐变更新（在定时器中断中调用）
void LED_Update_Fade(void) {
    for (int i = 0; i < LED_CHANNELS; i++) {
        uint16_t current = led_channels[i].current_brightness;
        uint16_t target = led_channels[i].target_brightness;
        
        if (current < target) {
            current += 5;  // 渐变速度
            if (current > target) current = target;
        } else if (current > target) {
            current -= 5;
            if (current < target) current = target;
        }
        
        led_channels[i].current_brightness = current;
        
        // 更新PWM
        __HAL_TIM_SET_COMPARE(led_channels[i].htim, 
                              led_channels[i].channel, 
                              current);
    }
}

// 伽马校正（人眼感知线性）
uint16_t gamma_correction(uint8_t linear_value) {
    // 使用查找表或公式
    // PWM = (linear / 255)^2.2 × 1000
    float normalized = linear_value / 255.0;
    float gamma = pow(normalized, 2.2);
    return (uint16_t)(gamma * 1000);
}
```

### 案例2：开关电源控制

```c
// Buck转换器PWM控制
#define BUCK_FREQ 100000  // 100kHz
#define VOUT_TARGET 5.0   // 目标输出5V

typedef struct {
    float Kp;
    float Ki;
    float Kd;
    float integral;
    float last_error;
    float output_min;
    float output_max;
} PID_Controller_t;

PID_Controller_t voltage_pid = {
    .Kp = 0.5,
    .Ki = 10.0,
    .Kd = 0.01,
    .integral = 0,
    .last_error = 0,
    .output_min = 0.1,
    .output_max = 0.9
};

// Buck转换器PWM初始化
void Buck_PWM_Init(void) {
    // 100kHz PWM
    htim1.Init.Prescaler = 0;
    htim1.Init.Period = 720;  // 100kHz @ 72MHz
    HAL_TIM_PWM_Init(&htim1);
    
    // 启动PWM
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
}

// 电压环PID控制
float voltage_pid_control(float target, float measured) {
    float error = target - measured;
    
    // 积分项
    voltage_pid.integral += error * 0.0001;  // 10kHz控制频率
    
    // 抗积分饱和
    if (voltage_pid.integral > 0.5) voltage_pid.integral = 0.5;
    if (voltage_pid.integral < -0.5) voltage_pid.integral = -0.5;
    
    // 微分项
    float derivative = (error - voltage_pid.last_error) / 0.0001;
    voltage_pid.last_error = error;
    
    // PID输出
    float output = voltage_pid.Kp * error + 
                   voltage_pid.Ki * voltage_pid.integral + 
                   voltage_pid.Kd * derivative;
    
    // 限幅
    if (output > voltage_pid.output_max) output = voltage_pid.output_max;
    if (output < voltage_pid.output_min) output = voltage_pid.output_min;
    
    return output;
}

// 主控制循环
void Buck_Control_Loop(void) {
    float vout = read_output_voltage();
    float duty = voltage_pid_control(VOUT_TARGET, vout);
    
    // 更新PWM占空比
    uint16_t ccr = (uint16_t)(duty * 720);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, ccr);
}
```

### 案例3：伺服电机控制

```c
// 标准伺服PWM（50Hz，1-2ms脉宽）
#define SERVO_FREQ 50      // 50Hz
#define SERVO_PERIOD 20000 // 20ms
#define SERVO_MIN 1000     // 1ms
#define SERVO_MAX 2000     // 2ms

// 伺服PWM初始化
void Servo_PWM_Init(void) {
    // 50Hz PWM
    htim2.Init.Prescaler = 72-1;  // 1MHz
    htim2.Init.Period = 20000-1;  // 50Hz
    HAL_TIM_PWM_Init(&htim2);
    
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
}

// 设置伺服角度（0-180度）
void Servo_Set_Angle(float angle) {
    // 限制角度范围
    if (angle < 0) angle = 0;
    if (angle > 180) angle = 180;
    
    // 转换为脉宽（1000-2000us）
    uint16_t pulse_width = SERVO_MIN + (uint16_t)((angle / 180.0) * (SERVO_MAX - SERVO_MIN));
    
    // 更新PWM
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse_width);
}

// 平滑移动到目标角度
void Servo_Move_Smooth(float target_angle, float speed) {
    static float current_angle = 90.0;
    
    float diff = target_angle - current_angle;
    
    if (fabs(diff) > speed) {
        if (diff > 0) {
            current_angle += speed;
        } else {
            current_angle -= speed;
        }
    } else {
        current_angle = target_angle;
    }
    
    Servo_Set_Angle(current_angle);
}
```

## 测试与调试

### PWM信号测试

**使用示波器**：
```
测试项目：
1. 频率测量
   - 设置：时基适当，触发在上升沿
   - 测量：周期T，计算f = 1/T
   
2. 占空比测量
   - 设置：光标测量
   - 测量：T_on和T，计算D = T_on/T × 100%
   
3. 上升/下降时间
   - 设置：时基放大到ns级
   - 测量：10%-90%上升时间
   
4. 死区时间
   - 同时观察互补PWM两路信号
   - 测量两路信号之间的间隔
```

**使用逻辑分析仪**：
```c
// 添加调试输出
void PWM_Debug_Output(void) {
    // 在关键点输出调试信号
    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_SET);
    
    // PWM更新代码
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, new_duty);
    
    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_RESET);
}
```

### 性能测试

```c
// 效率测试
typedef struct {
    float input_voltage;
    float input_current;
    float output_voltage;
    float output_current;
    float efficiency;
} Power_Measurement_t;

Power_Measurement_t measure_efficiency(void) {
    Power_Measurement_t result;
    
    result.input_voltage = read_vin();
    result.input_current = read_iin();
    result.output_voltage = read_vout();
    result.output_current = read_iout();
    
    float pin = result.input_voltage * result.input_current;
    float pout = result.output_voltage * result.output_current;
    
    result.efficiency = (pout / pin) * 100.0;
    
    return result;
}

// 纹波测试
float measure_ripple(void) {
    const int SAMPLES = 1000;
    float samples[SAMPLES];
    float sum = 0;
    
    // 采集数据
    for (int i = 0; i < SAMPLES; i++) {
        samples[i] = read_output_voltage();
        sum += samples[i];
        delayMicroseconds(10);
    }
    
    float average = sum / SAMPLES;
    
    // 计算峰峰值
    float max_val = samples[0];
    float min_val = samples[0];
    
    for (int i = 1; i < SAMPLES; i++) {
        if (samples[i] > max_val) max_val = samples[i];
        if (samples[i] < min_val) min_val = samples[i];
    }
    
    float ripple = max_val - min_val;
    return ripple;
}
```


## 最佳实践

### 1. PWM参数选择指南

**频率选择决策树**：
```
应用类型？
├─ 电机控制
│  ├─ 直流有刷电机：4-20kHz
│  ├─ 无刷电机：8-32kHz
│  └─ 步进电机：1-10kHz
│
├─ LED调光
│  ├─ 单色LED：200Hz-1kHz
│  ├─ RGB LED：1-5kHz
│  └─ 高速摄像：>10kHz
│
├─ 电源转换
│  ├─ Buck/Boost：50-500kHz
│  ├─ 充电器：20-100kHz
│  └─ 逆变器：10-50kHz
│
└─ 伺服控制
   └─ 标准伺服：50Hz（固定）
```

### 2. 代码组织建议

```c
// pwm_driver.h - PWM驱动接口
#ifndef PWM_DRIVER_H
#define PWM_DRIVER_H

#include "stm32f1xx_hal.h"

// PWM通道定义
typedef enum {
    PWM_CH1 = 0,
    PWM_CH2,
    PWM_CH3,
    PWM_CH4,
    PWM_CH_MAX
} PWM_Channel_t;

// PWM配置结构
typedef struct {
    uint32_t frequency;      // Hz
    uint16_t resolution;     // 位数
    uint16_t deadtime;       // 死区时间（定时器计数值）
    bool complementary;      // 是否使用互补输出
} PWM_Config_t;

// API函数
void PWM_Init(PWM_Channel_t channel, PWM_Config_t *config);
void PWM_SetDuty(PWM_Channel_t channel, float duty_percent);
void PWM_Start(PWM_Channel_t channel);
void PWM_Stop(PWM_Channel_t channel);
float PWM_GetDuty(PWM_Channel_t channel);
uint32_t PWM_GetFrequency(PWM_Channel_t channel);

#endif // PWM_DRIVER_H
```

```c
// pwm_driver.c - PWM驱动实现
#include "pwm_driver.h"

// 内部状态
static struct {
    TIM_HandleTypeDef *htim;
    uint32_t tim_channel;
    uint16_t period;
    uint16_t current_duty;
    bool is_running;
} pwm_channels[PWM_CH_MAX];

void PWM_Init(PWM_Channel_t channel, PWM_Config_t *config) {
    if (channel >= PWM_CH_MAX) return;
    
    // 计算定时器参数
    uint32_t timer_clock = HAL_RCC_GetPCLK1Freq() * 2;
    uint16_t prescaler = 0;
    uint16_t period = timer_clock / config->frequency - 1;
    
    // 如果period太大，使用预分频
    while (period > 65535) {
        prescaler++;
        period = timer_clock / (prescaler + 1) / config->frequency - 1;
    }
    
    // 配置定时器
    TIM_HandleTypeDef *htim = pwm_channels[channel].htim;
    htim->Init.Prescaler = prescaler;
    htim->Init.Period = period;
    htim->Init.CounterMode = TIM_COUNTERMODE_UP;
    htim->Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    
    HAL_TIM_PWM_Init(htim);
    
    // 保存配置
    pwm_channels[channel].period = period;
    pwm_channels[channel].current_duty = 0;
    pwm_channels[channel].is_running = false;
}

void PWM_SetDuty(PWM_Channel_t channel, float duty_percent) {
    if (channel >= PWM_CH_MAX) return;
    
    // 限制范围
    if (duty_percent < 0) duty_percent = 0;
    if (duty_percent > 100) duty_percent = 100;
    
    // 计算CCR值
    uint16_t ccr = (uint16_t)(duty_percent / 100.0 * pwm_channels[channel].period);
    
    // 更新PWM
    __HAL_TIM_SET_COMPARE(pwm_channels[channel].htim, 
                          pwm_channels[channel].tim_channel, 
                          ccr);
    
    pwm_channels[channel].current_duty = ccr;
}

void PWM_Start(PWM_Channel_t channel) {
    if (channel >= PWM_CH_MAX) return;
    
    HAL_TIM_PWM_Start(pwm_channels[channel].htim, 
                      pwm_channels[channel].tim_channel);
    pwm_channels[channel].is_running = true;
}

void PWM_Stop(PWM_Channel_t channel) {
    if (channel >= PWM_CH_MAX) return;
    
    HAL_TIM_PWM_Stop(pwm_channels[channel].htim, 
                     pwm_channels[channel].tim_channel);
    pwm_channels[channel].is_running = false;
}
```

### 3. 安全考虑

```c
// 安全PWM控制
typedef struct {
    float max_duty;          // 最大占空比限制
    float min_duty;          // 最小占空比限制
    uint32_t timeout_ms;     // 看门狗超时
    bool enable_protection;  // 使能保护
} PWM_Safety_t;

PWM_Safety_t pwm_safety = {
    .max_duty = 95.0,
    .min_duty = 5.0,
    .timeout_ms = 1000,
    .enable_protection = true
};

// 安全的PWM设置
bool PWM_SetDuty_Safe(PWM_Channel_t channel, float duty) {
    // 检查范围
    if (duty > pwm_safety.max_duty) {
        duty = pwm_safety.max_duty;
        // 记录警告
        log_warning("PWM duty limited to max");
    }
    
    if (duty < pwm_safety.min_duty) {
        duty = pwm_safety.min_duty;
        log_warning("PWM duty limited to min");
    }
    
    // 更新看门狗
    update_watchdog();
    
    // 设置PWM
    PWM_SetDuty(channel, duty);
    
    return true;
}

// 紧急停止
void PWM_Emergency_Stop(void) {
    // 停止所有PWM通道
    for (int i = 0; i < PWM_CH_MAX; i++) {
        PWM_Stop(i);
        PWM_SetDuty(i, 0);
    }
    
    // 记录事件
    log_error("Emergency stop triggered");
}
```

### 4. 性能监控

```c
// PWM性能统计
typedef struct {
    uint32_t update_count;
    uint32_t error_count;
    float avg_duty;
    float max_duty;
    float min_duty;
    uint32_t last_update_time;
} PWM_Stats_t;

PWM_Stats_t pwm_stats[PWM_CH_MAX];

void PWM_Update_Stats(PWM_Channel_t channel, float duty) {
    PWM_Stats_t *stats = &pwm_stats[channel];
    
    stats->update_count++;
    
    // 更新平均值
    stats->avg_duty = (stats->avg_duty * (stats->update_count - 1) + duty) 
                      / stats->update_count;
    
    // 更新最大最小值
    if (duty > stats->max_duty) stats->max_duty = duty;
    if (duty < stats->min_duty) stats->min_duty = duty;
    
    stats->last_update_time = HAL_GetTick();
}

void PWM_Print_Stats(PWM_Channel_t channel) {
    PWM_Stats_t *stats = &pwm_stats[channel];
    
    printf("PWM Channel %d Statistics:\n", channel);
    printf("  Updates: %lu\n", stats->update_count);
    printf("  Errors: %lu\n", stats->error_count);
    printf("  Avg Duty: %.2f%%\n", stats->avg_duty);
    printf("  Max Duty: %.2f%%\n", stats->max_duty);
    printf("  Min Duty: %.2f%%\n", stats->min_duty);
    printf("  Last Update: %lu ms ago\n", 
           HAL_GetTick() - stats->last_update_time);
}
```

## 总结

### 关键要点

1. **PWM原理**
   - 通过占空比控制平均功率
   - 频率选择需要权衡多个因素
   - 分辨率与频率相互制约

2. **频率选择**
   - 电机控制：1-20kHz
   - LED调光：200Hz-1kHz
   - 开关电源：50-500kHz
   - 考虑噪声、效率、EMI

3. **死区时间**
   - 防止桥臂直通
   - 根据器件特性计算
   - 需要占空比补偿

4. **互补PWM**
   - 用于H桥、半桥电路
   - 必须配置死区时间
   - 适用于电机驱动、电源转换

5. **性能优化**
   - 减少开关损耗
   - 降低EMI
   - 提高控制精度
   - 添加保护机制

### 学习检查清单

完成本文学习后，你应该能够：

- [x] 理解PWM的数学模型和工作原理
- [x] 根据应用选择合适的PWM频率
- [x] 计算和配置死区时间
- [x] 实现互补PWM信号生成
- [x] 优化PWM参数提高系统性能
- [x] 解决常见的PWM相关问题
- [x] 实现安全可靠的PWM控制系统

### 进阶学习方向

**深入主题**：
1. **SVPWM（空间矢量PWM）**
   - 三相电机控制
   - 提高电压利用率
   - 减少谐波

2. **自适应PWM**
   - 根据负载动态调整
   - 效率优化
   - 噪声最小化

3. **数字电源控制**
   - 数字PID算法
   - 状态空间控制
   - 预测控制

4. **高级调制技术**
   - 多电平PWM
   - 随机PWM
   - 混合调制

## 参考资料

### 技术文档

1. **芯片数据手册**
   - STM32 Reference Manual - Timer章节
   - TI Motor Control Application Notes
   - Microchip PWM Application Notes

2. **应用笔记**
   - AN4013: STM32 Timer Cookbook
   - AN2820: Driving MOSFET and IGBT
   - AN1160: Sensorless BLDC Control

### 推荐书籍

1. **《电力电子技术》** - Ned Mohan
   - PWM原理详解
   - 功率转换拓扑
   - 控制策略

2. **《嵌入式系统设计》** - Frank Vahid
   - 定时器应用
   - PWM实现
   - 实时控制

3. **《电机控制系统》** - R. Krishnan
   - 电机驱动技术
   - PWM调制策略
   - 控制算法

### 在线资源

1. **视频教程**
   - "Understanding PWM" - All About Circuits
   - "Advanced Timer Features" - STM32 MOOCs
   - "Motor Control with PWM" - TI Training

2. **开源项目**
   - [SimpleFOC](https://github.com/simplefoc/Arduino-FOC) - 电机控制库
   - [VESC](https://github.com/vedderb/bldc) - 开源电调
   - [ODrive](https://github.com/odriverobotics/ODrive) - 高性能电机控制器

3. **论坛和社区**
   - STM32 Community Forum
   - EEVblog Forum - Power Electronics
   - Stack Exchange - Electrical Engineering

### 相关教程

- [直流电机驱动与控制](../beginner/01-dc-motor-control.html) - PWM基础应用
- [无刷电机控制入门](../intermediate/02-bldc-motor-control.html) - 高级PWM应用
- [PID控制算法实战](../intermediate/03-pid-control.html) - 闭环控制
- 开关电源设计 - PWM在电源中的应用

## 练习与项目

### 练习1：PWM参数计算 ⭐

**任务**：给定系统时钟72MHz，计算以下PWM配置的参数：

1. 频率10kHz，分辨率10位
2. 频率100kHz，最大分辨率
3. 分辨率16位，最大频率

**提示**：使用公式 `频率 = 时钟 / (预分频 × 周期)`

### 练习2：死区时间设计 ⭐⭐

**任务**：设计H桥驱动电路的死区时间

**已知条件**：
- MOSFET型号：IRF540
- 关断时间：50ns
- 开通时间：30ns
- 安全裕量：30%

**要求**：
1. 计算最小死区时间
2. 在STM32上配置死区时间
3. 验证配置是否正确

### 练习3：软件PWM实现 ⭐⭐⭐

**任务**：使用定时器中断实现8通道软件PWM

**要求**：
- 频率：1kHz
- 分辨率：8位
- 占用CPU时间<10%
- 支持动态调整占空比

### 项目：智能LED调光系统 ⭐⭐⭐⭐

**功能要求**：
1. 16路LED独立控制
2. 支持渐变效果
3. 伽马校正
4. 预设场景模式
5. 蓝牙/WiFi控制

**技术要点**：
- 高频PWM（>1kHz）
- DMA传输减少CPU负载
- 平滑渐变算法
- 低功耗设计

---

**版权声明**：本文档采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。

**反馈与改进**：如发现文档错误或有改进建议，欢迎提交Issue或Pull Request。

