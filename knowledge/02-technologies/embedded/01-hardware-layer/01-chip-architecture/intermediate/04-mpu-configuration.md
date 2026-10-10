---
# 基础信息
title: "MPU内存保护单元配置实战"
description: "深入讲解ARM Cortex-M处理器的MPU（Memory Protection Unit）内存保护单元，掌握MPU区域配置、访问权限设置、内存属性配置和故障处理机制，学习如何设计安全的嵌入式应用系统"
slug: "mpu-configuration-tutorial"

# 分类信息
domain: "01-hardware-layer"
module: "01-chip-architecture"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - MPU
  - 内存保护
  - 系统安全
  - ARM Cortex-M
  - 访问权限
prerequisites:
  - "01-arm-cortex-m-intro"
  - "04-memory-architecture"
  - "06-processor-modes"
related_contents: []

# 学习信息
estimated_time: 55
difficulty_score: 3

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
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - MPU配置
  - 内存保护单元
  - 访问权限控制
  - 内存安全
  - 故障处理
cover_image: ""
---

# MPU内存保护单元配置实战

## 学习目标

完成本教程后，你将能够：

- [ ] 理解MPU的基本概念和工作原理
- [ ] 掌握MPU区域配置方法
- [ ] 配置不同的访问权限和内存属性
- [ ] 实现MPU故障处理机制
- [ ] 设计安全的嵌入式应用系统
- [ ] 调试和排查MPU相关问题


## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 理解ARM Cortex-M处理器架构
- 了解内存映射和地址空间
- 掌握处理器工作模式和特权级别
- 熟悉C语言编程

**技能要求**：
- 能够使用STM32开发板
- 会配置NVIC和中断
- 了解异常处理机制

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| STM32F4开发板 | 1 | 推荐STM32F407VGT6 | - |
| ST-Link调试器 | 1 | 用于程序下载和调试 | - |
| USB数据线 | 1 | 连接开发板和电脑 | - |

### 软件准备

- **开发环境**：STM32CubeIDE v1.10+ 或 Keil MDK
- **调试工具**：ST-Link驱动
- **辅助工具**：串口调试助手

### 环境配置

1. 安装STM32CubeIDE
2. 配置ST-Link驱动
3. 测试开发板连接

## 概述

MPU（Memory Protection Unit，内存保护单元）是ARM Cortex-M处理器中的一个可选硬件模块，用于保护内存区域免受非法访问。通过配置MPU，可以实现：

- **内存访问控制**：限制代码和数据的访问权限
- **系统安全性**：防止恶意代码破坏系统
- **故障隔离**：快速定位内存访问错误
- **RTOS支持**：为任务提供独立的内存空间

### MPU的优势

1. **提高系统安全性**
   - 防止栈溢出
   - 保护关键数据
   - 隔离不可信代码

2. **简化调试**
   - 快速定位内存错误
   - 精确的故障信息
   - 减少调试时间

3. **支持RTOS**
   - 任务内存隔离
   - 防止任务间干扰
   - 提高系统可靠性

### MPU应用场景

- **安全关键系统**：汽车、医疗、工业控制
- **多任务系统**：RTOS环境下的任务隔离
- **固件保护**：防止固件被篡改
- **调试辅助**：快速定位内存访问错误


## 步骤1：理解MPU基本概念

### 1.1 MPU架构

ARM Cortex-M处理器的MPU支持最多8个可编程的内存区域（Region）。

```
MPU架构示意图：

┌─────────────────────────────────────┐
│         MPU控制器                    │
│  ┌──────────┐  ┌──────────┐        │
│  │ Region 0 │  │ Region 1 │  ...   │
│  │ 配置寄存器│  │ 配置寄存器│        │
│  └──────────┘  └──────────┘        │
│       ↓              ↓              │
│  ┌─────────────────────────┐       │
│  │   访问权限检查逻辑       │       │
│  └─────────────────────────┘       │
│              ↓                      │
└──────────────┼──────────────────────┘
               ↓
        ┌──────────────┐
        │  内存访问    │
        │  允许/拒绝   │
        └──────────────┘

特点：
- 最多8个可编程区域
- 每个区域独立配置
- 支持区域重叠（高编号优先）
- 可以动态使能/禁用
```

### 1.2 MPU寄存器

MPU主要通过以下寄存器进行配置：

```c
// MPU类型寄存器（只读）
#define MPU_TYPE    (*((volatile uint32_t*)0xE000ED90))

// MPU控制寄存器
#define MPU_CTRL    (*((volatile uint32_t*)0xE000ED94))

// MPU区域编号寄存器
#define MPU_RNR     (*((volatile uint32_t*)0xE000ED98))

// MPU区域基地址寄存器
#define MPU_RBAR    (*((volatile uint32_t*)0xE000ED9C))

// MPU区域属性和大小寄存器
#define MPU_RASR    (*((volatile uint32_t*)0xE000EDA0))
```

**MPU_TYPE寄存器**：

```
位域说明：
[23:16] DREGION - 支持的数据区域数量
[15:8]  IREGION - 支持的指令区域数量（通常为0）
[0]     SEPARATE - 是否支持独立的指令和数据区域

示例值：0x00000800 表示支持8个数据区域
```

**MPU_CTRL寄存器**：

```c
// MPU控制位定义
#define MPU_CTRL_ENABLE     (1 << 0)  // MPU使能
#define MPU_CTRL_HFNMIENA   (1 << 1)  // HardFault和NMI期间使能MPU
#define MPU_CTRL_PRIVDEFENA (1 << 2)  // 特权模式默认内存映射使能

// 使能MPU
MPU_CTRL = MPU_CTRL_ENABLE | MPU_CTRL_PRIVDEFENA;
```

### 1.3 区域大小和对齐

MPU区域大小必须是2的幂次方，最小32字节，最大4GB。

```c
// 区域大小定义
typedef enum {
    MPU_REGION_SIZE_32B   = 0x04,  // 32字节
    MPU_REGION_SIZE_64B   = 0x05,  // 64字节
    MPU_REGION_SIZE_128B  = 0x06,  // 128字节
    MPU_REGION_SIZE_256B  = 0x07,  // 256字节
    MPU_REGION_SIZE_512B  = 0x08,  // 512字节
    MPU_REGION_SIZE_1KB   = 0x09,  // 1KB
    MPU_REGION_SIZE_2KB   = 0x0A,  // 2KB
    MPU_REGION_SIZE_4KB   = 0x0B,  // 4KB
    MPU_REGION_SIZE_8KB   = 0x0C,  // 8KB
    MPU_REGION_SIZE_16KB  = 0x0D,  // 16KB
    MPU_REGION_SIZE_32KB  = 0x0E,  // 32KB
    MPU_REGION_SIZE_64KB  = 0x0F,  // 64KB
    MPU_REGION_SIZE_128KB = 0x10,  // 128KB
    MPU_REGION_SIZE_256KB = 0x11,  // 256KB
    MPU_REGION_SIZE_512KB = 0x12,  // 512KB
    MPU_REGION_SIZE_1MB   = 0x13,  // 1MB
    MPU_REGION_SIZE_2MB   = 0x14,  // 2MB
    MPU_REGION_SIZE_4MB   = 0x15,  // 4MB
    MPU_REGION_SIZE_8MB   = 0x16,  // 8MB
    MPU_REGION_SIZE_16MB  = 0x17,  // 16MB
    MPU_REGION_SIZE_32MB  = 0x18,  // 32MB
    MPU_REGION_SIZE_64MB  = 0x19,  // 64MB
    MPU_REGION_SIZE_128MB = 0x1A,  // 128MB
    MPU_REGION_SIZE_256MB = 0x1B,  // 256MB
    MPU_REGION_SIZE_512MB = 0x1C,  // 512MB
    MPU_REGION_SIZE_1GB   = 0x1D,  // 1GB
    MPU_REGION_SIZE_2GB   = 0x1E,  // 2GB
    MPU_REGION_SIZE_4GB   = 0x1F   // 4GB
} MPU_RegionSize_t;

// 对齐要求：基地址必须对齐到区域大小
// 例如：64KB区域的基地址必须是64KB的整数倍
```

**预期结果**：
- 理解MPU的基本架构
- 熟悉MPU寄存器功能
- 掌握区域大小和对齐规则


## 步骤2：配置MPU区域

### 2.1 基本配置流程

配置MPU区域的基本步骤：

```c
/**
 * @brief  MPU区域配置基本流程
 */
void mpu_region_config_basic(void) {
    // 1. 禁用MPU
    MPU->CTRL = 0;
    
    // 2. 选择要配置的区域编号（0-7）
    MPU->RNR = 0;  // 配置Region 0
    
    // 3. 设置区域基地址
    MPU->RBAR = 0x20000000;  // SRAM起始地址
    
    // 4. 设置区域属性和大小
    MPU->RASR = (1 << 0)                    // 使能区域
              | (0x03 << 24)                // AP=011（完全访问）
              | (0x0D << 1)                 // 大小=16KB
              | (0 << 16);                  // 禁用子区域
    
    // 5. 使能MPU
    MPU->CTRL = MPU_CTRL_ENABLE | MPU_CTRL_PRIVDEFENA;
    
    // 6. 数据同步屏障
    __DSB();
    __ISB();
}
```

### 2.2 使用HAL库配置

STM32 HAL库提供了更方便的MPU配置接口：

```c
/**
 * @brief  使用HAL库配置MPU区域
 */
void mpu_hal_config_example(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    // 禁用MPU
    HAL_MPU_Disable();
    
    // 配置Region 0: 保护SRAM区域
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_64KB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsShareable = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 使能MPU
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```

### 2.3 完整配置示例

配置多个MPU区域保护不同的内存区域：

```c
/**
 * @brief  完整的MPU配置示例
 */
void mpu_complete_configuration(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    // 禁用MPU
    HAL_MPU_Disable();
    
    // ========== Region 0: Flash区域（只读，可执行） ==========
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_1MB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;  // 特权只读
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;  // 可执行
    MPU_InitStruct.IsShareable = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // ========== Region 1: SRAM区域（读写，不可执行） ==========
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;  // 完全访问
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;  // 不可执行
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // ========== Region 2: 外设区域（读写，不可执行） ==========
    MPU_InitStruct.Number = MPU_REGION_NUMBER2;
    MPU_InitStruct.BaseAddress = 0x40000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_512MB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // ========== Region 3: 栈保护区域（禁止访问） ==========
    // 在栈底部设置一个禁止访问的区域，防止栈溢出
    MPU_InitStruct.Number = MPU_REGION_NUMBER3;
    MPU_InitStruct.BaseAddress = 0x20000000;  // 栈底部
    MPU_InitStruct.Size = MPU_REGION_SIZE_256B;
    MPU_InitStruct.AccessPermission = MPU_REGION_NO_ACCESS;  // 禁止访问
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 使能MPU
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("MPU配置完成\n");
}
```

**预期结果**：
- MPU成功配置
- 不同内存区域有不同的访问权限
- 系统正常运行


## 步骤3：访问权限设置

### 3.1 访问权限类型

MPU支持多种访问权限配置：

```c
// 访问权限定义
typedef enum {
    MPU_REGION_NO_ACCESS        = 0x00,  // 000: 无访问权限
    MPU_REGION_PRIV_RW          = 0x01,  // 001: 特权读写
    MPU_REGION_PRIV_RW_URO      = 0x02,  // 010: 特权读写，用户只读
    MPU_REGION_FULL_ACCESS      = 0x03,  // 011: 完全访问（特权和用户读写）
    // 0x04 保留
    MPU_REGION_PRIV_RO          = 0x05,  // 101: 特权只读
    MPU_REGION_PRIV_RO_URO      = 0x06,  // 110: 特权只读，用户只读
    // 0x07 保留
} MPU_AccessPermission_t;

/**
 * @brief  访问权限配置示例
 */
void mpu_access_permission_examples(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 示例1: 代码区域 - 特权只读，可执行
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_512KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 示例2: 数据区域 - 完全访问，不可执行
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_64KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 示例3: 只读数据区域 - 特权和用户只读
    MPU_InitStruct.Number = MPU_REGION_NUMBER2;
    MPU_InitStruct.BaseAddress = 0x08080000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_64KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO_URO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 示例4: 保护区域 - 禁止访问
    MPU_InitStruct.Number = MPU_REGION_NUMBER3;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_256B;
    MPU_InitStruct.AccessPermission = MPU_REGION_NO_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```

### 3.2 特权级别与访问权限

访问权限与处理器特权级别的关系：

```
访问权限表：

AP[2:0] | 特权模式 | 用户模式 | 说明
--------|---------|---------|------------------
  000   |   无    |   无    | 完全禁止访问
  001   |   读写  |   无    | 仅特权模式可访问
  010   |   读写  |   只读  | 特权读写，用户只读
  011   |   读写  |   读写  | 完全访问
  101   |   只读  |   无    | 仅特权模式只读
  110   |   只读  |   只读  | 所有模式只读

应用场景：
- 000: 栈保护区、未使用区域
- 001: 系统关键数据、配置寄存器
- 010: 共享只读数据
- 011: 普通数据区域
- 101: 代码区域、常量数据
- 110: 全局只读配置
```

### 3.3 执行权限控制

通过XN（eXecute Never）位控制代码执行：

```c
/**
 * @brief  执行权限控制示例
 */
void mpu_execute_permission_example(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 场景1: Flash代码区域 - 可执行
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_1MB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;  // 可执行
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 场景2: SRAM数据区域 - 不可执行（防止代码注入攻击）
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;  // 不可执行
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 场景3: SRAM代码区域 - 可执行（用于动态加载代码）
    MPU_InitStruct.Number = MPU_REGION_NUMBER2;
    MPU_InitStruct.BaseAddress = 0x20010000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_16KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RW;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;  // 可执行
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("执行权限配置完成\n");
}

/**
 * @brief  测试执行权限
 */
void test_execute_permission(void) {
    // 定义一个简单的函数
    typedef void (*func_ptr_t)(void);
    
    // 在SRAM中的函数（如果配置为不可执行，会触发MemManage异常）
    uint32_t sram_code[] = {
        0x4770,  // BX LR (Thumb指令：返回)
    };
    
    func_ptr_t sram_func = (func_ptr_t)((uint32_t)sram_code | 0x01);
    
    printf("尝试执行SRAM中的代码...\n");
    sram_func();  // 如果SRAM配置为不可执行，这里会触发异常
    printf("执行成功\n");
}
```

**预期结果**：
- 不同区域有正确的访问权限
- 代码区域可执行，数据区域不可执行
- 非法访问会触发MemManage异常


## 步骤4：内存属性配置

### 4.1 内存类型和属性

MPU支持配置内存的缓存和缓冲属性：

```c
/**
 * @brief  内存属性配置
 * 
 * TEX[2:0] | C | B | 内存类型 | 说明
 * ---------|---|---|---------|------------------
 *   000    | 0 | 0 | Strongly-ordered | 严格有序
 *   000    | 0 | 1 | Device | 设备内存
 *   000    | 1 | 0 | Normal | 普通内存（不可缓存）
 *   000    | 1 | 1 | Normal | 普通内存（写通缓存）
 *   001    | 0 | 0 | Normal | 普通内存（写回缓存）
 *   001    | 0 | 1 | Normal | 普通内存（写回缓存）
 *   001    | 1 | 0 | Normal | 普通内存（不可缓存）
 *   001    | 1 | 1 | Normal | 普通内存（写回缓存）
 */

void mpu_memory_attributes_config(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 配置1: Flash - 可缓存，不可缓冲
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_1MB;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;      // C=1
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE; // B=0
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置2: SRAM - 可缓存，可缓冲
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;    // C=1
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;  // B=1
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置3: 外设 - 不可缓存，可缓冲（设备内存）
    MPU_InitStruct.Number = MPU_REGION_NUMBER2;
    MPU_InitStruct.BaseAddress = 0x40000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_512MB;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;  // C=0
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;    // B=1
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```

### 4.2 共享属性

共享属性用于多核系统或DMA访问：

```c
/**
 * @brief  共享属性配置
 */
void mpu_shareable_config(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 非共享区域 - 单核独占
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_64KB;
    MPU_InitStruct.IsShareable = MPU_ACCESS_NOT_SHAREABLE;  // 非共享
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 共享区域 - DMA缓冲区
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20010000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_16KB;
    MPU_InitStruct.IsShareable = MPU_ACCESS_SHAREABLE;  // 共享
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;  // DMA区域通常不缓存
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```

### 4.3 子区域禁用

每个MPU区域可以分为8个子区域，可以单独禁用：

```c
/**
 * @brief  子区域禁用示例
 */
void mpu_subregion_disable_example(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 配置一个64KB的区域，禁用第一个8KB子区域
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_64KB;  // 64KB = 8个8KB子区域
    
    // 子区域禁用位图（bit0对应第一个子区域）
    // 0x01 = 0b00000001 - 禁用第一个子区域（0x20000000-0x20001FFF）
    MPU_InitStruct.SubRegionDisable = 0x01;
    
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("子区域配置：\n");
    printf("  总区域: 0x20000000 - 0x2000FFFF (64KB)\n");
    printf("  禁用区域: 0x20000000 - 0x20001FFF (8KB)\n");
    printf("  可用区域: 0x20002000 - 0x2000FFFF (56KB)\n");
}

/**
 * @brief  使用子区域实现栈保护
 */
void mpu_stack_guard_with_subregion(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 假设栈区域为32KB，从0x20008000开始
    // 禁用最低的4KB作为栈保护区
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x20008000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_32KB;  // 32KB = 8个4KB子区域
    
    // 禁用第一个子区域（栈底部4KB）
    MPU_InitStruct.SubRegionDisable = 0x01;
    
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("栈保护配置完成\n");
    printf("  栈区域: 0x20008000 - 0x2000FFFF\n");
    printf("  保护区: 0x20008000 - 0x20008FFF (禁止访问)\n");
    printf("  可用栈: 0x20009000 - 0x2000FFFF\n");
}
```

**预期结果**：
- 内存属性正确配置
- 缓存和缓冲行为符合预期
- 子区域禁用功能正常工作


## 步骤5：故障处理机制

### 5.1 MemManage异常

MPU违规访问会触发MemManage异常：

```c
/**
 * @brief  MemManage异常处理函数
 */
void MemManage_Handler(void) {
    // 读取故障状态寄存器
    uint32_t cfsr = SCB->CFSR;
    uint32_t mmfsr = cfsr & 0xFF;  // MemManage Fault Status Register
    
    printf("\n=== MemManage Fault ===\n");
    
    // 分析故障原因
    if (mmfsr & SCB_CFSR_IACCVIOL_Msk) {
        printf("指令访问违规\n");
    }
    if (mmfsr & SCB_CFSR_DACCVIOL_Msk) {
        printf("数据访问违规\n");
    }
    if (mmfsr & SCB_CFSR_MUNSTKERR_Msk) {
        printf("异常返回时出栈错误\n");
    }
    if (mmfsr & SCB_CFSR_MSTKERR_Msk) {
        printf("异常入口时入栈错误\n");
    }
    if (mmfsr & SCB_CFSR_MLSPERR_Msk) {
        printf("浮点延迟状态保存错误\n");
    }
    
    // 如果MMARVALID位置位，读取故障地址
    if (mmfsr & SCB_CFSR_MMARVALID_Msk) {
        uint32_t mmfar = SCB->MMFAR;
        printf("故障地址: 0x%08X\n", (unsigned int)mmfar);
    }
    
    // 清除故障标志
    SCB->CFSR = mmfsr;
    
    // 进入死循环或重启系统
    while (1) {
        __NOP();
    }
}

/**
 * @brief  使能MemManage异常
 */
void enable_memmanage_fault(void) {
    // 使能MemManage异常
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk;
    
    // 设置MemManage异常优先级
    NVIC_SetPriority(MemoryManagement_IRQn, 0);
    
    printf("MemManage异常已使能\n");
}
```

### 5.2 故障调试技巧

```c
/**
 * @brief  MPU故障调试辅助函数
 */
void mpu_fault_debug_info(void) {
    uint32_t cfsr = SCB->CFSR;
    uint32_t mmfsr = cfsr & 0xFF;
    
    printf("\n=== MPU故障调试信息 ===\n");
    
    // 打印MPU配置
    printf("MPU控制寄存器: 0x%08X\n", (unsigned int)MPU->CTRL);
    printf("MPU类型寄存器: 0x%08X\n", (unsigned int)MPU->TYPE);
    
    // 打印所有区域配置
    for (int i = 0; i < 8; i++) {
        MPU->RNR = i;
        uint32_t rbar = MPU->RBAR;
        uint32_t rasr = MPU->RASR;
        
        if (rasr & 0x01) {  // 区域使能
            printf("\nRegion %d:\n", i);
            printf("  基地址: 0x%08X\n", (unsigned int)(rbar & 0xFFFFFFE0));
            printf("  大小: %d\n", (int)((rasr >> 1) & 0x1F));
            printf("  访问权限: 0x%X\n", (unsigned int)((rasr >> 24) & 0x07));
            printf("  XN: %d\n", (int)((rasr >> 28) & 0x01));
        }
    }
    
    // 打印故障信息
    if (mmfsr) {
        printf("\n故障状态: 0x%02X\n", (unsigned int)mmfsr);
        if (mmfsr & SCB_CFSR_MMARVALID_Msk) {
            printf("故障地址: 0x%08X\n", (unsigned int)SCB->MMFAR);
        }
    }
}

/**
 * @brief  测试MPU保护
 */
void test_mpu_protection(void) {
    printf("\n=== 测试MPU保护 ===\n");
    
    // 测试1: 访问禁止区域
    printf("测试1: 访问禁止区域...\n");
    volatile uint32_t *forbidden_addr = (uint32_t*)0x20000000;
    // *forbidden_addr = 0x12345678;  // 取消注释会触发MemManage异常
    printf("测试1跳过（避免触发异常）\n");
    
    // 测试2: 执行数据区域的代码
    printf("测试2: 执行数据区域的代码...\n");
    typedef void (*func_t)(void);
    uint32_t code_in_data[] = {0x4770};  // BX LR
    func_t func = (func_t)((uint32_t)code_in_data | 0x01);
    // func();  // 取消注释会触发MemManage异常
    printf("测试2跳过（避免触发异常）\n");
    
    // 测试3: 写入只读区域
    printf("测试3: 写入只读区域...\n");
    volatile uint32_t *readonly_addr = (uint32_t*)0x08000000;
    // *readonly_addr = 0xDEADBEEF;  // 取消注释会触发MemManage异常
    printf("测试3跳过（避免触发异常）\n");
    
    printf("所有测试完成\n");
}
```

### 5.3 故障恢复策略

```c
/**
 * @brief  MPU故障恢复策略
 */
typedef enum {
    MPU_FAULT_ACTION_HALT,      // 停止系统
    MPU_FAULT_ACTION_RESET,     // 重启系统
    MPU_FAULT_ACTION_LOG,       // 记录日志并继续
    MPU_FAULT_ACTION_RECOVER    // 尝试恢复
} MPU_FaultAction_t;

MPU_FaultAction_t mpu_fault_action = MPU_FAULT_ACTION_HALT;

/**
 * @brief  改进的MemManage异常处理
 */
void MemManage_Handler_Advanced(void) {
    uint32_t cfsr = SCB->CFSR;
    uint32_t mmfsr = cfsr & 0xFF;
    uint32_t fault_addr = 0;
    
    // 记录故障信息
    if (mmfsr & SCB_CFSR_MMARVALID_Msk) {
        fault_addr = SCB->MMFAR;
    }
    
    // 记录到日志
    log_mpu_fault(mmfsr, fault_addr);
    
    // 清除故障标志
    SCB->CFSR = mmfsr;
    
    // 根据策略处理
    switch (mpu_fault_action) {
        case MPU_FAULT_ACTION_HALT:
            printf("系统停止\n");
            while (1);
            break;
            
        case MPU_FAULT_ACTION_RESET:
            printf("系统重启\n");
            NVIC_SystemReset();
            break;
            
        case MPU_FAULT_ACTION_LOG:
            printf("记录日志并继续\n");
            // 返回到下一条指令（需要修改栈帧）
            break;
            
        case MPU_FAULT_ACTION_RECOVER:
            printf("尝试恢复\n");
            // 实现恢复逻辑
            break;
    }
}

/**
 * @brief  记录MPU故障日志
 */
void log_mpu_fault(uint32_t mmfsr, uint32_t fault_addr) {
    // 保存到Flash或发送到远程服务器
    printf("MPU故障日志:\n");
    printf("  时间戳: %u\n", (unsigned int)HAL_GetTick());
    printf("  故障状态: 0x%02X\n", (unsigned int)mmfsr);
    printf("  故障地址: 0x%08X\n", (unsigned int)fault_addr);
    
    // 保存到非易失性存储
    // save_to_flash(...);
}
```

**预期结果**：
- MemManage异常正确触发
- 故障信息准确记录
- 故障恢复策略有效


## 步骤6：安全应用设计

### 6.1 栈溢出保护

使用MPU保护栈区域，防止栈溢出：

```c
/**
 * @brief  栈溢出保护配置
 */
void mpu_stack_overflow_protection(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    // 获取栈信息（从链接脚本或启动文件）
    extern uint32_t _sstack;  // 栈底
    extern uint32_t _estack;  // 栈顶
    
    uint32_t stack_base = (uint32_t)&_sstack;
    uint32_t stack_size = (uint32_t)&_estack - stack_base;
    
    HAL_MPU_Disable();
    
    // 配置栈保护区（栈底部256字节禁止访问）
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = stack_base;
    MPU_InitStruct.Size = MPU_REGION_SIZE_256B;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.AccessPermission = MPU_REGION_NO_ACCESS;  // 禁止访问
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置正常栈区域
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = stack_base + 256;
    MPU_InitStruct.Size = MPU_REGION_SIZE_16KB;  // 根据实际栈大小调整
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("栈溢出保护已配置\n");
    printf("  栈底保护区: 0x%08X - 0x%08X\n", 
           (unsigned int)stack_base, 
           (unsigned int)(stack_base + 255));
}

/**
 * @brief  测试栈溢出保护
 */
void test_stack_overflow_protection(void) {
    printf("测试栈溢出保护...\n");
    
    // 递归函数，会导致栈溢出
    void recursive_function(int depth) {
        char buffer[1024];  // 大数组加速栈消耗
        buffer[0] = depth;
        
        printf("递归深度: %d\n", depth);
        
        if (depth < 100) {
            recursive_function(depth + 1);
        }
    }
    
    // 取消注释以测试（会触发MemManage异常）
    // recursive_function(0);
    
    printf("测试跳过（避免触发异常）\n");
}
```

### 6.2 代码注入防护

防止在数据区域执行代码：

```c
/**
 * @brief  代码注入防护配置
 */
void mpu_code_injection_protection(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 配置Flash代码区域 - 可执行
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_1MB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;  // 可执行
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置SRAM数据区域 - 不可执行
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;  // 不可执行
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("代码注入防护已配置\n");
    printf("  Flash区域: 可执行\n");
    printf("  SRAM区域: 不可执行\n");
}
```

### 6.3 关键数据保护

保护系统关键配置和密钥：

```c
/**
 * @brief  关键数据保护
 */
#define SECURE_DATA_BASE  0x20010000
#define SECURE_DATA_SIZE  4096

typedef struct {
    uint32_t magic;
    uint8_t  aes_key[32];
    uint32_t device_id;
    uint32_t checksum;
} SecureData_t;

__attribute__((section(".secure_data")))
SecureData_t secure_data;

void mpu_critical_data_protection(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 配置安全数据区域 - 特权只读
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = SECURE_DATA_BASE;
    MPU_InitStruct.Size = MPU_REGION_SIZE_4KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;  // 特权只读
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("关键数据保护已配置\n");
}

/**
 * @brief  安全数据访问接口
 */
void secure_data_write(const SecureData_t *data) {
    // 临时禁用MPU保护
    HAL_MPU_Disable();
    
    // 写入数据
    memcpy(&secure_data, data, sizeof(SecureData_t));
    
    // 重新使能MPU保护
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    printf("安全数据已更新\n");
}

const SecureData_t* secure_data_read(void) {
    // 读取不需要禁用MPU（配置为只读）
    return &secure_data;
}
```

### 6.4 RTOS任务隔离

在RTOS环境中使用MPU隔离任务：

```c
/**
 * @brief  RTOS任务MPU配置
 */
typedef struct {
    uint32_t stack_base;
    uint32_t stack_size;
    uint32_t data_base;
    uint32_t data_size;
} TaskMemoryConfig_t;

void mpu_task_isolation_config(TaskMemoryConfig_t *task_config) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // 配置任务栈区域
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = task_config->stack_base;
    MPU_InitStruct.Size = get_mpu_size(task_config->stack_size);
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置任务数据区域
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = task_config->data_base;
    MPU_InitStruct.Size = get_mpu_size(task_config->data_size);
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}

/**
 * @brief  获取MPU区域大小编码
 */
uint32_t get_mpu_size(uint32_t size_bytes) {
    // 将字节大小转换为MPU大小编码
    uint32_t size_code = 0;
    uint32_t temp_size = size_bytes;
    
    while (temp_size > 32) {
        temp_size >>= 1;
        size_code++;
    }
    
    return size_code + 4;  // MPU_REGION_SIZE_32B = 0x04
}

/**
 * @brief  FreeRTOS任务切换时更新MPU配置
 */
void vPortTaskSwitchHook(void *pxCurrentTCB, void *pxNewTCB) {
    // 获取新任务的内存配置
    TaskMemoryConfig_t *new_task_config = get_task_memory_config(pxNewTCB);
    
    // 更新MPU配置
    mpu_task_isolation_config(new_task_config);
}
```

**预期结果**：
- 栈溢出被MPU检测到
- 数据区域无法执行代码
- 关键数据受到保护
- RTOS任务内存隔离有效


## 故障排除

### 问题1：MPU配置后系统无法启动

**可能原因**：
- MPU区域配置错误，覆盖了关键内存
- 栈区域被禁用
- 中断向量表区域不可访问

**解决方法**：
1. 检查MPU区域配置是否正确
2. 确保栈区域可访问
3. 确保Flash代码区域可执行
4. 使用调试器单步跟踪启动过程

```c
// 调试代码
void debug_mpu_config(void) {
    printf("MPU配置检查:\n");
    printf("MPU_CTRL: 0x%08X\n", (unsigned int)MPU->CTRL);
    
    for (int i = 0; i < 8; i++) {
        MPU->RNR = i;
        if (MPU->RASR & 0x01) {
            printf("Region %d: Base=0x%08X, RASR=0x%08X\n", 
                   i, (unsigned int)MPU->RBAR, (unsigned int)MPU->RASR);
        }
    }
}
```

### 问题2：MemManage异常频繁触发

**可能原因**：
- 区域大小或对齐不正确
- 访问权限配置过于严格
- 代码访问了未配置的区域

**解决方法**：
1. 检查区域大小和对齐
2. 放宽访问权限进行测试
3. 在MemManage_Handler中打印详细信息
4. 使用MPU_PRIVILEGED_DEFAULT模式

```c
// 详细的故障信息
void detailed_memmanage_info(void) {
    uint32_t cfsr = SCB->CFSR;
    uint32_t mmfsr = cfsr & 0xFF;
    
    printf("CFSR: 0x%08X\n", (unsigned int)cfsr);
    printf("MMFSR: 0x%02X\n", (unsigned int)mmfsr);
    
    if (mmfsr & SCB_CFSR_MMARVALID_Msk) {
        printf("MMFAR: 0x%08X\n", (unsigned int)SCB->MMFAR);
    }
    
    // 打印栈回溯
    print_stack_trace();
}
```

### 问题3：DMA传输失败

**可能原因**：
- DMA缓冲区在MPU保护区域内
- 内存属性配置不当（缓存问题）
- 共享属性未正确配置

**解决方法**：
1. 将DMA缓冲区放在可访问区域
2. 配置DMA区域为非缓存
3. 设置共享属性
4. 使用Cache清理/无效化操作

```c
// DMA缓冲区MPU配置
void mpu_dma_buffer_config(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    HAL_MPU_Disable();
    
    // DMA缓冲区：非缓存，可缓冲，共享
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x20010000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_16KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsShareable = MPU_ACCESS_SHAREABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```

### 问题4：性能下降

**可能原因**：
- 过多的MPU区域检查
- 缓存属性配置不当
- 区域重叠导致额外开销

**解决方法**：
1. 减少MPU区域数量
2. 优化缓存配置
3. 避免不必要的区域重叠
4. 使用性能计数器测量影响

```c
// 性能测试
void test_mpu_performance(void) {
    uint32_t start, end;
    volatile uint32_t data;
    
    // 测试1：无MPU
    HAL_MPU_Disable();
    start = DWT->CYCCNT;
    for (int i = 0; i < 10000; i++) {
        data = *(volatile uint32_t*)0x20000000;
    }
    end = DWT->CYCCNT;
    printf("无MPU: %u 周期\n", (unsigned int)(end - start));
    
    // 测试2：有MPU
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    start = DWT->CYCCNT;
    for (int i = 0; i < 10000; i++) {
        data = *(volatile uint32_t*)0x20000000;
    }
    end = DWT->CYCCNT;
    printf("有MPU: %u 周期\n", (unsigned int)(end - start));
}
```

## 总结

通过本教程，你学习了：

- ✅ MPU的基本概念和架构
- ✅ MPU区域配置方法
- ✅ 访问权限和内存属性设置
- ✅ 故障处理和调试技巧
- ✅ 安全应用设计实践

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现一个完整的栈溢出检测系统
   - 配置栈保护区
   - 实现故障恢复机制
   - 记录故障日志

2. **挑战2**：为FreeRTOS任务配置MPU隔离
   - 每个任务独立的内存空间
   - 任务间通信机制
   - 权限管理

3. **挑战3**：实现安全启动流程
   - 使用MPU保护Bootloader
   - 验证应用程序完整性
   - 防止固件篡改

## 完整代码

完整的MPU配置示例代码：

```c
/**
 * @file    mpu_config.c
 * @brief   MPU完整配置示例
 */

#include "stm32f4xx_hal.h"
#include <stdio.h>

// 使能MemManage异常
void MPU_Init(void) {
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    // 禁用MPU
    HAL_MPU_Disable();
    
    // Region 0: Flash (1MB, 只读, 可执行)
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_1MB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_PRIV_RO;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;
    MPU_InitStruct.IsShareable = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // Region 1: SRAM (128KB, 读写, 不可执行)
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // Region 2: 外设 (512MB, 读写, 不可执行)
    MPU_InitStruct.Number = MPU_REGION_NUMBER2;
    MPU_InitStruct.BaseAddress = 0x40000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_512MB;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_NOT_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // Region 3: 栈保护区 (256B, 禁止访问)
    MPU_InitStruct.Number = MPU_REGION_NUMBER3;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_256B;
    MPU_InitStruct.AccessPermission = MPU_REGION_NO_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_DISABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 使能MPU
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
    
    // 使能MemManage异常
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk;
    
    printf("MPU初始化完成\n");
}

// MemManage异常处理
void MemManage_Handler(void) {
    uint32_t cfsr = SCB->CFSR;
    uint32_t mmfsr = cfsr & 0xFF;
    
    printf("\n=== MemManage Fault ===\n");
    printf("MMFSR: 0x%02X\n", (unsigned int)mmfsr);
    
    if (mmfsr & SCB_CFSR_MMARVALID_Msk) {
        printf("Fault Address: 0x%08X\n", (unsigned int)SCB->MMFAR);
    }
    
    // 清除故障标志
    SCB->CFSR = mmfsr;
    
    while (1);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 初始化MPU
    MPU_Init();
    
    // 应用程序代码
    while (1) {
        HAL_Delay(1000);
    }
}
```

## 下一步

建议继续学习：

- [浮点运算单元FPU使用指南](05-fpu-usage.html) - 学习FPU配置和使用
- [性能计数器与系统性能分析](../advanced/01-performance-analysis-tool.html) - 学习性能优化
- [JTAG与SWD调试技术](../advanced/02-jtag-swd-deep-dive.html) - 深入学习调试技术

## 参考资料

1. ARM Cortex-M4 Technical Reference Manual
2. STM32F4 Reference Manual - MPU章节
3. ARM Architecture Reference Manual
4. Application Note: Using the MPU on Cortex-M processors

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言！
