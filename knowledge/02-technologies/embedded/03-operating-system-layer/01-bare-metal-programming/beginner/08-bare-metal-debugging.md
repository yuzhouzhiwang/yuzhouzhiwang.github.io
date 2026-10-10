---
title: "裸机程序调试技巧：快速定位和解决问题"
description: "掌握裸机嵌入式系统的调试方法和技巧。通过本文，你将学会使用日志系统、断言机制、性能分析工具，以及如何处理常见的调试问题，提高开发效率和代码质量。"
slug: "bare-metal-debugging"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 调试技巧
  - 日志系统
  - 断言
  - 性能分析
  - 故障排查
prerequisites:
  - "bare-metal-programming-basics"
  - "bare-metal-memory-management"
related_contents: []

# 学习信息
estimated_time: 55
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
  - 裸机调试
  - 嵌入式调试
  - 日志系统
  - 断言机制
  - 性能分析
  - 故障排查
  - JTAG调试
cover_image: ""
---

# 裸机程序调试技巧：快速定位和解决问题

## 概述

调试是嵌入式开发中最具挑战性的环节之一。与桌面应用不同，裸机程序运行在资源受限的硬件上，没有操作系统的支持，调试工具和方法也相对有限。掌握有效的调试技巧，能够大幅提高开发效率，快速定位和解决问题。

通过本文学习，你将能够：

- 理解裸机环境下的调试挑战和方法
- 设计和实现高效的日志系统
- 使用断言机制进行运行时检查
- 掌握硬件调试工具的使用方法
- 进行性能分析和优化
- 识别和解决常见的调试问题

## 背景知识

### 裸机调试的挑战

**与桌面调试的区别**：

| 特性 | 桌面应用 | 裸机程序 |
|------|---------|---------|
| 调试器 | GDB、Visual Studio等 | JTAG/SWD调试器 |
| 输出 | printf到控制台 | 串口、LED、调试器 |
| 断点 | 无限制 | 有限的硬件断点 |
| 内存检查 | 工具丰富 | 手动检查 |
| 崩溃处理 | 操作系统捕获 | 硬件异常 |
| 实时性 | 不重要 | 关键因素 |

**裸机调试的困难**：
1. **资源限制**：RAM和Flash空间有限，调试代码占用资源
2. **实时性要求**：调试不能影响系统的实时性能
3. **硬件依赖**：需要专门的调试硬件（如J-Link、ST-Link）
4. **可见性差**：没有屏幕输出，难以观察程序状态
5. **并发问题**：中断和多任务导致的时序问题难以重现

### 调试方法分类

**1. 静态调试**：
- 代码审查
- 静态分析工具
- 编译器警告

**2. 动态调试**：
- 硬件调试器（JTAG/SWD）
- 日志输出
- LED指示
- 断言检查

**3. 性能分析**：
- 时间测量
- 资源使用监控
- 逻辑分析仪

## 核心内容

### 日志系统设计与实现

日志系统是裸机调试最重要的工具之一。一个好的日志系统应该：
- 开销小，不影响实时性
- 信息丰富，便于问题定位
- 灵活配置，可以按需开关
- 支持多种输出方式

#### 基础日志系统

```c
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

// 日志级别定义
typedef enum {
    LOG_LEVEL_DEBUG = 0,    // 调试信息
    LOG_LEVEL_INFO,         // 一般信息
    LOG_LEVEL_WARNING,      // 警告
    LOG_LEVEL_ERROR,        // 错误
    LOG_LEVEL_CRITICAL      // 严重错误
} LogLevel_t;

// 日志配置
typedef struct {
    LogLevel_t min_level;   // 最小输出级别
    bool timestamp_enabled; // 是否显示时间戳
    bool color_enabled;     // 是否使用颜色（串口终端）
} LogConfig_t;

// 全局日志配置
static LogConfig_t g_log_config = {
    .min_level = LOG_LEVEL_DEBUG,
    .timestamp_enabled = true,
    .color_enabled = false
};

// 日志级别名称
static const char* log_level_names[] = {
    "DEBUG",
    "INFO",
    "WARN",
    "ERROR",
    "CRIT"
};

// ANSI颜色代码（用于支持颜色的终端）
static const char* log_level_colors[] = {
    "\033[0;37m",  // DEBUG - 白色
    "\033[0;32m",  // INFO - 绿色
    "\033[0;33m",  // WARNING - 黄色
    "\033[0;31m",  // ERROR - 红色
    "\033[1;31m"   // CRITICAL - 亮红色
};
static const char* color_reset = "\033[0m";

// 获取系统时间戳（需要实现）
extern uint32_t GetSystemTick(void);

// 串口输出函数（需要实现）
extern void UART_SendString(const char *str);

// 设置日志级别
void Log_SetLevel(LogLevel_t level) {
    g_log_config.min_level = level;
}

// 启用/禁用时间戳
void Log_EnableTimestamp(bool enable) {
    g_log_config.timestamp_enabled = enable;
}

// 启用/禁用颜色
void Log_EnableColor(bool enable) {
    g_log_config.color_enabled = enable;
}

// 核心日志函数
void Log_Print(LogLevel_t level, const char *file, int line, 
               const char *func, const char *fmt, ...) {
    // 检查日志级别
    if(level < g_log_config.min_level) {
        return;
    }
    
    char buffer[256];
    int offset = 0;
    
    // 添加颜色代码
    if(g_log_config.color_enabled) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "%s", log_level_colors[level]);
    }
    
    // 添加时间戳
    if(g_log_config.timestamp_enabled) {
        uint32_t tick = GetSystemTick();
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "[%6lu.%03lu] ", tick / 1000, tick % 1000);
    }
    
    // 添加日志级别
    offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                      "[%s] ", log_level_names[level]);
    
    // 添加文件和行号（仅对ERROR和CRITICAL）
    if(level >= LOG_LEVEL_ERROR) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "%s:%d ", file, line);
    }
    
    // 添加函数名
    offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                      "%s(): ", func);
    
    // 添加用户消息
    va_list args;
    va_start(args, fmt);
    offset += vsnprintf(buffer + offset, sizeof(buffer) - offset, fmt, args);
    va_end(args);
    
    // 添加颜色重置和换行
    if(g_log_config.color_enabled) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "%s", color_reset);
    }
    offset += snprintf(buffer + offset, sizeof(buffer) - offset, "\r\n");
    
    // 输出到串口
    UART_SendString(buffer);
}

// 便捷宏定义
#define LOG_DEBUG(fmt, ...) \
    Log_Print(LOG_LEVEL_DEBUG, __FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_INFO(fmt, ...) \
    Log_Print(LOG_LEVEL_INFO, __FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_WARNING(fmt, ...) \
    Log_Print(LOG_LEVEL_WARNING, __FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_ERROR(fmt, ...) \
    Log_Print(LOG_LEVEL_ERROR, __FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_CRITICAL(fmt, ...) \
    Log_Print(LOG_LEVEL_CRITICAL, __FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

// 使用示例
void Example_LogSystem(void) {
    // 配置日志系统
    Log_SetLevel(LOG_LEVEL_DEBUG);
    Log_EnableTimestamp(true);
    Log_EnableColor(false);
    
    // 输出不同级别的日志
    LOG_DEBUG("System initializing...");
    LOG_INFO("UART configured at 115200 baud");
    LOG_WARNING("Temperature high: %d°C", 75);
    LOG_ERROR("Failed to read sensor, error code: %d", -1);
    LOG_CRITICAL("System halted!");
    
    // 运行时调整日志级别
    Log_SetLevel(LOG_LEVEL_WARNING);  // 只显示WARNING及以上
    LOG_DEBUG("This will not be printed");
    LOG_WARNING("This will be printed");
}
```

**输出示例**：
```
[  1234.567] [DEBUG] Example_LogSystem(): System initializing...
[  1234.568] [INFO] Example_LogSystem(): UART configured at 115200 baud
[  1234.569] [WARN] Example_LogSystem(): Temperature high: 75°C
[  1234.570] [ERROR] main.c:123 Example_LogSystem(): Failed to read sensor, error code: -1
[  1234.571] [CRIT] main.c:124 Example_LogSystem(): System halted!
```


#### 高级日志系统：环形缓冲区

为了减少对实时性的影响，可以使用环形缓冲区异步输出日志：

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 日志缓冲区配置
#define LOG_BUFFER_SIZE 2048
#define LOG_ENTRY_MAX_SIZE 128

// 环形缓冲区
typedef struct {
    char buffer[LOG_BUFFER_SIZE];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
    bool overflow;
} LogRingBuffer_t;

static LogRingBuffer_t g_log_buffer = {0};

// 初始化日志缓冲区
void LogBuffer_Init(void) {
    memset(&g_log_buffer, 0, sizeof(g_log_buffer));
}

// 写入日志到缓冲区（快速，不阻塞）
bool LogBuffer_Write(const char *message) {
    uint32_t len = strlen(message);
    
    // 检查空间
    if(len > LOG_BUFFER_SIZE - g_log_buffer.count) {
        g_log_buffer.overflow = true;
        return false;
    }
    
    // 写入数据
    for(uint32_t i = 0; i < len; i++) {
        g_log_buffer.buffer[g_log_buffer.head] = message[i];
        g_log_buffer.head = (g_log_buffer.head + 1) % LOG_BUFFER_SIZE;
        g_log_buffer.count++;
    }
    
    return true;
}

// 从缓冲区读取并输出（在空闲时调用）
void LogBuffer_Flush(void) {
    while(g_log_buffer.count > 0) {
        // 读取一个字符
        char ch = g_log_buffer.buffer[g_log_buffer.tail];
        g_log_buffer.tail = (g_log_buffer.tail + 1) % LOG_BUFFER_SIZE;
        g_log_buffer.count--;
        
        // 输出到串口
        UART_SendChar(ch);
    }
    
    // 检查溢出
    if(g_log_buffer.overflow) {
        UART_SendString("\r\n[LOG OVERFLOW]\r\n");
        g_log_buffer.overflow = false;
    }
}

// 异步日志函数
void Log_PrintAsync(LogLevel_t level, const char *fmt, ...) {
    if(level < g_log_config.min_level) {
        return;
    }
    
    char buffer[LOG_ENTRY_MAX_SIZE];
    
    // 格式化消息
    va_list args;
    va_start(args, fmt);
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    
    // 写入缓冲区（快速返回）
    LogBuffer_Write(buffer);
}

// 在主循环中定期刷新
void MainLoop(void) {
    while(1) {
        // 处理任务
        DoTasks();
        
        // 刷新日志缓冲区
        LogBuffer_Flush();
    }
}
```

**优点**：
- 日志写入非常快，不阻塞主程序
- 在空闲时才输出，不影响实时性
- 可以记录大量日志信息

**缺点**：
- 需要额外的RAM空间
- 可能丢失日志（缓冲区满时）
- 日志输出有延迟

### 断言机制

断言是一种运行时检查机制，用于验证程序的假设和不变量。

#### 基础断言实现

```c
#include <stdint.h>
#include <stdbool.h>

// 断言配置
#define ASSERT_ENABLED 1  // 1=启用，0=禁用

// 断言失败处理
void Assert_Failed(const char *file, int line, const char *func, 
                   const char *expr) {
    // 禁用中断（防止进一步破坏）
    __disable_irq();
    
    // 输出错误信息
    LOG_CRITICAL("ASSERTION FAILED!");
    LOG_CRITICAL("  File: %s", file);
    LOG_CRITICAL("  Line: %d", line);
    LOG_CRITICAL("  Function: %s", func);
    LOG_CRITICAL("  Expression: %s", expr);
    
    // 刷新日志缓冲区
    LogBuffer_Flush();
    
    // 进入死循环或重启
    while(1) {
        // 可以在这里闪烁LED指示错误
        LED_Toggle();
        Delay_ms(100);
    }
    
    // 或者触发软件复位
    // NVIC_SystemReset();
}

// 断言宏
#if ASSERT_ENABLED
    #define ASSERT(expr) \
        do { \
            if(!(expr)) { \
                Assert_Failed(__FILE__, __LINE__, __func__, #expr); \
            } \
        } while(0)
#else
    #define ASSERT(expr) ((void)0)
#endif

// 带消息的断言
#define ASSERT_MSG(expr, msg) \
    do { \
        if(!(expr)) { \
            LOG_CRITICAL("Assertion failed: %s", msg); \
            Assert_Failed(__FILE__, __LINE__, __func__, #expr); \
        } \
    } while(0)

// 使用示例
void ProcessData(uint8_t *data, uint32_t len) {
    // 检查参数有效性
    ASSERT(data != NULL);
    ASSERT(len > 0);
    ASSERT(len <= MAX_DATA_SIZE);
    
    // 检查状态
    ASSERT_MSG(system_initialized, "System not initialized");
    
    // 处理数据
    for(uint32_t i = 0; i < len; i++) {
        // 检查数组边界
        ASSERT(i < len);
        data[i] = ProcessByte(data[i]);
    }
}

// 常见的断言使用场景
void Example_Assertions(void) {
    // 1. 检查指针
    uint8_t *ptr = GetBuffer();
    ASSERT(ptr != NULL);
    
    // 2. 检查范围
    int value = GetValue();
    ASSERT(value >= 0 && value <= 100);
    
    // 3. 检查状态
    ASSERT(device_ready == true);
    
    // 4. 检查不变量
    ASSERT(queue.count <= queue.capacity);
    
    // 5. 检查返回值
    int result = InitDevice();
    ASSERT(result == 0);
}
```

#### 编译时断言

```c
// 编译时断言（C11标准）
#include <assert.h>

// 检查结构体大小
static_assert(sizeof(PacketHeader_t) == 16, 
              "PacketHeader must be 16 bytes");

// 检查对齐
static_assert(sizeof(DMABuffer_t) % 4 == 0, 
              "DMABuffer must be 4-byte aligned");

// 检查枚举值
static_assert(STATE_MAX < 256, 
              "State must fit in uint8_t");

// 自定义编译时断言（C99兼容）
#define STATIC_ASSERT(expr, msg) \
    typedef char static_assert_##msg[(expr) ? 1 : -1]

// 使用示例
STATIC_ASSERT(sizeof(int) == 4, int_must_be_4_bytes);
STATIC_ASSERT(MAX_BUFFER_SIZE <= 1024, buffer_too_large);
```

### 硬件调试工具

#### JTAG/SWD调试器使用

```c
// 调试器配置（在启动代码中）
void Debug_Init(void) {
    // 启用调试时钟
    RCC->APB2ENR |= RCC_APB2ENR_AFIOEN;
    
    // 配置SWD引脚（PA13=SWDIO, PA14=SWCLK）
    // 通常由启动代码自动配置
    
    // 启用ITM（Instrumentation Trace Macrocell）
    // 用于printf重定向
    ITM_Enable();
}

// ITM输出（通过调试器输出，不占用串口）
void ITM_SendChar(char ch) {
    // 等待ITM端口就绪
    while(ITM->PORT[0].u32 == 0);
    
    // 发送字符
    ITM->PORT[0].u8 = (uint8_t)ch;
}

// 重定向printf到ITM
int _write(int file, char *ptr, int len) {
    for(int i = 0; i < len; i++) {
        ITM_SendChar(ptr[i]);
    }
    return len;
}

// 使用printf输出到调试器
void Example_ITM(void) {
    printf("Hello from ITM!\n");
    printf("Value: %d\n", 42);
}
```

**调试器功能**：
- **断点**：设置代码断点，暂停程序执行
- **单步执行**：逐行执行代码
- **变量查看**：实时查看变量值
- **内存查看**：查看任意内存地址
- **寄存器查看**：查看CPU寄存器
- **实时跟踪**：ITM/ETM跟踪

#### 硬件断点限制

```c
// ARM Cortex-M通常只有4-6个硬件断点
// 需要合理使用

// 示例：在关键位置设置断点
void CriticalFunction(void) {
    // 在调试器中设置断点
    __BKPT(0);  // 软件断点指令
    
    // 关键代码
    ProcessCriticalData();
}

// 条件断点（在调试器中配置）
void ProcessLoop(void) {
    for(int i = 0; i < 1000; i++) {
        // 只在i==500时中断
        // 在调试器中设置条件：i == 500
        ProcessItem(i);
    }
}

// 数据断点（监视变量变化）
volatile uint32_t critical_variable;

void MonitorVariable(void) {
    // 在调试器中设置数据断点
    // 当critical_variable被修改时中断
    critical_variable = 123;
}
```

### 性能分析

#### 时间测量

```c
#include <stdint.h>

// 使用SysTick进行微秒级时间测量
void SysTick_Init(void) {
    // 配置SysTick为1MHz（1us分辨率）
    SysTick->LOAD = (SystemCoreClock / 1000000) - 1;
    SysTick->VAL = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | 
                    SysTick_CTRL_ENABLE_Msk;
}

// 获取微秒时间戳
uint32_t GetMicros(void) {
    static uint32_t overflow_count = 0;
    static uint32_t last_val = 0;
    
    uint32_t current_val = SysTick->VAL;
    
    // 检测溢出
    if(current_val > last_val) {
        overflow_count++;
    }
    last_val = current_val;
    
    return overflow_count * SysTick->LOAD + current_val;
}

// 测量函数执行时间
void MeasureExecutionTime(void) {
    uint32_t start = GetMicros();
    
    // 执行要测量的代码
    ProcessData();
    
    uint32_t end = GetMicros();
    uint32_t elapsed = end - start;
    
    LOG_INFO("Execution time: %lu us", elapsed);
}

// 性能计数器
typedef struct {
    const char *name;
    uint32_t count;
    uint32_t total_time;
    uint32_t min_time;
    uint32_t max_time;
} PerfCounter_t;

#define MAX_PERF_COUNTERS 10
static PerfCounter_t perf_counters[MAX_PERF_COUNTERS];
static uint32_t perf_counter_count = 0;

// 注册性能计数器
PerfCounter_t* PerfCounter_Register(const char *name) {
    if(perf_counter_count >= MAX_PERF_COUNTERS) {
        return NULL;
    }
    
    PerfCounter_t *counter = &perf_counters[perf_counter_count++];
    counter->name = name;
    counter->count = 0;
    counter->total_time = 0;
    counter->min_time = UINT32_MAX;
    counter->max_time = 0;
    
    return counter;
}

// 开始测量
uint32_t PerfCounter_Start(void) {
    return GetMicros();
}

// 结束测量
void PerfCounter_End(PerfCounter_t *counter, uint32_t start_time) {
    uint32_t elapsed = GetMicros() - start_time;
    
    counter->count++;
    counter->total_time += elapsed;
    
    if(elapsed < counter->min_time) {
        counter->min_time = elapsed;
    }
    if(elapsed > counter->max_time) {
        counter->max_time = elapsed;
    }
}

// 打印性能报告
void PerfCounter_PrintReport(void) {
    LOG_INFO("=== Performance Report ===");
    
    for(uint32_t i = 0; i < perf_counter_count; i++) {
        PerfCounter_t *c = &perf_counters[i];
        uint32_t avg = c->total_time / c->count;
        
        LOG_INFO("%s:", c->name);
        LOG_INFO("  Count: %lu", c->count);
        LOG_INFO("  Total: %lu us", c->total_time);
        LOG_INFO("  Avg: %lu us", avg);
        LOG_INFO("  Min: %lu us", c->min_time);
        LOG_INFO("  Max: %lu us", c->max_time);
    }
}

// 使用示例
PerfCounter_t *sensor_counter;
PerfCounter_t *comm_counter;

void Example_Performance(void) {
    // 注册计数器
    sensor_counter = PerfCounter_Register("Sensor Read");
    comm_counter = PerfCounter_Register("Communication");
    
    // 测量传感器读取
    uint32_t start = PerfCounter_Start();
    ReadSensor();
    PerfCounter_End(sensor_counter, start);
    
    // 测量通信
    start = PerfCounter_Start();
    SendData();
    PerfCounter_End(comm_counter, start);
    
    // 定期打印报告
    static uint32_t last_report = 0;
    if(GetSystemTick() - last_report > 10000) {
        PerfCounter_PrintReport();
        last_report = GetSystemTick();
    }
}
```


#### CPU使用率监控

```c
#include <stdint.h>
#include <stdbool.h>

// CPU使用率监控
typedef struct {
    uint32_t idle_count;
    uint32_t total_count;
    uint32_t last_update;
    uint8_t cpu_usage;
} CPUMonitor_t;

static CPUMonitor_t g_cpu_monitor = {0};

// 初始化CPU监控
void CPUMonitor_Init(void) {
    g_cpu_monitor.idle_count = 0;
    g_cpu_monitor.total_count = 0;
    g_cpu_monitor.last_update = GetSystemTick();
    g_cpu_monitor.cpu_usage = 0;
}

// 在空闲任务中调用
void CPUMonitor_IdleTask(void) {
    g_cpu_monitor.idle_count++;
    g_cpu_monitor.total_count++;
}

// 在其他任务中调用
void CPUMonitor_BusyTask(void) {
    g_cpu_monitor.total_count++;
}

// 计算CPU使用率
void CPUMonitor_Update(void) {
    uint32_t now = GetSystemTick();
    
    // 每秒更新一次
    if(now - g_cpu_monitor.last_update >= 1000) {
        // 计算使用率
        uint32_t idle_percent = (g_cpu_monitor.idle_count * 100) / 
                                g_cpu_monitor.total_count;
        g_cpu_monitor.cpu_usage = 100 - idle_percent;
        
        LOG_INFO("CPU Usage: %u%%", g_cpu_monitor.cpu_usage);
        
        // 重置计数器
        g_cpu_monitor.idle_count = 0;
        g_cpu_monitor.total_count = 0;
        g_cpu_monitor.last_update = now;
    }
}

// 获取CPU使用率
uint8_t CPUMonitor_GetUsage(void) {
    return g_cpu_monitor.cpu_usage;
}
```

### 常见问题调试

#### 问题1：程序不运行或立即崩溃

```c
// 调试步骤：

// 1. 检查启动代码
void CheckStartup(void) {
    // 验证栈指针
    uint32_t sp;
    __asm volatile ("MRS %0, MSP" : "=r" (sp));
    LOG_INFO("Stack Pointer: 0x%08lX", sp);
    
    // 验证向量表
    uint32_t vtor = SCB->VTOR;
    LOG_INFO("Vector Table: 0x%08lX", vtor);
    
    // 验证时钟配置
    uint32_t sysclk = SystemCoreClock;
    LOG_INFO("System Clock: %lu Hz", sysclk);
}

// 2. 检查内存配置
void CheckMemory(void) {
    // 检查栈是否溢出
    extern uint32_t _estack;
    extern uint32_t _sstack;
    uint32_t stack_size = (uint32_t)&_estack - (uint32_t)&_sstack;
    LOG_INFO("Stack size: %lu bytes", stack_size);
    
    // 检查堆配置
    extern uint32_t _heap_start;
    extern uint32_t _heap_end;
    uint32_t heap_size = (uint32_t)&_heap_end - (uint32_t)&_heap_start;
    LOG_INFO("Heap size: %lu bytes", heap_size);
}

// 3. 添加早期调试输出
void EarlyDebug(void) {
    // 在main()开始就输出
    UART_Init();
    LOG_INFO("=== System Starting ===");
    LOG_INFO("Build: %s %s", __DATE__, __TIME__);
    
    // 逐步初始化，每步输出
    LOG_INFO("Initializing clocks...");
    Clock_Init();
    LOG_INFO("Clock init OK");
    
    LOG_INFO("Initializing GPIO...");
    GPIO_Init();
    LOG_INFO("GPIO init OK");
}
```

#### 问题2：程序运行一段时间后崩溃

```c
// 可能原因：栈溢出、内存泄漏、野指针

// 1. 监控栈使用
void MonitorStack(void) {
    static uint32_t peak_usage = 0;
    uint32_t current = Stack_GetUsage();
    
    if(current > peak_usage) {
        peak_usage = current;
        LOG_WARNING("Stack peak: %lu bytes", peak_usage);
        
        // 栈使用超过80%时警告
        if(peak_usage > STACK_SIZE * 80 / 100) {
            LOG_ERROR("Stack usage critical!");
        }
    }
}

// 2. 监控内存分配
void MonitorMemory(void) {
    static uint32_t last_check = 0;
    uint32_t now = GetSystemTick();
    
    if(now - last_check > 5000) {
        Memory_GetStats();
        last_check = now;
    }
}

// 3. 添加看门狗
void Watchdog_Init(void) {
    // 配置独立看门狗（IWDG）
    IWDG->KR = 0x5555;  // 允许写入
    IWDG->PR = 4;       // 预分频器
    IWDG->RLR = 4095;   // 重载值（约1秒）
    IWDG->KR = 0xCCCC;  // 启动看门狗
}

void Watchdog_Feed(void) {
    IWDG->KR = 0xAAAA;  // 喂狗
}

// 在主循环中定期喂狗
void MainLoop(void) {
    while(1) {
        DoTasks();
        
        // 喂狗
        Watchdog_Feed();
        
        // 如果程序卡死，看门狗会复位系统
    }
}
```

#### 问题3：中断相关问题

```c
// 调试中断问题

// 1. 中断计数器
typedef struct {
    uint32_t count;
    uint32_t max_duration;
    uint32_t total_duration;
} IRQStats_t;

static IRQStats_t irq_stats[16];  // 支持16个中断

// 在中断处理函数中
void USART1_IRQHandler(void) {
    uint32_t start = GetMicros();
    
    // 中断处理代码
    HandleUART();
    
    uint32_t duration = GetMicros() - start;
    
    // 更新统计
    irq_stats[USART1_IRQn].count++;
    irq_stats[USART1_IRQn].total_duration += duration;
    if(duration > irq_stats[USART1_IRQn].max_duration) {
        irq_stats[USART1_IRQn].max_duration = duration;
    }
}

// 打印中断统计
void PrintIRQStats(void) {
    LOG_INFO("=== IRQ Statistics ===");
    for(int i = 0; i < 16; i++) {
        if(irq_stats[i].count > 0) {
            uint32_t avg = irq_stats[i].total_duration / irq_stats[i].count;
            LOG_INFO("IRQ %d: count=%lu, avg=%lu us, max=%lu us",
                    i, irq_stats[i].count, avg, irq_stats[i].max_duration);
        }
    }
}

// 2. 检测中断嵌套
volatile uint32_t irq_nesting_level = 0;
volatile uint32_t max_irq_nesting = 0;

void IRQ_Enter(void) {
    irq_nesting_level++;
    if(irq_nesting_level > max_irq_nesting) {
        max_irq_nesting = irq_nesting_level;
        LOG_WARNING("Max IRQ nesting: %lu", max_irq_nesting);
    }
}

void IRQ_Exit(void) {
    irq_nesting_level--;
}

// 3. 检测中断风暴
#define IRQ_STORM_THRESHOLD 1000  // 每秒1000次

typedef struct {
    uint32_t count;
    uint32_t last_check;
    bool storm_detected;
} IRQStormDetector_t;

static IRQStormDetector_t storm_detector = {0};

void IRQ_CheckStorm(void) {
    storm_detector.count++;
    
    uint32_t now = GetSystemTick();
    if(now - storm_detector.last_check >= 1000) {
        if(storm_detector.count > IRQ_STORM_THRESHOLD) {
            LOG_ERROR("IRQ storm detected! %lu interrupts/sec", 
                     storm_detector.count);
            storm_detector.storm_detected = true;
        }
        
        storm_detector.count = 0;
        storm_detector.last_check = now;
    }
}
```

#### 问题4：时序问题

```c
// 调试时序相关问题

// 1. 使用GPIO输出时序标记
#define DEBUG_PIN_SET()   GPIOA->BSRR = GPIO_PIN_0
#define DEBUG_PIN_CLEAR() GPIOA->BSRR = (GPIO_PIN_0 << 16)
#define DEBUG_PIN_TOGGLE() GPIOA->ODR ^= GPIO_PIN_0

void TimingCriticalFunction(void) {
    DEBUG_PIN_SET();      // 标记开始
    
    // 关键代码
    ProcessData();
    
    DEBUG_PIN_CLEAR();    // 标记结束
    
    // 使用逻辑分析仪或示波器测量脉冲宽度
}

// 2. 记录事件时间戳
#define MAX_EVENTS 100

typedef struct {
    uint32_t timestamp;
    uint8_t event_id;
    uint32_t data;
} EventRecord_t;

static EventRecord_t event_log[MAX_EVENTS];
static uint32_t event_index = 0;

void LogEvent(uint8_t event_id, uint32_t data) {
    if(event_index < MAX_EVENTS) {
        event_log[event_index].timestamp = GetMicros();
        event_log[event_index].event_id = event_id;
        event_log[event_index].data = data;
        event_index++;
    }
}

void PrintEventLog(void) {
    LOG_INFO("=== Event Log ===");
    for(uint32_t i = 0; i < event_index; i++) {
        LOG_INFO("[%lu us] Event %u: 0x%08lX",
                event_log[i].timestamp,
                event_log[i].event_id,
                event_log[i].data);
    }
}

// 使用示例
#define EVENT_SENSOR_READ  1
#define EVENT_DATA_READY   2
#define EVENT_SEND_START   3
#define EVENT_SEND_DONE    4

void Example_EventLog(void) {
    LogEvent(EVENT_SENSOR_READ, 0);
    ReadSensor();
    
    LogEvent(EVENT_DATA_READY, sensor_value);
    
    LogEvent(EVENT_SEND_START, 0);
    SendData();
    LogEvent(EVENT_SEND_DONE, 0);
    
    // 分析事件时序
    PrintEventLog();
}
```

## 实践示例

### 示例1：完整的调试系统

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// ==================== 调试系统配置 ====================

#define DEBUG_ENABLED 1
#define LOG_ENABLED 1
#define ASSERT_ENABLED 1
#define PERF_ENABLED 1

// ==================== 调试系统初始化 ====================

void Debug_SystemInit(void) {
    // 初始化串口（用于日志输出）
    UART_Init(115200);
    
    // 初始化日志系统
    Log_SetLevel(LOG_LEVEL_DEBUG);
    Log_EnableTimestamp(true);
    LogBuffer_Init();
    
    // 初始化性能监控
    CPUMonitor_Init();
    
    // 初始化栈监控
    Stack_Monitor_Init();
    
    // 输出启动信息
    LOG_INFO("=== Debug System Initialized ===");
    LOG_INFO("Build: %s %s", __DATE__, __TIME__);
    LOG_INFO("System Clock: %lu Hz", SystemCoreClock);
    LOG_INFO("Debug: %s", DEBUG_ENABLED ? "ON" : "OFF");
    LOG_INFO("Logging: %s", LOG_ENABLED ? "ON" : "OFF");
    LOG_INFO("Assertions: %s", ASSERT_ENABLED ? "ON" : "OFF");
}

// ==================== 调试任务 ====================

void Debug_Task(void) {
    static uint32_t last_update = 0;
    uint32_t now = GetSystemTick();
    
    // 每秒执行一次
    if(now - last_update >= 1000) {
        last_update = now;
        
        // 1. 检查栈使用
        uint32_t stack_usage = Stack_GetUsage();
        uint32_t stack_percent = Stack_GetUsagePercent();
        if(stack_percent > 75) {
            LOG_WARNING("Stack usage high: %lu%%", stack_percent);
        }
        
        // 2. 检查内存使用
        Memory_GetStats();
        
        // 3. 更新CPU使用率
        CPUMonitor_Update();
        
        // 4. 检查中断统计
        if(max_irq_nesting > 3) {
            LOG_WARNING("Deep IRQ nesting: %lu", max_irq_nesting);
        }
        
        // 5. 刷新日志缓冲区
        LogBuffer_Flush();
    }
}

// ==================== 应用示例 ====================

// 传感器读取任务
void SensorTask(void) {
    static PerfCounter_t *perf_counter = NULL;
    
    // 注册性能计数器
    if(perf_counter == NULL) {
        perf_counter = PerfCounter_Register("SensorTask");
    }
    
    // 开始测量
    uint32_t start = PerfCounter_Start();
    
    // 读取传感器
    LOG_DEBUG("Reading sensor...");
    int16_t temperature = ReadTemperatureSensor();
    
    // 检查有效性
    ASSERT(temperature >= -40 && temperature <= 125);
    
    if(temperature > 80) {
        LOG_WARNING("High temperature: %d°C", temperature);
    } else {
        LOG_INFO("Temperature: %d°C", temperature);
    }
    
    // 结束测量
    PerfCounter_End(perf_counter, start);
}

// 通信任务
void CommTask(void) {
    static PerfCounter_t *perf_counter = NULL;
    
    if(perf_counter == NULL) {
        perf_counter = PerfCounter_Register("CommTask");
    }
    
    uint32_t start = PerfCounter_Start();
    
    // 发送数据
    LOG_DEBUG("Sending data...");
    bool result = SendDataPacket();
    
    if(!result) {
        LOG_ERROR("Failed to send data");
    } else {
        LOG_INFO("Data sent successfully");
    }
    
    PerfCounter_End(perf_counter, start);
}

// 主程序
int main(void) {
    // 系统初始化
    SystemInit();
    
    // 调试系统初始化
    Debug_SystemInit();
    
    LOG_INFO("Application starting...");
    
    // 主循环
    while(1) {
        // 执行任务
        SensorTask();
        CommTask();
        
        // 调试任务
        Debug_Task();
        
        // 喂狗
        Watchdog_Feed();
        
        // 延时
        Delay_ms(100);
    }
}
```


### 示例2：硬件故障（HardFault）处理

```c
#include <stdint.h>

// HardFault寄存器结构
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
} HardFaultStack_t;

// HardFault处理函数
void HardFault_Handler(void) {
    // 获取栈指针
    uint32_t *stack_ptr;
    __asm volatile (
        "TST LR, #4 \n"
        "ITE EQ \n"
        "MRSEQ %0, MSP \n"
        "MRSNE %0, PSP \n"
        : "=r" (stack_ptr)
    );
    
    // 解析栈帧
    HardFaultStack_t *stack = (HardFaultStack_t*)stack_ptr;
    
    // 禁用中断
    __disable_irq();
    
    // 输出错误信息
    LOG_CRITICAL("=== HARD FAULT ===");
    LOG_CRITICAL("R0  = 0x%08lX", stack->r0);
    LOG_CRITICAL("R1  = 0x%08lX", stack->r1);
    LOG_CRITICAL("R2  = 0x%08lX", stack->r2);
    LOG_CRITICAL("R3  = 0x%08lX", stack->r3);
    LOG_CRITICAL("R12 = 0x%08lX", stack->r12);
    LOG_CRITICAL("LR  = 0x%08lX", stack->lr);
    LOG_CRITICAL("PC  = 0x%08lX", stack->pc);
    LOG_CRITICAL("PSR = 0x%08lX", stack->psr);
    
    // 读取故障状态寄存器
    uint32_t cfsr = SCB->CFSR;
    uint32_t hfsr = SCB->HFSR;
    uint32_t dfsr = SCB->DFSR;
    uint32_t afsr = SCB->AFSR;
    uint32_t bfar = SCB->BFAR;
    uint32_t mmar = SCB->MMFAR;
    
    LOG_CRITICAL("CFSR = 0x%08lX", cfsr);
    LOG_CRITICAL("HFSR = 0x%08lX", hfsr);
    LOG_CRITICAL("DFSR = 0x%08lX", dfsr);
    LOG_CRITICAL("AFSR = 0x%08lX", afsr);
    
    // 分析故障原因
    if(cfsr & 0x0080) {  // MMARVALID
        LOG_CRITICAL("Memory Management Fault at 0x%08lX", mmar);
    }
    if(cfsr & 0x8000) {  // BFARVALID
        LOG_CRITICAL("Bus Fault at 0x%08lX", bfar);
    }
    if(cfsr & 0x02000000) {  // DIVBYZERO
        LOG_CRITICAL("Division by zero");
    }
    if(cfsr & 0x01000000) {  // UNALIGNED
        LOG_CRITICAL("Unaligned access");
    }
    if(cfsr & 0x00010000) {  // UNDEFINSTR
        LOG_CRITICAL("Undefined instruction");
    }
    
    // 刷新日志
    LogBuffer_Flush();
    
    // 闪烁LED指示错误
    while(1) {
        LED_Toggle();
        for(volatile int i = 0; i < 1000000; i++);
    }
}

// 使用示例：故意触发HardFault
void Example_TriggerHardFault(void) {
    // 1. 除零错误
    // volatile int x = 1;
    // volatile int y = 0;
    // volatile int z = x / y;  // 触发HardFault
    
    // 2. 非法内存访问
    // volatile uint32_t *ptr = (uint32_t*)0xFFFFFFFF;
    // *ptr = 0x12345678;  // 触发HardFault
    
    // 3. 未对齐访问
    // uint8_t buffer[10];
    // volatile uint32_t *ptr = (uint32_t*)(buffer + 1);
    // *ptr = 0x12345678;  // 可能触发HardFault
}
```

### 示例3：内存转储工具

```c
#include <stdint.h>
#include <stdio.h>

// 内存转储函数
void MemoryDump(const void *addr, uint32_t len) {
    const uint8_t *ptr = (const uint8_t*)addr;
    
    LOG_INFO("Memory dump at 0x%08lX, %lu bytes:", (uint32_t)addr, len);
    
    for(uint32_t i = 0; i < len; i += 16) {
        // 打印地址
        printf("%08lX: ", (uint32_t)(ptr + i));
        
        // 打印十六进制
        for(uint32_t j = 0; j < 16 && (i + j) < len; j++) {
            printf("%02X ", ptr[i + j]);
        }
        
        // 填充空格
        for(uint32_t j = len - i; j < 16; j++) {
            printf("   ");
        }
        
        // 打印ASCII
        printf(" |");
        for(uint32_t j = 0; j < 16 && (i + j) < len; j++) {
            uint8_t ch = ptr[i + j];
            if(ch >= 32 && ch <= 126) {
                printf("%c", ch);
            } else {
                printf(".");
            }
        }
        printf("|\r\n");
    }
}

// 寄存器转储
void RegisterDump(void) {
    uint32_t r0, r1, r2, r3, r12, lr, pc, psr;
    uint32_t msp, psp, primask, control;
    
    __asm volatile (
        "MOV %0, R0 \n"
        "MOV %1, R1 \n"
        "MOV %2, R2 \n"
        "MOV %3, R3 \n"
        "MOV %4, R12 \n"
        "MOV %5, LR \n"
        "MOV %6, PC \n"
        "MRS %7, PSR \n"
        : "=r"(r0), "=r"(r1), "=r"(r2), "=r"(r3),
          "=r"(r12), "=r"(lr), "=r"(pc), "=r"(psr)
    );
    
    __asm volatile (
        "MRS %0, MSP \n"
        "MRS %1, PSP \n"
        "MRS %2, PRIMASK \n"
        "MRS %3, CONTROL \n"
        : "=r"(msp), "=r"(psp), "=r"(primask), "=r"(control)
    );
    
    LOG_INFO("=== Register Dump ===");
    LOG_INFO("R0  = 0x%08lX  R1  = 0x%08lX", r0, r1);
    LOG_INFO("R2  = 0x%08lX  R3  = 0x%08lX", r2, r3);
    LOG_INFO("R12 = 0x%08lX  LR  = 0x%08lX", r12, lr);
    LOG_INFO("PC  = 0x%08lX  PSR = 0x%08lX", pc, psr);
    LOG_INFO("MSP = 0x%08lX  PSP = 0x%08lX", msp, psp);
    LOG_INFO("PRIMASK = 0x%08lX  CONTROL = 0x%08lX", primask, control);
}

// 使用示例
void Example_MemoryDump(void) {
    // 转储变量
    uint32_t test_var = 0x12345678;
    MemoryDump(&test_var, sizeof(test_var));
    
    // 转储数组
    uint8_t test_array[] = "Hello, World!";
    MemoryDump(test_array, sizeof(test_array));
    
    // 转储栈
    uint8_t stack_buffer[64];
    MemoryDump(stack_buffer, sizeof(stack_buffer));
    
    // 转储寄存器
    RegisterDump();
}
```

## 深入理解

### 调试优化代码

编译器优化可能会影响调试体验：

```c
// 问题：优化后变量被优化掉
void OptimizedFunction(void) {
    int temp = CalculateValue();  // 可能被优化掉
    ProcessValue(temp);
}

// 解决方案1：使用volatile
void BetterFunction(void) {
    volatile int temp = CalculateValue();  // 不会被优化
    ProcessValue(temp);
}

// 解决方案2：禁用函数优化
__attribute__((optimize("O0")))
void DebugFunction(void) {
    int temp = CalculateValue();  // 保留所有变量
    ProcessValue(temp);
}

// 解决方案3：使用调试构建
#ifdef DEBUG
    #define OPTIMIZE_ATTR __attribute__((optimize("O0")))
#else
    #define OPTIMIZE_ATTR
#endif

OPTIMIZE_ATTR
void MyFunction(void) {
    // 调试版本不优化，发布版本优化
}
```

### 实时系统调试注意事项

```c
// 问题：调试输出影响时序
void TimingSensitiveFunction(void) {
    // 不好：日志输出很慢
    LOG_DEBUG("Processing...");
    ProcessData();  // 时序被破坏
}

// 解决方案1：使用异步日志
void BetterFunction(void) {
    Log_PrintAsync(LOG_LEVEL_DEBUG, "Processing...");
    ProcessData();  // 时序不受影响
}

// 解决方案2：使用GPIO标记
void BestFunction(void) {
    DEBUG_PIN_SET();
    ProcessData();
    DEBUG_PIN_CLEAR();
    // 使用逻辑分析仪观察，不影响时序
}

// 解决方案3：条件编译
void ConditionalDebug(void) {
    #ifdef VERBOSE_DEBUG
        LOG_DEBUG("Processing...");
    #endif
    ProcessData();
}
```

### 多线程/中断调试

```c
// 问题：竞态条件难以重现
volatile uint32_t shared_counter = 0;

void Task1(void) {
    shared_counter++;  // 非原子操作
}

void Task2(void) {
    shared_counter++;  // 可能产生竞态
}

// 解决方案1：添加调试代码检测竞态
void Task1_Debug(void) {
    uint32_t old_value = shared_counter;
    shared_counter++;
    
    // 检查是否被其他任务修改
    if(shared_counter != old_value + 1) {
        LOG_ERROR("Race condition detected!");
    }
}

// 解决方案2：使用原子操作
void Task1_Safe(void) {
    __atomic_fetch_add(&shared_counter, 1, __ATOMIC_SEQ_CST);
}

// 解决方案3：使用互斥保护
void Task1_Protected(void) {
    __disable_irq();
    shared_counter++;
    __enable_irq();
}
```

### 调试工具链

**常用工具**：

1. **GDB（GNU Debugger）**
   - 命令行调试器
   - 支持远程调试
   - 脚本化调试

2. **OpenOCD**
   - 开源片上调试器
   - 支持多种调试器硬件
   - 与GDB配合使用

3. **J-Link**
   - 商业调试器
   - 性能优秀
   - RTT（Real-Time Transfer）功能

4. **ST-Link**
   - STM32官方调试器
   - 价格便宜
   - 功能完善

**调试器配置示例**：

```bash
# OpenOCD配置文件
# openocd.cfg

source [find interface/stlink.cfg]
source [find target/stm32f4x.cfg]

# 启动OpenOCD
openocd -f openocd.cfg

# GDB连接
arm-none-eabi-gdb firmware.elf
(gdb) target remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) continue
```

## 常见问题

### Q1: 如何在没有调试器的情况下调试？

**A**: 可以使用以下方法：

```c
// 1. LED闪烁模式
void DebugWithLED(uint8_t code) {
    for(int i = 0; i < code; i++) {
        LED_On();
        Delay_ms(200);
        LED_Off();
        Delay_ms(200);
    }
    Delay_ms(1000);
}

// 使用示例
void MyFunction(void) {
    DebugWithLED(1);  // 到达点1
    
    if(condition) {
        DebugWithLED(2);  // 到达点2
    } else {
        DebugWithLED(3);  // 到达点3
    }
}

// 2. 串口输出
void DebugWithUART(const char *msg) {
    UART_SendString(msg);
    UART_SendString("\r\n");
}

// 3. 保存到Flash
void SaveDebugInfo(void) {
    // 将调试信息写入Flash
    // 重启后读取
}
```

### Q2: 如何调试优化后的代码？

**A**: 几种策略：

```c
// 1. 选择性禁用优化
#pragma GCC push_options
#pragma GCC optimize ("O0")

void DebugThisFunction(void) {
    // 这个函数不优化
}

#pragma GCC pop_options

// 2. 使用volatile防止优化
void CheckValue(void) {
    volatile int value = GetValue();
    // value不会被优化掉
    if(value < 0) {
        HandleError();
    }
}

// 3. 使用内联汇编
void ForceKeepValue(int value) {
    __asm volatile ("" : : "r"(value) : "memory");
    // 编译器认为value被使用
}
```

### Q3: 如何定位内存泄漏？

**A**: 使用内存跟踪：

```c
// 1. 包装分配函数
#define malloc(size) malloc_debug(size, __FILE__, __LINE__)
#define free(ptr) free_debug(ptr)

void* malloc_debug(size_t size, const char *file, int line) {
    void *ptr = malloc(size);
    if(ptr) {
        Memory_RecordAlloc(ptr, size, file, line);
    }
    return ptr;
}

void free_debug(void *ptr) {
    Memory_RecordFree(ptr);
    free(ptr);
}

// 2. 定期检查
void CheckMemoryLeaks(void) {
    Memory_CheckLeaks();
}

// 3. 使用内存池
// 内存池可以轻松跟踪所有分配
```

### Q4: 如何调试间歇性问题？

**A**: 使用事件记录：

```c
// 1. 记录所有关键事件
#define LOG_EVENT(id, data) LogEvent(id, data)

void ProblematicFunction(void) {
    LOG_EVENT(EVENT_ENTER, 0);
    
    if(condition1) {
        LOG_EVENT(EVENT_COND1, value1);
    }
    
    if(condition2) {
        LOG_EVENT(EVENT_COND2, value2);
    }
    
    LOG_EVENT(EVENT_EXIT, result);
}

// 2. 问题发生时分析事件序列
void AnalyzeEvents(void) {
    PrintEventLog();
    // 查找异常的事件序列
}

// 3. 使用断言捕获异常状态
ASSERT(value >= 0);
ASSERT(pointer != NULL);
```

### Q5: 日志输出太多怎么办？

**A**: 使用分级和过滤：

```c
// 1. 按模块分级
#define LOG_MODULE_SENSOR  LOG_LEVEL_INFO
#define LOG_MODULE_COMM    LOG_LEVEL_WARNING
#define LOG_MODULE_STORAGE LOG_LEVEL_ERROR

void SensorTask(void) {
    if(LOG_LEVEL_DEBUG >= LOG_MODULE_SENSOR) {
        LOG_DEBUG("Sensor reading...");
    }
}

// 2. 运行时调整
void SetModuleLogLevel(uint8_t module, LogLevel_t level) {
    module_log_levels[module] = level;
}

// 3. 使用日志过滤
void Log_SetFilter(const char *filter) {
    // 只输出包含特定字符串的日志
    log_filter = filter;
}
```

## 总结

裸机程序调试需要掌握多种技术和工具。本文介绍的关键要点：

**调试方法**：
- 设计高效的日志系统，支持分级和异步输出
- 使用断言机制进行运行时检查
- 掌握硬件调试器的使用方法
- 进行性能分析和优化

**调试技巧**：
- 使用GPIO输出时序标记
- 记录事件时间戳分析时序
- 监控栈和内存使用情况
- 实现HardFault处理和分析

**最佳实践**：
- 在开发早期就集成调试系统
- 使用条件编译控制调试代码
- 定期检查系统状态和资源使用
- 保留调试日志用于问题分析

**工具使用**：
- 熟悉JTAG/SWD调试器
- 使用逻辑分析仪分析时序
- 掌握GDB和OpenOCD
- 利用IDE的调试功能

掌握这些调试技巧，你就能快速定位和解决裸机程序中的各种问题，提高开发效率和代码质量。

## 延伸阅读

推荐进一步学习的资源：

- [裸机程序的内存管理](bare-metal-memory-management) - 内存相关问题调试
- [协作式多任务调度器实现](cooperative-scheduler) - 多任务调试
- [RTOS调试技巧](rtos-debugging) - 操作系统级调试
- [ARM Cortex-M调试指南](https://developer.arm.com/) - 官方调试文档

## 参考资料

1. ARM Cortex-M Programming Guide - ARM官方编程指南
2. "Debugging Embedded Systems" by Chris Hobbs - 嵌入式调试专著
3. "The Definitive Guide to ARM Cortex-M3/M4" by Joseph Yiu - Cortex-M权威指南
4. GDB User Manual - GDB官方文档
5. OpenOCD User's Guide - OpenOCD使用指南

---

**练习题**：

1. 实现一个完整的日志系统，支持多级别、时间戳和异步输出
2. 编写一个HardFault处理函数，能够详细分析故障原因并输出寄存器状态
3. 设计一个性能分析系统，能够测量函数执行时间和CPU使用率
4. 实现一个内存泄漏检测工具，跟踪所有内存分配和释放
5. 创建一个事件记录系统，用于分析间歇性时序问题

**下一步**：建议学习 [协作式多任务调度器实现](cooperative-scheduler)，了解如何在裸机环境中实现多任务。
