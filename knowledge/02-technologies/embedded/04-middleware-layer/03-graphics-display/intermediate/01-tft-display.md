---
# 基础信息
title: "TFT显示屏驱动完全指南"
description: "全面深入讲解TFT LCD显示原理、显示控制器（ILI9341、ST7789）驱动开发、SPI/并行接口实现、图形基元绘制和帧缓冲管理，掌握嵌入式系统中TFT显示屏的核心技术"
slug: "tft-display-driver-guide"

# 分类信息
domain: "04-middleware-layer"
module: "03-graphics-display"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - TFT显示屏
  - ILI9341
  - ST7789
  - SPI接口
  - 并行接口
  - 图形绘制
  - 帧缓冲
  - GUI开发
prerequisites:
  - "../beginner/01-display-basics.md"
  - "../../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-spi-driver.md"
  - "../../../01-hardware-layer/06-communication-interface-hardware/beginner/02-spi-hardware.md"
related_contents:
  - "02-graphics-optimization.md"
  - "01-gui-design-patterns.md"
  <!-- 以下链接指向的文件不存在，待补充后取消注释
  - "../advanced/01-gpu-acceleration.md"
  -->

# 学习信息
estimated_time: 120
difficulty_score: 6

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-04-06"
updated_at: "2026-04-06"
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
  - TFT LCD驱动
  - ILI9341驱动
  - ST7789驱动
  - SPI显示屏
  - 图形绘制
  - 帧缓冲管理
  - GUI编程
  - 显示优化
cover_image: ""
---

# TFT显示屏驱动完全指南

## 概述

TFT（Thin Film Transistor，薄膜晶体管）LCD是嵌入式系统中最常用的彩色显示方案。相比传统的段码LCD和字符LCD，TFT显示屏可以显示丰富的图形和图像，广泛应用于智能设备、工业控制、医疗仪器等领域。本教程将全面深入地讲解TFT显示屏的工作原理、驱动开发、图形绘制和性能优化。

### 什么是TFT显示屏

TFT LCD是一种有源矩阵液晶显示器，每个像素都由独立的薄膜晶体管控制。相比被动矩阵显示器，TFT具有更快的响应速度、更高的对比度和更好的色彩表现。

### TFT显示屏的优势

```
TFT vs 其他显示技术：

┌──────────────┬─────────┬─────────┬─────────┬─────────┐
│   特性       │  TFT    │  OLED   │ E-Ink   │ 段码LCD │
├──────────────┼─────────┼─────────┼─────────┼─────────┤
│ 色彩         │  丰富   │  丰富   │  单色   │  单色   │
│ 对比度       │  中     │  高     │  高     │  低     │
│ 响应速度     │  快     │  很快   │  慢     │  中     │
│ 功耗         │  中     │  低     │  极低   │  极低   │
│ 可视角度     │  中     │  广     │  广     │  窄     │
│ 阳光下可读   │  中     │  差     │  优秀   │  好     │
│ 成本         │  低     │  高     │  中     │  极低   │
│ 寿命         │  长     │  中     │  长     │  很长   │
└──────────────┴─────────┴─────────┴─────────┴─────────┘

应用建议：
- 通用GUI：TFT
- 高端产品：OLED
- 低功耗阅读：E-Ink
- 简单显示：段码LCD
```

### 本文内容概览

本教程将涵盖以下内容：

1. **TFT LCD原理**：液晶显示原理、色彩模型、分辨率
2. **显示控制器**：ILI9341、ST7789、ST7735等常用芯片
3. **硬件接口**：SPI接口、8/16位并行接口、LTDC接口
4. **驱动开发**：初始化、命令发送、数据传输
5. **图形基元**：点、线、矩形、圆、文本绘制
6. **帧缓冲管理**：单缓冲、双缓冲、局部刷新
7. **性能优化**：DMA传输、批量操作、硬件加速
8. **实战项目**：仪表盘、图表显示、图片查看器

## 第一部分：TFT LCD基础

### 1.1 液晶显示原理

**TFT LCD结构**：

```
TFT LCD层次结构（从背面到正面）：

┌─────────────────────────────────┐
│      背光模组 (Backlight)        │  LED背光
├─────────────────────────────────┤
│      下偏光片 (Polarizer)        │  垂直偏振
├─────────────────────────────────┤
│      玻璃基板                    │
├─────────────────────────────────┤
│      TFT阵列                     │  薄膜晶体管
├─────────────────────────────────┤
│      液晶层 (Liquid Crystal)     │  控制光线
├─────────────────────────────────┤
│      彩色滤光片 (Color Filter)   │  RGB子像素
├─────────────────────────────────┤
│      玻璃基板                    │
├─────────────────────────────────┤
│      上偏光片 (Polarizer)        │  水平偏振
└─────────────────────────────────┘

工作原理：
1. 背光发出白光
2. 下偏光片产生垂直偏振光
3. TFT控制液晶分子旋转角度
4. 液晶改变光的偏振方向
5. 彩色滤光片产生RGB颜色
6. 上偏光片控制光线通过量
```

### 1.2 色彩模型

**RGB565格式**：

```c
/**
 * @brief  RGB565色彩格式
 * @note   16位色彩，5位红色，6位绿色，5位蓝色
 */
typedef uint16_t color_t;

/* 常用颜色定义 */
#define COLOR_BLACK     0x0000  // 黑色
#define COLOR_WHITE     0xFFFF  // 白色
#define COLOR_RED       0xF800  // 红色
#define COLOR_GREEN     0x07E0  // 绿色
#define COLOR_BLUE      0x001F  // 蓝色
#define COLOR_YELLOW    0xFFE0  // 黄色
#define COLOR_CYAN      0x07FF  // 青色
#define COLOR_MAGENTA   0xF81F  // 洋红色
#define COLOR_GRAY      0x8410  // 灰色

/**
 * @brief  RGB888转RGB565
 */
color_t rgb888_to_rgb565(uint8_t r, uint8_t g, uint8_t b)
{
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

/**
 * @brief  RGB565转RGB888
 */
void rgb565_to_rgb888(color_t color, uint8_t *r, uint8_t *g, uint8_t *b)
{
    *r = (color >> 8) & 0xF8;
    *g = (color >> 3) & 0xFC;
    *b = (color << 3) & 0xF8;
}

/**
 * @brief  颜色混合（Alpha混合）
 */
color_t color_blend(color_t fg, color_t bg, uint8_t alpha)
{
    uint8_t r1, g1, b1, r2, g2, b2;
    
    // 分解前景色
    rgb565_to_rgb888(fg, &r1, &g1, &b1);
    
    // 分解背景色
    rgb565_to_rgb888(bg, &r2, &g2, &b2);
    
    // Alpha混合
    uint8_t r = (r1 * alpha + r2 * (255 - alpha)) / 255;
    uint8_t g = (g1 * alpha + g2 * (255 - alpha)) / 255;
    uint8_t b = (b1 * alpha + b2 * (255 - alpha)) / 255;
    
    return rgb888_to_rgb565(r, g, b);
}
```

### 1.3 分辨率和像素密度

```
常见TFT显示屏规格：

┌──────────┬─────────┬─────────┬─────────┬─────────┐
│  尺寸    │  分辨率 │  PPI    │  接口   │  控制器 │
├──────────┼─────────┼─────────┼─────────┼─────────┤
│  1.8"    │ 128×160 │  116    │  SPI    │ ST7735  │
│  2.4"    │ 240×320 │  167    │  SPI    │ ILI9341 │
│  2.8"    │ 240×320 │  143    │  SPI/8位│ ILI9341 │
│  3.2"    │ 240×320 │  125    │  8/16位 │ ILI9341 │
│  3.5"    │ 320×480 │  165    │  16位   │ ILI9488 │
│  4.3"    │ 480×272 │  128    │  RGB    │ 无      │
│  5.0"    │ 800×480 │  186    │  RGB    │ 无      │
│  7.0"    │ 800×480 │  133    │  RGB/LVDS│ 无     │
└──────────┴─────────┴─────────┴─────────┴─────────┘

PPI计算：
PPI = √(width² + height²) / diagonal_inches

示例（2.4寸 240×320）：
PPI = √(240² + 320²) / 2.4 = 400 / 2.4 = 167
```

## 第二部分：ILI9341驱动开发

### 2.1 ILI9341控制器简介

ILI9341是最常用的TFT LCD控制器之一，支持240×320分辨率，262K色彩。

**引脚定义**：

```
ILI9341 SPI接口引脚：

MCU          ILI9341
────────────────────
VCC    ───→  VCC (3.3V)
GND    ───→  GND
SCK    ───→  SCK (SPI时钟)
MOSI   ───→  SDI (SPI数据输入)
MISO   ←───  SDO (SPI数据输出，可选)
CS     ───→  CS  (片选，低有效)
DC     ───→  DC  (数据/命令选择)
RST    ───→  RST (复位，低有效)
BL     ───→  LED (背光控制)

DC引脚说明：
- DC=0: 发送命令
- DC=1: 发送数据
```

### 2.2 SPI接口驱动实现

```c
/**
 * @file    ili9341_spi.c
 * @brief   ILI9341 SPI接口驱动
 */

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* 显示屏参数 */
#define LCD_WIDTH   240
#define LCD_HEIGHT  320

/* 引脚定义 */
#define LCD_CS_PIN      GPIO_PIN_4
#define LCD_CS_PORT     GPIOA
#define LCD_DC_PIN      GPIO_PIN_5
#define LCD_DC_PORT     GPIOA
#define LCD_RST_PIN     GPIO_PIN_6
#define LCD_RST_PORT    GPIOA
#define LCD_BL_PIN      GPIO_PIN_7
#define LCD_BL_PORT     GPIOA

/* 引脚控制宏 */
#define LCD_CS_LOW()    HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET)
#define LCD_CS_HIGH()   HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET)
#define LCD_DC_LOW()    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET)
#define LCD_DC_HIGH()   HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET)
#define LCD_RST_LOW()   HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_RESET)
#define LCD_RST_HIGH()  HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET)
#define LCD_BL_ON()     HAL_GPIO_WritePin(LCD_BL_PORT, LCD_BL_PIN, GPIO_PIN_SET)
#define LCD_BL_OFF()    HAL_GPIO_WritePin(LCD_BL_PORT, LCD_BL_PIN, GPIO_PIN_RESET)

/* ILI9341命令定义 */
#define ILI9341_NOP         0x00
#define ILI9341_SWRESET     0x01
#define ILI9341_RDDID       0x04
#define ILI9341_RDDST       0x09
#define ILI9341_SLPIN       0x10
#define ILI9341_SLPOUT      0x11
#define ILI9341_PTLON       0x12
#define ILI9341_NORON       0x13
#define ILI9341_INVOFF      0x20
#define ILI9341_INVON       0x21
#define ILI9341_GAMMASET    0x26
#define ILI9341_DISPOFF     0x28
#define ILI9341_DISPON      0x29
#define ILI9341_CASET       0x2A
#define ILI9341_PASET       0x2B
#define ILI9341_RAMWR       0x2C
#define ILI9341_RAMRD       0x2E
#define ILI9341_PTLAR       0x30
#define ILI9341_MADCTL      0x36
#define ILI9341_PIXFMT      0x3A
#define ILI9341_FRMCTR1     0xB1
#define ILI9341_FRMCTR2     0xB2
#define ILI9341_FRMCTR3     0xB3
#define ILI9341_INVCTR      0xB4
#define ILI9341_DFUNCTR     0xB6
#define ILI9341_PWCTR1      0xC0
#define ILI9341_PWCTR2      0xC1
#define ILI9341_PWCTR3      0xC2
#define ILI9341_PWCTR4      0xC3
#define ILI9341_PWCTR5      0xC4
#define ILI9341_VMCTR1      0xC5
#define ILI9341_VMCTR2      0xC7
#define ILI9341_GMCTRP1     0xE0
#define ILI9341_GMCTRN1     0xE1

/* 显示方向 */
typedef enum {
    LCD_ORIENTATION_PORTRAIT = 0,
    LCD_ORIENTATION_LANDSCAPE,
    LCD_ORIENTATION_PORTRAIT_INV,
    LCD_ORIENTATION_LANDSCAPE_INV
} lcd_orientation_t;

/* SPI句柄 */
extern SPI_HandleTypeDef hspi1;

/**
 * @brief  SPI发送字节
 */
static void spi_write_byte(uint8_t data)
{
    HAL_SPI_Transmit(&hspi1, &data, 1, 100);
}

/**
 * @brief  发送命令
 */
void lcd_write_command(uint8_t cmd)
{
    LCD_DC_LOW();   // 命令模式
    LCD_CS_LOW();
    spi_write_byte(cmd);
    LCD_CS_HIGH();
}

/**
 * @brief  发送数据
 */
void lcd_write_data(uint8_t data)
{
    LCD_DC_HIGH();  // 数据模式
    LCD_CS_LOW();
    spi_write_byte(data);
    LCD_CS_HIGH();
}

/**
 * @brief  发送16位数据
 */
void lcd_write_data16(uint16_t data)
{
    LCD_DC_HIGH();
    LCD_CS_LOW();
    spi_write_byte(data >> 8);
    spi_write_byte(data & 0xFF);
    LCD_CS_HIGH();
}

/**
 * @brief  批量发送数据
 */
void lcd_write_data_bulk(uint8_t *data, uint32_t len)
{
    LCD_DC_HIGH();
    LCD_CS_LOW();
    HAL_SPI_Transmit(&hspi1, data, len, 1000);
    LCD_CS_HIGH();
}

/**
 * @brief  硬件复位
 */
void lcd_reset(void)
{
    LCD_RST_HIGH();
    HAL_Delay(10);
    LCD_RST_LOW();
    HAL_Delay(10);
    LCD_RST_HIGH();
    HAL_Delay(120);
}

/**
 * @brief  初始化ILI9341
 */
void ili9341_init(void)
{
    // 硬件复位
    lcd_reset();
    
    // 软件复位
    lcd_write_command(ILI9341_SWRESET);
    HAL_Delay(150);
    
    // 退出睡眠模式
    lcd_write_command(ILI9341_SLPOUT);
    HAL_Delay(500);
    
    // 电源控制
    lcd_write_command(ILI9341_PWCTR1);
    lcd_write_data(0x23);
    
    lcd_write_command(ILI9341_PWCTR2);
    lcd_write_data(0x10);
    
    lcd_write_command(ILI9341_VMCTR1);
    lcd_write_data(0x3E);
    lcd_write_data(0x28);
    
    lcd_write_command(ILI9341_VMCTR2);
    lcd_write_data(0x86);
    
    // 内存访问控制
    lcd_write_command(ILI9341_MADCTL);
    lcd_write_data(0x48);  // MY=0, MX=1, MV=0, ML=0, BGR=1
    
    // 像素格式：16位/像素
    lcd_write_command(ILI9341_PIXFMT);
    lcd_write_data(0x55);
    
    // 帧率控制
    lcd_write_command(ILI9341_FRMCTR1);
    lcd_write_data(0x00);
    lcd_write_data(0x18);
    
    // 显示功能控制
    lcd_write_command(ILI9341_DFUNCTR);
    lcd_write_data(0x08);
    lcd_write_data(0x82);
    lcd_write_data(0x27);
    
    // Gamma设置
    lcd_write_command(ILI9341_GAMMASET);
    lcd_write_data(0x01);
    
    // 正Gamma校正
    lcd_write_command(ILI9341_GMCTRP1);
    lcd_write_data(0x0F);
    lcd_write_data(0x31);
    lcd_write_data(0x2B);
    lcd_write_data(0x0C);
    lcd_write_data(0x0E);
    lcd_write_data(0x08);
    lcd_write_data(0x4E);
    lcd_write_data(0xF1);
    lcd_write_data(0x37);
    lcd_write_data(0x07);
    lcd_write_data(0x10);
    lcd_write_data(0x03);
    lcd_write_data(0x0E);
    lcd_write_data(0x09);
    lcd_write_data(0x00);
    
    // 负Gamma校正
    lcd_write_command(ILI9341_GMCTRN1);
    lcd_write_data(0x00);
    lcd_write_data(0x0E);
    lcd_write_data(0x14);
    lcd_write_data(0x03);
    lcd_write_data(0x11);
    lcd_write_data(0x07);
    lcd_write_data(0x31);
    lcd_write_data(0xC1);
    lcd_write_data(0x48);
    lcd_write_data(0x08);
    lcd_write_data(0x0F);
    lcd_write_data(0x0C);
    lcd_write_data(0x31);
    lcd_write_data(0x36);
    lcd_write_data(0x0F);
    
    // 退出睡眠
    lcd_write_command(ILI9341_SLPOUT);
    HAL_Delay(120);
    
    // 开启显示
    lcd_write_command(ILI9341_DISPON);
    HAL_Delay(120);
    
    // 开启背光
    LCD_BL_ON();
}

/**
 * @brief  设置显示窗口
 */
void lcd_set_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    // 列地址设置
    lcd_write_command(ILI9341_CASET);
    lcd_write_data(x1 >> 8);
    lcd_write_data(x1 & 0xFF);
    lcd_write_data(x2 >> 8);
    lcd_write_data(x2 & 0xFF);
    
    // 行地址设置
    lcd_write_command(ILI9341_PASET);
    lcd_write_data(y1 >> 8);
    lcd_write_data(y1 & 0xFF);
    lcd_write_data(y2 >> 8);
    lcd_write_data(y2 & 0xFF);
    
    // 写入RAM
    lcd_write_command(ILI9341_RAMWR);
}

/**
 * @brief  设置显示方向
 */
void lcd_set_orientation(lcd_orientation_t orientation)
{
    uint8_t madctl = 0;
    
    switch (orientation) {
        case LCD_ORIENTATION_PORTRAIT:
            madctl = 0x48;  // MY=0, MX=1, MV=0, BGR=1
            break;
        case LCD_ORIENTATION_LANDSCAPE:
            madctl = 0x28;  // MY=0, MX=0, MV=1, BGR=1
            break;
        case LCD_ORIENTATION_PORTRAIT_INV:
            madctl = 0x88;  // MY=1, MX=0, MV=0, BGR=1
            break;
        case LCD_ORIENTATION_LANDSCAPE_INV:
            madctl = 0xE8;  // MY=1, MX=1, MV=1, BGR=1
            break;
    }
    
    lcd_write_command(ILI9341_MADCTL);
    lcd_write_data(madctl);
}
```

### 2.3 DMA加速传输

```c
/**
 * @brief  DMA传输配置
 */
DMA_HandleTypeDef hdma_spi1_tx;

void lcd_dma_init(void)
{
    /* DMA controller clock enable */
    __HAL_RCC_DMA2_CLK_ENABLE();
    
    /* DMA配置 */
    hdma_spi1_tx.Instance = DMA2_Stream3;
    hdma_spi1_tx.Init.Channel = DMA_CHANNEL_3;
    hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_spi1_tx.Init.Mode = DMA_NORMAL;
    hdma_spi1_tx.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_spi1_tx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    
    HAL_DMA_Init(&hdma_spi1_tx);
    
    __HAL_LINKDMA(&hspi1, hdmaTx, hdma_spi1_tx);
    
    /* DMA中断配置 */
    HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);
}

/**
 * @brief  DMA传输数据
 */
void lcd_write_data_dma(uint8_t *data, uint32_t len)
{
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    HAL_SPI_Transmit_DMA(&hspi1, data, len);
    
    // 等待传输完成
    while (HAL_SPI_GetState(&hspi1) != HAL_SPI_STATE_READY) {
        // 可以在这里处理其他任务
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  DMA传输完成回调
 */
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        LCD_CS_HIGH();
        // 通知应用层传输完成
    }
}
```

## 第三部分：图形基元绘制

### 3.1 基本绘图函数

```c
/**
 * @brief  画点
 */
void lcd_draw_pixel(uint16_t x, uint16_t y, color_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) {
        return;
    }
    
    lcd_set_window(x, y, x, y);
    lcd_write_data16(color);
}

/**
 * @brief  画线（Bresenham算法）
 */
void lcd_draw_line(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, color_t color)
{
    int16_t dx = abs(x2 - x1);
    int16_t dy = abs(y2 - y1);
    int16_t sx = (x1 < x2) ? 1 : -1;
    int16_t sy = (y1 < y2) ? 1 : -1;
    int16_t err = dx - dy;
    
    while (1) {
        lcd_draw_pixel(x1, y1, color);
        
        if (x1 == x2 && y1 == y2) {
            break;
        }
        
        int16_t e2 = 2 * err;
        
        if (e2 > -dy) {
            err -= dy;
            x1 += sx;
        }
        
        if (e2 < dx) {
            err += dx;
            y1 += sy;
        }
    }
}

/**
 * @brief  画矩形
 */
void lcd_draw_rectangle(uint16_t x, uint16_t y, uint16_t width, uint16_t height, color_t color)
{
    lcd_draw_line(x, y, x + width - 1, y, color);                      // 上边
    lcd_draw_line(x, y + height - 1, x + width - 1, y + height - 1, color);  // 下边
    lcd_draw_line(x, y, x, y + height - 1, color);                     // 左边
    lcd_draw_line(x + width - 1, y, x + width - 1, y + height - 1, color);   // 右边
}

/**
 * @brief  填充矩形
 */
void lcd_fill_rectangle(uint16_t x, uint16_t y, uint16_t width, uint16_t height, color_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) {
        return;
    }
    
    // 边界检查
    if (x + width > LCD_WIDTH) {
        width = LCD_WIDTH - x;
    }
    if (y + height > LCD_HEIGHT) {
        height = LCD_HEIGHT - y;
    }
    
    // 设置窗口
    lcd_set_window(x, y, x + width - 1, y + height - 1);
    
    // 填充颜色
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    uint32_t total_pixels = width * height;
    for (uint32_t i = 0; i < total_pixels; i++) {
        spi_write_byte(color >> 8);
        spi_write_byte(color & 0xFF);
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  画圆（中点圆算法）
 */
void lcd_draw_circle(uint16_t x0, uint16_t y0, uint16_t radius, color_t color)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 0;
    
    while (x >= y) {
        lcd_draw_pixel(x0 + x, y0 + y, color);
        lcd_draw_pixel(x0 + y, y0 + x, color);
        lcd_draw_pixel(x0 - y, y0 + x, color);
        lcd_draw_pixel(x0 - x, y0 + y, color);
        lcd_draw_pixel(x0 - x, y0 - y, color);
        lcd_draw_pixel(x0 - y, y0 - x, color);
        lcd_draw_pixel(x0 + y, y0 - x, color);
        lcd_draw_pixel(x0 + x, y0 - y, color);
        
        if (err <= 0) {
            y += 1;
            err += 2 * y + 1;
        }
        
        if (err > 0) {
            x -= 1;
            err -= 2 * x + 1;
        }
    }
}

/**
 * @brief  填充圆
 */
void lcd_fill_circle(uint16_t x0, uint16_t y0, uint16_t radius, color_t color)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 0;
    
    while (x >= y) {
        lcd_draw_line(x0 - x, y0 + y, x0 + x, y0 + y, color);
        lcd_draw_line(x0 - y, y0 + x, x0 + y, y0 + x, color);
        lcd_draw_line(x0 - x, y0 - y, x0 + x, y0 - y, color);
        lcd_draw_line(x0 - y, y0 - x, x0 + y, y0 - x, color);
        
        if (err <= 0) {
            y += 1;
            err += 2 * y + 1;
        }
        
        if (err > 0) {
            x -= 1;
            err -= 2 * x + 1;
        }
    }
}

/**
 * @brief  清屏
 */
void lcd_clear(color_t color)
{
    lcd_fill_rectangle(0, 0, LCD_WIDTH, LCD_HEIGHT, color);
}
```

### 3.2 文本渲染

```c
/**
 * @brief  ASCII字体数据结构（8×16点阵）
 */
extern const uint8_t font_8x16[][16];

/**
 * @brief  显示ASCII字符
 */
void lcd_draw_char(uint16_t x, uint16_t y, char ch, color_t fg_color, color_t bg_color)
{
    if (ch < ' ' || ch > '~') {
        ch = ' ';
    }
    
    const uint8_t *font_data = font_8x16[ch - ' '];
    
    for (uint8_t row = 0; row < 16; row++) {
        uint8_t line = font_data[row];
        
        for (uint8_t col = 0; col < 8; col++) {
            if (line & (0x80 >> col)) {
                lcd_draw_pixel(x + col, y + row, fg_color);
            } else {
                lcd_draw_pixel(x + col, y + row, bg_color);
            }
        }
    }
}

/**
 * @brief  显示字符串
 */
void lcd_draw_string(uint16_t x, uint16_t y, const char *str, color_t fg_color, color_t bg_color)
{
    uint16_t x_offset = 0;
    
    while (*str) {
        if (*str == '\n') {
            x_offset = 0;
            y += 16;
        } else {
            lcd_draw_char(x + x_offset, y, *str, fg_color, bg_color);
            x_offset += 8;
            
            if (x + x_offset >= LCD_WIDTH) {
                x_offset = 0;
                y += 16;
            }
        }
        
        str++;
    }
}

/**
 * @brief  显示数字
 */
void lcd_draw_number(uint16_t x, uint16_t y, int32_t num, uint8_t digits, color_t fg_color, color_t bg_color)
{
    char buffer[12];
    snprintf(buffer, sizeof(buffer), "%*d", digits, num);
    lcd_draw_string(x, y, buffer, fg_color, bg_color);
}

/**
 * @brief  显示浮点数
 */
void lcd_draw_float(uint16_t x, uint16_t y, float num, uint8_t decimals, color_t fg_color, color_t bg_color)
{
    char buffer[16];
    snprintf(buffer, sizeof(buffer), "%.*f", decimals, num);
    lcd_draw_string(x, y, buffer, fg_color, bg_color);
}
```

### 3.3 图像显示

```c
/**
 * @brief  显示RGB565图像
 */
void lcd_draw_image(uint16_t x, uint16_t y, uint16_t width, uint16_t height, const uint16_t *image)
{
    lcd_set_window(x, y, x + width - 1, y + height - 1);
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    uint32_t total_pixels = width * height;
    for (uint32_t i = 0; i < total_pixels; i++) {
        uint16_t color = image[i];
        spi_write_byte(color >> 8);
        spi_write_byte(color & 0xFF);
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  显示RGB565图像（DMA加速）
 */
void lcd_draw_image_dma(uint16_t x, uint16_t y, uint16_t width, uint16_t height, const uint16_t *image)
{
    lcd_set_window(x, y, x + width - 1, y + height - 1);
    
    uint32_t total_bytes = width * height * 2;
    lcd_write_data_dma((uint8_t*)image, total_bytes);
}

/**
 * @brief  显示单色位图
 */
void lcd_draw_bitmap(uint16_t x, uint16_t y, uint16_t width, uint16_t height, 
                     const uint8_t *bitmap, color_t fg_color, color_t bg_color)
{
    uint16_t byte_width = (width + 7) / 8;
    
    for (uint16_t row = 0; row < height; row++) {
        for (uint16_t col = 0; col < width; col++) {
            uint16_t byte_index = row * byte_width + col / 8;
            uint8_t bit_index = 7 - (col % 8);
            
            if (bitmap[byte_index] & (1 << bit_index)) {
                lcd_draw_pixel(x + col, y + row, fg_color);
            } else {
                lcd_draw_pixel(x + col, y + row, bg_color);
            }
        }
    }
}
```

## 第四部分：帧缓冲管理

### 4.1 单缓冲模式

```c
/**
 * @brief  单缓冲配置
 */
#define FRAMEBUFFER_SIZE  (LCD_WIDTH * LCD_HEIGHT * 2)  // RGB565

static uint16_t framebuffer[LCD_WIDTH * LCD_HEIGHT];

/**
 * @brief  初始化帧缓冲
 */
void framebuffer_init(void)
{
    memset(framebuffer, 0, FRAMEBUFFER_SIZE);
}

/**
 * @brief  在帧缓冲中画点
 */
void fb_draw_pixel(uint16_t x, uint16_t y, color_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) {
        return;
    }
    
    framebuffer[y * LCD_WIDTH + x] = color;
}

/**
 * @brief  刷新帧缓冲到显示屏
 */
void framebuffer_flush(void)
{
    lcd_draw_image_dma(0, 0, LCD_WIDTH, LCD_HEIGHT, framebuffer);
}

/**
 * @brief  局部刷新
 */
void framebuffer_flush_region(uint16_t x, uint16_t y, uint16_t width, uint16_t height)
{
    lcd_set_window(x, y, x + width - 1, y + height - 1);
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    for (uint16_t row = 0; row < height; row++) {
        uint16_t *line = &framebuffer[(y + row) * LCD_WIDTH + x];
        
        for (uint16_t col = 0; col < width; col++) {
            uint16_t color = line[col];
            spi_write_byte(color >> 8);
            spi_write_byte(color & 0xFF);
        }
    }
    
    LCD_CS_HIGH();
}
```

### 4.2 双缓冲模式

```c
/**
 * @brief  双缓冲配置
 */
static uint16_t framebuffer_front[LCD_WIDTH * LCD_HEIGHT];
static uint16_t framebuffer_back[LCD_WIDTH * LCD_HEIGHT];
static uint16_t *current_fb = framebuffer_back;
static bool fb_swap_pending = false;

/**
 * @brief  在后台缓冲绘制
 */
void fb_draw_pixel_double(uint16_t x, uint16_t y, color_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) {
        return;
    }
    
    current_fb[y * LCD_WIDTH + x] = color;
}

/**
 * @brief  交换缓冲区
 */
void framebuffer_swap(void)
{
    // 等待上次传输完成
    while (fb_swap_pending) {
        // 等待
    }
    
    // 交换指针
    uint16_t *temp = framebuffer_front;
    framebuffer_front = current_fb;
    current_fb = temp;
    
    // 启动DMA传输前台缓冲
    fb_swap_pending = true;
    lcd_draw_image_dma(0, 0, LCD_WIDTH, LCD_HEIGHT, framebuffer_front);
}

/**
 * @brief  DMA传输完成回调
 */
void framebuffer_dma_complete_callback(void)
{
    fb_swap_pending = false;
}
```

### 4.3 脏矩形优化

```c
/**
 * @brief  脏矩形结构
 */
typedef struct {
    uint16_t x;
    uint16_t y;
    uint16_t width;
    uint16_t height;
    bool dirty;
} dirty_rect_t;

#define MAX_DIRTY_RECTS  10

static dirty_rect_t dirty_rects[MAX_DIRTY_RECTS];
static uint8_t dirty_rect_count = 0;

/**
 * @brief  标记脏矩形
 */
void framebuffer_mark_dirty(uint16_t x, uint16_t y, uint16_t width, uint16_t height)
{
    if (dirty_rect_count >= MAX_DIRTY_RECTS) {
        // 合并所有脏矩形
        framebuffer_merge_dirty_rects();
    }
    
    dirty_rects[dirty_rect_count].x = x;
    dirty_rects[dirty_rect_count].y = y;
    dirty_rects[dirty_rect_count].width = width;
    dirty_rects[dirty_rect_count].height = height;
    dirty_rects[dirty_rect_count].dirty = true;
    
    dirty_rect_count++;
}

/**
 * @brief  刷新脏矩形
 */
void framebuffer_flush_dirty(void)
{
    for (uint8_t i = 0; i < dirty_rect_count; i++) {
        if (dirty_rects[i].dirty) {
            framebuffer_flush_region(
                dirty_rects[i].x,
                dirty_rects[i].y,
                dirty_rects[i].width,
                dirty_rects[i].height
            );
            
            dirty_rects[i].dirty = false;
        }
    }
    
    dirty_rect_count = 0;
}

/**
 * @brief  合并脏矩形
 */
void framebuffer_merge_dirty_rects(void)
{
    if (dirty_rect_count == 0) {
        return;
    }
    
    // 计算包围盒
    uint16_t min_x = dirty_rects[0].x;
    uint16_t min_y = dirty_rects[0].y;
    uint16_t max_x = dirty_rects[0].x + dirty_rects[0].width;
    uint16_t max_y = dirty_rects[0].y + dirty_rects[0].height;
    
    for (uint8_t i = 1; i < dirty_rect_count; i++) {
        if (dirty_rects[i].x < min_x) min_x = dirty_rects[i].x;
        if (dirty_rects[i].y < min_y) min_y = dirty_rects[i].y;
        
        uint16_t right = dirty_rects[i].x + dirty_rects[i].width;
        uint16_t bottom = dirty_rects[i].y + dirty_rects[i].height;
        
        if (right > max_x) max_x = right;
        if (bottom > max_y) max_y = bottom;
    }
    
    // 创建合并后的矩形
    dirty_rects[0].x = min_x;
    dirty_rects[0].y = min_y;
    dirty_rects[0].width = max_x - min_x;
    dirty_rects[0].height = max_y - min_y;
    dirty_rects[0].dirty = true;
    
    dirty_rect_count = 1;
}
```

## 第五部分：性能优化

### 5.1 批量操作优化

```c
/**
 * @brief  快速填充（使用DMA）
 */
void lcd_fast_fill(uint16_t x, uint16_t y, uint16_t width, uint16_t height, color_t color)
{
    // 准备填充缓冲区
    static uint16_t fill_buffer[LCD_WIDTH];
    
    for (uint16_t i = 0; i < width; i++) {
        fill_buffer[i] = color;
    }
    
    // 设置窗口
    lcd_set_window(x, y, x + width - 1, y + height - 1);
    
    // 逐行DMA传输
    for (uint16_t row = 0; row < height; row++) {
        lcd_write_data_dma((uint8_t*)fill_buffer, width * 2);
    }
}

/**
 * @brief  快速水平线
 */
void lcd_fast_hline(uint16_t x, uint16_t y, uint16_t width, color_t color)
{
    lcd_set_window(x, y, x + width - 1, y);
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    for (uint16_t i = 0; i < width; i++) {
        spi_write_byte(color >> 8);
        spi_write_byte(color & 0xFF);
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  快速垂直线
 */
void lcd_fast_vline(uint16_t x, uint16_t y, uint16_t height, color_t color)
{
    lcd_set_window(x, y, x, y + height - 1);
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    for (uint16_t i = 0; i < height; i++) {
        spi_write_byte(color >> 8);
        spi_write_byte(color & 0xFF);
    }
    
    LCD_CS_HIGH();
}
```

### 5.2 SPI速度优化

```c
/**
 * @brief  配置高速SPI
 */
void spi_configure_high_speed(void)
{
    // 重新配置SPI为高速模式
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_2;  // 最高速度
    HAL_SPI_Init(&hspi1);
}

/**
 * @brief  性能测试
 */
void lcd_performance_test(void)
{
    uint32_t start_time, end_time;
    
    // 测试1：清屏速度
    start_time = HAL_GetTick();
    lcd_clear(COLOR_BLACK);
    end_time = HAL_GetTick();
    printf("清屏时间: %u ms\n", end_time - start_time);
    
    // 测试2：填充矩形速度
    start_time = HAL_GetTick();
    for (int i = 0; i < 100; i++) {
        lcd_fill_rectangle(10, 10, 100, 100, COLOR_RED);
    }
    end_time = HAL_GetTick();
    printf("100次填充矩形时间: %u ms\n", end_time - start_time);
    
    // 测试3：画线速度
    start_time = HAL_GetTick();
    for (int i = 0; i < 1000; i++) {
        lcd_draw_line(0, 0, 239, 319, COLOR_WHITE);
    }
    end_time = HAL_GetTick();
    printf("1000条线时间: %u ms\n", end_time - start_time);
    
    // 测试4：帧率测试
    start_time = HAL_GetTick();
    uint32_t frames = 0;
    while ((HAL_GetTick() - start_time) < 1000) {
        lcd_clear(COLOR_BLACK);
        lcd_fill_rectangle(50, 50, 140, 220, COLOR_BLUE);
        frames++;
    }
    printf("帧率: %u FPS\n", frames);
}
```

## 第六部分：实战项目

### 6.1 数字仪表盘

```c
/**
 * @brief  绘制仪表盘
 */
typedef struct {
    uint16_t x;
    uint16_t y;
    uint16_t radius;
    float value;
    float min_value;
    float max_value;
    const char *unit;
} gauge_t;

void draw_gauge(gauge_t *gauge)
{
    // 绘制外圆
    lcd_draw_circle(gauge->x, gauge->y, gauge->radius, COLOR_WHITE);
    lcd_draw_circle(gauge->x, gauge->y, gauge->radius - 2, COLOR_WHITE);
    
    // 绘制刻度
    for (int i = 0; i <= 10; i++) {
        float angle = -135.0f + i * 27.0f;  // -135° to +135°
        float rad = angle * 3.14159f / 180.0f;
        
        uint16_t x1 = gauge->x + (gauge->radius - 10) * cos(rad);
        uint16_t y1 = gauge->y + (gauge->radius - 10) * sin(rad);
        uint16_t x2 = gauge->x + (gauge->radius - 5) * cos(rad);
        uint16_t y2 = gauge->y + (gauge->radius - 5) * sin(rad);
        
        lcd_draw_line(x1, y1, x2, y2, COLOR_WHITE);
    }
    
    // 计算指针角度
    float ratio = (gauge->value - gauge->min_value) / (gauge->max_value - gauge->min_value);
    float angle = -135.0f + ratio * 270.0f;
    float rad = angle * 3.14159f / 180.0f;
    
    // 绘制指针
    uint16_t x_end = gauge->x + (gauge->radius - 15) * cos(rad);
    uint16_t y_end = gauge->y + (gauge->radius - 15) * sin(rad);
    
    lcd_draw_line(gauge->x, gauge->y, x_end, y_end, COLOR_RED);
    lcd_fill_circle(gauge->x, gauge->y, 5, COLOR_RED);
    
    // 显示数值
    char buffer[16];
    snprintf(buffer, sizeof(buffer), "%.1f %s", gauge->value, gauge->unit);
    lcd_draw_string(gauge->x - 30, gauge->y + gauge->radius + 10, buffer, COLOR_WHITE, COLOR_BLACK);
}

/**
 * @brief  仪表盘示例
 */
void gauge_example(void)
{
    gauge_t speed_gauge = {
        .x = 120,
        .y = 160,
        .radius = 80,
        .value = 0.0f,
        .min_value = 0.0f,
        .max_value = 200.0f,
        .unit = "km/h"
    };
    
    while (1) {
        // 清除旧仪表
        lcd_fill_circle(speed_gauge.x, speed_gauge.y, speed_gauge.radius + 5, COLOR_BLACK);
        
        // 更新数值
        speed_gauge.value += 5.0f;
        if (speed_gauge.value > speed_gauge.max_value) {
            speed_gauge.value = 0.0f;
        }
        
        // 绘制新仪表
        draw_gauge(&speed_gauge);
        
        HAL_Delay(100);
    }
}
```

### 6.2 实时图表显示

```c
/**
 * @brief  折线图结构
 */
#define MAX_DATA_POINTS  240

typedef struct {
    uint16_t x;
    uint16_t y;
    uint16_t width;
    uint16_t height;
    float data[MAX_DATA_POINTS];
    uint16_t data_count;
    float min_value;
    float max_value;
    color_t line_color;
    color_t bg_color;
} chart_t;

/**
 * @brief  绘制折线图
 */
void draw_chart(chart_t *chart)
{
    // 绘制背景
    lcd_fill_rectangle(chart->x, chart->y, chart->width, chart->height, chart->bg_color);
    
    // 绘制边框
    lcd_draw_rectangle(chart->x, chart->y, chart->width, chart->height, COLOR_WHITE);
    
    // 绘制网格
    for (int i = 1; i < 5; i++) {
        uint16_t y_grid = chart->y + (chart->height * i) / 5;
        lcd_draw_line(chart->x, y_grid, chart->x + chart->width, y_grid, COLOR_GRAY);
    }
    
    // 绘制数据
    if (chart->data_count < 2) {
        return;
    }
    
    float value_range = chart->max_value - chart->min_value;
    
    for (uint16_t i = 0; i < chart->data_count - 1; i++) {
        // 计算坐标
        uint16_t x1 = chart->x + (i * chart->width) / MAX_DATA_POINTS;
        uint16_t x2 = chart->x + ((i + 1) * chart->width) / MAX_DATA_POINTS;
        
        float ratio1 = (chart->data[i] - chart->min_value) / value_range;
        float ratio2 = (chart->data[i + 1] - chart->min_value) / value_range;
        
        uint16_t y1 = chart->y + chart->height - (uint16_t)(ratio1 * chart->height);
        uint16_t y2 = chart->y + chart->height - (uint16_t)(ratio2 * chart->height);
        
        // 绘制线段
        lcd_draw_line(x1, y1, x2, y2, chart->line_color);
    }
}

/**
 * @brief  添加数据点
 */
void chart_add_data(chart_t *chart, float value)
{
    if (chart->data_count >= MAX_DATA_POINTS) {
        // 移动数据
        memmove(chart->data, chart->data + 1, (MAX_DATA_POINTS - 1) * sizeof(float));
        chart->data[MAX_DATA_POINTS - 1] = value;
    } else {
        chart->data[chart->data_count++] = value;
    }
}

/**
 * @brief  图表示例
 */
void chart_example(void)
{
    chart_t temp_chart = {
        .x = 10,
        .y = 50,
        .width = 220,
        .height = 150,
        .data_count = 0,
        .min_value = 0.0f,
        .max_value = 100.0f,
        .line_color = COLOR_GREEN,
        .bg_color = COLOR_BLACK
    };
    
    // 标题
    lcd_draw_string(80, 20, "Temperature", COLOR_WHITE, COLOR_BLACK);
    
    while (1) {
        // 模拟温度数据
        float temp = 50.0f + 20.0f * sin(HAL_GetTick() / 1000.0f);
        
        // 添加数据
        chart_add_data(&temp_chart, temp);
        
        // 重绘图表
        draw_chart(&temp_chart);
        
        // 显示当前值
        char buffer[16];
        snprintf(buffer, sizeof(buffer), "%.1f C", temp);
        lcd_fill_rectangle(10, 220, 100, 20, COLOR_BLACK);
        lcd_draw_string(10, 220, buffer, COLOR_YELLOW, COLOR_BLACK);
        
        HAL_Delay(100);
    }
}
```

## 总结

TFT显示屏驱动开发涉及硬件接口、图形算法、性能优化等多个方面。通过本教程的学习，您应该掌握了：

1. **硬件原理**：TFT LCD工作原理、色彩模型
2. **驱动开发**：ILI9341/ST7789初始化和控制
3. **图形绘制**：基本图形、文本、图像显示
4. **性能优化**：DMA传输、帧缓冲、脏矩形
5. **实战应用**：仪表盘、图表、GUI开发

继续学习相关主题以深化理解：

- [GUI设计模式](01-gui-design-patterns.html)
- [图形优化技术](02-graphics-optimization.html)
<!-- 以下链接指向的文件不存在，待补充后取消注释
- [触摸屏驱动](../advanced/02-touchscreen-driver.html)
- [GPU加速](../advanced/01-gpu-acceleration.html)
-->

祝您在嵌入式图形显示领域取得成功！
