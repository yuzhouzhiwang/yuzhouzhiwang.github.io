---
# 基础信息
title: "传感器校准与误差补偿"
description: "深入讲解传感器校准原理、零点校准、灵敏度校准、温度补偿和非线性校正等技术，提供完整的校准算法实现"
slug: "sensor-calibration"

# 分类信息
domain: "01-hardware-layer"
module: "04-sensor-technology"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 传感器校准
  - 误差补偿
  - 精度优化
  - 零点校准
  - 温度补偿
  - 非线性校正
prerequisites:
  - "04-sensor-technology/beginner/01-temperature-humidity-sensor"
  - "04-sensor-technology/beginner/02-accelerometer-gyroscope"
related_contents:
  - "02-sensor-fusion"
  - "01-biosensor"
  - "03-light-pressure-sensor"

# 学习信息
estimated_time: 45
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
  - 传感器校准
  - 误差补偿
  - 灵敏度校准
  - 温度补偿
  - 非线性校正
  - 精度优化
cover_image: ""
---

# 传感器校准与误差补偿

## 概述

传感器校准是提高测量精度的关键技术。由于制造工艺、环境因素和使用条件的影响，传感器的实际输出往往与理想值存在偏差。通过系统的校准和误差补偿，可以显著提升传感器的测量精度和可靠性。本文将深入讲解传感器校准的核心原理和实用技术。

### 为什么需要传感器校准

1. **制造误差**：
   - 元件参数分散性
   - 装配误差
   - 批次差异
   - 典型误差：±5%~±10%

2. **环境影响**：
   - 温度漂移
   - 湿度影响
   - 气压变化
   - 电磁干扰

3. **老化效应**：
   - 元件老化
   - 机械磨损
   - 化学腐蚀
   - 长期漂移

4. **精度要求**：
   - 工业应用：±1%
   - 医疗设备：±0.5%
   - 科研仪器：±0.1%
   - 校准后可提升10-100倍精度

### 传感器误差类型

```
传感器误差分类：

┌─────────────────────────────────────────────┐
│           传感器误差类型                    │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ 系统误差     │  │ 随机误差     │        │
│  │ (可校准)     │  │ (可滤波)     │        │
│  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                 │
│    ┌────┴────┐       ┌────┴────┐           │
│    │         │       │         │           │
│  零点  灵敏度  │     噪声  漂移  │           │
│  误差  误差    │     误差  误差  │           │
│    │         │       │         │           │
│    └────┬────┘       └────┬────┘           │
│         │                 │                 │
│    ┌────▼─────────────────▼────┐           │
│    │      校准与补偿策略        │           │
│    └────────────────────────────┘           │
└─────────────────────────────────────────────┘

误差特性：
- 零点误差：输入为零时的输出偏差
- 灵敏度误差：输出与输入的比例偏差
- 非线性误差：输出与输入的非线性关系
- 温度漂移：温度变化引起的误差
- 迟滞误差：正反向测量的差异
```



## 第一部分：零点校准

### 零点校准原理

**基本概念**：

```
零点校准原理图：

理想传感器：
输入 = 0 → 输出 = 0

实际传感器：
输入 = 0 → 输出 = offset (零点偏移)

校准方法：
测量值_校准 = 测量值_原始 - offset

数学模型：
y_calibrated = y_measured - y_zero

其中：
- y_calibrated: 校准后的输出
- y_measured: 实际测量值
- y_zero: 零点偏移量

零点偏移来源：
1. 电路偏置电压
2. 传感器初始应力
3. 温度影响
4. 电源波动
```

### 零点校准实现

**单次零点校准**：

```c
/**
 * @file    zero_calibration.h
 * @brief   传感器零点校准
 */

#ifndef __ZERO_CALIBRATION_H
#define __ZERO_CALIBRATION_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief  零点校准结构
 */
typedef struct {
    float zero_offset;      // 零点偏移量
    bool calibrated;        // 校准标志
    uint32_t sample_count;  // 采样次数
} ZeroCalibration_t;

// 函数声明
void ZeroCalibration_Init(ZeroCalibration_t* cal);
bool ZeroCalibration_Start(ZeroCalibration_t* cal, 
                           float* samples, 
                           uint32_t count);
float ZeroCalibration_Apply(ZeroCalibration_t* cal, float raw_value);
void ZeroCalibration_Reset(ZeroCalibration_t* cal);

#endif /* __ZERO_CALIBRATION_H */
```

```c
/**
 * @file    zero_calibration.c
 * @brief   传感器零点校准实现
 */

#include "zero_calibration.h"

/**
 * @brief  初始化零点校准
 */
void ZeroCalibration_Init(ZeroCalibration_t* cal) {
    cal->zero_offset = 0.0f;
    cal->calibrated = false;
    cal->sample_count = 0;
}

/**
 * @brief  执行零点校准
 * @param  cal: 校准结构指针
 * @param  samples: 零点采样数据数组
 * @param  count: 采样数量
 * @return 校准是否成功
 */
bool ZeroCalibration_Start(ZeroCalibration_t* cal,
                           float* samples,
                           uint32_t count) {
    if (count == 0 || samples == NULL) {
        return false;
    }
    
    // 计算平均值作为零点偏移
    float sum = 0.0f;
    for (uint32_t i = 0; i < count; i++) {
        sum += samples[i];
    }
    
    cal->zero_offset = sum / count;
    cal->sample_count = count;
    cal->calibrated = true;
    
    return true;
}

/**
 * @brief  应用零点校准
 * @param  cal: 校准结构指针
 * @param  raw_value: 原始测量值
 * @return 校准后的值
 */
float ZeroCalibration_Apply(ZeroCalibration_t* cal, float raw_value) {
    if (!cal->calibrated) {
        return raw_value;  // 未校准，返回原始值
    }
    
    return raw_value - cal->zero_offset;
}

/**
 * @brief  重置校准
 */
void ZeroCalibration_Reset(ZeroCalibration_t* cal) {
    cal->zero_offset = 0.0f;
    cal->calibrated = false;
    cal->sample_count = 0;
}
```



### 多轴传感器零点校准

**加速度计/陀螺仪零点校准**：

```c
/**
 * @file    imu_zero_calibration.c
 * @brief   IMU传感器零点校准
 */

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief  IMU零点校准结构
 */
typedef struct {
    float accel_offset[3];  // 加速度计零点偏移 [x, y, z]
    float gyro_offset[3];   // 陀螺仪零点偏移 [x, y, z]
    bool calibrated;
} IMU_ZeroCalibration_t;

/**
 * @brief  IMU零点校准
 * @param  cal: 校准结构指针
 * @param  accel_samples: 加速度计采样数据 [N][3]
 * @param  gyro_samples: 陀螺仪采样数据 [N][3]
 * @param  count: 采样数量
 * @return 校准是否成功
 */
bool IMU_ZeroCalibration_Start(IMU_ZeroCalibration_t* cal,
                                float accel_samples[][3],
                                float gyro_samples[][3],
                                uint32_t count) {
    if (count == 0) {
        return false;
    }
    
    // 初始化累加器
    float accel_sum[3] = {0.0f, 0.0f, 0.0f};
    float gyro_sum[3] = {0.0f, 0.0f, 0.0f};
    
    // 累加所有采样
    for (uint32_t i = 0; i < count; i++) {
        for (int axis = 0; axis < 3; axis++) {
            accel_sum[axis] += accel_samples[i][axis];
            gyro_sum[axis] += gyro_samples[i][axis];
        }
    }
    
    // 计算平均值
    for (int axis = 0; axis < 3; axis++) {
        cal->accel_offset[axis] = accel_sum[axis] / count;
        cal->gyro_offset[axis] = gyro_sum[axis] / count;
    }
    
    // 加速度计Z轴应该是1g（重力），需要补偿
    cal->accel_offset[2] -= 1.0f;
    
    cal->calibrated = true;
    return true;
}

/**
 * @brief  应用IMU零点校准
 */
void IMU_ZeroCalibration_Apply(IMU_ZeroCalibration_t* cal,
                                float* accel_x, float* accel_y, float* accel_z,
                                float* gyro_x, float* gyro_y, float* gyro_z) {
    if (!cal->calibrated) {
        return;
    }
    
    // 应用加速度计校准
    if (accel_x) *accel_x -= cal->accel_offset[0];
    if (accel_y) *accel_y -= cal->accel_offset[1];
    if (accel_z) *accel_z -= cal->accel_offset[2];
    
    // 应用陀螺仪校准
    if (gyro_x) *gyro_x -= cal->gyro_offset[0];
    if (gyro_y) *gyro_y -= cal->gyro_offset[1];
    if (gyro_z) *gyro_z -= cal->gyro_offset[2];
}
```



## 第二部分：灵敏度校准

### 灵敏度校准原理

**基本概念**：

```
灵敏度校准原理图：

理想传感器：
输出 = 灵敏度_理想 × 输入

实际传感器：
输出 = 灵敏度_实际 × 输入
灵敏度_实际 ≠ 灵敏度_理想

校准方法：
输入_校准 = 输出_测量 / 灵敏度_实际

两点校准法：
已知两个标准输入值 x1, x2
测量对应输出值 y1, y2

灵敏度 = (y2 - y1) / (x2 - x1)
零点偏移 = y1 - 灵敏度 × x1

校准公式：
x = (y - offset) / sensitivity

示例：
标准点1: 0°C → 输出 512
标准点2: 100°C → 输出 3584
灵敏度 = (3584 - 512) / (100 - 0) = 30.72 LSB/°C
零点偏移 = 512 - 30.72 × 0 = 512
温度 = (ADC值 - 512) / 30.72
```

### 灵敏度校准实现

**两点校准法**：

```c
/**
 * @file    sensitivity_calibration.h
 * @brief   传感器灵敏度校准
 */

#ifndef __SENSITIVITY_CALIBRATION_H
#define __SENSITIVITY_CALIBRATION_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief  灵敏度校准结构
 */
typedef struct {
    float sensitivity;      // 灵敏度（斜率）
    float offset;           // 零点偏移（截距）
    bool calibrated;        // 校准标志
} SensitivityCalibration_t;

// 函数声明
void SensitivityCalibration_Init(SensitivityCalibration_t* cal);
bool SensitivityCalibration_TwoPoint(SensitivityCalibration_t* cal,
                                     float x1, float y1,
                                     float x2, float y2);
float SensitivityCalibration_Apply(SensitivityCalibration_t* cal, 
                                   float raw_value);
float SensitivityCalibration_Reverse(SensitivityCalibration_t* cal,
                                     float calibrated_value);

#endif /* __SENSITIVITY_CALIBRATION_H */
```

```c
/**
 * @file    sensitivity_calibration.c
 * @brief   传感器灵敏度校准实现
 */

#include "sensitivity_calibration.h"

/**
 * @brief  初始化灵敏度校准
 */
void SensitivityCalibration_Init(SensitivityCalibration_t* cal) {
    cal->sensitivity = 1.0f;
    cal->offset = 0.0f;
    cal->calibrated = false;
}

/**
 * @brief  两点校准法
 * @param  cal: 校准结构指针
 * @param  x1: 第一个标准输入值
 * @param  y1: 第一个测量输出值
 * @param  x2: 第二个标准输入值
 * @param  y2: 第二个测量输出值
 * @return 校准是否成功
 * 
 * @note   校准公式：
 *         sensitivity = (y2 - y1) / (x2 - x1)
 *         offset = y1 - sensitivity * x1
 *         x = (y - offset) / sensitivity
 */
bool SensitivityCalibration_TwoPoint(SensitivityCalibration_t* cal,
                                     float x1, float y1,
                                     float x2, float y2) {
    // 检查输入是否有效
    if (x1 == x2) {
        return false;  // 两点不能相同
    }
    
    // 计算灵敏度（斜率）
    cal->sensitivity = (y2 - y1) / (x2 - x1);
    
    // 计算零点偏移（截距）
    cal->offset = y1 - cal->sensitivity * x1;
    
    cal->calibrated = true;
    return true;
}

/**
 * @brief  应用灵敏度校准（输出 → 输入）
 * @param  cal: 校准结构指针
 * @param  raw_value: 原始测量值（传感器输出）
 * @return 校准后的值（实际输入）
 */
float SensitivityCalibration_Apply(SensitivityCalibration_t* cal,
                                   float raw_value) {
    if (!cal->calibrated) {
        return raw_value;
    }
    
    // x = (y - offset) / sensitivity
    return (raw_value - cal->offset) / cal->sensitivity;
}

/**
 * @brief  反向计算（输入 → 输出）
 * @param  cal: 校准结构指针
 * @param  calibrated_value: 校准后的值（实际输入）
 * @return 预期的传感器输出
 */
float SensitivityCalibration_Reverse(SensitivityCalibration_t* cal,
                                     float calibrated_value) {
    if (!cal->calibrated) {
        return calibrated_value;
    }
    
    // y = sensitivity * x + offset
    return cal->sensitivity * calibrated_value + cal->offset;
}
```



### 多点校准法

**用于非线性传感器**：

```c
/**
 * @file    multipoint_calibration.c
 * @brief   多点校准实现
 */

#include <stdint.h>
#include <stdbool.h>

#define MAX_CALIBRATION_POINTS  10

/**
 * @brief  多点校准结构
 */
typedef struct {
    float x_points[MAX_CALIBRATION_POINTS];  // 标准输入值
    float y_points[MAX_CALIBRATION_POINTS];  // 测量输出值
    uint32_t point_count;                    // 校准点数量
    bool calibrated;
} MultiPointCalibration_t;

/**
 * @brief  添加校准点
 */
bool MultiPointCalibration_AddPoint(MultiPointCalibration_t* cal,
                                    float x, float y) {
    if (cal->point_count >= MAX_CALIBRATION_POINTS) {
        return false;
    }
    
    cal->x_points[cal->point_count] = x;
    cal->y_points[cal->point_count] = y;
    cal->point_count++;
    
    if (cal->point_count >= 2) {
        cal->calibrated = true;
    }
    
    return true;
}

/**
 * @brief  线性插值校准
 * @param  cal: 校准结构指针
 * @param  raw_value: 原始测量值
 * @return 校准后的值
 */
float MultiPointCalibration_Apply(MultiPointCalibration_t* cal,
                                  float raw_value) {
    if (!cal->calibrated || cal->point_count < 2) {
        return raw_value;
    }
    
    // 查找插值区间
    for (uint32_t i = 0; i < cal->point_count - 1; i++) {
        float y1 = cal->y_points[i];
        float y2 = cal->y_points[i + 1];
        
        // 检查raw_value是否在[y1, y2]区间内
        if ((raw_value >= y1 && raw_value <= y2) ||
            (raw_value >= y2 && raw_value <= y1)) {
            
            float x1 = cal->x_points[i];
            float x2 = cal->x_points[i + 1];
            
            // 线性插值：x = x1 + (x2-x1) * (y-y1) / (y2-y1)
            float x = x1 + (x2 - x1) * (raw_value - y1) / (y2 - y1);
            return x;
        }
    }
    
    // 超出校准范围，使用最近的两点外推
    if (raw_value < cal->y_points[0]) {
        // 使用前两点外推
        float x1 = cal->x_points[0];
        float x2 = cal->x_points[1];
        float y1 = cal->y_points[0];
        float y2 = cal->y_points[1];
        return x1 + (x2 - x1) * (raw_value - y1) / (y2 - y1);
    } else {
        // 使用后两点外推
        uint32_t n = cal->point_count;
        float x1 = cal->x_points[n - 2];
        float x2 = cal->x_points[n - 1];
        float y1 = cal->y_points[n - 2];
        float y2 = cal->y_points[n - 1];
        return x1 + (x2 - x1) * (raw_value - y1) / (y2 - y1);
    }
}
```



## 第三部分：温度补偿

### 温度补偿原理

**温度对传感器的影响**：

```
温度补偿原理图：

温度影响：
┌─────────────────────────────────────┐
│  传感器输出随温度变化               │
│                                     │
│  输出                               │
│   ↑                                 │
│   │    ╱                            │
│   │   ╱  (温度升高，输出增大)       │
│   │  ╱                              │
│   │ ╱                               │
│   │╱                                │
│   └────────────→ 温度               │
└─────────────────────────────────────┘

补偿模型：
1. 线性温度补偿：
   y_comp = y_raw - k_temp × (T - T_ref)
   
2. 二次温度补偿：
   y_comp = y_raw - k1 × (T - T_ref) - k2 × (T - T_ref)²

3. 查表法：
   建立温度-误差对照表
   通过插值获得补偿值

参数说明：
- y_comp: 补偿后的输出
- y_raw: 原始输出
- k_temp: 温度系数
- T: 当前温度
- T_ref: 参考温度（通常25°C）
- k1, k2: 一次、二次温度系数
```

### 温度补偿实现

**线性温度补偿**：

```c
/**
 * @file    temperature_compensation.h
 * @brief   温度补偿
 */

#ifndef __TEMPERATURE_COMPENSATION_H
#define __TEMPERATURE_COMPENSATION_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief  线性温度补偿结构
 */
typedef struct {
    float temp_coeff;       // 温度系数
    float ref_temp;         // 参考温度（°C）
    bool calibrated;
} TempCompensation_Linear_t;

/**
 * @brief  二次温度补偿结构
 */
typedef struct {
    float temp_coeff1;      // 一次温度系数
    float temp_coeff2;      // 二次温度系数
    float ref_temp;         // 参考温度（°C）
    bool calibrated;
} TempCompensation_Quadratic_t;

// 函数声明
void TempCompensation_Linear_Init(TempCompensation_Linear_t* comp,
                                  float temp_coeff, float ref_temp);
float TempCompensation_Linear_Apply(TempCompensation_Linear_t* comp,
                                    float raw_value, float current_temp);

void TempCompensation_Quadratic_Init(TempCompensation_Quadratic_t* comp,
                                     float coeff1, float coeff2, float ref_temp);
float TempCompensation_Quadratic_Apply(TempCompensation_Quadratic_t* comp,
                                       float raw_value, float current_temp);

#endif /* __TEMPERATURE_COMPENSATION_H */
```

```c
/**
 * @file    temperature_compensation.c
 * @brief   温度补偿实现
 */

#include "temperature_compensation.h"

/**
 * @brief  初始化线性温度补偿
 * @param  comp: 补偿结构指针
 * @param  temp_coeff: 温度系数（单位/°C）
 * @param  ref_temp: 参考温度（°C）
 */
void TempCompensation_Linear_Init(TempCompensation_Linear_t* comp,
                                  float temp_coeff, float ref_temp) {
    comp->temp_coeff = temp_coeff;
    comp->ref_temp = ref_temp;
    comp->calibrated = true;
}

/**
 * @brief  应用线性温度补偿
 * @param  comp: 补偿结构指针
 * @param  raw_value: 原始测量值
 * @param  current_temp: 当前温度（°C）
 * @return 补偿后的值
 */
float TempCompensation_Linear_Apply(TempCompensation_Linear_t* comp,
                                    float raw_value, float current_temp) {
    if (!comp->calibrated) {
        return raw_value;
    }
    
    // y_comp = y_raw - k_temp × (T - T_ref)
    float temp_error = comp->temp_coeff * (current_temp - comp->ref_temp);
    return raw_value - temp_error;
}

/**
 * @brief  初始化二次温度补偿
 * @param  comp: 补偿结构指针
 * @param  coeff1: 一次温度系数
 * @param  coeff2: 二次温度系数
 * @param  ref_temp: 参考温度（°C）
 */
void TempCompensation_Quadratic_Init(TempCompensation_Quadratic_t* comp,
                                     float coeff1, float coeff2, float ref_temp) {
    comp->temp_coeff1 = coeff1;
    comp->temp_coeff2 = coeff2;
    comp->ref_temp = ref_temp;
    comp->calibrated = true;
}

/**
 * @brief  应用二次温度补偿
 * @param  comp: 补偿结构指针
 * @param  raw_value: 原始测量值
 * @param  current_temp: 当前温度（°C）
 * @return 补偿后的值
 */
float TempCompensation_Quadratic_Apply(TempCompensation_Quadratic_t* comp,
                                       float raw_value, float current_temp) {
    if (!comp->calibrated) {
        return raw_value;
    }
    
    // y_comp = y_raw - k1×(T-T_ref) - k2×(T-T_ref)²
    float delta_temp = current_temp - comp->ref_temp;
    float temp_error = comp->temp_coeff1 * delta_temp +
                       comp->temp_coeff2 * delta_temp * delta_temp;
    return raw_value - temp_error;
}
```



### 查表法温度补偿

```c
/**
 * @file    temperature_compensation_lut.c
 * @brief   查表法温度补偿
 */

#include <stdint.h>
#include <stdbool.h>

#define MAX_TEMP_POINTS  20

/**
 * @brief  查表法温度补偿结构
 */
typedef struct {
    float temp_points[MAX_TEMP_POINTS];     // 温度点（°C）
    float error_points[MAX_TEMP_POINTS];    // 对应误差
    uint32_t point_count;                   // 数据点数量
    bool calibrated;
} TempCompensation_LUT_t;

/**
 * @brief  添加温度补偿点
 */
bool TempCompensation_LUT_AddPoint(TempCompensation_LUT_t* comp,
                                   float temperature, float error) {
    if (comp->point_count >= MAX_TEMP_POINTS) {
        return false;
    }
    
    comp->temp_points[comp->point_count] = temperature;
    comp->error_points[comp->point_count] = error;
    comp->point_count++;
    
    if (comp->point_count >= 2) {
        comp->calibrated = true;
    }
    
    return true;
}

/**
 * @brief  应用查表法温度补偿
 * @param  comp: 补偿结构指针
 * @param  raw_value: 原始测量值
 * @param  current_temp: 当前温度（°C）
 * @return 补偿后的值
 */
float TempCompensation_LUT_Apply(TempCompensation_LUT_t* comp,
                                 float raw_value, float current_temp) {
    if (!comp->calibrated || comp->point_count < 2) {
        return raw_value;
    }
    
    // 查找插值区间
    for (uint32_t i = 0; i < comp->point_count - 1; i++) {
        float t1 = comp->temp_points[i];
        float t2 = comp->temp_points[i + 1];
        
        // 检查current_temp是否在[t1, t2]区间内
        if ((current_temp >= t1 && current_temp <= t2) ||
            (current_temp >= t2 && current_temp <= t1)) {
            
            float e1 = comp->error_points[i];
            float e2 = comp->error_points[i + 1];
            
            // 线性插值计算误差
            float error = e1 + (e2 - e1) * (current_temp - t1) / (t2 - t1);
            return raw_value - error;
        }
    }
    
    // 超出范围，使用最近点
    if (current_temp < comp->temp_points[0]) {
        return raw_value - comp->error_points[0];
    } else {
        return raw_value - comp->error_points[comp->point_count - 1];
    }
}
```



## 第四部分：非线性校正

### 非线性校正原理

**非线性特性**：

```
非线性校正原理图：

理想线性传感器：
输出 ∝ 输入（直线关系）

实际非线性传感器：
输出 = f(输入)（曲线关系）

┌─────────────────────────────────────┐
│  输出                               │
│   ↑                                 │
│   │        实际曲线                 │
│   │       ╱                         │
│   │      ╱                          │
│   │     ╱  理想直线                 │
│   │    ╱  ╱                         │
│   │   ╱  ╱                          │
│   │  ╱  ╱                           │
│   │ ╱  ╱                            │
│   │╱  ╱                             │
│   └────────────→ 输入               │
└─────────────────────────────────────┘

校正方法：
1. 多项式拟合：
   y = a0 + a1×x + a2×x² + a3×x³ + ...
   
2. 分段线性化：
   将曲线分成多段，每段用直线近似
   
3. 查表法：
   建立输入-输出对照表

非线性度计算：
非线性度 = (最大偏差 / 满量程) × 100%
```

### 多项式校正实现

```c
/**
 * @file    nonlinear_correction.h
 * @brief   非线性校正
 */

#ifndef __NONLINEAR_CORRECTION_H
#define __NONLINEAR_CORRECTION_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_POLYNOMIAL_ORDER  5

/**
 * @brief  多项式校正结构
 */
typedef struct {
    float coefficients[MAX_POLYNOMIAL_ORDER + 1];  // 多项式系数
    uint32_t order;                                // 多项式阶数
    bool calibrated;
} PolynomialCorrection_t;

// 函数声明
void PolynomialCorrection_Init(PolynomialCorrection_t* corr,
                               float* coeffs, uint32_t order);
float PolynomialCorrection_Apply(PolynomialCorrection_t* corr,
                                 float raw_value);

#endif /* __NONLINEAR_CORRECTION_H */
```

```c
/**
 * @file    nonlinear_correction.c
 * @brief   非线性校正实现
 */

#include "nonlinear_correction.h"
#include <math.h>

/**
 * @brief  初始化多项式校正
 * @param  corr: 校正结构指针
 * @param  coeffs: 多项式系数数组 [a0, a1, a2, ...]
 * @param  order: 多项式阶数
 * 
 * @note   多项式形式：y = a0 + a1×x + a2×x² + a3×x³ + ...
 */
void PolynomialCorrection_Init(PolynomialCorrection_t* corr,
                               float* coeffs, uint32_t order) {
    if (order > MAX_POLYNOMIAL_ORDER) {
        order = MAX_POLYNOMIAL_ORDER;
    }
    
    corr->order = order;
    
    for (uint32_t i = 0; i <= order; i++) {
        corr->coefficients[i] = coeffs[i];
    }
    
    corr->calibrated = true;
}

/**
 * @brief  应用多项式校正
 * @param  corr: 校正结构指针
 * @param  raw_value: 原始测量值
 * @return 校正后的值
 */
float PolynomialCorrection_Apply(PolynomialCorrection_t* corr,
                                 float raw_value) {
    if (!corr->calibrated) {
        return raw_value;
    }
    
    // 使用霍纳法则计算多项式
    // y = a0 + x(a1 + x(a2 + x(a3 + ...)))
    float result = corr->coefficients[corr->order];
    
    for (int i = corr->order - 1; i >= 0; i--) {
        result = result * raw_value + corr->coefficients[i];
    }
    
    return result;
}
```

### 分段线性化校正

```c
/**
 * @file    piecewise_linear_correction.c
 * @brief   分段线性化校正
 */

#include <stdint.h>
#include <stdbool.h>

#define MAX_SEGMENTS  10

/**
 * @brief  分段线性化校正结构
 */
typedef struct {
    float x_points[MAX_SEGMENTS + 1];  // 分段点（输入）
    float y_points[MAX_SEGMENTS + 1];  // 分段点（输出）
    uint32_t segment_count;            // 分段数量
    bool calibrated;
} PiecewiseLinearCorrection_t;

/**
 * @brief  添加分段点
 */
bool PiecewiseLinearCorrection_AddPoint(PiecewiseLinearCorrection_t* corr,
                                        float x, float y) {
    if (corr->segment_count >= MAX_SEGMENTS) {
        return false;
    }
    
    corr->x_points[corr->segment_count] = x;
    corr->y_points[corr->segment_count] = y;
    corr->segment_count++;
    
    if (corr->segment_count >= 2) {
        corr->calibrated = true;
    }
    
    return true;
}

/**
 * @brief  应用分段线性化校正
 */
float PiecewiseLinearCorrection_Apply(PiecewiseLinearCorrection_t* corr,
                                      float raw_value) {
    if (!corr->calibrated || corr->segment_count < 2) {
        return raw_value;
    }
    
    // 查找所在分段
    for (uint32_t i = 0; i < corr->segment_count - 1; i++) {
        float x1 = corr->x_points[i];
        float x2 = corr->x_points[i + 1];
        
        if ((raw_value >= x1 && raw_value <= x2) ||
            (raw_value >= x2 && raw_value <= x1)) {
            
            float y1 = corr->y_points[i];
            float y2 = corr->y_points[i + 1];
            
            // 线性插值
            float y = y1 + (y2 - y1) * (raw_value - x1) / (x2 - x1);
            return y;
        }
    }
    
    // 超出范围，使用最近段外推
    if (raw_value < corr->x_points[0]) {
        float x1 = corr->x_points[0];
        float x2 = corr->x_points[1];
        float y1 = corr->y_points[0];
        float y2 = corr->y_points[1];
        return y1 + (y2 - y1) * (raw_value - x1) / (x2 - x1);
    } else {
        uint32_t n = corr->segment_count;
        float x1 = corr->x_points[n - 2];
        float x2 = corr->x_points[n - 1];
        float y1 = corr->y_points[n - 2];
        float y2 = corr->y_points[n - 1];
        return y1 + (y2 - y1) * (raw_value - x1) / (x2 - x1);
    }
}
```



## 第五部分：综合校准系统

### 完整校准流程

**集成所有校准技术**：

```c
/**
 * @file    sensor_calibration_system.h
 * @brief   传感器综合校准系统
 */

#ifndef __SENSOR_CALIBRATION_SYSTEM_H
#define __SENSOR_CALIBRATION_SYSTEM_H

#include <stdint.h>
#include <stdbool.h>
#include "zero_calibration.h"
#include "sensitivity_calibration.h"
#include "temperature_compensation.h"
#include "nonlinear_correction.h"

/**
 * @brief  综合校准系统结构
 */
typedef struct {
    ZeroCalibration_t zero_cal;                     // 零点校准
    SensitivityCalibration_t sensitivity_cal;       // 灵敏度校准
    TempCompensation_Linear_t temp_comp;            // 温度补偿
    PolynomialCorrection_t nonlinear_corr;          // 非线性校正
    bool enabled[4];                                // 各模块使能标志
} SensorCalibrationSystem_t;

// 校准模块索引
typedef enum {
    CAL_MODULE_ZERO = 0,
    CAL_MODULE_SENSITIVITY = 1,
    CAL_MODULE_TEMP_COMP = 2,
    CAL_MODULE_NONLINEAR = 3
} CalibrationModule_e;

// 函数声明
void SensorCalibrationSystem_Init(SensorCalibrationSystem_t* sys);
void SensorCalibrationSystem_EnableModule(SensorCalibrationSystem_t* sys,
                                          CalibrationModule_e module,
                                          bool enable);
float SensorCalibrationSystem_Process(SensorCalibrationSystem_t* sys,
                                      float raw_value,
                                      float temperature);

#endif /* __SENSOR_CALIBRATION_SYSTEM_H */
```

```c
/**
 * @file    sensor_calibration_system.c
 * @brief   传感器综合校准系统实现
 */

#include "sensor_calibration_system.h"

/**
 * @brief  初始化综合校准系统
 */
void SensorCalibrationSystem_Init(SensorCalibrationSystem_t* sys) {
    ZeroCalibration_Init(&sys->zero_cal);
    SensitivityCalibration_Init(&sys->sensitivity_cal);
    TempCompensation_Linear_Init(&sys->temp_comp, 0.0f, 25.0f);
    
    // 默认禁用所有模块
    for (int i = 0; i < 4; i++) {
        sys->enabled[i] = false;
    }
}

/**
 * @brief  使能/禁用校准模块
 */
void SensorCalibrationSystem_EnableModule(SensorCalibrationSystem_t* sys,
                                          CalibrationModule_e module,
                                          bool enable) {
    if (module < 4) {
        sys->enabled[module] = enable;
    }
}

/**
 * @brief  处理传感器数据（应用所有校准）
 * @param  sys: 校准系统指针
 * @param  raw_value: 原始测量值
 * @param  temperature: 当前温度（°C）
 * @return 校准后的值
 * 
 * @note   校准顺序：
 *         1. 零点校准
 *         2. 灵敏度校准
 *         3. 温度补偿
 *         4. 非线性校正
 */
float SensorCalibrationSystem_Process(SensorCalibrationSystem_t* sys,
                                      float raw_value,
                                      float temperature) {
    float value = raw_value;
    
    // 步骤1：零点校准
    if (sys->enabled[CAL_MODULE_ZERO]) {
        value = ZeroCalibration_Apply(&sys->zero_cal, value);
    }
    
    // 步骤2：灵敏度校准
    if (sys->enabled[CAL_MODULE_SENSITIVITY]) {
        value = SensitivityCalibration_Apply(&sys->sensitivity_cal, value);
    }
    
    // 步骤3：温度补偿
    if (sys->enabled[CAL_MODULE_TEMP_COMP]) {
        value = TempCompensation_Linear_Apply(&sys->temp_comp, value, temperature);
    }
    
    // 步骤4：非线性校正
    if (sys->enabled[CAL_MODULE_NONLINEAR]) {
        value = PolynomialCorrection_Apply(&sys->nonlinear_corr, value);
    }
    
    return value;
}
```



## 第六部分：实践应用

### 应用示例1：温度传感器校准

```c
/**
 * @file    example_temperature_calibration.c
 * @brief   温度传感器校准示例
 */

#include "stm32f1xx_hal.h"
#include "sensor_calibration_system.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;

/**
 * @brief  温度传感器校准示例
 */
void example_temperature_calibration(void) {
    SensorCalibrationSystem_t cal_system;
    SensorCalibrationSystem_Init(&cal_system);
    
    printf("温度传感器校准程序\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 步骤1：零点校准（0°C冰水混合物）
    printf("步骤1：零点校准\n");
    printf("请将传感器放入冰水混合物中，按任意键继续...\n");
    getchar();
    
    float zero_samples[100];
    for (int i = 0; i < 100; i++) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        zero_samples[i] = HAL_ADC_GetValue(&hadc1);
        HAL_Delay(10);
    }
    
    ZeroCalibration_Start(&cal_system.zero_cal, zero_samples, 100);
    SensorCalibrationSystem_EnableModule(&cal_system, CAL_MODULE_ZERO, true);
    printf("零点校准完成！零点偏移 = %.2f\n\n", cal_system.zero_cal.zero_offset);
    
    // 步骤2：灵敏度校准（100°C沸水）
    printf("步骤2：灵敏度校准\n");
    printf("请将传感器放入沸水中，按任意键继续...\n");
    getchar();
    
    float boiling_samples[100];
    for (int i = 0; i < 100; i++) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        boiling_samples[i] = HAL_ADC_GetValue(&hadc1);
        HAL_Delay(10);
    }
    
    // 计算平均值
    float zero_avg = 0.0f, boiling_avg = 0.0f;
    for (int i = 0; i < 100; i++) {
        zero_avg += zero_samples[i];
        boiling_avg += boiling_samples[i];
    }
    zero_avg /= 100.0f;
    boiling_avg /= 100.0f;
    
    // 两点校准：0°C和100°C
    SensitivityCalibration_TwoPoint(&cal_system.sensitivity_cal,
                                    0.0f, zero_avg,
                                    100.0f, boiling_avg);
    SensorCalibrationSystem_EnableModule(&cal_system, CAL_MODULE_SENSITIVITY, true);
    
    printf("灵敏度校准完成！\n");
    printf("  灵敏度 = %.4f\n", cal_system.sensitivity_cal.sensitivity);
    printf("  偏移量 = %.2f\n\n", cal_system.sensitivity_cal.offset);
    
    // 步骤3：实时测量
    printf("步骤3：实时温度测量\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        float raw_adc = HAL_ADC_GetValue(&hadc1);
        
        // 应用校准
        float temperature = SensorCalibrationSystem_Process(&cal_system,
                                                            raw_adc,
                                                            25.0f);
        
        printf("ADC原始值: %.0f → 温度: %.2f°C\n", raw_adc, temperature);
        
        HAL_Delay(1000);
    }
}
```

### 应用示例2：加速度计校准

```c
/**
 * @file    example_accelerometer_calibration.c
 * @brief   加速度计校准示例
 */

#include "stm32f1xx_hal.h"
#include "mpu6050.h"
#include "sensor_calibration_system.h"
#include <stdio.h>

extern I2C_HandleTypeDef hi2c1;

/**
 * @brief  加速度计六面校准法
 */
void example_accelerometer_calibration(void) {
    MPU6050_Config mpu_config = {
        .hi2c = &hi2c1,
        .address = MPU6050_ADDR,
        .gyro_fs = MPU6050_GYRO_FS_250,
        .accel_fs = MPU6050_ACCEL_FS_2
    };
    
    if (!MPU6050_Init(&mpu_config)) {
        printf("MPU6050初始化失败！\n");
        return;
    }
    
    printf("加速度计六面校准法\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 六个面的校准数据
    float accel_data[6][3];  // [面][轴]
    const char* face_names[] = {
        "X轴正向（向右）",
        "X轴负向（向左）",
        "Y轴正向（向前）",
        "Y轴负向（向后）",
        "Z轴正向（向上）",
        "Z轴负向（向下）"
    };
    
    // 采集六个面的数据
    for (int face = 0; face < 6; face++) {
        printf("请将传感器%s放置，按任意键继续...\n", face_names[face]);
        getchar();
        
        float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
        MPU6050_Data mpu_data;
        
        // 采集100个样本
        for (int i = 0; i < 100; i++) {
            if (MPU6050_ReadData(&mpu_config, &mpu_data)) {
                sum_x += mpu_data.accel_x;
                sum_y += mpu_data.accel_y;
                sum_z += mpu_data.accel_z;
            }
            HAL_Delay(10);
        }
        
        accel_data[face][0] = sum_x / 100.0f;
        accel_data[face][1] = sum_y / 100.0f;
        accel_data[face][2] = sum_z / 100.0f;
        
        printf("采集完成：X=%.3f, Y=%.3f, Z=%.3f\n\n",
               accel_data[face][0],
               accel_data[face][1],
               accel_data[face][2]);
    }
    
    // 计算校准参数
    float offset[3], scale[3];
    
    for (int axis = 0; axis < 3; axis++) {
        int pos_face = axis * 2;      // 正向面
        int neg_face = axis * 2 + 1;  // 负向面
        
        float max_val = accel_data[pos_face][axis];
        float min_val = accel_data[neg_face][axis];
        
        // 零点偏移 = (最大值 + 最小值) / 2
        offset[axis] = (max_val + min_val) / 2.0f;
        
        // 灵敏度 = (最大值 - 最小值) / 2
        // 理想值应该是2g（±1g）
        scale[axis] = 2.0f / (max_val - min_val);
    }
    
    printf("校准参数计算完成：\n");
    printf("X轴：偏移=%.4f, 缩放=%.4f\n", offset[0], scale[0]);
    printf("Y轴：偏移=%.4f, 缩放=%.4f\n", offset[1], scale[1]);
    printf("Z轴：偏移=%.4f, 缩放=%.4f\n\n", offset[2], scale[2]);
    
    // 实时测量并应用校准
    printf("实时加速度测量（已校准）\n");
    printf("═══════════════════════════════════════\n\n");
    
    MPU6050_Data mpu_data;
    while (1) {
        if (MPU6050_ReadData(&mpu_config, &mpu_data)) {
            // 应用校准
            float accel_x = (mpu_data.accel_x - offset[0]) * scale[0];
            float accel_y = (mpu_data.accel_y - offset[1]) * scale[1];
            float accel_z = (mpu_data.accel_z - offset[2]) * scale[2];
            
            printf("加速度: X=%.3fg, Y=%.3fg, Z=%.3fg\n",
                   accel_x, accel_y, accel_z);
        }
        
        HAL_Delay(100);
    }
}
```



### 应用示例3：压力传感器非线性校正

```c
/**
 * @file    example_pressure_calibration.c
 * @brief   压力传感器非线性校正示例
 */

#include "stm32f1xx_hal.h"
#include "sensor_calibration_system.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;

/**
 * @brief  压力传感器非线性校正
 */
void example_pressure_calibration(void) {
    // 创建多点校准系统
    MultiPointCalibration_t pressure_cal;
    pressure_cal.point_count = 0;
    pressure_cal.calibrated = false;
    
    printf("压力传感器非线性校正\n");
    printf("═══════════════════════════════════════\n\n");
    
    // 标准压力点（kPa）
    float standard_pressures[] = {0.0f, 20.0f, 40.0f, 60.0f, 80.0f, 100.0f};
    int num_points = sizeof(standard_pressures) / sizeof(float);
    
    // 采集校准数据
    for (int i = 0; i < num_points; i++) {
        printf("请施加标准压力 %.1f kPa，按任意键继续...\n",
               standard_pressures[i]);
        getchar();
        
        // 采集100个样本
        float sum = 0.0f;
        for (int j = 0; j < 100; j++) {
            HAL_ADC_Start(&hadc1);
            HAL_ADC_PollForConversion(&hadc1, 100);
            sum += HAL_ADC_GetValue(&hadc1);
            HAL_Delay(10);
        }
        
        float avg_adc = sum / 100.0f;
        
        // 添加校准点
        MultiPointCalibration_AddPoint(&pressure_cal,
                                       standard_pressures[i],
                                       avg_adc);
        
        printf("ADC值: %.2f\n\n", avg_adc);
    }
    
    printf("校准完成！共%d个校准点\n\n", pressure_cal.point_count);
    
    // 实时测量
    printf("实时压力测量（已校正）\n");
    printf("═══════════════════════════════════════\n\n");
    
    while (1) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        float raw_adc = HAL_ADC_GetValue(&hadc1);
        
        // 应用非线性校正
        float pressure = MultiPointCalibration_Apply(&pressure_cal, raw_adc);
        
        printf("ADC: %.0f → 压力: %.2f kPa\n", raw_adc, pressure);
        
        HAL_Delay(500);
    }
}
```

## 第七部分：校准最佳实践

### 校准流程建议

```
完整校准流程：

1. 准备阶段
   ├─ 准备标准参考源
   ├─ 预热传感器（15-30分钟）
   ├─ 稳定环境条件
   └─ 准备记录工具

2. 零点校准
   ├─ 确保零输入条件
   ├─ 采集足够样本（≥100）
   ├─ 计算平均值
   └─ 验证稳定性

3. 灵敏度校准
   ├─ 选择校准点（至少2点）
   ├─ 使用标准参考源
   ├─ 采集多次测量
   └─ 计算校准系数

4. 温度补偿
   ├─ 在不同温度下测量
   ├─ 建立温度-误差关系
   ├─ 选择补偿模型
   └─ 验证补偿效果

5. 非线性校正
   ├─ 多点测量（≥5点）
   ├─ 选择校正方法
   ├─ 计算校正参数
   └─ 验证校正精度

6. 验证阶段
   ├─ 使用独立测试点
   ├─ 计算校准后误差
   ├─ 评估精度提升
   └─ 记录校准参数

7. 存储与应用
   ├─ 保存校准参数
   ├─ 实现自动加载
   ├─ 定期重新校准
   └─ 监控校准有效性
```

### 校准注意事项

**1. 采样要求**：
```c
// 采样数量建议
#define MIN_SAMPLES_ZERO_CAL      100   // 零点校准最少样本
#define MIN_SAMPLES_SENSITIVITY   50    // 灵敏度校准最少样本
#define MIN_SAMPLES_TEMP_COMP     20    // 温度补偿最少样本

// 采样间隔
#define SAMPLE_INTERVAL_MS        10    // 10ms采样间隔
#define SETTLING_TIME_MS          1000  // 1秒稳定时间
```

**2. 环境控制**：
- 温度稳定：±0.5°C
- 湿度控制：40-60% RH
- 避免振动和电磁干扰
- 充分预热时间

**3. 参考标准**：
- 使用高精度参考源
- 参考源精度应高于传感器10倍
- 定期校准参考源
- 可追溯到国家标准

**4. 数据处理**：
```c
/**
 * @brief  异常值检测与剔除
 */
float remove_outliers(float* data, uint32_t count) {
    // 计算平均值和标准差
    float mean = 0.0f, std_dev = 0.0f;
    
    for (uint32_t i = 0; i < count; i++) {
        mean += data[i];
    }
    mean /= count;
    
    for (uint32_t i = 0; i < count; i++) {
        float diff = data[i] - mean;
        std_dev += diff * diff;
    }
    std_dev = sqrtf(std_dev / count);
    
    // 剔除3σ外的异常值，重新计算平均值
    float sum = 0.0f;
    uint32_t valid_count = 0;
    
    for (uint32_t i = 0; i < count; i++) {
        if (fabsf(data[i] - mean) <= 3.0f * std_dev) {
            sum += data[i];
            valid_count++;
        }
    }
    
    return (valid_count > 0) ? (sum / valid_count) : mean;
}
```

**5. 校准参数存储**：
```c
/**
 * @brief  校准参数结构（用于存储）
 */
typedef struct {
    uint32_t magic_number;      // 魔数（用于验证）
    uint32_t version;           // 版本号
    uint32_t crc32;             // CRC校验
    
    // 零点校准
    float zero_offset;
    
    // 灵敏度校准
    float sensitivity;
    float offset;
    
    // 温度补偿
    float temp_coeff;
    float ref_temp;
    
    // 校准日期
    uint32_t calibration_date;
    
    // 预留空间
    uint8_t reserved[32];
} CalibrationParams_t;

#define CAL_MAGIC_NUMBER  0x43414C00  // "CAL\0"

/**
 * @brief  保存校准参数到Flash
 */
bool save_calibration_params(CalibrationParams_t* params) {
    params->magic_number = CAL_MAGIC_NUMBER;
    params->version = 1;
    
    // 计算CRC
    params->crc32 = calculate_crc32((uint8_t*)params,
                                    sizeof(CalibrationParams_t) - 4);
    
    // 写入Flash
    return flash_write(CALIBRATION_ADDR, (uint8_t*)params,
                      sizeof(CalibrationParams_t));
}

/**
 * @brief  从Flash加载校准参数
 */
bool load_calibration_params(CalibrationParams_t* params) {
    // 从Flash读取
    flash_read(CALIBRATION_ADDR, (uint8_t*)params,
              sizeof(CalibrationParams_t));
    
    // 验证魔数
    if (params->magic_number != CAL_MAGIC_NUMBER) {
        return false;
    }
    
    // 验证CRC
    uint32_t crc = calculate_crc32((uint8_t*)params,
                                   sizeof(CalibrationParams_t) - 4);
    if (crc != params->crc32) {
        return false;
    }
    
    return true;
}
```



## 总结

### 关键要点

1. **校准类型**：
   - 零点校准：消除零输入时的偏移
   - 灵敏度校准：修正输入输出比例关系
   - 温度补偿：消除温度影响
   - 非线性校正：修正非线性特性

2. **校准方法**：
   - 单点校准：仅零点校准
   - 两点校准：零点+灵敏度
   - 多点校准：非线性校正
   - 查表法：复杂非线性系统

3. **精度提升**：
   - 零点校准：提升2-5倍
   - 灵敏度校准：提升5-10倍
   - 温度补偿：提升3-8倍
   - 综合校准：提升10-100倍

4. **实施建议**：
   - 充分预热传感器
   - 使用高精度参考源
   - 采集足够样本数量
   - 控制环境条件
   - 定期重新校准

### 校准效果对比

```
校准前后精度对比：

传感器类型      校准前误差    校准后误差    精度提升
─────────────────────────────────────────────
温度传感器      ±2.0°C       ±0.2°C       10倍
压力传感器      ±5%          ±0.5%        10倍
加速度计        ±10%         ±1%          10倍
陀螺仪          ±5°/s        ±0.5°/s      10倍
磁力计          ±15%         ±2%          7.5倍

校准投入产出比：
- 开发时间：2-5天
- 成本增加：几乎为零
- 精度提升：5-100倍
- 用户满意度：显著提升
```

### 进阶学习

**推荐资源**：

1. **理论基础**：
   - 《传感器原理与应用》
   - 《测量不确定度评定》
   - 《数字信号处理》

2. **实践项目**：
   - 多传感器融合系统
   - 高精度测量仪器
   - 工业自动化系统

3. **相关技术**：
   - 卡尔曼滤波
   - 自适应滤波
   - 机器学习校准

### 常见问题

**Q1: 多久需要重新校准？**
A: 取决于传感器类型和应用要求：
- 高精度应用：每月或每季度
- 一般应用：每年
- 环境变化大：更频繁
- 出现异常时：立即重新校准

**Q2: 校准参数如何存储？**
A: 推荐方案：
- 存储位置：内部Flash或EEPROM
- 数据保护：CRC校验
- 版本管理：支持参数升级
- 备份机制：防止数据丢失

**Q3: 如何验证校准效果？**
A: 验证方法：
- 使用独立测试点
- 与高精度参考对比
- 计算残差和标准差
- 长期稳定性测试

**Q4: 温度补偿是否必需？**
A: 取决于应用场景：
- 宽温度范围：必需
- 高精度要求：必需
- 室温应用：可选
- 成本敏感：权衡考虑

**Q5: 如何处理多传感器校准？**
A: 建议策略：
- 独立校准每个传感器
- 考虑传感器间相互影响
- 使用统一校准框架
- 记录所有校准参数

### 实用工具

**校准辅助工具**：

```c
/**
 * @brief  校准质量评估
 */
typedef struct {
    float max_error;        // 最大误差
    float mean_error;       // 平均误差
    float std_dev;          // 标准差
    float r_squared;        // 拟合优度（R²）
} CalibrationQuality_t;

/**
 * @brief  评估校准质量
 */
void evaluate_calibration_quality(float* reference, float* measured,
                                  uint32_t count,
                                  CalibrationQuality_t* quality) {
    float sum_error = 0.0f;
    float sum_sq_error = 0.0f;
    float max_error = 0.0f;
    
    // 计算误差统计
    for (uint32_t i = 0; i < count; i++) {
        float error = measured[i] - reference[i];
        sum_error += error;
        sum_sq_error += error * error;
        
        if (fabsf(error) > max_error) {
            max_error = fabsf(error);
        }
    }
    
    quality->max_error = max_error;
    quality->mean_error = sum_error / count;
    quality->std_dev = sqrtf(sum_sq_error / count -
                            quality->mean_error * quality->mean_error);
    
    // 计算R²
    float mean_ref = 0.0f;
    for (uint32_t i = 0; i < count; i++) {
        mean_ref += reference[i];
    }
    mean_ref /= count;
    
    float ss_tot = 0.0f, ss_res = 0.0f;
    for (uint32_t i = 0; i < count; i++) {
        ss_tot += (reference[i] - mean_ref) * (reference[i] - mean_ref);
        ss_res += (measured[i] - reference[i]) * (measured[i] - reference[i]);
    }
    
    quality->r_squared = 1.0f - (ss_res / ss_tot);
}
```

### 下一步学习

完成本文学习后，建议继续学习：

1. **传感器数据融合**：
   - 多传感器信息融合
   - 卡尔曼滤波应用
   - 姿态解算算法

2. **自适应校准**：
   - 在线校准技术
   - 自学习算法
   - 智能补偿

3. **高级应用**：
   - 工业测量系统
   - 精密仪器开发
   - 质量控制系统

---

## 参考资料

1. IEEE Standard 1451 - Smart Transducer Interface Standards
2. ISO/IEC Guide 98-3 - Uncertainty of Measurement
3. NIST Special Publication 250 - Calibration Services
4. "Sensor Technology Handbook" - Jon S. Wilson
5. "Applied Sensor Technology" - Kourosh Kalantar-zadeh

---

**版权声明**：本文档由嵌入式知识平台内容团队原创，遵循CC BY-NC-SA 4.0协议。

**更新日志**：
- 2026-03-07: 初始版本发布
