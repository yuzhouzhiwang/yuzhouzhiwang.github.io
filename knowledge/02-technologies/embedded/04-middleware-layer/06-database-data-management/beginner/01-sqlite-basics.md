---
title: "SQLite嵌入式数据库应用：轻量级数据存储解决方案"
description: "全面学习SQLite嵌入式数据库，掌握数据库操作、SQL语句、事务处理和应用开发，通过实战项目实现嵌入式数据管理系统"
slug: "sqlite-basics"

# 分类信息
domain: "中间件层"
module: "数据库与数据管理"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - SQLite
  - 嵌入式数据库
  - SQL
  - 数据存储
  - 数据管理
prerequisites:
  - "02-driver-bsp-layer/02-device-driver-development/beginner/03-spi-driver"
  - "04-middleware-layer/01-file-systems/beginner/01-fat-filesystem"
related_contents:
  - "04-middleware-layer/06-database-data-management/beginner/02-kv-database"
  - "04-middleware-layer/02-storage-technology/beginner/03-sd-card-storage"

# 学习信息
estimated_time: 75
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
  - SQLite数据库
  - 嵌入式数据库
  - SQL语句
  - 事务处理
  - 数据持久化
cover_image: ""
---

# SQLite嵌入式数据库应用：轻量级数据存储解决方案


## 学习目标

完成本教程后，你将能够：

- [ ] 理解SQLite的特点和应用场景
- [ ] 掌握SQLite在嵌入式系统中的移植和配置
- [ ] 熟练使用SQL语句进行数据操作
- [ ] 掌握数据库的创建、查询、更新和删除
- [ ] 理解事务处理和数据完整性
- [ ] 能够在嵌入式项目中集成SQLite
- [ ] 完成一个完整的数据记录系统
- [ ] 掌握SQLite的性能优化技巧

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言编程
- 了解文件系统的基本概念
- 理解数据结构（表、记录、字段）
- 掌握基本的SQL语法（可选）
- 了解指针和内存管理

**技能要求**：
- 能够编写嵌入式C代码
- 会使用文件系统API
- 熟悉基本的数据操作
- 能够使用调试工具
- 了解交叉编译

**开发环境**：
- STM32或ESP32开发板
- SD卡或SPI Flash存储
- Keil MDK或STM32CubeIDE
- 串口调试工具
- SQLite源码


## SQLite概述

### 什么是SQLite

SQLite是一个轻量级的嵌入式关系型数据库管理系统，被广泛应用于嵌入式设备、移动应用和桌面软件中。它将整个数据库存储在单个文件中，无需独立的服务器进程。

**核心特性**：

1. **零配置**
   - 无需安装和配置
   - 无需服务器进程
   - 单个库文件即可使用
   - 跨平台支持

2. **轻量级**
   - 库文件小于600KB
   - 内存占用低
   - 适合资源受限的嵌入式系统
   - 可配置功能裁剪

3. **完整的SQL支持**
   - 支持标准SQL语法
   - 支持事务（ACID）
   - 支持触发器和视图
   - 支持子查询和连接

4. **高可靠性**
   - 原子性提交和回滚
   - 断电保护
   - 数据完整性约束
   - 自动恢复机制

### SQLite架构

**系统架构图**：

```
┌─────────────────────────────────────────────────┐
│    应用层 (Application)                          │
│    SQL查询、数据操作                             │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    SQLite API层                                  │
│    sqlite3_open, sqlite3_exec, sqlite3_close... │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    SQL编译器                                     │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 词法分析器   │  │ 语法分析器   │          │
│    └──────────────┘  └──────────────┘          │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 代码生成器   │  │ 虚拟机       │          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    后端引擎                                      │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ B-Tree       │  │ Pager        │          │
│    └──────────────┘  └──────────────┘          │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ 事务管理     │  │ 锁管理       │          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    操作系统接口层 (VFS)                          │
│    文件I/O、内存分配、互斥锁                     │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    文件系统                                      │
│    FAT32, LittleFS, SPIFFS                      │
└─────────────────────────────────────────────────┘
```

### SQLite vs 其他数据库

| 特性 | SQLite | MySQL | PostgreSQL |
|------|--------|-------|------------|
| 类型 | 嵌入式 | 客户端/服务器 | 客户端/服务器 |
| 配置 | 零配置 | 需要配置 | 需要配置 |
| 资源占用 | 极低 | 中等 | 较高 |
| 并发性 | 读多写少 | 高并发 | 高并发 |
| 网络访问 | 不支持 | 支持 | 支持 |
| 适用场景 | 嵌入式、移动端 | Web应用 | 企业应用 |
| 数据库大小 | < 140TB | 无限制 | 无限制 |

**选择建议**：
- 嵌入式设备 → SQLite
- 单机应用 → SQLite
- Web应用 → MySQL/PostgreSQL
- 大数据量 → PostgreSQL


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4或ESP32 | STM32F407VG |
| SD卡 | 1 | 存储数据库文件 | 8GB Class 10 |
| SD卡模块 | 1 | SD卡接口 | SPI接口 |
| USB线 | 1 | 供电和调试 | - |
| 杜邦线 | 若干 | 连接模块 | - |

### 软件准备

**必需软件**：
- STM32CubeIDE 或 Arduino IDE（ESP32）
- SQLite源码：https://www.sqlite.org/download.html
- FATFS文件系统库
- 串口调试助手

**SQLite版本选择**：
- 推荐使用SQLite 3.x最新稳定版
- 嵌入式系统建议使用精简版（约300KB）
- 可以通过编译选项裁剪功能

### 电路连接

**SD卡模块连接示意图**：

```
STM32F407              SD Card Module
  PA5 (SCK)  ────────► SCK
  PA6 (MISO) ◄──────── MISO
  PA7 (MOSI) ────────► MOSI
  PA4 (CS)   ────────► CS
  3.3V       ────────► VCC
  GND        ────────► GND
```

**连接说明**：
- 确保SD卡模块供电为3.3V
- 使用SPI接口连接
- CS片选可以使用任意GPIO
- 建议添加上拉电阻（10KΩ）

## 步骤1：获取和配置SQLite源码

### 1.1 下载SQLite

访问SQLite官网下载amalgamation版本（单文件版本）：

```bash
# 下载SQLite amalgamation
wget https://www.sqlite.org/2024/sqlite-amalgamation-3440200.zip

# 解压
unzip sqlite-amalgamation-3440200.zip
```

**需要的文件**：
- `sqlite3.c` - SQLite核心实现（约250KB源码）
- `sqlite3.h` - API头文件
- `shell.c` - 命令行工具（可选）

### 1.2 配置SQLite编译选项

创建配置文件 `sqlite3_config.h`：

```c
#ifndef SQLITE3_CONFIG_H
#define SQLITE3_CONFIG_H

// 基本配置
#define SQLITE_OMIT_LOAD_EXTENSION     // 禁用扩展加载
#define SQLITE_OMIT_VIRTUALTABLE       // 禁用虚拟表
#define SQLITE_OMIT_DEPRECATED         // 禁用废弃API
#define SQLITE_OMIT_SHARED_CACHE       // 禁用共享缓存

// 内存配置
#define SQLITE_DEFAULT_CACHE_SIZE 100  // 默认缓存页数
#define SQLITE_DEFAULT_PAGE_SIZE 1024  // 页大小（字节）
#define SQLITE_MAX_PAGE_SIZE 4096      // 最大页大小

// 功能裁剪（可选，减小代码大小）
// #define SQLITE_OMIT_AUTOVACUUM       // 禁用自动清理
// #define SQLITE_OMIT_DATETIME_FUNCS   // 禁用日期时间函数
// #define SQLITE_OMIT_FLOATING_POINT   // 禁用浮点数
// #define SQLITE_OMIT_TRIGGER          // 禁用触发器
// #define SQLITE_OMIT_VIEW             // 禁用视图

// 线程安全（根据需要选择）
#define SQLITE_THREADSAFE 0            // 0=单线程, 1=多线程

// 临时文件配置
#define SQLITE_TEMP_STORE 3            // 3=仅使用内存

// 调试配置
#ifdef DEBUG
    #define SQLITE_DEBUG 1
    #define SQLITE_ENABLE_API_ARMOR    // API参数检查
#endif

#endif // SQLITE3_CONFIG_H
```

**配置说明**：
- `SQLITE_OMIT_*`: 裁剪不需要的功能，减小代码大小
- `SQLITE_DEFAULT_CACHE_SIZE`: 影响性能和内存占用
- `SQLITE_THREADSAFE`: 单线程模式可减小代码大小
- `SQLITE_TEMP_STORE`: 使用内存存储临时数据

### 1.3 添加到工程

**STM32CubeIDE步骤**：

1. 将SQLite源文件添加到工程
   - 右键项目 → New → Folder → 创建 `Middlewares/SQLite`
   - 复制 `sqlite3.c` 和 `sqlite3.h`
   - 复制 `sqlite3_config.h` 到工程

2. 配置包含路径
   - 右键项目 → Properties → C/C++ Build → Settings
   - MCU GCC Compiler → Include paths
   - 添加 `Middlewares/SQLite`

3. 配置编译选项
   - MCU GCC Compiler → Preprocessor
   - 添加宏定义：
     ```
     SQLITE_OS_OTHER=1
     SQLITE_THREADSAFE=0
     SQLITE_OMIT_LOAD_EXTENSION
     ```

4. 编译测试
   ```bash
   # 应该能够成功编译
   Build Project
   ```

**注意事项**：
- SQLite源码较大，编译时间较长
- 优化等级建议设置为 `-O2` 或 `-Os`
- 如果内存不足，可以裁剪更多功能


## 步骤2：实现VFS虚拟文件系统接口

SQLite需要我们实现VFS（Virtual File System）接口来访问底层文件系统。

### 2.1 定义VFS结构

创建文件 `sqlite3_vfs_fatfs.h`：

```c
#ifndef SQLITE3_VFS_FATFS_H
#define SQLITE3_VFS_FATFS_H

#include "sqlite3.h"
#include "ff.h"  // FATFS头文件

// VFS初始化函数
int sqlite3_vfs_fatfs_register(void);

// 文件系统初始化
int fatfs_init(void);

#endif // SQLITE3_VFS_FATFS_H
```

### 2.2 实现VFS接口

创建文件 `sqlite3_vfs_fatfs.c`：

```c
#include "sqlite3_vfs_fatfs.h"
#include "ff.h"
#include <string.h>
#include <stdio.h>

// 文件对象结构
typedef struct FatfsFile {
    sqlite3_file base;  // 基类
    FIL fil;            // FATFS文件对象
    char *path;         // 文件路径
} FatfsFile;

/**
 * @brief  关闭文件
 */
static int fatfsClose(sqlite3_file *pFile)
{
    FatfsFile *p = (FatfsFile*)pFile;
    
    if (p->fil.obj.fs) {
        f_close(&p->fil);
    }
    
    if (p->path) {
        sqlite3_free(p->path);
        p->path = NULL;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  读取文件
 */
static int fatfsRead(sqlite3_file *pFile, void *zBuf, int iAmt, sqlite3_int64 iOfst)
{
    FatfsFile *p = (FatfsFile*)pFile;
    FRESULT res;
    UINT br;
    
    // 定位到指定位置
    res = f_lseek(&p->fil, (FSIZE_t)iOfst);
    if (res != FR_OK) {
        return SQLITE_IOERR_READ;
    }
    
    // 读取数据
    res = f_read(&p->fil, zBuf, iAmt, &br);
    if (res != FR_OK) {
        return SQLITE_IOERR_READ;
    }
    
    // 检查是否读取完整
    if (br < (UINT)iAmt) {
        // 未读取完整，填充0
        memset(&((char*)zBuf)[br], 0, iAmt - br);
        return SQLITE_IOERR_SHORT_READ;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  写入文件
 */
static int fatfsWrite(sqlite3_file *pFile, const void *zBuf, int iAmt, sqlite3_int64 iOfst)
{
    FatfsFile *p = (FatfsFile*)pFile;
    FRESULT res;
    UINT bw;
    
    // 定位到指定位置
    res = f_lseek(&p->fil, (FSIZE_t)iOfst);
    if (res != FR_OK) {
        return SQLITE_IOERR_WRITE;
    }
    
    // 写入数据
    res = f_write(&p->fil, zBuf, iAmt, &bw);
    if (res != FR_OK) {
        return SQLITE_IOERR_WRITE;
    }
    
    // 检查是否写入完整
    if (bw < (UINT)iAmt) {
        return SQLITE_FULL;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  截断文件
 */
static int fatfsTruncate(sqlite3_file *pFile, sqlite3_int64 size)
{
    FatfsFile *p = (FatfsFile*)pFile;
    FRESULT res;
    
    // 定位到指定大小
    res = f_lseek(&p->fil, (FSIZE_t)size);
    if (res != FR_OK) {
        return SQLITE_IOERR_TRUNCATE;
    }
    
    // 截断文件
    res = f_truncate(&p->fil);
    if (res != FR_OK) {
        return SQLITE_IOERR_TRUNCATE;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  同步文件
 */
static int fatfsSync(sqlite3_file *pFile, int flags)
{
    FatfsFile *p = (FatfsFile*)pFile;
    FRESULT res;
    
    // 同步文件数据
    res = f_sync(&p->fil);
    if (res != FR_OK) {
        return SQLITE_IOERR_FSYNC;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  获取文件大小
 */
static int fatfsFileSize(sqlite3_file *pFile, sqlite3_int64 *pSize)
{
    FatfsFile *p = (FatfsFile*)pFile;
    
    *pSize = (sqlite3_int64)f_size(&p->fil);
    
    return SQLITE_OK;
}

/**
 * @brief  文件锁定（简化实现）
 */
static int fatfsLock(sqlite3_file *pFile, int eLock)
{
    // 单线程环境，简化实现
    return SQLITE_OK;
}

/**
 * @brief  文件解锁（简化实现）
 */
static int fatfsUnlock(sqlite3_file *pFile, int eLock)
{
    // 单线程环境，简化实现
    return SQLITE_OK;
}

/**
 * @brief  检查锁状态（简化实现）
 */
static int fatfsCheckReservedLock(sqlite3_file *pFile, int *pResOut)
{
    *pResOut = 0;
    return SQLITE_OK;
}

/**
 * @brief  文件控制
 */
static int fatfsFileControl(sqlite3_file *pFile, int op, void *pArg)
{
    return SQLITE_NOTFOUND;
}

/**
 * @brief  获取扇区大小
 */
static int fatfsSectorSize(sqlite3_file *pFile)
{
    return 512;  // SD卡扇区大小
}

/**
 * @brief  获取设备特性
 */
static int fatfsDeviceCharacteristics(sqlite3_file *pFile)
{
    return 0;
}

// 文件方法表
static const sqlite3_io_methods fatfs_io_methods = {
    1,                              // iVersion
    fatfsClose,                     // xClose
    fatfsRead,                      // xRead
    fatfsWrite,                     // xWrite
    fatfsTruncate,                  // xTruncate
    fatfsSync,                      // xSync
    fatfsFileSize,                  // xFileSize
    fatfsLock,                      // xLock
    fatfsUnlock,                    // xUnlock
    fatfsCheckReservedLock,         // xCheckReservedLock
    fatfsFileControl,               // xFileControl
    fatfsSectorSize,                // xSectorSize
    fatfsDeviceCharacteristics,     // xDeviceCharacteristics
};
```

### 2.3 实现VFS方法

继续在 `sqlite3_vfs_fatfs.c` 中添加：

```c
/**
 * @brief  打开文件
 */
static int fatfsOpen(sqlite3_vfs *pVfs, const char *zName, sqlite3_file *pFile,
                    int flags, int *pOutFlags)
{
    FatfsFile *p = (FatfsFile*)pFile;
    FRESULT res;
    BYTE mode = 0;
    
    // 清零文件对象
    memset(p, 0, sizeof(FatfsFile));
    
    // 设置方法表
    p->base.pMethods = &fatfs_io_methods;
    
    // 保存文件路径
    if (zName) {
        p->path = sqlite3_mprintf("%s", zName);
        if (!p->path) {
            return SQLITE_NOMEM;
        }
    }
    
    // 确定打开模式
    if (flags & SQLITE_OPEN_READONLY) {
        mode = FA_READ;
    } else if (flags & SQLITE_OPEN_READWRITE) {
        mode = FA_READ | FA_WRITE;
    } else if (flags & SQLITE_OPEN_CREATE) {
        mode = FA_READ | FA_WRITE | FA_CREATE_ALWAYS;
    }
    
    // 打开文件
    res = f_open(&p->fil, zName, mode);
    if (res != FR_OK) {
        if (p->path) {
            sqlite3_free(p->path);
            p->path = NULL;
        }
        return SQLITE_CANTOPEN;
    }
    
    if (pOutFlags) {
        *pOutFlags = flags;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  删除文件
 */
static int fatfsDelete(sqlite3_vfs *pVfs, const char *zPath, int syncDir)
{
    FRESULT res;
    
    res = f_unlink(zPath);
    if (res != FR_OK && res != FR_NO_FILE) {
        return SQLITE_IOERR_DELETE;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  检查文件访问权限
 */
static int fatfsAccess(sqlite3_vfs *pVfs, const char *zPath, int flags, int *pResOut)
{
    FILINFO fno;
    FRESULT res;
    
    res = f_stat(zPath, &fno);
    
    if (flags == SQLITE_ACCESS_EXISTS) {
        *pResOut = (res == FR_OK);
    } else if (flags == SQLITE_ACCESS_READWRITE) {
        *pResOut = (res == FR_OK && !(fno.fattrib & AM_RDO));
    } else {
        *pResOut = 0;
    }
    
    return SQLITE_OK;
}

/**
 * @brief  获取完整路径
 */
static int fatfsFullPathname(sqlite3_vfs *pVfs, const char *zPath,
                            int nOut, char *zOut)
{
    sqlite3_snprintf(nOut, zOut, "%s", zPath);
    return SQLITE_OK;
}

/**
 * @brief  获取随机数
 */
static int fatfsRandomness(sqlite3_vfs *pVfs, int nByte, char *zOut)
{
    // 简单的随机数生成
    for (int i = 0; i < nByte; i++) {
        zOut[i] = (char)(rand() & 0xFF);
    }
    return nByte;
}

/**
 * @brief  休眠
 */
static int fatfsSleep(sqlite3_vfs *pVfs, int microseconds)
{
    // 使用HAL延时
    HAL_Delay(microseconds / 1000);
    return microseconds;
}

/**
 * @brief  获取当前时间
 */
static int fatfsCurrentTime(sqlite3_vfs *pVfs, double *prNow)
{
    // 简化实现：返回固定时间
    // 实际应用中应该使用RTC
    *prNow = 2440587.5;  // 1970-01-01 00:00:00
    return SQLITE_OK;
}

// VFS对象
static sqlite3_vfs fatfs_vfs = {
    1,                      // iVersion
    sizeof(FatfsFile),      // szOsFile
    260,                    // mxPathname
    0,                      // pNext
    "fatfs",                // zName
    0,                      // pAppData
    fatfsOpen,              // xOpen
    fatfsDelete,            // xDelete
    fatfsAccess,            // xAccess
    fatfsFullPathname,      // xFullPathname
    NULL,                   // xDlOpen
    NULL,                   // xDlError
    NULL,                   // xDlSym
    NULL,                   // xDlClose
    fatfsRandomness,        // xRandomness
    fatfsSleep,             // xSleep
    fatfsCurrentTime,       // xCurrentTime
    NULL,                   // xGetLastError
};

/**
 * @brief  注册VFS
 */
int sqlite3_vfs_fatfs_register(void)
{
    return sqlite3_vfs_register(&fatfs_vfs, 1);
}

/**
 * @brief  初始化文件系统
 */
int fatfs_init(void)
{
    FRESULT res;
    static FATFS fs;
    
    // 挂载文件系统
    res = f_mount(&fs, "0:", 1);
    if (res != FR_OK) {
        printf("Failed to mount filesystem: %d\n", res);
        return -1;
    }
    
    printf("Filesystem mounted successfully\n");
    return 0;
}
```

**代码说明**：
- `fatfsOpen`: 打开文件，支持创建、只读、读写模式
- `fatfsRead/Write`: 读写文件数据
- `fatfsSync`: 同步数据到存储设备
- `fatfsDelete`: 删除文件
- `fatfsAccess`: 检查文件是否存在


## 步骤3：初始化和打开数据库

### 3.1 初始化SQLite

创建文件 `sqlite3_app.c`：

```c
#include "sqlite3.h"
#include "sqlite3_vfs_fatfs.h"
#include <stdio.h>
#include <string.h>

// 数据库对象
static sqlite3 *db = NULL;

/**
 * @brief  初始化SQLite
 * @retval 0:成功, 负数:错误
 */
int sqlite3_app_init(void)
{
    int rc;
    
    // 初始化文件系统
    if (fatfs_init() != 0) {
        printf("Failed to initialize filesystem\n");
        return -1;
    }
    
    // 注册VFS
    rc = sqlite3_vfs_fatfs_register();
    if (rc != SQLITE_OK) {
        printf("Failed to register VFS: %d\n", rc);
        return -1;
    }
    
    printf("SQLite initialized successfully\n");
    return 0;
}

/**
 * @brief  打开数据库
 * @param  filename: 数据库文件名
 * @retval 0:成功, 负数:错误
 */
int sqlite3_app_open(const char *filename)
{
    int rc;
    
    // 打开数据库
    rc = sqlite3_open(filename, &db);
    if (rc != SQLITE_OK) {
        printf("Failed to open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        db = NULL;
        return -1;
    }
    
    printf("Database opened: %s\n", filename);
    return 0;
}

/**
 * @brief  关闭数据库
 * @retval 0:成功, 负数:错误
 */
int sqlite3_app_close(void)
{
    if (db) {
        sqlite3_close(db);
        db = NULL;
        printf("Database closed\n");
    }
    return 0;
}

/**
 * @brief  获取数据库对象
 */
sqlite3* sqlite3_app_get_db(void)
{
    return db;
}
```

### 3.2 在main函数中初始化

```c
#include "sqlite3_app.h"

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
    
    printf("SQLite Demo Starting...\n");
    
    // 初始化SQLite
    if (sqlite3_app_init() != 0) {
        printf("Failed to initialize SQLite\n");
        Error_Handler();
    }
    
    // 打开数据库
    if (sqlite3_app_open("0:/test.db") != 0) {
        printf("Failed to open database\n");
        Error_Handler();
    }
    
    // 应用程序代码
    // ...
    
    // 关闭数据库
    sqlite3_app_close();
    
    while (1) {
        // 主循环
    }
}
```

**预期输出**：
```
SQLite Demo Starting...
Filesystem mounted successfully
SQLite initialized successfully
Database opened: 0:/test.db
```

## 步骤4：创建表和插入数据

### 4.1 创建表

```c
/**
 * @brief  创建传感器数据表
 */
int create_sensor_table(void)
{
    char *err_msg = NULL;
    int rc;
    
    // SQL创建表语句
    const char *sql = 
        "CREATE TABLE IF NOT EXISTS sensor_data ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "timestamp INTEGER NOT NULL,"
        "temperature REAL NOT NULL,"
        "humidity REAL NOT NULL,"
        "pressure REAL"
        ");";
    
    // 执行SQL语句
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to create table: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Table created successfully\n");
    return 0;
}
```

**SQL语句说明**：
- `CREATE TABLE IF NOT EXISTS`: 如果表不存在则创建
- `INTEGER PRIMARY KEY AUTOINCREMENT`: 自增主键
- `NOT NULL`: 字段不能为空
- `REAL`: 浮点数类型

### 4.2 插入数据

```c
/**
 * @brief  插入传感器数据
 */
int insert_sensor_data(uint32_t timestamp, float temperature, 
                      float humidity, float pressure)
{
    char *err_msg = NULL;
    int rc;
    char sql[256];
    
    // 构造SQL插入语句
    snprintf(sql, sizeof(sql),
            "INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) "
            "VALUES (%lu, %.2f, %.2f, %.2f);",
            timestamp, temperature, humidity, pressure);
    
    // 执行SQL语句
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to insert data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Data inserted: T=%.2f, H=%.2f, P=%.2f\n", 
           temperature, humidity, pressure);
    return 0;
}
```

### 4.3 使用预编译语句（推荐）

```c
/**
 * @brief  使用预编译语句插入数据（更高效、更安全）
 */
int insert_sensor_data_prepared(uint32_t timestamp, float temperature,
                               float humidity, float pressure)
{
    sqlite3_stmt *stmt;
    int rc;
    
    // 准备SQL语句
    const char *sql = 
        "INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) "
        "VALUES (?, ?, ?, ?);";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        printf("Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    // 绑定参数
    sqlite3_bind_int(stmt, 1, timestamp);
    sqlite3_bind_double(stmt, 2, temperature);
    sqlite3_bind_double(stmt, 3, humidity);
    sqlite3_bind_double(stmt, 4, pressure);
    
    // 执行语句
    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        printf("Failed to execute statement: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -1;
    }
    
    // 释放语句
    sqlite3_finalize(stmt);
    
    printf("Data inserted (prepared): T=%.2f, H=%.2f\n", temperature, humidity);
    return 0;
}
```

**预编译语句优势**：
- 防止SQL注入攻击
- 性能更好（可重复使用）
- 类型安全
- 代码更清晰

### 4.4 批量插入数据

```c
/**
 * @brief  批量插入数据（使用事务）
 */
int insert_batch_data(void)
{
    char *err_msg = NULL;
    int rc;
    
    // 开始事务
    rc = sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to begin transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 批量插入100条数据
    for (int i = 0; i < 100; i++) {
        uint32_t timestamp = HAL_GetTick();
        float temperature = 20.0f + (rand() % 100) / 10.0f;
        float humidity = 40.0f + (rand() % 400) / 10.0f;
        float pressure = 1000.0f + (rand() % 200) / 10.0f;
        
        rc = insert_sensor_data_prepared(timestamp, temperature, 
                                        humidity, pressure);
        if (rc != 0) {
            // 回滚事务
            sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
            return -1;
        }
    }
    
    // 提交事务
    rc = sqlite3_exec(db, "COMMIT;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to commit transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
        return -1;
    }
    
    printf("Batch insert completed: 100 records\n");
    return 0;
}
```

**事务的重要性**：
- 大幅提升批量插入性能（100倍以上）
- 保证数据一致性
- 支持回滚操作
- 减少磁盘I/O次数


## 步骤5：查询数据

### 5.1 简单查询

```c
/**
 * @brief  查询回调函数
 */
static int query_callback(void *data, int argc, char **argv, char **col_name)
{
    // argc: 列数
    // argv: 列值数组
    // col_name: 列名数组
    
    for (int i = 0; i < argc; i++) {
        printf("%s = %s\n", col_name[i], argv[i] ? argv[i] : "NULL");
    }
    printf("\n");
    
    return 0;
}

/**
 * @brief  查询所有数据
 */
int query_all_data(void)
{
    char *err_msg = NULL;
    int rc;
    
    const char *sql = "SELECT * FROM sensor_data;";
    
    printf("Querying all data:\n");
    printf("----------------------------------------\n");
    
    rc = sqlite3_exec(db, sql, query_callback, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to query data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    return 0;
}
```

### 5.2 条件查询

```c
/**
 * @brief  查询温度大于25度的数据
 */
int query_high_temperature(void)
{
    char *err_msg = NULL;
    int rc;
    
    const char *sql = 
        "SELECT id, timestamp, temperature, humidity "
        "FROM sensor_data "
        "WHERE temperature > 25.0 "
        "ORDER BY timestamp DESC "
        "LIMIT 10;";
    
    printf("High temperature records:\n");
    printf("----------------------------------------\n");
    
    rc = sqlite3_exec(db, sql, query_callback, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to query data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    return 0;
}
```

### 5.3 使用预编译语句查询

```c
/**
 * @brief  使用预编译语句查询数据
 */
int query_data_prepared(float min_temp, float max_temp)
{
    sqlite3_stmt *stmt;
    int rc;
    
    // 准备SQL语句
    const char *sql = 
        "SELECT id, timestamp, temperature, humidity, pressure "
        "FROM sensor_data "
        "WHERE temperature BETWEEN ? AND ? "
        "ORDER BY timestamp DESC;";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        printf("Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    // 绑定参数
    sqlite3_bind_double(stmt, 1, min_temp);
    sqlite3_bind_double(stmt, 2, max_temp);
    
    printf("Temperature range: %.2f - %.2f\n", min_temp, max_temp);
    printf("%-5s %-12s %-8s %-8s %-8s\n", 
           "ID", "Timestamp", "Temp", "Humid", "Press");
    printf("------------------------------------------------\n");
    
    // 遍历结果
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        int timestamp = sqlite3_column_int(stmt, 1);
        double temperature = sqlite3_column_double(stmt, 2);
        double humidity = sqlite3_column_double(stmt, 3);
        double pressure = sqlite3_column_double(stmt, 4);
        
        printf("%-5d %-12d %-8.2f %-8.2f %-8.2f\n",
               id, timestamp, temperature, humidity, pressure);
    }
    
    if (rc != SQLITE_DONE) {
        printf("Query error: %s\n", sqlite3_errmsg(db));
    }
    
    // 释放语句
    sqlite3_finalize(stmt);
    
    return 0;
}
```

### 5.4 聚合查询

```c
/**
 * @brief  统计查询
 */
int query_statistics(void)
{
    sqlite3_stmt *stmt;
    int rc;
    
    // 准备SQL语句
    const char *sql = 
        "SELECT "
        "COUNT(*) as count, "
        "AVG(temperature) as avg_temp, "
        "MIN(temperature) as min_temp, "
        "MAX(temperature) as max_temp, "
        "AVG(humidity) as avg_humid "
        "FROM sensor_data;";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        printf("Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    // 获取结果
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        int count = sqlite3_column_int(stmt, 0);
        double avg_temp = sqlite3_column_double(stmt, 1);
        double min_temp = sqlite3_column_double(stmt, 2);
        double max_temp = sqlite3_column_double(stmt, 3);
        double avg_humid = sqlite3_column_double(stmt, 4);
        
        printf("Statistics:\n");
        printf("  Total records: %d\n", count);
        printf("  Avg temperature: %.2f°C\n", avg_temp);
        printf("  Min temperature: %.2f°C\n", min_temp);
        printf("  Max temperature: %.2f°C\n", max_temp);
        printf("  Avg humidity: %.2f%%\n", avg_humid);
    }
    
    sqlite3_finalize(stmt);
    return 0;
}
```

## 步骤6：更新和删除数据

### 6.1 更新数据

```c
/**
 * @brief  更新数据
 */
int update_sensor_data(int id, float new_temperature)
{
    char *err_msg = NULL;
    int rc;
    char sql[256];
    
    // 构造UPDATE语句
    snprintf(sql, sizeof(sql),
            "UPDATE sensor_data SET temperature = %.2f WHERE id = %d;",
            new_temperature, id);
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to update data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 获取影响的行数
    int changes = sqlite3_changes(db);
    printf("Updated %d record(s)\n", changes);
    
    return 0;
}

/**
 * @brief  批量更新数据
 */
int update_batch_data(void)
{
    char *err_msg = NULL;
    int rc;
    
    // 开始事务
    rc = sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to begin transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 更新所有温度大于30度的记录
    const char *sql = 
        "UPDATE sensor_data "
        "SET temperature = temperature * 0.9 "
        "WHERE temperature > 30.0;";
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to update data: %s\n", err_msg);
        sqlite3_free(err_msg);
        sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
        return -1;
    }
    
    // 提交事务
    rc = sqlite3_exec(db, "COMMIT;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to commit transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    int changes = sqlite3_changes(db);
    printf("Batch update completed: %d records\n", changes);
    
    return 0;
}
```

### 6.2 删除数据

```c
/**
 * @brief  删除指定ID的数据
 */
int delete_sensor_data(int id)
{
    char *err_msg = NULL;
    int rc;
    char sql[128];
    
    snprintf(sql, sizeof(sql), "DELETE FROM sensor_data WHERE id = %d;", id);
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to delete data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    int changes = sqlite3_changes(db);
    printf("Deleted %d record(s)\n", changes);
    
    return 0;
}

/**
 * @brief  删除旧数据（保留最新1000条）
 */
int delete_old_data(void)
{
    char *err_msg = NULL;
    int rc;
    
    const char *sql = 
        "DELETE FROM sensor_data "
        "WHERE id NOT IN ("
        "  SELECT id FROM sensor_data "
        "  ORDER BY timestamp DESC "
        "  LIMIT 1000"
        ");";
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to delete old data: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    int changes = sqlite3_changes(db);
    printf("Deleted %d old record(s)\n", changes);
    
    return 0;
}

/**
 * @brief  清空表
 */
int truncate_table(void)
{
    char *err_msg = NULL;
    int rc;
    
    const char *sql = "DELETE FROM sensor_data;";
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to truncate table: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 重置自增ID
    rc = sqlite3_exec(db, "DELETE FROM sqlite_sequence WHERE name='sensor_data';",
                     NULL, NULL, &err_msg);
    
    printf("Table truncated\n");
    return 0;
}
```

## 步骤7：事务处理

### 7.1 事务基础

```c
/**
 * @brief  事务示例
 */
int transaction_example(void)
{
    char *err_msg = NULL;
    int rc;
    
    printf("Starting transaction...\n");
    
    // 开始事务
    rc = sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to begin transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 执行多个操作
    for (int i = 0; i < 10; i++) {
        uint32_t timestamp = HAL_GetTick();
        float temperature = 20.0f + i;
        float humidity = 50.0f + i;
        float pressure = 1013.0f;
        
        rc = insert_sensor_data_prepared(timestamp, temperature, 
                                        humidity, pressure);
        if (rc != 0) {
            printf("Insert failed, rolling back...\n");
            sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
            return -1;
        }
    }
    
    // 提交事务
    rc = sqlite3_exec(db, "COMMIT;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to commit: %s\n", err_msg);
        sqlite3_free(err_msg);
        sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
        return -1;
    }
    
    printf("Transaction committed successfully\n");
    return 0;
}
```

### 7.2 事务隔离级别

```c
/**
 * @brief  设置事务模式
 */
int set_transaction_mode(const char *mode)
{
    char *err_msg = NULL;
    int rc;
    char sql[128];
    
    // SQLite支持三种事务模式：
    // DEFERRED (默认): 延迟锁定
    // IMMEDIATE: 立即获取写锁
    // EXCLUSIVE: 独占锁
    
    snprintf(sql, sizeof(sql), "BEGIN %s TRANSACTION;", mode);
    
    rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to begin transaction: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Transaction started in %s mode\n", mode);
    return 0;
}
```

### 7.3 保存点（Savepoint）

```c
/**
 * @brief  使用保存点
 */
int savepoint_example(void)
{
    char *err_msg = NULL;
    int rc;
    
    // 开始事务
    sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL);
    
    // 插入一些数据
    insert_sensor_data_prepared(HAL_GetTick(), 25.0f, 60.0f, 1013.0f);
    
    // 创建保存点
    rc = sqlite3_exec(db, "SAVEPOINT sp1;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to create savepoint: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 插入更多数据
    insert_sensor_data_prepared(HAL_GetTick(), 26.0f, 61.0f, 1014.0f);
    
    // 回滚到保存点（撤销第二次插入）
    rc = sqlite3_exec(db, "ROLLBACK TO sp1;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to rollback to savepoint: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 提交事务（只有第一次插入会被保存）
    sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    
    printf("Savepoint example completed\n");
    return 0;
}
```


## 步骤8：性能优化

### 8.1 创建索引

```c
/**
 * @brief  创建索引提升查询性能
 */
int create_indexes(void)
{
    char *err_msg = NULL;
    int rc;
    
    // 在timestamp列上创建索引
    const char *sql1 = 
        "CREATE INDEX IF NOT EXISTS idx_timestamp "
        "ON sensor_data(timestamp);";
    
    rc = sqlite3_exec(db, sql1, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to create index: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 在temperature列上创建索引
    const char *sql2 = 
        "CREATE INDEX IF NOT EXISTS idx_temperature "
        "ON sensor_data(temperature);";
    
    rc = sqlite3_exec(db, sql2, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to create index: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Indexes created successfully\n");
    return 0;
}
```

### 8.2 优化配置

```c
/**
 * @brief  优化SQLite配置
 */
int optimize_sqlite_config(void)
{
    char *err_msg = NULL;
    int rc;
    
    // 设置同步模式（NORMAL比FULL快，但稍微不安全）
    rc = sqlite3_exec(db, "PRAGMA synchronous = NORMAL;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to set synchronous: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 设置日志模式（WAL模式性能更好）
    rc = sqlite3_exec(db, "PRAGMA journal_mode = WAL;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to set journal mode: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 设置缓存大小（页数）
    rc = sqlite3_exec(db, "PRAGMA cache_size = 200;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to set cache size: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    // 设置临时存储位置（使用内存）
    rc = sqlite3_exec(db, "PRAGMA temp_store = MEMORY;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to set temp store: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("SQLite configuration optimized\n");
    return 0;
}
```

**PRAGMA说明**：
- `synchronous = NORMAL`: 平衡性能和安全性
- `journal_mode = WAL`: 写前日志，提升并发性能
- `cache_size`: 缓存页数，影响内存占用和性能
- `temp_store = MEMORY`: 临时数据存储在内存中

### 8.3 批量操作优化

```c
/**
 * @brief  性能测试：对比单条插入和批量插入
 */
void performance_test(void)
{
    uint32_t start_tick, end_tick;
    
    // 测试1：单条插入（无事务）
    printf("Test 1: Single insert without transaction\n");
    start_tick = HAL_GetTick();
    
    for (int i = 0; i < 100; i++) {
        insert_sensor_data_prepared(HAL_GetTick(), 
                                   20.0f + i * 0.1f, 
                                   50.0f + i * 0.1f, 
                                   1013.0f);
    }
    
    end_tick = HAL_GetTick();
    printf("Time: %lu ms\n\n", end_tick - start_tick);
    
    // 清空表
    truncate_table();
    
    // 测试2：批量插入（使用事务）
    printf("Test 2: Batch insert with transaction\n");
    start_tick = HAL_GetTick();
    
    sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL);
    
    for (int i = 0; i < 100; i++) {
        insert_sensor_data_prepared(HAL_GetTick(), 
                                   20.0f + i * 0.1f, 
                                   50.0f + i * 0.1f, 
                                   1013.0f);
    }
    
    sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    
    end_tick = HAL_GetTick();
    printf("Time: %lu ms\n\n", end_tick - start_tick);
    
    printf("Performance improvement: ~%lux faster\n", 
           (end_tick - start_tick) > 0 ? 
           ((end_tick - start_tick) / (end_tick - start_tick)) : 1);
}
```

### 8.4 查询优化

```c
/**
 * @brief  使用EXPLAIN分析查询
 */
int analyze_query(const char *sql)
{
    sqlite3_stmt *stmt;
    int rc;
    char explain_sql[512];
    
    // 添加EXPLAIN QUERY PLAN前缀
    snprintf(explain_sql, sizeof(explain_sql), "EXPLAIN QUERY PLAN %s", sql);
    
    rc = sqlite3_prepare_v2(db, explain_sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        printf("Failed to prepare explain: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    printf("Query Plan:\n");
    printf("----------------------------------------\n");
    
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *detail = (const char*)sqlite3_column_text(stmt, 3);
        printf("%s\n", detail);
    }
    
    sqlite3_finalize(stmt);
    return 0;
}
```

## 步骤9：数据库维护

### 9.1 数据库备份

```c
/**
 * @brief  备份数据库
 */
int backup_database(const char *backup_filename)
{
    sqlite3 *backup_db;
    sqlite3_backup *backup;
    int rc;
    
    // 打开备份数据库
    rc = sqlite3_open(backup_filename, &backup_db);
    if (rc != SQLITE_OK) {
        printf("Failed to open backup database: %s\n", sqlite3_errmsg(backup_db));
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 初始化备份
    backup = sqlite3_backup_init(backup_db, "main", db, "main");
    if (!backup) {
        printf("Failed to initialize backup: %s\n", sqlite3_errmsg(backup_db));
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 执行备份
    rc = sqlite3_backup_step(backup, -1);
    if (rc != SQLITE_DONE) {
        printf("Backup failed: %s\n", sqlite3_errmsg(backup_db));
        sqlite3_backup_finish(backup);
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 完成备份
    sqlite3_backup_finish(backup);
    sqlite3_close(backup_db);
    
    printf("Database backed up to: %s\n", backup_filename);
    return 0;
}
```

### 9.2 数据库恢复

```c
/**
 * @brief  从备份恢复数据库
 */
int restore_database(const char *backup_filename)
{
    sqlite3 *backup_db;
    sqlite3_backup *backup;
    int rc;
    
    // 打开备份数据库
    rc = sqlite3_open(backup_filename, &backup_db);
    if (rc != SQLITE_OK) {
        printf("Failed to open backup database: %s\n", sqlite3_errmsg(backup_db));
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 初始化恢复
    backup = sqlite3_backup_init(db, "main", backup_db, "main");
    if (!backup) {
        printf("Failed to initialize restore: %s\n", sqlite3_errmsg(db));
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 执行恢复
    rc = sqlite3_backup_step(backup, -1);
    if (rc != SQLITE_DONE) {
        printf("Restore failed: %s\n", sqlite3_errmsg(db));
        sqlite3_backup_finish(backup);
        sqlite3_close(backup_db);
        return -1;
    }
    
    // 完成恢复
    sqlite3_backup_finish(backup);
    sqlite3_close(backup_db);
    
    printf("Database restored from: %s\n", backup_filename);
    return 0;
}
```

### 9.3 数据库完整性检查

```c
/**
 * @brief  检查数据库完整性
 */
int check_database_integrity(void)
{
    sqlite3_stmt *stmt;
    int rc;
    
    const char *sql = "PRAGMA integrity_check;";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        printf("Failed to prepare integrity check: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    printf("Database Integrity Check:\n");
    printf("----------------------------------------\n");
    
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *result = (const char*)sqlite3_column_text(stmt, 0);
        printf("%s\n", result);
    }
    
    sqlite3_finalize(stmt);
    return 0;
}

/**
 * @brief  优化数据库（VACUUM）
 */
int vacuum_database(void)
{
    char *err_msg = NULL;
    int rc;
    
    printf("Vacuuming database...\n");
    
    // VACUUM会重建数据库文件，回收未使用的空间
    rc = sqlite3_exec(db, "VACUUM;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to vacuum database: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Database vacuumed successfully\n");
    return 0;
}

/**
 * @brief  分析数据库统计信息
 */
int analyze_database(void)
{
    char *err_msg = NULL;
    int rc;
    
    // ANALYZE收集统计信息，帮助查询优化器
    rc = sqlite3_exec(db, "ANALYZE;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        printf("Failed to analyze database: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    
    printf("Database analyzed successfully\n");
    return 0;
}
```

## 步骤10：完整应用示例

### 10.1 传感器数据记录系统

```c
/**
 * @brief  传感器数据记录系统主程序
 */
void sensor_data_logger_main(void)
{
    int rc;
    
    // 初始化SQLite
    if (sqlite3_app_init() != 0) {
        printf("Failed to initialize SQLite\n");
        return;
    }
    
    // 打开数据库
    if (sqlite3_app_open("0:/sensor.db") != 0) {
        printf("Failed to open database\n");
        return;
    }
    
    // 优化配置
    optimize_sqlite_config();
    
    // 创建表
    create_sensor_table();
    
    // 创建索引
    create_indexes();
    
    // 主循环
    uint32_t last_record_time = 0;
    uint32_t last_backup_time = 0;
    
    while (1) {
        uint32_t current_time = HAL_GetTick();
        
        // 每10秒记录一次数据
        if (current_time - last_record_time >= 10000) {
            // 读取传感器数据（示例）
            float temperature = read_temperature();
            float humidity = read_humidity();
            float pressure = read_pressure();
            
            // 插入数据库
            rc = insert_sensor_data_prepared(current_time, temperature, 
                                            humidity, pressure);
            if (rc == 0) {
                printf("Data recorded: T=%.2f, H=%.2f, P=%.2f\n",
                       temperature, humidity, pressure);
            }
            
            last_record_time = current_time;
        }
        
        // 每小时备份一次
        if (current_time - last_backup_time >= 3600000) {
            backup_database("0:/sensor_backup.db");
            last_backup_time = current_time;
        }
        
        // 每天清理旧数据（保留最新10000条）
        static uint32_t last_cleanup_day = 0;
        uint32_t current_day = current_time / 86400000;
        if (current_day != last_cleanup_day) {
            delete_old_data();
            vacuum_database();
            last_cleanup_day = current_day;
        }
        
        // 延时
        HAL_Delay(100);
    }
}
```

### 10.2 命令行接口

```c
/**
 * @brief  简单的命令行接口
 */
void command_line_interface(void)
{
    char cmd[128];
    
    printf("\nSQLite Command Line Interface\n");
    printf("Commands:\n");
    printf("  insert - Insert sample data\n");
    printf("  query  - Query all data\n");
    printf("  stats  - Show statistics\n");
    printf("  backup - Backup database\n");
    printf("  exit   - Exit\n");
    printf("\n");
    
    while (1) {
        printf("> ");
        
        // 读取命令（简化实现）
        scanf("%s", cmd);
        
        if (strcmp(cmd, "insert") == 0) {
            insert_sensor_data_prepared(HAL_GetTick(), 
                                       25.0f, 60.0f, 1013.0f);
            printf("Data inserted\n");
        }
        else if (strcmp(cmd, "query") == 0) {
            query_all_data();
        }
        else if (strcmp(cmd, "stats") == 0) {
            query_statistics();
        }
        else if (strcmp(cmd, "backup") == 0) {
            backup_database("0:/backup.db");
        }
        else if (strcmp(cmd, "exit") == 0) {
            break;
        }
        else {
            printf("Unknown command\n");
        }
    }
}
```


## 故障排除

### 问题1：数据库无法打开

**可能原因**：
- 文件系统未正确挂载
- 文件路径错误
- 权限不足
- 存储空间不足

**解决方法**：
1. 检查文件系统是否挂载成功
   ```c
   FRESULT res = f_mount(&fs, "0:", 1);
   if (res != FR_OK) {
       printf("Mount failed: %d\n", res);
   }
   ```

2. 验证文件路径
   ```c
   // 确保路径格式正确
   // 正确: "0:/test.db"
   // 错误: "/test.db" 或 "test.db"
   ```

3. 检查存储空间
   ```c
   FATFS *fs;
   DWORD fre_clust;
   f_getfree("0:", &fre_clust, &fs);
   printf("Free space: %lu KB\n", 
          fre_clust * fs->csize / 2);
   ```

### 问题2：插入数据很慢

**可能原因**：
- 未使用事务
- 同步模式设置为FULL
- 频繁的磁盘同步

**解决方法**：
1. 使用事务包装批量操作
   ```c
   sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL);
   // 批量插入
   sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
   ```

2. 调整同步模式
   ```c
   sqlite3_exec(db, "PRAGMA synchronous = NORMAL;", 
                NULL, NULL, NULL);
   ```

3. 使用WAL模式
   ```c
   sqlite3_exec(db, "PRAGMA journal_mode = WAL;", 
                NULL, NULL, NULL);
   ```

### 问题3：内存不足

**可能原因**：
- 缓存设置过大
- 查询结果集过大
- 内存泄漏

**解决方法**：
1. 减小缓存大小
   ```c
   sqlite3_exec(db, "PRAGMA cache_size = 50;", 
                NULL, NULL, NULL);
   ```

2. 使用分页查询
   ```c
   const char *sql = 
       "SELECT * FROM sensor_data "
       "LIMIT 100 OFFSET 0;";
   ```

3. 及时释放语句
   ```c
   sqlite3_finalize(stmt);  // 不要忘记释放
   ```

4. 裁剪SQLite功能
   ```c
   // 在编译时定义
   #define SQLITE_OMIT_VIRTUALTABLE
   #define SQLITE_OMIT_TRIGGER
   ```

### 问题4：数据库损坏

**可能原因**：
- 断电时正在写入
- 存储介质故障
- 文件系统错误

**解决方法**：
1. 检查数据库完整性
   ```c
   check_database_integrity();
   ```

2. 尝试恢复
   ```c
   // 导出数据
   sqlite3_exec(db, ".dump", callback, NULL, NULL);
   
   // 重建数据库
   sqlite3_exec(db, ".read dump.sql", NULL, NULL, NULL);
   ```

3. 从备份恢复
   ```c
   restore_database("0:/backup.db");
   ```

### 问题5：查询结果不正确

**可能原因**：
- SQL语句错误
- 数据类型不匹配
- 索引未更新

**解决方法**：
1. 检查SQL语句
   ```c
   // 使用EXPLAIN分析
   analyze_query("SELECT * FROM sensor_data WHERE temperature > 25");
   ```

2. 验证数据类型
   ```c
   // 确保绑定正确的类型
   sqlite3_bind_double(stmt, 1, temperature);  // 浮点数
   sqlite3_bind_int(stmt, 2, id);              // 整数
   ```

3. 重建索引
   ```c
   sqlite3_exec(db, "REINDEX;", NULL, NULL, NULL);
   ```

## 总结

通过本教程，你学习了：

- ✅ SQLite的特点和应用场景
- ✅ 在嵌入式系统中移植SQLite
- ✅ 实现VFS虚拟文件系统接口
- ✅ 使用SQL语句进行数据操作
- ✅ 创建表、插入、查询、更新和删除数据
- ✅ 事务处理和数据完整性
- ✅ 性能优化技巧
- ✅ 数据库备份和恢复
- ✅ 完整的数据记录系统实现

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现数据加密存储
   - 使用SQLite加密扩展（SEE）
   - 或实现自定义加密VFS

2. **挑战2**：实现数据同步功能
   - 本地数据库与云端同步
   - 处理冲突解决

3. **挑战3**：优化大数据量查询
   - 实现分页查询
   - 使用虚拟表
   - 优化索引策略

4. **挑战4**：实现数据导出功能
   - 导出为CSV格式
   - 导出为JSON格式
   - 支持数据筛选

## 完整代码

完整的项目代码可以在这里下载：[GitHub链接]

**项目结构**：
```
sqlite_demo/
├── Core/
│   ├── Src/
│   │   ├── main.c
│   │   └── ...
│   └── Inc/
│       └── ...
├── Middlewares/
│   ├── SQLite/
│   │   ├── sqlite3.c
│   │   ├── sqlite3.h
│   │   └── sqlite3_config.h
│   └── FATFS/
│       └── ...
├── Application/
│   ├── sqlite3_app.c
│   ├── sqlite3_app.h
│   ├── sqlite3_vfs_fatfs.c
│   └── sqlite3_vfs_fatfs.h
└── README.md
```

## 下一步

建议继续学习：

- [键值数据库实现](link) - 学习更简单的KV存储
- [时序数据库应用](link) - 学习时间序列数据处理
- [数据同步与备份策略](link) - 学习数据可靠性保证

## 参考资料

1. **官方文档**
   - SQLite官方网站：https://www.sqlite.org/
   - SQLite C/C++ API：https://www.sqlite.org/c3ref/intro.html
   - SQL语法参考：https://www.sqlite.org/lang.html

2. **技术文章**
   - SQLite性能优化：https://www.sqlite.org/optoverview.html
   - SQLite在嵌入式系统中的应用
   - VFS实现指南

3. **开源项目**
   - SQLite移植示例
   - 嵌入式数据库应用案例

4. **书籍推荐**
   - 《The Definitive Guide to SQLite》
   - 《SQLite Database System: Design and Implementation》

## 常见问题

**Q1: SQLite适合什么样的应用？**

A: SQLite适合：
- 嵌入式设备数据存储
- 移动应用本地数据库
- 桌面应用配置存储
- 小型Web应用
- 数据分析和测试

不适合：
- 高并发写入场景
- 需要网络访问的应用
- 超大数据量（>140TB）

**Q2: 如何选择合适的页大小？**

A: 页大小建议：
- SD卡：1024或2048字节
- SPI Flash：1024字节
- 内部Flash：512或1024字节
- 考虑存储介质的擦除块大小

**Q3: WAL模式的优缺点？**

A: 优点：
- 提升并发性能
- 减少锁竞争
- 更快的写入速度

缺点：
- 需要额外的WAL文件
- 占用更多存储空间
- 某些文件系统不支持

**Q4: 如何减小SQLite代码大小？**

A: 方法：
- 使用编译选项裁剪功能
- 禁用不需要的特性
- 使用-Os优化编译
- 参考官方裁剪指南

**Q5: 如何处理并发访问？**

A: 建议：
- 嵌入式系统通常单线程访问
- 如需多线程，使用互斥锁保护
- 考虑使用WAL模式
- 设置合适的超时时间

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言！

**版本历史**：
- v1.0 (2024-01-15): 初始版本，完整的SQLite教程

**贡献者**：嵌入式知识平台内容团队

**许可证**：本教程采用 CC BY-SA 4.0 许可协议
