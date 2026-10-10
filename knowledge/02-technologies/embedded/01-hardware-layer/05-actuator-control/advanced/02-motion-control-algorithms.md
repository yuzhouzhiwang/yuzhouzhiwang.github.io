---
title: "运动控制算法：梯形加减速与S曲线规划"
description: "深入讲解步进电机和伺服电机的运动规划算法，涵盖梯形速度曲线、S曲线加减速、实时插补原理、步进电机物理特性、微步进技术、失步检测与闭环控制，以及完整CNC单轴控制器项目实战"
slug: "motion-control-algorithms"

domain: "底层硬件层"
module: "执行器控制"
content_type: "article"
skill_level: "advanced"

tags:
  - 运动控制
  - 梯形加减速
  - S曲线
  - 运动规划
  - 步进电机
  - 插补算法
  - 微步进
  - DRV8825
  - 失步检测
  - 闭环控制
prerequisites:
  - "beginner/02-stepper-motor-control"
  - "intermediate/03-pid-control"
  - "intermediate/04-encoder-interface"
related_contents:
  - "advanced/03-multi-axis-sync"
  - "advanced/01-smart-car-control"
  - "advanced/04-smart-gimbal-project"
  - "advanced/05-robot-arm-project"

estimated_time: 180
difficulty_score: 5

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
  - 运动控制算法
  - 梯形速度曲线
  - S曲线加减速
  - 步进电机加速
  - 运动规划
cover_image: ""
---

# 运动控制算法：梯形加减速与S曲线规划

## 概述

直接以最高速度启动步进电机会导致失步（丢步），必须通过加减速算法平滑地改变速度。运动控制算法的核心是：**在给定起点、终点、最大速度和加速度的约束下，生成一条平滑的速度-时间曲线，并实时转换为脉冲序列输出给电机驱动器**。

本文从步进电机的物理特性出发，系统讲解梯形加减速、S曲线规划、微步进技术、失步检测与闭环控制，最终以完整的CNC单轴控制器项目收尾。

**学习目标**：

| 目标 | 技能点 |
|------|--------|
| 理解步进电机物理特性 | 保持转矩、齿槽转矩、共振机理 |
| 掌握梯形加减速 | 三段结构、定时器中断实现 |
| 掌握S曲线规划 | 七段结构、Jerk限制推导 |
| 实现微步进控制 | DRV8825配置、电流波形整形 |
| 实现失步检测 | 反电动势检测、编码器闭环 |
| 完成完整项目 | CNC单轴控制器、限位开关、回零 |

**前置知识**：
- 步进电机基础驱动（全步/半步）
- STM32定时器中断
- PID控制基础
- 编码器接口（可选，用于闭环章节）

## 背景知识

### 步进电机物理特性

#### 基本工作原理

步进电机（Stepper Motor）是一种将电脉冲信号转换为角位移的机电元件。每接收一个脉冲，转子旋转固定角度（步距角）。常见步距角为1.8°（200步/转）和0.9°（400步/转）。

```
步进电机内部结构（两相混合式）：

        定子（Stator）
    ┌───────────────────┐
    │  N  ┌─────┐  S   │
    │     │转子 │      │
    │  S  │(磁铁)│  N   │
    │     └─────┘      │
    │  线圈A    线圈B   │
    └───────────────────┘

两相四线：A+, A-, B+, B-
全步序列：AB → A̅B → A̅B̅ → AB̅ → AB
```

#### 保持转矩（Holding Torque）

保持转矩是电机通电但不旋转时，能抵抗外力的最大转矩。这是步进电机最重要的静态参数。

```
保持转矩 T_hold = N_r × Φ × I × sin(θ_e)

其中：
  N_r  = 转子齿数
  Φ    = 每极磁通量 (Wb)
  I    = 绕组电流 (A)
  θ_e  = 电气角偏差

实际意义：
  T_hold 与电流成正比
  额定电流下的保持转矩见数据手册
  例：NEMA17 17HS4401 = 0.4 N·m @ 1.7A
```

**保持转矩 vs 运行转矩**：

```
转矩 (N·m)
  │
  │  ████████████████  ← 保持转矩 (100%)
  │  ████████████       ← 低速运行转矩 (~80%)
  │  ████████            ← 中速运行转矩 (~60%)
  │  ████                ← 高速运行转矩 (~30%)
  │  ██                  ← 极高速转矩 (~10%)
  └──────────────────────── 速度 (steps/s)
     0   500  1000  2000  5000
```

> 关键结论：步进电机高速时转矩急剧下降，这是加减速算法存在的根本原因。

#### 齿槽转矩（Detent Torque / Cogging Torque）

齿槽转矩是电机**断电**时，由转子永磁体与定子齿槽相互作用产生的周期性转矩。

```
齿槽转矩特性：
  - 大小：约为保持转矩的5~20%
  - 周期：每个齿槽一个周期
  - 影响：低速运动不平滑，产生振动

齿槽转矩 T_cog = T_hold × k_cog × sin(N_r × θ_m)

其中 k_cog ≈ 0.05~0.20，θ_m 为机械角
```

**减小齿槽转矩的方法**：
1. 使用微步进（Microstepping）——最有效
2. 选择斜槽（Skewed Slot）设计的电机
3. 提高运行速度（高速时齿槽效应相对减弱）

#### 共振与中频失速

步进电机在特定速度范围内会发生共振（Resonance），表现为振动加剧、噪声增大，严重时失步。

```
共振机理：
  步进电机转子是一个弹簧-质量系统
  固有频率 f_n = (1/2π) × √(K_s / J)
  
  其中：
    K_s = 弹簧刚度（由保持转矩决定）
    J   = 转动惯量（转子+负载）

  当步进频率 = f_n 时，发生共振

典型共振区：
  ┌─────────────────────────────────────────┐
  │ 速度 (steps/s)  │ 现象                  │
  ├─────────────────┼───────────────────────┤
  │ 50~200          │ 低频共振（最严重）     │
  │ 500~1000        │ 中频共振              │
  │ 2000~5000       │ 高频共振（较轻微）    │
  └─────────────────┴───────────────────────┘
```

**抑制共振的方法**：

```c
// 方法1：快速通过共振区（加速度足够大）
// 方法2：使用微步进（减小步距角，提高固有频率）
// 方法3：添加阻尼（机械阻尼器或电气阻尼）
// 方法4：共振频率避让（在速度规划中跳过共振区）

// 共振区速度跳跃示例
void motion_plan_with_resonance_skip(uint32_t steps, float v_max) {
    // 定义共振区
    const float RESONANCE_LOW  = 150.0f;  // steps/s
    const float RESONANCE_HIGH = 250.0f;  // steps/s
    
    if (v_max > RESONANCE_LOW && v_max < RESONANCE_HIGH) {
        // 目标速度在共振区内，提高到共振区上方
        v_max = RESONANCE_HIGH + 50.0f;
    }
    
    // 加速时快速通过共振区
    // 使用较大加速度确保在共振区停留时间最短
    float accel = (v_max > RESONANCE_HIGH) ? v_max * 15.0f : v_max * 8.0f;
    motion_plan(steps, v_max, accel);
}
```

#### 转矩-速度特性曲线

```
转矩 (N·m)
  │
  0.40│████████████████████████████
  0.35│████████████████████████████
  0.30│████████████████████████
  0.25│████████████████████
  0.20│████████████████
  0.15│████████████
  0.10│████████
  0.05│████
  0.00└──────────────────────────── 速度 (steps/s)
       0   500  1000  2000  3000  5000

  ← 拉出转矩曲线（Pull-out Torque）：运行中不失步的最大转矩
  ← 拉入转矩曲线（Pull-in Torque）：自启动不失步的最大转矩
  
  两条曲线之间的区域 = 可运行但不能自启动的速度范围
  → 必须通过加减速算法进入该区域
```

### 微步进技术（Microstepping）

#### 微步进原理

全步驱动时，两相电流按方波切换，转子每次跳跃1.8°。微步进通过控制两相电流的比例，使转子停在中间位置，实现更小的步距角。

```
全步 vs 微步进电流波形：

全步（Full Step）：
  A相: ████    ████    ████
       ────────────────────
  B相:     ████    ████

半步（Half Step）：
  A相: ████  ████  ████
       ──────────────────
  B相:   ████  ████

1/16微步：
  A相: ╱‾‾‾‾‾‾‾‾‾‾‾‾╲___
       ──────────────────
  B相: ___╱‾‾‾‾‾‾‾‾‾‾‾‾╲

  A相电流 = I_max × cos(θ_e)
  B相电流 = I_max × sin(θ_e)
  θ_e 每步增加 π/(2×细分数)
```

#### 微步进电流波形整形

理想微步进需要正弦/余弦电流波形。DRV8825等驱动芯片内部集成了DAC和电流控制环路：

```c
// 软件微步进电流表（1/8细分，每相8个电流值）
// 归一化到 0~255，对应 0~I_max
const uint8_t MICROSTEP_TABLE[8] = {
    255, 239, 191, 130, 64, 18, 0, 18
    // cos(0°), cos(22.5°), cos(45°), cos(67.5°),
    // cos(90°), cos(112.5°), cos(135°), cos(157.5°)
};

// 对于硬件微步进（DRV8825），只需设置M0/M1/M2引脚
// 芯片内部自动处理电流波形
```

#### DRV8825微步进驱动器配置

DRV8825是TI公司的高性能步进电机驱动芯片，支持1/32细分，最大电流2.5A。

```
DRV8825 引脚连接图：

STM32                    DRV8825              NEMA17
─────────────────────────────────────────────────────
PA0 (STEP) ──────────── STEP
PA1 (DIR)  ──────────── DIR
PA2 (EN)   ──────────── ENABLE (低有效)
PA3        ──────────── M0  ┐
PA4        ──────────── M1  ├─ 细分设置
PA5        ──────────── M2  ┘
PA6        ──────────── FAULT (输入，低=故障)
PA7        ──────────── SLEEP (高=工作)
PA8        ──────────── RESET (高=工作)

3.3V ────────────────── VDD (逻辑电源)
12V  ────────────────── VMOT (电机电源)
GND  ────────────────── GND

                         A1 ──────────────── A+
                         A2 ──────────────── A-
                         B1 ──────────────── B+
                         B2 ──────────────── B-

电流限制设置（通过VREF引脚）：
  I_max = VREF / (5 × R_sense)
  R_sense = 0.1Ω（DRV8825默认）
  例：VREF = 0.85V → I_max = 0.85 / (5 × 0.1) = 1.7A
```

**细分设置真值表**：

```
M2  M1  M0  │ 细分数  │ 步距角(1.8°电机)
────────────┼─────────┼──────────────────
 0   0   0  │  全步   │  1.800°
 0   0   1  │  1/2    │  0.900°
 0   1   0  │  1/4    │  0.450°
 0   1   1  │  1/8    │  0.225°
 1   0   0  │  1/16   │  0.1125°
 1   0   1  │  1/32   │  0.05625°
```

```c
// DRV8825 初始化代码（STM32 HAL）
#define STEP_PIN    GPIO_PIN_0
#define DIR_PIN     GPIO_PIN_1
#define EN_PIN      GPIO_PIN_2
#define M0_PIN      GPIO_PIN_3
#define M1_PIN      GPIO_PIN_4
#define M2_PIN      GPIO_PIN_5
#define FAULT_PIN   GPIO_PIN_6
#define STEP_PORT   GPIOA

typedef enum {
    MICROSTEP_FULL  = 0,  // M2=0, M1=0, M0=0
    MICROSTEP_HALF  = 1,  // M2=0, M1=0, M0=1
    MICROSTEP_4     = 2,  // M2=0, M1=1, M0=0
    MICROSTEP_8     = 3,  // M2=0, M1=1, M0=1
    MICROSTEP_16    = 4,  // M2=1, M1=0, M0=0
    MICROSTEP_32    = 5,  // M2=1, M1=0, M0=1
} MicrostepMode;

void drv8825_init(MicrostepMode mode) {
    // 配置GPIO（假设已在CubeMX中设置为输出）
    
    // 设置细分模式
    HAL_GPIO_WritePin(STEP_PORT, M0_PIN, (mode >> 0) & 1);
    HAL_GPIO_WritePin(STEP_PORT, M1_PIN, (mode >> 1) & 1);
    HAL_GPIO_WritePin(STEP_PORT, M2_PIN, (mode >> 2) & 1);
    
    // 唤醒驱动器
    HAL_GPIO_WritePin(STEP_PORT, EN_PIN, GPIO_PIN_RESET);  // 使能（低有效）
    
    // 等待驱动器稳定（至少1ms）
    HAL_Delay(1);
}

void drv8825_set_direction(uint8_t dir) {
    HAL_GPIO_WritePin(STEP_PORT, DIR_PIN, dir ? GPIO_PIN_SET : GPIO_PIN_RESET);
    // DIR建立时间：至少200ns，在STEP上升沿前
    __NOP(); __NOP(); __NOP(); __NOP();
}

void drv8825_step_pulse(void) {
    // STEP脉冲宽度：最小1.9μs高电平
    HAL_GPIO_WritePin(STEP_PORT, STEP_PIN, GPIO_PIN_SET);
    // 精确延时（使用DWT计数器）
    DWT_Delay_us(2);
    HAL_GPIO_WritePin(STEP_PORT, STEP_PIN, GPIO_PIN_RESET);
    DWT_Delay_us(2);
}

uint8_t drv8825_check_fault(void) {
    // FAULT引脚低电平表示故障（过温、过流）
    return HAL_GPIO_ReadPin(STEP_PORT, FAULT_PIN) == GPIO_PIN_RESET;
}
```

### 为什么需要加减速

步进电机的转矩-速度特性决定了它在高速时转矩下降。如果启动时速度过高，电机转矩不足以克服惯性，就会发生失步：

```
转矩
  │
  │████████
  │        ████
  │            ████
  │                ████
  └──────────────────── 速度
  
低速区：转矩大，可以承受较大加速度
高速区：转矩小，需要缓慢加速
```

**加减速的本质**：控制每两个脉冲之间的时间间隔（步进周期），从大到小（加速），保持（匀速），再从小到大（减速）。

### 速度与脉冲周期的关系

```
速度(steps/s) = 1 / 脉冲周期(s)
速度(RPM)     = 速度(steps/s) × 60 / (每转步数 × 细分数)

例：200步/转电机，16细分，目标速度600RPM：
  steps/s = 600 × 200 × 16 / 60 = 32000 steps/s
  脉冲周期 = 1 / 32000 = 31.25 μs
```

## 核心内容

### 梯形速度曲线（Trapezoidal Profile）

梯形曲线是最常用的加减速方案，分三段：

```
速度
  │         ┌──────────────┐
  │        /│              │\
  │       / │              │ \
  │      /  │              │  \
  │     /   │              │   \
  └────┴────┴──────────────┴────┴── 时间
       加速段  匀速段（可能为0）  减速段
```

**关键参数**：
- `v_start`：起始速度（通常为最小可靠速度，如100 steps/s）
- `v_max`：最大速度
- `accel`：加速度（steps/s²）
- `total_steps`：总步数

**判断是否有匀速段**：

```
加速到v_max所需步数 = (v_max² - v_start²) / (2 × accel)
减速到v_start所需步数 = 同上

如果 加速步数 + 减速步数 > total_steps：
    → 没有匀速段，需要计算实际峰值速度（三角形曲线）
    → v_peak = sqrt(v_start² + accel × total_steps)
```

### 梯形加减速实现

基于定时器中断，每次中断产生一个脉冲，动态调整下次中断的时间间隔：

```c
#include <math.h>
#include <stdint.h>

// 运动参数
typedef struct {
    uint32_t total_steps;   // 总步数
    float    v_start;       // 起始速度 (steps/s)
    float    v_max;         // 最大速度 (steps/s)
    float    accel;         // 加速度 (steps/s²)

    // 运行时状态
    uint32_t step_count;    // 已执行步数
    uint32_t accel_steps;   // 加速段步数
    uint32_t decel_start;   // 开始减速的步数位置
    float    current_speed; // 当前速度 (steps/s)
    int8_t   phase;         // 0=加速, 1=匀速, 2=减速, 3=停止
} MotionProfile;

static MotionProfile motion;
static volatile uint8_t motion_done = 0;

// 预计算运动参数
void motion_plan(uint32_t steps, float v_max, float accel) {
    motion.total_steps = steps;
    motion.v_start     = 200.0f;   // 最小起始速度
    motion.v_max       = v_max;
    motion.accel       = accel;
    motion.step_count  = 0;
    motion.phase       = 0;
    motion_done        = 0;

    // 计算加速段步数
    float accel_steps_f = (v_max * v_max - motion.v_start * motion.v_start)
                          / (2.0f * accel);
    motion.accel_steps = (uint32_t)accel_steps_f;

    // 判断是否有匀速段
    if (motion.accel_steps * 2 >= steps) {
        // 三角形曲线：无匀速段
        motion.accel_steps = steps / 2;
        // 实际峰值速度
        motion.v_max = sqrtf(motion.v_start * motion.v_start
                             + accel * motion.accel_steps);
    }

    motion.decel_start  = steps - motion.accel_steps;
    motion.current_speed = motion.v_start;

    // 设置第一个定时器周期
    uint32_t period_us = (uint32_t)(1000000.0f / motion.v_start);
    timer_set_period(period_us);
    timer_start();
}

// 定时器中断服务函数：每次中断产生一个脉冲
void STEP_TIMER_IRQHandler(void) {
    timer_clear_flag();

    if (motion.step_count >= motion.total_steps) {
        timer_stop();
        step_pin_low();
        motion_done = 1;
        return;
    }

    // 产生步进脉冲
    step_pin_high();
    __NOP(); __NOP(); __NOP();  // 保持高电平至少1μs
    step_pin_low();

    motion.step_count++;

    // 更新速度
    float new_speed = motion.current_speed;

    if (motion.step_count < motion.accel_steps) {
        // 加速段：v² = v₀² + 2as，每步后更新速度
        new_speed = sqrtf(motion.current_speed * motion.current_speed
                          + 2.0f * motion.accel);
        if (new_speed > motion.v_max) new_speed = motion.v_max;
        motion.phase = 0;

    } else if (motion.step_count < motion.decel_start) {
        // 匀速段
        new_speed = motion.v_max;
        motion.phase = 1;

    } else {
        // 减速段
        float v2 = motion.current_speed * motion.current_speed
                   - 2.0f * motion.accel;
        new_speed = (v2 > motion.v_start * motion.v_start)
                    ? sqrtf(v2) : motion.v_start;
        motion.phase = 2;
    }

    motion.current_speed = new_speed;

    // 设置下一个脉冲的时间间隔
    uint32_t period_us = (uint32_t)(1000000.0f / new_speed);
    timer_set_period(period_us);
}

// 等待运动完成
void motion_wait_done(void) {
    while (!motion_done);
}
```

**使用示例**：

```c
// 以2000 steps/s最大速度，10000 steps/s²加速度，移动5000步
motion_plan(5000, 2000.0f, 10000.0f);
motion_wait_done();
printf("Motion complete!\n");
```

### S曲线加减速推导（Jerk-Limited Profile）

梯形曲线在加速段开始和结束时加速度突变，会产生冲击（Jerk）。S曲线通过限制加加速度（Jerk，单位 steps/s³）使加速度平滑变化：

```
梯形曲线的加速度（有冲击）：
  加速度
  │    ┌──────────────┐
  │    │              │
  │    │              │
  ────┘              └──── 时间
  ↑突变                ↑突变

S曲线的加速度（无冲击）：
  加速度
  │    ╱‾‾‾‾‾‾‾‾‾‾‾‾╲
  │   ╱              ╲
  │  ╱                ╲
  ──╱                  ╲── 时间
  平滑过渡

S曲线速度（S形）：
  v_max ─────────────────────────────────────────
        ╱‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾╲
       ╱                                        ╲
      ╱                                          ╲
  v_0 ─────────────────────────────────────────── v_0
      t1  t2  t3  t4  t5  t6  t7
```

**S曲线七段结构**：

```
段1 [0, t1]：加加速（Jerk+），加速度从0增加到a_max
段2 [t1, t2]：匀加速，加速度保持a_max（可能为0）
段3 [t2, t3]：减加速（Jerk-），加速度从a_max减少到0
段4 [t3, t4]：匀速，加速度=0（可能为0）
段5 [t4, t5]：加减速（Jerk+），加速度从0增加到-a_max
段6 [t5, t6]：匀减速，加速度保持-a_max（可能为0）
段7 [t6, t7]：减减速（Jerk-），加速度从-a_max增加到0
```

**各段数学推导**：

```
给定参数：
  v_0   = 起始速度 (steps/s)
  v_max = 最大速度 (steps/s)
  a_max = 最大加速度 (steps/s²)
  J     = 最大加加速度 Jerk (steps/s³)

Jerk段持续时间：
  t_j = a_max / J

每个Jerk段的速度增量：
  Δv_j = a_max² / (2J)

匀加速段速度增量：
  Δv_a = (v_max - v_0) - 2 × Δv_j

若 Δv_a ≥ 0：有匀加速段，t_a = Δv_a / a_max
若 Δv_a < 0：无匀加速段，需重新计算：
  t_j = sqrt((v_max - v_0) / J)
  t_a = 0

加速段总时间：T_accel = 2 × t_j + t_a
加速段位移（近似）：s_accel ≈ (v_0 + v_max) / 2 × T_accel
```

**简化S曲线实现**（正弦近似，适合资源受限MCU）：

```c
// 使用正弦函数近似S曲线
// 在加速段：speed = v_start + (v_max - v_start) × (1 - cos(π × t/T)) / 2
// t: 当前时间，T: 加速段总时间

float s_curve_speed(float t, float T, float v_start, float v_max) {
    if (t >= T) return v_max;
    float ratio = t / T;
    // 正弦S曲线：平滑的加速过渡，无需计算7段参数
    return v_start + (v_max - v_start) * (1.0f - cosf(M_PI * ratio)) / 2.0f;
}

// 正弦S曲线加速度（用于前馈控制）
float s_curve_accel(float t, float T, float v_start, float v_max) {
    if (t >= T) return 0.0f;
    float ratio = t / T;
    return (v_max - v_start) * M_PI / (2.0f * T) * sinf(M_PI * ratio);
}
```

**S曲线 vs 梯形曲线对比**：

| 特性 | 梯形曲线 | S曲线 |
|------|---------|-------|
| 实现复杂度 | 简单 | 中等 |
| 计算量 | 低 | 中（需要三角函数） |
| 机械冲击 | 有（加速度突变） | 无 |
| 定位精度 | 良好 | 更优 |
| 振动抑制 | 一般 | 优秀 |
| 适用场景 | 一般精度要求 | 高精度、高速场景 |
| MCU资源 | 低（Cortex-M0可用） | 中（需要FPU） |

### 实时轨迹生成（位置/速度/加速度输出）

在高级运动控制中，需要实时输出位置、速度、加速度三元组，供伺服驱动器使用：

```c
// 实时轨迹点结构
typedef struct {
    float position;     // 位置 (steps)
    float velocity;     // 速度 (steps/s)
    float acceleration; // 加速度 (steps/s²)
    float timestamp;    // 时间戳 (s)
} TrajectoryPoint;

// 梯形曲线实时轨迹生成器
// 以固定时间步长 dt 输出轨迹点
TrajectoryPoint trapezoid_trajectory(float t, float v_max, float accel,
                                      float total_time) {
    TrajectoryPoint pt;
    pt.timestamp = t;

    float t_accel = v_max / accel;  // 加速时间
    float t_decel = t_accel;        // 减速时间（对称）
    float t_const = total_time - t_accel - t_decel;

    if (t_const < 0) {
        // 三角形曲线
        t_accel = total_time / 2.0f;
        t_decel = t_accel;
        t_const = 0;
        v_max = accel * t_accel;
    }

    if (t < t_accel) {
        // 加速段
        pt.acceleration = accel;
        pt.velocity     = accel * t;
        pt.position     = 0.5f * accel * t * t;
    } else if (t < t_accel + t_const) {
        // 匀速段
        float dt = t - t_accel;
        pt.acceleration = 0;
        pt.velocity     = v_max;
        pt.position     = 0.5f * v_max * t_accel + v_max * dt;
    } else if (t < total_time) {
        // 减速段
        float dt = t - t_accel - t_const;
        float s0 = 0.5f * v_max * t_accel + v_max * t_const;
        pt.acceleration = -accel;
        pt.velocity     = v_max - accel * dt;
        pt.position     = s0 + v_max * dt - 0.5f * accel * dt * dt;
    } else {
        // 运动结束
        pt.acceleration = 0;
        pt.velocity     = 0;
        pt.position     = 0.5f * v_max * t_accel + v_max * t_const
                          + 0.5f * v_max * t_decel;
    }

    return pt;
}

// 使用示例：以1ms为步长生成轨迹
void generate_trajectory_table(void) {
    float dt = 0.001f;  // 1ms
    float total_time = 2.0f;  // 2秒运动
    
    for (float t = 0; t <= total_time; t += dt) {
        TrajectoryPoint pt = trapezoid_trajectory(t, 2000.0f, 5000.0f, total_time);
        // 发送给伺服驱动器或记录到缓冲区
        servo_set_target(pt.position, pt.velocity, pt.acceleration);
    }
}
```

### 参数调优指南

**加速度选择**：

```
保守值（不失步优先）：
  accel = v_max × 5    （加速时间约0.2s）

激进值（速度优先）：
  accel = v_max × 20   （加速时间约0.05s）

实际调试：从保守值开始，逐步增大直到出现失步，
          然后退回到失步值的70%作为工作参数
```

**起始速度选择**：

```
v_start 应小于电机的自启动频率（Start Frequency）
通常为100~500 steps/s，查阅电机数据手册
```

## 深入原理

### 失步检测（Step Loss Detection）

失步是步进电机最严重的故障模式。检测失步有两种主要方法：

#### 方法1：反电动势（Back-EMF）检测

步进电机在运动时，绕组会产生反电动势（Back-EMF）。通过在不驱动的相上测量感应电压，可以判断转子是否跟随命令运动：

```
反电动势检测原理：

两相步进电机，A相驱动时，B相产生感应电压：
  V_bemf = K_e × ω

其中：
  K_e = 反电动势常数 (V·s/rad)
  ω   = 转子角速度 (rad/s)

如果命令了运动但 V_bemf ≈ 0，说明转子没有转动 → 失步！

检测电路：
  B相绕组 ──┬── 分压电阻R1 ──── ADC输入
            └── 分压电阻R2 ──── GND

  ADC采样时机：在B相不驱动的时间窗口内采样
```

```c
// 反电动势失步检测实现
// 适用于两相步进电机，在不驱动相上采样

#define BEMF_THRESHOLD  50    // ADC计数，低于此值认为失步
#define BEMF_ADC_CH     ADC_CHANNEL_1  // B相反电动势ADC通道

typedef struct {
    uint32_t step_count;      // 命令步数
    uint32_t detected_steps;  // 检测到的实际步数
    uint8_t  stall_detected;  // 失步标志
    uint16_t bemf_value;      // 最近一次反电动势ADC值
} StallDetector;

static StallDetector stall_det;

// 在步进中断中调用：采样反电动势
void stall_detect_sample(void) {
    // 在STEP脉冲后的固定延时窗口内采样
    // 此时驱动器已切换相位，可以采样非驱动相
    DWT_Delay_us(50);  // 等待电流稳定
    
    stall_det.bemf_value = HAL_ADC_GetValue(&hadc1);
    stall_det.step_count++;
    
    if (stall_det.bemf_value > BEMF_THRESHOLD) {
        stall_det.detected_steps++;
    } else {
        // 反电动势过低，可能失步
        // 连续3步检测到才报警（避免误报）
        static uint8_t low_bemf_count = 0;
        low_bemf_count++;
        if (low_bemf_count >= 3) {
            stall_det.stall_detected = 1;
            low_bemf_count = 0;
        }
    }
}

// 检查是否失步
uint8_t stall_is_detected(void) {
    return stall_det.stall_detected;
}

// 清除失步标志
void stall_clear(void) {
    stall_det.stall_detected = 0;
    stall_det.step_count = 0;
    stall_det.detected_steps = 0;
}
```

#### 方法2：TMC2209 StallGuard™ 技术

TMC2209是Trinamic公司的智能步进驱动芯片，内置StallGuard4™失速检测，无需外部传感器：

```
TMC2209 StallGuard工作原理：
  1. 芯片持续监测绕组电流波形
  2. 计算实际电流与理想正弦波的偏差
  3. 偏差超过阈值 → 报告失速（DIAG引脚拉低）

优势：
  - 无需编码器或额外传感器
  - 可用于无传感器回零（Sensorless Homing）
  - 支持UART配置（波特率115200）

STM32连接：
  PA9 (UART1_TX) ──── PDN_UART (TMC2209)
  PA10 (UART1_RX) ─── PDN_UART (TMC2209)
  PB0 ─────────────── DIAG (失速输出，低有效)
```

```c
// TMC2209 UART配置（使用tmc2209库或直接寄存器操作）
// 寄存器地址参考TMC2209数据手册

#define TMC2209_ADDR    0x00  // 驱动器地址（MS1/MS2设置）

// 写寄存器
void tmc2209_write_reg(uint8_t addr, uint8_t reg, uint32_t value) {
    uint8_t buf[8];
    buf[0] = 0x05;          // 同步字节
    buf[1] = addr;          // 驱动器地址
    buf[2] = reg | 0x80;    // 寄存器地址（写标志）
    buf[3] = (value >> 24) & 0xFF;
    buf[4] = (value >> 16) & 0xFF;
    buf[5] = (value >> 8)  & 0xFF;
    buf[6] = (value >> 0)  & 0xFF;
    buf[7] = tmc2209_crc(buf, 7);  // CRC校验
    
    HAL_UART_Transmit(&huart1, buf, 8, 100);
}

// 配置StallGuard阈值
void tmc2209_set_stallguard(uint8_t threshold) {
    // SGTHRS寄存器（0x40）：StallGuard阈值
    // 值越大，越容易触发失速检测
    tmc2209_write_reg(TMC2209_ADDR, 0x40, threshold);
}

// 配置运行电流
void tmc2209_set_current(uint8_t run_current, uint8_t hold_current) {
    // IHOLD_IRUN寄存器（0x10）
    uint32_t val = ((uint32_t)hold_current & 0x1F)
                 | (((uint32_t)run_current & 0x1F) << 8)
                 | (3UL << 16);  // IHOLDDELAY = 3
    tmc2209_write_reg(TMC2209_ADDR, 0x10, val);
}

// 无传感器回零（Sensorless Homing）
void sensorless_home(void) {
    // 1. 降低速度和电流（提高灵敏度）
    tmc2209_set_current(10, 5);  // 低电流
    tmc2209_set_stallguard(50);  // 中等阈值
    
    // 2. 向限位方向运动
    drv_set_direction(DIR_NEGATIVE);
    
    // 3. 以低速运动，等待DIAG引脚触发
    motion_plan(100000, 500.0f, 2000.0f);  // 足够大的步数
    
    while (!motion_done) {
        if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0) == GPIO_PIN_RESET) {
            // DIAG引脚低 = 失速检测 = 到达限位
            motion_stop();
            break;
        }
    }
    
    // 4. 恢复正常电流和阈值
    tmc2209_set_current(20, 10);
    tmc2209_set_stallguard(100);
    
    // 5. 设置当前位置为零点
    current_position = 0;
}
```

### 闭环步进控制（Closed-Loop Stepper）

通过添加编码器反馈，步进电机可以实现真正的闭环控制，彻底消除失步问题：

```
闭环步进系统框图：

目标位置 ──→ [位置控制器] ──→ [速度规划] ──→ [步进驱动] ──→ 电机
                ↑                                              │
                └──────────── [编码器] ←──────────────────────┘
                              (位置反馈)

控制策略：
  1. 位置误差 = 目标位置 - 编码器实际位置
  2. 若误差 > 阈值：增加脉冲（补偿失步）
  3. 若误差 < -阈值：减少脉冲（防止过冲）
```

```c
// 闭环步进控制器
// 使用编码器反馈修正位置误差

#include "encoder.h"  // 编码器驱动（参考编码器接口文章）

#define POSITION_TOLERANCE  2    // 允许误差（编码器计数）
#define MAX_CORRECTION_SPEED 500.0f  // 最大修正速度 (steps/s)

typedef struct {
    int32_t  target_position;   // 目标位置（步进步数）
    int32_t  command_position;  // 命令位置（已发出的脉冲数）
    int32_t  encoder_position;  // 编码器实际位置（转换为步数）
    float    encoder_ratio;     // 编码器计数/步进步数 比例
    int32_t  position_error;    // 位置误差
    uint8_t  correction_active; // 修正运动标志
} ClosedLoopStepper;

static ClosedLoopStepper cls;

void cls_init(float encoder_ratio) {
    cls.encoder_ratio = encoder_ratio;
    cls.target_position = 0;
    cls.command_position = 0;
    cls.encoder_position = 0;
    cls.position_error = 0;
    cls.correction_active = 0;
}

// 在主循环中周期性调用（建议10ms）
void cls_update(void) {
    // 读取编码器位置并转换为步数
    int32_t enc_raw = encoder_get_count();
    cls.encoder_position = (int32_t)(enc_raw / cls.encoder_ratio);
    
    // 计算位置误差
    cls.position_error = cls.command_position - cls.encoder_position;
    
    // 如果误差超过容差，启动修正运动
    if (abs(cls.position_error) > POSITION_TOLERANCE && !cls.correction_active) {
        int32_t correction_steps = cls.position_error;
        float correction_speed = (float)abs(correction_steps) * 10.0f;
        
        // 限制修正速度
        if (correction_speed > MAX_CORRECTION_SPEED)
            correction_speed = MAX_CORRECTION_SPEED;
        
        // 设置修正方向
        drv8825_set_direction(correction_steps > 0 ? 1 : 0);
        
        // 执行修正运动
        cls.correction_active = 1;
        motion_plan(abs(correction_steps), correction_speed, correction_speed * 5.0f);
    }
    
    if (motion_done) {
        cls.correction_active = 0;
        cls.command_position += cls.position_error > 0 ?
                                abs(cls.position_error) : -abs(cls.position_error);
    }
}

// 移动到绝对位置
void cls_move_to(int32_t target) {
    int32_t delta = target - cls.command_position;
    if (delta == 0) return;
    
    cls.target_position = target;
    drv8825_set_direction(delta > 0 ? 1 : 0);
    motion_plan(abs(delta), 2000.0f, 10000.0f);
    
    // 等待运动完成并验证位置
    motion_wait_done();
    HAL_Delay(10);  // 等待机械稳定
    
    cls.command_position = target;
    cls_update();  // 检查并修正误差
}
```

### 性能优化：定时器精度分析

步进电机控制对定时器精度要求极高。以下分析STM32定时器的精度限制：

```
定时器精度分析（STM32F4，168MHz）：

定时器时钟：84MHz（APB1 × 2）
最小计数单位：1/84MHz ≈ 11.9 ns

速度精度：
  目标速度 2000 steps/s → 周期 500μs → 计数值 42000
  实际速度 = 84MHz / 42000 = 2000.0 steps/s（精确）

  目标速度 3333 steps/s → 周期 300μs → 计数值 25200
  实际速度 = 84MHz / 25200 = 3333.3 steps/s（误差 0.01%）

高速时的精度问题：
  目标速度 50000 steps/s → 周期 20μs → 计数值 1680
  实际速度 = 84MHz / 1680 = 50000 steps/s（精确）

  目标速度 50001 steps/s → 计数值 1679.97 → 取整1679
  实际速度 = 84MHz / 1679 = 50030 steps/s（误差 0.06%）

结论：速度越高，量化误差越大，但通常在可接受范围内
```


## 完整项目实战：CNC单轴控制器

### 项目概述

本项目实现一个完整的CNC单轴控制器，包含：
- DRV8825步进驱动（1/16细分）
- 两端限位开关（硬件限位）
- 回零（Homing）序列
- 梯形加减速运动
- 串口命令接口（G-code子集）

### 硬件清单（BOM）

| 序号 | 元件 | 型号 | 数量 | 参考价格 |
|------|------|------|------|---------|
| 1 | 主控MCU | STM32F103C8T6（蓝色药丸） | 1 | ¥8 |
| 2 | 步进驱动 | DRV8825模块 | 1 | ¥12 |
| 3 | 步进电机 | NEMA17 17HS4401（1.7A，0.4N·m） | 1 | ¥25 |
| 4 | 限位开关 | 微动开关 SS-5GL | 2 | ¥2 |
| 5 | 电源 | 12V/3A开关电源 | 1 | ¥20 |
| 6 | 电容 | 100μF/25V电解电容 | 1 | ¥1 |
| 7 | 电容 | 100nF陶瓷电容 | 2 | ¥0.5 |
| 8 | 电阻 | 10kΩ上拉电阻 | 2 | ¥0.2 |
| 9 | 导轨 | MGN12H线性导轨 200mm | 1 | ¥35 |
| 10 | 丝杆 | T8丝杆+螺母 200mm | 1 | ¥15 |

**总成本约：¥120**

### 硬件连接图

```
STM32F103C8T6          DRV8825模块
─────────────────────────────────────────────────────
PA0 (TIM2_CH1) ──────── STEP
PA1            ──────── DIR
PA2            ──────── ENABLE (低有效)
PA3            ──────── M0  ┐
PA4            ──────── M1  ├─ 1/16细分：M0=0,M1=0,M2=1
PA5            ──────── M2  ┘
PA6 (输入)     ──────── FAULT (故障检测)
3.3V           ──────── SLEEP, RESET (保持高电平)
3.3V           ──────── VDD
GND            ──────── GND

DRV8825模块            NEMA17步进电机
─────────────────────────────────────
VMOT (12V)     ──────── 电机电源
GND            ──────── GND
A1             ──────── A+ (黑线)
A2             ──────── A- (绿线)
B1             ──────── B+ (红线)
B2             ──────── B- (蓝线)

限位开关连接：
PA7 ──── 10kΩ上拉 ──── 3.3V
PA7 ──── 限位开关1 ──── GND  (负方向限位)

PA8 ──── 10kΩ上拉 ──── 3.3V
PA8 ──── 限位开关2 ──── GND  (正方向限位)

电源去耦：
VMOT ──── 100μF ──── GND  (靠近DRV8825)
VMOT ──── 100nF ──── GND
```

### 完整固件实现

```c
/* cnc_single_axis.c
 * CNC单轴控制器完整实现
 * 硬件：STM32F103C8T6 + DRV8825 + NEMA17
 * 编译：STM32CubeIDE，HAL库 v1.8.x，STM32F1xx_HAL_Driver
 */

#include "main.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// ============================================================
// 机械参数
// ============================================================
#define STEPS_PER_REV   200          // 电机步数/转
#define MICROSTEP       16           // 细分数
#define LEAD_MM         8.0f         // 丝杆导程 (mm/转)
#define STEPS_PER_MM    ((STEPS_PER_REV * MICROSTEP) / LEAD_MM)  // 400 steps/mm

// 运动限制
#define MAX_SPEED_MM_S  50.0f        // 最大速度 (mm/s)
#define MAX_ACCEL_MM_S2 200.0f       // 最大加速度 (mm/s²)
#define AXIS_LENGTH_MM  180.0f       // 轴行程 (mm)
#define HOME_SPEED_MM_S 10.0f        // 回零速度 (mm/s)
#define HOME_BACKOFF_MM 2.0f         // 回零后退距离 (mm)

// ============================================================
// 全局状态
// ============================================================
static volatile int32_t  current_position = 0;  // 当前位置 (steps)
static volatile uint8_t  is_homed = 0;
static volatile uint8_t  motion_active = 0;
static volatile uint8_t  fault_flag = 0;

// ISR使用的运动参数
static float    v_start_isr, v_max_isr, accel_isr;
static uint32_t total_steps_isr, step_count_isr;
static uint32_t accel_steps_isr, decel_start_isr;
static float    current_speed_isr;
static int8_t   motion_dir;

// ============================================================
// 底层驱动
// ============================================================
static inline void motor_enable(void)  { HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET); }
static inline void motor_disable(void) { HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_SET); }

static inline void motor_set_dir(int8_t d) {
    motion_dir = d;
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, d > 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    for (volatile int i = 0; i < 10; i++);  // DIR建立时间 ≥ 200ns
}

static inline uint8_t limit_neg(void) {
    return HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_7) == GPIO_PIN_RESET;
}
static inline uint8_t limit_pos(void) {
    return HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_8) == GPIO_PIN_RESET;
}

static inline void timer_set_us(uint32_t us) {
    // TIM2预分频72，计数频率1MHz，ARR = us-1
    __HAL_TIM_SET_AUTORELOAD(&htim2, us > 0 ? us - 1 : 0);
    __HAL_TIM_SET_COUNTER(&htim2, 0);
}

// ============================================================
// 运动规划与执行
// ============================================================
static int32_t mm_to_steps(float mm) { return (int32_t)(mm * STEPS_PER_MM); }
static float   steps_to_mm(int32_t s) { return (float)s / STEPS_PER_MM; }

HAL_StatusTypeDef motion_start(uint32_t steps, float v_mm, float a_mm, int8_t dir) {
    if (motion_active || steps == 0) return HAL_BUSY;
    if (dir > 0 && limit_pos()) return HAL_ERROR;
    if (dir < 0 && limit_neg()) return HAL_ERROR;

    v_start_isr = 200.0f;
    v_max_isr   = fminf(v_mm * STEPS_PER_MM, MAX_SPEED_MM_S * STEPS_PER_MM);
    accel_isr   = a_mm * STEPS_PER_MM;

    total_steps_isr = steps;
    step_count_isr  = 0;

    float as = (v_max_isr * v_max_isr - v_start_isr * v_start_isr) / (2.0f * accel_isr);
    accel_steps_isr = (uint32_t)as;

    if (accel_steps_isr * 2 >= steps) {
        accel_steps_isr = steps / 2;
        v_max_isr = sqrtf(v_start_isr * v_start_isr + accel_isr * accel_steps_isr);
    }

    decel_start_isr   = steps - accel_steps_isr;
    current_speed_isr = v_start_isr;

    motor_set_dir(dir);
    motor_enable();
    timer_set_us((uint32_t)(1000000.0f / v_start_isr));
    motion_active = 1;
    HAL_TIM_Base_Start_IT(&htim2);
    return HAL_OK;
}

void motion_stop_now(void) {
    HAL_TIM_Base_Stop_IT(&htim2);
    motion_active = 0;
}

HAL_StatusTypeDef motion_wait(uint32_t timeout_ms) {
    uint32_t t0 = HAL_GetTick();
    while (motion_active) {
        if (HAL_GetTick() - t0 > timeout_ms) return HAL_TIMEOUT;
        if (fault_flag) return HAL_ERROR;
    }
    return HAL_OK;
}

// 定时器中断
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance != TIM2) return;

    // 限位保护
    if ((motion_dir > 0 && limit_pos()) || (motion_dir < 0 && limit_neg())) {
        HAL_TIM_Base_Stop_IT(&htim2);
        motion_active = 0;
        return;
    }

    if (step_count_isr >= total_steps_isr) {
        HAL_TIM_Base_Stop_IT(&htim2);
        current_position += motion_dir * (int32_t)total_steps_isr;
        motion_active = 0;
        return;
    }

    // 产生脉冲（最小宽度 2μs）
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_SET);
    uint32_t c0 = DWT->CYCCNT;
    while (DWT->CYCCNT - c0 < 144);  // 2μs @ 72MHz
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
    step_count_isr++;

    // 速度更新
    float ns;
    if (step_count_isr < accel_steps_isr) {
        ns = sqrtf(current_speed_isr * current_speed_isr + 2.0f * accel_isr);
        if (ns > v_max_isr) ns = v_max_isr;
    } else if (step_count_isr < decel_start_isr) {
        ns = v_max_isr;
    } else {
        float v2 = current_speed_isr * current_speed_isr - 2.0f * accel_isr;
        ns = (v2 > v_start_isr * v_start_isr) ? sqrtf(v2) : v_start_isr;
    }
    current_speed_isr = ns;
    uint32_t p = (uint32_t)(1000000.0f / ns);
    if (p < 20) p = 20;
    timer_set_us(p);
}
```

### 回零序列实现

```c
// 回零步骤：快速触碰 → 后退 → 低速精确触碰 → 设置零点
HAL_StatusTypeDef axis_home(void) {
    printf("开始回零...\r\n");
    is_homed = 0;

    // 步骤1：快速向负方向运动
    motion_start(mm_to_steps(AXIS_LENGTH_MM + 10.0f),
                 HOME_SPEED_MM_S, HOME_SPEED_MM_S * 5.0f, -1);

    uint32_t t0 = HAL_GetTick();
    while (motion_active) {
        if (limit_neg()) { motion_stop_now(); break; }
        if (HAL_GetTick() - t0 > 30000) {
            motion_stop_now();
            printf("错误：回零超时！\r\n");
            return HAL_TIMEOUT;
        }
    }
    if (!limit_neg()) { printf("错误：未找到负限位！\r\n"); return HAL_ERROR; }
    HAL_Delay(50);

    // 步骤2：后退
    motion_start(mm_to_steps(HOME_BACKOFF_MM),
                 HOME_SPEED_MM_S, HOME_SPEED_MM_S * 5.0f, +1);
    motion_wait(5000);

    // 步骤3：低速精确触碰
    motion_start(mm_to_steps(HOME_BACKOFF_MM + 2.0f),
                 HOME_SPEED_MM_S / 3.0f, HOME_SPEED_MM_S * 2.0f, -1);
    t0 = HAL_GetTick();
    while (motion_active) {
        if (limit_neg()) { motion_stop_now(); break; }
        if (HAL_GetTick() - t0 > 10000) { motion_stop_now(); return HAL_TIMEOUT; }
    }

    // 步骤4：设置零点，移动到安全位置
    current_position = 0;
    is_homed = 1;
    printf("回零完成！\r\n");

    motion_start(mm_to_steps(5.0f), HOME_SPEED_MM_S, HOME_SPEED_MM_S * 5.0f, +1);
    motion_wait(5000);
    current_position = mm_to_steps(5.0f);
    return HAL_OK;
}

// 移动到绝对位置（mm）
HAL_StatusTypeDef axis_move_to(float target_mm) {
    if (!is_homed) { printf("错误：未回零！\r\n"); return HAL_ERROR; }
    if (target_mm < 0 || target_mm > AXIS_LENGTH_MM) {
        printf("错误：超出范围 [0, %.0f mm]\r\n", AXIS_LENGTH_MM);
        return HAL_ERROR;
    }
    int32_t delta = mm_to_steps(target_mm) - current_position;
    if (delta == 0) return HAL_OK;

    int8_t dir = (delta > 0) ? +1 : -1;
    HAL_StatusTypeDef ret = motion_start((uint32_t)abs(delta),
                                          MAX_SPEED_MM_S, MAX_ACCEL_MM_S2, dir);
    if (ret != HAL_OK) return ret;
    return motion_wait(30000);
}
```

### 测试验证步骤

```
1. 上电测试：
   - 确认DRV8825 FAULT引脚为高（无故障）
   - 用万用表测量VREF引脚电压（应为0.85V，对应1.7A）

2. 手动步进测试：
   - 发送命令：G0 X10（移动10mm）
   - 用卡尺测量实际位移，应为10.0±0.1mm

3. 回零测试：
   - 发送 HOME 命令
   - 观察电机向负方向运动，触碰限位后后退，再次精确触碰
   - 完成后发送 M114，应报告 X:5.000 mm

4. 往复运动测试：
   - 循环执行：G0 X100 → G0 X10 → G0 X100
   - 运行100次后检查位置误差（应 < 0.1mm）

5. 限位保护测试：
   - 手动触发限位开关，确认电机立即停止
```


## 常见问题与调试

### 问题1：共振/振动（Resonance / Vibration）

**现象**：电机在特定速度下发出异常噪声，振动加剧，甚至失步。

**根本原因**：步进电机固有频率与步进频率接近时发生共振。

```
诊断方法：
  1. 缓慢增加速度，记录出现振动的速度区间
  2. 典型共振区：50~200 steps/s（低频），500~1000 steps/s（中频）
  3. 用示波器观察电机绕组电流波形，共振时波形不规则
```

**解决方案**：

| 方案 | 效果 | 成本 |
|------|------|------|
| 增大细分数（如从1/8改为1/16） | 显著减小振动 | 无额外成本 |
| 快速通过共振区（增大加速度） | 减少在共振区停留时间 | 无额外成本 |
| 降低电流（减小保持转矩） | 降低共振幅度 | 可能影响负载能力 |
| 添加机械阻尼（橡胶垫） | 吸收振动能量 | 低成本 |
| 使用TMC2209 SpreadCycle模式 | 电气阻尼，效果最佳 | 需更换驱动芯片 |

```c
// 软件方案：共振区速度跳跃
// 在加速过程中快速跳过共振区
void motion_plan_skip_resonance(uint32_t steps, float v_max) {
    // 已知共振区：150~300 steps/s
    const float RES_LOW  = 150.0f;
    const float RES_HIGH = 300.0f;

    if (v_max <= RES_LOW) {
        // 目标速度在共振区以下，正常运行
        motion_plan(steps, v_max, v_max * 8.0f);
    } else {
        // 使用大加速度快速通过共振区
        // 加速度足够大，使在共振区内的时间 < 0.1s
        float accel = (RES_HIGH - 100.0f) / 0.05f;  // 0.05s内通过
        motion_plan(steps, v_max, accel);
    }
}
```

### 问题2：丢步（Missed Steps / Step Loss）

**现象**：运动结束后实际位置与命令位置不符，累积误差越来越大。

**常见原因及解决方案**：

```
原因1：加速度过大
  症状：高速运动时偶发丢步
  解决：降低加速度（减小 accel 参数）
  验证：accel = v_max × 3（保守值）

原因2：电流不足
  症状：负载较大时丢步
  解决：提高VREF电压（增大电流限制）
  注意：不超过电机额定电流，否则过热

原因3：电源电压不足
  症状：高速时丢步
  解决：提高电源电压（12V→24V）
  原理：高速时反电动势大，需要更高电压驱动电流

原因4：机械阻力过大
  症状：特定位置丢步
  解决：检查导轨润滑、丝杆预紧力、联轴器对中

原因5：定时器中断被抢占
  症状：随机丢步，与负载无关
  解决：提高步进定时器中断优先级
```

```c
// 丢步检测：通过编码器验证
void verify_position_with_encoder(void) {
    int32_t cmd_pos = current_position;
    int32_t enc_pos = mm_to_steps(steps_to_mm(encoder_get_count() / ENCODER_RATIO));
    int32_t error   = cmd_pos - enc_pos;

    if (abs(error) > 5) {  // 超过5步认为丢步
        printf("警告：位置误差 %ld steps（%.3f mm）\r\n",
               (long)error, steps_to_mm(error));
        // 修正位置
        current_position = enc_pos;
    }
}
```

### 问题3：加速度过激进（Acceleration Too Aggressive）

**现象**：电机启动时发出"咔哒"声，或在加速段开始时失步。

**诊断**：

```
加速度合理性检验：
  最大可用加速度 = (T_hold × η - T_load) / J_total

  其中：
    T_hold  = 保持转矩 (N·m)
    η       = 效率系数（0.5~0.8）
    T_load  = 负载转矩 (N·m)
    J_total = 总转动惯量 (kg·m²)

  例：NEMA17，T_hold=0.4N·m，η=0.6，T_load=0.1N·m
    J_rotor = 68 g·cm² = 6.8×10⁻⁶ kg·m²
    J_load  = m × r² = 0.5kg × (0.004m)² = 8×10⁻⁶ kg·m²（T8丝杆）
    J_total = 14.8×10⁻⁶ kg·m²

    a_max = (0.4×0.6 - 0.1) / 14.8×10⁻⁶ = 13500 rad/s²
    换算为 steps/s²：13500 × (200×16) / (2π) ≈ 6.9×10⁶ steps/s²

  实际使用时取理论值的30%~50%作为安全余量
```

**调试步骤**：

```
步骤1：从保守值开始
  accel = v_max × 3  （加速时间约0.33s）

步骤2：逐步增大，每次增加20%
  accel = v_max × 3.6, 4.3, 5.2, 6.2...

步骤3：找到失步临界点
  记录开始出现失步的加速度值 accel_critical

步骤4：设置工作值
  accel_work = accel_critical × 0.7  （70%安全余量）

步骤5：温度验证
  在工作温度范围内（-20°C~60°C）重复测试
  高温时转矩下降约10%，需要额外余量
```

### 问题4：电机过热

**现象**：电机外壳温度超过60°C，长时间运行后性能下降。

```
原因分析：
  步进电机在静止时仍然通全电流（保持转矩）
  铜损 P = I² × R（绕组电阻）
  例：NEMA17，I=1.7A，R=1.5Ω → P = 4.3W（每相）

解决方案：
  1. 静止时降低电流（Hold Current Reduction）
     DRV8825：通过DECAY引脚或软件控制
     TMC2209：IHOLD寄存器设置为运行电流的50%

  2. 使用PWM电流控制（DRV8825默认支持）
     自动根据负载调整电流

  3. 添加散热片（铝制散热片，导热硅脂）
```

```c
// 静止时自动降低电流（通过使能引脚PWM控制）
// 注意：DRV8825不支持直接电流调节，此方案适用于支持电流调节的驱动器

// 对于DRV8825，可以在静止时禁用驱动器（失去保持转矩）
void motor_idle_mode(uint8_t enable_hold) {
    if (enable_hold) {
        motor_enable();  // 全电流保持
    } else {
        motor_disable(); // 断电，无保持转矩（适合垂直轴以外的场景）
    }
}
```

### 问题5：限位开关抖动（Switch Bounce）

**现象**：触碰限位开关时，电机停止后又短暂运动，或触发多次中断。

```c
// 硬件消抖：在限位开关引脚并联100nF电容到GND
// 软件消抖：检测到限位后延时确认

uint8_t limit_neg_debounced(void) {
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_7) == GPIO_PIN_RESET) {
        HAL_Delay(5);  // 5ms消抖
        return HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_7) == GPIO_PIN_RESET;
    }
    return 0;
}
```

### 调试工具推荐

```
1. 逻辑分析仪（推荐：Saleae Logic 8）
   - 捕获STEP/DIR信号，验证脉冲时序
   - 测量脉冲宽度，确认满足DRV8825最小要求

2. 示波器（推荐：DS1054Z）
   - 观察电机绕组电流波形
   - 检测共振时的电流异常

3. 串口调试助手
   - 实时监控位置、速度、故障状态
   - 发送G-code命令测试

4. 万用表
   - 测量VREF电压（电流设置）
   - 检查电源电压（负载下的压降）
```


## 测试与验证

### 单元测试：梯形曲线参数计算

```c
// 验证梯形曲线参数计算的正确性
void test_trapezoid_params(void) {
    // 测试用例1：有匀速段
    // v_start=200, v_max=2000, accel=10000, steps=5000
    float v_start = 200.0f, v_max = 2000.0f, accel = 10000.0f;
    uint32_t steps = 5000;

    float accel_steps = (v_max*v_max - v_start*v_start) / (2.0f * accel);
    // 期望：(4000000 - 40000) / 20000 = 198 steps
    assert(fabsf(accel_steps - 198.0f) < 1.0f);

    // 加速+减速步数 = 396 < 5000，有匀速段
    assert(accel_steps * 2 < steps);

    // 测试用例2：无匀速段（三角形曲线）
    steps = 200;
    if (accel_steps * 2 >= steps) {
        accel_steps = steps / 2;
        float v_peak = sqrtf(v_start*v_start + accel * accel_steps);
        // 期望：sqrt(40000 + 10000*100) = sqrt(1040000) ≈ 1019.8
        assert(v_peak < v_max);
        assert(v_peak > v_start);
    }

    printf("梯形曲线参数测试通过\r\n");
}
```

### 属性测试：速度始终在合法范围内

```c
// 属性：在整个运动过程中，速度始终在 [v_start, v_max] 范围内
// Feature: motion-control-algorithms, Property 1: Speed bounds invariant
void property_speed_bounds(void) {
    float v_start = 200.0f, v_max = 2000.0f, accel = 10000.0f;
    uint32_t steps = 5000;

    // 模拟运动过程
    float speed = v_start;
    uint32_t accel_s = (uint32_t)((v_max*v_max - v_start*v_start) / (2.0f*accel));
    uint32_t decel_start = steps - accel_s;

    for (uint32_t i = 0; i < steps; i++) {
        // 断言：速度始终在合法范围内
        assert(speed >= v_start * 0.99f);  // 允许1%浮点误差
        assert(speed <= v_max * 1.01f);

        if (i < accel_s) {
            float ns = sqrtf(speed*speed + 2.0f*accel);
            if (ns > v_max) ns = v_max;
            speed = ns;
        } else if (i < decel_start) {
            speed = v_max;
        } else {
            float v2 = speed*speed - 2.0f*accel;
            speed = (v2 > v_start*v_start) ? sqrtf(v2) : v_start;
        }
    }
    printf("速度边界属性测试通过（%lu步）\r\n", (unsigned long)steps);
}
```

## 延伸阅读

- [多轴同步控制](03-multi-axis-sync.html) — 多电机协调运动、Bresenham插补
- [步进电机控制基础](../beginner/02-stepper-motor-control.html) — 回顾步进电机全步/半步驱动
- [编码器接口](../../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/04-encoder-interface.html) — 闭环反馈、位置测量
- [智能小车控制](01-smart-car-control.html) — 运动控制在移动机器人中的应用
- [智能云台项目](04-smart-gimbal-project.html) — 高精度角度控制
- [机械臂项目](05-robot-arm-project.html) — 多轴协调运动规划

## 参考资料

1. 《运动控制系统》— 阮毅、陈伯时，机械工业出版社
2. David Austin — "Generate stepper-motor speed profiles in real time" (Embedded Systems Programming, 2004)
3. Grbl开源固件 — CNC运动控制参考实现（GitHub: gnea/grbl）
4. Marlin固件 — 3D打印机运动控制参考实现（GitHub: MarlinFirmware/Marlin）
5. 《数控技术》— 廖效果，华中科技大学出版社
6. Klipper固件 — 高速3D打印控制（github.com/Klipper3d/klipper）
7. Singer, N.C. — "Residual Vibration Reduction in Computer Controlled Machines" (MIT, 1989)
8. TI DRV8825数据手册 — SLVSA73E，Texas Instruments
9. Trinamic TMC2209数据手册 — TMC2209_datasheet_rev1.09
10. 《步进电机应用技术》— 孙冬梅，电子工业出版社
11. Jerk-limited motion profiles — "Smooth Motion Control" (Automation Technology, 2018)
12. NEMA17 17HS4401数据手册 — Stepperonline产品规格书
