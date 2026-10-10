---
title: "PID控制算法实战"
description: "深入学习PID控制算法的原理、参数整定方法、数字实现技巧、抗积分饱和策略，掌握电机速度控制、温度控制等实际应用"
slug: "pid-control-tutorial"

# 分类信息
domain: "底层硬件层"
module: "执行器控制"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - PID控制
  - 控制算法
  - 参数整定
  - 电机控制
  - 闭环控制
  - 自动控制
prerequisites:
  - "dc-motor-control-tutorial"
  - "pwm-advanced-techniques"
related_contents:
  - "bldc-motor-control"
  - "encoder-interface"

# 学习信息
estimated_time: 80
difficulty_score: 4

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
  - PID控制算法
  - 参数整定
  - 闭环控制
  - 电机速度控制
  - 温度控制
  - 自动控制系统
cover_image: ""
---

# PID控制算法实战

## 学习目标

完成本教程后，你将能够：


- [ ] 理解PID控制器的工作原理和数学模型
- [ ] 掌握比例(P)、积分(I)、微分(D)三个环节的作用
- [ ] 学会PID参数整定的多种方法
- [ ] 实现数字PID控制器
- [ ] 掌握抗积分饱和和微分滤波技术
- [ ] 应用PID控制器实现电机速度控制

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 理解闭环控制系统的基本概念
- 掌握PWM技术和电机控制基础
- 了解基本的数学运算（加减乘除）
- 熟悉C语言编程

**技能要求**：
- 能够使用STM32或Arduino开发环境
- 会使用串口调试工具
- 能够编写定时器中断程序
- 具备基本的调试能力

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考价格 |
|------|------|------|----------|
| 开发板 | 1 | STM32F103或Arduino Uno | ¥30-50 |
| 直流电机 | 1 | 带编码器，12V | ¥40-80 |
| 电机驱动模块 | 1 | L298N或TB6612 | ¥10-20 |
| 电源 | 1 | 12V，2A以上 | ¥20-40 |
| 编码器 | 1 | 如电机自带则不需要 | ¥15-30 |
| 杜邦线 | 若干 | 公对公、公对母 | ¥5 |

### 软件准备

**STM32平台**：
- STM32CubeIDE 或 Keil MDK
- ST-Link驱动程序
- 串口调试助手

**Arduino平台**：
- Arduino IDE 1.8.x 或 2.x
- USB驱动程序
- 串口监视器


## 理论基础

### 什么是PID控制？

PID（Proportional-Integral-Derivative）控制器是工业控制中最常用的控制算法。它通过计算误差的比例、积分和微分来产生控制输出，使系统输出跟踪期望值。

**基本框图**：

```
设定值(Setpoint)
      │
      ├──────> [比例P] ──┐
      │                  │
      ├──────> [积分I] ──┼──> [求和] ──> 控制输出
      │                  │
      └──────> [微分D] ──┘
                         │
                         └──────> 执行器 ──> 被控对象
                                              │
                                              └──> 反馈测量
```

### PID数学模型

**连续时间PID方程**：

```
u(t) = Kp × e(t) + Ki × ∫e(t)dt + Kd × de(t)/dt

其中：
u(t) = 控制输出
e(t) = 误差 = 设定值 - 实际值
Kp = 比例系数
Ki = 积分系数
Kd = 微分系数
```

**离散时间PID方程**（用于数字实现）：

```
u(k) = Kp × e(k) + Ki × Σe(k) + Kd × [e(k) - e(k-1)]

其中：
k = 当前采样时刻
e(k) = 当前误差
Σe(k) = 误差累积和
e(k-1) = 上一次误差
```


### 三个环节的作用

**1. 比例环节（P）**

- **作用**：根据当前误差大小产生控制作用
- **特点**：响应快，但存在稳态误差
- **效果**：Kp越大，响应越快，但容易超调和振荡

```
比例输出 = Kp × 误差

示例：
误差 = 100，Kp = 2.0
比例输出 = 2.0 × 100 = 200
```

**2. 积分环节（I）**

- **作用**：消除稳态误差
- **特点**：累积历史误差，直到误差为零
- **效果**：Ki越大，消除误差越快，但容易积分饱和

```
积分输出 = Ki × Σ误差

示例：
误差历史 = [10, 8, 6, 4, 2]
Ki = 0.1
积分输出 = 0.1 × (10+8+6+4+2) = 3.0
```

**3. 微分环节（D）**

- **作用**：预测误差变化趋势，提前调节
- **特点**：对误差变化率敏感
- **效果**：Kd越大，超调越小，但对噪声敏感

```
微分输出 = Kd × (当前误差 - 上次误差)

示例：
当前误差 = 50，上次误差 = 60
Kd = 0.5
微分输出 = 0.5 × (50 - 60) = -5
```

### PID控制效果对比

| 控制器类型 | 响应速度 | 稳态误差 | 超调 | 稳定性 | 适用场景 |
|-----------|---------|---------|------|--------|---------|
| P | 快 | 有 | 中等 | 较好 | 简单系统 |
| PI | 中等 | 无 | 较大 | 好 | 大多数系统 |
| PD | 快 | 有 | 小 | 较好 | 快速响应系统 |
| PID | 快 | 无 | 可调 | 最好 | 复杂系统 |


## 步骤1：基础PID控制器实现

### 1.1 PID结构体定义

```c
// PID控制器结构体
typedef struct {
    // PID参数
    float Kp;              // 比例系数
    float Ki;              // 积分系数
    float Kd;              // 微分系数
    
    // 中间变量
    float setpoint;        // 设定值（目标值）
    float measured;        // 测量值（实际值）
    float error;           // 当前误差
    float last_error;      // 上次误差
    float integral;        // 积分累积
    float derivative;      // 微分值
    
    // 输出限制
    float output_min;      // 输出最小值
    float output_max;      // 输出最大值
    float output;          // 控制输出
    
    // 采样时间
    float sample_time;     // 采样周期（秒）
    
} PID_Controller;

// 初始化PID控制器
void PID_Init(PID_Controller *pid, float kp, float ki, float kd) {
    pid->Kp = kp;
    pid->Ki = ki;
    pid->Kd = kd;
    
    pid->setpoint = 0.0f;
    pid->measured = 0.0f;
    pid->error = 0.0f;
    pid->last_error = 0.0f;
    pid->integral = 0.0f;
    pid->derivative = 0.0f;
    
    pid->output_min = 0.0f;
    pid->output_max = 100.0f;
    pid->output = 0.0f;
    
    pid->sample_time = 0.01f;  // 默认10ms
}

// 设置输出限制
void PID_SetOutputLimits(PID_Controller *pid, float min, float max) {
    pid->output_min = min;
    pid->output_max = max;
}

// 设置采样时间
void PID_SetSampleTime(PID_Controller *pid, float sample_time) {
    pid->sample_time = sample_time;
}
```


### 1.2 基础PID计算函数

```c
// PID计算函数（位置式PID）
float PID_Compute(PID_Controller *pid, float setpoint, float measured) {
    // 更新设定值和测量值
    pid->setpoint = setpoint;
    pid->measured = measured;
    
    // 计算误差
    pid->error = pid->setpoint - pid->measured;
    
    // 比例项
    float p_term = pid->Kp * pid->error;
    
    // 积分项
    pid->integral += pid->error * pid->sample_time;
    float i_term = pid->Ki * pid->integral;
    
    // 微分项
    pid->derivative = (pid->error - pid->last_error) / pid->sample_time;
    float d_term = pid->Kd * pid->derivative;
    
    // PID输出
    pid->output = p_term + i_term + d_term;
    
    // 输出限幅
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }
    
    // 保存当前误差
    pid->last_error = pid->error;
    
    return pid->output;
}

// 重置PID控制器
void PID_Reset(PID_Controller *pid) {
    pid->error = 0.0f;
    pid->last_error = 0.0f;
    pid->integral = 0.0f;
    pid->derivative = 0.0f;
    pid->output = 0.0f;
}
```

### 1.3 测试代码

```c
// 测试PID控制器
void Test_PID_Basic(void) {
    PID_Controller pid;
    
    // 初始化PID（Kp=2.0, Ki=0.5, Kd=0.1）
    PID_Init(&pid, 2.0f, 0.5f, 0.1f);
    PID_SetOutputLimits(&pid, 0.0f, 100.0f);
    PID_SetSampleTime(&pid, 0.01f);  // 10ms
    
    // 模拟控制过程
    float setpoint = 100.0f;  // 目标值
    float measured = 0.0f;    // 当前值
    
    printf("Time(s)\tSetpoint\tMeasured\tError\tOutput\n");
    
    for (int i = 0; i < 200; i++) {
        // 计算PID输出
        float output = PID_Compute(&pid, setpoint, measured);
        
        // 模拟系统响应（简化的一阶系统）
        measured += (output - measured) * 0.1f;
        
        // 每10次打印一次
        if (i % 10 == 0) {
            printf("%.2f\t%.1f\t%.1f\t%.1f\t%.1f\n",
                   i * 0.01f, setpoint, measured, pid.error, output);
        }
        
        HAL_Delay(10);  // 10ms采样周期
    }
}
```


## 步骤2：抗积分饱和

### 2.1 积分饱和问题

当系统存在饱和限制时（如PWM占空比0-100%），积分项可能会持续累积，导致：
- 超调增大
- 调节时间延长
- 系统响应变慢

**示例**：
```
目标速度 = 1000 RPM
当前速度 = 0 RPM
误差 = 1000

如果没有抗饱和措施：
积分项会持续累积，即使输出已经达到100%
当速度接近目标时，积分项仍然很大
导致严重超调
```

### 2.2 积分限幅法

最简单的方法是限制积分项的范围：

```c
// 带积分限幅的PID计算
float PID_Compute_AntiWindup(PID_Controller *pid, float setpoint, float measured) {
    pid->setpoint = setpoint;
    pid->measured = measured;
    pid->error = pid->setpoint - pid->measured;
    
    // 比例项
    float p_term = pid->Kp * pid->error;
    
    // 积分项（带限幅）
    pid->integral += pid->error * pid->sample_time;
    
    // 计算积分限幅值
    float integral_max = (pid->output_max - pid->output_min) / pid->Ki;
    
    // 限制积分项
    if (pid->integral > integral_max) {
        pid->integral = integral_max;
    } else if (pid->integral < -integral_max) {
        pid->integral = -integral_max;
    }
    
    float i_term = pid->Ki * pid->integral;
    
    // 微分项
    pid->derivative = (pid->error - pid->last_error) / pid->sample_time;
    float d_term = pid->Kd * pid->derivative;
    
    // PID输出
    pid->output = p_term + i_term + d_term;
    
    // 输出限幅
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }
    
    pid->last_error = pid->error;
    
    return pid->output;
}
```


### 2.3 条件积分法

只在误差较小时进行积分：

```c
// 条件积分法
float PID_Compute_ConditionalIntegral(PID_Controller *pid, 
                                      float setpoint, float measured) {
    pid->setpoint = setpoint;
    pid->measured = measured;
    pid->error = pid->setpoint - pid->measured;
    
    // 比例项
    float p_term = pid->Kp * pid->error;
    
    // 条件积分：只在误差较小时积分
    float error_threshold = 10.0f;  // 误差阈值
    if (fabs(pid->error) < error_threshold) {
        pid->integral += pid->error * pid->sample_time;
    }
    
    float i_term = pid->Ki * pid->integral;
    
    // 微分项
    pid->derivative = (pid->error - pid->last_error) / pid->sample_time;
    float d_term = pid->Kd * pid->derivative;
    
    // PID输出
    pid->output = p_term + i_term + d_term;
    
    // 输出限幅
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }
    
    pid->last_error = pid->error;
    
    return pid->output;
}
```

### 2.4 反向计算法（推荐）

当输出饱和时，反向计算积分项：

```c
// 反向计算抗饱和
float PID_Compute_BackCalculation(PID_Controller *pid, 
                                   float setpoint, float measured) {
    pid->setpoint = setpoint;
    pid->measured = measured;
    pid->error = pid->setpoint - pid->measured;
    
    // 比例项
    float p_term = pid->Kp * pid->error;
    
    // 积分项
    pid->integral += pid->error * pid->sample_time;
    float i_term = pid->Ki * pid->integral;
    
    // 微分项
    pid->derivative = (pid->error - pid->last_error) / pid->sample_time;
    float d_term = pid->Kd * pid->derivative;
    
    // 计算未限幅的输出
    float output_unsat = p_term + i_term + d_term;
    
    // 输出限幅
    pid->output = output_unsat;
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }
    
    // 反向计算积分项（抗饱和）
    if (output_unsat != pid->output) {
        // 输出饱和，调整积分项
        float Kb = 1.0f / pid->Ki;  // 反向计算系数
        pid->integral += Kb * (pid->output - output_unsat) * pid->sample_time;
    }
    
    pid->last_error = pid->error;
    
    return pid->output;
}
```


## 步骤3：微分滤波

### 3.1 微分噪声问题

微分项对测量噪声非常敏感，会导致：
- 控制输出剧烈波动
- 执行器频繁动作
- 系统不稳定

**解决方法**：对微分项进行低通滤波

### 3.2 一阶低通滤波器

```c
// 带微分滤波的PID结构体
typedef struct {
    float Kp, Ki, Kd;
    float setpoint, measured;
    float error, last_error;
    float integral, derivative;
    float output_min, output_max, output;
    float sample_time;
    
    // 微分滤波参数
    float derivative_filtered;  // 滤波后的微分值
    float filter_coefficient;   // 滤波系数 (0-1)
    
} PID_Controller_Filtered;

// 初始化带滤波的PID
void PID_Init_Filtered(PID_Controller_Filtered *pid, 
                       float kp, float ki, float kd, float filter_coef) {
    pid->Kp = kp;
    pid->Ki = ki;
    pid->Kd = kd;
    
    pid->setpoint = 0.0f;
    pid->measured = 0.0f;
    pid->error = 0.0f;
    pid->last_error = 0.0f;
    pid->integral = 0.0f;
    pid->derivative = 0.0f;
    pid->derivative_filtered = 0.0f;
    
    pid->output_min = 0.0f;
    pid->output_max = 100.0f;
    pid->output = 0.0f;
    
    pid->sample_time = 0.01f;
    pid->filter_coefficient = filter_coef;  // 典型值：0.1-0.3
}

// 带微分滤波的PID计算
float PID_Compute_Filtered(PID_Controller_Filtered *pid, 
                           float setpoint, float measured) {
    pid->setpoint = setpoint;
    pid->measured = measured;
    pid->error = pid->setpoint - pid->measured;
    
    // 比例项
    float p_term = pid->Kp * pid->error;
    
    // 积分项（带抗饱和）
    pid->integral += pid->error * pid->sample_time;
    float integral_max = (pid->output_max - pid->output_min) / pid->Ki;
    if (pid->integral > integral_max) {
        pid->integral = integral_max;
    } else if (pid->integral < -integral_max) {
        pid->integral = -integral_max;
    }
    float i_term = pid->Ki * pid->integral;
    
    // 微分项（带低通滤波）
    pid->derivative = (pid->error - pid->last_error) / pid->sample_time;
    
    // 一阶低通滤波
    // filtered = α × new + (1-α) × old
    pid->derivative_filtered = pid->filter_coefficient * pid->derivative + 
                               (1.0f - pid->filter_coefficient) * pid->derivative_filtered;
    
    float d_term = pid->Kd * pid->derivative_filtered;
    
    // PID输出
    pid->output = p_term + i_term + d_term;
    
    // 输出限幅
    if (pid->output > pid->output_max) {
        pid->output = pid->output_max;
    } else if (pid->output < pid->output_min) {
        pid->output = pid->output_min;
    }
    
    pid->last_error = pid->error;
    
    return pid->output;
}
```


## 步骤4：增量式PID

### 4.1 位置式 vs 增量式

**位置式PID**：
- 输出是绝对值
- 需要累积所有历史误差
- 适合需要绝对位置控制的场合

**增量式PID**：
- 输出是增量值
- 只需要最近几次误差
- 适合需要增量控制的场合（如PWM调节）

### 4.2 增量式PID实现

```c
// 增量式PID结构体
typedef struct {
    float Kp, Ki, Kd;
    float error;           // 当前误差 e(k)
    float last_error;      // 上次误差 e(k-1)
    float prev_error;      // 上上次误差 e(k-2)
    float output_min, output_max;
    float sample_time;
} PID_Incremental;

// 初始化增量式PID
void PID_Incremental_Init(PID_Incremental *pid, float kp, float ki, float kd) {
    pid->Kp = kp;
    pid->Ki = ki;
    pid->Kd = kd;
    pid->error = 0.0f;
    pid->last_error = 0.0f;
    pid->prev_error = 0.0f;
    pid->output_min = -100.0f;
    pid->output_max = 100.0f;
    pid->sample_time = 0.01f;
}

// 增量式PID计算
float PID_Incremental_Compute(PID_Incremental *pid, 
                              float setpoint, float measured) {
    // 计算当前误差
    pid->error = setpoint - measured;
    
    // 增量式PID公式
    // Δu(k) = Kp[e(k)-e(k-1)] + Ki×e(k) + Kd[e(k)-2e(k-1)+e(k-2)]
    float delta_output = pid->Kp * (pid->error - pid->last_error) +
                         pid->Ki * pid->error * pid->sample_time +
                         pid->Kd * (pid->error - 2*pid->last_error + pid->prev_error) / pid->sample_time;
    
    // 限制增量范围
    if (delta_output > pid->output_max) {
        delta_output = pid->output_max;
    } else if (delta_output < pid->output_min) {
        delta_output = pid->output_min;
    }
    
    // 更新误差历史
    pid->prev_error = pid->last_error;
    pid->last_error = pid->error;
    
    return delta_output;  // 返回增量值
}

// 使用示例
void Example_Incremental_PID(void) {
    PID_Incremental pid;
    PID_Incremental_Init(&pid, 2.0f, 0.5f, 0.1f);
    
    float setpoint = 1000.0f;  // 目标速度
    float measured = 0.0f;     // 当前速度
    float pwm_duty = 50.0f;    // 当前PWM占空比
    
    for (int i = 0; i < 100; i++) {
        // 计算增量
        float delta_pwm = PID_Incremental_Compute(&pid, setpoint, measured);
        
        // 更新PWM占空比
        pwm_duty += delta_pwm;
        
        // 限制PWM范围
        if (pwm_duty > 100.0f) pwm_duty = 100.0f;
        if (pwm_duty < 0.0f) pwm_duty = 0.0f;
        
        // 应用PWM
        Set_Motor_PWM(pwm_duty);
        
        // 读取速度反馈
        measured = Read_Motor_Speed();
        
        HAL_Delay(10);
    }
}
```


## 步骤5：PID参数整定

### 5.1 参数整定方法概述

| 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 试凑法 | 简单直观 | 耗时，依赖经验 | 简单系统 |
| 临界比例法 | 系统化 | 可能不稳定 | 稳定系统 |
| 经验公式法 | 快速 | 精度一般 | 初步调试 |
| 自整定法 | 自动化 | 实现复杂 | 复杂系统 |

### 5.2 试凑法（推荐初学者）

**步骤1：只调Kp**
```
1. 设置 Ki=0, Kd=0
2. 从小到大增加Kp
3. 观察系统响应：
   - Kp太小：响应慢，误差大
   - Kp适中：响应快，有小幅振荡
   - Kp太大：振荡剧烈，不稳定
4. 选择响应快但不振荡的Kp值
```

**步骤2：增加Ki**
```
1. 保持Kp不变
2. 从小到大增加Ki
3. 观察系统响应：
   - Ki太小：稳态误差消除慢
   - Ki适中：快速消除稳态误差
   - Ki太大：超调大，振荡
4. 选择能快速消除误差但不超调的Ki值
```

**步骤3：增加Kd**
```
1. 保持Kp和Ki不变
2. 从小到大增加Kd
3. 观察系统响应：
   - Kd太小：超调较大
   - Kd适中：超调减小，响应平滑
   - Kd太大：响应变慢，对噪声敏感
4. 选择能减小超调的Kd值
```

### 5.3 经验公式法

根据系统类型选择初始参数：

**温度控制系统**：
```c
Kp = 10.0 ~ 50.0
Ki = 0.1 ~ 1.0
Kd = 1.0 ~ 5.0
```

**电机速度控制**：
```c
Kp = 0.5 ~ 5.0
Ki = 0.1 ~ 1.0
Kd = 0.01 ~ 0.5
```

**位置控制系统**：
```c
Kp = 1.0 ~ 10.0
Ki = 0.01 ~ 0.5
Kd = 0.1 ~ 2.0
```


### 5.4 在线整定工具

实现一个简单的在线整定工具：

```c
// 在线参数调整
void PID_Online_Tuning(void) {
    PID_Controller pid;
    PID_Init(&pid, 1.0f, 0.1f, 0.05f);
    PID_SetOutputLimits(&pid, 0.0f, 100.0f);
    
    float setpoint = 1000.0f;
    float measured = 0.0f;
    
    printf("PID Online Tuning Tool\n");
    printf("Commands:\n");
    printf("  p+/p- : Increase/Decrease Kp by 0.1\n");
    printf("  i+/i- : Increase/Decrease Ki by 0.01\n");
    printf("  d+/d- : Increase/Decrease Kd by 0.01\n");
    printf("  s : Show current parameters\n");
    printf("  r : Reset PID\n");
    printf("  q : Quit\n\n");
    
    while (1) {
        // 读取串口命令
        if (UART_Available()) {
            char cmd[3];
            UART_ReadString(cmd, 3);
            
            if (strcmp(cmd, "p+") == 0) {
                pid.Kp += 0.1f;
                printf("Kp = %.2f\n", pid.Kp);
            } else if (strcmp(cmd, "p-") == 0) {
                pid.Kp -= 0.1f;
                if (pid.Kp < 0) pid.Kp = 0;
                printf("Kp = %.2f\n", pid.Kp);
            } else if (strcmp(cmd, "i+") == 0) {
                pid.Ki += 0.01f;
                printf("Ki = %.3f\n", pid.Ki);
            } else if (strcmp(cmd, "i-") == 0) {
                pid.Ki -= 0.01f;
                if (pid.Ki < 0) pid.Ki = 0;
                printf("Ki = %.3f\n", pid.Ki);
            } else if (strcmp(cmd, "d+") == 0) {
                pid.Kd += 0.01f;
                printf("Kd = %.3f\n", pid.Kd);
            } else if (strcmp(cmd, "d-") == 0) {
                pid.Kd -= 0.01f;
                if (pid.Kd < 0) pid.Kd = 0;
                printf("Kd = %.3f\n", pid.Kd);
            } else if (strcmp(cmd, "s") == 0) {
                printf("Current Parameters:\n");
                printf("  Kp = %.2f\n", pid.Kp);
                printf("  Ki = %.3f\n", pid.Ki);
                printf("  Kd = %.3f\n", pid.Kd);
            } else if (strcmp(cmd, "r") == 0) {
                PID_Reset(&pid);
                printf("PID Reset\n");
            } else if (strcmp(cmd, "q") == 0) {
                break;
            }
        }
        
        // PID控制循环
        measured = Read_Motor_Speed();
        float output = PID_Compute(&pid, setpoint, measured);
        Set_Motor_PWM(output);
        
        // 定期输出状态
        static uint32_t last_print = 0;
        if (HAL_GetTick() - last_print > 500) {
            printf("SP:%.0f, PV:%.0f, Err:%.0f, Out:%.1f\n",
                   setpoint, measured, pid.error, output);
            last_print = HAL_GetTick();
        }
        
        HAL_Delay(10);
    }
}
```


## 步骤6：电机速度控制实战

### 6.1 硬件连接

```
STM32/Arduino          电机驱动(L298N)         直流电机
                                          
  PWM_A ---------> ENA                    
  IN1 ----------> IN1                    
  IN2 ----------> IN2                    
                      OUT1 ----------> 电机+
                      OUT2 ----------> 电机-
  
  ENCODER_A <--------- 编码器A相
  ENCODER_B <--------- 编码器B相
  
  GND ----------> GND
                      VCC <---------- 电源+ (12V)
                      GND <---------- 电源-
```

### 6.2 编码器速度测量

```c
// 编码器变量
volatile int32_t encoder_count = 0;
volatile int32_t last_encoder_count = 0;
float motor_speed_rpm = 0.0f;

// 编码器参数
#define ENCODER_PPR 360  // 编码器每转脉冲数
#define GEAR_RATIO 1.0f  // 减速比

// 编码器中断回调
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == ENCODER_A_PIN) {
        // 读取B相判断方向
        if (HAL_GPIO_ReadPin(ENCODER_B_PORT, ENCODER_B_PIN) == GPIO_PIN_SET) {
            encoder_count++;  // 正转
        } else {
            encoder_count--;  // 反转
        }
    }
}

// 计算速度（在定时器中断中调用，如10ms）
void Calculate_Motor_Speed(void) {
    // 计算脉冲差
    int32_t pulse_diff = encoder_count - last_encoder_count;
    last_encoder_count = encoder_count;
    
    // 计算RPM
    // RPM = (pulse_diff / PPR) × (60 / sample_time) / gear_ratio
    motor_speed_rpm = (float)pulse_diff / ENCODER_PPR * 
                      (60.0f / 0.01f) / GEAR_RATIO;
}

// 读取电机速度
float Read_Motor_Speed(void) {
    return motor_speed_rpm;
}
```


### 6.3 电机驱动函数

```c
// 电机方向枚举
typedef enum {
    MOTOR_FORWARD = 0,
    MOTOR_BACKWARD = 1,
    MOTOR_STOP = 2
} Motor_Direction;

// 设置电机速度和方向
void Set_Motor_Speed(float speed, Motor_Direction direction) {
    // 限制速度范围 0-100
    if (speed > 100.0f) speed = 100.0f;
    if (speed < 0.0f) speed = 0.0f;
    
    // 计算PWM占空比
    uint16_t pwm_value = (uint16_t)(speed * PWM_PERIOD / 100.0f);
    
    // 设置方向
    switch (direction) {
        case MOTOR_FORWARD:
            HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_SET);
            HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET);
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, pwm_value);
            break;
            
        case MOTOR_BACKWARD:
            HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_SET);
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, pwm_value);
            break;
            
        case MOTOR_STOP:
            HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET);
            __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
            break;
    }
}

// 应用PID输出到电机
void Apply_PID_Output(float pid_output) {
    if (pid_output > 0) {
        Set_Motor_Speed(pid_output, MOTOR_FORWARD);
    } else if (pid_output < 0) {
        Set_Motor_Speed(-pid_output, MOTOR_BACKWARD);
    } else {
        Set_Motor_Speed(0, MOTOR_STOP);
    }
}
```


### 6.4 完整的速度控制程序

```c
// 全局变量
PID_Controller speed_pid;
float target_speed = 0.0f;
uint8_t pid_enabled = 0;

// 初始化速度控制系统
void Speed_Control_Init(void) {
    // 初始化PID控制器
    PID_Init(&speed_pid, 2.0f, 0.5f, 0.1f);
    PID_SetOutputLimits(&speed_pid, -100.0f, 100.0f);
    PID_SetSampleTime(&speed_pid, 0.01f);  // 10ms
    
    // 初始化PWM
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    
    // 初始化编码器中断
    HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
    
    printf("Speed Control System Initialized\n");
}

// 速度控制任务（在10ms定时器中断中调用）
void Speed_Control_Task(void) {
    // 计算当前速度
    Calculate_Motor_Speed();
    
    if (pid_enabled) {
        // 读取当前速度
        float current_speed = Read_Motor_Speed();
        
        // PID计算
        float pid_output = PID_Compute(&speed_pid, target_speed, current_speed);
        
        // 应用到电机
        Apply_PID_Output(pid_output);
    }
}

// 主程序
int main(void) {
    // HAL初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM1_Init();
    MX_TIM2_Init();
    MX_USART1_UART_Init();
    
    // 初始化速度控制
    Speed_Control_Init();
    
    printf("\n=== Motor Speed Control with PID ===\n");
    printf("Commands:\n");
    printf("  s<speed> : Set target speed (e.g., s500)\n");
    printf("  e : Enable PID control\n");
    printf("  d : Disable PID control\n");
    printf("  p<value> : Set Kp (e.g., p2.5)\n");
    printf("  i<value> : Set Ki (e.g., i0.5)\n");
    printf("  k<value> : Set Kd (e.g., k0.1)\n");
    printf("  r : Reset PID\n");
    printf("  ? : Show status\n\n");
    
    // 启动10ms定时器中断
    HAL_TIM_Base_Start_IT(&htim2);
    
    while (1) {
        // 处理串口命令
        if (UART_Available()) {
            char cmd = UART_Read();
            
            switch (cmd) {
                case 's': {
                    // 设置目标速度
                    float speed;
                    scanf("%f", &speed);
                    target_speed = speed;
                    printf("Target speed set to: %.0f RPM\n", target_speed);
                    break;
                }
                
                case 'e':
                    pid_enabled = 1;
                    printf("PID control enabled\n");
                    break;
                    
                case 'd':
                    pid_enabled = 0;
                    Set_Motor_Speed(0, MOTOR_STOP);
                    printf("PID control disabled\n");
                    break;
                    
                case 'p': {
                    float kp;
                    scanf("%f", &kp);
                    speed_pid.Kp = kp;
                    printf("Kp set to: %.2f\n", kp);
                    break;
                }
                
                case 'i': {
                    float ki;
                    scanf("%f", &ki);
                    speed_pid.Ki = ki;
                    printf("Ki set to: %.3f\n", ki);
                    break;
                }
                
                case 'k': {
                    float kd;
                    scanf("%f", &kd);
                    speed_pid.Kd = kd;
                    printf("Kd set to: %.3f\n", kd);
                    break;
                }
                
                case 'r':
                    PID_Reset(&speed_pid);
                    printf("PID reset\n");
                    break;
                    
                case '?': {
                    float current_speed = Read_Motor_Speed();
                    printf("\n--- Status ---\n");
                    printf("PID: %s\n", pid_enabled ? "Enabled" : "Disabled");
                    printf("Target: %.0f RPM\n", target_speed);
                    printf("Current: %.0f RPM\n", current_speed);
                    printf("Error: %.0f RPM\n", speed_pid.error);
                    printf("Output: %.1f%%\n", speed_pid.output);
                    printf("Kp=%.2f, Ki=%.3f, Kd=%.3f\n", 
                           speed_pid.Kp, speed_pid.Ki, speed_pid.Kd);
                    printf("-------------\n\n");
                    break;
                }
            }
        }
        
        // 定期输出状态（每500ms）
        static uint32_t last_print = 0;
        if (HAL_GetTick() - last_print > 500 && pid_enabled) {
            float current_speed = Read_Motor_Speed();
            printf("Target:%.0f, Current:%.0f, Error:%.0f, Output:%.1f\n",
                   target_speed, current_speed, speed_pid.error, speed_pid.output);
            last_print = HAL_GetTick();
        }
        
        HAL_Delay(10);
    }
}

// 定时器中断回调（10ms）
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        Speed_Control_Task();
    }
}
```


## 步骤7：Arduino实现

### 7.1 Arduino完整代码

```cpp
// Arduino PID电机速度控制

// 引脚定义
const int MOTOR_PWM = 9;
const int MOTOR_IN1 = 7;
const int MOTOR_IN2 = 8;
const int ENCODER_A = 2;  // 中断引脚
const int ENCODER_B = 3;  // 中断引脚

// 编码器变量
volatile long encoder_count = 0;
long last_encoder_count = 0;
float motor_speed_rpm = 0.0;

// PID参数
float Kp = 2.0;
float Ki = 0.5;
float Kd = 0.1;

// PID变量
float setpoint = 0.0;
float measured = 0.0;
float error = 0.0;
float last_error = 0.0;
float integral = 0.0;
float derivative = 0.0;
float output = 0.0;

// 时间变量
unsigned long last_time = 0;
float sample_time = 0.01;  // 10ms

// 编码器参数
const int ENCODER_PPR = 360;

void setup() {
    Serial.begin(115200);
    
    // 配置引脚
    pinMode(MOTOR_PWM, OUTPUT);
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    pinMode(ENCODER_A, INPUT_PULLUP);
    pinMode(ENCODER_B, INPUT_PULLUP);
    
    // 配置编码器中断
    attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, RISING);
    
    // 配置PWM频率（31kHz）
    TCCR1B = TCCR1B & 0b11111000 | 0x01;
    
    Serial.println("Motor Speed Control with PID");
    Serial.println("Commands:");
    Serial.println("  s<speed> : Set target speed");
    Serial.println("  p<value> : Set Kp");
    Serial.println("  i<value> : Set Ki");
    Serial.println("  d<value> : Set Kd");
    Serial.println("  ? : Show status");
}

void loop() {
    // 处理串口命令
    if (Serial.available()) {
        char cmd = Serial.read();
        
        if (cmd == 's') {
            setpoint = Serial.parseFloat();
            Serial.print("Target speed: ");
            Serial.println(setpoint);
        } else if (cmd == 'p') {
            Kp = Serial.parseFloat();
            Serial.print("Kp = ");
            Serial.println(Kp);
        } else if (cmd == 'i') {
            Ki = Serial.parseFloat();
            Serial.print("Ki = ");
            Serial.println(Ki);
        } else if (cmd == 'd') {
            Kd = Serial.parseFloat();
            Serial.print("Kd = ");
            Serial.println(Kd);
        } else if (cmd == '?') {
            Serial.println("--- Status ---");
            Serial.print("Target: ");
            Serial.println(setpoint);
            Serial.print("Current: ");
            Serial.println(measured);
            Serial.print("Error: ");
            Serial.println(error);
            Serial.print("Output: ");
            Serial.println(output);
            Serial.print("Kp=");
            Serial.print(Kp);
            Serial.print(", Ki=");
            Serial.print(Ki);
            Serial.print(", Kd=");
            Serial.println(Kd);
        }
    }
    
    // PID控制循环（10ms）
    unsigned long current_time = millis();
    if (current_time - last_time >= 10) {
        last_time = current_time;
        
        // 计算速度
        calculateSpeed();
        
        // PID计算
        pidCompute();
        
        // 应用输出
        applyMotorOutput(output);
        
        // 定期输出（每500ms）
        static unsigned long last_print = 0;
        if (current_time - last_print >= 500) {
            Serial.print("SP:");
            Serial.print(setpoint);
            Serial.print(", PV:");
            Serial.print(measured);
            Serial.print(", Err:");
            Serial.print(error);
            Serial.print(", Out:");
            Serial.println(output);
            last_print = current_time;
        }
    }
}

// 编码器中断服务函数
void encoderISR() {
    if (digitalRead(ENCODER_B) == HIGH) {
        encoder_count++;
    } else {
        encoder_count--;
    }
}

// 计算速度
void calculateSpeed() {
    long pulse_diff = encoder_count - last_encoder_count;
    last_encoder_count = encoder_count;
    
    // 计算RPM
    motor_speed_rpm = (float)pulse_diff / ENCODER_PPR * (60.0 / sample_time);
    measured = motor_speed_rpm;
}

// PID计算
void pidCompute() {
    // 计算误差
    error = setpoint - measured;
    
    // 比例项
    float p_term = Kp * error;
    
    // 积分项（带抗饱和）
    integral += error * sample_time;
    float integral_max = 100.0 / Ki;
    if (integral > integral_max) integral = integral_max;
    if (integral < -integral_max) integral = -integral_max;
    float i_term = Ki * integral;
    
    // 微分项
    derivative = (error - last_error) / sample_time;
    float d_term = Kd * derivative;
    
    // PID输出
    output = p_term + i_term + d_term;
    
    // 输出限幅
    if (output > 100.0) output = 100.0;
    if (output < -100.0) output = -100.0;
    
    // 保存误差
    last_error = error;
}

// 应用电机输出
void applyMotorOutput(float pwm_value) {
    if (pwm_value > 0) {
        // 正转
        digitalWrite(MOTOR_IN1, HIGH);
        digitalWrite(MOTOR_IN2, LOW);
        analogWrite(MOTOR_PWM, (int)(pwm_value * 2.55));
    } else if (pwm_value < 0) {
        // 反转
        digitalWrite(MOTOR_IN1, LOW);
        digitalWrite(MOTOR_IN2, HIGH);
        analogWrite(MOTOR_PWM, (int)(-pwm_value * 2.55));
    } else {
        // 停止
        digitalWrite(MOTOR_IN1, LOW);
        digitalWrite(MOTOR_IN2, LOW);
        analogWrite(MOTOR_PWM, 0);
    }
}
```


## 调试技巧

### 1. 数据可视化

使用串口绘图工具（如Arduino Serial Plotter）实时观察PID效果：

```c
// 输出格式化数据用于绘图
void Print_For_Plotter(void) {
    printf("Setpoint:%d,Measured:%d,Output:%d\n",
           (int)target_speed,
           (int)Read_Motor_Speed(),
           (int)speed_pid.output);
}
```

### 2. 常见问题排查

**问题1：电机不转**
- 检查电源电压是否足够
- 检查PWM信号是否正常
- 检查电机驱动器连接
- 检查PID输出是否为0

**问题2：速度振荡**
- Kp过大，减小Kp
- Ki过大，减小Ki
- 增加微分项Kd
- 检查编码器信号质量

**问题3：响应慢**
- Kp过小，增大Kp
- Ki过小，增大Ki
- 检查采样周期是否合适
- 检查电机负载是否过大

**问题4：超调严重**
- Ki过大，减小Ki
- 增加Kd
- 检查抗积分饱和是否生效
- 使用软启动

**问题5：稳态误差大**
- Ki过小，增大Ki
- 检查积分项是否工作
- 检查输出是否饱和
- 检查速度测量精度

### 3. 性能评估指标

```c
// 性能评估
typedef struct {
    float rise_time;        // 上升时间（10%-90%）
    float settling_time;    // 稳定时间（进入±5%范围）
    float overshoot;        // 超调量（%）
    float steady_error;     // 稳态误差
} PID_Performance;

void Evaluate_PID_Performance(PID_Performance *perf) {
    // 记录响应曲线
    // 计算性能指标
    // 输出评估结果
}
```


## 进阶应用

### 1. 串级PID控制

用于位置控制系统，外环控制位置，内环控制速度：

```c
// 串级PID结构
typedef struct {
    PID_Controller position_pid;  // 外环：位置PID
    PID_Controller speed_pid;     // 内环：速度PID
} Cascade_PID;

// 串级PID计算
float Cascade_PID_Compute(Cascade_PID *cascade, 
                          float target_position, 
                          float current_position,
                          float current_speed) {
    // 外环：位置PID，输出为目标速度
    float target_speed = PID_Compute(&cascade->position_pid, 
                                      target_position, 
                                      current_position);
    
    // 内环：速度PID，输出为PWM
    float pwm_output = PID_Compute(&cascade->speed_pid, 
                                    target_speed, 
                                    current_speed);
    
    return pwm_output;
}
```

### 2. 前馈控制

结合前馈和反馈控制，提高响应速度：

```c
// 前馈+PID控制
float Feedforward_PID_Compute(PID_Controller *pid, 
                              float setpoint, 
                              float measured,
                              float feedforward_gain) {
    // 前馈项
    float feedforward = feedforward_gain * setpoint;
    
    // 反馈项（PID）
    float feedback = PID_Compute(pid, setpoint, measured);
    
    // 总输出
    float output = feedforward + feedback;
    
    // 限幅
    if (output > pid->output_max) output = pid->output_max;
    if (output < pid->output_min) output = pid->output_min;
    
    return output;
}
```

### 3. 自适应PID

根据系统状态自动调整PID参数：

```c
// 自适应PID
void Adaptive_PID_Compute(PID_Controller *pid, 
                          float setpoint, 
                          float measured) {
    float error = setpoint - measured;
    float error_abs = fabs(error);
    
    // 根据误差大小调整参数
    if (error_abs > 100.0f) {
        // 误差大：增大Kp，减小Ki和Kd
        pid->Kp = 3.0f;
        pid->Ki = 0.2f;
        pid->Kd = 0.05f;
    } else if (error_abs > 20.0f) {
        // 误差中等：正常参数
        pid->Kp = 2.0f;
        pid->Ki = 0.5f;
        pid->Kd = 0.1f;
    } else {
        // 误差小：减小Kp，增大Ki
        pid->Kp = 1.0f;
        pid->Ki = 0.8f;
        pid->Kd = 0.15f;
    }
    
    // 执行PID计算
    PID_Compute(pid, setpoint, measured);
}
```


## 实战练习

### 练习1：温度控制

使用PID控制加热器，维持恒定温度：

**任务**：
1. 读取温度传感器（如DS18B20）
2. 使用PID控制PWM输出
3. 驱动加热器（通过MOSFET）
4. 目标：将温度稳定在设定值±1°C

**提示**：
- 温度系统响应慢，采样周期可设为1秒
- Kp建议范围：5-20
- Ki建议范围：0.1-1.0
- Kd建议范围：1-10

### 练习2：平衡小车

使用PID控制平衡小车姿态：

**任务**：
1. 读取MPU6050姿态角
2. 使用PID计算电机输出
3. 控制两个电机保持平衡
4. 目标：小车能够自主平衡

**提示**：
- 需要快速响应，采样周期10ms
- 可能需要串级PID（角度+角速度）
- 参数整定需要耐心

### 练习3：位置跟踪

使用编码器实现精确位置控制：

**任务**：
1. 读取编码器位置
2. 使用串级PID（位置+速度）
3. 实现精确定位
4. 目标：定位精度±5个脉冲

**提示**：
- 外环（位置）：Kp=0.5-2.0, Ki=0, Kd=0
- 内环（速度）：Kp=1.0-3.0, Ki=0.3-1.0, Kd=0.05-0.2


## 总结

### 关键要点

1. **PID三个环节**：
   - P（比例）：快速响应，但有稳态误差
   - I（积分）：消除稳态误差，但可能超调
   - D（微分）：减少超调，但对噪声敏感

2. **数字实现要点**：
   - 使用离散化公式
   - 注意采样周期的影响
   - 实现抗积分饱和
   - 对微分项进行滤波

3. **参数整定原则**：
   - 先P后I再D
   - 从小到大逐步调整
   - 观察系统响应曲线
   - 根据实际效果微调

4. **常见问题**：
   - 积分饱和：使用抗饱和措施
   - 微分噪声：使用低通滤波
   - 参数不当：系统化整定
   - 采样周期：根据系统特性选择

### 学习检查清单

完成本教程后，你应该能够：

- [x] 理解PID控制器的工作原理
- [x] 实现基础的位置式PID
- [x] 实现增量式PID
- [x] 处理积分饱和问题
- [x] 对微分项进行滤波
- [x] 整定PID参数
- [x] 应用PID控制电机速度
- [x] 调试和优化PID性能

### 下一步学习

- **高级控制算法**：模糊PID、神经网络PID
- **状态空间控制**：现代控制理论
- **模型预测控制**：MPC算法
- **自适应控制**：参数自整定
- **鲁棒控制**：H∞控制、滑模控制

### 参考资源

**书籍**：
- 《自动控制原理》- 胡寿松
- 《PID控制器参数整定方法》
- 《嵌入式系统控制算法》

**在线资源**：
- PID控制器仿真工具
- Arduino PID库文档
- STM32 PID应用笔记

**开源项目**：
- Arduino PID Library
- STM32 Motor Control SDK
- ROS PID Controller

## 附录

### A. 完整代码仓库

完整的示例代码可在以下仓库获取：
- GitHub: [embedded-pid-control-examples]
- 包含STM32和Arduino完整工程
- 包含测试数据和调试工具

### B. PID参数速查表

| 应用场景 | Kp | Ki | Kd | 采样周期 |
|---------|----|----|----|----|
| 电机速度控制 | 1-5 | 0.1-1.0 | 0.01-0.5 | 10ms |
| 温度控制 | 5-20 | 0.1-1.0 | 1-10 | 1s |
| 位置控制 | 1-10 | 0.01-0.5 | 0.1-2.0 | 10ms |
| 压力控制 | 2-10 | 0.1-1.0 | 0.1-1.0 | 100ms |

### C. 故障排查流程图

```
电机不转？
  ├─ 检查电源
  ├─ 检查PWM信号
  ├─ 检查驱动器
  └─ 检查PID输出

速度振荡？
  ├─ 减小Kp
  ├─ 减小Ki
  ├─ 增大Kd
  └─ 检查编码器

响应慢？
  ├─ 增大Kp
  ├─ 增大Ki
  └─ 检查负载

稳态误差大？
  ├─ 增大Ki
  ├─ 检查积分项
  └─ 检查输出饱和
```

---

**作者**: 嵌入式知识平台  
**最后更新**: 2024-01-15  
**版本**: 1.0

如有问题或建议，欢迎反馈！
