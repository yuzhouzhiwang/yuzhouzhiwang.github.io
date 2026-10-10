---
# 基础信息
title: "加速度计与陀螺仪基础"
description: "深入讲解MEMS加速度计和陀螺仪的工作原理、MPU6050传感器的使用方法、数据解析技术、姿态计算算法和实际应用场景"
slug: "accelerometer-gyroscope"

# 分类信息
domain: "01-hardware-layer"
module: "04-sensor-technology"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 加速度计
  - 陀螺仪
  - MPU6050
  - 姿态检测
  - MEMS
  - IMU
prerequisites:
  - "01-chip-architecture/beginner/07-register-operations"
  - "02-hardware-design-fundamentals/beginner/08-interface-circuits"
related_contents:
  - "01-temperature-humidity-sensor"
  - "03-light-pressure-sensor"
  - "04-sensor-technology/intermediate/02-sensor-fusion"

# 学习信息
estimated_time: 40
difficulty_score: 3

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
  - 加速度计
  - 陀螺仪
  - MPU6050
  - 姿态检测
  - MEMS传感器
  - IMU
  - 运动传感器
cover_image: ""
---

# 加速度计与陀螺仪基础

## 概述

加速度计和陀螺仪是现代嵌入式系统中最重要的运动传感器，广泛应用于智能手机、无人机、机器人、可穿戴设备、游戏控制器等领域。本文将详细介绍MEMS（微机电系统）加速度计和陀螺仪的工作原理，重点讲解MPU6050六轴传感器的使用方法、数据解析和姿态计算。

### 为什么需要运动传感器

1. **姿态检测**：
   - 设备方向识别
   - 屏幕旋转控制
   - 水平校准
   - 倾斜角度测量

2. **运动追踪**：
   - 步数统计
   - 运动轨迹记录
   - 手势识别
   - 跌倒检测

3. **导航定位**：
   - 惯性导航系统
   - 航向角计算
   - 位置估算
   - GPS辅助定位

4. **稳定控制**：
   - 无人机姿态稳定
   - 云台防抖
   - 机器人平衡
   - 相机防抖

### 加速度计与陀螺仪对比

```
传感器特性对比：

┌──────────┬────────────────┬────────────────┐
│ 特性     │ 加速度计       │ 陀螺仪         │
├──────────┼────────────────┼────────────────┤
│ 测量对象 │ 线性加速度     │ 角速度         │
│ 单位     │ g (m/s²)       │ °/s (rad/s)    │
│ 坐标轴   │ X, Y, Z        │ X, Y, Z        │
│ 静态精度 │ 高             │ 低（漂移）     │
│ 动态响应 │ 慢             │ 快             │
│ 重力影响 │ 有             │ 无             │
│ 主要用途 │ 倾角测量       │ 旋转速度测量   │
│ 典型应用 │ 水平检测       │ 航向角计算     │
└──────────┴────────────────┴────────────────┘

互补特性：
- 加速度计：长期稳定，但对振动敏感
- 陀螺仪：短期准确，但存在累积漂移
- 组合使用：通过数据融合获得最佳性能
```



## 第一部分：MEMS原理

### 加速度计工作原理

**MEMS加速度计结构**：

```
MEMS加速度计原理图：

固定电极        可动质量块        固定电极
    │              │                │
    ├──────────────┼──────────────┤
    │   ┌──────────┴──────────┐   │
    │   │                      │   │
    ├───┤      质量块 (m)      ├───┤
    │   │                      │   │
    │   └──────────┬──────────┘   │
    ├──────────────┼──────────────┤
    │              │                │
   C1            弹簧              C2

工作原理：
1. 质量块通过弹簧悬浮在固定电极之间
2. 加速度使质量块产生位移
3. 位移改变电容值（C1和C2）
4. 电容变化转换为电压信号
5. ADC将电压转换为数字量

测量公式：
F = m × a  （牛顿第二定律）
x = F / k  （胡克定律，k为弹簧系数）

电容变化：
ΔC = ε₀ × A × Δx / d²
其中：
- ε₀: 真空介电常数
- A: 电极面积
- Δx: 位移
- d: 电极间距
```

**三轴加速度计**：

```
三轴加速度计坐标系：

        Z轴（垂直向上）
        ↑
        │
        │
        └────→ X轴（向右）
       ╱
      ╱
     ↙ Y轴（向前）

重力加速度分量：
- 水平放置：X=0g, Y=0g, Z=1g
- 垂直放置：X=1g, Y=0g, Z=0g
- 倾斜θ角：X=sin(θ)g, Y=0g, Z=cos(θ)g

测量范围：
- ±2g：高精度，适合姿态检测
- ±4g：平衡精度和范围
- ±8g：适合运动检测
- ±16g：高冲击应用
```

### 陀螺仪工作原理

**MEMS陀螺仪结构**：

```
MEMS陀螺仪原理（科里奥利效应）：

驱动方向
    ↕
    │
    │  质量块振动
    │
    └────→ 检测方向
         （科里奥利力）

工作原理：
1. 质量块在驱动方向上振动
2. 当传感器旋转时，产生科里奥利力
3. 科里奥利力使质量块在检测方向上位移
4. 位移量正比于角速度
5. 电容检测位移并转换为数字量

科里奥利力公式：
Fc = 2m × v × ω
其中：
- m: 质量块质量
- v: 振动速度
- ω: 角速度

角速度积分得到角度：
θ = ∫ω dt
```

**三轴陀螺仪**：

```
三轴陀螺仪测量：

绕X轴旋转（Roll - 横滚）：
    ↻
    │
    └────→ X轴

绕Y轴旋转（Pitch - 俯仰）：
    ↻
    │
    └────→ Y轴

绕Z轴旋转（Yaw - 偏航）：
    ↻
    │
    └────→ Z轴

测量范围：
- ±250°/s：高精度，慢速旋转
- ±500°/s：平衡精度和范围
- ±1000°/s：快速旋转
- ±2000°/s：极快旋转
```



## 第二部分：MPU6050传感器

### MPU6050简介

**MPU6050特性**：

```
MPU6050六轴传感器：

集成组件：
┌─────────────────────────────┐
│        MPU6050              │
│                             │
│  ┌──────────────────────┐  │
│  │  三轴加速度计        │  │
│  │  ±2g/±4g/±8g/±16g   │  │
│  └──────────────────────┘  │
│                             │
│  ┌──────────────────────┐  │
│  │  三轴陀螺仪          │  │
│  │  ±250/±500/±1000/   │  │
│  │  ±2000 °/s          │  │
│  └──────────────────────┘  │
│                             │
│  ┌──────────────────────┐  │
│  │  16位ADC             │  │
│  └──────────────────────┘  │
│                             │
│  ┌──────────────────────┐  │
│  │  数字运动处理器(DMP)│  │
│  └──────────────────────┘  │
│                             │
│  ┌──────────────────────┐  │
│  │  I2C接口             │  │
│  └──────────────────────┘  │
└─────────────────────────────┘

主要特性：
- 工作电压：2.375V - 3.46V
- 工作电流：3.9mA（正常模式）
- 睡眠电流：5μA
- I2C速度：400kHz
- 数据输出速率：最高8kHz
- 内置温度传感器
- 可编程中断
- 内置FIFO缓冲区（1024字节）
```

### 硬件连接

**MPU6050引脚定义**：

```
MPU6050模块引脚（GY-521）：

    ┌─────────────┐
    │   MPU6050   │
    │   GY-521    │
    └─┬─┬─┬─┬─┬─┬─┬─┬─┘
      1 2 3 4 5 6 7 8

引脚说明：
1. VCC  - 电源正极（3.3V-5V）
2. GND  - 电源地
3. SCL  - I2C时钟线
4. SDA  - I2C数据线
5. XDA  - 辅助I2C数据（可选）
6. XCL  - 辅助I2C时钟（可选）
7. AD0  - I2C地址选择
8. INT  - 中断输出（可选）

I2C地址：
- AD0接GND: 0x68
- AD0接VCC: 0x69
```

**硬件连接电路**：

```
连接方案：

MCU                    MPU6050
                      ┌─────────┐
3.3V ─────────────────┤1 VCC    │
                      │         │
GND ──────────────────┤2 GND    │
                      │         │
SCL ──────┬───────────┤3 SCL    │
          │           │         │
         ┌┴┐          │4 SDA    │
    4.7k │ │          │         │
         └┬┘          │5 XDA    │──NC
          │           │         │
SDA ──────┼──┬────────┤6 XCL    │──NC
          │  │        │         │
         ┌┴┐ │        │7 AD0    │──GND (地址0x68)
    4.7k │ │ │        │         │
         └┬┘ │        │8 INT    │──GPIO (可选)
          │  │        └─────────┘
GND ──────┴──┘

关键要点：
1. SCL和SDA需要上拉电阻（4.7kΩ）
2. 建议使用3.3V供电（更稳定）
3. AD0引脚选择I2C地址
4. INT引脚可用于数据就绪中断
5. 模块通常已集成上拉电阻和稳压器
```


### MPU6050寄存器

**重要寄存器列表**：

```
MPU6050寄存器地址：

配置寄存器：
0x19  SMPLRT_DIV      - 采样率分频器
0x1A  CONFIG          - 配置寄存器（DLPF）
0x1B  GYRO_CONFIG     - 陀螺仪配置
0x1C  ACCEL_CONFIG    - 加速度计配置
0x23  FIFO_EN         - FIFO使能
0x37  INT_PIN_CFG     - 中断引脚配置
0x38  INT_ENABLE      - 中断使能
0x3A  INT_STATUS      - 中断状态
0x6A  USER_CTRL       - 用户控制
0x6B  PWR_MGMT_1      - 电源管理1
0x6C  PWR_MGMT_2      - 电源管理2
0x75  WHO_AM_I        - 设备ID（0x68）

数据寄存器：
0x3B  ACCEL_XOUT_H    - 加速度X高字节
0x3C  ACCEL_XOUT_L    - 加速度X低字节
0x3D  ACCEL_YOUT_H    - 加速度Y高字节
0x3E  ACCEL_YOUT_L    - 加速度Y低字节
0x3F  ACCEL_ZOUT_H    - 加速度Z高字节
0x40  ACCEL_ZOUT_L    - 加速度Z低字节
0x41  TEMP_OUT_H      - 温度高字节
0x42  TEMP_OUT_L      - 温度低字节
0x43  GYRO_XOUT_H     - 陀螺仪X高字节
0x44  GYRO_XOUT_L     - 陀螺仪X低字节
0x45  GYRO_YOUT_H     - 陀螺仪Y高字节
0x46  GYRO_YOUT_L     - 陀螺仪Y低字节
0x47  GYRO_ZOUT_H     - 陀螺仪Z高字节
0x48  GYRO_ZOUT_L     - 陀螺仪Z低字节

配置示例：
PWR_MGMT_1 (0x6B)：
  Bit 7: DEVICE_RESET  - 设备复位
  Bit 6: SLEEP         - 睡眠模式
  Bit 5: CYCLE         - 循环模式
  Bit 3: TEMP_DIS      - 温度传感器禁用
  Bit 2-0: CLKSEL      - 时钟源选择

GYRO_CONFIG (0x1B)：
  Bit 4-3: FS_SEL      - 量程选择
    00: ±250°/s
    01: ±500°/s
    10: ±1000°/s
    11: ±2000°/s

ACCEL_CONFIG (0x1C)：
  Bit 4-3: AFS_SEL     - 量程选择
    00: ±2g
    01: ±4g
    10: ±8g
    11: ±16g
```



## 第三部分：MPU6050驱动开发

### 驱动头文件

```c
/**
 * @file    mpu6050.h
 * @brief   MPU6050六轴传感器驱动
 * @author  嵌入式知识平台
 */

#ifndef __MPU6050_H
#define __MPU6050_H

#include "stm32f1xx_hal.h"
#include <stdbool.h>
#include <math.h>

// MPU6050 I2C地址
#define MPU6050_ADDR        0x68    // AD0接GND
#define MPU6050_ADDR_ALT    0x69    // AD0接VCC

// MPU6050寄存器地址
#define MPU6050_REG_SMPLRT_DIV      0x19
#define MPU6050_REG_CONFIG          0x1A
#define MPU6050_REG_GYRO_CONFIG     0x1B
#define MPU6050_REG_ACCEL_CONFIG    0x1C
#define MPU6050_REG_INT_ENABLE      0x38
#define MPU6050_REG_ACCEL_XOUT_H    0x3B
#define MPU6050_REG_TEMP_OUT_H      0x41
#define MPU6050_REG_GYRO_XOUT_H     0x43
#define MPU6050_REG_PWR_MGMT_1      0x6B
#define MPU6050_REG_WHO_AM_I        0x75

/**
 * @brief  陀螺仪量程
 */
typedef enum {
    MPU6050_GYRO_FS_250  = 0,    // ±250°/s
    MPU6050_GYRO_FS_500  = 1,    // ±500°/s
    MPU6050_GYRO_FS_1000 = 2,    // ±1000°/s
    MPU6050_GYRO_FS_2000 = 3     // ±2000°/s
} MPU6050_GyroFS;

/**
 * @brief  加速度计量程
 */
typedef enum {
    MPU6050_ACCEL_FS_2  = 0,     // ±2g
    MPU6050_ACCEL_FS_4  = 1,     // ±4g
    MPU6050_ACCEL_FS_8  = 2,     // ±8g
    MPU6050_ACCEL_FS_16 = 3      // ±16g
} MPU6050_AccelFS;

/**
 * @brief  原始数据结构
 */
typedef struct {
    int16_t accel_x;    // 加速度X原始值
    int16_t accel_y;    // 加速度Y原始值
    int16_t accel_z;    // 加速度Z原始值
    int16_t temp;       // 温度原始值
    int16_t gyro_x;     // 陀螺仪X原始值
    int16_t gyro_y;     // 陀螺仪Y原始值
    int16_t gyro_z;     // 陀螺仪Z原始值
} MPU6050_RawData;

/**
 * @brief  处理后数据结构
 */
typedef struct {
    float accel_x;      // 加速度X (g)
    float accel_y;      // 加速度Y (g)
    float accel_z;      // 加速度Z (g)
    float temperature;  // 温度 (°C)
    float gyro_x;       // 陀螺仪X (°/s)
    float gyro_y;       // 陀螺仪Y (°/s)
    float gyro_z;       // 陀螺仪Z (°/s)
} MPU6050_Data;

/**
 * @brief  姿态角结构
 */
typedef struct {
    float roll;         // 横滚角 (°)
    float pitch;        // 俯仰角 (°)
    float yaw;          // 偏航角 (°)
} MPU6050_Attitude;

/**
 * @brief  MPU6050配置
 */
typedef struct {
    I2C_HandleTypeDef* hi2c;        // I2C句柄
    uint8_t address;                // I2C地址
    MPU6050_GyroFS gyro_fs;         // 陀螺仪量程
    MPU6050_AccelFS accel_fs;       // 加速度计量程
    float gyro_scale;               // 陀螺仪比例因子
    float accel_scale;              // 加速度计比例因子
} MPU6050_Config;

// 函数声明
bool MPU6050_Init(MPU6050_Config* config);
bool MPU6050_ReadRaw(MPU6050_Config* config, MPU6050_RawData* raw);
bool MPU6050_ReadData(MPU6050_Config* config, MPU6050_Data* data);
void MPU6050_CalculateAttitude(MPU6050_Data* data, MPU6050_Attitude* attitude);
bool MPU6050_Calibrate(MPU6050_Config* config);

#endif /* __MPU6050_H */
```

### 驱动实现

```c
/**
 * @file    mpu6050.c
 * @brief   MPU6050六轴传感器驱动实现
 */

#include "mpu6050.h"

// 私有函数声明
static bool MPU6050_WriteReg(MPU6050_Config* config, uint8_t reg, uint8_t data);
static bool MPU6050_ReadReg(MPU6050_Config* config, uint8_t reg, uint8_t* data);
static bool MPU6050_ReadRegs(MPU6050_Config* config, uint8_t reg, 
                             uint8_t* data, uint16_t length);
static void MPU6050_UpdateScaleFactors(MPU6050_Config* config);

/**
 * @brief  写入寄存器
 */
static bool MPU6050_WriteReg(MPU6050_Config* config, uint8_t reg, uint8_t data) {
    HAL_StatusTypeDef status = HAL_I2C_Mem_Write(
        config->hi2c,
        config->address << 1,
        reg,
        I2C_MEMADD_SIZE_8BIT,
        &data,
        1,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取寄存器
 */
static bool MPU6050_ReadReg(MPU6050_Config* config, uint8_t reg, uint8_t* data) {
    HAL_StatusTypeDef status = HAL_I2C_Mem_Read(
        config->hi2c,
        config->address << 1,
        reg,
        I2C_MEMADD_SIZE_8BIT,
        data,
        1,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  读取多个寄存器
 */
static bool MPU6050_ReadRegs(MPU6050_Config* config, uint8_t reg,
                             uint8_t* data, uint16_t length) {
    HAL_StatusTypeDef status = HAL_I2C_Mem_Read(
        config->hi2c,
        config->address << 1,
        reg,
        I2C_MEMADD_SIZE_8BIT,
        data,
        length,
        HAL_MAX_DELAY
    );
    
    return (status == HAL_OK);
}

/**
 * @brief  更新比例因子
 */
static void MPU6050_UpdateScaleFactors(MPU6050_Config* config) {
    // 陀螺仪比例因子
    switch (config->gyro_fs) {
        case MPU6050_GYRO_FS_250:
            config->gyro_scale = 131.0f;
            break;
        case MPU6050_GYRO_FS_500:
            config->gyro_scale = 65.5f;
            break;
        case MPU6050_GYRO_FS_1000:
            config->gyro_scale = 32.8f;
            break;
        case MPU6050_GYRO_FS_2000:
            config->gyro_scale = 16.4f;
            break;
    }
    
    // 加速度计比例因子
    switch (config->accel_fs) {
        case MPU6050_ACCEL_FS_2:
            config->accel_scale = 16384.0f;
            break;
        case MPU6050_ACCEL_FS_4:
            config->accel_scale = 8192.0f;
            break;
        case MPU6050_ACCEL_FS_8:
            config->accel_scale = 4096.0f;
            break;
        case MPU6050_ACCEL_FS_16:
            config->accel_scale = 2048.0f;
            break;
    }
}

/**
 * @brief  初始化MPU6050
 */
bool MPU6050_Init(MPU6050_Config* config) {
    uint8_t who_am_i;
    
    // 读取WHO_AM_I寄存器验证通信
    if (!MPU6050_ReadReg(config, MPU6050_REG_WHO_AM_I, &who_am_i)) {
        return false;
    }
    
    // 检查设备ID
    if (who_am_i != 0x68) {
        return false;
    }
    
    // 复位设备
    if (!MPU6050_WriteReg(config, MPU6050_REG_PWR_MGMT_1, 0x80)) {
        return false;
    }
    HAL_Delay(100);
    
    // 唤醒设备，选择PLL时钟源
    if (!MPU6050_WriteReg(config, MPU6050_REG_PWR_MGMT_1, 0x01)) {
        return false;
    }
    HAL_Delay(10);
    
    // 配置采样率分频器（1kHz / (1 + 7) = 125Hz）
    if (!MPU6050_WriteReg(config, MPU6050_REG_SMPLRT_DIV, 0x07)) {
        return false;
    }
    
    // 配置数字低通滤波器（DLPF = 3, 带宽44Hz）
    if (!MPU6050_WriteReg(config, MPU6050_REG_CONFIG, 0x03)) {
        return false;
    }
    
    // 配置陀螺仪量程
    if (!MPU6050_WriteReg(config, MPU6050_REG_GYRO_CONFIG, 
                          config->gyro_fs << 3)) {
        return false;
    }
    
    // 配置加速度计量程
    if (!MPU6050_WriteReg(config, MPU6050_REG_ACCEL_CONFIG,
                          config->accel_fs << 3)) {
        return false;
    }
    
    // 更新比例因子
    MPU6050_UpdateScaleFactors(config);
    
    return true;
}

/**
 * @brief  读取原始数据
 */
bool MPU6050_ReadRaw(MPU6050_Config* config, MPU6050_RawData* raw) {
    uint8_t buffer[14];
    
    // 从0x3B开始连续读取14字节
    if (!MPU6050_ReadRegs(config, MPU6050_REG_ACCEL_XOUT_H, buffer, 14)) {
        return false;
    }
    
    // 解析数据（大端序）
    raw->accel_x = (int16_t)((buffer[0] << 8) | buffer[1]);
    raw->accel_y = (int16_t)((buffer[2] << 8) | buffer[3]);
    raw->accel_z = (int16_t)((buffer[4] << 8) | buffer[5]);
    raw->temp     = (int16_t)((buffer[6] << 8) | buffer[7]);
    raw->gyro_x  = (int16_t)((buffer[8] << 8) | buffer[9]);
    raw->gyro_y  = (int16_t)((buffer[10] << 8) | buffer[11]);
    raw->gyro_z  = (int16_t)((buffer[12] << 8) | buffer[13]);
    
    return true;
}

/**
 * @brief  读取处理后的数据
 */
bool MPU6050_ReadData(MPU6050_Config* config, MPU6050_Data* data) {
    MPU6050_RawData raw;
    
    // 读取原始数据
    if (!MPU6050_ReadRaw(config, &raw)) {
        return false;
    }
    
    // 转换加速度数据（单位：g）
    data->accel_x = (float)raw.accel_x / config->accel_scale;
    data->accel_y = (float)raw.accel_y / config->accel_scale;
    data->accel_z = (float)raw.accel_z / config->accel_scale;
    
    // 转换温度数据（单位：°C）
    data->temperature = (float)raw.temp / 340.0f + 36.53f;
    
    // 转换陀螺仪数据（单位：°/s）
    data->gyro_x = (float)raw.gyro_x / config->gyro_scale;
    data->gyro_y = (float)raw.gyro_y / config->gyro_scale;
    data->gyro_z = (float)raw.gyro_z / config->gyro_scale;
    
    return true;
}

/**
 * @brief  计算姿态角（简单方法）
 */
void MPU6050_CalculateAttitude(MPU6050_Data* data, MPU6050_Attitude* attitude) {
    // 使用加速度计计算横滚角和俯仰角
    // Roll (绕X轴旋转)
    attitude->roll = atan2f(data->accel_y, data->accel_z) * 180.0f / M_PI;
    
    // Pitch (绕Y轴旋转)
    attitude->pitch = atan2f(-data->accel_x, 
                            sqrtf(data->accel_y * data->accel_y + 
                                  data->accel_z * data->accel_z)) * 180.0f / M_PI;
    
    // Yaw (绕Z轴旋转) - 需要磁力计或陀螺仪积分
    // 这里暂时设为0，实际应用需要数据融合
    attitude->yaw = 0.0f;
}

/**
 * @brief  校准传感器（静态偏移校准）
 */
bool MPU6050_Calibrate(MPU6050_Config* config) {
    #define CALIBRATION_SAMPLES 100
    
    int32_t accel_x_sum = 0, accel_y_sum = 0, accel_z_sum = 0;
    int32_t gyro_x_sum = 0, gyro_y_sum = 0, gyro_z_sum = 0;
    
    MPU6050_RawData raw;
    
    // 采集多组数据
    for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
        if (!MPU6050_ReadRaw(config, &raw)) {
            return false;
        }
        
        accel_x_sum += raw.accel_x;
        accel_y_sum += raw.accel_y;
        accel_z_sum += raw.accel_z;
        gyro_x_sum += raw.gyro_x;
        gyro_y_sum += raw.gyro_y;
        gyro_z_sum += raw.gyro_z;
        
        HAL_Delay(10);
    }
    
    // 计算平均值（偏移量）
    // 注意：实际应用中需要将这些偏移量存储并在读取时减去
    int16_t accel_x_offset = accel_x_sum / CALIBRATION_SAMPLES;
    int16_t accel_y_offset = accel_y_sum / CALIBRATION_SAMPLES;
    int16_t accel_z_offset = accel_z_sum / CALIBRATION_SAMPLES;
    int16_t gyro_x_offset = gyro_x_sum / CALIBRATION_SAMPLES;
    int16_t gyro_y_offset = gyro_y_sum / CALIBRATION_SAMPLES;
    int16_t gyro_z_offset = gyro_z_sum / CALIBRATION_SAMPLES;
    
    // 打印校准结果
    printf("校准完成:\n");
    printf("  加速度偏移: X=%d, Y=%d, Z=%d\n", 
           accel_x_offset, accel_y_offset, accel_z_offset);
    printf("  陀螺仪偏移: X=%d, Y=%d, Z=%d\n",
           gyro_x_offset, gyro_y_offset, gyro_z_offset);
    
    return true;
}
```


## 第四部分：数据解析与应用

### 使用示例

```c
/**
 * @file    main.c
 * @brief   MPU6050使用示例
 */

#include "stm32f1xx_hal.h"
#include "mpu6050.h"
#include <stdio.h>

// I2C句柄（需要在CubeMX中配置）
extern I2C_HandleTypeDef hi2c1;

// MPU6050配置
MPU6050_Config mpu_config = {
    .hi2c = &hi2c1,
    .address = MPU6050_ADDR,
    .gyro_fs = MPU6050_GYRO_FS_250,      // ±250°/s
    .accel_fs = MPU6050_ACCEL_FS_2       // ±2g
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
    
    printf("MPU6050六轴传感器测试\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 初始化MPU6050
    if (!MPU6050_Init(&mpu_config)) {
        printf("❌ MPU6050初始化失败！\n");
        printf("请检查：\n");
        printf("  1. I2C连接是否正确\n");
        printf("  2. 上拉电阻是否存在\n");
        printf("  3. 传感器地址是否正确\n");
        while (1);
    }
    
    printf("✓ MPU6050初始化成功\n\n");
    
    // 校准传感器
    printf("开始校准（请保持传感器静止）...\n");
    if (MPU6050_Calibrate(&mpu_config)) {
        printf("✓ 校准完成\n\n");
    }
    
    MPU6050_Data data;
    MPU6050_Attitude attitude;
    uint32_t count = 0;
    
    while (1) {
        // 读取传感器数据
        if (MPU6050_ReadData(&mpu_config, &data)) {
            count++;
            
            // 计算姿态角
            MPU6050_CalculateAttitude(&data, &attitude);
            
            // 打印数据
            printf("读取 #%lu:\n", count);
            printf("  加速度: X=%.3fg, Y=%.3fg, Z=%.3fg\n",
                   data.accel_x, data.accel_y, data.accel_z);
            printf("  陀螺仪: X=%.2f°/s, Y=%.2f°/s, Z=%.2f°/s\n",
                   data.gyro_x, data.gyro_y, data.gyro_z);
            printf("  温度: %.2f°C\n", data.temperature);
            printf("  姿态角: Roll=%.2f°, Pitch=%.2f°\n\n",
                   attitude.roll, attitude.pitch);
        } else {
            printf("读取失败 #%lu\n\n", count);
        }
        
        HAL_Delay(100);  // 100ms更新一次
    }
}
```

### 应用场景示例

**场景1：水平检测**

```c
/**
 * @brief  水平检测应用
 */
void application_level_detection(void) {
    MPU6050_Data data;
    MPU6050_Attitude attitude;
    
    const float LEVEL_THRESHOLD = 2.0f;  // 水平阈值（度）
    
    printf("水平检测应用\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            MPU6050_CalculateAttitude(&data, &attitude);
            
            // 检查是否水平
            bool is_level = (fabsf(attitude.roll) < LEVEL_THRESHOLD) &&
                           (fabsf(attitude.pitch) < LEVEL_THRESHOLD);
            
            if (is_level) {
                printf("✓ 设备已水平 (Roll=%.2f°, Pitch=%.2f°)\n",
                       attitude.roll, attitude.pitch);
                // 点亮绿色LED
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
            } else {
                printf("✗ 设备倾斜 (Roll=%.2f°, Pitch=%.2f°)\n",
                       attitude.roll, attitude.pitch);
                // 点亮红色LED
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);
            }
        }
        
        HAL_Delay(100);
    }
}
```

**场景2：跌倒检测**

```c
/**
 * @brief  跌倒检测应用
 */
void application_fall_detection(void) {
    MPU6050_Data data;
    
    const float FALL_THRESHOLD = 2.5f;   // 跌倒阈值（g）
    const float IMPACT_THRESHOLD = 3.0f; // 冲击阈值（g）
    
    printf("跌倒检测应用\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            // 计算加速度幅值
            float accel_magnitude = sqrtf(data.accel_x * data.accel_x +
                                         data.accel_y * data.accel_y +
                                         data.accel_z * data.accel_z);
            
            // 检测自由落体（加速度接近0）
            if (accel_magnitude < 0.5f) {
                printf("⚠ 检测到自由落体！\n");
                
                // 等待冲击
                HAL_Delay(100);
                
                if (MPU6050_ReadData(&mpu_config, &data)) {
                    accel_magnitude = sqrtf(data.accel_x * data.accel_x +
                                           data.accel_y * data.accel_y +
                                           data.accel_z * data.accel_z);
                    
                    // 检测冲击
                    if (accel_magnitude > IMPACT_THRESHOLD) {
                        printf("🚨 跌倒报警！加速度=%.2fg\n", accel_magnitude);
                        // 触发报警
                        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
                        HAL_Delay(5000);  // 报警5秒
                        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
                    }
                }
            }
            
            printf("加速度幅值: %.2fg\n", accel_magnitude);
        }
        
        HAL_Delay(50);  // 50ms检测一次
    }
}
```

**场景3：手势识别**

```c
/**
 * @brief  手势识别应用
 */
void application_gesture_recognition(void) {
    MPU6050_Data data;
    
    const float SHAKE_THRESHOLD = 2.0f;  // 摇晃阈值（g）
    
    printf("手势识别应用\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            // 检测X轴摇晃
            if (fabsf(data.accel_x) > SHAKE_THRESHOLD) {
                printf("👈 检测到左右摇晃\n");
            }
            
            // 检测Y轴摇晃
            if (fabsf(data.accel_y) > SHAKE_THRESHOLD) {
                printf("👆 检测到前后摇晃\n");
            }
            
            // 检测Z轴摇晃
            if (fabsf(data.accel_z - 1.0f) > SHAKE_THRESHOLD) {
                printf("🔼 检测到上下摇晃\n");
            }
            
            // 检测旋转（陀螺仪）
            if (fabsf(data.gyro_z) > 100.0f) {
                if (data.gyro_z > 0) {
                    printf("↻ 检测到顺时针旋转\n");
                } else {
                    printf("↺ 检测到逆时针旋转\n");
                }
            }
        }
        
        HAL_Delay(100);
    }
}
```

**场景4：步数统计**

```c
/**
 * @brief  步数统计应用
 */
void application_step_counter(void) {
    MPU6050_Data data;
    
    const float STEP_THRESHOLD = 1.2f;   // 步伐阈值（g）
    const uint32_t STEP_INTERVAL = 300;  // 最小步伐间隔（ms）
    
    uint32_t step_count = 0;
    uint32_t last_step_time = 0;
    bool step_detected = false;
    
    printf("步数统计应用\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            // 计算垂直加速度幅值
            float vertical_accel = fabsf(data.accel_z - 1.0f);
            
            uint32_t current_time = HAL_GetTick();
            
            // 检测步伐
            if (vertical_accel > STEP_THRESHOLD && !step_detected) {
                // 检查时间间隔
                if (current_time - last_step_time > STEP_INTERVAL) {
                    step_count++;
                    last_step_time = current_time;
                    step_detected = true;
                    
                    printf("👣 步数: %lu\n", step_count);
                }
            }
            
            // 重置检测标志
            if (vertical_accel < STEP_THRESHOLD) {
                step_detected = false;
            }
        }
        
        HAL_Delay(50);  // 50ms检测一次
    }
}
```



## 第五部分：高级应用

### 互补滤波算法

```c
/**
 * @brief  互补滤波器结构
 */
typedef struct {
    float alpha;            // 滤波系数（0-1）
    float roll;             // 横滚角
    float pitch;            // 俯仰角
    float yaw;              // 偏航角
    uint32_t last_time;     // 上次更新时间
} ComplementaryFilter;

/**
 * @brief  初始化互补滤波器
 */
void ComplementaryFilter_Init(ComplementaryFilter* filter, float alpha) {
    filter->alpha = alpha;
    filter->roll = 0.0f;
    filter->pitch = 0.0f;
    filter->yaw = 0.0f;
    filter->last_time = HAL_GetTick();
}

/**
 * @brief  更新互补滤波器
 */
void ComplementaryFilter_Update(ComplementaryFilter* filter, MPU6050_Data* data) {
    // 计算时间间隔（秒）
    uint32_t current_time = HAL_GetTick();
    float dt = (current_time - filter->last_time) / 1000.0f;
    filter->last_time = current_time;
    
    // 使用加速度计计算角度
    float accel_roll = atan2f(data->accel_y, data->accel_z) * 180.0f / M_PI;
    float accel_pitch = atan2f(-data->accel_x,
                               sqrtf(data->accel_y * data->accel_y +
                                     data->accel_z * data->accel_z)) * 180.0f / M_PI;
    
    // 使用陀螺仪积分计算角度变化
    float gyro_roll_delta = data->gyro_x * dt;
    float gyro_pitch_delta = data->gyro_y * dt;
    float gyro_yaw_delta = data->gyro_z * dt;
    
    // 互补滤波：融合加速度计和陀螺仪数据
    // 角度 = α × (角度 + 陀螺仪积分) + (1-α) × 加速度计角度
    filter->roll = filter->alpha * (filter->roll + gyro_roll_delta) +
                   (1.0f - filter->alpha) * accel_roll;
    
    filter->pitch = filter->alpha * (filter->pitch + gyro_pitch_delta) +
                    (1.0f - filter->alpha) * accel_pitch;
    
    // 偏航角只能通过陀螺仪积分（需要磁力计校正）
    filter->yaw += gyro_yaw_delta;
    
    // 限制偏航角范围在-180到180度
    if (filter->yaw > 180.0f) filter->yaw -= 360.0f;
    if (filter->yaw < -180.0f) filter->yaw += 360.0f;
}

/**
 * @brief  互补滤波示例
 */
void example_complementary_filter(void) {
    ComplementaryFilter filter;
    MPU6050_Data data;
    
    // 初始化滤波器（α=0.98，更信任陀螺仪）
    ComplementaryFilter_Init(&filter, 0.98f);
    
    printf("互补滤波姿态估计\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            // 更新滤波器
            ComplementaryFilter_Update(&filter, &data);
            
            // 打印姿态角
            printf("姿态角:\n");
            printf("  Roll:  %.2f°\n", filter.roll);
            printf("  Pitch: %.2f°\n", filter.pitch);
            printf("  Yaw:   %.2f°\n\n", filter.yaw);
        }
        
        HAL_Delay(10);  // 100Hz更新率
    }
}
```

### 数据可视化

```c
/**
 * @brief  数据可视化（通过串口发送到上位机）
 */
void example_data_visualization(void) {
    MPU6050_Data data;
    ComplementaryFilter filter;
    
    ComplementaryFilter_Init(&filter, 0.98f);
    
    printf("数据可视化模式\n");
    printf("═══════════════════════════════════════\n");
    printf("格式: AX,AY,AZ,GX,GY,GZ,Roll,Pitch,Yaw\n\n");
    
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &data)) {
            ComplementaryFilter_Update(&filter, &data);
            
            // 发送CSV格式数据（便于上位机解析）
            printf("%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n",
                   data.accel_x, data.accel_y, data.accel_z,
                   data.gyro_x, data.gyro_y, data.gyro_z,
                   filter.roll, filter.pitch, filter.yaw);
        }
        
        HAL_Delay(20);  // 50Hz更新率
    }
}
```



## 总结

### 关键要点

1. **MEMS原理**：
   - 加速度计测量线性加速度
   - 陀螺仪测量角速度
   - 两者互补，需要数据融合

2. **MPU6050特性**：
   - 六轴传感器（3轴加速度+3轴陀螺仪）
   - I2C接口，易于使用
   - 可配置量程和采样率
   - 内置DMP和FIFO

3. **数据处理**：
   - 原始数据需要比例转换
   - 加速度计可计算倾角
   - 陀螺仪需要积分得到角度
   - 互补滤波融合两者优势

4. **应用场景**：
   - 姿态检测和稳定控制
   - 运动追踪和手势识别
   - 跌倒检测和步数统计
   - 导航定位和惯性测量

### 常见问题

**Q1：为什么加速度计读数不准确？**
- 振动干扰：使用低通滤波
- 未校准：进行零点校准
- 量程不合适：调整量程设置

**Q2：陀螺仪为什么会漂移？**
- 温度影响：进行温度补偿
- 零点偏移：定期校准
- 积分累积误差：使用互补滤波

**Q3：如何提高姿态角精度？**
- 使用互补滤波或卡尔曼滤波
- 增加磁力计（九轴传感器）
- 提高采样率
- 进行传感器校准

**Q4：MPU6050通信失败怎么办？**
- 检查I2C连接和上拉电阻
- 确认I2C地址正确
- 检查电源电压
- 降低I2C速度

### 进阶学习

1. **卡尔曼滤波**：更精确的数据融合算法
2. **DMP使用**：利用MPU6050内置处理器
3. **九轴传感器**：增加磁力计进行航向角校正
4. **四元数**：避免万向节死锁的姿态表示方法

### 参考资料

- MPU6050数据手册
- InvenSense应用笔记
- 《惯性导航原理》
- 开源项目：MultiWii、Betaflight

---

**下一步学习**：
- [传感器数据融合技术](../intermediate/02-sensor-fusion.html)
- [光照与气压传感器应用](03-light-pressure-sensor.html)
- [卡尔曼滤波算法实现](../intermediate/02-sensor-fusion.html)
