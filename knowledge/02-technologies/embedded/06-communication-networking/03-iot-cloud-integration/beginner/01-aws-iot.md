---
title: "AWS IoT Core平台接入实战"
description: "深入学习AWS IoT Core云平台，掌握设备注册、证书认证、MQTT通信、设备影子服务和规则引擎，实现ESP32设备与AWS云端的安全连接和数据交互"
slug: "aws-iot-core-platform-integration"

# 分类信息
domain: "通信与网络"
module: "IoT平台与云集成"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - AWS IoT
  - 云平台
  - 设备接入
  - MQTT
  - 设备影子
  - ESP32
prerequisites:
  - "02-mqtt-protocol"
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
  - AWS IoT Core
  - 物联网云平台
  - 设备证书认证
  - 设备影子
  - 规则引擎
cover_image: ""
---

# AWS IoT Core平台接入实战

## 学习目标

完成本教程后，你将能够：

- [ ] 理解AWS IoT Core的核心概念和架构
- [ ] 掌握AWS IoT设备注册和证书管理
- [ ] 使用ESP32通过MQTT连接到AWS IoT Core
- [ ] 实现设备影子（Device Shadow）功能
- [ ] 配置AWS IoT规则引擎进行数据处理

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解MQTT协议基础知识
- 熟悉C语言编程
- 理解JSON数据格式
- 了解基本的云计算概念

**技能要求**：
- 能够使用Arduino IDE或ESP-IDF开发ESP32
- 会配置WiFi网络连接
- 有AWS账号（可使用免费套餐）

**账号准备**：
- AWS账号（注册地址：https://aws.amazon.com/）
- 信用卡（用于账号验证，免费套餐不收费）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| ESP32开发板 | 1 | ESP32-DevKitC或类似型号 | - |
| DHT11温湿度传感器 | 1 | 用于数据采集 | - |
| LED灯 | 2 | 用于演示远程控制 | - |
| 电阻 | 2 | 220Ω，LED限流电阻 | - |
| Micro USB数据线 | 1 | 用于供电和程序下载 | - |

### 软件准备

- **开发环境**：Arduino IDE 2.0+ 或 ESP-IDF v4.4+
- **AWS IoT库**：
  - Arduino: `AWS_IOT` by Evandro Copercini
  - ESP-IDF: 内置AWS IoT SDK组件
- **证书工具**：OpenSSL（用于证书格式转换）
- **AWS CLI**：可选，用于命令行管理

### AWS IoT Core免费套餐

AWS IoT Core提供12个月免费套餐：
- 每月250,000条消息（发布或传递）
- 每月500,000分钟连接时间
- 每月225,000次规则触发
- 每月250,000次设备影子操作

**注意**：超出免费额度后会产生费用，建议设置账单告警。

## AWS IoT Core基础概念

### 什么是AWS IoT Core？

AWS IoT Core是亚马逊提供的托管云服务，让连接的设备能够轻松安全地与云应用程序和其他设备交互。

**核心特点**：
- **安全连接**：基于X.509证书的双向认证
- **设备影子**：设备状态的虚拟副本，支持离线操作
- **规则引擎**：实时处理和路由设备数据
- **设备注册表**：集中管理设备元数据
- **高可用性**：自动扩展，支持数十亿设备

### AWS IoT Core架构

```mermaid
graph TB
    A[ESP32设备] -->|MQTT/TLS| B[AWS IoT Core]
    B --> C[设备影子]
    B --> D[规则引擎]
    D --> E[Lambda函数]
    D --> F[DynamoDB]
    D --> G[S3存储]
    D --> H[SNS通知]
    B --> I[设备注册表]
```

### 核心组件

**1. 设备注册表（Thing Registry）**
- 存储设备的元数据和属性
- 管理设备证书和策略
- 支持设备分组和类型定义

**2. 设备影子（Device Shadow）**
- 设备状态的JSON文档
- 支持设备离线时的状态同步
- 包含reported（设备上报）和desired（期望状态）

**3. 消息代理（Message Broker）**
- 基于MQTT 3.1.1协议
- 支持QoS 0和QoS 1
- 提供发布/订阅功能

**4. 规则引擎（Rules Engine）**
- 使用SQL语法处理消息
- 将数据路由到AWS服务
- 支持数据转换和过滤

## 步骤1：创建AWS IoT设备

### 1.1 登录AWS控制台

1. 访问 https://console.aws.amazon.com/
2. 登录你的AWS账号
3. 在服务搜索框中输入"IoT Core"
4. 选择"AWS IoT Core"服务
5. 选择你的区域（建议选择离你最近的区域，如ap-northeast-1东京）

### 1.2 创建IoT Thing（设备）

1. 在左侧菜单选择"管理" -> "所有设备" -> "物品"
2. 点击"创建物品"按钮
3. 选择"创建单个物品"
4. 填写物品属性：
   - 物品名称：`ESP32_Device_001`
   - 物品类型：可选，暂不设置
   - 物品组：可选，暂不设置
5. 点击"下一步"

### 1.3 配置设备证书

选择"自动生成新证书（推荐）"：

1. 点击"下一步"
2. 创建策略（如果还没有）：
   - 点击"创建策略"
   - 策略名称：`ESP32_Policy`
   - 策略文档：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:ap-northeast-1:*:client/ESP32_*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Publish",
      "Resource": "arn:aws:iot:ap-northeast-1:*:topic/esp32/*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:ap-northeast-1:*:topicfilter/esp32/*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Receive",
      "Resource": "arn:aws:iot:ap-northeast-1:*:topic/esp32/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:UpdateThingShadow",
        "iot:GetThingShadow"
      ],
      "Resource": "arn:aws:iot:ap-northeast-1:*:thing/ESP32_*"
    }
  ]
}
```

**策略说明**：
- `iot:Connect`：允许设备连接
- `iot:Publish`：允许发布到esp32/*主题
- `iot:Subscribe`：允许订阅esp32/*主题
- `iot:Receive`：允许接收消息
- `iot:UpdateThingShadow`：允许更新设备影子
- `iot:GetThingShadow`：允许获取设备影子

3. 选择刚创建的策略
4. 点击"创建物品"

### 1.4 下载证书文件

创建成功后，会显示证书下载页面，**必须立即下载**以下文件：

1. **设备证书**：`xxxxxxxxxx-certificate.pem.crt`
2. **私钥**：`xxxxxxxxxx-private.pem.key`
3. **根CA证书**：点击"下载"链接下载Amazon Root CA 1

**重要**：私钥只能下载一次，请妥善保存！

### 1.5 获取AWS IoT端点

1. 在左侧菜单选择"设置"
2. 找到"设备数据端点"
3. 复制端点地址，格式类似：`xxxxxxxxxxxxxx-ats.iot.ap-northeast-1.amazonaws.com`
4. 记录此端点，后续代码中会使用

**预期结果**：
- 成功创建IoT Thing
- 下载了3个证书文件
- 获取了AWS IoT端点地址

## 步骤2：准备ESP32开发环境

### 2.1 安装Arduino库

在Arduino IDE中安装以下库：

1. **WiFiClientSecure**：ESP32内置，用于TLS连接
2. **PubSubClient**：MQTT客户端库
3. **ArduinoJson**：JSON解析库

安装方法：
- 打开 工具 -> 管理库
- 搜索并安装 "PubSubClient" 和 "ArduinoJson"

### 2.2 准备证书文件

将下载的证书转换为C语言字符串格式：

#### 方法1：使用在线工具
访问 https://tomeko.net/online_tools/file_to_hex.php 转换

#### 方法2：使用Python脚本

创建 `convert_cert.py`：

```python
import sys

def convert_to_c_string(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # 转换为C字符串格式
    lines = content.split('\n')
    c_string = 'const char* cert = \n'
    for line in lines:
        if line:
            c_string += f'  "{line}\\n"\n'
    c_string += '  "\\n";'
    
    return c_string

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_cert.py <certificate_file>")
        sys.exit(1)
    
    result = convert_to_c_string(sys.argv[1])
    print(result)
```

使用方法：
```bash
python convert_cert.py certificate.pem.crt > certificate.h
python convert_cert.py private.pem.key > private_key.h
python convert_cert.py AmazonRootCA1.pem > root_ca.h
```

### 2.3 创建证书头文件

创建 `secrets.h` 文件，包含所有证书：

```c
#ifndef SECRETS_H
#define SECRETS_H

// WiFi配置
const char* WIFI_SSID = "你的WiFi名称";
const char* WIFI_PASSWORD = "你的WiFi密码";

// AWS IoT端点
const char* AWS_IOT_ENDPOINT = "xxxxxxxxxxxxxx-ats.iot.ap-northeast-1.amazonaws.com";

// 设备证书
const char AWS_CERT_CRT[] = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUXXXXXXXXXXXXXXXXXXXXXXXXXXX...
（此处粘贴完整的设备证书内容）
-----END CERTIFICATE-----
)EOF";

// 私钥
const char AWS_CERT_PRIVATE[] = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX...
（此处粘贴完整的私钥内容）
-----END RSA PRIVATE KEY-----
)EOF";

// Amazon Root CA 1
const char AWS_CERT_CA[] = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----
)EOF";

#endif
```

**安全提示**：
- 不要将此文件上传到公共代码仓库
- 使用`.gitignore`排除此文件
- 生产环境应使用安全存储方案

## 步骤3：实现基础AWS IoT连接

### 3.1 创建Arduino项目

创建新项目：`ESP32_AWS_IoT_Basic`

### 3.2 包含必要的库

```c
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

// MQTT主题定义
#define AWS_IOT_PUBLISH_TOPIC   "esp32/sensor/data"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/control/led"

// LED引脚
const int LED_PIN = 2;

// 创建客户端对象
WiFiClientSecure net;
PubSubClient client(net);
```

### 3.3 WiFi连接函数

```c
void connectWiFi() {
    Serial.print("连接到WiFi: ");
    Serial.println(WIFI_SSID);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
}
```

### 3.4 AWS IoT连接函数

```c
void connectAWS() {
    // 配置WiFiClientSecure使用AWS IoT证书
    net.setCACert(AWS_CERT_CA);
    net.setCertificate(AWS_CERT_CRT);
    net.setPrivateKey(AWS_CERT_PRIVATE);
    
    // 连接到AWS IoT MQTT代理
    client.setServer(AWS_IOT_ENDPOINT, 8883);
    client.setCallback(messageHandler);
    
    Serial.print("连接到AWS IoT...");
    
    while (!client.connected()) {
        // 使用设备名称作为客户端ID
        if (client.connect("ESP32_Device_001")) {
            Serial.println("已连接!");
            
            // 订阅控制主题
            client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
            Serial.print("已订阅主题: ");
            Serial.println(AWS_IOT_SUBSCRIBE_TOPIC);
        } else {
            Serial.print("连接失败, 错误代码=");
            Serial.print(client.state());
            Serial.println(" 5秒后重试");
            delay(5000);
        }
    }
}
```

**连接说明**：
- 使用8883端口（MQTT over TLS）
- 设置CA证书、设备证书和私钥
- 客户端ID必须与Thing名称匹配或符合策略规则

### 3.5 消息处理回调函数

```c
void messageHandler(char* topic, byte* payload, unsigned int length) {
    Serial.print("收到消息 [");
    Serial.print(topic);
    Serial.print("]: ");
    
    // 将payload转换为字符串
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);
    
    // 解析JSON消息
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("JSON解析失败: ");
        Serial.println(error.c_str());
        return;
    }
    
    // 处理LED控制命令
    if (doc.containsKey("led")) {
        String ledState = doc["led"];
        if (ledState == "ON") {
            digitalWrite(LED_PIN, HIGH);
            Serial.println("LED已打开");
        } else if (ledState == "OFF") {
            digitalWrite(LED_PIN, LOW);
            Serial.println("LED已关闭");
        }
    }
}
```

### 3.6 发布传感器数据

```c
void publishMessage() {
    // 创建JSON文档
    StaticJsonDocument<200> doc;
    doc["device"] = "ESP32_Device_001";
    doc["temperature"] = 25.5 + random(-50, 50) / 10.0;
    doc["humidity"] = 60.0 + random(-100, 100) / 10.0;
    doc["timestamp"] = millis();
    
    // 序列化为字符串
    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    
    // 发布消息
    Serial.print("发布消息: ");
    Serial.println(jsonBuffer);
    
    if (client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer)) {
        Serial.println("消息发布成功");
    } else {
        Serial.println("消息发布失败");
    }
}
```

### 3.7 主程序

```c
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    // 初始化LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // 连接WiFi
    connectWiFi();
    
    // 连接AWS IoT
    connectAWS();
    
    Serial.println("初始化完成");
}

void loop() {
    // 保持MQTT连接
    if (!client.connected()) {
        connectAWS();
    }
    client.loop();
    
    // 每10秒发布一次数据
    static unsigned long lastPublish = 0;
    unsigned long now = millis();
    
    if (now - lastPublish > 10000) {
        lastPublish = now;
        publishMessage();
    }
}
```

## 步骤4：测试AWS IoT连接

### 4.1 编译和上传

1. 确保`secrets.h`文件配置正确
2. 选择开发板：ESP32 Dev Module
3. 选择端口
4. 点击上传
5. 打开串口监视器（波特率115200）

**预期输出**：
```
连接到WiFi: YourWiFi
.....
WiFi连接成功
IP地址: 192.168.1.100
连接到AWS IoT...已连接!
已订阅主题: esp32/control/led
初始化完成
发布消息: {"device":"ESP32_Device_001","temperature":25.3,"humidity":62.5,"timestamp":10234}
消息发布成功
```

### 4.2 使用AWS IoT控制台测试

#### 测试消息接收：

1. 在AWS IoT控制台，选择"测试" -> "MQTT测试客户端"
2. 在"订阅主题"标签页：
   - 主题筛选条件：`esp32/sensor/data`
   - 点击"订阅"
3. 观察ESP32发送的消息

#### 测试远程控制：

1. 在"发布到主题"标签页：
   - 主题名称：`esp32/control/led`
   - 消息负载：
   ```json
   {
     "led": "ON"
   }
   ```
2. 点击"发布"
3. 观察ESP32的LED是否点亮
4. 发送`{"led": "OFF"}`测试关闭

**预期结果**：
- 能在控制台看到ESP32发送的数据
- 能通过控制台控制ESP32的LED

## 步骤5：实现设备影子功能

### 5.1 什么是设备影子？

设备影子（Device Shadow）是设备状态的JSON文档，包含：
- **reported**：设备上报的实际状态
- **desired**：应用程序期望的状态
- **delta**：desired和reported之间的差异

### 5.2 设备影子主题

AWS IoT为每个Thing自动创建影子主题：

```text
更新影子: $aws/things/ESP32_Device_001/shadow/update
获取影子: $aws/things/ESP32_Device_001/shadow/get
影子更新接受: $aws/things/ESP32_Device_001/shadow/update/accepted
影子更新拒绝: $aws/things/ESP32_Device_001/shadow/update/rejected
影子delta: $aws/things/ESP32_Device_001/shadow/update/delta
```

### 5.3 添加影子主题定义

```c
// 设备影子主题
#define THING_NAME "ESP32_Device_001"
#define AWS_IOT_SHADOW_UPDATE "$aws/things/" THING_NAME "/shadow/update"
#define AWS_IOT_SHADOW_UPDATE_ACCEPTED "$aws/things/" THING_NAME "/shadow/update/accepted"
#define AWS_IOT_SHADOW_UPDATE_REJECTED "$aws/things/" THING_NAME "/shadow/update/rejected"
#define AWS_IOT_SHADOW_UPDATE_DELTA "$aws/things/" THING_NAME "/shadow/update/delta"
#define AWS_IOT_SHADOW_GET "$aws/things/" THING_NAME "/shadow/get"
```

### 5.4 订阅影子主题

修改`connectAWS()`函数：

```c
void connectAWS() {
    // ... 前面的代码保持不变 ...
    
    if (client.connect("ESP32_Device_001")) {
        Serial.println("已连接!");
        
        // 订阅控制主题
        client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
        
        // 订阅影子主题
        client.subscribe(AWS_IOT_SHADOW_UPDATE_ACCEPTED);
        client.subscribe(AWS_IOT_SHADOW_UPDATE_REJECTED);
        client.subscribe(AWS_IOT_SHADOW_UPDATE_DELTA);
        
        Serial.println("已订阅所有主题");
        
        // 获取当前影子状态
        client.publish(AWS_IOT_SHADOW_GET, "");
    }
    // ... 后面的代码保持不变 ...
}
```

### 5.5 处理影子Delta消息

修改`messageHandler()`函数：

```c
void messageHandler(char* topic, byte* payload, unsigned int length) {
    Serial.print("收到消息 [");
    Serial.print(topic);
    Serial.print("]: ");
    
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);
    
    // 解析JSON
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("JSON解析失败: ");
        Serial.println(error.c_str());
        return;
    }
    
    // 处理影子Delta消息
    if (String(topic) == AWS_IOT_SHADOW_UPDATE_DELTA) {
        Serial.println("收到影子Delta更新");
        
        // 检查LED状态变化
        if (doc["state"].containsKey("led")) {
            String ledState = doc["state"]["led"];
            bool newLedState = (ledState == "ON");
            
            digitalWrite(LED_PIN, newLedState ? HIGH : LOW);
            Serial.print("LED状态更新为: ");
            Serial.println(ledState);
            
            // 上报新状态到影子
            updateShadowReported(newLedState);
        }
    }
    // 处理影子更新接受
    else if (String(topic) == AWS_IOT_SHADOW_UPDATE_ACCEPTED) {
        Serial.println("影子更新成功");
    }
    // 处理影子更新拒绝
    else if (String(topic) == AWS_IOT_SHADOW_UPDATE_REJECTED) {
        Serial.println("影子更新被拒绝");
    }
    // 处理普通控制消息
    else if (String(topic) == AWS_IOT_SUBSCRIBE_TOPIC) {
        if (doc.containsKey("led")) {
            String ledState = doc["led"];
            digitalWrite(LED_PIN, (ledState == "ON") ? HIGH : LOW);
        }
    }
}
```

### 5.6 更新设备影子

```c
void updateShadowReported(bool ledState) {
    // 创建影子更新文档
    StaticJsonDocument<512> doc;
    JsonObject state = doc.createNestedObject("state");
    JsonObject reported = state.createNestedObject("reported");
    
    reported["led"] = ledState ? "ON" : "OFF";
    reported["temperature"] = 25.5;
    reported["humidity"] = 60.0;
    reported["timestamp"] = millis();
    
    // 序列化
    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    
    // 发布到影子更新主题
    Serial.print("更新设备影子: ");
    Serial.println(jsonBuffer);
    client.publish(AWS_IOT_SHADOW_UPDATE, jsonBuffer);
}
```

### 5.7 定期上报状态

在`loop()`函数中添加：

```c
void loop() {
    // ... 保持连接的代码 ...
    
    // 每30秒更新一次影子
    static unsigned long lastShadowUpdate = 0;
    unsigned long now = millis();
    
    if (now - lastShadowUpdate > 30000) {
        lastShadowUpdate = now;
        
        bool currentLedState = digitalRead(LED_PIN);
        updateShadowReported(currentLedState);
    }
    
    // ... 其他代码 ...
}
```

### 5.8 测试设备影子

#### 在AWS控制台查看影子：

1. 进入AWS IoT控制台
2. 选择"管理" -> "所有设备" -> "物品"
3. 点击"ESP32_Device_001"
4. 选择"设备影子"标签页
5. 查看"经典影子"

**影子文档示例**：
```json
{
  "state": {
    "reported": {
      "led": "OFF",
      "temperature": 25.5,
      "humidity": 60.0,
      "timestamp": 123456
    }
  },
  "metadata": {
    "reported": {
      "led": {
        "timestamp": 1709876543
      }
    }
  },
  "version": 5,
  "timestamp": 1709876543
}
```

#### 通过影子控制设备：

1. 在影子页面点击"编辑"
2. 添加desired状态：
```json
{
  "state": {
    "desired": {
      "led": "ON"
    }
  }
}
```
3. 点击"更新"
4. 观察ESP32的LED是否点亮
5. 查看影子文档，reported应该更新为"ON"

## 步骤6：配置AWS IoT规则引擎

### 6.1 什么是规则引擎？

规则引擎允许你：
- 使用SQL语法查询和过滤消息
- 将数据路由到其他AWS服务
- 转换和处理数据
- 触发Lambda函数

### 6.2 创建规则：保存数据到DynamoDB

#### 创建DynamoDB表：

1. 打开DynamoDB控制台
2. 点击"创建表"
3. 表名称：`ESP32_SensorData`
4. 分区键：`device_id`（字符串）
5. 排序键：`timestamp`（数字）
6. 点击"创建表"

#### 创建IoT规则：

1. 返回AWS IoT控制台
2. 选择"消息路由" -> "规则"
3. 点击"创建规则"
4. 规则名称：`SaveSensorDataToDynamoDB`
5. SQL语句：

```sql
SELECT 
  device as device_id,
  temperature,
  humidity,
  timestamp
FROM 'esp32/sensor/data'
WHERE temperature > 20
```

6. 添加操作：
   - 选择"DynamoDB"
   - 表名：`ESP32_SensorData`
   - 分区键值：`${device_id}`
   - 排序键值：`${timestamp}`
   - 创建新角色或选择现有角色
7. 点击"创建"

**规则说明**：
- 只保存温度大于20°C的数据
- 自动将消息字段映射到DynamoDB列
- 使用`${}`语法引用消息字段

### 6.3 创建规则：温度告警

#### 创建SNS主题：

1. 打开SNS控制台
2. 创建主题：`ESP32_TemperatureAlert`
3. 创建订阅：
   - 协议：Email
   - 端点：你的邮箱地址
4. 确认订阅邮件

#### 创建告警规则：

1. 在IoT控制台创建新规则
2. 规则名称：`TemperatureAlert`
3. SQL语句：

```sql
SELECT 
  device,
  temperature,
  timestamp
FROM 'esp32/sensor/data'
WHERE temperature > 30
```

4. 添加操作：
   - 选择"SNS"
   - SNS主题：`ESP32_TemperatureAlert`
   - 消息格式：RAW
   - 创建或选择角色
5. 点击"创建"

**测试告警**：
修改ESP32代码，发送温度>30的数据，检查是否收到邮件。

### 6.4 创建规则：数据转换

创建规则将摄氏度转换为华氏度：

```sql
SELECT 
  device,
  temperature as temp_celsius,
  (temperature * 9/5 + 32) as temp_fahrenheit,
  humidity,
  timestamp
FROM 'esp32/sensor/data'
```

操作：发布到新主题`esp32/sensor/data/converted`

### 6.5 查看规则执行情况

1. 在规则详情页面，选择"指标"标签
2. 查看：
   - 规则触发次数
   - 成功执行次数
   - 失败次数
3. 在CloudWatch中查看详细日志

## 步骤7：添加真实传感器

### 7.1 连接DHT11传感器

```c
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
    // ... 其他初始化 ...
    dht.begin();
}
```

### 7.2 读取真实数据

```c
void publishMessage() {
    // 读取传感器
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    // 检查读取是否成功
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("读取DHT传感器失败!");
        return;
    }
    
    // 创建JSON
    StaticJsonDocument<200> doc;
    doc["device"] = THING_NAME;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["timestamp"] = millis();
    
    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    
    // 发布
    Serial.print("发布消息: ");
    Serial.println(jsonBuffer);
    client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
    
    // 同时更新影子
    updateShadowReported(digitalRead(LED_PIN));
}
```

## 故障排除

### 问题1：无法连接到AWS IoT

**可能原因**：
- 证书配置错误
- 端点地址错误
- 策略权限不足
- 时间不同步

**解决方法**：
1. 检查证书是否完整（包含BEGIN和END行）
2. 确认端点地址正确
3. 检查策略是否允许连接
4. 使用NTP同步时间：

```c
#include <time.h>

void syncTime() {
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    Serial.print("等待NTP时间同步: ");
    time_t now = time(nullptr);
    while (now < 8 * 3600 * 2) {
        delay(500);
        Serial.print(".");
        now = time(nullptr);
    }
    Serial.println("\n时间同步完成");
}

// 在setup()中调用
void setup() {
    // ...
    connectWiFi();
    syncTime();  // 在连接AWS之前同步时间
    connectAWS();
}
```

### 问题2：消息发布失败

**可能原因**：
- 主题权限不足
- 消息过大
- 连接不稳定

**解决方法**：
1. 检查策略中的Publish权限
2. 减小消息大小或增加缓冲区
3. 添加重试机制：

```c
bool publishWithRetry(const char* topic, const char* payload, int maxRetries = 3) {
    for (int i = 0; i < maxRetries; i++) {
        if (client.publish(topic, payload)) {
            return true;
        }
        Serial.print("发布失败，重试 ");
        Serial.println(i + 1);
        delay(1000);
    }
    return false;
}
```

### 问题3：设备影子更新失败

**可能原因**：
- JSON格式错误
- 影子权限不足
- 版本冲突

**解决方法**：
1. 验证JSON格式
2. 检查策略中的UpdateThingShadow权限
3. 使用正确的影子文档结构

### 问题4：规则引擎不触发

**可能原因**：
- SQL语句错误
- 主题不匹配
- 角色权限不足

**解决方法**：
1. 在规则中启用错误日志
2. 使用MQTT测试客户端验证消息格式
3. 检查IAM角色权限
4. 查看CloudWatch日志

## 总结

通过本教程，你学习了：

- ✅ AWS IoT Core的核心概念和架构
- ✅ 创建和配置IoT Thing和证书
- ✅ 使用ESP32通过TLS连接到AWS IoT
- ✅ 实现设备影子功能进行状态同步
- ✅ 配置规则引擎处理和路由数据
- ✅ 集成真实传感器采集数据

**关键要点**：
- AWS IoT使用X.509证书进行双向认证
- 设备影子实现设备状态的云端同步
- 规则引擎提供强大的数据处理能力
- 策略控制设备的访问权限
- 时间同步对TLS连接至关重要

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现OTA固件更新功能
2. **挑战2**：使用AWS IoT Jobs进行远程配置
3. **挑战3**：集成Amazon Timestream存储时序数据
4. **挑战4**：使用Lambda函数处理设备数据
5. **挑战5**：实现设备群组管理和批量控制

## 安全最佳实践

### 1. 证书管理

- **不要硬编码证书**：生产环境使用安全存储（如ESP32的NVS加密存储）
- **定期轮换证书**：设置证书过期时间并定期更新
- **使用证书吊销**：发现泄露立即吊销证书
- **最小权限原则**：策略只授予必要的权限

### 2. 网络安全

- **始终使用TLS**：使用8883端口，不使用1883
- **验证服务器证书**：确保连接到正确的AWS端点
- **使用VPN**：敏感环境考虑使用VPN
- **防火墙规则**：限制出站连接

### 3. 设备安全

- **安全启动**：启用ESP32的安全启动功能
- **固件加密**：加密存储的固件
- **调试接口保护**：生产环境禁用调试接口
- **看门狗定时器**：防止设备挂起

### 4. 数据安全

- **敏感数据加密**：传输前加密敏感数据
- **数据完整性**：使用HMAC验证数据完整性
- **访问控制**：使用IAM策略控制数据访问
- **审计日志**：启用CloudTrail记录所有操作

## 成本优化

### 免费套餐限制

- 消息数：250,000条/月
- 连接时间：500,000分钟/月
- 规则触发：225,000次/月
- 影子操作：250,000次/月

### 优化建议

1. **减少消息频率**：
   - 使用合理的上报间隔（如5-10分钟）
   - 只在数据变化时上报
   - 批量发送多个数据点

2. **优化连接**：
   - 使用持久会话
   - 合理设置Keep-Alive时间
   - 避免频繁重连

3. **规则优化**：
   - 使用WHERE子句过滤不必要的数据
   - 合并多个规则
   - 使用批处理

4. **监控使用量**：
   - 设置CloudWatch告警
   - 定期检查账单
   - 使用AWS Cost Explorer分析成本

## 完整代码

完整的项目代码可以在GitHub上找到：

```text
GitHub仓库: https://github.com/embedded-knowledge/aws-iot-esp32-tutorial
```

项目包含：
- 基础AWS IoT连接代码
- 设备影子实现
- DHT11传感器集成
- 规则引擎示例
- 安全配置示例

## 下一步

建议继续学习：

- Azure IoT平台应用 - 学习微软云IoT服务
- 阿里云IoT平台开发 - 学习国内云平台
- AWS IoT Greengrass - 学习边缘计算
- AWS IoT Analytics - 学习数据分析

## 参考资料

1. AWS IoT Core开发者指南 - https://docs.aws.amazon.com/iot/latest/developerguide/
2. AWS IoT Device SDK for Embedded C - https://github.com/aws/aws-iot-device-sdk-embedded-C
3. ESP32 AWS IoT示例 - https://github.com/espressif/esp-aws-iot
4. AWS IoT策略文档 - https://docs.aws.amazon.com/iot/latest/developerguide/iot-policies.html
5. AWS IoT设备影子服务 - https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html
6. AWS IoT规则引擎 - https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html
7. AWS IoT安全最佳实践 - https://docs.aws.amazon.com/iot/latest/developerguide/security-best-practices.html
8. AWS IoT定价 - https://aws.amazon.com/iot-core/pricing/

## 常见AWS IoT术语

- **Thing**：IoT设备在AWS中的虚拟表示
- **Thing Type**：设备类型，用于分组相似设备
- **Thing Group**：设备组，用于批量管理
- **Certificate**：X.509证书，用于设备认证
- **Policy**：访问策略，定义设备权限
- **Device Shadow**：设备影子，设备状态的JSON文档
- **Rule**：规则，用于处理和路由消息
- **Action**：规则触发的操作
- **Topic**：MQTT主题，用于消息路由
- **Message Broker**：消息代理，处理MQTT通信
- **Registry**：注册表，存储设备元数据
- **Job**：作业，用于远程管理设备

## AWS IoT与其他平台对比

| 特性 | AWS IoT Core | Azure IoT Hub | 阿里云IoT |
|------|--------------|---------------|-----------|
| 认证方式 | X.509证书 | 证书/SAS令牌 | 证书/密钥 |
| 协议支持 | MQTT, HTTPS, WebSocket | MQTT, AMQP, HTTPS | MQTT, CoAP, HTTPS |
| 设备影子 | Device Shadow | Device Twin | 物模型 |
| 规则引擎 | SQL语法 | 路由查询 | 规则引擎 |
| 边缘计算 | Greengrass | IoT Edge | Link Edge |
| 定价模式 | 按消息数 | 按消息数 | 按消息数 |
| 免费套餐 | 12个月 | 永久免费层 | 有限免费 |
| 区域支持 | 全球多区域 | 全球多区域 | 主要在中国 |

## 附录：完整示例代码

### 完整的ESP32 AWS IoT代码

```c
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <time.h>
#include "secrets.h"

// 硬件配置
#define LED_PIN 2
#define DHTPIN 4
#define DHTTYPE DHT11

// MQTT主题
#define AWS_IOT_PUBLISH_TOPIC   "esp32/sensor/data"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/control/led"
#define THING_NAME "ESP32_Device_001"
#define AWS_IOT_SHADOW_UPDATE "$aws/things/" THING_NAME "/shadow/update"
#define AWS_IOT_SHADOW_UPDATE_DELTA "$aws/things/" THING_NAME "/shadow/update/delta"

// 对象实例
WiFiClientSecure net;
PubSubClient client(net);
DHT dht(DHTPIN, DHTTYPE);

// 函数声明
void connectWiFi();
void syncTime();
void connectAWS();
void messageHandler(char* topic, byte* payload, unsigned int length);
void publishMessage();
void updateShadowReported(bool ledState);

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    dht.begin();
    
    connectWiFi();
    syncTime();
    connectAWS();
    
    Serial.println("初始化完成");
}

void loop() {
    if (!client.connected()) {
        connectAWS();
    }
    client.loop();
    
    static unsigned long lastPublish = 0;
    unsigned long now = millis();
    
    if (now - lastPublish > 10000) {
        lastPublish = now;
        publishMessage();
    }
}

void connectWiFi() {
    Serial.print("连接到WiFi: ");
    Serial.println(WIFI_SSID);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi连接成功");
    Serial.print("IP地址: ");
    Serial.println(WiFi.localIP());
}

void syncTime() {
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    Serial.print("等待NTP时间同步: ");
    time_t now = time(nullptr);
    while (now < 8 * 3600 * 2) {
        delay(500);
        Serial.print(".");
        now = time(nullptr);
    }
    Serial.println("\n时间同步完成");
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    Serial.print("当前时间: ");
    Serial.println(asctime(&timeinfo));
}

void connectAWS() {
    net.setCACert(AWS_CERT_CA);
    net.setCertificate(AWS_CERT_CRT);
    net.setPrivateKey(AWS_CERT_PRIVATE);
    
    client.setServer(AWS_IOT_ENDPOINT, 8883);
    client.setCallback(messageHandler);
    
    Serial.print("连接到AWS IoT...");
    
    while (!client.connected()) {
        if (client.connect(THING_NAME)) {
            Serial.println("已连接!");
            client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
            client.subscribe(AWS_IOT_SHADOW_UPDATE_DELTA);
            Serial.println("已订阅所有主题");
        } else {
            Serial.print("连接失败, rc=");
            Serial.print(client.state());
            Serial.println(" 5秒后重试");
            delay(5000);
        }
    }
}

void messageHandler(char* topic, byte* payload, unsigned int length) {
    Serial.print("收到消息 [");
    Serial.print(topic);
    Serial.print("]: ");
    
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("JSON解析失败: ");
        Serial.println(error.c_str());
        return;
    }
    
    if (String(topic) == AWS_IOT_SHADOW_UPDATE_DELTA) {
        if (doc["state"].containsKey("led")) {
            String ledState = doc["state"]["led"];
            bool newLedState = (ledState == "ON");
            digitalWrite(LED_PIN, newLedState ? HIGH : LOW);
            Serial.print("LED状态更新为: ");
            Serial.println(ledState);
            updateShadowReported(newLedState);
        }
    }
}

void publishMessage() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("读取DHT传感器失败!");
        return;
    }
    
    StaticJsonDocument<200> doc;
    doc["device"] = THING_NAME;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["timestamp"] = millis();
    
    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    
    Serial.print("发布消息: ");
    Serial.println(jsonBuffer);
    client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

void updateShadowReported(bool ledState) {
    StaticJsonDocument<512> doc;
    JsonObject state = doc.createNestedObject("state");
    JsonObject reported = state.createNestedObject("reported");
    
    reported["led"] = ledState ? "ON" : "OFF";
    reported["timestamp"] = millis();
    
    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    
    Serial.print("更新设备影子: ");
    Serial.println(jsonBuffer);
    client.publish(AWS_IOT_SHADOW_UPDATE, jsonBuffer);
}
```

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

**版权声明**：本教程遵循CC BY-NC-SA 4.0协议，欢迎分享和改编，但请注明出处。
