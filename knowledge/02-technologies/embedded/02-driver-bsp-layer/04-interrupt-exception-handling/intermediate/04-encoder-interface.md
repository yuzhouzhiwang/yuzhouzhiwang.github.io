---
title: "编码器接口与速度测量：正交编码器驱动开发"
description: "深入讲解增量式正交编码器的工作原理，基于STM32定时器编码器模式实现高精度位置和速度测量，涵盖M法、T法、M/T法测速算法及抗干扰处理，适用于电机控制和机器人开发"
slug: "encoder-interface-speed-measurement"

domain: "驱动与BSP层"
module: "中断与异常处理"
content_type: "tutorial"
skill_level: "intermediate"

tags:
  - 编码器
  - 正交编码器
  - 速度测量
  - 定时器
  - 电机控制
  - STM32
prerequisites:
  - "interrupt-basics"
  - "timer-basics"
related_contents:
  - "interrupt-priority"
  - "interrupt-safety"

estimated_time: 120
difficulty_score: 3

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "2.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - 编码器接口
  - 正交编码器
  - 速度测量算法
  - STM32编码器模式
  - 电机测速
  - 位置控制
  - 闭环控制
cover_image: ""
---

# 编码器接口与速度测量：正交编码器驱动开发

## 概述

增量式正交编码器（Incremental Quadrature Encoder）是电机控制系统中最常用的位置/速度反馈传感器。
它输出两路相位差90°的方波信号（A相和B相），通过计数脉冲数量得到位置，通过单位时间内的脉冲数得到速度。
STM32的定时器内置硬件编码器模式，可以无需CPU干预地自动计数，大幅降低软件开销。

**本文学习目标**：

| 目标 | 技能等级 |
|------|---------|
| 理解绝对式与增量式编码器的区别及选型 | 基础 |
| 掌握光电式与磁电式编码器的技术对比 | 基础 |
| 配置STM32 TIM2/TIM5（32位）编码器模式 | 中级 |
| 实现M法、T法、M/T法三种测速算法 | 中级 |
| 实现Z相归零（Homing）序列 | 中级 |
| 设计位置→速度→电流三环级联控制器 | 高级 |
| 实现带抗积分饱和的PID位置控制 | 高级 |
| 完成直流电机闭环位置控制完整项目 | 高级 |

**前置知识**：
- STM32 GPIO与定时器基础配置
- 中断优先级与NVIC配置（参见 [中断优先级配置](01-interrupt-priority.html)）
- PID控制算法基础
- 直流电机驱动基础（参见 [直流电机控制](../../../01-hardware-layer/05-actuator-control/beginner/01-dc-motor-control.html)）


## 背景知识

### 绝对式编码器 vs 增量式编码器

编码器按输出信号类型分为两大类，选型时需根据应用场景权衡：

```
┌─────────────────────────────────────────────────────────────────┐
│              编码器类型对比                                       │
├──────────────┬──────────────────────┬──────────────────────────┤
│ 特性         │ 增量式编码器          │ 绝对式编码器              │
├──────────────┼──────────────────────┼──────────────────────────┤
│ 输出信号     │ A/B/Z 方波脉冲        │ 并行二进制/SSI/BiSS/EnDat│
│ 断电记忆     │ 无（需重新归零）       │ 有（断电后位置保持）      │
│ 分辨率       │ PPR × 4（四倍频）     │ 位数决定（12~26位）       │
│ 典型分辨率   │ 100~10000 PPR        │ 4096~67M counts/转       │
│ 成本         │ 低（¥10~¥200）       │ 高（¥100~¥5000）         │
│ 接口复杂度   │ 简单（3根信号线）     │ 复杂（多线并行或串行协议）│
│ 抗干扰       │ 差分RS422可增强       │ 通常内置差分驱动          │
│ 适用场景     │ 速度控制、相对位置    │ 机器人关节、数控机床      │
│ 典型产品     │ 欧姆龙E6B2、编码器盘 │ 多摩川TS5700、海德汉ERN  │
└──────────────┴──────────────────────┴──────────────────────────┘
```

**选型建议**：
- 速度控制、相对位移测量 → 增量式（成本低，接口简单）
- 上电即需知道绝对位置、安全关键场合 → 绝对式
- 多圈绝对位置（如机械臂关节）→ 多圈绝对式编码器（带电池或齿轮组）

### 光电式 vs 磁电式编码器

```
┌─────────────────────────────────────────────────────────────────┐
│              传感原理对比                                         │
├──────────────┬──────────────────────┬──────────────────────────┤
│ 特性         │ 光电式编码器          │ 磁电式编码器              │
├──────────────┼──────────────────────┼──────────────────────────┤
│ 工作原理     │ 光栅码盘+光电管       │ 磁性码盘+霍尔/磁阻传感器  │
│ 分辨率       │ 高（可达10000 PPR）   │ 中（通常≤2048 PPR）      │
│ 抗污染       │ 差（油污/灰尘影响大） │ 好（密封性强）            │
│ 抗振动       │ 中（码盘易碎）        │ 好（无脆性部件）          │
│ 温度范围     │ -10~70°C             │ -40~125°C                │
│ 响应频率     │ 高（>500kHz）        │ 中（<200kHz）             │
│ 典型应用     │ 精密数控、实验室      │ 工业电机、汽车、户外设备  │
│ 代表产品     │ 欧姆龙E6B2-CWZ6C     │ AS5048A、MA730、TLE5012B │
└──────────────┴──────────────────────┴──────────────────────────┘
```

**磁电编码器工作原理**（以AS5048A为例）：
- 磁铁固定在电机轴端，随轴旋转
- 芯片内部霍尔阵列检测磁场方向
- CORDIC算法计算角度，输出14位绝对角度（0~16383对应0~360°）
- SPI接口读取，支持菊花链连接多个编码器

### 增量式编码器信号详解

```
正转（A相超前B相90°）：
         ┌──┐  ┌──┐  ┌──┐  ┌──┐
A相：────┘  └──┘  └──┘  └──┘  └──
      ┌──┐  ┌──┐  ┌──┐  ┌──┐
B相：─┘  └──┘  └──┘  └──┘  └────

反转（B相超前A相90°）：
      ┌──┐  ┌──┐  ┌──┐  ┌──┐
A相：─┘  └──┘  └──┘  └──┘  └────
         ┌──┐  ┌──┐  ┌──┐  ┌──┐
B相：────┘  └──┘  └──┘  └──┘  └──

Z相（每转一个脉冲，宽度通常=1个A相周期）：
                    ┌─┐
Z相：───────────────┘ └──────────
```

**四倍频计数原理**：
- 模式1（TI1）：仅A相边沿计数，分辨率 = PPR
- 模式2（TI2）：仅B相边沿计数，分辨率 = PPR
- 模式3（TI12）：A、B两相上升沿+下降沿均计数，分辨率 = PPR × 4

```
四倍频计数示意（1000 PPR编码器）：
A相：  ↑    ↓    ↑    ↓    ↑
B相：    ↑    ↓    ↑    ↓    ↑
计数：  1    2    3    4    5  ...
每转：1000 × 4 = 4000 counts
角度分辨率：360° / 4000 = 0.09°
```

### 编码器信号调理：施密特触发器与RS422差分

原始编码器信号在长距离传输或噪声环境中容易失真，需要信号调理：

**施密特触发器（Schmitt Trigger）整形**：

```
噪声信号（未整形）：
     ___/\/\/\___/\/\/\___
    /                     \
───/                       \───

经施密特触发器整形后：
    ┌────────────┐
────┘            └──────────────

施密特触发器迟滞特性：
  VT+ = 上升阈值（如3.0V）
  VT- = 下降阈值（如1.5V）
  迟滞 = VT+ - VT- = 1.5V（防止噪声引起误触发）
```

常用芯片：74HC14（六路反相施密特触发器）、SN74LVC1G17（单路同相）

**RS422差分传输**（长距离/强干扰场合）：

```
编码器端（差分驱动）：
  A+  ──────────────────────────→ 接收端 A+
  A-  ──────────────────────────→ 接收端 A-
  B+  ──────────────────────────→ 接收端 B+
  B-  ──────────────────────────→ 接收端 B-
  Z+  ──────────────────────────→ 接收端 Z+
  Z-  ──────────────────────────→ 接收端 Z-

差分信号抗共模干扰：
  干扰噪声同时叠加在A+和A-上
  接收端取差值：(A+ + noise) - (A- + noise) = A+ - A-
  共模噪声被完全消除
```

RS422接收芯片：AM26LS32（四路差分接收器），接STM32前需加100Ω终端电阻：

```c
// RS422接收电路（硬件层面，无需软件配置）
// AM26LS32输出为TTL电平，直接连接STM32 GPIO
// 注意：STM32 GPIO为3.3V，AM26LS32输出为5V，需加分压电阻或使用5V容忍引脚

// 推荐接法：
// AM26LS32 OUT → 1kΩ → STM32 TIMx_CH1
//                    ↓
//                  2kΩ → GND
// 分压后：5V × 2/(1+2) = 3.33V ≈ 3.3V（安全）
```


## 核心内容

### STM32定时器编码器模式

STM32的TIM1/TIM2/TIM3/TIM4/TIM5/TIM8均支持编码器模式，硬件自动处理方向判断和计数。

#### 16位 vs 32位定时器选择

```
┌─────────────────────────────────────────────────────────────────┐
│              STM32定时器编码器模式对比                            │
├──────────────┬──────────────────────┬──────────────────────────┤
│ 定时器       │ 计数位宽              │ 适用场景                  │
├──────────────┼──────────────────────┼──────────────────────────┤
│ TIM3/TIM4   │ 16位（0~65535）       │ 低速、短时间测量           │
│ TIM1/TIM8   │ 16位（高级定时器）    │ 低速、需要互补PWM同步      │
│ TIM2/TIM5   │ 32位（0~4294967295） │ 高速、长时间、高精度       │
└──────────────┴──────────────────────┴──────────────────────────┘

16位溢出分析（1000 PPR编码器，四倍频=4000 CPR）：
  最大计数：65535 counts
  对应圈数：65535 / 4000 = 16.38 圈
  3000 RPM时溢出时间：16.38 / (3000/60) = 0.33秒 → 频繁溢出！

32位溢出分析：
  最大计数：4294967295 counts
  对应圈数：4294967295 / 4000 = 1,073,741 圈
  3000 RPM时溢出时间：1,073,741 / (3000/60) = 21,474 秒 ≈ 5.96小时
  → 实际应用中几乎不会溢出
```

**结论**：高速电机控制（>500 RPM）或需要长时间累积位置时，务必使用TIM2或TIM5（32位）。

#### TIM2/TIM5 32位编码器配置

```c
// 文件：encoder.h
// 芯片：STM32F4xx，HAL库版本：STM32F4 HAL v1.8.x
// CubeMX配置：TIM2 → Encoder Mode → Encoder Mode TI1 and TI2

#ifndef ENCODER_H
#define ENCODER_H

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

// 编码器参数（根据实际编码器修改）
#define ENCODER_PPR         1000        // 编码器线数（每转脉冲数，单相）
#define ENCODER_CPR         (ENCODER_PPR * 4)  // 四倍频后每转计数 = 4000
#define ENCODER_GEAR_RATIO  1.0f        // 减速比（直连=1.0）

// 速度计算参数
#define SPEED_SAMPLE_MS     10          // 速度采样周期（毫秒）
#define SPEED_FILTER_ALPHA  0.3f        // 低通滤波系数（0~1，越小越平滑）

// 位置控制参数
#define POSITION_COUNTS_PER_DEG  (ENCODER_CPR / 360.0f)  // 每度对应计数

typedef struct {
    TIM_HandleTypeDef *htim;        // 定时器句柄
    int64_t  total_count;           // 累积总计数（64位，永不溢出）
    int32_t  last_count;            // 上次读取的32位计数值
    float    speed_rpm;             // 当前转速（RPM）
    float    position_deg;          // 当前位置（度）
    bool     direction;             // true=正转，false=反转
    bool     index_found;           // Z相是否已找到
    int64_t  index_count;           // Z相对应的累积计数
} Encoder_t;

// 函数声明
void     encoder_init(Encoder_t *enc, TIM_HandleTypeDef *htim);
void     encoder_update(Encoder_t *enc);        // 在定时器中断中调用
float    encoder_get_speed(Encoder_t *enc);
float    encoder_get_position(Encoder_t *enc);
int64_t  encoder_get_count(Encoder_t *enc);
void     encoder_reset_position(Encoder_t *enc);
bool     encoder_check_error(Encoder_t *enc, float max_rpm);

#endif // ENCODER_H
```

```c
// 文件：encoder.c
#include "encoder.h"
#include <math.h>

// TIM2硬件初始化（32位编码器模式）
// 引脚：PA0(TIM2_CH1/A相), PA1(TIM2_CH2/B相)
static void encoder_hw_init(TIM_HandleTypeDef *htim) {
    TIM_Encoder_InitTypeDef enc_cfg = {0};

    // 定时器基础配置
    htim->Instance               = TIM2;
    htim->Init.Prescaler         = 0;           // 不分频，直接计数
    htim->Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim->Init.Period            = 0xFFFFFFFF;  // 32位最大值
    htim->Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim->Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

    // 编码器模式：同时检测A、B两相的上升沿和下降沿（四倍频）
    enc_cfg.EncoderMode  = TIM_ENCODERMODE_TI12;

    // A相（CH1）配置
    enc_cfg.IC1Polarity  = TIM_ICPOLARITY_RISING;
    enc_cfg.IC1Selection = TIM_ICSELECTION_DIRECTTI;
    enc_cfg.IC1Prescaler = TIM_ICPSC_DIV1;
    enc_cfg.IC1Filter    = 0x0F;  // 数字滤波：8个采样周期确认，抑制毛刺

    // B相（CH2）配置
    enc_cfg.IC2Polarity  = TIM_ICPOLARITY_RISING;
    enc_cfg.IC2Selection = TIM_ICSELECTION_DIRECTTI;
    enc_cfg.IC2Prescaler = TIM_ICPSC_DIV1;
    enc_cfg.IC2Filter    = 0x0F;

    HAL_TIM_Encoder_Init(htim, &enc_cfg);

    // GPIO配置（PA0, PA1 → TIM2_CH1, TIM2_CH2）
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {
        .Pin       = GPIO_PIN_0 | GPIO_PIN_1,
        .Mode      = GPIO_MODE_AF_PP,
        .Pull      = GPIO_PULLUP,   // 上拉防悬空
        .Speed     = GPIO_SPEED_FREQ_HIGH,
        .Alternate = GPIO_AF1_TIM2
    };
    HAL_GPIO_Init(GPIOA, &gpio);

    // 启动编码器计数
    HAL_TIM_Encoder_Start(htim, TIM_CHANNEL_ALL);
}

void encoder_init(Encoder_t *enc, TIM_HandleTypeDef *htim) {
    enc->htim        = htim;
    enc->total_count = 0;
    enc->last_count  = 0;
    enc->speed_rpm   = 0.0f;
    enc->position_deg = 0.0f;
    enc->direction   = true;
    enc->index_found = false;
    enc->index_count = 0;

    encoder_hw_init(htim);

    // 将计数器初始化为中间值，使正负方向均可计数
    // 对于32位定时器，使用0即可（有符号处理）
    __HAL_TIM_SET_COUNTER(htim, 0);
}

// 更新编码器状态（在10ms定时器中断中调用）
void encoder_update(Encoder_t *enc) {
    // 读取当前32位计数值
    int32_t current = (int32_t)__HAL_TIM_GET_COUNTER(enc->htim);

    // 计算增量（32位有符号差值，自动处理溢出）
    int32_t delta = current - enc->last_count;
    enc->last_count = current;

    // 累积到64位总计数（永不溢出）
    enc->total_count += delta;

    // 更新方向
    enc->direction = (delta >= 0);

    // 计算速度（M法，单位：RPM）
    // RPM = (delta / CPR) × (60 / T_s)
    // T_s = SPEED_SAMPLE_MS / 1000
    float rpm_raw = (float)delta / ENCODER_CPR
                    * (60000.0f / SPEED_SAMPLE_MS);

    // 一阶低通滤波
    enc->speed_rpm = SPEED_FILTER_ALPHA * rpm_raw
                   + (1.0f - SPEED_FILTER_ALPHA) * enc->speed_rpm;

    // 更新位置（度）
    enc->position_deg = (float)enc->total_count / ENCODER_CPR * 360.0f;
}

float   encoder_get_speed(Encoder_t *enc)    { return enc->speed_rpm; }
float   encoder_get_position(Encoder_t *enc) { return enc->position_deg; }
int64_t encoder_get_count(Encoder_t *enc)    { return enc->total_count; }

void encoder_reset_position(Encoder_t *enc) {
    enc->total_count  = 0;
    enc->position_deg = 0.0f;
    __HAL_TIM_SET_COUNTER(enc->htim, 0);
}
```


### Z相归零（Homing）序列

Z相（Index）每转产生一个脉冲，用于建立绝对参考位置。归零序列是精密运动控制的必要步骤：

```c
// 文件：homing.c
// Z相归零状态机

typedef enum {
    HOMING_IDLE,            // 空闲
    HOMING_MOVING,          // 正在移动寻找Z相
    HOMING_FOUND,           // 找到Z相，减速停止
    HOMING_COMPLETE,        // 归零完成
    HOMING_ERROR            // 超时或错误
} HomingState_t;

typedef struct {
    HomingState_t state;
    uint32_t      start_time_ms;    // 归零开始时间
    uint32_t      timeout_ms;       // 超时时间（默认5000ms）
    float         search_speed_rpm; // 搜索速度（慢速，如50 RPM）
    int64_t       home_count;       // 归零后的参考计数
    bool          z_triggered;      // Z相中断标志（在ISR中置位）
} Homing_t;

static Homing_t homing = {
    .state           = HOMING_IDLE,
    .timeout_ms      = 5000,
    .search_speed_rpm = 50.0f,
    .z_triggered     = false
};

// Z相外部中断回调（配置PA2为EXTI，上升沿触发）
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_2) {  // Z相引脚
        homing.z_triggered = true;
    }
}

// 归零状态机（在主循环或低优先级任务中调用）
HomingState_t homing_run(Encoder_t *enc, void (*set_speed)(float)) {
    switch (homing.state) {
        case HOMING_IDLE:
            // 开始归零：以慢速正转
            homing.start_time_ms = HAL_GetTick();
            homing.z_triggered   = false;
            set_speed(homing.search_speed_rpm);
            homing.state = HOMING_MOVING;
            break;

        case HOMING_MOVING:
            // 检查超时
            if (HAL_GetTick() - homing.start_time_ms > homing.timeout_ms) {
                set_speed(0.0f);
                homing.state = HOMING_ERROR;
                break;
            }
            // 检查Z相触发
            if (homing.z_triggered) {
                set_speed(0.0f);                    // 立即停止
                homing.home_count = enc->total_count; // 记录归零位置
                encoder_reset_position(enc);          // 清零位置
                homing.state = HOMING_FOUND;
            }
            break;

        case HOMING_FOUND:
            // 等待电机完全停止（速度<1 RPM）
            if (fabsf(encoder_get_speed(enc)) < 1.0f) {
                homing.state = HOMING_COMPLETE;
            }
            break;

        case HOMING_COMPLETE:
        case HOMING_ERROR:
            // 终态，等待外部重置
            break;
    }
    return homing.state;
}

// 归零完成后，位置0对应Z相位置
// 可以进一步移动到机械零点（如偏移固定角度）
void homing_go_to_mechanical_zero(float offset_deg) {
    // 移动到 offset_deg 位置（由位置控制器执行）
    // position_controller_set_target(offset_deg);
}
```

**Z相归零时序图**：

```
电机转速：
  ──────────────────────────────────────────────────────
  50 RPM ████████████████████████████████████▌
                                              ↓ Z相触发
  0 RPM  ─────────────────────────────────────────────

Z相信号：
  ─────────────────────────────────────────┐ ┌─────────
                                           └─┘
  ↑ 开始归零                               ↑ 触发，停止

位置计数：
  0 → 4000 → 8000 → ... → N × 4000 → 重置为0
```

### 编码器错误检测

在高可靠性应用中，需要检测编码器故障：

```c
// 编码器错误检测
typedef enum {
    ENC_OK           = 0,
    ENC_ERR_SIGNAL   = 1,   // 信号丢失（长时间无脉冲但命令有速度）
    ENC_ERR_OVERSPEED = 2,  // 超速（超过最大允许转速）
    ENC_ERR_DIRECTION = 3,  // 方向异常（命令正转但反转）
} EncoderError_t;

// 错误检测（在速度控制循环中调用）
// max_rpm：最大允许转速
// cmd_speed：命令速度（正=正转，负=反转）
EncoderError_t encoder_check_error(Encoder_t *enc, float max_rpm) {
    float speed = enc->speed_rpm;

    // 检查超速
    if (fabsf(speed) > max_rpm) {
        return ENC_ERR_OVERSPEED;
    }

    return ENC_OK;
}

// 信号丢失检测（需要额外的硬件或软件机制）
// 方法1：硬件 - 用定时器捕获检测脉冲间隔，超时则报警
// 方法2：软件 - 命令速度非零但编码器速度持续为0超过阈值时间
typedef struct {
    uint32_t no_pulse_start_ms;     // 无脉冲开始时间
    uint32_t no_pulse_timeout_ms;   // 无脉冲超时阈值（如200ms）
    int64_t  last_total_count;      // 上次检查的总计数
} SignalLossDetector_t;

bool encoder_signal_lost(Encoder_t *enc, SignalLossDetector_t *det,
                         float cmd_speed) {
    // 如果命令速度接近0，不检测
    if (fabsf(cmd_speed) < 5.0f) {
        det->no_pulse_start_ms = 0;
        det->last_total_count  = enc->total_count;
        return false;
    }

    // 检查计数是否变化
    if (enc->total_count != det->last_total_count) {
        det->no_pulse_start_ms = 0;  // 有脉冲，重置计时
        det->last_total_count  = enc->total_count;
        return false;
    }

    // 计数未变化，开始计时
    if (det->no_pulse_start_ms == 0) {
        det->no_pulse_start_ms = HAL_GetTick();
    }

    // 超时判断
    return (HAL_GetTick() - det->no_pulse_start_ms > det->no_pulse_timeout_ms);
}
```

### 测速算法详解

#### M法（频率法）

固定时间T内统计脉冲数，适合**高速**场景（>100 RPM）：

```c
// M法测速：每T秒读取一次脉冲数
// 速度(RPM) = (脉冲数 / CPR) × (60 / T)
#define SAMPLE_TIME_MS  10      // 采样周期10ms

float speed_m_method(Encoder_t *enc) {
    static int64_t last_count = 0;
    int64_t current = enc->total_count;
    int64_t delta   = current - last_count;
    last_count = current;

    // RPM = (delta / CPR) × (60000 / SAMPLE_TIME_MS)
    return (float)delta / ENCODER_CPR * (60000.0f / SAMPLE_TIME_MS);
}

// M法误差分析：
// 最小可分辨速度 = 1 count / (CPR × T_s) × 60
// 以CPR=4000, T_s=10ms为例：
// 最小速度 = 1/4000/0.01×60 = 1.5 RPM
// 低于1.5 RPM时，速度分辨率为1.5 RPM（误差大）
```

#### T法（周期法）

测量相邻脉冲的时间间隔，适合**低速**场景（<50 RPM）：

```c
// T法测速：测量两个脉冲之间的时间
// 使用TIM5（32位，1MHz时钟）捕获A相脉冲时间戳

static volatile uint32_t t_method_period_us = 0;  // 脉冲周期（微秒）
static volatile uint32_t t_method_last_us   = 0;  // 上次脉冲时间戳

// 在A相外部中断中调用（或使用定时器输入捕获）
void encoder_a_phase_isr(void) {
    uint32_t now = TIM5->CNT;  // TIM5配置为1MHz自由运行计数器
    if (t_method_last_us != 0) {
        t_method_period_us = now - t_method_last_us;
    }
    t_method_last_us = now;
}

float speed_t_method(void) {
    uint32_t period = t_method_period_us;
    if (period == 0) return 0.0f;

    // 超时检测：如果超过500ms无脉冲，认为速度为0
    uint32_t elapsed = TIM5->CNT - t_method_last_us;
    if (elapsed > 500000) return 0.0f;  // 500ms超时

    // RPM = 60 × 10^6 / (CPR × 脉冲周期us)
    // 注意：T法计数的是单相脉冲，CPR需除以4
    return 60.0f * 1000000.0f / (ENCODER_PPR * period);
}
```

#### M/T法（推荐，全速度范围高精度）

```c
// M/T法：同时计数脉冲数和精确时间
// 在固定采样窗口内，同时记录脉冲数和高精度时间
typedef struct {
    int64_t  pulse_count;   // 采样窗口内的脉冲数
    uint32_t time_us;       // 实际计时时间（微秒，用TIM5测量）
    float    rpm;           // 计算结果
} MTSpeed_t;

void speed_mt_method(Encoder_t *enc, MTSpeed_t *s) {
    static uint32_t start_time_us = 0;
    static int64_t  start_count   = 0;

    uint32_t now   = TIM5->CNT;  // 1MHz高精度时间戳
    int64_t  count = enc->total_count;

    s->pulse_count = count - start_count;
    s->time_us     = now - start_time_us;

    if (s->time_us > 0 && s->pulse_count != 0) {
        // RPM = (脉冲数 / CPR) × (60 × 10^6 / 时间us)
        s->rpm = (float)s->pulse_count / ENCODER_CPR
                 * 60.0f * 1000000.0f / (float)s->time_us;
    } else {
        s->rpm = 0.0f;
    }

    start_time_us = now;
    start_count   = count;
}

// M/T法误差分析：
// 误差来源：时间测量误差（1μs）+ 计数误差（±1 count）
// 在低速时：时间长，计数误差相对小 → 精度高
// 在高速时：计数多，时间误差相对小 → 精度高
// 全速度范围误差均匀，优于单独使用M法或T法
```


## 深入原理

### 速度滤波算法

原始速度数据通常含有噪声，需要滤波处理：

```c
// 一阶低通滤波（指数移动平均，IIR滤波器）
// 传递函数：H(z) = α / (1 - (1-α)z^{-1})
// alpha越小，截止频率越低，滤波越强，但响应越慢
// 推荐：alpha = 0.1~0.5，根据噪声水平调整
float speed_lpf(float new_speed, float *state, float alpha) {
    *state = alpha * new_speed + (1.0f - alpha) * (*state);
    return *state;
}

// 滑动平均滤波（FIR滤波器，线性相位，延迟均匀）
#define MA_SIZE  8
float speed_moving_average(float new_speed) {
    static float buf[MA_SIZE] = {0};
    static int   idx = 0;
    static float sum = 0.0f;

    sum -= buf[idx];
    buf[idx] = new_speed;
    sum += new_speed;
    idx = (idx + 1) % MA_SIZE;
    return sum / MA_SIZE;
}

// 卡尔曼滤波（最优估计，适合噪声特性已知的场合）
typedef struct {
    float x;   // 状态估计（速度）
    float p;   // 估计误差协方差
    float q;   // 过程噪声协方差（系统噪声）
    float r;   // 测量噪声协方差（传感器噪声）
} KalmanFilter_t;

float speed_kalman(KalmanFilter_t *kf, float measurement) {
    // 预测步骤
    // x_pred = x（匀速模型，无加速度输入）
    float p_pred = kf->p + kf->q;

    // 更新步骤
    float k = p_pred / (p_pred + kf->r);  // 卡尔曼增益
    kf->x = kf->x + k * (measurement - kf->x);
    kf->p = (1.0f - k) * p_pred;

    return kf->x;
}

// 卡尔曼滤波初始化示例
// KalmanFilter_t kf = {.x=0, .p=1.0f, .q=0.01f, .r=0.1f};
// q越大：相信测量值，响应快但噪声大
// r越大：相信预测值，响应慢但平滑
```

### 位置→速度→电流三环级联控制

工业伺服驱动器的标准控制架构，三个控制环从外到内嵌套：

```
┌─────────────────────────────────────────────────────────────────┐
│                    三环级联控制架构                               │
│                                                                  │
│  位置指令    ┌──────────┐  速度指令   ┌──────────┐  电流指令    │
│  θ_ref ────→│ 位置环   │──→ ω_ref ──→│ 速度环   │──→ I_ref ──→│
│             │ PID控制  │             │ PID控制  │             │
│             └──────────┘             └──────────┘             │
│                  ↑                        ↑                    │
│             θ_feedback              ω_feedback                 │
│             (编码器位置)             (编码器速度)               │
│                                                                  │
│                                          ┌──────────┐  PWM     │
│                                 I_ref ──→│ 电流环   │──→ 电机  │
│                                          │ PI控制   │          │
│                                          └──────────┘          │
│                                               ↑                │
│                                          I_feedback            │
│                                          (电流传感器)           │
│                                                                  │
│  带宽关系：ω_current >> ω_velocity >> ω_position               │
│  典型值：  电流环1kHz,  速度环100Hz,  位置环10Hz               │
└─────────────────────────────────────────────────────────────────┘
```

**各环职责**：
- **电流环（最内环）**：控制电机电流（即转矩），响应最快（1kHz），使用PI控制
- **速度环（中间环）**：控制电机转速，响应中等（100Hz），使用PI控制
- **位置环（最外环）**：控制电机位置，响应最慢（10Hz），通常使用P控制（加速度前馈）

### 带抗积分饱和的PID位置控制

积分饱和（Integral Windup）是位置控制中的常见问题：当误差长时间存在（如机械限位），积分项持续累积，导致超调严重。

```c
// 文件：pid_controller.h
// 带抗积分饱和、微分滤波的完整PID实现

typedef struct {
    // PID参数
    float kp;           // 比例增益
    float ki;           // 积分增益
    float kd;           // 微分增益
    float n;            // 微分滤波系数（通常5~20）

    // 输出限幅
    float out_min;      // 输出下限
    float out_max;      // 输出上限

    // 积分限幅（抗饱和）
    float int_min;      // 积分项下限
    float int_max;      // 积分项上限

    // 内部状态
    float integral;     // 积分累积值
    float prev_error;   // 上次误差（用于微分）
    float prev_deriv;   // 上次微分值（用于滤波）

    // 采样时间
    float dt;           // 采样周期（秒）
} PID_t;

void pid_init(PID_t *pid, float kp, float ki, float kd,
              float out_min, float out_max, float dt) {
    pid->kp       = kp;
    pid->ki       = ki;
    pid->kd       = kd;
    pid->n        = 10.0f;      // 微分滤波系数
    pid->out_min  = out_min;
    pid->out_max  = out_max;
    pid->int_min  = out_min;    // 积分限幅与输出限幅相同
    pid->int_max  = out_max;
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_deriv = 0.0f;
    pid->dt       = dt;
}

float pid_compute(PID_t *pid, float setpoint, float measurement) {
    float error = setpoint - measurement;

    // 比例项
    float p_term = pid->kp * error;

    // 积分项（带限幅抗饱和）
    pid->integral += pid->ki * error * pid->dt;
    // 积分限幅：防止积分项无限增长
    if (pid->integral > pid->int_max) pid->integral = pid->int_max;
    if (pid->integral < pid->int_min) pid->integral = pid->int_min;
    float i_term = pid->integral;

    // 微分项（带低通滤波，抑制微分噪声）
    // 滤波微分：D(s) = kd × N × s / (s + N)
    // 离散化：d[k] = (1 - N×dt) × d[k-1] + kd × N × (e[k] - e[k-1])
    float deriv_raw = (error - pid->prev_error) / pid->dt;
    float alpha_d   = pid->n * pid->dt;
    pid->prev_deriv = (1.0f - alpha_d) * pid->prev_deriv + pid->kd * alpha_d * deriv_raw;
    float d_term    = pid->prev_deriv;

    pid->prev_error = error;

    // 输出求和与限幅
    float output = p_term + i_term + d_term;
    if (output > pid->out_max) output = pid->out_max;
    if (output < pid->out_min) output = pid->out_min;

    // 条件积分（Back-Calculation抗饱和）
    // 当输出饱和时，停止积分累积
    float output_unclamped = p_term + i_term + d_term;
    if ((output_unclamped > pid->out_max && error > 0) ||
        (output_unclamped < pid->out_min && error < 0)) {
        // 输出饱和且误差方向相同，停止积分
        pid->integral -= pid->ki * error * pid->dt;
    }

    return output;
}

void pid_reset(PID_t *pid) {
    pid->integral   = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_deriv = 0.0f;
}
```

**抗积分饱和效果对比**：

```
无抗饱和（普通PID）：
  位置误差：
  ████████████████████████████████████████████████████
  ↓ 到达目标                                          ↓ 超调严重
  ─────────────────────────────────────────────────────
  积分项：持续累积到很大值，到达目标后仍有大量积分残留

带抗饱和PID：
  位置误差：
  ████████████████████████████████████████
  ↓ 到达目标                              ↓ 轻微超调
  ─────────────────────────────────────────────────────
  积分项：饱和时停止累积，到达目标时积分值合理
```

### 速度前馈控制

纯反馈控制存在跟踪延迟，加入速度前馈可显著改善动态响应：

```c
// 带速度前馈的位置控制器
// 速度前馈：根据位置指令的变化率预测所需速度
typedef struct {
    PID_t    pos_pid;       // 位置PID
    PID_t    vel_pid;       // 速度PID
    float    ff_gain;       // 前馈增益（通常0.5~1.0）
    float    prev_setpoint; // 上次位置指令
    float    dt;            // 采样周期
} CascadeController_t;

float cascade_compute(CascadeController_t *ctrl,
                      float pos_setpoint,
                      float pos_feedback,
                      float vel_feedback) {
    // 位置环：计算速度指令
    float vel_cmd = pid_compute(&ctrl->pos_pid, pos_setpoint, pos_feedback);

    // 速度前馈：根据位置指令变化率计算前馈速度
    float pos_rate = (pos_setpoint - ctrl->prev_setpoint) / ctrl->dt;
    ctrl->prev_setpoint = pos_setpoint;
    vel_cmd += ctrl->ff_gain * pos_rate;

    // 速度环：计算电流/PWM指令
    float pwm_cmd = pid_compute(&ctrl->vel_pid, vel_cmd, vel_feedback);

    return pwm_cmd;
}
```


## 完整项目实战：直流电机闭环位置控制

### 项目概述

本项目实现一个完整的直流电机闭环位置控制系统，具备以下功能：
- 编码器位置/速度实时测量（TIM2，32位）
- 双环PID控制（位置环 + 速度环）
- Z相归零序列
- 串口命令接口（设置目标位置、查询状态）
- 过流/超速保护

**物料清单（BOM）**：

| 序号 | 元件 | 型号 | 数量 | 参考价格 |
|------|------|------|------|---------|
| 1 | 主控MCU | STM32F411CEU6（黑药丸） | 1 | ¥15 |
| 2 | 直流电机 | 25GA370减速电机，12V，带1000线编码器 | 1 | ¥45 |
| 3 | 电机驱动 | TB6612FNG双路H桥模块 | 1 | ¥8 |
| 4 | 电源 | 12V/2A开关电源 | 1 | ¥20 |
| 5 | 电源模块 | AMS1117-3.3V稳压模块 | 1 | ¥2 |
| 6 | 差分接收 | AM26LS32（可选，长距离用） | 1 | ¥5 |
| 7 | 电流传感器 | ACS712-5A（可选，电流环用） | 1 | ¥8 |
| 8 | 调试接口 | USB-TTL模块（CH340） | 1 | ¥5 |

**硬件连接图**：

```
STM32F411 引脚分配：
┌─────────────────────────────────────────────────────────────────┐
│  STM32F411CEU6                                                   │
│                                                                  │
│  PA0 (TIM2_CH1) ──────────────────→ 编码器 A相                  │
│  PA1 (TIM2_CH2) ──────────────────→ 编码器 B相                  │
│  PA2 (EXTI2)    ──────────────────→ 编码器 Z相                  │
│                                                                  │
│  PB6 (TIM4_CH1/PWM) ──────────────→ TB6612 PWMA                │
│  PB7 (GPIO_OUT)     ──────────────→ TB6612 AIN1                 │
│  PB8 (GPIO_OUT)     ──────────────→ TB6612 AIN2                 │
│  PB9 (GPIO_OUT)     ──────────────→ TB6612 STBY (高电平使能)    │
│                                                                  │
│  PA9  (USART1_TX) ────────────────→ USB-TTL RX                  │
│  PA10 (USART1_RX) ────────────────→ USB-TTL TX                  │
│                                                                  │
│  3.3V ────────────────────────────→ 编码器 VCC（若5V需分压）    │
│  GND  ────────────────────────────→ 编码器 GND, TB6612 GND      │
└─────────────────────────────────────────────────────────────────┘

TB6612FNG 接线：
  VM  → 12V电机电源
  VCC → 3.3V逻辑电源
  GND → 公共地
  AO1, AO2 → 电机两端
```

### 完整代码实现

```c
// 文件：main.c
// 直流电机闭环位置控制主程序
// 芯片：STM32F411CEU6，HAL库，系统时钟96MHz

#include "stm32f4xx_hal.h"
#include "encoder.h"
#include "pid_controller.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

// ─── 全局变量 ───────────────────────────────────────────────────
TIM_HandleTypeDef htim2;    // 编码器定时器（32位）
TIM_HandleTypeDef htim4;    // PWM定时器
UART_HandleTypeDef huart1;  // 调试串口

Encoder_t encoder;          // 编码器对象
PID_t     pos_pid;          // 位置PID
PID_t     vel_pid;          // 速度PID

float target_position_deg = 0.0f;   // 目标位置（度）
float target_speed_rpm    = 0.0f;   // 速度环目标（由位置环输出）

// 控制模式
typedef enum { MODE_IDLE, MODE_HOMING, MODE_POSITION } ControlMode_t;
ControlMode_t ctrl_mode = MODE_IDLE;

// ─── 电机PWM输出 ─────────────────────────────────────────────────
// duty: -100.0 ~ +100.0（负值反转）
void motor_set_pwm(float duty) {
    // 限幅
    if (duty >  100.0f) duty =  100.0f;
    if (duty < -100.0f) duty = -100.0f;

    uint32_t pwm_val = (uint32_t)(fabsf(duty) / 100.0f * 999);  // 0~999

    if (duty >= 0) {
        // 正转：AIN1=1, AIN2=0
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    } else {
        // 反转：AIN1=0, AIN2=1
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    }
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, pwm_val);
}

void motor_stop(void) {
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, 0);
}

// ─── 10ms控制中断（TIM3）────────────────────────────────────────
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance != TIM3) return;

    // 1. 更新编码器状态
    encoder_update(&encoder);

    float pos = encoder_get_position(&encoder);
    float vel = encoder_get_speed(&encoder);

    // 2. 根据控制模式执行控制
    switch (ctrl_mode) {
        case MODE_POSITION: {
            // 位置环：计算速度指令
            float vel_cmd = pid_compute(&pos_pid, target_position_deg, pos);

            // 速度环：计算PWM指令
            float pwm_cmd = pid_compute(&vel_pid, vel_cmd, vel);

            motor_set_pwm(pwm_cmd);

            // 到位检测（误差<0.5度且速度<5RPM）
            if (fabsf(target_position_deg - pos) < 0.5f &&
                fabsf(vel) < 5.0f) {
                // 到位，保持位置（PID继续运行，自动补偿扰动）
            }
            break;
        }
        case MODE_IDLE:
            motor_stop();
            break;
        default:
            break;
    }

    // 3. 超速保护
    if (fabsf(vel) > 3500.0f) {  // 超过3500 RPM
        motor_stop();
        ctrl_mode = MODE_IDLE;
        printf("ERROR: Overspeed! %.1f RPM\r\n", vel);
    }
}
```

```c
// 文件：main.c（续）—— 初始化与主循环

// ─── 系统初始化 ──────────────────────────────────────────────────
void system_init(void) {
    HAL_Init();
    SystemClock_Config();  // 96MHz

    // 初始化编码器（TIM2，32位）
    encoder_init(&encoder, &htim2);

    // 初始化位置PID
    // kp=0.8, ki=0.05, kd=0.02, 输出限幅±300 RPM, 采样10ms
    pid_init(&pos_pid, 0.8f, 0.05f, 0.02f, -300.0f, 300.0f, 0.01f);

    // 初始化速度PID
    // kp=0.3, ki=0.1, kd=0.0, 输出限幅±100% PWM, 采样10ms
    pid_init(&vel_pid, 0.3f, 0.1f, 0.0f, -100.0f, 100.0f, 0.01f);

    // 初始化PWM（TIM4，10kHz）
    pwm_init();

    // 初始化串口（115200 baud）
    uart_init();

    // 初始化10ms控制定时器（TIM3）
    control_timer_init();

    printf("System initialized. Type 'help' for commands.\r\n");
}

// ─── 串口命令处理 ────────────────────────────────────────────────
// 支持命令：
//   pos <degrees>  — 移动到指定位置（度）
//   home           — 执行归零序列
//   stop           — 停止电机
//   status         — 查询当前状态
//   pid p <kp> <ki> <kd>  — 设置位置PID参数
void process_command(const char *cmd) {
    float val;
    if (sscanf(cmd, "pos %f", &val) == 1) {
        target_position_deg = val;
        ctrl_mode = MODE_POSITION;
        printf("Moving to %.1f degrees\r\n", val);
    } else if (strcmp(cmd, "home") == 0) {
        ctrl_mode = MODE_HOMING;
        printf("Starting homing sequence...\r\n");
    } else if (strcmp(cmd, "stop") == 0) {
        ctrl_mode = MODE_IDLE;
        motor_stop();
        pid_reset(&pos_pid);
        pid_reset(&vel_pid);
        printf("Motor stopped\r\n");
    } else if (strcmp(cmd, "status") == 0) {
        printf("Position: %.2f deg | Speed: %.1f RPM | Target: %.1f deg\r\n",
               encoder_get_position(&encoder),
               encoder_get_speed(&encoder),
               target_position_deg);
    } else {
        printf("Commands: pos <deg>, home, stop, status\r\n");
    }
}

int main(void) {
    system_init();

    char cmd_buf[64];
    uint32_t last_print_ms = 0;

    while (1) {
        // 处理串口命令（非阻塞）
        if (uart_readline(cmd_buf, sizeof(cmd_buf))) {
            process_command(cmd_buf);
        }

        // 每500ms打印一次状态
        if (HAL_GetTick() - last_print_ms >= 500) {
            last_print_ms = HAL_GetTick();
            printf("Pos:%.1fdeg Vel:%.1fRPM Target:%.1fdeg\r\n",
                   encoder_get_position(&encoder),
                   encoder_get_speed(&encoder),
                   target_position_deg);
        }
    }
}
```

### 调试与参数整定

**PID参数整定步骤**（Ziegler-Nichols临界增益法）：

```
步骤1：速度环整定（先整定内环）
  1. 将ki=0, kd=0，逐渐增大kp
  2. 直到速度响应出现持续振荡，记录此时kp为Ku（临界增益）
  3. 记录振荡周期Tu
  4. 设置：kp = 0.45×Ku, ki = 0.54×Ku/Tu, kd = 0

步骤2：位置环整定（速度环稳定后）
  1. 将速度环参数固定
  2. 位置环通常只需P控制：kp = 0.1~0.5
  3. 过大的kp导致超调，过小导致响应慢
  4. 加入少量ki消除稳态误差

典型参数（25GA370电机，1000线编码器）：
  速度环：kp=0.3, ki=0.1, kd=0.0
  位置环：kp=0.8, ki=0.05, kd=0.02
```

**串口调试输出示例**：

```
System initialized. Type 'help' for commands.
> pos 360
Moving to 360.0 degrees
Pos:0.0deg Vel:0.0RPM Target:360.0deg
Pos:45.2deg Vel:285.3RPM Target:360.0deg
Pos:180.5deg Vel:312.1RPM Target:360.0deg
Pos:320.8deg Vel:198.4RPM Target:360.0deg
Pos:358.2deg Vel:45.6RPM Target:360.0deg
Pos:360.1deg Vel:2.3RPM Target:360.0deg   ← 到位
> status
Position: 360.05 deg | Speed: 0.8 RPM | Target: 360.0 deg
```


## 性能调优

### 编码器分辨率与控制精度的关系

```
位置分辨率 = 360° / (PPR × 4 × 减速比)

示例：
  1000线编码器，直连（减速比=1）：
    分辨率 = 360 / (1000 × 4) = 0.09°/count

  1000线编码器，100:1减速箱：
    分辨率 = 360 / (1000 × 4 × 100) = 0.0009°/count = 3.24角秒

速度分辨率（M法，10ms采样）：
  最小可分辨速度 = 1 count / (CPR × T_s) × 60
  = 1 / (4000 × 0.01) × 60 = 1.5 RPM

提高速度分辨率的方法：
  1. 增大采样周期（但会增加控制延迟）
  2. 使用M/T法（低速时精度更高）
  3. 使用更高线数编码器（2500线、5000线）
  4. 增大减速比（同时提高位置和速度分辨率）
```

### 中断优先级配置

编码器相关中断的优先级设置对系统稳定性至关重要：

```c
// 推荐优先级配置（数字越小优先级越高）
// 电流环中断（最高优先级，1kHz）
HAL_NVIC_SetPriority(TIM1_UP_TIM10_IRQn, 0, 0);

// 速度/位置控制中断（次高优先级，100Hz/10Hz）
HAL_NVIC_SetPriority(TIM3_IRQn, 1, 0);

// Z相外部中断（高优先级，确保归零精度）
HAL_NVIC_SetPriority(EXTI2_IRQn, 1, 1);

// 串口中断（低优先级）
HAL_NVIC_SetPriority(USART1_IRQn, 3, 0);

// 注意：编码器计数由硬件完成，无需中断，不占用CPU
```

## 常见问题与调试

### 问题1：计数方向反了

**现象**：电机正转时位置减小，反转时位置增大。

**原因**：A、B相接线顺序与定时器期望的相位关系相反。

**解决方案**：

```c
// 方法1（推荐）：交换A、B相物理接线
// 将编码器A相接到TIM2_CH2，B相接到TIM2_CH1

// 方法2：软件取反（不改变硬件）
int32_t encoder_get_count_corrected(Encoder_t *enc) {
    return -(enc->total_count);  // 取反
}

// 方法3：修改定时器极性配置
// 将IC1Polarity改为TIM_ICPOLARITY_FALLING
enc_cfg.IC1Polarity = TIM_ICPOLARITY_FALLING;  // 反转A相极性
```

### 问题2：噪声引起的误计数

**现象**：电机静止时计数值仍在跳动（±1~±5 counts）。

**原因**：
- 编码器信号线受到电机PWM干扰（共地噪声、辐射耦合）
- 编码器信号边沿不干净（上升/下降时间过长）
- GPIO上拉电阻过大，信号边沿缓慢

**解决方案**：

```c
// 方案1：增大硬件数字滤波（IC1Filter/IC2Filter）
// 值越大，需要更多连续采样才确认边沿，抑制毛刺
enc_cfg.IC1Filter = 0x0F;  // 最大滤波（8个采样周期）
enc_cfg.IC2Filter = 0x0F;

// 方案2：软件死区滤波（静止时忽略小抖动）
#define NOISE_THRESHOLD  3  // 小于3 counts认为是噪声

int32_t encoder_get_filtered_delta(Encoder_t *enc) {
    static int64_t last_stable_count = 0;
    int64_t delta = enc->total_count - last_stable_count;

    if (llabs(delta) > NOISE_THRESHOLD) {
        last_stable_count = enc->total_count;
        return (int32_t)delta;
    }
    return 0;  // 小抖动忽略
}

// 方案3：硬件措施
// - 编码器信号线使用屏蔽双绞线
// - 信号线远离电机驱动线（至少5cm间距）
// - 在编码器信号线上串联100Ω电阻 + 对地100pF电容（RC滤波）
// - 使用RS422差分传输（彻底消除共模干扰）
```

**噪声诊断方法**：

```c
// 统计静止时的计数抖动量
void encoder_noise_test(Encoder_t *enc, uint32_t duration_ms) {
    int64_t start_count = enc->total_count;
    int64_t max_count   = start_count;
    int64_t min_count   = start_count;
    uint32_t start_time = HAL_GetTick();

    printf("Noise test started (motor must be stationary)...\r\n");

    while (HAL_GetTick() - start_time < duration_ms) {
        int64_t c = enc->total_count;
        if (c > max_count) max_count = c;
        if (c < min_count) min_count = c;
        HAL_Delay(1);
    }

    printf("Noise range: %lld counts (%.3f degrees)\r\n",
           max_count - min_count,
           (float)(max_count - min_count) / ENCODER_CPR * 360.0f);
}
```

### 问题3：16位定时器溢出导致位置跳变

**现象**：高速运行时位置突然跳变±16384度（对应65536 counts）。

**原因**：使用16位定时器（TIM3/TIM4），计数器从65535溢出到0（或从0下溢到65535），差值计算错误。

**解决方案**：

```c
// 方案1（根本解决）：改用32位定时器TIM2或TIM5
// 32位定时器在实际应用中几乎不会溢出（见前文分析）

// 方案2：16位定时器的溢出处理（若必须使用16位）
// 关键：使用有符号16位差值，自动处理溢出
int32_t encoder_read_delta_16bit(TIM_HandleTypeDef *htim) {
    static uint16_t last_count = 0;
    uint16_t current = (uint16_t)__HAL_TIM_GET_COUNTER(htim);

    // 有符号16位差值：自动处理0→65535和65535→0的溢出
    int16_t delta = (int16_t)(current - last_count);
    last_count = current;
    return (int32_t)delta;
}

// 原理：
// 正转：current=100, last=65500 → delta = (int16_t)(100-65500) = (int16_t)(-65400) = 136
// 反转：current=65500, last=100 → delta = (int16_t)(65500-100) = (int16_t)(65400) = -136
// 利用16位整数溢出的环绕特性，自动得到正确的有符号差值
```

### 问题4：低速时速度为0或跳动

**现象**：电机低速运行（<20 RPM）时，M法测速结果为0或在0和某个值之间跳动。

**原因**：M法在低速时，采样周期内脉冲数太少（0或1个），分辨率不足。

**解决方案**：

```c
// 方案1：改用T法或M/T法（见前文）

// 方案2：增大M法采样周期（降低速度更新频率）
// 将采样周期从10ms增大到100ms，低速分辨率提高10倍
// 代价：速度反馈延迟增大

// 方案3：自适应测速（根据速度自动切换算法）
float speed_adaptive(Encoder_t *enc) {
    float m_speed = speed_m_method(enc);

    if (fabsf(m_speed) < 30.0f) {
        // 低速：使用T法（需要额外的脉冲捕获硬件）
        return speed_t_method();
    } else {
        // 高速：使用M法
        return m_speed;
    }
}
```

### 问题5：归零失败（Z相未找到）

**现象**：执行归零序列后，状态机进入`HOMING_ERROR`。

**排查步骤**：

```c
// 步骤1：验证Z相信号是否存在
// 用示波器或逻辑分析仪检查Z相引脚，手动转动电机一圈，应看到一个脉冲

// 步骤2：检查Z相中断配置
void z_phase_debug_init(void) {
    // 配置PA2为外部中断，上升沿触发
    GPIO_InitTypeDef gpio = {
        .Pin  = GPIO_PIN_2,
        .Mode = GPIO_MODE_IT_RISING,
        .Pull = GPIO_PULLUP
    };
    HAL_GPIO_Init(GPIOA, &gpio);
    HAL_NVIC_SetPriority(EXTI2_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(EXTI2_IRQn);
}

// 步骤3：在Z相中断中打印调试信息
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_2) {
        printf("Z phase triggered! Count=%lld\r\n", encoder.total_count);
        homing.z_triggered = true;
    }
}

// 步骤4：增大归零超时时间（默认5秒可能不够）
homing.timeout_ms = 10000;  // 增大到10秒

// 步骤5：降低归零速度（Z相脉冲宽度窄，速度过快可能错过）
homing.search_speed_rpm = 20.0f;  // 降低到20 RPM
```

### 问题6：位置控制超调严重

**现象**：电机到达目标位置后继续运动，超过目标后再反向，来回振荡。

**原因**：PID参数不合适（kp过大、ki过大、kd不足）或速度前馈增益过大。

**调试方法**：

```c
// 通过串口实时调整PID参数（无需重新编译）
void process_pid_command(const char *cmd) {
    float kp, ki, kd;
    if (sscanf(cmd, "pid p %f %f %f", &kp, &ki, &kd) == 3) {
        pos_pid.kp = kp;
        pos_pid.ki = ki;
        pos_pid.kd = kd;
        pid_reset(&pos_pid);
        printf("Position PID: kp=%.3f ki=%.3f kd=%.3f\r\n", kp, ki, kd);
    } else if (sscanf(cmd, "pid v %f %f %f", &kp, &ki, &kd) == 3) {
        vel_pid.kp = kp;
        vel_pid.ki = ki;
        vel_pid.kd = kd;
        pid_reset(&vel_pid);
        printf("Velocity PID: kp=%.3f ki=%.3f kd=%.3f\r\n", kp, ki, kd);
    }
}

// 超调问题的典型解决方案：
// 1. 减小位置环kp（从0.8降到0.4）
// 2. 增大位置环kd（加入微分抑制超调）
// 3. 减小速度环ki（减少积分超调）
// 4. 在接近目标时降低速度限幅（减速区间）
```

## 测试与验证

### 编码器功能验证测试

```c
// 测试1：方向验证
// 手动正转电机，计数应增加；反转，计数应减少
void test_encoder_direction(void) {
    printf("=== Direction Test ===\r\n");
    printf("Manually rotate motor FORWARD, count should INCREASE\r\n");
    HAL_Delay(3000);
    printf("Count: %lld\r\n", encoder.total_count);

    printf("Manually rotate motor BACKWARD, count should DECREASE\r\n");
    HAL_Delay(3000);
    printf("Count: %lld\r\n", encoder.total_count);
}

// 测试2：分辨率验证
// 手动转动一圈，计数应等于CPR（4000）
void test_encoder_resolution(void) {
    encoder_reset_position(&encoder);
    printf("=== Resolution Test ===\r\n");
    printf("Rotate motor exactly ONE full revolution, then press Enter\r\n");
    // 等待用户输入...
    printf("Count: %lld (expected: %d)\r\n",
           encoder.total_count, ENCODER_CPR);
    printf("Error: %.2f%%\r\n",
           fabsf((float)encoder.total_count - ENCODER_CPR) / ENCODER_CPR * 100.0f);
}

// 测试3：速度精度验证
// 以已知转速运行电机，验证测速精度
void test_speed_accuracy(float target_rpm) {
    printf("=== Speed Accuracy Test ===\r\n");
    printf("Running at %.1f RPM for 5 seconds...\r\n", target_rpm);

    // 设置开环PWM（需要预先标定PWM-速度关系）
    // motor_set_pwm(rpm_to_pwm(target_rpm));
    HAL_Delay(2000);  // 等待速度稳定

    float sum = 0;
    int   n   = 0;
    uint32_t start = HAL_GetTick();
    while (HAL_GetTick() - start < 3000) {
        sum += encoder_get_speed(&encoder);
        n++;
        HAL_Delay(10);
    }
    float avg_rpm = sum / n;
    printf("Measured: %.2f RPM, Error: %.2f%%\r\n",
           avg_rpm, fabsf(avg_rpm - target_rpm) / target_rpm * 100.0f);
}
```


## 延伸阅读

### 知识系统内部链接

- [中断优先级配置](01-interrupt-priority.html) — 编码器Z相中断与控制中断的优先级设置
- [中断安全编程](03-interrupt-safety.html) — 中断与主程序共享编码器数据的安全处理（volatile、临界区）
- [直流电机控制](../../../01-hardware-layer/05-actuator-control/beginner/01-dc-motor-control.html) — 电机驱动基础，PWM控制原理
- [电机驱动电路](../../../01-hardware-layer/02-hardware-design-fundamentals/intermediate/06-motor-driver-circuit.html) — H桥驱动电路设计，与编码器配合使用
- [加速度计与陀螺仪](../../../01-hardware-layer/04-sensor-technology/intermediate/04-accelerometer-gyroscope.html) — IMU传感器，与编码器融合用于机器人定位

### 进阶主题

**FOC（磁场定向控制）**：
- 无刷电机的高性能控制方案
- 需要高分辨率编码器（>2000线）或磁编码器（AS5048A）
- 参考：ST AN5397《STM32 FOC SDK用户手册》

**EtherCAT编码器接口**：
- 工业伺服系统的标准接口
- 支持EnDat 2.2、BiSS-C、HIPERFACE等协议
- 参考：Beckhoff EL5101编码器接口模块

**软件编码器（QSPI/SPI磁编码器）**：
- AS5048A：14位绝对角度，SPI接口，适合无刷电机FOC
- MA730：14位，SPI，-40~125°C，适合工业场合
- TLE5012B：GMR磁阻传感器，15位，SPI/SSC接口

## 参考资料

1. **STM32F4 Reference Manual (RM0090)** — Timer Encoder Interface Mode，第14章
   - 详细描述TIM2/TIM5 32位编码器模式寄存器配置
2. **ST Application Note AN4013** — STM32 timer overview
   - 各定时器功能对比，编码器模式最佳实践
3. **《现代电机控制技术》** — 王兆安，机械工业出版社
   - 第8章：位置/速度传感器，第10章：数字PID控制
4. **《机器人学导论》** — John J. Craig，机械工业出版社
   - 里程计章节：编码器在移动机器人中的应用
5. **AM26LS32 Datasheet** — Texas Instruments
   - RS422差分接收器，编码器长距离传输方案
6. **AS5048A Datasheet** — ams AG
   - 14位磁编码器，SPI/PWM接口，适合无刷电机
7. **《传感器原理及工程应用》** — 郭长城，电子工业出版社
   - 第6章：位移与速度传感器
8. **Ziegler-Nichols PID Tuning Method** — J.G. Ziegler, N.B. Nichols (1942)
   - 经典PID参数整定方法，适用于速度/位置控制
9. **《嵌入式实时操作系统FreeRTOS原理与实践》** — 刘火良
   - 多任务环境下编码器数据共享与同步
10. **GRBL开源固件** — github.com/gnea/grbl
    - 基于AVR/STM32的步进电机控制，包含编码器反馈实现参考

