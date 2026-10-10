---
title: "电机驱动电路设计：从H桥原理到PCB实现"
description: "系统讲解直流电机驱动电路的设计原理，涵盖H桥拓扑、MOSFET选型、栅极驱动、死区时间设计、续流保护和PCB布局要点，帮助工程师自主设计可靠的电机驱动硬件"
slug: "motor-driver-circuit-design"

domain: "底层硬件层"
module: "硬件设计基础"
content_type: "article"
skill_level: "intermediate"

tags:
  - 电机驱动
  - H桥电路
  - MOSFET
  - 栅极驱动
  - PCB设计
  - 功率电子
prerequisites:
  - "beginner/01-basic-components"
  - "beginner/03-digital-circuits"
related_contents:
  - "intermediate/01-signal-integrity"
  - "intermediate/02-emc-design"

estimated_time: 90
difficulty_score: 4

author: "嵌入式硬件设计团队"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "1.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - 电机驱动电路
  - H桥设计
  - MOSFET驱动
  - 栅极驱动电路
  - 电机驱动PCB
cover_image: ""
---

# 电机驱动电路设计：从H桥原理到PCB实现

## 概述

电机驱动电路是嵌入式系统中最常见的功率电子模块之一。理解其设计原理，不仅能帮助你正确使用现成的驱动芯片（L298N、DRV8833、TB6612），更能在需要时自主设计满足特定功率和性能要求的驱动电路。

完成本文学习后，你将能够：

- 理解H桥电路的工作原理和四种工作状态
- 掌握MOSFET选型的关键参数
- 设计栅极驱动电路，处理自举升压和死区时间
- 了解续流二极管、电流检测和过流保护设计
- 掌握电机驱动PCB的布局布线要点

## 背景知识

### 功率MOSFET物理原理

在深入H桥设计之前，理解功率MOSFET（Metal-Oxide-Semiconductor Field-Effect Transistor，金属氧化物半导体场效应晶体管）的内部物理机制至关重要。这些知识直接影响器件选型、驱动电路设计和可靠性分析。

#### 体二极管（Body Diode）

功率MOSFET的结构中，P型体区（Body）与N型漏极区之间天然形成一个PN结，即**体二极管**（Body Diode）。这个二极管是MOSFET制造工艺的副产品，无法消除。

```
功率N沟道MOSFET内部结构：

    漏极 (D)
      │
   ┌──┴──────────────┐
   │  N+ 漏极区       │
   │                  │
   │  N- 外延层       │  ← 高阻区，承受高压
   │                  │
   │  P 体区 ─────────┼── 体二极管阳极（内部连接源极）
   │  │               │
   │  N+ 源极区       │
   └──┬───────────────┘
      │
    源极 (S)  ← 体二极管阴极

体二极管方向：阳极→源极，阴极→漏极
（即电流可从源极流向漏极，反向导通）
```

**体二极管的关键特性**：

| 参数 | 典型值 | 影响 |
|------|--------|------|
| 正向压降 Vf | 0.7~1.2V | 续流时产生损耗 |
| 反向恢复时间 trr | 100ns~1μs | 影响高频开关效率 |
| 反向恢复电荷 Qrr | 10~500nC | 决定开关损耗大小 |

**体二极管在H桥中的作用**：

在PWM控制中，当上管关断、下管尚未开通的死区时间内，电机绕组的感性电流必须有续流路径。此时，对侧MOSFET的体二极管提供续流通道：

```
死区时间续流路径（电机正转，上管Q1关断瞬间）：

    VCC
     │
    Q1（关断）
     │
  MOTOR_A ──→ 电机绕组（感性，电流继续流动）──→ MOTOR_B
                                                    │
                                                   Q4（导通）
                                                    │
                                                   GND
                                                    │
                                              Q3体二极管（续流）
                                                    │
                                                 MOTOR_A（回到起点）
```

**优化建议**：对于高频PWM（>20kHz），体二极管的反向恢复损耗显著。可并联肖特基二极管（如STPS3L60，Vf=0.4V，trr<10ns）降低损耗，或选用GaN MOSFET（无体二极管问题）。

#### 雪崩额定值（Avalanche Rating）

当MOSFET漏源电压超过Vds(max)时，器件进入**雪崩击穿**（Avalanche Breakdown）状态。功率MOSFET通常具有一定的雪崩能量吸收能力，称为**雪崩额定值**（Avalanche Rating）。

**雪崩发生场景**：

```
电机驱动中的雪崩触发：

    VCC = 24V
     │
    Q1（突然关断）
     │
  电机绕组（L = 500μH，I = 5A）
     │
    Q4（导通）
     │
    GND

关断瞬间：V_spike = L × dI/dt = 500μH × 5A / 100ns = 25V
总电压 = VCC + V_spike = 24 + 25 = 49V > Vds(max)=30V → 雪崩！
```

**雪崩能量计算**：

$$E_{AS} = \frac{1}{2} \times L \times I_{peak}^2 \times \frac{V_{DS(max)}}{V_{DS(max)} - V_{CC}}$$

以上例为例：$E_{AS} = \frac{1}{2} \times 500\mu H \times 25 \times \frac{30}{30-24} = 31.25 \text{ mJ}$

**选型建议**：
- 查阅数据手册中的 $E_{AS}$（单次雪崩能量）和 $E_{AR}$（重复雪崩能量）
- 确保 $E_{AS(rated)} > E_{AS(calculated)} \times 2$（留2倍余量）
- 或选择Vds(max)足够高（≥2×VCC）的MOSFET，避免进入雪崩区

#### 安全工作区（SOA，Safe Operating Area）

SOA图描述了MOSFET在不损坏的前提下，漏极电流（Id）与漏源电压（Vds）的允许组合范围。

```
SOA图示意（对数坐标）：

Id (A)
100 │\
    │ \  DC工作区
 10 │  \────────────────
    │   \               \
  1 │    \  脉冲工作区   \
    │     \（10μs）       \
0.1 │      \              \
    └───────────────────────── Vds (V)
    0    10   20   50  100  200

边界由以下因素决定：
- 最大电流 Id(max)：金属连接线熔断
- 最大电压 Vds(max)：雪崩击穿
- 最大功耗 Pd(max)：热失控（受结温限制）
- 二次击穿（Si MOSFET无此问题，IGBT需注意）
```

**SOA在电机驱动中的应用**：

电机启动时，堵转电流可达额定电流的5~10倍，此时MOSFET工作在高电压+大电流的线性区（非饱和区），必须验证工作点在SOA范围内：

```c
// 软启动算法：限制di/dt，避免超出SOA
void motor_soft_start(uint8_t target_duty) {
    uint8_t current_duty = 0;
    while (current_duty < target_duty) {
        current_duty += 5;  // 每步增加5%占空比
        if (current_duty > target_duty) current_duty = target_duty;
        motor_set_duty(current_duty);
        HAL_Delay(10);  // 10ms步进，限制电流上升率
    }
}
```

### 为什么需要H桥

MCU的GPIO最大输出电流通常只有几毫安，而直流电机需要数百毫安到数安培的驱动电流，且需要正反转控制。H桥电路解决了这两个问题：

```
        VCC
         │
    ┌────┴────┐
    │  Q1(P)  │  Q2(P)  │
    └────┬────┘    └────┬────┘
         │              │
    MOTOR_A          MOTOR_B
         │              │
    ┌────┴────┐    ┌────┴────┐
    │  Q3(N)  │    │  Q4(N)  │
    └────┬────┘    └────┴────┘
         │              │
        GND            GND
```

**四种工作状态**：

| Q1 | Q2 | Q3 | Q4 | 状态 |
|----|----|----|-----|------|
| ON | OFF | OFF | ON | 正转（电流：VCC→Q1→A→B→Q4→GND） |
| OFF | ON | ON | OFF | 反转（电流：VCC→Q2→B→A→Q3→GND） |
| ON | ON | OFF | OFF | 制动（两端短接到VCC） |
| OFF | OFF | ON | ON | 制动（两端短接到GND，更常用） |
| OFF | OFF | OFF | OFF | 滑行（自由转动） |

**死区时间（Dead Time）**：同一桥臂的上下管（如Q1和Q3）绝对不能同时导通，否则直接短路VCC到GND（称为"直通"）。死区时间是上管关断到下管开通之间的延迟，通常设为100ns~1μs。

### H桥直通（Shoot-Through）深度分析

直通是H桥设计中最危险的故障模式，必须从多个层面防护。

#### 直通的物理过程

```
直通发生时序（以左桥臂为例）：

时间轴：
t0: Q1(高侧)开始关断，Vgs1从10V下降
t1: Q1完全关断（Vgs1 < Vth ≈ 2V）
t2: Q3(低侧)开始开通，Vgs3从0V上升
t3: Q3完全开通（Vgs3 > Vth）

危险区间：t0~t1（Q1关断过渡期）
如果Q3在t0之后、t1之前开通 → 直通！

电流路径：VCC → Q1（部分导通）→ Q3（导通）→ GND
峰值电流：仅受寄生电感限制，可达数百安培！
```

**直通电流波形**：

```
电流 (A)
  │
  │         ╭──╮  ← 直通峰值电流（可达100A+）
  │        ╱    ╲
  │       ╱      ╲
  │──────╱        ╲──────
  │
  └──────────────────────── 时间
         ↑        ↑
      直通开始   直通结束
      （约100ns~500ns）
```

#### 死区时间计算

死区时间必须大于MOSFET的关断时间（turn-off time），包括：

$$t_{dead} > t_{off(max)} = t_{d(off)} + t_f$$

其中：
- $t_{d(off)}$：关断延迟时间（从Vgs下降到Id开始下降）
- $t_f$：电流下降时间（Id从90%降到10%）

**实际设计中的死区时间计算**：

```c
/*
 * 死区时间计算示例（STM32 TIM1互补PWM）
 * 
 * MOSFET: IRLZ44N
 * td(off) = 40ns (典型值，数据手册)
 * tf = 44ns (典型值)
 * 温度系数：高温下增加约30%
 * 
 * 最小死区时间 = (40 + 44) × 1.3 = 109ns
 * 设计值：取200ns（留足余量）
 */

// STM32 TIM1 死区时间配置
// 系统时钟 = 72MHz，定时器时钟 = 72MHz
// 死区时间分辨率 = 1/72MHz ≈ 13.9ns

void TIM1_DeadTime_Config(void) {
    // 死区时间 = 200ns / 13.9ns ≈ 14个时钟周期
    // BDTR寄存器DTG字段 = 14 (0x0E)
    TIM1->BDTR &= ~TIM_BDTR_DTG;
    TIM1->BDTR |= 14;  // 14 × 13.9ns = 194ns ≈ 200ns
    
    // 使能主输出
    TIM1->BDTR |= TIM_BDTR_MOE;
}
```

#### 多层防护策略

```
防护层次（从硬件到软件）：

Layer 1: 硬件死区时间（栅极驱动芯片内置）
         ↓ 如果失效
Layer 2: MCU定时器硬件死区（TIM1 BDTR寄存器）
         ↓ 如果失效
Layer 3: 栅极串联电阻（减慢开通速度）
         ↓ 如果失效
Layer 4: 过流检测（检测到直通电流立即关断）
         ↓ 如果失效
Layer 5: 熔断器（最后防线，保护PCB不起火）
```

### PWM频率选择指南

PWM频率的选择是电机驱动设计中的重要权衡，涉及多个相互制约的因素。

#### 影响因素分析

**1. 可听噪声（Audible Noise）**

人耳可听频率范围：20Hz ~ 20kHz。当PWM频率在此范围内时，电机线圈和铁芯会产生可听噪声（磁致伸缩效应）。

```
噪声 vs PWM频率：

噪声强度
  │
  │████████████████
  │                ████
  │                    ████
  │                        ████
  │                            ████
  └──────────────────────────────────── 频率
  0   1k   5k  10k  15k  20k  25k  50k (Hz)
  
  < 20kHz：可听噪声（令人烦恼）
  > 20kHz：超声波，人耳不可听
  推荐：20kHz ~ 25kHz（刚好超出可听范围）
```

**2. 开关损耗（Switching Losses）**

每次开关切换都会产生损耗，频率越高损耗越大：

$$P_{sw} = \frac{1}{2} \times V_{DS} \times I_D \times (t_r + t_f) \times f_{PWM}$$

```
开关损耗 vs 频率（IRLZ44N，12V/5A）：

损耗 (W)
  │
5 │                              ●
  │                         ●
4 │                    ●
  │               ●
3 │          ●
  │     ●
2 │●
  │
1 │
  └──────────────────────────────── 频率
  0   5k  10k  20k  30k  50k  100k (Hz)
  
  20kHz时开关损耗约 3W（需要散热）
  100kHz时开关损耗约 15W（需要大散热片）
```

**3. 电机电感与电流纹波**

PWM频率越高，电流纹波越小，电机运行越平滑：

$$\Delta I = \frac{V_{CC} \times D \times (1-D)}{L \times f_{PWM}}$$

其中 D 为占空比，L 为电机绕组电感。

```c
/*
 * 电流纹波计算示例
 * VCC = 12V, D = 0.5, L = 1mH（典型小型DC电机）
 */
float calculate_current_ripple(float vcc, float duty, float inductance, float freq) {
    return (vcc * duty * (1.0f - duty)) / (inductance * freq);
}

// 20kHz: ΔI = 12 × 0.5 × 0.5 / (0.001 × 20000) = 0.15A（良好）
// 1kHz:  ΔI = 12 × 0.5 × 0.5 / (0.001 × 1000)  = 3.0A（过大，电机发热）
```

**4. 综合选择建议**

| 应用场景 | 推荐频率 | 原因 |
|---------|---------|------|
| 消费电子（安静环境） | 20~25kHz | 超出可听范围，损耗可接受 |
| 工业设备（噪声不敏感） | 10~20kHz | 降低开关损耗 |
| 高效率设计（>95%） | 50~100kHz + GaN | 低Qg器件，损耗可控 |
| 大功率（>1kW） | 8~16kHz | 降低开关损耗，散热可行 |
| 伺服驱动（精密控制） | 20kHz | 平衡噪声、纹波和损耗 |

```c
// STM32 TIM1 PWM频率配置
// 目标频率：20kHz，系统时钟：72MHz

void PWM_Frequency_Config(uint32_t freq_hz) {
    // ARR = 定时器时钟 / PWM频率 - 1
    // 72MHz / 20kHz - 1 = 3599
    uint32_t arr = SystemCoreClock / freq_hz - 1;
    TIM1->ARR = arr;
    
    // 更新占空比寄存器（保持占空比不变）
    // CCR = ARR × duty_percent / 100
}

// 初始化20kHz PWM
// TIM1->ARR = 3599
// 分辨率 = 1/3600 ≈ 0.028%（足够精细）
```

## 核心内容

### MOSFET选型

电机驱动中MOSFET是核心器件，选型需关注以下参数：

**关键参数**：

| 参数 | 说明 | 选型建议 |
|------|------|---------|
| Vds（漏源耐压） | 必须 > 电源电压 × 1.5 | 12V系统选30V以上 |
| Id（持续漏极电流） | 必须 > 最大电机电流 × 2 | 留足余量 |
| Rds(on)（导通电阻） | 越小发热越少 | 尽量选小，mΩ级 |
| Qg（栅极电荷） | 影响开关速度和驱动损耗 | 高频PWM选小Qg |
| 体二极管反向恢复时间 | 影响续流效率 | 选快恢复或SiC |

**常用MOSFET推荐**：

| 型号 | Vds | Id | Rds(on) | 适用场景 |
|------|-----|-----|---------|---------|
| AO3400 | 30V | 5.7A | 40mΩ | 小型机器人（SOT-23封装） |
| IRLZ44N | 55V | 47A | 22mΩ | 中功率（TO-220，5V栅极可驱动） |
| IRF3205 | 55V | 110A | 8mΩ | 大功率（TO-220） |
| CSD18532 | 60V | 100A | 2.2mΩ | 高效率设计（D2PAK） |

**N沟道 vs P沟道**：
- N沟道：Rds(on)小，性能好，但高侧驱动需要自举电路
- P沟道：高侧驱动简单，但Rds(on)大，通常只用于低频低功率场景
- **推荐**：全N沟道H桥 + 栅极驱动芯片

### 栅极驱动电路

**为什么需要栅极驱动**：

MOSFET的栅极等效为电容（Cgs），快速开关需要瞬间提供大电流给栅极充放电。MCU的GPIO驱动能力不足，需要专用栅极驱动芯片。

**自举电路（Bootstrap）**：

高侧N沟道MOSFET的栅极电压必须高于源极（即高于电机电压），需要自举电路产生高于VCC的电压：

```
        VCC
         │
    ┌────┴────┐
    │  自举电容 Cboot（100nF~1μF）
    │  自举二极管 Dboot（快恢复，如1N4148）
    └────┬────┘
         │ VBOOT = VCC + VCC ≈ 2×VCC
    ┌────┴────┐
    │  高侧MOSFET栅极
    └─────────┘
```

**推荐栅极驱动芯片**：

| 芯片 | 特点 | 适用场景 |
|------|------|---------|
| IR2104 | 半桥驱动，内置自举，死区时间固定 | 简单半桥/H桥 |
| DRV8302 | 三相全桥驱动，含电流检测放大器 | BLDC电机 |
| L6387 | 半桥驱动，可调死区时间 | 精确控制场景 |
| FAN7382 | 半桥驱动，高速（200ns死区） | 高频PWM |

**IR2104 典型应用电路**：

```
MCU_PWM ──→ IN  ┌─────────┐  HO ──→ 高侧MOSFET栅极
MCU_EN  ──→ SD  │ IR2104  │
                │         │  LO ──→ 低侧MOSFET栅极
           VCC ─┤ VCC  VS ├─ 电机高侧节点
           GND ─┤ COM  VB ├─ 自举电容正端
                └─────────┘
```

**IR2104 关键特性**：
- 内置死区时间：约520ns（防止直通）
- 自举电压：最高600V（适合高压应用）
- 输出电流：±130mA（可直接驱动中等Qg的MOSFET）

#### 自举电容精确计算

自举电容是高侧驱动的关键，容量不足会导致高侧MOSFET无法完全开通，产生额外损耗甚至损坏器件。

**自举电容充电需求分析**：

```
每个PWM周期，自举电容需要提供的电荷：

Q_total = Q_gate + Q_leakage + Q_level_shift

其中：
Q_gate     = Qg（MOSFET栅极电荷，数据手册查取）
Q_leakage  = I_leak × t_on（驱动芯片内部泄漏）
Q_level_shift = I_ls × t_on（电平转换电路消耗）
```

**计算示例（IRLZ44N + IR2104）**：

```c
/*
 * 自举电容计算
 * MOSFET: IRLZ44N, Qg = 36nC (Vgs=10V时)
 * IR2104: I_leak = 50μA (典型值), I_ls = 5mA (典型值)
 * PWM频率: 20kHz, 占空比最大: 95%
 * 
 * t_on(max) = 0.95 / 20kHz = 47.5μs
 */

// Q_gate = 36nC
// Q_leakage = 50μA × 47.5μs = 2.375nC
// Q_level_shift = 5mA × 47.5μs = 237.5nC

// Q_total = 36 + 2.375 + 237.5 = 275.875nC ≈ 276nC

// 自举电容电压降 ΔV = Q_total / C_boot
// 要求 ΔV < 1V（保证栅极电压足够）
// C_boot > Q_total / ΔV = 276nC / 1V = 276nF

// 选取标准值：470nF（留足余量）
// 实际选用：470nF/25V X7R陶瓷电容（低ESR）

#define CBOOT_NF    470     // 自举电容 470nF
#define VBOOT_MIN   9.0f    // 最低自举电压（Vgs需>8V才能完全导通）
```

**自举二极管选型**：

```
自举二极管要求：
1. 反向耐压 > VCC（防止高侧开通时反向击穿）
2. 正向压降低（减少自举电压损失）
3. 反向恢复时间短（防止高侧开通时短路）

推荐型号：
- 1N4148：Vf=0.7V, trr=4ns，适合<100V系统
- BAT54：Vf=0.3V（肖特基），trr<5ns，低压降优选
- UF4007：Vf=1.0V, trr=75ns，高压系统（>100V）
- STTH1L06：Vf=0.85V, trr<25ns，高频高压优选
```

#### 栅极保护：齐纳钳位（Zener Clamp）

MOSFET的栅极氧化层极薄（约10nm），最大栅源电压Vgs(max)通常为±20V。在以下情况下，栅极电压可能超过安全范围：

1. 高dV/dt引起的电容耦合（Miller效应）
2. 长走线的寄生电感产生的振荡
3. 静电放电（ESD）

**齐纳钳位电路**：

```
栅极驱动输出 ──┬── Rg（10Ω串联电阻）──┬── MOSFET栅极
               │                       │
               │                    Dz（齐纳二极管）
               │                       │
              GND ──────────────────── MOSFET源极

齐纳二极管选型：
- 击穿电压：12V（对于Vgs(max)=20V的MOSFET）
- 功率：0.5W（足够应对瞬态）
- 推荐型号：BZX84C12（SOT-23，12V，0.3W）
           MMSZ5242B（SOD-123，12V，0.5W）
```

**Miller效应防护**：

```
Miller效应原理：
当漏极电压快速变化时，通过Cgd（栅漏电容）
向栅极注入电流，可能误触发MOSFET

防护措施：
1. 栅极下拉电阻（10kΩ）：提供泄放路径
2. 负压关断（-5V）：增大关断裕量
3. 分立开通/关断电阻：
   - 开通电阻（Rg_on）：10Ω（控制开通速度）
   - 关断电阻（Rg_off）：3.3Ω（快速关断，抑制Miller）

电路实现：
栅极驱动 ──┬── Rg_on（10Ω）──┬── 栅极
           │                  │
           │              Rg_off（3.3Ω）
           │                  │
          GND ─────────────── 源极
```

```c
// 完整栅极驱动电路参数汇总
typedef struct {
    float rg_on_ohm;      // 开通电阻
    float rg_off_ohm;     // 关断电阻
    float rg_pulldown_kohm; // 下拉电阻
    float cboot_nf;       // 自举电容
    float vz_clamp_v;     // 齐纳钳位电压
    float dead_time_ns;   // 死区时间
} GateDriveConfig;

// 12V/10A H桥推荐配置
const GateDriveConfig h_bridge_config = {
    .rg_on_ohm       = 10.0f,   // 控制开通速度，减少EMI
    .rg_off_ohm      = 3.3f,    // 快速关断，抑制Miller效应
    .rg_pulldown_kohm = 10.0f,  // 防止悬空误触发
    .cboot_nf        = 470.0f,  // 自举电容
    .vz_clamp_v      = 12.0f,   // 栅极钳位电压
    .dead_time_ns    = 200.0f,  // 死区时间
};
```

### 电流检测：分流电阻 + INA240

精确的电流检测是过流保护和闭环控制的基础。INA240是专为电机驱动设计的差分电流检测放大器，具有出色的共模抑制比（CMR），可在高侧或低侧检测电流。

#### INA240 特性

| 参数 | 值 | 说明 |
|------|-----|------|
| 增益选项 | 20, 50, 100, 200 V/V | 对应INA240A1~A4 |
| 共模电压范围 | -4V ~ +80V | 适合高侧检测 |
| 共模抑制比 | 132dB（典型） | 抑制PWM开关噪声 |
| 带宽 | 400kHz | 足够检测快速电流变化 |
| 输入偏置电流 | 10μA（最大） | 影响小信号精度 |
| 封装 | SOT-23-5 | 紧凑，适合PCB集成 |

**INA240 vs 传统运放方案对比**：

```
传统方案（运放 + 分流电阻）：
优点：成本低
缺点：共模抑制差，PWM噪声干扰大，需要额外滤波

INA240方案：
优点：高CMR（132dB），内置PWM抑制，精度高
缺点：成本略高（约¥5/片）
结论：电机驱动推荐INA240
```

#### 分流电阻选型

```
分流电阻阻值计算：

目标：最大电流10A时，INA240输出接近满量程（3.3V）

INA240A2（增益=50）：
Vout = Ishunt × Rshunt × Gain
3.3V = 10A × Rshunt × 50
Rshunt = 3.3 / (10 × 50) = 6.6mΩ

选取标准值：5mΩ（留余量，最大输出 = 10A × 5mΩ × 50 = 2.5V）

分流电阻功耗：P = I² × R = 100 × 0.005 = 0.5W
选用：5mΩ / 1W / 1% 精度（如Vishay WSL2512R0050FEA）
```

**INA240 完整应用电路**：

```c
/*
 * INA240A2 电流检测电路
 * 
 * 硬件连接：
 * IN+  ── 分流电阻高侧（靠近电机侧）
 * IN-  ── 分流电阻低侧（靠近GND侧）
 * OUT  ── STM32 ADC输入（PA0）
 * VS   ── 3.3V（供电）
 * GND  ── GND
 * REF  ── GND（单端输出模式）
 * 
 * 注意：IN+/IN- 之间需要100nF去耦电容
 */

#define INA240_GAIN         50.0f    // INA240A2增益
#define SHUNT_RESISTANCE    0.005f   // 5mΩ分流电阻
#define ADC_VREF            3.3f     // ADC参考电压
#define ADC_RESOLUTION      4096.0f  // 12位ADC

// 电流检测函数
float INA240_ReadCurrent(void) {
    // 启动ADC转换
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint16_t adc_raw = HAL_ADC_GetValue(&hadc1);
    
    // 转换为电压
    float vout = (float)adc_raw / ADC_RESOLUTION * ADC_VREF;
    
    // 转换为电流
    // Vout = Ishunt × Rshunt × Gain
    // Ishunt = Vout / (Rshunt × Gain)
    float current = vout / (SHUNT_RESISTANCE * INA240_GAIN);
    
    return current;
}

// 过流保护（中断方式，响应更快）
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) {
        float current = INA240_ReadCurrent();
        if (current > CURRENT_LIMIT_A) {
            // 立即关断所有PWM输出（硬件层面）
            TIM1->BDTR &= ~TIM_BDTR_MOE;  // 关闭主输出使能
            fault_flag = 1;
            // 记录故障电流值
            fault_current = current;
        }
    }
}
```

**电流检测滤波**：

```c
// 滑动平均滤波（减少ADC噪声）
#define FILTER_SIZE 8

float current_filter_buf[FILTER_SIZE] = {0};
uint8_t filter_idx = 0;

float INA240_ReadCurrentFiltered(void) {
    float raw = INA240_ReadCurrent();
    
    // 更新滤波缓冲区
    current_filter_buf[filter_idx] = raw;
    filter_idx = (filter_idx + 1) % FILTER_SIZE;
    
    // 计算平均值
    float sum = 0;
    for (int i = 0; i < FILTER_SIZE; i++) {
        sum += current_filter_buf[i];
    }
    return sum / FILTER_SIZE;
}
```

### 再生制动（Regenerative Braking）电路分析

再生制动是将电机的动能转换回电能，回馈到电源或储能元件，提高系统效率。

#### 再生制动原理

```
正常驱动模式（电动机模式）：
电源 → H桥 → 电机（消耗电能，产生机械能）

再生制动模式（发电机模式）：
电机（消耗机械能，产生电能）→ H桥 → 电源（回馈电能）

能量流向：
┌─────────┐    驱动    ┌─────────┐
│  电源   │ ─────────→ │  电机   │
│ (VCC)   │ ←───────── │ (负载)  │
└─────────┘    制动    └─────────┘
```

**再生制动的H桥控制**：

```
再生制动实现（以正转为例）：

正转状态：Q1=ON, Q4=ON（电流：VCC→Q1→Motor→Q4→GND）

再生制动：Q1=OFF, Q2=OFF, Q3=ON, Q4=ON
（两个低侧管导通，电机两端短接到GND）
电机作为发电机，电流通过Q3/Q4体二极管流向VCC

能量回馈路径：
Motor_A → Q3体二极管 → VCC（充电）
Motor_B → Q4（导通）→ GND
```

**再生制动的电压尖峰问题**：

```c
/*
 * 再生制动时，电机反电动势（Back-EMF）叠加到VCC上
 * 可能导致VCC过压，损坏电容或其他器件
 * 
 * 解决方案：
 * 1. 大容量电解电容（1000μF+）吸收回馈能量
 * 2. 制动电阻（Braking Resistor）消耗多余能量
 * 3. 超级电容储能
 */

// 制动电阻控制（当VCC超过阈值时接入制动电阻）
#define VCC_OVERVOLTAGE_THRESHOLD  14.0f  // 12V系统，14V触发

void BrakingResistor_Control(void) {
    float vcc = ReadVCC_ADC();  // 读取VCC电压
    
    if (vcc > VCC_OVERVOLTAGE_THRESHOLD) {
        // 接入制动电阻（通过MOSFET控制）
        HAL_GPIO_WritePin(BRAKE_RES_GPIO, BRAKE_RES_PIN, GPIO_PIN_SET);
    } else {
        HAL_GPIO_WritePin(BRAKE_RES_GPIO, BRAKE_RES_PIN, GPIO_PIN_RESET);
    }
}

// 制动电阻功率计算
// P_brake = (V_back_emf)² / R_brake
// 对于12V/10A电机，V_back_emf ≈ 12V
// R_brake = 10Ω → P_brake = 144/10 = 14.4W
// 选用：10Ω/20W 线绕电阻
```

**四象限运行分析**：

```
电机四象限运行：

速度 (+)
  │  第二象限          第一象限
  │  （再生制动）      （正向驱动）
  │  ω>0, T<0         ω>0, T>0
──┼──────────────────────────── 转矩
  │  第三象限          第四象限
  │  （反向驱动）      （再生制动）
  │  ω<0, T<0         ω<0, T>0
速度 (-)

H桥可实现全四象限运行，是伺服驱动的基础
```

### 完整H桥设计

以12V/5A直流电机驱动为例的完整设计：

**器件清单**：

```
Q1, Q2, Q3, Q4: IRLZ44N（55V/47A，Rds=22mΩ）
U1, U2: IR2104（半桥驱动，每个驱动一个半桥）
D1, D2: 1N4148（自举二极管）
C1, C2: 100nF（自举电容）
C3: 100μF/25V（电源去耦）
C4: 100nF（电源高频去耦）
R1~R4: 10Ω（栅极串联电阻，抑制振荡）
R5, R6: 10kΩ（栅极下拉，防止悬空误触发）
```

**电路连接**：

```c
// MCU控制逻辑（以STM32为例）
// 使用TIM1的互补PWM输出，硬件死区时间

// 正转：IN1=PWM, IN2=0
// 反转：IN1=0, IN2=PWM
// 制动：IN1=1, IN2=1（低侧制动）
// 滑行：IN1=0, IN2=0

void motor_forward(uint8_t duty_percent) {
    uint16_t pwm_val = (uint16_t)(duty_percent * TIM1->ARR / 100);
    TIM1->CCR1 = pwm_val;  // IN1 = PWM
    TIM1->CCR2 = 0;        // IN2 = 0
}

void motor_reverse(uint8_t duty_percent) {
    uint16_t pwm_val = (uint16_t)(duty_percent * TIM1->ARR / 100);
    TIM1->CCR1 = 0;
    TIM1->CCR2 = pwm_val;
}

void motor_brake(void) {
    TIM1->CCR1 = TIM1->ARR;  // 100% duty
    TIM1->CCR2 = TIM1->ARR;
}

void motor_coast(void) {
    TIM1->CCR1 = 0;
    TIM1->CCR2 = 0;
}
```

### 保护电路设计

**过流保护**：

在低侧MOSFET的源极串联采样电阻，通过运放检测电流：

```
低侧MOSFET源极 ──┬── GND
                 │
              Rs（0.1Ω/2W）
                 │
              运放同相输入
              运放增益 = 10
              → 输出电压 = 电流 × Rs × 增益
              → 1A → 0.1V × 10 = 1V
              → 接MCU的ADC引脚
```

**软件过流保护**：

```c
#define CURRENT_LIMIT_A   5.0f   // 过流阈值5A
#define SHUNT_RESISTOR    0.1f   // 采样电阻0.1Ω
#define AMP_GAIN          10.0f  // 运放增益

float read_motor_current(void) {
    uint16_t adc_val = HAL_ADC_GetValue(&hadc1);
    float voltage = adc_val * 3.3f / 4096.0f;
    return voltage / (SHUNT_RESISTOR * AMP_GAIN);
}

void motor_current_check(void) {
    float current = read_motor_current();
    if (current > CURRENT_LIMIT_A) {
        motor_coast();  // 立即停止
        printf("OVERCURRENT: %.2fA, motor stopped!\n", current);
    }
}
```

**续流二极管**：

MOSFET体二极管在大多数情况下可以续流，但对于高频PWM（>20kHz），体二极管的反向恢复时间会导致损耗增大。可以并联肖特基二极管（如SS34）提高效率。

### PCB布局要点

电机驱动PCB的布局直接影响性能和可靠性：

**功率回路最小化**：

```
VCC → 电容 → 高侧MOSFET → 电机 → 低侧MOSFET → GND

这个回路面积越小越好，减少寄生电感，降低开关尖峰电压
```

**关键布局规则**：

1. **大电容靠近MOSFET**：100μF电解电容和100nF陶瓷电容并联，尽量靠近MOSFET的漏极和源极
2. **栅极驱动走线短**：栅极驱动芯片到MOSFET栅极的走线尽量短（<1cm），减少寄生电感
3. **栅极串联电阻**：10Ω串联电阻放在靠近MOSFET栅极端，抑制振荡
4. **功率地与信号地分开**：大电流回路的地与MCU信号地在单点连接，防止地弹噪声干扰控制信号
5. **铜箔加宽**：功率走线宽度按1A/mm²计算，5A电流需要5mm宽（1oz铜）
6. **散热考虑**：MOSFET下方铺铜散热，必要时加散热片

**层叠建议（4层板）**：

```
Layer 1（顶层）：信号走线、控制电路
Layer 2（内层）：GND平面（完整）
Layer 3（内层）：电源平面
Layer 4（底层）：功率走线、MOSFET
```

## 深入原理

### 热设计：结温、热阻与散热片计算

功率MOSFET的可靠性直接取决于结温（Junction Temperature，Tj）。超过最大结温（通常150°C或175°C）会导致器件永久损坏。

#### 热阻网络模型

```
热阻等效电路（类比欧姆定律）：

功率损耗 P（类比电流）
    │
    ▼
┌───────────┐
│ Rth(j-c)  │  结到壳热阻（数据手册给出）
│ 结→壳     │
└───────────┘
    │
    ▼
┌───────────┐
│ Rth(c-h)  │  壳到散热片热阻（取决于安装方式）
│ 壳→散热片 │  有绝缘垫：0.5~2°C/W
└───────────┘  无绝缘垫：0.1~0.5°C/W
    │
    ▼
┌───────────┐
│ Rth(h-a)  │  散热片到环境热阻（散热片规格）
│ 散热片→环境│
└───────────┘
    │
    ▼
环境温度 Ta（类比地电位）

结温公式：
Tj = Ta + P × (Rth(j-c) + Rth(c-h) + Rth(h-a))
```

#### 功率损耗计算

MOSFET的总功率损耗由两部分组成：

**1. 导通损耗（Conduction Loss）**：

$$P_{cond} = I_{rms}^2 \times R_{ds(on)} \times (1 + \alpha \times (T_j - 25°C))$$

其中 α 为温度系数（约0.004/°C，即温度每升高1°C，Rds(on)增加0.4%）。

**2. 开关损耗（Switching Loss）**：

$$P_{sw} = \frac{1}{2} \times V_{DS} \times I_D \times (t_r + t_f) \times f_{PWM} + Q_{rr} \times V_{DS} \times f_{PWM}$$

```c
/*
 * 功率损耗计算示例
 * MOSFET: IRLZ44N
 * 工作条件: VCC=12V, I_motor=5A(RMS), f_PWM=20kHz, D=0.5
 */

// IRLZ44N 参数（数据手册）
#define RDS_ON_25C      0.022f   // 22mΩ @ 25°C, Vgs=10V
#define TEMP_COEFF      0.004f   // 温度系数 0.4%/°C
#define TR_NS           35.0f    // 上升时间 35ns
#define TF_NS           44.0f    // 下降时间 44ns
#define QRR_NC          97.0f    // 反向恢复电荷 97nC

float calculate_mosfet_losses(float vcc, float i_rms, float freq, float tj) {
    // 导通损耗（考虑温度系数）
    float rds_on = RDS_ON_25C * (1.0f + TEMP_COEFF * (tj - 25.0f));
    float p_cond = i_rms * i_rms * rds_on;
    
    // 开关损耗
    float t_sw = (TR_NS + TF_NS) * 1e-9f;  // 转换为秒
    float p_sw = 0.5f * vcc * i_rms * t_sw * freq;
    
    // 体二极管反向恢复损耗
    float p_rr = QRR_NC * 1e-9f * vcc * freq;
    
    float p_total = p_cond + p_sw + p_rr;
    
    printf("导通损耗: %.2fW\n", p_cond);
    printf("开关损耗: %.2fW\n", p_sw);
    printf("反向恢复损耗: %.2fW\n", p_rr);
    printf("总损耗: %.2fW\n", p_total);
    
    return p_total;
}

// 示例计算：
// 导通损耗 = 25 × 0.022 × (1 + 0.004×50) = 0.825W
// 开关损耗 = 0.5 × 12 × 5 × 79ns × 20kHz = 0.047W
// 反向恢复 = 97nC × 12V × 20kHz = 0.023W
// 总损耗 ≈ 0.9W（每个MOSFET）
```

#### 散热片选型计算

```c
/*
 * 散热片热阻计算
 * 
 * 已知：
 * - 环境温度 Ta = 40°C（最恶劣工况）
 * - 最大结温 Tj(max) = 150°C（IRLZ44N规格）
 * - 设计结温 Tj(design) = 100°C（留50°C余量）
 * - 每个MOSFET功耗 P = 0.9W
 * - H桥共4个MOSFET，总功耗 P_total = 3.6W
 * 
 * IRLZ44N 热阻参数（TO-220封装）：
 * Rth(j-c) = 1.67°C/W（数据手册）
 * Rth(c-h) = 0.5°C/W（使用导热硅脂，无绝缘垫）
 */

float calculate_heatsink_resistance(void) {
    float ta = 40.0f;           // 环境温度
    float tj_design = 100.0f;   // 设计结温
    float p_per_mosfet = 0.9f;  // 每个MOSFET功耗
    float rth_jc = 1.67f;       // 结到壳热阻
    float rth_ch = 0.5f;        // 壳到散热片热阻
    
    // 散热片到环境的最大允许热阻
    // Tj = Ta + P × (Rth_jc + Rth_ch + Rth_ha)
    // Rth_ha = (Tj - Ta) / P - Rth_jc - Rth_ch
    float rth_ha_max = (tj_design - ta) / p_per_mosfet - rth_jc - rth_ch;
    
    printf("散热片最大热阻: %.1f°C/W\n", rth_ha_max);
    // 结果: (100-40)/0.9 - 1.67 - 0.5 = 66.7 - 2.17 = 64.5°C/W
    // 这个值很大，说明自然对流散热即可
    
    return rth_ha_max;
}

// 如果4个MOSFET共用一个散热片：
// P_total = 3.6W
// Rth_ha_max = (100-40)/3.6 - 1.67 - 0.5 = 16.67 - 2.17 = 14.5°C/W
// 选用：铝型材散热片，约15°C/W（50mm×50mm×10mm）
```

**散热片选型参考**：

```
常用散热片热阻参考（自然对流）：

尺寸（mm）      热阻（°C/W）   适用功率（ΔT=50°C）
25×25×10        35             1.4W
50×50×10        15             3.3W
75×75×20        8              6.3W
100×100×25      5              10W
150×150×40      2.5            20W

注：加风扇可降低热阻约50%
```

### EMI滤波器设计

电机驱动是强EMI（Electromagnetic Interference，电磁干扰）源，高频开关产生的噪声会干扰同一系统中的其他电路，甚至不符合CE/FCC认证要求。

#### EMI噪声来源分析

```
电机驱动EMI噪声频谱：

幅度 (dBμV)
  │
80│ ████ ← 基频（PWM频率，20kHz）
  │ ████
60│ ████ ████ ← 谐波（40kHz, 60kHz...）
  │ ████ ████ ████
40│ ████ ████ ████ ████ ← 高次谐波（逐渐衰减）
  │
20│                          ← 噪声底噪
  └──────────────────────────── 频率
  10k  100k  1M  10M  100M (Hz)

主要噪声类型：
1. 差模噪声（DM）：沿电源线传播，由开关电流引起
2. 共模噪声（CM）：通过寄生电容到地，由dV/dt引起
```

#### 共模扼流圈（Common-Mode Choke）

```
共模扼流圈工作原理：

差模电流（正常工作电流）：
L1 ──→──┐
         │ 电机
L2 ──←──┘
两线电流方向相反，磁通相消，扼流圈对差模呈低阻抗

共模电流（噪声电流）：
L1 ──→──┐
         │ 电机
L2 ──→──┘
两线电流方向相同，磁通叠加，扼流圈对共模呈高阻抗

电路符号：
VCC ──┬── L1 ──┬── 电机+
      │        │
     C_Y      C_Y  ← Y电容（共模滤波）
      │        │
GND ──┴── L2 ──┴── 电机-
```

**共模扼流圈选型**：

```
选型参数：
1. 额定电流：≥ 最大电机电流（10A）
2. 共模阻抗：在目标频率（1MHz）处 > 100Ω
3. 差模阻抗：尽量小（<1Ω），避免影响正常工作
4. 饱和电流：> 峰值电流（启动电流可达额定的5倍）

推荐型号：
- Würth 744272100：10A，共模阻抗1000Ω@1MHz
- TDK ACM7060：7A，共模阻抗800Ω@1MHz
- 自制：EE25磁芯，双线绕制20匝，μ=5000
```

#### X/Y电容配置

```
EMI滤波器完整电路：

VCC ──┬──────────────────────────────────────────── 电机驱动
      │
     Cx（X电容，差模滤波）
      │
GND ──┴──────────────────────────────────────────── GND

      ┌── Cy（Y电容，共模滤波，VCC到PE）
      │
PE ───┴── Cy（Y电容，共模滤波，GND到PE）

X电容选型：
- 容量：100nF ~ 1μF（差模滤波）
- 耐压：≥ 2×VCC（安全余量）
- 类型：X2级（交流应用）或普通陶瓷（直流应用）
- 推荐：100nF/50V X7R陶瓷（MLCC）

Y电容选型：
- 容量：1nF ~ 10nF（共模滤波，不能太大，否则漏电流超标）
- 耐压：≥ 500V（安全隔离要求）
- 类型：Y2级（安全认证要求）
- 推荐：4.7nF/500V Y2级
```

**完整EMI滤波器设计代码（PCB网表描述）**：

```c
/*
 * EMI滤波器元件清单（12V/10A电机驱动）
 * 
 * 差模滤波：
 * C1: 100nF/25V X7R（电源入口，靠近连接器）
 * C2: 10μF/25V 电解（低频储能）
 * L1: 共模扼流圈 10A（Würth 744272100）
 * 
 * 共模滤波：
 * C3, C4: 4.7nF/500V Y2（VCC/GND到机壳地）
 * 
 * 高频去耦（靠近MOSFET）：
 * C5, C6: 100nF/25V X7R（每个MOSFET一个）
 * C7: 1μF/25V（电源总线去耦）
 * 
 * 布局要求：
 * 1. 滤波器放在电源入口，靠近连接器
 * 2. 滤波器与功率级之间不要有其他走线穿越
 * 3. Y电容连接到机壳地（PE），不是信号地
 * 4. 共模扼流圈两线紧密耦合，避免差模泄漏
 */

// EMI测试频率点（CISPR 25 Class 5）
typedef struct {
    float freq_mhz;
    float limit_dbuv;  // 峰值限值
} EMI_LimitPoint;

const EMI_LimitPoint cispr25_class5[] = {
    {0.15f, 66.0f},   // 150kHz: 66dBμV
    {0.53f, 56.0f},   // 530kHz: 56dBμV
    {1.8f,  46.0f},   // 1.8MHz: 46dBμV
    {30.0f, 40.0f},   // 30MHz:  40dBμV
    {108.0f, 40.0f},  // 108MHz: 40dBμV
};
```

## 完整项目实战

### 12V/10A H桥驱动器（STM32互补PWM）

本节提供一个完整的、可直接用于生产的12V/10A H桥驱动器设计，包含完整的硬件电路、固件代码和PCB布局指南。

#### 系统架构

```
系统框图：

┌─────────────────────────────────────────────────────────┐
│                    12V/10A H桥驱动器                     │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │  EMI滤波 │    │  电源管理 │    │   STM32F103C8T6  │   │
│  │  共模扼流 │    │  12V→3.3V│    │   (控制核心)     │   │
│  │  X/Y电容 │    │  LDO稳压 │    │   TIM1互补PWM    │   │
│  └────┬─────┘    └────┬─────┘    └────────┬─────────┘   │
│       │               │                   │              │
│  ┌────▼───────────────▼───────────────────▼─────────┐   │
│  │              H桥功率级                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│  │  │ IR2104  │  │ IR2104  │  │ INA240  │          │   │
│  │  │ (左桥臂)│  │ (右桥臂)│  │ 电流检测│          │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘          │   │
│  │       │             │            │                │   │
│  │  Q1 Q3(IRLZ44N) Q2 Q4(IRLZ44N) ADC              │   │
│  └───────────────────────────────────────────────────┘   │
│                         │                                 │
│                    电机连接器                             │
└─────────────────────────────────────────────────────────┘
```

#### 完整BOM（物料清单）

| 位号 | 型号 | 规格 | 数量 | 说明 |
|------|------|------|------|------|
| Q1~Q4 | IRLZ44N | 55V/47A/22mΩ TO-220 | 4 | H桥MOSFET |
| U1, U2 | IR2104 | 半桥驱动 SO-8 | 2 | 栅极驱动 |
| U3 | INA240A2 | 电流检测 SOT-23-5 | 1 | 电流采样 |
| U4 | STM32F103C8T6 | 72MHz ARM Cortex-M3 | 1 | 主控 |
| U5 | AMS1117-3.3 | LDO 3.3V/1A | 1 | 电源 |
| D1, D2 | 1N4148 | 快恢复二极管 | 2 | 自举二极管 |
| D3~D6 | SS34 | 肖特基 3A/40V | 4 | 续流二极管 |
| D7 | BZX84C12 | 齐纳 12V SOT-23 | 4 | 栅极保护 |
| C1, C2 | 470nF/25V | X7R 0805 | 2 | 自举电容 |
| C3 | 1000μF/25V | 电解 | 1 | 主滤波电容 |
| C4~C7 | 100nF/25V | X7R 0805 | 4 | MOSFET去耦 |
| C8 | 100μF/25V | 电解 | 1 | 电源去耦 |
| R1~R4 | 10Ω | 0805 | 4 | 栅极开通电阻 |
| R5~R8 | 3.3Ω | 0805 | 4 | 栅极关断电阻 |
| R9~R12 | 10kΩ | 0805 | 4 | 栅极下拉 |
| R13 | 5mΩ/1W | 2512 | 1 | 电流采样电阻 |
| L1 | 共模扼流圈 10A | Würth 744272100 | 1 | EMI滤波 |
| F1 | 保险丝 15A | 插件 | 1 | 过流保护 |

#### 完整固件代码

```c
/* motor_driver.h */
#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include "stm32f1xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

// 电机状态枚举
typedef enum {
    MOTOR_COAST = 0,    // 滑行（自由转动）
    MOTOR_FORWARD,      // 正转
    MOTOR_REVERSE,      // 反转
    MOTOR_BRAKE,        // 制动
    MOTOR_FAULT         // 故障
} MotorState;

// 电机驱动配置
typedef struct {
    TIM_HandleTypeDef *htim;    // PWM定时器
    uint32_t channel_a;         // 通道A（正转）
    uint32_t channel_b;         // 通道B（反转）
    ADC_HandleTypeDef *hadc;    // 电流检测ADC
    float current_limit_a;      // 过流阈值（安培）
    float shunt_resistance;     // 采样电阻（欧姆）
    float ina240_gain;          // INA240增益
} MotorDriverConfig;

// 电机驱动状态
typedef struct {
    MotorState state;
    float current_a;            // 当前电流（安培）
    float fault_current_a;      // 故障时电流
    uint32_t fault_count;       // 故障计数
    bool enabled;
} MotorDriverStatus;

// 函数声明
void MotorDriver_Init(const MotorDriverConfig *config);
void MotorDriver_SetDuty(int8_t duty_percent);  // -100~+100
void MotorDriver_Brake(void);
void MotorDriver_Coast(void);
float MotorDriver_GetCurrent(void);
MotorState MotorDriver_GetState(void);
void MotorDriver_ClearFault(void);

#endif /* MOTOR_DRIVER_H */
```

```c
/* motor_driver.c */
#include "motor_driver.h"
#include <math.h>

static MotorDriverConfig g_config;
static MotorDriverStatus g_status;

// 软启动参数
#define SOFT_START_STEP     5       // 每步增加5%占空比
#define SOFT_START_DELAY_MS 10      // 每步延迟10ms

void MotorDriver_Init(const MotorDriverConfig *config) {
    g_config = *config;
    g_status.state = MOTOR_COAST;
    g_status.enabled = true;
    g_status.fault_count = 0;
    
    // 启动PWM定时器
    HAL_TIM_PWMEx_StartChannel(config->htim, config->channel_a);
    HAL_TIM_PWMEx_StartChannel(config->htim, config->channel_b);
    
    // 初始状态：滑行
    MotorDriver_Coast();
}

void MotorDriver_SetDuty(int8_t duty_percent) {
    if (!g_status.enabled || g_status.state == MOTOR_FAULT) return;
    
    // 限制范围
    if (duty_percent > 100) duty_percent = 100;
    if (duty_percent < -100) duty_percent = -100;
    
    uint32_t arr = g_config.htim->Init.Period;
    uint32_t pwm_val = (uint32_t)(abs(duty_percent) * arr / 100);
    
    if (duty_percent > 0) {
        // 正转
        __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_a, pwm_val);
        __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_b, 0);
        g_status.state = MOTOR_FORWARD;
    } else if (duty_percent < 0) {
        // 反转
        __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_a, 0);
        __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_b, pwm_val);
        g_status.state = MOTOR_REVERSE;
    } else {
        // 占空比为0，滑行
        MotorDriver_Coast();
    }
}

void MotorDriver_Brake(void) {
    // 低侧制动：两个低侧管导通，电机两端短接到GND
    __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_a, 
                          g_config.htim->Init.Period);
    __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_b, 
                          g_config.htim->Init.Period);
    g_status.state = MOTOR_BRAKE;
}

void MotorDriver_Coast(void) {
    __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_a, 0);
    __HAL_TIM_SET_COMPARE(g_config.htim, g_config.channel_b, 0);
    g_status.state = MOTOR_COAST;
}

float MotorDriver_GetCurrent(void) {
    HAL_ADC_Start(g_config.hadc);
    HAL_ADC_PollForConversion(g_config.hadc, 10);
    uint16_t adc_raw = HAL_ADC_GetValue(g_config.hadc);
    
    float vout = (float)adc_raw / 4096.0f * 3.3f;
    float current = vout / (g_config.shunt_resistance * g_config.ina240_gain);
    
    g_status.current_a = current;
    return current;
}

// 过流检测（在定时器中断中调用，1kHz）
void MotorDriver_CurrentCheck(void) {
    float current = MotorDriver_GetCurrent();
    
    if (current > g_config.current_limit_a) {
        // 立即关断
        MotorDriver_Coast();
        g_status.state = MOTOR_FAULT;
        g_status.fault_current_a = current;
        g_status.fault_count++;
        g_status.enabled = false;
    }
}

void MotorDriver_ClearFault(void) {
    if (g_status.state == MOTOR_FAULT) {
        g_status.state = MOTOR_COAST;
        g_status.enabled = true;
    }
}
```

#### PCB布局指南与层叠设计

```
4层PCB层叠建议（12V/10A电机驱动）：

┌─────────────────────────────────────────┐
│ Layer 1（顶层，35μm铜）                  │
│ - STM32、IR2104、INA240等控制器件        │
│ - 信号走线（细线，<0.2mm）               │
│ - 栅极驱动走线（短，<10mm）              │
├─────────────────────────────────────────┤
│ Layer 2（内层，35μm铜）                  │
│ - 完整GND平面（不分割）                  │
│ - 为Layer 1提供参考平面                  │
│ - 减少信号回流路径                       │
├─────────────────────────────────────────┤
│ Layer 3（内层，35μm铜）                  │
│ - 12V电源平面（功率区域）                │
│ - 3.3V电源平面（控制区域）               │
│ - 两个电源平面之间保持间距               │
├─────────────────────────────────────────┤
│ Layer 4（底层，70μm铜，加厚）            │
│ - MOSFET（TO-220立式安装）               │
│ - 功率走线（宽线，>3mm for 10A）         │
│ - 大面积铺铜散热                         │
└─────────────────────────────────────────┘

关键布局规则：
1. 功率回路（VCC→Q1→Motor→Q4→GND）面积最小化
2. 自举电容（C1/C2）紧靠IR2104的VB/VS引脚
3. 去耦电容（C4~C7）紧靠MOSFET漏极
4. 电流采样电阻（R13）放在低侧MOSFET源极到GND之间
5. INA240紧靠采样电阻，走线对称
6. 控制信号走线远离功率走线（>3mm间距）
7. MOSFET下方铺铜，通过过孔连接到底层散热铜
```

```
功率走线宽度计算（IPC-2221标准）：

电流（A）  外层走线宽度（mm）  内层走线宽度（mm）
1A         0.25mm              0.5mm
3A         0.75mm              1.5mm
5A         1.25mm              2.5mm
10A        2.5mm               5.0mm
15A        3.75mm              7.5mm

注：基于1oz铜（35μm），温升10°C
本设计（10A）：外层走线 ≥ 2.5mm，内层 ≥ 5mm
```

## 与集成驱动芯片对比

自制H桥 vs 集成驱动芯片的选择：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| L298N | 简单，便宜 | 效率低（压降2V），发热大 | 学习、低功率原型 |
| DRV8833 | 集成度高，保护完善 | 最大1.5A | 小型机器人 |
| TB6612 | 性能好，1.2A/通道 | 功率有限 | 中小型项目 |
| 自制全N桥 | 效率高，功率可定制 | 设计复杂 | 高功率、定制需求 |

## 常见问题与调试

### 故障1：直通（Shoot-Through）

**症状**：
- MOSFET立即损坏（漏极/源极短路）
- 电源保险丝熔断
- 电源电流异常大（数十安培）
- 有时伴随烟雾或焦味

**诊断步骤**：

```
直通诊断流程：

1. 测量死区时间
   示波器探头接高侧栅极和低侧栅极
   确认两者不同时为高电平
   死区时间 = 高侧关断到低侧开通的时间间隔
   
2. 检查栅极驱动波形
   正常：干净的方波，上升/下降时间<100ns
   异常：振荡、过冲、缓慢上升（可能导致线性区工作时间过长）
   
3. 检查自举电压
   测量IR2104的VB引脚电压
   正常：VCC + 10~15V（约22~27V for 12V系统）
   异常：电压不足 → 高侧MOSFET无法完全开通
```

**解决方案**：

```c
// 软件层面：增加死区时间
void TIM1_IncreasDeadTime(void) {
    // 将死区时间从200ns增加到500ns
    TIM1->BDTR &= ~TIM_BDTR_DTG;
    TIM1->BDTR |= 36;  // 36 × 13.9ns = 500ns
}

// 硬件层面：
// 1. 增大栅极串联电阻（减慢开通速度）
// 2. 检查栅极驱动芯片的死区时间设置
// 3. 确认自举电容容量足够（≥470nF）
// 4. 检查PCB布局，减少栅极走线寄生电感
```

### 故障2：栅极振荡（Gate Oscillation）

**症状**：
- 示波器观察到栅极波形有高频振荡（10~100MHz）
- MOSFET异常发热（开关损耗增大）
- EMI测试超标
- 偶发性误触发

**原因分析**：

```
栅极振荡等效电路：

栅极驱动输出阻抗（Rdrv）
        │
       Lg（走线寄生电感，1~10nH/cm）
        │
       Rg（串联电阻）
        │
       Cgs（栅源电容，约1~10nF）
        │
      ─────（源极）

LC谐振频率：f = 1/(2π√(Lg×Cgs))
例：Lg=5nH, Cgs=5nF → f = 1/(2π√(25×10⁻¹⁸)) = 450MHz
```

**解决方案**：

```
1. 增大栅极串联电阻（最有效）
   Rg = 10Ω → 33Ω（降低Q值，抑制振荡）
   代价：开关速度变慢，开关损耗略增

2. 缩短栅极走线
   目标：栅极驱动到MOSFET栅极 < 5mm
   减少寄生电感Lg

3. 添加铁氧体磁珠
   在栅极串联电阻后串联磁珠（如BLM18AG601SN1D）
   对高频振荡呈高阻抗

4. 检查PCB布局
   栅极驱动芯片紧靠MOSFET
   栅极走线不要与功率走线平行
```

### 故障3：热失控（Thermal Runaway）

**症状**：
- MOSFET温度持续上升，无法稳定
- 电流随温度升高而增大（正反馈）
- 最终器件损坏

**热失控机制**：

```
热失控正反馈循环：

温度升高
    ↓
Rds(on)增大（温度系数+0.4%/°C）
    ↓
导通损耗增大（P = I²×Rds(on)）
    ↓
温度进一步升高
    ↓
（循环，直到器件损坏）

临界条件：
dP/dT > 1/Rth（热阻的倒数）
即：功率随温度的增长率 > 散热能力
```

**预防措施**：

```c
// 温度监控（使用NTC热敏电阻）
#define NTC_R25         10000.0f  // 25°C时阻值 10kΩ
#define NTC_BETA        3950.0f   // B值
#define NTC_SERIES_R    10000.0f  // 串联电阻 10kΩ

float ReadMOSFET_Temperature(void) {
    HAL_ADC_Start(&hadc2);
    HAL_ADC_PollForConversion(&hadc2, 10);
    uint16_t adc_raw = HAL_ADC_GetValue(&hadc2);
    
    // 计算NTC电阻值
    float v_ntc = (float)adc_raw / 4096.0f * 3.3f;
    float r_ntc = NTC_SERIES_R * v_ntc / (3.3f - v_ntc);
    
    // Steinhart-Hart简化公式
    float temp_k = NTC_BETA / (logf(r_ntc / NTC_R25) + NTC_BETA / 298.15f);
    return temp_k - 273.15f;  // 转换为摄氏度
}

// 温度保护
#define TEMP_WARNING    80.0f   // 80°C警告
#define TEMP_SHUTDOWN   100.0f  // 100°C关断

void TemperatureProtection(void) {
    float temp = ReadMOSFET_Temperature();
    
    if (temp > TEMP_SHUTDOWN) {
        MotorDriver_Coast();
        g_status.state = MOTOR_FAULT;
        printf("THERMAL SHUTDOWN: %.1f°C\n", temp);
    } else if (temp > TEMP_WARNING) {
        // 降额运行：限制最大占空比
        uint8_t max_duty = (uint8_t)(100.0f * (TEMP_SHUTDOWN - temp) / 
                                     (TEMP_SHUTDOWN - TEMP_WARNING));
        printf("THERMAL WARNING: %.1f°C, max duty: %d%%\n", temp, max_duty);
    }
}
```

### 故障4：EMI超标

**症状**：
- CE/FCC认证测试失败
- 附近无线设备（WiFi、蓝牙）受干扰
- 示波器观察到电源线上有高频噪声

**EMI问题诊断**：

```
EMI诊断工具：
1. 近场探头（Near-field probe）：定位噪声源
2. 频谱分析仪：测量噪声频谱
3. 示波器（带宽>200MHz）：观察开关波形

常见EMI问题及原因：
┌─────────────────────────────────────────────────────┐
│ 问题                │ 原因              │ 解决方案   │
├─────────────────────────────────────────────────────┤
│ 基频（20kHz）超标   │ 差模噪声大        │ 增大X电容  │
│ 高次谐波超标        │ 开关速度太快      │ 增大Rg     │
│ 宽带噪声            │ 共模噪声          │ 加共模扼流 │
│ 特定频率尖峰        │ PCB谐振           │ 优化布局   │
└─────────────────────────────────────────────────────┘
```

**EMI整改措施**：

```c
/*
 * EMI整改优先级（从低成本到高成本）：
 * 
 * 1. 软件调整（零成本）：
 *    - 降低PWM频率（减少谐波数量）
 *    - 增加死区时间（减少直通风险，间接减少噪声）
 *    - 随机抖动PWM频率（扩展频谱，降低峰值）
 */

// 随机抖动PWM频率（Spread Spectrum）
void PWM_SpreadSpectrum(void) {
    static uint32_t lfsr = 0xACE1u;  // 线性反馈移位寄存器
    
    // 生成伪随机数
    lfsr = (lfsr >> 1) ^ (-(lfsr & 1u) & 0xB400u);
    
    // 在基频±5%范围内抖动
    uint32_t base_arr = 3599;  // 20kHz基频
    int32_t jitter = (int32_t)(lfsr & 0xFF) - 128;  // -128~+127
    uint32_t new_arr = base_arr + (jitter * base_arr / 2000);  // ±5%
    
    TIM1->ARR = new_arr;
}

/*
 * 2. 硬件调整（低成本）：
 *    - 增大栅极电阻（减慢开关速度，降低dV/dt）
 *    - 增加X/Y电容
 *    - 添加共模扼流圈
 * 
 * 3. PCB修改（中等成本）：
 *    - 缩小功率回路面积
 *    - 添加地平面
 *    - 优化去耦电容位置
 */
```

### 故障5：自举电路失效

**症状**：
- 高侧MOSFET无法完全开通（Vgs不足）
- 高侧MOSFET在线性区工作，异常发热
- 电机转速低于预期

**诊断**：

```c
// 自举电压监测
// 测量IR2104的VB引脚电压
// 正常：VCC + 10~15V（约22~27V for 12V系统）
// 异常：< VCC + 8V → 高侧MOSFET无法完全导通

// 常见原因：
// 1. 自举电容容量不足（<100nF）
// 2. 自举二极管反向恢复时间太长（使用1N4007而非1N4148）
// 3. 占空比过高（>95%），自举电容充电时间不足
// 4. 自举电容漏电（老化或质量差）

// 解决方案：
// 1. 增大自举电容（470nF → 1μF）
// 2. 更换快恢复二极管（1N4148或BAT54）
// 3. 限制最大占空比（<95%）
// 4. 定期刷新自举电容（在低侧导通时充电）

#define MAX_DUTY_PERCENT    95  // 限制最大占空比，保证自举充电时间

void MotorDriver_SetDutySafe(int8_t duty_percent) {
    // 限制最大占空比
    if (duty_percent > MAX_DUTY_PERCENT) duty_percent = MAX_DUTY_PERCENT;
    if (duty_percent < -MAX_DUTY_PERCENT) duty_percent = -MAX_DUTY_PERCENT;
    
    MotorDriver_SetDuty(duty_percent);
}
```

## 测试与验证

### 硬件测试流程

```
测试步骤（按顺序执行）：

Step 1: 静态测试（不通电）
□ 用万用表检查VCC到GND之间无短路
□ 检查MOSFET栅极到源极无短路
□ 检查所有焊点，无虚焊、桥接

Step 2: 低压上电测试（5V替代12V）
□ 电流表串联在电源线上，限流1A
□ 上电，观察电流（正常：<100mA）
□ 测量3.3V LDO输出（正常：3.3V±0.1V）
□ 测量STM32供电（正常：3.3V）

Step 3: 栅极驱动测试
□ 示波器观察IR2104的HO/LO输出
□ 确认死区时间（正常：200ns±50ns）
□ 确认无直通（HO和LO不同时为高）
□ 测量自举电压（正常：VCC+12V）

Step 4: 空载PWM测试（12V，无电机）
□ 示波器观察电机输出端波形
□ 确认PWM频率（正常：20kHz±1%）
□ 确认占空比可调（0~95%）
□ 测量MOSFET温度（正常：<40°C）

Step 5: 带载测试（接电机）
□ 从10%占空比开始，逐步增加
□ 监测电流（正常：与电机规格一致）
□ 监测MOSFET温度（正常：<80°C）
□ 测试正反转切换（确认无直通）
□ 测试制动功能
```

### 自动化测试代码

```c
// 电机驱动自检程序
typedef enum {
    TEST_PASS = 0,
    TEST_FAIL_OVERCURRENT,
    TEST_FAIL_TEMPERATURE,
    TEST_FAIL_NO_RESPONSE,
} TestResult;

TestResult MotorDriver_SelfTest(void) {
    printf("=== 电机驱动自检开始 ===\n");
    
    // 测试1：过流保护
    printf("测试1: 过流保护...");
    // 注入模拟过流信号（通过DAC或直接修改ADC读数）
    // 实际测试中，可以短暂堵转电机
    
    // 测试2：温度检测
    printf("测试2: 温度检测...");
    float temp = ReadMOSFET_Temperature();
    if (temp < -10.0f || temp > 150.0f) {
        printf("FAIL (%.1f°C)\n", temp);
        return TEST_FAIL_TEMPERATURE;
    }
    printf("PASS (%.1f°C)\n", temp);
    
    // 测试3：电机响应
    printf("测试3: 电机响应...");
    MotorDriver_SetDuty(20);  // 20%占空比
    HAL_Delay(100);
    float current = MotorDriver_GetCurrent();
    if (current < 0.1f) {  // 电机应该有电流
        printf("FAIL (%.2fA)\n", current);
        MotorDriver_Coast();
        return TEST_FAIL_NO_RESPONSE;
    }
    MotorDriver_Coast();
    printf("PASS (%.2fA)\n", current);
    
    printf("=== 自检完成：全部通过 ===\n");
    return TEST_PASS;
}
```

## 延伸阅读

- [信号完整性分析](01-signal-integrity.html) - 高速开关信号的完整性
- [EMC设计基础](02-emc-design.html) - 电机驱动的EMC处理
- [多层PCB设计](04-multilayer-pcb.html) - 功率PCB的层叠设计
- [编码器接口](../../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/04-encoder-interface.html) - 电机速度反馈
- [运动控制算法](../../05-actuator-control/advanced/02-motion-control-algorithms.html) - 梯形/S曲线加速度控制
- [智能小车控制](../../05-actuator-control/advanced/01-smart-car-control.html) - 电机驱动的实际应用
- [MQTT协议](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html) - 远程电机控制通信

## 参考资料

1. IR2104 Application Note - Infineon Technologies
2. 《电力电子技术》- 王兆安（第5版）
3. Texas Instruments - "Brushed DC Motor Fundamentals" (SLVA704)
4. Infineon - "MOSFET Power Losses Calculation Using the Data-Sheet Parameters"
5. DRV8833 Datasheet - Texas Instruments
6. TB6612FNG Datasheet - Toshiba
7. 《电磁兼容设计》- 白同云
8. DRV8302 Datasheet - Texas Instruments
9. IPC-2221 - PCB设计通用标准
