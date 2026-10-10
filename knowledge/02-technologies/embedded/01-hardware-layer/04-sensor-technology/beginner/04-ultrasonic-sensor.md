---
# 基础信息
title: "超声波测距传感器实战"
description: "全面讲解超声波测距传感器HC-SR04的工作原理、测距方法、精度优化技术、多传感器应用和障碍物检测实战案例"
slug: "ultrasonic-sensor"

# 分类信息
domain: "01-hardware-layer"
module: "04-sensor-technology"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 超声波
  - 测距
  - HC-SR04
  - 障碍物检测
  - 距离传感器
prerequisites:
  - "01-chip-architecture/beginner/07-register-operations"
  - "02-hardware-design-fundamentals/beginner/08-interface-circuits"
related_contents:
  - "01-temperature-humidity-sensor"
  - "02-accelerometer-gyroscope"
  - "03-light-pressure-sensor"

# 学习信息
estimated_time: 50
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
  - 超声波传感器
  - HC-SR04
  - 测距传感器
  - 障碍物检测
  - 距离测量
  - 超声波测距
cover_image: ""
---

# 超声波测距传感器实战

## 概述

超声波测距传感器是嵌入式系统中最常用的非接触式距离测量传感器，广泛应用于机器人避障、智能小车、停车辅助、液位检测、物体检测等领域。本教程将详细介绍HC-SR04超声波传感器的工作原理、硬件连接、软件驱动开发和实际应用案例。

### 为什么需要超声波传感器

1. **距离测量**：
   - 非接触式测量
   - 测量范围广（2cm-400cm）
   - 成本低廉
   - 使用简单

2. **障碍物检测**：
   - 机器人避障
   - 智能小车导航
   - 无人机高度检测
   - 自动泊车辅助

3. **物体检测**：
   - 人员接近检测
   - 物体存在判断
   - 液位监测
   - 料位检测

4. **应用优势**：
   - 不受光线影响
   - 对透明物体有效
   - 抗干扰能力强
   - 精度适中

### 超声波传感器对比

```
常用超声波传感器对比：

┌──────────┬─────────────┬─────────────┬─────────────┐
│ 参数     │ HC-SR04     │ US-100      │ JSN-SR04T   │
├──────────┼─────────────┼─────────────┼─────────────┤
│ 测量范围 │ 2-400cm     │ 2-450cm     │ 25-450cm    │
│ 精度     │ ±3mm        │ ±1mm        │ ±2mm        │
│ 接口     │ GPIO触发    │ GPIO/UART   │ GPIO触发    │
│ 电压     │ 5V          │ 5V          │ 3-5.5V      │
│ 电流     │ 15mA        │ 15mA        │ 30mA        │
│ 频率     │ 40kHz       │ 40kHz       │ 40kHz       │
│ 防水     │ 否          │ 否          │ 是          │
│ 价格     │ 低          │ 中          │ 中          │
│ 适用场景 │ 入门学习    │ 精密测量    │ 户外应用    │
└──────────┴─────────────┴─────────────┴─────────────┘

选型建议：
- 学习入门：HC-SR04（便宜、简单）
- 精密测量：US-100（高精度、双接口）
- 户外应用：JSN-SR04T（防水、稳定）
- 远距离：US-100或JSN-SR04T（测量范围更大）
```



## 第一部分：HC-SR04工作原理

### 超声波测距原理

**基本原理**：

```
超声波测距原理图：

发射器                                接收器
  │                                    │
  │ 发射超声波脉冲                     │
  ├────────────────────────────────────┤
  │                                    │
  │                                    │
  │            障碍物                  │
  │              ║                     │
  │              ║ 反射                │
  │              ║                     │
  │              ▼                     │
  │◄───────────────────────────────────┤
  │                                    │
  │ 接收回波信号                       │
  └────────────────────────────────────┘

测距公式：
距离 = (声速 × 时间) / 2

其中：
- 声速：约340 m/s（20°C时）
- 时间：从发射到接收的时间间隔
- 除以2：因为声波往返一次

实际计算：
距离(cm) = (时间(μs) × 0.034) / 2
         = 时间(μs) / 58.8
         = 时间(μs) / 58  (近似)

或者：
距离(cm) = 时间(μs) × 0.017
```

**声速与温度关系**：

```
声速随温度变化：

温度(°C)    声速(m/s)    修正系数
  -10         325.4        0.956
    0         331.5        0.974
   10         337.5        0.992
   20         343.4        1.010
   30         349.2        1.027
   40         355.0        1.044

修正公式：
声速 = 331.5 + 0.6 × 温度(°C)

精确测距：
距离(cm) = (时间(μs) × 声速(m/s)) / 20000
```

### HC-SR04硬件结构

**HC-SR04引脚定义**：

```
HC-SR04引脚（4针）：

    ┌─────────────┐
    │   HC-SR04   │
    │             │
    │  T      R   │  T: 发射器
    │  ┌────┐     │  R: 接收器
    └──┴─┴─┴─┴────┘
       1 2 3 4

引脚说明：
1. VCC   - 电源正极（5V）
2. Trig  - 触发引脚（输入）
3. Echo  - 回波引脚（输出）
4. GND   - 电源地

工作参数：
- 工作电压：5V DC
- 工作电流：15mA
- 工作频率：40kHz
- 测量范围：2cm - 400cm
- 测量角度：15°
- 精度：±3mm
- 触发信号：10μs TTL脉冲
```

**硬件连接电路**：

```
连接方案：

MCU (3.3V)             HC-SR04 (5V)
                      ┌─────────────┐
5V ───────────────────┤1 VCC        │
                      │             │
GPIO_Trig ────────────┤2 Trig       │
                      │             │
GPIO_Echo ────┬───────┤3 Echo       │
              │       │             │
             ┌┴┐      │4 GND        │
        1kΩ  │ │      └─────────────┘
             └┬┘
              │
             ┌┴┐
        2kΩ  │ │  电平转换（5V→3.3V）
             └┬┘
              │
GND ──────────┴───────────┘

关键要点：
1. HC-SR04需要5V供电
2. Trig引脚可直接连接3.3V GPIO（5V容忍）
3. Echo引脚需要电平转换（5V→3.3V）
4. 使用分压电阻：R1=1kΩ, R2=2kΩ
5. 或使用电平转换芯片（如74LVC245）
```

### 时序协议

**HC-SR04时序图**：

```
测距时序：

1. 触发信号（Trig）：
   MCU发送至少10μs的高电平脉冲

   Trig: ────┐          ┌────
             └──────────┘
             <-- >10μs -->

2. 发射超声波：
   HC-SR04自动发射8个40kHz超声波脉冲

   超声波: ┌┐┌┐┌┐┌┐┌┐┌┐┌┐┌┐
          └┘└┘└┘└┘└┘└┘└┘└┘
          <---- 200μs ---->

3. 回波信号（Echo）：
   HC-SR04拉高Echo引脚，直到接收到回波

   Echo: ────┐                    ┌────
             └────────────────────┘
             <---- 时间 T -------->

   时间T = 距离 × 58 (μs/cm)

4. 完整测距周期：

   Trig: ──┐  ┌──────────────────────
           └──┘
           10μs

   Echo: ────────┐              ┌─────
                 └──────────────┘
                 <---- T ------>

   超声波: ──────┐┐┐┐┐┐┐┐        ┌┐┐┐
                 └┘└┘└┘└┘        └┘└┘
                 发射              接收

5. 测量周期：
   - 最小间隔：60ms（避免回波干扰）
   - 推荐间隔：100ms
   - 超时时间：38ms（对应650cm）
```

**特殊情况处理**：

```
1. 无回波（超出范围或无障碍物）：
   Echo保持高电平约38ms后自动拉低

   Echo: ────┐                          ┌────
             └──────────────────────────┘
             <-------- 38ms ----------->

2. 近距离测量（<2cm）：
   可能无法区分发射和接收信号
   返回不稳定或错误数据

3. 角度偏差：
   超出15°锥形范围，信号减弱
   可能无法接收回波

4. 表面材质影响：
   - 硬质平面：反射强，测量准确
   - 软质材料：吸收声波，测量困难
   - 倾斜表面：反射偏离，可能无回波
```



## 第二部分：HC-SR04驱动开发

### 驱动头文件

```c
/**
 * @file    hcsr04.h
 * @brief   HC-SR04超声波测距传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __HCSR04_H
#define __HCSR04_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>

/**
 * @brief  HC-SR04配置结构
 */
typedef struct {
    GPIO_TypeDef* trig_port;    // Trig引脚端口
    uint16_t trig_pin;          // Trig引脚
    GPIO_TypeDef* echo_port;    // Echo引脚端口
    uint16_t echo_pin;          // Echo引脚
    float temperature;          // 环境温度（°C），用于声速修正
} HCSR04_Config;

/**
 * @brief  测量结果结构
 */
typedef struct {
    float distance_cm;          // 距离（厘米）
    float distance_mm;          // 距离（毫米）
    uint32_t echo_time_us;      // 回波时间（微秒）
    bool valid;                 // 数据有效标志
} HCSR04_Data;

// 测量参数
#define HCSR04_MAX_DISTANCE_CM    400    // 最大测量距离（cm）
#define HCSR04_MIN_DISTANCE_CM    2      // 最小测量距离（cm）
#define HCSR04_TIMEOUT_US         38000  // 超时时间（μs）
#define HCSR04_SOUND_SPEED_20C    343.4f // 20°C时声速（m/s）

// 函数声明
void HCSR04_Init(HCSR04_Config* config);
bool HCSR04_Measure(HCSR04_Config* config, HCSR04_Data* data);
float HCSR04_GetSoundSpeed(float temperature);
void HCSR04_Delay_us(uint32_t us);

#endif /* __HCSR04_H */
```


### 驱动实现文件

```c
/**
 * @file    hcsr04.c
 * @brief   HC-SR04超声波测距传感器驱动实现
 */

#include "hcsr04.h"

/**
 * @brief  微秒级延时（使用DWT）
 * @param  us: 延时时间（微秒）
 */
void HCSR04_Delay_us(uint32_t us) {
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000);
    
    while ((DWT->CYCCNT - start) < cycles);
}

/**
 * @brief  初始化HC-SR04传感器
 * @param  config: 传感器配置
 */
void HCSR04_Init(HCSR04_Config* config) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能DWT计数器（用于微秒延时）
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    
    // 配置Trig引脚为输出
    GPIO_InitStruct.Pin = config->trig_pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(config->trig_port, &GPIO_InitStruct);
    
    // 配置Echo引脚为输入
    GPIO_InitStruct.Pin = config->echo_pin;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(config->echo_port, &GPIO_InitStruct);
    
    // Trig引脚初始状态为低电平
    HAL_GPIO_WritePin(config->trig_port, config->trig_pin, GPIO_PIN_RESET);
    
    // 设置默认温度
    if (config->temperature == 0) {
        config->temperature = 20.0f;  // 默认20°C
    }
}

/**
 * @brief  根据温度计算声速
 * @param  temperature: 温度（°C）
 * @retval 声速（m/s）
 */
float HCSR04_GetSoundSpeed(float temperature) {
    // 声速公式：v = 331.5 + 0.6 × T
    return 331.5f + 0.6f * temperature;
}

/**
 * @brief  测量距离
 * @param  config: 传感器配置
 * @param  data: 测量结果
 * @retval true: 测量成功, false: 测量失败
 */
bool HCSR04_Measure(HCSR04_Config* config, HCSR04_Data* data) {
    uint32_t timeout;
    uint32_t start_time, end_time;
    
    // 1. 发送触发信号（至少10μs高电平）
    HAL_GPIO_WritePin(config->trig_port, config->trig_pin, GPIO_PIN_RESET);
    HCSR04_Delay_us(2);
    
    HAL_GPIO_WritePin(config->trig_port, config->trig_pin, GPIO_PIN_SET);
    HCSR04_Delay_us(12);  // 12μs触发脉冲
    
    HAL_GPIO_WritePin(config->trig_port, config->trig_pin, GPIO_PIN_RESET);
    
    // 2. 等待Echo引脚变高（超时保护）
    timeout = 0;
    while (HAL_GPIO_ReadPin(config->echo_port, config->echo_pin) == GPIO_PIN_RESET) {
        HCSR04_Delay_us(1);
        if (++timeout > 10000) {  // 10ms超时
            data->valid = false;
            return false;
        }
    }
    
    // 3. 记录Echo高电平开始时间
    start_time = DWT->CYCCNT;
    
    // 4. 等待Echo引脚变低（超时保护）
    timeout = 0;
    while (HAL_GPIO_ReadPin(config->echo_port, config->echo_pin) == GPIO_PIN_SET) {
        HCSR04_Delay_us(1);
        if (++timeout > HCSR04_TIMEOUT_US) {  // 38ms超时
            data->valid = false;
            return false;
        }
    }
    
    // 5. 记录Echo高电平结束时间
    end_time = DWT->CYCCNT;
    
    // 6. 计算回波时间（微秒）
    uint32_t cycles = end_time - start_time;
    data->echo_time_us = cycles / (SystemCoreClock / 1000000);
    
    // 7. 计算距离
    // 使用温度修正的声速
    float sound_speed = HCSR04_GetSoundSpeed(config->temperature);
    
    // 距离(cm) = (时间(μs) × 声速(m/s)) / 20000
    data->distance_cm = (data->echo_time_us * sound_speed) / 20000.0f;
    data->distance_mm = data->distance_cm * 10.0f;
    
    // 8. 验证测量范围
    if (data->distance_cm < HCSR04_MIN_DISTANCE_CM || 
        data->distance_cm > HCSR04_MAX_DISTANCE_CM) {
        data->valid = false;
        return false;
    }
    
    data->valid = true;
    return true;
}
```

/**
 * @brief  多次测量取平均值（提高精度）
 * @param  config: 传感器配置
 * @param  samples: 采样次数
 * @param  data: 测量结果
 * @retval true: 测量成功, false: 测量失败
 */
bool HCSR04_MeasureAverage(HCSR04_Config* config, uint8_t samples, HCSR04_Data* data) {
    float distance_sum = 0;
    uint8_t valid_count = 0;
    HCSR04_Data temp_data;
    
    for (uint8_t i = 0; i < samples; i++) {
        if (HCSR04_Measure(config, &temp_data)) {
            distance_sum += temp_data.distance_cm;
            valid_count++;
        }
        
        // 测量间隔（避免回波干扰）
        HAL_Delay(60);
    }
    
    // 至少有一半测量成功
    if (valid_count < samples / 2) {
        data->valid = false;
        return false;
    }
    
    // 计算平均值
    data->distance_cm = distance_sum / valid_count;
    data->distance_mm = data->distance_cm * 10.0f;
    data->valid = true;
    
    return true;
}
```



### 使用示例

```c
/**
 * @file    main.c
 * @brief   HC-SR04超声波传感器使用示例
 */

#include "stm32f1xx_hal.h"
#include "hcsr04.h"
#include <stdio.h>

// HC-SR04传感器配置
HCSR04_Config hcsr04_config = {
    .trig_port = GPIOA,
    .trig_pin = GPIO_PIN_0,
    .echo_port = GPIOA,
    .echo_pin = GPIO_PIN_1,
    .temperature = 20.0f    // 20°C
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
    
    printf("HC-SR04超声波测距传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化HC-SR04传感器
    HCSR04_Init(&hcsr04_config);
    
    printf("✓ HC-SR04初始化成功\n\n");
    
    HCSR04_Data data;
    uint32_t measure_count = 0;
    uint32_t error_count = 0;
    
    while (1) {
        // 测量距离
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            measure_count++;
            
            // 打印测量结果
            printf("测量 #%lu:\n", measure_count);
            printf("  距离: %.1f cm (%.0f mm)\n", 
                   data.distance_cm, data.distance_mm);
            printf("  回波时间: %lu μs\n", data.echo_time_us);
            
            // 距离分级提示
            if (data.distance_cm < 10) {
                printf("  状态: 🔴 非常近\n");
            } else if (data.distance_cm < 30) {
                printf("  状态: 🟡 较近\n");
            } else if (data.distance_cm < 100) {
                printf("  状态: 🟢 中等\n");
            } else {
                printf("  状态: 🔵 较远\n");
            }
            
            printf("\n");
        } else {
            error_count++;
            printf("测量失败 #%lu (总错误: %lu)\n\n", 
                   measure_count + error_count, error_count);
        }
        
        // 测量间隔（推荐至少60ms）
        HAL_Delay(100);
    }
}

/**
 * @brief  障碍物检测示例
 */
void obstacle_detection_example(void) {
    const float SAFE_DISTANCE = 30.0f;    // 安全距离（cm）
    const float WARNING_DISTANCE = 15.0f; // 警告距离（cm）
    const float DANGER_DISTANCE = 5.0f;   // 危险距离（cm）
    
    HCSR04_Data data;
    
    printf("障碍物检测系统\n");
    printf("═══════════════════════════════════════\n");
    printf("安全距离: %.1f cm\n", SAFE_DISTANCE);
    printf("警告距离: %.1f cm\n", WARNING_DISTANCE);
    printf("危险距离: %.1f cm\n\n", DANGER_DISTANCE);
    
    while (1) {
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            printf("距离: %.1f cm - ", data.distance_cm);
            
            if (data.distance_cm < DANGER_DISTANCE) {
                printf("🔴 危险！立即停止\n");
                // 触发紧急停止
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);  // 红灯
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
                // 蜂鸣器快速报警
                for (int i = 0; i < 5; i++) {
                    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_SET);
                    HAL_Delay(50);
                    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
                    HAL_Delay(50);
                }
            } else if (data.distance_cm < WARNING_DISTANCE) {
                printf("🟡 警告！减速\n");
                // 触发警告
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);  // 黄灯
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
                // 蜂鸣器慢速报警
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_SET);
                HAL_Delay(200);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
            } else if (data.distance_cm < SAFE_DISTANCE) {
                printf("🟢 注意！有障碍物\n");
                // 正常状态
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);  // 绿灯
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
            } else {
                printf("✓ 安全\n");
                // 关闭所有指示
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
            }
        }
        
        HAL_Delay(100);
    }
}
```


/**
 * @brief  停车辅助示例
 */
void parking_assist_example(void) {
    HCSR04_Data data;
    float last_distance = 0;
    
    printf("停车辅助系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            printf("距离: %.1f cm\n", data.distance_cm);
            
            // 计算蜂鸣器频率（距离越近，频率越高）
            uint16_t beep_interval;
            
            if (data.distance_cm < 10) {
                beep_interval = 100;  // 非常快
                printf("状态: 🔴🔴🔴 停止！\n");
            } else if (data.distance_cm < 20) {
                beep_interval = 200;  // 快
                printf("状态: 🔴🔴 非常近\n");
            } else if (data.distance_cm < 40) {
                beep_interval = 400;  // 中等
                printf("状态: 🟡 较近\n");
            } else if (data.distance_cm < 80) {
                beep_interval = 800;  // 慢
                printf("状态: 🟢 安全\n");
            } else {
                beep_interval = 0;    // 不响
                printf("状态: ✓ 距离充足\n");
            }
            
            // 蜂鸣器控制
            if (beep_interval > 0) {
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_SET);
                HAL_Delay(50);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_3, GPIO_PIN_RESET);
                HAL_Delay(beep_interval - 50);
            } else {
                HAL_Delay(500);
            }
            
            // 显示距离变化趋势
            if (last_distance > 0) {
                float change = data.distance_cm - last_distance;
                if (change < -1.0f) {
                    printf("趋势: ← 接近中\n");
                } else if (change > 1.0f) {
                    printf("趋势: → 远离中\n");
                } else {
                    printf("趋势: ═ 稳定\n");
                }
            }
            
            last_distance = data.distance_cm;
            printf("\n");
        }
    }
}

/**
 * @brief  液位检测示例
 */
void liquid_level_detection_example(void) {
    const float TANK_HEIGHT = 200.0f;     // 容器高度（cm）
    const float SENSOR_HEIGHT = 210.0f;   // 传感器安装高度（cm）
    const float FULL_LEVEL = 180.0f;      // 满液位（cm）
    const float LOW_LEVEL = 30.0f;        // 低液位（cm）
    
    HCSR04_Data data;
    
    printf("液位检测系统\n");
    printf("═══════════════════════════════════════\n");
    printf("容器高度: %.1f cm\n", TANK_HEIGHT);
    printf("满液位: %.1f cm\n", FULL_LEVEL);
    printf("低液位: %.1f cm\n\n", LOW_LEVEL);
    
    while (1) {
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            // 计算液位高度
            float liquid_level = SENSOR_HEIGHT - data.distance_cm;
            
            // 计算液位百分比
            float level_percent = (liquid_level / TANK_HEIGHT) * 100.0f;
            
            // 限制百分比范围
            if (level_percent < 0) level_percent = 0;
            if (level_percent > 100) level_percent = 100;
            
            printf("测量距离: %.1f cm\n", data.distance_cm);
            printf("液位高度: %.1f cm\n", liquid_level);
            printf("液位百分比: %.1f%%\n", level_percent);
            
            // 液位状态判断
            if (liquid_level >= FULL_LEVEL) {
                printf("状态: 🔴 液位过高！\n");
                // 触发高液位报警
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
            } else if (liquid_level <= LOW_LEVEL) {
                printf("状态: 🟡 液位过低！\n");
                // 触发低液位报警
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);
            } else {
                printf("状态: 🟢 液位正常\n");
                // 关闭报警
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
            }
            
            // 显示液位条形图
            printf("液位: [");
            int bars = (int)(level_percent / 5);  // 每5%一个方块
            for (int i = 0; i < 20; i++) {
                if (i < bars) {
                    printf("█");
                } else {
                    printf("░");
                }
            }
            printf("]\n\n");
        }
        
        HAL_Delay(1000);
    }
}
```



## 第三部分：精度优化

### 多次测量滤波

```c
/**
 * @brief  中值滤波（去除异常值）
 * @param  config: 传感器配置
 * @param  samples: 采样次数（建议奇数）
 * @param  data: 测量结果
 * @retval true: 测量成功, false: 测量失败
 */
bool HCSR04_MeasureMedian(HCSR04_Config* config, uint8_t samples, HCSR04_Data* data) {
    float distances[samples];
    uint8_t valid_count = 0;
    HCSR04_Data temp_data;
    
    // 采集多组数据
    for (uint8_t i = 0; i < samples; i++) {
        if (HCSR04_Measure(config, &temp_data)) {
            distances[valid_count++] = temp_data.distance_cm;
        }
        HAL_Delay(60);
    }
    
    if (valid_count < 3) {
        data->valid = false;
        return false;
    }
    
    // 冒泡排序
    for (uint8_t i = 0; i < valid_count - 1; i++) {
        for (uint8_t j = 0; j < valid_count - i - 1; j++) {
            if (distances[j] > distances[j + 1]) {
                float temp = distances[j];
                distances[j] = distances[j + 1];
                distances[j + 1] = temp;
            }
        }
    }
    
    // 取中值
    data->distance_cm = distances[valid_count / 2];
    data->distance_mm = data->distance_cm * 10.0f;
    data->valid = true;
    
    return true;
}

/**
 * @brief  卡尔曼滤波（平滑测量值）
 */
typedef struct {
    float q;        // 过程噪声协方差
    float r;        // 测量噪声协方差
    float x;        // 估计值
    float p;        // 估计协方差
    float k;        // 卡尔曼增益
} KalmanFilter;

/**
 * @brief  初始化卡尔曼滤波器
 */
void KalmanFilter_Init(KalmanFilter* kf, float q, float r, float initial_value) {
    kf->q = q;
    kf->r = r;
    kf->x = initial_value;
    kf->p = 1.0f;
}

/**
 * @brief  卡尔曼滤波更新
 */
float KalmanFilter_Update(KalmanFilter* kf, float measurement) {
    // 预测
    kf->p = kf->p + kf->q;
    
    // 更新
    kf->k = kf->p / (kf->p + kf->r);
    kf->x = kf->x + kf->k * (measurement - kf->x);
    kf->p = (1 - kf->k) * kf->p;
    
    return kf->x;
}

/**
 * @brief  使用卡尔曼滤波的测量示例
 */
void kalman_filter_example(void) {
    KalmanFilter kf;
    HCSR04_Data data;
    
    // 初始化卡尔曼滤波器
    // q=0.01（过程噪声小），r=0.5（测量噪声中等）
    KalmanFilter_Init(&kf, 0.01f, 0.5f, 100.0f);
    
    printf("卡尔曼滤波测距\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            // 应用卡尔曼滤波
            float filtered_distance = KalmanFilter_Update(&kf, data.distance_cm);
            
            printf("原始值: %.1f cm\n", data.distance_cm);
            printf("滤波值: %.1f cm\n", filtered_distance);
            printf("差值: %.1f cm\n\n", 
                   fabsf(data.distance_cm - filtered_distance));
        }
        
        HAL_Delay(100);
    }
}
```


### 温度补偿

```c
/**
 * @brief  带温度补偿的测距示例
 */
void temperature_compensated_measurement(void) {
    HCSR04_Data data;
    float temperature = 20.0f;  // 可以从温度传感器读取
    
    printf("温度补偿测距\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        // 更新温度（实际应用中从温度传感器读取）
        // temperature = read_temperature_sensor();
        hcsr04_config.temperature = temperature;
        
        if (HCSR04_Measure(&hcsr04_config, &data)) {
            float sound_speed = HCSR04_GetSoundSpeed(temperature);
            
            printf("温度: %.1f °C\n", temperature);
            printf("声速: %.1f m/s\n", sound_speed);
            printf("距离: %.1f cm\n\n", data.distance_cm);
        }
        
        HAL_Delay(1000);
    }
}
```



## 第四部分：多传感器应用

### 多传感器配置

```c
/**
 * @brief  多传感器配置示例（360°检测）
 */

// 定义4个传感器（前后左右）
HCSR04_Config sensors[4] = {
    // 前方传感器
    {
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_0,
        .echo_port = GPIOA,
        .echo_pin = GPIO_PIN_1,
        .temperature = 20.0f
    },
    // 后方传感器
    {
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_2,
        .echo_port = GPIOA,
        .echo_pin = GPIO_PIN_3,
        .temperature = 20.0f
    },
    // 左侧传感器
    {
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_4,
        .echo_port = GPIOA,
        .echo_pin = GPIO_PIN_5,
        .temperature = 20.0f
    },
    // 右侧传感器
    {
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_6,
        .echo_port = GPIOA,
        .echo_pin = GPIO_PIN_7,
        .temperature = 20.0f
    }
};

/**
 * @brief  360°障碍物检测
 */
void multi_sensor_detection(void) {
    HCSR04_Data data[4];
    const char* directions[] = {"前方", "后方", "左侧", "右侧"};
    
    printf("360°障碍物检测系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化所有传感器
    for (int i = 0; i < 4; i++) {
        HCSR04_Init(&sensors[i]);
    }
    
    while (1) {
        printf("═══════════════════════════════════════\n");
        printf("扫描结果:\n\n");
        
        // 依次测量每个方向
        for (int i = 0; i < 4; i++) {
            if (HCSR04_Measure(&sensors[i], &data[i])) {
                printf("%s: %.1f cm ", directions[i], data[i].distance_cm);
                
                // 状态指示
                if (data[i].distance_cm < 20) {
                    printf("🔴 危险\n");
                } else if (data[i].distance_cm < 50) {
                    printf("🟡 警告\n");
                } else {
                    printf("🟢 安全\n");
                }
            } else {
                printf("%s: 测量失败\n", directions[i]);
            }
            
            HAL_Delay(60);  // 传感器间隔
        }
        
        // 找出最近的障碍物
        float min_distance = 1000.0f;
        int min_index = -1;
        
        for (int i = 0; i < 4; i++) {
            if (data[i].valid && data[i].distance_cm < min_distance) {
                min_distance = data[i].distance_cm;
                min_index = i;
            }
        }
        
        if (min_index >= 0) {
            printf("\n最近障碍物: %s %.1f cm\n", 
                   directions[min_index], min_distance);
        }
        
        printf("\n");
        HAL_Delay(500);
    }
}

/**
 * @brief  智能避障导航
 */
void smart_navigation(void) {
    HCSR04_Data data[4];
    const float SAFE_DISTANCE = 40.0f;
    
    printf("智能避障导航系统\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        // 测量所有方向
        bool obstacle_detected = false;
        
        for (int i = 0; i < 4; i++) {
            if (HCSR04_Measure(&sensors[i], &data[i])) {
                if (data[i].distance_cm < SAFE_DISTANCE) {
                    obstacle_detected = true;
                }
            }
            HAL_Delay(60);
        }
        
        // 决策逻辑
        if (!obstacle_detected) {
            printf("✓ 前进\n");
            // 控制电机前进
        } else {
            // 分析各方向距离，选择最优路径
            if (data[0].valid && data[0].distance_cm < SAFE_DISTANCE) {
                printf("⚠ 前方有障碍物\n");
                
                // 比较左右距离
                if (data[2].distance_cm > data[3].distance_cm) {
                    printf("← 左转\n");
                    // 控制电机左转
                } else {
                    printf("→ 右转\n");
                    // 控制电机右转
                }
            } else if (data[1].valid && data[1].distance_cm < SAFE_DISTANCE) {
                printf("⚠ 后方有障碍物\n");
                printf("↑ 前进\n");
                // 控制电机前进
            }
        }
        
        HAL_Delay(200);
    }
}
```



## 第五部分：常见问题与解决

### 测量不稳定

```c
/**
 * @brief  测量稳定性改进
 */

// 问题1：测量值跳动大
// 解决方案：使用滑动平均滤波

#define FILTER_SIZE 5

typedef struct {
    float buffer[FILTER_SIZE];
    uint8_t index;
    bool full;
} MovingAverageFilter;

void MovingAverageFilter_Init(MovingAverageFilter* filter) {
    filter->index = 0;
    filter->full = false;
    for (int i = 0; i < FILTER_SIZE; i++) {
        filter->buffer[i] = 0;
    }
}

float MovingAverageFilter_Update(MovingAverageFilter* filter, float value) {
    filter->buffer[filter->index] = value;
    filter->index++;
    
    if (filter->index >= FILTER_SIZE) {
        filter->index = 0;
        filter->full = true;
    }
    
    // 计算平均值
    float sum = 0;
    int count = filter->full ? FILTER_SIZE : filter->index;
    
    for (int i = 0; i < count; i++) {
        sum += filter->buffer[i];
    }
    
    return sum / count;
}

// 问题2：偶尔出现异常值
// 解决方案：异常值检测和剔除

bool is_valid_measurement(float current, float previous, float threshold) {
    // 如果变化超过阈值，认为是异常值
    if (fabsf(current - previous) > threshold) {
        return false;
    }
    return true;
}

// 问题3：近距离测量不准
// 解决方案：增加最小距离限制和多次测量

bool HCSR04_MeasureReliable(HCSR04_Config* config, HCSR04_Data* data) {
    const uint8_t SAMPLES = 3;
    const float MIN_RELIABLE_DISTANCE = 5.0f;
    
    HCSR04_Data temp_data;
    float distances[SAMPLES];
    uint8_t valid_count = 0;
    
    for (uint8_t i = 0; i < SAMPLES; i++) {
        if (HCSR04_Measure(config, &temp_data)) {
            if (temp_data.distance_cm >= MIN_RELIABLE_DISTANCE) {
                distances[valid_count++] = temp_data.distance_cm;
            }
        }
        HAL_Delay(60);
    }
    
    if (valid_count == 0) {
        data->valid = false;
        return false;
    }
    
    // 计算平均值
    float sum = 0;
    for (uint8_t i = 0; i < valid_count; i++) {
        sum += distances[i];
    }
    
    data->distance_cm = sum / valid_count;
    data->distance_mm = data->distance_cm * 10.0f;
    data->valid = true;
    
    return true;
}
```

### 干扰问题

```c
/**
 * @brief  抗干扰措施
 */

// 问题1：多个传感器相互干扰
// 解决方案：时分复用，依次测量

void measure_with_time_division(void) {
    HCSR04_Data data;
    
    for (int i = 0; i < 4; i++) {
        // 测量第i个传感器
        if (HCSR04_Measure(&sensors[i], &data)) {
            // 处理数据
        }
        
        // 等待足够长的时间，避免回波干扰
        HAL_Delay(100);
    }
}

// 问题2：环境噪声干扰
// 解决方案：增加重试机制

bool HCSR04_MeasureWithRetry(HCSR04_Config* config, HCSR04_Data* data, uint8_t max_retries) {
    for (uint8_t retry = 0; retry < max_retries; retry++) {
        if (HCSR04_Measure(config, data)) {
            return true;
        }
        HAL_Delay(60);
    }
    
    data->valid = false;
    return false;
}

// 问题3：电源噪声影响
// 解决方案：硬件滤波和软件去抖

// 硬件：在VCC和GND之间加0.1μF和10μF电容
// 软件：使用数字滤波算法
```



## 总结

### 关键要点

1. **工作原理**：
   - 超声波往返时间测距
   - 声速受温度影响
   - 测量范围2-400cm
   - 精度约±3mm

2. **硬件连接**：
   - 需要5V供电
   - Echo引脚需要电平转换
   - 注意测量间隔（≥60ms）
   - 避免多传感器干扰

3. **软件驱动**：
   - 使用DWT实现微秒延时
   - 精确测量回波时间
   - 温度补偿提高精度
   - 滤波算法去除噪声

4. **应用场景**：
   - 障碍物检测和避障
   - 停车辅助系统
   - 液位和料位检测
   - 距离测量和定位

### 常见问题

**Q1：为什么测量值不稳定？**
- 表面材质影响：使用滤波算法
- 角度偏差：调整传感器角度
- 环境干扰：增加测量次数
- 电源噪声：改善电源滤波

**Q2：近距离测量不准怎么办？**
- 盲区问题：HC-SR04最小2cm
- 增加最小距离限制
- 使用多次测量平均
- 考虑使用红外传感器

**Q3：如何提高测量精度？**
- 温度补偿修正声速
- 多次测量取平均或中值
- 使用卡尔曼滤波
- 校准传感器

**Q4：多个传感器如何避免干扰？**
- 时分复用，依次测量
- 增加测量间隔（≥100ms）
- 使用不同频率传感器
- 物理隔离传感器

### 进阶学习

1. **高级滤波算法**：扩展卡尔曼滤波、粒子滤波
2. **传感器融合**：结合红外、激光等传感器
3. **SLAM应用**：同步定位与地图构建
4. **机器学习**：障碍物识别和分类

### 参考资料

- HC-SR04数据手册
- 超声波测距原理
- 《传感器技术与应用》
- 开源项目：Arduino超声波库

---

**下一步学习**：
- [传感器数据融合技术](../intermediate/02-sensor-fusion.html)
- [生物传感器：心率与血氧检测](../intermediate/01-biosensor.html)
- [智能小车运动控制系统](../../05-actuator-control/advanced/01-smart-car-control.html)
