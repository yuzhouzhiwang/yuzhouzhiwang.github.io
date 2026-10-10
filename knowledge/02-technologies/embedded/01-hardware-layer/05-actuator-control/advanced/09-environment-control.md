---
title: "环境监控与联动控制系统"
description: "完整的环境监控系统，集成温湿度、CO2、光照等多路传感器，通过规则引擎驱动继电器联动控制空调、风扇、灯光等设备，支持阈值告警和数据记录。深入讲解HVAC控制理论、PID算法、能效优化、传感器布置标准及完整温室控制项目实战"
slug: "environment-monitoring-control-system"

domain: "底层硬件层"
module: "执行器控制"
content_type: "project"
skill_level: "advanced"

tags:
  - 环境监控
  - 传感器联动
  - 继电器控制
  - 规则引擎
  - 智能控制
  - HVAC控制
  - PID算法
  - 温室自动化
  - 能效优化
  - 物联网
prerequisites:
  - "beginner/04-relay-control"
  - "../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol"
related_contents:
  - "advanced/07-smart-socket-project"
  - "advanced/08-automation-system"
  - "../../../04-sensor-technology/intermediate/04-accelerometer-gyroscope"
  - "../../../07-cloud-backend/03-data-analysis-visualization/beginner/03-data-visualization"

estimated_time: 300
difficulty_score: 4

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "1.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - 环境监控系统
  - 传感器联动控制
  - 智能环境控制
  - 温湿度控制
  - 规则引擎
  - HVAC控制理论
  - PID温度控制
  - 温室自动化
  - 能效优化
  - Grafana可视化
cover_image: ""
---

# 环境监控与联动控制系统

## 项目概述

本项目构建一个多传感器环境监控与联动控制系统，适用于温室大棚、机房、仓库等场景：

## 背景知识

### HVAC控制理论基础

环境控制系统的核心是HVAC（Heating, Ventilation, and Air Conditioning，供暖通风与空调）控制理论。不同于简单的开关控制，现代环境控制需要考虑多个因素：

**控制策略对比**：

| 控制方式 | 原理 | 优点 | 缺点 | 适用场景 |
|---------|------|------|------|---------|
| On-Off控制 | 超过阈值开启，低于阈值关闭 | 简单可靠 | 频繁开关，温度波动大 | 低精度场景 |
| 滞回控制 | 设置上下限，形成死区 | 减少开关次数 | 仍有温度波动 | 一般应用 |
| PID控制 | 比例-积分-微分反馈 | 精确稳定 | 参数调试复杂 | 高精度要求 |
| 模糊控制 | 基于规则的模糊推理 | 适应性强 | 需要专家知识 | 复杂多变环境 |

**死区（Deadband）与滞回（Hysteresis）**：

```
温度控制示例：
  目标温度：25°C
  死区：±1°C
  
  控制逻辑：
    温度 > 26°C → 开启空调
    温度 < 24°C → 关闭空调
    24°C ≤ 温度 ≤ 26°C → 保持当前状态
  
  优势：
    - 避免在目标温度附近频繁开关
    - 延长设备寿命
    - 降低能耗
```

**时间常数与响应特性**：

环境系统具有大时间常数特性（thermal inertia，热惯性）：

```
典型时间常数：
  小房间（20m²）：τ ≈ 10~15分钟
  温室大棚（100m²）：τ ≈ 30~60分钟
  大型机房（500m²）：τ ≈ 2~4小时

控制周期选择：
  采样周期 T_s ≈ τ/10 ~ τ/20
  控制动作最小间隔 ≥ 2τ（避免过度控制）
```

### 传感器布置标准

根据ASHRAE（American Society of Heating, Refrigerating and Air-Conditioning Engineers，美国供暖、制冷与空调工程师学会）标准55-2020，传感器布置需遵循以下原则：

**温湿度传感器布置**：

```
高度要求：
  - 居住空间：距地面1.1~1.7m（人体活动区域）
  - 机房：距地面0.6m和1.8m各一个（冷热分层监测）
  - 温室：距地面0.5m、1.5m、2.5m（垂直温度梯度）

水平位置：
  - 避开门窗、空调出风口（至少1.5m距离）
  - 避开热源（电器、阳光直射）
  - 选择空气流通但不剧烈的位置
  - 多点布置时呈对角线或网格分布

响应时间：
  - 裸露传感器：τ₆₃ ≈ 10~30秒
  - 带防护罩：τ₆₃ ≈ 1~3分钟
  - 选择原则：响应时间 < 控制周期/5
```

**CO₂传感器布置**：

```
高度：
  - 办公室/教室：1.2~1.5m（呼吸区域）
  - 温室：0.3~0.5m（植物冠层，CO₂下沉）

注意事项：
  - 避开通风口（测量值不代表整体）
  - 定期校准（ABC自动基线校准，需要400ppm新鲜空气）
  - 预热时间：NDIR传感器需3~5分钟稳定
```

**光照传感器布置**：

```
位置：
  - 水平放置，朝向天空或主光源
  - 避免阴影遮挡
  - 温室：多点测量取平均（光照不均匀）

光谱响应：
  - BH1750：接近人眼响应曲线（适合照明控制）
  - 植物补光：需要PAR（Photosynthetically Active Radiation，光合有效辐射）传感器
```

### 能效优化原则

环境控制系统的能耗占建筑总能耗的40~60%，优化策略包括：

**最小开关次数策略**：

```c
// 继电器寿命与开关次数关系
// 典型5V继电器：机械寿命10万次，电气寿命（阻性负载）10万次

// 策略1：最小动作间隔
#define MIN_ACTION_INTERVAL_MS  (5 * 60 * 1000)  // 5分钟

typedef struct {
    uint32_t last_action_time;
    bool     current_state;
} RelayState;

bool relay_set_with_limit(uint8_t ch, bool on, RelayState *state) {
    uint32_t now = HAL_GetTick();
    if (state->current_state == on) return true;  // 已经是目标状态
    
    if (now - state->last_action_time < MIN_ACTION_INTERVAL_MS) {
        return false;  // 动作过于频繁，拒绝
    }
    
    relay_set(ch, on);
    state->last_action_time = now;
    state->current_state = on;
    return true;
}
```

**预测性控制**：

```c
// 基于温度变化率预测
float predict_temperature(float current_temp, float rate_per_min, float minutes) {
    return current_temp + rate_per_min * minutes;
}

// 示例：提前关闭加热器
void smart_heater_control(float temp, float target) {
    static float last_temp = 0;
    static uint32_t last_time = 0;
    
    uint32_t now = HAL_GetTick();
    float dt_min = (now - last_time) / 60000.0f;
    
    if (dt_min > 0.1f) {  // 至少6秒间隔
        float rate = (temp - last_temp) / dt_min;  // °C/min
        
        // 预测5分钟后温度
        float predicted = predict_temperature(temp, rate, 5.0f);
        
        if (predicted >= target) {
            relay_set(HEATER_CH, false);  // 提前关闭
        } else if (temp < target - 2.0f) {
            relay_set(HEATER_CH, true);
        }
        
        last_temp = temp;
        last_time = now;
    }
}
```

### 多参数耦合关系

环境参数之间存在复杂的耦合关系：

**温湿度耦合**：

```
相对湿度RH与绝对湿度AH的关系：
  RH = (AH / AH_sat(T)) × 100%
  
  其中AH_sat(T)是饱和绝对湿度，随温度指数增长：
  AH_sat(T) ≈ 5.018 + 0.32321×T + 0.0081847×T² + 0.00031243×T³ (g/m³)
  
  实际影响：
    - 温度升高1°C，相对湿度下降约3~5%
    - 加热时需同时加湿
    - 降温时可能结露（露点温度）
```

**CO₂与通风耦合**：

```
CO₂浓度变化模型（简化）：
  dC/dt = G - V×(C - C_out)
  
  其中：
    C：室内CO₂浓度(ppm)
    G：CO₂产生速率(ppm/h)，人均约20~40ppm/h
    V：换气次数(次/h)
    C_out：室外CO₂浓度(约400ppm)
  
  稳态浓度：
    C_ss = C_out + G/V
  
  示例：10人办公室，50m³空间
    G = 10人 × 30ppm/h = 300ppm/h
    要求C_ss < 1000ppm
    则V > 300/(1000-400) = 0.5次/h
    风量 = 50m³ × 0.5次/h = 25m³/h
```

**光照与温度耦合**：

```
补光灯热效应：
  LED补光灯：光效100~150lm/W，发热约50~60%
  100W LED灯 → 约50~60W热量
  
  温室补光时需考虑：
    - 冬季：补光同时提供热量（有利）
    - 夏季：补光增加制冷负担（需加强通风）
```

**监测参数**：
- 温度（DHT22）
- 湿度（DHT22）
- CO₂浓度（MH-Z19B）
- 光照强度（BH1750）
- 土壤湿度（电阻式，可选）

**控制输出**（继电器）：
- CH0：空调/加热器
- CH1：排风扇
- CH2：加湿器
- CH3：补光灯
- CH4：灌溉泵（可选）

**硬件清单**：

| 器件 | 型号 | 接口 |
|------|------|------|
| 主控 | STM32F103C8T6 | - |
| 温湿度 | DHT22 | 单总线 |
| CO₂传感器 | MH-Z19B | UART |
| 光照传感器 | BH1750 | I2C |
| 继电器 | 4路5V继电器板 | GPIO |
| 显示屏 | 0.96" OLED | I2C |
| 通信 | ESP8266 AT | UART |

## 硬件系统设计

**监测参数**：
- 温度（DHT22）
- 湿度（DHT22）
- CO₂浓度（MH-Z19B）
- 光照强度（BH1750）
- 土壤湿度（电阻式，可选）

**控制输出**（继电器）：
- CH0：空调/加热器
- CH1：排风扇
- CH2：加湿器
- CH3：补光灯
- CH4：灌溉泵（可选）

**硬件清单**：

| 器件 | 型号 | 接口 |
|------|------|------|
| 主控 | STM32F103C8T6 | - |
| 温湿度 | DHT22 | 单总线 |
| CO₂传感器 | MH-Z19B | UART |
| 光照传感器 | BH1750 | I2C |
| 继电器 | 4路5V继电器板 | GPIO |
| 显示屏 | 0.96" OLED | I2C |
| 通信 | ESP8266 AT | UART |

## 传感器驱动实现

### DHT22温湿度传感器

```c
#include "dht22.h"

typedef struct {
    float temperature;  // 摄氏度
    float humidity;     // 相对湿度%
    bool  valid;
} DHT22_Data;

// 单总线时序读取（需要精确延时）
DHT22_Data dht22_read(GPIO_TypeDef *port, uint16_t pin) {
    DHT22_Data data = {0, 0, false};
    uint8_t buf[5] = {0};

    // 主机发送起始信号：拉低至少1ms
    GPIO_SetOutput(port, pin);
    GPIO_Low(port, pin);
    HAL_Delay(2);
    GPIO_High(port, pin);
    delay_us(30);
    GPIO_SetInput(port, pin);

    // 等待DHT22响应（低80us + 高80us）
    uint32_t timeout = 200;
    while (GPIO_Read(port, pin) && --timeout);
    if (!timeout) return data;
    timeout = 200;
    while (!GPIO_Read(port, pin) && --timeout);
    if (!timeout) return data;
    timeout = 200;
    while (GPIO_Read(port, pin) && --timeout);

    // 读取40位数据
    for (int i = 0; i < 40; i++) {
        timeout = 200;
        while (!GPIO_Read(port, pin) && --timeout);  // 等待高电平
        delay_us(40);  // 等待40us后采样
        if (GPIO_Read(port, pin)) {
            buf[i/8] |= (1 << (7 - i%8));  // 高电平>40us = 1
        }
        timeout = 200;
        while (GPIO_Read(port, pin) && --timeout);   // 等待低电平
    }

    // 校验和
    if (buf[4] != ((buf[0]+buf[1]+buf[2]+buf[3]) & 0xFF)) return data;

    data.humidity    = ((buf[0] << 8) | buf[1]) / 10.0f;
    data.temperature = (((buf[2] & 0x7F) << 8) | buf[3]) / 10.0f;
    if (buf[2] & 0x80) data.temperature = -data.temperature;
    data.valid = true;
    return data;
}
```

### MH-Z19B CO₂传感器

```c
// MH-Z19B通过UART通信，发送读取命令获取CO₂浓度
uint16_t mhz19_read_co2(UART_HandleTypeDef *huart) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
    uint8_t resp[9] = {0};

    HAL_UART_Transmit(huart, cmd, 9, 100);
    HAL_UART_Receive(huart, resp, 9, 500);

    // 验证响应
    if (resp[0] != 0xFF || resp[1] != 0x86) return 0;

    // 校验和
    uint8_t checksum = 0;
    for (int i = 1; i < 8; i++) checksum += resp[i];
    checksum = 0xFF - checksum + 1;
    if (checksum != resp[8]) return 0;

    return (resp[2] << 8) | resp[3];  // CO₂浓度(ppm)
}
```

### BH1750光照传感器

```c
#define BH1750_ADDR  0x23  // ADDR引脚接GND

uint16_t bh1750_read_lux(void) {
    uint8_t cmd = 0x20;  // 单次高分辨率模式
    uint8_t buf[2];

    HAL_I2C_Master_Transmit(&hi2c1, BH1750_ADDR << 1, &cmd, 1, 100);
    HAL_Delay(180);  // 等待测量完成（最长180ms）
    HAL_I2C_Master_Receive(&hi2c1, BH1750_ADDR << 1, buf, 2, 100);

    uint16_t raw = (buf[0] << 8) | buf[1];
    return raw * 10 / 12;  // 转换为lux
}
```

### SHT31高精度温湿度传感器

SHT31相比DHT22具有更高精度（±0.3°C/±2%RH）和更快响应速度，适合高精度应用：

```c
#define SHT31_ADDR  0x44  // ADDR引脚接GND

typedef struct {
    float temperature;
    float humidity;
    bool  valid;
} SHT31_Data;

// CRC-8校验（多项式0x31）
static uint8_t sht31_crc8(const uint8_t *data, uint8_t len) {
    uint8_t crc = 0xFF;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) crc = (crc << 1) ^ 0x31;
            else            crc = (crc << 1);
        }
    }
    return crc;
}

SHT31_Data sht31_read(void) {
    SHT31_Data data = {0, 0, false};
    uint8_t cmd[2] = {0x24, 0x00};  // 单次测量，高重复性
    uint8_t buf[6];

    // 发送测量命令
    if (HAL_I2C_Master_Transmit(&hi2c1, SHT31_ADDR << 1, cmd, 2, 100) != HAL_OK)
        return data;

    HAL_Delay(15);  // 等待测量完成（高重复性模式需15ms）

    // 读取6字节数据：温度MSB, 温度LSB, 温度CRC, 湿度MSB, 湿度LSB, 湿度CRC
    if (HAL_I2C_Master_Receive(&hi2c1, SHT31_ADDR << 1, buf, 6, 100) != HAL_OK)
        return data;

    // 校验CRC
    if (sht31_crc8(&buf[0], 2) != buf[2]) return data;
    if (sht31_crc8(&buf[3], 2) != buf[5]) return data;

    // 转换温度：T = -45 + 175 × (raw / 65535)
    uint16_t temp_raw = (buf[0] << 8) | buf[1];
    data.temperature = -45.0f + 175.0f * (temp_raw / 65535.0f);

    // 转换湿度：RH = 100 × (raw / 65535)
    uint16_t humi_raw = (buf[3] << 8) | buf[4];
    data.humidity = 100.0f * (humi_raw / 65535.0f);

    data.valid = true;
    return data;
}

// 软复位（解决传感器卡死）
void sht31_reset(void) {
    uint8_t cmd[2] = {0x30, 0xA2};
    HAL_I2C_Master_Transmit(&hi2c1, SHT31_ADDR << 1, cmd, 2, 100);
    HAL_Delay(2);
}

// 开启加热器（除湿，消除结露）
void sht31_heater_enable(bool enable) {
    uint8_t cmd[2] = enable ? (uint8_t[]){0x30, 0x6D} : (uint8_t[]){0x30, 0x66};
    HAL_I2C_Master_Transmit(&hi2c1, SHT31_ADDR << 1, cmd, 2, 100);
}
```

### MH-Z19B CO₂自动基线校准（ABC）

MH-Z19B支持ABC（Automatic Baseline Correction）算法，假设传感器每24小时至少暴露一次在400ppm新鲜空气中：

```c
// 启用/禁用ABC（出厂默认开启）
void mhz19_set_abc(UART_HandleTypeDef *huart, bool enable) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x79, enable ? 0xA0 : 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00};
    // 计算校验和
    uint8_t checksum = 0;
    for (int i = 1; i < 8; i++) checksum += cmd[i];
    cmd[8] = 0xFF - checksum + 1;
    
    HAL_UART_Transmit(huart, cmd, 9, 100);
}

// 手动零点校准（需在400ppm环境中）
void mhz19_calibrate_zero(UART_HandleTypeDef *huart) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78};
    HAL_UART_Transmit(huart, cmd, 9, 100);
    // 校准需要20分钟稳定时间
}

// 手动跨度校准（需在已知浓度气体中，如2000ppm）
void mhz19_calibrate_span(UART_HandleTypeDef *huart, uint16_t span_ppm) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x88, (span_ppm >> 8) & 0xFF, span_ppm & 0xFF,
                      0x00, 0x00, 0x00, 0x00};
    uint8_t checksum = 0;
    for (int i = 1; i < 8; i++) checksum += cmd[i];
    cmd[8] = 0xFF - checksum + 1;
    
    HAL_UART_Transmit(huart, cmd, 9, 100);
}

// 读取ABC状态
bool mhz19_get_abc_status(UART_HandleTypeDef *huart) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x82};
    uint8_t resp[9] = {0};
    
    HAL_UART_Transmit(huart, cmd, 9, 100);
    HAL_UART_Receive(huart, resp, 9, 500);
    
    if (resp[0] == 0xFF && resp[1] == 0x7D) {
        return resp[4] == 0xA0;  // 0xA0=开启, 0x00=关闭
    }
    return false;
}
```

**ABC算法原理**：

```
ABC假设：
  - 传感器每天至少有一次暴露在新鲜空气（400ppm）中
  - 记录24小时内的最低读数
  - 如果最低读数 > 400ppm，逐步调整基线使其接近400ppm
  
适用场景：
  ✓ 办公室、教室（夜间无人，CO₂降至400ppm）
  ✓ 家庭（开窗通风）
  ✗ 温室（植物持续呼吸，CO₂可能低于400ppm）
  ✗ 密闭空间（长期高浓度）
  
禁用ABC的场景：
  - 需要测量低于400ppm的浓度
  - 环境CO₂从不降至400ppm
  - 需要绝对精度（ABC会引入±50ppm误差）
```

### 时间调度系统

基于RTC实现时间相关的控制规则：

```c
#include "rtc.h"

typedef struct {
    uint8_t hour_start;   // 开始小时（0~23）
    uint8_t min_start;    // 开始分钟（0~59）
    uint8_t hour_end;     // 结束小时
    uint8_t min_end;      // 结束分钟
    uint8_t weekday_mask; // 星期掩码：bit0=周一, bit6=周日, 0xFF=每天
} TimeWindow;

// 判断当前时间是否在时间窗口内
bool time_in_window(const TimeWindow *win) {
    RTC_TimeTypeDef time;
    RTC_DateTypeDef date;
    HAL_RTC_GetTime(&hrtc, &time, RTC_FORMAT_BIN);
    HAL_RTC_GetDate(&hrtc, &date, RTC_FORMAT_BIN);  // 必须读取日期才能解锁时间
    
    // 检查星期
    uint8_t weekday = date.WeekDay;  // 1=周一, 7=周日
    if (!(win->weekday_mask & (1 << (weekday - 1)))) return false;
    
    // 转换为分钟数
    uint16_t now_min = time.Hours * 60 + time.Minutes;
    uint16_t start_min = win->hour_start * 60 + win->min_start;
    uint16_t end_min = win->hour_end * 60 + win->min_end;
    
    // 处理跨午夜情况
    if (end_min < start_min) {
        return (now_min >= start_min) || (now_min < end_min);
    } else {
        return (now_min >= start_min) && (now_min < end_min);
    }
}

// 扩展规则结构，增加时间窗口
typedef struct {
    SensorType sensor;
    CompareOp  op;
    float      threshold;
    uint8_t    relay_ch;
    bool       relay_on;
    uint32_t   min_duration_ms;
    uint32_t   condition_start;
    bool       triggered;
    TimeWindow time_window;  // 新增：时间窗口限制
    bool       use_time_window;  // 是否启用时间窗口
    char       desc[32];
} ControlRule;

// 修改规则评估函数
void rules_evaluate(const EnvData *env) {
    uint32_t now = HAL_GetTick();

    for (int i = 0; i < rule_count; i++) {
        ControlRule *r = &rules[i];
        
        // 检查时间窗口
        if (r->use_time_window && !time_in_window(&r->time_window)) {
            r->condition_start = 0;
            r->triggered = false;
            continue;
        }
        
        bool cond = eval_condition(r, env);

        if (cond) {
            if (r->condition_start == 0) r->condition_start = now;

            if (!r->triggered &&
                (now - r->condition_start >= r->min_duration_ms)) {
                relay_set(r->relay_ch, r->relay_on);
                r->triggered = true;
                printf("[RULE] %s → CH%d %s\n",
                       r->desc, r->relay_ch, r->relay_on ? "ON" : "OFF");
            }
        } else {
            r->condition_start = 0;
            r->triggered = false;
        }
    }
}

// 添加带时间窗口的规则
void rule_add_with_time(SensorType sensor, CompareOp op, float threshold,
                        uint8_t relay_ch, bool relay_on,
                        uint32_t min_duration_ms,
                        uint8_t hour_start, uint8_t min_start,
                        uint8_t hour_end, uint8_t min_end,
                        uint8_t weekday_mask,
                        const char *desc) {
    if (rule_count >= MAX_RULES) return;
    ControlRule *r = &rules[rule_count++];
    r->sensor          = sensor;
    r->op              = op;
    r->threshold       = threshold;
    r->relay_ch        = relay_ch;
    r->relay_on        = relay_on;
    r->min_duration_ms = min_duration_ms;
    r->condition_start = 0;
    r->triggered       = false;
    r->use_time_window = true;
    r->time_window.hour_start = hour_start;
    r->time_window.min_start  = min_start;
    r->time_window.hour_end   = hour_end;
    r->time_window.min_end    = min_end;
    r->time_window.weekday_mask = weekday_mask;
    strncpy(r->desc, desc, 31);
}
```

**时间调度应用示例**：

```c
void setup_time_based_rules(void) {
    // 补光灯：仅在6:00~20:00且光照不足时开启
    rule_add_with_time(SENSOR_LIGHT, OP_LT, 500, 3, true, 10000,
                       6, 0,   // 6:00开始
                       20, 0,  // 20:00结束
                       0xFF,   // 每天
                       "白天光照不足补光");
    
    // 夜间强制关闭补光灯
    rule_add_with_time(SENSOR_LIGHT, OP_GE, 0, 3, false, 0,
                       20, 0,  // 20:00开始
                       6, 0,   // 6:00结束
                       0xFF,
                       "夜间关闭补光");
    
    // 工作日白天降低空调阈值（办公室有人）
    rule_add_with_time(SENSOR_TEMP, OP_GT, 26.0f, 0, true, 60000,
                       8, 0,   // 8:00开始
                       18, 0,  // 18:00结束
                       0x1F,   // 周一~周五（bit0~bit4）
                       "工作日空调");
    
    // 周末/夜间提高空调阈值（节能）
    rule_add_with_time(SENSOR_TEMP, OP_GT, 30.0f, 0, true, 60000,
                       18, 0,  // 18:00开始
                       8, 0,   // 8:00结束
                       0xFF,   // 每天
                       "非工作时段空调");
}
```

## 规则引擎

规则引擎将传感器数据与控制动作解耦，支持灵活配置：

```c
// 环境数据快照
typedef struct {
    float    temperature;
    float    humidity;
    uint16_t co2_ppm;
    uint16_t light_lux;
    uint32_t timestamp;
} EnvData;

// 控制规则
typedef enum {
    OP_GT,  // 大于
    OP_LT,  // 小于
    OP_GE,  // 大于等于
    OP_LE,  // 小于等于
} CompareOp;

typedef enum {
    SENSOR_TEMP,
    SENSOR_HUMI,
    SENSOR_CO2,
    SENSOR_LIGHT,
} SensorType;

typedef struct {
    SensorType sensor;
    CompareOp  op;
    float      threshold;
    uint8_t    relay_ch;
    bool       relay_on;
    uint32_t   min_duration_ms;  // 条件持续多久才触发
    uint32_t   condition_start;  // 条件开始时间
    bool       triggered;
    char       desc[32];         // 规则描述（调试用）
} ControlRule;

#define MAX_RULES  16
ControlRule rules[MAX_RULES];
uint8_t     rule_count = 0;

// 注册规则
void rule_add(SensorType sensor, CompareOp op, float threshold,
              uint8_t relay_ch, bool relay_on,
              uint32_t min_duration_ms, const char *desc) {
    if (rule_count >= MAX_RULES) return;
    ControlRule *r = &rules[rule_count++];
    r->sensor          = sensor;
    r->op              = op;
    r->threshold       = threshold;
    r->relay_ch        = relay_ch;
    r->relay_on        = relay_on;
    r->min_duration_ms = min_duration_ms;
    r->condition_start = 0;
    r->triggered       = false;
    strncpy(r->desc, desc, 31);
}

// 评估单条规则
static bool eval_condition(const ControlRule *r, const EnvData *env) {
    float val = 0;
    switch (r->sensor) {
        case SENSOR_TEMP:  val = env->temperature; break;
        case SENSOR_HUMI:  val = env->humidity;    break;
        case SENSOR_CO2:   val = env->co2_ppm;     break;
        case SENSOR_LIGHT: val = env->light_lux;   break;
    }
    switch (r->op) {
        case OP_GT: return val >  r->threshold;
        case OP_LT: return val <  r->threshold;
        case OP_GE: return val >= r->threshold;
        case OP_LE: return val <= r->threshold;
    }
    return false;
}

// 执行所有规则
void rules_evaluate(const EnvData *env) {
    uint32_t now = HAL_GetTick();

    for (int i = 0; i < rule_count; i++) {
        ControlRule *r = &rules[i];
        bool cond = eval_condition(r, env);

        if (cond) {
            if (r->condition_start == 0) r->condition_start = now;

            // 条件持续时间达到阈值才触发
            if (!r->triggered &&
                (now - r->condition_start >= r->min_duration_ms)) {
                relay_set(r->relay_ch, r->relay_on);
                r->triggered = true;
                printf("[RULE] %s → CH%d %s\n",
                       r->desc, r->relay_ch, r->relay_on ? "ON" : "OFF");
            }
        } else {
            r->condition_start = 0;
            r->triggered = false;
        }
    }
}
```

## 预设规则配置

```c
void setup_rules(void) {
    // 温度控制
    rule_add(SENSOR_TEMP, OP_GT, 28.0f, 0, true,  60000, "温度>28°C 开空调");
    rule_add(SENSOR_TEMP, OP_LT, 22.0f, 0, false, 60000, "温度<22°C 关空调");

    // CO₂控制（换气）
    rule_add(SENSOR_CO2, OP_GT, 1000, 1, true,  30000, "CO2>1000ppm 开风扇");
    rule_add(SENSOR_CO2, OP_LT,  600, 1, false, 60000, "CO2<600ppm 关风扇");

    // 湿度控制
    rule_add(SENSOR_HUMI, OP_LT, 40.0f, 2, true,  30000, "湿度<40% 开加湿器");
    rule_add(SENSOR_HUMI, OP_GT, 70.0f, 2, false, 30000, "湿度>70% 关加湿器");

    // 光照控制（补光）
    rule_add(SENSOR_LIGHT, OP_LT, 500, 3, true,  10000, "光照<500lux 开补光灯");
    rule_add(SENSOR_LIGHT, OP_GT, 2000, 3, false, 10000, "光照>2000lux 关补光灯");
}
```

## 深入原理

### PID温度控制算法

对于高精度温度控制（如实验室恒温箱），PID控制优于简单的开关控制：

**PID控制器原理**：

```
PID输出：
  u(t) = Kp×e(t) + Ki×∫e(t)dt + Kd×de(t)/dt
  
  其中：
    e(t) = setpoint - measured_value（误差）
    Kp：比例系数（响应速度）
    Ki：积分系数（消除稳态误差）
    Kd：微分系数（抑制超调）
```

**离散PID实现（位置式）**：

```c
typedef struct {
    float Kp, Ki, Kd;
    float setpoint;
    float integral;
    float last_error;
    float output_min, output_max;
    float integral_min, integral_max;  // 积分限幅（抗饱和）
} PID_Controller;

void pid_init(PID_Controller *pid, float kp, float ki, float kd,
              float out_min, float out_max) {
    pid->Kp = kp;
    pid->Ki = ki;
    pid->Kd = kd;
    pid->setpoint = 0;
    pid->integral = 0;
    pid->last_error = 0;
    pid->output_min = out_min;
    pid->output_max = out_max;
    pid->integral_min = out_min / ki;  // 防止积分饱和
    pid->integral_max = out_max / ki;
}

float pid_compute(PID_Controller *pid, float measured, float dt) {
    float error = pid->setpoint - measured;
    
    // 比例项
    float p_term = pid->Kp * error;
    
    // 积分项（梯形积分）
    pid->integral += (error + pid->last_error) * 0.5f * dt;
    // 积分限幅（抗积分饱和）
    if (pid->integral > pid->integral_max) pid->integral = pid->integral_max;
    if (pid->integral < pid->integral_min) pid->integral = pid->integral_min;
    float i_term = pid->Ki * pid->integral;
    
    // 微分项（一阶低通滤波，截止频率fc=10Hz）
    float derivative = (error - pid->last_error) / dt;
    static float filtered_derivative = 0;
    float alpha = dt / (dt + 1.0f / (2.0f * 3.14159f * 10.0f));  // fc=10Hz
    filtered_derivative = alpha * derivative + (1 - alpha) * filtered_derivative;
    float d_term = pid->Kd * filtered_derivative;
    
    pid->last_error = error;
    
    // 输出限幅
    float output = p_term + i_term + d_term;
    if (output > pid->output_max) output = pid->output_max;
    if (output < pid->output_min) output = pid->output_min;
    
    return output;
}
```

**PWM加热器控制**：

```c
// 使用PID输出控制PWM占空比
void temperature_control_loop(void) {
    static PID_Controller temp_pid;
    static bool initialized = false;
    
    if (!initialized) {
        // 参数整定（Ziegler-Nichols方法）
        // Kp=10, Ki=0.5, Kd=2（需根据实际系统调整）
        pid_init(&temp_pid, 10.0f, 0.5f, 2.0f, 0.0f, 100.0f);
        temp_pid.setpoint = 25.0f;  // 目标温度25°C
        initialized = true;
    }
    
    static uint32_t last_time = 0;
    uint32_t now = HAL_GetTick();
    float dt = (now - last_time) / 1000.0f;  // 秒
    
    if (dt >= 1.0f) {  // 1秒控制周期
        float temp = read_temperature();
        float pwm_duty = pid_compute(&temp_pid, temp, dt);
        
        // 设置PWM占空比（0~100%）
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, (uint16_t)pwm_duty);
        
        last_time = now;
    }
}
```

**PID参数整定方法**：

```
1. Ziegler-Nichols临界振荡法：
   a) 设置Ki=0, Kd=0，逐步增大Kp直到系统持续振荡
   b) 记录临界增益Ku和振荡周期Tu
   c) 计算：
      Kp = 0.6 × Ku
      Ki = 2 × Kp / Tu
      Kd = Kp × Tu / 8

2. 经验调试法：
   a) 先调Kp：增大Kp加快响应，但过大会振荡
   b) 再调Ki：消除稳态误差，但过大会超调
   c) 最后调Kd：抑制超调，但过大会放大噪声

3. 典型参数范围（温度控制）：
   Kp: 5~20
   Ki: 0.1~1.0
   Kd: 1~5
```

### 能效优化策略

**负载预测与提前控制**：

```c
// 基于历史数据的负载预测
#define HISTORY_SIZE  24  // 24小时历史

typedef struct {
    float    temp_history[HISTORY_SIZE];
    uint8_t  hour_index[HISTORY_SIZE];
    uint8_t  count;
} TempHistory;

TempHistory history = {0};

void history_add(float temp, uint8_t hour) {
    if (history.count < HISTORY_SIZE) {
        history.temp_history[history.count] = temp;
        history.hour_index[history.count] = hour;
        history.count++;
    } else {
        // 循环覆盖最旧数据
        memmove(&history.temp_history[0], &history.temp_history[1],
                (HISTORY_SIZE - 1) * sizeof(float));
        memmove(&history.hour_index[0], &history.hour_index[1],
                (HISTORY_SIZE - 1) * sizeof(uint8_t));
        history.temp_history[HISTORY_SIZE - 1] = temp;
        history.hour_index[HISTORY_SIZE - 1] = hour;
    }
}

// 预测下一小时温度
float predict_next_hour_temp(uint8_t current_hour) {
    uint8_t next_hour = (current_hour + 1) % 24;
    float sum = 0;
    int count = 0;
    
    // 查找历史上同一时刻的温度
    for (int i = 0; i < history.count; i++) {
        if (history.hour_index[i] == next_hour) {
            sum += history.temp_history[i];
            count++;
        }
    }
    
    if (count > 0) return sum / count;
    return 25.0f;  // 默认值
}

// 提前预冷/预热
void predictive_control(void) {
    RTC_TimeTypeDef time;
    HAL_RTC_GetTime(&hrtc, &time, RTC_FORMAT_BIN);
    
    float predicted = predict_next_hour_temp(time.Hours);
    float current = read_temperature();
    
    // 如果预测1小时后会过热，提前开启空调
    if (predicted > 28.0f && current > 26.0f) {
        relay_set(AC_CH, true);
        printf("[PREDICT] 预测过热，提前开启空调\n");
    }
}
```

**多设备协同优化**：

```c
// 优先级调度：避免多个大功率设备同时启动
typedef enum {
    PRIORITY_HIGH   = 0,  // 空调、加热器（舒适性）
    PRIORITY_MEDIUM = 1,  // 风扇、加湿器
    PRIORITY_LOW    = 2,  // 补光灯、灌溉泵
} DevicePriority;

typedef struct {
    uint8_t         relay_ch;
    DevicePriority  priority;
    uint16_t        power_watts;  // 功率（W）
    bool            is_on;
} Device;

Device devices[] = {
    {0, PRIORITY_HIGH,   1500, false},  // 空调1500W
    {1, PRIORITY_MEDIUM,  50,  false},  // 风扇50W
    {2, PRIORITY_MEDIUM,  30,  false},  // 加湿器30W
    {3, PRIORITY_LOW,    100,  false},  // 补光灯100W
};

#define MAX_TOTAL_POWER  2000  // 最大总功率2000W

bool device_turn_on(uint8_t ch) {
    // 计算当前总功率
    uint16_t current_power = 0;
    for (int i = 0; i < sizeof(devices)/sizeof(Device); i++) {
        if (devices[i].is_on) current_power += devices[i].power_watts;
    }
    
    // 查找目标设备
    Device *target = NULL;
    for (int i = 0; i < sizeof(devices)/sizeof(Device); i++) {
        if (devices[i].relay_ch == ch) {
            target = &devices[i];
            break;
        }
    }
    if (!target) return false;
    
    // 检查是否超过功率限制
    if (current_power + target->power_watts > MAX_TOTAL_POWER) {
        // 尝试关闭低优先级设备
        for (int i = 0; i < sizeof(devices)/sizeof(Device); i++) {
            if (devices[i].is_on &&
                devices[i].priority > target->priority) {
                relay_set(devices[i].relay_ch, false);
                devices[i].is_on = false;
                current_power -= devices[i].power_watts;
                printf("[POWER] 关闭低优先级设备CH%d以腾出功率\n",
                       devices[i].relay_ch);
                
                if (current_power + target->power_watts <= MAX_TOTAL_POWER)
                    break;
            }
        }
    }
    
    // 再次检查
    if (current_power + target->power_watts <= MAX_TOTAL_POWER) {
        relay_set(ch, true);
        target->is_on = true;
        return true;
    }
    
    printf("[POWER] 功率不足，无法开启CH%d\n", ch);
    return false;
}
```

### 故障检测与自恢复

**传感器故障检测**：

```c
typedef struct {
    float    last_valid_value;
    uint32_t last_valid_time;
    uint8_t  consecutive_errors;
    bool     is_faulty;
} SensorHealth;

SensorHealth sensor_health[4] = {0};  // TEMP, HUMI, CO2, LIGHT

#define MAX_CONSECUTIVE_ERRORS  5
#define SENSOR_TIMEOUT_MS       (5 * 60 * 1000)  // 5分钟无有效数据

void sensor_health_check(SensorType type, float value, bool valid) {
    SensorHealth *health = &sensor_health[type];
    uint32_t now = HAL_GetTick();
    
    if (valid) {
        // 合理性检查
        bool reasonable = true;
        switch (type) {
            case SENSOR_TEMP:
                reasonable = (value >= -40.0f && value <= 80.0f);
                break;
            case SENSOR_HUMI:
                reasonable = (value >= 0.0f && value <= 100.0f);
                break;
            case SENSOR_CO2:
                reasonable = (value >= 300 && value <= 5000);
                break;
            case SENSOR_LIGHT:
                reasonable = (value >= 0 && value <= 100000);
                break;
        }
        
        if (reasonable) {
            health->last_valid_value = value;
            health->last_valid_time = now;
            health->consecutive_errors = 0;
            health->is_faulty = false;
        } else {
            health->consecutive_errors++;
        }
    } else {
        health->consecutive_errors++;
    }
    
    // 判断故障
    if (health->consecutive_errors >= MAX_CONSECUTIVE_ERRORS ||
        (now - health->last_valid_time > SENSOR_TIMEOUT_MS)) {
        if (!health->is_faulty) {
            health->is_faulty = true;
            printf("[FAULT] 传感器%d故障\n", type);
            // 发送告警
            esp8266_mqtt_publish("env/alert", "{\"type\":\"sensor_fault\"}");
        }
    }
}

// 使用最后有效值或安全默认值
float get_safe_sensor_value(SensorType type, float current, bool valid) {
    sensor_health_check(type, current, valid);
    
    if (sensor_health[type].is_faulty) {
        // 使用最后有效值或安全默认值
        if (sensor_health[type].last_valid_time > 0) {
            return sensor_health[type].last_valid_value;
        } else {
            // 安全默认值
            switch (type) {
                case SENSOR_TEMP:  return 25.0f;
                case SENSOR_HUMI:  return 50.0f;
                case SENSOR_CO2:   return 800;
                case SENSOR_LIGHT: return 500;
            }
        }
    }
    
    return current;
}
```

## 主循环与数据上报

```c
void app_main(void) {
    setup_rules();

    while (1) {
        // 采集传感器数据
        EnvData env;
        DHT22_Data dht = dht22_read(GPIOA, GPIO_PIN_0);
        env.temperature = dht.valid ? dht.temperature : 0;
        env.humidity    = dht.valid ? dht.humidity    : 0;
        env.co2_ppm     = mhz19_read_co2(&huart2);
        env.light_lux   = bh1750_read_lux();
        env.timestamp   = HAL_GetTick();

        // 执行规则
        rules_evaluate(&env);

        // OLED显示
        oled_printf(0, 0, "T:%.1fC H:%.1f%%", env.temperature, env.humidity);
        oled_printf(0, 1, "CO2:%dppm", env.co2_ppm);
        oled_printf(0, 2, "Light:%dlux", env.light_lux);
        oled_printf(0, 3, "Relay:%04X",
                    (relay_get(3)<<3)|(relay_get(2)<<2)|
                    (relay_get(1)<<1)| relay_get(0));

        // 通过ESP8266上报MQTT（每30秒）
        static uint32_t last_report = 0;
        if (HAL_GetTick() - last_report > 30000) {
            last_report = HAL_GetTick();
            char json[256];
            snprintf(json, sizeof(json),
                     "{\"temp\":%.1f,\"humi\":%.1f,\"co2\":%d,\"light\":%d}",
                     env.temperature, env.humidity,
                     env.co2_ppm, env.light_lux);
            esp8266_mqtt_publish("env/monitor/node001", json);
        }

        HAL_Delay(5000);  // 5秒采集一次
    }
}
```

## 完整项目实战：智能温室控制系统

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      云端服务器                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MQTT Broker  │  │  InfluxDB    │  │   Grafana    │      │
│  │  (EMQX)      │  │  (时序数据库) │  │  (可视化)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │ MQTT/TLS         │ HTTP             │ HTTP
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────┐
│         ▼                  ▼                  ▼              │
│  ┌──────────────────────────────────────────────────┐       │
│  │           ESP8266 WiFi模块                        │       │
│  │  - MQTT客户端                                     │       │
│  │  - OTA固件更新                                    │       │
│  │  - Web配置界面                                    │       │
│  └──────────────────┬───────────────────────────────┘       │
│                     │ UART                                   │
│  ┌──────────────────▼───────────────────────────────┐       │
│  │           STM32F103C8T6主控                       │       │
│  │  - 传感器数据采集                                 │       │
│  │  - 规则引擎                                       │       │
│  │  - 继电器控制                                     │       │
│  │  - 本地数据记录（SD卡）                           │       │
│  └─┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──┘       │
│    │    │    │    │    │    │    │    │    │    │          │
│  ┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐      │
│  │DHT││SHT││MH-││BH-││土壤││继电││继电││继电││继电││OLED│    │
│  │22 ││31 ││Z19││1750││湿度││器0││器1││器2││器3││显示│    │
│  └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘      │
│   温湿  温湿  CO₂  光照  土壤  空调  风扇  加湿  补光  状态  │
└─────────────────────────────────────────────────────────────┘
```

### 硬件BOM清单

| 类别 | 器件 | 型号/规格 | 数量 | 单价 | 来源 |
|------|------|----------|------|------|------|
| 主控 | MCU | STM32F103C8T6最小系统板 | 1 | ¥12 | 淘宝 |
| 通信 | WiFi模块 | ESP8266-01S | 1 | ¥8 | 淘宝 |
| 传感器 | 温湿度 | DHT22/AM2302 | 1 | ¥15 | 淘宝 |
| 传感器 | 温湿度（高精度） | SHT31-D | 1 | ¥25 | 立创商城 |
| 传感器 | CO₂ | MH-Z19B | 1 | ¥65 | 淘宝 |
| 传感器 | 光照 | BH1750 模块 | 1 | ¥3 | 淘宝 |
| 传感器 | 土壤湿度 | 电阻式土壤湿度传感器 | 2 | ¥2 | 淘宝 |
| 执行器 | 继电器 | 4路5V继电器模块 | 1 | ¥12 | 淘宝 |
| 显示 | OLED | 0.96" I2C OLED (SSD1306) | 1 | ¥8 | 淘宝 |
| 存储 | SD卡模块 | MicroSD卡模块 | 1 | ¥3 | 淘宝 |
| 电源 | 开关电源 | 5V/3A | 1 | ¥10 | 淘宝 |
| 其他 | 杜邦线 | 公对母/母对母 | 若干 | ¥5 | 淘宝 |
| 其他 | 面包板 | 830孔 | 1 | ¥5 | 淘宝 |
| **总计** | | | | **¥173** | |

### 接线图

```
STM32F103C8T6引脚分配：

传感器接口：
  PA0  ← DHT22 DATA（需10kΩ上拉）
  PB6  → I2C1_SCL（SHT31, BH1750, OLED）
  PB7  ← I2C1_SDA
  PA9  → USART1_TX（ESP8266）
  PA10 ← USART1_RX
  PA2  → USART2_TX（MH-Z19B）
  PA3  ← USART2_RX
  PA4  ← ADC1_IN4（土壤湿度1）
  PA5  ← ADC1_IN5（土壤湿度2）

继电器控制：
  PB12 → Relay CH0（空调）
  PB13 → Relay CH1（风扇）
  PB14 → Relay CH2（加湿器）
  PB15 → Relay CH3（补光灯）

SD卡（SPI1）：
  PA5  → SPI1_SCK
  PA6  ← SPI1_MISO
  PA7  → SPI1_MOSI
  PA4  → SPI1_CS

按键/LED：
  PC13 ← 板载LED
  PB0  ← 按键1（模式切换）
  PB1  ← 按键2（手动控制）

电源：
  5V   → STM32 5V输入
  3.3V → 传感器供电（STM32板载LDO输出）
  GND  → 公共地
```

### 完整主程序

```c
#include "main.h"
#include "fatfs.h"  // SD卡文件系统

// 全局变量
EnvData current_env;
bool    auto_mode = true;  // 自动/手动模式

// 数据记录到SD卡
void log_to_sd(const EnvData *env) {
    FIL file;
    FRESULT res;
    char line[128];
    
    res = f_open(&file, "env_log.csv", FA_OPEN_APPEND | FA_WRITE);
    if (res != FR_OK) {
        // 文件不存在，创建并写入表头
        res = f_open(&file, "env_log.csv", FA_CREATE_ALWAYS | FA_WRITE);
        if (res == FR_OK) {
            f_puts("timestamp,temp,humi,co2,light\n", &file);
        }
    }
    
    if (res == FR_OK) {
        snprintf(line, sizeof(line), "%lu,%.1f,%.1f,%d,%d\n",
                 env->timestamp, env->temperature, env->humidity,
                 env->co2_ppm, env->light_lux);
        f_puts(line, &file);
        f_close(&file);
    }
}

// 云端数据上报
void report_to_cloud(const EnvData *env) {
    char json[512];
    
    // 获取继电器状态
    uint8_t relay_status = 0;
    for (int i = 0; i < 4; i++) {
        if (relay_get(i)) relay_status |= (1 << i);
    }
    
    // 构造JSON
    snprintf(json, sizeof(json),
             "{"
             "\"device_id\":\"greenhouse_001\","
             "\"timestamp\":%lu,"
             "\"temperature\":%.2f,"
             "\"humidity\":%.2f,"
             "\"co2\":%d,"
             "\"light\":%d,"
             "\"relay_status\":%d,"
             "\"auto_mode\":%s"
             "}",
             env->timestamp,
             env->temperature,
             env->humidity,
             env->co2_ppm,
             env->light_lux,
             relay_status,
             auto_mode ? "true" : "false");
    
    esp8266_mqtt_publish("greenhouse/data", json);
}

// 移动端告警推送
void send_alert(const char *message) {
    char json[256];
    snprintf(json, sizeof(json),
             "{\"device\":\"greenhouse_001\",\"alert\":\"%s\",\"time\":%lu}",
             message, HAL_GetTick());
    esp8266_mqtt_publish("greenhouse/alert", json);
}

// 阈值告警检查
void check_alerts(const EnvData *env) {
    static bool temp_high_alerted = false;
    static bool temp_low_alerted = false;
    static bool co2_high_alerted = false;
    
    // 温度过高告警
    if (env->temperature > 35.0f) {
        if (!temp_high_alerted) {
            send_alert("温度过高！当前温度超过35°C");
            temp_high_alerted = true;
        }
    } else if (env->temperature < 33.0f) {
        temp_high_alerted = false;  // 恢复
    }
    
    // 温度过低告警
    if (env->temperature < 10.0f) {
        if (!temp_low_alerted) {
            send_alert("温度过低！当前温度低于10°C");
            temp_low_alerted = true;
        }
    } else if (env->temperature > 12.0f) {
        temp_low_alerted = false;
    }
    
    // CO₂过高告警
    if (env->co2_ppm > 2000) {
        if (!co2_high_alerted) {
            send_alert("CO₂浓度过高！当前浓度超过2000ppm");
            co2_high_alerted = true;
        }
    } else if (env->co2_ppm < 1800) {
        co2_high_alerted = false;
    }
}

// 按键处理
void handle_buttons(void) {
    static uint32_t last_btn1_time = 0;
    static uint32_t last_btn2_time = 0;
    uint32_t now = HAL_GetTick();
    
    // 按键1：切换自动/手动模式
    if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0) == GPIO_PIN_RESET) {
        if (now - last_btn1_time > 200) {  // 防抖200ms
            auto_mode = !auto_mode;
            printf("[MODE] %s模式\n", auto_mode ? "自动" : "手动");
            last_btn1_time = now;
        }
    }
    
    // 按键2：手动模式下循环切换继电器
    if (!auto_mode &&
        HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_1) == GPIO_PIN_RESET) {
        if (now - last_btn2_time > 200) {
            static uint8_t manual_ch = 0;
            relay_toggle(manual_ch);
            printf("[MANUAL] CH%d %s\n", manual_ch,
                   relay_get(manual_ch) ? "ON" : "OFF");
            manual_ch = (manual_ch + 1) % 4;
            last_btn2_time = now;
        }
    }
}

// MQTT命令处理回调
void mqtt_command_callback(const char *topic, const char *payload) {
    // 解析JSON命令
    // 示例：{"cmd":"set_relay","ch":0,"state":true}
    //      {"cmd":"set_mode","auto":true}
    //      {"cmd":"set_threshold","sensor":"temp","value":28.0}
    
    if (strstr(payload, "\"cmd\":\"set_relay\"")) {
        // 手动控制继电器
        int ch, state;
        if (sscanf(payload, "{\"cmd\":\"set_relay\",\"ch\":%d,\"state\":%d}",
                   &ch, &state) == 2) {
            if (ch >= 0 && ch < 4) {
                relay_set(ch, state);
                printf("[MQTT] 远程控制CH%d %s\n", ch, state ? "ON" : "OFF");
            }
        }
    } else if (strstr(payload, "\"cmd\":\"set_mode\"")) {
        // 切换模式
        int mode;
        if (sscanf(payload, "{\"cmd\":\"set_mode\",\"auto\":%d}", &mode) == 1) {
            auto_mode = mode;
            printf("[MQTT] 切换到%s模式\n", auto_mode ? "自动" : "手动");
        }
    }
}

// 主函数
int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 初始化外设
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_USART1_UART_Init();  // ESP8266
    MX_USART2_UART_Init();  // MH-Z19B
    MX_ADC1_Init();
    MX_SPI1_Init();
    MX_RTC_Init();
    MX_FATFS_Init();
    
    // 初始化传感器
    sht31_reset();
    mhz19_set_abc(&huart2, true);  // 启用ABC
    
    // 初始化ESP8266
    esp8266_init(&huart1);
    esp8266_mqtt_connect("mqtt.example.com", 1883, "greenhouse_001");
    esp8266_mqtt_subscribe("greenhouse/cmd", mqtt_command_callback);
    
    // 初始化OLED
    oled_init();
    oled_clear();
    oled_printf(0, 0, "Greenhouse v1.0");
    HAL_Delay(2000);
    
    // 设置规则
    setup_rules();
    setup_time_based_rules();
    
    printf("[SYSTEM] 温室控制系统启动\n");
    
    uint32_t last_sample = 0;
    uint32_t last_report = 0;
    uint32_t last_log = 0;
    
    while (1) {
        uint32_t now = HAL_GetTick();
        
        // 5秒采样一次
        if (now - last_sample >= 5000) {
            last_sample = now;
            
            // 采集传感器
            SHT31_Data sht = sht31_read();
            current_env.temperature = get_safe_sensor_value(
                SENSOR_TEMP, sht.temperature, sht.valid);
            current_env.humidity = get_safe_sensor_value(
                SENSOR_HUMI, sht.humidity, sht.valid);
            current_env.co2_ppm = get_safe_sensor_value(
                SENSOR_CO2, mhz19_read_co2(&huart2), true);
            current_env.light_lux = get_safe_sensor_value(
                SENSOR_LIGHT, bh1750_read_lux(), true);
            current_env.timestamp = now;
            
            // 自动模式下执行规则
            if (auto_mode) {
                rules_evaluate(&current_env);
            }
            
            // 告警检查
            check_alerts(&current_env);
            
            // 更新OLED显示
            oled_clear();
            oled_printf(0, 0, "T:%.1fC H:%.1f%%",
                       current_env.temperature, current_env.humidity);
            oled_printf(0, 1, "CO2:%dppm", current_env.co2_ppm);
            oled_printf(0, 2, "Lux:%d", current_env.light_lux);
            oled_printf(0, 3, "%s R:%d%d%d%d",
                       auto_mode ? "AUTO" : "MANU",
                       relay_get(0), relay_get(1),
                       relay_get(2), relay_get(3));
        }
        
        // 30秒上报一次云端
        if (now - last_report >= 30000) {
            last_report = now;
            report_to_cloud(&current_env);
        }
        
        // 10分钟记录一次SD卡
        if (now - last_log >= 600000) {
            last_log = now;
            log_to_sd(&current_env);
        }
        
        // 处理按键
        handle_buttons();
        
        // 处理MQTT消息
        esp8266_mqtt_loop();
        
        HAL_Delay(100);
    }
}
```

### Grafana仪表盘配置

在Grafana中创建温室监控仪表盘：

**Panel 1: 温度趋势**
```flux
from(bucket: "greenhouse")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "environment")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

**Panel 2: 湿度趋势**
```flux
from(bucket: "greenhouse")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

**Panel 3: CO₂浓度**
```flux
from(bucket: "greenhouse")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_field"] == "co2")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

**Panel 4: 继电器状态（State Timeline）**
```flux
from(bucket: "greenhouse")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_field"] == "relay_status")
  |> map(fn: (r) => ({
      r with
      relay0: if (r._value & 1) == 1 then "ON" else "OFF",
      relay1: if (r._value & 2) == 2 then "ON" else "OFF",
      relay2: if (r._value & 4) == 4 then "ON" else "OFF",
      relay3: if (r._value & 8) == 8 then "ON" else "OFF"
    }))
```

### 移动端控制界面（Node-RED）

使用Node-RED快速搭建移动端控制界面：

```json
[
  {
    "id": "mqtt_in",
    "type": "mqtt in",
    "topic": "greenhouse/data",
    "broker": "mqtt_broker"
  },
  {
    "id": "dashboard_temp",
    "type": "ui_gauge",
    "min": 0,
    "max": 50,
    "label": "温度(°C)"
  },
  {
    "id": "dashboard_switch",
    "type": "ui_switch",
    "label": "空调",
    "topic": "greenhouse/cmd",
    "payload": "{\"cmd\":\"set_relay\",\"ch\":0,\"state\":true}"
  }
]
```

## 延伸阅读

- [继电器控制基础](../beginner/04-relay-control.html) - 继电器工作原理
- [WiFi智能插座](07-smart-socket-project.html) - 单路WiFi控制
- [多路继电器自动化](08-automation-system.html) - 工业级多路控制
- [MQTT协议详解](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html) - MQTT深入学习

## 常见问题与调试

### 传感器相关问题

**问题1：DHT22读取失败或数据不稳定**

症状：
- 返回全0或全1
- 偶尔读取成功，大部分时间失败
- 温湿度值跳变剧烈

原因与解决：
```c
// 1. 时序问题（最常见）
// DHT22对时序要求严格，中断会破坏时序
void dht22_read_with_interrupt_disable(void) {
    __disable_irq();  // 关闭所有中断
    DHT22_Data data = dht22_read(GPIOA, GPIO_PIN_0);
    __enable_irq();   // 恢复中断
}

// 2. 上拉电阻问题
// DHT22需要4.7kΩ~10kΩ上拉电阻
// 检查：用万用表测量DATA引脚空闲时电压应为3.3V

// 3. 供电不足
// DHT22工作电流：0.5~2.5mA，瞬时可达2.5mA
// 解决：使用独立3.3V稳压，加100μF电容

// 4. 线缆过长
// 建议：DATA线长度<20cm，超过需加缓冲器

// 5. 采样频率过高
// DHT22最快0.5Hz（2秒一次），过快会返回上次数据
#define DHT22_MIN_INTERVAL_MS  2000
static uint32_t last_read_time = 0;

DHT22_Data dht22_read_safe(void) {
    uint32_t now = HAL_GetTick();
    if (now - last_read_time < DHT22_MIN_INTERVAL_MS) {
        return last_valid_data;  // 返回缓存
    }
    last_read_time = now;
    return dht22_read(GPIOA, GPIO_PIN_0);
}
```

**问题2：MH-Z19B CO₂读数异常**

症状：
- 读数始终为400ppm或5000ppm
- 读数缓慢上升不下降
- 预热后读数仍不准确

原因与解决：
```c
// 1. 预热不足
// MH-Z19B需要3分钟预热，建议等待5分钟
void mhz19_wait_ready(void) {
    printf("MH-Z19B预热中...\n");
    for (int i = 0; i < 300; i++) {  // 5分钟
        HAL_Delay(1000);
        if (i % 60 == 0) printf("%d分钟...\n", i/60);
    }
    printf("预热完成\n");
}

// 2. ABC算法误校准
// 如果环境CO₂从不降至400ppm，ABC会导致读数偏低
// 解决：禁用ABC或手动校准
mhz19_set_abc(&huart2, false);

// 3. 串口通信问题
// 检查波特率（9600）、校验和
void mhz19_test_communication(void) {
    uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
    uint8_t resp[9] = {0};
    
    HAL_UART_Transmit(&huart2, cmd, 9, 100);
    HAL_StatusTypeDef status = HAL_UART_Receive(&huart2, resp, 9, 500);
    
    if (status != HAL_OK) {
        printf("UART接收失败：%d\n", status);
    } else {
        printf("响应：");
        for (int i = 0; i < 9; i++) printf("%02X ", resp[i]);
        printf("\n");
    }
}

// 4. 零点漂移
// 长期使用后需要重新校准
// 在400ppm新鲜空气中放置20分钟后执行：
mhz19_calibrate_zero(&huart2);
```

**问题3：SHT31 I2C通信失败**

症状：
- HAL_I2C_Master_Transmit返回HAL_ERROR或HAL_TIMEOUT
- 读取数据全为0xFF

原因与解决：
```c
// 1. I2C地址错误
// SHT31有两个地址：0x44（ADDR→GND）或0x45（ADDR→VDD）
// 扫描I2C总线查找设备
void i2c_scan(void) {
    printf("扫描I2C总线...\n");
    for (uint8_t addr = 1; addr < 128; addr++) {
        if (HAL_I2C_IsDeviceReady(&hi2c1, addr << 1, 1, 10) == HAL_OK) {
            printf("发现设备：0x%02X\n", addr);
        }
    }
}

// 2. 上拉电阻
// I2C需要4.7kΩ上拉电阻（SCL和SDA各一个）
// 检查：用万用表测量SCL/SDA空闲时应为3.3V

// 3. 总线冲突
// 多个I2C设备共享总线，某个设备卡死会拉低总线
// 解决：逐个断开设备，找出故障设备
// 或软件复位I2C总线：
void i2c_reset(void) {
    HAL_I2C_DeInit(&hi2c1);
    HAL_Delay(10);
    HAL_I2C_Init(&hi2c1);
}

// 4. 时钟速度过快
// SHT31支持最高1MHz，但长线缆或多设备时降低速度
// 在CubeMX中设置I2C时钟为100kHz（标准模式）

// 5. SHT31卡死
// 长时间运行后可能卡死，需要软复位
if (sht31_read().valid == false) {
    sht31_reset();
    HAL_Delay(10);
}
```

### 控制系统问题

**问题4：继电器频繁开关**

症状：
- 继电器每隔几秒就开关一次
- 听到继电器"咔嗒咔嗒"声音

原因与解决：
```c
// 1. 死区设置不当
// 温度在阈值附近波动导致频繁触发
// 解决：增大死区
rule_add(SENSOR_TEMP, OP_GT, 28.0f, 0, true,  60000, "温度>28°C 开空调");
rule_add(SENSOR_TEMP, OP_LT, 24.0f, 0, false, 60000, "温度<24°C 关空调");
// 死区：24~28°C（4°C死区）

// 2. 最小动作间隔不足
// 增加min_duration_ms参数
rule_add(SENSOR_TEMP, OP_GT, 28.0f, 0, true,
         5 * 60 * 1000,  // 5分钟持续时间
         "温度>28°C 开空调");

// 3. 传感器噪声
// 对传感器数据进行滤波
#define FILTER_SIZE  5
float temp_filter[FILTER_SIZE] = {0};
uint8_t filter_index = 0;

float get_filtered_temp(float new_temp) {
    temp_filter[filter_index] = new_temp;
    filter_index = (filter_index + 1) % FILTER_SIZE;
    
    float sum = 0;
    for (int i = 0; i < FILTER_SIZE; i++) sum += temp_filter[i];
    return sum / FILTER_SIZE;
}
```

**问题5：规则冲突**

症状：
- 加湿器和排风扇同时开启（矛盾）
- 加热器和空调同时开启

原因与解决：
```c
// 添加互斥规则检查
typedef struct {
    uint8_t ch1, ch2;  // 互斥的继电器通道
} MutexPair;

MutexPair mutex_pairs[] = {
    {0, 1},  // 空调(CH0) 与 加热器(CH1) 互斥
    {2, 3},  // 加湿器(CH2) 与 排风扇(CH3) 互斥
};

void relay_set_with_mutex(uint8_t ch, bool on) {
    if (on) {
        // 检查互斥
        for (int i = 0; i < sizeof(mutex_pairs)/sizeof(MutexPair); i++) {
            if (mutex_pairs[i].ch1 == ch && relay_get(mutex_pairs[i].ch2)) {
                relay_set(mutex_pairs[i].ch2, false);  // 关闭互斥设备
                printf("[MUTEX] 关闭CH%d以开启CH%d\n", mutex_pairs[i].ch2, ch);
            }
            if (mutex_pairs[i].ch2 == ch && relay_get(mutex_pairs[i].ch1)) {
                relay_set(mutex_pairs[i].ch1, false);
                printf("[MUTEX] 关闭CH%d以开启CH%d\n", mutex_pairs[i].ch1, ch);
            }
        }
    }
    relay_set(ch, on);
}
```

### 通信问题

**问题6：MQTT连接频繁断开**

症状：
- ESP8266每隔几分钟断开重连
- 数据上报丢失

原因与解决：
```c
// 1. Keep-Alive超时
// MQTT默认60秒心跳，网络不稳定时容易超时
// 解决：缩短心跳间隔，增加超时时间
esp8266_mqtt_connect_ex("mqtt.example.com", 1883,
                        "greenhouse_001",
                        30,   // 30秒心跳
                        120); // 120秒超时

// 2. WiFi信号弱
// 检查信号强度
int8_t rssi = esp8266_get_rssi();
if (rssi < -70) {
    printf("[WARN] WiFi信号弱：%ddBm\n", rssi);
}

// 3. QoS设置
// 使用QoS 1确保消息送达
esp8266_mqtt_publish_qos("greenhouse/data", json, 1);

// 4. 自动重连
void mqtt_keepalive_task(void) {
    static uint32_t last_check = 0;
    uint32_t now = HAL_GetTick();
    
    if (now - last_check > 10000) {  // 每10秒检查一次
        last_check = now;
        if (!esp8266_mqtt_is_connected()) {
            printf("[MQTT] 连接断开，重连中...\n");
            esp8266_mqtt_connect("mqtt.example.com", 1883, "greenhouse_001");
        }
    }
}
```

**问题7：SD卡写入失败**

症状：
- f_open返回FR_DISK_ERR
- 数据记录不完整

原因与解决：
```c
// 1. SD卡格式化
// 使用FAT32格式，簇大小4KB
// Windows: format X: /FS:FAT32 /A:4096

// 2. SPI速度过快
// 降低SPI时钟频率（初始化时使用低速）
void sd_init_slow(void) {
    // 初始化时使用低速（<400kHz）
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_128;
    HAL_SPI_Init(&hspi1);
    
    // 初始化成功后切换到高速
    if (f_mount(&SDFatFS, "", 1) == FR_OK) {
        hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;
        HAL_SPI_Init(&hspi1);
    }
}

// 3. 文件未关闭
// 确保每次写入后关闭文件
void log_to_sd_safe(const EnvData *env) {
    FIL file;
    if (f_open(&file, "env_log.csv", FA_OPEN_APPEND | FA_WRITE) == FR_OK) {
        char line[128];
        snprintf(line, sizeof(line), "%lu,%.1f,%.1f,%d,%d\n",
                 env->timestamp, env->temperature, env->humidity,
                 env->co2_ppm, env->light_lux);
        f_puts(line, &file);
        f_sync(&file);   // 强制写入
        f_close(&file);  // 必须关闭
    }
}

// 4. SD卡写保护
// 检查SD卡物理写保护开关

// 5. SD卡寿命
// SD卡有写入次数限制（约10万次）
// 解决：减少写入频率，使用磨损均衡
```

### 系统稳定性问题

**问题8：系统运行一段时间后死机**

症状：
- 运行几小时或几天后无响应
- 看门狗复位

原因与解决：
```c
// 1. 内存泄漏
// 检查动态内存分配是否正确释放
// 避免在循环中使用malloc/free

// 2. 栈溢出
// 增大栈大小（在启动文件中修改）
// 或减少局部变量使用

// 3. 看门狗超时
// 在主循环中喂狗
void main_loop(void) {
    while (1) {
        // ... 业务逻辑 ...
        
        HAL_IWDG_Refresh(&hiwdg);  // 喂狗
        HAL_Delay(100);
    }
}

// 4. 中断嵌套过深
// 降低中断优先级，避免高频中断

// 5. 硬件故障
// 检查电源纹波、温度、湿度
// 添加硬件看门狗（外部看门狗芯片）
```

### 调试技巧

**串口日志分级**：

```c
typedef enum {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR,
} LogLevel;

LogLevel current_log_level = LOG_INFO;

void log_printf(LogLevel level, const char *fmt, ...) {
    if (level < current_log_level) return;
    
    const char *level_str[] = {"[DEBUG]", "[INFO]", "[WARN]", "[ERROR]"};
    printf("%s ", level_str[level]);
    
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}

// 使用
log_printf(LOG_DEBUG, "传感器读取：T=%.1f\n", temp);
log_printf(LOG_ERROR, "MQTT连接失败\n");
```

**性能监控**：

```c
// CPU使用率监控
uint32_t idle_count = 0;
uint32_t total_count = 0;

void idle_task(void) {
    idle_count++;
}

void calculate_cpu_usage(void) {
    static uint32_t last_idle = 0;
    static uint32_t last_total = 0;
    
    uint32_t idle_delta = idle_count - last_idle;
    uint32_t total_delta = total_count - last_total;
    
    float cpu_usage = 100.0f * (1.0f - (float)idle_delta / total_delta);
    printf("[CPU] 使用率：%.1f%%\n", cpu_usage);
    
    last_idle = idle_count;
    last_total = total_count;
}
```

## 参考资料

### 传感器数据手册

1. **DHT22/AM2302 Datasheet** - AOSONG Electronics
   - 温湿度测量原理
   - 单总线通信协议
   - 时序要求与电气特性

2. **SHT31-D Datasheet** - Sensirion AG
   - 高精度温湿度传感器
   - I2C通信协议
   - CRC-8校验算法

3. **MH-Z19B CO₂ Sensor Manual** - Winsen Electronics
   - NDIR（非色散红外）测量原理
   - UART通信协议
   - ABC自动基线校准算法

4. **BH1750 Ambient Light Sensor Datasheet** - ROHM Semiconductor
   - 光照强度测量原理
   - I2C通信协议
   - 测量模式与分辨率

5. **SSD1306 OLED Display Datasheet** - Solomon Systech
   - OLED显示原理
   - I2C/SPI接口
   - 图形显示命令

### 通信协议

6. **ESP8266 AT Instruction Set** - Espressif Systems
   - AT命令集
   - WiFi配置
   - TCP/UDP通信

7. **MQTT Version 3.1.1** - OASIS Standard
   - MQTT协议规范
   - QoS机制
   - 遗嘱消息

8. **MQTT Version 5.0** - OASIS Standard
   - 新增特性
   - 用户属性
   - 共享订阅

### 控制理论

9. **《自动控制原理》** - 胡寿松，科学出版社
   - PID控制器设计
   - 系统稳定性分析
   - 频域与时域分析

10. **《现代控制理论》** - 刘豹，机械工业出版社
    - 状态空间方法
    - 最优控制
    - 自适应控制

11. **PID Control System Design and Automatic Tuning** - Weng Khuen Ho
    - PID参数整定方法
    - Ziegler-Nichols法
    - 抗积分饱和技术

### 建筑自动化

12. **《智能建筑自动化系统》** - 张少军，中国建筑工业出版社
    - 楼宇自动化系统
    - HVAC控制策略
    - 能源管理系统

13. **ASHRAE Standard 55-2020** - Thermal Environmental Conditions for Human Occupancy
    - 热舒适标准
    - 温湿度要求
    - 空气质量标准

14. **ASHRAE Handbook - HVAC Systems and Equipment**
    - HVAC系统设计
    - 设备选型
    - 控制策略

15. **GB 50736-2012** - 《民用建筑供暖通风与空气调节设计规范》
    - 中国国家标准
    - 室内环境参数
    - 系统设计要求

### 农业自动化

16. **《设施农业环境工程学》** - 李保明，中国农业大学出版社
    - 温室环境控制
    - 光照补偿
    - 灌溉控制

17. **《智能温室控制系统设计》** - 王永维，化学工业出版社
    - 温室自动化
    - 传感器布置
    - 控制算法

### 嵌入式系统

18. **《STM32库开发实战指南》** - 刘火良，机械工业出版社
    - STM32 HAL库
    - 外设配置
    - 项目实战

19. **《嵌入式实时操作系统》** - 邵贝贝，清华大学出版社
    - FreeRTOS原理
    - 任务调度
    - 资源管理

### 物联网平台

20. **InfluxDB Documentation** - InfluxData
    - 时序数据库
    - Flux查询语言
    - 数据保留策略

21. **Grafana Documentation** - Grafana Labs
    - 仪表盘设计
    - 数据源配置
    - 告警规则

22. **Node-RED Documentation** - OpenJS Foundation
    - 可视化编程
    - MQTT集成
    - 仪表盘开发

### 能效标准

23. **GB/T 51350-2019** - 《近零能耗建筑技术标准》
    - 建筑能效
    - 节能设计
    - 能耗监测

24. **ISO 50001:2018** - Energy Management Systems
    - 能源管理体系
    - 能效优化
    - 持续改进

### 在线资源

25. **ASHRAE官网** - https://www.ashrae.org
    - 技术标准
    - 设计指南
    - 行业资讯

26. **STM32中文社区** - https://www.stmcu.org.cn
    - 技术论坛
    - 示例代码
    - 问题解答

27. **MQTT.org** - https://mqtt.org
    - 协议规范
    - 客户端库
    - 最佳实践

28. **Grafana Community** - https://community.grafana.com
    - 仪表盘分享
    - 插件开发
    - 技术讨论

---

## 附录：传感器参数速查

### DHT22 vs DHT11 vs SHT31

| 参数 | DHT11 | DHT22 | SHT31 |
|------|-------|-------|-------|
| 温度范围 | 0~50°C | -40~80°C | -40~125°C |
| 温度精度 | ±2°C | ±0.5°C | ±0.3°C |
| 湿度范围 | 20~80%RH | 0~100%RH | 0~100%RH |
| 湿度精度 | ±5%RH | ±2%RH | ±2%RH |
| 接口 | 单总线 | 单总线 | I2C |
| 采样率 | 1Hz | 0.5Hz | 最高10Hz |
| 价格 | ¥3 | ¥15 | ¥25 |
| 推荐场景 | 学习/低精度 | 一般应用 | 高精度/工业 |

### MH-Z19B vs SCD30 vs SCD41

| 参数 | MH-Z19B | SCD30 | SCD41 |
|------|---------|-------|-------|
| 测量原理 | NDIR | NDIR | 光声 |
| 量程 | 0~5000ppm | 400~10000ppm | 400~2000ppm |
| 精度 | ±50ppm | ±30ppm | ±40ppm |
| 预热时间 | 3分钟 | 2秒 | 5秒 |
| 接口 | UART/PWM | I2C/UART | I2C |
| 价格 | ¥65 | ¥350 | ¥200 |
| 推荐场景 | 一般应用 | 高精度 | 低功耗/便携 |

### 规则引擎参数参考

```
温室大棚推荐阈值：
  温度：
    加热器开启：< 15°C（持续5分钟）
    加热器关闭：> 20°C（持续5分钟）
    空调开启：> 30°C（持续5分钟）
    空调关闭：< 25°C（持续5分钟）
  
  湿度：
    加湿器开启：< 50%RH（持续5分钟）
    加湿器关闭：> 70%RH（持续5分钟）
    排风扇开启：> 85%RH（持续2分钟）
  
  CO₂：
    排风扇开启：> 1000ppm（持续2分钟）
    排风扇关闭：< 600ppm（持续5分钟）
  
  光照：
    补光灯开启：< 500lux（持续5分钟，且时间在6:00~20:00）
    补光灯关闭：> 2000lux（持续5分钟）

机房推荐阈值：
  温度：
    备用空调开启：> 25°C（持续2分钟）
    告警：> 28°C（立即）
    严重告警：> 32°C（立即，同时发送短信）
  
  湿度：
    告警（过低）：< 30%RH（静电风险）
    告警（过高）：> 70%RH（结露风险）
```
