---
# 基础信息
title: "中断向量表与异常处理机制"
description: "深入讲解ARM Cortex-M处理器的中断向量表结构、异常类型分类、优先级管理、NVIC配置和异常处理流程，掌握中断系统的核心机制"
slug: "interrupt-vector-table-and-exception-handling"

# 分类信息
domain: "01-hardware-layer"
module: "01-chip-architecture"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 中断
  - 异常处理
  - NVIC
  - 向量表
  - ARM Cortex-M
prerequisites:
  - "05-stm32-boot-process"
related_contents:
  - "06-processor-modes"

# 学习信息
estimated_time: 35
difficulty_score: 3

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
  - 中断向量表
  - 异常处理
  - NVIC配置
  - 中断优先级
  - ARM异常机制
cover_image: ""
---

# 中断向量表与异常处理机制

## 学习目标

完成本文学习后，你将能够：

- [ ] 理解中断向量表的结构和组织方式
- [ ] 掌握ARM Cortex-M的异常类型分类
- [ ] 了解异常优先级的管理机制
- [ ] 掌握NVIC（嵌套向量中断控制器）的配置方法
- [ ] 理解异常处理的完整流程
- [ ] 能够编写中断服务函数
- [ ] 掌握中断优先级分组和抢占机制

## 前置要求

在开始本文学习之前，你需要：

**知识要求**：
- 了解ARM Cortex-M架构基础
- 熟悉C语言和基本的汇编语言
- 掌握内存映射和地址空间概念
- 了解处理器工作模式和特权级别

**技能要求**：
- 能够阅读和编写C代码
- 了解寄存器操作方法
- 熟悉基本的调试技巧

**推荐但非必需**：
- 有STM32或其他ARM MCU开发经验
- 了解启动流程和系统初始化
- 熟悉外设编程基础

## 概述

中断和异常是嵌入式系统中最重要的机制之一，它们使处理器能够及时响应外部事件和内部错误。ARM Cortex-M处理器提供了一套完整的异常处理机制，包括中断向量表、NVIC控制器和灵活的优先级管理系统。

### 为什么需要中断机制

1. **实时响应**：
   - 及时处理外部事件（按键、传感器、通信）
   - 避免轮询带来的延迟和资源浪费
   - 提高系统响应速度

2. **多任务处理**：
   - 支持多个外设同时工作
   - 实现事件驱动的程序架构
   - 提高CPU利用率

3. **错误处理**：
   - 检测和处理系统错误
   - 实现故障恢复机制
   - 提高系统可靠性

4. **功耗优化**：
   - CPU可以进入低功耗模式
   - 事件发生时自动唤醒
   - 降低系统功耗


### 中断与异常的区别

在ARM Cortex-M中，"异常"是一个更广泛的概念，包括中断和其他异常事件：

```
异常 (Exception)
├── 系统异常 (System Exceptions)
│   ├── Reset (复位)
│   ├── NMI (不可屏蔽中断)
│   ├── HardFault (硬件错误)
│   ├── MemManage (内存管理错误)
│   ├── BusFault (总线错误)
│   ├── UsageFault (用法错误)
│   ├── SVC (系统服务调用)
│   ├── PendSV (可挂起的系统调用)
│   └── SysTick (系统滴答定时器)
└── 外部中断 (External Interrupts)
    ├── IRQ0 - IRQ239
    └── 由外设产生
```

**术语说明**：
- **异常（Exception）**：所有打断正常程序流程的事件
- **中断（Interrupt）**：由外设产生的异常
- **系统异常**：由处理器内部产生的异常
- **外部中断**：由外设产生的中断请求

## 第一部分：中断向量表结构

### 向量表的作用

中断向量表是一个包含所有异常处理函数地址的数组，位于内存的固定位置。当异常发生时，处理器会从向量表中读取对应的处理函数地址并跳转执行。

**向量表的关键特性**：

1. **固定位置**：
   - 默认位于地址0x00000000
   - 可以通过VTOR寄存器重定位
   - 必须256字节对齐

2. **固定格式**：
   - 第一个条目是初始栈指针值
   - 后续条目是异常处理函数地址
   - 每个条目占4字节（32位）

3. **优先级顺序**：
   - 表中位置决定了异常编号
   - 异常编号影响默认优先级
   - 系统异常在前，外部中断在后


### 向量表详细结构

以STM32F103为例，向量表的完整结构如下：

```
地址偏移    异常编号    异常名称                    说明
0x0000      -           __initial_sp               初始栈指针值
0x0004      1           Reset_Handler              复位处理函数
0x0008      2           NMI_Handler                不可屏蔽中断
0x000C      3           HardFault_Handler          硬件错误
0x0010      4           MemManage_Handler          内存管理错误
0x0014      5           BusFault_Handler           总线错误
0x0018      6           UsageFault_Handler         用法错误
0x001C      7           保留                        -
0x0020      8           保留                        -
0x0024      9           保留                        -
0x0028      10          保留                        -
0x002C      11          SVC_Handler                系统服务调用
0x0030      12          DebugMon_Handler           调试监视器
0x0034      13          保留                        -
0x0038      14          PendSV_Handler             可挂起的系统调用
0x003C      15          SysTick_Handler            系统滴答定时器
0x0040      16          WWDG_IRQHandler            窗口看门狗
0x0044      17          PVD_IRQHandler             电源电压检测
0x0048      18          TAMPER_IRQHandler          侵入检测
0x004C      19          RTC_IRQHandler             RTC全局中断
0x0050      20          FLASH_IRQHandler           Flash全局中断
0x0054      21          RCC_IRQHandler             RCC全局中断
0x0058      22          EXTI0_IRQHandler           外部中断线0
0x005C      23          EXTI1_IRQHandler           外部中断线1
...         ...         ...                        更多外设中断
```

**重要说明**：

1. **异常编号**：
   - 从1开始编号（0是栈指针）
   - 1-15是系统异常
   - 16及以上是外部中断（IRQ0对应异常16）

2. **保留位置**：
   - 某些位置保留供将来使用
   - 必须填充为0或默认处理函数

3. **外设中断**：
   - 不同芯片的外设中断数量不同
   - STM32F103有60个外设中断
   - STM32F4系列可能有90+个中断


### 启动文件中的向量表定义

在启动文件（startup_stm32f1xx.s）中，向量表是这样定义的：

```assembly
; 向量表定义
                AREA    RESET, DATA, READONLY
                EXPORT  __Vectors
                EXPORT  __Vectors_End
                EXPORT  __Vectors_Size

__Vectors       DCD     __initial_sp              ; 栈顶地址
                DCD     Reset_Handler             ; 复位向量
                DCD     NMI_Handler               ; NMI处理函数
                DCD     HardFault_Handler         ; 硬件错误处理
                DCD     MemManage_Handler         ; 内存管理错误
                DCD     BusFault_Handler          ; 总线错误
                DCD     UsageFault_Handler        ; 用法错误
                DCD     0                         ; 保留
                DCD     0                         ; 保留
                DCD     0                         ; 保留
                DCD     0                         ; 保留
                DCD     SVC_Handler               ; SVC处理函数
                DCD     DebugMon_Handler          ; 调试监视器
                DCD     0                         ; 保留
                DCD     PendSV_Handler            ; PendSV处理函数
                DCD     SysTick_Handler           ; SysTick处理函数

                ; 外部中断
                DCD     WWDG_IRQHandler           ; 窗口看门狗
                DCD     PVD_IRQHandler            ; PVD通过EXTI检测
                DCD     TAMPER_IRQHandler         ; 侵入检测
                DCD     RTC_IRQHandler            ; RTC全局中断
                DCD     FLASH_IRQHandler          ; Flash全局中断
                DCD     RCC_IRQHandler            ; RCC全局中断
                DCD     EXTI0_IRQHandler          ; 外部中断线0
                DCD     EXTI1_IRQHandler          ; 外部中断线1
                ; ... 更多中断向量
                
__Vectors_End

__Vectors_Size  EQU  __Vectors_End - __Vectors

                AREA    |.text|, CODE, READONLY
```

**代码说明**：

- `AREA RESET, DATA, READONLY`：定义只读数据区域
- `DCD`：定义一个32位常量（Define Constant Data）
- `__initial_sp`：栈顶地址，由链接脚本定义
- `EXPORT`：导出符号，使其他文件可以引用
- `EQU`：定义常量，计算向量表大小


### 向量表重定位

默认情况下，向量表位于Flash的起始地址（0x08000000），但可以通过VTOR（Vector Table Offset Register）寄存器将其重定位到其他位置。

**VTOR寄存器**：

```c
/**
 * @brief  向量表偏移寄存器 (VTOR)
 * @note   位于SCB (System Control Block)
 */
#define SCB_VTOR  (*((volatile uint32_t*)0xE000ED08))

// VTOR寄存器位定义
// bit 31-7: TBLOFF - 向量表偏移地址（必须256字节对齐）
// bit 6-0:  保留，必须为0
```

**重定位向量表示例**：

```c
/**
 * @brief  重定位向量表到SRAM
 * @note   用于在SRAM中运行代码或实现动态向量表
 */
void Relocate_Vector_Table_To_SRAM(void)
{
    extern uint32_t __Vectors[];  // 向量表起始地址
    uint32_t *src = __Vectors;
    uint32_t *dst = (uint32_t*)0x20000000;  // SRAM起始地址
    uint32_t vector_count = 16 + 60;  // 系统异常 + 外设中断
    
    /* 1. 复制向量表到SRAM */
    for (uint32_t i = 0; i < vector_count; i++) {
        dst[i] = src[i];
    }
    
    /* 2. 设置VTOR指向新位置 */
    SCB->VTOR = 0x20000000;
    
    /* 3. 指令同步屏障 */
    __DSB();
    __ISB();
    
    printf("向量表已重定位到SRAM: 0x%08X\n", SCB->VTOR);
}

/**
 * @brief  重定位向量表到Flash的其他位置
 * @param  offset: 偏移地址（必须256字节对齐）
 */
void Relocate_Vector_Table(uint32_t offset)
{
    /* 检查对齐 */
    if (offset & 0xFF) {
        printf("错误：向量表地址必须256字节对齐\n");
        return;
    }
    
    /* 设置VTOR */
    SCB->VTOR = FLASH_BASE + offset;
    __DSB();
    __ISB();
    
    printf("向量表已重定位到: 0x%08X\n", SCB->VTOR);
}
```

**重定位的应用场景**：

1. **Bootloader应用**：
   - Bootloader使用默认向量表
   - 应用程序使用重定位的向量表
   - 实现固件升级功能

2. **在SRAM中运行**：
   - 提高中断响应速度
   - 实现动态修改向量表
   - 用于特殊调试场景

3. **多应用程序**：
   - 不同应用使用不同向量表
   - 实现应用隔离
   - 支持应用切换


## 第二部分：异常类型详解

### 系统异常

系统异常是由处理器内部产生的异常，用于处理系统级事件和错误。

#### 1. Reset (异常1)

**触发条件**：
- 上电复位
- 外部复位引脚
- 看门狗复位
- 软件复位

**处理函数**：
```c
/**
 * @brief  复位处理函数
 * @note   系统启动后执行的第一个函数
 */
void Reset_Handler(void)
{
    // 调用系统初始化
    SystemInit();
    
    // 跳转到main函数
    __main();
}
```

#### 2. NMI - 不可屏蔽中断 (异常2)

**特点**：
- 不能被禁用或屏蔽
- 优先级固定为-2（仅次于Reset）
- 用于处理关键错误

**典型应用**：
```c
/**
 * @brief  NMI处理函数
 * @note   处理关键系统错误
 */
void NMI_Handler(void)
{
    /* 检查RCC时钟安全系统 */
    if (RCC->CIR & RCC_CIR_CSSF) {
        printf("时钟安全系统检测到HSE故障\n");
        
        /* 清除标志 */
        RCC->CIR |= RCC_CIR_CSSC;
        
        /* 切换到HSI时钟 */
        RCC->CR |= RCC_CR_HSION;
        while(!(RCC->CR & RCC_CR_HSIRDY));
        
        /* 切换系统时钟源 */
        RCC->CFGR &= ~RCC_CFGR_SW;
        RCC->CFGR |= RCC_CFGR_SW_HSI;
    }
    
    /* 其他NMI源处理 */
}
```

#### 3. HardFault - 硬件错误 (异常3)

**触发条件**：
- 访问无效内存地址
- 执行未定义指令
- 其他错误异常升级而来

**处理函数**：
```c
/**
 * @brief  HardFault处理函数
 * @note   捕获所有未处理的错误
 */
void HardFault_Handler(void)
{
    printf("HardFault异常！\n");
    
    /* 获取错误信息 */
    uint32_t cfsr = SCB->CFSR;  // 配置和状态寄存器
    uint32_t hfsr = SCB->HFSR;  // HardFault状态寄存器
    uint32_t dfsr = SCB->DFSR;  // 调试错误状态寄存器
    
    printf("CFSR = 0x%08X\n", cfsr);
    printf("HFSR = 0x%08X\n", hfsr);
    printf("DFSR = 0x%08X\n", dfsr);
    
    /* 检查是否由其他错误升级 */
    if (hfsr & SCB_HFSR_FORCED_Msk) {
        printf("由其他错误升级为HardFault\n");
    }
    
    /* 进入无限循环或复位 */
    while(1);
}
```


#### 4. MemManage - 内存管理错误 (异常4)

**触发条件**：
- MPU检测到非法内存访问
- 访问未定义的内存区域
- 违反内存访问权限

**处理函数**：
```c
/**
 * @brief  MemManage处理函数
 * @note   需要先使能MemManage异常
 */
void MemManage_Handler(void)
{
    printf("MemManage异常！\n");
    
    /* 检查错误类型 */
    uint32_t cfsr = SCB->CFSR;
    
    if (cfsr & SCB_CFSR_IACCVIOL_Msk) {
        printf("指令访问违规\n");
    }
    if (cfsr & SCB_CFSR_DACCVIOL_Msk) {
        printf("数据访问违规\n");
        
        /* 获取违规地址 */
        if (cfsr & SCB_CFSR_MMARVALID_Msk) {
            uint32_t mmfar = SCB->MMFAR;
            printf("违规地址: 0x%08X\n", mmfar);
        }
    }
    if (cfsr & SCB_CFSR_MSTKERR_Msk) {
        printf("入栈错误\n");
    }
    if (cfsr & SCB_CFSR_MUNSTKERR_Msk) {
        printf("出栈错误\n");
    }
    
    /* 清除错误标志 */
    SCB->CFSR = cfsr;
    
    while(1);
}

/**
 * @brief  使能MemManage异常
 */
void Enable_MemManage_Fault(void)
{
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk;
}
```

#### 5. BusFault - 总线错误 (异常5)

**触发条件**：
- 访问不存在的外设
- 总线访问超时
- 预取指令错误

**处理函数**：
```c
/**
 * @brief  BusFault处理函数
 */
void BusFault_Handler(void)
{
    printf("BusFault异常！\n");
    
    uint32_t cfsr = SCB->CFSR;
    
    if (cfsr & SCB_CFSR_IBUSERR_Msk) {
        printf("指令总线错误\n");
    }
    if (cfsr & SCB_CFSR_PRECISERR_Msk) {
        printf("精确数据总线错误\n");
        
        /* 获取错误地址 */
        if (cfsr & SCB_CFSR_BFARVALID_Msk) {
            uint32_t bfar = SCB->BFAR;
            printf("错误地址: 0x%08X\n", bfar);
        }
    }
    if (cfsr & SCB_CFSR_IMPRECISERR_Msk) {
        printf("非精确数据总线错误\n");
    }
    if (cfsr & SCB_CFSR_UNSTKERR_Msk) {
        printf("出栈总线错误\n");
    }
    if (cfsr & SCB_CFSR_STKERR_Msk) {
        printf("入栈总线错误\n");
    }
    
    SCB->CFSR = cfsr;
    while(1);
}
```


#### 6. UsageFault - 用法错误 (异常6)

**触发条件**：
- 执行未定义指令
- 未对齐的内存访问
- 除零错误（需使能）
- 协处理器访问错误

**处理函数**：
```c
/**
 * @brief  UsageFault处理函数
 */
void UsageFault_Handler(void)
{
    printf("UsageFault异常！\n");
    
    uint32_t cfsr = SCB->CFSR;
    
    if (cfsr & SCB_CFSR_UNDEFINSTR_Msk) {
        printf("未定义指令\n");
    }
    if (cfsr & SCB_CFSR_INVSTATE_Msk) {
        printf("无效状态\n");
    }
    if (cfsr & SCB_CFSR_INVPC_Msk) {
        printf("无效PC值\n");
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
    
    SCB->CFSR = cfsr;
    while(1);
}

/**
 * @brief  使能UsageFault异常
 */
void Enable_UsageFault(void)
{
    /* 使能UsageFault */
    SCB->SHCSR |= SCB_SHCSR_USGFAULTENA_Msk;
    
    /* 使能除零检测 */
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk;
    
    /* 使能未对齐访问检测 */
    SCB->CCR |= SCB_CCR_UNALIGN_TRP_Msk;
}
```

#### 7. SVC - 系统服务调用 (异常11)

**用途**：
- 用户程序请求系统服务
- 实现系统调用接口
- RTOS任务切换

**使用示例**：
```c
/**
 * @brief  触发SVC异常
 * @param  svc_num: SVC号
 */
void Trigger_SVC(uint8_t svc_num)
{
    __asm volatile ("SVC %0" : : "I" (svc_num));
}

/**
 * @brief  SVC处理函数
 */
void SVC_Handler(void)
{
    /* 获取栈帧 */
    uint32_t *stack_frame;
    if (__get_CONTROL() & CONTROL_SPSEL_Msk) {
        stack_frame = (uint32_t*)__get_PSP();
    } else {
        stack_frame = (uint32_t*)__get_MSP();
    }
    
    /* 获取返回地址 */
    uint32_t pc = stack_frame[6];
    
    /* 获取SVC号 */
    uint8_t svc_number = ((uint8_t*)pc)[-2];
    
    printf("SVC #%d 被调用\n", svc_number);
    
    /* 根据SVC号执行相应服务 */
    switch(svc_number) {
        case 0:
            // 系统服务0
            break;
        case 1:
            // 系统服务1
            break;
        default:
            printf("未知的SVC号\n");
            break;
    }
}
```


#### 8. PendSV - 可挂起的系统调用 (异常14)

**特点**：
- 可以被挂起和延迟执行
- 优先级可配置（通常设为最低）
- RTOS中用于任务切换

**应用示例**：
```c
/**
 * @brief  触发PendSV异常
 */
void Trigger_PendSV(void)
{
    SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
}

/**
 * @brief  PendSV处理函数
 * @note   RTOS中用于任务切换
 */
void PendSV_Handler(void)
{
    /* 保存当前任务上下文 */
    __asm volatile (
        "MRS R0, PSP\n"           // 获取PSP
        "STMDB R0!, {R4-R11}\n"   // 保存R4-R11到栈
        "STR R0, [%0]\n"          // 保存新的栈指针
        :
        : "r" (&current_task_sp)
        : "r0"
    );
    
    /* 选择下一个任务 */
    // next_task = scheduler();
    
    /* 恢复新任务上下文 */
    __asm volatile (
        "LDR R0, [%0]\n"          // 加载新任务栈指针
        "LDMIA R0!, {R4-R11}\n"   // 恢复R4-R11
        "MSR PSP, R0\n"           // 设置PSP
        "BX LR\n"                 // 返回
        :
        : "r" (&next_task_sp)
        : "r0"
    );
}
```

#### 9. SysTick - 系统滴答定时器 (异常15)

**用途**：
- 提供系统时基
- RTOS时间片调度
- 延时函数实现

**配置和使用**：
```c
/**
 * @brief  配置SysTick定时器
 * @param  ticks: 定时器重载值
 * @retval 0: 成功, 1: 失败
 */
uint32_t SysTick_Config(uint32_t ticks)
{
    /* 检查重载值范围 */
    if ((ticks - 1) > SysTick_LOAD_RELOAD_Msk) {
        return 1;  // 超出范围
    }
    
    /* 设置重载值 */
    SysTick->LOAD = ticks - 1;
    
    /* 设置优先级 */
    NVIC_SetPriority(SysTick_IRQn, (1UL << __NVIC_PRIO_BITS) - 1UL);
    
    /* 清除当前值 */
    SysTick->VAL = 0;
    
    /* 使能SysTick */
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |  // 使用处理器时钟
                    SysTick_CTRL_TICKINT_Msk |     // 使能中断
                    SysTick_CTRL_ENABLE_Msk;       // 使能定时器
    
    return 0;
}

/**
 * @brief  SysTick中断处理函数
 */
void SysTick_Handler(void)
{
    /* 更新系统滴答计数 */
    HAL_IncTick();
    
    /* RTOS时间片调度 */
    // OS_TimeSlice();
}

/**
 * @brief  配置1ms的SysTick
 */
void SysTick_Init_1ms(void)
{
    /* 假设系统时钟72MHz */
    SysTick_Config(72000);  // 72MHz / 72000 = 1kHz (1ms)
}
```


### 外部中断

外部中断由外设产生，用于通知处理器外部事件的发生。

**外部中断的特点**：

1. **数量众多**：
   - STM32F1系列：60个外部中断
   - STM32F4系列：90+个外部中断
   - 不同芯片型号数量不同

2. **可配置优先级**：
   - 每个中断都可以配置优先级
   - 支持抢占优先级和子优先级
   - 通过NVIC进行管理

3. **可以使能/禁用**：
   - 通过NVIC控制中断使能
   - 可以单独使能或禁用每个中断
   - 支持挂起和清除中断

**常见外设中断示例**：

```c
/**
 * @brief  EXTI0外部中断处理函数
 * @note   处理GPIO PA0的外部中断
 */
void EXTI0_IRQHandler(void)
{
    /* 检查中断标志 */
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        /* 清除中断标志 */
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        /* 处理中断事件 */
        printf("EXTI0中断触发\n");
        Handle_Button_Press();
    }
}

/**
 * @brief  USART1中断处理函数
 */
void USART1_IRQHandler(void)
{
    /* 接收中断 */
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
        UART_Receive_Callback(data);
    }
    
    /* 发送完成中断 */
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC)) {
        __HAL_UART_CLEAR_FLAG(&huart1, UART_FLAG_TC);
        UART_Transmit_Complete_Callback();
    }
}

/**
 * @brief  TIM2定时器中断处理函数
 */
void TIM2_IRQHandler(void)
{
    /* 更新中断 */
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        /* 定时器溢出处理 */
        Timer_Overflow_Callback();
    }
}
```

## 第三部分：NVIC配置

### NVIC简介

NVIC（Nested Vectored Interrupt Controller，嵌套向量中断控制器）是ARM Cortex-M处理器的中断管理单元，负责管理所有外部中断和部分系统异常。

**NVIC的主要功能**：

1. **中断使能/禁用**：
   - 控制每个中断的使能状态
   - 支持批量操作

2. **优先级管理**：
   - 配置中断优先级
   - 支持抢占和嵌套

3. **挂起管理**：
   - 设置和清除中断挂起状态
   - 查询中断状态

4. **活动状态**：
   - 查询中断是否正在执行
   - 支持中断嵌套


### NVIC寄存器

NVIC提供了一组寄存器用于中断管理：

```c
/**
 * @brief  NVIC寄存器结构
 */
typedef struct
{
    __IOM uint32_t ISER[8U];    // 中断使能寄存器
    uint32_t RESERVED0[24U];
    __IOM uint32_t ICER[8U];    // 中断清除使能寄存器
    uint32_t RESERVED1[24U];
    __IOM uint32_t ISPR[8U];    // 中断挂起寄存器
    uint32_t RESERVED2[24U];
    __IOM uint32_t ICPR[8U];    // 中断清除挂起寄存器
    uint32_t RESERVED3[24U];
    __IOM uint32_t IABR[8U];    // 中断活动位寄存器
    uint32_t RESERVED4[56U];
    __IOM uint8_t  IP[240U];    // 中断优先级寄存器
    uint32_t RESERVED5[644U];
    __OM  uint32_t STIR;        // 软件触发中断寄存器
} NVIC_Type;

#define NVIC  ((NVIC_Type*)0xE000E100UL)
```

**寄存器说明**：

1. **ISER (Interrupt Set-Enable Registers)**：
   - 使能中断
   - 写1使能对应中断
   - 读取返回使能状态

2. **ICER (Interrupt Clear-Enable Registers)**：
   - 禁用中断
   - 写1禁用对应中断

3. **ISPR (Interrupt Set-Pending Registers)**：
   - 设置中断挂起状态
   - 写1设置挂起

4. **ICPR (Interrupt Clear-Pending Registers)**：
   - 清除中断挂起状态
   - 写1清除挂起

5. **IABR (Interrupt Active Bit Registers)**：
   - 只读，显示中断活动状态
   - 1表示中断正在执行

6. **IP (Interrupt Priority Registers)**：
   - 配置中断优先级
   - 每个中断占8位

### NVIC基本操作

**使能和禁用中断**：

```c
/**
 * @brief  使能中断
 * @param  IRQn: 中断号
 */
void NVIC_EnableIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        NVIC->ISER[(((uint32_t)IRQn) >> 5UL)] = 
            (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    }
}

/**
 * @brief  禁用中断
 * @param  IRQn: 中断号
 */
void NVIC_DisableIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        NVIC->ICER[(((uint32_t)IRQn) >> 5UL)] = 
            (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    }
}

/**
 * @brief  获取中断使能状态
 * @param  IRQn: 中断号
 * @retval 0: 禁用, 1: 使能
 */
uint32_t NVIC_GetEnableIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        return ((uint32_t)(((NVIC->ISER[(((uint32_t)IRQn) >> 5UL)] & 
                (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
    }
    return 0;
}
```


**挂起和清除中断**：

```c
/**
 * @brief  设置中断挂起
 * @param  IRQn: 中断号
 */
void NVIC_SetPendingIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        NVIC->ISPR[(((uint32_t)IRQn) >> 5UL)] = 
            (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    }
}

/**
 * @brief  清除中断挂起
 * @param  IRQn: 中断号
 */
void NVIC_ClearPendingIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        NVIC->ICPR[(((uint32_t)IRQn) >> 5UL)] = 
            (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
    }
}

/**
 * @brief  获取中断挂起状态
 * @param  IRQn: 中断号
 * @retval 0: 未挂起, 1: 挂起
 */
uint32_t NVIC_GetPendingIRQ(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        return ((uint32_t)(((NVIC->ISPR[(((uint32_t)IRQn) >> 5UL)] & 
                (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
    }
    return 0;
}

/**
 * @brief  获取中断活动状态
 * @param  IRQn: 中断号
 * @retval 0: 未活动, 1: 活动
 */
uint32_t NVIC_GetActive(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        return ((uint32_t)(((NVIC->IABR[(((uint32_t)IRQn) >> 5UL)] & 
                (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
    }
    return 0;
}
```

**配置中断优先级**：

```c
/**
 * @brief  设置中断优先级
 * @param  IRQn: 中断号
 * @param  priority: 优先级值（0-15，值越小优先级越高）
 */
void NVIC_SetPriority(IRQn_Type IRQn, uint32_t priority)
{
    if ((int32_t)(IRQn) >= 0) {
        NVIC->IP[((uint32_t)IRQn)] = 
            (uint8_t)((priority << (8U - __NVIC_PRIO_BITS)) & (uint32_t)0xFFUL);
    } else {
        SCB->SHP[(((uint32_t)IRQn) & 0xFUL)-4UL] = 
            (uint8_t)((priority << (8U - __NVIC_PRIO_BITS)) & (uint32_t)0xFFUL);
    }
}

/**
 * @brief  获取中断优先级
 * @param  IRQn: 中断号
 * @retval 优先级值
 */
uint32_t NVIC_GetPriority(IRQn_Type IRQn)
{
    if ((int32_t)(IRQn) >= 0) {
        return (uint32_t)(NVIC->IP[((uint32_t)IRQn)] >> (8U - __NVIC_PRIO_BITS));
    } else {
        return (uint32_t)(SCB->SHP[(((uint32_t)IRQn) & 0xFUL)-4UL] >> 
                         (8U - __NVIC_PRIO_BITS));
    }
}
```


### 优先级分组

ARM Cortex-M支持将优先级分为抢占优先级和子优先级两部分。

**优先级分组配置**：

```c
/**
 * @brief  配置优先级分组
 * @param  PriorityGroup: 优先级分组
 *   @arg NVIC_PRIORITYGROUP_0: 0位抢占优先级，4位子优先级
 *   @arg NVIC_PRIORITYGROUP_1: 1位抢占优先级，3位子优先级
 *   @arg NVIC_PRIORITYGROUP_2: 2位抢占优先级，2位子优先级
 *   @arg NVIC_PRIORITYGROUP_3: 3位抢占优先级，1位子优先级
 *   @arg NVIC_PRIORITYGROUP_4: 4位抢占优先级，0位子优先级
 */
void NVIC_SetPriorityGrouping(uint32_t PriorityGroup)
{
    uint32_t reg_value;
    uint32_t PriorityGroupTmp = (PriorityGroup & (uint32_t)0x07UL);
    
    reg_value = SCB->AIRCR;
    reg_value &= ~((uint32_t)(SCB_AIRCR_VECTKEY_Msk | SCB_AIRCR_PRIGROUP_Msk));
    reg_value = (reg_value |
                ((uint32_t)0x5FAUL << SCB_AIRCR_VECTKEY_Pos) |
                (PriorityGroupTmp << SCB_AIRCR_PRIGROUP_Pos));
    SCB->AIRCR = reg_value;
}

/**
 * @brief  获取优先级分组
 * @retval 优先级分组值
 */
uint32_t NVIC_GetPriorityGrouping(void)
{
    return ((uint32_t)((SCB->AIRCR & SCB_AIRCR_PRIGROUP_Msk) >> 
                       SCB_AIRCR_PRIGROUP_Pos));
}

/**
 * @brief  编码优先级
 * @param  PriorityGroup: 优先级分组
 * @param  PreemptPriority: 抢占优先级
 * @param  SubPriority: 子优先级
 * @retval 编码后的优先级值
 */
uint32_t NVIC_EncodePriority(uint32_t PriorityGroup, 
                             uint32_t PreemptPriority, 
                             uint32_t SubPriority)
{
    uint32_t PriorityGroupTmp = (PriorityGroup & (uint32_t)0x07UL);
    uint32_t PreemptPriorityBits;
    uint32_t SubPriorityBits;
    
    PreemptPriorityBits = ((7UL - PriorityGroupTmp) > (uint32_t)(__NVIC_PRIO_BITS)) ? 
                          (uint32_t)(__NVIC_PRIO_BITS) : (uint32_t)(7UL - PriorityGroupTmp);
    SubPriorityBits = ((PriorityGroupTmp + (uint32_t)(__NVIC_PRIO_BITS)) < (uint32_t)7UL) ? 
                      (uint32_t)0UL : (uint32_t)((PriorityGroupTmp - 7UL) + (uint32_t)(__NVIC_PRIO_BITS));
    
    return (
        ((PreemptPriority & (uint32_t)((1UL << (PreemptPriorityBits)) - 1UL)) << SubPriorityBits) |
        ((SubPriority & (uint32_t)((1UL << (SubPriorityBits)) - 1UL)))
    );
}
```

**优先级分组示例**：

```c
/**
 * @brief  配置中断优先级示例
 */
void Interrupt_Priority_Config(void)
{
    /* 配置优先级分组为2:2 */
    NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    /* 配置EXTI0中断：抢占优先级2，子优先级1 */
    uint32_t priority = NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 1);
    NVIC_SetPriority(EXTI0_IRQn, priority);
    NVIC_EnableIRQ(EXTI0_IRQn);
    
    /* 配置USART1中断：抢占优先级1，子优先级0 */
    priority = NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 1, 0);
    NVIC_SetPriority(USART1_IRQn, priority);
    NVIC_EnableIRQ(USART1_IRQn);
    
    /* 配置TIM2中断：抢占优先级2，子优先级2 */
    priority = NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 2);
    NVIC_SetPriority(TIM2_IRQn, priority);
    NVIC_EnableIRQ(TIM2_IRQn);
}
```


## 第四部分：异常处理流程

### 异常响应过程

当异常发生时，处理器会自动执行以下步骤：

```
1. 挂起当前指令执行
   ↓
2. 保存上下文到栈
   - xPSR, PC, LR, R12, R3-R0
   ↓
3. 更新LR为特殊值
   - 0xFFFFFFF9: 返回线程模式，使用MSP
   - 0xFFFFFFFD: 返回线程模式，使用PSP
   - 0xFFFFFFF1: 返回处理器模式，使用MSP
   ↓
4. 切换到处理器模式
   - 自动切换到特权级别
   - 使用MSP
   ↓
5. 从向量表读取处理函数地址
   ↓
6. 跳转到异常处理函数
   ↓
7. 执行异常处理代码
   ↓
8. 异常返回（BX LR）
   ↓
9. 自动恢复上下文
   ↓
10. 返回被打断的代码
```

**栈帧结构**：

```
异常发生时自动压栈的寄存器：

高地址
    ┌─────────┐
    │  xPSR   │  ← SP + 28
    ├─────────┤
    │   PC    │  ← SP + 24 (返回地址)
    ├─────────┤
    │   LR    │  ← SP + 20
    ├─────────┤
    │   R12   │  ← SP + 16
    ├─────────┤
    │   R3    │  ← SP + 12
    ├─────────┤
    │   R2    │  ← SP + 8
    ├─────────┤
    │   R1    │  ← SP + 4
    ├─────────┤
    │   R0    │  ← SP (栈指针)
    └─────────┘
低地址
```

**获取栈帧信息**：

```c
/**
 * @brief  获取异常栈帧
 * @retval 栈帧指针
 */
uint32_t* Get_Exception_Stack_Frame(void)
{
    uint32_t *stack_frame;
    
    /* 检查使用的栈指针 */
    if (__get_CONTROL() & CONTROL_SPSEL_Msk) {
        stack_frame = (uint32_t*)__get_PSP();
    } else {
        stack_frame = (uint32_t*)__get_MSP();
    }
    
    return stack_frame;
}

/**
 * @brief  打印异常栈帧信息
 */
void Print_Exception_Stack_Frame(void)
{
    uint32_t *stack_frame = Get_Exception_Stack_Frame();
    
    printf("=== 异常栈帧 ===\n");
    printf("R0  = 0x%08X\n", stack_frame[0]);
    printf("R1  = 0x%08X\n", stack_frame[1]);
    printf("R2  = 0x%08X\n", stack_frame[2]);
    printf("R3  = 0x%08X\n", stack_frame[3]);
    printf("R12 = 0x%08X\n", stack_frame[4]);
    printf("LR  = 0x%08X\n", stack_frame[5]);
    printf("PC  = 0x%08X\n", stack_frame[6]);
    printf("xPSR= 0x%08X\n", stack_frame[7]);
}
```


### 异常返回机制

异常返回通过执行`BX LR`指令实现，LR寄存器包含特殊的返回值（EXC_RETURN）。

**EXC_RETURN值**：

```
0xFFFFFFF1: 返回处理器模式，使用MSP
0xFFFFFFF9: 返回线程模式，使用MSP
0xFFFFFFFD: 返回线程模式，使用PSP
0xFFFFFFE1: 返回处理器模式，使用MSP，浮点上下文
0xFFFFFFE9: 返回线程模式，使用MSP，浮点上下文
0xFFFFFFED: 返回线程模式，使用PSP，浮点上下文
```

**异常返回示例**：

```c
/**
 * @brief  中断处理函数示例
 */
void EXTI0_IRQHandler(void)
{
    /* 处理中断 */
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0)) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        /* 中断处理代码 */
        Handle_Interrupt();
    }
    
    /* 函数返回时自动执行异常返回 */
    /* 编译器会生成 BX LR 指令 */
}
```

### 中断嵌套

ARM Cortex-M支持中断嵌套，高优先级中断可以打断低优先级中断。

**嵌套规则**：

1. **抢占优先级决定嵌套**：
   - 只有抢占优先级更高的中断才能嵌套
   - 子优先级不影响嵌套

2. **自动保存和恢复**：
   - 硬件自动保存被打断中断的上下文
   - 返回时自动恢复

3. **尾链优化**：
   - 连续的中断可以优化上下文切换
   - 减少压栈和出栈开销

**嵌套示例**：

```c
/**
 * @brief  低优先级中断（抢占优先级3）
 */
void TIM2_IRQHandler(void)
{
    printf("TIM2中断开始\n");
    
    /* 长时间处理 */
    for (volatile int i = 0; i < 1000000; i++);
    
    printf("TIM2中断结束\n");
}

/**
 * @brief  高优先级中断（抢占优先级1）
 */
void EXTI0_IRQHandler(void)
{
    printf("  EXTI0中断开始（嵌套）\n");
    
    /* 快速处理 */
    Handle_Critical_Event();
    
    printf("  EXTI0中断结束\n");
}

/**
 * @brief  配置中断嵌套
 */
void Configure_Nested_Interrupts(void)
{
    /* 配置优先级分组 */
    NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    /* TIM2: 抢占优先级3，子优先级0 */
    NVIC_SetPriority(TIM2_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 3, 0));
    NVIC_EnableIRQ(TIM2_IRQn);
    
    /* EXTI0: 抢占优先级1，子优先级0 */
    NVIC_SetPriority(EXTI0_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 1, 0));
    NVIC_EnableIRQ(EXTI0_IRQn);
}
```

**执行流程**：

```
主程序运行
    ↓
TIM2中断触发 → 进入TIM2_IRQHandler
    ↓
    正在执行TIM2处理代码
    ↓
    EXTI0中断触发（优先级更高）
    ↓
    保存TIM2上下文 → 进入EXTI0_IRQHandler
    ↓
    执行EXTI0处理代码
    ↓
    EXTI0返回 → 恢复TIM2上下文
    ↓
    继续执行TIM2处理代码
    ↓
TIM2返回 → 返回主程序
```


## 第五部分：中断编程实践

### 完整的中断配置流程

以配置外部中断为例，展示完整的中断配置过程：

```c
/**
 * @brief  配置EXTI0外部中断
 * @note   PA0引脚，下降沿触发
 */
void EXTI0_Config(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* 1. 使能GPIO时钟 */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    /* 2. 配置GPIO */
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿触发中断
    GPIO_InitStruct.Pull = GPIO_PULLUP;           // 上拉
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    /* 3. 配置NVIC */
    /* 设置优先级分组 */
    NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    /* 设置中断优先级：抢占优先级2，子优先级1 */
    uint32_t priority = NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 1);
    NVIC_SetPriority(EXTI0_IRQn, priority);
    
    /* 使能中断 */
    NVIC_EnableIRQ(EXTI0_IRQn);
    
    printf("EXTI0中断已配置\n");
}

/**
 * @brief  EXTI0中断处理函数
 */
void EXTI0_IRQHandler(void)
{
    /* 检查中断标志 */
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0) != RESET) {
        /* 清除中断标志 */
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        /* 处理中断事件 */
        printf("按键按下\n");
        
        /* 翻转LED */
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
    }
}
```

### 定时器中断配置

```c
/**
 * @brief  配置TIM2定时器中断
 * @note   1ms定时中断
 */
void TIM2_Config(void)
{
    TIM_HandleTypeDef htim2;
    
    /* 1. 使能TIM2时钟 */
    __HAL_RCC_TIM2_CLK_ENABLE();
    
    /* 2. 配置定时器参数 */
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 7200 - 1;      // 预分频：72MHz/7200 = 10kHz
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 10 - 1;           // 周期：10kHz/10 = 1kHz (1ms)
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    
    if (HAL_TIM_Base_Init(&htim2) != HAL_OK) {
        Error_Handler();
    }
    
    /* 3. 配置NVIC */
    NVIC_SetPriority(TIM2_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 0));
    NVIC_EnableIRQ(TIM2_IRQn);
    
    /* 4. 启动定时器中断 */
    HAL_TIM_Base_Start_IT(&htim2);
    
    printf("TIM2定时器中断已配置\n");
}

/**
 * @brief  TIM2中断处理函数
 */
void TIM2_IRQHandler(void)
{
    /* 检查更新中断标志 */
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE) != RESET) {
        if (__HAL_TIM_GET_IT_SOURCE(&htim2, TIM_IT_UPDATE) != RESET) {
            /* 清除中断标志 */
            __HAL_TIM_CLEAR_IT(&htim2, TIM_IT_UPDATE);
            
            /* 定时器溢出处理 */
            static uint32_t counter = 0;
            counter++;
            
            if (counter >= 1000) {  // 1秒
                counter = 0;
                printf("1秒定时到\n");
            }
        }
    }
}
```


### UART中断配置

```c
/**
 * @brief  配置USART1中断
 */
void USART1_Config(void)
{
    UART_HandleTypeDef huart1;
    
    /* 1. 使能时钟 */
    __HAL_RCC_USART1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    /* 2. 配置GPIO */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_9 | GPIO_PIN_10;  // TX, RX
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    /* 3. 配置UART参数 */
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    
    if (HAL_UART_Init(&huart1) != HAL_OK) {
        Error_Handler();
    }
    
    /* 4. 配置NVIC */
    NVIC_SetPriority(USART1_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 1, 0));
    NVIC_EnableIRQ(USART1_IRQn);
    
    /* 5. 使能接收中断 */
    __HAL_UART_ENABLE_IT(&huart1, UART_IT_RXNE);
    
    printf("USART1中断已配置\n");
}

/**
 * @brief  USART1中断处理函数
 */
void USART1_IRQHandler(void)
{
    /* 接收中断 */
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE) != RESET) {
        if (__HAL_UART_GET_IT_SOURCE(&huart1, UART_IT_RXNE) != RESET) {
            /* 读取接收到的数据 */
            uint8_t data = (uint8_t)(huart1.Instance->DR & 0xFF);
            
            /* 处理接收数据 */
            UART_Receive_Handler(data);
        }
    }
    
    /* 发送完成中断 */
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC) != RESET) {
        if (__HAL_UART_GET_IT_SOURCE(&huart1, UART_IT_TC) != RESET) {
            __HAL_UART_CLEAR_FLAG(&huart1, UART_FLAG_TC);
            
            /* 发送完成处理 */
            UART_Transmit_Complete_Handler();
        }
    }
}

/**
 * @brief  UART接收数据处理
 */
void UART_Receive_Handler(uint8_t data)
{
    static uint8_t rx_buffer[256];
    static uint8_t rx_index = 0;
    
    /* 存储接收数据 */
    rx_buffer[rx_index++] = data;
    
    /* 检查是否接收完整帧 */
    if (data == '\n' || rx_index >= 256) {
        /* 处理接收到的数据 */
        Process_Received_Data(rx_buffer, rx_index);
        rx_index = 0;
    }
}
```

### 中断优先级管理

```c
/**
 * @brief  系统中断优先级配置
 * @note   统一管理所有中断的优先级
 */
void System_Interrupt_Priority_Config(void)
{
    /* 配置优先级分组：2位抢占，2位子优先级 */
    NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);
    
    /* 关键中断：抢占优先级0（最高） */
    NVIC_SetPriority(NMI_IRQn, 0);
    
    /* 高优先级中断：抢占优先级1 */
    NVIC_SetPriority(USART1_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 1, 0));
    NVIC_SetPriority(EXTI0_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 1, 1));
    
    /* 中等优先级中断：抢占优先级2 */
    NVIC_SetPriority(TIM2_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 0));
    NVIC_SetPriority(ADC1_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 2, 1));
    
    /* 低优先级中断：抢占优先级3 */
    NVIC_SetPriority(DMA1_Channel1_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 3, 0));
    
    /* 系统异常优先级 */
    NVIC_SetPriority(SysTick_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 3, 0));
    NVIC_SetPriority(PendSV_IRQn, NVIC_EncodePriority(NVIC_PRIORITYGROUP_2, 3, 3));
}
```


## 第六部分：中断编程最佳实践

### 中断服务函数设计原则

1. **快速执行**：
   - 中断处理应尽可能快
   - 避免长时间占用CPU
   - 复杂处理放到主循环

2. **最小化操作**：
   - 只做必要的处理
   - 设置标志位，主循环处理
   - 避免复杂计算

3. **避免阻塞**：
   - 不使用延时函数
   - 不等待外设就绪
   - 不使用printf（调试除外）

4. **保护共享资源**：
   - 使用临界区保护
   - 避免竞态条件
   - 使用原子操作

**良好的中断处理示例**：

```c
/* 全局标志和数据 */
volatile uint8_t uart_rx_flag = 0;
volatile uint8_t uart_rx_data = 0;

/**
 * @brief  UART中断处理函数（推荐）
 * @note   快速处理，设置标志
 */
void USART1_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        /* 读取数据 */
        uart_rx_data = (uint8_t)(huart1.Instance->DR & 0xFF);
        
        /* 设置标志 */
        uart_rx_flag = 1;
        
        /* 快速返回 */
    }
}

/**
 * @brief  主循环处理
 */
void main_loop(void)
{
    while(1) {
        /* 检查标志 */
        if (uart_rx_flag) {
            uart_rx_flag = 0;
            
            /* 在主循环中处理数据 */
            Process_UART_Data(uart_rx_data);
        }
        
        /* 其他任务 */
    }
}
```

**不推荐的中断处理**：

```c
/**
 * @brief  不推荐的中断处理函数
 * @note   包含延时和复杂处理
 */
void EXTI0_IRQHandler(void)
{
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0)) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        
        /* ❌ 不推荐：延时 */
        HAL_Delay(100);
        
        /* ❌ 不推荐：复杂计算 */
        float result = Complex_Calculation();
        
        /* ❌ 不推荐：printf */
        printf("Result: %f\n", result);
        
        /* ❌ 不推荐：等待外设 */
        while(!UART_Ready());
        Send_Data(result);
    }
}
```

### 临界区保护

```c
/**
 * @brief  进入临界区
 * @retval 之前的中断状态
 */
uint32_t Enter_Critical_Section(void)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    return primask;
}

/**
 * @brief  退出临界区
 * @param  primask: 之前的中断状态
 */
void Exit_Critical_Section(uint32_t primask)
{
    __set_PRIMASK(primask);
}

/**
 * @brief  使用临界区保护共享变量
 */
void Update_Shared_Variable(void)
{
    /* 进入临界区 */
    uint32_t primask = Enter_Critical_Section();
    
    /* 访问共享变量 */
    shared_counter++;
    shared_buffer[index] = data;
    
    /* 退出临界区 */
    Exit_Critical_Section(primask);
}

/**
 * @brief  使用宏简化临界区
 */
#define CRITICAL_SECTION_BEGIN()  uint32_t __primask = __get_PRIMASK(); __disable_irq()
#define CRITICAL_SECTION_END()    __set_PRIMASK(__primask)

void Example_Function(void)
{
    CRITICAL_SECTION_BEGIN();
    
    /* 临界区代码 */
    shared_data = new_value;
    
    CRITICAL_SECTION_END();
}
```


### 中断调试技巧

```c
/**
 * @brief  中断统计信息
 */
typedef struct {
    uint32_t count;           // 中断次数
    uint32_t max_duration;    // 最大执行时间
    uint32_t total_duration;  // 总执行时间
} IRQ_Stats_t;

IRQ_Stats_t irq_stats[60];  // 假设60个外设中断

/**
 * @brief  中断性能监控
 */
void IRQ_Performance_Monitor_Start(IRQn_Type IRQn)
{
    /* 启动DWT计数器 */
    DWT->CYCCNT = 0;
}

void IRQ_Performance_Monitor_End(IRQn_Type IRQn)
{
    /* 读取执行周期数 */
    uint32_t cycles = DWT->CYCCNT;
    
    /* 更新统计信息 */
    irq_stats[IRQn].count++;
    irq_stats[IRQn].total_duration += cycles;
    
    if (cycles > irq_stats[IRQn].max_duration) {
        irq_stats[IRQn].max_duration = cycles;
    }
}

/**
 * @brief  带性能监控的中断处理函数
 */
void EXTI0_IRQHandler(void)
{
    IRQ_Performance_Monitor_Start(EXTI0_IRQn);
    
    /* 中断处理代码 */
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0)) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        Handle_Interrupt();
    }
    
    IRQ_Performance_Monitor_End(EXTI0_IRQn);
}

/**
 * @brief  打印中断统计信息
 */
void Print_IRQ_Statistics(void)
{
    printf("=== 中断统计信息 ===\n");
    
    for (int i = 0; i < 60; i++) {
        if (irq_stats[i].count > 0) {
            uint32_t avg_cycles = irq_stats[i].total_duration / irq_stats[i].count;
            uint32_t avg_us = avg_cycles / (SystemCoreClock / 1000000);
            uint32_t max_us = irq_stats[i].max_duration / (SystemCoreClock / 1000000);
            
            printf("IRQ %d: 次数=%d, 平均=%dus, 最大=%dus\n",
                   i, irq_stats[i].count, avg_us, max_us);
        }
    }
}
```

### 中断丢失检测

```c
/**
 * @brief  中断丢失检测
 */
typedef struct {
    uint32_t expected_count;  // 期望的中断次数
    uint32_t actual_count;    // 实际的中断次数
    uint32_t lost_count;      // 丢失的中断次数
} IRQ_Monitor_t;

IRQ_Monitor_t irq_monitor;

/**
 * @brief  定时器中断（用于检测）
 */
void TIM2_IRQHandler(void)
{
    if (__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);
        
        /* 增加期望计数 */
        irq_monitor.expected_count++;
        
        /* 增加实际计数 */
        irq_monitor.actual_count++;
    }
}

/**
 * @brief  检查中断丢失
 */
void Check_IRQ_Lost(void)
{
    if (irq_monitor.actual_count < irq_monitor.expected_count) {
        irq_monitor.lost_count = irq_monitor.expected_count - irq_monitor.actual_count;
        printf("警告：检测到%d个中断丢失\n", irq_monitor.lost_count);
    }
}
```

## 总结

本文详细介绍了ARM Cortex-M处理器的中断向量表和异常处理机制，主要内容包括：

### 核心要点

1. **中断向量表**：
   - 包含所有异常处理函数地址的数组
   - 位于内存固定位置，可通过VTOR重定位
   - 第一个条目是栈指针，后续是异常处理函数地址

2. **异常类型**：
   - 系统异常：Reset, NMI, HardFault, MemManage, BusFault, UsageFault, SVC, PendSV, SysTick
   - 外部中断：由外设产生，数量因芯片而异

3. **NVIC控制器**：
   - 管理所有外部中断和部分系统异常
   - 支持中断使能/禁用、优先级配置、挂起管理
   - 提供灵活的优先级分组机制

4. **异常处理流程**：
   - 自动保存上下文到栈
   - 切换到处理器模式和特权级别
   - 执行异常处理函数
   - 自动恢复上下文并返回

5. **中断嵌套**：
   - 支持高优先级中断打断低优先级中断
   - 抢占优先级决定嵌套能力
   - 硬件自动管理上下文切换

### 最佳实践

1. **中断处理函数**：
   - 保持简短快速
   - 避免延时和阻塞操作
   - 使用标志位通知主循环

2. **优先级配置**：
   - 合理分配优先级
   - 关键中断使用高优先级
   - 统一管理优先级分组

3. **共享资源保护**：
   - 使用临界区保护
   - 避免竞态条件
   - 使用原子操作

4. **调试和监控**：
   - 添加性能监控
   - 检测中断丢失
   - 记录统计信息

## 延伸阅读

推荐进一步学习的内容：

1. **相关主题**：
   - [处理器工作模式与特权级别](06-processor-modes.html)
   - [STM32启动过程深度分析](05-stm32-boot-process.html)
   - [DMA工作原理与应用场景](../intermediate/03-dma-principles.html)

2. **高级主题**：
   - RTOS中的中断管理
   - 中断延迟优化
   - 实时性能分析

3. **实践项目**：
   - 多中断协同处理
   - 中断驱动的通信系统
   - 实时数据采集系统

## 参考资料

1. ARM Cortex-M3权威指南 - Joseph Yiu
2. ARM Cortex-M Programming Guide to Memory Barrier Instructions
3. STM32 Cortex-M3编程手册 - ST Microelectronics
4. The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors

---

**练习题**：

1. 解释中断向量表的结构，说明为什么第一个条目是栈指针而不是处理函数地址。

2. 编写代码实现以下功能：
   - 配置EXTI0外部中断（下降沿触发）
   - 配置TIM2定时器中断（1ms周期）
   - 设置合理的优先级，使EXTI0可以打断TIM2

3. 分析以下代码的问题并改正：
   ```c
   void EXTI0_IRQHandler(void)
   {
       __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
       
       HAL_Delay(100);  // 消抖延时
       
       if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET) {
           printf("按键按下\n");
           Process_Button();
       }
   }
   ```

4. 设计一个中断优先级方案，要求：
   - 系统有UART、定时器、ADC、按键四种中断源
   - UART数据不能丢失
   - 定时器需要精确计时
   - ADC采样可以延迟
   - 按键响应要求不高

5. 解释什么是中断嵌套，并说明在什么情况下会发生中断嵌套。

**下一步**：建议学习 [芯片数据手册阅读指南](09-datasheet-reading-guide.html)，掌握如何从数据手册中获取中断相关信息。
