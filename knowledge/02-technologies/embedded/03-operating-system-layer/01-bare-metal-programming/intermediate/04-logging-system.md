---
title: "日志系统设计与实现：构建专业的调试工具"
description: "深入学习嵌入式系统日志系统的设计与实现方法。掌握日志级别管理、格式化输出、缓冲机制、存储策略和性能优化等核心技术，学会构建高效可靠的日志系统。"
slug: "logging-system-implementation"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 日志系统
  - 调试工具
  - 系统监控
  - 格式化输出
  - 缓冲机制
  - 性能优化
prerequisites:
  - "beginner/01-bare-metal-basics.md"
  - "beginner/02-super-loop.md"
  - "beginner/06-ring-buffer.md"
related_contents:
  - "intermediate/03-cli-implementation.md"
  - "beginner/08-bare-metal-debugging.md"

# 学习信息
estimated_time: 70
difficulty_score: 6

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
  - 日志系统
  - Logging System
  - 嵌入式调试
  - 日志级别
  - 格式化输出
  - 环形缓冲区
cover_image: ""
---

# 日志系统设计与实现：构建专业的调试工具

## 概述

日志系统（Logging System）是嵌入式系统开发和调试中不可或缺的工具。一个设计良好的日志系统可以帮助开发者快速定位问题、监控系统运行状态、记录关键事件，并为系统优化提供数据支持。

完成本教程学习后，你将能够：

- 理解日志系统的架构设计原理
- 掌握日志级别的定义和使用方法
- 实现高效的格式化输出功能
- 设计可靠的缓冲和存储机制
- 优化日志系统的性能和资源占用
- 构建适合生产环境的日志系统

## 背景知识

### 什么是日志系统？

**日志系统（Logging System）**是一套用于记录程序运行时信息的软件组件，它可以输出调试信息、警告、错误等不同级别的消息，帮助开发者了解程序的运行状态。

**典型应用场景**：
- **开发调试**：输出变量值、函数调用、执行流程
- **问题诊断**：记录错误信息、异常状态、故障现场
- **性能分析**：记录时间戳、执行时间、资源使用
- **系统监控**：记录系统状态、传感器数据、通信日志
- **审计追踪**：记录用户操作、配置变更、安全事件

### 为什么需要日志系统？

在嵌入式开发中，传统的printf调试存在诸多问题：

**传统printf的局限性**：
- 无法控制输出级别（全部输出或全部关闭）
- 输出格式不统一，难以解析
- 缺少时间戳和上下文信息
- 性能开销大，影响实时性
- 无法持久化存储
- 难以在生产环境使用

**专业日志系统的优势**：
- 分级输出，灵活控制详细程度
- 统一格式，便于解析和分析
- 包含时间戳、模块名、级别等元信息
- 支持缓冲，减少性能影响
- 支持多种输出方式（串口、文件、网络）
- 可在生产环境安全使用


### 日志系统架构

一个完整的日志系统包含以下核心组件：

```
┌─────────────────────────────────────────┐
│        应用层（Application）             │
│    LOG_DEBUG(), LOG_INFO(), LOG_ERROR() │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       日志接口层（Log API）              │
│    级别过滤、格式化、时间戳添加          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       缓冲层（Buffer Layer）             │
│    环形缓冲区、异步处理、流量控制        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       输出层（Output Layer）             │
│    串口、文件、网络、多路输出            │
└─────────────────────────────────────────┘
```

## 核心内容

### 日志级别设计

日志级别是日志系统的核心概念，用于区分不同重要程度的消息。

#### 标准日志级别

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

// 日志级别定义
typedef enum {
    LOG_LEVEL_TRACE = 0,    // 追踪：最详细的信息，用于跟踪程序执行流程
    LOG_LEVEL_DEBUG = 1,    // 调试：调试信息，开发阶段使用
    LOG_LEVEL_INFO  = 2,    // 信息：一般信息，记录正常运行状态
    LOG_LEVEL_WARN  = 3,    // 警告：警告信息，可能存在问题但不影响运行
    LOG_LEVEL_ERROR = 4,    // 错误：错误信息，功能异常但系统可继续运行
    LOG_LEVEL_FATAL = 5,    // 致命：严重错误，系统无法继续运行
    LOG_LEVEL_NONE  = 6     // 关闭：不输出任何日志
} LogLevel_t;

// 日志级别名称
static const char *log_level_names[] = {
    "TRACE",
    "DEBUG",
    "INFO ",
    "WARN ",
    "ERROR",
    "FATAL"
};

// 日志级别颜色（ANSI转义码）
static const char *log_level_colors[] = {
    "\033[37m",  // TRACE - 白色
    "\033[36m",  // DEBUG - 青色
    "\033[32m",  // INFO  - 绿色
    "\033[33m",  // WARN  - 黄色
    "\033[31m",  // ERROR - 红色
    "\033[35m"   // FATAL - 紫色
};

#define COLOR_RESET "\033[0m"
```

**级别使用指南**：
- **TRACE**: 函数进入/退出、循环迭代、详细的执行流程
- **DEBUG**: 变量值、中间结果、调试信息
- **INFO**: 系统启动、配置加载、正常操作完成
- **WARN**: 配置缺失、使用默认值、性能下降
- **ERROR**: 操作失败、资源不足、通信错误
- **FATAL**: 硬件故障、内存耗尽、系统崩溃


### 基础日志系统实现

让我们从最简单的实现开始，逐步构建完整的日志系统。

#### 方法1：简单的日志输出

```c
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>

// 全局日志级别
static LogLevel_t g_log_level = LOG_LEVEL_DEBUG;

// 获取系统时间戳（毫秒）
extern uint32_t GetSystemTick(void);

// 串口输出函数
extern void UART_SendString(const char *str);

/**
 * @brief 设置日志级别
 * @param level 日志级别
 */
void Log_SetLevel(LogLevel_t level) {
    g_log_level = level;
}

/**
 * @brief 获取当前日志级别
 * @return 当前日志级别
 */
LogLevel_t Log_GetLevel(void) {
    return g_log_level;
}

/**
 * @brief 基础日志输出函数
 * @param level 日志级别
 * @param format 格式字符串
 * @param ... 可变参数
 */
void Log_Print(LogLevel_t level, const char *format, ...) {
    // 级别过滤
    if(level < g_log_level) {
        return;
    }
    
    char buffer[256];
    int len = 0;
    
    // 添加时间戳
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu] ",
                   tick / 1000, tick % 1000);
    
    // 添加级别标签
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%s] ",
                   log_level_names[level]);
    
    // 添加用户消息
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    // 添加换行符
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
        buffer[len] = '\0';
    }
    
    // 输出到串口
    UART_SendString(buffer);
}

// 便捷宏定义
#define LOG_TRACE(fmt, ...) Log_Print(LOG_LEVEL_TRACE, fmt, ##__VA_ARGS__)
#define LOG_DEBUG(fmt, ...) Log_Print(LOG_LEVEL_DEBUG, fmt, ##__VA_ARGS__)
#define LOG_INFO(fmt, ...)  Log_Print(LOG_LEVEL_INFO,  fmt, ##__VA_ARGS__)
#define LOG_WARN(fmt, ...)  Log_Print(LOG_LEVEL_WARN,  fmt, ##__VA_ARGS__)
#define LOG_ERROR(fmt, ...) Log_Print(LOG_LEVEL_ERROR, fmt, ##__VA_ARGS__)
#define LOG_FATAL(fmt, ...) Log_Print(LOG_LEVEL_FATAL, fmt, ##__VA_ARGS__)

// 使用示例
void Example_BasicLogging(void) {
    Log_SetLevel(LOG_LEVEL_DEBUG);
    
    LOG_TRACE("This is a trace message");      // 不会输出（级别太低）
    LOG_DEBUG("System initialized");           // 输出
    LOG_INFO("Temperature: %d C", 25);         // 输出
    LOG_WARN("Battery low: %d%%", 15);         // 输出
    LOG_ERROR("Sensor read failed");           // 输出
    LOG_FATAL("System crash!");                // 输出
}
```

**输出示例**：
```
[     0.123] [DEBUG] System initialized
[     0.456] [INFO ] Temperature: 25 C
[     0.789] [WARN ] Battery low: 15%
[     1.012] [ERROR] Sensor read failed
[     1.234] [FATAL] System crash!
```


### 增强功能：模块化日志

为不同的模块设置独立的日志级别：

```c
// 模块定义
typedef enum {
    LOG_MODULE_SYSTEM = 0,
    LOG_MODULE_SENSOR,
    LOG_MODULE_NETWORK,
    LOG_MODULE_STORAGE,
    LOG_MODULE_UI,
    LOG_MODULE_MAX
} LogModule_t;

// 模块名称
static const char *log_module_names[] = {
    "SYS",
    "SNS",
    "NET",
    "STG",
    "UI "
};

// 每个模块的日志级别
static LogLevel_t g_module_levels[LOG_MODULE_MAX] = {
    LOG_LEVEL_DEBUG,  // SYSTEM
    LOG_LEVEL_INFO,   // SENSOR
    LOG_LEVEL_WARN,   // NETWORK
    LOG_LEVEL_DEBUG,  // STORAGE
    LOG_LEVEL_INFO    // UI
};

/**
 * @brief 设置模块日志级别
 * @param module 模块ID
 * @param level 日志级别
 */
void Log_SetModuleLevel(LogModule_t module, LogLevel_t level) {
    if(module < LOG_MODULE_MAX) {
        g_module_levels[module] = level;
    }
}

/**
 * @brief 模块化日志输出
 * @param module 模块ID
 * @param level 日志级别
 * @param format 格式字符串
 * @param ... 可变参数
 */
void Log_ModulePrint(LogModule_t module, LogLevel_t level,
                     const char *format, ...) {
    // 检查模块和级别
    if(module >= LOG_MODULE_MAX || level < g_module_levels[module]) {
        return;
    }
    
    char buffer[256];
    int len = 0;
    
    // 时间戳
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu] ",
                   tick / 1000, tick % 1000);
    
    // 级别和模块
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%s][%s] ",
                   log_level_names[level],
                   log_module_names[module]);
    
    // 用户消息
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    // 换行
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
        buffer[len] = '\0';
    }
    
    UART_SendString(buffer);
}

// 模块化日志宏
#define LOG_SYS_DEBUG(fmt, ...) \
    Log_ModulePrint(LOG_MODULE_SYSTEM, LOG_LEVEL_DEBUG, fmt, ##__VA_ARGS__)
#define LOG_SYS_INFO(fmt, ...) \
    Log_ModulePrint(LOG_MODULE_SYSTEM, LOG_LEVEL_INFO, fmt, ##__VA_ARGS__)

#define LOG_SNS_INFO(fmt, ...) \
    Log_ModulePrint(LOG_MODULE_SENSOR, LOG_LEVEL_INFO, fmt, ##__VA_ARGS__)
#define LOG_SNS_ERROR(fmt, ...) \
    Log_ModulePrint(LOG_MODULE_SENSOR, LOG_LEVEL_ERROR, fmt, ##__VA_ARGS__)

// 使用示例
void Example_ModuleLogging(void) {
    // 设置不同模块的日志级别
    Log_SetModuleLevel(LOG_MODULE_SYSTEM, LOG_LEVEL_DEBUG);
    Log_SetModuleLevel(LOG_MODULE_SENSOR, LOG_LEVEL_INFO);
    
    LOG_SYS_DEBUG("System starting...");
    LOG_SYS_INFO("System ready");
    
    LOG_SNS_INFO("Temperature: %d C", 25);
    LOG_SNS_ERROR("Sensor timeout");
}
```

**输出示例**：
```
[     0.100] [DEBUG][SYS] System starting...
[     0.150] [INFO ][SYS] System ready
[     0.200] [INFO ][SNS] Temperature: 25 C
[     0.250] [ERROR][SNS] Sensor timeout
```


### 缓冲机制设计

直接输出日志会阻塞程序执行，使用缓冲可以提高性能。

#### 环形缓冲区实现

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 日志缓冲区配置
#define LOG_BUFFER_SIZE 2048
#define LOG_LINE_MAX_SIZE 256

// 环形缓冲区
typedef struct {
    char buffer[LOG_BUFFER_SIZE];
    volatile uint16_t write_pos;
    volatile uint16_t read_pos;
    volatile uint16_t count;
    volatile bool overflow;
} LogBuffer_t;

static LogBuffer_t g_log_buffer = {0};

/**
 * @brief 初始化日志缓冲区
 */
void LogBuffer_Init(void) {
    memset(&g_log_buffer, 0, sizeof(LogBuffer_t));
}

/**
 * @brief 写入日志到缓冲区
 * @param data 日志数据
 * @param len 数据长度
 * @return true: 成功, false: 缓冲区满
 */
bool LogBuffer_Write(const char *data, uint16_t len) {
    // 检查空间
    if(g_log_buffer.count + len > LOG_BUFFER_SIZE) {
        g_log_buffer.overflow = true;
        return false;
    }
    
    // 写入数据
    for(uint16_t i = 0; i < len; i++) {
        g_log_buffer.buffer[g_log_buffer.write_pos] = data[i];
        g_log_buffer.write_pos = (g_log_buffer.write_pos + 1) % LOG_BUFFER_SIZE;
    }
    
    g_log_buffer.count += len;
    return true;
}

/**
 * @brief 从缓冲区读取日志
 * @param data 输出缓冲区
 * @param max_len 最大长度
 * @return 实际读取的长度
 */
uint16_t LogBuffer_Read(char *data, uint16_t max_len) {
    uint16_t len = 0;
    
    while(g_log_buffer.count > 0 && len < max_len) {
        data[len++] = g_log_buffer.buffer[g_log_buffer.read_pos];
        g_log_buffer.read_pos = (g_log_buffer.read_pos + 1) % LOG_BUFFER_SIZE;
        g_log_buffer.count--;
    }
    
    return len;
}

/**
 * @brief 获取缓冲区可用空间
 * @return 可用字节数
 */
uint16_t LogBuffer_GetFreeSpace(void) {
    return LOG_BUFFER_SIZE - g_log_buffer.count;
}

/**
 * @brief 检查缓冲区是否溢出
 * @return true: 溢出, false: 正常
 */
bool LogBuffer_IsOverflow(void) {
    return g_log_buffer.overflow;
}

/**
 * @brief 清除溢出标志
 */
void LogBuffer_ClearOverflow(void) {
    g_log_buffer.overflow = false;
}

/**
 * @brief 带缓冲的日志输出
 * @param level 日志级别
 * @param module 模块ID
 * @param format 格式字符串
 * @param ... 可变参数
 */
void Log_BufferedPrint(LogLevel_t level, LogModule_t module,
                       const char *format, ...) {
    // 级别过滤
    if(module >= LOG_MODULE_MAX || level < g_module_levels[module]) {
        return;
    }
    
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 格式化日志
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu][%s][%s] ",
                   tick / 1000, tick % 1000,
                   log_level_names[level],
                   log_module_names[module]);
    
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
    }
    
    // 写入缓冲区
    if(!LogBuffer_Write(buffer, len)) {
        // 缓冲区满，可以选择：
        // 1. 丢弃日志
        // 2. 立即输出
        // 3. 覆盖旧日志
    }
}

/**
 * @brief 处理日志缓冲区（在主循环或定时器中调用）
 */
void Log_ProcessBuffer(void) {
    char buffer[128];
    uint16_t len;
    
    // 批量读取并输出
    while((len = LogBuffer_Read(buffer, sizeof(buffer))) > 0) {
        // 输出到串口
        for(uint16_t i = 0; i < len; i++) {
            UART_SendByte(buffer[i]);
        }
    }
    
    // 检查溢出
    if(LogBuffer_IsOverflow()) {
        UART_SendString("\r\n[WARN] Log buffer overflow!\r\n");
        LogBuffer_ClearOverflow();
    }
}

// 使用示例
void Example_BufferedLogging(void) {
    LogBuffer_Init();
    
    // 快速记录多条日志（不阻塞）
    for(int i = 0; i < 10; i++) {
        Log_BufferedPrint(LOG_LEVEL_INFO, LOG_MODULE_SYSTEM,
                         "Loop iteration %d", i);
    }
    
    // 在主循环中处理
    while(1) {
        Log_ProcessBuffer();
        // 其他任务...
    }
}
```


### 格式化输出增强

添加更多上下文信息，使日志更有价值。

#### 文件名和行号

```c
// 增强的日志宏，包含文件名和行号
#define LOG_DEBUG_EX(fmt, ...) \
    Log_PrintEx(LOG_LEVEL_DEBUG, LOG_MODULE_SYSTEM, \
                __FILE__, __LINE__, fmt, ##__VA_ARGS__)

#define LOG_ERROR_EX(fmt, ...) \
    Log_PrintEx(LOG_LEVEL_ERROR, LOG_MODULE_SYSTEM, \
                __FILE__, __LINE__, fmt, ##__VA_ARGS__)

/**
 * @brief 带文件名和行号的日志输出
 * @param level 日志级别
 * @param module 模块ID
 * @param file 文件名
 * @param line 行号
 * @param format 格式字符串
 * @param ... 可变参数
 */
void Log_PrintEx(LogLevel_t level, LogModule_t module,
                 const char *file, int line,
                 const char *format, ...) {
    if(module >= LOG_MODULE_MAX || level < g_module_levels[module]) {
        return;
    }
    
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 提取文件名（去掉路径）
    const char *filename = strrchr(file, '/');
    if(filename == NULL) {
        filename = strrchr(file, '\\');
    }
    filename = (filename != NULL) ? (filename + 1) : file;
    
    // 格式化日志
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu][%s][%s][%s:%d] ",
                   tick / 1000, tick % 1000,
                   log_level_names[level],
                   log_module_names[module],
                   filename, line);
    
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
    }
    
    LogBuffer_Write(buffer, len);
}

// 使用示例
void Example_ExtendedLogging(void) {
    LOG_DEBUG_EX("System initialized");
    LOG_ERROR_EX("Failed to read sensor, error code: %d", -1);
}
```

**输出示例**：
```
[     0.100][DEBUG][SYS][main.c:123] System initialized
[     0.200][ERROR][SYS][sensor.c:45] Failed to read sensor, error code: -1
```

#### 函数名和线程ID

```c
// 包含函数名的日志宏
#define LOG_FUNC_ENTRY() \
    LOG_TRACE(">>> %s", __FUNCTION__)

#define LOG_FUNC_EXIT() \
    LOG_TRACE("<<< %s", __FUNCTION__)

#define LOG_FUNC_EXIT_VAL(val) \
    LOG_TRACE("<<< %s = %d", __FUNCTION__, (int)(val))

// 使用示例
int Calculate_Sum(int a, int b) {
    LOG_FUNC_ENTRY();
    
    int result = a + b;
    LOG_DEBUG("a=%d, b=%d, result=%d", a, b, result);
    
    LOG_FUNC_EXIT_VAL(result);
    return result;
}
```

**输出示例**：
```
[     0.100][TRACE][SYS] >>> Calculate_Sum
[     0.101][DEBUG][SYS] a=10, b=20, result=30
[     0.102][TRACE][SYS] <<< Calculate_Sum = 30
```


### 存储策略

对于需要持久化的日志，可以将日志存储到Flash或SD卡。

#### Flash存储实现

```c
#include <stdint.h>
#include <stdbool.h>

// Flash日志配置
#define LOG_FLASH_START_ADDR  0x08080000  // Flash起始地址
#define LOG_FLASH_SIZE        (128 * 1024) // 128KB
#define LOG_FLASH_SECTOR_SIZE 4096         // 4KB扇区

// Flash日志管理
typedef struct {
    uint32_t write_addr;      // 当前写入地址
    uint32_t read_addr;       // 当前读取地址
    uint32_t total_written;   // 总写入字节数
    bool is_full;             // Flash是否已满
} LogFlash_t;

static LogFlash_t g_log_flash = {
    .write_addr = LOG_FLASH_START_ADDR,
    .read_addr = LOG_FLASH_START_ADDR,
    .total_written = 0,
    .is_full = false
};

// Flash操作函数（需要根据具体芯片实现）
extern bool Flash_EraseSector(uint32_t addr);
extern bool Flash_Write(uint32_t addr, const uint8_t *data, uint32_t len);
extern bool Flash_Read(uint32_t addr, uint8_t *data, uint32_t len);

/**
 * @brief 初始化Flash日志
 */
void LogFlash_Init(void) {
    // 可选：擦除整个日志区域
    // for(uint32_t addr = LOG_FLASH_START_ADDR;
    //     addr < LOG_FLASH_START_ADDR + LOG_FLASH_SIZE;
    //     addr += LOG_FLASH_SECTOR_SIZE) {
    //     Flash_EraseSector(addr);
    // }
    
    g_log_flash.write_addr = LOG_FLASH_START_ADDR;
    g_log_flash.read_addr = LOG_FLASH_START_ADDR;
    g_log_flash.total_written = 0;
    g_log_flash.is_full = false;
}

/**
 * @brief 写入日志到Flash
 * @param data 日志数据
 * @param len 数据长度
 * @return true: 成功, false: 失败
 */
bool LogFlash_Write(const char *data, uint16_t len) {
    // 检查空间
    if(g_log_flash.write_addr + len > LOG_FLASH_START_ADDR + LOG_FLASH_SIZE) {
        g_log_flash.is_full = true;
        return false;
    }
    
    // 检查是否需要擦除扇区
    uint32_t sector_start = (g_log_flash.write_addr / LOG_FLASH_SECTOR_SIZE) * LOG_FLASH_SECTOR_SIZE;
    uint32_t sector_end = sector_start + LOG_FLASH_SECTOR_SIZE;
    
    if(g_log_flash.write_addr == sector_start) {
        // 新扇区，需要擦除
        if(!Flash_EraseSector(sector_start)) {
            return false;
        }
    }
    
    // 写入数据
    if(!Flash_Write(g_log_flash.write_addr, (const uint8_t *)data, len)) {
        return false;
    }
    
    g_log_flash.write_addr += len;
    g_log_flash.total_written += len;
    
    return true;
}

/**
 * @brief 从Flash读取日志
 * @param data 输出缓冲区
 * @param max_len 最大长度
 * @return 实际读取的长度
 */
uint16_t LogFlash_Read(char *data, uint16_t max_len) {
    // 计算可读取的长度
    uint32_t available = g_log_flash.write_addr - g_log_flash.read_addr;
    uint16_t len = (available < max_len) ? available : max_len;
    
    if(len == 0) {
        return 0;
    }
    
    // 读取数据
    if(!Flash_Read(g_log_flash.read_addr, (uint8_t *)data, len)) {
        return 0;
    }
    
    g_log_flash.read_addr += len;
    return len;
}

/**
 * @brief 获取Flash日志统计信息
 */
void LogFlash_GetStats(uint32_t *total_written, uint32_t *available_space) {
    *total_written = g_log_flash.total_written;
    *available_space = LOG_FLASH_SIZE - (g_log_flash.write_addr - LOG_FLASH_START_ADDR);
}

/**
 * @brief 带Flash存储的日志输出
 * @param level 日志级别
 * @param module 模块ID
 * @param format 格式字符串
 * @param ... 可变参数
 */
void Log_PrintToFlash(LogLevel_t level, LogModule_t module,
                      const char *format, ...) {
    if(module >= LOG_MODULE_MAX || level < g_module_levels[module]) {
        return;
    }
    
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 格式化日志
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu][%s][%s] ",
                   tick / 1000, tick % 1000,
                   log_level_names[level],
                   log_module_names[module]);
    
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
    }
    
    // 同时输出到串口和Flash
    UART_SendString(buffer);
    LogFlash_Write(buffer, len);
}
```


### 性能优化

日志系统的性能优化非常重要，避免影响系统实时性。

#### 编译时优化

```c
// 编译时日志级别控制
#ifndef LOG_COMPILE_LEVEL
#define LOG_COMPILE_LEVEL LOG_LEVEL_DEBUG
#endif

// 编译时过滤的日志宏
#if LOG_COMPILE_LEVEL <= LOG_LEVEL_TRACE
#define LOG_TRACE(fmt, ...) Log_Print(LOG_LEVEL_TRACE, fmt, ##__VA_ARGS__)
#else
#define LOG_TRACE(fmt, ...) ((void)0)
#endif

#if LOG_COMPILE_LEVEL <= LOG_LEVEL_DEBUG
#define LOG_DEBUG(fmt, ...) Log_Print(LOG_LEVEL_DEBUG, fmt, ##__VA_ARGS__)
#else
#define LOG_DEBUG(fmt, ...) ((void)0)
#endif

// 在编译时定义：-DLOG_COMPILE_LEVEL=LOG_LEVEL_INFO
// 这样TRACE和DEBUG日志会被完全移除，不占用代码空间
```

#### 条件编译

```c
// 开发版本：启用所有日志
#ifdef DEBUG_BUILD
    #define LOG_ENABLED 1
    #define LOG_COMPILE_LEVEL LOG_LEVEL_TRACE
#else
    // 发布版本：只保留ERROR和FATAL
    #define LOG_ENABLED 1
    #define LOG_COMPILE_LEVEL LOG_LEVEL_ERROR
#endif

// 完全禁用日志
#ifndef LOG_ENABLED
    #define LOG_TRACE(fmt, ...) ((void)0)
    #define LOG_DEBUG(fmt, ...) ((void)0)
    #define LOG_INFO(fmt, ...)  ((void)0)
    #define LOG_WARN(fmt, ...)  ((void)0)
    #define LOG_ERROR(fmt, ...) ((void)0)
    #define LOG_FATAL(fmt, ...) ((void)0)
#endif
```

#### 性能测量

```c
/**
 * @brief 测量日志性能
 */
void Log_PerformanceTest(void) {
    uint32_t start, end;
    uint32_t iterations = 1000;
    
    // 测试1：直接输出
    start = GetSystemTick();
    for(uint32_t i = 0; i < iterations; i++) {
        Log_Print(LOG_LEVEL_INFO, "Test message %lu", i);
    }
    end = GetSystemTick();
    printf("Direct output: %lu ms for %lu logs\n",
           end - start, iterations);
    
    // 测试2：缓冲输出
    start = GetSystemTick();
    for(uint32_t i = 0; i < iterations; i++) {
        Log_BufferedPrint(LOG_LEVEL_INFO, LOG_MODULE_SYSTEM,
                         "Test message %lu", i);
    }
    end = GetSystemTick();
    printf("Buffered output: %lu ms for %lu logs\n",
           end - start, iterations);
    
    // 处理缓冲区
    start = GetSystemTick();
    Log_ProcessBuffer();
    end = GetSystemTick();
    printf("Buffer processing: %lu ms\n", end - start);
}
```

#### 内存优化

```c
// 使用静态缓冲区，避免动态分配
#define LOG_STATIC_BUFFER_SIZE 256
static char g_log_static_buffer[LOG_STATIC_BUFFER_SIZE];

/**
 * @brief 使用静态缓冲区的日志输出
 */
void Log_PrintStatic(LogLevel_t level, const char *format, ...) {
    if(level < g_log_level) {
        return;
    }
    
    int len = 0;
    
    // 使用静态缓冲区
    len += snprintf(g_log_static_buffer + len,
                   LOG_STATIC_BUFFER_SIZE - len,
                   "[%s] ", log_level_names[level]);
    
    va_list args;
    va_start(args, format);
    len += vsnprintf(g_log_static_buffer + len,
                    LOG_STATIC_BUFFER_SIZE - len,
                    format, args);
    va_end(args);
    
    if(len < LOG_STATIC_BUFFER_SIZE - 2) {
        g_log_static_buffer[len++] = '\r';
        g_log_static_buffer[len++] = '\n';
        g_log_static_buffer[len] = '\0';
    }
    
    UART_SendString(g_log_static_buffer);
}
```


## 实践示例

### 示例1：完整的日志系统

实现一个功能完整的日志系统：

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

// 日志系统配置
typedef struct {
    LogLevel_t global_level;              // 全局日志级别
    LogLevel_t module_levels[LOG_MODULE_MAX];  // 模块日志级别
    bool color_enabled;                   // 颜色输出使能
    bool timestamp_enabled;               // 时间戳使能
    bool file_line_enabled;               // 文件名行号使能
    uint32_t log_count;                   // 日志计数
    uint32_t dropped_count;               // 丢弃计数
} LogConfig_t;

static LogConfig_t g_log_config = {
    .global_level = LOG_LEVEL_DEBUG,
    .color_enabled = true,
    .timestamp_enabled = true,
    .file_line_enabled = false,
    .log_count = 0,
    .dropped_count = 0
};

/**
 * @brief 初始化日志系统
 */
void Log_Init(void) {
    // 初始化缓冲区
    LogBuffer_Init();
    
    // 设置默认模块级别
    for(int i = 0; i < LOG_MODULE_MAX; i++) {
        g_log_config.module_levels[i] = LOG_LEVEL_DEBUG;
    }
    
    // 输出启动信息
    LOG_INFO("Log system initialized");
    LOG_INFO("Buffer size: %d bytes", LOG_BUFFER_SIZE);
}

/**
 * @brief 配置日志系统
 */
void Log_Configure(bool color, bool timestamp, bool file_line) {
    g_log_config.color_enabled = color;
    g_log_config.timestamp_enabled = timestamp;
    g_log_config.file_line_enabled = file_line;
}

/**
 * @brief 完整的日志输出函数
 */
void Log_PrintFull(LogLevel_t level, LogModule_t module,
                   const char *file, int line,
                   const char *format, ...) {
    // 级别过滤
    if(level < g_log_config.global_level ||
       level < g_log_config.module_levels[module]) {
        return;
    }
    
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 颜色开始
    if(g_log_config.color_enabled) {
        len += snprintf(buffer + len, sizeof(buffer) - len,
                       "%s", log_level_colors[level]);
    }
    
    // 时间戳
    if(g_log_config.timestamp_enabled) {
        uint32_t tick = GetSystemTick();
        len += snprintf(buffer + len, sizeof(buffer) - len,
                       "[%6lu.%03lu] ",
                       tick / 1000, tick % 1000);
    }
    
    // 级别和模块
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%s][%s] ",
                   log_level_names[level],
                   log_module_names[module]);
    
    // 文件名和行号
    if(g_log_config.file_line_enabled && file != NULL) {
        const char *filename = strrchr(file, '/');
        if(filename == NULL) filename = strrchr(file, '\\');
        filename = (filename != NULL) ? (filename + 1) : file;
        
        len += snprintf(buffer + len, sizeof(buffer) - len,
                       "[%s:%d] ", filename, line);
    }
    
    // 用户消息
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    // 颜色结束
    if(g_log_config.color_enabled) {
        len += snprintf(buffer + len, sizeof(buffer) - len,
                       "%s", COLOR_RESET);
    }
    
    // 换行
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
    }
    
    // 写入缓冲区
    if(LogBuffer_Write(buffer, len)) {
        g_log_config.log_count++;
    } else {
        g_log_config.dropped_count++;
    }
}

/**
 * @brief 获取日志统计信息
 */
void Log_GetStats(uint32_t *total, uint32_t *dropped) {
    *total = g_log_config.log_count;
    *dropped = g_log_config.dropped_count;
}

/**
 * @brief 打印日志统计
 */
void Log_PrintStats(void) {
    uint32_t total, dropped;
    Log_GetStats(&total, &dropped);
    
    LOG_INFO("Log Statistics:");
    LOG_INFO("  Total logs: %lu", total);
    LOG_INFO("  Dropped logs: %lu", dropped);
    LOG_INFO("  Buffer usage: %d/%d bytes",
             LOG_BUFFER_SIZE - LogBuffer_GetFreeSpace(),
             LOG_BUFFER_SIZE);
}

// 完整的日志宏
#define LOG_FULL(level, module, fmt, ...) \
    Log_PrintFull(level, module, __FILE__, __LINE__, fmt, ##__VA_ARGS__)

// 使用示例
void Example_CompleteLogging(void) {
    // 初始化
    Log_Init();
    
    // 配置
    Log_Configure(true, true, true);
    
    // 使用日志
    LOG_FULL(LOG_LEVEL_INFO, LOG_MODULE_SYSTEM,
             "System started");
    LOG_FULL(LOG_LEVEL_DEBUG, LOG_MODULE_SENSOR,
             "Reading sensor: %d", 25);
    LOG_FULL(LOG_LEVEL_ERROR, LOG_MODULE_NETWORK,
             "Connection failed");
    
    // 处理缓冲区
    Log_ProcessBuffer();
    
    // 打印统计
    Log_PrintStats();
}
```


### 示例2：多输出目标

支持同时输出到多个目标（串口、文件、网络）：

```c
// 输出目标类型
typedef enum {
    LOG_OUTPUT_UART = 0,
    LOG_OUTPUT_FILE,
    LOG_OUTPUT_NETWORK,
    LOG_OUTPUT_MAX
} LogOutput_t;

// 输出函数类型
typedef void (*LogOutputFunc_t)(const char *data, uint16_t len);

// 输出目标配置
typedef struct {
    bool enabled;
    LogLevel_t min_level;
    LogOutputFunc_t output_func;
} LogOutputConfig_t;

static LogOutputConfig_t g_log_outputs[LOG_OUTPUT_MAX];

/**
 * @brief 注册输出目标
 */
void Log_RegisterOutput(LogOutput_t output, LogLevel_t min_level,
                        LogOutputFunc_t func) {
    if(output < LOG_OUTPUT_MAX) {
        g_log_outputs[output].enabled = true;
        g_log_outputs[output].min_level = min_level;
        g_log_outputs[output].output_func = func;
    }
}

/**
 * @brief 串口输出函数
 */
void Log_OutputUART(const char *data, uint16_t len) {
    for(uint16_t i = 0; i < len; i++) {
        UART_SendByte(data[i]);
    }
}

/**
 * @brief 文件输出函数
 */
void Log_OutputFile(const char *data, uint16_t len) {
    // 写入SD卡或Flash
    LogFlash_Write(data, len);
}

/**
 * @brief 网络输出函数
 */
void Log_OutputNetwork(const char *data, uint16_t len) {
    // 通过TCP/UDP发送
    // Network_Send(data, len);
}

/**
 * @brief 多目标日志输出
 */
void Log_PrintMulti(LogLevel_t level, const char *format, ...) {
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 格式化日志
    uint32_t tick = GetSystemTick();
    len += snprintf(buffer + len, sizeof(buffer) - len,
                   "[%6lu.%03lu][%s] ",
                   tick / 1000, tick % 1000,
                   log_level_names[level]);
    
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    if(len < sizeof(buffer) - 2) {
        buffer[len++] = '\r';
        buffer[len++] = '\n';
    }
    
    // 输出到所有启用的目标
    for(int i = 0; i < LOG_OUTPUT_MAX; i++) {
        if(g_log_outputs[i].enabled &&
           level >= g_log_outputs[i].min_level &&
           g_log_outputs[i].output_func != NULL) {
            g_log_outputs[i].output_func(buffer, len);
        }
    }
}

// 使用示例
void Example_MultiOutput(void) {
    // 注册输出目标
    Log_RegisterOutput(LOG_OUTPUT_UART, LOG_LEVEL_DEBUG,
                      Log_OutputUART);
    Log_RegisterOutput(LOG_OUTPUT_FILE, LOG_LEVEL_INFO,
                      Log_OutputFile);
    Log_RegisterOutput(LOG_OUTPUT_NETWORK, LOG_LEVEL_ERROR,
                      Log_OutputNetwork);
    
    // 输出日志
    Log_PrintMulti(LOG_LEVEL_DEBUG, "Debug message");    // 只到UART
    Log_PrintMulti(LOG_LEVEL_INFO, "Info message");      // UART + File
    Log_PrintMulti(LOG_LEVEL_ERROR, "Error message");    // 所有目标
}
```

### 示例3：日志过滤和搜索

实现日志过滤和搜索功能：

```c
/**
 * @brief 日志过滤器
 */
typedef struct {
    LogLevel_t min_level;
    LogLevel_t max_level;
    LogModule_t module;
    const char *keyword;
} LogFilter_t;

/**
 * @brief 检查日志是否匹配过滤器
 */
bool Log_MatchFilter(const char *log_line, const LogFilter_t *filter) {
    // 简单的字符串匹配
    if(filter->keyword != NULL) {
        if(strstr(log_line, filter->keyword) == NULL) {
            return false;
        }
    }
    
    // 可以添加更多过滤条件
    return true;
}

/**
 * @brief 从Flash读取并过滤日志
 */
void Log_ReadFiltered(const LogFilter_t *filter) {
    char buffer[LOG_LINE_MAX_SIZE];
    uint16_t len;
    
    // 重置读取位置
    g_log_flash.read_addr = LOG_FLASH_START_ADDR;
    
    printf("Filtered logs:\n");
    printf("----------------------------------------\n");
    
    while((len = LogFlash_Read(buffer, sizeof(buffer) - 1)) > 0) {
        buffer[len] = '\0';
        
        // 检查是否匹配过滤器
        if(Log_MatchFilter(buffer, filter)) {
            printf("%s", buffer);
        }
    }
    
    printf("----------------------------------------\n");
}

// 使用示例
void Example_LogFilter(void) {
    // 过滤ERROR级别的日志
    LogFilter_t filter = {
        .min_level = LOG_LEVEL_ERROR,
        .max_level = LOG_LEVEL_FATAL,
        .module = LOG_MODULE_MAX,  // 所有模块
        .keyword = NULL
    };
    
    Log_ReadFiltered(&filter);
    
    // 搜索包含"sensor"的日志
    filter.keyword = "sensor";
    Log_ReadFiltered(&filter);
}
```


## 深入理解

### 日志系统设计原则

#### 1. 性能优先

日志系统不应该成为性能瓶颈：

**最佳实践**：
- 使用缓冲机制，避免阻塞
- 编译时过滤低级别日志
- 使用静态内存，避免动态分配
- 批量输出，减少系统调用

**性能对比**：
```c
// 方案1：直接输出（慢）
void SlowLog(const char *msg) {
    printf("[INFO] %s\n", msg);  // 每次都调用printf
}

// 方案2：缓冲输出（快）
void FastLog(const char *msg) {
    LogBuffer_Write(msg, strlen(msg));  // 写入缓冲区
    // 稍后批量输出
}

// 性能差异：
// 直接输出：~1000us/条
// 缓冲输出：~10us/条（写入） + 批量输出时间
```

#### 2. 可靠性保证

日志系统必须可靠，不能因为日志导致系统崩溃：

**安全措施**：
- 缓冲区溢出保护
- 格式化字符串长度限制
- 中断安全的实现
- 错误处理和降级

```c
// 安全的日志实现
void SafeLog(LogLevel_t level, const char *format, ...) {
    // 1. 级别检查
    if(level < g_log_level) {
        return;
    }
    
    // 2. 缓冲区保护
    char buffer[LOG_LINE_MAX_SIZE];
    int len = 0;
    
    // 3. 安全的格式化
    va_list args;
    va_start(args, format);
    len = vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    // 4. 长度检查
    if(len >= sizeof(buffer)) {
        len = sizeof(buffer) - 1;
        buffer[len] = '\0';
    }
    
    // 5. 安全的写入
    if(!LogBuffer_Write(buffer, len)) {
        // 缓冲区满，记录丢弃
        g_log_config.dropped_count++;
    }
}
```

#### 3. 灵活性设计

日志系统应该灵活可配置：

**配置项**：
- 运行时调整日志级别
- 模块化的日志控制
- 多种输出目标
- 可选的格式化选项

```c
// 灵活的配置接口
typedef struct {
    LogLevel_t level;
    bool timestamp;
    bool color;
    bool file_line;
    LogOutput_t outputs[LOG_OUTPUT_MAX];
} LogSettings_t;

void Log_ApplySettings(const LogSettings_t *settings) {
    g_log_config.global_level = settings->level;
    g_log_config.timestamp_enabled = settings->timestamp;
    g_log_config.color_enabled = settings->color;
    g_log_config.file_line_enabled = settings->file_line;
    
    // 应用输出配置
    for(int i = 0; i < LOG_OUTPUT_MAX; i++) {
        // 配置输出目标
    }
}
```

### 常见问题和解决方案

#### 问题1：日志输出影响实时性

**现象**：
- 系统响应变慢
- 中断延迟增加
- 任务调度不及时

**原因**：
- 直接输出日志阻塞程序
- 格式化字符串耗时
- 串口发送速度慢

**解决方案**：
```c
// 1. 使用缓冲机制
void Log_Buffered(const char *msg) {
    LogBuffer_Write(msg, strlen(msg));
    // 不等待输出完成
}

// 2. 在低优先级任务中处理
void LowPriorityTask(void) {
    while(1) {
        Log_ProcessBuffer();  // 批量输出
        Delay_Ms(10);
    }
}

// 3. 使用DMA传输
void Log_DMA(const char *msg, uint16_t len) {
    UART_SendDMA(msg, len);  // DMA传输，不阻塞CPU
}
```

#### 问题2：缓冲区溢出

**现象**：
- 日志丢失
- 系统崩溃
- 内存损坏

**原因**：
- 日志产生速度 > 输出速度
- 缓冲区太小
- 没有溢出保护

**解决方案**：
```c
// 1. 增大缓冲区
#define LOG_BUFFER_SIZE 4096  // 增大到4KB

// 2. 溢出保护
bool LogBuffer_Write(const char *data, uint16_t len) {
    if(g_log_buffer.count + len > LOG_BUFFER_SIZE) {
        // 选项A：丢弃新日志
        g_log_buffer.overflow = true;
        return false;
        
        // 选项B：覆盖旧日志（环形缓冲）
        // 移动读指针，覆盖旧数据
    }
    // 写入数据...
}

// 3. 流量控制
static uint32_t last_log_time = 0;
#define LOG_MIN_INTERVAL 10  // 最小间隔10ms

void Log_RateLimited(const char *msg) {
    uint32_t now = GetSystemTick();
    if(now - last_log_time < LOG_MIN_INTERVAL) {
        return;  // 限流
    }
    last_log_time = now;
    
    Log_Print(msg);
}
```

#### 问题3：Flash写入寿命

**现象**：
- Flash损坏
- 写入失败
- 数据丢失

**原因**：
- 频繁写入同一扇区
- 超过Flash擦写次数限制

**解决方案**：
```c
// 1. 磨损均衡
typedef struct {
    uint32_t sector_addr;
    uint32_t erase_count;
} SectorInfo_t;

SectorInfo_t g_sectors[32];

uint32_t FindLeastUsedSector(void) {
    uint32_t min_count = 0xFFFFFFFF;
    uint32_t min_index = 0;
    
    for(int i = 0; i < 32; i++) {
        if(g_sectors[i].erase_count < min_count) {
            min_count = g_sectors[i].erase_count;
            min_index = i;
        }
    }
    
    return g_sectors[min_index].sector_addr;
}

// 2. 批量写入
#define LOG_FLASH_BATCH_SIZE 512
char g_flash_batch_buffer[LOG_FLASH_BATCH_SIZE];
uint16_t g_flash_batch_pos = 0;

void Log_FlashBatched(const char *msg, uint16_t len) {
    // 累积到批量缓冲区
    if(g_flash_batch_pos + len < LOG_FLASH_BATCH_SIZE) {
        memcpy(g_flash_batch_buffer + g_flash_batch_pos, msg, len);
        g_flash_batch_pos += len;
    } else {
        // 缓冲区满，一次性写入Flash
        LogFlash_Write(g_flash_batch_buffer, g_flash_batch_pos);
        g_flash_batch_pos = 0;
    }
}

// 3. 定期写入
void Log_FlashPeriodic(void) {
    static uint32_t last_flush = 0;
    uint32_t now = GetSystemTick();
    
    // 每5秒写入一次
    if(now - last_flush > 5000) {
        if(g_flash_batch_pos > 0) {
            LogFlash_Write(g_flash_batch_buffer, g_flash_batch_pos);
            g_flash_batch_pos = 0;
        }
        last_flush = now;
    }
}
```


### 最佳实践

#### 1. 日志级别使用指南

**TRACE级别**：
```c
// 用于追踪程序执行流程
void ProcessData(uint8_t *data, uint16_t len) {
    LOG_TRACE(">>> ProcessData(data=%p, len=%d)", data, len);
    
    for(uint16_t i = 0; i < len; i++) {
        LOG_TRACE("Processing byte[%d] = 0x%02X", i, data[i]);
        // 处理数据...
    }
    
    LOG_TRACE("<<< ProcessData");
}
```

**DEBUG级别**：
```c
// 用于调试信息和中间结果
void CalculateChecksum(uint8_t *data, uint16_t len) {
    uint16_t checksum = 0;
    
    for(uint16_t i = 0; i < len; i++) {
        checksum += data[i];
    }
    
    LOG_DEBUG("Checksum calculated: 0x%04X", checksum);
    return checksum;
}
```

**INFO级别**：
```c
// 用于记录正常操作和状态变化
void SystemInit(void) {
    LOG_INFO("System initializing...");
    
    HAL_Init();
    LOG_INFO("HAL initialized");
    
    SystemClock_Config();
    LOG_INFO("System clock configured: %lu MHz", SystemCoreClock / 1000000);
    
    GPIO_Init();
    LOG_INFO("GPIO initialized");
    
    LOG_INFO("System initialization complete");
}
```

**WARN级别**：
```c
// 用于警告信息，不影响功能但需要注意
void ReadSensor(void) {
    int16_t value = ADC_Read();
    
    if(value < 0) {
        LOG_WARN("Sensor value negative: %d, using 0", value);
        value = 0;
    }
    
    if(value > 4095) {
        LOG_WARN("Sensor value overflow: %d, clamping to 4095", value);
        value = 4095;
    }
    
    return value;
}
```

**ERROR级别**：
```c
// 用于错误信息，功能失败但系统可继续
bool SendData(uint8_t *data, uint16_t len) {
    if(data == NULL || len == 0) {
        LOG_ERROR("Invalid parameters: data=%p, len=%d", data, len);
        return false;
    }
    
    if(!Network_IsConnected()) {
        LOG_ERROR("Network not connected, cannot send data");
        return false;
    }
    
    int result = Network_Send(data, len);
    if(result < 0) {
        LOG_ERROR("Network send failed: error=%d", result);
        return false;
    }
    
    return true;
}
```

**FATAL级别**：
```c
// 用于致命错误，系统无法继续运行
void CriticalError(const char *msg) {
    LOG_FATAL("Critical error: %s", msg);
    LOG_FATAL("System halting...");
    
    // 保存关键数据
    SaveCriticalData();
    
    // 系统复位或停机
    NVIC_SystemReset();
}
```

#### 2. 日志消息编写规范

**清晰明确**：
```c
// ❌ 不好的日志
LOG_ERROR("Error");
LOG_ERROR("Failed");

// ✅ 好的日志
LOG_ERROR("Failed to read sensor: timeout after 1000ms");
LOG_ERROR("Network connection failed: error code -5");
```

**包含上下文**：
```c
// ❌ 缺少上下文
LOG_INFO("Value: %d", value);

// ✅ 包含上下文
LOG_INFO("Temperature sensor reading: %d C", value);
LOG_INFO("Battery voltage: %d mV", value);
```

**使用一致的格式**：
```c
// ✅ 统一的格式
LOG_INFO("System started");
LOG_INFO("Network connected");
LOG_INFO("Data received");

// ❌ 不一致的格式
LOG_INFO("System started");
LOG_INFO("The network is now connected");
LOG_INFO("Received some data");
```

**避免敏感信息**：
```c
// ❌ 包含敏感信息
LOG_INFO("User password: %s", password);
LOG_INFO("API key: %s", api_key);

// ✅ 隐藏敏感信息
LOG_INFO("User authenticated successfully");
LOG_INFO("API key validated");
```

#### 3. 性能优化技巧

**条件日志**：
```c
// 只在需要时格式化
#define LOG_DEBUG_IF(cond, fmt, ...) \
    do { \
        if(cond) { \
            LOG_DEBUG(fmt, ##__VA_ARGS__); \
        } \
    } while(0)

// 使用示例
LOG_DEBUG_IF(verbose_mode, "Detailed info: %d", value);
```

**延迟格式化**：
```c
// 先检查级别，再格式化
void Log_Lazy(LogLevel_t level, const char *format, ...) {
    if(level < g_log_level) {
        return;  // 直接返回，不格式化
    }
    
    // 只有需要输出时才格式化
    va_list args;
    va_start(args, format);
    // 格式化和输出...
    va_end(args);
}
```

**批量输出**：
```c
// 累积多条日志，一次性输出
void Log_Flush(void) {
    char buffer[512];
    uint16_t len = 0;
    
    // 从缓冲区读取多条日志
    while(len < sizeof(buffer) - LOG_LINE_MAX_SIZE) {
        uint16_t read_len = LogBuffer_Read(buffer + len,
                                          LOG_LINE_MAX_SIZE);
        if(read_len == 0) break;
        len += read_len;
    }
    
    // 一次性输出
    if(len > 0) {
        UART_SendDMA(buffer, len);
    }
}
```


## 总结

### 关键要点

通过本教程，我们学习了日志系统的完整设计和实现：

1. **日志级别管理**
   - 定义了TRACE、DEBUG、INFO、WARN、ERROR、FATAL六个级别
   - 实现了全局和模块化的级别控制
   - 支持编译时和运行时的级别过滤

2. **格式化输出**
   - 实现了统一的日志格式
   - 支持时间戳、模块名、文件名和行号
   - 支持颜色输出和自定义格式

3. **缓冲机制**
   - 使用环形缓冲区提高性能
   - 实现了异步输出和批量处理
   - 提供了溢出保护和流量控制

4. **存储策略**
   - 支持Flash持久化存储
   - 实现了磨损均衡和批量写入
   - 提供了日志读取和过滤功能

5. **性能优化**
   - 编译时优化减少代码体积
   - 使用静态内存避免动态分配
   - 实现了DMA传输和批量输出

### 实际应用建议

**开发阶段**：
- 使用DEBUG或TRACE级别
- 启用文件名和行号
- 输出到串口便于实时查看

**测试阶段**：
- 使用INFO级别
- 启用Flash存储记录问题
- 定期分析日志查找问题

**生产环境**：
- 使用WARN或ERROR级别
- 关闭详细信息减少开销
- 保留关键日志用于故障分析

### 下一步学习

掌握了日志系统后，你可以：

1. **学习RTOS日志**
   - 在RTOS环境中实现线程安全的日志
   - 使用消息队列传递日志
   - 实现日志任务和优先级管理

2. **学习远程日志**
   - 通过网络发送日志到服务器
   - 实现日志聚合和分析
   - 构建日志监控系统

3. **学习日志分析**
   - 使用工具解析日志文件
   - 实现日志可视化
   - 进行性能分析和故障诊断

## 常见问题

**Q1: 日志系统会影响系统性能吗？**

A: 如果设计得当，影响很小：
- 使用缓冲机制，避免阻塞
- 编译时过滤低级别日志
- 在低优先级任务中处理输出
- 生产环境只保留必要的日志

**Q2: 如何选择合适的日志级别？**

A: 根据信息的重要性：
- TRACE/DEBUG：开发调试使用
- INFO：记录正常操作
- WARN：潜在问题，不影响功能
- ERROR：功能失败，需要处理
- FATAL：系统崩溃，无法继续

**Q3: 缓冲区应该设置多大？**

A: 取决于日志产生速度和输出速度：
- 计算公式：缓冲区大小 ≥ 日志速度 × 输出间隔
- 一般建议：2KB - 8KB
- 可以根据实际情况动态调整

**Q4: 如何在中断中使用日志？**

A: 需要特别注意：
- 使用中断安全的缓冲区操作
- 避免使用printf等阻塞函数
- 只记录关键信息，保持简短
- 考虑使用专门的中断日志缓冲区

**Q5: Flash日志会影响Flash寿命吗？**

A: 需要合理使用：
- 使用磨损均衡算法
- 批量写入减少擦除次数
- 只记录重要日志到Flash
- 定期归档和清理旧日志

## 延伸阅读

### 相关教程
- 环形缓冲区设计与实现
- 命令行接口实现
- 裸机程序调试技巧

### 参考资料
- [C语言格式化输出](https://en.cppreference.com/w/c/io/fprintf)
- [嵌入式系统调试技术](https://www.embedded.com/debugging-techniques/)
- [日志系统设计模式](https://martinfowler.com/articles/patterns-of-distributed-systems/log.html)

### 开源项目
- [NLog](https://github.com/NLog/NLog) - .NET日志框架
- [spdlog](https://github.com/gabime/spdlog) - C++高性能日志库
- [zlog](https://github.com/HardySimpson/zlog) - C语言日志库

---

**学习建议**：日志系统是嵌入式开发的基础工具，建议在实际项目中不断完善和优化。从简单的实现开始，逐步添加功能，最终构建适合自己项目的日志系统。

**实践练习**：
1. 实现一个基础的日志系统，支持多个级别
2. 添加环形缓冲区，实现异步输出
3. 实现Flash存储功能
4. 添加日志过滤和搜索功能
5. 优化性能，测量日志开销

祝你学习愉快！
