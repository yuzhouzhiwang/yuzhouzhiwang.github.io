---
title: "Modbus工业协议实战开发"
description: "深入学习Modbus RTU和Modbus TCP协议原理、主从通信机制、寄存器操作，并通过STM32和ESP32实现完整的Modbus通信系统，掌握工业自动化通信技术"
slug: "modbus-protocol-industrial-communication"

# 分类信息
domain: "通信与网络"
module: "工业协议"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Modbus
  - 工业协议
  - 工业通信
  - RS485
  - Modbus TCP
prerequisites:
  - "01-tcpip-stack"
  - "04-http-https"
related_contents: []

# 学习信息
estimated_time: 85
difficulty_score: 3

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-08"
updated_at: "2026-03-08"
version: "1.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - Modbus协议
  - 工业通信
  - Modbus RTU
  - Modbus TCP
  - RS485通信
cover_image: ""
---

# Modbus工业协议实战开发

## 学习目标

完成本教程后，你将能够：

- [ ] 理解Modbus协议的工作原理和应用场景
- [ ] 掌握Modbus RTU和Modbus TCP的区别
- [ ] 了解主从通信机制和寄存器类型
- [ ] 使用STM32实现Modbus RTU从站
- [ ] 使用ESP32实现Modbus TCP服务器
- [ ] 开发Modbus主站进行设备控制和数据采集

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解串口通信基础（UART、RS485）
- 熟悉TCP/IP网络协议
- 理解客户端-服务器架构
- 掌握C语言编程

**技能要求**：
- 能够使用STM32CubeMX配置外设
- 会使用ESP32进行网络编程
- 了解工业自动化基本概念

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| STM32F103开发板 | 1 | 用于Modbus RTU从站 | - |
| ESP32开发板 | 1 | 用于Modbus TCP服务器 | - |
| RS485转换模块 | 1 | MAX485或类似芯片 | - |
| USB转RS485模块 | 1 | 用于PC端测试 | - |
| DHT11温湿度传感器 | 1 | 可选，用于数据采集 | - |
| 继电器模块 | 1 | 可选，用于控制输出 | - |
| Micro USB数据线 | 2 | 用于供电和程序下载 | - |

### 软件准备

- **开发环境**：
  - STM32CubeIDE 或 Keil MDK
  - Arduino IDE 2.0+ 或 ESP-IDF
- **Modbus库**：
  - FreeModbus (STM32)
  - ModbusMaster (Arduino)
  - esp-modbus (ESP-IDF)
- **测试工具**：
  - Modbus Poll (主站模拟器)
  - Modbus Slave (从站模拟器)
  - QModMaster (开源工具)

### 环境配置

#### 1. 安装STM32开发环境

- 下载并安装STM32CubeIDE
- 安装STM32F1系列支持包
- 配置串口调试工具（如PuTTY、Tera Term）

#### 2. 安装ESP32开发环境

在Arduino IDE中：
- 添加ESP32开发板支持
- 安装ModbusTCP库

或使用ESP-IDF：
- 安装ESP-IDF v4.4+
- esp-modbus组件已内置

#### 3. 安装Modbus测试工具

下载Modbus Poll和Modbus Slave：
- 访问 https://www.modbustools.com/
- 下载试用版或购买完整版
- 或使用开源工具QModMaster

## Modbus协议基础

### 什么是Modbus？

Modbus是一种串行通信协议，由Modicon（现为施耐德电气）于1979年发布，是工业自动化领域应用最广泛的通信协议之一。

**核心特点**：
- **开放标准**：协议规范公开，免费使用
- **简单可靠**：协议简单，易于实现和维护
- **主从架构**：一个主站，多个从站（最多247个）
- **广泛支持**：几乎所有工业设备都支持
- **多种传输方式**：支持串口（RTU/ASCII）和以太网（TCP）

### Modbus协议变体

| 协议类型 | 传输介质 | 数据格式 | 应用场景 |
|----------|----------|----------|----------|
| Modbus RTU | RS232/RS485 | 二进制 | 现场总线，短距离通信 |
| Modbus ASCII | RS232/RS485 | ASCII字符 | 调试和简单应用 |
| Modbus TCP | 以太网 | TCP/IP封装 | 工业以太网，远程监控 |

### Modbus数据模型

Modbus定义了四种数据类型（寄存器）：

| 数据类型 | 地址范围 | 访问权限 | 功能码 | 应用 |
|----------|----------|----------|--------|------|
| 线圈（Coil） | 00001-09999 | 读/写 | 01, 05, 15 | 数字输出（继电器、LED） |
| 离散输入（Discrete Input） | 10001-19999 | 只读 | 02 | 数字输入（开关、按钮） |
| 输入寄存器（Input Register） | 30001-39999 | 只读 | 04 | 模拟输入（传感器数据） |
| 保持寄存器（Holding Register） | 40001-49999 | 读/写 | 03, 06, 16 | 配置参数、设定值 |

**注意**：实际编程中地址从0开始，上表地址为Modbus协议规范中的逻辑地址。

### 常用功能码

| 功能码 | 名称 | 说明 |
|--------|------|------|
| 01 | Read Coils | 读取线圈状态 |
| 02 | Read Discrete Inputs | 读取离散输入状态 |
| 03 | Read Holding Registers | 读取保持寄存器 |
| 04 | Read Input Registers | 读取输入寄存器 |
| 05 | Write Single Coil | 写单个线圈 |
| 06 | Write Single Register | 写单个寄存器 |
| 15 | Write Multiple Coils | 写多个线圈 |
| 16 | Write Multiple Registers | 写多个寄存器 |

### Modbus RTU帧格式

```text
[从站地址][功能码][数据][CRC校验]
  1字节    1字节   N字节   2字节
```

**示例**：读取从站1的保持寄存器40001-40002（地址0-1）
```text
请求: 01 03 00 00 00 02 C4 0B
      |  |  |     |     |
      |  |  |     |     CRC校验
      |  |  |     读取2个寄存器
      |  |  起始地址0x0000
      |  功能码03（读保持寄存器）
      从站地址1

响应: 01 03 04 00 64 00 C8 FA 8D
      |  |  |  |           |
      |  |  |  数据值      CRC校验
      |  |  字节数4
      |  功能码03
      从站地址1
```

### Modbus TCP帧格式

```text
[MBAP报头][功能码][数据]
  7字节     1字节   N字节

MBAP报头:
[事务ID][协议ID][长度][单元ID]
 2字节   2字节   2字节  1字节
```

**示例**：读取保持寄存器
```text
请求: 00 01 00 00 00 06 01 03 00 00 00 02
      |     |     |     |  |  |     |
      |     |     |     |  |  |     读取2个寄存器
      |     |     |     |  |  起始地址
      |     |     |     |  功能码03
      |     |     |     单元ID
      |     |     后续字节数
      |     协议ID(0x0000)
      事务ID

响应: 00 01 00 00 00 07 01 03 04 00 64 00 C8
      |     |     |     |  |  |  数据值
      |     |     |     |  |  字节数
      |     |     |     |  功能码
      |     |     |     单元ID
      |     |     后续字节数
      |     协议ID
      事务ID
```

## 步骤1：STM32 Modbus RTU从站实现

### 1.1 硬件连接

#### RS485电路连接

| STM32引脚 | RS485模块 | 说明 |
|-----------|-----------|------|
| PA9 (TX) | DI | 发送数据 |
| PA10 (RX) | RO | 接收数据 |
| PA8 | DE/RE | 方向控制 |
| 3.3V | VCC | 电源 |
| GND | GND | 地 |

**RS485总线连接**：
- A端子连接所有设备的A端
- B端子连接所有设备的B端
- 总线两端需要120Ω终端电阻

### 1.2 STM32CubeMX配置

#### 配置UART1

1. 打开STM32CubeMX，选择STM32F103C8T6
2. 配置UART1：
   - Mode: Asynchronous
   - Baud Rate: 9600
   - Word Length: 8 Bits
   - Parity: None
   - Stop Bits: 1
3. 配置GPIO PA8为输出（RS485方向控制）
4. 生成代码

### 1.3 集成FreeModbus库

#### 下载FreeModbus

```bash
git clone https://github.com/armink/FreeModbus_Slave-Master-RTT-STM32.git
```

#### 添加源文件到项目

将以下文件添加到项目：
- `modbus/rtu/mbrtu.c`
- `modbus/functions/mbfunccoils.c`
- `modbus/functions/mbfuncdisc.c`
- `modbus/functions/mbfuncholding.c`
- `modbus/functions/mbfuncinput.c`
- `modbus/functions/mbutils.c`
- `modbus/mb.c`
- `port/portevent.c`
- `port/portserial.c`
- `port/porttimer.c`

### 1.4 移植代码

#### 配置mbconfig.h

```c
/* ----------------------- Defines ------------------------------------------*/
#define MB_RTU_ENABLED                  (1)     // 启用RTU模式
#define MB_ASCII_ENABLED                (0)     // 禁用ASCII模式
#define MB_TCP_ENABLED                  (0)     // 禁用TCP模式

#define MB_SLAVE_RTU_ENABLED            (1)     // 启用从站模式
#define MB_SLAVE_ASCII_ENABLED          (0)
#define MB_MASTER_RTU_ENABLED           (0)     // 禁用主站模式
#define MB_MASTER_ASCII_ENABLED         (0)

#define MB_FUNC_READ_COILS_ENABLED      (1)     // 功能码01
#define MB_FUNC_READ_DISCRETE_INPUTS_ENABLED (1) // 功能码02
#define MB_FUNC_READ_HOLDING_ENABLED    (1)     // 功能码03
#define MB_FUNC_READ_INPUT_ENABLED      (1)     // 功能码04
#define MB_FUNC_WRITE_COIL_ENABLED      (1)     // 功能码05
#define MB_FUNC_WRITE_SINGLE_REGISTER_ENABLED (1) // 功能码06
#define MB_FUNC_WRITE_MULTIPLE_COILS_ENABLED (1) // 功能码15
#define MB_FUNC_WRITE_MULTIPLE_REGISTERS_ENABLED (1) // 功能码16
```

#### 实现串口发送接收

在`portserial.c`中实现：

```c
#include "usart.h"

// RS485方向控制引脚
#define RS485_DE_PIN    GPIO_PIN_8
#define RS485_DE_PORT   GPIOA

// 设置为发送模式
#define RS485_TX_EN()   HAL_GPIO_WritePin(RS485_DE_PORT, RS485_DE_PIN, GPIO_PIN_SET)
// 设置为接收模式
#define RS485_RX_EN()   HAL_GPIO_WritePin(RS485_DE_PORT, RS485_DE_PIN, GPIO_PIN_RESET)

BOOL xMBPortSerialInit(UCHAR ucPORT, ULONG ulBaudRate, UCHAR ucDataBits, eMBParity eParity)
{
    // UART已在CubeMX中配置，这里只需要启用接收中断
    HAL_UART_Receive_IT(&huart1, &ucRxByte, 1);
    RS485_RX_EN();  // 默认接收模式
    return TRUE;
}

void vMBPortSerialEnable(BOOL xRxEnable, BOOL xTxEnable)
{
    if (xRxEnable) {
        RS485_RX_EN();
        HAL_UART_Receive_IT(&huart1, &ucRxByte, 1);
    } else {
        HAL_UART_AbortReceive_IT(&huart1);
    }
    
    if (xTxEnable) {
        RS485_TX_EN();
    }
}

BOOL xMBPortSerialPutByte(CHAR ucByte)
{
    HAL_UART_Transmit(&huart1, (uint8_t*)&ucByte, 1, 100);
    return TRUE;
}

BOOL xMBPortSerialGetByte(CHAR * pucByte)
{
    *pucByte = ucRxByte;
    return TRUE;
}

// UART接收中断回调
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        pxMBFrameCBByteReceived();  // 通知Modbus有新字节
        HAL_UART_Receive_IT(&huart1, &ucRxByte, 1);
    }
}
```

#### 实现定时器

在`porttimer.c`中实现：

```c
#include "tim.h"

BOOL xMBPortTimersInit(USHORT usTim1Timerout50us)
{
    // 使用TIM2，配置为50us中断
    // 计算ARR值: (72MHz / 预分频) * 50us - 1
    __HAL_TIM_SET_AUTORELOAD(&htim2, usTim1Timerout50us - 1);
    return TRUE;
}

void vMBPortTimersEnable(void)
{
    HAL_TIM_Base_Start_IT(&htim2);
}

void vMBPortTimersDisable(void)
{
    HAL_TIM_Base_Stop_IT(&htim2);
}

// 定时器中断回调
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2) {
        pxMBPortCBTimerExpired();  // 通知Modbus定时器超时
    }
}
```

### 1.5 实现寄存器回调函数

#### 定义寄存器数据

```c
// 保持寄存器（可读写）
#define REG_HOLDING_START   0
#define REG_HOLDING_NREGS   10
static USHORT usRegHoldingBuf[REG_HOLDING_NREGS] = {
    100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
};

// 输入寄存器（只读）
#define REG_INPUT_START     0
#define REG_INPUT_NREGS     5
static USHORT usRegInputBuf[REG_INPUT_NREGS] = {
    0, 0, 0, 0, 0  // 将存储传感器数据
};

// 线圈（可读写）
#define REG_COILS_START     0
#define REG_COILS_SIZE      8
static UCHAR ucRegCoilsBuf[REG_COILS_SIZE / 8] = {0};

// 离散输入（只读）
#define REG_DISCRETE_START  0
#define REG_DISCRETE_SIZE   8
static UCHAR ucRegDiscreteBuf[REG_DISCRETE_SIZE / 8] = {0};
```

#### 实现保持寄存器回调

```c
eMBErrorCode eMBRegHoldingCB(UCHAR * pucRegBuffer, USHORT usAddress, 
                              USHORT usNRegs, eMBRegisterMode eMode)
{
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex;
    
    // 检查地址范围
    if ((usAddress >= REG_HOLDING_START) &&
        (usAddress + usNRegs <= REG_HOLDING_START + REG_HOLDING_NREGS)) {
        
        iRegIndex = usAddress - REG_HOLDING_START;
        
        switch (eMode) {
            case MB_REG_READ:
                // 读取寄存器
                while (usNRegs > 0) {
                    *pucRegBuffer++ = (UCHAR)(usRegHoldingBuf[iRegIndex] >> 8);
                    *pucRegBuffer++ = (UCHAR)(usRegHoldingBuf[iRegIndex] & 0xFF);
                    iRegIndex++;
                    usNRegs--;
                }
                break;
                
            case MB_REG_WRITE:
                // 写入寄存器
                while (usNRegs > 0) {
                    usRegHoldingBuf[iRegIndex] = *pucRegBuffer++ << 8;
                    usRegHoldingBuf[iRegIndex] |= *pucRegBuffer++;
                    iRegIndex++;
                    usNRegs--;
                }
                break;
        }
    } else {
        eStatus = MB_ENOREG;
    }
    
    return eStatus;
}
```

#### 实现输入寄存器回调

```c
eMBErrorCode eMBRegInputCB(UCHAR * pucRegBuffer, USHORT usAddress, USHORT usNRegs)
{
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex;
    
    if ((usAddress >= REG_INPUT_START) &&
        (usAddress + usNRegs <= REG_INPUT_START + REG_INPUT_NREGS)) {
        
        iRegIndex = usAddress - REG_INPUT_START;
        
        while (usNRegs > 0) {
            *pucRegBuffer++ = (UCHAR)(usRegInputBuf[iRegIndex] >> 8);
            *pucRegBuffer++ = (UCHAR)(usRegInputBuf[iRegIndex] & 0xFF);
            iRegIndex++;
            usNRegs--;
        }
    } else {
        eStatus = MB_ENOREG;
    }
    
    return eStatus;
}
```

#### 实现线圈回调

```c
eMBErrorCode eMBRegCoilsCB(UCHAR * pucRegBuffer, USHORT usAddress, 
                            USHORT usNCoils, eMBRegisterMode eMode)
{
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iNCoils = usNCoils;
    USHORT usBitOffset;
    
    if ((usAddress >= REG_COILS_START) &&
        (usAddress + usNCoils <= REG_COILS_START + REG_COILS_SIZE)) {
        
        usBitOffset = usAddress - REG_COILS_START;
        
        switch (eMode) {
            case MB_REG_READ:
                while (iNCoils > 0) {
                    *pucRegBuffer++ = xMBUtilGetBits(ucRegCoilsBuf, usBitOffset,
                        (UCHAR)(iNCoils > 8 ? 8 : iNCoils));
                    iNCoils -= (iNCoils > 8) ? 8 : iNCoils;
                    usBitOffset += 8;
                }
                break;
                
            case MB_REG_WRITE:
                while (iNCoils > 0) {
                    xMBUtilSetBits(ucRegCoilsBuf, usBitOffset,
                        (UCHAR)(iNCoils > 8 ? 8 : iNCoils), *pucRegBuffer++);
                    iNCoils -= (iNCoils > 8) ? 8 : iNCoils;
                    usBitOffset += 8;
                }
                break;
        }
    } else {
        eStatus = MB_ENOREG;
    }
    
    return eStatus;
}
```

### 1.6 主程序实现

```c
#include "mb.h"

// Modbus从站地址
#define MB_SLAVE_ADDR   1

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();
    MX_TIM2_Init();
    
    // 初始化Modbus RTU从站
    // 参数: 从站地址, 串口号, 波特率, 校验位
    eMBInit(MB_RTU, MB_SLAVE_ADDR, 0, 9600, MB_PAR_NONE);
    
    // 启用Modbus
    eMBEnable();
    
    while (1)
    {
        // Modbus轮询处理
        eMBPoll();
        
        // 更新传感器数据到输入寄存器
        // 这里使用模拟数据，实际应用中读取真实传感器
        usRegInputBuf[0] = 250;  // 温度 * 10 (25.0°C)
        usRegInputBuf[1] = 650;  // 湿度 * 10 (65.0%)
        usRegInputBuf[2] = HAL_GetTick() / 1000;  // 运行时间（秒）
        
        // 根据线圈状态控制LED
        if (xMBUtilGetBits(ucRegCoilsBuf, 0, 1)) {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);  // LED亮
        } else {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);    // LED灭
        }
        
        HAL_Delay(10);
    }
}
```

**代码说明**：
- `eMBInit()`：初始化Modbus协议栈
- `eMBEnable()`：启用Modbus通信
- `eMBPoll()`：必须在主循环中定期调用，处理Modbus通信
- 定期更新输入寄存器的传感器数据
- 根据线圈状态控制输出

## 步骤2：使用Modbus Poll测试

### 2.1 配置Modbus Poll

1. 打开Modbus Poll软件
2. 创建新连接：
   - Connection -> Connect
   - Connection: Serial Port
   - Port: 选择USB转RS485的COM口
   - Baud: 9600
   - Parity: None
   - Data Bits: 8
   - Stop Bits: 1
3. 配置从站地址：
   - Setup -> Read/Write Definition
   - Slave ID: 1
   - Function: 03 (Read Holding Registers)
   - Address: 0
   - Quantity: 10

### 2.2 测试读取保持寄存器

1. 点击"Poll"按钮开始轮询
2. 应该看到10个寄存器的值：100, 200, 300...1000
3. 双击某个寄存器值进行修改
4. 观察STM32是否接收到新值

### 2.3 测试读取输入寄存器

1. Setup -> Read/Write Definition
2. Function: 04 (Read Input Registers)
3. Address: 0
4. Quantity: 3
5. 应该看到温度、湿度和运行时间数据

### 2.4 测试线圈控制

1. Setup -> Read/Write Definition
2. Function: 01 (Read Coils)
3. Address: 0
4. Quantity: 8
5. 双击线圈0，设置为1
6. 观察STM32的LED是否点亮

**预期结果**：
- 能够成功读取所有类型的寄存器
- 能够写入保持寄存器和线圈
- LED根据线圈状态变化

## 步骤3：ESP32 Modbus TCP服务器

### 3.1 Arduino实现

#### 安装ModbusTCP库

在Arduino IDE中：
- 工具 -> 管理库
- 搜索"ModbusTCP"
- 安装"ModbusTCP-ESP32"

#### 基础代码框架

```c
#include <WiFi.h>
#include <ModbusTCP.h>

// WiFi配置
const char* ssid = "你的WiFi名称";
const char* password = "你的WiFi密码";

// Modbus TCP服务器
ModbusTCP mb;

// 寄存器定义
#define COIL_START      0
#define COIL_COUNT      10
#define HREG_START      0
#define HREG_COUNT      10
#define IREG_START      0
#define IREG_COUNT      5

void setup() {
    Serial.begin(115200);
    
    // 连接WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    
    // 启动Modbus TCP服务器
    mb.server();
    
    // 添加寄存器
    for (int i = 0; i < HREG_COUNT; i++) {
        mb.addHreg(HREG_START + i, i * 100);
    }
    for (int i = 0; i < IREG_COUNT; i++) {
        mb.addIreg(IREG_START + i, 0);
    }
    for (int i = 0; i < COIL_COUNT; i++) {
        mb.addCoil(COIL_START + i, false);
    }
    
    Serial.println("Modbus TCP服务器已启动");
}

void loop() {
    // 处理Modbus请求
    mb.task();
    
    // 更新传感器数据到输入寄存器
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 1000) {
        lastUpdate = millis();
        
        // 模拟传感器数据
        float temperature = 20.0 + random(0, 100) / 10.0;
        float humidity = 50.0 + random(0, 300) / 10.0;
        
        mb.Ireg(IREG_START + 0, (uint16_t)(temperature * 10));
        mb.Ireg(IREG_START + 1, (uint16_t)(humidity * 10));
        mb.Ireg(IREG_START + 2, millis() / 1000);
    }
    
    // 根据线圈状态控制LED
    if (mb.Coil(COIL_START)) {
        digitalWrite(LED_BUILTIN, HIGH);
    } else {
        digitalWrite(LED_BUILTIN, LOW);
    }
    
    delay(10);
}
```

**代码说明**：
- `mb.server()`：启动Modbus TCP服务器（默认端口502）
- `mb.addHreg()`：添加保持寄存器
- `mb.addIreg()`：添加输入寄存器
- `mb.addCoil()`：添加线圈
- `mb.task()`：处理Modbus请求，必须在loop中调用
- `mb.Ireg()`：读写输入寄存器
- `mb.Coil()`：读写线圈

### 3.2 ESP-IDF实现

#### 配置menuconfig

```bash
idf.py menuconfig
```

在Component config -> Modbus configuration中：
- 启用Modbus TCP
- 配置最大连接数
- 配置端口号（默认502）

#### 主程序代码

```c
#include "esp_modbus_slave.h"
#include "mbcontroller.h"

// Modbus寄存器映射
#define MB_REG_HOLDING_START    0
#define MB_REG_HOLDING_SIZE     10
#define MB_REG_INPUT_START      0
#define MB_REG_INPUT_SIZE       5
#define MB_REG_COILS_START      0
#define MB_REG_COILS_SIZE       10

// 寄存器数据
static uint16_t holding_reg_area[MB_REG_HOLDING_SIZE] = {
    100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
};
static uint16_t input_reg_area[MB_REG_INPUT_SIZE] = {0};
static uint8_t coils_area[MB_REG_COILS_SIZE / 8 + 1] = {0};

// Modbus寄存器描述符
static const mb_register_area_descriptor_t reg_area[] = {
    {
        MB_PARAM_HOLDING,
        MB_REG_HOLDING_START,
        MB_REG_HOLDING_SIZE,
        (void*)holding_reg_area
    },
    {
        MB_PARAM_INPUT,
        MB_REG_INPUT_START,
        MB_REG_INPUT_SIZE,
        (void*)input_reg_area
    },
    {
        MB_PARAM_COIL,
        MB_REG_COILS_START,
        MB_REG_COILS_SIZE,
        (void*)coils_area
    }
};

void modbus_tcp_slave_init(void)
{
    mb_communication_info_t comm_info = {
        .ip_port = 502,
        .ip_addr_type = MB_IPV4,
        .ip_mode = MB_MODE_TCP,
        .ip_addr = NULL,
        .ip_netif_ptr = NULL
    };
    
    // 初始化Modbus控制器
    ESP_ERROR_CHECK(mbc_slave_init_tcp(&comm_info));
    
    // 设置寄存器区域
    ESP_ERROR_CHECK(mbc_slave_set_descriptor(reg_area, 
        sizeof(reg_area) / sizeof(reg_area[0])));
    
    // 启动Modbus
    ESP_ERROR_CHECK(mbc_slave_start());
    
    ESP_LOGI(TAG, "Modbus TCP从站已启动");
}

void app_main(void)
{
    // 初始化WiFi
    wifi_init_sta();
    
    // 初始化Modbus
    modbus_tcp_slave_init();
    
    while (1) {
        // 更新传感器数据
        input_reg_area[0] = 250;  // 温度
        input_reg_area[1] = 650;  // 湿度
        input_reg_area[2] = esp_timer_get_time() / 1000000;  // 运行时间
        
        // 检查寄存器变化
        mb_event_group_t event = mbc_slave_check_event(MB_READ_WRITE_MASK);
        if (event & MB_EVENT_HOLDING_REG_WR) {
            ESP_LOGI(TAG, "保持寄存器被写入");
        }
        if (event & MB_EVENT_COILS_WR) {
            ESP_LOGI(TAG, "线圈被写入");
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

## 步骤4：Modbus TCP客户端测试

### 4.1 使用Modbus Poll测试

1. 打开Modbus Poll
2. Connection -> Connect
3. Connection: Modbus TCP/IP
4. IP Address: ESP32的IP地址
5. Port: 502
6. Slave ID: 1（或255表示任意）
7. 配置读取功能和地址
8. 点击Poll开始测试

### 4.2 使用Python测试

安装pymodbus库：
```bash
pip install pymodbus
```

#### 读取寄存器

```python
from pymodbus.client import ModbusTcpClient

# 连接到Modbus TCP服务器
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# 读取保持寄存器
result = client.read_holding_registers(address=0, count=10, slave=1)
if not result.isError():
    print("保持寄存器:", result.registers)

# 读取输入寄存器
result = client.read_input_registers(address=0, count=5, slave=1)
if not result.isError():
    print("输入寄存器:", result.registers)
    print(f"温度: {result.registers[0] / 10.0}°C")
    print(f"湿度: {result.registers[1] / 10.0}%")

# 读取线圈
result = client.read_coils(address=0, count=10, slave=1)
if not result.isError():
    print("线圈状态:", result.bits)

client.close()
```

#### 写入寄存器

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# 写单个保持寄存器
client.write_register(address=0, value=999, slave=1)

# 写多个保持寄存器
client.write_registers(address=0, values=[111, 222, 333], slave=1)

# 写单个线圈
client.write_coil(address=0, value=True, slave=1)

# 写多个线圈
client.write_coils(address=0, values=[True, False, True, False], slave=1)

client.close()
```

## 步骤5：Modbus主站实现

### 5.1 Arduino Modbus主站

#### 安装ModbusMaster库

```bash
# 在Arduino IDE中安装ModbusMaster库
```

#### 主站代码

```c
#include <ModbusMaster.h>

// Modbus主站对象
ModbusMaster node;

// RS485方向控制
#define MAX485_DE   4
#define MAX485_RE   5

void preTransmission() {
    digitalWrite(MAX485_RE, HIGH);
    digitalWrite(MAX485_DE, HIGH);
}

void postTransmission() {
    digitalWrite(MAX485_RE, LOW);
    digitalWrite(MAX485_DE, LOW);
}

void setup() {
    Serial.begin(115200);
    Serial2.begin(9600);  // Modbus串口
    
    pinMode(MAX485_RE, OUTPUT);
    pinMode(MAX485_DE, OUTPUT);
    digitalWrite(MAX485_RE, LOW);
    digitalWrite(MAX485_DE, LOW);
    
    // 初始化Modbus主站
    node.begin(1, Serial2);  // 从站地址1
    node.preTransmission(preTransmission);
    node.postTransmission(postTransmission);
    
    Serial.println("Modbus主站已启动");
}

void loop() {
    uint8_t result;
    uint16_t data[10];
    
    // 读取保持寄存器
    result = node.readHoldingRegisters(0, 10);
    if (result == node.ku8MBSuccess) {
        Serial.println("保持寄存器:");
        for (int i = 0; i < 10; i++) {
            data[i] = node.getResponseBuffer(i);
            Serial.printf("  [%d] = %d\n", i, data[i]);
        }
    } else {
        Serial.printf("读取失败，错误码: 0x%02X\n", result);
    }
    
    delay(1000);
    
    // 读取输入寄存器
    result = node.readInputRegisters(0, 3);
    if (result == node.ku8MBSuccess) {
        float temp = node.getResponseBuffer(0) / 10.0;
        float humi = node.getResponseBuffer(1) / 10.0;
        uint16_t time = node.getResponseBuffer(2);
        Serial.printf("温度: %.1f°C, 湿度: %.1f%%, 运行时间: %ds\n", 
                      temp, humi, time);
    }
    
    delay(1000);
    
    // 写单个寄存器
    result = node.writeSingleRegister(0, 1234);
    if (result == node.ku8MBSuccess) {
        Serial.println("写入成功");
    }
    
    delay(1000);
    
    // 控制线圈
    static bool ledState = false;
    ledState = !ledState;
    result = node.writeSingleCoil(0, ledState);
    if (result == node.ku8MBSuccess) {
        Serial.printf("LED状态: %s\n", ledState ? "ON" : "OFF");
    }
    
    delay(2000);
}
```

### 5.2 ESP32 Modbus TCP主站

```c
#include <WiFi.h>
#include <ModbusTCP.h>

const char* ssid = "你的WiFi名称";
const char* password = "你的WiFi密码";

// Modbus TCP客户端
ModbusTCP mb;

// 从站IP地址
IPAddress remote(192, 168, 1, 100);

void setup() {
    Serial.begin(115200);
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi连接成功");
    
    // 连接到Modbus TCP从站
    mb.client();
    
    Serial.println("Modbus TCP主站已启动");
}

void loop() {
    // 连接到从站
    if (!mb.isConnected(remote)) {
        mb.connect(remote);
        Serial.println("连接到从站...");
        delay(1000);
        return;
    }
    
    // 读取保持寄存器
    if (mb.readHreg(remote, 0, 10)) {
        Serial.println("保持寄存器:");
        for (int i = 0; i < 10; i++) {
            Serial.printf("  [%d] = %d\n", i, mb.Hreg(i));
        }
    }
    
    delay(1000);
    
    // 读取输入寄存器
    if (mb.readIreg(remote, 0, 3)) {
        float temp = mb.Ireg(0) / 10.0;
        float humi = mb.Ireg(1) / 10.0;
        uint16_t time = mb.Ireg(2);
        Serial.printf("温度: %.1f°C, 湿度: %.1f%%, 运行时间: %ds\n", 
                      temp, humi, time);
    }
    
    delay(1000);
    
    // 写入寄存器
    mb.writeHreg(remote, 0, 5678);
    
    delay(1000);
    
    // 控制线圈
    static bool ledState = false;
    ledState = !ledState;
    mb.writeCoil(remote, 0, ledState);
    Serial.printf("LED状态: %s\n", ledState ? "ON" : "OFF");
    
    delay(2000);
}
```

## 步骤6：实际应用案例

### 6.1 多传感器数据采集系统

#### 系统架构

```text
[传感器1] --\
[传感器2] ----> [STM32 Modbus从站] --RS485--> [ESP32 Modbus主站] --WiFi--> [云平台]
[传感器3] --/
```

#### STM32从站代码（多传感器）

```c
#include "dht11.h"
#include "adc.h"

// 寄存器映射
// 输入寄存器0-9: 传感器数据
// 保持寄存器0-9: 配置参数
// 线圈0-7: 控制输出

void updateSensorData(void)
{
    // 读取DHT11温湿度
    DHT11_Data_TypeDef dht11_data;
    DHT11_Read_TempAndHumidity(&dht11_data);
    usRegInputBuf[0] = dht11_data.temp_int * 10 + dht11_data.temp_deci;
    usRegInputBuf[1] = dht11_data.humi_int * 10 + dht11_data.humi_deci;
    
    // 读取ADC光照传感器
    uint16_t adc_value = HAL_ADC_GetValue(&hadc1);
    usRegInputBuf[2] = adc_value;
    
    // 读取土壤湿度传感器
    uint16_t soil_moisture = HAL_ADC_GetValue(&hadc2);
    usRegInputBuf[3] = soil_moisture;
    
    // 系统状态
    usRegInputBuf[4] = HAL_GetTick() / 1000;  // 运行时间
    usRegInputBuf[5] = 1;  // 设备在线标志
}

void controlOutputs(void)
{
    // 根据线圈状态控制继电器
    if (xMBUtilGetBits(ucRegCoilsBuf, 0, 1)) {
        HAL_GPIO_WritePin(RELAY1_GPIO_Port, RELAY1_Pin, GPIO_PIN_SET);
    } else {
        HAL_GPIO_WritePin(RELAY1_GPIO_Port, RELAY1_Pin, GPIO_PIN_RESET);
    }
    
    if (xMBUtilGetBits(ucRegCoilsBuf, 1, 1)) {
        HAL_GPIO_WritePin(RELAY2_GPIO_Port, RELAY2_Pin, GPIO_PIN_SET);
    } else {
        HAL_GPIO_WritePin(RELAY2_GPIO_Port, RELAY2_Pin, GPIO_PIN_RESET);
    }
}

int main(void)
{
    // ... 初始化代码 ...
    
    while (1)
    {
        eMBPoll();
        updateSensorData();
        controlOutputs();
        HAL_Delay(100);
    }
}
```

### 6.2 ESP32网关（Modbus RTU转Modbus TCP）

```c
#include <WiFi.h>
#include <ModbusTCP.h>
#include <ModbusMaster.h>

// WiFi配置
const char* ssid = "你的WiFi名称";
const char* password = "你的WiFi密码";

// Modbus TCP服务器
ModbusTCP mbTCP;

// Modbus RTU主站
ModbusMaster mbRTU;

// RS485控制
#define MAX485_DE   4
#define MAX485_RE   5

void preTransmission() {
    digitalWrite(MAX485_RE, HIGH);
    digitalWrite(MAX485_DE, HIGH);
}

void postTransmission() {
    digitalWrite(MAX485_RE, LOW);
    digitalWrite(MAX485_DE, LOW);
}

void setup() {
    Serial.begin(115200);
    Serial2.begin(9600);  // Modbus RTU
    
    // RS485控制引脚
    pinMode(MAX485_RE, OUTPUT);
    pinMode(MAX485_DE, OUTPUT);
    digitalWrite(MAX485_RE, LOW);
    digitalWrite(MAX485_DE, LOW);
    
    // 连接WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    
    // 初始化Modbus TCP服务器
    mbTCP.server();
    for (int i = 0; i < 20; i++) {
        mbTCP.addHreg(i, 0);
        mbTCP.addIreg(i, 0);
    }
    
    // 初始化Modbus RTU主站
    mbRTU.begin(1, Serial2);  // 从站地址1
    mbRTU.preTransmission(preTransmission);
    mbRTU.postTransmission(postTransmission);
    
    Serial.println("Modbus网关已启动");
}

void loop() {
    // 处理Modbus TCP请求
    mbTCP.task();
    
    // 定期从RTU从站读取数据
    static unsigned long lastRead = 0;
    if (millis() - lastRead > 1000) {
        lastRead = millis();
        
        // 读取RTU从站的输入寄存器
        uint8_t result = mbRTU.readInputRegisters(0, 10);
        if (result == mbRTU.ku8MBSuccess) {
            // 将数据复制到TCP服务器的输入寄存器
            for (int i = 0; i < 10; i++) {
                mbTCP.Ireg(i, mbRTU.getResponseBuffer(i));
            }
        }
        
        // 读取RTU从站的保持寄存器
        result = mbRTU.readHoldingRegisters(0, 10);
        if (result == mbRTU.ku8MBSuccess) {
            // 将数据复制到TCP服务器的保持寄存器
            for (int i = 0; i < 10; i++) {
                mbTCP.Hreg(i, mbRTU.getResponseBuffer(i));
            }
        }
    }
    
    delay(10);
}
```

**网关功能**：
- 接收Modbus TCP请求
- 转发到Modbus RTU从站
- 将RTU从站数据映射到TCP服务器
- 实现协议转换和数据缓存

## 故障排除

### 问题1：Modbus RTU通信失败

**可能原因**：
- RS485接线错误（A/B反接）
- 波特率不匹配
- 从站地址错误
- 缺少终端电阻
- 方向控制引脚配置错误

**解决方法**：
1. 检查RS485接线，确保A-A、B-B连接
2. 确认主从站波特率一致
3. 验证从站地址设置
4. 在总线两端添加120Ω终端电阻
5. 检查DE/RE引脚控制逻辑

### 问题2：CRC校验错误

**可能原因**：
- 数据传输错误
- 波特率不匹配
- 电磁干扰
- 线缆质量差

**解决方法**：
1. 降低波特率（如从115200降到9600）
2. 使用屏蔽双绞线
3. 缩短通信距离
4. 添加滤波电容

### 问题3：Modbus TCP连接超时

**可能原因**：
- IP地址错误
- 端口被占用
- 防火墙阻止
- 网络不通

**解决方法**：
1. ping测试网络连通性
2. 确认端口502未被占用
3. 关闭防火墙或添加例外
4. 检查路由器设置

### 问题4：寄存器读写失败

**可能原因**：
- 地址超出范围
- 功能码不支持
- 数据类型错误
- 权限不足

**解决方法**：
1. 检查寄存器地址范围
2. 确认从站支持该功能码
3. 验证数据格式（大小端）
4. 检查读写权限设置

### 问题5：多从站冲突

**可能原因**：
- 从站地址重复
- 响应时间过长
- 总线负载过重

**解决方法**：
1. 确保每个从站地址唯一
2. 增加主站轮询间隔
3. 减少单次读取的寄存器数量
4. 优化从站响应速度

## 总结

通过本教程，你学习了：

- ✅ Modbus协议的基本原理和数据模型
- ✅ Modbus RTU和Modbus TCP的区别和应用
- ✅ 主从通信机制和寄存器操作
- ✅ STM32 Modbus RTU从站的完整实现
- ✅ ESP32 Modbus TCP服务器的开发
- ✅ Modbus主站的编程方法
- ✅ 协议转换网关的实现

**关键要点**：
- Modbus是工业自动化领域最广泛使用的通信协议
- RTU适合现场总线，TCP适合以太网环境
- 主从架构简单可靠，易于实现
- 四种寄存器类型满足不同应用需求
- CRC校验确保数据传输可靠性

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现Modbus ASCII模式通信
2. **挑战2**：添加多从站轮询功能
3. **挑战3**：实现Modbus异常响应处理
4. **挑战4**：开发Web界面监控Modbus设备
5. **挑战5**：实现Modbus数据记录和分析

## 完整代码

完整的项目代码可以在GitHub上找到：

```text
GitHub仓库: https://github.com/embedded-knowledge/modbus-tutorial
```

项目包含：
- STM32 Modbus RTU从站完整代码
- ESP32 Modbus TCP服务器代码
- Modbus主站示例代码
- 协议转换网关代码
- Python测试脚本

## 下一步

建议继续学习：

- CAN总线协议应用 - 学习汽车和工业总线
- OPC UA工业互联协议 - 学习现代工业通信
- MQTT协议应用开发 - 学习物联网通信
- Profibus/Profinet - 学习西门子工业协议

## 参考资料

1. Modbus协议规范 - https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
2. Modbus over Serial Line规范 - https://modbus.org/docs/Modbus_over_serial_line_V1_02.pdf
3. FreeModbus库文档 - https://github.com/armink/FreeModbus_Slave-Master-RTT-STM32
4. ESP-MQTT组件文档 - https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/protocols/modbus.html
5. ModbusMaster库 - https://github.com/4-20ma/ModbusMaster
6. pymodbus文档 - https://pymodbus.readthedocs.io/

## 常见Modbus术语

- **Master（主站）**：发起通信请求的设备
- **Slave（从站）**：响应主站请求的设备
- **RTU**：Remote Terminal Unit，远程终端单元模式
- **ASCII**：American Standard Code for Information Interchange，ASCII模式
- **TCP**：Transmission Control Protocol，基于TCP/IP的Modbus
- **Coil（线圈）**：可读写的单bit数据，用于数字输出
- **Discrete Input（离散输入）**：只读的单bit数据，用于数字输入
- **Holding Register（保持寄存器）**：可读写的16bit数据
- **Input Register（输入寄存器）**：只读的16bit数据
- **Function Code（功能码）**：指定操作类型的代码
- **CRC**：Cyclic Redundancy Check，循环冗余校验
- **MBAP**：Modbus Application Protocol，Modbus应用协议头

## Modbus功能码速查表

| 功能码 | 名称 | 操作 | 数据类型 |
|--------|------|------|----------|
| 01 | Read Coils | 读 | 线圈 |
| 02 | Read Discrete Inputs | 读 | 离散输入 |
| 03 | Read Holding Registers | 读 | 保持寄存器 |
| 04 | Read Input Registers | 读 | 输入寄存器 |
| 05 | Write Single Coil | 写 | 单个线圈 |
| 06 | Write Single Register | 写 | 单个保持寄存器 |
| 15 | Write Multiple Coils | 写 | 多个线圈 |
| 16 | Write Multiple Registers | 写 | 多个保持寄存器 |
| 23 | Read/Write Multiple Registers | 读写 | 保持寄存器 |

## 异常码说明

| 异常码 | 名称 | 说明 |
|--------|------|------|
| 01 | Illegal Function | 不支持的功能码 |
| 02 | Illegal Data Address | 非法的数据地址 |
| 03 | Illegal Data Value | 非法的数据值 |
| 04 | Slave Device Failure | 从站设备故障 |
| 05 | Acknowledge | 确认（需要长时间处理） |
| 06 | Slave Device Busy | 从站设备忙 |

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

