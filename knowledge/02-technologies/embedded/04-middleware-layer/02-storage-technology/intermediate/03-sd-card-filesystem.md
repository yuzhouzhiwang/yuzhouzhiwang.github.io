---
# 基础信息
title: "SD卡文件系统完全指南"
description: "全面深入讲解SD卡接口技术、FAT文件系统原理和FatFs库的使用方法，包括SPI/SDIO接口实现、文件系统操作、性能优化和实战项目，掌握嵌入式系统中SD卡存储的核心技术"
slug: "sd-card-filesystem-guide"

# 分类信息
domain: "04-middleware-layer"
module: "02-storage-technology"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - SD卡
  - FAT文件系统
  - FatFs
  - SPI接口
  - SDIO接口
  - 文件操作
  - 存储管理
  - 性能优化
prerequisites:
  - "../beginner/01-flash-technology.md"
  - "../../01-file-systems/beginner/02-littlefs.md"
  - "../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-spi-driver.md"
related_contents:
  - "01-wear-leveling.md"
  - "02-data-persistence.md"
  - "../../01-file-systems/intermediate/02-flash-filesystem.md"

# 学习信息
estimated_time: 120
difficulty_score: 6

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-04-05"
updated_at: "2026-04-05"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - SD卡接口
  - FAT32文件系统
  - FatFs库
  - SPI模式
  - SDIO模式
  - 文件读写
  - 目录管理
  - 存储优化
cover_image: ""
---

# SD卡文件系统完全指南

## 概述

SD卡（Secure Digital Card）是嵌入式系统中最常用的大容量存储解决方案之一。它具有容量大、价格低、易于更换、标准化接口等优点，广泛应用于数据记录、固件更新、媒体存储等场景。本教程将全面深入地讲解SD卡的硬件接口、FAT文件系统原理、FatFs库的使用方法以及性能优化技巧。

### 什么是SD卡文件系统

SD卡文件系统是指在SD卡上实现的文件组织和管理系统，通常使用FAT（File Allocation Table）文件系统。它包含三个核心部分：

1. **硬件接口层**：SPI或SDIO接口，负责与SD卡的物理通信
2. **协议层**：SD卡命令协议，实现卡的初始化、读写等操作
3. **文件系统层**：FAT12/FAT16/FAT32文件系统，提供文件和目录管理

### SD卡 vs 其他存储方案

```
存储方案对比：

┌──────────────┬─────────┬─────────┬─────────┬─────────┐
│   特性       │  SD卡   │  Flash  │ EEPROM  │  FRAM   │
├──────────────┼─────────┼─────────┼─────────┼─────────┤
│ 容量         │  GB级   │  MB级   │  KB级   │  KB级   │
│ 速度         │  快     │  很快   │  慢     │  很快   │
│ 可更换性     │  是     │  否     │  否     │  否     │
│ 文件系统     │  支持   │  需实现 │  不适合 │  不适合 │
│ 成本         │  低     │  中     │  中     │  高     │
│ 擦写次数     │  10万+  │  10万+  │  100万+ │  无限   │
│ 掉电保护     │  需要   │  需要   │  天然   │  天然   │
└──────────────┴─────────┴─────────┴─────────┴─────────┘

应用场景：
- SD卡：数据记录、媒体存储、固件更新
- Flash：程序存储、配置参数
- EEPROM：小量配置、校准数据
- FRAM：高速缓存、关键数据
```

### 应用场景

SD卡在嵌入式系统中的典型应用：

- **数据记录仪**：温度、压力、振动等传感器数据记录
- **音视频设备**：MP3播放器、数码相机、行车记录仪
- **工业控制**：PLC数据存储、配方管理
- **医疗设备**：病人数据记录、设备日志
- **物联网设备**：离线数据缓存、固件升级
- **测试设备**：测试数据存储、波形记录

### 本文内容概览

本教程将涵盖以下内容：

1. **SD卡基础**：SD卡规格、容量分类、物理接口
2. **SPI接口实现**：SPI模式初始化、命令协议、数据传输
3. **SDIO接口实现**：SDIO模式初始化、4位数据传输、DMA优化
4. **FAT文件系统**：FAT12/16/32原理、目录结构、文件分配表
5. **FatFs库使用**：FatFs移植、API使用、配置选项
6. **文件操作**：创建、读写、删除、重命名文件
7. **目录管理**：创建目录、遍历目录、路径操作
8. **性能优化**：缓存策略、DMA传输、多扇区读写
9. **错误处理**：卡检测、写保护、错误恢复
10. **实战项目**：数据记录系统、固件更新、文件浏览器

## 第一部分：SD卡基础知识

### 1.1 SD卡规格和分类

**SD卡容量分类**：

```
SD卡标准演进：

1. SD (Secure Digital)
   - 容量：最大2GB
   - 文件系统：FAT12/FAT16
   - 发布时间：1999年

2. SDHC (High Capacity)
   - 容量：2GB - 32GB
   - 文件系统：FAT32
   - 发布时间：2006年

3. SDXC (eXtended Capacity)
   - 容量：32GB - 2TB
   - 文件系统：exFAT
   - 发布时间：2009年

4. SDUC (Ultra Capacity)
   - 容量：2TB - 128TB
   - 文件系统：exFAT
   - 发布时间：2018年
```


**速度等级分类**：

```
SD卡速度等级：

Class 2:  最低写入速度 2MB/s
Class 4:  最低写入速度 4MB/s
Class 6:  最低写入速度 6MB/s
Class 10: 最低写入速度 10MB/s

UHS Speed Class (Ultra High Speed):
U1: 最低写入速度 10MB/s
U3: 最低写入速度 30MB/s

Video Speed Class:
V6:  最低写入速度 6MB/s  (Full HD)
V10: 最低写入速度 10MB/s (Full HD)
V30: 最低写入速度 30MB/s (4K)
V60: 最低写入速度 60MB/s (8K)
V90: 最低写入速度 90MB/s (8K)

应用建议：
- 数据记录：Class 4 或以上
- 音频播放：Class 2 或以上
- 视频录制：Class 10 或 U1 以上
- 4K视频：U3 或 V30 以上
```

### 1.2 SD卡物理接口

**引脚定义**：

```
SD卡引脚（标准模式）：

     ┌─────────────┐
     │  1  2  3  4 │
     │  5  6  7  8 │
     │  9          │
     └─────────────┘

引脚功能：
1. CD/DAT3  - 卡检测/数据线3
2. CMD      - 命令线
3. VSS      - 地
4. VDD      - 电源 (3.3V)
5. CLK      - 时钟
6. VSS      - 地
7. DAT0     - 数据线0
8. DAT1     - 数据线1
9. DAT2     - 数据线2

SPI模式引脚映射：
- CS   = DAT3 (片选)
- MOSI = CMD  (主机输出)
- MISO = DAT0 (主机输入)
- SCK  = CLK  (时钟)

SDIO模式：
- 1位模式：使用DAT0
- 4位模式：使用DAT0-DAT3
```

**电气特性**：

```c
/**
 * @brief  SD卡电气参数
 */
#define SD_VDD_MIN          2700    // mV，最低工作电压
#define SD_VDD_MAX          3600    // mV，最高工作电压
#define SD_VDD_TYPICAL      3300    // mV，典型工作电压

#define SD_CLK_INIT_MAX     400000  // Hz，初始化时最大时钟
#define SD_CLK_SPI_MAX      25000000 // Hz，SPI模式最大时钟
#define SD_CLK_SDIO_MAX     50000000 // Hz，SDIO模式最大时钟

#define SD_CURRENT_IDLE     1       // mA，空闲电流
#define SD_CURRENT_READ     50      // mA，读取电流
#define SD_CURRENT_WRITE    100     // mA，写入电流
```

### 1.3 SD卡内部结构

**存储结构**：

```
SD卡内部结构：

┌─────────────────────────────────────┐
│         主引导记录 (MBR)             │  扇区0
│  - 分区表                            │
│  - 引导代码                          │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         保留扇区                     │  扇区1-N
│  - 引导扇区 (Boot Sector)            │
│  - FSInfo (FAT32)                   │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         文件分配表 FAT1              │
│  - 簇链信息                          │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         文件分配表 FAT2 (备份)       │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         根目录区                     │
│  - 目录项                            │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         数据区                       │
│  - 文件数据                          │
│  - 子目录                            │
└─────────────────────────────────────┘

扇区大小：512字节
簇大小：通常为4KB、8KB、16KB、32KB
```

## 第二部分：SPI接口实现

### 2.1 SPI模式初始化

SPI模式是最简单的SD卡接口方式，只需要4根线（CS、MOSI、MISO、SCK）。

**初始化流程**：

```
SD卡SPI模式初始化流程：

1. 上电延迟（至少1ms）
2. 发送至少74个时钟脉冲（CS为高）
3. 发送CMD0（复位命令）
4. 发送CMD8（检查电压范围）
5. 发送ACMD41（初始化命令）
6. 发送CMD58（读取OCR寄存器）
7. 发送CMD16（设置块大小为512字节）
8. 初始化完成

时序要求：
- 初始化时时钟频率 ≤ 400kHz
- 初始化完成后可提高到 25MHz
```

**代码实现**：

```c
/**
 * @file    sd_spi.c
 * @brief   SD卡SPI接口驱动
 * @author  嵌入式知识平台
 */

#include <stdint.h>
#include <stdbool.h>
#include "stm32f1xx_hal.h"

/* SD卡命令定义 */
#define CMD0    0       // GO_IDLE_STATE - 复位
#define CMD1    1       // SEND_OP_COND - 初始化
#define CMD8    8       // SEND_IF_COND - 检查电压
#define CMD9    9       // SEND_CSD - 读取CSD寄存器
#define CMD10   10      // SEND_CID - 读取CID寄存器
#define CMD12   12      // STOP_TRANSMISSION - 停止传输
#define CMD16   16      // SET_BLOCKLEN - 设置块大小
#define CMD17   17      // READ_SINGLE_BLOCK - 读单块
#define CMD18   18      // READ_MULTIPLE_BLOCK - 读多块
#define CMD23   23      // SET_BLOCK_COUNT - 设置块数量
#define CMD24   24      // WRITE_BLOCK - 写单块
#define CMD25   25      // WRITE_MULTIPLE_BLOCK - 写多块
#define CMD55   55      // APP_CMD - 应用命令前缀
#define CMD58   58      // READ_OCR - 读取OCR寄存器
#define ACMD41  41      // SD_SEND_OP_COND - SD卡初始化

/* SD卡响应类型 */
#define R1_IDLE_STATE           0x01
#define R1_ERASE_RESET          0x02
#define R1_ILLEGAL_COMMAND      0x04
#define R1_COM_CRC_ERROR        0x08
#define R1_ERASE_SEQUENCE_ERROR 0x10
#define R1_ADDRESS_ERROR        0x20
#define R1_PARAMETER_ERROR      0x40

/* 数据令牌 */
#define TOKEN_START_BLOCK       0xFE
#define TOKEN_START_MULTI_WRITE 0xFC
#define TOKEN_STOP_MULTI_WRITE  0xFD

/* SD卡类型 */
typedef enum {
    SD_TYPE_UNKNOWN = 0,
    SD_TYPE_V1,             // SD卡 V1.x
    SD_TYPE_V2,             // SD卡 V2.0 标准容量
    SD_TYPE_V2HC            // SD卡 V2.0 高容量 (SDHC)
} sd_card_type_t;

/* SD卡信息结构 */
typedef struct {
    sd_card_type_t type;    // 卡类型
    uint32_t capacity;      // 容量（字节）
    uint16_t block_size;    // 块大小
    uint32_t block_count;   // 块数量
    bool initialized;       // 初始化标志
} sd_card_info_t;

static sd_card_info_t sd_info = {0};

/* SPI句柄（需要在main.c中初始化） */
extern SPI_HandleTypeDef hspi1;

/* CS引脚控制 */
#define SD_CS_LOW()     HAL_GPIO_WritePin(SD_CS_GPIO_Port, SD_CS_Pin, GPIO_PIN_RESET)
#define SD_CS_HIGH()    HAL_GPIO_WritePin(SD_CS_GPIO_Port, SD_CS_Pin, GPIO_PIN_SET)

/**
 * @brief  SPI发送接收一个字节
 */
static uint8_t spi_transfer(uint8_t data)
{
    uint8_t rx_data;
    HAL_SPI_TransmitReceive(&hspi1, &data, &rx_data, 1, 100);
    return rx_data;
}

/**
 * @brief  等待SD卡就绪
 * @param  timeout: 超时时间（ms）
 * @return 0: 就绪, -1: 超时
 */
static int sd_wait_ready(uint32_t timeout)
{
    uint32_t start = HAL_GetTick();
    
    while ((HAL_GetTick() - start) < timeout) {
        if (spi_transfer(0xFF) == 0xFF) {
            return 0;  // 就绪
        }
    }
    
    return -1;  // 超时
}

/**
 * @brief  发送SD卡命令
 * @param  cmd: 命令索引
 * @param  arg: 命令参数
 * @return R1响应
 */
static uint8_t sd_send_command(uint8_t cmd, uint32_t arg)
{
    uint8_t response;
    uint8_t retry = 0;
    
    // 等待卡就绪
    if (sd_wait_ready(500) != 0) {
        return 0xFF;
    }
    
    // 发送命令包
    spi_transfer(0x40 | cmd);           // 命令索引（bit6=1）
    spi_transfer((uint8_t)(arg >> 24)); // 参数[31:24]
    spi_transfer((uint8_t)(arg >> 16)); // 参数[23:16]
    spi_transfer((uint8_t)(arg >> 8));  // 参数[15:8]
    spi_transfer((uint8_t)arg);         // 参数[7:0]
    
    // CRC（对于CMD0和CMD8必须正确）
    if (cmd == CMD0) {
        spi_transfer(0x95);  // CMD0的CRC
    } else if (cmd == CMD8) {
        spi_transfer(0x87);  // CMD8的CRC
    } else {
        spi_transfer(0x01);  // 其他命令的虚拟CRC
    }
    
    // 等待响应（最多重试10次）
    for (retry = 0; retry < 10; retry++) {
        response = spi_transfer(0xFF);
        if ((response & 0x80) == 0) {
            break;  // 收到有效响应
        }
    }
    
    return response;
}

/**
 * @brief  发送应用命令（ACMD）
 * @param  cmd: 应用命令索引
 * @param  arg: 命令参数
 * @return R1响应
 */
static uint8_t sd_send_app_command(uint8_t cmd, uint32_t arg)
{
    uint8_t response;
    
    // 先发送CMD55
    response = sd_send_command(CMD55, 0);
    if (response > 1) {
        return response;  // 错误
    }
    
    // 再发送应用命令
    return sd_send_command(cmd, arg);
}

/**
 * @brief  初始化SD卡
 * @return 0: 成功, -1: 失败
 */
int sd_init(void)
{
    uint8_t response;
    uint32_t retry;
    uint8_t ocr[4];
    
    // 1. 上电延迟
    HAL_Delay(10);
    
    // 2. CS拉高，发送至少74个时钟脉冲
    SD_CS_HIGH();
    for (int i = 0; i < 10; i++) {
        spi_transfer(0xFF);
    }
    
    // 3. CS拉低，进入SPI模式
    SD_CS_LOW();
    
    // 4. 发送CMD0，进入空闲状态
    response = sd_send_command(CMD0, 0);
    if (response != R1_IDLE_STATE) {
        SD_CS_HIGH();
        return -1;  // 复位失败
    }
    
    // 5. 发送CMD8，检查电压范围（仅V2.0卡支持）
    response = sd_send_command(CMD8, 0x1AA);
    
    if (response == R1_IDLE_STATE) {
        // V2.0卡
        // 读取R7响应（4字节）
        for (int i = 0; i < 4; i++) {
            ocr[i] = spi_transfer(0xFF);
        }
        
        // 检查电压范围和校验模式
        if (ocr[2] == 0x01 && ocr[3] == 0xAA) {
            // 电压范围匹配
            sd_info.type = SD_TYPE_V2;
        } else {
            SD_CS_HIGH();
            return -1;  // 电压不匹配
        }
    } else {
        // V1.0卡或MMC卡
        sd_info.type = SD_TYPE_V1;
    }
    
    // 6. 发送ACMD41，等待初始化完成
    retry = 0;
    do {
        if (sd_info.type == SD_TYPE_V2) {
            // V2.0卡，设置HCS位
            response = sd_send_app_command(ACMD41, 0x40000000);
        } else {
            // V1.0卡
            response = sd_send_app_command(ACMD41, 0);
        }
        
        retry++;
        if (retry > 1000) {
            SD_CS_HIGH();
            return -1;  // 初始化超时
        }
        
        HAL_Delay(1);
    } while (response != 0x00);
    
    // 7. 读取OCR寄存器（仅V2.0卡）
    if (sd_info.type == SD_TYPE_V2) {
        response = sd_send_command(CMD58, 0);
        if (response != 0x00) {
            SD_CS_HIGH();
            return -1;
        }
        
        // 读取OCR
        for (int i = 0; i < 4; i++) {
            ocr[i] = spi_transfer(0xFF);
        }
        
        // 检查CCS位（bit30）
        if (ocr[0] & 0x40) {
            sd_info.type = SD_TYPE_V2HC;  // SDHC卡
        }
    }
    
    // 8. 设置块大小为512字节（标准容量卡需要）
    if (sd_info.type != SD_TYPE_V2HC) {
        response = sd_send_command(CMD16, 512);
        if (response != 0x00) {
            SD_CS_HIGH();
            return -1;
        }
    }
    
    SD_CS_HIGH();
    
    // 9. 设置卡信息
    sd_info.block_size = 512;
    sd_info.initialized = true;
    
    // 10. 读取卡容量（可选）
    sd_read_capacity();
    
    return 0;
}

/**
 * @brief  读取SD卡容量
 * @return 0: 成功, -1: 失败
 */
int sd_read_capacity(void)
{
    uint8_t csd[16];
    uint8_t response;
    uint32_t capacity;
    
    SD_CS_LOW();
    
    // 发送CMD9读取CSD寄存器
    response = sd_send_command(CMD9, 0);
    if (response != 0x00) {
        SD_CS_HIGH();
        return -1;
    }
    
    // 等待数据令牌
    uint32_t timeout = 1000;
    while (timeout--) {
        response = spi_transfer(0xFF);
        if (response == TOKEN_START_BLOCK) {
            break;
        }
    }
    
    if (timeout == 0) {
        SD_CS_HIGH();
        return -1;  // 超时
    }
    
    // 读取CSD数据（16字节）
    for (int i = 0; i < 16; i++) {
        csd[i] = spi_transfer(0xFF);
    }
    
    // 读取CRC（2字节）
    spi_transfer(0xFF);
    spi_transfer(0xFF);
    
    SD_CS_HIGH();
    
    // 解析CSD，计算容量
    if (sd_info.type == SD_TYPE_V2HC) {
        // SDHC卡（CSD V2.0）
        uint32_t c_size = ((uint32_t)csd[7] << 16) | 
                          ((uint32_t)csd[8] << 8) | 
                          csd[9];
        c_size = (c_size >> 8) & 0x3FFFFF;
        
        capacity = (c_size + 1) * 512 * 1024;  // 字节
        sd_info.block_count = (c_size + 1) * 1024;
    } else {
        // 标准容量卡（CSD V1.0）
        uint32_t c_size = ((uint32_t)(csd[6] & 0x03) << 10) |
                          ((uint32_t)csd[7] << 2) |
                          ((csd[8] & 0xC0) >> 6);
        
        uint8_t c_size_mult = ((csd[9] & 0x03) << 1) |
                              ((csd[10] & 0x80) >> 7);
        
        uint8_t read_bl_len = csd[5] & 0x0F;
        
        uint32_t block_len = 1 << read_bl_len;
        uint32_t mult = 1 << (c_size_mult + 2);
        uint32_t block_count = (c_size + 1) * mult;
        
        capacity = block_count * block_len;
        sd_info.block_count = capacity / 512;
    }
    
    sd_info.capacity = capacity;
    
    return 0;
}
```


### 2.2 读取数据块

```c
/**
 * @brief  读取单个数据块
 * @param  block_addr: 块地址（SDHC为块号，标准卡为字节地址）
 * @param  buffer: 数据缓冲区（512字节）
 * @return 0: 成功, -1: 失败
 */
int sd_read_block(uint32_t block_addr, uint8_t *buffer)
{
    uint8_t response;
    uint32_t timeout;
    
    // 标准容量卡需要转换为字节地址
    if (sd_info.type != SD_TYPE_V2HC) {
        block_addr *= 512;
    }
    
    SD_CS_LOW();
    
    // 发送CMD17（读单块）
    response = sd_send_command(CMD17, block_addr);
    if (response != 0x00) {
        SD_CS_HIGH();
        return -1;
    }
    
    // 等待数据令牌（0xFE）
    timeout = 100000;
    while (timeout--) {
        response = spi_transfer(0xFF);
        if (response == TOKEN_START_BLOCK) {
            break;
        }
    }
    
    if (timeout == 0) {
        SD_CS_HIGH();
        return -1;  // 超时
    }
    
    // 读取512字节数据
    for (int i = 0; i < 512; i++) {
        buffer[i] = spi_transfer(0xFF);
    }
    
    // 读取CRC（2字节，忽略）
    spi_transfer(0xFF);
    spi_transfer(0xFF);
    
    SD_CS_HIGH();
    
    return 0;
}

/**
 * @brief  读取多个数据块
 * @param  block_addr: 起始块地址
 * @param  buffer: 数据缓冲区
 * @param  block_count: 块数量
 * @return 0: 成功, -1: 失败
 */
int sd_read_multiple_blocks(uint32_t block_addr, uint8_t *buffer, uint32_t block_count)
{
    uint8_t response;
    uint32_t timeout;
    
    // 标准容量卡需要转换为字节地址
    if (sd_info.type != SD_TYPE_V2HC) {
        block_addr *= 512;
    }
    
    SD_CS_LOW();
    
    // 发送CMD18（读多块）
    response = sd_send_command(CMD18, block_addr);
    if (response != 0x00) {
        SD_CS_HIGH();
        return -1;
    }
    
    // 读取每个块
    for (uint32_t i = 0; i < block_count; i++) {
        // 等待数据令牌
        timeout = 100000;
        while (timeout--) {
            response = spi_transfer(0xFF);
            if (response == TOKEN_START_BLOCK) {
                break;
            }
        }
        
        if (timeout == 0) {
            // 发送CMD12停止传输
            sd_send_command(CMD12, 0);
            SD_CS_HIGH();
            return -1;
        }
        
        // 读取512字节数据
        for (int j = 0; j < 512; j++) {
            buffer[i * 512 + j] = spi_transfer(0xFF);
        }
        
        // 读取CRC（2字节）
        spi_transfer(0xFF);
        spi_transfer(0xFF);
    }
    
    // 发送CMD12停止传输
    sd_send_command(CMD12, 0);
    
    // 等待卡就绪
    sd_wait_ready(500);
    
    SD_CS_HIGH();
    
    return 0;
}
```

### 2.3 写入数据块

```c
/**
 * @brief  写入单个数据块
 * @param  block_addr: 块地址
 * @param  buffer: 数据缓冲区（512字节）
 * @return 0: 成功, -1: 失败
 */
int sd_write_block(uint32_t block_addr, const uint8_t *buffer)
{
    uint8_t response;
    
    // 标准容量卡需要转换为字节地址
    if (sd_info.type != SD_TYPE_V2HC) {
        block_addr *= 512;
    }
    
    SD_CS_LOW();
    
    // 发送CMD24（写单块）
    response = sd_send_command(CMD24, block_addr);
    if (response != 0x00) {
        SD_CS_HIGH();
        return -1;
    }
    
    // 发送数据令牌
    spi_transfer(TOKEN_START_BLOCK);
    
    // 发送512字节数据
    for (int i = 0; i < 512; i++) {
        spi_transfer(buffer[i]);
    }
    
    // 发送虚拟CRC（2字节）
    spi_transfer(0xFF);
    spi_transfer(0xFF);
    
    // 读取数据响应令牌
    response = spi_transfer(0xFF);
    if ((response & 0x1F) != 0x05) {
        SD_CS_HIGH();
        return -1;  // 写入被拒绝
    }
    
    // 等待写入完成
    if (sd_wait_ready(500) != 0) {
        SD_CS_HIGH();
        return -1;  // 超时
    }
    
    SD_CS_HIGH();
    
    return 0;
}
```


/**
 * @brief  写入多个数据块
 * @param  block_addr: 起始块地址
 * @param  buffer: 数据缓冲区
 * @param  block_count: 块数量
 * @return 0: 成功, -1: 失败
 */
int sd_write_multiple_blocks(uint32_t block_addr, const uint8_t *buffer, uint32_t block_count)
{
    uint8_t response;
    
    // 标准容量卡需要转换为字节地址
    if (sd_info.type != SD_TYPE_V2HC) {
        block_addr *= 512;
    }
    
    SD_CS_LOW();
    
    // 预擦除块数量（可选，提高性能）
    if (sd_info.type != SD_TYPE_V1) {
        sd_send_app_command(CMD23, block_count);
    }
    
    // 发送CMD25（写多块）
    response = sd_send_command(CMD25, block_addr);
    if (response != 0x00) {
        SD_CS_HIGH();
        return -1;
    }
    
    // 写入每个块
    for (uint32_t i = 0; i < block_count; i++) {
        // 发送多块写入令牌
        spi_transfer(TOKEN_START_MULTI_WRITE);
        
        // 发送512字节数据
        for (int j = 0; j < 512; j++) {
            spi_transfer(buffer[i * 512 + j]);
        }
        
        // 发送虚拟CRC
        spi_transfer(0xFF);
        spi_transfer(0xFF);
        
        // 读取数据响应
        response = spi_transfer(0xFF);
        if ((response & 0x1F) != 0x05) {
            // 停止传输
            spi_transfer(TOKEN_STOP_MULTI_WRITE);
            SD_CS_HIGH();
            return -1;
        }
        
        // 等待写入完成
        if (sd_wait_ready(500) != 0) {
            SD_CS_HIGH();
            return -1;
        }
    }
    
    // 发送停止令牌
    spi_transfer(TOKEN_STOP_MULTI_WRITE);
    
    // 等待卡就绪
    sd_wait_ready(500);
    
    SD_CS_HIGH();
    
    return 0;
}

/**
 * @brief  获取SD卡信息
 * @return SD卡信息结构指针
 */
const sd_card_info_t* sd_get_info(void)
{
    return &sd_info;
}

/**
 * @brief  检查SD卡是否存在
 * @return true: 存在, false: 不存在
 */
bool sd_is_present(void)
{
    // 读取卡检测引脚（如果有）
    // 这里假设有CD引脚
    return (HAL_GPIO_ReadPin(SD_CD_GPIO_Port, SD_CD_Pin) == GPIO_PIN_RESET);
}

/**
 * @brief  检查SD卡写保护状态
 * @return true: 写保护, false: 未写保护
 */
bool sd_is_write_protected(void)
{
    // 读取写保护引脚（如果有）
    return (HAL_GPIO_ReadPin(SD_WP_GPIO_Port, SD_WP_Pin) == GPIO_PIN_SET);
}
```

## 第三部分：SDIO接口实现

### 3.1 SDIO模式优势

SDIO（Secure Digital Input Output）模式相比SPI模式有显著优势：

```
SDIO vs SPI 对比：

┌──────────────┬─────────┬─────────┐
│   特性       │  SPI    │  SDIO   │
├──────────────┼─────────┼─────────┤
│ 数据线       │  1位    │  1/4位  │
│ 最大速度     │  25MHz  │  50MHz  │
│ 理论带宽     │  3MB/s  │  25MB/s │
│ 实际带宽     │  2MB/s  │  20MB/s │
│ 引脚数量     │  4      │  6      │
│ 实现复杂度   │  简单   │  中等   │
│ DMA支持      │  可选   │  推荐   │
└──────────────┴─────────┴─────────┘

应用建议：
- 低速应用（<1MB/s）：使用SPI
- 高速应用（>5MB/s）：使用SDIO
- 引脚受限：使用SPI
- 性能优先：使用SDIO
```

### 3.2 SDIO初始化

```c
/**
 * @file    sd_sdio.c
 * @brief   SD卡SDIO接口驱动
 */

#include "stm32f4xx_hal.h"
#include "stm32f4xx_hal_sd.h"

/* SDIO句柄 */
SD_HandleTypeDef hsd;

/**
 * @brief  SDIO初始化
 * @return HAL状态
 */
HAL_StatusTypeDef sdio_init(void)
{
    HAL_StatusTypeDef status;
    
    // 配置SDIO外设
    hsd.Instance = SDIO;
    hsd.Init.ClockEdge = SDIO_CLOCK_EDGE_RISING;
    hsd.Init.ClockBypass = SDIO_CLOCK_BYPASS_DISABLE;
    hsd.Init.ClockPowerSave = SDIO_CLOCK_POWER_SAVE_DISABLE;
    hsd.Init.BusWide = SDIO_BUS_WIDE_1B;  // 先使用1位模式初始化
    hsd.Init.HardwareFlowControl = SDIO_HARDWARE_FLOW_CONTROL_DISABLE;
    hsd.Init.ClockDiv = 0;  // 48MHz / (0+2) = 24MHz
    
    // 初始化SDIO
    status = HAL_SD_Init(&hsd);
    if (status != HAL_OK) {
        return status;
    }
    
    // 切换到4位模式（如果支持）
    status = HAL_SD_ConfigWideBusOperation(&hsd, SDIO_BUS_WIDE_4B);
    if (status != HAL_OK) {
        return status;
    }
    
    return HAL_OK;
}

/**
 * @brief  读取数据块（使用DMA）
 * @param  block_addr: 块地址
 * @param  buffer: 数据缓冲区
 * @param  block_count: 块数量
 * @return HAL状态
 */
HAL_StatusTypeDef sdio_read_blocks_dma(uint32_t block_addr, uint8_t *buffer, uint32_t block_count)
{
    HAL_StatusTypeDef status;
    
    // 启动DMA读取
    status = HAL_SD_ReadBlocks_DMA(&hsd, buffer, block_addr, block_count);
    if (status != HAL_OK) {
        return status;
    }
    
    // 等待传输完成
    while (HAL_SD_GetCardState(&hsd) != HAL_SD_CARD_TRANSFER) {
        // 可以在这里添加超时检测
    }
    
    return HAL_OK;
}

/**
 * @brief  写入数据块（使用DMA）
 * @param  block_addr: 块地址
 * @param  buffer: 数据缓冲区
 * @param  block_count: 块数量
 * @return HAL状态
 */
HAL_StatusTypeDef sdio_write_blocks_dma(uint32_t block_addr, const uint8_t *buffer, uint32_t block_count)
{
    HAL_StatusTypeDef status;
    
    // 启动DMA写入
    status = HAL_SD_WriteBlocks_DMA(&hsd, (uint8_t*)buffer, block_addr, block_count);
    if (status != HAL_OK) {
        return status;
    }
    
    // 等待传输完成
    while (HAL_SD_GetCardState(&hsd) != HAL_SD_CARD_TRANSFER) {
        // 可以在这里添加超时检测
    }
    
    return HAL_OK;
}

/**
 * @brief  获取SD卡信息
 * @param  card_info: 卡信息结构
 * @return HAL状态
 */
HAL_StatusTypeDef sdio_get_card_info(HAL_SD_CardInfoTypeDef *card_info)
{
    return HAL_SD_GetCardInfo(&hsd, card_info);
}
```

## 第四部分：FAT文件系统原理

### 4.1 FAT文件系统概述

FAT（File Allocation Table，文件分配表）是最常用的文件系统之一，具有简单、兼容性好的特点。

**FAT版本**：

```
FAT文件系统版本：

1. FAT12
   - 簇号：12位
   - 最大簇数：4,084
   - 最大卷大小：16MB
   - 应用：软盘

2. FAT16
   - 簇号：16位
   - 最大簇数：65,524
   - 最大卷大小：2GB（簇大小32KB）
   - 应用：小容量存储

3. FAT32
   - 簇号：28位（实际32位，高4位保留）
   - 最大簇数：268,435,444
   - 最大卷大小：2TB（簇大小32KB）
   - 应用：SD卡、U盘

4. exFAT
   - 簇号：32位
   - 最大文件大小：16EB
   - 最大卷大小：128PB
   - 应用：SDXC卡、大容量存储
```

### 4.2 FAT32结构详解

**引导扇区（Boot Sector）**：

```c
/**
 * @brief  FAT32引导扇区结构
 */
typedef struct {
    uint8_t  jmp_boot[3];           // 跳转指令
    uint8_t  oem_name[8];           // OEM名称
    uint16_t bytes_per_sector;      // 每扇区字节数（通常512）
    uint8_t  sectors_per_cluster;   // 每簇扇区数
    uint16_t reserved_sectors;      // 保留扇区数
    uint8_t  num_fats;              // FAT表数量（通常2）
    uint16_t root_entry_count;      // 根目录项数（FAT32为0）
    uint16_t total_sectors_16;      // 总扇区数（小于65536时使用）
    uint8_t  media_type;            // 媒体类型（0xF8表示硬盘）
    uint16_t fat_size_16;           // FAT表大小（FAT32为0）
    uint16_t sectors_per_track;     // 每磁道扇区数
    uint16_t num_heads;             // 磁头数
    uint32_t hidden_sectors;        // 隐藏扇区数
    uint32_t total_sectors_32;      // 总扇区数（大于65535时使用）
    
    // FAT32特有字段
    uint32_t fat_size_32;           // FAT表大小（扇区数）
    uint16_t ext_flags;             // 扩展标志
    uint16_t fs_version;            // 文件系统版本
    uint32_t root_cluster;          // 根目录起始簇号
    uint16_t fs_info;               // FSInfo扇区号
    uint16_t backup_boot_sector;    // 备份引导扇区号
    uint8_t  reserved[12];          // 保留
    uint8_t  drive_number;          // 驱动器号
    uint8_t  reserved1;             // 保留
    uint8_t  boot_signature;        // 扩展引导标记（0x29）
    uint32_t volume_id;             // 卷序列号
    uint8_t  volume_label[11];      // 卷标
    uint8_t  fs_type[8];            // 文件系统类型（"FAT32   "）
    uint8_t  boot_code[420];        // 引导代码
    uint16_t signature;             // 签名（0xAA55）
} __attribute__((packed)) fat32_boot_sector_t;
```


**文件分配表（FAT）**：

```c
/**
 * @brief  FAT表项值含义
 */
#define FAT32_FREE_CLUSTER      0x00000000  // 空闲簇
#define FAT32_RESERVED_MIN      0x0FFFFFF0  // 保留簇（最小）
#define FAT32_RESERVED_MAX      0x0FFFFFF6  // 保留簇（最大）
#define FAT32_BAD_CLUSTER       0x0FFFFFF7  // 坏簇
#define FAT32_EOC_MIN           0x0FFFFFF8  // 簇链结束（最小）
#define FAT32_EOC_MAX           0x0FFFFFFF  // 簇链结束（最大）

/**
 * @brief  读取FAT表项
 * @param  cluster: 簇号
 * @return FAT表项值
 */
uint32_t fat32_read_fat_entry(uint32_t cluster)
{
    uint32_t fat_offset = cluster * 4;  // FAT32每项4字节
    uint32_t fat_sector = boot_sector.reserved_sectors + 
                          (fat_offset / boot_sector.bytes_per_sector);
    uint32_t entry_offset = fat_offset % boot_sector.bytes_per_sector;
    
    uint8_t sector_buffer[512];
    sd_read_block(fat_sector, sector_buffer);
    
    uint32_t fat_entry = *(uint32_t*)&sector_buffer[entry_offset];
    return fat_entry & 0x0FFFFFFF;  // 只使用低28位
}

/**
 * @brief  写入FAT表项
 * @param  cluster: 簇号
 * @param  value: FAT表项值
 * @return 0: 成功, -1: 失败
 */
int fat32_write_fat_entry(uint32_t cluster, uint32_t value)
{
    uint32_t fat_offset = cluster * 4;
    uint32_t fat_sector = boot_sector.reserved_sectors + 
                          (fat_offset / boot_sector.bytes_per_sector);
    uint32_t entry_offset = fat_offset % boot_sector.bytes_per_sector;
    
    uint8_t sector_buffer[512];
    
    // 读取扇区
    if (sd_read_block(fat_sector, sector_buffer) != 0) {
        return -1;
    }
    
    // 修改FAT表项（保留高4位）
    uint32_t *fat_entry = (uint32_t*)&sector_buffer[entry_offset];
    *fat_entry = (*fat_entry & 0xF0000000) | (value & 0x0FFFFFFF);
    
    // 写回扇区
    if (sd_write_block(fat_sector, sector_buffer) != 0) {
        return -1;
    }
    
    // 更新备份FAT表
    uint32_t fat2_sector = fat_sector + boot_sector.fat_size_32;
    sd_write_block(fat2_sector, sector_buffer);
    
    return 0;
}

/**
 * @brief  分配新簇
 * @return 簇号，0表示失败
 */
uint32_t fat32_allocate_cluster(void)
{
    uint32_t total_clusters = boot_sector.total_sectors_32 / 
                               boot_sector.sectors_per_cluster;
    
    // 从簇2开始搜索（簇0和1保留）
    for (uint32_t cluster = 2; cluster < total_clusters; cluster++) {
        uint32_t fat_entry = fat32_read_fat_entry(cluster);
        
        if (fat_entry == FAT32_FREE_CLUSTER) {
            // 找到空闲簇，标记为已使用
            fat32_write_fat_entry(cluster, FAT32_EOC_MAX);
            return cluster;
        }
    }
    
    return 0;  // 没有空闲簇
}
```

**目录项结构**：

```c
/**
 * @brief  短文件名目录项（8.3格式）
 */
typedef struct {
    uint8_t  name[11];          // 文件名（8字节）+ 扩展名（3字节）
    uint8_t  attr;              // 文件属性
    uint8_t  nt_reserved;       // Windows NT保留
    uint8_t  create_time_tenth; // 创建时间（十分之一秒）
    uint16_t create_time;       // 创建时间
    uint16_t create_date;       // 创建日期
    uint16_t last_access_date;  // 最后访问日期
    uint16_t first_cluster_hi;  // 起始簇号（高16位）
    uint16_t write_time;        // 修改时间
    uint16_t write_date;        // 修改日期
    uint16_t first_cluster_lo;  // 起始簇号（低16位）
    uint32_t file_size;         // 文件大小（字节）
} __attribute__((packed)) fat_dir_entry_t;

/**
 * @brief  文件属性标志
 */
#define ATTR_READ_ONLY  0x01    // 只读
#define ATTR_HIDDEN     0x02    // 隐藏
#define ATTR_SYSTEM     0x04    // 系统
#define ATTR_VOLUME_ID  0x08    // 卷标
#define ATTR_DIRECTORY  0x10    // 目录
#define ATTR_ARCHIVE    0x20    // 归档
#define ATTR_LONG_NAME  0x0F    // 长文件名

/**
 * @brief  长文件名目录项
 */
typedef struct {
    uint8_t  order;             // 序号
    uint16_t name1[5];          // 名称第1部分（Unicode）
    uint8_t  attr;              // 属性（必须为0x0F）
    uint8_t  type;              // 类型（必须为0）
    uint8_t  checksum;          // 短文件名校验和
    uint16_t name2[6];          // 名称第2部分（Unicode）
    uint16_t first_cluster;     // 起始簇（必须为0）
    uint16_t name3[2];          // 名称第3部分（Unicode）
} __attribute__((packed)) fat_lfn_entry_t;

/**
 * @brief  计算短文件名校验和
 */
uint8_t fat_calculate_sfn_checksum(const uint8_t *sfn)
{
    uint8_t sum = 0;
    
    for (int i = 0; i < 11; i++) {
        sum = ((sum & 1) << 7) + (sum >> 1) + sfn[i];
    }
    
    return sum;
}
```

### 4.3 文件操作实现

```c
/**
 * @brief  打开文件
 * @param  path: 文件路径
 * @param  mode: 打开模式（'r', 'w', 'a'）
 * @return 文件句柄，NULL表示失败
 */
typedef struct {
    uint32_t first_cluster;     // 起始簇号
    uint32_t current_cluster;   // 当前簇号
    uint32_t file_size;         // 文件大小
    uint32_t position;          // 当前位置
    uint8_t  mode;              // 打开模式
    bool     is_open;           // 是否打开
} file_handle_t;

file_handle_t* fat_open_file(const char *path, char mode)
{
    file_handle_t *handle = malloc(sizeof(file_handle_t));
    if (!handle) {
        return NULL;
    }
    
    // 查找文件
    fat_dir_entry_t entry;
    if (fat_find_file(path, &entry) != 0) {
        if (mode == 'r') {
            free(handle);
            return NULL;  // 读模式下文件必须存在
        }
        
        // 写模式下创建新文件
        if (fat_create_file(path, &entry) != 0) {
            free(handle);
            return NULL;
        }
    }
    
    // 初始化文件句柄
    handle->first_cluster = ((uint32_t)entry.first_cluster_hi << 16) | 
                            entry.first_cluster_lo;
    handle->current_cluster = handle->first_cluster;
    handle->file_size = entry.file_size;
    handle->position = 0;
    handle->mode = mode;
    handle->is_open = true;
    
    // 追加模式：定位到文件末尾
    if (mode == 'a') {
        fat_seek_file(handle, entry.file_size);
    }
    
    return handle;
}

/**
 * @brief  读取文件
 * @param  handle: 文件句柄
 * @param  buffer: 数据缓冲区
 * @param  size: 读取字节数
 * @return 实际读取的字节数
 */
size_t fat_read_file(file_handle_t *handle, void *buffer, size_t size)
{
    if (!handle || !handle->is_open || handle->mode == 'w') {
        return 0;
    }
    
    size_t bytes_read = 0;
    uint8_t *buf = (uint8_t*)buffer;
    
    uint32_t cluster_size = boot_sector.sectors_per_cluster * 
                            boot_sector.bytes_per_sector;
    
    while (bytes_read < size && handle->position < handle->file_size) {
        // 计算当前簇内偏移
        uint32_t cluster_offset = handle->position % cluster_size;
        uint32_t bytes_in_cluster = cluster_size - cluster_offset;
        
        // 计算本次读取字节数
        size_t bytes_to_read = size - bytes_read;
        if (bytes_to_read > bytes_in_cluster) {
            bytes_to_read = bytes_in_cluster;
        }
        if (bytes_to_read > handle->file_size - handle->position) {
            bytes_to_read = handle->file_size - handle->position;
        }
        
        // 读取数据
        uint32_t sector = fat_cluster_to_sector(handle->current_cluster) +
                          (cluster_offset / boot_sector.bytes_per_sector);
        uint32_t sector_offset = cluster_offset % boot_sector.bytes_per_sector;
        
        uint8_t sector_buffer[512];
        sd_read_block(sector, sector_buffer);
        
        memcpy(&buf[bytes_read], &sector_buffer[sector_offset], bytes_to_read);
        
        bytes_read += bytes_to_read;
        handle->position += bytes_to_read;
        
        // 检查是否需要移动到下一个簇
        if (handle->position % cluster_size == 0 && 
            handle->position < handle->file_size) {
            uint32_t next_cluster = fat32_read_fat_entry(handle->current_cluster);
            if (next_cluster >= FAT32_EOC_MIN) {
                break;  // 到达文件末尾
            }
            handle->current_cluster = next_cluster;
        }
    }
    
    return bytes_read;
}

/**
 * @brief  写入文件
 * @param  handle: 文件句柄
 * @param  buffer: 数据缓冲区
 * @param  size: 写入字节数
 * @return 实际写入的字节数
 */
size_t fat_write_file(file_handle_t *handle, const void *buffer, size_t size)
{
    if (!handle || !handle->is_open || handle->mode == 'r') {
        return 0;
    }
    
    size_t bytes_written = 0;
    const uint8_t *buf = (const uint8_t*)buffer;
    
    uint32_t cluster_size = boot_sector.sectors_per_cluster * 
                            boot_sector.bytes_per_sector;
    
    while (bytes_written < size) {
        // 检查是否需要分配新簇
        if (handle->position % cluster_size == 0) {
            if (handle->position == 0) {
                // 第一个簇
                handle->first_cluster = fat32_allocate_cluster();
                handle->current_cluster = handle->first_cluster;
            } else {
                // 分配新簇并链接
                uint32_t new_cluster = fat32_allocate_cluster();
                fat32_write_fat_entry(handle->current_cluster, new_cluster);
                handle->current_cluster = new_cluster;
            }
        }
        
        // 计算当前簇内偏移
        uint32_t cluster_offset = handle->position % cluster_size;
        uint32_t bytes_in_cluster = cluster_size - cluster_offset;
        
        // 计算本次写入字节数
        size_t bytes_to_write = size - bytes_written;
        if (bytes_to_write > bytes_in_cluster) {
            bytes_to_write = bytes_in_cluster;
        }
        
        // 写入数据
        uint32_t sector = fat_cluster_to_sector(handle->current_cluster) +
                          (cluster_offset / boot_sector.bytes_per_sector);
        uint32_t sector_offset = cluster_offset % boot_sector.bytes_per_sector;
        
        uint8_t sector_buffer[512];
        
        // 如果不是整扇区写入，需要先读取
        if (sector_offset != 0 || bytes_to_write < 512) {
            sd_read_block(sector, sector_buffer);
        }
        
        memcpy(&sector_buffer[sector_offset], &buf[bytes_written], bytes_to_write);
        sd_write_block(sector, sector_buffer);
        
        bytes_written += bytes_to_write;
        handle->position += bytes_to_write;
        
        // 更新文件大小
        if (handle->position > handle->file_size) {
            handle->file_size = handle->position;
        }
    }
    
    return bytes_written;
}

/**
 * @brief  关闭文件
 * @param  handle: 文件句柄
 * @return 0: 成功, -1: 失败
 */
int fat_close_file(file_handle_t *handle)
{
    if (!handle || !handle->is_open) {
        return -1;
    }
    
    // 如果是写模式，更新目录项
    if (handle->mode == 'w' || handle->mode == 'a') {
        fat_update_dir_entry(handle);
    }
    
    handle->is_open = false;
    free(handle);
    
    return 0;
}

/**
 * @brief  簇号转扇区号
 */
uint32_t fat_cluster_to_sector(uint32_t cluster)
{
    uint32_t first_data_sector = boot_sector.reserved_sectors +
                                 (boot_sector.num_fats * boot_sector.fat_size_32);
    
    return first_data_sector + 
           ((cluster - 2) * boot_sector.sectors_per_cluster);
}
```

## 第五部分：FatFs库使用

### 5.1 FatFs简介

FatFs是一个通用的FAT文件系统模块，专为小型嵌入式系统设计。

**FatFs特性**：

```
FatFs主要特性：

✓ 支持FAT12/FAT16/FAT32/exFAT
✓ 多分区支持
✓ 多卷（多个存储设备）支持
✓ 长文件名（LFN）支持
✓ Unicode支持
✓ 可重入（线程安全）
✓ 可配置功能
✓ 小内存占用
✓ 免费开源（BSD许可）

配置选项：
- 只读/读写
- 最小化/完整功能
- 代码页选择
- LFN支持级别
- 文件锁定
- 相对路径
```


### 5.2 FatFs移植

**步骤1：添加FatFs源码**

```
FatFs文件结构：

fatfs/
├── source/
│   ├── ff.c            # FatFs核心代码
│   ├── ff.h            # FatFs头文件
│   ├── ffconf.h        # 配置文件
│   ├── diskio.c        # 磁盘I/O接口（需要实现）
│   └── diskio.h        # 磁盘I/O头文件
└── option/
    ├── ccsbcs.c        # 代码页转换
    └── syscall.c       # 系统调用（可选）
```

**步骤2：配置ffconf.h**

```c
/**
 * @file    ffconf.h
 * @brief   FatFs配置文件
 */

#define FFCONF_DEF  80286   // 版本号

/* 功能配置 */
#define FF_FS_READONLY  0   // 0:读写, 1:只读
#define FF_FS_MINIMIZE  0   // 0:完整功能, 1-3:最小化级别
#define FF_USE_STRFUNC  1   // 字符串函数支持
#define FF_USE_FIND     1   // 目录搜索功能
#define FF_USE_MKFS     1   // 格式化功能
#define FF_USE_FASTSEEK 1   // 快速定位功能
#define FF_USE_EXPAND   0   // 文件扩展功能
#define FF_USE_CHMOD    1   // 属性修改功能
#define FF_USE_LABEL    1   // 卷标功能
#define FF_USE_FORWARD  0   // 数据转发功能

/* 本地化配置 */
#define FF_CODE_PAGE    936 // 代码页（936=GBK, 437=US）
#define FF_USE_LFN      2   // 长文件名支持（0:禁用, 1:静态, 2:堆, 3:栈）
#define FF_MAX_LFN      255 // 最大长文件名长度
#define FF_LFN_UNICODE  0   // Unicode支持
#define FF_LFN_BUF      255 // LFN缓冲区大小
#define FF_SFN_BUF      12  // SFN缓冲区大小
#define FF_STRF_ENCODE  0   // 字符串编码

/* 驱动配置 */
#define FF_FS_RPATH     1   // 相对路径支持
#define FF_VOLUMES      1   // 逻辑驱动器数量
#define FF_STR_VOLUME_ID 0  // 卷ID字符串支持
#define FF_MULTI_PARTITION 0 // 多分区支持
#define FF_MIN_SS       512 // 最小扇区大小
#define FF_MAX_SS       512 // 最大扇区大小
#define FF_USE_TRIM     0   // TRIM功能
#define FF_FS_NOFSINFO  0   // FSInfo扇区

/* 系统配置 */
#define FF_FS_TINY      0   // Tiny缓冲区配置
#define FF_FS_EXFAT     0   // exFAT支持
#define FF_FS_NORTC     0   // 实时时钟支持
#define FF_NORTC_MON    1   // 默认月份
#define FF_NORTC_MDAY   1   // 默认日期
#define FF_NORTC_YEAR   2024 // 默认年份
#define FF_FS_LOCK      0   // 文件锁定功能
#define FF_FS_REENTRANT 0   // 可重入支持
#define FF_FS_TIMEOUT   1000 // 超时时间
#define FF_SYNC_t       void* // 同步对象类型
```

**步骤3：实现diskio.c**

```c
/**
 * @file    diskio.c
 * @brief   FatFs磁盘I/O接口实现
 */

#include "ff.h"
#include "diskio.h"
#include "sd_spi.h"  // 或 sd_sdio.h

/* 物理驱动器编号 */
#define DEV_SD  0

/**
 * @brief  获取驱动器状态
 * @param  pdrv: 物理驱动器编号
 * @return 状态标志
 */
DSTATUS disk_status(BYTE pdrv)
{
    DSTATUS stat = 0;
    
    switch (pdrv) {
        case DEV_SD:
            // 检查SD卡是否存在
            if (!sd_is_present()) {
                stat = STA_NODISK;
            }
            
            // 检查是否初始化
            if (!sd_info.initialized) {
                stat |= STA_NOINIT;
            }
            
            // 检查写保护
            if (sd_is_write_protected()) {
                stat |= STA_PROTECT;
            }
            break;
            
        default:
            stat = STA_NOINIT;
            break;
    }
    
    return stat;
}

/**
 * @brief  初始化驱动器
 * @param  pdrv: 物理驱动器编号
 * @return 状态标志
 */
DSTATUS disk_initialize(BYTE pdrv)
{
    DSTATUS stat = STA_NOINIT;
    
    switch (pdrv) {
        case DEV_SD:
            // 初始化SD卡
            if (sd_init() == 0) {
                stat = 0;  // 初始化成功
            }
            break;
            
        default:
            break;
    }
    
    return stat;
}

/**
 * @brief  读取扇区
 * @param  pdrv: 物理驱动器编号
 * @param  buff: 数据缓冲区
 * @param  sector: 起始扇区号
 * @param  count: 扇区数量
 * @return 结果代码
 */
DRESULT disk_read(BYTE pdrv, BYTE *buff, LBA_t sector, UINT count)
{
    DRESULT res = RES_PARERR;
    
    switch (pdrv) {
        case DEV_SD:
            if (count == 1) {
                // 读取单个扇区
                if (sd_read_block(sector, buff) == 0) {
                    res = RES_OK;
                } else {
                    res = RES_ERROR;
                }
            } else {
                // 读取多个扇区
                if (sd_read_multiple_blocks(sector, buff, count) == 0) {
                    res = RES_OK;
                } else {
                    res = RES_ERROR;
                }
            }
            break;
            
        default:
            res = RES_PARERR;
            break;
    }
    
    return res;
}

/**
 * @brief  写入扇区
 * @param  pdrv: 物理驱动器编号
 * @param  buff: 数据缓冲区
 * @param  sector: 起始扇区号
 * @param  count: 扇区数量
 * @return 结果代码
 */
DRESULT disk_write(BYTE pdrv, const BYTE *buff, LBA_t sector, UINT count)
{
    DRESULT res = RES_PARERR;
    
    switch (pdrv) {
        case DEV_SD:
            if (count == 1) {
                // 写入单个扇区
                if (sd_write_block(sector, buff) == 0) {
                    res = RES_OK;
                } else {
                    res = RES_ERROR;
                }
            } else {
                // 写入多个扇区
                if (sd_write_multiple_blocks(sector, buff, count) == 0) {
                    res = RES_OK;
                } else {
                    res = RES_ERROR;
                }
            }
            break;
            
        default:
            res = RES_PARERR;
            break;
    }
    
    return res;
}

/**
 * @brief  I/O控制
 * @param  pdrv: 物理驱动器编号
 * @param  cmd: 控制命令
 * @param  buff: 参数缓冲区
 * @return 结果代码
 */
DRESULT disk_ioctl(BYTE pdrv, BYTE cmd, void *buff)
{
    DRESULT res = RES_PARERR;
    
    switch (pdrv) {
        case DEV_SD:
            switch (cmd) {
                case CTRL_SYNC:
                    // 同步（确保写入完成）
                    res = RES_OK;
                    break;
                    
                case GET_SECTOR_COUNT:
                    // 获取扇区数量
                    *(LBA_t*)buff = sd_info.block_count;
                    res = RES_OK;
                    break;
                    
                case GET_SECTOR_SIZE:
                    // 获取扇区大小
                    *(WORD*)buff = sd_info.block_size;
                    res = RES_OK;
                    break;
                    
                case GET_BLOCK_SIZE:
                    // 获取擦除块大小
                    *(DWORD*)buff = 1;  // SD卡通常为1
                    res = RES_OK;
                    break;
                    
                case CTRL_TRIM:
                    // TRIM命令（可选）
                    res = RES_OK;
                    break;
                    
                default:
                    res = RES_PARERR;
                    break;
            }
            break;
            
        default:
            res = RES_PARERR;
            break;
    }
    
    return res;
}

/**
 * @brief  获取当前时间（用于文件时间戳）
 * @return 打包的时间值
 */
DWORD get_fattime(void)
{
    // 获取RTC时间（如果有）
    // 这里返回固定时间：2024-01-01 00:00:00
    return ((DWORD)(2024 - 1980) << 25)  // 年份
         | ((DWORD)1 << 21)              // 月份
         | ((DWORD)1 << 16)              // 日期
         | ((DWORD)0 << 11)              // 小时
         | ((DWORD)0 << 5)               // 分钟
         | ((DWORD)0 >> 1);              // 秒（除以2）
}
```

### 5.3 FatFs API使用

**文件操作API**：

```c
/**
 * @brief  FatFs文件操作示例
 */

#include "ff.h"

/**
 * @brief  挂载文件系统
 */
int mount_filesystem(void)
{
    FATFS fs;
    FRESULT res;
    
    // 挂载文件系统
    res = f_mount(&fs, "0:", 1);  // "0:" 表示驱动器0，1表示立即挂载
    
    if (res != FR_OK) {
        printf("Mount failed: %d\n", res);
        return -1;
    }
    
    printf("Filesystem mounted successfully\n");
    return 0;
}

/**
 * @brief  创建并写入文件
 */
int write_file_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_written;
    
    const char *filename = "0:/test.txt";
    const char *data = "Hello, FatFs!\n";
    
    // 打开文件（创建新文件或覆盖现有文件）
    res = f_open(&file, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Open file failed: %d\n", res);
        return -1;
    }
    
    // 写入数据
    res = f_write(&file, data, strlen(data), &bytes_written);
    if (res != FR_OK || bytes_written < strlen(data)) {
        printf("Write file failed: %d\n", res);
        f_close(&file);
        return -1;
    }
    
    printf("Written %u bytes\n", bytes_written);
    
    // 关闭文件
    f_close(&file);
    
    return 0;
}

/**
 * @brief  读取文件
 */
int read_file_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_read;
    char buffer[128];
    
    const char *filename = "0:/test.txt";
    
    // 打开文件（只读）
    res = f_open(&file, filename, FA_READ);
    if (res != FR_OK) {
        printf("Open file failed: %d\n", res);
        return -1;
    }
    
    // 读取数据
    res = f_read(&file, buffer, sizeof(buffer) - 1, &bytes_read);
    if (res != FR_OK) {
        printf("Read file failed: %d\n", res);
        f_close(&file);
        return -1;
    }
    
    buffer[bytes_read] = '\0';  // 添加字符串结束符
    printf("Read %u bytes: %s\n", bytes_read, buffer);
    
    // 关闭文件
    f_close(&file);
    
    return 0;
}

/**
 * @brief  追加数据到文件
 */
int append_file_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_written;
    
    const char *filename = "0:/test.txt";
    const char *data = "Appended data\n";
    
    // 打开文件（追加模式）
    res = f_open(&file, filename, FA_OPEN_APPEND | FA_WRITE);
    if (res != FR_OK) {
        printf("Open file failed: %d\n", res);
        return -1;
    }
    
    // 写入数据
    res = f_write(&file, data, strlen(data), &bytes_written);
    if (res != FR_OK) {
        printf("Write file failed: %d\n", res);
        f_close(&file);
        return -1;
    }
    
    printf("Appended %u bytes\n", bytes_written);
    
    // 关闭文件
    f_close(&file);
    
    return 0;
}

/**
 * @brief  文件定位
 */
int seek_file_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_read;
    char buffer[32];
    
    const char *filename = "0:/test.txt";
    
    // 打开文件
    res = f_open(&file, filename, FA_READ);
    if (res != FR_OK) {
        return -1;
    }
    
    // 定位到文件中间
    res = f_lseek(&file, f_size(&file) / 2);
    if (res != FR_OK) {
        f_close(&file);
        return -1;
    }
    
    // 读取数据
    f_read(&file, buffer, sizeof(buffer) - 1, &bytes_read);
    buffer[bytes_read] = '\0';
    
    printf("Data from middle: %s\n", buffer);
    
    f_close(&file);
    
    return 0;
}

/**
 * @brief  获取文件信息
 */
int get_file_info_example(void)
{
    FILINFO fno;
    FRESULT res;
    
    const char *filename = "0:/test.txt";
    
    // 获取文件信息
    res = f_stat(filename, &fno);
    if (res != FR_OK) {
        printf("Get file info failed: %d\n", res);
        return -1;
    }
    
    printf("File: %s\n", filename);
    printf("Size: %lu bytes\n", fno.fsize);
    printf("Date: %04d-%02d-%02d\n", 
           (fno.fdate >> 9) + 1980,
           (fno.fdate >> 5) & 0x0F,
           fno.fdate & 0x1F);
    printf("Time: %02d:%02d:%02d\n",
           fno.ftime >> 11,
           (fno.ftime >> 5) & 0x3F,
           (fno.ftime & 0x1F) * 2);
    printf("Attributes: %s%s%s%s\n",
           (fno.fattrib & AM_RDO) ? "R" : "",
           (fno.fattrib & AM_HID) ? "H" : "",
           (fno.fattrib & AM_SYS) ? "S" : "",
           (fno.fattrib & AM_DIR) ? "D" : "");
    
    return 0;
}
```


**目录操作API**:

```c
/**
 * @brief  创建目录
 */
int create_directory_example(void)
{
    FRESULT res;
    
    // 创建目录
    res = f_mkdir("0:/data");
    if (res != FR_OK && res != FR_EXIST) {
        printf("Create directory failed: %d\n", res);
        return -1;
    }
    
    printf("Directory created\n");
    return 0;
}

/**
 * @brief  遍历目录
 */
int list_directory_example(void)
{
    DIR dir;
    FILINFO fno;
    FRESULT res;
    
    // 打开目录
    res = f_opendir(&dir, "0:/");
    if (res != FR_OK) {
        printf("Open directory failed: %d\n", res);
        return -1;
    }
    
    printf("Directory listing:\n");
    
    // 遍历目录
    while (1) {
        res = f_readdir(&dir, &fno);
        if (res != FR_OK || fno.fname[0] == 0) {
            break;  // 错误或到达目录末尾
        }
        
        // 打印文件/目录信息
        printf("%s %10lu %s\n",
               (fno.fattrib & AM_DIR) ? "DIR " : "FILE",
               fno.fsize,
               fno.fname);
    }
    
    // 关闭目录
    f_closedir(&dir);
    
    return 0;
}

/**
 * @brief  删除文件或目录
 */
int delete_example(void)
{
    FRESULT res;
    
    // 删除文件
    res = f_unlink("0:/test.txt");
    if (res != FR_OK) {
        printf("Delete file failed: %d\n", res);
        return -1;
    }
    
    printf("File deleted\n");
    return 0;
}

/**
 * @brief  重命名文件或目录
 */
int rename_example(void)
{
    FRESULT res;
    
    // 重命名文件
    res = f_rename("0:/old.txt", "0:/new.txt");
    if (res != FR_OK) {
        printf("Rename failed: %d\n", res);
        return -1;
    }
    
    printf("File renamed\n");
    return 0;
}
```

## 第六部分：性能优化

### 6.1 缓存策略

```c
/**
 * @brief  使用缓冲区提高写入性能
 */
#define WRITE_BUFFER_SIZE   4096

int buffered_write_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_written;
    uint8_t buffer[WRITE_BUFFER_SIZE];
    
    // 打开文件
    res = f_open(&file, "0:/large.dat", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        return -1;
    }
    
    // 准备数据
    for (int i = 0; i < WRITE_BUFFER_SIZE; i++) {
        buffer[i] = i & 0xFF;
    }
    
    // 批量写入
    uint32_t start_time = HAL_GetTick();
    
    for (int i = 0; i < 100; i++) {
        res = f_write(&file, buffer, WRITE_BUFFER_SIZE, &bytes_written);
        if (res != FR_OK) {
            break;
        }
    }
    
    uint32_t elapsed = HAL_GetTick() - start_time;
    
    // 关闭文件
    f_close(&file);
    
    printf("Written 400KB in %lu ms\n", elapsed);
    printf("Speed: %.2f KB/s\n", 400.0 * 1000 / elapsed);
    
    return 0;
}
```


### 6.2 多扇区读写

```c
/**
 * @brief  多扇区读写优化
 */
int multi_sector_rw_example(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_rw;
    
    // 分配对齐的缓冲区（提高DMA性能）
    __attribute__((aligned(4))) uint8_t buffer[512 * 8];  // 8个扇区
    
    // 打开文件
    res = f_open(&file, "0:/data.bin", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        return -1;
    }
    
    // 一次写入多个扇区
    for (int i = 0; i < sizeof(buffer); i++) {
        buffer[i] = i & 0xFF;
    }
    
    res = f_write(&file, buffer, sizeof(buffer), &bytes_rw);
    
    f_close(&file);
    
    return (res == FR_OK) ? 0 : -1;
}
```

### 6.3 快速定位（FSEEK优化）

```c
/**
 * @brief  使用快速定位表
 */
int fast_seek_example(void)
{
    FIL file;
    FRESULT res;
    DWORD clmt[32];  // 簇链接表
    
    // 打开文件
    res = f_open(&file, "0:/large.dat", FA_READ);
    if (res != FR_OK) {
        return -1;
    }
    
    // 创建簇链接表
    file.cltbl = clmt;
    clmt[0] = sizeof(clmt) / sizeof(DWORD);
    
    res = f_lseek(&file, CREATE_LINKMAP);
    if (res != FR_OK) {
        f_close(&file);
        return -1;
    }
    
    // 现在可以快速定位
    res = f_lseek(&file, 1024 * 1024);  // 定位到1MB位置
    
    f_close(&file);
    
    return 0;
}
```

## 第七部分：错误处理与调试

### 7.1 错误代码处理

```c
/**
 * @brief  FatFs错误代码转字符串
 */
const char* fresult_to_string(FRESULT res)
{
    switch (res) {
        case FR_OK:                  return "Success";
        case FR_DISK_ERR:            return "Disk error";
        case FR_INT_ERR:             return "Internal error";
        case FR_NOT_READY:           return "Not ready";
        case FR_NO_FILE:             return "No file";
        case FR_NO_PATH:             return "No path";
        case FR_INVALID_NAME:        return "Invalid name";
        case FR_DENIED:              return "Access denied";
        case FR_EXIST:               return "Already exists";
        case FR_INVALID_OBJECT:      return "Invalid object";
        case FR_WRITE_PROTECTED:     return "Write protected";
        case FR_INVALID_DRIVE:       return "Invalid drive";
        case FR_NOT_ENABLED:         return "Not enabled";
        case FR_NO_FILESYSTEM:       return "No filesystem";
        case FR_MKFS_ABORTED:        return "Format aborted";
        case FR_TIMEOUT:             return "Timeout";
        case FR_LOCKED:              return "File locked";
        case FR_NOT_ENOUGH_CORE:     return "Not enough memory";
        case FR_TOO_MANY_OPEN_FILES: return "Too many open files";
        case FR_INVALID_PARAMETER:   return "Invalid parameter";
        default:                     return "Unknown error";
    }
}

/**
 * @brief  安全的文件操作（带错误处理）
 */
int safe_file_operation(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_written;
    const char *data = "Test data\n";
    
    // 尝试打开文件
    res = f_open(&file, "0:/test.txt", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Error opening file: %s\n", fresult_to_string(res));
        return -1;
    }
    
    // 尝试写入
    res = f_write(&file, data, strlen(data), &bytes_written);
    if (res != FR_OK) {
        printf("Error writing file: %s\n", fresult_to_string(res));
        f_close(&file);
        return -1;
    }
    
    // 检查写入字节数
    if (bytes_written < strlen(data)) {
        printf("Warning: Only %u bytes written\n", bytes_written);
    }
    
    // 同步数据到磁盘
    res = f_sync(&file);
    if (res != FR_OK) {
        printf("Error syncing file: %s\n", fresult_to_string(res));
    }
    
    // 关闭文件
    f_close(&file);
    
    return 0;
}
```

### 7.2 卡检测与热插拔

```c
/**
 * @brief  SD卡热插拔处理
 */
typedef enum {
    SD_STATE_NO_CARD = 0,
    SD_STATE_CARD_INSERTED,
    SD_STATE_MOUNTED,
    SD_STATE_ERROR
} sd_state_t;

static sd_state_t sd_state = SD_STATE_NO_CARD;
static FATFS fs;

/**
 * @brief  SD卡状态机
 */
void sd_card_state_machine(void)
{
    static uint32_t last_check = 0;
    uint32_t now = HAL_GetTick();
    
    // 每100ms检查一次
    if (now - last_check < 100) {
        return;
    }
    last_check = now;
    
    bool card_present = sd_is_present();
    
    switch (sd_state) {
        case SD_STATE_NO_CARD:
            if (card_present) {
                printf("SD card inserted\n");
                sd_state = SD_STATE_CARD_INSERTED;
            }
            break;
            
        case SD_STATE_CARD_INSERTED:
            if (!card_present) {
                sd_state = SD_STATE_NO_CARD;
                break;
            }
            
            // 尝试挂载
            if (f_mount(&fs, "0:", 1) == FR_OK) {
                printf("SD card mounted\n");
                sd_state = SD_STATE_MOUNTED;
            } else {
                printf("Mount failed\n");
                sd_state = SD_STATE_ERROR;
            }
            break;
            
        case SD_STATE_MOUNTED:
            if (!card_present) {
                printf("SD card removed\n");
                f_mount(NULL, "0:", 0);  // 卸载
                sd_state = SD_STATE_NO_CARD;
            }
            break;
            
        case SD_STATE_ERROR:
            if (!card_present) {
                sd_state = SD_STATE_NO_CARD;
            }
            break;
    }
}

/**
 * @brief  检查SD卡是否就绪
 */
bool sd_is_ready(void)
{
    return (sd_state == SD_STATE_MOUNTED);
}
```

## 第八部分：实战项目

### 8.1 数据记录系统

```c
/**
 * @brief  数据记录系统
 * @note   记录传感器数据到SD卡
 */

#define LOG_BUFFER_SIZE     512
#define LOG_FLUSH_INTERVAL  5000  // 5秒刷新一次

typedef struct {
    uint32_t timestamp;
    float temperature;
    float humidity;
    float pressure;
} sensor_data_t;

static FIL log_file;
static uint8_t log_buffer[LOG_BUFFER_SIZE];
static uint32_t log_buffer_pos = 0;
static uint32_t last_flush_time = 0;
static bool logging_enabled = false;

/**
 * @brief  启动数据记录
 */
int start_data_logging(void)
{
    FRESULT res;
    char filename[32];
    
    // 生成文件名（基于时间）
    snprintf(filename, sizeof(filename), "0:/log_%08lX.csv", HAL_GetTick());
    
    // 打开文件
    res = f_open(&log_file, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to create log file: %s\n", fresult_to_string(res));
        return -1;
    }
    
    // 写入CSV头
    const char *header = "Timestamp,Temperature,Humidity,Pressure\n";
    UINT bytes_written;
    f_write(&log_file, header, strlen(header), &bytes_written);
    
    logging_enabled = true;
    log_buffer_pos = 0;
    last_flush_time = HAL_GetTick();
    
    printf("Data logging started: %s\n", filename);
    
    return 0;
}

/**
 * @brief  记录一条数据
 */
int log_sensor_data(const sensor_data_t *data)
{
    if (!logging_enabled) {
        return -1;
    }
    
    // 格式化数据
    char line[128];
    int len = snprintf(line, sizeof(line), "%lu,%.2f,%.2f,%.2f\n",
                       data->timestamp,
                       data->temperature,
                       data->humidity,
                       data->pressure);
    
    // 检查缓冲区空间
    if (log_buffer_pos + len > LOG_BUFFER_SIZE) {
        // 缓冲区满，刷新到文件
        flush_log_buffer();
    }
    
    // 添加到缓冲区
    memcpy(&log_buffer[log_buffer_pos], line, len);
    log_buffer_pos += len;
    
    // 定时刷新
    uint32_t now = HAL_GetTick();
    if (now - last_flush_time >= LOG_FLUSH_INTERVAL) {
        flush_log_buffer();
        last_flush_time = now;
    }
    
    return 0;
}

/**
 * @brief  刷新日志缓冲区
 */
int flush_log_buffer(void)
{
    if (log_buffer_pos == 0) {
        return 0;
    }
    
    UINT bytes_written;
    FRESULT res = f_write(&log_file, log_buffer, log_buffer_pos, &bytes_written);
    
    if (res != FR_OK || bytes_written < log_buffer_pos) {
        printf("Log flush failed\n");
        return -1;
    }
    
    // 同步到磁盘
    f_sync(&log_file);
    
    log_buffer_pos = 0;
    
    return 0;
}

/**
 * @brief  停止数据记录
 */
int stop_data_logging(void)
{
    if (!logging_enabled) {
        return 0;
    }
    
    // 刷新剩余数据
    flush_log_buffer();
    
    // 关闭文件
    f_close(&log_file);
    
    logging_enabled = false;
    
    printf("Data logging stopped\n");
    
    return 0;
}

/**
 * @brief  数据记录任务（定时调用）
 */
void data_logging_task(void)
{
    static uint32_t last_log_time = 0;
    uint32_t now = HAL_GetTick();
    
    // 每秒记录一次
    if (now - last_log_time >= 1000) {
        sensor_data_t data;
        
        // 读取传感器数据
        data.timestamp = now;
        data.temperature = read_temperature();
        data.humidity = read_humidity();
        data.pressure = read_pressure();
        
        // 记录数据
        log_sensor_data(&data);
        
        last_log_time = now;
    }
}
```


### 8.2 固件更新系统

```c
/**
 * @brief  从SD卡更新固件
 */

#define FIRMWARE_FILE       "0:/firmware.bin"
#define FLASH_APP_ADDR      0x08010000  // 应用程序起始地址
#define FLASH_APP_SIZE      (128 * 1024) // 应用程序大小

/**
 * @brief  检查固件文件
 */
int check_firmware_file(uint32_t *file_size)
{
    FILINFO fno;
    FRESULT res;
    
    // 获取文件信息
    res = f_stat(FIRMWARE_FILE, &fno);
    if (res != FR_OK) {
        printf("Firmware file not found\n");
        return -1;
    }
    
    // 检查文件大小
    if (fno.fsize == 0 || fno.fsize > FLASH_APP_SIZE) {
        printf("Invalid firmware size: %lu\n", fno.fsize);
        return -1;
    }
    
    *file_size = fno.fsize;
    
    printf("Firmware file found: %lu bytes\n", fno.fsize);
    
    return 0;
}

/**
 * @brief  执行固件更新
 */
int perform_firmware_update(void)
{
    FIL file;
    FRESULT res;
    UINT bytes_read;
    uint8_t buffer[1024];
    uint32_t file_size;
    uint32_t bytes_programmed = 0;
    uint32_t flash_addr = FLASH_APP_ADDR;
    
    // 检查固件文件
    if (check_firmware_file(&file_size) != 0) {
        return -1;
    }
    
    // 打开固件文件
    res = f_open(&file, FIRMWARE_FILE, FA_READ);
    if (res != FR_OK) {
        printf("Failed to open firmware file\n");
        return -1;
    }
    
    printf("Starting firmware update...\n");
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 擦除应用程序区域
    printf("Erasing flash...\n");
    FLASH_EraseInitTypeDef erase_init;
    uint32_t page_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_PAGES;
    erase_init.PageAddress = FLASH_APP_ADDR;
    erase_init.NbPages = FLASH_APP_SIZE / FLASH_PAGE_SIZE;
    
    if (HAL_FLASHEx_Erase(&erase_init, &page_error) != HAL_OK) {
        printf("Flash erase failed\n");
        f_close(&file);
        HAL_FLASH_Lock();
        return -1;
    }
    
    // 编程Flash
    printf("Programming flash...\n");
    
    while (bytes_programmed < file_size) {
        // 读取数据
        res = f_read(&file, buffer, sizeof(buffer), &bytes_read);
        if (res != FR_OK) {
            printf("Read error\n");
            break;
        }
        
        if (bytes_read == 0) {
            break;
        }
        
        // 写入Flash
        for (uint32_t i = 0; i < bytes_read; i += 4) {
            uint32_t data = *(uint32_t*)&buffer[i];
            
            if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, flash_addr, data) != HAL_OK) {
                printf("Flash program failed at 0x%08lX\n", flash_addr);
                f_close(&file);
                HAL_FLASH_Lock();
                return -1;
            }
            
            flash_addr += 4;
        }
        
        bytes_programmed += bytes_read;
        
        // 显示进度
        printf("\rProgress: %lu%%", bytes_programmed * 100 / file_size);
    }
    
    printf("\n");
    
    // 关闭文件
    f_close(&file);
    
    // 锁定Flash
    HAL_FLASH_Lock();
    
    // 验证固件
    printf("Verifying firmware...\n");
    if (verify_firmware(file_size) != 0) {
        printf("Firmware verification failed\n");
        return -1;
    }
    
    printf("Firmware update completed successfully\n");
    
    return 0;
}

/**
 * @brief  验证固件
 */
int verify_firmware(uint32_t size)
{
    FIL file;
    FRESULT res;
    UINT bytes_read;
    uint8_t file_buffer[256];
    uint8_t *flash_ptr = (uint8_t*)FLASH_APP_ADDR;
    uint32_t bytes_verified = 0;
    
    // 打开固件文件
    res = f_open(&file, FIRMWARE_FILE, FA_READ);
    if (res != FR_OK) {
        return -1;
    }
    
    // 逐块比较
    while (bytes_verified < size) {
        res = f_read(&file, file_buffer, sizeof(file_buffer), &bytes_read);
        if (res != FR_OK || bytes_read == 0) {
            break;
        }
        
        // 比较数据
        if (memcmp(file_buffer, flash_ptr, bytes_read) != 0) {
            printf("Verification failed at offset %lu\n", bytes_verified);
            f_close(&file);
            return -1;
        }
        
        flash_ptr += bytes_read;
        bytes_verified += bytes_read;
    }
    
    f_close(&file);
    
    return 0;
}

/**
 * @brief  跳转到应用程序
 */
void jump_to_application(void)
{
    uint32_t app_stack = *(volatile uint32_t*)FLASH_APP_ADDR;
    uint32_t app_entry = *(volatile uint32_t*)(FLASH_APP_ADDR + 4);
    
    // 检查栈指针有效性
    if ((app_stack & 0x2FFE0000) != 0x20000000) {
        printf("Invalid application\n");
        return;
    }
    
    printf("Jumping to application...\n");
    
    // 关闭所有外设
    HAL_DeInit();
    
    // 禁用中断
    __disable_irq();
    
    // 设置栈指针
    __set_MSP(app_stack);
    
    // 跳转到应用程序
    void (*app_reset_handler)(void) = (void*)app_entry;
    app_reset_handler();
}
```

### 8.3 文件浏览器

```c
/**
 * @brief  简单的文件浏览器
 */

/**
 * @brief  递归列出目录内容
 */
int list_directory_recursive(const char *path, int level)
{
    DIR dir;
    FILINFO fno;
    FRESULT res;
    char full_path[256];
    
    // 打开目录
    res = f_opendir(&dir, path);
    if (res != FR_OK) {
        return -1;
    }
    
    // 遍历目录
    while (1) {
        res = f_readdir(&dir, &fno);
        if (res != FR_OK || fno.fname[0] == 0) {
            break;
        }
        
        // 跳过 "." 和 ".."
        if (strcmp(fno.fname, ".") == 0 || strcmp(fno.fname, "..") == 0) {
            continue;
        }
        
        // 打印缩进
        for (int i = 0; i < level; i++) {
            printf("  ");
        }
        
        // 打印文件/目录信息
        if (fno.fattrib & AM_DIR) {
            printf("[DIR]  %s\n", fno.fname);
            
            // 递归列出子目录
            snprintf(full_path, sizeof(full_path), "%s/%s", path, fno.fname);
            list_directory_recursive(full_path, level + 1);
        } else {
            printf("[FILE] %s (%lu bytes)\n", fno.fname, fno.fsize);
        }
    }
    
    f_closedir(&dir);
    
    return 0;
}

/**
 * @brief  计算目录大小
 */
uint32_t calculate_directory_size(const char *path)
{
    DIR dir;
    FILINFO fno;
    FRESULT res;
    uint32_t total_size = 0;
    char full_path[256];
    
    res = f_opendir(&dir, path);
    if (res != FR_OK) {
        return 0;
    }
    
    while (1) {
        res = f_readdir(&dir, &fno);
        if (res != FR_OK || fno.fname[0] == 0) {
            break;
        }
        
        if (fno.fattrib & AM_DIR) {
            // 递归计算子目录大小
            snprintf(full_path, sizeof(full_path), "%s/%s", path, fno.fname);
            total_size += calculate_directory_size(full_path);
        } else {
            total_size += fno.fsize;
        }
    }
    
    f_closedir(&dir);
    
    return total_size;
}

/**
 * @brief  获取磁盘空间信息
 */
int get_disk_space_info(void)
{
    FATFS *fs;
    DWORD free_clusters;
    FRESULT res;
    
    // 获取空闲簇数量
    res = f_getfree("0:", &free_clusters, &fs);
    if (res != FR_OK) {
        printf("Get free space failed: %s\n", fresult_to_string(res));
        return -1;
    }
    
    // 计算空间信息
    uint32_t total_sectors = (fs->n_fatent - 2) * fs->csize;
    uint32_t free_sectors = free_clusters * fs->csize;
    
    uint32_t total_kb = total_sectors / 2;  // 假设512字节扇区
    uint32_t free_kb = free_sectors / 2;
    uint32_t used_kb = total_kb - free_kb;
    
    printf("Disk Space Information:\n");
    printf("  Total: %lu KB (%.2f MB)\n", total_kb, total_kb / 1024.0);
    printf("  Used:  %lu KB (%.2f MB)\n", used_kb, used_kb / 1024.0);
    printf("  Free:  %lu KB (%.2f MB)\n", free_kb, free_kb / 1024.0);
    printf("  Usage: %.1f%%\n", used_kb * 100.0 / total_kb);
    
    return 0;
}
```

## 第九部分：故障排除

### 9.1 常见问题

**问题1：SD卡初始化失败**

```
症状：sd_init()返回错误

可能原因：
1. 硬件连接问题
   - 检查引脚连接
   - 检查电源电压（3.3V）
   - 检查上拉电阻

2. 时钟频率过高
   - 初始化时使用≤400kHz
   - 检查SPI时钟配置

3. SD卡不兼容
   - 尝试不同品牌的SD卡
   - 检查卡类型（SD/SDHC/SDXC）

4. 时序问题
   - 增加上电延迟
   - 增加命令响应超时

解决方法：
- 使用示波器检查信号
- 添加调试输出
- 尝试降低时钟频率
```

**问题2：文件系统挂载失败**

```
症状：f_mount()返回FR_NO_FILESYSTEM

可能原因：
1. SD卡未格式化
   - 使用电脑格式化为FAT32
   - 或使用f_mkfs()格式化

2. 分区表损坏
   - 重新格式化SD卡
   - 检查MBR

3. 扇区读取错误
   - 检查diskio.c实现
   - 验证扇区读取功能

解决方法：
// 格式化SD卡
FRESULT res;
BYTE work[FF_MAX_SS];

res = f_mkfs("0:", FM_FAT32, 0, work, sizeof(work));
if (res == FR_OK) {
    printf("Format successful\n");
}
```

**问题3：写入速度慢**

```
症状：写入速度<100KB/s

可能原因：
1. 使用SPI模式
   - 切换到SDIO模式

2. 单字节写入
   - 使用缓冲区批量写入
   - 增大写入块大小

3. 频繁同步
   - 减少f_sync()调用频率
   - 使用缓存

4. 低速SD卡
   - 使用Class 10或更高速卡

优化方法：
- 使用DMA传输
- 多扇区读写
- 预分配文件空间
```

### 9.2 调试技巧

```c
/**
 * @brief  SD卡诊断工具
 */
void sd_diagnostic(void)
{
    printf("\n=== SD Card Diagnostic ===\n\n");
    
    // 1. 检查卡是否存在
    printf("1. Card Detection: ");
    if (sd_is_present()) {
        printf("PASS\n");
    } else {
        printf("FAIL - No card detected\n");
        return;
    }
    
    // 2. 初始化测试
    printf("2. Initialization: ");
    if (sd_init() == 0) {
        printf("PASS\n");
    } else {
        printf("FAIL\n");
        return;
    }
    
    // 3. 读取卡信息
    printf("3. Card Information:\n");
    const sd_card_info_t *info = sd_get_info();
    printf("   Type: ");
    switch (info->type) {
        case SD_TYPE_V1:   printf("SD V1.x\n"); break;
        case SD_TYPE_V2:   printf("SD V2.0\n"); break;
        case SD_TYPE_V2HC: printf("SDHC\n"); break;
        default:           printf("Unknown\n"); break;
    }
    printf("   Capacity: %lu MB\n", info->capacity / (1024 * 1024));
    printf("   Block Size: %u bytes\n", info->block_size);
    printf("   Block Count: %lu\n", info->block_count);
    
    // 4. 读取测试
    printf("4. Read Test: ");
    uint8_t buffer[512];
    if (sd_read_block(0, buffer) == 0) {
        printf("PASS\n");
    } else {
        printf("FAIL\n");
    }
    
    // 5. 写入测试（如果未写保护）
    printf("5. Write Test: ");
    if (sd_is_write_protected()) {
        printf("SKIP - Write protected\n");
    } else {
        // 写入测试数据
        for (int i = 0; i < 512; i++) {
            buffer[i] = i & 0xFF;
        }
        
        if (sd_write_block(1000, buffer) == 0) {
            // 读回验证
            uint8_t verify_buffer[512];
            sd_read_block(1000, verify_buffer);
            
            if (memcmp(buffer, verify_buffer, 512) == 0) {
                printf("PASS\n");
            } else {
                printf("FAIL - Verification error\n");
            }
        } else {
            printf("FAIL - Write error\n");
        }
    }
    
    // 6. 文件系统测试
    printf("6. Filesystem Test: ");
    FATFS fs;
    if (f_mount(&fs, "0:", 1) == FR_OK) {
        printf("PASS\n");
        
        // 显示磁盘空间
        get_disk_space_info();
    } else {
        printf("FAIL\n");
    }
    
    printf("\n=== Diagnostic Complete ===\n\n");
}
```

## 第十部分：最佳实践

### 10.1 设计建议

```
1. 硬件设计
   ✓ 使用3.3V电平
   ✓ 添加上拉电阻（10kΩ-47kΩ）
   ✓ 添加去耦电容（0.1μF + 10μF）
   ✓ 使用短连线（<10cm）
   ✓ 添加ESD保护
   ✓ 考虑热插拔保护

2. 软件设计
   ✓ 实现卡检测
   ✓ 处理热插拔
   ✓ 定期同步数据
   ✓ 实现错误恢复
   ✓ 使用缓冲区
   ✓ 添加日志记录

3. 性能优化
   ✓ 使用SDIO而非SPI
   ✓ 启用DMA传输
   ✓ 多扇区读写
   ✓ 减少碎片化
   ✓ 预分配文件空间
   ✓ 使用快速定位

4. 可靠性
   ✓ 实现掉电保护
   ✓ 使用CRC校验
   ✓ 定期备份重要数据
   ✓ 监控磨损
   ✓ 实现故障恢复
```

### 10.2 代码规范

```c
/**
 * @brief  推荐的文件操作模式
 */

// 1. 始终检查返回值
FRESULT res = f_open(&file, "test.txt", FA_READ);
if (res != FR_OK) {
    // 处理错误
}

// 2. 使用RAII模式（资源获取即初始化）
int safe_file_read(const char *path, void *buffer, size_t size)
{
    FIL file;
    FRESULT res;
    UINT bytes_read;
    int result = -1;
    
    res = f_open(&file, path, FA_READ);
    if (res != FR_OK) {
        goto cleanup;
    }
    
    res = f_read(&file, buffer, size, &bytes_read);
    if (res != FR_OK) {
        goto cleanup;
    }
    
    result = bytes_read;
    
cleanup:
    if (file.obj.fs) {  // 文件已打开
        f_close(&file);
    }
    
    return result;
}

// 3. 使用宏简化错误处理
#define CHECK_FRESULT(expr) \
    do { \
        FRESULT _res = (expr); \
        if (_res != FR_OK) { \
            printf("Error at %s:%d: %s\n", __FILE__, __LINE__, \
                   fresult_to_string(_res)); \
            return -1; \
        } \
    } while(0)

// 使用示例
int example_with_macro(void)
{
    FIL file;
    
    CHECK_FRESULT(f_open(&file, "test.txt", FA_READ));
    CHECK_FRESULT(f_read(&file, buffer, size, &bytes_read));
    CHECK_FRESULT(f_close(&file));
    
    return 0;
}
```

## 总结

### 关键要点

1. **SD卡接口**
   - SPI模式简单但速度慢（≤25MHz）
   - SDIO模式复杂但速度快（≤50MHz）
   - 初始化时使用低速时钟（≤400kHz）

2. **FAT文件系统**
   - FAT32适用于大多数SD卡
   - 理解簇、扇区、FAT表的概念
   - 掌握目录项结构

3. **FatFs库**
   - 功能完整、易于移植
   - 需要实现diskio.c接口
   - 配置ffconf.h以优化功能和大小

4. **性能优化**
   - 使用缓冲区批量读写
   - 启用DMA传输
   - 多扇区操作
   - 减少同步频率

5. **可靠性**
   - 实现卡检测和热插拔处理
   - 添加错误处理和恢复机制
   - 定期同步数据
   - 使用CRC校验

### 学习路径

1. **入门阶段**
   - 理解SD卡基础知识
   - 实现SPI接口驱动
   - 使用FatFs库进行基本文件操作

2. **进阶阶段**
   - 实现SDIO接口驱动
   - 理解FAT文件系统原理
   - 优化读写性能

3. **高级阶段**
   - 实现数据记录系统
   - 实现固件更新功能
   - 处理复杂的错误场景

### 下一步学习

- [Flash文件系统](../../01-file-systems/intermediate/02-flash-filesystem.html) - 学习Flash上的文件系统
- [磨损均衡算法](01-wear-leveling.html) - 了解存储器寿命管理
- [数据持久化](02-data-persistence.html) - 掌握数据可靠性技术

## 参考资料

1. **SD卡规范**
   - SD Physical Layer Simplified Specification
   - SD Card Association官方文档

2. **FatFs文档**
   - FatFs官方网站：http://elm-chan.org/fsw/ff/
   - FatFs应用笔记

3. **相关标准**
   - FAT32文件系统规范
   - SPI总线规范
   - SDIO接口规范

4. **开源项目**
   - STM32 SD卡示例
   - ESP32 SD卡驱动
   - Arduino SD库

## 相关主题

- [Flash存储技术](../beginner/01-flash-technology.html)
- [EEPROM存储](../beginner/02-eeprom-storage.html)
- [LittleFS文件系统](../../01-file-systems/beginner/02-littlefs.html)
- [SPI驱动开发](../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-spi-driver.html)

---

*本文档持续更新中，最后更新时间：2026-04-05*
