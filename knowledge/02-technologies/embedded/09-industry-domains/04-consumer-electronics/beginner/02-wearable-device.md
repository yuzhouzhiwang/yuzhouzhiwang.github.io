---
title: "可穿戴设备开发：从零开始构建智能手环系统"
description: "全面学习可穿戴设备的硬件设计、传感器集成、低功耗设计、数据同步和移动应用开发，通过实践项目掌握智能手环的核心技术"
slug: "wearable-device-development"

# 分类信息
domain: "行业领域"
module: "消费电子"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 可穿戴设备
  - 智能手环
  - 健康监测
  - 低功耗设计
  - BLE蓝牙
prerequisites:
  - "基本电子知识"
  - "C/C++编程基础"
  - "移动应用开发基础"
related_contents:
  - "smart-home-system"
  - "biosignal-processing"
  - "power-optimization"

# 学习信息
estimated_time: 90
difficulty_score: 4

# 作者和版本
author: "可穿戴设备专家"
author_id: "wearable_device_expert"
created_at: "2024-01-15"
updated_at: "2024-01-15"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - 可穿戴设备开发
  - 智能手环
  - 健康监测
  - 低功耗设计
  - BLE蓝牙通信
cover_image: "/images/domains/consumer-electronics/wearable-device.jpg"
---

# 可穿戴设备开发：从零开始构建智能手环系统

## 学习目标

完成本教程后，你将能够：

- [ ] 理解可穿戴设备的系统架构和设计原则
- [ ] 掌握常用传感器的集成和数据采集方法
- [ ] 实现低功耗设计，延长设备续航时间
- [ ] 使用BLE蓝牙实现设备与手机的通信
- [ ] 开发移动应用进行数据同步和可视化
- [ ] 实现心率、步数、睡眠等健康监测功能
- [ ] 掌握固件OTA升级技术

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解基本的电子电路知识
- 掌握C/C++编程语言
- 理解蓝牙通信基础
- 了解传感器工作原理

**技能要求**：
- 能够使用开发板进行编程和调试
- 会使用示波器等基本测试工具
- 具备移动应用开发基础（Android或iOS）
- 了解基本的信号处理知识

## 第一部分：可穿戴设备概述

### 1.1 什么是可穿戴设备？

**可穿戴设备（Wearable Device）** 是指可以穿戴在身体上或整合到用户衣服或配件中的便携式设备，通过软件支持和数据交互实现强大的功能。

**核心特点**：
- **便携性**：小巧轻便，适合长时间佩戴
- **低功耗**：续航时间长，通常可达数天到数周
- **传感器丰富**：集成多种传感器，实时监测数据
- **无线连接**：通过蓝牙与手机同步数据
- **健康监测**：实时追踪运动、睡眠、心率等健康数据

**典型应用场景**：
- 运动追踪：步数、距离、卡路里消耗
- 健康监测：心率、血氧、睡眠质量
- 消息提醒：来电、短信、应用通知
- 移动支付：NFC支付功能
- 智能控制：控制智能家居设备


### 1.2 智能手环系统架构

```
┌─────────────────────────────────────────────────────────┐
│                  智能手环系统架构                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    应用层 (Application)                  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ 移动APP  │  │ 数据分析 │  │ 云端同步 │  │ 社交分享││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          ↕ BLE通信
┌─────────────────────────────────────────────────────────┐
│                    固件层 (Firmware)                     │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ 数据采集 │  │ 算法处理 │  │ 电源管理 │  │ BLE协议 ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                    硬件层 (Hardware)                     │
├─────────────────────────────────────────────────────────┤
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐   │
│  │MCU │ │加速│ │心率│ │显示│ │电池│ │充电│ │振动│   │
│  │    │ │度计│ │传感│ │屏幕│ │    │ │电路│ │马达│   │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘   │
└─────────────────────────────────────────────────────────┘
```

**各层功能说明**：

1. **硬件层**
   - 主控芯片（MCU）：nRF52832、ESP32等
   - 传感器：加速度计、心率传感器、陀螺仪
   - 显示：OLED屏幕
   - 电源：锂电池和充电管理
   - 交互：触摸按键、振动马达

2. **固件层**
   - 传感器数据采集和预处理
   - 算法实现（计步、心率分析、睡眠检测）
   - 低功耗管理和优化
   - BLE通信协议栈

3. **应用层**
   - 移动应用开发
   - 数据可视化和分析
   - 云端数据同步
   - 社交功能

### 1.3 关键技术挑战

| 挑战 | 描述 | 解决方案 |
|------|------|---------|
| **功耗** | 电池容量有限 | 低功耗MCU、睡眠模式、优化算法 |
| **体积** | 空间受限 | 高集成度芯片、紧凑PCB设计 |
| **精度** | 传感器精度要求高 | 算法优化、多传感器融合 |
| **续航** | 用户期望长续航 | 电源管理、动态调频 |
| **防水** | 日常使用需防水 | 密封设计、防水材料 |


## 第二部分：硬件设计与准备

### 2.1 核心硬件清单

| 名称 | 型号 | 数量 | 说明 | 参考价格 |
|------|------|------|------|----------|
| 主控芯片 | nRF52832 | 1 | BLE 5.0，低功耗 | ¥25 |
| 加速度计 | MPU6050 | 1 | 3轴加速度+陀螺仪 | ¥8 |
| 心率传感器 | MAX30102 | 1 | 光电容积脉搏波 | ¥15 |
| OLED显示屏 | SSD1306 | 1 | 0.96寸，128x64 | ¥12 |
| 锂电池 | 3.7V 150mAh | 1 | 聚合物锂电池 | ¥10 |
| 充电IC | TP4056 | 1 | 锂电池充电管理 | ¥2 |
| 振动马达 | 扁平马达 | 1 | 触觉反馈 | ¥3 |
| 触摸按键 | TTP223 | 1 | 电容触摸 | ¥2 |
| PCB板 | 定制 | 1 | 双层板 | ¥30 |
| 外壳和表带 | 3D打印 | 1 | ABS材料 | ¥20 |

**总预算**：约 ¥150

### 2.2 开发板选择

**推荐开发板**：
1. **Nordic nRF52 DK** - 官方开发板，功能完整
2. **Adafruit Feather nRF52** - 小巧，适合原型开发
3. **Seeed XIAO nRF52840** - 超小尺寸，适合可穿戴

**本教程使用**：nRF52832开发板

### 2.3 软件环境配置

#### 安装开发工具

**方案1：使用Arduino IDE**

```bash
# 1. 安装Arduino IDE
# 下载：https://www.arduino.cc/

# 2. 添加nRF52板支持
# 文件 → 首选项 → 附加开发板管理器网址
https://adafruit.github.io/arduino-board-index/package_adafruit_index.json

# 3. 安装Adafruit nRF52板
# 工具 → 开发板 → 开发板管理器
# 搜索"nRF52"并安装
```

**方案2：使用PlatformIO**

```bash
# 1. 安装VS Code
# 2. 安装PlatformIO扩展
# 3. 创建新项目，选择nRF52832平台
```

#### 安装必要库

```bash
# Arduino IDE中安装以下库：
- Adafruit_GFX
- Adafruit_SSD1306
- MPU6050
- MAX30105
- ArduinoBLE
```

### 2.4 硬件连接

#### 引脚分配

```
nRF52832 引脚连接：

传感器连接：
┌──────────────────────────────────┐
│ MPU6050 (加速度计)                │
│  SDA  → P26 (I2C_SDA)            │
│  SCL  → P27 (I2C_SCL)            │
│  VCC  → 3.3V                     │
│  GND  → GND                      │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ MAX30102 (心率传感器)             │
│  SDA  → P26 (I2C_SDA)            │
│  SCL  → P27 (I2C_SCL)            │
│  INT  → P28                      │
│  VCC  → 3.3V                     │
│  GND  → GND                      │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ SSD1306 (OLED显示屏)              │
│  SDA  → P26 (I2C_SDA)            │
│  SCL  → P27 (I2C_SCL)            │
│  VCC  → 3.3V                     │
│  GND  → GND                      │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ 其他外设                          │
│  振动马达 → P29 (PWM)             │
│  触摸按键 → P30 (GPIO)            │
│  充电检测 → P31 (ADC)             │
└──────────────────────────────────┘
```

⚠️ **注意事项**：
- 所有I2C设备共用同一总线
- 确保电源电压为3.3V
- 添加上拉电阻（4.7kΩ）到I2C总线


## 第三部分：传感器集成与数据采集

### 3.1 加速度计集成（计步功能）

#### 初始化MPU6050

```cpp
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// 计步相关变量
int stepCount = 0;
float lastAccelMagnitude = 0;
unsigned long lastStepTime = 0;
const float STEP_THRESHOLD = 1.2;  // 步态检测阈值
const int STEP_MIN_INTERVAL = 300; // 最小步态间隔(ms)

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  // 初始化MPU6050
  Serial.println("初始化MPU6050...");
  mpu.initialize();
  
  if (mpu.testConnection()) {
    Serial.println("MPU6050连接成功");
  } else {
    Serial.println("MPU6050连接失败");
    while(1);
  }
  
  // 配置传感器
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);  // ±2g
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);  // ±250°/s
  mpu.setDLPFMode(MPU6050_DLPF_BW_20);  // 低通滤波20Hz
}

void loop() {
  // 读取加速度数据
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  
  // 转换为g值
  float accelX = ax / 16384.0;
  float accelY = ay / 16384.0;
  float accelZ = az / 16384.0;
  
  // 计算加速度幅值
  float accelMagnitude = sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
  
  // 步态检测算法
  detectStep(accelMagnitude);
  
  delay(50);  // 20Hz采样率
}

void detectStep(float accelMagnitude) {
  unsigned long currentTime = millis();
  
  // 检测峰值
  if (accelMagnitude > STEP_THRESHOLD && 
      lastAccelMagnitude < STEP_THRESHOLD &&
      (currentTime - lastStepTime) > STEP_MIN_INTERVAL) {
    
    stepCount++;
    lastStepTime = currentTime;
    
    Serial.print("步数: ");
    Serial.println(stepCount);
    
    // 触发振动反馈（每10步）
    if (stepCount % 10 == 0) {
      vibrate(50);
    }
  }
  
  lastAccelMagnitude = accelMagnitude;
}

void vibrate(int duration) {
  digitalWrite(VIBRATION_PIN, HIGH);
  delay(duration);
  digitalWrite(VIBRATION_PIN, LOW);
}
```

#### 改进的计步算法

```cpp
// 使用滑动窗口和峰值检测的改进算法
#define WINDOW_SIZE 10

class StepDetector {
private:
  float accelWindow[WINDOW_SIZE];
  int windowIndex = 0;
  int stepCount = 0;
  unsigned long lastStepTime = 0;
  
  const float THRESHOLD_HIGH = 1.3;
  const float THRESHOLD_LOW = 0.8;
  const int MIN_STEP_INTERVAL = 250;
  const int MAX_STEP_INTERVAL = 2000;
  
public:
  void addSample(float accelMagnitude) {
    // 添加到滑动窗口
    accelWindow[windowIndex] = accelMagnitude;
    windowIndex = (windowIndex + 1) % WINDOW_SIZE;
    
    // 检测步态
    if (isPeak() && isValidStep()) {
      stepCount++;
      lastStepTime = millis();
      onStepDetected();
    }
  }
  
  bool isPeak() {
    // 检查当前值是否为局部峰值
    int currentIdx = (windowIndex - 1 + WINDOW_SIZE) % WINDOW_SIZE;
    float currentValue = accelWindow[currentIdx];
    
    if (currentValue < THRESHOLD_HIGH) return false;
    
    // 检查是否为局部最大值
    for (int i = 0; i < WINDOW_SIZE; i++) {
      if (i != currentIdx && accelWindow[i] >= currentValue) {
        return false;
      }
    }
    
    return true;
  }
  
  bool isValidStep() {
    unsigned long currentTime = millis();
    unsigned long interval = currentTime - lastStepTime;
    
    return (interval >= MIN_STEP_INTERVAL && 
            interval <= MAX_STEP_INTERVAL);
  }
  
  void onStepDetected() {
    Serial.print("检测到步态，总步数: ");
    Serial.println(stepCount);
  }
  
  int getStepCount() {
    return stepCount;
  }
  
  void resetStepCount() {
    stepCount = 0;
  }
};

StepDetector stepDetector;

void loop() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  
  float accelX = ax / 16384.0;
  float accelY = ay / 16384.0;
  float accelZ = az / 16384.0;
  
  float accelMagnitude = sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
  
  stepDetector.addSample(accelMagnitude);
  
  delay(50);
}
```


### 3.2 心率传感器集成

#### 初始化MAX30102

```cpp
#include <MAX30105.h>
#include <heartRate.h>

MAX30105 particleSensor;

// 心率计算相关
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;

void setupHeartRateSensor() {
  Serial.println("初始化MAX30102...");
  
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102未找到");
    while (1);
  }
  
  Serial.println("MAX30102初始化成功");
  
  // 配置传感器
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);    // 红光LED电流
  particleSensor.setPulseAmplitudeGreen(0);     // 关闭绿光
}

void readHeartRate() {
  long irValue = particleSensor.getIR();
  
  // 检测心跳
  if (checkForBeat(irValue) == true) {
    long delta = millis() - lastBeat;
    lastBeat = millis();
    
    beatsPerMinute = 60 / (delta / 1000.0);
    
    // 合理性检查
    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;
      
      // 计算平均心率
      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++) {
        beatAvg += rates[x];
      }
      beatAvg /= RATE_SIZE;
    }
  }
  
  Serial.print("IR=");
  Serial.print(irValue);
  Serial.print(", BPM=");
  Serial.print(beatsPerMinute);
  Serial.print(", Avg BPM=");
  Serial.println(beatAvg);
  
  // 检查手指是否放在传感器上
  if (irValue < 50000) {
    Serial.println("请将手指放在传感器上");
  }
}
```

#### 改进的心率算法

```cpp
class HeartRateMonitor {
private:
  MAX30105 sensor;
  
  // 信号处理
  const int BUFFER_SIZE = 100;
  uint32_t irBuffer[BUFFER_SIZE];
  uint32_t redBuffer[BUFFER_SIZE];
  int bufferIndex = 0;
  
  // 心率计算
  int32_t heartRate = 0;
  int8_t validHeartRate = 0;
  int32_t spo2 = 0;
  int8_t validSPO2 = 0;
  
public:
  bool begin() {
    if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
      return false;
    }
    
    // 优化配置
    byte ledBrightness = 60;
    byte sampleAverage = 4;
    byte ledMode = 2;  // 红光+红外
    int sampleRate = 100;
    int pulseWidth = 411;
    int adcRange = 4096;
    
    sensor.setup(ledBrightness, sampleAverage, ledMode, 
                 sampleRate, pulseWidth, adcRange);
    
    return true;
  }
  
  void update() {
    // 读取传感器数据
    uint32_t irValue = sensor.getIR();
    uint32_t redValue = sensor.getRed();
    
    // 存储到缓冲区
    irBuffer[bufferIndex] = irValue;
    redBuffer[bufferIndex] = redValue;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    
    // 缓冲区满后计算心率和血氧
    if (bufferIndex == 0) {
      calculateHeartRateAndSpO2();
    }
  }
  
  void calculateHeartRateAndSpO2() {
    // 使用Maxim的算法计算心率和血氧
    maxim_heart_rate_and_oxygen_saturation(
      irBuffer, BUFFER_SIZE,
      redBuffer,
      &spo2, &validSPO2,
      &heartRate, &validHeartRate
    );
  }
  
  int getHeartRate() {
    return validHeartRate ? heartRate : 0;
  }
  
  int getSpO2() {
    return validSPO2 ? spo2 : 0;
  }
  
  bool isFingerDetected() {
    return sensor.getIR() > 50000;
  }
};

HeartRateMonitor hrMonitor;

void setup() {
  Serial.begin(115200);
  
  if (!hrMonitor.begin()) {
    Serial.println("心率传感器初始化失败");
    while(1);
  }
}

void loop() {
  hrMonitor.update();
  
  if (hrMonitor.isFingerDetected()) {
    Serial.print("心率: ");
    Serial.print(hrMonitor.getHeartRate());
    Serial.print(" bpm, 血氧: ");
    Serial.print(hrMonitor.getSpO2());
    Serial.println(" %");
  } else {
    Serial.println("请将手指放在传感器上");
  }
  
  delay(100);
}
```

### 3.3 睡眠监测

```cpp
class SleepMonitor {
private:
  MPU6050 mpu;
  
  // 睡眠状态
  enum SleepState {
    AWAKE,
    LIGHT_SLEEP,
    DEEP_SLEEP
  };
  
  SleepState currentState = AWAKE;
  unsigned long sleepStartTime = 0;
  unsigned long deepSleepDuration = 0;
  unsigned long lightSleepDuration = 0;
  
  // 活动检测
  const float MOVEMENT_THRESHOLD = 0.1;
  const int SLEEP_DETECTION_WINDOW = 300000;  // 5分钟
  int movementCount = 0;
  
public:
  void update() {
    // 读取加速度数据
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;
    
    float accelMagnitude = sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
    
    // 检测活动
    if (abs(accelMagnitude - 1.0) > MOVEMENT_THRESHOLD) {
      movementCount++;
    }
    
    // 每分钟更新一次睡眠状态
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 60000) {
      updateSleepState();
      lastUpdate = millis();
      movementCount = 0;
    }
  }
  
  void updateSleepState() {
    SleepState previousState = currentState;
    
    // 根据活动量判断睡眠状态
    if (movementCount > 30) {
      currentState = AWAKE;
    } else if (movementCount > 5) {
      currentState = LIGHT_SLEEP;
    } else {
      currentState = DEEP_SLEEP;
    }
    
    // 记录睡眠时长
    if (currentState != AWAKE && previousState == AWAKE) {
      sleepStartTime = millis();
    }
    
    if (currentState == DEEP_SLEEP) {
      deepSleepDuration += 60000;
    } else if (currentState == LIGHT_SLEEP) {
      lightSleepDuration += 60000;
    }
    
    Serial.print("睡眠状态: ");
    Serial.println(getStateString());
  }
  
  String getStateString() {
    switch(currentState) {
      case AWAKE: return "清醒";
      case LIGHT_SLEEP: return "浅睡眠";
      case DEEP_SLEEP: return "深睡眠";
      default: return "未知";
    }
  }
  
  void getSleepReport(int &deepMinutes, int &lightMinutes) {
    deepMinutes = deepSleepDuration / 60000;
    lightMinutes = lightSleepDuration / 60000;
  }
  
  void resetSleepData() {
    deepSleepDuration = 0;
    lightSleepDuration = 0;
    sleepStartTime = 0;
  }
};
```


## 第四部分：显示界面开发

### 4.1 OLED显示初始化

```cpp
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setupDisplay() {
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306初始化失败");
    while(1);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.display();
}
```

### 4.2 多页面UI设计

```cpp
class WearableUI {
private:
  Adafruit_SSD1306 &display;
  
  enum Page {
    PAGE_TIME,
    PAGE_STEPS,
    PAGE_HEART_RATE,
    PAGE_SLEEP,
    PAGE_COUNT
  };
  
  Page currentPage = PAGE_TIME;
  unsigned long lastPageChange = 0;
  const int AUTO_SWITCH_INTERVAL = 5000;  // 5秒自动切换
  
public:
  WearableUI(Adafruit_SSD1306 &disp) : display(disp) {}
  
  void update() {
    display.clearDisplay();
    
    switch(currentPage) {
      case PAGE_TIME:
        drawTimePage();
        break;
      case PAGE_STEPS:
        drawStepsPage();
        break;
      case PAGE_HEART_RATE:
        drawHeartRatePage();
        break;
      case PAGE_SLEEP:
        drawSleepPage();
        break;
    }
    
    display.display();
  }
  
  void drawTimePage() {
    // 显示时间
    display.setTextSize(2);
    display.setCursor(20, 10);
    display.print("12:34");
    
    display.setTextSize(1);
    display.setCursor(30, 35);
    display.print("2024-01-15");
    
    // 显示电池电量
    drawBattery(100, 5, 80);
  }
  
  void drawStepsPage() {
    // 步数图标
    display.setTextSize(1);
    display.setCursor(10, 5);
    display.print("STEPS");
    
    // 步数数值
    display.setTextSize(3);
    display.setCursor(15, 25);
    display.print(stepDetector.getStepCount());
    
    // 目标进度条
    int progress = (stepDetector.getStepCount() * 100) / 10000;
    drawProgressBar(10, 55, 108, 6, progress);
  }
  
  void drawHeartRatePage() {
    // 心率图标
    display.setTextSize(1);
    display.setCursor(10, 5);
    display.print("HEART RATE");
    
    // 心率数值
    display.setTextSize(3);
    display.setCursor(25, 25);
    display.print(hrMonitor.getHeartRate());
    
    display.setTextSize(1);
    display.setCursor(85, 35);
    display.print("bpm");
    
    // 心率波形（简化）
    drawHeartWave();
  }
  
  void drawSleepPage() {
    display.setTextSize(1);
    display.setCursor(10, 5);
    display.print("SLEEP");
    
    int deepMinutes, lightMinutes;
    sleepMonitor.getSleepReport(deepMinutes, lightMinutes);
    
    display.setCursor(10, 20);
    display.print("Deep: ");
    display.print(deepMinutes);
    display.print(" min");
    
    display.setCursor(10, 35);
    display.print("Light: ");
    display.print(lightMinutes);
    display.print(" min");
    
    int totalMinutes = deepMinutes + lightMinutes;
    display.setCursor(10, 50);
    display.print("Total: ");
    display.print(totalMinutes / 60);
    display.print("h ");
    display.print(totalMinutes % 60);
    display.print("m");
  }
  
  void drawBattery(int x, int y, int percentage) {
    // 电池外框
    display.drawRect(x, y, 20, 10, SSD1306_WHITE);
    display.fillRect(x + 20, y + 3, 2, 4, SSD1306_WHITE);
    
    // 电量填充
    int fillWidth = (percentage * 18) / 100;
    display.fillRect(x + 1, y + 1, fillWidth, 8, SSD1306_WHITE);
  }
  
  void drawProgressBar(int x, int y, int width, int height, int percentage) {
    // 进度条外框
    display.drawRect(x, y, width, height, SSD1306_WHITE);
    
    // 进度填充
    int fillWidth = (percentage * (width - 2)) / 100;
    display.fillRect(x + 1, y + 1, fillWidth, height - 2, SSD1306_WHITE);
  }
  
  void drawHeartWave() {
    // 简化的心率波形
    int y = 55;
    for (int x = 0; x < 128; x += 4) {
      int waveY = y + sin(x * 0.1) * 5;
      display.drawPixel(x, waveY, SSD1306_WHITE);
    }
  }
  
  void nextPage() {
    currentPage = (Page)((currentPage + 1) % PAGE_COUNT);
    lastPageChange = millis();
  }
  
  void previousPage() {
    currentPage = (Page)((currentPage - 1 + PAGE_COUNT) % PAGE_COUNT);
    lastPageChange = millis();
  }
};

WearableUI ui(display);

void loop() {
  // 更新UI
  ui.update();
  
  // 检测按键切换页面
  if (digitalRead(BUTTON_PIN) == LOW) {
    ui.nextPage();
    delay(200);  // 防抖
  }
  
  delay(100);
}
```

### 4.3 动画效果

```cpp
class AnimationHelper {
public:
  // 淡入淡出效果
  static void fadeIn(Adafruit_SSD1306 &display, int duration) {
    for (int i = 0; i < 256; i += 16) {
      display.ssd1306_command(SSD1306_SETCONTRAST);
      display.ssd1306_command(i);
      delay(duration / 16);
    }
  }
  
  // 滑动切换效果
  static void slideTransition(Adafruit_SSD1306 &display, 
                              void (*drawOld)(), 
                              void (*drawNew)()) {
    for (int offset = 0; offset < 128; offset += 8) {
      display.clearDisplay();
      
      // 绘制旧页面（向左移动）
      display.setCursor(-offset, 0);
      drawOld();
      
      // 绘制新页面（从右侧进入）
      display.setCursor(128 - offset, 0);
      drawNew();
      
      display.display();
      delay(20);
    }
  }
  
  // 脉冲动画（用于心率显示）
  static void pulseAnimation(Adafruit_SSD1306 &display, int x, int y) {
    for (int r = 5; r < 15; r += 2) {
      display.drawCircle(x, y, r, SSD1306_WHITE);
      display.display();
      delay(50);
      display.drawCircle(x, y, r, SSD1306_BLACK);
    }
  }
};
```


## 第五部分：低功耗设计

### 5.1 功耗分析

**典型功耗**：
- MCU运行：5-10 mA
- BLE连接：8-15 mA
- OLED显示：10-20 mA
- 传感器采集：2-5 mA
- 睡眠模式：< 10 μA

**目标续航**：
- 电池容量：150 mAh
- 目标续航：5-7天
- 平均功耗：< 1 mA

### 5.2 低功耗策略

```cpp
#include <nrf_power.h>

class PowerManager {
private:
  enum PowerMode {
    ACTIVE,
    IDLE,
    DEEP_SLEEP
  };
  
  PowerMode currentMode = ACTIVE;
  unsigned long lastActivity = 0;
  const int IDLE_TIMEOUT = 10000;      // 10秒进入空闲
  const int SLEEP_TIMEOUT = 60000;     // 60秒进入深度睡眠
  
public:
  void init() {
    // 配置低功耗模式
    NRF_POWER->DCDCEN = 1;  // 启用DC/DC转换器
    
    // 配置GPIO为低功耗
    configureGPIO();
    
    // 配置外设低功耗
    configurePeripherals();
  }
  
  void update() {
    unsigned long idleTime = millis() - lastActivity;
    
    if (idleTime > SLEEP_TIMEOUT) {
      enterDeepSleep();
    } else if (idleTime > IDLE_TIMEOUT) {
      enterIdleMode();
    } else {
      enterActiveMode();
    }
  }
  
  void enterActiveMode() {
    if (currentMode == ACTIVE) return;
    
    currentMode = ACTIVE;
    
    // 启用所有外设
    enableDisplay();
    enableSensors();
    
    // 设置CPU频率为64MHz
    NRF_CLOCK->TASKS_HFCLKSTART = 1;
    
    Serial.println("进入活动模式");
  }
  
  void enterIdleMode() {
    if (currentMode == IDLE) return;
    
    currentMode = IDLE;
    
    // 关闭显示屏
    disableDisplay();
    
    // 降低传感器采样率
    reduceSensorSampling();
    
    // 降低CPU频率
    NRF_CLOCK->TASKS_HFCLKSTOP = 1;
    
    Serial.println("进入空闲模式");
  }
  
  void enterDeepSleep() {
    if (currentMode == DEEP_SLEEP) return;
    
    currentMode = DEEP_SLEEP;
    
    // 关闭所有外设
    disableDisplay();
    disableSensors();
    
    // 配置唤醒源
    configureWakeup();
    
    // 进入系统OFF模式
    NRF_POWER->SYSTEMOFF = 1;
    
    Serial.println("进入深度睡眠");
  }
  
  void configureGPIO() {
    // 未使用的GPIO配置为输入+下拉
    for (int pin = 0; pin < 32; pin++) {
      if (!isPinUsed(pin)) {
        pinMode(pin, INPUT_PULLDOWN);
      }
    }
  }
  
  void configurePeripherals() {
    // I2C低功耗配置
    Wire.setClock(100000);  // 降低I2C时钟
    
    // UART低功耗配置（调试时可关闭）
    #ifndef DEBUG
    Serial.end();
    #endif
  }
  
  void configureWakeup() {
    // 配置按键唤醒
    nrf_gpio_cfg_sense_input(BUTTON_PIN, 
                             NRF_GPIO_PIN_PULLUP, 
                             NRF_GPIO_PIN_SENSE_LOW);
    
    // 配置定时器唤醒（每小时）
    // 使用RTC实现
  }
  
  void onActivity() {
    lastActivity = millis();
    if (currentMode != ACTIVE) {
      enterActiveMode();
    }
  }
  
  bool isPinUsed(int pin) {
    // 检查引脚是否被使用
    const int usedPins[] = {26, 27, 28, 29, 30, 31};
    for (int i = 0; i < sizeof(usedPins)/sizeof(int); i++) {
      if (pin == usedPins[i]) return true;
    }
    return false;
  }
  
  void enableDisplay() {
    display.ssd1306_command(SSD1306_DISPLAYON);
  }
  
  void disableDisplay() {
    display.ssd1306_command(SSD1306_DISPLAYOFF);
  }
  
  void enableSensors() {
    mpu.setSleepEnabled(false);
    particleSensor.wakeUp();
  }
  
  void disableSensors() {
    mpu.setSleepEnabled(true);
    particleSensor.shutDown();
  }
  
  void reduceSensorSampling() {
    // 降低采样率到1Hz
    mpu.setRate(1);
  }
};

PowerManager powerMgr;

void setup() {
  powerMgr.init();
}

void loop() {
  powerMgr.update();
  
  // 检测用户活动
  if (digitalRead(BUTTON_PIN) == LOW) {
    powerMgr.onActivity();
  }
  
  delay(100);
}
```

### 5.3 电池管理

```cpp
class BatteryManager {
private:
  const int BATTERY_PIN = A0;
  const float VOLTAGE_DIVIDER = 2.0;  // 分压比
  const float ADC_REFERENCE = 3.3;
  const int ADC_RESOLUTION = 1024;
  
  float batteryVoltage = 0;
  int batteryPercentage = 100;
  bool isCharging = false;
  
public:
  void update() {
    // 读取电池电压
    int adcValue = analogRead(BATTERY_PIN);
    batteryVoltage = (adcValue * ADC_REFERENCE / ADC_RESOLUTION) * VOLTAGE_DIVIDER;
    
    // 计算电量百分比
    batteryPercentage = calculatePercentage(batteryVoltage);
    
    // 检测充电状态
    isCharging = digitalRead(CHARGING_PIN) == LOW;
    
    // 低电量警告
    if (batteryPercentage < 10 && !isCharging) {
      lowBatteryWarning();
    }
  }
  
  int calculatePercentage(float voltage) {
    // 锂电池电压-电量对应关系
    const float voltageTable[][2] = {
      {4.2, 100},
      {4.1, 90},
      {4.0, 80},
      {3.9, 70},
      {3.8, 60},
      {3.7, 50},
      {3.6, 40},
      {3.5, 30},
      {3.4, 20},
      {3.3, 10},
      {3.0, 0}
    };
    
    // 线性插值
    for (int i = 0; i < 10; i++) {
      if (voltage >= voltageTable[i+1][0]) {
        float v1 = voltageTable[i][0];
        float v2 = voltageTable[i+1][0];
        float p1 = voltageTable[i][1];
        float p2 = voltageTable[i+1][1];
        
        return p2 + (voltage - v2) * (p1 - p2) / (v1 - v2);
      }
    }
    
    return 0;
  }
  
  void lowBatteryWarning() {
    // 显示低电量警告
    display.clearDisplay();
    display.setTextSize(2);
    display.setCursor(10, 20);
    display.print("LOW");
    display.setCursor(10, 40);
    display.print("BATTERY");
    display.display();
    
    // 振动提醒
    vibrate(200);
    delay(500);
    vibrate(200);
  }
  
  float getVoltage() {
    return batteryVoltage;
  }
  
  int getPercentage() {
    return batteryPercentage;
  }
  
  bool getChargingStatus() {
    return isCharging;
  }
};

BatteryManager battery;
```


## 第六部分：BLE蓝牙通信

### 6.1 BLE服务设计

```cpp
#include <ArduinoBLE.h>

// 定义BLE服务和特征UUID
#define DEVICE_NAME "SmartBand"
#define SERVICE_UUID "180D"  // Heart Rate Service

// 自定义服务
#define CUSTOM_SERVICE_UUID "19B10000-E8F2-537E-4F6C-D104768A1214"
#define STEP_CHAR_UUID      "19B10001-E8F2-537E-4F6C-D104768A1214"
#define HR_CHAR_UUID        "19B10002-E8F2-537E-4F6C-D104768A1214"
#define BATTERY_CHAR_UUID   "19B10003-E8F2-537E-4F6C-D104768A1214"
#define CONTROL_CHAR_UUID   "19B10004-E8F2-537E-4F6C-D104768A1214"

// BLE服务和特征
BLEService customService(CUSTOM_SERVICE_UUID);
BLEIntCharacteristic stepCharacteristic(STEP_CHAR_UUID, BLERead | BLENotify);
BLEIntCharacteristic hrCharacteristic(HR_CHAR_UUID, BLERead | BLENotify);
BLEIntCharacteristic batteryCharacteristic(BATTERY_CHAR_UUID, BLERead | BLENotify);
BLEByteCharacteristic controlCharacteristic(CONTROL_CHAR_UUID, BLEWrite);

void setupBLE() {
  if (!BLE.begin()) {
    Serial.println("BLE初始化失败");
    while (1);
  }
  
  // 设置设备名称
  BLE.setLocalName(DEVICE_NAME);
  BLE.setDeviceName(DEVICE_NAME);
  
  // 设置广播的服务UUID
  BLE.setAdvertisedService(customService);
  
  // 添加特征到服务
  customService.addCharacteristic(stepCharacteristic);
  customService.addCharacteristic(hrCharacteristic);
  customService.addCharacteristic(batteryCharacteristic);
  customService.addCharacteristic(controlCharacteristic);
  
  // 添加服务
  BLE.addService(customService);
  
  // 设置初始值
  stepCharacteristic.writeValue(0);
  hrCharacteristic.writeValue(0);
  batteryCharacteristic.writeValue(100);
  
  // 设置回调函数
  controlCharacteristic.setEventHandler(BLEWritten, onControlWrite);
  
  // 开始广播
  BLE.advertise();
  
  Serial.println("BLE已启动，等待连接...");
}

void onControlWrite(BLEDevice central, BLECharacteristic characteristic) {
  byte command = controlCharacteristic.value();
  
  Serial.print("收到控制命令: ");
  Serial.println(command);
  
  switch(command) {
    case 0x01:  // 重置步数
      stepDetector.resetStepCount();
      Serial.println("步数已重置");
      break;
      
    case 0x02:  // 查找设备
      findDevice();
      break;
      
    case 0x03:  // 同步时间
      syncTime();
      break;
      
    case 0x04:  // 开始运动模式
      startWorkoutMode();
      break;
      
    case 0x05:  // 停止运动模式
      stopWorkoutMode();
      break;
      
    default:
      Serial.println("未知命令");
      break;
  }
}

void updateBLEData() {
  // 更新步数
  int steps = stepDetector.getStepCount();
  stepCharacteristic.writeValue(steps);
  
  // 更新心率
  int heartRate = hrMonitor.getHeartRate();
  hrCharacteristic.writeValue(heartRate);
  
  // 更新电池电量
  int batteryLevel = battery.getPercentage();
  batteryCharacteristic.writeValue(batteryLevel);
}

void loop() {
  // 等待BLE连接
  BLEDevice central = BLE.central();
  
  if (central) {
    Serial.print("已连接到: ");
    Serial.println(central.address());
    
    while (central.connected()) {
      // 更新传感器数据
      stepDetector.update();
      hrMonitor.update();
      battery.update();
      
      // 更新BLE特征值
      updateBLEData();
      
      delay(1000);
    }
    
    Serial.println("已断开连接");
  }
}
```

### 6.2 数据传输优化

```cpp
class BLEDataManager {
private:
  // 数据缓冲区
  struct SensorData {
    uint32_t timestamp;
    int16_t steps;
    uint8_t heartRate;
    uint8_t battery;
  };
  
  const int BUFFER_SIZE = 100;
  SensorData dataBuffer[BUFFER_SIZE];
  int bufferIndex = 0;
  
  unsigned long lastSync = 0;
  const int SYNC_INTERVAL = 60000;  // 每分钟同步一次
  
public:
  void addData(int steps, int heartRate, int battery) {
    if (bufferIndex < BUFFER_SIZE) {
      dataBuffer[bufferIndex].timestamp = millis();
      dataBuffer[bufferIndex].steps = steps;
      dataBuffer[bufferIndex].heartRate = heartRate;
      dataBuffer[bufferIndex].battery = battery;
      bufferIndex++;
    }
  }
  
  void syncData() {
    if (millis() - lastSync < SYNC_INTERVAL) return;
    
    Serial.println("开始同步数据...");
    
    // 分批发送数据
    const int BATCH_SIZE = 10;
    for (int i = 0; i < bufferIndex; i += BATCH_SIZE) {
      int batchEnd = min(i + BATCH_SIZE, bufferIndex);
      sendDataBatch(i, batchEnd);
      delay(100);  // 避免BLE缓冲区溢出
    }
    
    // 清空缓冲区
    bufferIndex = 0;
    lastSync = millis();
    
    Serial.println("数据同步完成");
  }
  
  void sendDataBatch(int start, int end) {
    // 构造数据包
    byte packet[20];  // BLE最大20字节
    int packetIndex = 0;
    
    for (int i = start; i < end && packetIndex < 18; i++) {
      packet[packetIndex++] = dataBuffer[i].steps & 0xFF;
      packet[packetIndex++] = (dataBuffer[i].steps >> 8) & 0xFF;
      packet[packetIndex++] = dataBuffer[i].heartRate;
      packet[packetIndex++] = dataBuffer[i].battery;
    }
    
    // 发送数据包
    // 这里需要定义一个数据传输特征
    // dataCharacteristic.writeValue(packet, packetIndex);
  }
};
```

### 6.3 固件OTA升级

```cpp
#include <InternalFileSystem.h>
#include <Adafruit_LittleFS.h>

using namespace Adafruit_LittleFS_Namespace;

class OTAManager {
private:
  File otaFile;
  uint32_t totalSize = 0;
  uint32_t receivedSize = 0;
  bool isUpdating = false;
  
public:
  void startOTA(uint32_t fileSize) {
    Serial.println("开始OTA升级...");
    
    totalSize = fileSize;
    receivedSize = 0;
    isUpdating = true;
    
    // 创建临时文件
    InternalFS.remove("firmware.bin");
    otaFile = InternalFS.open("firmware.bin", FILE_O_WRITE);
    
    if (!otaFile) {
      Serial.println("创建OTA文件失败");
      isUpdating = false;
      return;
    }
  }
  
  void writeOTAData(byte* data, int length) {
    if (!isUpdating) return;
    
    otaFile.write(data, length);
    receivedSize += length;
    
    int progress = (receivedSize * 100) / totalSize;
    Serial.print("OTA进度: ");
    Serial.print(progress);
    Serial.println("%");
    
    // 显示进度
    displayOTAProgress(progress);
    
    if (receivedSize >= totalSize) {
      finishOTA();
    }
  }
  
  void finishOTA() {
    otaFile.close();
    isUpdating = false;
    
    Serial.println("OTA升级完成，准备重启...");
    
    // 验证固件
    if (verifyFirmware()) {
      Serial.println("固件验证成功");
      
      // 应用新固件
      applyFirmware();
      
      // 重启设备
      delay(1000);
      NVIC_SystemReset();
    } else {
      Serial.println("固件验证失败");
      InternalFS.remove("firmware.bin");
    }
  }
  
  bool verifyFirmware() {
    // 简单的CRC校验
    // 实际应用中应该使用更安全的验证方法
    return true;
  }
  
  void applyFirmware() {
    // 将新固件写入Flash
    // 这部分需要使用bootloader支持
    Serial.println("应用新固件...");
  }
  
  void displayOTAProgress(int progress) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(10, 10);
    display.print("Updating...");
    
    display.setCursor(10, 30);
    display.print(progress);
    display.print("%");
    
    // 进度条
    display.drawRect(10, 45, 108, 10, SSD1306_WHITE);
    int fillWidth = (progress * 106) / 100;
    display.fillRect(11, 46, fillWidth, 8, SSD1306_WHITE);
    
    display.display();
  }
};

OTAManager otaManager;
```


## 第七部分：移动应用开发

### 7.1 Android应用开发

#### 项目配置

```gradle
// app/build.gradle
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    
    // BLE库
    implementation 'no.nordicsemi.android:ble:2.6.1'
    
    // 图表库
    implementation 'com.github.PhilJay:MPAndroidChart:v3.1.0'
    
    // 数据库
    implementation 'androidx.room:room-runtime:2.5.2'
    annotationProcessor 'androidx.room:room-compiler:2.5.2'
}
```

#### BLE连接管理

```java
// BLEManager.java
public class BLEManager {
    private BluetoothAdapter bluetoothAdapter;
    private BluetoothGatt bluetoothGatt;
    private Context context;
    
    // 服务和特征UUID
    private static final UUID SERVICE_UUID = 
        UUID.fromString("19B10000-E8F2-537E-4F6C-D104768A1214");
    private static final UUID STEP_CHAR_UUID = 
        UUID.fromString("19B10001-E8F2-537E-4F6C-D104768A1214");
    private static final UUID HR_CHAR_UUID = 
        UUID.fromString("19B10002-E8F2-537E-4F6C-D104768A1214");
    
    public BLEManager(Context context) {
        this.context = context;
        BluetoothManager bluetoothManager = 
            (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = bluetoothManager.getAdapter();
    }
    
    public void scanDevices(ScanCallback callback) {
        BluetoothLeScanner scanner = bluetoothAdapter.getBluetoothLeScanner();
        
        ScanSettings settings = new ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build();
        
        List<ScanFilter> filters = new ArrayList<>();
        ScanFilter filter = new ScanFilter.Builder()
            .setServiceUuid(new ParcelUuid(SERVICE_UUID))
            .build();
        filters.add(filter);
        
        scanner.startScan(filters, settings, callback);
    }
    
    public void connect(String deviceAddress) {
        BluetoothDevice device = bluetoothAdapter.getRemoteDevice(deviceAddress);
        bluetoothGatt = device.connectGatt(context, false, gattCallback);
    }
    
    private final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.d("BLE", "已连接到设备");
                gatt.discoverServices();
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.d("BLE", "已断开连接");
            }
        }
        
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d("BLE", "服务发现成功");
                enableNotifications();
            }
        }
        
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, 
                                           BluetoothGattCharacteristic characteristic) {
            UUID uuid = characteristic.getUuid();
            
            if (uuid.equals(STEP_CHAR_UUID)) {
                int steps = characteristic.getIntValue(
                    BluetoothGattCharacteristic.FORMAT_UINT32, 0);
                onStepsUpdated(steps);
            } else if (uuid.equals(HR_CHAR_UUID)) {
                int heartRate = characteristic.getIntValue(
                    BluetoothGattCharacteristic.FORMAT_UINT8, 0);
                onHeartRateUpdated(heartRate);
            }
        }
    };
    
    private void enableNotifications() {
        BluetoothGattService service = bluetoothGatt.getService(SERVICE_UUID);
        
        // 启用步数通知
        BluetoothGattCharacteristic stepChar = 
            service.getCharacteristic(STEP_CHAR_UUID);
        bluetoothGatt.setCharacteristicNotification(stepChar, true);
        
        BluetoothGattDescriptor descriptor = 
            stepChar.getDescriptor(UUID.fromString(
                "00002902-0000-1000-8000-00805f9b34fb"));
        descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
        bluetoothGatt.writeDescriptor(descriptor);
        
        // 启用心率通知
        BluetoothGattCharacteristic hrChar = 
            service.getCharacteristic(HR_CHAR_UUID);
        bluetoothGatt.setCharacteristicNotification(hrChar, true);
    }
    
    public void sendCommand(byte command) {
        BluetoothGattService service = bluetoothGatt.getService(SERVICE_UUID);
        BluetoothGattCharacteristic controlChar = 
            service.getCharacteristic(CONTROL_CHAR_UUID);
        
        controlChar.setValue(new byte[]{command});
        bluetoothGatt.writeCharacteristic(controlChar);
    }
    
    private void onStepsUpdated(int steps) {
        // 更新UI
        Log.d("BLE", "步数: " + steps);
    }
    
    private void onHeartRateUpdated(int heartRate) {
        // 更新UI
        Log.d("BLE", "心率: " + heartRate);
    }
}
```

#### 主界面实现

```java
// MainActivity.java
public class MainActivity extends AppCompatActivity {
    private BLEManager bleManager;
    private TextView tvSteps, tvHeartRate, tvBattery;
    private LineChart chartHeartRate;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initViews();
        initBLE();
    }
    
    private void initViews() {
        tvSteps = findViewById(R.id.tv_steps);
        tvHeartRate = findViewById(R.id.tv_heart_rate);
        tvBattery = findViewById(R.id.tv_battery);
        chartHeartRate = findViewById(R.id.chart_heart_rate);
        
        setupChart();
    }
    
    private void setupChart() {
        chartHeartRate.getDescription().setEnabled(false);
        chartHeartRate.setTouchEnabled(true);
        chartHeartRate.setDragEnabled(true);
        chartHeartRate.setScaleEnabled(true);
        
        XAxis xAxis = chartHeartRate.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        
        YAxis leftAxis = chartHeartRate.getAxisLeft();
        leftAxis.setAxisMinimum(40f);
        leftAxis.setAxisMaximum(180f);
        
        chartHeartRate.getAxisRight().setEnabled(false);
    }
    
    private void initBLE() {
        bleManager = new BLEManager(this);
        
        // 扫描设备
        bleManager.scanDevices(new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                BluetoothDevice device = result.getDevice();
                if ("SmartBand".equals(device.getName())) {
                    bleManager.connect(device.getAddress());
                }
            }
        });
    }
    
    public void updateSteps(int steps) {
        runOnUiThread(() -> {
            tvSteps.setText(String.valueOf(steps));
        });
    }
    
    public void updateHeartRate(int heartRate) {
        runOnUiThread(() -> {
            tvHeartRate.setText(heartRate + " bpm");
            addHeartRateData(heartRate);
        });
    }
    
    private void addHeartRateData(int heartRate) {
        LineData data = chartHeartRate.getData();
        
        if (data == null) {
            data = new LineData();
            chartHeartRate.setData(data);
        }
        
        ILineDataSet set = data.getDataSetByIndex(0);
        
        if (set == null) {
            set = createSet();
            data.addDataSet(set);
        }
        
        data.addEntry(new Entry(set.getEntryCount(), heartRate), 0);
        data.notifyDataChanged();
        
        chartHeartRate.notifyDataSetChanged();
        chartHeartRate.setVisibleXRangeMaximum(50);
        chartHeartRate.moveViewToX(data.getEntryCount());
    }
    
    private LineDataSet createSet() {
        LineDataSet set = new LineDataSet(null, "心率");
        set.setAxisDependency(YAxis.AxisDependency.LEFT);
        set.setColor(Color.RED);
        set.setLineWidth(2f);
        set.setDrawCircles(false);
        set.setDrawValues(false);
        set.setMode(LineDataSet.Mode.CUBIC_BEZIER);
        return set;
    }
}
```

### 7.2 数据存储

```java
// 使用Room数据库
@Entity(tableName = "health_data")
public class HealthData {
    @PrimaryKey(autoGenerate = true)
    public int id;
    
    public long timestamp;
    public int steps;
    public int heartRate;
    public int battery;
    public int sleepMinutes;
}

@Dao
public interface HealthDataDao {
    @Insert
    void insert(HealthData data);
    
    @Query("SELECT * FROM health_data WHERE timestamp >= :startTime AND timestamp <= :endTime")
    List<HealthData> getDataInRange(long startTime, long endTime);
    
    @Query("SELECT SUM(steps) FROM health_data WHERE DATE(timestamp/1000, 'unixepoch') = DATE('now')")
    int getTodaySteps();
    
    @Query("SELECT AVG(heartRate) FROM health_data WHERE timestamp >= :startTime")
    float getAverageHeartRate(long startTime);
}

@Database(entities = {HealthData.class}, version = 1)
public abstract class AppDatabase extends RoomDatabase {
    public abstract HealthDataDao healthDataDao();
    
    private static AppDatabase instance;
    
    public static AppDatabase getInstance(Context context) {
        if (instance == null) {
            instance = Room.databaseBuilder(
                context.getApplicationContext(),
                AppDatabase.class,
                "health_database"
            ).build();
        }
        return instance;
    }
}
```


### 7.3 数据可视化

```java
// StatisticsActivity.java
public class StatisticsActivity extends AppCompatActivity {
    private BarChart chartSteps;
    private LineChart chartSleep;
    private AppDatabase database;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_statistics);
        
        database = AppDatabase.getInstance(this);
        
        chartSteps = findViewById(R.id.chart_steps);
        chartSleep = findViewById(R.id.chart_sleep);
        
        loadWeeklySteps();
        loadSleepData();
    }
    
    private void loadWeeklySteps() {
        new Thread(() -> {
            List<BarEntry> entries = new ArrayList<>();
            
            for (int i = 6; i >= 0; i--) {
                long dayStart = getStartOfDay(i);
                long dayEnd = getEndOfDay(i);
                
                List<HealthData> data = database.healthDataDao()
                    .getDataInRange(dayStart, dayEnd);
                
                int totalSteps = 0;
                for (HealthData d : data) {
                    totalSteps += d.steps;
                }
                
                entries.add(new BarEntry(6 - i, totalSteps));
            }
            
            runOnUiThread(() -> {
                BarDataSet dataSet = new BarDataSet(entries, "每日步数");
                dataSet.setColor(Color.BLUE);
                
                BarData barData = new BarData(dataSet);
                chartSteps.setData(barData);
                chartSteps.invalidate();
            });
        }).start();
    }
    
    private void loadSleepData() {
        new Thread(() -> {
            List<Entry> entries = new ArrayList<>();
            
            for (int i = 6; i >= 0; i--) {
                long dayStart = getStartOfDay(i);
                long dayEnd = getEndOfDay(i);
                
                List<HealthData> data = database.healthDataDao()
                    .getDataInRange(dayStart, dayEnd);
                
                int totalSleep = 0;
                for (HealthData d : data) {
                    totalSleep += d.sleepMinutes;
                }
                
                entries.add(new Entry(6 - i, totalSleep / 60.0f));
            }
            
            runOnUiThread(() -> {
                LineDataSet dataSet = new LineDataSet(entries, "睡眠时长(小时)");
                dataSet.setColor(Color.MAGENTA);
                dataSet.setLineWidth(2f);
                
                LineData lineData = new LineData(dataSet);
                chartSleep.setData(lineData);
                chartSleep.invalidate();
            });
        }).start();
    }
    
    private long getStartOfDay(int daysAgo) {
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.DAY_OF_YEAR, -daysAgo);
        calendar.set(Calendar.HOUR_OF_DAY, 0);
        calendar.set(Calendar.MINUTE, 0);
        calendar.set(Calendar.SECOND, 0);
        return calendar.getTimeInMillis();
    }
    
    private long getEndOfDay(int daysAgo) {
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.DAY_OF_YEAR, -daysAgo);
        calendar.set(Calendar.HOUR_OF_DAY, 23);
        calendar.set(Calendar.MINUTE, 59);
        calendar.set(Calendar.SECOND, 59);
        return calendar.getTimeInMillis();
    }
}
```

## 第八部分：系统集成与测试

### 8.1 完整固件代码

```cpp
// main.cpp - 完整的智能手环固件
#include <Wire.h>
#include <ArduinoBLE.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MPU6050.h>
#include <MAX30105.h>

// 全局对象
Adafruit_SSD1306 display(128, 64, &Wire, -1);
MPU6050 mpu;
MAX30105 particleSensor;

// 功能模块
StepDetector stepDetector;
HeartRateMonitor hrMonitor;
SleepMonitor sleepMonitor;
BatteryManager battery;
PowerManager powerMgr;
WearableUI ui(display);

// BLE服务
BLEService customService("19B10000-E8F2-537E-4F6C-D104768A1214");
BLEIntCharacteristic stepChar("19B10001-E8F2-537E-4F6C-D104768A1214", 
                              BLERead | BLENotify);
BLEIntCharacteristic hrChar("19B10002-E8F2-537E-4F6C-D104768A1214", 
                            BLERead | BLENotify);

// 定时器
unsigned long lastSensorUpdate = 0;
unsigned long lastUIUpdate = 0;
unsigned long lastBLEUpdate = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  // 初始化显示
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("显示初始化失败");
    while(1);
  }
  
  // 初始化传感器
  if (!mpu.testConnection()) {
    Serial.println("MPU6050初始化失败");
    while(1);
  }
  
  if (!particleSensor.begin()) {
    Serial.println("MAX30102初始化失败");
    while(1);
  }
  
  // 初始化BLE
  setupBLE();
  
  // 初始化电源管理
  powerMgr.init();
  
  // 显示启动画面
  showSplashScreen();
  
  Serial.println("系统初始化完成");
}

void loop() {
  unsigned long currentTime = millis();
  
  // 传感器数据更新 (50ms)
  if (currentTime - lastSensorUpdate >= 50) {
    updateSensors();
    lastSensorUpdate = currentTime;
  }
  
  // UI更新 (100ms)
  if (currentTime - lastUIUpdate >= 100) {
    ui.update();
    lastUIUpdate = currentTime;
  }
  
  // BLE数据更新 (1000ms)
  if (currentTime - lastBLEUpdate >= 1000) {
    updateBLE();
    lastBLEUpdate = currentTime;
  }
  
  // 电源管理
  powerMgr.update();
  
  // 处理按键
  handleButtons();
}

void updateSensors() {
  // 更新加速度计
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  float accelMagnitude = sqrt(
    pow(ax/16384.0, 2) + 
    pow(ay/16384.0, 2) + 
    pow(az/16384.0, 2)
  );
  stepDetector.addSample(accelMagnitude);
  
  // 更新心率
  hrMonitor.update();
  
  // 更新睡眠监测
  sleepMonitor.update();
  
  // 更新电池
  battery.update();
}

void updateBLE() {
  BLEDevice central = BLE.central();
  
  if (central && central.connected()) {
    stepChar.writeValue(stepDetector.getStepCount());
    hrChar.writeValue(hrMonitor.getHeartRate());
  }
}

void handleButtons() {
  static unsigned long lastPress = 0;
  
  if (digitalRead(BUTTON_PIN) == LOW && 
      millis() - lastPress > 200) {
    
    ui.nextPage();
    powerMgr.onActivity();
    vibrate(30);
    
    lastPress = millis();
  }
}

void showSplashScreen() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 20);
  display.print("Smart");
  display.setCursor(10, 40);
  display.print("Band");
  display.display();
  delay(2000);
}

void vibrate(int duration) {
  digitalWrite(VIBRATION_PIN, HIGH);
  delay(duration);
  digitalWrite(VIBRATION_PIN, LOW);
}
```

### 8.2 功能测试

#### 计步测试

```cpp
void testStepDetection() {
  Serial.println("=== 计步测试 ===");
  
  // 模拟行走
  for (int i = 0; i < 100; i++) {
    // 模拟加速度变化
    float accel = 1.0 + sin(i * 0.3) * 0.5;
    stepDetector.addSample(accel);
    delay(500);  // 模拟步态间隔
  }
  
  int steps = stepDetector.getStepCount();
  Serial.print("检测到步数: ");
  Serial.println(steps);
  
  // 验证精度
  float accuracy = (steps / 100.0) * 100;
  Serial.print("精度: ");
  Serial.print(accuracy);
  Serial.println("%");
}
```

#### 心率测试

```cpp
void testHeartRate() {
  Serial.println("=== 心率测试 ===");
  Serial.println("请将手指放在传感器上...");
  
  int validReadings = 0;
  int totalReadings = 0;
  
  for (int i = 0; i < 30; i++) {
    hrMonitor.update();
    
    if (hrMonitor.isFingerDetected()) {
      int hr = hrMonitor.getHeartRate();
      if (hr > 0) {
        Serial.print("心率: ");
        Serial.println(hr);
        validReadings++;
      }
    }
    
    totalReadings++;
    delay(1000);
  }
  
  float successRate = (validReadings / (float)totalReadings) * 100;
  Serial.print("成功率: ");
  Serial.print(successRate);
  Serial.println("%");
}
```

#### 功耗测试

```cpp
void testPowerConsumption() {
  Serial.println("=== 功耗测试 ===");
  
  // 测试活动模式功耗
  Serial.println("活动模式...");
  powerMgr.enterActiveMode();
  delay(10000);
  
  // 测试空闲模式功耗
  Serial.println("空闲模式...");
  powerMgr.enterIdleMode();
  delay(10000);
  
  // 测试深度睡眠功耗
  Serial.println("深度睡眠模式...");
  // powerMgr.enterDeepSleep();  // 注意：会导致设备重启
  
  Serial.println("功耗测试完成");
}
```

### 8.3 性能优化

```cpp
// 优化建议

// 1. 减少I2C通信频率
void optimizeI2C() {
  // 批量读取传感器数据
  Wire.setClock(400000);  // 使用快速I2C
  
  // 使用DMA传输（如果支持）
}

// 2. 优化算法
void optimizeAlgorithms() {
  // 使用整数运算代替浮点运算
  // 使用查找表代替复杂计算
  // 减少不必要的计算
}

// 3. 优化显示刷新
void optimizeDisplay() {
  // 只更新变化的区域
  // 降低刷新率
  // 使用双缓冲
}

// 4. 优化BLE通信
void optimizeBLE() {
  // 使用连接参数优化
  BLE.setConnectionInterval(100, 200);  // 100-200ms
  
  // 批量发送数据
  // 使用数据压缩
}
```


## 第九部分：高级功能扩展

### 9.1 运动模式

```cpp
class WorkoutMode {
private:
  enum WorkoutType {
    RUNNING,
    WALKING,
    CYCLING,
    SWIMMING
  };
  
  WorkoutType currentType = RUNNING;
  bool isActive = false;
  unsigned long startTime = 0;
  int totalSteps = 0;
  float totalDistance = 0;
  int caloriesBurned = 0;
  
public:
  void start(WorkoutType type) {
    currentType = type;
    isActive = true;
    startTime = millis();
    totalSteps = 0;
    totalDistance = 0;
    caloriesBurned = 0;
    
    Serial.println("运动模式已启动");
  }
  
  void stop() {
    isActive = false;
    
    // 保存运动记录
    saveWorkoutRecord();
    
    Serial.println("运动模式已停止");
  }
  
  void update(int steps, int heartRate) {
    if (!isActive) return;
    
    totalSteps = steps;
    
    // 计算距离（假设步长70cm）
    totalDistance = totalSteps * 0.7 / 1000.0;  // km
    
    // 计算卡路里（简化公式）
    // 卡路里 = 体重(kg) × 距离(km) × 1.036
    caloriesBurned = 70 * totalDistance * 1.036;
    
    // 显示运动数据
    displayWorkoutData();
  }
  
  void displayWorkoutData() {
    display.clearDisplay();
    display.setTextSize(1);
    
    // 运动时长
    unsigned long duration = (millis() - startTime) / 1000;
    int minutes = duration / 60;
    int seconds = duration % 60;
    
    display.setCursor(10, 5);
    display.print("Time: ");
    display.print(minutes);
    display.print(":");
    if (seconds < 10) display.print("0");
    display.print(seconds);
    
    // 距离
    display.setCursor(10, 20);
    display.print("Dist: ");
    display.print(totalDistance, 2);
    display.print(" km");
    
    // 步数
    display.setCursor(10, 35);
    display.print("Steps: ");
    display.print(totalSteps);
    
    // 卡路里
    display.setCursor(10, 50);
    display.print("Cal: ");
    display.print(caloriesBurned);
    display.print(" kcal");
    
    display.display();
  }
  
  void saveWorkoutRecord() {
    // 保存到Flash或通过BLE发送到手机
    Serial.println("保存运动记录...");
    Serial.print("时长: ");
    Serial.print((millis() - startTime) / 60000);
    Serial.println(" 分钟");
    Serial.print("距离: ");
    Serial.print(totalDistance);
    Serial.println(" km");
    Serial.print("卡路里: ");
    Serial.print(caloriesBurned);
    Serial.println(" kcal");
  }
};

WorkoutMode workout;
```

### 9.2 消息通知

```cpp
class NotificationManager {
private:
  struct Notification {
    String title;
    String message;
    unsigned long timestamp;
  };
  
  const int MAX_NOTIFICATIONS = 10;
  Notification notifications[MAX_NOTIFICATIONS];
  int notificationCount = 0;
  
public:
  void addNotification(String title, String message) {
    if (notificationCount < MAX_NOTIFICATIONS) {
      notifications[notificationCount].title = title;
      notifications[notificationCount].message = message;
      notifications[notificationCount].timestamp = millis();
      notificationCount++;
      
      // 显示通知
      showNotification(title, message);
      
      // 振动提醒
      vibrate(100);
      delay(100);
      vibrate(100);
    }
  }
  
  void showNotification(String title, String message) {
    display.clearDisplay();
    
    // 标题
    display.setTextSize(1);
    display.setCursor(5, 5);
    display.print(title);
    
    // 分隔线
    display.drawLine(0, 15, 128, 15, SSD1306_WHITE);
    
    // 消息内容（自动换行）
    display.setTextSize(1);
    int y = 20;
    int maxWidth = 120;
    int charWidth = 6;
    int charsPerLine = maxWidth / charWidth;
    
    for (int i = 0; i < message.length(); i += charsPerLine) {
      String line = message.substring(i, min(i + charsPerLine, 
                                             (int)message.length()));
      display.setCursor(5, y);
      display.print(line);
      y += 10;
      
      if (y > 55) break;  // 防止溢出
    }
    
    display.display();
    
    // 5秒后返回主界面
    delay(5000);
  }
  
  void clearNotifications() {
    notificationCount = 0;
  }
  
  int getNotificationCount() {
    return notificationCount;
  }
};

NotificationManager notificationMgr;

// BLE接收通知
void onNotificationReceived(byte* data, int length) {
  // 解析通知数据
  // 格式: [type][title_length][title][message]
  
  byte type = data[0];
  byte titleLength = data[1];
  
  String title = "";
  for (int i = 0; i < titleLength; i++) {
    title += (char)data[2 + i];
  }
  
  String message = "";
  for (int i = 2 + titleLength; i < length; i++) {
    message += (char)data[i];
  }
  
  notificationMgr.addNotification(title, message);
}
```

### 9.3 天气显示

```cpp
class WeatherDisplay {
private:
  struct Weather {
    int temperature;
    int humidity;
    String condition;  // "sunny", "cloudy", "rainy"
    unsigned long lastUpdate;
  };
  
  Weather currentWeather;
  
public:
  void updateWeather(int temp, int humidity, String condition) {
    currentWeather.temperature = temp;
    currentWeather.humidity = humidity;
    currentWeather.condition = condition;
    currentWeather.lastUpdate = millis();
  }
  
  void display() {
    display.clearDisplay();
    
    // 天气图标
    drawWeatherIcon(currentWeather.condition);
    
    // 温度
    display.setTextSize(2);
    display.setCursor(50, 15);
    display.print(currentWeather.temperature);
    display.print("C");
    
    // 湿度
    display.setTextSize(1);
    display.setCursor(50, 40);
    display.print("Humidity: ");
    display.print(currentWeather.humidity);
    display.print("%");
    
    display.display();
  }
  
  void drawWeatherIcon(String condition) {
    // 简化的天气图标
    if (condition == "sunny") {
      // 太阳图标
      display.fillCircle(20, 30, 10, SSD1306_WHITE);
      for (int i = 0; i < 8; i++) {
        float angle = i * PI / 4;
        int x1 = 20 + cos(angle) * 12;
        int y1 = 30 + sin(angle) * 12;
        int x2 = 20 + cos(angle) * 18;
        int y2 = 30 + sin(angle) * 18;
        display.drawLine(x1, y1, x2, y2, SSD1306_WHITE);
      }
    } else if (condition == "cloudy") {
      // 云图标
      display.fillCircle(15, 30, 8, SSD1306_WHITE);
      display.fillCircle(25, 30, 10, SSD1306_WHITE);
      display.fillRect(10, 30, 20, 8, SSD1306_WHITE);
    } else if (condition == "rainy") {
      // 雨图标
      display.fillCircle(15, 25, 8, SSD1306_WHITE);
      display.fillCircle(25, 25, 10, SSD1306_WHITE);
      display.fillRect(10, 25, 20, 8, SSD1306_WHITE);
      
      // 雨滴
      for (int i = 0; i < 3; i++) {
        display.drawLine(12 + i*8, 35, 10 + i*8, 45, SSD1306_WHITE);
      }
    }
  }
};

WeatherDisplay weatherDisplay;
```

### 9.4 闹钟功能

```cpp
class AlarmManager {
private:
  struct Alarm {
    int hour;
    int minute;
    bool enabled;
    bool repeat[7];  // 周一到周日
  };
  
  const int MAX_ALARMS = 5;
  Alarm alarms[MAX_ALARMS];
  int alarmCount = 0;
  
public:
  void addAlarm(int hour, int minute, bool* repeatDays) {
    if (alarmCount < MAX_ALARMS) {
      alarms[alarmCount].hour = hour;
      alarms[alarmCount].minute = minute;
      alarms[alarmCount].enabled = true;
      
      for (int i = 0; i < 7; i++) {
        alarms[alarmCount].repeat[i] = repeatDays[i];
      }
      
      alarmCount++;
    }
  }
  
  void checkAlarms() {
    // 获取当前时间（需要RTC模块）
    int currentHour = 12;  // 示例
    int currentMinute = 30;
    int currentDay = 1;  // 周一
    
    for (int i = 0; i < alarmCount; i++) {
      if (alarms[i].enabled &&
          alarms[i].hour == currentHour &&
          alarms[i].minute == currentMinute &&
          alarms[i].repeat[currentDay]) {
        
        triggerAlarm(i);
      }
    }
  }
  
  void triggerAlarm(int index) {
    Serial.print("闹钟触发: ");
    Serial.println(index);
    
    // 显示闹钟界面
    displayAlarm();
    
    // 振动提醒
    for (int i = 0; i < 5; i++) {
      vibrate(200);
      delay(300);
    }
  }
  
  void displayAlarm() {
    display.clearDisplay();
    display.setTextSize(2);
    display.setCursor(20, 20);
    display.print("ALARM");
    display.setTextSize(1);
    display.setCursor(30, 45);
    display.print("Press to stop");
    display.display();
  }
  
  void disableAlarm(int index) {
    if (index < alarmCount) {
      alarms[index].enabled = false;
    }
  }
};

AlarmManager alarmMgr;
```

## 总结

通过本教程的学习，你已经掌握了：

✅ **硬件设计**
- 可穿戴设备的系统架构
- 传感器选型和集成
- 电源管理和充电电路

✅ **固件开发**
- 传感器数据采集和处理
- 计步、心率、睡眠监测算法
- 低功耗设计和优化
- BLE蓝牙通信协议

✅ **显示界面**
- OLED显示驱动
- 多页面UI设计
- 动画效果实现

✅ **移动应用**
- Android BLE通信
- 数据存储和管理
- 数据可视化

✅ **高级功能**
- 运动模式
- 消息通知
- 天气显示
- 闹钟功能

## 实践项目

为了巩固所学知识，建议完成以下项目：

### 项目1：基础智能手环
**要求**：
- 实现计步功能
- 实现心率监测
- OLED显示界面
- BLE数据同步

### 项目2：运动手环
**要求**：
- 多种运动模式
- GPS轨迹记录（需要GPS模块）
- 运动数据分析
- 目标设定和提醒

### 项目3：健康监测手环
**要求**：
- 24小时心率监测
- 血氧饱和度测量
- 睡眠质量分析
- 健康报告生成

## 进阶学习方向

### 技术深化

1. **更多传感器**
   - GPS定位
   - 气压计（海拔测量）
   - 环境光传感器
   - 皮肤温度传感器

2. **高级算法**
   - 机器学习算法
   - 运动识别
   - 异常检测
   - 个性化建议

3. **云端服务**
   - 数据云端存储
   - 多设备同步
   - 社交功能
   - 数据分析服务

4. **硬件优化**
   - PCB设计
   - 3D打印外壳
   - 防水设计
   - 无线充电

### 商业化方向

1. **产品化**
   - 工业设计
   - 量产制造
   - 质量控制
   - 认证测试

2. **软件生态**
   - iOS应用开发
   - 第三方应用集成
   - 开放API
   - 开发者社区

3. **市场定位**
   - 运动健身市场
   - 医疗健康市场
   - 老年人市场
   - 儿童市场

## 常见问题解答（FAQ）

**Q1：如何提高计步精度？**

A：
- 使用更好的算法（峰值检测、机器学习）
- 多传感器融合（加速度计+陀螺仪）
- 用户校准功能
- 收集真实数据进行训练

**Q2：如何延长续航时间？**

A：
- 优化功耗设计（低功耗MCU、睡眠模式）
- 降低传感器采样率
- 优化显示刷新
- 使用更大容量电池

**Q3：心率测量不准确怎么办？**

A：
- 确保传感器紧贴皮肤
- 优化LED电流设置
- 使用更好的算法
- 多次测量取平均值

**Q4：如何实现防水？**

A：
- 使用防水外壳
- 密封圈设计
- 防水胶涂覆
- 达到IP67或IP68等级

**Q5：如何添加GPS功能？**

A：
- 集成GPS模块（如NEO-6M）
- 注意功耗增加
- 优化定位算法
- 考虑使用A-GPS

## 学习资源

### 推荐书籍
1. 《可穿戴设备设计与开发》
2. 《低功耗蓝牙开发实战》
3. 《嵌入式系统低功耗设计》
4. 《生物医学信号处理》

### 在线资源
1. Nordic官方文档：https://www.nordicsemi.com/
2. Adafruit学习系统：https://learn.adafruit.com/
3. Arduino论坛：https://forum.arduino.cc/
4. GitHub开源项目

### 开源项目
1. Bangle.js：开源智能手表
2. PineTime：开源智能手表
3. Watchy：E-ink智能手表
4. OpenHAK：开源健康追踪器

### 社区论坛
1. 可穿戴设备开发者社区
2. Nordic开发者论坛
3. 嵌入式系统论坛
4. GitHub相关项目

## 下一步学习建议

完成本教程后，建议继续学习：

1. **[智能音箱开发技术](../intermediate/01-smart-speaker.html)** - 学习语音交互技术
2. **[生物信号处理基础](../../03-medical-devices/beginner/02-biosignal-processing.html)** - 深入学习信号处理
3. **低功耗设计** - 优化功耗设计

## 参考资料

1. Bluetooth SIG - BLE规范
2. IEEE 802.15.4 - 低功耗无线标准
3. 《可穿戴设备白皮书》
4. Nordic nRF52系列数据手册
5. MAX30102心率传感器应用笔记

---

**版权声明**：本教程内容仅供学习参考，实际项目应用请遵循相关安全规范和标准。

**反馈与建议**：如果你在学习过程中遇到问题或有改进建议，欢迎通过评论区反馈！

**最后更新**：2024-01-15
