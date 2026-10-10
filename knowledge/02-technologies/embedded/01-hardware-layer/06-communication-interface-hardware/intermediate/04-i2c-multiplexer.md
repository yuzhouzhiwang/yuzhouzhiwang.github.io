---
title: "I2C多路复用器应用"
description: "深入理解I2C多路复用器芯片（TCA9548A）的工作原理、地址冲突解决方案、总线管理策略，掌握多设备I2C系统的设计与实现"
slug: "i2c-multiplexer-application"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - I2C多路复用器
  - TCA9548A
  - 地址冲突
  - 总线管理
  - 多设备通信
  - 通道选择
prerequisites:
  - "I2C硬件接口基础"
  - "数字电路基础"
  - "GPIO操作"
related_contents:
  - "i2c-hardware-interface"
  - "smbus-protocol"
  - "uart-usart-hardware-interface"

# 学习信息
estimated_time: 90
difficulty_score: 5

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
  - I2C多路复用器
  - TCA9548A应用
  - I2C地址冲突
  - 多路复用器控制
  - I2C总线扩展
  - 设备枚举
cover_image: ""
---

# I2C多路复用器应用

## 概述

I2C多路复用器是解决I2C总线地址冲突和扩展总线容量的关键器件。在复杂的嵌入式系统中，经常会遇到多个相同地址的I2C设备需要连接到同一个主机的情况，或者需要连接超过总线负载能力的设备数量。I2C多路复用器通过将一条I2C总线扩展为多条独立的I2C通道，完美解决了这些问题。

完成本教程学习后，你将能够：

- 理解I2C多路复用器的工作原理和应用场景
- 掌握TCA9548A等常用多路复用器芯片的使用方法
- 学会解决I2C地址冲突问题
- 实现多通道I2C设备的管理和控制
- 掌握设备枚举和自动发现技术
- 理解总线负载和信号完整性问题
- 实现可靠的错误处理和恢复机制

## 背景知识

### I2C地址冲突问题

**什么是地址冲突**：

I2C协议使用7位地址（或10位地址）来标识总线上的设备。当两个或多个设备具有相同的I2C地址时，就会发生地址冲突，导致无法正常通信。

**常见冲突场景**：

1. **相同型号的多个传感器**：
   - 例如：需要连接4个MPU6050陀螺仪
   - MPU6050只有两个可选地址：0x68和0x69
   - 最多只能连接2个，无法满足4个的需求

2. **固定地址的设备**：
   - 某些设备地址完全固定，无法配置
   - 例如：DS1307 RTC固定地址0x68
   - 如果需要多个这样的设备，必然冲突

3. **总线负载限制**：
   - I2C总线有电容负载限制（标准模式400pF）
   - 每个设备增加约10pF电容
   - 连接过多设备会超出负载能力

4. **长距离布线**：
   - 需要在不同位置连接多组设备
   - 长距离走线增加电容和电阻
   - 影响信号质量和通信可靠性

### 解决方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 硬件地址配置 | 简单、成本低 | 地址数量有限 | 设备少、有可配置地址 |
| 软件I2C（BitBang） | 灵活、无限扩展 | 占用GPIO、软件复杂 | GPIO充足、速度要求不高 |
| I2C多路复用器 | 硬件实现、可靠 | 增加成本和复杂度 | 专业应用、大量设备 |
| I2C缓冲器/中继器 | 增强驱动能力 | 不解决地址冲突 | 长距离、大负载 |

### I2C多路复用器的优势

**1. 完美解决地址冲突**：
- 每个通道独立，可连接相同地址设备
- 支持8个通道（TCA9548A）
- 理论上可连接8个相同地址的设备

**2. 降低总线负载**：
- 每个通道独立，负载分散
- 单通道负载 = 主总线负载 / 通道数
- 提高信号质量和可靠性

**3. 灵活的总线管理**：
- 可选择性地使能/禁用通道
- 支持多通道同时使能
- 便于设备隔离和故障排查

**4. 提高系统可靠性**：
- 故障隔离：单个通道故障不影响其他通道
- 热插拔支持：可动态连接/断开设备
- 电源管理：可单独控制通道电源

**5. 简化布线**：
- 主总线到多路复用器距离短
- 各通道可就近连接设备
- 减少长距离走线

## I2C多路复用器工作原理

### 基本架构

**多路复用器结构图**：

```
主机（MCU）
    │
    ├─ SCL ────────┐
    ├─ SDA ────────┤
    │              │
    │         ┌────┴────┐
    │         │ TCA9548A│
    │         │  多路   │
    │         │  复用器 │
    │         └────┬────┘
    │              │
    ├──────────────┼─ 通道0 ─── 设备0 (0x50)
    ├──────────────┼─ 通道1 ─── 设备1 (0x50)
    ├──────────────┼─ 通道2 ─── 设备2 (0x50)
    ├──────────────┼─ 通道3 ─── 设备3 (0x50)
    ├──────────────┼─ 通道4 ─── 设备4 (0x50)
    ├──────────────┼─ 通道5 ─── 设备5 (0x50)
    ├──────────────┼─ 通道6 ─── 设备6 (0x50)
    └──────────────┴─ 通道7 ─── 设备7 (0x50)

特点：
- 8个独立I2C通道
- 每个通道可连接相同地址设备
- 通过控制寄存器选择通道
```

### 工作模式

**1. 单通道模式（最常用）**：

```
时刻1：选择通道0
主机 → 多路复用器(0x70) → 写入0x01 → 使能通道0
主机 → 通道0设备(0x50) → 读写数据

时刻2：选择通道1
主机 → 多路复用器(0x70) → 写入0x02 → 使能通道1
主机 → 通道1设备(0x50) → 读写数据

优点：
- 通道完全隔离
- 无干扰
- 最可靠

缺点：
- 需要频繁切换通道
- 效率相对较低
```

**2. 多通道同时使能模式**：

```
主机 → 多路复用器(0x70) → 写入0x0F → 使能通道0-3

此时通道0-3同时连接到主总线：
- 可以访问不同地址的设备
- 相同地址的设备会冲突
- 适用于地址不同的设备组

示例：
通道0: 温度传感器 (0x48)
通道1: 湿度传感器 (0x40)
通道2: 光照传感器 (0x23)
通道3: 压力传感器 (0x76)

可以同时使能，因为地址不同
```

**3. 级联模式**：

```
主机
  │
  └─ 多路复用器1 (0x70)
       ├─ 通道0 ─── 设备
       ├─ 通道1 ─── 设备
       ├─ 通道2 ─── 多路复用器2 (0x71)
       │              ├─ 通道0 ─── 设备
       │              ├─ 通道1 ─── 设备
       │              └─ 通道2 ─── 设备
       └─ 通道3 ─── 设备

优点：
- 可扩展到64个通道（8×8）
- 灵活的拓扑结构

缺点：
- 增加延迟
- 管理复杂度高
```

### 通道选择机制

**控制寄存器格式**：

```
TCA9548A控制寄存器（8位）：

Bit:  7    6    5    4    3    2    1    0
     CH7  CH6  CH5  CH4  CH3  CH2  CH1  CH0

每个位对应一个通道：
- 0 = 通道禁用
- 1 = 通道使能

示例：
0x01 = 0b00000001 → 使能通道0
0x02 = 0b00000010 → 使能通道1
0x04 = 0b00000100 → 使能通道2
0x08 = 0b00001000 → 使能通道3
0x0F = 0b00001111 → 使能通道0-3
0xFF = 0b11111111 → 使能所有通道
0x00 = 0b00000000 → 禁用所有通道
```

**通道切换时序**：

```
1. 写入多路复用器地址
2. 写入通道选择字节
3. 等待切换完成（通常<1μs）
4. 访问目标设备

完整时序：
START → MUX_ADDR(W) → ACK → CHANNEL_BYTE → ACK → STOP
START → DEV_ADDR(W/R) → ACK → DATA → ACK → STOP

注意：
- 通道切换后立即生效
- 无需额外延时
- 可以连续访问同一通道的多个设备
```

## TCA9548A详解

### 芯片特性

**TCA9548A主要参数**：

| 参数 | 值 | 说明 |
|------|-----|------|
| 工作电压 | 1.65V - 5.5V | 宽电压范围 |
| I2C速度 | 最高400kHz | 支持标准和快速模式 |
| 通道数量 | 8个 | 独立可控 |
| 地址范围 | 0x70 - 0x77 | 8个可选地址 |
| 通道电容 | 400pF | 每通道最大负载 |
| 上电状态 | 所有通道禁用 | 安全默认状态 |
| 封装 | TSSOP-24, QFN-24 | 小型封装 |

### 引脚定义

**TCA9548A引脚图（TSSOP-24）**：

```
        TCA9548A
     ┌──────────┐
A0  ─┤1      24├─ VCC
A1  ─┤2      23├─ SDA (主总线)
A2  ─┤3      22├─ SCL (主总线)
~RST─┤4      21├─ SD0 (通道0 SDA)
SD7 ─┤5      20├─ SC0 (通道0 SCL)
SC7 ─┤6      19├─ SD1 (通道1 SDA)
SD6 ─┤7      18├─ SC1 (通道1 SCL)
SC6 ─┤8      17├─ SD2 (通道2 SDA)
SD5 ─┤9      16├─ SC2 (通道2 SCL)
SC5 ─┤10     15├─ SD3 (通道3 SDA)
SD4 ─┤11     14├─ SC3 (通道3 SCL)
GND ─┤12     13├─ SC4 (通道4 SCL)
     └──────────┘

引脚功能：
- A0, A1, A2: 地址选择引脚
- ~RST: 复位引脚（低电平有效）
- SDA, SCL: 主I2C总线
- SD0-SD7: 通道0-7的SDA
- SC0-SC7: 通道0-7的SCL
- VCC: 电源（1.65V-5.5V）
- GND: 地
```

### 地址配置

**地址选择**：

```
A2  A1  A0  |  I2C地址
----|-------|----------
0   0   0   |  0x70
0   0   1   |  0x71
0   1   0   |  0x72
0   1   1   |  0x73
1   0   0   |  0x74
1   0   1   |  0x75
1   1   0   |  0x76
1   1   1   |  0x77

硬件连接：
- 接GND = 0
- 接VCC = 1
- 悬空 = 不确定（不推荐）

示例：
A2=GND, A1=GND, A0=VCC → 地址0x71
```

**多个多路复用器级联**：

```
主机
  │
  ├─ TCA9548A #1 (0x70) ─┬─ 通道0-7
  │                      │
  └─ TCA9548A #2 (0x71) ─┴─ 通道0-7

优点：
- 16个独立通道
- 地址不冲突
- 并行访问

注意：
- 两个多路复用器在同一主总线上
- 需要不同的地址
- 可以同时使能不同多路复用器的通道
```

### 复位功能

**硬件复位**：

```
~RST引脚功能：
- 低电平：复位，所有通道禁用
- 高电平：正常工作
- 上电时应先复位

复位时序：
~RST ────┐     ┌──────────
         └─────┘
         >100ns

复位后状态：
- 控制寄存器 = 0x00
- 所有通道禁用
- I2C接口正常
```

**软件复位**：

```c
// 通过写入0x00禁用所有通道
void TCA9548A_SoftReset(uint8_t mux_addr) {
    I2C_Start();
    I2C_SendAddress(mux_addr, I2C_WRITE);
    I2C_SendByte(0x00);  // 禁用所有通道
    I2C_Stop();
}
```

### 电气特性

**电源要求**：

```
VCC范围：1.65V - 5.5V

推荐配置：
- 3.3V系统：VCC = 3.3V
- 5V系统：VCC = 5V
- 混合系统：VCC = 较低电压

电流消耗：
- 静态电流：<5μA
- 工作电流：<50μA
- 总线电流：取决于负载
```

**电平兼容性**：

```
输入高电平（VIH）：0.7×VCC
输入低电平（VIL）：0.3×VCC

3.3V系统：
- VIH ≥ 2.31V
- VIL ≤ 0.99V

5V系统：
- VIH ≥ 3.5V
- VIL ≤ 1.5V

注意：
- TCA9548A支持电平转换
- 主总线和通道可以是不同电压
- 通过VCC设置参考电压
```

## 硬件电路设计

### 基本连接电路

**标准应用电路**：

```
MCU (3.3V)              TCA9548A              设备
                                              
3.3V ─┬─ 4.7kΩ ─┬─ SDA ──┤23                 
      └─ 4.7kΩ ─┴─ SCL ──┤22                 
                          │                   
PA11 ─────────────── SDA ─┤23                 
PA12 ─────────────── SCL ─┤22                 
                          │                   
3.3V ──────────────── VCC ┤24                 
GND ───────────────── GND ┤12                 
                          │                   
GND ──────────────────A0 ─┤1  (地址0x70)     
GND ──────────────────A1 ─┤2                  
GND ──────────────────A2 ─┤3                  
                          │                   
3.3V ─────────────── ~RST ┤4                  
                          │                   
                      SD0 ┤21 ─┬─ 4.7kΩ ─ 3.3V
                      SC0 ┤20 ─┴─ 4.7kΩ ─ 3.3V
                          │      │
                          │      └─ 设备0 (0x50)
                          │
                      SD1 ┤19 ─┬─ 4.7kΩ ─ 3.3V
                      SC1 ┤18 ─┴─ 4.7kΩ ─ 3.3V
                          │      │
                          │      └─ 设备1 (0x50)
                          │
                      ... (其他通道类似)

关键要点：
- 主总线需要上拉电阻
- 每个通道也需要上拉电阻
- 上拉电阻连接到VCC
- 所有设备共地
```

### 上拉电阻配置

**电阻值计算**：

```
主总线上拉电阻：
- 考虑所有通道的并联效果
- 通常使用较小的值（2.2kΩ - 4.7kΩ）

通道上拉电阻：
- 每个通道独立
- 根据通道设备数量选择
- 通常使用4.7kΩ - 10kΩ

示例计算：
主总线：
- 速度：400kHz
- 设备：TCA9548A + MCU
- 推荐：2.2kΩ

通道（每个通道2个设备）：
- 速度：400kHz
- 设备：2个传感器
- 推荐：4.7kΩ
```

**多种配置方案**：

**方案1：每个通道独立上拉（推荐）**：

```
优点：
- 通道完全独立
- 故障隔离好
- 灵活性高

缺点：
- 需要更多电阻
- PCB空间占用大

适用：
- 专业产品
- 高可靠性要求
```

**方案2：共享上拉电阻**：

```
主总线 ─┬─ 2.2kΩ ─ VCC
        │
     TCA9548A
        │
所有通道共享主总线上拉

优点：
- 节省元件
- 简化设计

缺点：
- 负载大
- 可靠性降低

适用：
- 原型开发
- 成本敏感应用
```

### 电平转换应用

**3.3V主机 + 5V设备**：

```
MCU (3.3V)          TCA9548A          设备 (5V)
                                      
3.3V ─┬─ 4.7kΩ ─┬─ SDA              
      └─ 4.7kΩ ─┴─ SCL              
                  │                  
3.3V ────── VCC ──┤ (参考3.3V)      
                  │                  
              SD0 ┤─┬─ 10kΩ ─ 5V    
              SC0 ┤─┴─ 10kΩ ─ 5V    
                  │    │             
                  │    └─ 5V设备    

工作原理：
- TCA9548A的VCC设置为3.3V
- 主总线电平为3.3V
- 通道上拉到5V
- TCA9548A的输出为开漏
- 5V设备可以正常工作

注意：
- 确保5V设备的输入容忍3.3V
- 或使用专用电平转换芯片
```

### PCB布线建议

**布局原则**：

```
1. 多路复用器位置：
   - 靠近主机
   - 居中放置
   - 便于走线

2. 主总线走线：
   - 短而直
   - 差分对布线
   - 远离干扰源

3. 通道走线：
   - 各通道独立
   - 避免交叉
   - 长度尽量相等

4. 去耦电容：
   - VCC引脚附近
   - 0.1μF + 10μF
   - 尽量靠近芯片
```

**推荐布局**：

```
        主机
         │
    ┌────┴────┐
    │ TCA9548A│
    └────┬────┘
         │
    ┌────┼────┬────┬────┬────┬────┬────┬────┐
    │    │    │    │    │    │    │    │    │
   CH0  CH1  CH2  CH3  CH4  CH5  CH6  CH7
    │    │    │    │    │    │    │    │
  设备  设备  设备  设备  设备  设备  设备  设备

特点：
- 对称布局
- 走线长度相近
- 便于维护
```

### ESD保护

**保护电路**：

```
外部接口保护：

SD0 ──┬─────────→ 接口
      │
      ├─ TVS ─┬─ GND
      │       │
SC0 ──┴───────┘

推荐器件：
- PESD3V3L2BT（双通道，3.3V）
- PESD5V0L2BT（双通道，5V）
- TPD2E001（双通道，通用）

放置位置：
- 外部接口处
- 尽量靠近连接器
- 每个通道独立保护
```

## 软件驱动实现

### 基础驱动函数

**TCA9548A驱动结构**：

```c
// TCA9548A驱动结构体
typedef struct {
    uint8_t address;        // 多路复用器I2C地址
    uint8_t current_channel; // 当前使能的通道
    bool initialized;       // 初始化标志
} TCA9548A_t;

// 全局实例
TCA9548A_t mux = {
    .address = 0x70,
    .current_channel = 0xFF,  // 无效值表示未选择
    .initialized = false
};
```

**初始化函数**：

```c
// 初始化TCA9548A
bool TCA9548A_Init(uint8_t address) {
    mux.address = address;
    
    // 检查设备是否存在
    if (!I2C_CheckDevice(address)) {
        printf("TCA9548A not found at 0x%02X\n", address);
        return false;
    }
    
    // 禁用所有通道
    if (!TCA9548A_DisableAllChannels()) {
        printf("Failed to disable channels\n");
        return false;
    }
    
    mux.initialized = true;
    printf("TCA9548A initialized at 0x%02X\n", address);
    return true;
}

// 检查设备是否存在
bool I2C_CheckDevice(uint8_t addr) {
    I2C_Start();
    bool ack = I2C_SendAddress(addr, I2C_WRITE);
    I2C_Stop();
    return ack;
}
```

**通道选择函数**：

```c
// 选择单个通道
bool TCA9548A_SelectChannel(uint8_t channel) {
    if (channel > 7) {
        printf("Invalid channel: %d\n", channel);
        return false;
    }
    
    if (!mux.initialized) {
        printf("TCA9548A not initialized\n");
        return false;
    }
    
    // 计算通道掩码
    uint8_t channel_mask = (1 << channel);
    
    // 写入多路复用器
    I2C_Start();
    if (!I2C_SendAddress(mux.address, I2C_WRITE)) {
        I2C_Stop();
        return false;
    }
    
    if (!I2C_SendByte(channel_mask)) {
        I2C_Stop();
        return false;
    }
    
    I2C_Stop();
    
    // 更新当前通道
    mux.current_channel = channel;
    
    return true;
}

// 选择多个通道
bool TCA9548A_SelectChannels(uint8_t channel_mask) {
    if (!mux.initialized) {
        return false;
    }
    
    I2C_Start();
    if (!I2C_SendAddress(mux.address, I2C_WRITE)) {
        I2C_Stop();
        return false;
    }
    
    if (!I2C_SendByte(channel_mask)) {
        I2C_Stop();
        return false;
    }
    
    I2C_Stop();
    return true;
}

// 禁用所有通道
bool TCA9548A_DisableAllChannels(void) {
    return TCA9548A_SelectChannels(0x00);
}
```

**读取当前状态**：

```c
// 读取当前通道状态
uint8_t TCA9548A_ReadChannels(void) {
    if (!mux.initialized) {
        return 0xFF;  // 错误值
    }
    
    uint8_t status;
    
    I2C_Start();
    if (!I2C_SendAddress(mux.address, I2C_READ)) {
        I2C_Stop();
        return 0xFF;
    }
    
    status = I2C_ReceiveByte(false);  // NACK
    I2C_Stop();
    
    return status;
}

// 检查特定通道是否使能
bool TCA9548A_IsChannelEnabled(uint8_t channel) {
    if (channel > 7) {
        return false;
    }
    
    uint8_t status = TCA9548A_ReadChannels();
    return (status & (1 << channel)) != 0;
}

// 获取使能的通道数量
uint8_t TCA9548A_GetEnabledChannelCount(void) {
    uint8_t status = TCA9548A_ReadChannels();
    uint8_t count = 0;
    
    for (int i = 0; i < 8; i++) {
        if (status & (1 << i)) {
            count++;
        }
    }
    
    return count;
}
```

### 设备访问封装

**通道设备访问函数**：

```c
// 在指定通道上读取设备
bool TCA9548A_ReadDevice(uint8_t channel, uint8_t dev_addr, 
                         uint8_t reg, uint8_t *data, uint16_t len) {
    // 选择通道
    if (!TCA9548A_SelectChannel(channel)) {
        return false;
    }
    
    // 延时确保通道切换完成（可选）
    // HAL_Delay(1);
    
    // 读取设备
    bool result = I2C_ReadRegister(dev_addr, reg, data, len);
    
    // 可选：读取后禁用通道
    // TCA9548A_DisableAllChannels();
    
    return result;
}

// 在指定通道上写入设备
bool TCA9548A_WriteDevice(uint8_t channel, uint8_t dev_addr,
                          uint8_t reg, uint8_t *data, uint16_t len) {
    // 选择通道
    if (!TCA9548A_SelectChannel(channel)) {
        return false;
    }
    
    // 写入设备
    bool result = I2C_WriteRegister(dev_addr, reg, data, len);
    
    return result;
}
```

**批量操作函数**：

```c
// 在所有通道上执行相同操作
bool TCA9548A_BroadcastWrite(uint8_t dev_addr, uint8_t reg, uint8_t data) {
    for (uint8_t ch = 0; ch < 8; ch++) {
        if (!TCA9548A_SelectChannel(ch)) {
            continue;
        }
        
        // 检查设备是否存在
        if (!I2C_CheckDevice(dev_addr)) {
            continue;
        }
        
        // 写入数据
        I2C_WriteRegister(dev_addr, reg, &data, 1);
    }
    
    return true;
}

// 从所有通道读取数据
bool TCA9548A_ReadAllChannels(uint8_t dev_addr, uint8_t reg, 
                               uint8_t data[8]) {
    for (uint8_t ch = 0; ch < 8; ch++) {
        if (!TCA9548A_SelectChannel(ch)) {
            data[ch] = 0xFF;  // 错误标记
            continue;
        }
        
        // 读取数据
        if (!I2C_ReadRegister(dev_addr, reg, &data[ch], 1)) {
            data[ch] = 0xFF;  // 错误标记
        }
    }
    
    return true;
}
```

### 设备枚举功能

**扫描所有通道的设备**：

```c
// 设备信息结构
typedef struct {
    uint8_t channel;
    uint8_t address;
    bool present;
} I2C_Device_t;

// 扫描单个通道
uint8_t TCA9548A_ScanChannel(uint8_t channel, uint8_t *devices, uint8_t max_devices) {
    uint8_t count = 0;
    
    // 选择通道
    if (!TCA9548A_SelectChannel(channel)) {
        return 0;
    }
    
    // 扫描所有可能的地址
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        // 跳过多路复用器自己的地址
        if (addr == mux.address) {
            continue;
        }
        
        // 检查设备是否存在
        if (I2C_CheckDevice(addr)) {
            if (count < max_devices) {
                devices[count++] = addr;
            }
        }
    }
    
    return count;
}
```

// 扫描所有通道
void TCA9548A_ScanAllChannels(void) {
    printf("\n=== TCA9548A Device Scan ===\n");
    printf("Multiplexer Address: 0x%02X\n\n", mux.address);
    
    for (uint8_t ch = 0; ch < 8; ch++) {
        printf("Channel %d: ", ch);
        
        uint8_t devices[16];
        uint8_t count = TCA9548A_ScanChannel(ch, devices, 16);
        
        if (count == 0) {
            printf("No devices found\n");
        } else {
            printf("Found %d device(s): ", count);
            for (uint8_t i = 0; i < count; i++) {
                printf("0x%02X ", devices[i]);
            }
            printf("\n");
        }
    }
    
    printf("\n");
}

// 构建设备映射表
typedef struct {
    uint8_t total_devices;
    I2C_Device_t devices[64];  // 最多8通道×8设备
} DeviceMap_t;

DeviceMap_t TCA9548A_BuildDeviceMap(void) {
    DeviceMap_t map;
    map.total_devices = 0;
    
    for (uint8_t ch = 0; ch < 8; ch++) {
        uint8_t devices[16];
        uint8_t count = TCA9548A_ScanChannel(ch, devices, 16);
        
        for (uint8_t i = 0; i < count; i++) {
            if (map.total_devices < 64) {
                map.devices[map.total_devices].channel = ch;
                map.devices[map.total_devices].address = devices[i];
                map.devices[map.total_devices].present = true;
                map.total_devices++;
            }
        }
    }
    
    return map;
}
```

## 实践应用示例

### 示例1：多个相同传感器

**场景**：连接8个MPU6050陀螺仪

```c
// MPU6050配置
#define MPU6050_ADDR    0x68
#define MPU6050_PWR_MGMT_1  0x6B
#define MPU6050_ACCEL_XOUT_H 0x3B

// 初始化所有MPU6050
void InitAllMPU6050(void) {
    printf("Initializing 8 MPU6050 sensors...\n");
    
    for (uint8_t ch = 0; ch < 8; ch++) {
        // 选择通道
        TCA9548A_SelectChannel(ch);
        
        // 唤醒MPU6050
        uint8_t data = 0x00;
        I2C_WriteRegister(MPU6050_ADDR, MPU6050_PWR_MGMT_1, &data, 1);
        
        HAL_Delay(100);
        
        printf("MPU6050 on channel %d initialized\n", ch);
    }
}
```

// 读取所有MPU6050数据
typedef struct {
    int16_t ax, ay, az;  // 加速度
    int16_t gx, gy, gz;  // 陀螺仪
} MPU6050_Data_t;

void ReadAllMPU6050(MPU6050_Data_t data[8]) {
    for (uint8_t ch = 0; ch < 8; ch++) {
        // 选择通道
        TCA9548A_SelectChannel(ch);
        
        // 读取14字节数据
        uint8_t buffer[14];
        I2C_ReadRegister(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H, buffer, 14);
        
        // 解析数据
        data[ch].ax = (buffer[0] << 8) | buffer[1];
        data[ch].ay = (buffer[2] << 8) | buffer[3];
        data[ch].az = (buffer[4] << 8) | buffer[5];
        // 跳过温度数据 buffer[6-7]
        data[ch].gx = (buffer[8] << 8) | buffer[9];
        data[ch].gy = (buffer[10] << 8) | buffer[11];
        data[ch].gz = (buffer[12] << 8) | buffer[13];
    }
}

// 主循环
void MPU6050_Example(void) {
    MPU6050_Data_t sensors[8];
    
    while (1) {
        ReadAllMPU6050(sensors);
        
        // 打印数据
        for (uint8_t i = 0; i < 8; i++) {
            printf("Sensor %d: AX=%d AY=%d AZ=%d GX=%d GY=%d GZ=%d\n",
                   i, sensors[i].ax, sensors[i].ay, sensors[i].az,
                   sensors[i].gx, sensors[i].gy, sensors[i].gz);
        }
        
        HAL_Delay(100);
    }
}
```

### 示例2：混合设备系统

**场景**：不同类型的传感器

```c
// 设备定义
#define TEMP_SENSOR_ADDR    0x48  // 温度传感器
#define HUMID_SENSOR_ADDR   0x40  // 湿度传感器
#define LIGHT_SENSOR_ADDR   0x23  // 光照传感器
#define PRESSURE_SENSOR_ADDR 0x76 // 压力传感器

// 传感器数据结构
typedef struct {
    float temperature;  // 温度 (°C)
    float humidity;     // 湿度 (%)
    float light;        // 光照 (lux)
    float pressure;     // 压力 (Pa)
} SensorData_t;

// 读取所有传感器
void ReadAllSensors(SensorData_t *data) {
    uint8_t buffer[4];
    
    // 通道0: 温度传感器
    TCA9548A_SelectChannel(0);
    I2C_ReadRegister(TEMP_SENSOR_ADDR, 0x00, buffer, 2);
    data->temperature = ((buffer[0] << 8) | buffer[1]) * 0.0625;
    
    // 通道1: 湿度传感器
    TCA9548A_SelectChannel(1);
    I2C_ReadRegister(HUMID_SENSOR_ADDR, 0x00, buffer, 2);
    data->humidity = ((buffer[0] << 8) | buffer[1]) / 65536.0 * 100.0;
    
    // 通道2: 光照传感器
    TCA9548A_SelectChannel(2);
    I2C_ReadRegister(LIGHT_SENSOR_ADDR, 0x00, buffer, 2);
    data->light = ((buffer[0] << 8) | buffer[1]) / 1.2;
    
    // 通道3: 压力传感器
    TCA9548A_SelectChannel(3);
    I2C_ReadRegister(PRESSURE_SENSOR_ADDR, 0xF7, buffer, 3);
    data->pressure = ((buffer[0] << 16) | (buffer[1] << 8) | buffer[2]) / 256.0;
}
```

### 示例3：EEPROM阵列

**场景**：8个EEPROM组成大容量存储

```c
// EEPROM配置
#define EEPROM_ADDR     0x50
#define EEPROM_SIZE     32768  // 32KB per EEPROM
#define TOTAL_SIZE      (EEPROM_SIZE * 8)  // 256KB total

// 写入数据到EEPROM阵列
bool WriteEEPROMArray(uint32_t address, uint8_t *data, uint16_t len) {
    while (len > 0) {
        // 计算通道和偏移
        uint8_t channel = address / EEPROM_SIZE;
        uint16_t offset = address % EEPROM_SIZE;
        
        // 计算本次写入长度
        uint16_t write_len = EEPROM_SIZE - offset;
        if (write_len > len) {
            write_len = len;
        }
        
        // 选择通道
        TCA9548A_SelectChannel(channel);
        
        // 写入EEPROM
        I2C_Start();
        I2C_SendAddress(EEPROM_ADDR, I2C_WRITE);
        I2C_SendByte(offset >> 8);    // 地址高字节
        I2C_SendByte(offset & 0xFF);  // 地址低字节
        
        for (uint16_t i = 0; i < write_len; i++) {
            I2C_SendByte(data[i]);
        }
        
        I2C_Stop();
        HAL_Delay(5);  // 等待写入完成
        
        // 更新指针
        address += write_len;
        data += write_len;
        len -= write_len;
    }
    
    return true;
}

// 从EEPROM阵列读取数据
bool ReadEEPROMArray(uint32_t address, uint8_t *buffer, uint16_t len) {
    while (len > 0) {
        // 计算通道和偏移
        uint8_t channel = address / EEPROM_SIZE;
        uint16_t offset = address % EEPROM_SIZE;
        
        // 计算本次读取长度
        uint16_t read_len = EEPROM_SIZE - offset;
        if (read_len > len) {
            read_len = len;
        }
        
        // 选择通道
        TCA9548A_SelectChannel(channel);
        
        // 写入地址
        I2C_Start();
        I2C_SendAddress(EEPROM_ADDR, I2C_WRITE);
        I2C_SendByte(offset >> 8);
        I2C_SendByte(offset & 0xFF);
        
        // 重新起始，读取数据
        I2C_Start();
        I2C_SendAddress(EEPROM_ADDR, I2C_READ);
        
        for (uint16_t i = 0; i < read_len; i++) {
            buffer[i] = I2C_ReceiveByte(i < read_len - 1);
        }
        
        I2C_Stop();
        
        // 更新指针
        address += read_len;
        buffer += read_len;
        len -= read_len;
    }
    
    return true;
}
```

### 示例4：热插拔检测

**场景**：动态检测设备连接状态

```c
// 设备状态跟踪
typedef struct {
    uint8_t channel;
    uint8_t address;
    bool connected;
    uint32_t last_seen;
} DeviceStatus_t;

DeviceStatus_t device_status[64];
uint8_t device_count = 0;

// 初始化设备状态
void InitDeviceStatus(void) {
    DeviceMap_t map = TCA9548A_BuildDeviceMap();
    
    device_count = map.total_devices;
    for (uint8_t i = 0; i < device_count; i++) {
        device_status[i].channel = map.devices[i].channel;
        device_status[i].address = map.devices[i].address;
        device_status[i].connected = true;
        device_status[i].last_seen = HAL_GetTick();
    }
}

// 检查设备连接状态
void CheckDeviceStatus(void) {
    uint32_t current_time = HAL_GetTick();
    
    for (uint8_t i = 0; i < device_count; i++) {
        // 选择通道
        TCA9548A_SelectChannel(device_status[i].channel);
        
        // 检查设备是否存在
        bool present = I2C_CheckDevice(device_status[i].address);
        
        if (present) {
            // 设备存在
            if (!device_status[i].connected) {
                // 设备重新连接
                printf("Device 0x%02X on channel %d reconnected\n",
                       device_status[i].address, device_status[i].channel);
                device_status[i].connected = true;
            }
            device_status[i].last_seen = current_time;
        } else {
            // 设备不存在
            if (device_status[i].connected) {
                // 设备断开
                printf("Device 0x%02X on channel %d disconnected\n",
                       device_status[i].address, device_status[i].channel);
                device_status[i].connected = false;
            }
        }
    }
}

// 定期检查任务
void DeviceMonitorTask(void) {
    static uint32_t last_check = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 每秒检查一次
    if (current_time - last_check >= 1000) {
        CheckDeviceStatus();
        last_check = current_time;
    }
}
```

## 高级应用技巧

### 通道缓存优化

**避免不必要的通道切换**：

```c
// 带缓存的通道选择
static uint8_t cached_channel = 0xFF;

bool TCA9548A_SelectChannelCached(uint8_t channel) {
    // 如果已经是目标通道，跳过切换
    if (cached_channel == channel) {
        return true;
    }
    
    // 切换通道
    if (TCA9548A_SelectChannel(channel)) {
        cached_channel = channel;
        return true;
    }
    
    return false;
}

// 使用示例
void OptimizedRead(void) {
    // 连续读取同一通道的多个设备
    TCA9548A_SelectChannelCached(0);
    ReadDevice1();
    ReadDevice2();
    ReadDevice3();
    // 只切换一次通道
}
```

### 并发访问管理

**多任务环境下的互斥保护**：

```c
// 使用互斥锁保护
#include "cmsis_os.h"

osMutexId_t mux_mutex;

// 初始化互斥锁
void TCA9548A_InitMutex(void) {
    mux_mutex = osMutexNew(NULL);
}

// 安全的设备访问
bool TCA9548A_SafeReadDevice(uint8_t channel, uint8_t dev_addr,
                              uint8_t reg, uint8_t *data, uint16_t len) {
    // 获取互斥锁
    if (osMutexAcquire(mux_mutex, osWaitForever) != osOK) {
        return false;
    }
    
    // 访问设备
    bool result = TCA9548A_ReadDevice(channel, dev_addr, reg, data, len);
    
    // 释放互斥锁
    osMutexRelease(mux_mutex);
    
    return result;
}
```

### 错误处理和恢复

**完善的错误处理机制**：

```c
// 错误类型
typedef enum {
    MUX_ERROR_NONE = 0,
    MUX_ERROR_NOT_FOUND,
    MUX_ERROR_CHANNEL_SWITCH,
    MUX_ERROR_DEVICE_ACCESS,
    MUX_ERROR_TIMEOUT
} MuxError_t;

// 错误计数器
typedef struct {
    uint32_t channel_switch_errors;
    uint32_t device_access_errors;
    uint32_t timeout_errors;
} ErrorCounters_t;

ErrorCounters_t error_counters = {0};

// 带重试的通道选择
bool TCA9548A_SelectChannelWithRetry(uint8_t channel, uint8_t retries) {
    for (uint8_t i = 0; i < retries; i++) {
        if (TCA9548A_SelectChannel(channel)) {
            return true;
        }
        
        error_counters.channel_switch_errors++;
        HAL_Delay(10);  // 延时后重试
    }
    
    return false;
}

// 带重试的设备访问
bool TCA9548A_ReadDeviceWithRetry(uint8_t channel, uint8_t dev_addr,
                                   uint8_t reg, uint8_t *data, 
                                   uint16_t len, uint8_t retries) {
    for (uint8_t i = 0; i < retries; i++) {
        // 选择通道
        if (!TCA9548A_SelectChannelWithRetry(channel, 3)) {
            continue;
        }
        
        // 读取设备
        if (I2C_ReadRegister(dev_addr, reg, data, len)) {
            return true;
        }
        
        error_counters.device_access_errors++;
        HAL_Delay(10);
    }
    
    return false;
}

// 错误统计报告
void PrintErrorStatistics(void) {
    printf("\n=== Error Statistics ===\n");
    printf("Channel switch errors: %lu\n", error_counters.channel_switch_errors);
    printf("Device access errors: %lu\n", error_counters.device_access_errors);
    printf("Timeout errors: %lu\n", error_counters.timeout_errors);
}
```

### 性能优化

**批量读取优化**：

```c
// 批量读取多个通道的相同寄存器
void TCA9548A_BatchRead(uint8_t dev_addr, uint8_t reg, 
                        uint8_t data[8], uint8_t channels) {
    for (uint8_t ch = 0; ch < channels; ch++) {
        TCA9548A_SelectChannelCached(ch);
        I2C_ReadRegister(dev_addr, reg, &data[ch], 1);
    }
}

// DMA优化（如果硬件支持）
void TCA9548A_DMARead(uint8_t channel, uint8_t dev_addr,
                      uint8_t reg, uint8_t *buffer, uint16_t len) {
    // 选择通道
    TCA9548A_SelectChannel(channel);
    
    // 使用DMA读取
    I2C_DMA_ReadRegister(dev_addr, reg, buffer, len);
    
    // 等待DMA完成
    while (I2C_DMA_IsBusy());
}
```

### 电源管理

**通道电源控制**：

```c
// 如果硬件支持通道电源控制
typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
} ChannelPower_t;

ChannelPower_t channel_power[8] = {
    {GPIOA, GPIO_PIN_0},
    {GPIOA, GPIO_PIN_1},
    // ... 其他通道
};

// 使能通道电源
void TCA9548A_EnableChannelPower(uint8_t channel) {
    if (channel < 8) {
        HAL_GPIO_WritePin(channel_power[channel].port,
                         channel_power[channel].pin, GPIO_PIN_SET);
        HAL_Delay(10);  // 等待电源稳定
    }
}

// 禁用通道电源
void TCA9548A_DisableChannelPower(uint8_t channel) {
    if (channel < 8) {
        HAL_GPIO_WritePin(channel_power[channel].port,
                         channel_power[channel].pin, GPIO_PIN_RESET);
    }
}

// 低功耗模式
void TCA9548A_EnterLowPower(void) {
    // 禁用所有通道
    TCA9548A_DisableAllChannels();
    
    // 关闭所有通道电源
    for (uint8_t ch = 0; ch < 8; ch++) {
        TCA9548A_DisableChannelPower(ch);
    }
}

// 从低功耗模式唤醒
void TCA9548A_WakeUp(void) {
    // 使能需要的通道电源
    for (uint8_t ch = 0; ch < 8; ch++) {
        TCA9548A_EnableChannelPower(ch);
    }
    
    HAL_Delay(10);
    
    // 重新初始化
    TCA9548A_Init(mux.address);
}
```

## 故障排查与调试

### 常见问题诊断

**问题1：多路复用器无响应**

```c
// 诊断函数
void DiagnoseMuxNotResponding(void) {
    printf("\n=== Diagnosing TCA9548A ===\n");
    
    // 1. 检查电源
    printf("1. Check VCC voltage (should be 1.65V-5.5V)\n");
    
    // 2. 检查复位引脚
    printf("2. Check ~RST pin (should be HIGH)\n");
    
    // 3. 检查I2C总线
    printf("3. Checking I2C bus...\n");
    if (!I2C_CheckBus()) {
        printf("   ERROR: I2C bus stuck!\n");
        I2C_BusRecovery();
    } else {
        printf("   OK: I2C bus is free\n");
    }
    
    // 4. 扫描I2C总线
    printf("4. Scanning I2C bus...\n");
    for (uint8_t addr = 0x70; addr <= 0x77; addr++) {
        if (I2C_CheckDevice(addr)) {
            printf("   Found device at 0x%02X\n", addr);
        }
    }
    
    // 5. 尝试读取状态
    printf("5. Reading multiplexer status...\n");
    uint8_t status = TCA9548A_ReadChannels();
    printf("   Status: 0x%02X\n", status);
}
```

**问题2：通道切换失败**

```c
// 通道切换诊断
void DiagnoseChannelSwitch(uint8_t channel) {
    printf("\n=== Diagnosing Channel %d ===\n", channel);
    
    // 1. 尝试切换通道
    printf("1. Attempting to switch to channel %d...\n", channel);
    if (TCA9548A_SelectChannel(channel)) {
        printf("   OK: Channel switched\n");
    } else {
        printf("   ERROR: Channel switch failed\n");
        return;
    }
    
    // 2. 验证通道状态
    printf("2. Verifying channel status...\n");
    uint8_t status = TCA9548A_ReadChannels();
    if (status & (1 << channel)) {
        printf("   OK: Channel %d is enabled\n", channel);
    } else {
        printf("   ERROR: Channel %d is not enabled\n", channel);
    }
    
    // 3. 检查通道上的设备
    printf("3. Scanning channel %d...\n", channel);
    uint8_t devices[16];
    uint8_t count = TCA9548A_ScanChannel(channel, devices, 16);
    printf("   Found %d device(s)\n", count);
    
    // 4. 检查上拉电阻
    printf("4. Check pull-up resistors on channel %d\n", channel);
    printf("   SDA and SCL should be HIGH when idle\n");
}
```

**问题3：设备通信错误**

```c
// 设备通信诊断
void DiagnoseDeviceCommunication(uint8_t channel, uint8_t dev_addr) {
    printf("\n=== Diagnosing Device 0x%02X on Channel %d ===\n", 
           dev_addr, channel);
    
    // 1. 选择通道
    printf("1. Selecting channel %d...\n", channel);
    if (!TCA9548A_SelectChannel(channel)) {
        printf("   ERROR: Failed to select channel\n");
        return;
    }
    
    // 2. 检查设备是否存在
    printf("2. Checking device presence...\n");
    if (!I2C_CheckDevice(dev_addr)) {
        printf("   ERROR: Device not found\n");
        printf("   - Check device power\n");
        printf("   - Check device address\n");
        printf("   - Check connections\n");
        return;
    }
    printf("   OK: Device found\n");
    
    // 3. 尝试读取设备
    printf("3. Attempting to read device...\n");
    uint8_t data;
    if (I2C_ReadRegister(dev_addr, 0x00, &data, 1)) {
        printf("   OK: Read successful, data=0x%02X\n", data);
    } else {
        printf("   ERROR: Read failed\n");
        printf("   - Check device register map\n");
        printf("   - Check I2C timing\n");
    }
    
    // 4. 测试写入
    printf("4. Attempting to write device...\n");
    uint8_t test_data = 0xAA;
    if (I2C_WriteRegister(dev_addr, 0x00, &test_data, 1)) {
        printf("   OK: Write successful\n");
    } else {
        printf("   ERROR: Write failed\n");
    }
}
```

### 调试工具函数

**详细的日志输出**：

```c
// 使能调试日志
#define MUX_DEBUG 1

#if MUX_DEBUG
#define MUX_LOG(fmt, ...) printf("[MUX] " fmt "\n", ##__VA_ARGS__)
#else
#define MUX_LOG(fmt, ...)
#endif

// 带日志的通道选择
bool TCA9548A_SelectChannelDebug(uint8_t channel) {
    MUX_LOG("Selecting channel %d", channel);
    
    if (channel > 7) {
        MUX_LOG("ERROR: Invalid channel %d", channel);
        return false;
    }
    
    uint8_t mask = (1 << channel);
    MUX_LOG("Channel mask: 0x%02X", mask);
    
    if (!TCA9548A_SelectChannels(mask)) {
        MUX_LOG("ERROR: Failed to select channel");
        return false;
    }
    
    // 验证
    uint8_t status = TCA9548A_ReadChannels();
    MUX_LOG("Current status: 0x%02X", status);
    
    if (status != mask) {
        MUX_LOG("WARNING: Status mismatch (expected 0x%02X, got 0x%02X)",
                mask, status);
    }
    
    return true;
}
```

**波形分析**：

```c
// 示波器测试点建议
void PrintOscilloscopeTestPoints(void) {
    printf("\n=== Oscilloscope Test Points ===\n");
    printf("1. Main Bus:\n");
    printf("   - CH1: Main SDA\n");
    printf("   - CH2: Main SCL\n");
    printf("   - Trigger: SCL falling edge\n");
    printf("   - Check: Address 0x70, channel select byte\n\n");
    
    printf("2. Channel 0:\n");
    printf("   - CH1: Channel 0 SDA\n");
    printf("   - CH2: Channel 0 SCL\n");
    printf("   - Trigger: SCL falling edge\n");
    printf("   - Check: Device address, data bytes\n\n");
    
    printf("3. Timing:\n");
    printf("   - Channel switch time: <1us\n");
    printf("   - SCL frequency: 100kHz or 400kHz\n");
    printf("   - SDA setup time: >100ns\n");
    printf("   - SDA hold time: >0ns\n");
}
```

### 性能测试

**吞吐量测试**：

```c
// 测试通道切换速度
void TestChannelSwitchSpeed(void) {
    uint32_t start_time, end_time;
    uint32_t iterations = 1000;
    
    printf("\n=== Channel Switch Speed Test ===\n");
    
    start_time = HAL_GetTick();
    
    for (uint32_t i = 0; i < iterations; i++) {
        TCA9548A_SelectChannel(i % 8);
    }
    
    end_time = HAL_GetTick();
    
    float time_per_switch = (float)(end_time - start_time) / iterations;
    printf("Average switch time: %.3f ms\n", time_per_switch);
    printf("Switches per second: %.0f\n", 1000.0 / time_per_switch);
}

// 测试数据吞吐量
void TestDataThroughput(void) {
    uint32_t start_time, end_time;
    uint32_t bytes_transferred = 0;
    uint8_t buffer[256];
    
    printf("\n=== Data Throughput Test ===\n");
    
    start_time = HAL_GetTick();
    
    // 测试1秒钟的数据传输
    while (HAL_GetTick() - start_time < 1000) {
        for (uint8_t ch = 0; ch < 8; ch++) {
            TCA9548A_SelectChannel(ch);
            I2C_ReadRegister(0x50, 0x00, buffer, 32);
            bytes_transferred += 32;
        }
    }
    
    end_time = HAL_GetTick();
    
    float throughput = (float)bytes_transferred / (end_time - start_time) * 1000;
    printf("Throughput: %.2f bytes/sec\n", throughput);
    printf("Throughput: %.2f kbps\n", throughput * 8 / 1000);
}
```

## 其他多路复用器芯片

### PCA9546A（4通道）

**特性对比**：

| 特性 | TCA9548A | PCA9546A |
|------|----------|----------|
| 通道数 | 8 | 4 |
| 地址范围 | 0x70-0x77 | 0x70-0x77 |
| 中断功能 | 无 | 有 |
| 复位功能 | 有 | 有 |
| 封装 | TSSOP-24 | TSSOP-16 |

**中断功能**：

```c
// PCA9546A支持中断聚合
// 每个通道的中断信号聚合到主中断引脚

// 读取中断状态
uint8_t PCA9546A_ReadInterruptStatus(void) {
    uint8_t status;
    
    I2C_Start();
    I2C_SendAddress(0x70, I2C_READ);
    status = I2C_ReceiveByte(false);
    I2C_Stop();
    
    // 高4位是中断状态
    return (status >> 4) & 0x0F;
}
```

### PCA9548A（8通道，带中断）

**与TCA9548A的区别**：

```
PCA9548A = TCA9548A + 中断功能

额外引脚：
- INT0-INT7: 各通道中断输入
- INT: 聚合中断输出

应用场景：
- 需要中断响应的传感器
- 事件驱动的系统
- 降低CPU轮询负担
```

**中断处理示例**：

```c
// 中断服务函数
void MUX_INT_Handler(void) {
    // 读取中断状态
    uint8_t int_status = PCA9548A_ReadInterruptStatus();
    
    // 处理各通道中断
    for (uint8_t ch = 0; ch < 8; ch++) {
        if (int_status & (1 << ch)) {
            // 选择通道
            PCA9548A_SelectChannel(ch);
            
            // 处理该通道的中断
            HandleChannelInterrupt(ch);
        }
    }
}
```

### TCA9545A（4通道，可配置）

**特殊功能**：

```
- 4个独立通道
- 每个通道可配置为上游或下游
- 支持双向通信
- 适用于复杂拓扑

应用：
- 多主机系统
- 双向通信
- 复杂总线结构
```

## 最佳实践

### 设计建议

**1. 通道分配策略**：

```
原则：
- 相同类型设备分配到不同通道
- 高速设备和低速设备分开
- 关键设备使用独立通道
- 预留通道用于扩展

示例分配：
通道0: 温度传感器（关键）
通道1: 湿度传感器（关键）
通道2: 光照传感器
通道3: 压力传感器
通道4: EEPROM（低速）
通道5: RTC（低速）
通道6: 扩展接口
通道7: 调试/测试
```

**2. 上拉电阻选择**：

```
主总线：
- 2.2kΩ（400kHz，短距离）
- 4.7kΩ（100kHz，标准）

通道：
- 4.7kΩ（1-2个设备）
- 2.2kΩ（3-5个设备）
- 1kΩ（6+个设备，不推荐）

注意：
- 避免过小（功耗高）
- 避免过大（速度慢）
- 考虑总线电容
```

**3. 错误处理策略**：

```c
// 分层错误处理
typedef enum {
    ERROR_LEVEL_INFO,     // 信息
    ERROR_LEVEL_WARNING,  // 警告
    ERROR_LEVEL_ERROR,    // 错误
    ERROR_LEVEL_CRITICAL  // 严重错误
} ErrorLevel_t;

void HandleMuxError(ErrorLevel_t level, const char *message) {
    switch (level) {
        case ERROR_LEVEL_INFO:
            // 记录日志
            LogInfo(message);
            break;
            
        case ERROR_LEVEL_WARNING:
            // 记录警告，继续运行
            LogWarning(message);
            break;
            
        case ERROR_LEVEL_ERROR:
            // 尝试恢复
            LogError(message);
            AttemptRecovery();
            break;
            
        case ERROR_LEVEL_CRITICAL:
            // 系统复位
            LogCritical(message);
            SystemReset();
            break;
    }
}
```

### 代码组织

**模块化设计**：

```c
// tca9548a.h - 头文件
#ifndef TCA9548A_H
#define TCA9548A_H

#include <stdint.h>
#include <stdbool.h>

// 配置
#define TCA9548A_MAX_CHANNELS  8
#define TCA9548A_DEFAULT_ADDR  0x70

// 初始化
bool TCA9548A_Init(uint8_t address);
void TCA9548A_DeInit(void);

// 通道控制
bool TCA9548A_SelectChannel(uint8_t channel);
bool TCA9548A_SelectChannels(uint8_t mask);
bool TCA9548A_DisableAllChannels(void);

// 状态查询
uint8_t TCA9548A_ReadChannels(void);
bool TCA9548A_IsChannelEnabled(uint8_t channel);

// 设备访问
bool TCA9548A_ReadDevice(uint8_t channel, uint8_t dev_addr,
                         uint8_t reg, uint8_t *data, uint16_t len);
bool TCA9548A_WriteDevice(uint8_t channel, uint8_t dev_addr,
                          uint8_t reg, uint8_t *data, uint16_t len);

// 设备枚举
uint8_t TCA9548A_ScanChannel(uint8_t channel, uint8_t *devices, 
                              uint8_t max_devices);
void TCA9548A_ScanAllChannels(void);

#endif // TCA9548A_H
```

**配置文件**：

```c
// tca9548a_config.h - 配置文件
#ifndef TCA9548A_CONFIG_H
#define TCA9548A_CONFIG_H

// 多路复用器地址
#define MUX_ADDRESS         0x70

// 使能的通道
#define MUX_CHANNEL_0_EN    1
#define MUX_CHANNEL_1_EN    1
#define MUX_CHANNEL_2_EN    1
#define MUX_CHANNEL_3_EN    1
#define MUX_CHANNEL_4_EN    0
#define MUX_CHANNEL_5_EN    0
#define MUX_CHANNEL_6_EN    0
#define MUX_CHANNEL_7_EN    0

// 通道描述
#define MUX_CH0_DESC        "Temperature Sensor"
#define MUX_CH1_DESC        "Humidity Sensor"
#define MUX_CH2_DESC        "Light Sensor"
#define MUX_CH3_DESC        "Pressure Sensor"

// 调试选项
#define MUX_DEBUG_ENABLE    1
#define MUX_ERROR_RETRY     3

// 性能选项
#define MUX_CACHE_CHANNEL   1
#define MUX_USE_MUTEX       1

#endif // TCA9548A_CONFIG_H
```

### 文档和注释

**完善的文档**：

```c
/**
 * @brief 选择I2C多路复用器的通道
 * 
 * 此函数通过向TCA9548A写入通道掩码来选择一个或多个I2C通道。
 * 选择通道后，主I2C总线将连接到选定的通道，可以访问该通道上的设备。
 * 
 * @param channel 要选择的通道号（0-7）
 * 
 * @return true  通道选择成功
 * @return false 通道选择失败（无效通道号或I2C通信错误）
 * 
 * @note 此函数会禁用其他所有通道
 * @note 通道切换时间小于1微秒
 * @note 如果已经选择了目标通道，函数会立即返回（使用缓存）
 * 
 * @warning 在多任务环境中使用时，需要外部互斥保护
 * 
 * @example
 * // 选择通道0
 * if (TCA9548A_SelectChannel(0)) {
 *     // 现在可以访问通道0上的设备
 *     ReadSensor(0x48);
 * }
 */
bool TCA9548A_SelectChannel(uint8_t channel);
```

## 实际项目案例

### 案例1：环境监测站

**需求**：
- 8个位置的温湿度监测
- 每个位置：温度传感器 + 湿度传感器
- 所有传感器地址相同

**解决方案**：

```c
// 传感器配置
#define TEMP_ADDR   0x48
#define HUMID_ADDR  0x40

typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
    bool valid;
} LocationData_t;

LocationData_t locations[8];

// 读取所有位置数据
void ReadAllLocations(void) {
    for (uint8_t loc = 0; loc < 8; loc++) {
        // 选择通道
        if (!TCA9548A_SelectChannel(loc)) {
            locations[loc].valid = false;
            continue;
        }
        
        // 读取温度
        uint8_t temp_data[2];
        if (I2C_ReadRegister(TEMP_ADDR, 0x00, temp_data, 2)) {
            int16_t raw = (temp_data[0] << 8) | temp_data[1];
            locations[loc].temperature = raw * 0.0625;
        }
        
        // 读取湿度
        uint8_t humid_data[2];
        if (I2C_ReadRegister(HUMID_ADDR, 0x00, humid_data, 2)) {
            uint16_t raw = (humid_data[0] << 8) | humid_data[1];
            locations[loc].humidity = raw / 65536.0 * 100.0;
        }
        
        locations[loc].timestamp = HAL_GetTick();
        locations[loc].valid = true;
    }
}

// 显示数据
void DisplayLocationData(void) {
    printf("\n=== Environmental Monitoring ===\n");
    for (uint8_t i = 0; i < 8; i++) {
        if (locations[i].valid) {
            printf("Location %d: %.2f°C, %.1f%% RH\n",
                   i, locations[i].temperature, locations[i].humidity);
        } else {
            printf("Location %d: ERROR\n", i);
        }
    }
}
```

### 案例2：机器人多传感器系统

**需求**：
- 8个MPU6050陀螺仪（机械臂关节）
- 实时读取姿态数据
- 高刷新率（100Hz）

**解决方案**：

```c
// MPU6050数据结构
typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t gyro_x, gyro_y, gyro_z;
    int16_t temperature;
} MPU6050_RawData_t;

typedef struct {
    float roll, pitch, yaw;
    uint32_t timestamp;
} JointAngle_t;

JointAngle_t joints[8];

// 快速读取所有关节数据
void ReadAllJoints(void) {
    uint32_t start_time = HAL_GetTick();
    
    for (uint8_t joint = 0; joint < 8; joint++) {
        // 选择通道（使用缓存优化）
        TCA9548A_SelectChannelCached(joint);
        
        // 读取14字节原始数据
        uint8_t buffer[14];
        I2C_ReadRegister(MPU6050_ADDR, 0x3B, buffer, 14);
        
        // 解析数据
        MPU6050_RawData_t raw;
        raw.accel_x = (buffer[0] << 8) | buffer[1];
        raw.accel_y = (buffer[2] << 8) | buffer[3];
        raw.accel_z = (buffer[4] << 8) | buffer[5];
        raw.temperature = (buffer[6] << 8) | buffer[7];
        raw.gyro_x = (buffer[8] << 8) | buffer[9];
        raw.gyro_y = (buffer[10] << 8) | buffer[11];
        raw.gyro_z = (buffer[12] << 8) | buffer[13];
        
        // 计算姿态角
        CalculateAngles(&raw, &joints[joint]);
        joints[joint].timestamp = HAL_GetTick();
    }
    
    uint32_t elapsed = HAL_GetTick() - start_time;
    printf("Read all joints in %lu ms\n", elapsed);
}

// 姿态角计算（简化版）
void CalculateAngles(MPU6050_RawData_t *raw, JointAngle_t *angle) {
    // 加速度计数据转换为角度
    float ax = raw->accel_x / 16384.0;
    float ay = raw->accel_y / 16384.0;
    float az = raw->accel_z / 16384.0;
    
    angle->roll = atan2(ay, az) * 180.0 / M_PI;
    angle->pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 180.0 / M_PI;
    
    // 陀螺仪积分（需要互补滤波或卡尔曼滤波）
    // 这里简化处理
}

// 实时任务（100Hz）
void JointMonitorTask(void) {
    static uint32_t last_update = 0;
    uint32_t current_time = HAL_GetTick();
    
    if (current_time - last_update >= 10) {  // 10ms = 100Hz
        ReadAllJoints();
        last_update = current_time;
    }
}
```

### 案例3：数据记录系统

**需求**：
- 8个EEPROM组成256KB存储
- 循环记录传感器数据
- 掉电保护

**解决方案**：

```c
// 数据记录配置
#define RECORD_SIZE     64      // 每条记录64字节
#define RECORDS_PER_EEPROM  512 // 每个EEPROM 512条记录
#define TOTAL_RECORDS   (RECORDS_PER_EEPROM * 8)

// 记录结构
typedef struct {
    uint32_t timestamp;
    float temperature;
    float humidity;
    float pressure;
    uint16_t light;
    uint8_t status;
    uint8_t checksum;
    uint8_t reserved[48];
} DataRecord_t;

// 当前写入位置
uint32_t current_record = 0;

// 写入记录
bool WriteRecord(DataRecord_t *record) {
    // 计算校验和
    record->checksum = CalculateChecksum((uint8_t*)record, 
                                         sizeof(DataRecord_t) - 1);
    
    // 计算EEPROM通道和地址
    uint8_t channel = current_record / RECORDS_PER_EEPROM;
    uint16_t addr = (current_record % RECORDS_PER_EEPROM) * RECORD_SIZE;
    
    // 选择通道
    if (!TCA9548A_SelectChannel(channel)) {
        return false;
    }
    
    // 写入EEPROM
    bool result = WriteEEPROM(EEPROM_ADDR, addr, 
                              (uint8_t*)record, sizeof(DataRecord_t));
    
    if (result) {
        // 更新写入位置（循环）
        current_record = (current_record + 1) % TOTAL_RECORDS;
    }
    
    return result;
}

// 读取记录
bool ReadRecord(uint32_t record_num, DataRecord_t *record) {
    if (record_num >= TOTAL_RECORDS) {
        return false;
    }
    
    // 计算EEPROM通道和地址
    uint8_t channel = record_num / RECORDS_PER_EEPROM;
    uint16_t addr = (record_num % RECORDS_PER_EEPROM) * RECORD_SIZE;
    
    // 选择通道
    if (!TCA9548A_SelectChannel(channel)) {
        return false;
    }
    
    // 读取EEPROM
    if (!ReadEEPROM(EEPROM_ADDR, addr, 
                    (uint8_t*)record, sizeof(DataRecord_t))) {
        return false;
    }
    
    // 验证校验和
    uint8_t checksum = CalculateChecksum((uint8_t*)record, 
                                         sizeof(DataRecord_t) - 1);
    return (checksum == record->checksum);
}

// 导出所有数据
void ExportAllRecords(void) {
    printf("\n=== Exporting All Records ===\n");
    
    DataRecord_t record;
    uint32_t valid_records = 0;
    
    for (uint32_t i = 0; i < TOTAL_RECORDS; i++) {
        if (ReadRecord(i, &record)) {
            printf("%lu,%lu,%.2f,%.1f,%.1f,%u\n",
                   i, record.timestamp, record.temperature,
                   record.humidity, record.pressure, record.light);
            valid_records++;
        }
    }
    
    printf("Total valid records: %lu\n", valid_records);
}
```

## 总结

通过本文学习，你已经掌握了：

- ✅ **I2C多路复用器原理**：工作机制、通道选择、地址配置
- ✅ **TCA9548A应用**：硬件连接、软件驱动、设备访问
- ✅ **地址冲突解决**：多路复用器方案、设备枚举、通道管理
- ✅ **高级功能**：错误处理、性能优化、电源管理
- ✅ **实际应用**：多传感器系统、数据记录、环境监测
- ✅ **故障排查**：诊断方法、调试工具、问题解决

### 关键要点

1. **多路复用器优势**：
   - 完美解决地址冲突
   - 降低总线负载
   - 提高系统可靠性
   - 灵活的总线管理

2. **硬件设计要点**：
   - 主总线和通道都需要上拉电阻
   - 合理选择电阻值（2.2kΩ-10kΩ）
   - 注意电平兼容性
   - 添加ESD保护

3. **软件实现要点**：
   - 模块化驱动设计
   - 通道缓存优化
   - 完善的错误处理
   - 互斥保护（多任务）

4. **性能优化**：
   - 减少不必要的通道切换
   - 批量操作
   - 使用DMA（如果支持）
   - 合理的任务调度

## 实践建议

### 初学者练习

1. **基础实验**：
   - 连接TCA9548A和2个相同地址的设备
   - 实现通道选择和设备访问
   - 测试设备枚举功能

2. **进阶实验**：
   - 连接8个相同传感器
   - 实现数据采集和显示
   - 添加错误处理

3. **综合项目**：
   - 设计多传感器监测系统
   - 实现数据记录功能
   - 添加远程通信

### 进阶项目

1. **智能家居系统**：
   - 多房间环境监测
   - 设备自动发现
   - 数据可视化

2. **工业监控系统**：
   - 多点温度监测
   - 实时数据采集
   - 报警和记录

3. **机器人系统**：
   - 多关节姿态监测
   - 实时控制
   - 数据融合

## 延伸阅读

### 相关文章

- [I2C硬件接口实战](../beginner/03-i2c-hardware.html) - I2C基础知识
- [SMBus协议详解](05-smbus-protocol.html) - SMBus协议应用
- [PMBus电源管理](../advanced/01-pmbus-power-management.html) - 电源管理总线

### 相关协议

- I2C规范（NXP UM10204）
- SMBus规范
- PMBus规范

### 硬件设计

- 信号完整性分析
- EMC设计实战
- PCB布线规范

## 参考资料

### 数据手册

1. [TCA9548A Datasheet](https://www.ti.com/lit/ds/symlink/tca9548a.pdf) - TI 8通道多路复用器
2. [PCA9548A Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9548A.pdf) - NXP 8通道多路复用器
3. [PCA9546A Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9546A.pdf) - NXP 4通道多路复用器

### 应用笔记

1. **AN-10441**: Level shifting techniques in I2C-bus design
2. **AN-11084**: Using the PCA9548A I2C multiplexer
3. **SLVA704**: TCA9548A Design Guide

### 在线资源

1. [I2C Bus Specification](https://www.nxp.com/docs/en/user-guide/UM10204.pdf) - I2C总线规范
2. [I2C Tools](https://i2c.wiki.kernel.org/index.php/I2C_Tools) - Linux I2C工具
3. [Adafruit TCA9548A Library](https://github.com/adafruit/Adafruit_TCA9548A) - Arduino库

### 开发工具

1. **Logic Analyzer**: 分析I2C通信
2. **Oscilloscope**: 测量信号质量
3. **I2C Scanner**: 设备扫描工具
4. **Bus Pirate**: 通用总线工具

## 常见应用场景

### 1. 传感器网络

**应用**：
- 环境监测
- 工业控制
- 智能农业

**配置**：多个相同传感器，独立通道

### 2. 显示系统

**应用**：
- 多屏显示
- LED矩阵
- OLED阵列

**配置**：多个显示控制器，相同地址

### 3. 存储扩展

**应用**：
- 大容量EEPROM
- 配置存储
- 数据记录

**配置**：多个EEPROM，组成阵列

### 4. 电源管理

**应用**：
- 多路电源监控
- 电池管理
- PMBus系统

**配置**：多个电源管理芯片

### 5. 测试系统

**应用**：
- 自动化测试
- 设备编程
- 质量检测

**配置**：多个测试点，独立控制

## 附录

### A. TCA9548A寄存器映射

| 寄存器 | 地址 | 位 | 功能 |
|--------|------|-----|------|
| Control | 0x00 | 7:0 | 通道使能控制 |

**控制寄存器位定义**：

```
Bit 7: 通道7使能
Bit 6: 通道6使能
Bit 5: 通道5使能
Bit 4: 通道4使能
Bit 3: 通道3使能
Bit 2: 通道2使能
Bit 1: 通道1使能
Bit 0: 通道0使能

0 = 通道禁用
1 = 通道使能
```

### B. 常用I2C设备地址表

| 设备类型 | 地址范围 | 可配置位 |
|---------|---------|---------|
| EEPROM (24C) | 0x50-0x57 | A2,A1,A0 |
| RTC (DS1307) | 0x68 | 固定 |
| RTC (PCF8563) | 0x51 | 固定 |
| 温度 (LM75) | 0x48-0x4F | A2,A1,A0 |
| 湿度 (SHT3x) | 0x44-0x45 | ADDR |
| 陀螺仪 (MPU6050) | 0x68-0x69 | AD0 |
| 加速度 (ADXL345) | 0x53,0x1D | SDO |
| 磁力计 (HMC5883L) | 0x1E | 固定 |
| 气压 (BMP280) | 0x76-0x77 | SDO |
| 光照 (BH1750) | 0x23,0x5C | ADDR |

### C. 故障排查检查清单

**硬件检查**：
- [ ] VCC电压正常（1.65V-5.5V）
- [ ] ~RST引脚为高电平
- [ ] 主总线有上拉电阻
- [ ] 各通道有上拉电阻
- [ ] 所有设备共地
- [ ] 地址配置正确（A0,A1,A2）

**软件检查**：
- [ ] I2C初始化正确
- [ ] 多路复用器地址正确
- [ ] 通道选择成功
- [ ] 设备地址正确
- [ ] 时序配置正确

**通信检查**：
- [ ] 主总线通信正常
- [ ] 通道切换成功
- [ ] 设备响应ACK
- [ ] 数据读写正确
- [ ] 无总线冲突

### D. 性能参数

**TCA9548A性能指标**：

| 参数 | 最小值 | 典型值 | 最大值 | 单位 |
|------|--------|--------|--------|------|
| 工作电压 | 1.65 | - | 5.5 | V |
| 工作电流 | - | 10 | 50 | μA |
| I2C频率 | - | - | 400 | kHz |
| 通道电容 | - | - | 400 | pF |
| 通道电阻 | - | 5 | - | Ω |
| 切换时间 | - | - | 1 | μs |
| 工作温度 | -40 | - | 85 | °C |

---

**版权声明**：本文档为嵌入式知识平台原创内容，遵循CC BY-SA 4.0协议。

**更新日志**：
- 2024-01-15: 初始版本发布
