---
title: "内存泄漏检测与分析"
description: "深入学习嵌入式系统中的内存泄漏检测技术，包括泄漏检测工具的使用、内存追踪机制的实现、常见泄漏原因分析和解决方案，帮助开发者构建可靠的内存管理系统"
slug: "memory-leak-detection"

# 分类信息
domain: "驱动与BSP层"
module: "内存管理"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 内存泄漏
  - 调试工具
  - 内存分析
  - 内存追踪
  - 故障诊断
prerequisites:
  - "memory-management-basics"
  - "dynamic-memory-allocation"
related_contents: []

# 学习信息
estimated_time: 75
difficulty_score: 3

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
  - 内存泄漏检测
  - 内存调试
  - 泄漏分析
  - 内存追踪
  - 调试技巧
cover_image: ""
---

# 内存泄漏检测与分析

## 学习目标

完成本教程后，你将能够：

- [ ] 理解内存泄漏的概念、原因和危害
- [ ] 掌握多种内存泄漏检测方法和工具
- [ ] 实现自定义的内存追踪和监控系统
- [ ] 分析和定位内存泄漏的根本原因
- [ ] 应用最佳实践预防内存泄漏

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 理解C语言的指针和动态内存分配
- 熟悉malloc/free的使用
- 了解内存管理的基本概念
- 掌握基本的调试技巧

**技能要求**：
- 能够编写和调试C程序
- 会使用基本的开发工具和调试器
- 了解如何分析程序运行状态


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 |
|------|------|------|
| 开发板 | 1 | STM32/ESP32或其他嵌入式开发板 |
| 调试器 | 1 | ST-Link、J-Link或板载调试器 |
| USB线 | 1 | 用于连接开发板 |

### 软件准备

- **开发环境**：STM32CubeIDE、Keil MDK或GCC工具链
- **调试工具**：GDB、OpenOCD
- **分析工具**：Valgrind（Linux）、AddressSanitizer（可选）
- **串口工具**：用于查看调试输出

### 环境配置

1. 安装开发环境和工具链
2. 配置调试器连接
3. 准备测试项目

## 什么是内存泄漏？

### 定义

内存泄漏是指程序在运行过程中分配了内存但未能正确释放，导致可用内存逐渐减少的现象。

**简单示例**：

```c
void memory_leak_example(void) {
    // 分配内存
    char* buffer = (char*)malloc(100);
    
    // 使用内存
    strcpy(buffer, "Hello");
    
    // 忘记释放内存 - 这就是内存泄漏！
    // free(buffer);  // 应该调用但没有调用
}

// 每次调用这个函数都会泄漏100字节
for (int i = 0; i < 1000; i++) {
    memory_leak_example();  // 总共泄漏100KB
}
```

### 内存泄漏的危害

在嵌入式系统中，内存泄漏的危害尤其严重：

1. **系统崩溃**：可用内存耗尽导致系统无法分配新内存
2. **性能下降**：内存碎片化影响分配效率
3. **功能失效**：关键功能因内存不足而无法执行
4. **不可预测**：问题可能在运行数小时或数天后才出现

**实际案例**：

```c
// 一个真实的泄漏场景
void process_sensor_data(void) {
    // 每秒调用一次
    sensor_data_t* data = (sensor_data_t*)malloc(sizeof(sensor_data_t));
    
    read_sensor(data);
    process_data(data);
    send_to_server(data);
    
    // 忘记释放！
    // 24小时后泄漏：86400次 × sizeof(sensor_data_t)
}
```

### 常见泄漏原因

1. **忘记释放**：最常见的原因
2. **异常路径**：错误处理分支中忘记释放
3. **循环引用**：对象相互引用导致无法释放
4. **指针丢失**：覆盖指针前未释放原内存
5. **资源管理错误**：文件句柄、套接字等资源未关闭


## 步骤1：实现基础内存追踪系统

### 1.1 设计追踪数据结构

首先，我们需要一个数据结构来记录每次内存分配：

```c
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

// 内存分配记录
typedef struct {
    void* ptr;              // 分配的内存地址
    size_t size;            // 分配的大小
    const char* file;       // 分配时的文件名
    int line;               // 分配时的行号
    uint32_t timestamp;     // 分配时间戳
    uint8_t is_active;      // 是否仍然活跃
} alloc_record_t;

// 追踪器配置
#define MAX_ALLOCATIONS 100
#define ENABLE_TRACKING 1

// 全局追踪数据
static alloc_record_t g_alloc_records[MAX_ALLOCATIONS];
static int g_alloc_count = 0;
static uint32_t g_alloc_id = 0;
static uint32_t g_total_allocated = 0;
static uint32_t g_total_freed = 0;
```

**代码说明**：
- `alloc_record_t`：记录每次分配的详细信息
- `MAX_ALLOCATIONS`：最多追踪的分配次数
- `g_alloc_records`：存储所有分配记录的数组
- `g_alloc_id`：唯一的分配ID，用于追踪

### 1.2 实现追踪函数

实现记录分配和释放的函数：

```c
// 记录内存分配
static void track_allocation(void* ptr, size_t size, 
                             const char* file, int line) {
    if (!ENABLE_TRACKING || ptr == NULL) return;
    
    // 查找空闲槽位
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (!g_alloc_records[i].is_active) {
            g_alloc_records[i].ptr = ptr;
            g_alloc_records[i].size = size;
            g_alloc_records[i].file = file;
            g_alloc_records[i].line = line;
            g_alloc_records[i].timestamp = g_alloc_id++;
            g_alloc_records[i].is_active = 1;
            
            g_alloc_count++;
            g_total_allocated += size;
            
            return;
        }
    }
    
    // 追踪表已满
    printf("WARNING: Allocation tracking table full!\n");
}

// 记录内存释放
static void track_deallocation(void* ptr) {
    if (!ENABLE_TRACKING || ptr == NULL) return;
    
    // 查找对应的分配记录
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (g_alloc_records[i].is_active && 
            g_alloc_records[i].ptr == ptr) {
            
            g_alloc_records[i].is_active = 0;
            g_alloc_count--;
            g_total_freed += g_alloc_records[i].size;
            
            return;
        }
    }
    
    // 未找到记录 - 可能是重复释放或野指针
    printf("WARNING: Freeing untracked pointer %p\n", ptr);
}
```

### 1.3 包装malloc和free

创建带追踪功能的内存分配函数：

```c
// 带追踪的malloc
#define tracked_malloc(size) \
    tracked_malloc_impl(size, __FILE__, __LINE__)

void* tracked_malloc_impl(size_t size, const char* file, int line) {
    void* ptr = malloc(size);
    
    if (ptr != NULL) {
        track_allocation(ptr, size, file, line);
        
        #ifdef DEBUG_MEMORY
        printf("[ALLOC] %zu bytes at %p (%s:%d)\n", 
               size, ptr, file, line);
        #endif
    }
    
    return ptr;
}

// 带追踪的free
void tracked_free(void* ptr) {
    if (ptr == NULL) return;
    
    #ifdef DEBUG_MEMORY
    printf("[FREE] %p\n", ptr);
    #endif
    
    track_deallocation(ptr);
    free(ptr);
}

// 带追踪的calloc
#define tracked_calloc(num, size) \
    tracked_calloc_impl(num, size, __FILE__, __LINE__)

void* tracked_calloc_impl(size_t num, size_t size, 
                          const char* file, int line) {
    void* ptr = calloc(num, size);
    
    if (ptr != NULL) {
        track_allocation(ptr, num * size, file, line);
    }
    
    return ptr;
}
```

**使用示例**：

```c
void test_tracking(void) {
    // 使用追踪版本的malloc
    char* str1 = (char*)tracked_malloc(50);
    char* str2 = (char*)tracked_malloc(100);
    
    if (str1 && str2) {
        strcpy(str1, "Hello");
        strcpy(str2, "World");
        
        // 正常释放
        tracked_free(str1);
        
        // 忘记释放str2 - 这会被检测到
    }
}
```


## 步骤2：实现泄漏检测和报告

### 2.1 检测内存泄漏

实现检查函数来发现未释放的内存：

```c
// 检查内存泄漏
void check_memory_leaks(void) {
    int leak_count = 0;
    size_t total_leaked = 0;
    
    printf("\n=== Memory Leak Report ===\n");
    
    // 遍历所有记录
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (g_alloc_records[i].is_active) {
            leak_count++;
            total_leaked += g_alloc_records[i].size;
            
            printf("LEAK #%d:\n", leak_count);
            printf("  Address: %p\n", g_alloc_records[i].ptr);
            printf("  Size: %zu bytes\n", g_alloc_records[i].size);
            printf("  Location: %s:%d\n", 
                   g_alloc_records[i].file, 
                   g_alloc_records[i].line);
            printf("  Timestamp: %lu\n", g_alloc_records[i].timestamp);
            printf("\n");
        }
    }
    
    if (leak_count == 0) {
        printf("✓ No memory leaks detected!\n");
    } else {
        printf("✗ Found %d memory leaks\n", leak_count);
        printf("✗ Total leaked: %zu bytes\n", total_leaked);
    }
    
    printf("=========================\n\n");
}

// 获取内存统计信息
void print_memory_stats(void) {
    printf("\n=== Memory Statistics ===\n");
    printf("Active allocations: %d\n", g_alloc_count);
    printf("Total allocated: %lu bytes\n", g_total_allocated);
    printf("Total freed: %lu bytes\n", g_total_freed);
    printf("Net allocated: %ld bytes\n", 
           (long)(g_total_allocated - g_total_freed));
    printf("=========================\n\n");
}
```

### 2.2 生成详细报告

创建更详细的泄漏报告：

```c
// 泄漏报告结构
typedef struct {
    int total_leaks;
    size_t total_bytes;
    int leaks_by_file[10];
    const char* file_names[10];
    int file_count;
} leak_report_t;

// 生成泄漏报告
void generate_leak_report(leak_report_t* report) {
    memset(report, 0, sizeof(leak_report_t));
    
    // 统计泄漏
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (g_alloc_records[i].is_active) {
            report->total_leaks++;
            report->total_bytes += g_alloc_records[i].size;
            
            // 按文件统计
            const char* file = g_alloc_records[i].file;
            int found = 0;
            
            for (int j = 0; j < report->file_count; j++) {
                if (strcmp(report->file_names[j], file) == 0) {
                    report->leaks_by_file[j]++;
                    found = 1;
                    break;
                }
            }
            
            if (!found && report->file_count < 10) {
                report->file_names[report->file_count] = file;
                report->leaks_by_file[report->file_count] = 1;
                report->file_count++;
            }
        }
    }
}

// 打印泄漏报告
void print_leak_report(void) {
    leak_report_t report;
    generate_leak_report(&report);
    
    printf("\n=== Detailed Leak Report ===\n");
    printf("Total leaks: %d\n", report.total_leaks);
    printf("Total bytes leaked: %zu\n", report.total_bytes);
    printf("\nLeaks by source file:\n");
    
    for (int i = 0; i < report.file_count; i++) {
        printf("  %s: %d leaks\n", 
               report.file_names[i], 
               report.leaks_by_file[i]);
    }
    
    printf("============================\n\n");
}
```

### 2.3 实时监控

实现实时内存使用监控：

```c
// 内存监控配置
#define MEMORY_WARNING_THRESHOLD 80  // 80%使用率警告
#define MEMORY_CRITICAL_THRESHOLD 95 // 95%使用率严重警告

// 监控内存使用
void monitor_memory_usage(void) {
    // 计算使用率
    float usage_percent = (float)g_alloc_count * 100 / MAX_ALLOCATIONS;
    
    if (usage_percent >= MEMORY_CRITICAL_THRESHOLD) {
        printf("CRITICAL: Memory usage at %.1f%%!\n", usage_percent);
    } else if (usage_percent >= MEMORY_WARNING_THRESHOLD) {
        printf("WARNING: Memory usage at %.1f%%\n", usage_percent);
    }
    
    // 显示当前状态
    printf("Memory: %d/%d allocations (%.1f%%)\n", 
           g_alloc_count, MAX_ALLOCATIONS, usage_percent);
}

// 定期检查（在主循环中调用）
void periodic_memory_check(void) {
    static uint32_t last_check = 0;
    uint32_t current_time = get_system_time();  // 获取系统时间
    
    // 每10秒检查一次
    if (current_time - last_check >= 10000) {
        monitor_memory_usage();
        last_check = current_time;
    }
}
```


## 步骤3：常见泄漏模式分析

### 3.1 简单泄漏

最基本的泄漏模式：

```c
// 模式1：忘记释放
void simple_leak(void) {
    char* buffer = (char*)tracked_malloc(100);
    strcpy(buffer, "Data");
    // 忘记调用 tracked_free(buffer);
}

// 检测方法
void test_simple_leak(void) {
    printf("Testing simple leak...\n");
    simple_leak();
    check_memory_leaks();  // 会检测到1个泄漏
}
```

### 3.2 条件分支泄漏

在错误处理路径中忘记释放：

```c
// 模式2：错误路径泄漏
int process_data(const char* filename) {
    char* buffer = (char*)tracked_malloc(1024);
    if (buffer == NULL) {
        return -1;  // 错误：这里不会泄漏
    }
    
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        // 错误：忘记释放buffer！
        return -1;
    }
    
    // 正常处理
    fread(buffer, 1, 1024, file);
    fclose(file);
    
    tracked_free(buffer);  // 只有正常路径会释放
    return 0;
}

// 正确的做法
int process_data_correct(const char* filename) {
    char* buffer = (char*)tracked_malloc(1024);
    if (buffer == NULL) {
        return -1;
    }
    
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        tracked_free(buffer);  // 正确：在返回前释放
        return -1;
    }
    
    fread(buffer, 1, 1024, file);
    fclose(file);
    
    tracked_free(buffer);
    return 0;
}
```

### 3.3 指针覆盖泄漏

覆盖指针前未释放原内存：

```c
// 模式3：指针覆盖
void pointer_overwrite_leak(void) {
    char* ptr = (char*)tracked_malloc(100);
    strcpy(ptr, "First allocation");
    
    // 错误：覆盖指针前未释放原内存
    ptr = (char*)tracked_malloc(200);
    strcpy(ptr, "Second allocation");
    
    tracked_free(ptr);  // 只释放了第二次分配的内存
    // 第一次分配的100字节泄漏了！
}

// 正确的做法
void pointer_overwrite_correct(void) {
    char* ptr = (char*)tracked_malloc(100);
    strcpy(ptr, "First allocation");
    
    // 正确：先释放再重新分配
    tracked_free(ptr);
    ptr = (char*)tracked_malloc(200);
    strcpy(ptr, "Second allocation");
    
    tracked_free(ptr);
}
```

### 3.4 循环中的泄漏

在循环中重复分配而不释放：

```c
// 模式4：循环泄漏
void loop_leak(void) {
    for (int i = 0; i < 10; i++) {
        char* temp = (char*)tracked_malloc(50);
        sprintf(temp, "Iteration %d", i);
        process_string(temp);
        // 错误：每次循环都泄漏50字节
    }
    // 总共泄漏500字节
}

// 正确的做法
void loop_correct(void) {
    for (int i = 0; i < 10; i++) {
        char* temp = (char*)tracked_malloc(50);
        sprintf(temp, "Iteration %d", i);
        process_string(temp);
        tracked_free(temp);  // 正确：每次循环后释放
    }
}

// 更好的做法：循环外分配
void loop_optimized(void) {
    char* temp = (char*)tracked_malloc(50);
    
    for (int i = 0; i < 10; i++) {
        sprintf(temp, "Iteration %d", i);
        process_string(temp);
    }
    
    tracked_free(temp);  // 循环结束后释放一次
}
```

### 3.5 结构体成员泄漏

忘记释放结构体内部的动态分配内存：

```c
// 数据结构
typedef struct {
    char* name;
    int* data;
    size_t data_size;
} my_struct_t;

// 模式5：结构体成员泄漏
void struct_member_leak(void) {
    my_struct_t* obj = (my_struct_t*)tracked_malloc(sizeof(my_struct_t));
    
    // 分配成员
    obj->name = (char*)tracked_malloc(50);
    obj->data = (int*)tracked_malloc(100 * sizeof(int));
    obj->data_size = 100;
    
    strcpy(obj->name, "MyObject");
    
    // 错误：只释放了结构体本身，成员内存泄漏
    tracked_free(obj);
}

// 正确的做法：创建销毁函数
my_struct_t* create_struct(void) {
    my_struct_t* obj = (my_struct_t*)tracked_malloc(sizeof(my_struct_t));
    if (obj == NULL) return NULL;
    
    obj->name = (char*)tracked_malloc(50);
    obj->data = (int*)tracked_malloc(100 * sizeof(int));
    obj->data_size = 100;
    
    return obj;
}

void destroy_struct(my_struct_t* obj) {
    if (obj == NULL) return;
    
    // 先释放成员
    tracked_free(obj->name);
    tracked_free(obj->data);
    
    // 再释放结构体本身
    tracked_free(obj);
}

// 使用示例
void struct_correct_usage(void) {
    my_struct_t* obj = create_struct();
    
    // 使用对象
    strcpy(obj->name, "MyObject");
    
    // 正确释放
    destroy_struct(obj);
}
```


## 步骤4：使用调试工具检测泄漏

### 4.1 使用GDB检测

GDB可以帮助追踪内存分配：

```bash
# 编译时启用调试信息
gcc -g -O0 -o myprogram myprogram.c

# 启动GDB
gdb ./myprogram

# 设置断点在malloc
(gdb) break malloc
(gdb) break free

# 运行程序
(gdb) run

# 查看调用栈
(gdb) backtrace

# 查看内存内容
(gdb) x/100x 0x12345678  # 查看地址的内容
```

### 4.2 使用Valgrind（Linux）

Valgrind是强大的内存调试工具：

```bash
# 安装Valgrind
sudo apt-get install valgrind

# 运行内存检查
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --verbose \
         ./myprogram

# 输出示例
==12345== HEAP SUMMARY:
==12345==     in use at exit: 100 bytes in 1 blocks
==12345==   total heap usage: 10 allocs, 9 frees, 1,000 bytes allocated
==12345==
==12345== 100 bytes in 1 blocks are definitely lost
==12345==    at malloc (vg_replace_malloc.c:299)
==12345==    by simple_leak (test.c:45)
==12345==    by main (test.c:100)
```

### 4.3 使用AddressSanitizer

AddressSanitizer是编译器内置的内存检测工具：

```bash
# 使用GCC编译
gcc -fsanitize=address -g -O0 -o myprogram myprogram.c

# 运行程序
./myprogram

# 输出示例
=================================================================
==12345==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 100 byte(s) in 1 object(s) allocated from:
    #0 0x7f8b9c malloc
    #1 0x400abc in simple_leak test.c:45
    #2 0x400def in main test.c:100

SUMMARY: AddressSanitizer: 100 byte(s) leaked in 1 allocation(s).
```

### 4.4 嵌入式系统的调试方法

在嵌入式系统中，可以使用以下方法：

```c
// 方法1：串口输出调试信息
void debug_print_allocation(void* ptr, size_t size, 
                           const char* file, int line) {
    printf("ALLOC: %p, %zu bytes at %s:%d\n", 
           ptr, size, file, line);
}

// 方法2：使用LED指示
void indicate_memory_status(void) {
    float usage = (float)g_alloc_count / MAX_ALLOCATIONS;
    
    if (usage > 0.9) {
        // 红灯：内存使用率>90%
        set_led(LED_RED, 1);
    } else if (usage > 0.7) {
        // 黄灯：内存使用率>70%
        set_led(LED_YELLOW, 1);
    } else {
        // 绿灯：内存正常
        set_led(LED_GREEN, 1);
    }
}

// 方法3：通过UART发送统计信息
void send_memory_stats_uart(void) {
    char buffer[128];
    
    snprintf(buffer, sizeof(buffer),
             "MEM: %d/%d allocs, %lu bytes\n",
             g_alloc_count, MAX_ALLOCATIONS, 
             g_total_allocated - g_total_freed);
    
    uart_send_string(buffer);
}
```

## 步骤5：预防内存泄漏的最佳实践

### 5.1 使用RAII模式（C++）

在C++中，使用RAII（Resource Acquisition Is Initialization）：

```cpp
// C++示例
class Buffer {
private:
    char* data;
    size_t size;
    
public:
    Buffer(size_t s) : size(s) {
        data = new char[size];
    }
    
    ~Buffer() {
        delete[] data;  // 自动释放
    }
    
    // 禁止拷贝
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
};

// 使用
void use_buffer() {
    Buffer buf(1024);
    // 使用buf
    // 函数结束时自动释放，不会泄漏
}
```

### 5.2 使用配对函数（C）

在C中，使用配对的创建/销毁函数：

```c
// 配对函数模式
typedef struct {
    char* data;
    size_t size;
} buffer_t;

// 创建函数
buffer_t* buffer_create(size_t size) {
    buffer_t* buf = (buffer_t*)tracked_malloc(sizeof(buffer_t));
    if (buf == NULL) return NULL;
    
    buf->data = (char*)tracked_malloc(size);
    if (buf->data == NULL) {
        tracked_free(buf);
        return NULL;
    }
    
    buf->size = size;
    return buf;
}

// 销毁函数
void buffer_destroy(buffer_t* buf) {
    if (buf == NULL) return;
    
    tracked_free(buf->data);
    tracked_free(buf);
}

// 使用示例
void use_buffer_correct(void) {
    buffer_t* buf = buffer_create(1024);
    if (buf == NULL) return;
    
    // 使用buffer
    memcpy(buf->data, "Hello", 6);
    
    // 确保释放
    buffer_destroy(buf);
}
```

### 5.3 使用内存池

内存池可以避免频繁的malloc/free：

```c
// 内存池方式
#define POOL_SIZE 10
static buffer_t buffer_pool[POOL_SIZE];
static uint8_t pool_used[POOL_SIZE] = {0};

buffer_t* buffer_alloc_from_pool(void) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (!pool_used[i]) {
            pool_used[i] = 1;
            return &buffer_pool[i];
        }
    }
    return NULL;  // 池已满
}

void buffer_free_to_pool(buffer_t* buf) {
    int index = buf - buffer_pool;
    if (index >= 0 && index < POOL_SIZE) {
        pool_used[index] = 0;
    }
}
```

### 5.4 代码审查清单

在代码审查时检查以下项目：

```c
// 审查清单
/*
 * 内存泄漏审查清单：
 * 
 * [ ] 每个malloc都有对应的free
 * [ ] 所有错误路径都正确释放内存
 * [ ] 循环中的分配在循环内或循环后释放
 * [ ] 结构体销毁时释放所有成员
 * [ ] 函数返回前释放所有局部分配
 * [ ] 使用配对的创建/销毁函数
 * [ ] 指针重新赋值前释放原内存
 * [ ] 考虑使用内存池代替动态分配
 */
```


## 测试验证

### 测试1：基本泄漏检测

创建测试程序验证追踪系统：

```c
#include <stdio.h>
#include <string.h>

// 测试用例1：无泄漏
void test_no_leak(void) {
    printf("\n=== Test 1: No Leak ===\n");
    
    char* str = (char*)tracked_malloc(100);
    strcpy(str, "Test string");
    tracked_free(str);
    
    check_memory_leaks();
}

// 测试用例2：简单泄漏
void test_simple_leak(void) {
    printf("\n=== Test 2: Simple Leak ===\n");
    
    char* str = (char*)tracked_malloc(100);
    strcpy(str, "Leaked string");
    // 故意不释放
    
    check_memory_leaks();
}

// 测试用例3：多次泄漏
void test_multiple_leaks(void) {
    printf("\n=== Test 3: Multiple Leaks ===\n");
    
    for (int i = 0; i < 5; i++) {
        char* str = (char*)tracked_malloc(50);
        sprintf(str, "Leak %d", i);
        // 故意不释放
    }
    
    check_memory_leaks();
    print_leak_report();
}

// 测试用例4：混合场景
void test_mixed_scenario(void) {
    printf("\n=== Test 4: Mixed Scenario ===\n");
    
    // 正常分配和释放
    char* str1 = (char*)tracked_malloc(100);
    strcpy(str1, "Normal");
    tracked_free(str1);
    
    // 泄漏
    char* str2 = (char*)tracked_malloc(200);
    strcpy(str2, "Leaked");
    
    // 再次正常
    char* str3 = (char*)tracked_malloc(150);
    strcpy(str3, "Normal again");
    tracked_free(str3);
    
    check_memory_leaks();
    print_memory_stats();
}

// 主测试函数
int main(void) {
    printf("Memory Leak Detection Test Suite\n");
    printf("==================================\n");
    
    test_no_leak();
    test_simple_leak();
    test_multiple_leaks();
    test_mixed_scenario();
    
    printf("\n=== Final Report ===\n");
    print_memory_stats();
    check_memory_leaks();
    
    return 0;
}
```

**预期输出**：

```
Memory Leak Detection Test Suite
==================================

=== Test 1: No Leak ===
=== Memory Leak Report ===
✓ No memory leaks detected!
=========================

=== Test 2: Simple Leak ===
=== Memory Leak Report ===
LEAK #1:
  Address: 0x12345678
  Size: 100 bytes
  Location: test.c:15
  Timestamp: 1

✗ Found 1 memory leaks
✗ Total leaked: 100 bytes
=========================

=== Test 3: Multiple Leaks ===
=== Memory Leak Report ===
LEAK #1:
  Address: 0x12345678
  Size: 50 bytes
  Location: test.c:25
  Timestamp: 2
...
✗ Found 5 memory leaks
✗ Total leaked: 250 bytes
=========================
```

### 测试2：性能测试

测试追踪系统的性能影响：

```c
#include <time.h>

void performance_test(void) {
    const int iterations = 1000;
    clock_t start, end;
    double cpu_time_used;
    
    // 测试不带追踪的malloc
    start = clock();
    for (int i = 0; i < iterations; i++) {
        void* ptr = malloc(100);
        free(ptr);
    }
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Without tracking: %.6f seconds\n", cpu_time_used);
    
    // 测试带追踪的malloc
    start = clock();
    for (int i = 0; i < iterations; i++) {
        void* ptr = tracked_malloc(100);
        tracked_free(ptr);
    }
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("With tracking: %.6f seconds\n", cpu_time_used);
}
```

### 测试3：压力测试

测试追踪系统在高负载下的表现：

```c
void stress_test(void) {
    printf("\n=== Stress Test ===\n");
    
    void* ptrs[MAX_ALLOCATIONS];
    int alloc_count = 0;
    
    // 填满追踪表
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        ptrs[i] = tracked_malloc(64);
        if (ptrs[i] != NULL) {
            alloc_count++;
        }
    }
    
    printf("Successfully allocated %d blocks\n", alloc_count);
    
    // 尝试超出限制
    void* extra = tracked_malloc(64);
    if (extra == NULL) {
        printf("Correctly rejected allocation beyond limit\n");
    }
    
    // 释放一半
    for (int i = 0; i < alloc_count / 2; i++) {
        tracked_free(ptrs[i]);
    }
    
    print_memory_stats();
    
    // 释放剩余
    for (int i = alloc_count / 2; i < alloc_count; i++) {
        tracked_free(ptrs[i]);
    }
    
    check_memory_leaks();
}
```

## 故障排除

### 问题1：追踪表已满

**现象**：
```
WARNING: Allocation tracking table full!
```

**原因**：
- 分配次数超过MAX_ALLOCATIONS
- 有大量未释放的内存

**解决方法**：
1. 增加MAX_ALLOCATIONS的值
2. 检查是否有内存泄漏
3. 使用内存池减少动态分配

```c
// 解决方案：动态扩展追踪表
#define INITIAL_TRACKING_SIZE 100
#define MAX_TRACKING_SIZE 1000

static alloc_record_t* g_alloc_records = NULL;
static int g_tracking_capacity = 0;

void expand_tracking_table(void) {
    int new_capacity = g_tracking_capacity * 2;
    if (new_capacity > MAX_TRACKING_SIZE) {
        new_capacity = MAX_TRACKING_SIZE;
    }
    
    alloc_record_t* new_table = realloc(g_alloc_records, 
                                        new_capacity * sizeof(alloc_record_t));
    if (new_table != NULL) {
        g_alloc_records = new_table;
        g_tracking_capacity = new_capacity;
        printf("Expanded tracking table to %d entries\n", new_capacity);
    }
}
```

### 问题2：误报泄漏

**现象**：
报告了实际已释放的内存为泄漏

**原因**：
- 使用了未追踪的free
- 追踪系统bug
- 指针被修改

**解决方法**：
```c
// 添加验证机制
void validate_tracking_system(void) {
    int active_count = 0;
    
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        if (g_alloc_records[i].is_active) {
            active_count++;
            
            // 验证指针有效性
            if (g_alloc_records[i].ptr == NULL) {
                printf("ERROR: Active record with NULL pointer!\n");
            }
        }
    }
    
    if (active_count != g_alloc_count) {
        printf("ERROR: Count mismatch! Expected %d, found %d\n",
               g_alloc_count, active_count);
    }
}
```

### 问题3：性能影响过大

**现象**：
启用追踪后程序明显变慢

**原因**：
- 追踪开销过大
- 频繁的内存分配

**解决方法**：
```c
// 条件编译：仅在调试时启用
#ifdef DEBUG_MEMORY_LEAKS
    #define ENABLE_TRACKING 1
#else
    #define ENABLE_TRACKING 0
#endif

// 或使用采样追踪
static int tracking_sample_rate = 10;  // 每10次追踪1次

void track_allocation_sampled(void* ptr, size_t size, 
                              const char* file, int line) {
    static int counter = 0;
    
    if (++counter >= tracking_sample_rate) {
        track_allocation(ptr, size, file, line);
        counter = 0;
    }
}
```


## 实践项目：完整的内存管理系统

### 项目目标

创建一个生产级的内存管理和泄漏检测系统，包括：
- 内存分配追踪
- 泄漏检测和报告
- 内存使用统计
- 实时监控
- 性能分析

### 项目结构

```
memory_manager/
├── memory_tracker.h      # 追踪系统头文件
├── memory_tracker.c      # 追踪系统实现
├── memory_pool.h         # 内存池头文件
├── memory_pool.c         # 内存池实现
├── memory_stats.h        # 统计模块头文件
├── memory_stats.c        # 统计模块实现
└── test_memory.c         # 测试程序
```

### 核心代码框架

```c
// memory_tracker.h
#ifndef MEMORY_TRACKER_H
#define MEMORY_TRACKER_H

#include <stddef.h>
#include <stdint.h>

// 配置
#define MAX_ALLOCATIONS 200
#define ENABLE_STACK_TRACE 1

// 初始化追踪系统
void memory_tracker_init(void);

// 追踪函数
void* tracked_malloc(size_t size, const char* file, int line);
void* tracked_calloc(size_t num, size_t size, const char* file, int line);
void* tracked_realloc(void* ptr, size_t size, const char* file, int line);
void tracked_free(void* ptr);

// 检测和报告
void check_memory_leaks(void);
void print_memory_stats(void);
void print_leak_report(void);

// 监控
void monitor_memory_usage(void);
uint32_t get_current_usage(void);
uint32_t get_peak_usage(void);

// 宏定义
#define MALLOC(size) tracked_malloc(size, __FILE__, __LINE__)
#define CALLOC(n, s) tracked_calloc(n, s, __FILE__, __LINE__)
#define REALLOC(p, s) tracked_realloc(p, s, __FILE__, __LINE__)
#define FREE(ptr) tracked_free(ptr)

#endif // MEMORY_TRACKER_H
```

### 使用示例

```c
#include "memory_tracker.h"

int main(void) {
    // 初始化
    memory_tracker_init();
    
    // 使用追踪的内存分配
    char* str1 = (char*)MALLOC(100);
    char* str2 = (char*)MALLOC(200);
    
    if (str1 && str2) {
        strcpy(str1, "Hello");
        strcpy(str2, "World");
        
        // 正常释放
        FREE(str1);
        
        // 故意泄漏str2用于测试
    }
    
    // 检查泄漏
    check_memory_leaks();
    print_memory_stats();
    
    return 0;
}
```

## 总结

通过本教程，你学习了：

- ✅ 内存泄漏的概念、原因和危害
- ✅ 实现自定义的内存追踪系统
- ✅ 检测和报告内存泄漏的方法
- ✅ 常见的泄漏模式和解决方案
- ✅ 使用专业工具进行内存调试
- ✅ 预防内存泄漏的最佳实践

### 关键要点

1. **预防优于检测**：
   - 使用配对的创建/销毁函数
   - 采用内存池减少动态分配
   - 建立代码审查机制

2. **及早检测**：
   - 在开发阶段启用追踪
   - 定期运行泄漏检测
   - 使用自动化测试

3. **工具辅助**：
   - 使用Valgrind、AddressSanitizer等工具
   - 实现自定义追踪系统
   - 结合静态分析工具

4. **持续监控**：
   - 实时监控内存使用
   - 设置告警阈值
   - 记录和分析趋势

## 进阶挑战

尝试以下挑战来深化理解：

1. **挑战1**：扩展追踪系统支持调用栈记录
2. **挑战2**：实现内存使用的可视化界面
3. **挑战3**：添加内存分配模式分析功能
4. **挑战4**：集成到RTOS中实现任务级内存追踪
5. **挑战5**：实现自动化的泄漏修复建议

## 完整代码

完整的项目代码可以在这里下载：
- [GitHub仓库](https://github.com/embedded-knowledge/memory-leak-detection)
- 示例项目

## 下一步

建议继续学习：

- [高效内存管理系统设计](../advanced/01-memory-management-system.html) - 学习高级内存管理技术
- [堆栈溢出检测与防护](../beginner/03-stack-overflow-detection.html) - 了解栈保护
- [MMU与虚拟内存管理](01-mmu-virtual-memory.html) - 学习虚拟内存

## 参考资料

1. "Finding Memory Leaks in Embedded Systems" - Embedded.com
2. "Valgrind User Manual" - Valgrind官方文档
3. "AddressSanitizer: A Fast Address Sanity Checker" - Google Research
4. "Memory Debugging in Embedded Systems" - ARM Developer
5. "Effective C: An Introduction to Professional C Programming" by Robert C. Seacord

## 常见问题

### Q1: 在嵌入式系统中应该使用哪种泄漏检测方法？

**A**: 根据系统资源和需求选择：

**资源充足的系统**：
- 使用完整的追踪系统
- 启用详细的日志记录
- 使用专业调试工具

**资源受限的系统**：
- 使用轻量级追踪（采样）
- 仅在开发阶段启用
- 使用简单的计数器

**生产环境**：
- 使用内存池避免动态分配
- 实现简单的监控机制
- 定期检查内存使用趋势

### Q2: 如何在RTOS中检测内存泄漏？

**A**: RTOS环境的特殊考虑：

```c
// 任务级内存追踪
typedef struct {
    TaskHandle_t task;
    uint32_t allocated;
    uint32_t freed;
} task_memory_t;

void* task_tracked_malloc(size_t size) {
    TaskHandle_t current = xTaskGetCurrentTaskHandle();
    void* ptr = pvPortMalloc(size);
    
    if (ptr != NULL) {
        // 记录到任务的内存使用
        update_task_memory(current, size);
    }
    
    return ptr;
}

// 定期检查每个任务的内存使用
void check_task_memory_leaks(void) {
    for (each task) {
        if (task_memory[i].allocated != task_memory[i].freed) {
            printf("Task %s has memory leak\n", task_name);
        }
    }
}
```

### Q3: 追踪系统会影响性能吗？

**A**: 会有一定影响，但可以优化：

**性能影响**：
- 每次分配增加10-50%开销
- 内存开销：每个分配约20-40字节

**优化方法**：
1. 仅在调试版本启用
2. 使用采样追踪
3. 使用条件编译
4. 优化数据结构

```c
// 条件编译示例
#ifdef DEBUG_BUILD
    #define MALLOC(s) tracked_malloc(s, __FILE__, __LINE__)
#else
    #define MALLOC(s) malloc(s)
#endif
```

### Q4: 如何处理第三方库的内存分配？

**A**: 几种处理方法：

1. **包装第三方库**：
```c
// 包装第三方库的分配函数
void* lib_malloc_wrapper(size_t size) {
    void* ptr = lib_malloc(size);
    track_allocation(ptr, size, "third_party_lib", 0);
    return ptr;
}
```

2. **使用钩子函数**：
```c
// 如果库支持自定义分配器
lib_set_allocator(tracked_malloc, tracked_free);
```

3. **分离追踪**：
```c
// 单独追踪第三方库的内存
void track_library_memory(void) {
    size_t before = get_free_memory();
    use_third_party_library();
    size_t after = get_free_memory();
    
    size_t used = before - after;
    printf("Library used %zu bytes\n", used);
}
```

---

**练习题**：

1. 实现一个支持调用栈记录的内存追踪系统
2. 创建一个内存泄漏的自动化测试套件
3. 实现按文件和函数统计内存使用的功能
4. 开发一个内存使用的可视化工具
5. 集成追踪系统到现有的嵌入式项目中

**实践项目**：

开发一个完整的内存管理框架，包括：
- 内存池管理
- 泄漏检测
- 使用统计
- 实时监控
- 性能分析
- 自动化测试

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言！
