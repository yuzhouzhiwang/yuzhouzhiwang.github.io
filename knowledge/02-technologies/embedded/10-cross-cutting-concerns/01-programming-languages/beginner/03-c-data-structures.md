---
title: "C语言数据结构实现"
description: "深入讲解如何使用C语言实现常用数据结构，包括链表、队列、栈、树和哈希表，掌握嵌入式系统中高效的数据组织与管理方法"
slug: "c-data-structures"

# 分类信息
domain: "横切关注点"
module: "编程语言"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - C语言
  - 数据结构
  - 算法
  - 链表
  - 队列
  - 栈
prerequisites:
  - "c-advanced-features"
  - "c-memory-management"
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
  - C语言数据结构
  - 链表实现
  - 队列实现
  - 栈实现
  - 树结构
  - 哈希表
cover_image: ""
---

# C语言数据结构实现


## 概述

数据结构是程序设计的基础，在嵌入式系统中合理选择和实现数据结构对系统性能至关重要。完成本教程学习后，你将能够：

- 使用C语言实现常用的线性数据结构（链表、栈、队列）
- 掌握树形结构的实现和应用
- 理解哈希表的原理并实现简单的哈希表
- 根据实际需求选择合适的数据结构
- 分析数据结构的时间和空间复杂度

## 背景知识

### 为什么数据结构重要？

在嵌入式系统开发中，数据结构的选择直接影响：

- **性能**：不同数据结构的操作效率差异巨大
- **内存占用**：嵌入式系统资源有限，需要精打细算
- **代码可维护性**：良好的数据结构使代码更清晰
- **实时性**：某些操作的时间复杂度影响系统响应

### 前置知识要求

本教程假设你已经掌握：
- C语言基础语法
- 指针和动态内存分配
- 结构体的使用
- 基本的算法概念

## 核心内容

### 1. 链表（Linked List）

链表是最基础的动态数据结构，在嵌入式系统中应用广泛。

#### 1.1 单向链表

单向链表每个节点包含数据和指向下一个节点的指针。

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// 链表节点定义
typedef struct node {
    int data;
    struct node *next;
} node_t;

// 链表结构
typedef struct {
    node_t *head;
    uint32_t size;
} list_t;

// 初始化链表
void list_init(list_t *list) {
    list->head = NULL;
    list->size = 0;
}

// 在头部插入节点
int list_insert_head(list_t *list, int data) {
    node_t *new_node = (node_t *)malloc(sizeof(node_t));
    if (new_node == NULL) {
        return -1;  // 内存分配失败
    }
    
    new_node->data = data;
    new_node->next = list->head;
    list->head = new_node;
    list->size++;
    
    return 0;
}

// 在尾部插入节点
int list_insert_tail(list_t *list, int data) {
    node_t *new_node = (node_t *)malloc(sizeof(node_t));
    if (new_node == NULL) {
        return -1;
    }
    
    new_node->data = data;
    new_node->next = NULL;
    
    if (list->head == NULL) {
        list->head = new_node;
    } else {
        node_t *current = list->head;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = new_node;
    }
    
    list->size++;
    return 0;
}

// 删除指定值的节点
int list_delete(list_t *list, int data) {
    if (list->head == NULL) {
        return -1;  // 链表为空
    }
    
    node_t *current = list->head;
    node_t *prev = NULL;
    
    // 查找要删除的节点
    while (current != NULL && current->data != data) {
        prev = current;
        current = current->next;
    }
    
    if (current == NULL) {
        return -1;  // 未找到
    }
    
    // 删除节点
    if (prev == NULL) {
        list->head = current->next;  // 删除头节点
    } else {
        prev->next = current->next;
    }
    
    free(current);
    list->size--;
    return 0;
}

// 查找节点
node_t *list_find(list_t *list, int data) {
    node_t *current = list->head;
    
    while (current != NULL) {
        if (current->data == data) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

// 打印链表
void list_print(list_t *list) {
    node_t *current = list->head;
    
    printf("List (%u elements): ", list->size);
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

// 销毁链表
void list_destroy(list_t *list) {
    node_t *current = list->head;
    node_t *next;
    
    while (current != NULL) {
        next = current->next;
        free(current);
        current = next;
    }
    
    list->head = NULL;
    list->size = 0;
}

// 使用示例
int main(void) {
    list_t my_list;
    list_init(&my_list);
    
    // 插入数据
    list_insert_head(&my_list, 10);
    list_insert_head(&my_list, 20);
    list_insert_tail(&my_list, 5);
    list_insert_tail(&my_list, 15);
    
    list_print(&my_list);  // 输出: 20 -> 10 -> 5 -> 15 -> NULL
    
    // 查找节点
    node_t *found = list_find(&my_list, 10);
    if (found != NULL) {
        printf("Found: %d\n", found->data);
    }
    
    // 删除节点
    list_delete(&my_list, 10);
    list_print(&my_list);  // 输出: 20 -> 5 -> 15 -> NULL
    
    // 清理
    list_destroy(&my_list);
    
    return 0;
}
```

**代码说明**：
- `list_init()`：初始化链表，设置头指针为NULL
- `list_insert_head()`：在头部插入，时间复杂度O(1)
- `list_insert_tail()`：在尾部插入，时间复杂度O(n)
- `list_delete()`：删除指定值的节点，时间复杂度O(n)
- `list_find()`：查找节点，时间复杂度O(n)
- `list_destroy()`：释放所有节点内存

**应用场景**：
- 任务队列管理
- 事件链表
- 动态缓冲区管理
- 设备驱动链表

#### 1.2 双向链表

双向链表每个节点包含指向前后节点的指针，支持双向遍历。

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// 双向链表节点
typedef struct dnode {
    int data;
    struct dnode *prev;
    struct dnode *next;
} dnode_t;

// 双向链表结构
typedef struct {
    dnode_t *head;
    dnode_t *tail;
    uint32_t size;
} dlist_t;

// 初始化双向链表
void dlist_init(dlist_t *list) {
    list->head = NULL;
    list->tail = NULL;
    list->size = 0;
}

// 在头部插入
int dlist_insert_head(dlist_t *list, int data) {
    dnode_t *new_node = (dnode_t *)malloc(sizeof(dnode_t));
    if (new_node == NULL) {
        return -1;
    }
    
    new_node->data = data;
    new_node->prev = NULL;
    new_node->next = list->head;
    
    if (list->head != NULL) {
        list->head->prev = new_node;
    } else {
        list->tail = new_node;  // 第一个节点
    }
    
    list->head = new_node;
    list->size++;
    return 0;
}

// 在尾部插入
int dlist_insert_tail(dlist_t *list, int data) {
    dnode_t *new_node = (dnode_t *)malloc(sizeof(dnode_t));
    if (new_node == NULL) {
        return -1;
    }
    
    new_node->data = data;
    new_node->next = NULL;
    new_node->prev = list->tail;
    
    if (list->tail != NULL) {
        list->tail->next = new_node;
    } else {
        list->head = new_node;  // 第一个节点
    }
    
    list->tail = new_node;
    list->size++;
    return 0;
}

// 删除节点
int dlist_delete(dlist_t *list, dnode_t *node) {
    if (node == NULL) {
        return -1;
    }
    
    if (node->prev != NULL) {
        node->prev->next = node->next;
    } else {
        list->head = node->next;  // 删除头节点
    }
    
    if (node->next != NULL) {
        node->next->prev = node->prev;
    } else {
        list->tail = node->prev;  // 删除尾节点
    }
    
    free(node);
    list->size--;
    return 0;
}

// 正向打印
void dlist_print_forward(dlist_t *list) {
    dnode_t *current = list->head;
    
    printf("Forward: ");
    while (current != NULL) {
        printf("%d <-> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

// 反向打印
void dlist_print_backward(dlist_t *list) {
    dnode_t *current = list->tail;
    
    printf("Backward: ");
    while (current != NULL) {
        printf("%d <-> ", current->data);
        current = current->prev;
    }
    printf("NULL\n");
}
```

**双向链表优势**：
- 可以双向遍历
- 删除节点更高效（已知节点指针时为O(1)）
- 适合需要频繁插入删除的场景

**缺点**：
- 每个节点多占用一个指针的内存
- 维护prev指针增加复杂度


### 2. 栈（Stack）

栈是后进先出（LIFO）的数据结构，在嵌入式系统中用于函数调用、表达式求值等。

#### 2.1 数组实现的栈

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define STACK_MAX_SIZE 100

// 栈结构
typedef struct {
    int data[STACK_MAX_SIZE];
    int top;
} stack_t;

// 初始化栈
void stack_init(stack_t *stack) {
    stack->top = -1;
}

// 判断栈是否为空
bool stack_is_empty(stack_t *stack) {
    return stack->top == -1;
}

// 判断栈是否已满
bool stack_is_full(stack_t *stack) {
    return stack->top == STACK_MAX_SIZE - 1;
}

// 入栈
int stack_push(stack_t *stack, int data) {
    if (stack_is_full(stack)) {
        return -1;  // 栈满
    }
    
    stack->data[++stack->top] = data;
    return 0;
}

// 出栈
int stack_pop(stack_t *stack, int *data) {
    if (stack_is_empty(stack)) {
        return -1;  // 栈空
    }
    
    *data = stack->data[stack->top--];
    return 0;
}

// 查看栈顶元素
int stack_peek(stack_t *stack, int *data) {
    if (stack_is_empty(stack)) {
        return -1;
    }
    
    *data = stack->data[stack->top];
    return 0;
}

// 获取栈大小
uint32_t stack_size(stack_t *stack) {
    return stack->top + 1;
}

// 使用示例
int main(void) {
    stack_t stack;
    stack_init(&stack);
    
    // 入栈
    stack_push(&stack, 10);
    stack_push(&stack, 20);
    stack_push(&stack, 30);
    
    printf("Stack size: %u\n", stack_size(&stack));
    
    // 查看栈顶
    int top_value;
    if (stack_peek(&stack, &top_value) == 0) {
        printf("Top: %d\n", top_value);
    }
    
    // 出栈
    int value;
    while (stack_pop(&stack, &value) == 0) {
        printf("Popped: %d\n", value);
    }
    
    return 0;
}
```

**代码说明**：
- 使用数组实现，固定大小
- `top`指向栈顶元素的索引
- 所有操作时间复杂度为O(1)
- 空间复杂度为O(n)

**应用场景**：
- 函数调用栈
- 表达式求值
- 括号匹配检查
- 深度优先搜索


### 3. 队列（Queue）

队列是先进先出（FIFO）的数据结构，在嵌入式系统中广泛用于任务调度、消息传递等。

#### 3.1 循环队列

循环队列使用数组实现，通过循环利用空间避免假溢出。

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define QUEUE_MAX_SIZE 10

// 循环队列结构
typedef struct {
    int data[QUEUE_MAX_SIZE];
    int front;
    int rear;
    uint32_t size;
} queue_t;

// 初始化队列
void queue_init(queue_t *queue) {
    queue->front = 0;
    queue->rear = 0;
    queue->size = 0;
}

// 判断队列是否为空
bool queue_is_empty(queue_t *queue) {
    return queue->size == 0;
}

// 判断队列是否已满
bool queue_is_full(queue_t *queue) {
    return queue->size == QUEUE_MAX_SIZE;
}

// 入队
int queue_enqueue(queue_t *queue, int data) {
    if (queue_is_full(queue)) {
        return -1;  // 队列满
    }
    
    queue->data[queue->rear] = data;
    queue->rear = (queue->rear + 1) % QUEUE_MAX_SIZE;
    queue->size++;
    
    return 0;
}

// 出队
int queue_dequeue(queue_t *queue, int *data) {
    if (queue_is_empty(queue)) {
        return -1;  // 队列空
    }
    
    *data = queue->data[queue->front];
    queue->front = (queue->front + 1) % QUEUE_MAX_SIZE;
    queue->size--;
    
    return 0;
}

// 查看队首元素
int queue_peek(queue_t *queue, int *data) {
    if (queue_is_empty(queue)) {
        return -1;
    }
    
    *data = queue->data[queue->front];
    return 0;
}

// 获取队列大小
uint32_t queue_size(queue_t *queue) {
    return queue->size;
}

// 使用示例
int main(void) {
    queue_t queue;
    queue_init(&queue);
    
    // 入队
    for (int i = 1; i <= 5; i++) {
        queue_enqueue(&queue, i * 10);
    }
    
    printf("Queue size: %u\n", queue_size(&queue));
    
    // 出队
    int value;
    while (queue_dequeue(&queue, &value) == 0) {
        printf("Dequeued: %d\n", value);
    }
    
    return 0;
}
```

**循环队列优势**：
- 充分利用数组空间
- 所有操作时间复杂度为O(1)
- 适合固定大小的缓冲区

**应用场景**：
- UART接收缓冲区
- 任务消息队列
- 数据采集缓冲
- 事件队列


### 4. 二叉树（Binary Tree）

二叉树是每个节点最多有两个子节点的树形结构。

#### 4.1 二叉搜索树

二叉搜索树（BST）满足：左子树所有节点值小于根节点，右子树所有节点值大于根节点。

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// 树节点定义
typedef struct tree_node {
    int data;
    struct tree_node *left;
    struct tree_node *right;
} tree_node_t;

// 二叉搜索树结构
typedef struct {
    tree_node_t *root;
    uint32_t size;
} bst_t;

// 初始化BST
void bst_init(bst_t *tree) {
    tree->root = NULL;
    tree->size = 0;
}

// 创建新节点
tree_node_t *create_node(int data) {
    tree_node_t *node = (tree_node_t *)malloc(sizeof(tree_node_t));
    if (node != NULL) {
        node->data = data;
        node->left = NULL;
        node->right = NULL;
    }
    return node;
}

// 插入节点（递归实现）
tree_node_t *bst_insert_recursive(tree_node_t *root, int data) {
    if (root == NULL) {
        return create_node(data);
    }
    
    if (data < root->data) {
        root->left = bst_insert_recursive(root->left, data);
    } else if (data > root->data) {
        root->right = bst_insert_recursive(root->right, data);
    }
    // 如果data == root->data，不插入重复值
    
    return root;
}

// 插入节点（对外接口）
int bst_insert(bst_t *tree, int data) {
    tree->root = bst_insert_recursive(tree->root, data);
    tree->size++;
    return 0;
}

// 查找节点
tree_node_t *bst_search(tree_node_t *root, int data) {
    if (root == NULL || root->data == data) {
        return root;
    }
    
    if (data < root->data) {
        return bst_search(root->left, data);
    } else {
        return bst_search(root->right, data);
    }
}

// 查找最小值节点
tree_node_t *find_min(tree_node_t *root) {
    while (root != NULL && root->left != NULL) {
        root = root->left;
    }
    return root;
}

// 删除节点
tree_node_t *bst_delete_recursive(tree_node_t *root, int data) {
    if (root == NULL) {
        return NULL;
    }
    
    if (data < root->data) {
        root->left = bst_delete_recursive(root->left, data);
    } else if (data > root->data) {
        root->right = bst_delete_recursive(root->right, data);
    } else {
        // 找到要删除的节点
        if (root->left == NULL) {
            tree_node_t *temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            tree_node_t *temp = root->left;
            free(root);
            return temp;
        }
        
        // 节点有两个子节点：找右子树的最小值替换
        tree_node_t *temp = find_min(root->right);
        root->data = temp->data;
        root->right = bst_delete_recursive(root->right, temp->data);
    }
    
    return root;
}

// 中序遍历（左-根-右）
void bst_inorder(tree_node_t *root) {
    if (root != NULL) {
        bst_inorder(root->left);
        printf("%d ", root->data);
        bst_inorder(root->right);
    }
}

// 前序遍历（根-左-右）
void bst_preorder(tree_node_t *root) {
    if (root != NULL) {
        printf("%d ", root->data);
        bst_preorder(root->left);
        bst_preorder(root->right);
    }
}

// 后序遍历（左-右-根）
void bst_postorder(tree_node_t *root) {
    if (root != NULL) {
        bst_postorder(root->left);
        bst_postorder(root->right);
        printf("%d ", root->data);
    }
}

// 使用示例
int main(void) {
    bst_t tree;
    bst_init(&tree);
    
    // 插入节点
    int values[] = {50, 30, 70, 20, 40, 60, 80};
    for (int i = 0; i < 7; i++) {
        bst_insert(&tree, values[i]);
    }
    
    // 遍历
    printf("Inorder: ");
    bst_inorder(tree.root);
    printf("\n");
    
    printf("Preorder: ");
    bst_preorder(tree.root);
    printf("\n");
    
    printf("Postorder: ");
    bst_postorder(tree.root);
    printf("\n");
    
    // 查找
    tree_node_t *found = bst_search(tree.root, 40);
    if (found != NULL) {
        printf("Found: %d\n", found->data);
    }
    
    // 删除
    tree.root = bst_delete_recursive(tree.root, 30);
    printf("After delete 30, Inorder: ");
    bst_inorder(tree.root);
    printf("\n");
    
    return 0;
}
```

**BST特点**：
- 查找、插入、删除平均时间复杂度O(log n)
- 最坏情况（退化成链表）O(n)
- 中序遍历得到有序序列

**应用场景**：
- 有序数据存储
- 优先级队列
- 符号表实现
- 文件系统目录结构


### 5. 哈希表（Hash Table）

哈希表通过哈希函数将键映射到数组索引，实现快速查找。

#### 5.1 链地址法哈希表

使用链表解决哈希冲突。

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define HASH_TABLE_SIZE 10

// 哈希表节点
typedef struct hash_node {
    char *key;
    int value;
    struct hash_node *next;
} hash_node_t;

// 哈希表结构
typedef struct {
    hash_node_t *buckets[HASH_TABLE_SIZE];
    uint32_t size;
} hash_table_t;

// 简单哈希函数
uint32_t hash_function(const char *key) {
    uint32_t hash = 0;
    while (*key) {
        hash = (hash * 31 + *key) % HASH_TABLE_SIZE;
        key++;
    }
    return hash;
}

// 初始化哈希表
void hash_table_init(hash_table_t *table) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        table->buckets[i] = NULL;
    }
    table->size = 0;
}

// 插入键值对
int hash_table_insert(hash_table_t *table, const char *key, int value) {
    uint32_t index = hash_function(key);
    
    // 检查键是否已存在
    hash_node_t *current = table->buckets[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            current->value = value;  // 更新值
            return 0;
        }
        current = current->next;
    }
    
    // 创建新节点
    hash_node_t *new_node = (hash_node_t *)malloc(sizeof(hash_node_t));
    if (new_node == NULL) {
        return -1;
    }
    
    new_node->key = strdup(key);
    new_node->value = value;
    new_node->next = table->buckets[index];
    table->buckets[index] = new_node;
    table->size++;
    
    return 0;
}

// 查找键值
int hash_table_get(hash_table_t *table, const char *key, int *value) {
    uint32_t index = hash_function(key);
    hash_node_t *current = table->buckets[index];
    
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            *value = current->value;
            return 0;  // 找到
        }
        current = current->next;
    }
    
    return -1;  // 未找到
}

// 删除键值对
int hash_table_delete(hash_table_t *table, const char *key) {
    uint32_t index = hash_function(key);
    hash_node_t *current = table->buckets[index];
    hash_node_t *prev = NULL;
    
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (prev == NULL) {
                table->buckets[index] = current->next;
            } else {
                prev->next = current->next;
            }
            
            free(current->key);
            free(current);
            table->size--;
            return 0;
        }
        prev = current;
        current = current->next;
    }
    
    return -1;  // 未找到
}

// 打印哈希表
void hash_table_print(hash_table_t *table) {
    printf("Hash Table (size: %u):\n", table->size);
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        printf("Bucket %d: ", i);
        hash_node_t *current = table->buckets[i];
        while (current != NULL) {
            printf("(%s: %d) -> ", current->key, current->value);
            current = current->next;
        }
        printf("NULL\n");
    }
}

// 使用示例
int main(void) {
    hash_table_t table;
    hash_table_init(&table);
    
    // 插入数据
    hash_table_insert(&table, "apple", 100);
    hash_table_insert(&table, "banana", 200);
    hash_table_insert(&table, "orange", 300);
    hash_table_insert(&table, "grape", 400);
    
    hash_table_print(&table);
    
    // 查找
    int value;
    if (hash_table_get(&table, "banana", &value) == 0) {
        printf("Found banana: %d\n", value);
    }
    
    // 删除
    hash_table_delete(&table, "orange");
    hash_table_print(&table);
    
    return 0;
}
```

**哈希表特点**：
- 平均查找、插入、删除时间复杂度O(1)
- 最坏情况（所有键冲突）O(n)
- 空间换时间的典型应用

**应用场景**：
- 配置参数存储
- 设备ID映射
- 缓存实现
- 符号表


## 实践示例

### 综合示例：任务管理系统

下面是一个综合运用多种数据结构的任务管理系统：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

// 任务优先级
typedef enum {
    PRIORITY_LOW = 0,
    PRIORITY_NORMAL,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL
} priority_t;

// 任务状态
typedef enum {
    TASK_READY = 0,
    TASK_RUNNING,
    TASK_BLOCKED,
    TASK_COMPLETED
} task_state_t;

// 任务结构
typedef struct task {
    uint32_t id;
    char name[32];
    priority_t priority;
    task_state_t state;
    void (*handler)(void);
    struct task *next;
} task_t;

// 任务队列（按优先级）
typedef struct {
    task_t *head;
    uint32_t count;
} task_queue_t;

// 初始化任务队列
void task_queue_init(task_queue_t *queue) {
    queue->head = NULL;
    queue->count = 0;
}

// 创建任务
task_t *task_create(uint32_t id, const char *name, priority_t priority, 
                    void (*handler)(void)) {
    task_t *task = (task_t *)malloc(sizeof(task_t));
    if (task == NULL) {
        return NULL;
    }
    
    task->id = id;
    strncpy(task->name, name, sizeof(task->name) - 1);
    task->name[sizeof(task->name) - 1] = '\0';
    task->priority = priority;
    task->state = TASK_READY;
    task->handler = handler;
    task->next = NULL;
    
    return task;
}

// 按优先级插入任务
int task_queue_insert(task_queue_t *queue, task_t *task) {
    if (task == NULL) {
        return -1;
    }
    
    // 空队列或优先级最高
    if (queue->head == NULL || task->priority > queue->head->priority) {
        task->next = queue->head;
        queue->head = task;
    } else {
        // 找到插入位置
        task_t *current = queue->head;
        while (current->next != NULL && 
               current->next->priority >= task->priority) {
            current = current->next;
        }
        task->next = current->next;
        current->next = task;
    }
    
    queue->count++;
    return 0;
}

// 获取最高优先级任务
task_t *task_queue_get_highest(task_queue_t *queue) {
    if (queue->head == NULL) {
        return NULL;
    }
    
    task_t *task = queue->head;
    queue->head = task->next;
    queue->count--;
    
    return task;
}

// 打印任务队列
void task_queue_print(task_queue_t *queue) {
    printf("Task Queue (%u tasks):\n", queue->count);
    task_t *current = queue->head;
    
    while (current != NULL) {
        printf("  [%u] %s (Priority: %d, State: %d)\n",
               current->id, current->name, current->priority, current->state);
        current = current->next;
    }
}

// 示例任务处理函数
void task_handler_1(void) {
    printf("Executing Task 1\n");
}

void task_handler_2(void) {
    printf("Executing Task 2\n");
}

void task_handler_3(void) {
    printf("Executing Task 3\n");
}

// 使用示例
int main(void) {
    task_queue_t queue;
    task_queue_init(&queue);
    
    // 创建任务
    task_t *task1 = task_create(1, "Low Priority Task", 
                                PRIORITY_LOW, task_handler_1);
    task_t *task2 = task_create(2, "High Priority Task", 
                                PRIORITY_HIGH, task_handler_2);
    task_t *task3 = task_create(3, "Normal Priority Task", 
                                PRIORITY_NORMAL, task_handler_3);
    task_t *task4 = task_create(4, "Critical Task", 
                                PRIORITY_CRITICAL, task_handler_1);
    
    // 插入任务
    task_queue_insert(&queue, task1);
    task_queue_insert(&queue, task2);
    task_queue_insert(&queue, task3);
    task_queue_insert(&queue, task4);
    
    // 打印队列
    task_queue_print(&queue);
    
    // 执行任务
    printf("\nExecuting tasks:\n");
    task_t *task;
    while ((task = task_queue_get_highest(&queue)) != NULL) {
        task->state = TASK_RUNNING;
        if (task->handler != NULL) {
            task->handler();
        }
        task->state = TASK_COMPLETED;
        free(task);
    }
    
    return 0;
}
```

**代码说明**：
- 使用链表实现优先级队列
- 任务按优先级排序
- 支持动态添加和执行任务
- 综合运用了结构体、枚举、函数指针


## 深入理解

### 数据结构选择指南

| 操作需求 | 推荐数据结构 | 时间复杂度 |
|---------|------------|-----------|
| 快速随机访问 | 数组 | O(1) |
| 频繁插入删除 | 链表 | O(1) |
| LIFO操作 | 栈 | O(1) |
| FIFO操作 | 队列 | O(1) |
| 有序数据 | 二叉搜索树 | O(log n) |
| 快速查找 | 哈希表 | O(1) |
| 优先级处理 | 优先队列/堆 | O(log n) |

### 内存管理考虑

#### 静态 vs 动态分配

```c
// 静态分配：编译时确定大小
#define MAX_TASKS 10
task_t static_tasks[MAX_TASKS];

// 动态分配：运行时分配
task_t *dynamic_task = (task_t *)malloc(sizeof(task_t));
```

**选择建议**：
- **静态分配**：
  - 优点：无内存碎片，速度快，可预测
  - 缺点：浪费内存，不灵活
  - 适用：资源受限的嵌入式系统

- **动态分配**：
  - 优点：灵活，按需分配
  - 缺点：可能内存碎片，分配失败风险
  - 适用：内存充足的系统

#### 内存池技术

对于频繁分配释放的场景，使用内存池可以提高效率：

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define POOL_SIZE 10

typedef struct {
    uint8_t data[64];  // 固定大小的块
    bool used;
} memory_block_t;

typedef struct {
    memory_block_t blocks[POOL_SIZE];
} memory_pool_t;

// 初始化内存池
void pool_init(memory_pool_t *pool) {
    for (int i = 0; i < POOL_SIZE; i++) {
        pool->blocks[i].used = false;
    }
}

// 从内存池分配
void *pool_alloc(memory_pool_t *pool) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (!pool->blocks[i].used) {
            pool->blocks[i].used = true;
            return pool->blocks[i].data;
        }
    }
    return NULL;  // 池已满
}

// 释放到内存池
void pool_free(memory_pool_t *pool, void *ptr) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (pool->blocks[i].data == ptr) {
            pool->blocks[i].used = false;
            return;
        }
    }
}
```

**内存池优势**：
- 避免内存碎片
- 分配释放速度快
- 可预测的内存使用
- 适合固定大小的对象

### 性能优化技巧

#### 1. 缓存友好的数据结构

```c
// 不友好：链表节点分散
typedef struct node {
    int data;
    struct node *next;
} node_t;

// 友好：数组连续存储
typedef struct {
    int data[1000];
    int size;
} array_t;
```

#### 2. 减少内存分配次数

```c
// 不好：多次分配
for (int i = 0; i < 100; i++) {
    node_t *node = malloc(sizeof(node_t));
    // 使用node
}

// 好：批量分配
node_t *nodes = malloc(100 * sizeof(node_t));
for (int i = 0; i < 100; i++) {
    // 使用nodes[i]
}
```

#### 3. 选择合适的数据结构

```c
// 场景：需要频繁查找
// 不好：使用链表 O(n)
list_find(list, key);

// 好：使用哈希表 O(1)
hash_table_get(table, key, &value);
```


## 常见问题

### Q1: 什么时候使用链表，什么时候使用数组？

**A**: 根据操作特点选择：

**使用数组**：
- 需要随机访问元素
- 元素数量固定或变化不大
- 内存连续访问（缓存友好）
- 示例：传感器数据缓冲区

**使用链表**：
- 频繁插入删除操作
- 元素数量动态变化
- 不需要随机访问
- 示例：任务队列、事件链表

### Q2: 如何避免内存泄漏？

**A**: 遵循以下原则：

1. **配对原则**：每个malloc对应一个free
```c
node_t *node = malloc(sizeof(node_t));
// 使用node
free(node);
node = NULL;  // 防止野指针
```

2. **清理函数**：提供销毁函数
```c
void list_destroy(list_t *list) {
    node_t *current = list->head;
    while (current != NULL) {
        node_t *next = current->next;
        free(current);
        current = next;
    }
}
```

3. **使用工具**：valgrind等内存检测工具

### Q3: 递归实现和迭代实现哪个更好？

**A**: 各有优劣：

**递归**：
- 优点：代码简洁，易理解
- 缺点：栈空间消耗，可能栈溢出
- 适用：树的遍历、分治算法

**迭代**：
- 优点：效率高，无栈溢出风险
- 缺点：代码可能复杂
- 适用：嵌入式系统（栈空间有限）

**建议**：嵌入式系统优先使用迭代

### Q4: 如何选择哈希函数？

**A**: 好的哈希函数应该：

1. **均匀分布**：减少冲突
2. **计算快速**：不影响性能
3. **确定性**：相同输入产生相同输出

常用哈希函数：
```c
// 字符串哈希
uint32_t hash_djb2(const char *str) {
    uint32_t hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}
```

### Q5: 如何处理哈希冲突？

**A**: 常用方法：

1. **链地址法**（本文使用）：
   - 每个桶使用链表存储冲突元素
   - 简单易实现
   - 适合冲突较多的情况

2. **开放地址法**：
   - 线性探测：顺序查找下一个空位
   - 二次探测：按平方数探测
   - 双重哈希：使用第二个哈希函数

```c
// 线性探测示例
uint32_t find_slot(hash_table_t *table, const char *key) {
    uint32_t index = hash_function(key);
    while (table->slots[index].used && 
           strcmp(table->slots[index].key, key) != 0) {
        index = (index + 1) % HASH_TABLE_SIZE;
    }
    return index;
}
```


## 总结

本教程深入讲解了C语言中常用数据结构的实现，这些是嵌入式系统开发的基础：

### 核心要点

1. **链表**
   - 单向链表：简单高效，适合单向遍历
   - 双向链表：支持双向遍历，删除更高效
   - 应用：动态数据管理、任务队列

2. **栈**
   - LIFO特性
   - 所有操作O(1)
   - 应用：函数调用、表达式求值

3. **队列**
   - FIFO特性
   - 循环队列充分利用空间
   - 应用：消息队列、缓冲区

4. **二叉树**
   - BST支持有序数据
   - 平均O(log n)操作
   - 应用：有序存储、优先级队列

5. **哈希表**
   - 平均O(1)查找
   - 空间换时间
   - 应用：快速查找、缓存

### 实践建议

- **理解原理**：掌握每种数据结构的特点和适用场景
- **动手实现**：自己实现一遍加深理解
- **性能分析**：了解时间和空间复杂度
- **实际应用**：在项目中合理选择数据结构
- **内存管理**：注意内存分配和释放

### 下一步学习

掌握这些数据结构后，建议继续学习：
- 高级数据结构（红黑树、B树、跳表）
- 算法设计（排序、搜索、图算法）
- 嵌入式C编程规范
- 代码优化技术

## 延伸阅读

### 推荐书籍

- 《数据结构与算法分析：C语言描述》- 经典教材
- 《算法导论》- 深入理解算法
- 《编程珠玑》- 实用算法技巧

### 在线资源

- [VisuAlgo](https://visualgo.net/) - 数据结构可视化
- [GeeksforGeeks](https://www.geeksforgeeks.org/) - 算法教程
- [LeetCode](https://leetcode.com/) - 算法练习

### 相关文章

- C语言高级特性详解 - 指针和函数指针
- C语言内存管理深入 - 动态内存分配
- 嵌入式C编程规范 - 代码质量保证

## 参考资料

1. Cormen, T. H., et al. "Introduction to Algorithms" (算法导论)
2. Weiss, M. A. "Data Structures and Algorithm Analysis in C" 
3. Sedgewick, R. "Algorithms in C" (C算法)
4. Kernighan, B. W., & Ritchie, D. M. "The C Programming Language"

---

**练习题**：

1. 实现一个支持撤销操作的文本编辑器（使用栈）
2. 使用队列实现一个生产者-消费者模型
3. 实现一个LRU缓存（使用哈希表+双向链表）
4. 编写一个表达式求值器（使用栈处理中缀表达式）

**实践项目**：

设计一个嵌入式任务调度系统，要求：
- 使用优先级队列管理任务
- 支持任务的创建、删除、执行
- 使用哈希表快速查找任务
- 实现任务统计功能（使用树结构）

**下一步**：建议学习 [嵌入式C编程规范](04-embedded-c-coding-standards.html)
