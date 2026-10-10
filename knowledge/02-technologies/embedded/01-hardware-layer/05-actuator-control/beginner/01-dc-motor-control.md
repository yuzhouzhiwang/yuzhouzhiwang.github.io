---
title: "直流电机驱动与控制实战教程"
description: "从零开始学习直流电机的驱动原理、H桥电路设计、PWM调速技术，使用L298N驱动模块实现电机的方向控制和速度调节"
slug: "dc-motor-control-tutorial"

# 分类信息
domain: "底层硬件层"
module: "执行器控制"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 直流电机
  - H桥
  - PWM
  - L298N
  - 电机驱动
  - 速度控制
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 65
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
  - 直流电机控制
  - H桥驱动
  - PWM调速
  - L298N驱动模块
  - 电机方向控制
cover_image: ""
---

# 直流电机驱动与控制实战教程

## 学习目标

完成本教程后，你将能够：

- [ ] 理解直流电机的工作原理和驱动需求
- [ ] 掌握H桥驱动电路的工作原理
- [ ] 学会使用L298N驱动模块控制电机
- [ ] 实现PWM调速和方向控制
- [ ] 添加电流保护和安全措施

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解C语言基础编程
- 熟悉基本电路知识（电压、电流、欧姆定律）
- 掌握GPIO和PWM的基本概念
- 了解数字信号的高低电平

**技能要求**：
- 能够使用Arduino IDE或STM32开发环境
- 会使用面包板搭建简单电路
- 能够使用万用表测量电压和电流

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考价格 |
|------|------|------|----------|
| 开发板 | 1 | Arduino Uno 或 STM32F103 | ¥30-80 |
| L298N驱动模块 | 1 | 双H桥电机驱动 | ¥8-15 |
| 直流电机 | 1-2 | 3-6V，带减速器更佳 | ¥5-20 |
| 电源 | 1 | 6-12V，2A以上 | ¥15-30 |
| 杜邦线 | 若干 | 公对公、公对母 | ¥5 |
| 面包板 | 1 | 可选，用于测试 | ¥5 |

### 软件准备

**Arduino平台**：
- Arduino IDE 1.8.x 或 2.x
- USB驱动程序（CH340或CP2102）

**STM32平台**：
- STM32CubeIDE 或 Keil MDK
- ST-Link驱动程序

### 安全注意事项

⚠️ **重要提醒**：
- 电机驱动电路可能产生较大电流，注意散热
- 接线时务必断电，避免短路
- 首次测试时使用较低电压（6V）
- 确保电源能够提供足够的电流（建议2A以上）
- L298N模块会发热，避免长时间满载运行

## 理论基础

### 直流电机工作原理

直流电机通过电磁感应原理工作：

1. **基本原理**：通电导体在磁场中受力旋转
2. **转速控制**：通过改变电压或PWM占空比调节转速
3. **方向控制**：通过改变电流方向改变旋转方向

**关键参数**：
- **额定电压**：电机设计工作电压（如3V、6V、12V）
- **额定电流**：正常工作时的电流（如200mA、1A）
- **堵转电流**：电机被卡住时的最大电流（通常是额定电流的5-10倍）
- **转速**：每分钟转数（RPM），如3000RPM

### H桥驱动原理

H桥电路是控制电机方向的核心电路，由4个开关（通常是MOSFET或三极管）组成：

```
        VCC
         |
    Q1   |   Q2
     |---+---|
     |       |
     +---M---+  (电机)
     |       |
     |---+---|
    Q3   |   Q4
         |
        GND
```

**工作模式**：

1. **正转**：Q1和Q4导通，Q2和Q3关断
   - 电流路径：VCC → Q1 → 电机 → Q4 → GND
   
2. **反转**：Q2和Q3导通，Q1和Q4关断
   - 电流路径：VCC → Q2 → 电机 → Q3 → GND
   
3. **制动**：Q1和Q2导通（或Q3和Q4导通）
   - 电机两端短路，快速停止
   
4. **滑行**：所有开关关断
   - 电机自由滑行停止

⚠️ **禁止状态**：Q1和Q3同时导通，或Q2和Q4同时导通会造成电源短路！

### L298N模块介绍

L298N是一款双H桥电机驱动芯片，可以同时驱动两个直流电机或一个步进电机。

**主要特性**：
- 工作电压：5V-35V
- 最大输出电流：2A（每通道）
- 峰值电流：3A
- 内置续流二极管
- 逻辑电平：5V TTL兼容

**引脚说明**：

| 引脚 | 功能 | 说明 |
|------|------|------|
| IN1, IN2 | 电机A方向控制 | 高低电平组合控制方向 |
| IN3, IN4 | 电机B方向控制 | 高低电平组合控制方向 |
| ENA | 电机A使能 | PWM信号控制速度 |
| ENB | 电机B使能 | PWM信号控制速度 |
| OUT1, OUT2 | 电机A输出 | 连接电机A |
| OUT3, OUT4 | 电机B输出 | 连接电机B |
| +12V | 电机电源输入 | 6-12V |
| GND | 地 | 公共地 |
| +5V | 逻辑电源输出 | 可为MCU供电（跳线帽） |

### PWM调速原理

PWM（脉宽调制）通过改变高电平占空比来控制电机的平均电压，从而控制转速。

**占空比计算**：
```
占空比 = (高电平时间 / 周期) × 100%
平均电压 = 电源电压 × 占空比
```

**示例**：
- 占空比50%，12V电源 → 平均电压6V → 中速
- 占空比75%，12V电源 → 平均电压9V → 高速
- 占空比25%，12V电源 → 平均电压3V → 低速

**PWM频率选择**：
- 推荐频率：1kHz - 20kHz
- 频率过低：电机会产生明显的啸叫声
- 频率过高：开关损耗增加，效率降低

## 电路连接

### 连接图

```
Arduino/STM32          L298N模块           直流电机
                                          
  D9 (PWM) ---------> ENA                
  D8 ----------> IN1                     
  D7 ----------> IN2                     
                      OUT1 ----------> 电机+
                      OUT2 ----------> 电机-
  GND ----------> GND
                      +12V <---------- 电源+
                      GND  <---------- 电源-
```

### 详细连接说明

**控制信号连接**（以Arduino为例）：

| Arduino引脚 | L298N引脚 | 功能 |
|------------|----------|------|
| D9 (PWM) | ENA | 电机A速度控制 |
| D8 | IN1 | 电机A方向控制1 |
| D7 | IN2 | 电机A方向控制2 |
| GND | GND | 公共地 |

**电源连接**：

| 电源 | L298N引脚 | 说明 |
|------|----------|------|
| +6V~12V | +12V | 电机电源（根据电机额定电压选择） |
| GND | GND | 电源地 |

**电机连接**：

| L298N引脚 | 连接 |
|----------|------|
| OUT1 | 电机正极 |
| OUT2 | 电机负极 |

**注意事项**：
1. ⚠️ **必须共地**：Arduino/STM32的GND必须与L298N的GND连接
2. ⚠️ **电源分离**：电机电源和MCU电源建议分开（避免电机启动时的电压波动影响MCU）
3. ⚠️ **跳线帽**：如果使用L298N的5V输出为Arduino供电，需要插上跳线帽；如果Arduino独立供电，建议拔掉跳线帽
4. ⚠️ **电机极性**：如果电机转向相反，交换OUT1和OUT2的连接即可

## 步骤1：基础测试 - 电机正转

### 1.1 创建Arduino项目

1. 打开Arduino IDE
2. 选择 文件 → 新建
3. 保存项目为 `dc_motor_basic`

### 1.2 定义引脚

在代码开头定义引脚：

```cpp
// L298N引脚定义
const int ENA = 9;   // PWM引脚，控制速度
const int IN1 = 8;   // 方向控制1
const int IN2 = 7;   // 方向控制2

void setup() {
  // 设置引脚模式
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  // 初始化串口（用于调试）
  Serial.begin(9600);
  Serial.println("DC Motor Control Test");
}
```

### 1.3 实现正转功能

```cpp
void loop() {
  // 电机正转
  digitalWrite(IN1, HIGH);  // IN1 = 1
  digitalWrite(IN2, LOW);   // IN2 = 0
  analogWrite(ENA, 200);    // PWM占空比约78% (200/255)
  
  Serial.println("Motor: Forward, Speed: 200/255");
  delay(3000);  // 运行3秒
  
  // 停止
  analogWrite(ENA, 0);
  Serial.println("Motor: Stop");
  delay(2000);  // 停止2秒
}
```

### 1.4 上传和测试

1. 选择正确的开发板和端口
2. 点击上传按钮
3. 观察电机运行情况

**预期结果**：
- 电机以中等速度正转3秒
- 停止2秒
- 循环重复

**调试技巧**：
- 打开串口监视器（波特率9600）查看调试信息
- 如果电机不转，检查电源和接线
- 如果转向相反，交换IN1和IN2的值

## 步骤2：实现方向控制

### 2.1 添加反转功能

创建控制函数：

```cpp
// 电机正转
void motorForward(int speed) {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, speed);
}

// 电机反转
void motorBackward(int speed) {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, speed);
}

// 电机停止
void motorStop() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
}

// 电机制动（快速停止）
void motorBrake() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, 255);
}
```

### 2.2 测试正反转

```cpp
void loop() {
  Serial.println("Forward");
  motorForward(200);
  delay(2000);
  
  Serial.println("Stop");
  motorStop();
  delay(1000);
  
  Serial.println("Backward");
  motorBackward(200);
  delay(2000);
  
  Serial.println("Brake");
  motorBrake();
  delay(1000);
}
```

**方向控制真值表**：

| IN1 | IN2 | ENA | 状态 |
|-----|-----|-----|------|
| 0 | 0 | X | 停止（滑行） |
| 0 | 1 | PWM | 反转 |
| 1 | 0 | PWM | 正转 |
| 1 | 1 | PWM | 制动（快速停止） |

## 步骤3：PWM调速实现

### 3.1 速度渐变效果

实现电机从慢到快的加速效果：

```cpp
void motorAccelerate() {
  Serial.println("Accelerating...");
  
  // 从速度0加速到255
  for (int speed = 0; speed <= 255; speed += 5) {
    motorForward(speed);
    Serial.print("Speed: ");
    Serial.println(speed);
    delay(100);  // 每100ms增加一次速度
  }
}

void motorDecelerate() {
  Serial.println("Decelerating...");
  
  // 从速度255减速到0
  for (int speed = 255; speed >= 0; speed -= 5) {
    motorForward(speed);
    Serial.print("Speed: ");
    Serial.println(speed);
    delay(100);
  }
}

void loop() {
  motorAccelerate();   // 加速
  delay(1000);         // 保持最高速1秒
  motorDecelerate();   // 减速
  delay(2000);         // 停止2秒
}
```

### 3.2 多档位速度控制

定义几个常用速度档位：

```cpp
// 速度档位定义
const int SPEED_STOP = 0;
const int SPEED_LOW = 100;      // 低速：约39%
const int SPEED_MEDIUM = 180;   // 中速：约71%
const int SPEED_HIGH = 255;     // 高速：100%

void testSpeedLevels() {
  Serial.println("Testing speed levels...");
  
  // 低速
  Serial.println("Low speed");
  motorForward(SPEED_LOW);
  delay(3000);
  
  // 中速
  Serial.println("Medium speed");
  motorForward(SPEED_MEDIUM);
  delay(3000);
  
  // 高速
  Serial.println("High speed");
  motorForward(SPEED_HIGH);
  delay(3000);
  
  // 停止
  motorStop();
  delay(2000);
}
```

### 3.3 PWM频率调整（高级）

Arduino默认PWM频率约为490Hz（D9、D10）或980Hz（D3、D5、D6、D11）。
如果需要调整频率，可以修改定时器寄存器：

```cpp
void setup() {
  // ... 其他初始化代码 ...
  
  // 设置D9引脚PWM频率为31kHz
  // 注意：这会影响D9和D10两个引脚
  TCCR1B = TCCR1B & 0b11111000 | 0x01;
  
  // 频率选项：
  // 0x01 -> 31kHz
  // 0x02 -> 4kHz
  // 0x03 -> 490Hz (默认)
  // 0x04 -> 122Hz
  // 0x05 -> 30Hz
}
```

**注意**：修改PWM频率会影响delay()和millis()函数的准确性。

## 步骤4：添加保护功能

### 4.1 软启动功能

避免电机突然启动造成的电流冲击：

```cpp
void motorSoftStart(int targetSpeed, int direction) {
  Serial.println("Soft start...");
  
  // 设置方向
  if (direction == 1) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  
  // 逐渐加速到目标速度
  for (int speed = 0; speed <= targetSpeed; speed += 2) {
    analogWrite(ENA, speed);
    delay(20);  // 每20ms增加速度
  }
}

void motorSoftStop() {
  Serial.println("Soft stop...");
  
  // 获取当前速度（简化版，实际应用中需要保存当前速度）
  for (int speed = 200; speed >= 0; speed -= 2) {
    analogWrite(ENA, speed);
    delay(20);
  }
  
  motorStop();
}
```

### 4.2 过流保护（硬件）

虽然L298N内置了一定的保护，但建议添加额外保护：

**硬件保护措施**：
1. **保险丝**：在电源正极串联2A保险丝
2. **续流二极管**：L298N已内置，外接电机时确保极性正确
3. **散热片**：L298N芯片上安装散热片，必要时加风扇
4. **电容滤波**：在电源输入端并联100μF电解电容和0.1μF陶瓷电容

### 4.3 堵转检测（软件）

通过检测电流或速度来判断电机是否堵转：

```cpp
// 简化版堵转检测（需要电流传感器）
// 这里使用时间超时作为简单判断

unsigned long motorStartTime = 0;
const unsigned long STALL_TIMEOUT = 5000;  // 5秒超时

void motorRunWithTimeout(int speed, int direction) {
  motorStartTime = millis();
  
  if (direction == 1) {
    motorForward(speed);
  } else {
    motorBackward(speed);
  }
  
  // 在主循环中检查
  while (millis() - motorStartTime < STALL_TIMEOUT) {
    // 这里可以添加电流检测逻辑
    // 如果检测到异常，立即停止
    delay(100);
  }
  
  // 超时停止
  motorStop();
  Serial.println("Motor timeout - stopped");
}
```

## 步骤5：完整示例程序

### 5.1 综合控制程序

```cpp
// ========================================
// 直流电机完整控制程序
// 功能：方向控制、速度调节、软启动
// ========================================

// 引脚定义
const int ENA = 9;
const int IN1 = 8;
const int IN2 = 7;

// 速度档位
const int SPEED_STOP = 0;
const int SPEED_LOW = 100;
const int SPEED_MEDIUM = 180;
const int SPEED_HIGH = 255;

// 方向定义
const int DIR_FORWARD = 1;
const int DIR_BACKWARD = -1;

// 当前状态
int currentSpeed = 0;
int currentDirection = 0;

void setup() {
  // 初始化引脚
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  // 初始化串口
  Serial.begin(9600);
  Serial.println("=== DC Motor Control System ===");
  Serial.println("Commands:");
  Serial.println("  f - Forward");
  Serial.println("  b - Backward");
  Serial.println("  s - Stop");
  Serial.println("  1 - Low speed");
  Serial.println("  2 - Medium speed");
  Serial.println("  3 - High speed");
  
  // 确保电机停止
  motorStop();
}

void loop() {
  // 检查串口命令
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    handleCommand(cmd);
  }
}

// 命令处理
void handleCommand(char cmd) {
  switch (cmd) {
    case 'f':
    case 'F':
      Serial.println("Command: Forward");
      setMotorDirection(DIR_FORWARD);
      break;
      
    case 'b':
    case 'B':
      Serial.println("Command: Backward");
      setMotorDirection(DIR_BACKWARD);
      break;
      
    case 's':
    case 'S':
      Serial.println("Command: Stop");
      motorSoftStop();
      break;
      
    case '1':
      Serial.println("Command: Low Speed");
      setMotorSpeed(SPEED_LOW);
      break;
      
    case '2':
      Serial.println("Command: Medium Speed");
      setMotorSpeed(SPEED_MEDIUM);
      break;
      
    case '3':
      Serial.println("Command: High Speed");
      setMotorSpeed(SPEED_HIGH);
      break;
      
    default:
      Serial.println("Unknown command");
      break;
  }
}

// 设置电机方向
void setMotorDirection(int direction) {
  if (direction == DIR_FORWARD) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    currentDirection = DIR_FORWARD;
    Serial.println("Direction: Forward");
  } else if (direction == DIR_BACKWARD) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    currentDirection = DIR_BACKWARD;
    Serial.println("Direction: Backward");
  }
  
  // 如果当前速度为0，设置为低速
  if (currentSpeed == 0) {
    setMotorSpeed(SPEED_LOW);
  }
}

// 设置电机速度（带软启动）
void setMotorSpeed(int targetSpeed) {
  Serial.print("Speed: ");
  Serial.print(targetSpeed);
  Serial.print(" (");
  Serial.print((targetSpeed * 100) / 255);
  Serial.println("%)");
  
  // 软启动/软停止
  if (targetSpeed > currentSpeed) {
    // 加速
    for (int s = currentSpeed; s <= targetSpeed; s += 5) {
      analogWrite(ENA, s);
      delay(20);
    }
  } else {
    // 减速
    for (int s = currentSpeed; s >= targetSpeed; s -= 5) {
      analogWrite(ENA, s);
      delay(20);
    }
  }
  
  currentSpeed = targetSpeed;
  analogWrite(ENA, currentSpeed);
}

// 电机停止
void motorStop() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
  currentSpeed = 0;
  currentDirection = 0;
  Serial.println("Motor stopped");
}

// 软停止
void motorSoftStop() {
  Serial.println("Soft stopping...");
  for (int s = currentSpeed; s >= 0; s -= 5) {
    analogWrite(ENA, s);
    delay(20);
  }
  motorStop();
}
```

### 5.2 STM32版本代码

对于STM32平台，使用HAL库实现：

```c
// STM32 HAL库版本
// 假设使用TIM2的CH1（PA0）作为PWM输出

// 引脚定义
#define IN1_PIN GPIO_PIN_1
#define IN2_PIN GPIO_PIN_2
#define IN1_PORT GPIOA
#define IN2_PORT GPIOA

// PWM定时器句柄（在main.c中初始化）
extern TIM_HandleTypeDef htim2;

// 电机正转
void Motor_Forward(uint16_t speed) {
    HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, speed);
}

// 电机反转
void Motor_Backward(uint16_t speed) {
    HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_SET);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, speed);
}

// 电机停止
void Motor_Stop(void) {
    HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, 0);
}

// 软启动
void Motor_SoftStart(uint16_t targetSpeed, uint8_t direction) {
    for (uint16_t speed = 0; speed <= targetSpeed; speed += 10) {
        if (direction == 1) {
            Motor_Forward(speed);
        } else {
            Motor_Backward(speed);
        }
        HAL_Delay(20);
    }
}
```

**STM32CubeMX配置要点**：
1. 配置TIM2为PWM模式
2. 设置PWM频率为10kHz（ARR=1000, PSC根据时钟计算）
3. 配置GPIO为输出模式（IN1, IN2）
4. 启动PWM：`HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);`

## 测试验证

### 基本功能测试清单

- [ ] **电源测试**：确认电源电压正确（6-12V）
- [ ] **静态测试**：上电后电机不应自动转动
- [ ] **正转测试**：发送正转命令，电机正向旋转
- [ ] **反转测试**：发送反转命令，电机反向旋转
- [ ] **停止测试**：发送停止命令，电机立即停止
- [ ] **速度测试**：测试低、中、高三个速度档位
- [ ] **软启动测试**：观察启动过程是否平滑
- [ ] **连续运行测试**：连续运行5分钟，检查发热情况

### 性能测试

**测试1：速度响应**
```cpp
void testSpeedResponse() {
  Serial.println("=== Speed Response Test ===");
  
  for (int speed = 50; speed <= 255; speed += 50) {
    Serial.print("Testing speed: ");
    Serial.println(speed);
    motorForward(speed);
    delay(2000);
  }
  
  motorStop();
}
```

**测试2：方向切换**
```cpp
void testDirectionChange() {
  Serial.println("=== Direction Change Test ===");
  
  for (int i = 0; i < 5; i++) {
    Serial.println("Forward");
    motorForward(150);
    delay(1000);
    
    Serial.println("Stop");
    motorStop();
    delay(500);
    
    Serial.println("Backward");
    motorBackward(150);
    delay(1000);
    
    Serial.println("Stop");
    motorStop();
    delay(500);
  }
}
```

### 调试技巧

**问题1：电机不转**
- 检查电源是否接通（用万用表测量）
- 检查L298N的LED指示灯是否亮起
- 检查ENA引脚是否有PWM信号（用示波器或LED测试）
- 检查IN1、IN2的电平状态
- 尝试直接给电机供电，确认电机本身正常

**问题2：电机转速不稳定**
- 检查电源是否足够（电流是否充足）
- 检查PWM频率是否合适
- 检查接线是否松动
- 添加电源滤波电容

**问题3：L298N过热**
- 降低电机负载
- 添加散热片
- 降低PWM占空比
- 检查是否短路

**问题4：电机有异响**
- 降低PWM频率（可能频率过低）
- 检查机械部分是否有摩擦
- 检查电机轴承是否正常

## 故障排除

### 常见问题解决方案

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| 电机不转 | 电源未接通 | 检查电源连接和电压 |
| | PWM信号无输出 | 检查代码和引脚配置 |
| | 电机损坏 | 更换电机 |
| 转向相反 | 接线错误 | 交换OUT1和OUT2 |
| 速度无法调节 | ENA未连接PWM | 检查ENA引脚连接 |
| | PWM频率不对 | 调整PWM配置 |
| L298N发烫 | 电流过大 | 降低负载或更换大功率驱动 |
| | 散热不良 | 添加散热片 |
| 电机抖动 | 电源不稳定 | 添加滤波电容 |
| | PWM频率过低 | 提高PWM频率 |
| MCU复位 | 电源干扰 | 电源分离，添加滤波 |

## 进阶扩展

### 扩展1：双电机控制

L298N可以同时控制两个电机，适合制作小车：

```cpp
// 双电机控制
const int ENA = 9;   // 左电机速度
const int IN1 = 8;   // 左电机方向1
const int IN2 = 7;   // 左电机方向2

const int ENB = 3;   // 右电机速度
const int IN3 = 5;   // 右电机方向1
const int IN4 = 4;   // 右电机方向2

void carForward(int speed) {
  // 左电机正转
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, speed);
  
  // 右电机正转
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, speed);
}

void carTurnLeft(int speed) {
  // 左电机停止或反转
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
  
  // 右电机正转
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, speed);
}

void carTurnRight(int speed) {
  // 左电机正转
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, speed);
  
  // 右电机停止或反转
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
}
```

### 扩展2：编码器反馈

添加编码器实现精确的速度和位置控制：

```cpp
// 编码器引脚
const int ENCODER_A = 2;  // 中断引脚
const int ENCODER_B = 3;  // 中断引脚

volatile long encoderCount = 0;
volatile int lastEncoded = 0;

void setup() {
  // ... 其他初始化 ...
  
  // 配置编码器引脚
  pinMode(ENCODER_A, INPUT_PULLUP);
  pinMode(ENCODER_B, INPUT_PULLUP);
  
  // 附加中断
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_B), updateEncoder, CHANGE);
}

void updateEncoder() {
  int MSB = digitalRead(ENCODER_A);
  int LSB = digitalRead(ENCODER_B);
  
  int encoded = (MSB << 1) | LSB;
  int sum = (lastEncoded << 2) | encoded;
  
  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) {
    encoderCount++;
  }
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) {
    encoderCount--;
  }
  
  lastEncoded = encoded;
}

// 获取速度（RPM）
float getMotorSpeed() {
  static long lastCount = 0;
  static unsigned long lastTime = 0;
  
  unsigned long currentTime = millis();
  long currentCount = encoderCount;
  
  float deltaTime = (currentTime - lastTime) / 1000.0;  // 秒
  long deltaCount = currentCount - lastCount;
  
  // 假设编码器每转1000个脉冲
  float rpm = (deltaCount / 1000.0) * (60.0 / deltaTime);
  
  lastCount = currentCount;
  lastTime = currentTime;
  
  return rpm;
}
```

### 扩展3：PID速度控制

使用PID算法实现精确的速度控制：

```cpp
// PID参数
float Kp = 2.0;
float Ki = 0.5;
float Kd = 0.1;

float targetSpeed = 100;  // 目标速度（RPM）
float integral = 0;
float lastError = 0;

void pidSpeedControl() {
  float currentSpeed = getMotorSpeed();
  float error = targetSpeed - currentSpeed;
  
  // 积分项
  integral += error;
  
  // 限制积分饱和
  if (integral > 100) integral = 100;
  if (integral < -100) integral = -100;
  
  // 微分项
  float derivative = error - lastError;
  
  // PID输出
  float output = Kp * error + Ki * integral + Kd * derivative;
  
  // 限制输出范围
  if (output > 255) output = 255;
  if (output < 0) output = 0;
  
  // 应用到电机
  motorForward((int)output);
  
  lastError = error;
}
```

### 扩展4：蓝牙/WiFi控制

添加无线控制功能：

```cpp
// 使用HC-05蓝牙模块
#include <SoftwareSerial.h>

SoftwareSerial bluetooth(10, 11);  // RX, TX

void setup() {
  // ... 其他初始化 ...
  bluetooth.begin(9600);
}

void loop() {
  if (bluetooth.available()) {
    char cmd = bluetooth.read();
    handleCommand(cmd);
    
    // 发送反馈
    bluetooth.print("Command executed: ");
    bluetooth.println(cmd);
  }
}
```

## 总结

通过本教程，你已经学习了：

- ✅ **直流电机基础**：工作原理、关键参数、驱动需求
- ✅ **H桥原理**：四种工作模式、禁止状态
- ✅ **L298N使用**：引脚功能、接线方法、注意事项
- ✅ **方向控制**：正转、反转、停止、制动
- ✅ **PWM调速**：占空比原理、速度档位、渐变效果
- ✅ **保护措施**：软启动、过流保护、堵转检测
- ✅ **完整程序**：串口控制、状态管理、错误处理

### 关键要点

1. **安全第一**：
   - 接线前务必断电
   - 避免H桥短路（同侧导通）
   - 注意散热和电流保护

2. **PWM调速**：
   - 频率选择：1kHz-20kHz
   - 占空比范围：0-100%
   - 软启动避免电流冲击

3. **方向控制**：
   - 使用真值表理解控制逻辑
   - 方向切换前最好先停止
   - 制动模式可快速停止

4. **电源管理**：
   - MCU和电机电源分离
   - 添加滤波电容
   - 确保电流充足

## 实践挑战

尝试以下挑战来巩固学习：

### 挑战1：智能小车基础控制 ⭐
**难度**：简单  
**任务**：使用两个电机和L298N制作一个可以前进、后退、左转、右转的小车。

**要求**：
- 实现四个基本运动方向
- 添加速度调节功能
- 通过串口或蓝牙控制

### 挑战2：自动避障小车 ⭐⭐
**难度**：中等  
**任务**：在挑战1的基础上，添加超声波传感器实现自动避障。

**要求**：
- 检测前方障碍物
- 自动转向避开障碍
- 保持一定的安全距离

### 挑战3：循迹小车 ⭐⭐⭐
**难度**：较难  
**任务**：使用红外传感器实现循迹功能。

**要求**：
- 识别黑线轨迹
- PID算法优化循迹效果
- 处理交叉路口和弯道

### 挑战4：速度闭环控制 ⭐⭐⭐⭐
**难度**：困难  
**任务**：添加编码器，实现精确的速度闭环控制。

**要求**：
- 实时测量电机转速
- PID算法控制速度
- 速度误差小于5%

## 常见应用场景

### 1. 智能小车
- 避障小车
- 循迹小车
- 遥控小车
- 竞赛机器人

### 2. 自动化设备
- 自动门控制
- 传送带控制
- 升降机构
- 旋转平台

### 3. 家用电器
- 电动窗帘
- 智能风扇
- 自动喂食器
- 扫地机器人

### 4. 教育项目
- STEM教育套件
- 机器人教学
- 创客项目
- 毕业设计

## 下一步学习

建议继续学习以下内容：

### 相关教程
- [步进电机控制](../beginner/02-stepper-motor-control.html) - 学习步进电机的精确位置控制
- [舵机控制](../beginner/03-servo-motor-control.html) - 学习舵机的角度控制
- [PID控制算法](../intermediate/03-pid-control.html) - 深入学习PID控制理论

### 进阶主题
- [无刷电机控制](../intermediate/02-bldc-motor-control.html) - 学习BLDC电机的FOC控制
- [编码器应用](../../../02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/04-encoder-interface.html) - 学习编码器接口和速度测量
- [电机驱动电路设计](../../02-hardware-design-fundamentals/intermediate/06-motor-driver-circuit.html) - 学习自己设计电机驱动电路

## 参考资料

### 数据手册
1. [L298N Datasheet](https://www.st.com/resource/en/datasheet/l298.pdf) - ST官方数据手册
2. [Arduino PWM Reference](https://www.arduino.cc/reference/en/language/functions/analog-io/analogwrite/) - Arduino PWM函数说明

### 技术文章
1. "H-Bridge Motor Driver Circuits" - 详细的H桥电路分析
2. "PWM Motor Speed Control" - PWM调速原理和实践
3. "Motor Protection Techniques" - 电机保护技术

### 视频教程
1. "DC Motor Control with Arduino" - YouTube教程
2. "L298N Motor Driver Tutorial" - 详细的L298N使用教程

### 开源项目
1. [Arduino Motor Shield](https://github.com/arduino/ArduinoMotorShield) - Arduino官方电机驱动库
2. [ROS Motor Control](https://github.com/ros-controls/ros_controllers) - ROS机器人电机控制

## 附录

### A. L298N引脚完整说明

| 引脚 | 类型 | 功能 | 说明 |
|------|------|------|------|
| ENA | 输入 | 电机A使能 | 高电平或PWM信号 |
| IN1 | 输入 | 电机A输入1 | 逻辑控制 |
| IN2 | 输入 | 电机A输入2 | 逻辑控制 |
| OUT1 | 输出 | 电机A输出1 | 连接电机 |
| OUT2 | 输出 | 电机A输出2 | 连接电机 |
| ENB | 输入 | 电机B使能 | 高电平或PWM信号 |
| IN3 | 输入 | 电机B输入1 | 逻辑控制 |
| IN4 | 输入 | 电机B输入2 | 逻辑控制 |
| OUT3 | 输出 | 电机B输出1 | 连接电机 |
| OUT4 | 输出 | 电机B输出2 | 连接电机 |
| +12V | 电源 | 电机电源 | 6-35V |
| +5V | 电源 | 逻辑电源输出 | 5V/1A（需跳线帽） |
| GND | 电源 | 公共地 | 必须与MCU共地 |

### B. 电机选型参考

| 电机类型 | 电压 | 电流 | 转速 | 扭矩 | 应用场景 |
|---------|------|------|------|------|---------|
| 130电机 | 3-6V | 0.2-0.5A | 15000RPM | 低 | 小型玩具 |
| 180电机 | 3-6V | 0.3-0.8A | 12000RPM | 中 | 小车、风扇 |
| 280电机 | 6-12V | 0.5-1.5A | 10000RPM | 中 | 中型小车 |
| 380电机 | 6-12V | 1-3A | 8000RPM | 高 | 大型小车 |
| 减速电机 | 6-12V | 0.5-2A | 100-500RPM | 很高 | 需要大扭矩场景 |

### C. 故障诊断流程图

```
电机不转？
  ├─ 检查电源
  │   ├─ 电压正常？
  │   │   ├─ 是 → 检查接线
  │   │   └─ 否 → 修复电源
  │   └─ 电流充足？
  │       ├─ 是 → 继续
  │       └─ 否 → 更换电源
  │
  ├─ 检查信号
  │   ├─ PWM输出正常？
  │   │   ├─ 是 → 检查方向信号
  │   │   └─ 否 → 检查代码/引脚
  │   └─ IN1/IN2电平正确？
  │       ├─ 是 → 检查L298N
  │       └─ 否 → 修复代码
  │
  └─ 检查硬件
      ├─ L298N发热？
      │   ├─ 是 → 可能短路或过载
      │   └─ 否 → 检查电机
      └─ 电机本身正常？
          ├─ 是 → 检查驱动电路
          └─ 否 → 更换电机
```

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 分享你的项目成果，与其他学习者交流
- 发现文档错误？请提交Issue帮助我们改进

**版权声明**：本教程采用 CC BY-SA 4.0 协议，欢迎分享和改编，但请注明出处。
