---
# 基础信息
title: "电源模式切换与唤醒源配置"
description: "深入讲解嵌入式系统的电源模式切换技术，包括多级睡眠模式、RTC唤醒、外部中断唤醒、唤醒时间优化和状态保存恢复，帮助开发者实现高效的低功耗管理"
slug: "power-mode-switching-wakeup"

# 分类信息
domain: "01-hardware-layer"
module: "03-power-management"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 电源模式
  - 唤醒源
  - 睡眠管理
  - RTC唤醒
  - 低功耗设计
prerequisites:
  - "01-power-design-basics"
  - "02-low-power-design"
  - "05-power-measurement"
related_contents:
  - "02-dynamic-power-management"
  - "01-bms-design"

# 学习信息
estimated_time: 70
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
  - 电源模式切换
  - 睡眠模式
  - 唤醒源配置
  - RTC唤醒
  - 外部中断唤醒
  - 状态保存
cover_image: ""
---

# 电源模式切换与唤醒源配置

## 概述

电源模式切换是嵌入式系统低功耗设计的核心技术之一。通过在不同工作负载下切换到合适的电源模式，系统可以在保证功能的同时大幅降低功耗。本教程将深入讲解多级睡眠模式、各种唤醒源的配置方法、唤醒时间优化技术以及状态保存恢复策略。

### 什么是电源模式切换

电源模式切换是指根据系统的工作状态，在不同的功耗模式之间进行切换的技术。典型的电源模式包括：

1. **运行模式 (Run Mode)**：
   - CPU全速运行
   - 所有外设可用
   - 功耗最高
   - 响应最快

2. **睡眠模式 (Sleep Mode)**：
   - CPU停止，外设运行
   - 中断可唤醒
   - 功耗中等
   - 唤醒快速

3. **停止模式 (Stop Mode)**：
   - CPU和大部分外设停止
   - 保持RAM数据
   - 功耗较低
   - 唤醒稍慢

4. **待机模式 (Standby Mode)**：
   - 几乎所有电路关闭
   - 仅保持RTC和备份寄存器
   - 功耗极低
   - 唤醒最慢


### 电源模式的重要性

```
为什么需要电源模式切换：

1. 延长电池寿命
   - 运行模式：50-100 mA
   - 睡眠模式：5-10 mA
   - 停止模式：10-100 μA
   - 待机模式：1-10 μA
   - 合理切换可延长电池寿命10-100倍

2. 降低系统功耗
   - 减少发热
   - 提高可靠性
   - 降低运营成本
   - 符合环保要求

3. 优化用户体验
   - 快速响应
   - 长续航时间
   - 静音运行
   - 温度适宜

4. 满足应用需求
   - 物联网节点：长期待机
   - 可穿戴设备：频繁唤醒
   - 传感器网络：定时采集
   - 移动设备：按需工作
```

### 应用场景

- **物联网传感器**：定时采集数据，大部分时间处于睡眠状态
- **可穿戴设备**：待机时低功耗，交互时快速响应
- **智能家居**：待命状态功耗极低，接收指令快速唤醒
- **便携设备**：电池供电，需要最大化续航时间
- **工业监控**：长期运行，降低能耗和发热



## 第一部分：多级睡眠模式详解

### STM32电源模式架构

**STM32F1系列电源模式**：

```
电源模式层次结构：

┌─────────────────────────────────────────────────────┐
│                  运行模式 (Run)                      │
│  - CPU: 运行                                         │
│  - 时钟: 全部使能                                    │
│  - 外设: 全部可用                                    │
│  - 功耗: 50-100 mA @ 72MHz                          │
│  - 唤醒: N/A                                         │
└─────────────────────────────────────────────────────┘
                      ↓ WFI/WFE
┌─────────────────────────────────────────────────────┐
│                  睡眠模式 (Sleep)                    │
│  - CPU: 停止                                         │
│  - 时钟: 运行                                        │
│  - 外设: 运行                                        │
│  - 功耗: 5-10 mA                                     │
│  - 唤醒: 任意中断 (<1μs)                            │
└─────────────────────────────────────────────────────┘
                      ↓ PDDS=0
┌─────────────────────────────────────────────────────┐
│                  停止模式 (Stop)                     │
│  - CPU: 停止                                         │
│  - 时钟: HSI/HSE停止                                │
│  - 外设: 部分停止                                    │
│  - 功耗: 10-100 μA                                   │
│  - 唤醒: EXTI, RTC (5-10μs)                         │
└─────────────────────────────────────────────────────┘
                      ↓ PDDS=1
┌─────────────────────────────────────────────────────┐
│                  待机模式 (Standby)                  │
│  - CPU: 关闭                                         │
│  - 时钟: 全部关闭                                    │
│  - 外设: 关闭（除RTC）                              │
│  - 功耗: 1-10 μA                                     │
│  - 唤醒: WKUP, RTC, RSTn (>1ms)                     │
└─────────────────────────────────────────────────────┘

模式选择原则：
1. 短时间空闲（<1ms）：睡眠模式
2. 中等时间空闲（1ms-1s）：停止模式
3. 长时间空闲（>1s）：待机模式
4. 需要保持外设状态：睡眠/停止模式
5. 极致低功耗：待机模式
```


### 睡眠模式实现

**睡眠模式特点**：
- CPU时钟停止，外设时钟继续运行
- 任何中断或事件都可以唤醒
- 唤醒时间极短（<1μs）
- 适合短时间等待

```c
/**
 * @file    sleep_mode.c
 * @brief   睡眠模式实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  进入睡眠模式
 * @param  sleep_on_exit: 是否在中断返回后继续睡眠
 * @retval None
 * 
 * @note   睡眠模式特性：
 *         - CPU停止，外设继续运行
 *         - 任意中断可唤醒
 *         - 唤醒后从停止处继续执行
 *         - 功耗：约5-10mA
 */
void Enter_SleepMode(bool sleep_on_exit) {
    printf("进入睡眠模式...\n");
    
    // 记录进入时间
    uint32_t enter_time = HAL_GetTick();
    
    if (sleep_on_exit) {
        // 设置SLEEPONEXIT位，中断返回后自动进入睡眠
        // 适用于中断驱动的应用
        HAL_PWR_EnableSleepOnExit();
    }
    
    // 进入睡眠模式
    // WFI: Wait For Interrupt
    // WFE: Wait For Event
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // 唤醒后从这里继续执行
    uint32_t wake_time = HAL_GetTick();
    uint32_t sleep_duration = wake_time - enter_time;
    
    printf("从睡眠模式唤醒，睡眠时间: %lu ms\n", sleep_duration);
}

/**
 * @brief  睡眠模式示例：等待UART接收
 */
void Sleep_Example_UART_Wait(void) {
    printf("等待UART数据，进入睡眠模式\n");
    
    // 使能UART接收中断
    HAL_UART_Receive_IT(&huart1, rx_buffer, 1);
    
    // 进入睡眠模式，等待UART中断唤醒
    Enter_SleepMode(false);
    
    // UART中断唤醒后继续执行
    printf("UART数据接收完成\n");
}

/**
 * @brief  睡眠模式示例：定时器周期唤醒
 */
void Sleep_Example_Timer_Periodic(void) {
    printf("启动定时器周期唤醒\n");
    
    // 配置定时器，每100ms产生一次中断
    HAL_TIM_Base_Start_IT(&htim2);
    
    while (1) {
        // 进入睡眠模式
        Enter_SleepMode(false);
        
        // 定时器中断唤醒后执行任务
        printf("定时器唤醒，执行周期任务\n");
        
        // 执行实际任务
        // ...
    }
}
```

### 停止模式实现

**停止模式特点**：
- CPU和大部分外设时钟停止
- 保持SRAM和寄存器内容
- 可通过EXTI线或RTC唤醒
- 唤醒时间约5-10μs
- 适合中等时间等待

```c
/**
 * @file    stop_mode.c
 * @brief   停止模式实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  进入停止模式
 * @param  regulator: 稳压器模式
 *         - PWR_MAINREGULATOR_ON: 主稳压器开启
 *         - PWR_LOWPOWERREGULATOR_ON: 低功耗稳压器开启
 * @retval None
 * 
 * @note   停止模式特性：
 *         - CPU和大部分外设停止
 *         - 保持SRAM和寄存器
 *         - EXTI和RTC可唤醒
 *         - 功耗：10-100μA
 *         - 唤醒后需要重新配置时钟
 */
void Enter_StopMode(uint32_t regulator) {
    printf("进入停止模式...\n");
    
    // 记录进入时间（使用RTC，因为SysTick会停止）
    uint32_t enter_time = HAL_GetTick();
    
    // 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // 进入停止模式
    HAL_PWR_EnterSTOPMode(regulator, PWR_STOPENTRY_WFI);
    
    // 唤醒后从这里继续执行
    // 注意：此时系统时钟为HSI (8MHz)，需要重新配置
    
    // 重新配置系统时钟到72MHz
    SystemClock_Config();
    
    uint32_t wake_time = HAL_GetTick();
    uint32_t sleep_duration = wake_time - enter_time;
    
    printf("从停止模式唤醒，睡眠时间: %lu ms\n", sleep_duration);
}

/**
 * @brief  停止模式示例：外部中断唤醒
 */
void Stop_Example_EXTI_Wakeup(void) {
    printf("配置外部中断唤醒源\n");
    
    // 配置PA0为外部中断（按键）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIOA时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    // 配置PA0
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;  // 上升沿触发
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 使能EXTI0中断
    HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    
    printf("按下按键唤醒系统\n");
    
    // 进入停止模式
    Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
    
    printf("按键按下，系统唤醒\n");
}

/**
 * @brief  外部中断回调函数
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        // PA0中断，系统将从停止模式唤醒
        printf("EXTI0中断触发\n");
    }
}
```


### 待机模式实现

**待机模式特点**：
- 几乎所有电路关闭
- 仅保持RTC和备份寄存器
- 功耗极低（1-10μA）
- 唤醒时间较长（>1ms）
- 唤醒后相当于复位

```c
/**
 * @file    standby_mode.c
 * @brief   待机模式实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  进入待机模式
 * @param  None
 * @retval None
 * 
 * @note   待机模式特性：
 *         - 几乎所有电路关闭
 *         - 仅保持RTC和备份寄存器
 *         - 功耗：1-10μA
 *         - 唤醒后相当于系统复位
 *         - 需要在备份寄存器中保存状态
 */
void Enter_StandbyMode(void) {
    printf("进入待机模式...\n");
    
    // 使能PWR时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 在备份寄存器中保存标志，表示从待机模式唤醒
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, 0xA5A5);
    
    // 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
    
    // 使能WKUP引脚唤醒功能
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // 进入待机模式
    HAL_PWR_EnterSTANDBYMode();
    
    // 注意：这里的代码不会执行
    // 唤醒后系统会复位，从main函数开始执行
}

/**
 * @brief  检查是否从待机模式唤醒
 * @retval true: 从待机模式唤醒, false: 正常上电
 */
bool Check_StandbyWakeup(void) {
    // 使能PWR和备份域时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_RCC_BKP_CLK_ENABLE();
    
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 检查待机标志
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB) != RESET) {
        // 清除待机标志
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        
        // 检查备份寄存器标志
        uint32_t backup_flag = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR1);
        if (backup_flag == 0xA5A5) {
            printf("从待机模式唤醒\n");
            return true;
        }
    }
    
    printf("正常上电启动\n");
    return false;
}

/**
 * @brief  待机模式示例：定时唤醒
 */
void Standby_Example_RTC_Wakeup(void) {
    printf("配置RTC定时唤醒\n");
    
    // 配置RTC闹钟，10秒后唤醒
    RTC_AlarmTypeDef sAlarm = {0};
    
    // 获取当前时间
    RTC_TimeTypeDef sTime;
    HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
    
    // 设置闹钟时间（当前时间+10秒）
    sAlarm.AlarmTime.Hours = sTime.Hours;
    sAlarm.AlarmTime.Minutes = sTime.Minutes;
    sAlarm.AlarmTime.Seconds = (sTime.Seconds + 10) % 60;
    sAlarm.Alarm = RTC_ALARM_A;
    
    HAL_RTC_SetAlarm_IT(&hrtc, &sAlarm, RTC_FORMAT_BIN);
    
    printf("10秒后RTC唤醒系统\n");
    
    // 进入待机模式
    Enter_StandbyMode();
}

/**
 * @brief  待机模式示例：WKUP引脚唤醒
 */
void Standby_Example_WKUP_Pin(void) {
    printf("配置WKUP引脚唤醒\n");
    printf("按下WKUP按键唤醒系统\n");
    
    // 进入待机模式
    // WKUP引脚（PA0）上升沿可唤醒
    Enter_StandbyMode();
}

/**
 * @brief  主函数中的待机模式处理
 */
void Standby_Main_Handler(void) {
    // 检查是否从待机模式唤醒
    if (Check_StandbyWakeup()) {
        // 从待机模式唤醒，恢复状态
        printf("恢复系统状态\n");
        
        // 从备份寄存器读取保存的数据
        uint32_t saved_data = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR2);
        printf("恢复的数据: 0x%08lX\n", saved_data);
        
        // 清除备份寄存器标志
        HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, 0);
    } else {
        // 正常上电，初始化系统
        printf("系统初始化\n");
    }
}
```



## 第二部分：RTC唤醒配置

### RTC基础配置

**RTC (Real-Time Clock)** 是一个独立的定时器，即使在停止和待机模式下也能继续运行，是实现定时唤醒的关键。

```c
/**
 * @file    rtc_wakeup.c
 * @brief   RTC唤醒配置实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

RTC_HandleTypeDef hrtc;

/**
 * @brief  初始化RTC
 * @retval None
 */
void RTC_Init(void) {
    // 使能PWR和BKP时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_RCC_BKP_CLK_ENABLE();
    
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 配置RTC时钟源为LSE（32.768kHz外部晶振）
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_LSE;
    RCC_OscInitStruct.LSEState = RCC_LSE_ON;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // 选择RTC时钟源
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};
    PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC;
    PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
    HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit);
    
    // 使能RTC时钟
    __HAL_RCC_RTC_ENABLE();
    
    // 配置RTC
    hrtc.Instance = RTC;
    hrtc.Init.AsynchPrediv = RTC_AUTO_1_SECOND;
    HAL_RTC_Init(&hrtc);
    
    printf("RTC初始化完成\n");
}

/**
 * @brief  配置RTC闹钟唤醒
 * @param  seconds: 多少秒后唤醒
 * @retval None
 */
void RTC_SetAlarmWakeup(uint32_t seconds) {
    RTC_AlarmTypeDef sAlarm = {0};
    RTC_TimeTypeDef sTime;
    RTC_DateTypeDef sDate;
    
    // 获取当前时间
    HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
    HAL_RTC_GetDate(&hrtc, &sDate, RTC_FORMAT_BIN);
    
    // 计算唤醒时间
    uint32_t total_seconds = sTime.Hours * 3600 + 
                             sTime.Minutes * 60 + 
                             sTime.Seconds + seconds;
    
    sAlarm.AlarmTime.Hours = (total_seconds / 3600) % 24;
    sAlarm.AlarmTime.Minutes = (total_seconds / 60) % 60;
    sAlarm.AlarmTime.Seconds = total_seconds % 60;
    sAlarm.Alarm = RTC_ALARM_A;
    
    // 设置闹钟
    HAL_RTC_SetAlarm_IT(&hrtc, &sAlarm, RTC_FORMAT_BIN);
    
    printf("RTC闹钟设置: %d秒后唤醒\n", seconds);
    printf("唤醒时间: %02d:%02d:%02d\n",
           sAlarm.AlarmTime.Hours,
           sAlarm.AlarmTime.Minutes,
           sAlarm.AlarmTime.Seconds);
}

/**
 * @brief  RTC闹钟中断回调
 */
void HAL_RTC_AlarmAEventCallback(RTC_HandleTypeDef *hrtc) {
    printf("RTC闹钟触发，系统唤醒\n");
}

/**
 * @brief  RTC周期唤醒示例
 */
void RTC_Periodic_Wakeup_Example(void) {
    printf("RTC周期唤醒示例\n");
    
    uint32_t wakeup_count = 0;
    
    while (1) {
        // 设置10秒后唤醒
        RTC_SetAlarmWakeup(10);
        
        printf("进入停止模式，等待RTC唤醒...\n");
        
        // 进入停止模式
        Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
        
        // RTC唤醒后继续执行
        wakeup_count++;
        printf("第 %lu 次唤醒\n", wakeup_count);
        
        // 执行周期任务
        // 例如：读取传感器数据
        printf("执行数据采集任务\n");
        
        // 任务完成后继续睡眠
    }
}
```


### RTC秒中断唤醒

```c
/**
 * @brief  配置RTC秒中断
 * @retval None
 * 
 * @note   RTC秒中断每秒触发一次
 *         可用于精确的周期唤醒
 */
void RTC_SecondInterrupt_Config(void) {
    // 使能RTC秒中断
    __HAL_RTC_SECOND_ENABLE_IT(&hrtc, RTC_IT_SEC);
    
    // 配置NVIC
    HAL_NVIC_SetPriority(RTC_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(RTC_IRQn);
    
    printf("RTC秒中断配置完成\n");
}

/**
 * @brief  RTC秒中断回调
 */
void HAL_RTCEx_RTCEventCallback(RTC_HandleTypeDef *hrtc) {
    static uint32_t second_count = 0;
    second_count++;
    
    printf("RTC秒中断: %lu 秒\n", second_count);
}

/**
 * @brief  RTC秒中断唤醒示例
 */
void RTC_Second_Wakeup_Example(void) {
    printf("RTC秒中断唤醒示例\n");
    
    // 配置RTC秒中断
    RTC_SecondInterrupt_Config();
    
    while (1) {
        printf("进入停止模式，每秒唤醒一次\n");
        
        // 进入停止模式
        Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
        
        // 每秒唤醒一次，执行任务
        printf("秒中断唤醒，执行任务\n");
    }
}
```



## 第三部分：外部中断唤醒

### EXTI配置

**EXTI (External Interrupt)** 可以在停止模式下唤醒系统，支持GPIO、RTC、USB等多种唤醒源。

```c
/**
 * @file    exti_wakeup.c
 * @brief   外部中断唤醒配置
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  配置GPIO外部中断唤醒
 * @param  GPIO_Port: GPIO端口
 * @param  GPIO_Pin: GPIO引脚
 * @param  trigger: 触发方式
 * @retval None
 */
void EXTI_GPIO_Wakeup_Config(GPIO_TypeDef* GPIO_Port, uint16_t GPIO_Pin, 
                              uint32_t trigger) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIO时钟
    if (GPIO_Port == GPIOA) {
        __HAL_RCC_GPIOA_CLK_ENABLE();
    } else if (GPIO_Port == GPIOB) {
        __HAL_RCC_GPIOB_CLK_ENABLE();
    } else if (GPIO_Port == GPIOC) {
        __HAL_RCC_GPIOC_CLK_ENABLE();
    }
    
    // 配置GPIO为外部中断模式
    GPIO_InitStruct.Pin = GPIO_Pin;
    GPIO_InitStruct.Mode = trigger;  // GPIO_MODE_IT_RISING/FALLING/RISING_FALLING
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIO_Port, &GPIO_InitStruct);
    
    // 配置NVIC
    IRQn_Type IRQn;
    if (GPIO_Pin == GPIO_PIN_0) {
        IRQn = EXTI0_IRQn;
    } else if (GPIO_Pin == GPIO_PIN_1) {
        IRQn = EXTI1_IRQn;
    } else if (GPIO_Pin <= GPIO_PIN_4) {
        IRQn = EXTI2_IRQn + (GPIO_Pin - GPIO_PIN_2);
    } else if (GPIO_Pin <= GPIO_PIN_9) {
        IRQn = EXTI9_5_IRQn;
    } else {
        IRQn = EXTI15_10_IRQn;
    }
    
    HAL_NVIC_SetPriority(IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(IRQn);
    
    printf("EXTI唤醒配置完成: GPIO引脚 %d\n", GPIO_Pin);
}

/**
 * @brief  多按键唤醒示例
 */
void EXTI_MultiButton_Wakeup_Example(void) {
    printf("配置多按键唤醒\n");
    
    // 配置按键1（PA0）- 上升沿触发
    EXTI_GPIO_Wakeup_Config(GPIOA, GPIO_PIN_0, GPIO_MODE_IT_RISING);
    
    // 配置按键2（PA1）- 上升沿触发
    EXTI_GPIO_Wakeup_Config(GPIOA, GPIO_PIN_1, GPIO_MODE_IT_RISING);
    
    // 配置按键3（PA2）- 上升沿触发
    EXTI_GPIO_Wakeup_Config(GPIOA, GPIO_PIN_2, GPIO_MODE_IT_RISING);
    
    printf("按下任意按键唤醒系统\n");
    
    // 进入停止模式
    Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
    
    printf("按键唤醒成功\n");
}

/**
 * @brief  GPIO中断回调函数
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    switch (GPIO_Pin) {
        case GPIO_PIN_0:
            printf("按键1按下（PA0）\n");
            break;
        case GPIO_PIN_1:
            printf("按键2按下（PA1）\n");
            break;
        case GPIO_PIN_2:
            printf("按键3按下（PA2）\n");
            break;
        default:
            printf("其他GPIO中断: Pin %d\n", GPIO_Pin);
            break;
    }
}
```

### 传感器中断唤醒

```c
/**
 * @brief  配置传感器中断唤醒
 * @retval None
 * 
 * @note   许多传感器支持中断输出
 *         例如：加速度计的运动检测中断
 *              温度传感器的阈值中断
 */
void Sensor_Interrupt_Wakeup_Config(void) {
    printf("配置传感器中断唤醒\n");
    
    // 示例：配置加速度计运动检测中断（假设连接到PB5）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOB_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    
    HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
    
    printf("传感器中断配置完成\n");
}

/**
 * @brief  传感器中断唤醒示例
 */
void Sensor_Wakeup_Example(void) {
    printf("传感器中断唤醒示例\n");
    
    // 配置传感器中断
    Sensor_Interrupt_Wakeup_Config();
    
    // 配置传感器的运动检测阈值
    // Sensor_ConfigMotionDetection(threshold);
    
    printf("系统进入睡眠，等待运动检测\n");
    
    // 进入停止模式
    Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
    
    printf("检测到运动，系统唤醒\n");
    
    // 读取传感器数据
    // Sensor_ReadData();
}
```



## 第四部分：唤醒时间优化

### 唤醒时间分析

```
唤醒时间组成：

总唤醒时间 = 硬件唤醒时间 + 软件初始化时间

1. 硬件唤醒时间：
   - 睡眠模式：<1μs
   - 停止模式：5-10μs（HSI启动）
   - 待机模式：>1ms（完整复位）

2. 软件初始化时间：
   - 时钟配置：100-500μs
   - 外设初始化：取决于外设数量
   - 应用初始化：取决于应用复杂度

优化策略：
1. 选择合适的电源模式
2. 优化时钟配置代码
3. 延迟非关键外设初始化
4. 使用快速启动技术
```

### 快速唤醒优化

```c
/**
 * @file    fast_wakeup.c
 * @brief   快速唤醒优化实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  快速时钟配置（优化版）
 * @retval None
 * 
 * @note   从停止模式唤醒后，系统时钟为HSI (8MHz)
 *         需要快速配置到目标频率
 */
void Fast_SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    // 配置PLL（使用HSI作为时钟源，避免等待HSE启动）
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI_DIV2;  // HSI/2 = 4MHz
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL16;  // 4MHz × 16 = 64MHz
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // 配置系统时钟
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
    
    SystemCoreClockUpdate();
}

/**
 * @brief  延迟外设初始化
 * @retval None
 * 
 * @note   只初始化关键外设，其他外设按需初始化
 */
void Lazy_Peripheral_Init(void) {
    // 只初始化必要的外设
    // 例如：GPIO、UART（用于调试）
    
    // 其他外设在实际使用时再初始化
}

/**
 * @brief  测量唤醒时间
 * @retval 唤醒时间（微秒）
 */
uint32_t Measure_Wakeup_Time(void) {
    // 使用DWT计数器精确测量
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    
    // 记录进入睡眠前的周期数
    uint32_t start_cycles = DWT->CYCCNT;
    
    // 进入停止模式
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
    
    // 唤醒后立即读取周期数
    uint32_t end_cycles = DWT->CYCCNT;
    
    // 重新配置时钟
    Fast_SystemClock_Config();
    
    // 计算唤醒时间
    uint32_t cycles = end_cycles - start_cycles;
    uint32_t wakeup_time_us = cycles / (SystemCoreClock / 1000000);
    
    printf("唤醒时间: %lu μs\n", wakeup_time_us);
    
    return wakeup_time_us;
}

/**
 * @brief  快速唤醒示例
 */
void Fast_Wakeup_Example(void) {
    printf("快速唤醒优化示例\n");
    
    // 配置外部中断唤醒
    EXTI_GPIO_Wakeup_Config(GPIOA, GPIO_PIN_0, GPIO_MODE_IT_RISING);
    
    printf("测量唤醒时间...\n");
    
    // 测量10次取平均值
    uint32_t total_time = 0;
    for (int i = 0; i < 10; i++) {
        uint32_t wakeup_time = Measure_Wakeup_Time();
        total_time += wakeup_time;
        HAL_Delay(100);
    }
    
    uint32_t avg_time = total_time / 10;
    printf("平均唤醒时间: %lu μs\n", avg_time);
}
```


## 第五部分：状态保存与恢复

### 状态保存策略

```
状态保存方案对比：

1. SRAM保存（睡眠/停止模式）
   优点：速度快、容量大
   缺点：待机模式会丢失
   适用：短期睡眠

2. 备份寄存器（所有模式）
   优点：待机模式保持
   缺点：容量小（20字节）
   适用：关键状态

3. Flash存储（所有模式）
   优点：永久保存、容量大
   缺点：写入慢、寿命有限
   适用：配置参数

4. 外部EEPROM（所有模式）
   优点：容量大、寿命长
   缺点：需要外部器件
   适用：大量数据
```

### 状态保存实现

```c
/**
 * @file    state_management.c
 * @brief   状态保存与恢复实现
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief  系统状态结构
 */
typedef struct {
    uint32_t magic_number;      // 魔数，用于验证数据有效性
    uint32_t system_state;      // 系统状态
    uint32_t sensor_data[10];   // 传感器数据
    uint32_t timestamp;         // 时间戳
    uint32_t checksum;          // 校验和
} SystemState_t;

static SystemState_t system_state = {0};

#define STATE_MAGIC_NUMBER  0x12345678

/**
 * @brief  计算校验和
 * @param  data: 数据指针
 * @param  length: 数据长度（字节）
 * @retval 校验和
 */
uint32_t Calculate_Checksum(uint8_t* data, uint32_t length) {
    uint32_t checksum = 0;
    for (uint32_t i = 0; i < length; i++) {
        checksum += data[i];
    }
    return checksum;
}

/**
 * @brief  保存状态到备份寄存器
 * @param  state: 状态结构指针
 * @retval 是否成功
 * 
 * @note   STM32F1有10个备份寄存器（BKP_DR1-BKP_DR10）
 *         每个寄存器16位，共20字节
 */
bool Save_State_To_Backup(SystemState_t* state) {
    // 使能PWR和BKP时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_RCC_BKP_CLK_ENABLE();
    
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 设置魔数
    state->magic_number = STATE_MAGIC_NUMBER;
    
    // 计算校验和
    state->checksum = Calculate_Checksum((uint8_t*)state, 
                                         sizeof(SystemState_t) - sizeof(uint32_t));
    
    // 保存到备份寄存器（示例：只保存部分数据）
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, (state->magic_number >> 16) & 0xFFFF);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR2, state->magic_number & 0xFFFF);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR3, (state->system_state >> 16) & 0xFFFF);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR4, state->system_state & 0xFFFF);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR5, (state->timestamp >> 16) & 0xFFFF);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR6, state->timestamp & 0xFFFF);
    
    printf("状态已保存到备份寄存器\n");
    return true;
}

/**
 * @brief  从备份寄存器恢复状态
 * @param  state: 状态结构指针
 * @retval 是否成功
 */
bool Restore_State_From_Backup(SystemState_t* state) {
    // 使能PWR和BKP时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_RCC_BKP_CLK_ENABLE();
    
    // 使能备份域访问
    HAL_PWR_EnableBkUpAccess();
    
    // 读取魔数
    uint32_t magic_high = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR1);
    uint32_t magic_low = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR2);
    state->magic_number = (magic_high << 16) | magic_low;
    
    // 验证魔数
    if (state->magic_number != STATE_MAGIC_NUMBER) {
        printf("备份寄存器数据无效\n");
        return false;
    }
    
    // 读取其他数据
    uint32_t state_high = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR3);
    uint32_t state_low = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR4);
    state->system_state = (state_high << 16) | state_low;
    
    uint32_t time_high = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR5);
    uint32_t time_low = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR6);
    state->timestamp = (time_high << 16) | time_low;
    
    printf("状态已从备份寄存器恢复\n");
    printf("系统状态: 0x%08lX\n", state->system_state);
    printf("时间戳: %lu\n", state->timestamp);
    
    return true;
}

/**
 * @brief  保存状态到Flash
 * @param  state: 状态结构指针
 * @retval 是否成功
 */
bool Save_State_To_Flash(SystemState_t* state) {
    // Flash地址（使用最后一页）
    #define STATE_FLASH_ADDR  0x0801FC00  // 假设Flash最后一页
    
    HAL_StatusTypeDef status;
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 擦除页
    FLASH_EraseInitTypeDef EraseInitStruct;
    uint32_t PageError;
    
    EraseInitStruct.TypeErase = FLASH_TYPEERASE_PAGES;
    EraseInitStruct.PageAddress = STATE_FLASH_ADDR;
    EraseInitStruct.NbPages = 1;
    
    status = HAL_FLASHEx_Erase(&EraseInitStruct, &PageError);
    if (status != HAL_OK) {
        printf("Flash擦除失败\n");
        HAL_FLASH_Lock();
        return false;
    }
    
    // 写入数据
    uint32_t* data = (uint32_t*)state;
    uint32_t length = sizeof(SystemState_t) / 4;
    
    for (uint32_t i = 0; i < length; i++) {
        status = HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD,
                                    STATE_FLASH_ADDR + i * 4,
                                    data[i]);
        if (status != HAL_OK) {
            printf("Flash写入失败\n");
            HAL_FLASH_Lock();
            return false;
        }
    }
    
    // 锁定Flash
    HAL_FLASH_Lock();
    
    printf("状态已保存到Flash\n");
    return true;
}

/**
 * @brief  从Flash恢复状态
 * @param  state: 状态结构指针
 * @retval 是否成功
 */
bool Restore_State_From_Flash(SystemState_t* state) {
    #define STATE_FLASH_ADDR  0x0801FC00
    
    // 从Flash读取数据
    memcpy(state, (void*)STATE_FLASH_ADDR, sizeof(SystemState_t));
    
    // 验证魔数
    if (state->magic_number != STATE_MAGIC_NUMBER) {
        printf("Flash数据无效\n");
        return false;
    }
    
    // 验证校验和
    uint32_t checksum = Calculate_Checksum((uint8_t*)state,
                                           sizeof(SystemState_t) - sizeof(uint32_t));
    if (checksum != state->checksum) {
        printf("Flash数据校验失败\n");
        return false;
    }
    
    printf("状态已从Flash恢复\n");
    return true;
}

/**
 * @brief  状态保存恢复示例
 */
void State_Management_Example(void) {
    printf("状态管理示例\n");
    
    // 准备状态数据
    system_state.system_state = 0x12345678;
    system_state.sensor_data[0] = 100;
    system_state.sensor_data[1] = 200;
    system_state.timestamp = HAL_GetTick();
    
    // 保存到备份寄存器
    Save_State_To_Backup(&system_state);
    
    // 保存到Flash
    Save_State_To_Flash(&system_state);
    
    printf("进入待机模式...\n");
    HAL_Delay(100);
    
    // 进入待机模式
    Enter_StandbyMode();
    
    // 唤醒后，在main函数中恢复状态
    // SystemState_t restored_state;
    // Restore_State_From_Backup(&restored_state);
    // 或
    // Restore_State_From_Flash(&restored_state);
}
```

### 上下文保存优化

```c
/**
 * @brief  最小上下文保存
 * @retval None
 * 
 * @note   只保存必要的状态，减少保存时间
 */
void Minimal_Context_Save(void) {
    // 只保存关键状态
    typedef struct {
        uint32_t critical_flag;
        uint32_t error_code;
        uint32_t wakeup_count;
    } MinimalContext_t;
    
    MinimalContext_t context;
    context.critical_flag = 0xABCD;
    context.error_code = 0;
    context.wakeup_count = 100;
    
    // 保存到备份寄存器
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR7, context.critical_flag);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR8, context.error_code);
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR9, context.wakeup_count);
    
    printf("最小上下文已保存\n");
}

/**
 * @brief  压缩状态保存
 * @retval None
 * 
 * @note   使用位域压缩多个状态到一个寄存器
 */
void Compressed_State_Save(void) {
    // 使用位域压缩状态
    typedef struct {
        uint32_t led_state : 1;      // LED状态（1位）
        uint32_t motor_state : 1;    // 电机状态（1位）
        uint32_t sensor_enable : 1;  // 传感器使能（1位）
        uint32_t mode : 3;            // 工作模式（3位）
        uint32_t error_flags : 8;    // 错误标志（8位）
        uint32_t reserved : 18;      // 保留（18位）
    } CompressedState_t;
    
    CompressedState_t state;
    state.led_state = 1;
    state.motor_state = 0;
    state.sensor_enable = 1;
    state.mode = 3;
    state.error_flags = 0x12;
    
    // 保存到一个备份寄存器
    uint32_t packed_state = *(uint32_t*)&state;
    HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR10, packed_state & 0xFFFF);
    
    printf("压缩状态已保存: 0x%08lX\n", packed_state);
}
```



## 第六部分：综合应用示例

### 智能传感器节点

```c
/**
 * @file    smart_sensor_node.c
 * @brief   智能传感器节点综合示例
 */

#include "stm32f1xx_hal.h"
#include <stdio.h>

/**
 * @brief  传感器节点配置
 */
typedef struct {
    uint32_t sample_interval_s;    // 采样间隔（秒）
    uint32_t tx_interval_s;        // 发送间隔（秒）
    uint8_t  samples_per_tx;       // 每次发送的样本数
    bool     motion_wakeup_enable; // 运动唤醒使能
} SensorNodeConfig_t;

static SensorNodeConfig_t node_config = {
    .sample_interval_s = 60,       // 每60秒采样一次
    .tx_interval_s = 600,          // 每10分钟发送一次
    .samples_per_tx = 10,          // 每次发送10个样本
    .motion_wakeup_enable = true   // 使能运动唤醒
};

/**
 * @brief  传感器数据缓冲
 */
#define MAX_SAMPLES  20
typedef struct {
    float temperature[MAX_SAMPLES];
    float humidity[MAX_SAMPLES];
    uint32_t timestamp[MAX_SAMPLES];
    uint8_t count;
} SensorDataBuffer_t;

static SensorDataBuffer_t data_buffer = {0};

/**
 * @brief  读取传感器数据
 */
void Read_Sensor_Data(void) {
    if (data_buffer.count >= MAX_SAMPLES) {
        printf("数据缓冲已满\n");
        return;
    }
    
    // 读取温湿度传感器
    // 这里使用模拟数据
    data_buffer.temperature[data_buffer.count] = 25.5f;
    data_buffer.humidity[data_buffer.count] = 60.0f;
    data_buffer.timestamp[data_buffer.count] = HAL_GetTick();
    data_buffer.count++;
    
    printf("采集数据 #%d: 温度=%.1f°C, 湿度=%.1f%%\n",
           data_buffer.count,
           data_buffer.temperature[data_buffer.count - 1],
           data_buffer.humidity[data_buffer.count - 1]);
}

/**
 * @brief  发送数据到服务器
 */
void Transmit_Data(void) {
    printf("发送数据到服务器...\n");
    
    // 打开无线模块
    PowerDomain_Enable(POWER_DOMAIN_WIRELESS);
    HAL_Delay(100);  // 等待模块启动
    
    // 发送数据
    for (uint8_t i = 0; i < data_buffer.count; i++) {
        printf("发送样本 #%d: T=%.1f°C, H=%.1f%%\n",
               i + 1,
               data_buffer.temperature[i],
               data_buffer.humidity[i]);
        
        // 实际发送代码
        // Wireless_Send(&data_buffer.temperature[i], ...);
    }
    
    // 清空缓冲
    data_buffer.count = 0;
    
    // 关闭无线模块
    PowerDomain_Disable(POWER_DOMAIN_WIRELESS);
    
    printf("数据发送完成\n");
}

/**
 * @brief  智能传感器节点主循环
 */
void Smart_Sensor_Node_Run(void) {
    printf("智能传感器节点启动\n");
    printf("采样间隔: %lu 秒\n", node_config.sample_interval_s);
    printf("发送间隔: %lu 秒\n", node_config.tx_interval_s);
    
    // 初始化RTC
    RTC_Init();
    
    // 配置运动检测唤醒（如果使能）
    if (node_config.motion_wakeup_enable) {
        Sensor_Interrupt_Wakeup_Config();
    }
    
    uint32_t sample_count = 0;
    
    while (1) {
        // 读取传感器数据
        Read_Sensor_Data();
        sample_count++;
        
        // 检查是否需要发送数据
        if (sample_count >= node_config.samples_per_tx) {
            Transmit_Data();
            sample_count = 0;
        }
        
        // 保存状态
        system_state.system_state = sample_count;
        system_state.timestamp = HAL_GetTick();
        Save_State_To_Backup(&system_state);
        
        // 配置RTC唤醒
        RTC_SetAlarmWakeup(node_config.sample_interval_s);
        
        printf("进入停止模式，%lu 秒后唤醒\n", node_config.sample_interval_s);
        
        // 进入停止模式
        Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
        
        // 唤醒后继续循环
        printf("系统唤醒\n");
    }
}
```


### 可穿戴设备电源管理

```c
/**
 * @brief  可穿戴设备电源管理示例
 */
void Wearable_Device_Power_Management(void) {
    printf("可穿戴设备电源管理\n");
    
    typedef enum {
        DEVICE_STATE_ACTIVE,      // 活动状态（用户交互）
        DEVICE_STATE_MONITORING,  // 监测状态（后台监测）
        DEVICE_STATE_IDLE,        // 空闲状态（无活动）
        DEVICE_STATE_SLEEP        // 睡眠状态（深度睡眠）
    } DeviceState_t;
    
    DeviceState_t device_state = DEVICE_STATE_IDLE;
    uint32_t idle_time = 0;
    
    while (1) {
        switch (device_state) {
            case DEVICE_STATE_ACTIVE:
                printf("活动状态：全功能运行\n");
                
                // 使能所有外设
                PowerDomain_Enable(POWER_DOMAIN_DISPLAY);
                PowerDomain_Enable(POWER_DOMAIN_PERIPHERAL);
                
                // 高性能模式
                DVFS_SwitchOperatingPoint(3);  // 72MHz
                
                // 检测用户活动
                // if (no_user_activity_for_30s) {
                //     device_state = DEVICE_STATE_MONITORING;
                // }
                
                HAL_Delay(100);
                break;
                
            case DEVICE_STATE_MONITORING:
                printf("监测状态：后台监测\n");
                
                // 关闭显示
                PowerDomain_Disable(POWER_DOMAIN_DISPLAY);
                
                // 中等性能模式
                DVFS_SwitchOperatingPoint(1);  // 24MHz
                
                // 定期采集传感器数据
                Read_Sensor_Data();
                
                // 配置1秒后唤醒
                RTC_SetAlarmWakeup(1);
                
                // 进入睡眠模式
                Enter_SleepMode(false);
                
                idle_time++;
                
                // 检测是否进入空闲状态
                if (idle_time > 60) {  // 60秒无活动
                    device_state = DEVICE_STATE_IDLE;
                    idle_time = 0;
                }
                break;
                
            case DEVICE_STATE_IDLE:
                printf("空闲状态：低功耗待机\n");
                
                // 关闭大部分外设
                PowerDomain_Disable(POWER_DOMAIN_PERIPHERAL);
                
                // 配置运动检测唤醒
                Sensor_Interrupt_Wakeup_Config();
                
                // 配置按键唤醒
                EXTI_GPIO_Wakeup_Config(GPIOA, GPIO_PIN_0, GPIO_MODE_IT_RISING);
                
                // 进入停止模式
                Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
                
                // 唤醒后检查唤醒源
                printf("从空闲状态唤醒\n");
                device_state = DEVICE_STATE_ACTIVE;
                break;
                
            case DEVICE_STATE_SLEEP:
                printf("睡眠状态：深度睡眠\n");
                
                // 保存状态
                Save_State_To_Backup(&system_state);
                
                // 配置RTC唤醒（例如：8小时后）
                RTC_SetAlarmWakeup(8 * 3600);
                
                // 进入待机模式
                Enter_StandbyMode();
                break;
        }
    }
}
```



## 实践练习

### 练习1：多模式切换

**目标**：实现一个支持多种电源模式切换的系统

**要求**：
1. 实现睡眠、停止、待机三种模式
2. 支持按键、RTC、传感器三种唤醒源
3. 测量并优化唤醒时间
4. 实现状态保存和恢复

**提示**：
```c
// 伪代码框架
void Power_Mode_Exercise(void) {
    // 1. 初始化系统
    System_Init();
    RTC_Init();
    
    // 2. 配置唤醒源
    EXTI_GPIO_Wakeup_Config(...);
    RTC_SetAlarmWakeup(...);
    Sensor_Interrupt_Wakeup_Config();
    
    // 3. 主循环
    while (1) {
        // 执行任务
        Do_Task();
        
        // 保存状态
        Save_State_To_Backup(&system_state);
        
        // 选择电源模式
        PowerMode_t mode = Select_Power_Mode();
        
        // 进入电源模式
        Enter_Power_Mode(mode);
        
        // 唤醒后恢复状态
        Restore_State_From_Backup(&system_state);
    }
}
```

### 练习2：自适应电源管理

**目标**：实现根据系统负载自动选择电源模式

**要求**：
1. 监测系统空闲时间
2. 根据空闲时间选择合适的电源模式
3. 实现快速唤醒机制
4. 统计功耗数据

**提示**：
```c
PowerMode_t Select_Power_Mode_Adaptive(uint32_t idle_time_ms) {
    if (idle_time_ms < 10) {
        return POWER_MODE_RUN;      // 继续运行
    } else if (idle_time_ms < 100) {
        return POWER_MODE_SLEEP;    // 睡眠模式
    } else if (idle_time_ms < 1000) {
        return POWER_MODE_STOP;     // 停止模式
    } else {
        return POWER_MODE_STANDBY;  // 待机模式
    }
}
```

### 练习3：物联网节点实现

**目标**：实现一个低功耗物联网传感器节点

**要求**：
1. 定时采集传感器数据
2. 批量发送数据到服务器
3. 支持运动检测唤醒
4. 实现超低功耗（平均<100μA）

**参考设计**：
```
工作流程：
1. 采集数据（10秒）
2. 进入停止模式（50秒）
3. RTC唤醒，重复步骤1-2
4. 累积10个样本后发送
5. 发送完成后继续采集

功耗分析：
- 采集：10mA × 10s = 100mAs
- 睡眠：50μA × 50s = 2.5mAs
- 发送：100mA × 5s = 500mAs
- 平均：(100 + 2.5 + 500) / 600s ≈ 1mA
```



## 常见问题与解决方案

### 问题1：从停止模式唤醒后系统不工作

**原因**：
- 时钟未重新配置
- 外设未重新初始化

**解决方案**：
```c
void Enter_StopMode_Safe(void) {
    // 进入停止模式
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
    
    // 唤醒后立即重新配置时钟
    SystemClock_Config();
    
    // 重新初始化必要的外设
    // HAL_UART_Init(&huart1);
}
```

### 问题2：RTC唤醒不工作

**原因**：
- RTC未正确初始化
- LSE晶振未起振
- 中断未使能

**解决方案**：
```c
void RTC_Debug(void) {
    // 检查LSE是否起振
    if (__HAL_RCC_GET_FLAG(RCC_FLAG_LSERDY) == RESET) {
        printf("错误：LSE未起振\n");
        // 尝试使用LSI
        // ...
    }
    
    // 检查RTC时钟是否使能
    if (__HAL_RCC_RTC_GET_FLAG() == RESET) {
        printf("错误：RTC时钟未使能\n");
    }
    
    // 检查中断是否使能
    if (HAL_NVIC_GetEnableIRQ(RTC_IRQn) == 0) {
        printf("错误：RTC中断未使能\n");
    }
}
```

### 问题3：待机模式唤醒后数据丢失

**原因**：
- 未保存到备份寄存器或Flash
- 备份域未使能

**解决方案**：
```c
void Standby_Data_Protection(void) {
    // 使能备份域
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_RCC_BKP_CLK_ENABLE();
    HAL_PWR_EnableBkUpAccess();
    
    // 保存关键数据到备份寄存器
    Save_State_To_Backup(&system_state);
    
    // 或保存到Flash
    Save_State_To_Flash(&system_state);
    
    // 进入待机模式
    Enter_StandbyMode();
}
```

### 问题4：功耗仍然很高

**原因**：
- 外设未关闭
- GPIO配置不当
- 调试接口未禁用

**解决方案**：
```c
void Minimize_Power_Consumption(void) {
    // 1. 关闭所有不需要的外设时钟
    __HAL_RCC_USART1_CLK_DISABLE();
    __HAL_RCC_SPI1_CLK_DISABLE();
    __HAL_RCC_I2C1_CLK_DISABLE();
    
    // 2. 配置所有GPIO为模拟输入（最低功耗）
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 3. 禁用调试接口（可选，会影响调试）
    // __HAL_AFIO_REMAP_SWJ_DISABLE();
    
    // 4. 使用低功耗稳压器
    Enter_StopMode(PWR_LOWPOWERREGULATOR_ON);
}
```



## 总结

本教程深入讲解了嵌入式系统的电源模式切换与唤醒源配置技术。通过学习本教程，你应该掌握：

1. **多级睡眠模式**：
   - 睡眠模式：快速唤醒，中等功耗
   - 停止模式：平衡功耗和唤醒时间
   - 待机模式：极低功耗，唤醒较慢

2. **唤醒源配置**：
   - RTC定时唤醒：周期性任务
   - 外部中断唤醒：事件驱动
   - 传感器中断唤醒：智能唤醒

3. **唤醒时间优化**：
   - 快速时钟配置
   - 延迟外设初始化
   - 精确测量唤醒时间

4. **状态保存恢复**：
   - 备份寄存器：小容量，快速
   - Flash存储：大容量，永久
   - 压缩存储：节省空间

5. **综合应用**：
   - 智能传感器节点
   - 可穿戴设备
   - 物联网应用

### 关键要点

```
电源模式选择原则：
1. 空闲时间 < 1ms：睡眠模式
2. 空闲时间 1ms-1s：停止模式
3. 空闲时间 > 1s：待机模式
4. 需要保持状态：睡眠/停止模式
5. 极致低功耗：待机模式

唤醒源选择原则：
1. 定时任务：RTC唤醒
2. 外部事件：GPIO中断
3. 传感器事件：传感器中断
4. 组合唤醒：多种唤醒源

优化建议：
1. 测量实际功耗
2. 优化唤醒时间
3. 合理保存状态
4. 选择合适模式
5. 持续监测优化
```

### 下一步学习

- 学习动态电源管理(DPM)技术
- 深入研究电池管理系统(BMS)
- 探索能量收集技术
- 学习超低功耗设计技巧

### 参考资源

- STM32参考手册：电源控制(PWR)章节
- AN4365: STM32F1系列低功耗模式
- AN4621: STM32电源管理最佳实践
- 《嵌入式系统低功耗设计》

---

**作者**: 嵌入式知识平台内容团队  
**最后更新**: 2026-03-07  
**版本**: 1.0.0
