---
title: "以太网接口硬件设计"
description: "深入学习以太网硬件接口设计，掌握以太网PHY芯片选型、MII/RMII接口配置、变压器隔离设计、RJ45接口应用、EMC优化措施，实现可靠的网络通信接口"
slug: "ethernet-hardware-interface-design"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 以太网
  - PHY
  - 网络接口
  - MII
  - RMII
  - 变压器隔离
prerequisites:
  - "数字电路基础"
  - "PCB设计基础"
  - "信号完整性基础"
related_contents:
  - "can-bus-hardware-design"
  - "usb-hardware-interface-design"
  - "spi-hardware-interface"

# 学习信息
estimated_time: 55
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
  - 以太网硬件设计
  - 以太网PHY
  - MII接口
  - RMII接口
  - 网络变压器
  - RJ45接口
cover_image: ""
---

# 以太网接口硬件设计

## 概述

以太网（Ethernet）是目前应用最广泛的局域网技术，由Xerox公司于1970年代开发。以太网以其高速率、标准化、成本低的特点，成为工业控制、物联网、嵌入式系统等领域的首选网络通信方案。

完成本文学习后，你将能够：

- 理解以太网的工作原理和硬件架构
- 掌握PHY芯片的选型和应用
- 学会MII/RMII接口的配置
- 理解网络变压器的作用和设计
- 实现STM32的以太网通信
- 掌握以太网接口的EMC设计

## 背景知识

### 以太网 vs 其他网络接口

| 特性 | 以太网 | CAN | USB | RS485 |
|------|--------|-----|-----|-------|
| 速度 | 10/100/1000 Mbps | 最高1Mbps | 最高480Mbps | 最高10Mbps |
| 传输距离 | 100m（双绞线） | 最远10km | 5m | 1200m |
| 拓扑结构 | 星型 | 总线型 | 树型 | 总线型 |
| 协议栈 | TCP/IP | CAN协议 | USB协议 | Modbus等 |
| 应用领域 | 网络通信 | 汽车、工业 | 外设连接 | 工业控制 |
| 成本 | 中等 | 低 | 低 | 低 |
| 复杂度 | 高 | 中 | 高 | 低 |

### 以太网的优势

**高速率**：
- 10BASE-T：10 Mbps
- 100BASE-TX：100 Mbps（Fast Ethernet）
- 1000BASE-T：1000 Mbps（Gigabit Ethernet）

**标准化**：
- IEEE 802.3标准
- 全球统一规范
- 互操作性好

**灵活性**：
- 支持TCP/IP协议栈
- 可接入互联网
- 支持多种应用协议

**成本低**：
- 芯片成本低
- 使用标准网线
- 易于维护


## 以太网硬件架构

### 系统框图

**完整的以太网系统**：

```
┌─────────────────────────────────────────────────────┐
│                   嵌入式系统                          │
│                                                      │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐  │
│  │   应用   │      │  TCP/IP  │      │   驱动   │  │
│  │   层     │ ←──→ │  协议栈  │ ←──→ │   层     │  │
│  └──────────┘      └──────────┘      └──────────┘  │
│                                           ↕          │
│  ┌──────────────────────────────────────────────┐  │
│  │              MCU (STM32)                      │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │         以太网MAC控制器                 │  │  │
│  │  │  (Media Access Control)                │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
│                      ↕ MII/RMII                    │
└──────────────────────┼────────────────────────────┘
                       ↓
┌──────────────────────┼────────────────────────────┐
│              PHY芯片 (物理层)                       │
│  ┌────────────────────────────────────────────┐  │
│  │         以太网PHY收发器                     │  │
│  │  (Physical Layer Transceiver)             │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────┼────────────────────────────┘
                       ↓ 差分信号
┌──────────────────────┼────────────────────────────┐
│              网络变压器                             │
│  ┌────────────────────────────────────────────┐  │
│  │         隔离变压器 (Transformer)            │  │
│  │  - 电气隔离                                 │  │
│  │  - 阻抗匹配                                 │  │
│  │  - 共模抑制                                 │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────┼────────────────────────────┘
                       ↓
┌──────────────────────┼────────────────────────────┐
│              RJ45接口                              │
│  ┌────────────────────────────────────────────┐  │
│  │         RJ45连接器                          │  │
│  │  - 8P8C接口                                 │  │
│  │  - 集成LED指示灯                            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────┼────────────────────────────┘
                       ↓
                   网络电缆
```

### MAC和PHY的分工

**MAC（Media Access Control）**：
- 数据帧的封装和解封装
- MAC地址管理
- 流量控制
- 冲突检测（半双工模式）
- 通常集成在MCU内部

**PHY（Physical Layer）**：
- 物理信号的编码和解码
- 差分信号的发送和接收
- 自动协商（速度和双工模式）
- 链路状态检测
- 独立芯片


## MII和RMII接口

### MII接口（Media Independent Interface）

**MII信号定义**：

```
MCU (MAC)                    PHY芯片
                             
TX_CLK  ←────────────────── 发送时钟（25MHz）
TXD[3:0] ───────────────→   发送数据（4位）
TX_EN   ───────────────→    发送使能
TX_ER   ───────────────→    发送错误（可选）

RX_CLK  ←────────────────── 接收时钟（25MHz）
RXD[3:0] ←──────────────    接收数据（4位）
RX_DV   ←──────────────     接收数据有效
RX_ER   ←──────────────     接收错误（可选）

COL     ←──────────────     冲突检测
CRS     ←──────────────     载波侦听

MDC     ───────────────→    管理时钟
MDIO    ←──────────────→    管理数据

总计：16个信号线
```

**MII时序特性**：

```
100Mbps模式：
- TX_CLK/RX_CLK：25MHz
- 数据宽度：4位
- 每个时钟周期传输4位
- 4位 × 25MHz = 100Mbps

10Mbps模式：
- TX_CLK/RX_CLK：2.5MHz
- 数据宽度：4位
- 每个时钟周期传输4位
- 4位 × 2.5MHz = 10Mbps
```

### RMII接口（Reduced MII）

**RMII信号定义**：

```
MCU (MAC)                    PHY芯片
                             
REF_CLK ←────────────────── 参考时钟（50MHz）
TXD[1:0] ───────────────→   发送数据（2位）
TX_EN   ───────────────→    发送使能

RXD[1:0] ←──────────────    接收数据（2位）
CRS_DV  ←──────────────     载波侦听/数据有效

MDC     ───────────────→    管理时钟
MDIO    ←──────────────→    管理数据

总计：7个信号线
```

**RMII时序特性**：

```
100Mbps模式：
- REF_CLK：50MHz
- 数据宽度：2位
- 每个时钟周期传输2位
- 2位 × 50MHz = 100Mbps

10Mbps模式：
- REF_CLK：50MHz
- 数据宽度：2位
- 每10个时钟周期传输2位
- 2位 × 5MHz = 10Mbps
```

### MII vs RMII对比

| 特性 | MII | RMII |
|------|-----|------|
| 信号线数量 | 16根 | 7根 |
| 时钟频率 | 25MHz/2.5MHz | 50MHz |
| 数据宽度 | 4位 | 2位 |
| PCB布线 | 复杂 | 简单 |
| 功耗 | 较高 | 较低 |
| 成本 | 较高 | 较低 |
| 应用 | 高性能系统 | 嵌入式系统 |

**推荐选择**：
- 嵌入式系统：优先选择RMII
- 高性能系统：可选择MII
- 成本敏感：选择RMII


## PHY芯片选型

### 常用PHY芯片

**1. LAN8720A（最常用）**：

| 参数 | 值 |
|------|-----|
| 接口 | RMII |
| 速度 | 10/100 Mbps |
| 工作电压 | 3.3V |
| 封装 | QFN-24 |
| 特点 | 成本低，应用广泛 |
| 厂商 | Microchip |

**2. DP83848（TI）**：

| 参数 | 值 |
|------|-----|
| 接口 | MII/RMII |
| 速度 | 10/100 Mbps |
| 工作电压 | 3.3V |
| 封装 | LQFP-48 |
| 特点 | 工业级，可靠性高 |
| 厂商 | Texas Instruments |

**3. RTL8201F（Realtek）**：

| 参数 | 值 |
|------|-----|
| 接口 | MII/RMII |
| 速度 | 10/100 Mbps |
| 工作电压 | 3.3V |
| 封装 | QFN-32 |
| 特点 | 集成LED驱动 |
| 厂商 | Realtek |

**4. KSZ8081（Microchip）**：

| 参数 | 值 |
|------|-----|
| 接口 | MII/RMII |
| 速度 | 10/100 Mbps |
| 工作电压 | 3.3V/2.5V |
| 封装 | QFN-24 |
| 特点 | 低功耗，支持HP Auto-MDIX |
| 厂商 | Microchip |

### PHY芯片引脚功能

**LAN8720A引脚图（RMII模式）**：

```
        LAN8720A (QFN-24)
     ┌──────────────────┐
VDD  ┤1              24├ VDDCR
TXD0 ┤2              23├ LED2/nINTSEL
TXD1 ┤3              22├ LED1/REGOFF
TX_EN┤4              21├ XTAL2
RXD0 ┤5              20├ XTAL1
RXD1 ┤6              19├ MDC
CRS_DV┤7             18├ MDIO
REF_CLK┤8            17├ nINT/REFCLKO
     │                 │
GND  ┤9              16├ nRST
     └──────────────────┘

关键引脚：
- VDD: 3.3V电源
- VDDCR: 内部1.2V稳压器输出
- TXD[1:0]: 发送数据
- RXD[1:0]: 接收数据
- REF_CLK: 50MHz参考时钟
- MDC/MDIO: 管理接口
- nRST: 复位（低电平有效）
```

### PHY地址配置

**MDIO地址设置**：

```
PHY地址通过硬件引脚配置：

LAN8720A地址配置：
- 地址0：RXD0=0, RXD1=0
- 地址1：RXD0=1, RXD1=0
- 地址2：RXD0=0, RXD1=1
- 地址3：RXD0=1, RXD1=1

配置方法：
在nRST释放时，RXD0和RXD1的电平
决定PHY地址

示例（地址1）：
RXD0 ──┬── 10kΩ ── VDD
       │
RXD1 ──┴── 10kΩ ── GND
```


## 网络变压器设计

### 变压器的作用

**为什么需要网络变压器**：

```
1. 电气隔离：
   - 隔离PHY和网线
   - 保护设备免受浪涌冲击
   - 防止地环路

2. 阻抗匹配：
   - PHY侧：50Ω
   - 网线侧：100Ω
   - 变压器实现阻抗转换

3. 共模抑制：
   - 抑制共模干扰
   - 改善EMC性能
   - 提高信号质量

4. 直流隔离：
   - 隔离直流分量
   - 只传输交流信号
```

### 变压器类型

**1. 分立变压器**：

```
PHY芯片 ──→ 变压器 ──→ RJ45接口

优点：
- 灵活性高
- 可选择不同规格
- 易于更换

缺点：
- 占用空间大
- 需要额外的中心抽头电容
- 布线复杂
```

**2. 集成变压器（带RJ45）**：

```
PHY芯片 ──→ 集成模块（变压器+RJ45）

优点：
- 节省空间
- 简化设计
- 减少布线
- 集成LED指示灯

缺点：
- 成本稍高
- 灵活性较低

推荐型号：
- HanRun HR911105A
- Pulse J0011D21BNL
- Wurth 7499111121
```

### 变压器电路设计

**标准变压器连接**：

```
PHY (LAN8720A)              变压器              RJ45
                                                
TXP ──┬─── 49.9Ω ───┬──→ ┌───┐ ──→ TD+ ──→ Pin 1
      │             │     │   │
      └─ 0.1μF ─┬─ GND    │ T │
                │         │ X │
TXN ──┬─── 49.9Ω ───┴──→ └───┘ ──→ TD- ──→ Pin 2
      │
      └─ 0.1μF ─── GND

RXP ←─┬─── 49.9Ω ───┬──← ┌───┐ ←── RD+ ←── Pin 3
      │             │     │   │
      └─ 0.1μF ─┬─ GND    │ R │
                │         │ X │
RXN ←─┬─── 49.9Ω ───┴──← └───┘ ←── RD- ←── Pin 6
      │
      └─ 0.1μF ─── GND

中心抽头电容：
- 发送侧：0.1μF × 2
- 接收侧：0.1μF × 2
- 作用：提供直流偏置路径

终端电阻：
- 49.9Ω × 4
- 作用：阻抗匹配
```

### RJ45接口引脚定义

**8P8C标准接口**：

```
RJ45接口（正面视图）
┌─────────────┐
│ 8 7 6 5 4 3 2 1 │
└─────────────┘

引脚定义（100BASE-TX）：
Pin 1: TD+  (发送正)
Pin 2: TD-  (发送负)
Pin 3: RD+  (接收正)
Pin 4: NC   (未使用)
Pin 5: NC   (未使用)
Pin 6: RD-  (接收负)
Pin 7: NC   (未使用)
Pin 8: NC   (未使用)

注意：
- 只使用4根线（1,2,3,6）
- 其他引脚在1000BASE-T中使用
```


## 硬件电路设计

### 基本以太网电路

**STM32 + LAN8720A完整电路**：

```
STM32F407                    LAN8720A              变压器+RJ45
                                                   
PA1  (REF_CLK) ←──────────── REF_CLK              
PA2  (MDIO)    ←──────────→  MDIO                 
PC1  (MDC)     ───────────→  MDC                  
                                                   
PG11 (TX_EN)   ───────────→  TX_EN                
PG13 (TXD0)    ───────────→  TXD0 ──┬─ 49.9Ω ─→ TD+
PG14 (TXD1)    ───────────→  TXD1 ──┴─ 49.9Ω ─→ TD-
                                                   
PC4  (RXD0)    ←──────────── RXD0 ←─┬─ 49.9Ω ←─ RD+
PC5  (RXD1)    ←──────────── RXD1 ←─┴─ 49.9Ω ←─ RD-
PA7  (CRS_DV)  ←──────────── CRS_DV               
                                                   
PG8  (nRST)    ───────────→  nRST                 
                             │                     
3.3V ─┬─ 0.1μF ─┬─ VDD ─────┤                     
      └─ 10μF ──┘            │                     
                             │                     
GND ──────────────── GND ────┤                     
                             │                     
                          VDDCR ─┬─ 10μF ─┬─ GND  
                                 └─ 0.1μF ┘        
                                                   
25MHz晶振：                                        
XTAL1 ──┬─── 晶振 ───┬─── XTAL2                   
        │            │                             
        ├─ 22pF ─┬─ GND                            
        │        │                                 
        └────────┴─ 22pF ─── GND                   
```

### 电源设计

**1. 3.3V主电源**：

```
5V ──┬─── LDO ───┬─── 3.3V ──→ PHY VDD
     │  (AMS1117) │
     │            ├─── 10μF ──┬─ GND
     │            │           │
     │            └─── 0.1μF ─┘
    GND

要求：
- 输出电流：≥200mA
- 纹波：<50mV
- 去耦电容：10μF + 0.1μF
```

**2. 内部稳压器**：

```
LAN8720A内部1.2V稳压器：

VDDCR ──┬─── 10μF ──┬─── GND
        │           │
        └─── 0.1μF ─┘

注意：
- VDDCR输出1.2V
- 必须外接去耦电容
- 10μF钽电容或陶瓷电容
- 0.1μF高频去耦
```

### 时钟设计

**1. 外部晶振（可选）**：

```
25MHz晶振电路：

XTAL1 ──┬─── 晶振 ───┬─── XTAL2
        │   (25MHz)  │
        │            │
        ├─ 22pF ─┬─ GND
        │        │
        └────────┴─ 22pF ─── GND

要求：
- 频率：25MHz ± 50ppm
- 负载电容：18-22pF
- ESR：<100Ω
```

**2. 外部时钟输入（推荐）**：

```
50MHz时钟源 ──→ REF_CLK (LAN8720A)
                    │
                    └──→ REF_CLK (STM32)

优点：
- 节省成本
- 减少元件
- 提高可靠性

时钟源：
- 有源晶振
- 时钟发生器
- MCU输出时钟
```


## PCB布局设计

### 布局原则

**1. 整体布局**：

```
推荐布局顺序：
1. RJ45接口放置在板边
2. 网络变压器紧邻RJ45
3. PHY芯片靠近变压器
4. MCU尽量靠近PHY

布局示意：
┌─────────────────────────┐
│                         │
│  [RJ45+变压器]          │ ← 板边
│       ↓                 │
│  [PHY芯片]              │ ← 距离<5cm
│       ↓                 │
│  [MCU]                  │ ← 尽量靠近
│                         │
└─────────────────────────┘
```

**2. 差分对布局**：

```
差分对走线要求：
- 保持平行
- 等长等宽
- 避免分叉
- 避免过孔

正确示例：
TD+ ═══════════════════
TD- ═══════════════════

错误示例：
TD+ ═══╗     ╔═════════
       ╚═════╝
TD- ═══════════════════
```

### 走线设计

**1. 差分对走线**：

```
走线参数（4层板）：
- 线宽：8mil（0.2mm）
- 间距：8mil（0.2mm）
- 差分阻抗：100Ω ± 10%
- 长度差：< 5mm

走线技巧：
1. 使用差分对走线工具
2. 保持等长
3. 避免直角转弯（使用45°或圆弧）
4. 避免跨越分割
```

**2. 时钟走线**：

```
REF_CLK走线要求：
- 尽量短
- 远离干扰源
- 包地处理
- 阻抗控制50Ω

走线示意：
PHY ═══ REF_CLK ═══ MCU
        ↓
       GND (包地)
```

**3. 地平面处理**：

```
地平面要求：
- 差分对下方保持完整地平面
- 不要分割地平面
- 多层板各层地平面互连

地平面示意：
┌─────────────────────┐
│  Top: 差分对         │
├─────────────────────┤
│  GND: 完整地平面     │ ← 参考平面
├─────────────────────┤
│  Power: 电源层       │
├─────────────────────┤
│  Bottom: 信号层      │
└─────────────────────┘
```

### EMC优化

**1. 共模扼流圈**：

```
添加共模扼流圈（CMC）：

PHY ─── TD+ ───┬─ CMC ─┬─── 变压器
               │       │
PHY ─── TD- ───┴───────┴─── 变压器

作用：
- 抑制共模干扰
- 改善EMC性能
- 不影响差分信号

推荐型号：
- Murata DLW5BSN900SQ2L
- TDK ACM2012-900-2P
```

**2. ESD保护**：

```
ESD保护电路：

RJ45 ──┬─── TVS ───┬─── 变压器
       │           │
      GND         GND

推荐器件：
- PESD5V0S4UF（4通道）
- TPD4E05U06（4通道）
- 钳位电压：<6V
- 电容：<5pF
```

**3. 屏蔽设计**：

```
屏蔽措施：
1. 使用带屏蔽的RJ45接口
2. 屏蔽层连接到GND
3. 在接口周围铺地
4. 使用屏蔽网线

屏蔽接口示意：
┌─────────────┐
│  RJ45接口   │
│  ┌───────┐  │
│  │ 屏蔽层 │  │ ← 连接到GND
│  └───────┘  │
└─────────────┘
```


## STM32以太网配置

### 硬件初始化

**GPIO和以太网外设配置**：

```c
// 1. 使能时钟
RCC->AHB1ENR |= RCC_AHB1ENR_ETHMACEN |      // 以太网MAC
                RCC_AHB1ENR_ETHMACTXEN |    // 以太网MAC TX
                RCC_AHB1ENR_ETHMACRXEN;     // 以太网MAC RX

RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN |       // GPIOA
                RCC_AHB1ENR_GPIOCEN |       // GPIOC
                RCC_AHB1ENR_GPIOGEN;        // GPIOG

// 2. 配置GPIO（RMII模式）
// PA1 (REF_CLK) - 复用功能
GPIOA->MODER &= ~(3 << 2);
GPIOA->MODER |= (2 << 2);
GPIOA->AFR[0] |= (11 << 4);  // AF11

// PA2 (MDIO) - 复用功能
GPIOA->MODER &= ~(3 << 4);
GPIOA->MODER |= (2 << 4);
GPIOA->AFR[0] |= (11 << 8);  // AF11

// PA7 (CRS_DV) - 复用功能
GPIOA->MODER &= ~(3 << 14);
GPIOA->MODER |= (2 << 14);
GPIOA->AFR[0] |= (11 << 28);  // AF11

// PC1 (MDC) - 复用功能
GPIOC->MODER &= ~(3 << 2);
GPIOC->MODER |= (2 << 2);
GPIOC->AFR[0] |= (11 << 4);  // AF11

// PC4 (RXD0) - 复用功能
GPIOC->MODER &= ~(3 << 8);
GPIOC->MODER |= (2 << 8);
GPIOC->AFR[0] |= (11 << 16);  // AF11

// PC5 (RXD1) - 复用功能
GPIOC->MODER &= ~(3 << 10);
GPIOC->MODER |= (2 << 10);
GPIOC->AFR[0] |= (11 << 20);  // AF11

// PG11 (TX_EN) - 复用功能
GPIOG->MODER &= ~(3 << 22);
GPIOG->MODER |= (2 << 22);
GPIOG->AFR[1] |= (11 << 12);  // AF11

// PG13 (TXD0) - 复用功能
GPIOG->MODER &= ~(3 << 26);
GPIOG->MODER |= (2 << 26);
GPIOG->AFR[1] |= (11 << 20);  // AF11

// PG14 (TXD1) - 复用功能
GPIOG->MODER &= ~(3 << 28);
GPIOG->MODER |= (2 << 28);
GPIOG->AFR[1] |= (11 << 24);  // AF11

// 3. 配置GPIO速度（高速）
GPIOA->OSPEEDR |= (3 << 2) | (3 << 4) | (3 << 14);
GPIOC->OSPEEDR |= (3 << 2) | (3 << 8) | (3 << 10);
GPIOG->OSPEEDR |= (3 << 22) | (3 << 26) | (3 << 28);
```

### PHY芯片初始化

```c
// PHY寄存器地址
#define PHY_BCR         0x00  // 基本控制寄存器
#define PHY_BSR         0x01  // 基本状态寄存器
#define PHY_ID1         0x02  // PHY标识符1
#define PHY_ID2         0x03  // PHY标识符2
#define PHY_ANAR        0x04  // 自动协商通告寄存器
#define PHY_ANLPAR      0x05  // 自动协商链路伙伴能力寄存器

// PHY地址（根据硬件配置）
#define PHY_ADDRESS     0x01

// 读取PHY寄存器
uint16_t ETH_ReadPHYRegister(uint8_t reg) {
    uint32_t timeout = 0;
    
    // 等待MDIO空闲
    while (ETH->MACMIIAR & ETH_MACMIIAR_MB) {
        if (++timeout > 1000) return 0xFFFF;
    }
    
    // 配置MDIO读操作
    ETH->MACMIIAR = (PHY_ADDRESS << 11) |  // PHY地址
                    (reg << 6) |            // 寄存器地址
                    ETH_MACMIIAR_CR_Div42 | // 时钟分频
                    ETH_MACMIIAR_MB;        // 开始操作
    
    // 等待操作完成
    timeout = 0;
    while (ETH->MACMIIAR & ETH_MACMIIAR_MB) {
        if (++timeout > 1000) return 0xFFFF;
    }
    
    // 返回读取的数据
    return (uint16_t)(ETH->MACMIIDR);
}

// 写入PHY寄存器
bool ETH_WritePHYRegister(uint8_t reg, uint16_t value) {
    uint32_t timeout = 0;
    
    // 等待MDIO空闲
    while (ETH->MACMIIAR & ETH_MACMIIAR_MB) {
        if (++timeout > 1000) return false;
    }
    
    // 写入数据
    ETH->MACMIIDR = value;
    
    // 配置MDIO写操作
    ETH->MACMIIAR = (PHY_ADDRESS << 11) |  // PHY地址
                    (reg << 6) |            // 寄存器地址
                    ETH_MACMIIAR_MW |       // 写操作
                    ETH_MACMIIAR_CR_Div42 | // 时钟分频
                    ETH_MACMIIAR_MB;        // 开始操作
    
    // 等待操作完成
    timeout = 0;
    while (ETH->MACMIIAR & ETH_MACMIIAR_MB) {
        if (++timeout > 1000) return false;
    }
    
    return true;
}

// PHY初始化
bool ETH_PHY_Init(void) {
    uint16_t reg_value;
    uint32_t timeout = 0;
    
    // 1. 读取PHY ID
    uint16_t id1 = ETH_ReadPHYRegister(PHY_ID1);
    uint16_t id2 = ETH_ReadPHYRegister(PHY_ID2);
    printf("PHY ID: 0x%04X%04X\n", id1, id2);
    
    // 2. 软复位PHY
    ETH_WritePHYRegister(PHY_BCR, 0x8000);
    
    // 等待复位完成
    do {
        reg_value = ETH_ReadPHYRegister(PHY_BCR);
        if (++timeout > 1000) return false;
    } while (reg_value & 0x8000);
    
    // 3. 配置自动协商
    ETH_WritePHYRegister(PHY_ANAR, 0x01E1);  // 10/100Mbps, 全/半双工
    
    // 4. 启动自动协商
    ETH_WritePHYRegister(PHY_BCR, 0x1200);  // 使能自动协商
    
    // 5. 等待链路建立
    timeout = 0;
    do {
        reg_value = ETH_ReadPHYRegister(PHY_BSR);
        HAL_Delay(10);
        if (++timeout > 500) {
            printf("Link timeout\n");
            return false;
        }
    } while (!(reg_value & 0x0004));  // 等待链路状态位
    
    printf("Link established\n");
    return true;
}
```


### MAC控制器配置

```c
// MAC初始化
void ETH_MAC_Init(void) {
    // 1. 软复位MAC
    ETH->DMABMR |= ETH_DMABMR_SR;
    while (ETH->DMABMR & ETH_DMABMR_SR);
    
    // 2. 配置MAC
    ETH->MACCR = ETH_MACCR_FES |      // 快速以太网（100Mbps）
                 ETH_MACCR_DM |       // 全双工模式
                 ETH_MACCR_IPCO |     // IPv4校验和卸载
                 ETH_MACCR_RD |       // 禁用重试
                 ETH_MACCR_APCS;      // 自动去除CRC
    
    // 3. 配置MAC帧过滤
    ETH->MACFFR = ETH_MACFFR_RA;      // 接收所有帧（混杂模式）
    
    // 4. 配置MAC地址
    ETH->MACA0HR = (MAC_ADDR[5] << 8) | MAC_ADDR[4];
    ETH->MACA0LR = (MAC_ADDR[3] << 24) | (MAC_ADDR[2] << 16) |
                   (MAC_ADDR[1] << 8) | MAC_ADDR[0];
    
    // 5. 配置DMA
    ETH->DMAOMR = ETH_DMAOMR_RSF |    // 接收存储转发
                  ETH_DMAOMR_TSF |    // 发送存储转发
                  ETH_DMAOMR_OSF;     // 操作第二帧
    
    // 6. 配置DMA总线模式
    ETH->DMABMR = ETH_DMABMR_AAB |    // 地址对齐突发
                  ETH_DMABMR_FB |     // 固定突发
                  ETH_DMABMR_RDP_32Beat | // RX DMA突发长度
                  ETH_DMABMR_PBL_32Beat | // 可编程突发长度
                  ETH_DMABMR_USP;     // 使用独立PBL
    
    // 7. 使能MAC和DMA
    ETH->MACCR |= ETH_MACCR_TE | ETH_MACCR_RE;  // 使能发送和接收
    ETH->DMAOMR |= ETH_DMAOMR_ST | ETH_DMAOMR_SR; // 启动DMA
}
```

### 数据发送和接收

```c
// 以太网描述符结构
typedef struct {
    uint32_t Status;
    uint32_t ControlBufferSize;
    uint32_t Buffer1Addr;
    uint32_t Buffer2NextDescAddr;
} ETH_DMADescTypeDef;

// 发送和接收缓冲区
#define ETH_RXBUFNB        4
#define ETH_TXBUFNB        2
#define ETH_RX_BUF_SIZE    1524
#define ETH_TX_BUF_SIZE    1524

__attribute__((aligned(4))) ETH_DMADescTypeDef DMARxDscrTab[ETH_RXBUFNB];
__attribute__((aligned(4))) ETH_DMADescTypeDef DMATxDscrTab[ETH_TXBUFNB];
__attribute__((aligned(4))) uint8_t Rx_Buff[ETH_RXBUFNB][ETH_RX_BUF_SIZE];
__attribute__((aligned(4))) uint8_t Tx_Buff[ETH_TXBUFNB][ETH_TX_BUF_SIZE];

// 初始化DMA描述符
void ETH_DMATxDescListInit(void) {
    for (int i = 0; i < ETH_TXBUFNB; i++) {
        DMATxDscrTab[i].Status = ETH_DMATXDESC_TCH;
        DMATxDscrTab[i].Buffer1Addr = (uint32_t)(&Tx_Buff[i][0]);
        
        if (i < (ETH_TXBUFNB - 1)) {
            DMATxDscrTab[i].Buffer2NextDescAddr = (uint32_t)(&DMATxDscrTab[i + 1]);
        } else {
            DMATxDscrTab[i].Buffer2NextDescAddr = (uint32_t)(&DMATxDscrTab[0]);
        }
    }
    
    // 设置发送描述符地址
    ETH->DMATDLAR = (uint32_t)DMATxDscrTab;
}

void ETH_DMARxDescListInit(void) {
    for (int i = 0; i < ETH_RXBUFNB; i++) {
        DMARxDscrTab[i].Status = ETH_DMARXDESC_OWN;
        DMARxDscrTab[i].ControlBufferSize = ETH_DMARXDESC_RCH | ETH_RX_BUF_SIZE;
        DMARxDscrTab[i].Buffer1Addr = (uint32_t)(&Rx_Buff[i][0]);
        
        if (i < (ETH_RXBUFNB - 1)) {
            DMARxDscrTab[i].Buffer2NextDescAddr = (uint32_t)(&DMARxDscrTab[i + 1]);
        } else {
            DMARxDscrTab[i].Buffer2NextDescAddr = (uint32_t)(&DMARxDscrTab[0]);
        }
    }
    
    // 设置接收描述符地址
    ETH->DMARDLAR = (uint32_t)DMARxDscrTab;
}

// 发送数据帧
bool ETH_TransmitFrame(uint8_t *data, uint16_t len) {
    static uint32_t tx_index = 0;
    
    // 检查描述符是否可用
    if (DMATxDscrTab[tx_index].Status & ETH_DMATXDESC_OWN) {
        return false;  // 描述符忙
    }
    
    // 复制数据到发送缓冲区
    memcpy((uint8_t *)DMATxDscrTab[tx_index].Buffer1Addr, data, len);
    
    // 配置描述符
    DMATxDscrTab[tx_index].ControlBufferSize = len & ETH_DMATXDESC_TBS1;
    DMATxDscrTab[tx_index].Status = ETH_DMATXDESC_OWN |
                                     ETH_DMATXDESC_FS |
                                     ETH_DMATXDESC_LS |
                                     ETH_DMATXDESC_IC;
    
    // 启动发送
    if (ETH->DMASR & ETH_DMASR_TBUS) {
        ETH->DMASR = ETH_DMASR_TBUS;
        ETH->DMATPDR = 0;
    }
    
    // 更新索引
    tx_index = (tx_index + 1) % ETH_TXBUFNB;
    
    return true;
}

// 接收数据帧
uint16_t ETH_ReceiveFrame(uint8_t *buffer, uint16_t max_len) {
    static uint32_t rx_index = 0;
    uint16_t len = 0;
    
    // 检查是否有数据
    if (DMARxDscrTab[rx_index].Status & ETH_DMARXDESC_OWN) {
        return 0;  // 无数据
    }
    
    // 检查帧状态
    if ((DMARxDscrTab[rx_index].Status & ETH_DMARXDESC_ES) == 0 &&
        (DMARxDscrTab[rx_index].Status & ETH_DMARXDESC_LS) &&
        (DMARxDscrTab[rx_index].Status & ETH_DMARXDESC_FS)) {
        
        // 获取帧长度
        len = ((DMARxDscrTab[rx_index].Status & ETH_DMARXDESC_FL) >> 16) - 4;
        
        // 复制数据
        if (len <= max_len) {
            memcpy(buffer, (uint8_t *)DMARxDscrTab[rx_index].Buffer1Addr, len);
        } else {
            len = 0;  // 缓冲区太小
        }
    }
    
    // 释放描述符
    DMARxDscrTab[rx_index].Status = ETH_DMARXDESC_OWN;
    
    // 恢复接收
    if (ETH->DMASR & ETH_DMASR_RBUS) {
        ETH->DMASR = ETH_DMASR_RBUS;
        ETH->DMARPDR = 0;
    }
    
    // 更新索引
    rx_index = (rx_index + 1) % ETH_RXBUFNB;
    
    return len;
}
```


## 常见问题与调试

### 问题1：无法建立链路

**可能原因**：

1. **硬件连接问题**
   - 检查：网线是否正常
   - 检查：RJ45接口是否接触良好
   - 解决：更换网线，检查接口

2. **PHY配置问题**
   - 检查：PHY地址是否正确
   - 检查：时钟是否正常
   - 解决：确认PHY地址配置，检查时钟信号

3. **变压器问题**
   - 检查：变压器是否损坏
   - 检查：终端电阻是否正确
   - 解决：更换变压器，检查电阻值

**调试步骤**：

```c
// 检查PHY状态
void Debug_CheckPHYStatus(void) {
    uint16_t bsr = ETH_ReadPHYRegister(PHY_BSR);
    
    printf("=== PHY状态 ===\n");
    
    if (bsr & 0x0004) {
        printf("链路状态: 已连接\n");
    } else {
        printf("链路状态: 未连接\n");
    }
    
    if (bsr & 0x0020) {
        printf("自动协商: 完成\n");
    } else {
        printf("自动协商: 进行中\n");
    }
    
    if (bsr & 0x0001) {
        printf("扩展能力: 支持\n");
    }
    
    // 读取链路伙伴能力
    uint16_t anlpar = ETH_ReadPHYRegister(PHY_ANLPAR);
    printf("链路伙伴能力: 0x%04X\n", anlpar);
    
    if (anlpar & 0x0100) {
        printf("  - 100BASE-TX 全双工\n");
    }
    if (anlpar & 0x0080) {
        printf("  - 100BASE-TX 半双工\n");
    }
    if (anlpar & 0x0040) {
        printf("  - 10BASE-T 全双工\n");
    }
    if (anlpar & 0x0020) {
        printf("  - 10BASE-T 半双工\n");
    }
}
```

### 问题2：数据传输错误

**可能原因**：

1. **信号完整性问题**
   - 检查：差分阻抗是否为100Ω
   - 检查：走线是否等长
   - 解决：优化PCB布线

2. **EMI干扰**
   - 检查：是否有干扰源
   - 检查：地平面是否完整
   - 解决：添加共模扼流圈，改善屏蔽

3. **MAC配置问题**
   - 检查：MAC地址是否正确
   - 检查：DMA配置是否正确
   - 解决：检查配置参数

**错误统计**：

```c
// 以太网错误计数器
typedef struct {
    uint32_t tx_errors;
    uint32_t rx_errors;
    uint32_t crc_errors;
    uint32_t collision_errors;
} ETH_ErrorCounter_t;

ETH_ErrorCounter_t eth_errors = {0};

// 错误监控
void ETH_MonitorErrors(void) {
    uint32_t dmasr = ETH->DMASR;
    
    // 检查发送错误
    if (dmasr & ETH_DMASR_TPS) {
        eth_errors.tx_errors++;
        printf("发送错误计数: %lu\n", eth_errors.tx_errors);
    }
    
    // 检查接收错误
    if (dmasr & ETH_DMASR_RPS) {
        eth_errors.rx_errors++;
        printf("接收错误计数: %lu\n", eth_errors.rx_errors);
    }
    
    // 清除错误标志
    ETH->DMASR = dmasr;
}
```

### 问题3：传输速率低

**可能原因**：

1. **协商速度低**
   - 检查：协商结果是10Mbps还是100Mbps
   - 解决：强制100Mbps模式

2. **DMA配置不当**
   - 检查：DMA突发长度
   - 检查：缓冲区大小
   - 解决：优化DMA配置

3. **CPU处理延迟**
   - 检查：中断处理时间
   - 解决：使用DMA，优化中断处理

**性能优化**：

```c
// 强制100Mbps全双工
void ETH_Force100MFullDuplex(void) {
    // 禁用自动协商，强制100Mbps全双工
    ETH_WritePHYRegister(PHY_BCR, 0x2100);
    
    // 配置MAC为100Mbps全双工
    ETH->MACCR |= ETH_MACCR_FES | ETH_MACCR_DM;
    
    printf("强制100Mbps全双工模式\n");
}

// 优化DMA配置
void ETH_OptimizeDMA(void) {
    // 增大DMA突发长度
    ETH->DMABMR &= ~ETH_DMABMR_PBL;
    ETH->DMABMR |= ETH_DMABMR_PBL_32Beat;
    
    // 使能存储转发模式
    ETH->DMAOMR |= ETH_DMAOMR_RSF | ETH_DMAOMR_TSF;
    
    printf("DMA配置已优化\n");
}
```


## 实用技巧

### 1. LED指示灯配置

```c
// 配置PHY LED指示灯
void ETH_ConfigureLED(void) {
    // LAN8720A LED配置
    // LED1: 链路状态/活动
    // LED2: 速度指示
    
    // 读取特殊模式寄存器
    uint16_t reg = ETH_ReadPHYRegister(0x1F);
    
    // 配置LED模式
    reg &= ~0x00F0;  // 清除LED配置位
    reg |= 0x0010;   // LED1: 链路/活动, LED2: 速度
    
    ETH_WritePHYRegister(0x1F, reg);
    
    printf("LED配置完成\n");
}
```

### 2. 网络唤醒（WoL）

```c
// 配置网络唤醒
void ETH_ConfigureWakeOnLAN(void) {
    // 使能魔术包检测
    ETH->MACPMTCSR |= ETH_MACPMTCSR_MPE;
    
    // 使能PMT中断
    ETH->MACIMR &= ~ETH_MACIMR_PMTIM;
    
    printf("网络唤醒已使能\n");
}

// 进入低功耗模式
void ETH_EnterLowPower(void) {
    // 配置PHY进入低功耗模式
    uint16_t bcr = ETH_ReadPHYRegister(PHY_BCR);
    bcr |= 0x0800;  // 使能低功耗模式
    ETH_WritePHYRegister(PHY_BCR, bcr);
    
    // 配置MAC进入低功耗模式
    ETH->MACPMTCSR |= ETH_MACPMTCSR_PD;
    
    printf("进入低功耗模式\n");
}
```

### 3. 环回测试

```c
// PHY环回测试
void ETH_LoopbackTest(void) {
    printf("开始环回测试...\n");
    
    // 使能PHY内部环回
    uint16_t bcr = ETH_ReadPHYRegister(PHY_BCR);
    bcr |= 0x4000;  // 使能环回
    ETH_WritePHYRegister(PHY_BCR, bcr);
    
    // 准备测试数据
    uint8_t tx_data[64];
    uint8_t rx_data[64];
    
    for (int i = 0; i < 64; i++) {
        tx_data[i] = i;
    }
    
    // 发送数据
    ETH_TransmitFrame(tx_data, 64);
    HAL_Delay(10);
    
    // 接收数据
    uint16_t len = ETH_ReceiveFrame(rx_data, 64);
    
    // 验证数据
    bool pass = true;
    if (len == 64) {
        for (int i = 0; i < 64; i++) {
            if (tx_data[i] != rx_data[i]) {
                pass = false;
                break;
            }
        }
    } else {
        pass = false;
    }
    
    // 禁用环回
    bcr &= ~0x4000;
    ETH_WritePHYRegister(PHY_BCR, bcr);
    
    if (pass) {
        printf("环回测试通过\n");
    } else {
        printf("环回测试失败\n");
    }
}
```

### 4. 链路状态监控

```c
// 链路状态监控
void ETH_MonitorLinkStatus(void) {
    static bool last_link_state = false;
    bool current_link_state;
    
    // 读取链路状态
    uint16_t bsr = ETH_ReadPHYRegister(PHY_BSR);
    current_link_state = (bsr & 0x0004) != 0;
    
    // 检测链路变化
    if (current_link_state != last_link_state) {
        if (current_link_state) {
            printf("链路已连接\n");
            
            // 读取协商结果
            uint16_t anlpar = ETH_ReadPHYRegister(PHY_ANLPAR);
            
            if (anlpar & 0x0100) {
                printf("速度: 100Mbps 全双工\n");
            } else if (anlpar & 0x0080) {
                printf("速度: 100Mbps 半双工\n");
            } else if (anlpar & 0x0040) {
                printf("速度: 10Mbps 全双工\n");
            } else if (anlpar & 0x0020) {
                printf("速度: 10Mbps 半双工\n");
            }
        } else {
            printf("链路已断开\n");
        }
        
        last_link_state = current_link_state;
    }
}
```

## 性能优化

### 提高吞吐量

**1. 使用零拷贝技术**：

```c
// 零拷贝发送（直接使用DMA缓冲区）
bool ETH_TransmitZeroCopy(uint8_t **buffer, uint16_t len) {
    static uint32_t tx_index = 0;
    
    // 检查描述符是否可用
    if (DMATxDscrTab[tx_index].Status & ETH_DMATXDESC_OWN) {
        return false;
    }
    
    // 返回缓冲区指针
    *buffer = (uint8_t *)DMATxDscrTab[tx_index].Buffer1Addr;
    
    // 配置描述符
    DMATxDscrTab[tx_index].ControlBufferSize = len & ETH_DMATXDESC_TBS1;
    DMATxDscrTab[tx_index].Status = ETH_DMATXDESC_OWN |
                                     ETH_DMATXDESC_FS |
                                     ETH_DMATXDESC_LS |
                                     ETH_DMATXDESC_IC;
    
    // 启动发送
    if (ETH->DMASR & ETH_DMASR_TBUS) {
        ETH->DMASR = ETH_DMASR_TBUS;
        ETH->DMATPDR = 0;
    }
    
    // 更新索引
    tx_index = (tx_index + 1) % ETH_TXBUFNB;
    
    return true;
}
```

**2. 增大缓冲区**：

```c
// 增大接收缓冲区数量
#define ETH_RXBUFNB        8  // 从4增加到8
#define ETH_TXBUFNB        4  // 从2增加到4

// 增大缓冲区大小
#define ETH_RX_BUF_SIZE    2048  // 从1524增加到2048
#define ETH_TX_BUF_SIZE    2048
```

### 降低延迟

**1. 使用中断模式**：

```c
// 使能以太网中断
void ETH_EnableInterrupt(void) {
    // 使能接收中断
    ETH->DMAIER |= ETH_DMAIER_NISE | ETH_DMAIER_RIE;
    
    // 配置NVIC
    NVIC_EnableIRQ(ETH_IRQn);
    NVIC_SetPriority(ETH_IRQn, 0);  // 最高优先级
}

// 中断处理函数
void ETH_IRQHandler(void) {
    uint32_t dmasr = ETH->DMASR;
    
    // 接收中断
    if (dmasr & ETH_DMASR_RS) {
        // 立即处理接收数据
        ETH_ProcessReceivedData();
        
        // 清除中断标志
        ETH->DMASR = ETH_DMASR_RS | ETH_DMASR_NIS;
    }
}
```

**2. 优化协议栈**：

```c
// 使用轻量级TCP/IP协议栈（如lwIP）
// 配置lwIP选项以降低延迟

#define LWIP_NETIF_TX_SINGLE_PBUF  1  // 单个pbuf发送
#define TCP_SND_QUEUELEN           8  // 发送队列长度
#define MEMP_NUM_TCP_SEG           16 // TCP段数量
#define PBUF_POOL_SIZE             16 // pbuf池大小
```


## 总结

通过本文学习，你已经掌握了：

- ✅ **以太网基础**：MAC/PHY架构、MII/RMII接口、信号定义
- ✅ **PHY芯片**：选型方法、引脚功能、地址配置
- ✅ **变压器设计**：作用原理、类型选择、电路连接
- ✅ **硬件设计**：电源设计、时钟设计、PCB布局
- ✅ **STM32配置**：GPIO配置、PHY初始化、MAC配置
- ✅ **数据传输**：DMA描述符、发送接收、错误处理
- ✅ **故障排除**：常见问题诊断和解决方法

### 关键要点

1. **硬件架构**：
   - MAC负责数据链路层
   - PHY负责物理层
   - 变压器提供隔离和阻抗匹配

2. **接口选择**：
   - 嵌入式系统优先选择RMII
   - RMII只需7根信号线
   - 50MHz参考时钟

3. **变压器设计**：
   - 必须使用网络变压器
   - 提供电气隔离
   - 实现阻抗匹配

4. **PCB设计**：
   - 差分对等长等宽
   - 完整的地平面
   - 良好的EMC措施

## 实践建议

### 初学者练习

1. **基础通信**：
   - 搭建STM32以太网节点
   - 实现简单的数据收发
   - 测试链路状态

2. **PHY配置**：
   - 读写PHY寄存器
   - 配置自动协商
   - 监控链路状态

3. **性能测试**：
   - 测试传输速率
   - 测试延迟
   - 优化配置

### 进阶项目

1. **TCP/IP协议栈**：
   - 移植lwIP协议栈
   - 实现HTTP服务器
   - 实现MQTT客户端

2. **工业以太网**：
   - 实现Modbus TCP
   - 实现EtherCAT从站
   - 实现PROFINET设备

3. **网络应用**：
   - 实现网络摄像头
   - 实现数据采集器
   - 实现远程控制

## 延伸阅读

### 相关文章

- [CAN总线硬件设计](01-can-bus-hardware.html) - 学习工业总线通信
- [USB硬件接口设计](02-usb-hardware.html) - 学习高速接口设计
- [SPI硬件接口与应用](../beginner/02-spi-hardware.html) - 学习同步通信

### 协议实现

- lwIP协议栈移植
- Modbus TCP实现

### 硬件设计

- [信号完整性分析](../../02-hardware-design-fundamentals/intermediate/01-signal-integrity.html)
- [EMC设计实战](../../02-hardware-design-fundamentals/intermediate/02-emc-design.html)
- [高速PCB设计要点](../../02-hardware-design-fundamentals/intermediate/03-high-speed-pcb.html)

## 参考资料

### 数据手册

1. [LAN8720A Datasheet](https://www.microchip.com/wwwproducts/en/LAN8720A) - Microchip PHY芯片
2. [DP83848 Datasheet](https://www.ti.com/product/DP83848) - TI PHY芯片
3. [STM32F4 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00031020.pdf) - 以太网章节

### 技术标准

1. **IEEE 802.3**：以太网标准
2. **IEEE 802.3u**：Fast Ethernet（100BASE-TX）
3. **IEEE 802.3ab**：Gigabit Ethernet（1000BASE-T）

### 在线工具

1. [Ethernet Frame Calculator](https://www.wireshark.org/) - 以太网帧分析
2. [PCB Impedance Calculator](https://www.eeweb.com/tools/microstrip-impedance/) - 阻抗计算器
3. [Network Cable Tester](https://www.flukenetworks.com/) - 网线测试工具

### 开源项目

1. [lwIP](https://savannah.nongnu.org/projects/lwip/) - 轻量级TCP/IP协议栈
2. [uIP](https://github.com/adamdunkels/uip) - 微型TCP/IP协议栈
3. [FreeRTOS+TCP](https://www.freertos.org/FreeRTOS-Plus/FreeRTOS_Plus_TCP/) - FreeRTOS TCP/IP栈

## 常见应用场景

### 1. 工业控制

**应用**：
- PLC通信
- 工业网关
- 数据采集

**配置**：100BASE-TX，Modbus TCP

### 2. 物联网设备

**应用**：
- 智能家居
- 环境监测
- 远程控制

**配置**：10/100BASE-TX，MQTT

### 3. 嵌入式服务器

**应用**：
- Web服务器
- 文件服务器
- 视频流服务器

**配置**：100BASE-TX，HTTP/FTP

### 4. 网络存储

**应用**：
- NAS设备
- 网络硬盘
- 数据备份

**配置**：1000BASE-T，NFS/SMB

### 5. 医疗设备

**应用**：
- 医疗监护
- 设备互联
- 数据传输

**配置**：100BASE-TX，HL7协议

## 附录

### A. PHY芯片对比表

| 型号 | 厂商 | 接口 | 速度 | 封装 | 特点 |
|------|------|------|------|------|------|
| LAN8720A | Microchip | RMII | 10/100 | QFN-24 | 成本低 |
| DP83848 | TI | MII/RMII | 10/100 | LQFP-48 | 工业级 |
| RTL8201F | Realtek | MII/RMII | 10/100 | QFN-32 | 集成LED |
| KSZ8081 | Microchip | MII/RMII | 10/100 | QFN-24 | 低功耗 |
| LAN8742A | Microchip | RMII | 10/100 | QFN-24 | 改进版 |

### B. 网络变压器对比表

| 型号 | 类型 | 隔离电压 | 插入损耗 | 应用 |
|------|------|---------|---------|------|
| HR911105A | 集成RJ45 | 1500V | <1dB | 通用 |
| J0011D21BNL | 集成RJ45 | 1500V | <1dB | 工业 |
| 7499111121 | 集成RJ45 | 1500V | <1dB | 汽车 |
| H1102NL | 分立变压器 | 1500V | <0.8dB | 高性能 |

### C. 故障排查检查清单

**硬件检查**：
- [ ] 网线连接正常
- [ ] RJ45接口无损坏
- [ ] 变压器安装正确
- [ ] 终端电阻值正确（49.9Ω）
- [ ] 电源电压正常（3.3V）
- [ ] 时钟信号正常（50MHz）

**软件检查**：
- [ ] PHY地址配置正确
- [ ] GPIO复用功能配置正确
- [ ] MAC地址配置正确
- [ ] DMA描述符初始化正确
- [ ] 中断使能
- [ ] 协议栈配置正确

**测试方法**：
- [ ] PHY ID读取正常
- [ ] 链路状态正常
- [ ] 环回测试通过
- [ ] 数据收发正常
- [ ] 性能测试达标

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 分享你的项目经验，与其他学习者交流
- 发现文档错误？请提交Issue帮助我们改进

**版权声明**：本文采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。
