---
title: "SD卡存储应用开发：大容量数据记录与文件管理实战"
description: "全面学习SD卡存储技术，掌握SDIO接口、FAT文件系统、数据记录和大容量存储应用开发方法"
slug: "sd-card-storage"

# 分类信息
domain: "中间件层"
module: "存储技术"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - SD卡
  - SDIO
  - 大容量存储
  - FAT文件系统
  - 数据记录
prerequisites:
  - "01-hardware-layer/01-chip-architecture/beginner/01-mcu-basics"
  - "02-driver-bsp-layer/02-device-driver-development/beginner/01-gpio-basics"
related_contents:
  - "04-middleware-layer/02-storage-technology/beginner/01-flash-technology"
  - "04-middleware-layer/01-file-systems/beginner/01-fat-filesystem"
  - "04-middleware-layer/02-storage-technology/beginner/02-eeprom-storage"

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
  - SD卡存储
  - SDIO接口
  - FAT文件系统
  - 数据记录
  - 大容量存储
  - microSD卡
cover_image: ""
---

# SD卡存储应用开发：大容量数据记录与文件管理实战

## 学习目标

完成本教程后，你将能够：

- [ ] 理解SD卡的工作原理和技术规范
- [ ] 掌握SDIO和SPI接口的使用方法
- [ ] 学会初始化和配置SD卡
- [ ] 掌握FAT文件系统的基本操作
- [ ] 实现数据记录和文件管理功能
- [ ] 了解SD卡的性能优化技巧
- [ ] 能够设计可靠的大容量存储方案

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解C语言基础编程
- 熟悉SPI或SDIO通信协议
- 了解文件系统基本概念
- 掌握MCU的基本使用

**技能要求**：
- 能够使用开发环境编写和调试代码
- 会使用示波器或逻辑分析仪（可选）
- 能够阅读芯片数据手册和SD卡规范


## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | 支持SDIO或SPI | STM32F4/ESP32 |
| SD卡模块 | 1 | 带电平转换 | microSD卡座模块 |
| microSD卡 | 1 | 容量2GB-32GB | Class 10推荐 |
| 杜邦线 | 若干 | - | - |

### 软件准备

- **开发环境**：STM32CubeIDE / Arduino IDE / ESP-IDF
- **文件系统库**：FatFs / SD库
- **辅助工具**：串口调试助手、SD卡格式化工具

### 环境配置

1. 安装开发环境和相关库
2. 配置SDIO或SPI外设
3. 准备SD卡（FAT32格式）

## 背景知识

### 什么是SD卡

SD卡（Secure Digital Card）是一种基于半导体闪存的存储卡，广泛应用于便携式设备中。

**核心特性**：
- **大容量**：从几MB到几TB
- **非易失性**：断电后数据不丢失
- **标准接口**：SDIO或SPI
- **文件系统**：通常使用FAT32或exFAT
- **热插拔**：支持在线插拔

**SD卡类型**：

| 类型 | 容量范围 | 文件系统 | 应用 |
|------|---------|---------|------|
| SD | 最大2GB | FAT16 | 老旧设备 |
| SDHC | 2GB-32GB | FAT32 | 常用 |
| SDXC | 32GB-2TB | exFAT | 大容量 |
| SDUC | 2TB-128TB | exFAT | 未来 |


### SD卡速度等级

**速度等级标识**：

```
Class 2:  最低2MB/s   (适合标清视频)
Class 4:  最低4MB/s   (适合高清视频)
Class 6:  最低6MB/s   (适合全高清视频)
Class 10: 最低10MB/s  (适合全高清录制)

UHS Speed Class:
U1: 最低10MB/s
U3: 最低30MB/s

Video Speed Class:
V6:  最低6MB/s
V10: 最低10MB/s
V30: 最低30MB/s
V60: 最低60MB/s
V90: 最低90MB/s
```

### SD卡工作原理

SD卡内部结构：

```
┌─────────────────────────────────┐
│         SD卡芯片                 │
│  ┌──────────────────────────┐  │
│  │   控制器                  │  │
│  │  - 命令处理               │  │
│  │  - 数据传输               │  │
│  │  - 错误校正(ECC)          │  │
│  │  - 磨损均衡               │  │
│  └──────────────────────────┘  │
│              ↕                   │
│  ┌──────────────────────────┐  │
│  │   NAND Flash存储阵列      │  │
│  │   (MLC/TLC)               │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
         ↕ (SDIO/SPI接口)
    ┌─────────────┐
    │   主控MCU    │
    └─────────────┘
```

**数据组织**：
- **块（Block）**：512字节，最小读写单位
- **扇区（Sector）**：通常等于块
- **簇（Cluster）**：文件系统分配单位，由多个块组成


### SDIO vs SPI接口

**接口对比**：

| 特性 | SDIO | SPI |
|------|------|-----|
| 数据线 | 1/4/8线 | 1线 |
| 时钟频率 | 最高208MHz | 最高25MHz |
| 传输速度 | 最高104MB/s | 最高3MB/s |
| 引脚数 | 6-10个 | 4个 |
| 硬件要求 | 需要SDIO控制器 | 标准SPI即可 |
| 实现难度 | 较复杂 | 简单 |
| 应用场景 | 高性能应用 | 简单应用 |

**SDIO引脚定义**：

```
SD卡引脚（9针）：
1. DAT2    - 数据线2
2. DAT3/CS - 数据线3/片选
3. CMD     - 命令线
4. VDD     - 电源(3.3V)
5. CLK     - 时钟
6. VSS     - 地
7. DAT0    - 数据线0
8. DAT1    - 数据线1
9. CD      - 卡检测（可选）
```

**SPI模式引脚映射**：

```
SD卡引脚    SPI信号
DAT3/CS  →  CS   (片选)
CMD      →  MOSI (主出从入)
DAT0     →  MISO (主入从出)
CLK      →  SCK  (时钟)
```


## 电路连接

### SDIO模式连接（STM32）

```
STM32F4                    SD卡模块
                          ┌─────────┐
  PC8  ────────────────►  DAT0      │
  PC9  ────────────────►  DAT1      │
  PC10 ────────────────►  DAT2      │
  PC11 ────────────────►  DAT3/CS   │
  PC12 ────────────────►  CLK       │
  PD2  ────────────────►  CMD       │
  3.3V ────────────────►  VDD       │
  GND  ────────────────►  GND       │
                          └─────────┘
```

**注意事项**：
- SDIO信号需要上拉电阻（10kΩ-47kΩ）
- 时钟线可以不上拉
- 确保电源稳定（3.3V）
- 数据线长度尽量短

### SPI模式连接（Arduino/ESP32）

```
Arduino/ESP32             SD卡模块
                          ┌─────────┐
  D13/SCK  ────────────►  CLK       │
  D11/MOSI ────────────►  CMD/MOSI  │
  D12/MISO ◄────────────  DAT0/MISO │
  D10/CS   ────────────►  DAT3/CS   │
  5V/3.3V  ────────────►  VDD       │
  GND      ────────────►  GND       │
                          └─────────┘
```

**电平转换**：
- 如果MCU是5V，SD卡是3.3V，需要电平转换
- 使用专用的SD卡模块（内置电平转换）
- 或使用电平转换芯片（如74LVC245）


## 步骤1：SD卡初始化（SPI模式）

### 1.1 Arduino SD库初始化

```cpp
#include <SPI.h>
#include <SD.h>

// SD卡片选引脚
const int chipSelect = 10;

void setup() {
    // 初始化串口
    Serial.begin(9600);
    while (!Serial) {
        ; // 等待串口连接
    }
    
    Serial.println("Initializing SD card...");
    
    // 初始化SD卡
    if (!SD.begin(chipSelect)) {
        Serial.println("SD card initialization failed!");
        Serial.println("Check:");
        Serial.println("  - Card is inserted");
        Serial.println("  - Wiring is correct");
        Serial.println("  - Card is formatted (FAT32)");
        return;
    }
    
    Serial.println("SD card initialized successfully!");
    
    // 获取卡信息
    printCardInfo();
}

void printCardInfo() {
    Serial.println("\n=== SD Card Information ===");
    
    // 卡类型
    Serial.print("Card type: ");
    switch (SD.type()) {
        case SD_CARD_TYPE_SD1:
            Serial.println("SD1");
            break;
        case SD_CARD_TYPE_SD2:
            Serial.println("SD2");
            break;
        case SD_CARD_TYPE_SDHC:
            Serial.println("SDHC");
            break;
        default:
            Serial.println("Unknown");
    }
    
    // 卡容量
    uint64_t cardSize = SD.cardSize() / (1024 * 1024);
    Serial.print("Card size: ");
    Serial.print(cardSize);
    Serial.println(" MB");
    
    // 可用空间
    uint64_t totalBytes = SD.totalBytes() / (1024 * 1024);
    uint64_t usedBytes = SD.usedBytes() / (1024 * 1024);
    Serial.print("Total space: ");
    Serial.print(totalBytes);
    Serial.println(" MB");
    Serial.print("Used space: ");
    Serial.print(usedBytes);
    Serial.println(" MB");
    
    Serial.println("===========================\n");
}
```


### 1.2 STM32 HAL库初始化（SDIO模式）

```c
#include "stm32f4xx_hal.h"
#include "fatfs.h"

SD_HandleTypeDef hsd;
FATFS SDFatFs;  // 文件系统对象
FIL MyFile;     // 文件对象
char SDPath[4]; // SD卡逻辑驱动器路径

/**
 * @brief  SDIO初始化
 */
void SDIO_Init(void) {
    // SDIO配置
    hsd.Instance = SDIO;
    hsd.Init.ClockEdge = SDIO_CLOCK_EDGE_RISING;
    hsd.Init.ClockBypass = SDIO_CLOCK_BYPASS_DISABLE;
    hsd.Init.ClockPowerSave = SDIO_CLOCK_POWER_SAVE_DISABLE;
    hsd.Init.BusWide = SDIO_BUS_WIDE_1B;  // 先用1位模式初始化
    hsd.Init.HardwareFlowControl = SDIO_HARDWARE_FLOW_CONTROL_DISABLE;
    hsd.Init.ClockDiv = 0;
    
    // 初始化SDIO
    if (HAL_SD_Init(&hsd) != HAL_OK) {
        Error_Handler();
    }
    
    // 切换到4位模式（提高速度）
    if (HAL_SD_ConfigWideBusOperation(&hsd, SDIO_BUS_WIDE_4B) != HAL_OK) {
        Error_Handler();
    }
}

/**
 * @brief  挂载文件系统
 */
uint8_t SD_Mount(void) {
    FRESULT res;
    
    // 链接驱动器
    if (FATFS_LinkDriver(&SD_Driver, SDPath) != 0) {
        return 1;
    }
    
    // 挂载文件系统
    res = f_mount(&SDFatFs, (TCHAR const*)SDPath, 1);
    if (res != FR_OK) {
        printf("Failed to mount SD card: %d\n", res);
        return 1;
    }
    
    printf("SD card mounted successfully\n");
    return 0;
}

/**
 * @brief  获取SD卡信息
 */
void SD_GetCardInfo(void) {
    HAL_SD_CardInfoTypeDef cardInfo;
    
    if (HAL_SD_GetCardInfo(&hsd, &cardInfo) == HAL_OK) {
        printf("\n=== SD Card Information ===\n");
        printf("Card Type: ");
        switch (cardInfo.CardType) {
            case CARD_SDSC:
                printf("SDSC (Standard Capacity)\n");
                break;
            case CARD_SDHC_SDXC:
                printf("SDHC/SDXC (High/Extended Capacity)\n");
                break;
            default:
                printf("Unknown\n");
        }
        
        printf("Card Version: %d\n", cardInfo.CardVersion);
        printf("Class: %d\n", cardInfo.Class);
        printf("Relative Card Address: 0x%08X\n", cardInfo.RelCardAdd);
        printf("Block Number: %lu\n", cardInfo.BlockNbr);
        printf("Block Size: %lu bytes\n", cardInfo.BlockSize);
        
        uint64_t capacity = (uint64_t)cardInfo.BlockNbr * cardInfo.BlockSize;
        printf("Capacity: %llu MB\n", capacity / (1024 * 1024));
        printf("===========================\n\n");
    }
}
```


## 步骤2：文件基本操作

### 2.1 创建和写入文件（Arduino）

```cpp
/**
 * @brief  创建文件并写入数据
 */
void createAndWriteFile() {
    Serial.println("Creating file...");
    
    // 打开文件（如果不存在则创建）
    File myFile = SD.open("test.txt", FILE_WRITE);
    
    if (myFile) {
        Serial.println("Writing to test.txt...");
        
        // 写入数据
        myFile.println("Hello, SD Card!");
        myFile.println("This is a test file.");
        myFile.print("Timestamp: ");
        myFile.println(millis());
        
        // 关闭文件
        myFile.close();
        Serial.println("Write complete!");
    } else {
        Serial.println("Error opening test.txt for writing");
    }
}

/**
 * @brief  追加数据到文件
 */
void appendToFile(const char* filename, const char* data) {
    // 以追加模式打开文件
    File myFile = SD.open(filename, FILE_WRITE);
    
    if (myFile) {
        // 移动到文件末尾
        myFile.seek(myFile.size());
        
        // 追加数据
        myFile.println(data);
        
        myFile.close();
        Serial.println("Data appended successfully");
    } else {
        Serial.println("Error opening file for appending");
    }
}
```

### 2.2 读取文件（Arduino）

```cpp
/**
 * @brief  读取文件内容
 */
void readFile(const char* filename) {
    Serial.print("Reading from ");
    Serial.println(filename);
    
    // 打开文件读取
    File myFile = SD.open(filename);
    
    if (myFile) {
        Serial.println("File content:");
        Serial.println("-------------------");
        
        // 逐字符读取并打印
        while (myFile.available()) {
            Serial.write(myFile.read());
        }
        
        Serial.println("\n-------------------");
        
        // 关闭文件
        myFile.close();
    } else {
        Serial.println("Error opening file for reading");
    }
}

/**
 * @brief  按行读取文件
 */
void readFileByLine(const char* filename) {
    File myFile = SD.open(filename);
    
    if (myFile) {
        int lineNumber = 1;
        
        while (myFile.available()) {
            String line = myFile.readStringUntil('\n');
            Serial.print("Line ");
            Serial.print(lineNumber++);
            Serial.print(": ");
            Serial.println(line);
        }
        
        myFile.close();
    } else {
        Serial.println("Error opening file");
    }
}
```


### 2.3 文件操作（STM32 FatFs）

```c
/**
 * @brief  创建文件并写入数据
 */
uint8_t SD_WriteFile(const char* filename, const char* data) {
    FRESULT res;
    UINT bytesWritten;
    
    // 打开文件（创建或覆盖）
    res = f_open(&MyFile, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to open file for writing: %d\n", res);
        return 1;
    }
    
    // 写入数据
    res = f_write(&MyFile, data, strlen(data), &bytesWritten);
    if (res != FR_OK) {
        printf("Failed to write file: %d\n", res);
        f_close(&MyFile);
        return 1;
    }
    
    printf("Wrote %u bytes to %s\n", bytesWritten, filename);
    
    // 关闭文件
    f_close(&MyFile);
    return 0;
}

/**
 * @brief  追加数据到文件
 */
uint8_t SD_AppendFile(const char* filename, const char* data) {
    FRESULT res;
    UINT bytesWritten;
    
    // 打开文件（追加模式）
    res = f_open(&MyFile, filename, FA_OPEN_APPEND | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to open file for appending: %d\n", res);
        return 1;
    }
    
    // 写入数据
    res = f_write(&MyFile, data, strlen(data), &bytesWritten);
    if (res != FR_OK) {
        printf("Failed to append file: %d\n", res);
        f_close(&MyFile);
        return 1;
    }
    
    printf("Appended %u bytes to %s\n", bytesWritten, filename);
    
    // 关闭文件
    f_close(&MyFile);
    return 0;
}

/**
 * @brief  读取文件内容
 */
uint8_t SD_ReadFile(const char* filename, char* buffer, uint32_t bufferSize) {
    FRESULT res;
    UINT bytesRead;
    
    // 打开文件读取
    res = f_open(&MyFile, filename, FA_READ);
    if (res != FR_OK) {
        printf("Failed to open file for reading: %d\n", res);
        return 1;
    }
    
    // 读取数据
    res = f_read(&MyFile, buffer, bufferSize - 1, &bytesRead);
    if (res != FR_OK) {
        printf("Failed to read file: %d\n", res);
        f_close(&MyFile);
        return 1;
    }
    
    buffer[bytesRead] = '\0';  // 添加字符串结束符
    printf("Read %u bytes from %s\n", bytesRead, filename);
    
    // 关闭文件
    f_close(&MyFile);
    return 0;
}
```


## 步骤3：目录操作

### 3.1 列出目录内容（Arduino）

```cpp
/**
 * @brief  列出根目录内容
 */
void listDirectory() {
    Serial.println("Files in root directory:");
    Serial.println("-------------------");
    
    File root = SD.open("/");
    printDirectory(root, 0);
    root.close();
    
    Serial.println("-------------------");
}

/**
 * @brief  递归打印目录内容
 */
void printDirectory(File dir, int numTabs) {
    while (true) {
        File entry = dir.openNextFile();
        if (!entry) {
            break;  // 没有更多文件
        }
        
        // 打印缩进
        for (uint8_t i = 0; i < numTabs; i++) {
            Serial.print('\t');
        }
        
        // 打印文件名
        Serial.print(entry.name());
        
        if (entry.isDirectory()) {
            Serial.println("/");
            // 递归打印子目录
            printDirectory(entry, numTabs + 1);
        } else {
            // 打印文件大小
            Serial.print("\t\t");
            Serial.print(entry.size(), DEC);
            Serial.println(" bytes");
        }
        
        entry.close();
    }
}

/**
 * @brief  创建目录
 */
void createDirectory(const char* dirname) {
    if (SD.mkdir(dirname)) {
        Serial.print("Directory created: ");
        Serial.println(dirname);
    } else {
        Serial.print("Failed to create directory: ");
        Serial.println(dirname);
    }
}

/**
 * @brief  删除目录
 */
void removeDirectory(const char* dirname) {
    if (SD.rmdir(dirname)) {
        Serial.print("Directory removed: ");
        Serial.println(dirname);
    } else {
        Serial.print("Failed to remove directory: ");
        Serial.println(dirname);
    }
}
```


### 3.2 目录操作（STM32 FatFs）

```c
/**
 * @brief  列出目录内容
 */
void SD_ListDirectory(const char* path) {
    FRESULT res;
    DIR dir;
    FILINFO fno;
    
    printf("Directory listing of %s:\n", path);
    printf("-------------------\n");
    
    // 打开目录
    res = f_opendir(&dir, path);
    if (res != FR_OK) {
        printf("Failed to open directory: %d\n", res);
        return;
    }
    
    // 读取目录项
    while (1) {
        res = f_readdir(&dir, &fno);
        if (res != FR_OK || fno.fname[0] == 0) {
            break;  // 错误或到达目录末尾
        }
        
        // 打印文件信息
        if (fno.fattrib & AM_DIR) {
            // 目录
            printf("[DIR]  %s\n", fno.fname);
        } else {
            // 文件
            printf("[FILE] %s\t%lu bytes\n", fno.fname, fno.fsize);
        }
    }
    
    printf("-------------------\n");
    
    // 关闭目录
    f_closedir(&dir);
}

/**
 * @brief  创建目录
 */
uint8_t SD_CreateDirectory(const char* dirname) {
    FRESULT res;
    
    res = f_mkdir(dirname);
    if (res == FR_OK) {
        printf("Directory created: %s\n", dirname);
        return 0;
    } else if (res == FR_EXIST) {
        printf("Directory already exists: %s\n", dirname);
        return 0;
    } else {
        printf("Failed to create directory: %d\n", res);
        return 1;
    }
}

/**
 * @brief  删除文件或目录
 */
uint8_t SD_Delete(const char* path) {
    FRESULT res;
    
    res = f_unlink(path);
    if (res == FR_OK) {
        printf("Deleted: %s\n", path);
        return 0;
    } else {
        printf("Failed to delete: %d\n", res);
        return 1;
    }
}

/**
 * @brief  重命名文件或目录
 */
uint8_t SD_Rename(const char* oldname, const char* newname) {
    FRESULT res;
    
    res = f_rename(oldname, newname);
    if (res == FR_OK) {
        printf("Renamed %s to %s\n", oldname, newname);
        return 0;
    } else {
        printf("Failed to rename: %d\n", res);
        return 1;
    }
}
```


## 步骤4：数据记录应用

### 4.1 传感器数据记录器

```cpp
/**
 * @brief  传感器数据记录系统
 */
class DataLogger {
private:
    File logFile;
    String filename;
    unsigned long lastLogTime;
    unsigned int logInterval;  // 记录间隔（毫秒）
    
public:
    DataLogger(const char* fname, unsigned int interval = 1000) {
        filename = fname;
        logInterval = interval;
        lastLogTime = 0;
    }
    
    /**
     * @brief  初始化日志文件
     */
    bool begin() {
        // 创建日志目录
        if (!SD.exists("/logs")) {
            SD.mkdir("/logs");
        }
        
        // 创建带时间戳的文件名
        String fullPath = "/logs/" + filename;
        
        // 打开文件（追加模式）
        logFile = SD.open(fullPath.c_str(), FILE_WRITE);
        if (!logFile) {
            Serial.println("Failed to open log file");
            return false;
        }
        
        // 写入文件头
        logFile.println("Timestamp,Temperature,Humidity,Pressure");
        logFile.close();
        
        Serial.print("Log file created: ");
        Serial.println(fullPath);
        return true;
    }
    
    /**
     * @brief  记录数据
     */
    void log(float temperature, float humidity, float pressure) {
        unsigned long currentTime = millis();
        
        // 检查是否到达记录间隔
        if (currentTime - lastLogTime < logInterval) {
            return;
        }
        
        lastLogTime = currentTime;
        
        // 打开文件追加
        String fullPath = "/logs/" + filename;
        logFile = SD.open(fullPath.c_str(), FILE_WRITE);
        
        if (logFile) {
            // 写入数据（CSV格式）
            logFile.print(currentTime);
            logFile.print(",");
            logFile.print(temperature, 2);
            logFile.print(",");
            logFile.print(humidity, 2);
            logFile.print(",");
            logFile.println(pressure, 2);
            
            logFile.close();
            
            Serial.print("Logged: ");
            Serial.print(temperature);
            Serial.print("°C, ");
            Serial.print(humidity);
            Serial.print("%, ");
            Serial.print(pressure);
            Serial.println(" hPa");
        } else {
            Serial.println("Failed to open log file");
        }
    }
    
    /**
     * @brief  设置记录间隔
     */
    void setInterval(unsigned int interval) {
        logInterval = interval;
    }
};

// 使用示例
DataLogger logger("sensor_data.csv", 5000);  // 每5秒记录一次

void setup() {
    Serial.begin(9600);
    
    // 初始化SD卡
    if (!SD.begin(10)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    
    // 初始化数据记录器
    if (!logger.begin()) {
        Serial.println("Logger initialization failed!");
        return;
    }
    
    Serial.println("Data logger ready!");
}

void loop() {
    // 读取传感器数据（示例）
    float temperature = readTemperature();
    float humidity = readHumidity();
    float pressure = readPressure();
    
    // 记录数据
    logger.log(temperature, humidity, pressure);
    
    delay(100);
}
```


### 4.2 循环缓冲日志（STM32）

```c
/**
 * @brief  循环缓冲日志系统
 */
#define MAX_LOG_FILES 10
#define MAX_LOG_SIZE (1024 * 1024)  // 1MB per file

typedef struct {
    char base_filename[32];
    uint8_t current_file_index;
    uint32_t current_file_size;
    FIL file;
    uint8_t is_open;
} CircularLogger_t;

CircularLogger_t g_logger;

/**
 * @brief  初始化循环日志
 */
uint8_t CircularLogger_Init(const char* base_filename) {
    strcpy(g_logger.base_filename, base_filename);
    g_logger.current_file_index = 0;
    g_logger.current_file_size = 0;
    g_logger.is_open = 0;
    
    // 创建日志目录
    f_mkdir("logs");
    
    return 0;
}

/**
 * @brief  打开当前日志文件
 */
uint8_t CircularLogger_OpenFile(void) {
    char filename[64];
    FRESULT res;
    
    // 生成文件名：logs/data_0.log, logs/data_1.log, ...
    sprintf(filename, "logs/%s_%d.log", 
            g_logger.base_filename, 
            g_logger.current_file_index);
    
    // 打开文件（追加模式）
    res = f_open(&g_logger.file, filename, FA_OPEN_APPEND | FA_WRITE);
    if (res != FR_OK) {
        // 文件不存在，创建新文件
        res = f_open(&g_logger.file, filename, FA_CREATE_ALWAYS | FA_WRITE);
        if (res != FR_OK) {
            return 1;
        }
        g_logger.current_file_size = 0;
    } else {
        // 获取当前文件大小
        g_logger.current_file_size = f_size(&g_logger.file);
    }
    
    g_logger.is_open = 1;
    return 0;
}

/**
 * @brief  写入日志
 */
uint8_t CircularLogger_Write(const char* data) {
    FRESULT res;
    UINT bytesWritten;
    uint32_t data_len = strlen(data);
    
    // 检查是否需要切换文件
    if (g_logger.current_file_size + data_len > MAX_LOG_SIZE) {
        // 关闭当前文件
        if (g_logger.is_open) {
            f_close(&g_logger.file);
            g_logger.is_open = 0;
        }
        
        // 切换到下一个文件
        g_logger.current_file_index = (g_logger.current_file_index + 1) % MAX_LOG_FILES;
        g_logger.current_file_size = 0;
        
        printf("Switching to log file %d\n", g_logger.current_file_index);
    }
    
    // 打开文件（如果未打开）
    if (!g_logger.is_open) {
        if (CircularLogger_OpenFile() != 0) {
            return 1;
        }
    }
    
    // 写入数据
    res = f_write(&g_logger.file, data, data_len, &bytesWritten);
    if (res != FR_OK) {
        return 1;
    }
    
    // 更新文件大小
    g_logger.current_file_size += bytesWritten;
    
    // 同步到SD卡
    f_sync(&g_logger.file);
    
    return 0;
}

/**
 * @brief  记录传感器数据
 */
void LogSensorData(float temperature, float humidity) {
    char buffer[128];
    uint32_t timestamp = HAL_GetTick();
    
    // 格式化数据
    sprintf(buffer, "%lu,%.2f,%.2f\n", timestamp, temperature, humidity);
    
    // 写入日志
    CircularLogger_Write(buffer);
}
```


## 步骤5：性能优化

### 5.1 缓冲写入

```c
/**
 * @brief  带缓冲的数据写入
 */
#define WRITE_BUFFER_SIZE 512

typedef struct {
    uint8_t buffer[WRITE_BUFFER_SIZE];
    uint16_t index;
    FIL* file;
} BufferedWriter_t;

BufferedWriter_t g_writer;

/**
 * @brief  初始化缓冲写入器
 */
void BufferedWriter_Init(FIL* file) {
    g_writer.file = file;
    g_writer.index = 0;
}

/**
 * @brief  写入数据到缓冲区
 */
uint8_t BufferedWriter_Write(const uint8_t* data, uint16_t length) {
    for (uint16_t i = 0; i < length; i++) {
        g_writer.buffer[g_writer.index++] = data[i];
        
        // 缓冲区满，刷新到SD卡
        if (g_writer.index >= WRITE_BUFFER_SIZE) {
            if (BufferedWriter_Flush() != 0) {
                return 1;
            }
        }
    }
    
    return 0;
}

/**
 * @brief  刷新缓冲区到SD卡
 */
uint8_t BufferedWriter_Flush(void) {
    FRESULT res;
    UINT bytesWritten;
    
    if (g_writer.index == 0) {
        return 0;  // 缓冲区为空
    }
    
    // 写入SD卡
    res = f_write(g_writer.file, g_writer.buffer, g_writer.index, &bytesWritten);
    if (res != FR_OK || bytesWritten != g_writer.index) {
        return 1;
    }
    
    // 重置缓冲区
    g_writer.index = 0;
    
    return 0;
}

/**
 * @brief  使用示例
 */
void BufferedWrite_Example(void) {
    FIL file;
    FRESULT res;
    
    // 打开文件
    res = f_open(&file, "buffered_data.bin", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        return;
    }
    
    // 初始化缓冲写入器
    BufferedWriter_Init(&file);
    
    // 写入大量数据
    for (int i = 0; i < 10000; i++) {
        uint8_t data[4];
        data[0] = (i >> 24) & 0xFF;
        data[1] = (i >> 16) & 0xFF;
        data[2] = (i >> 8) & 0xFF;
        data[3] = i & 0xFF;
        
        BufferedWriter_Write(data, 4);
    }
    
    // 刷新剩余数据
    BufferedWriter_Flush();
    
    // 关闭文件
    f_close(&file);
}
```


### 5.2 DMA传输（STM32）

```c
/**
 * @brief  使用DMA进行SD卡数据传输
 */
uint8_t SD_WriteDMA(uint32_t blockAddr, uint8_t* data, uint32_t numBlocks) {
    HAL_StatusTypeDef status;
    
    // 启动DMA写入
    status = HAL_SD_WriteBlocks_DMA(&hsd, data, blockAddr, numBlocks);
    if (status != HAL_OK) {
        return 1;
    }
    
    // 等待传输完成
    while (HAL_SD_GetCardState(&hsd) != HAL_SD_CARD_TRANSFER) {
        // 可以在这里处理其他任务
    }
    
    return 0;
}

/**
 * @brief  使用DMA读取SD卡数据
 */
uint8_t SD_ReadDMA(uint32_t blockAddr, uint8_t* data, uint32_t numBlocks) {
    HAL_StatusTypeDef status;
    
    // 启动DMA读取
    status = HAL_SD_ReadBlocks_DMA(&hsd, data, blockAddr, numBlocks);
    if (status != HAL_OK) {
        return 1;
    }
    
    // 等待传输完成
    while (HAL_SD_GetCardState(&hsd) != HAL_SD_CARD_TRANSFER) {
        // 可以在这里处理其他任务
    }
    
    return 0;
}

/**
 * @brief  DMA传输完成回调
 */
void HAL_SD_TxCpltCallback(SD_HandleTypeDef *hsd) {
    // DMA写入完成
    printf("DMA write complete\n");
}

void HAL_SD_RxCpltCallback(SD_HandleTypeDef *hsd) {
    // DMA读取完成
    printf("DMA read complete\n");
}
```

### 5.3 性能测试

```c
/**
 * @brief  SD卡性能测试
 */
void SD_PerformanceTest(void) {
    uint8_t buffer[512];
    uint32_t start_time, end_time;
    float speed;
    
    // 准备测试数据
    for (int i = 0; i < 512; i++) {
        buffer[i] = i & 0xFF;
    }
    
    printf("\n=== SD Card Performance Test ===\n");
    
    // 测试写入速度
    FIL file;
    f_open(&file, "speed_test.bin", FA_CREATE_ALWAYS | FA_WRITE);
    
    start_time = HAL_GetTick();
    for (int i = 0; i < 1000; i++) {
        UINT bw;
        f_write(&file, buffer, 512, &bw);
    }
    end_time = HAL_GetTick();
    
    f_close(&file);
    
    speed = (512.0 * 1000) / (end_time - start_time);  // KB/s
    printf("Write speed: %.2f KB/s\n", speed);
    
    // 测试读取速度
    f_open(&file, "speed_test.bin", FA_READ);
    
    start_time = HAL_GetTick();
    for (int i = 0; i < 1000; i++) {
        UINT br;
        f_read(&file, buffer, 512, &br);
    }
    end_time = HAL_GetTick();
    
    f_close(&file);
    
    speed = (512.0 * 1000) / (end_time - start_time);  // KB/s
    printf("Read speed: %.2f KB/s\n", speed);
    
    // 删除测试文件
    f_unlink("speed_test.bin");
    
    printf("================================\n\n");
}
```


## 步骤6：实际应用示例

### 6.1 GPS轨迹记录器

```cpp
/**
 * @brief  GPS轨迹记录器
 */
class GPSTracker {
private:
    File trackFile;
    String filename;
    unsigned long pointCount;
    
public:
    GPSTracker() {
        pointCount = 0;
    }
    
    /**
     * @brief  开始新的轨迹记录
     */
    bool startTrack() {
        // 生成文件名（基于时间戳）
        filename = "/tracks/track_" + String(millis()) + ".gpx";
        
        // 创建目录
        if (!SD.exists("/tracks")) {
            SD.mkdir("/tracks");
        }
        
        // 打开文件
        trackFile = SD.open(filename.c_str(), FILE_WRITE);
        if (!trackFile) {
            return false;
        }
        
        // 写入GPX文件头
        trackFile.println("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        trackFile.println("<gpx version=\"1.1\">");
        trackFile.println("  <trk>");
        trackFile.println("    <trkseg>");
        
        trackFile.close();
        pointCount = 0;
        
        Serial.print("Track started: ");
        Serial.println(filename);
        return true;
    }
    
    /**
     * @brief  记录GPS点
     */
    void logPoint(float latitude, float longitude, float altitude) {
        trackFile = SD.open(filename.c_str(), FILE_WRITE);
        if (!trackFile) {
            Serial.println("Failed to open track file");
            return;
        }
        
        // 写入轨迹点（GPX格式）
        trackFile.print("      <trkpt lat=\"");
        trackFile.print(latitude, 6);
        trackFile.print("\" lon=\"");
        trackFile.print(longitude, 6);
        trackFile.println("\">");
        trackFile.print("        <ele>");
        trackFile.print(altitude, 1);
        trackFile.println("</ele>");
        trackFile.print("        <time>");
        trackFile.print(getISO8601Time());
        trackFile.println("</time>");
        trackFile.println("      </trkpt>");
        
        trackFile.close();
        pointCount++;
        
        if (pointCount % 10 == 0) {
            Serial.print("Logged ");
            Serial.print(pointCount);
            Serial.println(" points");
        }
    }
    
    /**
     * @brief  结束轨迹记录
     */
    void stopTrack() {
        trackFile = SD.open(filename.c_str(), FILE_WRITE);
        if (trackFile) {
            // 写入GPX文件尾
            trackFile.println("    </trkseg>");
            trackFile.println("  </trk>");
            trackFile.println("</gpx>");
            trackFile.close();
            
            Serial.print("Track stopped. Total points: ");
            Serial.println(pointCount);
        }
    }
    
private:
    String getISO8601Time() {
        // 返回ISO 8601格式的时间戳
        // 实际应用中应该使用RTC
        return "2024-01-15T12:00:00Z";
    }
};

// 使用示例
GPSTracker tracker;

void setup() {
    Serial.begin(9600);
    
    if (!SD.begin(10)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    
    // 开始轨迹记录
    tracker.startTrack();
}

void loop() {
    // 读取GPS数据（示例）
    float lat = readGPSLatitude();
    float lon = readGPSLongitude();
    float alt = readGPSAltitude();
    
    // 记录轨迹点
    tracker.logPoint(lat, lon, alt);
    
    delay(1000);  // 每秒记录一次
}
```


### 6.2 配置文件管理

```c
/**
 * @brief  配置文件管理系统
 */
typedef struct {
    char device_name[32];
    uint8_t wifi_enabled;
    char wifi_ssid[32];
    char wifi_password[64];
    uint16_t sample_rate;
    uint8_t log_level;
} Config_t;

Config_t g_config;

/**
 * @brief  加载配置文件
 */
uint8_t Config_Load(void) {
    FIL file;
    FRESULT res;
    char line[128];
    
    // 打开配置文件
    res = f_open(&file, "config.ini", FA_READ);
    if (res != FR_OK) {
        printf("Config file not found, using defaults\n");
        Config_SetDefaults();
        return 1;
    }
    
    // 逐行读取配置
    while (f_gets(line, sizeof(line), &file)) {
        // 跳过注释和空行
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        
        // 解析配置项
        char key[32], value[96];
        if (sscanf(line, "%[^=]=%s", key, value) == 2) {
            // 去除空格
            trim(key);
            trim(value);
            
            // 设置配置值
            if (strcmp(key, "device_name") == 0) {
                strncpy(g_config.device_name, value, sizeof(g_config.device_name));
            } else if (strcmp(key, "wifi_enabled") == 0) {
                g_config.wifi_enabled = atoi(value);
            } else if (strcmp(key, "wifi_ssid") == 0) {
                strncpy(g_config.wifi_ssid, value, sizeof(g_config.wifi_ssid));
            } else if (strcmp(key, "wifi_password") == 0) {
                strncpy(g_config.wifi_password, value, sizeof(g_config.wifi_password));
            } else if (strcmp(key, "sample_rate") == 0) {
                g_config.sample_rate = atoi(value);
            } else if (strcmp(key, "log_level") == 0) {
                g_config.log_level = atoi(value);
            }
        }
    }
    
    f_close(&file);
    printf("Configuration loaded successfully\n");
    return 0;
}

/**
 * @brief  保存配置文件
 */
uint8_t Config_Save(void) {
    FIL file;
    FRESULT res;
    char buffer[128];
    
    // 打开配置文件（覆盖）
    res = f_open(&file, "config.ini", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to open config file for writing\n");
        return 1;
    }
    
    // 写入配置文件头
    f_puts("# Device Configuration File\n", &file);
    f_puts("# Generated automatically\n\n", &file);
    
    // 写入配置项
    sprintf(buffer, "device_name=%s\n", g_config.device_name);
    f_puts(buffer, &file);
    
    sprintf(buffer, "wifi_enabled=%d\n", g_config.wifi_enabled);
    f_puts(buffer, &file);
    
    sprintf(buffer, "wifi_ssid=%s\n", g_config.wifi_ssid);
    f_puts(buffer, &file);
    
    sprintf(buffer, "wifi_password=%s\n", g_config.wifi_password);
    f_puts(buffer, &file);
    
    sprintf(buffer, "sample_rate=%d\n", g_config.sample_rate);
    f_puts(buffer, &file);
    
    sprintf(buffer, "log_level=%d\n", g_config.log_level);
    f_puts(buffer, &file);
    
    f_close(&file);
    printf("Configuration saved successfully\n");
    return 0;
}

/**
 * @brief  设置默认配置
 */
void Config_SetDefaults(void) {
    strcpy(g_config.device_name, "MyDevice");
    g_config.wifi_enabled = 1;
    strcpy(g_config.wifi_ssid, "MyWiFi");
    strcpy(g_config.wifi_password, "password123");
    g_config.sample_rate = 1000;
    g_config.log_level = 2;
}

/**
 * @brief  辅助函数：去除字符串首尾空格
 */
void trim(char* str) {
    char* start = str;
    char* end;
    
    // 去除前导空格
    while (*start == ' ' || *start == '\t') {
        start++;
    }
    
    // 去除尾随空格
    end = start + strlen(start) - 1;
    while (end > start && (*end == ' ' || *end == '\t' || *end == '\n' || *end == '\r')) {
        end--;
    }
    *(end + 1) = '\0';
    
    // 移动字符串
    if (start != str) {
        memmove(str, start, strlen(start) + 1);
    }
}
```


## 故障排除

### 问题1：SD卡初始化失败

**现象**：
- SD.begin()返回false
- 无法检测到SD卡

**可能原因**：
- SD卡未插入或接触不良
- 电源电压不足或不稳定
- 接线错误
- SD卡损坏或格式不兼容
- SPI时钟频率过高

**解决方法**：

```cpp
// 调试SD卡初始化
void debugSDInit() {
    Serial.println("SD Card Initialization Debug:");
    
    // 1. 检查电源
    Serial.println("1. Check power supply (3.3V)");
    
    // 2. 检查接线
    Serial.println("2. Check wiring:");
    Serial.println("   CS   -> Pin 10");
    Serial.println("   MOSI -> Pin 11");
    Serial.println("   MISO -> Pin 12");
    Serial.println("   SCK  -> Pin 13");
    
    // 3. 尝试降低SPI速度
    Serial.println("3. Trying lower SPI speed...");
    SPI.setClockDivider(SPI_CLOCK_DIV64);  // 降低时钟
    
    if (SD.begin(10)) {
        Serial.println("SUCCESS with lower speed!");
    } else {
        Serial.println("Still failed. Check:");
        Serial.println("   - Card is formatted (FAT32)");
        Serial.println("   - Card is not write-protected");
        Serial.println("   - Try different card");
    }
}
```

### 问题2：文件操作失败

**现象**：
- 无法创建或打开文件
- 写入失败
- 读取数据错误

**可能原因**：
- 文件系统损坏
- SD卡已满
- 文件名不合法
- 文件已被其他程序打开

**解决方法**：

```c
/**
 * @brief  检查SD卡健康状态
 */
void SD_HealthCheck(void) {
    FATFS* fs;
    DWORD fre_clust;
    FRESULT res;
    
    // 获取文件系统信息
    res = f_getfree("", &fre_clust, &fs);
    if (res == FR_OK) {
        // 计算空间
        uint64_t total_space = (uint64_t)(fs->n_fatent - 2) * fs->csize * 512;
        uint64_t free_space = (uint64_t)fre_clust * fs->csize * 512;
        
        printf("SD Card Health Check:\n");
        printf("  Total space: %llu MB\n", total_space / (1024 * 1024));
        printf("  Free space: %llu MB\n", free_space / (1024 * 1024));
        printf("  Used space: %llu MB\n", (total_space - free_space) / (1024 * 1024));
        
        if (free_space < 1024 * 1024) {
            printf("  WARNING: Low disk space!\n");
        }
    } else {
        printf("Failed to get filesystem info: %d\n", res);
    }
}

/**
 * @brief  文件操作错误处理
 */
const char* GetFatFsError(FRESULT res) {
    switch (res) {
        case FR_OK: return "Success";
        case FR_DISK_ERR: return "Disk error";
        case FR_INT_ERR: return "Internal error";
        case FR_NOT_READY: return "Drive not ready";
        case FR_NO_FILE: return "File not found";
        case FR_NO_PATH: return "Path not found";
        case FR_INVALID_NAME: return "Invalid name";
        case FR_DENIED: return "Access denied";
        case FR_EXIST: return "File exists";
        case FR_INVALID_OBJECT: return "Invalid object";
        case FR_WRITE_PROTECTED: return "Write protected";
        case FR_INVALID_DRIVE: return "Invalid drive";
        case FR_NOT_ENABLED: return "Not enabled";
        case FR_NO_FILESYSTEM: return "No filesystem";
        case FR_TIMEOUT: return "Timeout";
        case FR_LOCKED: return "File locked";
        case FR_NOT_ENOUGH_CORE: return "Not enough memory";
        case FR_TOO_MANY_OPEN_FILES: return "Too many open files";
        default: return "Unknown error";
    }
}
```


### 问题3：数据丢失或损坏

**现象**：
- 文件内容不完整
- 数据乱码
- 文件系统损坏

**可能原因**：
- 写入时突然断电
- 未正确关闭文件
- SD卡质量问题
- 写入速度过快

**解决方法**：

```c
/**
 * @brief  安全写入（带同步）
 */
uint8_t SD_SafeWrite(const char* filename, const char* data) {
    FRESULT res;
    UINT bytesWritten;
    
    // 打开文件
    res = f_open(&MyFile, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        return 1;
    }
    
    // 写入数据
    res = f_write(&MyFile, data, strlen(data), &bytesWritten);
    if (res != FR_OK) {
        f_close(&MyFile);
        return 1;
    }
    
    // 同步到SD卡（确保数据写入）
    res = f_sync(&MyFile);
    if (res != FR_OK) {
        f_close(&MyFile);
        return 1;
    }
    
    // 关闭文件
    f_close(&MyFile);
    
    // 验证写入
    char verify_buffer[256];
    if (SD_ReadFile(filename, verify_buffer, sizeof(verify_buffer)) == 0) {
        if (strcmp(data, verify_buffer) == 0) {
            printf("Write verified successfully\n");
            return 0;
        } else {
            printf("Write verification failed!\n");
            return 1;
        }
    }
    
    return 1;
}

/**
 * @brief  定期同步数据
 */
void PeriodicSync(void) {
    static uint32_t last_sync = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 每5秒同步一次
    if (current_time - last_sync > 5000) {
        if (g_logger.is_open) {
            f_sync(&g_logger.file);
            printf("Data synced to SD card\n");
        }
        last_sync = current_time;
    }
}
```

### 问题4：性能不佳

**现象**：
- 写入速度慢
- 系统响应延迟
- 数据记录丢失

**可能原因**：
- 使用SPI模式而非SDIO
- 未使用缓冲
- 频繁打开关闭文件
- SD卡速度等级低

**解决方法**：

```c
/**
 * @brief  性能优化建议
 */
void PerformanceOptimization(void) {
    printf("SD Card Performance Optimization Tips:\n\n");
    
    printf("1. Use SDIO instead of SPI\n");
    printf("   - SDIO: up to 104MB/s\n");
    printf("   - SPI: up to 3MB/s\n\n");
    
    printf("2. Use buffered writes\n");
    printf("   - Reduce number of write operations\n");
    printf("   - Write in multiples of 512 bytes\n\n");
    
    printf("3. Keep files open\n");
    printf("   - Avoid frequent open/close\n");
    printf("   - Use f_sync() instead\n\n");
    
    printf("4. Use high-speed SD cards\n");
    printf("   - Class 10 or UHS-I\n");
    printf("   - Check card specifications\n\n");
    
    printf("5. Enable DMA transfers\n");
    printf("   - Offload CPU\n");
    printf("   - Improve throughput\n\n");
    
    printf("6. Optimize cluster size\n");
    printf("   - Format with appropriate cluster size\n");
    printf("   - Larger clusters for large files\n\n");
}
```


## 最佳实践

### 1. 文件命名规范

```c
/**
 * @brief  生成安全的文件名
 */
void GenerateSafeFilename(char* filename, size_t size, const char* prefix) {
    // 使用时间戳生成唯一文件名
    uint32_t timestamp = HAL_GetTick();
    
    // FAT32文件名限制：8.3格式（8个字符名称 + 3个字符扩展名）
    // 或长文件名（最多255个字符）
    snprintf(filename, size, "%s_%08lu.log", prefix, timestamp);
    
    // 确保文件名合法
    // - 不包含: \ / : * ? " < > |
    // - 不以空格或点开头
    // - 不使用保留名称（CON, PRN, AUX等）
}

/**
 * @brief  文件名规范示例
 */
void FilenameExamples(void) {
    printf("Good filenames:\n");
    printf("  data_20240115.csv\n");
    printf("  sensor_log_001.txt\n");
    printf("  config.ini\n\n");
    
    printf("Bad filenames:\n");
    printf("  data:log.txt  (contains ':')\n");
    printf("  my*file.dat   (contains '*')\n");
    printf("  .hidden       (starts with '.')\n");
    printf("  CON           (reserved name)\n");
}
```

### 2. 错误处理和重试

```c
/**
 * @brief  带重试的文件操作
 */
uint8_t SD_WriteWithRetry(const char* filename, const char* data, uint8_t max_retries) {
    for (uint8_t retry = 0; retry < max_retries; retry++) {
        FRESULT res = f_open(&MyFile, filename, FA_CREATE_ALWAYS | FA_WRITE);
        
        if (res == FR_OK) {
            UINT bw;
            res = f_write(&MyFile, data, strlen(data), &bw);
            f_close(&MyFile);
            
            if (res == FR_OK && bw == strlen(data)) {
                return 0;  // 成功
            }
        }
        
        // 失败，延时后重试
        printf("Write failed (attempt %d/%d), retrying...\n", retry + 1, max_retries);
        HAL_Delay(100);
    }
    
    printf("Write failed after %d attempts\n", max_retries);
    return 1;
}
```

### 3. 数据完整性保护

```c
/**
 * @brief  带CRC校验的数据记录
 */
typedef struct {
    uint32_t timestamp;
    float temperature;
    float humidity;
    uint16_t crc;
} SensorRecord_t;

/**
 * @brief  计算CRC16
 */
uint16_t Calculate_CRC16(uint8_t* data, uint16_t length) {
    uint16_t crc = 0xFFFF;
    
    for (uint16_t i = 0; i < length; i++) {
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
 * @brief  写入带校验的记录
 */
uint8_t WriteRecordWithCRC(SensorRecord_t* record) {
    // 计算CRC（不包括CRC字段）
    record->crc = Calculate_CRC16((uint8_t*)record, 
                                  sizeof(SensorRecord_t) - sizeof(uint16_t));
    
    // 写入文件
    UINT bw;
    FRESULT res = f_write(&MyFile, record, sizeof(SensorRecord_t), &bw);
    
    return (res == FR_OK && bw == sizeof(SensorRecord_t)) ? 0 : 1;
}

/**
 * @brief  读取并验证记录
 */
uint8_t ReadRecordWithCRC(SensorRecord_t* record) {
    UINT br;
    FRESULT res = f_read(&MyFile, record, sizeof(SensorRecord_t), &br);
    
    if (res != FR_OK || br != sizeof(SensorRecord_t)) {
        return 1;
    }
    
    // 验证CRC
    uint16_t calculated_crc = Calculate_CRC16((uint8_t*)record, 
                                              sizeof(SensorRecord_t) - sizeof(uint16_t));
    
    if (calculated_crc != record->crc) {
        printf("CRC mismatch! Data may be corrupted\n");
        return 2;
    }
    
    return 0;
}
```


### 4. 资源管理

```c
/**
 * @brief  文件句柄管理
 */
#define MAX_OPEN_FILES 5

typedef struct {
    FIL file;
    uint8_t in_use;
    char filename[64];
} FileHandle_t;

FileHandle_t g_file_handles[MAX_OPEN_FILES];

/**
 * @brief  初始化文件句柄池
 */
void FileHandles_Init(void) {
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        g_file_handles[i].in_use = 0;
    }
}

/**
 * @brief  分配文件句柄
 */
FIL* FileHandles_Allocate(const char* filename) {
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        if (!g_file_handles[i].in_use) {
            g_file_handles[i].in_use = 1;
            strncpy(g_file_handles[i].filename, filename, 
                    sizeof(g_file_handles[i].filename));
            return &g_file_handles[i].file;
        }
    }
    
    printf("ERROR: No free file handles\n");
    return NULL;
}

/**
 * @brief  释放文件句柄
 */
void FileHandles_Free(FIL* file) {
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        if (&g_file_handles[i].file == file) {
            f_close(file);
            g_file_handles[i].in_use = 0;
            g_file_handles[i].filename[0] = '\0';
            return;
        }
    }
}

/**
 * @brief  关闭所有文件
 */
void FileHandles_CloseAll(void) {
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        if (g_file_handles[i].in_use) {
            f_close(&g_file_handles[i].file);
            g_file_handles[i].in_use = 0;
        }
    }
}
```

### 5. 日志轮转策略

```c
/**
 * @brief  日志轮转管理
 */
#define MAX_LOG_SIZE (10 * 1024 * 1024)  // 10MB
#define MAX_LOG_FILES 5

typedef struct {
    char base_name[32];
    uint32_t current_size;
    uint8_t current_index;
    FIL current_file;
} LogRotation_t;

LogRotation_t g_log_rotation;

/**
 * @brief  初始化日志轮转
 */
void LogRotation_Init(const char* base_name) {
    strcpy(g_log_rotation.base_name, base_name);
    g_log_rotation.current_size = 0;
    g_log_rotation.current_index = 0;
    
    // 打开第一个日志文件
    char filename[64];
    sprintf(filename, "%s_%d.log", base_name, 0);
    f_open(&g_log_rotation.current_file, filename, FA_CREATE_ALWAYS | FA_WRITE);
}

/**
 * @brief  写入日志（自动轮转）
 */
void LogRotation_Write(const char* message) {
    uint32_t msg_len = strlen(message);
    
    // 检查是否需要轮转
    if (g_log_rotation.current_size + msg_len > MAX_LOG_SIZE) {
        // 关闭当前文件
        f_close(&g_log_rotation.current_file);
        
        // 切换到下一个文件
        g_log_rotation.current_index = (g_log_rotation.current_index + 1) % MAX_LOG_FILES;
        g_log_rotation.current_size = 0;
        
        // 打开新文件（覆盖旧文件）
        char filename[64];
        sprintf(filename, "%s_%d.log", 
                g_log_rotation.base_name, 
                g_log_rotation.current_index);
        f_open(&g_log_rotation.current_file, filename, FA_CREATE_ALWAYS | FA_WRITE);
        
        printf("Log rotated to %s\n", filename);
    }
    
    // 写入消息
    UINT bw;
    f_write(&g_log_rotation.current_file, message, msg_len, &bw);
    g_log_rotation.current_size += bw;
    
    // 定期同步
    if (g_log_rotation.current_size % 4096 == 0) {
        f_sync(&g_log_rotation.current_file);
    }
}
```


## 总结

通过本教程，你学习了：

- ✅ SD卡的工作原理和技术规范
- ✅ SDIO和SPI接口的使用方法
- ✅ SD卡初始化和配置
- ✅ FAT文件系统的基本操作
- ✅ 文件和目录管理
- ✅ 数据记录和日志系统
- ✅ 性能优化技巧
- ✅ 故障排除和最佳实践

**关键要点**：

1. **接口选择**
   - SDIO：高性能应用，速度快
   - SPI：简单应用，易于实现
   - 根据需求选择合适的接口

2. **文件系统**
   - 使用FAT32文件系统（兼容性好）
   - 正确打开和关闭文件
   - 使用f_sync()确保数据写入

3. **性能优化**
   - 使用缓冲写入
   - 启用DMA传输
   - 保持文件打开状态
   - 选择高速SD卡

4. **数据可靠性**
   - 添加CRC校验
   - 实现重试机制
   - 定期同步数据
   - 验证写入结果

5. **资源管理**
   - 限制同时打开的文件数
   - 实现日志轮转
   - 监控磁盘空间
   - 正确处理错误

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现一个完整的数据采集系统，支持多传感器数据记录
2. **挑战2**：添加数据压缩功能，减少存储空间占用
3. **挑战3**：实现SD卡热插拔检测和自动重新挂载
4. **挑战4**：开发一个简单的文件浏览器，支持文件查看和管理
5. **挑战5**：实现数据导出功能，将SD卡数据通过串口或网络传输


## 完整代码示例

### Arduino完整示例

```cpp
/**
 * @file    sd_card_logger.ino
 * @brief   SD卡数据记录完整示例
 */

#include <SPI.h>
#include <SD.h>

const int chipSelect = 10;
File dataFile;
unsigned long lastLogTime = 0;
const unsigned long logInterval = 1000;  // 1秒

void setup() {
    Serial.begin(9600);
    while (!Serial) {
        ; // 等待串口连接
    }
    
    Serial.println("SD Card Data Logger");
    Serial.println("==================");
    
    // 初始化SD卡
    if (!SD.begin(chipSelect)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    Serial.println("SD card initialized.");
    
    // 创建日志目录
    if (!SD.exists("/logs")) {
        SD.mkdir("/logs");
    }
    
    // 创建日志文件
    String filename = "/logs/data_" + String(millis()) + ".csv";
    dataFile = SD.open(filename.c_str(), FILE_WRITE);
    
    if (dataFile) {
        // 写入CSV文件头
        dataFile.println("Timestamp,Temperature,Humidity");
        dataFile.close();
        Serial.print("Log file created: ");
        Serial.println(filename);
    } else {
        Serial.println("Error creating log file");
    }
}

void loop() {
    unsigned long currentTime = millis();
    
    // 每隔logInterval记录一次数据
    if (currentTime - lastLogTime >= logInterval) {
        lastLogTime = currentTime;
        
        // 读取传感器数据（示例）
        float temperature = random(200, 300) / 10.0;  // 20.0-30.0°C
        float humidity = random(400, 800) / 10.0;     // 40.0-80.0%
        
        // 记录数据
        logData(currentTime, temperature, humidity);
        
        // 打印到串口
        Serial.print("Logged: ");
        Serial.print(temperature);
        Serial.print("°C, ");
        Serial.print(humidity);
        Serial.println("%");
    }
}

void logData(unsigned long timestamp, float temperature, float humidity) {
    // 打开文件追加
    dataFile = SD.open("/logs/data.csv", FILE_WRITE);
    
    if (dataFile) {
        // 写入数据
        dataFile.print(timestamp);
        dataFile.print(",");
        dataFile.print(temperature, 2);
        dataFile.print(",");
        dataFile.println(humidity, 2);
        
        // 关闭文件
        dataFile.close();
    } else {
        Serial.println("Error opening log file");
    }
}
```


### STM32完整示例

```c
/**
 * @file    main.c
 * @brief   STM32 SD卡数据记录完整示例
 */

#include "main.h"
#include "fatfs.h"
#include <stdio.h>
#include <string.h>

// 全局变量
SD_HandleTypeDef hsd;
FATFS SDFatFs;
FIL LogFile;
char SDPath[4];

// 函数声明
void SystemClock_Config(void);
void Error_Handler(void);
void SD_Init(void);
void DataLogger_Init(void);
void DataLogger_Write(float temperature, float humidity);

int main(void) {
    // 初始化HAL库
    HAL_Init();
    SystemClock_Config();
    
    // 初始化UART（用于调试）
    MX_USART1_UART_Init();
    
    printf("\n=== SD Card Data Logger ===\n");
    
    // 初始化SD卡
    SD_Init();
    
    // 初始化数据记录器
    DataLogger_Init();
    
    printf("System ready. Starting data logging...\n\n");
    
    // 主循环
    uint32_t lastLogTime = 0;
    while (1) {
        uint32_t currentTime = HAL_GetTick();
        
        // 每秒记录一次数据
        if (currentTime - lastLogTime >= 1000) {
            lastLogTime = currentTime;
            
            // 读取传感器数据（示例）
            float temperature = 25.0 + (rand() % 100) / 10.0;
            float humidity = 50.0 + (rand() % 300) / 10.0;
            
            // 记录数据
            DataLogger_Write(temperature, humidity);
            
            printf("Logged: %.2f°C, %.2f%%\n", temperature, humidity);
        }
        
        HAL_Delay(100);
    }
}

/**
 * @brief  初始化SD卡
 */
void SD_Init(void) {
    // 初始化SDIO
    MX_SDIO_SD_Init();
    
    // 挂载文件系统
    if (FATFS_LinkDriver(&SD_Driver, SDPath) != 0) {
        Error_Handler();
    }
    
    if (f_mount(&SDFatFs, (TCHAR const*)SDPath, 1) != FR_OK) {
        printf("Failed to mount SD card\n");
        Error_Handler();
    }
    
    printf("SD card mounted successfully\n");
    
    // 获取SD卡信息
    HAL_SD_CardInfoTypeDef cardInfo;
    if (HAL_SD_GetCardInfo(&hsd, &cardInfo) == HAL_OK) {
        uint64_t capacity = (uint64_t)cardInfo.BlockNbr * cardInfo.BlockSize;
        printf("SD Card Capacity: %llu MB\n", capacity / (1024 * 1024));
    }
}

/**
 * @brief  初始化数据记录器
 */
void DataLogger_Init(void) {
    FRESULT res;
    
    // 创建日志目录
    f_mkdir("logs");
    
    // 打开日志文件
    res = f_open(&LogFile, "logs/data.csv", FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to create log file: %d\n", res);
        Error_Handler();
    }
    
    // 写入CSV文件头
    f_puts("Timestamp,Temperature,Humidity\n", &LogFile);
    
    // 关闭文件
    f_close(&LogFile);
    
    printf("Data logger initialized\n");
}

/**
 * @brief  写入数据到日志
 */
void DataLogger_Write(float temperature, float humidity) {
    FRESULT res;
    char buffer[128];
    
    // 打开文件（追加模式）
    res = f_open(&LogFile, "logs/data.csv", FA_OPEN_APPEND | FA_WRITE);
    if (res != FR_OK) {
        printf("Failed to open log file: %d\n", res);
        return;
    }
    
    // 格式化数据
    uint32_t timestamp = HAL_GetTick();
    sprintf(buffer, "%lu,%.2f,%.2f\n", timestamp, temperature, humidity);
    
    // 写入数据
    f_puts(buffer, &LogFile);
    
    // 同步到SD卡
    f_sync(&LogFile);
    
    // 关闭文件
    f_close(&LogFile);
}

/**
 * @brief  错误处理
 */
void Error_Handler(void) {
    printf("Error occurred!\n");
    while (1) {
        HAL_Delay(1000);
    }
}
```


## 下一步

建议继续学习：

- [Flash存储器技术详解](./01-flash-technology.html) - 了解Flash存储技术
- [FAT文件系统原理与应用](../../01-file-systems/beginner/01-fat-filesystem.html) - 深入学习FAT文件系统
- [EEPROM数据存储应用](./02-eeprom-storage.html) - 学习小容量非易失存储
- [数据持久化与掉电保护](../intermediate/02-data-persistence.html) - 高级数据保护技术

## 参考资料

1. **SD卡规范**
   - SD Physical Layer Simplified Specification
   - SD Card Association Official Documentation

2. **文件系统**
   - FatFs - Generic FAT Filesystem Module
   - Microsoft FAT32 File System Specification

3. **芯片数据手册**
   - STM32F4 Reference Manual (SDIO)
   - ESP32 Technical Reference Manual

4. **应用笔记**
   - AN4187: Using the SDIO host controller (STM32)
   - AN2548: Using SD/SDIO/MMC memory cards with STM32

5. **在线资源**
   - [SD Association](https://www.sdcard.org/)
   - [FatFs Documentation](http://elm-chan.org/fsw/ff/)
   - [Arduino SD Library](https://www.arduino.cc/en/Reference/SD)

## 常见问题

### Q1: SDIO和SPI模式如何选择？

**A**: 根据应用需求选择：

- **选择SDIO**：
  - 需要高速数据传输（>10MB/s）
  - MCU支持SDIO接口
  - 引脚资源充足
  - 实时数据记录应用

- **选择SPI**：
  - 速度要求不高（<3MB/s）
  - MCU没有SDIO接口
  - 引脚资源有限
  - 简单的数据存储应用

### Q2: 如何选择合适的SD卡？

**A**: 考虑以下因素：

1. **容量**：根据数据量选择（2GB-32GB常用）
2. **速度等级**：Class 10或UHS-I推荐
3. **品牌**：选择知名品牌（SanDisk、Samsung等）
4. **工业级**：工业应用选择工业级SD卡
5. **温度范围**：确保满足工作环境要求

### Q3: 如何防止数据丢失？

**A**: 采用以下策略：

1. **定期同步**：使用f_sync()定期刷新缓冲区
2. **CRC校验**：添加数据校验码
3. **多副本**：重要数据保存多份
4. **日志轮转**：避免单个文件过大
5. **电源管理**：确保电源稳定，添加掉电检测

### Q4: SD卡寿命有多长？

**A**: SD卡寿命取决于多个因素：

- **擦写次数**：通常10,000-100,000次
- **使用模式**：频繁写入会缩短寿命
- **环境条件**：温度、湿度影响寿命
- **质量等级**：工业级寿命更长

**延长寿命的方法**：
- 减少不必要的写入
- 使用磨损均衡
- 避免频繁格式化
- 定期备份数据

### Q5: 如何提高SD卡性能？

**A**: 性能优化方法：

1. **使用SDIO接口**：比SPI快10倍以上
2. **启用4位模式**：提高数据传输速度
3. **使用DMA**：减少CPU占用
4. **缓冲写入**：批量写入数据
5. **保持文件打开**：减少打开关闭开销
6. **选择高速卡**：Class 10或UHS-I


---

**练习题**：

1. 解释SDIO和SPI接口的主要区别，并说明各自的应用场景
2. 编写一个程序，实现SD卡的文件浏览功能，显示所有文件和目录
3. 设计一个数据记录系统，支持多传感器数据的CSV格式存储
4. 实现一个循环缓冲日志系统，自动删除最旧的日志文件
5. 计算：如果每秒写入100字节数据，一张32GB的SD卡能记录多长时间？

**思考题**：

1. 为什么SD卡需要文件系统？直接读写块设备有什么问题？
2. 在什么情况下应该使用SD卡而不是Flash或EEPROM？
3. 如何设计一个既能保证数据完整性又能提高写入速度的存储方案？
4. SD卡突然拔出会导致什么问题？如何检测和处理？

---

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言或提交Issue！

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。
