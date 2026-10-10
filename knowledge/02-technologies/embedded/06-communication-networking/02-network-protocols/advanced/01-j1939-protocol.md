---
title: "J1939协议应用与车载网络开发"
description: "深入学习J1939车载网络通信协议的架构原理、PGN/SPN消息格式、传输协议和实战应用，掌握商用车辆CAN通信开发技术"
slug: "j1939-protocol-application"

# 分类信息
domain: "通信与网络"
module: "网络协议"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - J1939
  - CAN总线
  - 车载网络
  - PGN
  - SPN
  - 商用车辆
prerequisites:
  - "../../../01-hardware-layer/06-communication-interface-hardware/intermediate/01-can-bus-hardware.md"
  - "../../../01-hardware-layer/06-communication-interface-hardware/intermediate/06-canopen-protocol.md"
related_contents:
  - "../intermediate/03-can-protocol.md"
  <!-- 以下链接指向的文件不存在，待补充后取消注释
  - "../../01-wireless-communication/intermediate/02-vehicle-networking.md"
  -->

# 学习信息
estimated_time: 180
difficulty_score: 5

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
  - J1939协议
  - 车载CAN
  - PGN消息
  - SPN参数
  - 地址声明
cover_image: ""
---

# J1939协议应用与车载网络开发

## 学习目标

完成本教程后，你将能够：

- [ ] 理解J1939协议的架构设计和应用场景
- [ ] 掌握PGN（参数组编号）和SPN（可疑参数编号）的概念
- [ ] 熟悉J1939消息格式和标识符结构
- [ ] 能够实现J1939地址声明和网络管理
- [ ] 使用J1939传输协议进行大数据传输
- [ ] 实现J1939诊断消息和故障码
- [ ] 开发J1939车载网络应用

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉CAN总线基础知识和扩展帧格式
- 了解C语言编程和位操作
- 理解车辆电子系统基本概念
- 掌握嵌入式系统开发基础

**技能要求**：
- 能够使用CAN分析仪进行总线调试
- 会使用J1939协议分析工具
- 了解SAE J1939标准文档
- 熟悉RTOS基本使用（可选）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| STM32开发板 | 2+ | 带CAN控制器的MCU | STM32F407/F767/H743 |
| CAN收发器模块 | 2+ | CAN物理层收发器 | TJA1050/SN65HVD230 |
| CAN分析仪 | 1 | 支持J1939协议 | PCAN-USB/Vector VN1630 |
| 120Ω终端电阻 | 2 | CAN总线终端匹配 | - |
| 车辆诊断接口 | 1 | OBD-II或J1939接口 | - |
| USB调试器 | 1 | ST-Link V2或J-Link | - |

### 软件准备

| 软件 | 版本 | 用途 |
|------|------|------|
| STM32CubeIDE | 最新版 | 开发环境 |
| J1939 Stack | 开源版本 | J1939协议栈 |
| PCAN-View | 最新版 | CAN总线监控 |
| Vector CANoe | 可选 | 专业协议分析 |
| DBC Editor | 最新版 | 数据库编辑 |

## 1. J1939协议简介

### 1.1 什么是J1939

J1939是由SAE（美国汽车工程师学会）制定的车载网络通信协议，专门用于商用车辆（卡车、客车、工程机械等）的电子控制单元（ECU）之间的通信。

**核心特点**：
- **基于CAN 2.0B**：使用29位扩展标识符
- **标准化消息**：定义了大量标准PGN和SPN
- **多主网络**：支持多个ECU同时通信
- **地址管理**：动态地址声明和冲突解决
- **传输协议**：支持大于8字节的数据传输
- **诊断功能**：标准化的故障码和诊断消息

**应用领域**：
- 重型卡车（发动机、变速箱、制动系统）
- 客车（车身控制、空调系统）
- 工程机械（挖掘机、装载机、起重机）
- 农业机械（拖拉机、收割机）
- 船舶和海洋工程
- 发电机组和工业设备

### 1.2 J1939协议架构

J1939协议采用分层架构，建立在CAN 2.0B物理层之上：

```
┌─────────────────────────────────────────┐
│        应用层（Application Layer）        │
│  车辆功能、诊断、配置                     │
├─────────────────────────────────────────┤
│      J1939应用层（J1939/71-73）          │
│  PGN定义、SPN定义、诊断消息              │
├─────────────────────────────────────────┤
│      J1939网络层（J1939/21）             │
│  地址声明、网络管理、传输协议            │
├─────────────────────────────────────────┤
│      J1939数据链路层（J1939/11）         │
│  消息格式、优先级、标识符结构            │
├─────────────────────────────────────────┤
│      CAN物理层（ISO 11898）              │
│  差分信号、位时序、总线拓扑              │
└─────────────────────────────────────────┘
```

**J1939标准文档**：

| 文档编号 | 名称 | 内容 |
|---------|------|------|
| J1939/01 | 推荐实践 | 总体介绍和术语 |
| J1939/11 | 物理层 | 电气特性和连接器 |
| J1939/13 | 离线数据 | 数据库格式和工具 |
| J1939/21 | 数据链路层 | 消息格式和标识符 |
| J1939/31 | 网络层 | 地址管理和传输协议 |
| J1939/71 | 车辆应用层 | 标准PGN和SPN定义 |
| J1939/73 | 应用层诊断 | 诊断消息和故障码 |
| J1939/81 | 网络管理 | 网络配置和管理 |

### 1.3 J1939与CAN的关系

J1939使用CAN 2.0B扩展帧（29位标识符）：

```
CAN扩展帧格式：
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│SOF │ ID │SRR │IDE │ ID │RTR │r1  │r0  │DLC │Data│CRC │
│    │(11)│    │    │(18)│    │    │    │    │(0-8)│   │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

J1939标识符结构（29位）：
┌────┬────┬────┬────┬────┬────┬────┐
│ P  │ R  │ DP │ PF │ PS │ SA │    │
│(3) │(1) │(1) │(8) │(8) │(8) │    │
└────┴────┴────┴────┴────┴────┴────┘

P:  优先级（Priority，3位）
R:  保留位（Reserved，1位）
DP: 数据页（Data Page，1位）
PF: PDU格式（PDU Format，8位）
PS: PDU特定（PDU Specific，8位）
SA: 源地址（Source Address，8位）
```

**标识符字段说明**：

1. **优先级（P）**：0-7，0最高，7最低
2. **保留位（R）**：固定为0
3. **数据页（DP）**：扩展PGN空间，0或1
4. **PDU格式（PF）**：
   - PF < 240：PDU1格式（点对点通信）
   - PF ≥ 240：PDU2格式（广播通信）
5. **PDU特定（PS）**：
   - PDU1：目标地址（DA）
   - PDU2：组扩展（GE）
6. **源地址（SA）**：发送节点的地址（0-253）

### 1.4 PGN（参数组编号）

PGN是J1939中最重要的概念，它定义了一组相关参数的集合。

**PGN计算**：
```c
// PDU1格式（PF < 240）：点对点通信
// PGN = (DP << 16) | (PF << 8) | 0x00
// 例如：PF=234, DP=0 → PGN = 0x00EA00 = 59904

// PDU2格式（PF ≥ 240）：广播通信
// PGN = (DP << 16) | (PF << 8) | PS
// 例如：PF=240, PS=1, DP=0 → PGN = 0x00F001 = 61441

// PGN提取函数
uint32_t J1939_GetPGN(uint32_t canID) {
    uint8_t pf = (canID >> 16) & 0xFF;
    uint8_t ps = (canID >> 8) & 0xFF;
    uint8_t dp = (canID >> 24) & 0x01;
    
    if (pf < 240) {
        // PDU1：PS字段不是PGN的一部分
        return (dp << 16) | (pf << 8);
    } else {
        // PDU2：PS字段是PGN的一部分
        return (dp << 16) | (pf << 8) | ps;
    }
}
```

**常用PGN列表**：

| PGN | 名称 | 说明 | 更新率 |
|-----|------|------|--------|
| 0 | 转矩/速度控制 | 发动机转矩和速度命令 | 10ms |
| 61444 | 电子发动机控制器1 | 发动机转速、转矩 | 10ms |
| 61443 | 电子发动机控制器2 | 加速踏板位置、负载 | 50ms |
| 65262 | 发动机温度1 | 冷却液温度、燃油温度 | 1000ms |
| 65263 | 发动机流体液位/压力1 | 机油压力、燃油压力 | 1000ms |
| 65265 | 巡航控制/车速 | 车速、巡航控制状态 | 100ms |
| 65266 | 燃油经济性 | 燃油消耗率 | 1000ms |
| 65269 | 环境条件 | 大气压力、温度 | 1000ms |
| 61445 | 电子变速箱控制器1 | 档位、输出轴转速 | 10ms |
| 65247 | 电子制动控制器1 | 制动状态、ABS状态 | 20ms |
| 65215 | 车轮速度信息 | 各车轮速度 | 100ms |
| 59904 | 请求PGN | 请求特定PGN数据 | 按需 |
| 60416 | 传输协议-连接管理 | BAM/RTS/CTS | 按需 |
| 60160 | 传输协议-数据传输 | 多包数据传输 | 按需 |
| 60928 | 地址声明 | 节点地址声明 | 按需 |
| 65226 | 激活诊断故障码 | DTC状态 | 1000ms |

### 1.5 SPN（可疑参数编号）

SPN定义了PGN中的具体参数。每个SPN有唯一的编号、数据类型、单位和分辨率。

**SPN示例**：

| SPN | 名称 | 单位 | 分辨率 | 偏移 | 数据长度 |
|-----|------|------|--------|------|----------|
| 84 | 车速 | km/h | 1/256 | 0 | 16位 |
| 190 | 发动机转速 | rpm | 0.125 | 0 | 16位 |
| 110 | 冷却液温度 | °C | 1 | -40 | 8位 |
| 100 | 机油压力 | kPa | 4 | 0 | 8位 |
| 91 | 加速踏板位置 | % | 0.4 | 0 | 8位 |
| 92 | 发动机负载 | % | 1 | 0 | 8位 |
| 183 | 燃油消耗率 | L/h | 0.05 | 0 | 16位 |
| 96 | 燃油液位 | % | 0.4 | 0 | 8位 |
| 108 | 大气压力 | kPa | 0.5 | 0 | 8位 |
| 110 | 冷却液温度 | °C | 1 | -40 | 8位 |

**SPN数据解析**：

```c
// SPN数据结构
typedef struct {
    uint16_t spn;           // SPN编号
    uint8_t startBit;       // 起始位
    uint8_t bitLength;      // 位长度
    float resolution;       // 分辨率
    float offset;           // 偏移
    char* unit;             // 单位
} SPN_Info_t;

// 解析SPN值
float J1939_ParseSPN(uint8_t* data, SPN_Info_t* spn) {
    uint32_t rawValue = 0;
    uint8_t startByte = spn->startBit / 8;
    uint8_t startBitInByte = spn->startBit % 8;
    uint8_t bytesToRead = (spn->bitLength + startBitInByte + 7) / 8;
    
    // 提取原始值
    for (int i = 0; i < bytesToRead; i++) {
        rawValue |= (data[startByte + i] << (i * 8));
    }
    
    // 移位和掩码
    rawValue >>= startBitInByte;
    uint32_t mask = (1 << spn->bitLength) - 1;
    rawValue &= mask;
    
    // 应用分辨率和偏移
    float value = (rawValue * spn->resolution) + spn->offset;
    
    return value;
}

// 编码SPN值
void J1939_EncodeSPN(uint8_t* data, SPN_Info_t* spn, float value) {
    // 反向计算原始值
    uint32_t rawValue = (uint32_t)((value - spn->offset) / spn->resolution);
    
    uint8_t startByte = spn->startBit / 8;
    uint8_t startBitInByte = spn->startBit % 8;
    uint8_t bytesToWrite = (spn->bitLength + startBitInByte + 7) / 8;
    
    // 移位
    rawValue <<= startBitInByte;
    
    // 写入数据
    for (int i = 0; i < bytesToWrite; i++) {
        uint8_t mask = 0xFF;
        if (i == 0) {
            mask = ~((1 << startBitInByte) - 1);
        }
        if (i == bytesToWrite - 1) {
            uint8_t endBit = (spn->startBit + spn->bitLength) % 8;
            if (endBit > 0) {
                mask &= (1 << endBit) - 1;
            }
        }
        
        data[startByte + i] = (data[startByte + i] & ~mask) | 
                              ((rawValue >> (i * 8)) & mask);
    }
}

// 使用示例
void Example_ParseEngineSpeed(uint8_t* data) {
    // SPN 190: 发动机转速
    SPN_Info_t spn190 = {
        .spn = 190,
        .startBit = 24,      // 字节3-4
        .bitLength = 16,
        .resolution = 0.125,
        .offset = 0,
        .unit = "rpm"
    };
    
    float engineSpeed = J1939_ParseSPN(data, &spn190);
    printf("Engine Speed: %.1f %s\n", engineSpeed, spn190.unit);
}
```


## 2. J1939消息格式

### 2.1 标识符构造

```c
// J1939标识符构造
typedef struct {
    uint8_t priority;       // 优先级（0-7）
    uint8_t dataPage;       // 数据页（0-1）
    uint8_t pduFormat;      // PDU格式（0-255）
    uint8_t pduSpecific;    // PDU特定（0-255）
    uint8_t sourceAddress;  // 源地址（0-253）
} J1939_ID_t;

uint32_t J1939_ConstructID(J1939_ID_t* id) {
    uint32_t canID = 0;
    
    canID |= ((uint32_t)id->priority & 0x07) << 26;
    canID |= ((uint32_t)id->dataPage & 0x01) << 24;
    canID |= ((uint32_t)id->pduFormat & 0xFF) << 16;
    canID |= ((uint32_t)id->pduSpecific & 0xFF) << 8;
    canID |= ((uint32_t)id->sourceAddress & 0xFF);
    
    return canID;
}

void J1939_ParseID(uint32_t canID, J1939_ID_t* id) {
    id->priority = (canID >> 26) & 0x07;
    id->dataPage = (canID >> 24) & 0x01;
    id->pduFormat = (canID >> 16) & 0xFF;
    id->pduSpecific = (canID >> 8) & 0xFF;
    id->sourceAddress = canID & 0xFF;
}
```

### 2.2 常用PGN实现

```c
// PGN 61444: 电子发动机控制器1
typedef struct {
    uint16_t engineSpeed;           // SPN 190: 发动机转速（rpm）
    uint8_t engineTorqueMode;       // SPN 899: 转矩模式
    uint8_t driverDemandTorque;     // SPN 512: 驾驶员需求转矩（%）
    uint8_t actualTorque;           // SPN 513: 实际转矩（%）
} PGN_61444_t;

void EncodePGN61444(uint8_t* data, PGN_61444_t* pgn) {
    memset(data, 0xFF, 8);  // 初始化为无效值
    
    // SPN 899: 转矩模式（字节0，位0-3）
    data[0] = (data[0] & 0xF0) | (pgn->engineTorqueMode & 0x0F);
    
    // SPN 512: 驾驶员需求转矩（字节1）
    data[1] = pgn->driverDemandTorque;
    
    // SPN 513: 实际转矩（字节2）
    data[2] = pgn->actualTorque;
    
    // SPN 190: 发动机转速（字节3-4）
    uint16_t speedRaw = (uint16_t)(pgn->engineSpeed / 0.125);
    data[3] = speedRaw & 0xFF;
    data[4] = (speedRaw >> 8) & 0xFF;
}

// PGN 65265: 巡航控制/车速
typedef struct {
    uint16_t wheelBasedSpeed;       // SPN 84: 车速（km/h）
    uint8_t cruiseControlState;     // SPN 527: 巡航控制状态
    uint8_t cruiseControlSetSpeed;  // SPN 528: 巡航设定速度
} PGN_65265_t;

void EncodePGN65265(uint8_t* data, PGN_65265_t* pgn) {
    memset(data, 0xFF, 8);
    
    // SPN 84: 车速（字节1-2）
    uint16_t speedRaw = (uint16_t)(pgn->wheelBasedSpeed * 256);
    data[1] = speedRaw & 0xFF;
    data[2] = (speedRaw >> 8) & 0xFF;
    
    // SPN 527: 巡航控制状态（字节3，位0-2）
    data[3] = (data[3] & 0xF8) | (pgn->cruiseControlState & 0x07);
    
    // SPN 528: 巡航设定速度（字节5）
    data[5] = pgn->cruiseControlSetSpeed;
}
```

## 3. 地址管理

### 3.1 地址声明

```c
// 地址声明（PGN 60928）
typedef struct {
    uint32_t identityNumber;    // 21位：制造商分配的唯一编号
    uint16_t manufacturerCode;  // 11位：制造商代码
    uint8_t ecuInstance;        // 3位：ECU实例
    uint8_t functionInstance;   // 5位：功能实例
    uint8_t function;           // 8位：功能代码
    uint8_t vehicleSystem;      // 7位：车辆系统
    uint8_t vehicleSystemInstance; // 4位：车辆系统实例
    uint8_t industryGroup;      // 3位：行业组
    uint8_t arbitraryAddressCapable; // 1位：任意地址能力
} J1939_NAME_t;

uint64_t J1939_ConstructNAME(J1939_NAME_t* name) {
    uint64_t nameValue = 0;
    
    nameValue |= ((uint64_t)name->identityNumber & 0x1FFFFF);
    nameValue |= ((uint64_t)name->manufacturerCode & 0x7FF) << 21;
    nameValue |= ((uint64_t)name->ecuInstance & 0x07) << 32;
    nameValue |= ((uint64_t)name->functionInstance & 0x1F) << 35;
    nameValue |= ((uint64_t)name->function & 0xFF) << 40;
    nameValue |= ((uint64_t)name->vehicleSystem & 0x7F) << 48;
    nameValue |= ((uint64_t)name->vehicleSystemInstance & 0x0F) << 55;
    nameValue |= ((uint64_t)name->industryGroup & 0x07) << 59;
    nameValue |= ((uint64_t)name->arbitraryAddressCapable & 0x01) << 63;
    
    return nameValue;
}

void J1939_SendAddressClaim(uint8_t address, J1939_NAME_t* name) {
    uint8_t data[8];
    uint64_t nameValue = J1939_ConstructNAME(name);
    
    // 将NAME值转换为8字节数据
    for (int i = 0; i < 8; i++) {
        data[i] = (nameValue >> (i * 8)) & 0xFF;
    }
    
    // 构造CAN标识符（PGN 60928）
    J1939_ID_t id = {
        .priority = 6,
        .dataPage = 0,
        .pduFormat = 238,
        .pduSpecific = 0,
        .sourceAddress = address
    };
    
    uint32_t canID = J1939_ConstructID(&id);
    CAN_Send(canID, data, 8);
}
```

### 3.2 地址冲突解决

```c
typedef struct {
    uint8_t claimedAddress;
    J1939_NAME_t name;
    uint8_t addressClaimState;
    uint32_t lastClaimTime;
} J1939_AddressManager_t;

#define ADDR_STATE_IDLE             0
#define ADDR_STATE_WAIT_VERIFY      1
#define ADDR_STATE_CLAIMED          2
#define ADDR_STATE_CANNOT_CLAIM     3

void J1939_AddressClaimProcess(J1939_AddressManager_t* mgr) {
    switch (mgr->addressClaimState) {
        case ADDR_STATE_IDLE:
            // 发送地址声明
            J1939_SendAddressClaim(mgr->claimedAddress, &mgr->name);
            mgr->addressClaimState = ADDR_STATE_WAIT_VERIFY;
            mgr->lastClaimTime = GetMilliseconds();
            break;
            
        case ADDR_STATE_WAIT_VERIFY:
            // 等待250ms，检查是否有冲突
            if (GetMilliseconds() - mgr->lastClaimTime > 250) {
                mgr->addressClaimState = ADDR_STATE_CLAIMED;
            }
            break;
            
        case ADDR_STATE_CLAIMED:
            // 地址已声明，正常运行
            break;
            
        case ADDR_STATE_CANNOT_CLAIM:
            // 无法声明地址
            break;
    }
}

void J1939_HandleAddressClaimConflict(J1939_AddressManager_t* mgr, 
                                      uint8_t conflictAddress, 
                                      uint64_t conflictNAME) {
    if (conflictAddress != mgr->claimedAddress) {
        return;  // 不是我们的地址
    }
    
    uint64_t myNAME = J1939_ConstructNAME(&mgr->name);
    
    if (myNAME < conflictNAME) {
        // 我们的NAME优先级更高，重新声明
        J1939_SendAddressClaim(mgr->claimedAddress, &mgr->name);
    } else {
        // 对方NAME优先级更高，我们需要更换地址
        if (mgr->name.arbitraryAddressCapable) {
            // 尝试新地址
            mgr->claimedAddress++;
            if (mgr->claimedAddress > 253) {
                mgr->claimedAddress = 128;  // 从动态地址范围重新开始
            }
            mgr->addressClaimState = ADDR_STATE_IDLE;
        } else {
            // 无法更换地址
            mgr->addressClaimState = ADDR_STATE_CANNOT_CLAIM;
        }
    }
}
```

## 4. 传输协议

### 4.1 BAM（广播公告消息）

```c
// BAM传输（用于广播大于8字节的数据）
typedef struct {
    uint32_t pgn;
    uint16_t dataSize;
    uint8_t numPackets;
    uint8_t* data;
    uint8_t currentPacket;
} J1939_BAM_t;

void J1939_SendBAM(J1939_BAM_t* bam, uint8_t sourceAddress) {
    // 1. 发送BAM连接管理消息（PGN 60416）
    uint8_t cmData[8];
    cmData[0] = 32;  // 控制字节：BAM
    cmData[1] = bam->dataSize & 0xFF;
    cmData[2] = (bam->dataSize >> 8) & 0xFF;
    cmData[3] = bam->numPackets;
    cmData[4] = 0xFF;  // 保留
    cmData[5] = bam->pgn & 0xFF;
    cmData[6] = (bam->pgn >> 8) & 0xFF;
    cmData[7] = (bam->pgn >> 16) & 0xFF;
    
    J1939_ID_t cmID = {
        .priority = 6,
        .dataPage = 0,
        .pduFormat = 236,
        .pduSpecific = 255,  // 全局地址
        .sourceAddress = sourceAddress
    };
    CAN_Send(J1939_ConstructID(&cmID), cmData, 8);
    
    // 2. 发送数据包（PGN 60160）
    for (uint8_t i = 0; i < bam->numPackets; i++) {
        uint8_t dtData[8];
        dtData[0] = i + 1;  // 序列号
        
        uint16_t offset = i * 7;
        uint8_t bytesToCopy = (bam->dataSize - offset > 7) ? 7 : (bam->dataSize - offset);
        memcpy(&dtData[1], &bam->data[offset], bytesToCopy);
        
        // 填充剩余字节为0xFF
        for (uint8_t j = bytesToCopy + 1; j < 8; j++) {
            dtData[j] = 0xFF;
        }
        
        J1939_ID_t dtID = {
            .priority = 6,
            .dataPage = 0,
            .pduFormat = 235,
            .pduSpecific = 255,
            .sourceAddress = sourceAddress
        };
        CAN_Send(J1939_ConstructID(&dtID), dtData, 8);
        
        // BAM要求包间延迟50-200ms
        Delay_ms(50);
    }
}
```

### 4.2 CMDT（连接模式数据传输）

```c
// RTS/CTS传输（用于点对点大数据传输）
typedef struct {
    uint32_t pgn;
    uint16_t dataSize;
    uint8_t numPackets;
    uint8_t* data;
    uint8_t destAddress;
    uint8_t sourceAddress;
    uint8_t state;
    uint8_t nextPacket;
    uint8_t packetsToSend;
} J1939_CMDT_t;

#define CMDT_STATE_IDLE         0
#define CMDT_STATE_WAIT_CTS     1
#define CMDT_STATE_SENDING      2
#define CMDT_STATE_WAIT_EOMA    3

// 发送RTS（请求发送）
void J1939_SendRTS(J1939_CMDT_t* cmdt) {
    uint8_t data[8];
    data[0] = 16;  // 控制字节：RTS
    data[1] = cmdt->dataSize & 0xFF;
    data[2] = (cmdt->dataSize >> 8) & 0xFF;
    data[3] = cmdt->numPackets;
    data[4] = 0xFF;  // 最大包数（由接收方决定）
    data[5] = cmdt->pgn & 0xFF;
    data[6] = (cmdt->pgn >> 8) & 0xFF;
    data[7] = (cmdt->pgn >> 16) & 0xFF;
    
    J1939_ID_t id = {
        .priority = 6,
        .dataPage = 0,
        .pduFormat = 236,
        .pduSpecific = cmdt->destAddress,
        .sourceAddress = cmdt->sourceAddress
    };
    CAN_Send(J1939_ConstructID(&id), data, 8);
    
    cmdt->state = CMDT_STATE_WAIT_CTS;
}

// 处理CTS（清除发送）
void J1939_HandleCTS(J1939_CMDT_t* cmdt, uint8_t* data) {
    uint8_t packetsToSend = data[1];
    uint8_t nextPacket = data[2];
    
    cmdt->packetsToSend = packetsToSend;
    cmdt->nextPacket = nextPacket;
    cmdt->state = CMDT_STATE_SENDING;
}

// 发送数据包
void J1939_SendDataPackets(J1939_CMDT_t* cmdt) {
    for (uint8_t i = 0; i < cmdt->packetsToSend; i++) {
        uint8_t packetNum = cmdt->nextPacket + i;
        if (packetNum > cmdt->numPackets) {
            break;
        }
        
        uint8_t dtData[8];
        dtData[0] = packetNum;
        
        uint16_t offset = (packetNum - 1) * 7;
        uint8_t bytesToCopy = (cmdt->dataSize - offset > 7) ? 7 : (cmdt->dataSize - offset);
        memcpy(&dtData[1], &cmdt->data[offset], bytesToCopy);
        
        for (uint8_t j = bytesToCopy + 1; j < 8; j++) {
            dtData[j] = 0xFF;
        }
        
        J1939_ID_t id = {
            .priority = 6,
            .dataPage = 0,
            .pduFormat = 235,
            .pduSpecific = cmdt->destAddress,
            .sourceAddress = cmdt->sourceAddress
        };
        CAN_Send(J1939_ConstructID(&id), dtData, 8);
    }
    
    if (cmdt->nextPacket + cmdt->packetsToSend > cmdt->numPackets) {
        cmdt->state = CMDT_STATE_WAIT_EOMA;
    } else {
        cmdt->state = CMDT_STATE_WAIT_CTS;
    }
}
```

## 5. 诊断消息

### 5.1 DTC（诊断故障码）

```c
// DTC格式
typedef struct {
    uint32_t spn;           // SPN编号（19位）
    uint8_t fmi;            // 故障模式标识符（5位）
    uint8_t occurrenceCount;// 发生次数
} J1939_DTC_t;

// PGN 65226: 激活诊断故障码
void J1939_SendActiveDTC(J1939_DTC_t* dtc, uint8_t sourceAddress) {
    uint8_t data[8];
    
    // 保护灯状态（字节0-1）
    data[0] = 0xFF;
    data[1] = 0xFF;
    
    // DTC（字节2-5）
    uint32_t dtcValue = (dtc->spn & 0x7FFFF) | ((dtc->fmi & 0x1F) << 19);
    data[2] = dtcValue & 0xFF;
    data[3] = (dtcValue >> 8) & 0xFF;
    data[4] = (dtcValue >> 16) & 0xFF;
    data[5] = (dtcValue >> 24) & 0xFF;
    
    // 发生次数（字节6）
    data[6] = dtc->occurrenceCount;
    
    // 保留（字节7）
    data[7] = 0xFF;
    
    J1939_ID_t id = {
        .priority = 6,
        .dataPage = 0,
        .pduFormat = 254,
        .pduSpecific = 202,
        .sourceAddress = sourceAddress
    };
    CAN_Send(J1939_ConstructID(&id), data, 8);
}
```

## 6. 实战应用示例

### 6.1 发动机ECU实现

```c
typedef struct {
    // 地址管理
    J1939_AddressManager_t addrMgr;
    
    // 发动机参数
    uint16_t engineSpeed;       // rpm
    uint8_t engineLoad;         // %
    uint8_t coolantTemp;        // °C
    uint16_t fuelRate;          // L/h
    uint8_t throttlePosition;   // %
    
    // 诊断
    J1939_DTC_t activeDTCs[10];
    uint8_t numActiveDTCs;
} EngineECU_t;

void EngineECU_Init(EngineECU_t* ecu) {
    // 配置NAME
    ecu->addrMgr.name.identityNumber = 12345;
    ecu->addrMgr.name.manufacturerCode = 123;
    ecu->addrMgr.name.function = 0;  // 发动机
    ecu->addrMgr.name.vehicleSystem = 0;
    ecu->addrMgr.name.arbitraryAddressCapable = 1;
    
    // 声明地址
    ecu->addrMgr.claimedAddress = 0;  // 发动机通常使用地址0
    ecu->addrMgr.addressClaimState = ADDR_STATE_IDLE;
    
    // 初始化参数
    ecu->engineSpeed = 0;
    ecu->engineLoad = 0;
    ecu->coolantTemp = 20;
    ecu->fuelRate = 0;
    ecu->throttlePosition = 0;
    ecu->numActiveDTCs = 0;
}

void EngineECU_SendPGN61444(EngineECU_t* ecu) {
    PGN_61444_t pgn;
    pgn.engineSpeed = ecu->engineSpeed;
    pgn.engineTorqueMode = 0;
    pgn.driverDemandTorque = ecu->throttlePosition;
    pgn.actualTorque = ecu->engineLoad;
    
    uint8_t data[8];
    EncodePGN61444(data, &pgn);
    
    J1939_ID_t id = {
        .priority = 3,
        .dataPage = 0,
        .pduFormat = 240,
        .pduSpecific = 4,
        .sourceAddress = ecu->addrMgr.claimedAddress
    };
    CAN_Send(J1939_ConstructID(&id), data, 8);
}

void EngineECU_Process(EngineECU_t* ecu) {
    static uint32_t lastPGN61444Time = 0;
    static uint32_t lastDTCTime = 0;
    
    uint32_t currentTime = GetMilliseconds();
    
    // 地址声明处理
    J1939_AddressClaimProcess(&ecu->addrMgr);
    
    if (ecu->addrMgr.addressClaimState != ADDR_STATE_CLAIMED) {
        return;  // 地址未声明，不发送数据
    }
    
    // 发送PGN 61444（10ms周期）
    if (currentTime - lastPGN61444Time >= 10) {
        EngineECU_SendPGN61444(ecu);
        lastPGN61444Time = currentTime;
    }
    
    // 发送DTC（1000ms周期）
    if (currentTime - lastDTCTime >= 1000 && ecu->numActiveDTCs > 0) {
        J1939_SendActiveDTC(&ecu->activeDTCs[0], ecu->addrMgr.claimedAddress);
        lastDTCTime = currentTime;
    }
}
```

## 7. 调试与故障排除

### 7.1 常见问题

**问题1：地址冲突**
- 检查NAME配置是否唯一
- 验证地址声明流程
- 使用CAN分析仪监控地址声明消息

**问题2：数据解析错误**
- 验证PGN和SPN定义
- 检查字节序（小端序）
- 确认分辨率和偏移计算

**问题3：传输协议失败**
- 检查包间延迟
- 验证序列号
- 监控CTS/RTS消息

## 8. 最佳实践

1. **使用标准PGN**：优先使用SAE定义的标准PGN
2. **正确的优先级**：根据消息重要性设置优先级
3. **周期性发送**：按照标准要求的更新率发送
4. **错误处理**：实现完善的DTC报告机制
5. **测试验证**：使用专业工具进行一致性测试

## 9. 总结

J1939协议是商用车辆CAN通信的行业标准，掌握其核心概念（PGN、SPN、地址管理、传输协议）对于车载网络开发至关重要。

## 参考资料

1. SAE International. "J1939 Digital Annex". 2023.
2. SAE J1939/21. "Data Link Layer". 2015.
3. SAE J1939/71. "Vehicle Application Layer". 2017.
4. SAE J1939/73. "Application Layer - Diagnostics". 2016.
5. Copperhill Technologies. "J1939 Protocol Stack". 2022.

## 相关主题

- [CAN总线硬件](../../../01-hardware-layer/06-communication-interface-hardware/intermediate/01-can-bus-hardware.html)
- [CANopen协议](../../../01-hardware-layer/06-communication-interface-hardware/intermediate/06-canopen-protocol.html)
<!-- 以下链接指向的文件不存在，待补充后取消注释
- [车载网络](../../01-wireless-communication/intermediate/02-vehicle-networking.html)
-->

---

**文档版本**: 1.0  
**最后更新**: 2026-04-05  
**作者**: 嵌入式知识平台  
**许可**: CC BY-SA 4.0
