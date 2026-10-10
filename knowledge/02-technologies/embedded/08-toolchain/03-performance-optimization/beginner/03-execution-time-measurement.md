---
title: "代码执行时间测量方法：精确分析程序性能"
description: "全面介绍嵌入式系统中测量代码执行时间的各种方法，包括系统时钟、硬件计时器、DWT周期计数器、性能分析工具等，帮助开发者准确评估和优化程序性能"
slug: "execution-time-measurement"

# 分类信息
domain: "工具链"
module: "性能优化"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 时间测量
  - 性能分析
  - Profiling
  - DWT
  - 性能优化
prerequisites:
  - "code-optimization-basics"
  - "compiler-optimization"
related_contents:
  - "memory-optimization"
  - "real-time-optimization"
  - "performance-analysis-tool"

# 学习信息
estimated_time: 55
difficulty_score: 2

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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 执行时间测量
  - 性能分析
  - DWT计数器
  - 代码性能
  - 时间测量
cover_image: ""
---

# 代码执行时间测量方法：精确分析程序性能


## 概述

在嵌入式系统开发中，准确测量代码执行时间是性能优化的基础。只有通过精确的测量，我们才能：
- 识别性能瓶颈
- 量化优化效果
- 验证实时性要求
- 进行性能对比

本教程将介绍多种时间测量方法，从简单的系统时钟到高精度的硬件计数器，帮助你选择最适合的测量工具。

### 为什么需要测量执行时间？

**性能优化的基础**:
- **识别瓶颈**: 找出耗时最多的代码段
- **验证优化**: 量化优化前后的性能提升
- **实时性保证**: 确保任务在规定时间内完成
- **资源规划**: 合理分配CPU时间

**测量的挑战**:
- **测量精度**: 需要足够的时间分辨率
- **测量开销**: 测量本身不应影响结果
- **可重复性**: 结果应该稳定可靠
- **平台差异**: 不同MCU有不同的测量方法

### 测量方法概览

| 方法 | 精度 | 开销 | 适用场景 |
|------|------|------|---------|
| 系统时钟 | 毫秒级 | 低 | 长时间任务 |
| 硬件定时器 | 微秒级 | 低 | 一般测量 |
| DWT周期计数器 | 时钟周期 | 极低 | 精确测量 |
| GPIO翻转 | 纳秒级 | 极低 | 示波器测量 |
| 性能分析工具 | 函数级 | 中 | 全局分析 |


## 学习目标

完成本教程后，你将能够:

- [ ] 理解不同时间测量方法的原理和特点
- [ ] 使用系统时钟进行基本的时间测量
- [ ] 配置和使用硬件定时器测量执行时间
- [ ] 掌握DWT周期计数器的使用方法
- [ ] 使用GPIO和示波器进行高精度测量
- [ ] 选择适合特定场景的测量方法
- [ ] 分析和解释测量结果

## 前置要求

在开始本教程之前，你需要:

**知识要求**:
- 了解C语言编程基础
- 理解嵌入式系统基本概念
- 阅读过[代码优化基础原则](./01-code-optimization-basics.html)

**硬件要求**:
- ARM Cortex-M系列开发板（推荐STM32）
- USB调试器（ST-Link或J-Link）
- 示波器（可选，用于GPIO测量）

**软件要求**:
- STM32CubeIDE或Keil MDK
- 串口终端工具
- 调试器驱动程序


## 准备工作

### 硬件连接

```
开发板 <--USB--> 电脑
  |
  +---> 串口输出（查看测量结果）
  |
  +---> GPIO引脚（可选，连接示波器）
```

### 软件配置

创建新项目并配置：
- 系统时钟（如72MHz或168MHz）
- 串口通信（用于输出结果）
- 定时器（用于时间测量）
- DWT（调试和跟踪单元）


## 步骤1：使用系统时钟测量（毫秒级）

### 1.1 HAL库时钟函数

最简单的测量方法是使用HAL库提供的`HAL_GetTick()`函数。

**原理**: 
- SysTick定时器每1ms产生一次中断
- 中断中递增全局计数器
- 精度：1毫秒

**示例代码**:

```c
#include "main.h"
#include <stdio.h>

// 测试函数：计算数组和
uint32_t sum_array(uint32_t *array, int size) {
    uint32_t sum = 0;
    for (int i = 0; i < size; i++) {
        sum += array[i];
    }
    return sum;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 准备测试数据
    uint32_t test_data[1000];
    for (int i = 0; i < 1000; i++) {
        test_data[i] = i;
    }
    
    // 测量执行时间
    uint32_t start_tick = HAL_GetTick();
    
    uint32_t result = sum_array(test_data, 1000);
    
    uint32_t end_tick = HAL_GetTick();
    uint32_t elapsed_ms = end_tick - start_tick;
    
    printf("Result: %lu\n", result);
    printf("Execution time: %lu ms\n", elapsed_ms);
    
    while (1) {
        // 主循环
    }
}
```

### 1.2 优缺点分析

**优点**:
- ✅ 使用简单，无需额外配置
- ✅ 开销很小
- ✅ 跨平台兼容性好

**缺点**:
- ❌ 精度低（1ms）
- ❌ 不适合测量短时间任务
- ❌ 可能被中断影响

**适用场景**:
- 测量耗时较长的任务（>10ms）
- 粗略的性能评估
- 不需要高精度的场合


## 步骤2：使用硬件定时器测量（微秒级）

### 2.1 配置定时器

使用通用定时器可以获得更高的精度。

**配置步骤**:

```c
// 定时器配置（以TIM2为例，72MHz系统时钟）
TIM_HandleTypeDef htim2;

void Timer_Init(void) {
    // 使能定时器时钟
    __HAL_RCC_TIM2_CLK_ENABLE();
    
    // 配置定时器
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 72 - 1;  // 72MHz / 72 = 1MHz (1us per tick)
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 0xFFFFFFFF;  // 32位最大值
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    
    HAL_TIM_Base_Init(&htim2);
}

// 启动定时器
void Timer_Start(void) {
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    HAL_TIM_Base_Start(&htim2);
}

// 停止定时器并返回微秒数
uint32_t Timer_Stop(void) {
    HAL_TIM_Base_Stop(&htim2);
    return __HAL_TIM_GET_COUNTER(&htim2);
}
```

### 2.2 测量示例

```c
#include <stdio.h>

// 测试函数：冒泡排序
void bubble_sort(int *array, int size) {
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            if (array[j] > array[j + 1]) {
                int temp = array[j];
                array[j] = array[j + 1];
                array[j + 1] = temp;
            }
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    Timer_Init();
    
    // 准备测试数据
    int test_array[100];
    for (int i = 0; i < 100; i++) {
        test_array[i] = 100 - i;  // 逆序数组
    }
    
    // 测量排序时间
    Timer_Start();
    
    bubble_sort(test_array, 100);
    
    uint32_t elapsed_us = Timer_Stop();
    
    printf("Sorting completed\n");
    printf("Execution time: %lu us\n", elapsed_us);
    printf("Execution time: %.2f ms\n", elapsed_us / 1000.0f);
    
    while (1) {
        // 主循环
    }
}
```

### 2.3 多次测量取平均值

为了获得更准确的结果，应该多次测量并计算平均值：

```c
#define MEASUREMENT_COUNT 100

void measure_function_performance(void) {
    uint32_t measurements[MEASUREMENT_COUNT];
    uint32_t sum = 0;
    uint32_t min = UINT32_MAX;
    uint32_t max = 0;
    
    // 进行多次测量
    for (int i = 0; i < MEASUREMENT_COUNT; i++) {
        // 准备测试数据
        int test_array[100];
        for (int j = 0; j < 100; j++) {
            test_array[j] = 100 - j;
        }
        
        // 测量
        Timer_Start();
        bubble_sort(test_array, 100);
        measurements[i] = Timer_Stop();
        
        // 统计
        sum += measurements[i];
        if (measurements[i] < min) min = measurements[i];
        if (measurements[i] > max) max = measurements[i];
    }
    
    // 计算平均值
    uint32_t average = sum / MEASUREMENT_COUNT;
    
    printf("=== Performance Statistics ===\n");
    printf("Measurements: %d\n", MEASUREMENT_COUNT);
    printf("Average: %lu us\n", average);
    printf("Min: %lu us\n", min);
    printf("Max: %lu us\n", max);
    printf("Range: %lu us\n", max - min);
}
```

### 2.4 优缺点分析

**优点**:
- ✅ 精度高（微秒级）
- ✅ 适合大多数测量场景
- ✅ 配置灵活

**缺点**:
- ❌ 需要额外配置
- ❌ 占用一个定时器资源
- ❌ 测量范围受定时器位数限制

**适用场景**:
- 测量中等时长的任务（1us - 几秒）
- 需要较高精度的场合
- 一般性能分析


## 步骤3：使用DWT周期计数器（时钟周期级）

### 3.1 DWT简介

**DWT (Data Watchpoint and Trace)** 是ARM Cortex-M处理器的调试和跟踪单元，包含一个周期计数器。

**特点**:
- 精度：1个CPU时钟周期
- 范围：32位（约60秒@72MHz）
- 开销：几乎为零
- 不占用定时器资源

### 3.2 DWT初始化

```c
#include "stm32f4xx.h"  // 根据你的MCU修改

// 初始化DWT周期计数器
void DWT_Init(void) {
    // 使能DWT
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    
    // 复位周期计数器
    DWT->CYCCNT = 0;
    
    // 使能周期计数器
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// 获取当前周期数
static inline uint32_t DWT_GetCycles(void) {
    return DWT->CYCCNT;
}

// 周期数转换为微秒
static inline float DWT_CyclesToUs(uint32_t cycles) {
    return (float)cycles / (SystemCoreClock / 1000000.0f);
}

// 周期数转换为毫秒
static inline float DWT_CyclesToMs(uint32_t cycles) {
    return (float)cycles / (SystemCoreClock / 1000.0f);
}
```

### 3.3 测量示例

```c
#include <stdio.h>
#include <math.h>

// 测试函数：计算平方根
float calculate_sqrt_sum(float *data, int size) {
    float sum = 0;
    for (int i = 0; i < size; i++) {
        sum += sqrtf(data[i]);
    }
    return sum;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    DWT_Init();
    
    // 准备测试数据
    float test_data[1000];
    for (int i = 0; i < 1000; i++) {
        test_data[i] = (float)i;
    }
    
    // 测量执行时间
    uint32_t start_cycles = DWT_GetCycles();
    
    float result = calculate_sqrt_sum(test_data, 1000);
    
    uint32_t end_cycles = DWT_GetCycles();
    uint32_t elapsed_cycles = end_cycles - start_cycles;
    
    printf("Result: %.2f\n", result);
    printf("CPU Cycles: %lu\n", elapsed_cycles);
    printf("Time: %.2f us\n", DWT_CyclesToUs(elapsed_cycles));
    printf("Time: %.4f ms\n", DWT_CyclesToMs(elapsed_cycles));
    
    while (1) {
        // 主循环
    }
}
```

### 3.4 高精度性能分析

使用DWT可以进行非常精确的性能分析：

```c
// 性能分析结构
typedef struct {
    const char *name;
    uint32_t call_count;
    uint32_t total_cycles;
    uint32_t min_cycles;
    uint32_t max_cycles;
} PerfProfile_t;

#define MAX_PROFILES 10
PerfProfile_t profiles[MAX_PROFILES];
int profile_count = 0;

// 开始性能分析
int Perf_Start(const char *name) {
    // 查找或创建profile
    for (int i = 0; i < profile_count; i++) {
        if (strcmp(profiles[i].name, name) == 0) {
            return i;
        }
    }
    
    // 创建新profile
    if (profile_count < MAX_PROFILES) {
        profiles[profile_count].name = name;
        profiles[profile_count].call_count = 0;
        profiles[profile_count].total_cycles = 0;
        profiles[profile_count].min_cycles = UINT32_MAX;
        profiles[profile_count].max_cycles = 0;
        return profile_count++;
    }
    
    return -1;
}

// 记录性能数据
void Perf_Record(int id, uint32_t cycles) {
    if (id < 0 || id >= profile_count) return;
    
    profiles[id].call_count++;
    profiles[id].total_cycles += cycles;
    
    if (cycles < profiles[id].min_cycles) {
        profiles[id].min_cycles = cycles;
    }
    if (cycles > profiles[id].max_cycles) {
        profiles[id].max_cycles = cycles;
    }
}

// 打印性能报告
void Perf_PrintReport(void) {
    printf("\n=== Performance Report ===\n");
    printf("%-20s %8s %12s %10s %10s %10s\n",
           "Function", "Calls", "Total(us)", "Min(us)", "Max(us)", "Avg(us)");
    printf("-------------------------------------------------------------------\n");
    
    for (int i = 0; i < profile_count; i++) {
        uint32_t avg_cycles = profiles[i].total_cycles / profiles[i].call_count;
        
        printf("%-20s %8lu %12.2f %10.2f %10.2f %10.2f\n",
               profiles[i].name,
               profiles[i].call_count,
               DWT_CyclesToUs(profiles[i].total_cycles),
               DWT_CyclesToUs(profiles[i].min_cycles),
               DWT_CyclesToUs(profiles[i].max_cycles),
               DWT_CyclesToUs(avg_cycles));
    }
    printf("=========================\n\n");
}

// 使用示例
void my_function(void) {
    int id = Perf_Start("my_function");
    uint32_t start = DWT_GetCycles();
    
    // 函数代码
    for (int i = 0; i < 1000; i++) {
        // 一些计算
    }
    
    uint32_t cycles = DWT_GetCycles() - start;
    Perf_Record(id, cycles);
}
```


### 3.5 宏定义简化使用

```c
// 定义测量宏
#define PERF_MEASURE_START() \
    uint32_t __perf_start = DWT_GetCycles()

#define PERF_MEASURE_END(name) \
    do { \
        uint32_t __perf_cycles = DWT_GetCycles() - __perf_start; \
        printf("%s: %lu cycles (%.2f us)\n", \
               name, __perf_cycles, DWT_CyclesToUs(__perf_cycles)); \
    } while(0)

// 使用示例
void test_performance(void) {
    PERF_MEASURE_START();
    
    // 要测量的代码
    complex_calculation();
    
    PERF_MEASURE_END("complex_calculation");
}
```

### 3.6 优缺点分析

**优点**:
- ✅ 精度极高（时钟周期级）
- ✅ 开销几乎为零
- ✅ 不占用定时器资源
- ✅ 使用简单

**缺点**:
- ❌ 仅限ARM Cortex-M3及以上
- ❌ 32位计数器可能溢出
- ❌ 需要了解CPU时钟频率

**适用场景**:
- 精确的性能分析
- 测量短时间代码段
- 优化关键路径
- 性能对比测试


## 步骤4：使用GPIO和示波器测量

### 4.1 GPIO翻转方法

使用GPIO引脚翻转配合示波器可以进行非侵入式的时间测量。

**原理**:
- 代码开始时拉高GPIO
- 代码结束时拉低GPIO
- 示波器测量高电平持续时间

**配置GPIO**:

```c
// 配置GPIO用于性能测量
void Perf_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 配置PA5为输出
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 初始化为低电平
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
}

// 定义测量宏
#define PERF_PIN_HIGH() HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET)
#define PERF_PIN_LOW()  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET)
#define PERF_PIN_TOGGLE() HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5)
```

### 4.2 测量示例

```c
void test_function(void) {
    // 标记开始
    PERF_PIN_HIGH();
    
    // 要测量的代码
    for (int i = 0; i < 1000; i++) {
        // 一些计算
        volatile int x = i * i;
    }
    
    // 标记结束
    PERF_PIN_LOW();
}

// 测量多个代码段
void test_multiple_sections(void) {
    // 第一段代码
    PERF_PIN_HIGH();
    section1();
    PERF_PIN_LOW();
    
    HAL_Delay(1);  // 间隔
    
    // 第二段代码
    PERF_PIN_HIGH();
    section2();
    PERF_PIN_LOW();
}
```

### 4.3 使用寄存器直接操作（更快）

```c
// 使用寄存器直接操作，减少开销
#define PERF_PIN_SET_FAST()   (GPIOA->BSRR = GPIO_PIN_5)
#define PERF_PIN_RESET_FAST() (GPIOA->BSRR = (GPIO_PIN_5 << 16))
#define PERF_PIN_TOGGLE_FAST() (GPIOA->ODR ^= GPIO_PIN_5)

// 测量GPIO操作本身的开销
void measure_gpio_overhead(void) {
    uint32_t start, end;
    
    // 测量HAL函数开销
    start = DWT_GetCycles();
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
    end = DWT_GetCycles();
    printf("HAL GPIO overhead: %lu cycles\n", end - start);
    
    // 测量寄存器直接操作开销
    start = DWT_GetCycles();
    PERF_PIN_SET_FAST();
    end = DWT_GetCycles();
    printf("Direct GPIO overhead: %lu cycles\n", end - start);
}
```

### 4.4 优缺点分析

**优点**:
- ✅ 非侵入式测量
- ✅ 可视化效果好
- ✅ 可以测量多个代码段
- ✅ 不受软件调试影响

**缺点**:
- ❌ 需要示波器
- ❌ GPIO操作有开销
- ❌ 需要额外的硬件连接

**适用场景**:
- 硬件调试阶段
- 需要可视化时序
- 测量中断响应时间
- 验证实时性


## 步骤5：性能分析工具

### 5.1 使用GDB进行性能分析

```bash
# 在GDB中设置断点并计数
(gdb) break function_name
(gdb) commands
> silent
> set $count = $count + 1
> continue
> end

# 运行程序
(gdb) run

# 查看调用次数
(gdb) print $count
```

### 5.2 使用Segger SystemView

SystemView是一个强大的实时系统分析工具。

**配置步骤**:

```c
#include "SEGGER_SYSVIEW.h"

// 初始化SystemView
void SystemView_Init(void) {
    SEGGER_SYSVIEW_Conf();
    SEGGER_SYSVIEW_Start();
}

// 标记代码段
void my_function(void) {
    SEGGER_SYSVIEW_RecordEnterISR();
    
    // 函数代码
    
    SEGGER_SYSVIEW_RecordExitISR();
}
```

### 5.3 使用printf进行简单分析

```c
// 简单的时间戳打印
void debug_timestamp(const char *msg) {
    static uint32_t last_time = 0;
    uint32_t current_time = HAL_GetTick();
    uint32_t delta = current_time - last_time;
    
    printf("[%lu ms] (+%lu ms) %s\n", current_time, delta, msg);
    
    last_time = current_time;
}

// 使用示例
void process_data(void) {
    debug_timestamp("Start processing");
    
    step1();
    debug_timestamp("Step 1 complete");
    
    step2();
    debug_timestamp("Step 2 complete");
    
    step3();
    debug_timestamp("Step 3 complete");
}
```


## 步骤6：测量注意事项

### 6.1 避免常见错误

#### 错误1: 忽略测量开销

```c
// 错误：没有考虑测量开销
uint32_t start = DWT_GetCycles();
very_short_function();  // 只需要几个周期
uint32_t cycles = DWT_GetCycles() - start;
// cycles可能主要是测量开销

// 正确：测量并减去开销
uint32_t overhead;
{
    uint32_t s = DWT_GetCycles();
    uint32_t e = DWT_GetCycles();
    overhead = e - s;
}

uint32_t start = DWT_GetCycles();
very_short_function();
uint32_t cycles = DWT_GetCycles() - start - overhead;
```

#### 错误2: 单次测量

```c
// 错误：只测量一次
uint32_t time = measure_once();

// 正确：多次测量取平均
uint32_t sum = 0;
for (int i = 0; i < 100; i++) {
    sum += measure_once();
}
uint32_t average = sum / 100;
```

#### 错误3: 忽略缓存影响

```c
// 错误：第一次运行可能包含缓存未命中
measure_function();  // 第一次，缓存冷启动

// 正确：预热缓存
function();  // 预热
measure_function();  // 测量
```

### 6.2 提高测量准确性

```c
// 完整的测量函数
typedef struct {
    uint32_t min;
    uint32_t max;
    uint32_t average;
    uint32_t median;
    uint32_t std_dev;
} MeasurementResult_t;

MeasurementResult_t measure_with_statistics(
    void (*func)(void), 
    int iterations
) {
    uint32_t *measurements = malloc(iterations * sizeof(uint32_t));
    uint32_t sum = 0;
    
    // 预热
    func();
    
    // 测量
    for (int i = 0; i < iterations; i++) {
        uint32_t start = DWT_GetCycles();
        func();
        measurements[i] = DWT_GetCycles() - start;
        sum += measurements[i];
    }
    
    // 排序以计算中位数
    qsort(measurements, iterations, sizeof(uint32_t), compare_uint32);
    
    // 计算统计数据
    MeasurementResult_t result;
    result.min = measurements[0];
    result.max = measurements[iterations - 1];
    result.average = sum / iterations;
    result.median = measurements[iterations / 2];
    
    // 计算标准差
    uint64_t variance_sum = 0;
    for (int i = 0; i < iterations; i++) {
        int32_t diff = measurements[i] - result.average;
        variance_sum += diff * diff;
    }
    result.std_dev = (uint32_t)sqrt(variance_sum / iterations);
    
    free(measurements);
    return result;
}
```

### 6.3 处理计数器溢出

```c
// 处理32位计数器溢出
uint32_t calculate_elapsed(uint32_t start, uint32_t end) {
    if (end >= start) {
        return end - start;
    } else {
        // 发生溢出
        return (UINT32_MAX - start) + end + 1;
    }
}

// 使用示例
uint32_t start = DWT_GetCycles();
long_running_function();
uint32_t end = DWT_GetCycles();
uint32_t elapsed = calculate_elapsed(start, end);
```


## 步骤7：实战案例

### 案例1: 对比不同算法性能

```c
// 算法1：线性查找
int linear_search(int *array, int size, int target) {
    for (int i = 0; i < size; i++) {
        if (array[i] == target) {
            return i;
        }
    }
    return -1;
}

// 算法2：二分查找（需要排序数组）
int binary_search(int *array, int size, int target) {
    int left = 0;
    int right = size - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (array[mid] == target) {
            return mid;
        } else if (array[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}

// 性能对比
void compare_search_algorithms(void) {
    int test_array[1000];
    for (int i = 0; i < 1000; i++) {
        test_array[i] = i;
    }
    
    int target = 999;  // 最坏情况
    
    // 测量线性查找
    uint32_t start = DWT_GetCycles();
    int result1 = linear_search(test_array, 1000, target);
    uint32_t cycles1 = DWT_GetCycles() - start;
    
    // 测量二分查找
    start = DWT_GetCycles();
    int result2 = binary_search(test_array, 1000, target);
    uint32_t cycles2 = DWT_GetCycles() - start;
    
    printf("Linear search: %lu cycles (%.2f us)\n", 
           cycles1, DWT_CyclesToUs(cycles1));
    printf("Binary search: %lu cycles (%.2f us)\n", 
           cycles2, DWT_CyclesToUs(cycles2));
    printf("Speedup: %.2fx\n", (float)cycles1 / cycles2);
}
```


### 案例2: 优化前后对比

```c
// 原始版本：未优化
uint32_t sum_array_v1(uint32_t *array, int size) {
    uint32_t sum = 0;
    for (int i = 0; i < size; i++) {
        sum += array[i];
    }
    return sum;
}

// 优化版本：循环展开
uint32_t sum_array_v2(uint32_t *array, int size) {
    uint32_t sum = 0;
    int i;
    
    // 处理4的倍数部分
    for (i = 0; i < size - 3; i += 4) {
        sum += array[i];
        sum += array[i + 1];
        sum += array[i + 2];
        sum += array[i + 3];
    }
    
    // 处理剩余部分
    for (; i < size; i++) {
        sum += array[i];
    }
    
    return sum;
}

// 性能对比
void compare_optimization(void) {
    uint32_t test_data[10000];
    for (int i = 0; i < 10000; i++) {
        test_data[i] = i;
    }
    
    // 测量原始版本
    uint32_t cycles1 = 0;
    for (int i = 0; i < 100; i++) {
        uint32_t start = DWT_GetCycles();
        volatile uint32_t result = sum_array_v1(test_data, 10000);
        cycles1 += DWT_GetCycles() - start;
    }
    cycles1 /= 100;
    
    // 测量优化版本
    uint32_t cycles2 = 0;
    for (int i = 0; i < 100; i++) {
        uint32_t start = DWT_GetCycles();
        volatile uint32_t result = sum_array_v2(test_data, 10000);
        cycles2 += DWT_GetCycles() - start;
    }
    cycles2 /= 100;
    
    printf("Original: %lu cycles (%.2f us)\n", 
           cycles1, DWT_CyclesToUs(cycles1));
    printf("Optimized: %lu cycles (%.2f us)\n", 
           cycles2, DWT_CyclesToUs(cycles2));
    printf("Improvement: %.2f%%\n", 
           ((float)(cycles1 - cycles2) / cycles1) * 100);
}
```

### 案例3: 中断响应时间测量

```c
// 配置GPIO用于测量中断延迟
void setup_interrupt_measurement(void) {
    // 配置外部中断引脚（PA0）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 配置测量引脚（PA5）
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 使能中断
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

// 中断处理函数
void EXTI0_IRQHandler(void) {
    // 立即拉高测量引脚
    GPIOA->BSRR = GPIO_PIN_5;
    
    // 处理中断
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
    
    // 拉低测量引脚
    GPIOA->BSRR = (GPIO_PIN_5 << 16);
}

// 使用示波器测量PA0到PA5的延迟
// 这就是中断响应时间
```


## 步骤8：选择合适的测量方法

### 8.1 决策流程图

```
开始
  |
  v
需要测量什么？
  |
  +-- 长时间任务(>10ms) --> 使用HAL_GetTick()
  |
  +-- 中等时间(1us-10ms) --> 使用硬件定时器
  |
  +-- 短时间(<1us) --> 使用DWT周期计数器
  |
  +-- 可视化时序 --> 使用GPIO+示波器
  |
  +-- 全局分析 --> 使用性能分析工具
```

### 8.2 方法对比表

| 方法 | 精度 | 范围 | 开销 | 复杂度 | 推荐场景 |
|------|------|------|------|--------|---------|
| HAL_GetTick() | 1ms | 无限 | 低 | 简单 | 长时间任务 |
| 硬件定时器 | 1us | 秒级 | 低 | 中等 | 一般测量 |
| DWT计数器 | 1周期 | 60秒 | 极低 | 简单 | 精确测量 |
| GPIO+示波器 | ns级 | 无限 | 低 | 中等 | 硬件调试 |
| 性能工具 | 函数级 | 无限 | 中 | 复杂 | 全局分析 |

### 8.3 实际应用建议

**日常开发**:
- 使用DWT周期计数器进行快速测量
- 使用宏简化测量代码
- 建立性能基准数据库

**性能优化**:
- 使用多种方法交叉验证
- 多次测量取平均值
- 记录优化前后的数据

**生产调试**:
- 使用GPIO+示波器进行非侵入测量
- 使用性能分析工具找出瓶颈
- 建立自动化测试脚本


## 故障排除

### 问题1: DWT计数器不工作

**现象**: DWT->CYCCNT始终为0

**原因**:
- 未使能DWT
- 调试器未连接
- 芯片不支持DWT

**解决方法**:
```c
// 确保正确初始化
void DWT_Init_Safe(void) {
    // 检查是否支持DWT
    if (!(CoreDebug->DEMCR & CoreDebug_DEMCR_TRCENA_Msk)) {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    }
    
    // 复位计数器
    DWT->CYCCNT = 0;
    
    // 使能计数器
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    
    // 验证
    uint32_t test = DWT->CYCCNT;
    if (test == 0) {
        printf("Warning: DWT may not be working\n");
    }
}
```

### 问题2: 测量结果不稳定

**现象**: 每次测量结果差异很大

**原因**:
- 中断干扰
- 缓存影响
- 编译器优化

**解决方法**:
```c
// 禁用中断进行测量
void measure_without_interrupts(void) {
    __disable_irq();
    
    uint32_t start = DWT_GetCycles();
    function_to_measure();
    uint32_t cycles = DWT_GetCycles() - start;
    
    __enable_irq();
    
    printf("Cycles: %lu\n", cycles);
}

// 防止编译器优化
volatile uint32_t result;

void measure_with_volatile(void) {
    uint32_t start = DWT_GetCycles();
    result = function_to_measure();
    uint32_t cycles = DWT_GetCycles() - start;
}
```

### 问题3: 计数器溢出

**现象**: 长时间测量结果错误

**解决方法**:
```c
// 使用64位计数器
typedef struct {
    uint32_t low;
    uint32_t high;
} Counter64_t;

Counter64_t counter = {0, 0};
uint32_t last_count = 0;

void update_counter64(void) {
    uint32_t current = DWT->CYCCNT;
    
    // 检测溢出
    if (current < last_count) {
        counter.high++;
    }
    
    counter.low = current;
    last_count = current;
}

uint64_t get_counter64(void) {
    return ((uint64_t)counter.high << 32) | counter.low;
}
```


## 最佳实践

### DO（推荐做法）

**1. 多次测量**
- ✅ 至少测量10次取平均值
- ✅ 记录最小值、最大值和标准差
- ✅ 排除异常值

**2. 预热缓存**
- ✅ 第一次运行用于预热
- ✅ 从第二次开始记录数据
- ✅ 考虑缓存对性能的影响

**3. 减少干扰**
- ✅ 在测量关键代码时禁用中断
- ✅ 避免在测量期间进行I/O操作
- ✅ 使用volatile防止编译器优化

**4. 记录环境**
- ✅ 记录CPU频率
- ✅ 记录编译器优化级别
- ✅ 记录测试条件

**5. 自动化测试**
- ✅ 建立性能测试框架
- ✅ 定期运行性能测试
- ✅ 跟踪性能变化趋势

### DON'T（避免做法）

**1. 单次测量**
- ❌ 不要只测量一次
- ❌ 不要忽略测量误差
- ❌ 不要相信异常值

**2. 忽略开销**
- ❌ 不要忽略测量本身的开销
- ❌ 不要在测量中包含无关代码
- ❌ 不要使用慢速的测量方法

**3. 不考虑环境**
- ❌ 不要在不同条件下对比
- ❌ 不要忽略中断影响
- ❌ 不要忽略编译器优化

**4. 过度优化**
- ❌ 不要优化不是瓶颈的代码
- ❌ 不要为了微小提升牺牲可读性
- ❌ 不要过早优化

### 测量检查清单

**测量前**:
- [ ] 确定测量目标和精度要求
- [ ] 选择合适的测量方法
- [ ] 初始化测量工具
- [ ] 准备测试数据
- [ ] 记录测试环境

**测量中**:
- [ ] 预热缓存
- [ ] 多次测量
- [ ] 记录所有数据
- [ ] 检查异常值
- [ ] 验证结果合理性

**测量后**:
- [ ] 计算统计数据
- [ ] 分析结果
- [ ] 记录结论
- [ ] 保存测量数据
- [ ] 更新性能基准


## 总结

通过本教程，你学习了:

- ✅ 多种时间测量方法的原理和使用
- ✅ 如何选择适合的测量方法
- ✅ 如何提高测量准确性
- ✅ 如何避免常见的测量错误
- ✅ 如何进行性能对比和分析

**关键要点**:

1. **选择合适的方法**:
   - 长时间任务: HAL_GetTick()
   - 一般测量: 硬件定时器
   - 精确测量: DWT周期计数器
   - 硬件调试: GPIO+示波器

2. **提高准确性**:
   - 多次测量取平均
   - 预热缓存
   - 减少干扰
   - 记录环境

3. **实用技巧**:
   - 使用宏简化代码
   - 建立性能分析框架
   - 自动化测试
   - 跟踪性能趋势

4. **注意事项**:
   - 考虑测量开销
   - 处理计数器溢出
   - 防止编译器优化
   - 记录测试条件

**测量流程**:
```
1. 确定测量目标
2. 选择测量方法
3. 初始化测量工具
4. 预热缓存
5. 多次测量
6. 统计分析
7. 记录结果
```

记住，准确的测量是性能优化的基础。选择合适的工具，遵循最佳实践，你就能获得可靠的性能数据。


## 延伸阅读

### 相关文章

- [代码优化基础原则](./01-code-optimization-basics.html) - 优化的基本思路
- [编译器优化选项使用](./02-compiler-optimization.html) - 编译器优化
- [内存使用优化技术](../intermediate/01-memory-optimization.html) - 内存优化
- [算法复杂度与性能分析](../intermediate/03-algorithm-complexity.html) - 算法分析

### 进阶主题

- [实时性能优化技术](../advanced/01-real-time-optimization.html) - 实时系统优化
- [性能分析工具开发](../advanced/02-performance-analysis-tool.html) - 开发分析工具
- [单元测试框架搭建](../../02-debugging-testing/advanced/01-unit-testing-framework.html) - 测试框架

### 参考资料

**官方文档**:
1. [ARM Cortex-M DWT](https://developer.arm.com/documentation/) - DWT官方文档
2. [STM32 HAL库文档](https://www.st.com/en/embedded-software/stm32cube-mcu-mpu-packages.html) - HAL库参考
3. [Segger SystemView](https://www.segger.com/products/development-tools/systemview/) - 性能分析工具

**在线资源**:
1. [Embedded Artistry - Performance](https://embeddedartistry.com/blog/tag/performance/) - 性能优化文章
2. [ARM Community](https://community.arm.com/) - ARM开发者社区
3. [Stack Overflow - Embedded](https://stackoverflow.com/questions/tagged/embedded) - 问答社区

**工具推荐**:
1. **Segger SystemView**: 实时系统分析
2. **Tracealyzer**: RTOS性能分析
3. **Percepio**: 嵌入式追踪工具

---

**练习建议**:
1. 实现一个完整的性能测量框架
2. 对比不同算法的性能
3. 测量中断响应时间
4. 分析编译器优化效果
5. 建立项目的性能基准数据库

**实践项目**:
1. 开发一个性能分析库，支持多种测量方法
2. 实现自动化性能测试系统
3. 创建性能可视化工具
4. 建立性能回归测试框架
5. 优化现有项目并记录性能提升
