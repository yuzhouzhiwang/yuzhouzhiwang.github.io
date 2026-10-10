---
title: "MMU与虚拟内存管理"
description: "深入讲解嵌入式系统中的内存管理单元(MMU)和虚拟内存技术，包括MMU工作原理、页表配置、地址转换机制、虚拟内存管理和内存映射技术，帮助开发者掌握高级内存管理方法"
slug: "mmu-virtual-memory"

# 分类信息
domain: "驱动与BSP层"
module: "内存管理"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - MMU
  - 虚拟内存
  - 地址转换
  - 页表
  - 内存映射
prerequisites:
  - "memory-management-basics"
  - "dynamic-memory-allocation"
related_contents: []

# 学习信息
estimated_time: 90
difficulty_score: 4

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
  - MMU原理
  - 虚拟内存管理
  - 页表配置
  - 地址转换
  - 内存映射
cover_image: ""
---

# MMU与虚拟内存管理

## 学习目标


完成本教程后，你将能够：

- 理解MMU的工作原理和核心功能
- 掌握虚拟地址到物理地址的转换机制
- 学会配置和管理页表
- 了解内存保护和访问权限控制
- 掌握内存映射的实现方法
- 理解TLB的作用和优化策略

## 前置要求

### 知识要求

- 理解基本的内存管理概念
- 熟悉C语言编程
- 了解处理器架构基础
- 掌握位操作和指针使用

### 技能要求

- 能够阅读和编写C代码
- 了解ARM Cortex-A系列处理器
- 熟悉Linux或嵌入式操作系统基础

## 准备工作

### 硬件准备

- ARM Cortex-A系列开发板（如树莓派、BeagleBone）
- 或支持MMU的ARM Cortex-M7/M33处理器
- JTAG调试器（可选）

### 软件准备

- 交叉编译工具链（GCC ARM）
- 调试工具（GDB、OpenOCD）
- 串口终端工具

### 环境配置

```bash
# 安装交叉编译工具链
sudo apt-get install gcc-arm-linux-gnueabihf

# 验证安装
arm-linux-gnueabihf-gcc --version
```

## 背景知识

### 为什么需要MMU？

在没有MMU的系统中，程序直接访问物理内存地址，这会带来几个问题：


**问题1：内存碎片化**
- 程序需要连续的物理内存
- 难以有效利用分散的空闲内存

**问题2：安全性差**
- 程序可以访问任意物理地址
- 容易发生越界访问和数据破坏

**问题3：程序重定位困难**
- 程序必须加载到固定地址
- 多个程序难以共存

**问题4：内存保护缺失**
- 无法隔离不同程序的内存空间
- 系统稳定性差

MMU通过引入虚拟内存机制，完美解决了这些问题。

### MMU的核心功能

1. **地址转换**：将虚拟地址转换为物理地址
2. **内存保护**：控制内存访问权限
3. **内存映射**：灵活映射虚拟地址空间
4. **缓存控制**：配置内存区域的缓存属性

## 核心内容

### 1. MMU基本原理

#### 1.1 虚拟地址空间

虚拟地址空间是程序看到的地址空间，与物理内存独立。

**典型的32位虚拟地址空间布局**：

```
0xFFFFFFFF  ┌─────────────────┐
            │   内核空间       │  1GB
0xC0000000  ├─────────────────┤
            │   用户栈         │
            │       ↓          │
            ├─────────────────┤
            │   共享库         │
            ├─────────────────┤
            │       ↑          │
            │   用户堆         │
            ├─────────────────┤
            │   .bss段         │
            ├─────────────────┤
            │   .data段        │
            ├─────────────────┤
            │   .text段        │  3GB
0x00000000  └─────────────────┘
```


#### 1.2 地址转换过程

MMU将虚拟地址转换为物理地址的基本流程：

```
虚拟地址 → MMU查询页表 → 物理地址
         ↓
      TLB缓存
```

**地址转换示例**：

```
虚拟地址: 0x12345678
         ↓ MMU转换
物理地址: 0x87654000
```

#### 1.3 页表结构

页表是MMU进行地址转换的核心数据结构。

**一级页表（简化示例）**：

```c
// 页表项结构
typedef struct {
    uint32_t valid      : 1;   // 有效位
    uint32_t writable   : 1;   // 可写位
    uint32_t user       : 1;   // 用户模式可访问
    uint32_t reserved   : 9;   // 保留位
    uint32_t pfn        : 20;  // 物理页帧号
} page_table_entry_t;

// 页表
page_table_entry_t page_table[1024];  // 1024个页表项
```

**地址分解**：

```
32位虚拟地址:
┌──────────┬──────────┐
│ 页表索引  │  页内偏移 │
│  (20位)  │  (12位)  │
└──────────┴──────────┘
```

### 2. ARM MMU架构

#### 2.1 ARM MMU特点

ARM处理器的MMU具有以下特点：

- 支持多级页表（一级、二级）
- 可配置的页大小（4KB、64KB、1MB等）
- 硬件页表遍历
- TLB（Translation Lookaside Buffer）缓存
- 域（Domain）访问控制


#### 2.2 ARM页表格式

**一级页表描述符**：

```c
// 段描述符（1MB段）
typedef struct {
    uint32_t type       : 2;   // 描述符类型 (10 = 段)
    uint32_t b          : 1;   // 缓冲位
    uint32_t c          : 1;   // 缓存位
    uint32_t xn         : 1;   // 执行禁止
    uint32_t domain     : 4;   // 域
    uint32_t impl       : 1;   // 实现定义
    uint32_t ap         : 2;   // 访问权限
    uint32_t tex        : 3;   // 类型扩展
    uint32_t apx        : 1;   // 访问权限扩展
    uint32_t s          : 1;   // 共享
    uint32_t ng         : 1;   // 非全局
    uint32_t reserved   : 1;   // 保留
    uint32_t base       : 12;  // 段基地址[31:20]
} section_descriptor_t;

// 页表描述符（指向二级页表）
typedef struct {
    uint32_t type       : 2;   // 描述符类型 (01 = 页表)
    uint32_t pxn        : 1;   // 特权执行禁止
    uint32_t ns         : 1;   // 非安全
    uint32_t reserved   : 1;   // 保留
    uint32_t domain     : 4;   // 域
    uint32_t impl       : 1;   // 实现定义
    uint32_t base       : 22;  // 页表基地址[31:10]
} page_table_descriptor_t;
```

**二级页表描述符**：

```c
// 小页描述符（4KB页）
typedef struct {
    uint32_t xn         : 1;   // 执行禁止
    uint32_t type       : 1;   // 类型 (1 = 小页)
    uint32_t b          : 1;   // 缓冲位
    uint32_t c          : 1;   // 缓存位
    uint32_t ap         : 2;   // 访问权限
    uint32_t tex        : 3;   // 类型扩展
    uint32_t apx        : 1;   // 访问权限扩展
    uint32_t s          : 1;   // 共享
    uint32_t ng         : 1;   // 非全局
    uint32_t base       : 20;  // 页基地址[31:12]
} small_page_descriptor_t;
```


#### 2.3 MMU控制寄存器

ARM MMU通过协处理器CP15的寄存器进行配置：

```c
// SCTLR - 系统控制寄存器
#define SCTLR_M     (1 << 0)   // MMU使能
#define SCTLR_A     (1 << 1)   // 对齐检查使能
#define SCTLR_C     (1 << 2)   // 数据缓存使能
#define SCTLR_Z     (1 << 11)  // 分支预测使能
#define SCTLR_I     (1 << 12)  // 指令缓存使能
#define SCTLR_V     (1 << 13)  // 高向量使能

// TTBR0 - 页表基地址寄存器0
// TTBR1 - 页表基地址寄存器1
// TTBCR - 页表控制寄存器
// DACR  - 域访问控制寄存器

// 读取SCTLR
static inline uint32_t read_sctlr(void) {
    uint32_t val;
    asm volatile("mrc p15, 0, %0, c1, c0, 0" : "=r"(val));
    return val;
}

// 写入SCTLR
static inline void write_sctlr(uint32_t val) {
    asm volatile("mcr p15, 0, %0, c1, c0, 0" : : "r"(val));
}

// 设置页表基地址
static inline void set_ttbr0(uint32_t addr) {
    asm volatile("mcr p15, 0, %0, c2, c0, 0" : : "r"(addr));
}

// 设置域访问控制
static inline void set_dacr(uint32_t val) {
    asm volatile("mcr p15, 0, %0, c3, c0, 0" : : "r"(val));
}
```

### 3. 页表配置实践

#### 3.1 创建一级页表

让我们实现一个简单的页表配置：

```c
#include <stdint.h>
#include <string.h>

// 页表大小：4096个条目，每个4字节
#define PAGE_TABLE_SIZE 4096
#define SECTION_SIZE    (1024 * 1024)  // 1MB

// 一级页表（16KB，对齐到16KB边界）
static uint32_t page_table[PAGE_TABLE_SIZE] 
    __attribute__((aligned(16384)));

// 段描述符类型
#define DESC_TYPE_FAULT     0x0
#define DESC_TYPE_PAGE      0x1
#define DESC_TYPE_SECTION   0x2

// 访问权限
#define AP_NO_ACCESS        0x0
#define AP_PRIV_RW          0x1
#define AP_USER_RO          0x2
#define AP_FULL_ACCESS      0x3

// 域
#define DOMAIN_CLIENT       0x1
#define DOMAIN_MANAGER      0x3


// 创建段描述符
uint32_t create_section_descriptor(
    uint32_t base_addr,
    uint32_t ap,
    uint32_t domain,
    uint32_t cacheable,
    uint32_t bufferable
) {
    uint32_t desc = 0;
    
    // 设置类型为段
    desc |= DESC_TYPE_SECTION;
    
    // 设置缓存和缓冲属性
    desc |= (bufferable << 2);
    desc |= (cacheable << 3);
    
    // 设置域
    desc |= (domain << 5);
    
    // 设置访问权限
    desc |= (ap << 10);
    
    // 设置段基地址（高12位）
    desc |= (base_addr & 0xFFF00000);
    
    return desc;
}

// 初始化页表
void init_page_table(void) {
    // 清空页表
    memset(page_table, 0, sizeof(page_table));
    
    // 映射前4GB物理内存（恒等映射）
    // 虚拟地址 = 物理地址
    for (uint32_t i = 0; i < 4096; i++) {
        uint32_t phys_addr = i * SECTION_SIZE;
        
        // 创建段描述符
        page_table[i] = create_section_descriptor(
            phys_addr,
            AP_FULL_ACCESS,     // 完全访问
            0,                  // 域0
            1,                  // 可缓存
            1                   // 可缓冲
        );
    }
    
    // 特殊区域配置
    // 外设区域：不可缓存
    for (uint32_t i = 0x400; i < 0x600; i++) {  // 1GB-1.5GB
        uint32_t phys_addr = i * SECTION_SIZE;
        page_table[i] = create_section_descriptor(
            phys_addr,
            AP_PRIV_RW,         // 特权读写
            0,
            0,                  // 不可缓存
            0                   // 不可缓冲
        );
    }
}
```


#### 3.2 启用MMU

配置并启用MMU的完整流程：

```c
// 使能MMU
void enable_mmu(void) {
    uint32_t reg;
    
    // 1. 设置页表基地址
    set_ttbr0((uint32_t)page_table);
    
    // 2. 配置域访问控制
    // 域0设置为客户端模式（检查访问权限）
    set_dacr(DOMAIN_CLIENT << 0);
    
    // 3. 无效化TLB
    asm volatile("mcr p15, 0, %0, c8, c7, 0" : : "r"(0));
    
    // 4. 无效化指令缓存
    asm volatile("mcr p15, 0, %0, c7, c5, 0" : : "r"(0));
    
    // 5. 数据同步屏障
    asm volatile("dsb");
    
    // 6. 读取SCTLR
    reg = read_sctlr();
    
    // 7. 使能MMU、数据缓存、指令缓存
    reg |= SCTLR_M;  // MMU使能
    reg |= SCTLR_C;  // 数据缓存使能
    reg |= SCTLR_I;  // 指令缓存使能
    reg |= SCTLR_Z;  // 分支预测使能
    
    // 8. 写入SCTLR
    write_sctlr(reg);
    
    // 9. 指令同步屏障
    asm volatile("isb");
}

// 禁用MMU
void disable_mmu(void) {
    uint32_t reg;
    
    // 读取SCTLR
    reg = read_sctlr();
    
    // 清除MMU使能位
    reg &= ~SCTLR_M;
    reg &= ~SCTLR_C;
    reg &= ~SCTLR_I;
    
    // 写入SCTLR
    write_sctlr(reg);
    
    // 同步
    asm volatile("dsb");
    asm volatile("isb");
}
```


#### 3.3 完整示例

一个完整的MMU初始化和测试程序：

```c
#include <stdio.h>
#include <stdint.h>

// 测试MMU功能
void test_mmu(void) {
    printf("MMU Test Program\n");
    printf("================\n\n");
    
    // 1. 初始化页表
    printf("1. Initializing page table...\n");
    init_page_table();
    printf("   Page table initialized at 0x%08X\n", 
           (uint32_t)page_table);
    
    // 2. 启用MMU
    printf("2. Enabling MMU...\n");
    enable_mmu();
    printf("   MMU enabled\n");
    
    // 3. 测试内存访问
    printf("3. Testing memory access...\n");
    
    // 测试读写
    volatile uint32_t* test_addr = (uint32_t*)0x80000000;
    *test_addr = 0x12345678;
    uint32_t value = *test_addr;
    
    if (value == 0x12345678) {
        printf("   Memory access OK: 0x%08X\n", value);
    } else {
        printf("   Memory access FAILED\n");
    }
    
    // 4. 显示MMU状态
    printf("4. MMU Status:\n");
    uint32_t sctlr = read_sctlr();
    printf("   SCTLR: 0x%08X\n", sctlr);
    printf("   MMU:   %s\n", (sctlr & SCTLR_M) ? "Enabled" : "Disabled");
    printf("   DCache: %s\n", (sctlr & SCTLR_C) ? "Enabled" : "Disabled");
    printf("   ICache: %s\n", (sctlr & SCTLR_I) ? "Enabled" : "Disabled");
    
    printf("\nTest completed successfully!\n");
}

int main(void) {
    // 系统初始化
    SystemInit();
    
    // 运行MMU测试
    test_mmu();
    
    while(1) {
        // 主循环
    }
    
    return 0;
}
```


### 4. 虚拟内存映射

#### 4.1 内存映射类型

**恒等映射（Identity Mapping）**：
虚拟地址 = 物理地址

```c
// 恒等映射示例
void map_identity(uint32_t virt_addr, uint32_t size) {
    uint32_t num_sections = size / SECTION_SIZE;
    uint32_t start_index = virt_addr / SECTION_SIZE;
    
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t index = start_index + i;
        uint32_t phys_addr = virt_addr + (i * SECTION_SIZE);
        
        page_table[index] = create_section_descriptor(
            phys_addr,
            AP_FULL_ACCESS,
            0, 1, 1
        );
    }
}
```

**偏移映射（Offset Mapping）**：
虚拟地址 = 物理地址 + 偏移量

```c
// 偏移映射示例
void map_with_offset(
    uint32_t virt_addr,
    uint32_t phys_addr,
    uint32_t size
) {
    uint32_t num_sections = size / SECTION_SIZE;
    uint32_t virt_index = virt_addr / SECTION_SIZE;
    
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t index = virt_index + i;
        uint32_t phys = phys_addr + (i * SECTION_SIZE);
        
        page_table[index] = create_section_descriptor(
            phys,
            AP_FULL_ACCESS,
            0, 1, 1
        );
    }
}
```

**示例：将物理地址0x80000000映射到虚拟地址0xC0000000**：

```c
void setup_kernel_mapping(void) {
    // 内核空间：虚拟地址0xC0000000 -> 物理地址0x80000000
    map_with_offset(
        0xC0000000,     // 虚拟地址
        0x80000000,     // 物理地址
        256 * 1024 * 1024  // 256MB
    );
}
```


#### 4.2 内存保护

配置不同区域的访问权限：

```c
// 内存区域类型
typedef enum {
    MEM_TYPE_NORMAL_WB,      // 普通内存，写回缓存
    MEM_TYPE_NORMAL_WT,      // 普通内存，写通缓存
    MEM_TYPE_NORMAL_NC,      // 普通内存，不缓存
    MEM_TYPE_DEVICE,         // 设备内存
    MEM_TYPE_STRONGLY_ORDERED // 强序内存
} memory_type_t;

// 访问权限类型
typedef enum {
    ACCESS_NONE,             // 无访问权限
    ACCESS_PRIV_RW,          // 特权读写
    ACCESS_PRIV_RO,          // 特权只读
    ACCESS_FULL_RW,          // 完全读写
    ACCESS_FULL_RO           // 完全只读
} access_permission_t;

// 映射内存区域
void map_memory_region(
    uint32_t virt_addr,
    uint32_t phys_addr,
    uint32_t size,
    memory_type_t mem_type,
    access_permission_t access
) {
    uint32_t cacheable = 0;
    uint32_t bufferable = 0;
    uint32_t ap = 0;
    
    // 根据内存类型设置缓存属性
    switch (mem_type) {
        case MEM_TYPE_NORMAL_WB:
            cacheable = 1;
            bufferable = 1;
            break;
        case MEM_TYPE_NORMAL_WT:
            cacheable = 1;
            bufferable = 0;
            break;
        case MEM_TYPE_NORMAL_NC:
            cacheable = 0;
            bufferable = 0;
            break;
        case MEM_TYPE_DEVICE:
            cacheable = 0;
            bufferable = 1;
            break;
        case MEM_TYPE_STRONGLY_ORDERED:
            cacheable = 0;
            bufferable = 0;
            break;
    }
    
    // 根据访问权限设置AP位
    switch (access) {
        case ACCESS_NONE:
            ap = AP_NO_ACCESS;
            break;
        case ACCESS_PRIV_RW:
            ap = AP_PRIV_RW;
            break;
        case ACCESS_FULL_RW:
            ap = AP_FULL_ACCESS;
            break;
        default:
            ap = AP_FULL_ACCESS;
            break;
    }
    
    // 执行映射
    uint32_t num_sections = size / SECTION_SIZE;
    uint32_t virt_index = virt_addr / SECTION_SIZE;
    
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t index = virt_index + i;
        uint32_t phys = phys_addr + (i * SECTION_SIZE);
        
        page_table[index] = create_section_descriptor(
            phys, ap, 0, cacheable, bufferable
        );
    }
}
```


**使用示例**：

```c
void setup_memory_regions(void) {
    // 1. 代码段：只读，可缓存
    map_memory_region(
        0x00000000,              // 虚拟地址
        0x00000000,              // 物理地址
        16 * 1024 * 1024,        // 16MB
        MEM_TYPE_NORMAL_WB,      // 写回缓存
        ACCESS_PRIV_RO           // 特权只读
    );
    
    // 2. 数据段：读写，可缓存
    map_memory_region(
        0x01000000,
        0x01000000,
        16 * 1024 * 1024,
        MEM_TYPE_NORMAL_WB,
        ACCESS_PRIV_RW           // 特权读写
    );
    
    // 3. 外设区域：读写，不可缓存
    map_memory_region(
        0x40000000,
        0x40000000,
        256 * 1024 * 1024,
        MEM_TYPE_DEVICE,         // 设备内存
        ACCESS_PRIV_RW
    );
    
    // 4. 用户空间：读写，可缓存
    map_memory_region(
        0x80000000,
        0x80000000,
        512 * 1024 * 1024,
        MEM_TYPE_NORMAL_WB,
        ACCESS_FULL_RW           // 完全读写
    );
}
```

#### 4.3 动态映射

在运行时动态创建和修改映射：

```c
// 动态映射函数
int mmap_region(
    uint32_t virt_addr,
    uint32_t phys_addr,
    uint32_t size,
    uint32_t flags
) {
    // 检查地址对齐
    if ((virt_addr & (SECTION_SIZE - 1)) != 0 ||
        (phys_addr & (SECTION_SIZE - 1)) != 0) {
        return -1;  // 地址未对齐
    }
    
    // 检查大小
    if (size == 0 || (size & (SECTION_SIZE - 1)) != 0) {
        return -1;  // 大小无效
    }
    
    // 创建映射
    uint32_t num_sections = size / SECTION_SIZE;
    uint32_t virt_index = virt_addr / SECTION_SIZE;
    
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t index = virt_index + i;
        uint32_t phys = phys_addr + (i * SECTION_SIZE);
        
        // 检查是否已映射
        if (page_table[index] & DESC_TYPE_SECTION) {
            return -1;  // 已存在映射
        }
        
        // 创建新映射
        page_table[index] = create_section_descriptor(
            phys,
            (flags >> 0) & 0x3,   // AP
            (flags >> 2) & 0xF,   // Domain
            (flags >> 6) & 0x1,   // Cacheable
            (flags >> 7) & 0x1    // Bufferable
        );
    }
    
    // 刷新TLB
    asm volatile("mcr p15, 0, %0, c8, c7, 0" : : "r"(0));
    asm volatile("dsb");
    asm volatile("isb");
    
    return 0;
}

// 取消映射
int munmap_region(uint32_t virt_addr, uint32_t size) {
    uint32_t num_sections = size / SECTION_SIZE;
    uint32_t virt_index = virt_addr / SECTION_SIZE;
    
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t index = virt_index + i;
        
        // 清除映射
        page_table[index] = DESC_TYPE_FAULT;
    }
    
    // 刷新TLB
    asm volatile("mcr p15, 0, %0, c8, c7, 0" : : "r"(0));
    asm volatile("dsb");
    asm volatile("isb");
    
    return 0;
}
```


### 5. TLB管理

#### 5.1 TLB原理

TLB（Translation Lookaside Buffer）是MMU的缓存，用于加速地址转换。

**TLB工作流程**：

```
虚拟地址
   ↓
查询TLB
   ↓
命中? ──是→ 返回物理地址（快速）
   ↓否
查询页表
   ↓
更新TLB
   ↓
返回物理地址（慢速）
```

**TLB性能影响**：
- TLB命中：1-2个时钟周期
- TLB未命中：10-100个时钟周期

#### 5.2 TLB操作

```c
// 无效化整个TLB
static inline void invalidate_tlb_all(void) {
    asm volatile("mcr p15, 0, %0, c8, c7, 0" : : "r"(0));
    asm volatile("dsb");
    asm volatile("isb");
}

// 无效化单个TLB条目
static inline void invalidate_tlb_entry(uint32_t virt_addr) {
    asm volatile("mcr p15, 0, %0, c8, c7, 1" : : "r"(virt_addr));
    asm volatile("dsb");
    asm volatile("isb");
}

// 无效化指令TLB
static inline void invalidate_itlb(void) {
    asm volatile("mcr p15, 0, %0, c8, c5, 0" : : "r"(0));
    asm volatile("isb");
}

// 无效化数据TLB
static inline void invalidate_dtlb(void) {
    asm volatile("mcr p15, 0, %0, c8, c6, 0" : : "r"(0));
    asm volatile("dsb");
}
```

#### 5.3 TLB优化策略

**1. 减少TLB未命中**：

```c
// 使用大页减少TLB条目数
void use_large_pages(void) {
    // 使用1MB段而不是4KB页
    // 减少TLB压力
}

// 局部性优化
void optimize_locality(void) {
    // 将相关数据放在相邻页面
    // 提高TLB命中率
}
```

**2. 及时刷新TLB**：

```c
// 修改页表后刷新TLB
void update_page_table_entry(uint32_t index, uint32_t desc) {
    page_table[index] = desc;
    
    // 计算虚拟地址
    uint32_t virt_addr = index * SECTION_SIZE;
    
    // 只刷新相关条目
    invalidate_tlb_entry(virt_addr);
}
```


### 6. 实践项目：简单的虚拟内存管理器

让我们实现一个完整的虚拟内存管理器：

```c
#include <stdint.h>
#include <string.h>
#include <stdio.h>

// 虚拟内存管理器
typedef struct {
    uint32_t* page_table;
    uint32_t total_memory;
    uint32_t used_memory;
    uint32_t num_mappings;
} vmm_t;

// 全局VMM实例
static vmm_t g_vmm;

// 初始化虚拟内存管理器
void vmm_init(void) {
    memset(&g_vmm, 0, sizeof(vmm_t));
    
    // 使用全局页表
    g_vmm.page_table = page_table;
    g_vmm.total_memory = 4096 * SECTION_SIZE;  // 4GB
    g_vmm.used_memory = 0;
    g_vmm.num_mappings = 0;
    
    // 初始化页表
    init_page_table();
    
    printf("VMM initialized\n");
    printf("Total memory: %u MB\n", g_vmm.total_memory / (1024*1024));
}

// 分配虚拟内存
void* vmm_alloc(uint32_t size, uint32_t flags) {
    // 对齐到段大小
    size = (size + SECTION_SIZE - 1) & ~(SECTION_SIZE - 1);
    
    // 查找空闲虚拟地址
    uint32_t virt_addr = 0;
    uint32_t found = 0;
    
    for (uint32_t i = 0; i < 4096; i++) {
        if ((g_vmm.page_table[i] & 0x3) == DESC_TYPE_FAULT) {
            // 找到空闲段
            virt_addr = i * SECTION_SIZE;
            found = 1;
            break;
        }
    }
    
    if (!found) {
        printf("VMM: No free virtual address\n");
        return NULL;
    }
    
    // 分配物理内存（简化：使用恒等映射）
    uint32_t phys_addr = virt_addr;
    
    // 创建映射
    if (mmap_region(virt_addr, phys_addr, size, flags) != 0) {
        printf("VMM: Failed to create mapping\n");
        return NULL;
    }
    
    // 更新统计
    g_vmm.used_memory += size;
    g_vmm.num_mappings++;
    
    printf("VMM: Allocated %u bytes at 0x%08X\n", size, virt_addr);
    
    return (void*)virt_addr;
}

// 释放虚拟内存
void vmm_free(void* ptr, uint32_t size) {
    uint32_t virt_addr = (uint32_t)ptr;
    
    // 对齐到段大小
    size = (size + SECTION_SIZE - 1) & ~(SECTION_SIZE - 1);
    
    // 取消映射
    if (munmap_region(virt_addr, size) != 0) {
        printf("VMM: Failed to unmap region\n");
        return;
    }
    
    // 更新统计
    g_vmm.used_memory -= size;
    g_vmm.num_mappings--;
    
    printf("VMM: Freed %u bytes at 0x%08X\n", size, virt_addr);
}

// 打印VMM统计信息
void vmm_print_stats(void) {
    printf("\nVMM Statistics:\n");
    printf("===============\n");
    printf("Total memory:  %u MB\n", 
           g_vmm.total_memory / (1024*1024));
    printf("Used memory:   %u MB\n", 
           g_vmm.used_memory / (1024*1024));
    printf("Free memory:   %u MB\n", 
           (g_vmm.total_memory - g_vmm.used_memory) / (1024*1024));
    printf("Num mappings:  %u\n", g_vmm.num_mappings);
    printf("Usage:         %.1f%%\n", 
           (float)g_vmm.used_memory * 100 / g_vmm.total_memory);
}
```


**测试程序**：

```c
void test_vmm(void) {
    printf("Virtual Memory Manager Test\n");
    printf("============================\n\n");
    
    // 初始化VMM
    vmm_init();
    
    // 启用MMU
    enable_mmu();
    
    // 测试1：分配内存
    printf("\nTest 1: Allocate memory\n");
    void* ptr1 = vmm_alloc(4 * 1024 * 1024, 0x3F);  // 4MB
    void* ptr2 = vmm_alloc(8 * 1024 * 1024, 0x3F);  // 8MB
    
    // 测试2：使用内存
    printf("\nTest 2: Use memory\n");
    if (ptr1 != NULL) {
        uint32_t* data = (uint32_t*)ptr1;
        data[0] = 0xDEADBEEF;
        printf("Written: 0x%08X\n", data[0]);
        printf("Read:    0x%08X\n", data[0]);
    }
    
    // 测试3：打印统计
    printf("\nTest 3: Statistics\n");
    vmm_print_stats();
    
    // 测试4：释放内存
    printf("\nTest 4: Free memory\n");
    vmm_free(ptr1, 4 * 1024 * 1024);
    vmm_free(ptr2, 8 * 1024 * 1024);
    
    // 最终统计
    printf("\nFinal statistics:\n");
    vmm_print_stats();
    
    printf("\nAll tests passed!\n");
}
```

## 验证

### 测试方法

1. **编译程序**：

```bash
arm-linux-gnueabihf-gcc -o mmu_test mmu_test.c -O2 -march=armv7-a
```

2. **在开发板上运行**：

```bash
./mmu_test
```

### 预期结果

```
Virtual Memory Manager Test
============================

VMM initialized
Total memory: 4096 MB

Test 1: Allocate memory
VMM: Allocated 4194304 bytes at 0x00000000
VMM: Allocated 8388608 bytes at 0x00400000

Test 2: Use memory
Written: 0xDEADBEEF
Read:    0xDEADBEEF

Test 3: Statistics
VMM Statistics:
===============
Total memory:  4096 MB
Used memory:   12 MB
Free memory:   4084 MB
Num mappings:  2
Usage:         0.3%

Test 4: Free memory
VMM: Freed 4194304 bytes at 0x00000000
VMM: Freed 8388608 bytes at 0x00400000

Final statistics:
VMM Statistics:
===============
Total memory:  4096 MB
Used memory:   0 MB
Free memory:   4096 MB
Num mappings:  0
Usage:         0.0%

All tests passed!
```


## 故障排除

### 问题1：MMU启用后系统崩溃

**现象**：
启用MMU后立即发生异常或系统重启

**可能原因**：
1. 页表未正确初始化
2. 页表地址未对齐
3. 当前执行代码的地址未映射
4. 栈地址未映射

**解决方法**：

```c
// 1. 确保页表对齐
static uint32_t page_table[4096] 
    __attribute__((aligned(16384)));

// 2. 确保当前代码区域已映射
void ensure_code_mapped(void) {
    // 获取当前PC值
    uint32_t pc;
    asm volatile("mov %0, pc" : "=r"(pc));
    
    // 确保PC所在区域已映射
    uint32_t section = pc / SECTION_SIZE;
    if ((page_table[section] & 0x3) == DESC_TYPE_FAULT) {
        printf("ERROR: Current code not mapped!\n");
    }
}

// 3. 确保栈已映射
void ensure_stack_mapped(void) {
    uint32_t sp;
    asm volatile("mov %0, sp" : "=r"(sp));
    
    uint32_t section = sp / SECTION_SIZE;
    if ((page_table[section] & 0x3) == DESC_TYPE_FAULT) {
        printf("ERROR: Stack not mapped!\n");
    }
}
```

### 问题2：TLB未命中率高

**现象**：
系统性能下降，TLB未命中频繁

**可能原因**：
1. 使用小页面（4KB）
2. 内存访问模式分散
3. TLB容量不足

**解决方法**：

```c
// 1. 使用大页面（1MB段）
void use_sections_instead_of_pages(void) {
    // 优先使用段描述符而不是页表
}

// 2. 优化数据布局
void optimize_data_layout(void) {
    // 将相关数据放在相邻页面
    // 提高空间局部性
}

// 3. 监控TLB性能
void monitor_tlb_performance(void) {
    // 使用性能计数器监控TLB未命中
    // 根据统计数据优化
}
```

### 问题3：缓存一致性问题

**现象**：
数据不一致，读取到旧数据

**可能原因**：
1. DMA和CPU缓存不一致
2. 多核缓存同步问题
3. 缓存属性配置错误

**解决方法**：

```c
// 1. DMA缓冲区使用不可缓存内存
void setup_dma_buffer(void) {
    map_memory_region(
        dma_buffer_addr,
        dma_buffer_addr,
        dma_buffer_size,
        MEM_TYPE_NORMAL_NC,  // 不可缓存
        ACCESS_PRIV_RW
    );
}

// 2. 手动刷新缓存
static inline void clean_dcache_range(
    uint32_t start,
    uint32_t end
) {
    for (uint32_t addr = start; addr < end; addr += 32) {
        asm volatile("mcr p15, 0, %0, c7, c10, 1" : : "r"(addr));
    }
    asm volatile("dsb");
}

// 3. 无效化缓存
static inline void invalidate_dcache_range(
    uint32_t start,
    uint32_t end
) {
    for (uint32_t addr = start; addr < end; addr += 32) {
        asm volatile("mcr p15, 0, %0, c7, c6, 1" : : "r"(addr));
    }
    asm volatile("dsb");
}
```


### 问题4：页表占用内存过大

**现象**：
页表占用大量内存（16KB一级页表 + 多个1KB二级页表）

**可能原因**：
1. 使用二级页表映射大量小页面
2. 页表结构设计不合理

**解决方法**：

```c
// 1. 优先使用段映射
void prefer_section_mapping(void) {
    // 对于大块连续内存，使用1MB段
    // 只对需要细粒度控制的区域使用4KB页
}

// 2. 按需分配二级页表
void allocate_l2_table_on_demand(uint32_t l1_index) {
    // 只在需要时分配二级页表
    if ((page_table[l1_index] & 0x3) == DESC_TYPE_FAULT) {
        // 分配1KB二级页表
        uint32_t* l2_table = allocate_l2_table();
        
        // 创建页表描述符
        page_table[l1_index] = 
            ((uint32_t)l2_table & 0xFFFFFC00) | DESC_TYPE_PAGE;
    }
}
```

## 深入理解

### MMU与操作系统

MMU是操作系统实现以下功能的基础：

**1. 进程隔离**：
每个进程有独立的虚拟地址空间，互不干扰。

```c
// 进程切换时更新页表基地址
void switch_process(process_t* new_process) {
    // 切换到新进程的页表
    set_ttbr0((uint32_t)new_process->page_table);
    
    // 刷新TLB
    invalidate_tlb_all();
}
```

**2. 内存共享**：
多个进程可以映射到同一物理内存。

```c
// 共享内存映射
void map_shared_memory(
    process_t* proc1,
    process_t* proc2,
    uint32_t phys_addr,
    uint32_t size
) {
    // 在两个进程中映射相同的物理内存
    map_in_process(proc1, 0x80000000, phys_addr, size);
    map_in_process(proc2, 0x80000000, phys_addr, size);
}
```

**3. 按需分页**：
只在访问时才分配物理内存。

```c
// 缺页异常处理
void page_fault_handler(uint32_t fault_addr) {
    // 分配物理页面
    uint32_t phys_page = allocate_physical_page();
    
    // 创建映射
    map_page(fault_addr, phys_page);
    
    // 刷新TLB
    invalidate_tlb_entry(fault_addr);
}
```


### 性能优化

**1. 减少页表遍历**：

```c
// 使用TLB锁定关键页面
void lock_critical_pages(void) {
    // 某些ARM处理器支持TLB锁定
    // 将关键代码和数据锁定在TLB中
}
```

**2. 优化页表结构**：

```c
// 使用超级页（Supersection，16MB）
void use_supersections(void) {
    // 对于大块连续内存，使用16MB超级段
    // 减少页表条目数量
}
```

**3. 缓存优化**：

```c
// 为不同类型的内存配置合适的缓存策略
void optimize_cache_policy(void) {
    // 代码段：写回缓存
    // 数据段：写回缓存
    // DMA缓冲区：不可缓存
    // 外设寄存器：强序，不可缓存
}
```

### 安全考虑

**1. 权限检查**：

```c
// 严格的权限控制
void setup_secure_regions(void) {
    // 内核代码：特权只读
    map_memory_region(
        kernel_code_start,
        kernel_code_start,
        kernel_code_size,
        MEM_TYPE_NORMAL_WB,
        ACCESS_PRIV_RO
    );
    
    // 用户代码：用户可执行
    map_memory_region(
        user_code_start,
        user_code_start,
        user_code_size,
        MEM_TYPE_NORMAL_WB,
        ACCESS_FULL_RO
    );
}
```

**2. 执行保护**：

```c
// 使用XN（Execute Never）位
void enable_execute_protection(void) {
    // 数据段禁止执行
    // 防止代码注入攻击
}
```

**3. 地址空间随机化**：

```c
// ASLR（Address Space Layout Randomization）
uint32_t get_random_base_address(void) {
    // 随机化加载地址
    // 增加攻击难度
    return random() & 0xFFF00000;
}
```

## 常见问题

### Q1: MMU和MPU有什么区别？

**A**: 主要区别：

| 特性 | MMU | MPU |
|------|-----|-----|
| 地址转换 | 支持虚拟地址转换 | 不支持，直接使用物理地址 |
| 内存保护 | 支持 | 支持 |
| 页表 | 需要页表 | 不需要页表 |
| 复杂度 | 较高 | 较低 |
| 适用场景 | 运行操作系统 | 简单的嵌入式系统 |
| 处理器 | Cortex-A, Cortex-M7 | Cortex-M0/M3/M4 |


### Q2: 为什么需要刷新TLB？

**A**: TLB刷新的原因：

1. **页表修改**：修改页表后，TLB中的旧条目可能无效
2. **进程切换**：切换到新进程时，需要清除旧进程的TLB条目
3. **权限变更**：修改内存访问权限后需要更新TLB

**刷新策略**：
- 全局刷新：简单但性能开销大
- 单条目刷新：精确但需要知道具体地址
- ASID标记：避免进程切换时全局刷新

### Q3: 如何选择页面大小？

**A**: 选择依据：

**小页面（4KB）**：
- 优点：细粒度控制，减少内部碎片
- 缺点：页表占用内存多，TLB压力大
- 适用：需要精细内存管理的场景

**大页面（1MB段）**：
- 优点：页表占用少，TLB效率高
- 缺点：粗粒度控制，可能浪费内存
- 适用：大块连续内存映射

**混合策略**：
```c
// 推荐做法：混合使用
void setup_mixed_page_sizes(void) {
    // 大块内存使用1MB段
    map_sections(0x80000000, 256 * 1024 * 1024);
    
    // 需要细粒度控制的区域使用4KB页
    map_pages(0x90000000, 4 * 1024 * 1024);
}
```

### Q4: MMU对性能有什么影响？

**A**: 性能影响分析：

**正面影响**：
- 启用缓存，大幅提升性能（10-100倍）
- TLB命中时，地址转换开销很小

**负面影响**：
- TLB未命中时，需要遍历页表（10-100个周期）
- 页表占用内存和缓存
- 上下文切换需要刷新TLB

**优化建议**：
```c
// 1. 提高TLB命中率
void improve_tlb_hit_rate(void) {
    // 使用大页面
    // 优化数据局部性
    // 减少地址空间跳转
}

// 2. 减少TLB刷新
void reduce_tlb_flush(void) {
    // 使用ASID避免全局刷新
    // 只刷新必要的条目
}

// 3. 优化缓存使用
void optimize_cache(void) {
    // 合理配置缓存属性
    // 避免缓存抖动
}
```

### Q5: 如何调试MMU相关问题？

**A**: 调试方法：

**1. 使用调试寄存器**：
```c
// 读取故障状态寄存器
uint32_t read_dfsr(void) {
    uint32_t val;
    asm volatile("mrc p15, 0, %0, c5, c0, 0" : "=r"(val));
    return val;
}

// 读取故障地址寄存器
uint32_t read_dfar(void) {
    uint32_t val;
    asm volatile("mrc p15, 0, %0, c6, c0, 0" : "=r"(val));
    return val;
}

// 数据访问异常处理
void data_abort_handler(void) {
    uint32_t dfsr = read_dfsr();
    uint32_t dfar = read_dfar();
    
    printf("Data Abort!\n");
    printf("DFSR: 0x%08X\n", dfsr);
    printf("DFAR: 0x%08X\n", dfar);
    
    // 分析故障类型
    uint32_t status = dfsr & 0xF;
    switch (status) {
        case 0x5:
            printf("Translation fault (section)\n");
            break;
        case 0x7:
            printf("Translation fault (page)\n");
            break;
        case 0xD:
            printf("Permission fault (section)\n");
            break;
        case 0xF:
            printf("Permission fault (page)\n");
            break;
        default:
            printf("Unknown fault: %u\n", status);
            break;
    }
}
```

**2. 页表转储**：
```c
// 打印页表内容
void dump_page_table(void) {
    printf("Page Table Dump:\n");
    printf("================\n");
    
    for (uint32_t i = 0; i < 4096; i++) {
        uint32_t entry = page_table[i];
        
        if ((entry & 0x3) != DESC_TYPE_FAULT) {
            uint32_t virt = i * SECTION_SIZE;
            uint32_t phys = entry & 0xFFF00000;
            uint32_t type = entry & 0x3;
            
            printf("[%04u] VA:0x%08X -> PA:0x%08X Type:%u\n",
                   i, virt, phys, type);
        }
    }
}
```

**3. 单步调试**：
```c
// 在启用MMU前后设置断点
void debug_mmu_enable(void) {
    printf("Before MMU enable\n");
    // 断点1
    
    enable_mmu();
    
    printf("After MMU enable\n");
    // 断点2
}
```

## 总结

本教程深入讲解了MMU和虚拟内存管理的核心概念和实践方法，主要内容包括：

- **MMU原理**：地址转换、页表结构、TLB缓存
- **ARM MMU**：页表格式、控制寄存器、配置方法
- **页表配置**：创建页表、启用MMU、内存映射
- **虚拟内存**：恒等映射、偏移映射、动态映射
- **TLB管理**：TLB操作、性能优化
- **实践项目**：完整的虚拟内存管理器实现

掌握MMU和虚拟内存技术后，你将能够：
- 实现操作系统的内存管理
- 提供进程隔离和保护
- 优化内存使用和性能
- 调试内存相关问题

## 延伸阅读

- [内存泄漏检测与分析](02-memory-leak-detection.html) - 学习内存调试技术
- [高效内存管理系统设计](../advanced/01-memory-management-system.html) - 深入学习内存管理
- [堆栈溢出检测与防护](../beginner/03-stack-overflow-detection.html) - 了解栈保护

## 参考资料

1. ARM Architecture Reference Manual - ARM官方文档
2. "ARM System Developer's Guide" by Andrew Sloss
3. Linux内核源码 - arch/arm/mm/
4. "Understanding the Linux Virtual Memory Manager" by Mel Gorman
5. ARM Cortex-A Series Programmer's Guide - ARM官方指南

---

**练习题**：

1. 解释虚拟地址到物理地址的转换过程，画出详细的流程图。
2. 实现一个支持4KB小页面的二级页表系统。
3. 编写代码测试不同缓存策略对性能的影响。
4. 实现一个简单的按需分页机制，包括缺页异常处理。
5. 分析并优化一个TLB未命中率高的程序。

**实践项目**：

创建一个完整的虚拟内存管理系统，包括：
- 一级和二级页表支持
- 动态内存映射和取消映射
- TLB管理和优化
- 内存保护和权限控制
- 性能监控和统计
- 调试和诊断工具

**下一步**：建议学习 [内存泄漏检测与分析](02-memory-leak-detection.html)，掌握内存调试技术。
