---
title: "动态内存分配算法"
description: "深入讲解嵌入式系统中的动态内存分配算法，包括malloc/free实现原理、内存池设计、伙伴算法、碎片管理和内存对齐技术，帮助开发者掌握高效的内存管理方法"
slug: "dynamic-memory-allocation"

# 分类信息
domain: "驱动与BSP层"
module: "内存管理"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 动态内存
  - 内存池
  - 内存分配
  - malloc
  - 碎片管理
prerequisites:
  - "memory-management-basics"
related_contents: []

# 学习信息
estimated_time: 70
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
  - 动态内存分配
  - 内存池
  - malloc实现
  - 伙伴算法
  - 内存碎片
cover_image: ""
---

# 动态内存分配算法

## 概述

动态内存分配是嵌入式系统中一个重要但需要谨慎使用的技术。与桌面系统不同，嵌入式系统的内存资源有限，动态分配不当可能导致内存碎片、泄漏和系统不稳定。完成本教程后，你将能够：

- 理解malloc/free的实现原理和工作机制
- 掌握内存池的设计和实现方法
- 了解伙伴算法等高级内存分配算法
- 学会管理和预防内存碎片
- 掌握内存对齐的原理和实现

## 背景知识

### 为什么需要动态内存分配？

在某些场景下，我们无法在编译时确定需要多少内存：

- 处理可变长度的数据（如网络数据包）
- 实现动态数据结构（如链表、树）
- 临时缓冲区的创建和销毁
- 资源的按需分配

然而，在嵌入式系统中使用动态内存分配需要权衡：

**优点**：
- 灵活性高，按需分配
- 可以节省内存（不用预留最大空间）
- 适合处理可变大小的数据

**缺点**：
- 可能产生内存碎片
- 分配/释放时间不确定
- 可能导致内存泄漏
- 需要额外的管理开销

## 核心内容

### 1. malloc/free实现原理

#### 1.1 基本概念

malloc（memory allocation）和free是C标准库提供的动态内存分配函数。

**函数原型**：

```c
void* malloc(size_t size);  // 分配size字节的内存
void free(void* ptr);       // 释放ptr指向的内存
void* calloc(size_t num, size_t size);  // 分配并清零
void* realloc(void* ptr, size_t size);  // 重新分配大小
```

#### 1.2 内存块结构

动态内存分配器通常使用链表来管理空闲和已分配的内存块。

**内存块头部结构**：

```c
typedef struct mem_block {
    size_t size;              // 块大小（包含头部）
    struct mem_block* next;   // 下一个空闲块
    int is_free;              // 是否空闲
} mem_block_t;
```

**内存布局**：

```
┌──────────────┬──────────────┬──────────────┐
│  块头部      │  用户数据    │  块头部      │
│  (metadata)  │  (payload)   │  (metadata)  │
├──────────────┼──────────────┼──────────────┤
│ size | next  │   数据区     │ size | next  │
│ is_free      │              │ is_free      │
└──────────────┴──────────────┴──────────────┘
```

#### 1.3 简单malloc实现

让我们实现一个简单的内存分配器：

```c
#include <stdint.h>
#include <stddef.h>

// 内存块头部
typedef struct block_header {
    size_t size;                    // 块大小
    struct block_header* next;      // 下一个块
    int is_free;                    // 是否空闲
} block_header_t;

// 堆内存区域
#define HEAP_SIZE 4096
static uint8_t heap_memory[HEAP_SIZE];
static block_header_t* free_list = NULL;
static int heap_initialized = 0;

// 初始化堆
void heap_init(void) {
    if (heap_initialized) return;
    
    // 创建第一个空闲块
    free_list = (block_header_t*)heap_memory;
    free_list->size = HEAP_SIZE - sizeof(block_header_t);
    free_list->next = NULL;
    free_list->is_free = 1;
    
    heap_initialized = 1;
}

// 简单的malloc实现（首次适配算法）
void* simple_malloc(size_t size) {
    if (!heap_initialized) {
        heap_init();
    }
    
    if (size == 0) return NULL;
    
    // 对齐到4字节边界
    size = (size + 3) & ~3;
    
    // 遍历空闲链表
    block_header_t* current = free_list;
    block_header_t* prev = NULL;
    
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            // 找到合适的块
            
            // 如果剩余空间足够，分割块
            if (current->size >= size + sizeof(block_header_t) + 16) {
                block_header_t* new_block = 
                    (block_header_t*)((uint8_t*)current + 
                    sizeof(block_header_t) + size);
                
                new_block->size = current->size - size - sizeof(block_header_t);
                new_block->next = current->next;
                new_block->is_free = 1;
                
                current->size = size;
                current->next = new_block;
            }
            
            current->is_free = 0;
            return (void*)((uint8_t*)current + sizeof(block_header_t));
        }
        
        prev = current;
        current = current->next;
    }
    
    return NULL;  // 没有足够的内存
}

// 简单的free实现
void simple_free(void* ptr) {
    if (ptr == NULL) return;
    
    // 获取块头部
    block_header_t* block = 
        (block_header_t*)((uint8_t*)ptr - sizeof(block_header_t));
    
    block->is_free = 1;
    
    // 合并相邻的空闲块
    block_header_t* current = free_list;
    while (current != NULL) {
        if (current->is_free && current->next != NULL && 
            current->next->is_free) {
            // 合并当前块和下一个块
            current->size += sizeof(block_header_t) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}
```

**使用示例**：

```c
void test_simple_allocator(void) {
    // 分配内存
    int* array1 = (int*)simple_malloc(10 * sizeof(int));
    char* str = (char*)simple_malloc(50);
    
    if (array1 != NULL && str != NULL) {
        // 使用内存
        for (int i = 0; i < 10; i++) {
            array1[i] = i;
        }
        
        strcpy(str, "Hello, embedded world!");
        
        // 释放内存
        simple_free(array1);
        simple_free(str);
    }
}
```

### 2. 内存分配算法

#### 2.1 首次适配（First Fit）

从链表头开始，找到第一个足够大的空闲块。

**优点**：
- 实现简单
- 分配速度快

**缺点**：
- 容易在链表前部产生小碎片
- 可能浪费大块内存

```c
// 首次适配算法
void* first_fit_malloc(size_t size) {
    block_header_t* current = free_list;
    
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            // 找到第一个合适的块
            current->is_free = 0;
            return (void*)((uint8_t*)current + sizeof(block_header_t));
        }
        current = current->next;
    }
    
    return NULL;
}
```

#### 2.2 最佳适配（Best Fit）

遍历整个链表，找到最小的足够大的空闲块。

**优点**：
- 减少内存浪费
- 更好的空间利用率

**缺点**：
- 需要遍历整个链表，速度慢
- 可能产生很多小碎片

```c
// 最佳适配算法
void* best_fit_malloc(size_t size) {
    block_header_t* current = free_list;
    block_header_t* best = NULL;
    size_t best_size = SIZE_MAX;
    
    // 遍历所有空闲块
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            if (current->size < best_size) {
                best = current;
                best_size = current->size;
            }
        }
        current = current->next;
    }
    
    if (best != NULL) {
        best->is_free = 0;
        return (void*)((uint8_t*)best + sizeof(block_header_t));
    }
    
    return NULL;
}
```

#### 2.3 最差适配（Worst Fit）

找到最大的空闲块进行分配。

**优点**：
- 分割后剩余块较大，更有用
- 减少小碎片

**缺点**：
- 浪费大块内存
- 需要遍历整个链表

```c
// 最差适配算法
void* worst_fit_malloc(size_t size) {
    block_header_t* current = free_list;
    block_header_t* worst = NULL;
    size_t worst_size = 0;
    
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            if (current->size > worst_size) {
                worst = current;
                worst_size = current->size;
            }
        }
        current = current->next;
    }
    
    if (worst != NULL) {
        worst->is_free = 0;
        return (void*)((uint8_t*)worst + sizeof(block_header_t));
    }
    
    return NULL;
}
```

### 3. 内存池设计

内存池是嵌入式系统中最常用的内存管理方法，它预先分配固定大小的内存块。

#### 3.1 固定大小内存池

**设计思路**：
- 预分配N个固定大小的内存块
- 使用链表管理空闲块
- 分配和释放都是O(1)操作

**实现**：

```c
#include <stdint.h>
#include <string.h>

// 内存池配置
#define POOL_BLOCK_SIZE 64      // 每个块64字节
#define POOL_BLOCK_COUNT 32     // 总共32个块

// 内存池结构
typedef struct {
    uint8_t memory[POOL_BLOCK_SIZE * POOL_BLOCK_COUNT];
    void* free_list;
    uint32_t free_count;
    uint32_t total_count;
} memory_pool_t;

// 初始化内存池
void pool_init(memory_pool_t* pool) {
    pool->total_count = POOL_BLOCK_COUNT;
    pool->free_count = POOL_BLOCK_COUNT;
    
    // 构建空闲链表
    pool->free_list = NULL;
    for (int i = POOL_BLOCK_COUNT - 1; i >= 0; i--) {
        void** block = (void**)&pool->memory[i * POOL_BLOCK_SIZE];
        *block = pool->free_list;
        pool->free_list = block;
    }
}

// 从内存池分配
void* pool_alloc(memory_pool_t* pool) {
    if (pool->free_list == NULL) {
        return NULL;  // 内存池已满
    }
    
    // 从空闲链表取出第一个块
    void* block = pool->free_list;
    pool->free_list = *(void**)block;
    pool->free_count--;
    
    // 清零内存块
    memset(block, 0, POOL_BLOCK_SIZE);
    
    return block;
}

// 释放到内存池
void pool_free(memory_pool_t* pool, void* ptr) {
    if (ptr == NULL) return;
    
    // 将块加入空闲链表
    *(void**)ptr = pool->free_list;
    pool->free_list = ptr;
    pool->free_count++;
}

// 获取内存池使用情况
uint32_t pool_get_usage(memory_pool_t* pool) {
    return pool->total_count - pool->free_count;
}

uint32_t pool_get_free(memory_pool_t* pool) {
    return pool->free_count;
}
```

**使用示例**：

```c
// 全局内存池
static memory_pool_t g_pool;

void test_memory_pool(void) {
    // 初始化内存池
    pool_init(&g_pool);
    
    // 分配内存
    uint8_t* buffer1 = (uint8_t*)pool_alloc(&g_pool);
    uint8_t* buffer2 = (uint8_t*)pool_alloc(&g_pool);
    
    if (buffer1 != NULL && buffer2 != NULL) {
        // 使用内存
        memcpy(buffer1, "Data 1", 7);
        memcpy(buffer2, "Data 2", 7);
        
        printf("Pool usage: %lu/%lu\n", 
               pool_get_usage(&g_pool), 
               g_pool.total_count);
        
        // 释放内存
        pool_free(&g_pool, buffer1);
        pool_free(&g_pool, buffer2);
    }
}
```

#### 3.2 多级内存池

为了支持不同大小的内存分配，可以创建多个不同大小的内存池。

```c
// 多级内存池配置
typedef struct {
    size_t block_size;
    memory_pool_t pool;
} sized_pool_t;

#define POOL_SIZES 4

// 定义不同大小的内存池
static sized_pool_t pools[POOL_SIZES] = {
    {32, {0}},   // 32字节池
    {64, {0}},   // 64字节池
    {128, {0}},  // 128字节池
    {256, {0}}   // 256字节池
};

// 初始化所有内存池
void multi_pool_init(void) {
    for (int i = 0; i < POOL_SIZES; i++) {
        pool_init(&pools[i].pool);
    }
}

// 从合适的池中分配
void* multi_pool_alloc(size_t size) {
    // 找到最小的合适池
    for (int i = 0; i < POOL_SIZES; i++) {
        if (size <= pools[i].block_size) {
            return pool_alloc(&pools[i].pool);
        }
    }
    
    return NULL;  // 请求的大小太大
}

// 释放到对应的池
void multi_pool_free(void* ptr, size_t size) {
    for (int i = 0; i < POOL_SIZES; i++) {
        if (size <= pools[i].block_size) {
            pool_free(&pools[i].pool, ptr);
            return;
        }
    }
}
```

### 4. 伙伴算法（Buddy System）

伙伴算法是一种高效的内存分配算法，它将内存分成2的幂次大小的块。

#### 4.1 基本原理

- 内存块大小为2的幂次（如8, 16, 32, 64...）
- 分配时，如果没有合适大小的块，将大块分裂成两个"伙伴"
- 释放时，如果伙伴也空闲，则合并成更大的块

**示例**：

```
初始状态: [256字节空闲块]

分配70字节:
1. 256 → 128 + 128
2. 128 → 64 + 64
3. 64 → 32 + 32 (不够)
4. 128 → 64 + 64 (不够)
5. 分配128字节块

结果: [128已分配] [128空闲]
```

#### 4.2 简化实现

```c
#include <stdint.h>

#define MIN_BLOCK_SIZE 32       // 最小块32字节
#define MAX_BLOCK_SIZE 2048     // 最大块2KB
#define BUDDY_LEVELS 7          // log2(2048/32) + 1

typedef struct buddy_block {
    struct buddy_block* next;
    int is_free;
} buddy_block_t;

// 每个级别的空闲链表
static buddy_block_t* free_lists[BUDDY_LEVELS];
static uint8_t buddy_memory[MAX_BLOCK_SIZE];

// 计算块的级别
static int get_level(size_t size) {
    int level = 0;
    size_t block_size = MIN_BLOCK_SIZE;
    
    while (block_size < size && level < BUDDY_LEVELS - 1) {
        block_size *= 2;
        level++;
    }
    
    return level;
}

// 获取级别对应的块大小
static size_t get_block_size(int level) {
    return MIN_BLOCK_SIZE << level;
}

// 初始化伙伴系统
void buddy_init(void) {
    // 清空所有链表
    for (int i = 0; i < BUDDY_LEVELS; i++) {
        free_lists[i] = NULL;
    }
    
    // 将整个内存作为最大块加入
    buddy_block_t* block = (buddy_block_t*)buddy_memory;
    block->next = NULL;
    block->is_free = 1;
    free_lists[BUDDY_LEVELS - 1] = block;
}

// 分裂块
static void split_block(int level) {
    if (level >= BUDDY_LEVELS - 1) return;
    if (free_lists[level + 1] == NULL) {
        split_block(level + 1);
    }
    
    if (free_lists[level + 1] != NULL) {
        // 取出大块
        buddy_block_t* block = free_lists[level + 1];
        free_lists[level + 1] = block->next;
        
        // 分裂成两个伙伴
        size_t half_size = get_block_size(level);
        buddy_block_t* buddy = 
            (buddy_block_t*)((uint8_t*)block + half_size);
        
        // 加入小块链表
        block->next = buddy;
        buddy->next = free_lists[level];
        block->is_free = 1;
        buddy->is_free = 1;
        free_lists[level] = block;
    }
}

// 伙伴系统分配
void* buddy_alloc(size_t size) {
    int level = get_level(size);
    
    // 如果该级别没有空闲块，分裂更大的块
    if (free_lists[level] == NULL) {
        split_block(level);
    }
    
    if (free_lists[level] != NULL) {
        // 取出空闲块
        buddy_block_t* block = free_lists[level];
        free_lists[level] = block->next;
        block->is_free = 0;
        return (void*)block;
    }
    
    return NULL;
}

// 伙伴系统释放
void buddy_free(void* ptr, size_t size) {
    if (ptr == NULL) return;
    
    int level = get_level(size);
    buddy_block_t* block = (buddy_block_t*)ptr;
    
    // 标记为空闲
    block->is_free = 1;
    block->next = free_lists[level];
    free_lists[level] = block;
    
    // TODO: 实现伙伴合并逻辑
}
```

### 5. 内存碎片管理

#### 5.1 内存碎片类型

**外部碎片**：
- 空闲内存块太小，无法满足分配请求
- 虽然总空闲内存足够，但不连续

**内部碎片**：
- 分配的内存块大于实际需求
- 浪费的空间无法被其他分配使用

#### 5.2 碎片整理

在某些情况下，可以通过移动已分配的内存块来整理碎片。

```c
// 简单的碎片整理（仅适用于可移动的对象）
void defragment_memory(void) {
    block_header_t* current = free_list;
    
    while (current != NULL && current->next != NULL) {
        // 如果当前块和下一个块都空闲，合并它们
        if (current->is_free && current->next->is_free) {
            current->size += sizeof(block_header_t) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}
```

#### 5.3 预防碎片化

**最佳实践**：

1. **使用内存池**：预分配固定大小的块
2. **避免频繁分配释放**：重用内存块
3. **按大小分组**：使用多级内存池
4. **预留缓冲区**：使用静态缓冲区代替动态分配
5. **合并空闲块**：及时合并相邻的空闲块

### 6. 内存对齐

#### 6.1 为什么需要对齐？

现代处理器要求数据按特定边界对齐：
- 提高访问效率
- 某些指令要求对齐
- 避免硬件异常

**对齐规则**：
- 1字节数据：任意地址
- 2字节数据：2字节边界
- 4字节数据：4字节边界
- 8字节数据：8字节边界

#### 6.2 对齐实现

```c
// 向上对齐到指定边界
#define ALIGN_UP(size, align) (((size) + (align) - 1) & ~((align) - 1))

// 向下对齐到指定边界
#define ALIGN_DOWN(size, align) ((size) & ~((align) - 1))

// 检查是否对齐
#define IS_ALIGNED(ptr, align) (((uintptr_t)(ptr) & ((align) - 1)) == 0)

// 对齐分配示例
void* aligned_malloc(size_t size, size_t alignment) {
    // 分配额外空间用于对齐
    size_t total_size = size + alignment + sizeof(void*);
    void* raw_ptr = simple_malloc(total_size);
    
    if (raw_ptr == NULL) return NULL;
    
    // 计算对齐后的地址
    uintptr_t aligned_addr = 
        ALIGN_UP((uintptr_t)raw_ptr + sizeof(void*), alignment);
    void* aligned_ptr = (void*)aligned_addr;
    
    // 在对齐地址前保存原始指针
    ((void**)aligned_ptr)[-1] = raw_ptr;
    
    return aligned_ptr;
}

// 释放对齐分配的内存
void aligned_free(void* ptr) {
    if (ptr == NULL) return;
    
    // 获取原始指针
    void* raw_ptr = ((void**)ptr)[-1];
    simple_free(raw_ptr);
}
```

**使用示例**：

```c
void test_aligned_allocation(void) {
    // 分配16字节对齐的内存
    float* aligned_array = (float*)aligned_malloc(64, 16);
    
    if (aligned_array != NULL) {
        // 检查对齐
        if (IS_ALIGNED(aligned_array, 16)) {
            printf("Memory is properly aligned\n");
        }
        
        // 使用内存
        for (int i = 0; i < 16; i++) {
            aligned_array[i] = i * 1.5f;
        }
        
        // 释放内存
        aligned_free(aligned_array);
    }
}
```

## 实践示例

### 示例1：完整的内存池系统

让我们实现一个带统计功能的完整内存池系统：

```c
#include <stdint.h>
#include <string.h>
#include <stdio.h>

// 内存池统计信息
typedef struct {
    uint32_t total_allocs;      // 总分配次数
    uint32_t total_frees;       // 总释放次数
    uint32_t current_usage;     // 当前使用量
    uint32_t peak_usage;        // 峰值使用量
    uint32_t failed_allocs;     // 失败的分配次数
} pool_stats_t;

// 增强的内存池
typedef struct {
    uint8_t* memory;
    void* free_list;
    uint32_t block_size;
    uint32_t block_count;
    uint32_t free_count;
    pool_stats_t stats;
} enhanced_pool_t;

// 初始化增强内存池
void enhanced_pool_init(enhanced_pool_t* pool, 
                       uint8_t* memory,
                       uint32_t block_size, 
                       uint32_t block_count) {
    pool->memory = memory;
    pool->block_size = block_size;
    pool->block_count = block_count;
    pool->free_count = block_count;
    
    // 清空统计
    memset(&pool->stats, 0, sizeof(pool_stats_t));
    
    // 构建空闲链表
    pool->free_list = NULL;
    for (int i = block_count - 1; i >= 0; i--) {
        void** block = (void**)&memory[i * block_size];
        *block = pool->free_list;
        pool->free_list = block;
    }
}

// 从增强内存池分配
void* enhanced_pool_alloc(enhanced_pool_t* pool) {
    if (pool->free_list == NULL) {
        pool->stats.failed_allocs++;
        return NULL;
    }
    
    // 取出空闲块
    void* block = pool->free_list;
    pool->free_list = *(void**)block;
    pool->free_count--;
    
    // 更新统计
    pool->stats.total_allocs++;
    pool->stats.current_usage++;
    if (pool->stats.current_usage > pool->stats.peak_usage) {
        pool->stats.peak_usage = pool->stats.current_usage;
    }
    
    // 清零内存
    memset(block, 0, pool->block_size);
    
    return block;
}

// 释放到增强内存池
void enhanced_pool_free(enhanced_pool_t* pool, void* ptr) {
    if (ptr == NULL) return;
    
    // 验证指针是否属于这个池
    uintptr_t pool_start = (uintptr_t)pool->memory;
    uintptr_t pool_end = pool_start + 
                         (pool->block_size * pool->block_count);
    uintptr_t ptr_addr = (uintptr_t)ptr;
    
    if (ptr_addr < pool_start || ptr_addr >= pool_end) {
        // 指针不属于这个池
        return;
    }
    
    // 加入空闲链表
    *(void**)ptr = pool->free_list;
    pool->free_list = ptr;
    pool->free_count++;
    
    // 更新统计
    pool->stats.total_frees++;
    pool->stats.current_usage--;
}

// 打印内存池统计信息
void enhanced_pool_print_stats(enhanced_pool_t* pool) {
    printf("Memory Pool Statistics:\n");
    printf("  Block size: %lu bytes\n", pool->block_size);
    printf("  Total blocks: %lu\n", pool->block_count);
    printf("  Free blocks: %lu\n", pool->free_count);
    printf("  Used blocks: %lu\n", 
           pool->block_count - pool->free_count);
    printf("  Total allocations: %lu\n", pool->stats.total_allocs);
    printf("  Total frees: %lu\n", pool->stats.total_frees);
    printf("  Failed allocations: %lu\n", pool->stats.failed_allocs);
    printf("  Current usage: %lu blocks\n", pool->stats.current_usage);
    printf("  Peak usage: %lu blocks\n", pool->stats.peak_usage);
    printf("  Utilization: %.1f%%\n", 
           (float)pool->stats.current_usage * 100 / pool->block_count);
}
```

**使用示例**：

```c
#define POOL_BLOCK_SIZE 128
#define POOL_BLOCK_COUNT 50

static uint8_t pool_memory[POOL_BLOCK_SIZE * POOL_BLOCK_COUNT];
static enhanced_pool_t my_pool;

void test_enhanced_pool(void) {
    // 初始化内存池
    enhanced_pool_init(&my_pool, pool_memory, 
                      POOL_BLOCK_SIZE, POOL_BLOCK_COUNT);
    
    // 模拟使用场景
    void* buffers[10];
    
    // 分配多个块
    for (int i = 0; i < 10; i++) {
        buffers[i] = enhanced_pool_alloc(&my_pool);
        if (buffers[i] != NULL) {
            sprintf((char*)buffers[i], "Buffer %d", i);
        }
    }
    
    // 打印统计
    enhanced_pool_print_stats(&my_pool);
    
    // 释放一些块
    for (int i = 0; i < 5; i++) {
        enhanced_pool_free(&my_pool, buffers[i]);
    }
    
    // 再次打印统计
    printf("\nAfter freeing 5 blocks:\n");
    enhanced_pool_print_stats(&my_pool);
    
    // 释放剩余块
    for (int i = 5; i < 10; i++) {
        enhanced_pool_free(&my_pool, buffers[i]);
    }
}
```

### 示例2：内存泄漏检测

实现一个简单的内存泄漏检测机制：

```c
#include <stdint.h>
#include <stdio.h>

#define MAX_ALLOCATIONS 100

// 分配记录
typedef struct {
    void* ptr;
    size_t size;
    const char* file;
    int line;
    uint32_t timestamp;
} alloc_record_t;

// 分配跟踪器
static alloc_record_t alloc_records[MAX_ALLOCATIONS];
static int alloc_count = 0;
static uint32_t alloc_id = 0;

// 记录分配
static void record_alloc(void* ptr, size_t size, 
                        const char* file, int line) {
    if (alloc_count < MAX_ALLOCATIONS) {
        alloc_records[alloc_count].ptr = ptr;
        alloc_records[alloc_count].size = size;
        alloc_records[alloc_count].file = file;
        alloc_records[alloc_count].line = line;
        alloc_records[alloc_count].timestamp = alloc_id++;
        alloc_count++;
    }
}

// 记录释放
static void record_free(void* ptr) {
    for (int i = 0; i < alloc_count; i++) {
        if (alloc_records[i].ptr == ptr) {
            // 移除记录
            for (int j = i; j < alloc_count - 1; j++) {
                alloc_records[j] = alloc_records[j + 1];
            }
            alloc_count--;
            return;
        }
    }
    
    // 如果没找到，可能是重复释放或野指针
    printf("WARNING: Freeing untracked pointer %p\n", ptr);
}

// 带跟踪的malloc
#define tracked_malloc(size) \
    tracked_malloc_impl(size, __FILE__, __LINE__)

void* tracked_malloc_impl(size_t size, const char* file, int line) {
    void* ptr = simple_malloc(size);
    if (ptr != NULL) {
        record_alloc(ptr, size, file, line);
    }
    return ptr;
}

// 带跟踪的free
void tracked_free(void* ptr) {
    record_free(ptr);
    simple_free(ptr);
}

// 检查内存泄漏
void check_memory_leaks(void) {
    if (alloc_count == 0) {
        printf("No memory leaks detected!\n");
        return;
    }
    
    printf("Memory leak detected! %d allocations not freed:\n", 
           alloc_count);
    
    size_t total_leaked = 0;
    for (int i = 0; i < alloc_count; i++) {
        printf("  [%u] %zu bytes at %p (%s:%d)\n",
               alloc_records[i].timestamp,
               alloc_records[i].size,
               alloc_records[i].ptr,
               alloc_records[i].file,
               alloc_records[i].line);
        total_leaked += alloc_records[i].size;
    }
    
    printf("Total leaked: %zu bytes\n", total_leaked);
}
```

**使用示例**：

```c
void test_leak_detection(void) {
    // 正常使用
    char* str1 = (char*)tracked_malloc(50);
    strcpy(str1, "Hello");
    tracked_free(str1);
    
    // 内存泄漏
    char* str2 = (char*)tracked_malloc(100);
    strcpy(str2, "World");
    // 忘记释放str2
    
    // 检查泄漏
    check_memory_leaks();
}
```

## 深入理解

### 内存分配器的性能考虑

选择内存分配算法时需要考虑：

1. **分配速度**：
   - 首次适配：O(n)
   - 最佳适配：O(n)
   - 内存池：O(1)

2. **空间利用率**：
   - 最佳适配：最高
   - 首次适配：中等
   - 内存池：可能较低（固定大小）

3. **碎片化程度**：
   - 内存池：无碎片
   - 伙伴算法：内部碎片
   - 首次适配：外部碎片

4. **实时性**：
   - 内存池：确定性最好
   - malloc/free：不确定

### 嵌入式系统的选择建议

**推荐使用内存池的场景**：
- 实时系统
- 对象大小固定或可预测
- 需要确定性的分配时间
- 内存资源有限

**可以使用malloc/free的场景**：
- 非实时系统
- 对象大小变化大
- 内存充足
- 开发原型阶段

**混合策略**：
- 关键路径使用内存池
- 非关键路径使用动态分配
- 启动阶段使用动态分配，运行时使用静态

### 最佳实践

1. **优先使用静态分配**
   ```c
   // 好的做法
   static uint8_t buffer[1024];
   
   // 避免
   uint8_t* buffer = malloc(1024);
   ```

2. **使用内存池管理动态对象**
   ```c
   // 为特定类型创建内存池
   typedef struct {
       int id;
       char name[32];
       // ...
   } my_object_t;
   
   static my_object_t object_pool[MAX_OBJECTS];
   ```

3. **限制动态分配的使用**
   ```c
   // 只在初始化时分配
   void init(void) {
       buffer = malloc(size);
   }
   
   // 运行时不再分配
   void runtime_function(void) {
       // 使用已分配的buffer
   }
   ```

4. **使用RAII模式（C++）或配对函数（C）**
   ```c
   // 配对的分配和释放
   void* create_resource(void) {
       return pool_alloc(&pool);
   }
   
   void destroy_resource(void* res) {
       pool_free(&pool, res);
   }
   ```

5. **定期检查内存使用**
   ```c
   void monitor_memory(void) {
       uint32_t usage = pool_get_usage(&pool);
       uint32_t total = pool.total_count;
       
       if (usage > total * 0.9) {
           printf("WARNING: Memory usage > 90%%\n");
       }
   }
   ```

## 常见问题

### Q1: 什么时候应该使用动态内存分配？

**A**: 在嵌入式系统中，应该尽量避免使用动态内存分配。只在以下情况考虑：

**可以使用的场景**：
- 初始化阶段的一次性分配
- 数据大小在运行时才能确定
- 需要实现复杂的数据结构（如链表、树）
- 有足够的内存和时间余量

**应该避免的场景**：
- 实时任务中
- 中断服务程序中
- 频繁分配和释放
- 内存非常有限的系统

**替代方案**：
- 使用静态数组
- 使用内存池
- 预分配最大可能的空间

### Q2: 内存池和malloc/free有什么区别？

**A**: 主要区别：

| 特性 | 内存池 | malloc/free |
|------|--------|-------------|
| 分配速度 | O(1)，非常快 | O(n)，较慢 |
| 碎片化 | 无外部碎片 | 可能产生碎片 |
| 确定性 | 确定性好 | 不确定 |
| 灵活性 | 固定大小 | 任意大小 |
| 开销 | 低 | 较高 |
| 适用场景 | 实时系统 | 通用场景 |

**选择建议**：
- 实时系统：使用内存池
- 对象大小固定：使用内存池
- 对象大小变化大：考虑多级内存池或malloc
- 原型开发：可以先用malloc，后期优化为内存池

### Q3: 如何检测和预防内存泄漏？

**A**: 多种方法：

**1. 代码审查**：
- 检查每个malloc是否有对应的free
- 使用静态分析工具

**2. 运行时跟踪**：
```c
// 使用前面实现的跟踪机制
void* ptr = tracked_malloc(100);
// ...
tracked_free(ptr);
check_memory_leaks();  // 定期检查
```

**3. 使用工具**：
- Valgrind（Linux）
- AddressSanitizer
- 嵌入式专用工具

**4. 设计模式**：
- 使用配对的创建/销毁函数
- 明确内存所有权
- 使用智能指针（C++）

**5. 定期监控**：
```c
void periodic_check(void) {
    uint32_t free_mem = get_free_memory();
    if (free_mem < threshold) {
        log_warning("Low memory");
    }
}
```

### Q4: 伙伴算法相比其他算法有什么优势？

**A**: 伙伴算法的特点：

**优势**：
- 分配和释放速度快（O(log n)）
- 合并空闲块简单高效
- 减少外部碎片
- 实现相对简单

**劣势**：
- 存在内部碎片（2的幂次大小）
- 可能浪费空间（如请求65字节需要分配128字节）
- 需要额外的管理结构

**适用场景**：
- 内存充足的系统
- 需要支持多种大小的分配
- 对碎片化敏感的应用
- 操作系统内核

**示例**：
```c
// 请求70字节
// 伙伴算法会分配128字节（浪费58字节）
void* ptr = buddy_alloc(70);  // 实际分配128字节

// 内存池会分配固定大小
void* ptr = pool_alloc(&pool_128);  // 分配128字节块
```

### Q5: 如何选择内存池的块大小？

**A**: 选择策略：

**1. 分析实际使用**：
```c
// 统计实际分配的大小
void analyze_allocations(void) {
    // 记录每次分配的大小
    // 分析大小分布
    // 选择覆盖80-90%场景的大小
}
```

**2. 常见策略**：
- 小对象池：32, 64, 128字节
- 中等对象池：256, 512字节
- 大对象池：1024, 2048字节

**3. 多级池设计**：
```c
// 根据使用频率配置不同大小的池
static sized_pool_t pools[] = {
    {32,  100},  // 小对象，数量多
    {64,  50},   // 中等对象
    {128, 30},   // 较大对象
    {256, 10}    // 大对象，数量少
};
```

**4. 动态调整**：
```c
// 运行时监控使用情况
void monitor_pool_usage(void) {
    for (int i = 0; i < POOL_COUNT; i++) {
        float usage = get_pool_usage(&pools[i]);
        if (usage > 0.9) {
            log_warning("Pool %d usage high: %.1f%%", 
                       i, usage * 100);
        }
    }
}
```

## 总结

本教程深入讲解了动态内存分配的原理和实现，核心要点包括：

- **malloc/free原理**：基于链表的内存块管理
- **分配算法**：首次适配、最佳适配、最差适配各有优劣
- **内存池**：嵌入式系统的最佳选择，O(1)分配，无碎片
- **伙伴算法**：平衡了速度和空间利用率
- **碎片管理**：预防比治理更重要
- **内存对齐**：提高访问效率，满足硬件要求

在嵌入式系统开发中，应该：
1. 优先使用静态分配
2. 需要动态分配时首选内存池
3. 避免在实时任务中使用malloc/free
4. 定期监控内存使用情况
5. 使用工具检测内存泄漏

掌握这些技术后，你就能够设计出高效、可靠的内存管理系统。

## 延伸阅读

- [堆栈溢出检测与防护](03-stack-overflow-detection.html) - 学习栈保护技术
- [MMU与虚拟内存管理](../intermediate/01-mmu-virtual-memory.html) - 了解高级内存管理
- [内存泄漏检测与分析](../intermediate/02-memory-leak-detection.html) - 深入学习调试技术

## 参考资料

1. "Dynamic Memory Allocation in Embedded Systems" - Embedded.com
2. "The Art of Memory Management" - Embedded Systems Programming
3. "Memory Management Algorithms and Implementation in C/C++" by Bill Blunden
4. ARM Cortex-M Memory Management - ARM官方文档
5. "Embedded Systems Architecture" by Tammy Noergaard

---

**练习题**：

1. 实现一个简单的malloc/free，支持首次适配算法和块合并。
2. 设计一个多级内存池系统，支持32、64、128、256字节四种大小。
3. 实现伙伴算法的完整版本，包括块分裂和合并。
4. 编写一个内存泄漏检测工具，能够追踪所有分配和释放操作。
5. 比较不同分配算法的性能，测试分配速度和碎片化程度。

**实践项目**：

创建一个完整的内存管理系统，包括：
- 多级内存池
- 统计和监控功能
- 内存泄漏检测
- 碎片整理功能
- 性能分析工具

**下一步**：建议学习 [堆栈溢出检测与防护](03-stack-overflow-detection.html)，了解如何保护栈内存。

