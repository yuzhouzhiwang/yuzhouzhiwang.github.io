---
title: "I2C硬件接口实战"
description: "深入理解I2C两线总线通信接口的硬件原理、地址分配、上拉电阻配置、总线仲裁机制、多主机模式，掌握嵌入式系统中的灵活通信接口"
slug: "i2c-hardware-interface"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - I2C
  - 两线接口
  - 总线通信
  - 多主机
  - 地址分配
  - 上拉电阻
prerequisites:
  - "数字电路基础"
  - "GPIO操作"
related_contents:
  - "uart-usart-hardware-interface"
  - "spi-hardware-interface"

# 学习信息
estimated_time: 60
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
  - I2C硬件接口
  - I2C通信协议
  - 两线总线
  - 多主机模式
  - 地址分配
  - 上拉电阻配置
cover_image: ""
---

# I2C硬件接口实战

## 概述

I2C（Inter-Integrated Circuit，内部集成电路总线）是由Philips公司（现NXP）开发的一种同步、半双工、多主机的串行通信总线。I2C只需要两根信号线（SDA和SCL）就能实现多个设备之间的通信，广泛应用于MCU与传感器、EEPROM、RTC、LCD等外设的连接。

完成本教程学习后，你将能够：

- 理解I2C的工作原理和硬件特性
- 掌握I2C地址分配和寻址方式
- 学会上拉电阻的计算和配置
- 理解总线仲裁和多主机模式
- 实现STM32和Arduino的I2C通信
- 掌握常见I2C外设的应用

## 背景知识

### I2C vs SPI vs UART

| 特性 | I2C | SPI | UART |
|------|-----|-----|------|
| 通信方式 | 同步 | 同步 | 异步 |
| 数据线 | 2根（SDA/SCL） | 4根（MOSI/MISO/SCK/CS） | 2根（TX/RX） |
| 速度 | 中等（100kHz-3.4MHz） | 很快（MHz级） | 较慢（kbps级） |
| 全双工 | 否（半双工） | 是 | 是 |
| 多主机 | 支持 | 复杂 | 不支持 |
| 多从机 | 简单（地址） | 简单（独立CS） | 不支持 |
| 硬件复杂度 | 简单 | 中等 | 简单 |
| 传输距离 | 短（<1米） | 短（<1米） | 中（数米） |
| 线数优势 | ★★★ | ★ | ★★ |

### I2C的优势

**线数少**：
- 只需2根线（SDA、SCL）
- 节省GPIO资源
- 简化PCB布线

**多设备支持**：
- 支持多主机
- 支持多从机（最多127个）
- 通过地址寻址

**灵活性高**：
- 支持热插拔
- 支持动态地址分配
- 支持时钟拉伸

**成本低**：
- 硬件简单
- 无需额外芯片
- 广泛支持


## I2C工作原理

### 信号线定义

I2C使用2根信号线进行通信：

**1. SDA（Serial Data）- 串行数据线**
- 双向数据传输
- 开漏输出（Open-Drain）
- 需要外部上拉电阻
- 数据在SCL高电平期间保持稳定

**2. SCL（Serial Clock）- 串行时钟线**
- 同步时钟信号
- 由主机产生（通常）
- 开漏输出
- 需要外部上拉电阻
- 支持时钟拉伸（从机可拉低）

### 基本连接方式

**单主机多从机（最常见）**：

```
主机（MCU）              从机1        从机2        从机3
                        
VCC                     VCC          VCC          VCC
 │                       │            │            │
 ├─ Rp ─┬───────────────┼────────────┼────────────┤
 │      │               │            │            │
 │      └─ SDA ─────────┼─ SDA       │            │
 │                      │            │            │
 ├─ Rp ─┬───────────────┼────────────┼─ SDA       │
 │      │               │            │            │
 │      └─ SCL ─────────┼─ SCL ──────┼─ SCL ──────┼─ SDA
 │                      │            │            │
GND ────────────────────┴─ GND ──────┴─ GND ──────┴─ SCL
                                                    │
                                                   GND

Rp = 上拉电阻（通常4.7kΩ）
```

**关键要点**：
- SDA和SCL都需要上拉电阻
- 所有设备共享同一对SDA/SCL
- 通过地址区分不同从机
- 必须共地

### 开漏输出原理

**为什么使用开漏输出**：

```
开漏输出（Open-Drain）：
VCC
 │
 └─ Rp ─┬─ SDA/SCL
        │
    ┌───┴───┐
    │  NMOS │  ← 只能拉低，不能拉高
    └───┬───┘
        │
       GND

工作原理：
- NMOS关闭：SDA/SCL被上拉电阻拉高（逻辑1）
- NMOS导通：SDA/SCL被拉低到GND（逻辑0）
- 任何设备都可以拉低总线
- 只有所有设备都释放，总线才能为高
```

**优势**：
- 支持多主机（线与逻辑）
- 支持时钟拉伸
- 支持不同电压设备（通过上拉电阻电压）
- 防止总线冲突

### 数据传输格式

**I2C数据帧结构**：

```
起始条件 → 地址字节 → R/W位 → ACK → 数据字节 → ACK → ... → 停止条件

详细时序：
SDA: ──┐     ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐ ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐     ┌──
       └─────┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ └─────┘
       起始    A6 A5 A4 A3 A2 A1 A0 R/W ACK D7 D6 D5 D4 D3 D2 D1 D0 ACK 停止

SCL: ────┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌────
         └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
```

**起始条件（Start Condition）**：
```
SCL保持高电平时，SDA从高到低跳变

SDA: ────┐
         └─────
SCL: ──────────
         ↑
       起始条件
```

**停止条件（Stop Condition）**：
```
SCL保持高电平时，SDA从低到高跳变

SDA: ─────┌────
          │
SCL: ──────────
         ↑
       停止条件
```

**数据传输规则**：
1. SCL为高电平时，SDA必须保持稳定
2. SCL为低电平时，SDA可以改变
3. 数据在SCL上升沿后被采样
4. MSB（最高位）先传输

**应答位（ACK/NACK）**：
```
ACK（应答）：
- 接收方拉低SDA（逻辑0）
- 表示成功接收数据

NACK（非应答）：
- 接收方释放SDA（逻辑1）
- 表示接收结束或错误

SDA: ───┐   ┌───  (ACK)
        └───┘
        
SDA: ───────────  (NACK)

SCL: ─┐   ┌─┐
      └───┘ └───
```


## I2C地址分配

### 7位地址模式（最常用）

**地址格式**：
```
地址字节：A6 A5 A4 A3 A2 A1 A0 R/W

- A6-A0：7位设备地址（0x00-0x7F）
- R/W：读写位（0=写，1=读）
- 实际可用地址：0x08-0x77（保留地址除外）
```

**保留地址**：

| 地址 | 用途 |
|------|------|
| 0x00 | 通用调用地址 |
| 0x01 | CBUS地址 |
| 0x02 | 保留 |
| 0x03 | 保留 |
| 0x04-0x07 | Hs-mode主机代码 |
| 0x78-0x7F | 10位地址 |

**常见设备地址**：

| 设备类型 | 典型地址 | 可配置位 |
|---------|---------|---------|
| EEPROM (AT24C) | 0x50-0x57 | A2, A1, A0 |
| RTC (DS1307) | 0x68 | 固定 |
| RTC (PCF8563) | 0x51 | 固定 |
| 温湿度 (SHT3x) | 0x44/0x45 | ADDR引脚 |
| 加速度计 (ADXL345) | 0x53/0x1D | SDO引脚 |
| 陀螺仪 (MPU6050) | 0x68/0x69 | AD0引脚 |
| LCD (PCF8574) | 0x20-0x27 | A2, A1, A0 |
| DAC (MCP4725) | 0x60-0x67 | A2, A1, A0 |

### 10位地址模式（不常用）

**地址格式**：
```
第一字节：1 1 1 1 0 A9 A8 R/W
第二字节：A7 A6 A5 A4 A3 A2 A1 A0

- 前5位固定为11110
- A9-A0：10位设备地址（0x000-0x3FF）
- 可寻址1024个设备
```

**使用场景**：
- 需要大量设备
- 地址冲突无法解决
- 特殊应用

### 地址冲突解决

**问题**：两个设备地址相同

**解决方案**：

1. **硬件地址配置**：
```
设备1：A2=0, A1=0, A0=0 → 地址0x50
设备2：A2=0, A1=0, A0=1 → 地址0x51
设备3：A2=0, A1=1, A0=0 → 地址0x52
```

2. **使用I2C多路复用器**：
```
MCU ─── I2C ─── TCA9548A ───┬─ 通道0 ─── 设备1 (0x50)
                            ├─ 通道1 ─── 设备2 (0x50)
                            ├─ 通道2 ─── 设备3 (0x50)
                            └─ 通道7 ─── 设备8 (0x50)

TCA9548A地址：0x70-0x77
每个通道独立，可连接相同地址设备
```

3. **软件I2C（BitBang）**：
```
使用不同GPIO模拟多组I2C总线
```

### 地址扫描

**扫描总线上的所有设备**：

```c
void I2C_ScanDevices(void) {
    printf("Scanning I2C bus...\n");
    printf("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n");
    
    for (uint8_t row = 0; row < 8; row++) {
        printf("%02X: ", row * 16);
        
        for (uint8_t col = 0; col < 16; col++) {
            uint8_t addr = (row * 16) + col;
            
            // 跳过保留地址
            if (addr < 0x08 || addr > 0x77) {
                printf("   ");
                continue;
            }
            
            // 尝试通信
            if (I2C_CheckDevice(addr)) {
                printf("%02X ", addr);
            } else {
                printf("-- ");
            }
        }
        printf("\n");
    }
}

// 检查设备是否存在
bool I2C_CheckDevice(uint8_t addr) {
    // 发送起始条件和地址
    I2C_Start();
    bool ack = I2C_SendAddress(addr, I2C_WRITE);
    I2C_Stop();
    
    return ack;  // 收到ACK表示设备存在
}
```

**输出示例**：
```
Scanning I2C bus...
     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- 44 -- -- -- -- -- -- -- -- -- -- -- 
50: 50 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --

找到3个设备：
- 0x44: SHT3x温湿度传感器
- 0x50: AT24C EEPROM
- 0x68: MPU6050陀螺仪
```


## 上拉电阻配置

### 为什么需要上拉电阻

**开漏输出特性**：
- I2C使用开漏输出
- 设备只能拉低总线，不能拉高
- 需要外部上拉电阻将总线拉高

**没有上拉电阻的后果**：
- 总线始终为低电平
- 无法通信
- 数据全为0

### 上拉电阻计算

**计算公式**：

```
Rp(min) = (VCC - VOL(max)) / IOL

Rp(max) = tr / (0.8473 × Cb)

其中：
- VCC：电源电压（3.3V或5V）
- VOL(max)：最大低电平输出电压（通常0.4V）
- IOL：低电平输出电流（3mA）
- tr：上升时间（标准模式300ns，快速模式300ns，快速+模式120ns）
- Cb：总线电容（包括线路电容和设备电容）
```

**简化计算**：

| 速度模式 | 频率 | 推荐电阻值 | 适用场景 |
|---------|------|-----------|---------|
| 标准模式 | 100kHz | 4.7kΩ - 10kΩ | 长距离、多设备 |
| 快速模式 | 400kHz | 2.2kΩ - 4.7kΩ | 常规应用 |
| 快速+模式 | 1MHz | 1kΩ - 2.2kΩ | 短距离、少设备 |
| 高速模式 | 3.4MHz | 470Ω - 1kΩ | 特殊应用 |

**实际选择建议**：

```
总线长度 < 10cm，设备 < 3个：
- 100kHz: 10kΩ
- 400kHz: 4.7kΩ
- 1MHz: 2.2kΩ

总线长度 10-50cm，设备 3-7个：
- 100kHz: 4.7kΩ
- 400kHz: 2.2kΩ
- 1MHz: 1kΩ

总线长度 > 50cm，设备 > 7个：
- 100kHz: 2.2kΩ
- 400kHz: 1kΩ
- 不建议使用1MHz
```

### 上拉电阻连接

**标准连接**：

```
VCC (3.3V或5V)
 │
 ├─ 4.7kΩ ─┬─ SDA ─── 设备1 ─── 设备2 ─── 设备3
 │         │
 └─ 4.7kΩ ─┴─ SCL ─── 设备1 ─── 设备2 ─── 设备3
           │
          GND

注意：
- 只需要一组上拉电阻（通常在主机端）
- 不要在每个设备上都加上拉电阻
- 多个上拉电阻并联会降低总阻值
```

**多电压系统**：

```
3.3V MCU                    5V设备
                            
3.3V                        5V
 │                           │
 ├─ 4.7kΩ ─┬─ SDA ──────────┼─ SDA
 │         │                 │
 └─ 4.7kΩ ─┴─ SCL ──────────┼─ SCL
           │                 │
          GND ───────────────┴─ GND

说明：
- 上拉到3.3V
- 5V设备的输入通常容忍3.3V
- 5V设备的输出为开漏，不会输出5V
```

### 上拉电阻测试

**测试方法**：

```c
// 1. 测量空闲电压
// 应该接近VCC（3.3V或5V）

// 2. 测量上升时间
void Test_RiseTime(void) {
    // 使用示波器测量
    // 从10%到90%的时间应该 < 300ns（快速模式）
}

// 3. 测量下降时间
void Test_FallTime(void) {
    // 使用示波器测量
    // 从90%到10%的时间应该 < 300ns（快速模式）
}

// 4. 测试通信
void Test_Communication(void) {
    // 尝试读取设备
    uint8_t data;
    if (I2C_Read(0x50, 0x00, &data)) {
        printf("Communication OK\n");
    } else {
        printf("Communication Failed\n");
        printf("Check pull-up resistors!\n");
    }
}
```

**常见问题**：

| 现象 | 可能原因 | 解决方法 |
|------|---------|---------|
| 总线始终为低 | 缺少上拉电阻 | 添加上拉电阻 |
| 通信不稳定 | 上拉电阻过大 | 减小电阻值 |
| 波形振铃 | 上拉电阻过小 | 增大电阻值 |
| 速度慢 | 上拉电阻过大 | 减小电阻值 |
| 功耗高 | 上拉电阻过小 | 增大电阻值 |


## 总线仲裁与多主机模式

### 总线仲裁机制

**什么是总线仲裁**：
- 多个主机同时发起通信时的冲突解决机制
- 基于"线与"逻辑
- 自动、无损的仲裁过程

**仲裁原理**：

```
主机1和主机2同时发送数据：

时钟周期：  1    2    3    4    5    6    7    8
主机1发送： 1    0    1    1    0    1    0    1
主机2发送： 1    0    1    0    1    1    0    1
总线实际：  1    0    1    0    0    1    0    1
                      ↑
                   主机1检测到冲突，停止发送
                   主机2继续发送

规则：
- 0优先于1（线与逻辑）
- 发送1但检测到0的主机失败
- 失败的主机立即停止，等待总线空闲
```

**仲裁过程**：

```
1. 两个主机同时发送起始条件
2. 同时发送地址字节
3. 逐位比较：
   - 发送1，检测到1：继续
   - 发送0，检测到0：继续
   - 发送1，检测到0：失败，停止
   - 发送0，检测到1：不可能（线与逻辑）
4. 获胜的主机继续通信
5. 失败的主机等待总线空闲后重试
```

### 时钟拉伸（Clock Stretching）

**什么是时钟拉伸**：
- 从机拉低SCL，暂停通信
- 给从机更多时间处理数据
- 主机必须等待从机释放SCL

**工作原理**：

```
主机产生时钟：
SCL: ─┐   ┌─┐   ┌─┐   ┌─
      └───┘ └───┘ └───┘

从机拉伸时钟：
SCL: ─┐   ┌─┐   ┌─────────┐   ┌─
      └───┘ └───┘         └───┘
                ↑
            从机拉低SCL
            主机等待
```

**应用场景**：
- 从机处理速度慢
- 从机需要时间准备数据
- EEPROM写入操作
- ADC转换等待

**代码示例**：

```c
// 主机等待时钟拉伸
void I2C_WaitClockStretch(void) {
    uint32_t timeout = 1000;
    
    // 释放SCL
    I2C_SCL_High();
    
    // 等待从机释放SCL
    while (I2C_SCL_Read() == 0) {
        timeout--;
        if (timeout == 0) {
            // 超时错误
            return;
        }
        DelayUs(1);
    }
}
```

### 多主机配置

**硬件连接**：

```
主机1              主机2              从机1        从机2
                                      
VCC                VCC                VCC          VCC
 │                  │                  │            │
 ├─ 4.7kΩ ─┬────────┼──────────────────┼────────────┤
 │         │        │                  │            │
 │         └─ SDA ──┼─ SDA ────────────┼─ SDA       │
 │                  │                  │            │
 ├─ 4.7kΩ ─┬────────┼──────────────────┼────────────┼─ SDA
 │         │        │                  │            │
 │         └─ SCL ──┼─ SCL ────────────┼─ SCL ──────┼─ SCL
 │                  │                  │            │
GND ────────────────┴─ GND ────────────┴─ GND ──────┴─ GND

注意：
- 只需要一组上拉电阻
- 所有设备共享SDA/SCL
- 主机也可以作为从机
```

**软件实现**：

```c
// 多主机发送
bool I2C_MultiMaster_Send(uint8_t addr, uint8_t *data, uint16_t len) {
    int retry = 3;
    
    while (retry > 0) {
        // 等待总线空闲
        if (!I2C_WaitBusIdle(1000)) {
            return false;
        }
        
        // 发送起始条件
        I2C_Start();
        
        // 发送地址
        if (!I2C_SendAddress(addr, I2C_WRITE)) {
            // 仲裁失败
            I2C_Stop();
            retry--;
            HAL_Delay(10);  // 等待后重试
            continue;
        }
        
        // 发送数据
        for (uint16_t i = 0; i < len; i++) {
            if (!I2C_SendByte(data[i])) {
                I2C_Stop();
                return false;
            }
        }
        
        I2C_Stop();
        return true;
    }
    
    return false;  // 重试失败
}

// 检查总线是否空闲
bool I2C_WaitBusIdle(uint32_t timeout) {
    uint32_t start = HAL_GetTick();
    
    while ((HAL_GetTick() - start) < timeout) {
        // 检查SDA和SCL是否都为高
        if (I2C_SDA_Read() && I2C_SCL_Read()) {
            return true;
        }
        HAL_Delay(1);
    }
    
    return false;
}
```

### 多主机注意事项

**优点**：
- 灵活性高
- 可以实现对等通信
- 适合分布式系统

**缺点**：
- 软件复杂度高
- 需要处理仲裁失败
- 可能降低总线效率

**最佳实践**：
1. 尽量避免同时发起通信
2. 使用优先级机制（低地址优先）
3. 实现重试机制
4. 添加超时保护
5. 考虑使用单主机+中断方式


## I2C速度模式

### 标准速度模式

| 模式 | 频率 | 上升时间 | 下降时间 | 应用场景 |
|------|------|---------|---------|---------|
| 标准模式 | 100kHz | ≤1000ns | ≤300ns | 长距离、多设备 |
| 快速模式 | 400kHz | ≤300ns | ≤300ns | 常规应用 |
| 快速+模式 | 1MHz | ≤120ns | ≤120ns | 短距离、少设备 |
| 高速模式 | 3.4MHz | ≤80ns | ≤80ns | 特殊应用 |
| 超快速模式 | 5MHz | ≤40ns | ≤40ns | 极少使用 |

### 速度配置

**STM32配置示例**：

```c
// 标准模式（100kHz）
void I2C_Init_Standard(void) {
    // 假设APB1时钟为36MHz
    // CCR = 36MHz / (2 × 100kHz) = 180
    I2C1->CCR = 180;
    I2C1->TRISE = 37;  // (1000ns / 28ns) + 1
}

// 快速模式（400kHz）
void I2C_Init_Fast(void) {
    // CCR = 36MHz / (3 × 400kHz) = 30
    I2C1->CCR = 30 | I2C_CCR_FS;  // 快速模式
    I2C1->TRISE = 12;  // (300ns / 28ns) + 1
}

// 使用HAL库
void I2C_Init_HAL(void) {
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 400000;  // 400kHz
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}
```

**Arduino配置示例**：

```cpp
#include <Wire.h>

void setup() {
    Wire.begin();  // 默认100kHz
    
    // 设置为400kHz
    Wire.setClock(400000);
    
    // 设置为1MHz（快速+模式）
    // Wire.setClock(1000000);
}
```

### 速度选择建议

**100kHz（标准模式）**：
- 总线长度 > 50cm
- 设备数量 > 7个
- 对速度要求不高
- 兼容性最好

**400kHz（快速模式）**：
- 总线长度 < 50cm
- 设备数量 < 7个
- 常规应用
- 推荐使用

**1MHz（快速+模式）**：
- 总线长度 < 10cm
- 设备数量 < 3个
- 需要高速传输
- 需要验证设备支持

## I2C硬件设计要点

### PCB布线建议

**布线规则**：

1. **短而直**：
   - SDA/SCL走线尽量短（<30cm）
   - 避免长距离走线
   - 减少寄生电容

2. **平行走线**：
   - SDA和SCL平行走线
   - 间距保持一致（5-10mil）
   - 减少串扰

3. **地平面**：
   - 信号线下方保留完整地平面
   - 提供低阻抗回流路径
   - 减少EMI

4. **远离干扰源**：
   - 远离电源线、高速信号
   - 避免与其他信号平行走线
   - 必要时添加地线隔离

5. **上拉电阻位置**：
   ```
   推荐：靠近主机端
   VCC
    │
    ├─ Rp ─┬─ SDA ─── 主机 ─── 从机1 ─── 从机2
    │      │
    └─ Rp ─┴─ SCL
   
   不推荐：分散在各个设备
   ```

6. **去耦电容**：
   ```
   每个IC的VCC引脚附近：
   VCC ─┬─ 0.1μF ─┬─ GND
        └─ 10μF ──┘
   ```

### ESD保护

**保护电路**：

```
SDA ──┬─────────→ 外部接口
      │
      ├─ TVS二极管 ─┬─ GND
      │             │
      └─ 100Ω ──────┘

SCL ──┬─────────→ 外部接口
      │
      ├─ TVS二极管 ─┬─ GND
      │             │
      └─ 100Ω ──────┘

推荐TVS型号：
- PESD3V3L2BT（双通道）
- TPD2E001（双通道）
```

### 电平转换

**3.3V ↔ 5V电平转换**：

**方案1：使用专用芯片（推荐）**
```
3.3V侧          PCA9306          5V侧
                                 
3.3V ────────→ VREF1    VREF2 ←──── 5V
SDA ─────────→ SDA1     SDA2 ←───→ SDA
SCL ─────────→ SCL1     SCL2 ←───→ SCL
GND ─────────→ GND      GND ←───── GND

特点：
- 双向转换
- 自动方向检测
- 支持400kHz
```

**方案2：使用MOSFET（经济）**
```
3.3V侧                    5V侧
                          
3.3V                      5V
 │                         │
 ├─ 10kΩ ─┬───────────────┼─ 10kΩ
 │        │   BSS138      │
 │        ├─ G    D ───────┤
 │        │   │    │       │
SDA ──────┼─ S    S ───────┼─ SDA
          │                │
         GND              GND

SCL同样连接

特点：
- 成本低
- 双向转换
- 需要两个MOSFET
```

### 总线电容

**电容来源**：
- PCB走线电容（~1pF/cm）
- 设备输入电容（~10pF/设备）
- 连接器电容（~5pF）

**总电容计算**：
```
Cb = 走线电容 + 设备电容 × 设备数量 + 连接器电容

示例：
- 走线长度：20cm → 20pF
- 设备数量：5个 × 10pF → 50pF
- 连接器：2个 × 5pF → 10pF
- 总电容：20 + 50 + 10 = 80pF
```

**电容限制**：
- 标准模式：≤400pF
- 快速模式：≤400pF
- 快速+模式：≤550pF

**超出限制的解决方案**：
1. 减少设备数量
2. 缩短走线长度
3. 使用I2C缓冲器/中继器
4. 降低速度


## 实践示例

### 示例1：STM32 I2C硬件配置

**硬件连接**：
```
STM32F103C8T6          EEPROM (AT24C256)
PB6 (I2C1_SCL) ──────→ SCL
PB7 (I2C1_SDA) ──────→ SDA
3.3V ─┬─ 4.7kΩ ─┬────→ VCC
      └─ 4.7kΩ ─┘
GND ──────────────────→ GND
```

**寄存器配置**：

```c
// 1. 使能时钟
RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;   // I2C1时钟
RCC->APB2ENR |= RCC_APB2ENR_IOPBEN;   // GPIOB时钟

// 2. 配置GPIO（复用开漏输出）
// PB6 (SCL) - 复用开漏输出，50MHz
GPIOB->CRL &= ~(0xF << 24);
GPIOB->CRL |= (0xF << 24);  // 复用开漏，50MHz

// PB7 (SDA) - 复用开漏输出，50MHz
GPIOB->CRL &= ~(0xF << 28);
GPIOB->CRL |= (0xF << 28);

// 3. 复位I2C
I2C1->CR1 |= I2C_CR1_SWRST;
I2C1->CR1 &= ~I2C_CR1_SWRST;

// 4. 配置I2C
// 设置APB1时钟频率（36MHz）
I2C1->CR2 = 36;

// 配置时钟控制寄存器（400kHz快速模式）
// CCR = 36MHz / (3 × 400kHz) = 30
I2C1->CCR = 30 | I2C_CCR_FS;

// 配置上升时间（300ns）
I2C1->TRISE = 12;  // (300ns / 28ns) + 1

// 使能I2C
I2C1->CR1 |= I2C_CR1_PE;
```

**基本操作函数**：

```c
// 发送起始条件
void I2C_Start(void) {
    I2C1->CR1 |= I2C_CR1_START;
    while (!(I2C1->SR1 & I2C_SR1_SB));  // 等待起始条件发送完成
}

// 发送停止条件
void I2C_Stop(void) {
    I2C1->CR1 |= I2C_CR1_STOP;
}

// 发送地址
bool I2C_SendAddress(uint8_t addr, uint8_t direction) {
    I2C1->DR = (addr << 1) | direction;
    
    // 等待地址发送完成
    uint32_t timeout = 10000;
    while (!(I2C1->SR1 & I2C_SR1_ADDR) && timeout--);
    
    if (timeout == 0) {
        return false;  // 超时
    }
    
    // 清除ADDR标志
    (void)I2C1->SR1;
    (void)I2C1->SR2;
    
    return true;
}

// 发送数据
bool I2C_SendByte(uint8_t data) {
    // 等待发送缓冲区空
    uint32_t timeout = 10000;
    while (!(I2C1->SR1 & I2C_SR1_TXE) && timeout--);
    
    if (timeout == 0) {
        return false;
    }
    
    I2C1->DR = data;
    
    // 等待字节传输完成
    timeout = 10000;
    while (!(I2C1->SR1 & I2C_SR1_BTF) && timeout--);
    
    return (timeout > 0);
}

// 接收数据
uint8_t I2C_ReceiveByte(bool ack) {
    // 配置ACK
    if (ack) {
        I2C1->CR1 |= I2C_CR1_ACK;
    } else {
        I2C1->CR1 &= ~I2C_CR1_ACK;
    }
    
    // 等待接收缓冲区非空
    while (!(I2C1->SR1 & I2C_SR1_RXNE));
    
    return I2C1->DR;
}
```

**EEPROM读写示例**：

```c
// 写入单个字节
void EEPROM_WriteByte(uint16_t addr, uint8_t data) {
    I2C_Start();
    I2C_SendAddress(0x50, I2C_WRITE);  // EEPROM地址
    I2C_SendByte(addr >> 8);           // 地址高字节
    I2C_SendByte(addr & 0xFF);         // 地址低字节
    I2C_SendByte(data);                // 数据
    I2C_Stop();
    
    HAL_Delay(5);  // 等待写入完成（tWR）
}

// 读取单个字节
uint8_t EEPROM_ReadByte(uint16_t addr) {
    uint8_t data;
    
    // 写入地址
    I2C_Start();
    I2C_SendAddress(0x50, I2C_WRITE);
    I2C_SendByte(addr >> 8);
    I2C_SendByte(addr & 0xFF);
    
    // 重新起始，读取数据
    I2C_Start();
    I2C_SendAddress(0x50, I2C_READ);
    data = I2C_ReceiveByte(false);  // NACK
    I2C_Stop();
    
    return data;
}

// 页写入（最多64字节）
void EEPROM_WritePage(uint16_t addr, uint8_t *data, uint16_t len) {
    I2C_Start();
    I2C_SendAddress(0x50, I2C_WRITE);
    I2C_SendByte(addr >> 8);
    I2C_SendByte(addr & 0xFF);
    
    for (uint16_t i = 0; i < len; i++) {
        I2C_SendByte(data[i]);
    }
    
    I2C_Stop();
    HAL_Delay(5);
}

// 顺序读取
void EEPROM_ReadSequential(uint16_t addr, uint8_t *buffer, uint16_t len) {
    // 写入地址
    I2C_Start();
    I2C_SendAddress(0x50, I2C_WRITE);
    I2C_SendByte(addr >> 8);
    I2C_SendByte(addr & 0xFF);
    
    // 重新起始，读取数据
    I2C_Start();
    I2C_SendAddress(0x50, I2C_READ);
    
    for (uint16_t i = 0; i < len; i++) {
        if (i == len - 1) {
            buffer[i] = I2C_ReceiveByte(false);  // 最后一个字节NACK
        } else {
            buffer[i] = I2C_ReceiveByte(true);   // ACK
        }
    }
    
    I2C_Stop();
}
```

### 示例2：Arduino I2C配置

**硬件连接**：
```
Arduino Uno           传感器
A4 (SDA) ────────────→ SDA
A5 (SCL) ────────────→ SCL
5V ─┬─ 4.7kΩ ─┬──────→ VCC
    └─ 4.7kΩ ─┘
GND ─────────────────→ GND
```

**基本配置**：

```cpp
#include <Wire.h>

void setup() {
    Serial.begin(115200);
    
    // 初始化I2C（主机模式）
    Wire.begin();
    
    // 设置时钟频率
    Wire.setClock(400000);  // 400kHz
    
    Serial.println("I2C Ready!");
}

void loop() {
    // 扫描I2C设备
    scanI2CDevices();
    delay(5000);
}

// 扫描I2C总线
void scanI2CDevices() {
    Serial.println("Scanning I2C bus...");
    int count = 0;
    
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        uint8_t error = Wire.endTransmission();
        
        if (error == 0) {
            Serial.print("Device found at 0x");
            if (addr < 16) Serial.print("0");
            Serial.println(addr, HEX);
            count++;
        }
    }
    
    Serial.print("Found ");
    Serial.print(count);
    Serial.println(" device(s)");
}
```

**读写示例**：

```cpp
// 写入数据到设备
void writeI2C(uint8_t addr, uint8_t reg, uint8_t data) {
    Wire.beginTransmission(addr);
    Wire.write(reg);   // 寄存器地址
    Wire.write(data);  // 数据
    Wire.endTransmission();
}

// 从设备读取数据
uint8_t readI2C(uint8_t addr, uint8_t reg) {
    // 写入寄存器地址
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.endTransmission(false);  // 重复起始
    
    // 读取数据
    Wire.requestFrom(addr, (uint8_t)1);
    if (Wire.available()) {
        return Wire.read();
    }
    return 0;
}

// 读取多个字节
void readI2CMultiple(uint8_t addr, uint8_t reg, uint8_t *buffer, uint8_t len) {
    // 写入寄存器地址
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.endTransmission(false);
    
    // 读取数据
    Wire.requestFrom(addr, len);
    for (uint8_t i = 0; i < len; i++) {
        if (Wire.available()) {
            buffer[i] = Wire.read();
        }
    }
}
```

**MPU6050示例**：

```cpp
#define MPU6050_ADDR 0x68
#define PWR_MGMT_1   0x6B
#define ACCEL_XOUT_H 0x3B

void setup() {
    Serial.begin(115200);
    Wire.begin();
    Wire.setClock(400000);
    
    // 唤醒MPU6050
    writeI2C(MPU6050_ADDR, PWR_MGMT_1, 0x00);
    delay(100);
    
    Serial.println("MPU6050 initialized");
}

void loop() {
    // 读取加速度数据
    int16_t ax, ay, az;
    
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(ACCEL_XOUT_H);
    Wire.endTransmission(false);
    
    Wire.requestFrom(MPU6050_ADDR, (uint8_t)6);
    ax = (Wire.read() << 8) | Wire.read();
    ay = (Wire.read() << 8) | Wire.read();
    az = (Wire.read() << 8) | Wire.read();
    
    Serial.print("AX: "); Serial.print(ax);
    Serial.print(" AY: "); Serial.print(ay);
    Serial.print(" AZ: "); Serial.println(az);
    
    delay(100);
}
```

### 示例3：软件模拟I2C（BitBang）

```c
// 定义引脚
#define I2C_SDA_PIN   GPIO_PIN_0
#define I2C_SCL_PIN   GPIO_PIN_1
#define I2C_PORT      GPIOA

// 延时函数
void I2C_Delay(void) {
    for (volatile int i = 0; i < 20; i++);
}

// SDA控制
void I2C_SDA_Out(uint8_t val) {
    if (val) {
        GPIOA->ODR |= I2C_SDA_PIN;
    } else {
        GPIOA->ODR &= ~I2C_SDA_PIN;
    }
}

uint8_t I2C_SDA_In(void) {
    return (GPIOA->IDR & I2C_SDA_PIN) ? 1 : 0;
}

// SCL控制
void I2C_SCL_Out(uint8_t val) {
    if (val) {
        GPIOA->ODR |= I2C_SCL_PIN;
    } else {
        GPIOA->ODR &= ~I2C_SCL_PIN;
    }
}

// 初始化GPIO
void I2C_GPIO_Init(void) {
    // 使能GPIOA时钟
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    
    // SDA, SCL - 开漏输出
    GPIOA->CRL &= ~(0xFF << 0);
    GPIOA->CRL |= (0x77 << 0);  // 开漏输出，50MHz
    
    // 初始状态
    I2C_SDA_Out(1);
    I2C_SCL_Out(1);
}

// 起始条件
void I2C_Start_SW(void) {
    I2C_SDA_Out(1);
    I2C_SCL_Out(1);
    I2C_Delay();
    I2C_SDA_Out(0);  // SDA下降沿
    I2C_Delay();
    I2C_SCL_Out(0);
}

// 停止条件
void I2C_Stop_SW(void) {
    I2C_SDA_Out(0);
    I2C_SCL_Out(1);
    I2C_Delay();
    I2C_SDA_Out(1);  // SDA上升沿
    I2C_Delay();
}

// 发送一个字节
bool I2C_SendByte_SW(uint8_t data) {
    for (int i = 7; i >= 0; i--) {
        I2C_SCL_Out(0);
        I2C_Delay();
        
        // 输出数据位
        I2C_SDA_Out((data >> i) & 0x01);
        I2C_Delay();
        
        I2C_SCL_Out(1);  // 时钟高电平
        I2C_Delay();
    }
    
    // 接收ACK
    I2C_SCL_Out(0);
    I2C_SDA_Out(1);  // 释放SDA
    I2C_Delay();
    
    I2C_SCL_Out(1);
    I2C_Delay();
    
    bool ack = !I2C_SDA_In();  // ACK为低电平
    
    I2C_SCL_Out(0);
    
    return ack;
}

// 接收一个字节
uint8_t I2C_ReceiveByte_SW(bool ack) {
    uint8_t data = 0;
    
    I2C_SDA_Out(1);  // 释放SDA
    
    for (int i = 7; i >= 0; i--) {
        I2C_SCL_Out(0);
        I2C_Delay();
        
        I2C_SCL_Out(1);
        I2C_Delay();
        
        // 读取数据位
        if (I2C_SDA_In()) {
            data |= (1 << i);
        }
    }
    
    // 发送ACK/NACK
    I2C_SCL_Out(0);
    I2C_Delay();
    
    I2C_SDA_Out(ack ? 0 : 1);
    I2C_Delay();
    
    I2C_SCL_Out(1);
    I2C_Delay();
    I2C_SCL_Out(0);
    
    return data;
}
```


## 常见问题与调试

### 问题1：无法通信

**可能原因**：

1. **缺少上拉电阻**
   - 检查：用万用表测量SDA/SCL电压
   - 解决：添加4.7kΩ上拉电阻到VCC

2. **地址错误**
   - 检查：确认设备地址（7位还是8位）
   - 解决：查看数据手册，使用正确地址

3. **速度过快**
   - 检查：降低I2C时钟频率
   - 解决：从100kHz开始测试

4. **接线错误**
   - 检查：SDA/SCL是否接反
   - 解决：SDA连SDA，SCL连SCL

**调试步骤**：

```c
// 1. 检查总线电压
void Debug_CheckBusVoltage(void) {
    // 用万用表测量
    // SDA和SCL空闲时应该接近VCC
    printf("Measure SDA and SCL voltage\n");
    printf("Should be close to VCC (3.3V or 5V)\n");
}

// 2. 扫描设备
void Debug_ScanDevices(void) {
    printf("Scanning I2C bus...\n");
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        if (I2C_CheckDevice(addr)) {
            printf("Found device at 0x%02X\n", addr);
        }
    }
}

// 3. 测试读写
void Debug_TestReadWrite(uint8_t addr) {
    // 尝试写入
    I2C_Start();
    if (I2C_SendAddress(addr, I2C_WRITE)) {
        printf("Write address OK\n");
    } else {
        printf("Write address FAILED\n");
    }
    I2C_Stop();
    
    // 尝试读取
    I2C_Start();
    if (I2C_SendAddress(addr, I2C_READ)) {
        printf("Read address OK\n");
    } else {
        printf("Read address FAILED\n");
    }
    I2C_Stop();
}
```

### 问题2：数据错误

**可能原因**：

1. **时序问题**
   - 检查：用示波器观察波形
   - 解决：调整延时或降低速度

2. **干扰**
   - 检查：走线是否靠近干扰源
   - 解决：重新布线，添加滤波电容

3. **电容过大**
   - 检查：计算总线电容
   - 解决：减少设备或缩短走线

**数据验证**：

```c
// 写入并读回验证
bool Verify_WriteRead(uint8_t addr, uint8_t reg, uint8_t data) {
    // 写入
    writeI2C(addr, reg, data);
    HAL_Delay(10);
    
    // 读回
    uint8_t readback = readI2C(addr, reg);
    
    if (readback == data) {
        printf("Verify OK: 0x%02X\n", data);
        return true;
    } else {
        printf("Verify FAILED: wrote 0x%02X, read 0x%02X\n", data, readback);
        return false;
    }
}
```

### 问题3：总线挂死

**现象**：
- SDA或SCL被拉低
- 无法通信
- 复位后仍然挂死

**可能原因**：
- 从机在传输过程中被复位
- 从机等待时钟但主机已停止
- 总线仲裁失败

**解决方法**：

```c
// 总线恢复
void I2C_BusRecovery(void) {
    printf("Attempting bus recovery...\n");
    
    // 1. 禁用I2C外设
    I2C1->CR1 &= ~I2C_CR1_PE;
    
    // 2. 配置GPIO为开漏输出
    GPIOB->CRL &= ~(0xFF << 24);
    GPIOB->CRL |= (0x77 << 24);
    
    // 3. 检查SDA状态
    if (!(GPIOB->IDR & GPIO_PIN_7)) {
        printf("SDA is stuck low, sending clock pulses...\n");
        
        // 4. 发送9个时钟脉冲
        for (int i = 0; i < 9; i++) {
            GPIOB->ODR &= ~GPIO_PIN_6;  // SCL低
            HAL_Delay(1);
            GPIOB->ODR |= GPIO_PIN_6;   // SCL高
            HAL_Delay(1);
            
            // 检查SDA是否释放
            if (GPIOB->IDR & GPIO_PIN_7) {
                printf("SDA released after %d pulses\n", i + 1);
                break;
            }
        }
    }
    
    // 5. 发送停止条件
    GPIOB->ODR &= ~GPIO_PIN_7;  // SDA低
    HAL_Delay(1);
    GPIOB->ODR |= GPIO_PIN_6;   // SCL高
    HAL_Delay(1);
    GPIOB->ODR |= GPIO_PIN_7;   // SDA高（停止条件）
    HAL_Delay(1);
    
    // 6. 重新配置I2C
    GPIOB->CRL &= ~(0xFF << 24);
    GPIOB->CRL |= (0xFF << 24);  // 复用开漏
    
    I2C1->CR1 |= I2C_CR1_SWRST;
    I2C1->CR1 &= ~I2C_CR1_SWRST;
    I2C1->CR1 |= I2C_CR1_PE;
    
    printf("Bus recovery complete\n");
}
```

### 问题4：多设备冲突

**可能原因**：
- 地址冲突
- 上拉电阻不足
- 总线电容过大

**解决方案**：

```c
// 检查地址冲突
void Check_AddressConflict(void) {
    uint8_t devices[128] = {0};
    int count = 0;
    
    // 扫描所有地址
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        if (I2C_CheckDevice(addr)) {
            devices[count++] = addr;
        }
    }
    
    // 检查是否有重复
    for (int i = 0; i < count; i++) {
        for (int j = i + 1; j < count; j++) {
            if (devices[i] == devices[j]) {
                printf("Address conflict detected: 0x%02X\n", devices[i]);
            }
        }
    }
}

// 测试上拉电阻
void Test_PullUpResistor(void) {
    // 1. 测量空闲电压
    printf("Measure idle voltage on SDA and SCL\n");
    printf("Should be close to VCC\n");
    
    // 2. 测量上升时间
    printf("Use oscilloscope to measure rise time\n");
    printf("Should be < 300ns for 400kHz\n");
    
    // 3. 计算建议电阻值
    // Rp = tr / (0.8473 × Cb)
    float tr = 300e-9;  // 300ns
    float Cb = 100e-12; // 100pF（估计值）
    float Rp = tr / (0.8473 * Cb);
    printf("Recommended pull-up: %.1f kΩ\n", Rp / 1000);
}
```

## 常见I2C外设应用

### 1. EEPROM（AT24C系列）

**特点**：
- 容量：1KB - 256KB
- 地址：0x50-0x57（可配置）
- 页大小：8-64字节
- 应用：配置存储、数据记录

**基本操作**：

```c
#define EEPROM_ADDR 0x50

// 写入字节
void EEPROM_WriteByte(uint16_t addr, uint8_t data) {
    I2C_Start();
    I2C_SendAddress(EEPROM_ADDR, I2C_WRITE);
    I2C_SendByte(addr >> 8);
    I2C_SendByte(addr & 0xFF);
    I2C_SendByte(data);
    I2C_Stop();
    HAL_Delay(5);  // 写入延时
}

// 读取字节
uint8_t EEPROM_ReadByte(uint16_t addr) {
    uint8_t data;
    
    I2C_Start();
    I2C_SendAddress(EEPROM_ADDR, I2C_WRITE);
    I2C_SendByte(addr >> 8);
    I2C_SendByte(addr & 0xFF);
    
    I2C_Start();  // 重复起始
    I2C_SendAddress(EEPROM_ADDR, I2C_READ);
    data = I2C_ReceiveByte(false);
    I2C_Stop();
    
    return data;
}
```

### 2. RTC（DS1307）

**特点**：
- 实时时钟
- 地址：0x68（固定）
- 备用电池供电
- 应用：时间记录、定时任务

**基本操作**：

```c
#define DS1307_ADDR 0x68

// BCD转十进制
uint8_t BCD2DEC(uint8_t bcd) {
    return ((bcd >> 4) * 10) + (bcd & 0x0F);
}

// 十进制转BCD
uint8_t DEC2BCD(uint8_t dec) {
    return ((dec / 10) << 4) | (dec % 10);
}

// 设置时间
void DS1307_SetTime(uint8_t hour, uint8_t minute, uint8_t second) {
    I2C_Start();
    I2C_SendAddress(DS1307_ADDR, I2C_WRITE);
    I2C_SendByte(0x00);  // 秒寄存器地址
    I2C_SendByte(DEC2BCD(second));
    I2C_SendByte(DEC2BCD(minute));
    I2C_SendByte(DEC2BCD(hour));
    I2C_Stop();
}

// 读取时间
void DS1307_GetTime(uint8_t *hour, uint8_t *minute, uint8_t *second) {
    I2C_Start();
    I2C_SendAddress(DS1307_ADDR, I2C_WRITE);
    I2C_SendByte(0x00);
    
    I2C_Start();
    I2C_SendAddress(DS1307_ADDR, I2C_READ);
    *second = BCD2DEC(I2C_ReceiveByte(true) & 0x7F);
    *minute = BCD2DEC(I2C_ReceiveByte(true));
    *hour = BCD2DEC(I2C_ReceiveByte(false) & 0x3F);
    I2C_Stop();
}
```

### 3. 温湿度传感器（SHT3x）

**特点**：
- 高精度温湿度
- 地址：0x44/0x45
- 数字输出
- 应用：环境监测

**基本操作**：

```c
#define SHT3X_ADDR 0x44

// 读取温湿度
bool SHT3X_ReadTempHumidity(float *temp, float *humidity) {
    uint8_t data[6];
    
    // 发送测量命令（高重复性）
    I2C_Start();
    I2C_SendAddress(SHT3X_ADDR, I2C_WRITE);
    I2C_SendByte(0x2C);  // 命令高字节
    I2C_SendByte(0x06);  // 命令低字节
    I2C_Stop();
    
    HAL_Delay(15);  // 等待测量完成
    
    // 读取数据
    I2C_Start();
    I2C_SendAddress(SHT3X_ADDR, I2C_READ);
    for (int i = 0; i < 6; i++) {
        data[i] = I2C_ReceiveByte(i < 5);
    }
    I2C_Stop();
    
    // 计算温度
    uint16_t temp_raw = (data[0] << 8) | data[1];
    *temp = -45 + 175 * ((float)temp_raw / 65535.0);
    
    // 计算湿度
    uint16_t hum_raw = (data[3] << 8) | data[4];
    *humidity = 100 * ((float)hum_raw / 65535.0);
    
    return true;
}
```

### 4. 陀螺仪加速度计（MPU6050）

**特点**：
- 6轴IMU
- 地址：0x68/0x69
- 内置DMP
- 应用：姿态检测、运动追踪

**基本操作**：

```c
#define MPU6050_ADDR 0x68

// 初始化
void MPU6050_Init(void) {
    // 唤醒设备
    writeI2C(MPU6050_ADDR, 0x6B, 0x00);
    HAL_Delay(100);
    
    // 配置陀螺仪量程（±250°/s）
    writeI2C(MPU6050_ADDR, 0x1B, 0x00);
    
    // 配置加速度计量程（±2g）
    writeI2C(MPU6050_ADDR, 0x1C, 0x00);
}

// 读取加速度
void MPU6050_ReadAccel(int16_t *ax, int16_t *ay, int16_t *az) {
    uint8_t data[6];
    readI2CMultiple(MPU6050_ADDR, 0x3B, data, 6);
    
    *ax = (data[0] << 8) | data[1];
    *ay = (data[2] << 8) | data[3];
    *az = (data[4] << 8) | data[5];
}

// 读取陀螺仪
void MPU6050_ReadGyro(int16_t *gx, int16_t *gy, int16_t *gz) {
    uint8_t data[6];
    readI2CMultiple(MPU6050_ADDR, 0x43, data, 6);
    
    *gx = (data[0] << 8) | data[1];
    *gy = (data[2] << 8) | data[3];
    *gz = (data[4] << 8) | data[5];
}
```


## 性能优化

### 提高传输速度

**1. 使用更高时钟频率**

```c
// 从100kHz提升到400kHz
void I2C_SetFastMode(void) {
    I2C1->CR1 &= ~I2C_CR1_PE;  // 禁用I2C
    
    // 配置400kHz
    I2C1->CCR = 30 | I2C_CCR_FS;
    I2C1->TRISE = 12;
    
    I2C1->CR1 |= I2C_CR1_PE;  // 使能I2C
}

// 注意事项：
// - 确保所有设备支持400kHz
// - 减小上拉电阻（4.7kΩ → 2.2kΩ）
// - 缩短走线长度
```

**2. 使用DMA传输**

```c
// 配置DMA
void I2C_DMA_Config(void) {
    // 使能DMA时钟
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;
    
    // 配置DMA通道6（I2C1_TX）
    DMA1_Channel6->CPAR = (uint32_t)&I2C1->DR;
    DMA1_Channel6->CCR = DMA_CCR_MINC |  // 内存地址递增
                         DMA_CCR_DIR |   // 内存到外设
                         DMA_CCR_TCIE;   // 传输完成中断
    
    // 使能I2C的DMA请求
    I2C1->CR2 |= I2C_CR2_DMAEN;
}

// DMA发送
void I2C_DMA_Send(uint8_t addr, uint8_t *data, uint16_t len) {
    // 设置内存地址和数据长度
    DMA1_Channel6->CMAR = (uint32_t)data;
    DMA1_Channel6->CNDTR = len;
    
    // 发送起始条件和地址
    I2C_Start();
    I2C_SendAddress(addr, I2C_WRITE);
    
    // 使能DMA
    DMA1_Channel6->CCR |= DMA_CCR_EN;
}
```

**3. 批量传输**

```c
// 不好：逐字节传输
for (int i = 0; i < 100; i++) {
    EEPROM_WriteByte(i, data[i]);
    HAL_Delay(5);  // 每次写入延时
}
// 总时间：100 × 5ms = 500ms

// 好：页写入
for (int i = 0; i < 100; i += 64) {
    EEPROM_WritePage(i, &data[i], 64);
    HAL_Delay(5);  // 每页写入延时
}
// 总时间：2 × 5ms = 10ms
```

### 降低功耗

**1. 动态时钟控制**

```c
// 不使用时关闭I2C
void I2C_Sleep(void) {
    I2C1->CR1 &= ~I2C_CR1_PE;  // 禁用I2C
    RCC->APB1ENR &= ~RCC_APB1ENR_I2C1EN;  // 关闭时钟
}

// 使用时重新使能
void I2C_Wakeup(void) {
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;  // 使能时钟
    I2C1->CR1 |= I2C_CR1_PE;  // 使能I2C
}
```

**2. 降低时钟频率**

```c
// 低功耗模式：降低到10kHz
void I2C_LowPowerMode(void) {
    I2C1->CR1 &= ~I2C_CR1_PE;
    I2C1->CCR = 1800;  // 36MHz / (2 × 10kHz)
    I2C1->TRISE = 37;
    I2C1->CR1 |= I2C_CR1_PE;
}
```

**3. 增大上拉电阻**

```
标准模式：4.7kΩ → 功耗：VCC²/4.7kΩ = 2.3mA @ 3.3V
低功耗模式：10kΩ → 功耗：VCC²/10kΩ = 1.1mA @ 3.3V

注意：
- 上拉电阻越大，功耗越低
- 但速度会降低
- 需要权衡
```

### 提高可靠性

**1. 添加超时保护**

```c
// 带超时的发送
bool I2C_SendByte_Timeout(uint8_t data, uint32_t timeout) {
    uint32_t start = HAL_GetTick();
    
    // 等待发送缓冲区空
    while (!(I2C1->SR1 & I2C_SR1_TXE)) {
        if ((HAL_GetTick() - start) > timeout) {
            return false;  // 超时
        }
    }
    
    I2C1->DR = data;
    
    // 等待字节传输完成
    start = HAL_GetTick();
    while (!(I2C1->SR1 & I2C_SR1_BTF)) {
        if ((HAL_GetTick() - start) > timeout) {
            return false;  // 超时
        }
    }
    
    return true;
}
```

**2. 实现重试机制**

```c
#define MAX_RETRY 3

bool I2C_WriteWithRetry(uint8_t addr, uint8_t reg, uint8_t data) {
    for (int retry = 0; retry < MAX_RETRY; retry++) {
        I2C_Start();
        
        if (!I2C_SendAddress(addr, I2C_WRITE)) {
            I2C_Stop();
            HAL_Delay(10);
            continue;
        }
        
        if (!I2C_SendByte(reg)) {
            I2C_Stop();
            HAL_Delay(10);
            continue;
        }
        
        if (!I2C_SendByte(data)) {
            I2C_Stop();
            HAL_Delay(10);
            continue;
        }
        
        I2C_Stop();
        return true;  // 成功
    }
    
    return false;  // 失败
}
```

**3. 添加CRC校验**

```c
// 计算CRC8
uint8_t CRC8(uint8_t *data, uint16_t len) {
    uint8_t crc = 0xFF;
    
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    
    return crc;
}

// 带CRC的写入
bool I2C_WriteWithCRC(uint8_t addr, uint8_t *data, uint16_t len) {
    uint8_t crc = CRC8(data, len);
    
    I2C_Start();
    I2C_SendAddress(addr, I2C_WRITE);
    
    for (uint16_t i = 0; i < len; i++) {
        I2C_SendByte(data[i]);
    }
    
    I2C_SendByte(crc);  // 发送CRC
    I2C_Stop();
    
    return true;
}
```

## 总结

通过本教程学习，你已经掌握了：

- ✅ **I2C基础**：工作原理、信号线定义、开漏输出特性
- ✅ **地址分配**：7位/10位地址、地址冲突解决、设备扫描
- ✅ **上拉电阻**：计算方法、选择建议、测试方法
- ✅ **总线仲裁**：多主机模式、时钟拉伸、仲裁机制
- ✅ **硬件设计**：PCB布线、电平转换、ESD保护
- ✅ **实践应用**：STM32/Arduino配置、常见外设使用
- ✅ **故障排查**：常见问题诊断和解决方法
- ✅ **性能优化**：速度提升、功耗降低、可靠性增强

### 关键要点

1. **I2C两线制**：
   - SDA：双向数据线
   - SCL：时钟线
   - 都需要上拉电阻
   - 开漏输出

2. **地址寻址**：
   - 7位地址（最常用）
   - 通过地址区分设备
   - 最多127个设备
   - 注意保留地址

3. **上拉电阻**：
   - 必须添加
   - 标准模式：4.7kΩ
   - 快速模式：2.2kΩ
   - 根据速度和负载调整

4. **多主机支持**：
   - 自动总线仲裁
   - 线与逻辑
   - 支持时钟拉伸
   - 需要软件处理

5. **速度模式**：
   - 标准：100kHz
   - 快速：400kHz（推荐）
   - 快速+：1MHz
   - 高速：3.4MHz

## 实践建议

### 初学者练习

1. **基础通信**：
   - 实现MCU与EEPROM的I2C通信
   - 读写EEPROM数据
   - 实现地址扫描功能

2. **传感器应用**：
   - 读取温湿度传感器
   - 读取加速度计数据
   - 实现RTC时钟

3. **多设备系统**：
   - 连接2-3个I2C设备
   - 实现设备管理
   - 处理地址冲突

### 进阶项目

1. **环境监测站**：
   - 多传感器数据采集
   - EEPROM数据记录
   - RTC时间戳

2. **姿态检测系统**：
   - MPU6050数据读取
   - 姿态解算
   - 数据融合

3. **I2C总线分析仪**：
   - 实时监控I2C通信
   - 协议解析
   - 错误检测

## 延伸阅读

### 相关文章

- [UART/USART硬件接口详解](./01-uart-hardware.html) - 学习异步串行通信
- [SPI硬件接口与应用](./02-spi-hardware.html) - 学习高速同步通信
- [CAN总线硬件设计](../intermediate/01-can-bus-hardware.html) - 学习汽车和工业通信

### 外设应用

- EEPROM存储管理
- RTC实时时钟应用
- 传感器数据采集

### 高级主题

- I2C多路复用器应用
- SMBus协议详解
- PMBus电源管理

## 参考资料

### 技术标准

1. **I2C规范**：NXP UM10204 I2C-bus specification and user manual
2. **SMBus规范**：System Management Bus Specification
3. **PMBus规范**：Power Management Bus Specification

### 数据手册

1. [AT24C EEPROM](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0336.pdf)
2. [DS1307 RTC](https://datasheets.maximintegrated.com/en/ds/DS1307.pdf)
3. [SHT3x Sensor](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf)
4. [MPU6050 IMU](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf)
5. [STM32F1 Reference Manual](https://www.st.com/resource/en/reference_manual/cd00171190.pdf) - I2C章节

### 在线工具

1. [I2C地址计算器](https://www.i2c-bus.org/addressing/)
2. [上拉电阻计算器](https://www.ti.com/lit/an/slva689/slva689.pdf)
3. [Logic分析仪](https://www.saleae.com/)

### 开源项目

1. [Arduino Wire Library](https://github.com/arduino/ArduinoCore-avr/tree/master/libraries/Wire)
2. [I2C Tools](https://github.com/mozilla-b2g/i2c-tools) - Linux I2C工具
3. [TinyI2C](https://github.com/technoblogy/tiny-i2c) - 软件I2C实现

## 常见应用场景

### 1. 存储应用

**EEPROM**：
- 配置参数存储
- 校准数据保存
- 用户设置记录

**FRAM**：
- 高速非易失存储
- 无限次写入
- 低功耗应用

### 2. 时钟应用

**RTC**：
- 实时时钟
- 定时任务
- 时间戳记录

### 3. 传感器应用

**温湿度**：
- 环境监测
- 气象站
- 智能家居

**IMU**：
- 姿态检测
- 运动追踪
- 无人机控制

### 4. 显示应用

**LCD**：
- 字符显示
- I2C背包
- 简化接线

**OLED**：
- 图形显示
- 低功耗
- 高对比度

### 5. 扩展应用

**GPIO扩展**：
- PCF8574（8位）
- MCP23017（16位）
- 引脚扩展

**ADC/DAC**：
- ADS1115（16位ADC）
- MCP4725（12位DAC）
- 模拟信号处理

## 附录

### A. I2C速度对照表

| 模式 | 频率 | 上升时间 | 下降时间 | 上拉电阻 | 总线电容 |
|------|------|---------|---------|---------|---------|
| 标准 | 100kHz | ≤1000ns | ≤300ns | 4.7kΩ-10kΩ | ≤400pF |
| 快速 | 400kHz | ≤300ns | ≤300ns | 2.2kΩ-4.7kΩ | ≤400pF |
| 快速+ | 1MHz | ≤120ns | ≤120ns | 1kΩ-2.2kΩ | ≤550pF |
| 高速 | 3.4MHz | ≤80ns | ≤80ns | 470Ω-1kΩ | ≤100pF |

### B. 常见I2C设备地址表

| 设备 | 地址范围 | 默认地址 | 可配置 |
|------|---------|---------|--------|
| AT24C EEPROM | 0x50-0x57 | 0x50 | A2,A1,A0 |
| DS1307 RTC | 0x68 | 0x68 | 固定 |
| PCF8563 RTC | 0x51 | 0x51 | 固定 |
| SHT3x | 0x44-0x45 | 0x44 | ADDR |
| MPU6050 | 0x68-0x69 | 0x68 | AD0 |
| ADXL345 | 0x53,0x1D | 0x53 | SDO |
| BMP280 | 0x76-0x77 | 0x77 | SDO |
| PCF8574 LCD | 0x20-0x27 | 0x27 | A2,A1,A0 |
| MCP4725 DAC | 0x60-0x67 | 0x60 | A2,A1,A0 |
| ADS1115 ADC | 0x48-0x4B | 0x48 | ADDR |

### C. 故障排查检查清单

**硬件检查**：
- [ ] 电源电压正常（3.3V或5V）
- [ ] SDA和SCL都有上拉电阻
- [ ] 上拉电阻值合适（2.2kΩ-10kΩ）
- [ ] GND已连接
- [ ] 走线长度合理（<30cm）
- [ ] 设备地址无冲突

**软件检查**：
- [ ] I2C时钟已使能
- [ ] GPIO配置为复用开漏
- [ ] 时钟频率配置正确
- [ ] 地址格式正确（7位）
- [ ] 读写位正确（0=写，1=读）
- [ ] ACK/NACK处理正确

**测试方法**：
- [ ] 万用表测量SDA/SCL电压（应接近VCC）
- [ ] 示波器观察波形
- [ ] 逻辑分析仪抓包
- [ ] 地址扫描测试
- [ ] 回环测试

### D. 性能对比

| 参数 | I2C | SPI | UART |
|------|-----|-----|------|
| 线数 | 2 | 4+ | 2 |
| 速度 | 中（100kHz-3.4MHz） | 快（MHz级） | 慢（kbps级） |
| 全双工 | 否 | 是 | 是 |
| 多主机 | 支持 | 困难 | 不支持 |
| 多从机 | 简单（地址） | 简单（CS） | 不支持 |
| 距离 | 短（<1m） | 短（<1m） | 中（数米） |
| 功耗 | 低-中 | 中 | 低 |
| 复杂度 | 中 | 中 | 低 |
| 成本 | 低 | 中 | 低 |

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 分享你的I2C项目经验，与其他学习者交流
- 发现文档错误？请提交Issue帮助我们改进

**版权声明**：本文采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。
