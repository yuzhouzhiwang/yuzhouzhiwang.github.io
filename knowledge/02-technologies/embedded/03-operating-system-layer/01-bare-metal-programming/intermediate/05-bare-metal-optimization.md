---
title: "裸机程序性能优化：提升效率与响应速度"
description: "深入学习裸机嵌入式系统的性能优化技术。掌握性能分析方法、代码优化技巧、内存优化策略、中断优化和功耗优化，全面提升系统性能和效率。"
slug: "bare-metal-optimization"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 性能优化
  - 代码优化
  - 效率提升
  - 内存优化
  - 中断优化
  - 功耗优化
prerequisites:
  - "beginner/01-bare-metal-basics.md"
  - "beginner/02-super-loop.md"
  - "beginner/07-bare-metal-memory.md"
related_contents:
  - "intermediate/01-cooperative-scheduler.md"
  - "beginner/08-bare-metal-debugging.md"

# 学习信息
estimated_time: 55
difficulty_score: 7

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
  - 裸机优化
  - 性能优化
  - 代码优化
  - 内存优化
  - 中断优化
  - 功耗优化
  - 嵌入式性能
cover_image: ""
---

# 裸机程序性能优化：提升效率与响应速度

## 概述

在资源受限的嵌入式系统中，性能优化是确保系统稳定运行和满足实时性要求的关键。裸机程序的优化涉及多个层面，从代码层面的算法优化，到硬件层面的外设配置，再到系统层面的架构设计。

完成本文学习后，你将能够：

- 掌握系统性能分析的方法和工具
- 理解并应用代码级优化技巧
- 实施有效的内存优化策略
- 优化中断处理提升响应速度
- 应用功耗优化技术延长电池寿命
- 建立系统化的性能优化思维

## 背景知识

### 为什么需要性能优化？

**嵌入式系统的挑战**：
- **资源限制**：CPU频率、内存容量、存储空间都非常有限
- **实时性要求**：必须在规定时间内完成任务响应
- **功耗约束**：电池供电系统需要长时间运行
- **成本压力**：需要用最低成本的硬件实现功能

**优化的目标**：
- **提升执行速度**：减少任务执行时间，提高响应速度
- **降低内存占用**：在有限RAM中运行更多功能
- **减少代码体积**：节省Flash空间，降低成本
- **降低功耗**：延长电池寿命，减少发热
- **提高稳定性**：避免资源耗尽，提升可靠性

### 性能优化的层次

```
┌─────────────────────────────────────┐
│      算法层优化                      │
│  选择高效算法和数据结构              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      代码层优化                      │
│  编译器优化、循环优化、内联函数      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      系统层优化                      │
│  任务调度、中断管理、DMA使用         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      硬件层优化                      │
│  时钟配置、外设设置、功耗模式        │
└─────────────────────────────────────┘
```

### 优化的基本原则

**帕累托法则（80/20法则）**：
- 80%的执行时间花在20%的代码上
- 优先优化热点代码（Hot Spot）
- 使用性能分析工具找到瓶颈

**优化顺序**：
1. **先正确，后优化**：确保功能正确再考虑优化
2. **先测量，后优化**：用数据指导优化方向
3. **先算法，后细节**：算法优化效果远大于代码细节
4. **先瓶颈，后全局**：集中精力优化性能瓶颈

**权衡考虑**：
- 性能 vs 可读性
- 速度 vs 内存
- 功能 vs 功耗
- 开发时间 vs 优化效果


## 核心内容

### 性能分析方法

在优化之前，必须先了解系统的性能瓶颈在哪里。

#### 方法1：时间测量

使用系统定时器测量代码执行时间：

```c
#include <stdint.h>

// 获取系统时钟计数（假设使用SysTick或DWT）
extern uint32_t GetCycleCount(void);

/**
 * @brief 测量函数执行时间
 * @param func 要测量的函数指针
 * @return 执行周期数
 */
uint32_t MeasureExecutionTime(void (*func)(void)) {
    uint32_t start = GetCycleCount();
    func();
    uint32_t end = GetCycleCount();
    return end - start;
}

// 使用DWT（Data Watchpoint and Trace）进行精确测量
void DWT_Init(void) {
    // 启用DWT
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    // 复位计数器
    DWT->CYCCNT = 0;
    // 启用计数器
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

uint32_t DWT_GetCycles(void) {
    return DWT->CYCCNT;
}

// 测量示例
void Example_TimeMeasurement(void) {
    DWT_Init();
    
    uint32_t start = DWT_GetCycles();
    
    // 执行要测量的代码
    for(int i = 0; i < 1000; i++) {
        volatile int x = i * i;
    }
    
    uint32_t end = DWT_GetCycles();
    uint32_t cycles = end - start;
    
    // 假设CPU频率为72MHz
    float time_us = (float)cycles / 72.0f;
    printf("Execution time: %lu cycles (%.2f us)\n", cycles, time_us);
}
```

#### 方法2：GPIO翻转法

使用GPIO引脚翻转来可视化代码执行：

```c
// 在关键代码段前后翻转GPIO
#define PROFILE_PIN_HIGH()  GPIOA->BSRR = GPIO_PIN_0
#define PROFILE_PIN_LOW()   GPIOA->BSRR = (GPIO_PIN_0 << 16)

void ProfiledFunction(void) {
    PROFILE_PIN_HIGH();  // 开始
    
    // 执行代码
    ProcessData();
    
    PROFILE_PIN_LOW();   // 结束
}

// 使用示波器或逻辑分析仪测量高电平持续时间
```

#### 方法3：统计分析

记录函数调用次数和累计时间：

```c
#include <stdint.h>
#include <string.h>

#define MAX_PROFILE_POINTS 10

typedef struct {
    const char *name;
    uint32_t call_count;
    uint32_t total_cycles;
    uint32_t min_cycles;
    uint32_t max_cycles;
} ProfilePoint_t;

static ProfilePoint_t g_profile_points[MAX_PROFILE_POINTS];
static int g_profile_count = 0;

/**
 * @brief 注册性能分析点
 */
int Profile_Register(const char *name) {
    if(g_profile_count >= MAX_PROFILE_POINTS) {
        return -1;
    }
    
    int id = g_profile_count++;
    g_profile_points[id].name = name;
    g_profile_points[id].call_count = 0;
    g_profile_points[id].total_cycles = 0;
    g_profile_points[id].min_cycles = UINT32_MAX;
    g_profile_points[id].max_cycles = 0;
    
    return id;
}

/**
 * @brief 记录执行时间
 */
void Profile_Record(int id, uint32_t cycles) {
    if(id < 0 || id >= g_profile_count) {
        return;
    }
    
    g_profile_points[id].call_count++;
    g_profile_points[id].total_cycles += cycles;
    
    if(cycles < g_profile_points[id].min_cycles) {
        g_profile_points[id].min_cycles = cycles;
    }
    if(cycles > g_profile_points[id].max_cycles) {
        g_profile_points[id].max_cycles = cycles;
    }
}

/**
 * @brief 打印性能统计
 */
void Profile_Print(void) {
    printf("\n=== Performance Profile ===\n");
    printf("%-20s %10s %12s %10s %10s %10s\n",
           "Function", "Calls", "Total(cyc)", "Avg(cyc)", "Min(cyc)", "Max(cyc)");
    printf("-------------------------------------------------------------------\n");
    
    for(int i = 0; i < g_profile_count; i++) {
        ProfilePoint_t *p = &g_profile_points[i];
        uint32_t avg = (p->call_count > 0) ? (p->total_cycles / p->call_count) : 0;
        
        printf("%-20s %10lu %12lu %10lu %10lu %10lu\n",
               p->name, p->call_count, p->total_cycles,
               avg, p->min_cycles, p->max_cycles);
    }
}

// 使用宏简化性能分析
#define PROFILE_START(id) \
    uint32_t __profile_start_##id = DWT_GetCycles()

#define PROFILE_END(id) \
    do { \
        uint32_t __profile_cycles = DWT_GetCycles() - __profile_start_##id; \
        Profile_Record(id, __profile_cycles); \
    } while(0)

// 使用示例
void Example_Profiling(void) {
    // 注册分析点
    int id_sensor = Profile_Register("ReadSensor");
    int id_process = Profile_Register("ProcessData");
    int id_display = Profile_Register("UpdateDisplay");
    
    // 主循环
    for(int i = 0; i < 100; i++) {
        PROFILE_START(id_sensor);
        ReadSensor();
        PROFILE_END(id_sensor);
        
        PROFILE_START(id_process);
        ProcessData();
        PROFILE_END(id_process);
        
        PROFILE_START(id_display);
        UpdateDisplay();
        PROFILE_END(id_display);
    }
    
    // 打印统计
    Profile_Print();
}
```


### 代码优化技巧

#### 编译器优化选项

合理使用编译器优化可以显著提升性能：

```makefile
# GCC编译器优化级别
# -O0: 无优化（调试用）
# -O1: 基本优化
# -O2: 推荐的优化级别（平衡性能和代码大小）
# -O3: 最高优化（可能增加代码大小）
# -Os: 优化代码大小
# -Og: 优化调试体验

# 推荐配置
CFLAGS = -O2 -Wall -Wextra

# 针对特定CPU优化
CFLAGS += -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16

# 链接时优化（LTO）
CFLAGS += -flto
LDFLAGS += -flto
```

**优化级别对比**：
```c
// 测试代码
int sum_array(int *arr, int len) {
    int sum = 0;
    for(int i = 0; i < len; i++) {
        sum += arr[i];
    }
    return sum;
}

// -O0: ~200 cycles
// -O2: ~50 cycles (循环展开、寄存器优化)
// -O3: ~40 cycles (向量化、更激进的优化)
```

#### 循环优化

**技巧1：循环展开**

```c
// 未优化版本
void ClearBuffer_Slow(uint8_t *buf, int len) {
    for(int i = 0; i < len; i++) {
        buf[i] = 0;
    }
}

// 手动循环展开（4路）
void ClearBuffer_Fast(uint8_t *buf, int len) {
    int i = 0;
    
    // 处理4的倍数部分
    for(; i + 3 < len; i += 4) {
        buf[i]     = 0;
        buf[i + 1] = 0;
        buf[i + 2] = 0;
        buf[i + 3] = 0;
    }
    
    // 处理剩余部分
    for(; i < len; i++) {
        buf[i] = 0;
    }
}

// 使用32位访问（最快）
void ClearBuffer_Fastest(uint8_t *buf, int len) {
    uint32_t *p32 = (uint32_t *)buf;
    int words = len / 4;
    
    // 按32位清零
    for(int i = 0; i < words; i++) {
        p32[i] = 0;
    }
    
    // 处理剩余字节
    int remaining = len % 4;
    uint8_t *p8 = buf + (words * 4);
    for(int i = 0; i < remaining; i++) {
        p8[i] = 0;
    }
}

// 性能对比（1000字节）：
// ClearBuffer_Slow:    ~5000 cycles
// ClearBuffer_Fast:    ~1500 cycles
// ClearBuffer_Fastest: ~400 cycles
```

**技巧2：减少循环判断**

```c
// 低效：每次循环都判断两个条件
void Process_Slow(void) {
    for(int i = 0; i < 100 && !error_flag; i++) {
        ProcessItem(i);
    }
}

// 高效：提前退出
void Process_Fast(void) {
    for(int i = 0; i < 100; i++) {
        if(error_flag) break;
        ProcessItem(i);
    }
}

// 更高效：减少循环次数
void Process_Fastest(void) {
    int i = 0;
    while(i < 100 && !error_flag) {
        ProcessItem(i++);
        if(error_flag) break;
        ProcessItem(i++);
        if(error_flag) break;
        ProcessItem(i++);
        if(error_flag) break;
        ProcessItem(i++);
    }
}
```

**技巧3：循环不变量外提**

```c
// 低效：每次循环都计算相同的值
void Calculate_Slow(int *data, int len, int factor) {
    for(int i = 0; i < len; i++) {
        data[i] = data[i] * (factor + 10) / 2;
    }
}

// 高效：将不变量提到循环外
void Calculate_Fast(int *data, int len, int factor) {
    int multiplier = (factor + 10) / 2;
    for(int i = 0; i < len; i++) {
        data[i] = data[i] * multiplier;
    }
}
```

#### 函数优化

**技巧1：内联函数**

```c
// 小函数使用inline避免函数调用开销
static inline int Max(int a, int b) {
    return (a > b) ? a : b;
}

static inline int Min(int a, int b) {
    return (a < b) ? a : b;
}

// 使用__attribute__((always_inline))强制内联
__attribute__((always_inline))
static inline uint32_t SwapBytes(uint32_t value) {
    return __builtin_bswap32(value);
}

// 性能对比：
// 函数调用：~10 cycles（包括压栈、跳转、返回）
// 内联：    ~1 cycle（直接执行）
```

**技巧2：避免递归**

```c
// 递归版本（低效，可能栈溢出）
int Fibonacci_Recursive(int n) {
    if(n <= 1) return n;
    return Fibonacci_Recursive(n - 1) + Fibonacci_Recursive(n - 2);
}

// 迭代版本（高效）
int Fibonacci_Iterative(int n) {
    if(n <= 1) return n;
    
    int prev = 0, curr = 1;
    for(int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}

// 性能对比（n=20）：
// Recursive:  ~21891 次函数调用，~100000 cycles
// Iterative:  ~20 次循环，~100 cycles
```

**技巧3：查表法**

```c
// 计算版本（慢）
uint8_t CalculateCRC(uint8_t data) {
    uint8_t crc = 0;
    for(int i = 0; i < 8; i++) {
        if((crc ^ data) & 0x01) {
            crc = (crc >> 1) ^ 0x8C;
        } else {
            crc >>= 1;
        }
        data >>= 1;
    }
    return crc;
}

// 查表版本（快）
static const uint8_t crc_table[256] = {
    0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83,
    // ... 预计算的CRC表
};

uint8_t LookupCRC(uint8_t data) {
    return crc_table[data];
}

// 性能对比：
// Calculate: ~80 cycles
// Lookup:    ~5 cycles
```

#### 数据类型优化

```c
// 使用合适的数据类型
// 低效：使用64位类型（在32位MCU上）
uint64_t counter = 0;
counter++;  // 需要多条指令

// 高效：使用32位类型
uint32_t counter = 0;
counter++;  // 单条指令

// 位域优化
// 低效：使用多个变量
typedef struct {
    uint8_t flag1;
    uint8_t flag2;
    uint8_t flag3;
    uint8_t flag4;
} Flags_Slow;  // 占用4字节

// 高效：使用位域
typedef struct {
    uint8_t flag1 : 1;
    uint8_t flag2 : 1;
    uint8_t flag3 : 1;
    uint8_t flag4 : 1;
    uint8_t reserved : 4;
} Flags_Fast;  // 占用1字节

// 对齐优化
// 低效：未对齐
typedef struct {
    uint8_t  a;  // 1字节
    uint32_t b;  // 4字节，需要对齐
    uint8_t  c;  // 1字节
} Data_Slow;  // 实际占用12字节（有填充）

// 高效：手动对齐
typedef struct {
    uint32_t b;  // 4字节
    uint8_t  a;  // 1字节
    uint8_t  c;  // 1字节
    uint16_t pad;// 2字节填充
} Data_Fast;  // 占用8字节
```


### 内存优化策略

#### 减少全局变量

```c
// 低效：大量全局变量
uint8_t buffer1[1024];
uint8_t buffer2[1024];
uint8_t buffer3[1024];
// 总是占用3KB RAM

// 高效：复用缓冲区
typedef union {
    uint8_t buffer1[1024];
    uint8_t buffer2[1024];
    uint8_t buffer3[1024];
} SharedBuffer_t;

SharedBuffer_t g_shared_buffer;
// 只占用1KB RAM

// 使用时：
void Task1(void) {
    uint8_t *buf = g_shared_buffer.buffer1;
    // 使用buf...
}

void Task2(void) {
    uint8_t *buf = g_shared_buffer.buffer2;
    // 使用buf...
}
```

#### 使用const和ROM

```c
// 低效：常量数据占用RAM
uint8_t sine_table[256] = {
    0, 3, 6, 9, 12, 15, 18, 21, // ...
};

// 高效：常量数据放在Flash
const uint8_t sine_table[256] = {
    0, 3, 6, 9, 12, 15, 18, 21, // ...
};

// 字符串优化
// 低效：字符串在RAM中
char *msg = "Hello World";

// 高效：字符串在Flash中
const char *msg = "Hello World";

// 使用PROGMEM（AVR）或__attribute__((section(".rodata")))
```

#### 栈空间优化

```c
// 低效：大数组在栈上
void ProcessData_Slow(void) {
    uint8_t temp_buffer[2048];  // 占用2KB栈空间
    // 处理数据...
}

// 高效：使用静态变量或动态分配
void ProcessData_Fast(void) {
    static uint8_t temp_buffer[2048];  // 占用全局区
    // 处理数据...
}

// 或使用内存池
void ProcessData_Pool(void) {
    uint8_t *temp_buffer = MemPool_Alloc(2048);
    if(temp_buffer != NULL) {
        // 处理数据...
        MemPool_Free(temp_buffer);
    }
}
```

#### 数据压缩

```c
// 位打包
typedef struct {
    uint32_t sensor1 : 10;  // 0-1023
    uint32_t sensor2 : 10;  // 0-1023
    uint32_t sensor3 : 10;  // 0-1023
    uint32_t reserved : 2;
} SensorData_Packed;  // 4字节

// vs 未打包
typedef struct {
    uint16_t sensor1;  // 2字节
    uint16_t sensor2;  // 2字节
    uint16_t sensor3;  // 2字节
} SensorData_Normal;  // 6字节

// 节省33%内存
```

### 中断优化

#### 减少中断延迟

```c
// 低效：中断中执行复杂操作
void UART_IRQHandler(void) {
    if(UART->SR & UART_SR_RXNE) {
        uint8_t data = UART->DR;
        
        // 不好：在中断中处理数据
        ProcessReceivedData(data);
        UpdateDisplay();
        SaveToFlash(data);
    }
}

// 高效：中断中只做必要操作
volatile uint8_t g_rx_buffer[256];
volatile uint8_t g_rx_head = 0;
volatile uint8_t g_rx_tail = 0;
volatile bool g_data_ready = false;

void UART_IRQHandler(void) {
    if(UART->SR & UART_SR_RXNE) {
        uint8_t data = UART->DR;
        
        // 只存储数据
        g_rx_buffer[g_rx_head] = data;
        g_rx_head = (g_rx_head + 1) % 256;
        g_data_ready = true;
    }
}

// 在主循环中处理
void MainLoop(void) {
    while(1) {
        if(g_data_ready) {
            while(g_rx_tail != g_rx_head) {
                uint8_t data = g_rx_buffer[g_rx_tail];
                g_rx_tail = (g_rx_tail + 1) % 256;
                
                ProcessReceivedData(data);
            }
            g_data_ready = false;
        }
    }
}
```

#### 中断优先级配置

```c
// 合理设置中断优先级
void InterruptPriority_Init(void) {
    // 最高优先级：关键实时任务
    NVIC_SetPriority(TIM1_IRQn, 0);  // 电机控制
    
    // 高优先级：重要外设
    NVIC_SetPriority(UART1_IRQn, 1); // 通信
    NVIC_SetPriority(ADC_IRQn, 1);   // 采样
    
    // 中等优先级：一般外设
    NVIC_SetPriority(TIM2_IRQn, 2);  // 定时任务
    
    // 低优先级：非关键任务
    NVIC_SetPriority(EXTI0_IRQn, 3); // 按键
}
```

#### 使用DMA减少CPU负担

```c
// 低效：CPU搬运数据
void TransferData_CPU(uint8_t *src, uint8_t *dst, int len) {
    for(int i = 0; i < len; i++) {
        dst[i] = src[i];
    }
}

// 高效：使用DMA
void TransferData_DMA(uint8_t *src, uint8_t *dst, int len) {
    // 配置DMA
    DMA1_Channel1->CPAR = (uint32_t)src;
    DMA1_Channel1->CMAR = (uint32_t)dst;
    DMA1_Channel1->CNDTR = len;
    DMA1_Channel1->CCR = DMA_CCR_MEM2MEM | DMA_CCR_MINC | 
                         DMA_CCR_PINC | DMA_CCR_EN;
    
    // CPU可以做其他事情
    // DMA完成后会触发中断
}

// UART DMA接收
void UART_DMA_Init(void) {
    // 配置DMA接收
    DMA1_Channel5->CPAR = (uint32_t)&USART1->DR;
    DMA1_Channel5->CMAR = (uint32_t)g_rx_buffer;
    DMA1_Channel5->CNDTR = sizeof(g_rx_buffer);
    DMA1_Channel5->CCR = DMA_CCR_MINC | DMA_CCR_CIRC | DMA_CCR_EN;
    
    // 启用UART DMA接收
    USART1->CR3 |= USART_CR3_DMAR;
}
```


### 功耗优化

#### 时钟管理

```c
// 动态调整时钟频率
typedef enum {
    CLOCK_MODE_HIGH_PERFORMANCE,  // 72MHz
    CLOCK_MODE_NORMAL,            // 36MHz
    CLOCK_MODE_LOW_POWER          // 8MHz
} ClockMode_t;

void SetClockMode(ClockMode_t mode) {
    switch(mode) {
        case CLOCK_MODE_HIGH_PERFORMANCE:
            // 配置PLL到72MHz
            RCC->CFGR |= RCC_CFGR_PLLMULL9;  // PLL x9
            RCC->CR |= RCC_CR_PLLON;
            while(!(RCC->CR & RCC_CR_PLLRDY));
            RCC->CFGR |= RCC_CFGR_SW_PLL;
            break;
            
        case CLOCK_MODE_NORMAL:
            // 配置到36MHz
            RCC->CFGR &= ~RCC_CFGR_PLLMULL;
            RCC->CFGR |= RCC_CFGR_PLLMULL4;  // PLL x4
            break;
            
        case CLOCK_MODE_LOW_POWER:
            // 使用内部8MHz时钟
            RCC->CFGR &= ~RCC_CFGR_SW;
            RCC->CFGR |= RCC_CFGR_SW_HSI;
            RCC->CR &= ~RCC_CR_PLLON;  // 关闭PLL
            break;
    }
}

// 根据任务负载动态调整
void AdaptiveClockManagement(void) {
    static uint32_t idle_count = 0;
    
    if(IsSystemBusy()) {
        SetClockMode(CLOCK_MODE_HIGH_PERFORMANCE);
        idle_count = 0;
    } else {
        idle_count++;
        if(idle_count > 1000) {
            SetClockMode(CLOCK_MODE_LOW_POWER);
        }
    }
}
```

#### 外设时钟门控

```c
// 关闭不使用的外设时钟
void DisableUnusedPeripherals(void) {
    // 关闭不使用的外设
    RCC->APB1ENR &= ~(RCC_APB1ENR_TIM2EN |   // TIM2
                      RCC_APB1ENR_TIM3EN |   // TIM3
                      RCC_APB1ENR_SPI2EN);   // SPI2
    
    RCC->APB2ENR &= ~(RCC_APB2ENR_ADC2EN |   // ADC2
                      RCC_APB2ENR_USART2EN); // USART2
}

// 动态开关外设
void EnablePeripheralOnDemand(void) {
    // 使用前开启
    RCC->APB1ENR |= RCC_APB1ENR_SPI2EN;
    
    // 使用SPI2
    SPI2_Transfer(data);
    
    // 使用后关闭
    RCC->APB1ENR &= ~RCC_APB1ENR_SPI2EN;
}
```

#### 睡眠模式

```c
// 睡眠模式类型
typedef enum {
    SLEEP_MODE_NONE,    // 正常运行
    SLEEP_MODE_SLEEP,   // 睡眠模式（CPU停止，外设运行）
    SLEEP_MODE_STOP,    // 停止模式（CPU和大部分外设停止）
    SLEEP_MODE_STANDBY  // 待机模式（最低功耗）
} SleepMode_t;

/**
 * @brief 进入睡眠模式
 */
void EnterSleepMode(SleepMode_t mode) {
    switch(mode) {
        case SLEEP_MODE_SLEEP:
            // 睡眠模式：WFI（等待中断）
            __WFI();
            break;
            
        case SLEEP_MODE_STOP:
            // 停止模式
            PWR->CR |= PWR_CR_LPDS;  // 低功耗深度睡眠
            SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
            __WFI();
            // 唤醒后需要重新配置时钟
            SystemClock_Config();
            break;
            
        case SLEEP_MODE_STANDBY:
            // 待机模式
            PWR->CR |= PWR_CR_PDDS;  // 进入待机
            PWR->CR |= PWR_CR_CWUF;  // 清除唤醒标志
            SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
            __WFI();
            // 待机唤醒后会复位
            break;
            
        default:
            break;
    }
}

/**
 * @brief 智能睡眠管理
 */
void SmartSleepManagement(void) {
    static uint32_t last_activity = 0;
    uint32_t current_time = GetSystemTick();
    
    // 检查是否有待处理任务
    if(HasPendingTasks()) {
        last_activity = current_time;
        return;
    }
    
    // 根据空闲时间选择睡眠模式
    uint32_t idle_time = current_time - last_activity;
    
    if(idle_time < 10) {
        // 短时间空闲：不睡眠
        return;
    } else if(idle_time < 100) {
        // 中等空闲：睡眠模式
        EnterSleepMode(SLEEP_MODE_SLEEP);
    } else if(idle_time < 1000) {
        // 长时间空闲：停止模式
        EnterSleepMode(SLEEP_MODE_STOP);
    } else {
        // 很长时间空闲：待机模式
        EnterSleepMode(SLEEP_MODE_STANDBY);
    }
}
```

#### GPIO配置优化

```c
/**
 * @brief 配置GPIO为低功耗模式
 */
void GPIO_LowPowerConfig(void) {
    // 未使用的GPIO配置为模拟输入（最低功耗）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 只配置使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}
```

### 算法优化

#### 选择高效算法

```c
// 示例：查找最大值
// 方法1：线性查找 O(n)
int FindMax_Linear(int *arr, int len) {
    int max = arr[0];
    for(int i = 1; i < len; i++) {
        if(arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}

// 方法2：分治法（如果数据有序）O(1)
int FindMax_Sorted(int *arr, int len) {
    return arr[len - 1];  // 假设升序排列
}

// 示例：数据过滤
// 方法1：移动平均 O(n)
int MovingAverage(int *data, int len) {
    int sum = 0;
    for(int i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum / len;
}

// 方法2：增量更新 O(1)
typedef struct {
    int sum;
    int count;
    int buffer[10];
    int index;
} MovingAvg_t;

void MovingAvg_Init(MovingAvg_t *avg) {
    avg->sum = 0;
    avg->count = 0;
    avg->index = 0;
}

int MovingAvg_Update(MovingAvg_t *avg, int new_value) {
    // 减去旧值
    if(avg->count >= 10) {
        avg->sum -= avg->buffer[avg->index];
    } else {
        avg->count++;
    }
    
    // 加上新值
    avg->buffer[avg->index] = new_value;
    avg->sum += new_value;
    avg->index = (avg->index + 1) % 10;
    
    return avg->sum / avg->count;
}
```

#### 定点运算代替浮点

```c
// 浮点运算（慢）
float CalculateVoltage_Float(uint16_t adc_value) {
    float voltage = (float)adc_value * 3.3f / 4096.0f;
    return voltage;
}

// 定点运算（快）
// 使用Q16.16格式（16位整数，16位小数）
#define FLOAT_TO_FIXED(x) ((int32_t)((x) * 65536.0f))
#define FIXED_TO_FLOAT(x) ((float)(x) / 65536.0f)

int32_t CalculateVoltage_Fixed(uint16_t adc_value) {
    // 3.3 / 4096 = 0.000805664 ≈ 52.8 (Q16.16)
    int32_t voltage = (adc_value * 52) >> 6;  // 除以64近似
    return voltage;
}

// 性能对比：
// Float:  ~100 cycles（如果没有FPU）
// Fixed:  ~5 cycles

// 定点乘法
int32_t FixedMul(int32_t a, int32_t b) {
    return (int32_t)(((int64_t)a * b) >> 16);
}

// 定点除法
int32_t FixedDiv(int32_t a, int32_t b) {
    return (int32_t)(((int64_t)a << 16) / b);
}
```


## 实践示例

### 示例1：完整的性能优化案例

优化一个数据采集和处理系统：

```c
#include <stdint.h>
#include <stdbool.h>

// ========== 优化前的代码 ==========

// 低效的实现
typedef struct {
    float temperature;
    float humidity;
    float pressure;
    uint32_t timestamp;
} SensorData_Old;

SensorData_Old g_sensor_buffer_old[100];
int g_buffer_index_old = 0;

void ProcessSensor_Old(void) {
    // 读取传感器（阻塞）
    float temp = ReadTemperature();      // ~1000 cycles
    float humi = ReadHumidity();         // ~1000 cycles
    float pres = ReadPressure();         // ~1000 cycles
    
    // 浮点计算
    float temp_celsius = (temp - 32.0f) * 5.0f / 9.0f;  // ~100 cycles
    float humi_percent = humi * 100.0f;                  // ~50 cycles
    
    // 存储数据
    g_sensor_buffer_old[g_buffer_index_old].temperature = temp_celsius;
    g_sensor_buffer_old[g_buffer_index_old].humidity = humi_percent;
    g_sensor_buffer_old[g_buffer_index_old].pressure = pres;
    g_sensor_buffer_old[g_buffer_index_old].timestamp = GetSystemTick();
    
    g_buffer_index_old++;
    if(g_buffer_index_old >= 100) {
        g_buffer_index_old = 0;
    }
    
    // 数据处理
    float avg_temp = 0;
    for(int i = 0; i < 100; i++) {
        avg_temp += g_sensor_buffer_old[i].temperature;
    }
    avg_temp /= 100.0f;
    
    // 显示结果
    UpdateDisplay(avg_temp);
}

// 总耗时：~3500 cycles
// 内存占用：100 * 16 = 1600 bytes

// ========== 优化后的代码 ==========

// 使用定点数和紧凑存储
typedef struct {
    int16_t temperature;  // Q8.8格式（-128~127，精度0.004）
    uint16_t humidity;    // 0-10000表示0-100%
    uint16_t pressure;    // 单位：0.1 hPa
    uint16_t timestamp;   // 相对时间戳（秒）
} SensorData_New __attribute__((packed));

SensorData_New g_sensor_buffer_new[100];
uint8_t g_buffer_index_new = 0;

// 使用DMA读取传感器
volatile bool g_sensor_ready = false;
uint16_t g_adc_values[3];

void StartSensorRead_DMA(void) {
    // 配置ADC DMA读取3个通道
    ADC1->CR2 |= ADC_CR2_DMA;
    DMA1_Channel1->CMAR = (uint32_t)g_adc_values;
    DMA1_Channel1->CNDTR = 3;
    DMA1_Channel1->CCR |= DMA_CCR_EN;
    
    // 启动ADC转换
    ADC1->CR2 |= ADC_CR2_SWSTART;
}

void DMA1_Channel1_IRQHandler(void) {
    if(DMA1->ISR & DMA_ISR_TCIF1) {
        DMA1->IFCR = DMA_IFCR_CTCIF1;
        g_sensor_ready = true;
    }
}

// 优化的处理函数
int32_t g_temp_sum = 0;  // 累加和，避免每次重新计算

void ProcessSensor_New(void) {
    if(!g_sensor_ready) {
        return;  // 数据未就绪，直接返回
    }
    g_sensor_ready = false;
    
    // 定点转换（使用查表或位移）
    int16_t temp = (g_adc_values[0] * 165 >> 8) - 40;  // ~10 cycles
    uint16_t humi = (g_adc_values[1] * 100 >> 8);      // ~5 cycles
    uint16_t pres = g_adc_values[2];                    // ~1 cycle
    
    // 更新累加和（增量更新）
    if(g_buffer_index_new < 100) {
        g_temp_sum += temp;
    } else {
        // 减去旧值，加上新值
        g_temp_sum -= g_sensor_buffer_new[g_buffer_index_new].temperature;
        g_temp_sum += temp;
    }
    
    // 存储数据
    g_sensor_buffer_new[g_buffer_index_new].temperature = temp;
    g_sensor_buffer_new[g_buffer_index_new].humidity = humi;
    g_sensor_buffer_new[g_buffer_index_new].pressure = pres;
    g_sensor_buffer_new[g_buffer_index_new].timestamp = 
        (uint16_t)(GetSystemTick() / 1000);
    
    g_buffer_index_new = (g_buffer_index_new + 1) % 100;
    
    // 计算平均值（O(1)）
    int16_t avg_temp = g_temp_sum / 100;
    
    // 更新显示（异步）
    QueueDisplayUpdate(avg_temp);
}

// 总耗时：~50 cycles（不包括DMA传输时间）
// 内存占用：100 * 8 = 800 bytes

// 性能提升：70倍
// 内存节省：50%
```

### 示例2：实时任务优化

优化一个电机控制系统：

```c
// ========== 优化前 ==========

void MotorControl_Old(void) {
    // 读取编码器
    int32_t position = ReadEncoder();
    
    // PID计算（浮点）
    float error = target_position - position;
    float p_term = Kp * error;
    float i_term = Ki * integral;
    float d_term = Kd * (error - last_error);
    float output = p_term + i_term + d_term;
    
    // 限幅
    if(output > 100.0f) output = 100.0f;
    if(output < -100.0f) output = -100.0f;
    
    // 输出PWM
    SetPWM((int)output);
    
    // 更新状态
    integral += error;
    last_error = error;
}

// 耗时：~500 cycles

// ========== 优化后 ==========

// 使用定点PID
typedef struct {
    int32_t kp;        // Q16.16
    int32_t ki;        // Q16.16
    int32_t kd;        // Q16.16
    int32_t integral;  // Q16.16
    int32_t last_error;
    int32_t output_max;
    int32_t output_min;
} PID_Fixed_t;

PID_Fixed_t g_motor_pid = {
    .kp = FLOAT_TO_FIXED(1.5f),
    .ki = FLOAT_TO_FIXED(0.1f),
    .kd = FLOAT_TO_FIXED(0.05f),
    .output_max = FLOAT_TO_FIXED(100.0f),
    .output_min = FLOAT_TO_FIXED(-100.0f)
};

__attribute__((optimize("O3")))
void MotorControl_New(void) {
    // 读取编码器（使用硬件定时器）
    int32_t position = TIM2->CNT;
    
    // 定点PID计算
    int32_t error = g_target_position - position;
    
    // P项
    int32_t p_term = FixedMul(g_motor_pid.kp, error);
    
    // I项（带抗饱和）
    g_motor_pid.integral += error;
    if(g_motor_pid.integral > (1 << 20)) {
        g_motor_pid.integral = (1 << 20);
    } else if(g_motor_pid.integral < -(1 << 20)) {
        g_motor_pid.integral = -(1 << 20);
    }
    int32_t i_term = FixedMul(g_motor_pid.ki, g_motor_pid.integral);
    
    // D项
    int32_t d_error = error - g_motor_pid.last_error;
    int32_t d_term = FixedMul(g_motor_pid.kd, d_error);
    
    // 输出
    int32_t output = p_term + i_term + d_term;
    
    // 限幅（使用位运算）
    if(output > g_motor_pid.output_max) {
        output = g_motor_pid.output_max;
    } else if(output < g_motor_pid.output_min) {
        output = g_motor_pid.output_min;
    }
    
    // 输出PWM（直接写寄存器）
    TIM1->CCR1 = (output >> 16) + 50;  // 转换为0-100
    
    // 更新状态
    g_motor_pid.last_error = error;
}

// 耗时：~80 cycles
// 性能提升：6倍
```

### 示例3：通信协议优化

```c
// ========== 优化前：逐字节处理 ==========

void ProcessUART_Old(void) {
    if(UART->SR & UART_SR_RXNE) {
        uint8_t byte = UART->DR;
        
        // 逐字节解析协议
        switch(g_state) {
            case STATE_HEADER:
                if(byte == 0xAA) {
                    g_state = STATE_LENGTH;
                }
                break;
            case STATE_LENGTH:
                g_length = byte;
                g_state = STATE_DATA;
                g_index = 0;
                break;
            case STATE_DATA:
                g_buffer[g_index++] = byte;
                if(g_index >= g_length) {
                    g_state = STATE_CHECKSUM;
                }
                break;
            case STATE_CHECKSUM:
                if(byte == CalculateChecksum(g_buffer, g_length)) {
                    ProcessPacket(g_buffer, g_length);
                }
                g_state = STATE_HEADER;
                break;
        }
    }
}

// ========== 优化后：DMA + 批量处理 ==========

#define RX_BUFFER_SIZE 256

uint8_t g_rx_dma_buffer[RX_BUFFER_SIZE];
volatile uint16_t g_last_dma_pos = 0;

void UART_DMA_Init_Optimized(void) {
    // 配置循环DMA接收
    DMA1_Channel5->CPAR = (uint32_t)&USART1->DR;
    DMA1_Channel5->CMAR = (uint32_t)g_rx_dma_buffer;
    DMA1_Channel5->CNDTR = RX_BUFFER_SIZE;
    DMA1_Channel5->CCR = DMA_CCR_MINC | DMA_CCR_CIRC | 
                         DMA_CCR_TCIE | DMA_CCR_EN;
    
    USART1->CR3 |= USART_CR3_DMAR;
}

void ProcessUART_New(void) {
    // 获取当前DMA位置
    uint16_t current_pos = RX_BUFFER_SIZE - DMA1_Channel5->CNDTR;
    
    if(current_pos == g_last_dma_pos) {
        return;  // 没有新数据
    }
    
    // 批量处理数据
    while(g_last_dma_pos != current_pos) {
        uint8_t byte = g_rx_dma_buffer[g_last_dma_pos];
        g_last_dma_pos = (g_last_dma_pos + 1) % RX_BUFFER_SIZE;
        
        // 快速协议解析（使用查表）
        ParseProtocol_Fast(byte);
    }
}

// 使用状态机查表加速
typedef void (*StateHandler_t)(uint8_t byte);

void Handle_Header(uint8_t byte);
void Handle_Length(uint8_t byte);
void Handle_Data(uint8_t byte);
void Handle_Checksum(uint8_t byte);

StateHandler_t g_state_handlers[] = {
    Handle_Header,
    Handle_Length,
    Handle_Data,
    Handle_Checksum
};

void ParseProtocol_Fast(uint8_t byte) {
    g_state_handlers[g_protocol_state](byte);
}

// 性能提升：10倍（减少中断次数）
```


## 最佳实践

### 优化流程

1. **性能分析**
   - 使用工具测量实际性能
   - 识别性能瓶颈（热点代码）
   - 建立性能基准

2. **优先级排序**
   - 优先优化影响最大的部分
   - 考虑优化成本和收益
   - 避免过早优化

3. **实施优化**
   - 一次优化一个点
   - 保持代码可读性
   - 添加注释说明优化原因

4. **验证效果**
   - 测量优化后的性能
   - 确保功能正确性
   - 检查副作用

5. **文档记录**
   - 记录优化方法和效果
   - 说明权衡考虑
   - 便于后续维护

### 常见陷阱

**陷阱1：过早优化**
```c
// 不要这样做：在不了解性能瓶颈前就优化
void ProcessData(uint8_t *data, int len) {
    // 复杂的优化代码，但这个函数每秒只调用一次
    // 优化效果微乎其微，反而降低了可读性
}

// 应该这样：先确保正确，再根据需要优化
void ProcessData(uint8_t *data, int len) {
    // 清晰简单的实现
    // 如果性能分析显示这是瓶颈，再考虑优化
}
```

**陷阱2：牺牲可维护性**
```c
// 不好：过度优化导致难以理解
#define FAST_MOD(x, y) ((x) & ((y) - 1))  // 只对2的幂有效
int index = FAST_MOD(i, 16);  // 不明显

// 好：清晰的代码 + 注释
int index = i % 16;  // 编译器会优化为位运算
```

**陷阱3：忽略编译器优化**
```c
// 不必要的手动优化
int sum = 0;
for(int i = 0; i < 100; i += 4) {
    sum += arr[i];
    sum += arr[i+1];
    sum += arr[i+2];
    sum += arr[i+3];
}

// 编译器通常会自动做循环展开
int sum = 0;
for(int i = 0; i < 100; i++) {
    sum += arr[i];
}
// 使用 -O2 或 -O3 编译
```

### 性能优化检查清单

**代码层面**：
- [ ] 使用合适的编译器优化级别（-O2/-O3）
- [ ] 避免不必要的函数调用（使用inline）
- [ ] 减少循环内的计算
- [ ] 使用位运算代替乘除法（2的幂）
- [ ] 避免浮点运算（使用定点数）
- [ ] 使用查表法代替复杂计算

**内存层面**：
- [ ] 减少全局变量使用
- [ ] 复用缓冲区
- [ ] 使用const将常量放在Flash
- [ ] 优化数据结构对齐
- [ ] 使用位域压缩数据

**系统层面**：
- [ ] 使用DMA减少CPU负担
- [ ] 优化中断优先级
- [ ] 减少中断处理时间
- [ ] 使用硬件定时器
- [ ] 合理使用睡眠模式

**功耗层面**：
- [ ] 动态调整时钟频率
- [ ] 关闭不使用的外设
- [ ] 使用低功耗模式
- [ ] 优化GPIO配置
- [ ] 减少唤醒频率

### 性能优化工具

**测量工具**：
- **DWT（Data Watchpoint and Trace）**：精确的周期计数
- **SysTick**：毫秒级时间测量
- **GPIO + 示波器**：可视化时序
- **SEGGER SystemView**：系统级性能分析
- **Ozone Debugger**：代码覆盖率和性能分析

**分析工具**：
- **编译器报告**：查看优化效果
  ```bash
  arm-none-eabi-gcc -O2 -S main.c  # 生成汇编代码
  arm-none-eabi-size firmware.elf  # 查看代码大小
  ```
- **静态分析**：检查代码质量
  ```bash
  cppcheck --enable=all src/
  ```
- **内存分析**：检查内存使用
  ```bash
  arm-none-eabi-nm -S --size-sort firmware.elf
  ```

## 进阶学习

### 推荐资源

**书籍**：
- 《嵌入式系统软件优化》
- 《ARM Cortex-M3权威指南》
- 《Writing Efficient C Code》

**在线资源**：
- ARM官方优化指南
- GCC优化选项文档
- 芯片厂商应用笔记

**工具**：
- SEGGER SystemView
- Percepio Tracealyzer
- Keil MDK Performance Analyzer

### 相关主题

- **RTOS优化**：任务调度、同步机制优化
- **编译器原理**：理解编译器如何优化代码
- **处理器架构**：了解CPU流水线、缓存机制
- **汇编语言**：关键代码的汇编优化
- **硬件加速**：使用协处理器、DSP指令

## 总结

性能优化是嵌入式开发的重要技能，需要系统化的方法和实践经验。关键要点：

1. **测量先行**：使用工具找到真正的性能瓶颈
2. **分层优化**：从算法到代码到硬件，逐层优化
3. **权衡取舍**：在性能、内存、功耗、可维护性之间平衡
4. **持续改进**：优化是一个迭代过程，不断测量和改进

记住：**正确性第一，性能第二**。只有在确保功能正确的前提下，才考虑性能优化。

## 练习题

1. **性能分析**：使用DWT测量你的项目中最常调用的3个函数的执行时间
2. **代码优化**：找一个使用浮点运算的函数，改写为定点运算版本
3. **内存优化**：分析你的项目的内存使用，找出可以优化的地方
4. **功耗优化**：实现一个智能睡眠管理系统，根据系统负载动态调整功耗模式
5. **综合优化**：选择一个实际模块，应用本文的优化技巧，测量优化前后的性能差异

## 参考资料

1. ARM Cortex-M Programming Guide
2. GCC Optimization Options Documentation
3. Embedded Systems Performance Optimization Techniques
4. Power Management in Embedded Systems
5. Real-Time Systems Design and Analysis

---

**下一步学习**：
- 轻量级任务调度器设计
- 裸机程序的实时性分析
- RTOS基础
