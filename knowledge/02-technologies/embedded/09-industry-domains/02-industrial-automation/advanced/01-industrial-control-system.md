---
title: "工业自动化控制系统项目：构建完整的PLC控制解决方案"
description: "通过完整的工业自动化控制系统项目，学习PLC编程、HMI开发、网络通信和系统集成，掌握从需求分析到系统部署的全流程开发技能"
slug: "industrial-control-system-project"

# 分类信息
domain: "行业领域"
module: "工业自动化"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - 工业控制
  - 自动化项目
  - PLC
  - HMI
  - SCADA
  - Modbus
prerequisites:
  - "01-plc-programming.md"
  - "02-industrial-protocols.md"
  - "01-scada-system.md"
  - "熟练掌握PLC编程"
  - "了解工业通信协议"
related_contents:
  - "02-industrial-robot.md"
  - "03-industry-4.0.md"

# 学习信息
estimated_time: 260
difficulty_score: 5

# 作者和版本
author: "嵌入式知识平台"
author_id: "embedded-platform"
created_at: "2024-01-15"
updated_at: "2024-01-15"
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
  - 工业控制系统
  - PLC项目
  - 自动化系统
  - HMI开发
  - SCADA集成
  - 工业通信
  - 系统集成
cover_image: "/images/domains/industry/industrial-control-system.jpg"

# 项目特定信息
project_type: "hardware"
repository: "https://github.com/embedded-platform/industrial-control-system"
demo_video: ""
---

# 工业自动化控制系统项目：构建完整的PLC控制解决方案

## 项目概述

### 项目简介

本项目将带你构建一个**完整的工业自动化控制系统**，模拟真实工厂的生产线控制场景。系统包括PLC控制器、HMI人机界面、SCADA监控系统、多种传感器和执行器，以及完整的网络通信架构。

**项目场景**：自动化装配生产线控制系统
- 物料输送带自动控制
- 机械手抓取和放置
- 产品质量检测
- 自动计数和分拣
- 故障报警和处理
- 数据采集和监控


**项目特色**：
- 真实工业场景模拟
- 完整的系统架构设计
- PLC梯形图编程实践
- HMI界面开发
- 工业通信协议应用
- SCADA系统集成
- 故障诊断和处理

### 项目演示

```
┌─────────────────────────────────────────────────────────────┐
│              工业自动化控制系统架构图                        │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────┐
    │         SCADA监控系统 (上位机)                │
    │  - 实时数据监控                               │
    │  - 历史数据记录                               │
    │  - 报警管理                                   │
    │  - 报表生成                                   │
    └──────────────────┬───────────────────────────┘
                       │ Ethernet/Modbus TCP
    ┌──────────────────┴───────────────────────────┐
    │         HMI触摸屏 (现场操作站)                │
    │  - 工艺流程显示                               │
    │  - 参数设置                                   │
    │  - 手动/自动切换                              │
    │  - 报警显示                                   │
    └──────────────────┬───────────────────────────┘
                       │ Modbus RTU/RS485
    ┌──────────────────┴───────────────────────────┐
    │         PLC控制器 (西门子S7-1200)             │
    │  - 逻辑控制                                   │
    │  - 数据处理                                   │
    │  - 通信管理                                   │
    └──────────────────┬───────────────────────────┘
                       │ I/O信号
    ┌──────────────────┴───────────────────────────┐
    │              现场设备层                       │
    ├───────────────────────────────────────────────┤
    │ 输入设备:                                     │
    │  - 启动/停止按钮                              │
    │  - 光电传感器                                 │
    │  - 接近开关                                   │
    │  - 压力传感器                                 │
    │  - 温度传感器                                 │
    │                                               │
    │ 输出设备:                                     │
    │  - 输送带电机                                 │
    │  - 机械手气缸                                 │
    │  - 指示灯                                     │
    │  - 蜂鸣器                                     │
    │  - 电磁阀                                     │
    └───────────────────────────────────────────────┘
```


### 学习目标

完成本项目后，你将掌握：

- [ ] **系统设计能力**：理解工业控制系统的整体架构和设计方法
- [ ] **PLC编程技能**：熟练使用梯形图编写复杂控制逻辑
- [ ] **HMI开发能力**：设计和实现人机交互界面
- [ ] **通信协议应用**：掌握Modbus等工业通信协议
- [ ] **SCADA集成**：实现上位机监控系统
- [ ] **故障诊断技能**：具备系统调试和故障排查能力
- [ ] **项目管理经验**：了解工业项目的完整开发流程

## 项目特点

- ✨ **真实场景**：模拟实际工厂生产线控制
- ✨ **完整流程**：从需求分析到系统部署的全过程
- ✨ **模块化设计**：清晰的功能模块划分
- ✨ **可扩展性**：易于添加新功能和设备
- ✨ **工业标准**：遵循工业自动化开发规范
- ✨ **实用性强**：可直接应用于实际项目

## 技术栈

### 硬件平台

**PLC控制器**：
- **型号**：西门子S7-1200 CPU 1214C DC/DC/DC
- **数字输入**：14点（24VDC）
- **数字输出**：10点（24VDC，0.5A）
- **模拟输入**：2路（0-10V）
- **通信接口**：以太网、RS485

**HMI触摸屏**：
- **型号**：西门子KTP700 Basic
- **尺寸**：7英寸TFT
- **分辨率**：800x480
- **通信**：以太网、Profinet

**传感器和执行器**：
- 光电传感器（NPN型）
- 接近开关（电感式）
- 压力传感器（4-20mA）
- 温度传感器（PT100）
- 三相异步电机（0.75kW）
- 气动执行器（双作用气缸）
- 电磁阀（24VDC）


### 软件工具

**PLC编程**：
- TIA Portal V16（西门子集成开发环境）
- STEP 7 Professional
- WinCC Basic（HMI组态软件）

**SCADA系统**：
- WinCC SCADA V7.5
- 或开源方案：ScadaBR、OpenSCADA

**通信工具**：
- Modbus Poll/Slave（Modbus测试工具）
- Wireshark（网络抓包分析）
- S7 Communication Library

**辅助工具**：
- CAD软件（电气原理图设计）
- 仿真软件（Factory I/O、PLCSim）

## 硬件清单

### 必需硬件

| 名称 | 型号/规格 | 数量 | 用途 | 参考价格 | 购买链接 |
|------|-----------|------|------|----------|----------|
| PLC控制器 | 西门子S7-1200 CPU 1214C | 1 | 主控制器 | ¥2,800 | [西门子官网] |
| HMI触摸屏 | 西门子KTP700 Basic | 1 | 人机界面 | ¥3,500 | [西门子官网] |
| 电源模块 | 24VDC 5A开关电源 | 1 | 系统供电 | ¥150 | [淘宝] |
| 光电传感器 | E3Z-D61 NPN | 4 | 物料检测 | ¥120 | [欧姆龙] |
| 接近开关 | LJ12A3-4-Z/BX | 4 | 位置检测 | ¥80 | [淘宝] |
| 压力传感器 | 0-1MPa 4-20mA | 2 | 压力监测 | ¥200 | [淘宝] |
| 温度传感器 | PT100 | 2 | 温度监测 | ¥100 | [淘宝] |
| 继电器模块 | 8路继电器模块 | 2 | 负载控制 | ¥120 | [淘宝] |
| 指示灯 | 24VDC LED指示灯 | 10 | 状态显示 | ¥50 | [淘宝] |
| 按钮开关 | LA38-11BN | 6 | 手动控制 | ¥60 | [淘宝] |
| 蜂鸣器 | 24VDC 85dB | 2 | 报警提示 | ¥30 | [淘宝] |
| 电磁阀 | 24VDC 二位五通 | 4 | 气路控制 | ¥200 | [淘宝] |
| 气缸 | 双作用气缸 Φ32×100 | 2 | 机械动作 | ¥300 | [淘宝] |
| 变频器 | 0.75kW 220V | 1 | 电机调速 | ¥500 | [淘宝] |
| 三相电机 | 0.75kW 380V | 1 | 输送带驱动 | ¥400 | [淘宝] |
| 导轨 | DIN导轨 1米 | 2 | 设备安装 | ¥40 | [淘宝] |
| 端子排 | UK-2.5B | 50 | 接线端子 | ¥50 | [淘宝] |
| 线缆 | 屏蔽双绞线 | 100米 | 信号连接 | ¥200 | [淘宝] |
| 控制柜 | 600×800×250mm | 1 | 设备安装 | ¥800 | [淘宝] |

**总成本**：约 ¥9,700

### 可选硬件

| 名称 | 型号/规格 | 数量 | 用途 | 参考价格 |
|------|-----------|------|------|----------|
| 扩展模块 | S7-1200 DI/DO模块 | 1 | I/O扩展 | ¥1,200 |
| 模拟量模块 | S7-1200 AI/AO模块 | 1 | 模拟量扩展 | ¥1,500 |
| 工业交换机 | 8口以太网交换机 | 1 | 网络通信 | ¥600 |
| UPS电源 | 1000VA | 1 | 不间断电源 | ¥800 |
| 编码器 | 增量式编码器 | 1 | 位置反馈 | ¥300 |
| 伺服电机 | 400W伺服系统 | 1 | 精确定位 | ¥2,500 |


## 软件要求

### 开发环境配置

**系统要求**：
- 操作系统：Windows 10 Professional 64位
- 处理器：Intel Core i5或更高
- 内存：8GB RAM（推荐16GB）
- 硬盘：100GB可用空间
- 显示器：1920x1080分辨率

**软件安装**：

```powershell
# 1. 安装TIA Portal V16
# 从西门子官网下载安装包
# 安装路径：C:\Program Files\Siemens\Automation\Portal V16

# 2. 安装WinCC SCADA
# 从西门子官网下载
# 需要授权许可证

# 3. 安装Modbus工具
# 下载Modbus Poll和Modbus Slave
# 用于通信测试

# 4. 安装仿真软件（可选）
# Factory I/O - 3D工厂仿真
# PLCSim Advanced - PLC仿真器
```

### 许可证要求

- TIA Portal Professional License
- WinCC Basic License（HMI开发）
- WinCC SCADA License（可选，用于上位机）

**注意**：可以使用试用版进行学习，正式项目需要购买授权。

## 系统架构

### 整体架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    管理层 (Management Layer)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SCADA监控系统 (WinCC SCADA)                         │   │
│  │  - 实时监控  - 历史趋势  - 报警管理  - 报表生成      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ Ethernet/Modbus TCP
┌─────────────────────────────────────────────────────────────┐
│                    监控层 (Supervision Layer)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HMI触摸屏 (KTP700)                                  │   │
│  │  - 工艺画面  - 参数设置  - 手动操作  - 报警显示      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ Profinet/Modbus RTU
┌─────────────────────────────────────────────────────────────┐
│                    控制层 (Control Layer)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PLC控制器 (S7-1200)                                 │   │
│  │  - 逻辑控制  - 数据处理  - 通信管理  - 故障诊断      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ I/O信号
┌─────────────────────────────────────────────────────────────┐
│                    现场层 (Field Layer)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  传感器      │  │  执行器      │  │  指示设备    │      │
│  │  - 光电      │  │  - 电机      │  │  - 指示灯    │      │
│  │  - 接近开关  │  │  - 气缸      │  │  - 蜂鸣器    │      │
│  │  - 压力      │  │  - 电磁阀    │  │  - 按钮      │      │
│  │  - 温度      │  │  - 变频器    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```


### 控制系统功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                    PLC控制程序结构                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  OB1 - 主循环程序                                  │    │
│  │  - 调用各功能块                                    │    │
│  │  - 扫描周期：10ms                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  FC1 - 输入处理│  │  FC2 - 输送带  │  │  FC3 - 机械手│ │
│  │  - 信号滤波    │  │  - 启停控制    │  │  - 动作控制  │ │
│  │  - 边沿检测    │  │  - 速度调节    │  │  - 位置检测  │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  FC4 - 质检    │  │  FC5 - 计数    │  │  FC6 - 分拣  │ │
│  │  - 质量检测    │  │  - 产品计数    │  │  - 分类控制  │ │
│  │  - 不良品剔除  │  │  - 批次管理    │  │  - 路径选择  │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  FC7 - 报警    │  │  FC8 - 通信    │  │  FC9 - 数据  │ │
│  │  - 故障检测    │  │  - Modbus通信  │  │  - 数据采集  │ │
│  │  - 报警处理    │  │  - 数据交换    │  │  - 历史记录  │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  DB1 - 全局数据块                                  │    │
│  │  - 系统参数  - 运行状态  - 计数器  - 报警信息      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### I/O地址分配表

**数字输入（DI）**：

| 地址 | 名称 | 说明 | 设备类型 |
|------|------|------|----------|
| I0.0 | START_BTN | 启动按钮 | 按钮开关 |
| I0.1 | STOP_BTN | 停止按钮 | 按钮开关 |
| I0.2 | RESET_BTN | 复位按钮 | 按钮开关 |
| I0.3 | EMERGENCY_STOP | 急停按钮 | 急停开关 |
| I0.4 | SENSOR_FEED_IN | 进料传感器 | 光电传感器 |
| I0.5 | SENSOR_POSITION_1 | 位置1传感器 | 接近开关 |
| I0.6 | SENSOR_POSITION_2 | 位置2传感器 | 接近开关 |
| I0.7 | SENSOR_POSITION_3 | 位置3传感器 | 接近开关 |
| I1.0 | SENSOR_QUALITY | 质检传感器 | 光电传感器 |
| I1.1 | SENSOR_FEED_OUT | 出料传感器 | 光电传感器 |
| I1.2 | ARM_HOME | 机械手原点 | 接近开关 |
| I1.3 | ARM_WORK | 机械手工作位 | 接近开关 |
| I1.4 | GRIPPER_OPEN | 夹爪打开到位 | 接近开关 |
| I1.5 | GRIPPER_CLOSE | 夹爪关闭到位 | 接近开关 |
| I1.6 | PRESSURE_ALARM | 压力报警 | 压力开关 |
| I1.7 | TEMP_ALARM | 温度报警 | 温度开关 |

**数字输出（DO）**：

| 地址 | 名称 | 说明 | 设备类型 |
|------|------|------|----------|
| Q0.0 | MOTOR_CONVEYOR | 输送带电机 | 继电器 |
| Q0.1 | MOTOR_FORWARD | 电机正转 | 继电器 |
| Q0.2 | MOTOR_REVERSE | 电机反转 | 继电器 |
| Q0.3 | VALVE_ARM_UP | 机械手上升 | 电磁阀 |
| Q0.4 | VALVE_ARM_DOWN | 机械手下降 | 电磁阀 |
| Q0.5 | VALVE_GRIPPER | 夹爪控制 | 电磁阀 |
| Q0.6 | VALVE_REJECT | 不良品剔除 | 电磁阀 |
| Q0.7 | VALVE_SORT_A | 分拣通道A | 电磁阀 |
| Q1.0 | VALVE_SORT_B | 分拣通道B | 电磁阀 |
| Q1.1 | LIGHT_RUN | 运行指示灯 | LED灯 |
| Q1.2 | LIGHT_STOP | 停止指示灯 | LED灯 |
| Q1.3 | LIGHT_ALARM | 报警指示灯 | LED灯 |
| Q1.4 | BUZZER | 蜂鸣器 | 蜂鸣器 |
| Q1.5 | FAN_COOLING | 冷却风扇 | 继电器 |

**模拟输入（AI）**：

| 地址 | 名称 | 说明 | 量程 | 设备类型 |
|------|------|------|------|----------|
| IW64 | PRESSURE_VALUE | 压力值 | 0-1MPa | 压力传感器 |
| IW66 | TEMP_VALUE | 温度值 | 0-100°C | 温度传感器 |

**模拟输出（AO）**：

| 地址 | 名称 | 说明 | 量程 | 设备类型 |
|------|------|------|------|----------|
| QW64 | SPEED_SETPOINT | 速度设定 | 0-100% | 变频器 |


## 实现步骤

### 阶段1：系统设计与规划 (预计30小时)

#### 1.1 需求分析

**功能需求**：

1. **自动运行模式**
   - 按下启动按钮，系统自动运行
   - 输送带启动，物料自动输送
   - 机械手自动抓取和放置
   - 质量检测自动进行
   - 不良品自动剔除
   - 产品自动计数和分拣

2. **手动运行模式**
   - 可单独控制各个执行器
   - 用于调试和维护
   - 具有安全联锁保护

3. **监控功能**
   - 实时显示系统状态
   - 显示生产数据（产量、良品率等）
   - 显示设备状态（温度、压力等）
   - 历史数据记录和查询

4. **报警功能**
   - 故障自动检测
   - 声光报警提示
   - 报警信息记录
   - 报警确认和复位

**性能需求**：
- PLC扫描周期：≤10ms
- 响应时间：≤100ms
- 系统可用率：≥99%
- 数据采集周期：1秒
- 历史数据保存：≥30天

**安全需求**：
- 急停功能
- 安全联锁
- 故障安全
- 权限管理

#### 1.2 系统架构设计

**电气原理图设计**：

```
主电路：
┌─────────────────────────────────────────────────────────┐
│  L1  L2  L3  N  PE                                      │
│   │   │   │   │   │                                     │
│   └───┴───┴───┴───┘                                     │
│         │                                                │
│    ┌────┴────┐                                          │
│    │  断路器  │  QF1  63A                               │
│    └────┬────┘                                          │
│         │                                                │
│    ┌────┴────┐                                          │
│    │  接触器  │  KM1  (主接触器)                        │
│    └────┬────┘                                          │
│         │                                                │
│    ┌────┴────┐                                          │
│    │  变频器  │  VFD1  0.75kW                           │
│    └────┬────┘                                          │
│         │                                                │
│    ┌────┴────┐                                          │
│    │  电机    │  M1  0.75kW                             │
│    └─────────┘                                          │
└─────────────────────────────────────────────────────────┘

控制电路：
┌─────────────────────────────────────────────────────────┐
│  24VDC电源                                               │
│   +24V  0V                                              │
│    │     │                                               │
│    ├─────┴──────┐                                       │
│    │   PLC电源   │                                       │
│    └─────┬──────┘                                       │
│          │                                               │
│    ┌─────┴──────┐                                       │
│    │  S7-1200   │                                       │
│    │  CPU 1214C │                                       │
│    │            │                                       │
│    │  DI: I0.0-I1.7                                    │
│    │  DO: Q0.0-Q1.5                                    │
│    │  AI: IW64, IW66                                   │
│    │  AO: QW64                                         │
│    │            │                                       │
│    │  Ethernet  │───> HMI / SCADA                      │
│    │  RS485     │───> 变频器 / 仪表                     │
│    └────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

#### 1.3 工艺流程设计

**生产线工艺流程**：

```
┌─────────────────────────────────────────────────────────┐
│                    工艺流程图                            │
└─────────────────────────────────────────────────────────┘

  [开始]
    │
    ↓
  [系统初始化]
    │
    ↓
  [等待启动信号]
    │
    ↓
  [启动输送带] ──────────────────┐
    │                            │
    ↓                            │
  [检测物料到达] ←────────────────┘
    │ 是                         │ 否：继续等待
    ↓                            │
  [停止输送带]                   │
    │                            │
    ↓                            │
  [机械手下降]                   │
    │                            │
    ↓                            │
  [夹爪夹紧]                     │
    │                            │
    ↓                            │
  [机械手上升]                   │
    │                            │
    ↓                            │
  [移动到检测位置]               │
    │                            │
    ↓                            │
  [质量检测] ──> [不良品?] ──是──> [剔除通道]
    │              │ 否            │
    ↓              ↓               ↓
  [移动到放置位]  [良品计数]    [不良品计数]
    │              │               │
    ↓              ↓               │
  [夹爪松开]      [分拣]          │
    │              │               │
    ↓              ↓               │
  [机械手返回原点] │               │
    │              │               │
    └──────────────┴───────────────┘
                   │
                   ↓
              [继续生产?] ──是──> [返回启动输送带]
                   │ 否
                   ↓
              [停止系统]
                   │
                   ↓
                [结束]
```


### 阶段2：PLC程序开发 (预计80小时)

#### 2.1 创建TIA Portal项目

**步骤**：

1. 打开TIA Portal V16
2. 创建新项目：`Industrial_Control_System`
3. 添加PLC设备：S7-1200 CPU 1214C DC/DC/DC
4. 配置设备参数：
   - IP地址：192.168.0.10
   - 子网掩码：255.255.255.0
   - 扫描周期：10ms

#### 2.2 主程序框架（OB1）

```
// OB1 - Main Program Organization Block
// 扫描周期：10ms

ORGANIZATION_BLOCK "Main"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

BEGIN
    // ========================================
    // 1. 输入信号处理
    // ========================================
    CALL "FC_Input_Processing";
    
    // ========================================
    // 2. 系统模式选择
    // ========================================
    IF "DB_Global".System.Mode = 0 THEN
        // 手动模式
        CALL "FC_Manual_Mode";
    ELSIF "DB_Global".System.Mode = 1 THEN
        // 自动模式
        CALL "FC_Auto_Mode";
    END_IF;
    
    // ========================================
    // 3. 输送带控制
    // ========================================
    CALL "FC_Conveyor_Control";
    
    // ========================================
    // 4. 机械手控制
    // ========================================
    CALL "FC_Robot_Arm_Control";
    
    // ========================================
    // 5. 质量检测
    // ========================================
    CALL "FC_Quality_Check";
    
    // ========================================
    // 6. 计数和分拣
    // ========================================
    CALL "FC_Counting_Sorting";
    
    // ========================================
    // 7. 报警处理
    // ========================================
    CALL "FC_Alarm_Handler";
    
    // ========================================
    // 8. 通信处理
    // ========================================
    CALL "FC_Communication";
    
    // ========================================
    // 9. 数据采集
    // ========================================
    CALL "FC_Data_Acquisition";
    
    // ========================================
    // 10. 输出信号处理
    // ========================================
    CALL "FC_Output_Processing";
    
END_ORGANIZATION_BLOCK
```

#### 2.3 全局数据块（DB1）

```
DATA_BLOCK "DB_Global"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN

STRUCT
    // ========================================
    // 系统状态
    // ========================================
    System : STRUCT
        Mode : INT;              // 0=手动, 1=自动
        State : INT;             // 0=停止, 1=运行, 2=暂停, 3=故障
        StartCmd : BOOL;         // 启动命令
        StopCmd : BOOL;          // 停止命令
        ResetCmd : BOOL;         // 复位命令
        EmergencyStop : BOOL;    // 急停状态
    END_STRUCT;
    
    // ========================================
    // 输送带状态
    // ========================================
    Conveyor : STRUCT
        Running : BOOL;          // 运行状态
        Speed : INT;             // 速度 (0-100%)
        Direction : BOOL;        // 方向 (0=正转, 1=反转)
        MaterialDetected : BOOL; // 物料检测
    END_STRUCT;
    
    // ========================================
    // 机械手状态
    // ========================================
    RobotArm : STRUCT
        State : INT;             // 0=原点, 1=下降, 2=夹紧, 3=上升, 4=移动, 5=松开
        AtHome : BOOL;           // 在原点
        AtWork : BOOL;           // 在工作位
        GripperOpen : BOOL;      // 夹爪打开
        GripperClose : BOOL;     // 夹爪关闭
    END_STRUCT;
    
    // ========================================
    // 生产数据
    // ========================================
    Production : STRUCT
        TotalCount : DINT;       // 总产量
        GoodCount : DINT;        // 良品数
        BadCount : DINT;         // 不良品数
        GoodRate : REAL;         // 良品率 (%)
        CycleTime : TIME;        // 节拍时间
    END_STRUCT;
    
    // ========================================
    // 传感器数据
    // ========================================
    Sensors : STRUCT
        Pressure : REAL;         // 压力值 (MPa)
        Temperature : REAL;      // 温度值 (°C)
        PressureAlarm : BOOL;    // 压力报警
        TempAlarm : BOOL;        // 温度报警
    END_STRUCT;
    
    // ========================================
    // 报警信息
    // ========================================
    Alarms : STRUCT
        Active : BOOL;           // 有报警
        EmergencyStop : BOOL;    // 急停报警
        ConveyorFault : BOOL;    // 输送带故障
        ArmFault : BOOL;         // 机械手故障
        SensorFault : BOOL;      // 传感器故障
        CommFault : BOOL;        // 通信故障
    END_STRUCT;
    
END_STRUCT;

BEGIN
    // 初始值
    System.Mode := 0;
    System.State := 0;
    Production.TotalCount := 0;
    Production.GoodCount := 0;
    Production.BadCount := 0;
END_DATA_BLOCK
```


#### 2.4 输入处理功能（FC1）

```
FUNCTION "FC_Input_Processing" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    EdgeDetect : BOOL;
END_VAR

BEGIN
    // ========================================
    // 按钮信号处理（边沿检测）
    // ========================================
    
    // 启动按钮
    IF "I0.0" AND NOT "DB_Global".System.StartCmd THEN
        "DB_Global".System.StartCmd := TRUE;
    ELSIF NOT "I0.0" THEN
        "DB_Global".System.StartCmd := FALSE;
    END_IF;
    
    // 停止按钮
    IF "I0.1" AND NOT "DB_Global".System.StopCmd THEN
        "DB_Global".System.StopCmd := TRUE;
    ELSIF NOT "I0.1" THEN
        "DB_Global".System.StopCmd := FALSE;
    END_IF;
    
    // 复位按钮
    IF "I0.2" AND NOT "DB_Global".System.ResetCmd THEN
        "DB_Global".System.ResetCmd := TRUE;
    ELSIF NOT "I0.2" THEN
        "DB_Global".System.ResetCmd := FALSE;
    END_IF;
    
    // 急停按钮（常闭触点，按下为FALSE）
    "DB_Global".System.EmergencyStop := NOT "I0.3";
    
    // ========================================
    // 传感器信号处理
    // ========================================
    
    // 物料检测传感器
    "DB_Global".Conveyor.MaterialDetected := "I0.4";
    
    // 机械手位置传感器
    "DB_Global".RobotArm.AtHome := "I1.2";
    "DB_Global".RobotArm.AtWork := "I1.3";
    "DB_Global".RobotArm.GripperOpen := "I1.4";
    "DB_Global".RobotArm.GripperClose := "I1.5";
    
    // ========================================
    // 模拟量输入处理
    // ========================================
    
    // 压力传感器 (0-27648 对应 0-1MPa)
    "DB_Global".Sensors.Pressure := 
        NORM_X(
            MIN := 0,
            VALUE := "IW64",
            MAX := 27648
        );
    
    // 温度传感器 (0-27648 对应 0-100°C)
    "DB_Global".Sensors.Temperature := 
        SCALE_X(
            MIN := 0.0,
            VALUE := NORM_X(
                MIN := 0,
                VALUE := "IW66",
                MAX := 27648
            ),
            MAX := 100.0
        );
    
    // 报警阈值检测
    "DB_Global".Sensors.PressureAlarm := 
        "DB_Global".Sensors.Pressure > 0.8;  // 压力超过0.8MPa报警
    
    "DB_Global".Sensors.TempAlarm := 
        "DB_Global".Sensors.Temperature > 80.0;  // 温度超过80°C报警
    
END_FUNCTION
```

#### 2.5 输送带控制功能（FC2）

```
FUNCTION "FC_Conveyor_Control" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    SpeedSetpoint : INT;
END_VAR

BEGIN
    // ========================================
    // 输送带启停控制
    // ========================================
    
    // 自动模式下的输送带控制
    IF "DB_Global".System.Mode = 1 AND 
       "DB_Global".System.State = 1 THEN
        
        // 如果没有检测到物料，启动输送带
        IF NOT "DB_Global".Conveyor.MaterialDetected THEN
            "DB_Global".Conveyor.Running := TRUE;
        ELSE
            // 检测到物料，停止输送带
            "DB_Global".Conveyor.Running := FALSE;
        END_IF;
        
    // 手动模式下的输送带控制
    ELSIF "DB_Global".System.Mode = 0 THEN
        // 手动控制逻辑（由HMI控制）
        // "DB_Global".Conveyor.Running 由HMI设置
    ELSE
        // 其他情况停止输送带
        "DB_Global".Conveyor.Running := FALSE;
    END_IF;
    
    // 急停时强制停止
    IF "DB_Global".System.EmergencyStop THEN
        "DB_Global".Conveyor.Running := FALSE;
    END_IF;
    
    // ========================================
    // 输出控制
    // ========================================
    
    // 输送带电机控制
    "Q0.0" := "DB_Global".Conveyor.Running;
    
    // 方向控制
    IF "DB_Global".Conveyor.Direction THEN
        "Q0.1" := FALSE;  // 正转
        "Q0.2" := TRUE;   // 反转
    ELSE
        "Q0.1" := TRUE;   // 正转
        "Q0.2" := FALSE;  // 反转
    END_IF;
    
    // ========================================
    // 速度控制（模拟量输出到变频器）
    // ========================================
    
    IF "DB_Global".Conveyor.Running THEN
        SpeedSetpoint := "DB_Global".Conveyor.Speed;
    ELSE
        SpeedSetpoint := 0;
    END_IF;
    
    // 转换为模拟量输出 (0-27648 对应 0-100%)
    "QW64" := SCALE_X(
        MIN := 0,
        VALUE := INT_TO_REAL(SpeedSetpoint) / 100.0,
        MAX := 27648
    );
    
END_FUNCTION
```


#### 2.6 机械手控制功能（FC3）

```
FUNCTION "FC_Robot_Arm_Control" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    Timer_Down : TON;
    Timer_Grip : TON;
    Timer_Up : TON;
    Timer_Move : TON;
    Timer_Release : TON;
END_VAR

VAR STAT
    Step : INT := 0;  // 步骤：0=待机, 1=下降, 2=夹紧, 3=上升, 4=移动, 5=松开, 6=返回
    StepTimer : TON;
END_VAR

BEGIN
    // ========================================
    // 自动模式下的机械手顺序控制
    // ========================================
    
    IF "DB_Global".System.Mode = 1 AND 
       "DB_Global".System.State = 1 THEN
        
        CASE Step OF
            0:  // 待机状态，等待物料
                IF "DB_Global".Conveyor.MaterialDetected AND
                   NOT "DB_Global".Conveyor.Running THEN
                    Step := 1;  // 开始下降
                END_IF;
                
            1:  // 机械手下降
                "Q0.3" := FALSE;  // 停止上升
                "Q0.4" := TRUE;   // 开始下降
                
                // 等待下降到位（检测工作位传感器）
                IF "DB_Global".RobotArm.AtWork THEN
                    "Q0.4" := FALSE;  // 停止下降
                    Step := 2;        // 进入夹紧步骤
                END_IF;
                
            2:  // 夹爪夹紧
                "Q0.5" := TRUE;  // 夹爪夹紧
                
                // 延时确认夹紧（500ms）
                StepTimer(IN := TRUE, PT := T#500MS);
                IF StepTimer.Q THEN
                    StepTimer(IN := FALSE);
                    Step := 3;  // 进入上升步骤
                END_IF;
                
            3:  // 机械手上升
                "Q0.3" := TRUE;   // 开始上升
                "Q0.4" := FALSE;  // 停止下降
                
                // 等待上升到原点
                IF "DB_Global".RobotArm.AtHome THEN
                    "Q0.3" := FALSE;  // 停止上升
                    Step := 4;        // 进入质检步骤
                END_IF;
                
            4:  // 质量检测
                // 调用质量检测功能
                CALL "FC_Quality_Check";
                
                // 延时等待检测结果（1秒）
                StepTimer(IN := TRUE, PT := T#1S);
                IF StepTimer.Q THEN
                    StepTimer(IN := FALSE);
                    Step := 5;  // 进入放置步骤
                END_IF;
                
            5:  // 移动到放置位置并松开
                // 根据质检结果选择放置位置
                IF "DB_Global".Production.LastCheckResult THEN
                    // 良品，放到分拣通道A
                    "Q0.7" := TRUE;
                    "Q1.0" := FALSE;
                ELSE
                    // 不良品，放到分拣通道B（剔除）
                    "Q0.7" := FALSE;
                    "Q1.0" := TRUE;
                END_IF;
                
                // 松开夹爪
                "Q0.5" := FALSE;
                
                // 延时确认松开（500ms）
                StepTimer(IN := TRUE, PT := T#500MS);
                IF StepTimer.Q THEN
                    StepTimer(IN := FALSE);
                    Step := 6;  // 返回原点
                END_IF;
                
            6:  // 返回原点
                "Q0.7" := FALSE;
                "Q1.0" := FALSE;
                
                // 确认已在原点
                IF "DB_Global".RobotArm.AtHome THEN
                    Step := 0;  // 返回待机状态
                    
                    // 重新启动输送带
                    "DB_Global".Conveyor.Running := TRUE;
                END_IF;
                
        END_CASE;
        
        // 更新机械手状态
        "DB_Global".RobotArm.State := Step;
        
    // 手动模式
    ELSIF "DB_Global".System.Mode = 0 THEN
        // 手动控制由HMI直接控制输出
        // 这里只更新状态
        Step := 0;
        
    ELSE
        // 停止状态，复位所有输出
        "Q0.3" := FALSE;
        "Q0.4" := FALSE;
        "Q0.5" := FALSE;
        "Q0.7" := FALSE;
        "Q1.0" := FALSE;
        Step := 0;
    END_IF;
    
    // 急停时强制停止所有动作
    IF "DB_Global".System.EmergencyStop THEN
        "Q0.3" := FALSE;
        "Q0.4" := FALSE;
        "Q0.5" := FALSE;
        "Q0.7" := FALSE;
        "Q1.0" := FALSE;
        Step := 0;
    END_IF;
    
END_FUNCTION
```

#### 2.7 质量检测功能（FC4）

```
FUNCTION "FC_Quality_Check" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    QualityOK : BOOL;
END_VAR

BEGIN
    // ========================================
    // 质量检测逻辑
    // ========================================
    
    // 读取质检传感器
    QualityOK := "I1.0";  // 质检传感器信号
    
    // 保存检测结果
    "DB_Global".Production.LastCheckResult := QualityOK;
    
    // 如果是不良品，触发剔除
    IF NOT QualityOK THEN
        "Q0.6" := TRUE;  // 剔除阀动作
        
        // 延时复位（200ms）
        // 使用定时器实现
    ELSE
        "Q0.6" := FALSE;
    END_IF;
    
END_FUNCTION
```

#### 2.8 计数和分拣功能（FC5）

```
FUNCTION "FC_Counting_Sorting" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    CountTrigger : BOOL;
END_VAR

VAR STAT
    LastCheckResult : BOOL := FALSE;
    CountDone : BOOL := FALSE;
END_VAR

BEGIN
    // ========================================
    // 产品计数
    // ========================================
    
    // 检测到新的检测结果
    IF "DB_Global".Production.LastCheckResult <> LastCheckResult AND
       NOT CountDone THEN
        
        // 总产量加1
        "DB_Global".Production.TotalCount := 
            "DB_Global".Production.TotalCount + 1;
        
        // 根据质检结果分类计数
        IF "DB_Global".Production.LastCheckResult THEN
            // 良品计数
            "DB_Global".Production.GoodCount := 
                "DB_Global".Production.GoodCount + 1;
        ELSE
            // 不良品计数
            "DB_Global".Production.BadCount := 
                "DB_Global".Production.BadCount + 1;
        END_IF;
        
        CountDone := TRUE;
    END_IF;
    
    // 复位计数标志
    IF "DB_Global".RobotArm.State = 0 THEN
        CountDone := FALSE;
    END_IF;
    
    // 更新上次检测结果
    LastCheckResult := "DB_Global".Production.LastCheckResult;
    
    // ========================================
    // 计算良品率
    // ========================================
    
    IF "DB_Global".Production.TotalCount > 0 THEN
        "DB_Global".Production.GoodRate := 
            INT_TO_REAL("DB_Global".Production.GoodCount) / 
            INT_TO_REAL("DB_Global".Production.TotalCount) * 100.0;
    ELSE
        "DB_Global".Production.GoodRate := 0.0;
    END_IF;
    
END_FUNCTION
```


#### 2.9 报警处理功能（FC7）

```
FUNCTION "FC_Alarm_Handler" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    AnyAlarm : BOOL;
END_VAR

BEGIN
    // ========================================
    // 报警检测
    // ========================================
    
    // 急停报警
    "DB_Global".Alarms.EmergencyStop := "DB_Global".System.EmergencyStop;
    
    // 输送带故障（运行命令发出但未检测到运行）
    "DB_Global".Alarms.ConveyorFault := 
        "DB_Global".Conveyor.Running AND NOT "Q0.0";
    
    // 机械手故障（动作超时）
    // 这里简化处理，实际应该有超时检测
    "DB_Global".Alarms.ArmFault := FALSE;
    
    // 传感器故障
    "DB_Global".Alarms.SensorFault := 
        "DB_Global".Sensors.PressureAlarm OR 
        "DB_Global".Sensors.TempAlarm;
    
    // 通信故障（由通信功能块设置）
    // "DB_Global".Alarms.CommFault 由FC8设置
    
    // ========================================
    // 报警汇总
    // ========================================
    
    AnyAlarm := 
        "DB_Global".Alarms.EmergencyStop OR
        "DB_Global".Alarms.ConveyorFault OR
        "DB_Global".Alarms.ArmFault OR
        "DB_Global".Alarms.SensorFault OR
        "DB_Global".Alarms.CommFault;
    
    "DB_Global".Alarms.Active := AnyAlarm;
    
    // ========================================
    // 报警输出
    // ========================================
    
    // 报警指示灯（闪烁）
    IF AnyAlarm THEN
        "Q1.3" := TRUE;  // 报警灯亮
        
        // 蜂鸣器（间歇鸣叫）
        // 使用时钟脉冲实现闪烁
        "Q1.4" := "Clock_1Hz";
    ELSE
        "Q1.3" := FALSE;
        "Q1.4" := FALSE;
    END_IF;
    
    // ========================================
    // 报警处理
    // ========================================
    
    // 有报警时，系统进入故障状态
    IF AnyAlarm AND "DB_Global".System.State <> 3 THEN
        "DB_Global".System.State := 3;  // 故障状态
    END_IF;
    
    // 复位按钮清除报警
    IF "DB_Global".System.ResetCmd AND NOT AnyAlarm THEN
        "DB_Global".System.State := 0;  // 返回停止状态
    END_IF;
    
END_FUNCTION
```

### 阶段3：HMI界面开发 (预计60小时)

#### 3.1 创建HMI项目

**步骤**：

1. 在TIA Portal中添加HMI设备：KTP700 Basic
2. 配置HMI参数：
   - IP地址：192.168.0.20
   - 连接到PLC：192.168.0.10
3. 创建HMI变量连接

#### 3.2 主画面设计

**主画面布局**：

```
┌─────────────────────────────────────────────────────────────┐
│  工业自动化控制系统                    2024-01-15 14:30:25  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              工艺流程图                               │  │
│  │                                                        │  │
│  │   [进料] → [输送带] → [机械手] → [检测] → [分拣]    │  │
│  │     ●        ━━━━       ╔═╗       ◉        ⇓⇓      │  │
│  │                         ║ ║                          │  │
│  │                         ╚═╝                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 系统状态     │  │ 生产数据     │  │ 设备状态     │     │
│  │              │  │              │  │              │     │
│  │ 运行模式:    │  │ 总产量: 1250 │  │ 压力: 0.65MPa│     │
│  │  ● 自动      │  │ 良品: 1200   │  │ 温度: 45°C   │     │
│  │  ○ 手动      │  │ 不良品: 50   │  │ 速度: 80%    │     │
│  │              │  │ 良品率: 96%  │  │              │     │
│  │ 运行状态:    │  │              │  │ 状态: 正常   │     │
│  │  ● 运行中    │  │ 节拍: 12s    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [启动]  [停止]  [复位]  [参数]  [报警]  [趋势]     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3 HMI变量配置

**变量连接表**：

| HMI变量名 | PLC地址 | 数据类型 | 说明 |
|-----------|---------|----------|------|
| SystemMode | DB1.DBW0 | INT | 系统模式 |
| SystemState | DB1.DBW2 | INT | 系统状态 |
| StartCmd | DB1.DBX4.0 | BOOL | 启动命令 |
| StopCmd | DB1.DBX4.1 | BOOL | 停止命令 |
| ResetCmd | DB1.DBX4.2 | BOOL | 复位命令 |
| TotalCount | DB1.DBD20 | DINT | 总产量 |
| GoodCount | DB1.DBD24 | DINT | 良品数 |
| BadCount | DB1.DBD28 | DINT | 不良品数 |
| GoodRate | DB1.DBD32 | REAL | 良品率 |
| Pressure | DB1.DBD40 | REAL | 压力值 |
| Temperature | DB1.DBD44 | REAL | 温度值 |
| ConveyorSpeed | DB1.DBW10 | INT | 输送带速度 |

#### 3.4 按钮和指示灯配置

**启动按钮**：
- 类型：按钮
- 功能：按下时设置StartCmd为TRUE
- 颜色：绿色
- 使能条件：SystemState = 0（停止状态）

**停止按钮**：
- 类型：按钮
- 功能：按下时设置StopCmd为TRUE
- 颜色：红色
- 使能条件：SystemState = 1（运行状态）

**状态指示灯**：
- 运行指示：SystemState = 1时绿色闪烁
- 停止指示：SystemState = 0时灰色
- 故障指示：SystemState = 3时红色闪烁


### 阶段4：通信集成 (预计40小时)

#### 4.1 Modbus TCP通信配置

**PLC端配置**：

```
FUNCTION "FC_Communication" : VOID
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_TEMP
    MB_Server : MB_SERVER;
    MB_Client : MB_CLIENT;
END_VAR

BEGIN
    // ========================================
    // Modbus TCP服务器配置
    // ========================================
    
    // 配置Modbus服务器，监听502端口
    MB_Server(
        InterfaceId := #HW_ID_Ethernet,
        Timeout := T#5s,
        Connect := TRUE,
        Disconnect := FALSE
    );
    
    // 映射Modbus寄存器到PLC变量
    // 保持寄存器 40001-40100 映射到DB1
    
    // ========================================
    // Modbus寄存器映射表
    // ========================================
    // 40001: 系统模式
    // 40002: 系统状态
    // 40003: 输送带速度
    // 40011-40012: 总产量 (DINT)
    // 40013-40014: 良品数 (DINT)
    // 40015-40016: 不良品数 (DINT)
    // 40017-40018: 良品率 (REAL)
    // 40021-40022: 压力值 (REAL)
    // 40023-40024: 温度值 (REAL)
    
END_FUNCTION
```

#### 4.2 SCADA系统通信

**WinCC SCADA配置**：

1. **创建通信驱动**
   - 驱动类型：Simatic S7 Protocol Suite
   - 连接类型：TCP/IP
   - PLC地址：192.168.0.10
   - 机架：0，插槽：1

2. **变量配置**
   ```
   变量名称          PLC地址        数据类型    采集周期
   ─────────────────────────────────────────────────────
   SystemMode        DB1.DBW0       INT         1s
   SystemState       DB1.DBW2       INT         1s
   TotalCount        DB1.DBD20      DINT        1s
   GoodCount         DB1.DBD24      DINT        1s
   BadCount          DB1.DBD28      DINT        1s
   GoodRate          DB1.DBD32      REAL        1s
   Pressure          DB1.DBD40      REAL        1s
   Temperature       DB1.DBD44      REAL        1s
   ConveyorSpeed     DB1.DBW10      INT         1s
   AlarmActive       DB1.DBX60.0    BOOL        500ms
   ```

3. **历史数据归档**
   - 归档周期：1秒
   - 保存时间：30天
   - 归档变量：生产数据、传感器数据

### 阶段5：SCADA监控系统开发 (预计50小时)

#### 5.1 SCADA主画面设计

**画面布局**：

```
┌─────────────────────────────────────────────────────────────┐
│  工业自动化控制系统 SCADA                  [最小化] [关闭]  │
├─────────────────────────────────────────────────────────────┤
│  [主画面] [趋势] [报警] [报表] [设置]                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              实时工艺流程图                           │  │
│  │                                                        │  │
│  │   ┌────┐    ┌──────┐    ┌──────┐    ┌──────┐        │  │
│  │   │进料│───>│输送带│───>│机械手│───>│检测  │        │  │
│  │   └────┘    └──────┘    └──────┘    └──────┘        │  │
│  │     ●         ━━━━        ╔═╗         ◉             │  │
│  │   运行中      80%         工作中      良品           │  │
│  │                                                        │  │
│  │                           ↓                           │  │
│  │                      ┌──────┐                        │  │
│  │                      │分拣  │                        │  │
│  │                      └──────┘                        │  │
│  │                       ⇓    ⇓                         │  │
│  │                     良品  不良品                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 生产统计     │  │ 设备监控     │  │ 报警信息     │     │
│  │              │  │              │  │              │     │
│  │ 今日产量:    │  │ 压力:        │  │ 当前报警: 0  │     │
│  │   1250 件    │  │   0.65 MPa   │  │              │     │
│  │              │  │              │  │ 历史报警:    │     │
│  │ 良品率:      │  │ 温度:        │  │   查看详情   │     │
│  │   96.0 %     │  │   45 °C      │  │              │     │
│  │              │  │              │  │              │     │
│  │ 运行时间:    │  │ 输送带速度:  │  │              │     │
│  │   6h 32m     │  │   80 %       │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  实时趋势图 - 生产效率                                │  │
│  │  100% ┤                                               │  │
│  │   80% ┤     ╱‾‾‾╲                                    │  │
│  │   60% ┤    ╱     ╲    ╱‾‾╲                          │  │
│  │   40% ┤   ╱       ╲  ╱    ╲                         │  │
│  │   20% ┤  ╱         ╲╱      ╲                        │  │
│  │    0% ┼──────────────────────────────────────────>   │  │
│  │       10:00  11:00  12:00  13:00  14:00  15:00      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2 趋势图配置

**实时趋势**：
- 变量：生产效率、良品率、设备温度、压力
- 时间范围：最近1小时
- 刷新周期：1秒
- 颜色：
  - 生产效率：蓝色
  - 良品率：绿色
  - 温度：红色
  - 压力：橙色

**历史趋势**：
- 数据源：历史归档数据库
- 时间范围：可选（1小时、8小时、24小时、7天、30天）
- 支持缩放和平移
- 支持数据导出

#### 5.3 报警系统配置

**报警类别**：

| 报警类型 | 优先级 | 颜色 | 声音 | 说明 |
|----------|--------|------|------|------|
| 急停报警 | 紧急 | 红色 | 连续 | 急停按钮被按下 |
| 设备故障 | 高 | 红色 | 间歇 | 设备运行异常 |
| 传感器报警 | 中 | 黄色 | 单次 | 传感器超限 |
| 通信故障 | 中 | 黄色 | 单次 | 通信中断 |
| 质量报警 | 低 | 蓝色 | 无 | 不良品率超标 |

**报警处理流程**：
1. 报警产生 → 记录到数据库
2. 显示在报警列表
3. 声光提示
4. 发送通知（可选：邮件、短信）
5. 操作员确认
6. 报警消除 → 记录消除时间和操作员

#### 5.4 报表系统

**日报表**：
- 生产总量
- 良品数量和良品率
- 不良品数量和不良品率
- 设备运行时间
- 停机时间和原因
- 报警统计

**月报表**：
- 月度生产统计
- 设备效率分析
- 质量趋势分析
- 故障统计分析

**报表导出**：
- 格式：PDF、Excel、CSV
- 自动生成：每日凌晨自动生成前一天报表
- 手动生成：支持任意时间段报表生成


### 阶段6：系统集成与测试 (预计40小时)

#### 6.1 硬件接线

**电源接线**：
```
AC 220V ──> 开关电源 ──> DC 24V
                │
                ├──> PLC电源 (24VDC)
                ├──> 传感器电源 (24VDC)
                ├──> 执行器电源 (24VDC)
                └──> HMI电源 (24VDC)
```

**PLC输入接线**：
```
传感器/按钮 ──> PLC输入端子
              (共阳极接法)

+24V ──┬──> 传感器1 ──> I0.0
       ├──> 传感器2 ──> I0.1
       ├──> 按钮1   ──> I0.2
       └──> ...

0V ──> PLC COM端子
```

**PLC输出接线**：
```
PLC输出端子 ──> 继电器/执行器

Q0.0 ──> 继电器1 ──> 电机1
Q0.1 ──> 继电器2 ──> 电机2
Q0.2 ──> 电磁阀1
Q0.3 ──> 电磁阀2
...

+24V ──> 执行器公共端
```

**网络接线**：
```
PLC (192.168.0.10) ──┐
                     ├──> 交换机 ──> 上位机
HMI (192.168.0.20) ──┘
```

#### 6.2 系统调试步骤

**步骤1：硬件检查**
- [ ] 检查所有接线是否正确
- [ ] 检查电源电压是否正常
- [ ] 检查传感器工作是否正常
- [ ] 检查执行器动作是否正常
- [ ] 检查网络连接是否正常

**步骤2：PLC程序下载**
- [ ] 连接PLC
- [ ] 下载程序到PLC
- [ ] 切换PLC到RUN模式
- [ ] 在线监控程序运行

**步骤3：I/O测试**
- [ ] 测试所有输入点
- [ ] 测试所有输出点
- [ ] 测试模拟量输入
- [ ] 测试模拟量输出

**步骤4：功能测试**
- [ ] 测试手动模式各功能
- [ ] 测试自动模式运行
- [ ] 测试急停功能
- [ ] 测试报警功能
- [ ] 测试计数功能

**步骤5：HMI测试**
- [ ] 下载HMI程序
- [ ] 测试画面切换
- [ ] 测试按钮功能
- [ ] 测试数据显示
- [ ] 测试参数设置

**步骤6：通信测试**
- [ ] 测试PLC与HMI通信
- [ ] 测试PLC与SCADA通信
- [ ] 测试Modbus通信
- [ ] 测试数据采集

**步骤7：系统联调**
- [ ] 完整流程测试
- [ ] 连续运行测试
- [ ] 异常情况测试
- [ ] 性能测试

#### 6.3 常见问题排查

**问题1：PLC无法通信**
- 检查网络连接
- 检查IP地址配置
- 检查防火墙设置
- 使用ping命令测试连通性

**问题2：输入信号不稳定**
- 检查传感器电源
- 检查接线是否松动
- 添加软件滤波
- 检查传感器是否损坏

**问题3：输出不动作**
- 检查输出继电器
- 检查负载电源
- 检查程序逻辑
- 使用强制功能测试

**问题4：机械手动作不到位**
- 检查气压是否足够
- 检查电磁阀是否正常
- 检查气缸是否卡死
- 调整延时时间

**问题5：通信超时**
- 检查网络质量
- 调整超时时间
- 检查通信参数
- 减少通信频率

## 项目扩展

### 扩展功能1：远程监控

**实现方案**：
- 使用VPN或工业网关实现远程访问
- 开发Web版SCADA系统
- 支持手机APP监控
- 实现远程故障诊断

**技术要点**：
- 网络安全（VPN、防火墙）
- 数据加密传输
- 用户权限管理
- 实时数据推送

### 扩展功能2：数据分析

**实现方案**：
- 将生产数据导入数据库
- 使用Python进行数据分析
- 生成可视化报表
- 预测性维护

**分析内容**：
- 设备效率分析（OEE）
- 质量趋势分析
- 故障模式分析
- 能耗分析

### 扩展功能3：MES集成

**实现方案**：
- 与MES系统对接
- 接收生产订单
- 上报生产数据
- 质量追溯

**集成接口**：
- OPC UA
- RESTful API
- 数据库直连
- 消息队列（MQTT）

### 扩展功能4：AI质检

**实现方案**：
- 使用工业相机采集图像
- 部署深度学习模型
- 实时质量检测
- 缺陷分类

**技术栈**：
- OpenCV（图像处理）
- TensorFlow/PyTorch（深度学习）
- 边缘计算设备（Jetson Nano）
- PLC通信接口

## 学习资源

### 推荐书籍

1. **《西门子S7-1200 PLC编程与应用》** - 廖常初
   - 系统讲解S7-1200编程
   - 大量实例和项目案例

2. **《工业自动化控制系统设计》** - 王永华
   - 控制系统设计方法
   - 工程实践经验

3. **《WinCC组态与应用技术》** - 张万忠
   - HMI和SCADA开发
   - 实际项目案例

### 在线资源

1. **西门子工业支持中心**
   - 官方技术文档
   - 视频教程
   - 技术论坛

2. **工控网**
   - 技术文章
   - 项目案例
   - 问题解答

3. **YouTube频道**
   - "Automation Direct"
   - "RealPars"
   - "PLC Professor"

### 实践平台

1. **Factory I/O**
   - 3D工厂仿真软件
   - 支持多种PLC
   - 丰富的场景

2. **PLCSim Advanced**
   - 西门子PLC仿真器
   - 支持S7-1200/1500
   - 虚拟调试

3. **OpenPLC**
   - 开源PLC平台
   - 支持IEC 61131-3
   - 低成本学习

## 项目总结

### 项目成果

完成本项目后，你将获得：

✅ **完整的工业控制系统**
- PLC控制程序
- HMI人机界面
- SCADA监控系统
- 完整的硬件系统

✅ **实践经验**
- 系统设计能力
- PLC编程技能
- HMI开发能力
- 系统集成经验

✅ **项目文档**
- 需求分析文档
- 系统设计文档
- 程序说明文档
- 操作手册

### 技能提升

通过本项目，你将提升：

- **技术能力**：PLC编程、HMI开发、SCADA集成
- **工程能力**：系统设计、项目管理、文档编写
- **问题解决**：故障诊断、系统优化、性能调优
- **团队协作**：跨专业沟通、项目协调

### 职业发展

本项目经验可以帮助你：

- 胜任自动化工程师岗位
- 从事PLC编程工作
- 参与工业项目开发
- 向系统集成方向发展

## 常见问题解答（FAQ）

**Q1：没有实际硬件可以学习吗？**

A：可以！使用仿真软件：
- PLCSim Advanced（PLC仿真）
- Factory I/O（工厂仿真）
- WinCC Runtime（HMI仿真）
- 虚拟串口工具（通信仿真）

**Q2：需要购买TIA Portal授权吗？**

A：学习阶段可以使用：
- 试用版（14天）
- 教育版（学校提供）
- 基础版（功能受限但免费）
- OpenPLC（开源替代方案）

**Q3：如何选择PLC品牌？**

A：考虑因素：
- 项目需求和规模
- 预算限制
- 技术支持
- 行业应用习惯
- 个人学习目标

**Q4：项目开发周期多长？**

A：根据经验水平：
- 初学者：3-4个月
- 有基础：1-2个月
- 有经验：2-3周

**Q5：如何进行远程调试？**

A：方案：
- VPN远程连接
- TeamViewer等远程桌面
- 云PLC平台
- 4G工业路由器

## 下一步学习建议

完成本项目后，建议继续学习：

1. **[工业机器人控制](../intermediate/02-industrial-robot.html)** - 学习机器人编程
2. **[工业4.0与智能制造](../intermediate/03-industry-4.0.html)** - 了解智能制造
3. **OPC UA通信** - 学习工业通信标准

## 参考资料

1. IEC 61131-3 标准文档
2. 西门子 S7-1200 系统手册
3. 西门子 TIA Portal 编程手册
4. WinCC SCADA 用户手册
5. Modbus 协议规范
6. 工业自动化系统设计规范

---

**版权声明**：本项目内容仅供学习参考，实际项目应用请遵循相关安全规范和标准。

**反馈与建议**：如果你在项目实施过程中遇到问题或有改进建议，欢迎通过评论区反馈！

**最后更新**：2024-01-15
