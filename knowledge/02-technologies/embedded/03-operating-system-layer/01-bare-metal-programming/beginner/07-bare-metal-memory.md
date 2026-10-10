---
title: "裸机程序的内存管理：高效利用有限资源"
description: "深入学习裸机环境下的内存管理技术。通过本文，你将掌握静态内存分配、内存池设计、堆栈管理、内存优化技巧，以及如何避免内存碎片，确保嵌入式系统的稳定运行。"
slug: "bare-metal-memory-management"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 内存管理
  - 内存池
  - 静态分配
  - 堆栈管理
  - 内存优化
prerequisites:
  - "bare-metal-programming-basics"
  - "super-loop-programming"
related_contents: []

# 学习信息
estimated_time: 45
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
  - 裸机内存管理
  - 静态内存分配
  - 内存池
  - 堆栈管理
  - 内存碎片
  - 嵌入式内存优化
cover_image: ""
---

# 裸机程序的内存管理：高效利用有限资源

## 概述

在裸机嵌入式系统中，内存是最宝贵的资源之一。与桌面系统不同，嵌入式系统通常只有几KB到几百KB的RAM，没有操作系统提供的动态内存管理支持。因此，开发者必须精心设计内存使用策略，确保程序稳定可靠地运行。

通过本文学习，你将能够：

- 理解裸机环境下的内存布局和特点
- 掌握静态内存分配的方法和最佳实践
- 设计和实现高效的内存池管理系统
- 正确管理堆栈空间，避免栈溢出
- 应用内存优化技巧，减少内存占用
- 识别和避免内存碎片问题

## 背景知识

### 嵌入式系统的内存特点

**内存资源限制**：
- **RAM容量小**：从几KB（如STM32F0）到几百KB（如STM32F4）
- **无虚拟内存**：物理地址直接访问，无内存保护
- **无操作系统支持**：没有malloc/free等标准库函数
- **实时性要求**：内存分配必须快速且确定性

**典型MCU内存配置**：
```
STM32F103C8T6:
- Flash: 64KB (程序存储)
- SRAM:  20KB (数据存储)

STM32F407VG:
- Flash: 1MB
- SRAM:  192KB (128KB + 64KB)

ESP32:
- Flash: 4MB (外部)
- SRAM:  520KB (内部)
```

### 内存布局

典型的ARM Cortex-M内存布局：

```
高地址
┌─────────────────┐
│   栈区 (Stack)   │ ← 向下增长
│       ↓         │
├─────────────────┤
│   (未使用空间)   │
├─────────────────┤
│       ↑         │
│   堆区 (Heap)    │ ← 向上增长
├─────────────────┤
│   BSS段         │ ← 未初始化全局变量
├─────────────────┤
│   Data段        │ ← 已初始化全局变量
├─────────────────┤
│   代码段 (Text)  │ ← 程序代码
└─────────────────┘
低地址
```

**各区域说明**：
- **代码段（Text）**：存储程序指令，位于Flash或RAM
- **数据段（Data）**：已初始化的全局变量和静态变量
- **BSS段**：未初始化的全局变量和静态变量（初始化为0）
- **堆区（Heap）**：动态分配的内存（如果使用）
- **栈区（Stack）**：函数调用、局部变量、中断上下文


### 为什么裸机环境需要特殊的内存管理？

**问题场景**：
```c
// 危险的做法：在裸机环境使用malloc
void ProcessData(void) {
    uint8_t *buffer = (uint8_t*)malloc(1024);  // 可能失败！
    if(buffer == NULL) {
        // 内存分配失败，怎么办？
        // 裸机环境下没有swap，无法恢复
        return;
    }
    
    // 使用buffer...
    
    free(buffer);  // 可能产生内存碎片
}
```

**裸机环境的挑战**：
1. **无法处理分配失败**：没有虚拟内存，分配失败就是失败
2. **内存碎片**：频繁分配释放导致碎片，最终无法分配
3. **不确定性**：malloc/free时间不确定，影响实时性
4. **调试困难**：内存泄漏和越界难以发现

**解决方案**：
- 优先使用静态分配
- 使用内存池管理固定大小的内存块
- 避免动态分配，或在初始化时一次性分配
- 精心设计数据结构，减少内存占用

## 核心内容

### 静态内存分配

静态内存分配是裸机编程中最安全、最可靠的方式。

#### 全局变量和静态变量

```c
#include <stdint.h>

// 全局变量（Data段，已初始化）
uint8_t uart_rx_buffer[256] = {0};
uint32_t system_tick_count = 0;

// 全局变量（BSS段，未初始化，自动清零）
uint8_t sensor_data[100];
uint16_t adc_samples[512];

// 静态变量（函数内部，保持状态）
void UpdateCounter(void) {
    static uint32_t call_count = 0;  // 只初始化一次
    call_count++;
    printf("Called %lu times\n", call_count);
}

// 常量数据（存储在Flash中，不占用RAM）
const uint8_t lookup_table[256] = {
    0x00, 0x01, 0x02, 0x03, /* ... */
};

const char* error_messages[] = {
    "No Error",
    "Timeout",
    "Invalid Parameter",
    "Hardware Failure"
};
```

**优点**：
- 编译时确定大小和位置
- 无运行时开销
- 无分配失败风险
- 访问速度快

**缺点**：
- 内存使用固定，无法动态调整
- 可能浪费内存（如果预留过多）
- 大数组会增加程序体积

**最佳实践**：
```c
// ✓ 好的做法：合理的缓冲区大小
#define UART_BUFFER_SIZE 128
uint8_t uart_buffer[UART_BUFFER_SIZE];

// ✗ 不好的做法：过大的缓冲区
uint8_t huge_buffer[10240];  // 10KB，可能超过RAM容量

// ✓ 好的做法：使用const减少RAM占用
const uint16_t sine_table[360] = { /* ... */ };  // 存储在Flash

// ✗ 不好的做法：大数组占用RAM
uint16_t sine_table[360] = { /* ... */ };  // 占用720字节RAM
```


#### 局部变量和栈空间

```c
// 局部变量（栈上分配）
void ProcessSensorData(void) {
    uint8_t temp_buffer[64];     // 栈上分配64字节
    uint16_t sensor_value;       // 栈上分配2字节
    
    // 使用局部变量...
    ReadSensor(temp_buffer, sizeof(temp_buffer));
    sensor_value = CalculateAverage(temp_buffer, 64);
    
    // 函数返回时，栈空间自动释放
}

// 危险：过大的局部数组
void DangerousFunction(void) {
    uint8_t large_buffer[2048];  // 可能导致栈溢出！
    // ...
}

// 更好的做法：使用静态变量或全局变量
static uint8_t large_buffer[2048];  // 不占用栈空间

void SaferFunction(void) {
    // 使用静态变量
    memset(large_buffer, 0, sizeof(large_buffer));
    // ...
}
```

**栈空间管理要点**：
- 栈大小在启动代码中定义（通常1-4KB）
- 局部变量、函数参数、返回地址都占用栈
- 中断嵌套会增加栈使用
- 栈溢出是裸机程序最常见的崩溃原因

**检查栈使用情况**：
```c
// 启动代码中定义栈大小
__attribute__((section(".stack")))
uint8_t stack_memory[2048];  // 2KB栈空间

// 栈使用情况检查（填充模式）
void Stack_Init(void) {
    // 用特定模式填充栈空间
    memset(stack_memory, 0xA5, sizeof(stack_memory));
}

uint32_t Stack_GetUsage(void) {
    uint32_t unused = 0;
    
    // 从栈底向上查找未使用的空间
    for(uint32_t i = 0; i < sizeof(stack_memory); i++) {
        if(stack_memory[i] != 0xA5) {
            break;
        }
        unused++;
    }
    
    uint32_t used = sizeof(stack_memory) - unused;
    uint32_t usage_percent = (used * 100) / sizeof(stack_memory);
    
    printf("Stack usage: %lu / %lu bytes (%lu%%)\n", 
           used, sizeof(stack_memory), usage_percent);
    
    return used;
}
```

### 内存池设计与实现

内存池是裸机编程中最重要的内存管理技术，它提供了固定大小内存块的快速分配和释放。

#### 基础内存池实现

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 内存池配置
#define POOL_BLOCK_SIZE  64      // 每个块的大小
#define POOL_BLOCK_COUNT 16      // 块的数量

// 内存池结构
typedef struct {
    uint8_t memory[POOL_BLOCK_SIZE * POOL_BLOCK_COUNT];  // 实际内存
    bool used[POOL_BLOCK_COUNT];                          // 使用标记
    uint32_t block_size;                                  // 块大小
    uint32_t block_count;                                 // 块数量
    uint32_t allocated_count;                             // 已分配数量
} MemoryPool_t;

// 全局内存池
static MemoryPool_t g_memory_pool;

// 初始化内存池
void MemPool_Init(void) {
    memset(&g_memory_pool, 0, sizeof(g_memory_pool));
    g_memory_pool.block_size = POOL_BLOCK_SIZE;
    g_memory_pool.block_count = POOL_BLOCK_COUNT;
    g_memory_pool.allocated_count = 0;
}

// 分配内存块
void* MemPool_Alloc(void) {
    // 查找空闲块
    for(uint32_t i = 0; i < g_memory_pool.block_count; i++) {
        if(!g_memory_pool.used[i]) {
            // 找到空闲块
            g_memory_pool.used[i] = true;
            g_memory_pool.allocated_count++;
            
            // 返回块的地址
            return &g_memory_pool.memory[i * g_memory_pool.block_size];
        }
    }
    
    // 没有空闲块
    return NULL;
}

// 释放内存块
bool MemPool_Free(void *ptr) {
    if(ptr == NULL) {
        return false;
    }
    
    // 计算块索引
    uint32_t offset = (uint8_t*)ptr - g_memory_pool.memory;
    uint32_t index = offset / g_memory_pool.block_size;
    
    // 检查有效性
    if(index >= g_memory_pool.block_count) {
        return false;  // 无效指针
    }
    
    if(!g_memory_pool.used[index]) {
        return false;  // 重复释放
    }
    
    // 释放块
    g_memory_pool.used[index] = false;
    g_memory_pool.allocated_count--;
    
    // 可选：清零内存（帮助调试）
    memset(ptr, 0, g_memory_pool.block_size);
    
    return true;
}

// 获取内存池状态
void MemPool_GetStatus(uint32_t *total, uint32_t *used, uint32_t *free) {
    *total = g_memory_pool.block_count;
    *used = g_memory_pool.allocated_count;
    *free = g_memory_pool.block_count - g_memory_pool.allocated_count;
}

// 使用示例
void Example_MemoryPool(void) {
    // 初始化内存池
    MemPool_Init();
    
    // 分配内存块
    uint8_t *buffer1 = (uint8_t*)MemPool_Alloc();
    uint8_t *buffer2 = (uint8_t*)MemPool_Alloc();
    
    if(buffer1 != NULL && buffer2 != NULL) {
        // 使用内存块
        memcpy(buffer1, "Hello", 6);
        memcpy(buffer2, "World", 6);
        
        printf("Buffer1: %s\n", buffer1);
        printf("Buffer2: %s\n", buffer2);
        
        // 释放内存块
        MemPool_Free(buffer1);
        MemPool_Free(buffer2);
    }
    
    // 检查状态
    uint32_t total, used, free;
    MemPool_GetStatus(&total, &used, &free);
    printf("Pool: %lu total, %lu used, %lu free\n", total, used, free);
}
```

**内存池优点**：
- **O(1)时间复杂度**：分配和释放都很快
- **无内存碎片**：固定大小块，不会产生碎片
- **确定性**：分配时间可预测
- **易于调试**：可以跟踪内存使用情况

**内存池缺点**：
- **固定大小**：只能分配固定大小的块
- **可能浪费**：小对象也占用整个块
- **需要预先规划**：必须确定块大小和数量


#### 优化的内存池：使用链表

使用链表可以提高查找效率：

```c
// 内存块头部
typedef struct MemBlock {
    struct MemBlock *next;  // 指向下一个空闲块
} MemBlock_t;

// 优化的内存池
typedef struct {
    uint8_t *memory;           // 内存区域
    MemBlock_t *free_list;     // 空闲链表头
    uint32_t block_size;       // 块大小（包含头部）
    uint32_t block_count;      // 块数量
    uint32_t allocated_count;  // 已分配数量
} MemoryPoolOptimized_t;

// 初始化优化的内存池
void MemPool_Init_Optimized(MemoryPoolOptimized_t *pool, 
                            void *memory, 
                            uint32_t block_size, 
                            uint32_t block_count) {
    pool->memory = (uint8_t*)memory;
    pool->block_size = block_size;
    pool->block_count = block_count;
    pool->allocated_count = 0;
    
    // 构建空闲链表
    pool->free_list = (MemBlock_t*)memory;
    MemBlock_t *current = pool->free_list;
    
    for(uint32_t i = 0; i < block_count - 1; i++) {
        current->next = (MemBlock_t*)((uint8_t*)current + block_size);
        current = current->next;
    }
    current->next = NULL;  // 最后一个块
}

// 分配内存块（O(1)时间）
void* MemPool_Alloc_Optimized(MemoryPoolOptimized_t *pool) {
    if(pool->free_list == NULL) {
        return NULL;  // 没有空闲块
    }
    
    // 从链表头取出一个块
    MemBlock_t *block = pool->free_list;
    pool->free_list = block->next;
    pool->allocated_count++;
    
    // 返回块的数据区域（跳过头部）
    return (void*)block;
}

// 释放内存块（O(1)时间）
void MemPool_Free_Optimized(MemoryPoolOptimized_t *pool, void *ptr) {
    if(ptr == NULL) {
        return;
    }
    
    // 将块插入空闲链表头部
    MemBlock_t *block = (MemBlock_t*)ptr;
    block->next = pool->free_list;
    pool->free_list = block;
    pool->allocated_count--;
}

// 使用示例
#define OPTIMIZED_BLOCK_SIZE 64
#define OPTIMIZED_BLOCK_COUNT 32

uint8_t pool_memory[OPTIMIZED_BLOCK_SIZE * OPTIMIZED_BLOCK_COUNT];
MemoryPoolOptimized_t my_pool;

void Example_OptimizedPool(void) {
    // 初始化
    MemPool_Init_Optimized(&my_pool, pool_memory, 
                          OPTIMIZED_BLOCK_SIZE, 
                          OPTIMIZED_BLOCK_COUNT);
    
    // 快速分配
    void *ptr1 = MemPool_Alloc_Optimized(&my_pool);
    void *ptr2 = MemPool_Alloc_Optimized(&my_pool);
    void *ptr3 = MemPool_Alloc_Optimized(&my_pool);
    
    printf("Allocated: %lu / %lu\n", 
           my_pool.allocated_count, 
           my_pool.block_count);
    
    // 快速释放
    MemPool_Free_Optimized(&my_pool, ptr2);
    MemPool_Free_Optimized(&my_pool, ptr1);
    MemPool_Free_Optimized(&my_pool, ptr3);
}
```

**链表版本的优势**：
- 分配和释放都是O(1)
- 不需要遍历查找空闲块
- 内存开销小（只需要一个指针）

### 堆栈管理

#### 栈溢出检测

```c
// 栈保护字（金丝雀值）
#define STACK_CANARY 0xDEADBEEF

// 在栈底放置保护字
__attribute__((section(".stack_guard")))
uint32_t stack_guard = STACK_CANARY;

// 检查栈是否溢出
bool Stack_CheckOverflow(void) {
    if(stack_guard != STACK_CANARY) {
        // 栈溢出！保护字被破坏
        printf("ERROR: Stack overflow detected!\n");
        return true;
    }
    return false;
}

// 定期检查（在主循环或定时器中）
void MainLoop(void) {
    while(1) {
        // 检查栈溢出
        if(Stack_CheckOverflow()) {
            // 处理栈溢出
            ErrorHandler();
        }
        
        // 正常任务
        DoTasks();
    }
}
```

#### 栈大小配置

```c
// 在启动文件中配置栈大小
// startup_stm32f4xx.s

Stack_Size      EQU     0x00000800  ; 2KB栈空间

                AREA    STACK, NOINIT, READWRITE, ALIGN=3
Stack_Mem       SPACE   Stack_Size
__initial_sp

// 或在链接脚本中配置
/* linker_script.ld */
_estack = 0x20020000;    /* 栈顶地址 */
_Min_Stack_Size = 0x800; /* 最小栈大小 2KB */
```

**栈大小估算**：
```c
// 估算栈使用量
// 1. 主函数栈帧
// 2. 最深函数调用链
// 3. 中断嵌套深度
// 4. 局部变量总和

// 示例计算
// 主函数: 32字节
// 函数A: 64字节
// 函数B: 128字节
// 中断: 100字节 × 2层嵌套
// 安全余量: 50%
// 总计: (32 + 64 + 128 + 200) × 1.5 = 636字节
// 建议: 1024字节（1KB）
```


### 内存优化技巧

#### 1. 使用位域减少内存占用

```c
// 不优化的结构体
typedef struct {
    uint8_t flag1;      // 1字节
    uint8_t flag2;      // 1字节
    uint8_t flag3;      // 1字节
    uint8_t flag4;      // 1字节
    uint8_t status;     // 1字节
    // 总计: 5字节
} DeviceStatus_Normal;

// 使用位域优化
typedef struct {
    uint8_t flag1   : 1;  // 1位
    uint8_t flag2   : 1;  // 1位
    uint8_t flag3   : 1;  // 1位
    uint8_t flag4   : 1;  // 1位
    uint8_t status  : 4;  // 4位
    // 总计: 1字节（节省80%）
} DeviceStatus_Optimized;

// 使用示例
DeviceStatus_Optimized device;
device.flag1 = 1;
device.flag2 = 0;
device.status = 5;
```

#### 2. 结构体对齐优化

```c
// 未优化的结构体（有内存空洞）
typedef struct {
    uint8_t  a;   // 1字节
    // 3字节填充
    uint32_t b;   // 4字节
    uint8_t  c;   // 1字节
    // 3字节填充
    // 总计: 12字节
} BadAlignment;

// 优化后的结构体（按大小排序）
typedef struct {
    uint32_t b;   // 4字节
    uint8_t  a;   // 1字节
    uint8_t  c;   // 1字节
    // 2字节填充
    // 总计: 8字节（节省33%）
} GoodAlignment;

// 使用packed属性（谨慎使用）
typedef struct __attribute__((packed)) {
    uint8_t  a;   // 1字节
    uint32_t b;   // 4字节
    uint8_t  c;   // 1字节
    // 总计: 6字节
    // 注意：可能影响访问性能
} PackedStruct;
```

#### 3. 共用体节省内存

```c
// 使用共用体共享内存
typedef union {
    struct {
        uint8_t byte0;
        uint8_t byte1;
        uint8_t byte2;
        uint8_t byte3;
    } bytes;
    uint32_t word;
} DataConverter;

// 状态机使用共用体
typedef enum {
    STATE_IDLE,
    STATE_RUNNING,
    STATE_ERROR
} State_t;

typedef struct {
    State_t state;
    union {
        struct {
            uint32_t start_time;
            uint32_t duration;
        } running_data;
        struct {
            uint32_t error_code;
            char error_msg[32];
        } error_data;
    } state_data;
} StateMachine_t;

// 使用示例
StateMachine_t sm;
sm.state = STATE_RUNNING;
sm.state_data.running_data.start_time = GetTick();
sm.state_data.running_data.duration = 1000;

// 切换状态
sm.state = STATE_ERROR;
sm.state_data.error_data.error_code = 0x01;
strcpy(sm.state_data.error_data.error_msg, "Timeout");
```

#### 4. 使用const减少RAM占用

```c
// 错误：大数组占用RAM
uint8_t font_data[4096] = { /* ... */ };  // 4KB RAM

// 正确：使用const存储在Flash
const uint8_t font_data[4096] = { /* ... */ };  // 0 RAM, 4KB Flash

// 字符串常量
const char* menu_items[] = {  // 指针数组在RAM，字符串在Flash
    "Start",
    "Stop",
    "Settings",
    "Exit"
};

// 查找表
const uint16_t sin_table[360] = { /* ... */ };  // Flash存储

uint16_t GetSinValue(uint16_t angle) {
    return sin_table[angle % 360];  // 从Flash读取
}
```

#### 5. 缓冲区复用

```c
// 不好的做法：多个独立缓冲区
uint8_t uart_buffer[256];
uint8_t spi_buffer[256];
uint8_t i2c_buffer[256];
// 总计: 768字节

// 好的做法：共享缓冲区（如果不同时使用）
#define COMM_BUFFER_SIZE 256
uint8_t comm_buffer[COMM_BUFFER_SIZE];

void UART_Process(void) {
    // 使用共享缓冲区
    UART_Read(comm_buffer, COMM_BUFFER_SIZE);
    ProcessData(comm_buffer);
}

void SPI_Process(void) {
    // 复用同一缓冲区
    SPI_Read(comm_buffer, COMM_BUFFER_SIZE);
    ProcessData(comm_buffer);
}
```

### 避免内存碎片

#### 内存碎片的产生

```c
// 问题场景：频繁分配不同大小的内存
void* ptr1 = malloc(100);  // 分配100字节
void* ptr2 = malloc(200);  // 分配200字节
void* ptr3 = malloc(100);  // 分配100字节

free(ptr2);  // 释放中间的200字节

// 现在有200字节空闲，但是碎片化了
void* ptr4 = malloc(300);  // 失败！虽然总空闲空间够，但不连续
```

**内存碎片示意图**：
```
初始状态:
[空闲空间: 1000字节]

分配后:
[ptr1:100][ptr2:200][ptr3:100][空闲:600]

释放ptr2后:
[ptr1:100][空闲:200][ptr3:100][空闲:600]
         ↑ 碎片！

尝试分配300字节:
[ptr1:100][空闲:200][ptr3:100][空闲:600]
         ↑ 只有200字节  ↑ 只有600字节
         无法分配连续的300字节！
```

#### 避免碎片的策略

**策略1：使用固定大小的内存池**
```c
// 所有分配都是固定大小，不会产生碎片
MemoryPool_t pool_64;   // 64字节块
MemoryPool_t pool_128;  // 128字节块
MemoryPool_t pool_256;  // 256字节块

void* AllocateMemory(uint32_t size) {
    if(size <= 64) {
        return MemPool_Alloc(&pool_64);
    } else if(size <= 128) {
        return MemPool_Alloc(&pool_128);
    } else if(size <= 256) {
        return MemPool_Alloc(&pool_256);
    }
    return NULL;
}
```

**策略2：避免动态分配**
```c
// 在初始化时一次性分配所有需要的内存
typedef struct {
    uint8_t uart_buffer[256];
    uint8_t spi_buffer[128];
    uint8_t work_buffer[512];
} SystemBuffers_t;

static SystemBuffers_t g_buffers;  // 静态分配，无碎片

void System_Init(void) {
    // 初始化缓冲区
    memset(&g_buffers, 0, sizeof(g_buffers));
}
```

**策略3：使用环形缓冲区**
```c
// 环形缓冲区自动复用空间，无碎片
typedef struct {
    uint8_t buffer[1024];
    uint32_t head;
    uint32_t tail;
} RingBuffer_t;

// 写入和读取操作不会产生碎片
```


## 实践示例

### 示例1：完整的内存管理系统

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// ==================== 内存池管理 ====================

#define SMALL_BLOCK_SIZE  32
#define SMALL_BLOCK_COUNT 20
#define LARGE_BLOCK_SIZE  128
#define LARGE_BLOCK_COUNT 10

typedef struct MemBlock {
    struct MemBlock *next;
} MemBlock_t;

typedef struct {
    uint8_t *memory;
    MemBlock_t *free_list;
    uint32_t block_size;
    uint32_t block_count;
    uint32_t allocated_count;
    uint32_t peak_usage;
} MemPool_t;

// 内存池实例
static uint8_t small_pool_memory[SMALL_BLOCK_SIZE * SMALL_BLOCK_COUNT];
static uint8_t large_pool_memory[LARGE_BLOCK_SIZE * LARGE_BLOCK_COUNT];
static MemPool_t small_pool;
static MemPool_t large_pool;

// 初始化内存池
void MemPool_Init_Internal(MemPool_t *pool, void *memory, 
                           uint32_t block_size, uint32_t block_count) {
    pool->memory = (uint8_t*)memory;
    pool->block_size = block_size;
    pool->block_count = block_count;
    pool->allocated_count = 0;
    pool->peak_usage = 0;
    
    // 构建空闲链表
    pool->free_list = (MemBlock_t*)memory;
    MemBlock_t *current = pool->free_list;
    
    for(uint32_t i = 0; i < block_count - 1; i++) {
        current->next = (MemBlock_t*)((uint8_t*)current + block_size);
        current = current->next;
    }
    current->next = NULL;
}

// 从内存池分配
void* MemPool_Alloc_Internal(MemPool_t *pool) {
    if(pool->free_list == NULL) {
        return NULL;
    }
    
    MemBlock_t *block = pool->free_list;
    pool->free_list = block->next;
    pool->allocated_count++;
    
    // 更新峰值使用量
    if(pool->allocated_count > pool->peak_usage) {
        pool->peak_usage = pool->allocated_count;
    }
    
    return (void*)block;
}

// 释放到内存池
void MemPool_Free_Internal(MemPool_t *pool, void *ptr) {
    if(ptr == NULL) {
        return;
    }
    
    MemBlock_t *block = (MemBlock_t*)ptr;
    block->next = pool->free_list;
    pool->free_list = block;
    pool->allocated_count--;
}

// ==================== 公共接口 ====================

// 初始化内存管理系统
void Memory_Init(void) {
    MemPool_Init_Internal(&small_pool, small_pool_memory, 
                         SMALL_BLOCK_SIZE, SMALL_BLOCK_COUNT);
    MemPool_Init_Internal(&large_pool, large_pool_memory, 
                         LARGE_BLOCK_SIZE, LARGE_BLOCK_COUNT);
    
    printf("Memory system initialized\n");
    printf("Small pool: %u blocks × %u bytes\n", 
           SMALL_BLOCK_COUNT, SMALL_BLOCK_SIZE);
    printf("Large pool: %u blocks × %u bytes\n", 
           LARGE_BLOCK_COUNT, LARGE_BLOCK_SIZE);
}

// 智能分配（根据大小选择合适的池）
void* Memory_Alloc(uint32_t size) {
    if(size == 0) {
        return NULL;
    }
    
    if(size <= SMALL_BLOCK_SIZE) {
        return MemPool_Alloc_Internal(&small_pool);
    } else if(size <= LARGE_BLOCK_SIZE) {
        return MemPool_Alloc_Internal(&large_pool);
    }
    
    // 请求的大小超过最大块
    printf("ERROR: Requested size %lu too large\n", size);
    return NULL;
}

// 释放内存
void Memory_Free(void *ptr) {
    if(ptr == NULL) {
        return;
    }
    
    // 判断属于哪个池
    if(ptr >= (void*)small_pool_memory && 
       ptr < (void*)(small_pool_memory + sizeof(small_pool_memory))) {
        MemPool_Free_Internal(&small_pool, ptr);
    } else if(ptr >= (void*)large_pool_memory && 
              ptr < (void*)(large_pool_memory + sizeof(large_pool_memory))) {
        MemPool_Free_Internal(&large_pool, ptr);
    } else {
        printf("ERROR: Invalid pointer\n");
    }
}

// 获取内存使用统计
void Memory_GetStats(void) {
    printf("\n=== Memory Statistics ===\n");
    
    printf("Small Pool:\n");
    printf("  Allocated: %lu / %lu blocks\n", 
           small_pool.allocated_count, small_pool.block_count);
    printf("  Peak usage: %lu blocks\n", small_pool.peak_usage);
    printf("  Usage: %lu%%\n", 
           (small_pool.allocated_count * 100) / small_pool.block_count);
    
    printf("Large Pool:\n");
    printf("  Allocated: %lu / %lu blocks\n", 
           large_pool.allocated_count, large_pool.block_count);
    printf("  Peak usage: %lu blocks\n", large_pool.peak_usage);
    printf("  Usage: %lu%%\n", 
           (large_pool.allocated_count * 100) / large_pool.block_count);
    
    uint32_t total_allocated = 
        small_pool.allocated_count * SMALL_BLOCK_SIZE +
        large_pool.allocated_count * LARGE_BLOCK_SIZE;
    uint32_t total_capacity = 
        SMALL_BLOCK_COUNT * SMALL_BLOCK_SIZE +
        LARGE_BLOCK_COUNT * LARGE_BLOCK_SIZE;
    
    printf("Total Memory:\n");
    printf("  Allocated: %lu / %lu bytes\n", total_allocated, total_capacity);
    printf("  Usage: %lu%%\n", (total_allocated * 100) / total_capacity);
}

// ==================== 使用示例 ====================

void Example_MemoryManagement(void) {
    // 初始化
    Memory_Init();
    
    // 分配小块内存
    uint8_t *buffer1 = (uint8_t*)Memory_Alloc(20);
    uint8_t *buffer2 = (uint8_t*)Memory_Alloc(30);
    
    // 分配大块内存
    uint8_t *buffer3 = (uint8_t*)Memory_Alloc(100);
    
    if(buffer1 && buffer2 && buffer3) {
        // 使用内存
        memcpy(buffer1, "Small buffer 1", 15);
        memcpy(buffer2, "Small buffer 2", 15);
        memcpy(buffer3, "Large buffer", 13);
        
        printf("Buffer1: %s\n", buffer1);
        printf("Buffer2: %s\n", buffer2);
        printf("Buffer3: %s\n", buffer3);
    }
    
    // 查看统计
    Memory_GetStats();
    
    // 释放内存
    Memory_Free(buffer1);
    Memory_Free(buffer2);
    Memory_Free(buffer3);
    
    // 再次查看统计
    Memory_GetStats();
}
```

**代码说明**：
- 实现了两级内存池（小块和大块）
- 自动选择合适的池进行分配
- 跟踪内存使用统计和峰值
- 提供简单的malloc/free风格接口


### 示例2：内存泄漏检测

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// 内存分配记录
#define MAX_ALLOC_RECORDS 50

typedef struct {
    void *ptr;
    uint32_t size;
    const char *file;
    uint32_t line;
    uint32_t timestamp;
} AllocRecord_t;

static AllocRecord_t alloc_records[MAX_ALLOC_RECORDS];
static uint32_t record_count = 0;

// 记录分配
void Memory_RecordAlloc(void *ptr, uint32_t size, 
                       const char *file, uint32_t line) {
    if(record_count < MAX_ALLOC_RECORDS) {
        alloc_records[record_count].ptr = ptr;
        alloc_records[record_count].size = size;
        alloc_records[record_count].file = file;
        alloc_records[record_count].line = line;
        alloc_records[record_count].timestamp = GetSystemTick();
        record_count++;
    }
}

// 记录释放
void Memory_RecordFree(void *ptr) {
    for(uint32_t i = 0; i < record_count; i++) {
        if(alloc_records[i].ptr == ptr) {
            // 找到记录，移除
            for(uint32_t j = i; j < record_count - 1; j++) {
                alloc_records[j] = alloc_records[j + 1];
            }
            record_count--;
            return;
        }
    }
    
    // 未找到记录，可能是重复释放
    printf("WARNING: Free untracked pointer %p\n", ptr);
}

// 检查内存泄漏
void Memory_CheckLeaks(void) {
    if(record_count == 0) {
        printf("No memory leaks detected\n");
        return;
    }
    
    printf("\n=== Memory Leak Report ===\n");
    printf("Found %lu unreleased allocations:\n", record_count);
    
    uint32_t total_leaked = 0;
    for(uint32_t i = 0; i < record_count; i++) {
        printf("  [%lu] %lu bytes at %p\n", 
               i, alloc_records[i].size, alloc_records[i].ptr);
        printf("      Allocated at %s:%lu\n", 
               alloc_records[i].file, alloc_records[i].line);
        printf("      Time: %lu ms ago\n", 
               GetSystemTick() - alloc_records[i].timestamp);
        total_leaked += alloc_records[i].size;
    }
    
    printf("Total leaked: %lu bytes\n", total_leaked);
}

// 带调试信息的分配宏
#define Memory_Alloc_Debug(size) \
    Memory_Alloc_Internal(size, __FILE__, __LINE__)

void* Memory_Alloc_Internal(uint32_t size, const char *file, uint32_t line) {
    void *ptr = Memory_Alloc(size);
    if(ptr != NULL) {
        Memory_RecordAlloc(ptr, size, file, line);
    }
    return ptr;
}

void Memory_Free_Debug(void *ptr) {
    Memory_RecordFree(ptr);
    Memory_Free(ptr);
}

// 使用示例
void Example_LeakDetection(void) {
    printf("Testing memory leak detection...\n");
    
    // 正常分配和释放
    void *ptr1 = Memory_Alloc_Debug(32);
    void *ptr2 = Memory_Alloc_Debug(64);
    Memory_Free_Debug(ptr1);
    Memory_Free_Debug(ptr2);
    
    // 故意泄漏
    void *leak1 = Memory_Alloc_Debug(100);
    void *leak2 = Memory_Alloc_Debug(200);
    // 忘记释放！
    
    // 检查泄漏
    Memory_CheckLeaks();
}
```

### 示例3：栈使用监控

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 栈监控配置
#define STACK_SIZE 2048
#define STACK_FILL_PATTERN 0xA5
#define STACK_CANARY 0xDEADBEEF

// 栈内存（实际应该在启动代码中定义）
__attribute__((section(".stack")))
uint8_t stack_memory[STACK_SIZE];

// 栈保护字
__attribute__((section(".stack_guard")))
uint32_t stack_guard = STACK_CANARY;

// 初始化栈监控
void Stack_Monitor_Init(void) {
    // 填充栈空间
    memset(stack_memory, STACK_FILL_PATTERN, STACK_SIZE);
    printf("Stack monitor initialized (%u bytes)\n", STACK_SIZE);
}

// 检查栈溢出
bool Stack_CheckOverflow(void) {
    if(stack_guard != STACK_CANARY) {
        printf("CRITICAL: Stack overflow detected!\n");
        printf("Guard value: 0x%08lX (expected 0x%08X)\n", 
               stack_guard, STACK_CANARY);
        return true;
    }
    return false;
}

// 计算栈使用量
uint32_t Stack_GetUsage(void) {
    uint32_t unused = 0;
    
    // 从栈底向上查找
    for(uint32_t i = 0; i < STACK_SIZE; i++) {
        if(stack_memory[i] != STACK_FILL_PATTERN) {
            break;
        }
        unused++;
    }
    
    return STACK_SIZE - unused;
}

// 获取栈使用百分比
uint32_t Stack_GetUsagePercent(void) {
    uint32_t used = Stack_GetUsage();
    return (used * 100) / STACK_SIZE;
}

// 打印栈使用报告
void Stack_PrintReport(void) {
    uint32_t used = Stack_GetUsage();
    uint32_t percent = Stack_GetUsagePercent();
    
    printf("\n=== Stack Usage Report ===\n");
    printf("Stack size: %u bytes\n", STACK_SIZE);
    printf("Used: %lu bytes (%lu%%)\n", used, percent);
    printf("Free: %lu bytes\n", STACK_SIZE - used);
    
    // 警告级别
    if(percent > 90) {
        printf("WARNING: Stack usage critical!\n");
    } else if(percent > 75) {
        printf("WARNING: Stack usage high\n");
    } else if(percent > 50) {
        printf("INFO: Stack usage moderate\n");
    } else {
        printf("INFO: Stack usage normal\n");
    }
    
    // 检查溢出
    if(Stack_CheckOverflow()) {
        printf("ERROR: Stack overflow detected!\n");
    }
}

// 定期监控任务
void Stack_MonitorTask(void) {
    static uint32_t last_check = 0;
    uint32_t now = GetSystemTick();
    
    // 每秒检查一次
    if(now - last_check >= 1000) {
        last_check = now;
        
        // 检查溢出
        if(Stack_CheckOverflow()) {
            // 处理栈溢出
            ErrorHandler();
        }
        
        // 记录峰值使用
        static uint32_t peak_usage = 0;
        uint32_t current_usage = Stack_GetUsage();
        if(current_usage > peak_usage) {
            peak_usage = current_usage;
            printf("New stack peak: %lu bytes (%lu%%)\n", 
                   peak_usage, (peak_usage * 100) / STACK_SIZE);
        }
    }
}

// 使用示例
void Example_StackMonitoring(void) {
    // 初始化
    Stack_Monitor_Init();
    
    // 模拟一些栈使用
    uint8_t buffer[256];
    memset(buffer, 0, sizeof(buffer));
    
    // 打印报告
    Stack_PrintReport();
    
    // 在主循环中定期监控
    while(1) {
        Stack_MonitorTask();
        // 其他任务...
        Delay_ms(100);
    }
}
```


## 深入理解

### 内存对齐的影响

**为什么需要内存对齐？**

现代处理器通常要求数据按照其大小对齐访问：
- 8位数据：任意地址
- 16位数据：2字节对齐
- 32位数据：4字节对齐
- 64位数据：8字节对齐

**未对齐访问的后果**：
```c
// ARM Cortex-M3/M4 示例
uint32_t *ptr = (uint32_t*)0x20000001;  // 未对齐地址
uint32_t value = *ptr;  // 可能触发硬件异常！

// 某些处理器会：
// 1. 触发对齐异常（Hard Fault）
// 2. 自动处理但性能下降（多次访问）
// 3. 读取错误的数据
```

**对齐规则**：
```c
// 编译器自动对齐
struct Example {
    uint8_t  a;   // 偏移0
    // 1字节填充
    uint16_t b;   // 偏移2（2字节对齐）
    uint32_t c;   // 偏移4（4字节对齐）
};  // 总大小8字节

// 查看对齐
printf("Size: %zu\n", sizeof(struct Example));  // 8
printf("Offset a: %zu\n", offsetof(struct Example, a));  // 0
printf("Offset b: %zu\n", offsetof(struct Example, b));  // 2
printf("Offset c: %zu\n", offsetof(struct Example, c));  // 4
```

### DMA与内存管理

**DMA缓冲区要求**：
```c
// DMA缓冲区必须满足：
// 1. 地址对齐（通常4字节或更多）
// 2. 大小对齐
// 3. 位于可访问的内存区域

// 正确的DMA缓冲区定义
__attribute__((aligned(4)))
uint8_t dma_buffer[512];

// 或使用链接脚本指定
__attribute__((section(".dma_buffer")))
uint8_t dma_buffer[512];

// 检查对齐
if(((uint32_t)dma_buffer & 0x03) != 0) {
    printf("ERROR: DMA buffer not aligned!\n");
}
```

**DMA与缓存一致性**：
```c
// 在有缓存的系统中（如Cortex-M7）
// 需要确保缓存一致性

// 方法1：使用非缓存区域
__attribute__((section(".noncacheable")))
uint8_t dma_buffer[512];

// 方法2：手动刷新缓存
void DMA_Transmit(uint8_t *data, uint32_t len) {
    // 刷新数据缓存（写回到内存）
    SCB_CleanDCache_by_Addr((uint32_t*)data, len);
    
    // 启动DMA传输
    DMA_Start(data, len);
}

void DMA_Receive(uint8_t *data, uint32_t len) {
    // 启动DMA接收
    DMA_Start(data, len);
    
    // 等待完成
    while(!DMA_IsComplete());
    
    // 使数据缓存无效（从内存重新读取）
    SCB_InvalidateDCache_by_Addr((uint32_t*)data, len);
}
```

### 内存保护单元（MPU）

**使用MPU保护内存**：
```c
// 配置MPU保护栈区域
void MPU_ConfigureStack(void) {
    // 禁用MPU
    MPU->CTRL = 0;
    
    // 配置区域0：栈区域
    MPU->RNR = 0;  // 选择区域0
    MPU->RBAR = (uint32_t)stack_memory;  // 基地址
    MPU->RASR = 
        (0x01 << MPU_RASR_XN_Pos) |      // 禁止执行
        (0x03 << MPU_RASR_AP_Pos) |      // 读写权限
        (0x0A << MPU_RASR_SIZE_Pos) |    // 2KB大小
        (0x01 << MPU_RASR_ENABLE_Pos);   // 使能
    
    // 使能MPU
    MPU->CTRL = MPU_CTRL_ENABLE_Msk;
}

// MPU可以检测：
// - 栈溢出
// - 非法内存访问
// - 代码区域写入
// - 数据区域执行
```

### 性能考虑

**内存访问速度**：
```
典型的ARM Cortex-M4系统：
- SRAM访问：1个时钟周期
- Flash访问：2-3个时钟周期（有等待状态）
- 外部SDRAM：10+个时钟周期

优化建议：
1. 频繁访问的数据放在SRAM
2. 只读数据（常量）可以放在Flash
3. 关键代码复制到SRAM执行
```

**缓存优化**：
```c
// 对于有缓存的系统（如Cortex-M7）

// 1. 数据局部性
void ProcessData(void) {
    // 好：连续访问，缓存友好
    for(int i = 0; i < 1000; i++) {
        array[i] = array[i] * 2;
    }
    
    // 差：跳跃访问，缓存不友好
    for(int i = 0; i < 1000; i += 100) {
        array[i] = array[i] * 2;
    }
}

// 2. 结构体布局
typedef struct {
    // 将频繁访问的字段放在一起
    uint32_t frequently_used_1;
    uint32_t frequently_used_2;
    // 不常用的字段放在后面
    uint32_t rarely_used[100];
} OptimizedStruct;
```

### 最佳实践总结

**内存分配策略**：
1. **优先静态分配**：编译时确定，最安全
2. **使用内存池**：固定大小，无碎片
3. **避免动态分配**：或仅在初始化时使用
4. **复用缓冲区**：减少内存占用

**内存优化技巧**：
1. **使用const**：常量数据存储在Flash
2. **结构体对齐**：按大小排序字段
3. **位域**：节省标志位空间
4. **共用体**：共享内存空间

**安全措施**：
1. **栈溢出检测**：使用保护字和填充模式
2. **边界检查**：数组访问前检查索引
3. **内存泄漏检测**：跟踪分配和释放
4. **使用MPU**：硬件级内存保护

**调试技巧**：
1. **内存使用统计**：跟踪峰值使用
2. **栈使用监控**：定期检查栈深度
3. **内存填充**：使用特定模式填充
4. **断言检查**：验证指针有效性


## 常见问题

### Q1: 什么时候应该使用动态内存分配？

**A**: 在裸机环境中，应该尽量避免使用动态内存分配（malloc/free）。但在以下情况可以考虑：

1. **初始化阶段一次性分配**：
```c
void System_Init(void) {
    // 在初始化时分配，之后不再释放
    g_large_buffer = malloc(4096);
    if(g_large_buffer == NULL) {
        ErrorHandler();
    }
    // 之后一直使用，不释放
}
```

2. **使用内存池代替**：
```c
// 不要使用malloc/free
void* ptr = malloc(64);
free(ptr);

// 使用内存池
void* ptr = MemPool_Alloc(&pool);
MemPool_Free(&pool, ptr);
```

3. **确实需要动态大小时**：
- 使用专门的内存管理库（如TLSF）
- 严格控制分配和释放
- 充分测试内存碎片情况

### Q2: 如何确定需要多大的栈空间？

**A**: 栈大小估算方法：

```c
// 1. 理论计算
// 栈使用 = 最深调用链 + 中断嵌套 + 安全余量

// 示例计算：
// main(): 32字节局部变量
// FunctionA(): 64字节局部变量
// FunctionB(): 128字节局部变量
// 中断1: 100字节（包括上下文保存）
// 中断2: 100字节
// 安全余量: 50%
// 
// 总计 = (32 + 64 + 128 + 100 + 100) × 1.5 = 636字节
// 建议: 1024字节（向上取整到2的幂次）

// 2. 实际测量
void Measure_Stack_Usage(void) {
    Stack_Monitor_Init();  // 填充栈
    
    // 运行所有可能的代码路径
    RunAllTasks();
    TriggerAllInterrupts();
    
    // 测量峰值使用
    uint32_t peak = Stack_GetUsage();
    printf("Peak stack usage: %lu bytes\n", peak);
    
    // 建议大小 = 峰值 × 1.5（安全余量）
    uint32_t recommended = peak * 3 / 2;
    printf("Recommended stack size: %lu bytes\n", recommended);
}
```

### Q3: 内存池的块大小应该如何选择？

**A**: 块大小选择策略：

```c
// 1. 分析实际使用情况
// 统计程序中所有内存分配的大小

// 2. 使用多级内存池
MemoryPool small_pool;   // 32字节  - 小对象
MemoryPool medium_pool;  // 128字节 - 中等对象
MemoryPool large_pool;   // 512字节 - 大对象

// 3. 根据应用特点
// 串口通信：256字节缓冲区
// 传感器数据：64字节
// 网络数据包：1500字节

// 4. 考虑内存浪费
// 如果大部分分配是50字节，块大小64字节比较合适
// 浪费率 = (64 - 50) / 64 = 22%（可接受）
```

### Q4: 如何检测和调试内存泄漏？

**A**: 内存泄漏检测方法：

```c
// 1. 使用分配跟踪
#define malloc(size) malloc_debug(size, __FILE__, __LINE__)
#define free(ptr) free_debug(ptr, __FILE__, __LINE__)

// 2. 定期检查
void MainLoop(void) {
    while(1) {
        DoTasks();
        
        // 每10秒检查一次
        static uint32_t last_check = 0;
        if(GetTick() - last_check > 10000) {
            Memory_CheckLeaks();
            last_check = GetTick();
        }
    }
}

// 3. 使用静态分析工具
// - PC-lint
// - Coverity
// - Cppcheck

// 4. 运行时监控
void Monitor_Memory(void) {
    static uint32_t baseline = 0;
    uint32_t current = Memory_GetUsed();
    
    if(baseline == 0) {
        baseline = current;
    } else if(current > baseline + 1024) {
        printf("WARNING: Memory usage increased by %lu bytes\n", 
               current - baseline);
    }
}
```

### Q5: 全局变量太多会有什么问题？

**A**: 全局变量的问题和解决方案：

```c
// 问题1：占用RAM
uint8_t buffer1[1024];  // 1KB
uint8_t buffer2[1024];  // 1KB
uint8_t buffer3[1024];  // 1KB
// 总计3KB，可能超过小型MCU的RAM

// 解决方案：使用const或复用
const uint8_t lookup_table[1024] = {...};  // Flash，不占RAM
uint8_t shared_buffer[1024];  // 复用

// 问题2：初始化时间
uint8_t large_array[10000] = {0};  // 启动时需要清零

// 解决方案：按需初始化
uint8_t large_array[10000];  // BSS段，自动清零
// 或延迟初始化
void Init_When_Needed(void) {
    static bool initialized = false;
    if(!initialized) {
        memset(large_array, 0, sizeof(large_array));
        initialized = true;
    }
}

// 问题3：命名冲突和维护性
// 解决方案：使用模块前缀或静态变量
static uint8_t uart_buffer[256];  // 文件内部可见
static uint8_t spi_buffer[256];   // 避免命名冲突
```

## 总结

裸机环境下的内存管理是嵌入式开发的核心技能。本文介绍的关键要点：

**内存管理策略**：
- 优先使用静态分配，避免动态分配
- 使用内存池管理固定大小的内存块
- 合理规划栈空间，防止栈溢出
- 充分利用Flash存储常量数据

**优化技巧**：
- 使用const减少RAM占用
- 结构体字段按大小排序，减少填充
- 使用位域和共用体节省空间
- 复用缓冲区，避免重复分配

**安全措施**：
- 实现栈溢出检测机制
- 跟踪内存分配和释放
- 使用MPU进行硬件级保护
- 定期监控内存使用情况

**调试方法**：
- 使用填充模式检测栈使用
- 实现内存泄漏检测
- 记录峰值内存使用
- 使用断言验证指针有效性

掌握这些技术，你就能在资源受限的嵌入式系统中高效、安全地管理内存，开发出稳定可靠的裸机程序。

## 延伸阅读

推荐进一步学习的资源：

- [环形缓冲区设计与实现](ring-buffer-implementation) - 高效的数据流管理
- [软件定时器实现](software-timer-implementation) - 定时任务管理
- [RTOS内存管理](rtos-memory-management) - 操作系统级内存管理
- [ARM Cortex-M编程手册](https://developer.arm.com/) - 官方文档

## 参考资料

1. ARM Cortex-M3/M4 Technical Reference Manual - ARM官方文档
2. "Embedded Systems Architecture" by Tammy Noergaard - 嵌入式系统架构
3. "Making Embedded Systems" by Elecia White - 嵌入式系统设计
4. MISRA C Guidelines - C语言编码规范
5. "The Art of Designing Embedded Systems" by Jack Ganssle - 嵌入式设计艺术

---

**练习题**：

1. 设计一个支持三种不同大小（32、64、128字节）的多级内存池系统
2. 实现一个栈使用监控系统，能够检测栈溢出并报告峰值使用量
3. 编写一个内存泄漏检测工具，能够跟踪所有分配和释放操作
4. 优化一个包含多个大数组的程序，将RAM使用量减少50%
5. 实现一个简单的内存保护机制，防止数组越界访问

**下一步**：建议学习 [裸机程序调试技巧](bare-metal-debugging)，掌握如何调试内存相关问题。
