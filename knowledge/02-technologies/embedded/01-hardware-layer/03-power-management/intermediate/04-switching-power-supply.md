---
# 基础信息
title: "开关电源设计完全指南"
description: "全面深入讲解开关电源的设计原理、拓扑结构和实现方法，包括Buck/Boost/Buck-Boost转换器、PWM控制技术、元件选型、反馈控制和保护电路设计，通过完整实例掌握开关电源核心技术"
slug: "switching-power-supply-design"

# 分类信息
domain: "01-hardware-layer"
module: "03-power-management"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 开关电源
  - Buck转换器
  - Boost转换器
  - PWM控制
  - 电源设计
  - DC-DC转换
  - 反馈控制
  - 元件选型
prerequisites:
  - "../beginner/01-power-design-basics.md"
  - "../beginner/02-linear-regulator.md"
  - "../../02-hardware-design-fundamentals/intermediate/01-pcb-layout-advanced.md"
related_contents:
  - "01-bms-design.md"
  - "02-dynamic-power-management.md"
  - "../../01-chip-architecture/intermediate/02-power-domains.md"

# 学习信息
estimated_time: 120
difficulty_score: 7

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-04-05"
updated_at: "2026-04-05"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - 开关电源设计
  - Buck转换器
  - Boost转换器
  - PWM控制
  - DC-DC转换器
  - 电源拓扑
  - 反馈控制
  - 电感设计
cover_image: ""
---

# 开关电源设计完全指南

## 概述

开关电源(Switching Power Supply)是现代电子设备中最重要的电源转换技术，相比线性稳压器具有更高的效率和更灵活的电压转换能力。本教程将全面深入地讲解开关电源的设计原理、拓扑结构、控制技术和实际应用。

### 什么是开关电源

开关电源是一种通过高频开关动作和储能元件(电感、电容)来实现电压转换的电源技术。其核心思想是：

1. **开关控制**：通过功率开关管的快速通断
2. **能量存储**：利用电感和电容存储和释放能量
3. **PWM调制**：通过调节占空比控制输出电压
4. **反馈稳压**：通过闭环反馈保持输出稳定

### 开关电源 vs 线性稳压器

```
性能对比：

┌──────────────┬─────────────┬─────────────┐
│   特性       │  线性稳压器  │  开关电源    │
├──────────────┼─────────────┼─────────────┤
│ 效率         │  40-60%     │  80-95%     │
│ 发热量       │  大          │  小          │
│ 体积         │  大          │  小          │
│ 噪声         │  低          │  较高        │
│ 成本         │  低          │  中等        │
│ 设计复杂度   │  简单        │  复杂        │
│ 电压转换     │  降压        │  升/降/反转  │
│ 输出纹波     │  极低        │  较高        │
└──────────────┴─────────────┴─────────────┘

效率计算：
线性稳压器：η = Vout / Vin × 100%
开关电源：  η = Pout / Pin × 100% (通常 > 85%)

功耗对比示例：
输入：12V，输出：5V @ 1A

线性稳压器：
- 输出功率：5W
- 输入功率：12W
- 效率：41.7%
- 功耗：7W (发热严重)

开关电源：
- 输出功率：5W
- 输入功率：5.6W
- 效率：89%
- 功耗：0.6W (发热小)
```

### 应用场景

开关电源广泛应用于：

- **消费电子**：手机充电器、笔记本电源适配器
- **工业控制**：PLC电源、工业设备供电
- **通信设备**：基站电源、路由器电源
- **汽车电子**：车载DC-DC转换器
- **新能源**：光伏逆变器、电动车充电器
- **嵌入式系统**：单板计算机、物联网设备

### 本文内容概览

本教程将涵盖以下内容：

1. **基础理论**：开关电源工作原理、基本拓扑
2. **Buck转换器**：降压型开关电源设计
3. **Boost转换器**：升压型开关电源设计
4. **Buck-Boost转换器**：升降压型开关电源设计
5. **PWM控制**：脉宽调制技术和控制芯片
6. **元件选型**：电感、电容、MOSFET、二极管选择
7. **反馈控制**：电压反馈、电流反馈、补偿设计
8. **保护电路**：过流、过压、过温保护
9. **PCB设计**：布局布线、EMI抑制
10. **实战项目**：完整的开关电源设计实例

## 第一部分：开关电源基础理论

### 1.1 工作原理

开关电源的核心工作原理基于以下物理定律：

**电感的基本特性**：

```
电感电压-电流关系：
V_L = L × (di/dt)

关键特性：
1. 电感电流不能突变
2. 电感储能：E = (1/2) × L × I²
3. 电感阻止电流变化

电感在开关电源中的作用：
- 储存能量
- 平滑电流
- 实现电压转换
```

**电容的基本特性**：

```
电容电压-电流关系：
I_C = C × (dv/dt)

关键特性：
1. 电容电压不能突变
2. 电容储能：E = (1/2) × C × V²
3. 电容阻止电压变化

电容在开关电源中的作用：
- 滤波
- 储能
- 稳定电压
```

### 1.2 基本拓扑分类

开关电源有三种基本拓扑：

```
拓扑分类：

1. Buck (降压型)
   输入电压 > 输出电压
   Vout = Vin × D
   应用：12V → 5V, 5V → 3.3V

2. Boost (升压型)
   输入电压 < 输出电压
   Vout = Vin / (1 - D)
   应用：3.7V → 5V, 5V → 12V

3. Buck-Boost (升降压型)
   输入电压可大于或小于输出电压
   Vout = -Vin × D / (1 - D)
   应用：电池供电系统

其中 D 为占空比 (Duty Cycle)
D = Ton / (Ton + Toff) = Ton / T
```

### 1.3 PWM控制基础

**PWM (脉宽调制) 原理**：

```
PWM信号特性：

     ┌──┐    ┌──┐    ┌──┐
     │  │    │  │    │  │
─────┘  └────┘  └────┘  └────
     Ton Toff
     ├─────┤
        T

参数定义：
- T: 周期 (Period)
- f: 频率 (Frequency) = 1/T
- Ton: 导通时间
- Toff: 关断时间
- D: 占空比 = Ton/T

典型频率范围：
- 低频：20kHz - 100kHz
- 中频：100kHz - 500kHz
- 高频：500kHz - 2MHz

频率选择考虑：
- 频率越高，元件越小
- 频率越高，开关损耗越大
- 频率越高，EMI问题越严重
- 常用频率：100kHz - 500kHz
```

### 1.4 连续导通模式 (CCM) vs 断续导通模式 (DCM)

```
工作模式对比：

CCM (Continuous Conduction Mode)：
- 电感电流始终 > 0
- 电流连续流动
- 适合大负载
- 纹波小

DCM (Discontinuous Conduction Mode)：
- 电感电流降至 0
- 电流断续
- 适合轻载
- 纹波大

临界电感值：
L_crit = (Vin - Vout) × Vout / (2 × f × Vin × Iout_min)

设计建议：
- 大功率应用：设计为CCM
- 小功率应用：可工作在DCM
- 宽负载范围：考虑CCM/DCM混合模式
```

## 第二部分：Buck降压转换器设计

### 2.1 Buck转换器原理

Buck转换器是最常用的降压型开关电源拓扑。

**电路结构**：

```
Buck转换器基本电路：

Vin ──┬──[Q1]──┬──[L]──┬── Vout
      │        │       │
     ┌┴┐      ┌┴┐     ┌┴┐
     │C│      │D│     │C│  Rload
     │i│      │1│     │o│
     │n│      └─┘     └┬┘
     └┬┘               │
      │                │
     GND──────────────GND

组件说明：
- Q1: 功率开关管 (N-MOSFET)
- D1: 续流二极管 (Schottky)
- L: 储能电感
- Cin: 输入滤波电容
- Co: 输出滤波电容
- Rload: 负载
```

**工作过程**：

```
工作周期分析：

阶段1：Q1导通 (Ton)
┌─────────────────────────┐
│ Vin → Q1 → L → Vout     │
│ 电感电流上升             │
│ di/dt = (Vin-Vout)/L    │
│ 能量从输入传递到输出     │
└─────────────────────────┘

阶段2：Q1关断 (Toff)
┌─────────────────────────┐
│ L → D1 → Vout           │
│ 电感电流下降             │
│ di/dt = -Vout/L         │
│ 电感释放储存的能量       │
└─────────────────────────┘

稳态时：
Ton × (Vin - Vout) = Toff × Vout
推导得：
Vout = Vin × D
其中 D = Ton / (Ton + Toff)
```

### 2.2 Buck转换器设计步骤

**设计规格示例**：

```
设计要求：
- 输入电压：Vin = 12V ± 10%
- 输出电压：Vout = 5V
- 输出电流：Iout = 2A (max)
- 开关频率：f = 200kHz
- 输出纹波：ΔVout < 50mV
- 效率目标：η > 90%
```

**步骤1：计算占空比**：

```c
/**
 * @brief  计算Buck转换器占空比
 * @param  vin: 输入电压 (V)
 * @param  vout: 输出电压 (V)
 * @return 占空比 (0-1)
 */
float buck_calculate_duty_cycle(float vin, float vout)
{
    // 理想占空比
    float duty = vout / vin;
    
    // 考虑MOSFET导通压降和二极管压降
    float vd_mosfet = 0.1;  // MOSFET导通压降
    float vd_diode = 0.3;   // 二极管压降
    
    // 修正后的占空比
    duty = (vout + vd_diode) / (vin - vd_mosfet);
    
    // 限制范围
    if (duty < 0.1) duty = 0.1;
    if (duty > 0.9) duty = 0.9;
    
    return duty;
}

// 示例计算
// Vin = 12V, Vout = 5V
// D = 5 / 12 = 0.417 (41.7%)
```

**步骤2：选择电感值**：

```c
/**
 * @brief  计算Buck转换器电感值
 * @param  vin: 输入电压 (V)
 * @param  vout: 输出电压 (V)
 * @param  iout: 输出电流 (A)
 * @param  freq: 开关频率 (Hz)
 * @param  ripple_ratio: 电流纹波比 (0.2-0.4)
 * @return 电感值 (H)
 */
float buck_calculate_inductance(float vin, float vout, 
                                float iout, float freq, 
                                float ripple_ratio)
{
    // 电感电流纹波
    float delta_il = iout * ripple_ratio;
    
    // 占空比
    float duty = vout / vin;
    
    // 电感值计算
    // L = (Vin - Vout) × D / (f × ΔIL)
    float inductance = (vin - vout) * duty / (freq * delta_il);
    
    return inductance;
}

// 示例计算
// Vin = 12V, Vout = 5V, Iout = 2A
// f = 200kHz, ripple = 30%
// ΔIL = 2A × 0.3 = 0.6A
// L = (12-5) × 0.417 / (200000 × 0.6)
// L = 24.3 μH
// 选择标准值：L = 22μH 或 27μH
```

**步骤3：选择输出电容**：

```c
/**
 * @brief  计算Buck转换器输出电容
 * @param  delta_il: 电感电流纹波 (A)
 * @param  freq: 开关频率 (Hz)
 * @param  delta_vout: 允许的输出电压纹波 (V)
 * @return 输出电容值 (F)
 */
float buck_calculate_output_capacitance(float delta_il, 
                                        float freq, 
                                        float delta_vout)
{
    // 输出电容计算
    // Co = ΔIL / (8 × f × ΔVout)
    float capacitance = delta_il / (8.0 * freq * delta_vout);
    
    return capacitance;
}

// 示例计算
// ΔIL = 0.6A, f = 200kHz, ΔVout = 50mV
// Co = 0.6 / (8 × 200000 × 0.05)
// Co = 7.5 μF
// 考虑ESR影响，选择：Co = 22μF (低ESR陶瓷电容)
```


**步骤4：选择功率MOSFET**：

```c
/**
 * @brief  MOSFET选型参数计算
 */
typedef struct {
    float vds_max;      // 最大漏源电压 (V)
    float id_max;       // 最大漏极电流 (A)
    float rds_on;       // 导通电阻 (Ω)
    float qg_total;     // 总栅极电荷 (nC)
    float power_loss;   // 功耗 (W)
} MOSFET_Params_t;

/**
 * @brief  计算MOSFET选型参数
 */
void buck_select_mosfet(float vin, float iout, float freq,
                        MOSFET_Params_t *params)
{
    // 电压裕量：1.5-2倍
    params->vds_max = vin * 2.0;
    
    // 电流裕量：1.5-2倍
    params->id_max = iout * 2.0;
    
    // 导通损耗
    // P_cond = I²_rms × Rds(on)
    float i_rms = iout;  // 简化计算
    params->rds_on = 0.01;  // 目标值，越小越好
    float p_conduction = i_rms * i_rms * params->rds_on;
    
    // 开关损耗
    // P_sw = 0.5 × Vin × Iout × (tr + tf) × f
    float t_rise = 20e-9;   // 上升时间 20ns
    float t_fall = 20e-9;   // 下降时间 20ns
    float p_switching = 0.5 * vin * iout * (t_rise + t_fall) * freq;
    
    // 总功耗
    params->power_loss = p_conduction + p_switching;
    
    // 栅极电荷（影响驱动损耗）
    params->qg_total = 20;  // nC，越小越好
}

// 示例选型
// Vin = 12V, Iout = 2A, f = 200kHz
// 要求：
// - Vds > 24V (选择30V或40V)
// - Id > 4A (选择5A或更大)
// - Rds(on) < 10mΩ
// - Qg < 30nC
// 
// 推荐型号：
// - IRF3205 (55V, 110A, 8mΩ)
// - IRFZ44N (55V, 49A, 17.5mΩ)
// - Si2302 (20V, 2.3A, 85mΩ) - 小功率
```

**步骤5：选择续流二极管**：

```c
/**
 * @brief  二极管选型参数
 */
typedef struct {
    float vr_max;       // 最大反向电压 (V)
    float if_avg;       // 平均正向电流 (A)
    float vf;           // 正向压降 (V)
    float trr;          // 反向恢复时间 (ns)
    float power_loss;   // 功耗 (W)
} Diode_Params_t;

/**
 * @brief  计算二极管选型参数
 */
void buck_select_diode(float vin, float vout, float iout, 
                       float duty, Diode_Params_t *params)
{
    // 反向电压：输入电压 + 裕量
    params->vr_max = vin * 1.5;
    
    // 平均电流：(1-D) × Iout
    params->if_avg = (1.0 - duty) * iout;
    
    // 肖特基二极管正向压降
    params->vf = 0.3;  // 0.2-0.4V
    
    // 反向恢复时间（肖特基几乎为0）
    params->trr = 10;  // ns
    
    // 二极管功耗
    // P_diode = Vf × If_avg
    params->power_loss = params->vf * params->if_avg;
}

// 示例选型
// Vin = 12V, Vout = 5V, Iout = 2A, D = 0.417
// 要求：
// - Vr > 18V (选择20V或30V)
// - If > 1.2A (选择2A或3A)
// - Vf < 0.4V
// - 肖特基二极管
//
// 推荐型号：
// - SS34 (40V, 3A, Vf=0.5V)
// - 1N5819 (40V, 1A, Vf=0.6V)
// - MBRS340 (40V, 3A, Vf=0.5V)
```

### 2.3 Buck转换器完整设计实例

**完整的Buck转换器实现**：

```c
/**
 * @file    buck_converter.c
 * @brief   Buck降压转换器完整实现
 * @author  嵌入式知识平台
 */

#include <stdint.h>
#include <stdbool.h>
#include "stm32f1xx_hal.h"

/* 硬件配置 */
#define BUCK_PWM_TIMER          TIM1
#define BUCK_PWM_CHANNEL        TIM_CHANNEL_1
#define BUCK_PWM_FREQUENCY      200000      // 200kHz
#define BUCK_ADC_VOUT           ADC_CHANNEL_0
#define BUCK_ADC_IOUT           ADC_CHANNEL_1

/* 设计参数 */
#define BUCK_VIN_NOM            12.0f       // 标称输入电压
#define BUCK_VOUT_TARGET        5.0f        // 目标输出电压
#define BUCK_IOUT_MAX           2.0f        // 最大输出电流
#define BUCK_INDUCTANCE         22e-6f      // 22μH
#define BUCK_OUTPUT_CAP         22e-6f      // 22μF

/* 控制参数 */
#define BUCK_DUTY_MIN           0.1f        // 最小占空比
#define BUCK_DUTY_MAX           0.9f        // 最大占空比
#define BUCK_VOUT_TOLERANCE     0.05f       // 5%电压容差

/**
 * @brief  Buck转换器状态结构
 */
typedef struct {
    float vin;              // 输入电压 (V)
    float vout;             // 输出电压 (V)
    float iout;             // 输出电流 (A)
    float duty;             // 当前占空比
    float vout_target;      // 目标输出电压 (V)
    bool enabled;           // 使能状态
    uint32_t fault_flags;   // 故障标志
} Buck_State_t;

/* 全局状态 */
static Buck_State_t g_buck_state = {0};

/* PID控制器参数 */
typedef struct {
    float kp;               // 比例系数
    float ki;               // 积分系数
    float kd;               // 微分系数
    float integral;         // 积分累积
    float prev_error;       // 上次误差
    float output_min;       // 输出最小值
    float output_max;       // 输出最大值
} PID_Controller_t;

static PID_Controller_t g_voltage_pid = {
    .kp = 0.5f,
    .ki = 0.1f,
    .kd = 0.01f,
    .integral = 0.0f,
    .prev_error = 0.0f,
    .output_min = BUCK_DUTY_MIN,
    .output_max = BUCK_DUTY_MAX
};

/**
 * @brief  初始化Buck转换器
 * @retval 0: 成功, -1: 失败
 */
int buck_init(void)
{
    // 初始化PWM定时器
    TIM_HandleTypeDef htim;
    htim.Instance = BUCK_PWM_TIMER;
    htim.Init.Prescaler = 0;
    htim.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim.Init.Period = SystemCoreClock / BUCK_PWM_FREQUENCY - 1;
    htim.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    
    if (HAL_TIM_PWM_Init(&htim) != HAL_OK) {
        return -1;
    }
    
    // 配置PWM通道
    TIM_OC_InitTypeDef sConfigOC = {0};
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 0;  // 初始占空比为0
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    
    if (HAL_TIM_PWM_ConfigChannel(&htim, &sConfigOC, 
                                  BUCK_PWM_CHANNEL) != HAL_OK) {
        return -1;
    }
    
    // 初始化ADC用于电压电流采样
    // ... ADC初始化代码 ...
    
    // 初始化状态
    g_buck_state.vout_target = BUCK_VOUT_TARGET;
    g_buck_state.duty = 0.0f;
    g_buck_state.enabled = false;
    
    return 0;
}

/**
 * @brief  启动Buck转换器
 */
void buck_start(void)
{
    if (!g_buck_state.enabled) {
        // 软启动：从小占空比开始
        g_buck_state.duty = BUCK_DUTY_MIN;
        buck_set_duty_cycle(g_buck_state.duty);
        
        // 启动PWM
        HAL_TIM_PWM_Start(BUCK_PWM_TIMER, BUCK_PWM_CHANNEL);
        
        g_buck_state.enabled = true;
    }
}

/**
 * @brief  停止Buck转换器
 */
void buck_stop(void)
{
    if (g_buck_state.enabled) {
        // 停止PWM
        HAL_TIM_PWM_Stop(BUCK_PWM_TIMER, BUCK_PWM_CHANNEL);
        
        // 清零占空比
        g_buck_state.duty = 0.0f;
        buck_set_duty_cycle(0.0f);
        
        g_buck_state.enabled = false;
    }
}

/**
 * @brief  设置PWM占空比
 * @param  duty: 占空比 (0.0 - 1.0)
 */
void buck_set_duty_cycle(float duty)
{
    // 限制范围
    if (duty < BUCK_DUTY_MIN) duty = BUCK_DUTY_MIN;
    if (duty > BUCK_DUTY_MAX) duty = BUCK_DUTY_MAX;
    
    // 计算CCR值
    uint32_t period = __HAL_TIM_GET_AUTORELOAD(BUCK_PWM_TIMER);
    uint32_t pulse = (uint32_t)(duty * period);
    
    // 设置占空比
    __HAL_TIM_SET_COMPARE(BUCK_PWM_TIMER, BUCK_PWM_CHANNEL, pulse);
    
    g_buck_state.duty = duty;
}

/**
 * @brief  PID控制器更新
 * @param  pid: PID控制器
 * @param  setpoint: 设定值
 * @param  measurement: 测量值
 * @param  dt: 时间间隔 (s)
 * @return 控制输出
 */
float pid_update(PID_Controller_t *pid, float setpoint, 
                 float measurement, float dt)
{
    // 计算误差
    float error = setpoint - measurement;
    
    // 比例项
    float p_term = pid->kp * error;
    
    // 积分项
    pid->integral += error * dt;
    float i_term = pid->ki * pid->integral;
    
    // 微分项
    float derivative = (error - pid->prev_error) / dt;
    float d_term = pid->kd * derivative;
    
    // 总输出
    float output = p_term + i_term + d_term;
    
    // 限幅
    if (output < pid->output_min) {
        output = pid->output_min;
        // 抗积分饱和
        pid->integral -= error * dt;
    }
    if (output > pid->output_max) {
        output = pid->output_max;
        // 抗积分饱和
        pid->integral -= error * dt;
    }
    
    // 保存当前误差
    pid->prev_error = error;
    
    return output;
}

/**
 * @brief  读取输出电压
 * @return 输出电压 (V)
 */
float buck_read_vout(void)
{
    // 启动ADC转换
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 100);
    uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
    
    // 转换为电压值
    // 假设：ADC参考电压3.3V，12位ADC，分压比1:2
    float voltage = (adc_value * 3.3f / 4096.0f) * 2.0f;
    
    return voltage;
}

/**
 * @brief  读取输出电流
 * @return 输出电流 (A)
 */
float buck_read_iout(void)
{
    // 使用电流检测电阻或霍尔传感器
    // 这里假设使用0.1Ω检测电阻 + 运放放大10倍
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 100);
    uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
    
    // 转换为电流值
    float voltage = adc_value * 3.3f / 4096.0f;
    float current = voltage / 10.0f / 0.1f;  // I = V / (Gain × Rsense)
    
    return current;
}

/**
 * @brief  Buck转换器控制循环（定时调用，如1kHz）
 */
void buck_control_loop(void)
{
    if (!g_buck_state.enabled) {
        return;
    }
    
    // 读取输出电压和电流
    g_buck_state.vout = buck_read_vout();
    g_buck_state.iout = buck_read_iout();
    
    // PID控制
    float dt = 0.001f;  // 1ms控制周期
    float new_duty = pid_update(&g_voltage_pid, 
                                g_buck_state.vout_target,
                                g_buck_state.vout, 
                                dt);
    
    // 更新占空比
    buck_set_duty_cycle(new_duty);
    
    // 故障检测
    buck_check_faults();
}

/**
 * @brief  故障检测
 */
void buck_check_faults(void)
{
    g_buck_state.fault_flags = 0;
    
    // 过压保护
    if (g_buck_state.vout > BUCK_VOUT_TARGET * 1.2f) {
        g_buck_state.fault_flags |= (1 << 0);
        buck_stop();
    }
    
    // 欠压保护
    if (g_buck_state.vout < BUCK_VOUT_TARGET * 0.8f) {
        g_buck_state.fault_flags |= (1 << 1);
    }
    
    // 过流保护
    if (g_buck_state.iout > BUCK_IOUT_MAX * 1.2f) {
        g_buck_state.fault_flags |= (1 << 2);
        buck_stop();
    }
}

/**
 * @brief  设置目标输出电压
 * @param  voltage: 目标电压 (V)
 */
void buck_set_output_voltage(float voltage)
{
    g_buck_state.vout_target = voltage;
    
    // 重置PID积分项
    g_voltage_pid.integral = 0.0f;
}

/**
 * @brief  获取Buck转换器状态
 * @return 状态结构指针
 */
const Buck_State_t* buck_get_state(void)
{
    return &g_buck_state;
}
```


## 第三部分：Boost升压转换器设计

### 3.1 Boost转换器原理

Boost转换器用于将低电压升高到更高电压。

**电路结构**：

```
Boost转换器基本电路：

Vin ──[L]──┬──[D1]──┬── Vout
           │        │
          ┌┴┐      ┌┴┐
          │Q│      │C│  Rload
          │1│      │o│
          └┬┘      └┬┘
           │        │
          GND──────GND

组件说明：
- L: 储能电感
- Q1: 功率开关管 (N-MOSFET)
- D1: 整流二极管 (Schottky)
- Co: 输出滤波电容
- Rload: 负载
```

**工作过程**：

```
工作周期分析：

阶段1：Q1导通 (Ton)
┌─────────────────────────┐
│ Vin → L → Q1 → GND      │
│ 电感储能                 │
│ di/dt = Vin/L           │
│ 电感电流线性上升         │
└─────────────────────────┘

阶段2：Q1关断 (Toff)
┌─────────────────────────┐
│ Vin → L → D1 → Vout     │
│ 电感释放能量             │
│ di/dt = (Vin-Vout)/L    │
│ 电感电流下降             │
└─────────────────────────┘

稳态时：
Ton × Vin = Toff × (Vout - Vin)
推导得：
Vout = Vin / (1 - D)
其中 D = Ton / (Ton + Toff)

特点：
- 输出电压总是高于输入电压
- 占空比越大，升压比越高
- D → 1 时，Vout → ∞ (理论上)
- 实际最大占空比约0.8-0.85
```

### 3.2 Boost转换器设计步骤

**设计规格示例**：

```
设计要求：
- 输入电压：Vin = 3.7V (单节锂电池)
- 输出电压：Vout = 5V
- 输出电流：Iout = 1A
- 开关频率：f = 500kHz
- 输出纹波：ΔVout < 50mV
- 效率目标：η > 85%
```

**步骤1：计算占空比**：

```c
/**
 * @brief  计算Boost转换器占空比
 * @param  vin: 输入电压 (V)
 * @param  vout: 输出电压 (V)
 * @return 占空比 (0-1)
 */
float boost_calculate_duty_cycle(float vin, float vout)
{
    // 理想占空比
    // D = 1 - Vin/Vout
    float duty = 1.0f - (vin / vout);
    
    // 考虑二极管压降
    float vd = 0.3f;  // 肖特基二极管压降
    duty = 1.0f - (vin / (vout + vd));
    
    // 限制范围
    if (duty < 0.1f) duty = 0.1f;
    if (duty > 0.85f) duty = 0.85f;  // 实际最大值
    
    return duty;
}

// 示例计算
// Vin = 3.7V, Vout = 5V
// D = 1 - 3.7/5 = 0.26 (26%)
```

**步骤2：选择电感值**：

```c
/**
 * @brief  计算Boost转换器电感值
 * @param  vin: 输入电压 (V)
 * @param  iout: 输出电流 (A)
 * @param  vout: 输出电压 (V)
 * @param  freq: 开关频率 (Hz)
 * @param  ripple_ratio: 电流纹波比 (0.2-0.4)
 * @return 电感值 (H)
 */
float boost_calculate_inductance(float vin, float iout, 
                                 float vout, float freq,
                                 float ripple_ratio)
{
    // 输入电流（大于输出电流）
    float iin = iout * vout / vin / 0.9f;  // 考虑效率
    
    // 电感电流纹波
    float delta_il = iin * ripple_ratio;
    
    // 占空比
    float duty = 1.0f - (vin / vout);
    
    // 电感值计算
    // L = Vin × D / (f × ΔIL)
    float inductance = vin * duty / (freq * delta_il);
    
    return inductance;
}

// 示例计算
// Vin = 3.7V, Vout = 5V, Iout = 1A
// f = 500kHz, ripple = 30%
// Iin ≈ 1.5A
// ΔIL = 1.5A × 0.3 = 0.45A
// L = 3.7 × 0.26 / (500000 × 0.45)
// L = 4.3 μH
// 选择标准值：L = 4.7μH
```

**步骤3：选择输出电容**：

```c
/**
 * @brief  计算Boost转换器输出电容
 * @param  iout: 输出电流 (A)
 * @param  duty: 占空比
 * @param  freq: 开关频率 (Hz)
 * @param  delta_vout: 允许的输出电压纹波 (V)
 * @return 输出电容值 (F)
 */
float boost_calculate_output_capacitance(float iout, float duty,
                                         float freq, 
                                         float delta_vout)
{
    // Boost输出电容计算
    // Co = Iout × D / (f × ΔVout)
    float capacitance = iout * duty / (freq * delta_vout);
    
    return capacitance;
}

// 示例计算
// Iout = 1A, D = 0.26, f = 500kHz, ΔVout = 50mV
// Co = 1 × 0.26 / (500000 × 0.05)
// Co = 10.4 μF
// 选择：Co = 22μF (低ESR陶瓷电容)
```

### 3.3 Boost转换器完整实现

```c
/**
 * @file    boost_converter.c
 * @brief   Boost升压转换器完整实现
 */

#include <stdint.h>
#include <stdbool.h>
#include "stm32f1xx_hal.h"

/* 设计参数 */
#define BOOST_VIN_NOM           3.7f        // 标称输入电压
#define BOOST_VOUT_TARGET       5.0f        // 目标输出电压
#define BOOST_IOUT_MAX          1.0f        // 最大输出电流
#define BOOST_PWM_FREQUENCY     500000      // 500kHz
#define BOOST_INDUCTANCE        4.7e-6f     // 4.7μH
#define BOOST_OUTPUT_CAP        22e-6f      // 22μF

/**
 * @brief  Boost转换器状态
 */
typedef struct {
    float vin;              // 输入电压
    float vout;             // 输出电压
    float iin;              // 输入电流
    float iout;             // 输出电流
    float duty;             // 占空比
    float vout_target;      // 目标输出电压
    bool enabled;           // 使能状态
    uint32_t fault_flags;   // 故障标志
} Boost_State_t;

static Boost_State_t g_boost_state = {0};

/**
 * @brief  初始化Boost转换器
 */
int boost_init(void)
{
    // PWM初始化（类似Buck）
    // ... PWM配置代码 ...
    
    // ADC初始化
    // ... ADC配置代码 ...
    
    // 初始化状态
    g_boost_state.vout_target = BOOST_VOUT_TARGET;
    g_boost_state.duty = 0.0f;
    g_boost_state.enabled = false;
    
    return 0;
}

/**
 * @brief  启动Boost转换器（软启动）
 */
void boost_start(void)
{
    if (!g_boost_state.enabled) {
        // 软启动：逐步增加占空比
        for (float d = 0.1f; d < 0.3f; d += 0.01f) {
            boost_set_duty_cycle(d);
            HAL_Delay(10);  // 延迟10ms
        }
        
        g_boost_state.enabled = true;
    }
}

/**
 * @brief  Boost控制循环
 */
void boost_control_loop(void)
{
    if (!g_boost_state.enabled) {
        return;
    }
    
    // 读取电压电流
    g_boost_state.vin = boost_read_vin();
    g_boost_state.vout = boost_read_vout();
    g_boost_state.iin = boost_read_iin();
    g_boost_state.iout = boost_read_iout();
    
    // 计算理论占空比
    float duty_ideal = 1.0f - (g_boost_state.vin / 
                               g_boost_state.vout_target);
    
    // PID微调
    float error = g_boost_state.vout_target - g_boost_state.vout;
    float duty_correction = error * 0.01f;  // 简单比例控制
    
    float new_duty = duty_ideal + duty_correction;
    
    // 限制占空比
    if (new_duty < 0.1f) new_duty = 0.1f;
    if (new_duty > 0.85f) new_duty = 0.85f;
    
    boost_set_duty_cycle(new_duty);
    
    // 故障检测
    boost_check_faults();
}

/**
 * @brief  Boost故障检测
 */
void boost_check_faults(void)
{
    g_boost_state.fault_flags = 0;
    
    // 输入欠压
    if (g_boost_state.vin < 2.5f) {
        g_boost_state.fault_flags |= (1 << 0);
        boost_stop();
    }
    
    // 输出过压
    if (g_boost_state.vout > BOOST_VOUT_TARGET * 1.2f) {
        g_boost_state.fault_flags |= (1 << 1);
        boost_stop();
    }
    
    // 输入过流
    if (g_boost_state.iin > 3.0f) {
        g_boost_state.fault_flags |= (1 << 2);
        boost_stop();
    }
}
```

## 第四部分：Buck-Boost转换器设计

### 4.1 Buck-Boost转换器原理

Buck-Boost转换器可以实现升压或降压，输出电压极性与输入相反。

**电路结构**：

```
Buck-Boost转换器（反相）：

Vin ──┬──[Q1]──[L]──┬──[D1]──┬── -Vout
      │             │        │
     ┌┴┐           GND      ┌┴┐
     │C│                    │C│  Rload
     │i│                    │o│
     │n│                    └┬┘
     └┬┘                     │
      │                      │
     GND─────────────────────┘

输出电压：
Vout = -Vin × D / (1 - D)

特点：
- 输出电压极性相反
- 可升压可降压
- 输入输出不共地
```

**非反相Buck-Boost（SEPIC/Cuk）**：

```
SEPIC拓扑（同相升降压）：

Vin ──[L1]──┬──[Q1]──┬──[L2]──┬── Vout
            │        │        │
           ┌┴┐      ┌┴┐      ┌┴┐
           │C│      │C│      │C│  Rload
           │1│      │c│      │o│
           └┬┘      └┬┘      └┬┘
            │        │        │
           GND──────GND──────GND

优点：
- 输出同相
- 输入输出共地
- 输入电流连续

缺点：
- 元件多
- 成本高
- 设计复杂
```

### 4.2 四开关Buck-Boost设计

现代方案：使用四个开关实现非反相升降压。

**电路结构**：

```
四开关Buck-Boost：

        Q1        Q3
Vin ──┬─[S]─┬──[L]──┬─[S]─┬── Vout
      │     │       │     │
     ┌┴┐   ┌┴┐     ┌┴┐   ┌┴┐
     │C│   │S│     │S│   │C│  Rload
     │i│   │Q│     │Q│   │o│
     │n│   │2│     │4│   └┬┘
     └┬┘   └┬┘     └┬┘    │
      │     │       │      │
     GND───GND─────GND────GND

工作模式：
1. Buck模式 (Vin > Vout)
   - Q1, Q4导通/关断
   - Q2, Q3保持状态

2. Boost模式 (Vin < Vout)
   - Q2, Q3导通/关断
   - Q1, Q4保持状态

3. Buck-Boost模式 (Vin ≈ Vout)
   - 四个开关协调工作
```

**控制策略**：

```c
/**
 * @brief  四开关Buck-Boost控制
 */
typedef enum {
    MODE_BUCK = 0,          // Buck模式
    MODE_BOOST,             // Boost模式
    MODE_BUCK_BOOST         // Buck-Boost模式
} BuckBoost_Mode_t;

/**
 * @brief  选择工作模式
 */
BuckBoost_Mode_t select_operating_mode(float vin, float vout)
{
    float ratio = vin / vout;
    
    if (ratio > 1.1f) {
        // 输入明显高于输出，使用Buck
        return MODE_BUCK;
    }
    else if (ratio < 0.9f) {
        // 输入明显低于输出，使用Boost
        return MODE_BOOST;
    }
    else {
        // 输入接近输出，使用Buck-Boost
        return MODE_BUCK_BOOST;
    }
}

/**
 * @brief  四开关控制
 */
void four_switch_control(BuckBoost_Mode_t mode, float duty)
{
    switch (mode) {
        case MODE_BUCK:
            // Buck模式：Q1和Q4同步开关
            set_switch_q1(duty);        // PWM
            set_switch_q2(0);           // 关断
            set_switch_q3(1);           // 导通
            set_switch_q4(1.0f - duty); // 互补PWM
            break;
            
        case MODE_BOOST:
            // Boost模式：Q2和Q3同步开关
            set_switch_q1(1);           // 导通
            set_switch_q2(1.0f - duty); // 互补PWM
            set_switch_q3(duty);        // PWM
            set_switch_q4(0);           // 关断
            break;
            
        case MODE_BUCK_BOOST:
            // Buck-Boost模式：四开关协调
            // 复杂控制策略
            four_switch_buck_boost_control(duty);
            break;
    }
}
```


## 第五部分：PWM控制技术

### 5.1 PWM控制芯片

常用的PWM控制芯片：

```
控制芯片分类：

1. 电压模式控制
   - TL494 (经典双路PWM)
   - UC3842/3843 (电流模式)
   - SG3525 (推挽式)

2. 电流模式控制
   - UC3842/3843
   - LM2596 (集成开关)
   - LM2577 (Boost)

3. 同步整流控制
   - LTC3780 (Buck-Boost)
   - TPS54360 (Buck)
   - LM27313 (Boost)

4. 数字控制
   - UCD3138 (数字电源)
   - MCU + PWM外设
```

### 5.2 使用TL494设计Buck转换器

**TL494引脚功能**：

```
TL494引脚定义：

1  - IN1+      误差放大器1正输入
2  - IN1-      误差放大器1负输入
3  - FB        反馈输入
4  - DTC       死区时间控制
5  - CT         振荡器定时电容
6  - RT         振荡器定时电阻
7  - GND        地
8  - C1         补偿电容1
9  - E1         发射极1
10 - E2         发射极2
11 - C2         补偿电容2
12 - VCC        电源 (7-40V)
13 - OUT_CTRL   输出控制
14 - REF        5V基准输出
15 - IN2+       误差放大器2正输入
16 - IN2-       误差放大器2负输入

振荡频率：
f = 1 / (RT × CT)
```

**TL494 Buck转换器电路**：

```c
/**
 * @brief  TL494参数计算
 */

// 振荡频率设置
// 目标频率：100kHz
// 选择：CT = 1nF
// 计算：RT = 1 / (f × CT) = 1 / (100000 × 1e-9) = 10kΩ

// 反馈分压电阻
// Vout = 5V, Vref = 5V
// R1 / (R1 + R2) = Vref / Vout
// 选择：R1 = 10kΩ, R2 = 0 (直接反馈)

// 死区时间控制
// DTC引脚接地：0%死区
// DTC引脚接Vref：最大死区

/**
 * @brief  TL494应用电路示例
 */
const char* tl494_circuit = 
"TL494 Buck转换器电路：\n"
"\n"
"Vin(12V) ──┬── VCC(12)\n"
"           │\n"
"          ┌┴────────────┐\n"
"          │   TL494     │\n"
"  10kΩ ───┤RT(6)        │\n"
"  1nF  ───┤CT(5)        │\n"
"          │             │\n"
"  Vout ───┤FB(3)        │\n"
"          │             │\n"
"  GND  ───┤DTC(4)       │\n"
"          │             │\n"
"          │      E1(9)──┼── MOSFET Gate\n"
"          │      E2(10)─┼── (不用)\n"
"          │             │\n"
"         GND(7)        REF(14)── 5V输出\n"
"          └─────────────┘\n";
```

### 5.3 使用UC3842设计Boost转换器

**UC3842特性**：

```
UC3842/3843特性：

- 电流模式PWM控制
- 内置误差放大器
- 内置振荡器
- 欠压锁定 (UVLO)
- 最大占空比限制
- 输出驱动能力：1A

引脚定义：
1 - COMP      补偿
2 - VFB       电压反馈
3 - ISENSE    电流检测
4 - RT/CT     振荡器
5 - GND       地
6 - OUT       输出驱动
7 - VCC       电源
8 - VREF      5V基准
```

**UC3842 Boost转换器设计**：

```c
/**
 * @brief  UC3842 Boost转换器参数计算
 */

// 振荡频率设置
// f = 1.8 / (RT × CT)
// 目标：200kHz
// 选择：CT = 1nF
// RT = 1.8 / (200000 × 1e-9) = 9kΩ

// 电流检测电阻
// Rsense = 1V / Ipeak
// Ipeak = 2 × Iin_avg (Boost)
// Iin_avg = Pout / (Vin × η) = 5W / (3.7V × 0.85) = 1.59A
// Ipeak = 3.18A
// Rsense = 1V / 3.18A = 0.31Ω
// 选择：Rsense = 0.3Ω, 2W

// 反馈分压
// Vout = 5V, Vref = 2.5V
// R1 / (R1 + R2) = Vref / Vout = 2.5 / 5 = 0.5
// 选择：R1 = 10kΩ, R2 = 10kΩ

/**
 * @brief  UC3842电路连接
 */
void uc3842_circuit_description(void)
{
    /*
    UC3842 Boost电路：
    
    Vin ──[L]──┬──[D]──┬── Vout(5V)
               │       │
              ┌┴┐     ┌┴┐
              │Q│     │C│  Rload
              │ │     │o│
              └┬┘     └┬┘
               │       │
            [Rsense]   ├─[R1]─┬─[R2]─GND
               │       │       │
              GND      │      VFB(2)
                       │
                    ┌──┴──────────┐
                    │   UC3842    │
                    │             │
            9kΩ  ───┤RT/CT(4)     │
            1nF  ───┤             │
                    │      OUT(6)─┼── Q Gate
                    │             │
                   GND(5)    VCC(7)── 12V
                    └─────────────┘
    */
}
```

### 5.4 MCU实现PWM控制

使用STM32实现完整的PWM控制：

```c
/**
 * @file    mcu_pwm_control.c
 * @brief   MCU实现开关电源PWM控制
 */

#include "stm32f1xx_hal.h"

/* PWM配置 */
#define PWM_FREQUENCY       200000      // 200kHz
#define PWM_TIMER           TIM1
#define PWM_CHANNEL         TIM_CHANNEL_1
#define PWM_RESOLUTION      1000        // 10位分辨率

/* ADC通道 */
#define ADC_VOUT_CHANNEL    ADC_CHANNEL_0
#define ADC_IOUT_CHANNEL    ADC_CHANNEL_1
#define ADC_VIN_CHANNEL     ADC_CHANNEL_2

/**
 * @brief  初始化PWM
 */
int pwm_init(void)
{
    TIM_HandleTypeDef htim;
    
    // 计算定时器参数
    uint32_t timer_clock = HAL_RCC_GetPCLK1Freq() * 2;
    uint32_t prescaler = 0;
    uint32_t period = timer_clock / PWM_FREQUENCY - 1;
    
    // 如果period太大，使用预分频
    while (period > 65535) {
        prescaler++;
        period = timer_clock / (prescaler + 1) / PWM_FREQUENCY - 1;
    }
    
    // 配置定时器
    htim.Instance = PWM_TIMER;
    htim.Init.Prescaler = prescaler;
    htim.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim.Init.Period = period;
    htim.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim.Init.RepetitionCounter = 0;
    
    if (HAL_TIM_PWM_Init(&htim) != HAL_OK) {
        return -1;
    }
    
    // 配置PWM通道
    TIM_OC_InitTypeDef sConfigOC = {0};
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 0;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
    sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
    
    if (HAL_TIM_PWM_ConfigChannel(&htim, &sConfigOC, 
                                  PWM_CHANNEL) != HAL_OK) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief  设置PWM占空比
 * @param  duty: 占空比 (0.0 - 1.0)
 */
void pwm_set_duty(float duty)
{
    // 限制范围
    if (duty < 0.0f) duty = 0.0f;
    if (duty > 1.0f) duty = 1.0f;
    
    // 计算CCR值
    uint32_t period = __HAL_TIM_GET_AUTORELOAD(&htim1);
    uint32_t pulse = (uint32_t)(duty * period);
    
    // 设置比较值
    __HAL_TIM_SET_COMPARE(&htim1, PWM_CHANNEL, pulse);
}

/**
 * @brief  启动PWM输出
 */
void pwm_start(void)
{
    HAL_TIM_PWM_Start(&htim1, PWM_CHANNEL);
}

/**
 * @brief  停止PWM输出
 */
void pwm_stop(void)
{
    HAL_TIM_PWM_Stop(&htim1, PWM_CHANNEL);
}

/**
 * @brief  PWM频率可调
 * @param  frequency: 目标频率 (Hz)
 */
void pwm_set_frequency(uint32_t frequency)
{
    uint32_t timer_clock = HAL_RCC_GetPCLK1Freq() * 2;
    uint32_t period = timer_clock / frequency - 1;
    
    __HAL_TIM_SET_AUTORELOAD(&htim1, period);
}
```

## 第六部分：元件选型指南

### 6.1 电感选型

电感是开关电源的核心元件。

**电感参数**：

```
电感关键参数：

1. 电感值 (L)
   - 决定电流纹波
   - 影响动态响应
   - 典型值：1μH - 100μH

2. 饱和电流 (Isat)
   - 电感值下降10-30%时的电流
   - 必须 > 峰值电流
   - 留20-30%裕量

3. 额定电流 (Irms)
   - 温升限制的电流
   - 必须 > RMS电流
   - 留20-30%裕量

4. 直流电阻 (DCR)
   - 影响效率
   - 越小越好
   - 典型：几十mΩ

5. 封装尺寸
   - 功率越大，体积越大
   - 屏蔽式 vs 非屏蔽式
   - SMD vs 插件

电感类型：
- 铁粉芯：成本低，饱和特性软
- 铁氧体：高频特性好，饱和特性硬
- 合金粉芯：性能好，成本高
```

**电感选型步骤**：

```c
/**
 * @brief  电感选型计算
 */
typedef struct {
    float inductance;       // 电感值 (H)
    float isat_min;         // 最小饱和电流 (A)
    float irms_min;         // 最小额定电流 (A)
    float dcr_max;          // 最大直流电阻 (Ω)
    float peak_current;     // 峰值电流 (A)
    float rms_current;      // RMS电流 (A)
} Inductor_Spec_t;

/**
 * @brief  计算电感规格
 */
void calculate_inductor_spec(float vin, float vout, 
                            float iout, float freq,
                            Inductor_Spec_t *spec)
{
    // 计算电感值
    float duty = vout / vin;  // Buck示例
    float delta_il = iout * 0.3f;  // 30%纹波
    spec->inductance = (vin - vout) * duty / (freq * delta_il);
    
    // 计算峰值电流
    spec->peak_current = iout + delta_il / 2.0f;
    
    // 饱和电流要求（1.3倍裕量）
    spec->isat_min = spec->peak_current * 1.3f;
    
    // RMS电流（Buck近似等于输出电流）
    spec->rms_current = iout;
    
    // 额定电流要求（1.2倍裕量）
    spec->irms_min = spec->rms_current * 1.2f;
    
    // DCR要求（损耗 < 1%）
    spec->dcr_max = 0.01f * vout / spec->rms_current;
}

// 示例选型
// Vin=12V, Vout=5V, Iout=2A, f=200kHz
// 计算结果：
// - L = 24μH
// - Isat > 2.8A
// - Irms > 2.4A
// - DCR < 25mΩ
//
// 推荐型号：
// - Coilcraft MSS1260-223 (22μH, 3.5A, 2.8A, 23mΩ)
// - Wurth 744 043 220 (22μH, 4.2A, 3.5A, 18mΩ)
```

### 6.2 电容选型

**输入电容选型**：

```
输入电容要求：

1. 容值
   - 提供瞬态电流
   - 滤除输入纹波
   - 典型：10μF - 100μF

2. 耐压
   - 1.5-2倍输入电压
   - 考虑瞬态过压

3. ESR (等效串联电阻)
   - 影响纹波电压
   - 越小越好
   - 陶瓷电容ESR最小

4. 纹波电流额定值
   - 必须 > RMS纹波电流
   - 留50%裕量

电容类型选择：
- 陶瓷电容：ESR低，体积小，成本适中
- 电解电容：容值大，ESR较高，寿命受温度影响
- 钽电容：性能好，成本高，有失效风险
```

**输出电容选型**：

```c
/**
 * @brief  输出电容选型
 */
typedef struct {
    float capacitance;      // 电容值 (F)
    float voltage_rating;   // 耐压 (V)
    float esr_max;          // 最大ESR (Ω)
    float ripple_current;   // 纹波电流 (A)
} Capacitor_Spec_t;

/**
 * @brief  计算输出电容规格
 */
void calculate_output_cap_spec(float vout, float iout,
                               float delta_il, float freq,
                               float delta_vout,
                               Capacitor_Spec_t *spec)
{
    // 容值计算（基于纹波要求）
    spec->capacitance = delta_il / (8.0f * freq * delta_vout);
    
    // 耐压（1.5倍裕量）
    spec->voltage_rating = vout * 1.5f;
    
    // ESR要求
    // ΔVout_esr = ΔIL × ESR
    spec->esr_max = delta_vout / delta_il;
    
    // 纹波电流（RMS）
    // Ic_rms ≈ ΔIL / (2√3)
    spec->ripple_current = delta_il / (2.0f * 1.732f);
}

// 示例
// Vout=5V, Iout=2A, ΔIL=0.6A, f=200kHz, ΔVout=50mV
// 结果：
// - C > 7.5μF
// - Vrating > 7.5V (选10V或16V)
// - ESR < 83mΩ
// - Iripple > 0.17A
//
// 推荐：
// - 22μF/10V X7R陶瓷电容
// - 或 2×10μF/10V 并联
```


### 6.3 MOSFET选型详解

**MOSFET关键参数**：

```
MOSFET参数详解：

1. Vds (漏源击穿电压)
   - 必须 > 最大输入电压
   - 留1.5-2倍裕量
   - 考虑瞬态尖峰

2. Id (漏极电流)
   - 连续电流额定值
   - 必须 > 最大负载电流
   - 留1.5-2倍裕量

3. Rds(on) (导通电阻)
   - 影响导通损耗
   - 越小越好
   - 注意温度系数

4. Qg (总栅极电荷)
   - 影响开关速度
   - 影响驱动损耗
   - 越小越好

5. Ciss, Coss, Crss (寄生电容)
   - 影响开关特性
   - Crss (米勒电容) 影响最大

6. 封装
   - TO-220, TO-263, SO-8等
   - 散热能力
   - PCB面积

损耗计算：
P_cond = I²_rms × Rds(on)
P_sw = 0.5 × Vin × Iout × (tr + tf) × f
P_gate = Qg × Vgs × f
P_total = P_cond + P_sw + P_gate
```

**MOSFET选型实例**：

```c
/**
 * @brief  MOSFET损耗计算
 */
typedef struct {
    float p_conduction;     // 导通损耗 (W)
    float p_switching;      // 开关损耗 (W)
    float p_gate;           // 栅极驱动损耗 (W)
    float p_total;          // 总损耗 (W)
    float efficiency;       // 效率
    float tj_max;           // 最大结温 (°C)
} MOSFET_Loss_t;

/**
 * @brief  计算MOSFET损耗
 */
void calculate_mosfet_loss(float vin, float iout, float duty,
                          float rds_on, float qg, float freq,
                          float tr, float tf,
                          MOSFET_Loss_t *loss)
{
    // 导通损耗
    float i_rms = iout * sqrtf(duty);  // Buck RMS电流
    loss->p_conduction = i_rms * i_rms * rds_on;
    
    // 开关损耗
    loss->p_switching = 0.5f * vin * iout * (tr + tf) * freq;
    
    // 栅极驱动损耗
    float vgs = 10.0f;  // 栅极驱动电压
    loss->p_gate = qg * 1e-9f * vgs * freq;
    
    // 总损耗
    loss->p_total = loss->p_conduction + 
                    loss->p_switching + 
                    loss->p_gate;
    
    // 效率影响
    float p_out = iout * vin * duty;  // 输出功率
    loss->efficiency = p_out / (p_out + loss->p_total);
}

// 示例计算
// Vin=12V, Iout=2A, D=0.417, f=200kHz
// MOSFET: Rds(on)=10mΩ, Qg=20nC, tr=tf=20ns
//
// 结果：
// P_cond = (2×√0.417)² × 0.01 = 0.17W
// P_sw = 0.5 × 12 × 2 × 40e-9 × 200000 = 0.096W
// P_gate = 20e-9 × 10 × 200000 = 0.04W
// P_total = 0.306W
// η_loss = 0.306 / (5 + 0.306) = 5.8%
```

### 6.4 二极管选型

**肖特基二极管 vs 快恢复二极管**：

```
二极管类型对比：

肖特基二极管 (Schottky)：
优点：
- 正向压降低 (0.2-0.4V)
- 反向恢复时间极短 (几乎为0)
- 开关损耗小
- 效率高

缺点：
- 反向漏电流大
- 耐压较低 (通常<200V)
- 温度特性较差

应用：
- 低压大电流场合
- 高频开关电源
- Buck/Boost续流二极管

快恢复二极管 (Fast Recovery)：
优点：
- 耐压高
- 反向漏电流小
- 温度特性好

缺点：
- 正向压降高 (0.8-1.2V)
- 有反向恢复时间
- 效率较低

应用：
- 高压场合
- 工频整流
- PFC电路

超快恢复二极管 (Ultra Fast)：
- 介于两者之间
- trr < 50ns
- 适合中高压场合
```

**二极管选型计算**：

```c
/**
 * @brief  二极管损耗计算
 */
typedef struct {
    float p_conduction;     // 导通损耗 (W)
    float p_reverse;        // 反向恢复损耗 (W)
    float p_total;          // 总损耗 (W)
} Diode_Loss_t;

/**
 * @brief  计算二极管损耗
 */
void calculate_diode_loss(float if_avg, float vf,
                         float vin, float freq,
                         float trr, float qrr,
                         Diode_Loss_t *loss)
{
    // 导通损耗
    loss->p_conduction = if_avg * vf;
    
    // 反向恢复损耗
    // P_rr = 0.5 × Vin × Qrr × f
    loss->p_reverse = 0.5f * vin * qrr * 1e-9f * freq;
    
    // 总损耗
    loss->p_total = loss->p_conduction + loss->p_reverse;
}

// 肖特基二极管示例
// If_avg=1.2A, Vf=0.3V, Vin=12V, f=200kHz
// trr≈0, Qrr≈0
// P_cond = 1.2 × 0.3 = 0.36W
// P_rr ≈ 0W
// P_total = 0.36W

// 快恢复二极管示例
// If_avg=1.2A, Vf=1.0V, Vin=12V, f=200kHz
// trr=35ns, Qrr=50nC
// P_cond = 1.2 × 1.0 = 1.2W
// P_rr = 0.5 × 12 × 50e-9 × 200000 = 0.06W
// P_total = 1.26W
//
// 结论：肖特基效率更高！
```

## 第七部分：反馈控制与补偿

### 7.1 电压反馈原理

**反馈网络设计**：

```
电压反馈电路：

Vout ──┬──[R1]──┬── VFB (到控制器)
       │        │
      ┌┴┐      ┌┴┐
      │ │      │R│
      │L│      │2│
      │o│      └┬┘
      │a│       │
      │d│      GND
      └─┘

分压比：
VFB = Vout × R2 / (R1 + R2)

设计要求：
VFB = Vref (控制器基准电压)

电阻选择：
- 总电阻：10kΩ - 100kΩ
- 太小：功耗大
- 太大：噪声敏感

示例：
Vout = 5V, Vref = 1.25V
R2 / (R1 + R2) = 1.25 / 5 = 0.25
选择：R2 = 10kΩ, R1 = 30kΩ
```

**误差放大器**：

```c
/**
 * @brief  误差放大器传递函数
 */

// Type II补偿网络
// 一个零点，两个极点
//
//        R2
// Vout ──┬──────┬── VFB
//        │      │
//       ┌┴┐    ┌┴┐
//       │R│    │C│
//       │1│    │1│
//       └┬┘    └┬┘
//        │      │
//       ┌┴┐    ┌┴┐
//       │C│    │R│
//       │2│    │3│
//       └┬┘    └┬┘
//        │      │
//       GND    GND

// 零点频率：
// fz = 1 / (2π × R1 × C1)

// 极点频率：
// fp1 = 1 / (2π × R2 × C1)
// fp2 = 1 / (2π × R3 × C2)

// 设计步骤：
// 1. 零点放在LC谐振频率之前
// 2. 极点放在开关频率之前
// 3. 保证足够的相位裕度 (>45°)

/**
 * @brief  Type II补偿网络设计
 */
typedef struct {
    float r1, r2, r3;       // 电阻值 (Ω)
    float c1, c2;           // 电容值 (F)
    float fz;               // 零点频率 (Hz)
    float fp1, fp2;         // 极点频率 (Hz)
} TypeII_Comp_t;

/**
 * @brief  设计Type II补偿网络
 */
void design_type2_compensation(float fc, float fsw,
                               TypeII_Comp_t *comp)
{
    // 交越频率：开关频率的1/10
    fc = fsw / 10.0f;
    
    // 零点：交越频率的1/5
    comp->fz = fc / 5.0f;
    
    // 极点1：交越频率的5倍
    comp->fp1 = fc * 5.0f;
    
    // 极点2：开关频率的1/2
    comp->fp2 = fsw / 2.0f;
    
    // 选择C1
    comp->c1 = 100e-9f;  // 100nF
    
    // 计算R1
    comp->r1 = 1.0f / (2.0f * 3.14159f * comp->fz * comp->c1);
    
    // 计算R2
    comp->r2 = 1.0f / (2.0f * 3.14159f * comp->fp1 * comp->c1);
    
    // 选择C2
    comp->c2 = 10e-9f;  // 10nF
    
    // 计算R3
    comp->r3 = 1.0f / (2.0f * 3.14159f * comp->fp2 * comp->c2);
}

// 示例：fsw = 200kHz
// fc = 20kHz
// fz = 4kHz
// fp1 = 100kHz
// fp2 = 100kHz
// C1 = 100nF
// R1 = 398Ω (选390Ω)
// R2 = 15.9Ω (选15Ω)
// C2 = 10nF
// R3 = 159Ω (选160Ω)
```

### 7.2 电流模式控制

**电流模式控制原理**：

```
电流模式控制优点：

1. 内环电流控制
   - 逐周期限流
   - 快速响应
   - 自动斜率补偿

2. 简化补偿
   - 单极点系统
   - 补偿网络简单
   - 稳定性好

3. 并联均流
   - 多相电源
   - 负载均衡
   - 模块化设计

电流检测方法：
1. 检测电阻
   - 精度高
   - 功耗大
   - 成本低

2. DCR检测
   - 利用电感DCR
   - 无额外损耗
   - 需要RC网络

3. 霍尔传感器
   - 隔离检测
   - 无损耗
   - 成本高
```

**斜率补偿**：

```c
/**
 * @brief  斜率补偿计算
 */

// 为什么需要斜率补偿？
// 当占空比 > 50% 时，电流模式控制会出现次谐波振荡

// 斜率补偿原理：
// 在电流检测信号上叠加一个斜坡信号

// 补偿斜率计算：
// Se > 0.5 × Sn
// 其中：
// Se: 补偿斜率
// Sn: 电感电流下降斜率 = (Vout + Vd) / L

/**
 * @brief  计算所需补偿斜率
 */
float calculate_slope_compensation(float vout, float vd,
                                  float inductance, float fsw)
{
    // 电感电流下降斜率
    float sn = (vout + vd) / inductance;
    
    // 所需补偿斜率（取0.6倍安全系数）
    float se = 0.6f * sn;
    
    // 补偿电压幅度
    float v_comp = se * inductance / fsw;
    
    return v_comp;
}

// 示例：
// Vout = 5V, Vd = 0.3V, L = 22μH, fsw = 200kHz
// Sn = 5.3 / 22e-6 = 240,909 A/s
// Se = 0.6 × 240,909 = 144,545 A/s
// V_comp = 144,545 × 22e-6 / 200000 = 15.9mV
```

### 7.3 数字控制实现

使用MCU实现数字PID控制：

```c
/**
 * @file    digital_control.c
 * @brief   数字PID控制实现
 */

/**
 * @brief  数字PID控制器
 */
typedef struct {
    // PID参数
    float kp;               // 比例系数
    float ki;               // 积分系数
    float kd;               // 微分系数
    
    // 状态变量
    float integral;         // 积分累积
    float prev_error;       // 上次误差
    float prev_output;      // 上次输出
    
    // 限幅
    float output_min;       // 输出最小值
    float output_max;       // 输出最大值
    float integral_max;     // 积分限幅
    
    // 采样时间
    float dt;               // 采样周期 (s)
} Digital_PID_t;

/**
 * @brief  初始化数字PID
 */
void digital_pid_init(Digital_PID_t *pid, float kp, float ki,
                     float kd, float dt)
{
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->dt = dt;
    
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_output = 0.0f;
    
    pid->output_min = 0.0f;
    pid->output_max = 1.0f;
    pid->integral_max = 0.5f;
}

/**
 * @brief  数字PID更新（位置式）
 */
float digital_pid_update(Digital_PID_t *pid, 
                        float setpoint, 
                        float measurement)
{
    // 计算误差
    float error = setpoint - measurement;
    
    // 比例项
    float p_term = pid->kp * error;
    
    // 积分项（梯形积分）
    pid->integral += (error + pid->prev_error) * pid->dt / 2.0f;
    
    // 积分限幅（抗饱和）
    if (pid->integral > pid->integral_max) {
        pid->integral = pid->integral_max;
    }
    if (pid->integral < -pid->integral_max) {
        pid->integral = -pid->integral_max;
    }
    
    float i_term = pid->ki * pid->integral;
    
    // 微分项（一阶滤波）
    float derivative = (error - pid->prev_error) / pid->dt;
    float alpha = 0.1f;  // 滤波系数
    derivative = alpha * derivative + 
                 (1.0f - alpha) * pid->prev_output;
    float d_term = pid->kd * derivative;
    
    // 总输出
    float output = p_term + i_term + d_term;
    
    // 输出限幅
    if (output > pid->output_max) {
        output = pid->output_max;
    }
    if (output < pid->output_min) {
        output = pid->output_min;
    }
    
    // 保存状态
    pid->prev_error = error;
    pid->prev_output = output;
    
    return output;
}

/**
 * @brief  增量式PID
 */
float digital_pid_incremental(Digital_PID_t *pid,
                             float setpoint,
                             float measurement)
{
    // 当前误差
    float error = setpoint - measurement;
    
    // 增量计算
    float delta_output = pid->kp * (error - pid->prev_error) +
                        pid->ki * error * pid->dt +
                        pid->kd * (error - 2.0f * pid->prev_error + 
                                  pid->prev_output) / pid->dt;
    
    // 累加输出
    float output = pid->prev_output + delta_output;
    
    // 限幅
    if (output > pid->output_max) output = pid->output_max;
    if (output < pid->output_min) output = pid->output_min;
    
    // 保存状态
    pid->prev_output = pid->prev_error;
    pid->prev_error = error;
    pid->prev_output = output;
    
    return output;
}

/**
 * @brief  PID参数自整定（Ziegler-Nichols方法）
 */
void pid_auto_tune(Digital_PID_t *pid, float ku, float tu)
{
    // Ku: 临界增益
    // Tu: 临界周期
    
    // 经典PID参数
    pid->kp = 0.6f * ku;
    pid->ki = 1.2f * ku / tu;
    pid->kd = 0.075f * ku * tu;
}
```

