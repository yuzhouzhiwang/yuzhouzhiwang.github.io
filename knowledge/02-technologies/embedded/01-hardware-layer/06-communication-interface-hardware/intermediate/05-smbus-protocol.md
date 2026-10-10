---
title: "SMBus协议详解"
description: "深入理解SMBus（System Management Bus）协议规范、与I2C的区别、包错误检查（PEC）机制，掌握SMBus命令协议、超时处理和错误恢复技术"
slug: "smbus-protocol-detailed"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - SMBus协议
  - 系统管理总线
  - PEC校验
  - 超时处理
  - 电源管理
  - I2C扩展
prerequisites:
  - "I2C硬件接口基础"
  - "数字通信协议"
  - "CRC校验算法"
related_contents:
  - "i2c-hardware-interface"
  - "i2c-multiplexer-application"
  - "pmbus-power-management"

# 学习信息
estimated_time: 120
difficulty_score: 6

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
  - SMBus协议规范
  - PEC包错误检查
  - SMBus超时机制
  - 系统管理总线
  - SMBus命令集
  - 电池管理
cover_image: ""
---

# SMBus协议详解

## 概述

SMBus（System Management Bus，系统管理总线）是一种基于I2C的双线通信协议，专门为系统管理和电源管理应用而设计。SMBus由Intel在1995年提出，现已成为PC和嵌入式系统中电源管理、电池管理、温度监控等应用的标准协议。

SMBus在I2C的基础上增加了更严格的电气规范、超时机制、包错误检查（PEC）等特性，使其更适合关键系统管理任务。

完成本教程学习后，你将能够：

- 理解SMBus协议规范和设计理念
- 掌握SMBus与I2C的关键区别
- 实现SMBus命令协议（Quick Command、Send/Receive Byte、Read/Write Word等）
- 掌握PEC（Packet Error Checking）的计算和验证
- 实现SMBus超时检测和错误恢复机制
- 开发SMBus主机和从机设备驱动
- 应用SMBus于电池管理、温度监控等实际场景

## 背景知识

### SMBus的诞生背景

**为什么需要SMBus**：

1. **系统管理需求**：
   - PC系统需要监控电源、温度、风扇等
   - 需要可靠的低速通信协议
   - I2C虽然简单，但缺乏系统管理所需的特性

2. **可靠性要求**：
   - 系统管理涉及关键功能（电源、温度）
   - 需要错误检测机制
   - 需要超时保护避免总线挂死

3. **互操作性**：
   - 不同厂商的设备需要互通
   - 需要标准化的命令集
   - 需要明确的电气规范

4. **成本考虑**：
   - 基于成熟的I2C技术
   - 无需额外硬件
   - 易于实现和部署

### SMBus应用领域

**典型应用场景**：

| 应用领域 | 具体应用 | 典型设备 |
|---------|---------|---------|
| 电源管理 | 电源监控、电压调节 | PMBus电源、DC-DC转换器 |
| 电池管理 | 智能电池、充电控制 | Smart Battery、充电器 |
| 温度监控 | 系统温度、风扇控制 | 温度传感器、风扇控制器 |
| 内存管理 | SPD读取、内存配置 | DIMM模块、内存控制器 |
| 显示管理 | DDC/CI通信 | 显示器、显卡 |
| 系统监控 | 硬件监控、故障检测 | 监控芯片、BMC |

**SMBus在PC系统中的应用**：

```
CPU
 │
 ├─ 内存控制器 ──→ DIMM (SPD via SMBus)
 │
 ├─ 南桥芯片
 │   │
 │   ├─ SMBus控制器
 │   │   │
 │   │   ├─ 温度传感器 (0x48)
 │   │   ├─ 风扇控制器 (0x2E)
 │   │   ├─ 电源管理IC (0x10)
 │   │   ├─ 智能电池 (0x0B)
 │   │   └─ EEPROM (0x50)
 │   │
 │   └─ 其他外设
 │
 └─ 显卡 ──→ 显示器 (DDC/CI via SMBus)

特点：
- 所有系统管理设备通过SMBus连接
- 操作系统可以监控和控制硬件
- 支持热插拔和动态配置
```

### SMBus版本演进

**SMBus规范版本**：

1. **SMBus 1.0 (1995)**：
   - 初始版本
   - 定义基本协议和命令
   - 时钟频率10-100kHz

2. **SMBus 1.1 (1998)**：
   - 增加PEC支持
   - 改进超时规范
   - 增加ARP（Address Resolution Protocol）

3. **SMBus 2.0 (2000)**：
   - 支持更高速度（最高100kHz）
   - 改进电气规范
   - 增加新命令

4. **SMBus 3.0 (2014)**：
   - 支持更高速度（最高1MHz）
   - 增加快速模式+
   - 改进PEC机制
   - 向后兼容旧版本

## SMBus与I2C的区别

### 协议层面的区别

**核心差异对比**：

| 特性 | I2C | SMBus | 说明 |
|------|-----|-------|------|
| 时钟频率 | 100kHz/400kHz/3.4MHz | 10-100kHz (2.0), 最高1MHz (3.0) | SMBus更保守 |
| 超时机制 | 无 | 必须（25-35ms） | SMBus强制超时 |
| 最小时钟频率 | 无限制 | 10kHz | 防止时钟拉伸过长 |
| PEC支持 | 无 | 可选 | SMBus增加错误检测 |
| 逻辑电平 | 0.3VDD/0.7VDD | 固定阈值 | SMBus更严格 |
| 上升时间 | <1000ns | <1000ns | 相同 |
| 下降时间 | <300ns | <300ns | 相同 |
| 地址范围 | 0x00-0x7F | 0x08-0x77 | SMBus保留部分地址 |
| 时钟拉伸 | 允许 | 有限制（25ms） | SMBus限制拉伸时间 |

### 电气特性区别

**电压电平规范**：

```
I2C电平（相对于VDD）：
- VIL (输入低电平): < 0.3 × VDD
- VIH (输入高电平): > 0.7 × VDD
- VOL (输出低电平): < 0.4V @ 3mA

SMBus电平（固定阈值）：
- VIL (输入低电平): < 0.8V
- VIH (输入高电平): > 2.1V
- VOL (输出低电平): < 0.4V @ 4mA

关键区别：
1. SMBus使用固定电压阈值，不依赖VDD
2. SMBus输出驱动能力更强（4mA vs 3mA）
3. SMBus更适合3.3V和5V混合系统
```

**上拉电阻要求**：

```
I2C上拉电阻：
- 范围：1kΩ - 10kΩ
- 根据总线电容和速度计算
- 灵活性高

SMBus上拉电阻：
- 推荐：10kΩ - 100kΩ
- 通常使用较大值（降低功耗）
- 适合低速应用

计算公式：
Rp(min) = (VDD - 0.4V) / 0.004A = (VDD - 0.4) / 0.004
Rp(max) = tr / (0.8473 × Cb)

示例（VDD=3.3V, Cb=100pF, tr=1000ns）：
Rp(min) = (3.3 - 0.4) / 0.004 = 725Ω
Rp(max) = 1000ns / (0.8473 × 100pF) = 11.8kΩ
推荐值：4.7kΩ
```

### 超时机制

**SMBus超时规范**：

```
超时类型：

1. 时钟低电平超时（TLOW:SEXT）：
   - 最小值：25ms
   - 典型值：25-35ms
   - 触发条件：SCL被拉低超过此时间
   - 作用：防止从机时钟拉伸过长

2. 时钟高电平超时（THIGH:MAX）：
   - 最大值：50μs（SMBus 2.0）
   - 作用：限制时钟高电平时间

3. 累积时钟低电平超时：
   - 最大值：25-35ms
   - 包括所有时钟拉伸的累积时间
   - 超时后必须复位总线

超时处理流程：
START → 传输数据 → 时钟拉伸 → 超时检测 → 复位总线

示例：
主机发送数据 → 从机拉低SCL（处理数据）→ 
如果超过25ms → 主机检测超时 → 
主机发送STOP → 复位总线 → 重试或报错
```

**超时实现方法**：

```c
// 软件超时检测
#define SMBUS_TIMEOUT_MS  30

bool SMBus_WaitSCL_High(void) {
    uint32_t start_time = HAL_GetTick();
    
    while (GPIO_ReadPin(SCL_PORT, SCL_PIN) == 0) {
        if (HAL_GetTick() - start_time > SMBUS_TIMEOUT_MS) {
            // 超时，复位总线
            SMBus_BusReset();
            return false;
        }
    }
    
    return true;
}

// 硬件超时（使用定时器）
void SMBus_StartTimeout(void) {
    // 启动25ms定时器
    TIM_SetCounter(TIM2, 0);
    TIM_Cmd(TIM2, ENABLE);
}

void SMBus_StopTimeout(void) {
    TIM_Cmd(TIM2, DISABLE);
}

void TIM2_IRQHandler(void) {
    if (TIM_GetITStatus(TIM2, TIM_IT_Update)) {
        // 超时中断
        SMBus_TimeoutHandler();
        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
    }
}
```

### 地址保留

**SMBus保留地址**：

```
地址范围：0x00 - 0x7F (7位地址)

保留地址：
0x00      : 通用调用地址（General Call）
0x01      : CBUS地址
0x02      : 保留用于不同总线格式
0x03      : 保留用于未来使用
0x04-0x07 : Hs-mode主机代码
0x08-0x77 : 可用设备地址（SMBus设备使用此范围）
0x78-0x7B : 10位地址
0x7C-0x7F : 保留

I2C vs SMBus地址使用：
I2C: 0x00-0x7F 都可用（除特殊地址）
SMBus: 0x08-0x77 可用（更严格）

注意：
- SMBus设备不应使用0x00-0x07
- 避免使用0x78-0x7F
- 推荐使用0x10-0x6F范围
```

### 兼容性分析

**I2C设备在SMBus总线上**：

```
兼容性矩阵：

特性                I2C设备  SMBus总线  兼容性
电气特性            ✓        ✓         通常兼容
时钟频率            ✓        ✓         需要≤100kHz
超时机制            ✗        ✓         I2C设备可能不支持
PEC                 ✗        可选       I2C设备忽略PEC
地址范围            0x00-0x7F 0x08-0x77 需要检查地址

兼容性建议：
1. I2C设备可以在SMBus总线上工作
2. 但I2C设备不支持超时和PEC
3. 主机需要处理I2C设备的特殊性
4. 建议混合系统使用I2C模式
```

**SMBus设备在I2C总线上**：

```
兼容性考虑：

1. 电气兼容性：
   - SMBus设备通常可以在I2C总线上工作
   - 需要确认电压电平兼容

2. 超时问题：
   - SMBus设备期望主机支持超时
   - I2C主机可能不支持
   - 可能导致通信失败

3. PEC问题：
   - SMBus设备可能要求PEC
   - I2C主机不支持PEC
   - 需要禁用PEC或使用兼容模式

4. 时钟拉伸：
   - SMBus设备可能长时间拉伸时钟
   - I2C主机需要支持

建议：
- 使用SMBus兼容的I2C控制器
- 或在软件层实现SMBus特性
```

## SMBus协议规范

### 协议层次结构

**SMBus协议栈**：

```
┌─────────────────────────────────┐
│      应用层（Application）       │
│  - 设备特定命令                  │
│  - 数据解释                      │
├─────────────────────────────────┤
│      命令层（Command）           │
│  - Quick Command                │
│  - Send/Receive Byte            │
│  - Read/Write Byte/Word         │
│  - Block Read/Write             │
│  - Process Call                 │
├─────────────────────────────────┤
│      传输层（Transaction）       │
│  - START/STOP条件               │
│  - 地址传输                      │
│  - 数据传输                      │
│  - ACK/NACK                     │
│  - PEC校验                       │
├─────────────────────────────────┤
│      物理层（Physical）          │
│  - 电气特性                      │
│  - 时序要求                      │
│  - 总线仲裁                      │
└─────────────────────────────────┘
```

### 基本传输格式

**SMBus传输结构**：

```
基本格式：
START → 地址+R/W → ACK → 数据 → ACK → ... → STOP

详细格式：
S  : START条件
Sr : 重复START条件
P  : STOP条件
A  : ACK（确认）
N  : NACK（非确认）
Wr : 写位（0）
Rd : 读位（1）

示例1：写单字节
S → [Addr+Wr] → A → [Data] → A → P

示例2：读单字节
S → [Addr+Rd] → A → [Data] → N → P

示例3：写寄存器
S → [Addr+Wr] → A → [Cmd] → A → [Data] → A → P

示例4：读寄存器
S → [Addr+Wr] → A → [Cmd] → A → 
Sr → [Addr+Rd] → A → [Data] → N → P
```

### SMBus命令协议

**1. Quick Command（快速命令）**：

```
用途：
- 简单的设备开关控制
- 设备存在检测
- 无数据传输

格式：
S → [Addr+Wr/Rd] → A → P

特点：
- 最简单的SMBus命令
- 只传输地址和读写位
- 通过R/W位传递1位信息

应用示例：
- 开关设备电源
- 设备响应测试

代码实现：
```c
// Quick Command实现
bool SMBus_QuickCommand(uint8_t addr, bool read) {
    // 发送START
    SMBus_Start();
    
    // 发送地址+R/W位
    if (!SMBus_SendByte((addr << 1) | (read ? 1 : 0))) {
        SMBus_Stop();
        return false;
    }
    
    // 发送STOP
    SMBus_Stop();
    
    return true;
}

// 使用示例：设备存在检测
bool SMBus_DevicePresent(uint8_t addr) {
    return SMBus_QuickCommand(addr, false);
}
```

**2. Send Byte（发送字节）**：

```
用途：
- 发送单个字节到设备
- 简单的命令或数据传输

格式：
S → [Addr+Wr] → A → [Data] → A → P

特点：
- 传输1字节数据
- 无命令码
- 适合简单设备

应用示例：
- 设置设备模式
- 发送控制命令

代码实现：
```c
// Send Byte实现
bool SMBus_SendByte(uint8_t addr, uint8_t data) {
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据
    if (!SMBus_WriteByte(data)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：设置设备模式
void SetDeviceMode(uint8_t addr, uint8_t mode) {
    SMBus_SendByte(addr, mode);
}
```

**3. Receive Byte（接收字节）**：

```
用途：
- 从设备读取单个字节
- 读取状态或简单数据

格式：
S → [Addr+Rd] → A → [Data] → N → P

特点：
- 读取1字节数据
- 无命令码
- 主机发送NACK结束

应用示例：
- 读取设备状态
- 读取传感器数据

代码实现：
```c
// Receive Byte实现
bool SMBus_ReceiveByte(uint8_t addr, uint8_t *data) {
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据（发送NACK）
    *data = SMBus_ReadByte(false);
    
    SMBus_Stop();
    return true;
}

// 使用示例：读取温度
uint8_t ReadTemperature(uint8_t addr) {
    uint8_t temp;
    if (SMBus_ReceiveByte(addr, &temp)) {
        return temp;
    }
    return 0xFF;  // 错误值
}
```

**4. Write Byte（写字节）**：

```
用途：
- 写入数据到指定寄存器
- 最常用的SMBus命令

格式：
S → [Addr+Wr] → A → [Cmd] → A → [Data] → A → P

特点：
- 包含命令码（寄存器地址）
- 写入1字节数据
- 支持寄存器访问

应用示例：
- 配置设备寄存器
- 写入控制参数

代码实现：
```c
// Write Byte实现
bool SMBus_WriteByte(uint8_t addr, uint8_t cmd, uint8_t data) {
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据
    if (!SMBus_WriteByte(data)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：配置传感器
void ConfigureSensor(uint8_t addr) {
    SMBus_WriteByte(addr, 0x01, 0x60);  // 配置寄存器
    SMBus_WriteByte(addr, 0x02, 0x80);  // 控制寄存器
}
```

**5. Read Byte（读字节）**：

```
用途：
- 从指定寄存器读取数据
- 最常用的SMBus读命令

格式：
S → [Addr+Wr] → A → [Cmd] → A → 
Sr → [Addr+Rd] → A → [Data] → N → P

特点：
- 包含命令码
- 使用重复START
- 读取1字节数据

应用示例：
- 读取寄存器值
- 读取传感器数据

代码实现：
```c
// Read Byte实现
bool SMBus_ReadByte(uint8_t addr, uint8_t cmd, uint8_t *data) {
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据
    *data = SMBus_ReadByte(false);  // NACK
    
    SMBus_Stop();
    return true;
}

// 使用示例：读取状态寄存器
uint8_t ReadStatus(uint8_t addr) {
    uint8_t status;
    if (SMBus_ReadByte(addr, 0x00, &status)) {
        return status;
    }
    return 0xFF;
}
```

**6. Write Word（写字）**：

```
用途：
- 写入16位数据到寄存器
- 传输双字节数据

格式：
S → [Addr+Wr] → A → [Cmd] → A → [DataLow] → A → [DataHigh] → A → P

特点：
- 传输2字节数据
- 低字节在前（LSB first）
- 适合16位寄存器

应用示例：
- 设置16位配置值
- 写入阈值参数

代码实现：
```c
// Write Word实现
bool SMBus_WriteWord(uint8_t addr, uint8_t cmd, uint16_t data) {
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送低字节
    if (!SMBus_WriteByte(data & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送高字节
    if (!SMBus_WriteByte((data >> 8) & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：设置温度阈值
void SetTemperatureThreshold(uint8_t addr, int16_t threshold) {
    // 温度值通常是16位有符号数
    SMBus_WriteWord(addr, 0x05, (uint16_t)threshold);
}
```

**7. Read Word（读字）**：

```
用途：
- 从寄存器读取16位数据
- 读取双字节值

格式：
S → [Addr+Wr] → A → [Cmd] → A → 
Sr → [Addr+Rd] → A → [DataLow] → A → [DataHigh] → N → P

特点：
- 读取2字节数据
- 低字节在前
- 最后一个字节NACK

应用示例：
- 读取16位传感器数据
- 读取配置值

代码实现：
```c
// Read Word实现
bool SMBus_ReadWord(uint8_t addr, uint8_t cmd, uint16_t *data) {
    uint8_t low, high;
    
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取低字节（ACK）
    low = SMBus_ReadByte(true);
    
    // 读取高字节（NACK）
    high = SMBus_ReadByte(false);
    
    SMBus_Stop();
    
    // 组合数据
    *data = (high << 8) | low;
    
    return true;
}

// 使用示例：读取电压值
float ReadVoltage(uint8_t addr) {
    uint16_t raw_value;
    if (SMBus_ReadWord(addr, 0x09, &raw_value)) {
        // 转换为实际电压（假设LSB=1mV）
        return raw_value / 1000.0;
    }
    return 0.0;
}
```

**8. Process Call（处理调用）**：

```
用途：
- 发送16位数据，接收16位结果
- 类似函数调用
- 用于计算或转换

格式：
S → [Addr+Wr] → A → [Cmd] → A → [DataLow] → A → [DataHigh] → A → 
Sr → [Addr+Rd] → A → [ResultLow] → A → [ResultHigh] → N → P

特点：
- 写入2字节，读取2字节
- 单次事务完成
- 适合需要处理的操作

应用示例：
- 温度转换
- 数据校准
- 计算操作

代码实现：
```c
// Process Call实现
bool SMBus_ProcessCall(uint8_t addr, uint8_t cmd, 
                       uint16_t data_in, uint16_t *data_out) {
    uint8_t low, high;
    
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送输入数据（低字节）
    if (!SMBus_WriteByte(data_in & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送输入数据（高字节）
    if (!SMBus_WriteByte((data_in >> 8) & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取结果（低字节，ACK）
    low = SMBus_ReadByte(true);
    
    // 读取结果（高字节，NACK）
    high = SMBus_ReadByte(false);
    
    SMBus_Stop();
    
    // 组合结果
    *data_out = (high << 8) | low;
    
    return true;
}

// 使用示例：温度校准
int16_t CalibrateTemperature(uint8_t addr, int16_t raw_temp) {
    uint16_t calibrated;
    if (SMBus_ProcessCall(addr, 0x10, (uint16_t)raw_temp, &calibrated)) {
        return (int16_t)calibrated;
    }
    return raw_temp;  // 校准失败，返回原始值
}
```

**9. Block Write（块写入）**：

```
用途：
- 写入多字节数据块
- 传输大量数据

格式：
S → [Addr+Wr] → A → [Cmd] → A → [Count] → A → 
[Data1] → A → [Data2] → A → ... → [DataN] → A → P

特点：
- 可传输1-32字节
- 包含字节计数
- 适合批量写入

应用示例：
- 写入配置数据
- 固件更新
- 批量参数设置

代码实现：
```c
// Block Write实现
bool SMBus_BlockWrite(uint8_t addr, uint8_t cmd, 
                      uint8_t *data, uint8_t count) {
    // 检查数据长度
    if (count == 0 || count > 32) {
        return false;
    }
    
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送字节计数
    if (!SMBus_WriteByte(count)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据块
    for (uint8_t i = 0; i < count; i++) {
        if (!SMBus_WriteByte(data[i])) {
            SMBus_Stop();
            return false;
        }
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：写入配置数据
void WriteConfiguration(uint8_t addr) {
    uint8_t config[] = {
        0x01, 0x02, 0x03, 0x04,  // 配置参数
        0x05, 0x06, 0x07, 0x08
    };
    
    SMBus_BlockWrite(addr, 0x20, config, sizeof(config));
}
```

**10. Block Read（块读取）**：

```
用途：
- 读取多字节数据块
- 接收大量数据

格式：
S → [Addr+Wr] → A → [Cmd] → A → 
Sr → [Addr+Rd] → A → [Count] → A → 
[Data1] → A → [Data2] → A → ... → [DataN] → N → P

特点：
- 可读取1-32字节
- 从机返回字节计数
- 最后一个字节NACK

应用示例：
- 读取传感器数据
- 读取设备信息
- 批量数据采集

代码实现：
```c
// Block Read实现
bool SMBus_BlockRead(uint8_t addr, uint8_t cmd, 
                     uint8_t *data, uint8_t *count) {
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取字节计数
    *count = SMBus_ReadByte(true);  // ACK
    
    // 检查计数有效性
    if (*count == 0 || *count > 32) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据块
    for (uint8_t i = 0; i < *count; i++) {
        // 最后一个字节发送NACK
        bool ack = (i < *count - 1);
        data[i] = SMBus_ReadByte(ack);
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：读取设备信息
void ReadDeviceInfo(uint8_t addr) {
    uint8_t info[32];
    uint8_t count;
    
    if (SMBus_BlockRead(addr, 0x30, info, &count)) {
        printf("Device Info (%d bytes):\n", count);
        for (uint8_t i = 0; i < count; i++) {
            printf("%02X ", info[i]);
        }
        printf("\n");
    }
}
```

**11. Block Write-Block Read Process Call（块处理调用）**：

```
用途：
- 发送数据块，接收数据块
- 复杂的数据处理
- 批量转换操作

格式：
S → [Addr+Wr] → A → [Cmd] → A → [WriteCount] → A → 
[WriteData1] → A → ... → [WriteDataN] → A → 
Sr → [Addr+Rd] → A → [ReadCount] → A → 
[ReadData1] → A → ... → [ReadDataM] → N → P

特点：
- 写入和读取数据块
- 单次事务完成
- 最复杂的SMBus命令

应用示例：
- 批量数据转换
- 加密/解密操作
- 复杂计算

代码实现：
```c
// Block Write-Block Read Process Call实现
bool SMBus_BlockProcessCall(uint8_t addr, uint8_t cmd,
                            uint8_t *write_data, uint8_t write_count,
                            uint8_t *read_data, uint8_t *read_count) {
    // 检查写入数据长度
    if (write_count == 0 || write_count > 32) {
        return false;
    }
    
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送写入字节计数
    if (!SMBus_WriteByte(write_count)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送写入数据
    for (uint8_t i = 0; i < write_count; i++) {
        if (!SMBus_WriteByte(write_data[i])) {
            SMBus_Stop();
            return false;
        }
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取字节计数
    *read_count = SMBus_ReadByte(true);
    
    // 检查计数有效性
    if (*read_count == 0 || *read_count > 32) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据块
    for (uint8_t i = 0; i < *read_count; i++) {
        bool ack = (i < *read_count - 1);
        read_data[i] = SMBus_ReadByte(ack);
    }
    
    SMBus_Stop();
    return true;
}

// 使用示例：批量数据转换
void ConvertSensorData(uint8_t addr) {
    uint8_t raw_data[] = {0x12, 0x34, 0x56, 0x78};
    uint8_t converted_data[32];
    uint8_t result_count;
    
    if (SMBus_BlockProcessCall(addr, 0x40, 
                               raw_data, sizeof(raw_data),
                               converted_data, &result_count)) {
        printf("Converted %d bytes\n", result_count);
    }
}
```

### SMBus命令总结

**命令对比表**：

| 命令 | 写入字节数 | 读取字节数 | 用途 | 复杂度 |
|------|-----------|-----------|------|--------|
| Quick Command | 0 | 0 | 设备控制/检测 | ★☆☆☆☆ |
| Send Byte | 1 | 0 | 发送命令 | ★☆☆☆☆ |
| Receive Byte | 0 | 1 | 读取状态 | ★☆☆☆☆ |
| Write Byte | 2 | 0 | 写寄存器 | ★★☆☆☆ |
| Read Byte | 1 | 1 | 读寄存器 | ★★☆☆☆ |
| Write Word | 3 | 0 | 写16位数据 | ★★☆☆☆ |
| Read Word | 1 | 2 | 读16位数据 | ★★☆☆☆ |
| Process Call | 3 | 2 | 数据处理 | ★★★☆☆ |
| Block Write | 2-33 | 0 | 批量写入 | ★★★★☆ |
| Block Read | 1 | 1-32 | 批量读取 | ★★★★☆ |
| Block Process Call | 2-33 | 1-32 | 批量处理 | ★★★★★ |

## 包错误检查（PEC）

### PEC概述

**什么是PEC**：

```
PEC (Packet Error Checking) 是SMBus的可选错误检测机制：

特点：
- 基于CRC-8算法
- 多项式：x^8 + x^2 + x + 1 (0x07)
- 初始值：0x00
- 检测单字节和多字节错误
- 可选功能（设备可以不支持）

优势：
- 提高通信可靠性
- 检测传输错误
- 适合关键应用

劣势：
- 增加1字节开销
- 增加计算复杂度
- 不是所有设备都支持
```

### PEC计算算法

**CRC-8计算原理**：

```
多项式：P(x) = x^8 + x^2 + x + 1
二进制：100000111
十六进制：0x07

计算步骤：
1. 初始化CRC = 0x00
2. 对每个字节：
   a. CRC = CRC XOR 字节
   b. 对8位循环：
      - 如果CRC最高位为1：
        CRC = (CRC << 1) XOR 0x07
      - 否则：
        CRC = CRC << 1
3. 最终CRC值即为PEC

示例计算：
数据：0x5A
初始CRC：0x00

步骤1：CRC = 0x00 XOR 0x5A = 0x5A (01011010)
步骤2：处理8位
  位7(1): CRC = (0x5A << 1) XOR 0x07 = 0xB4 XOR 0x07 = 0xB3
  位6(0): CRC = 0xB3 << 1 = 0x66
  位5(1): CRC = (0x66 << 1) XOR 0x07 = 0xCC XOR 0x07 = 0xCB
  位4(1): CRC = (0xCB << 1) XOR 0x07 = 0x96 XOR 0x07 = 0x91
  位3(0): CRC = 0x91 << 1 = 0x22
  位2(1): CRC = (0x22 << 1) XOR 0x07 = 0x44 XOR 0x07 = 0x43
  位1(0): CRC = 0x43 << 1 = 0x86
  位0(1): CRC = (0x86 << 1) XOR 0x07 = 0x0C XOR 0x07 = 0x0B

结果：PEC = 0x0B
```

**软件实现**：

```c
// CRC-8查找表（优化性能）
static const uint8_t crc8_table[256] = {
    0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15,
    0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D,
    0x70, 0x77, 0x7E, 0x79, 0x6C, 0x6B, 0x62, 0x65,
    0x48, 0x4F, 0x46, 0x41, 0x54, 0x53, 0x5A, 0x5D,
    0xE0, 0xE7, 0xEE, 0xE9, 0xFC, 0xFB, 0xF2, 0xF5,
    0xD8, 0xDF, 0xD6, 0xD1, 0xC4, 0xC3, 0xCA, 0xCD,
    0x90, 0x97, 0x9E, 0x99, 0x8C, 0x8B, 0x82, 0x85,
    0xA8, 0xAF, 0xA6, 0xA1, 0xB4, 0xB3, 0xBA, 0xBD,
    0xC7, 0xC0, 0xC9, 0xCE, 0xDB, 0xDC, 0xD5, 0xD2,
    0xFF, 0xF8, 0xF1, 0xF6, 0xE3, 0xE4, 0xED, 0xEA,
    0xB7, 0xB0, 0xB9, 0xBE, 0xAB, 0xAC, 0xA5, 0xA2,
    0x8F, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9D, 0x9A,
    0x27, 0x20, 0x29, 0x2E, 0x3B, 0x3C, 0x35, 0x32,
    0x1F, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0D, 0x0A,
    0x57, 0x50, 0x59, 0x5E, 0x4B, 0x4C, 0x45, 0x42,
    0x6F, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7D, 0x7A,
    0x89, 0x8E, 0x87, 0x80, 0x95, 0x92, 0x9B, 0x9C,
    0xB1, 0xB6, 0xBF, 0xB8, 0xAD, 0xAA, 0xA3, 0xA4,
    0xF9, 0xFE, 0xF7, 0xF0, 0xE5, 0xE2, 0xEB, 0xEC,
    0xC1, 0xC6, 0xCF, 0xC8, 0xDD, 0xDA, 0xD3, 0xD4,
    0x69, 0x6E, 0x67, 0x60, 0x75, 0x72, 0x7B, 0x7C,
    0x51, 0x56, 0x5F, 0x58, 0x4D, 0x4A, 0x43, 0x44,
    0x19, 0x1E, 0x17, 0x10, 0x05, 0x02, 0x0B, 0x0C,
    0x21, 0x26, 0x2F, 0x28, 0x3D, 0x3A, 0x33, 0x34,
    0x4E, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5C, 0x5B,
    0x76, 0x71, 0x78, 0x7F, 0x6A, 0x6D, 0x64, 0x63,
    0x3E, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2C, 0x2B,
    0x06, 0x01, 0x08, 0x0F, 0x1A, 0x1D, 0x14, 0x13,
    0xAE, 0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB,
    0x96, 0x91, 0x98, 0x9F, 0x8A, 0x8D, 0x84, 0x83,
    0xDE, 0xD9, 0xD0, 0xD7, 0xC2, 0xC5, 0xCC, 0xCB,
    0xE6, 0xE1, 0xE8, 0xEF, 0xFA, 0xFD, 0xF4, 0xF3
};

// 使用查找表计算CRC-8
uint8_t SMBus_CalculatePEC_Table(uint8_t *data, uint8_t len) {
    uint8_t crc = 0x00;
    
    for (uint8_t i = 0; i < len; i++) {
        crc = crc8_table[crc ^ data[i]];
    }
    
    return crc;
}

// 不使用查找表的实现（节省内存）
uint8_t SMBus_CalculatePEC(uint8_t *data, uint8_t len) {
    uint8_t crc = 0x00;
    
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc = crc << 1;
            }
        }
    }
    
    return crc;
}

// 增量计算PEC（逐字节更新）
uint8_t SMBus_UpdatePEC(uint8_t crc, uint8_t data) {
    return crc8_table[crc ^ data];
}
```

### PEC在SMBus命令中的应用

**带PEC的命令格式**：

```
Write Byte with PEC:
S → [Addr+Wr] → A → [Cmd] → A → [Data] → A → [PEC] → A → P

Read Byte with PEC:
S → [Addr+Wr] → A → [Cmd] → A → 
Sr → [Addr+Rd] → A → [Data] → A → [PEC] → N → P

PEC计算范围：
- 包括所有传输的字节
- 包括地址字节（带R/W位）
- 不包括START、STOP、ACK/NACK

示例：Write Byte (Addr=0x5A, Cmd=0x10, Data=0x25)
传输序列：
S → [0xB4] → A → [0x10] → A → [0x25] → A → [PEC] → A → P
     ^^^^         ^^^^         ^^^^         ^^^^
   Addr+Wr(0)    Cmd         Data         PEC

PEC计算：
数据序列：0xB4, 0x10, 0x25
CRC = 0x00
CRC = CRC8(0x00, 0xB4) = 0x3E
CRC = CRC8(0x3E, 0x10) = 0x7C
CRC = CRC8(0x7C, 0x25) = 0x42
PEC = 0x42
```

**带PEC的命令实现**：

```c
// Write Byte with PEC
bool SMBus_WriteByteWithPEC(uint8_t addr, uint8_t cmd, uint8_t data) {
    uint8_t pec_data[3];
    uint8_t pec;
    
    // 准备PEC计算数据
    pec_data[0] = (addr << 1) | 0;  // 地址+写位
    pec_data[1] = cmd;
    pec_data[2] = data;
    
    // 计算PEC
    pec = SMBus_CalculatePEC(pec_data, 3);
    
    SMBus_Start();
    
    // 发送地址+写位
    if (!SMBus_WriteByte(pec_data[0])) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据
    if (!SMBus_WriteByte(data)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送PEC
    if (!SMBus_WriteByte(pec)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// Read Byte with PEC
bool SMBus_ReadByteWithPEC(uint8_t addr, uint8_t cmd, uint8_t *data) {
    uint8_t pec_data[4];
    uint8_t received_pec;
    uint8_t calculated_pec;
    
    SMBus_Start();
    
    // 发送地址+写位
    pec_data[0] = (addr << 1) | 0;
    if (!SMBus_WriteByte(pec_data[0])) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令码
    pec_data[1] = cmd;
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读位
    pec_data[2] = (addr << 1) | 1;
    if (!SMBus_WriteByte(pec_data[2])) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据（ACK）
    *data = SMBus_ReadByte(true);
    pec_data[3] = *data;
    
    // 读取PEC（NACK）
    received_pec = SMBus_ReadByte(false);
    
    SMBus_Stop();
    
    // 验证PEC
    calculated_pec = SMBus_CalculatePEC(pec_data, 4);
    
    if (received_pec != calculated_pec) {
        printf("PEC Error: Expected 0x%02X, Got 0x%02X\n", 
               calculated_pec, received_pec);
        return false;
    }
    
    return true;
}

// Block Write with PEC
bool SMBus_BlockWriteWithPEC(uint8_t addr, uint8_t cmd,
                             uint8_t *data, uint8_t count) {
    if (count == 0 || count > 32) {
        return false;
    }
    
    // 准备PEC计算
    uint8_t crc = 0x00;
    
    SMBus_Start();
    
    // 发送地址+写位
    uint8_t addr_byte = (addr << 1) | 0;
    if (!SMBus_WriteByte(addr_byte)) {
        SMBus_Stop();
        return false;
    }
    crc = SMBus_UpdatePEC(crc, addr_byte);
    
    // 发送命令码
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    crc = SMBus_UpdatePEC(crc, cmd);
    
    // 发送字节计数
    if (!SMBus_WriteByte(count)) {
        SMBus_Stop();
        return false;
    }
    crc = SMBus_UpdatePEC(crc, count);
    
    // 发送数据块
    for (uint8_t i = 0; i < count; i++) {
        if (!SMBus_WriteByte(data[i])) {
            SMBus_Stop();
            return false;
        }
        crc = SMBus_UpdatePEC(crc, data[i]);
    }
    
    // 发送PEC
    if (!SMBus_WriteByte(crc)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}
```

### PEC错误处理

**PEC错误处理策略**：

```c
// PEC错误统计
typedef struct {
    uint32_t total_transactions;
    uint32_t pec_errors;
    uint32_t retry_success;
    uint32_t retry_failed;
} SMBus_Statistics_t;

SMBus_Statistics_t smbus_stats = {0};

// 带重试的PEC读取
bool SMBus_ReadByteWithPEC_Retry(uint8_t addr, uint8_t cmd, 
                                 uint8_t *data, uint8_t max_retries) {
    smbus_stats.total_transactions++;
    
    for (uint8_t retry = 0; retry < max_retries; retry++) {
        if (SMBus_ReadByteWithPEC(addr, cmd, data)) {
            if (retry > 0) {
                smbus_stats.retry_success++;
            }
            return true;
        }
        
        smbus_stats.pec_errors++;
        
        // 延时后重试
        HAL_Delay(10);
    }
    
    smbus_stats.retry_failed++;
    return false;
}

// 打印统计信息
void SMBus_PrintStatistics(void) {
    printf("\n=== SMBus Statistics ===\n");
    printf("Total Transactions: %lu\n", smbus_stats.total_transactions);
    printf("PEC Errors: %lu (%.2f%%)\n", 
           smbus_stats.pec_errors,
           (float)smbus_stats.pec_errors / smbus_stats.total_transactions * 100);
    printf("Retry Success: %lu\n", smbus_stats.retry_success);
    printf("Retry Failed: %lu\n", smbus_stats.retry_failed);
}
```

## 超时处理机制

### 超时类型和检测

**超时检测实现**：

```c
// 超时配置
#define SMBUS_TIMEOUT_MS        30      // 总超时
#define SMBUS_CLOCK_LOW_MAX_MS  25      // 时钟低电平最大时间
#define SMBUS_BYTE_TIMEOUT_MS   10      // 单字节超时

// 超时检测结构
typedef struct {
    uint32_t start_time;
    uint32_t timeout_ms;
    bool enabled;
} SMBus_Timeout_t;

SMBus_Timeout_t smbus_timeout;

// 启动超时计时
void SMBus_TimeoutStart(uint32_t timeout_ms) {
    smbus_timeout.start_time = HAL_GetTick();
    smbus_timeout.timeout_ms = timeout_ms;
    smbus_timeout.enabled = true;
}

// 停止超时计时
void SMBus_TimeoutStop(void) {
    smbus_timeout.enabled = false;
}

// 检查是否超时
bool SMBus_IsTimeout(void) {
    if (!smbus_timeout.enabled) {
        return false;
    }
    
    uint32_t elapsed = HAL_GetTick() - smbus_timeout.start_time;
    return (elapsed >= smbus_timeout.timeout_ms);
}

// 等待SCL高电平（带超时）
bool SMBus_WaitSCL_High_Timeout(void) {
    SMBus_TimeoutStart(SMBUS_CLOCK_LOW_MAX_MS);
    
    while (GPIO_ReadPin(SCL_PORT, SCL_PIN) == 0) {
        if (SMBus_IsTimeout()) {
            printf("Timeout: SCL stuck low\n");
            SMBus_TimeoutStop();
            return false;
        }
    }
    
    SMBus_TimeoutStop();
    return true;
}

// 等待ACK（带超时）
bool SMBus_WaitACK_Timeout(void) {
    SMBus_TimeoutStart(SMBUS_BYTE_TIMEOUT_MS);
    
    // 释放SDA
    SDA_HIGH();
    
    // 等待从机拉低SDA（ACK）
    while (GPIO_ReadPin(SDA_PORT, SDA_PIN) == 1) {
        if (SMBus_IsTimeout()) {
            printf("Timeout: No ACK received\n");
            SMBus_TimeoutStop();
            return false;
        }
    }
    
    SMBus_TimeoutStop();
    return true;
}
```

### 超时恢复机制

**总线复位和恢复**：

```c
// 总线复位
void SMBus_BusReset(void) {
    printf("Performing SMBus bus reset...\n");
    
    // 1. 确保SDA和SCL都是高电平
    SDA_HIGH();
    SCL_HIGH();
    HAL_Delay(1);
    
    // 2. 发送9个时钟脉冲清除总线
    for (int i = 0; i < 9; i++) {
        SCL_LOW();
        HAL_Delay_us(5);
        SCL_HIGH();
        HAL_Delay_us(5);
        
        // 检查SDA是否释放
        if (GPIO_ReadPin(SDA_PORT, SDA_PIN) == 1) {
            break;
        }
    }
    
    // 3. 发送STOP条件
    SDA_LOW();
    HAL_Delay_us(5);
    SCL_HIGH();
    HAL_Delay_us(5);
    SDA_HIGH();
    HAL_Delay_us(5);
    
    printf("Bus reset complete\n");
}

// 超时错误处理
typedef enum {
    SMBUS_TIMEOUT_NONE = 0,
    SMBUS_TIMEOUT_CLOCK_LOW,
    SMBUS_TIMEOUT_NO_ACK,
    SMBUS_TIMEOUT_BYTE_TRANSFER,
    SMBUS_TIMEOUT_TRANSACTION
} SMBus_TimeoutType_t;

void SMBus_HandleTimeout(SMBus_TimeoutType_t type) {
    printf("SMBus Timeout: ");
    
    switch (type) {
        case SMBUS_TIMEOUT_CLOCK_LOW:
            printf("Clock stuck low\n");
            break;
        case SMBUS_TIMEOUT_NO_ACK:
            printf("No ACK received\n");
            break;
        case SMBUS_TIMEOUT_BYTE_TRANSFER:
            printf("Byte transfer timeout\n");
            break;
        case SMBUS_TIMEOUT_TRANSACTION:
            printf("Transaction timeout\n");
            break;
        default:
            printf("Unknown\n");
            break;
    }
    
    // 执行总线复位
    SMBus_BusReset();
    
    // 延时后重新初始化
    HAL_Delay(100);
}

// 带超时保护的写字节
bool SMBus_WriteByte_Protected(uint8_t data) {
    SMBus_TimeoutStart(SMBUS_BYTE_TIMEOUT_MS);
    
    for (int bit = 7; bit >= 0; bit--) {
        // 检查超时
        if (SMBus_IsTimeout()) {
            SMBus_HandleTimeout(SMBUS_TIMEOUT_BYTE_TRANSFER);
            return false;
        }
        
        // 设置数据位
        if (data & (1 << bit)) {
            SDA_HIGH();
        } else {
            SDA_LOW();
        }
        HAL_Delay_us(5);
        
        // 时钟高电平
        SCL_HIGH();
        if (!SMBus_WaitSCL_High_Timeout()) {
            SMBus_HandleTimeout(SMBUS_TIMEOUT_CLOCK_LOW);
            return false;
        }
        HAL_Delay_us(5);
        
        // 时钟低电平
        SCL_LOW();
        HAL_Delay_us(5);
    }
    
    // 等待ACK
    if (!SMBus_WaitACK_Timeout()) {
        SMBus_HandleTimeout(SMBUS_TIMEOUT_NO_ACK);
        return false;
    }
    
    SMBus_TimeoutStop();
    return true;
}
```

## SMBus驱动完整实现

### 驱动架构设计

**驱动层次结构**：

```
┌─────────────────────────────────┐
│      应用层                      │
│  - 设备特定驱动                  │
│  - 业务逻辑                      │
├─────────────────────────────────┤
│      SMBus协议层                 │
│  - 命令实现                      │
│  - PEC计算                       │
│  - 超时处理                      │
├─────────────────────────────────┤
│      SMBus传输层                 │
│  - START/STOP                   │
│  - 字节读写                      │
│  - ACK/NACK                     │
├─────────────────────────────────┤
│      硬件抽象层（HAL）           │
│  - GPIO操作                      │
│  - 延时函数                      │
│  - 中断处理                      │
└─────────────────────────────────┘
```

### 硬件抽象层

**GPIO和延时函数**：

```c
// GPIO定义
#define SCL_PORT    GPIOB
#define SCL_PIN     GPIO_PIN_6
#define SDA_PORT    GPIOB
#define SDA_PIN     GPIO_PIN_7

// GPIO操作宏
#define SCL_HIGH()  HAL_GPIO_WritePin(SCL_PORT, SCL_PIN, GPIO_PIN_SET)
#define SCL_LOW()   HAL_GPIO_WritePin(SCL_PORT, SCL_PIN, GPIO_PIN_RESET)
#define SDA_HIGH()  HAL_GPIO_WritePin(SDA_PORT, SDA_PIN, GPIO_PIN_SET)
#define SDA_LOW()   HAL_GPIO_WritePin(SDA_PORT, SDA_PIN, GPIO_PIN_RESET)

#define SCL_READ()  HAL_GPIO_ReadPin(SCL_PORT, SCL_PIN)
#define SDA_READ()  HAL_GPIO_ReadPin(SDA_PORT, SDA_PIN)

// 微秒延时（根据实际MCU调整）
void HAL_Delay_us(uint32_t us) {
    uint32_t ticks = us * (SystemCoreClock / 1000000);
    while (ticks--) {
        __NOP();
    }
}

// GPIO初始化
void SMBus_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIO时钟
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    // 配置SCL和SDA为开漏输出
    GPIO_InitStruct.Pin = SCL_PIN | SDA_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    // 初始状态为高电平
    SCL_HIGH();
    SDA_HIGH();
}
```

### 传输层实现

**基本传输函数**：

```c
// SMBus时序参数（100kHz）
#define SMBUS_DELAY_US  5   // 半个时钟周期

// 发送START条件
void SMBus_Start(void) {
    SDA_HIGH();
    SCL_HIGH();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SDA_LOW();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SCL_LOW();
    HAL_Delay_us(SMBUS_DELAY_US);
}

// 发送STOP条件
void SMBus_Stop(void) {
    SDA_LOW();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SCL_HIGH();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SDA_HIGH();
    HAL_Delay_us(SMBUS_DELAY_US);
}

// 写入一个字节
bool SMBus_WriteByte(uint8_t data) {
    // 发送8位数据
    for (int bit = 7; bit >= 0; bit--) {
        if (data & (1 << bit)) {
            SDA_HIGH();
        } else {
            SDA_LOW();
        }
        HAL_Delay_us(SMBUS_DELAY_US);
        
        SCL_HIGH();
        HAL_Delay_us(SMBUS_DELAY_US);
        
        SCL_LOW();
        HAL_Delay_us(SMBUS_DELAY_US);
    }
    
    // 读取ACK
    SDA_HIGH();  // 释放SDA
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SCL_HIGH();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    bool ack = (SDA_READ() == 0);  // ACK = 低电平
    
    SCL_LOW();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    return ack;
}

// 读取一个字节
uint8_t SMBus_ReadByte(bool ack) {
    uint8_t data = 0;
    
    SDA_HIGH();  // 释放SDA
    
    // 读取8位数据
    for (int bit = 7; bit >= 0; bit--) {
        HAL_Delay_us(SMBUS_DELAY_US);
        
        SCL_HIGH();
        HAL_Delay_us(SMBUS_DELAY_US);
        
        if (SDA_READ()) {
            data |= (1 << bit);
        }
        
        SCL_LOW();
    }
    
    // 发送ACK/NACK
    if (ack) {
        SDA_LOW();   // ACK
    } else {
        SDA_HIGH();  // NACK
    }
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SCL_HIGH();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SCL_LOW();
    HAL_Delay_us(SMBUS_DELAY_US);
    
    SDA_HIGH();  // 释放SDA
    
    return data;
}
```

### 协议层实现

**完整的SMBus驱动**：

```c
// SMBus驱动结构
typedef struct {
    bool initialized;
    bool pec_enabled;
    uint32_t timeout_ms;
    SMBus_Statistics_t stats;
} SMBus_Driver_t;

SMBus_Driver_t smbus_driver = {
    .initialized = false,
    .pec_enabled = false,
    .timeout_ms = SMBUS_TIMEOUT_MS,
    .stats = {0}
};

// 初始化SMBus
bool SMBus_Init(bool enable_pec) {
    // 初始化GPIO
    SMBus_GPIO_Init();
    
    // 配置PEC
    smbus_driver.pec_enabled = enable_pec;
    
    // 总线复位
    SMBus_BusReset();
    
    smbus_driver.initialized = true;
    
    printf("SMBus initialized (PEC: %s)\n", 
           enable_pec ? "Enabled" : "Disabled");
    
    return true;
}

// Quick Command
bool SMBus_QuickCommand(uint8_t addr, bool read) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    SMBus_Start();
    
    bool result = SMBus_WriteByte((addr << 1) | (read ? 1 : 0));
    
    SMBus_Stop();
    
    return result;
}

// Send Byte
bool SMBus_SendByte(uint8_t addr, uint8_t data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(data)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// Receive Byte
bool SMBus_ReceiveByte(uint8_t addr, uint8_t *data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    *data = SMBus_ReadByte(false);  // NACK
    
    SMBus_Stop();
    return true;
}

// Write Byte (with optional PEC)
bool SMBus_WriteByte_Data(uint8_t addr, uint8_t cmd, uint8_t data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    if (smbus_driver.pec_enabled) {
        return SMBus_WriteByteWithPEC(addr, cmd, data);
    }
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(data)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// Read Byte (with optional PEC)
bool SMBus_ReadByte_Data(uint8_t addr, uint8_t cmd, uint8_t *data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    if (smbus_driver.pec_enabled) {
        return SMBus_ReadByteWithPEC(addr, cmd, data);
    }
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Start();  // 重复START
    
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    *data = SMBus_ReadByte(false);  // NACK
    
    SMBus_Stop();
    return true;
}

// Write Word
bool SMBus_WriteWord_Data(uint8_t addr, uint8_t cmd, uint16_t data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(data & 0xFF)) {  // 低字节
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte((data >> 8) & 0xFF)) {  // 高字节
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    return true;
}

// Read Word
bool SMBus_ReadWord_Data(uint8_t addr, uint8_t cmd, uint16_t *data) {
    if (!smbus_driver.initialized) {
        return false;
    }
    
    uint8_t low, high;
    
    SMBus_Start();
    
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Start();  // 重复START
    
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    low = SMBus_ReadByte(true);   // ACK
    high = SMBus_ReadByte(false); // NACK
    
    SMBus_Stop();
    
    *data = (high << 8) | low;
    
    return true;
}
```

## 实际应用案例

### 案例1：智能电池管理（Smart Battery）

**Smart Battery System规范**：

```
Smart Battery System (SBS) 是基于SMBus的电池管理标准：

组件：
- Smart Battery（智能电池）
- Smart Battery Charger（智能充电器）
- System Management Bus（SMBus）
- Host Controller（主机控制器）

地址分配：
0x0B: Smart Battery
0x09: Smart Battery Charger
0x16: Smart Battery Selector

标准命令：
0x08: Temperature（温度）
0x09: Voltage（电压）
0x0A: Current（电流）
0x0D: Relative State of Charge（相对电量）
0x0F: Battery Status（电池状态）
0x10: Cycle Count（循环次数）
```

**Smart Battery驱动实现**：

```c
// Smart Battery地址和命令
#define SMART_BATTERY_ADDR      0x0B

#define SB_CMD_TEMPERATURE      0x08
#define SB_CMD_VOLTAGE          0x09
#define SB_CMD_CURRENT          0x0A
#define SB_CMD_AVG_CURRENT      0x0B
#define SB_CMD_MAX_ERROR        0x0C
#define SB_CMD_RSOC             0x0D  // Relative State of Charge
#define SB_CMD_ASOC             0x0E  // Absolute State of Charge
#define SB_CMD_REMAINING_CAP    0x0F
#define SB_CMD_FULL_CAP         0x10
#define SB_CMD_RUN_TIME         0x11
#define SB_CMD_AVG_TIME         0x12
#define SB_CMD_BATTERY_STATUS   0x16
#define SB_CMD_CYCLE_COUNT      0x17
#define SB_CMD_DESIGN_CAP       0x18
#define SB_CMD_DESIGN_VOLTAGE   0x19
#define SB_CMD_SPEC_INFO        0x1A
#define SB_CMD_MFG_DATE         0x1B
#define SB_CMD_SERIAL_NUM       0x1C
#define SB_CMD_MFG_NAME         0x20
#define SB_CMD_DEVICE_NAME      0x21
#define SB_CMD_DEVICE_CHEM      0x22

// Smart Battery数据结构
typedef struct {
    int16_t temperature;      // 0.1K
    uint16_t voltage;         // mV
    int16_t current;          // mA
    uint16_t rsoc;            // %
    uint16_t remaining_cap;   // mAh
    uint16_t full_cap;        // mAh
    uint16_t status;          // 状态标志
    uint16_t cycle_count;     // 循环次数
} SmartBattery_Data_t;

// 读取电池温度
float SmartBattery_ReadTemperature(void) {
    uint16_t temp_raw;
    
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_TEMPERATURE, &temp_raw)) {
        // 温度单位：0.1K，转换为摄氏度
        float temp_k = temp_raw / 10.0;
        float temp_c = temp_k - 273.15;
        return temp_c;
    }
    
    return -999.0;  // 错误值
}

// 读取电池电压
float SmartBattery_ReadVoltage(void) {
    uint16_t voltage_mv;
    
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_VOLTAGE, &voltage_mv)) {
        return voltage_mv / 1000.0;  // 转换为V
    }
    
    return 0.0;
}

// 读取电池电流
float SmartBattery_ReadCurrent(void) {
    int16_t current_ma;
    
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_CURRENT, 
                           (uint16_t*)&current_ma)) {
        return current_ma / 1000.0;  // 转换为A
    }
    
    return 0.0;
}

// 读取电池电量（百分比）
uint8_t SmartBattery_ReadSOC(void) {
    uint16_t soc;
    
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_RSOC, &soc)) {
        return (uint8_t)soc;
    }
    
    return 0;
}

// 读取电池状态
uint16_t SmartBattery_ReadStatus(void) {
    uint16_t status;
    
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_BATTERY_STATUS, &status)) {
        return status;
    }
    
    return 0xFFFF;
}

// 解析电池状态
void SmartBattery_ParseStatus(uint16_t status) {
    printf("Battery Status: 0x%04X\n", status);
    
    if (status & 0x8000) printf("  - Over Charged Alarm\n");
    if (status & 0x4000) printf("  - Terminate Charge Alarm\n");
    if (status & 0x1000) printf("  - Over Temp Alarm\n");
    if (status & 0x0800) printf("  - Terminate Discharge Alarm\n");
    if (status & 0x0200) printf("  - Remaining Capacity Alarm\n");
    if (status & 0x0100) printf("  - Remaining Time Alarm\n");
    if (status & 0x0080) printf("  - Initialized\n");
    if (status & 0x0040) printf("  - Discharging\n");
    if (status & 0x0020) printf("  - Fully Charged\n");
    if (status & 0x0010) printf("  - Fully Discharged\n");
}

// 读取电池信息字符串
bool SmartBattery_ReadString(uint8_t cmd, char *buffer, uint8_t max_len) {
    uint8_t data[32];
    uint8_t count;
    
    if (!SMBus_BlockRead(SMART_BATTERY_ADDR, cmd, data, &count)) {
        return false;
    }
    
    // 限制长度
    if (count > max_len - 1) {
        count = max_len - 1;
    }
    
    // 复制字符串
    memcpy(buffer, data, count);
    buffer[count] = '\0';
    
    return true;
}

// 读取完整电池信息
void SmartBattery_ReadFullInfo(SmartBattery_Data_t *data) {
    char str_buffer[32];
    
    printf("\n=== Smart Battery Information ===\n");
    
    // 读取制造商
    if (SmartBattery_ReadString(SB_CMD_MFG_NAME, str_buffer, sizeof(str_buffer))) {
        printf("Manufacturer: %s\n", str_buffer);
    }
    
    // 读取设备名称
    if (SmartBattery_ReadString(SB_CMD_DEVICE_NAME, str_buffer, sizeof(str_buffer))) {
        printf("Device Name: %s\n", str_buffer);
    }
    
    // 读取化学类型
    if (SmartBattery_ReadString(SB_CMD_DEVICE_CHEM, str_buffer, sizeof(str_buffer))) {
        printf("Chemistry: %s\n", str_buffer);
    }
    
    // 读取序列号
    uint16_t serial;
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_SERIAL_NUM, &serial)) {
        printf("Serial Number: %u\n", serial);
    }
    
    // 读取设计容量
    uint16_t design_cap;
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_DESIGN_CAP, &design_cap)) {
        printf("Design Capacity: %u mAh\n", design_cap);
    }
    
    // 读取设计电压
    uint16_t design_voltage;
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_DESIGN_VOLTAGE, &design_voltage)) {
        printf("Design Voltage: %u mV\n", design_voltage);
    }
    
    // 读取循环次数
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_CYCLE_COUNT, &data->cycle_count)) {
        printf("Cycle Count: %u\n", data->cycle_count);
    }
    
    // 读取实时数据
    printf("\n--- Real-time Data ---\n");
    printf("Temperature: %.1f °C\n", SmartBattery_ReadTemperature());
    printf("Voltage: %.3f V\n", SmartBattery_ReadVoltage());
    printf("Current: %.3f A\n", SmartBattery_ReadCurrent());
    printf("State of Charge: %u %%\n", SmartBattery_ReadSOC());
    
    // 读取剩余容量
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_REMAINING_CAP, &data->remaining_cap)) {
        printf("Remaining Capacity: %u mAh\n", data->remaining_cap);
    }
    
    // 读取满充容量
    if (SMBus_ReadWord_Data(SMART_BATTERY_ADDR, SB_CMD_FULL_CAP, &data->full_cap)) {
        printf("Full Charge Capacity: %u mAh\n", data->full_cap);
    }
    
    // 读取并解析状态
    data->status = SmartBattery_ReadStatus();
    SmartBattery_ParseStatus(data->status);
}

// 电池监控任务
void SmartBattery_MonitorTask(void) {
    static uint32_t last_update = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 每5秒更新一次
    if (current_time - last_update >= 5000) {
        SmartBattery_Data_t battery_data;
        
        battery_data.temperature = (int16_t)(SmartBattery_ReadTemperature() * 10);
        battery_data.voltage = (uint16_t)(SmartBattery_ReadVoltage() * 1000);
        battery_data.current = (int16_t)(SmartBattery_ReadCurrent() * 1000);
        battery_data.rsoc = SmartBattery_ReadSOC();
        
        // 检查电池状态
        if (battery_data.rsoc < 20) {
            printf("WARNING: Low battery (%u%%)\n", battery_data.rsoc);
        }
        
        if (battery_data.temperature > 450) {  // 45°C
            printf("WARNING: High temperature (%.1f°C)\n", 
                   battery_data.temperature / 10.0);
        }
        
        last_update = current_time;
    }
}
```

### 案例2：温度传感器（LM75）

**LM75温度传感器**：

```
LM75是常见的SMBus温度传感器：

特性：
- SMBus/I2C兼容
- 9位温度分辨率（0.5°C）
- 温度范围：-55°C to +125°C
- 可编程温度阈值
- 中断输出

地址：0x48-0x4F（可配置）

寄存器：
0x00: Temperature（温度，只读）
0x01: Configuration（配置）
0x02: T_hyst（滞后温度）
0x03: T_os（过温阈值）
```

**LM75驱动实现**：

```c
// LM75地址和寄存器
#define LM75_ADDR           0x48

#define LM75_REG_TEMP       0x00
#define LM75_REG_CONF       0x01
#define LM75_REG_THYST      0x02
#define LM75_REG_TOS        0x03

// LM75配置位
#define LM75_CONF_SHUTDOWN  0x01
#define LM75_CONF_OS_MODE   0x02
#define LM75_CONF_OS_POL    0x04
#define LM75_CONF_FAULT_Q1  0x08
#define LM75_CONF_FAULT_Q2  0x10

// 初始化LM75
bool LM75_Init(uint8_t addr) {
    // 读取配置寄存器验证设备存在
    uint8_t config;
    if (!SMBus_ReadByte_Data(addr, LM75_REG_CONF, &config)) {
        printf("LM75 not found at 0x%02X\n", addr);
        return false;
    }
    
    // 配置为正常模式
    config &= ~LM75_CONF_SHUTDOWN;
    SMBus_WriteByte_Data(addr, LM75_REG_CONF, config);
    
    printf("LM75 initialized at 0x%02X\n", addr);
    return true;
}

// 读取温度
float LM75_ReadTemperature(uint8_t addr) {
    uint16_t temp_raw;
    
    if (!SMBus_ReadWord_Data(addr, LM75_REG_TEMP, &temp_raw)) {
        return -999.0;
    }
    
    // LM75温度格式：11位，0.125°C/LSB
    // 高字节是整数部分，低字节高5位是小数部分
    int16_t temp_value = (int16_t)temp_raw;
    temp_value >>= 5;  // 右移5位得到11位温度值
    
    float temperature = temp_value * 0.125;
    
    return temperature;
}

// 设置过温阈值
bool LM75_SetThreshold(uint8_t addr, float temp_os, float temp_hyst) {
    // 转换温度为LM75格式
    int16_t os_raw = (int16_t)(temp_os / 0.5) << 7;
    int16_t hyst_raw = (int16_t)(temp_hyst / 0.5) << 7;
    
    // 写入阈值
    if (!SMBus_WriteWord_Data(addr, LM75_REG_TOS, (uint16_t)os_raw)) {
        return false;
    }
    
    if (!SMBus_WriteWord_Data(addr, LM75_REG_THYST, (uint16_t)hyst_raw)) {
        return false;
    }
    
    printf("LM75 thresholds set: OS=%.1f°C, HYST=%.1f°C\n", temp_os, temp_hyst);
    return true;
}

// 使用示例
void LM75_Example(void) {
    uint8_t lm75_addr = LM75_ADDR;
    
    // 初始化
    if (!LM75_Init(lm75_addr)) {
        return;
    }
    
    // 设置阈值
    LM75_SetThreshold(lm75_addr, 50.0, 45.0);
    
    // 读取温度
    while (1) {
        float temp = LM75_ReadTemperature(lm75_addr);
        printf("Temperature: %.2f °C\n", temp);
        
        HAL_Delay(1000);
    }
}
```

### 案例3：EEPROM（24C02）

**24C02 EEPROM**：

```
24C02是256字节的I2C/SMBus EEPROM：

特性：
- 容量：256字节（2Kbit）
- 页大小：8字节
- 写周期：5ms
- SMBus兼容

地址：0x50-0x57（可配置）

操作：
- 字节写入
- 页写入（最多8字节）
- 当前地址读取
- 随机地址读取
- 顺序读取
```

**24C02驱动实现**：

```c
// 24C02地址
#define EEPROM_ADDR     0x50

// 24C02参数
#define EEPROM_SIZE     256
#define EEPROM_PAGE_SIZE 8

// 写入单字节
bool EEPROM_WriteByte(uint8_t addr, uint8_t mem_addr, uint8_t data) {
    if (!SMBus_WriteByte_Data(addr, mem_addr, data)) {
        return false;
    }
    
    // 等待写入完成（5ms）
    HAL_Delay(5);
    
    return true;
}

// 读取单字节
bool EEPROM_ReadByte(uint8_t addr, uint8_t mem_addr, uint8_t *data) {
    return SMBus_ReadByte_Data(addr, mem_addr, data);
}

// 页写入（最多8字节）
bool EEPROM_WritePage(uint8_t addr, uint8_t mem_addr, 
                      uint8_t *data, uint8_t len) {
    if (len == 0 || len > EEPROM_PAGE_SIZE) {
        return false;
    }
    
    // 检查是否跨页
    if ((mem_addr / EEPROM_PAGE_SIZE) != 
        ((mem_addr + len - 1) / EEPROM_PAGE_SIZE)) {
        printf("Error: Page boundary crossed\n");
        return false;
    }
    
    SMBus_Start();
    
    // 发送设备地址
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送内存地址
    if (!SMBus_WriteByte(mem_addr)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据
    for (uint8_t i = 0; i < len; i++) {
        if (!SMBus_WriteByte(data[i])) {
            SMBus_Stop();
            return false;
        }
    }
    
    SMBus_Stop();
    
    // 等待写入完成
    HAL_Delay(5);
    
    return true;
}

// 顺序读取
bool EEPROM_ReadSequential(uint8_t addr, uint8_t mem_addr,
                          uint8_t *buffer, uint8_t len) {
    if (len == 0) {
        return false;
    }
    
    SMBus_Start();
    
    // 发送设备地址+写
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送内存地址
    if (!SMBus_WriteByte(mem_addr)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送设备地址+读
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据
    for (uint8_t i = 0; i < len; i++) {
        bool ack = (i < len - 1);  // 最后一个字节NACK
        buffer[i] = SMBus_ReadByte(ack);
    }
    
    SMBus_Stop();
    
    return true;
}

// 写入多字节（自动处理页边界）
bool EEPROM_WriteMulti(uint8_t addr, uint8_t mem_addr,
                       uint8_t *data, uint16_t len) {
    uint16_t written = 0;
    
    while (written < len) {
        // 计算当前页剩余空间
        uint8_t page_offset = (mem_addr + written) % EEPROM_PAGE_SIZE;
        uint8_t page_remaining = EEPROM_PAGE_SIZE - page_offset;
        
        // 计算本次写入长度
        uint8_t write_len = (len - written) < page_remaining ? 
                           (len - written) : page_remaining;
        
        // 写入一页
        if (!EEPROM_WritePage(addr, mem_addr + written, 
                             data + written, write_len)) {
            return false;
        }
        
        written += write_len;
    }
    
    return true;
}

// 使用示例
void EEPROM_Example(void) {
    uint8_t write_data[] = "Hello, SMBus!";
    uint8_t read_data[32];
    
    // 写入数据
    printf("Writing to EEPROM...\n");
    if (EEPROM_WriteMulti(EEPROM_ADDR, 0x00, 
                         write_data, sizeof(write_data))) {
        printf("Write successful\n");
    }
    
    // 读取数据
    printf("Reading from EEPROM...\n");
    if (EEPROM_ReadSequential(EEPROM_ADDR, 0x00, 
                             read_data, sizeof(write_data))) {
        read_data[sizeof(write_data)] = '\0';
        printf("Read data: %s\n", read_data);
    }
}
```

## 故障排查与调试

### 常见问题诊断

**问题1：设备无响应**：

```c
// 诊断函数
void SMBus_DiagnoseNoResponse(uint8_t addr) {
    printf("\n=== Diagnosing SMBus Device 0x%02X ===\n", addr);
    
    // 1. 检查总线状态
    printf("1. Checking bus status...\n");
    if (SCL_READ() == 0) {
        printf("   ERROR: SCL stuck low!\n");
        printf("   Possible causes:\n");
        printf("   - Device holding SCL (clock stretching)\n");
        printf("   - Short circuit on SCL\n");
        printf("   - Faulty device\n");
        SMBus_BusReset();
        return;
    }
    
    if (SDA_READ() == 0) {
        printf("   ERROR: SDA stuck low!\n");
        printf("   Possible causes:\n");
        printf("   - Device holding SDA\n");
        printf("   - Short circuit on SDA\n");
        printf("   - Bus not properly terminated\n");
        SMBus_BusReset();
        return;
    }
    
    printf("   OK: Bus lines are high\n");
    
    // 2. 检查上拉电阻
    printf("2. Checking pull-up resistors...\n");
    printf("   Measure voltage on SCL and SDA\n");
    printf("   Should be close to VDD (3.3V or 5V)\n");
    
    // 3. 尝试Quick Command
    printf("3. Trying Quick Command...\n");
    if (SMBus_QuickCommand(addr, false)) {
        printf("   OK: Device responded to Quick Command\n");
    } else {
        printf("   ERROR: No response to Quick Command\n");
        printf("   Possible causes:\n");
        printf("   - Wrong device address\n");
        printf("   - Device not powered\n");
        printf("   - Device in sleep mode\n");
        printf("   - Timing issues\n");
    }
    
    // 4. 扫描总线
    printf("4. Scanning SMBus...\n");
    SMBus_ScanBus();
}

// 总线扫描
void SMBus_ScanBus(void) {
    printf("\nScanning SMBus (0x08-0x77)...\n");
    
    uint8_t found_count = 0;
    
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        if (SMBus_QuickCommand(addr, false)) {
            printf("Device found at 0x%02X\n", addr);
            found_count++;
        }
    }
    
    if (found_count == 0) {
        printf("No devices found!\n");
    } else {
        printf("Found %d device(s)\n", found_count);
    }
}
```

**问题2：PEC错误**：

```c
// PEC错误诊断
void SMBus_DiagnosePECError(uint8_t addr, uint8_t cmd) {
    printf("\n=== Diagnosing PEC Errors ===\n");
    
    // 1. 禁用PEC重试
    printf("1. Testing without PEC...\n");
    bool old_pec = smbus_driver.pec_enabled;
    smbus_driver.pec_enabled = false;
    
    uint8_t data;
    if (SMBus_ReadByte_Data(addr, cmd, &data)) {
        printf("   OK: Communication works without PEC\n");
        printf("   Data: 0x%02X\n", data);
    } else {
        printf("   ERROR: Communication fails even without PEC\n");
        smbus_driver.pec_enabled = old_pec;
        return;
    }
    
    // 2. 测试PEC计算
    printf("2. Testing PEC calculation...\n");
    uint8_t test_data[] = {0xB4, 0x10, 0x25};
    uint8_t pec = SMBus_CalculatePEC(test_data, 3);
    printf("   Test PEC: 0x%02X (expected: 0x42)\n", pec);
    
    if (pec != 0x42) {
        printf("   ERROR: PEC calculation incorrect!\n");
        printf("   Check CRC-8 implementation\n");
    }
    
    // 3. 启用PEC重试
    printf("3. Testing with PEC...\n");
    smbus_driver.pec_enabled = true;
    
    uint8_t success_count = 0;
    uint8_t fail_count = 0;
    
    for (int i = 0; i < 10; i++) {
        if (SMBus_ReadByte_Data(addr, cmd, &data)) {
            success_count++;
        } else {
            fail_count++;
        }
        HAL_Delay(10);
    }
    
    printf("   Results: %d success, %d failed\n", success_count, fail_count);
    
    if (fail_count > 0) {
        printf("   Possible causes:\n");
        printf("   - Electrical noise\n");
        printf("   - Poor signal quality\n");
        printf("   - Timing issues\n");
        printf("   - Device PEC implementation error\n");
    }
    
    smbus_driver.pec_enabled = old_pec;
}
```

**问题3：超时错误**：

```c
// 超时诊断
void SMBus_DiagnoseTimeout(uint8_t addr) {
    printf("\n=== Diagnosing Timeout Issues ===\n");
    
    // 1. 测量时钟拉伸时间
    printf("1. Measuring clock stretch time...\n");
    
    uint32_t max_stretch = 0;
    uint32_t total_stretch = 0;
    uint32_t stretch_count = 0;
    
    for (int i = 0; i < 10; i++) {
        SMBus_Start();
        
        uint32_t start = HAL_GetTick();
        SMBus_WriteByte((addr << 1) | 0);
        uint32_t stretch = HAL_GetTick() - start;
        
        if (stretch > 0) {
            total_stretch += stretch;
            stretch_count++;
            if (stretch > max_stretch) {
                max_stretch = stretch;
            }
        }
        
        SMBus_Stop();
        HAL_Delay(10);
    }
    
    if (stretch_count > 0) {
        printf("   Max stretch: %lu ms\n", max_stretch);
        printf("   Avg stretch: %lu ms\n", total_stretch / stretch_count);
        
        if (max_stretch > SMBUS_CLOCK_LOW_MAX_MS) {
            printf("   WARNING: Clock stretch exceeds SMBus limit!\n");
            printf("   SMBus limit: %d ms\n", SMBUS_CLOCK_LOW_MAX_MS);
            printf("   Device may not be SMBus compliant\n");
        }
    } else {
        printf("   No clock stretching detected\n");
    }
    
    // 2. 测试不同超时值
    printf("2. Testing different timeout values...\n");
    
    uint32_t timeout_values[] = {10, 25, 50, 100};
    
    for (int i = 0; i < 4; i++) {
        smbus_driver.timeout_ms = timeout_values[i];
        
        uint8_t data;
        bool result = SMBus_ReadByte_Data(addr, 0x00, &data);
        
        printf("   Timeout %lu ms: %s\n", 
               timeout_values[i], 
               result ? "OK" : "FAILED");
    }
    
    // 恢复默认超时
    smbus_driver.timeout_ms = SMBUS_TIMEOUT_MS;
}
```

### 调试工具

**逻辑分析仪配置**：

```
推荐设置：
- 采样率：≥1MHz（对于100kHz SMBus）
- 触发：SCL下降沿
- 解码：I2C/SMBus协议
- 显示：地址、数据、ACK/NACK、PEC

关键信号：
- SCL：时钟信号
- SDA：数据信号
- 可选：中断信号、复位信号

分析要点：
1. 检查START/STOP条件
2. 验证地址和R/W位
3. 检查ACK/NACK
4. 测量时序参数
5. 验证PEC值
6. 检查时钟拉伸
```

**软件调试输出**：

```c
// 调试级别
typedef enum {
    SMBUS_DEBUG_NONE = 0,
    SMBUS_DEBUG_ERROR,
    SMBUS_DEBUG_WARN,
    SMBUS_DEBUG_INFO,
    SMBUS_DEBUG_VERBOSE
} SMBus_DebugLevel_t;

SMBus_DebugLevel_t smbus_debug_level = SMBUS_DEBUG_INFO;

// 调试打印宏
#define SMBUS_DEBUG(level, fmt, ...) \
    do { \
        if (level <= smbus_debug_level) { \
            printf("[SMBus] " fmt "\n", ##__VA_ARGS__); \
        } \
    } while(0)

// 带调试的写字节
bool SMBus_WriteByte_Debug(uint8_t data) {
    SMBUS_DEBUG(SMBUS_DEBUG_VERBOSE, "Writing byte: 0x%02X", data);
    
    bool result = SMBus_WriteByte(data);
    
    if (result) {
        SMBUS_DEBUG(SMBUS_DEBUG_VERBOSE, "  ACK received");
    } else {
        SMBUS_DEBUG(SMBUS_DEBUG_ERROR, "  NACK received!");
    }
    
    return result;
}

// 事务跟踪
typedef struct {
    uint32_t timestamp;
    uint8_t addr;
    uint8_t cmd;
    uint8_t data[32];
    uint8_t len;
    bool is_read;
    bool success;
    uint8_t pec;
} SMBus_Transaction_t;

#define SMBUS_TRACE_SIZE 16
SMBus_Transaction_t smbus_trace[SMBUS_TRACE_SIZE];
uint8_t smbus_trace_index = 0;

// 记录事务
void SMBus_TraceTransaction(uint8_t addr, uint8_t cmd, 
                            uint8_t *data, uint8_t len,
                            bool is_read, bool success) {
    SMBus_Transaction_t *t = &smbus_trace[smbus_trace_index];
    
    t->timestamp = HAL_GetTick();
    t->addr = addr;
    t->cmd = cmd;
    t->len = len;
    t->is_read = is_read;
    t->success = success;
    
    if (len > 0 && len <= 32) {
        memcpy(t->data, data, len);
    }
    
    smbus_trace_index = (smbus_trace_index + 1) % SMBUS_TRACE_SIZE;
}

// 打印事务历史
void SMBus_PrintTrace(void) {
    printf("\n=== SMBus Transaction Trace ===\n");
    
    for (int i = 0; i < SMBUS_TRACE_SIZE; i++) {
        int idx = (smbus_trace_index + i) % SMBUS_TRACE_SIZE;
        SMBus_Transaction_t *t = &smbus_trace[idx];
        
        if (t->timestamp == 0) continue;
        
        printf("[%lu] Addr:0x%02X Cmd:0x%02X %s Len:%d %s\n",
               t->timestamp, t->addr, t->cmd,
               t->is_read ? "READ" : "WRITE",
               t->len,
               t->success ? "OK" : "FAIL");
        
        if (t->len > 0) {
            printf("  Data: ");
            for (int j = 0; j < t->len; j++) {
                printf("%02X ", t->data[j]);
            }
            printf("\n");
        }
    }
}
```

## 高级主题

### ARP（Address Resolution Protocol）

**SMBus ARP概述**：

```
ARP是SMBus 2.0引入的地址分配协议：

目的：
- 动态分配设备地址
- 解决地址冲突
- 支持热插拔

ARP设备类型：
- ARP Master：主机控制器
- ARP Slave：支持ARP的设备

ARP地址：
0x61: ARP地址（所有ARP设备响应）

ARP命令：
- Prepare to ARP
- Reset Device
- Get UDID
- Assign Address
```

**ARP实现示例**：

```c
// ARP地址和命令
#define SMBUS_ARP_ADDR          0x61

#define ARP_CMD_PREPARE         0x01
#define ARP_CMD_RESET_DEVICE    0x02
#define ARP_CMD_GET_UDID        0x03
#define ARP_CMD_ASSIGN_ADDR     0x04

// UDID结构（128位唯一标识符）
typedef struct {
    uint8_t device_capabilities;
    uint8_t version;
    uint16_t vendor_id;
    uint16_t device_id;
    uint16_t interface;
    uint16_t subsystem_vendor_id;
    uint16_t subsystem_device_id;
    uint32_t vendor_specific;
} SMBus_UDID_t;

// Prepare to ARP
bool SMBus_ARP_Prepare(void) {
    return SMBus_SendByte(SMBUS_ARP_ADDR, ARP_CMD_PREPARE);
}

// Reset Device (General Call)
bool SMBus_ARP_ResetDevice(void) {
    SMBus_Start();
    
    // 通用调用地址
    if (!SMBus_WriteByte(0x00)) {
        SMBus_Stop();
        return false;
    }
    
    // Reset命令
    if (!SMBus_WriteByte(0x06)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    
    HAL_Delay(100);  // 等待设备复位
    
    return true;
}

// Get UDID
bool SMBus_ARP_GetUDID(SMBus_UDID_t *udid) {
    uint8_t data[17];  // 16字节UDID + 1字节地址
    uint8_t count;
    
    if (!SMBus_BlockRead(SMBUS_ARP_ADDR, ARP_CMD_GET_UDID, data, &count)) {
        return false;
    }
    
    if (count != 17) {
        return false;
    }
    
    // 解析UDID
    memcpy(udid, data, 16);
    
    return true;
}

// Assign Address
bool SMBus_ARP_AssignAddress(SMBus_UDID_t *udid, uint8_t new_addr) {
    uint8_t data[17];
    
    // 准备数据：16字节UDID + 1字节新地址
    memcpy(data, udid, 16);
    data[16] = new_addr << 1;  // 地址左移1位
    
    return SMBus_BlockWrite(SMBUS_ARP_ADDR, ARP_CMD_ASSIGN_ADDR, data, 17);
}

// ARP枚举所有设备
void SMBus_ARP_EnumerateDevices(void) {
    printf("\n=== SMBus ARP Enumeration ===\n");
    
    // 1. 准备ARP
    printf("1. Preparing ARP...\n");
    if (!SMBus_ARP_Prepare()) {
        printf("   Failed to prepare ARP\n");
        return;
    }
    
    // 2. 枚举设备
    printf("2. Enumerating devices...\n");
    
    uint8_t assigned_addr = 0x10;  // 起始地址
    uint8_t device_count = 0;
    
    while (device_count < 10) {  // 最多10个设备
        SMBus_UDID_t udid;
        
        // 获取UDID
        if (!SMBus_ARP_GetUDID(&udid)) {
            break;  // 没有更多设备
        }
        
        printf("   Device %d:\n", device_count);
        printf("     Vendor ID: 0x%04X\n", udid.vendor_id);
        printf("     Device ID: 0x%04X\n", udid.device_id);
        
        // 分配地址
        if (SMBus_ARP_AssignAddress(&udid, assigned_addr)) {
            printf("     Assigned address: 0x%02X\n", assigned_addr);
            assigned_addr++;
            device_count++;
        } else {
            printf("     Failed to assign address\n");
            break;
        }
    }
    
    printf("Total devices enumerated: %d\n", device_count);
}
```

### Zone Read/Write

**Zone操作概述**：

```
Zone Read/Write是SMBus 3.0引入的高级功能：

特点：
- 支持大数据块传输（>32字节）
- 分区访问
- 提高传输效率

Zone Write格式：
S → [Addr+Wr] → A → [Cmd] → A → [Zone] → A → 
[Count] → A → [Data...] → A → P

Zone Read格式：
S → [Addr+Wr] → A → [Cmd] → A → [Zone] → A → 
Sr → [Addr+Rd] → A → [Count] → A → [Data...] → N → P
```

**Zone操作实现**：

```c
// Zone Write
bool SMBus_ZoneWrite(uint8_t addr, uint8_t cmd, uint8_t zone,
                     uint8_t *data, uint8_t count) {
    if (count == 0 || count > 255) {
        return false;
    }
    
    SMBus_Start();
    
    // 发送地址+写
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送区域号
    if (!SMBus_WriteByte(zone)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送字节计数
    if (!SMBus_WriteByte(count)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据
    for (uint8_t i = 0; i < count; i++) {
        if (!SMBus_WriteByte(data[i])) {
            SMBus_Stop();
            return false;
        }
    }
    
    SMBus_Stop();
    
    return true;
}

// Zone Read
bool SMBus_ZoneRead(uint8_t addr, uint8_t cmd, uint8_t zone,
                    uint8_t *data, uint8_t *count) {
    SMBus_Start();
    
    // 发送地址+写
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送命令
    if (!SMBus_WriteByte(cmd)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送区域号
    if (!SMBus_WriteByte(zone)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 读取字节计数
    *count = SMBus_ReadByte(true);
    
    if (*count == 0 || *count > 255) {
        SMBus_Stop();
        return false;
    }
    
    // 读取数据
    for (uint8_t i = 0; i < *count; i++) {
        bool ack = (i < *count - 1);
        data[i] = SMBus_ReadByte(ack);
    }
    
    SMBus_Stop();
    
    return true;
}
```

### Host Notify Protocol

**Host Notify概述**：

```
Host Notify允许从机主动通知主机：

特点：
- 从机作为主机发起通信
- 用于中断/事件通知
- 无需轮询

Host Notify地址：
0x08: Host Notify地址

格式：
S → [0x08+Wr] → A → [DevAddr] → A → [Data] → A → P

应用：
- 中断通知
- 事件报告
- 状态变化
```

**Host Notify实现**：

```c
// Host Notify地址
#define SMBUS_HOST_NOTIFY_ADDR  0x08

// 从机发送Host Notify（从机端实现）
bool SMBus_SendHostNotify(uint8_t device_addr, uint16_t data) {
    SMBus_Start();
    
    // 发送Host Notify地址+写
    if (!SMBus_WriteByte((SMBUS_HOST_NOTIFY_ADDR << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送设备地址
    if (!SMBus_WriteByte(device_addr << 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据（低字节）
    if (!SMBus_WriteByte(data & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送数据（高字节）
    if (!SMBus_WriteByte((data >> 8) & 0xFF)) {
        SMBus_Stop();
        return false;
    }
    
    SMBus_Stop();
    
    return true;
}

// 主机接收Host Notify（主机端实现）
typedef struct {
    uint8_t device_addr;
    uint16_t data;
    uint32_t timestamp;
} HostNotify_Event_t;

#define HOST_NOTIFY_QUEUE_SIZE 8
HostNotify_Event_t host_notify_queue[HOST_NOTIFY_QUEUE_SIZE];
uint8_t host_notify_head = 0;
uint8_t host_notify_tail = 0;

// Host Notify中断处理
void SMBus_HostNotify_IRQHandler(void) {
    uint8_t device_addr;
    uint16_t data;
    
    // 读取设备地址
    device_addr = SMBus_ReadByte(true);
    
    // 读取数据
    uint8_t low = SMBus_ReadByte(true);
    uint8_t high = SMBus_ReadByte(false);
    data = (high << 8) | low;
    
    // 添加到队列
    uint8_t next = (host_notify_tail + 1) % HOST_NOTIFY_QUEUE_SIZE;
    if (next != host_notify_head) {
        host_notify_queue[host_notify_tail].device_addr = device_addr >> 1;
        host_notify_queue[host_notify_tail].data = data;
        host_notify_queue[host_notify_tail].timestamp = HAL_GetTick();
        host_notify_tail = next;
    }
}

// 处理Host Notify事件
void SMBus_ProcessHostNotify(void) {
    while (host_notify_head != host_notify_tail) {
        HostNotify_Event_t *event = &host_notify_queue[host_notify_head];
        
        printf("Host Notify from 0x%02X: Data=0x%04X Time=%lu\n",
               event->device_addr, event->data, event->timestamp);
        
        // 处理事件
        // ...
        
        host_notify_head = (host_notify_head + 1) % HOST_NOTIFY_QUEUE_SIZE;
    }
}
```

## 性能优化

### 传输速度优化

**时钟频率选择**：

```c
// 不同速度的时序参数
typedef struct {
    uint32_t clock_freq;      // Hz
    uint32_t delay_us;        // 半周期延时
    uint32_t setup_time_us;   // 建立时间
    uint32_t hold_time_us;    // 保持时间
} SMBus_Timing_t;

// 标准速度配置
const SMBus_Timing_t smbus_timing_configs[] = {
    // 10kHz（最低速度）
    {10000, 50, 5, 5},
    
    // 50kHz（低速）
    {50000, 10, 2, 2},
    
    // 100kHz（标准速度）
    {100000, 5, 1, 1},
    
    // 400kHz（快速模式，SMBus 3.0）
    {400000, 1, 0, 0}
};

// 设置SMBus速度
void SMBus_SetSpeed(uint32_t freq_hz) {
    for (int i = 0; i < 4; i++) {
        if (smbus_timing_configs[i].clock_freq == freq_hz) {
            // 更新全局时序参数
            // ...
            printf("SMBus speed set to %lu Hz\n", freq_hz);
            return;
        }
    }
    
    printf("Unsupported frequency: %lu Hz\n", freq_hz);
}
```

### DMA传输

**使用DMA加速数据传输**：

```c
// DMA配置（以STM32为例）
void SMBus_DMA_Init(void) {
    // 配置I2C DMA
    // 注意：需要硬件I2C控制器支持
    
    // TX DMA配置
    hdma_i2c_tx.Instance = DMA1_Channel6;
    hdma_i2c_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_i2c_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_i2c_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_i2c_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_i2c_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_i2c_tx.Init.Mode = DMA_NORMAL;
    hdma_i2c_tx.Init.Priority = DMA_PRIORITY_HIGH;
    HAL_DMA_Init(&hdma_i2c_tx);
    
    // RX DMA配置
    hdma_i2c_rx.Instance = DMA1_Channel7;
    hdma_i2c_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    // ... 类似配置
    HAL_DMA_Init(&hdma_i2c_rx);
}

// DMA Block Write
bool SMBus_BlockWrite_DMA(uint8_t addr, uint8_t cmd,
                          uint8_t *data, uint8_t count) {
    // 使用硬件I2C + DMA
    HAL_I2C_Mem_Write_DMA(&hi2c1, addr << 1, cmd, 
                          I2C_MEMADD_SIZE_8BIT, data, count);
    
    // 等待传输完成
    while (HAL_I2C_GetState(&hi2c1) != HAL_I2C_STATE_READY) {
        // 可以在这里处理其他任务
    }
    
    return true;
}
```

### 批量操作优化

**减少START/STOP开销**：

```c
// 批量读取多个寄存器
bool SMBus_ReadMultipleRegisters(uint8_t addr, uint8_t start_reg,
                                 uint8_t *data, uint8_t count) {
    // 使用顺序读取，只需一次START/STOP
    SMBus_Start();
    
    // 发送地址+写
    if (!SMBus_WriteByte((addr << 1) | 0)) {
        SMBus_Stop();
        return false;
    }
    
    // 发送起始寄存器地址
    if (!SMBus_WriteByte(start_reg)) {
        SMBus_Stop();
        return false;
    }
    
    // 重复START
    SMBus_Start();
    
    // 发送地址+读
    if (!SMBus_WriteByte((addr << 1) | 1)) {
        SMBus_Stop();
        return false;
    }
    
    // 连续读取多个字节
    for (uint8_t i = 0; i < count; i++) {
        bool ack = (i < count - 1);
        data[i] = SMBus_ReadByte(ack);
    }
    
    SMBus_Stop();
    
    return true;
}

// 使用示例：读取传感器的多个寄存器
void ReadSensorData(uint8_t addr) {
    uint8_t data[6];
    
    // 一次读取6个连续寄存器
    if (SMBus_ReadMultipleRegisters(addr, 0x00, data, 6)) {
        int16_t ax = (data[0] << 8) | data[1];
        int16_t ay = (data[2] << 8) | data[3];
        int16_t az = (data[4] << 8) | data[5];
        
        printf("Accel: X=%d Y=%d Z=%d\n", ax, ay, az);
    }
}
```

### 缓存和预取

**数据缓存策略**：

```c
// 寄存器缓存
typedef struct {
    uint8_t addr;
    uint8_t reg;
    uint8_t value;
    uint32_t timestamp;
    bool valid;
} RegCache_t;

#define REG_CACHE_SIZE 16
RegCache_t reg_cache[REG_CACHE_SIZE];

// 缓存读取
bool SMBus_ReadByte_Cached(uint8_t addr, uint8_t reg, 
                           uint8_t *data, uint32_t cache_time_ms) {
    uint32_t current_time = HAL_GetTick();
    
    // 查找缓存
    for (int i = 0; i < REG_CACHE_SIZE; i++) {
        if (reg_cache[i].valid &&
            reg_cache[i].addr == addr &&
            reg_cache[i].reg == reg) {
            
            // 检查缓存是否过期
            if (current_time - reg_cache[i].timestamp < cache_time_ms) {
                *data = reg_cache[i].value;
                return true;  // 使用缓存值
            }
        }
    }
    
    // 缓存未命中，读取设备
    if (!SMBus_ReadByte_Data(addr, reg, data)) {
        return false;
    }
    
    // 更新缓存
    for (int i = 0; i < REG_CACHE_SIZE; i++) {
        if (!reg_cache[i].valid) {
            reg_cache[i].addr = addr;
            reg_cache[i].reg = reg;
            reg_cache[i].value = *data;
            reg_cache[i].timestamp = current_time;
            reg_cache[i].valid = true;
            break;
        }
    }
    
    return true;
}

// 清除缓存
void SMBus_ClearCache(void) {
    for (int i = 0; i < REG_CACHE_SIZE; i++) {
        reg_cache[i].valid = false;
    }
}
```

## 最佳实践

### 设计建议

**1. 硬件设计**：

```
上拉电阻选择：
- 计算公式：Rp = (VDD - VOL) / IOL
- 考虑总线电容
- 推荐值：4.7kΩ - 10kΩ

PCB布线：
- SCL和SDA走线尽量短
- 避免长距离走线
- 远离高频信号
- 添加地平面

ESD保护：
- 外部接口必须添加ESD保护
- 推荐使用TVS二极管
- 靠近连接器放置

电源去耦：
- 每个设备添加0.1μF去耦电容
- 靠近VCC引脚放置
- 添加10μF大电容
```

**2. 软件设计**：

```c
// 错误处理
typedef enum {
    SMBUS_OK = 0,
    SMBUS_ERROR_TIMEOUT,
    SMBUS_ERROR_NACK,
    SMBUS_ERROR_PEC,
    SMBUS_ERROR_BUS_BUSY,
    SMBUS_ERROR_INVALID_PARAM
} SMBus_Error_t;

// 统一的错误处理
SMBus_Error_t SMBus_Transaction(uint8_t addr, uint8_t cmd,
                                uint8_t *data, uint8_t len,
                                bool is_read) {
    // 参数检查
    if (len > 32) {
        return SMBUS_ERROR_INVALID_PARAM;
    }
    
    // 总线忙检查
    if (smbus_driver.busy) {
        return SMBUS_ERROR_BUS_BUSY;
    }
    
    smbus_driver.busy = true;
    
    // 执行事务
    bool result;
    if (is_read) {
        result = SMBus_BlockRead(addr, cmd, data, &len);
    } else {
        result = SMBus_BlockWrite(addr, cmd, data, len);
    }
    
    smbus_driver.busy = false;
    
    if (!result) {
        // 根据具体错误返回
        if (smbus_timeout.enabled && SMBus_IsTimeout()) {
            return SMBUS_ERROR_TIMEOUT;
        }
        return SMBUS_ERROR_NACK;
    }
    
    return SMBUS_OK;
}
```

**3. 可靠性设计**：

```c
// 重试机制
#define SMBUS_MAX_RETRIES 3

SMBus_Error_t SMBus_Transaction_Retry(uint8_t addr, uint8_t cmd,
                                      uint8_t *data, uint8_t len,
                                      bool is_read) {
    SMBus_Error_t error;
    
    for (int retry = 0; retry < SMBUS_MAX_RETRIES; retry++) {
        error = SMBus_Transaction(addr, cmd, data, len, is_read);
        
        if (error == SMBUS_OK) {
            return SMBUS_OK;
        }
        
        // 错误处理
        if (error == SMBUS_ERROR_TIMEOUT) {
            SMBus_BusReset();
        }
        
        // 延时后重试
        HAL_Delay(10);
    }
    
    return error;
}

// 看门狗保护
void SMBus_WatchdogTask(void) {
    static uint32_t last_activity = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 检查总线活动
    if (smbus_driver.busy) {
        last_activity = current_time;
    }
    
    // 如果总线长时间忙，执行复位
    if (smbus_driver.busy && 
        (current_time - last_activity > 1000)) {
        printf("SMBus watchdog timeout, resetting bus\n");
        SMBus_BusReset();
        smbus_driver.busy = false;
    }
}
```

### 调试技巧

**1. 逐步验证**：

```
验证步骤：
1. 硬件检查
   - 测量VCC电压
   - 检查SCL/SDA上拉
   - 验证连接

2. 基本通信
   - Quick Command
   - Send/Receive Byte
   - 验证ACK

3. 寄存器访问
   - Read/Write Byte
   - Read/Write Word
   - 验证数据

4. 高级功能
   - Block操作
   - PEC校验
   - 超时处理
```

**2. 常见错误模式**：

```
错误模式识别：

1. 所有设备无响应
   → 检查上拉电阻
   → 检查电源
   → 检查GPIO配置

2. 特定设备无响应
   → 检查设备地址
   → 检查设备电源
   → 检查设备使能

3. 间歇性错误
   → 检查信号质量
   → 检查电源纹波
   → 检查EMI干扰

4. PEC错误
   → 检查PEC计算
   → 检查信号完整性
   → 降低速度测试
```

## 工具与资源

### 开发工具

**1. 硬件工具**：

```
逻辑分析仪：
- Saleae Logic
- DSLogic
- PulseView + 廉价分析仪

特点：
- 支持I2C/SMBus协议解码
- 实时波形显示
- 触发和搜索功能
- 导出数据分析

SMBus适配器：
- Total Phase Aardvark
- Bus Pirate
- USB-to-SMBus适配器

功能：
- 主机模式
- 从机模拟
- 总线监控
- 脚本自动化

示波器：
- 测量信号质量
- 检查时序参数
- 分析噪声
- 验证电平
```

**2. 软件工具**：

```
Linux SMBus工具：
- i2c-tools
  - i2cdetect: 扫描总线
  - i2cdump: 转储设备寄存器
  - i2cget: 读取寄存器
  - i2cset: 写入寄存器

使用示例：
# 扫描I2C总线0
i2cdetect -y 0

# 读取设备0x48的寄存器0x00
i2cget -y 0 0x48 0x00

# 写入设备0x48的寄存器0x01，值0x60
i2cset -y 0 0x48 0x01 0x60

# 转储设备0x50的所有寄存器
i2cdump -y 0 0x50

Python库：
- smbus2
- pysmbus
- python-smbus

示例代码：
```python
from smbus2 import SMBus

# 打开I2C总线
bus = SMBus(1)

# 读取字节
data = bus.read_byte_data(0x48, 0x00)
print(f"Temperature: {data}")

# 写入字节
bus.write_byte_data(0x48, 0x01, 0x60)

# 读取字
data = bus.read_word_data(0x48, 0x00)
print(f"Value: {data}")

# 块读取
data = bus.read_i2c_block_data(0x50, 0x00, 16)
print(f"Data: {data}")

bus.close()
```

### 参考资料

**官方规范**：

```
SMBus规范文档：
1. SMBus Specification Version 3.0
   - 完整协议定义
   - 电气特性
   - 命令集
   - 下载：smbus.org

2. I2C-bus Specification
   - I2C基础协议
   - 与SMBus的关系
   - 下载：nxp.com

3. Smart Battery Data Specification
   - 智能电池协议
   - 命令定义
   - 数据格式

4. PMBus Specification
   - 电源管理总线
   - 基于SMBus
   - 电源控制命令
```

**推荐书籍**：

```
1. "I2C Manual" - NXP
   - I2C协议详解
   - 硬件设计指南
   - 应用案例

2. "The I2C Bus: From Theory to Practice"
   - 理论基础
   - 实践应用
   - 故障排查

3. "Embedded Systems Design using the TI MSP430 Series"
   - 包含I2C/SMBus章节
   - 实际项目案例
```

**在线资源**：

```
网站：
- smbus.org: SMBus官方网站
- i2c-bus.org: I2C协议资源
- embeddedrelated.com: 嵌入式论坛

教程：
- SparkFun I2C Tutorial
- Adafruit I2C/SMBus Guide
- Texas Instruments Application Notes

开源项目：
- Linux Kernel I2C/SMBus驱动
- Arduino Wire库
- Zephyr RTOS I2C驱动
```

### 常用芯片数据手册

**SMBus控制器**：

```
1. Intel ICH系列
   - 集成SMBus控制器
   - PC主板常用

2. NXP PCA9564
   - 独立SMBus控制器
   - 并行接口

3. TI TCA9548A
   - I2C/SMBus多路复用器
   - 8通道

4. Microchip MCP2221
   - USB转I2C/SMBus
   - 开发调试用
```

**SMBus设备**：

```
温度传感器：
- LM75 (NXP)
- TMP75 (TI)
- ADT7410 (Analog Devices)

电源管理：
- LTC3880 (Analog Devices)
- UCD9090 (TI)
- MAX34440 (Maxim)

EEPROM：
- 24C02/24C64 (Microchip)
- AT24C256 (Atmel)
- M24C64 (STMicroelectronics)

智能电池：
- BQ20Z75 (TI)
- MAX17055 (Maxim)
```

## 总结

### 关键要点

**SMBus核心特性**：

1. **基于I2C**：
   - 兼容I2C物理层
   - 增加系统管理特性
   - 更严格的规范

2. **超时机制**：
   - 强制25-35ms超时
   - 防止总线挂死
   - 提高可靠性

3. **PEC校验**：
   - CRC-8错误检测
   - 可选功能
   - 提高数据完整性

4. **标准命令集**：
   - Quick Command
   - Byte/Word操作
   - Block操作
   - Process Call

5. **应用领域**：
   - 电源管理
   - 电池管理
   - 温度监控
   - 系统管理

### 实现要点

**硬件设计**：
- 正确选择上拉电阻
- 添加ESD保护
- 注意PCB布线
- 电源去耦

**软件实现**：
- 实现完整的命令集
- 添加超时保护
- 支持PEC校验
- 错误处理和重试

**调试技巧**：
- 使用逻辑分析仪
- 逐步验证功能
- 识别错误模式
- 记录事务日志

### 学习路径

**初级阶段**：
1. 理解I2C基础
2. 学习SMBus与I2C的区别
3. 实现基本命令（Quick Command、Byte操作）
4. 完成简单设备驱动（温度传感器）

**中级阶段**：
1. 实现完整命令集
2. 添加PEC支持
3. 实现超时机制
4. 开发复杂设备驱动（智能电池）

**高级阶段**：
1. 实现ARP协议
2. 支持Host Notify
3. 性能优化
4. 多主机仲裁

### 下一步学习

**相关主题**：

1. **PMBus协议**：
   - 基于SMBus的电源管理协议
   - 更多电源控制命令
   - 遥测和监控功能

2. **I3C协议**：
   - 下一代I2C/SMBus
   - 更高速度
   - 更多功能

3. **CAN总线**：
   - 另一种系统管理总线
   - 更高可靠性
   - 汽车应用

4. **SPI总线**：
   - 更高速度
   - 全双工通信
   - 不同的应用场景

## 参考资料

1. System Management Bus (SMBus) Specification Version 3.0, SBS Implementers Forum, 2014
2. I2C-bus specification and user manual, NXP Semiconductors, Rev. 6, 2014
3. Smart Battery Data Specification, Revision 1.1, SBS Implementers Forum, 1998
4. Power Management Bus (PMBus) Specification, Part I and II, PMBus-IF, 2015
5. Intel 8 Series/C220 Series Chipset Family Platform Controller Hub (PCH) Datasheet
6. Texas Instruments, "Understanding the I2C Bus", Application Report SLVA704
7. Analog Devices, "SMBus and I2C: Compatible or Not?", Technical Article MS-2469
8. Microchip, "I2C Overview and Use of the PICmicro MSSP Module", AN735

## 相关主题

- [I2C硬件接口基础](../beginner/03-i2c-hardware.html)
- [I2C多路复用器应用](04-i2c-multiplexer.html)
- [PMBus电源管理](../advanced/01-pmbus-power-management.html)
- [CAN总线硬件](01-can-bus-hardware.html)
- [SPI硬件接口](../beginner/02-spi-hardware.html)
