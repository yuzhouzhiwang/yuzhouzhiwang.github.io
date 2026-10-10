---
title: "算法复杂度与性能分析：嵌入式系统中的智能选择"
description: "深入讲解时间复杂度、空间复杂度、算法选择、性能评估和优化方法，帮助嵌入式开发者在资源受限环境中做出最优算法决策"
slug: "algorithm-complexity"

# 分类信息
domain: "工具链"
module: "性能优化"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 算法复杂度
  - 性能分析
  - 算法优化
  - 时间复杂度
  - 空间复杂度
prerequisites:
  - "了解基本数据结构"
  - "掌握C语言编程"
  - "理解嵌入式系统限制"
related_contents:
  - "code-optimization-basics"
  - "memory-optimization"
  - "execution-time-measurement"

# 学习信息
estimated_time: 45
difficulty_score: 4

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
  - 算法复杂度
  - 性能分析
  - 算法选择
  - 大O符号
  - 嵌入式算法
cover_image: ""
---

# 算法复杂度与性能分析：嵌入式系统中的智能选择

## 概述

在嵌入式系统开发中，选择正确的算法往往比优化代码实现更重要。一个O(n²)的算法无论如何优化，在大数据集上都无法与O(n log n)的算法竞争。本文将深入探讨算法复杂度的概念、如何分析和评估算法性能，以及在资源受限的嵌入式环境中如何做出最优的算法选择。

通过理解算法复杂度，你将能够：
- 预测算法在不同数据规模下的性能表现
- 在时间和空间之间做出明智的权衡
- 选择最适合嵌入式场景的算法
- 避免性能陷阱和常见误区

### 为什么算法复杂度在嵌入式系统中至关重要？

**资源限制的现实**:
- **处理器性能有限**: 无法通过暴力计算解决问题
- **内存容量受限**: 必须考虑空间复杂度
- **实时性要求**: 必须在规定时间内完成任务
- **功耗敏感**: 高效算法意味着更低的功耗
- **可预测性**: 需要知道最坏情况下的性能

**算法选择的影响**:
```c
// 示例：在1000个元素中查找
// 线性查找: O(n) = 1000次比较
// 二分查找: O(log n) = 10次比较
// 性能差异: 100倍！
```

这种差异在嵌入式系统中可能意味着：
- 任务能否在deadline内完成
- 电池能用1天还是1个月
- 系统能否响应实时事件



## 时间复杂度基础

### 大O符号（Big O Notation）

**定义**: 描述算法执行时间如何随输入规模增长

**常见复杂度**:

| 符号 | 名称 | 示例 | n=10 | n=100 | n=1000 |
|------|------|------|------|-------|--------|
| O(1) | 常数 | 数组访问 | 1 | 1 | 1 |
| O(log n) | 对数 | 二分查找 | 3 | 7 | 10 |
| O(n) | 线性 | 线性查找 | 10 | 100 | 1000 |
| O(n log n) | 线性对数 | 快速排序 | 30 | 700 | 10000 |
| O(n²) | 平方 | 冒泡排序 | 100 | 10000 | 1000000 |
| O(2ⁿ) | 指数 | 递归斐波那契 | 1024 | 1.27e30 | - |

**可视化对比**:
```
操作次数
    |
1M  |                                    O(n²)
    |                                  /
100K|                            O(n log n)
    |                          /
10K |                    O(n)
    |                  /
1K  |            O(log n)
    |          /
100 |    O(1)
    |________________________________________
        10    100   1000  10000  输入规模(n)
```

### 复杂度分析方法

**规则1: 忽略常数因子**
```c
// 这两个函数都是O(n)
void function1(int *arr, int n) {
    for (int i = 0; i < n; i++) {
        arr[i] = i;
    }
}

void function2(int *arr, int n) {
    for (int i = 0; i < n; i++) {
        arr[i] = i * 2 + 5;  // 更多操作，但仍是O(n)
    }
}
```

**规则2: 只保留最高阶项**
```c
// O(n² + n + 1) = O(n²)
void function(int *arr, int n) {
    // O(n²)
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            arr[i] += arr[j];
        }
    }
    
    // O(n)
    for (int i = 0; i < n; i++) {
        arr[i]++;
    }
    
    // O(1)
    int sum = 0;
}
```

**规则3: 嵌套循环相乘**
```c
// O(n * m)
void function(int n, int m) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            // 操作
        }
    }
}

// O(n²)
void function2(int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            // 操作
        }
    }
}
```

**规则4: 顺序执行相加**
```c
// O(n + m)
void function(int *arr1, int n, int *arr2, int m) {
    // O(n)
    for (int i = 0; i < n; i++) {
        process(arr1[i]);
    }
    
    // O(m)
    for (int i = 0; i < m; i++) {
        process(arr2[i]);
    }
}
```



### 常见算法复杂度分析

**O(1) - 常数时间**:
```c
// 数组访问
int get_element(int *arr, int index) {
    return arr[index];  // O(1)
}

// 哈希表查找（平均情况）
int hash_lookup(HashTable *table, int key) {
    int index = hash(key) % table->size;
    return table->data[index];  // O(1)
}

// 位操作
bool is_power_of_two(uint32_t n) {
    return (n != 0) && ((n & (n - 1)) == 0);  // O(1)
}
```

**O(log n) - 对数时间**:
```c
// 二分查找
int binary_search(int *arr, int size, int target) {
    int left = 0, right = size - 1;
    
    while (left <= right) {  // 每次循环减半
        int mid = left + (right - left) / 2;
        
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
// 复杂度分析: 每次迭代搜索空间减半
// 迭代次数 = log₂(n)

// 平衡二叉树查找
Node *bst_search(Node *root, int value) {
    if (root == NULL || root->value == value) {
        return root;
    }
    
    if (value < root->value) {
        return bst_search(root->left, value);
    } else {
        return bst_search(root->right, value);
    }
}
// 树高 = log₂(n)，每层访问一个节点
```

**O(n) - 线性时间**:
```c
// 线性查找
int linear_search(int *arr, int size, int target) {
    for (int i = 0; i < size; i++) {  // 最多n次
        if (arr[i] == target) {
            return i;
        }
    }
    return -1;
}

// 数组求和
int sum_array(int *arr, int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {  // 恰好n次
        sum += arr[i];
    }
    return sum;
}

// 链表遍历
int list_length(Node *head) {
    int count = 0;
    while (head != NULL) {  // 访问每个节点一次
        count++;
        head = head->next;
    }
    return count;
}
```

**O(n log n) - 线性对数时间**:
```c
// 快速排序（平均情况）
void quick_sort(int *arr, int left, int right) {
    if (left < right) {
        int pivot = partition(arr, left, right);  // O(n)
        quick_sort(arr, left, pivot - 1);         // T(n/2)
        quick_sort(arr, pivot + 1, right);        // T(n/2)
    }
}
// 递归关系: T(n) = 2T(n/2) + O(n) = O(n log n)

// 归并排序
void merge_sort(int *arr, int left, int right) {
    if (left < right) {
        int mid = (left + right) / 2;
        merge_sort(arr, left, mid);      // T(n/2)
        merge_sort(arr, mid + 1, right); // T(n/2)
        merge(arr, left, mid, right);    // O(n)
    }
}
// 递归关系: T(n) = 2T(n/2) + O(n) = O(n log n)
```

**O(n²) - 平方时间**:
```c
// 冒泡排序
void bubble_sort(int *arr, int size) {
    for (int i = 0; i < size - 1; i++) {        // n次
        for (int j = 0; j < size - i - 1; j++) { // n次
            if (arr[j] > arr[j + 1]) {
                swap(&arr[j], &arr[j + 1]);
            }
        }
    }
}
// 总操作: n * n = n²

// 选择排序
void selection_sort(int *arr, int size) {
    for (int i = 0; i < size - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < size; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        swap(&arr[i], &arr[min_idx]);
    }
}

// 矩阵乘法（朴素算法）
void matrix_multiply(int A[][N], int B[][N], int C[][N], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
            for (int k = 0; k < n; k++) {  // 三重循环 = O(n³)
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}
```



## 空间复杂度分析

### 空间复杂度的重要性

在嵌入式系统中，空间复杂度往往比时间复杂度更关键：
- RAM通常只有几KB到几百KB
- 栈空间非常有限
- 无法使用虚拟内存
- 内存分配失败会导致系统崩溃

**空间复杂度的组成**:
```c
// 空间 = 输入空间 + 辅助空间 + 输出空间
// 通常只计算辅助空间
```

### 常见空间复杂度

**O(1) - 常数空间**:
```c
// 原地交换
void swap(int *a, int *b) {
    int temp = *a;  // 只需要一个临时变量
    *a = *b;
    *b = temp;
}

// 原地反转数组
void reverse_array(int *arr, int size) {
    int left = 0, right = size - 1;
    while (left < right) {
        swap(&arr[left], &arr[right]);
        left++;
        right--;
    }
}
// 只使用固定数量的变量，与输入大小无关
```

**O(log n) - 对数空间**:
```c
// 二分查找（递归实现）
int binary_search_recursive(int *arr, int left, int right, int target) {
    if (left > right) {
        return -1;
    }
    
    int mid = left + (right - left) / 2;
    
    if (arr[mid] == target) {
        return mid;
    } else if (arr[mid] < target) {
        return binary_search_recursive(arr, mid + 1, right, target);
    } else {
        return binary_search_recursive(arr, left, mid - 1, target);
    }
}
// 递归深度 = log₂(n)
// 每层递归需要栈空间
```

**O(n) - 线性空间**:
```c
// 归并排序需要额外数组
void merge_sort(int *arr, int size) {
    int *temp = malloc(size * sizeof(int));  // O(n)空间
    merge_sort_helper(arr, temp, 0, size - 1);
    free(temp);
}

// 复制数组
int *copy_array(int *arr, int size) {
    int *copy = malloc(size * sizeof(int));  // O(n)空间
    for (int i = 0; i < size; i++) {
        copy[i] = arr[i];
    }
    return copy;
}

// 递归树遍历
void print_tree(Node *root) {
    if (root == NULL) return;
    
    print_tree(root->left);   // 递归深度最多n
    printf("%d ", root->value);
    print_tree(root->right);
}
// 最坏情况（链状树）: O(n)栈空间
// 平衡树: O(log n)栈空间
```

**O(n²) - 平方空间**:
```c
// 邻接矩阵表示图
typedef struct {
    int vertices;
    int **adj_matrix;  // n×n矩阵
} Graph;

Graph *create_graph(int n) {
    Graph *g = malloc(sizeof(Graph));
    g->vertices = n;
    g->adj_matrix = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        g->adj_matrix[i] = calloc(n, sizeof(int));
    }
    return g;
}
// 空间: n² 个整数
```

### 时间-空间权衡

**案例1: 斐波那契数列**

```c
// 方法1: 递归 - O(2ⁿ)时间, O(n)空间
int fib_recursive(int n) {
    if (n <= 1) return n;
    return fib_recursive(n-1) + fib_recursive(n-2);
}

// 方法2: 动态规划 - O(n)时间, O(n)空间
int fib_dp(int n) {
    int *dp = malloc((n+1) * sizeof(int));
    dp[0] = 0;
    dp[1] = 1;
    
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    
    int result = dp[n];
    free(dp);
    return result;
}

// 方法3: 优化DP - O(n)时间, O(1)空间
int fib_optimized(int n) {
    if (n <= 1) return n;
    
    int prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}
```

**案例2: 查找表 vs 计算**

```c
// 方法1: 预计算查找表 - O(1)时间, O(n)空间
const uint8_t sin_table[360] = {
    0, 2, 4, 7, /* ... 预计算的正弦值 ... */
};

uint8_t get_sin_fast(int angle) {
    return sin_table[angle % 360];  // O(1)
}

// 方法2: 实时计算 - O(1)时间, O(1)空间
uint8_t get_sin_calc(int angle) {
    return (uint8_t)(sin(angle * PI / 180) * 255);  // 慢但省空间
}

// 嵌入式选择: 通常选择查找表
// - Flash充足，RAM紧张
// - 速度比空间更重要
```



## 算法选择指南

### 排序算法对比

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定性 | 适用场景 |
|------|---------|---------|------|--------|---------|
| 冒泡排序 | O(n²) | O(n²) | O(1) | 稳定 | 小数据集，教学 |
| 选择排序 | O(n²) | O(n²) | O(1) | 不稳定 | 小数据集 |
| 插入排序 | O(n²) | O(n²) | O(1) | 稳定 | 小数据集，近似有序 |
| 快速排序 | O(n log n) | O(n²) | O(log n) | 不稳定 | 通用，大数据集 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | 稳定 | 需要稳定性 |
| 堆排序 | O(n log n) | O(n log n) | O(1) | 不稳定 | 内存受限 |
| 计数排序 | O(n+k) | O(n+k) | O(k) | 稳定 | 整数，范围小 |

**嵌入式场景选择**:

```c
// 场景1: 小数据集（<50个元素）
// 推荐: 插入排序
void sort_small_array(int *arr, int size) {
    for (int i = 1; i < size; i++) {
        int key = arr[i];
        int j = i - 1;
        
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}
// 优点: 简单，常数因子小，缓存友好
// 缺点: O(n²)，大数据集慢

// 场景2: 中等数据集（50-1000个元素）
// 推荐: 快速排序
void quick_sort(int *arr, int left, int right) {
    if (left < right) {
        int pivot = partition(arr, left, right);
        quick_sort(arr, left, pivot - 1);
        quick_sort(arr, pivot + 1, right);
    }
}
// 优点: 平均O(n log n)，原地排序
// 缺点: 最坏O(n²)，递归深度

// 场景3: 内存极度受限
// 推荐: 堆排序
void heap_sort(int *arr, int size) {
    // 构建最大堆
    for (int i = size / 2 - 1; i >= 0; i--) {
        heapify(arr, size, i);
    }
    
    // 逐个提取元素
    for (int i = size - 1; i > 0; i--) {
        swap(&arr[0], &arr[i]);
        heapify(arr, i, 0);
    }
}
// 优点: O(n log n)，O(1)空间
// 缺点: 不稳定，常数因子大

// 场景4: 整数，范围已知
// 推荐: 计数排序
void counting_sort(uint8_t *arr, int size) {
    int count[256] = {0};
    
    // 计数
    for (int i = 0; i < size; i++) {
        count[arr[i]]++;
    }
    
    // 重建数组
    int index = 0;
    for (int i = 0; i < 256; i++) {
        while (count[i]-- > 0) {
            arr[index++] = i;
        }
    }
}
// 优点: O(n)时间
// 缺点: 需要额外空间，仅适用于整数
```

### 查找算法对比

| 算法 | 时间复杂度 | 空间 | 前提条件 | 适用场景 |
|------|-----------|------|---------|---------|
| 线性查找 | O(n) | O(1) | 无 | 小数据集，无序 |
| 二分查找 | O(log n) | O(1) | 已排序 | 大数据集，静态 |
| 哈希表 | O(1)平均 | O(n) | 无 | 频繁查找 |
| 二叉搜索树 | O(log n)平均 | O(n) | 无 | 动态数据 |

**实际应用示例**:

```c
// 场景1: 配置参数查找（小数据集）
typedef struct {
    const char *name;
    int value;
} Config;

const Config configs[] = {
    {"timeout", 1000},
    {"retry", 3},
    {"buffer_size", 256}
};

int get_config(const char *name) {
    for (int i = 0; i < sizeof(configs)/sizeof(Config); i++) {
        if (strcmp(configs[i].name, name) == 0) {
            return configs[i].value;
        }
    }
    return -1;
}
// 线性查找足够，简单高效

// 场景2: 传感器ID查找（已排序）
const uint16_t sensor_ids[] = {
    0x0001, 0x0005, 0x0012, 0x0023, /* ... 已排序 ... */
};

int find_sensor(uint16_t id) {
    int left = 0, right = SENSOR_COUNT - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (sensor_ids[mid] == id) {
            return mid;
        } else if (sensor_ids[mid] < id) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
// 二分查找，O(log n)

// 场景3: 命令解析（频繁查找）
#define HASH_SIZE 32

typedef struct Command {
    const char *name;
    void (*handler)(void);
    struct Command *next;
} Command;

Command *command_table[HASH_SIZE];

uint32_t hash(const char *str) {
    uint32_t hash = 5381;
    while (*str) {
        hash = ((hash << 5) + hash) + *str++;
    }
    return hash % HASH_SIZE;
}

Command *find_command(const char *name) {
    uint32_t index = hash(name);
    Command *cmd = command_table[index];
    
    while (cmd != NULL) {
        if (strcmp(cmd->name, name) == 0) {
            return cmd;
        }
        cmd = cmd->next;
    }
    return NULL;
}
// 哈希表，O(1)平均
```

### 数据结构选择

**数组 vs 链表**:

```c
// 数组: 连续内存，随机访问O(1)
typedef struct {
    int data[MAX_SIZE];
    int size;
} ArrayList;

// 优点:
// - 随机访问O(1)
// - 缓存友好
// - 内存紧凑
// 缺点:
// - 插入/删除O(n)
// - 固定大小

// 链表: 分散内存，顺序访问O(n)
typedef struct Node {
    int data;
    struct Node *next;
} Node;

// 优点:
// - 插入/删除O(1)
// - 动态大小
// 缺点:
// - 随机访问O(n)
// - 指针开销
// - 缓存不友好

// 选择建议:
// - 频繁随机访问 → 数组
// - 频繁插入删除 → 链表
// - 内存紧张 → 数组（无指针开销）
// - 大小固定 → 数组
```

**栈 vs 队列**:

```c
// 栈: LIFO（后进先出）
typedef struct {
    int data[MAX_SIZE];
    int top;
} Stack;

void push(Stack *s, int value) {
    s->data[++s->top] = value;  // O(1)
}

int pop(Stack *s) {
    return s->data[s->top--];  // O(1)
}

// 应用: 函数调用，表达式求值，回溯

// 队列: FIFO（先进先出）
typedef struct {
    int data[MAX_SIZE];
    int front, rear;
} Queue;

void enqueue(Queue *q, int value) {
    q->data[q->rear] = value;  // O(1)
    q->rear = (q->rear + 1) % MAX_SIZE;
}

int dequeue(Queue *q) {
    int value = q->data[q->front];  // O(1)
    q->front = (q->front + 1) % MAX_SIZE;
    return value;
}

// 应用: 任务调度，缓冲区，BFS
```



## 性能评估方法

### 理论分析

**主定理（Master Theorem）**:

用于分析分治算法的复杂度：
```
T(n) = aT(n/b) + f(n)

其中:
- a: 子问题数量
- n/b: 子问题规模
- f(n): 合并代价

结果:
1. 如果 f(n) = O(n^(log_b(a) - ε)), 则 T(n) = Θ(n^log_b(a))
2. 如果 f(n) = Θ(n^log_b(a)), 则 T(n) = Θ(n^log_b(a) * log n)
3. 如果 f(n) = Ω(n^(log_b(a) + ε)), 则 T(n) = Θ(f(n))
```

**示例应用**:

```c
// 归并排序
void merge_sort(int *arr, int left, int right) {
    if (left < right) {
        int mid = (left + right) / 2;
        merge_sort(arr, left, mid);      // T(n/2)
        merge_sort(arr, mid + 1, right); // T(n/2)
        merge(arr, left, mid, right);    // O(n)
    }
}

// 分析:
// T(n) = 2T(n/2) + O(n)
// a=2, b=2, f(n)=O(n)
// log_b(a) = log_2(2) = 1
// f(n) = Θ(n^1) = Θ(n^log_b(a))
// 因此: T(n) = Θ(n log n)

// 二分查找
int binary_search(int *arr, int left, int right, int target) {
    if (left > right) return -1;
    
    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    
    if (arr[mid] < target) {
        return binary_search(arr, mid + 1, right, target);  // T(n/2)
    } else {
        return binary_search(arr, left, mid - 1, target);   // T(n/2)
    }
}

// 分析:
// T(n) = T(n/2) + O(1)
// a=1, b=2, f(n)=O(1)
// log_b(a) = log_2(1) = 0
// f(n) = Θ(n^0) = Θ(1) = Θ(n^log_b(a))
// 因此: T(n) = Θ(log n)
```

### 实验测量

**基准测试框架**:

```c
#include <time.h>

typedef struct {
    const char *name;
    void (*func)(int*, int);
    uint32_t time_us;
} Benchmark;

void benchmark_sort(Benchmark *bench, int *data, int size) {
    // 复制数据
    int *arr = malloc(size * sizeof(int));
    memcpy(arr, data, size * sizeof(int));
    
    // 测量时间
    uint32_t start = DWT_CYCCNT;
    bench->func(arr, size);
    uint32_t end = DWT_CYCCNT;
    
    bench->time_us = (end - start) / (SystemCoreClock / 1000000);
    
    free(arr);
}

void run_benchmarks(void) {
    Benchmark benchmarks[] = {
        {"Bubble Sort", bubble_sort, 0},
        {"Quick Sort", quick_sort_wrapper, 0},
        {"Heap Sort", heap_sort, 0}
    };
    
    int sizes[] = {10, 100, 1000};
    
    for (int s = 0; s < 3; s++) {
        int size = sizes[s];
        int *data = generate_random_data(size);
        
        printf("\n=== Size: %d ===\n", size);
        
        for (int i = 0; i < 3; i++) {
            benchmark_sort(&benchmarks[i], data, size);
            printf("%-15s: %lu us\n", 
                   benchmarks[i].name, 
                   benchmarks[i].time_us);
        }
        
        free(data);
    }
}
```

**性能曲线绘制**:

```c
void plot_performance_curve(void) {
    int sizes[] = {10, 20, 50, 100, 200, 500, 1000};
    
    printf("\nSize\tBubble\tQuick\tHeap\n");
    printf("----\t------\t-----\t----\n");
    
    for (int i = 0; i < 7; i++) {
        int size = sizes[i];
        int *data = generate_random_data(size);
        
        uint32_t t1 = measure_time(bubble_sort, data, size);
        uint32_t t2 = measure_time(quick_sort, data, size);
        uint32_t t3 = measure_time(heap_sort, data, size);
        
        printf("%d\t%lu\t%lu\t%lu\n", size, t1, t2, t3);
        
        free(data);
    }
}

// 输出示例:
// Size  Bubble  Quick   Heap
// ----  ------  -----   ----
// 10    15      8       12
// 20    45      18      28
// 50    280     52      85
// 100   1100    120     195
// 200   4400    280     450
// 500   27500   800     1300
// 1000  110000  1800    2900
```



## 嵌入式系统中的特殊考虑

### 实时性约束

**硬实时 vs 软实时**:

```c
// 硬实时: 必须在deadline内完成
// 示例: 电机控制，每1ms更新一次
void motor_control_task(void) {
    // 必须在1ms内完成
    // 选择O(1)或O(log n)算法
    // 避免O(n)或更高复杂度
    
    read_sensors();        // O(1)
    calculate_pid();       // O(1)
    update_pwm();          // O(1)
}

// 软实时: 偶尔超时可接受
// 示例: 数据日志，每秒记录一次
void logging_task(void) {
    // 通常在1s内完成即可
    // 可以使用O(n)算法
    
    collect_data();        // O(n)
    compress_data();       // O(n log n)
    write_to_flash();      // O(n)
}
```

**最坏情况分析**:

```c
// 不好: 快速排序（最坏O(n²)）
void process_realtime_data(int *data, int size) {
    quick_sort(data, 0, size - 1);  // 最坏O(n²)！
    // 如果遇到最坏情况，可能超时
}

// 好: 堆排序（保证O(n log n)）
void process_realtime_data_safe(int *data, int size) {
    heap_sort(data, size);  // 保证O(n log n)
    // 可预测的性能
}

// 更好: 如果可能，避免排序
void process_realtime_data_optimal(int *data, int size) {
    // 使用优先队列或其他数据结构
    // 避免完整排序
    int max = find_max(data, size);  // O(n)
    process(max);
}
```

### 缓存效应

**缓存友好的算法**:

```c
// 不好: 列优先访问（缓存未命中多）
void sum_matrix_column_major(int matrix[][N], int rows, int cols) {
    for (int j = 0; j < cols; j++) {
        for (int i = 0; i < rows; i++) {
            sum += matrix[i][j];  // 跳跃访问
        }
    }
}

// 好: 行优先访问（缓存友好）
void sum_matrix_row_major(int matrix[][N], int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            sum += matrix[i][j];  // 连续访问
        }
    }
}

// 性能差异: 在大矩阵上可达2-3倍
```

**数据局部性**:

```c
// 不好: 结构体数组（AoS）
typedef struct {
    float x, y, z;
    float vx, vy, vz;
} Particle;

Particle particles[1000];

void update_positions(void) {
    for (int i = 0; i < 1000; i++) {
        particles[i].x += particles[i].vx;  // 加载整个结构体
        particles[i].y += particles[i].vy;
        particles[i].z += particles[i].vz;
    }
}

// 好: 数组结构体（SoA）
typedef struct {
    float x[1000], y[1000], z[1000];
    float vx[1000], vy[1000], vz[1000];
} ParticleSystem;

ParticleSystem particles;

void update_positions_optimized(void) {
    for (int i = 0; i < 1000; i++) {
        particles.x[i] += particles.vx[i];  // 连续访问
        particles.y[i] += particles.vy[i];
        particles.z[i] += particles.vz[i];
    }
}
```

### 功耗考虑

**算法选择影响功耗**:

```c
// 高功耗: 复杂算法，长时间运行
void high_power_approach(void) {
    // O(n²)算法，运行时间长
    bubble_sort(data, 1000);  // 100ms @ 100MHz
    // CPU持续工作，功耗高
}

// 低功耗: 高效算法，快速完成
void low_power_approach(void) {
    // O(n log n)算法，快速完成
    quick_sort(data, 1000);  // 5ms @ 100MHz
    // 快速完成，进入睡眠，功耗低
}

// 更低功耗: 降频 + 高效算法
void ultra_low_power_approach(void) {
    // 降低时钟频率
    set_clock_frequency(10MHz);  // 降到10MHz
    
    // 使用高效算法
    quick_sort(data, 1000);  // 50ms @ 10MHz
    
    // 虽然时间更长，但功耗更低
    // 10MHz功耗 << 100MHz功耗
    
    // 恢复时钟
    set_clock_frequency(100MHz);
}
```

**动态调整策略**:

```c
void adaptive_algorithm_selection(int *data, int size) {
    if (battery_level > 50) {
        // 电量充足，使用快速算法
        quick_sort(data, size);  // O(n log n)，快
    } else if (battery_level > 20) {
        // 电量中等，平衡模式
        heap_sort(data, size);  // O(n log n)，省电
    } else {
        // 电量低，极度省电
        set_clock_frequency(LOW_FREQ);
        insertion_sort(data, size);  // 简单，低功耗
        set_clock_frequency(NORMAL_FREQ);
    }
}
```



## 实际案例分析

### 案例1: 传感器数据滤波

**需求**: 对传感器数据进行中值滤波

**方案对比**:

```c
// 方案1: 排序法 - O(n log n)
float median_filter_sort(float *window, int size) {
    float *temp = malloc(size * sizeof(float));
    memcpy(temp, window, size * sizeof(float));
    
    quick_sort(temp, size);  // O(n log n)
    
    float median = temp[size / 2];
    free(temp);
    return median;
}
// 时间: O(n log n)
// 空间: O(n)
// 适用: 窗口较大（>20）

// 方案2: 选择法 - O(n)
float median_filter_select(float *window, int size) {
    // 使用快速选择算法
    return quick_select(window, 0, size - 1, size / 2);
}
// 时间: O(n)平均
// 空间: O(1)
// 适用: 窗口中等（10-50）

// 方案3: 插入排序 - O(n²)
float median_filter_insertion(float *window, int size) {
    // 对于小窗口，插入排序很快
    insertion_sort(window, size);
    return window[size / 2];
}
// 时间: O(n²)
// 空间: O(1)
// 适用: 小窗口（<10）

// 实际选择:
float median_filter_adaptive(float *window, int size) {
    if (size <= 5) {
        return median_filter_insertion(window, size);
    } else if (size <= 20) {
        return median_filter_select(window, size);
    } else {
        return median_filter_sort(window, size);
    }
}
```

### 案例2: 事件队列管理

**需求**: 管理定时器事件，按时间排序

**方案对比**:

```c
// 方案1: 数组 + 线性查找
typedef struct {
    Event events[MAX_EVENTS];
    int count;
} EventQueue_Array;

void insert_event_array(EventQueue_Array *q, Event e) {
    // 线性查找插入位置
    int i;
    for (i = q->count - 1; i >= 0 && q->events[i].time > e.time; i--) {
        q->events[i + 1] = q->events[i];
    }
    q->events[i + 1] = e;
    q->count++;
}
// 插入: O(n)
// 获取最早: O(1)
// 空间: O(n)

// 方案2: 链表
typedef struct EventNode {
    Event event;
    struct EventNode *next;
} EventNode;

void insert_event_list(EventNode **head, Event e) {
    EventNode *node = malloc(sizeof(EventNode));
    node->event = e;
    
    // 查找插入位置
    EventNode **p = head;
    while (*p && (*p)->event.time < e.time) {
        p = &(*p)->next;
    }
    node->next = *p;
    *p = node;
}
// 插入: O(n)
// 获取最早: O(1)
// 空间: O(n) + 指针开销

// 方案3: 最小堆
typedef struct {
    Event heap[MAX_EVENTS];
    int size;
} EventQueue_Heap;

void insert_event_heap(EventQueue_Heap *q, Event e) {
    q->heap[q->size] = e;
    heap_bubble_up(q->heap, q->size);
    q->size++;
}

Event get_earliest_event(EventQueue_Heap *q) {
    Event e = q->heap[0];
    q->heap[0] = q->heap[--q->size];
    heap_bubble_down(q->heap, 0, q->size);
    return e;
}
// 插入: O(log n)
// 获取最早: O(log n)
// 空间: O(n)

// 嵌入式选择: 最小堆
// - 插入和删除都是O(log n)
// - 无动态分配
// - 空间紧凑
```

### 案例3: 数据压缩

**需求**: 压缩传感器数据以节省存储

**方案对比**:

```c
// 方案1: 游程编码（RLE）- O(n)
int rle_compress(uint8_t *input, int size, uint8_t *output) {
    int out_idx = 0;
    int i = 0;
    
    while (i < size) {
        uint8_t value = input[i];
        int count = 1;
        
        while (i + count < size && input[i + count] == value && count < 255) {
            count++;
        }
        
        output[out_idx++] = value;
        output[out_idx++] = count;
        i += count;
    }
    
    return out_idx;
}
// 时间: O(n)
// 压缩比: 适合重复数据
// 适用: 传感器数据变化慢

// 方案2: 差分编码 - O(n)
int delta_compress(int16_t *input, int size, int8_t *output) {
    output[0] = input[0] & 0xFF;
    output[1] = (input[0] >> 8) & 0xFF;
    
    int out_idx = 2;
    for (int i = 1; i < size; i++) {
        int16_t delta = input[i] - input[i-1];
        
        if (delta >= -127 && delta <= 127) {
            output[out_idx++] = (int8_t)delta;
        } else {
            output[out_idx++] = 0x80;  // 转义标记
            output[out_idx++] = delta & 0xFF;
            output[out_idx++] = (delta >> 8) & 0xFF;
        }
    }
    
    return out_idx;
}
// 时间: O(n)
// 压缩比: 适合缓慢变化的数据
// 适用: 温度、压力等传感器

// 方案3: 霍夫曼编码 - O(n log n)
// 构建霍夫曼树: O(n log n)
// 编码: O(n)
// 压缩比: 最优
// 适用: 数据分布不均匀

// 嵌入式选择: 差分编码
// - 简单快速
// - 压缩比好
// - 无需额外内存
// - 适合实时处理
```



## 优化技巧

### 技巧1: 提前终止

```c
// 不好: 总是完整遍历
bool contains_duplicate(int *arr, int size) {
    for (int i = 0; i < size; i++) {
        for (int j = i + 1; j < size; j++) {
            if (arr[i] == arr[j]) {
                // 找到重复，但继续循环
            }
        }
    }
}

// 好: 找到后立即返回
bool contains_duplicate_optimized(int *arr, int size) {
    for (int i = 0; i < size; i++) {
        for (int j = i + 1; j < size; j++) {
            if (arr[i] == arr[j]) {
                return true;  // 立即返回
            }
        }
    }
    return false;
}
```

### 技巧2: 缓存结果

```c
// 不好: 重复计算
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);  // 大量重复计算
}

// 好: 缓存结果
int fib_cache[100] = {0};

int fibonacci_cached(int n) {
    if (n <= 1) return n;
    
    if (fib_cache[n] != 0) {
        return fib_cache[n];  // 使用缓存
    }
    
    fib_cache[n] = fibonacci_cached(n-1) + fibonacci_cached(n-2);
    return fib_cache[n];
}
```

### 技巧3: 预处理

```c
// 不好: 每次都计算
bool is_prime(int n) {
    if (n < 2) return false;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return false;
    }
    return true;
}

// 好: 预计算素数表
const bool prime_table[1000] = {
    false, false, true, true, false, true, /* ... */
};

bool is_prime_fast(int n) {
    if (n < 1000) {
        return prime_table[n];  // O(1)
    }
    return is_prime(n);  // 大数才计算
}
```

### 技巧4: 分而治之

```c
// 不好: 暴力搜索最大子数组和
int max_subarray_brute(int *arr, int size) {
    int max_sum = INT_MIN;
    
    for (int i = 0; i < size; i++) {
        for (int j = i; j < size; j++) {
            int sum = 0;
            for (int k = i; k <= j; k++) {
                sum += arr[k];
            }
            if (sum > max_sum) {
                max_sum = sum;
            }
        }
    }
    
    return max_sum;
}
// O(n³)

// 好: Kadane算法
int max_subarray_kadane(int *arr, int size) {
    int max_sum = arr[0];
    int current_sum = arr[0];
    
    for (int i = 1; i < size; i++) {
        current_sum = (arr[i] > current_sum + arr[i]) ? 
                      arr[i] : current_sum + arr[i];
        if (current_sum > max_sum) {
            max_sum = current_sum;
        }
    }
    
    return max_sum;
}
// O(n)
```



## 总结

通过本文，你已经学习了:

- ✅ 时间复杂度和空间复杂度的概念
- ✅ 常见算法的复杂度分析方法
- ✅ 如何选择合适的算法和数据结构
- ✅ 嵌入式系统中的特殊考虑
- ✅ 实际案例和优化技巧

**关键要点**:

1. **算法优于代码**: 选择正确的算法比优化代码更重要
2. **理解权衡**: 时间、空间、功耗之间需要平衡
3. **考虑实际**: 理论复杂度 ≠ 实际性能
4. **测量验证**: 始终测量实际性能
5. **适应场景**: 根据具体需求选择算法

**决策流程**:

```
1. 明确需求
   ├─ 数据规模？
   ├─ 实时性要求？
   ├─ 内存限制？
   └─ 功耗要求？

2. 分析复杂度
   ├─ 时间复杂度
   ├─ 空间复杂度
   └─ 最坏情况

3. 选择算法
   ├─ 理论分析
   ├─ 实验测试
   └─ 权衡决策

4. 优化实现
   ├─ 提前终止
   ├─ 缓存结果
   └─ 预处理数据

5. 验证性能
   ├─ 基准测试
   ├─ 压力测试
   └─ 长期监控
```

**持续提升**:
- 学习经典算法和数据结构
- 分析开源项目中的算法选择
- 积累不同场景的经验
- 关注新的算法研究
- 建立算法工具库

记住，在嵌入式系统中，没有"最好"的算法，只有"最合适"的算法。根据具体场景做出明智的选择，才是优秀工程师的标志。

## 延伸阅读

### 相关文章

- [代码优化基础原则](../beginner/01-code-optimization-basics.html) - 优化基础
- [编译器优化选项使用](../beginner/02-compiler-optimization.html) - 编译器优化
- [内存使用优化技术](./01-memory-optimization.html) - 内存优化
- [功耗优化实战](./02-power-optimization.html) - 功耗优化

### 进阶主题

- [实时性能优化技术](../advanced/01-real-time-optimization.html) - 实时系统
- [性能分析工具开发](../advanced/02-performance-analysis-tool.html) - 分析工具

### 参考资料

**书籍推荐**:
1. 《算法导论》- Thomas H. Cormen
2. 《算法设计手册》- Steven S. Skiena
3. 《编程珠玑》- Jon Bentley

**在线资源**:
1. [Big-O Cheat Sheet](https://www.bigocheatsheet.com/) - 复杂度速查
2. [VisuAlgo](https://visualgo.net/) - 算法可视化
3. [Algorithm Visualizer](https://algorithm-visualizer.org/) - 算法动画

**算法库**:
1. [C Algorithms](https://github.com/fragglet/c-algorithms) - C语言算法库
2. [Embedded Artistry](https://embeddedartistry.com/) - 嵌入式算法

---

**练习建议**:
1. 分析你项目中的关键算法复杂度
2. 对比不同算法在实际硬件上的性能
3. 实现并测试本文中的算法示例
4. 建立自己的算法性能数据库
5. 参与算法竞赛，提升分析能力
