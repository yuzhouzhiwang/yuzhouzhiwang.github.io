---
# 基础信息
title: "AT命令集应用完全指南"
description: "全面深入讲解AT命令集的基础知识、常用命令、调制解调器控制和实际应用，包括命令语法、响应解析、错误处理和UART通信实现，掌握嵌入式系统中AT命令的核心技术"
slug: "at-commands-application-guide"

# 分类信息
domain: "06-communication-networking"
module: "02-network-protocols"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - AT命令
  - 调制解调器
  - UART通信
  - GSM模块
  - WiFi模块
  - 蓝牙模块
  - 命令解析
  - 串口通信
prerequisites:
  - "../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-uart-driver.md"
  - "../../../01-hardware-layer/06-communication-interface-hardware/beginner/01-uart-hardware.md"
related_contents:
  - "01-tcpip-stack.md"
  - "02-mqtt-protocol.md"
  - "../intermediate/02-modbus-protocol.md"

# 学习信息
estimated_time: 90
difficulty_score: 3

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
  - AT命令集
  - Hayes命令
  - 调制解调器控制
  - GSM AT命令
  - ESP8266 AT命令
  - 蓝牙AT命令
  - 命令响应解析
  - 串口通信协议
cover_image: ""
---

# AT命令集应用完全指南

## 概述

AT命令集（AT Commands）是一种用于控制调制解调器和通信模块的文本命令协议。AT是"Attention"（注意）的缩写，最初由Hayes公司为其调制解调器开发，后来成为事实上的工业标准。在嵌入式系统中，AT命令广泛应用于GSM/GPRS模块、WiFi模块、蓝牙模块等各类通信设备的控制。

### 什么是AT命令

AT命令是一种基于ASCII文本的命令协议，具有以下特点：

1. **简单易用**：命令和响应都是可读的ASCII文本
2. **标准化**：遵循Hayes命令集标准，具有良好的兼容性
3. **串口通信**：通常通过UART串口进行通信
4. **同步/异步**：支持同步命令响应和异步事件通知
5. **可扩展**：厂商可以添加自定义命令

### AT命令的基本格式

```
AT命令格式：

基本命令：
AT<command>[<parameters>]<CR>

示例：
AT<CR>              - 测试命令
ATI<CR>             - 查询信息
ATD13800138000<CR>  - 拨号命令
AT+CGMI<CR>         - 查询厂商信息

响应格式：
<CR><LF><response><CR><LF>

示例：
<CR><LF>OK<CR><LF>
<CR><LF>ERROR<CR><LF>
<CR><LF>+CME ERROR: 3<CR><LF>

其中：
<CR> = 回车符 (0x0D)
<LF> = 换行符 (0x0A)
```

### AT命令 vs 其他通信协议

```
通信协议对比：

┌──────────────┬─────────┬─────────┬─────────┬─────────┐
│   特性       │  AT命令 │ Modbus  │  MQTT   │  HTTP   │
├──────────────┼─────────┼─────────┼─────────┼─────────┤
│ 复杂度       │  简单   │  中等   │  中等   │  复杂   │
│ 可读性       │  高     │  低     │  中     │  高     │
│ 传输效率     │  低     │  高     │  高     │  中     │
│ 实时性       │  好     │  很好   │  好     │  一般   │
│ 标准化       │  高     │  高     │  高     │  高     │
│ 学习曲线     │  平缓   │  中等   │  陡峭   │  陡峭   │
│ 应用场景     │  模块控制│工业控制│物联网   │Web应用  │
└──────────────┴─────────┴─────────┴─────────┴─────────┘

AT命令优势：
- 人类可读，便于调试
- 实现简单，资源占用少
- 广泛支持，兼容性好
- 适合交互式控制

AT命令劣势：
- 传输效率低
- 不适合大数据传输
- 解析相对复杂
```

### 应用场景

AT命令在嵌入式系统中的典型应用：

- **GSM/GPRS模块**：SIM800、SIM900、EC20等，用于短信、语音、数据通信
- **WiFi模块**：ESP8266、ESP32、WizFi360等，用于WiFi连接和网络通信
- **蓝牙模块**：HC-05、HC-06、BLE模块等，用于蓝牙配对和数据传输
- **GPS模块**：NEO-6M、NEO-M8N等，用于定位数据获取
- **LoRa模块**：RYLR896、E32等，用于远距离通信
- **NB-IoT模块**：BC95、BC26等，用于物联网通信
- **4G/5G模块**：EC25、RG500等，用于高速数据通信

### 本文内容概览

本教程将涵盖以下内容：

1. **AT命令基础**：命令格式、响应类型、错误处理
2. **UART通信实现**：串口配置、数据发送接收、缓冲管理
3. **命令解析器**：命令发送、响应解析、超时处理
4. **基本AT命令**：测试命令、信息查询、配置命令
5. **GSM模块应用**：SIM卡管理、短信收发、语音通话
6. **WiFi模块应用**：网络连接、TCP/UDP通信、HTTP请求
7. **蓝牙模块应用**：配对连接、数据传输、参数配置
8. **高级特性**：URC处理、多线程安全、命令队列
9. **错误处理**：超时重试、错误恢复、日志记录
10. **实战项目**：GSM短信收发、WiFi数据上传、蓝牙透传

## 第一部分：AT命令基础知识

### 1.1 AT命令分类

**按功能分类**：

```
AT命令功能分类：

1. 基本命令（Basic Commands）
   - AT      : 测试命令
   - ATE0/1  : 回显控制
   - ATZ     : 复位
   - AT&F    : 恢复出厂设置
   - AT&W    : 保存配置

2. 扩展命令（Extended Commands）
   - AT+<cmd> : 扩展命令格式
   - AT+<cmd>? : 查询命令
   - AT+<cmd>=? : 测试命令
   - AT+<cmd>=<params> : 设置命令

3. 专有命令（Proprietary Commands）
   - 厂商自定义命令
   - 模块特定功能

命令示例：
AT+CGMI     - 查询厂商信息
AT+CGMM     - 查询模块型号
AT+CGMR     - 查询固件版本
AT+CGSN     - 查询IMEI号
AT+CIMI     - 查询SIM卡IMSI
```

**按操作类型分类**：

```c
/**
 * @brief  AT命令操作类型
 */
typedef enum {
    AT_CMD_TEST,        // 测试命令：AT+CMD=?
    AT_CMD_QUERY,       // 查询命令：AT+CMD?
    AT_CMD_SET,         // 设置命令：AT+CMD=<params>
    AT_CMD_EXECUTE      // 执行命令：AT+CMD
} at_cmd_type_t;

/**
 * @brief  AT命令示例
 */
// 测试命令 - 查询命令支持的参数范围
// AT+CGDCONT=?
// 响应：+CGDCONT: (1-16),"IP",,,(0-2),(0-4)

// 查询命令 - 查询当前设置
// AT+CGDCONT?
// 响应：+CGDCONT: 1,"IP","cmnet","0.0.0.0",0,0

// 设置命令 - 设置参数
// AT+CGDCONT=1,"IP","cmnet"
// 响应：OK

// 执行命令 - 执行操作
// AT+CGACT=1,1
// 响应：OK
```

### 1.2 AT命令响应类型

**标准响应**：

```
AT命令响应类型：

1. 成功响应
   OK<CR><LF>

2. 错误响应
   ERROR<CR><LF>

3. CME错误（移动设备错误）
   +CME ERROR: <err><CR><LF>
   
   常见CME错误码：
   0   : 手机故障
   1   : 不支持
   2   : 不允许
   3   : 不允许的操作
   4   : 不支持的操作
   10  : SIM卡未插入
   11  : SIM卡PIN码需要
   12  : SIM卡PUK码需要
   13  : SIM卡故障
   14  : SIM卡忙
   15  : SIM卡错误
   16  : 密码错误
   17  : SIM卡PIN2码需要
   18  : SIM卡PUK2码需要

4. CMS错误（短信错误）
   +CMS ERROR: <err><CR><LF>
   
   常见CMS错误码：
   300 : ME故障
   301 : SMS服务保留
   302 : 不允许的操作
   303 : 不支持的操作
   304 : 无效的PDU模式参数
   305 : 无效的文本模式参数
   310 : SIM卡未插入
   311 : SIM卡PIN码需要
   312 : PH-SIM PIN码需要
   313 : SIM卡故障
   314 : SIM卡忙
   315 : SIM卡错误

5. 信息响应
   +<cmd>: <data><CR><LF>
   
   示例：
   +CGMI: SIMCOM_Ltd<CR><LF>
   +CSQ: 25,0<CR><LF>
   +CREG: 0,1<CR><LF>

6. 数据响应
   CONNECT<CR><LF>
   <data>
   NO CARRIER<CR><LF>
```

**响应代码定义**：

```c
/**
 * @brief  AT命令响应结果
 */
typedef enum {
    AT_RESP_OK = 0,         // 成功
    AT_RESP_ERROR,          // 一般错误
    AT_RESP_CME_ERROR,      // CME错误
    AT_RESP_CMS_ERROR,      // CMS错误
    AT_RESP_TIMEOUT,        // 超时
    AT_RESP_BUSY,           // 忙
    AT_RESP_NO_CARRIER,     // 无载波
    AT_RESP_NO_ANSWER,      // 无应答
    AT_RESP_NO_DIALTONE     // 无拨号音
} at_response_t;

/**
 * @brief  AT响应结构
 */
typedef struct {
    at_response_t result;   // 响应结果
    int error_code;         // 错误码
    char *data;             // 响应数据
    uint16_t data_len;      // 数据长度
} at_response_info_t;
```

### 1.3 URC（非请求结果码）

URC（Unsolicited Result Code）是模块主动上报的信息，不是对AT命令的响应。

**常见URC**：

```
URC示例：

1. 网络注册状态
   +CREG: <stat>
   +CGREG: <stat>
   
   示例：
   +CREG: 1  // 已注册本地网络

2. 信号质量变化
   +CSQ: <rssi>,<ber>
   
   示例：
   +CSQ: 25,0  // 信号强度25

3. 来电提示
   RING
   +CLIP: "<number>",<type>
   
   示例：
   RING
   +CLIP: "13800138000",129

4. 短信接收
   +CMTI: "<mem>",<index>
   
   示例：
   +CMTI: "SM",1  // SIM卡收到短信，索引1

5. TCP/IP连接状态
   <n>,CLOSED
   <n>,CONNECT OK
   
   示例：
   0,CONNECT OK  // 连接0建立成功

6. 数据接收
   +RECEIVE,<link_id>,<len>
   
   示例：
   +RECEIVE,0,100  // 连接0收到100字节数据
```

**URC处理机制**：

```c
/**
 * @brief  URC回调函数类型
 */
typedef void (*urc_callback_t)(const char *urc, uint16_t len);

/**
 * @brief  URC处理器结构
 */
typedef struct {
    const char *prefix;     // URC前缀
    urc_callback_t callback; // 回调函数
} urc_handler_t;

/**
 * @brief  URC处理器表
 */
static urc_handler_t urc_handlers[] = {
    {"+CREG:", handle_creg_urc},
    {"+CGREG:", handle_cgreg_urc},
    {"RING", handle_ring_urc},
    {"+CLIP:", handle_clip_urc},
    {"+CMTI:", handle_cmti_urc},
    {"+RECEIVE,", handle_receive_urc},
    {"CLOSED", handle_closed_urc},
    {NULL, NULL}  // 结束标记
};

/**
 * @brief  检查并处理URC
 * @param  line: 接收到的行
 * @return true: 是URC, false: 不是URC
 */
bool at_check_urc(const char *line)
{
    for (int i = 0; urc_handlers[i].prefix != NULL; i++) {
        if (strncmp(line, urc_handlers[i].prefix, 
                    strlen(urc_handlers[i].prefix)) == 0) {
            // 找到匹配的URC
            if (urc_handlers[i].callback != NULL) {
                urc_handlers[i].callback(line, strlen(line));
            }
            return true;
        }
    }
    return false;
}
```

## 第二部分：UART通信实现

### 2.1 UART配置

AT命令通常通过UART串口通信，需要正确配置串口参数。

**串口参数配置**：

```c
/**
 * @file    at_uart.c
 * @brief   AT命令UART通信实现
 * @author  嵌入式知识平台
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "stm32f1xx_hal.h"

/* UART句柄 */
UART_HandleTypeDef huart2;

/* 接收缓冲区 */
#define RX_BUFFER_SIZE  1024
static uint8_t rx_buffer[RX_BUFFER_SIZE];
static uint16_t rx_head = 0;
static uint16_t rx_tail = 0;

/* 单字节接收缓冲 */
static uint8_t rx_byte;

/**
 * @brief  UART初始化
 * @param  baudrate: 波特率
 * @return HAL状态
 */
HAL_StatusTypeDef at_uart_init(uint32_t baudrate)
{
    HAL_StatusTypeDef status;
    
    // 配置UART参数
    huart2.Instance = USART2;
    huart2.Init.BaudRate = baudrate;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    
    // 初始化UART
    status = HAL_UART_Init(&huart2);
    if (status != HAL_OK) {
        return status;
    }
    
    // 启动接收中断
    status = HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
    
    return status;
}

/**
 * @brief  UART接收中断回调
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        // 将接收到的字节放入环形缓冲区
        uint16_t next_head = (rx_head + 1) % RX_BUFFER_SIZE;
        
        if (next_head != rx_tail) {
            rx_buffer[rx_head] = rx_byte;
            rx_head = next_head;
        }
        
        // 继续接收下一个字节
        HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
    }
}

/**
 * @brief  发送数据
 * @param  data: 数据指针
 * @param  len: 数据长度
 * @return 发送的字节数
 */
int at_uart_send(const uint8_t *data, uint16_t len)
{
    HAL_StatusTypeDef status;
    
    status = HAL_UART_Transmit(&huart2, (uint8_t*)data, len, 1000);
    
    return (status == HAL_OK) ? len : -1;
}

/**
 * @brief  接收数据
 * @param  data: 数据缓冲区
 * @param  max_len: 最大长度
 * @return 接收的字节数
 */
int at_uart_receive(uint8_t *data, uint16_t max_len)
{
    uint16_t count = 0;
    
    while (rx_tail != rx_head && count < max_len) {
        data[count++] = rx_buffer[rx_tail];
        rx_tail = (rx_tail + 1) % RX_BUFFER_SIZE;
    }
    
    return count;
}

/**
 * @brief  获取可用数据数量
 * @return 可用字节数
 */
uint16_t at_uart_available(void)
{
    if (rx_head >= rx_tail) {
        return rx_head - rx_tail;
    } else {
        return RX_BUFFER_SIZE - rx_tail + rx_head;
    }
}

/**
 * @brief  清空接收缓冲区
 */
void at_uart_flush(void)
{
    rx_head = 0;
    rx_tail = 0;
}
```

### 2.2 行缓冲实现

AT命令是基于行的协议，需要实现行缓冲功能。

```c
/**
 * @file    at_line_buffer.c
 * @brief   AT命令行缓冲实现
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* 行缓冲区 */
#define LINE_BUFFER_SIZE  256
static char line_buffer[LINE_BUFFER_SIZE];
static uint16_t line_pos = 0;

/**
 * @brief  读取一行数据
 * @param  line: 行缓冲区
 * @param  max_len: 最大长度
 * @param  timeout_ms: 超时时间（毫秒）
 * @return 行长度，-1表示超时
 */
int at_read_line(char *line, uint16_t max_len, uint32_t timeout_ms)
{
    uint32_t start_time = HAL_GetTick();
    uint8_t ch;
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        // 检查是否有数据
        if (at_uart_available() > 0) {
            at_uart_receive(&ch, 1);
            
            // 处理回车换行
            if (ch == '\r' || ch == '\n') {
                if (line_pos > 0) {
                    // 行结束
                    line_buffer[line_pos] = '\0';
                    
                    // 复制到输出缓冲区
                    strncpy(line, line_buffer, max_len - 1);
                    line[max_len - 1] = '\0';
                    
                    uint16_t len = line_pos;
                    line_pos = 0;
                    
                    return len;
                }
                // 忽略空行
            } else {
                // 添加字符到行缓冲
                if (line_pos < LINE_BUFFER_SIZE - 1) {
                    line_buffer[line_pos++] = ch;
                }
            }
        }
    }
    
    return -1;  // 超时
}

/**
 * @brief  清空行缓冲
 */
void at_clear_line_buffer(void)
{
    line_pos = 0;
    memset(line_buffer, 0, LINE_BUFFER_SIZE);
}
```


## 第三部分：AT命令解析器实现

### 3.1 命令发送器

```c
/**
 * @file    at_parser.c
 * @brief   AT命令解析器实现
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>

/* AT命令超时时间 */
#define AT_DEFAULT_TIMEOUT  1000    // 默认超时1秒
#define AT_LONG_TIMEOUT     30000   // 长超时30秒

/**
 * @brief  发送AT命令
 * @param  cmd: 命令字符串
 * @return 发送的字节数
 */
int at_send_command(const char *cmd)
{
    int len = strlen(cmd);
    
    // 发送命令
    at_uart_send((const uint8_t*)cmd, len);
    
    // 发送回车换行
    at_uart_send((const uint8_t*)"\r\n", 2);
    
    return len + 2;
}

/**
 * @brief  发送格式化AT命令
 * @param  fmt: 格式字符串
 * @param  ...: 可变参数
 * @return 发送的字节数
 */
int at_send_command_fmt(const char *fmt, ...)
{
    char cmd_buffer[256];
    va_list args;
    
    va_start(args, fmt);
    vsnprintf(cmd_buffer, sizeof(cmd_buffer), fmt, args);
    va_end(args);
    
    return at_send_command(cmd_buffer);
}

/**
 * @brief  等待响应
 * @param  expected: 期望的响应字符串（可以为NULL）
 * @param  timeout_ms: 超时时间
 * @return AT响应结果
 */
at_response_t at_wait_response(const char *expected, uint32_t timeout_ms)
{
    char line[256];
    uint32_t start_time = HAL_GetTick();
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        // 读取一行
        int len = at_read_line(line, sizeof(line), 100);
        
        if (len > 0) {
            // 检查是否是URC
            if (at_check_urc(line)) {
                continue;  // 跳过URC，继续等待响应
            }
            
            // 检查响应
            if (strcmp(line, "OK") == 0) {
                return AT_RESP_OK;
            }
            else if (strcmp(line, "ERROR") == 0) {
                return AT_RESP_ERROR;
            }
            else if (strncmp(line, "+CME ERROR:", 11) == 0) {
                return AT_RESP_CME_ERROR;
            }
            else if (strncmp(line, "+CMS ERROR:", 11) == 0) {
                return AT_RESP_CMS_ERROR;
            }
            else if (strcmp(line, "BUSY") == 0) {
                return AT_RESP_BUSY;
            }
            else if (strcmp(line, "NO CARRIER") == 0) {
                return AT_RESP_NO_CARRIER;
            }
            else if (expected != NULL && strstr(line, expected) != NULL) {
                // 找到期望的响应
                return AT_RESP_OK;
            }
        }
    }
    
    return AT_RESP_TIMEOUT;
}

/**
 * @brief  执行AT命令并等待响应
 * @param  cmd: 命令字符串
 * @param  expected: 期望的响应（可以为NULL）
 * @param  timeout_ms: 超时时间
 * @return AT响应结果
 */
at_response_t at_execute_command(const char *cmd, const char *expected, uint32_t timeout_ms)
{
    // 清空接收缓冲
    at_uart_flush();
    at_clear_line_buffer();
    
    // 发送命令
    at_send_command(cmd);
    
    // 等待响应
    return at_wait_response(expected, timeout_ms);
}
```

### 3.2 响应解析器

```c
/**
 * @brief  解析响应数据
 * @param  response: 响应字符串
 * @param  prefix: 响应前缀
 * @param  data: 输出数据缓冲区
 * @param  max_len: 最大长度
 * @return 解析的数据长度，-1表示失败
 */
int at_parse_response(const char *response, const char *prefix, char *data, uint16_t max_len)
{
    // 查找前缀
    const char *start = strstr(response, prefix);
    if (start == NULL) {
        return -1;
    }
    
    // 跳过前缀
    start += strlen(prefix);
    
    // 跳过空格
    while (*start == ' ') {
        start++;
    }
    
    // 复制数据
    uint16_t len = 0;
    while (*start != '\r' && *start != '\n' && *start != '\0' && len < max_len - 1) {
        data[len++] = *start++;
    }
    data[len] = '\0';
    
    return len;
}

/**
 * @brief  解析整数参数
 * @param  response: 响应字符串
 * @param  prefix: 响应前缀
 * @param  value: 输出整数值
 * @return 0: 成功, -1: 失败
 */
int at_parse_int(const char *response, const char *prefix, int *value)
{
    char data[32];
    
    if (at_parse_response(response, prefix, data, sizeof(data)) < 0) {
        return -1;
    }
    
    *value = atoi(data);
    return 0;
}

/**
 * @brief  解析多个参数
 * @param  response: 响应字符串
 * @param  prefix: 响应前缀
 * @param  params: 参数数组
 * @param  max_params: 最大参数数量
 * @return 解析的参数数量
 */
int at_parse_params(const char *response, const char *prefix, char params[][64], int max_params)
{
    char data[256];
    
    if (at_parse_response(response, prefix, data, sizeof(data)) < 0) {
        return -1;
    }
    
    int count = 0;
    char *token = strtok(data, ",");
    
    while (token != NULL && count < max_params) {
        // 去除引号
        if (token[0] == '"') {
            token++;
            char *end = strchr(token, '"');
            if (end != NULL) {
                *end = '\0';
            }
        }
        
        strncpy(params[count], token, 63);
        params[count][63] = '\0';
        count++;
        
        token = strtok(NULL, ",");
    }
    
    return count;
}

/**
 * @brief  读取响应数据
 * @param  prefix: 响应前缀
 * @param  data: 数据缓冲区
 * @param  max_len: 最大长度
 * @param  timeout_ms: 超时时间
 * @return 读取的数据长度，-1表示失败
 */
int at_read_response_data(const char *prefix, char *data, uint16_t max_len, uint32_t timeout_ms)
{
    char line[256];
    uint32_t start_time = HAL_GetTick();
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        int len = at_read_line(line, sizeof(line), 100);
        
        if (len > 0) {
            // 检查是否包含前缀
            if (strncmp(line, prefix, strlen(prefix)) == 0) {
                // 解析数据
                return at_parse_response(line, prefix, data, max_len);
            }
        }
    }
    
    return -1;  // 超时
}
```

### 3.3 命令重试机制

```c
/**
 * @brief  带重试的命令执行
 * @param  cmd: 命令字符串
 * @param  expected: 期望的响应
 * @param  timeout_ms: 超时时间
 * @param  retry_count: 重试次数
 * @return AT响应结果
 */
at_response_t at_execute_with_retry(const char *cmd, const char *expected, 
                                     uint32_t timeout_ms, int retry_count)
{
    at_response_t result;
    
    for (int i = 0; i <= retry_count; i++) {
        result = at_execute_command(cmd, expected, timeout_ms);
        
        if (result == AT_RESP_OK) {
            return result;  // 成功
        }
        
        // 失败，延迟后重试
        if (i < retry_count) {
            HAL_Delay(500);
        }
    }
    
    return result;  // 所有重试都失败
}

/**
 * @brief  测试AT命令
 * @return true: 模块响应正常, false: 模块无响应
 */
bool at_test(void)
{
    at_response_t result = at_execute_with_retry("AT", NULL, 1000, 3);
    return (result == AT_RESP_OK);
}
```

## 第四部分：基本AT命令应用

### 4.1 模块信息查询

```c
/**
 * @file    at_basic.c
 * @brief   基本AT命令应用
 */

/**
 * @brief  查询厂商信息
 * @param  manufacturer: 厂商名称缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_get_manufacturer(char *manufacturer, uint16_t max_len)
{
    at_response_t result;
    
    // 发送命令
    at_send_command("AT+CGMI");
    
    // 读取响应
    if (at_read_response_data("", manufacturer, max_len, 1000) < 0) {
        return -1;
    }
    
    // 等待OK
    result = at_wait_response(NULL, 1000);
    
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询模块型号
 * @param  model: 型号缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_get_model(char *model, uint16_t max_len)
{
    at_send_command("AT+CGMM");
    
    if (at_read_response_data("", model, max_len, 1000) < 0) {
        return -1;
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询固件版本
 * @param  version: 版本缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_get_firmware_version(char *version, uint16_t max_len)
{
    at_send_command("AT+CGMR");
    
    if (at_read_response_data("", version, max_len, 1000) < 0) {
        return -1;
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询IMEI号
 * @param  imei: IMEI缓冲区（至少16字节）
 * @return 0: 成功, -1: 失败
 */
int at_get_imei(char *imei)
{
    at_send_command("AT+CGSN");
    
    if (at_read_response_data("", imei, 16, 1000) < 0) {
        return -1;
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```

### 4.2 模块配置命令

```c
/**
 * @brief  设置回显模式
 * @param  enable: true启用回显，false禁用回显
 * @return 0: 成功, -1: 失败
 */
int at_set_echo(bool enable)
{
    const char *cmd = enable ? "ATE1" : "ATE0";
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  复位模块
 * @return 0: 成功, -1: 失败
 */
int at_reset(void)
{
    at_response_t result = at_execute_command("ATZ", NULL, 3000);
    HAL_Delay(1000);  // 等待模块重启
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  恢复出厂设置
 * @return 0: 成功, -1: 失败
 */
int at_factory_reset(void)
{
    at_response_t result = at_execute_command("AT&F", NULL, 3000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  保存配置
 * @return 0: 成功, -1: 失败
 */
int at_save_config(void)
{
    at_response_t result = at_execute_command("AT&W", NULL, 3000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```


## 第五部分：GSM模块应用

### 5.1 SIM卡管理

```c
/**
 * @file    at_gsm.c
 * @brief   GSM模块AT命令应用
 */

/**
 * @brief  检查SIM卡状态
 * @return 0: SIM卡就绪, -1: SIM卡未就绪
 */
int at_check_sim_status(void)
{
    at_response_t result;
    char response[64];
    
    at_send_command("AT+CPIN?");
    
    // 读取响应
    if (at_read_response_data("+CPIN:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    // 等待OK
    result = at_wait_response(NULL, 1000);
    if (result != AT_RESP_OK) {
        return -1;
    }
    
    // 检查状态
    if (strstr(response, "READY") != NULL) {
        return 0;  // SIM卡就绪
    }
    
    return -1;  // SIM卡未就绪或需要PIN码
}

/**
 * @brief  输入PIN码
 * @param  pin: PIN码字符串
 * @return 0: 成功, -1: 失败
 */
int at_enter_pin(const char *pin)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CPIN=\"%s\"", pin);
    
    at_response_t result = at_execute_command(cmd, NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询IMSI号
 * @param  imsi: IMSI缓冲区（至少16字节）
 * @return 0: 成功, -1: 失败
 */
int at_get_imsi(char *imsi)
{
    at_send_command("AT+CIMI");
    
    if (at_read_response_data("", imsi, 16, 1000) < 0) {
        return -1;
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询SIM卡运营商
 * @param  operator: 运营商名称缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_get_operator(char *operator, uint16_t max_len)
{
    at_send_command("AT+COPS?");
    
    char response[128];
    if (at_read_response_data("+COPS:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    // 解析运营商名称
    char params[5][64];
    int count = at_parse_params(response, "+COPS:", params, 5);
    
    if (count >= 3) {
        strncpy(operator, params[2], max_len - 1);
        operator[max_len - 1] = '\0';
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```

### 5.2 网络注册

```c
/**
 * @brief  网络注册状态
 */
typedef enum {
    NET_NOT_REGISTERED = 0,     // 未注册
    NET_REGISTERED_HOME,        // 已注册本地网络
    NET_SEARCHING,              // 正在搜索
    NET_REGISTRATION_DENIED,    // 注册被拒绝
    NET_UNKNOWN,                // 未知
    NET_REGISTERED_ROAMING      // 已注册漫游网络
} network_status_t;

/**
 * @brief  查询网络注册状态
 * @param  status: 网络状态
 * @return 0: 成功, -1: 失败
 */
int at_get_network_status(network_status_t *status)
{
    at_send_command("AT+CREG?");
    
    char response[64];
    if (at_read_response_data("+CREG:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    // 解析状态
    char params[3][64];
    int count = at_parse_params(response, "+CREG:", params, 3);
    
    if (count >= 2) {
        *status = (network_status_t)atoi(params[1]);
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  等待网络注册
 * @param  timeout_ms: 超时时间
 * @return 0: 成功, -1: 超时
 */
int at_wait_network_registration(uint32_t timeout_ms)
{
    uint32_t start_time = HAL_GetTick();
    network_status_t status;
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        if (at_get_network_status(&status) == 0) {
            if (status == NET_REGISTERED_HOME || status == NET_REGISTERED_ROAMING) {
                return 0;  // 已注册
            }
        }
        
        HAL_Delay(1000);  // 每秒检查一次
    }
    
    return -1;  // 超时
}

/**
 * @brief  查询信号强度
 * @param  rssi: 信号强度（0-31，99表示未知）
 * @param  ber: 误码率（0-7，99表示未知）
 * @return 0: 成功, -1: 失败
 */
int at_get_signal_quality(int *rssi, int *ber)
{
    at_send_command("AT+CSQ");
    
    char response[64];
    if (at_read_response_data("+CSQ:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    // 解析参数
    char params[2][64];
    int count = at_parse_params(response, "+CSQ:", params, 2);
    
    if (count >= 2) {
        *rssi = atoi(params[0]);
        *ber = atoi(params[1]);
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  将RSSI转换为dBm
 * @param  rssi: RSSI值（0-31）
 * @return dBm值
 */
int at_rssi_to_dbm(int rssi)
{
    if (rssi == 0) {
        return -113;  // 或更低
    } else if (rssi == 1) {
        return -111;
    } else if (rssi >= 2 && rssi <= 30) {
        return -109 + (rssi - 2) * 2;
    } else if (rssi == 31) {
        return -51;  // 或更高
    } else {
        return -999;  // 未知
    }
}
```

### 5.3 短信收发

```c
/**
 * @brief  设置短信格式
 * @param  text_mode: true为文本模式，false为PDU模式
 * @return 0: 成功, -1: 失败
 */
int at_set_sms_format(bool text_mode)
{
    const char *cmd = text_mode ? "AT+CMGF=1" : "AT+CMGF=0";
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  发送短信（文本模式）
 * @param  phone_number: 电话号码
 * @param  message: 短信内容
 * @return 0: 成功, -1: 失败
 */
int at_send_sms(const char *phone_number, const char *message)
{
    char cmd[64];
    at_response_t result;
    
    // 设置为文本模式
    if (at_set_sms_format(true) != 0) {
        return -1;
    }
    
    // 发送AT+CMGS命令
    snprintf(cmd, sizeof(cmd), "AT+CMGS=\"%s\"", phone_number);
    at_send_command(cmd);
    
    // 等待'>'提示符
    HAL_Delay(500);
    
    // 发送短信内容
    at_uart_send((const uint8_t*)message, strlen(message));
    
    // 发送Ctrl+Z（0x1A）结束
    uint8_t ctrl_z = 0x1A;
    at_uart_send(&ctrl_z, 1);
    
    // 等待响应（发送短信可能需要较长时间）
    result = at_wait_response("+CMGS:", 30000);
    
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  读取短信
 * @param  index: 短信索引
 * @param  phone_number: 电话号码缓冲区
 * @param  message: 短信内容缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_read_sms(int index, char *phone_number, char *message, uint16_t max_len)
{
    char cmd[32];
    char line[256];
    
    // 设置为文本模式
    if (at_set_sms_format(true) != 0) {
        return -1;
    }
    
    // 发送读取命令
    snprintf(cmd, sizeof(cmd), "AT+CMGR=%d", index);
    at_send_command(cmd);
    
    // 读取响应头
    if (at_read_line(line, sizeof(line), 2000) < 0) {
        return -1;
    }
    
    // 解析电话号码
    // +CMGR: "REC UNREAD","+8613800138000",,"21/01/01,12:00:00+32"
    char params[5][64];
    int count = at_parse_params(line, "+CMGR:", params, 5);
    
    if (count >= 2) {
        strncpy(phone_number, params[1], 31);
        phone_number[31] = '\0';
    }
    
    // 读取短信内容
    if (at_read_line(message, max_len, 2000) < 0) {
        return -1;
    }
    
    // 等待OK
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  删除短信
 * @param  index: 短信索引
 * @return 0: 成功, -1: 失败
 */
int at_delete_sms(int index)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CMGD=%d", index);
    
    at_response_t result = at_execute_command(cmd, NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  列出所有短信
 * @param  status: 短信状态（"ALL", "REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"）
 * @return 0: 成功, -1: 失败
 */
int at_list_sms(const char *status)
{
    char cmd[64];
    
    // 设置为文本模式
    if (at_set_sms_format(true) != 0) {
        return -1;
    }
    
    // 发送列表命令
    snprintf(cmd, sizeof(cmd), "AT+CMGL=\"%s\"", status);
    at_send_command(cmd);
    
    // 读取所有短信
    char line[256];
    while (1) {
        int len = at_read_line(line, sizeof(line), 2000);
        
        if (len < 0) {
            break;  // 超时
        }
        
        if (strcmp(line, "OK") == 0) {
            return 0;  // 成功
        }
        
        // 处理短信列表项
        if (strncmp(line, "+CMGL:", 6) == 0) {
            // 这是短信头
            // 下一行是短信内容
            at_read_line(line, sizeof(line), 2000);
            // 这里可以处理短信内容
        }
    }
    
    return -1;
}
```

### 5.4 语音通话

```c
/**
 * @brief  拨打电话
 * @param  phone_number: 电话号码
 * @return 0: 成功, -1: 失败
 */
int at_dial(const char *phone_number)
{
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "ATD%s;", phone_number);
    
    at_response_t result = at_execute_command(cmd, NULL, 30000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  接听电话
 * @return 0: 成功, -1: 失败
 */
int at_answer_call(void)
{
    at_response_t result = at_execute_command("ATA", NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  挂断电话
 * @return 0: 成功, -1: 失败
 */
int at_hangup(void)
{
    at_response_t result = at_execute_command("ATH", NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  启用来电显示
 * @param  enable: true启用，false禁用
 * @return 0: 成功, -1: 失败
 */
int at_enable_caller_id(bool enable)
{
    const char *cmd = enable ? "AT+CLIP=1" : "AT+CLIP=0";
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```


## 第六部分：WiFi模块应用（ESP8266）

### 6.1 WiFi基本配置

```c
/**
 * @file    at_wifi.c
 * @brief   WiFi模块（ESP8266）AT命令应用
 */

/**
 * @brief  设置WiFi模式
 * @param  mode: 1=Station, 2=AP, 3=Station+AP
 * @return 0: 成功, -1: 失败
 */
int at_wifi_set_mode(int mode)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CWMODE=%d", mode);
    
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  连接WiFi网络
 * @param  ssid: WiFi名称
 * @param  password: WiFi密码
 * @return 0: 成功, -1: 失败
 */
int at_wifi_connect(const char *ssid, const char *password)
{
    char cmd[128];
    snprintf(cmd, sizeof(cmd), "AT+CWJAP=\"%s\",\"%s\"", ssid, password);
    
    // WiFi连接可能需要较长时间
    at_response_t result = at_execute_command(cmd, NULL, 20000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  断开WiFi连接
 * @return 0: 成功, -1: 失败
 */
int at_wifi_disconnect(void)
{
    at_response_t result = at_execute_command("AT+CWQAP", NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询WiFi连接状态
 * @param  ssid: SSID缓冲区
 * @param  max_len: 最大长度
 * @return 0: 已连接, -1: 未连接
 */
int at_wifi_get_connection(char *ssid, uint16_t max_len)
{
    at_send_command("AT+CWJAP?");
    
    char response[128];
    if (at_read_response_data("+CWJAP:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    // 解析SSID
    char params[5][64];
    int count = at_parse_params(response, "+CWJAP:", params, 5);
    
    if (count >= 1) {
        strncpy(ssid, params[0], max_len - 1);
        ssid[max_len - 1] = '\0';
    }
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  获取IP地址
 * @param  ip: IP地址缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_wifi_get_ip(char *ip, uint16_t max_len)
{
    at_send_command("AT+CIFSR");
    
    char line[128];
    
    // 读取多行响应
    while (1) {
        int len = at_read_line(line, sizeof(line), 2000);
        
        if (len < 0) {
            return -1;  // 超时
        }
        
        // 查找STAIP
        if (strncmp(line, "+CIFSR:STAIP,", 13) == 0) {
            // 解析IP地址
            char *start = strchr(line, '"');
            if (start != NULL) {
                start++;
                char *end = strchr(start, '"');
                if (end != NULL) {
                    int ip_len = end - start;
                    if (ip_len < max_len) {
                        strncpy(ip, start, ip_len);
                        ip[ip_len] = '\0';
                        return 0;
                    }
                }
            }
        }
        
        if (strcmp(line, "OK") == 0) {
            break;
        }
    }
    
    return -1;
}

/**
 * @brief  扫描WiFi网络
 * @return 0: 成功, -1: 失败
 */
int at_wifi_scan(void)
{
    at_send_command("AT+CWLAP");
    
    char line[256];
    
    // 读取扫描结果
    while (1) {
        int len = at_read_line(line, sizeof(line), 10000);
        
        if (len < 0) {
            return -1;  // 超时
        }
        
        if (strncmp(line, "+CWLAP:", 7) == 0) {
            // 解析WiFi信息
            // +CWLAP:(3,"SSID",-65,"aa:bb:cc:dd:ee:ff",1)
            // 这里可以处理扫描结果
        }
        
        if (strcmp(line, "OK") == 0) {
            return 0;  // 成功
        }
    }
}
```

### 6.2 TCP/IP通信

```c
/**
 * @brief  设置多连接模式
 * @param  enable: true启用多连接，false单连接
 * @return 0: 成功, -1: 失败
 */
int at_wifi_set_mux(bool enable)
{
    const char *cmd = enable ? "AT+CIPMUX=1" : "AT+CIPMUX=0";
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  建立TCP连接
 * @param  link_id: 连接ID（0-4，多连接模式）
 * @param  type: 连接类型（"TCP"或"UDP"）
 * @param  remote_ip: 远程IP地址
 * @param  remote_port: 远程端口
 * @return 0: 成功, -1: 失败
 */
int at_wifi_connect_tcp(int link_id, const char *type, const char *remote_ip, int remote_port)
{
    char cmd[128];
    snprintf(cmd, sizeof(cmd), "AT+CIPSTART=%d,\"%s\",\"%s\",%d", 
             link_id, type, remote_ip, remote_port);
    
    at_response_t result = at_execute_command(cmd, "CONNECT", 10000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  发送数据
 * @param  link_id: 连接ID
 * @param  data: 数据指针
 * @param  len: 数据长度
 * @return 0: 成功, -1: 失败
 */
int at_wifi_send_data(int link_id, const uint8_t *data, uint16_t len)
{
    char cmd[64];
    at_response_t result;
    
    // 发送AT+CIPSEND命令
    snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%d,%d", link_id, len);
    at_send_command(cmd);
    
    // 等待'>'提示符
    HAL_Delay(100);
    
    // 发送数据
    at_uart_send(data, len);
    
    // 等待SEND OK
    result = at_wait_response("SEND OK", 5000);
    
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  接收数据
 * @param  link_id: 连接ID
 * @param  data: 数据缓冲区
 * @param  max_len: 最大长度
 * @param  timeout_ms: 超时时间
 * @return 接收的字节数，-1表示失败
 */
int at_wifi_receive_data(int link_id, uint8_t *data, uint16_t max_len, uint32_t timeout_ms)
{
    char line[256];
    uint32_t start_time = HAL_GetTick();
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        int len = at_read_line(line, sizeof(line), 100);
        
        if (len > 0) {
            // 检查是否是数据接收通知
            // +IPD,<link_id>,<len>:<data>
            if (strncmp(line, "+IPD,", 5) == 0) {
                // 解析参数
                int recv_link_id, recv_len;
                sscanf(line, "+IPD,%d,%d:", &recv_link_id, &recv_len);
                
                if (recv_link_id == link_id && recv_len <= max_len) {
                    // 查找数据起始位置
                    char *data_start = strchr(line, ':');
                    if (data_start != NULL) {
                        data_start++;
                        
                        // 复制数据
                        int copy_len = strlen(data_start);
                        if (copy_len > recv_len) {
                            copy_len = recv_len;
                        }
                        
                        memcpy(data, data_start, copy_len);
                        return copy_len;
                    }
                }
            }
        }
    }
    
    return -1;  // 超时
}

/**
 * @brief  关闭连接
 * @param  link_id: 连接ID
 * @return 0: 成功, -1: 失败
 */
int at_wifi_close_connection(int link_id)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CIPCLOSE=%d", link_id);
    
    at_response_t result = at_execute_command(cmd, NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```

### 6.3 HTTP请求

```c
/**
 * @brief  HTTP GET请求
 * @param  url: URL地址
 * @param  response: 响应缓冲区
 * @param  max_len: 最大长度
 * @return 接收的字节数，-1表示失败
 */
int at_wifi_http_get(const char *url, char *response, uint16_t max_len)
{
    char cmd[256];
    at_response_t result;
    
    // 设置HTTP参数
    snprintf(cmd, sizeof(cmd), "AT+HTTPCLIENT=2,0,\"%s\",,,2", url);
    at_send_command(cmd);
    
    // 读取响应
    char line[256];
    int total_len = 0;
    
    while (1) {
        int len = at_read_line(line, sizeof(line), 30000);
        
        if (len < 0) {
            return -1;  // 超时
        }
        
        // 检查是否是数据行
        if (strncmp(line, "+HTTPCLIENT:", 12) == 0) {
            // 解析数据长度
            int data_len;
            sscanf(line, "+HTTPCLIENT:%d", &data_len);
            
            // 读取数据
            if (data_len > 0 && total_len + data_len < max_len) {
                at_uart_receive((uint8_t*)&response[total_len], data_len);
                total_len += data_len;
            }
        }
        
        if (strcmp(line, "OK") == 0) {
            response[total_len] = '\0';
            return total_len;
        }
        
        if (strcmp(line, "ERROR") == 0) {
            return -1;
        }
    }
}

/**
 * @brief  HTTP POST请求
 * @param  url: URL地址
 * @param  data: POST数据
 * @param  response: 响应缓冲区
 * @param  max_len: 最大长度
 * @return 接收的字节数，-1表示失败
 */
int at_wifi_http_post(const char *url, const char *data, char *response, uint16_t max_len)
{
    char cmd[512];
    
    // 设置HTTP参数
    snprintf(cmd, sizeof(cmd), "AT+HTTPCLIENT=3,0,\"%s\",,\"%s\",2", url, data);
    at_send_command(cmd);
    
    // 读取响应（类似GET）
    char line[256];
    int total_len = 0;
    
    while (1) {
        int len = at_read_line(line, sizeof(line), 30000);
        
        if (len < 0) {
            return -1;
        }
        
        if (strncmp(line, "+HTTPCLIENT:", 12) == 0) {
            int data_len;
            sscanf(line, "+HTTPCLIENT:%d", &data_len);
            
            if (data_len > 0 && total_len + data_len < max_len) {
                at_uart_receive((uint8_t*)&response[total_len], data_len);
                total_len += data_len;
            }
        }
        
        if (strcmp(line, "OK") == 0) {
            response[total_len] = '\0';
            return total_len;
        }
        
        if (strcmp(line, "ERROR") == 0) {
            return -1;
        }
    }
}
```


## 第七部分：蓝牙模块应用（HC-05/HC-06）

### 7.1 蓝牙基本配置

```c
/**
 * @file    at_bluetooth.c
 * @brief   蓝牙模块（HC-05）AT命令应用
 */

/**
 * @brief  进入AT命令模式
 * @note   HC-05需要在上电前将KEY引脚拉高
 * @return 0: 成功, -1: 失败
 */
int at_bt_enter_at_mode(void)
{
    // HC-05在AT模式下波特率为38400
    at_uart_init(38400);
    
    // 测试AT命令
    at_response_t result = at_execute_with_retry("AT", NULL, 1000, 3);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询蓝牙名称
 * @param  name: 名称缓冲区
 * @param  max_len: 最大长度
 * @return 0: 成功, -1: 失败
 */
int at_bt_get_name(char *name, uint16_t max_len)
{
    at_send_command("AT+NAME?");
    
    char response[64];
    if (at_read_response_data("+NAME:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    strncpy(name, response, max_len - 1);
    name[max_len - 1] = '\0';
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  设置蓝牙名称
 * @param  name: 新名称
 * @return 0: 成功, -1: 失败
 */
int at_bt_set_name(const char *name)
{
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+NAME=%s", name);
    
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询蓝牙地址
 * @param  addr: 地址缓冲区（格式：XXXX:XX:XXXXXX）
 * @return 0: 成功, -1: 失败
 */
int at_bt_get_address(char *addr)
{
    at_send_command("AT+ADDR?");
    
    char response[32];
    if (at_read_response_data("+ADDR:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    strcpy(addr, response);
    
    at_response_t result = at_wait_response(NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  设置蓝牙PIN码
 * @param  pin: PIN码（4位数字）
 * @return 0: 成功, -1: 失败
 */
int at_bt_set_pin(const char *pin)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+PSWD=%s", pin);
    
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  设置蓝牙角色
 * @param  role: 0=从机，1=主机，2=从机循环
 * @return 0: 成功, -1: 失败
 */
int at_bt_set_role(int role)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+ROLE=%d", role);
    
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  设置串口参数
 * @param  baudrate: 波特率
 * @param  stop_bits: 停止位（0=1位，1=2位）
 * @param  parity: 校验位（0=无，1=奇，2=偶）
 * @return 0: 成功, -1: 失败
 */
int at_bt_set_uart(uint32_t baudrate, int stop_bits, int parity)
{
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+UART=%lu,%d,%d", baudrate, stop_bits, parity);
    
    at_response_t result = at_execute_command(cmd, NULL, 1000);
    return (result == AT_RESP_OK) ? 0 : -1;
}
```

### 7.2 蓝牙配对和连接

```c
/**
 * @brief  搜索蓝牙设备
 * @param  max_devices: 最大设备数量
 * @param  timeout_ms: 搜索超时时间
 * @return 找到的设备数量，-1表示失败
 */
int at_bt_scan_devices(int max_devices, uint32_t timeout_ms)
{
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+INQM=1,5,%d", max_devices);
    
    // 设置搜索模式
    if (at_execute_command(cmd, NULL, 1000) != AT_RESP_OK) {
        return -1;
    }
    
    // 开始搜索
    at_send_command("AT+INQ");
    
    char line[128];
    int device_count = 0;
    uint32_t start_time = HAL_GetTick();
    
    while ((HAL_GetTick() - start_time) < timeout_ms) {
        int len = at_read_line(line, sizeof(line), 1000);
        
        if (len > 0) {
            // 解析设备信息
            // +INQ:1234:56:789ABC,1F00,7FFF
            if (strncmp(line, "+INQ:", 5) == 0) {
                device_count++;
                // 这里可以保存设备信息
            }
            
            if (strcmp(line, "OK") == 0) {
                return device_count;
            }
        }
    }
    
    // 取消搜索
    at_send_command("AT+INQC");
    
    return device_count;
}

/**
 * @brief  连接蓝牙设备
 * @param  address: 设备地址（格式：XXXX,XX,XXXXXX）
 * @return 0: 成功, -1: 失败
 */
int at_bt_connect(const char *address)
{
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+LINK=%s", address);
    
    // 连接可能需要较长时间
    at_response_t result = at_execute_command(cmd, NULL, 30000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  断开蓝牙连接
 * @return 0: 成功, -1: 失败
 */
int at_bt_disconnect(void)
{
    at_response_t result = at_execute_command("AT+DISC", NULL, 5000);
    return (result == AT_RESP_OK) ? 0 : -1;
}

/**
 * @brief  查询连接状态
 * @return 0: 未连接, 1: 已连接, -1: 查询失败
 */
int at_bt_get_connection_status(void)
{
    at_send_command("AT+STATE?");
    
    char response[32];
    if (at_read_response_data("+STATE:", response, sizeof(response), 1000) < 0) {
        return -1;
    }
    
    at_wait_response(NULL, 1000);
    
    // 解析状态
    if (strstr(response, "CONNECTED") != NULL) {
        return 1;  // 已连接
    } else {
        return 0;  // 未连接
    }
}
```

## 第八部分：高级特性

### 8.1 命令队列

```c
/**
 * @file    at_queue.c
 * @brief   AT命令队列实现
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* 命令队列大小 */
#define CMD_QUEUE_SIZE  10

/**
 * @brief  命令队列项
 */
typedef struct {
    char cmd[128];              // 命令字符串
    char expected[64];          // 期望响应
    uint32_t timeout;           // 超时时间
    at_response_t result;       // 执行结果
    bool completed;             // 完成标志
} cmd_queue_item_t;

/**
 * @brief  命令队列
 */
static cmd_queue_item_t cmd_queue[CMD_QUEUE_SIZE];
static int queue_head = 0;
static int queue_tail = 0;
static int queue_count = 0;

/**
 * @brief  添加命令到队列
 * @param  cmd: 命令字符串
 * @param  expected: 期望响应
 * @param  timeout: 超时时间
 * @return 0: 成功, -1: 队列已满
 */
int at_queue_add(const char *cmd, const char *expected, uint32_t timeout)
{
    if (queue_count >= CMD_QUEUE_SIZE) {
        return -1;  // 队列已满
    }
    
    // 添加到队列尾部
    strncpy(cmd_queue[queue_tail].cmd, cmd, sizeof(cmd_queue[queue_tail].cmd) - 1);
    
    if (expected != NULL) {
        strncpy(cmd_queue[queue_tail].expected, expected, sizeof(cmd_queue[queue_tail].expected) - 1);
    } else {
        cmd_queue[queue_tail].expected[0] = '\0';
    }
    
    cmd_queue[queue_tail].timeout = timeout;
    cmd_queue[queue_tail].completed = false;
    
    queue_tail = (queue_tail + 1) % CMD_QUEUE_SIZE;
    queue_count++;
    
    return 0;
}

/**
 * @brief  处理命令队列
 * @return 处理的命令数量
 */
int at_queue_process(void)
{
    int processed = 0;
    
    while (queue_count > 0) {
        // 获取队列头部命令
        cmd_queue_item_t *item = &cmd_queue[queue_head];
        
        // 执行命令
        const char *expected = (item->expected[0] != '\0') ? item->expected : NULL;
        item->result = at_execute_command(item->cmd, expected, item->timeout);
        item->completed = true;
        
        // 移动队列头部
        queue_head = (queue_head + 1) % CMD_QUEUE_SIZE;
        queue_count--;
        processed++;
    }
    
    return processed;
}

/**
 * @brief  清空命令队列
 */
void at_queue_clear(void)
{
    queue_head = 0;
    queue_tail = 0;
    queue_count = 0;
}
```

### 8.2 多线程安全

```c
/**
 * @file    at_thread_safe.c
 * @brief   AT命令多线程安全实现
 */

#include "cmsis_os.h"

/* 互斥锁 */
static osMutexId_t at_mutex = NULL;

/**
 * @brief  初始化AT命令互斥锁
 * @return 0: 成功, -1: 失败
 */
int at_mutex_init(void)
{
    at_mutex = osMutexNew(NULL);
    return (at_mutex != NULL) ? 0 : -1;
}

/**
 * @brief  线程安全的命令执行
 * @param  cmd: 命令字符串
 * @param  expected: 期望响应
 * @param  timeout_ms: 超时时间
 * @return AT响应结果
 */
at_response_t at_execute_command_safe(const char *cmd, const char *expected, uint32_t timeout_ms)
{
    at_response_t result;
    
    // 获取互斥锁
    if (osMutexAcquire(at_mutex, osWaitForever) != osOK) {
        return AT_RESP_ERROR;
    }
    
    // 执行命令
    result = at_execute_command(cmd, expected, timeout_ms);
    
    // 释放互斥锁
    osMutexRelease(at_mutex);
    
    return result;
}
```

### 8.3 日志记录

```c
/**
 * @file    at_log.c
 * @brief   AT命令日志记录
 */

#include <stdio.h>
#include <stdarg.h>

/* 日志级别 */
typedef enum {
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARN,
    LOG_LEVEL_ERROR
} log_level_t;

static log_level_t current_log_level = LOG_LEVEL_INFO;

/**
 * @brief  设置日志级别
 * @param  level: 日志级别
 */
void at_log_set_level(log_level_t level)
{
    current_log_level = level;
}

/**
 * @brief  记录日志
 * @param  level: 日志级别
 * @param  fmt: 格式字符串
 * @param  ...: 可变参数
 */
void at_log(log_level_t level, const char *fmt, ...)
{
    if (level < current_log_level) {
        return;
    }
    
    const char *level_str[] = {"DEBUG", "INFO", "WARN", "ERROR"};
    
    printf("[AT][%s] ", level_str[level]);
    
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    
    printf("\r\n");
}

/**
 * @brief  记录命令
 * @param  cmd: 命令字符串
 */
void at_log_command(const char *cmd)
{
    at_log(LOG_LEVEL_DEBUG, "TX: %s", cmd);
}

/**
 * @brief  记录响应
 * @param  response: 响应字符串
 */
void at_log_response(const char *response)
{
    at_log(LOG_LEVEL_DEBUG, "RX: %s", response);
}
```


## 第九部分：错误处理与故障排除

### 9.1 常见错误处理

```c
/**
 * @file    at_error.c
 * @brief   AT命令错误处理
 */

/**
 * @brief  错误码定义
 */
typedef enum {
    AT_ERR_OK = 0,              // 成功
    AT_ERR_TIMEOUT,             // 超时
    AT_ERR_INVALID_PARAM,       // 无效参数
    AT_ERR_NOT_SUPPORTED,       // 不支持
    AT_ERR_SIM_NOT_READY,       // SIM卡未就绪
    AT_ERR_NETWORK_ERROR,       // 网络错误
    AT_ERR_CONNECTION_FAILED,   // 连接失败
    AT_ERR_SEND_FAILED,         // 发送失败
    AT_ERR_RECEIVE_FAILED,      // 接收失败
    AT_ERR_UNKNOWN              // 未知错误
} at_error_t;

/**
 * @brief  错误信息表
 */
static const char *error_messages[] = {
    "Success",
    "Timeout",
    "Invalid parameter",
    "Not supported",
    "SIM card not ready",
    "Network error",
    "Connection failed",
    "Send failed",
    "Receive failed",
    "Unknown error"
};

/**
 * @brief  获取错误信息
 * @param  error: 错误码
 * @return 错误信息字符串
 */
const char* at_get_error_message(at_error_t error)
{
    if (error < sizeof(error_messages) / sizeof(error_messages[0])) {
        return error_messages[error];
    }
    return "Invalid error code";
}

/**
 * @brief  错误恢复策略
 * @param  error: 错误码
 * @return 0: 成功恢复, -1: 无法恢复
 */
int at_error_recovery(at_error_t error)
{
    switch (error) {
        case AT_ERR_TIMEOUT:
            // 超时：清空缓冲区，重试
            at_uart_flush();
            at_clear_line_buffer();
            HAL_Delay(100);
            return 0;
            
        case AT_ERR_SIM_NOT_READY:
            // SIM卡未就绪：等待SIM卡初始化
            HAL_Delay(2000);
            return at_check_sim_status();
            
        case AT_ERR_NETWORK_ERROR:
            // 网络错误：重新注册网络
            return at_wait_network_registration(30000);
            
        case AT_ERR_CONNECTION_FAILED:
            // 连接失败：延迟后重试
            HAL_Delay(5000);
            return 0;
            
        default:
            return -1;  // 无法恢复
    }
}
```

### 9.2 超时处理

```c
/**
 * @brief  带超时重试的命令执行
 * @param  cmd: 命令字符串
 * @param  expected: 期望响应
 * @param  timeout_ms: 单次超时时间
 * @param  retry_count: 重试次数
 * @param  retry_delay_ms: 重试延迟
 * @return AT响应结果
 */
at_response_t at_execute_with_timeout_retry(const char *cmd, const char *expected,
                                             uint32_t timeout_ms, int retry_count,
                                             uint32_t retry_delay_ms)
{
    at_response_t result;
    
    for (int i = 0; i <= retry_count; i++) {
        // 执行命令
        result = at_execute_command(cmd, expected, timeout_ms);
        
        if (result == AT_RESP_OK) {
            return result;  // 成功
        }
        
        // 记录错误
        at_log(LOG_LEVEL_WARN, "Command failed (attempt %d/%d): %s", 
               i + 1, retry_count + 1, cmd);
        
        // 超时恢复
        if (result == AT_RESP_TIMEOUT) {
            at_error_recovery(AT_ERR_TIMEOUT);
        }
        
        // 延迟后重试
        if (i < retry_count) {
            HAL_Delay(retry_delay_ms);
        }
    }
    
    at_log(LOG_LEVEL_ERROR, "Command failed after %d attempts: %s", 
           retry_count + 1, cmd);
    
    return result;
}
```

### 9.3 故障诊断

```c
/**
 * @brief  诊断AT命令通信
 * @return 0: 正常, -1: 异常
 */
int at_diagnose(void)
{
    at_log(LOG_LEVEL_INFO, "Starting AT command diagnostics...");
    
    // 1. 测试基本通信
    at_log(LOG_LEVEL_INFO, "Testing basic communication...");
    if (!at_test()) {
        at_log(LOG_LEVEL_ERROR, "Basic communication failed");
        return -1;
    }
    at_log(LOG_LEVEL_INFO, "Basic communication OK");
    
    // 2. 查询模块信息
    at_log(LOG_LEVEL_INFO, "Querying module information...");
    char info[64];
    
    if (at_get_manufacturer(info, sizeof(info)) == 0) {
        at_log(LOG_LEVEL_INFO, "Manufacturer: %s", info);
    }
    
    if (at_get_model(info, sizeof(info)) == 0) {
        at_log(LOG_LEVEL_INFO, "Model: %s", info);
    }
    
    if (at_get_firmware_version(info, sizeof(info)) == 0) {
        at_log(LOG_LEVEL_INFO, "Firmware: %s", info);
    }
    
    // 3. 检查SIM卡（如果是GSM模块）
    at_log(LOG_LEVEL_INFO, "Checking SIM card...");
    if (at_check_sim_status() == 0) {
        at_log(LOG_LEVEL_INFO, "SIM card ready");
        
        if (at_get_imsi(info) == 0) {
            at_log(LOG_LEVEL_INFO, "IMSI: %s", info);
        }
    } else {
        at_log(LOG_LEVEL_WARN, "SIM card not ready");
    }
    
    // 4. 检查网络注册
    at_log(LOG_LEVEL_INFO, "Checking network registration...");
    network_status_t status;
    if (at_get_network_status(&status) == 0) {
        at_log(LOG_LEVEL_INFO, "Network status: %d", status);
        
        if (status == NET_REGISTERED_HOME || status == NET_REGISTERED_ROAMING) {
            // 查询信号强度
            int rssi, ber;
            if (at_get_signal_quality(&rssi, &ber) == 0) {
                at_log(LOG_LEVEL_INFO, "Signal: RSSI=%d (%d dBm), BER=%d", 
                       rssi, at_rssi_to_dbm(rssi), ber);
            }
        }
    }
    
    at_log(LOG_LEVEL_INFO, "Diagnostics completed");
    return 0;
}
```

### 9.4 常见问题解决

```
AT命令常见问题及解决方案：

1. 模块无响应
   原因：
   - 串口参数不匹配
   - 模块未上电或复位
   - 接线错误
   
   解决：
   - 检查波特率、数据位、停止位、校验位
   - 确认模块电源正常
   - 检查TX/RX是否交叉连接
   - 尝试不同波特率（9600, 115200等）

2. 响应乱码
   原因：
   - 波特率不匹配
   - 电平不匹配（TTL vs RS232）
   - 干扰
   
   解决：
   - 调整波特率
   - 使用电平转换芯片
   - 检查接地，缩短连线

3. 命令超时
   原因：
   - 超时时间设置过短
   - 模块处理慢
   - 网络延迟
   
   解决：
   - 增加超时时间
   - 添加重试机制
   - 检查网络状态

4. SIM卡错误
   原因：
   - SIM卡未插入
   - SIM卡接触不良
   - 需要PIN码
   
   解决：
   - 检查SIM卡安装
   - 清洁SIM卡触点
   - 输入正确PIN码

5. 网络注册失败
   原因：
   - 信号弱
   - SIM卡欠费
   - 运营商限制
   
   解决：
   - 改善天线位置
   - 检查SIM卡余额
   - 联系运营商

6. 连接失败
   原因：
   - 网络未注册
   - APN设置错误
   - 服务器地址错误
   
   解决：
   - 等待网络注册
   - 设置正确APN
   - 检查服务器地址和端口

7. 数据发送失败
   原因：
   - 连接已断开
   - 缓冲区满
   - 数据格式错误
   
   解决：
   - 检查连接状态
   - 等待缓冲区空闲
   - 检查数据格式

8. URC丢失
   原因：
   - 接收缓冲区溢出
   - 处理不及时
   
   解决：
   - 增大接收缓冲区
   - 使用中断接收
   - 及时处理URC
```

## 第十部分：最佳实践

### 10.1 设计原则

```
AT命令应用设计原则：

1. 模块化设计
   - 将AT命令功能封装成独立模块
   - 提供清晰的API接口
   - 便于移植和维护

2. 错误处理
   - 所有函数都应返回错误码
   - 实现完善的错误恢复机制
   - 记录详细的错误日志

3. 超时机制
   - 所有命令都应设置超时
   - 根据命令类型设置合理的超时时间
   - 实现超时重试机制

4. 状态管理
   - 维护模块状态机
   - 在执行命令前检查状态
   - 状态转换要有明确的条件

5. 资源管理
   - 合理分配缓冲区大小
   - 及时释放资源
   - 避免内存泄漏

6. 线程安全
   - 多线程环境下使用互斥锁
   - 避免竞态条件
   - 保证命令的原子性

7. 日志记录
   - 记录所有命令和响应
   - 记录错误和异常
   - 便于问题定位和调试
```

### 10.2 性能优化

```c
/**
 * @brief  批量命令执行
 * @param  commands: 命令数组
 * @param  count: 命令数量
 * @return 成功执行的命令数量
 */
int at_execute_batch(const char *commands[], int count)
{
    int success_count = 0;
    
    for (int i = 0; i < count; i++) {
        if (at_execute_command(commands[i], NULL, 1000) == AT_RESP_OK) {
            success_count++;
        } else {
            at_log(LOG_LEVEL_WARN, "Batch command %d failed: %s", i, commands[i]);
        }
    }
    
    return success_count;
}

/**
 * @brief  使用DMA提高传输效率
 */
void at_enable_dma(void)
{
    // 配置UART DMA接收
    HAL_UART_Receive_DMA(&huart2, rx_buffer, RX_BUFFER_SIZE);
}

/**
 * @brief  缓存常用响应
 */
typedef struct {
    char key[32];
    char value[128];
    uint32_t timestamp;
    uint32_t ttl;  // 生存时间（毫秒）
} cache_entry_t;

#define CACHE_SIZE  10
static cache_entry_t response_cache[CACHE_SIZE];

/**
 * @brief  从缓存获取响应
 * @param  key: 缓存键
 * @param  value: 输出值
 * @return 0: 命中, -1: 未命中
 */
int at_cache_get(const char *key, char *value)
{
    uint32_t current_time = HAL_GetTick();
    
    for (int i = 0; i < CACHE_SIZE; i++) {
        if (strcmp(response_cache[i].key, key) == 0) {
            // 检查是否过期
            if ((current_time - response_cache[i].timestamp) < response_cache[i].ttl) {
                strcpy(value, response_cache[i].value);
                return 0;  // 命中
            }
        }
    }
    
    return -1;  // 未命中
}

/**
 * @brief  添加响应到缓存
 * @param  key: 缓存键
 * @param  value: 缓存值
 * @param  ttl: 生存时间（毫秒）
 */
void at_cache_set(const char *key, const char *value, uint32_t ttl)
{
    static int cache_index = 0;
    
    strncpy(response_cache[cache_index].key, key, sizeof(response_cache[cache_index].key) - 1);
    strncpy(response_cache[cache_index].value, value, sizeof(response_cache[cache_index].value) - 1);
    response_cache[cache_index].timestamp = HAL_GetTick();
    response_cache[cache_index].ttl = ttl;
    
    cache_index = (cache_index + 1) % CACHE_SIZE;
}
```

### 10.3 安全考虑

```c
/**
 * @brief  输入验证
 * @param  input: 输入字符串
 * @return true: 有效, false: 无效
 */
bool at_validate_input(const char *input)
{
    // 检查空指针
    if (input == NULL) {
        return false;
    }
    
    // 检查长度
    size_t len = strlen(input);
    if (len == 0 || len > 256) {
        return false;
    }
    
    // 检查非法字符
    for (size_t i = 0; i < len; i++) {
        if (input[i] < 0x20 || input[i] > 0x7E) {
            // 非可打印ASCII字符
            if (input[i] != '\r' && input[i] != '\n') {
                return false;
            }
        }
    }
    
    return true;
}

/**
 * @brief  防止命令注入
 * @param  user_input: 用户输入
 * @param  safe_output: 安全输出
 * @param  max_len: 最大长度
 */
void at_sanitize_input(const char *user_input, char *safe_output, size_t max_len)
{
    size_t j = 0;
    
    for (size_t i = 0; user_input[i] != '\0' && j < max_len - 1; i++) {
        // 只允许字母、数字和部分符号
        if (isalnum(user_input[i]) || user_input[i] == '.' || 
            user_input[i] == '-' || user_input[i] == '_') {
            safe_output[j++] = user_input[i];
        }
    }
    
    safe_output[j] = '\0';
}
```


## 第十一部分：实战项目

### 11.1 项目一：GSM短信收发系统

```c
/**
 * @file    project_sms.c
 * @brief   GSM短信收发系统实现
 */

/**
 * @brief  SMS系统状态
 */
typedef enum {
    SMS_STATE_INIT,
    SMS_STATE_READY,
    SMS_STATE_ERROR
} sms_state_t;

static sms_state_t sms_state = SMS_STATE_INIT;

/**
 * @brief  初始化SMS系统
 * @return 0: 成功, -1: 失败
 */
int sms_system_init(void)
{
    at_log(LOG_LEVEL_INFO, "Initializing SMS system...");
    
    // 1. 初始化UART
    if (at_uart_init(115200) != HAL_OK) {
        at_log(LOG_LEVEL_ERROR, "UART initialization failed");
        return -1;
    }
    
    // 2. 测试AT命令
    if (!at_test()) {
        at_log(LOG_LEVEL_ERROR, "AT command test failed");
        return -1;
    }
    
    // 3. 关闭回显
    at_set_echo(false);
    
    // 4. 检查SIM卡
    if (at_check_sim_status() != 0) {
        at_log(LOG_LEVEL_ERROR, "SIM card not ready");
        return -1;
    }
    
    // 5. 等待网络注册
    at_log(LOG_LEVEL_INFO, "Waiting for network registration...");
    if (at_wait_network_registration(30000) != 0) {
        at_log(LOG_LEVEL_ERROR, "Network registration failed");
        return -1;
    }
    
    // 6. 设置短信格式为文本模式
    if (at_set_sms_format(true) != 0) {
        at_log(LOG_LEVEL_ERROR, "Failed to set SMS format");
        return -1;
    }
    
    // 7. 启用短信接收通知
    if (at_execute_command("AT+CNMI=2,1,0,0,0", NULL, 1000) != AT_RESP_OK) {
        at_log(LOG_LEVEL_ERROR, "Failed to enable SMS notification");
        return -1;
    }
    
    sms_state = SMS_STATE_READY;
    at_log(LOG_LEVEL_INFO, "SMS system initialized successfully");
    
    return 0;
}

/**
 * @brief  发送短信
 * @param  phone: 电话号码
 * @param  message: 短信内容
 * @return 0: 成功, -1: 失败
 */
int sms_send(const char *phone, const char *message)
{
    if (sms_state != SMS_STATE_READY) {
        at_log(LOG_LEVEL_ERROR, "SMS system not ready");
        return -1;
    }
    
    at_log(LOG_LEVEL_INFO, "Sending SMS to %s: %s", phone, message);
    
    if (at_send_sms(phone, message) == 0) {
        at_log(LOG_LEVEL_INFO, "SMS sent successfully");
        return 0;
    } else {
        at_log(LOG_LEVEL_ERROR, "Failed to send SMS");
        return -1;
    }
}

/**
 * @brief  处理接收到的短信
 * @param  urc: URC字符串
 * @param  len: 长度
 */
void handle_sms_received(const char *urc, uint16_t len)
{
    // 解析短信索引
    // +CMTI: "SM",1
    int index;
    if (sscanf(urc, "+CMTI: \"SM\",%d", &index) == 1) {
        at_log(LOG_LEVEL_INFO, "New SMS received at index %d", index);
        
        // 读取短信
        char phone[32];
        char message[256];
        
        if (at_read_sms(index, phone, message, sizeof(message)) == 0) {
            at_log(LOG_LEVEL_INFO, "SMS from %s: %s", phone, message);
            
            // 这里可以处理短信内容
            // 例如：解析命令、自动回复等
            
            // 删除已读短信
            at_delete_sms(index);
        }
    }
}

/**
 * @brief  SMS系统主循环
 */
void sms_system_loop(void)
{
    if (sms_state != SMS_STATE_READY) {
        return;
    }
    
    // 处理URC
    char line[256];
    if (at_read_line(line, sizeof(line), 100) > 0) {
        if (at_check_urc(line)) {
            // URC已被处理
        }
    }
}
```

### 11.2 项目二：WiFi数据上传系统

```c
/**
 * @file    project_wifi_upload.c
 * @brief   WiFi数据上传系统实现
 */

/**
 * @brief  WiFi上传系统配置
 */
typedef struct {
    char ssid[64];
    char password[64];
    char server_ip[32];
    int server_port;
    int upload_interval;  // 上传间隔（秒）
} wifi_upload_config_t;

static wifi_upload_config_t wifi_config = {
    .ssid = "MyWiFi",
    .password = "12345678",
    .server_ip = "192.168.1.100",
    .server_port = 8080,
    .upload_interval = 60
};

/**
 * @brief  初始化WiFi上传系统
 * @return 0: 成功, -1: 失败
 */
int wifi_upload_init(void)
{
    at_log(LOG_LEVEL_INFO, "Initializing WiFi upload system...");
    
    // 1. 初始化UART
    if (at_uart_init(115200) != HAL_OK) {
        return -1;
    }
    
    // 2. 测试AT命令
    if (!at_test()) {
        return -1;
    }
    
    // 3. 设置WiFi模式为Station
    if (at_wifi_set_mode(1) != 0) {
        return -1;
    }
    
    // 4. 连接WiFi
    at_log(LOG_LEVEL_INFO, "Connecting to WiFi: %s", wifi_config.ssid);
    if (at_wifi_connect(wifi_config.ssid, wifi_config.password) != 0) {
        at_log(LOG_LEVEL_ERROR, "WiFi connection failed");
        return -1;
    }
    
    // 5. 获取IP地址
    char ip[32];
    if (at_wifi_get_ip(ip, sizeof(ip)) == 0) {
        at_log(LOG_LEVEL_INFO, "IP address: %s", ip);
    }
    
    // 6. 设置多连接模式
    at_wifi_set_mux(true);
    
    at_log(LOG_LEVEL_INFO, "WiFi upload system initialized");
    return 0;
}

/**
 * @brief  上传传感器数据
 * @param  temperature: 温度
 * @param  humidity: 湿度
 * @return 0: 成功, -1: 失败
 */
int wifi_upload_sensor_data(float temperature, float humidity)
{
    char json_data[256];
    char response[512];
    int link_id = 0;
    
    // 1. 构建JSON数据
    snprintf(json_data, sizeof(json_data),
             "{\"temperature\":%.2f,\"humidity\":%.2f,\"timestamp\":%lu}",
             temperature, humidity, HAL_GetTick());
    
    at_log(LOG_LEVEL_INFO, "Uploading data: %s", json_data);
    
    // 2. 建立TCP连接
    if (at_wifi_connect_tcp(link_id, "TCP", wifi_config.server_ip, wifi_config.server_port) != 0) {
        at_log(LOG_LEVEL_ERROR, "Failed to connect to server");
        return -1;
    }
    
    // 3. 构建HTTP POST请求
    char http_request[512];
    snprintf(http_request, sizeof(http_request),
             "POST /api/data HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: %d\r\n"
             "\r\n"
             "%s",
             wifi_config.server_ip, strlen(json_data), json_data);
    
    // 4. 发送HTTP请求
    if (at_wifi_send_data(link_id, (uint8_t*)http_request, strlen(http_request)) != 0) {
        at_log(LOG_LEVEL_ERROR, "Failed to send data");
        at_wifi_close_connection(link_id);
        return -1;
    }
    
    // 5. 接收响应
    int recv_len = at_wifi_receive_data(link_id, (uint8_t*)response, sizeof(response) - 1, 5000);
    if (recv_len > 0) {
        response[recv_len] = '\0';
        at_log(LOG_LEVEL_INFO, "Server response: %s", response);
    }
    
    // 6. 关闭连接
    at_wifi_close_connection(link_id);
    
    at_log(LOG_LEVEL_INFO, "Data uploaded successfully");
    return 0;
}

/**
 * @brief  WiFi上传系统主循环
 */
void wifi_upload_loop(void)
{
    static uint32_t last_upload_time = 0;
    uint32_t current_time = HAL_GetTick();
    
    // 定时上传数据
    if ((current_time - last_upload_time) >= (wifi_config.upload_interval * 1000)) {
        // 读取传感器数据（示例）
        float temperature = 25.5;  // 实际应从传感器读取
        float humidity = 60.0;
        
        // 上传数据
        wifi_upload_sensor_data(temperature, humidity);
        
        last_upload_time = current_time;
    }
}
```

### 11.3 项目三：蓝牙透传系统

```c
/**
 * @file    project_bt_transparent.c
 * @brief   蓝牙透传系统实现
 */

/**
 * @brief  蓝牙透传状态
 */
typedef enum {
    BT_TRANS_DISCONNECTED,
    BT_TRANS_CONNECTED,
    BT_TRANS_DATA_MODE
} bt_trans_state_t;

static bt_trans_state_t bt_state = BT_TRANS_DISCONNECTED;

/**
 * @brief  初始化蓝牙透传系统
 * @return 0: 成功, -1: 失败
 */
int bt_transparent_init(void)
{
    at_log(LOG_LEVEL_INFO, "Initializing Bluetooth transparent transmission...");
    
    // 1. 进入AT命令模式
    if (at_bt_enter_at_mode() != 0) {
        return -1;
    }
    
    // 2. 设置蓝牙名称
    at_bt_set_name("BT_TRANS");
    
    // 3. 设置PIN码
    at_bt_set_pin("1234");
    
    // 4. 设置为从机模式
    at_bt_set_role(0);
    
    // 5. 设置串口参数（透传模式）
    at_bt_set_uart(9600, 0, 0);
    
    // 6. 复位模块，进入透传模式
    at_reset();
    
    // 重新初始化UART为透传波特率
    at_uart_init(9600);
    
    at_log(LOG_LEVEL_INFO, "Bluetooth transparent transmission initialized");
    return 0;
}

/**
 * @brief  蓝牙透传发送数据
 * @param  data: 数据指针
 * @param  len: 数据长度
 * @return 发送的字节数
 */
int bt_transparent_send(const uint8_t *data, uint16_t len)
{
    if (bt_state != BT_TRANS_DATA_MODE) {
        return -1;
    }
    
    return at_uart_send(data, len);
}

/**
 * @brief  蓝牙透传接收数据
 * @param  data: 数据缓冲区
 * @param  max_len: 最大长度
 * @return 接收的字节数
 */
int bt_transparent_receive(uint8_t *data, uint16_t max_len)
{
    if (bt_state != BT_TRANS_DATA_MODE) {
        return -1;
    }
    
    return at_uart_receive(data, max_len);
}

/**
 * @brief  蓝牙透传主循环
 */
void bt_transparent_loop(void)
{
    uint8_t buffer[256];
    
    // 检查是否有数据接收
    int len = bt_transparent_receive(buffer, sizeof(buffer));
    
    if (len > 0) {
        // 处理接收到的数据
        at_log(LOG_LEVEL_DEBUG, "Received %d bytes", len);
        
        // 回显数据（示例）
        bt_transparent_send(buffer, len);
    }
}
```

## 第十二部分：工具与资源

### 12.1 开发工具

```
AT命令开发常用工具：

1. 串口调试助手
   - SSCOM（Windows）
   - CoolTerm（跨平台）
   - PuTTY（跨平台）
   - minicom（Linux）
   
   功能：
   - 发送AT命令
   - 查看响应
   - 十六进制显示
   - 日志记录

2. AT命令测试工具
   - Tera Term（Windows）
   - RealTerm（Windows）
   - Serial Port Monitor（Windows）
   
   功能：
   - 脚本自动化
   - 时间戳
   - 数据分析

3. 网络调试工具
   - Packet Sender（跨平台）
   - SocketTest（Windows）
   - netcat（Linux）
   
   功能：
   - TCP/UDP测试
   - 数据收发
   - 服务器模拟

4. HTTP测试工具
   - Postman（跨平台）
   - curl（命令行）
   - HTTPie（命令行）
   
   功能：
   - HTTP请求测试
   - API调试
   - 响应分析
```

### 12.2 参考资料

```
AT命令参考资料：

1. 标准文档
   - ITU-T V.250: AT命令标准
   - 3GPP TS 27.007: GSM AT命令集
   - 3GPP TS 27.005: SMS AT命令集

2. 厂商文档
   - SIMCOM: SIM800/SIM900系列AT命令手册
   - Espressif: ESP8266/ESP32 AT命令手册
   - u-blox: SARA/TOBY系列AT命令手册
   - Quectel: EC20/EC25系列AT命令手册

3. 在线资源
   - AT Commands Reference: https://www.developershome.com/sms/
   - GSM Modem AT Commands: https://www.smssolutions.net/
   - ESP8266 AT Instruction Set: https://www.espressif.com/

4. 开源项目
   - TinyGSM: https://github.com/vshymanskyy/TinyGSM
   - ESP-AT: https://github.com/espressif/esp-at
   - AT Command Parser: https://github.com/ARMmbed/ATParser
```

## 总结

### 关键要点

1. **AT命令基础**
   - AT命令是基于ASCII文本的命令协议
   - 命令格式：AT+<cmd>[=<params>]
   - 响应类型：OK、ERROR、+CME ERROR、+CMS ERROR
   - URC是模块主动上报的信息

2. **UART通信**
   - 正确配置串口参数（波特率、数据位、停止位、校验位）
   - 使用中断接收提高效率
   - 实现环形缓冲区管理数据
   - 实现行缓冲处理AT命令

3. **命令解析**
   - 实现命令发送器
   - 实现响应解析器
   - 处理超时和重试
   - 区分命令响应和URC

4. **模块应用**
   - GSM模块：SIM卡管理、网络注册、短信收发、语音通话
   - WiFi模块：网络连接、TCP/IP通信、HTTP请求
   - 蓝牙模块：配对连接、数据传输、参数配置

5. **高级特性**
   - 命令队列提高效率
   - 多线程安全保护
   - 日志记录便于调试
   - 缓存优化性能

6. **错误处理**
   - 完善的错误码定义
   - 错误恢复策略
   - 超时重试机制
   - 故障诊断工具

7. **最佳实践**
   - 模块化设计
   - 输入验证
   - 安全考虑
   - 性能优化

### 学习路径

1. **入门阶段**
   - 学习AT命令基础知识
   - 使用串口工具手动发送AT命令
   - 理解命令格式和响应类型
   - 掌握基本的模块配置

2. **进阶阶段**
   - 实现UART通信和命令解析
   - 开发GSM/WiFi/蓝牙应用
   - 处理URC和异步事件
   - 实现错误处理和重试机制

3. **高级阶段**
   - 优化性能和资源使用
   - 实现多线程安全
   - 开发复杂的应用系统
   - 集成到实际产品中

### 下一步学习

- [TCP/IP协议栈](01-tcpip-stack.html) - 深入学习网络协议
- [MQTT协议](02-mqtt-protocol.html) - 学习物联网通信协议
- [Modbus协议](../intermediate/02-modbus-protocol.html) - 学习工业通信协议
- [UART驱动开发](../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-uart-driver.html) - 深入学习UART底层

## 参考资料

1. ITU-T Recommendation V.250: Serial asynchronous automatic dialling and control
2. 3GPP TS 27.007: AT command set for User Equipment (UE)
3. 3GPP TS 27.005: Use of Data Terminal Equipment - Data Circuit terminating Equipment (DTE-DCE) interface for Short Message Service (SMS)
4. SIMCOM SIM800 Series AT Command Manual
5. Espressif ESP8266 AT Instruction Set
6. HC-05 Bluetooth Module AT Command Reference
7. Quectel EC20 AT Commands Manual
8. u-blox AT Commands Manual

## 相关主题

- [TCP/IP协议栈基础](01-tcpip-stack.html)
- [MQTT协议应用](02-mqtt-protocol.html)
- [CoAP协议详解](03-coap-protocol.html)
- [HTTP/HTTPS通信](04-http-https.html)
- [Modbus协议实现](../intermediate/02-modbus-protocol.html)
- [UART硬件接口](../../../01-hardware-layer/06-communication-interface-hardware/beginner/01-uart-hardware.html)
- [UART驱动开发](../../../02-driver-bsp-layer/02-device-driver-development/beginner/01-uart-driver.html)

---

*本文档持续更新中，最后更新时间：2026-04-06*
