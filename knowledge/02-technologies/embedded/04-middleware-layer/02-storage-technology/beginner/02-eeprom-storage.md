---
title: "EEPROM数据存储应用：掉电保护与参数配置实战"
description: "全面学习EEPROM存储器的工作原理、读写操作、数据保护和磨损均衡技术，掌握嵌入式系统中非易失性数据存储的实用方法"
slug: "eeprom-storage"

# 分类信息
domain: "中间件层"
module: "存储技术"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - EEPROM
  - 数据存储
  - 非易失存储
  - 参数配置
  - 掉电保护
prerequisites:
  - "01-hardware-layer/01-chip-architecture/beginner/01-mcu-basics"
  - "02-driver-bsp-layer/02-device-driver-development/beginner/01-gpio-basics"
related_contents:
  - "04-middleware-layer/02-storage-technology/beginner/01-flash-technology"
  - "04-middleware-layer/02-storage-technology/intermediate/01-wear-leveling"
  - "04-middleware-layer/02-storage-technology/intermediate/02-data-persistence"

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
  - EEPROM存储器
  - 非易失性存储
  - 数据持久化
  - 参数保存
  - I2C EEPROM
  - SPI EEPROM
cover_image: ""
---

# EEPROM数据存储应用：掉电保护与参数配置实战

## 学习目标

完成本教程后，你将能够：

- [ ] 理解EEPROM的工作原理和特点
- [ ] 掌握I2C和SPI接口EEPROM的使用方法
- [ ] 学会实现EEPROM的读写操作
- [ ] 掌握数据保护和校验技术
- [ ] 了解EEPROM的磨损均衡策略
- [ ] 能够设计可靠的参数存储方案
- [ ] 实现掉电保护的配置数据管理

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解C语言基础编程
- 熟悉基本的数字电路知识
- 掌握I2C或SPI通信协议基础
- 了解MCU的基本使用

**技能要求**：
- 能够使用开发环境编写和调试代码
- 会使用示波器或逻辑分析仪（可选）
- 能够阅读芯片数据手册

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32或Arduino | STM32F103/Arduino Uno |
| I2C EEPROM | 1 | 容量2KB-64KB | AT24C02/AT24C256 |
| 上拉电阻 | 2 | 4.7kΩ | 用于I2C总线 |
| 面包板 | 1 | - | - |
| 杜邦线 | 若干 | - | - |

### 软件准备

- **开发环境**：STM32CubeIDE / Arduino IDE
- **驱动库**：HAL库 / Wire库
- **辅助工具**：串口调试助手

### 环境配置

1. 安装开发环境
2. 配置I2C或SPI外设
3. 准备测试代码框架

## 背景知识

### 什么是EEPROM

EEPROM（Electrically Erasable Programmable Read-Only Memory，电可擦除可编程只读存储器）是一种非易失性存储器，具有以下特点：

**核心特性**：
- **非易失性**：断电后数据不丢失
- **字节可擦写**：可以按字节单独擦写
- **有限寿命**：典型擦写次数100万次
- **低功耗**：待机电流通常<1μA
- **慢速写入**：写入时间3-10ms

**与Flash的区别**：

| 特性 | EEPROM | Flash |
|------|--------|-------|
| 擦除单位 | 字节 | 块（4KB-64KB） |
| 擦写次数 | 100万次 | 10万次 |
| 写入速度 | 3-10ms/字节 | 快（页编程） |
| 容量 | 几KB-几MB | 几MB-几GB |
| 成本 | 较高 | 较低 |
| 应用 | 配置参数 | 程序代码、大数据 |

### EEPROM工作原理

EEPROM基于浮栅晶体管技术，但与Flash不同的是：

**存储单元结构**：

```
        控制栅极
              |
    ┌─────────┴─────────┐
    │    氧化层          │
    ├───────────────────┤
    │  浮栅（存储电荷）  │
    ├───────────────────┤
    │    隧道氧化层      │  ← 更薄，便于擦写
    └─────────┬─────────┘
              |
         源极 ─┴─ 漏极
```

**读写原理**：
1. **写入**：通过隧道效应将电子注入浮栅（约5-10ms）
2. **擦除**：通过隧道效应将电子从浮栅移除（约5-10ms）
3. **读取**：检测晶体管导通状态（快速，<1μs）

### EEPROM类型

**按接口分类**：

1. **并行EEPROM**
   - 地址和数据总线并行
   - 速度快，引脚多
   - 适合嵌入MCU内部

2. **I2C EEPROM**
   - 2线串行接口（SDA、SCL）
   - 引脚少，易于使用
   - 最常用的外部EEPROM

3. **SPI EEPROM**
   - 4线串行接口
   - 速度比I2C快
   - 容量通常较大

4. **Microwire EEPROM**
   - 3线串行接口
   - 较少使用

**常见型号**：

| 型号 | 接口 | 容量 | 特点 |
|------|------|------|------|
| AT24C02 | I2C | 2Kbit (256B) | 小容量，常用 |
| AT24C256 | I2C | 256Kbit (32KB) | 中等容量 |
| 25LC256 | SPI | 256Kbit (32KB) | SPI接口 |
| 93C46 | Microwire | 1Kbit (128B) | 简单应用 |

## 电路连接

### I2C EEPROM连接

以AT24C256为例：

```
STM32/Arduino          AT24C256 (I2C EEPROM)
                       ┌─────────┐
  3.3V/5V ────────────┤1 A0   VCC├──── 3.3V/5V
  GND ────────────────┤2 A1   WP ├──── GND (写保护禁用)
  GND ────────────────┤3 A2   SCL├◄─── SCL (I2C时钟)
  GND ────────────────┤4 GND  SDA├◄──► SDA (I2C数据)
                       └─────────┘
                           │   │
                         4.7kΩ 4.7kΩ (上拉电阻)
                           │   │
                          VCC VCC
```

**引脚说明**：
- **A0-A2**：设备地址选择（接地或VCC）
- **WP**：写保护引脚（接地禁用写保护）
- **SCL/SDA**：I2C总线，需要上拉电阻
- **VCC/GND**：电源（3.3V或5V）

### 设备地址配置

I2C EEPROM的7位地址格式：

```
1 0 1 0 A2 A1 A0
│ │ │ │  │  │  │
│ │ │ │  └──┴──┴─ 可配置位（通过A0-A2引脚）
│ │ │ └─────────── 固定位
└─┴─┴───────────── 器件类型（1010 = EEPROM）

示例：
A2=0, A1=0, A0=0 → 地址 = 0x50 (1010000)
A2=0, A1=0, A0=1 → 地址 = 0x51 (1010001)
A2=1, A1=1, A1=1 → 地址 = 0x57 (1010111)
```

**注意事项**：
- 确保上拉电阻正确连接（4.7kΩ）
- 检查电源电压与EEPROM兼容
- WP引脚接地以允许写入
- 同一总线上的设备地址不能冲突


## 步骤1：I2C接口初始化

### 1.1 STM32 HAL库初始化

```c
// I2C配置
#include "stm32f1xx_hal.h"

I2C_HandleTypeDef hi2c1;

void I2C_Init(void) {
    // 使能I2C时钟
    __HAL_RCC_I2C1_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    // 配置GPIO（PB6=SCL, PB7=SDA）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;  // 开漏输出
    GPIO_InitStruct.Pull = GPIO_PULLUP;      // 上拉
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    // 配置I2C参数
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 100000;          // 100kHz
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    
    // 初始化I2C
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}
```

### 1.2 Arduino Wire库初始化

```cpp
#include <Wire.h>

void setup() {
    // 初始化I2C
    Wire.begin();
    
    // 设置I2C时钟频率（可选）
    Wire.setClock(100000);  // 100kHz
    
    // 初始化串口用于调试
    Serial.begin(9600);
    Serial.println("EEPROM Test Started");
}
```

**代码说明**：
- I2C时钟频率通常设置为100kHz（标准模式）
- GPIO配置为开漏输出模式，需要外部上拉
- Arduino的Wire库自动处理大部分底层细节

## 步骤2：EEPROM基本读写

### 2.1 字节写入

```c
// EEPROM配置
#define EEPROM_ADDR 0x50  // 7位地址（A2=A1=A0=0）
#define EEPROM_I2C_ADDR (EEPROM_ADDR << 1)  // 8位地址

/**
 * @brief  写入单个字节到EEPROM
 * @param  mem_addr: EEPROM内存地址（0-32767）
 * @param  data: 要写入的数据
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_WriteByte(uint16_t mem_addr, uint8_t data) {
    uint8_t buffer[3];
    
    // AT24C256使用16位地址
    buffer[0] = (mem_addr >> 8) & 0xFF;  // 高字节
    buffer[1] = mem_addr & 0xFF;         // 低字节
    buffer[2] = data;                    // 数据
    
    // 发送数据
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        &hi2c1,
        EEPROM_I2C_ADDR,
        buffer,
        3,
        HAL_MAX_DELAY
    );
    
    // 等待写入完成（约5ms）
    HAL_Delay(5);
    
    return (status == HAL_OK) ? 0 : 1;
}
```

### 2.2 字节读取

```c
/**
 * @brief  从EEPROM读取单个字节
 * @param  mem_addr: EEPROM内存地址
 * @param  data: 读取数据的指针
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_ReadByte(uint16_t mem_addr, uint8_t *data) {
    uint8_t addr_buffer[2];
    
    // 发送内存地址
    addr_buffer[0] = (mem_addr >> 8) & 0xFF;
    addr_buffer[1] = mem_addr & 0xFF;
    
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        &hi2c1,
        EEPROM_I2C_ADDR,
        addr_buffer,
        2,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) return 1;
    
    // 读取数据
    status = HAL_I2C_Master_Receive(
        &hi2c1,
        EEPROM_I2C_ADDR,
        data,
        1,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK) ? 0 : 1;
}
```


### 2.3 Arduino实现

```cpp
// 写入字节
void EEPROM_WriteByte(uint16_t address, uint8_t data) {
    Wire.beginTransmission(EEPROM_ADDR);
    Wire.write((uint8_t)(address >> 8));   // 高字节
    Wire.write((uint8_t)(address & 0xFF)); // 低字节
    Wire.write(data);                      // 数据
    Wire.endTransmission();
    
    delay(5);  // 等待写入完成
}

// 读取字节
uint8_t EEPROM_ReadByte(uint16_t address) {
    // 发送地址
    Wire.beginTransmission(EEPROM_ADDR);
    Wire.write((uint8_t)(address >> 8));
    Wire.write((uint8_t)(address & 0xFF));
    Wire.endTransmission();
    
    // 读取数据
    Wire.requestFrom(EEPROM_ADDR, 1);
    if (Wire.available()) {
        return Wire.read();
    }
    return 0xFF;  // 读取失败
}
```

### 2.4 测试读写功能

```c
void Test_BasicReadWrite(void) {
    uint8_t write_data = 0xA5;
    uint8_t read_data = 0;
    uint16_t test_addr = 0x0100;
    
    printf("Testing EEPROM Read/Write...\n");
    
    // 写入数据
    printf("Writing 0x%02X to address 0x%04X\n", write_data, test_addr);
    if (EEPROM_WriteByte(test_addr, write_data) == 0) {
        printf("Write successful\n");
    } else {
        printf("Write failed\n");
        return;
    }
    
    // 读取数据
    if (EEPROM_ReadByte(test_addr, &read_data) == 0) {
        printf("Read data: 0x%02X\n", read_data);
        
        // 验证数据
        if (read_data == write_data) {
            printf("Test PASSED!\n");
        } else {
            printf("Test FAILED! Data mismatch\n");
        }
    } else {
        printf("Read failed\n");
    }
}
```

**预期结果**：
- 写入成功，无错误
- 读取的数据与写入的数据一致
- 串口输出显示"Test PASSED!"

## 步骤3：页写入优化

### 3.1 页写入原理

EEPROM支持页写入模式，可以一次写入多个字节（通常16-64字节），提高写入效率。

**AT24C256页写入特性**：
- 页大小：64字节
- 页边界：地址必须对齐到64字节边界
- 跨页写入：会回卷到页首，导致数据覆盖

```
页0: 0x0000 - 0x003F (64字节)
页1: 0x0040 - 0x007F (64字节)
页2: 0x0080 - 0x00BF (64字节)
...
```

### 3.2 页写入实现

```c
#define EEPROM_PAGE_SIZE 64

/**
 * @brief  页写入（不跨页）
 * @param  mem_addr: 起始地址
 * @param  data: 数据缓冲区
 * @param  length: 数据长度（不超过页大小）
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_PageWrite(uint16_t mem_addr, uint8_t *data, uint16_t length) {
    // 检查是否跨页
    uint16_t page_offset = mem_addr % EEPROM_PAGE_SIZE;
    if (page_offset + length > EEPROM_PAGE_SIZE) {
        return 1;  // 跨页错误
    }
    
    uint8_t buffer[EEPROM_PAGE_SIZE + 2];
    
    // 准备地址和数据
    buffer[0] = (mem_addr >> 8) & 0xFF;
    buffer[1] = mem_addr & 0xFF;
    memcpy(&buffer[2], data, length);
    
    // 发送数据
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        &hi2c1,
        EEPROM_I2C_ADDR,
        buffer,
        length + 2,
        HAL_MAX_DELAY
    );
    
    // 等待写入完成
    HAL_Delay(5);
    
    return (status == HAL_OK) ? 0 : 1;
}
```

### 3.3 多字节写入（自动分页）

```c
/**
 * @brief  写入多字节数据（自动处理分页）
 * @param  mem_addr: 起始地址
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_WriteMultiBytes(uint16_t mem_addr, uint8_t *data, uint16_t length) {
    uint16_t bytes_written = 0;
    
    while (bytes_written < length) {
        // 计算当前页剩余空间
        uint16_t current_addr = mem_addr + bytes_written;
        uint16_t page_offset = current_addr % EEPROM_PAGE_SIZE;
        uint16_t bytes_to_write = EEPROM_PAGE_SIZE - page_offset;
        
        // 不超过剩余数据长度
        if (bytes_to_write > (length - bytes_written)) {
            bytes_to_write = length - bytes_written;
        }
        
        // 写入当前页
        if (EEPROM_PageWrite(current_addr, &data[bytes_written], bytes_to_write) != 0) {
            return 1;  // 写入失败
        }
        
        bytes_written += bytes_to_write;
    }
    
    return 0;
}
```


### 3.4 多字节读取

```c
/**
 * @brief  读取多字节数据
 * @param  mem_addr: 起始地址
 * @param  data: 数据缓冲区
 * @param  length: 读取长度
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_ReadMultiBytes(uint16_t mem_addr, uint8_t *data, uint16_t length) {
    uint8_t addr_buffer[2];
    
    // 发送起始地址
    addr_buffer[0] = (mem_addr >> 8) & 0xFF;
    addr_buffer[1] = mem_addr & 0xFF;
    
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        &hi2c1,
        EEPROM_I2C_ADDR,
        addr_buffer,
        2,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) return 1;
    
    // 连续读取数据
    status = HAL_I2C_Master_Receive(
        &hi2c1,
        EEPROM_I2C_ADDR,
        data,
        length,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK) ? 0 : 1;
}
```

### 3.5 测试页写入

```c
void Test_PageWrite(void) {
    uint8_t write_buffer[64];
    uint8_t read_buffer[64];
    uint16_t test_addr = 0x0000;  // 页对齐地址
    
    // 准备测试数据
    for (int i = 0; i < 64; i++) {
        write_buffer[i] = i;
    }
    
    printf("Testing Page Write...\n");
    
    // 页写入
    if (EEPROM_PageWrite(test_addr, write_buffer, 64) == 0) {
        printf("Page write successful\n");
    } else {
        printf("Page write failed\n");
        return;
    }
    
    // 读取验证
    if (EEPROM_ReadMultiBytes(test_addr, read_buffer, 64) == 0) {
        // 比较数据
        int errors = 0;
        for (int i = 0; i < 64; i++) {
            if (read_buffer[i] != write_buffer[i]) {
                errors++;
                printf("Error at offset %d: wrote 0x%02X, read 0x%02X\n",
                       i, write_buffer[i], read_buffer[i]);
            }
        }
        
        if (errors == 0) {
            printf("Page write test PASSED!\n");
        } else {
            printf("Page write test FAILED! %d errors\n", errors);
        }
    }
}
```

## 步骤4：数据保护与校验

### 4.1 CRC校验

为确保数据完整性，添加CRC校验：

```c
#include <stdint.h>

/**
 * @brief  计算CRC-8校验值
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval CRC-8校验值
 */
uint8_t Calculate_CRC8(uint8_t *data, uint16_t length) {
    uint8_t crc = 0x00;
    
    for (uint16_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;  // CRC-8多项式
            } else {
                crc <<= 1;
            }
        }
    }
    
    return crc;
}

/**
 * @brief  带CRC校验的数据写入
 * @param  mem_addr: 起始地址
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_WriteWithCRC(uint16_t mem_addr, uint8_t *data, uint16_t length) {
    // 计算CRC
    uint8_t crc = Calculate_CRC8(data, length);
    
    // 写入数据
    if (EEPROM_WriteMultiBytes(mem_addr, data, length) != 0) {
        return 1;
    }
    
    // 写入CRC（紧跟数据后）
    if (EEPROM_WriteByte(mem_addr + length, crc) != 0) {
        return 1;
    }
    
    return 0;
}

/**
 * @brief  带CRC校验的数据读取
 * @param  mem_addr: 起始地址
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval 0=成功且校验通过, 1=失败, 2=校验错误
 */
uint8_t EEPROM_ReadWithCRC(uint16_t mem_addr, uint8_t *data, uint16_t length) {
    uint8_t stored_crc;
    
    // 读取数据
    if (EEPROM_ReadMultiBytes(mem_addr, data, length) != 0) {
        return 1;
    }
    
    // 读取CRC
    if (EEPROM_ReadByte(mem_addr + length, &stored_crc) != 0) {
        return 1;
    }
    
    // 验证CRC
    uint8_t calculated_crc = Calculate_CRC8(data, length);
    if (calculated_crc != stored_crc) {
        return 2;  // CRC校验失败
    }
    
    return 0;
}
```


### 4.2 数据结构设计

设计带版本和校验的数据结构：

```c
// 配置数据结构
typedef struct {
    uint32_t magic;          // 魔数，用于识别有效数据
    uint16_t version;        // 数据版本
    uint16_t length;         // 数据长度
    uint8_t  data[56];       // 实际数据（56字节）
    uint8_t  crc;            // CRC校验值
    uint8_t  reserved[3];    // 保留字节（对齐到64字节）
} Config_Data_t;

#define CONFIG_MAGIC 0x12345678
#define CONFIG_VERSION 1
#define CONFIG_ADDR 0x0000

/**
 * @brief  保存配置数据
 * @param  config: 配置数据指针
 * @retval 0=成功, 1=失败
 */
uint8_t Config_Save(Config_Data_t *config) {
    // 设置魔数和版本
    config->magic = CONFIG_MAGIC;
    config->version = CONFIG_VERSION;
    config->length = sizeof(config->data);
    
    // 计算CRC（不包括CRC字段本身）
    config->crc = Calculate_CRC8((uint8_t*)config, 
                                  sizeof(Config_Data_t) - 4);
    
    // 写入EEPROM
    return EEPROM_PageWrite(CONFIG_ADDR, (uint8_t*)config, 
                            sizeof(Config_Data_t));
}

/**
 * @brief  加载配置数据
 * @param  config: 配置数据指针
 * @retval 0=成功, 1=失败, 2=数据无效
 */
uint8_t Config_Load(Config_Data_t *config) {
    // 从EEPROM读取
    if (EEPROM_ReadMultiBytes(CONFIG_ADDR, (uint8_t*)config, 
                              sizeof(Config_Data_t)) != 0) {
        return 1;
    }
    
    // 验证魔数
    if (config->magic != CONFIG_MAGIC) {
        return 2;  // 数据无效
    }
    
    // 验证版本
    if (config->version != CONFIG_VERSION) {
        return 2;  // 版本不匹配
    }
    
    // 验证CRC
    uint8_t calculated_crc = Calculate_CRC8((uint8_t*)config, 
                                            sizeof(Config_Data_t) - 4);
    if (calculated_crc != config->crc) {
        return 2;  // CRC校验失败
    }
    
    return 0;
}
```

### 4.3 默认值处理

```c
/**
 * @brief  初始化默认配置
 * @param  config: 配置数据指针
 */
void Config_SetDefaults(Config_Data_t *config) {
    memset(config, 0, sizeof(Config_Data_t));
    
    // 设置默认值
    config->data[0] = 100;  // 示例：默认亮度
    config->data[1] = 50;   // 示例：默认音量
    config->data[2] = 1;    // 示例：默认启用状态
    // ... 其他默认值
}

/**
 * @brief  配置系统初始化
 * @param  config: 配置数据指针
 */
void Config_Init(Config_Data_t *config) {
    uint8_t result = Config_Load(config);
    
    if (result == 0) {
        printf("Configuration loaded successfully\n");
    } else {
        printf("Failed to load configuration, using defaults\n");
        Config_SetDefaults(config);
        Config_Save(config);  // 保存默认配置
    }
}
```

## 步骤5：磨损均衡

### 5.1 简单的磨损均衡策略

EEPROM的擦写次数有限（约100万次），频繁写入同一地址会缩短寿命。

**磨损均衡原理**：
- 将数据分散到多个位置
- 轮流使用不同的存储区域
- 记录写入次数，选择使用最少的区域

```c
#define WEAR_LEVEL_COPIES 4  // 保存4份副本
#define WEAR_LEVEL_BASE_ADDR 0x0000
#define WEAR_LEVEL_COPY_SIZE 64

typedef struct {
    uint32_t write_count;    // 写入次数
    uint8_t  data[60];       // 实际数据
} WearLevel_Data_t;

/**
 * @brief  磨损均衡写入
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval 0=成功, 1=失败
 */
uint8_t WearLevel_Write(uint8_t *data, uint16_t length) {
    WearLevel_Data_t wl_data;
    uint32_t min_count = 0xFFFFFFFF;
    uint8_t min_index = 0;
    
    // 查找写入次数最少的副本
    for (uint8_t i = 0; i < WEAR_LEVEL_COPIES; i++) {
        uint16_t addr = WEAR_LEVEL_BASE_ADDR + (i * WEAR_LEVEL_COPY_SIZE);
        
        // 读取写入次数
        uint32_t count;
        EEPROM_ReadMultiBytes(addr, (uint8_t*)&count, sizeof(count));
        
        if (count < min_count) {
            min_count = count;
            min_index = i;
        }
    }
    
    // 准备数据
    wl_data.write_count = min_count + 1;
    memcpy(wl_data.data, data, length);
    
    // 写入到选定的副本
    uint16_t addr = WEAR_LEVEL_BASE_ADDR + (min_index * WEAR_LEVEL_COPY_SIZE);
    return EEPROM_PageWrite(addr, (uint8_t*)&wl_data, sizeof(wl_data));
}
```


### 5.2 读取最新数据

```c
/**
 * @brief  磨损均衡读取（读取最新的副本）
 * @param  data: 数据缓冲区
 * @param  length: 数据长度
 * @retval 0=成功, 1=失败
 */
uint8_t WearLevel_Read(uint8_t *data, uint16_t length) {
    WearLevel_Data_t wl_data;
    uint32_t max_count = 0;
    uint8_t max_index = 0;
    
    // 查找写入次数最多的副本（最新数据）
    for (uint8_t i = 0; i < WEAR_LEVEL_COPIES; i++) {
        uint16_t addr = WEAR_LEVEL_BASE_ADDR + (i * WEAR_LEVEL_COPY_SIZE);
        
        // 读取写入次数
        uint32_t count;
        EEPROM_ReadMultiBytes(addr, (uint8_t*)&count, sizeof(count));
        
        if (count > max_count && count != 0xFFFFFFFF) {
            max_count = count;
            max_index = i;
        }
    }
    
    // 读取最新的副本
    uint16_t addr = WEAR_LEVEL_BASE_ADDR + (max_index * WEAR_LEVEL_COPY_SIZE);
    if (EEPROM_ReadMultiBytes(addr, (uint8_t*)&wl_data, sizeof(wl_data)) != 0) {
        return 1;
    }
    
    // 复制数据
    memcpy(data, wl_data.data, length);
    return 0;
}
```

## 步骤6：实际应用示例

### 6.1 系统参数管理

```c
// 系统参数结构
typedef struct {
    // 显示设置
    uint8_t brightness;      // 亮度 (0-100)
    uint8_t contrast;        // 对比度 (0-100)
    
    // 音频设置
    uint8_t volume;          // 音量 (0-100)
    uint8_t mute;            // 静音 (0/1)
    
    // 网络设置
    uint8_t ip_addr[4];      // IP地址
    uint16_t port;           // 端口号
    
    // 用户设置
    char username[16];       // 用户名
    uint32_t user_id;        // 用户ID
    
    // 运行统计
    uint32_t run_time;       // 运行时间（秒）
    uint32_t power_cycles;   // 开机次数
} System_Params_t;

System_Params_t g_system_params;

/**
 * @brief  系统参数初始化
 */
void SystemParams_Init(void) {
    Config_Data_t config;
    
    if (Config_Load(&config) == 0) {
        // 加载成功，解析参数
        memcpy(&g_system_params, config.data, sizeof(System_Params_t));
        printf("System parameters loaded\n");
        
        // 更新开机次数
        g_system_params.power_cycles++;
        SystemParams_Save();
    } else {
        // 加载失败，使用默认值
        printf("Using default parameters\n");
        SystemParams_SetDefaults();
        SystemParams_Save();
    }
}

/**
 * @brief  设置默认参数
 */
void SystemParams_SetDefaults(void) {
    memset(&g_system_params, 0, sizeof(System_Params_t));
    
    // 显示设置
    g_system_params.brightness = 80;
    g_system_params.contrast = 50;
    
    // 音频设置
    g_system_params.volume = 50;
    g_system_params.mute = 0;
    
    // 网络设置
    g_system_params.ip_addr[0] = 192;
    g_system_params.ip_addr[1] = 168;
    g_system_params.ip_addr[2] = 1;
    g_system_params.ip_addr[3] = 100;
    g_system_params.port = 8080;
    
    // 用户设置
    strcpy(g_system_params.username, "admin");
    g_system_params.user_id = 1;
    
    // 运行统计
    g_system_params.run_time = 0;
    g_system_params.power_cycles = 1;
}

/**
 * @brief  保存系统参数
 */
void SystemParams_Save(void) {
    Config_Data_t config;
    
    // 复制参数到配置结构
    memcpy(config.data, &g_system_params, sizeof(System_Params_t));
    
    // 保存到EEPROM
    if (Config_Save(&config) == 0) {
        printf("System parameters saved\n");
    } else {
        printf("Failed to save parameters\n");
    }
}

/**
 * @brief  更新单个参数
 */
void SystemParams_SetBrightness(uint8_t value) {
    if (value <= 100) {
        g_system_params.brightness = value;
        SystemParams_Save();
    }
}

void SystemParams_SetVolume(uint8_t value) {
    if (value <= 100) {
        g_system_params.volume = value;
        SystemParams_Save();
    }
}
```

### 6.2 运行时间记录

```c
/**
 * @brief  定时更新运行时间（每秒调用一次）
 */
void SystemParams_UpdateRunTime(void) {
    static uint32_t save_counter = 0;
    
    g_system_params.run_time++;
    save_counter++;
    
    // 每60秒保存一次（减少EEPROM写入次数）
    if (save_counter >= 60) {
        SystemParams_Save();
        save_counter = 0;
    }
}
```


### 6.3 完整示例程序

```c
int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    I2C_Init();
    UART_Init();
    
    printf("\n=== EEPROM Storage System ===\n");
    
    // 初始化系统参数
    SystemParams_Init();
    
    // 显示当前参数
    printf("\nCurrent Parameters:\n");
    printf("  Brightness: %d\n", g_system_params.brightness);
    printf("  Volume: %d\n", g_system_params.volume);
    printf("  IP: %d.%d.%d.%d:%d\n",
           g_system_params.ip_addr[0],
           g_system_params.ip_addr[1],
           g_system_params.ip_addr[2],
           g_system_params.ip_addr[3],
           g_system_params.port);
    printf("  Username: %s\n", g_system_params.username);
    printf("  Run Time: %lu seconds\n", g_system_params.run_time);
    printf("  Power Cycles: %lu\n", g_system_params.power_cycles);
    
    // 主循环
    while (1) {
        // 每秒更新运行时间
        HAL_Delay(1000);
        SystemParams_UpdateRunTime();
        
        // 处理用户输入或其他任务
        // ...
    }
}
```

## 测试验证

### 测试1：基本读写测试

```c
void Test_Suite(void) {
    printf("\n=== EEPROM Test Suite ===\n\n");
    
    // 测试1：单字节读写
    printf("Test 1: Single Byte Read/Write\n");
    Test_BasicReadWrite();
    
    // 测试2：页写入
    printf("\nTest 2: Page Write\n");
    Test_PageWrite();
    
    // 测试3：CRC校验
    printf("\nTest 3: CRC Verification\n");
    Test_CRCVerification();
    
    // 测试4：配置保存加载
    printf("\nTest 4: Configuration Save/Load\n");
    Test_ConfigSaveLoad();
    
    printf("\n=== All Tests Complete ===\n");
}
```

### 测试2：CRC校验测试

```c
void Test_CRCVerification(void) {
    uint8_t test_data[32];
    uint8_t read_data[32];
    uint16_t test_addr = 0x0200;
    
    // 准备测试数据
    for (int i = 0; i < 32; i++) {
        test_data[i] = i * 2;
    }
    
    // 写入带CRC的数据
    if (EEPROM_WriteWithCRC(test_addr, test_data, 32) == 0) {
        printf("Write with CRC successful\n");
    } else {
        printf("Write with CRC failed\n");
        return;
    }
    
    // 读取并验证
    uint8_t result = EEPROM_ReadWithCRC(test_addr, read_data, 32);
    if (result == 0) {
        printf("Read with CRC successful, data valid\n");
        
        // 验证数据
        int match = 1;
        for (int i = 0; i < 32; i++) {
            if (read_data[i] != test_data[i]) {
                match = 0;
                break;
            }
        }
        
        if (match) {
            printf("Test PASSED!\n");
        } else {
            printf("Test FAILED! Data mismatch\n");
        }
    } else if (result == 2) {
        printf("CRC verification failed\n");
    } else {
        printf("Read failed\n");
    }
}
```

### 测试3：掉电保护测试

```c
void Test_PowerLossProtection(void) {
    printf("Testing power loss protection...\n");
    
    // 保存当前参数
    uint8_t original_brightness = g_system_params.brightness;
    
    // 修改参数
    g_system_params.brightness = 75;
    SystemParams_Save();
    printf("Changed brightness to 75 and saved\n");
    
    // 模拟掉电重启（重新加载）
    printf("Simulating power loss...\n");
    SystemParams_Init();
    
    // 验证数据是否保持
    if (g_system_params.brightness == 75) {
        printf("Test PASSED! Data survived power loss\n");
    } else {
        printf("Test FAILED! Data lost: %d\n", g_system_params.brightness);
    }
    
    // 恢复原始值
    g_system_params.brightness = original_brightness;
    SystemParams_Save();
}
```

**预期结果**：
- 所有测试通过
- 数据读写正确
- CRC校验有效
- 掉电后数据保持

## 故障排除

### 问题1：无法检测到EEPROM

**现象**：
- I2C通信失败
- 读写操作返回错误

**可能原因**：
- 硬件连接错误
- 上拉电阻缺失或值不对
- 设备地址错误
- 电源电压不匹配

**解决方法**：
1. 检查硬件连接，确保SDA、SCL正确连接
2. 确认上拉电阻已连接（4.7kΩ）
3. 使用I2C扫描程序检测设备地址
4. 检查电源电压（3.3V或5V）

```c
// I2C设备扫描
void I2C_Scan(void) {
    printf("Scanning I2C bus...\n");
    
    for (uint8_t addr = 0x08; addr < 0x78; addr++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, addr << 1, 1, 10) == HAL_OK) {
            printf("Found device at address 0x%02X\n", addr);
        }
    }
    
    printf("Scan complete\n");
}
```


### 问题2：写入失败或数据错误

**现象**：
- 写入操作返回失败
- 读取的数据与写入不一致
- CRC校验失败

**可能原因**：
- 写保护引脚(WP)未正确连接
- 写入延时不足
- 跨页写入导致数据回卷
- 地址计算错误

**解决方法**：
1. 确保WP引脚接地（禁用写保护）
2. 写入后延时至少5ms
3. 检查页边界，避免跨页写入
4. 验证地址计算逻辑

```c
// 调试写入过程
uint8_t EEPROM_WriteByte_Debug(uint16_t mem_addr, uint8_t data) {
    printf("Writing 0x%02X to address 0x%04X\n", data, mem_addr);
    
    uint8_t result = EEPROM_WriteByte(mem_addr, data);
    
    if (result == 0) {
        // 读回验证
        uint8_t read_data;
        EEPROM_ReadByte(mem_addr, &read_data);
        
        if (read_data == data) {
            printf("Write verified OK\n");
        } else {
            printf("Write verification FAILED! Read 0x%02X\n", read_data);
        }
    } else {
        printf("Write operation FAILED\n");
    }
    
    return result;
}
```

### 问题3：数据丢失或损坏

**现象**：
- 重启后数据丢失
- 读取到全0xFF或全0x00
- CRC校验经常失败

**可能原因**：
- EEPROM寿命耗尽
- 电源不稳定导致写入中断
- 没有使用CRC校验
- 频繁写入同一地址

**解决方法**：
1. 实现磨损均衡，分散写入
2. 添加CRC校验保护数据
3. 使用多副本备份重要数据
4. 减少不必要的写入操作
5. 确保电源稳定

```c
// 健康检查
void EEPROM_HealthCheck(void) {
    uint8_t test_data = 0xA5;
    uint8_t read_data;
    uint16_t test_addr = 0x7F00;  // 使用末尾地址测试
    
    printf("EEPROM Health Check...\n");
    
    // 写入测试
    if (EEPROM_WriteByte(test_addr, test_data) != 0) {
        printf("WARNING: Write operation failed\n");
        return;
    }
    
    // 读取测试
    if (EEPROM_ReadByte(test_addr, &read_data) != 0) {
        printf("WARNING: Read operation failed\n");
        return;
    }
    
    // 验证数据
    if (read_data == test_data) {
        printf("EEPROM health: OK\n");
    } else {
        printf("WARNING: Data corruption detected\n");
        printf("  Wrote: 0x%02X, Read: 0x%02X\n", test_data, read_data);
    }
}
```

### 问题4：I2C通信速度慢

**现象**：
- 读写操作耗时过长
- 系统响应缓慢

**可能原因**：
- I2C时钟频率设置过低
- 使用轮询方式等待
- 没有使用页写入优化

**解决方法**：
1. 提高I2C时钟频率（100kHz → 400kHz）
2. 使用DMA或中断方式
3. 使用页写入代替单字节写入
4. 批量操作，减少通信次数

```c
// 性能测试
void EEPROM_PerformanceTest(void) {
    uint8_t buffer[64];
    uint32_t start_time, end_time;
    
    // 准备测试数据
    for (int i = 0; i < 64; i++) {
        buffer[i] = i;
    }
    
    // 测试单字节写入
    start_time = HAL_GetTick();
    for (int i = 0; i < 64; i++) {
        EEPROM_WriteByte(0x0100 + i, buffer[i]);
    }
    end_time = HAL_GetTick();
    printf("Single byte write (64 bytes): %lu ms\n", end_time - start_time);
    
    // 测试页写入
    start_time = HAL_GetTick();
    EEPROM_PageWrite(0x0200, buffer, 64);
    end_time = HAL_GetTick();
    printf("Page write (64 bytes): %lu ms\n", end_time - start_time);
}
```

## 最佳实践

### 1. 减少写入次数

```c
// 不好的做法：频繁写入
void Bad_Practice(void) {
    for (int i = 0; i < 1000; i++) {
        sensor_value = Read_Sensor();
        EEPROM_WriteByte(0x0000, sensor_value);  // 每次都写入
        HAL_Delay(100);
    }
}

// 好的做法：批量写入或定时写入
void Good_Practice(void) {
    uint8_t buffer[100];
    uint8_t index = 0;
    
    for (int i = 0; i < 1000; i++) {
        sensor_value = Read_Sensor();
        buffer[index++] = sensor_value;
        
        // 缓冲区满时才写入
        if (index >= 100) {
            EEPROM_WriteMultiBytes(0x0000, buffer, 100);
            index = 0;
        }
        
        HAL_Delay(100);
    }
}
```

### 2. 使用缓存机制

```c
// 参数缓存
typedef struct {
    System_Params_t params;
    uint8_t dirty;  // 脏标志
} Params_Cache_t;

Params_Cache_t g_params_cache;

void Params_SetBrightness(uint8_t value) {
    g_params_cache.params.brightness = value;
    g_params_cache.dirty = 1;  // 标记为已修改
}

void Params_Flush(void) {
    if (g_params_cache.dirty) {
        SystemParams_Save();
        g_params_cache.dirty = 0;
    }
}

// 定时刷新（例如每分钟）
void Timer_Callback(void) {
    Params_Flush();
}
```

### 3. 数据版本管理

```c
// 支持多版本数据迁移
uint8_t Config_LoadWithMigration(Config_Data_t *config) {
    if (EEPROM_ReadMultiBytes(CONFIG_ADDR, (uint8_t*)config, 
                              sizeof(Config_Data_t)) != 0) {
        return 1;
    }
    
    // 检查版本
    if (config->version < CONFIG_VERSION) {
        printf("Migrating from v%d to v%d\n", 
               config->version, CONFIG_VERSION);
        
        // 执行数据迁移
        Config_Migrate(config);
        
        // 保存新版本
        config->version = CONFIG_VERSION;
        Config_Save(config);
    }
    
    return 0;
}
```


### 4. 错误处理和重试

```c
/**
 * @brief  带重试的EEPROM写入
 * @param  mem_addr: 内存地址
 * @param  data: 数据
 * @param  max_retries: 最大重试次数
 * @retval 0=成功, 1=失败
 */
uint8_t EEPROM_WriteByte_WithRetry(uint16_t mem_addr, uint8_t data, 
                                   uint8_t max_retries) {
    for (uint8_t retry = 0; retry < max_retries; retry++) {
        if (EEPROM_WriteByte(mem_addr, data) == 0) {
            // 写入成功，验证数据
            uint8_t read_data;
            if (EEPROM_ReadByte(mem_addr, &read_data) == 0) {
                if (read_data == data) {
                    return 0;  // 成功
                }
            }
        }
        
        // 失败，延时后重试
        HAL_Delay(10);
    }
    
    return 1;  // 所有重试都失败
}
```

### 5. 日志记录

```c
// 写入日志
typedef struct {
    uint32_t timestamp;
    uint8_t  event_type;
    uint8_t  data[3];
} Log_Entry_t;

#define LOG_BASE_ADDR 0x1000
#define LOG_MAX_ENTRIES 100

uint16_t g_log_index = 0;

void Log_Write(uint8_t event_type, uint8_t *data) {
    Log_Entry_t entry;
    
    entry.timestamp = HAL_GetTick();
    entry.event_type = event_type;
    memcpy(entry.data, data, 3);
    
    // 计算地址（循环缓冲区）
    uint16_t addr = LOG_BASE_ADDR + 
                    ((g_log_index % LOG_MAX_ENTRIES) * sizeof(Log_Entry_t));
    
    // 写入日志
    EEPROM_WriteMultiBytes(addr, (uint8_t*)&entry, sizeof(Log_Entry_t));
    
    g_log_index++;
}
```

## 总结

通过本教程，你学习了：

- ✅ EEPROM的工作原理和特点
- ✅ I2C接口EEPROM的硬件连接
- ✅ 基本的读写操作实现
- ✅ 页写入优化技术
- ✅ CRC校验和数据保护
- ✅ 磨损均衡策略
- ✅ 系统参数管理的完整方案
- ✅ 故障排除和最佳实践

**关键要点**：

1. **数据保护**
   - 使用CRC校验确保数据完整性
   - 添加魔数和版本号识别有效数据
   - 实现多副本备份重要数据

2. **寿命管理**
   - 减少不必要的写入操作
   - 使用磨损均衡分散写入
   - 批量写入代替频繁单字节写入

3. **可靠性设计**
   - 实现写入验证和重试机制
   - 提供默认值和数据迁移
   - 定期进行健康检查

4. **性能优化**
   - 使用页写入提高效率
   - 实现缓存机制减少访问
   - 合理设置I2C时钟频率

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现一个环形缓冲区日志系统，支持自动覆盖旧数据
2. **挑战2**：添加数据压缩功能，提高存储容量利用率
3. **挑战3**：实现SPI接口EEPROM驱动，对比I2C和SPI的性能
4. **挑战4**：设计一个文件系统，支持多个文件的存储和管理
5. **挑战5**：实现加密存储，保护敏感配置数据

## 完整代码

完整的项目代码可以在这里下载：
- [GitHub仓库](https://github.com/embedded-platform/eeprom-storage-tutorial)
- 包含STM32和Arduino两个版本
- 包含所有示例和测试代码

## 下一步

建议继续学习：

- [Flash存储器技术详解](./01-flash-technology.html) - 了解Flash与EEPROM的区别
- [Flash磨损均衡算法](../intermediate/01-wear-leveling.html) - 深入学习磨损均衡
- [数据持久化与掉电保护](../intermediate/02-data-persistence.html) - 高级数据保护技术
- [LittleFS轻量级文件系统](../../01-file-systems/beginner/02-littlefs.html) - 在Flash上实现文件系统

## 参考资料

1. **芯片数据手册**
   - Microchip AT24C256 Datasheet
   - STMicroelectronics M24C64 Datasheet

2. **应用笔记**
   - AN2578: EEPROM Emulation in STM32
   - AN1028: Software Techniques for Improving System Reliability

3. **标准和协议**
   - I2C-bus Specification (NXP)
   - SPI Protocol Specification

4. **在线资源**
   - [I2C总线协议详解](https://www.i2c-bus.org/)
   - [EEPROM应用指南](https://www.microchip.com/eeprom)

---

**练习题**：

1. 解释EEPROM和Flash存储器的主要区别，并说明各自的应用场景
2. 编写一个函数，实现EEPROM的批量擦除功能（写入0xFF）
3. 设计一个数据结构，支持存储10个用户的配置信息
4. 计算：如果每天写入100次，EEPROM（100万次擦写）能使用多少年？
5. 实现一个简单的文件系统，支持创建、读取、删除文件

**思考题**：

1. 为什么EEPROM写入需要延时？如何确定合适的延时时间？
2. 在什么情况下应该使用EEPROM而不是Flash？
3. 如何设计一个既节省EEPROM寿命又能快速响应的参数保存方案？
4. 如果EEPROM容量不足，有哪些优化策略？

---

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言或提交Issue！

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。
