---
# 基础信息
title: "电池管理系统(BMS)设计实战"
description: "深入讲解电池管理系统(BMS)的设计与实现，包括电量计算算法、充放电控制、电池保护、均衡管理和通信接口，通过实战项目掌握BMS核心技术"
slug: "bms-design-practical"

# 分类信息
domain: "01-hardware-layer"
module: "03-power-management"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - BMS
  - 电池管理
  - 充放电控制
  - 电量计算
  - 电池保护
  - 均衡管理
prerequisites:
  - "01-power-design-basics"
  - "03-battery-powered-system"
  - "04-power-monitoring"
related_contents:
  - "02-low-power-design"
  - "05-power-measurement"

# 学习信息
estimated_time: 90
difficulty_score: 6

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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - BMS设计
  - 电池管理系统
  - 电量计算
  - 充放电控制
  - 电池保护
  - SOC算法
cover_image: ""
---

# 电池管理系统(BMS)设计实战

## 概述


电池管理系统(Battery Management System, BMS)是电池供电设备的核心组件，负责监测电池状态、控制充放电过程、保护电池安全、延长电池寿命。本教程将通过实战项目，深入讲解BMS的设计与实现。

### 什么是BMS

BMS是一个智能电子系统，用于管理可充电电池组，主要功能包括：

1. **状态监测**：
   - 电压监测（单体/总压）
   - 电流监测（充电/放电）
   - 温度监测（多点测温）
   - 电量估算（SOC计算）

2. **安全保护**：
   - 过充保护
   - 过放保护
   - 过流保护
   - 过温保护
   - 短路保护

3. **充放电控制**：
   - 充电管理
   - 放电管理
   - 预充电控制
   - 充电均衡

4. **通信接口**：
   - 与主控通信
   - 数据上报
   - 参数配置
   - 故障诊断

### BMS的重要性

```
为什么需要BMS：

1. 安全性
   - 防止电池过充/过放
   - 避免热失控
   - 防止短路起火
   - 保护人身安全

2. 可靠性
   - 延长电池寿命
   - 提高系统稳定性
   - 减少故障率
   - 降低维护成本

3. 性能优化
   - 准确的电量显示
   - 优化充放电策略
   - 提高能量利用率
   - 改善用户体验

4. 法规要求
   - 满足安全认证
   - 符合行业标准
   - 通过质量检测
   - 获得市场准入
```

### 应用场景

- **消费电子**：手机、平板、笔记本电脑
- **电动工具**：电钻、电锯、割草机
- **电动车辆**：电动自行车、电动汽车
- **储能系统**：家庭储能、UPS电源
- **便携设备**：移动电源、无人机



## 第一部分：BMS系统架构

### 硬件架构

**典型BMS硬件组成**：

```
BMS硬件架构：

┌─────────────────────────────────────────────────────┐
│                    主控MCU                           │
│  (STM32F103 / ESP32 / nRF52)                       │
│  - 核心控制逻辑                                      │
│  - 算法计算                                          │
│  - 通信管理                                          │
└──────┬──────────┬──────────┬──────────┬────────────┘
       │          │          │          │
   ┌───▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼────┐
   │电压监测│  │电流监测│  │温度监测│  │充放电控制│
   │芯片    │  │电路    │  │电路    │  │MOSFET   │
   │(AFE)  │  │(霍尔)  │  │(NTC)  │  │驱动     │
   └───┬───┘  └──┬───┘  └──┬───┘  └──┬────┘
       │          │          │          │
   ┌───▼──────────▼──────────▼──────────▼────┐
   │              电池组                       │
   │  Cell1  Cell2  Cell3  ...  CellN        │
   └──────────────────────────────────────────┘

关键组件：
1. 主控MCU：STM32F103C8T6
2. 电压监测：BQ76920 (3-5串锂电池)
3. 电流检测：ACS712 (霍尔传感器)
4. 温度监测：NTC热敏电阻 × 2
5. 充放电控制：N-MOSFET × 2
6. 通信接口：UART/CAN/I2C
```

### 软件架构

**BMS软件模块**：

```c
/**
 * @file    bms_architecture.h
 * @brief   BMS软件架构定义
 */

#ifndef BMS_ARCHITECTURE_H
#define BMS_ARCHITECTURE_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief  BMS系统状态
 */
typedef enum {
    BMS_STATE_INIT = 0,        // 初始化
    BMS_STATE_IDLE,            // 空闲
    BMS_STATE_CHARGING,        // 充电中
    BMS_STATE_DISCHARGING,     // 放电中
    BMS_STATE_BALANCING,       // 均衡中
    BMS_STATE_FAULT,           // 故障
    BMS_STATE_SLEEP            // 休眠
} BMS_State_t;

/**
 * @brief  电池参数
 */
typedef struct {
    uint16_t cell_voltage[5];  // 单体电压 (mV)
    uint16_t pack_voltage;     // 总电压 (mV)
    int16_t  current;          // 电流 (mA, 正=充电, 负=放电)
    int16_t  temperature[2];   // 温度 (0.1°C)
    uint8_t  soc;              // 电量百分比 (0-100%)
    uint8_t  soh;              // 健康度 (0-100%)
    uint32_t capacity_mah;     // 剩余容量 (mAh)
} BMS_BatteryParams_t;

/**
 * @brief  保护状态
 */
typedef struct {
    bool overcharge;           // 过充保护
    bool overdischarge;        // 过放保护
    bool overcurrent_charge;   // 充电过流
    bool overcurrent_discharge;// 放电过流
    bool overtemperature;      // 过温保护
    bool undertemperature;     // 低温保护
    bool short_circuit;        // 短路保护
    bool cell_imbalance;       // 单体不均衡
} BMS_Protection_t;

/**
 * @brief  BMS配置参数
 */
typedef struct {
    uint16_t cell_overvoltage_mv;      // 单体过充电压 (mV)
    uint16_t cell_undervoltage_mv;     // 单体过放电压 (mV)
    uint16_t charge_overcurrent_ma;    // 充电过流阈值 (mA)
    uint16_t discharge_overcurrent_ma; // 放电过流阈值 (mA)
    int16_t  overtemperature_c;        // 过温阈值 (°C)
    int16_t  undertemperature_c;       // 低温阈值 (°C)
    uint16_t balance_voltage_diff_mv;  // 均衡电压差 (mV)
    uint32_t design_capacity_mah;      // 设计容量 (mAh)
} BMS_Config_t;

/**
 * @brief  BMS主数据结构
 */
typedef struct {
    BMS_State_t state;                 // 系统状态
    BMS_BatteryParams_t battery;       // 电池参数
    BMS_Protection_t protection;       // 保护状态
    BMS_Config_t config;               // 配置参数
    uint32_t timestamp_ms;             // 时间戳
    uint32_t cycle_count;              // 循环次数
} BMS_Handle_t;

#endif // BMS_ARCHITECTURE_H
```



## 第二部分：电量计算算法

### SOC (State of Charge) 计算

SOC表示电池的剩余电量百分比，是BMS最重要的功能之一。

**常用SOC计算方法**：

```
SOC计算方法对比：

1. 开路电压法 (OCV)
   优点：简单、无需电流传感器
   缺点：需要静置、精度低
   适用：低成本应用

2. 安时积分法 (Coulomb Counting)
   优点：实时、精度高
   缺点：累积误差、需要校准
   适用：大多数应用

3. 卡尔曼滤波法
   优点：精度最高、自适应
   缺点：计算复杂、资源消耗大
   适用：高端应用

4. 混合算法
   优点：综合优势、精度高
   缺点：实现复杂
   适用：推荐方案
```

### 安时积分法实现

```c
/**
 * @file    soc_calculation.c
 * @brief   SOC计算算法实现
 */

#include "bms_architecture.h"
#include <math.h>

/**
 * @brief  SOC计算器数据结构
 */
typedef struct {
    float soc_percent;              // 当前SOC (%)
    float remaining_capacity_mah;   // 剩余容量 (mAh)
    float full_capacity_mah;        // 满充容量 (mAh)
    uint32_t last_update_ms;        // 上次更新时间
    bool initialized;               // 是否已初始化
} SOC_Calculator_t;

static SOC_Calculator_t soc_calc = {0};

/**
 * @brief  初始化SOC计算器
 * @param  initial_soc: 初始SOC (%)
 * @param  capacity_mah: 电池容量 (mAh)
 */
void SOC_Init(float initial_soc, float capacity_mah) {
    soc_calc.soc_percent = initial_soc;
    soc_calc.full_capacity_mah = capacity_mah;
    soc_calc.remaining_capacity_mah = capacity_mah * initial_soc / 100.0f;
    soc_calc.last_update_ms = HAL_GetTick();
    soc_calc.initialized = true;
    
    printf("SOC初始化: %.1f%%, 容量: %.0f mAh\n", 
           initial_soc, capacity_mah);
}

/**
 * @brief  通过OCV估算初始SOC
 * @param  voltage_mv: 开路电压 (mV)
 * @retval 估算的SOC (%)
 */
float SOC_EstimateFromOCV(uint16_t voltage_mv) {
    // 锂电池OCV-SOC曲线（3.7V标称电压）
    // 这是一个简化的线性近似，实际应使用查表法
    
    const uint16_t voltage_100 = 4200;  // 100% SOC电压
    const uint16_t voltage_0   = 3000;  // 0% SOC电压
    
    if (voltage_mv >= voltage_100) {
        return 100.0f;
    } else if (voltage_mv <= voltage_0) {
        return 0.0f;
    }
    
    // 线性插值
    float soc = (float)(voltage_mv - voltage_0) / 
                (voltage_100 - voltage_0) * 100.0f;
    
    return soc;
}

/**
 * @brief  更新SOC（安时积分法）
 * @param  current_ma: 当前电流 (mA, 正=充电, 负=放电)
 * @param  timestamp_ms: 当前时间戳 (ms)
 */
void SOC_Update(int16_t current_ma, uint32_t timestamp_ms) {
    if (!soc_calc.initialized) {
        printf("错误：SOC未初始化\n");
        return;
    }
    
    // 计算时间差 (小时)
    uint32_t delta_ms = timestamp_ms - soc_calc.last_update_ms;
    float delta_hours = delta_ms / 3600000.0f;
    
    // 计算电量变化 (mAh)
    // Q = I × t
    float delta_capacity = current_ma * delta_hours;
    
    // 更新剩余容量
    soc_calc.remaining_capacity_mah += delta_capacity;
    
    // 限制范围
    if (soc_calc.remaining_capacity_mah > soc_calc.full_capacity_mah) {
        soc_calc.remaining_capacity_mah = soc_calc.full_capacity_mah;
    } else if (soc_calc.remaining_capacity_mah < 0) {
        soc_calc.remaining_capacity_mah = 0;
    }
    
    // 计算SOC百分比
    soc_calc.soc_percent = soc_calc.remaining_capacity_mah / 
                           soc_calc.full_capacity_mah * 100.0f;
    
    // 更新时间戳
    soc_calc.last_update_ms = timestamp_ms;
}

/**
 * @brief  获取当前SOC
 * @retval SOC百分比 (0-100%)
 */
float SOC_GetPercent(void) {
    return soc_calc.soc_percent;
}

/**
 * @brief  获取剩余容量
 * @retval 剩余容量 (mAh)
 */
float SOC_GetRemainingCapacity(void) {
    return soc_calc.remaining_capacity_mah;
}

/**
 * @brief  SOC校准（充满时）
 */
void SOC_CalibrateFullCharge(void) {
    soc_calc.soc_percent = 100.0f;
    soc_calc.remaining_capacity_mah = soc_calc.full_capacity_mah;
    printf("SOC校准：充满 100%%\n");
}

/**
 * @brief  SOC校准（放空时）
 */
void SOC_CalibrateEmpty(void) {
    soc_calc.soc_percent = 0.0f;
    soc_calc.remaining_capacity_mah = 0.0f;
    printf("SOC校准：放空 0%%\n");
}

/**
 * @brief  混合SOC算法（安时积分 + OCV校准）
 * @param  current_ma: 电流 (mA)
 * @param  voltage_mv: 电压 (mV)
 * @param  timestamp_ms: 时间戳 (ms)
 */
void SOC_UpdateHybrid(int16_t current_ma, uint16_t voltage_mv, 
                      uint32_t timestamp_ms) {
    // 1. 安时积分更新
    SOC_Update(current_ma, timestamp_ms);
    
    // 2. 静置时使用OCV校准
    static uint32_t idle_start_ms = 0;
    const uint32_t IDLE_TIME_MS = 300000;  // 5分钟静置
    
    if (abs(current_ma) < 50) {  // 电流小于50mA视为静置
        if (idle_start_ms == 0) {
            idle_start_ms = timestamp_ms;
        } else if (timestamp_ms - idle_start_ms > IDLE_TIME_MS) {
            // 静置足够长时间，使用OCV校准
            float ocv_soc = SOC_EstimateFromOCV(voltage_mv);
            
            // 加权融合
            float weight_ocv = 0.3f;  // OCV权重
            float weight_cc = 0.7f;   // 安时积分权重
            
            soc_calc.soc_percent = soc_calc.soc_percent * weight_cc + 
                                   ocv_soc * weight_ocv;
            
            soc_calc.remaining_capacity_mah = soc_calc.soc_percent / 100.0f *
                                              soc_calc.full_capacity_mah;
            
            printf("SOC混合校准: CC=%.1f%%, OCV=%.1f%%, 融合=%.1f%%\n",
                   soc_calc.soc_percent * weight_cc / (weight_cc + weight_ocv),
                   ocv_soc,
                   soc_calc.soc_percent);
            
            idle_start_ms = 0;  // 重置静置计时
        }
    } else {
        idle_start_ms = 0;  // 有电流，重置静置计时
    }
}
```



## 第三部分：充放电控制

### 充电管理

**充电阶段**：

```
锂电池充电曲线（CC-CV）：

电压
  │
4.2V├─────────────────────────┐
  │                           │ CV恒压阶段
  │                           │ (电流逐渐减小)
  │                           │
3.7V├──────────────┐          │
  │                │          │
  │  CC恒流阶段    │          │
  │  (恒定电流)    │          │
  │                │          │
3.0V├────────────────┴──────────┴─────→ 时间
    预充电  恒流充电(CC)  恒压充电(CV)  充满

充电阶段：
1. 预充电 (Pre-charge)
   - 条件：电压 < 3.0V
   - 电流：0.1C
   - 目的：激活深度放电的电池

2. 恒流充电 (CC)
   - 条件：3.0V < 电压 < 4.2V
   - 电流：0.5C - 1C
   - 目的：快速充电

3. 恒压充电 (CV)
   - 条件：电压 = 4.2V
   - 电流：逐渐减小
   - 目的：充满电池

4. 充电完成
   - 条件：电流 < 0.05C
   - 动作：停止充电
```

### 充电控制实现

```c
/**
 * @file    charge_control.c
 * @brief   充电控制实现
 */

#include "bms_architecture.h"

/**
 * @brief  充电状态
 */
typedef enum {
    CHARGE_STATE_IDLE = 0,     // 空闲
    CHARGE_STATE_PRECHARGE,    // 预充电
    CHARGE_STATE_CC,           // 恒流充电
    CHARGE_STATE_CV,           // 恒压充电
    CHARGE_STATE_COMPLETE,     // 充电完成
    CHARGE_STATE_FAULT         // 故障
} ChargeState_t;

/**
 * @brief  充电控制器
 */
typedef struct {
    ChargeState_t state;       // 充电状态
    uint32_t charge_start_ms;  // 充电开始时间
    uint32_t state_start_ms;   // 当前状态开始时间
    float accumulated_mah;     // 累积充电量
} ChargeController_t;

static ChargeController_t charge_ctrl = {0};

/**
 * @brief  充电参数配置
 */
#define PRECHARGE_VOLTAGE_MV    3000   // 预充电电压阈值
#define CC_VOLTAGE_MV           4200   // 恒流充电目标电压
#define CV_VOLTAGE_MV           4200   // 恒压充电电压
#define PRECHARGE_CURRENT_MA    200    // 预充电电流 (0.1C for 2000mAh)
#define CC_CURRENT_MA           1000   // 恒流充电电流 (0.5C for 2000mAh)
#define CV_CUTOFF_CURRENT_MA    100    // 恒压截止电流 (0.05C)
#define CHARGE_TIMEOUT_MS       14400000  // 充电超时 (4小时)

/**
 * @brief  初始化充电控制器
 */
void Charge_Init(void) {
    charge_ctrl.state = CHARGE_STATE_IDLE;
    charge_ctrl.charge_start_ms = 0;
    charge_ctrl.state_start_ms = 0;
    charge_ctrl.accumulated_mah = 0;
    
    printf("充电控制器初始化完成\n");
}

/**
 * @brief  开始充电
 */
void Charge_Start(void) {
    charge_ctrl.state = CHARGE_STATE_PRECHARGE;
    charge_ctrl.charge_start_ms = HAL_GetTick();
    charge_ctrl.state_start_ms = HAL_GetTick();
    charge_ctrl.accumulated_mah = 0;
    
    printf("开始充电\n");
}

/**
 * @brief  停止充电
 */
void Charge_Stop(void) {
    charge_ctrl.state = CHARGE_STATE_IDLE;
    
    // 关闭充电MOSFET
    HAL_GPIO_WritePin(CHARGE_MOSFET_GPIO, CHARGE_MOSFET_PIN, GPIO_PIN_RESET);
    
    printf("停止充电\n");
}

/**
 * @brief  充电状态机
 * @param  bms: BMS句柄
 */
void Charge_StateMachine(BMS_Handle_t* bms) {
    uint16_t voltage = bms->battery.pack_voltage;
    int16_t current = bms->battery.current;
    uint32_t now_ms = HAL_GetTick();
    
    switch (charge_ctrl.state) {
        case CHARGE_STATE_IDLE:
            // 空闲状态，等待开始充电
            break;
            
        case CHARGE_STATE_PRECHARGE:
            printf("预充电阶段: 电压=%d mV, 电流=%d mA\n", voltage, current);
            
            // 设置预充电电流
            Charge_SetCurrent(PRECHARGE_CURRENT_MA);
            
            // 检查是否进入恒流充电
            if (voltage >= PRECHARGE_VOLTAGE_MV) {
                charge_ctrl.state = CHARGE_STATE_CC;
                charge_ctrl.state_start_ms = now_ms;
                printf("进入恒流充电阶段\n");
            }
            
            // 超时检查
            if (now_ms - charge_ctrl.state_start_ms > 1800000) {  // 30分钟
                printf("预充电超时\n");
                charge_ctrl.state = CHARGE_STATE_FAULT;
            }
            break;
            
        case CHARGE_STATE_CC:
            printf("恒流充电阶段: 电压=%d mV, 电流=%d mA\n", voltage, current);
            
            // 设置恒流充电电流
            Charge_SetCurrent(CC_CURRENT_MA);
            
            // 检查是否进入恒压充电
            if (voltage >= CC_VOLTAGE_MV) {
                charge_ctrl.state = CHARGE_STATE_CV;
                charge_ctrl.state_start_ms = now_ms;
                printf("进入恒压充电阶段\n");
            }
            
            // 超时检查
            if (now_ms - charge_ctrl.charge_start_ms > CHARGE_TIMEOUT_MS) {
                printf("充电超时\n");
                charge_ctrl.state = CHARGE_STATE_FAULT;
            }
            break;
            
        case CHARGE_STATE_CV:
            printf("恒压充电阶段: 电压=%d mV, 电流=%d mA\n", voltage, current);
            
            // 设置恒压充电电压
            Charge_SetVoltage(CV_VOLTAGE_MV);
            
            // 检查是否充电完成
            if (current < CV_CUTOFF_CURRENT_MA) {
                charge_ctrl.state = CHARGE_STATE_COMPLETE;
                charge_ctrl.state_start_ms = now_ms;
                printf("充电完成\n");
                
                // SOC校准为100%
                SOC_CalibrateFullCharge();
            }
            
            // 超时检查
            if (now_ms - charge_ctrl.charge_start_ms > CHARGE_TIMEOUT_MS) {
                printf("充电超时\n");
                charge_ctrl.state = CHARGE_STATE_FAULT;
            }
            break;
            
        case CHARGE_STATE_COMPLETE:
            // 充电完成，停止充电
            Charge_Stop();
            break;
            
        case CHARGE_STATE_FAULT:
            // 故障状态，停止充电
            Charge_Stop();
            printf("充电故障\n");
            break;
    }
}

/**
 * @brief  设置充电电流（硬件相关）
 * @param  current_ma: 目标电流 (mA)
 */
void Charge_SetCurrent(uint16_t current_ma) {
    // 这里需要根据实际硬件实现
    // 例如：通过DAC或PWM控制充电芯片的电流设置引脚
    
    // 示例：使用DAC输出控制电流
    // DAC_value = current_ma / 1000.0 * 4095 / 3.3;
    // HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, DAC_value);
    
    printf("设置充电电流: %d mA\n", current_ma);
}

/**
 * @brief  设置充电电压（硬件相关）
 * @param  voltage_mv: 目标电压 (mV)
 */
void Charge_SetVoltage(uint16_t voltage_mv) {
    // 这里需要根据实际硬件实现
    // 例如：通过DAC或PWM控制充电芯片的电压设置引脚
    
    printf("设置充电电压: %d mV\n", voltage_mv);
}

/**
 * @brief  获取充电状态
 * @retval 充电状态
 */
ChargeState_t Charge_GetState(void) {
    return charge_ctrl.state;
}
```

### 放电管理

```c
/**
 * @file    discharge_control.c
 * @brief   放电控制实现
 */

/**
 * @brief  放电状态
 */
typedef enum {
    DISCHARGE_STATE_IDLE = 0,      // 空闲
    DISCHARGE_STATE_NORMAL,        // 正常放电
    DISCHARGE_STATE_LIMITED,       // 限流放电
    DISCHARGE_STATE_CUTOFF,        // 截止放电
    DISCHARGE_STATE_FAULT          // 故障
} DischargeState_t;

/**
 * @brief  放电控制器
 */
typedef struct {
    DischargeState_t state;        // 放电状态
    uint32_t discharge_start_ms;   // 放电开始时间
    float accumulated_mah;         // 累积放电量
    uint16_t current_limit_ma;     // 电流限制
} DischargeController_t;

static DischargeController_t discharge_ctrl = {0};

/**
 * @brief  放电参数配置
 */
#define DISCHARGE_CUTOFF_VOLTAGE_MV  3000   // 放电截止电压
#define DISCHARGE_MAX_CURRENT_MA     3000   // 最大放电电流
#define DISCHARGE_LIMIT_VOLTAGE_MV   3200   // 限流电压阈值
#define DISCHARGE_LIMITED_CURRENT_MA 1000   // 限流值

/**
 * @brief  初始化放电控制器
 */
void Discharge_Init(void) {
    discharge_ctrl.state = DISCHARGE_STATE_IDLE;
    discharge_ctrl.discharge_start_ms = 0;
    discharge_ctrl.accumulated_mah = 0;
    discharge_ctrl.current_limit_ma = DISCHARGE_MAX_CURRENT_MA;
    
    printf("放电控制器初始化完成\n");
}

/**
 * @brief  使能放电
 */
void Discharge_Enable(void) {
    discharge_ctrl.state = DISCHARGE_STATE_NORMAL;
    discharge_ctrl.discharge_start_ms = HAL_GetTick();
    
    // 打开放电MOSFET
    HAL_GPIO_WritePin(DISCHARGE_MOSFET_GPIO, DISCHARGE_MOSFET_PIN, GPIO_PIN_SET);
    
    printf("使能放电\n");
}

/**
 * @brief  禁止放电
 */
void Discharge_Disable(void) {
    discharge_ctrl.state = DISCHARGE_STATE_IDLE;
    
    // 关闭放电MOSFET
    HAL_GPIO_WritePin(DISCHARGE_MOSFET_GPIO, DISCHARGE_MOSFET_PIN, GPIO_PIN_RESET);
    
    printf("禁止放电\n");
}

/**
 * @brief  放电状态机
 * @param  bms: BMS句柄
 */
void Discharge_StateMachine(BMS_Handle_t* bms) {
    uint16_t voltage = bms->battery.pack_voltage;
    int16_t current = abs(bms->battery.current);  // 放电电流为负值，取绝对值
    
    switch (discharge_ctrl.state) {
        case DISCHARGE_STATE_IDLE:
            // 空闲状态
            break;
            
        case DISCHARGE_STATE_NORMAL:
            printf("正常放电: 电压=%d mV, 电流=%d mA\n", voltage, current);
            
            // 检查是否需要限流
            if (voltage < DISCHARGE_LIMIT_VOLTAGE_MV) {
                discharge_ctrl.state = DISCHARGE_STATE_LIMITED;
                discharge_ctrl.current_limit_ma = DISCHARGE_LIMITED_CURRENT_MA;
                printf("进入限流放电\n");
            }
            
            // 检查是否达到截止电压
            if (voltage < DISCHARGE_CUTOFF_VOLTAGE_MV) {
                discharge_ctrl.state = DISCHARGE_STATE_CUTOFF;
                Discharge_Disable();
                printf("达到放电截止电压\n");
                
                // SOC校准为0%
                SOC_CalibrateEmpty();
            }
            break;
            
        case DISCHARGE_STATE_LIMITED:
            printf("限流放电: 电压=%d mV, 电流=%d mA (限制=%d mA)\n",
                   voltage, current, discharge_ctrl.current_limit_ma);
            
            // 检查是否恢复正常
            if (voltage > DISCHARGE_LIMIT_VOLTAGE_MV + 100) {  // 加100mV滞回
                discharge_ctrl.state = DISCHARGE_STATE_NORMAL;
                discharge_ctrl.current_limit_ma = DISCHARGE_MAX_CURRENT_MA;
                printf("恢复正常放电\n");
            }
            
            // 检查是否达到截止电压
            if (voltage < DISCHARGE_CUTOFF_VOLTAGE_MV) {
                discharge_ctrl.state = DISCHARGE_STATE_CUTOFF;
                Discharge_Disable();
                printf("达到放电截止电压\n");
                SOC_CalibrateEmpty();
            }
            break;
            
        case DISCHARGE_STATE_CUTOFF:
            // 放电截止，已禁止放电
            break;
            
        case DISCHARGE_STATE_FAULT:
            // 故障状态
            Discharge_Disable();
            break;
    }
}

/**
 * @brief  获取放电电流限制
 * @retval 电流限制 (mA)
 */
uint16_t Discharge_GetCurrentLimit(void) {
    return discharge_ctrl.current_limit_ma;
}
```



## 第四部分：电池保护

### 保护功能实现

```c
/**
 * @file    battery_protection.c
 * @brief   电池保护功能实现
 */

#include "bms_architecture.h"

/**
 * @brief  保护检查结果
 */
typedef struct {
    bool fault_detected;       // 是否检测到故障
    char fault_message[64];    // 故障信息
} ProtectionCheck_t;

/**
 * @brief  过充保护检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckOvercharge(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    
    // 检查单体电压
    for (int i = 0; i < 5; i++) {
        if (bms->battery.cell_voltage[i] > bms->config.cell_overvoltage_mv) {
            result.fault_detected = true;
            snprintf(result.fault_message, sizeof(result.fault_message),
                    "单体%d过充: %d mV > %d mV", 
                    i+1, 
                    bms->battery.cell_voltage[i],
                    bms->config.cell_overvoltage_mv);
            
            // 设置保护标志
            bms->protection.overcharge = true;
            
            // 停止充电
            Charge_Stop();
            
            printf("⚠ %s\n", result.fault_message);
            break;
        }
    }
    
    return result;
}

/**
 * @brief  过放保护检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckOverdischarge(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    
    // 检查单体电压
    for (int i = 0; i < 5; i++) {
        if (bms->battery.cell_voltage[i] < bms->config.cell_undervoltage_mv) {
            result.fault_detected = true;
            snprintf(result.fault_message, sizeof(result.fault_message),
                    "单体%d过放: %d mV < %d mV",
                    i+1,
                    bms->battery.cell_voltage[i],
                    bms->config.cell_undervoltage_mv);
            
            // 设置保护标志
            bms->protection.overdischarge = true;
            
            // 停止放电
            Discharge_Disable();
            
            printf("⚠ %s\n", result.fault_message);
            break;
        }
    }
    
    return result;
}

/**
 * @brief  过流保护检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckOvercurrent(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    int16_t current = bms->battery.current;
    
    // 检查充电过流
    if (current > 0 && current > bms->config.charge_overcurrent_ma) {
        result.fault_detected = true;
        snprintf(result.fault_message, sizeof(result.fault_message),
                "充电过流: %d mA > %d mA",
                current,
                bms->config.charge_overcurrent_ma);
        
        bms->protection.overcurrent_charge = true;
        Charge_Stop();
        
        printf("⚠ %s\n", result.fault_message);
    }
    
    // 检查放电过流
    if (current < 0 && abs(current) > bms->config.discharge_overcurrent_ma) {
        result.fault_detected = true;
        snprintf(result.fault_message, sizeof(result.fault_message),
                "放电过流: %d mA > %d mA",
                abs(current),
                bms->config.discharge_overcurrent_ma);
        
        bms->protection.overcurrent_discharge = true;
        Discharge_Disable();
        
        printf("⚠ %s\n", result.fault_message);
    }
    
    return result;
}

/**
 * @brief  温度保护检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckTemperature(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    
    for (int i = 0; i < 2; i++) {
        int16_t temp = bms->battery.temperature[i] / 10;  // 转换为°C
        
        // 检查过温
        if (temp > bms->config.overtemperature_c) {
            result.fault_detected = true;
            snprintf(result.fault_message, sizeof(result.fault_message),
                    "温度%d过高: %d°C > %d°C",
                    i+1, temp, bms->config.overtemperature_c);
            
            bms->protection.overtemperature = true;
            
            // 停止充放电
            Charge_Stop();
            Discharge_Disable();
            
            printf("⚠ %s\n", result.fault_message);
            break;
        }
        
        // 检查低温
        if (temp < bms->config.undertemperature_c) {
            result.fault_detected = true;
            snprintf(result.fault_message, sizeof(result.fault_message),
                    "温度%d过低: %d°C < %d°C",
                    i+1, temp, bms->config.undertemperature_c);
            
            bms->protection.undertemperature = true;
            
            // 低温禁止充电
            Charge_Stop();
            
            printf("⚠ %s\n", result.fault_message);
            break;
        }
    }
    
    return result;
}

/**
 * @brief  短路保护检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckShortCircuit(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    
    // 短路判断：电流突然超过阈值（例如10A）
    const int16_t SHORT_CIRCUIT_CURRENT_MA = 10000;
    
    if (abs(bms->battery.current) > SHORT_CIRCUIT_CURRENT_MA) {
        result.fault_detected = true;
        snprintf(result.fault_message, sizeof(result.fault_message),
                "检测到短路: 电流=%d mA", bms->battery.current);
        
        bms->protection.short_circuit = true;
        
        // 立即断开充放电
        Charge_Stop();
        Discharge_Disable();
        
        printf("⚠⚠⚠ %s\n", result.fault_message);
    }
    
    return result;
}

/**
 * @brief  单体不均衡检查
 * @param  bms: BMS句柄
 * @retval 检查结果
 */
ProtectionCheck_t Protection_CheckCellImbalance(BMS_Handle_t* bms) {
    ProtectionCheck_t result = {false, ""};
    
    // 找出最高和最低电压
    uint16_t max_voltage = 0;
    uint16_t min_voltage = 65535;
    uint8_t max_cell = 0;
    uint8_t min_cell = 0;
    
    for (int i = 0; i < 5; i++) {
        if (bms->battery.cell_voltage[i] > max_voltage) {
            max_voltage = bms->battery.cell_voltage[i];
            max_cell = i;
        }
        if (bms->battery.cell_voltage[i] < min_voltage) {
            min_voltage = bms->battery.cell_voltage[i];
            min_cell = i;
        }
    }
    
    // 计算电压差
    uint16_t voltage_diff = max_voltage - min_voltage;
    
    if (voltage_diff > bms->config.balance_voltage_diff_mv) {
        result.fault_detected = true;
        snprintf(result.fault_message, sizeof(result.fault_message),
                "单体不均衡: Cell%d(%d mV) - Cell%d(%d mV) = %d mV",
                max_cell+1, max_voltage,
                min_cell+1, min_voltage,
                voltage_diff);
        
        bms->protection.cell_imbalance = true;
        
        printf("⚠ %s\n", result.fault_message);
    }
    
    return result;
}

/**
 * @brief  执行所有保护检查
 * @param  bms: BMS句柄
 * @retval 是否检测到故障
 */
bool Protection_CheckAll(BMS_Handle_t* bms) {
    bool fault_detected = false;
    
    // 清除之前的保护标志
    memset(&bms->protection, 0, sizeof(BMS_Protection_t));
    
    // 执行各项检查
    if (Protection_CheckOvercharge(bms).fault_detected) {
        fault_detected = true;
    }
    
    if (Protection_CheckOverdischarge(bms).fault_detected) {
        fault_detected = true;
    }
    
    if (Protection_CheckOvercurrent(bms).fault_detected) {
        fault_detected = true;
    }
    
    if (Protection_CheckTemperature(bms).fault_detected) {
        fault_detected = true;
    }
    
    if (Protection_CheckShortCircuit(bms).fault_detected) {
        fault_detected = true;
    }
    
    if (Protection_CheckCellImbalance(bms).fault_detected) {
        fault_detected = true;
    }
    
    return fault_detected;
}

/**
 * @brief  清除保护故障（需要人工确认）
 * @param  bms: BMS句柄
 */
void Protection_ClearFaults(BMS_Handle_t* bms) {
    memset(&bms->protection, 0, sizeof(BMS_Protection_t));
    printf("保护故障已清除\n");
}
```



## 第五部分：均衡管理

### 被动均衡原理

```
被动均衡（电阻放电）：

高电压单体 ──→ [均衡电阻] ──→ 热量
                 ↓
              能量损耗

优点：
- 电路简单
- 成本低
- 可靠性高

缺点：
- 能量浪费
- 产生热量
- 均衡速度慢

主动均衡（能量转移）：

高电压单体 ──→ [DC-DC转换器] ──→ 低电压单体
                 ↓
              能量转移

优点：
- 能量利用率高
- 均衡速度快
- 发热少

缺点：
- 电路复杂
- 成本高
- 可靠性相对低
```

### 被动均衡实现

```c
/**
 * @file    cell_balancing.c
 * @brief   电池均衡管理实现
 */

#include "bms_architecture.h"

/**
 * @brief  均衡控制器
 */
typedef struct {
    bool balancing_active;         // 均衡是否激活
    uint8_t balance_cells;         // 需要均衡的单体（位掩码）
    uint32_t balance_start_ms;     // 均衡开始时间
    uint32_t balance_duration_ms;  // 均衡持续时间
} BalanceController_t;

static BalanceController_t balance_ctrl = {0};

/**
 * @brief  均衡参数配置
 */
#define BALANCE_VOLTAGE_THRESHOLD_MV  50    // 均衡电压差阈值
#define BALANCE_MIN_VOLTAGE_MV        3600  // 最低均衡电压
#define BALANCE_MAX_DURATION_MS       3600000  // 最大均衡时间（1小时）
#define BALANCE_CURRENT_MA            100   // 均衡电流（取决于均衡电阻）

/**
 * @brief  初始化均衡控制器
 */
void Balance_Init(void) {
    balance_ctrl.balancing_active = false;
    balance_ctrl.balance_cells = 0;
    balance_ctrl.balance_start_ms = 0;
    balance_ctrl.balance_duration_ms = 0;
    
    // 关闭所有均衡开关
    for (int i = 0; i < 5; i++) {
        Balance_SetCell(i, false);
    }
    
    printf("均衡控制器初始化完成\n");
}

/**
 * @brief  控制单体均衡开关
 * @param  cell_index: 单体索引 (0-4)
 * @param  enable: 使能/禁止
 */
void Balance_SetCell(uint8_t cell_index, bool enable) {
    // 这里需要根据实际硬件实现
    // 例如：通过GPIO控制MOSFET开关
    
    GPIO_TypeDef* gpio_port;
    uint16_t gpio_pin;
    
    switch (cell_index) {
        case 0: gpio_port = GPIOA; gpio_pin = GPIO_PIN_0; break;
        case 1: gpio_port = GPIOA; gpio_pin = GPIO_PIN_1; break;
        case 2: gpio_port = GPIOA; gpio_pin = GPIO_PIN_2; break;
        case 3: gpio_port = GPIOA; gpio_pin = GPIO_PIN_3; break;
        case 4: gpio_port = GPIOA; gpio_pin = GPIO_PIN_4; break;
        default: return;
    }
    
    HAL_GPIO_WritePin(gpio_port, gpio_pin, enable ? GPIO_PIN_SET : GPIO_PIN_RESET);
    
    printf("单体%d均衡: %s\n", cell_index+1, enable ? "开启" : "关闭");
}

/**
 * @brief  计算需要均衡的单体
 * @param  bms: BMS句柄
 * @retval 需要均衡的单体（位掩码）
 */
uint8_t Balance_CalculateTargets(BMS_Handle_t* bms) {
    uint8_t balance_targets = 0;
    
    // 找出最低电压
    uint16_t min_voltage = 65535;
    for (int i = 0; i < 5; i++) {
        if (bms->battery.cell_voltage[i] < min_voltage) {
            min_voltage = bms->battery.cell_voltage[i];
        }
    }
    
    // 标记需要均衡的单体（电压高于最低电压+阈值）
    for (int i = 0; i < 5; i++) {
        uint16_t voltage_diff = bms->battery.cell_voltage[i] - min_voltage;
        
        if (voltage_diff > BALANCE_VOLTAGE_THRESHOLD_MV &&
            bms->battery.cell_voltage[i] > BALANCE_MIN_VOLTAGE_MV) {
            balance_targets |= (1 << i);
            printf("单体%d需要均衡: %d mV (差值=%d mV)\n",
                   i+1, bms->battery.cell_voltage[i], voltage_diff);
        }
    }
    
    return balance_targets;
}

/**
 * @brief  开始均衡
 * @param  bms: BMS句柄
 */
void Balance_Start(BMS_Handle_t* bms) {
    // 计算需要均衡的单体
    balance_ctrl.balance_cells = Balance_CalculateTargets(bms);
    
    if (balance_ctrl.balance_cells == 0) {
        printf("无需均衡\n");
        return;
    }
    
    // 开启均衡
    balance_ctrl.balancing_active = true;
    balance_ctrl.balance_start_ms = HAL_GetTick();
    
    // 使能对应单体的均衡
    for (int i = 0; i < 5; i++) {
        if (balance_ctrl.balance_cells & (1 << i)) {
            Balance_SetCell(i, true);
        }
    }
    
    printf("开始均衡，目标单体: 0x%02X\n", balance_ctrl.balance_cells);
}

/**
 * @brief  停止均衡
 */
void Balance_Stop(void) {
    // 关闭所有均衡开关
    for (int i = 0; i < 5; i++) {
        Balance_SetCell(i, false);
    }
    
    balance_ctrl.balancing_active = false;
    balance_ctrl.balance_cells = 0;
    
    printf("停止均衡\n");
}

/**
 * @brief  均衡状态机
 * @param  bms: BMS句柄
 */
void Balance_StateMachine(BMS_Handle_t* bms) {
    if (!balance_ctrl.balancing_active) {
        return;
    }
    
    uint32_t now_ms = HAL_GetTick();
    uint32_t elapsed_ms = now_ms - balance_ctrl.balance_start_ms;
    
    // 检查是否超时
    if (elapsed_ms > BALANCE_MAX_DURATION_MS) {
        printf("均衡超时，停止均衡\n");
        Balance_Stop();
        return;
    }
    
    // 检查是否均衡完成
    uint8_t new_targets = Balance_CalculateTargets(bms);
    
    if (new_targets == 0) {
        printf("均衡完成，耗时: %.1f 分钟\n", elapsed_ms / 60000.0f);
        Balance_Stop();
        return;
    }
    
    // 更新均衡目标（可能有单体已经均衡完成）
    if (new_targets != balance_ctrl.balance_cells) {
        printf("更新均衡目标: 0x%02X -> 0x%02X\n",
               balance_ctrl.balance_cells, new_targets);
        
        // 关闭已完成的单体
        for (int i = 0; i < 5; i++) {
            if ((balance_ctrl.balance_cells & (1 << i)) &&
                !(new_targets & (1 << i))) {
                Balance_SetCell(i, false);
                printf("单体%d均衡完成\n", i+1);
            }
        }
        
        balance_ctrl.balance_cells = new_targets;
    }
    
    // 定期打印均衡进度
    static uint32_t last_print_ms = 0;
    if (now_ms - last_print_ms > 10000) {  // 每10秒打印一次
        printf("均衡进行中... 已耗时: %.1f 分钟\n", elapsed_ms / 60000.0f);
        
        for (int i = 0; i < 5; i++) {
            printf("  单体%d: %d mV %s\n",
                   i+1,
                   bms->battery.cell_voltage[i],
                   (balance_ctrl.balance_cells & (1 << i)) ? "[均衡中]" : "");
        }
        
        last_print_ms = now_ms;
    }
}

/**
 * @brief  判断是否需要均衡
 * @param  bms: BMS句柄
 * @retval true=需要均衡, false=不需要
 */
bool Balance_IsNeeded(BMS_Handle_t* bms) {
    uint8_t targets = Balance_CalculateTargets(bms);
    return (targets != 0);
}

/**
 * @brief  获取均衡状态
 * @retval true=均衡中, false=未均衡
 */
bool Balance_IsActive(void) {
    return balance_ctrl.balancing_active;
}
```



## 第六部分：通信接口

### UART通信协议

```c
/**
 * @file    bms_communication.c
 * @brief   BMS通信接口实现
 */

#include "bms_architecture.h"
#include <string.h>

/**
 * @brief  通信协议定义
 */
#define COMM_START_BYTE     0xAA
#define COMM_END_BYTE       0x55
#define COMM_MAX_DATA_LEN   64

/**
 * @brief  命令类型
 */
typedef enum {
    CMD_GET_STATUS = 0x01,         // 获取状态
    CMD_GET_VOLTAGE = 0x02,        // 获取电压
    CMD_GET_CURRENT = 0x03,        // 获取电流
    CMD_GET_TEMPERATURE = 0x04,    // 获取温度
    CMD_GET_SOC = 0x05,            // 获取SOC
    CMD_START_CHARGE = 0x10,       // 开始充电
    CMD_STOP_CHARGE = 0x11,        // 停止充电
    CMD_START_BALANCE = 0x12,      // 开始均衡
    CMD_STOP_BALANCE = 0x13,       // 停止均衡
    CMD_CLEAR_FAULTS = 0x14,       // 清除故障
    CMD_SET_CONFIG = 0x20,         // 设置配置
    CMD_GET_CONFIG = 0x21          // 获取配置
} CommCommand_t;

/**
 * @brief  通信数据包结构
 */
typedef struct {
    uint8_t start;                 // 起始字节 (0xAA)
    uint8_t command;               // 命令字节
    uint8_t length;                // 数据长度
    uint8_t data[COMM_MAX_DATA_LEN]; // 数据
    uint8_t checksum;              // 校验和
    uint8_t end;                   // 结束字节 (0x55)
} __attribute__((packed)) CommPacket_t;

/**
 * @brief  计算校验和
 * @param  data: 数据指针
 * @param  length: 数据长度
 * @retval 校验和
 */
uint8_t Comm_CalculateChecksum(uint8_t* data, uint8_t length) {
    uint8_t checksum = 0;
    for (uint8_t i = 0; i < length; i++) {
        checksum += data[i];
    }
    return checksum;
}

/**
 * @brief  发送数据包
 * @param  command: 命令
 * @param  data: 数据
 * @param  length: 数据长度
 */
void Comm_SendPacket(uint8_t command, uint8_t* data, uint8_t length) {
    CommPacket_t packet;
    
    packet.start = COMM_START_BYTE;
    packet.command = command;
    packet.length = length;
    
    if (length > 0 && data != NULL) {
        memcpy(packet.data, data, length);
    }
    
    // 计算校验和（命令 + 长度 + 数据）
    uint8_t checksum_data[2 + COMM_MAX_DATA_LEN];
    checksum_data[0] = packet.command;
    checksum_data[1] = packet.length;
    memcpy(&checksum_data[2], packet.data, length);
    packet.checksum = Comm_CalculateChecksum(checksum_data, 2 + length);
    
    packet.end = COMM_END_BYTE;
    
    // 发送数据包
    uint8_t packet_size = 5 + length;  // start + cmd + len + data + checksum + end
    HAL_UART_Transmit(&huart1, (uint8_t*)&packet, packet_size, 1000);
}

/**
 * @brief  处理接收到的命令
 * @param  bms: BMS句柄
 * @param  packet: 接收到的数据包
 */
void Comm_ProcessCommand(BMS_Handle_t* bms, CommPacket_t* packet) {
    uint8_t response_data[COMM_MAX_DATA_LEN];
    uint8_t response_length = 0;
    
    switch (packet->command) {
        case CMD_GET_STATUS:
            // 返回系统状态
            response_data[0] = bms->state;
            response_data[1] = bms->protection.overcharge ? 1 : 0;
            response_data[2] = bms->protection.overdischarge ? 1 : 0;
            response_data[3] = bms->protection.overcurrent_charge ? 1 : 0;
            response_data[4] = bms->protection.overcurrent_discharge ? 1 : 0;
            response_data[5] = bms->protection.overtemperature ? 1 : 0;
            response_length = 6;
            break;
            
        case CMD_GET_VOLTAGE:
            // 返回电压信息
            for (int i = 0; i < 5; i++) {
                response_data[i*2] = (bms->battery.cell_voltage[i] >> 8) & 0xFF;
                response_data[i*2+1] = bms->battery.cell_voltage[i] & 0xFF;
            }
            response_data[10] = (bms->battery.pack_voltage >> 8) & 0xFF;
            response_data[11] = bms->battery.pack_voltage & 0xFF;
            response_length = 12;
            break;
            
        case CMD_GET_CURRENT:
            // 返回电流信息
            response_data[0] = (bms->battery.current >> 8) & 0xFF;
            response_data[1] = bms->battery.current & 0xFF;
            response_length = 2;
            break;
            
        case CMD_GET_TEMPERATURE:
            // 返回温度信息
            for (int i = 0; i < 2; i++) {
                response_data[i*2] = (bms->battery.temperature[i] >> 8) & 0xFF;
                response_data[i*2+1] = bms->battery.temperature[i] & 0xFF;
            }
            response_length = 4;
            break;
            
        case CMD_GET_SOC:
            // 返回SOC信息
            response_data[0] = bms->battery.soc;
            response_data[1] = bms->battery.soh;
            response_data[2] = (bms->battery.capacity_mah >> 24) & 0xFF;
            response_data[3] = (bms->battery.capacity_mah >> 16) & 0xFF;
            response_data[4] = (bms->battery.capacity_mah >> 8) & 0xFF;
            response_data[5] = bms->battery.capacity_mah & 0xFF;
            response_length = 6;
            break;
            
        case CMD_START_CHARGE:
            // 开始充电
            Charge_Start();
            response_data[0] = 0x00;  // 成功
            response_length = 1;
            break;
            
        case CMD_STOP_CHARGE:
            // 停止充电
            Charge_Stop();
            response_data[0] = 0x00;  // 成功
            response_length = 1;
            break;
            
        case CMD_START_BALANCE:
            // 开始均衡
            Balance_Start(bms);
            response_data[0] = 0x00;  // 成功
            response_length = 1;
            break;
            
        case CMD_STOP_BALANCE:
            // 停止均衡
            Balance_Stop();
            response_data[0] = 0x00;  // 成功
            response_length = 1;
            break;
            
        case CMD_CLEAR_FAULTS:
            // 清除故障
            Protection_ClearFaults(bms);
            response_data[0] = 0x00;  // 成功
            response_length = 1;
            break;
            
        default:
            // 未知命令
            response_data[0] = 0xFF;  // 错误
            response_length = 1;
            break;
    }
    
    // 发送响应
    Comm_SendPacket(packet->command, response_data, response_length);
}

/**
 * @brief  接收数据包（中断回调）
 * @param  bms: BMS句柄
 * @param  rx_data: 接收缓冲区
 * @param  rx_length: 接收长度
 */
void Comm_ReceiveCallback(BMS_Handle_t* bms, uint8_t* rx_data, uint16_t rx_length) {
    static uint8_t rx_buffer[256];
    static uint16_t rx_index = 0;
    
    // 将接收数据添加到缓冲区
    for (uint16_t i = 0; i < rx_length; i++) {
        rx_buffer[rx_index++] = rx_data[i];
        
        // 防止缓冲区溢出
        if (rx_index >= sizeof(rx_buffer)) {
            rx_index = 0;
        }
    }
    
    // 查找完整的数据包
    for (uint16_t i = 0; i < rx_index - 5; i++) {
        if (rx_buffer[i] == COMM_START_BYTE) {
            uint8_t length = rx_buffer[i + 2];
            uint16_t packet_size = 5 + length;
            
            if (i + packet_size <= rx_index &&
                rx_buffer[i + packet_size - 1] == COMM_END_BYTE) {
                
                // 找到完整数据包
                CommPacket_t* packet = (CommPacket_t*)&rx_buffer[i];
                
                // 验证校验和
                uint8_t checksum_data[2 + COMM_MAX_DATA_LEN];
                checksum_data[0] = packet->command;
                checksum_data[1] = packet->length;
                memcpy(&checksum_data[2], packet->data, length);
                uint8_t calculated_checksum = Comm_CalculateChecksum(checksum_data, 2 + length);
                
                if (calculated_checksum == packet->checksum) {
                    // 校验通过，处理命令
                    Comm_ProcessCommand(bms, packet);
                } else {
                    printf("校验和错误\n");
                }
                
                // 移除已处理的数据包
                memmove(rx_buffer, &rx_buffer[i + packet_size], rx_index - i - packet_size);
                rx_index -= (i + packet_size);
                i = 0;
            }
        }
    }
}

/**
 * @brief  定期上报数据
 * @param  bms: BMS句柄
 */
void Comm_PeriodicReport(BMS_Handle_t* bms) {
    static uint32_t last_report_ms = 0;
    uint32_t now_ms = HAL_GetTick();
    
    // 每秒上报一次
    if (now_ms - last_report_ms >= 1000) {
        // 上报电压
        uint8_t voltage_data[12];
        for (int i = 0; i < 5; i++) {
            voltage_data[i*2] = (bms->battery.cell_voltage[i] >> 8) & 0xFF;
            voltage_data[i*2+1] = bms->battery.cell_voltage[i] & 0xFF;
        }
        voltage_data[10] = (bms->battery.pack_voltage >> 8) & 0xFF;
        voltage_data[11] = bms->battery.pack_voltage & 0xFF;
        Comm_SendPacket(CMD_GET_VOLTAGE, voltage_data, 12);
        
        // 上报SOC
        uint8_t soc_data[6];
        soc_data[0] = bms->battery.soc;
        soc_data[1] = bms->battery.soh;
        soc_data[2] = (bms->battery.capacity_mah >> 24) & 0xFF;
        soc_data[3] = (bms->battery.capacity_mah >> 16) & 0xFF;
        soc_data[4] = (bms->battery.capacity_mah >> 8) & 0xFF;
        soc_data[5] = bms->battery.capacity_mah & 0xFF;
        Comm_SendPacket(CMD_GET_SOC, soc_data, 6);
        
        last_report_ms = now_ms;
    }
}
```



## 第七部分：完整BMS主程序

### 主程序实现

```c
/**
 * @file    bms_main.c
 * @brief   BMS主程序
 */

#include "bms_architecture.h"

// 全局BMS句柄
BMS_Handle_t g_bms = {0};

/**
 * @brief  BMS初始化
 */
void BMS_Init(void) {
    printf("\n═══════════════════════════════════════════\n");
    printf("    电池管理系统 (BMS) 初始化\n");
    printf("═══════════════════════════════════════════\n\n");
    
    // 初始化状态
    g_bms.state = BMS_STATE_INIT;
    
    // 初始化配置参数
    g_bms.config.cell_overvoltage_mv = 4250;       // 4.25V
    g_bms.config.cell_undervoltage_mv = 2800;      // 2.8V
    g_bms.config.charge_overcurrent_ma = 2000;     // 2A
    g_bms.config.discharge_overcurrent_ma = 5000;  // 5A
    g_bms.config.overtemperature_c = 60;           // 60°C
    g_bms.config.undertemperature_c = 0;           // 0°C
    g_bms.config.balance_voltage_diff_mv = 50;     // 50mV
    g_bms.config.design_capacity_mah = 2000;       // 2000mAh
    
    printf("配置参数：\n");
    printf("  过充电压: %d mV\n", g_bms.config.cell_overvoltage_mv);
    printf("  过放电压: %d mV\n", g_bms.config.cell_undervoltage_mv);
    printf("  充电过流: %d mA\n", g_bms.config.charge_overcurrent_ma);
    printf("  放电过流: %d mA\n", g_bms.config.discharge_overcurrent_ma);
    printf("  设计容量: %d mAh\n\n", g_bms.config.design_capacity_mah);
    
    // 初始化各模块
    SOC_Init(50.0f, g_bms.config.design_capacity_mah);
    Charge_Init();
    Discharge_Init();
    Balance_Init();
    
    // 初始化硬件
    BMS_HardwareInit();
    
    // 读取初始电池参数
    BMS_ReadBatteryParams(&g_bms);
    
    // 根据电压估算初始SOC
    float initial_soc = SOC_EstimateFromOCV(g_bms.battery.pack_voltage / 5);
    SOC_Init(initial_soc, g_bms.config.design_capacity_mah);
    
    printf("初始电池状态：\n");
    printf("  总电压: %d mV\n", g_bms.battery.pack_voltage);
    printf("  电流: %d mA\n", g_bms.battery.current);
    printf("  温度: %.1f°C\n", g_bms.battery.temperature[0] / 10.0f);
    printf("  SOC: %.1f%%\n\n", initial_soc);
    
    // 进入空闲状态
    g_bms.state = BMS_STATE_IDLE;
    
    printf("BMS初始化完成\n");
    printf("═══════════════════════════════════════════\n\n");
}

/**
 * @brief  硬件初始化
 */
void BMS_HardwareInit(void) {
    // 初始化GPIO
    // 充电MOSFET控制引脚
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = CHARGE_MOSFET_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(CHARGE_MOSFET_GPIO, &GPIO_InitStruct);
    
    // 放电MOSFET控制引脚
    GPIO_InitStruct.Pin = DISCHARGE_MOSFET_PIN;
    HAL_GPIO_Init(DISCHARGE_MOSFET_GPIO, &GPIO_InitStruct);
    
    // 初始化ADC（用于电压/电流/温度采集）
    HAL_ADC_Start(&hadc1);
    
    // 初始化UART（用于通信）
    // 已在main.c中初始化
    
    printf("硬件初始化完成\n");
}

/**
 * @brief  读取电池参数
 * @param  bms: BMS句柄
 */
void BMS_ReadBatteryParams(BMS_Handle_t* bms) {
    // 读取单体电压（通过AFE芯片，如BQ76920）
    // 这里使用模拟数据，实际应从AFE芯片读取
    bms->battery.cell_voltage[0] = 3750;  // mV
    bms->battery.cell_voltage[1] = 3760;
    bms->battery.cell_voltage[2] = 3755;
    bms->battery.cell_voltage[3] = 3765;
    bms->battery.cell_voltage[4] = 3770;
    
    // 计算总电压
    bms->battery.pack_voltage = 0;
    for (int i = 0; i < 5; i++) {
        bms->battery.pack_voltage += bms->battery.cell_voltage[i];
    }
    
    // 读取电流（通过霍尔传感器）
    // 这里使用模拟数据
    bms->battery.current = 0;  // mA (正=充电, 负=放电)
    
    // 读取温度（通过NTC热敏电阻）
    // 这里使用模拟数据
    bms->battery.temperature[0] = 250;  // 25.0°C
    bms->battery.temperature[1] = 260;  // 26.0°C
    
    // 更新SOC
    bms->battery.soc = (uint8_t)SOC_GetPercent();
    bms->battery.capacity_mah = (uint32_t)SOC_GetRemainingCapacity();
    
    // 更新SOH（简化实现，实际需要复杂算法）
    bms->battery.soh = 100;  // 100%
    
    // 更新时间戳
    bms->timestamp_ms = HAL_GetTick();
}

/**
 * @brief  BMS主循环
 */
void BMS_MainLoop(void) {
    static uint32_t last_update_ms = 0;
    uint32_t now_ms = HAL_GetTick();
    
    // 每100ms更新一次
    if (now_ms - last_update_ms >= 100) {
        // 读取电池参数
        BMS_ReadBatteryParams(&g_bms);
        
        // 更新SOC
        SOC_UpdateHybrid(g_bms.battery.current,
                        g_bms.battery.pack_voltage / 5,
                        now_ms);
        
        // 执行保护检查
        bool fault = Protection_CheckAll(&g_bms);
        
        if (fault) {
            g_bms.state = BMS_STATE_FAULT;
        }
        
        // 执行充电状态机
        if (g_bms.state == BMS_STATE_CHARGING) {
            Charge_StateMachine(&g_bms);
        }
        
        // 执行放电状态机
        if (g_bms.state == BMS_STATE_DISCHARGING) {
            Discharge_StateMachine(&g_bms);
        }
        
        // 执行均衡状态机
        if (g_bms.state == BMS_STATE_BALANCING) {
            Balance_StateMachine(&g_bms);
        }
        
        last_update_ms = now_ms;
    }
    
    // 处理通信
    Comm_PeriodicReport(&g_bms);
}

/**
 * @brief  打印BMS状态
 */
void BMS_PrintStatus(void) {
    printf("\n═══════════════════════════════════════════\n");
    printf("           BMS 状态报告\n");
    printf("═══════════════════════════════════════════\n");
    
    // 系统状态
    const char* state_str[] = {
        "初始化", "空闲", "充电中", "放电中", "均衡中", "故障", "休眠"
    };
    printf("系统状态: %s\n", state_str[g_bms.state]);
    
    // 电池参数
    printf("\n电池参数:\n");
    printf("  单体电压:\n");
    for (int i = 0; i < 5; i++) {
        printf("    Cell%d: %d mV\n", i+1, g_bms.battery.cell_voltage[i]);
    }
    printf("  总电压: %d mV\n", g_bms.battery.pack_voltage);
    printf("  电流: %d mA %s\n",
           abs(g_bms.battery.current),
           g_bms.battery.current > 0 ? "(充电)" :
           g_bms.battery.current < 0 ? "(放电)" : "(静置)");
    printf("  温度1: %.1f°C\n", g_bms.battery.temperature[0] / 10.0f);
    printf("  温度2: %.1f°C\n", g_bms.battery.temperature[1] / 10.0f);
    printf("  SOC: %d%%\n", g_bms.battery.soc);
    printf("  SOH: %d%%\n", g_bms.battery.soh);
    printf("  剩余容量: %d mAh\n", g_bms.battery.capacity_mah);
    
    // 保护状态
    printf("\n保护状态:\n");
    printf("  过充保护: %s\n", g_bms.protection.overcharge ? "触发" : "正常");
    printf("  过放保护: %s\n", g_bms.protection.overdischarge ? "触发" : "正常");
    printf("  充电过流: %s\n", g_bms.protection.overcurrent_charge ? "触发" : "正常");
    printf("  放电过流: %s\n", g_bms.protection.overcurrent_discharge ? "触发" : "正常");
    printf("  过温保护: %s\n", g_bms.protection.overtemperature ? "触发" : "正常");
    printf("  低温保护: %s\n", g_bms.protection.undertemperature ? "触发" : "正常");
    printf("  短路保护: %s\n", g_bms.protection.short_circuit ? "触发" : "正常");
    printf("  单体不均衡: %s\n", g_bms.protection.cell_imbalance ? "是" : "否");
    
    // 运行时间
    printf("\n运行时间: %.1f 小时\n", g_bms.timestamp_ms / 3600000.0f);
    printf("循环次数: %d\n", g_bms.cycle_count);
    
    printf("═══════════════════════════════════════════\n\n");
}

/**
 * @brief  主函数
 */
int main(void) {
    // HAL库初始化
    HAL_Init();
    SystemClock_Config();
    
    // 初始化外设
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART1_UART_Init();
    
    // 初始化BMS
    BMS_Init();
    
    // 主循环
    while (1) {
        BMS_MainLoop();
        
        // 定期打印状态（每10秒）
        static uint32_t last_print_ms = 0;
        if (HAL_GetTick() - last_print_ms >= 10000) {
            BMS_PrintStatus();
            last_print_ms = HAL_GetTick();
        }
        
        HAL_Delay(10);
    }
}
```



## 实践建议

### 开发流程

**1. 硬件准备**：
- 开发板（STM32F103）
- 电池组（5串锂电池）
- AFE芯片（BQ76920）
- 电流传感器（ACS712）
- NTC热敏电阻
- MOSFET开关
- 调试工具（ST-Link）

**2. 软件开发步骤**：

```
开发顺序：

第一阶段：基础功能
1. 搭建硬件平台
2. 实现电压采集
3. 实现电流采集
4. 实现温度采集
5. 验证数据准确性

第二阶段：核心算法
1. 实现SOC计算
2. 实现充电控制
3. 实现放电控制
4. 测试充放电流程

第三阶段：保护功能
1. 实现各项保护
2. 测试保护触发
3. 验证保护可靠性
4. 优化保护参数

第四阶段：高级功能
1. 实现均衡管理
2. 实现通信接口
3. 添加数据记录
4. 优化用户体验

第五阶段：测试验证
1. 功能测试
2. 压力测试
3. 长期测试
4. 认证测试
```

### 调试技巧

**1. 电压测量校准**：

```c
/**
 * @brief  电压校准
 */
void BMS_CalibrateVoltage(void) {
    printf("电压校准程序\n");
    printf("请使用万用表测量实际电压\n\n");
    
    for (int i = 0; i < 5; i++) {
        uint16_t measured_mv = BMS_ReadCellVoltage(i);
        
        printf("单体%d:\n", i+1);
        printf("  测量值: %d mV\n", measured_mv);
        printf("  请输入万用表读数(mV): ");
        
        uint16_t actual_mv;
        scanf("%d", &actual_mv);
        
        // 计算校准系数
        float calibration_factor = (float)actual_mv / measured_mv;
        
        printf("  校准系数: %.4f\n\n", calibration_factor);
        
        // 保存校准系数到EEPROM
        BMS_SaveCalibration(i, calibration_factor);
    }
    
    printf("电压校准完成\n");
}
```

**2. 电流传感器校准**：

```c
/**
 * @brief  电流校准
 */
void BMS_CalibrateCurrent(void) {
    printf("电流校准程序\n");
    printf("请确保电池无负载\n");
    printf("按任意键开始零点校准...\n");
    getchar();
    
    // 零点校准
    int32_t zero_offset = 0;
    for (int i = 0; i < 100; i++) {
        zero_offset += BMS_ReadCurrentRaw();
        HAL_Delay(10);
    }
    zero_offset /= 100;
    
    printf("零点偏移: %d\n", zero_offset);
    
    // 满量程校准
    printf("\n请连接已知负载（例如1A）\n");
    printf("按任意键继续...\n");
    getchar();
    
    int32_t load_reading = 0;
    for (int i = 0; i < 100; i++) {
        load_reading += BMS_ReadCurrentRaw();
        HAL_Delay(10);
    }
    load_reading /= 100;
    
    printf("负载读数: %d\n", load_reading);
    printf("请输入实际电流(mA): ");
    
    int16_t actual_current;
    scanf("%d", &actual_current);
    
    // 计算校准系数
    float current_scale = (float)actual_current / (load_reading - zero_offset);
    
    printf("电流比例: %.4f mA/LSB\n", current_scale);
    
    // 保存校准参数
    BMS_SaveCurrentCalibration(zero_offset, current_scale);
    
    printf("电流校准完成\n");
}
```

### 常见问题

**问题1：SOC不准确**

```
原因分析：
1. 初始SOC估算不准
2. 电流测量误差
3. 累积误差
4. 温度影响

解决方案：
1. 使用OCV校准初始SOC
2. 定期使用OCV校准
3. 充满/放空时重新校准
4. 考虑温度补偿
5. 使用卡尔曼滤波
```

**问题2：保护误触发**

```
原因分析：
1. 阈值设置过严
2. 测量噪声
3. 瞬态干扰
4. 传感器故障

解决方案：
1. 调整保护阈值
2. 添加滤波算法
3. 增加延时判断
4. 多次采样确认
5. 添加滞回机制
```

**问题3：均衡效果差**

```
原因分析：
1. 均衡电流太小
2. 均衡时间不足
3. 电池老化不一致
4. 温度影响

解决方案：
1. 增大均衡电阻功率
2. 延长均衡时间
3. 考虑主动均衡
4. 定期维护
5. 更换老化电池
```

### 性能优化

**1. 降低功耗**：

```c
/**
 * @brief  低功耗模式
 */
void BMS_EnterLowPowerMode(void) {
    // 关闭不必要的外设
    HAL_ADC_Stop(&hadc1);
    
    // 降低采样频率
    // 从100ms改为1s
    
    // 关闭LED指示
    HAL_GPIO_WritePin(LED_GPIO, LED_PIN, GPIO_PIN_RESET);
    
    // 进入睡眠模式
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
}
```

**2. 提高响应速度**：

```c
/**
 * @brief  快速保护响应
 */
void BMS_FastProtection(void) {
    // 使用硬件比较器
    // 过流时立即断开MOSFET
    
    // 配置比较器
    HAL_COMP_Start(&hcomp1);
    
    // 配置中断
    HAL_NVIC_SetPriority(COMP_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(COMP_IRQn);
}

/**
 * @brief  比较器中断
 */
void COMP_IRQHandler(void) {
    // 立即断开MOSFET
    HAL_GPIO_WritePin(DISCHARGE_MOSFET_GPIO, 
                     DISCHARGE_MOSFET_PIN, 
                     GPIO_PIN_RESET);
    
    // 设置故障标志
    g_bms.protection.overcurrent_discharge = true;
    
    printf("过流保护触发！\n");
}
```

## 总结

### 关键要点

1. **系统架构**：
   - 模块化设计
   - 清晰的接口
   - 状态机管理
   - 分层架构

2. **核心算法**：
   - SOC计算（安时积分 + OCV校准）
   - 充电管理（CC-CV）
   - 放电控制（限流保护）
   - 均衡管理（被动/主动）

3. **安全保护**：
   - 多重保护机制
   - 快速响应
   - 可靠性设计
   - 故障诊断

4. **通信接口**：
   - 标准协议
   - 数据上报
   - 远程控制
   - 参数配置

### 进阶学习

完成本教程后，建议继续学习：

- **动态电源管理(DPM)技术**：学习更高级的功耗管理
- **超低功耗传感器节点设计**：应用BMS技术到IoT设备
- **电源完整性分析与优化**：深入理解电源系统设计
- **锂电池化学特性**：理解电池工作原理

### 参考资源

**标准和规范**：
- IEC 62133：锂电池安全标准
- UL 2054：电池安全认证
- GB/T 31485：电动汽车BMS标准

**芯片厂商资料**：
- TI BQ系列BMS芯片
- Analog Devices LTC系列
- Maxim MAX系列
- NXP BMS解决方案

**开源项目**：
- DieBieMS：开源BMS项目
- LibreSolar：太阳能BMS
- VESC BMS：电动车BMS

**在线资源**：
- Battery University：电池知识库
- TI BMS设计指南
- Analog Devices BMS教程

---

**作者**: 嵌入式知识平台内容团队  
**最后更新**: 2026-03-07  
**版本**: 1.0.0
