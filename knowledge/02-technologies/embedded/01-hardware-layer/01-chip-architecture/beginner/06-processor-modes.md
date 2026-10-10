---
# 基础信息
title: "处理器工作模式与特权级别"
description: "深入讲解ARM Cortex-M处理器的线程模式与处理器模式、特权级别与非特权级别的区别，掌握模式切换机制和CONTROL寄存器配置，理解处理器模式在系统安全中的重要作用"
slug: "processor-modes-and-privilege-levels"

# 分类信息
domain: "01-hardware-layer"
module: "01-chip-architecture"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 处理器模式
  - 特权级别
  - 系统安全
  - ARM Cortex-M
  - CONTROL寄存器
prerequisites:
  - "01-arm-cortex-m-intro"
related_contents:
  - "08-interrupt-vector-table"

# 学习信息
estimated_time: 30
difficulty_score: 2

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
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 处理器模式
  - 特权级别
  - 线程模式
  - 处理器模式
  - 系统安全
cover_image: ""
---

# 处理器工作模式与特权级别

## 学习目标

完成本文学习后，你将能够：

- [ ] 理解ARM Cortex-M的两种工作模式：线程模式和处理器模式
- [ ] 掌握特权级别和非特权级别的区别
- [ ] 了解模式切换的触发条件和机制
- [ ] 掌握CONTROL寄存器的配置方法
- [ ] 理解处理器模式在系统安全中的作用
- [ ] 能够编写代码实现模式切换
- [ ] 了解操作系统如何利用特权级别保护系统

## 前置要求

在开始本文学习之前，你需要：

**知识要求**：
- 了解ARM Cortex-M架构基础
- 熟悉C语言编程
- 了解中断和异常的基本概念
- 掌握寄存器操作基础

**技能要求**：
- 能够阅读和编写简单的C代码
- 了解位操作和寄存器配置
- 熟悉基本的调试方法

**推荐但非必需**：
- 有嵌入式系统开发经验
- 了解操作系统基础概念
- 熟悉汇编语言

## 概述

ARM Cortex-M处理器设计了两种工作模式和两种特权级别，这种设计为嵌入式系统提供了基本的安全保护机制。通过合理使用这些模式和特权级别，可以隔离关键系统代码和用户应用代码，防止错误的用户代码破坏系统稳定性。

### 为什么需要处理器模式

1. **系统保护**：
   - 保护关键系统资源不被意外修改
   - 防止用户代码破坏系统配置
   - 提高系统稳定性和可靠性

2. **权限管理**：
   - 区分系统代码和应用代码
   - 限制应用代码的访问权限
   - 实现基本的安全隔离

3. **操作系统支持**：
   - 为RTOS提供基础支持
   - 实现任务隔离
   - 支持系统调用机制

4. **错误隔离**：
   - 限制错误代码的影响范围
   - 便于故障诊断和恢复
   - 提高系统鲁棒性


### 处理器模式概览

ARM Cortex-M处理器有两个维度的模式划分：

```
┌─────────────────────────────────────────┐
│         处理器工作模式                   │
├──────────────────┬──────────────────────┤
│   线程模式       │    处理器模式         │
│  (Thread Mode)   │   (Handler Mode)     │
│                  │                      │
│  执行应用代码    │   执行异常处理代码    │
│  可以是特权或    │   总是特权级别        │
│  非特权级别      │                      │
└──────────────────┴──────────────────────┘

┌─────────────────────────────────────────┐
│         特权级别                         │
├──────────────────┬──────────────────────┤
│   特权级别       │    非特权级别         │
│  (Privileged)    │   (Unprivileged)     │
│                  │                      │
│  可以访问所有    │   访问受限            │
│  系统资源        │   不能访问某些资源    │
│  可以执行所有    │   不能执行某些指令    │
│  指令            │                      │
└──────────────────┴──────────────────────┘
```

**四种可能的组合**：

1. **线程模式 + 特权级别**：系统启动后的默认状态
2. **线程模式 + 非特权级别**：运行用户应用代码
3. **处理器模式 + 特权级别**：处理中断和异常（唯一组合）
4. ~~处理器模式 + 非特权级别~~：不存在这种组合

## 第一部分：线程模式与处理器模式

### 线程模式（Thread Mode）

线程模式是处理器执行普通应用代码时的工作模式。

**线程模式的特点**：

1. **执行应用代码**：
   - main函数及其调用的函数
   - 任务代码（在RTOS中）
   - 普通的应用逻辑

2. **可配置特权级别**：
   - 可以是特权级别
   - 也可以是非特权级别
   - 通过CONTROL寄存器配置

3. **使用主栈或进程栈**：
   - 可以使用主栈指针（MSP）
   - 也可以使用进程栈指针（PSP）
   - 由CONTROL寄存器控制

4. **可以被中断打断**：
   - 响应中断时切换到处理器模式
   - 中断返回后继续线程模式

**线程模式的典型应用**：

```c
/**
 * @brief  线程模式示例
 * @note   main函数和普通函数都在线程模式下执行
 */
int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    
    // 应用代码（线程模式）
    while(1) {
        // 执行应用逻辑
        Process_Data();
        
        // 等待事件
        Wait_For_Event();
        
        // 处理任务
        Handle_Task();
    }
}

void Process_Data(void)
{
    // 这个函数也在线程模式下执行
    uint32_t data = Read_Sensor();
    Filter_Data(data);
    Send_Data(data);
}
```

### 处理器模式（Handler Mode）

处理器模式是处理器执行异常处理代码时的工作模式。

**处理器模式的特点**：

1. **执行异常处理代码**：
   - 中断服务函数（ISR）
   - 异常处理函数
   - 系统异常处理

2. **总是特权级别**：
   - 不能配置为非特权级别
   - 始终具有完全访问权限
   - 可以访问所有系统资源

3. **总是使用主栈**：
   - 固定使用主栈指针（MSP）
   - 不能使用进程栈指针（PSP）
   - 确保异常处理的栈空间独立

4. **异常嵌套**：
   - 可以被更高优先级的异常打断
   - 支持异常嵌套
   - 自动保存和恢复上下文

**处理器模式的典型应用**：

```c
/**
 * @brief  SysTick中断处理函数
 * @note   在处理器模式下执行
 */
void SysTick_Handler(void)
{
    // 这个函数在处理器模式下执行
    // 总是特权级别
    // 使用主栈（MSP）
    
    // 更新系统滴答计数
    HAL_IncTick();
    
    // 可以访问所有系统资源
    SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;  // 触发PendSV
}

/**
 * @brief  外部中断处理函数
 * @note   在处理器模式下执行
 */
void EXTI0_IRQHandler(void)
{
    // 处理器模式，特权级别
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        // 处理中断事件
        Handle_Button_Press();
    }
}
```


### 模式切换机制

处理器在线程模式和处理器模式之间自动切换：

```
线程模式
  │
  │ 发生异常/中断
  ↓
处理器模式
  │
  │ 异常返回
  ↓
线程模式
```

**切换到处理器模式**：

- 当发生异常或中断时
- 处理器自动切换到处理器模式
- 自动保存上下文到栈
- 跳转到异常处理函数

**返回线程模式**：

- 异常处理函数执行完毕
- 执行异常返回指令（BX LR，LR包含特殊值）
- 自动恢复上下文
- 返回到被打断的代码

**模式切换示例**：

```c
/**
 * @brief  演示模式切换
 */
void Mode_Switch_Demo(void)
{
    // 当前在线程模式
    printf("在线程模式中\n");
    
    // 触发一个中断
    NVIC_SetPendingIRQ(EXTI0_IRQn);
    
    // 中断处理完成后，继续在线程模式
    printf("中断处理完成，返回线程模式\n");
}

/**
 * @brief  中断处理函数
 * @note   自动切换到处理器模式
 */
void EXTI0_IRQHandler(void)
{
    // 现在在处理器模式
    printf("在处理器模式中处理中断\n");
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    // 函数返回时自动切换回线程模式
}
```

**检测当前模式**：

```c
/**
 * @brief  检测当前处理器模式
 * @retval 0: 线程模式, 1: 处理器模式
 */
int Is_Handler_Mode(void)
{
    // 读取IPSR寄存器
    uint32_t ipsr = __get_IPSR();
    
    // IPSR为0表示线程模式，非0表示处理器模式
    return (ipsr != 0);
}

/**
 * @brief  打印当前模式
 */
void Print_Current_Mode(void)
{
    if (Is_Handler_Mode()) {
        printf("当前在处理器模式\n");
    } else {
        printf("当前在线程模式\n");
    }
}
```

## 第二部分：特权级别与非特权级别

### 特权级别（Privileged）

特权级别具有对系统的完全访问权限。

**特权级别的权限**：

1. **访问所有内存区域**：
   - 可以访问所有SRAM
   - 可以访问所有Flash
   - 可以访问所有外设寄存器

2. **执行所有指令**：
   - 可以执行所有ARM指令
   - 可以修改CONTROL寄存器
   - 可以配置系统控制寄存器

3. **访问系统控制空间**：
   - 可以访问SCB（系统控制块）
   - 可以配置NVIC（中断控制器）
   - 可以配置MPU（内存保护单元）

4. **切换到非特权级别**：
   - 可以主动降低权限
   - 通过修改CONTROL寄存器实现

**特权级别的典型代码**：

```c
/**
 * @brief  特权级别操作示例
 * @note   只能在特权级别下执行
 */
void Privileged_Operations(void)
{
    // 1. 配置系统控制寄存器
    SCB->VTOR = 0x08000000;  // 设置向量表地址
    
    // 2. 配置NVIC
    NVIC_SetPriority(SysTick_IRQn, 0);  // 设置中断优先级
    NVIC_EnableIRQ(EXTI0_IRQn);         // 使能中断
    
    // 3. 配置MPU
    MPU->CTRL = MPU_CTRL_ENABLE_Msk;    // 使能MPU
    
    // 4. 修改CONTROL寄存器
    __set_CONTROL(__get_CONTROL() | CONTROL_nPRIV_Msk);  // 切换到非特权
    __ISB();  // 指令同步屏障
}
```

### 非特权级别（Unprivileged）

非特权级别的访问权限受到限制，用于运行用户应用代码。

**非特权级别的限制**：

1. **不能访问某些内存区域**：
   - 不能访问系统控制空间
   - 不能访问某些外设（由MPU配置）
   - 可能不能访问某些SRAM区域

2. **不能执行某些指令**：
   - 不能修改CONTROL寄存器
   - 不能直接配置系统寄存器
   - 不能禁用中断（除非使用PRIMASK）

3. **需要通过系统调用访问系统服务**：
   - 使用SVC指令请求系统服务
   - 由特权级别的代码处理请求
   - 类似于操作系统的系统调用

4. **不能切换回特权级别**：
   - 只能通过异常返回恢复特权级别
   - 或通过系统调用请求切换

**非特权级别的典型代码**：

```c
/**
 * @brief  非特权级别操作示例
 * @note   在非特权级别下执行
 */
void Unprivileged_Operations(void)
{
    // 1. 可以执行普通的应用逻辑
    uint32_t data = Read_Sensor();
    Process_Data(data);
    
    // 2. 可以访问普通的外设
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
    
    // 3. 不能直接配置系统寄存器
    // SCB->VTOR = 0x08000000;  // ❌ 会触发错误
    
    // 4. 需要通过系统调用访问系统服务
    SVC_Request_System_Service();
}

/**
 * @brief  系统调用示例
 * @note   使用SVC指令请求系统服务
 */
void SVC_Request_System_Service(void)
{
    // 使用SVC指令触发系统调用
    __asm volatile ("SVC #0");
}

/**
 * @brief  SVC处理函数
 * @note   在特权级别下执行
 */
void SVC_Handler(void)
{
    // 现在在特权级别
    // 可以执行需要特权的操作
    
    // 处理系统调用请求
    Handle_System_Call();
}
```


### 特权级别切换

**从特权切换到非特权**：

```c
/**
 * @brief  切换到非特权级别
 * @note   只能在特权级别下调用
 */
void Switch_To_Unprivileged(void)
{
    // 读取CONTROL寄存器
    uint32_t control = __get_CONTROL();
    
    // 设置nPRIV位（bit 0）
    control |= CONTROL_nPRIV_Msk;
    
    // 写回CONTROL寄存器
    __set_CONTROL(control);
    
    // 指令同步屏障，确保修改生效
    __ISB();
    
    printf("已切换到非特权级别\n");
}
```

**从非特权切换到特权**：

非特权级别不能直接切换回特权级别，必须通过以下方式：

1. **通过异常返回**：
   ```c
   /**
    * @brief  通过SVC切换回特权级别
    */
   void Request_Privileged_Mode(void)
   {
       // 触发SVC异常
       __asm volatile ("SVC #1");
   }
   
   /**
    * @brief  SVC处理函数
    */
   void SVC_Handler(void)
   {
       // 在处理器模式下，总是特权级别
       // 可以修改返回时的CONTROL寄存器值
       
       // 获取栈帧
       uint32_t *stack_frame;
       if (__get_CONTROL() & CONTROL_SPSEL_Msk) {
           stack_frame = (uint32_t*)__get_PSP();
       } else {
           stack_frame = (uint32_t*)__get_MSP();
       }
       
       // 修改CONTROL寄存器（在异常返回时生效）
       __set_CONTROL(__get_CONTROL() & ~CONTROL_nPRIV_Msk);
       __ISB();
   }
   ```

2. **通过复位**：
   ```c
   /**
    * @brief  通过复位恢复特权级别
    */
   void Reset_To_Privileged(void)
   {
       // 系统复位后默认为特权级别
       NVIC_SystemReset();
   }
   ```

## 第三部分：CONTROL寄存器

### CONTROL寄存器结构

CONTROL寄存器是一个特殊功能寄存器，用于控制处理器的工作模式和特权级别。

**CONTROL寄存器位定义**：

```
31                                    3    2    1    0
┌─────────────────────────────────────┬────┬────┬────┐
│           保留 (0)                  │FPCA│SPSEL│nPRIV│
└─────────────────────────────────────┴────┴────┴────┘

bit 0 - nPRIV: 特权级别控制
        0 = 特权级别 (Privileged)
        1 = 非特权级别 (Unprivileged)
        注意：只在线程模式下有效

bit 1 - SPSEL: 栈指针选择
        0 = 使用主栈指针 (MSP)
        1 = 使用进程栈指针 (PSP)
        注意：只在线程模式下有效

bit 2 - FPCA: 浮点上下文激活
        0 = 没有浮点指令执行
        1 = 浮点指令已执行
        注意：只在有FPU的处理器上有效

bit 3-31: 保留，必须为0
```

**CONTROL寄存器的特点**：

1. **只能在特权级别修改**：
   - 非特权级别不能修改CONTROL寄存器
   - 尝试修改会被忽略（不会产生异常）

2. **只在线程模式下有效**：
   - nPRIV和SPSEL位只在线程模式下有效
   - 处理器模式下总是特权级别，总是使用MSP

3. **需要指令同步屏障**：
   - 修改后需要执行ISB指令
   - 确保修改立即生效

### CONTROL寄存器操作

**读取CONTROL寄存器**：

```c
/**
 * @brief  读取CONTROL寄存器
 * @retval CONTROL寄存器的值
 */
uint32_t Read_CONTROL(void)
{
    uint32_t control = __get_CONTROL();
    
    printf("CONTROL寄存器: 0x%08X\n", control);
    printf("  nPRIV (bit 0): %d (%s)\n", 
           (control & CONTROL_nPRIV_Msk) ? 1 : 0,
           (control & CONTROL_nPRIV_Msk) ? "非特权" : "特权");
    printf("  SPSEL (bit 1): %d (%s)\n", 
           (control & CONTROL_SPSEL_Msk) ? 1 : 0,
           (control & CONTROL_SPSEL_Msk) ? "PSP" : "MSP");
    printf("  FPCA  (bit 2): %d\n", 
           (control & CONTROL_FPCA_Msk) ? 1 : 0);
    
    return control;
}
```

**修改CONTROL寄存器**：

```c
/**
 * @brief  配置CONTROL寄存器
 * @param  npriv: 特权级别 (0=特权, 1=非特权)
 * @param  spsel: 栈选择 (0=MSP, 1=PSP)
 */
void Configure_CONTROL(uint32_t npriv, uint32_t spsel)
{
    uint32_t control = __get_CONTROL();
    
    // 清除nPRIV和SPSEL位
    control &= ~(CONTROL_nPRIV_Msk | CONTROL_SPSEL_Msk);
    
    // 设置新值
    if (npriv) {
        control |= CONTROL_nPRIV_Msk;
    }
    if (spsel) {
        control |= CONTROL_SPSEL_Msk;
    }
    
    // 写回CONTROL寄存器
    __set_CONTROL(control);
    
    // 指令同步屏障
    __ISB();
    
    printf("CONTROL寄存器已配置\n");
}
```

**检查当前特权级别**：

```c
/**
 * @brief  检查当前是否为特权级别
 * @retval 1: 特权级别, 0: 非特权级别
 */
int Is_Privileged(void)
{
    // 如果在处理器模式，总是特权级别
    if (Is_Handler_Mode()) {
        return 1;
    }
    
    // 在线程模式，检查CONTROL寄存器
    uint32_t control = __get_CONTROL();
    return !(control & CONTROL_nPRIV_Msk);
}

/**
 * @brief  打印当前特权级别
 */
void Print_Privilege_Level(void)
{
    if (Is_Privileged()) {
        printf("当前为特权级别\n");
    } else {
        printf("当前为非特权级别\n");
    }
}
```

### 栈指针选择

CONTROL寄存器的SPSEL位控制线程模式下使用哪个栈指针。

**主栈指针（MSP）**：

- 系统启动后默认使用
- 处理器模式总是使用MSP
- 通常用于系统代码和中断处理

**进程栈指针（PSP）**：

- 需要通过CONTROL寄存器切换
- 只在线程模式下使用
- 通常用于任务代码（RTOS）

**切换栈指针示例**：

```c
/**
 * @brief  切换到进程栈指针
 * @param  psp_value: PSP的初始值
 */
void Switch_To_PSP(uint32_t psp_value)
{
    // 设置PSP的值
    __set_PSP(psp_value);
    
    // 切换到PSP
    uint32_t control = __get_CONTROL();
    control |= CONTROL_SPSEL_Msk;
    __set_CONTROL(control);
    __ISB();
    
    printf("已切换到PSP，PSP = 0x%08X\n", psp_value);
}

/**
 * @brief  切换回主栈指针
 */
void Switch_To_MSP(void)
{
    // 切换到MSP
    uint32_t control = __get_CONTROL();
    control &= ~CONTROL_SPSEL_Msk;
    __set_CONTROL(control);
    __ISB();
    
    printf("已切换到MSP\n");
}

/**
 * @brief  获取当前使用的栈指针
 * @retval 当前栈指针的值
 */
uint32_t Get_Current_SP(void)
{
    uint32_t control = __get_CONTROL();
    
    if (Is_Handler_Mode()) {
        // 处理器模式总是使用MSP
        return __get_MSP();
    } else {
        // 线程模式，检查SPSEL位
        if (control & CONTROL_SPSEL_Msk) {
            return __get_PSP();  // 使用PSP
        } else {
            return __get_MSP();  // 使用MSP
        }
    }
}
```


## 第四部分：模式切换实战

### 完整的模式切换示例

以下是一个完整的示例，演示如何在不同模式和特权级别之间切换：

```c
#include "stm32f1xx_hal.h"
#include <stdio.h>

// 定义进程栈
#define PSP_STACK_SIZE  1024
uint32_t psp_stack[PSP_STACK_SIZE];

/**
 * @brief  初始化进程栈
 */
void Init_PSP_Stack(void)
{
    // 设置PSP指向栈顶
    uint32_t psp_top = (uint32_t)&psp_stack[PSP_STACK_SIZE];
    __set_PSP(psp_top);
    
    printf("PSP栈已初始化，栈顶: 0x%08X\n", psp_top);
}

/**
 * @brief  打印当前状态
 */
void Print_Status(void)
{
    printf("\n=== 当前状态 ===\n");
    
    // 打印模式
    if (Is_Handler_Mode()) {
        printf("模式: 处理器模式\n");
    } else {
        printf("模式: 线程模式\n");
    }
    
    // 打印特权级别
    if (Is_Privileged()) {
        printf("特权级别: 特权\n");
    } else {
        printf("特权级别: 非特权\n");
    }
    
    // 打印栈指针
    uint32_t control = __get_CONTROL();
    if (Is_Handler_Mode() || !(control & CONTROL_SPSEL_Msk)) {
        printf("栈指针: MSP = 0x%08X\n", __get_MSP());
    } else {
        printf("栈指针: PSP = 0x%08X\n", __get_PSP());
    }
    
    // 打印CONTROL寄存器
    printf("CONTROL: 0x%08X\n", control);
    printf("================\n\n");
}

/**
 * @brief  特权级别的函数
 */
void Privileged_Function(void)
{
    printf("执行特权级别函数\n");
    Print_Status();
    
    // 可以访问系统寄存器
    uint32_t vtor = SCB->VTOR;
    printf("VTOR = 0x%08X\n", vtor);
}

/**
 * @brief  非特权级别的函数
 */
void Unprivileged_Function(void)
{
    printf("执行非特权级别函数\n");
    Print_Status();
    
    // 尝试访问系统寄存器（会失败）
    // uint32_t vtor = SCB->VTOR;  // ❌ 会触发错误
    
    // 只能执行普通操作
    HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
}

/**
 * @brief  模式切换演示
 */
void Mode_Switch_Demo(void)
{
    printf("\n========== 模式切换演示 ==========\n\n");
    
    // 1. 初始状态：线程模式 + 特权级别 + MSP
    printf("1. 初始状态\n");
    Print_Status();
    Privileged_Function();
    
    // 2. 切换到PSP
    printf("\n2. 切换到PSP\n");
    Init_PSP_Stack();
    uint32_t control = __get_CONTROL();
    control |= CONTROL_SPSEL_Msk;
    __set_CONTROL(control);
    __ISB();
    Print_Status();
    
    // 3. 切换到非特权级别
    printf("\n3. 切换到非特权级别\n");
    control = __get_CONTROL();
    control |= CONTROL_nPRIV_Msk;
    __set_CONTROL(control);
    __ISB();
    Print_Status();
    Unprivileged_Function();
    
    // 4. 触发中断（自动切换到处理器模式）
    printf("\n4. 触发中断\n");
    NVIC_SetPendingIRQ(EXTI0_IRQn);
    
    // 5. 中断返回后，仍然是非特权级别
    printf("\n5. 中断返回后\n");
    Print_Status();
    
    // 6. 通过SVC切换回特权级别
    printf("\n6. 通过SVC切换回特权级别\n");
    __asm volatile ("SVC #0");
    Print_Status();
    Privileged_Function();
    
    printf("\n========== 演示结束 ==========\n\n");
}

/**
 * @brief  EXTI0中断处理函数
 */
void EXTI0_IRQHandler(void)
{
    printf("进入中断处理函数\n");
    Print_Status();  // 会显示：处理器模式 + 特权级别 + MSP
    
    // 清除中断标志
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
    
    printf("退出中断处理函数\n");
}

/**
 * @brief  SVC处理函数
 */
void SVC_Handler(void)
{
    printf("进入SVC处理函数\n");
    Print_Status();  // 会显示：处理器模式 + 特权级别 + MSP
    
    // 切换回特权级别
    uint32_t control = __get_CONTROL();
    control &= ~CONTROL_nPRIV_Msk;
    __set_CONTROL(control);
    __ISB();
    
    printf("已切换回特权级别\n");
}
```

### RTOS中的应用

在实时操作系统（RTOS）中，处理器模式和特权级别被广泛使用：

```c
/**
 * @brief  RTOS任务切换示例
 * @note   简化的RTOS任务切换机制
 */

// 任务控制块
typedef struct {
    uint32_t *stack_ptr;  // 任务栈指针
    uint32_t priority;    // 任务优先级
    uint32_t state;       // 任务状态
} Task_TCB;

Task_TCB task1_tcb;
Task_TCB task2_tcb;
Task_TCB *current_task;

/**
 * @brief  创建任务
 * @param  tcb: 任务控制块
 * @param  task_func: 任务函数
 * @param  stack: 任务栈
 * @param  stack_size: 栈大小
 */
void Create_Task(Task_TCB *tcb, void (*task_func)(void), 
                 uint32_t *stack, uint32_t stack_size)
{
    // 初始化任务栈
    uint32_t *stack_top = &stack[stack_size - 16];
    
    // 设置初始栈帧（模拟异常返回）
    stack_top[15] = 0x01000000;  // xPSR (Thumb bit)
    stack_top[14] = (uint32_t)task_func;  // PC
    stack_top[13] = 0xFFFFFFFD;  // LR (返回线程模式，使用PSP)
    // ... 其他寄存器
    
    // 保存栈指针
    tcb->stack_ptr = stack_top;
}

/**
 * @brief  启动第一个任务
 */
void Start_First_Task(void)
{
    // 切换到PSP
    __set_PSP((uint32_t)current_task->stack_ptr);
    
    uint32_t control = __get_CONTROL();
    control |= CONTROL_SPSEL_Msk;  // 使用PSP
    control |= CONTROL_nPRIV_Msk;  // 非特权级别
    __set_CONTROL(control);
    __ISB();
    
    // 触发PendSV进行任务切换
    SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
}

/**
 * @brief  PendSV处理函数（任务切换）
 * @note   在处理器模式下执行，特权级别
 */
void PendSV_Handler(void)
{
    // 保存当前任务上下文
    __asm volatile (
        "MRS R0, PSP\n"           // 获取PSP
        "STMDB R0!, {R4-R11}\n"   // 保存R4-R11到栈
        "STR R0, [%0]\n"          // 保存新的栈指针
        :
        : "r" (&current_task->stack_ptr)
        : "r0"
    );
    
    // 选择下一个任务
    // current_task = next_task;
    
    // 恢复新任务上下文
    __asm volatile (
        "LDR R0, [%0]\n"          // 加载新任务栈指针
        "LDMIA R0!, {R4-R11}\n"   // 恢复R4-R11
        "MSR PSP, R0\n"           // 设置PSP
        "BX LR\n"                 // 返回
        :
        : "r" (&current_task->stack_ptr)
        : "r0"
    );
}

/**
 * @brief  任务1
 */
void Task1(void)
{
    while(1) {
        printf("Task1 running\n");
        // 任务在非特权级别运行
        // 使用PSP
        HAL_Delay(1000);
    }
}

/**
 * @brief  任务2
 */
void Task2(void)
{
    while(1) {
        printf("Task2 running\n");
        // 任务在非特权级别运行
        // 使用PSP
        HAL_Delay(1000);
    }
}
```

## 第五部分：安全性考虑

### 使用特权级别保护系统

合理使用特权级别可以提高系统的安全性和稳定性：

```c
/**
 * @brief  系统初始化（特权级别）
 */
void System_Init(void)
{
    // 在特权级别下初始化系统
    HAL_Init();
    SystemClock_Config();
    
    // 配置MPU保护关键区域
    Configure_MPU();
    
    // 配置关键外设
    Configure_Critical_Peripherals();
    
    // 初始化用户栈
    Init_User_Stack();
    
    // 切换到非特权级别运行用户代码
    Switch_To_Unprivileged();
    
    // 现在用户代码在非特权级别运行
    User_Application();
}

/**
 * @brief  配置MPU保护系统区域
 */
void Configure_MPU(void)
{
    // 禁用MPU
    MPU->CTRL = 0;
    
    // 配置区域0：保护系统代码（只读）
    MPU->RBAR = 0x08000000 | MPU_REGION_NUMBER0;
    MPU->RASR = MPU_RASR_ENABLE_Msk | 
                MPU_RASR_SIZE_64KB |
                MPU_RASR_AP_RO;  // 只读
    
    // 配置区域1：保护系统数据（特权读写）
    MPU->RBAR = 0x20000000 | MPU_REGION_NUMBER1;
    MPU->RASR = MPU_RASR_ENABLE_Msk | 
                MPU_RASR_SIZE_4KB |
                MPU_RASR_AP_PRIV_RW;  // 特权读写
    
    // 配置区域2：用户数据（用户读写）
    MPU->RBAR = 0x20001000 | MPU_REGION_NUMBER2;
    MPU->RASR = MPU_RASR_ENABLE_Msk | 
                MPU_RASR_SIZE_16KB |
                MPU_RASR_AP_FULL;  // 完全访问
    
    // 使能MPU
    MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
}

/**
 * @brief  用户应用程序（非特权级别）
 */
void User_Application(void)
{
    // 用户代码在非特权级别运行
    // 不能访问系统保护的区域
    
    while(1) {
        // 执行用户任务
        User_Task();
        
        // 需要系统服务时，通过SVC调用
        if (Need_System_Service()) {
            Request_System_Service();
        }
    }
}

/**
 * @brief  系统服务请求
 */
void Request_System_Service(void)
{
    // 使用SVC指令请求系统服务
    __asm volatile ("SVC #1");
}

/**
 * @brief  SVC处理函数（特权级别）
 */
void SVC_Handler(void)
{
    // 获取SVC号
    uint32_t *stack_frame;
    if (__get_CONTROL() & CONTROL_SPSEL_Msk) {
        stack_frame = (uint32_t*)__get_PSP();
    } else {
        stack_frame = (uint32_t*)__get_MSP();
    }
    
    uint32_t pc = stack_frame[6];  // 返回地址
    uint8_t svc_number = ((uint8_t*)pc)[-2];  // SVC号
    
    // 根据SVC号执行相应的系统服务
    switch(svc_number) {
        case 0:
            // 切换回特权级别
            __set_CONTROL(__get_CONTROL() & ~CONTROL_nPRIV_Msk);
            __ISB();
            break;
            
        case 1:
            // 执行系统服务
            Execute_System_Service();
            break;
            
        default:
            // 未知的SVC号
            break;
    }
}
```


### 错误处理

当非特权代码尝试执行特权操作时，会触发错误：

```c
/**
 * @brief  MemManage错误处理函数
 * @note   当MPU检测到非法访问时触发
 */
void MemManage_Handler(void)
{
    printf("MemManage错误！\n");
    
    // 检查错误类型
    uint32_t cfsr = SCB->CFSR;
    
    if (cfsr & SCB_CFSR_IACCVIOL_Msk) {
        printf("指令访问违规\n");
    }
    if (cfsr & SCB_CFSR_DACCVIOL_Msk) {
        printf("数据访问违规\n");
        
        // 获取违规地址
        uint32_t mmfar = SCB->MMFAR;
        printf("违规地址: 0x%08X\n", mmfar);
    }
    if (cfsr & SCB_CFSR_MSTKERR_Msk) {
        printf("入栈错误\n");
    }
    if (cfsr & SCB_CFSR_MUNSTKERR_Msk) {
        printf("出栈错误\n");
    }
    
    // 清除错误标志
    SCB->CFSR = cfsr;
    
    // 错误处理
    Error_Handler();
}

/**
 * @brief  UsageFault错误处理函数
 * @note   当执行非法指令时触发
 */
void UsageFault_Handler(void)
{
    printf("UsageFault错误！\n");
    
    // 检查错误类型
    uint32_t cfsr = SCB->CFSR;
    
    if (cfsr & SCB_CFSR_UNDEFINSTR_Msk) {
        printf("未定义指令\n");
    }
    if (cfsr & SCB_CFSR_INVSTATE_Msk) {
        printf("无效状态\n");
    }
    if (cfsr & SCB_CFSR_INVPC_Msk) {
        printf("无效PC\n");
    }
    if (cfsr & SCB_CFSR_NOCP_Msk) {
        printf("无协处理器\n");
    }
    if (cfsr & SCB_CFSR_UNALIGNED_Msk) {
        printf("未对齐访问\n");
    }
    if (cfsr & SCB_CFSR_DIVBYZERO_Msk) {
        printf("除零错误\n");
    }
    
    // 清除错误标志
    SCB->CFSR = cfsr;
    
    // 错误处理
    Error_Handler();
}
```

## 总结

本文详细介绍了ARM Cortex-M处理器的工作模式和特权级别，主要内容包括：

### 核心要点

1. **两种工作模式**：
   - 线程模式：执行应用代码
   - 处理器模式：执行异常处理代码

2. **两种特权级别**：
   - 特权级别：完全访问权限
   - 非特权级别：受限访问权限

3. **CONTROL寄存器**：
   - nPRIV位：控制特权级别
   - SPSEL位：选择栈指针
   - 只能在特权级别修改

4. **模式切换**：
   - 异常触发：线程模式 → 处理器模式
   - 异常返回：处理器模式 → 线程模式
   - 特权切换：需要通过SVC或异常

5. **安全应用**：
   - 使用MPU保护关键区域
   - 用户代码运行在非特权级别
   - 通过SVC提供系统服务

### 最佳实践

1. **系统设计**：
   - 系统代码运行在特权级别
   - 用户代码运行在非特权级别
   - 使用MPU保护关键资源

2. **RTOS应用**：
   - 任务使用PSP和非特权级别
   - 内核使用MSP和特权级别
   - 通过PendSV进行任务切换

3. **错误处理**：
   - 使能MemManage和UsageFault
   - 提供详细的错误信息
   - 实现错误恢复机制

### 应用场景

1. **裸机应用**：
   - 简单应用可以一直使用特权级别
   - 复杂应用可以使用非特权级别保护系统

2. **RTOS应用**：
   - 必须使用不同的模式和特权级别
   - 实现任务隔离和保护

3. **安全应用**：
   - 使用MPU和特权级别
   - 保护关键代码和数据
   - 防止恶意代码攻击

## 延伸阅读

推荐进一步学习的内容：

1. **内存保护**：
   - [MPU内存保护单元配置实战](../intermediate/04-mpu-configuration.html)
   - [内存访问权限管理](link)
   - [安全启动技术](link)

2. **RTOS相关**：
   - [FreeRTOS任务管理](link)
   - [任务切换机制详解](link)
   - [系统调用实现](link)

3. **高级主题**：
   - [TrustZone安全技术](link)
   - [安全固件设计](link)
   - [代码保护技术](link)

## 参考资料

1. ARM Cortex-M3权威指南 - Joseph Yiu
2. ARM Architecture Reference Manual
3. STM32 Cortex-M3编程手册 - ST Microelectronics
4. The Definitive Guide to ARM Cortex-M0 and Cortex-M0+ Processors

---

**练习题**：

1. 解释线程模式和处理器模式的区别，并说明何时会发生模式切换。

2. 编写代码实现以下功能：
   - 在特权级别下初始化系统
   - 切换到非特权级别运行用户代码
   - 通过SVC切换回特权级别

3. 分析以下代码的执行结果：
   ```c
   void Test_Function(void)
   {
       // 当前在线程模式，特权级别
       printf("1. 当前状态\n");
       Print_Status();
       
       // 切换到非特权级别
       __set_CONTROL(__get_CONTROL() | CONTROL_nPRIV_Msk);
       __ISB();
       
       printf("2. 切换后状态\n");
       Print_Status();
       
       // 尝试修改CONTROL寄存器
       __set_CONTROL(__get_CONTROL() & ~CONTROL_nPRIV_Msk);
       __ISB();
       
       printf("3. 尝试切换后状态\n");
       Print_Status();
   }
   ```
   说明每一步的状态变化。

4. 设计一个简单的系统，要求：
   - 系统代码运行在特权级别
   - 用户代码运行在非特权级别
   - 使用MPU保护系统内存
   - 提供系统调用接口

5. 解释为什么RTOS需要使用PSP和非特权级别？如果不使用会有什么问题？

**下一步**：建议学习 [寄存器操作与位操作技巧](07-register-operations.html)，掌握高效的寄存器操作方法。
