---
title: "WebSocket实时通信开发实战"
description: "深入学习WebSocket协议原理、双向通信机制和实时数据传输，通过ESP32实现WebSocket客户端和服务器，掌握物联网实时通信技术"
slug: "websocket-real-time-communication"

# 分类信息
domain: "通信与网络"
module: "网络协议"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - WebSocket
  - 实时通信
  - 双向通信
  - ESP32
  - Web技术
prerequisites:
  - "04-http-https"
related_contents: []

# 学习信息
estimated_time: 80
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
  - WebSocket协议
  - 实时通信
  - 双向数据传输
  - ESP32开发
  - Web实时应用
cover_image: ""
---

# WebSocket实时通信开发实战

## 学习目标

完成本教程后，你将能够：

- [ ] 理解WebSocket协议的工作原理和优势
- [ ] 掌握WebSocket握手过程和帧格式
- [ ] 了解WebSocket与HTTP的区别和联系
- [ ] 使用ESP32实现WebSocket客户端功能
- [ ] 使用ESP32搭建WebSocket服务器
- [ ] 实现设备与Web页面的实时双向通信

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉HTTP协议基础知识
- 了解TCP/IP网络编程
- 掌握C/C++编程语言
- 理解客户端-服务器架构

**技能要求**：
- 能够使用Arduino IDE或ESP-IDF开发ESP32
- 会配置WiFi网络连接
- 了解基本的HTML和JavaScript
- 熟悉JSON数据格式

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| ESP32开发板 | 1 | ESP32-DevKitC或类似型号 | - |
| DHT22温湿度传感器 | 1 | 可选，用于数据采集 | - |
| LED灯 | 2 | 用于演示远程控制 | - |
| 电阻 | 2 | 220Ω，LED限流电阻 | - |
| Micro USB数据线 | 1 | 用于供电和程序下载 | - |

### 软件准备

- **开发环境**：Arduino IDE 2.0+ 或 ESP-IDF v4.4+
- **WebSocket库**：ArduinoWebsockets (Arduino) 或 ESP-IDF WebSocket组件
- **Web浏览器**：Chrome、Firefox或Edge（支持WebSocket）
- **测试工具**：Postman或在线WebSocket测试工具

### 环境配置

#### 1. 安装Arduino IDE和ESP32支持

在Arduino IDE中添加ESP32开发板支持：
- 打开 文件 -> 首选项 -> 附加开发板管理器网址
- 添加URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`

#### 2. 安装WebSocket库

在Arduino IDE中：
- 打开 工具 -> 管理库
- 搜索 "ArduinoWebsockets"
- 选择 by Gil Maimon
- 点击安装

或使用ESP-IDF（已内置WebSocket支持）

#### 3. 测试WiFi连接

确保ESP32能够连接到WiFi网络。

## WebSocket协议基础

### 什么是WebSocket？

WebSocket是一种在单个TCP连接上进行全双工通信的协议，允许服务器主动向客户端推送数据。

**核心特点**：
- **全双工通信**：客户端和服务器可以同时发送和接收数据
- **持久连接**：建立连接后保持打开状态，无需重复握手
- **低延迟**：消息传输延迟低，适合实时应用
- **轻量级**：相比HTTP轮询，减少了大量的协议开销
- **跨域支持**：支持跨域通信（CORS）

### WebSocket vs HTTP

| 特性 | HTTP | WebSocket |
|------|------|-----------|
| 通信模式 | 请求-响应（单向） | 全双工（双向） |
| 连接方式 | 短连接（每次请求建立） | 长连接（持久） |
| 协议开销 | 每次请求都有完整HTTP头 | 握手后只有少量帧头 |
| 实时性 | 需要轮询，延迟高 | 主动推送，延迟低 |
| 服务器推送 | 不支持（需要长轮询） | 原生支持 |
| 适用场景 | 普通Web请求 | 实时应用、推送通知 |

### WebSocket握手过程

WebSocket使用HTTP升级机制建立连接：

```text
客户端请求（HTTP Upgrade）:
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

服务器响应:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**握手步骤**：
1. 客户端发送HTTP Upgrade请求
2. 服务器验证请求并返回101状态码
3. 连接升级为WebSocket协议
4. 开始双向数据传输

### WebSocket帧格式

WebSocket使用帧（Frame）进行数据传输：

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

**帧类型（opcode）**：
- `0x0`：继续帧
- `0x1`：文本帧
- `0x2`：二进制帧
- `0x8`：关闭连接
- `0x9`：Ping
- `0xA`：Pong

## 步骤1：ESP32 WebSocket客户端

### 1.1 创建Arduino项目

创建新的Arduino项目：`ESP32_WebSocket_Client`

### 1.2 基础配置和连接

```c
#include <WiFi.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

// WiFi配置
const char* ssid = "你的WiFi名称";
const char* password = "你的WiFi密码";

// WebSocket服务器地址
const char* websocket_server = "ws://echo.websocket.org";  // 测试服务器

// 创建WebSocket客户端
WebsocketsClient client;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    // 连接WiFi
    Serial.print("连接WiFi: ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    
    // 设置WebSocket回调函数
    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);
    
    // 连接到WebSocket服务器
    Serial.println("连接到WebSocket服务器...");
    bool connected = client.connect(websocket_server);
    
    if (connected) {
        Serial.println("WebSocket连接成功!");
        client.send("Hello from ESP32!");
    } else {
        Serial.println("WebSocket连接失败!");
    }
}
```

**代码说明**：
- `ArduinoWebsockets.h`：WebSocket库头文件
- `websocket_server`：WebSocket服务器地址，使用`ws://`协议
- `client.onMessage()`：设置消息接收回调
- `client.onEvent()`：设置事件回调
- `client.connect()`：连接到服务器

### 1.3 消息接收回调函数

```c
// WebSocket消息接收回调
void onMessageCallback(WebsocketsMessage message) {
    Serial.print("收到消息: ");
    Serial.println(message.data());
    
    // 判断消息类型
    if (message.isText()) {
        Serial.println("消息类型: 文本");
    } else if (message.isBinary()) {
        Serial.println("消息类型: 二进制");
        Serial.print("数据长度: ");
        Serial.println(message.length());
    }
}

// WebSocket事件回调
void onEventsCallback(WebsocketsEvent event, String data) {
    switch (event) {
        case WebsocketsEvent::ConnectionOpened:
            Serial.println("事件: 连接已建立");
            break;
        case WebsocketsEvent::ConnectionClosed:
            Serial.println("事件: 连接已关闭");
            break;
        case WebsocketsEvent::GotPing:
            Serial.println("事件: 收到Ping");
            break;
        case WebsocketsEvent::GotPong:
            Serial.println("事件: 收到Pong");
            break;
    }
}
```

**回调函数说明**：
- `onMessageCallback`：处理接收到的消息
- `message.data()`：获取消息内容
- `message.isText()`：判断是否为文本消息
- `onEventsCallback`：处理连接事件

### 1.4 主循环和消息发送

```c
void loop() {
    // 保持WebSocket连接活跃
    client.poll();
    
    // 每5秒发送一次消息
    static unsigned long lastSend = 0;
    unsigned long now = millis();
    
    if (now - lastSend > 5000) {
        lastSend = now;
        
        if (client.available()) {
            // 构建JSON消息
            String message = "{";
            message += "\"device\":\"ESP32\",";
            message += "\"timestamp\":" + String(millis()) + ",";
            message += "\"temperature\":" + String(random(20, 30)) + ",";
            message += "\"humidity\":" + String(random(40, 80));
            message += "}";
            
            Serial.print("发送消息: ");
            Serial.println(message);
            client.send(message);
        } else {
            Serial.println("WebSocket未连接，尝试重连...");
            client.connect(websocket_server);
        }
    }
}
```

**主循环说明**：
- `client.poll()`：必须定期调用，处理接收消息和保持连接
- `client.available()`：检查连接状态
- `client.send()`：发送消息到服务器
- 每5秒发送一次模拟的传感器数据

## 步骤2：ESP32 WebSocket服务器

### 2.1 创建WebSocket服务器项目

创建新项目：`ESP32_WebSocket_Server`

### 2.2 服务器基础代码

```c
#include <WiFi.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

// WiFi配置
const char* ssid = "你的WiFi名称";
const char* password = "你的WiFi密码";

// 创建WebSocket服务器（端口80）
WebsocketsServer server;

// LED引脚
const int LED_PIN = 2;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    // 初始化LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // 连接WiFi
    Serial.print("连接WiFi: ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
    
    // 启动WebSocket服务器
    server.listen(80);
    Serial.println("WebSocket服务器已启动");
    Serial.println("连接地址: ws://" + WiFi.localIP().toString() + "/");
}
```

**服务器配置说明**：
- `WebsocketsServer server`：创建服务器对象
- `server.listen(80)`：在80端口监听连接
- 服务器地址格式：`ws://IP地址/`

### 2.3 处理客户端连接

```c
void loop() {
    // 检查是否有新的客户端连接
    WebsocketsClient client = server.accept();
    
    if (client.available()) {
        Serial.println("新客户端已连接");
        
        // 设置消息回调
        client.onMessage([](WebsocketsMessage message) {
            Serial.print("收到消息: ");
            Serial.println(message.data());
            
            // 解析JSON命令
            String data = message.data();
            
            if (data.indexOf("\"led\":\"on\"") > 0) {
                digitalWrite(LED_PIN, HIGH);
                Serial.println("LED已打开");
                
                // 发送响应
                client.send("{\"status\":\"ok\",\"led\":\"on\"}");
            } 
            else if (data.indexOf("\"led\":\"off\"") > 0) {
                digitalWrite(LED_PIN, LOW);
                Serial.println("LED已关闭");
                
                // 发送响应
                client.send("{\"status\":\"ok\",\"led\":\"off\"}");
            }
            else if (data.indexOf("\"action\":\"status\"") > 0) {
                // 返回设备状态
                String status = "{";
                status += "\"device\":\"ESP32\",";
                status += "\"led\":" + String(digitalRead(LED_PIN) ? "\"on\"" : "\"off\"") + ",";
                status += "\"uptime\":" + String(millis() / 1000) + ",";
                status += "\"freeHeap\":" + String(ESP.getFreeHeap());
                status += "}";
                
                client.send(status);
            }
        });
        
        // 设置事件回调
        client.onEvent([](WebsocketsEvent event, String data) {
            if (event == WebsocketsEvent::ConnectionClosed) {
                Serial.println("客户端已断开");
            }
        });
        
        // 发送欢迎消息
        client.send("{\"message\":\"Welcome to ESP32 WebSocket Server\"}");
        
        // 保持连接
        while (client.available()) {
            client.poll();
            delay(10);
        }
    }
}
```

**服务器处理逻辑**：
- `server.accept()`：接受新的客户端连接
- 为每个客户端设置消息和事件回调
- 解析JSON命令并执行相应操作
- 发送响应消息给客户端
- 使用`client.poll()`保持连接活跃

## 步骤3：创建Web控制界面

### 3.1 HTML页面结构

创建文件：`websocket_client.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 WebSocket控制面板</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .status {
            padding: 10px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .connected {
            background-color: #4CAF50;
            color: white;
        }
        .disconnected {
            background-color: #f44336;
            color: white;
        }
        .control-panel {
            margin: 20px 0;
        }
        button {
            padding: 15px 30px;
            margin: 10px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn-on {
            background-color: #4CAF50;
            color: white;
        }
        .btn-off {
            background-color: #f44336;
            color: white;
        }
        .btn-status {
            background-color: #2196F3;
            color: white;
        }
        button:hover {
            opacity: 0.8;
        }
        #messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 20px 0;
            background-color: #f9f9f9;
            font-family: monospace;
            font-size: 14px;
        }
        .message {
            margin: 5px 0;
            padding: 5px;
        }
        .sent {
            color: #2196F3;
        }
        .received {
            color: #4CAF50;
        }
        .error {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 WebSocket控制面板</h1>
        
        <div id="status" class="status disconnected">未连接</div>
        
        <div class="control-panel">
            <input type="text" id="serverUrl" placeholder="ws://192.168.1.100/" 
                   style="width: 300px; padding: 10px; margin: 10px;">
            <button onclick="connect()" class="btn-status">连接</button>
            <button onclick="disconnect()" class="btn-off">断开</button>
        </div>
        
        <div class="control-panel">
            <button onclick="sendCommand('on')" class="btn-on">打开LED</button>
            <button onclick="sendCommand('off')" class="btn-off">关闭LED</button>
            <button onclick="getStatus()" class="btn-status">获取状态</button>
        </div>
        
        <div id="messages"></div>
    </div>
</body>
</html>
```

### 3.2 JavaScript WebSocket客户端

在HTML文件的`</body>`标签前添加：

```html
<script>
    let ws = null;
    const messagesDiv = document.getElementById('messages');
    const statusDiv = document.getElementById('status');
    
    // 连接到WebSocket服务器
    function connect() {
        const url = document.getElementById('serverUrl').value;
        
        if (!url) {
            addMessage('请输入服务器地址', 'error');
            return;
        }
        
        try {
            ws = new WebSocket(url);
            
            // 连接打开事件
            ws.onopen = function(event) {
                addMessage('WebSocket连接已建立', 'received');
                updateStatus(true);
            };
            
            // 接收消息事件
            ws.onmessage = function(event) {
                addMessage('收到: ' + event.data, 'received');
                
                // 解析JSON响应
                try {
                    const data = JSON.parse(event.data);
                    if (data.led) {
                        addMessage('LED状态: ' + data.led, 'received');
                    }
                } catch (e) {
                    // 非JSON消息
                }
            };
            
            // 连接关闭事件
            ws.onclose = function(event) {
                addMessage('WebSocket连接已关闭', 'error');
                updateStatus(false);
            };
            
            // 错误事件
            ws.onerror = function(error) {
                addMessage('WebSocket错误: ' + error, 'error');
                updateStatus(false);
            };
            
        } catch (error) {
            addMessage('连接失败: ' + error, 'error');
        }
    }
    
    // 断开连接
    function disconnect() {
        if (ws) {
            ws.close();
            ws = null;
        }
    }
    
    // 发送LED控制命令
    function sendCommand(action) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addMessage('未连接到服务器', 'error');
            return;
        }
        
        const command = {
            led: action
        };
        
        const message = JSON.stringify(command);
        ws.send(message);
        addMessage('发送: ' + message, 'sent');
    }
    
    // 获取设备状态
    function getStatus() {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addMessage('未连接到服务器', 'error');
            return;
        }
        
        const command = {
            action: 'status'
        };
        
        const message = JSON.stringify(command);
        ws.send(message);
        addMessage('发送: ' + message, 'sent');
    }
    
    // 添加消息到显示区域
    function addMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message ' + type;
        messageElement.textContent = new Date().toLocaleTimeString() + ' - ' + message;
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    // 更新连接状态显示
    function updateStatus(connected) {
        if (connected) {
            statusDiv.textContent = '已连接';
            statusDiv.className = 'status connected';
        } else {
            statusDiv.textContent = '未连接';
            statusDiv.className = 'status disconnected';
        }
    }
</script>
```

**JavaScript代码说明**：
- `new WebSocket(url)`：创建WebSocket连接
- `ws.onopen`：连接建立时触发
- `ws.onmessage`：接收到消息时触发
- `ws.onclose`：连接关闭时触发
- `ws.onerror`：发生错误时触发
- `ws.send()`：发送消息到服务器
- `ws.readyState`：连接状态（OPEN、CLOSED等）

## 步骤4：实时数据监控系统

### 4.1 ESP32传感器数据推送

修改服务器代码，添加定时推送功能：

```c
// 全局变量
WebsocketsClient connectedClient;
bool clientConnected = false;
unsigned long lastPush = 0;

void loop() {
    // 接受新连接
    if (!clientConnected) {
        connectedClient = server.accept();
        if (connectedClient.available()) {
            Serial.println("新客户端已连接");
            clientConnected = true;
            
            // 设置回调
            connectedClient.onMessage(handleMessage);
            connectedClient.onEvent(handleEvent);
            
            // 发送欢迎消息
            connectedClient.send("{\"message\":\"Connected to ESP32\"}");
        }
    }
    
    // 处理已连接的客户端
    if (clientConnected) {
        connectedClient.poll();
        
        // 每2秒推送一次传感器数据
        unsigned long now = millis();
        if (now - lastPush > 2000) {
            lastPush = now;
            pushSensorData();
        }
    }
}

// 推送传感器数据
void pushSensorData() {
    if (!clientConnected) return;
    
    // 读取传感器数据（这里使用模拟数据）
    float temperature = 20.0 + random(0, 100) / 10.0;
    float humidity = 50.0 + random(0, 300) / 10.0;
    int rssi = WiFi.RSSI();
    
    // 构建JSON数据
    String data = "{";
    data += "\"type\":\"sensor\",";
    data += "\"temperature\":" + String(temperature, 1) + ",";
    data += "\"humidity\":" + String(humidity, 1) + ",";
    data += "\"rssi\":" + String(rssi) + ",";
    data += "\"uptime\":" + String(millis() / 1000);
    data += "}";
    
    // 发送数据
    connectedClient.send(data);
    Serial.println("推送数据: " + data);
}

// 消息处理函数
void handleMessage(WebsocketsMessage message) {
    Serial.print("收到消息: ");
    Serial.println(message.data());
    
    String data = message.data();
    
    // 解析并处理命令
    if (data.indexOf("\"led\":\"on\"") > 0) {
        digitalWrite(LED_PIN, HIGH);
        connectedClient.send("{\"status\":\"ok\",\"led\":\"on\"}");
    } 
    else if (data.indexOf("\"led\":\"off\"") > 0) {
        digitalWrite(LED_PIN, LOW);
        connectedClient.send("{\"status\":\"ok\",\"led\":\"off\"}");
    }
}

// 事件处理函数
void handleEvent(WebsocketsEvent event, String data) {
    if (event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("客户端已断开");
        clientConnected = false;
    }
}
```

### 4.2 Web页面实时图表

在HTML中添加Chart.js库和实时图表：

```html
<!-- 在head中添加Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- 在container中添加图表容器 -->
<div style="margin: 20px 0;">
    <canvas id="temperatureChart" width="400" height="200"></canvas>
</div>

<script>
    // 图表配置
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '温度 (°C)',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.1
            }, {
                label: '湿度 (%)',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            animation: {
                duration: 0
            }
        }
    });
    
    // 修改onmessage处理函数
    ws.onmessage = function(event) {
        addMessage('收到: ' + event.data, 'received');
        
        try {
            const data = JSON.parse(event.data);
            
            // 处理传感器数据
            if (data.type === 'sensor') {
                updateChart(data);
            }
            
            // 处理LED状态
            if (data.led) {
                addMessage('LED状态: ' + data.led, 'received');
            }
        } catch (e) {
            // 非JSON消息
        }
    };
    
    // 更新图表
    function updateChart(data) {
        const time = new Date().toLocaleTimeString();
        
        // 添加新数据
        chart.data.labels.push(time);
        chart.data.datasets[0].data.push(data.temperature);
        chart.data.datasets[1].data.push(data.humidity);
        
        // 保持最多20个数据点
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }
        
        // 更新图表
        chart.update();
    }
</script>
```

**实时图表说明**：
- 使用Chart.js库绘制折线图
- 接收到传感器数据时自动更新图表
- 保持最近20个数据点
- 显示温度和湿度两条曲线

## 步骤5：安全WebSocket (WSS)

### 5.1 生成自签名证书

使用OpenSSL生成证书（在电脑上执行）：

```bash
# 生成私钥
openssl genrsa -out server_key.pem 2048

# 生成证书签名请求
openssl req -new -key server_key.pem -out server_csr.pem

# 生成自签名证书（有效期365天）
openssl x509 -req -days 365 -in server_csr.pem -signkey server_key.pem -out server_cert.pem
```

### 5.2 ESP32 WSS服务器

```c
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoWebsockets.h>

// 证书和私钥（需要转换为C字符串格式）
const char* server_cert = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDXTCCAkWgAwIBAgIJAKL0UG+mRKSzMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n" \
"...\n" \
"-----END CERTIFICATE-----\n";

const char* server_key = \
"-----BEGIN RSA PRIVATE KEY-----\n" \
"MIIEpAIBAAKCAQEAyLqkXvPvXvJmOvCBJvZqZjGvXvJmOvCBJvZqZjGvXvJmOvCB\n" \
"...\n" \
"-----END RSA PRIVATE KEY-----\n";

WebsocketsServer secureServer;

void setup() {
    // ... WiFi连接代码 ...
    
    // 配置SSL证书
    secureServer.setCertificate(server_cert);
    secureServer.setPrivateKey(server_key);
    
    // 启动安全服务器（端口443）
    secureServer.listen(443);
    Serial.println("WSS服务器已启动");
    Serial.println("连接地址: wss://" + WiFi.localIP().toString() + "/");
}
```

**WSS配置说明**：
- 使用`wss://`协议（WebSocket Secure）
- 默认端口443
- 需要SSL证书和私钥
- 数据传输加密，更安全

### 5.3 Web客户端连接WSS

```javascript
// 连接到安全WebSocket服务器
function connectSecure() {
    const url = 'wss://192.168.1.100/';  // 使用wss协议
    
    try {
        ws = new WebSocket(url);
        // ... 其他代码相同 ...
    } catch (error) {
        console.error('连接失败:', error);
    }
}
```

**注意事项**：
- 浏览器会验证证书
- 自签名证书需要手动信任
- 生产环境建议使用CA签发的证书

## 步骤6：多客户端管理

### 6.1 服务器端多客户端支持

```c
#include <vector>

// 客户端列表
std::vector<WebsocketsClient> clients;
const int MAX_CLIENTS = 5;

void loop() {
    // 接受新连接
    WebsocketsClient newClient = server.accept();
    if (newClient.available()) {
        if (clients.size() < MAX_CLIENTS) {
            Serial.println("新客户端已连接");
            Serial.print("当前客户端数量: ");
            Serial.println(clients.size() + 1);
            
            // 设置回调
            newClient.onMessage([](WebsocketsMessage message) {
                handleClientMessage(message);
            });
            
            newClient.onEvent([](WebsocketsEvent event, String data) {
                if (event == WebsocketsEvent::ConnectionClosed) {
                    Serial.println("客户端断开");
                }
            });
            
            // 添加到客户端列表
            clients.push_back(newClient);
            
            // 发送欢迎消息
            newClient.send("{\"message\":\"Connected\",\"clientId\":" + 
                          String(clients.size()) + "}");
        } else {
            Serial.println("客户端数量已达上限");
            newClient.send("{\"error\":\"Server full\"}");
            newClient.close();
        }
    }
    
    // 处理所有已连接的客户端
    for (int i = 0; i < clients.size(); i++) {
        if (clients[i].available()) {
            clients[i].poll();
        } else {
            // 移除断开的客户端
            clients.erase(clients.begin() + i);
            i--;
            Serial.println("移除断开的客户端");
        }
    }
    
    // 定时广播数据
    static unsigned long lastBroadcast = 0;
    if (millis() - lastBroadcast > 2000) {
        lastBroadcast = millis();
        broadcastSensorData();
    }
}

// 广播消息到所有客户端
void broadcastSensorData() {
    if (clients.empty()) return;
    
    // 构建传感器数据
    String data = "{";
    data += "\"type\":\"sensor\",";
    data += "\"temperature\":" + String(20.0 + random(0, 100) / 10.0, 1) + ",";
    data += "\"humidity\":" + String(50.0 + random(0, 300) / 10.0, 1) + ",";
    data += "\"timestamp\":" + String(millis());
    data += "}";
    
    // 发送给所有客户端
    for (auto& client : clients) {
        if (client.available()) {
            client.send(data);
        }
    }
    
    Serial.println("广播数据到 " + String(clients.size()) + " 个客户端");
}

// 处理客户端消息
void handleClientMessage(WebsocketsMessage message) {
    Serial.print("收到消息: ");
    Serial.println(message.data());
    
    // 解析命令并广播给所有客户端
    String response = "{\"broadcast\":true,\"message\":\"" + 
                     message.data() + "\"}";
    
    for (auto& client : clients) {
        if (client.available()) {
            client.send(response);
        }
    }
}
```

**多客户端管理说明**：
- 使用`std::vector`存储客户端连接
- 限制最大客户端数量
- 定期清理断开的连接
- 支持广播消息到所有客户端
- 每个客户端独立处理

## 步骤7：心跳和断线重连

### 7.1 客户端心跳机制

```c
// 客户端代码
unsigned long lastPing = 0;
const unsigned long PING_INTERVAL = 30000;  // 30秒

void loop() {
    if (client.available()) {
        client.poll();
        
        // 发送心跳
        unsigned long now = millis();
        if (now - lastPing > PING_INTERVAL) {
            lastPing = now;
            client.ping();
            Serial.println("发送Ping");
        }
    } else {
        // 断线重连
        Serial.println("连接断开，尝试重连...");
        delay(5000);
        reconnect();
    }
}

// 重连函数
void reconnect() {
    int retries = 0;
    const int MAX_RETRIES = 5;
    
    while (retries < MAX_RETRIES) {
        Serial.print("重连尝试 ");
        Serial.print(retries + 1);
        Serial.print("/");
        Serial.println(MAX_RETRIES);
        
        if (client.connect(websocket_server)) {
            Serial.println("重连成功!");
            return;
        }
        
        retries++;
        delay(5000);
    }
    
    Serial.println("重连失败，请检查网络");
}
```

### 7.2 服务器端超时检测

```c
// 为每个客户端添加最后活动时间
struct ClientInfo {
    WebsocketsClient client;
    unsigned long lastActivity;
};

std::vector<ClientInfo> clientInfos;
const unsigned long CLIENT_TIMEOUT = 60000;  // 60秒超时

void loop() {
    // ... 接受新连接代码 ...
    
    // 检查客户端超时
    unsigned long now = millis();
    for (int i = 0; i < clientInfos.size(); i++) {
        if (now - clientInfos[i].lastActivity > CLIENT_TIMEOUT) {
            Serial.println("客户端超时，关闭连接");
            clientInfos[i].client.close();
            clientInfos.erase(clientInfos.begin() + i);
            i--;
        } else if (clientInfos[i].client.available()) {
            clientInfos[i].client.poll();
        }
    }
}

// 在消息回调中更新活动时间
void handleMessage(WebsocketsMessage message, int clientIndex) {
    clientInfos[clientIndex].lastActivity = millis();
    // ... 处理消息 ...
}
```

**心跳机制说明**：
- 客户端定期发送Ping帧
- 服务器自动响应Pong帧
- 检测超时并关闭无响应连接
- 客户端断线后自动重连

## 故障排除

### 问题1：无法建立WebSocket连接

**可能原因**：
- WiFi未连接
- 服务器地址或端口错误
- 防火墙阻止连接
- 协议不匹配（ws vs wss）

**解决方法**：
1. 检查WiFi连接状态和IP地址
2. 确认服务器地址格式：`ws://IP:端口/`
3. 检查防火墙设置
4. 确保客户端和服务器使用相同协议

### 问题2：连接频繁断开

**可能原因**：
- WiFi信号不稳定
- 没有实现心跳机制
- 服务器资源不足
- 消息处理阻塞

**解决方法**：
1. 改善WiFi信号质量
2. 实现Ping/Pong心跳
3. 增加服务器内存
4. 避免在回调中执行耗时操作

### 问题3：消息发送失败

**可能原因**：
- 连接未建立
- 消息过大
- 发送速度过快
- 缓冲区溢出

**解决方法**：
1. 检查`client.available()`状态
2. 分片发送大消息
3. 控制发送频率
4. 增加缓冲区大小

### 问题4：Web页面无法连接

**可能原因**：
- 浏览器不支持WebSocket
- CORS跨域问题
- 证书验证失败（WSS）
- URL格式错误

**解决方法**：
1. 使用现代浏览器（Chrome、Firefox）
2. 检查浏览器控制台错误信息
3. 信任自签名证书
4. 确认URL格式正确

### 问题5：数据接收延迟

**可能原因**：
- 网络延迟
- 未及时调用`poll()`
- 消息队列积压
- 处理逻辑耗时

**解决方法**：
1. 优化网络环境
2. 在loop()中频繁调用`poll()`
3. 异步处理消息
4. 优化消息处理代码

## 总结

通过本教程，你学习了：

- ✅ WebSocket协议的核心概念和工作原理
- ✅ WebSocket与HTTP的区别和优势
- ✅ ESP32 WebSocket客户端的完整开发
- ✅ ESP32 WebSocket服务器的实现
- ✅ Web页面与ESP32的实时双向通信
- ✅ 实时数据监控和可视化
- ✅ 安全WebSocket (WSS) 的配置
- ✅ 多客户端管理和消息广播
- ✅ 心跳机制和断线重连

**关键要点**：
- WebSocket提供全双工实时通信能力
- 适合需要低延迟、高频率数据交换的场景
- 服务器可以主动推送数据到客户端
- 需要实现心跳机制保持连接活跃
- 生产环境建议使用WSS加密传输

## 性能优化建议

### 1. 消息压缩

对于大量数据传输，可以使用压缩：

```c
// 使用简化的JSON格式
// 不推荐: {"temperature":25.5,"humidity":60.2}
// 推荐: {"t":25.5,"h":60.2}

// 或使用二进制格式
uint8_t data[8];
memcpy(data, &temperature, 4);
memcpy(data + 4, &humidity, 4);
client.sendBinary((char*)data, 8);
```

### 2. 批量发送

将多个小消息合并为一个大消息：

```c
String batch = "[";
for (int i = 0; i < 10; i++) {
    if (i > 0) batch += ",";
    batch += "{\"sensor\":" + String(i) + ",\"value\":" + String(readSensor(i)) + "}";
}
batch += "]";
client.send(batch);
```

### 3. 选择性推送

只在数据变化时推送：

```c
float lastTemp = 0;
const float THRESHOLD = 0.5;

void loop() {
    float temp = readTemperature();
    if (abs(temp - lastTemp) > THRESHOLD) {
        pushData(temp);
        lastTemp = temp;
    }
}
```

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现消息确认机制（ACK）
   - 客户端发送消息后等待服务器确认
   - 超时未收到确认则重发
   - 使用消息ID追踪

2. **挑战2**：添加用户认证功能
   - 连接时验证用户名和密码
   - 使用Token进行身份验证
   - 不同用户有不同权限

3. **挑战3**：实现房间/频道功能
   - 客户端可以加入不同的房间
   - 消息只发送给同一房间的客户端
   - 支持房间列表和用户列表

4. **挑战4**：开发移动App客户端
   - 使用React Native或Flutter
   - 实现与ESP32的实时通信
   - 添加推送通知功能

5. **挑战5**：实现文件传输功能
   - 通过WebSocket传输文件
   - 支持断点续传
   - 显示传输进度

## 应用场景

WebSocket在嵌入式系统中的典型应用：

### 1. 智能家居控制
- 实时控制灯光、空调等设备
- 传感器数据实时显示
- 设备状态同步

### 2. 工业监控
- 设备运行状态监控
- 报警信息实时推送
- 生产数据可视化

### 3. 机器人控制
- 远程操控机器人
- 视频流传输
- 传感器数据反馈

### 4. 游戏手柄
- 低延迟控制信号
- 实时位置追踪
- 多人协作

### 5. 数据采集系统
- 高频数据采集
- 实时数据分析
- 异常检测和告警

## 完整代码

完整的项目代码可以在GitHub上找到：

```text
GitHub仓库: https://github.com/embedded-knowledge/websocket-esp32-tutorial
```

项目包含：
- ESP32 WebSocket客户端完整代码
- ESP32 WebSocket服务器完整代码
- Web控制面板HTML/JavaScript代码
- 实时图表示例
- 多客户端管理示例
- WSS安全连接示例

## 下一步

建议继续学习：

- Modbus工业协议实战 - 学习工业通信协议
- CAN总线协议应用 - 学习汽车和工业总线
- OPC UA工业互联协议 - 学习工业4.0通信标准
- AWS IoT平台接入 - 学习云平台集成

## 参考资料

1. WebSocket协议规范 (RFC 6455) - https://tools.ietf.org/html/rfc6455
2. ArduinoWebsockets库文档 - https://github.com/gilmaimon/ArduinoWebsockets
3. ESP-IDF WebSocket组件 - https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/protocols/esp_websocket_client.html
4. MDN WebSocket API - https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
5. WebSocket.org - https://www.websocket.org/
6. Chart.js文档 - https://www.chartjs.org/docs/latest/

## WebSocket vs 其他协议对比

| 协议 | 实时性 | 双向通信 | 开销 | 复杂度 | 适用场景 |
|------|--------|----------|------|--------|----------|
| WebSocket | 高 | 是 | 低 | 中 | 实时应用、推送 |
| HTTP | 低 | 否 | 高 | 低 | 普通Web请求 |
| MQTT | 高 | 是 | 低 | 中 | IoT设备通信 |
| CoAP | 中 | 是 | 极低 | 中 | 资源受限设备 |
| SSE | 中 | 否 | 中 | 低 | 服务器推送 |

## 常见WebSocket术语

- **Frame**：WebSocket数据帧，最小传输单位
- **Opcode**：操作码，标识帧类型
- **Payload**：有效载荷，实际传输的数据
- **Masking**：掩码，客户端发送的数据必须掩码
- **Ping/Pong**：心跳帧，用于保持连接活跃
- **Close Frame**：关闭帧，用于优雅关闭连接
- **Handshake**：握手，HTTP升级到WebSocket的过程
- **Upgrade**：协议升级，从HTTP切换到WebSocket

## 最佳实践

1. **连接管理**
   - 实现自动重连机制
   - 设置合理的超时时间
   - 限制最大连接数

2. **消息处理**
   - 使用JSON格式便于解析
   - 添加消息类型字段
   - 实现消息确认机制

3. **错误处理**
   - 捕获所有异常
   - 记录详细日志
   - 提供友好的错误提示

4. **安全性**
   - 生产环境使用WSS
   - 实现身份验证
   - 验证消息来源

5. **性能优化**
   - 控制消息发送频率
   - 使用二进制格式传输大数据
   - 实现消息压缩

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

