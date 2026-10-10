---
title: "嵌入式系统功耗优化实战完全指南"
description: "深入讲解嵌入式系统中的功耗分析、优化策略、低功耗模式、外设管理和测试验证方法，帮助开发者设计节能高效的嵌入式系统"
slug: "power-optimization"

# 分类信息
domain: "工具链"
module: "性能优化"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 功耗优化
  - 低功耗
  - 能耗管理
  - 电源管理
  - 睡眠模式
prerequisites:
  - "了解嵌入式系统架构"
  - "掌握C语言编程"
  - "理解MCU工作原理"
related_contents:
  - "memory-optimization"
  - "code-optimization-basics"
  - "compiler-optimization"

# 学习信息
estimated_time: 80
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: "embedded-platform"
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
  - 功耗优化
  - 低功耗设计
  - 电源管理
  - 睡眠模式
  - 能耗分析
cover_image: ""
---

# 嵌入式系统功耗优化实战完全指南

## 学习目标

完成本教程后，你将能够:

- [ ] 理解嵌入式系统的功耗来源和特点
- [ ] 掌握功耗测量和分析方法
- [ ] 配置和使用MCU的低功耗模式
- [ ] 优化外设和时钟管理以降低功耗
- [ ] 实现动态电压频率调节（DVFS）
- [ ] 设计低功耗软件架构
- [ ] 优化中断和唤醒机制
- [ ] 验证和测试功耗优化效果

## 前置要求

在开始本教程之前，你需要:

**知识要求**:
- 熟悉C语言编程
- 了解MCU架构和外设
- 理解中断和定时器
- 掌握基本的电路知识

**技能要求**:
- 能够配置MCU时钟系统
- 会使用外设驱动
- 了解电源管理概念
- 能够阅读数据手册

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| 开发板 | 1 | STM32或其他ARM开发板 | - |
| 电流表/功耗分析仪 | 1 | 测量电流消耗 | - |
| 调试器 | 1 | ST-Link、J-Link或CMSIS-DAP | - |
| USB线 | 1-2 | 连接调试器和开发板 | - |
| 万用表 | 1 | 测量电压和电流 | - |

### 软件准备

- **IDE**: Keil MDK、IAR EWARM或VS Code
- **编译器**: ARM GCC工具链
- **分析工具**: STM32CubeMX、功耗计算器
- **测量软件**: 示波器软件、数据记录工具

### 系统要求

- **操作系统**: Windows、Linux或macOS
- **内存**: 至少4GB RAM
- **开发环境**: 已配置好的嵌入式开发工具链


## 步骤1: 理解功耗基础

### 1.1 功耗来源

**MCU功耗组成**:
```
总功耗 = 核心功耗 + 外设功耗 + 静态功耗 + 动态功耗
```

**核心功耗**:
- CPU执行指令
- 内存访问
- 缓存操作
- 与时钟频率和电压成正比

**外设功耗**:
- GPIO、UART、SPI、I2C等
- ADC、DAC转换
- 定时器运行
- DMA传输

**静态功耗（漏电流）**:
- 晶体管漏电
- 与温度相关
- 与工艺相关
- 通常很小但不可忽略

**动态功耗**:
```
P_dynamic = C × V² × f
```
- C: 负载电容
- V: 工作电压
- f: 工作频率

### 1.2 功耗模式

**典型MCU功耗模式（以STM32为例）**:

**运行模式（Run Mode）**:
- CPU和所有外设运行
- 功耗最高：10-50 mA
- 适用于正常工作

**睡眠模式（Sleep Mode）**:
- CPU停止，外设继续运行
- 功耗：2-10 mA
- 任何中断可唤醒
- 唤醒时间：微秒级

**停止模式（Stop Mode）**:
- CPU和大部分外设停止
- 保持SRAM和寄存器内容
- 功耗：1-100 μA
- 特定中断可唤醒
- 唤醒时间：毫秒级

**待机模式（Standby Mode）**:
- 几乎所有电路关闭
- 仅保持备份域
- 功耗：0.1-10 μA
- 需要复位唤醒
- 唤醒时间：毫秒级

**关断模式（Shutdown Mode）**:
- 所有电路关闭
- 功耗：< 1 μA
- 需要外部复位
- 数据丢失

### 1.3 功耗计算

**平均功耗计算**:
```c
// 工作周期模型
typedef struct {
    float run_current_mA;      // 运行电流
    float run_time_ms;         // 运行时间
    float sleep_current_mA;    // 睡眠电流
    float sleep_time_ms;       // 睡眠时间
} PowerProfile_t;

float calculate_average_current(const PowerProfile_t *profile) {
    float total_time = profile->run_time_ms + profile->sleep_time_ms;
    
    float avg_current = (profile->run_current_mA * profile->run_time_ms +
                        profile->sleep_current_mA * profile->sleep_time_ms) /
                        total_time;
    
    return avg_current;
}

// 示例：每秒采集一次传感器数据
void example_calculation(void) {
    PowerProfile_t profile = {
        .run_current_mA = 20.0f,    // 运行时20mA
        .run_time_ms = 100.0f,      // 运行100ms
        .sleep_current_mA = 0.05f,  // 睡眠时50μA
        .sleep_time_ms = 900.0f     // 睡眠900ms
    };
    
    float avg = calculate_average_current(&profile);
    printf("平均电流: %.2f mA\n", avg);  // 约2.05 mA
    
    // 电池寿命估算
    float battery_mAh = 2000.0f;  // 2000mAh电池
    float lifetime_hours = battery_mAh / avg;
    printf("电池寿命: %.1f 小时 (%.1f 天)\n", 
           lifetime_hours, lifetime_hours / 24);
}
```

**能量消耗计算**:
```c
// 能量 = 功率 × 时间
typedef struct {
    float voltage_V;           // 工作电压
    float current_mA;          // 电流
    float duration_ms;         // 持续时间
} EnergyProfile_t;

float calculate_energy_mJ(const EnergyProfile_t *profile) {
    // 功率(mW) = 电压(V) × 电流(mA)
    float power_mW = profile->voltage_V * profile->current_mA;
    
    // 能量(mJ) = 功率(mW) × 时间(s)
    float energy_mJ = power_mW * (profile->duration_ms / 1000.0f);
    
    return energy_mJ;
}
```


## 步骤2: 功耗测量

### 2.1 硬件测量方法

**方法1：串联电流表**:
```
电源 → 电流表 → MCU VDD
```

**优点**:
- 简单直接
- 精确度高

**缺点**:
- 无法测量瞬态电流
- 可能影响电路

**方法2：分流电阻测量**:
```c
// 在VDD和MCU之间串联小电阻（如0.1Ω）
// 测量电阻两端电压，计算电流

// 电流(A) = 电压(V) / 电阻(Ω)
float measure_current_shunt(float voltage_mV, float resistance_ohm) {
    return (voltage_mV / 1000.0f) / resistance_ohm * 1000.0f;  // 返回mA
}

// 示例：0.1Ω电阻，测得2mV电压
// 电流 = 2mV / 0.1Ω = 20mA
```

**方法3：功耗分析仪**:
- 使用专业设备（如Joulescope、PPK2）
- 可以捕获瞬态电流
- 提供详细的功耗曲线
- 支持数据记录和分析

### 2.2 软件测量方法

**使用内部ADC测量**:
```c
// 通过ADC测量分流电阻电压
#define SHUNT_RESISTANCE 0.1f  // 0.1Ω
#define ADC_VREF 3.3f          // ADC参考电压

float measure_current_adc(void) {
    // 读取ADC值（12位）
    uint16_t adc_value = HAL_ADC_GetValue(&hadc1);
    
    // 转换为电压
    float voltage = (adc_value / 4095.0f) * ADC_VREF;
    
    // 计算电流
    float current_mA = (voltage / SHUNT_RESISTANCE) * 1000.0f;
    
    return current_mA;
}

// 连续监控
void monitor_power_consumption(void) {
    static uint32_t sample_count = 0;
    static float total_current = 0;
    
    float current = measure_current_adc();
    total_current += current;
    sample_count++;
    
    if (sample_count >= 1000) {
        float avg_current = total_current / sample_count;
        printf("平均电流: %.2f mA\n", avg_current);
        
        // 重置
        sample_count = 0;
        total_current = 0;
    }
}
```

**功耗日志记录**:
```c
#define POWER_LOG_SIZE 1000

typedef struct {
    uint32_t timestamp_ms;
    float current_mA;
    uint8_t power_mode;
} PowerLogEntry_t;

PowerLogEntry_t power_log[POWER_LOG_SIZE];
uint16_t log_index = 0;

void log_power_consumption(float current_mA, uint8_t mode) {
    if (log_index < POWER_LOG_SIZE) {
        power_log[log_index].timestamp_ms = HAL_GetTick();
        power_log[log_index].current_mA = current_mA;
        power_log[log_index].power_mode = mode;
        log_index++;
    }
}

void print_power_log(void) {
    printf("\n=== Power Consumption Log ===\n");
    printf("Time(ms)  Current(mA)  Mode\n");
    
    for (uint16_t i = 0; i < log_index; i++) {
        printf("%8lu  %10.2f  %4d\n",
               power_log[i].timestamp_ms,
               power_log[i].current_mA,
               power_log[i].power_mode);
    }
    
    // 计算统计信息
    float total = 0, max = 0, min = 999999;
    for (uint16_t i = 0; i < log_index; i++) {
        float curr = power_log[i].current_mA;
        total += curr;
        if (curr > max) max = curr;
        if (curr < min) min = curr;
    }
    
    printf("\nStatistics:\n");
    printf("Average: %.2f mA\n", total / log_index);
    printf("Maximum: %.2f mA\n", max);
    printf("Minimum: %.2f mA\n", min);
}
```

### 2.3 功耗分析

**识别功耗热点**:
```c
typedef struct {
    const char *name;
    uint32_t start_time;
    uint32_t duration_ms;
    float avg_current_mA;
    float energy_mJ;
} PowerHotspot_t;

#define MAX_HOTSPOTS 10
PowerHotspot_t hotspots[MAX_HOTSPOTS];
uint8_t hotspot_count = 0;

void start_power_measurement(const char *name) {
    if (hotspot_count < MAX_HOTSPOTS) {
        hotspots[hotspot_count].name = name;
        hotspots[hotspot_count].start_time = HAL_GetTick();
    }
}

void end_power_measurement(float avg_current_mA) {
    if (hotspot_count < MAX_HOTSPOTS) {
        uint32_t end_time = HAL_GetTick();
        PowerHotspot_t *hs = &hotspots[hotspot_count];
        
        hs->duration_ms = end_time - hs->start_time;
        hs->avg_current_mA = avg_current_mA;
        hs->energy_mJ = (avg_current_mA * 3.3f) * (hs->duration_ms / 1000.0f);
        
        hotspot_count++;
    }
}

void print_power_hotspots(void) {
    printf("\n=== Power Hotspots ===\n");
    printf("%-20s Duration(ms)  Current(mA)  Energy(mJ)\n", "Function");
    
    for (uint8_t i = 0; i < hotspot_count; i++) {
        PowerHotspot_t *hs = &hotspots[i];
        printf("%-20s %11lu  %11.2f  %10.2f\n",
               hs->name, hs->duration_ms, hs->avg_current_mA, hs->energy_mJ);
    }
    
    // 按能量排序并显示最耗能的操作
    // （简化版，实际应该排序）
}

// 使用示例
void example_usage(void) {
    start_power_measurement("ADC_Conversion");
    // 执行ADC转换
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 100);
    end_power_measurement(5.2f);  // 测得5.2mA
    
    start_power_measurement("UART_Transmit");
    // 发送数据
    HAL_UART_Transmit(&huart1, data, size, 100);
    end_power_measurement(8.5f);  // 测得8.5mA
}
```


## 步骤3: 低功耗模式配置

### 3.1 睡眠模式（Sleep Mode）

**STM32睡眠模式配置**:
```c
// 进入睡眠模式
void enter_sleep_mode(void) {
    // 挂起SysTick以避免唤醒
    HAL_SuspendTick();
    
    // 进入睡眠模式
    // 参数：PWR_MAINREGULATOR_ON - 保持主稳压器开启
    //       PWR_SLEEPENTRY_WFI - 使用WFI指令进入
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // 唤醒后恢复SysTick
    HAL_ResumeTick();
}

// 配置唤醒源
void configure_wakeup_sources(void) {
    // 配置外部中断唤醒
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 配置定时器唤醒
    HAL_NVIC_SetPriority(TIM2_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
}

// 中断处理函数
void EXTI0_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
    // MCU自动唤醒
}

// 使用示例
void low_power_task(void) {
    while (1) {
        // 执行任务
        process_data();
        
        // 进入睡眠等待中断
        enter_sleep_mode();
        
        // 被中断唤醒后继续执行
    }
}
```

**使用WFI和WFE指令**:
```c
// WFI (Wait For Interrupt) - 等待中断
void sleep_wfi(void) {
    __WFI();  // CPU停止，等待任何中断
}

// WFE (Wait For Event) - 等待事件
void sleep_wfe(void) {
    __WFE();  // CPU停止，等待事件或中断
}

// SEV (Send Event) - 发送事件
void wakeup_other_cores(void) {
    __SEV();  // 唤醒等待事件的核心
}
```

### 3.2 停止模式（Stop Mode）

**STM32停止模式配置**:
```c
// 进入停止模式
void enter_stop_mode(void) {
    // 挂起SysTick
    HAL_SuspendTick();
    
    // 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // 进入停止模式
    // PWR_LOWPOWERREGULATOR_ON - 使用低功耗稳压器
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
    
    // 唤醒后重新配置时钟（停止模式会关闭HSE和PLL）
    SystemClock_Config();
    
    // 恢复SysTick
    HAL_ResumeTick();
}

// 配置RTC唤醒
void configure_rtc_wakeup(uint32_t seconds) {
    // 禁用RTC唤醒
    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    
    // 配置唤醒时间
    HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds, RTC_WAKEUPCLOCK_CK_SPRE_16BITS);
}

// RTC唤醒中断处理
void RTC_WKUP_IRQHandler(void) {
    HAL_RTCEx_WakeUpTimerIRQHandler(&hrtc);
}

void HAL_RTCEx_WakeUpTimerEventCallback(RTC_HandleTypeDef *hrtc) {
    // 从停止模式唤醒
}

// 使用示例：每10秒唤醒一次
void periodic_wakeup_example(void) {
    configure_rtc_wakeup(10);  // 10秒后唤醒
    
    while (1) {
        // 执行任务
        read_sensor();
        transmit_data();
        
        // 进入停止模式
        enter_stop_mode();
        
        // 10秒后被RTC唤醒
    }
}
```

**外设时钟管理**:
```c
// 进入停止模式前关闭不需要的外设
void disable_peripherals_for_stop(void) {
    // 关闭不需要的外设时钟
    __HAL_RCC_GPIOB_CLK_DISABLE();
    __HAL_RCC_GPIOC_CLK_DISABLE();
    __HAL_RCC_SPI1_CLK_DISABLE();
    __HAL_RCC_USART2_CLK_DISABLE();
    __HAL_RCC_TIM3_CLK_DISABLE();
    
    // 保持必要的外设（如RTC、EXTI）
}

// 唤醒后重新使能外设
void enable_peripherals_after_stop(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_SPI1_CLK_ENABLE();
    __HAL_RCC_USART2_CLK_ENABLE();
    __HAL_RCC_TIM3_CLK_ENABLE();
}
```

### 3.3 待机模式（Standby Mode）

**STM32待机模式配置**:
```c
// 进入待机模式
void enter_standby_mode(void) {
    // 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
    
    // 使能唤醒引脚
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // 进入待机模式
    HAL_PWR_EnterSTANDBYMode();
    
    // 注意：此函数不会返回
    // 唤醒后MCU会复位重启
}

// 配置RTC闹钟唤醒
void configure_rtc_alarm_wakeup(uint32_t seconds) {
    RTC_AlarmTypeDef alarm = {0};
    RTC_TimeTypeDef time;
    
    // 获取当前时间
    HAL_RTC_GetTime(&hrtc, &time, RTC_FORMAT_BIN);
    
    // 设置闹钟时间
    alarm.AlarmTime.Hours = time.Hours;
    alarm.AlarmTime.Minutes = time.Minutes;
    alarm.AlarmTime.Seconds = (time.Seconds + seconds) % 60;
    alarm.AlarmMask = RTC_ALARMMASK_DATEWEEKDAY;
    alarm.Alarm = RTC_ALARM_A;
    
    HAL_RTC_SetAlarm_IT(&hrtc, &alarm, RTC_FORMAT_BIN);
}

// 检查唤醒原因
void check_wakeup_reason(void) {
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB)) {
        // 从待机模式唤醒
        printf("Wakeup from Standby mode\n");
        
        // 清除标志
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    } else {
        // 正常上电或复位
        printf("Normal power-on or reset\n");
    }
}

// 使用示例：每小时唤醒一次
void hourly_wakeup_example(void) {
    // 检查唤醒原因
    check_wakeup_reason();
    
    // 执行任务
    read_sensor();
    transmit_data();
    
    // 配置1小时后唤醒
    configure_rtc_alarm_wakeup(3600);
    
    // 进入待机模式
    enter_standby_mode();
}
```

**备份域数据保存**:
```c
// 在待机模式下保存数据到备份寄存器
void save_data_to_backup(uint32_t data) {
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 写入备份寄存器
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR0, data);
    
    // 禁用备份域访问
    HAL_PWR_DisableBkUpAccess();
}

// 从备份寄存器读取数据
uint32_t read_data_from_backup(void) {
    return HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR0);
}

// 使用示例
void backup_example(void) {
    uint32_t counter = read_data_from_backup();
    counter++;
    
    printf("Wakeup count: %lu\n", counter);
    
    save_data_to_backup(counter);
    
    // 进入待机模式
    enter_standby_mode();
}
```


## 步骤4: 时钟和电压优化

### 4.1 动态时钟调节

**降低系统时钟频率**:
```c
// 时钟配置结构
typedef struct {
    uint32_t sysclk_freq;      // 系统时钟频率
    uint32_t ahb_prescaler;    // AHB预分频
    uint32_t apb1_prescaler;   // APB1预分频
    uint32_t apb2_prescaler;   // APB2预分频
} ClockConfig_t;

// 预定义的时钟配置
const ClockConfig_t clock_configs[] = {
    // 高性能模式：72MHz
    {72000000, RCC_SYSCLK_DIV1, RCC_HCLK_DIV2, RCC_HCLK_DIV1},
    // 中等性能：36MHz
    {36000000, RCC_SYSCLK_DIV2, RCC_HCLK_DIV1, RCC_HCLK_DIV1},
    // 低功耗模式：8MHz
    {8000000, RCC_SYSCLK_DIV1, RCC_HCLK_DIV1, RCC_HCLK_DIV1}
};

// 切换时钟配置
void switch_clock_config(uint8_t config_index) {
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    const ClockConfig_t *config = &clock_configs[config_index];
    
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = config->ahb_prescaler;
    RCC_ClkInitStruct.APB1CLKDivider = config->apb1_prescaler;
    RCC_ClkInitStruct.APB2CLKDivider = config->apb2_prescaler;
    
    // 调整Flash等待周期
    uint32_t flash_latency = (config->sysclk_freq > 48000000) ? 
                             FLASH_LATENCY_2 : FLASH_LATENCY_1;
    
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, flash_latency);
    
    // 更新SystemCoreClock变量
    SystemCoreClockUpdate();
}

// 根据负载动态调整时钟
void dynamic_clock_scaling(void) {
    static uint32_t idle_count = 0;
    static uint8_t current_config = 0;  // 0=高性能, 1=中等, 2=低功耗
    
    if (is_system_busy()) {
        // 系统繁忙，切换到高性能模式
        if (current_config != 0) {
            switch_clock_config(0);
            current_config = 0;
        }
        idle_count = 0;
    } else {
        // 系统空闲
        idle_count++;
        
        if (idle_count > 1000 && current_config != 2) {
            // 长时间空闲，切换到低功耗模式
            switch_clock_config(2);
            current_config = 2;
        } else if (idle_count > 100 && current_config == 0) {
            // 短时间空闲，切换到中等性能
            switch_clock_config(1);
            current_config = 1;
        }
    }
}
```

**外设时钟门控**:
```c
// 外设时钟管理
typedef struct {
    uint32_t gpio_clocks;
    uint32_t timer_clocks;
    uint32_t comm_clocks;
    uint32_t adc_clocks;
} PeripheralClocks_t;

// 保存当前使能的时钟
PeripheralClocks_t enabled_clocks = {0};

// 使能外设时钟
void enable_peripheral_clock(uint32_t peripheral) {
    switch (peripheral) {
        case PERIPHERAL_GPIOA:
            __HAL_RCC_GPIOA_CLK_ENABLE();
            enabled_clocks.gpio_clocks |= (1 << 0);
            break;
        case PERIPHERAL_USART1:
            __HAL_RCC_USART1_CLK_ENABLE();
            enabled_clocks.comm_clocks |= (1 << 0);
            break;
        case PERIPHERAL_TIM2:
            __HAL_RCC_TIM2_CLK_ENABLE();
            enabled_clocks.timer_clocks |= (1 << 0);
            break;
        // 其他外设...
    }
}

// 禁用外设时钟
void disable_peripheral_clock(uint32_t peripheral) {
    switch (peripheral) {
        case PERIPHERAL_GPIOA:
            __HAL_RCC_GPIOA_CLK_DISABLE();
            enabled_clocks.gpio_clocks &= ~(1 << 0);
            break;
        case PERIPHERAL_USART1:
            __HAL_RCC_USART1_CLK_DISABLE();
            enabled_clocks.comm_clocks &= ~(1 << 0);
            break;
        case PERIPHERAL_TIM2:
            __HAL_RCC_TIM2_CLK_DISABLE();
            enabled_clocks.timer_clocks &= ~(1 << 0);
            break;
        // 其他外设...
    }
}

// 批量禁用未使用的外设
void disable_unused_peripherals(void) {
    // 禁用未使用的GPIO
    __HAL_RCC_GPIOB_CLK_DISABLE();
    __HAL_RCC_GPIOC_CLK_DISABLE();
    __HAL_RCC_GPIOD_CLK_DISABLE();
    
    // 禁用未使用的定时器
    __HAL_RCC_TIM3_CLK_DISABLE();
    __HAL_RCC_TIM4_CLK_DISABLE();
    
    // 禁用未使用的通信接口
    __HAL_RCC_SPI2_CLK_DISABLE();
    __HAL_RCC_I2C2_CLK_DISABLE();
    
    // 禁用未使用的ADC/DAC
    __HAL_RCC_ADC2_CLK_DISABLE();
    __HAL_RCC_DAC_CLK_DISABLE();
}
```

### 4.2 动态电压调节

**电压调节器配置**:
```c
// STM32电压调节器模式
typedef enum {
    VOLTAGE_SCALE_HIGH = PWR_REGULATOR_VOLTAGE_SCALE1,  // 高性能
    VOLTAGE_SCALE_MED = PWR_REGULATOR_VOLTAGE_SCALE2,   // 中等性能
    VOLTAGE_SCALE_LOW = PWR_REGULATOR_VOLTAGE_SCALE3    // 低功耗
} VoltageScale_t;

// 设置电压调节器模式
void set_voltage_scale(VoltageScale_t scale) {
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(scale);
    
    // 等待电压稳定
    while (__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY) == RESET);
}

// 根据时钟频率调整电压
void adjust_voltage_for_frequency(uint32_t freq_hz) {
    if (freq_hz > 64000000) {
        // 高频需要高电压
        set_voltage_scale(VOLTAGE_SCALE_HIGH);
    } else if (freq_hz > 16000000) {
        // 中频使用中等电压
        set_voltage_scale(VOLTAGE_SCALE_MED);
    } else {
        // 低频使用低电压
        set_voltage_scale(VOLTAGE_SCALE_LOW);
    }
}

// DVFS（动态电压频率调节）
void dvfs_set_performance_level(uint8_t level) {
    switch (level) {
        case 0:  // 低功耗模式
            set_voltage_scale(VOLTAGE_SCALE_LOW);
            switch_clock_config(2);  // 8MHz
            break;
            
        case 1:  // 中等性能
            set_voltage_scale(VOLTAGE_SCALE_MED);
            switch_clock_config(1);  // 36MHz
            break;
            
        case 2:  // 高性能
            set_voltage_scale(VOLTAGE_SCALE_HIGH);
            switch_clock_config(0);  // 72MHz
            break;
    }
}
```

### 4.3 时钟源选择

**使用低功耗时钟源**:
```c
// 切换到内部RC振荡器（HSI）
void switch_to_hsi(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    // 配置HSI
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
    
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // 切换系统时钟到HSI
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
    
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0);
    
    // 关闭HSE和PLL以节省功耗
    __HAL_RCC_HSE_CONFIG(RCC_HSE_OFF);
    __HAL_RCC_PLL_DISABLE();
}

// 切换到外部晶振（HSE）+ PLL
void switch_to_hse_pll(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    // 配置HSE和PLL
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;
    RCC_OscInitStruct.PLL.PLLN = 72;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // 切换系统时钟到PLL
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}
```


## 步骤5: 外设功耗优化

### 5.1 GPIO优化

**GPIO配置优化**:
```c
// 未使用的GPIO应配置为模拟输入（最低功耗）
void configure_unused_gpio_low_power(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // 配置所有未使用的引脚为模拟输入
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    
    // GPIOA未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_3 | GPIO_PIN_4 | GPIO_PIN_5;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // GPIOB未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    // GPIOC未使用的引脚
    GPIO_InitStruct.Pin = GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 配置完成后可以禁用GPIO时钟
    __HAL_RCC_GPIOB_CLK_DISABLE();
    __HAL_RCC_GPIOC_CLK_DISABLE();
}

// 输出引脚的功耗优化
void optimize_gpio_output(void) {
    // 使用推挽输出而不是开漏输出（功耗更低）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;  // 推挽输出
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;  // 低速度（低功耗）
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

// 输入引脚的功耗优化
void optimize_gpio_input(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    
    // 根据外部电路选择上拉或下拉，避免浮空
    // 浮空输入会导致额外功耗
    GPIO_InitStruct.Pull = GPIO_PULLUP;  // 或 GPIO_PULLDOWN
    
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}
```

**LED功耗优化**:
```c
// 使用PWM控制LED亮度，降低平均功耗
void led_pwm_control(uint8_t brightness) {
    // brightness: 0-100
    TIM_OC_InitTypeDef sConfigOC = {0};
    
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = brightness;  // 占空比
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    
    HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
}

// 使用定时器自动关闭LED
void led_auto_off(uint32_t timeout_ms) {
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    
    // 启动定时器
    HAL_TIM_Base_Start_IT(&htim3);
    
    // 定时器中断中关闭LED
}
```

### 5.2 通信接口优化

**UART功耗优化**:
```c
// 使用DMA传输，CPU可以进入睡眠
void uart_transmit_dma_low_power(uint8_t *data, uint16_t size) {
    // 启动DMA传输
    HAL_UART_Transmit_DMA(&huart1, data, size);
    
    // 进入睡眠模式，等待传输完成中断
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
}

// 传输完成回调
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    // 传输完成，CPU自动唤醒
    // 可以禁用UART以节省功耗
    HAL_UART_DeInit(huart);
    __HAL_RCC_USART1_CLK_DISABLE();
}

// 接收时使用中断模式
void uart_receive_low_power(uint8_t *buffer, uint16_t size) {
    // 配置接收中断
    HAL_UART_Receive_IT(&huart1, buffer, size);
    
    // 进入睡眠模式
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
}

// 不使用时禁用UART
void uart_disable_when_idle(void) {
    HAL_UART_DeInit(&huart1);
    __HAL_RCC_USART1_CLK_DISABLE();
}

// 需要时重新使能
void uart_enable_when_needed(void) {
    __HAL_RCC_USART1_CLK_ENABLE();
    HAL_UART_Init(&huart1);
}
```

**SPI功耗优化**:
```c
// SPI传输后立即禁用
void spi_transfer_low_power(uint8_t *tx_data, uint8_t *rx_data, uint16_t size) {
    // 使能SPI
    __HAL_RCC_SPI1_CLK_ENABLE();
    
    // 传输数据
    HAL_SPI_TransmitReceive(&hspi1, tx_data, rx_data, size, 1000);
    
    // 立即禁用SPI
    HAL_SPI_DeInit(&hspi1);
    __HAL_RCC_SPI1_CLK_DISABLE();
}

// 使用DMA传输
void spi_transfer_dma_low_power(uint8_t *tx_data, uint8_t *rx_data, uint16_t size) {
    __HAL_RCC_SPI1_CLK_ENABLE();
    
    // 启动DMA传输
    HAL_SPI_TransmitReceive_DMA(&hspi1, tx_data, rx_data, size);
    
    // 进入睡眠模式
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
}
```

**I2C功耗优化**:
```c
// I2C快速模式vs标准模式
void i2c_configure_for_low_power(void) {
    // 标准模式（100kHz）比快速模式（400kHz）功耗更低
    hi2c1.Init.ClockSpeed = 100000;  // 100kHz
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    HAL_I2C_Init(&hi2c1);
}

// 批量传输减少启动开销
void i2c_batch_transfer(uint8_t device_addr, uint8_t *data, uint16_t size) {
    // 一次传输多个字节，而不是多次单字节传输
    HAL_I2C_Master_Transmit(&hi2c1, device_addr, data, size, 1000);
}
```

### 5.3 ADC功耗优化

**ADC配置优化**:
```c
// 使用较低的采样率
void adc_configure_low_power(void) {
    ADC_ChannelConfTypeDef sConfig = {0};
    
    // 配置ADC
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV8;  // 降低时钟
    hadc1.Init.Resolution = ADC_RESOLUTION_8B;  // 8位分辨率（如果足够）
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;  // 单次转换
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    
    HAL_ADC_Init(&hadc1);
    
    // 配置通道采样时间（较长的采样时间可以降低功耗）
    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_239CYCLES_5;  // 长采样时间
    
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
}

// 按需启动ADC
void adc_on_demand_conversion(void) {
    // 使能ADC
    __HAL_RCC_ADC1_CLK_ENABLE();
    HAL_ADC_Start(&hadc1);
    
    // 等待转换完成
    HAL_ADC_PollForConversion(&hadc1, 100);
    uint32_t value = HAL_ADC_GetValue(&hadc1);
    
    // 立即停止并禁用ADC
    HAL_ADC_Stop(&hadc1);
    __HAL_RCC_ADC1_CLK_DISABLE();
    
    // 处理数据
    process_adc_value(value);
}

// 使用DMA和定时器自动采集
void adc_dma_timer_low_power(void) {
    uint16_t adc_buffer[10];
    
    // 配置定时器触发ADC
    HAL_TIM_Base_Start(&htim2);
    
    // 启动DMA采集
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, 10);
    
    // 进入睡眠模式
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // DMA完成后自动唤醒
}
```

### 5.4 定时器优化

**定时器功耗优化**:
```c
// 使用低功耗定时器（LPTIM）
void lptim_configure(void) {
    // LPTIM可以在停止模式下继续运行
    hlptim1.Instance = LPTIM1;
    hlptim1.Init.Clock.Source = LPTIM_CLOCKSOURCE_APBCLOCK_LPOSC;
    hlptim1.Init.Clock.Prescaler = LPTIM_PRESCALER_DIV1;
    hlptim1.Init.Trigger.Source = LPTIM_TRIGSOURCE_SOFTWARE;
    hlptim1.Init.OutputPolarity = LPTIM_OUTPUTPOLARITY_HIGH;
    hlptim1.Init.UpdateMode = LPTIM_UPDATE_IMMEDIATE;
    hlptim1.Init.CounterSource = LPTIM_COUNTERSOURCE_INTERNAL;
    
    HAL_LPTIM_Init(&hlptim1);
}

// 使用RTC代替通用定时器
void rtc_periodic_wakeup(uint32_t period_seconds) {
    // RTC功耗远低于通用定时器
    HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, period_seconds, 
                                RTC_WAKEUPCLOCK_CK_SPRE_16BITS);
}

// 禁用不需要的定时器
void disable_unused_timers(void) {
    HAL_TIM_Base_Stop(&htim3);
    HAL_TIM_Base_Stop(&htim4);
    
    __HAL_RCC_TIM3_CLK_DISABLE();
    __HAL_RCC_TIM4_CLK_DISABLE();
}
```


## 步骤6: 软件架构优化

### 6.1 事件驱动架构

**轮询 vs 事件驱动**:
```c
// 不好：轮询方式（持续消耗CPU）
void polling_approach(void) {
    while (1) {
        if (button_pressed()) {
            handle_button();
        }
        if (data_available()) {
            process_data();
        }
        // CPU一直运行，功耗高
    }
}

// 好：事件驱动（CPU大部分时间睡眠）
void event_driven_approach(void) {
    // 配置中断
    configure_button_interrupt();
    configure_data_ready_interrupt();
    
    while (1) {
        // 进入睡眠模式
        enter_sleep_mode();
        
        // 被中断唤醒后处理事件
        if (button_event) {
            handle_button();
            button_event = false;
        }
        if (data_event) {
            process_data();
            data_event = false;
        }
    }
}
```

**事件队列实现**:
```c
#define EVENT_QUEUE_SIZE 16

typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESS,
    EVENT_DATA_READY,
    EVENT_TIMER_EXPIRED,
    EVENT_SENSOR_READING
} EventType_t;

typedef struct {
    EventType_t type;
    uint32_t data;
    uint32_t timestamp;
} Event_t;

typedef struct {
    Event_t events[EVENT_QUEUE_SIZE];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
} EventQueue_t;

EventQueue_t event_queue = {0};

// 添加事件到队列
bool event_queue_push(EventType_t type, uint32_t data) {
    if (event_queue.count >= EVENT_QUEUE_SIZE) {
        return false;  // 队列满
    }
    
    Event_t *event = &event_queue.events[event_queue.tail];
    event->type = type;
    event->data = data;
    event->timestamp = HAL_GetTick();
    
    event_queue.tail = (event_queue.tail + 1) % EVENT_QUEUE_SIZE;
    event_queue.count++;
    
    return true;
}

// 从队列获取事件
bool event_queue_pop(Event_t *event) {
    if (event_queue.count == 0) {
        return false;  // 队列空
    }
    
    *event = event_queue.events[event_queue.head];
    event_queue.head = (event_queue.head + 1) % EVENT_QUEUE_SIZE;
    event_queue.count--;
    
    return true;
}

// 主循环
void event_driven_main_loop(void) {
    Event_t event;
    
    while (1) {
        // 处理所有待处理事件
        while (event_queue_pop(&event)) {
            switch (event.type) {
                case EVENT_BUTTON_PRESS:
                    handle_button_press(event.data);
                    break;
                case EVENT_DATA_READY:
                    process_data(event.data);
                    break;
                case EVENT_TIMER_EXPIRED:
                    handle_timer(event.data);
                    break;
                case EVENT_SENSOR_READING:
                    process_sensor(event.data);
                    break;
                default:
                    break;
            }
        }
        
        // 所有事件处理完毕，进入睡眠
        enter_sleep_mode();
    }
}

// 中断中添加事件
void EXTI0_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
    event_queue_push(EVENT_BUTTON_PRESS, 0);
}
```

### 6.2 任务调度优化

**简单的任务调度器**:
```c
#define MAX_TASKS 8

typedef void (*TaskFunction_t)(void);

typedef struct {
    TaskFunction_t function;
    uint32_t period_ms;
    uint32_t last_run;
    bool enabled;
} Task_t;

Task_t tasks[MAX_TASKS];
uint8_t task_count = 0;

// 注册任务
void task_register(TaskFunction_t func, uint32_t period_ms) {
    if (task_count < MAX_TASKS) {
        tasks[task_count].function = func;
        tasks[task_count].period_ms = period_ms;
        tasks[task_count].last_run = 0;
        tasks[task_count].enabled = true;
        task_count++;
    }
}

// 计算下次唤醒时间
uint32_t calculate_next_wakeup(void) {
    uint32_t current_time = HAL_GetTick();
    uint32_t next_wakeup = UINT32_MAX;
    
    for (uint8_t i = 0; i < task_count; i++) {
        if (tasks[i].enabled) {
            uint32_t next_run = tasks[i].last_run + tasks[i].period_ms;
            if (next_run < next_wakeup) {
                next_wakeup = next_run;
            }
        }
    }
    
    return (next_wakeup > current_time) ? (next_wakeup - current_time) : 0;
}

// 任务调度器主循环
void task_scheduler_run(void) {
    while (1) {
        uint32_t current_time = HAL_GetTick();
        bool task_executed = false;
        
        // 执行到期的任务
        for (uint8_t i = 0; i < task_count; i++) {
            if (tasks[i].enabled) {
                uint32_t elapsed = current_time - tasks[i].last_run;
                if (elapsed >= tasks[i].period_ms) {
                    tasks[i].function();
                    tasks[i].last_run = current_time;
                    task_executed = true;
                }
            }
        }
        
        // 如果没有任务执行，进入睡眠
        if (!task_executed) {
            uint32_t sleep_time = calculate_next_wakeup();
            
            if (sleep_time > 0) {
                // 配置定时器唤醒
                configure_timer_wakeup(sleep_time);
                
                // 进入睡眠模式
                enter_sleep_mode();
            }
        }
    }
}

// 示例任务
void task_read_sensor(void) {
    // 读取传感器
    float temperature = read_temperature();
    printf("Temperature: %.1f\n", temperature);
}

void task_send_data(void) {
    // 发送数据
    transmit_data();
}

void task_check_battery(void) {
    // 检查电池电量
    float voltage = read_battery_voltage();
    printf("Battery: %.2fV\n", voltage);
}

// 初始化
void init_tasks(void) {
    task_register(task_read_sensor, 1000);   // 每1秒
    task_register(task_send_data, 5000);     // 每5秒
    task_register(task_check_battery, 60000); // 每60秒
}
```

### 6.3 批处理优化

**批量处理数据**:
```c
#define BATCH_SIZE 10

typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
} SensorData_t;

SensorData_t data_buffer[BATCH_SIZE];
uint8_t buffer_index = 0;

// 收集数据
void collect_sensor_data(void) {
    if (buffer_index < BATCH_SIZE) {
        data_buffer[buffer_index].temperature = read_temperature();
        data_buffer[buffer_index].humidity = read_humidity();
        data_buffer[buffer_index].timestamp = HAL_GetTick();
        buffer_index++;
    }
    
    // 缓冲区满时批量发送
    if (buffer_index >= BATCH_SIZE) {
        batch_transmit_data();
        buffer_index = 0;
    }
}

// 批量发送（减少通信开销）
void batch_transmit_data(void) {
    // 一次性发送所有数据
    uart_transmit_dma((uint8_t*)data_buffer, 
                      sizeof(SensorData_t) * BATCH_SIZE);
}
```

**延迟处理**:
```c
// 延迟非关键任务到空闲时间
typedef struct {
    void (*function)(void);
    uint32_t priority;
} DeferredTask_t;

#define DEFERRED_QUEUE_SIZE 16
DeferredTask_t deferred_queue[DEFERRED_QUEUE_SIZE];
uint8_t deferred_count = 0;

// 添加延迟任务
void defer_task(void (*func)(void), uint32_t priority) {
    if (deferred_count < DEFERRED_QUEUE_SIZE) {
        deferred_queue[deferred_count].function = func;
        deferred_queue[deferred_count].priority = priority;
        deferred_count++;
    }
}

// 在空闲时处理延迟任务
void process_deferred_tasks(void) {
    if (deferred_count > 0) {
        // 执行最高优先级任务
        uint8_t highest_priority_index = 0;
        uint32_t highest_priority = 0;
        
        for (uint8_t i = 0; i < deferred_count; i++) {
            if (deferred_queue[i].priority > highest_priority) {
                highest_priority = deferred_queue[i].priority;
                highest_priority_index = i;
            }
        }
        
        // 执行任务
        deferred_queue[highest_priority_index].function();
        
        // 移除任务
        for (uint8_t i = highest_priority_index; i < deferred_count - 1; i++) {
            deferred_queue[i] = deferred_queue[i + 1];
        }
        deferred_count--;
    }
}
```


## 步骤7: 实际案例

### 案例1: 温度监测系统

**需求**:
- 每分钟采集一次温度
- 每小时上传一次数据
- 电池供电，需要运行1年

**原始实现（高功耗）**:
```c
void temperature_monitor_high_power(void) {
    while (1) {
        // 读取温度
        float temp = read_temperature();
        store_temperature(temp);
        
        // 检查是否需要上传
        if (should_upload()) {
            upload_data();
        }
        
        // 延时1分钟（CPU一直运行）
        HAL_Delay(60000);
    }
}

// 功耗分析：
// - 运行模式：20mA × 60秒 = 1200mA·s
// - 平均功耗：20mA
// - 电池寿命：2000mAh / 20mA = 100小时 ≈ 4天
```

**优化实现（低功耗）**:
```c
void temperature_monitor_low_power(void) {
    // 配置RTC每分钟唤醒
    configure_rtc_wakeup(60);
    
    uint8_t sample_count = 0;
    
    while (1) {
        // 快速采集温度
        float temp = read_temperature_fast();
        store_temperature(temp);
        sample_count++;
        
        // 每60次采样（1小时）上传一次
        if (sample_count >= 60) {
            upload_data();
            sample_count = 0;
        }
        
        // 进入停止模式，等待RTC唤醒
        enter_stop_mode();
    }
}

// 功耗分析：
// - 采集：5mA × 0.1秒 = 0.5mA·s
// - 上传：50mA × 2秒 = 100mA·s（每小时一次）
// - 停止模式：0.01mA × 59.9秒 = 0.599mA·s
// - 平均功耗：(0.5 + 0.599) / 60 + 100 / 3600 ≈ 0.046mA
// - 电池寿命：2000mAh / 0.046mA ≈ 43478小时 ≈ 5年
```

### 案例2: 门磁传感器

**需求**:
- 检测门的开关状态
- 状态变化时立即上报
- 纽扣电池供电，需要运行3年

**优化实现**:
```c
void door_sensor_low_power(void) {
    // 配置GPIO中断检测门状态变化
    configure_door_interrupt();
    
    // 初始状态上报
    report_door_status(get_door_status());
    
    while (1) {
        // 进入待机模式（最低功耗）
        enter_standby_mode();
        
        // 门状态变化时被唤醒（复位）
        // 重新初始化
        system_init();
        
        // 上报新状态
        report_door_status(get_door_status());
    }
}

// 功耗分析：
// - 待机模式：0.001mA
// - 唤醒上报：20mA × 0.5秒 = 10mA·s（假设每天10次）
// - 平均功耗：0.001mA + (10 × 10) / 86400 ≈ 0.0022mA
// - 电池寿命：220mAh / 0.0022mA ≈ 100000小时 ≈ 11年
```

### 案例3: 可穿戴设备

**需求**:
- 持续监测心率和步数
- 显示时间和数据
- 充电一次使用7天

**优化策略**:
```c
typedef enum {
    MODE_ACTIVE,      // 显示开启，高采样率
    MODE_NORMAL,      // 显示关闭，正常采样
    MODE_SLEEP        // 用户睡眠，低采样率
} DeviceMode_t;

DeviceMode_t current_mode = MODE_NORMAL;

void wearable_device_main(void) {
    while (1) {
        switch (current_mode) {
            case MODE_ACTIVE:
                // 高性能模式
                set_cpu_frequency(72000000);  // 72MHz
                enable_display();
                set_sensor_rate(100);  // 100Hz采样
                
                // 5秒无操作后切换到正常模式
                if (idle_time > 5000) {
                    current_mode = MODE_NORMAL;
                }
                break;
                
            case MODE_NORMAL:
                // 正常模式
                set_cpu_frequency(8000000);  // 8MHz
                disable_display();
                set_sensor_rate(25);  // 25Hz采样
                
                // 检测用户活动
                if (user_interaction()) {
                    current_mode = MODE_ACTIVE;
                } else if (is_sleep_time()) {
                    current_mode = MODE_SLEEP;
                }
                break;
                
            case MODE_SLEEP:
                // 睡眠模式
                set_cpu_frequency(1000000);  // 1MHz
                disable_display();
                set_sensor_rate(1);  // 1Hz采样
                
                // 检测用户醒来
                if (detect_wakeup()) {
                    current_mode = MODE_NORMAL;
                }
                break;
        }
        
        // 处理传感器数据
        process_sensor_data();
        
        // 进入睡眠等待下次采样
        enter_sleep_mode();
    }
}

// 功耗估算：
// - 活跃模式（1小时/天）：15mA
// - 正常模式（15小时/天）：2mA
// - 睡眠模式（8小时/天）：0.5mA
// - 平均功耗：(15×1 + 2×15 + 0.5×8) / 24 ≈ 2.29mA
// - 电池寿命：300mAh / 2.29mA ≈ 131小时 ≈ 5.5天
// - 通过优化可达到7天目标
```

### 案例4: 智能水表

**需求**:
- 每小时记录用水量
- 每天上传数据
- 电池供电10年

**优化实现**:
```c
void smart_water_meter(void) {
    // 使用脉冲计数器（硬件计数，无需CPU）
    configure_pulse_counter();
    
    // 配置RTC每小时唤醒
    configure_rtc_alarm(3600);
    
    uint8_t hour_count = 0;
    
    while (1) {
        // 读取脉冲计数（用水量）
        uint32_t pulses = read_pulse_counter();
        store_water_usage(pulses);
        reset_pulse_counter();
        
        hour_count++;
        
        // 每24小时上传一次
        if (hour_count >= 24) {
            upload_daily_data();
            hour_count = 0;
        }
        
        // 进入待机模式
        enter_standby_mode();
        
        // 1小时后被RTC唤醒
    }
}

// 功耗分析：
// - 待机模式：0.002mA
// - 每小时唤醒：5mA × 0.1秒 = 0.5mA·s
// - 每天上传：30mA × 3秒 = 90mA·s
// - 平均功耗：0.002 + 0.5/3600 + 90/86400 ≈ 0.0032mA
// - 电池寿命：2000mAh / 0.0032mA ≈ 625000小时 ≈ 71年
// - 实际考虑电池自放电，可达10年以上
```


## 步骤8: 功耗测试验证

### 8.1 测试环境搭建

**硬件连接**:
```
电源 → 电流表 → MCU VDD
         ↓
    数据记录设备
```

**测试工具配置**:
```c
// 测试辅助函数
typedef struct {
    const char *test_name;
    uint32_t duration_ms;
    float expected_current_mA;
} PowerTest_t;

void power_test_start(const char *name) {
    printf("\n=== Power Test: %s ===\n", name);
    printf("Starting test...\n");
    
    // 稳定一段时间
    HAL_Delay(100);
}

void power_test_end(float measured_current, float expected_current) {
    printf("Measured: %.3f mA\n", measured_current);
    printf("Expected: %.3f mA\n", expected_current);
    
    float error = fabs(measured_current - expected_current) / expected_current * 100;
    printf("Error: %.1f%%\n", error);
    
    if (error < 10.0f) {
        printf("Result: PASS\n");
    } else {
        printf("Result: FAIL\n");
    }
}
```

### 8.2 功耗测试用例

**测试1: 运行模式功耗**:
```c
void test_run_mode_power(void) {
    power_test_start("Run Mode");
    
    // 配置为最高性能
    set_cpu_frequency(72000000);
    enable_all_peripherals();
    
    // 运行一段时间
    uint32_t start = HAL_GetTick();
    while (HAL_GetTick() - start < 5000) {
        // 执行一些计算
        volatile uint32_t result = 0;
        for (int i = 0; i < 10000; i++) {
            result += i * i;
        }
    }
    
    // 测量电流（需要外部测量设备）
    float measured = measure_current();
    power_test_end(measured, 20.0f);  // 预期20mA
}

// 测试2: 睡眠模式功耗
void test_sleep_mode_power(void) {
    power_test_start("Sleep Mode");
    
    // 配置睡眠模式
    configure_sleep_mode();
    
    // 配置定时器5秒后唤醒
    configure_timer_wakeup(5000);
    
    // 进入睡眠
    enter_sleep_mode();
    
    // 测量电流
    float measured = measure_current();
    power_test_end(measured, 2.0f);  // 预期2mA
}

// 测试3: 停止模式功耗
void test_stop_mode_power(void) {
    power_test_start("Stop Mode");
    
    // 配置停止模式
    configure_stop_mode();
    
    // 配置RTC 5秒后唤醒
    configure_rtc_wakeup(5);
    
    // 进入停止模式
    enter_stop_mode();
    
    // 测量电流
    float measured = measure_current();
    power_test_end(measured, 0.05f);  // 预期50μA
}

// 测试4: 待机模式功耗
void test_standby_mode_power(void) {
    power_test_start("Standby Mode");
    
    // 配置待机模式
    configure_standby_mode();
    
    // 配置RTC闹钟5秒后唤醒
    configure_rtc_alarm_wakeup(5);
    
    // 进入待机模式（不会返回）
    enter_standby_mode();
}
```

**测试5: 外设功耗**:
```c
void test_peripheral_power(void) {
    // 测试GPIO功耗
    power_test_start("GPIO Toggle");
    enable_gpio();
    
    uint32_t start = HAL_GetTick();
    while (HAL_GetTick() - start < 5000) {
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_0);
        HAL_Delay(1);
    }
    
    float gpio_current = measure_current();
    power_test_end(gpio_current, 5.0f);
    
    // 测试UART功耗
    power_test_start("UART Transmit");
    enable_uart();
    
    start = HAL_GetTick();
    while (HAL_GetTick() - start < 5000) {
        HAL_UART_Transmit(&huart1, (uint8_t*)"Test", 4, 100);
        HAL_Delay(10);
    }
    
    float uart_current = measure_current();
    power_test_end(uart_current, 8.0f);
    
    // 测试ADC功耗
    power_test_start("ADC Conversion");
    enable_adc();
    
    start = HAL_GetTick();
    while (HAL_GetTick() - start < 5000) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 100);
        HAL_ADC_GetValue(&hadc1);
        HAL_Delay(10);
    }
    
    float adc_current = measure_current();
    power_test_end(adc_current, 6.0f);
}
```

### 8.3 长期稳定性测试

**电池寿命测试**:
```c
typedef struct {
    uint32_t test_duration_hours;
    float battery_capacity_mAh;
    float initial_voltage;
    float final_voltage;
    float avg_current_mA;
    float estimated_lifetime_hours;
} BatteryTest_t;

void battery_lifetime_test(void) {
    BatteryTest_t test = {0};
    
    printf("\n=== Battery Lifetime Test ===\n");
    
    // 记录初始状态
    test.battery_capacity_mAh = 2000.0f;
    test.initial_voltage = read_battery_voltage();
    
    printf("Initial voltage: %.2fV\n", test.initial_voltage);
    printf("Starting long-term test...\n");
    
    uint32_t start_time = HAL_GetTick();
    uint32_t sample_count = 0;
    float total_current = 0;
    
    // 运行24小时测试
    while ((HAL_GetTick() - start_time) < (24 * 3600 * 1000)) {
        // 正常工作循环
        normal_operation();
        
        // 每分钟采样一次电流
        if ((HAL_GetTick() % 60000) == 0) {
            float current = measure_current();
            total_current += current;
            sample_count++;
            
            printf("Sample %lu: %.3f mA\n", sample_count, current);
        }
    }
    
    // 记录最终状态
    test.test_duration_hours = 24;
    test.final_voltage = read_battery_voltage();
    test.avg_current_mA = total_current / sample_count;
    
    // 估算电池寿命
    test.estimated_lifetime_hours = test.battery_capacity_mAh / test.avg_current_mA;
    
    printf("\n=== Test Results ===\n");
    printf("Test duration: %lu hours\n", test.test_duration_hours);
    printf("Initial voltage: %.2fV\n", test.initial_voltage);
    printf("Final voltage: %.2fV\n", test.final_voltage);
    printf("Voltage drop: %.2fV\n", test.initial_voltage - test.final_voltage);
    printf("Average current: %.3f mA\n", test.avg_current_mA);
    printf("Estimated lifetime: %.1f hours (%.1f days)\n",
           test.estimated_lifetime_hours,
           test.estimated_lifetime_hours / 24);
}
```

**温度影响测试**:
```c
void temperature_power_test(void) {
    printf("\n=== Temperature vs Power Test ===\n");
    
    int8_t temperatures[] = {-20, 0, 25, 50, 85};
    
    for (int i = 0; i < 5; i++) {
        printf("\nTemperature: %d°C\n", temperatures[i]);
        
        // 等待温度稳定（实际需要温箱）
        printf("Waiting for temperature stabilization...\n");
        HAL_Delay(60000);
        
        // 测量不同模式的功耗
        printf("Run mode: ");
        float run_current = test_run_mode_current();
        printf("%.2f mA\n", run_current);
        
        printf("Sleep mode: ");
        float sleep_current = test_sleep_mode_current();
        printf("%.2f mA\n", sleep_current);
        
        printf("Stop mode: ");
        float stop_current = test_stop_mode_current();
        printf("%.3f mA\n", stop_current);
    }
}
```

### 8.4 功耗优化验证

**优化前后对比**:
```c
typedef struct {
    const char *scenario;
    float before_mA;
    float after_mA;
    float improvement_percent;
} OptimizationResult_t;

void compare_optimization_results(void) {
    OptimizationResult_t results[] = {
        {"Idle state", 20.0f, 0.05f, 0},
        {"Sensor reading", 15.0f, 5.0f, 0},
        {"Data transmission", 50.0f, 30.0f, 0},
        {"Display update", 25.0f, 15.0f, 0}
    };
    
    int count = sizeof(results) / sizeof(results[0]);
    
    printf("\n=== Optimization Results ===\n");
    printf("%-20s Before(mA)  After(mA)  Improvement\n", "Scenario");
    printf("--------------------------------------------------------\n");
    
    for (int i = 0; i < count; i++) {
        results[i].improvement_percent = 
            (results[i].before_mA - results[i].after_mA) / 
            results[i].before_mA * 100;
        
        printf("%-20s %9.2f  %9.2f  %10.1f%%\n",
               results[i].scenario,
               results[i].before_mA,
               results[i].after_mA,
               results[i].improvement_percent);
    }
    
    // 计算总体改善
    float total_before = 0, total_after = 0;
    for (int i = 0; i < count; i++) {
        total_before += results[i].before_mA;
        total_after += results[i].after_mA;
    }
    
    float overall_improvement = (total_before - total_after) / total_before * 100;
    
    printf("--------------------------------------------------------\n");
    printf("Overall improvement: %.1f%%\n", overall_improvement);
}
```


## 故障排除

### 问题1: 无法进入低功耗模式

**现象**:
- 调用睡眠函数后立即返回
- 功耗没有明显降低

**可能原因和解决方法**:

**1. 中断未正确配置**:
```c
// 检查中断配置
void debug_interrupt_config(void) {
    printf("Checking interrupt configuration...\n");
    
    // 检查NVIC使能状态
    if (NVIC_GetEnableIRQ(EXTI0_IRQn)) {
        printf("EXTI0 interrupt enabled\n");
    } else {
        printf("WARNING: EXTI0 interrupt not enabled\n");
        HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    }
    
    // 检查中断优先级
    uint32_t priority = NVIC_GetPriority(EXTI0_IRQn);
    printf("EXTI0 priority: %lu\n", priority);
}
```

**2. 外设时钟未关闭**:
```c
// 检查外设时钟状态
void debug_peripheral_clocks(void) {
    printf("Checking peripheral clocks...\n");
    
    if (__HAL_RCC_GPIOA_IS_CLK_ENABLED()) {
        printf("GPIOA clock enabled\n");
    }
    if (__HAL_RCC_USART1_IS_CLK_ENABLED()) {
        printf("USART1 clock enabled\n");
    }
    if (__HAL_RCC_TIM2_IS_CLK_ENABLED()) {
        printf("TIM2 clock enabled\n");
    }
    
    // 禁用不需要的时钟
    disable_unused_peripherals();
}
```

**3. 调试器连接**:
```c
// 调试器会阻止进入低功耗模式
void disable_debug_in_low_power(void) {
    // 在停止和待机模式下禁用调试
    __HAL_DBGMCU_FREEZE_IWDG();
    __HAL_DBGMCU_FREEZE_WWDG();
    
    // 完全禁用调试（生产环境）
    #ifdef PRODUCTION
    DBGMCU->CR = 0;
    #endif
}
```

### 问题2: 从低功耗模式唤醒失败

**现象**:
- 系统进入低功耗模式后无法唤醒
- 需要复位才能恢复

**诊断方法**:
```c
// 检查唤醒源配置
void debug_wakeup_sources(void) {
    printf("Checking wakeup sources...\n");
    
    // 检查RTC唤醒
    if (HAL_RTCEx_GetWakeUpTimer(&hrtc) != HAL_OK) {
        printf("ERROR: RTC wakeup not configured\n");
    } else {
        printf("RTC wakeup configured\n");
    }
    
    // 检查EXTI唤醒
    if (HAL_GPIO_ReadPin(WAKEUP_GPIO_Port, WAKEUP_Pin)) {
        printf("Wakeup pin HIGH\n");
    } else {
        printf("Wakeup pin LOW\n");
    }
    
    // 检查唤醒标志
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_WU)) {
        printf("Wakeup flag set\n");
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    }
}
```

**解决方法**:
```c
// 确保唤醒源正确配置
void configure_reliable_wakeup(void) {
    // 1. 配置外部中断唤醒
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = WAKEUP_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(WAKEUP_GPIO_Port, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    // 2. 配置RTC唤醒作为备份
    HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, 60, RTC_WAKEUPCLOCK_CK_SPRE_16BITS);
    
    // 3. 清除所有唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
}
```

### 问题3: 功耗高于预期

**诊断步骤**:
```c
void diagnose_high_power_consumption(void) {
    printf("\n=== Power Consumption Diagnosis ===\n");
    
    // 1. 检查时钟配置
    printf("System clock: %lu Hz\n", HAL_RCC_GetSysClockFreq());
    printf("HCLK: %lu Hz\n", HAL_RCC_GetHCLKFreq());
    printf("PCLK1: %lu Hz\n", HAL_RCC_GetPCLK1Freq());
    printf("PCLK2: %lu Hz\n", HAL_RCC_GetPCLK2Freq());
    
    // 2. 检查外设状态
    debug_peripheral_clocks();
    
    // 3. 检查GPIO配置
    printf("\nChecking GPIO configuration...\n");
    check_gpio_configuration();
    
    // 4. 检查中断状态
    printf("\nChecking interrupt status...\n");
    debug_interrupt_config();
    
    // 5. 测量各部分功耗
    printf("\nMeasuring component power...\n");
    measure_component_power();
}

void check_gpio_configuration(void) {
    // 检查是否有浮空输入
    // 浮空输入会导致额外功耗
    
    // 示例：检查GPIOA
    for (int pin = 0; pin < 16; pin++) {
        uint32_t mode = (GPIOA->MODER >> (pin * 2)) & 0x3;
        uint32_t pupd = (GPIOA->PUPDR >> (pin * 2)) & 0x3;
        
        if (mode == 0 && pupd == 0) {  // 输入模式且无上下拉
            printf("WARNING: PA%d is floating input\n", pin);
        }
    }
}

void measure_component_power(void) {
    float baseline = measure_current();
    printf("Baseline current: %.3f mA\n", baseline);
    
    // 逐个使能外设并测量
    __HAL_RCC_GPIOA_CLK_ENABLE();
    float with_gpioa = measure_current();
    printf("With GPIOA: %.3f mA (+%.3f mA)\n", 
           with_gpioa, with_gpioa - baseline);
    
    __HAL_RCC_USART1_CLK_ENABLE();
    float with_uart = measure_current();
    printf("With UART1: %.3f mA (+%.3f mA)\n",
           with_uart, with_uart - with_gpioa);
    
    // 继续测试其他外设...
}
```

### 问题4: 电池寿命不符合预期

**分析方法**:
```c
void analyze_battery_lifetime(void) {
    printf("\n=== Battery Lifetime Analysis ===\n");
    
    // 1. 测量实际工作周期
    typedef struct {
        const char *state;
        float current_mA;
        float time_percent;
        float energy_mAh;
    } StateAnalysis_t;
    
    StateAnalysis_t states[] = {
        {"Active", 20.0f, 5.0f, 0},      // 5%时间活跃
        {"Idle", 2.0f, 10.0f, 0},        // 10%时间空闲
        {"Sleep", 0.05f, 85.0f, 0}       // 85%时间睡眠
    };
    
    float total_energy = 0;
    
    printf("%-10s Current(mA)  Time(%%)  Energy(mAh/day)\n", "State");
    printf("------------------------------------------------\n");
    
    for (int i = 0; i < 3; i++) {
        // 计算每天的能量消耗
        states[i].energy_mAh = states[i].current_mA * 
                               (states[i].time_percent / 100.0f) * 24;
        total_energy += states[i].energy_mAh;
        
        printf("%-10s %10.2f  %7.1f  %15.2f\n",
               states[i].state,
               states[i].current_mA,
               states[i].time_percent,
               states[i].energy_mAh);
    }
    
    printf("------------------------------------------------\n");
    printf("Total energy per day: %.2f mAh\n", total_energy);
    
    // 2. 计算电池寿命
    float battery_capacity = 2000.0f;  // mAh
    float lifetime_days = battery_capacity / total_energy;
    
    printf("Battery capacity: %.0f mAh\n", battery_capacity);
    printf("Estimated lifetime: %.1f days (%.1f months)\n",
           lifetime_days, lifetime_days / 30);
    
    // 3. 考虑电池自放电
    float self_discharge_percent = 2.0f;  // 每月2%
    float effective_capacity = battery_capacity * 
                              (1 - self_discharge_percent / 100 * (lifetime_days / 30));
    float actual_lifetime = effective_capacity / total_energy;
    
    printf("With self-discharge: %.1f days (%.1f months)\n",
           actual_lifetime, actual_lifetime / 30);
}
```

**优化建议**:
```c
void suggest_power_optimizations(void) {
    printf("\n=== Optimization Suggestions ===\n");
    
    float current_avg = measure_average_current();
    
    if (current_avg > 10.0f) {
        printf("1. Current too high (%.2f mA)\n", current_avg);
        printf("   - Check if CPU frequency can be reduced\n");
        printf("   - Verify all unused peripherals are disabled\n");
        printf("   - Consider using lower power mode\n");
    }
    
    if (current_avg > 1.0f && current_avg < 10.0f) {
        printf("2. Moderate power consumption (%.2f mA)\n", current_avg);
        printf("   - Use sleep mode instead of active waiting\n");
        printf("   - Batch operations to reduce active time\n");
        printf("   - Use DMA for data transfers\n");
    }
    
    if (current_avg < 1.0f) {
        printf("3. Good power efficiency (%.2f mA)\n", current_avg);
        printf("   - Consider stop mode for longer idle periods\n");
        printf("   - Optimize wakeup frequency\n");
        printf("   - Use standby mode if possible\n");
    }
}
```


## 最佳实践总结

### 设计阶段

1. **功耗预算规划**
   - 明确电池容量和目标寿命
   - 分析各状态的时间占比
   - 计算平均功耗预算
   - 预留20-30%安全余量

2. **选择合适的MCU**
   - 评估低功耗模式支持
   - 考虑外设功耗
   - 查看数据手册的功耗数据
   - 选择合适的封装和工艺

3. **硬件设计考虑**
   - 使用低功耗外围器件
   - 添加电源开关控制
   - 合理设计电源管理电路
   - 考虑电池类型和容量

### 实现阶段

1. **时钟管理**
   ```c
   // 使用最低可行频率
   // 动态调整时钟
   // 关闭未使用的时钟
   ```

2. **外设管理**
   ```c
   // 按需使能外设
   // 使用完立即禁用
   // 配置GPIO为低功耗状态
   ```

3. **低功耗模式**
   ```c
   // 尽可能使用深度睡眠
   // 优化唤醒频率
   // 快速执行任务后睡眠
   ```

4. **软件架构**
   ```c
   // 事件驱动而非轮询
   // 批处理操作
   // 延迟非关键任务
   ```

### 测试阶段

1. **功耗测量**
   - 使用专业测量设备
   - 测量所有工作模式
   - 记录详细数据
   - 分析功耗分布

2. **长期测试**
   - 24小时以上连续测试
   - 不同温度下测试
   - 验证电池寿命
   - 检查稳定性

3. **优化验证**
   - 对比优化前后
   - 验证功能正确性
   - 确认满足需求
   - 记录优化效果

### 维护阶段

1. **持续监控**
   ```c
   // 记录功耗数据
   // 监控电池电压
   // 检测异常功耗
   ```

2. **版本对比**
   - 每个版本测试功耗
   - 对比历史数据
   - 及时发现退化
   - 保持优化水平

3. **用户反馈**
   - 收集实际使用数据
   - 分析电池寿命
   - 根据反馈优化
   - 持续改进

## 总结

通过本教程，你已经学习了:

- ✅ 嵌入式系统功耗的来源和特点
- ✅ 功耗测量和分析方法
- ✅ MCU低功耗模式的配置和使用
- ✅ 时钟和电压的动态调节
- ✅ 外设功耗优化技术
- ✅ 低功耗软件架构设计
- ✅ 实际案例和测试验证方法

**关键要点**:

1. **理解功耗模型**: 知道功耗来自哪里
2. **测量是基础**: 没有测量就没有优化
3. **选择合适的模式**: 根据需求选择低功耗模式
4. **优化时钟和电压**: 使用最低可行的频率和电压
5. **管理外设**: 按需使能，用完禁用
6. **事件驱动**: 避免轮询，使用中断
7. **批处理**: 减少唤醒次数
8. **持续验证**: 测试和监控功耗

**优化原则**:

- 先测量，再优化
- 优先优化占比大的部分
- 在功耗和性能之间平衡
- 保持功能正确性
- 考虑用户体验

**实践建议**:

- 从项目开始就关注功耗
- 建立功耗预算和目标
- 定期测量和分析
- 使用自动化测试
- 记录优化决策和效果

## 下一步学习

建议继续学习以下内容:

### 相关主题
- [内存使用优化技术](./01-memory-optimization.html) - 内存优化
- [代码优化基础原则](../beginner/01-code-optimization-basics.html) - 优化思维
- [编译器优化选项使用](../beginner/02-compiler-optimization.html) - 编译器技巧

### 进阶主题
- [算法复杂度与性能分析](./03-algorithm-complexity.html) - 算法优化
- [实时性能优化技术](../advanced/01-real-time-optimization.html) - 实时系统
- [性能分析工具开发](../advanced/02-performance-analysis-tool.html) - 工具开发

### 深入学习
- 电源管理IC（PMIC）使用
- 能量收集技术
- 超低功耗设计
- 电池管理系统

## 参考资料

### 芯片厂商文档
1. [STM32 Low-Power Modes](https://www.st.com/resource/en/application_note/an4365-using-stm32f4-mcu-power-modes-with-best-dynamic-efficiency-stmicroelectronics.pdf)
2. [ARM Cortex-M Power Management](https://developer.arm.com/documentation/ddi0337/e/power-management)
3. [Nordic nRF52 Power Profiler](https://www.nordicsemi.com/Products/Development-tools/Power-Profiler-Kit-2)

### 推荐阅读
1. "Low-Power Design Essentials" - Jan M. Rabaey
2. "Embedded Systems Architecture" - Tammy Noergaard
3. "Making Embedded Systems" - Elecia White

### 在线资源
1. [Embedded Artistry - Power Management](https://embeddedartistry.com/blog/tag/power/)
2. [EEVblog - Power Measurement](https://www.eevblog.com/)
3. [ARM Community - Low Power](https://community.arm.com/developer/ip-products/processors/f/cortex-m-forum)

### 工具和软件
1. [STM32CubeMX Power Consumption Calculator](https://www.st.com/en/development-tools/stm32cubemx.html)
2. [Joulescope Precision DC Energy Analyzer](https://www.joulescope.com/)
3. [Nordic Power Profiler Kit](https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2)

### 标准和指南
1. [IEC 61000-3-2 Power Quality](https://webstore.iec.ch/publication/4149)
2. [Energy Star Program Requirements](https://www.energystar.gov/)
3. [Battery University](https://batteryuniversity.com/)

---

**练习建议**:
1. 测量开发板在不同模式下的功耗
2. 实现一个低功耗的传感器节点
3. 优化现有项目的功耗
4. 设计一个电池供电的应用
5. 编写功耗监控和分析工具

**版本历史**:
- v1.0 (2024-01-15): 初始版本发布

**许可证**：本文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议
