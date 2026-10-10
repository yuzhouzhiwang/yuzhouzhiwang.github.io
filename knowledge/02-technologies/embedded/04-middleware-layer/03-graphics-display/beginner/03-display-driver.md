---
title: "LCD/OLED显示驱动开发实战：从原理到实现"
description: "本教程详细介绍LCD和OLED显示器的工作原理、SPI/I2C接口驱动开发、图形绘制算法和字符显示实现，帮助你掌握嵌入式显示技术"
slug: "lcd-oled-display-driver-development"

# 分类信息
domain: "中间件层"
module: "图形与显示"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - LCD驱动
  - OLED
  - 显示器
  - SPI接口
  - I2C接口
  - 图形绘制
prerequisites: []
related_contents:
  - "04-middleware-layer/03-graphics-display/beginner/01-lvgl-quickstart"
  - "04-middleware-layer/03-graphics-display/beginner/02-touchscreen-driver"

# 学习信息
estimated_time: 75
difficulty_score: 3

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
  - LCD驱动开发
  - OLED驱动
  - SPI显示器
  - I2C显示器
  - 图形绘制
  - 字符显示
cover_image: ""
---

# LCD/OLED显示驱动开发实战：从原理到实现


## 学习目标

完成本教程后，你将能够：

- [ ] 理解LCD和OLED显示器的工作原理和区别
- [ ] 掌握SPI和I2C接口的显示器通信协议
- [ ] 实现ILI9341 TFT LCD的完整驱动
- [ ] 实现SSD1306 OLED的完整驱动
- [ ] 掌握基本图形绘制算法（点、线、矩形、圆）
- [ ] 实现字符和字符串显示功能
- [ ] 理解显示缓冲区和刷新机制
- [ ] 优化显示性能和降低功耗

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉C语言编程
- 了解嵌入式系统基础
- 掌握SPI或I2C通信协议
- 了解基本的数字电路知识

**技能要求**：
- 能够使用嵌入式开发IDE
- 会配置GPIO和外设
- 具备基本的调试能力
- 会使用示波器或逻辑分析仪（推荐）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4系列或ESP32 | STM32F407VGT6 |
| TFT LCD | 1 | 2.4-3.5寸彩色屏 | ILI9341/ST7789 |
| OLED显示屏 | 1 | 0.96-1.3寸单色屏 | SSD1306/SH1106 |
| 杜邦线 | 若干 | 用于连接 | - |

### 软件准备

- **开发环境**：STM32CubeIDE / ESP-IDF / Arduino IDE
- **调试工具**：串口调试助手、逻辑分析仪
- **辅助软件**：
  - 取模软件（用于字体和图片）
  - Image2LCD（图片转换工具）

### 环境配置

1. **创建项目**

```bash
# 使用STM32CubeMX创建新项目
# 配置SPI1和I2C1外设
```

2. **项目目录结构**

```
project/
├── Drivers/
│   ├── lcd_ili9341.c/h    # ILI9341 LCD驱动
│   ├── oled_ssd1306.c/h   # SSD1306 OLED驱动
│   ├── lcd_graphics.c/h   # 图形绘制库
│   └── fonts.c/h          # 字体数据
├── main.c                 # 主程序
└── config.h               # 配置文件
```


## 步骤1：显示器原理介绍

### 1.1 LCD显示原理

**LCD (Liquid Crystal Display)** 液晶显示器通过控制液晶分子的排列来控制光的透过率。

**TFT LCD结构**：

```
背光层
   ↓
偏振片
   ↓
玻璃基板
   ↓
液晶层 ← 控制电压
   ↓
彩色滤光片 (RGB)
   ↓
偏振片
   ↓
显示面
```

**特点**：
- ✅ 色彩丰富，支持真彩色显示
- ✅ 分辨率高，可达数百万像素
- ✅ 视角大，可视范围广
- ✅ 成本适中
- ❌ 需要背光，功耗较高
- ❌ 对比度相对较低
- ❌ 响应速度较慢

**常见LCD控制器**：

| 控制器 | 分辨率 | 接口 | 色深 | 特点 |
|--------|--------|------|------|------|
| ILI9341 | 240×320 | SPI/并口 | 18位 | 应用广泛 |
| ST7789 | 240×320 | SPI | 18位 | 低功耗 |
| ST7735 | 128×160 | SPI | 18位 | 小尺寸 |
| ILI9486 | 320×480 | SPI/并口 | 18位 | 大屏幕 |

### 1.2 OLED显示原理

**OLED (Organic Light-Emitting Diode)** 有机发光二极管显示器，每个像素自发光。

**OLED结构**：

```
玻璃基板
   ↓
阳极 (ITO)
   ↓
有机发光层 ← 通电发光
   ↓
阴极
   ↓
封装层
```

**特点**：
- ✅ 自发光，无需背光
- ✅ 对比度极高（黑色完全不发光）
- ✅ 响应速度快（微秒级）
- ✅ 超薄，可弯曲
- ✅ 功耗低（显示黑色时）
- ❌ 成本较高
- ❌ 寿命相对较短
- ❌ 容易烧屏

**常见OLED控制器**：

| 控制器 | 分辨率 | 接口 | 色深 | 特点 |
|--------|--------|------|------|------|
| SSD1306 | 128×64 | I2C/SPI | 单色 | 最常用 |
| SH1106 | 128×64 | I2C/SPI | 单色 | 兼容1306 |
| SSD1351 | 128×128 | SPI | 彩色 | 支持65K色 |
| SSD1331 | 96×64 | SPI | 彩色 | 小尺寸彩屏 |

### 1.3 显示接口对比

**SPI接口**：
- 速度快（可达几十MHz）
- 引脚少（4-5根）
- 适合高分辨率彩屏
- 单向通信，无法读取显存

**I2C接口**：
- 速度较慢（通常400kHz）
- 引脚最少（2根）
- 适合小尺寸单色屏
- 双向通信，可读取状态

**并口接口**：
- 速度最快
- 引脚多（8-16根数据线）
- 适合大屏幕
- 占用GPIO资源多


## 步骤2：ILI9341 TFT LCD驱动开发

### 2.1 硬件连接

**ILI9341引脚定义**：

| 引脚 | 功能 | 连接到MCU | 说明 |
|------|------|-----------|------|
| VCC | 电源 | 3.3V/5V | 根据模块要求 |
| GND | 地 | GND | - |
| CS | 片选 | PA4 | 低电平有效 |
| RESET | 复位 | PA3 | 低电平复位 |
| DC | 数据/命令 | PA2 | 0=命令, 1=数据 |
| SDI(MOSI) | 数据输入 | PA7 (SPI1_MOSI) | - |
| SCK | 时钟 | PA5 (SPI1_SCK) | - |
| LED | 背光 | PA1 | PWM控制亮度 |
| SDO(MISO) | 数据输出 | PA6 (可选) | 读取功能 |

**连接示意图**：

```
STM32F4          ILI9341
  PA1  --------> LED (背光)
  PA2  --------> DC
  PA3  --------> RESET
  PA4  --------> CS
  PA5  --------> SCK
  PA7  --------> SDI(MOSI)
  3.3V --------> VCC
  GND  --------> GND
```

### 2.2 创建驱动头文件

创建 `lcd_ili9341.h` 文件：

```c
#ifndef LCD_ILI9341_H
#define LCD_ILI9341_H

#include "stdint.h"
#include "stdbool.h"

/* LCD分辨率 */
#define LCD_WIDTH   240
#define LCD_HEIGHT  320

/* 颜色定义 (RGB565格式) */
#define COLOR_WHITE   0xFFFF
#define COLOR_BLACK   0x0000
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_YELLOW  0xFFE0
#define COLOR_CYAN    0x07FF
#define COLOR_MAGENTA 0xF81F
#define COLOR_GRAY    0x8410

/* 显示方向 */
typedef enum {
    LCD_ORIENTATION_PORTRAIT = 0,      // 竖屏
    LCD_ORIENTATION_LANDSCAPE = 1,     // 横屏
    LCD_ORIENTATION_PORTRAIT_INV = 2,  // 竖屏倒置
    LCD_ORIENTATION_LANDSCAPE_INV = 3  // 横屏倒置
} LCD_Orientation_t;

/* 函数声明 */
void LCD_Init(void);
void LCD_SetOrientation(LCD_Orientation_t orientation);
void LCD_SetBacklight(uint8_t brightness);
void LCD_Clear(uint16_t color);
void LCD_DrawPixel(uint16_t x, uint16_t y, uint16_t color);
void LCD_DrawLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, uint16_t color);
void LCD_DrawRect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color);
void LCD_FillRect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color);
void LCD_DrawCircle(uint16_t x0, uint16_t y0, uint16_t radius, uint16_t color);
void LCD_FillCircle(uint16_t x0, uint16_t y0, uint16_t radius, uint16_t color);
void LCD_DrawChar(uint16_t x, uint16_t y, char ch, uint16_t color, uint16_t bg_color);
void LCD_DrawString(uint16_t x, uint16_t y, const char *str, uint16_t color, uint16_t bg_color);

#endif
```

### 2.3 实现底层通信函数

创建 `lcd_ili9341.c` 文件：

```c
#include "lcd_ili9341.h"
#include "main.h"

/* 引脚定义 */
#define LCD_CS_PIN    GPIO_PIN_4
#define LCD_CS_PORT   GPIOA
#define LCD_RST_PIN   GPIO_PIN_3
#define LCD_RST_PORT  GPIOA
#define LCD_DC_PIN    GPIO_PIN_2
#define LCD_DC_PORT   GPIOA
#define LCD_LED_PIN   GPIO_PIN_1
#define LCD_LED_PORT  GPIOA

/* 引脚控制宏 */
#define LCD_CS_LOW()   HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET)
#define LCD_CS_HIGH()  HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET)
#define LCD_RST_LOW()  HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_RESET)
#define LCD_RST_HIGH() HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET)
#define LCD_DC_LOW()   HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET)
#define LCD_DC_HIGH()  HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET)

/* 外部SPI句柄 */
extern SPI_HandleTypeDef hspi1;

/* ILI9341命令定义 */
#define ILI9341_SWRESET   0x01  // 软件复位
#define ILI9341_SLPOUT    0x11  // 退出睡眠
#define ILI9341_DISPOFF   0x28  // 关闭显示
#define ILI9341_DISPON    0x29  // 开启显示
#define ILI9341_CASET     0x2A  // 列地址设置
#define ILI9341_PASET     0x2B  // 页地址设置
#define ILI9341_RAMWR     0x2C  // 写入显存
#define ILI9341_MADCTL    0x36  // 内存访问控制
#define ILI9341_PIXFMT    0x3A  // 像素格式设置

/**
 * @brief  写命令到LCD
 * @param  cmd: 命令字节
 */
static void LCD_WriteCmd(uint8_t cmd)
{
    LCD_DC_LOW();   // DC=0表示命令
    LCD_CS_LOW();
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
    LCD_CS_HIGH();
}

/**
 * @brief  写数据到LCD
 * @param  data: 数据字节
 */
static void LCD_WriteData(uint8_t data)
{
    LCD_DC_HIGH();  // DC=1表示数据
    LCD_CS_LOW();
    HAL_SPI_Transmit(&hspi1, &data, 1, HAL_MAX_DELAY);
    LCD_CS_HIGH();
}

/**
 * @brief  写16位数据到LCD
 * @param  data: 16位数据
 */
static void LCD_WriteData16(uint16_t data)
{
    uint8_t buf[2];
    buf[0] = data >> 8;    // 高字节
    buf[1] = data & 0xFF;  // 低字节
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    HAL_SPI_Transmit(&hspi1, buf, 2, HAL_MAX_DELAY);
    LCD_CS_HIGH();
}

/**
 * @brief  批量写数据到LCD
 * @param  data: 数据缓冲区
 * @param  len: 数据长度
 */
static void LCD_WriteDataBuf(uint16_t *data, uint32_t len)
{
    LCD_DC_HIGH();
    LCD_CS_LOW();
    HAL_SPI_Transmit(&hspi1, (uint8_t*)data, len * 2, HAL_MAX_DELAY);
    LCD_CS_HIGH();
}
```


### 2.4 实现LCD初始化

```c
/**
 * @brief  硬件复位LCD
 */
static void LCD_HardwareReset(void)
{
    LCD_RST_HIGH();
    HAL_Delay(10);
    LCD_RST_LOW();
    HAL_Delay(10);
    LCD_RST_HIGH();
    HAL_Delay(120);
}

/**
 * @brief  设置显示窗口
 * @param  x1, y1: 起始坐标
 * @param  x2, y2: 结束坐标
 */
static void LCD_SetWindow(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    /* 列地址设置 */
    LCD_WriteCmd(ILI9341_CASET);
    LCD_WriteData16(x1);
    LCD_WriteData16(x2);
    
    /* 行地址设置 */
    LCD_WriteCmd(ILI9341_PASET);
    LCD_WriteData16(y1);
    LCD_WriteData16(y2);
    
    /* 开始写入显存 */
    LCD_WriteCmd(ILI9341_RAMWR);
}

/**
 * @brief  LCD初始化
 */
void LCD_Init(void)
{
    /* 硬件复位 */
    LCD_HardwareReset();
    
    /* 软件复位 */
    LCD_WriteCmd(ILI9341_SWRESET);
    HAL_Delay(120);
    
    /* 退出睡眠模式 */
    LCD_WriteCmd(ILI9341_SLPOUT);
    HAL_Delay(120);
    
    /* 像素格式设置：16位色 (RGB565) */
    LCD_WriteCmd(ILI9341_PIXFMT);
    LCD_WriteData(0x55);  // 16位/像素
    
    /* 内存访问控制 */
    LCD_WriteCmd(ILI9341_MADCTL);
    LCD_WriteData(0x48);  // MY=0, MX=1, MV=0, ML=0, BGR=1
    
    /* 开启显示 */
    LCD_WriteCmd(ILI9341_DISPON);
    HAL_Delay(10);
    
    /* 开启背光 */
    LCD_SetBacklight(100);
    
    /* 清屏 */
    LCD_Clear(COLOR_BLACK);
}

/**
 * @brief  设置背光亮度
 * @param  brightness: 亮度值 (0-100)
 */
void LCD_SetBacklight(uint8_t brightness)
{
    /* 使用PWM控制背光亮度 */
    if (brightness > 100) brightness = 100;
    
    /* 简单实现：直接开关背光 */
    if (brightness > 0) {
        HAL_GPIO_WritePin(LCD_LED_PORT, LCD_LED_PIN, GPIO_PIN_SET);
    } else {
        HAL_GPIO_WritePin(LCD_LED_PORT, LCD_LED_PIN, GPIO_PIN_RESET);
    }
    
    /* 如果配置了PWM，可以使用以下代码：
    uint16_t pulse = (brightness * TIM_PERIOD) / 100;
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse);
    */
}

/**
 * @brief  设置显示方向
 * @param  orientation: 显示方向
 */
void LCD_SetOrientation(LCD_Orientation_t orientation)
{
    uint8_t madctl = 0x48;  // 基础值：BGR=1
    
    switch (orientation) {
        case LCD_ORIENTATION_PORTRAIT:
            madctl = 0x48;  // MY=0, MX=1, MV=0
            break;
        case LCD_ORIENTATION_LANDSCAPE:
            madctl = 0x28;  // MY=0, MX=0, MV=1
            break;
        case LCD_ORIENTATION_PORTRAIT_INV:
            madctl = 0x88;  // MY=1, MX=0, MV=0
            break;
        case LCD_ORIENTATION_LANDSCAPE_INV:
            madctl = 0xE8;  // MY=1, MX=1, MV=1
            break;
    }
    
    LCD_WriteCmd(ILI9341_MADCTL);
    LCD_WriteData(madctl);
}
```

### 2.5 实现基本绘图函数

```c
/**
 * @brief  清屏
 * @param  color: 填充颜色
 */
void LCD_Clear(uint16_t color)
{
    LCD_FillRect(0, 0, LCD_WIDTH, LCD_HEIGHT, color);
}

/**
 * @brief  画点
 * @param  x, y: 坐标
 * @param  color: 颜色
 */
void LCD_DrawPixel(uint16_t x, uint16_t y, uint16_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
    
    LCD_SetWindow(x, y, x, y);
    LCD_WriteData16(color);
}

/**
 * @brief  画线（Bresenham算法）
 * @param  x1, y1: 起点坐标
 * @param  x2, y2: 终点坐标
 * @param  color: 颜色
 */
void LCD_DrawLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, uint16_t color)
{
    int16_t dx = abs(x2 - x1);
    int16_t dy = abs(y2 - y1);
    int16_t sx = (x1 < x2) ? 1 : -1;
    int16_t sy = (y1 < y2) ? 1 : -1;
    int16_t err = dx - dy;
    
    while (1) {
        LCD_DrawPixel(x1, y1, color);
        
        if (x1 == x2 && y1 == y2) break;
        
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
 * @param  x, y: 左上角坐标
 * @param  width, height: 宽度和高度
 * @param  color: 颜色
 */
void LCD_DrawRect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color)
{
    LCD_DrawLine(x, y, x + width - 1, y, color);                    // 上边
    LCD_DrawLine(x, y + height - 1, x + width - 1, y + height - 1, color);  // 下边
    LCD_DrawLine(x, y, x, y + height - 1, color);                   // 左边
    LCD_DrawLine(x + width - 1, y, x + width - 1, y + height - 1, color);   // 右边
}

/**
 * @brief  填充矩形
 * @param  x, y: 左上角坐标
 * @param  width, height: 宽度和高度
 * @param  color: 颜色
 */
void LCD_FillRect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
    if (x + width > LCD_WIDTH) width = LCD_WIDTH - x;
    if (y + height > LCD_HEIGHT) height = LCD_HEIGHT - y;
    
    LCD_SetWindow(x, y, x + width - 1, y + height - 1);
    
    /* 批量写入像素数据 */
    uint32_t total_pixels = width * height;
    
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    for (uint32_t i = 0; i < total_pixels; i++) {
        uint8_t buf[2] = {color >> 8, color & 0xFF};
        HAL_SPI_Transmit(&hspi1, buf, 2, HAL_MAX_DELAY);
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  画圆（中点圆算法）
 * @param  x0, y0: 圆心坐标
 * @param  radius: 半径
 * @param  color: 颜色
 */
void LCD_DrawCircle(uint16_t x0, uint16_t y0, uint16_t radius, uint16_t color)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 0;
    
    while (x >= y) {
        LCD_DrawPixel(x0 + x, y0 + y, color);
        LCD_DrawPixel(x0 + y, y0 + x, color);
        LCD_DrawPixel(x0 - y, y0 + x, color);
        LCD_DrawPixel(x0 - x, y0 + y, color);
        LCD_DrawPixel(x0 - x, y0 - y, color);
        LCD_DrawPixel(x0 - y, y0 - x, color);
        LCD_DrawPixel(x0 + y, y0 - x, color);
        LCD_DrawPixel(x0 + x, y0 - y, color);
        
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
 * @param  x0, y0: 圆心坐标
 * @param  radius: 半径
 * @param  color: 颜色
 */
void LCD_FillCircle(uint16_t x0, uint16_t y0, uint16_t radius, uint16_t color)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 0;
    
    while (x >= y) {
        LCD_DrawLine(x0 - x, y0 + y, x0 + x, y0 + y, color);
        LCD_DrawLine(x0 - y, y0 + x, x0 + y, y0 + x, color);
        LCD_DrawLine(x0 - x, y0 - y, x0 + x, y0 - y, color);
        LCD_DrawLine(x0 - y, y0 - x, x0 + y, y0 - x, color);
        
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
```


### 2.6 实现字符显示

首先需要定义字体数据。创建 `fonts.h` 文件：

```c
#ifndef FONTS_H
#define FONTS_H

#include "stdint.h"

/* 8x16字体 */
extern const uint8_t Font8x16[];

/* 获取字符字模 */
const uint8_t* Font_GetChar(char ch);

#endif
```

创建 `fonts.c` 文件（这里只展示部分字符）：

```c
#include "fonts.h"

/* 8x16 ASCII字体数据 */
const uint8_t Font8x16[] = {
    /* 空格 (0x20) */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    
    /* ! (0x21) */
    0x00, 0x00, 0x00, 0xF8, 0xF8, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x33, 0x33, 0x00, 0x00, 0x00,
    
    /* A (0x41) */
    0x00, 0x00, 0xC0, 0x38, 0xE0, 0x00, 0x00, 0x00,
    0x20, 0x3C, 0x23, 0x02, 0x02, 0x27, 0x38, 0x20,
    
    /* ... 更多字符数据 ... */
};

/**
 * @brief  获取字符字模
 * @param  ch: 字符
 * @retval 字模数据指针
 */
const uint8_t* Font_GetChar(char ch)
{
    if (ch < 0x20 || ch > 0x7E) {
        ch = 0x20;  // 不支持的字符显示为空格
    }
    return &Font8x16[(ch - 0x20) * 16];
}
```

在 `lcd_ili9341.c` 中实现字符显示函数：

```c
/**
 * @brief  显示单个字符
 * @param  x, y: 起始坐标
 * @param  ch: 字符
 * @param  color: 前景色
 * @param  bg_color: 背景色
 */
void LCD_DrawChar(uint16_t x, uint16_t y, char ch, uint16_t color, uint16_t bg_color)
{
    const uint8_t *font = Font_GetChar(ch);
    
    for (uint8_t i = 0; i < 16; i++) {
        uint8_t line = font[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (line & 0x80) {
                LCD_DrawPixel(x + j, y + i, color);
            } else {
                LCD_DrawPixel(x + j, y + i, bg_color);
            }
            line <<= 1;
        }
    }
}

/**
 * @brief  显示字符串
 * @param  x, y: 起始坐标
 * @param  str: 字符串
 * @param  color: 前景色
 * @param  bg_color: 背景色
 */
void LCD_DrawString(uint16_t x, uint16_t y, const char *str, uint16_t color, uint16_t bg_color)
{
    uint16_t x_offset = 0;
    
    while (*str) {
        if (*str == '\n') {
            /* 换行 */
            y += 16;
            x_offset = 0;
        } else {
            LCD_DrawChar(x + x_offset, y, *str, color, bg_color);
            x_offset += 8;
            
            /* 自动换行 */
            if (x + x_offset >= LCD_WIDTH) {
                y += 16;
                x_offset = 0;
            }
        }
        str++;
    }
}

/**
 * @brief  显示数字
 * @param  x, y: 起始坐标
 * @param  num: 数字
 * @param  len: 显示长度
 * @param  color: 前景色
 * @param  bg_color: 背景色
 */
void LCD_DrawNumber(uint16_t x, uint16_t y, int32_t num, uint8_t len, uint16_t color, uint16_t bg_color)
{
    char buf[12];
    snprintf(buf, sizeof(buf), "%*d", len, num);
    LCD_DrawString(x, y, buf, color, bg_color);
}
```


## 步骤3：SSD1306 OLED驱动开发

### 3.1 硬件连接

**SSD1306引脚定义（I2C接口）**：

| 引脚 | 功能 | 连接到MCU | 说明 |
|------|------|-----------|------|
| VCC | 电源 | 3.3V | - |
| GND | 地 | GND | - |
| SCL | I2C时钟 | PB6 (I2C1_SCL) | - |
| SDA | I2C数据 | PB7 (I2C1_SDA) | - |

**连接示意图**：

```
STM32F4          SSD1306
  PB6  --------> SCL
  PB7  <-------> SDA
  3.3V --------> VCC
  GND  --------> GND
```

### 3.2 创建OLED驱动头文件

创建 `oled_ssd1306.h` 文件：

```c
#ifndef OLED_SSD1306_H
#define OLED_SSD1306_H

#include "stdint.h"
#include "stdbool.h"

/* OLED分辨率 */
#define OLED_WIDTH   128
#define OLED_HEIGHT  64

/* 颜色定义（单色屏） */
#define OLED_COLOR_BLACK  0
#define OLED_COLOR_WHITE  1

/* 函数声明 */
void OLED_Init(void);
void OLED_Clear(void);
void OLED_Display(void);
void OLED_DrawPixel(uint8_t x, uint8_t y, uint8_t color);
void OLED_DrawLine(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2, uint8_t color);
void OLED_DrawRect(uint8_t x, uint8_t y, uint8_t width, uint8_t height, uint8_t color);
void OLED_FillRect(uint8_t x, uint8_t y, uint8_t width, uint8_t height, uint8_t color);
void OLED_DrawCircle(uint8_t x0, uint8_t y0, uint8_t radius, uint8_t color);
void OLED_DrawChar(uint8_t x, uint8_t y, char ch, uint8_t color);
void OLED_DrawString(uint8_t x, uint8_t y, const char *str, uint8_t color);
void OLED_SetContrast(uint8_t contrast);
void OLED_SetInvert(bool invert);

#endif
```

### 3.3 实现I2C通信函数

创建 `oled_ssd1306.c` 文件：

```c
#include "oled_ssd1306.h"
#include "main.h"
#include <string.h>

/* I2C地址 */
#define SSD1306_I2C_ADDR  0x78  // 0x3C << 1

/* 命令/数据标志 */
#define SSD1306_CMD   0x00
#define SSD1306_DATA  0x40

/* SSD1306命令定义 */
#define SSD1306_SETCONTRAST         0x81
#define SSD1306_DISPLAYALLON_RESUME 0xA4
#define SSD1306_DISPLAYALLON        0xA5
#define SSD1306_NORMALDISPLAY       0xA6
#define SSD1306_INVERTDISPLAY       0xA7
#define SSD1306_DISPLAYOFF          0xAE
#define SSD1306_DISPLAYON           0xAF
#define SSD1306_SETDISPLAYOFFSET    0xD3
#define SSD1306_SETCOMPINS          0xDA
#define SSD1306_SETVCOMDETECT       0xDB
#define SSD1306_SETDISPLAYCLOCKDIV  0xD5
#define SSD1306_SETPRECHARGE        0xD9
#define SSD1306_SETMULTIPLEX        0xA8
#define SSD1306_SETLOWCOLUMN        0x00
#define SSD1306_SETHIGHCOLUMN       0x10
#define SSD1306_SETSTARTLINE        0x40
#define SSD1306_MEMORYMODE          0x20
#define SSD1306_COLUMNADDR          0x21
#define SSD1306_PAGEADDR            0x22
#define SSD1306_COMSCANINC          0xC0
#define SSD1306_COMSCANDEC          0xC8
#define SSD1306_SEGREMAP            0xA0
#define SSD1306_CHARGEPUMP          0x8D

/* 外部I2C句柄 */
extern I2C_HandleTypeDef hi2c1;

/* 显示缓冲区 */
static uint8_t oled_buffer[OLED_WIDTH * OLED_HEIGHT / 8];

/**
 * @brief  写命令到OLED
 * @param  cmd: 命令字节
 */
static void OLED_WriteCmd(uint8_t cmd)
{
    uint8_t buf[2] = {SSD1306_CMD, cmd};
    HAL_I2C_Master_Transmit(&hi2c1, SSD1306_I2C_ADDR, buf, 2, HAL_MAX_DELAY);
}

/**
 * @brief  写数据到OLED
 * @param  data: 数据字节
 */
static void OLED_WriteData(uint8_t data)
{
    uint8_t buf[2] = {SSD1306_DATA, data};
    HAL_I2C_Master_Transmit(&hi2c1, SSD1306_I2C_ADDR, buf, 2, HAL_MAX_DELAY);
}

/**
 * @brief  OLED初始化
 */
void OLED_Init(void)
{
    HAL_Delay(100);  // 等待OLED上电稳定
    
    /* 关闭显示 */
    OLED_WriteCmd(SSD1306_DISPLAYOFF);
    
    /* 设置显示时钟分频 */
    OLED_WriteCmd(SSD1306_SETDISPLAYCLOCKDIV);
    OLED_WriteCmd(0x80);
    
    /* 设置多路复用比 */
    OLED_WriteCmd(SSD1306_SETMULTIPLEX);
    OLED_WriteCmd(0x3F);  // 64行
    
    /* 设置显示偏移 */
    OLED_WriteCmd(SSD1306_SETDISPLAYOFFSET);
    OLED_WriteCmd(0x00);
    
    /* 设置起始行 */
    OLED_WriteCmd(SSD1306_SETSTARTLINE | 0x00);
    
    /* 使能电荷泵 */
    OLED_WriteCmd(SSD1306_CHARGEPUMP);
    OLED_WriteCmd(0x14);
    
    /* 设置内存寻址模式 */
    OLED_WriteCmd(SSD1306_MEMORYMODE);
    OLED_WriteCmd(0x00);  // 水平寻址模式
    
    /* 设置段重映射 */
    OLED_WriteCmd(SSD1306_SEGREMAP | 0x01);
    
    /* 设置COM扫描方向 */
    OLED_WriteCmd(SSD1306_COMSCANDEC);
    
    /* 设置COM引脚配置 */
    OLED_WriteCmd(SSD1306_SETCOMPINS);
    OLED_WriteCmd(0x12);
    
    /* 设置对比度 */
    OLED_WriteCmd(SSD1306_SETCONTRAST);
    OLED_WriteCmd(0xCF);
    
    /* 设置预充电周期 */
    OLED_WriteCmd(SSD1306_SETPRECHARGE);
    OLED_WriteCmd(0xF1);
    
    /* 设置VCOMH电压 */
    OLED_WriteCmd(SSD1306_SETVCOMDETECT);
    OLED_WriteCmd(0x40);
    
    /* 全局显示开启 */
    OLED_WriteCmd(SSD1306_DISPLAYALLON_RESUME);
    
    /* 正常显示 */
    OLED_WriteCmd(SSD1306_NORMALDISPLAY);
    
    /* 开启显示 */
    OLED_WriteCmd(SSD1306_DISPLAYON);
    
    /* 清空缓冲区 */
    OLED_Clear();
    OLED_Display();
}

/**
 * @brief  清空显示缓冲区
 */
void OLED_Clear(void)
{
    memset(oled_buffer, 0, sizeof(oled_buffer));
}

/**
 * @brief  刷新显示（将缓冲区数据发送到OLED）
 */
void OLED_Display(void)
{
    /* 设置列地址范围 */
    OLED_WriteCmd(SSD1306_COLUMNADDR);
    OLED_WriteCmd(0);              // 起始列
    OLED_WriteCmd(OLED_WIDTH - 1); // 结束列
    
    /* 设置页地址范围 */
    OLED_WriteCmd(SSD1306_PAGEADDR);
    OLED_WriteCmd(0);              // 起始页
    OLED_WriteCmd(7);              // 结束页 (64/8=8页)
    
    /* 发送缓冲区数据 */
    for (uint16_t i = 0; i < sizeof(oled_buffer); i++) {
        OLED_WriteData(oled_buffer[i]);
    }
}
```


### 3.4 实现OLED绘图函数

```c
/**
 * @brief  画点
 * @param  x, y: 坐标
 * @param  color: 颜色 (0=黑, 1=白)
 */
void OLED_DrawPixel(uint8_t x, uint8_t y, uint8_t color)
{
    if (x >= OLED_WIDTH || y >= OLED_HEIGHT) return;
    
    /* 计算缓冲区位置 */
    uint16_t index = x + (y / 8) * OLED_WIDTH;
    uint8_t bit = y % 8;
    
    if (color) {
        oled_buffer[index] |= (1 << bit);   // 设置位
    } else {
        oled_buffer[index] &= ~(1 << bit);  // 清除位
    }
}

/**
 * @brief  画线
 * @param  x1, y1: 起点坐标
 * @param  x2, y2: 终点坐标
 * @param  color: 颜色
 */
void OLED_DrawLine(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2, uint8_t color)
{
    int16_t dx = abs(x2 - x1);
    int16_t dy = abs(y2 - y1);
    int16_t sx = (x1 < x2) ? 1 : -1;
    int16_t sy = (y1 < y2) ? 1 : -1;
    int16_t err = dx - dy;
    
    while (1) {
        OLED_DrawPixel(x1, y1, color);
        
        if (x1 == x2 && y1 == y2) break;
        
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
 * @param  x, y: 左上角坐标
 * @param  width, height: 宽度和高度
 * @param  color: 颜色
 */
void OLED_DrawRect(uint8_t x, uint8_t y, uint8_t width, uint8_t height, uint8_t color)
{
    OLED_DrawLine(x, y, x + width - 1, y, color);
    OLED_DrawLine(x, y + height - 1, x + width - 1, y + height - 1, color);
    OLED_DrawLine(x, y, x, y + height - 1, color);
    OLED_DrawLine(x + width - 1, y, x + width - 1, y + height - 1, color);
}

/**
 * @brief  填充矩形
 * @param  x, y: 左上角坐标
 * @param  width, height: 宽度和高度
 * @param  color: 颜色
 */
void OLED_FillRect(uint8_t x, uint8_t y, uint8_t width, uint8_t height, uint8_t color)
{
    for (uint8_t i = 0; i < height; i++) {
        OLED_DrawLine(x, y + i, x + width - 1, y + i, color);
    }
}

/**
 * @brief  画圆
 * @param  x0, y0: 圆心坐标
 * @param  radius: 半径
 * @param  color: 颜色
 */
void OLED_DrawCircle(uint8_t x0, uint8_t y0, uint8_t radius, uint8_t color)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 0;
    
    while (x >= y) {
        OLED_DrawPixel(x0 + x, y0 + y, color);
        OLED_DrawPixel(x0 + y, y0 + x, color);
        OLED_DrawPixel(x0 - y, y0 + x, color);
        OLED_DrawPixel(x0 - x, y0 + y, color);
        OLED_DrawPixel(x0 - x, y0 - y, color);
        OLED_DrawPixel(x0 - y, y0 - x, color);
        OLED_DrawPixel(x0 + y, y0 - x, color);
        OLED_DrawPixel(x0 + x, y0 - y, color);
        
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
 * @brief  显示字符
 * @param  x, y: 起始坐标
 * @param  ch: 字符
 * @param  color: 颜色
 */
void OLED_DrawChar(uint8_t x, uint8_t y, char ch, uint8_t color)
{
    const uint8_t *font = Font_GetChar(ch);
    
    for (uint8_t i = 0; i < 16; i++) {
        uint8_t line = font[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (line & 0x80) {
                OLED_DrawPixel(x + j, y + i, color);
            } else {
                OLED_DrawPixel(x + j, y + i, !color);
            }
            line <<= 1;
        }
    }
}

/**
 * @brief  显示字符串
 * @param  x, y: 起始坐标
 * @param  str: 字符串
 * @param  color: 颜色
 */
void OLED_DrawString(uint8_t x, uint8_t y, const char *str, uint8_t color)
{
    uint8_t x_offset = 0;
    
    while (*str) {
        if (*str == '\n') {
            y += 16;
            x_offset = 0;
        } else {
            OLED_DrawChar(x + x_offset, y, *str, color);
            x_offset += 8;
            
            if (x + x_offset >= OLED_WIDTH) {
                y += 16;
                x_offset = 0;
            }
        }
        str++;
    }
}

/**
 * @brief  设置对比度
 * @param  contrast: 对比度值 (0-255)
 */
void OLED_SetContrast(uint8_t contrast)
{
    OLED_WriteCmd(SSD1306_SETCONTRAST);
    OLED_WriteCmd(contrast);
}

/**
 * @brief  设置反色显示
 * @param  invert: true=反色, false=正常
 */
void OLED_SetInvert(bool invert)
{
    if (invert) {
        OLED_WriteCmd(SSD1306_INVERTDISPLAY);
    } else {
        OLED_WriteCmd(SSD1306_NORMALDISPLAY);
    }
}
```


## 步骤4：显示性能优化

### 4.1 使用DMA传输

使用DMA可以大幅提高数据传输速度，释放CPU资源。

**配置DMA**：

```c
/* 在CubeMX中配置SPI1的DMA */
// SPI1_TX -> DMA2 Stream 3 Channel 3

/**
 * @brief  使用DMA批量写数据
 * @param  data: 数据缓冲区
 * @param  len: 数据长度（字节数）
 */
void LCD_WriteDataBuf_DMA(uint16_t *data, uint32_t len)
{
    LCD_DC_HIGH();
    LCD_CS_LOW();
    
    /* 启动DMA传输 */
    HAL_SPI_Transmit_DMA(&hspi1, (uint8_t*)data, len * 2);
    
    /* 等待传输完成 */
    while (HAL_SPI_GetState(&hspi1) != HAL_SPI_STATE_READY) {
        // 可以在这里执行其他任务
    }
    
    LCD_CS_HIGH();
}

/**
 * @brief  优化的填充矩形（使用DMA）
 */
void LCD_FillRect_Fast(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color)
{
    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
    if (x + width > LCD_WIDTH) width = LCD_WIDTH - x;
    if (y + height > LCD_HEIGHT) height = LCD_HEIGHT - y;
    
    LCD_SetWindow(x, y, x + width - 1, y + height - 1);
    
    /* 准备颜色缓冲区 */
    static uint16_t color_buf[LCD_WIDTH];
    for (uint16_t i = 0; i < width; i++) {
        color_buf[i] = color;
    }
    
    /* 逐行使用DMA传输 */
    for (uint16_t i = 0; i < height; i++) {
        LCD_WriteDataBuf_DMA(color_buf, width);
    }
}
```

### 4.2 局部刷新优化

只刷新变化的区域可以显著提高性能。

```c
/* 脏区域标记 */
typedef struct {
    uint16_t x1, y1;  // 左上角
    uint16_t x2, y2;  // 右下角
    bool dirty;       // 是否需要刷新
} DirtyRegion_t;

static DirtyRegion_t dirty_region = {0};

/**
 * @brief  标记脏区域
 * @param  x, y: 起始坐标
 * @param  width, height: 宽度和高度
 */
void LCD_MarkDirty(uint16_t x, uint16_t y, uint16_t width, uint16_t height)
{
    if (!dirty_region.dirty) {
        /* 第一次标记 */
        dirty_region.x1 = x;
        dirty_region.y1 = y;
        dirty_region.x2 = x + width - 1;
        dirty_region.y2 = y + height - 1;
        dirty_region.dirty = true;
    } else {
        /* 扩展脏区域 */
        if (x < dirty_region.x1) dirty_region.x1 = x;
        if (y < dirty_region.y1) dirty_region.y1 = y;
        if (x + width - 1 > dirty_region.x2) dirty_region.x2 = x + width - 1;
        if (y + height - 1 > dirty_region.y2) dirty_region.y2 = y + height - 1;
    }
}

/**
 * @brief  刷新脏区域
 */
void LCD_RefreshDirty(void)
{
    if (!dirty_region.dirty) return;
    
    /* 刷新脏区域 */
    // 这里需要配合显示缓冲区使用
    // 只传输脏区域的数据到LCD
    
    /* 清除脏标记 */
    dirty_region.dirty = false;
}
```

### 4.3 双缓冲技术

使用双缓冲可以避免画面撕裂。

```c
/* 双缓冲区 */
static uint16_t frame_buffer[2][LCD_WIDTH * LCD_HEIGHT];
static uint8_t current_buffer = 0;

/**
 * @brief  获取当前绘图缓冲区
 */
uint16_t* LCD_GetDrawBuffer(void)
{
    return frame_buffer[current_buffer];
}

/**
 * @brief  交换缓冲区并刷新显示
 */
void LCD_SwapBuffers(void)
{
    /* 将当前缓冲区内容传输到LCD */
    LCD_SetWindow(0, 0, LCD_WIDTH - 1, LCD_HEIGHT - 1);
    LCD_WriteDataBuf_DMA(frame_buffer[current_buffer], LCD_WIDTH * LCD_HEIGHT);
    
    /* 切换缓冲区 */
    current_buffer = 1 - current_buffer;
}
```

### 4.4 SPI速度优化

提高SPI时钟频率可以加快数据传输。

```c
/**
 * @brief  设置SPI速度
 * @param  prescaler: 分频系数
 */
void LCD_SetSPISpeed(uint32_t prescaler)
{
    /* 修改SPI分频 */
    hspi1.Init.BaudRatePrescaler = prescaler;
    HAL_SPI_Init(&hspi1);
}

/* 使用示例 */
void LCD_Init(void)
{
    /* 初始化时使用较低速度 */
    LCD_SetSPISpeed(SPI_BAUDRATEPRESCALER_16);  // 约5MHz
    
    /* 初始化序列... */
    
    /* 初始化完成后提高速度 */
    LCD_SetSPISpeed(SPI_BAUDRATEPRESCALER_2);   // 约42MHz
}
```


## 步骤5：完整示例程序

### 5.1 LCD测试程序

```c
/**
 * @brief  LCD功能测试
 */
void LCD_Test(void)
{
    /* 初始化LCD */
    LCD_Init();
    
    /* 测试1：清屏 */
    LCD_Clear(COLOR_WHITE);
    HAL_Delay(500);
    
    /* 测试2：画点 */
    LCD_Clear(COLOR_BLACK);
    for (uint16_t i = 0; i < 100; i++) {
        uint16_t x = rand() % LCD_WIDTH;
        uint16_t y = rand() % LCD_HEIGHT;
        uint16_t color = rand() % 0xFFFF;
        LCD_DrawPixel(x, y, color);
    }
    HAL_Delay(2000);
    
    /* 测试3：画线 */
    LCD_Clear(COLOR_BLACK);
    LCD_DrawLine(0, 0, LCD_WIDTH-1, LCD_HEIGHT-1, COLOR_RED);
    LCD_DrawLine(0, LCD_HEIGHT-1, LCD_WIDTH-1, 0, COLOR_GREEN);
    LCD_DrawLine(LCD_WIDTH/2, 0, LCD_WIDTH/2, LCD_HEIGHT-1, COLOR_BLUE);
    LCD_DrawLine(0, LCD_HEIGHT/2, LCD_WIDTH-1, LCD_HEIGHT/2, COLOR_YELLOW);
    HAL_Delay(2000);
    
    /* 测试4：画矩形 */
    LCD_Clear(COLOR_BLACK);
    LCD_DrawRect(10, 10, 100, 80, COLOR_RED);
    LCD_FillRect(130, 10, 100, 80, COLOR_GREEN);
    LCD_DrawRect(10, 110, 100, 80, COLOR_BLUE);
    LCD_FillRect(130, 110, 100, 80, COLOR_YELLOW);
    HAL_Delay(2000);
    
    /* 测试5：画圆 */
    LCD_Clear(COLOR_BLACK);
    LCD_DrawCircle(60, 60, 50, COLOR_RED);
    LCD_FillCircle(180, 60, 50, COLOR_GREEN);
    LCD_DrawCircle(60, 180, 50, COLOR_BLUE);
    LCD_FillCircle(180, 180, 50, COLOR_YELLOW);
    HAL_Delay(2000);
    
    /* 测试6：显示文字 */
    LCD_Clear(COLOR_BLACK);
    LCD_DrawString(10, 10, "Hello LCD!", COLOR_WHITE, COLOR_BLACK);
    LCD_DrawString(10, 30, "ILI9341 Driver", COLOR_RED, COLOR_BLACK);
    LCD_DrawString(10, 50, "STM32F407", COLOR_GREEN, COLOR_BLACK);
    LCD_DrawNumber(10, 70, 12345, 5, COLOR_BLUE, COLOR_BLACK);
    HAL_Delay(2000);
    
    /* 测试7：颜色渐变 */
    LCD_Clear(COLOR_BLACK);
    for (uint16_t y = 0; y < LCD_HEIGHT; y++) {
        uint16_t color = (y * 31 / LCD_HEIGHT) << 11;  // 红色渐变
        LCD_DrawLine(0, y, LCD_WIDTH-1, y, color);
    }
    HAL_Delay(2000);
}

/**
 * @brief  LCD动画演示
 */
void LCD_Animation_Demo(void)
{
    LCD_Clear(COLOR_BLACK);
    
    /* 移动的圆 */
    int16_t x = 30, y = 30;
    int16_t dx = 2, dy = 2;
    uint16_t radius = 20;
    
    while (1) {
        /* 清除旧位置 */
        LCD_FillCircle(x, y, radius, COLOR_BLACK);
        
        /* 更新位置 */
        x += dx;
        y += dy;
        
        /* 边界检测 */
        if (x - radius <= 0 || x + radius >= LCD_WIDTH) {
            dx = -dx;
        }
        if (y - radius <= 0 || y + radius >= LCD_HEIGHT) {
            dy = -dy;
        }
        
        /* 绘制新位置 */
        LCD_FillCircle(x, y, radius, COLOR_RED);
        
        HAL_Delay(20);
    }
}
```

### 5.2 OLED测试程序

```c
/**
 * @brief  OLED功能测试
 */
void OLED_Test(void)
{
    /* 初始化OLED */
    OLED_Init();
    
    /* 测试1：显示文字 */
    OLED_Clear();
    OLED_DrawString(0, 0, "Hello OLED!", OLED_COLOR_WHITE);
    OLED_DrawString(0, 16, "SSD1306", OLED_COLOR_WHITE);
    OLED_DrawString(0, 32, "128x64", OLED_COLOR_WHITE);
    OLED_Display();
    HAL_Delay(2000);
    
    /* 测试2：画图形 */
    OLED_Clear();
    OLED_DrawRect(10, 10, 40, 40, OLED_COLOR_WHITE);
    OLED_FillRect(60, 10, 40, 40, OLED_COLOR_WHITE);
    OLED_Display();
    HAL_Delay(2000);
    
    /* 测试3：画圆 */
    OLED_Clear();
    OLED_DrawCircle(32, 32, 20, OLED_COLOR_WHITE);
    OLED_DrawCircle(96, 32, 20, OLED_COLOR_WHITE);
    OLED_Display();
    HAL_Delay(2000);
    
    /* 测试4：反色显示 */
    OLED_SetInvert(true);
    HAL_Delay(1000);
    OLED_SetInvert(false);
    HAL_Delay(1000);
}

/**
 * @brief  OLED滚动文字演示
 */
void OLED_Scroll_Demo(void)
{
    const char *text = "Scrolling Text Demo";
    int16_t x = OLED_WIDTH;
    
    while (1) {
        OLED_Clear();
        OLED_DrawString(x, 24, text, OLED_COLOR_WHITE);
        OLED_Display();
        
        x -= 2;
        if (x < -strlen(text) * 8) {
            x = OLED_WIDTH;
        }
        
        HAL_Delay(50);
    }
}
```

### 5.3 实时数据显示示例

```c
/**
 * @brief  传感器数据显示
 */
void Sensor_Display_Demo(void)
{
    float temperature = 0.0f;
    float humidity = 0.0f;
    uint32_t last_update = 0;
    
    LCD_Clear(COLOR_BLACK);
    
    /* 绘制界面框架 */
    LCD_DrawString(10, 10, "Sensor Monitor", COLOR_WHITE, COLOR_BLACK);
    LCD_DrawLine(0, 30, LCD_WIDTH-1, 30, COLOR_BLUE);
    
    while (1) {
        /* 每秒更新一次 */
        if (HAL_GetTick() - last_update >= 1000) {
            last_update = HAL_GetTick();
            
            /* 读取传感器数据（模拟） */
            temperature = 20.0f + (rand() % 100) / 10.0f;
            humidity = 40.0f + (rand() % 400) / 10.0f;
            
            /* 显示温度 */
            char buf[32];
            snprintf(buf, sizeof(buf), "Temp: %.1f C  ", temperature);
            LCD_DrawString(10, 50, buf, COLOR_RED, COLOR_BLACK);
            
            /* 显示湿度 */
            snprintf(buf, sizeof(buf), "Humi: %.1f %%  ", humidity);
            LCD_DrawString(10, 70, buf, COLOR_GREEN, COLOR_BLACK);
            
            /* 绘制温度条形图 */
            uint16_t bar_width = (uint16_t)((temperature - 20) * 200 / 10);
            LCD_FillRect(10, 100, 200, 20, COLOR_BLACK);
            LCD_FillRect(10, 100, bar_width, 20, COLOR_RED);
            LCD_DrawRect(10, 100, 200, 20, COLOR_WHITE);
            
            /* 绘制湿度条形图 */
            bar_width = (uint16_t)((humidity - 40) * 200 / 40);
            LCD_FillRect(10, 140, 200, 20, COLOR_BLACK);
            LCD_FillRect(10, 140, bar_width, 20, COLOR_GREEN);
            LCD_DrawRect(10, 140, 200, 20, COLOR_WHITE);
        }
        
        HAL_Delay(10);
    }
}
```


## 步骤6：故障排除

### 问题1：LCD无显示

**可能原因**：
- 硬件连接错误
- 电源电压不足
- 背光未开启
- 初始化序列错误
- SPI通信失败

**解决方法**：

1. **检查硬件连接**
```c
// 测试引脚输出
HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
HAL_Delay(100);
HAL_GPIO_WritePin(LCD_CS_PORT, LCD_CS_PIN, GPIO_PIN_SET);
// 用万用表测量引脚电平变化
```

2. **检查背光**
```c
// 强制开启背光
HAL_GPIO_WritePin(LCD_LED_PORT, LCD_LED_PIN, GPIO_PIN_SET);
```

3. **测试SPI通信**
```c
// 发送测试命令
LCD_WriteCmd(0x00);  // NOP命令
// 用逻辑分析仪查看SPI波形
```

4. **简化初始化序列**
```c
// 使用最简单的初始化
LCD_HardwareReset();
LCD_WriteCmd(0x11);  // 退出睡眠
HAL_Delay(120);
LCD_WriteCmd(0x29);  // 开启显示
```

### 问题2：显示颜色不正常

**可能原因**：
- 颜色格式设置错误
- RGB顺序错误
- 像素格式不匹配

**解决方法**：

1. **检查颜色格式**
```c
// 确认使用RGB565格式
LCD_WriteCmd(ILI9341_PIXFMT);
LCD_WriteData(0x55);  // 16位色
```

2. **调整RGB顺序**
```c
// 在MADCTL命令中设置BGR位
LCD_WriteCmd(ILI9341_MADCTL);
LCD_WriteData(0x48);  // BGR=1
// 或者
LCD_WriteData(0x40);  // BGR=0 (RGB顺序)
```

3. **测试纯色**
```c
// 显示纯红色
LCD_Clear(0xF800);  // RGB565: 11111 000000 00000
// 显示纯绿色
LCD_Clear(0x07E0);  // RGB565: 00000 111111 00000
// 显示纯蓝色
LCD_Clear(0x001F);  // RGB565: 00000 000000 11111
```

### 问题3：OLED显示模糊或闪烁

**可能原因**：
- I2C速度太快
- 对比度设置不当
- 刷新频率太高
- 电源不稳定

**解决方法**：

1. **降低I2C速度**
```c
// 在CubeMX中设置I2C速度为100kHz（标准模式）
// 或400kHz（快速模式）
```

2. **调整对比度**
```c
// 尝试不同的对比度值
OLED_SetContrast(0x7F);  // 中等对比度
OLED_SetContrast(0xFF);  // 最高对比度
```

3. **优化刷新策略**
```c
// 只在数据变化时刷新
static uint8_t last_buffer[OLED_WIDTH * OLED_HEIGHT / 8];

void OLED_Display_Smart(void)
{
    if (memcmp(oled_buffer, last_buffer, sizeof(oled_buffer)) != 0) {
        OLED_Display();
        memcpy(last_buffer, oled_buffer, sizeof(oled_buffer));
    }
}
```

### 问题4：显示速度慢

**可能原因**：
- SPI/I2C速度太慢
- 未使用DMA
- 刷新整个屏幕
- CPU主频太低

**解决方法**：

1. **提高通信速度**
```c
// SPI: 提高到最大支持速度
LCD_SetSPISpeed(SPI_BAUDRATEPRESCALER_2);  // 42MHz

// I2C: 使用快速模式
// 在CubeMX中设置为400kHz
```

2. **使用DMA传输**
```c
// 启用SPI DMA
HAL_SPI_Transmit_DMA(&hspi1, data, len);
```

3. **局部刷新**
```c
// 只刷新变化的区域
LCD_SetWindow(x, y, x+w-1, y+h-1);
// 只传输该区域的数据
```

### 问题5：显示内容错位

**可能原因**：
- 显示方向设置错误
- 坐标计算错误
- 窗口设置错误

**解决方法**：

1. **调整显示方向**
```c
// 尝试不同的方向设置
LCD_SetOrientation(LCD_ORIENTATION_PORTRAIT);
LCD_SetOrientation(LCD_ORIENTATION_LANDSCAPE);
```

2. **检查坐标范围**
```c
// 添加边界检查
if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
```

3. **验证窗口设置**
```c
// 打印窗口参数
printf("Window: (%d,%d) to (%d,%d)\n", x1, y1, x2, y2);
```


## 总结

通过本教程，你学习了：

- ✅ LCD和OLED显示器的工作原理和区别
- ✅ ILI9341 TFT LCD的完整驱动开发（SPI接口）
- ✅ SSD1306 OLED的完整驱动开发（I2C接口）
- ✅ 基本图形绘制算法的实现（点、线、矩形、圆）
- ✅ 字符和字符串显示功能的开发
- ✅ 显示缓冲区的使用和刷新机制
- ✅ 显示性能优化技术（DMA、局部刷新、双缓冲）
- ✅ 常见问题的诊断和解决方法

**关键要点**：

1. **显示器选择**：
   - LCD：色彩丰富，适合多媒体应用
   - OLED：对比度高，适合低功耗应用

2. **接口选择**：
   - SPI：速度快，适合彩色大屏
   - I2C：引脚少，适合单色小屏

3. **驱动开发**：
   - 理解控制器命令集
   - 正确配置初始化序列
   - 实现基本的读写函数

4. **图形绘制**：
   - 使用经典算法（Bresenham、中点圆）
   - 注意坐标边界检查
   - 优化绘制性能

5. **性能优化**：
   - 使用DMA传输大量数据
   - 实现局部刷新减少传输量
   - 使用双缓冲避免撕裂
   - 提高通信速度

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1：实现图片显示**
   - 使用取模软件转换图片
   - 实现BMP/JPG图片解码
   - 支持图片缩放和旋转

2. **挑战2：实现中文显示**
   - 使用字库芯片（如GT21L16S2W）
   - 或者将常用汉字字模存储到Flash
   - 实现UTF-8编码支持

3. **挑战3：实现动画效果**
   - 淡入淡出效果
   - 滑动切换效果
   - 缩放动画

4. **挑战4：实现触摸绘图**
   - 结合触摸屏驱动
   - 实现画笔工具
   - 支持不同颜色和粗细

5. **挑战5：实现视频播放**
   - 解码MJPEG视频流
   - 实现帧缓冲管理
   - 优化播放性能

## 完整代码

完整的项目代码可以在这里下载：

- **GitHub仓库**: [display-driver-example](https://github.com/embedded-platform/display-driver)
- **代码结构**:
  ```
  display-driver/
  ├── Drivers/
  │   ├── lcd_ili9341.c/h        # ILI9341驱动
  │   ├── lcd_st7789.c/h         # ST7789驱动
  │   ├── oled_ssd1306.c/h       # SSD1306驱动
  │   ├── oled_sh1106.c/h        # SH1106驱动
  │   ├── lcd_graphics.c/h       # 图形绘制库
  │   └── fonts.c/h              # 字体数据
  ├── Examples/
  │   ├── lcd_test.c             # LCD测试程序
  │   ├── oled_test.c            # OLED测试程序
  │   ├── animation_demo.c       # 动画演示
  │   └── sensor_display.c       # 传感器数据显示
  └── README.md
  ```

## 下一步

建议继续学习：

- [LVGL图形库快速入门](01-lvgl-quickstart.html) - 学习高级GUI开发
- [触摸屏驱动开发](02-touchscreen-driver.html) - 实现人机交互
- [GUI设计模式与架构](../intermediate/01-gui-design-patterns.html) - 学习GUI架构设计
- [图形性能优化技术](../intermediate/02-graphics-optimization.html) - 深入优化技术

**推荐资源**：

1. **官方文档**
   - [ILI9341数据手册](https://www.displayfuture.com/Display/datasheet/controller/ILI9341.pdf)
   - [ST7789数据手册](https://www.sitronix.com.tw/en/product/Driver/mobile_display.html)
   - [SSD1306数据手册](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf)
   - [SH1106数据手册](https://www.velleman.eu/downloads/29/infosheets/sh1106_datasheet.pdf)

2. **开发工具**
   - [Image2LCD](http://www.buydisplay.com/) - 图片转换工具
   - [PCtoLCD2002](http://www.pc2lcd.com/) - 字模提取工具
   - [LVGL Font Converter](https://lvgl.io/tools/fontconverter) - 字体转换

3. **参考项目**
   - Adafruit GFX Library
   - U8g2 Library
   - LVGL Graphics Library

4. **学习资源**
   - 图形算法教程
   - 嵌入式显示技术文章
   - LCD/OLED驱动开发视频

## 参考资料

1. **显示器技术文档**
   - ILI9341 LCD Controller Datasheet
   - ST7789 LCD Controller Datasheet
   - SSD1306 OLED Controller Datasheet
   - SH1106 OLED Controller Datasheet
   - TFT LCD Technology Overview
   - OLED Display Technology Guide

2. **通信协议文档**
   - SPI Protocol Specification
   - I2C Bus Specification
   - STM32 SPI Application Note (AN4031)
   - STM32 I2C Application Note (AN4235)

3. **图形算法**
   - Bresenham's Line Algorithm
   - Midpoint Circle Algorithm
   - Flood Fill Algorithm
   - Anti-Aliasing Techniques

4. **开发板文档**
   - STM32F407 Reference Manual
   - STM32F4 HAL Library User Manual
   - ESP32 Technical Reference Manual

5. **相关教程**
   - SPI通信协议详解
   - I2C通信协议详解
   - DMA数据传输
   - [LVGL图形库入门](01-lvgl-quickstart.html)

---

**反馈与支持**：

如果你在学习过程中遇到问题，欢迎通过以下方式获取帮助：

- 💬 在评论区留言
- 📧 发送邮件至 support@embedded-platform.com
- 🐛 在GitHub提交Issue
- 💡 在论坛发起讨论

**贡献**：

欢迎为本教程贡献代码示例、改进建议或错误修正！

---

**版权声明**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**最后更新**: 2024-01-15  
**教程版本**: 1.0  
**适用硬件**: STM32F4系列、ESP32等  
**适用显示器**: ILI9341、ST7789、SSD1306、SH1106等
