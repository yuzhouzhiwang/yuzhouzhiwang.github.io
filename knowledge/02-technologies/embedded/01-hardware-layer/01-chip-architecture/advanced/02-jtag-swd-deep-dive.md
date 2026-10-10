---
# 基础信息
title: "底层调试技术：JTAG与SWD深入解析"
description: "深入探讨JTAG和SWD调试协议的工作原理、硬件接口、寄存器访问机制、实时跟踪技术和高级调试技巧，掌握调试器开发基础和底层调试方法"
slug: "jtag-swd-deep-dive"

# 分类信息
domain: "01-hardware-layer"
module: "01-chip-architecture"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - JTAG
  - SWD
  - 调试技术
  - 调试协议
  - ARM CoreSight
  - 实时跟踪
prerequisites:
  - "01-arm-cortex-m-intro"
  - "08-interrupt-vector-table"
  - "06-processor-modes"
related_contents:
  - "01-performance-analysis-tool"

# 学习信息
estimated_time: 90
difficulty_score: 5

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-03-07"
updated_at: "2026-03-07"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - JTAG调试
  - SWD协议
  - 调试端口
  - CoreSight
  - 实时跟踪
  - 调试器开发
cover_image: ""
---

# 底层调试技术：JTAG与SWD深入解析


## 学习目标

完成本教程学习后，你将能够：

- [ ] 深入理解JTAG和SWD调试协议的工作原理
- [ ] 掌握调试端口（Debug Port）的寄存器访问方法
- [ ] 了解访问端口（Access Port）的配置和使用
- [ ] 掌握实时跟踪技术（ITM、ETM、DWT）
- [ ] 能够使用OpenOCD等工具进行底层调试
- [ ] 了解调试器开发的基础知识
- [ ] 掌握高级调试技巧和故障排查方法

## 前置要求

在开始本教程学习之前，你需要：

**知识要求**：
- 深入理解ARM Cortex-M架构
- 熟悉C语言和汇编语言
- 了解数字电路和通信协议基础
- 掌握寄存器操作和位操作

**技能要求**：
- 有嵌入式系统开发经验
- 熟悉调试工具的使用（GDB、OpenOCD等）
- 能够阅读和理解技术规范文档
- 具备基本的硬件调试能力

**硬件要求**：
- ARM Cortex-M开发板（支持SWD/JTAG）
- 调试器（ST-Link、J-Link或CMSIS-DAP）
- 逻辑分析仪（可选，用于协议分析）

## 概述

JTAG（Joint Test Action Group）和SWD（Serial Wire Debug）是嵌入式系统中最常用的调试接口。理解这些协议的底层工作原理，对于高级调试、性能优化和调试器开发至关重要。

### 为什么需要深入理解调试协议

1. **高级调试需求**：
   - 解决复杂的调试问题
   - 实现自定义调试功能
   - 优化调试性能

2. **调试器开发**：
   - 开发自定义调试工具
   - 集成调试功能到产品中
   - 实现生产测试工具

3. **实时跟踪**：
   - 实现非侵入式性能分析
   - 实时监控系统行为
   - 记录程序执行轨迹

4. **故障诊断**：
   - 诊断调试接口问题
   - 解决连接失败
   - 优化调试配置

### 调试架构概览

ARM Cortex-M处理器使用CoreSight调试架构：

```
┌─────────────────────────────────────────────────────────┐
│              ARM CoreSight 调试架构                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │  调试主机    │      │  调试探针    │               │
│  │  (Host PC)   │◄────►│ (Debugger)   │               │
│  └──────────────┘      └──────────────┘               │
│                              │                          │
│                              │ JTAG/SWD                │
│                              ↓                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │          调试端口 (Debug Port - DP)              │  │
│  │  - JTAG-DP: 5线接口                             │  │
│  │  - SW-DP: 2线接口                               │  │
│  └─────────────────────────────────────────────────┘  │
│                              │                          │
│                              ↓                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │         访问端口 (Access Port - AP)              │  │
│  │  - MEM-AP: 内存访问                             │  │
│  │  - JTAG-AP: JTAG链访问                          │  │
│  └─────────────────────────────────────────────────┘  │
│                              │                          │
│                              ↓                          │
│  ┌──────────┬──────────┬──────────┬──────────────┐   │
│  │   CPU    │  Memory  │   DWT    │     ITM      │   │
│  │  Debug   │  Access  │  (Trace) │   (Trace)    │   │
│  └──────────┴──────────┴──────────┴──────────────┘   │
└─────────────────────────────────────────────────────────┘
```



## 第一部分：JTAG协议详解

### JTAG基础

JTAG最初是为芯片测试设计的标准（IEEE 1149.1），后来被广泛用于调试。

**JTAG信号线**：

```
┌──────────────────────────────────────────┐
│         JTAG 5线接口                      │
├──────────────────────────────────────────┤
│  TCK  - Test Clock (时钟)                │
│  TMS  - Test Mode Select (模式选择)      │
│  TDI  - Test Data In (数据输入)          │
│  TDO  - Test Data Out (数据输出)         │
│  TRST - Test Reset (复位，可选)          │
└──────────────────────────────────────────┘
```

**JTAG状态机**：

JTAG使用一个16状态的状态机控制操作：

```
                    TMS=1
        ┌───────────────────────────┐
        │                           │
        ↓                           │
   Test-Logic-Reset                 │
        │ TMS=0                     │
        ↓                           │
    Run-Test/Idle ←─────────────────┘
        │ TMS=1
        ↓
   Select-DR-Scan
        │ TMS=0          TMS=1
        ↓                 ↓
   Capture-DR        Select-IR-Scan
        │                 │
        ↓                 ↓
    Shift-DR          Capture-IR
        │                 │
        ↓                 ↓
    Exit1-DR          Shift-IR
        │                 │
        ↓                 ↓
    Pause-DR          Exit1-IR
        │                 │
        ↓                 ↓
    Exit2-DR          Pause-IR
        │                 │
        ↓                 ↓
   Update-DR          Exit2-IR
        │                 │
        └─────────────────┘
             TMS=0
```

### JTAG寄存器

JTAG定义了两类寄存器：

1. **指令寄存器（IR）**：
   - 选择要访问的数据寄存器
   - 控制JTAG操作模式
   - 长度通常为4-5位

2. **数据寄存器（DR）**：
   - BYPASS：1位，用于绕过设备
   - IDCODE：32位，设备识别码
   - DPACC：35位，调试端口访问
   - APACC：35位，访问端口访问

**JTAG指令示例**：

```c
/**
 * @brief JTAG指令定义
 */
#define JTAG_IR_BYPASS      0x0F    // 绕过
#define JTAG_IR_IDCODE      0x0E    // 读取ID
#define JTAG_IR_DPACC       0x0A    // DP访问
#define JTAG_IR_APACC       0x0B    // AP访问
#define JTAG_IR_ABORT       0x08    // 中止操作

/**
 * @brief JTAG状态机状态
 */
typedef enum {
    JTAG_STATE_TEST_LOGIC_RESET = 0,
    JTAG_STATE_RUN_TEST_IDLE,
    JTAG_STATE_SELECT_DR_SCAN,
    JTAG_STATE_CAPTURE_DR,
    JTAG_STATE_SHIFT_DR,
    JTAG_STATE_EXIT1_DR,
    JTAG_STATE_PAUSE_DR,
    JTAG_STATE_EXIT2_DR,
    JTAG_STATE_UPDATE_DR,
    JTAG_STATE_SELECT_IR_SCAN,
    JTAG_STATE_CAPTURE_IR,
    JTAG_STATE_SHIFT_IR,
    JTAG_STATE_EXIT1_IR,
    JTAG_STATE_PAUSE_IR,
    JTAG_STATE_EXIT2_IR,
    JTAG_STATE_UPDATE_IR
} jtag_state_t;
```

### JTAG操作序列

**读取IDCODE示例**：

```c
/**
 * @brief 读取JTAG IDCODE
 * @retval 32位IDCODE值
 */
uint32_t JTAG_Read_IDCODE(void)
{
    uint32_t idcode = 0;
    
    // 1. 复位到Test-Logic-Reset状态
    JTAG_Reset();
    
    // 2. 进入Run-Test/Idle状态
    JTAG_Move_To_State(JTAG_STATE_RUN_TEST_IDLE);
    
    // 3. 进入Select-DR-Scan状态
    JTAG_Set_TMS(1);
    JTAG_Clock();
    
    // 4. 进入Capture-DR状态（自动加载IDCODE）
    JTAG_Set_TMS(0);
    JTAG_Clock();
    
    // 5. 进入Shift-DR状态
    JTAG_Set_TMS(0);
    JTAG_Clock();
    
    // 6. 移出32位IDCODE
    for (int i = 0; i < 32; i++) {
        JTAG_Set_TMS(0);  // 保持在Shift-DR
        JTAG_Clock();
        
        // 读取TDO
        if (JTAG_Read_TDO()) {
            idcode |= (1 << i);
        }
    }
    
    // 7. 返回到Run-Test/Idle
    JTAG_Move_To_State(JTAG_STATE_RUN_TEST_IDLE);
    
    return idcode;
}

/**
 * @brief JTAG复位
 */
void JTAG_Reset(void)
{
    // 发送5个TMS=1，进入Test-Logic-Reset
    for (int i = 0; i < 5; i++) {
        JTAG_Set_TMS(1);
        JTAG_Clock();
    }
}

/**
 * @brief 移动到指定状态
 * @param target_state 目标状态
 */
void JTAG_Move_To_State(jtag_state_t target_state)
{
    // 根据当前状态和目标状态，生成TMS序列
    // 这里简化处理，实际需要状态机转换表
    
    // 示例：移动到Run-Test/Idle
    if (target_state == JTAG_STATE_RUN_TEST_IDLE) {
        JTAG_Set_TMS(0);
        JTAG_Clock();
    }
}

/**
 * @brief 产生一个时钟周期
 */
void JTAG_Clock(void)
{
    // TCK低电平
    GPIO_ResetBits(JTAG_TCK_PORT, JTAG_TCK_PIN);
    Delay_us(1);
    
    // TCK高电平
    GPIO_SetBits(JTAG_TCK_PORT, JTAG_TCK_PIN);
    Delay_us(1);
}

/**
 * @brief 设置TMS信号
 * @param value TMS值（0或1）
 */
void JTAG_Set_TMS(uint8_t value)
{
    if (value) {
        GPIO_SetBits(JTAG_TMS_PORT, JTAG_TMS_PIN);
    } else {
        GPIO_ResetBits(JTAG_TMS_PORT, JTAG_TMS_PIN);
    }
}

/**
 * @brief 设置TDI信号
 * @param value TDI值（0或1）
 */
void JTAG_Set_TDI(uint8_t value)
{
    if (value) {
        GPIO_SetBits(JTAG_TDI_PORT, JTAG_TDI_PIN);
    } else {
        GPIO_ResetBits(JTAG_TDI_PORT, JTAG_TDI_PIN);
    }
}

/**
 * @brief 读取TDO信号
 * @retval TDO值（0或1）
 */
uint8_t JTAG_Read_TDO(void)
{
    return GPIO_ReadInputDataBit(JTAG_TDO_PORT, JTAG_TDO_PIN);
}
```

### JTAG链扫描

当多个设备连接在JTAG链上时，需要扫描链以识别所有设备：

```c
/**
 * @brief JTAG链扫描
 * @param idcodes 存储IDCODE的数组
 * @param max_devices 最大设备数
 * @retval 检测到的设备数量
 */
int JTAG_Scan_Chain(uint32_t *idcodes, int max_devices)
{
    int device_count = 0;
    
    // 1. 复位JTAG
    JTAG_Reset();
    
    // 2. 进入Shift-DR状态（IDCODE自动加载）
    JTAG_Move_To_State(JTAG_STATE_SHIFT_DR);
    
    // 3. 扫描链，读取所有IDCODE
    for (int dev = 0; dev < max_devices; dev++) {
        uint32_t idcode = 0;
        
        // 读取32位
        for (int bit = 0; bit < 32; bit++) {
            JTAG_Set_TMS(0);  // 保持在Shift-DR
            JTAG_Clock();
            
            if (JTAG_Read_TDO()) {
                idcode |= (1 << bit);
            }
        }
        
        // 检查IDCODE是否有效
        if (idcode == 0xFFFFFFFF || idcode == 0x00000000) {
            break;  // 链结束
        }
        
        idcodes[device_count++] = idcode;
    }
    
    // 4. 返回到Run-Test/Idle
    JTAG_Move_To_State(JTAG_STATE_RUN_TEST_IDLE);
    
    return device_count;
}

/**
 * @brief 解析IDCODE
 * @param idcode IDCODE值
 */
void JTAG_Parse_IDCODE(uint32_t idcode)
{
    uint8_t version = (idcode >> 28) & 0x0F;
    uint16_t part_number = (idcode >> 12) & 0xFFFF;
    uint16_t manufacturer = (idcode >> 1) & 0x7FF;
    uint8_t lsb = idcode & 0x01;
    
    printf("IDCODE: 0x%08X\n", idcode);
    printf("  Version: 0x%X\n", version);
    printf("  Part Number: 0x%04X\n", part_number);
    printf("  Manufacturer: 0x%03X\n", manufacturer);
    printf("  LSB: %d (should be 1)\n", lsb);
}
```



## 第二部分：SWD协议详解

### SWD基础

SWD（Serial Wire Debug）是ARM专门为调试设计的2线协议，相比JTAG更简单高效。

**SWD信号线**：

```
┌──────────────────────────────────────────┐
│         SWD 2线接口                       │
├──────────────────────────────────────────┤
│  SWCLK - Serial Wire Clock (时钟)        │
│  SWDIO - Serial Wire Data I/O (数据)     │
│  (可选) SWO - Serial Wire Output (跟踪)  │
└──────────────────────────────────────────┘
```

**SWD vs JTAG对比**：

| 特性 | JTAG | SWD |
|------|------|-----|
| 信号线数量 | 5线（TCK, TMS, TDI, TDO, TRST） | 2线（SWCLK, SWDIO） |
| 数据传输 | 单向（TDI/TDO分离） | 双向（SWDIO） |
| 速度 | 较慢 | 较快 |
| 引脚占用 | 多 | 少 |
| 链式连接 | 支持 | 不支持 |
| 实时跟踪 | 需要额外引脚 | 集成SWO |

### SWD协议格式

SWD使用包（Packet）进行通信，每个包包含：

```
SWD数据包格式（8位请求 + 3位ACK + 32位数据 + 1位奇偶校验）

请求阶段（8位）：
┌────┬────┬────┬────┬────┬────┬────┬────┐
│Start│APnDP│ RnW │ A2 │ A3 │Parity│Stop│Park│
└────┴────┴────┴────┴────┴────┴────┴────┘
  1     1     1     1    1     1     1    1

- Start: 起始位，固定为1
- APnDP: 0=DP访问, 1=AP访问
- RnW: 0=写, 1=读
- A2, A3: 地址位[2:3]
- Parity: 奇偶校验位
- Stop: 停止位，固定为0
- Park: 停车位，固定为1

ACK阶段（3位）：
┌────┬────┬────┐
│ b0 │ b1 │ b2 │
└────┴────┴────┘

- 001 (OK): 操作成功
- 010 (WAIT): 等待，需要重试
- 100 (FAULT): 错误
- 111: 协议错误

数据阶段（33位，仅在读/写操作时）：
┌──────────────────────────┬────────┐
│    32位数据               │ Parity │
└──────────────────────────┴────────┘
```

### SWD操作实现

**SWD初始化序列**：

```c
/**
 * @brief SWD初始化
 */
void SWD_Init(void)
{
    // 1. 发送至少50个时钟周期，SWDIO保持高电平
    //    这会复位任何现有的JTAG状态
    SWD_Set_SWDIO(1);
    for (int i = 0; i < 60; i++) {
        SWD_Clock();
    }
    
    // 2. 发送JTAG到SWD切换序列（16位）
    //    序列值：0xE79E (0b1110011110011110)
    uint16_t switch_seq = 0xE79E;
    for (int i = 0; i < 16; i++) {
        SWD_Set_SWDIO((switch_seq >> i) & 1);
        SWD_Clock();
    }
    
    // 3. 再发送至少50个时钟周期，SWDIO保持高电平
    SWD_Set_SWDIO(1);
    for (int i = 0; i < 60; i++) {
        SWD_Clock();
    }
    
    // 4. 发送线复位序列（至少50个时钟，SWDIO保持高电平）
    //    然后发送2个空闲周期（SWDIO=0）
    for (int i = 0; i < 2; i++) {
        SWD_Set_SWDIO(0);
        SWD_Clock();
    }
    
    printf("SWD初始化完成\n");
}

/**
 * @brief 产生一个SWD时钟周期
 */
void SWD_Clock(void)
{
    // SWCLK低电平
    GPIO_ResetBits(SWD_CLK_PORT, SWD_CLK_PIN);
    Delay_ns(100);  // 根据目标速度调整
    
    // SWCLK高电平
    GPIO_SetBits(SWD_CLK_PORT, SWD_CLK_PIN);
    Delay_ns(100);
}

/**
 * @brief 设置SWDIO为输出模式
 */
void SWD_SWDIO_Output(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = SWD_DIO_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(SWD_DIO_PORT, &GPIO_InitStruct);
}

/**
 * @brief 设置SWDIO为输入模式
 */
void SWD_SWDIO_Input(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = SWD_DIO_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(SWD_DIO_PORT, &GPIO_InitStruct);
}

/**
 * @brief 设置SWDIO信号
 * @param value SWDIO值（0或1）
 */
void SWD_Set_SWDIO(uint8_t value)
{
    if (value) {
        GPIO_SetBits(SWD_DIO_PORT, SWD_DIO_PIN);
    } else {
        GPIO_ResetBits(SWD_DIO_PORT, SWD_DIO_PIN);
    }
}

/**
 * @brief 读取SWDIO信号
 * @retval SWDIO值（0或1）
 */
uint8_t SWD_Read_SWDIO(void)
{
    return GPIO_ReadInputDataBit(SWD_DIO_PORT, SWD_DIO_PIN);
}
```

**SWD读写操作**：

```c
/**
 * @brief 计算奇偶校验位
 * @param data 数据
 * @param bits 位数
 * @retval 奇偶校验位（奇校验）
 */
uint8_t SWD_Parity(uint32_t data, int bits)
{
    uint8_t parity = 0;
    for (int i = 0; i < bits; i++) {
        parity ^= (data >> i) & 1;
    }
    return parity;
}

/**
 * @brief 发送SWD请求
 * @param APnDP 0=DP, 1=AP
 * @param RnW 0=写, 1=读
 * @param addr 地址（A[3:2]）
 * @retval ACK响应
 */
uint8_t SWD_Send_Request(uint8_t APnDP, uint8_t RnW, uint8_t addr)
{
    uint8_t request = 0;
    uint8_t parity = 0;
    
    // 构建请求字节
    request |= (1 << 0);        // Start bit
    request |= (APnDP << 1);    // APnDP
    request |= (RnW << 2);      // RnW
    request |= ((addr & 0x0C) >> 2) << 3;  // A[3:2]
    
    // 计算奇偶校验
    parity = APnDP ^ RnW ^ ((addr >> 2) & 1) ^ ((addr >> 3) & 1);
    request |= (parity << 5);   // Parity
    request |= (0 << 6);        // Stop bit
    request |= (1 << 7);        // Park bit
    
    // 发送请求（8位）
    SWD_SWDIO_Output();
    for (int i = 0; i < 8; i++) {
        SWD_Set_SWDIO((request >> i) & 1);
        SWD_Clock();
    }
    
    // 切换到输入模式，读取ACK
    SWD_SWDIO_Input();
    
    // 读取ACK（3位）
    uint8_t ack = 0;
    for (int i = 0; i < 3; i++) {
        SWD_Clock();
        if (SWD_Read_SWDIO()) {
            ack |= (1 << i);
        }
    }
    
    return ack;
}

/**
 * @brief SWD读操作
 * @param APnDP 0=DP, 1=AP
 * @param addr 地址
 * @param data 读取的数据
 * @retval 0=成功, -1=失败
 */
int SWD_Read(uint8_t APnDP, uint8_t addr, uint32_t *data)
{
    uint8_t ack;
    int retry = 0;
    
    do {
        // 发送读请求
        ack = SWD_Send_Request(APnDP, 1, addr);
        
        if (ack == 0x01) {  // OK
            // 读取数据（32位）
            uint32_t value = 0;
            for (int i = 0; i < 32; i++) {
                SWD_Clock();
                if (SWD_Read_SWDIO()) {
                    value |= (1 << i);
                }
            }
            
            // 读取奇偶校验位
            SWD_Clock();
            uint8_t parity_bit = SWD_Read_SWDIO();
            
            // 验证奇偶校验
            uint8_t calc_parity = SWD_Parity(value, 32);
            if (parity_bit != calc_parity) {
                printf("SWD读取奇偶校验错误\n");
                return -1;
            }
            
            *data = value;
            
            // 发送2个空闲周期
            SWD_SWDIO_Output();
            SWD_Set_SWDIO(0);
            SWD_Clock();
            SWD_Clock();
            
            return 0;  // 成功
            
        } else if (ack == 0x02) {  // WAIT
            // 等待并重试
            retry++;
            if (retry > 100) {
                printf("SWD读取超时（WAIT）\n");
                return -1;
            }
            Delay_us(10);
            
        } else if (ack == 0x04) {  // FAULT
            printf("SWD读取错误（FAULT）\n");
            return -1;
            
        } else {
            printf("SWD读取协议错误（ACK=0x%X）\n", ack);
            return -1;
        }
    } while (ack == 0x02);
    
    return -1;
}

/**
 * @brief SWD写操作
 * @param APnDP 0=DP, 1=AP
 * @param addr 地址
 * @param data 要写入的数据
 * @retval 0=成功, -1=失败
 */
int SWD_Write(uint8_t APnDP, uint8_t addr, uint32_t data)
{
    uint8_t ack;
    int retry = 0;
    
    do {
        // 发送写请求
        ack = SWD_Send_Request(APnDP, 0, addr);
        
        if (ack == 0x01) {  // OK
            // 发送一个周转周期
            SWD_SWDIO_Input();
            SWD_Clock();
            
            // 切换到输出模式
            SWD_SWDIO_Output();
            
            // 写入数据（32位）
            for (int i = 0; i < 32; i++) {
                SWD_Set_SWDIO((data >> i) & 1);
                SWD_Clock();
            }
            
            // 写入奇偶校验位
            uint8_t parity = SWD_Parity(data, 32);
            SWD_Set_SWDIO(parity);
            SWD_Clock();
            
            // 发送2个空闲周期
            SWD_Set_SWDIO(0);
            SWD_Clock();
            SWD_Clock();
            
            return 0;  // 成功
            
        } else if (ack == 0x02) {  // WAIT
            retry++;
            if (retry > 100) {
                printf("SWD写入超时（WAIT）\n");
                return -1;
            }
            Delay_us(10);
            
        } else if (ack == 0x04) {  // FAULT
            printf("SWD写入错误（FAULT）\n");
            return -1;
            
        } else {
            printf("SWD写入协议错误（ACK=0x%X）\n", ack);
            return -1;
        }
    } while (ack == 0x02);
    
    return -1;
}
```



## 第三部分：调试端口（Debug Port）

### DP寄存器

调试端口提供了访问目标系统的接口，主要寄存器包括：

```c
/**
 * @brief DP寄存器地址定义
 */
#define DP_IDCODE       0x00    // 识别码寄存器（只读）
#define DP_ABORT        0x00    // 中止寄存器（只写）
#define DP_CTRL_STAT    0x04    // 控制/状态寄存器
#define DP_SELECT       0x08    // 选择寄存器
#define DP_RDBUFF       0x0C    // 读缓冲寄存器（只读）

/**
 * @brief CTRL/STAT寄存器位定义
 */
#define DP_CTRL_CSYSPWRUPREQ    (1 << 30)  // 系统电源请求
#define DP_CTRL_CSYSPWRUPACK    (1 << 31)  // 系统电源确认
#define DP_CTRL_CDBGPWRUPREQ    (1 << 28)  // 调试电源请求
#define DP_CTRL_CDBGPWRUPACK    (1 << 29)  // 调试电源确认
#define DP_CTRL_STICKYERR       (1 << 5)   // 粘性错误标志
#define DP_CTRL_STICKYCMP       (1 << 4)   // 粘性比较标志
#define DP_CTRL_STICKYORUN      (1 << 1)   // 粘性溢出标志

/**
 * @brief ABORT寄存器位定义
 */
#define DP_ABORT_ORUNERRCLR     (1 << 4)   // 清除溢出错误
#define DP_ABORT_WDERRCLR       (1 << 3)   // 清除写错误
#define DP_ABORT_STKERRCLR      (1 << 2)   // 清除粘性错误
#define DP_ABORT_STKCMPCLR      (1 << 1)   // 清除粘性比较
#define DP_ABORT_DAPABORT       (1 << 0)   // DAP中止
```

### DP初始化

```c
/**
 * @brief 初始化调试端口
 * @retval 0=成功, -1=失败
 */
int DP_Init(void)
{
    uint32_t idcode;
    uint32_t ctrl_stat;
    
    // 1. 初始化SWD接口
    SWD_Init();
    
    // 2. 读取IDCODE
    if (SWD_Read(0, DP_IDCODE, &idcode) != 0) {
        printf("读取IDCODE失败\n");
        return -1;
    }
    
    printf("DP IDCODE: 0x%08X\n", idcode);
    
    // 解析IDCODE
    uint8_t version = (idcode >> 28) & 0x0F;
    uint16_t part_no = (idcode >> 12) & 0xFFFF;
    uint16_t designer = (idcode >> 1) & 0x7FF;
    
    printf("  Version: 0x%X\n", version);
    printf("  Part Number: 0x%04X\n", part_no);
    printf("  Designer: 0x%03X\n", designer);
    
    // 3. 清除错误标志
    if (SWD_Write(0, DP_ABORT, 0x1E) != 0) {
        printf("清除错误标志失败\n");
        return -1;
    }
    
    // 4. 上电调试域
    ctrl_stat = DP_CTRL_CSYSPWRUPREQ | DP_CTRL_CDBGPWRUPREQ;
    if (SWD_Write(0, DP_CTRL_STAT, ctrl_stat) != 0) {
        printf("上电调试域失败\n");
        return -1;
    }
    
    // 5. 等待上电完成
    int timeout = 1000;
    do {
        if (SWD_Read(0, DP_CTRL_STAT, &ctrl_stat) != 0) {
            printf("读取CTRL/STAT失败\n");
            return -1;
        }
        
        if ((ctrl_stat & (DP_CTRL_CSYSPWRUPACK | DP_CTRL_CDBGPWRUPACK)) ==
            (DP_CTRL_CSYSPWRUPACK | DP_CTRL_CDBGPWRUPACK)) {
            break;  // 上电完成
        }
        
        Delay_us(10);
        timeout--;
    } while (timeout > 0);
    
    if (timeout == 0) {
        printf("上电超时\n");
        return -1;
    }
    
    printf("调试端口初始化成功\n");
    return 0;
}

/**
 * @brief 检查DP错误
 * @retval 0=无错误, -1=有错误
 */
int DP_Check_Error(void)
{
    uint32_t ctrl_stat;
    
    if (SWD_Read(0, DP_CTRL_STAT, &ctrl_stat) != 0) {
        return -1;
    }
    
    if (ctrl_stat & DP_CTRL_STICKYERR) {
        printf("DP粘性错误\n");
        
        // 清除错误
        SWD_Write(0, DP_ABORT, DP_ABORT_STKERRCLR);
        return -1;
    }
    
    if (ctrl_stat & DP_CTRL_STICKYORUN) {
        printf("DP溢出错误\n");
        
        // 清除错误
        SWD_Write(0, DP_ABORT, DP_ABORT_ORUNERRCLR);
        return -1;
    }
    
    return 0;
}
```

## 第四部分：访问端口（Access Port）

### MEM-AP寄存器

MEM-AP（Memory Access Port）用于访问目标系统的内存和寄存器：

```c
/**
 * @brief MEM-AP寄存器地址定义
 */
#define AP_CSW          0x00    // 控制/状态字寄存器
#define AP_TAR          0x04    // 传输地址寄存器
#define AP_DRW          0x0C    // 数据读/写寄存器
#define AP_BD0          0x10    // 字节数据寄存器0
#define AP_BD1          0x14    // 字节数据寄存器1
#define AP_BD2          0x18    // 字节数据寄存器2
#define AP_BD3          0x1C    // 字节数据寄存器3
#define AP_CFG          0xF4    // 配置寄存器
#define AP_BASE         0xF8    // 基地址寄存器
#define AP_IDR          0xFC    // 识别寄存器

/**
 * @brief CSW寄存器位定义
 */
#define AP_CSW_DBGSWENABLE      (1 << 31)  // 调试软件使能
#define AP_CSW_PROT_MASK        (0x7F << 24)  // 保护位
#define AP_CSW_SPIDEN           (1 << 23)  // 安全特权指令使能
#define AP_CSW_MODE_MASK        (0x0F << 8)   // 模式
#define AP_CSW_TRINPROG         (1 << 7)   // 传输进行中
#define AP_CSW_DEVICEEN         (1 << 6)   // 设备使能
#define AP_CSW_ADDRINC_OFF      (0 << 4)   // 地址不递增
#define AP_CSW_ADDRINC_SINGLE   (1 << 4)   // 单次递增
#define AP_CSW_ADDRINC_PACKED   (2 << 4)   // 打包递增
#define AP_CSW_SIZE_8BIT        (0 << 0)   // 8位访问
#define AP_CSW_SIZE_16BIT       (1 << 0)   // 16位访问
#define AP_CSW_SIZE_32BIT       (2 << 0)   // 32位访问
```

### AP访问操作

```c
/**
 * @brief 选择AP
 * @param ap_num AP编号
 * @retval 0=成功, -1=失败
 */
int AP_Select(uint8_t ap_num)
{
    uint32_t select = (ap_num << 24);
    return SWD_Write(0, DP_SELECT, select);
}

/**
 * @brief 读取AP寄存器
 * @param addr AP寄存器地址
 * @param data 读取的数据
 * @retval 0=成功, -1=失败
 */
int AP_Read(uint8_t addr, uint32_t *data)
{
    // 1. 发起AP读操作
    if (SWD_Read(1, addr, data) != 0) {
        return -1;
    }
    
    // 2. 读取RDBUFF获取实际数据
    //    （AP读操作有一个周期的延迟）
    if (SWD_Read(0, DP_RDBUFF, data) != 0) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 写入AP寄存器
 * @param addr AP寄存器地址
 * @param data 要写入的数据
 * @retval 0=成功, -1=失败
 */
int AP_Write(uint8_t addr, uint32_t data)
{
    return SWD_Write(1, addr, data);
}

/**
 * @brief 初始化MEM-AP
 * @retval 0=成功, -1=失败
 */
int MEM_AP_Init(void)
{
    uint32_t idr;
    
    // 1. 选择AP0（通常是MEM-AP）
    if (AP_Select(0) != 0) {
        printf("选择AP失败\n");
        return -1;
    }
    
    // 2. 读取IDR
    if (AP_Read(AP_IDR, &idr) != 0) {
        printf("读取AP IDR失败\n");
        return -1;
    }
    
    printf("AP IDR: 0x%08X\n", idr);
    
    // 3. 配置CSW
    uint32_t csw = AP_CSW_DBGSWENABLE | 
                   AP_CSW_SIZE_32BIT | 
                   AP_CSW_ADDRINC_SINGLE;
    
    if (AP_Write(AP_CSW, csw) != 0) {
        printf("配置CSW失败\n");
        return -1;
    }
    
    printf("MEM-AP初始化成功\n");
    return 0;
}
```

### 内存读写操作

```c
/**
 * @brief 读取32位内存
 * @param addr 内存地址
 * @param data 读取的数据
 * @retval 0=成功, -1=失败
 */
int MEM_Read32(uint32_t addr, uint32_t *data)
{
    // 1. 设置传输地址
    if (AP_Write(AP_TAR, addr) != 0) {
        return -1;
    }
    
    // 2. 读取数据
    if (AP_Read(AP_DRW, data) != 0) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 写入32位内存
 * @param addr 内存地址
 * @param data 要写入的数据
 * @retval 0=成功, -1=失败
 */
int MEM_Write32(uint32_t addr, uint32_t data)
{
    // 1. 设置传输地址
    if (AP_Write(AP_TAR, addr) != 0) {
        return -1;
    }
    
    // 2. 写入数据
    if (AP_Write(AP_DRW, data) != 0) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 读取内存块
 * @param addr 起始地址
 * @param data 数据缓冲区
 * @param count 字数（32位）
 * @retval 0=成功, -1=失败
 */
int MEM_Read_Block(uint32_t addr, uint32_t *data, uint32_t count)
{
    // 1. 配置CSW为自动递增模式
    uint32_t csw = AP_CSW_DBGSWENABLE | 
                   AP_CSW_SIZE_32BIT | 
                   AP_CSW_ADDRINC_SINGLE;
    
    if (AP_Write(AP_CSW, csw) != 0) {
        return -1;
    }
    
    // 2. 设置起始地址
    if (AP_Write(AP_TAR, addr) != 0) {
        return -1;
    }
    
    // 3. 连续读取
    for (uint32_t i = 0; i < count; i++) {
        if (AP_Read(AP_DRW, &data[i]) != 0) {
            return -1;
        }
    }
    
    return 0;
}

/**
 * @brief 写入内存块
 * @param addr 起始地址
 * @param data 数据缓冲区
 * @param count 字数（32位）
 * @retval 0=成功, -1=失败
 */
int MEM_Write_Block(uint32_t addr, const uint32_t *data, uint32_t count)
{
    // 1. 配置CSW为自动递增模式
    uint32_t csw = AP_CSW_DBGSWENABLE | 
                   AP_CSW_SIZE_32BIT | 
                   AP_CSW_ADDRINC_SINGLE;
    
    if (AP_Write(AP_CSW, csw) != 0) {
        return -1;
    }
    
    // 2. 设置起始地址
    if (AP_Write(AP_TAR, addr) != 0) {
        return -1;
    }
    
    // 3. 连续写入
    for (uint32_t i = 0; i < count; i++) {
        if (AP_Write(AP_DRW, data[i]) != 0) {
            return -1;
        }
    }
    
    return 0;
}
```



## 第五部分：CPU调试功能

### CPU调试寄存器

ARM Cortex-M提供了一组调试寄存器用于控制CPU：

```c
/**
 * @brief CPU调试寄存器地址定义
 */
#define DHCSR           0xE000EDF0  // 调试停机控制和状态寄存器
#define DCRSR           0xE000EDF4  // 调试核心寄存器选择器
#define DCRDR           0xE000EDF8  // 调试核心寄存器数据
#define DEMCR           0xE000EDFC  // 调试异常和监视器控制寄存器

/**
 * @brief DHCSR寄存器位定义
 */
#define DHCSR_DBGKEY            (0xA05F << 16)  // 调试密钥
#define DHCSR_S_RESET_ST        (1 << 25)  // 复位状态
#define DHCSR_S_RETIRE_ST       (1 << 24)  // 指令退休状态
#define DHCSR_S_LOCKUP          (1 << 19)  // 锁定状态
#define DHCSR_S_SLEEP           (1 << 18)  // 睡眠状态
#define DHCSR_S_HALT            (1 << 17)  // 停机状态
#define DHCSR_S_REGRDY          (1 << 16)  // 寄存器就绪
#define DHCSR_C_SNAPSTALL       (1 << 5)   // 快照停顿
#define DHCSR_C_MASKINTS        (1 << 3)   // 屏蔽中断
#define DHCSR_C_STEP            (1 << 2)   // 单步执行
#define DHCSR_C_HALT            (1 << 1)   // 停机请求
#define DHCSR_C_DEBUGEN         (1 << 0)   // 调试使能

/**
 * @brief DCRSR寄存器位定义
 */
#define DCRSR_REGWnR            (1 << 16)  // 0=读, 1=写
#define DCRSR_REGSEL_MASK       0x1F       // 寄存器选择

/**
 * @brief DEMCR寄存器位定义
 */
#define DEMCR_TRCENA            (1 << 24)  // 跟踪使能
#define DEMCR_MON_REQ           (1 << 19)  // 监视器请求
#define DEMCR_MON_STEP          (1 << 18)  // 监视器单步
#define DEMCR_MON_PEND          (1 << 17)  // 监视器挂起
#define DEMCR_MON_EN            (1 << 16)  // 监视器使能
#define DEMCR_VC_HARDERR        (1 << 10)  // 硬错误向量捕获
#define DEMCR_VC_INTERR         (1 << 9)   // 中断错误向量捕获
#define DEMCR_VC_BUSERR         (1 << 8)   // 总线错误向量捕获
#define DEMCR_VC_STATERR        (1 << 7)   // 状态错误向量捕获
#define DEMCR_VC_CHKERR         (1 << 6)   // 检查错误向量捕获
#define DEMCR_VC_NOCPERR        (1 << 5)   // 无协处理器错误向量捕获
#define DEMCR_VC_MMERR          (1 << 4)   // 内存管理错误向量捕获
#define DEMCR_VC_CORERESET      (1 << 0)   // 核心复位向量捕获
```

### CPU控制操作

```c
/**
 * @brief 停止CPU
 * @retval 0=成功, -1=失败
 */
int CPU_Halt(void)
{
    uint32_t dhcsr;
    
    // 1. 发送停机请求
    dhcsr = DHCSR_DBGKEY | DHCSR_C_DEBUGEN | DHCSR_C_HALT;
    if (MEM_Write32(DHCSR, dhcsr) != 0) {
        return -1;
    }
    
    // 2. 等待CPU停机
    int timeout = 1000;
    do {
        if (MEM_Read32(DHCSR, &dhcsr) != 0) {
            return -1;
        }
        
        if (dhcsr & DHCSR_S_HALT) {
            printf("CPU已停机\n");
            return 0;
        }
        
        Delay_us(10);
        timeout--;
    } while (timeout > 0);
    
    printf("CPU停机超时\n");
    return -1;
}

/**
 * @brief 恢复CPU运行
 * @retval 0=成功, -1=失败
 */
int CPU_Resume(void)
{
    uint32_t dhcsr;
    
    // 清除停机位
    dhcsr = DHCSR_DBGKEY | DHCSR_C_DEBUGEN;
    if (MEM_Write32(DHCSR, dhcsr) != 0) {
        return -1;
    }
    
    printf("CPU已恢复运行\n");
    return 0;
}

/**
 * @brief CPU单步执行
 * @retval 0=成功, -1=失败
 */
int CPU_Step(void)
{
    uint32_t dhcsr;
    
    // 1. 设置单步标志
    dhcsr = DHCSR_DBGKEY | DHCSR_C_DEBUGEN | DHCSR_C_STEP | DHCSR_C_MASKINTS;
    if (MEM_Write32(DHCSR, dhcsr) != 0) {
        return -1;
    }
    
    // 2. 恢复运行（执行一条指令后自动停止）
    dhcsr = DHCSR_DBGKEY | DHCSR_C_DEBUGEN | DHCSR_C_STEP;
    if (MEM_Write32(DHCSR, dhcsr) != 0) {
        return -1;
    }
    
    // 3. 等待停机
    int timeout = 1000;
    do {
        if (MEM_Read32(DHCSR, &dhcsr) != 0) {
            return -1;
        }
        
        if (dhcsr & DHCSR_S_HALT) {
            return 0;
        }
        
        Delay_us(10);
        timeout--;
    } while (timeout > 0);
    
    return -1;
}

/**
 * @brief 复位CPU
 * @retval 0=成功, -1=失败
 */
int CPU_Reset(void)
{
    uint32_t aircr;
    
    // 1. 读取AIRCR
    if (MEM_Read32(0xE000ED0C, &aircr) != 0) {
        return -1;
    }
    
    // 2. 保留优先级分组，设置复位请求
    aircr = (0x05FA << 16) | (aircr & 0x700) | (1 << 2);
    
    // 3. 写入AIRCR触发复位
    if (MEM_Write32(0xE000ED0C, aircr) != 0) {
        return -1;
    }
    
    printf("CPU复位请求已发送\n");
    
    // 4. 等待复位完成
    Delay_ms(100);
    
    return 0;
}
```

### 寄存器读写

```c
/**
 * @brief 读取CPU核心寄存器
 * @param reg_num 寄存器编号（0-20）
 * @param value 读取的值
 * @retval 0=成功, -1=失败
 */
int CPU_Read_Register(uint8_t reg_num, uint32_t *value)
{
    uint32_t dhcsr;
    
    // 1. 确保CPU已停机
    if (MEM_Read32(DHCSR, &dhcsr) != 0) {
        return -1;
    }
    
    if (!(dhcsr & DHCSR_S_HALT)) {
        printf("CPU未停机，无法读取寄存器\n");
        return -1;
    }
    
    // 2. 选择要读取的寄存器
    uint32_t dcrsr = reg_num & DCRSR_REGSEL_MASK;
    if (MEM_Write32(DCRSR, dcrsr) != 0) {
        return -1;
    }
    
    // 3. 等待寄存器就绪
    int timeout = 1000;
    do {
        if (MEM_Read32(DHCSR, &dhcsr) != 0) {
            return -1;
        }
        
        if (dhcsr & DHCSR_S_REGRDY) {
            break;
        }
        
        Delay_us(1);
        timeout--;
    } while (timeout > 0);
    
    if (timeout == 0) {
        return -1;
    }
    
    // 4. 读取寄存器值
    if (MEM_Read32(DCRDR, value) != 0) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 写入CPU核心寄存器
 * @param reg_num 寄存器编号（0-20）
 * @param value 要写入的值
 * @retval 0=成功, -1=失败
 */
int CPU_Write_Register(uint8_t reg_num, uint32_t value)
{
    uint32_t dhcsr;
    
    // 1. 确保CPU已停机
    if (MEM_Read32(DHCSR, &dhcsr) != 0) {
        return -1;
    }
    
    if (!(dhcsr & DHCSR_S_HALT)) {
        printf("CPU未停机，无法写入寄存器\n");
        return -1;
    }
    
    // 2. 写入寄存器值
    if (MEM_Write32(DCRDR, value) != 0) {
        return -1;
    }
    
    // 3. 选择要写入的寄存器并设置写标志
    uint32_t dcrsr = DCRSR_REGWnR | (reg_num & DCRSR_REGSEL_MASK);
    if (MEM_Write32(DCRSR, dcrsr) != 0) {
        return -1;
    }
    
    // 4. 等待写入完成
    int timeout = 1000;
    do {
        if (MEM_Read32(DHCSR, &dhcsr) != 0) {
            return -1;
        }
        
        if (dhcsr & DHCSR_S_REGRDY) {
            return 0;
        }
        
        Delay_us(1);
        timeout--;
    } while (timeout > 0);
    
    return -1;
}

/**
 * @brief 打印所有核心寄存器
 */
void CPU_Print_Registers(void)
{
    const char *reg_names[] = {
        "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
        "R8", "R9", "R10", "R11", "R12", "SP", "LR", "PC",
        "xPSR", "MSP", "PSP", "CONTROL"
    };
    
    printf("\n=== CPU寄存器 ===\n");
    
    for (int i = 0; i < 20; i++) {
        uint32_t value;
        if (CPU_Read_Register(i, &value) == 0) {
            printf("%-8s: 0x%08X\n", reg_names[i], value);
        }
    }
    
    printf("=================\n\n");
}
```



## 第六部分：实时跟踪技术

### ITM（Instrumentation Trace Macrocell）

ITM提供了一种非侵入式的调试输出方法，通过SWO引脚输出跟踪数据。

```c
/**
 * @brief ITM寄存器地址定义
 */
#define ITM_STIM0           0xE0000000  // 激励端口0
#define ITM_TER             0xE0000E00  // 跟踪使能寄存器
#define ITM_TPR             0xE0000E40  // 跟踪特权寄存器
#define ITM_TCR             0xE0000E80  // 跟踪控制寄存器
#define ITM_LAR             0xE0000FB0  // 锁访问寄存器

/**
 * @brief 初始化ITM
 * @param baudrate SWO波特率
 * @retval 0=成功, -1=失败
 */
int ITM_Init(uint32_t baudrate)
{
    uint32_t demcr;
    
    // 1. 使能跟踪
    if (MEM_Read32(DEMCR, &demcr) != 0) {
        return -1;
    }
    
    demcr |= DEMCR_TRCENA;
    if (MEM_Write32(DEMCR, demcr) != 0) {
        return -1;
    }
    
    // 2. 解锁ITM
    if (MEM_Write32(ITM_LAR, 0xC5ACCE55) != 0) {
        return -1;
    }
    
    // 3. 配置ITM
    uint32_t itm_tcr = (1 << 0) |   // ITM使能
                       (1 << 3) |   // 同步包使能
                       (1 << 16);   // 跟踪总线ID
    
    if (MEM_Write32(ITM_TCR, itm_tcr) != 0) {
        return -1;
    }
    
    // 4. 使能激励端口0
    if (MEM_Write32(ITM_TER, 0x00000001) != 0) {
        return -1;
    }
    
    // 5. 配置TPIU（Trace Port Interface Unit）
    // 这里需要根据具体芯片配置TPIU的分频器
    // 以匹配所需的SWO波特率
    
    printf("ITM初始化完成\n");
    return 0;
}

/**
 * @brief 通过ITM发送字符
 * @param ch 要发送的字符
 * @retval 0=成功, -1=失败
 */
int ITM_SendChar(char ch)
{
    uint32_t stim0;
    int timeout = 1000;
    
    // 等待激励端口就绪
    do {
        if (MEM_Read32(ITM_STIM0, &stim0) != 0) {
            return -1;
        }
        
        if (stim0 & 0x01) {  // 端口就绪
            break;
        }
        
        Delay_us(1);
        timeout--;
    } while (timeout > 0);
    
    if (timeout == 0) {
        return -1;
    }
    
    // 写入字符
    if (MEM_Write32(ITM_STIM0, ch) != 0) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 通过ITM发送字符串
 * @param str 要发送的字符串
 * @retval 0=成功, -1=失败
 */
int ITM_SendString(const char *str)
{
    while (*str) {
        if (ITM_SendChar(*str++) != 0) {
            return -1;
        }
    }
    return 0;
}
```

### DWT（Data Watchpoint and Trace）

DWT提供了数据观察点和性能计数功能：

```c
/**
 * @brief DWT寄存器地址定义
 */
#define DWT_CTRL            0xE0001000  // 控制寄存器
#define DWT_CYCCNT          0xE0001004  // 周期计数器
#define DWT_CPICNT          0xE0001008  // CPI计数器
#define DWT_EXCCNT          0xE000100C  // 异常计数器
#define DWT_SLEEPCNT        0xE0001010  // 睡眠计数器
#define DWT_LSUCNT          0xE0001014  // LSU计数器
#define DWT_FOLDCNT         0xE0001018  // 折叠计数器
#define DWT_COMP0           0xE0001020  // 比较器0
#define DWT_MASK0           0xE0001024  // 掩码0
#define DWT_FUNCTION0       0xE0001028  // 功能0

/**
 * @brief 初始化DWT
 * @retval 0=成功, -1=失败
 */
int DWT_Init(void)
{
    uint32_t demcr;
    
    // 1. 使能跟踪
    if (MEM_Read32(DEMCR, &demcr) != 0) {
        return -1;
    }
    
    demcr |= DEMCR_TRCENA;
    if (MEM_Write32(DEMCR, demcr) != 0) {
        return -1;
    }
    
    // 2. 复位周期计数器
    if (MEM_Write32(DWT_CYCCNT, 0) != 0) {
        return -1;
    }
    
    // 3. 使能周期计数器
    uint32_t dwt_ctrl;
    if (MEM_Read32(DWT_CTRL, &dwt_ctrl) != 0) {
        return -1;
    }
    
    dwt_ctrl |= (1 << 0);  // CYCCNTENA
    if (MEM_Write32(DWT_CTRL, dwt_ctrl) != 0) {
        return -1;
    }
    
    printf("DWT初始化完成\n");
    return 0;
}

/**
 * @brief 设置数据观察点
 * @param comp_num 比较器编号（0-3）
 * @param addr 观察地址
 * @param size 数据大小（0=字节, 1=半字, 2=字）
 * @param function 功能（0=禁用, 4=读, 5=写, 6=读写）
 * @retval 0=成功, -1=失败
 */
int DWT_Set_Watchpoint(uint8_t comp_num, uint32_t addr, 
                       uint8_t size, uint8_t function)
{
    uint32_t comp_base = DWT_COMP0 + (comp_num * 0x10);
    uint32_t mask_base = DWT_MASK0 + (comp_num * 0x10);
    uint32_t func_base = DWT_FUNCTION0 + (comp_num * 0x10);
    
    // 1. 设置比较地址
    if (MEM_Write32(comp_base, addr) != 0) {
        return -1;
    }
    
    // 2. 设置掩码（0表示精确匹配）
    if (MEM_Write32(mask_base, 0) != 0) {
        return -1;
    }
    
    // 3. 设置功能
    uint32_t func_val = (function << 0) | (size << 10);
    if (MEM_Write32(func_base, func_val) != 0) {
        return -1;
    }
    
    printf("数据观察点%d已设置：地址=0x%08X\n", comp_num, addr);
    return 0;
}

/**
 * @brief 清除数据观察点
 * @param comp_num 比较器编号（0-3）
 * @retval 0=成功, -1=失败
 */
int DWT_Clear_Watchpoint(uint8_t comp_num)
{
    uint32_t func_base = DWT_FUNCTION0 + (comp_num * 0x10);
    
    // 禁用比较器
    if (MEM_Write32(func_base, 0) != 0) {
        return -1;
    }
    
    printf("数据观察点%d已清除\n", comp_num);
    return 0;
}
```

### 断点设置

```c
/**
 * @brief FPB寄存器地址定义
 */
#define FPB_CTRL            0xE0002000  // 控制寄存器
#define FPB_REMAP           0xE0002004  // 重映射寄存器
#define FPB_COMP0           0xE0002008  // 比较器0

/**
 * @brief 初始化FPB（Flash Patch and Breakpoint）
 * @retval 0=成功, -1=失败
 */
int FPB_Init(void)
{
    uint32_t fpb_ctrl;
    
    // 读取FPB控制寄存器
    if (MEM_Read32(FPB_CTRL, &fpb_ctrl) != 0) {
        return -1;
    }
    
    // 获取比较器数量
    uint8_t num_code = ((fpb_ctrl >> 8) & 0x70) | ((fpb_ctrl >> 4) & 0x0F);
    uint8_t num_lit = (fpb_ctrl >> 8) & 0x0F;
    
    printf("FPB: %d个代码比较器, %d个字面量比较器\n", num_code, num_lit);
    
    // 使能FPB
    fpb_ctrl |= (1 << 0);  // ENABLE
    fpb_ctrl |= (1 << 1);  // KEY
    
    if (MEM_Write32(FPB_CTRL, fpb_ctrl) != 0) {
        return -1;
    }
    
    printf("FPB初始化完成\n");
    return 0;
}

/**
 * @brief 设置硬件断点
 * @param comp_num 比较器编号
 * @param addr 断点地址
 * @retval 0=成功, -1=失败
 */
int FPB_Set_Breakpoint(uint8_t comp_num, uint32_t addr)
{
    uint32_t comp_addr = FPB_COMP0 + (comp_num * 4);
    
    // 构建比较器值
    // bit[31:2]: 地址[31:2]
    // bit[1]: 保留
    // bit[0]: 使能
    uint32_t comp_val = (addr & 0xFFFFFFFC) | 0x01;
    
    if (MEM_Write32(comp_addr, comp_val) != 0) {
        return -1;
    }
    
    printf("硬件断点%d已设置：地址=0x%08X\n", comp_num, addr);
    return 0;
}

/**
 * @brief 清除硬件断点
 * @param comp_num 比较器编号
 * @retval 0=成功, -1=失败
 */
int FPB_Clear_Breakpoint(uint8_t comp_num)
{
    uint32_t comp_addr = FPB_COMP0 + (comp_num * 4);
    
    // 禁用比较器
    if (MEM_Write32(comp_addr, 0) != 0) {
        return -1;
    }
    
    printf("硬件断点%d已清除\n", comp_num);
    return 0;
}
```



## 第七部分：使用OpenOCD进行调试

### OpenOCD简介

OpenOCD（Open On-Chip Debugger）是一个开源的调试工具，支持多种调试接口和目标芯片。

**OpenOCD架构**：

```
┌─────────────────────────────────────────┐
│         OpenOCD架构                      │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐                      │
│  │   GDB客户端  │                      │
│  └──────────────┘                      │
│         │                               │
│         ↓ GDB协议                       │
│  ┌──────────────┐                      │
│  │  OpenOCD     │                      │
│  │  服务器      │                      │
│  └──────────────┘                      │
│         │                               │
│         ↓ 调试接口                      │
│  ┌──────────────┐                      │
│  │  调试适配器  │                      │
│  │ (ST-Link等)  │                      │
│  └──────────────┘                      │
│         │                               │
│         ↓ JTAG/SWD                     │
│  ┌──────────────┐                      │
│  │  目标芯片    │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
```

### OpenOCD配置文件

**接口配置（stlink.cfg）**：

```tcl
# ST-Link调试器配置
interface stlink

# 传输协议选择
transport select hla_swd

# 适配器速度（kHz）
adapter speed 1000
```

**目标配置（stm32f1x.cfg）**：

```tcl
# STM32F1系列目标配置

# 芯片类型
set CHIPNAME stm32f1x
set WORKAREASIZE 0x5000

# 创建目标
target create $_CHIPNAME.cpu cortex_m -chain-position $_CHIPNAME.cpu

# 工作区域（用于算法）
$_CHIPNAME.cpu configure -work-area-phys 0x20000000 \
                         -work-area-size $WORKAREASIZE \
                         -work-area-backup 0

# Flash配置
flash bank $_CHIPNAME.flash stm32f1x 0x08000000 0 0 0 $_CHIPNAME.cpu

# 复位配置
reset_config srst_only
```

### OpenOCD命令

**启动OpenOCD**：

```bash
# 使用配置文件启动
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg

# 或使用自定义配置
openocd -f my_config.cfg
```

**Telnet连接**：

```bash
# 连接到OpenOCD Telnet服务器（默认端口4444）
telnet localhost 4444
```

**常用OpenOCD命令**：

```tcl
# 停止目标
halt

# 恢复运行
resume

# 单步执行
step

# 复位
reset
reset halt  # 复位并停止

# 读取内存
mdw 0x20000000 10  # 读取10个字（32位）
mdh 0x20000000 10  # 读取10个半字（16位）
mdb 0x20000000 10  # 读取10个字节（8位）

# 写入内存
mww 0x20000000 0x12345678  # 写入字
mwh 0x20000000 0x1234      # 写入半字
mwb 0x20000000 0x12        # 写入字节

# 读取寄存器
reg
reg r0
reg pc

# 写入寄存器
reg r0 0x12345678
reg pc 0x08000000

# 设置断点
bp 0x08000100 2 hw  # 硬件断点
bp 0x08000200 2     # 软件断点

# 删除断点
rbp 0x08000100

# 设置观察点
wp 0x20000000 4 r   # 读观察点
wp 0x20000000 4 w   # 写观察点
wp 0x20000000 4 a   # 读写观察点

# 删除观察点
rwp 0x20000000

# Flash操作
flash probe 0           # 探测Flash
flash info 0            # 显示Flash信息
flash erase_sector 0 0 last  # 擦除所有扇区
flash write_image erase firmware.bin 0x08000000  # 烧写固件

# 显示目标信息
targets
target current
```

### 使用GDB调试

**启动GDB**：

```bash
# 启动ARM GDB
arm-none-eabi-gdb firmware.elf

# 在GDB中连接到OpenOCD
(gdb) target extended-remote localhost:3333

# 加载程序
(gdb) load

# 复位并停止
(gdb) monitor reset halt

# 设置断点
(gdb) break main
(gdb) break *0x08000100

# 运行
(gdb) continue

# 单步执行
(gdb) step
(gdb) next

# 查看寄存器
(gdb) info registers
(gdb) print $r0
(gdb) print $pc

# 查看内存
(gdb) x/10x 0x20000000
(gdb) x/10i $pc

# 查看变量
(gdb) print variable_name
(gdb) print *pointer

# 查看调用栈
(gdb) backtrace
(gdb) frame 0

# 观察点
(gdb) watch variable_name
(gdb) rwatch variable_name  # 读观察点
(gdb) awatch variable_name  # 读写观察点
```

### OpenOCD脚本示例

**自动化调试脚本（debug.tcl）**：

```tcl
# 连接到目标
init

# 停止CPU
halt

# 读取设备ID
set idcode [dap info]
puts "Device ID: $idcode"

# 擦除Flash
flash erase_sector 0 0 last

# 烧写固件
flash write_image erase firmware.bin 0x08000000

# 验证
flash verify_image firmware.bin 0x08000000

# 复位并运行
reset run

# 退出
shutdown
```

**执行脚本**：

```bash
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -f debug.tcl
```

## 第八部分：高级调试技巧

### 调试死锁问题

```c
/**
 * @brief 检测死锁
 * @retval 0=正常, 1=死锁
 */
int Debug_Check_Deadlock(void)
{
    uint32_t dhcsr;
    uint32_t pc1, pc2;
    
    // 1. 读取当前PC
    if (CPU_Halt() != 0) {
        return -1;
    }
    
    if (CPU_Read_Register(15, &pc1) != 0) {
        return -1;
    }
    
    // 2. 恢复运行一小段时间
    if (CPU_Resume() != 0) {
        return -1;
    }
    
    Delay_ms(100);
    
    // 3. 再次读取PC
    if (CPU_Halt() != 0) {
        return -1;
    }
    
    if (CPU_Read_Register(15, &pc2) != 0) {
        return -1;
    }
    
    // 4. 比较PC
    if (pc1 == pc2) {
        printf("检测到死锁！PC=0x%08X\n", pc1);
        
        // 打印寄存器帮助诊断
        CPU_Print_Registers();
        
        return 1;  // 死锁
    }
    
    return 0;  // 正常
}
```

### 内存泄漏检测

```c
/**
 * @brief 监控堆使用情况
 */
void Debug_Monitor_Heap(void)
{
    // 假设堆起始地址和大小已知
    uint32_t heap_start = 0x20001000;
    uint32_t heap_size = 0x1000;
    
    // 定期读取堆内存
    uint32_t *heap_data = malloc(heap_size);
    if (heap_data == NULL) {
        return;
    }
    
    if (MEM_Read_Block(heap_start, heap_data, heap_size / 4) != 0) {
        free(heap_data);
        return;
    }
    
    // 分析堆使用模式
    // 这里可以实现更复杂的分析逻辑
    
    free(heap_data);
}
```

### 性能分析

```c
/**
 * @brief 使用DWT进行性能分析
 */
void Debug_Profile_Function(uint32_t func_addr)
{
    uint32_t start_cycles, end_cycles;
    
    // 1. 在函数入口设置断点
    if (FPB_Set_Breakpoint(0, func_addr) != 0) {
        return;
    }
    
    // 2. 恢复运行
    if (CPU_Resume() != 0) {
        return;
    }
    
    // 3. 等待断点触发
    // （这里需要轮询或使用中断）
    
    // 4. 读取开始周期数
    if (MEM_Read32(DWT_CYCCNT, &start_cycles) != 0) {
        return;
    }
    
    // 5. 单步执行整个函数
    // （这里需要循环单步直到函数返回）
    
    // 6. 读取结束周期数
    if (MEM_Read32(DWT_CYCCNT, &end_cycles) != 0) {
        return;
    }
    
    // 7. 计算执行时间
    uint32_t cycles = end_cycles - start_cycles;
    printf("函数执行周期数: %u\n", cycles);
    
    // 8. 清除断点
    FPB_Clear_Breakpoint(0);
}
```

### 实时日志输出

```c
/**
 * @brief 实时读取ITM输出
 */
void Debug_Read_ITM_Output(void)
{
    // 这个函数应该在主机端运行
    // 通过SWO引脚读取ITM数据
    
    // 伪代码示例：
    while (1) {
        // 读取SWO数据
        uint8_t data = SWO_Read_Byte();
        
        // 解析ITM包
        if (data & 0x01) {  // 激励端口包
            uint8_t port = (data >> 3) & 0x1F;
            uint8_t size = (data & 0x06) >> 1;
            
            // 读取数据
            for (int i = 0; i < (1 << size); i++) {
                uint8_t byte = SWO_Read_Byte();
                printf("%c", byte);
            }
        }
    }
}
```

## 总结

本教程深入讲解了JTAG和SWD调试协议的底层原理和实现方法，主要内容包括：

### 核心要点

1. **JTAG协议**：
   - 5线接口，16状态状态机
   - 支持链式连接多个设备
   - 通过IR和DR寄存器进行操作

2. **SWD协议**：
   - 2线接口，更简单高效
   - 双向数据传输
   - 包格式：请求+ACK+数据

3. **调试端口（DP）**：
   - 提供调试接口访问
   - 控制电源域
   - 错误管理

4. **访问端口（AP）**：
   - MEM-AP用于内存访问
   - 支持自动地址递增
   - 高效的块传输

5. **CPU调试**：
   - 停机、恢复、单步执行
   - 寄存器读写
   - 复位控制

6. **实时跟踪**：
   - ITM：非侵入式日志输出
   - DWT：数据观察点和性能计数
   - FPB：硬件断点

7. **OpenOCD**：
   - 开源调试工具
   - 支持多种接口和目标
   - 与GDB集成

### 最佳实践

1. **调试接口选择**：
   - 单设备优先使用SWD（引脚少）
   - 多设备链式连接使用JTAG
   - 需要实时跟踪时使用SWD+SWO

2. **性能优化**：
   - 使用块传输提高效率
   - 合理设置时钟频率
   - 减少不必要的读写操作

3. **错误处理**：
   - 始终检查ACK响应
   - 处理WAIT和FAULT
   - 清除粘性错误标志

4. **安全考虑**：
   - 保护调试接口
   - 使用调试认证
   - 生产环境禁用调试

### 应用场景

1. **开发调试**：
   - 使用GDB进行源码级调试
   - 设置断点和观察点
   - 查看变量和内存

2. **性能分析**：
   - 使用DWT测量执行时间
   - 分析性能瓶颈
   - 优化关键代码

3. **故障诊断**：
   - 检测死锁和死循环
   - 分析崩溃原因
   - 监控系统状态

4. **生产测试**：
   - 自动化测试脚本
   - Flash烧写
   - 功能验证

## 延伸阅读

推荐进一步学习的内容：

1. **调试技术**：
   - [基于性能计数器的系统性能分析工具](01-performance-analysis-tool.html)
   - [中断向量表与异常处理机制](../beginner/08-interrupt-vector-table.html)
   - [处理器工作模式与特权级别](../beginner/06-processor-modes.html)

2. **CoreSight架构**：
   - ARM CoreSight Architecture Specification
   - ETM（Embedded Trace Macrocell）
   - CTI（Cross Trigger Interface）

3. **调试工具**：
   - OpenOCD官方文档
   - GDB调试指南
   - SEGGER J-Link文档

4. **高级主题**：
   - 多核调试
   - 安全调试（TrustZone）
   - 实时操作系统调试

## 参考资料

1. ARM Debug Interface Architecture Specification (ADIv5)
2. ARM CoreSight Components Technical Reference Manual
3. OpenOCD User's Guide
4. STM32 Programming Manual
5. SEGGER J-Link / J-Trace User Guide

---

**练习题**：

1. 实现一个简单的SWD调试器，能够读取目标芯片的IDCODE。

2. 编写代码通过MEM-AP读写目标芯片的内存，并验证数据正确性。

3. 使用OpenOCD编写脚本，自动化完成以下任务：
   - 连接目标
   - 擦除Flash
   - 烧写固件
   - 验证固件
   - 复位运行

4. 实现一个性能分析工具，使用DWT测量函数执行时间。

5. 配置ITM，实现通过SWO输出调试信息，并在主机端接收显示。

**下一步**：建议学习 [基于性能计数器的系统性能分析工具](01-performance-analysis-tool.html)，将调试技术应用到实际的性能分析中。

