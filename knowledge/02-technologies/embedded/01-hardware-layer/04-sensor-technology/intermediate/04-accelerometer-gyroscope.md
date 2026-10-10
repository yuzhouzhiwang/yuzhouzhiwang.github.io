---
title: "加速度计与陀螺仪：原理、驱动与姿态解算"
description: "深入讲解MEMS加速度计和陀螺仪的工作原理、I2C/SPI驱动开发、数据滤波处理，以及互补滤波、Mahony滤波和卡尔曼滤波实现姿态角解算，涵盖DMP、ICM-42688-P、9-DOF磁力计融合与自平衡机器人实战"
slug: "accelerometer-gyroscope-imu-basics"

domain: "底层硬件层"
module: "传感器技术"
content_type: "article"
skill_level: "intermediate"

tags:
  - 加速度计
  - 陀螺仪
  - IMU
  - 姿态解算
  - MEMS传感器
  - MPU6050
  - ICM-42688
  - 四元数
  - Mahony滤波
  - 卡尔曼滤波
prerequisites:
  - "beginner/01-sensor-basics"
  - "beginner/02-i2c-spi-basics"
related_contents:
  - "intermediate/02-sensor-fusion"
  - "intermediate/03-sensor-calibration"
  - "advanced/04-smart-gimbal-project"

estimated_time: 180
difficulty_score: 4

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "2.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: true
is_premium: false

keywords:
  - 加速度计原理
  - 陀螺仪驱动
  - IMU姿态解算
  - MPU6050教程
  - 互补滤波
  - Mahony滤波
  - 四元数姿态
  - Allan方差
  - MEMS噪声
cover_image: ""
---

# 加速度计与陀螺仪：原理、驱动与姿态解算

## 概述

加速度计（Accelerometer）和陀螺仪（Gyroscope）是惯性测量单元（IMU，Inertial Measurement Unit）的核心传感器，广泛应用于可穿戴设备、无人机、机器人和手机姿态检测。现代 MEMS（Micro-Electro-Mechanical Systems，微机电系统）工艺将两者集成在单芯片上（如 MPU6050、ICM-42688），通过 I2C 或 SPI 接口与 MCU 通信。

**学习目标**：

| 目标 | 技能等级 |
|------|---------|
| 理解 MEMS 加速度计和陀螺仪的工作原理与制造工艺 | 理论 |
| 掌握 IMU 误差模型：噪声密度、Allan 方差、零偏不稳定性 | 理论 |
| 编写 MPU6050 的 I2C 驱动，读取原始数据 | 实践 |
| 使用 DMP（数字运动处理器）获取四元数姿态 | 实践 |
| 驱动 ICM-42688-P 高精度 IMU | 实践 |
| 集成 HMC5883L/QMC5883L 磁力计实现 9-DOF 融合 | 实践 |
| 实现 Mahony 滤波器与四元数姿态表示 | 算法 |
| 实现自平衡机器人角度测量与 PID 控制 | 项目 |

**前置知识**：I2C/SPI 通信协议、C 语言指针与结构体、基础线性代数（矩阵乘法）


## 背景知识

### MEMS 传感器制造工艺

MEMS 传感器通过半导体工艺在硅片上制造微米级机械结构，与 CMOS 电路集成在同一芯片上。

**表面微加工工艺（Surface Micromachining）**：

```
工艺流程：
┌─────────────────────────────────────────────────────────┐
│  1. 硅基底（Substrate）                                   │
│     ↓ 沉积牺牲层（SiO₂，约2μm）                          │
│  2. 牺牲层图案化                                          │
│     ↓ 沉积结构层（多晶硅，约2μm）                         │
│  3. 结构层图案化（定义质量块、弹簧、梳齿）                  │
│     ↓ HF腐蚀去除牺牲层（释放结构）                        │
│  4. 悬浮质量块 + 固定梳齿电极                             │
│     ↓ 封装（真空或惰性气体）                              │
│  5. 成品MEMS传感器                                        │
└─────────────────────────────────────────────────────────┘

关键尺寸：
  质量块：100μm × 100μm × 2μm（约50ng）
  弹簧宽度：2~5μm
  梳齿间距：2~4μm（电容约10~100fF）
```

**加速度计结构**：差分电容式，质量块位移改变两侧电容差值：

```
固定电极A    质量块（可动）    固定电极B
   |||    ←弹簧→  |||  ←弹簧→   |||
   |||             |||            |||
   Ca              Cb
   
静止：Ca = Cb
加速时（向右）：质量块向左偏移 → Ca增大，Cb减小
差分输出：ΔC = Ca - Cb ∝ 加速度
```

**陀螺仪结构**：科里奥利效应（Coriolis Effect），振动质量块在旋转时受到垂直力：

```
驱动轴（X）：质量块以固定频率振动（约20kHz）
感测轴（Y）：旋转时科里奥利力使质量块在Y方向偏移

科里奥利力：F_c = 2m × v × Ω
  m：质量块质量
  v：驱动轴速度
  Ω：旋转角速度（待测量）

→ 通过测量Y方向电容变化得到Ω
```

### IMU 噪声模型与 Allan 方差

理解 IMU 噪声对于选型和滤波器设计至关重要。

**噪声密度（Noise Density）**：

噪声密度描述传感器的随机噪声水平，单位：
- 加速度计：μg/√Hz（微重力每根号赫兹）
- 陀螺仪：°/s/√Hz 或 mdps/√Hz

实际噪声 = 噪声密度 × √(带宽)

```
示例：MPU6050 陀螺仪噪声密度 = 0.005 °/s/√Hz
带宽 = 42Hz（低通滤波后）
实际噪声 = 0.005 × √42 ≈ 0.032 °/s (RMS)

ICM-42688-P 陀螺仪噪声密度 = 0.0028 °/s/√Hz（更优）
```

**Allan 方差（Allan Variance）**：

Allan 方差是分析 IMU 长期稳定性的标准方法，通过对不同积分时间τ的输出方差分析，识别不同噪声源：

```
Allan 偏差 σ(τ) 的对数-对数曲线：

σ(τ)
 |  \  量化噪声(Q)    零偏不稳定性(B)
 |   \  斜率-1       /  最低点
 |    \             /
 |     \    角度随机游走(N)
 |      \  斜率-1/2
 |       \________/
 |                 \  速率随机游走(K)
 |                  \ 斜率+1/2
 |                   \
 └──────────────────────── τ（积分时间）

主要噪声类型：
  N（角度随机游走，ARW）：白噪声，τ=1s时的Allan偏差值
  B（零偏不稳定性）：曲线最低点，长期稳定性指标
  K（速率随机游走）：低频漂移
```

**IMU 误差模型**：

```c
// 完整IMU误差模型
typedef struct {
    // 确定性误差（可校准）
    float bias[3];          // 零偏（°/s 或 g）
    float scale_factor[3];  // 比例因子误差（ppm）
    float cross_axis[3][3]; // 轴间耦合误差矩阵

    // 随机误差（统计特性）
    float noise_density;    // 噪声密度（°/s/√Hz）
    float arw;              // 角度随机游走（°/√h）
    float bias_instability; // 零偏不稳定性（°/h）
    float rate_rw;          // 速率随机游走（°/h/√h）

    // 温度相关误差
    float temp_coeff_bias;  // 零偏温度系数（°/s/°C）
    float temp_coeff_scale; // 比例因子温度系数（ppm/°C）
} IMU_ErrorModel;

// 误差补偿（应用校准参数）
void imu_apply_calibration(float raw[3], float corrected[3],
                           const IMU_ErrorModel *model) {
    // 1. 减去零偏
    float debiased[3];
    for (int i = 0; i < 3; i++)
        debiased[i] = raw[i] - model->bias[i];

    // 2. 应用比例因子和轴间耦合校正
    // corrected = (I + diag(sf)) × T × debiased
    // 简化版（忽略轴间耦合）：
    for (int i = 0; i < 3; i++)
        corrected[i] = debiased[i] * (1.0f + model->scale_factor[i] * 1e-6f);
}
```

**主流 IMU 芯片性能对比**：

| 芯片 | 接口 | 加速度量程 | 陀螺仪量程 | 陀螺仪噪声密度 | 零偏不稳定性 | 特点 |
|------|------|-----------|-----------|--------------|------------|------|
| MPU6050 | I2C | ±2~16g | ±250~2000°/s | 0.005°/s/√Hz | 10°/h | 经典入门，内置DMP |
| MPU9250 | I2C/SPI | ±2~16g | ±250~2000°/s | 0.01°/s/√Hz | 10°/h | 9轴，含AK8963磁力计 |
| ICM-42688-P | SPI | ±2~16g | ±15.6~2000°/s | 0.0028°/s/√Hz | 2°/h | 高精度，低噪声，推荐新设计 |
| LSM6DSO | I2C/SPI | ±2~16g | ±125~2000°/s | 0.004°/s/√Hz | 3°/h | ST出品，工业级 |
| BMI088 | SPI | ±3~24g | ±125~2000°/s | 0.014°/s/√Hz | 2°/h | 无人机专用，抗振动 |

### MEMS 传感器原理回顾

**加速度计**：基于电容式 MEMS 结构，内部有一个悬浮质量块。当设备加速时，质量块相对于基底发生位移，改变电容值，从而测量加速度。

```
静止时（重力加速度）：
  Z轴朝上放置 → az = +1g（约9.8 m/s²）
  X轴朝上放置 → ax = +1g
  倒置放置    → az = -1g

运动时：
  测量值 = 重力分量 + 线性加速度分量
  → 需要通过滤波分离两者
```

**陀螺仪**：基于科里奥利效应，内部振动质量块在旋转时受到科里奥利力，通过测量该力得到角速度（单位：°/s 或 rad/s）。

```
特点：
  ✓ 短时间内精度高，响应快
  ✗ 存在零偏漂移（积分后角度误差随时间累积）
  ✗ 无法感知绝对方向（只能测量变化量）
```

**为什么需要融合**：

| 传感器 | 优点 | 缺点 |
|--------|------|------|
| 加速度计 | 长期稳定，可感知绝对姿态（重力方向） | 对振动敏感，动态时误差大 |
| 陀螺仪 | 动态响应快，短期精度高 | 零偏漂移，积分误差累积 |
| 磁力计 | 提供绝对航向（Yaw） | 受磁场干扰，需硬铁/软铁校准 |
| 融合后 | 兼顾动态响应和长期稳定性 | 需要算法处理 |


## 核心内容

### MPU6050 硬件连接

**I2C 接线**（以 STM32F4 为例）：

```
MPU6050        STM32F4
VCC    ──────  3.3V
GND    ──────  GND
SCL    ──────  PB6 (I2C1_SCL)  ← 4.7kΩ上拉至3.3V
SDA    ──────  PB7 (I2C1_SDA)  ← 4.7kΩ上拉至3.3V
INT    ──────  PA0 (EXTI0，数据就绪中断，可选)
AD0    ──────  GND (I2C地址 = 0x68，接VCC则为0x69)
FSYNC  ──────  GND (帧同步，不使用时接GND)

注意：
  - 上拉电阻必须接，否则I2C通信不稳定
  - 走线尽量短，避免与高频信号并行
  - 去耦电容：VCC引脚附近放100nF + 10μF
```

**SPI 接线**（高速模式，适合 ICM-42688-P）：

```
ICM-42688-P    STM32F4
VDD    ──────  3.3V
GND    ──────  GND
SCLK   ──────  PA5 (SPI1_SCK)   最高24MHz
MOSI   ──────  PA7 (SPI1_MOSI)
MISO   ──────  PA6 (SPI1_MISO)
CS     ──────  PA4 (GPIO_OUT)   片选，低有效
INT1   ──────  PB0 (EXTI0)      数据就绪中断
```

**I2C 地址**：AD0 接 GND → `0x68`，接 VCC → `0x69`，同一总线可挂两个 MPU6050。

### MPU6050 寄存器与初始化

关键寄存器：

```c
// MPU6050 寄存器地址（来自官方Register Map文档）
#define MPU6050_ADDR        0x68  // I2C地址（AD0=GND）
#define REG_SELF_TEST_X     0x0D  // 自检寄存器
#define REG_SMPLRT_DIV      0x19  // 采样率分频：采样率 = 陀螺仪输出率/(1+SMPLRT_DIV)
#define REG_CONFIG          0x1A  // DLPF低通滤波配置
#define REG_GYRO_CONFIG     0x1B  // 陀螺仪量程：bit[4:3] 00=±250, 01=±500, 10=±1000, 11=±2000
#define REG_ACCEL_CONFIG    0x1C  // 加速度计量程：bit[4:3] 00=±2g, 01=±4g, 10=±8g, 11=±16g
#define REG_FIFO_EN         0x23  // FIFO使能
#define REG_INT_PIN_CFG     0x37  // 中断引脚配置
#define REG_INT_ENABLE      0x38  // 中断使能
#define REG_INT_STATUS      0x3A  // 中断状态
#define REG_ACCEL_XOUT_H    0x3B  // 加速度计数据起始地址（共6字节）
#define REG_TEMP_OUT_H      0x41  // 温度数据（2字节）
#define REG_GYRO_XOUT_H     0x43  // 陀螺仪数据起始地址（共6字节）
#define REG_USER_CTRL       0x6A  // 用户控制（DMP使能等）
#define REG_PWR_MGMT_1      0x6B  // 电源管理1：bit[6]睡眠, bit[2:0]时钟源
#define REG_PWR_MGMT_2      0x6C  // 电源管理2：各轴使能
#define REG_WHO_AM_I        0x75  // 芯片ID（应返回0x68）

// DLPF配置（REG_CONFIG bit[2:0]）
// 值  | 加速度计带宽 | 陀螺仪带宽 | 延迟
// 0   | 260Hz       | 256Hz     | 0ms
// 1   | 184Hz       | 188Hz     | 2ms
// 2   | 94Hz        | 98Hz      | 3ms
// 3   | 44Hz        | 42Hz      | 4.9ms  ← 推荐通用
// 4   | 21Hz        | 20Hz      | 8.5ms
// 5   | 10Hz        | 10Hz      | 13.8ms
// 6   | 5Hz         | 5Hz       | 19ms
```

**初始化代码**（HAL 库，STM32CubeIDE）：

```c
#include "i2c.h"
#include <string.h>

#define MPU_ADDR  (0x68 << 1)  // HAL库需要左移1位

// 写单个寄存器
static HAL_StatusTypeDef mpu_write(uint8_t reg, uint8_t data) {
    return HAL_I2C_Mem_Write(&hi2c1, MPU_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                             &data, 1, 100);
}

// 读多个寄存器
static HAL_StatusTypeDef mpu_read(uint8_t reg, uint8_t *buf, uint16_t len) {
    return HAL_I2C_Mem_Read(&hi2c1, MPU_ADDR, reg, I2C_MEMADD_SIZE_8BIT,
                            buf, len, 100);
}

// 初始化MPU6050
// 返回：0=成功，-1=通信失败，-2=芯片ID错误
int mpu6050_init(void) {
    uint8_t id;
    HAL_StatusTypeDef ret;

    // 等待上电稳定
    HAL_Delay(100);

    // 验证芯片ID
    ret = mpu_read(REG_WHO_AM_I, &id, 1);
    if (ret != HAL_OK) return -1;
    if (id != 0x68) return -2;

    // 复位所有寄存器
    mpu_write(REG_PWR_MGMT_1, 0x80);  // DEVICE_RESET=1
    HAL_Delay(100);

    // 退出睡眠，使用PLL（陀螺仪X轴）作为时钟源（比内部8MHz更稳定）
    mpu_write(REG_PWR_MGMT_1, 0x01);  // CLKSEL=001
    HAL_Delay(10);

    // 采样率 = 1kHz / (1 + 7) = 125Hz
    mpu_write(REG_SMPLRT_DIV, 0x07);

    // DLPF：截止频率约42Hz（减少高频噪声，适合姿态解算）
    mpu_write(REG_CONFIG, 0x03);

    // 陀螺仪量程：±500°/s（灵敏度65.5 LSB/°/s）
    // 适合一般运动；高速旋转选±2000°/s
    mpu_write(REG_GYRO_CONFIG, 0x08);

    // 加速度计量程：±4g（灵敏度8192 LSB/g）
    mpu_write(REG_ACCEL_CONFIG, 0x08);

    // 使能数据就绪中断（可选）
    mpu_write(REG_INT_PIN_CFG, 0x30);  // INT引脚高电平，读取INT_STATUS清除
    mpu_write(REG_INT_ENABLE, 0x01);   // DATA_RDY_EN=1

    return 0;
}
```

### 读取原始数据

```c
typedef struct {
    float ax, ay, az;   // 加速度 (g)
    float gx, gy, gz;   // 角速度 (°/s)
    float temp;         // 温度 (°C)
} MPU6050_Data;

// 量程对应的灵敏度（LSB per unit）
#define ACCEL_SCALE  8192.0f   // ±4g: 8192 LSB/g
#define GYRO_SCALE   65.5f     // ±500°/s: 65.5 LSB/°/s

int mpu6050_read(MPU6050_Data *data) {
    uint8_t buf[14];

    // 一次性读取14字节：加速度(6) + 温度(2) + 陀螺仪(6)
    if (mpu_read(REG_ACCEL_XOUT_H, buf, 14) != HAL_OK)
        return -1;

    // 合并高低字节（大端序，MSB在前）
    int16_t raw_ax = (int16_t)((buf[0]  << 8) | buf[1]);
    int16_t raw_ay = (int16_t)((buf[2]  << 8) | buf[3]);
    int16_t raw_az = (int16_t)((buf[4]  << 8) | buf[5]);
    int16_t raw_t  = (int16_t)((buf[6]  << 8) | buf[7]);
    int16_t raw_gx = (int16_t)((buf[8]  << 8) | buf[9]);
    int16_t raw_gy = (int16_t)((buf[10] << 8) | buf[11]);
    int16_t raw_gz = (int16_t)((buf[12] << 8) | buf[13]);

    // 转换为物理量
    data->ax   = raw_ax / ACCEL_SCALE;
    data->ay   = raw_ay / ACCEL_SCALE;
    data->az   = raw_az / ACCEL_SCALE;
    data->gx   = raw_gx / GYRO_SCALE;
    data->gy   = raw_gy / GYRO_SCALE;
    data->gz   = raw_gz / GYRO_SCALE;
    data->temp = raw_t / 340.0f + 36.53f;  // 官方公式：Temperature(°C) = TEMP_OUT/340 + 36.53

    return 0;
}
```

### 零偏校准

静止时陀螺仪输出不为零（零偏），需要校准：

```c
typedef struct {
    float gx_offset, gy_offset, gz_offset;
    float ax_offset, ay_offset;  // Z轴不校准（含重力1g）
} MPU6050_Offset;

// 静止放置，采集N次取平均作为零偏
// 注意：校准期间设备必须完全静止，放在水平面上
void mpu6050_calibrate(MPU6050_Offset *offset, int samples) {
    MPU6050_Data data;
    double sum_gx = 0, sum_gy = 0, sum_gz = 0;
    double sum_ax = 0, sum_ay = 0;

    // 丢弃前50次数据（等待传感器稳定）
    for (int i = 0; i < 50; i++) {
        mpu6050_read(&data);
        HAL_Delay(10);
    }

    for (int i = 0; i < samples; i++) {
        mpu6050_read(&data);
        sum_gx += data.gx;
        sum_gy += data.gy;
        sum_gz += data.gz;
        sum_ax += data.ax;
        sum_ay += data.ay;
        HAL_Delay(8);  // 125Hz采样间隔
    }

    offset->gx_offset = (float)(sum_gx / samples);
    offset->gy_offset = (float)(sum_gy / samples);
    offset->gz_offset = (float)(sum_gz / samples);
    offset->ax_offset = (float)(sum_ax / samples);
    offset->ay_offset = (float)(sum_ay / samples);
}

// 读取时减去零偏
void mpu6050_read_calibrated(MPU6050_Data *data, const MPU6050_Offset *offset) {
    mpu6050_read(data);
    data->gx -= offset->gx_offset;
    data->gy -= offset->gy_offset;
    data->gz -= offset->gz_offset;
    data->ax -= offset->ax_offset;
    data->ay -= offset->ay_offset;
}
```

### DMP（数字运动处理器）使用

MPU6050 内置 DMP（Digital Motion Processor，数字运动处理器），可在芯片内部完成四元数姿态解算，减轻 MCU 负担。

**DMP 工作原理**：

```
┌─────────────────────────────────────────────────────┐
│                   MPU6050 内部                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │加速度计   │───▶│  DMP     │───▶│  FIFO Buffer │  │
│  │陀螺仪    │───▶│ (运动处理)│    │  (1024字节)  │  │
│  └──────────┘    └──────────┘    └──────┬───────┘  │
│                                          │           │
└──────────────────────────────────────────┼───────────┘
                                           │ I2C中断
                                           ▼
                                      STM32读取
                                    四元数/欧拉角
```

**使用 I2Cdevlib 库驱动 DMP**（Arduino/ESP32 平台）：

```cpp
// 依赖：I2Cdevlib-MPU6050（Jeff Rowberg）
// 安装：Arduino Library Manager 搜索 "MPU6050"
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"

MPU6050 mpu;

// DMP状态变量
bool dmpReady = false;
uint8_t mpuIntStatus;
uint8_t devStatus;
uint16_t packetSize;
uint16_t fifoCount;
uint8_t fifoBuffer[64];

// 姿态数据
Quaternion q;           // 四元数 [w, x, y, z]
VectorFloat gravity;    // 重力向量
float ypr[3];           // Yaw/Pitch/Roll（弧度）

volatile bool mpuInterrupt = false;
void dmpDataReady() { mpuInterrupt = true; }

void setup() {
    Wire.begin();
    Wire.setClock(400000);  // 400kHz I2C
    Serial.begin(115200);

    mpu.initialize();
    if (!mpu.testConnection()) {
        Serial.println("MPU6050 connection failed");
        while(1);
    }

    // 初始化DMP
    devStatus = mpu.dmpInitialize();

    // 设置陀螺仪零偏（通过校准获得）
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788);

    if (devStatus == 0) {
        mpu.CalibrateAccel(6);  // 自动校准加速度计（6次迭代）
        mpu.CalibrateGyro(6);
        mpu.setDMPEnabled(true);

        // 配置中断
        attachInterrupt(digitalPinToInterrupt(2), dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();
        dmpReady = true;
        packetSize = mpu.dmpGetFIFOPacketSize();
        Serial.println("DMP ready!");
    } else {
        // 错误码：1=初始内存加载失败，2=DMP配置更新失败
        Serial.printf("DMP init failed (code %d)\n", devStatus);
    }
}

void loop() {
    if (!dmpReady) return;
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
        // 获取四元数
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);

        Serial.printf("Yaw: %6.2f  Pitch: %6.2f  Roll: %6.2f\n",
                      ypr[0] * 180.0f / M_PI,
                      ypr[1] * 180.0f / M_PI,
                      ypr[2] * 180.0f / M_PI);
    }
}
```

**DMP 输出的四元数含义**：

```
四元数 q = [w, x, y, z]，满足 w² + x² + y² + z² = 1

转换为欧拉角（ZYX顺序）：
  Roll  (φ) = atan2(2(wy+xz), 1-2(y²+z²))
  Pitch (θ) = arcsin(2(wx-yz))
  Yaw   (ψ) = atan2(2(wz+xy), 1-2(x²+z²))

注意：Yaw角需要磁力计才能获得绝对方向，
      仅用加速度计+陀螺仪的Yaw会随时间漂移
```


### ICM-42688-P 高精度 IMU 驱动

ICM-42688-P 是 TDK InvenSense 的新一代高精度 IMU，噪声性能比 MPU6050 提升约 2 倍，推荐用于新设计。

**ICM-42688-P 关键特性**：
- 陀螺仪噪声密度：0.0028 °/s/√Hz（MPU6050 的 1/2）
- 加速度计噪声密度：70 μg/√Hz
- 支持 SPI（最高 24MHz）和 I2C（最高 1MHz）
- 内置 FIFO（8KB）
- 支持 APEX（高级姿态引擎）：计步、倾斜检测

**SPI 驱动实现**（STM32 HAL）：

```c
// icm42688.h
#ifndef ICM42688_H
#define ICM42688_H

#include "spi.h"

// 寄存器地址（Bank 0）
#define ICM42688_WHO_AM_I       0x75  // 应返回0x47
#define ICM42688_DEVICE_CONFIG  0x11
#define ICM42688_INT_CONFIG     0x14
#define ICM42688_FIFO_CONFIG    0x16
#define ICM42688_TEMP_DATA1     0x1D
#define ICM42688_ACCEL_DATA_X1  0x1F  // 加速度计数据（6字节）
#define ICM42688_GYRO_DATA_X1   0x25  // 陀螺仪数据（6字节）
#define ICM42688_INT_STATUS     0x2D
#define ICM42688_PWR_MGMT0      0x4E
#define ICM42688_GYRO_CONFIG0   0x4F  // 陀螺仪量程和ODR
#define ICM42688_ACCEL_CONFIG0  0x50  // 加速度计量程和ODR
#define ICM42688_GYRO_CONFIG1   0x51
#define ICM42688_ACCEL_CONFIG1  0x53
#define ICM42688_INTF_CONFIG1   0x4D

// 量程配置
#define GYRO_FS_2000DPS   0x00
#define GYRO_FS_1000DPS   0x20
#define GYRO_FS_500DPS    0x40
#define GYRO_FS_250DPS    0x60
#define ACCEL_FS_16G      0x00
#define ACCEL_FS_8G       0x20
#define ACCEL_FS_4G       0x40
#define ACCEL_FS_2G       0x60

// ODR（输出数据率）
#define ODR_1KHZ    0x06
#define ODR_500HZ   0x07
#define ODR_200HZ   0x08

typedef struct {
    float ax, ay, az;  // g
    float gx, gy, gz;  // °/s
    float temp;        // °C
} ICM42688_Data;

int  icm42688_init(void);
int  icm42688_read(ICM42688_Data *data);

#endif

// icm42688.c
#include "icm42688.h"

#define CS_LOW()   HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET)
#define CS_HIGH()  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET)

static uint8_t icm_read_reg(uint8_t reg) {
    uint8_t tx = reg | 0x80;  // 读操作：bit7=1
    uint8_t rx;
    CS_LOW();
    HAL_SPI_Transmit(&hspi1, &tx, 1, 10);
    HAL_SPI_Receive(&hspi1, &rx, 1, 10);
    CS_HIGH();
    return rx;
}

static void icm_write_reg(uint8_t reg, uint8_t data) {
    uint8_t buf[2] = {reg & 0x7F, data};  // 写操作：bit7=0
    CS_LOW();
    HAL_SPI_Transmit(&hspi1, buf, 2, 10);
    CS_HIGH();
}

static void icm_read_regs(uint8_t reg, uint8_t *buf, uint16_t len) {
    uint8_t tx = reg | 0x80;
    CS_LOW();
    HAL_SPI_Transmit(&hspi1, &tx, 1, 10);
    HAL_SPI_Receive(&hspi1, buf, len, 50);
    CS_HIGH();
}

int icm42688_init(void) {
    HAL_Delay(10);

    // 验证芯片ID
    uint8_t id = icm_read_reg(ICM42688_WHO_AM_I);
    if (id != 0x47) return -1;

    // 软复位
    icm_write_reg(ICM42688_DEVICE_CONFIG, 0x01);
    HAL_Delay(10);

    // 配置陀螺仪：±500°/s，1kHz ODR
    icm_write_reg(ICM42688_GYRO_CONFIG0, GYRO_FS_500DPS | ODR_1KHZ);

    // 配置加速度计：±4g，1kHz ODR
    icm_write_reg(ICM42688_ACCEL_CONFIG0, ACCEL_FS_4G | ODR_1KHZ);

    // 使能加速度计和陀螺仪（低噪声模式）
    // bit[3:2]=11: 加速度计低噪声模式
    // bit[1:0]=11: 陀螺仪低噪声模式
    icm_write_reg(ICM42688_PWR_MGMT0, 0x0F);
    HAL_Delay(50);  // 等待传感器稳定

    return 0;
}

int icm42688_read(ICM42688_Data *data) {
    uint8_t buf[12];
    icm_read_regs(ICM42688_ACCEL_DATA_X1, buf, 12);

    // 加速度计（±4g，灵敏度8192 LSB/g）
    int16_t raw_ax = (int16_t)((buf[0] << 8) | buf[1]);
    int16_t raw_ay = (int16_t)((buf[2] << 8) | buf[3]);
    int16_t raw_az = (int16_t)((buf[4] << 8) | buf[5]);

    // 陀螺仪（±500°/s，灵敏度65.5 LSB/°/s）
    int16_t raw_gx = (int16_t)((buf[6]  << 8) | buf[7]);
    int16_t raw_gy = (int16_t)((buf[8]  << 8) | buf[9]);
    int16_t raw_gz = (int16_t)((buf[10] << 8) | buf[11]);

    data->ax = raw_ax / 8192.0f;
    data->ay = raw_ay / 8192.0f;
    data->az = raw_az / 8192.0f;
    data->gx = raw_gx / 65.5f;
    data->gy = raw_gy / 65.5f;
    data->gz = raw_gz / 65.5f;

    // 读取温度
    uint8_t tbuf[2];
    icm_read_regs(ICM42688_TEMP_DATA1, tbuf, 2);
    int16_t raw_t = (int16_t)((tbuf[0] << 8) | tbuf[1]);
    data->temp = raw_t / 132.48f + 25.0f;  // 官方公式

    return 0;
}
```

### 磁力计集成：9-DOF 姿态解算

加入磁力计（Magnetometer）可获得绝对航向角（Yaw），实现完整的 9-DOF（9 自由度）姿态解算。

**HMC5883L / QMC5883L 接线**：

```
HMC5883L       MPU6050（辅助I2C）
VCC    ──────  3.3V
GND    ──────  GND
SCL    ──────  XCL（辅助I2C时钟）
SDA    ──────  XDA（辅助I2C数据）
DRDY   ──────  不连接（可选）

注意：MPU6050可通过辅助I2C总线直接读取磁力计，
      DMP可自动融合磁力计数据输出9轴四元数
```

**QMC5883L 独立驱动**（直接连接到主 I2C 总线）：

```c
// QMC5883L（HMC5883L的国产替代，寄存器不同）
#define QMC5883L_ADDR    0x0D  // I2C地址固定
#define QMC_REG_DATA     0x00  // 数据寄存器（6字节：X_L,X_H,Y_L,Y_H,Z_L,Z_H）
#define QMC_REG_STATUS   0x06  // 状态寄存器
#define QMC_REG_CTRL1    0x09  // 控制寄存器1
#define QMC_REG_CTRL2    0x0A  // 控制寄存器2
#define QMC_REG_SETRESET 0x0B  // SET/RESET周期寄存器

typedef struct {
    float mx, my, mz;  // 磁场强度（μT）
    float heading;     // 航向角（度，0~360）
} Magnetometer_Data;

// 硬铁校准偏移（需要通过旋转校准获得）
static float mag_offset_x = 0, mag_offset_y = 0, mag_offset_z = 0;

int qmc5883l_init(void) {
    // 配置：连续测量模式，200Hz，±8G量程，512过采样
    uint8_t data = 0x1D;  // MODE=01(连续), ODR=11(200Hz), RNG=01(±8G), OSR=00(512)
    HAL_I2C_Mem_Write(&hi2c1, QMC5883L_ADDR << 1, QMC_REG_CTRL1, 1, &data, 1, 100);

    data = 0x40;  // 软复位
    HAL_I2C_Mem_Write(&hi2c1, QMC5883L_ADDR << 1, QMC_REG_CTRL2, 1, &data, 1, 100);

    data = 0x01;  // SET/RESET周期
    HAL_I2C_Mem_Write(&hi2c1, QMC5883L_ADDR << 1, QMC_REG_SETRESET, 1, &data, 1, 100);

    return 0;
}

int qmc5883l_read(Magnetometer_Data *data) {
    uint8_t status;
    HAL_I2C_Mem_Read(&hi2c1, QMC5883L_ADDR << 1, QMC_REG_STATUS, 1, &status, 1, 10);
    if (!(status & 0x01)) return -1;  // 数据未就绪

    uint8_t buf[6];
    HAL_I2C_Mem_Read(&hi2c1, QMC5883L_ADDR << 1, QMC_REG_DATA, 1, buf, 6, 100);

    // QMC5883L：小端序（LSB在前）
    int16_t raw_x = (int16_t)((buf[1] << 8) | buf[0]);
    int16_t raw_y = (int16_t)((buf[3] << 8) | buf[2]);
    int16_t raw_z = (int16_t)((buf[5] << 8) | buf[4]);

    // ±8G量程：灵敏度3000 LSB/Gauss = 300 LSB/μT
    data->mx = (raw_x - mag_offset_x) / 300.0f;
    data->my = (raw_y - mag_offset_y) / 300.0f;
    data->mz = (raw_z - mag_offset_z) / 300.0f;

    // 计算水平面航向角（需要先进行倾斜补偿）
    data->heading = atan2f(data->my, data->mx) * 180.0f / M_PI;
    if (data->heading < 0) data->heading += 360.0f;

    return 0;
}

// 硬铁校准：旋转设备一圈，记录最大最小值
void mag_calibrate_hard_iron(float *offset_x, float *offset_y, float *offset_z) {
    float max_x = -9999, min_x = 9999;
    float max_y = -9999, min_y = 9999;
    float max_z = -9999, min_z = 9999;
    Magnetometer_Data mag;

    printf("Rotate device slowly in all directions for 30 seconds...\n");

    uint32_t start = HAL_GetTick();
    while (HAL_GetTick() - start < 30000) {
        if (qmc5883l_read(&mag) == 0) {
            if (mag.mx > max_x) max_x = mag.mx;
            if (mag.mx < min_x) min_x = mag.mx;
            if (mag.my > max_y) max_y = mag.my;
            if (mag.my < min_y) min_y = mag.my;
            if (mag.mz > max_z) max_z = mag.mz;
            if (mag.mz < min_z) min_z = mag.mz;
        }
        HAL_Delay(10);
    }

    *offset_x = (max_x + min_x) / 2.0f;
    *offset_y = (max_y + min_y) / 2.0f;
    *offset_z = (max_z + min_z) / 2.0f;
    printf("Hard iron offsets: X=%.2f Y=%.2f Z=%.2f\n",
           *offset_x, *offset_y, *offset_z);
}
```


### 姿态解算：互补滤波

互补滤波结合加速度计（低频稳定）和陀螺仪（高频响应快）：

```
姿态角 = α × (上次角度 + 陀螺仪积分) + (1-α) × 加速度计角度

α 接近1：更信任陀螺仪（动态响应好，但长期漂移）
α 接近0：更信任加速度计（长期稳定，但动态噪声大）
典型值：α = 0.98（对应时间常数 τ = α×dt/(1-α) ≈ 0.39s）
```

```c
#include <math.h>

#define ALPHA       0.98f   // 互补滤波系数
#define RAD_TO_DEG  57.295779513f

typedef struct {
    float roll;   // 横滚角（绕X轴，单位：度）
    float pitch;  // 俯仰角（绕Y轴，单位：度）
} Attitude;

// dt: 采样时间间隔（秒），如125Hz采样则dt=0.008
void complementary_filter(Attitude *att, const MPU6050_Data *data, float dt) {
    // 加速度计计算姿态角（静态时准确）
    float acc_roll  = atan2f(data->ay, data->az) * RAD_TO_DEG;
    float acc_pitch = atan2f(-data->ax,
                             sqrtf(data->ay * data->ay + data->az * data->az))
                      * RAD_TO_DEG;

    // 陀螺仪积分（动态时准确，但有漂移）
    float gyro_roll  = att->roll  + data->gx * dt;
    float gyro_pitch = att->pitch + data->gy * dt;

    // 互补融合
    att->roll  = ALPHA * gyro_roll  + (1.0f - ALPHA) * acc_roll;
    att->pitch = ALPHA * gyro_pitch + (1.0f - ALPHA) * acc_pitch;
}
```

### 卡尔曼滤波

互补滤波简单高效，但卡尔曼滤波精度更高，适合对姿态精度要求严格的场景（无人机飞控、机器人）：

```c
// 简化版单轴卡尔曼滤波（Kalman Filter）
typedef struct {
    float angle;    // 估计角度
    float bias;     // 陀螺仪零偏估计
    float P[2][2];  // 误差协方差矩阵
} KalmanState;

// 噪声参数（需根据实际传感器调整）
#define Q_ANGLE   0.001f   // 过程噪声：角度
#define Q_BIAS    0.003f   // 过程噪声：零偏
#define R_MEASURE 0.03f    // 测量噪声

float kalman_update(KalmanState *kf, float new_angle, float new_rate, float dt) {
    // 预测步骤
    float rate = new_rate - kf->bias;
    kf->angle += dt * rate;

    kf->P[0][0] += dt * (dt * kf->P[1][1] - kf->P[0][1] - kf->P[1][0] + Q_ANGLE);
    kf->P[0][1] -= dt * kf->P[1][1];
    kf->P[1][0] -= dt * kf->P[1][1];
    kf->P[1][1] += Q_BIAS * dt;

    // 更新步骤
    float S = kf->P[0][0] + R_MEASURE;
    float K[2] = { kf->P[0][0] / S, kf->P[1][0] / S };

    float y = new_angle - kf->angle;
    kf->angle += K[0] * y;
    kf->bias  += K[1] * y;

    float P00_temp = kf->P[0][0];
    float P01_temp = kf->P[0][1];
    kf->P[0][0] -= K[0] * P00_temp;
    kf->P[0][1] -= K[0] * P01_temp;
    kf->P[1][0] -= K[1] * P00_temp;
    kf->P[1][1] -= K[1] * P01_temp;

    return kf->angle;
}
```

## 深入原理

### 四元数姿态表示

欧拉角（Roll/Pitch/Yaw）直观但存在万向节死锁（Gimbal Lock）问题；四元数（Quaternion）是更稳健的姿态表示方式。

**四元数基础**：

```
四元数：q = w + xi + yj + zk
  w：标量部分（实部）
  x, y, z：向量部分（虚部）
  约束：w² + x² + y² + z² = 1（单位四元数）

几何意义：绕单位轴 n̂ = (nx, ny, nz) 旋转角度 θ：
  w = cos(θ/2)
  x = nx × sin(θ/2)
  y = ny × sin(θ/2)
  z = nz × sin(θ/2)

四元数乘法（非交换）：
  q1 ⊗ q2 = [w1w2 - x1x2 - y1y2 - z1z2,
              w1x2 + x1w2 + y1z2 - z1y2,
              w1y2 - x1z2 + y1w2 + z1x2,
              w1z2 + x1y2 - y1x2 + z1w2]

共轭（逆旋转）：q* = [w, -x, -y, -z]
```

**四元数与旋转矩阵的转换**：

```c
// 四元数转旋转矩阵（3×3）
void quat_to_rotation_matrix(float q[4], float R[3][3]) {
    float w = q[0], x = q[1], y = q[2], z = q[3];

    R[0][0] = 1 - 2*(y*y + z*z);
    R[0][1] = 2*(x*y - w*z);
    R[0][2] = 2*(x*z + w*y);

    R[1][0] = 2*(x*y + w*z);
    R[1][1] = 1 - 2*(x*x + z*z);
    R[1][2] = 2*(y*z - w*x);

    R[2][0] = 2*(x*z - w*y);
    R[2][1] = 2*(y*z + w*x);
    R[2][2] = 1 - 2*(x*x + y*y);
}

// 四元数转欧拉角（ZYX顺序，单位：弧度）
void quat_to_euler(float q[4], float *roll, float *pitch, float *yaw) {
    float w = q[0], x = q[1], y = q[2], z = q[3];

    // Roll (x-axis rotation)
    float sinr_cosp = 2.0f * (w*x + y*z);
    float cosr_cosp = 1.0f - 2.0f * (x*x + y*y);
    *roll = atan2f(sinr_cosp, cosr_cosp);

    // Pitch (y-axis rotation)
    float sinp = 2.0f * (w*y - z*x);
    if (fabsf(sinp) >= 1.0f)
        *pitch = copysignf(M_PI / 2.0f, sinp);  // 万向节死锁处理
    else
        *pitch = asinf(sinp);

    // Yaw (z-axis rotation)
    float siny_cosp = 2.0f * (w*z + x*y);
    float cosy_cosp = 1.0f - 2.0f * (y*y + z*z);
    *yaw = atan2f(siny_cosp, cosy_cosp);
}
```

**万向节死锁（Gimbal Lock）说明**：

```
欧拉角的问题：当Pitch = ±90°时，Roll和Yaw轴重合，
丢失一个自由度，无法区分绕这两个轴的旋转。

四元数的优势：
  ✓ 无万向节死锁
  ✓ 插值平滑（SLERP球面线性插值）
  ✓ 计算效率高（乘法代替三角函数）
  ✗ 不直观，需要转换才能理解

适用场景：
  欧拉角：显示给用户、简单姿态控制
  四元数：内部计算、飞控、机器人运动学
```

### Mahony 滤波器实现

Mahony 滤波器（2008年，Robert Mahony 提出）是一种基于互补滤波思想的四元数姿态估计算法，计算量小，适合嵌入式系统。

**算法原理**：

```
核心思想：
1. 用陀螺仪积分更新四元数（预测步骤）
2. 用加速度计（和磁力计）计算误差向量
3. 用PI控制器修正陀螺仪零偏

误差计算：
  v = q ⊗ [0,0,0,1] ⊗ q*  （将重力向量从世界系转到机体系）
  e = a × v                  （叉积得到误差向量）
  
  其中 a 是归一化加速度计测量值
       v 是估计的重力方向

PI修正：
  integral += Ki × e × dt
  gyro_corrected = gyro + Kp × e + integral
  
四元数更新：
  q̇ = 0.5 × q ⊗ [0, gx, gy, gz]
  q += q̇ × dt
  归一化 q
```

**完整 Mahony 滤波器实现**（6-DOF，仅加速度计+陀螺仪）：

```c
// mahony_filter.h / mahony_filter.c
// 参考：Mahony, R. et al., IEEE TAC 2008

#include <math.h>

// 滤波器参数（需根据传感器特性调整）
#define MAHONY_KP  2.0f   // 比例增益（越大收敛越快，但噪声越大）
#define MAHONY_KI  0.005f // 积分增益（补偿陀螺仪零偏）

typedef struct {
    float q[4];           // 四元数 [w, x, y, z]
    float integral[3];    // 积分误差 [ix, iy, iz]
} MahonyFilter;

// 初始化（假设初始姿态水平）
void mahony_init(MahonyFilter *f) {
    f->q[0] = 1.0f; f->q[1] = 0.0f;
    f->q[2] = 0.0f; f->q[3] = 0.0f;
    f->integral[0] = f->integral[1] = f->integral[2] = 0.0f;
}

// 更新（6-DOF：仅加速度计+陀螺仪）
// gx,gy,gz: 陀螺仪（rad/s）
// ax,ay,az: 加速度计（任意单位，会被归一化）
// dt: 时间步长（秒）
void mahony_update(MahonyFilter *f,
                   float gx, float gy, float gz,
                   float ax, float ay, float az,
                   float dt) {
    float q0 = f->q[0], q1 = f->q[1], q2 = f->q[2], q3 = f->q[3];
    float recipNorm;
    float vx, vy, vz;
    float ex, ey, ez;

    // 归一化加速度计（如果模长为0则跳过）
    float norm = sqrtf(ax*ax + ay*ay + az*az);
    if (norm < 1e-6f) goto integrate;
    recipNorm = 1.0f / norm;
    ax *= recipNorm; ay *= recipNorm; az *= recipNorm;

    // 将重力向量从世界系（[0,0,1]）旋转到机体系
    // v = q* ⊗ [0,0,1] ⊗ q（简化计算）
    vx = 2.0f * (q1*q3 - q0*q2);
    vy = 2.0f * (q0*q1 + q2*q3);
    vz = q0*q0 - q1*q1 - q2*q2 + q3*q3;

    // 误差 = 测量重力 × 估计重力（叉积）
    ex = ay*vz - az*vy;
    ey = az*vx - ax*vz;
    ez = ax*vy - ay*vx;

    // PI积分修正
    f->integral[0] += MAHONY_KI * ex * dt;
    f->integral[1] += MAHONY_KI * ey * dt;
    f->integral[2] += MAHONY_KI * ez * dt;

    gx += MAHONY_KP * ex + f->integral[0];
    gy += MAHONY_KP * ey + f->integral[1];
    gz += MAHONY_KP * ez + f->integral[2];

integrate:
    // 四元数微分方程积分
    // q̇ = 0.5 × q ⊗ ω_quat
    float dq0 = 0.5f * (-q1*gx - q2*gy - q3*gz);
    float dq1 = 0.5f * ( q0*gx + q2*gz - q3*gy);
    float dq2 = 0.5f * ( q0*gy - q1*gz + q3*gx);
    float dq3 = 0.5f * ( q0*gz + q1*gy - q2*gx);

    q0 += dq0 * dt; q1 += dq1 * dt;
    q2 += dq2 * dt; q3 += dq3 * dt;

    // 归一化四元数（防止数值漂移）
    recipNorm = 1.0f / sqrtf(q0*q0 + q1*q1 + q2*q2 + q3*q3);
    f->q[0] = q0 * recipNorm; f->q[1] = q1 * recipNorm;
    f->q[2] = q2 * recipNorm; f->q[3] = q3 * recipNorm;
}

// 9-DOF版本（加入磁力计修正Yaw）
void mahony_update_9dof(MahonyFilter *f,
                        float gx, float gy, float gz,
                        float ax, float ay, float az,
                        float mx, float my, float mz,
                        float dt) {
    float q0 = f->q[0], q1 = f->q[1], q2 = f->q[2], q3 = f->q[3];
    float recipNorm;
    float hx, hy, bx, bz;
    float vx, vy, vz, wx, wy, wz;
    float ex, ey, ez;

    // 归一化加速度计
    float norm = sqrtf(ax*ax + ay*ay + az*az);
    if (norm < 1e-6f) return;
    recipNorm = 1.0f / norm;
    ax *= recipNorm; ay *= recipNorm; az *= recipNorm;

    // 归一化磁力计
    norm = sqrtf(mx*mx + my*my + mz*mz);
    if (norm < 1e-6f) {
        // 磁力计无效，退化为6-DOF
        mahony_update(f, gx, gy, gz, ax, ay, az, dt);
        return;
    }
    recipNorm = 1.0f / norm;
    mx *= recipNorm; my *= recipNorm; mz *= recipNorm;

    // 将磁力计测量值旋转到世界系，提取水平分量
    hx = 2.0f * (mx*(0.5f - q2*q2 - q3*q3) + my*(q1*q2 - q0*q3) + mz*(q1*q3 + q0*q2));
    hy = 2.0f * (mx*(q1*q2 + q0*q3) + my*(0.5f - q1*q1 - q3*q3) + mz*(q2*q3 - q0*q1));
    bx = sqrtf(hx*hx + hy*hy);  // 水平磁场强度
    bz = 2.0f * (mx*(q1*q3 - q0*q2) + my*(q2*q3 + q0*q1) + mz*(0.5f - q1*q1 - q2*q2));

    // 估计重力和磁场方向（机体系）
    vx = 2.0f * (q1*q3 - q0*q2);
    vy = 2.0f * (q0*q1 + q2*q3);
    vz = q0*q0 - q1*q1 - q2*q2 + q3*q3;

    wx = 2.0f * (bx*(0.5f - q2*q2 - q3*q3) + bz*(q1*q3 - q0*q2));
    wy = 2.0f * (bx*(q1*q2 - q0*q3) + bz*(q0*q1 + q2*q3));
    wz = 2.0f * (bx*(q0*q2 + q1*q3) + bz*(0.5f - q1*q1 - q2*q2));

    // 误差（加速度计 + 磁力计）
    ex = (ay*vz - az*vy) + (my*wz - mz*wy);
    ey = (az*vx - ax*vz) + (mz*wx - mx*wz);
    ez = (ax*vy - ay*vx) + (mx*wy - my*wx);

    // PI修正
    f->integral[0] += MAHONY_KI * ex * dt;
    f->integral[1] += MAHONY_KI * ey * dt;
    f->integral[2] += MAHONY_KI * ez * dt;

    gx += MAHONY_KP * ex + f->integral[0];
    gy += MAHONY_KP * ey + f->integral[1];
    gz += MAHONY_KP * ez + f->integral[2];

    // 四元数积分
    float dq0 = 0.5f * (-q1*gx - q2*gy - q3*gz);
    float dq1 = 0.5f * ( q0*gx + q2*gz - q3*gy);
    float dq2 = 0.5f * ( q0*gy - q1*gz + q3*gx);
    float dq3 = 0.5f * ( q0*gz + q1*gy - q2*gx);

    q0 += dq0 * dt; q1 += dq1 * dt;
    q2 += dq2 * dt; q3 += dq3 * dt;

    recipNorm = 1.0f / sqrtf(q0*q0 + q1*q1 + q2*q2 + q3*q3);
    f->q[0] = q0 * recipNorm; f->q[1] = q1 * recipNorm;
    f->q[2] = q2 * recipNorm; f->q[3] = q3 * recipNorm;
}
```

**滤波器性能对比**：

| 特性 | 互补滤波 | 卡尔曼滤波 | Mahony滤波 | Madgwick滤波 |
|------|---------|-----------|-----------|-------------|
| 实现复杂度 | 简单 | 中等 | 中等 | 中等 |
| 计算量（Cortex-M4） | ~5μs | ~20μs | ~15μs | ~12μs |
| 精度（静态） | ±1° | ±0.5° | ±0.5° | ±0.5° |
| 精度（动态） | ±3° | ±1° | ±1.5° | ±1° |
| 磁力计支持 | 需扩展 | 需扩展 | 内置 | 内置 |
| 参数调整 | 1个(α) | 3个 | 2个(Kp,Ki) | 1个(β) |
| 适用场景 | 入门 | 高精度 | 飞控/机器人 | 飞控/机器人 |

### GPS 辅助惯性导航（Dead Reckoning）

将 IMU 与 GPS 融合，可在 GPS 信号丢失时通过惯性导航（Dead Reckoning，航位推算）继续定位。

**系统架构**：

```
┌──────────┐    ┌──────────────────────────────────────┐
│  GPS     │───▶│           扩展卡尔曼滤波（EKF）        │
│ (1~10Hz) │    │                                      │
└──────────┘    │  状态向量：[位置(3), 速度(3),          │
                │            姿态四元数(4), 零偏(6)]    │
┌──────────┐    │                                      │
│  IMU     │───▶│  预测：IMU积分（高频，100~1000Hz）     │
│(100~1kHz)│    │  更新：GPS测量（低频，1~10Hz）         │
└──────────┘    └──────────────────────────────────────┘
                              │
                              ▼
                    位置/速度/姿态估计
```

**简化的 IMU 积分（位置推算）**：

```c
typedef struct {
    float pos[3];   // 位置 (m)，NED坐标系
    float vel[3];   // 速度 (m/s)
    float att[4];   // 姿态四元数
} NavState;

// 将机体系加速度转换到导航系（NED）并积分
void nav_propagate(NavState *state, const float accel_body[3],
                   const float gyro[3], float dt) {
    float R[3][3];
    quat_to_rotation_matrix(state->att, R);

    // 机体系加速度 → 导航系
    float accel_nav[3];
    for (int i = 0; i < 3; i++) {
        accel_nav[i] = R[i][0]*accel_body[0]
                     + R[i][1]*accel_body[1]
                     + R[i][2]*accel_body[2];
    }

    // 减去重力（NED系中重力在Z轴正方向）
    accel_nav[2] -= 9.81f;

    // 速度积分
    for (int i = 0; i < 3; i++)
        state->vel[i] += accel_nav[i] * dt;

    // 位置积分
    for (int i = 0; i < 3; i++)
        state->pos[i] += state->vel[i] * dt;

    // 姿态更新（使用Mahony或四元数积分）
    // ... (同前述mahony_update)
}
```

**注意**：纯 IMU 积分的位置误差随时间平方增长（加速度计零偏 0.01g → 1分钟后位置误差约 18m），必须定期用 GPS 修正。


## 完整项目实战：自平衡机器人

### 项目概述

自平衡机器人（Two-Wheel Self-Balancing Robot）是 IMU 姿态解算的经典应用，通过 MPU6050 实时测量倾斜角，PID 控制器驱动电机保持平衡。

**系统架构**：

```
┌─────────────────────────────────────────────────────────┐
│                    自平衡机器人系统                        │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ MPU6050  │───▶│ 互补滤波 │───▶│   PID控制器      │  │
│  │ (I2C)   │    │ 姿态解算 │    │  (角度+角速度)   │  │
│  └──────────┘    └──────────┘    └────────┬─────────┘  │
│                                           │             │
│  ┌──────────┐                    ┌────────▼─────────┐  │
│  │ 编码器   │───▶ 速度反馈 ──────▶│   速度PID        │  │
│  └──────────┘                    └────────┬─────────┘  │
│                                           │             │
│                                  ┌────────▼─────────┐  │
│                                  │  L298N/TB6612    │  │
│                                  │  电机驱动        │  │
│                                  └────────┬─────────┘  │
│                                           │             │
│                                  ┌────────▼─────────┐  │
│                                  │  直流减速电机     │  │
│                                  │  (左右各一个)    │  │
│                                  └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**物料清单（BOM）**：

| 序号 | 元件 | 型号/规格 | 数量 | 参考价格 |
|------|------|---------|------|---------|
| 1 | 主控MCU | STM32F103C8T6（蓝色小板） | 1 | ¥15 |
| 2 | IMU传感器 | MPU6050模块 | 1 | ¥8 |
| 3 | 电机驱动 | TB6612FNG模块 | 1 | ¥12 |
| 4 | 直流减速电机 | 带编码器，6V，1:30减速比 | 2 | ¥25×2 |
| 5 | 车轮 | 65mm橡胶轮 | 2 | ¥8×2 |
| 6 | 锂电池 | 7.4V 2000mAh（2S） | 1 | ¥35 |
| 7 | 降压模块 | MP1584（5V/3A） | 1 | ¥5 |
| 8 | 亚克力底板 | 激光切割，150×100mm | 1 | ¥20 |

### 硬件连接

```
STM32F103C8T6 引脚分配：

MPU6050：
  PB6 → SCL（I2C1）
  PB7 → SDA（I2C1）
  PA0 → INT（数据就绪中断）

TB6612FNG（左电机）：
  PA8  → PWMA（TIM1_CH1，PWM输出）
  PB12 → AIN1（方向控制）
  PB13 → AIN2（方向控制）

TB6612FNG（右电机）：
  PA9  → PWMB（TIM1_CH2，PWM输出）
  PB14 → BIN1（方向控制）
  PB15 → BIN2（方向控制）

编码器（左）：
  PA6 → TIM3_CH1（编码器A相）
  PA7 → TIM3_CH2（编码器B相）

编码器（右）：
  PB6 → TIM4_CH1（编码器A相）
  PB7 → TIM4_CH2（编码器B相）

注意：编码器引脚与I2C冲突，实际使用时需重新分配
      建议：I2C使用PB10/PB11（I2C2），编码器使用TIM3/TIM4
```

### 完整代码实现

**PID 控制器**：

```c
// pid.h
typedef struct {
    float kp, ki, kd;       // PID参数
    float setpoint;          // 目标值
    float integral;          // 积分项
    float prev_error;        // 上次误差（用于微分）
    float integral_limit;    // 积分限幅（防止积分饱和）
    float output_limit;      // 输出限幅
} PID_Controller;

void pid_init(PID_Controller *pid, float kp, float ki, float kd,
              float integral_limit, float output_limit) {
    pid->kp = kp; pid->ki = ki; pid->kd = kd;
    pid->setpoint = 0;
    pid->integral = 0;
    pid->prev_error = 0;
    pid->integral_limit = integral_limit;
    pid->output_limit = output_limit;
}

float pid_update(PID_Controller *pid, float measured, float dt) {
    float error = pid->setpoint - measured;

    // 积分（带限幅）
    pid->integral += error * dt;
    if (pid->integral >  pid->integral_limit) pid->integral =  pid->integral_limit;
    if (pid->integral < -pid->integral_limit) pid->integral = -pid->integral_limit;

    // 微分（使用测量值微分，避免设定值突变引起的微分冲击）
    float derivative = (error - pid->prev_error) / dt;
    pid->prev_error = error;

    float output = pid->kp * error + pid->ki * pid->integral + pid->kd * derivative;

    // 输出限幅
    if (output >  pid->output_limit) output =  pid->output_limit;
    if (output < -pid->output_limit) output = -pid->output_limit;

    return output;
}

void pid_reset(PID_Controller *pid) {
    pid->integral = 0;
    pid->prev_error = 0;
}
```

**电机驱动**：

```c
// motor.h / motor.c
#include "tim.h"

#define PWM_MAX  1000  // PWM最大值（对应100%占空比）

// 设置左电机速度（-1000 ~ +1000）
void motor_left_set(int16_t speed) {
    if (speed > 0) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_SET);   // AIN1=1
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); // AIN2=0
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, speed);
    } else if (speed < 0) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET); // AIN1=0
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET);   // AIN2=1
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, -speed);
    } else {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
    }
}

// 设置右电机速度（-1000 ~ +1000）
void motor_right_set(int16_t speed) {
    if (speed > 0) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_SET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_RESET);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, speed);
    } else if (speed < 0) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_SET);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, -speed);
    } else {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_RESET);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
    }
}
```

**主控制循环**：

```c
// main_balance.c
#include "mpu6050.h"
#include "pid.h"
#include "motor.h"
#include "encoder.h"

// PID参数（需要根据实际机器人调整）
// 角度环：快速响应倾斜
#define ANGLE_KP  25.0f
#define ANGLE_KI  0.5f
#define ANGLE_KD  0.8f

// 速度环：防止机器人前后漂移
#define SPEED_KP  0.5f
#define SPEED_KI  0.3f
#define SPEED_KD  0.0f

// 机械零点（MPU6050安装角度偏差，需校准）
#define BALANCE_ANGLE  0.0f  // 单位：度，正值表示前倾

#define CONTROL_DT  0.005f   // 控制周期：5ms（200Hz）
#define FALL_ANGLE  45.0f    // 超过此角度认为已倒下，停止电机

PID_Controller angle_pid;
PID_Controller speed_pid;
MPU6050_Data   imu_data;
MPU6050_Offset imu_offset;
Attitude       attitude;

void balance_robot_init(void) {
    // 初始化IMU
    if (mpu6050_init() != 0) {
        Error_Handler();
    }
    mpu6050_calibrate(&imu_offset, 500);

    // 初始化PID
    pid_init(&angle_pid, ANGLE_KP, ANGLE_KI, ANGLE_KD, 200.0f, 1000.0f);
    pid_init(&speed_pid, SPEED_KP, SPEED_KI, SPEED_KD, 100.0f, 200.0f);

    // 设定目标：直立（0度）
    angle_pid.setpoint = BALANCE_ANGLE;
    speed_pid.setpoint = 0;  // 目标速度：静止

    // 启动PWM
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);

    // 启动编码器
    HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
    HAL_TIM_Encoder_Start(&htim4, TIM_CHANNEL_ALL);
}

// 控制定时器中断（200Hz）
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance != TIM2) return;  // 仅处理控制定时器

    // 1. 读取IMU数据
    mpu6050_read_calibrated(&imu_data, &imu_offset);

    // 2. 姿态解算（互补滤波）
    complementary_filter(&attitude, &imu_data, CONTROL_DT);

    // 3. 倒下检测
    if (fabsf(attitude.pitch) > FALL_ANGLE) {
        motor_left_set(0);
        motor_right_set(0);
        pid_reset(&angle_pid);
        pid_reset(&speed_pid);
        return;
    }

    // 4. 读取编码器速度（脉冲/控制周期）
    int16_t enc_left  = encoder_read_left();
    int16_t enc_right = encoder_read_right();
    float speed = (enc_left + enc_right) / 2.0f;  // 平均速度

    // 5. 速度环（外环）：输出角度修正量
    float angle_correction = pid_update(&speed_pid, speed, CONTROL_DT);

    // 6. 角度环（内环）：输出电机PWM
    angle_pid.setpoint = BALANCE_ANGLE + angle_correction;
    float motor_output = pid_update(&angle_pid, attitude.pitch, CONTROL_DT);

    // 7. 驱动电机
    int16_t pwm = (int16_t)motor_output;
    motor_left_set(pwm);
    motor_right_set(pwm);
}
```

### PID 参数调整方法

```
调参步骤（串级PID）：

第一步：关闭速度环（speed_pid.kp=ki=kd=0），只调角度环
  1. 先将 Kd=0，Ki=0，逐渐增大 Kp 直到机器人能短暂平衡但有振荡
  2. 增大 Kd 减小振荡（通常 Kd ≈ Kp/30）
  3. 少量增加 Ki 消除稳态误差（Ki 过大会导致积分饱和）

第二步：调整速度环
  1. 角度环调好后，机器人能平衡但会前后漂移
  2. 增大速度环 Kp 减小漂移
  3. 增大速度环 Ki 消除长期漂移

典型参数范围（仅供参考，需根据实际调整）：
  角度环：Kp=20~40, Ki=0~2, Kd=0.5~2
  速度环：Kp=0.3~1, Ki=0.1~0.5, Kd=0

调试工具：
  - 串口输出 attitude.pitch 和 motor_output，用 Serial Studio 绘图
  - 观察阶跃响应：手推机器人后能否快速恢复平衡
```

### 测试与验证

```c
// 验证IMU数据质量
void test_imu_quality(void) {
    MPU6050_Data data;
    float sum_gz = 0;
    int N = 1000;

    // 静止1秒，测量陀螺仪噪声
    for (int i = 0; i < N; i++) {
        mpu6050_read(&data);
        sum_gz += data.gz * data.gz;  // 方差
        HAL_Delay(1);
    }
    float rms_gz = sqrtf(sum_gz / N);
    printf("Gyro Z RMS noise: %.4f °/s\n", rms_gz);
    // 期望值：< 0.05 °/s（MPU6050典型值）

    // 验证加速度计静态精度
    Attitude att = {0, 0};
    for (int i = 0; i < N; i++) {
        mpu6050_read(&data);
        complementary_filter(&att, &data, 0.001f);
        HAL_Delay(1);
    }
    printf("Static angle: Roll=%.2f° Pitch=%.2f°\n", att.roll, att.pitch);
    // 期望值：水平放置时 |Roll| < 1°, |Pitch| < 1°
}
```


## 性能调优

### 降低噪声的硬件措施

```
PCB布局建议：
┌─────────────────────────────────────────────────────────┐
│  1. 去耦电容：VCC引脚旁放100nF（0402）+ 10μF（0805）    │
│  2. 地平面：MPU6050下方铺完整地平面，减少地弹噪声        │
│  3. 走线：I2C走线尽量短（<5cm），避免与PWM信号并行       │
│  4. 安装位置：远离电机、开关电源等振动/电磁干扰源        │
│  5. 机械隔振：使用硅胶减振垫安装IMU（无人机必须）        │
└─────────────────────────────────────────────────────────┘
```

### 软件滤波优化

```c
// 一阶低通滤波（IIR滤波器）
// 截止频率 fc = 1/(2π×τ)，τ = RC时间常数
// 离散化：y[n] = α×y[n-1] + (1-α)×x[n]
// α = τ/(τ+dt)

typedef struct {
    float alpha;
    float prev_output;
} LowPassFilter;

void lpf_init(LowPassFilter *f, float cutoff_hz, float sample_hz) {
    float tau = 1.0f / (2.0f * M_PI * cutoff_hz);
    float dt = 1.0f / sample_hz;
    f->alpha = tau / (tau + dt);
    f->prev_output = 0;
}

float lpf_update(LowPassFilter *f, float input) {
    f->prev_output = f->alpha * f->prev_output + (1.0f - f->alpha) * input;
    return f->prev_output;
}

// 使用示例：对加速度计数据进行20Hz低通滤波
LowPassFilter ax_filter, ay_filter, az_filter;
lpf_init(&ax_filter, 20.0f, 125.0f);  // 截止20Hz，采样125Hz
```

### 采样率与精度权衡

```
采样率选择指南：

应用场景          推荐采样率    DLPF设置    说明
─────────────────────────────────────────────────────
自平衡机器人      200~500Hz    42Hz带宽    需要快速响应
无人机飞控        500~1000Hz   98Hz带宽    极快响应
手势识别          50~100Hz     20Hz带宽    低功耗优先
计步器            10~50Hz      5Hz带宽     超低功耗
姿态显示          50~100Hz     42Hz带宽    平滑显示

注意：采样率越高，CPU占用越大，但噪声也越大（带宽更宽）
      DLPF截止频率应设为采样率的1/5~1/10
```

## 常见问题与调试

### I2C 通信故障

**问题1：WHO_AM_I 返回 0xFF 或 0x00**

```
原因分析：
  ├── 上拉电阻缺失或阻值过大（>10kΩ）
  ├── VCC电压不足（MPU6050需要3.3V，不能接5V）
  ├── I2C地址错误（AD0引脚状态）
  └── 总线速度过高（超过400kHz时需要更小的上拉电阻）

解决方案：
  1. 用万用表测量SCL/SDA静止时电压（应为3.3V）
  2. 确认上拉电阻为4.7kΩ（400kHz）或10kΩ（100kHz）
  3. 用逻辑分析仪抓取I2C波形，检查ACK位
  4. 尝试降低I2C速度到100kHz
```

**问题2：I2C 通信偶发失败（HAL_TIMEOUT）**

```c
// 解决方案：添加I2C总线复位机制
void i2c_bus_reset(void) {
    // 手动产生9个时钟脉冲，强制从机释放SDA
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // 将SCL/SDA配置为GPIO输出
    GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    // 产生9个时钟脉冲
    for (int i = 0; i < 9; i++) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
        HAL_Delay(1);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);
        HAL_Delay(1);
    }

    // 产生STOP条件
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_RESET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);

    // 重新初始化I2C外设
    HAL_I2C_DeInit(&hi2c1);
    HAL_I2C_Init(&hi2c1);
}
```

### 振动混叠（Vibration Aliasing）

**问题**：电机振动频率接近采样率的一半（奈奎斯特频率），导致加速度计数据出现低频虚假信号。

```
示例：
  电机振动频率：60Hz
  采样率：100Hz（奈奎斯特频率50Hz）
  混叠后：100-60=40Hz 的虚假信号出现在加速度计数据中

解决方案：
  1. 提高采样率（>120Hz，使奈奎斯特频率>60Hz）
  2. 降低DLPF截止频率（低于振动频率）
  3. 硬件隔振（硅胶减振垫）
  4. 使用BMI088（专为无人机设计，抗振动性能更好）

DLPF设置建议（电机振动场景）：
  mpu_write(REG_CONFIG, 0x04);  // 截止频率21Hz，滤除高频振动
```

### 万向节死锁（Gimbal Lock）

**问题**：使用欧拉角时，当 Pitch = ±90° 时，Roll 和 Yaw 轴重合，丢失一个自由度。

```
症状：
  - 机器人/无人机做大角度机动时，姿态角突然跳变
  - 特别是在 Pitch 接近 ±90° 时出现

解决方案：
  1. 改用四元数内部计算，仅在显示时转换为欧拉角
  2. 使用 Mahony 或 Madgwick 滤波器（内部使用四元数）
  3. 如果必须用欧拉角，检测奇异点并特殊处理：

void safe_euler_from_quat(float q[4], float *roll, float *pitch, float *yaw) {
    float sinp = 2.0f * (q[0]*q[2] - q[3]*q[1]);

    // 检测万向节死锁
    if (fabsf(sinp) >= 0.9999f) {
        // 奇异点：Pitch = ±90°
        *pitch = copysignf(M_PI / 2.0f, sinp);
        *roll  = 0;  // Roll任意，设为0
        *yaw   = atan2f(2.0f*(q[0]*q[3]+q[1]*q[2]),
                        1.0f-2.0f*(q[2]*q[2]+q[3]*q[3]));
    } else {
        quat_to_euler(q, roll, pitch, yaw);
    }
}
```

### 角度漂移问题

**问题**：长时间运行后，姿态角持续偏移。

```
原因与解决方案：

1. 陀螺仪零偏未校准
   → 增加校准采样次数（500~1000次）
   → 每次上电重新校准
   → 使用温度补偿（零偏随温度变化约0.01°/s/°C）

2. 互补滤波α值过大
   → 降低α值（如从0.98降到0.95）
   → 增加加速度计权重

3. 加速度计受线性加速度干扰
   → 检测加速度模长：|a| ≈ 1g时才更新加速度计权重
   → 动态调整α值：运动时增大α，静止时减小α

// 自适应互补滤波
void adaptive_complementary_filter(Attitude *att, const MPU6050_Data *data, float dt) {
    float acc_magnitude = sqrtf(data->ax*data->ax + data->ay*data->ay + data->az*data->az);

    // 加速度模长偏离1g时，降低加速度计权重
    float acc_weight = 1.0f - fminf(fabsf(acc_magnitude - 1.0f) / 0.5f, 1.0f);
    float alpha = 0.98f + 0.02f * (1.0f - acc_weight);  // 0.98~1.0

    float acc_roll  = atan2f(data->ay, data->az) * RAD_TO_DEG;
    float acc_pitch = atan2f(-data->ax,
                             sqrtf(data->ay*data->ay + data->az*data->az)) * RAD_TO_DEG;

    att->roll  = alpha * (att->roll  + data->gx * dt) + (1.0f - alpha) * acc_roll;
    att->pitch = alpha * (att->pitch + data->gy * dt) + (1.0f - alpha) * acc_pitch;
}
```

### 磁力计干扰

**问题**：磁力计受到硬铁（Hard Iron）和软铁（Soft Iron）干扰，航向角不准。

```
硬铁干扰：固定偏移，由永磁体（电机、扬声器）引起
  → 通过旋转校准消除（记录最大最小值，取中点）

软铁干扰：椭球形变形，由铁磁材料引起
  → 需要椭球拟合校准（更复杂）

快速判断是否有干扰：
  旋转设备一圈，绘制 mx vs my 散点图
  ✓ 正常：圆形，圆心在原点
  ✗ 硬铁：圆形，圆心偏移
  ✗ 软铁：椭圆形

实用建议：
  - 磁力计距离电机至少5cm
  - 避免在金属桌面上校准
  - 每次更换安装位置后重新校准
```

### 常见错误速查表

| 现象 | 可能原因 | 解决方法 |
|------|---------|---------|
| WHO_AM_I 返回 0xFF | I2C通信失败 | 检查接线、上拉电阻 |
| 数据全为0 | 未退出睡眠模式 | 检查PWR_MGMT_1写入 |
| 角度漂移严重 | 零偏未校准 | 增加校准采样次数 |
| 动态时角度抖动 | DLPF截止频率过高 | 降低截止频率 |
| 振动时数据异常 | 振动混叠 | 提高采样率或加硬件隔振 |
| Pitch=90°时Roll跳变 | 万向节死锁 | 改用四元数 |
| 航向角不准 | 磁力计未校准 | 执行硬铁校准 |
| DMP初始化失败 | 固件加载失败 | 检查I2C速度，重试 |
| 温度升高后漂移增大 | 温度零偏 | 添加温度补偿 |


## 测试与验证

### 单元测试：IMU 驱动验证

```c
// test_imu.c - 在开发阶段运行的验证测试
#include <assert.h>
#include <math.h>

// 测试1：验证原始数据转换
void test_raw_conversion(void) {
    // 已知：±4g量程，灵敏度8192 LSB/g
    // 输入：raw_az = 8192（对应1g）
    int16_t raw_az = 8192;
    float az = raw_az / 8192.0f;
    assert(fabsf(az - 1.0f) < 0.001f);  // 应为1.0g

    // 输入：raw_gz = 655（对应10°/s）
    int16_t raw_gz = 655;
    float gz = raw_gz / 65.5f;
    assert(fabsf(gz - 10.0f) < 0.1f);  // 应为10°/s

    printf("PASS: raw conversion\n");
}

// 测试2：验证互补滤波收敛性
void test_complementary_filter_convergence(void) {
    Attitude att = {0, 0};
    MPU6050_Data data = {
        .ax = 0, .ay = 0, .az = 1.0f,  // 水平放置
        .gx = 0, .gy = 0, .gz = 0
    };

    // 运行1000步（8秒），应收敛到0度
    for (int i = 0; i < 1000; i++) {
        complementary_filter(&att, &data, 0.008f);
    }

    assert(fabsf(att.roll)  < 0.1f);  // 应收敛到0°
    assert(fabsf(att.pitch) < 0.1f);
    printf("PASS: complementary filter convergence\n");
}

// 测试3：验证四元数归一化
void test_quaternion_normalization(void) {
    MahonyFilter f;
    mahony_init(&f);

    // 运行100步
    for (int i = 0; i < 100; i++) {
        mahony_update(&f, 0.1f, 0.0f, 0.0f,
                      0.0f, 0.0f, 1.0f, 0.01f);
    }

    // 四元数模长应为1
    float norm = sqrtf(f.q[0]*f.q[0] + f.q[1]*f.q[1] +
                       f.q[2]*f.q[2] + f.q[3]*f.q[3]);
    assert(fabsf(norm - 1.0f) < 1e-5f);
    printf("PASS: quaternion normalization\n");
}

void run_all_tests(void) {
    test_raw_conversion();
    test_complementary_filter_convergence();
    test_quaternion_normalization();
    printf("All tests passed!\n");
}
```

### 硬件验证步骤

```
验收测试流程：

1. 通信验证
   □ WHO_AM_I 返回 0x68（MPU6050）或 0x47（ICM-42688-P）
   □ 连续读取100次无错误

2. 静态精度验证
   □ 水平放置：|Roll| < 1°, |Pitch| < 1°
   □ 竖直放置（X轴朝上）：|Roll - 90°| < 2°
   □ 陀螺仪静止噪声：RMS < 0.05 °/s

3. 动态响应验证
   □ 快速旋转90°后恢复水平：角度误差 < 3°
   □ 振动测试：电机运行时角度噪声 < 2°

4. 长期稳定性验证
   □ 静止放置10分钟：角度漂移 < 2°
   □ 温度变化10°C：角度变化 < 3°
```

## 延伸阅读

- [传感器数据融合技术](../../04-sensor-technology/intermediate/02-sensor-fusion.html) - 多传感器融合进阶
- [传感器标定与校准](../../04-sensor-technology/intermediate/03-sensor-calibration.html) - 系统性校准方法
- [智能云台项目](../../05-actuator-control/advanced/04-smart-gimbal-project.html) - MPU6050实际应用
- [编码器接口](../../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/04-encoder-interface.html) - 与编码器配合实现运动控制
- [MQTT协议](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html) - 将IMU数据上传云端

## 参考资料

1. MPU-6000/MPU-6050 Product Specification Rev 3.4 - InvenSense/TDK
2. MPU-6000/MPU-6050 Register Map and Descriptions Rev 4.2 - InvenSense
3. ICM-42688-P Datasheet Rev 1.7 - TDK InvenSense
4. QMC5883L Datasheet - QST Corporation
5. Mahony, R., Hamel, T., Pflimlin, J.M. - "Nonlinear Complementary Filters on the Special Orthogonal Group" - IEEE Transactions on Automatic Control, 2008
6. Madgwick, S.O.H. - "An efficient orientation filter for inertial and inertial/magnetic sensor arrays" - University of Bristol, 2010
7. Kalman, R.E. - "A New Approach to Linear Filtering and Prediction Problems" - ASME Journal of Basic Engineering, 1960
8. IEEE Std 1554-2005 - IEEE Standard for Inertial Sensor Terminology
9. [I2Cdevlib MPU6050](https://github.com/jrowberg/i2cdevlib) - Jeff Rowberg 开源驱动库
10. [Madgwick Filter 开源实现](https://x-io.co.uk/open-source-imu-and-ahrs-algorithms/) - x-io Technologies
11. Allan, D.W. - "Statistics of Atomic Frequency Standards" - Proceedings of the IEEE, 1966
12. BMI088 Datasheet - Bosch Sensortec（无人机专用IMU参考）

