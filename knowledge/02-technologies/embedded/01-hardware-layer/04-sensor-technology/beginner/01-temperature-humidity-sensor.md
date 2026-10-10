---
# 基础信息
title: "温湿度传感器应用开发"
description: "全面讲解温湿度传感器的工作原理、接口使用和应用开发，包括DHT11/DHT22、SHT3x系列传感器的数据读取、校准方法和实际应用案例"
slug: "temperature-humidity-sensor"

# 分类信息
domain: "01-hardware-layer"
module: "04-sensor-technology"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 温湿度传感器
  - DHT
  - SHT
  - 环境监测
  - I2C
  - 单总线
prerequisites:
  - "01-chip-architecture/beginner/07-register-operations"
  - "02-hardware-design-fundamentals/beginner/08-interface-circuits"
related_contents:
  - "02-accelerometer-gyroscope"
  - "03-light-pressure-sensor"

# 学习信息
estimated_time: 60
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
  - 温湿度传感器
  - DHT11
  - DHT22
  - SHT3x
  - 环境监测
  - 传感器应用
cover_image: ""
---

# 温湿度传感器应用开发

## 概述

温湿度传感器是嵌入式系统中最常用的环境监测传感器之一，广泛应用于智能家居、气象站、农业监测、工业控制等领域。本教程将介绍常用的温湿度传感器（DHT11/DHT22和SHT3x系列），讲解其工作原理、硬件连接、软件驱动开发和实际应用。

### 为什么需要温湿度传感器

1. **环境监测**：
   - 室内空气质量监测
   - 气象数据采集
   - 温室大棚监控
   - 仓储环境管理

2. **设备保护**：
   - 防止设备过热
   - 避免结露损坏
   - 优化工作环境
   - 延长设备寿命

3. **舒适度控制**：
   - 智能空调控制
   - 加湿器自动调节
   - 通风系统优化
   - 节能管理

4. **工业应用**：
   - 生产过程监控
   - 产品质量控制
   - 安全预警
   - 数据记录

### 常用温湿度传感器对比

```
传感器类型对比：

┌─────────┬──────────┬──────────┬──────────┬──────────┐
│ 参数    │ DHT11    │ DHT22    │ SHT30    │ SHT31    │
├─────────┼──────────┼──────────┼──────────┼──────────┤
│ 温度范围│ 0-50°C   │ -40-80°C │ -40-125°C│ -40-125°C│
│ 温度精度│ ±2°C     │ ±0.5°C   │ ±0.3°C   │ ±0.2°C   │
│ 湿度范围│ 20-90%RH │ 0-100%RH │ 0-100%RH │ 0-100%RH │
│ 湿度精度│ ±5%RH    │ ±2%RH    │ ±2%RH    │ ±1.5%RH  │
│ 接口    │ 单总线   │ 单总线   │ I2C      │ I2C      │
│ 响应时间│ 6-15s    │ 2s       │ <8s      │ <8s      │
│ 价格    │ 低       │ 中       │ 中       │ 高       │
│ 适用场景│ 入门学习 │ 一般应用 │ 精密测量 │ 高精度   │
└─────────┴──────────┴──────────┴──────────┴──────────┘

选型建议：
- 学习入门：DHT11（便宜、简单）
- 一般应用：DHT22（性价比高）
- 精密测量：SHT30/SHT31（高精度、稳定）
- 工业应用：SHT31（最高精度、可靠性好）
```



## 第一部分：DHT11/DHT22传感器

### 硬件连接

**DHT11/DHT22引脚定义**：

```
DHT传感器引脚（4针封装）：

    ┌─────────┐
    │  DHT11  │
    │  DHT22  │
    └─┬─┬─┬─┬─┘
      1 2 3 4

引脚说明：
1. VCC  - 电源正极（3.3V-5V）
2. DATA - 数据线（单总线）
3. NC   - 不连接
4. GND  - 电源地

注意：3针封装没有NC引脚
```

**硬件连接电路**：

```
连接方案：

MCU                    DHT传感器
                      ┌─────────┐
3.3V/5V ──────────────┤1 VCC    │
                      │         │
GPIO ─────┬───────────┤2 DATA   │
          │           │         │
         ┌┴┐          │3 NC     │
    4.7k │ │          │         │
         └┬┘          │4 GND    │
          │           └─────────┘
GND ──────┴───────────────┘

关键要点：
1. DATA引脚需要上拉电阻（4.7kΩ）
2. 电源电压：DHT11支持3.3V-5V，DHT22支持3.3V-5.5V
3. 数据线长度不宜超过20米
4. 建议在VCC和GND之间加0.1μF去耦电容
```

### 通信协议

**单总线协议时序**：

```
DHT单总线通信协议：

1. 起始信号（主机发送）：
   主机拉低DATA线至少18ms，然后释放

   ────┐                    ┌────
       └────────────────────┘
       <------- >18ms ------>

2. 响应信号（DHT发送）：
   DHT拉低80μs，然后拉高80μs

   ────┐        ┌────────────
       └────────┘
       <-80μs-><---80μs--->

3. 数据传输（DHT发送40位数据）：
   每位数据：先拉低50μs，然后拉高
   - 数据0：拉高26-28μs
   - 数据1：拉高70μs

   数据0：
   ────┐    ┌──────
       └────┘
       50μs 26-28μs

   数据1：
   ────┐    ┌──────────────
       └────┘
       50μs    70μs

4. 数据格式（40位）：
   [湿度整数][湿度小数][温度整数][温度小数][校验和]
   每部分8位，共40位

   DHT11：小数部分为0
   DHT22：小数部分有效

5. 校验和计算：
   校验和 = (湿度整数 + 湿度小数 + 温度整数 + 温度小数) & 0xFF
```



### DHT驱动代码实现

**驱动头文件**：

```c
/**
 * @file    dht.h
 * @brief   DHT11/DHT22温湿度传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __DHT_H
#define __DHT_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>

/**
 * @brief  DHT传感器类型
 */
typedef enum {
    DHT_TYPE_DHT11 = 0,    // DHT11传感器
    DHT_TYPE_DHT22 = 1     // DHT22传感器（AM2302）
} DHT_Type;

/**
 * @brief  DHT数据结构
 */
typedef struct {
    float temperature;      // 温度（°C）
    float humidity;         // 湿度（%RH）
    bool valid;            // 数据有效标志
} DHT_Data;

/**
 * @brief  DHT传感器配置
 */
typedef struct {
    GPIO_TypeDef* gpio_port;    // GPIO端口
    uint16_t gpio_pin;          // GPIO引脚
    DHT_Type type;              // 传感器类型
} DHT_Config;

// 函数声明
void DHT_Init(DHT_Config* config);
bool DHT_Read(DHT_Config* config, DHT_Data* data);
void DHT_Delay_us(uint32_t us);

#endif /* __DHT_H */
```

**驱动实现文件**：

```c
/**
 * @file    dht.c
 * @brief   DHT11/DHT22温湿度传感器驱动实现
 */

#include "dht.h"

// 私有函数声明
static void DHT_SetPinOutput(DHT_Config* config);
static void DHT_SetPinInput(DHT_Config* config);
static void DHT_WriteBit(DHT_Config* config, uint8_t bit);
static uint8_t DHT_ReadBit(DHT_Config* config);
static bool DHT_Start(DHT_Config* config);
static bool DHT_CheckResponse(DHT_Config* config);
static uint8_t DHT_ReadByte(DHT_Config* config);

/**
 * @brief  微秒级延时（使用DWT）
 * @param  us: 延时时间（微秒）
 */
void DHT_Delay_us(uint32_t us) {
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000);
    
    while ((DWT->CYCCNT - start) < cycles);
}

/**
 * @brief  初始化DHT传感器
 * @param  config: 传感器配置
 */
void DHT_Init(DHT_Config* config) {
    // 使能DWT计数器（用于微秒延时）
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    
    // 配置GPIO为输出模式
    DHT_SetPinOutput(config);
    
    // 初始状态拉高
    HAL_GPIO_WritePin(config->gpio_port, config->gpio_pin, GPIO_PIN_SET);
    
    // 等待传感器稳定
    HAL_Delay(1000);
}

/**
 * @brief  设置GPIO为输出模式
 */
static void DHT_SetPinOutput(DHT_Config* config) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    GPIO_InitStruct.Pin = config->gpio_pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    
    HAL_GPIO_Init(config->gpio_port, &GPIO_InitStruct);
}

/**
 * @brief  设置GPIO为输入模式
 */
static void DHT_SetPinInput(DHT_Config* config) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    GPIO_InitStruct.Pin = config->gpio_pin;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    
    HAL_GPIO_Init(config->gpio_port, &GPIO_InitStruct);
}

/**
 * @brief  发送起始信号
 * @retval true: 成功, false: 失败
 */
static bool DHT_Start(DHT_Config* config) {
    // 设置为输出模式
    DHT_SetPinOutput(config);
    
    // 拉低至少18ms
    HAL_GPIO_WritePin(config->gpio_port, config->gpio_pin, GPIO_PIN_RESET);
    HAL_Delay(20);
    
    // 释放总线
    HAL_GPIO_WritePin(config->gpio_port, config->gpio_pin, GPIO_PIN_SET);
    DHT_Delay_us(30);
    
    // 切换为输入模式
    DHT_SetPinInput(config);
    
    return true;
}

/**
 * @brief  检查DHT响应
 * @retval true: 响应正常, false: 无响应
 */
static bool DHT_CheckResponse(DHT_Config* config) {
    uint8_t timeout = 0;
    
    // 等待DHT拉低（80μs）
    while (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_SET) {
        DHT_Delay_us(1);
        if (++timeout > 100) return false;
    }
    
    timeout = 0;
    // 等待DHT拉高（80μs）
    while (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_RESET) {
        DHT_Delay_us(1);
        if (++timeout > 100) return false;
    }
    
    timeout = 0;
    // 等待DHT准备发送数据
    while (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_SET) {
        DHT_Delay_us(1);
        if (++timeout > 100) return false;
    }
    
    return true;
}

/**
 * @brief  读取一个字节
 * @retval 读取的字节数据
 */
static uint8_t DHT_ReadByte(DHT_Config* config) {
    uint8_t byte = 0;
    
    for (int i = 0; i < 8; i++) {
        uint8_t timeout = 0;
        
        // 等待低电平结束（50μs）
        while (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_RESET) {
            DHT_Delay_us(1);
            if (++timeout > 100) return 0;
        }
        
        // 延时30μs后采样
        DHT_Delay_us(30);
        
        // 读取位值
        byte <<= 1;
        if (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_SET) {
            byte |= 0x01;
        }
        
        timeout = 0;
        // 等待高电平结束
        while (HAL_GPIO_ReadPin(config->gpio_port, config->gpio_pin) == GPIO_PIN_SET) {
            DHT_Delay_us(1);
            if (++timeout > 100) return 0;
        }
    }
    
    return byte;
}

/**
 * @brief  读取DHT传感器数据
 * @param  config: 传感器配置
 * @param  data: 数据存储结构
 * @retval true: 读取成功, false: 读取失败
 */
bool DHT_Read(DHT_Config* config, DHT_Data* data) {
    uint8_t buffer[5] = {0};
    
    // 发送起始信号
    if (!DHT_Start(config)) {
        data->valid = false;
        return false;
    }
    
    // 检查响应
    if (!DHT_CheckResponse(config)) {
        data->valid = false;
        return false;
    }
    
    // 读取40位数据（5字节）
    for (int i = 0; i < 5; i++) {
        buffer[i] = DHT_ReadByte(config);
    }
    
    // 切换回输出模式
    DHT_SetPinOutput(config);
    HAL_GPIO_WritePin(config->gpio_port, config->gpio_pin, GPIO_PIN_SET);
    
    // 校验和检查
    uint8_t checksum = (buffer[0] + buffer[1] + buffer[2] + buffer[3]) & 0xFF;
    if (checksum != buffer[4]) {
        data->valid = false;
        return false;
    }
    
    // 解析数据
    if (config->type == DHT_TYPE_DHT11) {
        // DHT11：整数部分有效
        data->humidity = (float)buffer[0];
        data->temperature = (float)buffer[2];
    } else {
        // DHT22：包含小数部分
        data->humidity = ((buffer[0] << 8) | buffer[1]) / 10.0f;
        
        // 处理负温度
        if (buffer[2] & 0x80) {
            data->temperature = -((((buffer[2] & 0x7F) << 8) | buffer[3]) / 10.0f);
        } else {
            data->temperature = (((buffer[2] << 8) | buffer[3]) / 10.0f);
        }
    }
    
    data->valid = true;
    return true;
}
```



### DHT使用示例

```c
/**
 * @file    main.c
 * @brief   DHT传感器使用示例
 */

#include "stm32f1xx_hal.h"
#include "dht.h"
#include <stdio.h>

// DHT传感器配置
DHT_Config dht_config = {
    .gpio_port = GPIOA,
    .gpio_pin = GPIO_PIN_0,
    .type = DHT_TYPE_DHT22    // 使用DHT22
};

/**
 * @brief  主函数
 */
int main(void) {
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化UART（用于打印）
    MX_USART1_UART_Init();
    
    // 初始化DHT传感器
    DHT_Init(&dht_config);
    
    printf("DHT22温湿度传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    DHT_Data data;
    uint32_t read_count = 0;
    uint32_t error_count = 0;
    
    while (1) {
        // 读取传感器数据
        if (DHT_Read(&dht_config, &data)) {
            read_count++;
            
            // 打印数据
            printf("读取 #%lu:\n", read_count);
            printf("  温度: %.1f °C\n", data.temperature);
            printf("  湿度: %.1f %%RH\n", data.humidity);
            printf("  状态: 有效\n\n");
            
            // 数据范围检查
            if (data.temperature < -40 || data.temperature > 80) {
                printf("  ⚠ 警告：温度超出正常范围！\n");
            }
            if (data.humidity < 0 || data.humidity > 100) {
                printf("  ⚠ 警告：湿度超出正常范围！\n");
            }
        } else {
            error_count++;
            printf("读取失败 #%lu (总错误: %lu)\n\n", read_count + error_count, error_count);
        }
        
        // DHT22建议读取间隔至少2秒
        HAL_Delay(2000);
    }
}

/**
 * @brief  高级示例：数据平滑滤波
 */
void advanced_example_filtering(void) {
    #define FILTER_SIZE 5
    
    float temp_buffer[FILTER_SIZE] = {0};
    float humi_buffer[FILTER_SIZE] = {0};
    uint8_t buffer_index = 0;
    bool buffer_full = false;
    
    DHT_Data data;
    
    while (1) {
        if (DHT_Read(&dht_config, &data)) {
            // 存储数据到缓冲区
            temp_buffer[buffer_index] = data.temperature;
            humi_buffer[buffer_index] = data.humidity;
            
            buffer_index++;
            if (buffer_index >= FILTER_SIZE) {
                buffer_index = 0;
                buffer_full = true;
            }
            
            // 计算平均值（移动平均滤波）
            if (buffer_full) {
                float temp_avg = 0, humi_avg = 0;
                
                for (int i = 0; i < FILTER_SIZE; i++) {
                    temp_avg += temp_buffer[i];
                    humi_avg += humi_buffer[i];
                }
                
                temp_avg /= FILTER_SIZE;
                humi_avg /= FILTER_SIZE;
                
                printf("滤波后数据:\n");
                printf("  温度: %.1f °C (原始: %.1f °C)\n", 
                       temp_avg, data.temperature);
                printf("  湿度: %.1f %%RH (原始: %.1f %%RH)\n\n",
                       humi_avg, data.humidity);
            }
        }
        
        HAL_Delay(2000);
    }
}

/**
 * @brief  高级示例：温湿度报警
 */
void advanced_example_alarm(void) {
    // 报警阈值
    const float TEMP_HIGH = 30.0f;
    const float TEMP_LOW = 15.0f;
    const float HUMI_HIGH = 80.0f;
    const float HUMI_LOW = 30.0f;
    
    DHT_Data data;
    
    while (1) {
        if (DHT_Read(&dht_config, &data)) {
            printf("当前环境:\n");
            printf("  温度: %.1f °C\n", data.temperature);
            printf("  湿度: %.1f %%RH\n", data.humidity);
            
            // 温度报警
            if (data.temperature > TEMP_HIGH) {
                printf("  🔥 温度过高报警！\n");
                // 触发降温措施
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);  // 开启风扇
            } else if (data.temperature < TEMP_LOW) {
                printf("  ❄️  温度过低报警！\n");
                // 触发加热措施
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);  // 开启加热器
            } else {
                printf("  ✓ 温度正常\n");
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
            }
            
            // 湿度报警
            if (data.humidity > HUMI_HIGH) {
                printf("  💧 湿度过高报警！\n");
                // 触发除湿措施
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);  // 开启除湿器
            } else if (data.humidity < HUMI_LOW) {
                printf("  🏜️  湿度过低报警！\n");
                // 触发加湿措施
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_SET);  // 开启加湿器
            } else {
                printf("  ✓ 湿度正常\n");
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
            }
            
            printf("\n");
        }
        
        HAL_Delay(2000);
    }
}
```



## 第二部分：SHT3x系列传感器

### 硬件连接

**SHT3x引脚定义**：

```
SHT30/SHT31引脚（6针封装）：

    ┌─────────┐
    │  SHT3x  │
    └─┬─┬─┬─┬─┬─┬─┘
      1 2 3 4 5 6

引脚说明：
1. VDD   - 电源正极（2.4V-5.5V）
2. SDA   - I2C数据线
3. SCL   - I2C时钟线
4. ADDR  - I2C地址选择（接GND或VDD）
5. ALERT - 报警输出（可选）
6. VSS   - 电源地

I2C地址：
- ADDR接GND: 0x44
- ADDR接VDD: 0x45
```

**硬件连接电路**：

```
连接方案：

MCU                    SHT3x传感器
                      ┌─────────┐
3.3V ─────────────────┤1 VDD    │
                      │         │
SDA ──────┬───────────┤2 SDA    │
          │           │         │
         ┌┴┐          │3 SCL    │
    4.7k │ │          │         │
         └┬┘          │4 ADDR   │──┐
          │           │         │  │ 接GND或VDD
SCL ──────┼──┬────────┤5 ALERT  │  │ 选择地址
          │  │        │         │  │
         ┌┴┐ │        │6 VSS    │  │
    4.7k │ │ │        └─────────┘  │
         └┬┘ │                      │
          │  │                      │
GND ──────┴──┴──────────────────────┘

关键要点：
1. SDA和SCL需要上拉电阻（4.7kΩ）
2. 支持标准模式（100kHz）和快速模式（400kHz）
3. ADDR引脚选择I2C地址
4. ALERT引脚可用于温湿度报警（可选）
```

### I2C通信协议

**SHT3x命令集**：

```
常用命令：

1. 单次测量模式：
   - 高重复性：0x2C06
   - 中重复性：0x2C0D
   - 低重复性：0x2C10

2. 周期测量模式：
   - 0.5 mps, 高重复性：0x2032
   - 1 mps, 高重复性：0x2130
   - 2 mps, 高重复性：0x2236
   - 4 mps, 高重复性：0x2334
   - 10 mps, 高重复性：0x2737

3. 读取测量结果：
   - 读取数据：0xE000

4. 软复位：
   - 复位命令：0x30A2

5. 状态寄存器：
   - 读取状态：0xF32D
   - 清除状态：0x3041

数据格式：
[温度高字节][温度低字节][温度CRC][湿度高字节][湿度低字节][湿度CRC]

温度计算：
Temperature (°C) = -45 + 175 × (ST / 65535)

湿度计算：
Humidity (%RH) = 100 × (SRH / 65535)
```



### SHT3x驱动代码实现

**驱动头文件**：

```c
/**
 * @file    sht3x.h
 * @brief   SHT30/SHT31温湿度传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __SHT3X_H
#define __SHT3X_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>

/**
 * @brief  SHT3x I2C地址
 */
#define SHT3X_ADDR_LOW   0x44    // ADDR引脚接GND
#define SHT3X_ADDR_HIGH  0x45    // ADDR引脚接VDD

/**
 * @brief  SHT3x命令
 */
#define SHT3X_CMD_MEASURE_HIGH    0x2C06    // 单次测量，高重复性
#define SHT3X_CMD_MEASURE_MEDIUM  0x2C0D    // 单次测量，中重复性
#define SHT3X_CMD_MEASURE_LOW     0x2C10    // 单次测量，低重复性
#define SHT3X_CMD_READ_STATUS     0xF32D    // 读取状态寄存器
#define SHT3X_CMD_CLEAR_STATUS    0x3041    // 清除状态寄存器
#define SHT3X_CMD_SOFT_RESET      0x30A2    // 软复位
#define SHT3X_CMD_HEATER_ENABLE   0x306D    // 使能加热器
#define SHT3X_CMD_HEATER_DISABLE  0x3066    // 禁用加热器

/**
 * @brief  SHT3x数据结构
 */
typedef struct {
    float temperature;      // 温度（°C）
    float humidity;         // 湿度（%RH）
    bool valid;            // 数据有效标志
} SHT3X_Data;

/**
 * @brief  SHT3x配置
 */
typedef struct {
    I2C_HandleTypeDef* hi2c;    // I2C句柄
    uint8_t address;            // I2C地址
} SHT3X_Config;

// 函数声明
bool SHT3X_Init(SHT3X_Config* config);
bool SHT3X_Read(SHT3X_Config* config, SHT3X_Data* data);
bool SHT3X_SoftReset(SHT3X_Config* config);
bool SHT3X_ReadStatus(SHT3X_Config* config, uint16_t* status);
bool SHT3X_EnableHeater(SHT3X_Config* config, bool enable);

#endif /* __SHT3X_H */
```

**驱动实现文件**：

```c
/**
 * @file    sht3x.c
 * @brief   SHT30/SHT31温湿度传感器驱动实现
 */

#include "sht3x.h"

// 私有函数声明
static bool SHT3X_WriteCommand(SHT3X_Config* config, uint16_t cmd);
static uint8_t SHT3X_CalculateCRC(uint8_t* data, uint8_t length);
static bool SHT3X_CheckCRC(uint8_t* data, uint8_t length, uint8_t crc);

/**
 * @brief  计算CRC-8校验
 * @param  data: 数据指针
 * @param  length: 数据长度
 * @retval CRC值
 */
static uint8_t SHT3X_CalculateCRC(uint8_t* data, uint8_t length) {
    uint8_t crc = 0xFF;
    
    for (uint8_t i = 0; i < length; i++) {
        crc ^= data[i];
        
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc = crc << 1;
            }
        }
    }
    
    return crc;
}

/**
 * @brief  检查CRC校验
 * @param  data: 数据指针
 * @param  length: 数据长度
 * @param  crc: 接收到的CRC值
 * @retval true: 校验通过, false: 校验失败
 */
static bool SHT3X_CheckCRC(uint8_t* data, uint8_t length, uint8_t crc) {
    return (SHT3X_CalculateCRC(data, length) == crc);
}

/**
 * @brief  写入命令
 * @param  config: 传感器配置
 * @param  cmd: 命令
 * @retval true: 成功, false: 失败
 */
static bool SHT3X_WriteCommand(SHT3X_Config* config, uint16_t cmd) {
    uint8_t buffer[2];
    buffer[0] = (cmd >> 8) & 0xFF;
    buffer[1] = cmd & 0xFF;
    
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
 * @brief  初始化SHT3x传感器
 * @param  config: 传感器配置
 * @retval true: 成功, false: 失败
 */
bool SHT3X_Init(SHT3X_Config* config) {
    // 软复位
    if (!SHT3X_SoftReset(config)) {
        return false;
    }
    
    // 等待复位完成
    HAL_Delay(10);
    
    // 读取状态寄存器验证通信
    uint16_t status;
    if (!SHT3X_ReadStatus(config, &status)) {
        return false;
    }
    
    return true;
}

/**
 * @brief  软复位
 * @param  config: 传感器配置
 * @retval true: 成功, false: 失败
 */
bool SHT3X_SoftReset(SHT3X_Config* config) {
    return SHT3X_WriteCommand(config, SHT3X_CMD_SOFT_RESET);
}

/**
 * @brief  读取状态寄存器
 * @param  config: 传感器配置
 * @param  status: 状态值指针
 * @retval true: 成功, false: 失败
 */
bool SHT3X_ReadStatus(SHT3X_Config* config, uint16_t* status) {
    uint8_t buffer[3];
    
    // 发送读取状态命令
    if (!SHT3X_WriteCommand(config, SHT3X_CMD_READ_STATUS)) {
        return false;
    }
    
    // 读取状态数据
    HAL_StatusTypeDef hal_status = HAL_I2C_Master_Receive(
        config->hi2c,
        config->address << 1,
        buffer,
        3,
        HAL_MAX_DELAY
    );
    
    if (hal_status != HAL_OK) {
        return false;
    }
    
    // 检查CRC
    if (!SHT3X_CheckCRC(buffer, 2, buffer[2])) {
        return false;
    }
    
    *status = (buffer[0] << 8) | buffer[1];
    return true;
}

/**
 * @brief  控制加热器
 * @param  config: 传感器配置
 * @param  enable: true-使能, false-禁用
 * @retval true: 成功, false: 失败
 */
bool SHT3X_EnableHeater(SHT3X_Config* config, bool enable) {
    uint16_t cmd = enable ? SHT3X_CMD_HEATER_ENABLE : SHT3X_CMD_HEATER_DISABLE;
    return SHT3X_WriteCommand(config, cmd);
}

/**
 * @brief  读取温湿度数据
 * @param  config: 传感器配置
 * @param  data: 数据存储结构
 * @retval true: 成功, false: 失败
 */
bool SHT3X_Read(SHT3X_Config* config, SHT3X_Data* data) {
    uint8_t buffer[6];
    
    // 发送测量命令（高重复性）
    if (!SHT3X_WriteCommand(config, SHT3X_CMD_MEASURE_HIGH)) {
        data->valid = false;
        return false;
    }
    
    // 等待测量完成（高重复性需要15ms）
    HAL_Delay(20);
    
    // 读取测量数据
    HAL_StatusTypeDef status = HAL_I2C_Master_Receive(
        config->hi2c,
        config->address << 1,
        buffer,
        6,
        HAL_MAX_DELAY
    );
    
    if (status != HAL_OK) {
        data->valid = false;
        return false;
    }
    
    // 检查温度CRC
    if (!SHT3X_CheckCRC(&buffer[0], 2, buffer[2])) {
        data->valid = false;
        return false;
    }
    
    // 检查湿度CRC
    if (!SHT3X_CheckCRC(&buffer[3], 2, buffer[5])) {
        data->valid = false;
        return false;
    }
    
    // 计算温度
    uint16_t temp_raw = (buffer[0] << 8) | buffer[1];
    data->temperature = -45.0f + 175.0f * ((float)temp_raw / 65535.0f);
    
    // 计算湿度
    uint16_t humi_raw = (buffer[3] << 8) | buffer[4];
    data->humidity = 100.0f * ((float)humi_raw / 65535.0f);
    
    data->valid = true;
    return true;
}
```



### SHT3x使用示例

```c
/**
 * @file    main.c
 * @brief   SHT3x传感器使用示例
 */

#include "stm32f1xx_hal.h"
#include "sht3x.h"
#include <stdio.h>

// I2C句柄（需要在CubeMX中配置）
extern I2C_HandleTypeDef hi2c1;

// SHT3x传感器配置
SHT3X_Config sht3x_config = {
    .hi2c = &hi2c1,
    .address = SHT3X_ADDR_LOW    // ADDR引脚接GND
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
    
    printf("SHT3x温湿度传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化SHT3x传感器
    if (!SHT3X_Init(&sht3x_config)) {
        printf("❌ SHT3x初始化失败！\n");
        printf("请检查：\n");
        printf("  1. I2C连接是否正确\n");
        printf("  2. 上拉电阻是否存在\n");
        printf("  3. 传感器地址是否正确\n");
        while (1);
    }
    
    printf("✓ SHT3x初始化成功\n\n");
    
    // 读取状态寄存器
    uint16_t status;
    if (SHT3X_ReadStatus(&sht3x_config, &status)) {
        printf("状态寄存器: 0x%04X\n", status);
        printf("  校验和状态: %s\n", (status & 0x0001) ? "失败" : "正常");
        printf("  命令状态: %s\n", (status & 0x0002) ? "失败" : "正常");
        printf("  复位检测: %s\n", (status & 0x0010) ? "是" : "否");
        printf("  温度报警: %s\n", (status & 0x0400) ? "触发" : "正常");
        printf("  湿度报警: %s\n", (status & 0x0800) ? "触发" : "正常");
        printf("  加热器状态: %s\n\n", (status & 0x2000) ? "开启" : "关闭");
    }
    
    SHT3X_Data data;
    uint32_t read_count = 0;
    uint32_t error_count = 0;
    
    while (1) {
        // 读取传感器数据
        if (SHT3X_Read(&sht3x_config, &data)) {
            read_count++;
            
            // 打印数据
            printf("读取 #%lu:\n", read_count);
            printf("  温度: %.2f °C\n", data.temperature);
            printf("  湿度: %.2f %%RH\n", data.humidity);
            printf("  状态: 有效\n\n");
            
            // 数据范围检查
            if (data.temperature < -40 || data.temperature > 125) {
                printf("  ⚠ 警告：温度超出正常范围！\n");
            }
            if (data.humidity < 0 || data.humidity > 100) {
                printf("  ⚠ 警告：湿度超出正常范围！\n");
            }
        } else {
            error_count++;
            printf("读取失败 #%lu (总错误: %lu)\n\n", 
                   read_count + error_count, error_count);
        }
        
        // SHT3x可以快速读取，但建议间隔至少1秒
        HAL_Delay(1000);
    }
}

/**
 * @brief  高级示例：加热器除湿功能
 */
void advanced_example_heater(void) {
    SHT3X_Data data;
    
    printf("加热器除湿测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 读取初始湿度
    if (SHT3X_Read(&sht3x_config, &data)) {
        printf("初始湿度: %.2f %%RH\n\n", data.humidity);
    }
    
    // 如果湿度过高，启动加热器
    if (data.humidity > 80.0f) {
        printf("湿度过高，启动加热器...\n");
        
        // 使能加热器
        SHT3X_EnableHeater(&sht3x_config, true);
        
        // 加热30秒
        for (int i = 0; i < 30; i++) {
            HAL_Delay(1000);
            
            if (SHT3X_Read(&sht3x_config, &data)) {
                printf("  %2ds: 温度=%.2f°C, 湿度=%.2f%%RH\n",
                       i+1, data.temperature, data.humidity);
            }
        }
        
        // 禁用加热器
        SHT3X_EnableHeater(&sht3x_config, false);
        printf("\n加热器已关闭\n");
        
        // 等待冷却
        HAL_Delay(5000);
        
        // 读取最终湿度
        if (SHT3X_Read(&sht3x_config, &data)) {
            printf("最终湿度: %.2f %%RH\n", data.humidity);
        }
    }
}

/**
 * @brief  高级示例：数据记录
 */
void advanced_example_data_logging(void) {
    #define LOG_SIZE 100
    
    typedef struct {
        uint32_t timestamp;
        float temperature;
        float humidity;
    } DataLog;
    
    DataLog logs[LOG_SIZE];
    uint16_t log_index = 0;
    
    SHT3X_Data data;
    
    printf("开始数据记录（%d条）\n", LOG_SIZE);
    printf("═══════════════════════════════════════\n\n");
    
    // 记录数据
    while (log_index < LOG_SIZE) {
        if (SHT3X_Read(&sht3x_config, &data)) {
            logs[log_index].timestamp = HAL_GetTick();
            logs[log_index].temperature = data.temperature;
            logs[log_index].humidity = data.humidity;
            
            printf("记录 #%d: T=%.2f°C, H=%.2f%%RH\n",
                   log_index + 1, data.temperature, data.humidity);
            
            log_index++;
        }
        
        HAL_Delay(1000);  // 每秒记录一次
    }
    
    // 数据分析
    printf("\n数据分析\n");
    printf("═══════════════════════════════════════\n");
    
    float temp_min = logs[0].temperature;
    float temp_max = logs[0].temperature;
    float temp_avg = 0;
    float humi_min = logs[0].humidity;
    float humi_max = logs[0].humidity;
    float humi_avg = 0;
    
    for (int i = 0; i < LOG_SIZE; i++) {
        // 温度统计
        if (logs[i].temperature < temp_min) temp_min = logs[i].temperature;
        if (logs[i].temperature > temp_max) temp_max = logs[i].temperature;
        temp_avg += logs[i].temperature;
        
        // 湿度统计
        if (logs[i].humidity < humi_min) humi_min = logs[i].humidity;
        if (logs[i].humidity > humi_max) humi_max = logs[i].humidity;
        humi_avg += logs[i].humidity;
    }
    
    temp_avg /= LOG_SIZE;
    humi_avg /= LOG_SIZE;
    
    printf("温度统计:\n");
    printf("  最小值: %.2f °C\n", temp_min);
    printf("  最大值: %.2f °C\n", temp_max);
    printf("  平均值: %.2f °C\n", temp_avg);
    printf("  变化范围: %.2f °C\n\n", temp_max - temp_min);
    
    printf("湿度统计:\n");
    printf("  最小值: %.2f %%RH\n", humi_min);
    printf("  最大值: %.2f %%RH\n", humi_max);
    printf("  平均值: %.2f %%RH\n", humi_avg);
    printf("  变化范围: %.2f %%RH\n", humi_max - humi_min);
}
```



## 第三部分：传感器校准

### 为什么需要校准

温湿度传感器在使用过程中可能出现漂移，导致测量误差增大。定期校准可以：

1. **提高测量精度**：消除系统误差
2. **延长使用寿命**：及时发现传感器老化
3. **保证数据可靠性**：满足应用要求
4. **符合标准要求**：通过认证测试

### 校准方法

**方法1：两点校准法**

```c
/**
 * @brief  两点校准数据结构
 */
typedef struct {
    float ref_low;      // 低点参考值
    float meas_low;     // 低点测量值
    float ref_high;     // 高点参考值
    float meas_high;    // 高点测量值
    float k;            // 校准系数
    float b;            // 校准偏移
} CalibrationData;

/**
 * @brief  计算校准参数
 * @param  calib: 校准数据
 */
void calculate_calibration(CalibrationData* calib) {
    // 计算线性校准参数
    // y = k * x + b
    // 其中 y 是真实值，x 是测量值
    
    calib->k = (calib->ref_high - calib->ref_low) / 
               (calib->meas_high - calib->meas_low);
    
    calib->b = calib->ref_low - calib->k * calib->meas_low;
    
    printf("校准参数计算完成:\n");
    printf("  k = %.4f\n", calib->k);
    printf("  b = %.4f\n", calib->b);
}

/**
 * @brief  应用校准
 * @param  measured: 测量值
 * @param  calib: 校准数据
 * @retval 校准后的值
 */
float apply_calibration(float measured, CalibrationData* calib) {
    return calib->k * measured + calib->b;
}

/**
 * @brief  温度校准示例
 */
void temperature_calibration_example(void) {
    CalibrationData temp_calib;
    
    printf("温度传感器校准\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 步骤1：低温点校准（例如：冰水混合物 0°C）
    printf("步骤1：将传感器放入冰水混合物中\n");
    printf("等待温度稳定...\n");
    HAL_Delay(60000);  // 等待1分钟
    
    SHT3X_Data data;
    float temp_sum = 0;
    for (int i = 0; i < 10; i++) {
        SHT3X_Read(&sht3x_config, &data);
        temp_sum += data.temperature;
        HAL_Delay(1000);
    }
    
    temp_calib.ref_low = 0.0f;  // 参考值：0°C
    temp_calib.meas_low = temp_sum / 10.0f;  // 测量平均值
    printf("低温点测量值: %.2f °C\n\n", temp_calib.meas_low);
    
    // 步骤2：高温点校准（例如：沸水 100°C，需根据气压调整）
    printf("步骤2：将传感器放入沸水中（注意安全！）\n");
    printf("等待温度稳定...\n");
    HAL_Delay(60000);  // 等待1分钟
    
    temp_sum = 0;
    for (int i = 0; i < 10; i++) {
        SHT3X_Read(&sht3x_config, &data);
        temp_sum += data.temperature;
        HAL_Delay(1000);
    }
    
    temp_calib.ref_high = 100.0f;  // 参考值：100°C（标准大气压）
    temp_calib.meas_high = temp_sum / 10.0f;  // 测量平均值
    printf("高温点测量值: %.2f °C\n\n", temp_calib.meas_high);
    
    // 计算校准参数
    calculate_calibration(&temp_calib);
    
    // 验证校准
    printf("\n校准验证:\n");
    printf("测量值 -> 校准后\n");
    for (float t = 0; t <= 100; t += 10) {
        float calibrated = apply_calibration(t, &temp_calib);
        printf("%.1f°C -> %.2f°C\n", t, calibrated);
    }
}

/**
 * @brief  湿度校准示例（使用饱和盐溶液）
 */
void humidity_calibration_example(void) {
    CalibrationData humi_calib;
    
    printf("湿度传感器校准\n");
    printf("═══════════════════════════════════════\n\n");
    
    printf("使用饱和盐溶液法校准\n");
    printf("常用饱和盐溶液相对湿度（25°C）：\n");
    printf("  LiCl:  11.3%%RH\n");
    printf("  MgCl2: 33.0%%RH\n");
    printf("  NaCl:  75.3%%RH\n");
    printf("  KCl:   84.3%%RH\n\n");
    
    // 步骤1：低湿度点（使用MgCl2饱和盐溶液）
    printf("步骤1：将传感器放入MgCl2饱和盐溶液密闭容器中\n");
    printf("等待湿度稳定（至少8小时）...\n");
    printf("按任意键继续...\n");
    // 等待用户输入
    
    SHT3X_Data data;
    float humi_sum = 0;
    for (int i = 0; i < 10; i++) {
        SHT3X_Read(&sht3x_config, &data);
        humi_sum += data.humidity;
        HAL_Delay(1000);
    }
    
    humi_calib.ref_low = 33.0f;  // MgCl2参考值：33%RH
    humi_calib.meas_low = humi_sum / 10.0f;
    printf("低湿度点测量值: %.2f %%RH\n\n", humi_calib.meas_low);
    
    // 步骤2：高湿度点（使用KCl饱和盐溶液）
    printf("步骤2：将传感器放入KCl饱和盐溶液密闭容器中\n");
    printf("等待湿度稳定（至少8小时）...\n");
    printf("按任意键继续...\n");
    // 等待用户输入
    
    humi_sum = 0;
    for (int i = 0; i < 10; i++) {
        SHT3X_Read(&sht3x_config, &data);
        humi_sum += data.humidity;
        HAL_Delay(1000);
    }
    
    humi_calib.ref_high = 84.3f;  // KCl参考值：84.3%RH
    humi_calib.meas_high = humi_sum / 10.0f;
    printf("高湿度点测量值: %.2f %%RH\n\n", humi_calib.meas_high);
    
    // 计算校准参数
    calculate_calibration(&humi_calib);
    
    // 保存校准参数到Flash
    // save_calibration_to_flash(&humi_calib);
}
```

**方法2：与标准仪器对比校准**

```c
/**
 * @brief  与标准仪器对比校准
 */
void calibration_with_reference(void) {
    printf("与标准仪器对比校准\n");
    printf("═══════════════════════════════════════\n\n");
    
    printf("将传感器与标准温湿度计放置在同一环境中\n");
    printf("等待环境稳定...\n");
    HAL_Delay(300000);  // 等待5分钟
    
    SHT3X_Data data;
    
    // 读取多次取平均
    float temp_sum = 0, humi_sum = 0;
    const int samples = 20;
    
    for (int i = 0; i < samples; i++) {
        if (SHT3X_Read(&sht3x_config, &data)) {
            temp_sum += data.temperature;
            humi_sum += data.humidity;
        }
        HAL_Delay(1000);
    }
    
    float temp_measured = temp_sum / samples;
    float humi_measured = humi_sum / samples;
    
    printf("测量平均值:\n");
    printf("  温度: %.2f °C\n", temp_measured);
    printf("  湿度: %.2f %%RH\n\n", humi_measured);
    
    printf("请输入标准仪器读数:\n");
    printf("  温度: ");
    float temp_reference;
    scanf("%f", &temp_reference);
    
    printf("  湿度: ");
    float humi_reference;
    scanf("%f", &humi_reference);
    
    // 计算误差
    float temp_error = temp_measured - temp_reference;
    float humi_error = humi_measured - humi_reference;
    
    printf("\n测量误差:\n");
    printf("  温度误差: %.2f °C\n", temp_error);
    printf("  湿度误差: %.2f %%RH\n", humi_error);
    
    // 简单偏移校准
    printf("\n校准偏移量:\n");
    printf("  温度偏移: %.2f °C\n", -temp_error);
    printf("  湿度偏移: %.2f %%RH\n", -humi_error);
}
```



## 第四部分：实际应用案例

### 案例1：智能温室监控系统

```c
/**
 * @brief  智能温室监控系统
 */

// 温室环境参数
typedef struct {
    float temp_target;      // 目标温度
    float temp_tolerance;   // 温度容差
    float humi_target;      // 目标湿度
    float humi_tolerance;   // 湿度容差
} GreenhouseConfig;

// 控制输出
typedef struct {
    bool heater;           // 加热器
    bool cooler;           // 冷却器（风扇）
    bool humidifier;       // 加湿器
    bool dehumidifier;     // 除湿器
} GreenhouseControl;

/**
 * @brief  温室控制逻辑
 */
void greenhouse_control(SHT3X_Data* sensor, 
                       GreenhouseConfig* config,
                       GreenhouseControl* control) {
    // 温度控制
    if (sensor->temperature < config->temp_target - config->temp_tolerance) {
        // 温度过低，开启加热器
        control->heater = true;
        control->cooler = false;
        printf("🔥 开启加热器\n");
    } else if (sensor->temperature > config->temp_target + config->temp_tolerance) {
        // 温度过高，开启冷却器
        control->heater = false;
        control->cooler = true;
        printf("❄️  开启冷却器\n");
    } else {
        // 温度正常
        control->heater = false;
        control->cooler = false;
        printf("✓ 温度正常\n");
    }
    
    // 湿度控制
    if (sensor->humidity < config->humi_target - config->humi_tolerance) {
        // 湿度过低，开启加湿器
        control->humidifier = true;
        control->dehumidifier = false;
        printf("💧 开启加湿器\n");
    } else if (sensor->humidity > config->humi_target + config->humi_tolerance) {
        // 湿度过高，开启除湿器
        control->humidifier = false;
        control->dehumidifier = true;
        printf("🌵 开启除湿器\n");
    } else {
        // 湿度正常
        control->humidifier = false;
        control->dehumidifier = false;
        printf("✓ 湿度正常\n");
    }
}

/**
 * @brief  温室监控主循环
 */
void greenhouse_monitoring(void) {
    // 配置目标参数
    GreenhouseConfig config = {
        .temp_target = 25.0f,      // 目标温度25°C
        .temp_tolerance = 2.0f,    // 容差±2°C
        .humi_target = 70.0f,      // 目标湿度70%RH
        .humi_tolerance = 5.0f     // 容差±5%RH
    };
    
    GreenhouseControl control = {0};
    SHT3X_Data sensor_data;
    
    printf("智能温室监控系统启动\n");
    printf("═══════════════════════════════════════\n");
    printf("目标温度: %.1f°C (±%.1f°C)\n", 
           config.temp_target, config.temp_tolerance);
    printf("目标湿度: %.1f%%RH (±%.1f%%RH)\n\n",
           config.humi_target, config.humi_tolerance);
    
    while (1) {
        // 读取传感器数据
        if (SHT3X_Read(&sht3x_config, &sensor_data)) {
            printf("当前环境:\n");
            printf("  温度: %.2f °C\n", sensor_data.temperature);
            printf("  湿度: %.2f %%RH\n", sensor_data.humidity);
            
            // 执行控制逻辑
            greenhouse_control(&sensor_data, &config, &control);
            
            // 输出控制信号
            HAL_GPIO_WritePin(HEATER_GPIO_Port, HEATER_Pin, 
                            control.heater ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(COOLER_GPIO_Port, COOLER_Pin,
                            control.cooler ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(HUMIDIFIER_GPIO_Port, HUMIDIFIER_Pin,
                            control.humidifier ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(DEHUMIDIFIER_GPIO_Port, DEHUMIDIFIER_Pin,
                            control.dehumidifier ? GPIO_PIN_SET : GPIO_PIN_RESET);
            
            printf("\n");
        }
        
        // 每30秒检测一次
        HAL_Delay(30000);
    }
}
```

### 案例2：舒适度指数计算

```c
/**
 * @brief  计算热指数（Heat Index）
 * @param  temp: 温度（°C）
 * @param  humi: 相对湿度（%）
 * @retval 热指数（°C）
 */
float calculate_heat_index(float temp, float humi) {
    // 转换为华氏度
    float T = temp * 9.0f / 5.0f + 32.0f;
    float RH = humi;
    
    // Rothfusz回归方程
    float HI = -42.379f + 
               2.04901523f * T + 
               10.14333127f * RH - 
               0.22475541f * T * RH - 
               0.00683783f * T * T - 
               0.05481717f * RH * RH + 
               0.00122874f * T * T * RH + 
               0.00085282f * T * RH * RH - 
               0.00000199f * T * T * RH * RH;
    
    // 转换回摄氏度
    return (HI - 32.0f) * 5.0f / 9.0f;
}

/**
 * @brief  计算露点温度
 * @param  temp: 温度（°C）
 * @param  humi: 相对湿度（%）
 * @retval 露点温度（°C）
 */
float calculate_dew_point(float temp, float humi) {
    float a = 17.27f;
    float b = 237.7f;
    
    float alpha = ((a * temp) / (b + temp)) + logf(humi / 100.0f);
    float dew_point = (b * alpha) / (a - alpha);
    
    return dew_point;
}

/**
 * @brief  评估舒适度等级
 */
const char* evaluate_comfort(float temp, float humi) {
    // 舒适度评估标准
    if (temp < 18.0f) {
        return "偏冷";
    } else if (temp > 26.0f) {
        if (humi > 70.0f) {
            return "闷热";
        } else {
            return "偏热";
        }
    } else {
        // 18-26°C
        if (humi < 30.0f) {
            return "干燥";
        } else if (humi > 70.0f) {
            return "潮湿";
        } else {
            return "舒适";
        }
    }
}

/**
 * @brief  舒适度监测示例
 */
void comfort_monitoring(void) {
    SHT3X_Data data;
    
    printf("室内舒适度监测\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (SHT3X_Read(&sht3x_config, &data)) {
            // 计算衍生参数
            float heat_index = calculate_heat_index(data.temperature, data.humidity);
            float dew_point = calculate_dew_point(data.temperature, data.humidity);
            const char* comfort = evaluate_comfort(data.temperature, data.humidity);
            
            // 显示结果
            printf("环境参数:\n");
            printf("  温度: %.2f °C\n", data.temperature);
            printf("  湿度: %.2f %%RH\n", data.humidity);
            printf("  热指数: %.2f °C\n", heat_index);
            printf("  露点: %.2f °C\n", dew_point);
            printf("  舒适度: %s\n", comfort);
            
            // 建议
            printf("\n建议:\n");
            if (strcmp(comfort, "偏冷") == 0) {
                printf("  💡 建议开启暖气或增加衣物\n");
            } else if (strcmp(comfort, "偏热") == 0) {
                printf("  💡 建议开启空调或增加通风\n");
            } else if (strcmp(comfort, "闷热") == 0) {
                printf("  💡 建议开启空调除湿模式\n");
            } else if (strcmp(comfort, "干燥") == 0) {
                printf("  💡 建议开启加湿器\n");
            } else if (strcmp(comfort, "潮湿") == 0) {
                printf("  💡 建议开启除湿器或增加通风\n");
            } else {
                printf("  ✓ 环境舒适，无需调整\n");
            }
            
            printf("\n");
        }
        
        HAL_Delay(60000);  // 每分钟更新一次
    }
}
```

### 案例3：数据上传到云平台

```c
/**
 * @brief  数据上传到云平台（示例：MQTT）
 */

#include "mqtt_client.h"  // MQTT客户端库
#include <cJSON.h>        // JSON库

/**
 * @brief  构建JSON数据
 */
char* build_json_data(SHT3X_Data* data) {
    cJSON* root = cJSON_CreateObject();
    
    // 添加设备信息
    cJSON_AddStringToObject(root, "device_id", "greenhouse_001");
    cJSON_AddNumberToObject(root, "timestamp", HAL_GetTick());
    
    // 添加传感器数据
    cJSON* sensor = cJSON_CreateObject();
    cJSON_AddNumberToObject(sensor, "temperature", data->temperature);
    cJSON_AddNumberToObject(sensor, "humidity", data->humidity);
    cJSON_AddItemToObject(root, "sensor_data", sensor);
    
    // 转换为字符串
    char* json_string = cJSON_Print(root);
    
    // 释放内存
    cJSON_Delete(root);
    
    return json_string;
}

/**
 * @brief  上传数据到云平台
 */
void upload_to_cloud(void) {
    // MQTT配置
    mqtt_client_config_t mqtt_cfg = {
        .host = "mqtt.example.com",
        .port = 1883,
        .client_id = "greenhouse_001",
        .username = "user",
        .password = "pass"
    };
    
    // 连接MQTT服务器
    mqtt_client_handle_t client = mqtt_client_init(&mqtt_cfg);
    mqtt_client_start(client);
    
    printf("云平台数据上传\n");
    printf("═══════════════════════════════════════\n\n");
    
    SHT3X_Data data;
    
    while (1) {
        // 读取传感器数据
        if (SHT3X_Read(&sht3x_config, &data)) {
            // 构建JSON数据
            char* json_data = build_json_data(&data);
            
            printf("上传数据: %s\n", json_data);
            
            // 发布到MQTT主题
            mqtt_client_publish(client, 
                              "greenhouse/sensor/data",
                              json_data,
                              strlen(json_data),
                              1,  // QoS
                              0); // retain
            
            // 释放内存
            free(json_data);
            
            printf("✓ 数据上传成功\n\n");
        }
        
        // 每5分钟上传一次
        HAL_Delay(300000);
    }
}
```



## 常见问题与解决方案

### DHT传感器常见问题

**问题1：读取失败或数据不稳定**

```
可能原因：
1. 上拉电阻缺失或阻值不合适
   解决：添加4.7kΩ上拉电阻

2. 数据线过长
   解决：缩短数据线长度（<20米）

3. 电源不稳定
   解决：添加去耦电容（0.1μF）

4. 时序不准确
   解决：使用DWT精确延时，避免使用HAL_Delay

5. 读取频率过高
   解决：DHT11至少间隔1秒，DHT22至少间隔2秒
```

**问题2：校验和错误**

```c
/**
 * @brief  校验和错误诊断
 */
void diagnose_checksum_error(void) {
    printf("校验和错误诊断\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 测试多次读取
    int success = 0;
    int checksum_error = 0;
    int timeout_error = 0;
    
    for (int i = 0; i < 100; i++) {
        DHT_Data data;
        if (DHT_Read(&dht_config, &data)) {
            success++;
        } else {
            // 分析错误类型
            // 这里需要修改DHT_Read函数返回详细错误码
            checksum_error++;
        }
        HAL_Delay(2000);
    }
    
    printf("测试结果（100次）:\n");
    printf("  成功: %d\n", success);
    printf("  校验和错误: %d\n", checksum_error);
    printf("  超时错误: %d\n", timeout_error);
    printf("  成功率: %.1f%%\n", success / 100.0f * 100);
    
    if (checksum_error > 10) {
        printf("\n⚠ 校验和错误率过高！\n");
        printf("建议检查：\n");
        printf("  1. 数据线是否有干扰\n");
        printf("  2. 上拉电阻是否合适\n");
        printf("  3. 电源是否稳定\n");
        printf("  4. 传感器是否损坏\n");
    }
}
```

**问题3：温度或湿度读数异常**

```
异常表现：
1. 读数为0或固定值
   - 检查传感器连接
   - 检查传感器是否损坏

2. 读数跳变剧烈
   - 增加软件滤波
   - 检查电源稳定性
   - 远离干扰源

3. 读数偏差大
   - 进行校准
   - 检查环境是否稳定
   - 等待传感器预热

解决方案：
```

```c
/**
 * @brief  数据有效性检查
 */
bool validate_sensor_data(DHT_Data* data) {
    // 温度范围检查
    if (data->temperature < -40 || data->temperature > 80) {
        printf("⚠ 温度超出范围: %.2f°C\n", data->temperature);
        return false;
    }
    
    // 湿度范围检查
    if (data->humidity < 0 || data->humidity > 100) {
        printf("⚠ 湿度超出范围: %.2f%%RH\n", data->humidity);
        return false;
    }
    
    // 变化率检查（与上次读数对比）
    static float last_temp = 25.0f;
    static float last_humi = 50.0f;
    
    float temp_change = fabsf(data->temperature - last_temp);
    float humi_change = fabsf(data->humidity - last_humi);
    
    if (temp_change > 10.0f) {
        printf("⚠ 温度变化过大: %.2f°C\n", temp_change);
        return false;
    }
    
    if (humi_change > 20.0f) {
        printf("⚠ 湿度变化过大: %.2f%%RH\n", humi_change);
        return false;
    }
    
    // 更新历史值
    last_temp = data->temperature;
    last_humi = data->humidity;
    
    return true;
}
```

### SHT3x传感器常见问题

**问题1：I2C通信失败**

```
可能原因：
1. I2C地址错误
   解决：检查ADDR引脚连接，确认地址（0x44或0x45）

2. 上拉电阻缺失
   解决：添加4.7kΩ上拉电阻到SDA和SCL

3. I2C速度过快
   解决：降低I2C时钟频率（100kHz或400kHz）

4. 总线冲突
   解决：检查总线上是否有其他设备冲突

5. 电源问题
   解决：确保电源电压在2.4V-5.5V范围内
```

**问题2：CRC校验失败**

```c
/**
 * @brief  CRC错误诊断
 */
void diagnose_crc_error(void) {
    printf("CRC错误诊断\n");
    printf("═══════════════════════════════════════\n\n");
    
    int success = 0;
    int crc_error = 0;
    int i2c_error = 0;
    
    for (int i = 0; i < 100; i++) {
        SHT3X_Data data;
        if (SHT3X_Read(&sht3x_config, &data)) {
            success++;
        } else {
            // 需要修改SHT3X_Read返回详细错误码
            crc_error++;
        }
        HAL_Delay(1000);
    }
    
    printf("测试结果（100次）:\n");
    printf("  成功: %d\n", success);
    printf("  CRC错误: %d\n", crc_error);
    printf("  I2C错误: %d\n", i2c_error);
    printf("  成功率: %.1f%%\n", success / 100.0f * 100);
    
    if (crc_error > 5) {
        printf("\n⚠ CRC错误率过高！\n");
        printf("建议检查：\n");
        printf("  1. I2C信号质量\n");
        printf("  2. 上拉电阻值\n");
        printf("  3. 线缆长度和质量\n");
        printf("  4. 电磁干扰\n");
    }
}
```

**问题3：测量值漂移**

```
原因分析：
1. 传感器老化
   - 定期校准
   - 更换传感器

2. 环境污染
   - 使用加热器清洁（SHT3x内置）
   - 避免接触化学物质

3. 长期高湿度
   - 定期使用加热器除湿
   - 改善使用环境

解决方案：
```

```c
/**
 * @brief  传感器自清洁（使用内置加热器）
 */
void sensor_self_cleaning(void) {
    printf("传感器自清洁程序\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 读取清洁前数据
    SHT3X_Data data_before;
    SHT3X_Read(&sht3x_config, &data_before);
    printf("清洁前: T=%.2f°C, H=%.2f%%RH\n", 
           data_before.temperature, data_before.humidity);
    
    // 启动加热器
    printf("\n启动加热器清洁...\n");
    SHT3X_EnableHeater(&sht3x_config, true);
    
    // 加热10秒
    for (int i = 0; i < 10; i++) {
        HAL_Delay(1000);
        printf(".");
    }
    printf("\n");
    
    // 关闭加热器
    SHT3X_EnableHeater(&sht3x_config, false);
    
    // 等待冷却
    printf("等待冷却...\n");
    HAL_Delay(30000);
    
    // 读取清洁后数据
    SHT3X_Data data_after;
    SHT3X_Read(&sht3x_config, &data_after);
    printf("清洁后: T=%.2f°C, H=%.2f%%RH\n",
           data_after.temperature, data_after.humidity);
    
    printf("\n✓ 清洁完成\n");
    printf("建议每月执行一次自清洁程序\n");
}
```

## 性能优化建议

### 降低功耗

```c
/**
 * @brief  低功耗模式示例
 */
void low_power_example(void) {
    SHT3X_Data data;
    
    while (1) {
        // 唤醒传感器并读取数据
        SHT3X_Read(&sht3x_config, &data);
        
        // 处理数据
        process_sensor_data(&data);
        
        // 关闭I2C外设
        __HAL_RCC_I2C1_CLK_DISABLE();
        
        // 进入低功耗模式
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        
        // 唤醒后恢复时钟
        SystemClock_Config();
        __HAL_RCC_I2C1_CLK_ENABLE();
        
        // 下次测量间隔（例如：每10分钟）
        // 实际由RTC或定时器唤醒
    }
}
```

### 提高可靠性

```c
/**
 * @brief  带重试机制的读取
 */
bool reliable_read(SHT3X_Config* config, SHT3X_Data* data, uint8_t max_retry) {
    for (uint8_t i = 0; i < max_retry; i++) {
        if (SHT3X_Read(config, data)) {
            // 数据有效性检查
            if (validate_sensor_data(data)) {
                return true;
            }
        }
        
        // 失败后延时重试
        HAL_Delay(100);
    }
    
    return false;
}

/**
 * @brief  多传感器冗余
 */
void multi_sensor_redundancy(void) {
    SHT3X_Config sensor1 = {.hi2c = &hi2c1, .address = SHT3X_ADDR_LOW};
    SHT3X_Config sensor2 = {.hi2c = &hi2c1, .address = SHT3X_ADDR_HIGH};
    
    SHT3X_Data data1, data2;
    
    bool read1 = SHT3X_Read(&sensor1, &data1);
    bool read2 = SHT3X_Read(&sensor2, &data2);
    
    if (read1 && read2) {
        // 两个传感器都正常，取平均值
        float temp_avg = (data1.temperature + data2.temperature) / 2.0f;
        float humi_avg = (data1.humidity + data2.humidity) / 2.0f;
        
        printf("平均值: T=%.2f°C, H=%.2f%%RH\n", temp_avg, humi_avg);
        
        // 检查差异
        float temp_diff = fabsf(data1.temperature - data2.temperature);
        float humi_diff = fabsf(data1.humidity - data2.humidity);
        
        if (temp_diff > 2.0f || humi_diff > 5.0f) {
            printf("⚠ 警告：传感器读数差异较大！\n");
            printf("  传感器1: T=%.2f°C, H=%.2f%%RH\n",
                   data1.temperature, data1.humidity);
            printf("  传感器2: T=%.2f°C, H=%.2f%%RH\n",
                   data2.temperature, data2.humidity);
        }
    } else if (read1) {
        // 只有传感器1正常
        printf("使用传感器1数据\n");
    } else if (read2) {
        // 只有传感器2正常
        printf("使用传感器2数据\n");
    } else {
        // 两个传感器都失败
        printf("❌ 所有传感器读取失败！\n");
    }
}
```

## 总结

### 关键要点

1. **传感器选型**：
   - 入门学习：DHT11（便宜、简单）
   - 一般应用：DHT22（性价比高）
   - 精密测量：SHT30/SHT31（高精度）

2. **硬件设计**：
   - 必须添加上拉电阻（4.7kΩ）
   - 电源去耦电容（0.1μF）
   - 注意数据线长度
   - 合理选择I2C地址

3. **软件实现**：
   - DHT：使用精确的微秒延时
   - SHT3x：正确实现CRC校验
   - 添加数据有效性检查
   - 实现重试机制

4. **校准维护**：
   - 定期校准提高精度
   - 使用标准参考源
   - 记录校准参数
   - 定期清洁传感器

5. **实际应用**：
   - 合理设置采样间隔
   - 添加数据滤波
   - 实现报警功能
   - 考虑低功耗设计

### 下一步学习

完成本教程后，建议继续学习：

- **加速度计与陀螺仪基础**：学习运动传感器
- **光照与气压传感器应用**：扩展环境监测能力
- **传感器数据融合技术**：多传感器协同工作

### 参考资源

**数据手册**：
- DHT11 Datasheet
- DHT22/AM2302 Datasheet
- SHT30 Datasheet
- SHT31 Datasheet

**应用笔记**：
- Sensirion - Handling Instructions for SHT3x
- Sensirion - Calibration Guide
- DHT Sensor Application Notes

**开发工具**：
- STM32CubeMX
- Sensirion SHT3x Evaluation Kit
- I2C分析仪

**在线资源**：
- Sensirion官方网站
- Adafruit DHT传感器教程
- Arduino温湿度传感器库

---

**作者**: 嵌入式知识平台内容团队  
**最后更新**: 2026-03-07  
**版本**: 1.0.0
