---
title: "CAN总线硬件设计"
description: "深入理解CAN（Controller Area Network）总线的硬件原理、差分信号传输、终端电阻配置、收发器选型、总线拓扑设计，掌握汽车和工业领域的可靠通信接口"
slug: "can-bus-hardware-design"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - CAN总线
  - 汽车电子
  - 工业通信
  - 差分信号
  - 终端电阻
  - 收发器
prerequisites:
  - "数字电路基础"
  - "UART/SPI/I2C基础"
related_contents:
  - "uart-usart-hardware-interface"
  - "spi-hardware-interface"
  - "i2c-hardware-interface"

# 学习信息
estimated_time: 50
difficulty_score: 4

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
  - CAN总线硬件
  - CAN协议
  - 差分信号传输
  - 终端电阻
  - CAN收发器
  - 汽车总线
cover_image: ""
---

# CAN总线硬件设计

## 概述

CAN（Controller Area Network，控制器局域网）是由德国Bosch公司开发的一种串行通信协议，专为汽车和工业控制系统设计。CAN总线以其高可靠性、实时性强、抗干扰能力出色的特点，成为汽车电子、工业自动化、医疗设备等领域的标准通信协议。

完成本文学习后，你将能够：

- 理解CAN总线的工作原理和硬件特性
- 掌握差分信号传输和终端电阻配置
- 学会CAN收发器的选型和应用
- 理解总线拓扑和布线要求
- 实现STM32的CAN通信
- 掌握CAN总线的调试和故障排查

## 背景知识

### CAN vs 其他总线

| 特性 | CAN | UART | SPI | I2C |
|------|-----|------|-----|-----|
| 通信方式 | 多主机 | 点对点 | 主从 | 多主机 |
| 数据线 | 2根（CAN_H/CAN_L） | 2根（TX/RX） | 4根 | 2根 |
| 速度 | 最高1Mbps | kbps级 | MHz级 | kHz-MHz |
| 传输距离 | 最远10km | 数米 | <1米 | <1米 |
| 抗干扰 | 极强 | 中等 | 弱 | 弱 |
| 实时性 | 优秀 | 一般 | 好 | 一般 |
| 错误检测 | 强大 | 简单 | 无 | 简单 |
| 应用领域 | 汽车、工业 | 通用 | 高速外设 | 传感器 |

### CAN总线的优势

**高可靠性**：
- 差分信号传输，抗干扰能力强
- 完善的错误检测机制（5种错误检测）
- 自动重传机制
- 错误节点自动隔离

**实时性强**：
- 非破坏性仲裁机制
- 优先级管理
- 确定性延迟

**灵活性高**：
- 多主机架构
- 支持广播和多播
- 节点可热插拔
- 最多支持110个节点

**成本低**：
- 只需2根线
- 简化布线
- 降低连接器成本


## CAN总线工作原理

### 信号线定义

CAN总线使用2根差分信号线进行通信：

**1. CAN_H（CAN High）- 高电平线**
- 显性位时为高电平（约3.5V）
- 隐性位时为中间电平（约2.5V）

**2. CAN_L（CAN Low）- 低电平线**
- 显性位时为低电平（约1.5V）
- 隐性位时为中间电平（约2.5V）

**差分电压**：
```
显性位（逻辑0）：
CAN_H = 3.5V, CAN_L = 1.5V
差分电压 = CAN_H - CAN_L = 2.0V

隐性位（逻辑1）：
CAN_H = 2.5V, CAN_L = 2.5V
差分电压 = CAN_H - CAN_L = 0V

判决阈值：
|CAN_H - CAN_L| > 0.9V → 显性位（0）
|CAN_H - CAN_L| < 0.5V → 隐性位（1）
```

### 基本连接方式

**标准CAN总线拓扑**：

```
节点1              节点2              节点3              节点4
                  
MCU                MCU                MCU                MCU
CAN_TX ──→ TXD    CAN_TX ──→ TXD    CAN_TX ──→ TXD    CAN_TX ──→ TXD
CAN_RX ←── RXD    CAN_RX ←── RXD    CAN_RX ←── RXD    CAN_RX ←── RXD
           │                 │                 │                 │
        收发器            收发器            收发器            收发器
           │                 │                 │                 │
        CAN_H ───────────────┼─────────────────┼─────────────────┤
        CAN_L ───────────────┼─────────────────┼─────────────────┤
           │                 │                 │                 │
         120Ω                                                   120Ω
           │                                                     │
          GND                                                   GND

终端电阻：总线两端各一个120Ω电阻
```

**关键要点**：
- 使用双绞线连接
- 总线两端必须有120Ω终端电阻
- 所有节点并联连接到主干线
- 支线长度应尽量短（<30cm）


### 差分信号原理

**为什么使用差分信号**：

```
单端信号（如UART）：
信号线 ────┬─── 接收端
           │
干扰 ──→ ──┴─── 干扰直接影响信号

差分信号（CAN）：
CAN_H ────┬─── 接收端
          │    （检测差值）
CAN_L ────┴───
          │
干扰 ──→ 同时影响两根线，差值不变

优势：
- 共模干扰被抵消
- 抗电磁干扰能力强
- 可以长距离传输
- 减少电磁辐射
```

**差分信号波形**：

```
显性位（0）和隐性位（1）：

CAN_H: ────┐       ┌────┐       ┌────
       3.5V│       │2.5V│       │
           └───────┘    └───────┘
           显性(0)      隐性(1)

CAN_L: ────┐       ┌────┐       ┌────
       1.5V│       │2.5V│       │
           └───────┘    └───────┘

差分:  ────┐       ┌────┐       ┌────
       2.0V│       │ 0V │       │
           └───────┘    └───────┘
            0        1    0
```

### 位时序和波特率

**CAN位时序结构**：

```
一个位时间分为4个时间段：

|<────────── 1 Bit Time ──────────>|
|                                   |
| SS | PTS | PBS1 | PBS2 |
|    |     |      |      |
同步段 传播段 相位段1 相位段2
     采样点↑

SS (Sync Segment): 同步段，1 TQ
PTS (Propagation Time Segment): 传播时间段，1-8 TQ
PBS1 (Phase Buffer Segment 1): 相位缓冲段1，1-8 TQ
PBS2 (Phase Buffer Segment 2): 相位缓冲段2，2-8 TQ

TQ (Time Quantum): 时间量子，最小时间单位
```

**波特率计算**：

```
波特率 = CAN时钟频率 / (预分频器 × 位时间)
位时间 = SS + PTS + PBS1 + PBS2 (单位：TQ)

示例（STM32，36MHz APB1时钟，500kbps）：
预分频器 = 4
位时间 = 1 + 6 + 7 + 4 = 18 TQ
波特率 = 36MHz / (4 × 18) = 500kbps
```

**标准波特率**：

| 波特率 | 最大距离 | 应用场景 |
|--------|---------|---------|
| 1 Mbps | 40m | 高速应用 |
| 500 kbps | 100m | 汽车CAN |
| 250 kbps | 250m | 工业控制 |
| 125 kbps | 500m | 长距离 |
| 50 kbps | 1km | 超长距离 |
| 20 kbps | 2.5km | 极长距离 |
| 10 kbps | 5km | 最大距离 |
| 5 kbps | 10km | 理论极限 |


### 显性位和隐性位

**线与逻辑**：

```
CAN总线使用"线与"逻辑：
- 显性位（0）优先于隐性位（1）
- 任何节点发送显性位，总线就是显性
- 只有所有节点都发送隐性位，总线才是隐性

节点1发送：  1    0    1    1    0
节点2发送：  1    1    1    0    1
总线实际：   1    0    1    0    0
                  ↑         ↑
               显性优先   显性优先
```

**仲裁机制**：

```
基于标识符的非破坏性仲裁：

节点1 (ID=0x123): 0 0 0 1 0 0 1 0 0 0 1 1
节点2 (ID=0x456): 0 1 0 0 0 1 0 1 0 1 1 0
总线实际：        0 0 0 0 0 0 0 0 0 0 1 0
                    ↑
                 节点2检测到冲突，停止发送
                 节点1继续发送（ID更小，优先级更高）

规则：
- ID越小，优先级越高
- 失败的节点自动重试
- 无数据丢失
```

## CAN收发器选型

### 常用CAN收发器

**1. TJA1050（最常用）**：

| 参数 | 值 |
|------|-----|
| 工作电压 | 4.75V - 5.25V |
| 最高速率 | 1 Mbps |
| 节点数 | 最多110个 |
| 工作温度 | -40°C ~ +125°C |
| 特点 | 成本低，应用广泛 |

**2. TJA1051（改进版）**：

| 参数 | 值 |
|------|-----|
| 工作电压 | 4.75V - 5.25V |
| 最高速率 | 1 Mbps |
| 节点数 | 最多110个 |
| 工作温度 | -40°C ~ +125°C |
| 特点 | 更好的EMC性能 |

**3. SN65HVD230（3.3V）**：

| 参数 | 值 |
|------|-----|
| 工作电压 | 3.0V - 3.6V |
| 最高速率 | 1 Mbps |
| 节点数 | 最多120个 |
| 工作温度 | -40°C ~ +125°C |
| 特点 | 3.3V供电，低功耗 |

**4. MCP2551（Microchip）**：

| 参数 | 值 |
|------|-----|
| 工作电压 | 4.5V - 5.5V |
| 最高速率 | 1 Mbps |
| 节点数 | 最多112个 |
| 工作温度 | -40°C ~ +125°C |
| 特点 | 兼容TJA1050 |

### 收发器引脚定义

**TJA1050引脚图**：

```
        TJA1050
     ┌──────────┐
TXD ─┤1       8├─ VCC (5V)
GND ─┤2       7├─ CANH
VCC ─┤3       6├─ CANL
RXD ─┤4       5├─ VREF (2.5V)
     └──────────┘

引脚功能：
1. TXD: 发送数据输入（来自MCU）
2. GND: 地
3. VCC: 电源（5V）
4. RXD: 接收数据输出（到MCU）
5. VREF: 参考电压输出（2.5V）
6. CANL: CAN低电平线
7. CANH: CAN高电平线
8. VCC: 电源（5V）
```

**SN65HVD230引脚图**：

```
      SN65HVD230
     ┌──────────┐
  D ─┤1       8├─ VCC (3.3V)
GND ─┤2       7├─ CANH
VCC ─┤3       6├─ CANL
  R ─┤4       5├─ VREF (1.65V)
     └──────────┘

引脚功能：
1. D: 发送数据输入
2. GND: 地
3. VCC: 电源（3.3V）
4. R: 接收数据输出
5. VREF: 参考电压输出
6. CANL: CAN低电平线
7. CANH: CAN高电平线
8. VCC: 电源（3.3V）
```


## 终端电阻配置

### 为什么需要终端电阻

**信号反射问题**：

```
没有终端电阻：
发送端 ──────────────────→ 开路端
        信号反射 ←──────────

结果：
- 信号振铃
- 波形失真
- 通信错误

有终端电阻：
发送端 ──────────────────→ 120Ω ─ GND
        信号被吸收

结果：
- 波形清晰
- 无反射
- 通信可靠
```

### 终端电阻值计算

**理论计算**：

```
CAN总线特性阻抗 ≈ 120Ω

终端电阻 = 特性阻抗 = 120Ω

两个120Ω并联：
总阻抗 = 120Ω || 120Ω = 60Ω

总线空闲时电流：
I = 5V / 60Ω ≈ 83mA
```

**标准配置**：

```
总线两端各一个120Ω电阻：

节点1                                    节点N
  │                                        │
120Ω ─┬─ CAN_H ─────────────────────┬─ 120Ω
      │                              │
120Ω ─┴─ CAN_L ─────────────────────┴─ 120Ω
  │                                    │
 GND                                  GND

注意：
- 只在总线两端放置
- 中间节点不需要终端电阻
- 使用1/4W或更高功率的电阻
```

### 终端电阻类型

**1. 标准终端（最常用）**：

```
CAN_H ─┬─ 120Ω ─┬─ GND
       │        │
CAN_L ─┴────────┘

优点：简单、可靠
缺点：功耗较高（83mA）
```

**2. 分压终端（低功耗）**：

```
VCC (5V)
  │
  ├─ 60Ω ─┬─ CAN_H
  │       │
  ├─ 60Ω ─┴─ CAN_L
  │       │
  └─ 60Ω ─┴─ GND

优点：降低功耗
缺点：需要3个电阻
```

**3. 可切换终端**：

```
CAN_H ─┬─ 开关 ─┬─ 120Ω ─┬─ GND
       │        │        │
CAN_L ─┴────────┴────────┘

优点：灵活配置
缺点：增加复杂度
应用：可移动节点
```

### 终端电阻测试

**测量方法**：

```c
// 1. 断电测量
// 用万用表测量CAN_H和CAN_L之间的电阻
// 应该约为60Ω（两个120Ω并联）

// 2. 上电测量
// 测量CAN_H和CAN_L的电压
// 空闲时应该都约为2.5V

// 3. 示波器观察
// 观察CAN信号波形
// 应该无振铃、无过冲
```

**常见问题**：

| 现象 | 可能原因 | 解决方法 |
|------|---------|---------|
| 通信不稳定 | 缺少终端电阻 | 添加120Ω电阻 |
| 波形振铃 | 终端电阻值不对 | 使用标准120Ω |
| 功耗过高 | 终端电阻过小 | 检查电阻值 |
| 信号幅度小 | 终端电阻过大 | 使用120Ω |


## 总线拓扑设计

### 标准线性拓扑（推荐）

```
主干线（双绞线）
═══════════════════════════════════════════════
120Ω                                        120Ω
  │                                           │
节点1    节点2    节点3    节点4    节点5    节点6
  │       │        │        │        │        │
支线     支线     支线     支线     支线     支线
(<30cm) (<30cm) (<30cm) (<30cm) (<30cm) (<30cm)

优点：
- 信号质量好
- 易于布线
- 易于维护

要求：
- 主干线使用双绞线
- 支线尽量短（<30cm）
- 两端有终端电阻
```

### 错误拓扑（避免）

**星型拓扑（不推荐）**：

```
        节点1
          │
    节点2─┼─节点3
          │
        节点4

问题：
- 信号反射严重
- 通信不可靠
- 不符合CAN标准
```

**环形拓扑（不推荐）**：

```
节点1 ─ 节点2
  │       │
节点4 ─ 节点3

问题：
- 无法正确终端
- 信号环路
- 不符合标准
```

### 布线要求

**1. 使用双绞线**：

```
推荐规格：
- 特性阻抗：120Ω ± 5%
- 线径：0.5mm² - 0.75mm²
- 绞距：约20mm
- 屏蔽：可选（高干扰环境推荐）

常用型号：
- CANBUS线缆
- CAT5网线（应急）
```

**2. 长度限制**：

```
波特率与最大长度的关系：

1 Mbps  → 40m
500 kbps → 100m
250 kbps → 250m
125 kbps → 500m
50 kbps  → 1km
20 kbps  → 2.5km
10 kbps  → 5km
5 kbps   → 10km

公式（近似）：
最大长度(m) ≈ 50,000 / 波特率(kbps)
```

**3. 支线长度**：

```
支线（Stub）长度限制：

波特率      最大支线长度
1 Mbps      30cm
500 kbps    30cm
250 kbps    60cm
125 kbps    120cm
50 kbps     300cm

建议：
- 尽量短
- 所有支线长度总和 < 主干线长度
```

**4. 节点数量**：

```
理论最大：110个节点
实际推荐：<32个节点

限制因素：
- 总线负载
- 收发器驱动能力
- 信号延迟
```

### PCB布线建议

**1. 差分对布线**：

```
CAN_H和CAN_L应该：
- 平行走线
- 等长（误差<5mm）
- 间距一致（5-10mil）
- 避免分叉
```

**2. 地平面**：

```
信号线下方保留完整地平面：
- 提供回流路径
- 减少EMI
- 改善信号完整性
```

**3. 去耦电容**：

```
收发器电源引脚附近：
VCC ─┬─ 0.1μF ─┬─ GND
     └─ 10μF ──┘

位置：
- 尽量靠近芯片
- 0.1μF高频去耦
- 10μF低频去耦
```

**4. ESD保护**：

```
外部接口处添加TVS二极管：

CAN_H ──┬─────────→ 接口
        │
        ├─ TVS ─┬─ GND
        │       │
CAN_L ──┴───────┘

推荐型号：
- PESD2CAN（双通道）
- TPD2ECAN（双通道）
```


## 硬件电路设计

### 基本CAN节点电路

**STM32 + TJA1050电路**：

```
STM32F103                TJA1050              CAN总线
                                              
PA11 (CAN_RX) ──→ RXD ─┤4                    
PA12 (CAN_TX) ──→ TXD ─┤1                    
                        │                     
5V ──┬─ 0.1μF ─┬─ VCC ─┤3,8                  
     └─ 10μF ──┘        │                     
                        │                     
GND ────────────── GND ─┤2                    
                        │                     
                     CANH┤7 ──┬─────────→ CAN_H
                        │    │
                     CANL┤6 ──┴─────────→ CAN_L
                        │
                    VREF┤5 (悬空或接0.1μF到GND)
                        
终端电阻（总线两端）：
CAN_H ─┬─ 120Ω ─┬─ GND
       │        │
CAN_L ─┴────────┘
```

**3.3V系统 + SN65HVD230电路**：

```
STM32F103              SN65HVD230            CAN总线
                                              
PA11 (CAN_RX) ──→ R ───┤4                    
PA12 (CAN_TX) ──→ D ───┤1                    
                        │                     
3.3V ─┬─ 0.1μF ─┬─ VCC ┤3,8                  
      └─ 10μF ──┘       │                     
                        │                     
GND ───────────── GND ──┤2                    
                        │                     
                    CANH┤7 ──┬─────────→ CAN_H
                        │    │
                    CANL┤6 ──┴─────────→ CAN_L
                        │
                   VREF ┤5 (悬空或接0.1μF到GND)
```

### 隔离CAN电路（高可靠性）

**光耦隔离方案**：

```
MCU侧（3.3V）          隔离侧（5V）          CAN总线
                                              
CAN_TX ──→ 光耦 ──→ TXD ─┤TJA1050            
CAN_RX ←── 光耦 ←── RXD ─┤                   
                          │                   
3.3V                   5V ┤VCC                
                          │                   
GND1                  GND2┤GND ──→ CAN_H/CAN_L
                          
隔离电源：
- DC-DC隔离模块
- 或独立5V电源

优点：
- 保护MCU
- 隔离地环路
- 提高可靠性

应用：
- 工业控制
- 医疗设备
- 高压环境
```

### 共模扼流圈（CMC）

**EMC改善电路**：

```
收发器                CMC                  接口
                                           
CANH ──→ ┌───┐ ──→ TVS ──→ 接口
         │CMC│
CANL ──→ └───┘ ──→ TVS ──→ 接口

共模扼流圈参数：
- 阻抗：>100Ω @ 100MHz
- 差模阻抗：<5Ω
- 额定电流：>100mA

作用：
- 抑制共模干扰
- 改善EMC性能
- 保护总线
```

### 完整节点电路示例

```
┌─────────────────────────────────────────────┐
│                 CAN节点                      │
│                                              │
│  STM32F103                                   │
│  ┌────────┐                                  │
│  │        │ PA11 ──→ RXD                     │
│  │  MCU   │ PA12 ──→ TXD                     │
│  │        │              ┌──────────┐        │
│  └────────┘              │ TJA1050  │        │
│                          │          │        │
│  5V ─┬─ 0.1μF ─┬─ VCC ──┤VCC       │        │
│      └─ 10μF ──┘         │          │        │
│                          │      CANH├──┬─→ 接口
│  GND ──────────── GND ───┤GND       │  │     │
│                          │      CANL├──┴─→ 接口
│                          └──────────┘  │     │
│                                        │     │
│  终端电阻（可选）：                     │     │
│  ┌─ 跳线 ─┬─ 120Ω ─┬─ GND             │     │
│  │        │        │                   │     │
│  └────────┴────────┘                   │     │
│                                        │     │
│  ESD保护：                              │     │
│  CAN_H ──┬─ TVS ─┬─ GND               │     │
│          │       │                     │     │
│  CAN_L ──┴───────┘                     │     │
│                                        │     │
└────────────────────────────────────────┼─────┘
                                         │
                                    CAN总线
```


## STM32 CAN配置实例

### 硬件初始化

**GPIO和CAN外设配置**：

```c
// 1. 使能时钟
RCC->APB1ENR |= RCC_APB1ENR_CAN1EN;   // CAN1时钟
RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;   // GPIOA时钟

// 2. 配置GPIO（复用推挽输出）
// PA11 (CAN_RX) - 浮空输入
GPIOA->CRH &= ~(0xF << 12);
GPIOA->CRH |= (0x4 << 12);

// PA12 (CAN_TX) - 复用推挽输出，50MHz
GPIOA->CRH &= ~(0xF << 16);
GPIOA->CRH |= (0xB << 16);

// 3. 进入初始化模式
CAN1->MCR |= CAN_MCR_INRQ;
while (!(CAN1->MSR & CAN_MSR_INAK));  // 等待进入初始化模式

// 4. 退出睡眠模式
CAN1->MCR &= ~CAN_MCR_SLEEP;
while (CAN1->MSR & CAN_MSR_SLAK);

// 5. 配置位时序（500kbps，36MHz APB1时钟）
// 预分频器 = 4, BS1 = 6, BS2 = 7, SJW = 1
// 位时间 = (1 + 6 + 7) × 4 / 36MHz = 1.556μs ≈ 500kbps
CAN1->BTR = (3 << 0) |   // BRP: 预分频器-1 = 3 (分频4)
            (6 << 16) |  // TS1: 时间段1 = 6
            (7 << 20) |  // TS2: 时间段2 = 7
            (0 << 24);   // SJW: 重同步跳跃宽度 = 1

// 6. 配置工作模式
CAN1->MCR &= ~CAN_MCR_TTCM;  // 禁用时间触发模式
CAN1->MCR &= ~CAN_MCR_ABOM;  // 禁用自动离线管理
CAN1->MCR &= ~CAN_MCR_AWUM;  // 禁用自动唤醒
CAN1->MCR &= ~CAN_MCR_NART;  // 使能自动重传
CAN1->MCR &= ~CAN_MCR_RFLM;  // 接收FIFO锁定模式
CAN1->MCR &= ~CAN_MCR_TXFP;  // 发送FIFO优先级

// 7. 配置过滤器（接收所有消息）
CAN1->FMR |= CAN_FMR_FINIT;  // 进入过滤器初始化模式

// 过滤器0：接收所有标准帧
CAN1->FA1R |= (1 << 0);      // 激活过滤器0
CAN1->FM1R &= ~(1 << 0);     // 标识符屏蔽模式
CAN1->FS1R |= (1 << 0);      // 32位模式
CAN1->FFA1R &= ~(1 << 0);    // 分配到FIFO0

CAN1->sFilterRegister[0].FR1 = 0x00000000;  // 标识符
CAN1->sFilterRegister[0].FR2 = 0x00000000;  // 屏蔽码（接收所有）

CAN1->FMR &= ~CAN_FMR_FINIT;  // 退出过滤器初始化模式

// 8. 退出初始化模式
CAN1->MCR &= ~CAN_MCR_INRQ;
while (CAN1->MSR & CAN_MSR_INAK);  // 等待退出初始化模式
```

### 发送数据

```c
// CAN发送函数
bool CAN_Transmit(uint32_t id, uint8_t *data, uint8_t len) {
    // 检查发送邮箱是否空闲
    if (!(CAN1->TSR & CAN_TSR_TME0)) {
        return false;  // 邮箱0忙
    }
    
    // 配置标识符（标准帧）
    CAN1->sTxMailBox[0].TIR = (id << 21);  // 标准ID
    
    // 配置数据长度
    CAN1->sTxMailBox[0].TDTR = len;
    
    // 填充数据
    CAN1->sTxMailBox[0].TDLR = (data[3] << 24) | (data[2] << 16) |
                                (data[1] << 8)  | data[0];
    CAN1->sTxMailBox[0].TDHR = (data[7] << 24) | (data[6] << 16) |
                                (data[5] << 8)  | data[4];
    
    // 请求发送
    CAN1->sTxMailBox[0].TIR |= CAN_TI0R_TXRQ;
    
    // 等待发送完成（可选）
    uint32_t timeout = 1000;
    while (!(CAN1->TSR & CAN_TSR_RQCP0) && timeout--);
    
    if (timeout == 0) {
        return false;  // 超时
    }
    
    // 清除请求完成标志
    CAN1->TSR |= CAN_TSR_RQCP0;
    
    return true;
}

// 使用示例
void CAN_SendExample(void) {
    uint8_t data[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    
    if (CAN_Transmit(0x123, data, 8)) {
        printf("CAN message sent\n");
    } else {
        printf("CAN send failed\n");
    }
}
```

### 接收数据

```c
// CAN接收函数
bool CAN_Receive(uint32_t *id, uint8_t *data, uint8_t *len) {
    // 检查FIFO0是否有消息
    if (!(CAN1->RF0R & CAN_RF0R_FMP0)) {
        return false;  // FIFO0空
    }
    
    // 读取标识符
    *id = (CAN1->sFIFOMailBox[0].RIR >> 21) & 0x7FF;
    
    // 读取数据长度
    *len = CAN1->sFIFOMailBox[0].RDTR & 0x0F;
    
    // 读取数据
    uint32_t low = CAN1->sFIFOMailBox[0].RDLR;
    uint32_t high = CAN1->sFIFOMailBox[0].RDHR;
    
    data[0] = (low >> 0) & 0xFF;
    data[1] = (low >> 8) & 0xFF;
    data[2] = (low >> 16) & 0xFF;
    data[3] = (low >> 24) & 0xFF;
    data[4] = (high >> 0) & 0xFF;
    data[5] = (high >> 8) & 0xFF;
    data[6] = (high >> 16) & 0xFF;
    data[7] = (high >> 24) & 0xFF;
    
    // 释放FIFO
    CAN1->RF0R |= CAN_RF0R_RFOM0;
    
    return true;
}

// 使用示例（轮询方式）
void CAN_ReceiveExample(void) {
    uint32_t id;
    uint8_t data[8];
    uint8_t len;
    
    if (CAN_Receive(&id, data, &len)) {
        printf("Received CAN message:\n");
        printf("ID: 0x%03X\n", id);
        printf("Length: %d\n", len);
        printf("Data: ");
        for (int i = 0; i < len; i++) {
            printf("%02X ", data[i]);
        }
        printf("\n");
    }
}

// 中断方式接收
void CAN1_RX0_IRQHandler(void) {
    uint32_t id;
    uint8_t data[8];
    uint8_t len;
    
    if (CAN_Receive(&id, data, &len)) {
        // 处理接收到的数据
        ProcessCANMessage(id, data, len);
    }
}
```


### 过滤器配置

```c
// 配置过滤器接收特定ID
void CAN_FilterConfig(uint32_t id, uint32_t mask) {
    CAN1->FMR |= CAN_FMR_FINIT;  // 进入过滤器初始化模式
    
    // 过滤器0：标识符列表模式
    CAN1->FA1R |= (1 << 0);      // 激活过滤器0
    CAN1->FM1R |= (1 << 0);      // 标识符列表模式
    CAN1->FS1R |= (1 << 0);      // 32位模式
    CAN1->FFA1R &= ~(1 << 0);    // 分配到FIFO0
    
    // 设置标识符（标准帧）
    CAN1->sFilterRegister[0].FR1 = (id << 21);
    CAN1->sFilterRegister[0].FR2 = (mask << 21);
    
    CAN1->FMR &= ~CAN_FMR_FINIT;  // 退出过滤器初始化模式
}

// 配置多个ID过滤
void CAN_FilterMultipleIDs(void) {
    CAN1->FMR |= CAN_FMR_FINIT;
    
    // 过滤器0：接收ID 0x100-0x10F
    CAN1->FA1R |= (1 << 0);
    CAN1->FM1R &= ~(1 << 0);     // 屏蔽模式
    CAN1->FS1R |= (1 << 0);      // 32位
    CAN1->FFA1R &= ~(1 << 0);    // FIFO0
    
    CAN1->sFilterRegister[0].FR1 = (0x100 << 21);  // ID
    CAN1->sFilterRegister[0].FR2 = (0x7F0 << 21);  // Mask (低4位不关心)
    
    // 过滤器1：接收ID 0x200
    CAN1->FA1R |= (1 << 1);
    CAN1->FM1R |= (1 << 1);      // 列表模式
    CAN1->FS1R |= (1 << 1);      // 32位
    CAN1->FFA1R |= (1 << 1);     // FIFO1
    
    CAN1->sFilterRegister[1].FR1 = (0x200 << 21);
    CAN1->sFilterRegister[1].FR2 = (0x300 << 21);
    
    CAN1->FMR &= ~CAN_FMR_FINIT;
}
```

## 常见问题与调试

### 问题1：无法通信

**可能原因**：

1. **缺少终端电阻**
   - 检查：用万用表测量CAN_H和CAN_L之间电阻
   - 应该约为60Ω
   - 解决：在总线两端添加120Ω电阻

2. **波特率不匹配**
   - 检查：所有节点波特率必须一致
   - 解决：统一配置为相同波特率

3. **接线错误**
   - 检查：CAN_H连CAN_H，CAN_L连CAN_L
   - 解决：检查并纠正接线

4. **收发器故障**
   - 检查：测量收发器电源和信号
   - 解决：更换收发器

**调试步骤**：

```c
// 1. 检查CAN控制器状态
void Debug_CheckCANStatus(void) {
    if (CAN1->MSR & CAN_MSR_INAK) {
        printf("CAN in initialization mode\n");
    }
    if (CAN1->ESR & CAN_ESR_BOFF) {
        printf("CAN bus-off\n");
    }
    if (CAN1->ESR & CAN_ESR_EPVF) {
        printf("CAN error passive\n");
    }
    if (CAN1->ESR & CAN_ESR_EWGF) {
        printf("CAN error warning\n");
    }
}

// 2. 测量总线电压
void Debug_MeasureBusVoltage(void) {
    printf("Measure CAN_H and CAN_L voltage:\n");
    printf("Idle: Both should be ~2.5V\n");
    printf("Dominant: CAN_H ~3.5V, CAN_L ~1.5V\n");
}

// 3. 回环测试
void Debug_LoopbackTest(void) {
    // 配置为回环模式
    CAN1->BTR |= CAN_BTR_LBKM;
    
    // 发送测试消息
    uint8_t data[8] = {0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA};
    CAN_Transmit(0x123, data, 8);
    
    // 尝试接收
    uint32_t id;
    uint8_t rx_data[8];
    uint8_t len;
    
    if (CAN_Receive(&id, rx_data, &len)) {
        printf("Loopback test OK\n");
    } else {
        printf("Loopback test FAILED\n");
    }
    
    // 退出回环模式
    CAN1->BTR &= ~CAN_BTR_LBKM;
}
```

### 问题2：数据错误

**可能原因**：

1. **EMI干扰**
   - 检查：走线是否靠近干扰源
   - 解决：重新布线，添加共模扼流圈

2. **总线过长**
   - 检查：总线长度是否超过限制
   - 解决：降低波特率或缩短总线

3. **节点过多**
   - 检查：节点数量是否过多
   - 解决：减少节点或使用中继器

**错误计数器监控**：

```c
void Monitor_ErrorCounters(void) {
    uint8_t tec = (CAN1->ESR >> 16) & 0xFF;  // 发送错误计数
    uint8_t rec = (CAN1->ESR >> 24) & 0xFF;  // 接收错误计数
    
    printf("TEC: %d, REC: %d\n", tec, rec);
    
    if (tec > 127 || rec > 127) {
        printf("Warning: Error passive state\n");
    }
    if (tec > 255) {
        printf("Error: Bus-off state\n");
    }
}
```

### 问题3：总线关闭（Bus-Off）

**原因**：
- 发送错误计数器 > 255
- 通常由于硬件故障或配置错误

**恢复方法**：

```c
void CAN_BusOffRecovery(void) {
    // 检查是否处于Bus-Off状态
    if (CAN1->ESR & CAN_ESR_BOFF) {
        printf("Bus-Off detected, attempting recovery...\n");
        
        // 方法1：软件复位
        CAN1->MCR |= CAN_MCR_RESET;
        HAL_Delay(10);
        
        // 重新初始化
        CAN_Init();
        
        // 方法2：自动离线管理（ABOM）
        // CAN1->MCR |= CAN_MCR_ABOM;
        // 硬件会自动尝试恢复
    }
}
```


### 问题4：波形质量差

**可能原因**：

1. **终端电阻不正确**
   - 检查：测量总线阻抗
   - 解决：使用标准120Ω电阻

2. **走线过长或不规范**
   - 检查：支线长度、双绞线使用
   - 解决：优化布线

3. **地环路**
   - 检查：多点接地
   - 解决：单点接地或使用隔离

**示波器测试**：

```
理想波形：
CAN_H: ────┐       ┌────
       3.5V│       │2.5V
           └───────┘
           
CAN_L: ────┐       ┌────
       1.5V│       │2.5V
           └───────┘

检查项：
- 上升/下降时间 < 50ns
- 无振铃
- 无过冲
- 差分电压 ≈ 2V（显性位）
```

## 实用技巧

### 1. CAN总线监控

```c
// 静默模式（只监听，不发送）
void CAN_SilentMode(void) {
    CAN1->BTR |= CAN_BTR_SILM;
    
    // 现在可以接收但不能发送
    // 用于总线监控和分析
}

// 监控所有消息
void CAN_MonitorAll(void) {
    // 配置过滤器接收所有消息
    CAN1->FMR |= CAN_FMR_FINIT;
    
    CAN1->FA1R |= (1 << 0);
    CAN1->FM1R &= ~(1 << 0);     // 屏蔽模式
    CAN1->FS1R |= (1 << 0);
    CAN1->FFA1R &= ~(1 << 0);
    
    CAN1->sFilterRegister[0].FR1 = 0x00000000;
    CAN1->sFilterRegister[0].FR2 = 0x00000000;  // 接收所有
    
    CAN1->FMR &= ~CAN_FMR_FINIT;
    
    // 进入静默模式
    CAN_SilentMode();
}
```

### 2. 时间戳功能

```c
// 使能时间触发通信模式
void CAN_EnableTimestamp(void) {
    CAN1->MCR |= CAN_MCR_TTCM;
    
    // 读取消息时间戳
    uint16_t timestamp = CAN1->sFIFOMailBox[0].RDTR >> 16;
    printf("Message timestamp: %d\n", timestamp);
}
```

### 3. 自动重传控制

```c
// 禁用自动重传（单次发送）
void CAN_DisableAutoRetransmit(void) {
    CAN1->MCR |= CAN_MCR_NART;
    
    // 发送失败后不会自动重传
    // 适用于实时性要求高的场景
}

// 使能自动重传（默认）
void CAN_EnableAutoRetransmit(void) {
    CAN1->MCR &= ~CAN_MCR_NART;
}
```

### 4. 优先级管理

```c
// 配置发送优先级
void CAN_SetTxPriority(uint8_t mailbox, uint8_t priority) {
    // 优先级：0-3，数字越小优先级越高
    CAN1->sTxMailBox[mailbox].TDTR &= ~(0x3 << 0);
    CAN1->sTxMailBox[mailbox].TDTR |= (priority << 0);
}

// 使用标识符优先级
void CAN_UseIDPriority(void) {
    CAN1->MCR |= CAN_MCR_TXFP;
    
    // 现在按标识符优先级发送
    // ID越小，优先级越高
}
```

## 性能优化

### 提高吞吐量

**1. 使用DMA**：

```c
// 配置DMA接收
void CAN_DMA_Config(void) {
    // 使能DMA时钟
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;
    
    // 配置DMA通道
    // （具体配置取决于MCU型号）
    
    // 使能CAN的DMA请求
    // 注意：并非所有MCU的CAN都支持DMA
}
```

**2. 批量发送**：

```c
// 使用多个发送邮箱
void CAN_BatchTransmit(void) {
    uint8_t data1[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    uint8_t data2[8] = {0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18};
    uint8_t data3[8] = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28};
    
    // 同时填充3个邮箱
    CAN_TransmitMailbox(0, 0x100, data1, 8);
    CAN_TransmitMailbox(1, 0x101, data2, 8);
    CAN_TransmitMailbox(2, 0x102, data3, 8);
    
    // 硬件会自动按优先级发送
}
```

### 降低延迟

**1. 使用中断**：

```c
// 配置接收中断
void CAN_EnableRxInterrupt(void) {
    // 使能FIFO0消息挂起中断
    CAN1->IER |= CAN_IER_FMPIE0;
    
    // 配置NVIC
    NVIC_EnableIRQ(CAN1_RX0_IRQn);
    NVIC_SetPriority(CAN1_RX0_IRQn, 0);  // 最高优先级
}

// 中断处理函数
void CAN1_RX0_IRQHandler(void) {
    // 立即处理接收到的消息
    // 延迟最小
}
```

**2. 提高波特率**：

```c
// 配置为1Mbps（最高速度）
void CAN_SetHighSpeed(void) {
    // 预分频器 = 2, BS1 = 6, BS2 = 7
    // 位时间 = (1 + 6 + 7) × 2 / 36MHz = 0.778μs ≈ 1Mbps
    CAN1->BTR = (1 << 0) |   // BRP = 1 (分频2)
                (6 << 16) |  // TS1 = 6
                (7 << 20) |  // TS2 = 7
                (0 << 24);   // SJW = 1
}
```

### 提高可靠性

**1. 错误处理**：

```c
// 完善的错误处理
bool CAN_TransmitReliable(uint32_t id, uint8_t *data, uint8_t len) {
    int retry = 3;
    
    while (retry > 0) {
        if (CAN_Transmit(id, data, len)) {
            return true;
        }
        
        // 检查错误状态
        if (CAN1->ESR & CAN_ESR_BOFF) {
            CAN_BusOffRecovery();
        }
        
        retry--;
        HAL_Delay(10);
    }
    
    return false;
}
```

**2. 看门狗监控**：

```c
// CAN总线看门狗
void CAN_Watchdog(void) {
    static uint32_t last_rx_time = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 如果超过1秒没有收到消息
    if (current_time - last_rx_time > 1000) {
        printf("CAN bus timeout!\n");
        
        // 尝试恢复
        CAN_BusOffRecovery();
        
        last_rx_time = current_time;
    }
}
```


## 总结

通过本文学习，你已经掌握了：

- ✅ **CAN基础**：差分信号、显性位/隐性位、仲裁机制
- ✅ **硬件设计**：收发器选型、终端电阻配置、总线拓扑
- ✅ **电路设计**：基本电路、隔离电路、ESD保护
- ✅ **STM32配置**：初始化、发送接收、过滤器配置
- ✅ **故障排查**：常见问题诊断和解决方法
- ✅ **性能优化**：提高吞吐量、降低延迟、提高可靠性

### 关键要点

1. **CAN总线特点**：
   - 差分信号传输，抗干扰能力强
   - 多主机架构，非破坏性仲裁
   - 完善的错误检测和处理机制

2. **硬件要求**：
   - 使用双绞线
   - 总线两端必须有120Ω终端电阻
   - 支线长度尽量短（<30cm）

3. **波特率与距离**：
   - 1 Mbps → 40m
   - 500 kbps → 100m
   - 125 kbps → 500m
   - 10 kbps → 5km

4. **可靠性保证**：
   - 添加ESD保护
   - 使用隔离（高可靠性应用）
   - 实现错误处理和恢复机制

## 实践建议

### 初学者练习

1. **基础通信**：
   - 搭建两节点CAN网络
   - 实现简单的数据收发
   - 测试不同波特率

2. **过滤器配置**：
   - 配置接收特定ID
   - 实现多ID过滤
   - 测试过滤效果

3. **错误处理**：
   - 模拟总线错误
   - 实现错误检测
   - 测试恢复机制

### 进阶项目

1. **CAN网关**：
   - 实现多CAN总线互联
   - 协议转换
   - 数据路由

2. **CAN分析仪**：
   - 监控总线流量
   - 解析CAN消息
   - 统计分析

3. **CANopen协议**：
   - 实现CANopen从站
   - 支持SDO/PDO
   - 网络管理

## 延伸阅读

### 相关文章

- [UART/USART硬件接口详解](../beginner/01-uart-hardware.html) - 学习串口通信基础
- [SPI硬件接口与应用](../beginner/02-spi-hardware.html) - 学习高速同步通信
- [I2C硬件接口实战](../beginner/03-i2c-hardware.html) - 学习两线总线通信

### 协议标准

- CANopen协议实现
- J1939协议应用

### 硬件设计

- [信号完整性分析](../../02-hardware-design-fundamentals/intermediate/01-signal-integrity.html)
- [EMC设计实战](../../02-hardware-design-fundamentals/intermediate/02-emc-design.html)

## 参考资料

### 数据手册

1. [TJA1050 Datasheet](https://www.nxp.com/docs/en/data-sheet/TJA1050.pdf) - NXP CAN收发器
2. [SN65HVD230 Datasheet](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf) - TI 3.3V CAN收发器
3. [STM32F1 Reference Manual](https://www.st.com/resource/en/reference_manual/cd00171190.pdf) - bxCAN章节

### 技术标准

1. **ISO 11898-1**：CAN数据链路层和物理信令
2. **ISO 11898-2**：CAN高速物理层
3. **ISO 11898-3**：CAN低速容错物理层

### 在线工具

1. [CAN Bit Timing Calculator](https://www.kvaser.com/support/calculators/bit-timing-calculator/) - 位时序计算器
2. [CANopen Calculator](https://www.can-cia.org/can-knowledge/canopen/canopen-tools/) - CANopen工具
3. [CAN Bus Analyzer](https://www.peak-system.com/PCAN-View.242.0.html) - CAN总线分析软件

### 开源项目

1. [SocketCAN](https://github.com/linux-can/can-utils) - Linux CAN工具集
2. [python-can](https://github.com/hardbyte/python-can) - Python CAN库
3. [CANdevStudio](https://github.com/GENIVI/CANdevStudio) - CAN开发工具

## 常见应用场景

### 1. 汽车电子

**应用**：
- 发动机控制
- 车身控制
- 仪表通信
- 诊断系统

**配置**：500 kbps, 标准帧

### 2. 工业自动化

**应用**：
- PLC通信
- 传感器网络
- 运动控制
- 过程控制

**配置**：250 kbps, CANopen协议

### 3. 医疗设备

**应用**：
- 设备互联
- 参数监控
- 数据采集

**配置**：125 kbps, 隔离设计

### 4. 农业机械

**应用**：
- 车辆总线
- 设备控制
- 远程监控

**配置**：250 kbps, J1939协议

### 5. 能源管理

**应用**：
- 电池管理系统
- 充电桩通信
- 储能系统

**配置**：500 kbps, 标准帧

## 附录

### A. 常用波特率配置表

**36MHz APB1时钟**：

| 波特率 | BRP | TS1 | TS2 | SJW | 采样点 |
|--------|-----|-----|-----|-----|--------|
| 1 Mbps | 2 | 6 | 7 | 1 | 78.6% |
| 500 kbps | 4 | 6 | 7 | 1 | 78.6% |
| 250 kbps | 8 | 6 | 7 | 1 | 78.6% |
| 125 kbps | 16 | 6 | 7 | 1 | 78.6% |
| 100 kbps | 20 | 6 | 7 | 1 | 78.6% |
| 50 kbps | 40 | 6 | 7 | 1 | 78.6% |

### B. 收发器对比表

| 型号 | 电压 | 速率 | 节点数 | 特点 |
|------|------|------|--------|------|
| TJA1050 | 5V | 1Mbps | 110 | 标准，广泛使用 |
| TJA1051 | 5V | 1Mbps | 110 | 改进EMC |
| TJA1055 | 5V | 1Mbps | 110 | 低功耗 |
| SN65HVD230 | 3.3V | 1Mbps | 120 | 3.3V供电 |
| MCP2551 | 5V | 1Mbps | 112 | 兼容TJA1050 |
| ISO1050 | 5V | 1Mbps | 110 | 集成隔离 |

### C. 故障排查检查清单

**硬件检查**：
- [ ] 终端电阻已安装（120Ω × 2）
- [ ] 总线阻抗约60Ω
- [ ] CAN_H和CAN_L空闲电压约2.5V
- [ ] 使用双绞线
- [ ] 支线长度<30cm
- [ ] 总线长度符合波特率要求

**软件检查**：
- [ ] 波特率配置正确
- [ ] 位时序配置正确
- [ ] 过滤器配置正确
- [ ] 中断使能
- [ ] 错误处理完善

**测试方法**：
- [ ] 回环测试通过
- [ ] 示波器波形正常
- [ ] 错误计数器正常
- [ ] 通信稳定可靠

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 分享你的项目经验，与其他学习者交流
- 发现文档错误？请提交Issue帮助我们改进

**版权声明**：本文采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。
