---
title: "舵机控制与应用技术详解"
description: "深入学习舵机的工作原理、PWM信号控制、角度控制技术，掌握单舵机和多舵机协调控制，实现机械臂等实际应用"
slug: "servo-motor-control-guide"

# 分类信息
domain: "底层硬件层"
module: "执行器控制"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 舵机
  - PWM控制
  - 角度控制
  - 机械臂
  - SG90
  - MG996R
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 35
difficulty_score: 2

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
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
  - 舵机控制
  - PWM信号
  - 角度控制
  - 多舵机协调
  - 机械臂控制
cover_image: ""
---

# 舵机控制与应用技术详解

## 概述

舵机（Servo Motor）是一种能够精确控制角度的执行器，广泛应用于机器人、航模、机械臂等领域。与普通直流电机不同，舵机内部集成了控制电路、减速齿轮和位置反馈系统，只需要一个简单的PWM信号就能实现精确的角度控制。

本文将深入讲解舵机的工作原理、控制方法和实际应用，帮助你快速掌握舵机控制技术。

### 你将学到

- 舵机的内部结构和工作原理
- PWM信号与角度的对应关系
- 单舵机和多舵机的控制方法
- 舵机在机械臂中的协调控制
- 常见问题的解决方案

### 适用场景

- 机器人关节控制
- 航模舵面控制
- 云台控制
- 机械臂设计
- 自动化装置

## 舵机基础知识

### 舵机的内部结构

舵机主要由以下几个部分组成：


```
┌─────────────────────────────────┐
│         舵机内部结构              │
│                                 │
│  ┌──────┐    ┌──────┐          │
│  │ 控制 │───>│ 电机 │          │
│  │ 电路 │    └──┬───┘          │
│  └──┬───┘       │              │
│     │           │              │
│     │      ┌────▼────┐         │
│     │      │ 减速齿轮 │         │
│     │      └────┬────┘         │
│     │           │              │
│     │      ┌────▼────┐         │
│     └──────│ 电位器  │         │
│            │(位置反馈)│         │
│            └─────────┘         │
│                                 │
│  输入: PWM信号                   │
│  输出: 精确角度                  │
└─────────────────────────────────┘
```

**各部分功能**：

1. **控制电路**：接收PWM信号，比较目标位置和当前位置，驱动电机
2. **直流电机**：提供动力，驱动齿轮转动
3. **减速齿轮组**：降低转速，增大扭矩，提高精度
4. **电位器**：检测输出轴的实际位置，提供反馈信号
5. **输出轴**：连接负载，实现角度控制


### 舵机的工作原理

舵机采用**闭环控制**系统：

1. **接收PWM信号**：控制电路接收来自MCU的PWM信号
2. **解析目标角度**：根据PWM脉宽计算目标角度
3. **读取当前角度**：通过电位器获取当前输出轴角度
4. **计算误差**：比较目标角度和当前角度
5. **驱动电机**：根据误差驱动电机正转或反转
6. **到达目标**：当误差足够小时，停止电机

这个过程持续进行，形成一个**负反馈控制回路**，确保输出轴始终保持在目标角度。

### 常见舵机类型

| 类型 | 角度范围 | 扭矩 | 速度 | 应用场景 |
|------|---------|------|------|---------|
| **微型舵机** | 180° | 1-2kg·cm | 0.1s/60° | 小型机器人、航模 |
| **标准舵机** | 180° | 3-10kg·cm | 0.15s/60° | 机械臂、云台 |
| **大扭矩舵机** | 180° | 15-35kg·cm | 0.2s/60° | 重载机械臂 |
| **数字舵机** | 180° | 10-20kg·cm | 0.08s/60° | 高精度应用 |
| **360°舵机** | 连续旋转 | 2-5kg·cm | 可调速 | 轮式机器人 |


**常用舵机型号**：

- **SG90**：9g微型舵机，1.8kg·cm，180°，价格低廉
- **MG90S**：金属齿轮版SG90，更耐用
- **MG996R**：标准舵机，11kg·cm，180°，性价比高
- **DS3218**：数字舵机，20kg·cm，高精度
- **FS90R**：360°连续旋转舵机

### 舵机引脚说明

舵机通常有三根线：

| 线色 | 功能 | 说明 |
|------|------|------|
| **红色** | VCC | 电源正极（4.8V-6V） |
| **棕色/黑色** | GND | 电源负极 |
| **橙色/黄色** | Signal | PWM控制信号 |

⚠️ **注意**：不同品牌的舵机线色可能不同，使用前请查看数据手册。


## PWM信号控制原理

### PWM信号参数

舵机通过PWM信号的**脉宽**（高电平持续时间）来控制角度：

```
PWM周期: 20ms (50Hz)
        
        ┌─────┐                    ┌─────┐
        │     │                    │     │
信号 ────┘     └────────────────────┘     └────
        
        ├─────┤                    
        脉宽                        
        (0.5ms - 2.5ms)            
        
        ├──────────────────────────┤
                 周期 (20ms)
```

**标准PWM参数**：

| 脉宽 | 角度 | 说明 |
|------|------|------|
| 0.5ms | 0° | 最小角度（左极限） |
| 1.0ms | 45° | 四分之一位置 |
| 1.5ms | 90° | 中间位置 |
| 2.0ms | 135° | 四分之三位置 |
| 2.5ms | 180° | 最大角度（右极限） |


### 角度与脉宽的计算

**线性关系公式**：

```
脉宽(ms) = 0.5 + (角度 / 180) × 2.0
角度(°) = (脉宽(ms) - 0.5) / 2.0 × 180
```

**示例计算**：

- 60°角度：脉宽 = 0.5 + (60/180) × 2.0 = 1.17ms
- 120°角度：脉宽 = 0.5 + (120/180) × 2.0 = 1.83ms

**占空比计算**（用于PWM配置）：

```
占空比 = 脉宽 / 周期 × 100%

示例：
- 0°:   占空比 = 0.5ms / 20ms × 100% = 2.5%
- 90°:  占空比 = 1.5ms / 20ms × 100% = 7.5%
- 180°: 占空比 = 2.5ms / 20ms × 100% = 12.5%
```

### 不同舵机的差异

⚠️ **重要提示**：不同品牌和型号的舵机，脉宽范围可能略有差异：

- **标准舵机**：0.5ms - 2.5ms（180°）
- **某些舵机**：0.6ms - 2.4ms（180°）
- **数字舵机**：0.5ms - 2.5ms（更精确）

建议在实际使用时进行**校准测试**，找出准确的脉宽范围。


## Arduino舵机控制

### 使用Servo库（推荐）

Arduino提供了专门的Servo库，简化舵机控制：

```cpp
#include <Servo.h>

Servo myServo;  // 创建舵机对象

void setup() {
  myServo.attach(9);  // 连接到D9引脚
  Serial.begin(9600);
}

void loop() {
  // 方法1：直接设置角度（0-180°）
  myServo.write(0);    // 转到0°
  delay(1000);
  
  myServo.write(90);   // 转到90°
  delay(1000);
  
  myServo.write(180);  // 转到180°
  delay(1000);
  
  // 方法2：设置脉宽（微秒）
  myServo.writeMicroseconds(1500);  // 1.5ms = 90°
  delay(1000);
}
```

**Servo库常用函数**：

| 函数 | 功能 | 参数 |
|------|------|------|
| `attach(pin)` | 绑定引脚 | 引脚号 |
| `write(angle)` | 设置角度 | 0-180° |
| `writeMicroseconds(us)` | 设置脉宽 | 500-2500μs |
| `read()` | 读取当前角度 | 返回0-180° |
| `attached()` | 检查是否绑定 | 返回true/false |
| `detach()` | 解除绑定 | 无 |


### 平滑角度控制

直接跳转到目标角度可能导致动作过快，使用循环实现平滑过渡：

```cpp
#include <Servo.h>

Servo myServo;
int currentAngle = 90;  // 当前角度

void setup() {
  myServo.attach(9);
  myServo.write(currentAngle);
  Serial.begin(9600);
}

// 平滑移动到目标角度
void smoothMove(int targetAngle, int stepDelay) {
  if (targetAngle > currentAngle) {
    // 正向移动
    for (int angle = currentAngle; angle <= targetAngle; angle++) {
      myServo.write(angle);
      delay(stepDelay);
    }
  } else {
    // 反向移动
    for (int angle = currentAngle; angle >= targetAngle; angle--) {
      myServo.write(angle);
      delay(stepDelay);
    }
  }
  currentAngle = targetAngle;
}

void loop() {
  smoothMove(180, 15);  // 移动到180°，每步延时15ms
  delay(1000);
  
  smoothMove(0, 15);    // 移动到0°
  delay(1000);
}
```


### 串口控制舵机

通过串口发送角度值控制舵机：

```cpp
#include <Servo.h>

Servo myServo;

void setup() {
  myServo.attach(9);
  myServo.write(90);  // 初始位置
  
  Serial.begin(9600);
  Serial.println("Servo Control Ready");
  Serial.println("Enter angle (0-180):");
}

void loop() {
  if (Serial.available() > 0) {
    int angle = Serial.parseInt();  // 读取整数
    
    // 限制角度范围
    if (angle >= 0 && angle <= 180) {
      myServo.write(angle);
      Serial.print("Moved to: ");
      Serial.print(angle);
      Serial.println("°");
    } else {
      Serial.println("Invalid angle! (0-180)");
    }
  }
}
```

**使用方法**：
1. 打开串口监视器（波特率9600）
2. 输入角度值（如：90）
3. 按回车发送
4. 观察舵机转动


## 多舵机协调控制

### 控制多个舵机

Arduino Uno最多可以同时控制12个舵机（使用Servo库）：

```cpp
#include <Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;

void setup() {
  servo1.attach(9);   // 舵机1连接D9
  servo2.attach(10);  // 舵机2连接D10
  servo3.attach(11);  // 舵机3连接D11
  
  // 初始化到中间位置
  servo1.write(90);
  servo2.write(90);
  servo3.write(90);
  
  Serial.begin(9600);
}

void loop() {
  // 同时控制三个舵机
  moveAllServos(0, 90, 180);
  delay(2000);
  
  moveAllServos(180, 90, 0);
  delay(2000);
}

// 同时移动所有舵机
void moveAllServos(int angle1, int angle2, int angle3) {
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);
  
  Serial.print("Servos: ");
  Serial.print(angle1);
  Serial.print("°, ");
  Serial.print(angle2);
  Serial.print("°, ");
  Serial.print(angle3);
  Serial.println("°");
}
```


### 多舵机同步平滑移动

实现多个舵机同时平滑移动到目标位置：

```cpp
#include <Servo.h>

const int SERVO_COUNT = 3;
Servo servos[SERVO_COUNT];
int currentAngles[SERVO_COUNT] = {90, 90, 90};

void setup() {
  servos[0].attach(9);
  servos[1].attach(10);
  servos[2].attach(11);
  
  // 初始化位置
  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].write(currentAngles[i]);
  }
  
  Serial.begin(9600);
}

// 多舵机同步平滑移动
void smoothMoveAll(int targetAngles[], int totalTime) {
  int steps = 50;  // 分50步完成
  int stepDelay = totalTime / steps;
  
  // 计算每步的增量
  float increments[SERVO_COUNT];
  for (int i = 0; i < SERVO_COUNT; i++) {
    increments[i] = (targetAngles[i] - currentAngles[i]) / (float)steps;
  }
  
  // 执行移动
  for (int step = 0; step < steps; step++) {
    for (int i = 0; i < SERVO_COUNT; i++) {
      int angle = currentAngles[i] + (int)(increments[i] * (step + 1));
      servos[i].write(angle);
    }
    delay(stepDelay);
  }
  
  // 更新当前角度
  for (int i = 0; i < SERVO_COUNT; i++) {
    currentAngles[i] = targetAngles[i];
  }
}

void loop() {
  int pose1[] = {0, 90, 180};
  smoothMoveAll(pose1, 2000);  // 2秒内移动到pose1
  delay(1000);
  
  int pose2[] = {180, 90, 0};
  smoothMoveAll(pose2, 2000);  // 2秒内移动到pose2
  delay(1000);
}
```


## 机械臂应用示例

### 简单三自由度机械臂

使用三个舵机实现基础机械臂控制：

```cpp
#include <Servo.h>

// 机械臂舵机
Servo baseServo;    // 底座旋转
Servo shoulderServo; // 肩部
Servo elbowServo;    // 肘部

// 当前角度
int baseAngle = 90;
int shoulderAngle = 90;
int elbowAngle = 90;

void setup() {
  baseServo.attach(9);
  shoulderServo.attach(10);
  elbowServo.attach(11);
  
  // 初始化到安全位置
  moveToPosition(90, 90, 90, 1000);
  
  Serial.begin(9600);
  Serial.println("Robot Arm Control");
  Serial.println("Commands: b<angle> s<angle> e<angle>");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    int angle = Serial.parseInt();
    
    switch(cmd) {
      case 'b':  // 底座
        if (angle >= 0 && angle <= 180) {
          baseAngle = angle;
          baseServo.write(angle);
          Serial.print("Base: ");
          Serial.println(angle);
        }
        break;
        
      case 's':  // 肩部
        if (angle >= 0 && angle <= 180) {
          shoulderAngle = angle;
          shoulderServo.write(angle);
          Serial.print("Shoulder: ");
          Serial.println(angle);
        }
        break;
        
      case 'e':  // 肘部
        if (angle >= 0 && angle <= 180) {
          elbowAngle = angle;
          elbowServo.write(angle);
          Serial.print("Elbow: ");
          Serial.println(angle);
        }
        break;
    }
  }
}

// 移动到指定位置（带时间控制）
void moveToPosition(int base, int shoulder, int elbow, int duration) {
  // 简化版：同时移动所有关节
  baseServo.write(base);
  shoulderServo.write(shoulder);
  elbowServo.write(elbow);
  
  baseAngle = base;
  shoulderAngle = shoulder;
  elbowAngle = elbow;
  
  delay(duration);
}
```


### 预设动作序列

定义一组预设动作，实现机械臂的自动化操作：

```cpp
// 动作结构体
struct ArmPose {
  int base;
  int shoulder;
  int elbow;
  int duration;  // 移动时间(ms)
};

// 预设动作序列
ArmPose sequence[] = {
  {90, 90, 90, 1000},    // 初始位置
  {45, 60, 120, 2000},   // 动作1
  {135, 60, 120, 2000},  // 动作2
  {90, 120, 60, 2000},   // 动作3
  {90, 90, 90, 2000}     // 回到初始位置
};

int sequenceLength = sizeof(sequence) / sizeof(ArmPose);

void executeSequence() {
  Serial.println("Executing sequence...");
  
  for (int i = 0; i < sequenceLength; i++) {
    Serial.print("Step ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(sequence[i].base);
    Serial.print(", ");
    Serial.print(sequence[i].shoulder);
    Serial.print(", ");
    Serial.println(sequence[i].elbow);
    
    moveToPosition(
      sequence[i].base,
      sequence[i].shoulder,
      sequence[i].elbow,
      sequence[i].duration
    );
    
    delay(500);  // 每个动作之间暂停
  }
  
  Serial.println("Sequence complete!");
}
```


## STM32舵机控制

### 使用HAL库PWM

STM32通过定时器PWM输出控制舵机：

```c
// STM32 HAL库版本
// 假设使用TIM2的CH1（PA0）输出PWM

// 定时器句柄（在main.c中初始化）
extern TIM_HandleTypeDef htim2;

// 舵机角度转PWM值
// ARR=20000, PSC配置为1ms计数1000次
// 脉宽范围：500-2500 (0.5ms-2.5ms)
uint16_t angleToP WM(uint8_t angle) {
    // 限制角度范围
    if (angle > 180) angle = 180;
    
    // 计算PWM值：500 + (angle/180) * 2000
    uint16_t pwm = 500 + (angle * 2000) / 180;
    return pwm;
}

// 设置舵机角度
void Servo_SetAngle(uint8_t angle) {
    uint16_t pwm = angleToPWM(angle);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pwm);
}

// 初始化舵机
void Servo_Init(void) {
    // 启动PWM输出
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    
    // 设置到中间位置
    Servo_SetAngle(90);
}

// 平滑移动
void Servo_SmoothMove(uint8_t targetAngle, uint16_t duration) {
    static uint8_t currentAngle = 90;
    
    int steps = 50;
    int stepDelay = duration / steps;
    float increment = (targetAngle - currentAngle) / (float)steps;
    
    for (int i = 0; i < steps; i++) {
        uint8_t angle = currentAngle + (uint8_t)(increment * (i + 1));
        Servo_SetAngle(angle);
        HAL_Delay(stepDelay);
    }
    
    currentAngle = targetAngle;
}
```


**STM32CubeMX配置要点**：

1. **定时器配置**：
   - 选择TIM2，模式设为PWM Generation CH1
   - 设置PSC（预分频器）和ARR（自动重装载值）
   - 目标：PWM周期20ms（50Hz）

2. **计算示例**（假设APB1时钟72MHz）：
   ```
   PWM频率 = 72MHz / ((PSC+1) * (ARR+1))
   50Hz = 72MHz / ((PSC+1) * (ARR+1))
   
   选择：PSC = 71, ARR = 19999
   验证：72MHz / (72 * 20000) = 50Hz ✓
   
   此时计数器每计数1，时间为1μs
   脉宽500 = 0.5ms, 脉宽2500 = 2.5ms
   ```

3. **GPIO配置**：
   - PA0设为TIM2_CH1（Alternate Function）
   - 无需上拉/下拉电阻


## 电源与接线注意事项

### 电源要求

舵机对电源有较高要求：

**电压**：
- 标准舵机：4.8V - 6V
- 数字舵机：6V - 7.4V
- 大扭矩舵机：6V - 7.4V

**电流**：
- 空载：50-100mA
- 负载：200-800mA
- 堵转：可达1-2A

⚠️ **重要提示**：
1. **不要用Arduino的5V引脚直接供电**（电流不足）
2. **使用独立电源**（如5V/2A电源适配器或电池）
3. **多个舵机需要更大电流**（每个舵机按500mA计算）

### 正确接线方法

```
Arduino/STM32          舵机           电源
                                    
  D9 (PWM) ---------> 信号线         
  GND ----------> GND --------> GND
                      VCC --------> +5V (2A)
                      
注意：Arduino的GND必须与电源GND连接（共地）
```


**多舵机供电方案**：

```
方案1：小功率（1-3个舵机）
┌─────────────┐
│  5V/2A电源  │
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
 舵机1   舵机2   舵机3   Arduino GND

方案2：大功率（4个以上舵机）
┌─────────────┐
│  6V/5A电源  │
└──────┬──────┘
       │
   ┌───┴───┐
   │ 电源  │
   │ 分配板 │
   └───┬───┘
       │
   ┌───┴───┬───────┬───────┬───────┐
   │       │       │       │       │
 舵机1   舵机2   舵机3   舵机4   Arduino GND
```

**电源滤波**：
- 在电源输入端并联100μF电解电容
- 每个舵机附近并联0.1μF陶瓷电容
- 减少电压波动和干扰


## 常见问题与解决方案

### 问题1：舵机抖动

**现象**：舵机在某个位置不停抖动

**可能原因**：
1. 电源电压不稳定
2. PWM信号质量差
3. 舵机负载过大
4. 舵机内部齿轮磨损

**解决方法**：
- 使用稳定的电源，添加滤波电容
- 检查PWM信号频率（应为50Hz）
- 减小负载或更换大扭矩舵机
- 更换舵机

### 问题2：舵机不响应

**现象**：发送控制信号，舵机不动

**排查步骤**：
1. 检查电源是否接通（用万用表测量）
2. 检查信号线是否连接正确
3. 检查PWM信号是否输出（用示波器或LED）
4. 尝试用另一个舵机测试
5. 检查代码中的引脚配置

### 问题3：舵机角度不准

**现象**：设置90°，实际不在中间位置

**解决方法**：
```cpp
// 方法1：使用writeMicroseconds()微调
myServo.writeMicroseconds(1500);  // 标准90°
myServo.writeMicroseconds(1480);  // 微调-20μs

// 方法2：创建校准函数
int calibratedAngle(int angle) {
  // 根据实际测试调整
  return map(angle, 0, 180, 5, 175);  // 映射到实际范围
}

myServo.write(calibratedAngle(90));
```


### 问题4：Arduino复位或重启

**现象**：舵机转动时Arduino重启

**原因**：舵机启动瞬间电流过大，导致电源电压跌落

**解决方法**：
1. **电源分离**：Arduino和舵机使用独立电源
2. **添加电容**：在舵机电源端并联大电容（470μF-1000μF）
3. **软启动**：使用平滑移动函数，避免突然启动
4. **限流**：使用电源模块的限流功能

### 问题5：多舵机不同步

**现象**：多个舵机移动速度不一致

**原因**：
- 不同舵机的响应速度不同
- 负载不同导致速度差异

**解决方法**：
```cpp
// 使用时间控制，而不是步进控制
void syncMove(Servo servos[], int targets[], int count, int duration) {
  unsigned long startTime = millis();
  int startAngles[count];
  
  // 记录起始角度
  for (int i = 0; i < count; i++) {
    startAngles[i] = servos[i].read();
  }
  
  // 按时间比例移动
  while (millis() - startTime < duration) {
    float progress = (millis() - startTime) / (float)duration;
    
    for (int i = 0; i < count; i++) {
      int angle = startAngles[i] + 
                  (targets[i] - startAngles[i]) * progress;
      servos[i].write(angle);
    }
    
    delay(20);
  }
  
  // 确保到达目标位置
  for (int i = 0; i < count; i++) {
    servos[i].write(targets[i]);
  }
}
```


## 进阶技巧

### 1. 舵机校准工具

创建一个交互式校准程序：

```cpp
#include <Servo.h>

Servo myServo;
int currentPulse = 1500;  // 微秒

void setup() {
  myServo.attach(9);
  myServo.writeMicroseconds(currentPulse);
  
  Serial.begin(9600);
  Serial.println("=== Servo Calibration Tool ===");
  Serial.println("Commands:");
  Serial.println("  + : Increase pulse by 10us");
  Serial.println("  - : Decrease pulse by 10us");
  Serial.println("  [ : Increase pulse by 1us");
  Serial.println("  ] : Decrease pulse by 1us");
  Serial.println("  r : Reset to 1500us");
  printStatus();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    switch(cmd) {
      case '+':
        currentPulse += 10;
        break;
      case '-':
        currentPulse -= 10;
        break;
      case '[':
        currentPulse += 1;
        break;
      case ']':
        currentPulse -= 1;
        break;
      case 'r':
        currentPulse = 1500;
        break;
    }
    
    // 限制范围
    currentPulse = constrain(currentPulse, 500, 2500);
    
    myServo.writeMicroseconds(currentPulse);
    printStatus();
  }
}

void printStatus() {
  Serial.print("Pulse: ");
  Serial.print(currentPulse);
  Serial.print("us (");
  Serial.print((currentPulse - 500) * 180 / 2000);
  Serial.println("°)");
}
```


### 2. 缓动函数（Easing）

使用缓动函数实现更自然的运动效果：

```cpp
// 缓入缓出函数（Ease In-Out）
float easeInOutQuad(float t) {
  return t < 0.5 ? 2 * t * t : 1 - pow(-2 * t + 2, 2) / 2;
}

void easingMove(Servo &servo, int startAngle, int endAngle, int duration) {
  unsigned long startTime = millis();
  
  while (millis() - startTime < duration) {
    float progress = (millis() - startTime) / (float)duration;
    float eased = easeInOutQuad(progress);
    
    int angle = startAngle + (endAngle - startAngle) * eased;
    servo.write(angle);
    
    delay(20);
  }
  
  servo.write(endAngle);
}

// 使用示例
void loop() {
  easingMove(myServo, 0, 180, 2000);   // 平滑移动
  delay(1000);
  easingMove(myServo, 180, 0, 2000);
  delay(1000);
}
```

### 3. 舵机保护

添加软件保护机制：

```cpp
class SafeServo {
private:
  Servo servo;
  int minAngle;
  int maxAngle;
  int currentAngle;
  unsigned long lastMoveTime;
  const unsigned long MOVE_INTERVAL = 20;  // 最小移动间隔(ms)
  
public:
  SafeServo(int min = 0, int max = 180) {
    minAngle = min;
    maxAngle = max;
    currentAngle = 90;
    lastMoveTime = 0;
  }
  
  void attach(int pin) {
    servo.attach(pin);
    servo.write(currentAngle);
  }
  
  bool write(int angle) {
    // 检查移动间隔
    if (millis() - lastMoveTime < MOVE_INTERVAL) {
      return false;
    }
    
    // 限制角度范围
    angle = constrain(angle, minAngle, maxAngle);
    
    // 限制单次移动幅度（防止过快）
    int maxStep = 30;
    if (abs(angle - currentAngle) > maxStep) {
      if (angle > currentAngle) {
        angle = currentAngle + maxStep;
      } else {
        angle = currentAngle - maxStep;
      }
    }
    
    servo.write(angle);
    currentAngle = angle;
    lastMoveTime = millis();
    
    return true;
  }
  
  int read() {
    return currentAngle;
  }
};
```


## 实际应用案例

### 案例1：云台控制

双轴云台用于摄像头或传感器的方向控制：

```cpp
#include <Servo.h>

Servo panServo;   // 水平旋转（Pan）
Servo tiltServo;  // 垂直俯仰（Tilt）

int panAngle = 90;
int tiltAngle = 90;

void setup() {
  panServo.attach(9);
  tiltServo.attach(10);
  
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
  
  Serial.begin(9600);
  Serial.println("Gimbal Control");
  Serial.println("WASD to control, R to reset");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    switch(cmd) {
      case 'w':  // 向上
      case 'W':
        tiltAngle = constrain(tiltAngle + 5, 0, 180);
        break;
      case 's':  // 向下
      case 'S':
        tiltAngle = constrain(tiltAngle - 5, 0, 180);
        break;
      case 'a':  // 向左
      case 'A':
        panAngle = constrain(panAngle - 5, 0, 180);
        break;
      case 'd':  // 向右
      case 'D':
        panAngle = constrain(panAngle + 5, 0, 180);
        break;
      case 'r':  // 复位
      case 'R':
        panAngle = 90;
        tiltAngle = 90;
        break;
    }
    
    panServo.write(panAngle);
    tiltServo.write(tiltAngle);
    
    Serial.print("Pan: ");
    Serial.print(panAngle);
    Serial.print("° Tilt: ");
    Serial.print(tiltAngle);
    Serial.println("°");
  }
}
```


### 案例2：自动门控制

使用舵机控制小型自动门：

```cpp
#include <Servo.h>

Servo doorServo;
const int SENSOR_PIN = 2;  // 红外传感器

const int DOOR_CLOSED = 0;
const int DOOR_OPEN = 90;

bool doorState = false;  // false=关闭, true=打开
unsigned long lastDetectTime = 0;
const unsigned long CLOSE_DELAY = 3000;  // 3秒后自动关门

void setup() {
  doorServo.attach(9);
  pinMode(SENSOR_PIN, INPUT);
  
  doorServo.write(DOOR_CLOSED);
  
  Serial.begin(9600);
  Serial.println("Automatic Door System");
}

void loop() {
  bool detected = digitalRead(SENSOR_PIN);
  
  if (detected) {
    // 检测到人，开门
    if (!doorState) {
      Serial.println("Opening door...");
      smoothMove(DOOR_CLOSED, DOOR_OPEN, 1000);
      doorState = true;
    }
    lastDetectTime = millis();
  } else {
    // 未检测到人，延时后关门
    if (doorState && (millis() - lastDetectTime > CLOSE_DELAY)) {
      Serial.println("Closing door...");
      smoothMove(DOOR_OPEN, DOOR_CLOSED, 1000);
      doorState = false;
    }
  }
  
  delay(100);
}

void smoothMove(int start, int end, int duration) {
  int steps = duration / 20;
  float increment = (end - start) / (float)steps;
  
  for (int i = 0; i <= steps; i++) {
    int angle = start + (int)(increment * i);
    doorServo.write(angle);
    delay(20);
  }
}
```


### 案例3：太阳能追踪器

使用光敏电阻和舵机实现太阳追踪：

```cpp
#include <Servo.h>

Servo panServo;
Servo tiltServo;

// 光敏电阻引脚（四个方向）
const int LDR_LEFT = A0;
const int LDR_RIGHT = A1;
const int LDR_UP = A2;
const int LDR_DOWN = A3;

int panAngle = 90;
int tiltAngle = 90;

const int THRESHOLD = 50;  // 光强差异阈值

void setup() {
  panServo.attach(9);
  tiltServo.attach(10);
  
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
  
  Serial.begin(9600);
}

void loop() {
  // 读取四个方向的光强
  int leftLight = analogRead(LDR_LEFT);
  int rightLight = analogRead(LDR_RIGHT);
  int upLight = analogRead(LDR_UP);
  int downLight = analogRead(LDR_DOWN);
  
  // 水平方向调整
  int horizontalDiff = leftLight - rightLight;
  if (abs(horizontalDiff) > THRESHOLD) {
    if (horizontalDiff > 0) {
      // 左边更亮，向左转
      panAngle = constrain(panAngle - 1, 0, 180);
    } else {
      // 右边更亮，向右转
      panAngle = constrain(panAngle + 1, 0, 180);
    }
    panServo.write(panAngle);
  }
  
  // 垂直方向调整
  int verticalDiff = upLight - downLight;
  if (abs(verticalDiff) > THRESHOLD) {
    if (verticalDiff > 0) {
      // 上方更亮，向上转
      tiltAngle = constrain(tiltAngle + 1, 0, 180);
    } else {
      // 下方更亮，向下转
      tiltAngle = constrain(tiltAngle - 1, 0, 180);
    }
    tiltServo.write(tiltAngle);
  }
  
  delay(100);
}
```


## 性能优化建议

### 1. 减少抖动

```cpp
// 使用死区（Dead Zone）减少微小抖动
int applyDeadZone(int targetAngle, int currentAngle, int deadZone = 2) {
  if (abs(targetAngle - currentAngle) < deadZone) {
    return currentAngle;  // 在死区内，不移动
  }
  return targetAngle;
}
```

### 2. 降低功耗

```cpp
// 到达目标位置后，detach舵机以节省电源
void moveAndDetach(Servo &servo, int angle) {
  servo.write(angle);
  delay(1000);  // 等待到达
  servo.detach();  // 断开PWM信号
}

// 需要移动时再attach
void moveAgain(Servo &servo, int pin, int angle) {
  servo.attach(pin);
  servo.write(angle);
  delay(1000);
  servo.detach();
}
```

### 3. 提高响应速度

```cpp
// 使用中断处理传感器输入，提高响应速度
volatile bool needUpdate = false;
volatile int targetAngle = 90;

void setup() {
  attachInterrupt(digitalPinToInterrupt(2), sensorISR, CHANGE);
}

void sensorISR() {
  // 在中断中更新目标角度
  targetAngle = calculateAngle();
  needUpdate = true;
}

void loop() {
  if (needUpdate) {
    myServo.write(targetAngle);
    needUpdate = false;
  }
}
```


## 总结

### 关键要点

1. **工作原理**：
   - 舵机内部集成控制电路、电机、齿轮和位置反馈
   - 通过PWM信号的脉宽控制角度
   - 闭环控制系统确保精确定位

2. **PWM控制**：
   - 周期：20ms（50Hz）
   - 脉宽范围：0.5ms-2.5ms对应0°-180°
   - 不同舵机可能有细微差异，需要校准

3. **电源管理**：
   - 使用独立电源供电（5V/2A以上）
   - 必须与MCU共地
   - 添加滤波电容减少干扰

4. **多舵机控制**：
   - Arduino Uno最多支持12个舵机
   - 注意电源容量
   - 使用同步移动算法实现协调控制

5. **常见应用**：
   - 机械臂关节控制
   - 云台方向控制
   - 自动门/窗控制
   - 太阳能追踪

### 最佳实践

- ✅ 使用Servo库简化开发
- ✅ 实现平滑移动避免突然启动
- ✅ 添加角度限制保护机制
- ✅ 电源与MCU分离
- ✅ 定期校准舵机
- ❌ 避免频繁大幅度移动
- ❌ 不要长时间堵转
- ❌ 不要超出角度范围


## 下一步学习

### 相关教程

- **[直流电机控制](./01-dc-motor-control.html)** - 学习直流电机的速度和方向控制
- **[步进电机控制](./02-stepper-motor-control.html)** - 学习步进电机的精确位置控制
- **[继电器控制](./04-relay-control.html)** - 学习大功率负载的开关控制

### 进阶主题

- **[PID控制算法](../intermediate/03-pid-control.html)** - 学习更精确的控制算法
- **[无刷电机控制](../intermediate/02-bldc-motor-control.html)** - 学习高性能电机控制
- **机械臂运动学** - 学习机械臂的数学建模

### 项目实践

- **[智能云台项目](../advanced/04-smart-gimbal-project.html)** - 制作自动追踪云台
- **[四自由度机械臂](../advanced/05-robot-arm-project.html)** - 完整的机械臂控制系统
- **[六足机器人](../advanced/06-hexapod-robot.html)** - 多舵机协调控制


## 参考资料

### 数据手册

1. **[SG90 Datasheet](http://www.ee.ic.ac.uk/pcheung/teaching/DE1_EE/stores/sg90_datasheet.pdf)** - TowerPro SG90舵机规格书
2. **[MG996R Datasheet](https://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf)** - TowerPro MG996R舵机规格书
3. **[Arduino Servo Library](https://www.arduino.cc/reference/en/libraries/servo/)** - Arduino官方Servo库文档

### 技术文章

1. "How Servo Motors Work" - 舵机工作原理详解
2. "PWM Signal Generation for Servo Control" - PWM信号生成技术
3. "Multi-Servo Synchronization Techniques" - 多舵机同步控制技术
4. "Power Supply Design for Servo Systems" - 舵机系统电源设计

### 视频教程

1. "Arduino Servo Motor Tutorial" - YouTube基础教程
2. "Building a Robot Arm with Servos" - 机械臂制作教程
3. "Servo Motor Calibration Guide" - 舵机校准指南

### 开源项目

1. **[Arduino Servo Library](https://github.com/arduino-libraries/Servo)** - Arduino官方舵机库
2. **[ServoEasing](https://github.com/ArminJo/ServoEasing)** - 带缓动效果的舵机库
3. **[Braccio Robot Arm](https://github.com/arduino-libraries/Braccio)** - Arduino官方机械臂项目

### 工具和软件

1. **[Servo Tester](https://www.thingiverse.com/thing:2786292)** - 3D打印舵机测试工具
2. **[ServoCity](https://www.servocity.com/)** - 舵机配件和机械件
3. **[Robot Arm Designer](https://www.robotshop.com/community/robots/show/robot-arm-designer)** - 机械臂设计工具

## 附录

### A. 常用舵机参数对照表

| 型号 | 扭矩 | 速度 | 工作电压 | 重量 | 价格 | 应用 |
|------|------|------|---------|------|------|------|
| SG90 | 1.8kg·cm | 0.1s/60° | 4.8-6V | 9g | ¥5 | 小型项目 |
| MG90S | 2.2kg·cm | 0.1s/60° | 4.8-6V | 13.4g | ¥8 | 小型机械臂 |
| MG996R | 11kg·cm | 0.17s/60° | 4.8-7.2V | 55g | ¥15 | 标准应用 |
| DS3218 | 20kg·cm | 0.16s/60° | 4.8-6.8V | 60g | ¥35 | 高精度应用 |
| HS-422 | 4.1kg·cm | 0.21s/60° | 4.8-6V | 45.5g | ¥25 | 航模 |
| HS-645MG | 9.6kg·cm | 0.24s/60° | 4.8-6V | 56g | ¥50 | 大扭矩应用 |


### B. PWM脉宽与角度对照表

| 角度(°) | 脉宽(ms) | 脉宽(μs) | 占空比(%) |
|---------|---------|---------|-----------|
| 0 | 0.50 | 500 | 2.5 |
| 15 | 0.67 | 667 | 3.3 |
| 30 | 0.83 | 833 | 4.2 |
| 45 | 1.00 | 1000 | 5.0 |
| 60 | 1.17 | 1167 | 5.8 |
| 75 | 1.33 | 1333 | 6.7 |
| 90 | 1.50 | 1500 | 7.5 |
| 105 | 1.67 | 1667 | 8.3 |
| 120 | 1.83 | 1833 | 9.2 |
| 135 | 2.00 | 2000 | 10.0 |
| 150 | 2.17 | 2167 | 10.8 |
| 165 | 2.33 | 2333 | 11.7 |
| 180 | 2.50 | 2500 | 12.5 |

### C. 故障排查流程图

```
舵机不工作？
  │
  ├─ 检查电源
  │   ├─ 电压是否正确？(4.8-6V)
  │   │   ├─ 是 → 继续
  │   │   └─ 否 → 调整电源电压
  │   └─ 电流是否充足？(>500mA)
  │       ├─ 是 → 继续
  │       └─ 否 → 更换大功率电源
  │
  ├─ 检查接线
  │   ├─ 信号线连接正确？
  │   │   ├─ 是 → 继续
  │   │   └─ 否 → 重新连接
  │   └─ 是否共地？
  │       ├─ 是 → 继续
  │       └─ 否 → 连接GND
  │
  ├─ 检查信号
  │   ├─ PWM频率正确？(50Hz)
  │   │   ├─ 是 → 继续
  │   │   └─ 否 → 修改代码
  │   └─ 脉宽范围正确？(0.5-2.5ms)
  │       ├─ 是 → 继续
  │       └─ 否 → 调整参数
  │
  └─ 检查舵机
      ├─ 更换舵机测试
      │   ├─ 正常 → 原舵机损坏
      │   └─ 仍不正常 → 检查MCU
      └─ 手动转动舵机
          ├─ 卡住 → 齿轮损坏
          └─ 正常 → 控制电路问题
```

### D. 选型建议

**根据应用场景选择舵机**：

1. **小型玩具/教学项目**：
   - 推荐：SG90
   - 理由：价格低廉，够用

2. **小型机械臂（2-3自由度）**：
   - 推荐：MG90S或MG996R
   - 理由：金属齿轮更耐用

3. **标准机械臂（4-6自由度）**：
   - 推荐：MG996R + DS3218组合
   - 理由：根据关节负载选择

4. **高精度应用**：
   - 推荐：DS3218或更高级数字舵机
   - 理由：精度高，响应快

5. **航模应用**：
   - 推荐：HS系列
   - 理由：专业航模舵机，可靠性高

---

**版权声明**：本文档采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。

**反馈与支持**：
- 发现错误或有改进建议？请在评论区留言
- 分享你的舵机项目，与社区交流
- 需要技术支持？访问我们的论坛

**最后更新**：2024-01-15
