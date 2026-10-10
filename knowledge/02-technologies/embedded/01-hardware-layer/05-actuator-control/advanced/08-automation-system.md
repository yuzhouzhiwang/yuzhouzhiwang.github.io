---
title: "多路继电器自动化控制系统"
description: "基于STM32和PCF8574 I2C扩展的16路继电器控制系统，实现顺序控制、互锁保护、条件触发和Modbus RTU通信，适用于工业自动化和楼宇控制场景"
slug: "multi-relay-automation-system"

domain: "底层硬件层"
module: "执行器控制"
content_type: "project"
skill_level: "advanced"

tags:
  - 继电器
  - 自动化控制
  - Modbus
  - PCF8574
  - 顺序控制
  - 互锁保护
prerequisites:
  - "beginner/04-relay-control"
related_contents:
  - "advanced/07-smart-socket-project"
  - "advanced/09-environment-control"

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
is_featured: false
is_premium: false

keywords:
  - 多路继电器控制
  - 自动化控制系统
  - Modbus RTU
  - PCF8574扩展
  - 顺序控制
cover_image: ""
---

# 多路继电器自动化控制系统

## 项目概述

本项目构建一个16路继电器自动化控制系统，具备：

- **16路独立控制**：通过2片PCF8574 I2C扩展，用4根线控制16路继电器
- **顺序控制**：按预设时序依次启动/停止设备（如生产线启动顺序）
- **互锁保护**：防止互斥设备同时运行（如正反转不能同时接通）
- **条件触发**：传感器输入触发继电器动作（如温度超限启动风扇）
- **Modbus RTU**：标准工业通信协议，可接入SCADA系统

**硬件清单**：

| 器件 | 型号 | 数量 |
|------|------|------|
| 主控 | STM32F103C8T6 | 1 |
| I2C扩展 | PCF8574 | 2 |
| 继电器模块 | 8路5V继电器板 | 2 |
| RS485收发器 | MAX485 | 1 |
| 电源 | 12V/2A + 5V/3A | 1 |

## 背景知识

### 工业自动化层次结构

现代工业自动化系统采用分层架构，从底层设备到顶层管理形成完整的控制体系：

```
┌─────────────────────────────────────────────────────────┐
│  企业层 (Enterprise Level)                               │
│  ERP、MES、生产计划、资源管理                            │
└─────────────────────────────────────────────────────────┘
                          ↕ Ethernet/OPC UA
┌─────────────────────────────────────────────────────────┐
│  监控层 (Supervisory Level)                              │
│  SCADA、HMI、数据采集、报表生成                          │
└─────────────────────────────────────────────────────────┘
                          ↕ Modbus TCP/Profinet
┌─────────────────────────────────────────────────────────┐
│  控制层 (Control Level)                                  │
│  PLC、DCS、运动控制器、逻辑控制                          │
└─────────────────────────────────────────────────────────┘
                          ↕ Modbus RTU/CAN/Profibus
┌─────────────────────────────────────────────────────────┐
│  现场层 (Field Level)                                    │
│  传感器、执行器、继电器、变频器、阀门                    │
└─────────────────────────────────────────────────────────┘
```

**各层职责**：

1. **现场层（Field Level）**：
   - 直接与物理过程交互的设备
   - 传感器采集温度、压力、流量等物理量
   - 执行器（继电器、电机、阀门）执行控制命令
   - 本项目的16路继电器模块属于此层

2. **控制层（Control Level）**：
   - 实时逻辑控制和数据处理
   - PLC执行梯形图/结构化文本程序
   - 运动控制器执行轨迹规划
   - 本项目的STM32主控承担此层功能

3. **监控层（Supervisory Level）**：
   - 人机交互界面（HMI）
   - 数据采集与监视控制（SCADA）
   - 历史数据存储和趋势分析
   - 报警管理和事件记录

4. **企业层（Enterprise Level）**：
   - 生产计划和调度
   - 制造执行系统（MES）
   - 企业资源规划（ERP）
   - 质量管理和追溯

**通信协议选择**：

| 层级 | 常用协议 | 特点 | 应用场景 |
|------|---------|------|---------|
| 企业层↔监控层 | OPC UA, MQTT | 跨平台、安全、语义化 | 云端集成、远程监控 |
| 监控层↔控制层 | Modbus TCP, Profinet | 以太网、高速、大数据量 | 工厂内部网络 |
| 控制层↔现场层 | Modbus RTU, CAN, Profibus | 串行总线、实时性强、抗干扰 | 现场设备互联 |

本项目采用**Modbus RTU**作为控制层与现场层的通信协议，原因：
- 协议简单，易于实现
- 工业标准，兼容性好
- RS485物理层，抗干扰能力强
- 支持多主多从拓扑

### Modbus RTU协议详解

Modbus RTU是Modbus协议的串行传输模式，采用二进制编码和CRC校验。

#### 帧结构

Modbus RTU帧由以下字段组成：

```
┌──────┬──────┬──────────┬──────────┬─────┬─────┐
│ 从站 │ 功能 │ 数据地址 │ 数据内容 │ CRC │ CRC │
│ 地址 │ 码   │ (2字节)  │ (N字节)  │ 低  │ 高  │
│ 1B   │ 1B   │          │          │ 1B  │ 1B  │
└──────┴──────┴──────────┴──────────┴─────┴─────┘
  ↑      ↑        ↑           ↑         ↑
  1-247  见下表   大端序      功能码相关  CRC-16/Modbus
```

**字节级示例**（读取从站1的线圈0~7状态）：

```
请求帧：
  01    03    00 00    00 08    44 0C
  │     │     │        │        └─ CRC-16 (0x0C44)
  │     │     │        └─ 数量：8个线圈
  │     │     └─ 起始地址：0x0000
  │     └─ 功能码：0x03 (读保持寄存器)
  └─ 从站地址：1

响应帧：
  01    03    10    12 34 56 78 ...    XX XX
  │     │     │     │                  └─ CRC-16
  │     │     │     └─ 数据内容（16字节）
  │     │     └─ 字节数：16
  │     └─ 功能码：0x03
  └─ 从站地址：1
```

#### 常用功能码

| 功能码 | 名称 | 操作对象 | 说明 |
|--------|------|---------|------|
| 0x01 | Read Coils | 线圈（输出） | 读取1~2000个线圈状态 |
| 0x02 | Read Discrete Inputs | 离散输入 | 读取1~2000个输入状态 |
| 0x03 | Read Holding Registers | 保持寄存器 | 读取1~125个16位寄存器 |
| 0x04 | Read Input Registers | 输入寄存器 | 读取1~125个16位寄存器 |
| 0x05 | Write Single Coil | 线圈 | 写单个线圈（0xFF00=ON, 0x0000=OFF） |
| 0x06 | Write Single Register | 保持寄存器 | 写单个16位寄存器 |
| 0x0F | Write Multiple Coils | 线圈 | 写多个线圈（1~1968个） |
| 0x10 | Write Multiple Registers | 保持寄存器 | 写多个寄存器（1~123个） |

**数据模型**：

Modbus定义了4种数据类型：

```
地址空间：
  线圈（Coils）：           0x0000 ~ 0xFFFF  读写  1位  输出继电器
  离散输入（Discrete）：    0x0000 ~ 0xFFFF  只读  1位  输入开关
  输入寄存器（Input Reg）： 0x0000 ~ 0xFFFF  只读  16位 ADC采样值
  保持寄存器（Holding Reg）：0x0000 ~ 0xFFFF  读写  16位 配置参数
```

#### CRC-16/Modbus计算

Modbus RTU使用CRC-16校验，多项式为0xA001（反向表示）：

```c
uint16_t modbus_crc16(uint8_t *buf, uint16_t len) {
    uint16_t crc = 0xFFFF;  // 初始值
    for (uint16_t i = 0; i < len; i++) {
        crc ^= buf[i];      // 与当前字节异或
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;  // 多项式
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;  // 低字节在前，高字节在后
}
```

**CRC计算示例**：

```
数据：01 03 00 00 00 08
步骤：
  初始CRC = 0xFFFF
  处理0x01: CRC = 0xFF00 ^ 0x01 = 0xFF01 → 移位8次 → 0x0C44
  处理0x03: ...
  最终CRC = 0x0C44
  帧尾追加：44 0C（低字节在前）
```

### RS485电气特性

RS485是Modbus RTU的物理层标准，采用差分信号传输。

#### 差分信号原理

RS485使用一对双绞线（A+和B-）传输差分信号：

```
发送端：                      接收端：
  ┌────┐                      ┌────┐
  │ TX │─ A+ ─────────────── A+ ─│ RX │
  │    │                          │    │
  │    │─ B- ─────────────────── B- ─│    │
  └────┘                      └────┘
         ↑                      ↑
      差分电压              差分电压
      VA - VB              VA - VB

逻辑1（Mark）：  VA - VB < -200mV  (B电压高于A)
逻辑0（Space）： VA - VB > +200mV  (A电压高于B)
```

**抗干扰原理**：
- 共模干扰（如电磁辐射）同时影响A和B线
- 差分接收器只关心VA-VB，共模干扰被抵消
- 双绞线绞合进一步减少电磁耦合

#### 总线拓扑

RS485支持多点通信（最多32个节点，使用中继器可扩展到256个）：

```
主站                从站1      从站2      从站3
┌────┐             ┌────┐    ┌────┐    ┌────┐
│ PC │             │ STM│    │ STM│    │ STM│
│    │             │ 32 │    │ 32 │    │ 32 │
└─┬──┘             └─┬──┘    └─┬──┘    └─┬──┘
  │ A+ ───────────────┼────────┼────────┼───
  │ B- ───────────────┼────────┼────────┼───
  │ GND ──────────────┼────────┼────────┼───
  │                   │        │        │
 120Ω               (无)     (无)     120Ω
 终端电阻                              终端电阻
```

**关键参数**：

| 参数 | 典型值 | 说明 |
|------|--------|------|
| 最大传输距离 | 1200m | 9600bps时，更高波特率需缩短距离 |
| 最大节点数 | 32个 | 标准负载，使用中继器可扩展 |
| 差分电压 | ±1.5V ~ ±6V | 发送端输出电压 |
| 接收灵敏度 | ±200mV | 接收端最小可识别电压差 |
| 共模电压范围 | -7V ~ +12V | 允许的地电位差 |
| 波特率 | 9600 ~ 115200 | 常用115200bps |

#### 终端电阻

总线两端必须接120Ω终端电阻，防止信号反射：

```
为什么需要终端电阻？
  信号在传输线末端遇到阻抗不匹配时会反射
  反射信号叠加在原信号上，导致波形失真
  120Ω匹配双绞线特性阻抗（约120Ω）

接法：
  ┌─ A+ ─┬─ 120Ω ─┬─ B- ─┐
  │      │         │      │
  └──────┴─────────┴──────┘
         总线末端节点
```

**错误接法**：
- ❌ 每个节点都接终端电阻 → 总线负载过重，电压不足
- ❌ 不接终端电阻 → 信号反射，通信不稳定
- ✅ 仅在总线两端接终端电阻

#### MAX485芯片

MAX485是常用的RS485收发器芯片：

```
引脚定义：
  RO (Receiver Output)：  接MCU的RX引脚
  RE (Receiver Enable)：  低电平使能接收
  DE (Driver Enable)：    高电平使能发送
  DI (Driver Input)：     接MCU的TX引脚
  A：  差分信号正端
  B：  差分信号负端
  VCC：5V电源
  GND：地

典型连接：
  STM32_TX ──→ DI
  STM32_RX ←── RO
  STM32_GPIO ─→ DE/RE（通常短接）
  A ──→ 总线A+
  B ──→ 总线B-
```

**半双工控制**：

RS485是半双工通信，同一时刻只能发送或接收：

```c
// 发送前使能发送
HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_SET);
HAL_UART_Transmit(&huart1, tx_buf, tx_len, 100);
HAL_Delay(1);  // 等待发送完成
HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_RESET);

// 接收时DE/RE保持低电平
HAL_UART_Receive(&huart1, rx_buf, rx_len, 1000);
```

## PCF8574驱动

PCF8574是8位I2C I/O扩展芯片，两片级联实现16路输出：

```c
#include "i2c.h"

// PCF8574地址（A0~A2引脚决定）
#define PCF8574_ADDR1  0x20  // 第1片：A2A1A0=000
#define PCF8574_ADDR2  0x21  // 第2片：A2A1A0=001

// 继电器状态（16位，每位对应一路，1=断开，0=吸合）
// PCF8574输出低电平时继电器吸合（低电平触发）
static uint8_t relay_state[2] = {0xFF, 0xFF};  // 初始全断开

// 写PCF8574输出
static void pcf8574_write(uint8_t addr, uint8_t data) {
    HAL_I2C_Master_Transmit(&hi2c1, addr << 1, &data, 1, 100);
}

// 设置单路继电器
void relay_set(uint8_t ch, bool on) {
    if (ch >= 16) return;
    uint8_t chip = ch / 8;
    uint8_t bit  = ch % 8;

    if (on) relay_state[chip] &= ~(1 << bit);   // 低电平吸合
    else    relay_state[chip] |=  (1 << bit);   // 高电平断开

    uint8_t addr = (chip == 0) ? PCF8574_ADDR1 : PCF8574_ADDR2;
    pcf8574_write(addr, relay_state[chip]);
}

// 获取继电器状态
bool relay_get(uint8_t ch) {
    if (ch >= 16) return false;
    uint8_t chip = ch / 8;
    uint8_t bit  = ch % 8;
    return !(relay_state[chip] & (1 << bit));  // 0=吸合=true
}

// 批量设置（16位掩码，1=吸合）
void relay_set_all(uint16_t mask) {
    relay_state[0] = ~(mask & 0xFF);
    relay_state[1] = ~((mask >> 8) & 0xFF);
    pcf8574_write(PCF8574_ADDR1, relay_state[0]);
    pcf8574_write(PCF8574_ADDR2, relay_state[1]);
}
```

## 互锁保护

防止互斥继电器同时吸合（如电机正反转）：

```c
// 互锁组定义：同一组内只能有一路吸合
typedef struct {
    uint8_t  channels[8];  // 互锁的继电器通道号
    uint8_t  count;        // 通道数量
} InterlockGroup;

#define MAX_INTERLOCK_GROUPS  4
InterlockGroup interlock_groups[MAX_INTERLOCK_GROUPS];
uint8_t        interlock_count = 0;

// 注册互锁组（如通道0和1互锁：电机正反转）
void interlock_register(uint8_t *channels, uint8_t count) {
    if (interlock_count >= MAX_INTERLOCK_GROUPS) return;
    InterlockGroup *g = &interlock_groups[interlock_count++];
    memcpy(g->channels, channels, count);
    g->count = count;
}

// 带互锁检查的继电器设置
bool relay_set_safe(uint8_t ch, bool on) {
    if (!on) {
        relay_set(ch, false);
        return true;
    }

    // 检查是否与互锁组中其他通道冲突
    for (int i = 0; i < interlock_count; i++) {
        InterlockGroup *g = &interlock_groups[i];
        bool in_group = false;
        for (int j = 0; j < g->count; j++) {
            if (g->channels[j] == ch) { in_group = true; break; }
        }
        if (!in_group) continue;

        // 先断开同组其他通道
        for (int j = 0; j < g->count; j++) {
            if (g->channels[j] != ch && relay_get(g->channels[j])) {
                relay_set(g->channels[j], false);
                HAL_Delay(100);  // 等待继电器完全断开
            }
        }
    }

    relay_set(ch, true);
    return true;
}
```

## 顺序控制

按预设时序执行一系列继电器动作：

```c
// 顺序控制步骤
typedef struct {
    uint8_t  channel;    // 继电器通道
    bool     action;     // true=吸合，false=断开
    uint32_t delay_ms;   // 执行后等待时间
} SeqStep;

// 示例：生产线启动顺序
// 1. 启动传送带（CH0）→ 等2秒
// 2. 启动加热器（CH1）→ 等5秒
// 3. 启动压力机（CH2）→ 等1秒
// 4. 启动出料机（CH3）
SeqStep startup_seq[] = {
    {0, true,  2000},
    {1, true,  5000},
    {2, true,  1000},
    {3, true,     0},
};

SeqStep shutdown_seq[] = {
    {3, false, 1000},
    {2, false, 1000},
    {1, false, 2000},
    {0, false,    0},
};

void run_sequence(SeqStep *seq, uint8_t steps) {
    for (int i = 0; i < steps; i++) {
        relay_set_safe(seq[i].channel, seq[i].action);
        if (seq[i].delay_ms > 0) HAL_Delay(seq[i].delay_ms);
    }
}
```

## 条件触发

传感器输入触发继电器动作：

```c
// 触发条件类型
typedef enum {
    TRIGGER_ADC_ABOVE,   // ADC值超过阈值
    TRIGGER_ADC_BELOW,   // ADC值低于阈值
    TRIGGER_GPIO_HIGH,   // GPIO变高
    TRIGGER_GPIO_LOW,    // GPIO变低
} TriggerType;

typedef struct {
    TriggerType type;
    uint8_t     input_ch;    // 输入通道（ADC或GPIO编号）
    float       threshold;   // 阈值
    uint8_t     relay_ch;    // 触发的继电器通道
    bool        relay_action;// 触发动作
    uint32_t    debounce_ms; // 防抖时间
    uint32_t    last_trigger;
} TriggerRule;

#define MAX_RULES  8
TriggerRule rules[MAX_RULES];
uint8_t     rule_count = 0;

void trigger_check_all(void) {
    uint32_t now = HAL_GetTick();

    for (int i = 0; i < rule_count; i++) {
        TriggerRule *r = &rules[i];
        if (now - r->last_trigger < r->debounce_ms) continue;

        bool triggered = false;
        float val = 0;

        switch (r->type) {
            case TRIGGER_ADC_ABOVE:
                val = adc_read(r->input_ch);
                triggered = (val > r->threshold);
                break;
            case TRIGGER_ADC_BELOW:
                val = adc_read(r->input_ch);
                triggered = (val < r->threshold);
                break;
            case TRIGGER_GPIO_HIGH:
                triggered = HAL_GPIO_ReadPin(input_ports[r->input_ch],
                                             input_pins[r->input_ch]);
                break;
            case TRIGGER_GPIO_LOW:
                triggered = !HAL_GPIO_ReadPin(input_ports[r->input_ch],
                                              input_pins[r->input_ch]);
                break;
        }

        if (triggered) {
            relay_set_safe(r->relay_ch, r->relay_action);
            r->last_trigger = now;
        }
    }
}
```

## Modbus RTU通信

实现标准Modbus RTU从站，支持上位机读写继电器状态：

```c
// Modbus RTU完整实现
// 支持功能码：0x01(读线圈), 0x05(写单线圈), 0x0F(写多线圈)
// 支持功能码：0x03(读保持寄存器), 0x06(写单寄存器), 0x10(写多寄存器)

#define MODBUS_ADDR  1  // 从站地址
#define MODBUS_TIMEOUT_MS  100  // 帧间隔超时

// Modbus异常码
#define MODBUS_EX_ILLEGAL_FUNCTION      0x01
#define MODBUS_EX_ILLEGAL_DATA_ADDRESS  0x02
#define MODBUS_EX_ILLEGAL_DATA_VALUE    0x03
#define MODBUS_EX_SLAVE_DEVICE_FAILURE  0x04

uint16_t modbus_crc16(uint8_t *buf, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= buf[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
            else              crc >>= 1;
        }
    }
    return crc;
}

// 发送异常响应
void modbus_send_exception(uint8_t func, uint8_t ex_code,
                           uint8_t *resp, uint16_t *resp_len) {
    resp[0] = MODBUS_ADDR;
    resp[1] = func | 0x80;  // 功能码最高位置1表示异常
    resp[2] = ex_code;
    *resp_len = 3;
    uint16_t crc = modbus_crc16(resp, 3);
    resp[3] = crc & 0xFF;
    resp[4] = crc >> 8;
    *resp_len = 5;
}

void modbus_process(uint8_t *req, uint16_t req_len,
                    uint8_t *resp, uint16_t *resp_len) {
    // 校验帧长度
    if (req_len < 4) return;
    
    // 校验CRC
    uint16_t crc_recv = req[req_len-2] | (req[req_len-1] << 8);
    uint16_t crc_calc = modbus_crc16(req, req_len - 2);
    if (crc_recv != crc_calc) return;  // CRC错误，丢弃帧
    
    // 校验从站地址
    if (req[0] != MODBUS_ADDR) return;

    uint8_t func = req[1];
    uint16_t addr = (req[2] << 8) | req[3];

    switch (func) {
        case 0x01: {  // 读线圈状态
            uint16_t count = (req[4] << 8) | req[5];
            if (count < 1 || count > 2000 || addr + count > 16) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_ADDRESS,
                                     resp, resp_len);
                return;
            }
            uint8_t byte_count = (count + 7) / 8;
            resp[0] = MODBUS_ADDR;
            resp[1] = 0x01;
            resp[2] = byte_count;
            memset(&resp[3], 0, byte_count);
            for (int i = 0; i < count; i++) {
                if (relay_get(addr + i))
                    resp[3 + i/8] |= (1 << (i % 8));
            }
            *resp_len = 3 + byte_count;
            break;
        }
        case 0x03: {  // 读保持寄存器
            uint16_t count = (req[4] << 8) | req[5];
            if (count < 1 || count > 125) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_VALUE,
                                     resp, resp_len);
                return;
            }
            resp[0] = MODBUS_ADDR;
            resp[1] = 0x03;
            resp[2] = count * 2;
            for (int i = 0; i < count; i++) {
                uint16_t val = holding_register_read(addr + i);
                resp[3 + i*2] = val >> 8;
                resp[4 + i*2] = val & 0xFF;
            }
            *resp_len = 3 + count * 2;
            break;
        }
        case 0x05: {  // 写单线圈
            uint16_t val = (req[4] << 8) | req[5];
            if (val != 0xFF00 && val != 0x0000) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_VALUE,
                                     resp, resp_len);
                return;
            }
            if (addr >= 16) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_ADDRESS,
                                     resp, resp_len);
                return;
            }
            relay_set_safe(addr, val == 0xFF00);
            memcpy(resp, req, 6);  // 回显请求
            *resp_len = 6;
            break;
        }
        case 0x06: {  // 写单寄存器
            uint16_t val = (req[4] << 8) | req[5];
            if (!holding_register_write(addr, val)) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_ADDRESS,
                                     resp, resp_len);
                return;
            }
            memcpy(resp, req, 6);
            *resp_len = 6;
            break;
        }
        case 0x0F: {  // 写多线圈
            uint16_t count = (req[4] << 8) | req[5];
            uint8_t byte_count = req[6];
            if (count < 1 || count > 1968 || addr + count > 16) {
                modbus_send_exception(func, MODBUS_EX_ILLEGAL_DATA_ADDRESS,
                                     resp, resp_len);
                return;
            }
            for (int i = 0; i < count; i++) {
                bool state = (req[7 + i/8] >> (i % 8)) & 0x01;
                relay_set_safe(addr + i, state);
            }
            resp[0] = MODBUS_ADDR;
            resp[1] = 0x0F;
            resp[2] = req[2];
            resp[3] = req[3];
            resp[4] = req[4];
            resp[5] = req[5];
            *resp_len = 6;
            break;
        }
        default:
            modbus_send_exception(func, MODBUS_EX_ILLEGAL_FUNCTION,
                                 resp, resp_len);
            return;
    }

    // 追加CRC
    uint16_t crc = modbus_crc16(resp, *resp_len);
    resp[(*resp_len)++] = crc & 0xFF;
    resp[(*resp_len)++] = crc >> 8;
}

// 保持寄存器读写（示例映射）
uint16_t holding_register_read(uint16_t addr) {
    switch (addr) {
        case 0x0000:  // 继电器状态掩码
            return (relay_state[1] << 8) | relay_state[0];
        case 0x0001:  // 系统状态
            return system_status;
        case 0x0002:  // ADC输入1
            return adc_read(0);
        case 0x0003:  // ADC输入2
            return adc_read(1);
        case 0x0010:  // 顺序控制状态
            return sequence_state;
        case 0x0020:  // 系统运行时间（秒）
            return HAL_GetTick() / 1000;
        default:
            return 0;
    }
}

bool holding_register_write(uint16_t addr, uint16_t val) {
    switch (addr) {
        case 0x0000:  // 批量设置继电器
            relay_set_all(val);
            return true;
        case 0x0010:  // 顺序控制命令
            if (val == 1) run_sequence(startup_seq, 4);
            else if (val == 2) run_sequence(shutdown_seq, 4);
            return true;
        default:
            return false;  // 只读或不存在的地址
    }
}
```

### Modbus TCP网关实现

将Modbus RTU设备桥接到以太网，实现远程访问：

```c
// 使用W5500以太网模块实现Modbus TCP网关
// Modbus TCP = MBAP头(7字节) + Modbus PDU

#include "w5500.h"

#define MODBUS_TCP_PORT  502
#define MAX_TCP_CLIENTS  4

typedef struct {
    uint16_t transaction_id;  // 事务标识符
    uint16_t protocol_id;     // 协议标识符（0=Modbus）
    uint16_t length;          // 后续字节数
    uint8_t  unit_id;         // 单元标识符（从站地址）
} MBAP_Header;

void modbus_tcp_gateway_task(void) {
    uint8_t sock = 0;
    uint8_t rx_buf[260];
    uint8_t tx_buf[260];
    uint16_t rx_len, tx_len;

    // 监听TCP 502端口
    if (getSn_SR(sock) == SOCK_CLOSED) {
        socket(sock, Sn_MR_TCP, MODBUS_TCP_PORT, 0);
        listen(sock);
    }

    if (getSn_SR(sock) == SOCK_ESTABLISHED) {
        rx_len = getSn_RX_RSR(sock);
        if (rx_len >= 7) {  // 至少有MBAP头
            recv(sock, rx_buf, rx_len);

            // 解析MBAP头
            MBAP_Header *mbap = (MBAP_Header*)rx_buf;
            mbap->transaction_id = ntohs(mbap->transaction_id);
            mbap->protocol_id = ntohs(mbap->protocol_id);
            mbap->length = ntohs(mbap->length);

            if (mbap->protocol_id != 0) {
                disconnect(sock);
                return;
            }

            // 提取Modbus PDU（去掉MBAP头）
            uint8_t *pdu = &rx_buf[7];
            uint16_t pdu_len = mbap->length - 1;

            // 转发到Modbus RTU从站
            uint8_t rtu_req[260];
            rtu_req[0] = mbap->unit_id;  // 从站地址
            memcpy(&rtu_req[1], pdu, pdu_len);
            uint16_t crc = modbus_crc16(rtu_req, pdu_len + 1);
            rtu_req[pdu_len + 1] = crc & 0xFF;
            rtu_req[pdu_len + 2] = crc >> 8;

            // 通过RS485发送
            HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_SET);
            HAL_UART_Transmit(&huart1, rtu_req, pdu_len + 3, 100);
            HAL_Delay(1);
            HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_RESET);

            // 接收RTU响应
            uint8_t rtu_resp[260];
            uint16_t rtu_resp_len = 0;
            HAL_UART_Receive(&huart1, rtu_resp, 260, 1000);
            // 实际应用中需要根据功能码计算响应长度

            // 去掉从站地址和CRC，提取PDU
            uint8_t *resp_pdu = &rtu_resp[1];
            uint16_t resp_pdu_len = rtu_resp_len - 3;

            // 构造MBAP响应
            MBAP_Header *resp_mbap = (MBAP_Header*)tx_buf;
            resp_mbap->transaction_id = htons(mbap->transaction_id);
            resp_mbap->protocol_id = 0;
            resp_mbap->length = htons(resp_pdu_len + 1);
            resp_mbap->unit_id = mbap->unit_id;
            memcpy(&tx_buf[7], resp_pdu, resp_pdu_len);
            tx_len = 7 + resp_pdu_len;

            // 发送TCP响应
            send(sock, tx_buf, tx_len);
        }
    }
}
```

### PLC梯形图等效C代码

将PLC梯形图逻辑转换为C代码实现：

```c
// PLC梯形图示例：启动/停止按钮控制电机
// 
//  ┌─┤ START ├─┤ /STOP ├─┤ /ALARM ├─( MOTOR )─┐
//  │                                            │
//  └─┤ MOTOR ├────────────────────────────────┘
//
// 逻辑：按下START且未按STOP且无ALARM时启动电机，电机自保持

typedef struct {
    bool START;   // 启动按钮（常开）
    bool STOP;    // 停止按钮（常闭）
    bool ALARM;   // 报警信号（常闭）
    bool MOTOR;   // 电机输出
} PLC_IO;

PLC_IO plc;

void plc_scan_cycle(void) {
    // 读取输入
    plc.START = HAL_GPIO_ReadPin(START_GPIO_Port, START_Pin);
    plc.STOP  = !HAL_GPIO_ReadPin(STOP_GPIO_Port, STOP_Pin);  // 常闭
    plc.ALARM = !HAL_GPIO_ReadPin(ALARM_GPIO_Port, ALARM_Pin);

    // 梯形图逻辑
    bool rung1 = plc.START && plc.STOP && plc.ALARM;  // 第一条支路
    bool rung2 = plc.MOTOR;                           // 第二条支路（自保持）
    plc.MOTOR = rung1 || rung2;

    // 写入输出
    relay_set(0, plc.MOTOR);
}

// 更复杂的梯形图：三台电机顺序启动
//
//  ┌─┤ START ├─┤ /M1 ├─────────────────( M1 )─┐
//  │                                            │
//  └─┤ M1 ├───────────────────────────────────┘
//
//  ┌─┤ M1 ├─┤ TON_1 ├─┤ /M2 ├───────────( M2 )─┐
//  │                                            │
//  └─┤ M2 ├───────────────────────────────────┘
//
//  ┌─┤ M2 ├─┤ TON_2 ├─┤ /M3 ├───────────( M3 )─┐
//  │                                            │
//  └─┤ M3 ├───────────────────────────────────┘

typedef struct {
    bool IN;
    bool Q;
    uint32_t PT;  // 预设时间（ms）
    uint32_t ET;  // 经过时间（ms）
    uint32_t start_time;
} TON_Timer;

void TON_update(TON_Timer *t) {
    if (t->IN) {
        if (!t->Q) {
            if (t->start_time == 0) t->start_time = HAL_GetTick();
            t->ET = HAL_GetTick() - t->start_time;
            if (t->ET >= t->PT) t->Q = true;
        }
    } else {
        t->Q = false;
        t->ET = 0;
        t->start_time = 0;
    }
}

PLC_IO plc2;
TON_Timer TON_1 = {.PT = 2000};  // 2秒延时
TON_Timer TON_2 = {.PT = 3000};  // 3秒延时

void plc_sequential_start(void) {
    // 读取输入
    plc2.START = HAL_GPIO_ReadPin(START_GPIO_Port, START_Pin);

    // M1逻辑
    bool m1_start = plc2.START && !plc2.MOTOR;
    plc2.MOTOR = m1_start || plc2.MOTOR;
    relay_set(0, plc2.MOTOR);

    // M2逻辑（M1启动2秒后）
    TON_1.IN = plc2.MOTOR;
    TON_update(&TON_1);
    bool m2_start = TON_1.Q && !plc2.M2;
    plc2.M2 = m2_start || plc2.M2;
    relay_set(1, plc2.M2);

    // M3逻辑（M2启动3秒后）
    TON_2.IN = plc2.M2;
    TON_update(&TON_2);
    bool m3_start = TON_2.Q && !plc2.M3;
    plc2.M3 = m3_start || plc2.M3;
    relay_set(2, plc2.M3);
}
```

### SCADA集成：Node-RED仪表板

使用Node-RED创建Web HMI界面，通过Modbus TCP读写继电器：

```json
// Node-RED流程配置（导入到Node-RED）
[
    {
        "id": "modbus_client",
        "type": "modbus-client",
        "name": "继电器控制器",
        "clienttype": "tcp",
        "bufferCommands": true,
        "stateLogEnabled": false,
        "tcpHost": "192.168.1.100",
        "tcpPort": "502",
        "tcpType": "DEFAULT",
        "serialPort": "/dev/ttyUSB0",
        "serialType": "RTU-BUFFERD",
        "serialBaudrate": "115200",
        "serialDatabits": "8",
        "serialStopbits": "1",
        "serialParity": "none",
        "serialConnectionDelay": "100",
        "unit_id": "1",
        "commandDelay": "1",
        "clientTimeout": "1000",
        "reconnectTimeout": "2000"
    },
    {
        "id": "read_coils",
        "type": "modbus-read",
        "name": "读取继电器状态",
        "topic": "",
        "showStatusActivities": false,
        "logIOActivities": false,
        "showErrors": false,
        "unitid": "1",
        "dataType": "Coil",
        "adr": "0",
        "quantity": "16",
        "rate": "1000",
        "rateUnit": "ms",
        "delayOnStart": false,
        "startDelayTime": "",
        "server": "modbus_client",
        "useIOFile": false,
        "ioFile": "",
        "useIOForPayload": false,
        "x": 200,
        "y": 100,
        "wires": [["dashboard_display"]]
    },
    {
        "id": "dashboard_display",
        "type": "ui_template",
        "group": "relay_group",
        "name": "继电器状态显示",
        "order": 1,
        "width": "12",
        "height": "8",
        "format": "<div ng-bind-html=\"msg.payload\"></div>",
        "storeOutMessages": true,
        "fwdInMessages": true,
        "templateScope": "local",
        "x": 400,
        "y": 100,
        "wires": [[]]
    },
    {
        "id": "relay_switch",
        "type": "ui_switch",
        "group": "relay_group",
        "name": "继电器1控制",
        "label": "继电器1",
        "tooltip": "",
        "order": 2,
        "width": "3",
        "height": "1",
        "passthru": true,
        "decouple": "false",
        "topic": "",
        "style": "",
        "onvalue": "true",
        "onvalueType": "bool",
        "onicon": "",
        "oncolor": "",
        "offvalue": "false",
        "offvalueType": "bool",
        "officon": "",
        "offcolor": "",
        "x": 200,
        "y": 200,
        "wires": [["write_coil"]]
    },
    {
        "id": "write_coil",
        "type": "modbus-write",
        "name": "写入继电器",
        "showStatusActivities": false,
        "showErrors": false,
        "unitid": "1",
        "dataType": "Coil",
        "adr": "0",
        "quantity": "1",
        "server": "modbus_client",
        "x": 400,
        "y": 200,
        "wires": [[]]
    }
]
```

**Node-RED仪表板功能**：
- 实时显示16路继电器状态（绿色=吸合，灰色=断开）
- 开关按钮控制单路继电器
- 顺序控制按钮（启动/停止生产线）
- 历史数据图表（继电器动作次数、运行时间）
- 报警通知（互锁冲突、通信故障）

**部署步骤**：
1. 安装Node-RED：`npm install -g node-red`
2. 安装Modbus节点：`npm install node-red-contrib-modbus`
3. 安装仪表板：`npm install node-red-dashboard`
4. 导入上述流程JSON
5. 访问 `http://localhost:1880/ui` 查看仪表板
```

## 延伸阅读

- [继电器控制基础](../beginner/04-relay-control.html) - 继电器工作原理
- [WiFi智能插座](07-smart-socket-project.html) - 单路WiFi控制
- [环境监控系统](09-environment-control.html) - 传感器联动

## 深入原理

### IEC 61131-3编程模型

IEC 61131-3是PLC编程语言的国际标准，定义了5种编程语言：

#### 1. 梯形图（Ladder Diagram, LD）

最直观的图形化语言，模拟继电器控制电路：

```
基本元素：
  ─┤ ├─   常开触点（Normally Open）
  ─┤/├─   常闭触点（Normally Closed）
  ─( )─   线圈（Coil）
  ─(S)─   置位线圈（Set）
  ─(R)─   复位线圈（Reset）
  ─[TON]─ 定时器（Timer On Delay）
  ─[CTU]─ 计数器（Counter Up）

示例：电机星三角启动
  ┌─┤ START ├─┤ /STOP ├─┤ /KM1 ├─( KM1 )─┐  主接触器
  │                                         │
  └─┤ KM1 ├──────────────────────────────┘  自保持
  
  ┌─┤ KM1 ├─┤ TON_1 ├─┤ /KM2 ├─( KM2 )─┐  星形接触器
  │                                       │
  └─┤ KM2 ├─┤ /TON_1.Q ├────────────────┘
  
  ┌─┤ KM1 ├─┤ TON_1.Q ├─┤ /KM3 ├─( KM3 )─┐  三角形接触器
  │                                         │
  └─┤ KM3 ├──────────────────────────────┘
```

**C语言等效实现**：

```c
typedef struct {
    bool START, STOP, KM1, KM2, KM3;
    TON_Timer TON_1;
} StarDelta_PLC;

void star_delta_logic(StarDelta_PLC *plc) {
    // 主接触器KM1
    bool km1_set = plc->START && !plc->STOP && !plc->KM1;
    plc->KM1 = km1_set || plc->KM1;
    
    // 星形接触器KM2（KM1启动后立即吸合）
    plc->TON_1.IN = plc->KM1;
    TON_update(&plc->TON_1);
    bool km2_set = plc->KM1 && !plc->TON_1.Q && !plc->KM2;
    plc->KM2 = km2_set || (plc->KM2 && !plc->TON_1.Q);
    
    // 三角形接触器KM3（延时后切换）
    bool km3_set = plc->KM1 && plc->TON_1.Q && !plc->KM3;
    plc->KM3 = km3_set || plc->KM3;
    
    // 输出
    relay_set(0, plc->KM1);
    relay_set(1, plc->KM2);
    relay_set(2, plc->KM3);
}
```

#### 2. 功能块图（Function Block Diagram, FBD）

类似数字电路的逻辑门连接：

```
     START ──┬──┐
             │  │
     STOP ───┼──┤ AND ├─┬─┐
             │  │      │ │
     ALARM ──┴──┘      │ │
                       │ │
     MOTOR ────────────┘ │
                         │
                      ┌──┴──┐
                      │  OR │──── MOTOR
                      └─────┘
```

#### 3. 结构化文本（Structured Text, ST）

类似Pascal的高级语言：

```pascal
(* 星三角启动程序 *)
PROGRAM StarDelta
VAR
    START, STOP : BOOL;
    KM1, KM2, KM3 : BOOL;
    TON_1 : TON;
END_VAR

(* 主接触器 *)
IF START AND NOT STOP THEN
    KM1 := TRUE;
END_IF;

IF STOP THEN
    KM1 := FALSE;
    KM2 := FALSE;
    KM3 := FALSE;
END_IF;

(* 星形接触器 *)
TON_1(IN := KM1, PT := T#5S);
IF KM1 AND NOT TON_1.Q THEN
    KM2 := TRUE;
    KM3 := FALSE;
END_IF;

(* 三角形接触器 *)
IF KM1 AND TON_1.Q THEN
    KM2 := FALSE;
    KM3 := TRUE;
END_IF;

END_PROGRAM
```

#### 4. 指令表（Instruction List, IL）

类似汇编语言：

```
LD    START
AND   STOP
ANDN  KM1
ST    KM1

LD    KM1
TON   TON_1, T#5S
ANDN  KM2
ST    KM2
```

#### 5. 顺序功能图（Sequential Function Chart, SFC）

描述顺序控制流程：

```
    ┌───────┐
    │ INIT  │ 初始步
    └───┬───┘
        │ START=1
    ┌───▼───┐
    │ STEP1 │ 启动主接触器
    └───┬───┘
        │ KM1=1
    ┌───▼───┐
    │ STEP2 │ 星形启动
    └───┬───┘
        │ T=5s
    ┌───▼───┐
    │ STEP3 │ 切换三角形
    └───┬───┘
        │ STOP=1
    ┌───▼───┐
    │ STOP  │ 停止
    └───────┘
```

### 安全继电器原理

安全继电器（Safety Relay）用于安全关键应用，符合IEC 61508功能安全标准。

#### 双通道冗余架构

```
输入1 ──┬─→ 通道A ──┬─→ 输出1
        │           │
        │  监控     │
        │  逻辑     │
        │           │
输入2 ──┴─→ 通道B ──┴─→ 输出2

监控逻辑：
  - 两个通道独立处理
  - 交叉监控对方状态
  - 任一通道故障则安全断开
  - 定期自检（脉冲测试）
```

**实现示例**：

```c
typedef struct {
    bool input1, input2;
    bool channel_a, channel_b;
    bool output1, output2;
    uint32_t last_test_time;
    bool test_passed;
} SafetyRelay;

void safety_relay_update(SafetyRelay *sr) {
    uint32_t now = HAL_GetTick();
    
    // 每100ms自检一次
    if (now - sr->last_test_time > 100) {
        sr->last_test_time = now;
        
        // 脉冲测试：短暂断开输出，检查反馈
        relay_set(0, false);
        relay_set(1, false);
        HAL_Delay(1);
        
        // 检查反馈回路
        bool fb1 = HAL_GPIO_ReadPin(FEEDBACK1_GPIO_Port, FEEDBACK1_Pin);
        bool fb2 = HAL_GPIO_ReadPin(FEEDBACK2_GPIO_Port, FEEDBACK2_Pin);
        sr->test_passed = (!fb1 && !fb2);  // 应该都断开
        
        if (!sr->test_passed) {
            // 自检失败，进入安全状态
            sr->channel_a = false;
            sr->channel_b = false;
            return;
        }
    }
    
    // 双通道逻辑
    sr->channel_a = sr->input1 && sr->test_passed;
    sr->channel_b = sr->input2 && sr->test_passed;
    
    // 交叉监控：两个通道必须一致
    if (sr->channel_a != sr->channel_b) {
        // 通道不一致，安全断开
        sr->output1 = false;
        sr->output2 = false;
    } else {
        sr->output1 = sr->channel_a;
        sr->output2 = sr->channel_b;
    }
    
    relay_set(0, sr->output1);
    relay_set(1, sr->output2);
}
```

#### 安全等级（SIL）

IEC 61508定义了4个安全完整性等级：

| SIL等级 | 失效概率（每小时） | 风险降低因子 | 应用场景 |
|---------|-------------------|-------------|---------|
| SIL 1 | 10⁻⁵ ~ 10⁻⁶ | 10 ~ 100 | 轻伤风险 |
| SIL 2 | 10⁻⁶ ~ 10⁻⁷ | 100 ~ 1000 | 重伤风险 |
| SIL 3 | 10⁻⁷ ~ 10⁻⁸ | 1000 ~ 10000 | 死亡风险 |
| SIL 4 | 10⁻⁸ ~ 10⁻⁹ | 10000 ~ 100000 | 多人死亡 |

**达到SIL 2的措施**：
- 双通道冗余
- 交叉监控
- 定期自检
- 故障安全设计（Fail-Safe）
- 软件符合MISRA C规范

### 看门狗定时器（Watchdog Timer）

防止程序跑飞或死循环，确保系统可靠运行。

#### 独立看门狗（IWDG）

STM32内置独立看门狗，由独立RC振荡器驱动：

```c
// 初始化IWDG，超时时间1秒
void iwdg_init(void) {
    IWDG->KR = 0x5555;  // 允许写入PR和RLR
    IWDG->PR = 6;       // 预分频器：40kHz / 256 = 156Hz
    IWDG->RLR = 156;    // 重载值：156 / 156Hz = 1秒
    IWDG->KR = 0xCCCC;  // 启动看门狗
}

// 喂狗（必须在1秒内调用）
void iwdg_feed(void) {
    IWDG->KR = 0xAAAA;
}

// 主循环
int main(void) {
    HAL_Init();
    iwdg_init();
    
    while (1) {
        // 正常任务
        relay_control_task();
        modbus_task();
        trigger_check_all();
        
        // 喂狗
        iwdg_feed();
        
        HAL_Delay(100);
    }
}
```

#### 窗口看门狗（WWDG）

窗口看门狗要求在特定时间窗口内喂狗，防止程序运行过快或过慢：

```c
// 初始化WWDG，窗口时间50~100ms
void wwdg_init(void) {
    __HAL_RCC_WWDG_CLK_ENABLE();
    
    WWDG_HandleTypeDef hwwdg;
    hwwdg.Instance = WWDG;
    hwwdg.Init.Prescaler = WWDG_PRESCALER_8;  // 72MHz / 4096 / 8 = 2.2kHz
    hwwdg.Init.Window = 80;    // 窗口上限：80 / 2.2kHz = 36ms
    hwwdg.Init.Counter = 127;  // 计数器初值
    hwwdg.Init.EWIMode = WWDG_EWI_ENABLE;  // 使能早期唤醒中断
    
    HAL_WWDG_Init(&hwwdg);
}

// 早期唤醒中断（在超时前触发）
void WWDG_IRQHandler(void) {
    HAL_WWDG_IRQHandler(&hwwdg);
}

void HAL_WWDG_EarlyWakeupCallback(WWDG_HandleTypeDef *hwwdg) {
    // 在窗口内喂狗
    HAL_WWDG_Refresh(hwwdg);
}
```

#### 软件看门狗

多任务系统中，监控各任务是否正常运行：

```c
#define MAX_TASKS  4

typedef struct {
    const char *name;
    uint32_t timeout_ms;
    uint32_t last_feed_time;
    bool alive;
} TaskWatchdog;

TaskWatchdog task_wdg[MAX_TASKS] = {
    {"ModbusTask",  1000, 0, true},
    {"RelayTask",   500,  0, true},
    {"TriggerTask", 2000, 0, true},
    {"LogTask",     5000, 0, true},
};

// 任务喂狗
void task_feed_watchdog(uint8_t task_id) {
    if (task_id < MAX_TASKS) {
        task_wdg[task_id].last_feed_time = HAL_GetTick();
        task_wdg[task_id].alive = true;
    }
}

// 看门狗监控任务（高优先级）
void watchdog_monitor_task(void) {
    uint32_t now = HAL_GetTick();
    bool all_alive = true;
    
    for (int i = 0; i < MAX_TASKS; i++) {
        if (now - task_wdg[i].last_feed_time > task_wdg[i].timeout_ms) {
            task_wdg[i].alive = false;
            all_alive = false;
            printf("Task %s timeout!\n", task_wdg[i].name);
        }
    }
    
    if (!all_alive) {
        // 任务超时，进入安全状态
        relay_set_all(0);  // 断开所有继电器
        system_status = STATUS_ERROR;
        // 可选：触发系统复位
        // NVIC_SystemReset();
    } else {
        // 所有任务正常，喂硬件看门狗
        iwdg_feed();
    }
}
```

## 参考资料

1. PCF8574 Datasheet - NXP Semiconductors
2. Modbus Application Protocol Specification V1.1b3
3. MAX485 Datasheet - Maxim Integrated
4. 《可编程控制器原理及应用》- 廖常初
5. 《工业控制网络》- 阳宪惠
6. IEC 61131-3 - PLC编程语言标准
7. W5500 Datasheet - WIZnet
8. IEC 61508 - 功能安全标准
9. MISRA C:2012 - 嵌入式C编程规范
10. Modbus TCP/IP Specification - Modbus Organization

## 完整项目实战：工业自动化控制柜

### 项目需求

设计一个16路继电器自动化控制柜，用于小型生产线控制：

**控制对象**：
- 4台传送带电机（M1~M4）
- 2台加热器（H1~H2）
- 2台冷却风扇（F1~F2）
- 4个电磁阀（V1~V4）
- 2个指示灯（L1~L2）
- 2路备用（R1~R2）

**功能要求**：
1. 本地HMI触摸屏控制
2. 远程Modbus TCP监控
3. 顺序启动/停止（防止电流冲击）
4. 互锁保护（加热器与风扇不能同时运行）
5. 温度/压力传感器联动
6. 故障报警和日志记录
7. 手动/自动模式切换

### 硬件设计

#### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    控制柜面板                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 急停按钮 │  │ 模式选择 │  │ 指示灯   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │         7寸HMI触摸屏（UART/RS485）         │         │
│  └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    STM32F407主控板                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ UART1   │  │ UART2   │  │ I2C1    │  │ SPI1    │   │
│  │ HMI     │  │ Modbus  │  │ PCF8574 │  │ W5500   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ ADC1    │  │ TIM2    │  │ IWDG    │                │
│  │ 传感器  │  │ 编码器  │  │ 看门狗  │                │
│  └─────────┘  └─────────┘  └─────────┘                │
└─────────────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ PCF8574 #1   │ │ PCF8574 #2   │ │ MAX485       │
│ 8路继电器    │ │ 8路继电器    │ │ RS485总线    │
└──────────────┘ └──────────────┘ └──────────────┘
         │              │              │
         ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ M1 M2 M3 M4  │ │ H1 H2 F1 F2  │ │ 远程监控PC   │
│ 传送带电机   │ │ 加热器/风扇  │ │ SCADA系统    │
└──────────────┘ └──────────────┘ └──────────────┘
```

#### 完整BOM清单

| 类别 | 器件 | 型号/规格 | 数量 | 单价 | 采购链接 |
|------|------|----------|------|------|---------|
| 主控 | MCU开发板 | STM32F407VET6核心板 | 1 | ¥35 | 淘宝/立创商城 |
| 扩展 | I2C扩展 | PCF8574模块 | 2 | ¥3 | 淘宝 |
| 继电器 | 继电器模块 | 8路5V继电器板（光耦隔离） | 2 | ¥18 | 淘宝 |
| 通信 | RS485收发器 | MAX485模块 | 1 | ¥2 | 淘宝 |
| 网络 | 以太网模块 | W5500模块 | 1 | ¥25 | 淘宝 |
| HMI | 触摸屏 | 7寸串口屏（UART） | 1 | ¥120 | 淘宝（迪文/大彩） |
| 传感器 | 温度传感器 | DS18B20防水探头 | 2 | ¥5 | 淘宝 |
| 传感器 | 压力传感器 | 0-1.6MPa压力变送器（4-20mA） | 1 | ¥45 | 淘宝 |
| 电源 | 开关电源 | 12V/5A | 1 | ¥15 | 淘宝 |
| 电源 | DC-DC模块 | 12V转5V/3A | 1 | ¥3 | 淘宝 |
| 电源 | DC-DC模块 | 12V转3.3V/1A | 1 | ¥2 | 淘宝 |
| 机箱 | 配电箱 | 400×300×200mm铁箱 | 1 | ¥60 | 淘宝 |
| 接线 | 端子排 | UK-2.5N导轨端子 | 20 | ¥0.5 | 淘宝 |
| 接线 | 导轨 | 35mm DIN导轨 1米 | 1 | ¥8 | 淘宝 |
| 线材 | 电源线 | RVV 3×1.5mm² | 5米 | ¥2/米 | 五金店 |
| 线材 | 信号线 | RVVP 2×0.5mm²屏蔽线 | 10米 | ¥1.5/米 | 淘宝 |
| 保护 | 空气开关 | DZ47-63 C10 2P | 1 | ¥12 | 淘宝 |
| 保护 | 熔断器 | RT18-32 10A | 4 | ¥3 | 淘宝 |
| 按钮 | 急停按钮 | LA38-11ZS红色蘑菇头 | 1 | ¥8 | 淘宝 |
| 按钮 | 选择开关 | LA38-11XD 2档旋钮 | 1 | ¥6 | 淘宝 |
| 指示灯 | 信号灯 | AD16-22DS 22mm LED | 3 | ¥3 | 淘宝 |

**总成本**：约 ¥450

#### 接线图

```
电源部分：
  AC 220V ──→ 空气开关 ──→ 开关电源12V ──┬──→ 继电器模块（12V线圈）
                                        ├──→ DC-DC 5V ──→ STM32/PCF8574
                                        └──→ DC-DC 3.3V ──→ W5500

控制部分：
  STM32_I2C1_SDA ──→ PCF8574 #1 SDA ──→ PCF8574 #2 SDA
  STM32_I2C1_SCL ──→ PCF8574 #1 SCL ──→ PCF8574 #2 SCL
  
  PCF8574 #1 P0~P7 ──→ 继电器1~8控制端
  PCF8574 #2 P0~P7 ──→ 继电器9~16控制端
  
  STM32_UART1_TX ──→ HMI_RX
  STM32_UART1_RX ──→ HMI_TX
  
  STM32_UART2_TX ──→ MAX485_DI
  STM32_UART2_RX ──→ MAX485_RO
  STM32_PA8 ──→ MAX485_DE/RE
  
  STM32_SPI1 ──→ W5500 (MOSI/MISO/SCK/CS)
  
  STM32_PA0 ──→ 温度传感器1（DS18B20）
  STM32_PA1 ──→ 温度传感器2（DS18B20）
  STM32_ADC1_IN2 ──→ 压力变送器（4-20mA转0-3.3V）

负载部分：
  继电器1~4 常开触点 ──→ 传送带电机接触器线圈
  继电器5~6 常开触点 ──→ 加热器接触器线圈
  继电器7~8 常开触点 ──→ 风扇接触器线圈
  继电器9~12 常开触点 ──→ 电磁阀线圈
  继电器13~14 常开触点 ──→ 指示灯
```

### 软件实现

#### 主程序架构

```c
// main.c - 主程序
#include "stm32f4xx_hal.h"
#include "relay_control.h"
#include "modbus_rtu.h"
#include "hmi_protocol.h"
#include "sensor_read.h"
#include "automation_logic.h"

// 系统状态
typedef enum {
    MODE_MANUAL,    // 手动模式
    MODE_AUTO,      // 自动模式
    MODE_EMERGENCY  // 急停模式
} SystemMode;

SystemMode system_mode = MODE_MANUAL;
bool emergency_stop = false;

int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 初始化外设
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_UART1_Init();  // HMI
    MX_UART2_Init();  // Modbus
    MX_SPI1_Init();   // W5500
    MX_ADC1_Init();
    MX_TIM2_Init();
    
    // 初始化功能模块
    relay_init();
    modbus_init();
    hmi_init();
    sensor_init();
    w5500_init();
    iwdg_init();
    
    // 启动定时器中断（1ms）
    HAL_TIM_Base_Start_IT(&htim2);
    
    while (1) {
        // 读取急停按钮
        emergency_stop = !HAL_GPIO_ReadPin(ESTOP_GPIO_Port, ESTOP_Pin);
        if (emergency_stop) {
            system_mode = MODE_EMERGENCY;
            relay_set_all(0);  // 断开所有继电器
            continue;
        }
        
        // 读取模式选择开关
        bool mode_sw = HAL_GPIO_ReadPin(MODE_SW_GPIO_Port, MODE_SW_Pin);
        system_mode = mode_sw ? MODE_AUTO : MODE_MANUAL;
        
        // 读取传感器
        float temp1 = ds18b20_read(0);
        float temp2 = ds18b20_read(1);
        float pressure = pressure_sensor_read();
        
        // 执行控制逻辑
        if (system_mode == MODE_AUTO) {
            automation_logic_update(temp1, temp2, pressure);
        }
        
        // 处理HMI通信
        hmi_process();
        
        // 处理Modbus通信
        modbus_process_task();
        
        // 处理以太网通信
        w5500_process();
        
        // 喂狗
        iwdg_feed();
        
        HAL_Delay(10);
    }
}

// 1ms定时器中断
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        // 更新定时器
        for (int i = 0; i < MAX_TIMERS; i++) {
            TON_update(&timers[i]);
        }
        
        // 更新计数器
        for (int i = 0; i < MAX_COUNTERS; i++) {
            CTU_update(&counters[i]);
        }
    }
}
```

#### 自动化控制逻辑

```c
// automation_logic.c - 自动化控制逻辑
#include "automation_logic.h"

typedef enum {
    STATE_IDLE,
    STATE_STARTING,
    STATE_RUNNING,
    STATE_STOPPING,
    STATE_ERROR
} AutoState;

AutoState auto_state = STATE_IDLE;
TON_Timer startup_timers[4];
bool start_button = false;
bool stop_button = false;

void automation_logic_update(float temp1, float temp2, float pressure) {
    // 读取HMI按钮状态
    start_button = hmi_get_button(BTN_START);
    stop_button = hmi_get_button(BTN_STOP);
    
    switch (auto_state) {
        case STATE_IDLE:
            if (start_button && !stop_button) {
                auto_state = STATE_STARTING;
                // 重置定时器
                for (int i = 0; i < 4; i++) {
                    startup_timers[i].IN = false;
                    startup_timers[i].Q = false;
                    startup_timers[i].ET = 0;
                }
            }
            break;
            
        case STATE_STARTING:
            // 顺序启动：M1 → 2s → M2 → 2s → M3 → 2s → M4
            startup_timers[0].IN = true;
            startup_timers[0].PT = 0;  // 立即启动M1
            TON_update(&startup_timers[0]);
            if (startup_timers[0].Q) {
                relay_set_safe(0, true);  // M1
                
                startup_timers[1].IN = true;
                startup_timers[1].PT = 2000;
                TON_update(&startup_timers[1]);
                if (startup_timers[1].Q) {
                    relay_set_safe(1, true);  // M2
                    
                    startup_timers[2].IN = true;
                    startup_timers[2].PT = 2000;
                    TON_update(&startup_timers[2]);
                    if (startup_timers[2].Q) {
                        relay_set_safe(2, true);  // M3
                        
                        startup_timers[3].IN = true;
                        startup_timers[3].PT = 2000;
                        TON_update(&startup_timers[3]);
                        if (startup_timers[3].Q) {
                            relay_set_safe(3, true);  // M4
                            auto_state = STATE_RUNNING;
                        }
                    }
                }
            }
            
            if (stop_button) {
                auto_state = STATE_STOPPING;
            }
            break;
            
        case STATE_RUNNING:
            // 温度控制：温度过高启动风扇，温度过低启动加热器
            if (temp1 > 80.0f) {
                relay_set_safe(4, false);  // 关闭加热器H1
                relay_set_safe(6, true);   // 启动风扇F1
            } else if (temp1 < 60.0f) {
                relay_set_safe(6, false);  // 关闭风扇F1
                relay_set_safe(4, true);   // 启动加热器H1
            }
            
            if (temp2 > 80.0f) {
                relay_set_safe(5, false);  // 关闭加热器H2
                relay_set_safe(7, true);   // 启动风扇F2
            } else if (temp2 < 60.0f) {
                relay_set_safe(7, false);  // 关闭风扇F2
                relay_set_safe(5, true);   // 启动加热器H2
            }
            
            // 压力控制：压力过高打开泄压阀
            if (pressure > 1.2f) {
                relay_set_safe(8, true);   // 打开泄压阀V1
            } else if (pressure < 0.8f) {
                relay_set_safe(8, false);  // 关闭泄压阀V1
            }
            
            // 故障检测
            if (temp1 > 100.0f || temp2 > 100.0f || pressure > 1.5f) {
                auto_state = STATE_ERROR;
                relay_set(12, true);  // 点亮故障指示灯
            }
            
            if (stop_button) {
                auto_state = STATE_STOPPING;
            }
            break;
            
        case STATE_STOPPING:
            // 逆序停止：M4 → 1s → M3 → 1s → M2 → 1s → M1
            relay_set_safe(3, false);  // M4
            HAL_Delay(1000);
            relay_set_safe(2, false);  // M3
            HAL_Delay(1000);
            relay_set_safe(1, false);  // M2
            HAL_Delay(1000);
            relay_set_safe(0, false);  // M1
            
            // 关闭所有加热器和风扇
            relay_set_safe(4, false);
            relay_set_safe(5, false);
            relay_set_safe(6, false);
            relay_set_safe(7, false);
            
            auto_state = STATE_IDLE;
            break;
            
        case STATE_ERROR:
            // 故障状态：断开所有继电器
            relay_set_all(0);
            
            // 等待复位按钮
            if (hmi_get_button(BTN_RESET)) {
                relay_set(12, false);  // 熄灭故障指示灯
                auto_state = STATE_IDLE;
            }
            break;
    }
    
    // 更新HMI显示
    hmi_update_status(auto_state, temp1, temp2, pressure);
}
```

#### HMI通信协议

```c
// hmi_protocol.c - 串口屏通信协议
#include "hmi_protocol.h"

// 迪文串口屏协议：帧头(3字节) + 数据 + 帧尾(3字节)
// 帧头：5A A5 长度
// 帧尾：FF FF FF

#define HMI_FRAME_HEAD1  0x5A
#define HMI_FRAME_HEAD2  0xA5

typedef struct {
    uint8_t buttons;  // 按钮状态（位域）
    float temp1, temp2, pressure;
    uint8_t relay_state[2];
} HMI_Data;

HMI_Data hmi_data;

void hmi_send_frame(uint8_t cmd, uint8_t *data, uint16_t len) {
    uint8_t frame[256];
    frame[0] = HMI_FRAME_HEAD1;
    frame[1] = HMI_FRAME_HEAD2;
    frame[2] = len + 3;  // 长度包含命令字
    frame[3] = cmd;
    memcpy(&frame[4], data, len);
    
    HAL_UART_Transmit(&huart1, frame, len + 4, 100);
}

void hmi_update_status(AutoState state, float temp1, float temp2, float pressure) {
    // 更新文本显示控件（地址0x1000）
    char text[64];
    snprintf(text, sizeof(text), "温度1: %.1f°C\n温度2: %.1f°C\n压力: %.2fMPa",
             temp1, temp2, pressure);
    
    uint8_t data[128];
    data[0] = 0x10;  // 写变量指令
    data[1] = 0x00;  // 地址高字节
    data[2] = 0x10;  // 地址低字节
    memcpy(&data[3], text, strlen(text));
    
    hmi_send_frame(0x82, data, strlen(text) + 3);
    
    // 更新继电器状态图标（地址0x2000~0x200F）
    for (int i = 0; i < 16; i++) {
        data[0] = 0x10;
        data[1] = 0x20 + (i >> 8);
        data[2] = i & 0xFF;
        data[3] = relay_get(i) ? 0x01 : 0x00;
        hmi_send_frame(0x82, data, 4);
    }
}

bool hmi_get_button(uint8_t btn_id) {
    return (hmi_data.buttons >> btn_id) & 0x01;
}

void hmi_process(void) {
    uint8_t rx_buf[256];
    uint16_t rx_len = 0;
    
    // 接收HMI数据（非阻塞）
    if (HAL_UART_Receive(&huart1, rx_buf, 256, 10) == HAL_OK) {
        if (rx_buf[0] == HMI_FRAME_HEAD1 && rx_buf[1] == HMI_FRAME_HEAD2) {
            uint8_t len = rx_buf[2];
            uint8_t cmd = rx_buf[3];
            
            if (cmd == 0x83) {  // 按钮事件
                uint16_t addr = (rx_buf[4] << 8) | rx_buf[5];
                uint8_t value = rx_buf[6];
                
                // 解析按钮
                if (addr >= 0x3000 && addr < 0x3010) {
                    uint8_t btn_id = addr - 0x3000;
                    if (value) hmi_data.buttons |= (1 << btn_id);
                    else       hmi_data.buttons &= ~(1 << btn_id);
                }
            }
        }
    }
}
```

### 调试与测试

#### 单元测试

```c
// test_relay.c - 继电器模块测试
void test_relay_basic(void) {
    printf("测试1：单路继电器控制\n");
    for (int i = 0; i < 16; i++) {
        relay_set(i, true);
        HAL_Delay(200);
        assert(relay_get(i) == true);
        relay_set(i, false);
        HAL_Delay(200);
        assert(relay_get(i) == false);
    }
    printf("通过\n");
}

void test_relay_interlock(void) {
    printf("测试2：互锁保护\n");
    uint8_t group1[] = {0, 1};  // M1正转/反转
    interlock_register(group1, 2);
    
    relay_set_safe(0, true);
    assert(relay_get(0) == true);
    
    relay_set_safe(1, true);  // 应该先断开CH0
    HAL_Delay(150);
    assert(relay_get(0) == false);
    assert(relay_get(1) == true);
    printf("通过\n");
}

void test_sequence_control(void) {
    printf("测试3：顺序控制\n");
    run_sequence(startup_seq, 4);
    assert(relay_get(0) == true);
    assert(relay_get(1) == true);
    assert(relay_get(2) == true);
    assert(relay_get(3) == true);
    printf("通过\n");
}
```

#### 集成测试

```c
// test_integration.c - 集成测试
void test_modbus_communication(void) {
    printf("测试4：Modbus通信\n");
    
    // 模拟主站请求：读取线圈0~15
    uint8_t req[] = {0x01, 0x01, 0x00, 0x00, 0x00, 0x10, 0x3D, 0xC6};
    uint8_t resp[256];
    uint16_t resp_len;
    
    modbus_process(req, sizeof(req), resp, &resp_len);
    
    assert(resp[0] == 0x01);  // 从站地址
    assert(resp[1] == 0x01);  // 功能码
    assert(resp[2] == 0x02);  // 字节数
    printf("通过\n");
}

void test_automation_logic(void) {
    printf("测试5：自动化逻辑\n");
    
    // 模拟温度过高
    automation_logic_update(90.0f, 70.0f, 1.0f);
    assert(relay_get(4) == false);  // 加热器关闭
    assert(relay_get(6) == true);   // 风扇启动
    
    // 模拟温度过低
    automation_logic_update(50.0f, 70.0f, 1.0f);
    assert(relay_get(4) == true);   // 加热器启动
    assert(relay_get(6) == false);  // 风扇关闭
    
    printf("通过\n");
}
```

### 现场安装与调试

#### 安装步骤

1. **机械安装**：
   - 将控制柜固定在墙面或支架上
   - 安装DIN导轨和端子排
   - 固定主控板、继电器模块、电源模块

2. **电气接线**：
   - 按接线图连接电源线（注意相线/零线/地线）
   - 连接控制信号线（使用屏蔽线，远离动力线）
   - 连接负载线（通过继电器常开触点）
   - 安装终端电阻（RS485总线两端）

3. **功能测试**：
   - 上电前检查：万用表测量电源电压、绝缘电阻
   - 空载测试：不接负载，测试继电器动作
   - 负载测试：接入实际负载，测试控制逻辑
   - 通信测试：Modbus Poll读写测试、HMI触摸测试

4. **参数调整**：
   - 调整顺序控制延时时间
   - 调整温度/压力阈值
   - 调整PID参数（如有）
   - 设置报警限值

#### 常见问题排查

见下一节"常见问题与调试"。

## 常见问题与调试

### 1. Modbus CRC校验错误

**现象**：
- 主站报告CRC错误，无法读取从站数据
- 从站偶尔收到错误帧

**原因分析**：
1. 波特率不匹配（主站115200，从站9600）
2. 数据位/停止位/校验位配置错误
3. RS485总线干扰（未接地、未屏蔽）
4. CRC计算算法错误（字节序、多项式）

**解决方法**：

```c
// 1. 确认UART配置一致
void uart_config_check(void) {
    // 主站和从站必须完全一致
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    HAL_UART_Init(&huart2);
}

// 2. 验证CRC算法
void test_crc(void) {
    uint8_t test_data[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x08};
    uint16_t crc = modbus_crc16(test_data, 6);
    // 正确结果：0x0C44（低字节0x44，高字节0x0C）
    printf("CRC: 0x%04X (应为0x0C44)\n", crc);
}

// 3. 添加CRC错误计数和日志
uint32_t crc_error_count = 0;

void modbus_process_with_log(uint8_t *req, uint16_t req_len,
                              uint8_t *resp, uint16_t *resp_len) {
    if (req_len < 4) return;
    
    uint16_t crc_recv = req[req_len-2] | (req[req_len-1] << 8);
    uint16_t crc_calc = modbus_crc16(req, req_len - 2);
    
    if (crc_recv != crc_calc) {
        crc_error_count++;
        printf("CRC错误 #%lu: 接收=0x%04X, 计算=0x%04X\n",
               crc_error_count, crc_recv, crc_calc);
        // 打印原始数据帮助调试
        printf("原始帧: ");
        for (int i = 0; i < req_len; i++) {
            printf("%02X ", req[i]);
        }
        printf("\n");
        return;
    }
    
    // 正常处理...
}
```

**硬件检查**：
- 使用示波器/逻辑分析仪查看波形是否完整
- 检查RS485 A/B线是否接反
- 确认终端电阻已正确安装（120Ω，仅总线两端）
- 检查地线连接（所有设备共地）

### 2. RS485总线冲突

**现象**：
- 多个从站同时响应，数据混乱
- 从站地址冲突
- 总线"卡死"，无法通信

**原因分析**：
1. 多个从站使用相同地址
2. 从站未正确释放总线（DE/RE控制错误）
3. 主站轮询间隔过短，从站来不及响应
4. 总线负载过重（超过32个节点）

**解决方法**：

```c
// 1. 从站地址管理（通过拨码开关设置）
uint8_t get_modbus_address(void) {
    uint8_t addr = 0;
    // 读取4位拨码开关（支持1~15地址）
    if (HAL_GPIO_ReadPin(ADDR_BIT0_GPIO_Port, ADDR_BIT0_Pin)) addr |= 0x01;
    if (HAL_GPIO_ReadPin(ADDR_BIT1_GPIO_Port, ADDR_BIT1_Pin)) addr |= 0x02;
    if (HAL_GPIO_ReadPin(ADDR_BIT2_GPIO_Port, ADDR_BIT2_Pin)) addr |= 0x04;
    if (HAL_GPIO_ReadPin(ADDR_BIT3_GPIO_Port, ADDR_BIT3_Pin)) addr |= 0x08;
    
    if (addr == 0) addr = 1;  // 默认地址1
    return addr;
}

// 2. 严格的DE/RE控制时序
void modbus_send_response(uint8_t *resp, uint16_t resp_len) {
    // 使能发送
    HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_SET);
    HAL_Delay(1);  // 等待MAX485切换（典型值120ns，留足余量）
    
    // 发送数据
    HAL_UART_Transmit(&huart2, resp, resp_len, 100);
    
    // 等待发送完成（重要！）
    while (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_TC) == RESET);
    HAL_Delay(1);  // 等待最后一个字节完全发出
    
    // 释放总线
    HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_RESET);
}

// 3. 主站轮询策略（避免冲突）
void master_polling_task(void) {
    for (uint8_t addr = 1; addr <= 16; addr++) {
        // 发送请求
        uint8_t req[] = {addr, 0x01, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00};
        uint16_t crc = modbus_crc16(req, 6);
        req[6] = crc & 0xFF;
        req[7] = crc >> 8;
        
        HAL_UART_Transmit(&huart2, req, 8, 100);
        
        // 等待响应（超时100ms）
        uint8_t resp[256];
        HAL_StatusTypeDef status = HAL_UART_Receive(&huart2, resp, 256, 100);
        
        if (status == HAL_OK) {
            // 处理响应
            process_response(resp);
        } else {
            printf("从站%d无响应\n", addr);
        }
        
        // 轮询间隔（重要！给从站足够时间）
        HAL_Delay(50);
    }
}
```

**总线负载计算**：
- 标准RS485：最多32个节点（每个节点1个单位负载）
- 使用中继器/集线器可扩展到256个节点
- 计算公式：总负载 = 发送器负载 + 接收器负载 × 节点数
- MAX485：发送器1 UL，接收器1/8 UL

### 3. 继电器触点粘连/烧蚀

**现象**：
- 继电器无法断开（触点粘连）
- 触点发黑、凹坑（电弧烧蚀）
- 继电器寿命缩短

**原因分析**：
1. 负载电流超过继电器额定值
2. 感性负载（电机、线圈）产生反向电动势
3. 频繁开关（超过机械寿命）
4. 环境潮湿导致触点氧化

**解决方法**：

```c
// 1. 软启动（减少冲击电流）
void relay_soft_start(uint8_t ch) {
    // PWM软启动（仅适用于阻性负载）
    for (int duty = 0; duty <= 100; duty += 10) {
        // 使用PWM控制继电器线圈电压
        __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
        HAL_Delay(10);
    }
    relay_set(ch, true);
}

// 2. 限制开关频率
typedef struct {
    uint32_t last_switch_time;
    uint32_t min_interval_ms;  // 最小开关间隔
    uint32_t switch_count;     // 开关次数统计
} RelayLifetime;

RelayLifetime relay_lifetime[16];

bool relay_set_with_limit(uint8_t ch, bool on) {
    if (ch >= 16) return false;
    
    uint32_t now = HAL_GetTick();
    RelayLifetime *rl = &relay_lifetime[ch];
    
    // 检查开关间隔
    if (now - rl->last_switch_time < rl->min_interval_ms) {
        printf("继电器%d开关过于频繁，已限制\n", ch);
        return false;
    }
    
    // 检查寿命（假设额定寿命10万次）
    if (rl->switch_count > 100000) {
        printf("继电器%d已达寿命，建议更换\n", ch);
        // 可选：禁用该继电器
        return false;
    }
    
    relay_set(ch, on);
    rl->last_switch_time = now;
    rl->switch_count++;
    
    return true;
}

// 3. 感性负载保护（硬件方案）
// 在继电器触点并联RC吸收电路或压敏电阻
/*
  继电器触点
    ┌─────┐
    │  NO │───┬─→ 负载
    └─────┘   │
              ├─ 100nF ─┐
              │          │
              ├─ 100Ω ──┤
              │          │
              └──────────┘
              RC吸收电路
*/
```

**硬件改进**：
- 选用额定电流更大的继电器（留2倍余量）
- 使用固态继电器（SSR）替代机械继电器（无触点磨损）
- 添加RC吸收电路或压敏电阻（MOV）
- 定期清洁触点（使用无水酒精）

**寿命预测**：

| 负载类型 | 额定寿命 | 实际寿命 | 改进措施 |
|---------|---------|---------|---------|
| 阻性负载（加热器） | 10万次 | 8~10万次 | 无需改进 |
| 感性负载（电机） | 10万次 | 3~5万次 | 添加RC吸收 |
| 容性负载（电容器） | 10万次 | 2~3万次 | 添加限流电阻 |
| 灯负载（白炽灯） | 10万次 | 1~2万次 | 使用SSR |

### 4. I2C通信失败

**现象**：
- PCF8574无响应
- 继电器状态不更新
- I2C总线"卡死"

**原因分析**：
1. I2C地址冲突（两片PCF8574地址相同）
2. 上拉电阻不合适（过大或过小）
3. 线缆过长（超过1米）
4. 电源不稳定（PCF8574复位）

**解决方法**：

```c
// 1. I2C地址扫描
void i2c_scan(void) {
    printf("扫描I2C总线...\n");
    for (uint8_t addr = 0x20; addr <= 0x27; addr++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, addr << 1, 3, 100) == HAL_OK) {
            printf("发现设备：0x%02X\n", addr);
        }
    }
}

// 2. I2C错误恢复
void i2c_error_recovery(void) {
    // 检测I2C总线状态
    if (__HAL_I2C_GET_FLAG(&hi2c1, I2C_FLAG_BUSY)) {
        printf("I2C总线忙，尝试恢复...\n");
        
        // 方法1：软件复位
        HAL_I2C_DeInit(&hi2c1);
        HAL_Delay(10);
        HAL_I2C_Init(&hi2c1);
        
        // 方法2：时钟脉冲恢复（如果方法1无效）
        // 手动产生9个时钟脉冲，释放被拉低的SDA
        for (int i = 0; i < 9; i++) {
            HAL_GPIO_WritePin(I2C_SCL_GPIO_Port, I2C_SCL_Pin, GPIO_PIN_RESET);
            HAL_Delay(1);
            HAL_GPIO_WritePin(I2C_SCL_GPIO_Port, I2C_SCL_Pin, GPIO_PIN_SET);
            HAL_Delay(1);
        }
    }
}

// 3. 带重试的I2C写入
bool pcf8574_write_retry(uint8_t addr, uint8_t data, uint8_t retries) {
    for (uint8_t i = 0; i < retries; i++) {
        HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(&hi2c1, addr << 1,
                                                            &data, 1, 100);
        if (status == HAL_OK) {
            return true;
        }
        
        printf("I2C写入失败（尝试%d/%d），错误码：%d\n", i+1, retries, status);
        
        if (status == HAL_TIMEOUT) {
            i2c_error_recovery();
        }
        
        HAL_Delay(10);
    }
    return false;
}
```

**硬件检查**：
- 确认PCF8574地址引脚（A0/A1/A2）设置正确
- 测量上拉电阻值（推荐4.7kΩ，快速模式2.2kΩ）
- 缩短I2C线缆长度（<30cm为佳）
- 检查电源纹波（使用示波器）

### 5. 系统死机/看门狗复位

**现象**：
- 系统运行一段时间后死机
- 看门狗频繁复位
- 程序跑飞到非法地址

**原因分析**：
1. 栈溢出（递归调用、局部变量过大）
2. 野指针访问
3. 中断优先级配置错误
4. 任务执行时间过长，未及时喂狗

**解决方法**：

```c
// 1. 栈使用监控
void check_stack_usage(void) {
    extern uint32_t _estack;  // 栈顶地址（链接脚本定义）
    uint32_t stack_top = (uint32_t)&_estack;
    uint32_t stack_ptr = __get_MSP();  // 当前栈指针
    uint32_t stack_used = stack_top - stack_ptr;
    
    printf("栈使用：%lu / %lu 字节 (%.1f%%)\n",
           stack_used, STACK_SIZE, stack_used * 100.0f / STACK_SIZE);
    
    if (stack_used > STACK_SIZE * 0.8) {
        printf("警告：栈使用率过高！\n");
    }
}

// 2. 硬件故障检测
void hardfault_handler_c(uint32_t *hardfault_args) {
    uint32_t stacked_r0 = hardfault_args[0];
    uint32_t stacked_r1 = hardfault_args[1];
    uint32_t stacked_r2 = hardfault_args[2];
    uint32_t stacked_r3 = hardfault_args[3];
    uint32_t stacked_r12 = hardfault_args[4];
    uint32_t stacked_lr = hardfault_args[5];
    uint32_t stacked_pc = hardfault_args[6];
    uint32_t stacked_psr = hardfault_args[7];
    
    printf("HardFault!\n");
    printf("R0  = 0x%08lX\n", stacked_r0);
    printf("R1  = 0x%08lX\n", stacked_r1);
    printf("R2  = 0x%08lX\n", stacked_r2);
    printf("R3  = 0x%08lX\n", stacked_r3);
    printf("R12 = 0x%08lX\n", stacked_r12);
    printf("LR  = 0x%08lX\n", stacked_lr);
    printf("PC  = 0x%08lX\n", stacked_pc);  // 故障地址
    printf("PSR = 0x%08lX\n", stacked_psr);
    
    // 保存到Flash或EEPROM，重启后上报
    save_crash_log(stacked_pc, stacked_lr);
    
    while (1);  // 停止运行，等待复位
}

// 3. 任务执行时间监控
void task_monitor(void) {
    uint32_t start_time = HAL_GetTick();
    
    // 执行任务
    relay_control_task();
    
    uint32_t elapsed = HAL_GetTick() - start_time;
    if (elapsed > 100) {  // 任务超过100ms
        printf("警告：relay_control_task耗时%lums\n", elapsed);
    }
}

// 4. 看门狗喂狗策略优化
void watchdog_feed_strategy(void) {
    static uint32_t last_feed_time = 0;
    uint32_t now = HAL_GetTick();
    
    // 每500ms喂一次狗（看门狗超时1秒）
    if (now - last_feed_time >= 500) {
        // 检查所有关键任务是否正常
        if (modbus_task_alive && relay_task_alive && sensor_task_alive) {
            iwdg_feed();
            last_feed_time = now;
        } else {
            // 有任务异常，不喂狗，让系统复位
            printf("检测到任务异常，触发看门狗复位\n");
        }
    }
}
```

### 6. 电磁干扰（EMI）问题

**现象**：
- 继电器误动作
- 通信数据错误
- MCU复位

**解决方法**：
- 继电器线圈并联续流二极管（1N4007）
- 信号线使用屏蔽双绞线，屏蔽层单端接地
- 电源输入端添加共模电感和X/Y电容
- PCB布局：数字地和模拟地分开，单点接地
- 机箱接大地（PE保护地）

### 7. 温度传感器读数异常

**现象**：
- DS18B20读数为85°C（默认值）
- 读数跳变、不稳定

**解决方法**：

```c
// 1. 增加读取重试
float ds18b20_read_retry(uint8_t ch, uint8_t retries) {
    for (uint8_t i = 0; i < retries; i++) {
        float temp = ds18b20_read(ch);
        
        // 检查是否为有效值
        if (temp != 85.0f && temp > -55.0f && temp < 125.0f) {
            return temp;
        }
        
        HAL_Delay(100);
    }
    
    printf("DS18B20读取失败\n");
    return -999.0f;  // 错误标志
}

// 2. 添加滤波
#define TEMP_FILTER_SIZE  5
float temp_filter_buf[TEMP_FILTER_SIZE];
uint8_t temp_filter_idx = 0;

float ds18b20_read_filtered(uint8_t ch) {
    float temp = ds18b20_read(ch);
    
    // 存入滤波缓冲区
    temp_filter_buf[temp_filter_idx] = temp;
    temp_filter_idx = (temp_filter_idx + 1) % TEMP_FILTER_SIZE;
    
    // 计算平均值
    float sum = 0;
    for (int i = 0; i < TEMP_FILTER_SIZE; i++) {
        sum += temp_filter_buf[i];
    }
    
    return sum / TEMP_FILTER_SIZE;
}
```

**硬件检查**：
- 确认DS18B20供电电压（3.0~5.5V）
- 数据线上拉电阻4.7kΩ
- 线缆长度<20米（长距离需降低上拉电阻到2.2kΩ）

---

## 附录：Modbus寄存器完整映射表

| 地址 | 类型 | 访问 | 说明 | 单位/范围 |
|------|------|------|------|---------|
| 线圈 0x0000 | 线圈 | 读写 | 继电器CH0 | 0=断开，1=吸合 |
| 线圈 0x0001 | 线圈 | 读写 | 继电器CH1 | 0=断开，1=吸合 |
| 线圈 0x0002 | 线圈 | 读写 | 继电器CH2 | 0=断开，1=吸合 |
| 线圈 0x0003 | 线圈 | 读写 | 继电器CH3 | 0=断开，1=吸合 |
| 线圈 0x0004 | 线圈 | 读写 | 继电器CH4 | 0=断开，1=吸合 |
| 线圈 0x0005 | 线圈 | 读写 | 继电器CH5 | 0=断开，1=吸合 |
| 线圈 0x0006 | 线圈 | 读写 | 继电器CH6 | 0=断开，1=吸合 |
| 线圈 0x0007 | 线圈 | 读写 | 继电器CH7 | 0=断开，1=吸合 |
| 线圈 0x0008~0x000F | 线圈 | 读写 | 继电器CH8~CH15 | 同上 |
| 离散输入 0x0000 | 离散输入 | 只读 | 数字输入DI0 | 0/1 |
| 离散输入 0x0001 | 离散输入 | 只读 | 数字输入DI1 | 0/1 |
| 保持寄存器 0x0000 | 寄存器 | 读写 | 继电器状态掩码 | 16位，bit=1表示吸合 |
| 保持寄存器 0x0001 | 寄存器 | 只读 | 系统状态 | 0=正常，1=告警 |
| 保持寄存器 0x0002 | 寄存器 | 只读 | ADC输入1 | 0~4095 |
| 保持寄存器 0x0003 | 寄存器 | 只读 | ADC输入2 | 0~4095 |
| 保持寄存器 0x0010 | 寄存器 | 读写 | 顺序控制命令 | 1=启动，2=停止，3=暂停，4=恢复 |
| 保持寄存器 0x0011 | 寄存器 | 只读 | 顺序控制状态 | 0=空闲，1=运行，2=暂停，3=错误，4=完成 |
| 保持寄存器 0x0020 | 寄存器 | 只读 | 系统运行时间（秒） | 0~65535 |
| 保持寄存器 0x0021 | 寄存器 | 只读 | 告警计数 | 0~65535 |

**Modbus Poll配置示例**：

```
连接设置：
  Port: COM3（RS485转USB适配器）
  Baud Rate: 115200
  Data Bits: 8
  Parity: None
  Stop Bits: 1

读取继电器状态（FC01）：
  Slave ID: 1
  Function: 01 Read Coils
  Address: 0
  Length: 16

控制单路继电器（FC05）：
  Slave ID: 1
  Function: 05 Write Single Coil
  Address: 0（CH0）
  Value: FF00（吸合）或 0000（断开）

批量控制（FC0F）：
  Slave ID: 1
  Function: 0F Write Multiple Coils
  Address: 0
  Length: 16
  Data: 0x00FF（CH0~CH7吸合，CH8~CH15断开）
```
