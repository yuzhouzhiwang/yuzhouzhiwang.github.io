---
# 基础信息
title: "光照与气压传感器应用"
description: "全面讲解光照传感器BH1750和气压传感器BMP280的工作原理、I2C通信接口使用和实际应用开发，包括环境监测、高度测量等应用场景"
slug: "light-pressure-sensor"

# 分类信息
domain: "01-hardware-layer"
module: "04-sensor-technology"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 光照传感器
  - 气压传感器
  - 环境监测
  - BH1750
  - BMP280
  - I2C
prerequisites:
  - "01-chip-architecture/beginner/07-register-operations"
  - "02-hardware-design-fundamentals/beginner/08-interface-circuits"
related_contents:
  - "01-temperature-humidity-sensor"
  - "02-accelerometer-gyroscope"

# 学习信息
estimated_time: 55
difficulty_score: 2

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-03-07"
updated_at: "2026-03-07"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 光照传感器
  - 气压传感器
  - BH1750
  - BMP280
  - 环境监测
  - 高度测量
cover_image: ""
---

# 光照与气压传感器应用

## 概述

光照传感器和气压传感器是环境监测系统中的重要组成部分。光照传感器用于测量环境光强度，广泛应用于自动照明控制、显示屏亮度调节等场景；气压传感器用于测量大气压力，可用于天气预报、高度测量、室内外检测等应用。本教程将介绍BH1750光照传感器和BMP280气压传感器的使用方法。

### 为什么需要光照和气压传感器

1. **光照传感器应用**：
   - 自动照明控制（路灯、室内灯）
   - 显示屏亮度自适应
   - 光照强度监测
   - 植物生长环境监测
   - 节能管理系统

2. **气压传感器应用**：
   - 天气预报和气象监测
   - 高度和楼层检测
   - 室内外位置判断
   - 运动追踪（爬楼、登山）
   - 无人机高度控制

3. **组合应用优势**：
   - 完整的环境监测
   - 多维度数据分析
   - 提高系统智能化
   - 增强用户体验

### 传感器对比

```
传感器参数对比：

┌──────────┬─────────────┬─────────────┬─────────────┐
│ 参数     │ BH1750      │ BMP280      │ BME280      │
├──────────┼─────────────┼─────────────┼─────────────┤
│ 测量类型 │ 光照强度    │ 气压+温度   │ 气压+温湿度 │
│ 测量范围 │ 1-65535 lux │ 300-1100hPa │ 300-1100hPa │
│ 精度     │ ±20%        │ ±1 hPa      │ ±1 hPa      │
│ 接口     │ I2C         │ I2C/SPI     │ I2C/SPI     │
│ 电压     │ 2.4-3.6V    │ 1.71-3.6V   │ 1.71-3.6V   │
│ 功耗     │ 0.12mA      │ 2.7μA       │ 3.6μA       │
│ 价格     │ 低          │ 中          │ 中高        │
│ 适用场景 │ 光照检测    │ 气压测量    │ 综合环境    │
└──────────┴─────────────┴─────────────┴─────────────┘

选型建议：
- 仅需光照：BH1750（简单、便宜）
- 气压+温度：BMP280（性价比高）
- 完整环境：BME280（功能全面）
- 高精度气压：BMP388（更高精度）
```



## 第一部分：BH1750光照传感器

### 硬件连接

**BH1750引脚定义**：

```
BH1750引脚（5针封装）：

    ┌─────────┐
    │ BH1750  │
    └─┬─┬─┬─┬─┬─┘
      1 2 3 4 5

引脚说明：
1. VCC  - 电源正极（2.4V-3.6V）
2. GND  - 电源地
3. SCL  - I2C时钟线
4. SDA  - I2C数据线
5. ADDR - I2C地址选择

I2C地址：
- ADDR接GND或悬空: 0x23
- ADDR接VCC: 0x5C
```

**硬件连接电路**：

```
连接方案：

MCU                    BH1750传感器
                      ┌─────────┐
3.3V ─────────────────┤1 VCC    │
                      │         │
GND ──────────────────┤2 GND    │
                      │         │
SCL ──────┬───────────┤3 SCL    │
          │           │         │
         ┌┴┐          │4 SDA    │
    4.7k │ │          │         │
         └┬┘          │5 ADDR   │──┐
          │           └─────────┘  │
SDA ──────┼──┬────────────────────┘
          │  │                      
         ┌┴┐ │        接GND选择0x23
    4.7k │ │ │        接VCC选择0x5C
         └┬┘ │        
          │  │        
GND ──────┴──┘        

关键要点：
1. SDA和SCL需要上拉电阻（4.7kΩ）
2. 支持标准模式（100kHz）和快速模式（400kHz）
3. ADDR引脚选择I2C地址
4. 建议使用3.3V供电
```

### I2C通信协议

**BH1750命令集**：

```
常用命令：

1. 电源控制：
   - Power Down: 0x00
   - Power On: 0x01

2. 测量模式：
   - 连续H分辨率模式: 0x10 (1 lux分辨率)
   - 连续H分辨率模式2: 0x11 (0.5 lux分辨率)
   - 连续L分辨率模式: 0x13 (4 lux分辨率)
   - 单次H分辨率模式: 0x20
   - 单次H分辨率模式2: 0x21
   - 单次L分辨率模式: 0x23

3. 测量时间：
   - H分辨率模式: 120ms
   - H分辨率模式2: 120ms
   - L分辨率模式: 16ms

4. 灵敏度调整：
   - 改变测量时间: 0x40-0x7F (高位)
   - 改变测量时间: 0x60-0x7F (低位)

数据格式：
[高字节][低字节]

光照度计算：
Lux = (高字节 << 8 | 低字节) / 1.2
```



### BH1750驱动代码实现

**驱动头文件**：


```c
/**
 * @file    bh1750.h
 * @brief   BH1750光照传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __BH1750_H
#define __BH1750_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>

/**
 * @brief  BH1750 I2C地址
 */
#define BH1750_ADDR_LOW   0x23    // ADDR引脚接GND
#define BH1750_ADDR_HIGH  0x5C    // ADDR引脚接VCC

/**
 * @brief  BH1750命令
 */
#define BH1750_POWER_DOWN         0x00    // 关闭
#define BH1750_POWER_ON           0x01    // 开启
#define BH1750_RESET              0x07    // 复位
#define BH1750_CONT_H_RES_MODE    0x10    // 连续H分辨率
#define BH1750_CONT_H_RES_MODE2   0x11    // 连续H分辨率2
#define BH1750_CONT_L_RES_MODE    0x13    // 连续L分辨率
#define BH1750_ONE_H_RES_MODE     0x20    // 单次H分辨率
#define BH1750_ONE_H_RES_MODE2    0x21    // 单次H分辨率2
#define BH1750_ONE_L_RES_MODE     0x23    // 单次L分辨率

/**
 * @brief  BH1750测量模式
 */
typedef enum {
    BH1750_MODE_CONT_H_RES = 0,     // 连续H分辨率（1 lux）
    BH1750_MODE_CONT_H_RES2,        // 连续H分辨率2（0.5 lux）
    BH1750_MODE_CONT_L_RES,         // 连续L分辨率（4 lux）
    BH1750_MODE_ONE_H_RES,          // 单次H分辨率
    BH1750_MODE_ONE_H_RES2,         // 单次H分辨率2
    BH1750_MODE_ONE_L_RES           // 单次L分辨率
} BH1750_Mode;

/**
 * @brief  BH1750配置
 */
typedef struct {
    I2C_HandleTypeDef* hi2c;    // I2C句柄
    uint8_t address;            // I2C地址
    BH1750_Mode mode;           // 测量模式
} BH1750_Config;

// 函数声明
bool BH1750_Init(BH1750_Config* config);
bool BH1750_ReadLight(BH1750_Config* config, float* lux);
bool BH1750_SetMode(BH1750_Config* config, BH1750_Mode mode);
bool BH1750_PowerDown(BH1750_Config* config);
bool BH1750_PowerOn(BH1750_Config* config);

#endif /* __BH1750_H */
```

**驱动实现文件**：

```c
/**
 * @file    bh1750.c
 * @brief   BH1750光照传感器驱动实现
 */

#include "bh1750.h"

// 私有函数声明
static bool BH1750_WriteCommand(BH1750_Config* config, uint8_t cmd);
static bool BH1750_ReadData(BH1750_Config* config, uint16_t* data);

/**
 * @brief  写入命令
 * @param  config: 传感器配置
 * @param  cmd: 命令
 * @retval true: 成功, false: 失败
 */
static bool BH1750_WriteCommand(BH1750_Config* config, uint8_t cmd) {
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        config->hi2c,
        config->address << 1,
        &cmd,
        1,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取数据
 * @param  config: 传感器配置
 * @param  data: 数据指针
 * @retval true: 成功, false: 失败
 */
static bool BH1750_ReadData(BH1750_Config* config, uint16_t* data) {
    uint8_t buffer[2];
    
    HAL_StatusTypeDef status = HAL_I2C_Master_Receive(
        config->hi2c,
        config->address << 1,
        buffer,
        2,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) {
        return false;
    }
    
    *data = (buffer[0] << 8) | buffer[1];
    return true;
}

/**
 * @brief  初始化BH1750传感器
 * @param  config: 传感器配置
 * @retval true: 成功, false: 失败
 */
bool BH1750_Init(BH1750_Config* config) {
    // 上电
    if (!BH1750_PowerOn(config)) {
        return false;
    }
    
    HAL_Delay(10);
    
    // 设置测量模式
    if (!BH1750_SetMode(config, config->mode)) {
        return false;
    }
    
    return true;
}

/**
 * @brief  上电
 * @param  config: 传感器配置
 * @retval true: 成功, false: 失败
 */
bool BH1750_PowerOn(BH1750_Config* config) {
    return BH1750_WriteCommand(config, BH1750_POWER_ON);
}

/**
 * @brief  关闭
 * @param  config: 传感器配置
 * @retval true: 成功, false: 失败
 */
bool BH1750_PowerDown(BH1750_Config* config) {
    return BH1750_WriteCommand(config, BH1750_POWER_DOWN);
}

/**
 * @brief  设置测量模式
 * @param  config: 传感器配置
 * @param  mode: 测量模式
 * @retval true: 成功, false: 失败
 */
bool BH1750_SetMode(BH1750_Config* config, BH1750_Mode mode) {
    uint8_t cmd;
    
    switch (mode) {
        case BH1750_MODE_CONT_H_RES:
            cmd = BH1750_CONT_H_RES_MODE;
            break;
        case BH1750_MODE_CONT_H_RES2:
            cmd = BH1750_CONT_H_RES_MODE2;
            break;
        case BH1750_MODE_CONT_L_RES:
            cmd = BH1750_CONT_L_RES_MODE;
            break;
        case BH1750_MODE_ONE_H_RES:
            cmd = BH1750_ONE_H_RES_MODE;
            break;
        case BH1750_MODE_ONE_H_RES2:
            cmd = BH1750_ONE_H_RES_MODE2;
            break;
        case BH1750_MODE_ONE_L_RES:
            cmd = BH1750_ONE_L_RES_MODE;
            break;
        default:
            return false;
    }
    
    config->mode = mode;
    return BH1750_WriteCommand(config, cmd);
}

/**
 * @brief  读取光照强度
 * @param  config: 传感器配置
 * @param  lux: 光照强度指针（lux）
 * @retval true: 成功, false: 失败
 */
bool BH1750_ReadLight(BH1750_Config* config, float* lux) {
    uint16_t raw_data;
    
    // 如果是单次模式，需要先发送测量命令
    if (config->mode >= BH1750_MODE_ONE_H_RES) {
        if (!BH1750_SetMode(config, config->mode)) {
            return false;
        }
        
        // 等待测量完成
        if (config->mode == BH1750_MODE_ONE_L_RES) {
            HAL_Delay(24);  // L分辨率模式：16ms + 余量
        } else {
            HAL_Delay(180);  // H分辨率模式：120ms + 余量
        }
    }
    
    // 读取数据
    if (!BH1750_ReadData(config, &raw_data)) {
        return false;
    }
    
    // 计算光照强度
    // 公式：Lux = raw_data / 1.2
    *lux = (float)raw_data / 1.2f;
    
    return true;
}
```



### BH1750使用示例

```c
/**
 * @file    main.c
 * @brief   BH1750传感器使用示例
 */

#include "stm32f1xx_hal.h"
#include "bh1750.h"
#include <stdio.h>

// I2C句柄（需要在CubeMX中配置）
extern I2C_HandleTypeDef hi2c1;

// BH1750传感器配置
BH1750_Config bh1750_config = {
    .hi2c = &hi2c1,
    .address = BH1750_ADDR_LOW,
    .mode = BH1750_MODE_CONT_H_RES    // 连续高分辨率模式
};

/**
 * @brief  主函数
 */
int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化I2C
    MX_I2C1_Init();
    
    // 初始化UART（用于打印）
    MX_USART1_UART_Init();
    
    printf("BH1750光照传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化BH1750传感器
    if (!BH1750_Init(&bh1750_config)) {
        printf("❌ BH1750初始化失败！\n");
        printf("请检查：\n");
        printf("  1. I2C连接是否正确\n");
        printf("  2. 上拉电阻是否存在\n");
        printf("  3. 传感器地址是否正确\n");
        while (1);
    }
    
    printf("✓ BH1750初始化成功\n\n");
    
    float lux;
    uint32_t read_count = 0;
    
    while (1) {
        // 读取光照强度
        if (BH1750_ReadLight(&bh1750_config, &lux)) {
            read_count++;
            
            // 打印数据
            printf("读取 #%lu:\n", read_count);
            printf("  光照强度: %.1f lux\n", lux);
            
            // 光照等级评估
            if (lux < 10) {
                printf("  等级: 黑暗 🌑\n");
            } else if (lux < 50) {
                printf("  等级: 昏暗 🌘\n");
            } else if (lux < 200) {
                printf("  等级: 室内照明 💡\n");
            } else if (lux < 1000) {
                printf("  等级: 明亮 ☀️\n");
            } else {
                printf("  等级: 强光 ☀️☀️\n");
            }
            
            printf("\n");
        } else {
            printf("读取失败\n\n");
        }
        
        // 每秒读取一次
        HAL_Delay(1000);
    }
}

/**
 * @brief  自动照明控制示例
 */
void auto_lighting_control(void) {
    const float LIGHT_THRESHOLD_LOW = 50.0f;   // 开灯阈值
    const float LIGHT_THRESHOLD_HIGH = 100.0f; // 关灯阈值
    
    float lux;
    bool light_on = false;
    
    printf("自动照明控制系统\n");
    printf("═══════════════════════════════════════\n");
    printf("开灯阈值: %.1f lux\n", LIGHT_THRESHOLD_LOW);
    printf("关灯阈值: %.1f lux\n\n", LIGHT_THRESHOLD_HIGH);
    
    while (1) {
        if (BH1750_ReadLight(&bh1750_config, &lux)) {
            printf("当前光照: %.1f lux\n", lux);
            
            // 滞回控制，避免频繁开关
            if (!light_on && lux < LIGHT_THRESHOLD_LOW) {
                // 光照过低，开灯
                HAL_GPIO_WritePin(LIGHT_GPIO_Port, LIGHT_Pin, GPIO_PIN_SET);
                light_on = true;
                printf("💡 开灯\n");
            } else if (light_on && lux > LIGHT_THRESHOLD_HIGH) {
                // 光照充足，关灯
                HAL_GPIO_WritePin(LIGHT_GPIO_Port, LIGHT_Pin, GPIO_PIN_RESET);
                light_on = false;
                printf("🌙 关灯\n");
            } else {
                printf("状态: %s\n", light_on ? "开启" : "关闭");
            }
            
            printf("\n");
        }
        
        HAL_Delay(2000);
    }
}

/**
 * @brief  显示屏亮度自适应示例
 */
void display_brightness_control(void) {
    float lux;
    uint8_t brightness;
    
    printf("显示屏亮度自适应\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (BH1750_ReadLight(&bh1750_config, &lux)) {
            // 根据光照强度计算亮度（0-100%）
            if (lux < 10) {
                brightness = 10;  // 最低亮度
            } else if (lux > 1000) {
                brightness = 100;  // 最高亮度
            } else {
                // 对数映射
                brightness = (uint8_t)(10 + 90 * logf(lux / 10.0f) / logf(100.0f));
            }
            
            printf("光照: %.1f lux -> 亮度: %d%%\n", lux, brightness);
            
            // 设置PWM占空比控制背光
            __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, brightness);
        }
        
        HAL_Delay(500);
    }
}
```



## 第二部分：BMP280气压传感器

### 硬件连接

**BMP280引脚定义**：

```
BMP280引脚（6针封装）：

    ┌─────────┐
    │ BMP280  │
    └─┬─┬─┬─┬─┬─┬─┘
      1 2 3 4 5 6

引脚说明：
1. VCC  - 电源正极（1.71V-3.6V）
2. GND  - 电源地
3. SCL  - I2C时钟线 / SPI时钟线
4. SDA  - I2C数据线 / SPI MOSI
5. CSB  - 片选（I2C模式接VCC）
6. SDO  - I2C地址选择 / SPI MISO

I2C地址：
- SDO接GND: 0x76
- SDO接VCC: 0x77
```

**硬件连接电路（I2C模式）**：

```
连接方案：

MCU                    BMP280传感器
                      ┌─────────┐
3.3V ─────────────────┤1 VCC    │
                      │         │
GND ──────────────────┤2 GND    │
                      │         │
SCL ──────┬───────────┤3 SCL    │
          │           │         │
         ┌┴┐          │4 SDA    │
    4.7k │ │          │         │
         └┬┘          │5 CSB    │──── VCC (I2C模式)
          │           │         │
SDA ──────┼──┬────────┤6 SDO    │──┐
          │  │        └─────────┘  │
         ┌┴┐ │                      │
    4.7k │ │ │        接GND选择0x76
         └┬┘ │        接VCC选择0x77
          │  │        
GND ──────┴──┘        

关键要点：
1. SDA和SCL需要上拉电阻（4.7kΩ）
2. CSB接VCC选择I2C模式
3. SDO引脚选择I2C地址
4. 支持3.3V供电
```

### 寄存器和数据格式

**BMP280寄存器地址**：


```
重要寄存器：

0xD0: chip_id (固定值0x58)
0xE0: reset (写入0xB6复位)
0xF3: status (测量状态)
0xF4: ctrl_meas (测量控制)
0xF5: config (配置)
0xF7-0xF9: press_msb, press_lsb, press_xlsb (气压数据)
0xFA-0xFC: temp_msb, temp_lsb, temp_xlsb (温度数据)
0x88-0xA1: 校准参数

测量模式：
- Sleep模式: 00
- Forced模式: 01或10 (单次测量)
- Normal模式: 11 (连续测量)

过采样设置：
- 跳过: 000
- ×1: 001
- ×2: 010
- ×4: 011
- ×8: 100
- ×16: 101
```



### BMP280驱动代码实现

**驱动头文件**：

```c
/**
 * @file    bmp280.h
 * @brief   BMP280气压传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __BMP280_H
#define __BMP280_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>

/**
 * @brief  BMP280 I2C地址
 */
#define BMP280_ADDR_LOW   0x76    // SDO接GND
#define BMP280_ADDR_HIGH  0x77    // SDO接VCC

/**
 * @brief  BMP280寄存器地址
 */
#define BMP280_REG_CHIP_ID      0xD0
#define BMP280_REG_RESET        0xE0
#define BMP280_REG_STATUS       0xF3
#define BMP280_REG_CTRL_MEAS    0xF4
#define BMP280_REG_CONFIG       0xF5
#define BMP280_REG_PRESS_MSB    0xF7
#define BMP280_REG_TEMP_MSB     0xFA
#define BMP280_REG_CALIB_START  0x88

/**
 * @brief  BMP280芯片ID
 */
#define BMP280_CHIP_ID          0x58

/**
 * @brief  BMP280工作模式
 */
typedef enum {
    BMP280_MODE_SLEEP = 0,
    BMP280_MODE_FORCED = 1,
    BMP280_MODE_NORMAL = 3
} BMP280_Mode;

/**
 * @brief  BMP280过采样
 */
typedef enum {
    BMP280_OVERSAMPLING_SKIP = 0,
    BMP280_OVERSAMPLING_1X = 1,
    BMP280_OVERSAMPLING_2X = 2,
    BMP280_OVERSAMPLING_4X = 3,
    BMP280_OVERSAMPLING_8X = 4,
    BMP280_OVERSAMPLING_16X = 5
} BMP280_Oversampling;

/**
 * @brief  BMP280校准参数
 */
typedef struct {
    uint16_t dig_T1;
    int16_t dig_T2;
    int16_t dig_T3;
    uint16_t dig_P1;
    int16_t dig_P2;
    int16_t dig_P3;
    int16_t dig_P4;
    int16_t dig_P5;
    int16_t dig_P6;
    int16_t dig_P7;
    int16_t dig_P8;
    int16_t dig_P9;
    int32_t t_fine;
} BMP280_CalibData;

/**
 * @brief  BMP280配置
 */
typedef struct {
    I2C_HandleTypeDef* hi2c;
    uint8_t address;
    BMP280_Mode mode;
    BMP280_Oversampling temp_oversampling;
    BMP280_Oversampling press_oversampling;
    BMP280_CalibData calib;
} BMP280_Config;

/**
 * @brief  BMP280数据
 */
typedef struct {
    float temperature;    // 温度（°C）
    float pressure;       // 气压（hPa）
    float altitude;       // 高度（米）
    bool valid;
} BMP280_Data;

// 函数声明
bool BMP280_Init(BMP280_Config* config);
bool BMP280_Read(BMP280_Config* config, BMP280_Data* data);
bool BMP280_ReadPressure(BMP280_Config* config, float* pressure);
bool BMP280_ReadTemperature(BMP280_Config* config, float* temperature);
float BMP280_CalculateAltitude(float pressure, float sea_level_pressure);

#endif /* __BMP280_H */
```


**驱动实现文件**：

```c
/**
 * @file    bmp280.c
 * @brief   BMP280气压传感器驱动实现
 */

#include "bmp280.h"
#include <math.h>

// 私有函数声明
static bool BMP280_WriteReg(BMP280_Config* config, uint8_t reg, uint8_t value);
static bool BMP280_ReadReg(BMP280_Config* config, uint8_t reg, uint8_t* value);
static bool BMP280_ReadRegs(BMP280_Config* config, uint8_t reg, uint8_t* buffer, uint8_t len);
static bool BMP280_ReadCalibration(BMP280_Config* config);
static int32_t BMP280_CompensateTemperature(BMP280_Config* config, int32_t adc_T);
static uint32_t BMP280_CompensatePressure(BMP280_Config* config, int32_t adc_P);

/**
 * @brief  写入寄存器
 */
static bool BMP280_WriteReg(BMP280_Config* config, uint8_t reg, uint8_t value) {
    uint8_t buffer[2] = {reg, value};
    
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        config->hi2c,
        config->address << 1,
        buffer,
        2,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取寄存器
 */
static bool BMP280_ReadReg(BMP280_Config* config, uint8_t reg, uint8_t* value) {
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        config->hi2c,
        config->address << 1,
        &reg,
        1,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) return false;
    
    status = HAL_I2C_Master_Receive(
        config->hi2c,
        config->address << 1,
        value,
        1,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取多个寄存器
 */
static bool BMP280_ReadRegs(BMP280_Config* config, uint8_t reg, uint8_t* buffer, uint8_t len) {
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(
        config->hi2c,
        config->address << 1,
        &reg,
        1,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) return false;
    
    status = HAL_I2C_Master_Receive(
        config->hi2c,
        config->address << 1,
        buffer,
        len,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取校准参数
 */
static bool BMP280_ReadCalibration(BMP280_Config* config) {
    uint8_t calib[24];
    
    if (!BMP280_ReadRegs(config, BMP280_REG_CALIB_START, calib, 24)) {
        return false;
    }
    
    config->calib.dig_T1 = (calib[1] << 8) | calib[0];
    config->calib.dig_T2 = (calib[3] << 8) | calib[2];
    config->calib.dig_T3 = (calib[5] << 8) | calib[4];
    config->calib.dig_P1 = (calib[7] << 8) | calib[6];
    config->calib.dig_P2 = (calib[9] << 8) | calib[8];
    config->calib.dig_P3 = (calib[11] << 8) | calib[10];
    config->calib.dig_P4 = (calib[13] << 8) | calib[12];
    config->calib.dig_P5 = (calib[15] << 8) | calib[14];
    config->calib.dig_P6 = (calib[17] << 8) | calib[16];
    config->calib.dig_P7 = (calib[19] << 8) | calib[18];
    config->calib.dig_P8 = (calib[21] << 8) | calib[20];
    config->calib.dig_P9 = (calib[23] << 8) | calib[22];
    
    return true;
}

/**
 * @brief  温度补偿计算
 */
static int32_t BMP280_CompensateTemperature(BMP280_Config* config, int32_t adc_T) {
    int32_t var1, var2, T;
    
    var1 = ((((adc_T >> 3) - ((int32_t)config->calib.dig_T1 << 1))) * 
            ((int32_t)config->calib.dig_T2)) >> 11;
    
    var2 = (((((adc_T >> 4) - ((int32_t)config->calib.dig_T1)) * 
              ((adc_T >> 4) - ((int32_t)config->calib.dig_T1))) >> 12) * 
            ((int32_t)config->calib.dig_T3)) >> 14;
    
    config->calib.t_fine = var1 + var2;
    T = (config->calib.t_fine * 5 + 128) >> 8;
    
    return T;
}

/**
 * @brief  气压补偿计算
 */
static uint32_t BMP280_CompensatePressure(BMP280_Config* config, int32_t adc_P) {
    int64_t var1, var2, p;
    
    var1 = ((int64_t)config->calib.t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)config->calib.dig_P6;
    var2 = var2 + ((var1 * (int64_t)config->calib.dig_P5) << 17);
    var2 = var2 + (((int64_t)config->calib.dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)config->calib.dig_P3) >> 8) + 
           ((var1 * (int64_t)config->calib.dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)config->calib.dig_P1) >> 33;
    
    if (var1 == 0) {
        return 0;
    }
    
    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)config->calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)config->calib.dig_P8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (((int64_t)config->calib.dig_P7) << 4);
    
    return (uint32_t)p;
}

/**
 * @brief  初始化BMP280传感器
 */
bool BMP280_Init(BMP280_Config* config) {
    uint8_t chip_id;
    
    // 读取芯片ID
    if (!BMP280_ReadReg(config, BMP280_REG_CHIP_ID, &chip_id)) {
        return false;
    }
    
    if (chip_id != BMP280_CHIP_ID) {
        return false;
    }
    
    // 软复位
    BMP280_WriteReg(config, BMP280_REG_RESET, 0xB6);
    HAL_Delay(10);
    
    // 读取校准参数
    if (!BMP280_ReadCalibration(config)) {
        return false;
    }
    
    // 配置测量参数
    uint8_t ctrl_meas = (config->temp_oversampling << 5) | 
                        (config->press_oversampling << 2) | 
                        config->mode;
    
    if (!BMP280_WriteReg(config, BMP280_REG_CTRL_MEAS, ctrl_meas)) {
        return false;
    }
    
    // 配置滤波器和待机时间
    uint8_t config_reg = (0 << 5) | (4 << 2) | 0;  // 滤波器关闭，待机时间500ms
    if (!BMP280_WriteReg(config, BMP280_REG_CONFIG, config_reg)) {
        return false;
    }
    
    return true;
}

/**
 * @brief  读取传感器数据
 */
bool BMP280_Read(BMP280_Config* config, BMP280_Data* data) {
    uint8_t buffer[6];
    
    // 如果是Forced模式，需要触发测量
    if (config->mode == BMP280_MODE_FORCED) {
        uint8_t ctrl_meas = (config->temp_oversampling << 5) | 
                            (config->press_oversampling << 2) | 
                            BMP280_MODE_FORCED;
        BMP280_WriteReg(config, BMP280_REG_CTRL_MEAS, ctrl_meas);
        HAL_Delay(50);  // 等待测量完成
    }
    
    // 读取原始数据
    if (!BMP280_ReadRegs(config, BMP280_REG_PRESS_MSB, buffer, 6)) {
        data->valid = false;
        return false;
    }
    
    // 解析原始数据
    int32_t adc_P = ((int32_t)buffer[0] << 12) | ((int32_t)buffer[1] << 4) | ((int32_t)buffer[2] >> 4);
    int32_t adc_T = ((int32_t)buffer[3] << 12) | ((int32_t)buffer[4] << 4) | ((int32_t)buffer[5] >> 4);
    
    // 温度补偿
    int32_t temp = BMP280_CompensateTemperature(config, adc_T);
    data->temperature = (float)temp / 100.0f;
    
    // 气压补偿
    uint32_t press = BMP280_CompensatePressure(config, adc_P);
    data->pressure = (float)press / 25600.0f;
    
    // 计算高度
    data->altitude = BMP280_CalculateAltitude(data->pressure, 1013.25f);
    
    data->valid = true;
    return true;
}

/**
 * @brief  计算高度
 * @param  pressure: 当前气压（hPa）
 * @param  sea_level_pressure: 海平面气压（hPa）
 * @retval 高度（米）
 */
float BMP280_CalculateAltitude(float pressure, float sea_level_pressure) {
    return 44330.0f * (1.0f - powf(pressure / sea_level_pressure, 0.1903f));
}
```




### BMP280使用示例

```c
/**
 * @file    main.c
 * @brief   BMP280传感器使用示例
 */

#include "stm32f1xx_hal.h"
#include "bmp280.h"
#include <stdio.h>

// I2C句柄
extern I2C_HandleTypeDef hi2c1;

// BMP280传感器配置
BMP280_Config bmp280_config = {
    .hi2c = &hi2c1,
    .address = BMP280_ADDR_LOW,
    .mode = BMP280_MODE_NORMAL,
    .temp_oversampling = BMP280_OVERSAMPLING_2X,
    .press_oversampling = BMP280_OVERSAMPLING_16X
};

/**
 * @brief  主函数
 */
int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化I2C
    MX_I2C1_Init();
    
    // 初始化UART
    MX_USART1_UART_Init();
    
    printf("BMP280气压传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化BMP280传感器
    if (!BMP280_Init(&bmp280_config)) {
        printf("❌ BMP280初始化失败！\n");
        while (1);
    }
    
    printf("✓ BMP280初始化成功\n\n");
    
    BMP280_Data data;
    uint32_t read_count = 0;
    
    while (1) {
        // 读取传感器数据
        if (BMP280_Read(&bmp280_config, &data)) {
            read_count++;
            
            printf("读取 #%lu:\n", read_count);
            printf("  温度: %.2f °C\n", data.temperature);
            printf("  气压: %.2f hPa\n", data.pressure);
            printf("  高度: %.1f 米\n", data.altitude);
            printf("\n");
        }
        
        HAL_Delay(1000);
    }
}

/**
 * @brief  天气预报示例
 */
void weather_forecast(void) {
    #define HISTORY_SIZE 12  // 保存12小时数据
    
    float pressure_history[HISTORY_SIZE];
    uint8_t history_index = 0;
    bool history_full = false;
    
    BMP280_Data data;
    
    printf("简易天气预报系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (BMP280_Read(&bmp280_config, &data)) {
            // 保存气压历史
            pressure_history[history_index] = data.pressure;
            history_index++;
            
            if (history_index >= HISTORY_SIZE) {
                history_index = 0;
                history_full = true;
            }
            
            printf("当前气压: %.2f hPa\n", data.pressure);
            
            // 分析气压趋势
            if (history_full) {
                float pressure_change = data.pressure - pressure_history[history_index];
                
                printf("12小时气压变化: %.2f hPa\n", pressure_change);
                
                if (pressure_change > 3.0f) {
                    printf("天气预报: ☀️ 天气转好\n");
                } else if (pressure_change < -3.0f) {
                    printf("天气预报: 🌧️ 可能降雨\n");
                } else {
                    printf("天气预报: ⛅ 天气稳定\n");
                }
            } else {
                printf("正在收集数据... (%d/%d)\n", 
                       history_index, HISTORY_SIZE);
            }
            
            printf("\n");
        }
        
        // 每小时更新一次
        HAL_Delay(3600000);
    }
}

/**
 * @brief  楼层检测示例
 */
void floor_detection(void) {
    const float FLOOR_HEIGHT = 3.0f;  // 每层楼高度（米）
    float reference_pressure = 0;
    int16_t reference_floor = 0;
    
    BMP280_Data data;
    
    printf("楼层检测系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 设置参考楼层
    printf("请在参考楼层按下按钮...\n");
    // 等待按钮按下
    while (HAL_GPIO_ReadPin(BUTTON_GPIO_Port, BUTTON_Pin) == GPIO_PIN_SET);
    
    if (BMP280_Read(&bmp280_config, &data)) {
        reference_pressure = data.pressure;
        printf("参考楼层气压: %.2f hPa\n\n", reference_pressure);
    }
    
    while (1) {
        if (BMP280_Read(&bmp280_config, &data)) {
            // 计算相对高度
            float altitude_diff = BMP280_CalculateAltitude(data.pressure, reference_pressure);
            
            // 计算楼层
            int16_t floor = reference_floor + (int16_t)(altitude_diff / FLOOR_HEIGHT);
            
            printf("当前气压: %.2f hPa\n", data.pressure);
            printf("相对高度: %.1f 米\n", altitude_diff);
            printf("当前楼层: %d\n", floor);
            
            if (floor > reference_floor) {
                printf("方向: ⬆️ 上升 %d 层\n", floor - reference_floor);
            } else if (floor < reference_floor) {
                printf("方向: ⬇️ 下降 %d 层\n", reference_floor - floor);
            } else {
                printf("方向: ➡️ 同一楼层\n");
            }
            
            printf("\n");
        }
        
        HAL_Delay(1000);
    }
}
```



## 第三部分：组合应用

### 完整环境监测系统

```c
/**
 * @brief  完整环境监测系统
 */

typedef struct {
    float light;          // 光照强度（lux）
    float temperature;    // 温度（°C）
    float pressure;       // 气压（hPa）
    float altitude;       // 高度（米）
    uint32_t timestamp;   // 时间戳
} EnvironmentData;

/**
 * @brief  读取所有环境数据
 */
bool read_environment(EnvironmentData* env) {
    BH1750_Config* light_sensor = &bh1750_config;
    BMP280_Config* pressure_sensor = &bmp280_config;
    
    // 读取光照
    if (!BH1750_ReadLight(light_sensor, &env->light)) {
        return false;
    }
    
    // 读取气压和温度
    BMP280_Data bmp_data;
    if (!BMP280_Read(pressure_sensor, &bmp_data)) {
        return false;
    }
    
    env->temperature = bmp_data.temperature;
    env->pressure = bmp_data.pressure;
    env->altitude = bmp_data.altitude;
    env->timestamp = HAL_GetTick();
    
    return true;
}

/**
 * @brief  环境监测主程序
 */
void environment_monitoring(void) {
    EnvironmentData env;
    
    printf("完整环境监测系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (read_environment(&env)) {
            printf("环境数据 [%lu ms]:\n", env.timestamp);
            printf("┌─────────────────────────────────┐\n");
            printf("│ 光照强度: %8.1f lux      │\n", env.light);
            printf("│ 温度:     %8.2f °C       │\n", env.temperature);
            printf("│ 气压:     %8.2f hPa      │\n", env.pressure);
            printf("│ 高度:     %8.1f 米       │\n", env.altitude);
            printf("└─────────────────────────────────┘\n");
            
            // 环境评估
            printf("\n环境评估:\n");
            
            // 光照评估
            if (env.light < 50) {
                printf("  💡 光照不足，建议开灯\n");
            } else if (env.light > 1000) {
                printf("  ☀️ 光照充足\n");
            } else {
                printf("  ✓ 光照适中\n");
            }
            
            // 温度评估
            if (env.temperature < 18) {
                printf("  ❄️ 温度偏低\n");
            } else if (env.temperature > 26) {
                printf("  🔥 温度偏高\n");
            } else {
                printf("  ✓ 温度舒适\n");
            }
            
            // 气压评估
            if (env.pressure < 1000) {
                printf("  📉 气压偏低，可能降雨\n");
            } else if (env.pressure > 1020) {
                printf("  📈 气压偏高，天气晴好\n");
            } else {
                printf("  ✓ 气压正常\n");
            }
            
            printf("\n");
        }
        
        HAL_Delay(5000);
    }
}

/**
 * @brief  室内外检测
 */
void indoor_outdoor_detection(void) {
    EnvironmentData env;
    
    printf("室内外检测系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (read_environment(&env)) {
            bool is_indoor = false;
            uint8_t confidence = 0;
            
            // 判断依据1：光照强度
            if (env.light < 500) {
                confidence += 30;  // 室内可能性+30%
            } else if (env.light > 5000) {
                confidence -= 30;  // 室外可能性+30%
            }
            
            // 判断依据2：气压变化稳定性
            static float last_pressure = 0;
            if (last_pressure != 0) {
                float pressure_change = fabsf(env.pressure - last_pressure);
                if (pressure_change < 0.5f) {
                    confidence += 20;  // 室内气压更稳定
                }
            }
            last_pressure = env.pressure;
            
            // 判断依据3：温度稳定性
            static float last_temp = 0;
            if (last_temp != 0) {
                float temp_change = fabsf(env.temperature - last_temp);
                if (temp_change < 1.0f) {
                    confidence += 20;  // 室内温度更稳定
                }
            }
            last_temp = env.temperature;
            
            // 综合判断
            is_indoor = (confidence > 30);
            
            printf("位置判断:\n");
            printf("  光照: %.1f lux\n", env.light);
            printf("  气压: %.2f hPa\n", env.pressure);
            printf("  温度: %.2f °C\n", env.temperature);
            printf("  置信度: %d%%\n", 50 + confidence);
            printf("  判断结果: %s\n\n", is_indoor ? "🏠 室内" : "🌳 室外");
        }
        
        HAL_Delay(10000);
    }
}
```



## 常见问题与解决方案

### BH1750常见问题

**问题1：读数始终为0或65535**

```
可能原因：
1. I2C通信失败
   - 检查I2C地址是否正确
   - 检查上拉电阻
   - 检查连线

2. 传感器未上电
   - 检查VCC连接
   - 测量电源电压

3. 传感器损坏
   - 更换传感器测试

解决方案：
```

```c
/**
 * @brief  BH1750诊断
 */
void diagnose_bh1750(void) {
    printf("BH1750诊断程序\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 测试I2C通信
    printf("1. 测试I2C通信...\n");
    uint8_t test_data;
    HAL_StatusTypeDef status = HAL_I2C_Master_Receive(
        bh1750_config.hi2c,
        bh1750_config.address << 1,
        &test_data,
        1,
        100
    );
    
    if (status == HAL_OK) {
        printf("   ✓ I2C通信正常\n");
    } else {
        printf("   ❌ I2C通信失败 (错误码: %d)\n", status);
        printf("   请检查：\n");
        printf("     - I2C地址是否正确\n");
        printf("     - 上拉电阻是否存在\n");
        printf("     - 连线是否正确\n");
        return;
    }
    
    // 测试多次读取
    printf("\n2. 测试连续读取...\n");
    int success = 0;
    float lux;
    
    for (int i = 0; i < 10; i++) {
        if (BH1750_ReadLight(&bh1750_config, &lux)) {
            success++;
            printf("   读取 #%d: %.1f lux\n", i+1, lux);
        }
        HAL_Delay(200);
    }
    
    printf("   成功率: %d/10\n", success);
    
    if (success < 8) {
        printf("   ⚠ 成功率偏低，可能存在问题\n");
    } else {
        printf("   ✓ 传感器工作正常\n");
    }
}
```

**问题2：光照读数不准确**

```
校准方法：
1. 使用标准光照计对比
2. 在不同光照条件下测试
3. 考虑传感器安装位置
4. 避免遮挡和反光

注意事项：
- BH1750精度约±20%
- 适合相对测量，不适合精密测量
- 定期校准提高精度
```

### BMP280常见问题

**问题1：气压读数异常**

```c
/**
 * @brief  BMP280数据验证
 */
bool validate_bmp280_data(BMP280_Data* data) {
    // 气压范围检查（300-1100 hPa）
    if (data->pressure < 300 || data->pressure > 1100) {
        printf("⚠ 气压超出范围: %.2f hPa\n", data->pressure);
        return false;
    }
    
    // 温度范围检查（-40 to 85°C）
    if (data->temperature < -40 || data->temperature > 85) {
        printf("⚠ 温度超出范围: %.2f°C\n", data->temperature);
        return false;
    }
    
    // 变化率检查
    static float last_pressure = 1013.25f;
    float pressure_change = fabsf(data->pressure - last_pressure);
    
    if (pressure_change > 10.0f) {
        printf("⚠ 气压变化过大: %.2f hPa\n", pressure_change);
        return false;
    }
    
    last_pressure = data->pressure;
    return true;
}
```

**问题2：高度计算不准确**

```
影响因素：
1. 海平面气压设置
   - 需要根据当地实际气压校准
   - 可从气象站获取

2. 温度影响
   - 气压随温度变化
   - 使用温度补偿

3. 天气变化
   - 气压随天气变化
   - 定期更新参考气压

解决方案：
```

```c
/**
 * @brief  高度校准
 */
void calibrate_altitude(void) {
    BMP280_Data data;
    float known_altitude;  // 已知高度
    float sea_level_pressure;
    
    printf("高度校准程序\n");
    printf("═══════════════════════════════════════\n\n");
    
    printf("请输入当前已知高度（米）: ");
    scanf("%f", &known_altitude);
    
    // 读取当前气压
    if (BMP280_Read(&bmp280_config, &data)) {
        // 反推海平面气压
        // P0 = P / (1 - h/44330)^5.255
        sea_level_pressure = data.pressure / 
            powf(1.0f - known_altitude / 44330.0f, 5.255f);
        
        printf("\n校准结果:\n");
        printf("  当前气压: %.2f hPa\n", data.pressure);
        printf("  已知高度: %.1f 米\n", known_altitude);
        printf("  海平面气压: %.2f hPa\n", sea_level_pressure);
        printf("\n请在代码中使用此海平面气压值\n");
    }
}
```



## 性能优化与最佳实践

### 低功耗设计

```c
/**
 * @brief  低功耗环境监测
 */
void low_power_monitoring(void) {
    EnvironmentData env;
    
    while (1) {
        // 唤醒传感器
        BH1750_PowerOn(&bh1750_config);
        HAL_Delay(10);
        
        // 读取数据
        read_environment(&env);
        
        // 处理数据
        process_environment_data(&env);
        
        // 关闭传感器
        BH1750_PowerDown(&bh1750_config);
        
        // 进入低功耗模式
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        
        // 唤醒后恢复时钟
        SystemClock_Config();
        
        // 下次测量间隔由RTC唤醒控制
    }
}
```

### 数据滤波

```c
/**
 * @brief  移动平均滤波
 */
typedef struct {
    float buffer[10];
    uint8_t index;
    bool full;
} MovingAverage;

float moving_average_filter(MovingAverage* ma, float new_value) {
    ma->buffer[ma->index] = new_value;
    ma->index++;
    
    if (ma->index >= 10) {
        ma->index = 0;
        ma->full = true;
    }
    
    float sum = 0;
    int count = ma->full ? 10 : ma->index;
    
    for (int i = 0; i < count; i++) {
        sum += ma->buffer[i];
    }
    
    return sum / count;
}
```

## 总结

### 关键要点

1. **传感器选型**：
   - BH1750：简单易用的光照传感器
   - BMP280：高精度气压温度传感器
   - 组合使用实现完整环境监测

2. **硬件设计**：
   - I2C上拉电阻必不可少
   - 注意地址选择引脚配置
   - 电源去耦电容
   - 合理布局减少干扰

3. **软件实现**：
   - 正确实现I2C通信
   - BMP280需要校准参数补偿
   - 添加数据有效性检查
   - 实现滤波提高稳定性

4. **实际应用**：
   - 自动照明控制
   - 天气预报
   - 高度/楼层检测
   - 室内外判断
   - 完整环境监测

### 下一步学习

- 超声波测距传感器
- 生物传感器（心率、血氧）
- 传感器数据融合技术
- 多传感器系统设计

---

**作者**: 嵌入式知识平台内容团队  
**最后更新**: 2026-03-07  
**版本**: 1.0.0
