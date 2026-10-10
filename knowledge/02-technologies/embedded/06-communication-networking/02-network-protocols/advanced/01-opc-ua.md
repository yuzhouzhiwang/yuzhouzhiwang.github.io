---
title: "OPC UA工业互联协议实战开发"
description: "深入学习OPC UA架构、信息模型、安全机制和客户端开发，掌握工业4.0时代的核心通信技术，实现设备互联互通和数据安全传输"
slug: "opc-ua-industrial-protocol"

# 分类信息
domain: "通信与网络"
module: "网络协议"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - OPC UA
  - 工业互联
  - 工业4.0
  - 信息模型
  - 安全通信
prerequisites:
  - "01-tcpip-stack"
  - "04-http-https"
  - "02-modbus-protocol"
related_contents: []

# 学习信息
estimated_time: 100
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-08"
updated_at: "2026-03-08"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - OPC UA协议
  - 工业通信
  - 信息模型
  - 安全机制
  - 工业4.0
cover_image: ""
---

# OPC UA工业互联协议实战开发

## 学习目标

完成本教程后，你将能够：

- [ ] 理解OPC UA的架构和核心概念
- [ ] 掌握OPC UA信息模型和地址空间
- [ ] 了解OPC UA的安全机制和证书管理
- [ ] 使用open62541库开发OPC UA服务器
- [ ] 开发OPC UA客户端进行数据读写和订阅
- [ ] 实现工业设备的OPC UA接口集成

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉TCP/IP网络协议
- 了解客户端-服务器架构
- 理解工业自动化基本概念
- 掌握C/C++编程
- 了解XML和JSON数据格式

**技能要求**：
- 能够使用Linux开发环境
- 会使用CMake构建系统
- 了解证书和加密基础知识
- 熟悉Modbus等工业协议（可选）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| Linux开发机 | 1 | Ubuntu 20.04+或树莓派 | - |
| STM32/ESP32开发板 | 1 | 可选，用于嵌入式实现 | - |
| 工业传感器 | 若干 | 可选，用于数据采集 | - |
| 以太网线 | 1 | 网络连接 | - |

### 软件准备

- **开发环境**：
  - Ubuntu 20.04 LTS 或更高版本
  - GCC 9.0+ 或 Clang 10.0+
  - CMake 3.15+
  - Git
- **OPC UA库**：
  - open62541 (开源C实现)
  - Python opcua库 (用于测试)
- **测试工具**：
  - UaExpert (OPC UA客户端)
  - Prosys OPC UA Browser
  - Wireshark (网络抓包)

### 环境配置

#### 1. 安装依赖包

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装编译工具
sudo apt install -y build-essential cmake git

# 安装依赖库
sudo apt install -y libmbedtls-dev python3-pip

# 安装Python OPC UA库（用于测试）
pip3 install opcua
```

#### 2. 下载并编译open62541

```bash
# 克隆仓库
git clone https://github.com/open62541/open62541.git
cd open62541

# 创建构建目录
mkdir build && cd build

# 配置CMake（启用加密和示例）
cmake -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DUA_ENABLE_ENCRYPTION=MBEDTLS \
      -DUA_BUILD_EXAMPLES=ON \
      ..

# 编译
make -j$(nproc)

# 安装
sudo make install
sudo ldconfig
```

#### 3. 安装UaExpert测试工具

- 访问 https://www.unified-automation.com/
- 下载UaExpert客户端
- 安装并启动

## OPC UA协议基础

### 什么是OPC UA？

OPC UA (OPC Unified Architecture) 是由OPC基金会开发的工业通信标准，是OPC Classic的继任者，专为工业4.0和物联网设计。

**核心特点**：
- **平台无关**：支持Windows、Linux、嵌入式系统
- **安全可靠**：内置加密、认证和授权机制
- **语义丰富**：信息模型支持复杂数据结构
- **可扩展性**：支持自定义数据类型和对象模型
- **互操作性**：统一的标准，不同厂商设备可互联

### OPC UA vs OPC Classic vs Modbus

| 特性 | OPC UA | OPC Classic | Modbus |
|------|--------|-------------|--------|
| 平台支持 | 跨平台 | 仅Windows | 跨平台 |
| 安全性 | 内置加密认证 | 依赖DCOM | 无安全机制 |
| 数据模型 | 面向对象 | 简单标签 | 寄存器 |
| 传输协议 | TCP/IP | DCOM | TCP/RS485 |
| 复杂度 | 高 | 中 | 低 |
| 应用场景 | 工业4.0 | 传统SCADA | 现场设备 |

### OPC UA架构

```text
┌─────────────────────────────────────────┐
│         应用层 (Application)            │
│  ┌──────────┐  ┌──────────┐            │
│  │  Client  │  │  Server  │            │
│  └──────────┘  └──────────┘            │
├─────────────────────────────────────────┤
│      服务层 (Services)                  │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │ 发现服务 │ │ 会话服务 │ │ 订阅服务 │ │
│  └─────────┘ └─────────┘ └──────────┘ │
├─────────────────────────────────────────┤
│      通信层 (Communication)             │
│  ┌──────────────┐  ┌─────────────────┐│
│  │  UA Binary   │  │  UA JSON/XML    ││
│  └──────────────┘  └─────────────────┘│
├─────────────────────────────────────────┤
│      传输层 (Transport)                 │
│  ┌──────────────┐  ┌─────────────────┐│
│  │   TCP/IP     │  │   HTTPS/WSS     ││
│  └──────────────┘  └─────────────────┘│
└─────────────────────────────────────────┘
```

### OPC UA信息模型

OPC UA使用面向对象的信息模型，核心概念包括：

**1. 节点 (Node)**
- 地址空间中的基本元素
- 每个节点有唯一的NodeId
- 包含属性和引用

**2. 节点类型**
| 类型 | 说明 | 示例 |
|------|------|------|
| Object | 对象节点 | 设备、传感器 |
| Variable | 变量节点 | 温度值、状态 |
| Method | 方法节点 | 启动、停止 |
| ObjectType | 对象类型 | 传感器类型 |
| VariableType | 变量类型 | 模拟量类型 |
| DataType | 数据类型 | Int32、String |
| ReferenceType | 引用类型 | HasComponent |

**3. 引用 (Reference)**
- 连接节点的关系
- 常用引用类型：
  - HasComponent: 组件关系
  - HasProperty: 属性关系
  - Organizes: 组织关系
  - HasTypeDefinition: 类型定义

**4. 地址空间示例**

```text
Root
├── Objects
│   ├── Server
│   │   ├── ServerStatus
│   │   └── ServerCapabilities
│   └── MyDevice (自定义对象)
│       ├── Temperature (变量)
│       ├── Humidity (变量)
│       └── Start() (方法)
├── Types
│   ├── ObjectTypes
│   └── VariableTypes
└── Views
```

### OPC UA安全机制

OPC UA提供三层安全保护：

**1. 传输层安全**
- 使用TLS/SSL加密通信
- 支持证书认证
- 防止中间人攻击

**2. 应用层安全**
- 消息签名和加密
- 支持多种安全策略：
  - None: 无安全
  - Basic128Rsa15: 基础加密
  - Basic256: 标准加密
  - Basic256Sha256: 强加密

**3. 用户认证**
- 匿名认证
- 用户名/密码认证
- X.509证书认证
- Kerberos认证

### OPC UA服务

OPC UA定义了多种服务集：

| 服务集 | 功能 | 主要服务 |
|--------|------|----------|
| Discovery | 发现服务器 | FindServers, GetEndpoints |
| Session | 会话管理 | CreateSession, ActivateSession |
| NodeManagement | 节点管理 | AddNodes, DeleteNodes |
| View | 浏览地址空间 | Browse, BrowseNext |
| Attribute | 读写属性 | Read, Write |
| Method | 调用方法 | Call |
| MonitoredItem | 数据监控 | CreateMonitoredItems |
| Subscription | 订阅管理 | CreateSubscription |

## 步骤1：创建基础OPC UA服务器

### 1.1 创建项目结构

```bash
mkdir opcua_server && cd opcua_server
mkdir src include build
```

### 1.2 编写基础服务器代码

创建 `src/server_basic.c`：

```c
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>

#include <signal.h>
#include <stdlib.h>

// 运行标志
static volatile UA_Boolean running = true;

// 信号处理函数
static void stopHandler(int sig) {
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "收到信号 %d", sig);
    running = false;
}

int main(void) {
    // 注册信号处理
    signal(SIGINT, stopHandler);
    signal(SIGTERM, stopHandler);

    // 创建服务器实例
    UA_Server *server = UA_Server_new();
    
    // 使用默认配置（端口4840）
    UA_ServerConfig_setDefault(UA_Server_getConfig(server));

    // 启动服务器
    UA_StatusCode retval = UA_Server_run(server, &running);

    // 清理资源
    UA_Server_delete(server);
    
    return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
```

**代码说明**：
- `UA_Server_new()`: 创建服务器实例
- `UA_ServerConfig_setDefault()`: 使用默认配置（端口4840）
- `UA_Server_run()`: 启动服务器并进入事件循环
- `UA_Server_delete()`: 清理服务器资源

### 1.3 创建CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.15)
project(opcua_server C)

# 查找open62541库
find_package(open62541 REQUIRED)

# 添加可执行文件
add_executable(server_basic src/server_basic.c)

# 链接库
target_link_libraries(server_basic open62541::open62541)

# 设置C标准
set_property(TARGET server_basic PROPERTY C_STANDARD 99)
```

### 1.4 编译和运行

```bash
cd build
cmake ..
make

# 运行服务器
./server_basic
```

**预期输出**：
```text
[2026-03-08 10:00:00.000 (UTC+0800)] info/server    OPC UA Server started
[2026-03-08 10:00:00.001 (UTC+0800)] info/network   TCP network layer listening on opc.tcp://localhost:4840/
```

### 1.5 使用UaExpert连接测试

1. 打开UaExpert
2. 点击 "Server" -> "Add Server"
3. 选择 "Custom Discovery"
4. 输入URL: `opc.tcp://localhost:4840`
5. 点击 "Get Endpoints"
6. 选择端点并连接
7. 浏览地址空间，查看默认节点

## 步骤2：添加自定义变量节点

### 2.1 添加简单变量

创建 `src/server_variables.c`：

```c
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>

#include <signal.h>
#include <stdlib.h>

static volatile UA_Boolean running = true;
static void stopHandler(int sig) {
    running = false;
}

// 添加变量节点的函数
static void addVariableNode(UA_Server *server) {
    // 定义变量属性
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    
    // 设置初始值
    UA_Int32 myInteger = 42;
    UA_Variant_setScalar(&attr.value, &myInteger, &UA_TYPES[UA_TYPES_INT32]);
    
    // 设置节点属性
    attr.description = UA_LOCALIZEDTEXT("en-US", "My Integer Variable");
    attr.displayName = UA_LOCALIZEDTEXT("en-US", "MyInteger");
    attr.dataType = UA_TYPES[UA_TYPES_INT32].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;

    // 定义节点ID
    UA_NodeId myIntegerNodeId = UA_NODEID_STRING(1, "MyInteger");
    
    // 定义父节点（Objects文件夹）
    UA_NodeId parentNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER);
    UA_NodeId parentReferenceNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES);
    
    // 定义浏览名称
    UA_QualifiedName myIntegerName = UA_QUALIFIEDNAME(1, "MyInteger");
    
    // 添加变量节点
    UA_StatusCode retval = UA_Server_addVariableNode(
        server,
        myIntegerNodeId,           // 节点ID
        parentNodeId,              // 父节点ID
        parentReferenceNodeId,     // 引用类型
        myIntegerName,             // 浏览名称
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),  // 类型定义
        attr,                      // 属性
        NULL,                      // 节点上下文
        NULL                       // 输出节点ID
    );

    if(retval == UA_STATUSCODE_GOOD)
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, 
                    "成功添加变量节点 'MyInteger'");
}

int main(void) {
    signal(SIGINT, stopHandler);
    signal(SIGTERM, stopHandler);

    UA_Server *server = UA_Server_new();
    UA_ServerConfig_setDefault(UA_Server_getConfig(server));

    // 添加自定义变量
    addVariableNode(server);

    UA_StatusCode retval = UA_Server_run(server, &running);
    UA_Server_delete(server);
    
    return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
```

**代码说明**：
- `UA_VariableAttributes_default`: 创建默认变量属性
- `UA_Variant_setScalar()`: 设置变量值
- `UA_NODEID_STRING()`: 创建字符串类型的节点ID
- `UA_Server_addVariableNode()`: 添加变量节点到地址空间
- `UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE`: 设置读写权限

### 2.2 添加多个不同类型的变量

```c
// 添加温度变量（浮点数）
static void addTemperatureVariable(UA_Server *server) {
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    UA_Double temperature = 25.5;
    UA_Variant_setScalar(&attr.value, &temperature, &UA_TYPES[UA_TYPES_DOUBLE]);
    
    attr.description = UA_LOCALIZEDTEXT("zh-CN", "当前温度");
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "温度");
    attr.dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;

    UA_NodeId nodeId = UA_NODEID_STRING(1, "Temperature");
    UA_QualifiedName name = UA_QUALIFIEDNAME(1, "Temperature");
    
    UA_Server_addVariableNode(
        server, nodeId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        name,
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );
}

// 添加设备状态变量（字符串）
static void addStatusVariable(UA_Server *server) {
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    UA_String status = UA_STRING("Running");
    UA_Variant_setScalar(&attr.value, &status, &UA_TYPES[UA_TYPES_STRING]);
    
    attr.description = UA_LOCALIZEDTEXT("zh-CN", "设备状态");
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "状态");
    attr.dataType = UA_TYPES[UA_TYPES_STRING].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ;  // 只读

    UA_NodeId nodeId = UA_NODEID_STRING(1, "DeviceStatus");
    UA_QualifiedName name = UA_QUALIFIEDNAME(1, "DeviceStatus");
    
    UA_Server_addVariableNode(
        server, nodeId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        name,
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );
}

// 添加布尔变量
static void addAlarmVariable(UA_Server *server) {
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    UA_Boolean alarm = false;
    UA_Variant_setScalar(&attr.value, &alarm, &UA_TYPES[UA_TYPES_BOOLEAN]);
    
    attr.description = UA_LOCALIZEDTEXT("zh-CN", "报警状态");
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "报警");
    attr.dataType = UA_TYPES[UA_TYPES_BOOLEAN].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;

    UA_NodeId nodeId = UA_NODEID_STRING(1, "Alarm");
    UA_QualifiedName name = UA_QUALIFIEDNAME(1, "Alarm");
    
    UA_Server_addVariableNode(
        server, nodeId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        name,
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );
}
```

### 2.3 添加数组变量

```c
// 添加数组变量
static void addArrayVariable(UA_Server *server) {
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    
    // 创建整数数组
    UA_Int32 array[5] = {10, 20, 30, 40, 50};
    UA_Variant_setArray(&attr.value, array, 5, &UA_TYPES[UA_TYPES_INT32]);
    
    attr.description = UA_LOCALIZEDTEXT("zh-CN", "数据数组");
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "数组");
    attr.dataType = UA_TYPES[UA_TYPES_INT32].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    attr.valueRank = UA_VALUERANK_ONE_DIMENSION;  // 一维数组
    
    // 设置数组维度
    UA_UInt32 arrayDimensions[1] = {5};
    attr.arrayDimensionsSize = 1;
    attr.arrayDimensions = arrayDimensions;

    UA_NodeId nodeId = UA_NODEID_STRING(1, "DataArray");
    UA_QualifiedName name = UA_QUALIFIEDNAME(1, "DataArray");
    
    UA_Server_addVariableNode(
        server, nodeId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        name,
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );
}
```

## 步骤3：创建对象和组织结构

### 3.1 创建自定义对象

```c
// 创建设备对象
static UA_NodeId addDeviceObject(UA_Server *server) {
    // 对象属性
    UA_ObjectAttributes oAttr = UA_ObjectAttributes_default;
    oAttr.description = UA_LOCALIZEDTEXT("zh-CN", "工业设备");
    oAttr.displayName = UA_LOCALIZEDTEXT("zh-CN", "设备1");

    // 添加对象节点
    UA_NodeId deviceId;
    UA_Server_addObjectNode(
        server,
        UA_NODEID_STRING(1, "Device1"),  // 节点ID
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),  // 父节点
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),  // 引用类型
        UA_QUALIFIEDNAME(1, "Device1"),  // 浏览名称
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEOBJECTTYPE),  // 类型定义
        oAttr,  // 属性
        NULL,  // 节点上下文
        &deviceId  // 输出节点ID
    );

    return deviceId;
}

// 为设备对象添加属性
static void addDeviceProperties(UA_Server *server, UA_NodeId deviceId) {
    // 添加设备名称属性
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    UA_String deviceName = UA_STRING("Industrial Sensor");
    UA_Variant_setScalar(&attr.value, &deviceName, &UA_TYPES[UA_TYPES_STRING]);
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "设备名称");
    
    UA_Server_addVariableNode(
        server,
        UA_NODEID_STRING(1, "Device1.Name"),
        deviceId,  // 父节点是设备对象
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASPROPERTY),  // 属性引用
        UA_QUALIFIEDNAME(1, "Name"),
        UA_NODEID_NUMERIC(0, UA_NS0ID_PROPERTYTYPE),
        attr, NULL, NULL
    );

    // 添加序列号属性
    UA_String serialNumber = UA_STRING("SN-2024-001");
    UA_Variant_setScalar(&attr.value, &serialNumber, &UA_TYPES[UA_TYPES_STRING]);
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "序列号");
    
    UA_Server_addVariableNode(
        server,
        UA_NODEID_STRING(1, "Device1.SerialNumber"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASPROPERTY),
        UA_QUALIFIEDNAME(1, "SerialNumber"),
        UA_NODEID_NUMERIC(0, UA_NS0ID_PROPERTYTYPE),
        attr, NULL, NULL
    );
}

// 为设备对象添加组件（传感器数据）
static void addDeviceComponents(UA_Server *server, UA_NodeId deviceId) {
    // 添加温度组件
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    UA_Double temperature = 25.0;
    UA_Variant_setScalar(&attr.value, &temperature, &UA_TYPES[UA_TYPES_DOUBLE]);
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "温度");
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;
    
    UA_Server_addVariableNode(
        server,
        UA_NODEID_STRING(1, "Device1.Temperature"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),  // 组件引用
        UA_QUALIFIEDNAME(1, "Temperature"),
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );

    // 添加湿度组件
    UA_Double humidity = 60.0;
    UA_Variant_setScalar(&attr.value, &humidity, &UA_TYPES[UA_TYPES_DOUBLE]);
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "湿度");
    
    UA_Server_addVariableNode(
        server,
        UA_NODEID_STRING(1, "Device1.Humidity"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "Humidity"),
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );
}
```

**代码说明**：
- `UA_Server_addObjectNode()`: 添加对象节点
- `UA_NS0ID_HASPROPERTY`: 属性引用类型
- `UA_NS0ID_HASCOMPONENT`: 组件引用类型
- 属性用于描述对象的静态信息
- 组件用于表示对象的功能部分

### 3.2 创建文件夹组织结构

```c
// 创建文件夹节点
static UA_NodeId addFolder(UA_Server *server, const char *name, 
                           UA_NodeId parentId) {
    UA_ObjectAttributes oAttr = UA_ObjectAttributes_default;
    oAttr.displayName = UA_LOCALIZEDTEXT("zh-CN", name);

    UA_NodeId folderId;
    UA_Server_addObjectNode(
        server,
        UA_NODEID_NULL,  // 自动生成ID
        parentId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        UA_QUALIFIEDNAME(1, name),
        UA_NODEID_NUMERIC(0, UA_NS0ID_FOLDERTYPE),  // 文件夹类型
        oAttr,
        NULL,
        &folderId
    );

    return folderId;
}

// 创建层次结构
static void createHierarchy(UA_Server *server) {
    // 创建工厂文件夹
    UA_NodeId factoryId = addFolder(server, "Factory", 
                                    UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER));
    
    // 创建车间文件夹
    UA_NodeId workshop1Id = addFolder(server, "Workshop1", factoryId);
    UA_NodeId workshop2Id = addFolder(server, "Workshop2", factoryId);
    
    // 在车间1下添加设备
    UA_NodeId device1 = addDeviceObject(server);
    // 将设备移动到车间1下（需要删除原引用并添加新引用）
    UA_Server_addReference(server, device1, 
                          UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
                          UA_EXPANDEDNODEID_NUMERIC(0, workshop1Id.identifier.numeric),
                          true);
}
```

**地址空间结构**：
```text
Objects
└── Factory
    ├── Workshop1
    │   └── Device1
    │       ├── Name (属性)
    │       ├── SerialNumber (属性)
    │       ├── Temperature (组件)
    │       └── Humidity (组件)
    └── Workshop2
```

## 步骤4：实现数据源回调

### 4.1 添加数据源回调

```c
// 数据源读取回调
static UA_StatusCode
readTemperature(UA_Server *server,
                const UA_NodeId *sessionId, void *sessionContext,
                const UA_NodeId *nodeId, void *nodeContext,
                UA_Boolean sourceTimeStamp, const UA_NumericRange *range,
                UA_DataValue *dataValue) {
    // 模拟读取传感器数据
    UA_Double temperature = 20.0 + (rand() % 100) / 10.0;  // 20.0-30.0°C
    
    UA_Variant_setScalarCopy(&dataValue->value, &temperature, 
                             &UA_TYPES[UA_TYPES_DOUBLE]);
    dataValue->hasValue = true;
    
    // 设置时间戳
    if(sourceTimeStamp) {
        dataValue->sourceTimestamp = UA_DateTime_now();
        dataValue->hasSourceTimestamp = true;
    }
    
    return UA_STATUSCODE_GOOD;
}

// 数据源写入回调
static UA_StatusCode
writeTemperature(UA_Server *server,
                 const UA_NodeId *sessionId, void *sessionContext,
                 const UA_NodeId *nodeId, void *nodeContext,
                 const UA_NumericRange *range, const UA_DataValue *data) {
    // 验证数据类型
    if(data->value.type != &UA_TYPES[UA_TYPES_DOUBLE])
        return UA_STATUSCODE_BADTYPEMISMATCH;
    
    UA_Double *temperature = (UA_Double*)data->value.data;
    
    // 验证数据范围
    if(*temperature < -50.0 || *temperature > 100.0) {
        UA_LOG_WARNING(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                      "温度值超出范围: %.2f", *temperature);
        return UA_STATUSCODE_BADOUTOFRANGE;
    }
    
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                "温度设定为: %.2f°C", *temperature);
    
    // 这里可以实际控制硬件
    // controlHeater(*temperature);
    
    return UA_STATUSCODE_GOOD;
}

// 添加带数据源的变量
static void addVariableWithDataSource(UA_Server *server) {
    UA_VariableAttributes attr = UA_VariableAttributes_default;
    attr.description = UA_LOCALIZEDTEXT("zh-CN", "实时温度");
    attr.displayName = UA_LOCALIZEDTEXT("zh-CN", "温度");
    attr.dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    attr.accessLevel = UA_ACCESSLEVELMASK_READ | UA_ACCESSLEVELMASK_WRITE;

    UA_NodeId temperatureId = UA_NODEID_STRING(1, "Temperature");
    
    // 添加变量节点
    UA_Server_addVariableNode(
        server, temperatureId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER),
        UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES),
        UA_QUALIFIEDNAME(1, "Temperature"),
        UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
        attr, NULL, NULL
    );

    // 设置数据源
    UA_DataSource temperatureDataSource;
    temperatureDataSource.read = readTemperature;
    temperatureDataSource.write = writeTemperature;
    
    UA_Server_setVariableNode_dataSource(server, temperatureId, 
                                         temperatureDataSource);
}
```

**代码说明**：
- 数据源回调允许动态生成数据
- `read`回调在客户端读取时调用
- `write`回调在客户端写入时调用
- 可以在回调中访问实际硬件或数据库

### 4.2 周期性更新变量值

```c
// 定时器回调函数
static void updateVariables(UA_Server *server, void *data) {
    // 更新温度值
    UA_NodeId temperatureId = UA_NODEID_STRING(1, "Device1.Temperature");
    UA_Double temperature = 20.0 + (rand() % 100) / 10.0;
    UA_Variant value;
    UA_Variant_setScalar(&value, &temperature, &UA_TYPES[UA_TYPES_DOUBLE]);
    UA_Server_writeValue(server, temperatureId, value);

    // 更新湿度值
    UA_NodeId humidityId = UA_NODEID_STRING(1, "Device1.Humidity");
    UA_Double humidity = 50.0 + (rand() % 300) / 10.0;
    UA_Variant_setScalar(&value, &humidity, &UA_TYPES[UA_TYPES_DOUBLE]);
    UA_Server_writeValue(server, humidityId, value);
}

int main(void) {
    signal(SIGINT, stopHandler);
    signal(SIGTERM, stopHandler);

    UA_Server *server = UA_Server_new();
    UA_ServerConfig_setDefault(UA_Server_getConfig(server));

    // 添加节点
    UA_NodeId deviceId = addDeviceObject(server);
    addDeviceProperties(server, deviceId);
    addDeviceComponents(server, deviceId);

    // 添加定时器（每1000ms更新一次）
    UA_Server_addRepeatedCallback(server, updateVariables, NULL, 1000, NULL);

    UA_StatusCode retval = UA_Server_run(server, &running);
    UA_Server_delete(server);
    
    return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
```

**代码说明**：
- `UA_Server_addRepeatedCallback()`: 添加周期性回调
- `UA_Server_writeValue()`: 写入变量值
- 定时器在服务器事件循环中执行
- 适合周期性采集传感器数据

## 步骤5：添加方法节点

### 5.1 实现方法回调

```c
// 方法回调函数：启动设备
static UA_StatusCode
startDeviceMethod(UA_Server *server,
                  const UA_NodeId *sessionId, void *sessionContext,
                  const UA_NodeId *methodId, void *methodContext,
                  const UA_NodeId *objectId, void *objectContext,
                  size_t inputSize, const UA_Variant *input,
                  size_t outputSize, UA_Variant *output) {
    
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "设备启动");
    
    // 更新设备状态
    UA_NodeId statusId = UA_NODEID_STRING(1, "Device1.Status");
    UA_String status = UA_STRING("Running");
    UA_Variant value;
    UA_Variant_setScalar(&value, &status, &UA_TYPES[UA_TYPES_STRING]);
    UA_Server_writeValue(server, statusId, value);
    
    // 设置输出参数（返回启动时间）
    UA_DateTime startTime = UA_DateTime_now();
    UA_Variant_setScalarCopy(&output[0], &startTime, &UA_TYPES[UA_TYPES_DATETIME]);
    
    return UA_STATUSCODE_GOOD;
}

// 方法回调函数：停止设备
static UA_StatusCode
stopDeviceMethod(UA_Server *server,
                 const UA_NodeId *sessionId, void *sessionContext,
                 const UA_NodeId *methodId, void *methodContext,
                 const UA_NodeId *objectId, void *objectContext,
                 size_t inputSize, const UA_Variant *input,
                 size_t outputSize, UA_Variant *output) {
    
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "设备停止");
    
    // 更新设备状态
    UA_NodeId statusId = UA_NODEID_STRING(1, "Device1.Status");
    UA_String status = UA_STRING("Stopped");
    UA_Variant value;
    UA_Variant_setScalar(&value, &status, &UA_TYPES[UA_TYPES_STRING]);
    UA_Server_writeValue(server, statusId, value);
    
    return UA_STATUSCODE_GOOD;
}

// 带参数的方法：设置温度阈值
static UA_StatusCode
setThresholdMethod(UA_Server *server,
                   const UA_NodeId *sessionId, void *sessionContext,
                   const UA_NodeId *methodId, void *methodContext,
                   const UA_NodeId *objectId, void *objectContext,
                   size_t inputSize, const UA_Variant *input,
                   size_t outputSize, UA_Variant *output) {
    
    // 获取输入参数
    UA_Double minTemp = *(UA_Double*)input[0].data;
    UA_Double maxTemp = *(UA_Double*)input[1].data;
    
    // 验证参数
    if(minTemp >= maxTemp) {
        UA_LOG_WARNING(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                      "无效的温度范围: %.2f - %.2f", minTemp, maxTemp);
        return UA_STATUSCODE_BADINVALIDARGUMENT;
    }
    
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                "设置温度阈值: %.2f - %.2f", minTemp, maxTemp);
    
    // 设置输出参数（返回是否成功）
    UA_Boolean success = true;
    UA_Variant_setScalarCopy(&output[0], &success, &UA_TYPES[UA_TYPES_BOOLEAN]);
    
    return UA_STATUSCODE_GOOD;
}
```

### 5.2 添加方法节点

```c
// 添加启动方法
static void addStartMethod(UA_Server *server, UA_NodeId deviceId) {
    // 定义输出参数
    UA_Argument outputArgument;
    UA_Argument_init(&outputArgument);
    outputArgument.description = UA_LOCALIZEDTEXT("zh-CN", "启动时间");
    outputArgument.name = UA_STRING("StartTime");
    outputArgument.dataType = UA_TYPES[UA_TYPES_DATETIME].typeId;
    outputArgument.valueRank = UA_VALUERANK_SCALAR;

    // 方法属性
    UA_MethodAttributes methodAttr = UA_MethodAttributes_default;
    methodAttr.description = UA_LOCALIZEDTEXT("zh-CN", "启动设备");
    methodAttr.displayName = UA_LOCALIZEDTEXT("zh-CN", "启动");
    methodAttr.executable = true;
    methodAttr.userExecutable = true;

    // 添加方法节点
    UA_Server_addMethodNode(
        server,
        UA_NODEID_STRING(1, "Device1.Start"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "Start"),
        methodAttr,
        &startDeviceMethod,  // 方法回调
        0, NULL,             // 输入参数
        1, &outputArgument,  // 输出参数
        NULL, NULL
    );
}

// 添加停止方法
static void addStopMethod(UA_Server *server, UA_NodeId deviceId) {
    UA_MethodAttributes methodAttr = UA_MethodAttributes_default;
    methodAttr.description = UA_LOCALIZEDTEXT("zh-CN", "停止设备");
    methodAttr.displayName = UA_LOCALIZEDTEXT("zh-CN", "停止");
    methodAttr.executable = true;
    methodAttr.userExecutable = true;

    UA_Server_addMethodNode(
        server,
        UA_NODEID_STRING(1, "Device1.Stop"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "Stop"),
        methodAttr,
        &stopDeviceMethod,
        0, NULL,  // 无输入参数
        0, NULL,  // 无输出参数
        NULL, NULL
    );
}

// 添加设置阈值方法
static void addSetThresholdMethod(UA_Server *server, UA_NodeId deviceId) {
    // 定义输入参数
    UA_Argument inputArguments[2];
    UA_Argument_init(&inputArguments[0]);
    inputArguments[0].description = UA_LOCALIZEDTEXT("zh-CN", "最小温度");
    inputArguments[0].name = UA_STRING("MinTemperature");
    inputArguments[0].dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    inputArguments[0].valueRank = UA_VALUERANK_SCALAR;

    UA_Argument_init(&inputArguments[1]);
    inputArguments[1].description = UA_LOCALIZEDTEXT("zh-CN", "最大温度");
    inputArguments[1].name = UA_STRING("MaxTemperature");
    inputArguments[1].dataType = UA_TYPES[UA_TYPES_DOUBLE].typeId;
    inputArguments[1].valueRank = UA_VALUERANK_SCALAR;

    // 定义输出参数
    UA_Argument outputArgument;
    UA_Argument_init(&outputArgument);
    outputArgument.description = UA_LOCALIZEDTEXT("zh-CN", "是否成功");
    outputArgument.name = UA_STRING("Success");
    outputArgument.dataType = UA_TYPES[UA_TYPES_BOOLEAN].typeId;
    outputArgument.valueRank = UA_VALUERANK_SCALAR;

    // 方法属性
    UA_MethodAttributes methodAttr = UA_MethodAttributes_default;
    methodAttr.description = UA_LOCALIZEDTEXT("zh-CN", "设置温度阈值");
    methodAttr.displayName = UA_LOCALIZEDTEXT("zh-CN", "设置阈值");
    methodAttr.executable = true;
    methodAttr.userExecutable = true;

    // 添加方法节点
    UA_Server_addMethodNode(
        server,
        UA_NODEID_STRING(1, "Device1.SetThreshold"),
        deviceId,
        UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
        UA_QUALIFIEDNAME(1, "SetThreshold"),
        methodAttr,
        &setThresholdMethod,
        2, inputArguments,   // 2个输入参数
        1, &outputArgument,  // 1个输出参数
        NULL, NULL
    );
}
```

**代码说明**：
- 方法节点允许客户端调用服务器端函数
- `UA_Argument`: 定义方法的输入输出参数
- `UA_Server_addMethodNode()`: 添加方法节点
- 方法回调函数执行实际操作
- 可以有多个输入和输出参数

## 步骤6：开发OPC UA客户端

### 6.1 基础客户端连接

创建 `src/client_basic.c`：

```c
#include <open62541/client.h>
#include <open62541/client_config_default.h>
#include <open62541/plugin/log_stdout.h>

#include <stdlib.h>

int main(void) {
    // 创建客户端实例
    UA_Client *client = UA_Client_new();
    UA_ClientConfig_setDefault(UA_Client_getConfig(client));

    // 连接到服务器
    UA_StatusCode retval = UA_Client_connect(client, "opc.tcp://localhost:4840");
    if(retval != UA_STATUSCODE_GOOD) {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "连接失败: %s", UA_StatusCode_name(retval));
        UA_Client_delete(client);
        return EXIT_FAILURE;
    }

    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "连接成功");

    // 断开连接
    UA_Client_disconnect(client);
    UA_Client_delete(client);
    
    return EXIT_SUCCESS;
}
```

### 6.2 读取变量值

```c
// 读取单个变量
static void readVariable(UA_Client *client) {
    // 定义要读取的节点ID
    UA_NodeId nodeId = UA_NODEID_STRING(1, "Device1.Temperature");
    
    // 读取变量值
    UA_Variant value;
    UA_Variant_init(&value);
    UA_StatusCode retval = UA_Client_readValueAttribute(client, nodeId, &value);
    
    if(retval == UA_STATUSCODE_GOOD && 
       UA_Variant_hasScalarType(&value, &UA_TYPES[UA_TYPES_DOUBLE])) {
        UA_Double temperature = *(UA_Double*)value.data;
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "温度: %.2f°C", temperature);
    } else {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "读取失败: %s", UA_StatusCode_name(retval));
    }
    
    UA_Variant_clear(&value);
}

// 读取多个变量
static void readMultipleVariables(UA_Client *client) {
    // 定义要读取的节点
    UA_ReadValueId readIds[2];
    UA_ReadValueId_init(&readIds[0]);
    readIds[0].nodeId = UA_NODEID_STRING(1, "Device1.Temperature");
    readIds[0].attributeId = UA_ATTRIBUTEID_VALUE;
    
    UA_ReadValueId_init(&readIds[1]);
    readIds[1].nodeId = UA_NODEID_STRING(1, "Device1.Humidity");
    readIds[1].attributeId = UA_ATTRIBUTEID_VALUE;
    
    // 创建读取请求
    UA_ReadRequest request;
    UA_ReadRequest_init(&request);
    request.nodesToRead = readIds;
    request.nodesToReadSize = 2;
    
    // 发送请求
    UA_ReadResponse response = UA_Client_Service_read(client, request);
    
    // 处理响应
    if(response.responseHeader.serviceResult == UA_STATUSCODE_GOOD) {
        for(size_t i = 0; i < response.resultsSize; i++) {
            if(response.results[i].hasValue) {
                UA_Variant *value = &response.results[i].value;
                if(UA_Variant_hasScalarType(value, &UA_TYPES[UA_TYPES_DOUBLE])) {
                    UA_Double val = *(UA_Double*)value->data;
                    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                               "值[%zu]: %.2f", i, val);
                }
            }
        }
    }
    
    UA_ReadResponse_clear(&response);
}
```

### 6.3 写入变量值

```c
// 写入单个变量
static void writeVariable(UA_Client *client) {
    UA_NodeId nodeId = UA_NODEID_STRING(1, "Device1.Temperature");
    
    // 准备要写入的值
    UA_Double newTemperature = 28.5;
    UA_Variant value;
    UA_Variant_setScalar(&value, &newTemperature, &UA_TYPES[UA_TYPES_DOUBLE]);
    
    // 写入变量
    UA_StatusCode retval = UA_Client_writeValueAttribute(client, nodeId, &value);
    
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "写入成功: %.2f°C", newTemperature);
    } else {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "写入失败: %s", UA_StatusCode_name(retval));
    }
}

// 写入多个变量
static void writeMultipleVariables(UA_Client *client) {
    // 定义要写入的节点和值
    UA_WriteValue writeValues[2];
    
    UA_WriteValue_init(&writeValues[0]);
    writeValues[0].nodeId = UA_NODEID_STRING(1, "Device1.Temperature");
    writeValues[0].attributeId = UA_ATTRIBUTEID_VALUE;
    UA_Double temp = 26.0;
    UA_Variant_setScalar(&writeValues[0].value.value, &temp, 
                        &UA_TYPES[UA_TYPES_DOUBLE]);
    writeValues[0].value.hasValue = true;
    
    UA_WriteValue_init(&writeValues[1]);
    writeValues[1].nodeId = UA_NODEID_STRING(1, "Device1.Humidity");
    writeValues[1].attributeId = UA_ATTRIBUTEID_VALUE;
    UA_Double humi = 65.0;
    UA_Variant_setScalar(&writeValues[1].value.value, &humi, 
                        &UA_TYPES[UA_TYPES_DOUBLE]);
    writeValues[1].value.hasValue = true;
    
    // 创建写入请求
    UA_WriteRequest request;
    UA_WriteRequest_init(&request);
    request.nodesToWrite = writeValues;
    request.nodesToWriteSize = 2;
    
    // 发送请求
    UA_WriteResponse response = UA_Client_Service_write(client, request);
    
    // 检查结果
    if(response.responseHeader.serviceResult == UA_STATUSCODE_GOOD) {
        for(size_t i = 0; i < response.resultsSize; i++) {
            if(response.results[i] == UA_STATUSCODE_GOOD) {
                UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                           "写入[%zu]成功", i);
            }
        }
    }
    
    UA_WriteResponse_clear(&response);
}
```

### 6.4 调用方法

```c
// 调用无参数方法
static void callStartMethod(UA_Client *client) {
    UA_NodeId objectId = UA_NODEID_STRING(1, "Device1");
    UA_NodeId methodId = UA_NODEID_STRING(1, "Device1.Start");
    
    size_t outputSize;
    UA_Variant *output;
    
    // 调用方法
    UA_StatusCode retval = UA_Client_call(client, objectId, methodId,
                                          0, NULL,  // 无输入参数
                                          &outputSize, &output);
    
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "方法调用成功");
        
        // 处理输出参数
        if(outputSize > 0 && 
           UA_Variant_hasScalarType(&output[0], &UA_TYPES[UA_TYPES_DATETIME])) {
            UA_DateTime startTime = *(UA_DateTime*)output[0].data;
            UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                       "启动时间: %lld", startTime);
        }
        
        UA_Array_delete(output, outputSize, &UA_TYPES[UA_TYPES_VARIANT]);
    } else {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "方法调用失败: %s", UA_StatusCode_name(retval));
    }
}

// 调用带参数方法
static void callSetThresholdMethod(UA_Client *client) {
    UA_NodeId objectId = UA_NODEID_STRING(1, "Device1");
    UA_NodeId methodId = UA_NODEID_STRING(1, "Device1.SetThreshold");
    
    // 准备输入参数
    UA_Variant input[2];
    UA_Double minTemp = 15.0;
    UA_Double maxTemp = 35.0;
    UA_Variant_setScalar(&input[0], &minTemp, &UA_TYPES[UA_TYPES_DOUBLE]);
    UA_Variant_setScalar(&input[1], &maxTemp, &UA_TYPES[UA_TYPES_DOUBLE]);
    
    size_t outputSize;
    UA_Variant *output;
    
    // 调用方法
    UA_StatusCode retval = UA_Client_call(client, objectId, methodId,
                                          2, input,  // 2个输入参数
                                          &outputSize, &output);
    
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "设置阈值成功");
        
        // 处理输出参数
        if(outputSize > 0 && 
           UA_Variant_hasScalarType(&output[0], &UA_TYPES[UA_TYPES_BOOLEAN])) {
            UA_Boolean success = *(UA_Boolean*)output[0].data;
            UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                       "结果: %s", success ? "成功" : "失败");
        }
        
        UA_Array_delete(output, outputSize, &UA_TYPES[UA_TYPES_VARIANT]);
    }
}
```

### 6.5 订阅和监控

```c
// 订阅回调函数
static void
dataChangeNotificationCallback(UA_Client *client, UA_UInt32 subId, void *subContext,
                               UA_UInt32 monId, void *monContext,
                               UA_DataValue *value) {
    if(UA_Variant_hasScalarType(&value->value, &UA_TYPES[UA_TYPES_DOUBLE])) {
        UA_Double val = *(UA_Double*)value->value.data;
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "数据变化通知: %.2f", val);
    }
}

// 创建订阅
static void createSubscription(UA_Client *client) {
    // 创建订阅请求
    UA_CreateSubscriptionRequest request = UA_CreateSubscriptionRequest_default();
    request.requestedPublishingInterval = 500.0;  // 500ms发布间隔
    
    UA_CreateSubscriptionResponse response = 
        UA_Client_Subscriptions_create(client, request,
                                       NULL, NULL, NULL);
    
    if(response.responseHeader.serviceResult == UA_STATUSCODE_GOOD) {
        UA_UInt32 subId = response.subscriptionId;
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "订阅创建成功, ID: %u", subId);
        
        // 添加监控项
        UA_MonitoredItemCreateRequest monRequest =
            UA_MonitoredItemCreateRequest_default(
                UA_NODEID_STRING(1, "Device1.Temperature"));
        monRequest.requestedParameters.samplingInterval = 250.0;  // 250ms采样
        
        UA_MonitoredItemCreateResult monResponse =
            UA_Client_MonitoredItems_createDataChange(
                client, subId,
                UA_TIMESTAMPSTORETURN_BOTH,
                monRequest,
                NULL,  // 监控项上下文
                dataChangeNotificationCallback,  // 回调函数
                NULL   // 删除回调
            );
        
        if(monResponse.statusCode == UA_STATUSCODE_GOOD) {
            UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                       "监控项创建成功, ID: %u", monResponse.monitoredItemId);
        }
    }
}

// 客户端主循环（处理订阅通知）
int main(void) {
    UA_Client *client = UA_Client_new();
    UA_ClientConfig_setDefault(UA_Client_getConfig(client));

    UA_StatusCode retval = UA_Client_connect(client, "opc.tcp://localhost:4840");
    if(retval != UA_STATUSCODE_GOOD) {
        UA_Client_delete(client);
        return EXIT_FAILURE;
    }

    // 创建订阅
    createSubscription(client);

    // 运行客户端循环（接收订阅通知）
    for(int i = 0; i < 100; i++) {
        UA_Client_run_iterate(client, 100);  // 100ms超时
        // 这里会触发dataChangeNotificationCallback
    }

    UA_Client_disconnect(client);
    UA_Client_delete(client);
    
    return EXIT_SUCCESS;
}
```

**代码说明**：
- 订阅允许客户端接收数据变化通知
- `UA_Client_Subscriptions_create()`: 创建订阅
- `UA_Client_MonitoredItems_createDataChange()`: 添加监控项
- `dataChangeNotificationCallback`: 数据变化时调用
- `UA_Client_run_iterate()`: 处理订阅通知

### 6.6 浏览地址空间

```c
// 浏览节点
static void browseNode(UA_Client *client, UA_NodeId nodeId, int depth) {
    // 创建浏览请求
    UA_BrowseRequest bReq;
    UA_BrowseRequest_init(&bReq);
    bReq.requestedMaxReferencesPerNode = 0;
    bReq.nodesToBrowse = UA_BrowseDescription_new();
    bReq.nodesToBrowseSize = 1;
    bReq.nodesToBrowse[0].nodeId = nodeId;
    bReq.nodesToBrowse[0].resultMask = UA_BROWSERESULTMASK_ALL;
    
    // 发送浏览请求
    UA_BrowseResponse bResp = UA_Client_Service_browse(client, bReq);
    
    // 处理结果
    for(size_t i = 0; i < bResp.resultsSize; ++i) {
        for(size_t j = 0; j < bResp.results[i].referencesSize; ++j) {
            UA_ReferenceDescription *ref = &(bResp.results[i].references[j]);
            
            // 打印节点信息
            for(int k = 0; k < depth; k++)
                printf("  ");
            
            printf("├─ %.*s", (int)ref->browseName.name.length,
                   ref->browseName.name.data);
            
            // 打印节点类型
            switch(ref->nodeClass) {
                case UA_NODECLASS_OBJECT:
                    printf(" [Object]");
                    break;
                case UA_NODECLASS_VARIABLE:
                    printf(" [Variable]");
                    break;
                case UA_NODECLASS_METHOD:
                    printf(" [Method]");
                    break;
                default:
                    break;
            }
            printf("\n");
            
            // 递归浏览子节点（限制深度）
            if(depth < 3 && ref->nodeClass == UA_NODECLASS_OBJECT) {
                browseNode(client, ref->nodeId.nodeId, depth + 1);
            }
        }
    }
    
    UA_BrowseRequest_clear(&bReq);
    UA_BrowseResponse_clear(&bResp);
}

// 浏览整个地址空间
static void browseAddressSpace(UA_Client *client) {
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND, "浏览地址空间:");
    
    // 从Objects文件夹开始浏览
    UA_NodeId objectsFolder = UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER);
    browseNode(client, objectsFolder, 0);
}
```

## 步骤7：实现安全通信

### 7.1 生成证书

```bash
# 创建证书目录
mkdir -p certs

# 生成服务器证书
openssl req -x509 -newkey rsa:2048 -keyout certs/server_key.pem \
    -out certs/server_cert.pem -days 365 -nodes \
    -subj "/CN=OPC UA Server/O=MyCompany/C=CN"

# 生成客户端证书
openssl req -x509 -newkey rsa:2048 -keyout certs/client_key.pem \
    -out certs/client_cert.pem -days 365 -nodes \
    -subj "/CN=OPC UA Client/O=MyCompany/C=CN"

# 转换为DER格式（open62541需要）
openssl x509 -in certs/server_cert.pem -outform der -out certs/server_cert.der
openssl rsa -in certs/server_key.pem -outform der -out certs/server_key.der
openssl x509 -in certs/client_cert.pem -outform der -out certs/client_cert.der
openssl rsa -in certs/client_key.pem -outform der -out certs/client_key.der
```

### 7.2 配置安全服务器

```c
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>

// 加载证书文件
static UA_ByteString loadFile(const char *path) {
    UA_ByteString fileContents = UA_STRING_NULL;
    
    FILE *fp = fopen(path, "rb");
    if(!fp) {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "无法打开文件: %s", path);
        return fileContents;
    }
    
    fseek(fp, 0, SEEK_END);
    fileContents.length = (size_t)ftell(fp);
    fileContents.data = (UA_Byte*)UA_malloc(fileContents.length);
    
    fseek(fp, 0, SEEK_SET);
    size_t read = fread(fileContents.data, sizeof(UA_Byte), 
                       fileContents.length, fp);
    if(read != fileContents.length) {
        UA_ByteString_clear(&fileContents);
    }
    
    fclose(fp);
    return fileContents;
}

int main(void) {
    // 创建服务器
    UA_Server *server = UA_Server_new();
    
    // 加载证书和私钥
    UA_ByteString certificate = loadFile("certs/server_cert.der");
    UA_ByteString privateKey = loadFile("certs/server_key.der");
    
    if(certificate.length == 0 || privateKey.length == 0) {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "证书加载失败");
        UA_Server_delete(server);
        return EXIT_FAILURE;
    }
    
    // 配置安全端点
    UA_ServerConfig *config = UA_Server_getConfig(server);
    UA_StatusCode retval = 
        UA_ServerConfig_setDefaultWithSecurityPolicies(
            config,
            4840,
            &certificate, &privateKey,
            NULL, 0,  // 信任列表（可选）
            NULL, 0,  // 发行者列表（可选）
            NULL, 0   // 撤销列表（可选）
        );
    
    UA_ByteString_clear(&certificate);
    UA_ByteString_clear(&privateKey);
    
    if(retval != UA_STATUSCODE_GOOD) {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "安全配置失败: %s", UA_StatusCode_name(retval));
        UA_Server_delete(server);
        return EXIT_FAILURE;
    }
    
    // 启动服务器
    retval = UA_Server_run_startup(server);
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "安全服务器已启动");
        
        // 运行服务器
        volatile UA_Boolean running = true;
        while(running) {
            UA_Server_run_iterate(server, true);
        }
        
        UA_Server_run_shutdown(server);
    }
    
    UA_Server_delete(server);
    return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
```

### 7.3 配置安全客户端

```c
#include <open62541/client.h>
#include <open62541/client_config_default.h>
#include <open62541/plugin/log_stdout.h>

int main(void) {
    UA_Client *client = UA_Client_new();
    
    // 加载客户端证书
    UA_ByteString certificate = loadFile("certs/client_cert.der");
    UA_ByteString privateKey = loadFile("certs/client_key.der");
    
    // 配置安全连接
    UA_ClientConfig *config = UA_Client_getConfig(client);
    UA_StatusCode retval = 
        UA_ClientConfig_setDefaultEncryption(
            config,
            certificate, privateKey,
            NULL, 0,  // 信任的服务器证书
            NULL, 0   // 撤销列表
        );
    
    UA_ByteString_clear(&certificate);
    UA_ByteString_clear(&privateKey);
    
    if(retval != UA_STATUSCODE_GOOD) {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "安全配置失败");
        UA_Client_delete(client);
        return EXIT_FAILURE;
    }
    
    // 连接到安全端点
    retval = UA_Client_connect(client, "opc.tcp://localhost:4840");
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "安全连接成功");
        
        // 执行操作...
        
        UA_Client_disconnect(client);
    } else {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                    "连接失败: %s", UA_StatusCode_name(retval));
    }
    
    UA_Client_delete(client);
    return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
```

### 7.4 用户认证

```c
// 服务器端：配置用户认证
static UA_StatusCode
activateSession_default(UA_Server *server,
                       UA_AccessControl *ac,
                       const UA_EndpointDescription *endpointDescription,
                       const UA_ByteString *secureChannelRemoteCertificate,
                       const UA_NodeId *sessionId,
                       const UA_ExtensionObject *userIdentityToken,
                       void **sessionContext) {
    
    // 检查用户名密码
    if(userIdentityToken->encoding == UA_EXTENSIONOBJECT_DECODED) {
        if(userIdentityToken->content.decoded.type == 
           &UA_TYPES[UA_TYPES_USERNAMEIDENTITYTOKEN]) {
            
            UA_UserNameIdentityToken *userToken = 
                (UA_UserNameIdentityToken*)userIdentityToken->content.decoded.data;
            
            // 验证用户名和密码
            if(UA_String_equal(&userToken->userName, &UA_STRING("admin")) &&
               UA_String_equal(&userToken->password, &UA_STRING("password123"))) {
                UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                           "用户认证成功: admin");
                return UA_STATUSCODE_GOOD;
            }
        }
    }
    
    UA_LOG_WARNING(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                  "用户认证失败");
    return UA_STATUSCODE_BADUSERACCESSDENIED;
}

// 客户端：使用用户名密码连接
static void connectWithCredentials(UA_Client *client) {
    UA_ClientConfig *config = UA_Client_getConfig(client);
    
    // 设置用户名和密码
    UA_UserNameIdentityToken* identityToken = UA_UserNameIdentityToken_new();
    identityToken->userName = UA_STRING_ALLOC("admin");
    identityToken->password = UA_STRING_ALLOC("password123");
    
    UA_ExtensionObject_clear(&config->userIdentityToken);
    config->userIdentityToken.encoding = UA_EXTENSIONOBJECT_DECODED;
    config->userIdentityToken.content.decoded.type = 
        &UA_TYPES[UA_TYPES_USERNAMEIDENTITYTOKEN];
    config->userIdentityToken.content.decoded.data = identityToken;
    
    // 连接
    UA_StatusCode retval = UA_Client_connect(client, "opc.tcp://localhost:4840");
    if(retval == UA_STATUSCODE_GOOD) {
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                   "认证连接成功");
    }
}
```

## 步骤8：Python客户端开发

### 8.1 安装Python库

```bash
pip3 install opcua
```

### 8.2 Python客户端示例

创建 `client.py`：

```python
from opcua import Client
import time

# 连接到服务器
client = Client("opc.tcp://localhost:4840")

try:
    client.connect()
    print("连接成功")
    
    # 获取根节点
    root = client.get_root_node()
    print("根节点:", root)
    
    # 获取Objects节点
    objects = client.get_objects_node()
    print("Objects节点:", objects)
    
    # 浏览子节点
    print("\n浏览Objects下的节点:")
    for child in objects.get_children():
        print(f"  - {child.get_browse_name()}")
    
    # 读取变量
    temp_node = client.get_node("ns=1;s=Device1.Temperature")
    temperature = temp_node.get_value()
    print(f"\n当前温度: {temperature}°C")
    
    # 写入变量
    temp_node.set_value(27.5)
    print("温度已设置为: 27.5°C")
    
    # 再次读取确认
    new_temperature = temp_node.get_value()
    print(f"新温度: {new_temperature}°C")
    
    # 调用方法
    device_node = client.get_node("ns=1;s=Device1")
    start_method = device_node.get_child(["1:Start"])
    result = device_node.call_method(start_method)
    print(f"\n启动方法返回: {result}")
    
    # 调用带参数的方法
    set_threshold_method = device_node.get_child(["1:SetThreshold"])
    result = device_node.call_method(set_threshold_method, 15.0, 35.0)
    print(f"设置阈值返回: {result}")
    
finally:
    client.disconnect()
    print("\n已断开连接")
```

### 8.3 Python订阅示例

```python
from opcua import Client, ua

class SubHandler:
    """订阅处理器"""
    
    def datachange_notification(self, node, val, data):
        """数据变化通知"""
        print(f"数据变化: {node} = {val}")
    
    def event_notification(self, event):
        """事件通知"""
        print(f"事件: {event}")

# 连接到服务器
client = Client("opc.tcp://localhost:4840")

try:
    client.connect()
    print("连接成功")
    
    # 创建订阅
    handler = SubHandler()
    subscription = client.create_subscription(500, handler)
    print("订阅创建成功")
    
    # 添加监控项
    temp_node = client.get_node("ns=1;s=Device1.Temperature")
    humi_node = client.get_node("ns=1;s=Device1.Humidity")
    
    handle1 = subscription.subscribe_data_change(temp_node)
    handle2 = subscription.subscribe_data_change(humi_node)
    print("监控项已添加")
    
    # 运行一段时间接收通知
    print("\n等待数据变化通知（30秒）...")
    time.sleep(30)
    
    # 取消订阅
    subscription.unsubscribe(handle1)
    subscription.unsubscribe(handle2)
    subscription.delete()
    print("\n订阅已取消")
    
finally:
    client.disconnect()
    print("已断开连接")
```

### 8.4 Python服务器示例

```python
from opcua import Server
import time
import random

# 创建服务器
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
server.set_server_name("Python OPC UA Server")

# 设置命名空间
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# 获取Objects节点
objects = server.get_objects_node()

# 创建设备对象
device = objects.add_object(idx, "Device1")

# 添加变量
temperature = device.add_variable(idx, "Temperature", 25.0)
humidity = device.add_variable(idx, "Humidity", 60.0)

# 设置变量可写
temperature.set_writable()
humidity.set_writable()

# 添加方法
def start_device(parent):
    """启动设备方法"""
    print("设备启动")
    return [time.time()]

def stop_device(parent):
    """停止设备方法"""
    print("设备停止")
    return []

def set_threshold(parent, min_temp, max_temp):
    """设置阈值方法"""
    print(f"设置阈值: {min_temp} - {max_temp}")
    return [True]

# 添加方法节点
device.add_method(idx, "Start", start_device, [], [ua.VariantType.DateTime])
device.add_method(idx, "Stop", stop_device, [], [])
device.add_method(idx, "SetThreshold", set_threshold,
                 [ua.VariantType.Double, ua.VariantType.Double],
                 [ua.VariantType.Boolean])

# 启动服务器
server.start()
print("服务器已启动: opc.tcp://localhost:4840")

try:
    # 定期更新变量值
    while True:
        time.sleep(1)
        
        # 模拟传感器数据
        new_temp = 20.0 + random.uniform(0, 10)
        new_humi = 50.0 + random.uniform(0, 30)
        
        temperature.set_value(new_temp)
        humidity.set_value(new_humi)
        
        print(f"温度: {new_temp:.2f}°C, 湿度: {new_humi:.2f}%")

except KeyboardInterrupt:
    print("\n停止服务器...")
finally:
    server.stop()
    print("服务器已停止")
```

**代码说明**：
- Python opcua库提供了简洁的API
- 支持服务器和客户端开发
- 适合快速原型开发和测试
- 可以与C/C++服务器互操作

## 故障排除

### 问题1：连接失败

**可能原因**：
- 服务器未启动
- 端口被占用
- 防火墙阻止
- URL格式错误

**解决方法**：
1. 确认服务器正在运行
2. 检查端口4840是否被占用：`netstat -an | grep 4840`
3. 临时关闭防火墙测试
4. 验证URL格式：`opc.tcp://hostname:port`

### 问题2：证书验证失败

**可能原因**：
- 证书格式错误
- 证书过期
- 证书路径错误
- 信任列表未配置

**解决方法**：
1. 检查证书格式（DER格式）
2. 重新生成证书
3. 验证证书路径
4. 将服务器证书添加到客户端信任列表

### 问题3：节点ID不存在

**可能原因**：
- NodeId格式错误
- 命名空间索引错误
- 节点未创建

**解决方法**：
1. 使用UaExpert浏览地址空间，确认NodeId
2. 检查命名空间索引（ns=1表示自定义命名空间）
3. 确认节点已成功创建

### 问题4：订阅无数据

**可能原因**：
- 采样间隔过长
- 数据未变化
- 客户端未调用iterate
- 订阅被删除

**解决方法**：
1. 减小采样间隔
2. 确保数据在变化
3. 定期调用`UA_Client_run_iterate()`
4. 检查订阅状态

### 问题5：方法调用失败

**可能原因**：
- 方法不存在
- 参数类型错误
- 参数数量错误
- 权限不足

**解决方法**：
1. 确认方法NodeId正确
2. 检查输入参数类型和数量
3. 验证用户权限
4. 查看服务器日志

## 总结

通过本教程，你学习了：

- ✅ OPC UA的架构和核心概念
- ✅ 信息模型和地址空间的设计
- ✅ 使用open62541开发OPC UA服务器
- ✅ 创建对象、变量和方法节点
- ✅ 实现数据源回调和周期更新
- ✅ 开发OPC UA客户端进行读写和订阅
- ✅ 配置安全通信和用户认证
- ✅ 使用Python进行快速开发

**关键要点**：
- OPC UA是工业4.0的核心通信标准
- 面向对象的信息模型支持复杂数据结构
- 内置安全机制确保通信安全
- 订阅机制实现高效的数据监控
- 跨平台支持实现设备互联互通

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现自定义数据类型（结构体）
2. **挑战2**：创建历史数据访问功能
3. **挑战3**：实现报警和事件系统
4. **挑战4**：开发OPC UA网关（连接Modbus设备）
5. **挑战5**：实现冗余服务器配置

## 完整代码

完整的项目代码可以在GitHub上找到：

```text
GitHub仓库: https://github.com/embedded-knowledge/opcua-tutorial
```

项目包含：
- OPC UA服务器完整实现
- 多种客户端示例（C和Python）
- 安全配置示例
- 证书生成脚本
- Docker部署配置

## 下一步

建议继续学习：

- Modbus工业协议实战 - 学习传统工业协议
- MQTT协议应用开发 - 学习物联网通信
- 工业以太网技术 - 学习Profinet、EtherCAT
- 时间敏感网络(TSN) - 学习实时以太网

## 参考资料

1. **OPC Foundation官方文档**
   - https://opcfoundation.org/
   - OPC UA规范文档

2. **open62541文档**
   - https://www.open62541.org/
   - API参考和示例

3. **书籍推荐**
   - 《OPC Unified Architecture》by Wolfgang Mahnke
   - 《工业4.0与OPC UA》

4. **在线资源**
   - OPC UA在线培训课程
   - GitHub上的开源项目
   - Stack Overflow OPC UA标签

5. **工具和软件**
   - UaExpert (客户端工具)
   - UAModeler (信息模型设计)
   - Prosys OPC UA Simulation Server

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

**贡献**：欢迎提交Pull Request改进本教程！
