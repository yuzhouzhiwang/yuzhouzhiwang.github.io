---
title: "性能分析工具开发：构建专业的嵌入式性能分析系统"
description: "深入讲解嵌入式性能分析工具的设计、数据采集、分析算法、可视化实现和完整工具开发，帮助开发者构建专业的性能分析系统"
slug: "performance-analysis-tool"

# 分类信息
domain: "工具链"
module: "性能优化"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - 性能工具
  - 工具开发
  - 性能分析
  - 数据可视化
  - 性能监控
  - 系统分析
prerequisites:
  - "熟悉嵌入式系统开发"
  - "掌握C/C++或Python编程"
  - "了解性能优化基础"
  - "熟悉数据结构和算法"
related_contents:
  - "code-optimization-basics"
  - "execution-time-measurement"
  - "real-time-optimization"

# 学习信息
estimated_time: 180
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
  - 性能分析工具
  - 性能监控
  - 工具开发
  - 嵌入式分析
  - 性能可视化
  - 系统监控
cover_image: ""
---


# 性能分析工具开发：构建专业的嵌入式性能分析系统

## 项目概述

本项目将指导你开发一个完整的嵌入式性能分析工具，用于实时监控、分析和可视化嵌入式系统的性能数据。该工具能够帮助开发者快速识别性能瓶颈，优化系统性能，提高开发效率。

### 项目目标

完成本项目后，你将拥有:

- [ ] 完整的性能数据采集系统
- [ ] 实时性能监控界面
- [ ] 多维度性能分析算法
- [ ] 交互式数据可视化工具
- [ ] 性能报告生成系统
- [ ] 历史数据管理功能
- [ ] 可扩展的插件架构

### 项目特点

**技术亮点**:
- 低开销的数据采集机制
- 实时数据处理和分析
- 丰富的可视化图表
- 智能性能瓶颈识别
- 支持多种嵌入式平台
- 模块化设计，易于扩展

**应用场景**:
- 实时系统性能监控
- 性能瓶颈定位
- 功耗分析
- 内存使用分析
- 任务调度分析
- 中断响应分析

## 前置要求

### 知识要求

**必备知识**:
- 精通C/C++或Python编程
- 深入理解嵌入式系统架构
- 熟悉性能优化原理
- 了解数据结构和算法
- 掌握串口通信协议

**推荐知识**:
- 了解Web开发基础(HTML/CSS/JavaScript)
- 熟悉数据可视化库(Matplotlib, Chart.js等)
- 了解数据库操作
- 掌握多线程编程
- 了解统计分析方法

### 技能要求

- 能够设计系统架构
- 能够编写高效的数据处理代码
- 能够创建用户界面
- 能够分析性能数据
- 能够编写技术文档



## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考价格 |
|------|------|------|----------|
| 开发主机 | 1 | PC或笔记本，运行分析工具 | ¥3000-8000 |
| 目标开发板 | 1 | STM32/ESP32等嵌入式开发板 | ¥50-500 |
| 调试器 | 1 | J-Link/ST-Link等 | ¥200-1000 |
| USB转串口 | 1 | 用于数据传输 | ¥20-50 |
| 逻辑分析仪 | 1 | 可选，用于信号分析 | ¥200-2000 |

### 软件准备

**开发环境**:
- **操作系统**: Windows 10+, Linux (Ubuntu 20.04+) 或 macOS
- **编程语言**: Python 3.8+ (主机端), C/C++ (嵌入式端)
- **IDE**: VS Code, PyCharm 或 Visual Studio
- **版本控制**: Git

**Python依赖**:
```bash
# 核心库
pip install pyserial numpy pandas

# 数据可视化
pip install matplotlib plotly dash

# Web界面
pip install flask flask-socketio

# 数据处理
pip install scipy scikit-learn

# 数据库
pip install sqlalchemy sqlite3
```

**嵌入式工具链**:
- ARM GCC 或对应平台的编译器
- OpenOCD 或 J-Link 软件
- 串口调试工具

### 系统要求

**最低配置**:
- CPU: Intel i5 或同等性能
- 内存: 8GB RAM
- 存储: 50GB 可用空间
- 显示: 1920x1080分辨率

**推荐配置**:
- CPU: Intel i7 或更高
- 内存: 16GB+ RAM
- 存储: 256GB SSD
- 显示: 双显示器，2K分辨率



## 步骤1: 系统架构设计

### 1.1 性能分析工具概述

**什么是性能分析工具？**

性能分析工具是用于监控、采集、分析和可视化嵌入式系统运行时性能数据的软件系统。它能够帮助开发者:
- 实时监控系统运行状态
- 识别性能瓶颈
- 分析资源使用情况
- 优化系统性能
- 生成性能报告

**核心功能**:
- **数据采集**: 从目标设备采集性能数据
- **实时监控**: 实时显示系统运行状态
- **数据分析**: 分析性能数据，识别问题
- **可视化**: 以图表形式展示数据
- **报告生成**: 生成详细的性能报告

### 1.2 系统架构

**整体架构图**:
```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │实时监控  │  │数据分析  │  │报告生成  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    数据处理层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │数据解析  │  │数据分析  │  │数据存储  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    通信层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │串口通信  │  │网络通信  │  │调试接口  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    嵌入式端                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │数据采集  │  │数据编码  │  │数据发送  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 1.3 核心模块设计

**1. 嵌入式端数据采集模块**

功能:
- CPU使用率采集
- 内存使用情况采集
- 任务执行时间采集
- 中断响应时间采集
- 函数调用统计
- 自定义性能计数器

**2. 主机端通信模块**

功能:
- 串口数据接收
- 数据包解析
- 数据缓冲管理
- 通信错误处理

**3. 数据处理模块**

功能:
- 数据解码和验证
- 数据聚合和统计
- 性能指标计算
- 异常检测

**4. 数据存储模块**

功能:
- 实时数据缓存
- 历史数据存储
- 数据查询接口
- 数据导出功能

**5. 可视化模块**

功能:
- 实时曲线图
- 柱状图和饼图
- 热力图
- 时间线视图
- 交互式图表

**6. 分析模块**

功能:
- 性能瓶颈识别
- 趋势分析
- 对比分析
- 统计分析
- 智能建议

### 1.4 数据格式设计

**性能数据包格式**:
```
┌────────┬────────┬────────┬────────────┬────────┬────────┐
│ Header │ Length │  Type  │    Data    │  CRC   │  Tail  │
│ (2B)   │ (2B)   │ (1B)   │  (N bytes) │ (2B)   │ (1B)   │
└────────┴────────┴────────┴────────────┴────────┴────────┘

Header: 0xAA55 (固定)
Length: 数据长度
Type: 数据类型
  0x01: CPU使用率
  0x02: 内存使用
  0x03: 任务信息
  0x04: 函数性能
  0x05: 中断统计
  0x06: 自定义数据
Data: 实际数据
CRC: CRC16校验
Tail: 0x0D (固定)
```

**数据类型定义**:
```c
// CPU使用率数据
typedef struct {
    uint32_t timestamp;      // 时间戳(ms)
    uint8_t  cpu_usage;      // CPU使用率(0-100)
    uint32_t idle_time;      // 空闲时间(us)
    uint32_t total_time;     // 总时间(us)
} CPUData_t;

// 内存使用数据
typedef struct {
    uint32_t timestamp;      // 时间戳(ms)
    uint32_t total_heap;     // 总堆大小
    uint32_t used_heap;      // 已用堆大小
    uint32_t free_heap;      // 空闲堆大小
    uint32_t peak_usage;     // 峰值使用
} MemoryData_t;

// 任务性能数据
typedef struct {
    uint32_t timestamp;      // 时间戳(ms)
    uint8_t  task_id;        // 任务ID
    char     task_name[16];  // 任务名称
    uint32_t exec_time;      // 执行时间(us)
    uint32_t exec_count;     // 执行次数
    uint8_t  priority;       // 优先级
    uint8_t  state;          // 状态
} TaskData_t;

// 函数性能数据
typedef struct {
    uint32_t timestamp;      // 时间戳(ms)
    uint16_t func_id;        // 函数ID
    char     func_name[32];  // 函数名称
    uint32_t call_count;     // 调用次数
    uint32_t total_time;     // 总时间(us)
    uint32_t min_time;       // 最小时间(us)
    uint32_t max_time;       // 最大时间(us)
    uint32_t avg_time;       // 平均时间(us)
} FunctionData_t;
```

### 1.5 目录结构设计

```
performance_analyzer/
├── embedded/               # 嵌入式端代码
│   ├── inc/               # 头文件
│   │   ├── perf_monitor.h
│   │   ├── perf_config.h
│   │   └── perf_protocol.h
│   ├── src/               # 源文件
│   │   ├── perf_monitor.c
│   │   ├── perf_cpu.c
│   │   ├── perf_memory.c
│   │   ├── perf_task.c
│   │   └── perf_comm.c
│   └── examples/          # 示例代码
├── host/                   # 主机端代码
│   ├── core/              # 核心模块
│   │   ├── data_receiver.py
│   │   ├── data_parser.py
│   │   ├── data_analyzer.py
│   │   └── data_storage.py
│   ├── ui/                # 用户界面
│   │   ├── main_window.py
│   │   ├── monitor_panel.py
│   │   ├── analysis_panel.py
│   │   └── report_panel.py
│   ├── visualization/     # 可视化
│   │   ├── realtime_chart.py
│   │   ├── histogram.py
│   │   └── timeline.py
│   └── utils/             # 工具函数
│       ├── logger.py
│       ├── config.py
│       └── report_gen.py
├── config/                 # 配置文件
│   ├── analyzer.yaml
│   └── logging.yaml
├── data/                   # 数据目录
│   ├── realtime/          # 实时数据
│   └── history/           # 历史数据
├── reports/                # 报告目录
├── docs/                   # 文档
├── tests/                  # 测试代码
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```



## 步骤2: 嵌入式端数据采集实现

### 2.1 性能监控核心模块

**性能监控头文件** (`perf_monitor.h`):

```c
#ifndef PERF_MONITOR_H
#define PERF_MONITOR_H

#include <stdint.h>
#include <stdbool.h>

// 配置参数
#define PERF_MAX_FUNCTIONS    50    // 最大监控函数数
#define PERF_MAX_TASKS        10    // 最大监控任务数
#define PERF_BUFFER_SIZE      1024  // 数据缓冲区大小
#define PERF_SAMPLE_INTERVAL  100   // 采样间隔(ms)

// 数据类型
typedef enum {
    PERF_TYPE_CPU = 0x01,
    PERF_TYPE_MEMORY = 0x02,
    PERF_TYPE_TASK = 0x03,
    PERF_TYPE_FUNCTION = 0x04,
    PERF_TYPE_INTERRUPT = 0x05,
    PERF_TYPE_CUSTOM = 0x06
} PerfDataType_t;

// CPU性能数据
typedef struct {
    uint32_t timestamp;
    uint8_t  cpu_usage;
    uint32_t idle_time;
    uint32_t total_time;
} PerfCPUData_t;

// 内存性能数据
typedef struct {
    uint32_t timestamp;
    uint32_t total_heap;
    uint32_t used_heap;
    uint32_t free_heap;
    uint32_t peak_usage;
} PerfMemoryData_t;

// 函数性能计数器
typedef struct {
    const char *name;
    uint16_t func_id;
    uint32_t call_count;
    uint32_t total_cycles;
    uint32_t min_cycles;
    uint32_t max_cycles;
    bool enabled;
} PerfFunctionCounter_t;

// 性能监控配置
typedef struct {
    bool cpu_monitor_enabled;
    bool memory_monitor_enabled;
    bool task_monitor_enabled;
    bool function_monitor_enabled;
    uint32_t sample_interval_ms;
    void (*send_callback)(uint8_t *data, uint16_t len);
} PerfMonitorConfig_t;

// 初始化和控制
void Perf_Init(PerfMonitorConfig_t *config);
void Perf_Start(void);
void Perf_Stop(void);
void Perf_Reset(void);

// CPU监控
void Perf_CPU_Update(void);
uint8_t Perf_CPU_GetUsage(void);

// 内存监控
void Perf_Memory_Update(void);
uint32_t Perf_Memory_GetUsed(void);
uint32_t Perf_Memory_GetFree(void);

// 函数性能监控
int Perf_Function_Register(const char *name);
void Perf_Function_Start(int func_id);
void Perf_Function_End(int func_id);
void Perf_Function_GetStats(int func_id, PerfFunctionCounter_t *stats);

// 数据发送
void Perf_SendData(PerfDataType_t type, void *data, uint16_t len);

// 辅助宏
#define PERF_MEASURE_START(id) \
    static int __perf_id_##id = -1; \
    if (__perf_id_##id == -1) { \
        __perf_id_##id = Perf_Function_Register(#id); \
    } \
    Perf_Function_Start(__perf_id_##id)

#define PERF_MEASURE_END(id) \
    Perf_Function_End(__perf_id_##id)

#endif // PERF_MONITOR_H
```

### 2.2 CPU使用率监控

**CPU监控实现** (`perf_cpu.c`):

```c
#include "perf_monitor.h"
#include <string.h>

// DWT寄存器定义(Cortex-M)
#define DWT_CTRL    (*(volatile uint32_t *)0xE0001000)
#define DWT_CYCCNT  (*(volatile uint32_t *)0xE0001004)
#define DEM_CR      (*(volatile uint32_t *)0xE000EDFC)
#define DEM_CR_TRCENA (1 << 24)

// CPU监控数据
static struct {
    uint32_t last_total_cycles;
    uint32_t last_idle_cycles;
    uint32_t last_timestamp;
    uint8_t  cpu_usage;
    bool initialized;
} cpu_monitor;

/**
 * @brief 初始化DWT周期计数器
 */
static void DWT_Init(void) {
    // 使能DWT
    DEM_CR |= DEM_CR_TRCENA;
    
    // 复位周期计数器
    DWT_CYCCNT = 0;
    
    // 使能周期计数器
    DWT_CTRL |= 1;
}

/**
 * @brief 获取当前周期计数
 */
static inline uint32_t DWT_GetCycles(void) {
    return DWT_CYCCNT;
}

/**
 * @brief 初始化CPU监控
 */
void Perf_CPU_Init(void) {
    DWT_Init();
    
    cpu_monitor.last_total_cycles = 0;
    cpu_monitor.last_idle_cycles = 0;
    cpu_monitor.last_timestamp = 0;
    cpu_monitor.cpu_usage = 0;
    cpu_monitor.initialized = true;
}

/**
 * @brief 更新CPU使用率
 * 
 * 应在空闲任务中调用，记录空闲时间
 */
void Perf_CPU_Update(void) {
    if (!cpu_monitor.initialized) {
        return;
    }
    
    uint32_t current_cycles = DWT_GetCycles();
    uint32_t current_time = HAL_GetTick();
    
    // 计算时间差
    uint32_t delta_time = current_time - cpu_monitor.last_timestamp;
    
    if (delta_time >= PERF_SAMPLE_INTERVAL) {
        // 计算周期差
        uint32_t total_cycles = current_cycles - cpu_monitor.last_total_cycles;
        uint32_t idle_cycles = cpu_monitor.last_idle_cycles;
        
        // 计算CPU使用率
        if (total_cycles > 0) {
            uint32_t busy_cycles = total_cycles - idle_cycles;
            cpu_monitor.cpu_usage = (busy_cycles * 100) / total_cycles;
            
            // 限制在0-100范围
            if (cpu_monitor.cpu_usage > 100) {
                cpu_monitor.cpu_usage = 100;
            }
        }
        
        // 发送数据
        PerfCPUData_t data = {
            .timestamp = current_time,
            .cpu_usage = cpu_monitor.cpu_usage,
            .idle_time = idle_cycles,
            .total_time = total_cycles
        };
        Perf_SendData(PERF_TYPE_CPU, &data, sizeof(data));
        
        // 更新记录
        cpu_monitor.last_total_cycles = current_cycles;
        cpu_monitor.last_idle_cycles = 0;
        cpu_monitor.last_timestamp = current_time;
    }
}

/**
 * @brief 记录空闲时间
 * 
 * 在空闲任务中调用
 */
void Perf_CPU_RecordIdle(void) {
    static uint32_t idle_start = 0;
    
    if (idle_start == 0) {
        idle_start = DWT_GetCycles();
    } else {
        uint32_t idle_end = DWT_GetCycles();
        cpu_monitor.last_idle_cycles += (idle_end - idle_start);
        idle_start = idle_end;
    }
}

/**
 * @brief 获取CPU使用率
 */
uint8_t Perf_CPU_GetUsage(void) {
    return cpu_monitor.cpu_usage;
}
```

### 2.3 内存使用监控

**内存监控实现** (`perf_memory.c`):

```c
#include "perf_monitor.h"
#include <stdlib.h>
#include <string.h>

// 内存监控数据
static struct {
    uint32_t total_heap;
    uint32_t used_heap;
    uint32_t free_heap;
    uint32_t peak_usage;
    uint32_t alloc_count;
    uint32_t free_count;
    bool initialized;
} memory_monitor;

// 内存块头部
typedef struct MemBlock {
    size_t size;
    struct MemBlock *next;
    uint32_t magic;  // 用于检测内存损坏
} MemBlock_t;

#define MEM_MAGIC 0xDEADBEEF

// 内存块链表
static MemBlock_t *mem_list_head = NULL;

/**
 * @brief 初始化内存监控
 */
void Perf_Memory_Init(uint32_t heap_size) {
    memory_monitor.total_heap = heap_size;
    memory_monitor.used_heap = 0;
    memory_monitor.free_heap = heap_size;
    memory_monitor.peak_usage = 0;
    memory_monitor.alloc_count = 0;
    memory_monitor.free_count = 0;
    memory_monitor.initialized = true;
    
    mem_list_head = NULL;
}

/**
 * @brief 包装的malloc函数
 */
void* Perf_Malloc(size_t size) {
    if (!memory_monitor.initialized) {
        return malloc(size);
    }
    
    // 分配额外空间存储头部
    size_t total_size = size + sizeof(MemBlock_t);
    MemBlock_t *block = (MemBlock_t*)malloc(total_size);
    
    if (block) {
        // 填充头部
        block->size = size;
        block->magic = MEM_MAGIC;
        block->next = mem_list_head;
        mem_list_head = block;
        
        // 更新统计
        memory_monitor.used_heap += size;
        memory_monitor.free_heap -= size;
        memory_monitor.alloc_count++;
        
        // 更新峰值
        if (memory_monitor.used_heap > memory_monitor.peak_usage) {
            memory_monitor.peak_usage = memory_monitor.used_heap;
        }
        
        // 返回用户数据指针
        return (void*)((uint8_t*)block + sizeof(MemBlock_t));
    }
    
    return NULL;
}

/**
 * @brief 包装的free函数
 */
void Perf_Free(void *ptr) {
    if (!ptr || !memory_monitor.initialized) {
        free(ptr);
        return;
    }
    
    // 获取块头部
    MemBlock_t *block = (MemBlock_t*)((uint8_t*)ptr - sizeof(MemBlock_t));
    
    // 检查魔数
    if (block->magic != MEM_MAGIC) {
        // 内存损坏
        return;
    }
    
    // 从链表中移除
    MemBlock_t **current = &mem_list_head;
    while (*current) {
        if (*current == block) {
            *current = block->next;
            break;
        }
        current = &(*current)->next;
    }
    
    // 更新统计
    memory_monitor.used_heap -= block->size;
    memory_monitor.free_heap += block->size;
    memory_monitor.free_count++;
    
    // 释放内存
    free(block);
}

/**
 * @brief 更新内存监控数据
 */
void Perf_Memory_Update(void) {
    if (!memory_monitor.initialized) {
        return;
    }
    
    // 发送数据
    PerfMemoryData_t data = {
        .timestamp = HAL_GetTick(),
        .total_heap = memory_monitor.total_heap,
        .used_heap = memory_monitor.used_heap,
        .free_heap = memory_monitor.free_heap,
        .peak_usage = memory_monitor.peak_usage
    };
    
    Perf_SendData(PERF_TYPE_MEMORY, &data, sizeof(data));
}

/**
 * @brief 获取已用内存
 */
uint32_t Perf_Memory_GetUsed(void) {
    return memory_monitor.used_heap;
}

/**
 * @brief 获取空闲内存
 */
uint32_t Perf_Memory_GetFree(void) {
    return memory_monitor.free_heap;
}

/**
 * @brief 检测内存泄漏
 */
bool Perf_Memory_CheckLeaks(void) {
    return (memory_monitor.alloc_count != memory_monitor.free_count);
}
```

### 2.4 函数性能监控

**函数性能监控实现** (`perf_function.c`):

```c
#include "perf_monitor.h"
#include <string.h>

// 函数性能计数器数组
static PerfFunctionCounter_t function_counters[PERF_MAX_FUNCTIONS];
static int function_count = 0;

// 当前测量状态
typedef struct {
    int func_id;
    uint32_t start_cycles;
} PerfMeasureState_t;

static PerfMeasureState_t measure_stack[10];
static int measure_stack_top = 0;

/**
 * @brief 初始化函数性能监控
 */
void Perf_Function_Init(void) {
    memset(function_counters, 0, sizeof(function_counters));
    function_count = 0;
    measure_stack_top = 0;
}

/**
 * @brief 注册函数
 */
int Perf_Function_Register(const char *name) {
    if (function_count >= PERF_MAX_FUNCTIONS) {
        return -1;
    }
    
    // 检查是否已注册
    for (int i = 0; i < function_count; i++) {
        if (strcmp(function_counters[i].name, name) == 0) {
            return i;
        }
    }
    
    // 注册新函数
    int id = function_count++;
    function_counters[id].name = name;
    function_counters[id].func_id = id;
    function_counters[id].call_count = 0;
    function_counters[id].total_cycles = 0;
    function_counters[id].min_cycles = UINT32_MAX;
    function_counters[id].max_cycles = 0;
    function_counters[id].enabled = true;
    
    return id;
}

/**
 * @brief 开始测量函数
 */
void Perf_Function_Start(int func_id) {
    if (func_id < 0 || func_id >= function_count) {
        return;
    }
    
    if (!function_counters[func_id].enabled) {
        return;
    }
    
    // 压栈
    if (measure_stack_top < 10) {
        measure_stack[measure_stack_top].func_id = func_id;
        measure_stack[measure_stack_top].start_cycles = DWT_CYCCNT;
        measure_stack_top++;
    }
}

/**
 * @brief 结束测量函数
 */
void Perf_Function_End(int func_id) {
    if (func_id < 0 || func_id >= function_count) {
        return;
    }
    
    if (!function_counters[func_id].enabled) {
        return;
    }
    
    // 出栈
    if (measure_stack_top > 0) {
        measure_stack_top--;
        
        if (measure_stack[measure_stack_top].func_id == func_id) {
            uint32_t end_cycles = DWT_CYCCNT;
            uint32_t elapsed = end_cycles - measure_stack[measure_stack_top].start_cycles;
            
            // 更新统计
            PerfFunctionCounter_t *counter = &function_counters[func_id];
            counter->call_count++;
            counter->total_cycles += elapsed;
            
            if (elapsed < counter->min_cycles) {
                counter->min_cycles = elapsed;
            }
            if (elapsed > counter->max_cycles) {
                counter->max_cycles = elapsed;
            }
        }
    }
}

/**
 * @brief 获取函数统计信息
 */
void Perf_Function_GetStats(int func_id, PerfFunctionCounter_t *stats) {
    if (func_id < 0 || func_id >= function_count || !stats) {
        return;
    }
    
    memcpy(stats, &function_counters[func_id], sizeof(PerfFunctionCounter_t));
}

/**
 * @brief 发送所有函数统计数据
 */
void Perf_Function_SendAll(void) {
    for (int i = 0; i < function_count; i++) {
        if (function_counters[i].call_count > 0) {
            // 计算平均值
            uint32_t avg_cycles = function_counters[i].total_cycles / 
                                 function_counters[i].call_count;
            
            // 构造数据包
            typedef struct {
                uint32_t timestamp;
                uint16_t func_id;
                char func_name[32];
                uint32_t call_count;
                uint32_t total_cycles;
                uint32_t min_cycles;
                uint32_t max_cycles;
                uint32_t avg_cycles;
            } FunctionPerfData_t;
            
            FunctionPerfData_t data = {
                .timestamp = HAL_GetTick(),
                .func_id = i,
                .call_count = function_counters[i].call_count,
                .total_cycles = function_counters[i].total_cycles,
                .min_cycles = function_counters[i].min_cycles,
                .max_cycles = function_counters[i].max_cycles,
                .avg_cycles = avg_cycles
            };
            
            strncpy(data.func_name, function_counters[i].name, 31);
            data.func_name[31] = '\0';
            
            Perf_SendData(PERF_TYPE_FUNCTION, &data, sizeof(data));
        }
    }
}

/**
 * @brief 重置函数统计
 */
void Perf_Function_Reset(int func_id) {
    if (func_id < 0) {
        // 重置所有
        for (int i = 0; i < function_count; i++) {
            function_counters[i].call_count = 0;
            function_counters[i].total_cycles = 0;
            function_counters[i].min_cycles = UINT32_MAX;
            function_counters[i].max_cycles = 0;
        }
    } else if (func_id < function_count) {
        // 重置指定函数
        function_counters[func_id].call_count = 0;
        function_counters[func_id].total_cycles = 0;
        function_counters[func_id].min_cycles = UINT32_MAX;
        function_counters[func_id].max_cycles = 0;
    }
}
```



### 2.5 数据通信协议

**通信协议实现** (`perf_comm.c`):

```c
#include "perf_monitor.h"
#include <string.h>

// 协议定义
#define PERF_HEADER  0xAA55
#define PERF_TAIL    0x0D

// 数据包结构
typedef struct __attribute__((packed)) {
    uint16_t header;
    uint16_t length;
    uint8_t  type;
    uint8_t  data[256];
    uint16_t crc;
    uint8_t  tail;
} PerfPacket_t;

// 发送回调
static void (*send_callback)(uint8_t *data, uint16_t len) = NULL;

/**
 * @brief 计算CRC16
 */
static uint16_t Calculate_CRC16(uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    
    return crc;
}

/**
 * @brief 设置发送回调
 */
void Perf_Comm_SetCallback(void (*callback)(uint8_t *data, uint16_t len)) {
    send_callback = callback;
}

/**
 * @brief 发送性能数据
 */
void Perf_SendData(PerfDataType_t type, void *data, uint16_t len) {
    if (!send_callback || len > 256) {
        return;
    }
    
    PerfPacket_t packet;
    
    // 填充包头
    packet.header = PERF_HEADER;
    packet.length = len;
    packet.type = type;
    
    // 复制数据
    memcpy(packet.data, data, len);
    
    // 计算CRC (header + length + type + data)
    uint8_t *crc_data = (uint8_t*)&packet;
    uint16_t crc_len = 5 + len;  // 2(header) + 2(length) + 1(type) + len
    packet.crc = Calculate_CRC16(crc_data, crc_len);
    
    // 填充包尾
    packet.tail = PERF_TAIL;
    
    // 发送数据包
    uint16_t packet_len = 5 + len + 3;  // header+length+type+data+crc+tail
    send_callback((uint8_t*)&packet, packet_len);
}

/**
 * @brief 串口发送回调实现示例
 */
void UART_SendCallback(uint8_t *data, uint16_t len) {
    // 使用HAL库发送
    HAL_UART_Transmit(&huart1, data, len, 100);
}
```

### 2.6 主监控模块

**主监控模块实现** (`perf_monitor.c`):

```c
#include "perf_monitor.h"
#include <string.h>

// 监控配置
static PerfMonitorConfig_t monitor_config;
static bool monitor_running = false;
static uint32_t last_update_time = 0;

/**
 * @brief 初始化性能监控
 */
void Perf_Init(PerfMonitorConfig_t *config) {
    if (!config) {
        return;
    }
    
    // 保存配置
    memcpy(&monitor_config, config, sizeof(PerfMonitorConfig_t));
    
    // 初始化各模块
    if (monitor_config.cpu_monitor_enabled) {
        Perf_CPU_Init();
    }
    
    if (monitor_config.memory_monitor_enabled) {
        Perf_Memory_Init(64 * 1024);  // 假设64KB堆
    }
    
    if (monitor_config.function_monitor_enabled) {
        Perf_Function_Init();
    }
    
    // 设置通信回调
    if (monitor_config.send_callback) {
        Perf_Comm_SetCallback(monitor_config.send_callback);
    }
    
    last_update_time = HAL_GetTick();
}

/**
 * @brief 启动性能监控
 */
void Perf_Start(void) {
    monitor_running = true;
}

/**
 * @brief 停止性能监控
 */
void Perf_Stop(void) {
    monitor_running = false;
}

/**
 * @brief 重置性能监控
 */
void Perf_Reset(void) {
    if (monitor_config.function_monitor_enabled) {
        Perf_Function_Reset(-1);  // 重置所有函数
    }
    
    last_update_time = HAL_GetTick();
}

/**
 * @brief 性能监控更新
 * 
 * 应在主循环或定时器中周期性调用
 */
void Perf_Update(void) {
    if (!monitor_running) {
        return;
    }
    
    uint32_t current_time = HAL_GetTick();
    uint32_t elapsed = current_time - last_update_time;
    
    if (elapsed >= monitor_config.sample_interval_ms) {
        // 更新CPU监控
        if (monitor_config.cpu_monitor_enabled) {
            Perf_CPU_Update();
        }
        
        // 更新内存监控
        if (monitor_config.memory_monitor_enabled) {
            Perf_Memory_Update();
        }
        
        // 发送函数性能数据
        if (monitor_config.function_monitor_enabled) {
            Perf_Function_SendAll();
        }
        
        last_update_time = current_time;
    }
}
```

### 2.7 使用示例

**示例代码** (`main.c`):

```c
#include "perf_monitor.h"

// 外部UART句柄
extern UART_HandleTypeDef huart1;

// 串口发送回调
void UART_SendData(uint8_t *data, uint16_t len) {
    HAL_UART_Transmit(&huart1, data, len, 100);
}

// 测试函数1
void TestFunction1(void) {
    PERF_MEASURE_START(TestFunction1);
    
    // 模拟工作
    for (volatile int i = 0; i < 10000; i++);
    
    PERF_MEASURE_END(TestFunction1);
}

// 测试函数2
void TestFunction2(void) {
    PERF_MEASURE_START(TestFunction2);
    
    // 模拟工作
    HAL_Delay(10);
    
    PERF_MEASURE_END(TestFunction2);
}

// 空闲任务(FreeRTOS)
void vApplicationIdleHook(void) {
    Perf_CPU_RecordIdle();
}

int main(void) {
    // 硬件初始化
    HAL_Init();
    SystemClock_Config();
    MX_UART1_Init();
    
    // 配置性能监控
    PerfMonitorConfig_t config = {
        .cpu_monitor_enabled = true,
        .memory_monitor_enabled = true,
        .task_monitor_enabled = false,
        .function_monitor_enabled = true,
        .sample_interval_ms = 100,
        .send_callback = UART_SendData
    };
    
    // 初始化性能监控
    Perf_Init(&config);
    Perf_Start();
    
    // 主循环
    while (1) {
        // 更新性能监控
        Perf_Update();
        
        // 调用测试函数
        TestFunction1();
        TestFunction2();
        
        // 使用监控的内存分配
        void *ptr = Perf_Malloc(100);
        if (ptr) {
            // 使用内存
            Perf_Free(ptr);
        }
        
        HAL_Delay(50);
    }
}
```



## 步骤3: 主机端数据接收与解析

### 3.1 数据接收模块

**数据接收器** (`data_receiver.py`):

```python
import serial
import threading
import queue
import struct
import logging
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass
class PerfPacket:
    """性能数据包"""
    header: int
    length: int
    type: int
    data: bytes
    crc: int
    tail: int
    timestamp: float  # 接收时间戳

class DataReceiver:
    """数据接收器"""
    
    # 数据类型
    TYPE_CPU = 0x01
    TYPE_MEMORY = 0x02
    TYPE_TASK = 0x03
    TYPE_FUNCTION = 0x04
    TYPE_INTERRUPT = 0x05
    TYPE_CUSTOM = 0x06
    
    def __init__(self, port: str, baudrate: int = 115200):
        """
        初始化数据接收器
        
        Args:
            port: 串口名称
            baudrate: 波特率
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.rx_thread: Optional[threading.Thread] = None
        self.packet_queue = queue.Queue()
        self.callbacks = {}
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.stats = {
            'packets_received': 0,
            'packets_valid': 0,
            'packets_invalid': 0,
            'crc_errors': 0,
            'bytes_received': 0
        }
    
    def open(self) -> bool:
        """打开串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            self.logger.info(f"串口 {self.port} 打开成功")
            return True
        except serial.SerialException as e:
            self.logger.error(f"打开串口失败: {e}")
            return False
    
    def close(self):
        """关闭串口"""
        self.stop()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.logger.info("串口已关闭")
    
    def start(self):
        """启动接收线程"""
        if not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未打开")
            return
        
        self.running = True
        self.rx_thread = threading.Thread(target=self._rx_thread_func, daemon=True)
        self.rx_thread.start()
        self.logger.info("接收线程已启动")
    
    def stop(self):
        """停止接收线程"""
        self.running = False
        if self.rx_thread:
            self.rx_thread.join(timeout=2.0)
            self.logger.info("接收线程已停止")
    
    def register_callback(self, data_type: int, callback: Callable):
        """
        注册数据类型回调
        
        Args:
            data_type: 数据类型
            callback: 回调函数
        """
        self.callbacks[data_type] = callback
    
    def get_packet(self, timeout: float = 0.1) -> Optional[PerfPacket]:
        """
        从队列获取数据包
        
        Args:
            timeout: 超时时间(秒)
            
        Returns:
            数据包或None
        """
        try:
            return self.packet_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _calculate_crc16(self, data: bytes) -> int:
        """计算CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _parse_packet(self, buffer: bytes) -> Optional[PerfPacket]:
        """
        解析数据包
        
        Args:
            buffer: 数据缓冲区
            
        Returns:
            解析的数据包或None
        """
        if len(buffer) < 8:  # 最小包长度
            return None
        
        try:
            # 查找包头
            header_pos = buffer.find(b'\x55\xAA')
            if header_pos == -1:
                return None
            
            buffer = buffer[header_pos:]
            
            # 解析包头
            header = struct.unpack('<H', buffer[0:2])[0]
            length = struct.unpack('<H', buffer[2:4])[0]
            data_type = buffer[4]
            
            # 检查长度
            packet_len = 5 + length + 3  # header+length+type+data+crc+tail
            if len(buffer) < packet_len:
                return None
            
            # 提取数据
            data = buffer[5:5+length]
            crc_received = struct.unpack('<H', buffer[5+length:7+length])[0]
            tail = buffer[7+length]
            
            # 验证CRC
            crc_data = buffer[0:5+length]
            crc_calculated = self._calculate_crc16(crc_data)
            
            if crc_received != crc_calculated:
                self.stats['crc_errors'] += 1
                self.logger.warning(f"CRC错误: 接收={crc_received:04X}, 计算={crc_calculated:04X}")
                return None
            
            # 验证包尾
            if tail != 0x0D:
                self.logger.warning(f"包尾错误: {tail:02X}")
                return None
            
            # 创建数据包
            import time
            packet = PerfPacket(
                header=header,
                length=length,
                type=data_type,
                data=data,
                crc=crc_received,
                tail=tail,
                timestamp=time.time()
            )
            
            self.stats['packets_valid'] += 1
            return packet
            
        except Exception as e:
            self.logger.error(f"解析数据包失败: {e}")
            self.stats['packets_invalid'] += 1
            return None
    
    def _rx_thread_func(self):
        """接收线程函数"""
        buffer = bytearray()
        
        while self.running:
            try:
                # 读取数据
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)
                    self.stats['bytes_received'] += len(data)
                    
                    # 解析数据包
                    while len(buffer) >= 8:
                        packet = self._parse_packet(bytes(buffer))
                        
                        if packet:
                            # 放入队列
                            self.packet_queue.put(packet)
                            self.stats['packets_received'] += 1
                            
                            # 调用回调
                            if packet.type in self.callbacks:
                                self.callbacks[packet.type](packet)
                            
                            # 移除已处理的数据
                            packet_len = 5 + packet.length + 3
                            buffer = buffer[packet_len:]
                        else:
                            # 移除第一个字节，继续查找
                            if len(buffer) > 0:
                                buffer = buffer[1:]
                            break
                
            except Exception as e:
                self.logger.error(f"接收线程错误: {e}")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()
```

### 3.2 数据解析模块

**数据解析器** (`data_parser.py`):

```python
import struct
from dataclasses import dataclass
from typing import Optional
import logging

@dataclass
class CPUData:
    """CPU性能数据"""
    timestamp: int
    cpu_usage: int
    idle_time: int
    total_time: int

@dataclass
class MemoryData:
    """内存性能数据"""
    timestamp: int
    total_heap: int
    used_heap: int
    free_heap: int
    peak_usage: int

@dataclass
class FunctionData:
    """函数性能数据"""
    timestamp: int
    func_id: int
    func_name: str
    call_count: int
    total_cycles: int
    min_cycles: int
    max_cycles: int
    avg_cycles: int

class DataParser:
    """数据解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_cpu_data(self, data: bytes) -> Optional[CPUData]:
        """
        解析CPU数据
        
        Args:
            data: 原始数据
            
        Returns:
            CPU数据对象
        """
        try:
            if len(data) < 13:
                return None
            
            timestamp, cpu_usage, idle_time, total_time = struct.unpack('<IBII', data)
            
            return CPUData(
                timestamp=timestamp,
                cpu_usage=cpu_usage,
                idle_time=idle_time,
                total_time=total_time
            )
        except Exception as e:
            self.logger.error(f"解析CPU数据失败: {e}")
            return None
    
    def parse_memory_data(self, data: bytes) -> Optional[MemoryData]:
        """
        解析内存数据
        
        Args:
            data: 原始数据
            
        Returns:
            内存数据对象
        """
        try:
            if len(data) < 20:
                return None
            
            timestamp, total_heap, used_heap, free_heap, peak_usage = \
                struct.unpack('<IIIII', data)
            
            return MemoryData(
                timestamp=timestamp,
                total_heap=total_heap,
                used_heap=used_heap,
                free_heap=free_heap,
                peak_usage=peak_usage
            )
        except Exception as e:
            self.logger.error(f"解析内存数据失败: {e}")
            return None
    
    def parse_function_data(self, data: bytes) -> Optional[FunctionData]:
        """
        解析函数性能数据
        
        Args:
            data: 原始数据
            
        Returns:
            函数数据对象
        """
        try:
            if len(data) < 58:
                return None
            
            # 解析固定部分
            timestamp, func_id = struct.unpack('<IH', data[0:6])
            func_name = data[6:38].decode('utf-8', errors='ignore').rstrip('\x00')
            call_count, total_cycles, min_cycles, max_cycles, avg_cycles = \
                struct.unpack('<IIIII', data[38:58])
            
            return FunctionData(
                timestamp=timestamp,
                func_id=func_id,
                func_name=func_name,
                call_count=call_count,
                total_cycles=total_cycles,
                min_cycles=min_cycles,
                max_cycles=max_cycles,
                avg_cycles=avg_cycles
            )
        except Exception as e:
            self.logger.error(f"解析函数数据失败: {e}")
            return None
```



### 3.3 数据存储模块

**数据存储器** (`data_storage.py`):

```python
import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

class DataStorage:
    """数据存储器"""
    
    def __init__(self, db_path: str = "performance_data.db"):
        """
        初始化数据存储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # 创建CPU数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    cpu_usage INTEGER,
                    idle_time INTEGER,
                    total_time INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建内存数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    total_heap INTEGER,
                    used_heap INTEGER,
                    free_heap INTEGER,
                    peak_usage INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建函数性能表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS function_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    func_id INTEGER,
                    func_name TEXT,
                    call_count INTEGER,
                    total_cycles INTEGER,
                    min_cycles INTEGER,
                    max_cycles INTEGER,
                    avg_cycles INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    description TEXT,
                    metadata TEXT
                )
            ''')
            
            self.conn.commit()
            self.logger.info("数据库初始化成功")
            
        except sqlite3.Error as e:
            self.logger.error(f"数据库初始化失败: {e}")
    
    def save_cpu_data(self, data: 'CPUData'):
        """保存CPU数据"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO cpu_data (timestamp, cpu_usage, idle_time, total_time)
                VALUES (?, ?, ?, ?)
            ''', (data.timestamp, data.cpu_usage, data.idle_time, data.total_time))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"保存CPU数据失败: {e}")
    
    def save_memory_data(self, data: 'MemoryData'):
        """保存内存数据"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO memory_data 
                (timestamp, total_heap, used_heap, free_heap, peak_usage)
                VALUES (?, ?, ?, ?, ?)
            ''', (data.timestamp, data.total_heap, data.used_heap, 
                  data.free_heap, data.peak_usage))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"保存内存数据失败: {e}")
    
    def save_function_data(self, data: 'FunctionData'):
        """保存函数性能数据"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO function_data 
                (timestamp, func_id, func_name, call_count, total_cycles,
                 min_cycles, max_cycles, avg_cycles)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data.timestamp, data.func_id, data.func_name, data.call_count,
                  data.total_cycles, data.min_cycles, data.max_cycles, data.avg_cycles))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"保存函数数据失败: {e}")
    
    def query_cpu_data(self, start_time: int = 0, end_time: int = None, 
                       limit: int = 1000) -> List[Dict[str, Any]]:
        """
        查询CPU数据
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 最大记录数
            
        Returns:
            数据列表
        """
        try:
            cursor = self.conn.cursor()
            
            if end_time:
                cursor.execute('''
                    SELECT * FROM cpu_data 
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (start_time, end_time, limit))
            else:
                cursor.execute('''
                    SELECT * FROM cpu_data 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (start_time, limit))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"查询CPU数据失败: {e}")
            return []
    
    def query_memory_data(self, start_time: int = 0, end_time: int = None,
                          limit: int = 1000) -> List[Dict[str, Any]]:
        """查询内存数据"""
        try:
            cursor = self.conn.cursor()
            
            if end_time:
                cursor.execute('''
                    SELECT * FROM memory_data 
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (start_time, end_time, limit))
            else:
                cursor.execute('''
                    SELECT * FROM memory_data 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (start_time, limit))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"查询内存数据失败: {e}")
            return []
    
    def query_function_data(self, func_name: str = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """查询函数性能数据"""
        try:
            cursor = self.conn.cursor()
            
            if func_name:
                cursor.execute('''
                    SELECT * FROM function_data 
                    WHERE func_name = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (func_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM function_data 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"查询函数数据失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            
            # CPU统计
            cursor.execute('SELECT COUNT(*), AVG(cpu_usage), MAX(cpu_usage) FROM cpu_data')
            row = cursor.fetchone()
            stats['cpu'] = {
                'count': row[0],
                'avg_usage': row[1],
                'max_usage': row[2]
            }
            
            # 内存统计
            cursor.execute('SELECT COUNT(*), AVG(used_heap), MAX(peak_usage) FROM memory_data')
            row = cursor.fetchone()
            stats['memory'] = {
                'count': row[0],
                'avg_used': row[1],
                'peak_usage': row[2]
            }
            
            # 函数统计
            cursor.execute('SELECT COUNT(DISTINCT func_name) FROM function_data')
            stats['functions'] = {
                'unique_count': cursor.fetchone()[0]
            }
            
            return stats
            
        except sqlite3.Error as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def clear_data(self, table: str = None):
        """
        清空数据
        
        Args:
            table: 表名，None表示清空所有表
        """
        try:
            cursor = self.conn.cursor()
            
            if table:
                cursor.execute(f'DELETE FROM {table}')
            else:
                cursor.execute('DELETE FROM cpu_data')
                cursor.execute('DELETE FROM memory_data')
                cursor.execute('DELETE FROM function_data')
            
            self.conn.commit()
            self.logger.info(f"数据已清空: {table or '所有表'}")
            
        except sqlite3.Error as e:
            self.logger.error(f"清空数据失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.logger.info("数据库连接已关闭")
```



## 步骤4: 数据可视化实现

### 4.1 实时图表绘制

**实时图表类** (`realtime_chart.py`):

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np
from typing import List, Tuple
import logging

class RealtimeChart:
    """实时图表"""
    
    def __init__(self, title: str, ylabel: str, max_points: int = 100):
        """
        初始化实时图表
        
        Args:
            title: 图表标题
            ylabel: Y轴标签
            max_points: 最大数据点数
        """
        self.title = title
        self.ylabel = ylabel
        self.max_points = max_points
        
        # 数据缓冲区
        self.time_data = deque(maxlen=max_points)
        self.value_data = deque(maxlen=max_points)
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        
        # 配置图表
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel('时间 (s)', fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        self.logger = logging.getLogger(__name__)
    
    def add_data(self, time: float, value: float):
        """
        添加数据点
        
        Args:
            time: 时间
            value: 值
        """
        self.time_data.append(time)
        self.value_data.append(value)
    
    def update(self, frame):
        """更新图表"""
        if len(self.time_data) > 0:
            self.line.set_data(list(self.time_data), list(self.value_data))
            
            # 自动调整坐标轴
            self.ax.relim()
            self.ax.autoscale_view()
        
        return self.line,
    
    def start(self, interval: int = 100):
        """
        启动动画
        
        Args:
            interval: 更新间隔(ms)
        """
        self.anim = FuncAnimation(
            self.fig, 
            self.update, 
            interval=interval,
            blit=True
        )
        plt.show()
    
    def save(self, filename: str):
        """保存图表"""
        self.fig.savefig(filename, dpi=300, bbox_inches='tight')
        self.logger.info(f"图表已保存: {filename}")

class MultiLineChart:
    """多线图表"""
    
    def __init__(self, title: str, ylabel: str, 
                 line_labels: List[str], max_points: int = 100):
        """
        初始化多线图表
        
        Args:
            title: 图表标题
            ylabel: Y轴标签
            line_labels: 线条标签列表
            max_points: 最大数据点数
        """
        self.title = title
        self.ylabel = ylabel
        self.line_labels = line_labels
        self.max_points = max_points
        
        # 数据缓冲区
        self.time_data = deque(maxlen=max_points)
        self.value_data = {label: deque(maxlen=max_points) 
                          for label in line_labels}
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        
        # 创建线条
        colors = ['b', 'r', 'g', 'orange', 'purple']
        self.lines = {}
        for i, label in enumerate(line_labels):
            color = colors[i % len(colors)]
            line, = self.ax.plot([], [], color=color, linewidth=2, label=label)
            self.lines[label] = line
        
        # 配置图表
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel('时间 (s)', fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.legend(loc='upper right')
        self.ax.grid(True, alpha=0.3)
        
        self.logger = logging.getLogger(__name__)
    
    def add_data(self, time: float, values: dict):
        """
        添加数据点
        
        Args:
            time: 时间
            values: 值字典 {label: value}
        """
        self.time_data.append(time)
        for label, value in values.items():
            if label in self.value_data:
                self.value_data[label].append(value)
    
    def update(self, frame):
        """更新图表"""
        if len(self.time_data) > 0:
            time_list = list(self.time_data)
            
            for label, line in self.lines.items():
                value_list = list(self.value_data[label])
                line.set_data(time_list, value_list)
            
            # 自动调整坐标轴
            self.ax.relim()
            self.ax.autoscale_view()
        
        return list(self.lines.values())
    
    def start(self, interval: int = 100):
        """启动动画"""
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            interval=interval,
            blit=True
        )
        plt.show()
```

### 4.2 统计图表

**统计图表类** (`histogram.py`):

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
import logging

class PerformanceHistogram:
    """性能直方图"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def plot_function_performance(self, function_data: List[Dict[str, Any]],
                                  top_n: int = 10):
        """
        绘制函数性能对比图
        
        Args:
            function_data: 函数性能数据列表
            top_n: 显示前N个函数
        """
        if not function_data:
            self.logger.warning("没有函数数据")
            return
        
        # 按平均执行时间排序
        sorted_data = sorted(function_data, 
                           key=lambda x: x['avg_cycles'], 
                           reverse=True)[:top_n]
        
        func_names = [d['func_name'] for d in sorted_data]
        avg_cycles = [d['avg_cycles'] for d in sorted_data]
        call_counts = [d['call_count'] for d in sorted_data]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 平均执行时间
        bars1 = ax1.barh(func_names, avg_cycles, color='steelblue')
        ax1.set_xlabel('平均周期数', fontsize=12)
        ax1.set_title('函数平均执行时间 (Top 10)', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # 添加数值标签
        for bar in bars1:
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=10)
        
        # 调用次数
        bars2 = ax2.barh(func_names, call_counts, color='coral')
        ax2.set_xlabel('调用次数', fontsize=12)
        ax2.set_title('函数调用次数 (Top 10)', fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 添加数值标签
        for bar in bars2:
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.show()
    
    def plot_memory_usage(self, memory_data: List[Dict[str, Any]]):
        """
        绘制内存使用情况
        
        Args:
            memory_data: 内存数据列表
        """
        if not memory_data:
            self.logger.warning("没有内存数据")
            return
        
        # 提取数据
        timestamps = [d['timestamp'] / 1000.0 for d in memory_data]  # 转换为秒
        used_heap = [d['used_heap'] / 1024 for d in memory_data]  # 转换为KB
        free_heap = [d['free_heap'] / 1024 for d in memory_data]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 堆叠面积图
        ax.fill_between(timestamps, 0, used_heap, 
                        alpha=0.6, color='steelblue', label='已用内存')
        ax.fill_between(timestamps, used_heap, 
                        [u + f for u, f in zip(used_heap, free_heap)],
                        alpha=0.6, color='lightgreen', label='空闲内存')
        
        ax.set_xlabel('时间 (s)', fontsize=12)
        ax.set_ylabel('内存 (KB)', fontsize=12)
        ax.set_title('内存使用情况', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_cpu_usage_distribution(self, cpu_data: List[Dict[str, Any]]):
        """
        绘制CPU使用率分布
        
        Args:
            cpu_data: CPU数据列表
        """
        if not cpu_data:
            self.logger.warning("没有CPU数据")
            return
        
        # 提取CPU使用率
        cpu_usage = [d['cpu_usage'] for d in cpu_data]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 直方图
        ax1.hist(cpu_usage, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('CPU使用率 (%)', fontsize=12)
        ax1.set_ylabel('频次', fontsize=12)
        ax1.set_title('CPU使用率分布', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 箱线图
        ax2.boxplot(cpu_usage, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue'))
        ax2.set_ylabel('CPU使用率 (%)', fontsize=12)
        ax2.set_title('CPU使用率统计', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # 添加统计信息
        stats_text = f'平均: {np.mean(cpu_usage):.1f}%\n'
        stats_text += f'中位数: {np.median(cpu_usage):.1f}%\n'
        stats_text += f'最大: {np.max(cpu_usage):.1f}%\n'
        stats_text += f'最小: {np.min(cpu_usage):.1f}%'
        ax2.text(1.15, 0.5, stats_text, transform=ax2.transAxes,
                fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()
```



## 步骤5: 性能分析算法

### 5.1 性能分析器

**性能分析器** (`data_analyzer.py`):

```python
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

@dataclass
class PerformanceIssue:
    """性能问题"""
    severity: str  # 'critical', 'warning', 'info'
    category: str  # 'cpu', 'memory', 'function'
    description: str
    recommendation: str
    data: Dict[str, Any]

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 阈值配置
        self.thresholds = {
            'cpu_high': 80,  # CPU使用率高阈值
            'cpu_critical': 95,  # CPU使用率临界阈值
            'memory_high': 80,  # 内存使用率高阈值
            'memory_critical': 95,  # 内存使用率临界阈值
            'function_slow': 10000,  # 函数慢阈值(周期数)
        }
    
    def analyze_cpu_usage(self, cpu_data: List[Dict[str, Any]]) -> List[PerformanceIssue]:
        """
        分析CPU使用情况
        
        Args:
            cpu_data: CPU数据列表
            
        Returns:
            性能问题列表
        """
        issues = []
        
        if not cpu_data:
            return issues
        
        # 提取CPU使用率
        cpu_usage = [d['cpu_usage'] for d in cpu_data]
        
        # 计算统计信息
        avg_usage = np.mean(cpu_usage)
        max_usage = np.max(cpu_usage)
        std_usage = np.std(cpu_usage)
        
        # 检查平均使用率
        if avg_usage > self.thresholds['cpu_critical']:
            issues.append(PerformanceIssue(
                severity='critical',
                category='cpu',
                description=f'CPU平均使用率过高: {avg_usage:.1f}%',
                recommendation='考虑优化算法或降低任务频率',
                data={'avg_usage': avg_usage, 'max_usage': max_usage}
            ))
        elif avg_usage > self.thresholds['cpu_high']:
            issues.append(PerformanceIssue(
                severity='warning',
                category='cpu',
                description=f'CPU平均使用率较高: {avg_usage:.1f}%',
                recommendation='建议进行性能优化',
                data={'avg_usage': avg_usage, 'max_usage': max_usage}
            ))
        
        # 检查峰值使用率
        if max_usage > self.thresholds['cpu_critical']:
            issues.append(PerformanceIssue(
                severity='critical',
                category='cpu',
                description=f'CPU峰值使用率达到: {max_usage:.1f}%',
                recommendation='检查是否有突发性高负载任务',
                data={'max_usage': max_usage}
            ))
        
        # 检查使用率波动
        if std_usage > 20:
            issues.append(PerformanceIssue(
                severity='info',
                category='cpu',
                description=f'CPU使用率波动较大: 标准差={std_usage:.1f}%',
                recommendation='考虑负载均衡或任务调度优化',
                data={'std_usage': std_usage}
            ))
        
        return issues
    
    def analyze_memory_usage(self, memory_data: List[Dict[str, Any]]) -> List[PerformanceIssue]:
        """
        分析内存使用情况
        
        Args:
            memory_data: 内存数据列表
            
        Returns:
            性能问题列表
        """
        issues = []
        
        if not memory_data:
            return issues
        
        # 计算内存使用率
        usage_rates = []
        for d in memory_data:
            if d['total_heap'] > 0:
                rate = (d['used_heap'] / d['total_heap']) * 100
                usage_rates.append(rate)
        
        if not usage_rates:
            return issues
        
        # 统计信息
        avg_usage = np.mean(usage_rates)
        max_usage = np.max(usage_rates)
        peak_usage = memory_data[-1]['peak_usage']
        total_heap = memory_data[-1]['total_heap']
        peak_rate = (peak_usage / total_heap) * 100 if total_heap > 0 else 0
        
        # 检查平均使用率
        if avg_usage > self.thresholds['memory_critical']:
            issues.append(PerformanceIssue(
                severity='critical',
                category='memory',
                description=f'内存平均使用率过高: {avg_usage:.1f}%',
                recommendation='检查内存泄漏，优化内存使用',
                data={'avg_usage': avg_usage, 'peak_rate': peak_rate}
            ))
        elif avg_usage > self.thresholds['memory_high']:
            issues.append(PerformanceIssue(
                severity='warning',
                category='memory',
                description=f'内存平均使用率较高: {avg_usage:.1f}%',
                recommendation='考虑优化数据结构或增加内存',
                data={'avg_usage': avg_usage, 'peak_rate': peak_rate}
            ))
        
        # 检查峰值使用率
        if peak_rate > self.thresholds['memory_critical']:
            issues.append(PerformanceIssue(
                severity='critical',
                category='memory',
                description=f'内存峰值使用率: {peak_rate:.1f}%',
                recommendation='存在内存不足风险，需要优化',
                data={'peak_rate': peak_rate, 'peak_usage': peak_usage}
            ))
        
        # 检查内存增长趋势
        if len(usage_rates) > 10:
            # 简单线性回归检测趋势
            x = np.arange(len(usage_rates))
            y = np.array(usage_rates)
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.1:  # 增长趋势
                issues.append(PerformanceIssue(
                    severity='warning',
                    category='memory',
                    description='检测到内存使用持续增长',
                    recommendation='可能存在内存泄漏，建议检查',
                    data={'growth_rate': slope}
                ))
        
        return issues
    
    def analyze_function_performance(self, function_data: List[Dict[str, Any]]) -> List[PerformanceIssue]:
        """
        分析函数性能
        
        Args:
            function_data: 函数性能数据列表
            
        Returns:
            性能问题列表
        """
        issues = []
        
        if not function_data:
            return issues
        
        # 按函数分组
        func_stats = {}
        for d in function_data:
            func_name = d['func_name']
            if func_name not in func_stats:
                func_stats[func_name] = []
            func_stats[func_name].append(d)
        
        # 分析每个函数
        for func_name, data_list in func_stats.items():
            # 获取最新数据
            latest = data_list[-1]
            avg_cycles = latest['avg_cycles']
            max_cycles = latest['max_cycles']
            call_count = latest['call_count']
            
            # 检查执行时间
            if avg_cycles > self.thresholds['function_slow']:
                issues.append(PerformanceIssue(
                    severity='warning',
                    category='function',
                    description=f'函数 {func_name} 执行较慢: 平均{avg_cycles}周期',
                    recommendation='考虑优化算法或减少计算量',
                    data={
                        'func_name': func_name,
                        'avg_cycles': avg_cycles,
                        'max_cycles': max_cycles
                    }
                ))
            
            # 检查执行时间波动
            if max_cycles > avg_cycles * 3:
                issues.append(PerformanceIssue(
                    severity='info',
                    category='function',
                    description=f'函数 {func_name} 执行时间波动大',
                    recommendation='检查是否有条件分支导致性能差异',
                    data={
                        'func_name': func_name,
                        'avg_cycles': avg_cycles,
                        'max_cycles': max_cycles
                    }
                ))
            
            # 检查调用频率
            if call_count > 1000:
                issues.append(PerformanceIssue(
                    severity='info',
                    category='function',
                    description=f'函数 {func_name} 调用频繁: {call_count}次',
                    recommendation='如果性能有问题，优先优化此函数',
                    data={
                        'func_name': func_name,
                        'call_count': call_count
                    }
                ))
        
        return issues
    
    def generate_report(self, cpu_data: List[Dict[str, Any]],
                       memory_data: List[Dict[str, Any]],
                       function_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成性能分析报告
        
        Args:
            cpu_data: CPU数据
            memory_data: 内存数据
            function_data: 函数数据
            
        Returns:
            分析报告
        """
        report = {
            'summary': {},
            'issues': [],
            'recommendations': []
        }
        
        # CPU分析
        cpu_issues = self.analyze_cpu_usage(cpu_data)
        report['issues'].extend(cpu_issues)
        
        if cpu_data:
            cpu_usage = [d['cpu_usage'] for d in cpu_data]
            report['summary']['cpu'] = {
                'avg_usage': np.mean(cpu_usage),
                'max_usage': np.max(cpu_usage),
                'min_usage': np.min(cpu_usage),
                'std_usage': np.std(cpu_usage)
            }
        
        # 内存分析
        memory_issues = self.analyze_memory_usage(memory_data)
        report['issues'].extend(memory_issues)
        
        if memory_data:
            latest_mem = memory_data[-1]
            report['summary']['memory'] = {
                'total_heap': latest_mem['total_heap'],
                'used_heap': latest_mem['used_heap'],
                'free_heap': latest_mem['free_heap'],
                'peak_usage': latest_mem['peak_usage'],
                'usage_rate': (latest_mem['used_heap'] / latest_mem['total_heap'] * 100)
                              if latest_mem['total_heap'] > 0 else 0
            }
        
        # 函数分析
        function_issues = self.analyze_function_performance(function_data)
        report['issues'].extend(function_issues)
        
        if function_data:
            # 找出最慢的函数
            sorted_funcs = sorted(function_data, 
                                key=lambda x: x['avg_cycles'], 
                                reverse=True)[:5]
            report['summary']['top_slow_functions'] = [
                {
                    'name': f['func_name'],
                    'avg_cycles': f['avg_cycles'],
                    'call_count': f['call_count']
                }
                for f in sorted_funcs
            ]
        
        # 生成建议
        critical_issues = [i for i in report['issues'] if i.severity == 'critical']
        warning_issues = [i for i in report['issues'] if i.severity == 'warning']
        
        if critical_issues:
            report['recommendations'].append(
                '发现严重性能问题，需要立即处理'
            )
        if warning_issues:
            report['recommendations'].append(
                '存在性能警告，建议进行优化'
            )
        if not report['issues']:
            report['recommendations'].append(
                '系统性能良好，无明显问题'
            )
        
        return report
```



## 步骤6: 主程序集成

### 6.1 主程序

**主程序** (`main.py`):

```python
import sys
import time
import logging
from pathlib import Path

from core.data_receiver import DataReceiver
from core.data_parser import DataParser
from core.data_storage import DataStorage
from core.data_analyzer import PerformanceAnalyzer
from visualization.realtime_chart import RealtimeChart, MultiLineChart
from visualization.histogram import PerformanceHistogram

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_analyzer.log'),
        logging.StreamHandler()
    ]
)

class PerformanceAnalyzerApp:
    """性能分析工具主程序"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        """
        初始化应用
        
        Args:
            port: 串口名称
            baudrate: 波特率
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化模块
        self.receiver = DataReceiver(port, baudrate)
        self.parser = DataParser()
        self.storage = DataStorage()
        self.analyzer = PerformanceAnalyzer()
        
        # 实时图表
        self.cpu_chart = RealtimeChart('CPU使用率', 'CPU (%)')
        self.memory_chart = MultiLineChart(
            '内存使用情况', 
            '内存 (KB)',
            ['已用', '空闲']
        )
        
        # 统计图表
        self.histogram = PerformanceHistogram()
        
        # 数据缓存
        self.cpu_data_cache = []
        self.memory_data_cache = []
        self.function_data_cache = []
        
        # 起始时间
        self.start_time = time.time()
    
    def setup(self) -> bool:
        """设置应用"""
        # 打开串口
        if not self.receiver.open():
            self.logger.error("无法打开串口")
            return False
        
        # 注册回调
        self.receiver.register_callback(
            DataReceiver.TYPE_CPU,
            self._on_cpu_data
        )
        self.receiver.register_callback(
            DataReceiver.TYPE_MEMORY,
            self._on_memory_data
        )
        self.receiver.register_callback(
            DataReceiver.TYPE_FUNCTION,
            self._on_function_data
        )
        
        # 启动接收
        self.receiver.start()
        
        self.logger.info("应用设置完成")
        return True
    
    def _on_cpu_data(self, packet):
        """CPU数据回调"""
        data = self.parser.parse_cpu_data(packet.data)
        if data:
            # 保存到数据库
            self.storage.save_cpu_data(data)
            
            # 缓存数据
            self.cpu_data_cache.append({
                'timestamp': data.timestamp,
                'cpu_usage': data.cpu_usage,
                'idle_time': data.idle_time,
                'total_time': data.total_time
            })
            
            # 更新实时图表
            elapsed = time.time() - self.start_time
            self.cpu_chart.add_data(elapsed, data.cpu_usage)
            
            self.logger.debug(f"CPU使用率: {data.cpu_usage}%")
    
    def _on_memory_data(self, packet):
        """内存数据回调"""
        data = self.parser.parse_memory_data(packet.data)
        if data:
            # 保存到数据库
            self.storage.save_memory_data(data)
            
            # 缓存数据
            self.memory_data_cache.append({
                'timestamp': data.timestamp,
                'total_heap': data.total_heap,
                'used_heap': data.used_heap,
                'free_heap': data.free_heap,
                'peak_usage': data.peak_usage
            })
            
            # 更新实时图表
            elapsed = time.time() - self.start_time
            self.memory_chart.add_data(elapsed, {
                '已用': data.used_heap / 1024,
                '空闲': data.free_heap / 1024
            })
            
            self.logger.debug(f"内存使用: {data.used_heap}/{data.total_heap}")
    
    def _on_function_data(self, packet):
        """函数数据回调"""
        data = self.parser.parse_function_data(packet.data)
        if data:
            # 保存到数据库
            self.storage.save_function_data(data)
            
            # 缓存数据
            self.function_data_cache.append({
                'timestamp': data.timestamp,
                'func_id': data.func_id,
                'func_name': data.func_name,
                'call_count': data.call_count,
                'total_cycles': data.total_cycles,
                'min_cycles': data.min_cycles,
                'max_cycles': data.max_cycles,
                'avg_cycles': data.avg_cycles
            })
            
            self.logger.debug(f"函数 {data.func_name}: 平均{data.avg_cycles}周期")
    
    def run_realtime_monitor(self, duration: int = 60):
        """
        运行实时监控
        
        Args:
            duration: 监控时长(秒)
        """
        self.logger.info(f"开始实时监控，时长: {duration}秒")
        
        # 启动实时图表(在单独线程中)
        import threading
        
        def show_cpu_chart():
            self.cpu_chart.start(interval=100)
        
        def show_memory_chart():
            self.memory_chart.start(interval=100)
        
        cpu_thread = threading.Thread(target=show_cpu_chart, daemon=True)
        memory_thread = threading.Thread(target=show_memory_chart, daemon=True)
        
        cpu_thread.start()
        memory_thread.start()
        
        # 等待指定时长
        time.sleep(duration)
        
        self.logger.info("实时监控结束")
    
    def run_analysis(self):
        """运行性能分析"""
        self.logger.info("开始性能分析")
        
        # 生成分析报告
        report = self.analyzer.generate_report(
            self.cpu_data_cache,
            self.memory_data_cache,
            self.function_data_cache
        )
        
        # 打印报告
        print("\n" + "="*60)
        print("性能分析报告")
        print("="*60)
        
        # 摘要
        print("\n摘要:")
        if 'cpu' in report['summary']:
            cpu = report['summary']['cpu']
            print(f"  CPU使用率: 平均={cpu['avg_usage']:.1f}%, "
                  f"最大={cpu['max_usage']:.1f}%, "
                  f"最小={cpu['min_usage']:.1f}%")
        
        if 'memory' in report['summary']:
            mem = report['summary']['memory']
            print(f"  内存使用: {mem['used_heap']}/{mem['total_heap']} "
                  f"({mem['usage_rate']:.1f}%), "
                  f"峰值={mem['peak_usage']}")
        
        if 'top_slow_functions' in report['summary']:
            print("\n  最慢的5个函数:")
            for func in report['summary']['top_slow_functions']:
                print(f"    - {func['name']}: {func['avg_cycles']}周期 "
                      f"(调用{func['call_count']}次)")
        
        # 问题
        if report['issues']:
            print("\n发现的问题:")
            for issue in report['issues']:
                severity_icon = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'info': '🔵'
                }.get(issue.severity, '⚪')
                
                print(f"  {severity_icon} [{issue.severity.upper()}] "
                      f"{issue.description}")
                print(f"     建议: {issue.recommendation}")
        
        # 建议
        if report['recommendations']:
            print("\n总体建议:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        print("\n" + "="*60 + "\n")
        
        # 显示统计图表
        if self.function_data_cache:
            self.histogram.plot_function_performance(self.function_data_cache)
        
        if self.memory_data_cache:
            self.histogram.plot_memory_usage(self.memory_data_cache)
        
        if self.cpu_data_cache:
            self.histogram.plot_cpu_usage_distribution(self.cpu_data_cache)
    
    def cleanup(self):
        """清理资源"""
        self.receiver.close()
        self.storage.close()
        self.logger.info("资源已清理")

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python main.py <串口名称> [波特率]")
        print("示例: python main.py COM3 115200")
        sys.exit(1)
    
    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    # 创建应用
    app = PerformanceAnalyzerApp(port, baudrate)
    
    try:
        # 设置应用
        if not app.setup():
            sys.exit(1)
        
        # 运行实时监控
        print("正在监控性能数据...")
        print("按Ctrl+C停止监控并生成分析报告")
        
        # 持续监控
        while True:
            time.sleep(1)
            
            # 显示统计信息
            stats = app.receiver.get_stats()
            print(f"\r接收: {stats['packets_received']}包, "
                  f"有效: {stats['packets_valid']}包, "
                  f"CRC错误: {stats['crc_errors']}包", end='')
    
    except KeyboardInterrupt:
        print("\n\n停止监控...")
        
        # 运行分析
        app.run_analysis()
    
    finally:
        # 清理
        app.cleanup()

if __name__ == '__main__':
    main()
```

### 6.2 配置文件

**配置文件** (`config/analyzer.yaml`):

```yaml
# 性能分析工具配置

# 串口配置
serial:
  port: "COM3"  # Windows: COM3, Linux: /dev/ttyUSB0
  baudrate: 115200
  timeout: 1.0

# 数据采集配置
collection:
  sample_interval: 100  # 采样间隔(ms)
  buffer_size: 1024     # 缓冲区大小
  max_points: 1000      # 最大数据点数

# 分析配置
analysis:
  thresholds:
    cpu_high: 80        # CPU使用率高阈值(%)
    cpu_critical: 95    # CPU使用率临界阈值(%)
    memory_high: 80     # 内存使用率高阈值(%)
    memory_critical: 95 # 内存使用率临界阈值(%)
    function_slow: 10000  # 函数慢阈值(周期数)

# 可视化配置
visualization:
  realtime_update_interval: 100  # 实时图表更新间隔(ms)
  chart_max_points: 100          # 图表最大数据点数
  colors:
    cpu: "steelblue"
    memory_used: "coral"
    memory_free: "lightgreen"

# 存储配置
storage:
  database: "performance_data.db"
  auto_save: true
  save_interval: 10  # 自动保存间隔(秒)

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "performance_analyzer.log"
  max_size: 10485760  # 10MB
  backup_count: 5
```



## 步骤7: 测试与验证

### 7.1 单元测试

**测试数据解析** (`tests/test_parser.py`):

```python
import unittest
import struct
from core.data_parser import DataParser, CPUData, MemoryData, FunctionData

class TestDataParser(unittest.TestCase):
    """数据解析器测试"""
    
    def setUp(self):
        self.parser = DataParser()
    
    def test_parse_cpu_data(self):
        """测试CPU数据解析"""
        # 构造测试数据
        timestamp = 1000
        cpu_usage = 75
        idle_time = 25000
        total_time = 100000
        
        data = struct.pack('<IBII', timestamp, cpu_usage, idle_time, total_time)
        
        # 解析
        result = self.parser.parse_cpu_data(data)
        
        # 验证
        self.assertIsNotNone(result)
        self.assertEqual(result.timestamp, timestamp)
        self.assertEqual(result.cpu_usage, cpu_usage)
        self.assertEqual(result.idle_time, idle_time)
        self.assertEqual(result.total_time, total_time)
    
    def test_parse_memory_data(self):
        """测试内存数据解析"""
        # 构造测试数据
        timestamp = 2000
        total_heap = 65536
        used_heap = 32768
        free_heap = 32768
        peak_usage = 40000
        
        data = struct.pack('<IIIII', timestamp, total_heap, used_heap, 
                          free_heap, peak_usage)
        
        # 解析
        result = self.parser.parse_memory_data(data)
        
        # 验证
        self.assertIsNotNone(result)
        self.assertEqual(result.timestamp, timestamp)
        self.assertEqual(result.total_heap, total_heap)
        self.assertEqual(result.used_heap, used_heap)
        self.assertEqual(result.free_heap, free_heap)
        self.assertEqual(result.peak_usage, peak_usage)
    
    def test_parse_function_data(self):
        """测试函数数据解析"""
        # 构造测试数据
        timestamp = 3000
        func_id = 1
        func_name = b"test_function\x00" + b'\x00' * 19  # 32字节
        call_count = 100
        total_cycles = 50000
        min_cycles = 400
        max_cycles = 600
        avg_cycles = 500
        
        data = struct.pack('<IH', timestamp, func_id)
        data += func_name
        data += struct.pack('<IIIII', call_count, total_cycles, 
                           min_cycles, max_cycles, avg_cycles)
        
        # 解析
        result = self.parser.parse_function_data(data)
        
        # 验证
        self.assertIsNotNone(result)
        self.assertEqual(result.timestamp, timestamp)
        self.assertEqual(result.func_id, func_id)
        self.assertEqual(result.func_name, "test_function")
        self.assertEqual(result.call_count, call_count)
        self.assertEqual(result.avg_cycles, avg_cycles)

if __name__ == '__main__':
    unittest.main()
```

### 7.2 集成测试

**测试完整流程** (`tests/test_integration.py`):

```python
import unittest
import time
import threading
from core.data_receiver import DataReceiver
from core.data_parser import DataParser
from core.data_storage import DataStorage

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.storage = DataStorage(':memory:')  # 使用内存数据库
        self.parser = DataParser()
    
    def tearDown(self):
        self.storage.close()
    
    def test_data_flow(self):
        """测试数据流"""
        # 模拟CPU数据
        import struct
        cpu_data_raw = struct.pack('<IBII', 1000, 75, 25000, 100000)
        cpu_data = self.parser.parse_cpu_data(cpu_data_raw)
        
        # 保存到数据库
        self.storage.save_cpu_data(cpu_data)
        
        # 查询数据
        results = self.storage.query_cpu_data()
        
        # 验证
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['cpu_usage'], 75)
    
    def test_statistics(self):
        """测试统计功能"""
        # 添加多条数据
        import struct
        for i in range(10):
            cpu_data_raw = struct.pack('<IBII', i*1000, 50+i, 25000, 100000)
            cpu_data = self.parser.parse_cpu_data(cpu_data_raw)
            self.storage.save_cpu_data(cpu_data)
        
        # 获取统计
        stats = self.storage.get_statistics()
        
        # 验证
        self.assertEqual(stats['cpu']['count'], 10)
        self.assertGreater(stats['cpu']['avg_usage'], 0)

if __name__ == '__main__':
    unittest.main()
```

## 项目总结

### 完成的功能

通过本项目，我们实现了一个完整的嵌入式性能分析工具，包括:

- ✅ 嵌入式端数据采集系统
  - CPU使用率监控
  - 内存使用监控
  - 函数性能监控
  - 低开销的数据采集机制

- ✅ 主机端数据处理系统
  - 串口通信和数据接收
  - 数据包解析和验证
  - 数据存储和查询
  - 性能数据分析

- ✅ 可视化系统
  - 实时性能曲线图
  - 统计图表和分布图
  - 交互式数据展示

- ✅ 分析系统
  - 性能瓶颈识别
  - 智能问题检测
  - 优化建议生成

### 技术亮点

1. **低开销采集**: 使用DWT周期计数器，对系统性能影响小
2. **实时监控**: 支持实时数据采集和显示
3. **多维分析**: 从CPU、内存、函数多个维度分析性能
4. **智能诊断**: 自动识别性能问题并给出建议
5. **可扩展架构**: 模块化设计，易于扩展新功能

### 应用场景

- 嵌入式系统性能优化
- 实时系统调试
- 产品性能测试
- 系统资源监控
- 性能回归测试

### 扩展方向

**功能扩展**:
- 支持更多通信接口(网络、USB等)
- 添加任务调度分析
- 支持多设备同时监控
- 添加性能对比功能
- 实现远程监控

**界面扩展**:
- 开发Web界面
- 添加更多图表类型
- 支持自定义仪表盘
- 实现报警功能

**分析扩展**:
- 机器学习异常检测
- 性能预测
- 自动优化建议
- 性能基准测试

## 延伸阅读

### 相关文章

- [代码优化基础原则](../beginner/01-code-optimization-basics.html) - 优化基础
- [代码执行时间测量方法](../beginner/03-execution-time-measurement.html) - 时间测量
- [内存使用优化技术](../intermediate/01-memory-optimization.html) - 内存优化
- [实时性能优化技术](./01-real-time-optimization.html) - 实时优化

### 进阶主题

- [单元测试框架搭建](../../02-debugging-testing/advanced/01-unit-testing-framework.html) - 测试框架
- [HIL测试系统](../../02-debugging-testing/advanced/02-hil-testing-system.html) - 测试系统
- [CI/CD实践](../../01-development-tools/intermediate/03-cicd-practice.html) - 持续集成

### 参考资料

**工具和库**:
1. [Matplotlib](https://matplotlib.org/) - Python绘图库
2. [PySerial](https://pyserial.readthedocs.io/) - Python串口库
3. [SQLite](https://www.sqlite.org/) - 轻量级数据库
4. [NumPy](https://numpy.org/) - 数值计算库

**技术文档**:
1. [ARM DWT](https://developer.arm.com/documentation/) - ARM调试和追踪
2. [Cortex-M Performance](https://www.arm.com/products/silicon-ip-cpu/cortex-m) - Cortex-M性能
3. [Python Threading](https://docs.python.org/3/library/threading.html) - Python多线程

**开源项目**:
1. [Tracealyzer](https://percepio.com/tracealyzer/) - RTOS追踪工具
2. [SystemView](https://www.segger.com/products/development-tools/systemview/) - 系统分析工具
3. [Perfetto](https://perfetto.dev/) - 性能追踪工具

---

**项目交付物**:
- 完整的源代码
- 配置文件和文档
- 测试用例
- 使用说明
- 示例项目

**预计开发时间**: 180小时

**难度等级**: 高级

**适用人群**: 有嵌入式开发经验，熟悉Python编程，了解性能优化的开发者

