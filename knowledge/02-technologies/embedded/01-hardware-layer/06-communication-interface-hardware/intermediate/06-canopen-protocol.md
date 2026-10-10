---
title: "CANopen协议实现与应用开发"
description: "深入学习CANopen工业通信协议的架构原理、对象字典、通信服务和实战应用，掌握工业自动化网络通信开发技术"
slug: "canopen-protocol-implementation"

# 分类信息
domain: "硬件层"
module: "通信接口硬件"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - CANopen
  - CAN总线
  - 工业通信
  - 对象字典
  - SDO/PDO
prerequisites:
  - "01-can-bus-hardware.md"
  - "../beginner/04-can-bus-basics.md"
related_contents:
  - "../../05-actuator-control/intermediate/02-bldc-motor-control.md"
  - "../../../06-communication-networking/02-network-protocols/advanced/01-j1939-protocol.md"

# 学习信息
estimated_time: 150
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-04-05"
updated_at: "2026-04-05"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - CANopen协议
  - 对象字典
  - SDO通信
  - PDO映射
  - 网络管理
cover_image: ""
---

# CANopen协议实现与应用开发

## 学习目标

完成本教程后，你将能够：

- [ ] 理解CANopen协议的架构设计和通信模型
- [ ] 掌握对象字典（Object Dictionary）的结构和配置
- [ ] 熟悉SDO和PDO通信服务的实现原理
- [ ] 能够配置和管理CANopen网络节点
- [ ] 使用CANopen协议栈进行设备开发
- [ ] 实现设备配置文件（Device Profile）
- [ ] 调试和解决CANopen通信问题

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉CAN总线基础知识和硬件接口
- 了解C语言编程和数据结构
- 理解工业通信协议基本概念
- 掌握嵌入式系统开发基础

**技能要求**：
- 能够使用CAN分析仪进行总线调试
- 会使用CANopen配置工具（如CANopen Magic）
- 了解EDS文件格式和DCF文件
- 熟悉RTOS基本使用（可选）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| STM32开发板 | 2+ | 带CAN控制器的MCU | STM32F103/F407/F767 |
| CAN收发器模块 | 2+ | CAN物理层收发器 | TJA1050/SN65HVD230 |
| CAN分析仪 | 1 | 用于总线监控和调试 | PCAN-USB/USBCAN |
| 120Ω终端电阻 | 2 | CAN总线终端匹配 | - |
| 杜邦线 | 若干 | 连接CAN总线 | - |
| USB调试器 | 1 | ST-Link V2或J-Link | - |

### 软件准备

| 软件 | 版本 | 用途 |
|------|------|------|
| STM32CubeIDE | 最新版 | 开发环境 |
| CANopenNode | v4.0+ | CANopen协议栈 |
| CANopen Magic | 最新版 | EDS编辑和配置 |
| PCAN-View | 最新版 | CAN总线监控 |
| Wireshark | 最新版 | 协议分析（可选） |


## 1. CANopen协议简介

### 1.1 什么是CANopen

CANopen是一种基于CAN（Controller Area Network）总线的高层通信协议，由CAN in Automation（CiA）组织制定和维护。它为工业自动化、医疗设备、轨道交通等领域提供了标准化的通信解决方案。

**核心特点**：
- **标准化**：遵循CiA 301规范，确保不同厂商设备互操作性
- **灵活性**：支持多种通信模型（SDO、PDO、NMT、SYNC等）
- **实时性**：PDO通信提供确定性实时数据传输
- **可配置**：通过对象字典实现设备参数化配置
- **模块化**：设备配置文件（Device Profile）定义标准设备类型

**应用领域**：
- 工业自动化（PLC、伺服驱动、传感器）
- 医疗设备（手术机器人、诊断设备）
- 轨道交通（列车控制系统）
- 楼宇自动化（电梯控制、HVAC系统）
- 新能源（电动汽车充电桩、储能系统）

### 1.2 CANopen协议架构

CANopen协议采用分层架构，建立在CAN 2.0A/B物理层和数据链路层之上：

```
┌─────────────────────────────────────────┐
│        应用层（Application Layer）        │
│  设备配置文件（Device Profiles）          │
├─────────────────────────────────────────┤
│      CANopen应用层（CANopen Layer）       │
│  SDO | PDO | NMT | SYNC | EMCY | TIME   │
├─────────────────────────────────────────┤
│      CAN数据链路层（CAN Data Link）       │
│  帧格式 | 仲裁 | 错误检测                 │
├─────────────────────────────────────────┤
│      CAN物理层（CAN Physical Layer）      │
│  差分信号 | 位时序 | 总线拓扑              │
└─────────────────────────────────────────┘
```

**通信服务类型**：

1. **SDO（Service Data Object）**：服务数据对象
   - 用于配置和参数访问
   - 面向连接的通信
   - 支持分段传输大数据

2. **PDO（Process Data Object）**：过程数据对象
   - 用于实时过程数据交换
   - 无连接的广播通信
   - 低延迟、高效率

3. **NMT（Network Management）**：网络管理
   - 节点状态控制（初始化、运行、停止）
   - 心跳监控和节点保护

4. **SYNC（Synchronization）**：同步对象
   - 提供网络同步时钟
   - 协调PDO同步传输

5. **EMCY（Emergency）**：紧急对象
   - 报告设备错误和异常
   - 高优先级传输

6. **TIME（Time Stamp）**：时间戳对象
   - 提供网络时间同步
   - 用于事件时间标记

### 1.3 CANopen标识符分配

CANopen使用11位CAN标识符（CAN 2.0A），采用预定义连接集（Predefined Connection Set）分配方案：

| COB-ID范围 | 功能 | 优先级 |
|-----------|------|--------|
| 0x000 | NMT（网络管理） | 最高 |
| 0x001 | SYNC（同步对象） | 最高 |
| 0x080 | EMCY（紧急对象） | 高 |
| 0x100 | TIME（时间戳） | 高 |
| 0x180-0x1FF | TPDO1（发送PDO1） | 高 |
| 0x200-0x27F | RPDO1（接收PDO1） | 高 |
| 0x280-0x2FF | TPDO2（发送PDO2） | 中 |
| 0x300-0x37F | RPDO2（接收PDO2） | 中 |
| 0x380-0x3FF | TPDO3（发送PDO3） | 中 |
| 0x400-0x47F | RPDO3（接收PDO3） | 中 |
| 0x480-0x4FF | TPDO4（发送PDO4） | 低 |
| 0x500-0x57F | RPDO4（接收PDO4） | 低 |
| 0x580-0x5FF | SDO响应（Tx） | 低 |
| 0x600-0x67F | SDO请求（Rx） | 低 |
| 0x700-0x7FF | NMT心跳 | 最低 |

**COB-ID计算公式**：
```
COB-ID = 功能码 + 节点ID
例如：节点5的TPDO1 = 0x180 + 5 = 0x185
```

### 1.4 CANopen节点状态机

每个CANopen节点都有一个状态机，由NMT主站控制：

```
        ┌──────────────┐
        │  初始化状态   │
        │ Initializing │
        └──────┬───────┘
               │ 自动
               ↓
        ┌──────────────┐
        │  预操作状态   │
        │ Pre-Operational│←──┐
        └──────┬───────┘    │
               │ Start      │ Stop
               ↓            │
        ┌──────────────┐    │
        │  操作状态     │────┘
        │ Operational  │
        └──────┬───────┘
               │ Stop
               ↓
        ┌──────────────┐
        │  停止状态     │
        │   Stopped    │
        └──────────────┘
```

**状态说明**：

1. **Initializing（初始化）**：
   - 节点上电后的初始状态
   - 执行硬件初始化和自检
   - 自动进入Pre-Operational状态

2. **Pre-Operational（预操作）**：
   - 可以接收SDO配置
   - 不能发送/接收PDO
   - 用于设备配置和参数设置

3. **Operational（操作）**：
   - 正常工作状态
   - 可以发送/接收PDO和SDO
   - 执行实时通信任务

4. **Stopped（停止）**：
   - 只能接收NMT命令
   - 不能进行SDO和PDO通信
   - 用于设备维护或故障隔离


## 2. 对象字典（Object Dictionary）

### 2.1 对象字典概述

对象字典是CANopen设备的核心数据结构，它定义了设备的所有参数、配置和通信对象。可以将其理解为设备的"数据库"或"寄存器映射表"。

**对象字典结构**：
- 使用16位索引（Index）和8位子索引（Sub-index）寻址
- 索引范围：0x0000 - 0xFFFF
- 每个索引可以包含多个子索引（数组或记录类型）

**对象类型**：

1. **VAR（变量）**：单个数据项
2. **ARRAY（数组）**：相同类型的数据集合
3. **RECORD（记录）**：不同类型的数据集合

**访问权限**：
- **RO（Read Only）**：只读
- **WO（Write Only）**：只写
- **RW（Read/Write）**：读写
- **RWR（Read/Write on Reset）**：复位时可写
- **RWW（Read/Write on Write）**：写入时可读写

### 2.2 对象字典标准区域划分

| 索引范围 | 名称 | 说明 |
|---------|------|------|
| 0x0000 | 未使用 | 保留 |
| 0x0001-0x001F | 数据类型 | 标准数据类型定义 |
| 0x0020-0x003F | 复杂数据类型 | 用户自定义数据类型 |
| 0x0040-0x005F | 厂商特定 | 厂商自定义数据类型 |
| 0x0060-0x007F | 设备配置文件 | 特定设备类型数据类型 |
| 0x0080-0x009F | 保留 | 未来扩展 |
| 0x1000-0x1FFF | 通信配置区 | 通信参数和对象 |
| 0x2000-0x5FFF | 厂商特定区 | 厂商自定义对象 |
| 0x6000-0x9FFF | 标准设备配置区 | 设备配置文件对象 |
| 0xA000-0xFFFF | 保留 | 未来扩展 |

### 2.3 通信配置区对象（0x1000-0x1FFF）

**核心通信对象**：

```c
// 设备类型（0x1000）
#define OD_DEVICE_TYPE              0x1000
// 子索引0：设备类型值
// 例如：0x00000000（通用设备）

// 错误寄存器（0x1001）
#define OD_ERROR_REGISTER           0x1001
// 子索引0：错误状态位
// Bit 0: 通用错误
// Bit 1: 电流错误
// Bit 2: 电压错误
// Bit 3: 温度错误
// Bit 4: 通信错误
// Bit 5: 设备配置文件特定错误
// Bit 6-7: 保留

// 制造商状态寄存器（0x1002）
#define OD_MANUFACTURER_STATUS      0x1002
// 子索引0：厂商特定状态

// 预定义错误字段（0x1003）
#define OD_PRE_DEFINED_ERROR_FIELD  0x1003
// 子索引0：错误历史数量
// 子索引1-8：错误代码历史

// COB-ID SYNC（0x1005）
#define OD_COB_ID_SYNC              0x1005
// 子索引0：SYNC对象的COB-ID

// 通信周期时间（0x1006）
#define OD_COMMUNICATION_CYCLE      0x1006
// 子索引0：SYNC周期（微秒）

// 同步窗口长度（0x1007）
#define OD_SYNC_WINDOW_LENGTH       0x1007
// 子索引0：同步窗口时间（微秒）

// 制造商设备名称（0x1008）
#define OD_MANUFACTURER_DEVICE_NAME 0x1008
// 子索引0：设备名称字符串

// 制造商硬件版本（0x1009）
#define OD_MANUFACTURER_HW_VERSION  0x1009
// 子索引0：硬件版本字符串

// 制造商软件版本（0x100A）
#define OD_MANUFACTURER_SW_VERSION  0x100A
// 子索引0：软件版本字符串

// 节点ID（0x100B）
#define OD_NODE_ID                  0x100B
// 子索引0：当前节点ID（1-127）

// 保护时间（0x100C）
#define OD_GUARD_TIME               0x100C
// 子索引0：节点保护时间（毫秒）

// 生命周期因子（0x100D）
#define OD_LIFE_TIME_FACTOR         0x100D
// 子索引0：生命周期因子

// 存储参数（0x1010）
#define OD_STORE_PARAMETERS         0x1010
// 子索引0：子索引数量
// 子索引1：保存所有参数
// 子索引2：保存通信参数
// 子索引3：保存应用参数

// 恢复默认参数（0x1011）
#define OD_RESTORE_DEFAULT_PARAM    0x1011
// 子索引0：子索引数量
// 子索引1：恢复所有参数
// 子索引2：恢复通信参数
// 子索引3：恢复应用参数

// COB-ID EMCY（0x1014）
#define OD_COB_ID_EMCY              0x1014
// 子索引0：EMCY对象的COB-ID

// 禁止时间（0x1015）
#define OD_INHIBIT_TIME_EMCY        0x1015
// 子索引0：EMCY禁止时间（100微秒单位）

// 消费者心跳时间（0x1016）
#define OD_CONSUMER_HEARTBEAT_TIME  0x1016
// 子索引0：监控节点数量
// 子索引1-127：节点ID和心跳时间

// 生产者心跳时间（0x1017）
#define OD_PRODUCER_HEARTBEAT_TIME  0x1017
// 子索引0：心跳周期（毫秒）

// 身份对象（0x1018）
#define OD_IDENTITY_OBJECT          0x1018
// 子索引0：子索引数量（4）
// 子索引1：厂商ID
// 子索引2：产品代码
// 子索引3：版本号
// 子索引4：序列号
```

### 2.4 SDO服务器参数（0x1200-0x127F）

SDO服务器参数定义了SDO通信的COB-ID：

```c
// SDO服务器参数（0x1200）
typedef struct {
    uint8_t  numberOfEntries;    // 子索引0：条目数量（2）
    uint32_t COB_IDClientToServer; // 子索引1：客户端到服务器COB-ID（Rx）
    uint32_t COB_IDServerToClient; // 子索引2：服务器到客户端COB-ID（Tx）
} OD_SDOServerParameter_t;

// 默认值（节点ID = N）：
// 子索引1：0x600 + N（接收SDO请求）
// 子索引2：0x580 + N（发送SDO响应）
```

### 2.5 接收PDO通信参数（0x1400-0x15FF）

接收PDO（RPDO）通信参数定义了PDO的COB-ID和传输类型：

```c
// RPDO通信参数（0x1400-0x15FF）
typedef struct {
    uint8_t  numberOfEntries;    // 子索引0：条目数量
    uint32_t COB_ID;             // 子索引1：COB-ID
    uint8_t  transmissionType;   // 子索引2：传输类型
    uint16_t inhibitTime;        // 子索引3：禁止时间（可选）
    uint8_t  compatibilityEntry; // 子索引4：兼容性条目（可选）
    uint16_t eventTimer;         // 子索引5：事件定时器（可选）
    uint8_t  SYNCStartValue;     // 子索引6：SYNC起始值（可选）
} OD_RPDOCommunicationParameter_t;

// 传输类型值：
// 0：同步（非循环）
// 1-240：同步（循环，每N个SYNC）
// 241-251：保留
// 252-253：同步RTR
// 254：异步（事件驱动）
// 255：异步（设备配置文件特定）
```

### 2.6 接收PDO映射参数（0x1600-0x17FF）

接收PDO映射参数定义了PDO数据字段到对象字典的映射关系：

```c
// RPDO映射参数（0x1600-0x17FF）
typedef struct {
    uint8_t  numberOfEntries;    // 子索引0：映射对象数量（0-8）
    uint32_t mappedObject1;      // 子索引1：映射对象1
    uint32_t mappedObject2;      // 子索引2：映射对象2
    // ... 最多8个映射对象
} OD_RPDOMappingParameter_t;

// 映射对象格式（32位）：
// Bit 31-16：对象字典索引
// Bit 15-8：子索引
// Bit 7-0：数据长度（位）

// 示例：映射0x6040子索引0（16位）
// 映射值 = (0x6040 << 16) | (0x00 << 8) | 16 = 0x60400010
```

### 2.7 发送PDO通信参数（0x1800-0x19FF）

发送PDO（TPDO）通信参数与RPDO类似，但用于发送数据：

```c
// TPDO通信参数（0x1800-0x19FF）
typedef struct {
    uint8_t  numberOfEntries;    // 子索引0：条目数量
    uint32_t COB_ID;             // 子索引1：COB-ID
    uint8_t  transmissionType;   // 子索引2：传输类型
    uint16_t inhibitTime;        // 子索引3：禁止时间（100微秒单位）
    uint8_t  compatibilityEntry; // 子索引4：兼容性条目（可选）
    uint16_t eventTimer;         // 子索引5：事件定时器（毫秒）
    uint8_t  SYNCStartValue;     // 子索引6：SYNC起始值（可选）
} OD_TPDOCommunicationParameter_t;
```

### 2.8 发送PDO映射参数（0x1A00-0x1BFF）

发送PDO映射参数定义了对象字典到PDO数据字段的映射：

```c
// TPDO映射参数（0x1A00-0x1BFF）
typedef struct {
    uint8_t  numberOfEntries;    // 子索引0：映射对象数量（0-8）
    uint32_t mappedObject1;      // 子索引1：映射对象1
    uint32_t mappedObject2;      // 子索引2：映射对象2
    // ... 最多8个映射对象
} OD_TPDOMappingParameter_t;
```

### 2.9 对象字典示例

以下是一个简单的对象字典定义示例：

```c
// 对象字典条目结构
typedef struct {
    uint16_t index;              // 索引
    uint8_t  subIndex;           // 子索引
    uint8_t  dataType;           // 数据类型
    uint8_t  attribute;          // 访问属性
    uint32_t dataLength;         // 数据长度
    void*    pData;              // 数据指针
} OD_Entry_t;

// 示例：设备类型对象（0x1000）
uint32_t OD_DeviceType = 0x00000000;

OD_Entry_t OD_1000 = {
    .index = 0x1000,
    .subIndex = 0,
    .dataType = 0x07,            // UNSIGNED32
    .attribute = ODA_SDO_R,      // SDO只读
    .dataLength = 4,
    .pData = &OD_DeviceType
};

// 示例：错误寄存器（0x1001）
uint8_t OD_ErrorRegister = 0x00;

OD_Entry_t OD_1001 = {
    .index = 0x1001,
    .subIndex = 0,
    .dataType = 0x05,            // UNSIGNED8
    .attribute = ODA_SDO_R,      // SDO只读
    .dataLength = 1,
    .pData = &OD_ErrorRegister
};

// 示例：制造商设备名称（0x1008）
char OD_ManufacturerDeviceName[] = "CANopen Device";

OD_Entry_t OD_1008 = {
    .index = 0x1008,
    .subIndex = 0,
    .dataType = 0x09,            // VISIBLE_STRING
    .attribute = ODA_SDO_R,      // SDO只读
    .dataLength = sizeof(OD_ManufacturerDeviceName),
    .pData = OD_ManufacturerDeviceName
};

// 示例：心跳生产者时间（0x1017）
uint16_t OD_ProducerHeartbeatTime = 1000; // 1000ms

OD_Entry_t OD_1017 = {
    .index = 0x1017,
    .subIndex = 0,
    .dataType = 0x06,            // UNSIGNED16
    .attribute = ODA_SDO_RW,     // SDO读写
    .dataLength = 2,
    .pData = &OD_ProducerHeartbeatTime
};
```


## 3. SDO通信服务

### 3.1 SDO通信概述

SDO（Service Data Object）是CANopen中用于配置和参数访问的通信服务。它提供了面向连接的、可靠的数据传输机制，支持访问对象字典中的任意对象。

**SDO特点**：
- **面向连接**：客户端-服务器模型
- **可靠传输**：带确认和错误检测
- **分段传输**：支持传输大于7字节的数据
- **灵活访问**：可读写对象字典任意对象
- **低优先级**：适用于非实时配置任务

**SDO通信模型**：
```
┌──────────────┐                    ┌──────────────┐
│  SDO客户端   │                    │  SDO服务器   │
│  (Master)    │                    │  (Slave)     │
├──────────────┤                    ├──────────────┤
│ 发送请求     │──── SDO请求 ────→  │ 接收请求     │
│ COB-ID:0x600+N│                    │ 处理请求     │
│              │                    │ 访问对象字典 │
│ 接收响应     │←─── SDO响应 ────  │ 发送响应     │
│ COB-ID:0x580+N│                    │ COB-ID:0x580+N│
└──────────────┘                    └──────────────┘
```

### 3.2 SDO协议格式

SDO使用8字节CAN数据帧，格式如下：

```
┌────┬────┬────┬────┬────┬────┬────┬────┐
│Byte│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│    │ CS │Index_L│Index_H│Sub │  Data (4 bytes)  │
└────┴────┴────┴────┴────┴────┴────┴────┘

CS: 命令说明符（Command Specifier）
Index: 对象字典索引（16位，小端序）
Sub: 子索引（8位）
Data: 数据字段（4字节）
```

**命令说明符（CS）格式**：
```
Bit 7  6  5  4  3  2  1  0
    │  │  │  │  │  │  │  │
    │  │  │  │  │  │  │  └─ 保留
    │  │  │  │  └──┴──┴──── 数据字节数（n）或传输类型
    │  │  └──┴──────────── 命令类型
    └──┴──────────────── 客户端命令说明符（ccs）或服务器命令说明符（scs）
```

### 3.3 SDO下载（写入）

SDO下载用于客户端向服务器写入数据到对象字典。

**快速下载（数据≤4字节）**：

```c
// 客户端请求（下载初始化）
typedef struct {
    uint8_t cs;          // 0x23: 下载，4字节数据
                         // 0x2F: 下载，1字节数据
                         // 0x2B: 下载，2字节数据
                         // 0x27: 下载，3字节数据
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t data[4];     // 数据（小端序）
} SDO_DownloadInitiate_t;

// 服务器响应（下载确认）
typedef struct {
    uint8_t cs;          // 0x60: 下载确认
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t reserved[4]; // 保留（全0）
} SDO_DownloadResponse_t;

// 示例：写入心跳时间（0x1017，值=1000ms）
uint8_t sdo_request[8] = {
    0x2B,                // CS: 下载，2字节数据
    0x17, 0x10,          // Index: 0x1017
    0x00,                // SubIndex: 0
    0xE8, 0x03, 0x00, 0x00  // Data: 1000 (0x03E8)
};

// 服务器响应
uint8_t sdo_response[8] = {
    0x60,                // CS: 下载确认
    0x17, 0x10,          // Index: 0x1017
    0x00,                // SubIndex: 0
    0x00, 0x00, 0x00, 0x00  // Reserved
};
```

**分段下载（数据>4字节）**：

```c
// 1. 下载初始化请求
typedef struct {
    uint8_t cs;          // 0x21: 下载初始化，指示数据大小
                         // 0x20: 下载初始化，未指示数据大小
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint32_t dataSize;   // 数据总大小（字节）
} SDO_DownloadInitiateSegmented_t;

// 2. 下载初始化响应
typedef struct {
    uint8_t cs;          // 0x60: 下载确认
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t reserved[4]; // 保留
} SDO_DownloadInitiateResponse_t;

// 3. 下载分段请求
typedef struct {
    uint8_t cs;          // Bit 7-5: 000（下载分段）
                         // Bit 4: toggle（切换位，0/1交替）
                         // Bit 3-1: n（7-n = 有效数据字节数）
                         // Bit 0: c（最后一段标志）
    uint8_t data[7];     // 分段数据（最多7字节）
} SDO_DownloadSegment_t;

// 4. 下载分段响应
typedef struct {
    uint8_t cs;          // Bit 7-5: 001（下载分段确认）
                         // Bit 4: toggle（切换位，与请求相同）
                         // Bit 3-0: 保留
    uint8_t reserved[7]; // 保留
} SDO_DownloadSegmentResponse_t;

// 示例：分段下载流程
void SDO_SegmentedDownload(uint16_t index, uint8_t subIndex, 
                           uint8_t* data, uint32_t size) {
    // 1. 发送下载初始化
    uint8_t init_req[8] = {
        0x21,                    // CS: 下载初始化，指示大小
        index & 0xFF, index >> 8,// Index
        subIndex,                // SubIndex
        size & 0xFF, (size >> 8) & 0xFF,
        (size >> 16) & 0xFF, (size >> 24) & 0xFF
    };
    CAN_Send(0x600 + nodeID, init_req, 8);
    
    // 2. 等待下载初始化响应
    // ...
    
    // 3. 发送数据分段
    uint8_t toggle = 0;
    uint32_t offset = 0;
    
    while (offset < size) {
        uint8_t seg_req[8];
        uint8_t bytes_to_send = (size - offset > 7) ? 7 : (size - offset);
        uint8_t n = 7 - bytes_to_send;
        uint8_t c = (offset + bytes_to_send >= size) ? 1 : 0;
        
        seg_req[0] = (toggle << 4) | (n << 1) | c;
        memcpy(&seg_req[1], &data[offset], bytes_to_send);
        memset(&seg_req[1 + bytes_to_send], 0, 7 - bytes_to_send);
        
        CAN_Send(0x600 + nodeID, seg_req, 8);
        
        // 等待分段响应
        // ...
        
        toggle ^= 1;  // 切换位翻转
        offset += bytes_to_send;
    }
}
```

### 3.4 SDO上传（读取）

SDO上传用于客户端从服务器读取对象字典数据。

**快速上传（数据≤4字节）**：

```c
// 客户端请求（上传初始化）
typedef struct {
    uint8_t cs;          // 0x40: 上传初始化
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t reserved[4]; // 保留（全0）
} SDO_UploadInitiate_t;

// 服务器响应（上传数据）
typedef struct {
    uint8_t cs;          // 0x43: 上传，4字节数据
                         // 0x4F: 上传，1字节数据
                         // 0x4B: 上传，2字节数据
                         // 0x47: 上传，3字节数据
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t data[4];     // 数据（小端序）
} SDO_UploadResponse_t;

// 示例：读取心跳时间（0x1017）
uint8_t sdo_request[8] = {
    0x40,                // CS: 上传初始化
    0x17, 0x10,          // Index: 0x1017
    0x00,                // SubIndex: 0
    0x00, 0x00, 0x00, 0x00  // Reserved
};

// 服务器响应（假设值为1000ms）
uint8_t sdo_response[8] = {
    0x4B,                // CS: 上传，2字节数据
    0x17, 0x10,          // Index: 0x1017
    0x00,                // SubIndex: 0
    0xE8, 0x03, 0x00, 0x00  // Data: 1000 (0x03E8)
};
```

**分段上传（数据>4字节）**：

```c
// 1. 上传初始化请求
typedef struct {
    uint8_t cs;          // 0x40: 上传初始化
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint8_t reserved[4]; // 保留
} SDO_UploadInitiateSegmented_t;

// 2. 上传初始化响应
typedef struct {
    uint8_t cs;          // 0x41: 上传初始化，指示数据大小
                         // 0x40: 上传初始化，未指示数据大小
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint32_t dataSize;   // 数据总大小（字节）
} SDO_UploadInitiateResponse_t;

// 3. 上传分段请求
typedef struct {
    uint8_t cs;          // Bit 7-5: 011（上传分段）
                         // Bit 4: toggle（切换位，0/1交替）
                         // Bit 3-0: 保留
    uint8_t reserved[7]; // 保留
} SDO_UploadSegment_t;

// 4. 上传分段响应
typedef struct {
    uint8_t cs;          // Bit 7-5: 000（上传分段数据）
                         // Bit 4: toggle（切换位，与请求相同）
                         // Bit 3-1: n（7-n = 有效数据字节数）
                         // Bit 0: c（最后一段标志）
    uint8_t data[7];     // 分段数据（最多7字节）
} SDO_UploadSegmentResponse_t;
```

### 3.5 SDO中止传输

当SDO传输出现错误时，可以发送中止传输消息：

```c
// SDO中止传输
typedef struct {
    uint8_t cs;          // 0x80: 中止传输
    uint16_t index;      // 对象索引
    uint8_t subIndex;    // 子索引
    uint32_t abortCode;  // 中止代码
} SDO_Abort_t;

// 常见中止代码
#define SDO_ABORT_TOGGLE_BIT            0x05030000  // 切换位错误
#define SDO_ABORT_TIMEOUT               0x05040000  // SDO超时
#define SDO_ABORT_CMD_SPECIFIER         0x05040001  // 无效命令说明符
#define SDO_ABORT_BLOCK_SIZE            0x05040002  // 无效块大小
#define SDO_ABORT_SEQ_NUM               0x05040003  // 无效序列号
#define SDO_ABORT_CRC                   0x05040004  // CRC错误
#define SDO_ABORT_OUT_OF_MEMORY         0x05040005  // 内存不足
#define SDO_ABORT_UNSUPPORTED_ACCESS    0x06010000  // 不支持的访问
#define SDO_ABORT_WRITE_ONLY            0x06010001  // 尝试读取只写对象
#define SDO_ABORT_READ_ONLY             0x06010002  // 尝试写入只读对象
#define SDO_ABORT_OBJECT_NOT_EXIST      0x06020000  // 对象不存在
#define SDO_ABORT_CANNOT_MAP_PDO        0x06040041  // 对象不能映射到PDO
#define SDO_ABORT_PDO_LENGTH_EXCEEDED   0x06040042  // PDO长度超限
#define SDO_ABORT_PARAM_INCOMPATIBILITY 0x06040043  // 参数不兼容
#define SDO_ABORT_INTERNAL_INCOMPATIBILITY 0x06040047 // 内部不兼容
#define SDO_ABORT_HARDWARE_ERROR        0x06060000  // 硬件错误
#define SDO_ABORT_DATA_TYPE_MISMATCH    0x06070010  // 数据类型不匹配
#define SDO_ABORT_DATA_TYPE_LENGTH_HIGH 0x06070012  // 数据长度过大
#define SDO_ABORT_DATA_TYPE_LENGTH_LOW  0x06070013  // 数据长度过小
#define SDO_ABORT_SUB_INDEX_NOT_EXIST   0x06090011  // 子索引不存在
#define SDO_ABORT_VALUE_RANGE_EXCEEDED  0x06090030  // 值超出范围
#define SDO_ABORT_VALUE_TOO_HIGH        0x06090031  // 值过大
#define SDO_ABORT_VALUE_TOO_LOW         0x06090032  // 值过小
#define SDO_ABORT_MAX_LESS_MIN          0x06090036  // 最大值小于最小值
#define SDO_ABORT_GENERAL_ERROR         0x08000000  // 通用错误
#define SDO_ABORT_DATA_TRANSFER         0x08000020  // 数据传输错误
#define SDO_ABORT_DATA_TRANSFER_LOCAL   0x08000021  // 本地控制错误
#define SDO_ABORT_DATA_TRANSFER_STATE   0x08000022  // 设备状态错误
#define SDO_ABORT_DICTIONARY_ERROR      0x08000023  // 对象字典错误
```

### 3.6 SDO实现示例

```c
// SDO服务器实现
typedef struct {
    uint8_t state;           // SDO状态
    uint16_t index;          // 当前索引
    uint8_t subIndex;        // 当前子索引
    uint8_t* buffer;         // 数据缓冲区
    uint32_t size;           // 数据大小
    uint32_t offset;         // 当前偏移
    uint8_t toggle;          // 切换位
} SDO_Server_t;

// SDO状态定义
#define SDO_STATE_IDLE              0
#define SDO_STATE_DOWNLOAD_INITIATE 1
#define SDO_STATE_DOWNLOAD_SEGMENT  2
#define SDO_STATE_UPLOAD_INITIATE   3
#define SDO_STATE_UPLOAD_SEGMENT    4

// SDO服务器初始化
void SDO_ServerInit(SDO_Server_t* sdo, uint8_t nodeID) {
    sdo->state = SDO_STATE_IDLE;
    sdo->index = 0;
    sdo->subIndex = 0;
    sdo->buffer = NULL;
    sdo->size = 0;
    sdo->offset = 0;
    sdo->toggle = 0;
    
    // 配置SDO接收过滤器
    CAN_SetFilter(0x600 + nodeID, 0x7FF);
}

// SDO请求处理
void SDO_ProcessRequest(SDO_Server_t* sdo, uint8_t* data) {
    uint8_t cs = data[0];
    uint16_t index = data[1] | (data[2] << 8);
    uint8_t subIndex = data[3];
    
    // 解析命令类型
    uint8_t ccs = (cs >> 5) & 0x07;
    
    switch (ccs) {
        case 1:  // 下载初始化
            SDO_HandleDownloadInitiate(sdo, data);
            break;
            
        case 0:  // 下载分段
            SDO_HandleDownloadSegment(sdo, data);
            break;
            
        case 2:  // 上传初始化
            SDO_HandleUploadInitiate(sdo, data);
            break;
            
        case 3:  // 上传分段
            SDO_HandleUploadSegment(sdo, data);
            break;
            
        case 4:  // 中止传输
            SDO_HandleAbort(sdo, data);
            break;
            
        default:
            // 发送中止：无效命令说明符
            SDO_SendAbort(sdo, index, subIndex, SDO_ABORT_CMD_SPECIFIER);
            break;
    }
}

// 处理下载初始化
void SDO_HandleDownloadInitiate(SDO_Server_t* sdo, uint8_t* data) {
    uint8_t cs = data[0];
    uint16_t index = data[1] | (data[2] << 8);
    uint8_t subIndex = data[3];
    
    // 检查对象是否存在
    OD_Entry_t* entry = OD_FindEntry(index, subIndex);
    if (entry == NULL) {
        SDO_SendAbort(sdo, index, subIndex, SDO_ABORT_OBJECT_NOT_EXIST);
        return;
    }
    
    // 检查访问权限
    if (!(entry->attribute & ODA_SDO_W)) {
        SDO_SendAbort(sdo, index, subIndex, SDO_ABORT_READ_ONLY);
        return;
    }
    
    // 判断是快速下载还是分段下载
    if (cs & 0x02) {  // 快速下载（数据大小指示）
        uint8_t n = (cs >> 2) & 0x03;
        uint8_t dataSize = 4 - n;
        
        // 写入数据到对象字典
        memcpy(entry->pData, &data[4], dataSize);
        
        // 发送下载确认
        uint8_t response[8] = {0x60, data[1], data[2], data[3], 0, 0, 0, 0};
        CAN_Send(0x580 + nodeID, response, 8);
        
        sdo->state = SDO_STATE_IDLE;
    } else {  // 分段下载
        // 保存索引和子索引
        sdo->index = index;
        sdo->subIndex = subIndex;
        sdo->buffer = (uint8_t*)entry->pData;
        sdo->offset = 0;
        sdo->toggle = 0;
        
        if (cs & 0x01) {  // 数据大小指示
            sdo->size = data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24);
        } else {
            sdo->size = entry->dataLength;
        }
        
        // 发送下载初始化响应
        uint8_t response[8] = {0x60, data[1], data[2], data[3], 0, 0, 0, 0};
        CAN_Send(0x580 + nodeID, response, 8);
        
        sdo->state = SDO_STATE_DOWNLOAD_SEGMENT;
    }
}

// 处理下载分段
void SDO_HandleDownloadSegment(SDO_Server_t* sdo, uint8_t* data) {
    if (sdo->state != SDO_STATE_DOWNLOAD_SEGMENT) {
        SDO_SendAbort(sdo, sdo->index, sdo->subIndex, SDO_ABORT_CMD_SPECIFIER);
        return;
    }
    
    uint8_t cs = data[0];
    uint8_t toggle = (cs >> 4) & 0x01;
    uint8_t n = (cs >> 1) & 0x07;
    uint8_t c = cs & 0x01;
    uint8_t dataSize = 7 - n;
    
    // 检查切换位
    if (toggle != sdo->toggle) {
        SDO_SendAbort(sdo, sdo->index, sdo->subIndex, SDO_ABORT_TOGGLE_BIT);
        return;
    }
    
    // 复制数据
    memcpy(&sdo->buffer[sdo->offset], &data[1], dataSize);
    sdo->offset += dataSize;
    
    // 发送下载分段响应
    uint8_t response[8] = {(0x01 << 5) | (toggle << 4), 0, 0, 0, 0, 0, 0, 0};
    CAN_Send(0x580 + nodeID, response, 8);
    
    // 切换位翻转
    sdo->toggle ^= 1;
    
    // 检查是否为最后一段
    if (c) {
        sdo->state = SDO_STATE_IDLE;
    }
}

// 处理上传初始化
void SDO_HandleUploadInitiate(SDO_Server_t* sdo, uint8_t* data) {
    uint16_t index = data[1] | (data[2] << 8);
    uint8_t subIndex = data[3];
    
    // 检查对象是否存在
    OD_Entry_t* entry = OD_FindEntry(index, subIndex);
    if (entry == NULL) {
        SDO_SendAbort(sdo, index, subIndex, SDO_ABORT_OBJECT_NOT_EXIST);
        return;
    }
    
    // 检查访问权限
    if (!(entry->attribute & ODA_SDO_R)) {
        SDO_SendAbort(sdo, index, subIndex, SDO_ABORT_WRITE_ONLY);
        return;
    }
    
    // 判断是快速上传还是分段上传
    if (entry->dataLength <= 4) {  // 快速上传
        uint8_t n = 4 - entry->dataLength;
        uint8_t response[8] = {
            (0x02 << 5) | (n << 2) | 0x03,  // CS: 上传，指示大小
            data[1], data[2], data[3],      // Index and SubIndex
            0, 0, 0, 0
        };
        memcpy(&response[4], entry->pData, entry->dataLength);
        CAN_Send(0x580 + nodeID, response, 8);
        
        sdo->state = SDO_STATE_IDLE;
    } else {  // 分段上传
        sdo->index = index;
        sdo->subIndex = subIndex;
        sdo->buffer = (uint8_t*)entry->pData;
        sdo->size = entry->dataLength;
        sdo->offset = 0;
        sdo->toggle = 0;
        
        // 发送上传初始化响应
        uint8_t response[8] = {
            0x41,  // CS: 上传初始化，指示大小
            data[1], data[2], data[3],
            sdo->size & 0xFF, (sdo->size >> 8) & 0xFF,
            (sdo->size >> 16) & 0xFF, (sdo->size >> 24) & 0xFF
        };
        CAN_Send(0x580 + nodeID, response, 8);
        
        sdo->state = SDO_STATE_UPLOAD_SEGMENT;
    }
}

// 处理上传分段
void SDO_HandleUploadSegment(SDO_Server_t* sdo, uint8_t* data) {
    if (sdo->state != SDO_STATE_UPLOAD_SEGMENT) {
        SDO_SendAbort(sdo, sdo->index, sdo->subIndex, SDO_ABORT_CMD_SPECIFIER);
        return;
    }
    
    uint8_t cs = data[0];
    uint8_t toggle = (cs >> 4) & 0x01;
    
    // 检查切换位
    if (toggle != sdo->toggle) {
        SDO_SendAbort(sdo, sdo->index, sdo->subIndex, SDO_ABORT_TOGGLE_BIT);
        return;
    }
    
    // 计算本段数据大小
    uint32_t remaining = sdo->size - sdo->offset;
    uint8_t dataSize = (remaining > 7) ? 7 : remaining;
    uint8_t n = 7 - dataSize;
    uint8_t c = (sdo->offset + dataSize >= sdo->size) ? 1 : 0;
    
    // 发送上传分段响应
    uint8_t response[8] = {(toggle << 4) | (n << 1) | c, 0, 0, 0, 0, 0, 0, 0};
    memcpy(&response[1], &sdo->buffer[sdo->offset], dataSize);
    CAN_Send(0x580 + nodeID, response, 8);
    
    sdo->offset += dataSize;
    sdo->toggle ^= 1;
    
    // 检查是否传输完成
    if (c) {
        sdo->state = SDO_STATE_IDLE;
    }
}

// 发送SDO中止
void SDO_SendAbort(SDO_Server_t* sdo, uint16_t index, uint8_t subIndex, uint32_t abortCode) {
    uint8_t response[8] = {
        0x80,  // CS: 中止传输
        index & 0xFF, index >> 8,
        subIndex,
        abortCode & 0xFF, (abortCode >> 8) & 0xFF,
        (abortCode >> 16) & 0xFF, (abortCode >> 24) & 0xFF
    };
    CAN_Send(0x580 + nodeID, response, 8);
    sdo->state = SDO_STATE_IDLE;
}
```


## 4. PDO通信服务

### 4.1 PDO通信概述

PDO（Process Data Object）是CANopen中用于实时过程数据交换的通信服务。它提供了高效、低延迟的数据传输机制，适用于周期性或事件驱动的数据通信。

**PDO特点**：
- **无连接**：广播式通信，无需确认
- **实时性**：低延迟，高优先级
- **高效性**：最多8字节数据，无协议开销
- **灵活映射**：通过对象字典配置数据映射
- **多种触发**：支持同步、异步、事件驱动

**PDO类型**：
- **TPDO（Transmit PDO）**：发送PDO，节点发送数据
- **RPDO（Receive PDO）**：接收PDO，节点接收数据

**PDO通信模型**：
```
节点A                          节点B
┌──────────┐                  ┌──────────┐
│  TPDO1   │──── 广播 ────→   │  RPDO1   │
│ COB-ID:  │                  │ COB-ID:  │
│ 0x180+A  │                  │ 0x180+A  │
└──────────┘                  └──────────┘

节点B                          节点A
┌──────────┐                  ┌──────────┐
│  TPDO1   │──── 广播 ────→   │  RPDO1   │
│ COB-ID:  │                  │ COB-ID:  │
│ 0x180+B  │                  │ 0x180+B  │
└──────────┘                  └──────────┘
```

### 4.2 PDO传输类型

PDO支持多种传输类型，通过通信参数对象（0x1400-0x1BFF）的传输类型字段配置：

| 传输类型值 | 名称 | 说明 |
|-----------|------|------|
| 0 | 同步（非循环） | 收到SYNC后，由应用触发发送 |
| 1-240 | 同步（循环） | 每N个SYNC周期发送一次 |
| 241-251 | 保留 | 未定义 |
| 252 | 同步RTR | 收到SYNC和RTR后发送 |
| 253 | 异步RTR | 收到RTR后发送 |
| 254 | 异步（事件驱动） | 事件发生时立即发送 |
| 255 | 设备配置文件特定 | 由设备配置文件定义 |

**传输类型示例**：

```c
// 传输类型定义
#define PDO_TRANS_TYPE_SYNC_ACYCLIC     0    // 同步非循环
#define PDO_TRANS_TYPE_SYNC_CYCLIC_1    1    // 每1个SYNC
#define PDO_TRANS_TYPE_SYNC_CYCLIC_2    2    // 每2个SYNC
#define PDO_TRANS_TYPE_SYNC_CYCLIC_240  240  // 每240个SYNC
#define PDO_TRANS_TYPE_SYNC_RTR         252  // 同步RTR
#define PDO_TRANS_TYPE_ASYNC_RTR        253  // 异步RTR
#define PDO_TRANS_TYPE_ASYNC_EVENT      254  // 异步事件驱动
#define PDO_TRANS_TYPE_DEVICE_PROFILE   255  // 设备配置文件特定

// 配置TPDO1为同步循环（每10个SYNC）
OD_TPDOCommunicationParameter[0].transmissionType = 10;

// 配置TPDO2为异步事件驱动
OD_TPDOCommunicationParameter[1].transmissionType = 254;
```

### 4.3 PDO映射配置

PDO映射定义了对象字典对象到PDO数据字段的映射关系。每个PDO最多可以映射8个对象，总数据长度不超过8字节。

**映射配置步骤**：

1. **禁用PDO**：设置COB-ID的有效位（bit 31）为1
2. **清除映射**：设置映射参数子索引0为0
3. **配置映射**：设置映射对象（子索引1-8）
4. **设置映射数量**：设置映射参数子索引0为映射对象数量
5. **启用PDO**：设置COB-ID的有效位（bit 31）为0

**映射配置示例**：

```c
// 示例：配置TPDO1映射
// 映射对象：
// - 0x6040 子索引0（控制字，16位）
// - 0x6060 子索引0（操作模式，8位）
// - 0x607A 子索引0（目标位置，32位）
// 总长度：16 + 8 + 32 = 56位 = 7字节

void ConfigureTPDO1Mapping(void) {
    uint32_t mapping[4];
    
    // 1. 禁用TPDO1
    OD_TPDOCommunicationParameter[0].COB_ID |= 0x80000000;
    
    // 2. 清除映射
    OD_TPDOMappingParameter[0].numberOfEntries = 0;
    
    // 3. 配置映射对象
    // 映射对象1：0x6040 子索引0，16位
    mapping[0] = (0x6040 << 16) | (0x00 << 8) | 16;
    OD_TPDOMappingParameter[0].mappedObject1 = mapping[0];
    
    // 映射对象2：0x6060 子索引0，8位
    mapping[1] = (0x6060 << 16) | (0x00 << 8) | 8;
    OD_TPDOMappingParameter[0].mappedObject2 = mapping[1];
    
    // 映射对象3：0x607A 子索引0，32位
    mapping[2] = (0x607A << 16) | (0x00 << 8) | 32;
    OD_TPDOMappingParameter[0].mappedObject3 = mapping[2];
    
    // 4. 设置映射数量
    OD_TPDOMappingParameter[0].numberOfEntries = 3;
    
    // 5. 启用TPDO1
    OD_TPDOCommunicationParameter[0].COB_ID &= ~0x80000000;
}

// PDO数据打包
void PackTPDO1Data(uint8_t* data) {
    uint16_t controlWord = OD_ControlWord;
    uint8_t operationMode = OD_OperationMode;
    uint32_t targetPosition = OD_TargetPosition;
    
    // 按映射顺序打包数据（小端序）
    data[0] = controlWord & 0xFF;
    data[1] = (controlWord >> 8) & 0xFF;
    data[2] = operationMode;
    data[3] = targetPosition & 0xFF;
    data[4] = (targetPosition >> 8) & 0xFF;
    data[5] = (targetPosition >> 16) & 0xFF;
    data[6] = (targetPosition >> 24) & 0xFF;
}

// PDO数据解包
void UnpackRPDO1Data(uint8_t* data) {
    uint16_t controlWord;
    uint8_t operationMode;
    uint32_t targetPosition;
    
    // 按映射顺序解包数据（小端序）
    controlWord = data[0] | (data[1] << 8);
    operationMode = data[2];
    targetPosition = data[3] | (data[4] << 8) | (data[5] << 16) | (data[6] << 24);
    
    // 写入对象字典
    OD_ControlWord = controlWord;
    OD_OperationMode = operationMode;
    OD_TargetPosition = targetPosition;
}
```

### 4.4 同步PDO

同步PDO使用SYNC对象作为同步时钟，确保多个节点的数据在同一时刻更新。

**SYNC对象**：
- COB-ID：0x080（默认）
- 数据长度：0字节（仅作为触发信号）
- 周期：由对象0x1006定义（微秒）

**同步PDO工作流程**：

```
时间轴：
    │
    ├─ SYNC ─┬─ 节点A发送TPDO1
    │        ├─ 节点B发送TPDO1
    │        └─ 节点C发送TPDO1
    │
    ├─ SYNC ─┬─ 节点A发送TPDO1
    │        ├─ 节点B发送TPDO1
    │        └─ 节点C发送TPDO1
    │
    └─ ...
```

**同步PDO实现**：

```c
// SYNC生产者（主站）
typedef struct {
    uint32_t period;         // SYNC周期（微秒）
    uint32_t counter;        // SYNC计数器
    uint32_t lastTime;       // 上次发送时间
} SYNC_Producer_t;

void SYNC_ProducerInit(SYNC_Producer_t* sync, uint32_t period) {
    sync->period = period;
    sync->counter = 0;
    sync->lastTime = GetMicroseconds();
}

void SYNC_ProducerProcess(SYNC_Producer_t* sync) {
    uint32_t currentTime = GetMicroseconds();
    
    if (currentTime - sync->lastTime >= sync->period) {
        // 发送SYNC对象
        uint8_t data[1] = {sync->counter & 0xFF};
        CAN_Send(0x080, data, (sync->counter > 0) ? 1 : 0);
        
        sync->counter++;
        if (sync->counter > 240) {
            sync->counter = 1;
        }
        
        sync->lastTime = currentTime;
    }
}

// SYNC消费者（从站）
typedef struct {
    uint8_t syncCounter;     // SYNC计数器
    uint8_t syncReceived;    // SYNC接收标志
} SYNC_Consumer_t;

void SYNC_ConsumerInit(SYNC_Consumer_t* sync) {
    sync->syncCounter = 0;
    sync->syncReceived = 0;
}

void SYNC_ConsumerReceive(SYNC_Consumer_t* sync, uint8_t* data, uint8_t len) {
    if (len > 0) {
        sync->syncCounter = data[0];
    } else {
        sync->syncCounter++;
        if (sync->syncCounter > 240) {
            sync->syncCounter = 1;
        }
    }
    
    sync->syncReceived = 1;
}

// 同步TPDO处理
void ProcessSyncTPDO(SYNC_Consumer_t* sync, PDO_t* pdo) {
    if (!sync->syncReceived) {
        return;
    }
    
    // 检查传输类型
    if (pdo->transmissionType == 0) {
        // 同步非循环：由应用触发
        if (pdo->sendRequest) {
            PDO_Send(pdo);
            pdo->sendRequest = 0;
        }
    } else if (pdo->transmissionType >= 1 && pdo->transmissionType <= 240) {
        // 同步循环：每N个SYNC发送
        if (sync->syncCounter % pdo->transmissionType == 0) {
            PDO_Send(pdo);
        }
    }
    
    sync->syncReceived = 0;
}
```

### 4.5 异步PDO

异步PDO不依赖SYNC对象，可以在事件发生时立即发送，提供更低的延迟。

**异步PDO特点**：
- **事件驱动**：数据变化时立即发送
- **低延迟**：无需等待SYNC
- **禁止时间**：防止发送过于频繁
- **事件定时器**：定期发送，即使数据未变化

**异步PDO实现**：

```c
// 异步TPDO处理
typedef struct {
    uint32_t COB_ID;         // COB-ID
    uint8_t transmissionType;// 传输类型
    uint16_t inhibitTime;    // 禁止时间（100微秒单位）
    uint16_t eventTimer;     // 事件定时器（毫秒）
    uint32_t lastSendTime;   // 上次发送时间
    uint32_t lastEventTime;  // 上次事件时间
    uint8_t dataChanged;     // 数据变化标志
    uint8_t data[8];         // PDO数据
    uint8_t dataLen;         // 数据长度
} AsyncTPDO_t;

void AsyncTPDO_Init(AsyncTPDO_t* pdo, uint32_t cobID, uint16_t inhibitTime, uint16_t eventTimer) {
    pdo->COB_ID = cobID;
    pdo->transmissionType = 254;  // 异步事件驱动
    pdo->inhibitTime = inhibitTime;
    pdo->eventTimer = eventTimer;
    pdo->lastSendTime = 0;
    pdo->lastEventTime = GetMicroseconds();
    pdo->dataChanged = 0;
    pdo->dataLen = 0;
}

void AsyncTPDO_SetData(AsyncTPDO_t* pdo, uint8_t* data, uint8_t len) {
    // 检查数据是否变化
    if (len != pdo->dataLen || memcmp(data, pdo->data, len) != 0) {
        memcpy(pdo->data, data, len);
        pdo->dataLen = len;
        pdo->dataChanged = 1;
    }
}

void AsyncTPDO_Process(AsyncTPDO_t* pdo) {
    uint32_t currentTime = GetMicroseconds();
    uint32_t timeSinceLastSend = currentTime - pdo->lastSendTime;
    uint32_t timeSinceLastEvent = (currentTime - pdo->lastEventTime) / 1000;  // 转换为毫秒
    
    // 检查是否需要发送
    bool shouldSend = false;
    
    // 条件1：数据变化且超过禁止时间
    if (pdo->dataChanged && timeSinceLastSend >= pdo->inhibitTime * 100) {
        shouldSend = true;
        pdo->dataChanged = 0;
    }
    
    // 条件2：事件定时器超时
    if (pdo->eventTimer > 0 && timeSinceLastEvent >= pdo->eventTimer) {
        shouldSend = true;
        pdo->lastEventTime = currentTime;
    }
    
    // 发送PDO
    if (shouldSend) {
        CAN_Send(pdo->COB_ID, pdo->data, pdo->dataLen);
        pdo->lastSendTime = currentTime;
    }
}

// 使用示例
AsyncTPDO_t tpdo1;

void Application_Init(void) {
    // 初始化TPDO1：禁止时间=10ms，事件定时器=100ms
    AsyncTPDO_Init(&tpdo1, 0x181, 100, 100);
}

void Application_Process(void) {
    // 更新PDO数据
    uint8_t data[8];
    PackTPDO1Data(data);
    AsyncTPDO_SetData(&tpdo1, data, 7);
    
    // 处理PDO发送
    AsyncTPDO_Process(&tpdo1);
}
```

### 4.6 PDO动态映射

PDO动态映射允许在运行时修改PDO映射配置，提供更大的灵活性。

**动态映射步骤**：

```c
// 通过SDO动态配置PDO映射
void DynamicConfigurePDO(uint8_t nodeID, uint8_t pdoNum) {
    // 1. 禁用PDO（设置COB-ID bit 31 = 1）
    uint16_t commIndex = 0x1800 + pdoNum - 1;  // TPDO通信参数索引
    uint32_t cobID;
    SDO_Upload(nodeID, commIndex, 1, &cobID, 4);
    cobID |= 0x80000000;
    SDO_Download(nodeID, commIndex, 1, &cobID, 4);
    
    // 2. 清除映射（设置子索引0 = 0）
    uint16_t mapIndex = 0x1A00 + pdoNum - 1;  // TPDO映射参数索引
    uint8_t numEntries = 0;
    SDO_Download(nodeID, mapIndex, 0, &numEntries, 1);
    
    // 3. 配置新映射
    uint32_t mapping1 = (0x6040 << 16) | (0x00 << 8) | 16;  // 控制字，16位
    SDO_Download(nodeID, mapIndex, 1, &mapping1, 4);
    
    uint32_t mapping2 = (0x6041 << 16) | (0x00 << 8) | 16;  // 状态字，16位
    SDO_Download(nodeID, mapIndex, 2, &mapping2, 4);
    
    // 4. 设置映射数量
    numEntries = 2;
    SDO_Download(nodeID, mapIndex, 0, &numEntries, 1);
    
    // 5. 启用PDO（设置COB-ID bit 31 = 0）
    cobID &= ~0x80000000;
    SDO_Download(nodeID, commIndex, 1, &cobID, 4);
}
```

### 4.7 PDO实现完整示例

```c
// PDO管理器
typedef struct {
    uint32_t COB_ID;         // COB-ID
    uint8_t transmissionType;// 传输类型
    uint16_t inhibitTime;    // 禁止时间
    uint16_t eventTimer;     // 事件定时器
    uint8_t numberOfMappings;// 映射数量
    uint32_t mappings[8];    // 映射对象
    uint8_t data[8];         // PDO数据缓冲区
    uint8_t dataLen;         // 数据长度
    uint32_t lastSendTime;   // 上次发送时间
    uint8_t enabled;         // 使能标志
} PDO_t;

// PDO初始化
void PDO_Init(PDO_t* pdo, uint16_t commIndex, uint16_t mapIndex) {
    // 读取通信参数
    OD_Entry_t* commEntry = OD_FindEntry(commIndex, 0);
    if (commEntry) {
        pdo->COB_ID = *(uint32_t*)OD_GetData(commIndex, 1);
        pdo->transmissionType = *(uint8_t*)OD_GetData(commIndex, 2);
        pdo->inhibitTime = *(uint16_t*)OD_GetData(commIndex, 3);
        pdo->eventTimer = *(uint16_t*)OD_GetData(commIndex, 5);
    }
    
    // 读取映射参数
    OD_Entry_t* mapEntry = OD_FindEntry(mapIndex, 0);
    if (mapEntry) {
        pdo->numberOfMappings = *(uint8_t*)OD_GetData(mapIndex, 0);
        for (uint8_t i = 0; i < pdo->numberOfMappings; i++) {
            pdo->mappings[i] = *(uint32_t*)OD_GetData(mapIndex, i + 1);
        }
    }
    
    // 计算PDO数据长度
    pdo->dataLen = 0;
    for (uint8_t i = 0; i < pdo->numberOfMappings; i++) {
        uint8_t bitLen = pdo->mappings[i] & 0xFF;
        pdo->dataLen += (bitLen + 7) / 8;
    }
    
    // 检查PDO是否使能
    pdo->enabled = !(pdo->COB_ID & 0x80000000);
    pdo->lastSendTime = 0;
}

// 打包TPDO数据
void PDO_PackData(PDO_t* pdo) {
    uint8_t bitOffset = 0;
    memset(pdo->data, 0, 8);
    
    for (uint8_t i = 0; i < pdo->numberOfMappings; i++) {
        uint32_t mapping = pdo->mappings[i];
        uint16_t index = (mapping >> 16) & 0xFFFF;
        uint8_t subIndex = (mapping >> 8) & 0xFF;
        uint8_t bitLen = mapping & 0xFF;
        uint8_t byteLen = (bitLen + 7) / 8;
        
        // 读取对象字典数据
        void* pData = OD_GetData(index, subIndex);
        if (pData) {
            // 复制数据到PDO缓冲区
            uint8_t byteOffset = bitOffset / 8;
            memcpy(&pdo->data[byteOffset], pData, byteLen);
            bitOffset += bitLen;
        }
    }
}

// 解包RPDO数据
void PDO_UnpackData(PDO_t* pdo, uint8_t* data) {
    uint8_t bitOffset = 0;
    
    for (uint8_t i = 0; i < pdo->numberOfMappings; i++) {
        uint32_t mapping = pdo->mappings[i];
        uint16_t index = (mapping >> 16) & 0xFFFF;
        uint8_t subIndex = (mapping >> 8) & 0xFF;
        uint8_t bitLen = mapping & 0xFF;
        uint8_t byteLen = (bitLen + 7) / 8;
        
        // 写入对象字典
        void* pData = OD_GetData(index, subIndex);
        if (pData) {
            uint8_t byteOffset = bitOffset / 8;
            memcpy(pData, &data[byteOffset], byteLen);
            bitOffset += bitLen;
        }
    }
}

// 发送TPDO
void PDO_Send(PDO_t* pdo) {
    if (!pdo->enabled) {
        return;
    }
    
    // 打包数据
    PDO_PackData(pdo);
    
    // 发送CAN帧
    CAN_Send(pdo->COB_ID & 0x7FF, pdo->data, pdo->dataLen);
    
    pdo->lastSendTime = GetMicroseconds();
}

// 接收RPDO
void PDO_Receive(PDO_t* pdo, uint8_t* data, uint8_t len) {
    if (!pdo->enabled) {
        return;
    }
    
    // 解包数据
    PDO_UnpackData(pdo, data);
}
```


## 5. 网络管理（NMT）

### 5.1 NMT服务概述

NMT（Network Management）服务用于管理CANopen网络中节点的状态和行为。它提供了节点状态控制、错误监控和网络同步等功能。

**NMT功能**：
- **节点状态控制**：初始化、启动、停止、复位
- **心跳监控**：监控节点在线状态
- **节点保护**：检测节点故障
- **启动管理**：协调节点启动顺序

**NMT通信模型**：
```
┌──────────────┐                    ┌──────────────┐
│  NMT主站     │                    │  NMT从站     │
│  (Master)    │                    │  (Slave)     │
├──────────────┤                    ├──────────────┤
│ 发送NMT命令  │──── NMT命令 ────→  │ 接收NMT命令  │
│ COB-ID: 0x000│                    │ 状态转换     │
│              │                    │              │
│ 接收心跳     │←─── 心跳消息 ────  │ 发送心跳     │
│              │  COB-ID: 0x700+N   │ COB-ID: 0x700+N│
└──────────────┘                    └──────────────┘
```

### 5.2 NMT命令

NMT命令使用COB-ID 0x000（最高优先级），数据长度为2字节：

```
┌────┬────┐
│Byte│ 0  │ 1  │
├────┼────┼────┤
│    │ CS │NodeID│
└────┴────┴────┘

CS: 命令说明符（Command Specifier）
NodeID: 目标节点ID（0=所有节点，1-127=特定节点）
```

**NMT命令类型**：

```c
// NMT命令说明符
#define NMT_CMD_START_REMOTE_NODE       0x01  // 启动远程节点
#define NMT_CMD_STOP_REMOTE_NODE        0x02  // 停止远程节点
#define NMT_CMD_ENTER_PRE_OPERATIONAL   0x80  // 进入预操作状态
#define NMT_CMD_RESET_NODE              0x81  // 复位节点
#define NMT_CMD_RESET_COMMUNICATION     0x82  // 复位通信

// NMT命令结构
typedef struct {
    uint8_t commandSpecifier;  // 命令说明符
    uint8_t nodeID;            // 节点ID
} NMT_Command_t;

// 发送NMT命令
void NMT_SendCommand(uint8_t cmd, uint8_t nodeID) {
    uint8_t data[2] = {cmd, nodeID};
    CAN_Send(0x000, data, 2);
}

// 使用示例
NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, 5);      // 启动节点5
NMT_SendCommand(NMT_CMD_STOP_REMOTE_NODE, 0);       // 停止所有节点
NMT_SendCommand(NMT_CMD_ENTER_PRE_OPERATIONAL, 3);  // 节点3进入预操作
NMT_SendCommand(NMT_CMD_RESET_NODE, 7);             // 复位节点7
```

### 5.3 NMT状态机实现

```c
// NMT状态定义
typedef enum {
    NMT_STATE_INITIALIZING = 0,      // 初始化状态
    NMT_STATE_PRE_OPERATIONAL = 127, // 预操作状态
    NMT_STATE_OPERATIONAL = 5,       // 操作状态
    NMT_STATE_STOPPED = 4            // 停止状态
} NMT_State_t;

// NMT管理器
typedef struct {
    NMT_State_t state;               // 当前状态
    uint8_t nodeID;                  // 节点ID
    void (*stateChangeCallback)(NMT_State_t oldState, NMT_State_t newState);
} NMT_Manager_t;

// NMT初始化
void NMT_Init(NMT_Manager_t* nmt, uint8_t nodeID) {
    nmt->state = NMT_STATE_INITIALIZING;
    nmt->nodeID = nodeID;
    nmt->stateChangeCallback = NULL;
    
    // 配置NMT接收过滤器
    CAN_SetFilter(0x000, 0x7FF);
    
    // 执行初始化
    // ...
    
    // 自动进入预操作状态
    NMT_ChangeState(nmt, NMT_STATE_PRE_OPERATIONAL);
}

// 状态转换
void NMT_ChangeState(NMT_Manager_t* nmt, NMT_State_t newState) {
    NMT_State_t oldState = nmt->state;
    
    if (oldState == newState) {
        return;
    }
    
    // 执行状态退出操作
    switch (oldState) {
        case NMT_STATE_OPERATIONAL:
            // 停止PDO通信
            PDO_StopAll();
            break;
        default:
            break;
    }
    
    // 更新状态
    nmt->state = newState;
    
    // 执行状态进入操作
    switch (newState) {
        case NMT_STATE_PRE_OPERATIONAL:
            // 允许SDO通信，禁止PDO通信
            SDO_Enable();
            PDO_DisableAll();
            break;
            
        case NMT_STATE_OPERATIONAL:
            // 允许SDO和PDO通信
            SDO_Enable();
            PDO_EnableAll();
            break;
            
        case NMT_STATE_STOPPED:
            // 禁止SDO和PDO通信
            SDO_Disable();
            PDO_DisableAll();
            break;
            
        default:
            break;
    }
    
    // 调用状态变化回调
    if (nmt->stateChangeCallback) {
        nmt->stateChangeCallback(oldState, newState);
    }
}

// 处理NMT命令
void NMT_ProcessCommand(NMT_Manager_t* nmt, uint8_t* data) {
    uint8_t cmd = data[0];
    uint8_t nodeID = data[1];
    
    // 检查命令是否针对本节点
    if (nodeID != 0 && nodeID != nmt->nodeID) {
        return;
    }
    
    // 执行命令
    switch (cmd) {
        case NMT_CMD_START_REMOTE_NODE:
            if (nmt->state == NMT_STATE_PRE_OPERATIONAL || 
                nmt->state == NMT_STATE_STOPPED) {
                NMT_ChangeState(nmt, NMT_STATE_OPERATIONAL);
            }
            break;
            
        case NMT_CMD_STOP_REMOTE_NODE:
            if (nmt->state == NMT_STATE_PRE_OPERATIONAL || 
                nmt->state == NMT_STATE_OPERATIONAL) {
                NMT_ChangeState(nmt, NMT_STATE_STOPPED);
            }
            break;
            
        case NMT_CMD_ENTER_PRE_OPERATIONAL:
            if (nmt->state == NMT_STATE_OPERATIONAL || 
                nmt->state == NMT_STATE_STOPPED) {
                NMT_ChangeState(nmt, NMT_STATE_PRE_OPERATIONAL);
            }
            break;
            
        case NMT_CMD_RESET_NODE:
            // 执行节点复位
            NVIC_SystemReset();
            break;
            
        case NMT_CMD_RESET_COMMUNICATION:
            // 复位通信参数
            NMT_ResetCommunication(nmt);
            NMT_ChangeState(nmt, NMT_STATE_PRE_OPERATIONAL);
            break;
            
        default:
            break;
    }
}

// 复位通信
void NMT_ResetCommunication(NMT_Manager_t* nmt) {
    // 重新初始化CAN控制器
    CAN_DeInit();
    CAN_Init();
    
    // 重新加载通信参数
    SDO_Init();
    PDO_InitAll();
    
    // 重新配置过滤器
    CAN_SetFilter(0x000, 0x7FF);  // NMT
    CAN_SetFilter(0x080, 0x7FF);  // SYNC
    CAN_SetFilter(0x080 + nmt->nodeID, 0x7FF);  // EMCY
    CAN_SetFilter(0x580 + nmt->nodeID, 0x7FF);  // SDO Tx
    CAN_SetFilter(0x600 + nmt->nodeID, 0x7FF);  // SDO Rx
    // ... 配置PDO过滤器
}
```

### 5.4 心跳机制

心跳（Heartbeat）是CANopen中用于监控节点在线状态的机制。每个节点定期发送心跳消息，主站监控心跳超时。

**心跳消息格式**：
```
COB-ID: 0x700 + NodeID
数据长度: 1字节
数据: 节点状态
```

**心跳生产者实现**：

```c
// 心跳生产者
typedef struct {
    uint8_t nodeID;              // 节点ID
    uint16_t period;             // 心跳周期（毫秒）
    uint32_t lastSendTime;       // 上次发送时间
    NMT_State_t state;           // 节点状态
} Heartbeat_Producer_t;

void Heartbeat_ProducerInit(Heartbeat_Producer_t* hb, uint8_t nodeID, uint16_t period) {
    hb->nodeID = nodeID;
    hb->period = period;
    hb->lastSendTime = GetMilliseconds();
    hb->state = NMT_STATE_PRE_OPERATIONAL;
}

void Heartbeat_ProducerProcess(Heartbeat_Producer_t* hb, NMT_State_t currentState) {
    if (hb->period == 0) {
        return;  // 心跳未使能
    }
    
    uint32_t currentTime = GetMilliseconds();
    
    if (currentTime - hb->lastSendTime >= hb->period) {
        // 发送心跳消息
        uint8_t data[1] = {currentState};
        CAN_Send(0x700 + hb->nodeID, data, 1);
        
        hb->lastSendTime = currentTime;
        hb->state = currentState;
    }
}
```

**心跳消费者实现**：

```c
// 心跳消费者
typedef struct {
    uint8_t nodeID;              // 监控的节点ID
    uint16_t timeout;            // 心跳超时时间（毫秒）
    uint32_t lastReceiveTime;    // 上次接收时间
    NMT_State_t state;           // 节点状态
    uint8_t isAlive;             // 节点在线标志
    void (*timeoutCallback)(uint8_t nodeID);
} Heartbeat_Consumer_t;

void Heartbeat_ConsumerInit(Heartbeat_Consumer_t* hb, uint8_t nodeID, uint16_t timeout) {
    hb->nodeID = nodeID;
    hb->timeout = timeout;
    hb->lastReceiveTime = GetMilliseconds();
    hb->state = NMT_STATE_INITIALIZING;
    hb->isAlive = 0;
    hb->timeoutCallback = NULL;
    
    // 配置心跳接收过滤器
    CAN_SetFilter(0x700 + nodeID, 0x7FF);
}

void Heartbeat_ConsumerReceive(Heartbeat_Consumer_t* hb, uint8_t* data) {
    hb->state = (NMT_State_t)data[0];
    hb->lastReceiveTime = GetMilliseconds();
    hb->isAlive = 1;
}

void Heartbeat_ConsumerProcess(Heartbeat_Consumer_t* hb) {
    if (hb->timeout == 0) {
        return;  // 心跳监控未使能
    }
    
    uint32_t currentTime = GetMilliseconds();
    
    if (hb->isAlive && (currentTime - hb->lastReceiveTime > hb->timeout)) {
        // 心跳超时
        hb->isAlive = 0;
        
        // 调用超时回调
        if (hb->timeoutCallback) {
            hb->timeoutCallback(hb->nodeID);
        }
    }
}

// 心跳管理器（监控多个节点）
#define MAX_HEARTBEAT_CONSUMERS 16

typedef struct {
    Heartbeat_Consumer_t consumers[MAX_HEARTBEAT_CONSUMERS];
    uint8_t numConsumers;
} Heartbeat_Manager_t;

void Heartbeat_ManagerInit(Heartbeat_Manager_t* mgr) {
    mgr->numConsumers = 0;
    
    // 从对象字典读取消费者心跳配置（0x1016）
    uint8_t numEntries = *(uint8_t*)OD_GetData(0x1016, 0);
    
    for (uint8_t i = 0; i < numEntries && i < MAX_HEARTBEAT_CONSUMERS; i++) {
        uint32_t config = *(uint32_t*)OD_GetData(0x1016, i + 1);
        uint8_t nodeID = (config >> 16) & 0x7F;
        uint16_t timeout = config & 0xFFFF;
        
        if (nodeID > 0 && timeout > 0) {
            Heartbeat_ConsumerInit(&mgr->consumers[mgr->numConsumers], nodeID, timeout);
            mgr->numConsumers++;
        }
    }
}

void Heartbeat_ManagerProcess(Heartbeat_Manager_t* mgr) {
    for (uint8_t i = 0; i < mgr->numConsumers; i++) {
        Heartbeat_ConsumerProcess(&mgr->consumers[i]);
    }
}

void Heartbeat_ManagerReceive(Heartbeat_Manager_t* mgr, uint32_t cobID, uint8_t* data) {
    uint8_t nodeID = cobID - 0x700;
    
    for (uint8_t i = 0; i < mgr->numConsumers; i++) {
        if (mgr->consumers[i].nodeID == nodeID) {
            Heartbeat_ConsumerReceive(&mgr->consumers[i], data);
            break;
        }
    }
}
```

### 5.5 节点保护（Node Guarding）

节点保护是CANopen早期版本的节点监控机制，现已被心跳机制取代，但仍在一些旧系统中使用。

**节点保护原理**：
- 主站定期发送RTR（Remote Transmission Request）到从站
- 从站响应包含状态信息的消息
- 主站检测响应超时

**节点保护实现**：

```c
// 节点保护配置
typedef struct {
    uint16_t guardTime;          // 保护时间（毫秒）
    uint8_t lifeTimeFactor;      // 生命周期因子
    uint8_t toggle;              // 切换位
    uint32_t lastGuardTime;      // 上次保护时间
} NodeGuarding_t;

void NodeGuarding_Init(NodeGuarding_t* ng) {
    // 从对象字典读取配置
    ng->guardTime = *(uint16_t*)OD_GetData(0x100C, 0);
    ng->lifeTimeFactor = *(uint8_t*)OD_GetData(0x100D, 0);
    ng->toggle = 0;
    ng->lastGuardTime = GetMilliseconds();
}

void NodeGuarding_ProcessRTR(NodeGuarding_t* ng, NMT_State_t state, uint8_t nodeID) {
    // 响应节点保护RTR
    uint8_t data[1] = {state | (ng->toggle << 7)};
    CAN_Send(0x700 + nodeID, data, 1);
    
    // 切换位翻转
    ng->toggle ^= 1;
    ng->lastGuardTime = GetMilliseconds();
}

void NodeGuarding_CheckTimeout(NodeGuarding_t* ng) {
    if (ng->guardTime == 0 || ng->lifeTimeFactor == 0) {
        return;  // 节点保护未使能
    }
    
    uint32_t timeout = ng->guardTime * ng->lifeTimeFactor;
    uint32_t currentTime = GetMilliseconds();
    
    if (currentTime - ng->lastGuardTime > timeout) {
        // 节点保护超时，触发生命周期事件
        // 可以发送EMCY消息或进入错误状态
    }
}
```

### 5.6 启动管理

启动管理用于协调多个节点的启动顺序，确保网络按预定顺序初始化。

**启动流程**：

```c
// 主站启动管理
void Master_StartupSequence(void) {
    // 1. 复位所有节点通信
    NMT_SendCommand(NMT_CMD_RESET_COMMUNICATION, 0);
    Delay_ms(100);
    
    // 2. 等待所有节点进入预操作状态
    Delay_ms(500);
    
    // 3. 配置从站参数（通过SDO）
    for (uint8_t nodeID = 1; nodeID <= 10; nodeID++) {
        // 配置心跳周期
        uint16_t heartbeatTime = 1000;
        SDO_Download(nodeID, 0x1017, 0, &heartbeatTime, 2);
        
        // 配置PDO映射
        ConfigurePDOMapping(nodeID);
        
        Delay_ms(50);
    }
    
    // 4. 启动所有节点
    NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, 0);
    
    // 5. 开始心跳监控
    Heartbeat_ManagerInit(&heartbeatManager);
}

// 从站启动流程
void Slave_StartupSequence(uint8_t nodeID) {
    // 1. 硬件初始化
    HAL_Init();
    SystemClock_Config();
    CAN_Init();
    
    // 2. 加载对象字典
    OD_Init();
    
    // 3. 初始化CANopen协议栈
    NMT_Init(&nmtManager, nodeID);
    SDO_ServerInit(&sdoServer, nodeID);
    PDO_InitAll();
    
    // 4. 进入预操作状态
    NMT_ChangeState(&nmtManager, NMT_STATE_PRE_OPERATIONAL);
    
    // 5. 等待主站配置和启动命令
    while (nmtManager.state != NMT_STATE_OPERATIONAL) {
        CANopen_Process();
        Delay_ms(10);
    }
    
    // 6. 开始正常运行
    Application_Run();
}
```


## 6. 紧急对象（EMCY）

### 6.1 EMCY概述

EMCY（Emergency）对象用于报告设备内部错误和异常情况。它提供了高优先级的错误通知机制，使主站能够及时响应设备故障。

**EMCY特点**：
- **高优先级**：COB-ID 0x080 + NodeID
- **异步传输**：错误发生时立即发送
- **错误代码**：标准化的错误分类
- **错误寄存器**：反映当前错误状态
- **禁止时间**：防止错误消息过于频繁

**EMCY消息格式**：
```
COB-ID: 0x080 + NodeID
数据长度: 8字节

┌────┬────┬────┬────┬────┬────┬────┬────┐
│Byte│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│    │Error Code │ ER │ Manufacturer Specific │
│    │  (16bit)  │    │      (5 bytes)        │
└────┴────┴────┴────┴────┴────┴────┴────┘

Error Code: 错误代码（16位，小端序）
ER: 错误寄存器（8位）
Manufacturer Specific: 厂商特定数据（5字节）
```

### 6.2 标准错误代码

CANopen定义了标准化的错误代码分类：

```c
// 错误代码定义
#define EMCY_NO_ERROR                   0x0000  // 无错误（错误恢复）

// 通用错误（0x10xx）
#define EMCY_GENERIC_ERROR              0x1000  // 通用错误
#define EMCY_CURRENT_GENERIC            0x2000  // 电流通用错误
#define EMCY_CURRENT_INPUT              0x2100  // 输入电流错误
#define EMCY_CURRENT_INSIDE             0x2200  // 内部电流错误
#define EMCY_CURRENT_OUTPUT             0x2300  // 输出电流错误

// 电压错误（0x30xx）
#define EMCY_VOLTAGE_GENERIC            0x3000  // 电压通用错误
#define EMCY_VOLTAGE_MAINS              0x3100  // 主电源电压错误
#define EMCY_VOLTAGE_INSIDE             0x3200  // 内部电压错误
#define EMCY_VOLTAGE_OUTPUT             0x3300  // 输出电压错误

// 温度错误（0x40xx）
#define EMCY_TEMPERATURE_GENERIC        0x4000  // 温度通用错误
#define EMCY_TEMPERATURE_AMBIENT        0x4100  // 环境温度错误
#define EMCY_TEMPERATURE_DEVICE         0x4200  // 设备温度错误

// 硬件错误（0x50xx）
#define EMCY_HARDWARE_GENERIC           0x5000  // 硬件通用错误

// 软件错误（0x60xx）
#define EMCY_SOFTWARE_GENERIC           0x6000  // 软件通用错误
#define EMCY_SOFTWARE_INTERNAL          0x6100  // 内部软件错误
#define EMCY_SOFTWARE_USER              0x6200  // 用户软件错误
#define EMCY_SOFTWARE_DATA_SET          0x6300  // 数据集错误

// 附加模块错误（0x70xx）
#define EMCY_ADDITIONAL_MODULES         0x7000  // 附加模块错误

// 监控错误（0x80xx）
#define EMCY_MONITORING_GENERIC         0x8000  // 监控通用错误
#define EMCY_MONITORING_COMMUNICATION   0x8100  // 通信监控错误
#define EMCY_MONITORING_PROTOCOL        0x8200  // 协议错误

// 外部错误（0x90xx）
#define EMCY_EXTERNAL_ERROR             0x9000  // 外部错误

// 附加功能错误（0xF0xx）
#define EMCY_ADDITIONAL_FUNCTIONS       0xF000  // 附加功能错误

// 设备特定错误（0xFFxx）
#define EMCY_DEVICE_SPECIFIC            0xFF00  // 设备特定错误
```

### 6.3 错误寄存器

错误寄存器（0x1001）是一个8位值，反映设备当前的错误状态：

```c
// 错误寄存器位定义
#define ERROR_REG_GENERIC               0x01  // Bit 0: 通用错误
#define ERROR_REG_CURRENT               0x02  // Bit 1: 电流错误
#define ERROR_REG_VOLTAGE               0x04  // Bit 2: 电压错误
#define ERROR_REG_TEMPERATURE           0x08  // Bit 3: 温度错误
#define ERROR_REG_COMMUNICATION         0x10  // Bit 4: 通信错误
#define ERROR_REG_DEVICE_PROFILE        0x20  // Bit 5: 设备配置文件特定错误
#define ERROR_REG_RESERVED              0x40  // Bit 6: 保留
#define ERROR_REG_MANUFACTURER          0x80  // Bit 7: 厂商特定错误

// 错误寄存器操作
uint8_t OD_ErrorRegister = 0x00;

void ErrorRegister_Set(uint8_t errorBit) {
    OD_ErrorRegister |= errorBit;
}

void ErrorRegister_Clear(uint8_t errorBit) {
    OD_ErrorRegister &= ~errorBit;
}

uint8_t ErrorRegister_Get(void) {
    return OD_ErrorRegister;
}
```

### 6.4 EMCY实现

```c
// EMCY管理器
typedef struct {
    uint8_t nodeID;              // 节点ID
    uint16_t inhibitTime;        // 禁止时间（100微秒单位）
    uint32_t lastSendTime;       // 上次发送时间
    uint16_t errorHistory[8];    // 错误历史（对象0x1003）
    uint8_t errorCount;          // 错误数量
} EMCY_Manager_t;

// EMCY初始化
void EMCY_Init(EMCY_Manager_t* emcy, uint8_t nodeID) {
    emcy->nodeID = nodeID;
    emcy->inhibitTime = *(uint16_t*)OD_GetData(0x1015, 0);
    emcy->lastSendTime = 0;
    emcy->errorCount = 0;
    memset(emcy->errorHistory, 0, sizeof(emcy->errorHistory));
}

// 发送EMCY消息
void EMCY_Send(EMCY_Manager_t* emcy, uint16_t errorCode, uint8_t* mfrData) {
    // 检查禁止时间
    uint32_t currentTime = GetMicroseconds();
    if (currentTime - emcy->lastSendTime < emcy->inhibitTime * 100) {
        return;  // 在禁止时间内，不发送
    }
    
    // 构造EMCY消息
    uint8_t data[8];
    data[0] = errorCode & 0xFF;
    data[1] = (errorCode >> 8) & 0xFF;
    data[2] = OD_ErrorRegister;
    
    if (mfrData) {
        memcpy(&data[3], mfrData, 5);
    } else {
        memset(&data[3], 0, 5);
    }
    
    // 发送EMCY消息
    CAN_Send(0x080 + emcy->nodeID, data, 8);
    
    emcy->lastSendTime = currentTime;
    
    // 更新错误历史（对象0x1003）
    if (errorCode != EMCY_NO_ERROR) {
        // 移动错误历史
        for (int i = 7; i > 0; i--) {
            emcy->errorHistory[i] = emcy->errorHistory[i-1];
        }
        emcy->errorHistory[0] = errorCode;
        
        if (emcy->errorCount < 8) {
            emcy->errorCount++;
        }
        
        // 更新对象字典
        *(uint8_t*)OD_GetData(0x1003, 0) = emcy->errorCount;
    }
}

// 报告错误
void EMCY_ReportError(EMCY_Manager_t* emcy, uint16_t errorCode, uint8_t errorRegBit, uint8_t* mfrData) {
    // 设置错误寄存器
    ErrorRegister_Set(errorRegBit);
    
    // 发送EMCY消息
    EMCY_Send(emcy, errorCode, mfrData);
}

// 清除错误
void EMCY_ClearError(EMCY_Manager_t* emcy, uint8_t errorRegBit) {
    // 清除错误寄存器
    ErrorRegister_Clear(errorRegBit);
    
    // 如果所有错误都已清除，发送错误恢复消息
    if (OD_ErrorRegister == 0) {
        EMCY_Send(emcy, EMCY_NO_ERROR, NULL);
    }
}

// 使用示例
void Application_ErrorHandling(void) {
    // 检测过流错误
    if (GetCurrent() > MAX_CURRENT) {
        uint8_t mfrData[5] = {0};
        uint32_t current = GetCurrent();
        memcpy(mfrData, &current, 4);
        
        EMCY_ReportError(&emcyManager, EMCY_CURRENT_OUTPUT, 
                        ERROR_REG_CURRENT, mfrData);
    }
    
    // 检测过温错误
    if (GetTemperature() > MAX_TEMPERATURE) {
        uint8_t mfrData[5] = {0};
        uint16_t temp = GetTemperature();
        memcpy(mfrData, &temp, 2);
        
        EMCY_ReportError(&emcyManager, EMCY_TEMPERATURE_DEVICE, 
                        ERROR_REG_TEMPERATURE, mfrData);
    }
    
    // 检测通信错误
    if (CAN_GetErrorCount() > 100) {
        EMCY_ReportError(&emcyManager, EMCY_MONITORING_COMMUNICATION, 
                        ERROR_REG_COMMUNICATION, NULL);
    }
}
```

### 6.5 EMCY接收和处理

主站需要接收和处理从站发送的EMCY消息：

```c
// EMCY消费者
typedef struct {
    uint8_t nodeID;              // 节点ID
    uint16_t lastErrorCode;      // 最后错误代码
    uint8_t lastErrorReg;        // 最后错误寄存器
    uint32_t errorCount;         // 错误计数
    void (*errorCallback)(uint8_t nodeID, uint16_t errorCode, uint8_t errorReg);
} EMCY_Consumer_t;

// EMCY消费者初始化
void EMCY_ConsumerInit(EMCY_Consumer_t* consumer, uint8_t nodeID) {
    consumer->nodeID = nodeID;
    consumer->lastErrorCode = 0;
    consumer->lastErrorReg = 0;
    consumer->errorCount = 0;
    consumer->errorCallback = NULL;
    
    // 配置EMCY接收过滤器
    CAN_SetFilter(0x080 + nodeID, 0x7FF);
}

// EMCY消息接收
void EMCY_ConsumerReceive(EMCY_Consumer_t* consumer, uint8_t* data) {
    uint16_t errorCode = data[0] | (data[1] << 8);
    uint8_t errorReg = data[2];
    uint8_t mfrData[5];
    memcpy(mfrData, &data[3], 5);
    
    consumer->lastErrorCode = errorCode;
    consumer->lastErrorReg = errorReg;
    
    if (errorCode != EMCY_NO_ERROR) {
        consumer->errorCount++;
    }
    
    // 调用错误回调
    if (consumer->errorCallback) {
        consumer->errorCallback(consumer->nodeID, errorCode, errorReg);
    }
    
    // 记录错误日志
    printf("EMCY from Node %d: ErrorCode=0x%04X, ErrorReg=0x%02X\n", 
           consumer->nodeID, errorCode, errorReg);
}

// 错误处理回调示例
void Master_ErrorCallback(uint8_t nodeID, uint16_t errorCode, uint8_t errorReg) {
    switch (errorCode) {
        case EMCY_NO_ERROR:
            printf("Node %d: Error cleared\n", nodeID);
            break;
            
        case EMCY_CURRENT_OUTPUT:
            printf("Node %d: Output current error\n", nodeID);
            // 采取纠正措施
            NMT_SendCommand(NMT_CMD_STOP_REMOTE_NODE, nodeID);
            break;
            
        case EMCY_TEMPERATURE_DEVICE:
            printf("Node %d: Device temperature error\n", nodeID);
            // 采取纠正措施
            break;
            
        case EMCY_MONITORING_COMMUNICATION:
            printf("Node %d: Communication error\n", nodeID);
            // 尝试重新初始化通信
            NMT_SendCommand(NMT_CMD_RESET_COMMUNICATION, nodeID);
            break;
            
        default:
            printf("Node %d: Unknown error 0x%04X\n", nodeID, errorCode);
            break;
    }
}
```

## 7. 时间戳对象（TIME）

### 7.1 TIME概述

TIME对象用于在CANopen网络中提供时间同步服务。它允许所有节点共享统一的时间基准，用于事件时间标记和数据记录。

**TIME特点**：
- **COB-ID**：0x100（默认）
- **数据长度**：6字节
- **时间格式**：CANopen时间格式（自1984年1月1日午夜的毫秒数）
- **广播传输**：由时间生产者定期发送

**TIME消息格式**：
```
COB-ID: 0x100
数据长度: 6字节

┌────┬────┬────┬────┬────┬────┬────┐
│Byte│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │
├────┼────┼────┼────┼────┼────┼────┤
│    │  Time of Day (28bit)  │Days│
│    │      (milliseconds)    │    │
└────┴────┴────┴────┴────┴────┴────┘

Time of Day: 当天时间（毫秒，0-86399999）
Days: 自1984年1月1日的天数（16位）
```

### 7.2 TIME实现

```c
// TIME生产者
typedef struct {
    uint32_t period;             // TIME发送周期（毫秒）
    uint32_t lastSendTime;       // 上次发送时间
    uint32_t timeOfDay;          // 当天时间（毫秒）
    uint16_t days;               // 天数
} TIME_Producer_t;

void TIME_ProducerInit(TIME_Producer_t* time, uint32_t period) {
    time->period = period;
    time->lastSendTime = GetMilliseconds();
    time->timeOfDay = 0;
    time->days = 0;
}

void TIME_ProducerProcess(TIME_Producer_t* time) {
    uint32_t currentTime = GetMilliseconds();
    
    if (currentTime - time->lastSendTime >= time->period) {
        // 构造TIME消息
        uint8_t data[6];
        uint32_t timeOfDay = time->timeOfDay & 0x0FFFFFFF;
        
        data[0] = timeOfDay & 0xFF;
        data[1] = (timeOfDay >> 8) & 0xFF;
        data[2] = (timeOfDay >> 16) & 0xFF;
        data[3] = (timeOfDay >> 24) & 0x0F;
        data[4] = time->days & 0xFF;
        data[5] = (time->days >> 8) & 0xFF;
        
        // 发送TIME消息
        CAN_Send(0x100, data, 6);
        
        time->lastSendTime = currentTime;
        
        // 更新时间
        time->timeOfDay += time->period;
        if (time->timeOfDay >= 86400000) {  // 24小时 = 86400000毫秒
            time->timeOfDay -= 86400000;
            time->days++;
        }
    }
}

// TIME消费者
typedef struct {
    uint32_t timeOfDay;          // 当天时间（毫秒）
    uint16_t days;               // 天数
    uint8_t synchronized;        // 同步标志
} TIME_Consumer_t;

void TIME_ConsumerInit(TIME_Consumer_t* time) {
    time->timeOfDay = 0;
    time->days = 0;
    time->synchronized = 0;
}

void TIME_ConsumerReceive(TIME_Consumer_t* time, uint8_t* data) {
    // 解析TIME消息
    time->timeOfDay = data[0] | (data[1] << 8) | (data[2] << 16) | ((data[3] & 0x0F) << 24);
    time->days = data[4] | (data[5] << 8);
    time->synchronized = 1;
}

// 时间转换函数
typedef struct {
    uint16_t year;
    uint8_t month;
    uint8_t day;
    uint8_t hour;
    uint8_t minute;
    uint8_t second;
    uint16_t millisecond;
} DateTime_t;

void TIME_ToDateTime(uint32_t timeOfDay, uint16_t days, DateTime_t* dt) {
    // 计算日期（从1984年1月1日开始）
    uint32_t totalDays = days;
    dt->year = 1984;
    
    while (1) {
        uint16_t daysInYear = (dt->year % 4 == 0 && (dt->year % 100 != 0 || dt->year % 400 == 0)) ? 366 : 365;
        if (totalDays < daysInYear) {
            break;
        }
        totalDays -= daysInYear;
        dt->year++;
    }
    
    // 计算月份和日期
    uint8_t daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (dt->year % 4 == 0 && (dt->year % 100 != 0 || dt->year % 400 == 0)) {
        daysInMonth[1] = 29;  // 闰年
    }
    
    dt->month = 1;
    for (int i = 0; i < 12; i++) {
        if (totalDays < daysInMonth[i]) {
            break;
        }
        totalDays -= daysInMonth[i];
        dt->month++;
    }
    dt->day = totalDays + 1;
    
    // 计算时间
    dt->millisecond = timeOfDay % 1000;
    uint32_t totalSeconds = timeOfDay / 1000;
    dt->second = totalSeconds % 60;
    totalSeconds /= 60;
    dt->minute = totalSeconds % 60;
    dt->hour = totalSeconds / 60;
}
```


## 8. CANopen协议栈集成

### 8.1 CANopenNode协议栈

CANopenNode是一个开源的CANopen协议栈实现，支持多种微控制器平台。

**CANopenNode特点**：
- 完整的CANopen实现（CiA 301）
- 支持SDO、PDO、NMT、EMCY、SYNC、TIME
- 模块化设计，易于移植
- 支持多种设备配置文件
- MIT许可证

**目录结构**：
```
CANopenNode/
├── stack/              # 协议栈核心代码
│   ├── CO_SDO.c/h     # SDO实现
│   ├── CO_PDO.c/h     # PDO实现
│   ├── CO_NMT_Heartbeat.c/h  # NMT和心跳
│   ├── CO_SYNC.c/h    # SYNC实现
│   ├── CO_Emergency.c/h  # EMCY实现
│   └── CO_OD.c/h      # 对象字典
├── example/           # 示例代码
├── doc/               # 文档
└── CANopen.c/h        # 主接口
```

### 8.2 STM32平台移植

**硬件配置**：

```c
// CAN初始化（STM32 HAL库）
void CAN_Init(void) {
    CAN_HandleTypeDef hcan1;
    
    // CAN外设时钟使能
    __HAL_RCC_CAN1_CLK_ENABLE();
    
    // GPIO配置
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_11 | GPIO_PIN_12;  // PA11=RX, PA12=TX
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF9_CAN1;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // CAN参数配置
    hcan1.Instance = CAN1;
    hcan1.Init.Prescaler = 6;              // 波特率分频
    hcan1.Init.Mode = CAN_MODE_NORMAL;     // 正常模式
    hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;
    hcan1.Init.TimeSeg1 = CAN_BS1_13TQ;
    hcan1.Init.TimeSeg2 = CAN_BS2_2TQ;
    hcan1.Init.TimeTriggeredMode = DISABLE;
    hcan1.Init.AutoBusOff = ENABLE;
    hcan1.Init.AutoWakeUp = DISABLE;
    hcan1.Init.AutoRetransmission = ENABLE;
    hcan1.Init.ReceiveFifoLocked = DISABLE;
    hcan1.Init.TransmitFifoPriority = DISABLE;
    
    if (HAL_CAN_Init(&hcan1) != HAL_OK) {
        Error_Handler();
    }
    
    // 配置过滤器
    CAN_FilterTypeDef sFilterConfig;
    sFilterConfig.FilterBank = 0;
    sFilterConfig.FilterMode = CAN_FILTERMODE_IDMASK;
    sFilterConfig.FilterScale = CAN_FILTERSCALE_32BIT;
    sFilterConfig.FilterIdHigh = 0x0000;
    sFilterConfig.FilterIdLow = 0x0000;
    sFilterConfig.FilterMaskIdHigh = 0x0000;
    sFilterConfig.FilterMaskIdLow = 0x0000;
    sFilterConfig.FilterFIFOAssignment = CAN_RX_FIFO0;
    sFilterConfig.FilterActivation = ENABLE;
    sFilterConfig.SlaveStartFilterBank = 14;
    
    if (HAL_CAN_ConfigFilter(&hcan1, &sFilterConfig) != HAL_OK) {
        Error_Handler();
    }
    
    // 启动CAN
    if (HAL_CAN_Start(&hcan1) != HAL_OK) {
        Error_Handler();
    }
    
    // 使能接收中断
    if (HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING) != HAL_OK) {
        Error_Handler();
    }
}

// CAN发送函数
bool CAN_Send(uint32_t cobID, uint8_t* data, uint8_t len) {
    CAN_TxHeaderTypeDef TxHeader;
    uint32_t TxMailbox;
    
    TxHeader.StdId = cobID;
    TxHeader.ExtId = 0;
    TxHeader.RTR = CAN_RTR_DATA;
    TxHeader.IDE = CAN_ID_STD;
    TxHeader.DLC = len;
    TxHeader.TransmitGlobalTime = DISABLE;
    
    if (HAL_CAN_AddTxMessage(&hcan1, &TxHeader, data, &TxMailbox) != HAL_OK) {
        return false;
    }
    
    return true;
}

// CAN接收中断回调
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef RxHeader;
    uint8_t RxData[8];
    
    if (HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &RxHeader, RxData) == HAL_OK) {
        // 调用CANopen接收处理
        CANopen_ProcessReceive(RxHeader.StdId, RxData, RxHeader.DLC);
    }
}
```

**CANopenNode集成**：

```c
#include "CANopen.h"

// CANopen对象
CO_t *CO = NULL;

// 初始化CANopen
void CANopen_Init(uint8_t nodeID) {
    CO_ReturnError_t err;
    
    // 分配CANopen对象
    CO = CO_new(NULL, NULL);
    if (CO == NULL) {
        Error_Handler();
    }
    
    // 初始化CANopen
    err = CO_CANinit(CO, NULL, 500);  // 500kbps
    if (err != CO_ERROR_NO) {
        Error_Handler();
    }
    
    // 初始化CANopen节点
    err = CO_CANopenInit(CO,
                         NULL,           // 备用位时序
                         NULL,           // 备用对象字典
                         NULL,           // 备用存储
                         NMT_CONTROL_RESET_NODE,
                         1000,           // 首次HB时间
                         nodeID);        // 节点ID
    
    if (err != CO_ERROR_NO && err != CO_ERROR_NODE_ID_UNCONFIGURED_LSS) {
        Error_Handler();
    }
    
    // 配置回调函数
    CO_EM_initCallbackPre(CO->em, EmergencyCallback);
    
    // 启动CANopen
    CO_CANopenInitPDO(CO, CO->em, OD, nodeID, &err);
    
    // 进入预操作状态
    CO_NMT_sendCommand(CO->NMT, CO_NMT_ENTER_PRE_OPERATIONAL, nodeID);
}

// CANopen主循环
void CANopen_Process(void) {
    CO_NMT_reset_cmd_t reset = CO_RESET_NOT;
    uint32_t timeDifference_us = 1000;  // 1ms
    
    // 处理CANopen
    reset = CO_process(CO, false, timeDifference_us, NULL);
    
    // 处理复位命令
    if (reset == CO_RESET_COMM) {
        // 复位通信
        CO_CANopenInit(CO, NULL, NULL, NULL, NMT_CONTROL_RESET_COMMUNICATION, 
                      1000, CO->NMT->nodeId);
    } else if (reset == CO_RESET_APP) {
        // 复位应用
        NVIC_SystemReset();
    }
}

// 紧急消息回调
void EmergencyCallback(const uint16_t ident, const uint16_t errorCode, 
                       const uint8_t errorRegister, const uint8_t errorBit, 
                       const uint32_t infoCode) {
    printf("EMCY: ErrorCode=0x%04X, ErrorReg=0x%02X\n", errorCode, errorRegister);
}
```

### 8.3 对象字典生成

使用CANopen Magic或其他EDS编辑器创建对象字典：

**EDS文件示例**：
```ini
[DeviceInfo]
VendorName=MyCompany
ProductName=CANopen Device
OrderCode=
VendorNumber=0x00000000
ProductNumber=0x00000000
RevisionNumber=0x00010001
SerialNumber=12345
BaudRate_10=1
BaudRate_20=1
BaudRate_50=1
BaudRate_125=1
BaudRate_250=1
BaudRate_500=1
BaudRate_800=1
BaudRate_1000=1
SimpleBootUpMaster=0
SimpleBootUpSlave=1
Granularity=8
GroupMessaging=0
CompactPDO=0
LSS_Supported=1

[DummyUsage]
Dummy0001=0
Dummy0002=0
Dummy0003=0
Dummy0004=0
Dummy0005=1
Dummy0006=1
Dummy0007=1

[MandatoryObjects]
SupportedObjects=3
1=0x1000
2=0x1001
3=0x1018

[1000]
ParameterName=Device type
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=0x00000000
PDOMapping=0

[1001]
ParameterName=Error register
ObjectType=0x7
DataType=0x0005
AccessType=ro
DefaultValue=0
PDOMapping=1

[1018]
ParameterName=Identity
ObjectType=0x9
SubNumber=5

[1018sub0]
ParameterName=Number of entries
ObjectType=0x7
DataType=0x0005
AccessType=ro
DefaultValue=4
PDOMapping=0

[1018sub1]
ParameterName=Vendor ID
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=0x00000000
PDOMapping=0

[1018sub2]
ParameterName=Product code
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=0x00000000
PDOMapping=0

[1018sub3]
ParameterName=Revision number
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=0x00010001
PDOMapping=0

[1018sub4]
ParameterName=Serial number
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=12345
PDOMapping=0
```

**从EDS生成C代码**：

使用CANopenNode的objdictgen工具：
```bash
python objdictgen.py device.eds OD.c OD.h
```

生成的对象字典代码：
```c
// OD.h
#ifndef OD_H
#define OD_H

#include "CO_ODinterface.h"

// 对象字典条目数量
#define OD_CNT_NMT 1
#define OD_CNT_EM 1
#define OD_CNT_SYNC 1
#define OD_CNT_EM_PROD 1
#define OD_CNT_HB_CONS 0
#define OD_CNT_HB_PROD 1
#define OD_CNT_SDO_SRV 1
#define OD_CNT_SDO_CLI 0
#define OD_CNT_RPDO 4
#define OD_CNT_TPDO 4

// 对象字典索引
#define OD_H1000_DEV_TYPE                   0x1000
#define OD_H1001_ERR_REG                    0x1001
#define OD_H1002_MANUF_STATUS_REG           0x1002
#define OD_H1003_PRE_DEF_ERR_FIELD          0x1003
#define OD_H1005_COB_ID_SYNC                0x1005
#define OD_H1006_COMM_CYCL_PERIOD           0x1006
#define OD_H1007_SYNC_WINDOW_LEN            0x1007
#define OD_H1008_MANUF_DEV_NAME             0x1008
#define OD_H1009_MANUF_HW_VERSION           0x1009
#define OD_H100A_MANUF_SW_VERSION           0x100A
#define OD_H1010_STORE_PARAM                0x1010
#define OD_H1011_REST_PARAM                 0x1011
#define OD_H1014_COB_ID_EMCY                0x1014
#define OD_H1015_INHIBIT_TIME_EMCY          0x1015
#define OD_H1016_CONSUMER_HB_TIME           0x1016
#define OD_H1017_PRODUCER_HB_TIME           0x1017
#define OD_H1018_IDENTITY_OBJECT            0x1018
#define OD_H1200_SDO_SERVER_PARAM           0x1200
#define OD_H1400_RXPDO_1_PARAM              0x1400
#define OD_H1401_RXPDO_2_PARAM              0x1401
#define OD_H1402_RXPDO_3_PARAM              0x1402
#define OD_H1403_RXPDO_4_PARAM              0x1403
#define OD_H1600_RXPDO_1_MAPPING            0x1600
#define OD_H1601_RXPDO_2_MAPPING            0x1601
#define OD_H1602_RXPDO_3_MAPPING            0x1602
#define OD_H1603_RXPDO_4_MAPPING            0x1603
#define OD_H1800_TXPDO_1_PARAM              0x1800
#define OD_H1801_TXPDO_2_PARAM              0x1801
#define OD_H1802_TXPDO_3_PARAM              0x1802
#define OD_H1803_TXPDO_4_PARAM              0x1803
#define OD_H1A00_TXPDO_1_MAPPING            0x1A00
#define OD_H1A01_TXPDO_2_MAPPING            0x1A01
#define OD_H1A02_TXPDO_3_MAPPING            0x1A02
#define OD_H1A03_TXPDO_4_MAPPING            0x1A03

// 应用对象
#define OD_H6000_READ_INPUT_8BIT            0x6000
#define OD_H6200_WRITE_OUTPUT_8BIT          0x6200
#define OD_H6401_READ_ANALOG_INPUT          0x6401
#define OD_H6411_WRITE_ANALOG_OUTPUT        0x6411

// 对象字典结构
extern OD_t *OD;

// 对象字典初始化
OD_t *OD_create(void);
void OD_delete(OD_t *od);

#endif // OD_H
```

### 8.4 完整应用示例

```c
// main.c
#include "stm32f4xx_hal.h"
#include "CANopen.h"
#include "OD.h"

// 全局变量
CO_t *CO = NULL;
uint8_t nodeID = 5;
uint16_t heartbeatTime = 1000;  // 1秒

// 应用变量（映射到对象字典）
uint8_t digitalInputs = 0;      // 0x6000
uint8_t digitalOutputs = 0;     // 0x6200
uint16_t analogInput = 0;       // 0x6401
uint16_t analogOutput = 0;      // 0x6411

int main(void) {
    // HAL初始化
    HAL_Init();
    SystemClock_Config();
    
    // 外设初始化
    GPIO_Init();
    ADC_Init();
    DAC_Init();
    CAN_Init();
    
    // CANopen初始化
    CANopen_Init(nodeID);
    
    // 主循环
    while (1) {
        // 处理CANopen
        CANopen_Process();
        
        // 应用逻辑
        Application_Process();
        
        // 延时
        HAL_Delay(1);
    }
}

// 应用处理
void Application_Process(void) {
    // 读取数字输入
    digitalInputs = 0;
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0)) digitalInputs |= 0x01;
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_1)) digitalInputs |= 0x02;
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_2)) digitalInputs |= 0x04;
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_3)) digitalInputs |= 0x08;
    
    // 写入数字输出
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, (digitalOutputs & 0x01) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, (digitalOutputs & 0x02) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, (digitalOutputs & 0x04) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, (digitalOutputs & 0x08) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    
    // 读取模拟输入
    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        analogInput = HAL_ADC_GetValue(&hadc1);
    }
    HAL_ADC_Stop(&hadc1);
    
    // 写入模拟输出
    HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, analogOutput);
}

// 系统时钟配置
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
    
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }
    
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
    
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}

// 错误处理
void Error_Handler(void) {
    __disable_irq();
    while (1) {
        // 错误指示（LED闪烁）
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        HAL_Delay(100);
    }
}
```


## 9. 设备配置文件（Device Profiles）

### 9.1 设备配置文件概述

设备配置文件（Device Profile）定义了特定类型设备的标准化对象字典和行为规范。它确保不同厂商的同类设备具有互操作性。

**常见设备配置文件**：

| CiA编号 | 名称 | 应用 |
|---------|------|------|
| CiA 401 | I/O模块 | 数字/模拟输入输出 |
| CiA 402 | 驱动和运动控制 | 伺服驱动、步进电机 |
| CiA 404 | 测量设备和闭环控制器 | 传感器、PID控制器 |
| CiA 405 | IEC 61131-3可编程控制器 | PLC |
| CiA 406 | 编码器 | 旋转编码器、线性编码器 |
| CiA 410 | 倾角传感器 | 倾斜角度测量 |
| CiA 413 | 卡车网关 | 车载网络网关 |
| CiA 417 | 升降平台 | 液压升降系统 |
| CiA 418 | 电池模块 | 电池管理系统 |
| CiA 443 | 接口模块 | 通信接口转换 |

### 9.2 CiA 402驱动和运动控制配置文件

CiA 402是最常用的设备配置文件之一，用于伺服驱动器和运动控制器。

**核心对象**：

```c
// 控制字（0x6040）
#define CONTROLWORD_SWITCH_ON           0x0001  // Bit 0: 开关使能
#define CONTROLWORD_ENABLE_VOLTAGE      0x0002  // Bit 1: 电压使能
#define CONTROLWORD_QUICK_STOP          0x0004  // Bit 2: 快速停止
#define CONTROLWORD_ENABLE_OPERATION    0x0008  // Bit 3: 操作使能
#define CONTROLWORD_NEW_SETPOINT        0x0010  // Bit 4: 新设定点
#define CONTROLWORD_CHANGE_SET_IMM      0x0020  // Bit 5: 立即改变设定
#define CONTROLWORD_ABS_REL             0x0040  // Bit 6: 绝对/相对
#define CONTROLWORD_FAULT_RESET         0x0080  // Bit 7: 故障复位
#define CONTROLWORD_HALT                0x0100  // Bit 8: 暂停

// 状态字（0x6041）
#define STATUSWORD_READY_TO_SWITCH_ON   0x0001  // Bit 0: 准备开关
#define STATUSWORD_SWITCHED_ON          0x0002  // Bit 1: 已开关
#define STATUSWORD_OPERATION_ENABLED    0x0004  // Bit 2: 操作使能
#define STATUSWORD_FAULT                0x0008  // Bit 3: 故障
#define STATUSWORD_VOLTAGE_ENABLED      0x0010  // Bit 4: 电压使能
#define STATUSWORD_QUICK_STOP           0x0020  // Bit 5: 快速停止
#define STATUSWORD_SWITCH_ON_DISABLED   0x0040  // Bit 6: 开关禁用
#define STATUSWORD_WARNING              0x0080  // Bit 7: 警告
#define STATUSWORD_REMOTE               0x0200  // Bit 9: 远程
#define STATUSWORD_TARGET_REACHED       0x0400  // Bit 10: 目标到达
#define STATUSWORD_INTERNAL_LIMIT       0x0800  // Bit 11: 内部限位

// 操作模式（0x6060）
#define OPMODE_NO_MODE                  0       // 无模式
#define OPMODE_PROFILE_POSITION         1       // 位置模式
#define OPMODE_VELOCITY                 2       // 速度模式
#define OPMODE_PROFILE_VELOCITY         3       // 速度轮廓模式
#define OPMODE_PROFILE_TORQUE           4       // 转矩轮廓模式
#define OPMODE_HOMING                   6       // 回零模式
#define OPMODE_INTERPOLATED_POSITION    7       // 插补位置模式
#define OPMODE_CYCLIC_SYNC_POSITION     8       // 循环同步位置模式
#define OPMODE_CYCLIC_SYNC_VELOCITY     9       // 循环同步速度模式
#define OPMODE_CYCLIC_SYNC_TORQUE       10      // 循环同步转矩模式

// 位置控制对象
#define OD_TARGET_POSITION              0x607A  // 目标位置
#define OD_POSITION_RANGE_LIMIT         0x607B  // 位置范围限制
#define OD_HOME_OFFSET                  0x607C  // 回零偏移
#define OD_SOFTWARE_POSITION_LIMIT      0x607D  // 软件位置限位
#define OD_POLARITY                     0x607E  // 极性
#define OD_MAX_PROFILE_VELOCITY         0x607F  // 最大轮廓速度
#define OD_PROFILE_VELOCITY             0x6081  // 轮廓速度
#define OD_END_VELOCITY                 0x6082  // 结束速度
#define OD_PROFILE_ACCELERATION         0x6083  // 轮廓加速度
#define OD_PROFILE_DECELERATION         0x6084  // 轮廓减速度
#define OD_QUICK_STOP_DECELERATION      0x6085  // 快速停止减速度
#define OD_MOTION_PROFILE_TYPE          0x6086  // 运动轮廓类型
#define OD_POSITION_ACTUAL_VALUE        0x6064  // 实际位置值
#define OD_POSITION_DEMAND_VALUE        0x6062  // 位置需求值
#define OD_FOLLOWING_ERROR_ACTUAL       0x60F4  // 实际跟随误差
#define OD_FOLLOWING_ERROR_WINDOW       0x6065  // 跟随误差窗口
#define OD_FOLLOWING_ERROR_TIMEOUT      0x6066  // 跟随误差超时

// 速度控制对象
#define OD_TARGET_VELOCITY              0x60FF  // 目标速度
#define OD_VELOCITY_SENSOR_ACTUAL       0x6069  // 速度传感器实际值
#define OD_VELOCITY_DEMAND_VALUE        0x606B  // 速度需求值
#define OD_VELOCITY_ACTUAL_VALUE        0x606C  // 实际速度值
#define OD_VELOCITY_WINDOW              0x606D  // 速度窗口
#define OD_VELOCITY_WINDOW_TIME         0x606E  // 速度窗口时间
#define OD_VELOCITY_THRESHOLD           0x6070  // 速度阈值
#define OD_VELOCITY_THRESHOLD_TIME      0x6071  // 速度阈值时间

// 转矩控制对象
#define OD_TARGET_TORQUE                0x6071  // 目标转矩
#define OD_MAX_TORQUE                   0x6072  // 最大转矩
#define OD_MAX_CURRENT                  0x6073  // 最大电流
#define OD_TORQUE_DEMAND_VALUE          0x6074  // 转矩需求值
#define OD_MOTOR_RATED_CURRENT          0x6075  // 电机额定电流
#define OD_MOTOR_RATED_TORQUE           0x6076  // 电机额定转矩
#define OD_TORQUE_ACTUAL_VALUE          0x6077  // 实际转矩值
#define OD_CURRENT_ACTUAL_VALUE         0x6078  // 实际电流值
```

**CiA 402状态机**：

```c
// CiA 402状态定义
typedef enum {
    DS402_STATE_NOT_READY_TO_SWITCH_ON = 0,
    DS402_STATE_SWITCH_ON_DISABLED,
    DS402_STATE_READY_TO_SWITCH_ON,
    DS402_STATE_SWITCHED_ON,
    DS402_STATE_OPERATION_ENABLED,
    DS402_STATE_QUICK_STOP_ACTIVE,
    DS402_STATE_FAULT_REACTION_ACTIVE,
    DS402_STATE_FAULT
} DS402_State_t;

// 状态机实现
typedef struct {
    DS402_State_t state;
    uint16_t controlWord;
    uint16_t statusWord;
    int8_t operationMode;
    int32_t targetPosition;
    int32_t actualPosition;
    int32_t targetVelocity;
    int32_t actualVelocity;
    int16_t targetTorque;
    int16_t actualTorque;
} DS402_Drive_t;

// 获取当前状态
DS402_State_t DS402_GetState(uint16_t statusWord) {
    uint16_t mask = statusWord & 0x006F;
    
    if ((mask & 0x004F) == 0x0000) {
        return DS402_STATE_NOT_READY_TO_SWITCH_ON;
    } else if ((mask & 0x004F) == 0x0040) {
        return DS402_STATE_SWITCH_ON_DISABLED;
    } else if ((mask & 0x006F) == 0x0021) {
        return DS402_STATE_READY_TO_SWITCH_ON;
    } else if ((mask & 0x006F) == 0x0023) {
        return DS402_STATE_SWITCHED_ON;
    } else if ((mask & 0x006F) == 0x0027) {
        return DS402_STATE_OPERATION_ENABLED;
    } else if ((mask & 0x006F) == 0x0007) {
        return DS402_STATE_QUICK_STOP_ACTIVE;
    } else if ((mask & 0x004F) == 0x000F) {
        return DS402_STATE_FAULT_REACTION_ACTIVE;
    } else if ((mask & 0x004F) == 0x0008) {
        return DS402_STATE_FAULT;
    }
    
    return DS402_STATE_NOT_READY_TO_SWITCH_ON;
}

// 状态转换
void DS402_StateMachine(DS402_Drive_t* drive) {
    drive->state = DS402_GetState(drive->statusWord);
    
    switch (drive->state) {
        case DS402_STATE_NOT_READY_TO_SWITCH_ON:
            // 自动转换到SWITCH_ON_DISABLED
            drive->statusWord = 0x0040;
            break;
            
        case DS402_STATE_SWITCH_ON_DISABLED:
            // 等待Shutdown命令
            if ((drive->controlWord & 0x0087) == 0x0006) {
                drive->statusWord = 0x0021;  // READY_TO_SWITCH_ON
            }
            break;
            
        case DS402_STATE_READY_TO_SWITCH_ON:
            // 等待Switch On命令
            if ((drive->controlWord & 0x0087) == 0x0007) {
                drive->statusWord = 0x0023;  // SWITCHED_ON
            } else if ((drive->controlWord & 0x0087) == 0x0000) {
                drive->statusWord = 0x0040;  // SWITCH_ON_DISABLED
            }
            break;
            
        case DS402_STATE_SWITCHED_ON:
            // 等待Enable Operation命令
            if ((drive->controlWord & 0x008F) == 0x000F) {
                drive->statusWord = 0x0027;  // OPERATION_ENABLED
            } else if ((drive->controlWord & 0x0087) == 0x0006) {
                drive->statusWord = 0x0021;  // READY_TO_SWITCH_ON
            } else if ((drive->controlWord & 0x0087) == 0x0000) {
                drive->statusWord = 0x0040;  // SWITCH_ON_DISABLED
            }
            break;
            
        case DS402_STATE_OPERATION_ENABLED:
            // 正常运行状态
            if ((drive->controlWord & 0x008F) == 0x0007) {
                drive->statusWord = 0x0023;  // SWITCHED_ON
            } else if ((drive->controlWord & 0x008F) == 0x0002) {
                drive->statusWord = 0x0007;  // QUICK_STOP_ACTIVE
            } else if ((drive->controlWord & 0x0087) == 0x0006) {
                drive->statusWord = 0x0021;  // READY_TO_SWITCH_ON
            } else if ((drive->controlWord & 0x0087) == 0x0000) {
                drive->statusWord = 0x0040;  // SWITCH_ON_DISABLED
            }
            
            // 执行运动控制
            DS402_ExecuteMotion(drive);
            break;
            
        case DS402_STATE_QUICK_STOP_ACTIVE:
            // 快速停止
            if ((drive->controlWord & 0x0087) == 0x0000) {
                drive->statusWord = 0x0040;  // SWITCH_ON_DISABLED
            }
            break;
            
        case DS402_STATE_FAULT:
            // 故障状态，等待Fault Reset
            if ((drive->controlWord & 0x0080) == 0x0080) {
                drive->statusWord = 0x0040;  // SWITCH_ON_DISABLED
            }
            break;
            
        default:
            break;
    }
}

// 执行运动控制
void DS402_ExecuteMotion(DS402_Drive_t* drive) {
    switch (drive->operationMode) {
        case OPMODE_PROFILE_POSITION:
            // 位置模式
            DS402_ProfilePositionMode(drive);
            break;
            
        case OPMODE_PROFILE_VELOCITY:
            // 速度模式
            DS402_ProfileVelocityMode(drive);
            break;
            
        case OPMODE_PROFILE_TORQUE:
            // 转矩模式
            DS402_ProfileTorqueMode(drive);
            break;
            
        case OPMODE_HOMING:
            // 回零模式
            DS402_HomingMode(drive);
            break;
            
        default:
            break;
    }
}

// 位置模式实现
void DS402_ProfilePositionMode(DS402_Drive_t* drive) {
    // 检查新设定点
    if (drive->controlWord & CONTROLWORD_NEW_SETPOINT) {
        // 开始位置运动
        int32_t error = drive->targetPosition - drive->actualPosition;
        
        // 简化的位置控制（实际应用中需要使用轮廓生成器）
        if (error > 0) {
            drive->actualPosition += 100;  // 增量
        } else if (error < 0) {
            drive->actualPosition -= 100;  // 减量
        }
        
        // 检查是否到达目标
        if (abs(error) < 10) {
            drive->statusWord |= STATUSWORD_TARGET_REACHED;
        } else {
            drive->statusWord &= ~STATUSWORD_TARGET_REACHED;
        }
    }
}

// 速度模式实现
void DS402_ProfileVelocityMode(DS402_Drive_t* drive) {
    // 速度控制
    drive->actualVelocity = drive->targetVelocity;
    
    // 更新位置
    drive->actualPosition += drive->actualVelocity / 1000;  // 假设1ms周期
}

// 转矩模式实现
void DS402_ProfileTorqueMode(DS402_Drive_t* drive) {
    // 转矩控制
    drive->actualTorque = drive->targetTorque;
}

// 回零模式实现
void DS402_HomingMode(DS402_Drive_t* drive) {
    // 回零逻辑
    // 1. 寻找回零开关
    // 2. 移动到回零位置
    // 3. 设置位置为0
    
    if (/* 回零完成 */ 0) {
        drive->actualPosition = 0;
        drive->statusWord |= STATUSWORD_TARGET_REACHED;
    }
}
```

### 9.3 CiA 401 I/O模块配置文件

CiA 401定义了通用I/O模块的标准对象：

```c
// 数字输入（0x6000）
#define OD_READ_INPUT_8BIT              0x6000  // 8位数字输入
#define OD_READ_INPUT_16BIT             0x6020  // 16位数字输入
#define OD_READ_INPUT_32BIT             0x6030  // 32位数字输入

// 数字输出（0x6200）
#define OD_WRITE_OUTPUT_8BIT            0x6200  // 8位数字输出
#define OD_WRITE_OUTPUT_16BIT           0x6220  // 16位数字输出
#define OD_WRITE_OUTPUT_32BIT           0x6230  // 32位数字输出

// 模拟输入（0x6401）
#define OD_READ_ANALOG_INPUT            0x6401  // 模拟输入值
#define OD_ANALOG_INPUT_INTERRUPT       0x6402  // 模拟输入中断
#define OD_ANALOG_INPUT_GLOBAL_INT      0x6403  // 全局中断使能
#define OD_ANALOG_INPUT_INT_UPPER_LIMIT 0x6404  // 中断上限
#define OD_ANALOG_INPUT_INT_LOWER_LIMIT 0x6405  // 中断下限
#define OD_ANALOG_INPUT_INT_DELTA       0x6406  // 中断增量
#define OD_ANALOG_INPUT_OFFSET          0x6410  // 模拟输入偏移
#define OD_ANALOG_INPUT_SCALING         0x6411  // 模拟输入缩放

// 模拟输出（0x6411）
#define OD_WRITE_ANALOG_OUTPUT          0x6411  // 模拟输出值
#define OD_ANALOG_OUTPUT_OFFSET         0x6420  // 模拟输出偏移
#define OD_ANALOG_OUTPUT_SCALING        0x6421  // 模拟输出缩放
#define OD_ANALOG_OUTPUT_ERROR_MODE     0x6422  // 错误模式
#define OD_ANALOG_OUTPUT_ERROR_VALUE    0x6423  // 错误值

// CiA 401 I/O模块实现
typedef struct {
    uint8_t digitalInput8[8];    // 8位数字输入
    uint8_t digitalOutput8[8];   // 8位数字输出
    int16_t analogInput[8];      // 模拟输入
    int16_t analogOutput[8];     // 模拟输出
} CiA401_IO_t;

void CiA401_ProcessIO(CiA401_IO_t* io) {
    // 读取数字输入
    for (int i = 0; i < 8; i++) {
        io->digitalInput8[i] = GPIO_ReadInput(i);
    }
    
    // 写入数字输出
    for (int i = 0; i < 8; i++) {
        GPIO_WriteOutput(i, io->digitalOutput8[i]);
    }
    
    // 读取模拟输入
    for (int i = 0; i < 8; i++) {
        io->analogInput[i] = ADC_Read(i);
    }
    
    // 写入模拟输出
    for (int i = 0; i < 8; i++) {
        DAC_Write(i, io->analogOutput[i]);
    }
}
```


## 10. 调试与故障排除

### 10.1 调试工具

**CAN分析仪**：
- PCAN-USB：Peak System的USB-CAN适配器
- USBCAN：Kvaser的USB-CAN接口
- CANalyzer：Vector的专业CAN分析软件
- Wireshark：开源协议分析工具（支持SocketCAN）

**CANopen配置工具**：
- CANopen Magic：EDS编辑和网络配置
- CANopen DeviceDesigner：设备配置文件开发
- CANopen Conformance Test Tool：一致性测试

### 10.2 常见问题诊断

**问题1：节点无法进入操作状态**

症状：
- 节点停留在预操作状态
- 无法接收/发送PDO

诊断步骤：
```c
// 1. 检查NMT状态
uint8_t nmtState = CO->NMT->operatingState;
printf("NMT State: %d\n", nmtState);

// 2. 检查错误寄存器
uint8_t errorReg = OD_ErrorRegister;
printf("Error Register: 0x%02X\n", errorReg);

// 3. 检查错误历史
uint8_t errorCount = *(uint8_t*)OD_GetData(0x1003, 0);
for (int i = 0; i < errorCount; i++) {
    uint32_t errorCode = *(uint32_t*)OD_GetData(0x1003, i + 1);
    printf("Error %d: 0x%08X\n", i, errorCode);
}

// 4. 发送NMT启动命令
NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, nodeID);
```

解决方案：
- 检查PDO映射配置是否正确
- 确认所有必需的对象字典条目已配置
- 检查CAN总线连接和终端电阻
- 验证波特率设置是否匹配

**问题2：SDO通信超时**

症状：
- SDO请求无响应
- SDO中止代码0x05040000（超时）

诊断步骤：
```c
// 1. 检查节点是否在线
bool isAlive = Heartbeat_IsAlive(nodeID);
printf("Node %d alive: %d\n", nodeID, isAlive);

// 2. 检查SDO COB-ID配置
uint32_t sdoRxCobID = *(uint32_t*)OD_GetData(0x1200, 1);
uint32_t sdoTxCobID = *(uint32_t*)OD_GetData(0x1200, 2);
printf("SDO Rx COB-ID: 0x%03X\n", sdoRxCobID);
printf("SDO Tx COB-ID: 0x%03X\n", sdoTxCobID);

// 3. 监控CAN总线流量
CAN_Monitor_Enable();
```

解决方案：
- 增加SDO超时时间
- 检查节点ID是否正确
- 验证SDO服务器是否已初始化
- 检查CAN总线负载是否过高

**问题3：PDO数据不更新**

症状：
- PDO消息发送但数据不变
- 接收PDO但对象字典未更新

诊断步骤：
```c
// 1. 检查PDO使能状态
uint32_t pdoCobID = *(uint32_t*)OD_GetData(0x1800, 1);  // TPDO1
bool pdoEnabled = !(pdoCobID & 0x80000000);
printf("PDO Enabled: %d\n", pdoEnabled);

// 2. 检查PDO映射
uint8_t numMappings = *(uint8_t*)OD_GetData(0x1A00, 0);  // TPDO1映射
printf("Number of mappings: %d\n", numMappings);

for (int i = 0; i < numMappings; i++) {
    uint32_t mapping = *(uint32_t*)OD_GetData(0x1A00, i + 1);
    uint16_t index = (mapping >> 16) & 0xFFFF;
    uint8_t subIndex = (mapping >> 8) & 0xFF;
    uint8_t bitLen = mapping & 0xFF;
    printf("Mapping %d: 0x%04X:%02X (%d bits)\n", i, index, subIndex, bitLen);
}

// 3. 检查传输类型
uint8_t transType = *(uint8_t*)OD_GetData(0x1800, 2);
printf("Transmission Type: %d\n", transType);

// 4. 手动触发PDO发送
PDO_Send(&tpdo1);
```

解决方案：
- 验证PDO映射配置正确
- 检查传输类型设置（同步/异步）
- 确认SYNC消息正常发送（同步PDO）
- 检查禁止时间和事件定时器设置

**问题4：心跳超时**

症状：
- 主站报告从站心跳超时
- 从站无法检测到主站

诊断步骤：
```c
// 1. 检查心跳生产者配置
uint16_t producerTime = *(uint16_t*)OD_GetData(0x1017, 0);
printf("Producer Heartbeat Time: %d ms\n", producerTime);

// 2. 检查心跳消费者配置
uint8_t numConsumers = *(uint8_t*)OD_GetData(0x1016, 0);
for (int i = 0; i < numConsumers; i++) {
    uint32_t config = *(uint32_t*)OD_GetData(0x1016, i + 1);
    uint8_t nodeID = (config >> 16) & 0x7F;
    uint16_t timeout = config & 0xFFFF;
    printf("Consumer %d: Node %d, Timeout %d ms\n", i, nodeID, timeout);
}

// 3. 监控心跳消息
void CAN_MonitorHeartbeat(uint32_t cobID, uint8_t* data) {
    if (cobID >= 0x700 && cobID <= 0x77F) {
        uint8_t nodeID = cobID - 0x700;
        uint8_t state = data[0];
        printf("Heartbeat from Node %d: State %d\n", nodeID, state);
    }
}
```

解决方案：
- 确认心跳周期配置合理（通常1000ms）
- 检查心跳超时时间是否足够（建议3倍周期）
- 验证节点ID配置正确
- 检查CAN总线稳定性

**问题5：EMCY消息频繁发送**

症状：
- 大量EMCY消息占用总线带宽
- 相同错误重复报告

诊断步骤：
```c
// 1. 检查EMCY禁止时间
uint16_t inhibitTime = *(uint16_t*)OD_GetData(0x1015, 0);
printf("EMCY Inhibit Time: %d * 100us\n", inhibitTime);

// 2. 分析错误代码
void EMCY_Analyze(uint16_t errorCode, uint8_t errorReg) {
    printf("Error Code: 0x%04X\n", errorCode);
    printf("Error Register: 0x%02X\n", errorReg);
    
    if (errorReg & ERROR_REG_GENERIC) printf("  - Generic Error\n");
    if (errorReg & ERROR_REG_CURRENT) printf("  - Current Error\n");
    if (errorReg & ERROR_REG_VOLTAGE) printf("  - Voltage Error\n");
    if (errorReg & ERROR_REG_TEMPERATURE) printf("  - Temperature Error\n");
    if (errorReg & ERROR_REG_COMMUNICATION) printf("  - Communication Error\n");
}

// 3. 检查错误源
void CheckErrorSources(void) {
    if (GetCurrent() > MAX_CURRENT) {
        printf("Overcurrent detected\n");
    }
    if (GetVoltage() > MAX_VOLTAGE) {
        printf("Overvoltage detected\n");
    }
    if (GetTemperature() > MAX_TEMPERATURE) {
        printf("Overtemperature detected\n");
    }
}
```

解决方案：
- 增加EMCY禁止时间（如100 = 10ms）
- 修复根本错误原因
- 实现错误去抖动逻辑
- 使用错误计数器避免频繁报告

### 10.3 性能优化

**优化1：减少SDO通信延迟**

```c
// 使用块传输（Block Transfer）代替分段传输
void SDO_BlockDownload(uint8_t nodeID, uint16_t index, uint8_t subIndex, 
                       uint8_t* data, uint32_t size) {
    // 块传输可以显著提高大数据传输效率
    // 每个块包含多个分段，减少确认次数
}

// 批量配置参数
void BatchConfigureParameters(uint8_t nodeID) {
    // 进入预操作状态
    NMT_SendCommand(NMT_CMD_ENTER_PRE_OPERATIONAL, nodeID);
    
    // 批量写入参数（无需等待每个响应）
    SDO_Download_Async(nodeID, 0x1017, 0, &heartbeatTime, 2);
    SDO_Download_Async(nodeID, 0x6081, 0, &profileVelocity, 4);
    SDO_Download_Async(nodeID, 0x6083, 0, &profileAccel, 4);
    
    // 等待所有SDO完成
    SDO_WaitAllComplete();
    
    // 启动节点
    NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, nodeID);
}
```

**优化2：PDO映射优化**

```c
// 合并多个小对象到一个PDO
void OptimizePDOMapping(void) {
    // 不好的映射：每个对象一个PDO
    // TPDO1: 控制字（2字节）
    // TPDO2: 操作模式（1字节）
    // TPDO3: 目标位置（4字节）
    
    // 优化的映射：合并到一个PDO
    // TPDO1: 控制字（2字节）+ 操作模式（1字节）+ 目标位置（4字节）= 7字节
    
    uint32_t mapping[3];
    mapping[0] = (0x6040 << 16) | (0x00 << 8) | 16;  // 控制字
    mapping[1] = (0x6060 << 16) | (0x00 << 8) | 8;   // 操作模式
    mapping[2] = (0x607A << 16) | (0x00 << 8) | 32;  // 目标位置
    
    ConfigureTPDOMapping(1, mapping, 3);
}

// 使用同步PDO提高实时性
void ConfigureSyncPDO(void) {
    // 设置SYNC周期
    uint32_t syncPeriod = 1000;  // 1ms
    SDO_Download(nodeID, 0x1006, 0, &syncPeriod, 4);
    
    // 配置PDO为同步传输
    uint8_t transType = 1;  // 每个SYNC发送
    SDO_Download(nodeID, 0x1800, 2, &transType, 1);
}
```

**优化3：减少CPU负载**

```c
// 使用DMA传输CAN数据
void CAN_DMA_Init(void) {
    // 配置DMA用于CAN接收
    // 减少中断频率和CPU占用
}

// 优化对象字典查找
typedef struct {
    uint16_t index;
    uint8_t subIndex;
    OD_Entry_t* entry;
} OD_Cache_t;

OD_Cache_t odCache[32];
uint8_t cacheSize = 0;

OD_Entry_t* OD_FindEntry_Cached(uint16_t index, uint8_t subIndex) {
    // 先查找缓存
    for (int i = 0; i < cacheSize; i++) {
        if (odCache[i].index == index && odCache[i].subIndex == subIndex) {
            return odCache[i].entry;
        }
    }
    
    // 缓存未命中，查找对象字典
    OD_Entry_t* entry = OD_FindEntry(index, subIndex);
    
    // 添加到缓存
    if (entry && cacheSize < 32) {
        odCache[cacheSize].index = index;
        odCache[cacheSize].subIndex = subIndex;
        odCache[cacheSize].entry = entry;
        cacheSize++;
    }
    
    return entry;
}
```

### 10.4 测试方法

**单元测试**：

```c
// SDO测试
void Test_SDO_Download(void) {
    uint16_t testValue = 1234;
    
    // 写入测试值
    SDO_Download(nodeID, 0x1017, 0, &testValue, 2);
    
    // 读回验证
    uint16_t readValue;
    SDO_Upload(nodeID, 0x1017, 0, &readValue, 2);
    
    assert(readValue == testValue);
}

// PDO测试
void Test_PDO_Communication(void) {
    // 配置TPDO
    ConfigureTPDOMapping(1, testMapping, 3);
    
    // 发送PDO
    PDO_Send(&tpdo1);
    
    // 验证接收
    // ...
}

// NMT测试
void Test_NMT_StateMachine(void) {
    // 测试状态转换
    NMT_SendCommand(NMT_CMD_ENTER_PRE_OPERATIONAL, nodeID);
    Delay_ms(100);
    assert(GetNMTState(nodeID) == NMT_STATE_PRE_OPERATIONAL);
    
    NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, nodeID);
    Delay_ms(100);
    assert(GetNMTState(nodeID) == NMT_STATE_OPERATIONAL);
}
```

**集成测试**：

```c
// 完整通信流程测试
void Test_CompleteWorkflow(void) {
    // 1. 复位节点
    NMT_SendCommand(NMT_CMD_RESET_COMMUNICATION, nodeID);
    Delay_ms(500);
    
    // 2. 配置参数
    uint16_t heartbeatTime = 1000;
    SDO_Download(nodeID, 0x1017, 0, &heartbeatTime, 2);
    
    // 3. 配置PDO
    ConfigurePDOMapping(nodeID);
    
    // 4. 启动节点
    NMT_SendCommand(NMT_CMD_START_REMOTE_NODE, nodeID);
    Delay_ms(100);
    
    // 5. 验证心跳
    assert(Heartbeat_IsAlive(nodeID));
    
    // 6. 测试PDO通信
    Test_PDO_Communication();
    
    // 7. 测试SDO通信
    Test_SDO_Download();
}
```

**压力测试**：

```c
// 总线负载测试
void Test_BusLoad(void) {
    uint32_t startTime = GetMilliseconds();
    uint32_t messageCount = 0;
    
    // 发送大量消息
    for (int i = 0; i < 10000; i++) {
        PDO_Send(&tpdo1);
        messageCount++;
    }
    
    uint32_t endTime = GetMilliseconds();
    uint32_t duration = endTime - startTime;
    
    printf("Sent %d messages in %d ms\n", messageCount, duration);
    printf("Message rate: %d msg/s\n", messageCount * 1000 / duration);
}

// 错误恢复测试
void Test_ErrorRecovery(void) {
    // 模拟错误
    EMCY_ReportError(&emcyManager, EMCY_CURRENT_OUTPUT, ERROR_REG_CURRENT, NULL);
    
    // 验证错误状态
    assert(OD_ErrorRegister & ERROR_REG_CURRENT);
    
    // 清除错误
    EMCY_ClearError(&emcyManager, ERROR_REG_CURRENT);
    
    // 验证恢复
    assert(OD_ErrorRegister == 0);
}
```

## 11. 最佳实践

### 11.1 设计原则

**1. 模块化设计**
- 将CANopen功能分解为独立模块
- 使用清晰的接口定义
- 便于测试和维护

**2. 错误处理**
- 实现完善的错误检测和报告机制
- 使用EMCY消息通知错误
- 提供错误恢复策略

**3. 实时性保证**
- 使用PDO进行实时数据交换
- 合理配置SYNC周期
- 避免在中断中执行耗时操作

**4. 可配置性**
- 通过对象字典实现参数配置
- 支持运行时参数修改
- 提供默认配置和恢复功能

### 11.2 编码规范

```c
// 命名规范
#define OD_INDEX_DEVICE_TYPE    0x1000  // 对象字典索引使用大写
typedef struct {
    uint8_t state;                      // 结构体成员使用小写
    uint16_t controlWord;               // 驼峰命名
} CANopen_Device_t;                     // 类型名使用_t后缀

// 函数命名
void CANopen_Init(void);                // 模块_功能
uint8_t SDO_Download(/* ... */);        // 返回错误码
void PDO_Send(PDO_t* pdo);              // 传递指针

// 错误处理
CO_ReturnError_t err;
err = CO_CANopenInit(/* ... */);
if (err != CO_ERROR_NO) {
    // 处理错误
    Error_Handler();
}

// 注释规范
/**
 * @brief 发送SDO下载请求
 * @param nodeID 目标节点ID
 * @param index 对象字典索引
 * @param subIndex 子索引
 * @param data 数据指针
 * @param len 数据长度
 * @return 错误码
 */
uint8_t SDO_Download(uint8_t nodeID, uint16_t index, uint8_t subIndex, 
                     void* data, uint8_t len);
```

### 11.3 安全考虑

**1. 输入验证**
```c
// 验证节点ID范围
if (nodeID < 1 || nodeID > 127) {
    return ERROR_INVALID_NODE_ID;
}

// 验证数据长度
if (len > 8) {
    return ERROR_DATA_TOO_LONG;
}

// 验证对象字典访问权限
if (!(entry->attribute & ODA_SDO_W)) {
    return ERROR_READ_ONLY;
}
```

**2. 资源保护**
```c
// 使用互斥锁保护共享资源
void PDO_Send_Safe(PDO_t* pdo) {
    Mutex_Lock(&pdoMutex);
    PDO_Send(pdo);
    Mutex_Unlock(&pdoMutex);
}

// 防止缓冲区溢出
void SDO_CopyData(uint8_t* dest, uint8_t* src, uint8_t len) {
    if (len > MAX_SDO_DATA_SIZE) {
        len = MAX_SDO_DATA_SIZE;
    }
    memcpy(dest, src, len);
}
```

**3. 故障安全**
```c
// 看门狗监控
void Watchdog_Feed(void) {
    IWDG_ReloadCounter();
}

// 安全状态
void EnterSafeState(void) {
    // 停止所有运动
    StopAllMotors();
    
    // 禁用输出
    DisableAllOutputs();
    
    // 进入停止状态
    NMT_ChangeState(&nmtManager, NMT_STATE_STOPPED);
}
```

## 12. 总结

### 12.1 关键要点

1. **CANopen协议架构**
   - 基于CAN 2.0A/B的高层协议
   - 提供SDO、PDO、NMT、EMCY等通信服务
   - 使用对象字典实现设备参数化

2. **对象字典**
   - CANopen设备的核心数据结构
   - 使用索引和子索引寻址
   - 定义设备的所有参数和通信对象

3. **通信服务**
   - SDO：配置和参数访问（面向连接）
   - PDO：实时数据交换（无连接广播）
   - NMT：网络管理和状态控制
   - EMCY：错误报告和诊断

4. **设备配置文件**
   - 标准化特定类型设备的对象和行为
   - CiA 402：驱动和运动控制
   - CiA 401：I/O模块

5. **实现要点**
   - 使用成熟的协议栈（如CANopenNode）
   - 合理配置PDO映射和传输类型
   - 实现完善的错误处理机制
   - 进行充分的测试和验证

### 12.2 学习路径

**初级阶段**：
1. 学习CAN总线基础知识
2. 理解CANopen协议架构
3. 掌握对象字典概念
4. 实现简单的SDO通信

**中级阶段**：
1. 掌握PDO配置和映射
2. 实现NMT状态机
3. 集成CANopen协议栈
4. 开发基本应用

**高级阶段**：
1. 实现设备配置文件
2. 优化通信性能
3. 开发复杂应用
4. 进行系统集成

### 12.3 进一步学习资源

**官方规范**：
- CiA 301：CANopen应用层和通信配置文件
- CiA 302：CANopen框架
- CiA 401-418：各种设备配置文件

**开源项目**：
- CANopenNode：完整的CANopen协议栈实现
- CanFestival：另一个开源CANopen协议栈
- CANopen for Python：Python实现的CANopen库

**工具软件**：
- CANopen Magic：EDS编辑和网络配置
- PCAN-View：CAN总线监控和分析
- Wireshark：协议分析（支持SocketCAN）

**在线资源**：
- CAN in Automation官网：https://www.can-cia.org/
- CANopenNode文档：https://canopennode.github.io/
- Embedded Artistry博客：CANopen教程系列

## 参考资料

1. CAN in Automation (CiA). "CANopen Application Layer and Communication Profile (CiA 301)". Version 4.2.0, 2011.

2. CAN in Automation (CiA). "CANopen Device Profile for Drives and Motion Control (CiA 402)". Version 3.3, 2014.

3. CAN in Automation (CiA). "CANopen Device Profile for Generic I/O Modules (CiA 401)". Version 2.1, 2002.

4. Pfeiffer, O., Ayre, A., & Keydel, C. "Embedded Networking with CAN and CANopen". Copperhill Technologies, 2008.

5. CANopenNode. "CANopenNode Documentation". https://canopennode.github.io/, 2023.

6. Etschberger, K. "Controller Area Network: Basics, Protocols, Chips and Applications". IXXAT Automation, 2001.

7. Lawrenz, W. "CAN System Engineering: From Theory to Practical Applications". Springer, 1997.

8. Vector Informatik. "Introduction to CANopen". Application Note AN-ION-1-3100, 2008.

9. Peak System. "PCAN-USB User Manual". Document Version 3.5, 2020.

10. STMicroelectronics. "STM32 CAN Peripheral Application Note (AN2606)". 2019.

## 相关主题

- [CAN总线硬件基础](01-can-bus-hardware.html) - CAN物理层和硬件接口
- [J1939协议应用](../../../06-communication-networking/02-network-protocols/advanced/01-j1939-protocol.html) - 车载网络协议
- [Modbus协议实现](../../../06-communication-networking/02-network-protocols/intermediate/02-modbus-protocol.html) - 工业通信协议
- [BLDC电机控制](../../05-actuator-control/intermediate/02-bldc-motor-control.html) - 电机驱动应用
- [实时操作系统](../../../03-operating-system-layer/02-rtos-fundamentals/intermediate/01-task-scheduling.html) - RTOS任务调度

---

**文档版本**: 1.0  
**最后更新**: 2026-04-05  
**作者**: 嵌入式知识平台  
**许可**: CC BY-SA 4.0
