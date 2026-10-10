---
title: "智能云台项目：自动追踪与姿态稳定"
description: "完整的两轴智能云台项目，集成MPU6050姿态传感器、PID稳定控制和视觉追踪，实现防抖稳定和目标自动追踪功能"
slug: "smart-gimbal-auto-tracking-project"

domain: "底层硬件层"
module: "执行器控制"
content_type: "project"
skill_level: "advanced"

tags:
  - 云台
  - 舵机控制
  - PID控制
  - 姿态稳定
  - 目标追踪
  - MPU6050
prerequisites:
  - "beginner/03-servo-motor-control"
  - "intermediate/03-pid-control"
related_contents:
  - "advanced/05-robot-arm-project"
  - "advanced/02-motion-control-algorithms"

estimated_time: 180
difficulty_score: 4

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "1.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: true
is_premium: false

keywords:
  - 智能云台
  - 自动追踪云台
  - 舵机PID控制
  - 姿态稳定
cover_image: ""
---

# 智能云台项目：自动追踪与姿态稳定

---

## 1. 项目概述

### 1.1 项目背景

云台（Gimbal）是一种用于稳定摄像机或传感器的机械装置，通过主动控制旋转轴来抵消载体的振动和姿态变化。随着无人机、运动相机和安防监控的普及，智能云台已成为现代影像系统的核心组件。

传统的被动减振方案（橡胶减振球、弹簧阻尼）只能衰减高频振动，对低频晃动和姿态偏转几乎无效。主动稳定云台通过惯性测量单元（IMU）实时感知姿态变化，并驱动电机进行反向补偿，可以实现毫秒级的响应速度和亚度级的稳定精度。

本项目构建一个完整的两轴（Pan/Tilt）智能云台系统，具备以下核心能力：

- **姿态稳定模式**：通过MPU6050检测载体的俯仰（Pitch）和横滚（Roll）变化，驱动舵机进行实时补偿，将摄像头保持在水平稳定状态
- **视觉追踪模式**：通过OpenMV摄像头检测特定颜色目标，将目标锁定在画面中心，实现自动跟踪
- **模式切换**：通过按键在两种模式间无缝切换，LED指示当前工作状态

### 1.2 应用场景

**无人机航拍**

无人机飞行时受到螺旋桨振动、风力扰动和机身姿态变化的影响，摄像头会产生严重抖动。两轴云台可以补偿俯仰和横滚方向的扰动，配合三轴云台还能补偿偏航，使航拍画面保持平稳。典型应用包括大疆Phantom系列、Inspire系列的云台系统。

**手持稳定器**

手持拍摄时，手部的细微抖动会导致画面不稳。手持云台（如大疆如影、智云CRANE系列）通过三轴无刷电机主动补偿，使摄影师可以边走边拍而画面依然平稳。

**安防监控**

PTZ（Pan-Tilt-Zoom）摄像机是安防领域的标准配置，可以远程控制摄像头的水平旋转（Pan）、垂直俯仰（Tilt）和焦距缩放（Zoom）。智能云台还可以结合人脸识别或运动检测，自动追踪可疑目标。

**机器人视觉**

服务机器人、巡检机器人需要摄像头跟踪目标人物或感兴趣区域。云台提供了比整体转动机身更快速、更精确的视觉定向能力。

**科学仪器**

天文望远镜的赤道仪、激光测距仪的指向系统、卫星天线的跟踪系统，都是云台控制的典型应用，对精度要求极高。

### 1.3 功能特性列表

| 功能 | 规格 | 说明 |
|------|------|------|
| 控制轴数 | 2轴（Pan + Tilt） | 水平旋转 ± 90°，垂直俯仰 ± 45° |
| 姿态传感器 | MPU6050 6轴IMU | 3轴加速度计 + 3轴陀螺仪 |
| 姿态解算 | 互补滤波 | 100Hz更新率，精度 ± 1° |
| 控制算法 | 双轴独立PID | 位置式PID，抗积分饱和 |
| 控制频率 | 100Hz | 10ms定时器中断 |
| 舵机类型 | MG996R金属齿轮 | 扭矩13kg·cm，速度0.17s/60° |
| 视觉追踪 | OpenMV H7 | UART通信，30fps目标检测 |
| 通信接口 | UART + I2C | 调试串口 + IMU通信 |
| 工作电压 | 5V（舵机）/ 3.3V（MCU） | 独立供电，防干扰 |
| 功耗 | 最大2.5A@5V | 双舵机满载 |

### 1.4 技术难点分析

**难点1：姿态解算的漂移问题**

陀螺仪积分会产生累积误差（漂移），加速度计在动态条件下受振动干扰严重。单独使用任何一种传感器都无法获得准确的长期姿态估计。互补滤波通过融合两种传感器的优势（陀螺仪短期精确、加速度计长期稳定）来解决这个问题。

**难点2：PID参数整定**

云台系统是一个非线性、时变的控制对象。舵机的死区、摩擦力、负载变化都会影响控制特性。PID参数过大会导致振荡，过小会导致响应迟缓。需要系统化的整定方法和在线调参能力。

**难点3：舵机控制精度**

标准舵机的PWM控制精度受限于定时器分辨率和舵机本身的机械精度。MG996R的死区约为±5μs，对应约±0.45°的角度误差。需要合理设计PWM参数以充分利用定时器分辨率。

**难点4：视觉追踪的延迟**

从摄像头采集图像到云台响应，存在图像处理延迟（约33ms@30fps）、串口传输延迟（约1ms）和控制计算延迟（约1ms）。总延迟约35ms，在高速运动追踪时会导致明显的滞后。需要通过预测算法或提高帧率来改善。

**难点5：模式切换的平滑过渡**

从稳定模式切换到追踪模式时，如果直接切换PID目标值，可能导致云台突然跳动。需要设计平滑过渡机制，逐渐将目标值从当前位置过渡到新目标。

---

## 2. 硬件系统设计

### 2.1 完整硬件清单

| 器件 | 型号/规格 | 数量 | 参考价格 | 选型理由 |
|------|-----------|------|----------|----------|
| 主控MCU | STM32F103C8T6（蓝色小板） | 1 | ¥15 | 72MHz Cortex-M3，丰富定时器，I2C/UART齐全，性价比极高 |
| 舵机（Pan轴） | MG996R 金属齿轮舵机 | 1 | ¥18 | 13kg·cm扭矩，金属齿轮耐用，180°行程 |
| 舵机（Tilt轴） | MG996R 金属齿轮舵机 | 1 | ¥18 | 同上，双轴统一型号便于调参 |
| 姿态传感器 | MPU6050 GY-521模块 | 1 | ¥8 | 6轴IMU，I2C接口，内置DMP，资料丰富 |
| 视觉模块 | OpenMV H7 | 1 | ¥380 | MicroPython编程，内置颜色追踪算法，UART输出 |
| 云台支架 | 铝合金两轴云台套件 | 1 | ¥35 | 含两个舵机安装座，结构紧凑，重量轻 |
| 降压模块 | LM2596 5V/3A | 1 | ¥5 | 为舵机提供稳定5V电源，与MCU电源隔离 |
| 主电源 | 7.4V 2S锂电池 2200mAh | 1 | ¥45 | 为整个系统供电，容量足够长时间工作 |
| 电容 | 1000μF/10V 电解电容 | 2 | ¥2 | 舵机电源滤波，抑制启动冲击电流 |
| 电容 | 100nF 陶瓷电容 | 4 | ¥1 | 高频去耦 |
| 电阻 | 4.7kΩ | 2 | ¥0.5 | I2C上拉电阻 |
| LED | 红色/绿色 3mm | 2 | ¥1 | 模式状态指示 |
| 电阻 | 330Ω | 2 | ¥0.5 | LED限流 |
| 按键 | 6×6mm 轻触开关 | 1 | ¥0.5 | 模式切换 |
| 排针/杜邦线 | 2.54mm | 若干 | ¥5 | 连接各模块 |
| 洞洞板 | 5×7cm | 1 | ¥3 | 焊接主控电路 |
| **合计** | | | **约¥537** | |

**选型说明**

MG996R vs SG90：SG90扭矩仅1.8kg·cm，对于承载摄像头的云台来说扭矩不足，在快速运动时容易失步。MG996R的13kg·cm扭矩有充足余量，金属齿轮也更耐磨。

STM32F103C8T6 vs Arduino Nano：Arduino的16MHz时钟和有限的定时器资源难以同时处理100Hz控制循环、I2C通信和UART接收。STM32的72MHz时钟和丰富外设更适合实时控制应用。

OpenMV vs 树莓派摄像头：树莓派需要运行Linux系统，启动时间长，延迟高。OpenMV是专为机器视觉设计的嵌入式平台，启动快，延迟低，通过UART与STM32通信简单可靠。

### 2.2 详细电路原理图

```
                        智能云台系统电路原理图
                        ========================

    7.4V锂电池
    ┌─────────┐
    │ + ─────────────────────────────────────────────────────┐
    │         │                                              │
    │ - ──────┼──────────────────────────────────────────── GND
    └─────────┘
               │
               ▼
    ┌──────────────────┐
    │   LM2596 降压    │  5V/3A输出
    │   IN: 7.4V       ├──────────────────────────────────────┐
    │   OUT: 5V        │                                      │
    └──────────────────┘                                      │
                                                              │
    ┌─────────────────────────────────────────────────────────┼──┐
    │              STM32F103C8T6                              │  │
    │                                                         │  │
    │  3.3V ◄── AMS1117-3.3 ◄──────────────────────────── 5V │  │
    │                                                         │  │
    │  PA0 (TIM2_CH1) ──────────────────────────────────────► │  │
    │                                                    Pan舵机信号
    │  PA1 (TIM2_CH2) ──────────────────────────────────────► │  │
    │                                                   Tilt舵机信号
    │  PB6 (I2C1_SCL) ──── 4.7kΩ ──► 3.3V              │  │
    │                  └──────────────────────────────► MPU6050 SCL
    │  PB7 (I2C1_SDA) ──── 4.7kΩ ──► 3.3V              │  │
    │                  └──────────────────────────────► MPU6050 SDA
    │                                                         │  │
    │  PA9  (USART1_TX) ─────────────────────────────────────►│  │
    │                                                   OpenMV RX
    │  PA10 (USART1_RX) ◄────────────────────────────────────│  │
    │                                                   OpenMV TX
    │                                                         │  │
    │  PA2  (USART2_TX) ──────────────────────────────────────►调试串口TX
    │  PA3  (USART2_RX) ◄─────────────────────────────────────调试串口RX
    │                                                         │  │
    │  PA8  ──── 按键 ──── GND  (模式切换，内部上拉)          │  │
    │                                                         │  │
    │  PC13 ──── 330Ω ──── LED红 ──── GND (稳定模式指示)     │  │
    │  PB12 ──── 330Ω ──── LED绿 ──── GND (追踪模式指示)     │  │
    │                                                         │  │
    └─────────────────────────────────────────────────────────┘  │
                                                                  │
    舵机电源（5V独立供电）                                        │
    ┌──────────────────────────────────────────────────────────┐  │
    │  5V ◄──────────────────────────────────────────────────── ┘  │
    │  ├── 1000μF电解电容 ──► GND  (大容量滤波)                    │
    │  ├── 100nF陶瓷电容  ──► GND  (高频去耦)                      │
    │  │                                                            │
    │  ├── Pan舵机  红线(+5V) ── 橙线(信号←PA0) ── 棕线(GND)      │
    │  └── Tilt舵机 红线(+5V) ── 橙线(信号←PA1) ── 棕线(GND)      │
    └──────────────────────────────────────────────────────────────┘

    MPU6050 GY-521模块
    ┌─────────────────┐
    │  VCC ──► 3.3V   │
    │  GND ──► GND    │
    │  SCL ──► PB6    │
    │  SDA ──► PB7    │
    │  AD0 ──► GND    │  (I2C地址 0x68)
    │  INT ──► PB0    │  (数据就绪中断，可选)
    └─────────────────┘
```

### 2.3 电源设计分析

**电源需求计算**

MG996R舵机规格：
- 空载电流：约200mA
- 堵转电流：约1400mA
- 正常工作电流：约500mA

双舵机同时工作的最大电流估算：
- 正常工作：2 × 500mA = 1000mA
- 启动冲击：2 × 1400mA = 2800mA（短暂）
- MCU + 传感器：约200mA

因此选用5V/3A的LM2596降压模块，持续电流3A满足正常工作需求，配合1000μF大电容吸收启动冲击电流。

**电源隔离设计**

舵机是感性负载，启动和换向时会产生较大的电流冲击和电磁干扰。如果舵机和MCU共用电源，电流冲击会导致电源电压跌落，可能引起MCU复位或传感器读数异常。

解决方案：
1. 舵机使用独立的5V/3A降压模块供电
2. MCU使用板载AMS1117-3.3从5V降压到3.3V
3. 在舵机电源线上并联1000μF电解电容和100nF陶瓷电容
4. 信号线上串联100Ω电阻，防止高频干扰通过信号线传入MCU

**LM2596配置**

LM2596是一款简单易用的降压开关电源IC，输出电压通过外部分压电阻设定：

```
Vout = Vref × (1 + R2/R1)
Vref = 1.23V（LM2596内部参考）

目标Vout = 5V：
5 = 1.23 × (1 + R2/R1)
R2/R1 = (5/1.23) - 1 = 3.065

选取R1 = 1kΩ，R2 = 3.09kΩ（用3.3kΩ并联100kΩ近似）
实际可使用LM2596可调版模块，通过电位器直接调节输出电压
```

### 2.4 PCB布局建议

如果制作PCB，以下布局原则可以减少干扰：

1. **电源区域**：LM2596及其滤波电容放置在PCB一角，远离MCU和传感器
2. **模拟区域**：MPU6050尽量远离开关电源和舵机驱动信号线
3. **地平面**：使用完整的地平面（铺铜），减少地线阻抗
4. **去耦电容**：每个IC的VCC引脚旁放置100nF陶瓷电容，尽量靠近引脚
5. **I2C走线**：SCL和SDA走线尽量短，避免与PWM信号线平行走线
6. **舵机接口**：舵机连接器靠近板边，信号线串联100Ω电阻

---

## 3. 舵机PWM驱动

### 3.1 50Hz PWM原理详解

标准RC舵机使用50Hz（周期20ms）的PWM信号控制角度：

```
PWM信号时序图：
                    ┌──┐                              ┌──┐
                    │  │                              │  │
────────────────────┘  └──────────────────────────────┘  └────
│←────────────── 20ms（50Hz周期）──────────────────→│
         │←脉宽→│
         500μs ~ 2500μs

脉宽与角度对应关系（MG996R）：
  500μs  → -90°（最左/最下）
  1000μs → -45°
  1500μs →   0°（中位）
  2000μs → +45°
  2500μs → +90°（最右/最上）

角度分辨率：
  脉宽范围：2500 - 500 = 2000μs
  角度范围：90 - (-90) = 180°
  分辨率：2000μs / 180° ≈ 11.1μs/°
```

**为什么是50Hz？**

早期RC接收机使用模拟电路产生50Hz信号，舵机内部的控制电路也是针对50Hz设计的。舵机内部有一个基准信号发生器，产生约1.5ms的基准脉冲，通过比较外部PWM脉宽与基准脉宽的差值来驱动电机。

现代数字舵机（如MG996R）可以接受更高频率（最高333Hz），更高的更新频率可以提高响应速度，但也会增加功耗。本项目使用标准50Hz以保证兼容性。

### 3.2 STM32 TIM2配置（含CubeMX步骤）

**CubeMX配置步骤**

1. 打开CubeMX，选择STM32F103C8T6
2. 在Pinout视图中，点击PA0，选择TIM2_CH1
3. 点击PA1，选择TIM2_CH2
4. 在左侧Timers → TIM2中：
   - Mode: Internal Clock
   - Channel1: PWM Generation CH1
   - Channel2: PWM Generation CH2
5. 在Configuration → Parameter Settings中：
   - Prescaler: 71（72MHz / 72 = 1MHz）
   - Counter Period: 19999（1MHz / 20000 = 50Hz）
   - Counter Mode: Up
   - Clock Division: No Division
   - Auto-reload preload: Enable
6. Channel Settings（CH1和CH2相同）：
   - Mode: PWM mode 1
   - Pulse: 1500（初始中位）
   - Output compare preload: Enable
   - Fast Mode: Disable
   - Polarity: High
7. 生成代码

**手动配置代码（不使用CubeMX）**

```c
/* gimbal_pwm.h */
#ifndef GIMBAL_PWM_H
#define GIMBAL_PWM_H

#include "stm32f1xx_hal.h"

/* 舵机通道定义 */
#define GIMBAL_CH_PAN   0   /* Pan轴：TIM2_CH1，PA0 */
#define GIMBAL_CH_TILT  1   /* Tilt轴：TIM2_CH2，PA1 */

/* 脉宽范围（单位：定时器计数值，1计数 = 1μs） */
#define SERVO_PULSE_MIN   500   /* 对应 -90° */
#define SERVO_PULSE_MID  1500   /* 对应   0° */
#define SERVO_PULSE_MAX  2500   /* 对应 +90° */

/* 角度范围 */
#define SERVO_ANGLE_MIN  -90.0f
#define SERVO_ANGLE_MAX   90.0f

/* Pan轴物理限位（防止云台结构干涉） */
#define PAN_ANGLE_MIN   -80.0f
#define PAN_ANGLE_MAX    80.0f

/* Tilt轴物理限位 */
#define TILT_ANGLE_MIN  -45.0f
#define TILT_ANGLE_MAX   45.0f

void gimbal_pwm_init(void);
void gimbal_set_angle(uint8_t ch, float angle);
void gimbal_set_pulse(uint8_t ch, uint32_t pulse_us);
float gimbal_get_angle(uint8_t ch);
void gimbal_center(void);

#endif /* GIMBAL_PWM_H */
```

```c
/* gimbal_pwm.c */
#include "gimbal_pwm.h"

/* 全局定时器句柄（需要在其他地方访问） */
TIM_HandleTypeDef htim2;

/* 当前角度记录 */
static float current_angle[2] = {0.0f, 0.0f};

/**
 * @brief  初始化云台PWM输出
 * @note   TIM2，72MHz时钟
 *         Prescaler=71 → 1MHz计数频率（1μs分辨率）
 *         Period=19999  → 20ms周期（50Hz）
 *         PA0 = TIM2_CH1 = Pan轴
 *         PA1 = TIM2_CH2 = Tilt轴
 */
void gimbal_pwm_init(void)
{
    GPIO_InitTypeDef gpio = {0};
    TIM_OC_InitTypeDef oc  = {0};

    /* 1. 使能时钟 */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();

    /* 2. 配置PA0、PA1为复用推挽输出 */
    gpio.Pin   = GPIO_PIN_0 | GPIO_PIN_1;
    gpio.Mode  = GPIO_MODE_AF_PP;       /* 复用推挽 */
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;  /* 高速，确保PWM边沿陡峭 */
    HAL_GPIO_Init(GPIOA, &gpio);

    /* 3. 配置TIM2基本参数 */
    htim2.Instance               = TIM2;
    htim2.Init.Prescaler         = 72 - 1;     /* 72MHz / 72 = 1MHz */
    htim2.Init.Period            = 20000 - 1;  /* 1MHz / 20000 = 50Hz */
    htim2.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim2.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_PWM_Init(&htim2);

    /* 4. 配置PWM输出通道 */
    oc.OCMode       = TIM_OCMODE_PWM1;          /* 计数值 < CCR时输出高电平 */
    oc.OCPolarity   = TIM_OCPOLARITY_HIGH;
    oc.OCFastMode   = TIM_OCFAST_DISABLE;
    oc.OCNPolarity  = TIM_OCNPOLARITY_HIGH;
    oc.OCNIdleState = TIM_OCNIDLESTATE_RESET;
    oc.OCIdleState  = TIM_OCIDLESTATE_RESET;

    /* CH1：Pan轴，初始中位1500μs */
    oc.Pulse = SERVO_PULSE_MID;
    HAL_TIM_PWM_ConfigChannel(&htim2, &oc, TIM_CHANNEL_1);

    /* CH2：Tilt轴，初始中位1500μs */
    oc.Pulse = SERVO_PULSE_MID;
    HAL_TIM_PWM_ConfigChannel(&htim2, &oc, TIM_CHANNEL_2);

    /* 5. 启动PWM输出 */
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
}

/**
 * @brief  设置舵机角度
 * @param  ch     通道：GIMBAL_CH_PAN 或 GIMBAL_CH_TILT
 * @param  angle  目标角度，单位：度，范围 -90° ~ +90°
 */
void gimbal_set_angle(uint8_t ch, float angle)
{
    /* 根据通道应用物理限位 */
    float angle_min = (ch == GIMBAL_CH_PAN) ? PAN_ANGLE_MIN  : TILT_ANGLE_MIN;
    float angle_max = (ch == GIMBAL_CH_PAN) ? PAN_ANGLE_MAX  : TILT_ANGLE_MAX;

    /* 限幅 */
    if (angle > angle_max) angle = angle_max;
    if (angle < angle_min) angle = angle_min;

    /* 角度转脉宽：线性映射
     * angle=-90° → pulse=500μs
     * angle=  0° → pulse=1500μs
     * angle=+90° → pulse=2500μs
     * pulse = 1500 + angle * (1000/90)
     */
    uint32_t pulse = (uint32_t)(SERVO_PULSE_MID +
                                angle * ((float)(SERVO_PULSE_MAX - SERVO_PULSE_MID) /
                                         SERVO_ANGLE_MAX));

    /* 安全限幅（防止计算误差超出范围） */
    if (pulse > SERVO_PULSE_MAX) pulse = SERVO_PULSE_MAX;
    if (pulse < SERVO_PULSE_MIN) pulse = SERVO_PULSE_MIN;

    /* 写入比较寄存器 */
    if (ch == GIMBAL_CH_PAN) {
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse);
    } else {
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pulse);
    }

    /* 记录当前角度 */
    current_angle[ch] = angle;
}

/**
 * @brief  直接设置脉宽（用于精细调试）
 * @param  ch        通道
 * @param  pulse_us  脉宽，单位微秒，范围 500~2500
 */
void gimbal_set_pulse(uint8_t ch, uint32_t pulse_us)
{
    if (pulse_us > SERVO_PULSE_MAX) pulse_us = SERVO_PULSE_MAX;
    if (pulse_us < SERVO_PULSE_MIN) pulse_us = SERVO_PULSE_MIN;

    if (ch == GIMBAL_CH_PAN) {
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse_us);
    } else {
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pulse_us);
    }
    /* 反算角度并记录 */
    current_angle[ch] = ((float)pulse_us - SERVO_PULSE_MID) *
                        (SERVO_ANGLE_MAX / (float)(SERVO_PULSE_MAX - SERVO_PULSE_MID));
}

/** @brief 获取当前角度 */
float gimbal_get_angle(uint8_t ch)
{
    return current_angle[ch];
}

/** @brief 云台回中 */
void gimbal_center(void)
{
    gimbal_set_angle(GIMBAL_CH_PAN,  0.0f);
    gimbal_set_angle(GIMBAL_CH_TILT, 0.0f);
}

### 3.3 舵机死区处理

MG996R舵机存在约±5μs的死区，即脉宽变化小于5μs时舵机不会响应。在PID控制中，如果误差很小，PID输出的角度变化量可能落在死区内，导致舵机不动但积分项持续累积，最终引起积分饱和和振荡。

```c
/**
 * @brief  带死区补偿的角度设置
 * @note   当角度变化量小于死区阈值时，不更新舵机
 *         避免频繁的微小调整导致舵机抖动和发热
 */
#define SERVO_DEADBAND_DEG  0.5f  /* 死区：±0.5°，对应约±5.5μs */

void gimbal_set_angle_with_deadband(uint8_t ch, float angle)
{
    float delta = angle - current_angle[ch];

    /* 死区判断：变化量小于阈值则不更新 */
    if (delta > -SERVO_DEADBAND_DEG && delta < SERVO_DEADBAND_DEG) {
        return;
    }

    gimbal_set_angle(ch, angle);
}
```

### 3.4 多舵机同步控制

在某些应用中，需要两个舵机同时到达目标位置（例如云台快速转向时）。由于两轴的运动距离不同，如果以相同速度运动，会先后到达目标，导致运动轨迹不平滑。

```c
/**
 * @brief  同步移动两轴到目标角度（线性插值）
 * @param  pan_target   Pan轴目标角度
 * @param  tilt_target  Tilt轴目标角度
 * @param  steps        插值步数（步数越多越平滑，但到达时间越长）
 * @param  step_delay_ms 每步延时（毫秒）
 */
void gimbal_move_sync(float pan_target, float tilt_target,
                      uint16_t steps, uint16_t step_delay_ms)
{
    float pan_start  = gimbal_get_angle(GIMBAL_CH_PAN);
    float tilt_start = gimbal_get_angle(GIMBAL_CH_TILT);

    for (uint16_t i = 1; i <= steps; i++) {
        float t = (float)i / (float)steps;  /* 0.0 ~ 1.0 */

        /* 线性插值 */
        float pan_now  = pan_start  + t * (pan_target  - pan_start);
        float tilt_now = tilt_start + t * (tilt_target - tilt_start);

        gimbal_set_angle(GIMBAL_CH_PAN,  pan_now);
        gimbal_set_angle(GIMBAL_CH_TILT, tilt_now);

        HAL_Delay(step_delay_ms);
    }
}
```

---

## 4. MPU6050姿态传感器

### 4.1 I2C通信协议

MPU6050通过I2C总线与STM32通信。I2C是一种两线制串行总线，使用SCL（时钟线）和SDA（数据线）。

**I2C地址**

MPU6050的7位I2C地址由AD0引脚决定：
- AD0 = 0（接GND）：地址 = 0x68
- AD0 = 1（接VCC）：地址 = 0x69

写操作地址：0xD0（0x68 << 1 | 0）
读操作地址：0xD1（0x68 << 1 | 1）

**I2C时序**

```
写寄存器时序：
START → 设备地址(写) → ACK → 寄存器地址 → ACK → 数据 → ACK → STOP

读寄存器时序：
START → 设备地址(写) → ACK → 寄存器地址 → ACK →
RESTART → 设备地址(读) → ACK → 数据 → NACK → STOP
```

**STM32 I2C配置**

```c
/* I2C1配置：PB6=SCL，PB7=SDA，400kHz快速模式 */
I2C_HandleTypeDef hi2c1;

void i2c1_init(void)
{
    hi2c1.Instance             = I2C1;
    hi2c1.Init.ClockSpeed      = 400000;           /* 400kHz快速模式 */
    hi2c1.Init.DutyCycle       = I2C_DUTYCYCLE_2;  /* 标准占空比 */
    hi2c1.Init.OwnAddress1     = 0;
    hi2c1.Init.AddressingMode  = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode   = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}
```

### 4.2 MPU6050关键寄存器详解

| 寄存器地址 | 名称 | 说明 |
|-----------|------|------|
| 0x6B | PWR_MGMT_1 | 电源管理，复位后默认睡眠模式，需清零唤醒 |
| 0x6C | PWR_MGMT_2 | 各轴使能控制 |
| 0x19 | SMPLRT_DIV | 采样率分频：采样率 = 陀螺仪输出率 / (1 + SMPLRT_DIV) |
| 0x1A | CONFIG | DLPF（数字低通滤波器）配置 |
| 0x1B | GYRO_CONFIG | 陀螺仪量程：0=±250°/s，1=±500°/s，2=±1000°/s，3=±2000°/s |
| 0x1C | ACCEL_CONFIG | 加速度计量程：0=±2g，1=±4g，2=±8g，3=±16g |
| 0x3B~0x40 | ACCEL_XOUT_H~ACCEL_ZOUT_L | 加速度计原始数据（各16位有符号整数） |
| 0x41~0x42 | TEMP_OUT_H~TEMP_OUT_L | 温度原始数据 |
| 0x43~0x48 | GYRO_XOUT_H~GYRO_ZOUT_L | 陀螺仪原始数据（各16位有符号整数） |
| 0x75 | WHO_AM_I | 设备ID，固定值0x68，用于验证通信 |

**DLPF配置（数字低通滤波器）**

```
CONFIG寄存器 DLPF_CFG 位：
  000: 加速度计260Hz，陀螺仪256Hz（无滤波，噪声最大）
  001: 加速度计184Hz，陀螺仪188Hz
  010: 加速度计94Hz， 陀螺仪98Hz
  011: 加速度计44Hz， 陀螺仪42Hz  ← 推荐（云台应用）
  100: 加速度计21Hz， 陀螺仪20Hz
  101: 加速度计10Hz， 陀螺仪10Hz
  110: 加速度计5Hz，  陀螺仪5Hz（最平滑，延迟最大）
```

对于100Hz控制频率的云台，选择DLPF_CFG=3（44Hz截止频率）是合理的折中：既能滤除高频振动噪声，又不会引入过大的相位延迟。

### 4.3 完整初始化代码

```c
/* mpu6050.h */
#ifndef MPU6050_H
#define MPU6050_H

#include "stm32f1xx_hal.h"

/* I2C地址（AD0=GND） */
#define MPU6050_ADDR        0x68
#define MPU6050_ADDR_WRITE  (MPU6050_ADDR << 1)
#define MPU6050_ADDR_READ   (MPU6050_ADDR_WRITE | 1)

/* 寄存器地址 */
#define MPU6050_REG_SMPLRT_DIV   0x19
#define MPU6050_REG_CONFIG       0x1A
#define MPU6050_REG_GYRO_CONFIG  0x1B
#define MPU6050_REG_ACCEL_CONFIG 0x1C
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_TEMP_OUT_H   0x41
#define MPU6050_REG_GYRO_XOUT_H  0x43
#define MPU6050_REG_PWR_MGMT_1   0x6B
#define MPU6050_REG_WHO_AM_I     0x75

/* 量程配置 */
#define GYRO_SCALE_250   0x00  /* ±250°/s，灵敏度131 LSB/(°/s) */
#define GYRO_SCALE_500   0x08  /* ±500°/s，灵敏度65.5 LSB/(°/s) */
#define GYRO_SCALE_1000  0x10  /* ±1000°/s，灵敏度32.8 LSB/(°/s) */
#define GYRO_SCALE_2000  0x18  /* ±2000°/s，灵敏度16.4 LSB/(°/s) */

#define ACCEL_SCALE_2G   0x00  /* ±2g，灵敏度16384 LSB/g */
#define ACCEL_SCALE_4G   0x08  /* ±4g，灵敏度8192 LSB/g */
#define ACCEL_SCALE_8G   0x10  /* ±8g，灵敏度4096 LSB/g */
#define ACCEL_SCALE_16G  0x18  /* ±16g，灵敏度2048 LSB/g */

/* 灵敏度（对应±250°/s和±2g量程） */
#define GYRO_SENSITIVITY   131.0f   /* LSB/(°/s) */
#define ACCEL_SENSITIVITY  16384.0f /* LSB/g */

/* 温度转换公式：Temperature(°C) = (TEMP_OUT / 340.0) + 36.53 */
#define TEMP_SENSITIVITY   340.0f
#define TEMP_OFFSET        36.53f

/* 数据结构 */
typedef struct {
    float ax, ay, az;  /* 加速度，单位：g */
    float gx, gy, gz;  /* 角速度，单位：°/s */
    float temp;        /* 温度，单位：°C */
} MPU6050_Data;

typedef struct {
    float ax_offset, ay_offset, az_offset;  /* 加速度计零偏 */
    float gx_offset, gy_offset, gz_offset;  /* 陀螺仪零偏 */
} MPU6050_Offset;

/* 函数声明 */
HAL_StatusTypeDef mpu6050_init(void);
HAL_StatusTypeDef mpu6050_read_raw(MPU6050_Data *data);
HAL_StatusTypeDef mpu6050_read_calibrated(MPU6050_Data *data,
                                           const MPU6050_Offset *offset);
void mpu6050_calibrate(MPU6050_Offset *offset, uint16_t samples);

#endif /* MPU6050_H */
```

```c
/* mpu6050.c */
#include "mpu6050.h"
#include <string.h>

extern I2C_HandleTypeDef hi2c1;

/* 内部辅助函数：写单个寄存器 */
static HAL_StatusTypeDef mpu_write_reg(uint8_t reg, uint8_t data)
{
    uint8_t buf[2] = {reg, data};
    return HAL_I2C_Master_Transmit(&hi2c1, MPU6050_ADDR_WRITE,
                                   buf, 2, HAL_MAX_DELAY);
}

/* 内部辅助函数：读多个寄存器 */
static HAL_StatusTypeDef mpu_read_regs(uint8_t reg, uint8_t *buf, uint16_t len)
{
    HAL_StatusTypeDef ret;
    /* 先发送寄存器地址 */
    ret = HAL_I2C_Master_Transmit(&hi2c1, MPU6050_ADDR_WRITE,
                                  &reg, 1, HAL_MAX_DELAY);
    if (ret != HAL_OK) return ret;
    /* 再读取数据 */
    return HAL_I2C_Master_Receive(&hi2c1, MPU6050_ADDR_READ,
                                  buf, len, HAL_MAX_DELAY);
}

/**
 * @brief  初始化MPU6050
 * @retval HAL_OK 成功，HAL_ERROR 失败（设备未找到）
 */
HAL_StatusTypeDef mpu6050_init(void)
{
    uint8_t who_am_i = 0;

    /* 1. 验证设备ID */
    if (mpu_read_regs(MPU6050_REG_WHO_AM_I, &who_am_i, 1) != HAL_OK) {
        return HAL_ERROR;
    }
    if (who_am_i != 0x68) {
        return HAL_ERROR;  /* 设备ID不匹配 */
    }

    /* 2. 复位设备（PWR_MGMT_1 bit7=1） */
    mpu_write_reg(MPU6050_REG_PWR_MGMT_1, 0x80);
    HAL_Delay(100);  /* 等待复位完成 */

    /* 3. 唤醒设备，选择PLL时钟源（比内部8MHz振荡器更稳定）
     *    PWR_MGMT_1: SLEEP=0, CLKSEL=001（X轴陀螺仪PLL）
     */
    mpu_write_reg(MPU6050_REG_PWR_MGMT_1, 0x01);
    HAL_Delay(10);

    /* 4. 配置采样率
     *    陀螺仪输出率 = 1kHz（DLPF使能时）
     *    采样率 = 1000 / (1 + 9) = 100Hz
     */
    mpu_write_reg(MPU6050_REG_SMPLRT_DIV, 9);

    /* 5. 配置DLPF：截止频率44Hz（DLPF_CFG=3）
     *    同时设置FSYNC=0（不使用外部同步）
     */
    mpu_write_reg(MPU6050_REG_CONFIG, 0x03);

    /* 6. 配置陀螺仪量程：±500°/s
     *    云台最大角速度约200°/s，±500°/s有足够余量
     *    灵敏度：65.5 LSB/(°/s)
     */
    mpu_write_reg(MPU6050_REG_GYRO_CONFIG, GYRO_SCALE_500);

    /* 7. 配置加速度计量程：±2g
     *    云台正常工作时加速度不超过1g，±2g足够
     *    灵敏度：16384 LSB/g（最高精度）
     */
    mpu_write_reg(MPU6050_REG_ACCEL_CONFIG, ACCEL_SCALE_2G);

    return HAL_OK;
}

/**
 * @brief  读取原始传感器数据并转换为物理量
 * @param  data  输出数据结构
 */
HAL_StatusTypeDef mpu6050_read_raw(MPU6050_Data *data)
{
    uint8_t buf[14];  /* 6字节加速度 + 2字节温度 + 6字节陀螺仪 */
    int16_t raw_ax, raw_ay, raw_az;
    int16_t raw_temp;
    int16_t raw_gx, raw_gy, raw_gz;

    /* 从0x3B开始连续读取14个字节 */
    if (mpu_read_regs(MPU6050_REG_ACCEL_XOUT_H, buf, 14) != HAL_OK) {
        return HAL_ERROR;
    }

    /* 合并高低字节（大端序） */
    raw_ax   = (int16_t)(buf[0]  << 8 | buf[1]);
    raw_ay   = (int16_t)(buf[2]  << 8 | buf[3]);
    raw_az   = (int16_t)(buf[4]  << 8 | buf[5]);
    raw_temp = (int16_t)(buf[6]  << 8 | buf[7]);
    raw_gx   = (int16_t)(buf[8]  << 8 | buf[9]);
    raw_gy   = (int16_t)(buf[10] << 8 | buf[11]);
    raw_gz   = (int16_t)(buf[12] << 8 | buf[13]);

    /* 转换为物理量（使用±500°/s量程，灵敏度65.5） */
    data->ax   = (float)raw_ax / ACCEL_SENSITIVITY;   /* 单位：g */
    data->ay   = (float)raw_ay / ACCEL_SENSITIVITY;
    data->az   = (float)raw_az / ACCEL_SENSITIVITY;
    data->gx   = (float)raw_gx / 65.5f;               /* 单位：°/s */
    data->gy   = (float)raw_gy / 65.5f;
    data->gz   = (float)raw_gz / 65.5f;
    data->temp = (float)raw_temp / TEMP_SENSITIVITY + TEMP_OFFSET;

    return HAL_OK;
}

/**
 * @brief  读取校准后的传感器数据（减去零偏）
 */
HAL_StatusTypeDef mpu6050_read_calibrated(MPU6050_Data *data,
                                           const MPU6050_Offset *offset)
{
    HAL_StatusTypeDef ret = mpu6050_read_raw(data);
    if (ret != HAL_OK) return ret;

    data->ax -= offset->ax_offset;
    data->ay -= offset->ay_offset;
    data->az -= offset->az_offset;
    data->gx -= offset->gx_offset;
    data->gy -= offset->gy_offset;
    data->gz -= offset->gz_offset;

    return HAL_OK;
}

/**
 * @brief  零偏校准（静止状态下采集多次取平均）
 * @param  offset   输出零偏结构
 * @param  samples  采样次数（建议500次，约5秒）
 * @note   校准时必须保持传感器静止且水平放置
 *         校准完成后az_offset应接近0（因为静止时az≈1g）
 */
void mpu6050_calibrate(MPU6050_Offset *offset, uint16_t samples)
{
    MPU6050_Data data;
    double sum_ax = 0, sum_ay = 0, sum_az = 0;
    double sum_gx = 0, sum_gy = 0, sum_gz = 0;

    /* 丢弃前50次数据（传感器稳定时间） */
    for (uint16_t i = 0; i < 50; i++) {
        mpu6050_read_raw(&data);
        HAL_Delay(10);
    }

    /* 采集samples次数据 */
    for (uint16_t i = 0; i < samples; i++) {
        mpu6050_read_raw(&data);
        sum_ax += data.ax;
        sum_ay += data.ay;
        sum_az += data.az;
        sum_gx += data.gx;
        sum_gy += data.gy;
        sum_gz += data.gz;
        HAL_Delay(10);  /* 10ms间隔，总计约5秒 */
    }

    /* 计算平均值作为零偏 */
    offset->ax_offset = (float)(sum_ax / samples);
    offset->ay_offset = (float)(sum_ay / samples);
    /* az静止时应为1g（重力），零偏 = 测量值 - 1g */
    offset->az_offset = (float)(sum_az / samples) - 1.0f;
    offset->gx_offset = (float)(sum_gx / samples);
    offset->gy_offset = (float)(sum_gy / samples);
    offset->gz_offset = (float)(sum_gz / samples);
}

---

## 5. 姿态解算算法

### 5.1 欧拉角定义

欧拉角用三个角度描述刚体在三维空间中的姿态：

- **Roll（横滚角，φ）**：绕X轴旋转，飞机左右倾斜
- **Pitch（俯仰角，θ）**：绕Y轴旋转，飞机抬头低头
- **Yaw（偏航角，ψ）**：绕Z轴旋转，飞机左右转向

对于两轴云台，我们主要关心Roll和Pitch，Yaw由Pan轴控制。

**从加速度计计算姿态角**

静止时，加速度计测量的是重力加速度矢量在传感器坐标系中的分量：

```
Roll  = atan2(ay, az)          （绕X轴倾斜）
Pitch = atan2(-ax, sqrt(ay²+az²))  （绕Y轴倾斜）

其中 ax, ay, az 为归一化加速度（单位：g）
```

**从陀螺仪积分计算姿态角**

陀螺仪测量角速度，通过积分得到角度变化：

```
Roll_gyro  += gx * dt
Pitch_gyro += gy * dt
```

### 5.2 互补滤波原理与推导

**问题分析**

- 加速度计：长期稳定（重力方向不变），但短期受振动干扰，噪声大
- 陀螺仪：短期精确（积分精度高），但长期漂移（积分误差累积）

互补滤波的思路：用高通滤波器处理陀螺仪数据（保留快速变化），用低通滤波器处理加速度计数据（保留慢速变化），然后将两者融合。

**数学推导**

设真实角度为 θ，陀螺仪估计为 θ_gyro，加速度计估计为 θ_acc，互补滤波系数为 α（0 < α < 1）：

```
θ_filtered = α × (θ_filtered_prev + ω × dt) + (1-α) × θ_acc

其中：
  α = 0.98（典型值，高通截止频率约0.3Hz）
  ω = 陀螺仪角速度（°/s）
  dt = 采样时间（s）
  θ_acc = atan2(ay, az)（加速度计计算的角度）
```

**截止频率计算**

互补滤波等效于一阶高通滤波器，截止频率：

```
f_c = (1-α) / (2π × α × dt)

当 α=0.98，dt=0.01s：
f_c = 0.02 / (2π × 0.98 × 0.01) ≈ 0.325 Hz

即：低于0.325Hz的慢速变化由加速度计主导
    高于0.325Hz的快速变化由陀螺仪主导
```

### 5.3 完整C代码实现

```c
/* attitude.h */
#ifndef ATTITUDE_H
#define ATTITUDE_H

#include "mpu6050.h"
#include <math.h>

/* 互补滤波系数（0.98表示98%信任陀螺仪，2%信任加速度计） */
#define COMP_FILTER_ALPHA  0.98f

/* 弧度转角度 */
#define RAD_TO_DEG  (180.0f / 3.14159265f)
#define DEG_TO_RAD  (3.14159265f / 180.0f)

typedef struct {
    float roll;   /* 横滚角，单位：度 */
    float pitch;  /* 俯仰角，单位：度 */
    float yaw;    /* 偏航角，单位：度（仅陀螺仪积分，有漂移） */
} Attitude;

void attitude_init(Attitude *att);
void complementary_filter(Attitude *att, const MPU6050_Data *imu, float dt);

#endif /* ATTITUDE_H */
```

```c
/* attitude.c */
#include "attitude.h"

void attitude_init(Attitude *att)
{
    att->roll  = 0.0f;
    att->pitch = 0.0f;
    att->yaw   = 0.0f;
}

/**
 * @brief  互补滤波姿态解算
 * @param  att  姿态结构（输入上次结果，输出本次结果）
 * @param  imu  IMU数据（已校准）
 * @param  dt   采样时间，单位：秒（本项目为0.01s）
 *
 * @note   坐标系定义（右手系）：
 *         X轴：指向前方（机头方向）
 *         Y轴：指向左方
 *         Z轴：指向上方
 *
 *         Roll  = 绕X轴旋转（右倾为正）
 *         Pitch = 绕Y轴旋转（抬头为正）
 */
void complementary_filter(Attitude *att, const MPU6050_Data *imu, float dt)
{
    /* 1. 加速度计计算姿态角（仅在加速度接近1g时可信） */
    float acc_magnitude = sqrtf(imu->ax * imu->ax +
                                imu->ay * imu->ay +
                                imu->az * imu->az);

    float roll_acc  = 0.0f;
    float pitch_acc = 0.0f;

    /* 只有当合加速度在0.5g~1.5g范围内时，加速度计数据才可信 */
    if (acc_magnitude > 0.5f && acc_magnitude < 1.5f) {
        /* atan2返回弧度，转换为角度 */
        roll_acc  = atan2f(imu->ay, imu->az) * RAD_TO_DEG;
        pitch_acc = atan2f(-imu->ax,
                           sqrtf(imu->ay * imu->ay + imu->az * imu->az))
                   * RAD_TO_DEG;
    } else {
        /* 动态条件下，完全信任陀螺仪 */
        roll_acc  = att->roll;
        pitch_acc = att->pitch;
    }

    /* 2. 陀螺仪积分（注意：gx对应Roll，gy对应Pitch） */
    float roll_gyro  = att->roll  + imu->gx * dt;
    float pitch_gyro = att->pitch + imu->gy * dt;

    /* 3. 互补融合 */
    att->roll  = COMP_FILTER_ALPHA * roll_gyro  +
                 (1.0f - COMP_FILTER_ALPHA) * roll_acc;
    att->pitch = COMP_FILTER_ALPHA * pitch_gyro +
                 (1.0f - COMP_FILTER_ALPHA) * pitch_acc;

    /* 4. 偏航角仅用陀螺仪积分（无磁力计时无法修正漂移） */
    att->yaw += imu->gz * dt;

    /* 5. 角度限幅（-180° ~ +180°） */
    if (att->roll  >  180.0f) att->roll  -= 360.0f;
    if (att->roll  < -180.0f) att->roll  += 360.0f;
    if (att->pitch >  180.0f) att->pitch -= 360.0f;
    if (att->pitch < -180.0f) att->pitch += 360.0f;
}
```

### 5.4 卡尔曼滤波对比

卡尔曼滤波是更严格的最优估计方法，但计算量更大：

| 特性 | 互补滤波 | 卡尔曼滤波 |
|------|----------|------------|
| 计算复杂度 | 低（几次乘加） | 中（矩阵运算） |
| 参数调整 | 简单（1个α） | 复杂（Q、R矩阵） |
| 最优性 | 非最优 | 线性最优 |
| 实时性 | 极好 | 好 |
| 精度 | 足够用于云台 | 更高 |
| 适用场景 | 资源受限MCU | 高精度应用 |

对于本项目的云台应用，互补滤波的精度（±1°）完全满足需求，且实现简单，推荐使用。

### 5.5 采样率对精度的影响

采样率越高，陀螺仪积分误差越小，但CPU负载越大：

```
积分误差 ≈ ω_noise × dt × sqrt(N)

其中：
  ω_noise = 陀螺仪噪声密度（MPU6050约0.005°/s/√Hz）
  dt = 采样间隔
  N = 采样次数

1秒内的积分误差：
  100Hz（dt=10ms）：0.005 × 0.01 × sqrt(100) ≈ 0.0005°
  50Hz（dt=20ms）：0.005 × 0.02 × sqrt(50)  ≈ 0.0007°
  10Hz（dt=100ms）：0.005 × 0.1 × sqrt(10)  ≈ 0.0016°
```

100Hz采样率对于云台应用已经足够，更高的采样率收益递减。

---

## 6. PID控制器设计

### 6.1 PID理论回顾

PID控制器由三个部分组成：

```
u(t) = Kp × e(t) + Ki × ∫e(t)dt + Kd × de(t)/dt

其中：
  e(t) = 设定值 - 测量值（误差）
  Kp   = 比例增益（即时响应）
  Ki   = 积分增益（消除稳态误差）
  Kd   = 微分增益（预测趋势，抑制振荡）
```

**各项作用直觉理解**

- **P项**：误差越大，输出越大。就像开车时，偏离车道越多，方向盘打得越多。
- **I项**：误差持续存在时，输出逐渐增大。就像开车时，如果一直偏左，就持续向右修正。
- **D项**：误差变化越快，输出越大。就像开车时，如果快速偏离，提前大幅修正。

### 6.2 位置式PID vs 增量式PID

**位置式PID**（本项目使用）

```
u(k) = Kp×e(k) + Ki×Σe(i)×dt + Kd×(e(k)-e(k-1))/dt

优点：直接输出控制量（角度），直观
缺点：积分项需要累加历史误差，存在积分饱和风险
适用：舵机角度控制（输出是绝对位置）
```

**增量式PID**

```
Δu(k) = Kp×(e(k)-e(k-1)) + Ki×e(k)×dt + Kd×(e(k)-2e(k-1)+e(k-2))/dt
u(k) = u(k-1) + Δu(k)

优点：无积分饱和问题，上电时输出从当前值开始
缺点：需要记录更多历史值
适用：电机速度控制（输出是增量）
```

### 6.3 抗积分饱和

当系统长时间存在误差（如云台被外力阻挡），积分项会无限增大，导致积分饱和。一旦误差消除，积分项需要很长时间才能减小，造成超调。

```c
/* 方法1：积分限幅（简单有效） */
pid->integral += error * dt;
if (pid->integral >  pid->integral_limit) pid->integral =  pid->integral_limit;
if (pid->integral < -pid->integral_limit) pid->integral = -pid->integral_limit;

/* 方法2：条件积分（输出饱和时停止积分） */
float output_before_limit = Kp*e + Ki*integral + Kd*derivative;
if (output_before_limit < output_max && output_before_limit > output_min) {
    integral += error * dt;  /* 只有输出未饱和时才积分 */
}

/* 方法3：反向积分（输出饱和时反向积分，快速退出饱和） */
if ((output >= output_max && error > 0) ||
    (output <= output_min && error < 0)) {
    /* 不积分 */
} else {
    integral += error * dt;
}
```

### 6.4 微分滤波

纯微分项对噪声极其敏感，传感器噪声会被微分放大，导致输出剧烈抖动。解决方法是对微分项加低通滤波：

```c
/* 一阶低通滤波微分项 */
/* 截止频率 fc = 1/(2π×τ)，τ为滤波时间常数 */
/* 典型值：τ = 5×dt ~ 20×dt */

#define DERIV_FILTER_TAU  0.05f  /* 时间常数50ms，截止频率约3.2Hz */

float raw_derivative = (error - pid->last_error) / dt;
/* 一阶低通：y = y_prev + (x - y_prev) × (dt / (τ + dt)) */
pid->filtered_derivative = pid->filtered_derivative +
    (raw_derivative - pid->filtered_derivative) *
    (dt / (DERIV_FILTER_TAU + dt));

float d_term = pid->kd * pid->filtered_derivative;
```

### 6.5 双轴独立PID完整代码

```c
/* pid.h */
#ifndef PID_H
#define PID_H

#include <stdint.h>

typedef struct {
    /* PID参数 */
    float kp;
    float ki;
    float kd;

    /* 状态变量 */
    float integral;             /* 积分累积值 */
    float last_error;           /* 上次误差（用于微分） */
    float filtered_derivative;  /* 滤波后的微分项 */

    /* 限幅参数 */
    float output_limit;    /* 输出限幅（±output_limit） */
    float integral_limit;  /* 积分限幅 */

    /* 微分滤波时间常数 */
    float deriv_tau;

    /* 统计信息（调试用） */
    float last_output;
    float last_p_term;
    float last_i_term;
    float last_d_term;
} PID_Controller;

void pid_init(PID_Controller *pid, float kp, float ki, float kd,
              float output_limit, float integral_limit, float deriv_tau);
float pid_compute(PID_Controller *pid, float setpoint,
                  float measured, float dt);
void pid_reset(PID_Controller *pid);
void pid_set_params(PID_Controller *pid, float kp, float ki, float kd);

#endif /* PID_H */
```

```c
/* pid.c */
#include "pid.h"
#include <string.h>

/**
 * @brief  初始化PID控制器
 * @param  kp, ki, kd      PID参数
 * @param  output_limit    输出限幅（角度，单位：度）
 * @param  integral_limit  积分限幅
 * @param  deriv_tau       微分滤波时间常数（秒），0表示不滤波
 */
void pid_init(PID_Controller *pid, float kp, float ki, float kd,
              float output_limit, float integral_limit, float deriv_tau)
{
    memset(pid, 0, sizeof(PID_Controller));
    pid->kp             = kp;
    pid->ki             = ki;
    pid->kd             = kd;
    pid->output_limit   = output_limit;
    pid->integral_limit = integral_limit;
    pid->deriv_tau      = deriv_tau;
}

/**
 * @brief  计算PID输出
 * @param  setpoint  目标值（角度）
 * @param  measured  测量值（角度）
 * @param  dt        采样时间（秒）
 * @retval PID输出值（角度）
 */
float pid_compute(PID_Controller *pid, float setpoint,
                  float measured, float dt)
{
    float error = setpoint - measured;

    /* P项 */
    float p_term = pid->kp * error;

    /* I项（带条件积分抗饱和） */
    float output_preview = p_term + pid->ki * pid->integral;
    if ((output_preview < pid->output_limit && output_preview > -pid->output_limit) ||
        (output_preview >= pid->output_limit && error < 0) ||
        (output_preview <= -pid->output_limit && error > 0)) {
        pid->integral += error * dt;
    }
    /* 积分限幅 */
    if (pid->integral >  pid->integral_limit) pid->integral =  pid->integral_limit;
    if (pid->integral < -pid->integral_limit) pid->integral = -pid->integral_limit;
    float i_term = pid->ki * pid->integral;

    /* D项（带低通滤波） */
    float raw_deriv = (error - pid->last_error) / dt;
    if (pid->deriv_tau > 0.0f) {
        pid->filtered_derivative += (raw_deriv - pid->filtered_derivative) *
                                    (dt / (pid->deriv_tau + dt));
    } else {
        pid->filtered_derivative = raw_deriv;
    }
    float d_term = pid->kd * pid->filtered_derivative;
    pid->last_error = error;

    /* 求和并限幅 */
    float output = p_term + i_term + d_term;
    if (output >  pid->output_limit) output =  pid->output_limit;
    if (output < -pid->output_limit) output = -pid->output_limit;

    /* 保存调试信息 */
    pid->last_output = output;
    pid->last_p_term = p_term;
    pid->last_i_term = i_term;
    pid->last_d_term = d_term;

    return output;
}

/** @brief 重置PID状态（切换模式时调用） */
void pid_reset(PID_Controller *pid)
{
    pid->integral            = 0.0f;
    pid->last_error          = 0.0f;
    pid->filtered_derivative = 0.0f;
    pid->last_output         = 0.0f;
}

/** @brief 在线修改PID参数 */
void pid_set_params(PID_Controller *pid, float kp, float ki, float kd)
{
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
}
```

### 6.6 参数整定方法（Ziegler-Nichols法）

Ziegler-Nichols临界振荡法是一种经典的PID整定方法：

**步骤**

1. 将Ki=0，Kd=0，只保留P控制
2. 逐渐增大Kp，直到系统产生持续等幅振荡
3. 记录此时的临界增益 Ku 和振荡周期 Tu
4. 按照以下公式计算PID参数：

```
PID控制器（标准Ziegler-Nichols）：
  Kp = 0.6 × Ku
  Ki = 2 × Kp / Tu
  Kd = Kp × Tu / 8

对于云台（需要更平滑，减小超调）：
  Kp = 0.33 × Ku  （降低到1/3，减少超调）
  Ki = Kp / Tu
  Kd = Kp × Tu / 6
```

**云台典型参数范围**

```
稳定模式（低带宽，平滑优先）：
  Kp = 0.8 ~ 1.5
  Ki = 0.02 ~ 0.1
  Kd = 0.05 ~ 0.2
  output_limit = 45°
  integral_limit = 20°

追踪模式（高带宽，响应优先）：
  Kp = 1.5 ~ 3.0
  Ki = 0.05 ~ 0.2
  Kd = 0.1 ~ 0.5
  output_limit = 60°
  integral_limit = 30°
```

---

## 7. 稳定模式实现

### 7.1 完整稳定控制循环

稳定模式的目标是：无论载体如何运动，保持摄像头水平（Roll=0，Pitch=0）。

控制逻辑：
1. 读取IMU数据
2. 互补滤波计算当前姿态角
3. 以0°为目标，计算姿态误差
4. PID计算补偿角度
5. 将补偿角度输出到舵机

```c
/* stabilize.h */
#ifndef STABILIZE_H
#define STABILIZE_H

#include "attitude.h"
#include "pid.h"
#include "gimbal_pwm.h"

/* 稳定模式PID参数 */
#define STAB_KP           1.2f
#define STAB_KI           0.05f
#define STAB_KD           0.12f
#define STAB_OUTPUT_LIMIT 45.0f
#define STAB_INTEG_LIMIT  20.0f
#define STAB_DERIV_TAU    0.05f

/* 软启动参数：上电后逐渐增大输出，避免突然跳动 */
#define SOFT_START_STEPS  100   /* 100步 × 10ms = 1秒软启动 */

void stabilize_init(void);
void stabilize_task(void);  /* 在10ms定时器中断中调用 */

#endif /* STABILIZE_H */
```

```c
/* stabilize.c */
#include "stabilize.h"
#include "mpu6050.h"
#include <math.h>

/* 全局对象 */
static Attitude      g_attitude  = {0};
static PID_Controller g_pan_pid  = {0};
static PID_Controller g_tilt_pid = {0};
static MPU6050_Offset g_imu_offset = {0};

/* 软启动计数器 */
static uint16_t soft_start_counter = 0;

/* 外部声明（在main.c中定义） */
extern MPU6050_Offset g_calibration;

void stabilize_init(void)
{
    /* 初始化姿态 */
    attitude_init(&g_attitude);

    /* 初始化Pan轴PID */
    pid_init(&g_pan_pid,
             STAB_KP, STAB_KI, STAB_KD,
             STAB_OUTPUT_LIMIT, STAB_INTEG_LIMIT, STAB_DERIV_TAU);

    /* 初始化Tilt轴PID */
    pid_init(&g_tilt_pid,
             STAB_KP, STAB_KI, STAB_KD,
             STAB_OUTPUT_LIMIT, STAB_INTEG_LIMIT, STAB_DERIV_TAU);

    /* 复制校准数据 */
    g_imu_offset = g_calibration;

    /* 重置软启动计数器 */
    soft_start_counter = 0;
}

/**
 * @brief  稳定模式控制任务（每10ms调用一次）
 * @note   在TIM3定时器中断中调用，执行时间约200μs
 */
void stabilize_task(void)
{
    MPU6050_Data imu;
    const float dt = 0.01f;  /* 10ms */

    /* 1. 读取IMU数据 */
    if (mpu6050_read_calibrated(&imu, &g_imu_offset) != HAL_OK) {
        /* 读取失败：保持当前输出，不更新 */
        return;
    }

    /* 2. 互补滤波姿态解算 */
    complementary_filter(&g_attitude, &imu, dt);

    /* 3. 计算PID输出
     *    目标姿态：Roll=0°，Pitch=0°（水平）
     *    误差 = 目标 - 当前 = 0 - 当前姿态角
     *    注意：补偿方向与姿态角方向相反
     */
    float pan_output  = pid_compute(&g_pan_pid,  0.0f, g_attitude.pitch, dt);
    float tilt_output = pid_compute(&g_tilt_pid, 0.0f, g_attitude.roll,  dt);

    /* 4. 软启动：逐渐增大输出比例 */
    float scale = 1.0f;
    if (soft_start_counter < SOFT_START_STEPS) {
        scale = (float)soft_start_counter / (float)SOFT_START_STEPS;
        soft_start_counter++;
    }
    pan_output  *= scale;
    tilt_output *= scale;

    /* 5. 输出到舵机 */
    gimbal_set_angle(GIMBAL_CH_PAN,  pan_output);
    gimbal_set_angle(GIMBAL_CH_TILT, tilt_output);
}
```

### 7.2 10ms定时器中断配置

```c
/* 使用TIM3产生10ms定时中断 */
TIM_HandleTypeDef htim3;

void tim3_init(void)
{
    __HAL_RCC_TIM3_CLK_ENABLE();

    /* 72MHz / 7200 = 10kHz，计数100次 = 10ms */
    htim3.Instance               = TIM3;
    htim3.Init.Prescaler         = 7200 - 1;
    htim3.Init.Period            = 100 - 1;
    htim3.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim3.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim3);

    /* 配置NVIC，优先级高于普通任务 */
    HAL_NVIC_SetPriority(TIM3_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM3_IRQn);

    HAL_TIM_Base_Start_IT(&htim3);
}

/* TIM3中断处理函数（在stm32f1xx_it.c中） */
void TIM3_IRQHandler(void)
{
    HAL_TIM_IRQHandler(&htim3);
}

/* HAL回调（在main.c或gimbal_control.c中） */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance != TIM3) return;

    /* 根据当前模式执行对应任务 */
    extern volatile uint8_t g_gimbal_mode;
    if (g_gimbal_mode == 0) {
        stabilize_task();
    } else {
        track_task();
    }
}
```

---

## 8. 视觉追踪模式

### 8.1 OpenMV通信协议设计

OpenMV通过UART向STM32发送目标坐标。协议设计原则：
- 帧格式简单，便于解析
- 包含帧头帧尾，便于同步
- 包含校验，防止数据错误

**帧格式定义**

```
字节序号:  0     1     2     3     4     5
内容:    0xAA  XH    XL    YH    YL   0x55

其中：
  0xAA：帧头
  XH/XL：X坐标高低字节（int16，范围-1000~+1000，对应-1.0~+1.0）
  YH/YL：Y坐标高低字节（int16，范围-1000~+1000，对应-1.0~+1.0）
  0x55：帧尾

坐标定义：
  X: -1000（画面最左）~ +1000（画面最右），0为中心
  Y: -1000（画面最下）~ +1000（画面最上），0为中心

目标丢失时发送：0xAA 0x7F 0xFF 0x7F 0xFF 0x55
  （X=0x7FFF=32767，超出正常范围，作为"无目标"标志）
```

**OpenMV端Python代码**

```python
# OpenMV H7 目标追踪脚本
import sensor, image, time, struct
from pyb import UART

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)  # 320x240
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# 初始化UART（波特率115200）
uart = UART(3, 115200)

# 追踪目标颜色阈值（红色，LAB色彩空间）
# 格式：(L_min, L_max, A_min, A_max, B_min, B_max)
RED_THRESHOLD = (30, 100, 15, 127, 15, 127)

clock = time.clock()
IMG_W = 320
IMG_H = 240

while True:
    clock.tick()
    img = sensor.snapshot()

    # 查找最大色块
    blobs = img.find_blobs([RED_THRESHOLD], pixels_threshold=200,
                            area_threshold=200, merge=True)

    if blobs:
        # 取面积最大的色块
        largest = max(blobs, key=lambda b: b.pixels())

        # 计算偏差（相对于画面中心，归一化到-1000~+1000）
        cx = largest.cx()
        cy = largest.cy()
        x_err = int((cx - IMG_W // 2) / (IMG_W // 2) * 1000)
        y_err = int((IMG_H // 2 - cy) / (IMG_H // 2) * 1000)  # Y轴翻转

        # 限幅
        x_err = max(-1000, min(1000, x_err))
        y_err = max(-1000, min(1000, y_err))

        # 发送帧（大端序）
        frame = struct.pack('>BhhB', 0xAA, x_err, y_err, 0x55)
        uart.write(frame)

        # 调试显示
        img.draw_cross(cx, cy, color=(255, 0, 0))
        img.draw_rectangle(largest.rect(), color=(255, 0, 0))
    else:
        # 目标丢失：发送特殊值
        frame = struct.pack('>BhhB', 0xAA, 32767, 32767, 0x55)
        uart.write(frame)
```

### 8.2 STM32 UART DMA接收

使用DMA接收避免CPU轮询，提高效率：

```c
/* vision.h */
#ifndef VISION_H
#define VISION_H

#include "stm32f1xx_hal.h"

#define VISION_FRAME_LEN    6      /* 帧长度：6字节 */
#define VISION_FRAME_HEAD   0xAA
#define VISION_FRAME_TAIL   0x55
#define VISION_NO_TARGET    32767  /* 目标丢失标志值 */
#define VISION_TIMEOUT_MS   200    /* 超时时间：200ms无数据视为目标丢失 */

typedef struct {
    float x;          /* 归一化X坐标，-1.0~+1.0 */
    float y;          /* 归一化Y坐标，-1.0~+1.0 */
    uint8_t valid;    /* 1=目标有效，0=目标丢失 */
    uint32_t last_update_tick;  /* 最后更新时间（HAL_GetTick） */
} VisionTarget;

void vision_init(void);
void vision_uart_callback(void);  /* 在UART接收完成回调中调用 */
const VisionTarget* vision_get_target(void);
uint8_t vision_is_target_valid(void);

#endif /* VISION_H */
```

```c
/* vision.c */
#include "vision.h"
#include <string.h>

extern UART_HandleTypeDef huart1;

/* DMA接收缓冲区（双缓冲，防止数据覆盖） */
static uint8_t rx_buf[VISION_FRAME_LEN * 2];
static VisionTarget g_target = {0};

void vision_init(void)
{
    memset(&g_target, 0, sizeof(g_target));

    /* 启动DMA循环接收，每次接收6字节 */
    HAL_UART_Receive_DMA(&huart1, rx_buf, VISION_FRAME_LEN);
}

/**
 * @brief  解析视觉帧（在HAL_UART_RxCpltCallback中调用）
 */
void vision_uart_callback(void)
{
    uint8_t *buf = rx_buf;

    /* 验证帧头帧尾 */
    if (buf[0] != VISION_FRAME_HEAD || buf[5] != VISION_FRAME_TAIL) {
        /* 帧错误：重新启动接收 */
        HAL_UART_Receive_DMA(&huart1, rx_buf, VISION_FRAME_LEN);
        return;
    }

    /* 解析坐标（大端序有符号16位整数） */
    int16_t raw_x = (int16_t)((buf[1] << 8) | buf[2]);
    int16_t raw_y = (int16_t)((buf[3] << 8) | buf[4]);

    /* 检查是否为"目标丢失"标志 */
    if (raw_x == VISION_NO_TARGET || raw_y == VISION_NO_TARGET) {
        g_target.valid = 0;
    } else {
        g_target.x     = (float)raw_x / 1000.0f;
        g_target.y     = (float)raw_y / 1000.0f;
        g_target.valid = 1;
    }
    g_target.last_update_tick = HAL_GetTick();

    /* 重新启动DMA接收 */
    HAL_UART_Receive_DMA(&huart1, rx_buf, VISION_FRAME_LEN);
}

const VisionTarget* vision_get_target(void)
{
    return &g_target;
}

/**
 * @brief  检查目标是否有效（有效且未超时）
 */
uint8_t vision_is_target_valid(void)
{
    if (!g_target.valid) return 0;
    /* 超时检查 */
    if (HAL_GetTick() - g_target.last_update_tick > VISION_TIMEOUT_MS) {
        g_target.valid = 0;
        return 0;
    }
    return 1;
}

/* UART接收完成回调（在stm32f1xx_it.c或main.c中） */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        vision_uart_callback();
    }
}
```

### 8.3 追踪PID控制

```c
/* track.h */
#ifndef TRACK_H
#define TRACK_H

#include "pid.h"
#include "vision.h"
#include "gimbal_pwm.h"

/* 追踪模式PID参数（比稳定模式更激进） */
#define TRACK_KP           2.0f
#define TRACK_KI           0.1f
#define TRACK_KD           0.2f
#define TRACK_OUTPUT_LIMIT 60.0f
#define TRACK_INTEG_LIMIT  30.0f
#define TRACK_DERIV_TAU    0.03f

void track_init(void);
void track_task(void);

#endif /* TRACK_H */
```

```c
/* track.c */
#include "track.h"

static PID_Controller g_track_pan_pid  = {0};
static PID_Controller g_track_tilt_pid = {0};

/* 目标丢失时的保持计数器 */
static uint16_t lost_counter = 0;
#define LOST_HOLD_STEPS  50  /* 目标丢失后保持50步（500ms）再回中 */

void track_init(void)
{
    pid_init(&g_track_pan_pid,
             TRACK_KP, TRACK_KI, TRACK_KD,
             TRACK_OUTPUT_LIMIT, TRACK_INTEG_LIMIT, TRACK_DERIV_TAU);

    pid_init(&g_track_tilt_pid,
             TRACK_KP, TRACK_KI, TRACK_KD,
             TRACK_OUTPUT_LIMIT, TRACK_INTEG_LIMIT, TRACK_DERIV_TAU);

    lost_counter = 0;
}

/**
 * @brief  追踪模式控制任务（每10ms调用一次）
 * @note   目标坐标为画面中心偏差（-1.0~+1.0）
 *         PID目标值为0（目标在画面中心）
 *         PID输出为云台需要转动的角度
 */
void track_task(void)
{
    const float dt = 0.01f;

    if (vision_is_target_valid()) {
        const VisionTarget *target = vision_get_target();
        lost_counter = 0;

        /* 追踪PID：误差 = 0 - 目标偏差
         * 目标在画面右侧（x>0）→ 云台向右转（pan增大）
         * 目标在画面上方（y>0）→ 云台向上转（tilt增大）
         */
        float pan_output  = pid_compute(&g_track_pan_pid,
                                        0.0f, -target->x, dt);
        float tilt_output = pid_compute(&g_track_tilt_pid,
                                        0.0f, -target->y, dt);

        /* 叠加当前位置（追踪是相对运动） */
        float new_pan  = gimbal_get_angle(GIMBAL_CH_PAN)  + pan_output  * dt * 10.0f;
        float new_tilt = gimbal_get_angle(GIMBAL_CH_TILT) + tilt_output * dt * 10.0f;

        gimbal_set_angle(GIMBAL_CH_PAN,  new_pan);
        gimbal_set_angle(GIMBAL_CH_TILT, new_tilt);

    } else {
        /* 目标丢失处理 */
        lost_counter++;
        pid_reset(&g_track_pan_pid);
        pid_reset(&g_track_tilt_pid);

        if (lost_counter > LOST_HOLD_STEPS) {
            /* 超过保持时间，缓慢回中 */
            float pan_now  = gimbal_get_angle(GIMBAL_CH_PAN);
            float tilt_now = gimbal_get_angle(GIMBAL_CH_TILT);
            gimbal_set_angle(GIMBAL_CH_PAN,  pan_now  * 0.95f);
            gimbal_set_angle(GIMBAL_CH_TILT, tilt_now * 0.95f);
        }
    }
}
```

---

## 9. 模式切换与状态机

### 9.1 系统状态机设计

```
                    系统状态机
                    =========

              上电/复位
                  │
                  ▼
           ┌─────────────┐
           │   INIT      │  初始化所有外设
           │  初始化状态  │  MPU6050校准（5秒）
           └──────┬──────┘
                  │ 初始化完成
                  ▼
           ┌─────────────┐
     ┌────►│  STABILIZE  │◄────┐
     │     │  稳定模式    │     │
     │     └──────┬──────┘     │
     │            │ 按键按下    │
     │            ▼            │
     │     ┌─────────────┐     │
     │     │  SWITCHING  │     │
     │     │  切换过渡    │     │
     │     └──────┬──────┘     │
     │            │ 过渡完成    │
     │            ▼            │
     │     ┌─────────────┐     │
     └─────│   TRACK     │─────┘
           │  追踪模式    │  按键按下
           └─────────────┘

状态说明：
  INIT：上电初始化，LED快速闪烁（100ms）
  STABILIZE：稳定模式，红色LED常亮
  SWITCHING：模式切换过渡（500ms），两个LED交替闪烁
  TRACK：追踪模式，绿色LED常亮
```

### 9.2 完整状态机代码

```c
/* gimbal_fsm.h */
#ifndef GIMBAL_FSM_H
#define GIMBAL_FSM_H

#include "stm32f1xx_hal.h"

/* 系统状态枚举 */
typedef enum {
    GIMBAL_STATE_INIT       = 0,  /* 初始化 */
    GIMBAL_STATE_STABILIZE  = 1,  /* 稳定模式 */
    GIMBAL_STATE_SWITCHING  = 2,  /* 模式切换过渡 */
    GIMBAL_STATE_TRACK      = 3,  /* 追踪模式 */
    GIMBAL_STATE_ERROR      = 4,  /* 错误状态 */
} GimbalState;

/* LED引脚定义 */
#define LED_RED_PORT    GPIOC
#define LED_RED_PIN     GPIO_PIN_13
#define LED_GREEN_PORT  GPIOB
#define LED_GREEN_PIN   GPIO_PIN_12

/* 按键引脚定义 */
#define BTN_PORT        GPIOA
#define BTN_PIN         GPIO_PIN_8

/* 消抖时间（毫秒） */
#define BTN_DEBOUNCE_MS  20

void gimbal_fsm_init(void);
void gimbal_fsm_update(void);  /* 在主循环中调用 */
GimbalState gimbal_fsm_get_state(void);

/* 供定时器中断查询当前模式 */
extern volatile GimbalState g_gimbal_state;

#endif /* GIMBAL_FSM_H */
```

```c
/* gimbal_fsm.c */
#include "gimbal_fsm.h"
#include "stabilize.h"
#include "track.h"
#include "gimbal_pwm.h"

volatile GimbalState g_gimbal_state = GIMBAL_STATE_INIT;

/* 按键状态 */
static uint8_t  btn_last_state    = 1;  /* 1=未按，0=按下（内部上拉） */
static uint32_t btn_press_tick    = 0;
static uint8_t  btn_debounced     = 0;

/* 切换过渡计时器 */
static uint32_t switch_start_tick = 0;
#define SWITCH_DURATION_MS  500

/* LED闪烁计时器 */
static uint32_t led_tick = 0;

/* 内部函数 */
static void led_set(uint8_t red, uint8_t green);
static void led_update(void);
static uint8_t btn_read_debounced(void);

void gimbal_fsm_init(void)
{
    /* 初始化LED GPIO */
    GPIO_InitTypeDef gpio = {0};
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    gpio.Pin   = LED_RED_PIN;
    gpio.Mode  = GPIO_MODE_OUTPUT_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_RED_PORT, &gpio);

    gpio.Pin = LED_GREEN_PIN;
    HAL_GPIO_Init(LED_GREEN_PORT, &gpio);

    /* 初始化按键GPIO（内部上拉输入） */
    gpio.Pin  = BTN_PIN;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(BTN_PORT, &gpio);

    g_gimbal_state = GIMBAL_STATE_INIT;
}

/**
 * @brief  状态机更新（在主循环中调用，约每10ms一次）
 */
void gimbal_fsm_update(void)
{
    uint8_t btn_pressed = btn_read_debounced();

    switch (g_gimbal_state) {

        case GIMBAL_STATE_INIT:
            /* 初始化完成后进入稳定模式 */
            /* （初始化在main中完成，完成后调用此函数前已切换状态） */
            break;

        case GIMBAL_STATE_STABILIZE:
            /* 检测按键，切换到追踪模式 */
            if (btn_pressed) {
                g_gimbal_state    = GIMBAL_STATE_SWITCHING;
                switch_start_tick = HAL_GetTick();
                /* 重置追踪PID */
                track_init();
                /* 云台回中，准备追踪 */
                gimbal_center();
            }
            break;

        case GIMBAL_STATE_SWITCHING:
            /* 等待过渡时间 */
            if (HAL_GetTick() - switch_start_tick >= SWITCH_DURATION_MS) {
                /* 根据上一个状态决定切换到哪个模式 */
                /* 简化：SWITCHING后总是进入TRACK */
                g_gimbal_state = GIMBAL_STATE_TRACK;
            }
            break;

        case GIMBAL_STATE_TRACK:
            /* 检测按键，切换回稳定模式 */
            if (btn_pressed) {
                g_gimbal_state    = GIMBAL_STATE_SWITCHING;
                switch_start_tick = HAL_GetTick();
                /* 重置稳定PID */
                stabilize_init();
                /* 云台回中 */
                gimbal_center();
                /* 标记：过渡后进入稳定模式 */
                /* 使用负数trick：用SWITCHING+1表示切换到稳定 */
                /* 实际实现中可用额外标志位 */
                g_gimbal_state = GIMBAL_STATE_STABILIZE;
            }
            break;

        case GIMBAL_STATE_ERROR:
            /* 错误状态：LED快速闪烁，等待复位 */
            break;

        default:
            g_gimbal_state = GIMBAL_STATE_ERROR;
            break;
    }

    /* 更新LED指示 */
    led_update();
}

/**
 * @brief  带消抖的按键读取
 * @retval 1=检测到一次按键事件，0=无事件
 */
static uint8_t btn_read_debounced(void)
{
    uint8_t current = HAL_GPIO_ReadPin(BTN_PORT, BTN_PIN);

    if (current == 0 && btn_last_state == 1) {
        /* 检测到下降沿，记录时间 */
        btn_press_tick = HAL_GetTick();
        btn_debounced  = 0;
    }

    if (current == 0 && !btn_debounced) {
        if (HAL_GetTick() - btn_press_tick >= BTN_DEBOUNCE_MS) {
            btn_debounced = 1;
            btn_last_state = current;
            return 1;  /* 确认按键事件 */
        }
    }

    btn_last_state = current;
    return 0;
}

/** @brief 设置LED状态（1=亮，0=灭） */
static void led_set(uint8_t red, uint8_t green)
{
    /* STM32F103C8T6板载LED低电平亮 */
    HAL_GPIO_WritePin(LED_RED_PORT,   LED_RED_PIN,
                      red   ? GPIO_PIN_RESET : GPIO_PIN_SET);
    HAL_GPIO_WritePin(LED_GREEN_PORT, LED_GREEN_PIN,
                      green ? GPIO_PIN_RESET : GPIO_PIN_SET);
}

/** @brief 根据状态更新LED */
static void led_update(void)
{
    uint32_t now = HAL_GetTick();

    switch (g_gimbal_state) {
        case GIMBAL_STATE_INIT:
            /* 快速闪烁（100ms） */
            if ((now / 100) % 2) led_set(1, 1);
            else                 led_set(0, 0);
            break;

        case GIMBAL_STATE_STABILIZE:
            led_set(1, 0);  /* 红灯常亮 */
            break;

        case GIMBAL_STATE_SWITCHING:
            /* 交替闪烁（250ms） */
            if ((now / 250) % 2) led_set(1, 0);
            else                 led_set(0, 1);
            break;

        case GIMBAL_STATE_TRACK:
            led_set(0, 1);  /* 绿灯常亮 */
            break;

        case GIMBAL_STATE_ERROR:
            /* 红灯快速闪烁（50ms） */
            if ((now / 50) % 2) led_set(1, 0);
            else                led_set(0, 0);
            break;
    }
}

GimbalState gimbal_fsm_get_state(void)
{
    return g_gimbal_state;
}
```

---

## 10. 系统集成与主程序

### 10.1 FreeRTOS任务划分

虽然本项目可以用裸机（bare-metal）实现，但使用FreeRTOS可以更清晰地组织代码，便于扩展。

**任务划分**

| 任务名 | 优先级 | 周期 | 功能 |
|--------|--------|------|------|
| AttitudeTask | 最高(4) | 10ms | IMU读取 + 姿态解算 |
| ControlTask | 高(3) | 10ms | PID计算 + 舵机输出 |
| VisionTask | 中(2) | 33ms | 视觉数据解析 |
| CommTask | 低(1) | 100ms | 串口调试输出 |
| IdleTask | 最低(0) | - | 系统空闲 |

**任务通信**

```
AttitudeTask ──(队列)──► ControlTask
VisionTask   ──(队列)──► ControlTask
CommTask     ◄─(队列)─── ControlTask（调试数据）
```

### 10.2 完整main.c

```c
/* main.c - 智能云台主程序 */
#include "main.h"
#include "stm32f1xx_hal.h"
#include "gimbal_pwm.h"
#include "mpu6050.h"
#include "attitude.h"
#include "pid.h"
#include "stabilize.h"
#include "track.h"
#include "vision.h"
#include "gimbal_fsm.h"
#include <stdio.h>
#include <string.h>

/* ============================================================
 * 全局变量
 * ============================================================ */

/* 外设句柄 */
UART_HandleTypeDef huart1;  /* 视觉模块UART */
UART_HandleTypeDef huart2;  /* 调试串口 */
I2C_HandleTypeDef  hi2c1;   /* MPU6050 I2C */
TIM_HandleTypeDef  htim2;   /* PWM输出 */
TIM_HandleTypeDef  htim3;   /* 控制定时器 */

/* 校准数据（全局，供各模块使用） */
MPU6050_Offset g_calibration = {0};

/* 调试输出缓冲区 */
static char debug_buf[128];

/* ============================================================
 * 函数声明
 * ============================================================ */
static void SystemClock_Config(void);
static void uart1_init(void);
static void uart2_init(void);
static void i2c1_init(void);
static void debug_print(const char *fmt, ...);

/* ============================================================
 * 主函数
 * ============================================================ */
int main(void)
{
    /* 1. HAL初始化 */
    HAL_Init();
    SystemClock_Config();

    /* 2. 外设初始化 */
    i2c1_init();
    uart1_init();   /* 视觉模块 */
    uart2_init();   /* 调试串口 */

    /* 3. 云台PWM初始化 */
    gimbal_pwm_init();
    gimbal_center();  /* 上电回中 */
    HAL_Delay(500);   /* 等待舵机到位 */

    /* 4. 状态机初始化（LED、按键） */
    gimbal_fsm_init();
    g_gimbal_state = GIMBAL_STATE_INIT;

    /* 5. MPU6050初始化 */
    debug_print("Initializing MPU6050...\r\n");
    if (mpu6050_init() != HAL_OK) {
        debug_print("MPU6050 init FAILED!\r\n");
        g_gimbal_state = GIMBAL_STATE_ERROR;
        while (1) {
            gimbal_fsm_update();
            HAL_Delay(50);
        }
    }
    debug_print("MPU6050 OK\r\n");

    /* 6. IMU零偏校准（保持静止5秒） */
    debug_print("Calibrating IMU (keep still for 5s)...\r\n");
    mpu6050_calibrate(&g_calibration, 500);
    debug_print("Calibration done: gx=%.3f gy=%.3f gz=%.3f\r\n",
                g_calibration.gx_offset,
                g_calibration.gy_offset,
                g_calibration.gz_offset);

    /* 7. 初始化稳定模式 */
    stabilize_init();

    /* 8. 初始化视觉接收 */
    vision_init();

    /* 9. 启动控制定时器（10ms中断） */
    tim3_init();

    /* 10. 进入稳定模式 */
    g_gimbal_state = GIMBAL_STATE_STABILIZE;
    debug_print("System ready! Mode: STABILIZE\r\n");

    /* ============================================================
     * 主循环（低优先级任务）
     * ============================================================ */
    uint32_t last_debug_tick = 0;

    while (1) {
        /* 状态机更新（按键检测、LED更新） */
        gimbal_fsm_update();

        /* 每500ms输出一次调试信息 */
        if (HAL_GetTick() - last_debug_tick >= 500) {
            last_debug_tick = HAL_GetTick();

            /* 输出当前状态 */
            const char *mode_str = (g_gimbal_state == GIMBAL_STATE_STABILIZE)
                                   ? "STAB" : "TRACK";
            debug_print("[%s] Pan=%.1f Tilt=%.1f\r\n",
                        mode_str,
                        gimbal_get_angle(GIMBAL_CH_PAN),
                        gimbal_get_angle(GIMBAL_CH_TILT));
        }

        HAL_Delay(10);
    }
}

/* ============================================================
 * 外设初始化函数
 * ============================================================ */

static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};

    /* 使能HSE（外部8MHz晶振），PLL倍频到72MHz */
    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    osc.HSEState       = RCC_HSE_ON;
    osc.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    osc.PLL.PLLState   = RCC_PLL_ON;
    osc.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLMUL     = RCC_PLL_MUL9;  /* 8MHz × 9 = 72MHz */
    HAL_RCC_OscConfig(&osc);

    clk.ClockType      = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                         RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider  = RCC_SYSCLK_DIV1;   /* HCLK = 72MHz */
    clk.APB1CLKDivider = RCC_HCLK_DIV2;     /* APB1 = 36MHz */
    clk.APB2CLKDivider = RCC_HCLK_DIV1;     /* APB2 = 72MHz */
    HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_2);
}

static void uart1_init(void)
{
    /* USART1：PA9(TX)，PA10(RX)，115200，8N1 */
    __HAL_RCC_USART1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin   = GPIO_PIN_9;
    gpio.Mode  = GPIO_MODE_AF_PP;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &gpio);

    gpio.Pin  = GPIO_PIN_10;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio);

    huart1.Instance          = USART1;
    huart1.Init.BaudRate     = 115200;
    huart1.Init.WordLength   = UART_WORDLENGTH_8B;
    huart1.Init.StopBits     = UART_STOPBITS_1;
    huart1.Init.Parity       = UART_PARITY_NONE;
    huart1.Init.Mode         = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl    = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart1);

    /* 使能USART1中断 */
    HAL_NVIC_SetPriority(USART1_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
}

static void uart2_init(void)
{
    /* USART2：PA2(TX)，PA3(RX)，115200，调试用 */
    __HAL_RCC_USART2_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin   = GPIO_PIN_2;
    gpio.Mode  = GPIO_MODE_AF_PP;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &gpio);

    gpio.Pin  = GPIO_PIN_3;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio);

    huart2.Instance          = USART2;
    huart2.Init.BaudRate     = 115200;
    huart2.Init.WordLength   = UART_WORDLENGTH_8B;
    huart2.Init.StopBits     = UART_STOPBITS_1;
    huart2.Init.Parity       = UART_PARITY_NONE;
    huart2.Init.Mode         = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl    = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart2);
}

static void i2c1_init(void)
{
    __HAL_RCC_I2C1_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* PB6=SCL，PB7=SDA，开漏输出 */
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin   = GPIO_PIN_6 | GPIO_PIN_7;
    gpio.Mode  = GPIO_MODE_AF_OD;  /* 复用开漏（I2C要求） */
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOB, &gpio);

    hi2c1.Instance             = I2C1;
    hi2c1.Init.ClockSpeed      = 400000;
    hi2c1.Init.DutyCycle       = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1     = 0;
    hi2c1.Init.AddressingMode  = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode   = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}

/* 调试串口输出（重定向printf到USART2） */
static void debug_print(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    int len = vsnprintf(debug_buf, sizeof(debug_buf), fmt, args);
    va_end(args);
    HAL_UART_Transmit(&huart2, (uint8_t*)debug_buf, len, 100);
}

/* 重定向fputc到USART2（可选，用于printf） */
int fputc(int ch, FILE *f)
{
    HAL_UART_Transmit(&huart2, (uint8_t*)&ch, 1, 10);
    return ch;
}
```

---

## 11. 调试与测试

### 11.1 串口调试输出

调试时通过USART2输出关键数据，使用串口助手（如SSCOM、MobaXterm）查看：

```c
/* 调试数据输出格式（每100ms输出一次） */
void debug_output_task(void)
{
    static uint32_t last_tick = 0;
    if (HAL_GetTick() - last_tick < 100) return;
    last_tick = HAL_GetTick();

    /* 输出格式：时间戳,Roll,Pitch,Pan角度,Tilt角度,Pan_P,Pan_I,Pan_D */
    printf("%lu,%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f\r\n",
           HAL_GetTick(),
           g_attitude.roll,
           g_attitude.pitch,
           gimbal_get_angle(GIMBAL_CH_PAN),
           gimbal_get_angle(GIMBAL_CH_TILT),
           g_pan_pid.last_p_term,
           g_pan_pid.last_i_term,
           g_pan_pid.last_d_term);
}
```

**使用Python绘制实时曲线**

```python
# plot_gimbal.py - 实时绘制云台调试数据
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

PORT = 'COM3'  # 根据实际端口修改
BAUD = 115200
MAX_POINTS = 200

ser = serial.Serial(PORT, BAUD, timeout=0.1)
times  = deque(maxlen=MAX_POINTS)
rolls  = deque(maxlen=MAX_POINTS)
pitchs = deque(maxlen=MAX_POINTS)
pans   = deque(maxlen=MAX_POINTS)
tilts  = deque(maxlen=MAX_POINTS)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

def update(frame):
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if not line: return
    try:
        parts = line.split(',')
        if len(parts) >= 5:
            times.append(int(parts[0]) / 1000.0)
            rolls.append(float(parts[1]))
            pitchs.append(float(parts[2]))
            pans.append(float(parts[3]))
            tilts.append(float(parts[4]))
    except: return

    ax1.clear()
    ax1.plot(list(times), list(rolls),  label='Roll')
    ax1.plot(list(times), list(pitchs), label='Pitch')
    ax1.set_ylabel('Attitude (deg)')
    ax1.legend()
    ax1.grid(True)

    ax2.clear()
    ax2.plot(list(times), list(pans),  label='Pan')
    ax2.plot(list(times), list(tilts), label='Tilt')
    ax2.set_ylabel('Servo Angle (deg)')
    ax2.set_xlabel('Time (s)')
    ax2.legend()
    ax2.grid(True)

ani = animation.FuncAnimation(fig, update, interval=50)
plt.tight_layout()
plt.show()
```

### 11.2 PID参数调整步骤

**步骤1：确认传感器正常**

```
串口输出应看到：
  Roll和Pitch在静止时接近0°
  手动倾斜时角度变化方向正确
  无明显噪声（抖动 < ±0.5°）
```

**步骤2：调整Kp（比例增益）**

```
初始：Kp=0.5, Ki=0, Kd=0
观察：手动倾斜云台，松手后是否能回到水平
  - 回不去：增大Kp
  - 振荡：减小Kp
目标：Kp约为临界振荡值的60%
```

**步骤3：调整Kd（微分增益）**

```
在Kp基础上加入Kd
  - 从Kd=0.05开始，逐步增大
  - 观察响应速度和超调量
  - Kd过大会引起高频抖动（噪声放大）
目标：响应快速，无明显超调
```

**步骤4：调整Ki（积分增益）**

```
最后加入Ki消除稳态误差
  - 从Ki=0.01开始，逐步增大
  - 观察稳态误差是否消除
  - Ki过大会引起低频振荡（积分饱和）
目标：稳态误差 < 0.5°
```

### 11.3 常见问题排查

**问题1：云台持续振荡**

```
现象：舵机来回抖动，无法稳定
原因分析：
  1. Kp过大 → 减小Kp到原来的70%
  2. Kd过大 → 减小Kd，或增大微分滤波时间常数
  3. 控制频率太低 → 检查定时器配置，确保100Hz
  4. 传感器噪声大 → 增大DLPF截止频率（减小DLPF_CFG值）
  5. 机械共振 → 检查云台支架是否松动

排查步骤：
  1. 将Ki=0，Kd=0，只用P控制
  2. 从Kp=0.3开始，逐步增大
  3. 找到临界振荡点，取60%作为工作Kp
```

**问题2：姿态角漂移**

```
现象：静止时Roll/Pitch角度缓慢漂移
原因分析：
  1. 陀螺仪零偏未校准 → 重新校准（确保静止5秒）
  2. 互补滤波α值过大 → 减小α（如从0.98改为0.95）
  3. 温度变化导致零偏变化 → 加入温度补偿
  4. 采样率不稳定 → 检查定时器中断是否被其他中断抢占

验证方法：
  将云台固定在水平面，观察30秒内漂移量
  正常：< 2°/分钟
  异常：> 5°/分钟，需要重新校准
```

**问题3：响应速度慢**

```
现象：手动倾斜后，云台需要很长时间才能回到水平
原因分析：
  1. Kp太小 → 增大Kp
  2. 积分限幅太小 → 增大integral_limit
  3. 输出限幅太小 → 增大output_limit
  4. 舵机速度不足 → 检查舵机电源电压（应为5V）

测试方法：
  快速倾斜45°，测量回到水平（误差<2°）所需时间
  目标：< 500ms
```

**问题4：视觉追踪抖动**

```
现象：目标静止时，云台仍然来回抖动
原因分析：
  1. 视觉检测噪声大 → 在OpenMV端增加目标位置滤波
  2. 追踪Kp过大 → 减小追踪PID的Kp
  3. 死区太小 → 增大SERVO_DEADBAND_DEG
  4. 帧率太低 → 提高OpenMV帧率或降低图像分辨率

解决方案：
  在OpenMV端对目标坐标做滑动平均滤波：
  x_filtered = 0.7 * x_filtered + 0.3 * x_new
```

### 11.4 性能测试方法

**稳定性测试**

```
测试1：静态稳定精度
  方法：将云台固定，测量输出角度的标准差
  指标：σ < 0.5°

测试2：动态稳定效果
  方法：以1Hz、5°幅度正弦波扰动，测量输出角度
  指标：输出幅度 < 输入幅度的10%（衰减20dB）

测试3：阶跃响应
  方法：突然施加30°扰动，测量恢复时间
  指标：恢复到±2°以内的时间 < 300ms
```

**追踪性能测试**

```
测试1：静态追踪精度
  方法：目标静止在画面中，测量目标偏离中心的像素数
  指标：< 5像素（320×240分辨率）

测试2：动态追踪延迟
  方法：目标以已知速度运动，测量云台跟踪延迟
  指标：延迟 < 100ms

测试3：最大追踪速度
  方法：逐渐增大目标运动速度，直到追踪失败
  指标：> 30°/s
```

---

## 12. 性能优化

### 12.1 滤波器截止频率选择

互补滤波的截止频率影响稳定性和响应速度的平衡：

```
截止频率 fc = (1-α) / (2π × α × dt)

α=0.98, dt=0.01s → fc=0.325Hz（推荐，平衡稳定性和响应）
α=0.95, dt=0.01s → fc=0.844Hz（更快响应，但更多漂移）
α=0.99, dt=0.01s → fc=0.160Hz（更稳定，但响应更慢）

选择原则：
  - 如果主要扰动频率 < 1Hz（慢速晃动）：α=0.98
  - 如果主要扰动频率 > 5Hz（高频振动）：α=0.99
  - 如果需要快速响应（追踪运动目标）：α=0.95
```

### 12.2 控制频率优化

提高控制频率可以改善稳定性，但会增加CPU负载：

```
控制频率 vs 性能：
  50Hz（dt=20ms）：基本可用，但响应较慢
  100Hz（dt=10ms）：推荐，平衡性能和负载
  200Hz（dt=5ms）：更好，需要确保IMU读取时间 < 3ms
  500Hz（dt=2ms）：高性能，需要SPI接口的IMU（I2C太慢）

STM32F103@72MHz的I2C读取时间：
  400kHz I2C，读取14字节：约350μs
  100Hz控制频率时，I2C占用3.5%的CPU时间
  200Hz时占用7%，仍然可以接受
```

### 12.3 舵机响应速度提升

MG996R的标称速度是0.17s/60°（5V时），可以通过以下方法提升响应：

```c
/* 方法1：提高舵机电压（5V→6V，速度提升约20%）
 * 注意：需要确认舵机支持6V，MG996R支持4.8V~7.2V
 */

/* 方法2：前馈控制（预测目标位置，提前输出）
 * 在PID输出基础上加入速度前馈
 */
float feedforward = attitude_rate * 0.1f;  /* 角速度前馈 */
float total_output = pid_output + feedforward;

/* 方法3：使用数字舵机（如DS3218，支持333Hz PWM）
 * 更高的PWM频率可以减少舵机响应延迟
 * 修改TIM2配置：Period=3000-1（333Hz）
 */
```

### 12.4 功耗优化

```c
/* 方法1：舵机空闲时关闭PWM
 * 当云台长时间静止时，关闭PWM信号
 * 舵机会进入自由状态（无保持力矩），节省电流
 */
#define IDLE_THRESHOLD_DEG  0.3f   /* 角度变化小于0.3°视为静止 */
#define IDLE_COUNT_MAX      100    /* 连续100次（1秒）静止后关闭PWM */

static uint16_t idle_count = 0;
static uint8_t  pwm_enabled = 1;

void servo_idle_management(float angle_change)
{
    if (fabsf(angle_change) < IDLE_THRESHOLD_DEG) {
        idle_count++;
        if (idle_count >= IDLE_COUNT_MAX && pwm_enabled) {
            /* 关闭PWM（舵机进入自由状态） */
            HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_1);
            HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_2);
            pwm_enabled = 0;
        }
    } else {
        idle_count = 0;
        if (!pwm_enabled) {
            /* 重新启动PWM */
            HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
            HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
            pwm_enabled = 1;
        }
    }
}

/* 方法2：降低MCU时钟频率（非控制时段）
 * 在主循环空闲时，将时钟从72MHz降到36MHz
 * 控制中断触发时自动恢复（中断不受时钟降频影响）
 */

/* 方法3：MPU6050低功耗模式
 * 不使用时可以将MPU6050置于低功耗模式
 * PWR_MGMT_1寄存器bit5=1（CYCLE模式，1.25Hz采样）
 */
```

---

## 13. 扩展功能

### 13.1 三轴云台扩展

在两轴基础上增加Yaw轴（偏航轴），实现完整的三轴稳定：

```c
/* 三轴云台需要增加：
 * 1. 第三个舵机（Yaw轴）：TIM2_CH3，PA2
 * 2. 磁力计（如HMC5883L）：提供绝对偏航角参考
 * 3. 九轴融合算法（Mahony或Madgwick滤波器）
 */

/* Mahony滤波器（比互补滤波更精确的九轴融合） */
typedef struct {
    float q0, q1, q2, q3;  /* 四元数 */
    float ex_int, ey_int, ez_int;  /* 积分误差 */
    float Kp, Ki;  /* 比例积分增益 */
} MahonyFilter;

void mahony_update(MahonyFilter *f,
                   float gx, float gy, float gz,  /* 陀螺仪 °/s */
                   float ax, float ay, float az,  /* 加速度计 g */
                   float mx, float my, float mz,  /* 磁力计 uT */
                   float dt)
{
    float norm;
    float hx, hy, bx, bz;
    float vx, vy, vz, wx, wy, wz;
    float ex, ey, ez;

    /* 归一化加速度 */
    norm = sqrtf(ax*ax + ay*ay + az*az);
    if (norm == 0.0f) return;
    ax /= norm; ay /= norm; az /= norm;

    /* 归一化磁力计 */
    norm = sqrtf(mx*mx + my*my + mz*mz);
    if (norm == 0.0f) return;
    mx /= norm; my /= norm; mz /= norm;

    /* 从四元数计算参考方向 */
    hx = 2.0f*mx*(0.5f - f->q2*f->q2 - f->q3*f->q3) +
         2.0f*my*(f->q1*f->q2 - f->q0*f->q3) +
         2.0f*mz*(f->q1*f->q3 + f->q0*f->q2);
    hy = 2.0f*mx*(f->q1*f->q2 + f->q0*f->q3) +
         2.0f*my*(0.5f - f->q1*f->q1 - f->q3*f->q3) +
         2.0f*mz*(f->q2*f->q3 - f->q0*f->q1);
    bx = sqrtf(hx*hx + hy*hy);
    bz = 2.0f*mx*(f->q1*f->q3 - f->q0*f->q2) +
         2.0f*my*(f->q2*f->q3 + f->q0*f->q1) +
         2.0f*mz*(0.5f - f->q1*f->q1 - f->q2*f->q2);

    /* 估计重力和磁场方向 */
    vx = 2.0f*(f->q1*f->q3 - f->q0*f->q2);
    vy = 2.0f*(f->q0*f->q1 + f->q2*f->q3);
    vz = f->q0*f->q0 - f->q1*f->q1 - f->q2*f->q2 + f->q3*f->q3;
    wx = 2.0f*bx*(0.5f - f->q2*f->q2 - f->q3*f->q3) +
         2.0f*bz*(f->q1*f->q3 - f->q0*f->q2);
    wy = 2.0f*bx*(f->q1*f->q2 - f->q0*f->q3) +
         2.0f*bz*(f->q0*f->q1 + f->q2*f->q3);
    wz = 2.0f*bx*(f->q0*f->q2 + f->q1*f->q3) +
         2.0f*bz*(0.5f - f->q1*f->q1 - f->q2*f->q2);

    /* 误差（叉积） */
    ex = ay*vz - az*vy + my*wz - mz*wy;
    ey = az*vx - ax*vz + mz*wx - mx*wz;
    ez = ax*vy - ay*vx + mx*wy - my*wx;

    /* 积分误差 */
    f->ex_int += f->Ki * ex * dt;
    f->ey_int += f->Ki * ey * dt;
    f->ez_int += f->Ki * ez * dt;

    /* 修正陀螺仪 */
    gx += f->Kp*ex + f->ex_int;
    gy += f->Kp*ey + f->ey_int;
    gz += f->Kp*ez + f->ez_int;

    /* 四元数积分 */
    f->q0 += (-f->q1*gx - f->q2*gy - f->q3*gz) * (0.5f*dt);
    f->q1 += ( f->q0*gx + f->q2*gz - f->q3*gy) * (0.5f*dt);
    f->q2 += ( f->q0*gy - f->q1*gz + f->q3*gx) * (0.5f*dt);
    f->q3 += ( f->q0*gz + f->q1*gy - f->q2*gx) * (0.5f*dt);

    /* 归一化四元数 */
    norm = sqrtf(f->q0*f->q0 + f->q1*f->q1 +
                 f->q2*f->q2 + f->q3*f->q3);
    f->q0 /= norm; f->q1 /= norm;
    f->q2 /= norm; f->q3 /= norm;
}
```

### 13.2 蓝牙遥控扩展

通过HC-05蓝牙模块，手机APP可以远程控制云台：

```c
/* 蓝牙命令协议：
 * 'P' + angle_byte：设置Pan角度（angle_byte: 0~180，对应-90°~+90°）
 * 'T' + angle_byte：设置Tilt角度
 * 'C'：云台回中
 * 'S'：切换到稳定模式
 * 'K'：切换到追踪模式
 */

void bluetooth_parse_command(uint8_t *buf, uint16_t len)
{
    for (uint16_t i = 0; i < len - 1; i++) {
        switch (buf[i]) {
            case 'P':
                {
                    float angle = (float)buf[i+1] - 90.0f;
                    gimbal_set_angle(GIMBAL_CH_PAN, angle);
                    i++;
                }
                break;
            case 'T':
                {
                    float angle = (float)buf[i+1] - 90.0f;
                    gimbal_set_angle(GIMBAL_CH_TILT, angle);
                    i++;
                }
                break;
            case 'C':
                gimbal_center();
                break;
            case 'S':
                g_gimbal_state = GIMBAL_STATE_STABILIZE;
                stabilize_init();
                break;
            case 'K':
                g_gimbal_state = GIMBAL_STATE_TRACK;
                track_init();
                break;
        }
    }
}
```

### 13.3 自动校准功能

上电时自动进行零偏校准，并将结果保存到Flash：

```c
/* 将校准数据保存到STM32内部Flash
 * STM32F103C8T6 Flash大小64KB，最后一页（0x0800FC00）用于存储
 */
#define CALIB_FLASH_ADDR  0x0800FC00UL
#define CALIB_MAGIC       0xCAFEBABEUL

typedef struct {
    uint32_t magic;           /* 魔数，验证数据有效性 */
    MPU6050_Offset offset;    /* 校准数据 */
    uint32_t checksum;        /* 简单校验和 */
} CalibFlashData;

void calib_save_to_flash(const MPU6050_Offset *offset)
{
    CalibFlashData data;
    data.magic  = CALIB_MAGIC;
    data.offset = *offset;

    /* 计算校验和 */
    uint32_t *p = (uint32_t*)&data.offset;
    data.checksum = 0;
    for (size_t i = 0; i < sizeof(MPU6050_Offset)/4; i++) {
        data.checksum ^= p[i];
    }

    /* 解锁Flash */
    HAL_FLASH_Unlock();

    /* 擦除页 */
    FLASH_EraseInitTypeDef erase = {
        .TypeErase   = FLASH_TYPEERASE_PAGES,
        .PageAddress = CALIB_FLASH_ADDR,
        .NbPages     = 1
    };
    uint32_t page_error;
    HAL_FLASHEx_Erase(&erase, &page_error);

    /* 写入数据（每次写16位） */
    uint16_t *src = (uint16_t*)&data;
    uint32_t addr = CALIB_FLASH_ADDR;
    for (size_t i = 0; i < sizeof(CalibFlashData)/2; i++) {
        HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, addr, src[i]);
        addr += 2;
    }

    HAL_FLASH_Lock();
}

uint8_t calib_load_from_flash(MPU6050_Offset *offset)
{
    CalibFlashData *data = (CalibFlashData*)CALIB_FLASH_ADDR;

    if (data->magic != CALIB_MAGIC) return 0;  /* 无有效数据 */

    /* 验证校验和 */
    uint32_t *p = (uint32_t*)&data->offset;
    uint32_t checksum = 0;
    for (size_t i = 0; i < sizeof(MPU6050_Offset)/4; i++) {
        checksum ^= p[i];
    }
    if (checksum != data->checksum) return 0;  /* 数据损坏 */

    *offset = data->offset;
    return 1;  /* 加载成功 */
}
```

---

## 14. 延伸阅读

- [舵机控制基础](../beginner/03-servo-motor-control.html) — 舵机PWM控制原理、角度映射、多舵机控制
- [PID控制算法](../intermediate/03-pid-control.html) — PID理论、离散化、参数整定方法
- [四自由度机械臂](05-robot-arm-project.html) — 更复杂的多舵机协调控制系统
- [六足机器人](06-hexapod-robot.html) — 18舵机协调控制、步态规划
<!-- 以下链接指向的文件不存在，待补充后取消注释
- [I2C通信协议](../../03-communication-protocols/i2c-protocol.html) — I2C时序、多设备总线、常见问题
-->

---

## 15. 参考资料

1. **MG996R Datasheet** — Tower Pro，舵机电气特性和机械规格
2. **MPU-6000/MPU-6050 Product Specification** — InvenSense，寄存器映射和通信协议
3. **STM32F103xx Reference Manual** — STMicroelectronics，定时器、I2C、UART详细说明
4. **《PID控制器设计与调参》** — 陶永华，PID理论和工程整定方法
5. **《四旋翼飞行器设计与控制》** — 全权，姿态解算和控制算法
6. **Mahony, R. et al.** — "Nonlinear Complementary Filters on the Special Orthogonal Group"，IEEE TAC 2008
7. **OpenMV官方文档** — [docs.openmv.io](https://docs.openmv.io/)，视觉追踪API参考
8. **STM32 HAL库用户手册** — UM1850，HAL API详细说明

---

## 16. 云台机械原理深入：无刷电机 vs 舵机

### 16.1 两种驱动方案对比

云台驱动方案主要分为两类：**舵机（Servo）驱动**和**无刷直流电机（Brushless DC Motor，BLDC）驱动**。两者在性能、成本和复杂度上有显著差异。

```
云台驱动方案对比
================

舵机云台                          无刷电机云台
┌─────────────────────┐           ┌─────────────────────┐
│  控制器              │           │  控制器              │
│  (STM32/Arduino)    │           │  (SimpleBGC/Storm32) │
│         │           │           │         │           │
│    PWM信号           │           │   FOC算法 + 三相PWM  │
│         │           │           │         │           │
│  ┌──────▼──────┐    │           │  ┌──────▼──────┐    │
│  │  舵机内部   │    │           │  │  无刷电机   │    │
│  │  控制电路   │    │           │  │  (直接驱动) │    │
│  │  + 减速齿轮 │    │           │  │  无减速齿轮 │    │
│  └─────────────┘    │           │  └─────────────┘    │
└─────────────────────┘           └─────────────────────┘

特性对比：
┌──────────────┬──────────────────┬──────────────────────┐
│ 特性          │ 舵机云台          │ 无刷电机云台          │
├──────────────┼──────────────────┼──────────────────────┤
│ 控制复杂度    │ 低（PWM直接控制） │ 高（需要FOC算法）     │
│ 成本          │ 低（¥20~50/轴）  │ 高（¥100~500/轴）    │
│ 精度          │ 中（±0.5°~1°）  │ 高（±0.1°~0.3°）    │
│ 响应速度      │ 慢（0.17s/60°）  │ 快（<10ms）          │
│ 噪音          │ 有（齿轮噪音）   │ 极低（直驱）          │
│ 扭矩          │ 中（13kg·cm）   │ 高（取决于电机）      │
│ 反向驱动性    │ 差（齿轮自锁）   │ 好（可被外力推动）    │
│ 适用场景      │ 教学/低成本项目  │ 专业航拍/商业产品     │
└──────────────┴──────────────────┴──────────────────────┘
```

**舵机云台的局限性**

舵机内部有减速齿轮组（通常减速比1:200~1:300），这带来了几个问题：

1. **齿隙（Backlash）**：齿轮间的间隙导致约0.5°~2°的死区，影响精度
2. **摩擦力**：齿轮摩擦产生非线性阻力，使PID调参困难
3. **响应延迟**：内部控制电路有约20ms的响应延迟
4. **噪音**：齿轮啮合产生明显的机械噪音，不适合录音场景

**无刷电机云台的优势**

无刷电机直接驱动（无减速齿轮），通过磁场定向控制（FOC）精确控制转矩：

1. **零齿隙**：直驱无机械间隙，精度极高
2. **低噪音**：无齿轮摩擦，运行几乎无声
3. **快速响应**：电流环响应时间<1ms，整体系统带宽可达50Hz以上
4. **可反向驱动**：外力可以推动电机，适合需要手动调整的场景

### 16.2 稳定化理论：扰动抑制原理

云台稳定化的本质是**扰动抑制控制（Disturbance Rejection Control）**。

```
稳定化控制框图
==============

                    扰动 d(t)（载体运动）
                         │
                         ▼
目标姿态    ┌─────┐  控制量  ┌──────────┐  实际姿态
θ_ref ────►│ PID ├─────────►│  云台+   ├──────────► θ_actual
           └──┬──┘          │  电机    │
              │             └──────────┘
              │                  │
              │    ┌─────────┐   │
              └────┤  IMU    │◄──┘
                   │ 姿态解算 │
                   └─────────┘

控制目标：θ_actual → θ_ref（通常为0°，即水平）
扰动来源：载体的俯仰、横滚、偏航运动
```

**频域分析**

云台稳定性可以用频域方法分析。典型的扰动频率分布：

```
扰动频率分布（无人机场景）：
  0.1~2Hz：机身低频晃动（风力、操控输入）
  10~50Hz：螺旋桨振动（4轴无人机，电机转速1000~8000RPM）
  100~500Hz：高频机械振动（电机轴承、碳纤维共振）

云台控制带宽要求：
  需要抑制的频率：0.1~50Hz
  控制带宽：至少100Hz（奈奎斯特定理：采样率≥2×最高频率）
  实际推荐：200~500Hz控制频率（无刷电机云台）

舵机云台的局限：
  舵机响应带宽约5~10Hz，只能抑制低频扰动（<2Hz）
  对螺旋桨振动（10~50Hz）几乎无效
  → 这是为什么专业无人机云台必须使用无刷电机
```

### 16.3 SimpleBGC（BGC32）开源云台控制器

SimpleBGC（也称BGC32）是目前最流行的开源无刷电机云台控制器，由俄罗斯工程师Aleksey Moskalenko开发。

**硬件规格**

```
SimpleBGC 32-bit 规格：
┌─────────────────────────────────────────┐
│  主控：STM32F103（72MHz Cortex-M3）      │
│  IMU：MPU6050（主IMU）+ 可选第二IMU      │
│  电机驱动：3路三相桥（每路最大3A）        │
│  通信：UART（调试/配置）、I2C（IMU）      │
│  输入：RC接收机（PPM/PWM）、UART命令      │
│  电源：8~25V输入，内置5V/3.3V稳压        │
│  尺寸：50×50mm（标准版）                 │
└─────────────────────────────────────────┘

控制架构（三环级联PID）：
  外环：姿态角环（角度PID）
  中环：角速度环（速率PID）
  内环：电流环（FOC电流控制）

控制频率：
  角度环：400Hz
  速率环：400Hz
  电流环：32kHz（FOC PWM频率）
```

**SimpleBGC GUI配置界面**

SimpleBGC提供Windows/Mac GUI软件（SimpleBGC_GUI）通过串口配置参数：

```
主要配置项：
1. 电机参数
   - 极对数（Pole Pairs）：决定电角度与机械角度的关系
   - 功率（Power）：0~255，控制最大电流
   - 反转（Invert）：改变电机旋转方向

2. PID参数（每轴独立）
   - P（比例）：0~255
   - I（积分）：0~255
   - D（微分）：0~255
   - 外环P（Outer P）：角度环比例增益

3. 自动调参（Auto Tune）
   - 自动激励电机，测量系统响应
   - 自动计算最优PID参数
   - 适合初学者快速上手

4. 跟随模式（Follow Mode）
   - 跟随偏航（Follow Yaw）：云台跟随机身偏航
   - 跟随俯仰（Follow Pitch）：云台跟随机身俯仰
   - 锁定模式（Lock Mode）：完全锁定，不跟随任何轴
```

**SimpleBGC串口命令协议**

SimpleBGC支持通过串口发送命令控制云台，适合与上位机集成：

```c
/* SimpleBGC串口协议（SBGC32 Serial API）
 * 帧格式：'>' + CMD_ID + DATA_SIZE + DATA + CHECKSUM
 */

/* 常用命令ID */
#define SBGC_CMD_CONTROL          0x43  /* 'C'：控制云台角度/速度 */
#define SBGC_CMD_GET_ANGLES       0x49  /* 'I'：获取当前角度 */
#define SBGC_CMD_CALIB_ACC        0x61  /* 'a'：加速度计校准 */
#define SBGC_CMD_MOTORS_ON        0x4D  /* 'M'：开启电机 */
#define SBGC_CMD_MOTORS_OFF       0x6D  /* 'm'：关闭电机 */

/* 控制命令数据结构 */
typedef struct __attribute__((packed)) {
    uint8_t  roll_mode;    /* 0=无控制，1=速度，2=角度 */
    int16_t  roll_speed;   /* 速度模式：°/s × 0.1220740379 */
    int16_t  roll_angle;   /* 角度模式：度 × 182.04444 */
    uint8_t  pitch_mode;
    int16_t  pitch_speed;
    int16_t  pitch_angle;
    uint8_t  yaw_mode;
    int16_t  yaw_speed;
    int16_t  yaw_angle;
} SBGC_ControlData;

/* 发送控制命令 */
void sbgc_send_control(UART_HandleTypeDef *huart,
                       float pitch_deg, float yaw_deg)
{
    SBGC_ControlData ctrl = {0};

    /* 设置Pitch轴为角度模式 */
    ctrl.pitch_mode  = 2;
    ctrl.pitch_angle = (int16_t)(pitch_deg * 182.04444f);

    /* 设置Yaw轴为角度模式 */
    ctrl.yaw_mode  = 2;
    ctrl.yaw_angle = (int16_t)(yaw_deg * 182.04444f);

    /* 构建帧 */
    uint8_t frame[sizeof(SBGC_ControlData) + 4];
    frame[0] = '>';
    frame[1] = SBGC_CMD_CONTROL;
    frame[2] = sizeof(SBGC_ControlData);
    memcpy(&frame[3], &ctrl, sizeof(SBGC_ControlData));

    /* 计算校验和（所有数据字节之和的低8位） */
    uint8_t checksum = 0;
    for (int i = 1; i < 3 + sizeof(SBGC_ControlData); i++) {
        checksum += frame[i];
    }
    frame[3 + sizeof(SBGC_ControlData)] = checksum;

    HAL_UART_Transmit(huart, frame, sizeof(frame), 100);
}
```

### 16.4 Storm32 BGC 开源控制器

Storm32 BGC是另一款流行的开源三轴云台控制器，基于STM32F103，支持三轴无刷电机控制。

```
Storm32 BGC 特点：
┌─────────────────────────────────────────────┐
│  主控：STM32F103CBT6（128KB Flash）          │
│  IMU：MPU6050 × 2（主IMU + 辅助IMU）        │
│  电机驱动：3路三相桥（每路最大2.5A）          │
│  通信：UART × 2、I2C、SPI                   │
│  特色功能：                                  │
│    - 支持MAVLink协议（与飞控直接通信）        │
│    - 支持NT（NTLogger）实时数据记录           │
│    - 支持RC直通（Pass-through）模式          │
│    - 开源固件（GitHub: olliw42/stm32f1）     │
└─────────────────────────────────────────────┘

Storm32 vs SimpleBGC 对比：
┌──────────────┬──────────────────┬──────────────────┐
│ 特性          │ SimpleBGC 32bit  │ Storm32 BGC      │
├──────────────┼──────────────────┼──────────────────┤
│ 价格          │ ¥200~500（正版） │ ¥80~150（克隆版）│
│ 软件          │ 闭源（固件）     │ 完全开源         │
│ MAVLink支持   │ 有限             │ 原生支持         │
│ 社区          │ 大（rcgroups）   │ 中等             │
│ 调参难度      │ 低（GUI友好）    │ 中等             │
│ 三轴支持      │ 是               │ 是               │
└──────────────┴──────────────────┴──────────────────┘
```


---

## 17. 级联PID控制架构

### 17.1 三环级联PID原理

专业云台控制器（如SimpleBGC）使用三环级联PID（Cascade PID），而不是本项目中的单环PID。理解三环架构有助于进一步提升控制性能。

```
三环级联PID控制框图
==================

目标角度                                              实际角度
θ_ref ──►[角度环PID]──► ω_ref ──►[速率环PID]──► I_ref ──►[电流环FOC]──► 电机 ──► θ_actual
          (外环)                   (中环)                  (内环)              │
            ▲                        ▲                        ▲               │
            │                        │                        │               │
            └────────────────────────┴────────────────────────┘               │
                              IMU反馈（角度、角速度）                          │
                                                                               │
                              编码器/霍尔传感器反馈（电流）◄──────────────────┘

各环说明：
  外环（角度环）：输入=目标角度，输出=目标角速度，带宽约5~20Hz
  中环（速率环）：输入=目标角速度，输出=目标电流，带宽约50~200Hz
  内环（电流环）：输入=目标电流，输出=PWM占空比，带宽约1~10kHz
```

**为什么需要三环？**

单环PID直接从角度误差输出PWM，存在以下问题：
1. 系统非线性（电机特性、摩擦力）难以用单个PID补偿
2. 带宽受限：单环PID的带宽受限于最慢的环节（机械惯量）
3. 抗扰动能力弱：外部扰动需要通过角度误差才能被感知

三环级联的优势：
1. 内环快速响应，外环稳定精确
2. 每环独立调参，降低调参难度
3. 内环可以补偿电机非线性，外环只需处理线性化后的系统

### 17.2 级联PID C代码实现

```c
/* cascade_pid.h - 三环级联PID控制器 */
#ifndef CASCADE_PID_H
#define CASCADE_PID_H

#include "pid.h"

/* 级联PID结构体 */
typedef struct {
    PID_Controller angle_pid;   /* 外环：角度PID */
    PID_Controller rate_pid;    /* 中环：速率PID */
    /* 内环（电流环）通常由FOC硬件实现，此处用简化版 */

    /* 各环输出 */
    float angle_output;   /* 角度环输出（目标角速度，°/s） */
    float rate_output;    /* 速率环输出（目标电流/PWM） */
} CascadePID;

/* 初始化参数 */
typedef struct {
    /* 角度环参数 */
    float angle_kp, angle_ki, angle_kd;
    float angle_output_limit;   /* 最大角速度，°/s */

    /* 速率环参数 */
    float rate_kp, rate_ki, rate_kd;
    float rate_output_limit;    /* 最大输出（PWM占空比，0~1） */
} CascadePIDParams;

void cascade_pid_init(CascadePID *cpid, const CascadePIDParams *params);
float cascade_pid_compute(CascadePID *cpid,
                          float angle_setpoint,  /* 目标角度，° */
                          float angle_measured,  /* 测量角度，° */
                          float rate_measured,   /* 测量角速度，°/s */
                          float dt);             /* 采样时间，s */
void cascade_pid_reset(CascadePID *cpid);

#endif /* CASCADE_PID_H */
```

```c
/* cascade_pid.c */
#include "cascade_pid.h"
#include <string.h>

void cascade_pid_init(CascadePID *cpid, const CascadePIDParams *params)
{
    memset(cpid, 0, sizeof(CascadePID));

    /* 初始化角度环（外环）
     * 输出限幅：最大角速度（°/s）
     * 积分限幅：角速度限幅的50%
     */
    pid_init(&cpid->angle_pid,
             params->angle_kp, params->angle_ki, params->angle_kd,
             params->angle_output_limit,
             params->angle_output_limit * 0.5f,
             0.02f);  /* 微分滤波时间常数20ms */

    /* 初始化速率环（中环）
     * 输出限幅：PWM占空比（0~1）
     * 积分限幅：输出限幅的30%
     */
    pid_init(&cpid->rate_pid,
             params->rate_kp, params->rate_ki, params->rate_kd,
             params->rate_output_limit,
             params->rate_output_limit * 0.3f,
             0.005f);  /* 微分滤波时间常数5ms */
}

/**
 * @brief  级联PID计算
 * @param  angle_setpoint  目标角度（°）
 * @param  angle_measured  IMU测量角度（°）
 * @param  rate_measured   IMU测量角速度（°/s）
 * @param  dt              采样时间（s）
 * @retval 最终输出（PWM占空比，-1.0~+1.0）
 *
 * @note   级联PID的关键：外环输出作为内环的设定值
 *         外环：角度误差 → 目标角速度
 *         内环：角速度误差 → 电机控制量
 */
float cascade_pid_compute(CascadePID *cpid,
                          float angle_setpoint,
                          float angle_measured,
                          float rate_measured,
                          float dt)
{
    /* 外环：角度PID → 输出目标角速度 */
    cpid->angle_output = pid_compute(&cpid->angle_pid,
                                     angle_setpoint,
                                     angle_measured,
                                     dt);

    /* 内环：速率PID → 输出电机控制量
     * 设定值 = 外环输出（目标角速度）
     * 测量值 = IMU陀螺仪角速度
     */
    cpid->rate_output = pid_compute(&cpid->rate_pid,
                                    cpid->angle_output,
                                    rate_measured,
                                    dt);

    return cpid->rate_output;
}

void cascade_pid_reset(CascadePID *cpid)
{
    pid_reset(&cpid->angle_pid);
    pid_reset(&cpid->rate_pid);
    cpid->angle_output = 0.0f;
    cpid->rate_output  = 0.0f;
}
```

**级联PID参数整定顺序**

```
整定顺序（从内到外）：
1. 先整定速率环（中环）
   - 将角度环增益设为0（只用速率环）
   - 给定阶跃角速度指令，调整速率环PID
   - 目标：快速无超调地跟踪角速度指令

2. 再整定角度环（外环）
   - 速率环已整定好后，整定角度环
   - 给定阶跃角度指令，调整角度环PID
   - 目标：快速无超调地跟踪角度指令

典型参数范围（舵机云台）：
  角度环：Kp=2~5, Ki=0.01~0.1, Kd=0.1~0.5
          output_limit=200°/s（最大角速度）
  速率环：Kp=0.01~0.05, Ki=0.001~0.01, Kd=0
          output_limit=45°（最大舵机角度变化）
```

### 17.3 重力前馈补偿

对于Tilt轴（俯仰轴），摄像头的重力会产生一个与角度相关的扰动力矩。当摄像头向前倾斜时，重力力矩会使其继续向前倾斜；向后倾斜时同理。

```
重力力矩分析：
===============

         摄像头质心
              │
              │ L（力臂）
              │
    ──────────●──────────  Tilt轴
              │
              ▼ mg（重力）

重力力矩：τ_gravity = m × g × L × sin(θ)

其中：
  m = 摄像头质量（kg）
  g = 9.8 m/s²
  L = 质心到转轴的距离（m）
  θ = Tilt轴当前角度（rad）

当θ=0°（水平）时，τ_gravity=0（无重力力矩）
当θ=30°时，τ_gravity = m×g×L×sin(30°) = 0.5×m×g×L
当θ=90°时，τ_gravity = m×g×L（最大）
```

**前馈补偿代码**

```c
/* gravity_feedforward.h */
#ifndef GRAVITY_FF_H
#define GRAVITY_FF_H

#include <math.h>

/* 重力前馈参数 */
typedef struct {
    float mass_kg;      /* 摄像头质量（kg） */
    float arm_m;        /* 力臂长度（m） */
    float ff_gain;      /* 前馈增益（调整系数，0.5~1.5） */
} GravityFF;

/**
 * @brief  计算重力前馈补偿量
 * @param  ff       前馈参数
 * @param  tilt_deg Tilt轴当前角度（°）
 * @retval 前馈补偿量（叠加到PID输出上）
 *
 * @note   前馈补偿的方向：
 *         当tilt>0（摄像头向前倾）时，重力使其继续向前
 *         前馈应输出正值（向后补偿）
 */
float gravity_ff_compute(const GravityFF *ff, float tilt_deg)
{
    float tilt_rad = tilt_deg * (3.14159265f / 180.0f);

    /* 重力力矩（归一化，单位：N·m） */
    float gravity_torque = ff->mass_kg * 9.8f * ff->arm_m * sinf(tilt_rad);

    /* 转换为控制量（需要根据实际系统标定ff_gain） */
    return gravity_torque * ff->ff_gain;
}

#endif /* GRAVITY_FF_H */
```

**在控制循环中使用前馈**

```c
/* 在稳定控制任务中加入重力前馈 */
void stabilize_task_with_feedforward(void)
{
    MPU6050_Data imu;
    const float dt = 0.01f;

    if (mpu6050_read_calibrated(&imu, &g_imu_offset) != HAL_OK) return;

    complementary_filter(&g_attitude, &imu, dt);

    /* PID计算 */
    float pan_output  = pid_compute(&g_pan_pid,  0.0f, g_attitude.pitch, dt);
    float tilt_output = pid_compute(&g_tilt_pid, 0.0f, g_attitude.roll,  dt);

    /* 重力前馈补偿（仅Tilt轴需要） */
    GravityFF ff = {
        .mass_kg = 0.15f,   /* 摄像头150g */
        .arm_m   = 0.03f,   /* 力臂30mm */
        .ff_gain = 1.0f     /* 初始增益1.0，需要实测标定 */
    };
    float ff_compensation = gravity_ff_compute(&ff, g_attitude.roll);
    tilt_output += ff_compensation;

    /* 输出限幅 */
    if (tilt_output >  TILT_ANGLE_MAX) tilt_output =  TILT_ANGLE_MAX;
    if (tilt_output < -TILT_ANGLE_MAX) tilt_output = -TILT_ANGLE_MAX;

    gimbal_set_angle(GIMBAL_CH_PAN,  pan_output);
    gimbal_set_angle(GIMBAL_CH_TILT, tilt_output);
}
```

**前馈增益标定方法**

```
标定步骤：
1. 将Ki=0（关闭积分），只用P+D+前馈
2. 将云台倾斜到30°，观察稳态误差
3. 如果有稳态误差（摄像头不能保持30°）：
   - 误差为正（实际角度<目标）：增大ff_gain
   - 误差为负（实际角度>目标）：减小ff_gain
4. 在多个角度（0°、15°、30°、45°）重复验证
5. 前馈标定好后，再加入Ki消除残余稳态误差

理想效果：加入前馈后，Ki可以设置得很小（甚至为0）
          系统在各个角度都能快速稳定，无稳态误差
```

### 17.4 跟随模式与锁定模式切换

专业云台支持两种工作模式：

```
模式对比：
┌──────────────┬──────────────────────────┬──────────────────────────┐
│ 模式          │ 锁定模式（Lock Mode）     │ 跟随模式（Follow Mode）  │
├──────────────┼──────────────────────────┼──────────────────────────┤
│ 目标角度      │ 固定（如0°水平）          │ 跟随载体缓慢运动          │
│ 适用场景      │ 航拍稳定、固定拍摄        │ 手持跟拍、运动拍摄        │
│ 效果          │ 画面完全稳定              │ 画面稳定但跟随拍摄方向    │
│ 实现方式      │ 目标角度=常数             │ 目标角度=低通滤波后的载体角│
└──────────────┴──────────────────────────┴──────────────────────────┘
```

**跟随模式实现**

跟随模式的关键是：对载体的慢速运动（<1Hz）进行跟随，对快速扰动（>1Hz）进行抑制。

```c
/* follow_mode.h */
#ifndef FOLLOW_MODE_H
#define FOLLOW_MODE_H

/* 跟随模式低通滤波器时间常数
 * 较大的τ：跟随更慢，稳定性更好
 * 较小的τ：跟随更快，但可能引入抖动
 */
#define FOLLOW_TAU_PAN   2.0f   /* Pan轴跟随时间常数（秒） */
#define FOLLOW_TAU_TILT  0.0f   /* Tilt轴不跟随（锁定水平） */

/* 跟随死区：载体运动小于此角度时不跟随（防止微小抖动触发跟随） */
#define FOLLOW_DEADBAND  5.0f   /* 5°死区 */

typedef struct {
    float pan_target;   /* 跟随模式下的Pan目标角度 */
    float tilt_target;  /* 跟随模式下的Tilt目标角度 */
} FollowState;

void follow_mode_update(FollowState *fs,
                        float carrier_yaw,    /* 载体偏航角（°） */
                        float carrier_pitch,  /* 载体俯仰角（°） */
                        float dt);

#endif /* FOLLOW_MODE_H */
```

```c
/* follow_mode.c */
#include "follow_mode.h"
#include <math.h>

/**
 * @brief  跟随模式目标角度更新
 * @param  fs            跟随状态
 * @param  carrier_yaw   载体偏航角（由IMU积分得到，有漂移）
 * @param  carrier_pitch 载体俯仰角
 * @param  dt            采样时间（s）
 *
 * @note   跟随模式使用一阶低通滤波器平滑目标角度
 *         目标角度 = 低通滤波后的载体角度
 *         PID的设定值 = 目标角度（而非固定的0°）
 */
void follow_mode_update(FollowState *fs,
                        float carrier_yaw,
                        float carrier_pitch,
                        float dt)
{
    /* Pan轴跟随（偏航跟随） */
    if (FOLLOW_TAU_PAN > 0.0f) {
        /* 死区判断：载体运动小于死区时不更新目标 */
        float pan_error = carrier_yaw - fs->pan_target;

        /* 角度归一化到-180°~+180° */
        while (pan_error >  180.0f) pan_error -= 360.0f;
        while (pan_error < -180.0f) pan_error += 360.0f;

        if (fabsf(pan_error) > FOLLOW_DEADBAND) {
            /* 一阶低通滤波：y += (x - y) × (dt / (τ + dt)) */
            fs->pan_target += pan_error * (dt / (FOLLOW_TAU_PAN + dt));
        }
    }

    /* Tilt轴：默认锁定水平（不跟随） */
    if (FOLLOW_TAU_TILT > 0.0f) {
        float tilt_error = carrier_pitch - fs->tilt_target;
        if (fabsf(tilt_error) > FOLLOW_DEADBAND) {
            fs->tilt_target += tilt_error * (dt / (FOLLOW_TAU_TILT + dt));
        }
    }
    /* 否则 fs->tilt_target 保持0°（锁定水平） */
}
```

**模式切换状态机扩展**

```c
/* 扩展状态机，支持跟随/锁定模式 */
typedef enum {
    GIMBAL_MODE_LOCK   = 0,  /* 锁定模式：完全稳定 */
    GIMBAL_MODE_FOLLOW = 1,  /* 跟随模式：跟随载体慢速运动 */
    GIMBAL_MODE_TRACK  = 2,  /* 追踪模式：视觉目标追踪 */
} GimbalMode;

/* 模式切换时的平滑过渡 */
void gimbal_switch_mode(GimbalMode new_mode)
{
    static GimbalMode current_mode = GIMBAL_MODE_LOCK;

    if (new_mode == current_mode) return;

    /* 重置PID积分，防止切换时突变 */
    pid_reset(&g_pan_pid);
    pid_reset(&g_tilt_pid);

    /* 切换到跟随模式时，初始化跟随目标为当前角度 */
    if (new_mode == GIMBAL_MODE_FOLLOW) {
        g_follow_state.pan_target  = gimbal_get_angle(GIMBAL_CH_PAN);
        g_follow_state.tilt_target = gimbal_get_angle(GIMBAL_CH_TILT);
    }

    /* 切换到锁定模式时，目标角度设为当前角度（平滑过渡） */
    if (new_mode == GIMBAL_MODE_LOCK) {
        /* 目标角度逐渐过渡到0°（在控制循环中实现） */
    }

    current_mode = new_mode;
}
```


---

## 18. 深入原理：无刷电机磁场定向控制（FOC）

### 18.1 无刷电机基础

无刷直流电机（Brushless DC Motor，BLDC）是云台专业应用的核心驱动器。与有刷电机不同，BLDC通过电子换相（Electronic Commutation）代替机械电刷，具有更高效率、更长寿命和更低噪音。

```
无刷电机结构（外转子型，云台常用）：
=================================

         ┌─────────────────────────────┐
         │         外转子（永磁体）      │
         │   N  S  N  S  N  S  N  S   │
         │  ┌──────────────────────┐   │
         │  │    内定子（线圈）     │   │
         │  │   ┌──┐  ┌──┐  ┌──┐  │   │
         │  │   │U │  │V │  │W │  │   │
         │  │   └──┘  └──┘  └──┘  │   │
         │  │    三相绕组（120°间隔）│   │
         │  └──────────────────────┘   │
         └─────────────────────────────┘

三相绕组（U、V、W）通过三相逆变桥驱动：
  ┌──────────────────────────────────────┐
  │  VCC                                 │
  │   │                                  │
  │  [Q1]  [Q3]  [Q5]  ← 上桥臂（高侧）  │
  │   │     │     │                      │
  │   U     V     W    ← 电机三相         │
  │   │     │     │                      │
  │  [Q2]  [Q4]  [Q6]  ← 下桥臂（低侧）  │
  │   │                                  │
  │  GND                                 │
  └──────────────────────────────────────┘

极对数（Pole Pairs）：
  云台电机通常有7~14对极（14~28个磁极）
  极对数越多，转矩越大，但转速越低
  电角度 = 机械角度 × 极对数
```

### 18.2 FOC（磁场定向控制）原理

FOC（Field Oriented Control，磁场定向控制）是控制无刷电机的最优方法，通过将三相电流变换到旋转坐标系（d-q坐标系），实现对转矩和磁通的独立控制。

```
FOC控制框图
===========

目标转矩                                              实际转矩
T_ref ──►[转矩→Iq转换]──► Iq_ref ──►[电流环PI]──► Vq ──►[SVPWM]──► 三相逆变桥 ──► 电机
                                                                                      │
                          Id_ref=0 ──►[电流环PI]──► Vd ──►[SVPWM]                   │
                                                                                      │
                                    ┌──────────────────────────────────────────────┐  │
                                    │  Clarke变换 + Park变换（三相→d-q坐标系）      │◄─┘
                                    │  需要转子位置角θ（来自编码器或无感估算）      │
                                    └──────────────────────────────────────────────┘

坐标变换：
  三相静止坐标系（a-b-c）
       ↓ Clarke变换
  两相静止坐标系（α-β）
       ↓ Park变换（需要转子角度θ）
  两相旋转坐标系（d-q）
    d轴：磁通方向（控制磁通，Id=0可最大化转矩）
    q轴：转矩方向（控制转矩，Iq正比于转矩）
```

**Clarke变换（三相→两相静止）**

```c
/* Clarke变换：将三相电流(Ia, Ib, Ic)转换为两相静止坐标系(Iα, Iβ)
 * 假设三相平衡：Ia + Ib + Ic = 0，因此Ic = -(Ia + Ib)
 */
void clarke_transform(float Ia, float Ib,
                      float *I_alpha, float *I_beta)
{
    /* 标准Clarke变换（等幅值变换） */
    *I_alpha = Ia;
    *I_beta  = (Ia + 2.0f * Ib) / 1.7320508f;  /* 1/√3 */
}
```

**Park变换（两相静止→两相旋转）**

```c
/* Park变换：将静止坐标系(Iα, Iβ)转换为旋转坐标系(Id, Iq)
 * 需要转子电角度θ（由编码器或无感估算提供）
 */
void park_transform(float I_alpha, float I_beta, float theta,
                    float *Id, float *Iq)
{
    float cos_theta = cosf(theta);
    float sin_theta = sinf(theta);

    *Id =  I_alpha * cos_theta + I_beta * sin_theta;
    *Iq = -I_alpha * sin_theta + I_beta * cos_theta;
}

/* 逆Park变换：将(Vd, Vq)转换回静止坐标系(Vα, Vβ) */
void inverse_park_transform(float Vd, float Vq, float theta,
                             float *V_alpha, float *V_beta)
{
    float cos_theta = cosf(theta);
    float sin_theta = sinf(theta);

    *V_alpha = Vd * cos_theta - Vq * sin_theta;
    *V_beta  = Vd * sin_theta + Vq * cos_theta;
}
```

**简化FOC控制循环（适用于云台应用）**

```c
/* foc_gimbal.h - 云台用简化FOC控制器 */
#ifndef FOC_GIMBAL_H
#define FOC_GIMBAL_H

#include "pid.h"
#include <math.h>

/* FOC控制器参数 */
#define FOC_PWM_FREQ_HZ    32000   /* PWM频率32kHz（超声波频率，无噪音） */
#define FOC_CURRENT_KP     0.5f    /* 电流环比例增益 */
#define FOC_CURRENT_KI     100.0f  /* 电流环积分增益 */
#define FOC_POLE_PAIRS     7       /* 极对数（根据实际电机修改） */

typedef struct {
    PID_Controller id_pid;   /* d轴电流PID（目标Id=0） */
    PID_Controller iq_pid;   /* q轴电流PID（目标Iq=转矩指令） */

    float theta_e;           /* 电角度（rad） */
    float theta_m;           /* 机械角度（rad） */

    /* 三相PWM占空比输出（0.0~1.0） */
    float duty_a, duty_b, duty_c;
} FOCController;

void foc_init(FOCController *foc);
void foc_update(FOCController *foc,
                float Ia, float Ib,      /* 相电流（A） */
                float theta_m,           /* 机械角度（rad） */
                float Iq_ref);           /* 目标q轴电流（转矩指令） */

#endif /* FOC_GIMBAL_H */
```

```c
/* foc_gimbal.c */
#include "foc_gimbal.h"
#include <string.h>

void foc_init(FOCController *foc)
{
    memset(foc, 0, sizeof(FOCController));

    /* 电流环PI（注意：电流环不需要D项） */
    pid_init(&foc->id_pid,
             FOC_CURRENT_KP, FOC_CURRENT_KI, 0.0f,
             1.0f, 0.5f, 0.0f);  /* 输出限幅±1.0（归一化电压） */

    pid_init(&foc->iq_pid,
             FOC_CURRENT_KP, FOC_CURRENT_KI, 0.0f,
             1.0f, 0.5f, 0.0f);
}

/**
 * @brief  FOC控制更新（在PWM中断中调用，32kHz）
 * @param  Ia, Ib    相电流（A），Ic由基尔霍夫定律推算
 * @param  theta_m   机械角度（rad），来自编码器
 * @param  Iq_ref    目标q轴电流（转矩指令，A）
 */
void foc_update(FOCController *foc,
                float Ia, float Ib,
                float theta_m,
                float Iq_ref)
{
    const float dt = 1.0f / FOC_PWM_FREQ_HZ;

    /* 1. 计算电角度 */
    foc->theta_m = theta_m;
    foc->theta_e = theta_m * FOC_POLE_PAIRS;

    /* 2. Clarke变换：三相→两相静止 */
    float I_alpha, I_beta;
    clarke_transform(Ia, Ib, &I_alpha, &I_beta);

    /* 3. Park变换：两相静止→两相旋转 */
    float Id_measured, Iq_measured;
    park_transform(I_alpha, I_beta, foc->theta_e,
                   &Id_measured, &Iq_measured);

    /* 4. 电流环PI控制
     * d轴：目标Id=0（最大转矩控制，无磁通弱化）
     * q轴：目标Iq=Iq_ref（转矩控制）
     */
    float Vd = pid_compute(&foc->id_pid, 0.0f, Id_measured, dt);
    float Vq = pid_compute(&foc->iq_pid, Iq_ref, Iq_measured, dt);

    /* 5. 逆Park变换：两相旋转→两相静止 */
    float V_alpha, V_beta;
    inverse_park_transform(Vd, Vq, foc->theta_e, &V_alpha, &V_beta);

    /* 6. SVPWM（空间矢量PWM）生成三相占空比
     * 简化版：使用正弦PWM近似SVPWM
     */
    foc->duty_a = 0.5f + V_alpha;
    foc->duty_b = 0.5f + (-0.5f * V_alpha + 0.8660254f * V_beta);
    foc->duty_c = 0.5f + (-0.5f * V_alpha - 0.8660254f * V_beta);

    /* 限幅到0~1 */
    if (foc->duty_a > 1.0f) foc->duty_a = 1.0f;
    if (foc->duty_a < 0.0f) foc->duty_a = 0.0f;
    if (foc->duty_b > 1.0f) foc->duty_b = 1.0f;
    if (foc->duty_b < 0.0f) foc->duty_b = 0.0f;
    if (foc->duty_c > 1.0f) foc->duty_c = 1.0f;
    if (foc->duty_c < 0.0f) foc->duty_c = 0.0f;

    /* 7. 将占空比写入PWM定时器（由调用者完成） */
}
```

### 18.3 无感FOC：转子位置估算

专业云台电机通常不带编码器（降低成本和重量），需要通过反电动势（Back-EMF）估算转子位置。

```
无感FOC转子位置估算方法：
========================

方法1：反电动势过零检测（简单，低速性能差）
  - 检测三相反电动势的过零点
  - 适用于高速旋转（>100RPM）
  - 低速时反电动势太小，无法可靠检测

方法2：磁通观测器（Flux Observer）
  - 通过积分电压方程估算磁通矢量
  - 从磁通矢量计算转子角度
  - 低速性能好，但需要精确的电机参数

方法3：高频注入（High Frequency Injection）
  - 注入高频信号，通过电感各向异性检测转子位置
  - 适用于零速和低速
  - 计算复杂，需要较强的DSP能力

云台应用推荐：磁通观测器（SimpleBGC使用此方法）

简化磁通观测器：
  λ_α = ∫(Vα - Rs×Iα)dt
  λ_β = ∫(Vβ - Rs×Iβ)dt
  θ_e = atan2(λ_β, λ_α)

其中：
  λ_α, λ_β = 磁通分量
  Vα, Vβ   = 电压分量（由PWM占空比计算）
  Rs        = 定子电阻（需要测量）
  Iα, Iβ   = 电流分量（由Clarke变换得到）
```

### 18.4 振动隔离安装设计

云台的振动隔离（Vibration Isolation）是影响稳定效果的关键机械因素。即使控制算法再好，如果高频振动直接传入IMU，也会导致控制失效。

```
振动传递路径分析：
=================

无人机机架
    │
    │ 高频振动（螺旋桨，10~500Hz）
    ▼
减振球/减振板（第一级隔振）
    │
    │ 低频振动（<10Hz）
    ▼
云台基座
    │
    │ 主动控制补偿
    ▼
云台相机平台（IMU安装位置）

减振效果目标：
  10Hz以上振动衰减 > 20dB（10倍）
  50Hz以上振动衰减 > 40dB（100倍）
```

**减振球选型**

```
减振球（Damping Ball）参数选择：
================================

减振球的固有频率：
  f_n = (1/2π) × √(k/m)

其中：
  k = 减振球刚度（N/m）
  m = 被支撑质量（kg）

设计原则：
  固有频率 f_n 应远低于需要隔离的振动频率
  通常选择 f_n = 5~15Hz（隔离10Hz以上振动）

常用减振球规格：
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 型号          │ 承重（g）    │ 刚度（N/m）  │ 固有频率     │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ 小号（红色）  │ 50~100g      │ 约200 N/m    │ 约7Hz        │
│ 中号（蓝色）  │ 100~200g     │ 约400 N/m    │ 约7Hz        │
│ 大号（黑色）  │ 200~400g     │ 约800 N/m    │ 约7Hz        │
└──────────────┴──────────────┴──────────────┴──────────────┘

选型原则：
  每个减振球承重 = 总重量 / 减振球数量
  通常使用4个减振球，每个承重 = 总重量/4
  选择承重范围覆盖实际承重的减振球型号
```

**减振安装结构设计**

```
减振安装结构（俯视图）：
========================

    无人机机架
    ┌─────────────────────────────┐
    │                             │
    │  ●──────────────────────●  │  ← 减振球安装点（4个）
    │  │                      │  │
    │  │    云台安装板         │  │
    │  │    ┌──────────┐      │  │
    │  │    │  云台基座 │      │  │
    │  │    │  + IMU   │      │  │
    │  │    └──────────┘      │  │
    │  │                      │  │
    │  ●──────────────────────●  │
    │                             │
    └─────────────────────────────┘

减振球安装要点：
1. 四角对称安装，保证重心在减振系统中心
2. 减振球预压缩量约30%（提高线性度）
3. 减振球与安装板之间不能有刚性接触
4. 信号线（IMU、电机线）需要留有足够余量，避免传递振动

IMU安装位置：
  IMU应安装在云台相机平台上（被稳定的一侧）
  不能安装在云台基座上（会感受到未被隔离的振动）
  IMU与安装板之间可以加一层薄泡沫（进一步隔振）
```

**振动测试方法**

```python
# vibration_test.py - 使用MPU6050测量振动频谱
# 在Python主机端运行，通过串口读取MPU6050数据

import serial
import numpy as np
import matplotlib.pyplot as plt

PORT = 'COM3'
BAUD = 115200
SAMPLE_RATE = 100  # Hz
DURATION = 10      # 秒

ser = serial.Serial(PORT, BAUD, timeout=1)
samples = []

print(f"采集{DURATION}秒振动数据...")
for _ in range(SAMPLE_RATE * DURATION):
    line = ser.readline().decode().strip()
    try:
        # 格式：ax,ay,az,gx,gy,gz
        vals = [float(x) for x in line.split(',')]
        samples.append(vals[2])  # az轴加速度
    except:
        pass

# FFT分析
data = np.array(samples)
fft = np.fft.rfft(data)
freqs = np.fft.rfftfreq(len(data), 1.0/SAMPLE_RATE)
magnitude = 20 * np.log10(np.abs(fft) + 1e-10)  # dB

plt.figure(figsize=(10, 4))
plt.plot(freqs, magnitude)
plt.xlabel('频率 (Hz)')
plt.ylabel('幅度 (dB)')
plt.title('云台振动频谱分析')
plt.grid(True)
plt.xlim(0, 50)
plt.show()

# 找出主要振动频率
peak_idx = np.argmax(magnitude[1:]) + 1
print(f"主要振动频率: {freqs[peak_idx]:.1f} Hz")
print(f"振动幅度: {magnitude[peak_idx]:.1f} dB")
```


---

## 19. 完整项目实战：两轴云台自动调平与摇杆控制

### 19.1 项目功能概述

本节实现一个功能完整的两轴云台系统，在原有稳定/追踪模式基础上增加：

1. **自动调平（Auto-Leveling）**：上电后自动将云台调整到水平位置
2. **摇杆手动控制**：通过双轴摇杆（PS2摇杆模块）手动控制云台方向
3. **模式指示**：通过OLED显示屏显示当前模式、角度和PID参数

```
完整系统架构图
==============

                    ┌─────────────────────────────────────────┐
                    │           STM32F103C8T6                  │
                    │                                          │
  MPU6050 ─I2C────►│ 姿态解算  ──►  级联PID  ──►  PWM输出    │──► Pan舵机
                    │                                          │
  摇杆X轴 ─ADC────►│ 摇杆读取  ──►  模式选择  ──►  PWM输出   │──► Tilt舵机
  摇杆Y轴 ─ADC────►│                                          │
  摇杆按键 ─GPIO───►│                                          │
                    │                                          │
  按键1 ─GPIO──────►│ 状态机    ──►  LED控制                  │──► LED红/绿
  按键2 ─GPIO──────►│                                          │
                    │                                          │
  OLED ─I2C────────►│ 显示任务  ──►  状态显示                  │──► OLED屏
                    │                                          │
  调试串口 ─UART───►│ 调试输出                                 │──► PC串口
                    └─────────────────────────────────────────┘

工作模式：
  模式0（稳定）：IMU控制，自动保持水平
  模式1（摇杆）：摇杆控制云台方向，IMU辅助稳定
  模式2（追踪）：OpenMV视觉追踪
  模式3（调平）：上电自动调平序列
```

### 19.2 扩展硬件清单

在原有硬件基础上增加：

| 器件 | 型号/规格 | 数量 | 参考价格 | 说明 |
|------|-----------|------|----------|------|
| 摇杆模块 | PS2双轴摇杆（KY-023） | 1 | ¥5 | X/Y轴模拟输出 + 按键 |
| OLED显示屏 | 0.96寸 128×64 I2C | 1 | ¥12 | 显示状态信息 |
| 按键 | 6×6mm 轻触开关 | 2 | ¥1 | 模式切换（增加一个） |
| 电阻 | 10kΩ | 2 | ¥0.5 | 摇杆按键上拉 |

**摇杆接线**

```
KY-023摇杆模块接线：
  VCC  → 3.3V
  GND  → GND
  VRx  → PA4（ADC1_CH4，X轴）
  VRy  → PA5（ADC1_CH5，Y轴）
  SW   → PA6（GPIO输入，内部上拉，按下=低电平）

摇杆中位电压：约1.65V（3.3V/2）
摇杆范围：0V（最左/最下）~ 3.3V（最右/最上）
ADC分辨率：12位，0~4095
中位ADC值：约2048
```

### 19.3 ADC摇杆读取

```c
/* joystick.h */
#ifndef JOYSTICK_H
#define JOYSTICK_H

#include "stm32f1xx_hal.h"

/* 摇杆死区（中位附近的不灵敏区域） */
#define JOY_DEADBAND    100   /* ADC值，±100/4096 ≈ ±2.4% */
#define JOY_CENTER      2048  /* 12位ADC中位值 */
#define JOY_MAX_SPEED   60.0f /* 摇杆满偏时的最大角速度（°/s） */

typedef struct {
    float x;        /* 归一化X轴，-1.0~+1.0（左负右正） */
    float y;        /* 归一化Y轴，-1.0~+1.0（下负上正） */
    uint8_t btn;    /* 按键状态：1=按下，0=未按 */
} JoystickData;

void joystick_init(void);
void joystick_read(JoystickData *joy);

#endif /* JOYSTICK_H */
```

```c
/* joystick.c */
#include "joystick.h"

ADC_HandleTypeDef hadc1;

void joystick_init(void)
{
    GPIO_InitTypeDef gpio = {0};
    ADC_ChannelConfTypeDef ch = {0};

    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* PA4、PA5配置为模拟输入 */
    gpio.Pin  = GPIO_PIN_4 | GPIO_PIN_5;
    gpio.Mode = GPIO_MODE_ANALOG;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* PA6配置为数字输入（摇杆按键） */
    gpio.Pin  = GPIO_PIN_6;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* ADC1配置 */
    hadc1.Instance                   = ADC1;
    hadc1.Init.ScanConvMode          = ADC_SCAN_DISABLE;
    hadc1.Init.ContinuousConvMode    = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConv      = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign             = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion       = 1;
    HAL_ADC_Init(&hadc1);

    /* ADC校准（STM32F1特有，提高精度） */
    HAL_ADCEx_Calibration_Start(&hadc1);
}

/**
 * @brief  读取摇杆数据
 * @param  joy  输出摇杆数据
 */
void joystick_read(JoystickData *joy)
{
    ADC_ChannelConfTypeDef ch = {0};
    uint32_t raw_x, raw_y;

    /* 读取X轴（PA4，CH4） */
    ch.Channel      = ADC_CHANNEL_4;
    ch.Rank         = 1;
    ch.SamplingTime = ADC_SAMPLETIME_28CYCLES_5;
    HAL_ADC_ConfigChannel(&hadc1, &ch);
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    raw_x = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);

    /* 读取Y轴（PA5，CH5） */
    ch.Channel = ADC_CHANNEL_5;
    HAL_ADC_ConfigChannel(&hadc1, &ch);
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    raw_y = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);

    /* 读取按键 */
    joy->btn = (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_6) == GPIO_PIN_RESET) ? 1 : 0;

    /* 归一化：去除死区，映射到-1.0~+1.0 */
    int32_t dx = (int32_t)raw_x - JOY_CENTER;
    int32_t dy = (int32_t)raw_y - JOY_CENTER;

    /* 死区处理 */
    if (dx > -JOY_DEADBAND && dx < JOY_DEADBAND) dx = 0;
    if (dy > -JOY_DEADBAND && dy < JOY_DEADBAND) dy = 0;

    /* 归一化（死区外线性映射） */
    joy->x = (float)dx / (float)(JOY_CENTER - JOY_DEADBAND);
    joy->y = (float)dy / (float)(JOY_CENTER - JOY_DEADBAND);

    /* 限幅 */
    if (joy->x >  1.0f) joy->x =  1.0f;
    if (joy->x < -1.0f) joy->x = -1.0f;
    if (joy->y >  1.0f) joy->y =  1.0f;
    if (joy->y < -1.0f) joy->y = -1.0f;
}
```

### 19.4 自动调平序列

上电后，云台执行自动调平序列：

```c
/* auto_level.h */
#ifndef AUTO_LEVEL_H
#define AUTO_LEVEL_H

#include "attitude.h"
#include "gimbal_pwm.h"

/* 调平精度要求：误差小于此值视为调平完成 */
#define LEVEL_THRESHOLD_DEG  1.0f

/* 调平超时时间（毫秒） */
#define LEVEL_TIMEOUT_MS     5000

/* 调平控制增益（比例控制） */
#define LEVEL_KP             0.5f

typedef enum {
    LEVEL_IDLE    = 0,  /* 未开始 */
    LEVEL_RUNNING = 1,  /* 调平中 */
    LEVEL_DONE    = 2,  /* 调平完成 */
    LEVEL_TIMEOUT = 3,  /* 超时失败 */
} LevelStatus;

LevelStatus auto_level_run(const Attitude *att, uint32_t elapsed_ms);

#endif /* AUTO_LEVEL_H */
```

```c
/* auto_level.c */
#include "auto_level.h"
#include <math.h>

/**
 * @brief  自动调平控制（每10ms调用一次）
 * @param  att         当前姿态
 * @param  elapsed_ms  已运行时间（毫秒）
 * @retval 调平状态
 *
 * @note   调平策略：
 *         1. 读取当前Roll和Pitch角度
 *         2. 以0°为目标，使用比例控制驱动舵机
 *         3. 当误差小于阈值时，认为调平完成
 *         4. 超过超时时间仍未完成，返回超时状态
 */
LevelStatus auto_level_run(const Attitude *att, uint32_t elapsed_ms)
{
    /* 超时检查 */
    if (elapsed_ms > LEVEL_TIMEOUT_MS) {
        return LEVEL_TIMEOUT;
    }

    /* 计算误差 */
    float roll_error  = 0.0f - att->roll;
    float pitch_error = 0.0f - att->pitch;

    /* 检查是否已调平 */
    if (fabsf(roll_error)  < LEVEL_THRESHOLD_DEG &&
        fabsf(pitch_error) < LEVEL_THRESHOLD_DEG) {
        return LEVEL_DONE;
    }

    /* 比例控制输出 */
    float pan_cmd  = pitch_error * LEVEL_KP;
    float tilt_cmd = roll_error  * LEVEL_KP;

    /* 限幅（调平时使用较小的速度，避免突然跳动） */
    if (pan_cmd  >  20.0f) pan_cmd  =  20.0f;
    if (pan_cmd  < -20.0f) pan_cmd  = -20.0f;
    if (tilt_cmd >  20.0f) tilt_cmd =  20.0f;
    if (tilt_cmd < -20.0f) tilt_cmd = -20.0f;

    /* 输出到舵机 */
    float new_pan  = gimbal_get_angle(GIMBAL_CH_PAN)  + pan_cmd  * 0.01f;
    float new_tilt = gimbal_get_angle(GIMBAL_CH_TILT) + tilt_cmd * 0.01f;
    gimbal_set_angle(GIMBAL_CH_PAN,  new_pan);
    gimbal_set_angle(GIMBAL_CH_TILT, new_tilt);

    return LEVEL_RUNNING;
}
```

### 19.5 摇杆控制模式

摇杆控制模式下，摇杆输入叠加到IMU稳定输出上：

```c
/* joystick_control.c - 摇杆控制模式 */
#include "joystick.h"
#include "attitude.h"
#include "pid.h"
#include "gimbal_pwm.h"

/* 摇杆控制参数 */
#define JOY_RATE_SCALE   30.0f   /* 摇杆满偏对应30°/s的角速度指令 */
#define JOY_SMOOTH_TAU   0.05f   /* 摇杆输入平滑时间常数（50ms） */

static float joy_pan_smooth  = 0.0f;
static float joy_tilt_smooth = 0.0f;

/**
 * @brief  摇杆控制任务（每10ms调用一次）
 * @param  att  当前姿态（用于IMU辅助稳定）
 * @param  pid_pan, pid_tilt  PID控制器
 */
void joystick_control_task(const Attitude *att,
                           PID_Controller *pid_pan,
                           PID_Controller *pid_tilt)
{
    const float dt = 0.01f;
    JoystickData joy;

    /* 读取摇杆 */
    joystick_read(&joy);

    /* 平滑摇杆输入（防止突变） */
    joy_pan_smooth  += (joy.x - joy_pan_smooth)  * (dt / (JOY_SMOOTH_TAU + dt));
    joy_tilt_smooth += (joy.y - joy_tilt_smooth) * (dt / (JOY_SMOOTH_TAU + dt));

    /* 摇杆输入转换为角速度指令（°/s） */
    float pan_rate_cmd  = joy_pan_smooth  * JOY_RATE_SCALE;
    float tilt_rate_cmd = joy_tilt_smooth * JOY_RATE_SCALE;

    /* 当前角度 */
    float pan_now  = gimbal_get_angle(GIMBAL_CH_PAN);
    float tilt_now = gimbal_get_angle(GIMBAL_CH_TILT);

    /* 摇杆控制：直接积分角速度指令得到目标角度 */
    float pan_target  = pan_now  + pan_rate_cmd  * dt;
    float tilt_target = tilt_now + tilt_rate_cmd * dt;

    /* IMU辅助稳定：当摇杆无输入时，PID保持当前角度 */
    float pan_pid_out  = 0.0f;
    float tilt_pid_out = 0.0f;

    if (fabsf(joy_pan_smooth) < 0.05f) {
        /* 摇杆无输入：PID稳定当前角度 */
        pan_pid_out = pid_compute(pid_pan, pan_now, att->pitch, dt);
    } else {
        /* 摇杆有输入：重置PID积分，跟随摇杆 */
        pid_reset(pid_pan);
        pan_pid_out = 0.0f;
    }

    if (fabsf(joy_tilt_smooth) < 0.05f) {
        tilt_pid_out = pid_compute(pid_tilt, tilt_now, att->roll, dt);
    } else {
        pid_reset(pid_tilt);
        tilt_pid_out = 0.0f;
    }

    /* 合并摇杆指令和PID输出 */
    float final_pan  = pan_target  + pan_pid_out;
    float final_tilt = tilt_target + tilt_pid_out;

    gimbal_set_angle(GIMBAL_CH_PAN,  final_pan);
    gimbal_set_angle(GIMBAL_CH_TILT, final_tilt);
}
```

### 19.6 OLED状态显示

使用SSD1306 OLED显示屏（128×64，I2C接口）显示系统状态：

```c
/* oled_display.h */
#ifndef OLED_DISPLAY_H
#define OLED_DISPLAY_H

#include "stm32f1xx_hal.h"
#include "attitude.h"
#include "gimbal_fsm.h"

/* SSD1306 I2C地址 */
#define SSD1306_ADDR  0x3C

void oled_init(void);
void oled_clear(void);
void oled_show_status(const Attitude *att,
                      GimbalState state,
                      float pan_angle,
                      float tilt_angle);

#endif /* OLED_DISPLAY_H */
```

```c
/* oled_display.c - SSD1306 OLED显示（简化版） */
#include "oled_display.h"
#include <stdio.h>
#include <string.h>

extern I2C_HandleTypeDef hi2c1;

/* SSD1306初始化命令序列 */
static const uint8_t ssd1306_init_cmds[] = {
    0xAE,        /* 关闭显示 */
    0xD5, 0x80,  /* 设置时钟分频 */
    0xA8, 0x3F,  /* 设置多路复用比（64行） */
    0xD3, 0x00,  /* 设置显示偏移 */
    0x40,        /* 设置起始行 */
    0x8D, 0x14,  /* 使能电荷泵 */
    0x20, 0x00,  /* 水平寻址模式 */
    0xA1,        /* 列地址映射（左右翻转） */
    0xC8,        /* 行扫描方向（上下翻转） */
    0xDA, 0x12,  /* COM引脚配置 */
    0x81, 0xCF,  /* 设置对比度 */
    0xD9, 0xF1,  /* 预充电周期 */
    0xDB, 0x40,  /* VCOMH电压 */
    0xA4,        /* 全局显示开启（跟随RAM） */
    0xA6,        /* 正常显示（非反色） */
    0xAF,        /* 开启显示 */
};

static void oled_send_cmd(uint8_t cmd)
{
    uint8_t buf[2] = {0x00, cmd};  /* 0x00 = 命令模式 */
    HAL_I2C_Master_Transmit(&hi2c1, SSD1306_ADDR << 1, buf, 2, 10);
}

void oled_init(void)
{
    HAL_Delay(100);  /* 等待OLED上电稳定 */
    for (size_t i = 0; i < sizeof(ssd1306_init_cmds); i++) {
        oled_send_cmd(ssd1306_init_cmds[i]);
    }
    oled_clear();
}

void oled_clear(void)
{
    /* 设置全屏地址范围 */
    oled_send_cmd(0x21); oled_send_cmd(0); oled_send_cmd(127);  /* 列0~127 */
    oled_send_cmd(0x22); oled_send_cmd(0); oled_send_cmd(7);    /* 页0~7 */

    /* 发送全零数据（清屏） */
    uint8_t buf[129];
    buf[0] = 0x40;  /* 数据模式 */
    memset(&buf[1], 0, 128);
    for (int page = 0; page < 8; page++) {
        HAL_I2C_Master_Transmit(&hi2c1, SSD1306_ADDR << 1, buf, 129, 50);
    }
}

/**
 * @brief  显示云台状态信息
 * @note   使用简单的字符显示（需要字库，此处为示意）
 *         实际项目中可使用u8g2库简化显示代码
 */
void oled_show_status(const Attitude *att,
                      GimbalState state,
                      float pan_angle,
                      float tilt_angle)
{
    char line[32];

    /* 第1行：模式 */
    const char *mode_names[] = {"INIT", "STAB", "SWITCH", "TRACK", "ERR"};
    snprintf(line, sizeof(line), "Mode: %s",
             (state < 5) ? mode_names[state] : "???");
    /* oled_draw_string(0, 0, line); */  /* 需要字库实现 */

    /* 第2行：Roll/Pitch */
    snprintf(line, sizeof(line), "R:%.1f P:%.1f",
             att->roll, att->pitch);
    /* oled_draw_string(0, 2, line); */

    /* 第3行：Pan/Tilt角度 */
    snprintf(line, sizeof(line), "Pan:%.1f Tilt:%.1f",
             pan_angle, tilt_angle);
    /* oled_draw_string(0, 4, line); */

    /* 实际项目推荐使用u8g2库：
     * u8g2_ClearBuffer(&u8g2);
     * u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);
     * u8g2_DrawStr(&u8g2, 0, 10, line);
     * u8g2_SendBuffer(&u8g2);
     */
}
```

### 19.7 完整项目测试流程

```
测试步骤：
==========

步骤1：硬件验证
  □ 用万用表测量5V和3.3V电源电压（误差<±5%）
  □ 用示波器测量PWM信号（周期20ms，脉宽500~2500μs）
  □ 串口输出"MPU6050 OK"（验证I2C通信）
  □ 串口输出校准数据（陀螺仪零偏<0.5°/s）

步骤2：自动调平测试
  □ 将云台倾斜30°，上电
  □ 观察云台是否在5秒内回到水平（误差<1°）
  □ 串口输出"Auto-level DONE"

步骤3：稳定模式测试
  □ 手动快速倾斜云台，观察舵机是否快速补偿
  □ 用手机水平仪APP测量摄像头平台角度
  □ 在1Hz、5°幅度正弦扰动下，输出角度应<0.5°

步骤4：摇杆控制测试
  □ 切换到摇杆模式（按键2）
  □ 推动摇杆，云台应平滑跟随
  □ 松开摇杆，云台应保持当前角度（IMU稳定）
  □ 摇杆满偏时，角速度应约30°/s

步骤5：视觉追踪测试
  □ 切换到追踪模式（按键1）
  □ 将红色目标放在画面中，云台应追踪目标
  □ 目标丢失后，云台应在500ms内开始缓慢回中

步骤6：综合测试
  □ 在运动中（手持云台走动）测试稳定效果
  □ 录制视频，对比有无稳定的画面抖动差异
  □ 连续运行30分钟，检查舵机温度（<60°C）
```


---

## 20. 常见问题深度排查

### 20.1 振荡（Oscillation）

振荡是云台调试中最常见的问题，表现为舵机来回抖动，无法稳定。

```
振荡诊断流程图
==============

                    云台振荡
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      高频振荡        低频振荡      间歇振荡
    （>5Hz抖动）    （<2Hz摆动）  （偶发振荡）
          │             │             │
          ▼             ▼             ▼
    可能原因：        可能原因：    可能原因：
    - Kp过大         - Ki过大      - 积分饱和
    - Kd过大         - 机械共振    - 模式切换突变
    - 传感器噪声     - 负载变化    - 电源电压波动
    - 控制频率低     - 摩擦力非线性
```

**高频振荡（>5Hz）排查**

```c
/* 排查步骤1：降低Kp */
/* 将Kp减小到原来的50%，观察振荡是否消失 */
pid_set_params(&g_pan_pid, g_pan_pid.kp * 0.5f,
               g_pan_pid.ki, g_pan_pid.kd);

/* 排查步骤2：增大微分滤波时间常数 */
/* 如果Kd引起高频抖动，增大滤波时间常数 */
#define DERIV_FILTER_TAU_NEW  0.1f  /* 从0.05增大到0.1 */

/* 排查步骤3：检查控制频率 */
/* 确认TIM3中断确实在100Hz运行 */
void check_control_frequency(void)
{
    static uint32_t last_tick = 0;
    static uint32_t count = 0;
    count++;
    if (count >= 100) {
        uint32_t elapsed = HAL_GetTick() - last_tick;
        /* elapsed应约为1000ms（100次×10ms） */
        printf("Control freq: %.1f Hz\r\n", 100000.0f / elapsed);
        last_tick = HAL_GetTick();
        count = 0;
    }
}

/* 排查步骤4：检查传感器噪声 */
/* 静止时输出IMU数据，观察噪声水平 */
void check_imu_noise(void)
{
    MPU6050_Data imu;
    mpu6050_read_calibrated(&imu, &g_imu_offset);
    /* 正常：gx/gy/gz噪声 < ±0.5°/s */
    printf("gx=%.3f gy=%.3f gz=%.3f\r\n", imu.gx, imu.gy, imu.gz);
}
```

**低频振荡（<2Hz）排查**

```
低频振荡通常由积分项引起（积分饱和或Ki过大）：

诊断方法：
1. 将Ki设为0，观察振荡是否消失
   - 消失：Ki过大，减小Ki到原来的30%
   - 未消失：不是积分问题，检查机械共振

2. 检查积分限幅是否合理
   - integral_limit应约为output_limit的30%~50%
   - 如果integral_limit过大，积分项会主导输出

3. 检查机械共振
   - 用手指轻弹云台支架，观察是否有明显共振
   - 如果有共振，加固支架或增加阻尼材料

修复方案：
  Ki过大：减小Ki，或增大积分限幅
  机械共振：加固结构，或在共振频率处加陷波滤波器
```

**陷波滤波器（Notch Filter）消除机械共振**

```c
/* 二阶陷波滤波器（消除特定频率的振荡）
 * 用于消除机械共振引起的振荡
 */
typedef struct {
    float b0, b1, b2;  /* 分子系数 */
    float a1, a2;      /* 分母系数 */
    float x1, x2;      /* 输入历史 */
    float y1, y2;      /* 输出历史 */
} NotchFilter;

/**
 * @brief  初始化陷波滤波器
 * @param  f_notch  陷波频率（Hz）
 * @param  Q        品质因数（越大陷波越窄，典型值2~10）
 * @param  fs       采样频率（Hz）
 */
void notch_filter_init(NotchFilter *nf, float f_notch, float Q, float fs)
{
    float omega = 2.0f * 3.14159265f * f_notch / fs;
    float alpha = sinf(omega) / (2.0f * Q);

    nf->b0 =  1.0f;
    nf->b1 = -2.0f * cosf(omega);
    nf->b2 =  1.0f;
    float a0 = 1.0f + alpha;
    nf->a1 = -2.0f * cosf(omega) / a0;
    nf->a2 = (1.0f - alpha) / a0;
    nf->b0 /= a0;
    nf->b1 /= a0;
    nf->b2 /= a0;

    nf->x1 = nf->x2 = nf->y1 = nf->y2 = 0.0f;
}

float notch_filter_update(NotchFilter *nf, float x)
{
    float y = nf->b0*x + nf->b1*nf->x1 + nf->b2*nf->x2
              - nf->a1*nf->y1 - nf->a2*nf->y2;
    nf->x2 = nf->x1; nf->x1 = x;
    nf->y2 = nf->y1; nf->y1 = y;
    return y;
}

/* 使用示例：消除15Hz机械共振 */
/* NotchFilter nf;
 * notch_filter_init(&nf, 15.0f, 5.0f, 100.0f);
 * float filtered_output = notch_filter_update(&nf, pid_output);
 */
```

### 20.2 姿态漂移（Drift）

**现象**：云台静止时，Roll/Pitch角度缓慢漂移，导致摄像头逐渐偏离水平。

```
漂移原因分析：
=============

原因1：陀螺仪零偏未校准（最常见）
  症状：漂移速度恒定（约0.1~1°/s）
  验证：将云台固定，观察30秒内漂移量
  修复：重新执行零偏校准（确保静止5秒以上）

原因2：互补滤波α值过大
  症状：漂移速度随温度变化
  验证：α=0.98时，漂移约0.3Hz以下的低频变化
  修复：减小α（如0.95），增大加速度计权重

原因3：温度漂移
  症状：刚上电时漂移快，稳定后漂移慢
  原因：陀螺仪零偏随温度变化（MPU6050约0.02°/s/°C）
  修复：上电后等待2~3分钟让传感器温度稳定再校准

原因4：振动引起的加速度计误差
  症状：在振动环境中漂移加剧
  修复：增大互补滤波α值（减小加速度计权重）
        或在加速度计数据上加低通滤波
```

**漂移量化测试**

```c
/* 漂移测试：固定云台，记录1分钟内的角度变化 */
void drift_test(void)
{
    Attitude att_start, att_now;
    MPU6050_Data imu;
    MPU6050_Offset offset = {0};

    /* 校准 */
    mpu6050_calibrate(&offset, 500);
    attitude_init(&att_start);

    /* 运行1分钟 */
    for (int i = 0; i < 6000; i++) {  /* 6000 × 10ms = 60s */
        mpu6050_read_calibrated(&imu, &offset);
        complementary_filter(&att_start, &imu, 0.01f);
        HAL_Delay(10);
    }

    /* 输出漂移量 */
    printf("1分钟漂移：Roll=%.2f° Pitch=%.2f°\r\n",
           att_start.roll, att_start.pitch);
    /* 正常：< 2°/分钟 */
}
```

### 20.3 万向节死锁（Gimbal Lock）

万向节死锁（Gimbal Lock）是欧拉角表示法的固有问题，当某个轴旋转90°时，另外两个轴会重合，导致失去一个自由度。

```
万向节死锁示意：
================

正常状态（Pitch=0°）：
  Roll轴（X）─────────────────────────────────
  Pitch轴（Y）─────────────────────────────────
  Yaw轴（Z）  ─────────────────────────────────
  三轴独立，可以表示任意姿态

死锁状态（Pitch=90°，摄像头朝上）：
  Roll轴（X）─────────────────────────────────
  Pitch轴（Y）已旋转90°，与Yaw轴重合！
  Yaw轴（Z）  ─────────────────────────────────
  Roll和Yaw变成同一个轴，失去一个自由度

后果：
  在Pitch=90°附近，Roll和Yaw的控制会相互干扰
  云台可能出现不可预期的旋转
```

**解决方案**

```c
/* 方案1：限制Tilt轴角度范围，避免接近90° */
#define TILT_ANGLE_MIN  -80.0f  /* 不允许超过±80°，留10°余量 */
#define TILT_ANGLE_MAX   80.0f

/* 方案2：使用四元数表示姿态（根本解决方案）
 * 四元数没有万向节死锁问题
 * 但计算更复杂，需要Mahony或Madgwick滤波器
 */

/* 方案3：检测接近死锁状态并发出警告 */
void check_gimbal_lock(const Attitude *att)
{
    if (fabsf(att->pitch) > 75.0f) {
        /* 接近死锁区域，发出警告 */
        printf("WARNING: Approaching gimbal lock! Pitch=%.1f°\r\n",
               att->pitch);
        /* 可以在此处限制Pan轴运动，防止死锁 */
    }
}

/* 方案4：四元数转欧拉角时的奇异点处理 */
void quaternion_to_euler_safe(float q0, float q1, float q2, float q3,
                               float *roll, float *pitch, float *yaw)
{
    /* 计算sin(pitch) */
    float sinp = 2.0f * (q0*q2 - q3*q1);

    /* 检测奇异点（|sinp| ≈ 1） */
    if (fabsf(sinp) >= 0.9999f) {
        /* 万向节死锁：Pitch = ±90° */
        *pitch = copysignf(90.0f, sinp);
        *roll  = 0.0f;  /* Roll设为0（任意值，因为Roll和Yaw重合）*/
        *yaw   = atan2f(2.0f*(q0*q3 + q1*q2),
                        1.0f - 2.0f*(q2*q2 + q3*q3)) * (180.0f/3.14159265f);
    } else {
        *pitch = asinf(sinp) * (180.0f/3.14159265f);
        *roll  = atan2f(2.0f*(q0*q1 + q2*q3),
                        1.0f - 2.0f*(q1*q1 + q2*q2)) * (180.0f/3.14159265f);
        *yaw   = atan2f(2.0f*(q0*q3 + q1*q2),
                        1.0f - 2.0f*(q2*q2 + q3*q3)) * (180.0f/3.14159265f);
    }
}
```

### 20.4 电机齿槽效应（Motor Cogging）

齿槽效应（Cogging）是无刷电机特有的问题，表现为电机在低速旋转时出现周期性的阻力，导致云台运动不平滑。

```
齿槽效应原理：
=============

无刷电机定子铁芯有槽（Slot），转子永磁体在旋转时
会被铁芯槽吸引，产生周期性的齿槽转矩（Cogging Torque）

齿槽转矩特性：
  - 周期：每转 = 极数 × 槽数 次
  - 幅度：约为额定转矩的1%~5%
  - 影响：低速时明显，高速时被惯性平滑

对云台的影响：
  - 云台缓慢运动时出现"卡顿"感
  - 追踪慢速目标时，运动不平滑
  - 在某些角度位置，云台有"吸附"感
```

**齿槽效应补偿**

```c
/* 齿槽效应补偿（前馈补偿）
 * 通过预先测量齿槽转矩曲线，在控制输出中加入补偿
 */

/* 齿槽转矩查找表（需要实测标定）
 * 每个电机不同，需要单独标定
 * 表中存储每个电角度对应的补偿量
 */
#define COGGING_TABLE_SIZE  360  /* 每度一个采样点 */
static float cogging_table[COGGING_TABLE_SIZE] = {0};  /* 初始全零 */

/**
 * @brief  标定齿槽转矩（需要在无负载条件下进行）
 * @note   以恒定低速旋转电机，记录每个角度需要的额外电流
 *         这个额外电流就是齿槽转矩的补偿量
 */
void cogging_calibrate(void)
{
    /* 以极低速度（约1RPM）旋转电机一圈
     * 记录每个角度位置的PID输出（即克服齿槽所需的电流）
     * 将这些值存入cogging_table
     */
    printf("Cogging calibration: rotate motor slowly one full turn...\r\n");
    /* 实际标定代码需要根据具体硬件实现 */
}

/**
 * @brief  获取当前角度的齿槽补偿量
 * @param  theta_e  电角度（度，0~360）
 * @retval 补偿量（叠加到控制输出）
 */
float cogging_get_compensation(float theta_e)
{
    /* 归一化到0~360 */
    while (theta_e < 0.0f)    theta_e += 360.0f;
    while (theta_e >= 360.0f) theta_e -= 360.0f;

    int idx = (int)theta_e;
    float frac = theta_e - idx;

    /* 线性插值 */
    float c0 = cogging_table[idx];
    float c1 = cogging_table[(idx + 1) % COGGING_TABLE_SIZE];
    return c0 + frac * (c1 - c0);
}
```

**软件层面的齿槽效应缓解**

```c
/* 方法1：增大控制带宽（提高控制频率）
 * 更高的控制频率可以更快地响应齿槽扰动
 * 从100Hz提高到400Hz（需要SPI接口的IMU）
 */

/* 方法2：在PID输出上加低通滤波（平滑运动）
 * 牺牲一些响应速度，换取更平滑的运动
 */
static float output_smooth = 0.0f;
#define OUTPUT_SMOOTH_TAU  0.02f  /* 20ms平滑时间常数 */

float smooth_output(float raw_output, float dt)
{
    output_smooth += (raw_output - output_smooth) *
                     (dt / (OUTPUT_SMOOTH_TAU + dt));
    return output_smooth;
}

/* 方法3：选用低齿槽效应的电机
 * 无槽电机（Slotless Motor）：无铁芯，齿槽效应极小
 * 但效率略低，成本更高
 * 代表产品：T-Motor AK系列、Maxon EC系列
 */
```

### 20.5 其他常见问题速查表

```
问题速查表
==========

┌──────────────────────┬──────────────────────────┬──────────────────────────┐
│ 现象                  │ 可能原因                  │ 解决方案                  │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 上电后舵机突然跳动    │ 初始PWM值不正确           │ 确保上电时输出中位脉宽    │
│                      │ 软启动未实现              │ 实现软启动（逐渐增大输出）│
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 舵机发热严重          │ 负载过重                  │ 检查云台重量，减轻负载    │
│                      │ PID振荡导致持续运动       │ 调整PID参数消除振荡       │
│                      │ 死区太小，频繁微调        │ 增大死区阈值              │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ I2C通信失败           │ 上拉电阻缺失              │ 添加4.7kΩ上拉电阻        │
│                      │ 走线过长（>30cm）         │ 缩短I2C走线              │
│                      │ 地线连接不良              │ 检查GND连接              │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 视觉追踪延迟大        │ OpenMV帧率低              │ 降低图像分辨率（QQVGA）  │
│                      │ 串口波特率低              │ 提高波特率到230400        │
│                      │ 颜色阈值不准确            │ 重新标定颜色阈值          │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 模式切换时云台跳动    │ 切换时PID积分未清零       │ 切换前调用pid_reset()    │
│                      │ 目标角度突变              │ 实现平滑过渡              │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 电源电压不稳定        │ 舵机启动冲击电流          │ 增大滤波电容（1000μF）   │
│                      │ 导线过细                  │ 使用≥0.5mm²导线         │
├──────────────────────┼──────────────────────────┼──────────────────────────┤
│ 角度控制不准确        │ 舵机个体差异              │ 单独标定每个舵机的脉宽    │
│                      │ 机械安装偏差              │ 调整安装角度或软件补偿    │
└──────────────────────┴──────────────────────────┴──────────────────────────┘
```

---

## 21. 测试与验证

### 21.1 单元测试：PID控制器验证

```c
/* test_pid.c - PID控制器单元测试 */
#include "pid.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

/* 测试1：纯P控制，验证比例响应 */
void test_pid_proportional(void)
{
    PID_Controller pid;
    pid_init(&pid, 2.0f, 0.0f, 0.0f, 100.0f, 50.0f, 0.0f);

    /* 误差=10°，Kp=2，期望输出=20° */
    float output = pid_compute(&pid, 10.0f, 0.0f, 0.01f);
    assert(fabsf(output - 20.0f) < 0.001f);
    printf("Test 1 PASS: P control output=%.3f (expected 20.0)\r\n", output);
}

/* 测试2：积分限幅验证 */
void test_pid_integral_limit(void)
{
    PID_Controller pid;
    pid_init(&pid, 0.0f, 1.0f, 0.0f, 100.0f, 10.0f, 0.0f);

    /* 持续误差=1°，积分应被限制在10° */
    float output = 0.0f;
    for (int i = 0; i < 1000; i++) {
        output = pid_compute(&pid, 1.0f, 0.0f, 0.01f);
    }
    /* 积分限幅=10，Ki=1，输出应≤10 */
    assert(output <= 10.0f + 0.001f);
    printf("Test 2 PASS: Integral limit output=%.3f (expected ≤10.0)\r\n", output);
}

/* 测试3：输出限幅验证 */
void test_pid_output_limit(void)
{
    PID_Controller pid;
    pid_init(&pid, 10.0f, 0.0f, 0.0f, 45.0f, 20.0f, 0.0f);

    /* 大误差，输出应被限制在45° */
    float output = pid_compute(&pid, 100.0f, 0.0f, 0.01f);
    assert(fabsf(output) <= 45.0f + 0.001f);
    printf("Test 3 PASS: Output limit output=%.3f (expected ≤45.0)\r\n", output);
}

/* 测试4：重置功能验证 */
void test_pid_reset(void)
{
    PID_Controller pid;
    pid_init(&pid, 1.0f, 1.0f, 0.0f, 100.0f, 50.0f, 0.0f);

    /* 积累一些积分 */
    for (int i = 0; i < 100; i++) {
        pid_compute(&pid, 1.0f, 0.0f, 0.01f);
    }
    assert(pid.integral != 0.0f);

    /* 重置后积分应为0 */
    pid_reset(&pid);
    assert(pid.integral == 0.0f);
    assert(pid.last_error == 0.0f);
    printf("Test 4 PASS: PID reset successful\r\n");
}

void run_all_pid_tests(void)
{
    printf("=== PID Controller Unit Tests ===\r\n");
    test_pid_proportional();
    test_pid_integral_limit();
    test_pid_output_limit();
    test_pid_reset();
    printf("All tests PASSED!\r\n");
}
```

### 21.2 系统集成测试

```c
/* 系统集成测试：验证完整控制链路 */
void integration_test_stabilize(void)
{
    printf("=== Stabilize Mode Integration Test ===\r\n");

    /* 初始化所有模块 */
    gimbal_pwm_init();
    mpu6050_init();
    mpu6050_calibrate(&g_calibration, 200);
    stabilize_init();

    /* 运行10秒，记录最大误差 */
    float max_roll_error  = 0.0f;
    float max_pitch_error = 0.0f;
    Attitude att = {0};
    MPU6050_Data imu;

    for (int i = 0; i < 1000; i++) {
        mpu6050_read_calibrated(&imu, &g_calibration);
        complementary_filter(&att, &imu, 0.01f);

        float roll_err  = fabsf(att.roll);
        float pitch_err = fabsf(att.pitch);
        if (roll_err  > max_roll_error)  max_roll_error  = roll_err;
        if (pitch_err > max_pitch_error) max_pitch_error = pitch_err;

        HAL_Delay(10);
    }

    printf("Max Roll error:  %.2f° (target: <2°)\r\n", max_roll_error);
    printf("Max Pitch error: %.2f° (target: <2°)\r\n", max_pitch_error);

    if (max_roll_error < 2.0f && max_pitch_error < 2.0f) {
        printf("Integration test PASSED!\r\n");
    } else {
        printf("Integration test FAILED! Check PID parameters.\r\n");
    }
}
```

---

## 22. 延伸阅读

- [舵机控制基础](../beginner/03-servo-motor-control.html) — 舵机PWM控制原理、角度映射、多舵机控制
- [PID控制算法](../intermediate/03-pid-control.html) — PID理论、离散化、参数整定方法
- [四自由度机械臂](05-robot-arm-project.html) — 更复杂的多舵机协调控制系统
- [六足机器人](06-hexapod-robot.html) — 18舵机协调控制、步态规划
- [运动控制算法](02-motion-control-algorithms.html) — 梯形/S曲线加速度、步进电机控制
<!-- 以下链接指向的文件不存在，待补充后取消注释
- [I2C通信协议](../../03-communication-protocols/i2c-protocol.html) — I2C时序、多设备总线、常见问题
-->

---

## 23. 参考资料

1. **MG996R Datasheet** — Tower Pro，舵机电气特性和机械规格
2. **MPU-6000/MPU-6050 Product Specification** — InvenSense，寄存器映射和通信协议
3. **STM32F103xx Reference Manual** — STMicroelectronics，定时器、I2C、UART详细说明
4. **《PID控制器设计与调参》** — 陶永华，PID理论和工程整定方法
5. **《四旋翼飞行器设计与控制》** — 全权，姿态解算和控制算法
6. **Mahony, R. et al.** — "Nonlinear Complementary Filters on the Special Orthogonal Group"，IEEE TAC 2008
7. **OpenMV官方文档** — [docs.openmv.io](https://docs.openmv.io/)，视觉追踪API参考
8. **STM32 HAL库用户手册** — UM1850，HAL API详细说明
9. **SimpleBGC Serial API** — Basecam Electronics，串口控制协议文档
10. **Storm32 BGC Wiki** — [olliw42.github.io](https://olliw42.github.io/storm32bgc-wiki/)，开源云台控制器文档
11. **《无刷电机FOC控制原理》** — 德州仪器应用笔记SPRABQ7，磁场定向控制详解
12. **Betz, R.E.** — "Introduction to Field Oriented Control of Induction Motors"，Newcastle大学讲义
