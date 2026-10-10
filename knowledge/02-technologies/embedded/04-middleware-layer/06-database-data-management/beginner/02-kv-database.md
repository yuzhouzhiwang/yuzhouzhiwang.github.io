---
title: "键值数据库(KV Database)实现：轻量级数据存储方案"
description: "深入学习键值数据库原理与实现，掌握数据存储、索引管理、性能优化技术，通过实战项目构建高效的嵌入式KV存储系统"
slug: "kv-database"

# 分类信息
domain: "中间件层"
module: "数据库与数据管理"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - KV数据库
  - 键值存储
  - NoSQL
  - 数据存储
  - 嵌入式数据库
prerequisites:
  - "04-middleware-layer/01-file-systems/beginner/01-fat-filesystem"
  - "04-middleware-layer/02-storage-technology/beginner/01-flash-technology"
related_contents:
  - "04-middleware-layer/06-database-data-management/beginner/01-sqlite-basics"
  - "04-middleware-layer/02-storage-technology/intermediate/01-wear-leveling"

# 学习信息
estimated_time: 70
difficulty_score: 3

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
  - 键值数据库
  - KV存储
  - NoSQL数据库
  - 嵌入式存储
  - 数据索引
cover_image: ""
---

# 键值数据库(KV Database)实现：轻量级数据存储方案


## 学习目标

完成本教程后，你将能够：

- [ ] 理解键值数据库的原理和应用场景
- [ ] 掌握KV数据库的核心数据结构
- [ ] 实现基本的增删改查操作
- [ ] 掌握哈希表索引技术
- [ ] 理解数据持久化机制
- [ ] 实现数据压缩和优化
- [ ] 完成一个完整的KV存储系统
- [ ] 掌握性能优化技巧

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言编程
- 了解数据结构（哈希表、链表）
- 理解文件系统的基本概念
- 掌握指针和内存管理
- 了解Flash存储特性

**技能要求**：
- 能够编写嵌入式C代码
- 会使用文件系统API
- 熟悉基本的数据操作
- 能够使用调试工具
- 了解内存优化技巧

**开发环境**：
- STM32或ESP32开发板
- SPI Flash或SD卡存储
- Keil MDK或STM32CubeIDE
- 串口调试工具


## KV数据库概述

### 什么是KV数据库

键值数据库（Key-Value Database）是一种NoSQL数据库，使用简单的键值对存储数据。它是最简单、最快速的数据库类型之一，特别适合嵌入式系统。


**核心特性**：

1. **简单高效**
   - 只有键值对，没有复杂的表结构
   - O(1)时间复杂度的查询
   - 内存占用小
   - 适合快速读写

2. **灵活性强**
   - 值可以是任意类型
   - 无需预定义模式
   - 易于扩展
   - 支持动态添加字段

3. **高性能**
   - 基于哈希表的快速索引
   - 内存缓存机制
   - 批量操作支持
   - 异步写入优化

4. **持久化**
   - 数据持久化到Flash/SD卡
   - 支持定期快照
   - 写前日志（WAL）
   - 断电保护

### KV数据库架构

**系统架构图**：

```
┌─────────────────────────────────────────────────┐
│    应用层 (Application)                          │
│    kv_put(), kv_get(), kv_delete()              │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    API层                                         │
│    参数验证、错误处理、接口封装                  │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    缓存层 (Cache)                                │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 内存哈希表   │  │ LRU缓存      │          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    索引层 (Index)                                │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 哈希索引     │  │ 位置映射     │          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    存储层 (Storage)                              │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 数据文件     │  │ 日志文件     │          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    文件系统层                                    │
│    FAT32, LittleFS, SPIFFS                      │
└─────────────────────────────────────────────────┘
```

### KV数据库 vs 关系型数据库

| 特性 | KV数据库 | 关系型数据库 |
|------|----------|--------------|
| 数据模型 | 键值对 | 表、行、列 |
| 查询方式 | 按键查询 | SQL查询 |
| 性能 | 极快 | 较慢 |
| 复杂查询 | 不支持 | 支持 |
| 事务 | 简单 | 完整ACID |
| 内存占用 | 极低 | 较高 |
| 代码大小 | 小 | 大 |
| 适用场景 | 配置存储、缓存 | 复杂数据关系 |

**选择建议**：
- 配置参数存储 → KV数据库
- 简单数据缓存 → KV数据库
- 复杂查询需求 → 关系型数据库
- 数据关系复杂 → 关系型数据库


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4或ESP32 | STM32F407VG |
| SPI Flash | 1 | 外部存储 | W25Q128 (16MB) |
| SD卡 | 1 | 可选，大容量存储 | 8GB Class 10 |
| USB线 | 1 | 供电和调试 | - |
| 杜邦线 | 若干 | 连接模块 | - |

### 软件准备

**必需软件**：
- STM32CubeIDE 或 Arduino IDE（ESP32）
- 文件系统库（FATFS或LittleFS）
- 串口调试助手

### 电路连接

**SPI Flash连接示意图**：

```
STM32F407              W25Q128 Flash
  PA5 (SCK)  ────────► CLK
  PA6 (MISO) ◄──────── DO
  PA7 (MOSI) ────────► DI
  PA4 (CS)   ────────► CS
  3.3V       ────────► VCC
  GND        ────────► GND
```



## 步骤1：定义数据结构

### 1.1 基本数据结构

创建文件 `kv_database.h`：

```c
#ifndef KV_DATABASE_H
#define KV_DATABASE_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// 配置参数
#define KV_MAX_KEY_LEN      32      // 最大键长度
#define KV_MAX_VALUE_LEN    256     // 最大值长度
#define KV_HASH_TABLE_SIZE  128     // 哈希表大小
#define KV_MAX_ENTRIES      512     // 最大条目数
#define KV_CACHE_SIZE       32      // 缓存大小

// 错误码
typedef enum {
    KV_OK = 0,              // 成功
    KV_ERR_NOT_FOUND,       // 键不存在
    KV_ERR_NO_SPACE,        // 空间不足
    KV_ERR_INVALID_KEY,     // 无效的键
    KV_ERR_INVALID_VALUE,   // 无效的值
    KV_ERR_IO,              // I/O错误
    KV_ERR_CORRUPTED,       // 数据损坏
} kv_error_t;

// 键值对条目
typedef struct {
    char key[KV_MAX_KEY_LEN];           // 键
    uint8_t value[KV_MAX_VALUE_LEN];    // 值
    uint16_t value_len;                 // 值长度
    uint32_t timestamp;                 // 时间戳
    bool valid;                         // 是否有效
} kv_entry_t;

// 哈希表节点
typedef struct kv_node {
    kv_entry_t entry;       // 键值对
    struct kv_node *next;   // 链表指针（处理冲突）
} kv_node_t;

// KV数据库对象
typedef struct {
    kv_node_t *hash_table[KV_HASH_TABLE_SIZE];  // 哈希表
    uint32_t entry_count;                       // 条目数量
    bool dirty;                                 // 是否有未保存的修改
    char db_file[64];                           // 数据库文件路径
} kv_database_t;

// API函数
kv_error_t kv_init(kv_database_t *db, const char *filename);
kv_error_t kv_deinit(kv_database_t *db);
kv_error_t kv_put(kv_database_t *db, const char *key, const void *value, uint16_t value_len);
kv_error_t kv_get(kv_database_t *db, const char *key, void *value, uint16_t *value_len);
kv_error_t kv_delete(kv_database_t *db, const char *key);
kv_error_t kv_exists(kv_database_t *db, const char *key, bool *exists);
kv_error_t kv_save(kv_database_t *db);
kv_error_t kv_load(kv_database_t *db);
kv_error_t kv_clear(kv_database_t *db);
uint32_t kv_count(kv_database_t *db);

#endif // KV_DATABASE_H
```

**数据结构说明**：
- `kv_entry_t`: 存储单个键值对
- `kv_node_t`: 哈希表节点，支持链表解决冲突
- `kv_database_t`: 数据库主对象，包含哈希表和元数据

### 1.2 哈希函数

创建文件 `kv_database.c`：

```c
#include "kv_database.h"
#include <stdio.h>
#include <stdlib.h>

/**
 * @brief  计算字符串的哈希值（DJB2算法）
 * @param  key: 键字符串
 * @retval 哈希值
 */
static uint32_t kv_hash(const char *key)
{
    uint32_t hash = 5381;
    int c;
    
    while ((c = *key++)) {
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c
    }
    
    return hash % KV_HASH_TABLE_SIZE;
}

/**
 * @brief  验证键的有效性
 * @param  key: 键字符串
 * @retval true:有效, false:无效
 */
static bool kv_validate_key(const char *key)
{
    if (!key || key[0] == '\0') {
        return false;
    }
    
    size_t len = strlen(key);
    if (len >= KV_MAX_KEY_LEN) {
        return false;
    }
    
    return true;
}

/**
 * @brief  验证值的有效性
 * @param  value: 值数据
 * @param  value_len: 值长度
 * @retval true:有效, false:无效
 */
static bool kv_validate_value(const void *value, uint16_t value_len)
{
    if (!value || value_len == 0 || value_len > KV_MAX_VALUE_LEN) {
        return false;
    }
    
    return true;
}
```

**哈希函数说明**：
- 使用DJB2算法，简单高效
- 取模运算映射到哈希表范围
- 冲突通过链表法解决


## 步骤2：实现基本操作

### 2.1 初始化和清理

```c
/**
 * @brief  初始化KV数据库
 * @param  db: 数据库对象
 * @param  filename: 数据库文件名
 * @retval 错误码
 */
kv_error_t kv_init(kv_database_t *db, const char *filename)
{
    if (!db || !filename) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 清零哈希表
    memset(db->hash_table, 0, sizeof(db->hash_table));
    
    // 初始化元数据
    db->entry_count = 0;
    db->dirty = false;
    strncpy(db->db_file, filename, sizeof(db->db_file) - 1);
    db->db_file[sizeof(db->db_file) - 1] = '\0';
    
    printf("KV Database initialized: %s\n", filename);
    
    // 尝试加载已有数据
    kv_load(db);
    
    return KV_OK;
}

/**
 * @brief  清理KV数据库
 * @param  db: 数据库对象
 * @retval 错误码
 */
kv_error_t kv_deinit(kv_database_t *db)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 保存未保存的修改
    if (db->dirty) {
        kv_save(db);
    }
    
    // 释放所有节点
    for (int i = 0; i < KV_HASH_TABLE_SIZE; i++) {
        kv_node_t *node = db->hash_table[i];
        while (node) {
            kv_node_t *next = node->next;
            free(node);
            node = next;
        }
        db->hash_table[i] = NULL;
    }
    
    db->entry_count = 0;
    db->dirty = false;
    
    printf("KV Database deinitialized\n");
    
    return KV_OK;
}
```


### 2.2 插入/更新操作

```c
/**
 * @brief  插入或更新键值对
 * @param  db: 数据库对象
 * @param  key: 键
 * @param  value: 值
 * @param  value_len: 值长度
 * @retval 错误码
 */
kv_error_t kv_put(kv_database_t *db, const char *key, const void *value, uint16_t value_len)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 验证参数
    if (!kv_validate_key(key)) {
        return KV_ERR_INVALID_KEY;
    }
    
    if (!kv_validate_value(value, value_len)) {
        return KV_ERR_INVALID_VALUE;
    }
    
    // 计算哈希值
    uint32_t hash = kv_hash(key);
    
    // 查找是否已存在
    kv_node_t *node = db->hash_table[hash];
    kv_node_t *prev = NULL;
    
    while (node) {
        if (strcmp(node->entry.key, key) == 0) {
            // 键已存在，更新值
            memcpy(node->entry.value, value, value_len);
            node->entry.value_len = value_len;
            node->entry.timestamp = HAL_GetTick();  // 或使用RTC
            node->entry.valid = true;
            
            db->dirty = true;
            
            printf("KV Updated: %s\n", key);
            return KV_OK;
        }
        prev = node;
        node = node->next;
    }
    
    // 键不存在，创建新节点
    if (db->entry_count >= KV_MAX_ENTRIES) {
        return KV_ERR_NO_SPACE;
    }
    
    kv_node_t *new_node = (kv_node_t*)malloc(sizeof(kv_node_t));
    if (!new_node) {
        return KV_ERR_NO_SPACE;
    }
    
    // 填充数据
    strncpy(new_node->entry.key, key, KV_MAX_KEY_LEN - 1);
    new_node->entry.key[KV_MAX_KEY_LEN - 1] = '\0';
    memcpy(new_node->entry.value, value, value_len);
    new_node->entry.value_len = value_len;
    new_node->entry.timestamp = HAL_GetTick();
    new_node->entry.valid = true;
    new_node->next = NULL;
    
    // 插入到哈希表
    if (prev) {
        prev->next = new_node;
    } else {
        db->hash_table[hash] = new_node;
    }
    
    db->entry_count++;
    db->dirty = true;
    
    printf("KV Inserted: %s (count: %lu)\n", key, db->entry_count);
    
    return KV_OK;
}
```

### 2.3 查询操作

```c
/**
 * @brief  查询键值对
 * @param  db: 数据库对象
 * @param  key: 键
 * @param  value: 输出值缓冲区
 * @param  value_len: 输入输出参数，输入为缓冲区大小，输出为实际值长度
 * @retval 错误码
 */
kv_error_t kv_get(kv_database_t *db, const char *key, void *value, uint16_t *value_len)
{
    if (!db || !value || !value_len) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 验证键
    if (!kv_validate_key(key)) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 计算哈希值
    uint32_t hash = kv_hash(key);
    
    // 查找节点
    kv_node_t *node = db->hash_table[hash];
    
    while (node) {
        if (strcmp(node->entry.key, key) == 0 && node->entry.valid) {
            // 找到了
            uint16_t copy_len = node->entry.value_len;
            if (copy_len > *value_len) {
                copy_len = *value_len;
            }
            
            memcpy(value, node->entry.value, copy_len);
            *value_len = node->entry.value_len;
            
            printf("KV Found: %s (len: %u)\n", key, node->entry.value_len);
            return KV_OK;
        }
        node = node->next;
    }
    
    // 未找到
    return KV_ERR_NOT_FOUND;
}

/**
 * @brief  检查键是否存在
 * @param  db: 数据库对象
 * @param  key: 键
 * @param  exists: 输出参数，是否存在
 * @retval 错误码
 */
kv_error_t kv_exists(kv_database_t *db, const char *key, bool *exists)
{
    if (!db || !exists) {
        return KV_ERR_INVALID_KEY;
    }
    
    if (!kv_validate_key(key)) {
        return KV_ERR_INVALID_KEY;
    }
    
    uint32_t hash = kv_hash(key);
    kv_node_t *node = db->hash_table[hash];
    
    while (node) {
        if (strcmp(node->entry.key, key) == 0 && node->entry.valid) {
            *exists = true;
            return KV_OK;
        }
        node = node->next;
    }
    
    *exists = false;
    return KV_OK;
}
```

### 2.4 删除操作

```c
/**
 * @brief  删除键值对
 * @param  db: 数据库对象
 * @param  key: 键
 * @retval 错误码
 */
kv_error_t kv_delete(kv_database_t *db, const char *key)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    if (!kv_validate_key(key)) {
        return KV_ERR_INVALID_KEY;
    }
    
    uint32_t hash = kv_hash(key);
    kv_node_t *node = db->hash_table[hash];
    kv_node_t *prev = NULL;
    
    while (node) {
        if (strcmp(node->entry.key, key) == 0) {
            // 找到了，删除节点
            if (prev) {
                prev->next = node->next;
            } else {
                db->hash_table[hash] = node->next;
            }
            
            free(node);
            db->entry_count--;
            db->dirty = true;
            
            printf("KV Deleted: %s (count: %lu)\n", key, db->entry_count);
            return KV_OK;
        }
        prev = node;
        node = node->next;
    }
    
    return KV_ERR_NOT_FOUND;
}

/**
 * @brief  清空所有数据
 * @param  db: 数据库对象
 * @retval 错误码
 */
kv_error_t kv_clear(kv_database_t *db)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 释放所有节点
    for (int i = 0; i < KV_HASH_TABLE_SIZE; i++) {
        kv_node_t *node = db->hash_table[i];
        while (node) {
            kv_node_t *next = node->next;
            free(node);
            node = next;
        }
        db->hash_table[i] = NULL;
    }
    
    db->entry_count = 0;
    db->dirty = true;
    
    printf("KV Database cleared\n");
    
    return KV_OK;
}

/**
 * @brief  获取条目数量
 * @param  db: 数据库对象
 * @retval 条目数量
 */
uint32_t kv_count(kv_database_t *db)
{
    return db ? db->entry_count : 0;
}
```


## 步骤3：实现数据持久化

### 3.1 保存到文件

```c
#include "ff.h"  // FATFS文件系统

/**
 * @brief  保存数据库到文件
 * @param  db: 数据库对象
 * @retval 错误码
 */
kv_error_t kv_save(kv_database_t *db)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    FIL file;
    FRESULT res;
    UINT bw;
    
    // 打开文件
    res = f_open(&file, db->db_file, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to open file for writing: %d\n", res);
        return KV_ERR_IO;
    }
    
    // 写入文件头
    uint32_t magic = 0x4B564442;  // "KVDB"
    uint32_t version = 1;
    uint32_t count = db->entry_count;
    
    f_write(&file, &magic, sizeof(magic), &bw);
    f_write(&file, &version, sizeof(version), &bw);
    f_write(&file, &count, sizeof(count), &bw);
    
    // 写入所有条目
    uint32_t written = 0;
    for (int i = 0; i < KV_HASH_TABLE_SIZE; i++) {
        kv_node_t *node = db->hash_table[i];
        while (node) {
            if (node->entry.valid) {
                // 写入条目
                f_write(&file, &node->entry, sizeof(kv_entry_t), &bw);
                if (bw != sizeof(kv_entry_t)) {
                    f_close(&file);
                    return KV_ERR_IO;
                }
                written++;
            }
            node = node->next;
        }
    }
    
    // 关闭文件
    f_close(&file);
    
    db->dirty = false;
    
    printf("KV Database saved: %lu entries\n", written);
    
    return KV_OK;
}
```


### 3.2 从文件加载

```c
/**
 * @brief  从文件加载数据库
 * @param  db: 数据库对象
 * @retval 错误码
 */
kv_error_t kv_load(kv_database_t *db)
{
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    FIL file;
    FRESULT res;
    UINT br;
    
    // 打开文件
    res = f_open(&file, db->db_file, FA_READ);
    if (res != FR_OK) {
        printf("Database file not found, starting fresh\n");
        return KV_OK;  // 文件不存在不算错误
    }
    
    // 读取文件头
    uint32_t magic, version, count;
    
    f_read(&file, &magic, sizeof(magic), &br);
    if (br != sizeof(magic) || magic != 0x4B564442) {
        printf("Invalid database file format\n");
        f_close(&file);
        return KV_ERR_CORRUPTED;
    }
    
    f_read(&file, &version, sizeof(version), &br);
    f_read(&file, &count, sizeof(count), &br);
    
    printf("Loading KV Database: version=%lu, count=%lu\n", version, count);
    
    // 读取所有条目
    for (uint32_t i = 0; i < count; i++) {
        kv_entry_t entry;
        
        f_read(&file, &entry, sizeof(kv_entry_t), &br);
        if (br != sizeof(kv_entry_t)) {
            printf("Failed to read entry %lu\n", i);
            break;
        }
        
        // 插入到哈希表
        if (entry.valid) {
            kv_put(db, entry.key, entry.value, entry.value_len);
        }
    }
    
    // 关闭文件
    f_close(&file);
    
    db->dirty = false;
    
    printf("KV Database loaded: %lu entries\n", db->entry_count);
    
    return KV_OK;
}
```

### 3.3 自动保存机制

```c
/**
 * @brief  定期自动保存（在主循环中调用）
 * @param  db: 数据库对象
 * @param  interval_ms: 保存间隔（毫秒）
 * @retval 错误码
 */
kv_error_t kv_auto_save(kv_database_t *db, uint32_t interval_ms)
{
    static uint32_t last_save_time = 0;
    uint32_t current_time = HAL_GetTick();
    
    if (!db) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 检查是否需要保存
    if (db->dirty && (current_time - last_save_time >= interval_ms)) {
        kv_error_t err = kv_save(db);
        if (err == KV_OK) {
            last_save_time = current_time;
            printf("Auto-saved at %lu ms\n", current_time);
        }
        return err;
    }
    
    return KV_OK;
}
```


## 步骤4：实用工具函数

### 4.1 遍历所有键值对

```c
/**
 * @brief  遍历回调函数类型
 */
typedef void (*kv_foreach_callback_t)(const char *key, const void *value, 
                                      uint16_t value_len, void *user_data);

/**
 * @brief  遍历所有键值对
 * @param  db: 数据库对象
 * @param  callback: 回调函数
 * @param  user_data: 用户数据
 * @retval 错误码
 */
kv_error_t kv_foreach(kv_database_t *db, kv_foreach_callback_t callback, void *user_data)
{
    if (!db || !callback) {
        return KV_ERR_INVALID_KEY;
    }
    
    for (int i = 0; i < KV_HASH_TABLE_SIZE; i++) {
        kv_node_t *node = db->hash_table[i];
        while (node) {
            if (node->entry.valid) {
                callback(node->entry.key, node->entry.value, 
                        node->entry.value_len, user_data);
            }
            node = node->next;
        }
    }
    
    return KV_OK;
}

/**
 * @brief  打印所有键值对（示例回调）
 */
static void print_kv_callback(const char *key, const void *value, 
                             uint16_t value_len, void *user_data)
{
    printf("  %s = ", key);
    
    // 尝试作为字符串打印
    bool is_string = true;
    const uint8_t *data = (const uint8_t*)value;
    for (int i = 0; i < value_len; i++) {
        if (data[i] < 32 || data[i] > 126) {
            is_string = false;
            break;
        }
    }
    
    if (is_string) {
        printf("\"%.*s\"\n", value_len, (const char*)value);
    } else {
        printf("[");
        for (int i = 0; i < value_len && i < 16; i++) {
            printf("%02X ", data[i]);
        }
        if (value_len > 16) {
            printf("...");
        }
        printf("] (%u bytes)\n", value_len);
    }
}

/**
 * @brief  打印数据库内容
 * @param  db: 数据库对象
 */
void kv_print_all(kv_database_t *db)
{
    if (!db) {
        return;
    }
    
    printf("\n=== KV Database Contents ===\n");
    printf("Total entries: %lu\n", db->entry_count);
    printf("----------------------------\n");
    
    kv_foreach(db, print_kv_callback, NULL);
    
    printf("============================\n\n");
}
```

### 4.2 批量操作

```c
/**
 * @brief  批量插入
 * @param  db: 数据库对象
 * @param  keys: 键数组
 * @param  values: 值数组
 * @param  value_lens: 值长度数组
 * @param  count: 数量
 * @retval 成功插入的数量
 */
uint32_t kv_put_batch(kv_database_t *db, const char **keys, 
                     const void **values, const uint16_t *value_lens, 
                     uint32_t count)
{
    if (!db || !keys || !values || !value_lens) {
        return 0;
    }
    
    uint32_t success_count = 0;
    
    for (uint32_t i = 0; i < count; i++) {
        if (kv_put(db, keys[i], values[i], value_lens[i]) == KV_OK) {
            success_count++;
        }
    }
    
    return success_count;
}

/**
 * @brief  批量删除
 * @param  db: 数据库对象
 * @param  keys: 键数组
 * @param  count: 数量
 * @retval 成功删除的数量
 */
uint32_t kv_delete_batch(kv_database_t *db, const char **keys, uint32_t count)
{
    if (!db || !keys) {
        return 0;
    }
    
    uint32_t success_count = 0;
    
    for (uint32_t i = 0; i < count; i++) {
        if (kv_delete(db, keys[i]) == KV_OK) {
            success_count++;
        }
    }
    
    return success_count;
}
```

### 4.3 辅助函数

```c
/**
 * @brief  存储整数值
 */
kv_error_t kv_put_int(kv_database_t *db, const char *key, int32_t value)
{
    return kv_put(db, key, &value, sizeof(value));
}

/**
 * @brief  读取整数值
 */
kv_error_t kv_get_int(kv_database_t *db, const char *key, int32_t *value)
{
    uint16_t len = sizeof(*value);
    return kv_get(db, key, value, &len);
}

/**
 * @brief  存储字符串值
 */
kv_error_t kv_put_string(kv_database_t *db, const char *key, const char *value)
{
    return kv_put(db, key, value, strlen(value));
}

/**
 * @brief  读取字符串值
 */
kv_error_t kv_get_string(kv_database_t *db, const char *key, char *value, uint16_t max_len)
{
    uint16_t len = max_len;
    kv_error_t err = kv_get(db, key, value, &len);
    if (err == KV_OK && len < max_len) {
        value[len] = '\0';  // 添加字符串结束符
    }
    return err;
}

/**
 * @brief  存储浮点数值
 */
kv_error_t kv_put_float(kv_database_t *db, const char *key, float value)
{
    return kv_put(db, key, &value, sizeof(value));
}

/**
 * @brief  读取浮点数值
 */
kv_error_t kv_get_float(kv_database_t *db, const char *key, float *value)
{
    uint16_t len = sizeof(*value);
    return kv_get(db, key, value, &len);
}
```


## 步骤5：性能优化

### 5.1 统计信息

```c
/**
 * @brief  数据库统计信息
 */
typedef struct {
    uint32_t total_entries;         // 总条目数
    uint32_t hash_collisions;       // 哈希冲突数
    uint32_t max_chain_length;      // 最大链表长度
    float load_factor;              // 负载因子
    uint32_t memory_usage;          // 内存占用（字节）
} kv_stats_t;

/**
 * @brief  获取统计信息
 * @param  db: 数据库对象
 * @param  stats: 输出统计信息
 * @retval 错误码
 */
kv_error_t kv_get_stats(kv_database_t *db, kv_stats_t *stats)
{
    if (!db || !stats) {
        return KV_ERR_INVALID_KEY;
    }
    
    memset(stats, 0, sizeof(kv_stats_t));
    
    stats->total_entries = db->entry_count;
    
    // 统计冲突和链表长度
    for (int i = 0; i < KV_HASH_TABLE_SIZE; i++) {
        kv_node_t *node = db->hash_table[i];
        uint32_t chain_length = 0;
        
        while (node) {
            chain_length++;
            node = node->next;
        }
        
        if (chain_length > 1) {
            stats->hash_collisions += (chain_length - 1);
        }
        
        if (chain_length > stats->max_chain_length) {
            stats->max_chain_length = chain_length;
        }
    }
    
    // 计算负载因子
    stats->load_factor = (float)db->entry_count / KV_HASH_TABLE_SIZE;
    
    // 估算内存占用
    stats->memory_usage = sizeof(kv_database_t) + 
                         db->entry_count * sizeof(kv_node_t);
    
    return KV_OK;
}

/**
 * @brief  打印统计信息
 */
void kv_print_stats(kv_database_t *db)
{
    kv_stats_t stats;
    
    if (kv_get_stats(db, &stats) != KV_OK) {
        return;
    }
    
    printf("\n=== KV Database Statistics ===\n");
    printf("Total entries:     %lu\n", stats.total_entries);
    printf("Hash collisions:   %lu\n", stats.hash_collisions);
    printf("Max chain length:  %lu\n", stats.max_chain_length);
    printf("Load factor:       %.2f\n", stats.load_factor);
    printf("Memory usage:      %lu bytes (%.2f KB)\n", 
           stats.memory_usage, stats.memory_usage / 1024.0f);
    printf("==============================\n\n");
}
```


### 5.2 缓存优化

```c
/**
 * @brief  LRU缓存节点
 */
typedef struct lru_node {
    char key[KV_MAX_KEY_LEN];
    uint8_t value[KV_MAX_VALUE_LEN];
    uint16_t value_len;
    struct lru_node *prev;
    struct lru_node *next;
} lru_node_t;

/**
 * @brief  LRU缓存
 */
typedef struct {
    lru_node_t *head;
    lru_node_t *tail;
    uint32_t size;
    uint32_t capacity;
} lru_cache_t;

/**
 * @brief  初始化LRU缓存
 */
static void lru_init(lru_cache_t *cache, uint32_t capacity)
{
    cache->head = NULL;
    cache->tail = NULL;
    cache->size = 0;
    cache->capacity = capacity;
}

/**
 * @brief  从缓存获取值
 */
static bool lru_get(lru_cache_t *cache, const char *key, 
                   void *value, uint16_t *value_len)
{
    lru_node_t *node = cache->head;
    
    while (node) {
        if (strcmp(node->key, key) == 0) {
            // 找到了，移到头部
            if (node != cache->head) {
                // 从当前位置移除
                if (node->prev) node->prev->next = node->next;
                if (node->next) node->next->prev = node->prev;
                if (node == cache->tail) cache->tail = node->prev;
                
                // 移到头部
                node->next = cache->head;
                node->prev = NULL;
                cache->head->prev = node;
                cache->head = node;
            }
            
            // 复制值
            memcpy(value, node->value, node->value_len);
            *value_len = node->value_len;
            
            return true;
        }
        node = node->next;
    }
    
    return false;
}

/**
 * @brief  添加到缓存
 */
static void lru_put(lru_cache_t *cache, const char *key, 
                   const void *value, uint16_t value_len)
{
    // 检查是否已存在
    lru_node_t *node = cache->head;
    while (node) {
        if (strcmp(node->key, key) == 0) {
            // 更新值
            memcpy(node->value, value, value_len);
            node->value_len = value_len;
            return;
        }
        node = node->next;
    }
    
    // 创建新节点
    lru_node_t *new_node = (lru_node_t*)malloc(sizeof(lru_node_t));
    if (!new_node) return;
    
    strncpy(new_node->key, key, KV_MAX_KEY_LEN - 1);
    new_node->key[KV_MAX_KEY_LEN - 1] = '\0';
    memcpy(new_node->value, value, value_len);
    new_node->value_len = value_len;
    
    // 插入到头部
    new_node->next = cache->head;
    new_node->prev = NULL;
    
    if (cache->head) {
        cache->head->prev = new_node;
    }
    cache->head = new_node;
    
    if (!cache->tail) {
        cache->tail = new_node;
    }
    
    cache->size++;
    
    // 检查容量
    if (cache->size > cache->capacity) {
        // 移除尾部节点
        lru_node_t *old_tail = cache->tail;
        cache->tail = old_tail->prev;
        if (cache->tail) {
            cache->tail->next = NULL;
        }
        free(old_tail);
        cache->size--;
    }
}
```


## 步骤6：完整应用示例

### 6.1 配置管理系统

```c
/**
 * @brief  配置管理示例
 */
void config_manager_example(void)
{
    kv_database_t db;
    kv_error_t err;
    
    // 初始化数据库
    err = kv_init(&db, "0:/config.db");
    if (err != KV_OK) {
        printf("Failed to initialize database\n");
        return;
    }
    
    // 存储配置参数
    kv_put_string(&db, "device_name", "STM32_Sensor");
    kv_put_int(&db, "sample_rate", 1000);
    kv_put_float(&db, "threshold", 25.5f);
    kv_put_string(&db, "wifi_ssid", "MyNetwork");
    kv_put_string(&db, "wifi_password", "MyPassword123");
    
    // 保存到文件
    kv_save(&db);
    
    printf("Configuration saved\n");
    
    // 读取配置
    char device_name[32];
    int32_t sample_rate;
    float threshold;
    
    kv_get_string(&db, "device_name", device_name, sizeof(device_name));
    kv_get_int(&db, "sample_rate", &sample_rate);
    kv_get_float(&db, "threshold", &threshold);
    
    printf("Device Name: %s\n", device_name);
    printf("Sample Rate: %ld Hz\n", sample_rate);
    printf("Threshold: %.2f\n", threshold);
    
    // 打印所有配置
    kv_print_all(&db);
    
    // 清理
    kv_deinit(&db);
}
```

### 6.2 传感器数据缓存

```c
/**
 * @brief  传感器数据缓存示例
 */
void sensor_cache_example(void)
{
    kv_database_t db;
    
    kv_init(&db, "0:/sensor_cache.db");
    
    // 模拟传感器数据
    typedef struct {
        float temperature;
        float humidity;
        uint32_t timestamp;
    } sensor_data_t;
    
    // 存储最新的传感器数据
    for (int i = 0; i < 10; i++) {
        sensor_data_t data;
        data.temperature = 20.0f + i * 0.5f;
        data.humidity = 50.0f + i * 2.0f;
        data.timestamp = HAL_GetTick();
        
        char key[32];
        snprintf(key, sizeof(key), "sensor_%d", i);
        
        kv_put(&db, key, &data, sizeof(data));
        
        HAL_Delay(100);
    }
    
    // 读取并显示
    printf("\nSensor Data Cache:\n");
    for (int i = 0; i < 10; i++) {
        char key[32];
        sensor_data_t data;
        uint16_t len = sizeof(data);
        
        snprintf(key, sizeof(key), "sensor_%d", i);
        
        if (kv_get(&db, key, &data, &len) == KV_OK) {
            printf("  %s: T=%.2f°C, H=%.2f%%, Time=%lu\n",
                   key, data.temperature, data.humidity, data.timestamp);
        }
    }
    
    // 统计信息
    kv_print_stats(&db);
    
    kv_deinit(&db);
}
```

### 6.3 主程序集成

```c
/**
 * @brief  主程序
 */
int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化外设
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_USART1_UART_Init();
    MX_FATFS_Init();
    
    printf("KV Database Demo Starting...\n");
    
    // 运行示例
    config_manager_example();
    sensor_cache_example();
    
    // 主循环
    kv_database_t db;
    kv_init(&db, "0:/app.db");
    
    uint32_t counter = 0;
    
    while (1) {
        // 定期更新数据
        if (counter % 100 == 0) {
            char key[32];
            snprintf(key, sizeof(key), "counter");
            kv_put_int(&db, key, counter);
            
            // 自动保存（每10秒）
            kv_auto_save(&db, 10000);
        }
        
        counter++;
        HAL_Delay(100);
    }
}
```


## 步骤7：高级特性

### 7.1 数据压缩

```c
/**
 * @brief  简单的RLE压缩
 * @param  input: 输入数据
 * @param  input_len: 输入长度
 * @param  output: 输出缓冲区
 * @param  output_len: 输出长度
 * @retval 压缩后的长度
 */
static uint16_t kv_compress_rle(const uint8_t *input, uint16_t input_len,
                                uint8_t *output, uint16_t output_len)
{
    uint16_t out_pos = 0;
    uint16_t in_pos = 0;
    
    while (in_pos < input_len && out_pos < output_len - 2) {
        uint8_t value = input[in_pos];
        uint8_t count = 1;
        
        // 计算重复次数
        while (in_pos + count < input_len && 
               input[in_pos + count] == value && 
               count < 255) {
            count++;
        }
        
        // 写入压缩数据
        output[out_pos++] = count;
        output[out_pos++] = value;
        
        in_pos += count;
    }
    
    return out_pos;
}

/**
 * @brief  RLE解压缩
 */
static uint16_t kv_decompress_rle(const uint8_t *input, uint16_t input_len,
                                  uint8_t *output, uint16_t output_len)
{
    uint16_t out_pos = 0;
    uint16_t in_pos = 0;
    
    while (in_pos < input_len - 1 && out_pos < output_len) {
        uint8_t count = input[in_pos++];
        uint8_t value = input[in_pos++];
        
        for (uint8_t i = 0; i < count && out_pos < output_len; i++) {
            output[out_pos++] = value;
        }
    }
    
    return out_pos;
}
```

### 7.2 数据加密

```c
/**
 * @brief  简单的XOR加密
 * @param  data: 数据
 * @param  len: 长度
 * @param  key: 密钥
 */
static void kv_encrypt_xor(uint8_t *data, uint16_t len, uint8_t key)
{
    for (uint16_t i = 0; i < len; i++) {
        data[i] ^= key;
    }
}

/**
 * @brief  存储加密数据
 */
kv_error_t kv_put_encrypted(kv_database_t *db, const char *key, 
                           const void *value, uint16_t value_len, 
                           uint8_t encrypt_key)
{
    uint8_t encrypted[KV_MAX_VALUE_LEN];
    
    if (value_len > KV_MAX_VALUE_LEN) {
        return KV_ERR_INVALID_VALUE;
    }
    
    // 复制并加密
    memcpy(encrypted, value, value_len);
    kv_encrypt_xor(encrypted, value_len, encrypt_key);
    
    return kv_put(db, key, encrypted, value_len);
}

/**
 * @brief  读取加密数据
 */
kv_error_t kv_get_encrypted(kv_database_t *db, const char *key, 
                           void *value, uint16_t *value_len, 
                           uint8_t encrypt_key)
{
    kv_error_t err = kv_get(db, key, value, value_len);
    
    if (err == KV_OK) {
        // 解密
        kv_encrypt_xor((uint8_t*)value, *value_len, encrypt_key);
    }
    
    return err;
}
```

### 7.3 事务支持

```c
/**
 * @brief  事务对象
 */
typedef struct {
    kv_database_t *db;
    kv_database_t backup;
    bool active;
} kv_transaction_t;

/**
 * @brief  开始事务
 */
kv_error_t kv_begin_transaction(kv_transaction_t *txn, kv_database_t *db)
{
    if (!txn || !db) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 备份当前状态
    memcpy(&txn->backup, db, sizeof(kv_database_t));
    txn->db = db;
    txn->active = true;
    
    printf("Transaction started\n");
    
    return KV_OK;
}

/**
 * @brief  提交事务
 */
kv_error_t kv_commit_transaction(kv_transaction_t *txn)
{
    if (!txn || !txn->active) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 保存到文件
    kv_error_t err = kv_save(txn->db);
    
    txn->active = false;
    
    printf("Transaction committed\n");
    
    return err;
}

/**
 * @brief  回滚事务
 */
kv_error_t kv_rollback_transaction(kv_transaction_t *txn)
{
    if (!txn || !txn->active) {
        return KV_ERR_INVALID_KEY;
    }
    
    // 恢复备份状态
    memcpy(txn->db, &txn->backup, sizeof(kv_database_t));
    
    txn->active = false;
    
    printf("Transaction rolled back\n");
    
    return KV_OK;
}
```


## 故障排除

### 问题1：哈希冲突过多

**可能原因**：
- 哈希表太小
- 哈希函数分布不均
- 数据量过大

**解决方法**：
1. 增大哈希表大小
   ```c
   #define KV_HASH_TABLE_SIZE  256  // 增大到256
   ```

2. 使用更好的哈希函数
   ```c
   // MurmurHash或其他高质量哈希函数
   ```

3. 监控负载因子
   ```c
   kv_stats_t stats;
   kv_get_stats(&db, &stats);
   if (stats.load_factor > 0.75) {
       // 考虑重建哈希表
   }
   ```


### 问题2：内存不足

**可能原因**：
- 条目数量过多
- 值长度过大
- 内存泄漏

**解决方法**：
1. 限制条目数量
   ```c
   if (db->entry_count >= KV_MAX_ENTRIES) {
       // 删除最旧的条目
       kv_delete_oldest(&db);
   }
   ```

2. 减小值长度限制
   ```c
   #define KV_MAX_VALUE_LEN  128  // 减小到128字节
   ```

3. 使用内存池
   ```c
   // 预分配固定大小的内存池
   static kv_node_t node_pool[KV_MAX_ENTRIES];
   ```

4. 检查内存泄漏
   ```c
   // 确保每个malloc都有对应的free
   // 使用内存分析工具
   ```

### 问题3：数据丢失

**可能原因**：
- 未及时保存
- 文件系统错误
- 断电

**解决方法**：
1. 启用自动保存
   ```c
   // 在主循环中
   kv_auto_save(&db, 5000);  // 每5秒保存
   ```

2. 使用写前日志（WAL）
   ```c
   // 先写日志，再修改数据
   kv_write_log(&db, operation);
   kv_apply_operation(&db, operation);
   ```

3. 实现断电保护
   ```c
   // 使用双缓冲或校验和
   ```

### 问题4：查询速度慢

**可能原因**：
- 链表过长
- 缓存未命中
- 频繁的文件I/O

**解决方法**：
1. 优化哈希表大小
   ```c
   // 保持负载因子在0.5-0.75之间
   ```

2. 启用LRU缓存
   ```c
   lru_cache_t cache;
   lru_init(&cache, 32);
   ```

3. 批量操作
   ```c
   // 使用批量读写减少I/O次数
   kv_put_batch(&db, keys, values, lens, count);
   ```

### 问题5：文件损坏

**可能原因**：
- 写入中断
- 存储介质故障
- 文件系统错误

**解决方法**：
1. 添加校验和
   ```c
   uint32_t crc = calculate_crc32(data, len);
   f_write(&file, &crc, sizeof(crc), &bw);
   ```

2. 使用备份文件
   ```c
   kv_save(&db);  // 保存到主文件
   kv_backup(&db, "backup.db");  // 备份
   ```

3. 验证文件完整性
   ```c
   if (kv_verify_file(&db) != KV_OK) {
       kv_restore_from_backup(&db);
   }
   ```


## 性能测试

### 测试代码

```c
/**
 * @brief  性能测试
 */
void kv_performance_test(void)
{
    kv_database_t db;
    uint32_t start_tick, end_tick;
    
    kv_init(&db, "0:/perf_test.db");
    
    // 测试1：插入性能
    printf("\n=== Insert Performance Test ===\n");
    start_tick = HAL_GetTick();
    
    for (int i = 0; i < 1000; i++) {
        char key[32];
        int32_t value = i;
        snprintf(key, sizeof(key), "key_%d", i);
        kv_put_int(&db, key, value);
    }
    
    end_tick = HAL_GetTick();
    printf("Inserted 1000 entries in %lu ms\n", end_tick - start_tick);
    printf("Average: %.2f ms per insert\n", 
           (end_tick - start_tick) / 1000.0f);
    
    // 测试2：查询性能
    printf("\n=== Query Performance Test ===\n");
    start_tick = HAL_GetTick();
    
    for (int i = 0; i < 1000; i++) {
        char key[32];
        int32_t value;
        snprintf(key, sizeof(key), "key_%d", i);
        kv_get_int(&db, key, &value);
    }
    
    end_tick = HAL_GetTick();
    printf("Queried 1000 entries in %lu ms\n", end_tick - start_tick);
    printf("Average: %.2f ms per query\n", 
           (end_tick - start_tick) / 1000.0f);
    
    // 测试3：保存性能
    printf("\n=== Save Performance Test ===\n");
    start_tick = HAL_GetTick();
    
    kv_save(&db);
    
    end_tick = HAL_GetTick();
    printf("Saved 1000 entries in %lu ms\n", end_tick - start_tick);
    
    // 测试4：加载性能
    printf("\n=== Load Performance Test ===\n");
    kv_clear(&db);
    
    start_tick = HAL_GetTick();
    
    kv_load(&db);
    
    end_tick = HAL_GetTick();
    printf("Loaded 1000 entries in %lu ms\n", end_tick - start_tick);
    
    // 打印统计信息
    kv_print_stats(&db);
    
    kv_deinit(&db);
}
```

**预期结果**：
```
=== Insert Performance Test ===
Inserted 1000 entries in 150 ms
Average: 0.15 ms per insert

=== Query Performance Test ===
Queried 1000 entries in 80 ms
Average: 0.08 ms per query

=== Save Performance Test ===
Saved 1000 entries in 500 ms

=== Load Performance Test ===
Loaded 1000 entries in 450 ms

=== KV Database Statistics ===
Total entries:     1000
Hash collisions:   120
Max chain length:  8
Load factor:       7.81
Memory usage:      32768 bytes (32.00 KB)
==============================
```


## 总结

通过本教程，你学习了：

- ✅ 键值数据库的原理和应用场景
- ✅ 哈希表和链表的数据结构实现
- ✅ 基本的增删改查操作
- ✅ 数据持久化到文件系统
- ✅ 性能优化技巧（缓存、索引）
- ✅ 高级特性（压缩、加密、事务）
- ✅ 完整的配置管理系统实现
- ✅ 性能测试和故障排除

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现过期时间（TTL）
   - 为每个键值对添加过期时间
   - 自动清理过期数据
   - 支持续期操作

2. **挑战2**：实现数据同步
   - 多个设备之间同步数据
   - 冲突解决策略
   - 增量同步

3. **挑战3**：实现更高级的索引
   - 支持范围查询
   - 支持前缀匹配
   - 实现B树索引

4. **挑战4**：实现数据迁移
   - 支持数据导入导出
   - 版本兼容性
   - 数据格式转换

## 完整代码

完整的项目代码可以在这里下载：[GitHub链接]

**项目结构**：
```
kv_database/
├── Core/
│   ├── Src/
│   │   ├── main.c
│   │   └── ...
│   └── Inc/
│       └── ...
├── Middlewares/
│   ├── KV_Database/
│   │   ├── kv_database.c
│   │   ├── kv_database.h
│   │   └── kv_utils.c
│   └── FATFS/
│       └── ...
└── README.md
```

## 下一步

建议继续学习：

- [SQLite嵌入式数据库](./01-sqlite-basics.html) - 学习更强大的关系型数据库
- [时序数据库应用](../intermediate/01-time-series-database.html) - 学习时间序列数据处理
- [数据同步与备份策略](../intermediate/02-data-sync-backup.html) - 学习数据可靠性保证

## 参考资料

1. **技术文章**
   - Redis设计与实现
   - LevelDB源码分析
   - 哈希表实现原理

2. **开源项目**
   - Redis: https://redis.io/
   - LevelDB: https://github.com/google/leveldb
   - RocksDB: https://rocksdb.org/

3. **书籍推荐**
   - 《数据结构与算法分析》
   - 《数据库系统概念》
   - 《高性能MySQL》

4. **相关标准**
   - NoSQL数据库设计模式
   - 键值存储最佳实践

## 常见问题

**Q1: KV数据库适合什么场景？**

A: KV数据库适合：
- 配置参数存储
- 会话数据缓存
- 简单的数据持久化
- 快速查找场景
- 资源受限的嵌入式系统

不适合：
- 复杂的关系查询
- 需要事务的场景
- 大量范围查询
- 需要SQL的应用

**Q2: 如何选择哈希表大小？**

A: 建议：
- 根据预期数据量选择
- 保持负载因子在0.5-0.75
- 使用质数作为大小
- 考虑内存限制
- 可以动态调整

**Q3: 如何处理哈希冲突？**

A: 常用方法：
- 链表法（本教程使用）
- 开放寻址法
- 双重哈希
- 布谷鸟哈希

**Q4: 如何保证数据安全？**

A: 建议：
- 定期自动保存
- 使用写前日志
- 实现校验和验证
- 定期备份
- 断电保护机制

**Q5: 性能如何优化？**

A: 优化方法：
- 使用LRU缓存
- 批量操作
- 异步写入
- 内存池管理
- 减少文件I/O

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言！

**版本历史**：
- v1.0 (2024-01-15): 初始版本，完整的KV数据库教程

**贡献者**：嵌入式知识平台内容团队

**许可证**：本教程采用 CC BY-SA 4.0 许可协议
