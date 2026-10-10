---
title: "PMBus电源管理"
description: "深入理解PMBus（Power Management Bus）电源管理协议规范、命令集、遥测功能，掌握PMBus电源控制、监控、故障管理和配置技术"
slug: "pmbus-power-management"

# 分类信息
domain: "底层硬件层"
module: "通信接口硬件"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - PMBus协议
  - 电源管理
  - 数字电源
  - 遥测监控
  - 故障管理
  - SMBus扩展
prerequisites:
  - "SMBus协议详解"
  - "I2C硬件接口基础"
  - "开关电源设计"
related_contents:
  - "smbus-protocol-detailed"
  - "switching-power-supply-design"
  - "i2c-hardware-interface"

# 学习信息
estimated_time: 180
difficulty_score: 8

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
  - PMBus协议规范
  - 数字电源管理
  - PMBus命令集
  - 电源遥测
  - 故障管理
  - 电源配置
cover_image: ""
---

# PMBus电源管理

## 概述

PMBus（Power Management Bus，电源管理总线）是一种基于SMBus的开放标准数字电源管理协议，专门为数字电源管理和监控而设计。PMBus由PMBus-IF（PMBus Implementers Forum）维护，现已成为服务器、通信设备、工业控制等领域数字电源管理的事实标准。

PMBus在SMBus的基础上定义了标准化的命令集、数据格式和通信协议，使不同厂商的电源设备能够互操作，并提供统一的管理接口。

完成本教程学习后，你将能够：

- 理解PMBus协议规范和架构设计
- 掌握PMBus命令集和数据格式
- 实现PMBus电源控制和配置
- 掌握PMBus遥测数据读取和处理
- 实现PMBus故障检测和管理
- 开发PMBus主机控制器和从机设备
- 应用PMBus于服务器电源、DC-DC转换器等实际场景
- 理解PMBus与其他电源管理协议的区别

## 背景知识

### PMBus的诞生背景

**为什么需要PMBus**：

1. **数字电源管理需求**：
   - 传统模拟电源缺乏灵活性
   - 需要远程监控和配置能力
   - 需要精确的遥测数据
   - 需要智能故障管理

2. **标准化需求**：
   - 不同厂商电源接口不统一
   - 集成和维护成本高
   - 需要通用的管理协议
   - 需要互操作性保证

3. **系统复杂度增加**：
   - 多路电源管理
   - 动态电压调节（DVS）
   - 电源排序控制
   - 功耗优化需求

4. **可靠性要求**：
   - 实时故障检测
   - 预测性维护
   - 详细的故障日志
   - 远程诊断能力

### PMBus应用领域

**典型应用场景**：

| 应用领域 | 具体应用 | 典型设备 |
|---------|---------|---------|
| 服务器电源 | 机架电源、冗余电源 | PSU、CRPS电源 |
| 数据中心 | 电源管理、能效监控 | PDU、电源分配单元 |
| 通信设备 | 基站电源、网络设备 | DC-DC转换器、PoE |
| 工业控制 | PLC电源、工业电源 | 工业电源模块 |
| 存储系统 | 磁盘阵列电源 | 存储电源模块 |
| 计算设备 | 工作站、高性能计算 | VRM、多相电源 |

**PMBus在服务器系统中的应用**：

```
服务器主板
 │
 ├─ BMC（基板管理控制器）
 │   │
 │   ├─ PMBus控制器
 │   │   │
 │   │   ├─ PSU #1 (0x58) - 主电源
 │   │   │   ├─ 12V输出 (600W)
 │   │   │   ├─ 5V待机 (10W)
 │   │   │   └─ 遥测：电压、电流、温度、功率
 │   │   │
 │   │   ├─ PSU #2 (0x59) - 冗余电源
 │   │   │   └─ 同PSU #1
 │   │   │
 │   │   ├─ VRM #1 (0x60) - CPU电源
 │   │   │   ├─ Vcore (动态调节)
 │   │   │   └─ 多相控制
 │   │   │
 │   │   ├─ VRM #2 (0x61) - 内存电源
 │   │   │   └─ DDR电压控制
 │   │   │
 │   │   └─ DC-DC (0x62) - 外设电源
 │   │       ├─ 3.3V
 │   │       ├─ 1.8V
 │   │       └─ 1.2V
 │   │
 │   └─ 管理功能
 │       ├─ 实时监控
 │       ├─ 故障告警
 │       ├─ 电源排序
 │       └─ 功耗管理
 │
 └─ 操作系统/IPMI
     └─ 远程管理接口

特点：
- 统一的PMBus接口管理所有电源
- 实时监控电压、电流、温度、功率
- 自动故障检测和保护
- 支持热插拔和冗余
- 远程配置和诊断
```

### PMBus版本演进

**PMBus规范版本**：

1. **PMBus 1.0 (2005)**：
   - 初始版本
   - 定义基本命令集
   - 基于SMBus 2.0

2. **PMBus 1.1 (2007)**：
   - 增加新命令
   - 改进数据格式
   - 增强故障管理

3. **PMBus 1.2 (2010)**：
   - 扩展命令集
   - 增加AVSBus支持
   - 改进遥测功能

4. **PMBus 1.3 (2015)**：
   - 增加新的电源管理功能
   - 改进故障处理
   - 增强安全特性

5. **PMBus 1.3.1 (2020)**：
   - 修正和澄清
   - 增加新设备类型
   - 向后兼容

## PMBus协议架构

### 协议层次结构

**PMBus协议栈**：

```
┌─────────────────────────────────────┐
│      应用层（Application）           │
│  - 电源管理策略                      │
│  - 故障处理逻辑                      │
│  - 用户界面                          │
├─────────────────────────────────────┤
│      PMBus命令层（PMBus Commands）   │
│  - 标准命令（0x00-0x7F）            │
│  - 制造商命令（0x80-0xFF）          │
│  - 数据格式转换                      │
├─────────────────────────────────────┤
│      SMBus传输层（SMBus）            │
│  - 命令协议（Read/Write Byte/Word）  │
│  - Block Read/Write                 │
│  - PEC校验                           │
├─────────────────────────────────────┤
│      I2C物理层（I2C）                │
│  - 电气特性                          │
│  - 时序控制                          │
│  - 总线仲裁                          │
└─────────────────────────────────────┘
```

### PMBus设备类型

**设备角色分类**：

```
1. PMBus主机（Host/Controller）：
   - 系统管理控制器（BMC）
   - 嵌入式控制器（EC）
   - 微控制器（MCU）
   - 功能：发送命令、读取遥测、配置设备

2. PMBus从机（Device/Slave）：
   - 电源供应器（PSU）
   - DC-DC转换器
   - 电压调节器（VRM）
   - 功能：执行命令、报告状态、提供遥测

3. PMBus中继器（Repeater）：
   - 总线扩展器
   - 隔离器
   - 功能：扩展总线距离、隔离保护

设备地址分配：
- 0x08-0x7F：PMBus设备地址范围
- 常用地址：
  - 0x58-0x5F：电源供应器（PSU）
  - 0x60-0x6F：DC-DC转换器
  - 0x70-0x77：VRM、多相控制器
```

### PMBus通信模型

**主从通信模式**：

```
主机 → 从机：命令和配置
┌──────────┐                    ┌──────────┐
│  PMBus   │  ─── 写命令 ───→   │  电源    │
│  主机    │  ←── 应答 ────     │  设备    │
│  (BMC)   │  ─── 读遥测 ───→   │  (PSU)   │
│          │  ←── 数据 ────     │          │
└──────────┘                    └──────────┘

通信特点：
- 主机主动发起通信
- 从机被动响应
- 支持轮询和中断
- 支持多主机（仲裁）

典型通信流程：
1. 主机发送命令（如READ_VOUT）
2. 从机处理命令
3. 从机返回数据（输出电压值）
4. 主机解析数据
5. 主机根据数据采取行动
```

## PMBus数据格式

### 数据类型

**PMBus定义的数据格式**：

```
1. 无符号整数（Unsigned Integer）：
   - 8位：0-255
   - 16位：0-65535
   - 用途：计数、状态位

2. 有符号整数（Signed Integer）：
   - 8位：-128 to 127
   - 16位：-32768 to 32767
   - 用途：温度、相对值

3. 线性数据格式（Linear Format）：
   - 11位尾数 + 5位指数
   - 表示范围：±32768
   - 用途：电压、电流、功率

4. 直接数据格式（Direct Format）：
   - 用户定义的缩放因子
   - 更高精度
   - 用途：高精度测量

5. VID格式（Voltage Identification）：
   - Intel VID标准
   - 用途：CPU电压设置

6. 字符串（String）：
   - ASCII字符串
   - 用途：设备信息、序列号
```

### 线性数据格式（Linear Format）

**Linear11格式详解**：

```
格式定义：
┌─────────────────────────────────┐
│ 15  14  13  12  11│10  9  8  7  6  5  4  3  2  1  0 │
├───────────────────┼─────────────────────────────────┤
│   指数(N)         │        尾数(Y)                  │
│   5位有符号       │        11位有符号               │
└───────────────────┴─────────────────────────────────┘

计算公式：
实际值 = Y × 2^N

其中：
- N：5位有符号指数（-16 to +15）
- Y：11位有符号尾数（-1024 to +1023）

表示范围：
- 最小值：-1024 × 2^-16 = -0.015625
- 最大值：+1023 × 2^15 = +33521664
- 精度：取决于指数值

示例1：表示12.5V
Y = 12.5 / 2^0 = 12.5 ≈ 13 (取整)
N = 0
编码：0x000D (N=0, Y=13)
实际值：13 × 2^0 = 13V

示例2：表示3.3V
Y = 3.3 / 2^-2 = 13.2 ≈ 13
N = -2 (0x1E，5位补码)
编码：0xF00D (N=-2, Y=13)
实际值：13 × 2^-2 = 3.25V

示例3：表示1000W
Y = 1000 / 2^5 = 31.25 ≈ 31
N = 5
编码：0x281F (N=5, Y=31)
实际值：31 × 2^5 = 992W
```

**Linear11编解码实现**：

```c
// Linear11数据结构
typedef union {
    uint16_t raw;
    struct {
        int16_t mantissa : 11;  // 11位尾数（有符号）
        int16_t exponent : 5;   // 5位指数（有符号）
    } fields;
} Linear11_t;

// 将浮点数转换为Linear11格式
uint16_t Float_To_Linear11(float value) {
    Linear11_t linear;
    int exponent = 0;
    float mantissa = value;
    
    // 找到合适的指数
    while (mantissa > 1023.0 && exponent < 15) {
        mantissa /= 2.0;
        exponent++;
    }
    
    while (mantissa < -1024.0 && exponent < 15) {
        mantissa /= 2.0;
        exponent++;
    }
    
    while (mantissa < 512.0 && mantissa > -512.0 && exponent > -16) {
        mantissa *= 2.0;
        exponent--;
    }
    
    // 设置尾数和指数
    linear.fields.mantissa = (int16_t)mantissa;
    linear.fields.exponent = (int16_t)exponent;
    
    return linear.raw;
}

// 将Linear11格式转换为浮点数
float Linear11_To_Float(uint16_t linear_value) {
    Linear11_t linear;
    linear.raw = linear_value;
    
    // 提取尾数和指数
    int16_t mantissa = linear.fields.mantissa;
    int16_t exponent = linear.fields.exponent;
    
    // 计算实际值：Y × 2^N
    float result = (float)mantissa;
    
    if (exponent >= 0) {
        result *= (1 << exponent);
    } else {
        result /= (1 << (-exponent));
    }
    
    return result;
}

// 使用示例
void Linear11_Example(void) {
    float voltage = 12.5;
    uint16_t linear_voltage;
    float decoded_voltage;
    
    // 编码
    linear_voltage = Float_To_Linear11(voltage);
    printf("12.5V encoded as: 0x%04X\n", linear_voltage);
    
    // 解码
    decoded_voltage = Linear11_To_Float(linear_voltage);
    printf("Decoded value: %.2fV\n", decoded_voltage);
    
    // 更多示例
    float values[] = {3.3, 5.0, 12.0, 24.0, 48.0};
    for (int i = 0; i < 5; i++) {
        uint16_t encoded = Float_To_Linear11(values[i]);
        float decoded = Linear11_To_Float(encoded);
        printf("%.1fV → 0x%04X → %.2fV\n", 
               values[i], encoded, decoded);
    }
}
```

### Linear16格式

**Linear16格式详解**：

```
格式定义：
- 16位有符号尾数
- 指数存储在VOUT_MODE寄存器中
- 用于输出电压测量

VOUT_MODE寄存器格式：
┌───────────────────────────────┐
│ 7  6  5 │ 4  3  2  1  0       │
├─────────┼─────────────────────┤
│  模式   │    指数(N)          │
│  (010)  │    5位有符号        │
└─────────┴─────────────────────┘

模式值：
- 0b010：Linear模式
- 0b000：VID模式
- 0b001：Direct模式

计算公式：
实际值 = Y × 2^N

其中：
- N：从VOUT_MODE读取的指数
- Y：16位有符号尾数

示例：
VOUT_MODE = 0x13 (模式=010, N=-13)
VOUT = 0x1A00 (Y=6656)
实际电压 = 6656 × 2^-13 = 0.8125V
```

**Linear16编解码实现**：

```c
// VOUT_MODE寄存器
typedef union {
    uint8_t raw;
    struct {
        int8_t exponent : 5;  // 5位指数（有符号）
        uint8_t mode : 3;     // 3位模式
    } fields;
} VoutMode_t;

// Linear16上下文
typedef struct {
    int8_t exponent;  // 从VOUT_MODE读取的指数
} Linear16_Context_t;

// 读取VOUT_MODE并初始化上下文
bool PMBus_InitLinear16Context(uint8_t device_addr, 
                                Linear16_Context_t *context) {
    uint8_t vout_mode;
    
    // 读取VOUT_MODE寄存器
    if (!PMBus_ReadByte(device_addr, PMBUS_CMD_VOUT_MODE, &vout_mode)) {
        return false;
    }
    
    VoutMode_t mode;
    mode.raw = vout_mode;
    
    // 检查模式
    if (mode.fields.mode != 0x02) {  // 必须是Linear模式
        printf("Error: Not in Linear mode\n");
        return false;
    }
    
    // 保存指数
    context->exponent = mode.fields.exponent;
    
    printf("VOUT_MODE: 0x%02X, Exponent: %d\n", 
           vout_mode, context->exponent);
    
    return true;
}

// 将浮点数转换为Linear16格式
uint16_t Float_To_Linear16(float value, Linear16_Context_t *context) {
    // 计算尾数：Y = value / 2^N
    float mantissa = value;
    
    if (context->exponent >= 0) {
        mantissa /= (1 << context->exponent);
    } else {
        mantissa *= (1 << (-context->exponent));
    }
    
    // 限制范围
    if (mantissa > 32767.0) mantissa = 32767.0;
    if (mantissa < -32768.0) mantissa = -32768.0;
    
    return (uint16_t)((int16_t)mantissa);
}

// 将Linear16格式转换为浮点数
float Linear16_To_Float(uint16_t linear_value, 
                        Linear16_Context_t *context) {
    int16_t mantissa = (int16_t)linear_value;
    float result = (float)mantissa;
    
    // 应用指数：result = Y × 2^N
    if (context->exponent >= 0) {
        result *= (1 << context->exponent);
    } else {
        result /= (1 << (-context->exponent));
    }
    
    return result;
}

// 使用示例
void Linear16_Example(uint8_t device_addr) {
    Linear16_Context_t context;
    
    // 初始化上下文（读取VOUT_MODE）
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return;
    }
    
    // 读取输出电压
    uint16_t vout_raw;
    if (PMBus_ReadWord(device_addr, PMBUS_CMD_READ_VOUT, &vout_raw)) {
        float voltage = Linear16_To_Float(vout_raw, &context);
        printf("Output Voltage: %.4fV (raw: 0x%04X)\n", 
               voltage, vout_raw);
    }
    
    // 设置输出电压
    float target_voltage = 1.2;
    uint16_t vout_command = Float_To_Linear16(target_voltage, &context);
    PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_COMMAND, vout_command);
    printf("Set voltage to %.2fV (command: 0x%04X)\n", 
           target_voltage, vout_command);
}
```

### 直接数据格式（Direct Format）

**Direct格式详解**：

```
格式定义：
实际值 = (1/m) × (Y × 10^-R - b)

其中：
- Y：16位原始数据
- m：缩放系数（斜率）
- b：偏移量
- R：小数位数

系数存储：
- m, b, R存储在设备的系数寄存器中
- 或在设备数据手册中定义
- 主机需要知道这些系数才能转换

示例：
某电流传感器：
m = 10
b = 0
R = 3
Y = 1234 (原始读数)

实际电流 = (1/10) × (1234 × 10^-3 - 0)
         = 0.1 × 1.234
         = 0.1234 A
         = 123.4 mA
```

**Direct格式实现**：

```c
// Direct格式系数
typedef struct {
    int16_t m;  // 斜率
    int16_t b;  // 偏移
    int8_t R;   // 小数位数
} DirectFormat_Coefficients_t;

// Direct格式上下文
typedef struct {
    DirectFormat_Coefficients_t vout;   // 输出电压系数
    DirectFormat_Coefficients_t iout;   // 输出电流系数
    DirectFormat_Coefficients_t pout;   // 输出功率系数
    DirectFormat_Coefficients_t temp;   // 温度系数
} DirectFormat_Context_t;

// 读取Direct格式系数
bool PMBus_ReadDirectCoefficients(uint8_t device_addr,
                                  DirectFormat_Context_t *context) {
    // 读取VOUT系数
    uint8_t coef_data[6];
    if (PMBus_BlockRead(device_addr, PMBUS_CMD_COEFFICIENTS, 
                        coef_data, 6)) {
        context->vout.m = (coef_data[1] << 8) | coef_data[0];
        context->vout.b = (coef_data[3] << 8) | coef_data[2];
        context->vout.R = (int8_t)coef_data[4];
    }
    
    // 类似地读取其他系数...
    
    return true;
}

// 将原始数据转换为实际值
float Direct_To_Float(uint16_t raw_value, 
                      DirectFormat_Coefficients_t *coef) {
    int16_t Y = (int16_t)raw_value;
    float result;
    
    // 计算：(1/m) × (Y × 10^-R - b)
    result = (float)Y;
    
    // 应用小数位数：Y × 10^-R
    for (int i = 0; i < coef->R; i++) {
        result /= 10.0;
    }
    
    // 减去偏移：Y × 10^-R - b
    result -= (float)coef->b;
    
    // 应用斜率：(1/m) × (...)
    result /= (float)coef->m;
    
    return result;
}

// 将实际值转换为原始数据
uint16_t Float_To_Direct(float value,
                         DirectFormat_Coefficients_t *coef) {
    float Y;
    
    // 反向计算：Y = (value × m + b) × 10^R
    Y = value * (float)coef->m;
    Y += (float)coef->b;
    
    // 应用小数位数
    for (int i = 0; i < coef->R; i++) {
        Y *= 10.0;
    }
    
    // 限制范围
    if (Y > 32767.0) Y = 32767.0;
    if (Y < -32768.0) Y = -32768.0;
    
    return (uint16_t)((int16_t)Y);
}

// 使用示例
void DirectFormat_Example(uint8_t device_addr) {
    DirectFormat_Context_t context;
    
    // 读取系数
    PMBus_ReadDirectCoefficients(device_addr, &context);
    
    printf("VOUT Coefficients: m=%d, b=%d, R=%d\n",
           context.vout.m, context.vout.b, context.vout.R);
    
    // 读取输出电压
    uint16_t vout_raw;
    if (PMBus_ReadWord(device_addr, PMBUS_CMD_READ_VOUT, &vout_raw)) {
        float voltage = Direct_To_Float(vout_raw, &context.vout);
        printf("Output Voltage: %.4fV (raw: 0x%04X)\n", 
               voltage, vout_raw);
    }
    
    // 读取输出电流
    uint16_t iout_raw;
    if (PMBus_ReadWord(device_addr, PMBUS_CMD_READ_IOUT, &iout_raw)) {
        float current = Direct_To_Float(iout_raw, &context.iout);
        printf("Output Current: %.3fA (raw: 0x%04X)\n", 
               current, iout_raw);
    }
}
```


## PMBus命令集

### 命令分类

**PMBus命令按功能分类**：

```
1. 控制命令（Control Commands）：
   - OPERATION：设备操作控制
   - ON_OFF_CONFIG：开关配置
   - CLEAR_FAULTS：清除故障
   - PAGE：页面选择（多路输出）

2. 配置命令（Configuration Commands）：
   - VOUT_COMMAND：输出电压设置
   - VOUT_MAX：最大输出电压
   - VOUT_MARGIN_HIGH/LOW：电压裕度
   - FREQUENCY_SWITCH：开关频率

3. 遥测命令（Telemetry Commands）：
   - READ_VOUT：读取输出电压
   - READ_IOUT：读取输出电流
   - READ_TEMPERATURE_1/2：读取温度
   - READ_POUT：读取输出功率
   - READ_VIN：读取输入电压

4. 状态命令（Status Commands）：
   - STATUS_WORD：状态字
   - STATUS_VOUT：输出电压状态
   - STATUS_IOUT：输出电流状态
   - STATUS_TEMPERATURE：温度状态
   - STATUS_CML：通信状态

5. 限制命令（Limit Commands）：
   - VOUT_OV_FAULT_LIMIT：过压故障限制
   - VOUT_UV_FAULT_LIMIT：欠压故障限制
   - IOUT_OC_FAULT_LIMIT：过流故障限制
   - OT_FAULT_LIMIT：过温故障限制

6. 信息命令（Identification Commands）：
   - MFR_ID：制造商ID
   - MFR_MODEL：型号
   - MFR_REVISION：版本
   - MFR_SERIAL：序列号
```

### 命令编码

**PMBus命令码定义**：

```c
// PMBus标准命令码（部分）
#define PMBUS_CMD_PAGE                  0x00
#define PMBUS_CMD_OPERATION             0x01
#define PMBUS_CMD_ON_OFF_CONFIG         0x02
#define PMBUS_CMD_CLEAR_FAULTS          0x03
#define PMBUS_CMD_PHASE                 0x04
#define PMBUS_CMD_PAGE_PLUS_WRITE       0x05
#define PMBUS_CMD_PAGE_PLUS_READ        0x06

#define PMBUS_CMD_WRITE_PROTECT         0x10
#define PMBUS_CMD_STORE_DEFAULT_ALL     0x11
#define PMBUS_CMD_RESTORE_DEFAULT_ALL   0x12
#define PMBUS_CMD_STORE_USER_ALL        0x15
#define PMBUS_CMD_RESTORE_USER_ALL      0x16

#define PMBUS_CMD_CAPABILITY            0x19
#define PMBUS_CMD_QUERY                 0x1A
#define PMBUS_CMD_SMBALERT_MASK         0x1B

#define PMBUS_CMD_VOUT_MODE             0x20
#define PMBUS_CMD_VOUT_COMMAND          0x21
#define PMBUS_CMD_VOUT_TRIM             0x22
#define PMBUS_CMD_VOUT_CAL_OFFSET       0x23
#define PMBUS_CMD_VOUT_MAX              0x24
#define PMBUS_CMD_VOUT_MARGIN_HIGH      0x25
#define PMBUS_CMD_VOUT_MARGIN_LOW       0x26
#define PMBUS_CMD_VOUT_TRANSITION_RATE  0x27
#define PMBUS_CMD_VOUT_DROOP            0x28
#define PMBUS_CMD_VOUT_SCALE_LOOP       0x29
#define PMBUS_CMD_VOUT_SCALE_MONITOR    0x2A

#define PMBUS_CMD_COEFFICIENTS          0x30
#define PMBUS_CMD_POUT_MAX              0x31

#define PMBUS_CMD_FREQUENCY_SWITCH      0x33

#define PMBUS_CMD_VIN_ON                0x35
#define PMBUS_CMD_VIN_OFF               0x36

#define PMBUS_CMD_IOUT_CAL_GAIN         0x38
#define PMBUS_CMD_IOUT_CAL_OFFSET       0x39

#define PMBUS_CMD_VOUT_OV_FAULT_LIMIT   0x40
#define PMBUS_CMD_VOUT_OV_FAULT_RESPONSE 0x41
#define PMBUS_CMD_VOUT_OV_WARN_LIMIT    0x42
#define PMBUS_CMD_VOUT_UV_WARN_LIMIT    0x43
#define PMBUS_CMD_VOUT_UV_FAULT_LIMIT   0x44
#define PMBUS_CMD_VOUT_UV_FAULT_RESPONSE 0x45

#define PMBUS_CMD_IOUT_OC_FAULT_LIMIT   0x46
#define PMBUS_CMD_IOUT_OC_FAULT_RESPONSE 0x47
#define PMBUS_CMD_IOUT_OC_LV_FAULT_LIMIT 0x48
#define PMBUS_CMD_IOUT_OC_LV_FAULT_RESPONSE 0x49
#define PMBUS_CMD_IOUT_OC_WARN_LIMIT    0x4A
#define PMBUS_CMD_IOUT_UC_FAULT_LIMIT   0x4B
#define PMBUS_CMD_IOUT_UC_FAULT_RESPONSE 0x4C

#define PMBUS_CMD_OT_FAULT_LIMIT        0x4F
#define PMBUS_CMD_OT_FAULT_RESPONSE     0x50
#define PMBUS_CMD_OT_WARN_LIMIT         0x51
#define PMBUS_CMD_UT_WARN_LIMIT         0x52
#define PMBUS_CMD_UT_FAULT_LIMIT        0x53
#define PMBUS_CMD_UT_FAULT_RESPONSE     0x54
#define PMBUS_CMD_VIN_OV_FAULT_LIMIT    0x55
#define PMBUS_CMD_VIN_OV_FAULT_RESPONSE 0x56
#define PMBUS_CMD_VIN_OV_WARN_LIMIT     0x57
#define PMBUS_CMD_VIN_UV_WARN_LIMIT     0x58
#define PMBUS_CMD_VIN_UV_FAULT_LIMIT    0x59
#define PMBUS_CMD_VIN_UV_FAULT_RESPONSE 0x5A

#define PMBUS_CMD_IIN_OC_FAULT_LIMIT    0x5B
#define PMBUS_CMD_IIN_OC_FAULT_RESPONSE 0x5C
#define PMBUS_CMD_IIN_OC_WARN_LIMIT     0x5D

#define PMBUS_CMD_POWER_GOOD_ON         0x5E
#define PMBUS_CMD_POWER_GOOD_OFF        0x5F
#define PMBUS_CMD_TON_DELAY             0x60
#define PMBUS_CMD_TON_RISE              0x61
#define PMBUS_CMD_TON_MAX_FAULT_LIMIT   0x62
#define PMBUS_CMD_TON_MAX_FAULT_RESPONSE 0x63
#define PMBUS_CMD_TOFF_DELAY            0x64
#define PMBUS_CMD_TOFF_FALL             0x65
#define PMBUS_CMD_TOFF_MAX_WARN_LIMIT   0x66

#define PMBUS_CMD_STATUS_BYTE           0x78
#define PMBUS_CMD_STATUS_WORD           0x79
#define PMBUS_CMD_STATUS_VOUT           0x7A
#define PMBUS_CMD_STATUS_IOUT           0x7B
#define PMBUS_CMD_STATUS_INPUT          0x7C
#define PMBUS_CMD_STATUS_TEMPERATURE    0x7D
#define PMBUS_CMD_STATUS_CML            0x7E
#define PMBUS_CMD_STATUS_OTHER          0x7F
#define PMBUS_CMD_STATUS_MFR_SPECIFIC   0x80

#define PMBUS_CMD_READ_VIN              0x88
#define PMBUS_CMD_READ_IIN              0x89
#define PMBUS_CMD_READ_VCAP             0x8A
#define PMBUS_CMD_READ_VOUT             0x8B
#define PMBUS_CMD_READ_IOUT             0x8C
#define PMBUS_CMD_READ_TEMPERATURE_1    0x8D
#define PMBUS_CMD_READ_TEMPERATURE_2    0x8E
#define PMBUS_CMD_READ_TEMPERATURE_3    0x8F
#define PMBUS_CMD_READ_FAN_SPEED_1      0x90
#define PMBUS_CMD_READ_FAN_SPEED_2      0x91
#define PMBUS_CMD_READ_FAN_SPEED_3      0x92
#define PMBUS_CMD_READ_FAN_SPEED_4      0x93
#define PMBUS_CMD_READ_DUTY_CYCLE       0x94
#define PMBUS_CMD_READ_FREQUENCY        0x95
#define PMBUS_CMD_READ_POUT             0x96
#define PMBUS_CMD_READ_PIN              0x97

#define PMBUS_CMD_PMBUS_REVISION        0x98
#define PMBUS_CMD_MFR_ID                0x99
#define PMBUS_CMD_MFR_MODEL             0x9A
#define PMBUS_CMD_MFR_REVISION          0x9B
#define PMBUS_CMD_MFR_LOCATION          0x9C
#define PMBUS_CMD_MFR_DATE              0x9D
#define PMBUS_CMD_MFR_SERIAL            0x9E

// 制造商特定命令（0xA0-0xFF）
#define PMBUS_CMD_MFR_SPECIFIC_00       0xD0
// ... 更多制造商命令
```


### 核心控制命令

**OPERATION命令（0x01）**：

```
功能：控制设备操作状态

数据格式：1字节

位定义：
┌───────────────────────────────────────┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0       │
├───┼───┼───┼───┼───┼───┼───┼─────────┤
│   │   │   │   │   │   │   │ 操作状态 │
└───┴───┴───┴───┴───┴───┴───┴─────────┘

操作状态值：
0x00：立即关闭（Immediate Off）
0x40：软关闭（Soft Off）
0x80：开启（On）
0xC0：裕度测试低（Margin Low）
0xE0：裕度测试高（Margin High）

使用场景：
- 开启/关闭电源
- 进入裕度测试模式
- 紧急关闭
```

**实现代码**：

```c
// OPERATION命令值
typedef enum {
    PMBUS_OP_OFF_IMMEDIATE = 0x00,
    PMBUS_OP_OFF_SOFT      = 0x40,
    PMBUS_OP_ON            = 0x80,
    PMBUS_OP_MARGIN_LOW    = 0xC0,
    PMBUS_OP_MARGIN_HIGH   = 0xE0
} PMBus_Operation_t;

// 设置设备操作状态
bool PMBus_SetOperation(uint8_t device_addr, PMBus_Operation_t operation) {
    return PMBus_SendByte(device_addr, PMBUS_CMD_OPERATION, operation);
}

// 读取设备操作状态
bool PMBus_GetOperation(uint8_t device_addr, PMBus_Operation_t *operation) {
    uint8_t value;
    if (PMBus_ReadByte(device_addr, PMBUS_CMD_OPERATION, &value)) {
        *operation = (PMBus_Operation_t)value;
        return true;
    }
    return false;
}

// 开启电源
bool PMBus_PowerOn(uint8_t device_addr) {
    printf("Turning on power...\n");
    return PMBus_SetOperation(device_addr, PMBUS_OP_ON);
}

// 关闭电源（软关闭）
bool PMBus_PowerOff(uint8_t device_addr) {
    printf("Turning off power (soft)...\n");
    return PMBus_SetOperation(device_addr, PMBUS_OP_OFF_SOFT);
}

// 紧急关闭
bool PMBus_EmergencyShutdown(uint8_t device_addr) {
    printf("Emergency shutdown!\n");
    return PMBus_SetOperation(device_addr, PMBUS_OP_OFF_IMMEDIATE);
}

// 进入裕度测试模式
bool PMBus_MarginTest(uint8_t device_addr, bool high) {
    PMBus_Operation_t op = high ? PMBUS_OP_MARGIN_HIGH : PMBUS_OP_MARGIN_LOW;
    printf("Entering margin test mode (%s)...\n", high ? "HIGH" : "LOW");
    return PMBus_SetOperation(device_addr, op);
}
```

**ON_OFF_CONFIG命令（0x02）**：

```
功能：配置开关行为

数据格式：1字节

位定义：
┌───────────────────────────────────────────────┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0               │
├───┼───┼───┼───┼───┼───┼───┼─────────────────┤
│   │   │   │   │PU │CMD│PIN│ CTRL引脚功能    │
└───┴───┴───┴───┴───┴───┴───┴─────────────────┘

位说明：
- Bit 4 (PU)：上电时的操作
  0：保持关闭
  1：自动开启
  
- Bit 3 (CMD)：OPERATION命令控制
  0：禁用
  1：启用
  
- Bit 2 (PIN)：CONTROL引脚控制
  0：禁用
  1：启用
  
- Bit 1-0：CONTROL引脚功能
  00：引脚无效
  01：引脚高电平开启
  10：引脚低电平开启
  11：保留

常用配置：
0x1E：上电自动开启，支持命令和引脚控制
0x16：保持关闭，支持命令和引脚控制
0x0A：仅支持命令控制
```

**实现代码**：

```c
// ON_OFF_CONFIG位定义
#define PMBUS_ON_OFF_PU_MASK    0x10
#define PMBUS_ON_OFF_CMD_MASK   0x08
#define PMBUS_ON_OFF_PIN_MASK   0x04
#define PMBUS_ON_OFF_CTRL_MASK  0x03

typedef struct {
    bool power_up_on;       // 上电自动开启
    bool cmd_control;       // 命令控制使能
    bool pin_control;       // 引脚控制使能
    uint8_t pin_function;   // 引脚功能（0-3）
} PMBus_OnOffConfig_t;

// 配置开关行为
bool PMBus_ConfigureOnOff(uint8_t device_addr, PMBus_OnOffConfig_t *config) {
    uint8_t value = 0;
    
    if (config->power_up_on) {
        value |= PMBUS_ON_OFF_PU_MASK;
    }
    
    if (config->cmd_control) {
        value |= PMBUS_ON_OFF_CMD_MASK;
    }
    
    if (config->pin_control) {
        value |= PMBUS_ON_OFF_PIN_MASK;
    }
    
    value |= (config->pin_function & PMBUS_ON_OFF_CTRL_MASK);
    
    return PMBus_SendByte(device_addr, PMBUS_CMD_ON_OFF_CONFIG, value);
}

// 读取开关配置
bool PMBus_GetOnOffConfig(uint8_t device_addr, PMBus_OnOffConfig_t *config) {
    uint8_t value;
    
    if (!PMBus_ReadByte(device_addr, PMBUS_CMD_ON_OFF_CONFIG, &value)) {
        return false;
    }
    
    config->power_up_on = (value & PMBUS_ON_OFF_PU_MASK) != 0;
    config->cmd_control = (value & PMBUS_ON_OFF_CMD_MASK) != 0;
    config->pin_control = (value & PMBUS_ON_OFF_PIN_MASK) != 0;
    config->pin_function = value & PMBUS_ON_OFF_CTRL_MASK;
    
    return true;
}

// 使用示例
void OnOffConfig_Example(uint8_t device_addr) {
    PMBus_OnOffConfig_t config;
    
    // 配置：上电自动开启，支持命令和引脚控制
    config.power_up_on = true;
    config.cmd_control = true;
    config.pin_control = true;
    config.pin_function = 1;  // 引脚高电平开启
    
    if (PMBus_ConfigureOnOff(device_addr, &config)) {
        printf("ON_OFF_CONFIG set successfully\n");
    }
    
    // 读取并显示配置
    if (PMBus_GetOnOffConfig(device_addr, &config)) {
        printf("Power-up: %s\n", config.power_up_on ? "ON" : "OFF");
        printf("CMD control: %s\n", config.cmd_control ? "Enabled" : "Disabled");
        printf("PIN control: %s\n", config.pin_control ? "Enabled" : "Disabled");
        printf("PIN function: %d\n", config.pin_function);
    }
}
```

**CLEAR_FAULTS命令（0x03）**：

```
功能：清除所有故障状态

数据格式：Send Byte（无数据）

使用方法：
- 发送此命令清除所有故障标志
- 清除STATUS寄存器中的故障位
- 允许设备从故障状态恢复

注意事项：
- 必须先解决故障原因
- 某些故障可能需要断电才能清除
- 清除后设备可能自动重启
```

**实现代码**：

```c
// 清除故障
bool PMBus_ClearFaults(uint8_t device_addr) {
    printf("Clearing all faults...\n");
    return PMBus_SendByte(device_addr, PMBUS_CMD_CLEAR_FAULTS, 0x00);
}

// 清除故障并验证
bool PMBus_ClearFaultsAndVerify(uint8_t device_addr) {
    uint16_t status_before, status_after;
    
    // 读取清除前的状态
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_STATUS_WORD, &status_before)) {
        return false;
    }
    
    printf("Status before clear: 0x%04X\n", status_before);
    
    // 清除故障
    if (!PMBus_ClearFaults(device_addr)) {
        return false;
    }
    
    // 延时等待清除完成
    HAL_Delay(100);
    
    // 读取清除后的状态
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_STATUS_WORD, &status_after)) {
        return false;
    }
    
    printf("Status after clear: 0x%04X\n", status_after);
    
    // 检查是否成功清除
    if (status_after == 0x0000) {
        printf("All faults cleared successfully\n");
        return true;
    } else {
        printf("Warning: Some faults remain: 0x%04X\n", status_after);
        return false;
    }
}
```

**PAGE命令（0x00）**：

```
功能：选择多路输出的页面

数据格式：1字节

页面值：
0x00-0x1F：页面0-31（最多32路输出）
0xFF：所有页面（广播）

使用场景：
- 多路输出电源
- 每路输出独立配置
- 批量配置所有输出

注意：
- 发送PAGE命令后，后续命令作用于选定页面
- PAGE=0xFF时，命令作用于所有页面
- 单路输出设备可能不支持PAGE命令
```

**实现代码**：

```c
// 选择页面
bool PMBus_SelectPage(uint8_t device_addr, uint8_t page) {
    if (page > 0x1F && page != 0xFF) {
        printf("Error: Invalid page number %d\n", page);
        return false;
    }
    
    return PMBus_SendByte(device_addr, PMBUS_CMD_PAGE, page);
}

// 读取当前页面
bool PMBus_GetCurrentPage(uint8_t device_addr, uint8_t *page) {
    return PMBus_ReceiveByte(device_addr, PMBUS_CMD_PAGE, page);
}

// 多页面操作示例
void MultiPage_Example(uint8_t device_addr) {
    // 配置第0路输出为3.3V
    PMBus_SelectPage(device_addr, 0);
    PMBus_SetVoltage(device_addr, 3.3);
    
    // 配置第1路输出为5.0V
    PMBus_SelectPage(device_addr, 1);
    PMBus_SetVoltage(device_addr, 5.0);
    
    // 配置第2路输出为12.0V
    PMBus_SelectPage(device_addr, 2);
    PMBus_SetVoltage(device_addr, 12.0);
    
    // 开启所有输出
    PMBus_SelectPage(device_addr, 0xFF);  // 选择所有页面
    PMBus_PowerOn(device_addr);
    
    printf("All outputs configured and enabled\n");
}
```


### 电压配置命令

**VOUT_COMMAND命令（0x21）**：

```
功能：设置输出电压目标值

数据格式：2字节（Linear16或Direct格式）

使用方法：
1. 确定数据格式（读取VOUT_MODE）
2. 将目标电压转换为对应格式
3. 写入VOUT_COMMAND
4. 设备调节输出到目标电压

精度：
- 取决于数据格式和指数
- 通常0.1%-1%精度
- 某些设备支持更高精度

限制：
- 不能超过VOUT_MAX
- 受硬件能力限制
- 可能有步进限制
```

**实现代码**：

```c
// 设置输出电压
bool PMBus_SetVoltage(uint8_t device_addr, float voltage) {
    Linear16_Context_t context;
    uint16_t vout_command;
    
    // 初始化Linear16上下文
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 转换为Linear16格式
    vout_command = Float_To_Linear16(voltage, &context);
    
    // 写入VOUT_COMMAND
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_COMMAND, vout_command)) {
        return false;
    }
    
    printf("Set voltage to %.3fV (command: 0x%04X)\n", voltage, vout_command);
    
    return true;
}

// 读取电压设置
bool PMBus_GetVoltageCommand(uint8_t device_addr, float *voltage) {
    Linear16_Context_t context;
    uint16_t vout_command;
    
    // 初始化上下文
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 读取VOUT_COMMAND
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_VOUT_COMMAND, &vout_command)) {
        return false;
    }
    
    // 转换为浮点数
    *voltage = Linear16_To_Float(vout_command, &context);
    
    return true;
}

// 电压调节示例
void VoltageControl_Example(uint8_t device_addr) {
    float target_voltage = 3.3;
    float actual_voltage;
    
    // 设置目标电压
    if (PMBus_SetVoltage(device_addr, target_voltage)) {
        printf("Voltage command set to %.2fV\n", target_voltage);
        
        // 等待稳定
        HAL_Delay(100);
        
        // 读取实际输出电压
        if (PMBus_ReadVoltage(device_addr, &actual_voltage)) {
            printf("Actual output voltage: %.3fV\n", actual_voltage);
            
            // 计算误差
            float error = (actual_voltage - target_voltage) / target_voltage * 100;
            printf("Error: %.2f%%\n", error);
        }
    }
}
```

**VOUT_MAX命令（0x24）**：

```
功能：设置最大输出电压限制

数据格式：2字节（Linear16或Direct格式）

作用：
- 保护负载免受过压损坏
- 限制VOUT_COMMAND的最大值
- 硬件保护的软件补充

典型值：
- 3.3V输出：VOUT_MAX = 3.6V
- 5V输出：VOUT_MAX = 5.5V
- 12V输出：VOUT_MAX = 13.2V
```

**实现代码**：

```c
// 设置最大电压限制
bool PMBus_SetVoltageMax(uint8_t device_addr, float max_voltage) {
    Linear16_Context_t context;
    uint16_t vout_max;
    
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    vout_max = Float_To_Linear16(max_voltage, &context);
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_MAX, vout_max)) {
        return false;
    }
    
    printf("Set maximum voltage to %.2fV\n", max_voltage);
    
    return true;
}

// 读取最大电压限制
bool PMBus_GetVoltageMax(uint8_t device_addr, float *max_voltage) {
    Linear16_Context_t context;
    uint16_t vout_max;
    
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_VOUT_MAX, &vout_max)) {
        return false;
    }
    
    *max_voltage = Linear16_To_Float(vout_max, &context);
    
    return true;
}
```

**VOUT_MARGIN_HIGH/LOW命令（0x25/0x26）**：

```
功能：设置裕度测试电压

数据格式：2字节（Linear16或Direct格式）

裕度测试：
- MARGIN_HIGH：高于标称电压的测试值（如+5%）
- MARGIN_LOW：低于标称电压的测试值（如-5%）
- 用于测试负载在电压变化时的稳定性

使用流程：
1. 设置VOUT_MARGIN_HIGH和VOUT_MARGIN_LOW
2. 发送OPERATION命令进入裕度测试模式
3. 观察负载行为
4. 返回正常模式

示例：
标称电压：3.3V
MARGIN_HIGH：3.465V (+5%)
MARGIN_LOW：3.135V (-5%)
```

**实现代码**：

```c
// 配置裕度测试
bool PMBus_ConfigureMarginTest(uint8_t device_addr, 
                                float nominal_voltage,
                                float margin_percent) {
    Linear16_Context_t context;
    float margin_high, margin_low;
    uint16_t high_value, low_value;
    
    // 初始化上下文
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 计算裕度电压
    margin_high = nominal_voltage * (1.0 + margin_percent / 100.0);
    margin_low = nominal_voltage * (1.0 - margin_percent / 100.0);
    
    printf("Configuring margin test:\n");
    printf("  Nominal: %.3fV\n", nominal_voltage);
    printf("  High: %.3fV (+%.1f%%)\n", margin_high, margin_percent);
    printf("  Low: %.3fV (-%.1f%%)\n", margin_low, margin_percent);
    
    // 转换并写入
    high_value = Float_To_Linear16(margin_high, &context);
    low_value = Float_To_Linear16(margin_low, &context);
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_MARGIN_HIGH, high_value)) {
        return false;
    }
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_MARGIN_LOW, low_value)) {
        return false;
    }
    
    return true;
}

// 执行裕度测试
bool PMBus_RunMarginTest(uint8_t device_addr, uint32_t test_duration_ms) {
    float voltage;
    
    printf("\n=== Starting Margin Test ===\n");
    
    // 测试高裕度
    printf("\nTesting MARGIN HIGH...\n");
    PMBus_SetOperation(device_addr, PMBUS_OP_MARGIN_HIGH);
    HAL_Delay(test_duration_ms);
    
    if (PMBus_ReadVoltage(device_addr, &voltage)) {
        printf("Voltage at MARGIN HIGH: %.3fV\n", voltage);
    }
    
    // 测试低裕度
    printf("\nTesting MARGIN LOW...\n");
    PMBus_SetOperation(device_addr, PMBUS_OP_MARGIN_LOW);
    HAL_Delay(test_duration_ms);
    
    if (PMBus_ReadVoltage(device_addr, &voltage)) {
        printf("Voltage at MARGIN LOW: %.3fV\n", voltage);
    }
    
    // 返回正常模式
    printf("\nReturning to normal operation...\n");
    PMBus_SetOperation(device_addr, PMBUS_OP_ON);
    HAL_Delay(100);
    
    if (PMBus_ReadVoltage(device_addr, &voltage)) {
        printf("Voltage at normal: %.3fV\n", voltage);
    }
    
    printf("\n=== Margin Test Complete ===\n");
    
    return true;
}
```

### 遥测读取命令

**READ_VOUT命令（0x8B）**：

```
功能：读取实际输出电压

数据格式：2字节（Linear16或Direct格式）

特点：
- 实时测量值
- 高精度ADC采样
- 通常10-12位分辨率
- 更新频率：10-100Hz

应用：
- 电压监控
- 闭环控制
- 故障检测
- 数据记录
```

**实现代码**：

```c
// 读取输出电压
bool PMBus_ReadVoltage(uint8_t device_addr, float *voltage) {
    Linear16_Context_t context;
    uint16_t vout_raw;
    
    // 初始化上下文
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 读取原始数据
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_READ_VOUT, &vout_raw)) {
        return false;
    }
    
    // 转换为浮点数
    *voltage = Linear16_To_Float(vout_raw, &context);
    
    return true;
}

// 连续监控电压
void PMBus_MonitorVoltage(uint8_t device_addr, uint32_t duration_ms) {
    uint32_t start_time = HAL_GetTick();
    float voltage;
    float min_voltage = 999.0;
    float max_voltage = 0.0;
    float sum_voltage = 0.0;
    uint32_t sample_count = 0;
    
    printf("Monitoring voltage for %lu ms...\n", duration_ms);
    
    while (HAL_GetTick() - start_time < duration_ms) {
        if (PMBus_ReadVoltage(device_addr, &voltage)) {
            // 更新统计
            if (voltage < min_voltage) min_voltage = voltage;
            if (voltage > max_voltage) max_voltage = voltage;
            sum_voltage += voltage;
            sample_count++;
            
            printf("%.3fV ", voltage);
            if (sample_count % 10 == 0) printf("\n");
        }
        
        HAL_Delay(100);  // 100ms采样间隔
    }
    
    // 打印统计信息
    printf("\n\n=== Voltage Statistics ===\n");
    printf("Samples: %lu\n", sample_count);
    printf("Min: %.3fV\n", min_voltage);
    printf("Max: %.3fV\n", max_voltage);
    printf("Avg: %.3fV\n", sum_voltage / sample_count);
    printf("Range: %.3fV\n", max_voltage - min_voltage);
}
```

**READ_IOUT命令（0x8C）**：

```
功能：读取实际输出电流

数据格式：2字节（Linear11格式）

特点：
- 实时电流测量
- 通常使用电流检测电阻
- 精度：1-5%
- 用于过流保护和功率计算

应用：
- 负载监控
- 过流检测
- 功率计算
- 效率分析
```

**实现代码**：

```c
// 读取输出电流
bool PMBus_ReadCurrent(uint8_t device_addr, float *current) {
    uint16_t iout_raw;
    
    // 读取原始数据
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_READ_IOUT, &iout_raw)) {
        return false;
    }
    
    // 转换为浮点数（Linear11格式）
    *current = Linear11_To_Float(iout_raw);
    
    return true;
}

// 读取输出功率
bool PMBus_ReadPower(uint8_t device_addr, float *power) {
    uint16_t pout_raw;
    
    // 读取原始数据
    if (!PMBus_ReadWord(device_addr, PMBUS_CMD_READ_POUT, &pout_raw)) {
        return false;
    }
    
    // 转换为浮点数（Linear11格式）
    *power = Linear11_To_Float(pout_raw);
    
    return true;
}

// 计算效率
float PMBus_CalculateEfficiency(uint8_t device_addr) {
    float vin, iin, vout, iout;
    float pin, pout, efficiency;
    
    // 读取输入参数
    if (!PMBus_ReadInputVoltage(device_addr, &vin)) return 0.0;
    if (!PMBus_ReadInputCurrent(device_addr, &iin)) return 0.0;
    
    // 读取输出参数
    if (!PMBus_ReadVoltage(device_addr, &vout)) return 0.0;
    if (!PMBus_ReadCurrent(device_addr, &iout)) return 0.0;
    
    // 计算功率
    pin = vin * iin;
    pout = vout * iout;
    
    // 计算效率
    if (pin > 0.0) {
        efficiency = (pout / pin) * 100.0;
    } else {
        efficiency = 0.0;
    }
    
    printf("\n=== Power Analysis ===\n");
    printf("Input: %.2fV × %.3fA = %.2fW\n", vin, iin, pin);
    printf("Output: %.2fV × %.3fA = %.2fW\n", vout, iout, pout);
    printf("Efficiency: %.2f%%\n", efficiency);
    
    return efficiency;
}
```

**READ_TEMPERATURE命令（0x8D/0x8E/0x8F）**：

```
功能：读取温度传感器数据

命令：
- READ_TEMPERATURE_1 (0x8D)：主温度传感器
- READ_TEMPERATURE_2 (0x8E)：次温度传感器
- READ_TEMPERATURE_3 (0x8F)：第三温度传感器

数据格式：2字节（Linear11格式）

单位：摄氏度（°C）

传感器位置：
- 温度1：通常是功率器件温度
- 温度2：通常是环境温度
- 温度3：通常是输出端温度

应用：
- 过温保护
- 风扇控制
- 降额运行
- 可靠性监控
```

**实现代码**：

```c
// 读取温度
bool PMBus_ReadTemperature(uint8_t device_addr, uint8_t sensor, float *temperature) {
    uint8_t cmd;
    uint16_t temp_raw;
    
    // 选择温度传感器命令
    switch (sensor) {
        case 1:
            cmd = PMBUS_CMD_READ_TEMPERATURE_1;
            break;
        case 2:
            cmd = PMBUS_CMD_READ_TEMPERATURE_2;
            break;
        case 3:
            cmd = PMBUS_CMD_READ_TEMPERATURE_3;
            break;
        default:
            return false;
    }
    
    // 读取原始数据
    if (!PMBus_ReadWord(device_addr, cmd, &temp_raw)) {
        return false;
    }
    
    // 转换为浮点数（Linear11格式）
    *temperature = Linear11_To_Float(temp_raw);
    
    return true;
}

// 读取所有温度
void PMBus_ReadAllTemperatures(uint8_t device_addr) {
    float temp1, temp2, temp3;
    
    printf("\n=== Temperature Readings ===\n");
    
    if (PMBus_ReadTemperature(device_addr, 1, &temp1)) {
        printf("Temperature 1 (Power): %.1f°C\n", temp1);
    }
    
    if (PMBus_ReadTemperature(device_addr, 2, &temp2)) {
        printf("Temperature 2 (Ambient): %.1f°C\n", temp2);
    }
    
    if (PMBus_ReadTemperature(device_addr, 3, &temp3)) {
        printf("Temperature 3 (Output): %.1f°C\n", temp3);
    }
}

// 温度监控和保护
void PMBus_TemperatureMonitor(uint8_t device_addr, float threshold) {
    float temperature;
    
    while (1) {
        if (PMBus_ReadTemperature(device_addr, 1, &temperature)) {
            printf("Temperature: %.1f°C\n", temperature);
            
            // 检查过温
            if (temperature > threshold) {
                printf("WARNING: Over temperature! (%.1f°C > %.1f°C)\n",
                       temperature, threshold);
                
                // 降额运行或关闭
                if (temperature > threshold + 10.0) {
                    printf("CRITICAL: Emergency shutdown!\n");
                    PMBus_EmergencyShutdown(device_addr);
                    break;
                }
            }
        }
        
        HAL_Delay(1000);  // 1秒采样间隔
    }
}
```


### 状态监控命令

**STATUS_WORD命令（0x79）**：

```
功能：读取设备总体状态

数据格式：2字节

位定义：
┌─────────────────────────────────────────────────────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │ 9 │ 8 │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 │
├────┼────┼────┼────┼────┼────┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│VOUT│IOUT│INPUT│MFR │POWER│CML│   │TEMP│OFF│BUSY│OTHER│UNKNOWN│NONE│
└────┴────┴────┴────┴────┴────┴───┴────┴────┴────┴────┴────────┴────┘

位说明：
Bit 15 (VOUT)：输出电压故障/警告
Bit 14 (IOUT)：输出电流故障/警告
Bit 13 (INPUT)：输入故障/警告
Bit 12 (MFR)：制造商特定故障
Bit 11 (POWER_GOOD#)：电源好信号无效
Bit 10 (FANS)：风扇故障/警告
Bit 9 (OTHER)：其他故障/警告
Bit 8 (UNKNOWN)：未知故障
Bit 7 (BUSY)：设备忙
Bit 6 (OFF)：设备关闭
Bit 5 (VOUT_OV)：输出过压故障
Bit 4 (IOUT_OC)：输出过流故障
Bit 3 (VIN_UV)：输入欠压故障
Bit 2 (TEMPERATURE)：温度故障/警告
Bit 1 (CML)：通信/内存/逻辑故障
Bit 0 (NONE)：无故障（保留）

使用：
- 快速检查设备状态
- 确定需要读取哪些详细状态寄存器
- 故障诊断的起点
```

**实现代码**：

```c
// STATUS_WORD位定义
#define PMBUS_STATUS_VOUT       (1 << 15)
#define PMBUS_STATUS_IOUT       (1 << 14)
#define PMBUS_STATUS_INPUT      (1 << 13)
#define PMBUS_STATUS_MFR        (1 << 12)
#define PMBUS_STATUS_POWER_GOOD (1 << 11)
#define PMBUS_STATUS_FANS       (1 << 10)
#define PMBUS_STATUS_OTHER      (1 << 9)
#define PMBUS_STATUS_UNKNOWN    (1 << 8)
#define PMBUS_STATUS_BUSY       (1 << 7)
#define PMBUS_STATUS_OFF        (1 << 6)
#define PMBUS_STATUS_VOUT_OV    (1 << 5)
#define PMBUS_STATUS_IOUT_OC    (1 << 4)
#define PMBUS_STATUS_VIN_UV     (1 << 3)
#define PMBUS_STATUS_TEMPERATURE (1 << 2)
#define PMBUS_STATUS_CML        (1 << 1)

// 读取状态字
bool PMBus_ReadStatusWord(uint8_t device_addr, uint16_t *status) {
    return PMBus_ReadWord(device_addr, PMBUS_CMD_STATUS_WORD, status);
}

// 解析并打印状态
void PMBus_PrintStatus(uint16_t status) {
    printf("\n=== Device Status (0x%04X) ===\n", status);
    
    if (status == 0x0000) {
        printf("No faults or warnings\n");
        return;
    }
    
    if (status & PMBUS_STATUS_VOUT) {
        printf("[VOUT] Output voltage fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_IOUT) {
        printf("[IOUT] Output current fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_INPUT) {
        printf("[INPUT] Input fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_MFR) {
        printf("[MFR] Manufacturer specific fault\n");
    }
    
    if (status & PMBUS_STATUS_POWER_GOOD) {
        printf("[POWER_GOOD] Power good signal deasserted\n");
    }
    
    if (status & PMBUS_STATUS_FANS) {
        printf("[FANS] Fan fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_OTHER) {
        printf("[OTHER] Other fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_UNKNOWN) {
        printf("[UNKNOWN] Unknown fault\n");
    }
    
    if (status & PMBUS_STATUS_BUSY) {
        printf("[BUSY] Device is busy\n");
    }
    
    if (status & PMBUS_STATUS_OFF) {
        printf("[OFF] Device is off\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_OV) {
        printf("[VOUT_OV] Output overvoltage fault\n");
    }
    
    if (status & PMBUS_STATUS_IOUT_OC) {
        printf("[IOUT_OC] Output overcurrent fault\n");
    }
    
    if (status & PMBUS_STATUS_VIN_UV) {
        printf("[VIN_UV] Input undervoltage fault\n");
    }
    
    if (status & PMBUS_STATUS_TEMPERATURE) {
        printf("[TEMPERATURE] Temperature fault/warning\n");
    }
    
    if (status & PMBUS_STATUS_CML) {
        printf("[CML] Communication/Memory/Logic fault\n");
    }
}

// 检查设备健康状态
bool PMBus_CheckHealth(uint8_t device_addr) {
    uint16_t status;
    
    if (!PMBus_ReadStatusWord(device_addr, &status)) {
        printf("Error: Failed to read status\n");
        return false;
    }
    
    PMBus_PrintStatus(status);
    
    // 检查关键故障
    uint16_t critical_faults = PMBUS_STATUS_VOUT_OV | 
                               PMBUS_STATUS_IOUT_OC |
                               PMBUS_STATUS_VIN_UV |
                               PMBUS_STATUS_TEMPERATURE;
    
    if (status & critical_faults) {
        printf("\nCRITICAL: Device has critical faults!\n");
        return false;
    }
    
    if (status == 0x0000) {
        printf("\nDevice is healthy\n");
        return true;
    }
    
    printf("\nDevice has warnings but is operational\n");
    return true;
}
```

**STATUS_VOUT命令（0x7A）**：

```
功能：读取输出电压详细状态

数据格式：1字节

位定义：
┌───────────────────────────────────────────┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0           │
├───┼───┼───┼───┼───┼───┼───┼─────────────┤
│OV │OV │UV │UV │MAX│   │   │VOUT跟踪错误 │
│故障│警告│警告│故障│   │   │             │
└───┴───┴───┴───┴───┴───┴───┴─────────────┘

位说明：
Bit 7：过压故障（VOUT > OV_FAULT_LIMIT）
Bit 6：过压警告（VOUT > OV_WARN_LIMIT）
Bit 5：欠压警告（VOUT < UV_WARN_LIMIT）
Bit 4：欠压故障（VOUT < UV_FAULT_LIMIT）
Bit 3：VOUT达到最大值
Bit 2-1：保留
Bit 0：VOUT跟踪错误
```

**实现代码**：

```c
// STATUS_VOUT位定义
#define PMBUS_STATUS_VOUT_OV_FAULT  (1 << 7)
#define PMBUS_STATUS_VOUT_OV_WARN   (1 << 6)
#define PMBUS_STATUS_VOUT_UV_WARN   (1 << 5)
#define PMBUS_STATUS_VOUT_UV_FAULT  (1 << 4)
#define PMBUS_STATUS_VOUT_MAX       (1 << 3)
#define PMBUS_STATUS_VOUT_TRACKING  (1 << 0)

// 读取输出电压状态
bool PMBus_ReadVoutStatus(uint8_t device_addr, uint8_t *status) {
    return PMBus_ReadByte(device_addr, PMBUS_CMD_STATUS_VOUT, status);
}

// 解析输出电压状态
void PMBus_PrintVoutStatus(uint8_t status) {
    printf("\n=== VOUT Status (0x%02X) ===\n", status);
    
    if (status == 0x00) {
        printf("Output voltage is normal\n");
        return;
    }
    
    if (status & PMBUS_STATUS_VOUT_OV_FAULT) {
        printf("[FAULT] Output overvoltage\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_OV_WARN) {
        printf("[WARNING] Output voltage high\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_UV_WARN) {
        printf("[WARNING] Output voltage low\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_UV_FAULT) {
        printf("[FAULT] Output undervoltage\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_MAX) {
        printf("[INFO] Output at maximum\n");
    }
    
    if (status & PMBUS_STATUS_VOUT_TRACKING) {
        printf("[ERROR] Voltage tracking error\n");
    }
}
```

**STATUS_IOUT命令（0x7B）**：

```
功能：读取输出电流详细状态

数据格式：1字节

位定义：
┌───────────────────────────────────────────┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0           │
├───┼───┼───┼───┼───┼───┼───┼─────────────┤
│OC │OC │OC │UC │UC │   │POUT│POUT        │
│故障│LV │警告│故障│警告│   │OV  │OP       │
└───┴───┴───┴───┴───┴───┴───┴─────────────┘

位说明：
Bit 7：过流故障
Bit 6：低压过流故障
Bit 5：过流警告
Bit 4：欠流故障
Bit 3：欠流警告
Bit 2：保留
Bit 1：输出功率过载
Bit 0：输出功率限制运行
```

**实现代码**：

```c
// STATUS_IOUT位定义
#define PMBUS_STATUS_IOUT_OC_FAULT    (1 << 7)
#define PMBUS_STATUS_IOUT_OC_LV_FAULT (1 << 6)
#define PMBUS_STATUS_IOUT_OC_WARN     (1 << 5)
#define PMBUS_STATUS_IOUT_UC_FAULT    (1 << 4)
#define PMBUS_STATUS_IOUT_UC_WARN     (1 << 3)
#define PMBUS_STATUS_POUT_OP_FAULT    (1 << 1)
#define PMBUS_STATUS_POUT_OP_WARN     (1 << 0)

// 读取输出电流状态
bool PMBus_ReadIoutStatus(uint8_t device_addr, uint8_t *status) {
    return PMBus_ReadByte(device_addr, PMBUS_CMD_STATUS_IOUT, status);
}

// 解析输出电流状态
void PMBus_PrintIoutStatus(uint8_t status) {
    printf("\n=== IOUT Status (0x%02X) ===\n", status);
    
    if (status == 0x00) {
        printf("Output current is normal\n");
        return;
    }
    
    if (status & PMBUS_STATUS_IOUT_OC_FAULT) {
        printf("[FAULT] Output overcurrent\n");
    }
    
    if (status & PMBUS_STATUS_IOUT_OC_LV_FAULT) {
        printf("[FAULT] Output overcurrent at low voltage\n");
    }
    
    if (status & PMBUS_STATUS_IOUT_OC_WARN) {
        printf("[WARNING] Output current high\n");
    }
    
    if (status & PMBUS_STATUS_IOUT_UC_FAULT) {
        printf("[FAULT] Output undercurrent\n");
    }
    
    if (status & PMBUS_STATUS_IOUT_UC_WARN) {
        printf("[WARNING] Output current low\n");
    }
    
    if (status & PMBUS_STATUS_POUT_OP_FAULT) {
        printf("[FAULT] Output power overload\n");
    }
    
    if (status & PMBUS_STATUS_POUT_OP_WARN) {
        printf("[WARNING] Output power limit\n");
    }
}
```

**STATUS_TEMPERATURE命令（0x7D）**：

```
功能：读取温度详细状态

数据格式：1字节

位定义：
┌───────────────────────────────────────────┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0           │
├───┼───┼───┼───┼───┼───┼───┼─────────────┤
│OT │OT │UT │UT │   │   │   │             │
│故障│警告│警告│故障│   │   │             │
└───┴───┴───┴───┴───┴───┴───┴─────────────┘

位说明：
Bit 7：过温故障
Bit 6：过温警告
Bit 5：欠温警告
Bit 4：欠温故障
Bit 3-0：保留
```

**实现代码**：

```c
// STATUS_TEMPERATURE位定义
#define PMBUS_STATUS_OT_FAULT  (1 << 7)
#define PMBUS_STATUS_OT_WARN   (1 << 6)
#define PMBUS_STATUS_UT_WARN   (1 << 5)
#define PMBUS_STATUS_UT_FAULT  (1 << 4)

// 读取温度状态
bool PMBus_ReadTemperatureStatus(uint8_t device_addr, uint8_t *status) {
    return PMBus_ReadByte(device_addr, PMBUS_CMD_STATUS_TEMPERATURE, status);
}

// 解析温度状态
void PMBus_PrintTemperatureStatus(uint8_t status) {
    printf("\n=== Temperature Status (0x%02X) ===\n", status);
    
    if (status == 0x00) {
        printf("Temperature is normal\n");
        return;
    }
    
    if (status & PMBUS_STATUS_OT_FAULT) {
        printf("[FAULT] Over temperature\n");
    }
    
    if (status & PMBUS_STATUS_OT_WARN) {
        printf("[WARNING] Temperature high\n");
    }
    
    if (status & PMBUS_STATUS_UT_WARN) {
        printf("[WARNING] Temperature low\n");
    }
    
    if (status & PMBUS_STATUS_UT_FAULT) {
        printf("[FAULT] Under temperature\n");
    }
}

// 综合状态检查
void PMBus_ComprehensiveStatusCheck(uint8_t device_addr) {
    uint16_t status_word;
    uint8_t status_vout, status_iout, status_temp;
    
    printf("\n========== Comprehensive Status Check ==========\n");
    
    // 读取STATUS_WORD
    if (PMBus_ReadStatusWord(device_addr, &status_word)) {
        PMBus_PrintStatus(status_word);
        
        // 根据STATUS_WORD读取详细状态
        if (status_word & PMBUS_STATUS_VOUT) {
            if (PMBus_ReadVoutStatus(device_addr, &status_vout)) {
                PMBus_PrintVoutStatus(status_vout);
            }
        }
        
        if (status_word & PMBUS_STATUS_IOUT) {
            if (PMBus_ReadIoutStatus(device_addr, &status_iout)) {
                PMBus_PrintIoutStatus(status_iout);
            }
        }
        
        if (status_word & PMBUS_STATUS_TEMPERATURE) {
            if (PMBus_ReadTemperatureStatus(device_addr, &status_temp)) {
                PMBus_PrintTemperatureStatus(status_temp);
            }
        }
    }
    
    printf("\n===============================================\n");
}
```

### 故障限制配置命令

**VOUT_OV_FAULT_LIMIT命令（0x40）**：

```
功能：设置输出过压故障限制

数据格式：2字节（Linear16或Direct格式）

作用：
- 当VOUT > OV_FAULT_LIMIT时触发故障
- 通常设置为标称电压的110%-120%
- 触发后根据VOUT_OV_FAULT_RESPONSE执行动作

示例：
3.3V输出：OV_FAULT_LIMIT = 3.6V (109%)
5V输出：OV_FAULT_LIMIT = 5.5V (110%)
12V输出：OV_FAULT_LIMIT = 13.2V (110%)
```

**实现代码**：

```c
// 配置过压保护
bool PMBus_ConfigureOVP(uint8_t device_addr, 
                        float nominal_voltage,
                        float ov_percent) {
    Linear16_Context_t context;
    float ov_limit;
    uint16_t ov_value;
    
    // 初始化上下文
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 计算过压限制
    ov_limit = nominal_voltage * (1.0 + ov_percent / 100.0);
    
    printf("Configuring OVP:\n");
    printf("  Nominal: %.2fV\n", nominal_voltage);
    printf("  OV Limit: %.2fV (+%.1f%%)\n", ov_limit, ov_percent);
    
    // 转换并写入
    ov_value = Float_To_Linear16(ov_limit, &context);
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_OV_FAULT_LIMIT, ov_value)) {
        return false;
    }
    
    return true;
}

// 配置欠压保护
bool PMBus_ConfigureUVP(uint8_t device_addr,
                        float nominal_voltage,
                        float uv_percent) {
    Linear16_Context_t context;
    float uv_limit;
    uint16_t uv_value;
    
    if (!PMBus_InitLinear16Context(device_addr, &context)) {
        return false;
    }
    
    // 计算欠压限制
    uv_limit = nominal_voltage * (1.0 - uv_percent / 100.0);
    
    printf("Configuring UVP:\n");
    printf("  Nominal: %.2fV\n", nominal_voltage);
    printf("  UV Limit: %.2fV (-%.1f%%)\n", uv_limit, uv_percent);
    
    uv_value = Float_To_Linear16(uv_limit, &context);
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_VOUT_UV_FAULT_LIMIT, uv_value)) {
        return false;
    }
    
    return true;
}
```

**IOUT_OC_FAULT_LIMIT命令（0x46）**：

```
功能：设置输出过流故障限制

数据格式：2字节（Linear11格式）

作用：
- 当IOUT > OC_FAULT_LIMIT时触发故障
- 通常设置为额定电流的120%-150%
- 保护电源和负载

示例：
10A输出：OC_FAULT_LIMIT = 12A (120%)
20A输出：OC_FAULT_LIMIT = 25A (125%)
```

**实现代码**：

```c
// 配置过流保护
bool PMBus_ConfigureOCP(uint8_t device_addr,
                        float rated_current,
                        float oc_percent) {
    float oc_limit;
    uint16_t oc_value;
    
    // 计算过流限制
    oc_limit = rated_current * (1.0 + oc_percent / 100.0);
    
    printf("Configuring OCP:\n");
    printf("  Rated: %.2fA\n", rated_current);
    printf("  OC Limit: %.2fA (+%.1f%%)\n", oc_limit, oc_percent);
    
    // 转换为Linear11格式
    oc_value = Float_To_Linear11(oc_limit);
    
    if (!PMBus_WriteWord(device_addr, PMBUS_CMD_IOUT_OC_FAULT_LIMIT, oc_value)) {
        return false;
    }
    
    return true;
}

// 配置完整的保护参数
bool PMBus_ConfigureProtection(uint8_t device_addr,
                                float nominal_voltage,
                                float rated_current) {
    printf("\n=== Configuring Protection Parameters ===\n");
    
    // 配置过压保护（+10%）
    if (!PMBus_ConfigureOVP(device_addr, nominal_voltage, 10.0)) {
        printf("Error: Failed to configure OVP\n");
        return false;
    }
    
    // 配置欠压保护（-10%）
    if (!PMBus_ConfigureUVP(device_addr, nominal_voltage, 10.0)) {
        printf("Error: Failed to configure UVP\n");
        return false;
    }
    
    // 配置过流保护（+20%）
    if (!PMBus_ConfigureOCP(device_addr, rated_current, 20.0)) {
        printf("Error: Failed to configure OCP\n");
        return false;
    }
    
    printf("\nProtection configured successfully\n");
    
    return true;
}
```


## PMBus主机实现

### 硬件接口设计

**PMBus主机硬件连接**：

```
微控制器（STM32/ESP32）
 │
 ├─ I2C/SMBus接口
 │   │
 │   ├─ SCL ──┬── 4.7kΩ上拉 ── VDD (3.3V)
 │   │        │
 │   │        ├── PMBus设备1 (SCL)
 │   │        ├── PMBus设备2 (SCL)
 │   │        └── PMBus设备3 (SCL)
 │   │
 │   └─ SDA ──┬── 4.7kΩ上拉 ── VDD (3.3V)
 │            │
 │            ├── PMBus设备1 (SDA)
 │            ├── PMBus设备2 (SDA)
 │            └── PMBus设备3 (SDA)
 │
 ├─ SMBALERT# ─┬── 10kΩ上拉 ── VDD
 │             │
 │             ├── PMBus设备1 (ALERT#)
 │             ├── PMBus设备2 (ALERT#)
 │             └── PMBus设备3 (ALERT#)
 │
 └─ CONTROL引脚
     ├── GPIO1 ── PMBus设备1 (CTRL)
     ├── GPIO2 ── PMBus设备2 (CTRL)
     └── GPIO3 ── PMBus设备3 (CTRL)

硬件设计要点：
1. 上拉电阻：4.7kΩ适合100kHz，根据总线电容调整
2. SMBALERT#：开漏输出，需要上拉电阻
3. 电平转换：如果MCU是3.3V，PMBus设备是5V，需要电平转换器
4. ESD保护：建议在SCL/SDA线上增加ESD保护
5. PCB布线：SCL/SDA走线尽量短，避免长距离走线
```

### 软件架构设计

**PMBus驱动层次结构**：

```c
// PMBus软件架构

┌─────────────────────────────────────┐
│      应用层（Application）           │
│  - 电源管理策略                      │
│  - 用户接口                          │
│  - 数据记录                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      PMBus API层                     │
│  - PMBus_Init()                     │
│  - PMBus_SetVoltage()               │
│  - PMBus_ReadTelemetry()            │
│  - PMBus_ConfigureProtection()      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      PMBus命令层                     │
│  - 命令编码/解码                     │
│  - 数据格式转换                      │
│  - 错误处理                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      SMBus传输层                     │
│  - Read/Write Byte/Word             │
│  - Block Read/Write                 │
│  - PEC计算和验证                     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      I2C HAL层                       │
│  - I2C_Start/Stop                   │
│  - I2C_WriteByte/ReadByte           │
│  - 超时处理                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      硬件层（Hardware）              │
│  - I2C外设寄存器                     │
│  - GPIO控制                          │
│  - 中断处理                          │
└─────────────────────────────────────┘
```

### PMBus驱动实现

**PMBus设备对象**：

```c
// PMBus设备配置
typedef struct {
    uint8_t address;              // 设备I2C地址
    char name[32];                // 设备名称
    uint8_t num_pages;            // 页面数量
    bool supports_pec;            // 是否支持PEC
    Linear16_Context_t linear16;  // Linear16上下文
    DirectFormat_Context_t direct; // Direct格式上下文
} PMBus_Device_t;

// PMBus设备句柄
typedef struct {
    PMBus_Device_t device;        // 设备配置
    I2C_HandleTypeDef *hi2c;      // I2C句柄
    bool initialized;             // 初始化标志
    uint32_t error_count;         // 错误计数
    uint32_t transaction_count;   // 事务计数
} PMBus_Handle_t;

// PMBus管理器（管理多个设备）
typedef struct {
    PMBus_Handle_t devices[PMBUS_MAX_DEVICES];
    uint8_t device_count;
    I2C_HandleTypeDef *hi2c;
} PMBus_Manager_t;

// 全局PMBus管理器
static PMBus_Manager_t g_pmbus_manager = {0};
```

**初始化函数**：

```c
// 初始化PMBus管理器
bool PMBus_ManagerInit(I2C_HandleTypeDef *hi2c) {
    g_pmbus_manager.hi2c = hi2c;
    g_pmbus_manager.device_count = 0;
    
    printf("PMBus Manager initialized\n");
    
    return true;
}

// 添加PMBus设备
PMBus_Handle_t* PMBus_AddDevice(uint8_t address, const char *name) {
    if (g_pmbus_manager.device_count >= PMBUS_MAX_DEVICES) {
        printf("Error: Maximum devices reached\n");
        return NULL;
    }
    
    PMBus_Handle_t *handle = &g_pmbus_manager.devices[g_pmbus_manager.device_count];
    
    // 配置设备
    handle->device.address = address;
    strncpy(handle->device.name, name, sizeof(handle->device.name) - 1);
    handle->hi2c = g_pmbus_manager.hi2c;
    handle->initialized = false;
    handle->error_count = 0;
    handle->transaction_count = 0;
    
    g_pmbus_manager.device_count++;
    
    printf("Added PMBus device: %s (0x%02X)\n", name, address);
    
    return handle;
}

// 初始化PMBus设备
bool PMBus_DeviceInit(PMBus_Handle_t *handle) {
    uint8_t pmbus_revision;
    uint8_t capability;
    
    printf("\nInitializing PMBus device: %s\n", handle->device.name);
    
    // 读取PMBus版本
    if (PMBus_ReadByte(handle->device.address, 
                       PMBUS_CMD_PMBUS_REVISION, 
                       &pmbus_revision)) {
        printf("  PMBus Revision: %d.%d\n", 
               (pmbus_revision >> 4) & 0x0F,
               pmbus_revision & 0x0F);
    }
    
    // 读取设备能力
    if (PMBus_ReadByte(handle->device.address,
                       PMBUS_CMD_CAPABILITY,
                       &capability)) {
        printf("  Capability: 0x%02X\n", capability);
        handle->device.supports_pec = (capability & 0x80) != 0;
        handle->device.num_pages = (capability & 0x1F);
        
        printf("    PEC Support: %s\n", 
               handle->device.supports_pec ? "Yes" : "No");
        printf("    Pages: %d\n", handle->device.num_pages);
    }
    
    // 初始化Linear16上下文
    if (!PMBus_InitLinear16Context(handle->device.address, 
                                    &handle->device.linear16)) {
        printf("  Warning: Failed to init Linear16 context\n");
    }
    
    // 读取设备信息
    uint8_t mfr_id[16];
    uint8_t mfr_model[16];
    uint8_t mfr_serial[16];
    uint8_t count;
    
    if (PMBus_BlockRead(handle->device.address, PMBUS_CMD_MFR_ID, 
                        mfr_id, &count)) {
        mfr_id[count] = '\0';
        printf("  Manufacturer: %s\n", mfr_id);
    }
    
    if (PMBus_BlockRead(handle->device.address, PMBUS_CMD_MFR_MODEL,
                        mfr_model, &count)) {
        mfr_model[count] = '\0';
        printf("  Model: %s\n", mfr_model);
    }
    
    if (PMBus_BlockRead(handle->device.address, PMBUS_CMD_MFR_SERIAL,
                        mfr_serial, &count)) {
        mfr_serial[count] = '\0';
        printf("  Serial: %s\n", mfr_serial);
    }
    
    handle->initialized = true;
    
    printf("Device initialized successfully\n");
    
    return true;
}

// 扫描PMBus总线
void PMBus_ScanBus(void) {
    printf("\n=== Scanning PMBus Bus ===\n");
    
    for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
        // 尝试Quick Command
        if (PMBus_QuickCommand(addr, false)) {
            printf("Found device at address 0x%02X\n", addr);
            
            // 尝试读取设备信息
            uint8_t mfr_id[16];
            uint8_t count;
            if (PMBus_BlockRead(addr, PMBUS_CMD_MFR_ID, mfr_id, &count)) {
                mfr_id[count] = '\0';
                printf("  Manufacturer: %s\n", mfr_id);
            }
        }
    }
    
    printf("=== Scan Complete ===\n");
}
```

### 高级功能实现

**电源排序控制**：

```c
// 电源排序配置
typedef struct {
    PMBus_Handle_t *handle;
    uint16_t delay_ms;        // 延时（毫秒）
    float target_voltage;     // 目标电压
} PowerSequence_Step_t;

// 电源排序
bool PMBus_PowerSequence(PowerSequence_Step_t *sequence, uint8_t num_steps) {
    printf("\n=== Starting Power Sequence ===\n");
    
    for (uint8_t i = 0; i < num_steps; i++) {
        PowerSequence_Step_t *step = &sequence[i];
        
        printf("\nStep %d: %s\n", i + 1, step->handle->device.name);
        printf("  Target: %.2fV\n", step->target_voltage);
        printf("  Delay: %dms\n", step->delay_ms);
        
        // 设置电压
        if (!PMBus_SetVoltage(step->handle->device.address, 
                              step->target_voltage)) {
            printf("  Error: Failed to set voltage\n");
            return false;
        }
        
        // 开启电源
        if (!PMBus_PowerOn(step->handle->device.address)) {
            printf("  Error: Failed to power on\n");
            return false;
        }
        
        // 等待稳定
        HAL_Delay(step->delay_ms);
        
        // 验证输出
        float actual_voltage;
        if (PMBus_ReadVoltage(step->handle->device.address, &actual_voltage)) {
            printf("  Actual: %.3fV\n", actual_voltage);
            
            // 检查电压是否在范围内
            float error = fabs(actual_voltage - step->target_voltage);
            if (error > step->target_voltage * 0.05) {  // 5%容差
                printf("  Warning: Voltage out of range\n");
            }
        }
        
        printf("  Step %d complete\n", i + 1);
    }
    
    printf("\n=== Power Sequence Complete ===\n");
    
    return true;
}

// 使用示例
void PowerSequence_Example(void) {
    // 定义电源排序
    PowerSequence_Step_t sequence[] = {
        {&psu_handle, 100, 12.0},    // 步骤1：12V电源，延时100ms
        {&vrm1_handle, 50, 3.3},     // 步骤2：3.3V VRM，延时50ms
        {&vrm2_handle, 50, 1.8},     // 步骤3：1.8V VRM，延时50ms
        {&vrm3_handle, 50, 1.2},     // 步骤4：1.2V VRM，延时50ms
    };
    
    PMBus_PowerSequence(sequence, sizeof(sequence) / sizeof(sequence[0]));
}
```

**动态电压调节（DVS）**：

```c
// DVS配置
typedef struct {
    float voltage_min;        // 最小电压
    float voltage_max;        // 最大电压
    float voltage_step;       // 电压步进
    uint16_t transition_rate; // 转换速率（mV/μs）
} DVS_Config_t;

// 配置DVS
bool PMBus_ConfigureDVS(PMBus_Handle_t *handle, DVS_Config_t *config) {
    Linear16_Context_t *ctx = &handle->device.linear16;
    uint16_t vout_min, vout_max, transition_rate;
    
    printf("\nConfiguring DVS for %s:\n", handle->device.name);
    printf("  Range: %.3fV - %.3fV\n", config->voltage_min, config->voltage_max);
    printf("  Step: %.3fV\n", config->voltage_step);
    printf("  Rate: %d mV/μs\n", config->transition_rate);
    
    // 设置电压范围
    vout_min = Float_To_Linear16(config->voltage_min, ctx);
    vout_max = Float_To_Linear16(config->voltage_max, ctx);
    
    PMBus_WriteWord(handle->device.address, PMBUS_CMD_VOUT_MARGIN_LOW, vout_min);
    PMBus_WriteWord(handle->device.address, PMBUS_CMD_VOUT_MAX, vout_max);
    
    // 设置转换速率
    transition_rate = Float_To_Linear11(config->transition_rate / 1000.0);
    PMBus_WriteWord(handle->device.address, 
                    PMBUS_CMD_VOUT_TRANSITION_RATE, 
                    transition_rate);
    
    return true;
}

// 执行DVS
bool PMBus_PerformDVS(PMBus_Handle_t *handle, float target_voltage) {
    float current_voltage;
    
    // 读取当前电压
    if (!PMBus_ReadVoltage(handle->device.address, &current_voltage)) {
        return false;
    }
    
    printf("DVS: %.3fV → %.3fV\n", current_voltage, target_voltage);
    
    // 设置目标电压
    if (!PMBus_SetVoltage(handle->device.address, target_voltage)) {
        return false;
    }
    
    // 等待转换完成
    uint32_t start_time = HAL_GetTick();
    uint32_t timeout = 1000;  // 1秒超时
    
    while (HAL_GetTick() - start_time < timeout) {
        float voltage;
        if (PMBus_ReadVoltage(handle->device.address, &voltage)) {
            float error = fabs(voltage - target_voltage);
            if (error < 0.01) {  // 10mV容差
                printf("DVS complete: %.3fV (%.1fms)\n", 
                       voltage, (float)(HAL_GetTick() - start_time));
                return true;
            }
        }
        HAL_Delay(10);
    }
    
    printf("DVS timeout\n");
    return false;
}

// DVS性能测试
void PMBus_DVS_PerformanceTest(PMBus_Handle_t *handle) {
    float voltages[] = {1.0, 1.2, 1.0, 0.8, 1.2, 1.0};
    uint32_t total_time = 0;
    
    printf("\n=== DVS Performance Test ===\n");
    
    for (int i = 0; i < sizeof(voltages) / sizeof(voltages[0]); i++) {
        uint32_t start = HAL_GetTick();
        
        if (PMBus_PerformDVS(handle, voltages[i])) {
            uint32_t elapsed = HAL_GetTick() - start;
            total_time += elapsed;
            printf("Step %d: %.1fms\n", i + 1, (float)elapsed);
        }
        
        HAL_Delay(100);
    }
    
    printf("\nTotal time: %.1fms\n", (float)total_time);
    printf("Average: %.1fms\n", (float)total_time / (sizeof(voltages) / sizeof(voltages[0])));
}
```

**故障记录和分析**：

```c
// 故障记录
typedef struct {
    uint32_t timestamp;       // 时间戳
    uint16_t status_word;     // 状态字
    uint8_t status_vout;      // 输出电压状态
    uint8_t status_iout;      // 输出电流状态
    uint8_t status_temp;      // 温度状态
    float vout;               // 输出电压
    float iout;               // 输出电流
    float temperature;        // 温度
} PMBus_FaultRecord_t;

// 故障日志
#define FAULT_LOG_SIZE 100
static PMBus_FaultRecord_t g_fault_log[FAULT_LOG_SIZE];
static uint16_t g_fault_log_index = 0;

// 记录故障
void PMBus_RecordFault(PMBus_Handle_t *handle) {
    PMBus_FaultRecord_t *record = &g_fault_log[g_fault_log_index];
    
    // 记录时间戳
    record->timestamp = HAL_GetTick();
    
    // 读取状态
    PMBus_ReadStatusWord(handle->device.address, &record->status_word);
    PMBus_ReadVoutStatus(handle->device.address, &record->status_vout);
    PMBus_ReadIoutStatus(handle->device.address, &record->status_iout);
    PMBus_ReadTemperatureStatus(handle->device.address, &record->status_temp);
    
    // 读取遥测数据
    PMBus_ReadVoltage(handle->device.address, &record->vout);
    PMBus_ReadCurrent(handle->device.address, &record->iout);
    PMBus_ReadTemperature(handle->device.address, 1, &record->temperature);
    
    // 更新索引
    g_fault_log_index = (g_fault_log_index + 1) % FAULT_LOG_SIZE;
    
    printf("Fault recorded at %lu ms\n", record->timestamp);
}

// 打印故障日志
void PMBus_PrintFaultLog(void) {
    printf("\n=== Fault Log ===\n");
    printf("Total records: %d\n\n", 
           g_fault_log_index < FAULT_LOG_SIZE ? g_fault_log_index : FAULT_LOG_SIZE);
    
    for (uint16_t i = 0; i < FAULT_LOG_SIZE; i++) {
        PMBus_FaultRecord_t *record = &g_fault_log[i];
        
        if (record->timestamp == 0) continue;
        
        printf("Record %d (Time: %lu ms):\n", i, record->timestamp);
        printf("  STATUS_WORD: 0x%04X\n", record->status_word);
        printf("  VOUT: %.3fV (Status: 0x%02X)\n", 
               record->vout, record->status_vout);
        printf("  IOUT: %.3fA (Status: 0x%02X)\n",
               record->iout, record->status_iout);
        printf("  TEMP: %.1f°C (Status: 0x%02X)\n",
               record->temperature, record->status_temp);
        printf("\n");
    }
}

// 故障分析
void PMBus_AnalyzeFaults(void) {
    uint32_t ovp_count = 0;
    uint32_t uvp_count = 0;
    uint32_t ocp_count = 0;
    uint32_t otp_count = 0;
    
    printf("\n=== Fault Analysis ===\n");
    
    for (uint16_t i = 0; i < FAULT_LOG_SIZE; i++) {
        PMBus_FaultRecord_t *record = &g_fault_log[i];
        
        if (record->timestamp == 0) continue;
        
        if (record->status_vout & PMBUS_STATUS_VOUT_OV_FAULT) ovp_count++;
        if (record->status_vout & PMBUS_STATUS_VOUT_UV_FAULT) uvp_count++;
        if (record->status_iout & PMBUS_STATUS_IOUT_OC_FAULT) ocp_count++;
        if (record->status_temp & PMBUS_STATUS_OT_FAULT) otp_count++;
    }
    
    printf("Overvoltage faults: %lu\n", ovp_count);
    printf("Undervoltage faults: %lu\n", uvp_count);
    printf("Overcurrent faults: %lu\n", ocp_count);
    printf("Overtemperature faults: %lu\n", otp_count);
    
    // 计算故障率
    uint32_t total_records = g_fault_log_index < FAULT_LOG_SIZE ? 
                             g_fault_log_index : FAULT_LOG_SIZE;
    if (total_records > 0) {
        printf("\nFault rates:\n");
        printf("  OVP: %.2f%%\n", (float)ovp_count / total_records * 100);
        printf("  UVP: %.2f%%\n", (float)uvp_count / total_records * 100);
        printf("  OCP: %.2f%%\n", (float)ocp_count / total_records * 100);
        printf("  OTP: %.2f%%\n", (float)otp_count / total_records * 100);
    }
}
```


## 实战项目：服务器电源管理系统

### 项目需求

**系统规格**：

```
硬件配置：
- 主控：STM32F407微控制器
- 电源：2个冗余PSU（PMBus接口）
- VRM：3个电压调节器（CPU、内存、外设）
- 传感器：温度、风扇转速
- 接口：UART调试、以太网管理

功能需求：
1. 电源监控：
   - 实时监控所有电源的电压、电流、功率
   - 温度监控和过温保护
   - 效率计算和优化

2. 电源控制：
   - 电源排序控制
   - 动态电压调节（DVS）
   - 冗余切换

3. 故障管理：
   - 故障检测和记录
   - 自动恢复
   - 告警通知

4. 远程管理：
   - UART命令行接口
   - 以太网管理接口
   - 日志上传

性能指标：
- 遥测采样率：10Hz
- 故障响应时间：<100ms
- DVS转换时间：<10ms
- 系统可用性：>99.9%
```

### 系统架构设计

**软件架构**：

```c
// 系统架构

┌─────────────────────────────────────────────┐
│           应用层（Application）              │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ 电源管理策略 │  │ 用户接口    │          │
│  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────┘
              ↓              ↓
┌─────────────────────────────────────────────┐
│           服务层（Services）                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │遥测服务  │ │故障管理  │ │日志服务  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
              ↓              ↓
┌─────────────────────────────────────────────┐
│           驱动层（Drivers）                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │PMBus驱动 │ │UART驱动  │ │以太网驱动│   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
              ↓              ↓
┌─────────────────────────────────────────────┐
│           HAL层（Hardware Abstraction）      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │I2C HAL   │ │UART HAL  │ │ETH HAL   │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
```

### 核心代码实现

**系统初始化**：

```c
// 系统配置
typedef struct {
    PMBus_Handle_t psu1;          // PSU #1
    PMBus_Handle_t psu2;          // PSU #2
    PMBus_Handle_t vrm_cpu;       // CPU VRM
    PMBus_Handle_t vrm_mem;       // 内存VRM
    PMBus_Handle_t vrm_peri;      // 外设VRM
    
    bool psu1_active;             // PSU1活动状态
    bool psu2_active;             // PSU2活动状态
    bool redundancy_enabled;      // 冗余使能
    
    uint32_t telemetry_interval;  // 遥测间隔（ms）
    uint32_t fault_check_interval; // 故障检查间隔（ms）
} PowerSystem_Config_t;

// 全局系统配置
static PowerSystem_Config_t g_power_system;

// 系统初始化
bool PowerSystem_Init(void) {
    printf("\n========================================\n");
    printf("  Server Power Management System\n");
    printf("========================================\n\n");
    
    // 初始化PMBus管理器
    if (!PMBus_ManagerInit(&hi2c1)) {
        printf("Error: Failed to initialize PMBus manager\n");
        return false;
    }
    
    // 添加PSU设备
    printf("Initializing PSU devices...\n");
    PMBus_Handle_t *psu1 = PMBus_AddDevice(0x58, "PSU #1");
    PMBus_Handle_t *psu2 = PMBus_AddDevice(0x59, "PSU #2");
    
    if (psu1) {
        PMBus_DeviceInit(psu1);
        g_power_system.psu1 = *psu1;
        g_power_system.psu1_active = true;
    }
    
    if (psu2) {
        PMBus_DeviceInit(psu2);
        g_power_system.psu2 = *psu2;
        g_power_system.psu2_active = true;
    }
    
    // 添加VRM设备
    printf("\nInitializing VRM devices...\n");
    PMBus_Handle_t *vrm_cpu = PMBus_AddDevice(0x60, "CPU VRM");
    PMBus_Handle_t *vrm_mem = PMBus_AddDevice(0x61, "Memory VRM");
    PMBus_Handle_t *vrm_peri = PMBus_AddDevice(0x62, "Peripheral VRM");
    
    if (vrm_cpu) {
        PMBus_DeviceInit(vrm_cpu);
        g_power_system.vrm_cpu = *vrm_cpu;
    }
    
    if (vrm_mem) {
        PMBus_DeviceInit(vrm_mem);
        g_power_system.vrm_mem = *vrm_mem;
    }
    
    if (vrm_peri) {
        PMBus_DeviceInit(vrm_peri);
        g_power_system.vrm_peri = *vrm_peri;
    }
    
    // 配置系统参数
    g_power_system.redundancy_enabled = true;
    g_power_system.telemetry_interval = 100;  // 100ms
    g_power_system.fault_check_interval = 50; // 50ms
    
    printf("\nSystem initialized successfully\n");
    printf("Redundancy: %s\n", 
           g_power_system.redundancy_enabled ? "Enabled" : "Disabled");
    
    return true;
}

// 配置电源保护参数
bool PowerSystem_ConfigureProtection(void) {
    printf("\nConfiguring protection parameters...\n");
    
    // 配置PSU保护
    PMBus_ConfigureProtection(g_power_system.psu1.device.address, 12.0, 50.0);
    PMBus_ConfigureProtection(g_power_system.psu2.device.address, 12.0, 50.0);
    
    // 配置VRM保护
    PMBus_ConfigureProtection(g_power_system.vrm_cpu.device.address, 1.0, 10.0);
    PMBus_ConfigureProtection(g_power_system.vrm_mem.device.address, 1.35, 5.0);
    PMBus_ConfigureProtection(g_power_system.vrm_peri.device.address, 3.3, 5.0);
    
    printf("Protection configured\n");
    
    return true;
}

// 电源上电序列
bool PowerSystem_PowerOn(void) {
    printf("\n=== Power-On Sequence ===\n");
    
    // 定义上电序列
    PowerSequence_Step_t sequence[] = {
        {&g_power_system.psu1, 200, 12.0},      // PSU1: 12V
        {&g_power_system.vrm_peri, 100, 3.3},   // 外设: 3.3V
        {&g_power_system.vrm_mem, 100, 1.35},   // 内存: 1.35V
        {&g_power_system.vrm_cpu, 100, 1.0},    // CPU: 1.0V
    };
    
    // 执行上电序列
    if (!PMBus_PowerSequence(sequence, 
                             sizeof(sequence) / sizeof(sequence[0]))) {
        printf("Error: Power-on sequence failed\n");
        return false;
    }
    
    printf("\nSystem powered on successfully\n");
    
    return true;
}

// 电源下电序列
bool PowerSystem_PowerOff(void) {
    printf("\n=== Power-Off Sequence ===\n");
    
    // 反向关闭电源
    printf("Shutting down CPU VRM...\n");
    PMBus_PowerOff(g_power_system.vrm_cpu.device.address);
    HAL_Delay(100);
    
    printf("Shutting down Memory VRM...\n");
    PMBus_PowerOff(g_power_system.vrm_mem.device.address);
    HAL_Delay(100);
    
    printf("Shutting down Peripheral VRM...\n");
    PMBus_PowerOff(g_power_system.vrm_peri.device.address);
    HAL_Delay(100);
    
    printf("Shutting down PSU...\n");
    PMBus_PowerOff(g_power_system.psu1.device.address);
    HAL_Delay(200);
    
    printf("\nSystem powered off\n");
    
    return true;
}
```

**遥测服务**：

```c
// 遥测数据
typedef struct {
    float voltage;
    float current;
    float power;
    float temperature;
    float efficiency;
} Telemetry_Data_t;

// 系统遥测
typedef struct {
    Telemetry_Data_t psu1;
    Telemetry_Data_t psu2;
    Telemetry_Data_t vrm_cpu;
    Telemetry_Data_t vrm_mem;
    Telemetry_Data_t vrm_peri;
    uint32_t timestamp;
} System_Telemetry_t;

// 读取设备遥测
bool PowerSystem_ReadDeviceTelemetry(PMBus_Handle_t *handle, 
                                     Telemetry_Data_t *data) {
    // 读取电压
    if (!PMBus_ReadVoltage(handle->device.address, &data->voltage)) {
        return false;
    }
    
    // 读取电流
    if (!PMBus_ReadCurrent(handle->device.address, &data->current)) {
        return false;
    }
    
    // 读取功率
    if (!PMBus_ReadPower(handle->device.address, &data->power)) {
        // 如果设备不支持直接读取功率，则计算
        data->power = data->voltage * data->current;
    }
    
    // 读取温度
    if (!PMBus_ReadTemperature(handle->device.address, 1, &data->temperature)) {
        data->temperature = 0.0;
    }
    
    // 计算效率（仅对PSU）
    data->efficiency = 0.0;
    
    return true;
}

// 读取系统遥测
bool PowerSystem_ReadTelemetry(System_Telemetry_t *telemetry) {
    telemetry->timestamp = HAL_GetTick();
    
    // 读取PSU遥测
    if (!PowerSystem_ReadDeviceTelemetry(&g_power_system.psu1, 
                                         &telemetry->psu1)) {
        return false;
    }
    
    if (g_power_system.psu2_active) {
        PowerSystem_ReadDeviceTelemetry(&g_power_system.psu2, 
                                        &telemetry->psu2);
    }
    
    // 读取VRM遥测
    PowerSystem_ReadDeviceTelemetry(&g_power_system.vrm_cpu, 
                                    &telemetry->vrm_cpu);
    PowerSystem_ReadDeviceTelemetry(&g_power_system.vrm_mem,
                                    &telemetry->vrm_mem);
    PowerSystem_ReadDeviceTelemetry(&g_power_system.vrm_peri,
                                    &telemetry->vrm_peri);
    
    return true;
}

// 打印遥测数据
void PowerSystem_PrintTelemetry(System_Telemetry_t *telemetry) {
    printf("\n========== System Telemetry ==========\n");
    printf("Time: %lu ms\n\n", telemetry->timestamp);
    
    printf("PSU #1:\n");
    printf("  Voltage: %.2fV\n", telemetry->psu1.voltage);
    printf("  Current: %.2fA\n", telemetry->psu1.current);
    printf("  Power: %.2fW\n", telemetry->psu1.power);
    printf("  Temperature: %.1f°C\n", telemetry->psu1.temperature);
    
    if (g_power_system.psu2_active) {
        printf("\nPSU #2:\n");
        printf("  Voltage: %.2fV\n", telemetry->psu2.voltage);
        printf("  Current: %.2fA\n", telemetry->psu2.current);
        printf("  Power: %.2fW\n", telemetry->psu2.power);
        printf("  Temperature: %.1f°C\n", telemetry->psu2.temperature);
    }
    
    printf("\nCPU VRM:\n");
    printf("  Voltage: %.3fV\n", telemetry->vrm_cpu.voltage);
    printf("  Current: %.2fA\n", telemetry->vrm_cpu.current);
    printf("  Power: %.2fW\n", telemetry->vrm_cpu.power);
    printf("  Temperature: %.1f°C\n", telemetry->vrm_cpu.temperature);
    
    printf("\nMemory VRM:\n");
    printf("  Voltage: %.3fV\n", telemetry->vrm_mem.voltage);
    printf("  Current: %.2fA\n", telemetry->vrm_mem.current);
    printf("  Power: %.2fW\n", telemetry->vrm_mem.power);
    printf("  Temperature: %.1f°C\n", telemetry->vrm_mem.temperature);
    
    printf("\nPeripheral VRM:\n");
    printf("  Voltage: %.3fV\n", telemetry->vrm_peri.voltage);
    printf("  Current: %.2fA\n", telemetry->vrm_peri.current);
    printf("  Power: %.2fW\n", telemetry->vrm_peri.power);
    printf("  Temperature: %.1f°C\n", telemetry->vrm_peri.temperature);
    
    // 计算总功率
    float total_power = telemetry->vrm_cpu.power + 
                        telemetry->vrm_mem.power +
                        telemetry->vrm_peri.power;
    
    printf("\nTotal System Power: %.2fW\n", total_power);
    
    printf("======================================\n");
}

// 遥测任务
void PowerSystem_TelemetryTask(void) {
    static uint32_t last_update = 0;
    System_Telemetry_t telemetry;
    
    if (HAL_GetTick() - last_update >= g_power_system.telemetry_interval) {
        if (PowerSystem_ReadTelemetry(&telemetry)) {
            PowerSystem_PrintTelemetry(&telemetry);
            
            // 可以在这里添加数据记录、上传等功能
        }
        
        last_update = HAL_GetTick();
    }
}
```

**故障管理服务**：

```c
// 故障类型
typedef enum {
    FAULT_NONE = 0,
    FAULT_OVP,          // 过压
    FAULT_UVP,          // 欠压
    FAULT_OCP,          // 过流
    FAULT_OTP,          // 过温
    FAULT_COMM,         // 通信故障
    FAULT_PSU_FAIL,     // PSU故障
} Fault_Type_t;

// 故障事件
typedef struct {
    Fault_Type_t type;
    PMBus_Handle_t *device;
    uint32_t timestamp;
    uint16_t status_word;
    bool resolved;
} Fault_Event_t;

// 故障队列
#define FAULT_QUEUE_SIZE 50
static Fault_Event_t g_fault_queue[FAULT_QUEUE_SIZE];
static uint16_t g_fault_queue_head = 0;
static uint16_t g_fault_queue_tail = 0;

// 添加故障事件
void PowerSystem_AddFaultEvent(Fault_Type_t type, PMBus_Handle_t *device) {
    Fault_Event_t *event = &g_fault_queue[g_fault_queue_tail];
    
    event->type = type;
    event->device = device;
    event->timestamp = HAL_GetTick();
    PMBus_ReadStatusWord(device->device.address, &event->status_word);
    event->resolved = false;
    
    g_fault_queue_tail = (g_fault_queue_tail + 1) % FAULT_QUEUE_SIZE;
    
    // 记录故障
    PMBus_RecordFault(device);
    
    printf("\n!!! FAULT DETECTED !!!\n");
    printf("Device: %s\n", device->device.name);
    printf("Type: %d\n", type);
    printf("Time: %lu ms\n", event->timestamp);
    printf("Status: 0x%04X\n", event->status_word);
}

// 检查设备故障
bool PowerSystem_CheckDeviceFaults(PMBus_Handle_t *handle) {
    uint16_t status_word;
    uint8_t status_vout, status_iout, status_temp;
    bool fault_detected = false;
    
    // 读取状态字
    if (!PMBus_ReadStatusWord(handle->device.address, &status_word)) {
        PowerSystem_AddFaultEvent(FAULT_COMM, handle);
        return true;
    }
    
    // 检查各类故障
    if (status_word & PMBUS_STATUS_VOUT) {
        PMBus_ReadVoutStatus(handle->device.address, &status_vout);
        
        if (status_vout & PMBUS_STATUS_VOUT_OV_FAULT) {
            PowerSystem_AddFaultEvent(FAULT_OVP, handle);
            fault_detected = true;
        }
        
        if (status_vout & PMBUS_STATUS_VOUT_UV_FAULT) {
            PowerSystem_AddFaultEvent(FAULT_UVP, handle);
            fault_detected = true;
        }
    }
    
    if (status_word & PMBUS_STATUS_IOUT) {
        PMBus_ReadIoutStatus(handle->device.address, &status_iout);
        
        if (status_iout & PMBUS_STATUS_IOUT_OC_FAULT) {
            PowerSystem_AddFaultEvent(FAULT_OCP, handle);
            fault_detected = true;
        }
    }
    
    if (status_word & PMBUS_STATUS_TEMPERATURE) {
        PMBus_ReadTemperatureStatus(handle->device.address, &status_temp);
        
        if (status_temp & PMBUS_STATUS_OT_FAULT) {
            PowerSystem_AddFaultEvent(FAULT_OTP, handle);
            fault_detected = true;
        }
    }
    
    return fault_detected;
}

// 故障检查任务
void PowerSystem_FaultCheckTask(void) {
    static uint32_t last_check = 0;
    
    if (HAL_GetTick() - last_check >= g_power_system.fault_check_interval) {
        // 检查所有设备
        PowerSystem_CheckDeviceFaults(&g_power_system.psu1);
        
        if (g_power_system.psu2_active) {
            PowerSystem_CheckDeviceFaults(&g_power_system.psu2);
        }
        
        PowerSystem_CheckDeviceFaults(&g_power_system.vrm_cpu);
        PowerSystem_CheckDeviceFaults(&g_power_system.vrm_mem);
        PowerSystem_CheckDeviceFaults(&g_power_system.vrm_peri);
        
        last_check = HAL_GetTick();
    }
}

// 故障恢复
bool PowerSystem_RecoverFromFault(Fault_Event_t *event) {
    printf("\nAttempting fault recovery...\n");
    printf("Device: %s\n", event->device->device.name);
    printf("Fault type: %d\n", event->type);
    
    // 清除故障
    PMBus_ClearFaults(event->device->device.address);
    HAL_Delay(100);
    
    // 检查是否恢复
    uint16_t status_word;
    if (PMBus_ReadStatusWord(event->device->device.address, &status_word)) {
        if (status_word == 0x0000) {
            printf("Fault cleared successfully\n");
            event->resolved = true;
            return true;
        }
    }
    
    printf("Fault recovery failed\n");
    return false;
}
```

**冗余管理**：

```c
// PSU冗余切换
bool PowerSystem_SwitchPSU(void) {
    printf("\n=== PSU Redundancy Switch ===\n");
    
    if (!g_power_system.redundancy_enabled) {
        printf("Redundancy not enabled\n");
        return false;
    }
    
    // 检查PSU1状态
    uint16_t psu1_status;
    bool psu1_ok = PMBus_ReadStatusWord(g_power_system.psu1.device.address, 
                                        &psu1_status);
    psu1_ok = psu1_ok && (psu1_status == 0x0000);
    
    // 检查PSU2状态
    uint16_t psu2_status;
    bool psu2_ok = PMBus_ReadStatusWord(g_power_system.psu2.device.address,
                                        &psu2_status);
    psu2_ok = psu2_ok && (psu2_status == 0x0000);
    
    printf("PSU1 Status: %s (0x%04X)\n", psu1_ok ? "OK" : "FAULT", psu1_status);
    printf("PSU2 Status: %s (0x%04X)\n", psu2_ok ? "OK" : "FAULT", psu2_status);
    
    // 如果PSU1故障，切换到PSU2
    if (!psu1_ok && psu2_ok) {
        printf("Switching to PSU2...\n");
        g_power_system.psu1_active = false;
        g_power_system.psu2_active = true;
        
        // 关闭PSU1
        PMBus_PowerOff(g_power_system.psu1.device.address);
        
        // 确保PSU2开启
        PMBus_PowerOn(g_power_system.psu2.device.address);
        
        printf("Switched to PSU2\n");
        return true;
    }
    
    // 如果PSU2故障，切换到PSU1
    if (!psu2_ok && psu1_ok) {
        printf("Switching to PSU1...\n");
        g_power_system.psu1_active = true;
        g_power_system.psu2_active = false;
        
        // 关闭PSU2
        PMBus_PowerOff(g_power_system.psu2.device.address);
        
        // 确保PSU1开启
        PMBus_PowerOn(g_power_system.psu1.device.address);
        
        printf("Switched to PSU1\n");
        return true;
    }
    
    // 如果两个都故障
    if (!psu1_ok && !psu2_ok) {
        printf("CRITICAL: Both PSUs failed!\n");
        return false;
    }
    
    printf("No switch needed, both PSUs OK\n");
    return true;
}
```


### 主循环实现

**系统主循环**：

```c
// 主循环
void PowerSystem_MainLoop(void) {
    printf("\n=== Starting Power System Main Loop ===\n");
    
    while (1) {
        // 遥测任务
        PowerSystem_TelemetryTask();
        
        // 故障检查任务
        PowerSystem_FaultCheckTask();
        
        // 处理故障队列
        if (g_fault_queue_head != g_fault_queue_tail) {
            Fault_Event_t *event = &g_fault_queue[g_fault_queue_head];
            
            if (!event->resolved) {
                PowerSystem_RecoverFromFault(event);
            }
            
            g_fault_queue_head = (g_fault_queue_head + 1) % FAULT_QUEUE_SIZE;
        }
        
        // 冗余检查
        if (g_power_system.redundancy_enabled) {
            static uint32_t last_redundancy_check = 0;
            if (HAL_GetTick() - last_redundancy_check >= 5000) {  // 5秒
                PowerSystem_SwitchPSU();
                last_redundancy_check = HAL_GetTick();
            }
        }
        
        // 让出CPU
        HAL_Delay(10);
    }
}

// 主函数
int main(void) {
    // 硬件初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_USART1_UART_Init();
    
    // 系统初始化
    if (!PowerSystem_Init()) {
        printf("System initialization failed!\n");
        while (1);
    }
    
    // 配置保护参数
    PowerSystem_ConfigureProtection();
    
    // 上电
    if (!PowerSystem_PowerOn()) {
        printf("Power-on failed!\n");
        while (1);
    }
    
    // 进入主循环
    PowerSystem_MainLoop();
    
    return 0;
}
```

## 调试与故障排除

### 常见问题

**1. 通信失败**：

```
问题现象：
- 无法读取设备
- 读取数据全为0xFF
- 超时错误

可能原因：
1. 硬件连接问题
   - SCL/SDA线路断开
   - 上拉电阻缺失或值不对
   - 电源未连接

2. 地址错误
   - 设备地址配置错误
   - 地址冲突

3. 时序问题
   - I2C时钟频率过高
   - 时序不符合SMBus规范

4. 电平不匹配
   - 3.3V和5V混用
   - 需要电平转换

排查步骤：
1. 用示波器检查SCL/SDA波形
2. 验证上拉电阻值
3. 检查设备地址
4. 降低I2C时钟频率
5. 检查电源和地线
```

**调试代码**：

```c
// I2C总线诊断
void PMBus_DiagnoseBus(void) {
    printf("\n=== PMBus Bus Diagnostics ===\n");
    
    // 检查I2C外设状态
    printf("I2C Status: 0x%08lX\n", hi2c1.Instance->SR1);
    printf("I2C Error: 0x%08lX\n", hi2c1.ErrorCode);
    
    // 检查GPIO状态
    GPIO_PinState scl_state = HAL_GPIO_ReadPin(I2C1_SCL_GPIO_Port, I2C1_SCL_Pin);
    GPIO_PinState sda_state = HAL_GPIO_ReadPin(I2C1_SDA_GPIO_Port, I2C1_SDA_Pin);
    
    printf("SCL State: %s\n", scl_state ? "HIGH" : "LOW");
    printf("SDA State: %s\n", sda_state ? "HIGH" : "LOW");
    
    // 如果SCL或SDA被拉低，可能是总线挂死
    if (!scl_state || !sda_state) {
        printf("WARNING: Bus may be stuck!\n");
        printf("Attempting bus recovery...\n");
        
        // 尝试恢复总线
        PMBus_BusRecovery();
    }
    
    // 扫描总线
    printf("\nScanning bus...\n");
    PMBus_ScanBus();
}

// 总线恢复
void PMBus_BusRecovery(void) {
    printf("Performing bus recovery...\n");
    
    // 方法1：发送STOP条件
    hi2c1.Instance->CR1 |= I2C_CR1_STOP;
    HAL_Delay(10);
    
    // 方法2：时钟脉冲恢复
    // 将SCL配置为GPIO输出
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = I2C1_SCL_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(I2C1_SCL_GPIO_Port, &GPIO_InitStruct);
    
    // 发送9个时钟脉冲
    for (int i = 0; i < 9; i++) {
        HAL_GPIO_WritePin(I2C1_SCL_GPIO_Port, I2C1_SCL_Pin, GPIO_PIN_RESET);
        HAL_Delay(1);
        HAL_GPIO_WritePin(I2C1_SCL_GPIO_Port, I2C1_SCL_Pin, GPIO_PIN_SET);
        HAL_Delay(1);
    }
    
    // 恢复I2C功能
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
    GPIO_InitStruct.Alternate = GPIO_AF4_I2C1;
    HAL_GPIO_Init(I2C1_SCL_GPIO_Port, &GPIO_InitStruct);
    
    // 重新初始化I2C
    HAL_I2C_DeInit(&hi2c1);
    HAL_Delay(10);
    HAL_I2C_Init(&hi2c1);
    
    printf("Bus recovery complete\n");
}
```

**2. 数据格式错误**：

```
问题现象：
- 读取的电压/电流值异常
- 数值跳变
- 负数出现在不应该的地方

可能原因：
1. 数据格式理解错误
   - Linear11/Linear16/Direct格式混淆
   - 指数计算错误
   - 字节序错误

2. VOUT_MODE未正确读取
   - Linear16需要先读取VOUT_MODE
   - 指数值错误

3. 系数配置错误
   - Direct格式系数不正确

排查步骤：
1. 打印原始数据（十六进制）
2. 验证VOUT_MODE值
3. 手动计算验证
4. 参考设备数据手册
```

**调试代码**：

```c
// 数据格式调试
void PMBus_DebugDataFormat(uint8_t device_addr) {
    uint8_t vout_mode;
    uint16_t vout_raw;
    float vout_float;
    
    printf("\n=== Data Format Debug ===\n");
    
    // 读取VOUT_MODE
    if (PMBus_ReadByte(device_addr, PMBUS_CMD_VOUT_MODE, &vout_mode)) {
        printf("VOUT_MODE: 0x%02X\n", vout_mode);
        printf("  Mode: %d\n", (vout_mode >> 5) & 0x07);
        printf("  Exponent: %d\n", (int8_t)(vout_mode & 0x1F));
    }
    
    // 读取VOUT原始数据
    if (PMBus_ReadWord(device_addr, PMBUS_CMD_READ_VOUT, &vout_raw)) {
        printf("\nREAD_VOUT: 0x%04X\n", vout_raw);
        printf("  Binary: ");
        for (int i = 15; i >= 0; i--) {
            printf("%d", (vout_raw >> i) & 1);
            if (i == 11) printf(" ");  // 分隔指数和尾数
        }
        printf("\n");
        
        // 解析Linear16
        Linear16_Context_t context;
        if (PMBus_InitLinear16Context(device_addr, &context)) {
            vout_float = Linear16_To_Float(vout_raw, &context);
            printf("  Decoded (Linear16): %.4fV\n", vout_float);
            
            // 手动计算验证
            int16_t mantissa = (int16_t)vout_raw;
            int8_t exponent = context.exponent;
            float manual_calc = (float)mantissa;
            if (exponent >= 0) {
                manual_calc *= (1 << exponent);
            } else {
                manual_calc /= (1 << (-exponent));
            }
            printf("  Manual calculation: %.4fV\n", manual_calc);
            printf("  Mantissa: %d, Exponent: %d\n", mantissa, exponent);
        }
    }
    
    // 读取电流（Linear11格式）
    uint16_t iout_raw;
    if (PMBus_ReadWord(device_addr, PMBUS_CMD_READ_IOUT, &iout_raw)) {
        printf("\nREAD_IOUT: 0x%04X\n", iout_raw);
        
        // 解析Linear11
        Linear11_t linear;
        linear.raw = iout_raw;
        printf("  Mantissa: %d (0x%03X)\n", 
               linear.fields.mantissa, linear.fields.mantissa & 0x7FF);
        printf("  Exponent: %d (0x%02X)\n",
               linear.fields.exponent, linear.fields.exponent & 0x1F);
        
        float iout_float = Linear11_To_Float(iout_raw);
        printf("  Decoded: %.4fA\n", iout_float);
    }
}
```

**3. PEC校验失败**：

```
问题现象：
- PEC错误频繁
- 通信不稳定

可能原因：
1. 噪声干扰
   - PCB布线不当
   - 电源噪声
   - EMI干扰

2. 时序问题
   - 时钟频率过高
   - 上升/下降时间不符合规范

3. PEC计算错误
   - 算法实现错误
   - 包含了不应该包含的字节

排查步骤：
1. 降低I2C时钟频率
2. 检查PCB布线
3. 添加滤波电容
4. 验证PEC计算算法
5. 使用示波器检查信号质量
```

**调试代码**：

```c
// PEC调试
void PMBus_DebugPEC(uint8_t device_addr) {
    uint8_t cmd = PMBUS_CMD_READ_VOUT;
    uint16_t data;
    
    printf("\n=== PEC Debug ===\n");
    
    // 手动执行带PEC的读取
    uint8_t pec_data[4];
    uint8_t received_pec;
    uint8_t calculated_pec;
    
    // 构建PEC计算数据
    pec_data[0] = (device_addr << 1) | 0;  // 写地址
    pec_data[1] = cmd;                      // 命令
    pec_data[2] = (device_addr << 1) | 1;  // 读地址
    
    printf("PEC calculation data:\n");
    printf("  Write Address: 0x%02X\n", pec_data[0]);
    printf("  Command: 0x%02X\n", pec_data[1]);
    printf("  Read Address: 0x%02X\n", pec_data[2]);
    
    // 执行读取
    if (PMBus_ReadWord(device_addr, cmd, &data)) {
        pec_data[3] = data & 0xFF;  // 数据低字节
        
        printf("  Data Low: 0x%02X\n", pec_data[3]);
        
        // 计算PEC
        calculated_pec = SMBus_CalculatePEC(pec_data, 4);
        printf("\nCalculated PEC: 0x%02X\n", calculated_pec);
        
        // 读取实际PEC（需要修改读取函数返回PEC）
        // received_pec = ...
        // printf("Received PEC: 0x%02X\n", received_pec);
        
        // 逐步计算PEC
        printf("\nStep-by-step PEC calculation:\n");
        uint8_t crc = 0x00;
        for (int i = 0; i < 4; i++) {
            printf("  Step %d: CRC=0x%02X, Data=0x%02X", 
                   i, crc, pec_data[i]);
            crc = SMBus_UpdatePEC(crc, pec_data[i]);
            printf(" → CRC=0x%02X\n", crc);
        }
    }
}
```

### 性能优化

**1. 批量读取优化**：

```c
// 批量读取遥测数据
typedef struct {
    uint8_t cmd;
    uint16_t *data;
} BatchRead_Item_t;

bool PMBus_BatchRead(uint8_t device_addr, 
                     BatchRead_Item_t *items, 
                     uint8_t count) {
    for (uint8_t i = 0; i < count; i++) {
        if (!PMBus_ReadWord(device_addr, items[i].cmd, items[i].data)) {
            return false;
        }
    }
    return true;
}

// 使用示例
void PMBus_FastTelemetry(uint8_t device_addr) {
    uint16_t vout_raw, iout_raw, pout_raw, temp_raw;
    
    BatchRead_Item_t items[] = {
        {PMBUS_CMD_READ_VOUT, &vout_raw},
        {PMBUS_CMD_READ_IOUT, &iout_raw},
        {PMBUS_CMD_READ_POUT, &pout_raw},
        {PMBUS_CMD_READ_TEMPERATURE_1, &temp_raw},
    };
    
    uint32_t start = HAL_GetTick();
    
    if (PMBus_BatchRead(device_addr, items, 4)) {
        uint32_t elapsed = HAL_GetTick() - start;
        printf("Batch read completed in %lu ms\n", elapsed);
        
        // 解码数据
        // ...
    }
}
```

**2. 缓存优化**：

```c
// 遥测数据缓存
typedef struct {
    float voltage;
    float current;
    float power;
    float temperature;
    uint32_t timestamp;
    bool valid;
} TelemetryCache_t;

static TelemetryCache_t g_telemetry_cache[PMBUS_MAX_DEVICES];

// 带缓存的读取
bool PMBus_ReadVoltage_Cached(uint8_t device_addr, 
                               float *voltage,
                               uint32_t max_age_ms) {
    uint8_t device_index = device_addr - 0x58;  // 假设地址从0x58开始
    
    if (device_index >= PMBUS_MAX_DEVICES) {
        return false;
    }
    
    TelemetryCache_t *cache = &g_telemetry_cache[device_index];
    
    // 检查缓存是否有效
    if (cache->valid && 
        (HAL_GetTick() - cache->timestamp) < max_age_ms) {
        *voltage = cache->voltage;
        return true;
    }
    
    // 缓存过期，重新读取
    if (PMBus_ReadVoltage(device_addr, voltage)) {
        cache->voltage = *voltage;
        cache->timestamp = HAL_GetTick();
        cache->valid = true;
        return true;
    }
    
    return false;
}
```

## 最佳实践

### 设计建议

**1. 硬件设计**：

```
上拉电阻选择：
- 100kHz：4.7kΩ
- 400kHz：2.2kΩ
- 考虑总线电容

PCB布线：
- SCL/SDA走线尽量短（<30cm）
- 避免平行长距离走线
- 远离高频信号
- 添加地平面

ESD保护：
- 在SCL/SDA线上添加TVS二极管
- 靠近连接器放置

电源设计：
- 为PMBus设备提供干净的电源
- 添加去耦电容
- 考虑隔离

连接器：
- 使用带锁扣的连接器
- 考虑热插拔需求
- 预留测试点
```

**2. 软件设计**：

```c
// 错误处理
#define PMBUS_MAX_RETRIES 3

bool PMBus_ReadWord_Robust(uint8_t device_addr, 
                            uint8_t cmd,
                            uint16_t *data) {
    for (uint8_t retry = 0; retry < PMBUS_MAX_RETRIES; retry++) {
        if (PMBus_ReadWord(device_addr, cmd, data)) {
            return true;
        }
        
        // 重试前延时
        HAL_Delay(10);
        
        // 如果是最后一次重试，尝试恢复总线
        if (retry == PMBUS_MAX_RETRIES - 1) {
            PMBus_BusRecovery();
        }
    }
    
    return false;
}

// 超时保护
bool PMBus_ReadWord_WithTimeout(uint8_t device_addr,
                                 uint8_t cmd,
                                 uint16_t *data,
                                 uint32_t timeout_ms) {
    uint32_t start = HAL_GetTick();
    
    while (HAL_GetTick() - start < timeout_ms) {
        if (PMBus_ReadWord(device_addr, cmd, data)) {
            return true;
        }
        
        HAL_Delay(1);
    }
    
    return false;
}

// 参数验证
bool PMBus_SetVoltage_Safe(uint8_t device_addr, float voltage) {
    // 读取电压范围
    float vout_max;
    if (!PMBus_GetVoltageMax(device_addr, &vout_max)) {
        return false;
    }
    
    // 验证范围
    if (voltage < 0.0 || voltage > vout_max) {
        printf("Error: Voltage %.2fV out of range (0 - %.2fV)\n",
               voltage, vout_max);
        return false;
    }
    
    // 设置电压
    return PMBus_SetVoltage(device_addr, voltage);
}
```

**3. 测试策略**：

```
单元测试：
- 数据格式转换函数
- PEC计算函数
- 命令编解码函数

集成测试：
- 设备初始化流程
- 遥测读取功能
- 故障检测和恢复

系统测试：
- 电源排序
- 冗余切换
- 长时间稳定性测试

压力测试：
- 高频率遥测读取
- 故障注入测试
- 边界条件测试
```

## 总结

### 关键要点

1. **PMBus协议特点**：
   - 基于SMBus的数字电源管理协议
   - 标准化命令集和数据格式
   - 支持遥测、控制、配置、故障管理
   - 广泛应用于服务器、通信、工业领域

2. **数据格式**：
   - Linear11：11位尾数+5位指数
   - Linear16：16位尾数+外部指数
   - Direct：用户定义系数
   - 正确理解和转换是关键

3. **命令分类**：
   - 控制命令：OPERATION、ON_OFF_CONFIG
   - 配置命令：VOUT_COMMAND、限制设置
   - 遥测命令：READ_VOUT/IOUT/TEMPERATURE
   - 状态命令：STATUS_WORD及详细状态

4. **实现要点**：
   - 分层架构设计
   - 错误处理和重试机制
   - 超时保护
   - 数据缓存优化

5. **应用场景**：
   - 服务器电源管理
   - 电源排序控制
   - 动态电压调节
   - 冗余和故障管理

### 学习路径

**初级阶段**：
1. 掌握SMBus基础
2. 理解PMBus数据格式
3. 实现基本的读写操作
4. 完成简单的遥测读取

**中级阶段**：
1. 实现完整的命令集
2. 开发设备驱动
3. 实现故障检测
4. 完成电源控制功能

**高级阶段**：
1. 实现复杂的电源管理策略
2. 优化性能和可靠性
3. 开发完整的管理系统
4. 处理各种异常情况

### 下一步学习

**相关主题**：
- [SMBus协议详解](../intermediate/05-smbus-protocol.html)
- [I2C硬件接口](../beginner/03-i2c-hardware.html)
- [开关电源设计](../../03-power-management/intermediate/04-switching-power-supply.html)

**进阶方向**：
- AVSBus协议（自适应电压调节）
- PMBus从机设备开发
- 电源管理算法优化
- 故障预测和诊断

## 参考资料

1. **官方规范**：
   - PMBus Power System Management Protocol Specification (Part I & II)
   - SMBus Specification Version 3.0
   - I2C-bus Specification

2. **应用笔记**：
   - Texas Instruments: PMBus Design Guide
   - Analog Devices: Digital Power Management
   - Infineon: PMBus Implementation Guide

3. **开发工具**：
   - PMBus命令分析器
   - 数字电源开发套件
   - 协议分析仪

4. **在线资源**：
   - PMBus Implementers Forum (pmbus.org)
   - 厂商技术支持论坛
   - 开源PMBus驱动代码

5. **推荐书籍**：
   - 《Digital Power Management》
   - 《Power Supply Design》
   - 《Embedded Systems Design》

---

**文档版本**: 1.0  
**最后更新**: 2024-01-15  
**作者**: 嵌入式知识平台

如有问题或建议，欢迎反馈！
