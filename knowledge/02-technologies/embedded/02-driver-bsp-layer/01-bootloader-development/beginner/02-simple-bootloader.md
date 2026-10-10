---
title: "从零实现一个简单的Bootloader"
description: "通过实践教程，从零开始构建一个功能完整的简单Bootloader，包括启动代码编写、应用跳转、串口通信、固件下载和Flash编程，掌握Bootloader开发的核心技术"
slug: "simple-bootloader"

# 分类信息
domain: "驱动与BSP层"
module: "Bootloader开发"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - Bootloader开发
  - 固件下载
  - Flash编程
  - 串口通信
  - IAP升级
prerequisites:
  - "bootloader-basics"
related_contents:
  - "firmware-partition"
  - "bootloader-app-communication"

# 学习信息
estimated_time: 120
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
  - Bootloader实现
  - 固件升级
  - Flash编程
  - 串口IAP
  - 嵌入式开发
cover_image: ""
---

# 从零实现一个简单的Bootloader

## 概述

在上一篇文章中，我们学习了Bootloader的基础概念和工作原理。现在，让我们动手实践，从零开始构建一个功能完整的简单Bootloader。通过本教程，你将学会如何编写启动代码、实现应用程序跳转、配置串口通信、接收固件数据以及进行Flash编程。

完成本教程后，你将能够：

- 从零开始搭建Bootloader工程
- 实现基本的硬件初始化和应用程序跳转
- 通过串口接收固件数据
- 编写Flash擦除和编程函数
- 实现完整的固件下载和更新流程
- 理解Bootloader与应用程序的协同工作机制

## 准备工作

### 硬件要求

本教程使用以下硬件平台（可根据实际情况调整）：

- **开发板**：STM32F407VGT6开发板（或其他STM32F4系列）
- **调试器**：ST-Link V2或J-Link
- **串口工具**：USB转TTL模块
- **连接线**：杜邦线若干

**硬件连接**：
```
STM32F407          USB转TTL
PA9 (USART1_TX) -> RX
PA10 (USART1_RX) -> TX
GND              -> GND
```

### 软件要求

- **开发环境**：Keil MDK 5.x 或 STM32CubeIDE
- **编译器**：ARM Compiler 5/6 或 GCC
- **下载工具**：STM32 ST-LINK Utility
- **串口助手**：SecureCRT、Xshell或自定义上位机
- **固件库**：STM32F4xx HAL库或标准外设库

### 项目结构

创建以下项目目录结构：

```
SimpleBootloader/
├── Bootloader/              # Bootloader工程
│   ├── Core/
│   │   ├── Src/
│   │   │   ├── main.c
│   │   │   ├── flash.c
│   │   │   └── uart.c
│   │   └── Inc/
│   │       ├── flash.h
│   │       └── uart.h
│   ├── Drivers/             # STM32驱动库
│   └── STM32F407VGTx_FLASH.ld  # Bootloader链接脚本
│
└── Application/             # 应用程序工程
    ├── Core/
    ├── Drivers/
    └── STM32F407VGTx_FLASH.ld  # 应用程序链接脚本
```

## 核心内容

### 步骤1：Flash内存布局规划

首先，我们需要规划Flash的内存布局。STM32F407VGT6有1MB Flash，我们这样分配：

```
Flash布局（1MB总容量）：

0x08000000  ┌─────────────────────┐
            │  Bootloader         │  32KB (0x8000)
0x08008000  ├─────────────────────┤
            │  应用程序           │  480KB (0x78000)
0x08080000  ├─────────────────────┤
            │  升级缓存区         │  480KB (0x78000)
0x080F8000  ├─────────────────────┤
            │  参数存储区         │  32KB (0x8000)
0x08100000  └─────────────────────┘
```

**地址定义**：
```c
// flash.h
#ifndef __FLASH_H
#define __FLASH_H

#include "stm32f4xx.h"

// Flash地址定义
#define BOOTLOADER_START_ADDR   0x08000000
#define BOOTLOADER_SIZE         0x00008000  // 32KB

#define APP_START_ADDR          0x08008000
#define APP_SIZE                0x00078000  // 480KB

#define UPGRADE_START_ADDR      0x08080000
#define UPGRADE_SIZE            0x00078000  // 480KB

#define PARAM_START_ADDR        0x080F8000
#define PARAM_SIZE              0x00008000  // 32KB

// Flash扇区定义（STM32F407）
#define FLASH_SECTOR_0     0
#define FLASH_SECTOR_1     1
#define FLASH_SECTOR_2     2
#define FLASH_SECTOR_3     3
#define FLASH_SECTOR_4     4
#define FLASH_SECTOR_5     5
#define FLASH_SECTOR_6     6
#define FLASH_SECTOR_7     7
#define FLASH_SECTOR_8     8
#define FLASH_SECTOR_9     9
#define FLASH_SECTOR_10    10
#define FLASH_SECTOR_11    11

// 函数声明
void Flash_Unlock(void);
void Flash_Lock(void);
uint8_t Flash_EraseSector(uint8_t sector);
uint8_t Flash_WriteWord(uint32_t addr, uint32_t data);
uint8_t Flash_WriteBuffer(uint32_t addr, uint8_t *buf, uint32_t len);

#endif
```

### 步骤2：修改链接脚本

**Bootloader链接脚本**（STM32F407VGTx_FLASH.ld）：


```ld
/* Bootloader链接脚本 - 起始地址0x08000000，大小32KB */
MEMORY
{
  FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 32K
  RAM (xrw)       : ORIGIN = 0x20000000, LENGTH = 128K
  CCMRAM (rw)     : ORIGIN = 0x10000000, LENGTH = 64K
}

/* 其余部分保持标准配置 */
```

**应用程序链接脚本**（STM32F407VGTx_FLASH.ld）：

```ld
/* 应用程序链接脚本 - 起始地址0x08008000，大小480KB */
MEMORY
{
  FLASH (rx)      : ORIGIN = 0x08008000, LENGTH = 480K
  RAM (xrw)       : ORIGIN = 0x20000000, LENGTH = 128K
  CCMRAM (rw)     : ORIGIN = 0x10000000, LENGTH = 64K
}

/* 其余部分保持标准配置 */
```

### 步骤3：实现Flash操作函数

创建`flash.c`文件，实现Flash的基本操作：

```c
// flash.c
#include "flash.h"

// 解锁Flash
void Flash_Unlock(void) {
    if (FLASH->CR & FLASH_CR_LOCK) {
        FLASH->KEYR = 0x45670123;
        FLASH->KEYR = 0xCDEF89AB;
    }
}

// 锁定Flash
void Flash_Lock(void) {
    FLASH->CR |= FLASH_CR_LOCK;
}

// 等待Flash操作完成
static uint8_t Flash_WaitForLastOperation(uint32_t timeout) {
    uint32_t tickstart = HAL_GetTick();
    
    while ((FLASH->SR & FLASH_SR_BSY) != 0) {
        if ((HAL_GetTick() - tickstart) > timeout) {
            return 1;  // 超时
        }
    }
    
    // 检查错误标志
    if (FLASH->SR & (FLASH_SR_PGSERR | FLASH_SR_PGPERR | FLASH_SR_PGAERR)) {
        FLASH->SR = FLASH_SR_PGSERR | FLASH_SR_PGPERR | FLASH_SR_PGAERR;
        return 2;  // 错误
    }
    
    return 0;  // 成功
}

// 擦除Flash扇区
uint8_t Flash_EraseSector(uint8_t sector) {
    uint8_t status;
    
    // 等待上一次操作完成
    status = Flash_WaitForLastOperation(50000);
    if (status != 0) {
        return status;
    }
    
    // 配置擦除操作
    FLASH->CR &= ~FLASH_CR_PSIZE;
    FLASH->CR |= FLASH_CR_PSIZE_1;  // 32位并行
    FLASH->CR &= ~FLASH_CR_SNB;
    FLASH->CR |= (sector << FLASH_CR_SNB_Pos);
    FLASH->CR |= FLASH_CR_SER;      // 扇区擦除
    FLASH->CR |= FLASH_CR_STRT;     // 开始擦除
    
    // 等待擦除完成
    status = Flash_WaitForLastOperation(50000);
    
    // 清除擦除标志
    FLASH->CR &= ~FLASH_CR_SER;
    FLASH->CR &= ~FLASH_CR_SNB;
    
    return status;
}

// 写入一个字（32位）
uint8_t Flash_WriteWord(uint32_t addr, uint32_t data) {
    uint8_t status;
    
    // 等待上一次操作完成
    status = Flash_WaitForLastOperation(50000);
    if (status != 0) {
        return status;
    }
    
    // 配置编程操作
    FLASH->CR &= ~FLASH_CR_PSIZE;
    FLASH->CR |= FLASH_CR_PSIZE_1;  // 32位并行
    FLASH->CR |= FLASH_CR_PG;       // 编程使能
    
    // 写入数据
    *(__IO uint32_t*)addr = data;
    
    // 等待编程完成
    status = Flash_WaitForLastOperation(50000);
    
    // 清除编程标志
    FLASH->CR &= ~FLASH_CR_PG;
    
    return status;
}

// 写入缓冲区
uint8_t Flash_WriteBuffer(uint32_t addr, uint8_t *buf, uint32_t len) {
    uint32_t i;
    uint32_t word_data;
    uint8_t status;
    
    // 按字对齐写入
    for (i = 0; i < len; i += 4) {
        // 组装32位数据
        word_data = buf[i] | (buf[i+1] << 8) | (buf[i+2] << 16) | (buf[i+3] << 24);
        
        // 写入Flash
        status = Flash_WriteWord(addr + i, word_data);
        if (status != 0) {
            return status;
        }
    }
    
    return 0;
}

// 获取扇区号
uint8_t Flash_GetSector(uint32_t addr) {
    uint8_t sector = 0;
    
    if (addr < 0x08004000) {
        sector = FLASH_SECTOR_0;
    } else if (addr < 0x08008000) {
        sector = FLASH_SECTOR_1;
    } else if (addr < 0x0800C000) {
        sector = FLASH_SECTOR_2;
    } else if (addr < 0x08010000) {
        sector = FLASH_SECTOR_3;
    } else if (addr < 0x08020000) {
        sector = FLASH_SECTOR_4;
    } else if (addr < 0x08040000) {
        sector = FLASH_SECTOR_5;
    } else if (addr < 0x08060000) {
        sector = FLASH_SECTOR_6;
    } else if (addr < 0x08080000) {
        sector = FLASH_SECTOR_7;
    } else if (addr < 0x080A0000) {
        sector = FLASH_SECTOR_8;
    } else if (addr < 0x080C0000) {
        sector = FLASH_SECTOR_9;
    } else if (addr < 0x080E0000) {
        sector = FLASH_SECTOR_10;
    } else {
        sector = FLASH_SECTOR_11;
    }
    
    return sector;
}
```

### 步骤4：实现串口通信

创建`uart.c`文件，实现串口收发功能：

```c
// uart.h
#ifndef __UART_H
#define __UART_H

#include "stm32f4xx.h"
#include <stdint.h>

void UART_Init(void);
void UART_SendByte(uint8_t data);
void UART_SendString(char *str);
uint8_t UART_ReceiveByte(uint32_t timeout);
uint32_t UART_ReceiveBuffer(uint8_t *buf, uint32_t len, uint32_t timeout);

#endif
```

```c
// uart.c
#include "uart.h"

// 初始化UART1（PA9-TX, PA10-RX）
void UART_Init(void) {
    // 使能时钟
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    
    // 配置GPIO
    // PA9: TX, PA10: RX
    GPIOA->MODER &= ~(GPIO_MODER_MODER9 | GPIO_MODER_MODER10);
    GPIOA->MODER |= (GPIO_MODER_MODER9_1 | GPIO_MODER_MODER10_1);  // 复用功能
    
    GPIOA->AFR[1] &= ~(0xFF << 4);
    GPIOA->AFR[1] |= (0x77 << 4);  // AF7: USART1
    
    // 配置UART参数：115200, 8N1
    // 假设系统时钟84MHz，APB2时钟84MHz
    // BRR = 84000000 / 115200 = 729.166 ≈ 729 (0x2D9)
    USART1->BRR = 0x2D9;
    
    // 使能发送和接收
    USART1->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}

// 发送一个字节
void UART_SendByte(uint8_t data) {
    while (!(USART1->SR & USART_SR_TXE));
    USART1->DR = data;
}

// 发送字符串
void UART_SendString(char *str) {
    while (*str) {
        UART_SendByte(*str++);
    }
}

// 接收一个字节（带超时）
uint8_t UART_ReceiveByte(uint32_t timeout) {
    uint32_t tickstart = HAL_GetTick();
    
    while (!(USART1->SR & USART_SR_RXNE)) {
        if ((HAL_GetTick() - tickstart) > timeout) {
            return 0xFF;  // 超时返回0xFF
        }
    }
    
    return (uint8_t)(USART1->DR & 0xFF);
}

// 接收缓冲区
uint32_t UART_ReceiveBuffer(uint8_t *buf, uint32_t len, uint32_t timeout) {
    uint32_t i;
    uint8_t data;
    
    for (i = 0; i < len; i++) {
        data = UART_ReceiveByte(timeout);
        if (data == 0xFF) {
            return i;  // 超时，返回已接收字节数
        }
        buf[i] = data;
    }
    
    return len;
}
```

### 步骤5：实现应用程序跳转

在`main.c`中实现跳转功能：

```c
// main.c
#include "stm32f4xx.h"
#include "flash.h"
#include "uart.h"

// 应用程序起始地址
#define APP_START_ADDR  0x08008000

// 跳转到应用程序
void JumpToApplication(uint32_t app_addr) {
    // 检查栈指针是否有效（指向RAM区域）
    if (((*(__IO uint32_t*)app_addr) & 0x2FFE0000) == 0x20000000) {
        // 定义函数指针类型
        typedef void (*pFunction)(void);
        
        // 获取应用程序的栈指针和复位向量
        uint32_t app_sp = *(__IO uint32_t*)app_addr;
        uint32_t app_entry = *(__IO uint32_t*)(app_addr + 4);
        pFunction app_reset_handler = (pFunction)app_entry;
        
        // 关闭所有中断
        __disable_irq();
        
        // 关闭SysTick
        SysTick->CTRL = 0;
        SysTick->LOAD = 0;
        SysTick->VAL = 0;
        
        // 关闭所有外设（可选，根据需要）
        // RCC->APB1ENR = 0;
        // RCC->APB2ENR = 0;
        
        // 重新设置中断向量表偏移
        SCB->VTOR = app_addr;
        
        // 设置主堆栈指针
        __set_MSP(app_sp);
        
        // 跳转到应用程序
        app_reset_handler();
    }
}
```

### 步骤6：实现固件下载协议

定义一个简单的固件下载协议：


```c
// 固件下载协议定义
#define CMD_START       0xA5    // 开始下载命令
#define CMD_DATA        0xA6    // 数据包命令
#define CMD_END         0xA7    // 结束下载命令
#define CMD_ERASE       0xA8    // 擦除Flash命令

#define ACK_OK          0x79    // 应答成功
#define ACK_ERROR       0x1F    // 应答失败

// 数据包结构
typedef struct {
    uint8_t cmd;            // 命令字
    uint16_t seq;           // 序号
    uint16_t len;           // 数据长度
    uint8_t data[1024];     // 数据
    uint8_t checksum;       // 校验和
} FirmwarePacket;

// 计算校验和
uint8_t CalculateChecksum(uint8_t *data, uint16_t len) {
    uint8_t sum = 0;
    for (uint16_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum;
}

// 固件下载处理
void FirmwareDownload(void) {
    FirmwarePacket packet;
    uint32_t write_addr = UPGRADE_START_ADDR;
    uint16_t expected_seq = 0;
    uint8_t cmd;
    
    UART_SendString("\r\nBootloader Ready. Waiting for firmware...\r\n");
    
    while (1) {
        // 接收命令字
        cmd = UART_ReceiveByte(5000);
        
        switch (cmd) {
            case CMD_START:
                UART_SendString("Received START command\r\n");
                write_addr = UPGRADE_START_ADDR;
                expected_seq = 0;
                UART_SendByte(ACK_OK);
                break;
                
            case CMD_ERASE:
                UART_SendString("Erasing flash...\r\n");
                
                // 擦除升级区域的所有扇区
                Flash_Unlock();
                for (uint8_t sector = 8; sector <= 10; sector++) {
                    if (Flash_EraseSector(sector) != 0) {
                        UART_SendString("Erase failed!\r\n");
                        UART_SendByte(ACK_ERROR);
                        Flash_Lock();
                        return;
                    }
                }
                Flash_Lock();
                
                UART_SendString("Erase complete\r\n");
                UART_SendByte(ACK_OK);
                break;
                
            case CMD_DATA:
                // 接收序号（2字节）
                packet.seq = UART_ReceiveByte(1000);
                packet.seq |= (UART_ReceiveByte(1000) << 8);
                
                // 接收长度（2字节）
                packet.len = UART_ReceiveByte(1000);
                packet.len |= (UART_ReceiveByte(1000) << 8);
                
                // 检查序号
                if (packet.seq != expected_seq) {
                    UART_SendString("Sequence error!\r\n");
                    UART_SendByte(ACK_ERROR);
                    continue;
                }
                
                // 接收数据
                if (UART_ReceiveBuffer(packet.data, packet.len, 2000) != packet.len) {
                    UART_SendString("Data receive timeout!\r\n");
                    UART_SendByte(ACK_ERROR);
                    continue;
                }
                
                // 接收校验和
                packet.checksum = UART_ReceiveByte(1000);
                
                // 验证校验和
                uint8_t calc_sum = CalculateChecksum(packet.data, packet.len);
                if (calc_sum != packet.checksum) {
                    UART_SendString("Checksum error!\r\n");
                    UART_SendByte(ACK_ERROR);
                    continue;
                }
                
                // 写入Flash
                Flash_Unlock();
                if (Flash_WriteBuffer(write_addr, packet.data, packet.len) != 0) {
                    UART_SendString("Flash write error!\r\n");
                    UART_SendByte(ACK_ERROR);
                    Flash_Lock();
                    return;
                }
                Flash_Lock();
                
                // 更新地址和序号
                write_addr += packet.len;
                expected_seq++;
                
                UART_SendByte(ACK_OK);
                break;
                
            case CMD_END:
                UART_SendString("Download complete!\r\n");
                
                // 这里可以添加固件校验逻辑
                // 如果校验通过，将固件从升级区复制到应用区
                
                UART_SendByte(ACK_OK);
                return;
                
            default:
                // 超时或无效命令，继续等待
                break;
        }
    }
}
```

### 步骤7：完整的Bootloader主程序

将所有功能整合到主程序中：

```c
// main.c (完整版本)
#include "stm32f4xx.h"
#include "flash.h"
#include "uart.h"
#include <string.h>

#define APP_START_ADDR      0x08008000
#define UPGRADE_START_ADDR  0x08080000
#define PARAM_START_ADDR    0x080F8000

// 升级标志定义
#define UPGRADE_FLAG_ADDR   PARAM_START_ADDR
#define UPGRADE_FLAG_VALUE  0x5AA5A55A

// LED控制（假设使用PD12）
#define LED_INIT()      do { \
                            RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN; \
                            GPIOD->MODER |= GPIO_MODER_MODER12_0; \
                        } while(0)

#define LED_ON()        GPIOD->BSRR = GPIO_BSRR_BS_12
#define LED_OFF()       GPIOD->BSRR = GPIO_BSRR_BR_12
#define LED_TOGGLE()    GPIOD->ODR ^= GPIO_ODR_ODR_12

// 按键控制（假设使用PA0）
#define KEY_INIT()      do { \
                            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN; \
                            GPIOA->MODER &= ~GPIO_MODER_MODER0; \
                            GPIOA->PUPDR |= GPIO_PUPDR_PUPDR0_1; \
                        } while(0)

#define KEY_PRESSED()   (GPIOA->IDR & GPIO_IDR_IDR_0)

// 延时函数（简单实现）
void Delay_Ms(uint32_t ms) {
    for (volatile uint32_t i = 0; i < ms * 4000; i++);
}

// 检查升级标志
uint8_t CheckUpgradeFlag(void) {
    uint32_t flag = *(__IO uint32_t*)UPGRADE_FLAG_ADDR;
    return (flag == UPGRADE_FLAG_VALUE);
}

// 清除升级标志
void ClearUpgradeFlag(void) {
    uint8_t sector = Flash_GetSector(UPGRADE_FLAG_ADDR);
    
    Flash_Unlock();
    Flash_EraseSector(sector);
    Flash_Lock();
}

// 设置升级标志
void SetUpgradeFlag(void) {
    uint8_t sector = Flash_GetSector(UPGRADE_FLAG_ADDR);
    
    Flash_Unlock();
    Flash_EraseSector(sector);
    Flash_WriteWord(UPGRADE_FLAG_ADDR, UPGRADE_FLAG_VALUE);
    Flash_Lock();
}

// 复制固件从升级区到应用区
uint8_t CopyFirmware(void) {
    uint32_t src_addr = UPGRADE_START_ADDR;
    uint32_t dst_addr = APP_START_ADDR;
    uint32_t size = APP_SIZE;
    uint8_t buffer[256];
    
    UART_SendString("Copying firmware...\r\n");
    
    // 擦除应用区
    Flash_Unlock();
    for (uint8_t sector = 2; sector <= 7; sector++) {
        LED_TOGGLE();
        if (Flash_EraseSector(sector) != 0) {
            UART_SendString("Erase app area failed!\r\n");
            Flash_Lock();
            return 1;
        }
    }
    
    // 复制数据
    for (uint32_t i = 0; i < size; i += sizeof(buffer)) {
        LED_TOGGLE();
        
        // 读取升级区数据
        memcpy(buffer, (uint8_t*)src_addr, sizeof(buffer));
        
        // 写入应用区
        if (Flash_WriteBuffer(dst_addr, buffer, sizeof(buffer)) != 0) {
            UART_SendString("Write app area failed!\r\n");
            Flash_Lock();
            return 2;
        }
        
        src_addr += sizeof(buffer);
        dst_addr += sizeof(buffer);
    }
    
    Flash_Lock();
    
    UART_SendString("Firmware copy complete!\r\n");
    return 0;
}

// 跳转到应用程序
void JumpToApplication(uint32_t app_addr) {
    if (((*(__IO uint32_t*)app_addr) & 0x2FFE0000) == 0x20000000) {
        typedef void (*pFunction)(void);
        
        uint32_t app_sp = *(__IO uint32_t*)app_addr;
        uint32_t app_entry = *(__IO uint32_t*)(app_addr + 4);
        pFunction app_reset_handler = (pFunction)app_entry;
        
        UART_SendString("Jumping to application...\r\n\r\n");
        Delay_Ms(100);  // 等待串口发送完成
        
        __disable_irq();
        
        SysTick->CTRL = 0;
        SysTick->LOAD = 0;
        SysTick->VAL = 0;
        
        SCB->VTOR = app_addr;
        __set_MSP(app_sp);
        
        app_reset_handler();
    }
}

int main(void) {
    // 系统初始化
    SystemInit();
    HAL_Init();
    
    // 初始化外设
    LED_INIT();
    KEY_INIT();
    UART_Init();
    
    // LED闪烁3次，表示Bootloader启动
    for (int i = 0; i < 3; i++) {
        LED_ON();
        Delay_Ms(100);
        LED_OFF();
        Delay_Ms(100);
    }
    
    // 发送启动信息
    UART_SendString("\r\n");
    UART_SendString("========================================\r\n");
    UART_SendString("  Simple Bootloader v1.0\r\n");
    UART_SendString("  Build: " __DATE__ " " __TIME__ "\r\n");
    UART_SendString("========================================\r\n");
    
    // 检查是否需要升级
    uint8_t need_upgrade = 0;
    
    // 方式1：检查按键
    if (KEY_PRESSED()) {
        UART_SendString("Key pressed, entering upgrade mode...\r\n");
        need_upgrade = 1;
    }
    
    // 方式2：检查升级标志
    if (CheckUpgradeFlag()) {
        UART_SendString("Upgrade flag detected...\r\n");
        need_upgrade = 1;
        ClearUpgradeFlag();
    }
    
    // 进入升级模式
    if (need_upgrade) {
        LED_ON();  // LED常亮表示升级模式
        
        UART_SendString("\r\n");
        UART_SendString("Upgrade Mode\r\n");
        UART_SendString("Commands:\r\n");
        UART_SendString("  1 - Download firmware\r\n");
        UART_SendString("  2 - Jump to application\r\n");
        UART_SendString("  3 - System reset\r\n");
        UART_SendString("\r\n");
        
        while (1) {
            uint8_t cmd = UART_ReceiveByte(100);
            
            switch (cmd) {
                case '1':
                    UART_SendString("\r\nStarting firmware download...\r\n");
                    FirmwareDownload();
                    
                    // 下载完成后复制固件
                    if (CopyFirmware() == 0) {
                        UART_SendString("Upgrade successful!\r\n");
                        Delay_Ms(1000);
                        NVIC_SystemReset();
                    } else {
                        UART_SendString("Upgrade failed!\r\n");
                    }
                    break;
                    
                case '2':
                    JumpToApplication(APP_START_ADDR);
                    // 如果跳转失败
                    UART_SendString("Jump failed! Invalid application.\r\n");
                    break;
                    
                case '3':
                    UART_SendString("System resetting...\r\n");
                    Delay_Ms(100);
                    NVIC_SystemReset();
                    break;
                    
                default:
                    // LED闪烁表示等待命令
                    LED_TOGGLE();
                    break;
            }
        }
    }
    
    // 正常启动模式
    UART_SendString("Normal boot mode\r\n");
    UART_SendString("Checking application...\r\n");
    
    // 检查应用程序是否有效
    uint32_t app_sp = *(__IO uint32_t*)APP_START_ADDR;
    if ((app_sp & 0x2FFE0000) == 0x20000000) {
        UART_SendString("Application valid\r\n");
        JumpToApplication(APP_START_ADDR);
    } else {
        UART_SendString("Application invalid!\r\n");
        UART_SendString("Please download firmware first.\r\n");
        
        // 应用程序无效，LED快速闪烁
        while (1) {
            LED_TOGGLE();
            Delay_Ms(200);
        }
    }
    
    // 永远不会执行到这里
    while (1);
}
```

### 步骤8：配置应用程序

应用程序需要做以下修改：

**1. 修改链接脚本**（已在步骤2完成）

**2. 修改启动代码**

在应用程序的`system_stm32f4xx.c`中，添加中断向量表重定位：

```c
// system_stm32f4xx.c
void SystemInit(void) {
    // ... 其他初始化代码 ...
    
    // 重新设置中断向量表偏移
    SCB->VTOR = 0x08008000;  // 应用程序起始地址
    
    // ... 其他初始化代码 ...
}
```

**3. 添加升级请求功能**（可选）

在应用程序中添加请求升级的功能：

```c
// app_main.c
#define PARAM_START_ADDR    0x080F8000
#define UPGRADE_FLAG_ADDR   PARAM_START_ADDR
#define UPGRADE_FLAG_VALUE  0x5AA5A55A

void RequestUpgrade(void) {
    // 设置升级标志
    HAL_FLASH_Unlock();
    
    // 擦除参数区
    FLASH_EraseInitTypeDef erase_init;
    uint32_t sector_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_SECTORS;
    erase_init.Sector = FLASH_SECTOR_11;
    erase_init.NbSectors = 1;
    erase_init.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    
    HAL_FLASHEx_Erase(&erase_init, &sector_error);
    
    // 写入升级标志
    HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, UPGRADE_FLAG_ADDR, UPGRADE_FLAG_VALUE);
    
    HAL_FLASH_Lock();
    
    // 复位系统
    NVIC_SystemReset();
}
```

## 实践示例

### 示例1：编译和下载Bootloader

**步骤**：

1. 打开Bootloader工程
2. 确认链接脚本配置正确（起始地址0x08000000）
3. 编译工程
4. 使用ST-Link下载到开发板
5. 打开串口助手（115200, 8N1）
6. 复位开发板，观察串口输出

**预期输出**：
```
========================================
  Simple Bootloader v1.0
  Build: Jan 15 2024 10:30:00
========================================
Normal boot mode
Checking application...
Application invalid!
Please download firmware first.
```

### 示例2：编译和下载应用程序

**步骤**：

1. 创建一个简单的应用程序（例如LED闪烁）
2. 修改链接脚本（起始地址0x08008000）
3. 在`SystemInit()`中添加`SCB->VTOR = 0x08008000;`
4. 编译工程，生成bin文件
5. 按住按键，复位开发板进入升级模式
6. 使用上位机发送固件

**简单的应用程序示例**：

```c
// app_main.c
#include "stm32f4xx.h"

void SystemClock_Config(void);

int main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 初始化LED
    __HAL_RCC_GPIOD_CLK_ENABLE();
    
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_12;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);
    
    // LED闪烁
    while (1) {
        HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_12);
        HAL_Delay(500);
    }
}
```

### 示例3：使用Python编写上位机

创建一个简单的Python上位机用于发送固件：


```python
# firmware_uploader.py
import serial
import time
import struct

# 协议定义
CMD_START = 0xA5
CMD_DATA = 0xA6
CMD_END = 0xA7
CMD_ERASE = 0xA8
ACK_OK = 0x79
ACK_ERROR = 0x1F

class FirmwareUploader:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)
        
    def send_command(self, cmd):
        """发送命令"""
        self.ser.write(bytes([cmd]))
        
    def wait_ack(self, timeout=5):
        """等待应答"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                ack = self.ser.read(1)[0]
                return ack == ACK_OK
        return False
        
    def calculate_checksum(self, data):
        """计算校验和"""
        return sum(data) & 0xFF
        
    def upload_firmware(self, filename):
        """上传固件"""
        # 读取固件文件
        with open(filename, 'rb') as f:
            firmware = f.read()
            
        print(f"Firmware size: {len(firmware)} bytes")
        
        # 发送开始命令
        print("Sending START command...")
        self.send_command(CMD_START)
        if not self.wait_ack():
            print("START command failed!")
            return False
        print("START command OK")
        
        # 发送擦除命令
        print("Sending ERASE command...")
        self.send_command(CMD_ERASE)
        if not self.wait_ack(timeout=30):  # 擦除需要更长时间
            print("ERASE command failed!")
            return False
        print("ERASE command OK")
        
        # 分包发送数据
        packet_size = 1024
        total_packets = (len(firmware) + packet_size - 1) // packet_size
        
        for seq in range(total_packets):
            offset = seq * packet_size
            data = firmware[offset:offset + packet_size]
            
            # 如果最后一包不足1024字节，填充0xFF
            if len(data) < packet_size:
                data += b'\xFF' * (packet_size - len(data))
            
            # 发送数据包
            print(f"Sending packet {seq + 1}/{total_packets}...", end='')
            
            # 命令字
            self.ser.write(bytes([CMD_DATA]))
            
            # 序号（2字节，小端）
            self.ser.write(struct.pack('<H', seq))
            
            # 长度（2字节，小端）
            self.ser.write(struct.pack('<H', len(data)))
            
            # 数据
            self.ser.write(data)
            
            # 校验和
            checksum = self.calculate_checksum(data)
            self.ser.write(bytes([checksum]))
            
            # 等待应答
            if not self.wait_ack():
                print(" FAILED!")
                return False
            print(" OK")
            
            time.sleep(0.01)  # 短暂延时
        
        # 发送结束命令
        print("Sending END command...")
        self.send_command(CMD_END)
        if not self.wait_ack():
            print("END command failed!")
            return False
        print("END command OK")
        
        print("Firmware upload complete!")
        return True
        
    def close(self):
        """关闭串口"""
        self.ser.close()

# 使用示例
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python firmware_uploader.py <COM_PORT> <FIRMWARE_FILE>")
        print("Example: python firmware_uploader.py COM3 application.bin")
        sys.exit(1)
    
    port = sys.argv[1]
    firmware_file = sys.argv[2]
    
    print(f"Opening port {port}...")
    uploader = FirmwareUploader(port)
    
    print(f"Uploading firmware from {firmware_file}...")
    success = uploader.upload_firmware(firmware_file)
    
    uploader.close()
    
    if success:
        print("\nUpload successful!")
        sys.exit(0)
    else:
        print("\nUpload failed!")
        sys.exit(1)
```

**使用方法**：

```bash
# 安装依赖
pip install pyserial

# 上传固件
python firmware_uploader.py COM3 application.bin
```

## 深入理解

### Flash编程原理

STM32F4的Flash编程需要遵循以下步骤：

1. **解锁Flash**：写入特定的密钥序列
2. **擦除扇区**：Flash必须先擦除才能编程
3. **编程数据**：按字（32位）写入数据
4. **等待完成**：检查BSY标志位
5. **锁定Flash**：保护Flash不被意外修改

**关键寄存器**：

- `FLASH->KEYR`：密钥寄存器，用于解锁
- `FLASH->SR`：状态寄存器，包含BSY、错误标志等
- `FLASH->CR`：控制寄存器，配置擦除/编程操作

**扇区大小**（STM32F407）：

| 扇区 | 地址范围 | 大小 |
|-----|---------|------|
| 0-3 | 0x08000000-0x0800FFFF | 16KB × 4 |
| 4 | 0x08010000-0x0801FFFF | 64KB |
| 5-11 | 0x08020000-0x080FFFFF | 128KB × 7 |

### 中断向量表重定位

ARM Cortex-M系列使用VTOR（Vector Table Offset Register）寄存器来设置中断向量表的位置。

**为什么需要重定位**：

- Bootloader和应用程序都有自己的中断向量表
- 跳转到应用程序后，需要使用应用程序的中断向量表
- VTOR寄存器允许动态改变向量表位置

**重定位步骤**：

```c
// 1. 在Bootloader中跳转前设置
SCB->VTOR = 0x08008000;  // 应用程序起始地址

// 2. 在应用程序的SystemInit()中再次设置（确保正确）
SCB->VTOR = 0x08008000;
```

**注意事项**：

- VTOR的值必须是512字节对齐（Cortex-M4）
- 应用程序的链接脚本必须匹配VTOR的值
- 跳转前必须关闭所有中断

### 固件校验机制

为了确保固件的完整性，通常使用以下校验方法：

**1. 简单校验和**：

```c
uint8_t CalculateChecksum(uint8_t *data, uint32_t len) {
    uint8_t sum = 0;
    for (uint32_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum;
}
```

**2. CRC32校验**：

```c
// 使用STM32硬件CRC
uint32_t CalculateCRC32(uint32_t *data, uint32_t len) {
    // 使能CRC时钟
    RCC->AHB1ENR |= RCC_AHB1ENR_CRCEN;
    
    // 复位CRC
    CRC->CR = CRC_CR_RESET;
    
    // 计算CRC
    for (uint32_t i = 0; i < len; i++) {
        CRC->DR = data[i];
    }
    
    return CRC->DR;
}

// 验证固件
bool VerifyFirmware(uint32_t addr, uint32_t size) {
    uint32_t calculated_crc = CalculateCRC32((uint32_t*)addr, size / 4);
    uint32_t stored_crc = *(__IO uint32_t*)(addr + size);
    
    return (calculated_crc == stored_crc);
}
```

**3. 数字签名**（高级）：

使用RSA或ECDSA算法验证固件的合法性，防止固件被篡改。

### 双区升级策略

为了提高升级的可靠性，可以采用双区升级策略：

```
Flash布局：
├── Bootloader (32KB)
├── 应用区A (480KB)  ← 当前运行
├── 应用区B (480KB)  ← 升级缓存
└── 参数区 (32KB)
```

**升级流程**：

1. 应用程序运行在区域A
2. 新固件下载到区域B
3. 校验区域B的固件
4. 如果校验通过，设置标志，下次启动从区域B运行
5. 如果区域B启动失败，自动回滚到区域A

**优点**：

- 升级失败不影响当前固件
- 支持快速回滚
- 提高系统可靠性

**缺点**：

- 需要更多Flash空间
- 实现复杂度增加

### 安全性考虑

**1. 读保护**：

启用Flash读保护，防止固件被读取：

```c
// 设置读保护级别1
FLASH_OBProgramInitTypeDef ob_config;
ob_config.OptionType = OPTIONBYTE_RDP;
ob_config.RDPLevel = OB_RDP_LEVEL_1;

HAL_FLASH_Unlock();
HAL_FLASH_OB_Unlock();
HAL_FLASHEx_OBProgram(&ob_config);
HAL_FLASH_OB_Launch();
HAL_FLASH_OB_Lock();
HAL_FLASH_Lock();
```

**警告**：读保护级别2不可逆，会永久锁定芯片！

**2. 写保护**：

保护Bootloader区域不被意外擦除：

```c
// 设置扇区0-1写保护
FLASH_OBProgramInitTypeDef ob_config;
ob_config.OptionType = OPTIONBYTE_WRP;
ob_config.WRPSector = OB_WRP_SECTOR_0 | OB_WRP_SECTOR_1;
ob_config.WRPState = OB_WRPSTATE_ENABLE;

HAL_FLASH_Unlock();
HAL_FLASH_OB_Unlock();
HAL_FLASHEx_OBProgram(&ob_config);
HAL_FLASH_OB_Launch();
HAL_FLASH_OB_Lock();
HAL_FLASH_Lock();
```

**3. 固件加密**：

对固件进行AES加密，Bootloader解密后再写入Flash：

```c
// 伪代码
void DecryptAndWrite(uint8_t *encrypted_data, uint32_t addr, uint32_t len) {
    uint8_t decrypted_data[256];
    
    // 使用AES解密
    AES_Decrypt(encrypted_data, decrypted_data, len, aes_key);
    
    // 写入Flash
    Flash_WriteBuffer(addr, decrypted_data, len);
}
```

## 常见问题

### Q1: 为什么跳转到应用程序后系统复位？

**A**: 可能的原因：

1. **栈指针无效**：检查应用程序的栈指针是否指向有效的RAM区域
2. **中断向量表未重定位**：确保在跳转前设置了`SCB->VTOR`
3. **应用程序链接脚本错误**：检查起始地址是否正确
4. **外设未关闭**：跳转前关闭Bootloader使用的外设

**调试方法**：

```c
// 在跳转前打印调试信息
uint32_t app_sp = *(__IO uint32_t*)APP_START_ADDR;
uint32_t app_entry = *(__IO uint32_t*)(APP_START_ADDR + 4);

printf("App SP: 0x%08X\r\n", app_sp);
printf("App Entry: 0x%08X\r\n", app_entry);

// 检查栈指针是否有效
if ((app_sp & 0x2FFE0000) != 0x20000000) {
    printf("Invalid stack pointer!\r\n");
}
```

### Q2: Flash编程失败怎么办？

**A**: 检查以下几点：

1. **Flash是否解锁**：确保调用了`Flash_Unlock()`
2. **地址是否对齐**：Flash编程地址必须4字节对齐
3. **扇区是否擦除**：Flash必须先擦除才能编程
4. **电压范围**：确保VDD在正常范围内（2.7V-3.6V）
5. **写保护**：检查是否启用了写保护

**错误处理**：

```c
uint8_t status = Flash_WriteWord(addr, data);
if (status != 0) {
    // 检查错误类型
    if (FLASH->SR & FLASH_SR_PGSERR) {
        printf("Programming sequence error\r\n");
    }
    if (FLASH->SR & FLASH_SR_PGPERR) {
        printf("Programming parallelism error\r\n");
    }
    if (FLASH->SR & FLASH_SR_PGAERR) {
        printf("Programming alignment error\r\n");
    }
    if (FLASH->SR & FLASH_SR_WRPERR) {
        printf("Write protection error\r\n");
    }
}
```

### Q3: 串口通信不稳定怎么办？

**A**: 优化措施：

1. **增加超时时间**：根据实际情况调整超时参数
2. **添加重传机制**：数据包传输失败时自动重传
3. **使用流控制**：硬件流控（RTS/CTS）或软件流控（XON/XOFF）
4. **降低波特率**：如果线路质量差，降低到57600或更低
5. **添加校验**：使用CRC16代替简单校验和

**改进的协议**：

```c
// 添加重传机制
#define MAX_RETRY 3

for (int retry = 0; retry < MAX_RETRY; retry++) {
    // 发送数据包
    SendPacket(&packet);
    
    // 等待应答
    if (WaitAck(2000)) {
        break;  // 成功
    }
    
    if (retry == MAX_RETRY - 1) {
        printf("Max retry reached, giving up\r\n");
        return ERROR;
    }
    
    printf("Retry %d/%d\r\n", retry + 1, MAX_RETRY);
}
```

### Q4: 如何实现断点续传？

**A**: 实现方法：

1. **记录进度**：在参数区保存当前传输的序号
2. **恢复传输**：重新连接后从上次中断处继续
3. **校验已传输数据**：确保已传输的数据完整

```c
// 保存进度
void SaveProgress(uint16_t seq, uint32_t addr) {
    Flash_Unlock();
    Flash_WriteWord(PROGRESS_ADDR, seq);
    Flash_WriteWord(PROGRESS_ADDR + 4, addr);
    Flash_Lock();
}

// 恢复进度
void RestoreProgress(uint16_t *seq, uint32_t *addr) {
    *seq = *(__IO uint32_t*)PROGRESS_ADDR;
    *addr = *(__IO uint32_t*)(PROGRESS_ADDR + 4);
}

// 在固件下载函数中使用
void FirmwareDownload(void) {
    uint16_t seq;
    uint32_t addr;
    
    // 尝试恢复进度
    RestoreProgress(&seq, &addr);
    
    if (seq > 0) {
        printf("Resume from packet %d\r\n", seq);
    }
    
    // ... 继续传输 ...
}
```

### Q5: 如何优化启动时间？

**A**: 优化策略：

1. **最小化初始化**：只初始化必要的外设
2. **快速判断**：尽快决定是否跳转到应用程序
3. **并行处理**：在等待按键时进行其他初始化
4. **优化编译选项**：使用-O2或-O3优化级别
5. **减少延时**：缩短LED闪烁等指示的时间

```c
// 优化后的主程序
int main(void) {
    SystemInit();
    
    // 快速检查按键（不初始化其他外设）
    KEY_INIT();
    if (!KEY_PRESSED()) {
        // 按键未按下，直接跳转
        JumpToApplication(APP_START_ADDR);
    }
    
    // 按键按下，才初始化其他外设
    LED_INIT();
    UART_Init();
    
    // 进入升级模式
    UpgradeMode();
}
```

## 总结

通过本教程，我们从零开始实现了一个功能完整的简单Bootloader，涵盖了以下核心内容：

- **Flash内存布局规划**：合理分配Bootloader、应用程序和升级区域
- **链接脚本配置**：为Bootloader和应用程序配置不同的起始地址
- **Flash操作**：实现Flash解锁、擦除、编程等基本操作
- **串口通信**：实现串口初始化和数据收发
- **应用程序跳转**：正确设置栈指针和中断向量表，跳转到应用程序
- **固件下载协议**：设计简单的通信协议，实现固件接收和烧写
- **完整的主程序**：整合所有功能，实现完整的Bootloader逻辑

这个Bootloader虽然简单，但包含了实际项目中的核心功能。在实际应用中，你可以根据需要添加更多功能，如：

- 更安全的固件校验（CRC32、数字签名）
- 双区升级和回滚机制
- 更完善的错误处理和恢复
- 支持多种通信接口（USB、CAN、以太网）
- 固件加密和读保护

## 延伸阅读

推荐进一步学习的内容：

- [固件分区与内存布局设计](04-firmware-partition.html) - 深入学习内存规划
- [Bootloader与应用程序通信机制](05-bootloader-app-communication.html) - 参数传递和数据交换
- [IAP在线升级功能实现](../intermediate/01-iap-implementation.html) - 完整的IAP系统
- [安全启动(Secure Boot)技术详解](../intermediate/02-secure-boot.html) - 提升系统安全性

**参考资料**：

- STM32F4xx参考手册 - Flash编程章节
- ARM Cortex-M4编程手册 - 中断向量表和VTOR
- AN2606: STM32微控制器系统存储器Bootloader - ST官方应用笔记
- AN3155: USART协议用于Bootloader - ST官方应用笔记

## 练习题

1. **基础练习**：修改Bootloader，使用不同的LED闪烁模式表示不同的状态（启动、升级、错误等）。

2. **进阶练习**：实现固件的CRC32校验功能，在下载完成后验证固件完整性。

3. **挑战练习**：实现双区升级功能，支持固件回滚。

4. **综合练习**：编写一个图形化的上位机程序（使用Python + PyQt5），实现固件选择、进度显示、日志输出等功能。

5. **思考题**：如果Bootloader本身需要升级，应该如何设计？提示：考虑多级Bootloader方案。

---

**下一步**：建议学习 [固件分区与内存布局设计](04-firmware-partition.html)，深入理解Flash分区策略和链接脚本配置。
