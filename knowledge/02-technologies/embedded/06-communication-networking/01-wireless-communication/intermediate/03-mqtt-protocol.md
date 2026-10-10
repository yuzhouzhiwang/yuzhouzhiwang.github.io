---
title: "MQTT协议详解：物联网消息传输实践"
description: "深入讲解MQTT协议的设计原理、报文结构、QoS机制和安全特性，通过ESP32/STM32实战案例掌握嵌入式设备接入MQTT Broker的完整开发流程"
slug: "mqtt-protocol-iot-messaging"

domain: "通信与网络"
module: "无线通信"
content_type: "article"
skill_level: "intermediate"

tags:
  - MQTT
  - 物联网
  - 消息队列
  - 发布订阅
  - IoT通信
  - ESP32
prerequisites:
  - "beginner/01-wifi-basics"
related_contents:
  - "intermediate/01-nb-iot"
  - "intermediate/02-5g-embedded"

estimated_time: 120
difficulty_score: 3

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "2.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - MQTT协议
  - 物联网通信
  - 发布订阅模式
  - MQTT Broker
  - 嵌入式MQTT
  - MQTT 5.0
  - ESP-IDF
  - EMQX集群
cover_image: ""
---
{% raw %}

# MQTT协议详解：物联网消息传输实践

## 概述

MQTT（Message Queuing Telemetry Transport，消息队列遥测传输）是一种基于发布/订阅（Publish/Subscribe）模式的轻量级消息传输协议，专为低带宽、高延迟或不可靠网络环境下的物联网（IoT）设备设计。由IBM于1999年发明，现已成为IoT领域事实上的标准协议（ISO/IEC 20922）。

**学习目标**：

| 目标 | 技能点 |
|------|--------|
| 理解协议原理 | 发布/订阅架构、QoS三级别、报文结构 |
| 掌握版本差异 | MQTT 3.1.1 vs 5.0 新特性对比 |
| 嵌入式实现 | ESP-IDF原生客户端、STM32 coreMQTT |
| 云平台集成 | AWS IoT Core、阿里云IoT接入 |
| 生产部署 | EMQX集群、消息持久化、桥接配置 |
| 完整项目 | 5节点传感器网络→Broker→InfluxDB→Grafana |

**前置知识**：TCP/IP基础、JSON格式、基本C/C++编程


## 背景知识

### 为什么选择MQTT

与HTTP相比，MQTT在IoT场景中的优势：

| 特性 | HTTP/1.1 | HTTP/2 | MQTT 3.1.1 | MQTT 5.0 |
|------|----------|--------|------------|----------|
| 通信模式 | 请求/响应 | 请求/响应+推送 | 发布/订阅 | 发布/订阅 |
| 连接方式 | 短连接 | 多路复用长连接 | 长连接 | 长连接 |
| 最小报文 | ~200字节 | ~9字节帧头 | 2字节 | 2字节 |
| 实时推送 | 需轮询/SSE | Server Push | 原生支持 | 原生支持 |
| 离线消息 | 不支持 | 不支持 | 持久会话 | 持久会话+增强 |
| 错误反馈 | HTTP状态码 | HTTP状态码 | 有限 | 原因码（Reason Code） |
| 用户属性 | HTTP头 | HTTP头 | 不支持 | 支持 |
| 主题别名 | 不适用 | 不适用 | 不支持 | 支持（减少带宽） |
| 适用场景 | Web API | Web API | IoT传感器 | IoT传感器+高级特性 |

### MQTT vs CoAP vs AMQP vs HTTP/2 IoT对比

```
协议选型决策树：

设备资源极度受限（<10KB RAM）？
├── 是 → CoAP（UDP，RESTful，适合LwM2M）
└── 否 → 需要消息路由/过滤？
         ├── 是 → 需要企业级消息队列？
         │        ├── 是 → AMQP（RabbitMQ，金融/企业）
         │        └── 否 → MQTT（IoT首选）
         └── 否 → 需要Web兼容？
                  └── 是 → HTTP/2 + SSE
```

| 协议 | 传输层 | 最小开销 | 消息模式 | 典型场景 |
|------|--------|----------|----------|----------|
| MQTT | TCP | 2字节 | 发布/订阅 | IoT传感器、设备控制 |
| CoAP | UDP | 4字节 | 请求/响应 | 受限设备、LwM2M |
| AMQP | TCP | ~8字节 | 队列/路由 | 企业消息总线 |
| HTTP/2 | TCP | ~9字节帧 | 请求/响应 | Web API、流媒体 |
| WebSocket | TCP | 2字节帧 | 双向流 | 实时Web应用 |

**MQTT适用场景**：
- 传感器数据周期上报（温湿度、GPS位置）
- 云端下发控制指令（开关、参数配置）
- 设备状态监控（在线/离线检测）
- 多设备广播通知

### MQTT 3.1.1 vs MQTT 5.0 特性对比

MQTT 5.0于2019年3月发布，是协议的重大升级：

| 特性 | MQTT 3.1.1 | MQTT 5.0 | 说明 |
|------|------------|----------|------|
| 原因码（Reason Code） | 有限（CONNACK返回码） | 全面扩展（所有报文） | 精确错误诊断 |
| 用户属性（User Properties） | 不支持 | 支持（键值对元数据） | 自定义元数据传递 |
| 共享订阅（Shared Subscriptions） | 不支持 | 支持（$share/group/topic） | 负载均衡消费 |
| 主题别名（Topic Alias） | 不支持 | 支持（整数替代长主题名） | 减少带宽消耗 |
| 消息过期（Message Expiry） | 不支持 | 支持（秒级TTL） | 避免过期消息堆积 |
| 订阅选项（Subscription Options） | 无 | noLocal、retainAsPublished | 精细控制 |
| 请求/响应模式 | 需自行实现 | 内置（Response Topic + Correlation Data） | 标准化RPC |
| 流量控制 | 无 | 接收最大值（Receive Maximum） | 防止消息洪泛 |
| 会话过期间隔 | cleanSession二选一 | 精确秒数控制 | 灵活会话管理 |
| 认证增强 | 用户名/密码 | AUTH报文（SCRAM、Kerberos） | 挑战-响应认证 |
| 遗嘱延迟 | 立即发布 | 可配置延迟（Will Delay Interval） | 避免短暂断线误报 |
| 内容类型 | 无 | Content-Type字段 | 标识Payload格式 |

**MQTT 5.0关键新特性详解**：

**1. 原因码（Reason Code）**：
```
MQTT 3.1.1 CONNACK返回码：
  0x00 = 连接成功
  0x01 = 不支持的协议版本
  0x05 = 未授权

MQTT 5.0 CONNACK原因码（更细粒度）：
  0x00 = 成功
  0x80 = 未指定错误
  0x81 = 格式错误的报文
  0x82 = 协议错误
  0x87 = 未授权
  0x88 = 服务器不可用
  0x89 = 服务器繁忙
  0x8A = 禁止访问
  0x90 = 主题名无效
  0x97 = 超出配额
  0x9E = 不支持共享订阅
```

**2. 共享订阅（Shared Subscriptions）**：
```
普通订阅（每个订阅者都收到消息）：
  订阅者A: subscribe("sensor/data")  → 收到所有消息
  订阅者B: subscribe("sensor/data")  → 收到所有消息（重复）

共享订阅（消息在订阅者间负载均衡）：
  订阅者A: subscribe("$share/workers/sensor/data")  → 轮流收到
  订阅者B: subscribe("$share/workers/sensor/data")  → 轮流收到
  
格式：$share/{ShareName}/{TopicFilter}
用途：多消费者并行处理，实现水平扩展
```

**3. 请求/响应模式（Request/Response）**：
```
MQTT 5.0内置RPC机制：

请求方：
  发布到: "device/cmd/node001"
  设置: Response Topic = "device/response/client123"
  设置: Correlation Data = "req-uuid-456"

响应方：
  收到请求后，发布到Response Topic
  携带相同的Correlation Data
  
请求方通过Correlation Data匹配响应
```

### Broker架构内部原理

#### 订阅树（Subscription Tree）

Broker内部使用前缀树（Trie）存储订阅关系，实现高效的主题匹配：

```
订阅树示例（存储3个订阅）：
  订阅者A: "sensor/+/temperature"
  订阅者B: "sensor/room1/#"
  订阅者C: "device/status"

Trie结构：
  root
  ├── sensor
  │   ├── + (通配符节点)
  │   │   └── temperature → [订阅者A]
  │   └── room1
  │       └── # (多层通配符) → [订阅者B]
  └── device
      └── status → [订阅者C]

消息路由：publish("sensor/room1/temperature")
  → 匹配 sensor/+/temperature → 转发给订阅者A
  → 匹配 sensor/room1/#       → 转发给订阅者B
  时间复杂度：O(主题层级数)，与订阅者数量无关
```

#### 会话存储（Session Store）

```
持久会话（cleanSession=false / MQTT5: sessionExpiryInterval>0）存储内容：

┌─────────────────────────────────────────────────────┐
│  Session Store (per ClientID)                       │
│                                                     │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │  订阅列表        │  │  离线消息队列             │  │
│  │  topic: sensor/# │  │  [msg1, QoS1, packetId=1]│  │
│  │  qos: 1          │  │  [msg2, QoS2, packetId=2]│  │
│  │  topic: cmd/+    │  │  [msg3, QoS1, packetId=3]│  │
│  │  qos: 2          │  └──────────────────────────┘  │
│  └─────────────────┘                                 │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │  飞行中消息（In-Flight Messages）             │    │
│  │  QoS1: 等待PUBACK的消息                      │    │
│  │  QoS2: 等待PUBREC/PUBREL/PUBCOMP的消息       │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```


## 核心内容

### MQTT报文结构

每个MQTT报文由三部分组成：

```
┌─────────────────────────────────────────┐
│  固定头（Fixed Header）  2字节起         │
│  ├── 报文类型（4bit）+ 标志位（4bit）    │
│  └── 剩余长度（1-4字节，变长编码）       │
├─────────────────────────────────────────┤
│  可变头（Variable Header）  可选         │
│  └── 报文标识符、协议名称等              │
├─────────────────────────────────────────┤
│  有效载荷（Payload）  可选               │
│  └── 实际消息内容                        │
└─────────────────────────────────────────┘
```

**CONNECT报文字节级解析**（MQTT 3.1.1）：

```
字节  内容                    说明
----  ----------------------  --------------------------------
0x10  固定头：CONNECT报文类型
0x??  剩余长度（变长编码）
--- 可变头 ---
0x00 0x04  协议名长度 = 4
0x4D 0x51 0x54 0x54  "MQTT"
0x04  协议级别 = 4（MQTT 3.1.1）
0xC2  连接标志：
      bit7=1: 用户名存在
      bit6=1: 密码存在
      bit5=0: 遗嘱保留=false
      bit4-3=00: 遗嘱QoS=0
      bit2=0: 遗嘱标志=false
      bit1=1: cleanSession=true
      bit0=0: 保留
0x00 0x3C  保活时间 = 60秒
--- 载荷 ---
0x00 0x0C  客户端ID长度 = 12
"esp32_node_01"  客户端ID
```

**主要报文类型**：

| 报文类型 | 值 | 方向 | 说明 |
|---------|-----|------|------|
| CONNECT | 1 | 客户端→Broker | 建立连接 |
| CONNACK | 2 | Broker→客户端 | 连接确认 |
| PUBLISH | 3 | 双向 | 发布消息 |
| PUBACK | 4 | 双向 | QoS1确认 |
| PUBREC | 5 | 双向 | QoS2第一步 |
| PUBREL | 6 | 双向 | QoS2第二步 |
| PUBCOMP | 7 | 双向 | QoS2完成 |
| SUBSCRIBE | 8 | 客户端→Broker | 订阅主题 |
| SUBACK | 9 | Broker→客户端 | 订阅确认 |
| UNSUBSCRIBE | 10 | 客户端→Broker | 取消订阅 |
| UNSUBACK | 11 | Broker→客户端 | 取消订阅确认 |
| PINGREQ | 12 | 客户端→Broker | 心跳请求 |
| PINGRESP | 13 | Broker→客户端 | 心跳响应 |
| DISCONNECT | 14 | 客户端→Broker | 断开连接 |
| AUTH | 15 | 双向 | 增强认证（MQTT 5.0） |

### QoS三个级别

**QoS 0 - 最多一次（At Most Once）**：
```
发布者 ──PUBLISH──→ Broker ──PUBLISH──→ 订阅者
       （发完即忘，可能丢失）
```
适用：传感器高频上报，偶尔丢失可接受（如每秒上报温度）。

**QoS 1 - 至少一次（At Least Once）**：
```
发布者 ──PUBLISH(packetId=1)──→ Broker
Broker ──PUBACK(packetId=1)──→ 发布者（确认收到）
Broker ──PUBLISH(packetId=2)──→ 订阅者
订阅者 ──PUBACK(packetId=2)──→ Broker
（确保送达，可能重复）
```
适用：重要数据上报，可以接受重复但不能丢失（如报警事件）。

**QoS 2 - 恰好一次（Exactly Once）**：
```
发布者 ──PUBLISH(packetId=1)──→ Broker
Broker ──PUBREC(packetId=1)──→ 发布者
发布者 ──PUBREL(packetId=1)──→ Broker
Broker ──PUBCOMP(packetId=1)──→ 发布者
（4次握手，确保恰好一次）
```
适用：金融交易、计费数据等不能重复也不能丢失的场景。开销最大。

**选择建议**：
- 传感器周期上报 → QoS 0
- 设备状态变更、告警 → QoS 1
- 控制指令（开关、配置下发）→ QoS 1 或 QoS 2

### 遗嘱消息（Last Will and Testament）

设备异常断线时，Broker自动发布预设的遗嘱消息，用于检测设备离线：

```c
// 连接时设置遗嘱（MQTT 3.1.1）
MQTTClient_willOptions will = MQTTClient_willOptions_initializer;
will.topicName = "device/status/node001";
will.message   = "{\"status\":\"offline\",\"reason\":\"unexpected\"}";
will.qos       = 1;
will.retained  = 1;  // 保留消息，新订阅者也能收到

// MQTT 5.0 遗嘱延迟（Will Delay Interval）
// 设备重连后，如果在延迟时间内重连成功，遗嘱不会发布
// 避免短暂网络抖动导致误报离线
will_delay_interval = 30;  // 30秒内重连则不发布遗嘱
```

### 保留消息（Retained Message）

Broker保存某个主题的最后一条消息，新订阅者立即收到最新状态：

```
场景：设备上报当前温度，新连接的手机App立即显示最新温度
→ 发布时设置 retain=true
→ Broker保存该消息（每个主题只保留最后一条）
→ 任何新订阅者连接后立即收到
→ 发布空消息（payload长度=0）可清除保留消息
```

### 持久会话（Persistent Session）

```
cleanSession=false（MQTT 3.1.1）/ sessionExpiryInterval>0（MQTT 5.0）时：
→ Broker记住客户端的订阅关系
→ 离线期间的QoS1/2消息排队等待
→ 重连后自动补发离线消息

适用场景：设备网络不稳定，需要保证离线期间的控制指令不丢失
注意：持久会话会占用Broker内存，需要设置合理的过期时间
```

### MQTT 5.0 新特性实现

#### 用户属性（User Properties）

```c
// ESP-IDF MQTT 5.0 用户属性示例
#include "mqtt5_client.h"

esp_mqtt5_publish_property_config_t publish_property = {
    .payload_format_indicator = 1,  // 1=UTF-8文本
    .message_expiry_interval  = 300, // 5分钟后过期
    .content_type             = "application/json",
};

// 添加用户属性（键值对元数据）
esp_mqtt5_client_set_user_property(
    &publish_property.user_property,
    "device_type", "temperature_sensor"
);
esp_mqtt5_client_set_user_property(
    &publish_property.user_property,
    "firmware_version", "v2.1.0"
);
esp_mqtt5_client_set_user_property(
    &publish_property.user_property,
    "location", "building_A_floor_3"
);

// 发布带用户属性的消息
esp_mqtt5_client_publish(
    client,
    "iot/sensor/node001/data",
    payload_json,
    strlen(payload_json),
    1,    // QoS 1
    0,    // retain=false
    &publish_property
);
```

#### 共享订阅（Shared Subscriptions）负载均衡

```c
// 多个消费者订阅同一共享组，消息轮流分发
// 格式：$share/{GroupName}/{TopicFilter}

// 消费者1
esp_mqtt_client_subscribe(client1, "$share/data_workers/iot/sensor/#", 1);

// 消费者2
esp_mqtt_client_subscribe(client2, "$share/data_workers/iot/sensor/#", 1);

// 消费者3
esp_mqtt_client_subscribe(client3, "$share/data_workers/iot/sensor/#", 1);

// 效果：发布到 iot/sensor/node001/data 的消息
// 只有一个消费者收到（轮询或随机分发，取决于Broker实现）
// 实现水平扩展的消息处理
```

### ESP-IDF 原生 MQTT 客户端

ESP-IDF（Espressif IoT Development Framework）提供原生MQTT客户端，无需Arduino库：

```c
// main/mqtt_client_main.c
// ESP-IDF v5.x + MQTT 5.0
#include <stdio.h>
#include <string.h>
#include "esp_log.h"
#include "esp_event.h"
#include "mqtt_client.h"

static const char *TAG = "MQTT5_CLIENT";

// MQTT Broker配置
#define MQTT_BROKER_URI    "mqtt://broker.emqx.io:1883"
#define MQTT_CLIENT_ID     "esp32_idf_node001"
#define MQTT_USERNAME      "iot_user"
#define MQTT_PASSWORD      "iot_password"

// 主题定义
#define TOPIC_SENSOR_DATA  "iot/sensor/node001/data"
#define TOPIC_CONTROL_CMD  "iot/control/node001/cmd"
#define TOPIC_STATUS       "iot/device/node001/status"

static esp_mqtt_client_handle_t mqtt_client = NULL;

// MQTT事件处理函数
static void mqtt_event_handler(void *handler_args,
                                esp_event_base_t base,
                                int32_t event_id,
                                void *event_data)
{
    esp_mqtt_event_handle_t event = event_data;

    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT Connected to broker");
            // 订阅控制主题
            esp_mqtt_client_subscribe(mqtt_client, TOPIC_CONTROL_CMD, 1);
            // 发布上线状态（保留消息）
            esp_mqtt_client_publish(mqtt_client, TOPIC_STATUS,
                                    "{\"status\":\"online\"}", 0, 1, 1);
            break;

        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGW(TAG, "MQTT Disconnected");
            break;

        case MQTT_EVENT_SUBSCRIBED:
            ESP_LOGI(TAG, "Subscribed, msg_id=%d", event->msg_id);
            break;

        case MQTT_EVENT_DATA:
            ESP_LOGI(TAG, "Received on topic: %.*s",
                     event->topic_len, event->topic);
            ESP_LOGI(TAG, "Payload: %.*s",
                     event->data_len, event->data);
            // 处理控制指令
            handle_control_command(event->data, event->data_len);
            break;

        case MQTT_EVENT_ERROR:
            ESP_LOGE(TAG, "MQTT Error: %d",
                     event->error_handle->error_type);
            if (event->error_handle->error_type ==
                MQTT_ERROR_TYPE_TCP_TRANSPORT) {
                ESP_LOGE(TAG, "TCP error: %d",
                         event->error_handle->esp_transport_sock_errno);
            }
            break;

        default:
            break;
    }
}

// 处理控制指令
static void handle_control_command(const char *data, int len)
{
    // 简单JSON解析（生产环境使用cJSON库）
    if (strncmp(data, "{\"cmd\":\"led_on\"}", len) == 0) {
        gpio_set_level(GPIO_NUM_2, 1);
        ESP_LOGI(TAG, "LED ON");
    } else if (strncmp(data, "{\"cmd\":\"led_off\"}", len) == 0) {
        gpio_set_level(GPIO_NUM_2, 0);
        ESP_LOGI(TAG, "LED OFF");
    } else if (strncmp(data, "{\"cmd\":\"reboot\"}", len) == 0) {
        ESP_LOGW(TAG, "Rebooting...");
        esp_restart();
    }
}

// 初始化MQTT客户端
esp_err_t mqtt_app_start(void)
{
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker = {
            .address.uri = MQTT_BROKER_URI,
        },
        .credentials = {
            .client_id = MQTT_CLIENT_ID,
            .username  = MQTT_USERNAME,
            .authentication.password = MQTT_PASSWORD,
        },
        .session = {
            .keepalive         = 60,
            .disable_clean_session = false,
            // 遗嘱消息配置
            .last_will = {
                .topic   = TOPIC_STATUS,
                .msg     = "{\"status\":\"offline\"}",
                .msg_len = 20,
                .qos     = 1,
                .retain  = true,
            },
        },
        .network = {
            .reconnect_timeout_ms = 5000,  // 5秒后重连
            .timeout_ms           = 10000, // 连接超时10秒
        },
        .buffer = {
            .size     = 1024,  // 接收缓冲区
            .out_size = 1024,  // 发送缓冲区
        },
    };

    mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    if (mqtt_client == NULL) {
        ESP_LOGE(TAG, "Failed to init MQTT client");
        return ESP_FAIL;
    }

    // 注册事件处理函数
    esp_mqtt_client_register_event(mqtt_client, ESP_EVENT_ANY_ID,
                                   mqtt_event_handler, NULL);

    return esp_mqtt_client_start(mqtt_client);
}

// 发布传感器数据
esp_err_t mqtt_publish_sensor_data(float temperature,
                                    float humidity,
                                    float pressure)
{
    if (mqtt_client == NULL) return ESP_ERR_INVALID_STATE;

    char payload[256];
    snprintf(payload, sizeof(payload),
             "{"
             "\"device_id\":\"%s\","
             "\"temperature\":%.2f,"
             "\"humidity\":%.2f,"
             "\"pressure\":%.2f,"
             "\"timestamp\":%lld"
             "}",
             MQTT_CLIENT_ID,
             temperature, humidity, pressure,
             (long long)esp_timer_get_time() / 1000000LL);

    int msg_id = esp_mqtt_client_publish(
        mqtt_client,
        TOPIC_SENSOR_DATA,
        payload,
        strlen(payload),
        0,    // QoS 0（传感器数据允许丢失）
        0     // retain=false
    );

    if (msg_id < 0) {
        ESP_LOGE(TAG, "Publish failed");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Published sensor data, msg_id=%d", msg_id);
    return ESP_OK;
}

// app_main
void app_main(void)
{
    // 初始化NVS（WiFi需要）
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    // 初始化网络
    esp_netif_init();
    esp_event_loop_create_default();

    // 连接WiFi（省略WiFi初始化代码）
    wifi_init_sta();

    // 启动MQTT
    mqtt_app_start();

    // 主循环：每30秒上报传感器数据
    while (1) {
        float temp = read_temperature_sensor();
        float humi = read_humidity_sensor();
        float pres = read_pressure_sensor();
        mqtt_publish_sensor_data(temp, humi, pres);
        vTaskDelay(pdMS_TO_TICKS(30000));
    }
}
```

**CMakeLists.txt配置**：

```cmake
# main/CMakeLists.txt
idf_component_register(
    SRCS "mqtt_client_main.c"
    INCLUDE_DIRS "."
    REQUIRES
        mqtt          # ESP-IDF MQTT组件
        esp_wifi
        nvs_flash
        esp_netif
        json          # cJSON组件
)
```

**sdkconfig关键配置**：

```
# MQTT配置
CONFIG_MQTT_PROTOCOL_5=y          # 启用MQTT 5.0支持
CONFIG_MQTT_BUFFER_SIZE=1024
CONFIG_MQTT_TASK_STACK_SIZE=6144
CONFIG_MQTT_OUTBOX_EXPIRED_TIMEOUT_MS=30000

# TLS配置（生产环境）
CONFIG_MQTT_TRANSPORT_SSL=y
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y
```

### AWS IoT Core 接入

AWS IoT Core是托管的MQTT Broker，支持设备影子（Device Shadow）和规则引擎：

```c
// AWS IoT Core连接（使用X.509证书认证）
// 证书文件从AWS IoT控制台下载

#include "mqtt_client.h"

// AWS IoT端点（从控制台获取）
#define AWS_IOT_ENDPOINT  "xxxxxx-ats.iot.us-east-1.amazonaws.com"
#define AWS_IOT_PORT      8883

// 证书（嵌入到固件中）
extern const uint8_t aws_root_ca_pem_start[]
    asm("_binary_aws_root_ca_pem_start");
extern const uint8_t aws_certificate_pem_crt_start[]
    asm("_binary_certificate_pem_crt_start");
extern const uint8_t aws_private_pem_key_start[]
    asm("_binary_private_pem_key_start");

esp_mqtt_client_config_t aws_cfg = {
    .broker = {
        .address = {
            .hostname = AWS_IOT_ENDPOINT,
            .port     = AWS_IOT_PORT,
            .transport = MQTT_TRANSPORT_OVER_SSL,
        },
        .verification = {
            .certificate = (const char*)aws_root_ca_pem_start,
        },
    },
    .credentials = {
        .client_id = "esp32_thing_001",
        .authentication = {
            .certificate = (const char*)aws_certificate_pem_crt_start,
            .key         = (const char*)aws_private_pem_key_start,
        },
    },
};

// AWS IoT设备影子（Device Shadow）主题
// 获取影子：$aws/things/{thingName}/shadow/get
// 更新影子：$aws/things/{thingName}/shadow/update
// 影子格式：
// {
//   "state": {
//     "reported": { "led": "on", "temperature": 25.3 },
//     "desired":  { "led": "off" }
//   }
// }

void update_device_shadow(bool led_state, float temperature)
{
    char shadow_payload[256];
    snprintf(shadow_payload, sizeof(shadow_payload),
             "{\"state\":{\"reported\":{"
             "\"led\":\"%s\","
             "\"temperature\":%.1f"
             "}}}",
             led_state ? "on" : "off",
             temperature);

    esp_mqtt_client_publish(
        mqtt_client,
        "$aws/things/esp32_thing_001/shadow/update",
        shadow_payload,
        strlen(shadow_payload),
        1, 0
    );
}
```

**AWS IoT规则引擎（将MQTT数据写入DynamoDB）**：

```sql
-- AWS IoT规则SQL
SELECT
    device_id,
    temperature,
    humidity,
    timestamp() AS ts
FROM 'iot/sensor/+/data'
WHERE temperature > 0 AND humidity > 0
```

### 阿里云IoT平台接入

```c
// 阿里云IoT平台使用MQTT + 三元组认证
// 三元组：ProductKey + DeviceName + DeviceSecret

#define ALIYUN_PRODUCT_KEY   "a1xxxxxxxx"
#define ALIYUN_DEVICE_NAME   "esp32_node001"
#define ALIYUN_DEVICE_SECRET "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#define ALIYUN_REGION        "cn-shanghai"

// 阿里云MQTT Broker地址
// 格式：{ProductKey}.iot-as-mqtt.{Region}.aliyuncs.com
#define ALIYUN_BROKER_HOST   ALIYUN_PRODUCT_KEY \
                             ".iot-as-mqtt." \
                             ALIYUN_REGION \
                             ".aliyuncs.com"
#define ALIYUN_BROKER_PORT   1883

// ClientID格式：{DeviceName}|securemode=3,signmethod=hmacsha256,timestamp=xxxxx|
// Username格式：{DeviceName}&{ProductKey}
// Password：HMAC-SHA256签名

// 阿里云物模型（Thing Model）上报主题
// /sys/{ProductKey}/{DeviceName}/thing/event/property/post
#define ALIYUN_TOPIC_POST \
    "/sys/" ALIYUN_PRODUCT_KEY "/" ALIYUN_DEVICE_NAME \
    "/thing/event/property/post"

void aliyun_publish_properties(float temperature, float humidity)
{
    char payload[512];
    snprintf(payload, sizeof(payload),
             "{"
             "\"id\":\"1\","
             "\"version\":\"1.0\","
             "\"params\":{"
             "\"CurrentTemperature\":{\"value\":%.1f},"
             "\"CurrentHumidity\":{\"value\":%.1f}"
             "},"
             "\"method\":\"thing.event.property.post\""
             "}",
             temperature, humidity);

    esp_mqtt_client_publish(mqtt_client, ALIYUN_TOPIC_POST,
                            payload, strlen(payload), 1, 0);
}
```


## 深入原理

### EMQX Broker集群架构

EMQX是目前最流行的开源MQTT Broker之一，支持水平扩展的集群部署：

```
EMQX集群架构（3节点示例）：

                    ┌─────────────────────────────┐
                    │      负载均衡器（HAProxy）    │
                    │   TCP 1883 / TLS 8883        │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────┴──────┐ ┌───────┴──────┐ ┌──────┴───────┐
    │  EMQX Node 1   │ │ EMQX Node 2  │ │ EMQX Node 3  │
    │  emqx@node1    │ │ emqx@node2   │ │ emqx@node3   │
    │  192.168.1.11  │ │ 192.168.1.12 │ │ 192.168.1.13 │
    └────────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────────────┴────────────────┘
                    Erlang分布式通信（4370端口）
                    订阅路由表全局同步
                    
集群特性：
- 任意节点接收的消息，自动路由到订阅者所在节点
- 节点故障时，客户端自动重连到其他节点
- 水平扩展：单集群支持1000万+并发连接
```

**EMQX集群配置（emqx.conf）**：

```hocon
# emqx.conf - EMQX 5.x配置格式（HOCON）

# 节点名称
node {
  name = "emqx@192.168.1.11"
  cookie = "emqx_secret_cookie_change_me"
  data_dir = "/var/lib/emqx"
}

# 集群配置
cluster {
  name = "emqxcl"
  discovery_strategy = static  # 静态节点发现

  static {
    seeds = [
      "emqx@192.168.1.11",
      "emqx@192.168.1.12",
      "emqx@192.168.1.13"
    ]
  }
}

# 监听器配置
listeners.tcp.default {
  bind = "0.0.0.0:1883"
  max_connections = 1024000
  # 每个连接的接收缓冲区
  tcp_options {
    buffer = 4KB
    recbuf = 4KB
    sndbuf = 4KB
  }
}

listeners.ssl.default {
  bind = "0.0.0.0:8883"
  ssl_options {
    cacertfile = "/etc/emqx/certs/ca.pem"
    certfile   = "/etc/emqx/certs/server.pem"
    keyfile    = "/etc/emqx/certs/server.key"
    verify     = verify_peer  # 双向TLS认证
  }
}

# 认证配置（内置数据库）
authentication = [
  {
    mechanism = password_based
    backend   = built_in_database
    password_hash_algorithm {
      name = bcrypt
      salt_rounds = 10
    }
  }
]

# 授权（ACL）配置
authorization {
  no_match = deny  # 默认拒绝
  deny_action = disconnect

  sources = [
    {
      type = built_in_database
      enable = true
    }
  ]
}
```

**Docker Compose部署3节点EMQX集群**：

```yaml
# docker-compose-emqx-cluster.yml
version: '3.8'

services:
  emqx1:
    image: emqx/emqx:5.3.0
    container_name: emqx1
    environment:
      - EMQX_NODE_NAME=emqx@emqx1
      - EMQX_CLUSTER__DISCOVERY_STRATEGY=static
      - EMQX_CLUSTER__STATIC__SEEDS=emqx@emqx1,emqx@emqx2,emqx@emqx3
      - EMQX_NODE__COOKIE=emqx_secret_cookie
    ports:
      - "1883:1883"
      - "8083:8083"   # WebSocket
      - "8084:8084"   # WebSocket TLS
      - "8883:8883"   # MQTT TLS
      - "18083:18083" # Dashboard
    networks:
      emqx_bridge:
        aliases:
          - emqx1
    volumes:
      - emqx1_data:/var/lib/emqx

  emqx2:
    image: emqx/emqx:5.3.0
    container_name: emqx2
    environment:
      - EMQX_NODE_NAME=emqx@emqx2
      - EMQX_CLUSTER__DISCOVERY_STRATEGY=static
      - EMQX_CLUSTER__STATIC__SEEDS=emqx@emqx1,emqx@emqx2,emqx@emqx3
      - EMQX_NODE__COOKIE=emqx_secret_cookie
    networks:
      emqx_bridge:
        aliases:
          - emqx2
    volumes:
      - emqx2_data:/var/lib/emqx

  emqx3:
    image: emqx/emqx:5.3.0
    container_name: emqx3
    environment:
      - EMQX_NODE_NAME=emqx@emqx3
      - EMQX_CLUSTER__DISCOVERY_STRATEGY=static
      - EMQX_CLUSTER__STATIC__SEEDS=emqx@emqx1,emqx@emqx2,emqx@emqx3
      - EMQX_NODE__COOKIE=emqx_secret_cookie
    networks:
      emqx_bridge:
        aliases:
          - emqx3
    volumes:
      - emqx3_data:/var/lib/emqx

  haproxy:
    image: haproxy:2.8
    container_name: haproxy
    ports:
      - "1884:1884"  # 负载均衡MQTT端口
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    networks:
      - emqx_bridge

networks:
  emqx_bridge:
    driver: bridge

volumes:
  emqx1_data:
  emqx2_data:
  emqx3_data:
```

### 消息持久化（Message Persistence）

EMQX支持将消息持久化到外部数据库，防止Broker重启丢失消息：

```
消息持久化架构：

MQTT设备 → EMQX Broker → 规则引擎（Rule Engine）
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         InfluxDB         PostgreSQL       Redis
         (时序数据)        (业务数据)      (实时缓存)
```

**EMQX规则引擎配置（将消息写入InfluxDB）**：

```sql
-- EMQX规则引擎SQL（从MQTT主题提取数据）
SELECT
    payload.device_id AS device_id,
    payload.temperature AS temperature,
    payload.humidity AS humidity,
    payload.pressure AS pressure,
    timestamp AS ts
FROM "iot/sensor/+/data"
WHERE payload.temperature > -40 AND payload.temperature < 85
```

```hocon
# EMQX规则引擎动作：写入InfluxDB 2.x
bridges.influxdb.iot_metrics {
  enable = true
  server = "http://influxdb:8086"
  token  = "your_influxdb_token"
  org    = "iot_org"
  bucket = "sensor_data"
  precision = ms

  write_syntax =
    "sensor_data,device=${device_id} "
    "temperature=${temperature},"
    "humidity=${humidity},"
    "pressure=${pressure} ${ts}"
}
```

### MQTT桥接（Bridge）配置

桥接用于连接两个独立的MQTT Broker，实现跨网络消息转发：

```
桥接场景：工厂内网Broker → 云端Broker

工厂内网：                    云端：
设备A ─┐                    ┌─ 云端应用
设备B ─┤→ 本地Broker ──桥接──→ 云端Broker ─┤
设备C ─┘  (Mosquitto)        (EMQX Cloud)  └─ 数据库

优势：
- 内网设备无需直接连接公网
- 减少公网带宽（只转发需要的主题）
- 本地Broker提供离线缓存
```

**Mosquitto桥接配置（mosquitto.conf）**：

```conf
# /etc/mosquitto/conf.d/bridge.conf

# 桥接连接名称
connection cloud_bridge

# 云端Broker地址
address broker.emqx.io:8883

# TLS配置
bridge_cafile /etc/mosquitto/certs/ca.crt
bridge_certfile /etc/mosquitto/certs/client.crt
bridge_keyfile /etc/mosquitto/certs/client.key
bridge_tls_version tlsv1.3

# 认证
remote_username bridge_user
remote_password bridge_password

# 桥接主题配置
# 格式：topic <pattern> [direction] [qos] [local_prefix] [remote_prefix]
# direction: in(云→本地), out(本地→云), both(双向)

# 将本地传感器数据转发到云端
topic iot/sensor/# out 1 "" factory/building_a/

# 从云端接收控制指令
topic iot/control/# in 1 "" factory/building_a/

# 桥接保活时间
keepalive_interval 60

# 断线重连间隔
restart_timeout 5

# 本地消息缓存（断网时）
bridge_attempt_unsubscribe false
```

### MQTT over WebSocket

WebSocket传输允许浏览器直接连接MQTT Broker，无需中间层：

```
WebSocket MQTT架构：

浏览器 ──WebSocket(ws://broker:8083/mqtt)──→ EMQX Broker
                                                    │
                                              ←─────┘
                                         实时推送传感器数据
```

**JavaScript浏览器端MQTT客户端（MQTT.js）**：

```javascript
// 安装：npm install mqtt
// 或CDN：<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>

const mqtt = require('mqtt');

// 连接EMQX WebSocket端口
const client = mqtt.connect('ws://broker.emqx.io:8083/mqtt', {
    clientId: 'browser_dashboard_' + Math.random().toString(16).substr(2, 8),
    username: 'dashboard_user',
    password: 'dashboard_pass',
    keepalive: 60,
    reconnectPeriod: 3000,  // 3秒重连
    connectTimeout: 10000,
    // MQTT 5.0选项
    protocolVersion: 5,
    properties: {
        sessionExpiryInterval: 300,  // 5分钟会话过期
    }
});

// 连接成功
client.on('connect', (connack) => {
    console.log('Connected to MQTT broker');

    // 订阅传感器数据
    client.subscribe('iot/sensor/#', { qos: 1 }, (err, granted) => {
        if (!err) {
            console.log('Subscribed:', granted);
        }
    });
});

// 接收消息
client.on('message', (topic, payload, packet) => {
    const data = JSON.parse(payload.toString());
    console.log(`[${topic}]`, data);

    // 更新Dashboard图表
    updateChart(data.device_id, data.temperature, data.timestamp);
});

// 发布控制指令
function sendCommand(deviceId, command) {
    const topic = `iot/control/${deviceId}/cmd`;
    const payload = JSON.stringify({ cmd: command, ts: Date.now() });

    client.publish(topic, payload, {
        qos: 1,
        retain: false,
        properties: {
            messageExpiryInterval: 30,  // 30秒后过期
            userProperties: {
                source: 'web_dashboard',
                operator: 'admin'
            }
        }
    });
}

// 错误处理
client.on('error', (err) => {
    console.error('MQTT Error:', err.message);
});

client.on('offline', () => {
    console.warn('MQTT client offline');
});

client.on('reconnect', () => {
    console.log('Reconnecting...');
});
```

**EMQX WebSocket监听器配置**：

```hocon
# emqx.conf
listeners.ws.default {
  bind = "0.0.0.0:8083"
  websocket.mqtt_path = "/mqtt"
  max_connections = 102400
}

listeners.wss.default {
  bind = "0.0.0.0:8084"
  websocket.mqtt_path = "/mqtt"
  ssl_options {
    certfile = "/etc/emqx/certs/server.pem"
    keyfile  = "/etc/emqx/certs/server.key"
  }
}
```

### MQTT安全深度解析

**TLS双向认证（mTLS）**：

```bash
# 生成CA证书
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
    -subj "/CN=IoT CA/O=MyCompany"

# 生成服务器证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/CN=broker.example.com"
openssl x509 -req -days 365 -in server.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

# 生成设备证书（每个设备唯一）
openssl genrsa -out device001.key 2048
openssl req -new -key device001.key -out device001.csr \
    -subj "/CN=device001/O=MyCompany"
openssl x509 -req -days 365 -in device001.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial -out device001.crt
```

**ESP-IDF TLS连接配置**：

```c
// TLS + 双向认证
esp_mqtt_client_config_t tls_cfg = {
    .broker = {
        .address = {
            .hostname  = "broker.example.com",
            .port      = 8883,
            .transport = MQTT_TRANSPORT_OVER_SSL,
        },
        .verification = {
            .certificate = (const char*)ca_crt_start,
            .certificate_len = ca_crt_end - ca_crt_start,
        },
    },
    .credentials = {
        .client_id = "device001",
        .authentication = {
            // 设备证书（双向TLS）
            .certificate     = (const char*)device_crt_start,
            .certificate_len = device_crt_end - device_crt_start,
            .key             = (const char*)device_key_start,
            .key_len         = device_key_end - device_key_start,
        },
    },
};
```


## 完整项目实战：5节点IoT传感器网络

### 系统架构

本项目构建一个完整的IoT传感器网络，包含5个ESP32传感器节点、MQTT Broker、时序数据库和可视化Dashboard。

```
完整系统架构：

┌─────────────────────────────────────────────────────────────────┐
│                        传感器层（5个节点）                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Node 001 │  │ Node 002 │  │ Node 003 │  │ Node 004 │  │ Node 005 │ │
│  │ 温湿度   │  │ 温湿度   │  │ 温湿度   │  │ 空气质量 │  │ 光照强度 │ │
│  │ DHT22    │  │ SHT31    │  │ BME280   │  │ MQ-135  │  │ BH1750  │ │
│  │ ESP32    │  │ ESP32    │  │ ESP32    │  │ ESP32   │  │ ESP32   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  └────┬────┘ │
└───────┼─────────────┼─────────────┼──────────────┼────────────┼──────┘
        │             │             │              │            │
        └─────────────┴─────────────┴──────────────┴────────────┘
                                    │ MQTT (TLS 8883)
                                    ▼
                         ┌──────────────────┐
                         │   EMQX Broker    │
                         │  (Docker容器)    │
                         │  规则引擎         │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
             ┌──────────┐  ┌──────────┐  ┌──────────┐
             │InfluxDB  │  │  Redis   │  │  MySQL   │
             │(时序数据) │  │(实时缓存) │  │(设备注册) │
             └────┬─────┘  └──────────┘  └──────────┘
                  │
                  ▼
             ┌──────────┐
             │ Grafana  │
             │(可视化)  │
             └──────────┘
```

### 物料清单（BOM）

| 序号 | 器件 | 型号 | 数量 | 说明 |
|------|------|------|------|------|
| 1 | 主控模块 | ESP32-WROOM-32D | 5 | WiFi+蓝牙，4MB Flash |
| 2 | 温湿度传感器 | DHT22 | 2 | ±0.5°C，±2%RH |
| 3 | 高精度温湿度 | SHT31-D | 1 | ±0.3°C，±2%RH，I2C |
| 4 | 环境传感器 | BME280 | 1 | 温湿度+气压，I2C/SPI |
| 5 | 空气质量传感器 | MQ-135 | 1 | CO2/NH3/苯，模拟输出 |
| 6 | 光照传感器 | BH1750FVI | 1 | 1-65535 lux，I2C |
| 7 | 开发板 | ESP32 DevKit V1 | 5 | 含USB转串口 |
| 8 | 服务器 | 树莓派4B 4GB | 1 | 运行Docker容器 |
| 9 | 电源 | 5V/2A USB充电器 | 5 | 节点供电 |

### Docker Compose部署（服务器端）

```yaml
# docker-compose.yml
version: '3.8'

services:
  # MQTT Broker
  emqx:
    image: emqx/emqx:5.3.0
    container_name: emqx
    restart: unless-stopped
    ports:
      - "1883:1883"   # MQTT
      - "8883:8883"   # MQTT TLS
      - "8083:8083"   # WebSocket
      - "18083:18083" # Dashboard (admin/public)
    environment:
      - EMQX_NODE_NAME=emqx@127.0.0.1
      - EMQX_DASHBOARD__DEFAULT_PASSWORD=admin123
    volumes:
      - emqx_data:/var/lib/emqx
      - ./emqx/certs:/etc/emqx/certs
    networks:
      - iot_network

  # 时序数据库
  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: unless-stopped
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=admin123456
      - DOCKER_INFLUXDB_INIT_ORG=iot_org
      - DOCKER_INFLUXDB_INIT_BUCKET=sensor_data
      - DOCKER_INFLUXDB_INIT_RETENTION=30d
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-token
    volumes:
      - influxdb_data:/var/lib/influxdb2
    networks:
      - iot_network

  # 数据采集代理（MQTT → InfluxDB）
  telegraf:
    image: telegraf:1.29
    container_name: telegraf
    restart: unless-stopped
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    depends_on:
      - emqx
      - influxdb
    networks:
      - iot_network

  # 可视化
  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-worldmap-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - influxdb
    networks:
      - iot_network

  # Redis（实时状态缓存）
  redis:
    image: redis:7.2-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - iot_network

networks:
  iot_network:
    driver: bridge

volumes:
  emqx_data:
  influxdb_data:
  grafana_data:
```

### Telegraf配置（MQTT订阅→InfluxDB写入）

```toml
# telegraf/telegraf.conf

[agent]
  interval = "10s"
  flush_interval = "10s"
  metric_batch_size = 1000

# 输出：InfluxDB 2.x
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "my-super-secret-token"
  organization = "iot_org"
  bucket = "sensor_data"

# 输入：MQTT订阅
[[inputs.mqtt_consumer]]
  servers = ["tcp://emqx:1883"]
  topics = ["iot/sensor/#"]
  username = "telegraf"
  password = "telegraf_pass"
  client_id = "telegraf_consumer"
  qos = 1
  persistent_session = true

  # 数据格式：JSON
  data_format = "json"
  json_time_key = "timestamp"
  json_time_format = "unix_ms"
  json_string_fields = ["device_id"]

  # 从主题提取标签
  # 主题格式：iot/sensor/{node_id}/data
  [[inputs.mqtt_consumer.topic_parsing]]
    topic = "iot/sensor/+/data"
    measurement = "_"
    tags = "_/sensor/${node_id}/_"
    fields = "_"
```

### 传感器节点固件（完整版）

```c
// sensor_node/main/sensor_node.c
// ESP-IDF v5.x，支持DHT22/SHT31/BME280

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "mqtt_client.h"
#include "cJSON.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

static const char *TAG = "SENSOR_NODE";

// 节点配置（每个节点修改这里）
#define NODE_ID          "node001"
#define SENSOR_TYPE      "DHT22"
#define WIFI_SSID        "your_wifi_ssid"
#define WIFI_PASSWORD    "your_wifi_password"
#define MQTT_BROKER_URI  "mqtt://192.168.1.100:1883"
#define MQTT_USERNAME    "sensor_node"
#define MQTT_PASSWORD    "sensor_pass"

// 主题
#define TOPIC_DATA    "iot/sensor/" NODE_ID "/data"
#define TOPIC_STATUS  "iot/sensor/" NODE_ID "/status"
#define TOPIC_CMD     "iot/control/" NODE_ID "/cmd"

// 上报间隔（毫秒）
#define REPORT_INTERVAL_MS  30000

// WiFi事件组
static EventGroupHandle_t wifi_event_group;
#define WIFI_CONNECTED_BIT BIT0

static esp_mqtt_client_handle_t mqtt_client = NULL;
static bool mqtt_connected = false;

// ─── 传感器读取 ───────────────────────────────────────────────

// DHT22读取（单总线协议）
typedef struct {
    float temperature;
    float humidity;
    bool  valid;
} dht22_data_t;

static dht22_data_t dht22_read(gpio_num_t pin)
{
    dht22_data_t result = {0};
    uint8_t data[5] = {0};

    // 发送起始信号
    gpio_set_direction(pin, GPIO_MODE_OUTPUT);
    gpio_set_level(pin, 0);
    vTaskDelay(pdMS_TO_TICKS(20));  // 低电平20ms
    gpio_set_level(pin, 1);
    esp_rom_delay_us(30);

    // 切换为输入，等待DHT22响应
    gpio_set_direction(pin, GPIO_MODE_INPUT);

    // 等待DHT22拉低（响应信号）
    int timeout = 100;
    while (gpio_get_level(pin) == 1 && timeout-- > 0) esp_rom_delay_us(1);
    if (timeout <= 0) return result;

    // 等待DHT22拉高
    timeout = 100;
    while (gpio_get_level(pin) == 0 && timeout-- > 0) esp_rom_delay_us(1);
    timeout = 100;
    while (gpio_get_level(pin) == 1 && timeout-- > 0) esp_rom_delay_us(1);

    // 读取40位数据
    for (int i = 0; i < 40; i++) {
        // 等待低电平结束
        timeout = 60;
        while (gpio_get_level(pin) == 0 && timeout-- > 0) esp_rom_delay_us(1);

        // 测量高电平时长（>40us为1，<30us为0）
        int high_time = 0;
        while (gpio_get_level(pin) == 1 && high_time < 80) {
            esp_rom_delay_us(1);
            high_time++;
        }

        data[i / 8] <<= 1;
        if (high_time > 40) data[i / 8] |= 1;
    }

    // 校验和验证
    if (data[4] != ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
        ESP_LOGW(TAG, "DHT22 checksum error");
        return result;
    }

    result.humidity    = ((data[0] << 8) | data[1]) / 10.0f;
    result.temperature = (((data[2] & 0x7F) << 8) | data[3]) / 10.0f;
    if (data[2] & 0x80) result.temperature = -result.temperature;
    result.valid = true;

    return result;
}

// ─── MQTT事件处理 ─────────────────────────────────────────────

static void mqtt_event_handler(void *args, esp_event_base_t base,
                                int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t event = event_data;

    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT connected");
            mqtt_connected = true;

            // 订阅控制主题
            esp_mqtt_client_subscribe(mqtt_client, TOPIC_CMD, 1);

            // 发布上线状态
            char status_msg[128];
            snprintf(status_msg, sizeof(status_msg),
                     "{\"status\":\"online\",\"node\":\"%s\","
                     "\"sensor\":\"%s\",\"fw\":\"v1.0.0\"}",
                     NODE_ID, SENSOR_TYPE);
            esp_mqtt_client_publish(mqtt_client, TOPIC_STATUS,
                                    status_msg, 0, 1, 1);
            break;

        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGW(TAG, "MQTT disconnected");
            mqtt_connected = false;
            break;

        case MQTT_EVENT_DATA:
            ESP_LOGI(TAG, "CMD received: %.*s",
                     event->data_len, event->data);
            // 解析并执行控制指令
            cJSON *cmd_json = cJSON_ParseWithLength(event->data,
                                                     event->data_len);
            if (cmd_json) {
                cJSON *cmd = cJSON_GetObjectItem(cmd_json, "cmd");
                if (cJSON_IsString(cmd)) {
                    if (strcmp(cmd->valuestring, "get_status") == 0) {
                        // 立即上报一次数据
                        // （触发传感器任务）
                    } else if (strcmp(cmd->valuestring, "set_interval") == 0) {
                        cJSON *interval = cJSON_GetObjectItem(cmd_json,
                                                               "interval_ms");
                        if (cJSON_IsNumber(interval)) {
                            ESP_LOGI(TAG, "New interval: %d ms",
                                     (int)interval->valuedouble);
                        }
                    }
                }
                cJSON_Delete(cmd_json);
            }
            break;

        default:
            break;
    }
}

// ─── 传感器上报任务 ───────────────────────────────────────────

static void sensor_report_task(void *pvParameters)
{
    // 等待MQTT连接
    while (!mqtt_connected) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    while (1) {
        // 读取传感器
        dht22_data_t sensor = dht22_read(GPIO_NUM_4);

        if (sensor.valid) {
            // 构建JSON载荷
            cJSON *root = cJSON_CreateObject();
            cJSON_AddStringToObject(root, "device_id", NODE_ID);
            cJSON_AddStringToObject(root, "sensor_type", SENSOR_TYPE);
            cJSON_AddNumberToObject(root, "temperature",
                                    roundf(sensor.temperature * 10) / 10.0);
            cJSON_AddNumberToObject(root, "humidity",
                                    roundf(sensor.humidity * 10) / 10.0);
            cJSON_AddNumberToObject(root, "timestamp",
                                    (double)(esp_timer_get_time() / 1000));
            cJSON_AddNumberToObject(root, "rssi",
                                    (double)get_wifi_rssi());

            char *payload = cJSON_PrintUnformatted(root);
            cJSON_Delete(root);

            if (payload) {
                int msg_id = esp_mqtt_client_publish(
                    mqtt_client, TOPIC_DATA,
                    payload, strlen(payload),
                    0, 0  // QoS 0，不保留
                );
                ESP_LOGI(TAG, "Published: %s (msg_id=%d)", payload, msg_id);
                free(payload);
            }
        } else {
            ESP_LOGW(TAG, "Sensor read failed, skipping");
        }

        vTaskDelay(pdMS_TO_TICKS(REPORT_INTERVAL_MS));
    }
}

// ─── WiFi初始化 ───────────────────────────────────────────────

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                                int32_t event_id, void *event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT &&
               event_id == WIFI_EVENT_STA_DISCONNECTED) {
        ESP_LOGW(TAG, "WiFi disconnected, reconnecting...");
        esp_wifi_connect();
        xEventGroupClearBits(wifi_event_group, WIFI_CONNECTED_BIT);
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        ESP_LOGI(TAG, "Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
        xEventGroupSetBits(wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

static void wifi_init_sta(void)
{
    wifi_event_group = xEventGroupCreate();

    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                wifi_event_handler, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
                                wifi_event_handler, NULL);

    wifi_config_t wifi_config = {
        .sta = {
            .ssid     = WIFI_SSID,
            .password = WIFI_PASSWORD,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };

    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    esp_wifi_start();

    // 等待连接
    xEventGroupWaitBits(wifi_event_group, WIFI_CONNECTED_BIT,
                        pdFALSE, pdTRUE, portMAX_DELAY);
}

// ─── 主函数 ───────────────────────────────────────────────────

void app_main(void)
{
    // 初始化NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    esp_netif_init();
    esp_event_loop_create_default();

    // 连接WiFi
    wifi_init_sta();
    ESP_LOGI(TAG, "WiFi connected");

    // 初始化MQTT
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = MQTT_BROKER_URI,
        .credentials = {
            .client_id = "esp32_" NODE_ID,
            .username  = MQTT_USERNAME,
            .authentication.password = MQTT_PASSWORD,
        },
        .session = {
            .keepalive = 60,
            .last_will = {
                .topic   = TOPIC_STATUS,
                .msg     = "{\"status\":\"offline\"}",
                .msg_len = 20,
                .qos     = 1,
                .retain  = true,
            },
        },
        .network.reconnect_timeout_ms = 5000,
    };

    mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(mqtt_client, ESP_EVENT_ANY_ID,
                                   mqtt_event_handler, NULL);
    esp_mqtt_client_start(mqtt_client);

    // 启动传感器上报任务
    xTaskCreate(sensor_report_task, "sensor_report",
                4096, NULL, 5, NULL);

    ESP_LOGI(TAG, "Sensor node %s started", NODE_ID);
}
```

### Grafana Dashboard配置

**数据源配置（InfluxDB 2.x）**：

```json
{
  "name": "IoT InfluxDB",
  "type": "influxdb",
  "url": "http://influxdb:8086",
  "jsonData": {
    "version": "Flux",
    "organization": "iot_org",
    "defaultBucket": "sensor_data",
    "tlsSkipVerify": false
  },
  "secureJsonData": {
    "token": "my-super-secret-token"
  }
}
```

**温度趋势面板（Flux查询）**：

```flux
// 查询过去1小时所有节点的温度数据
from(bucket: "sensor_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "temperature_trend")
```

**实时状态面板（最新值）**：

```flux
// 查询每个节点的最新温湿度
from(bucket: "sensor_data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> last()
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**Grafana告警规则（温度超限）**：

```yaml
# grafana/provisioning/alerting/temperature_alert.yaml
apiVersion: 1
groups:
  - orgId: 1
    name: IoT Alerts
    folder: IoT
    interval: 1m
    rules:
      - uid: temp_high_alert
        title: Temperature High Alert
        condition: C
        data:
          - refId: A
            queryType: ''
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: influxdb_uid
            model:
              query: |
                from(bucket: "sensor_data")
                  |> range(start: -5m)
                  |> filter(fn: (r) => r._field == "temperature")
                  |> last()
          - refId: C
            queryType: ''
            relativeTimeRange:
              from: 0
              to: 0
            datasourceUid: __expr__
            model:
              conditions:
                - evaluator:
                    params: [35]
                    type: gt
                  operator:
                    type: and
                  query:
                    params: [A]
                  reducer:
                    type: last
              type: classic_conditions
        noDataState: NoData
        execErrState: Error
        for: 2m
        annotations:
          summary: "Temperature exceeds 35°C"
          description: "Node {{ $labels.device_id }} temperature is {{ $values.A }}°C"
        labels:
          severity: warning
```

### 系统测试验证

```bash
# 1. 验证MQTT连接
mosquitto_sub -h localhost -t "iot/sensor/#" -v -u sensor_node -P sensor_pass

# 2. 模拟传感器数据（测试用）
mosquitto_pub -h localhost \
  -t "iot/sensor/node001/data" \
  -m '{"device_id":"node001","temperature":25.3,"humidity":65.2,"timestamp":1709000000000}' \
  -u sensor_node -P sensor_pass -q 1

# 3. 验证InfluxDB写入
curl -X POST "http://localhost:8086/api/v2/query?org=iot_org" \
  -H "Authorization: Token my-super-secret-token" \
  -H "Content-Type: application/vnd.flux" \
  -d 'from(bucket:"sensor_data") |> range(start:-5m) |> last()'

# 4. 发送控制指令
mosquitto_pub -h localhost \
  -t "iot/control/node001/cmd" \
  -m '{"cmd":"get_status"}' \
  -u sensor_node -P sensor_pass -q 1

# 5. 查看设备在线状态
mosquitto_sub -h localhost \
  -t "iot/sensor/+/status" \
  -v --retained-only \
  -u sensor_node -P sensor_pass
```


## 性能调优

### 连接数与吞吐量优化

```
EMQX性能调优参数：

# /etc/sysctl.conf（Linux系统级优化）
fs.file-max = 1000000          # 最大文件描述符
net.core.somaxconn = 32768     # TCP连接队列
net.ipv4.tcp_max_syn_backlog = 16384
net.core.netdev_max_backlog = 16384
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
```

```hocon
# EMQX性能配置
node {
  # Erlang进程数上限
  process_limit = 2097152
  # 最大端口数
  max_ports = 1048576
}

listeners.tcp.default {
  max_connections = 1024000
  # 接受器进程数（CPU核心数×2）
  acceptors = 16
}

# 消息队列深度（每个订阅者）
mqtt.max_mqueue_len = 1000
mqtt.mqueue_store_qos0 = false  # QoS0不入队（节省内存）
```

### 带宽优化

```c
// 1. 使用主题别名（MQTT 5.0）减少带宽
// 长主题名 "iot/sensor/building_a/floor_3/room_301/temperature"
// 首次发布时建立别名映射
esp_mqtt5_publish_property_config_t prop = {
    .topic_alias = 1,  // 别名ID=1
};
// 后续发布只发送别名ID，不发送完整主题名
// 节省约50字节/消息

// 2. 压缩Payload（大消息）
// MQTT本身不支持压缩，但可以在应用层压缩
#include "miniz.h"
uint8_t compressed[512];
uLongf comp_len = sizeof(compressed);
compress(compressed, &comp_len,
         (uint8_t*)payload, strlen(payload));
// 发布压缩后的二进制数据

// 3. 使用二进制格式替代JSON（MessagePack）
// JSON: {"temperature":25.3,"humidity":65.2} = 38字节
// MessagePack: 约15字节（节省60%）
```

## 常见问题与调试

### 问题1：频繁断线重连

**现象**：设备每隔几分钟断线，日志显示 `MQTT_EVENT_DISCONNECTED`。

**原因分析**：
```
可能原因：
1. 保活时间（keepalive）设置过短，网络延迟导致心跳超时
2. WiFi信号弱，TCP连接不稳定
3. Broker端连接数超限，主动断开旧连接
4. 路由器NAT超时（通常60-300秒）
5. 设备内存不足，MQTT任务栈溢出
```

**解决方案**：

```c
// 方案1：增大保活时间，启用TCP keepalive
esp_mqtt_client_config_t cfg = {
    .session.keepalive = 120,  // 增大到120秒（默认60）
    .network = {
        .timeout_ms = 15000,   // 连接超时15秒
        .reconnect_timeout_ms = 5000,  // 5秒后重连
        // 启用TCP keepalive（防止NAT超时）
        .disable_auto_reconnect = false,
    },
};

// 方案2：监控断线原因，针对性处理
case MQTT_EVENT_DISCONNECTED:
    ESP_LOGW(TAG, "Disconnected, reason: %d",
             event->error_handle->error_type);
    // 记录断线时间和原因，上报到监控系统
    break;

// 方案3：增大任务栈（防止栈溢出）
// sdkconfig:
// CONFIG_MQTT_TASK_STACK_SIZE=8192  (默认6144)
```

### 问题2：消息顺序错乱

**现象**：订阅者收到的消息顺序与发布顺序不一致。

**原因分析**：
```
MQTT协议本身不保证消息顺序，以下情况会导致乱序：
1. QoS 1重传：消息丢失后重传，可能在新消息之后到达
2. 多路径网络：不同消息走不同网络路径
3. Broker集群：不同节点处理不同消息
4. 并发发布：多线程同时发布到同一主题
```

**解决方案**：

```c
// 方案1：在Payload中加入序列号
static uint32_t seq_num = 0;

void publish_with_sequence(float value)
{
    char payload[128];
    snprintf(payload, sizeof(payload),
             "{\"seq\":%u,\"value\":%.2f,\"ts\":%lld}",
             seq_num++, value,
             (long long)esp_timer_get_time() / 1000);
    esp_mqtt_client_publish(mqtt_client, TOPIC_DATA,
                            payload, 0, 1, 0);
}

// 订阅者端：检测并处理乱序
static uint32_t last_seq = 0;

void on_message(const char *payload)
{
    cJSON *json = cJSON_Parse(payload);
    uint32_t seq = cJSON_GetObjectItem(json, "seq")->valueint;

    if (seq < last_seq) {
        ESP_LOGW(TAG, "Out-of-order message: seq=%u, expected>%u",
                 seq, last_seq);
        // 丢弃或缓存处理
    } else if (seq > last_seq + 1) {
        ESP_LOGW(TAG, "Missing messages: seq=%u, last=%u",
                 seq, last_seq);
        // 记录丢失消息数量
    }
    last_seq = seq;
    cJSON_Delete(json);
}

// 方案2：使用QoS 2（保证顺序，但开销大）
// 仅适用于消息量少、顺序严格要求的场景
```

### 问题3：重复消息（Duplicate Delivery）

**现象**：订阅者收到同一条消息多次（QoS 1/2场景）。

**原因分析**：
```
QoS 1重复原因：
- 发布者未收到PUBACK（网络丢包），重传消息
- Broker未收到订阅者的PUBACK，重传消息
- 设备重启后，持久会话中的消息重新投递

QoS 2重复原因（理论上不应发生）：
- Broker实现Bug
- 网络分区导致状态不一致
```

**解决方案**：

```c
// 方案1：幂等处理（最推荐）
// 在Payload中加入唯一消息ID，处理前检查是否已处理

#include "esp_random.h"

// 发布时生成唯一消息ID
void publish_idempotent(const char *data)
{
    char msg_id[37];  // UUID格式
    uint32_t r[4];
    esp_fill_random(r, sizeof(r));
    snprintf(msg_id, sizeof(msg_id),
             "%08x-%04x-%04x-%04x-%08x%04x",
             r[0], r[1] >> 16, r[1] & 0xFFFF,
             r[2] >> 16, r[2] & 0xFFFF, r[3]);

    char payload[256];
    snprintf(payload, sizeof(payload),
             "{\"msg_id\":\"%s\",\"data\":%s}", msg_id, data);
    esp_mqtt_client_publish(mqtt_client, TOPIC_DATA,
                            payload, 0, 1, 0);
}

// 订阅者端：使用Redis去重
// Python示例
import redis
r = redis.Redis()

def handle_message(payload):
    data = json.loads(payload)
    msg_id = data['msg_id']

    # 检查是否已处理（TTL=1小时）
    if r.set(f"processed:{msg_id}", 1, nx=True, ex=3600):
        # 首次处理
        process_data(data)
    else:
        # 重复消息，忽略
        logger.warning(f"Duplicate message: {msg_id}")
```

### 问题4：Broker过载

**现象**：Broker CPU/内存占用高，消息延迟增大，客户端连接超时。

**诊断方法**：

```bash
# EMQX监控命令
# 查看当前连接数
emqx ctl broker stats | grep connections

# 查看消息速率
emqx ctl broker metrics | grep messages

# 查看订阅数
emqx ctl broker stats | grep subscriptions

# 查看内存使用
emqx ctl vm memory

# 查看进程数
emqx ctl vm process_count
```

**解决方案**：

```
过载处理策略：

1. 水平扩展（推荐）
   → 增加EMQX集群节点
   → 在负载均衡器前端分流

2. 消息速率限制（防止单客户端洪泛）
   # emqx.conf
   mqtt.max_inflight = 32        # 飞行中消息上限
   mqtt.max_mqueue_len = 1000    # 消息队列深度
   
   # 客户端级别限速
   limiter.client.publish.rate = "100/s"  # 每秒最多100条

3. 主题设计优化
   # 避免：每个设备用独立主题（百万主题）
   # 推荐：分层主题，减少订阅数
   
   # 差：每个传感器独立主题
   iot/sensor/node001/temperature
   iot/sensor/node001/humidity
   iot/sensor/node001/pressure
   
   # 好：合并为一条消息
   iot/sensor/node001/data  → {"temp":25.3,"humi":65.2,"pres":1013}

4. QoS降级
   # 高频传感器数据使用QoS 0（减少ACK开销）
   # 只有关键控制指令使用QoS 1/2

5. 消息过期（MQTT 5.0）
   # 设置消息TTL，避免积压过期消息
   message_expiry_interval = 60  # 60秒后过期
```

### 问题5：TLS握手失败

**现象**：设备无法建立TLS连接，日志显示 `SSL handshake failed`。

```c
// 常见原因和解决方案

// 原因1：证书时间不匹配（设备时钟未同步）
// 解决：使用SNTP同步时间
#include "esp_sntp.h"

void sync_time(void)
{
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, "pool.ntp.org");
    sntp_init();

    // 等待时间同步
    time_t now = 0;
    struct tm timeinfo = {0};
    int retry = 0;
    while (timeinfo.tm_year < (2020 - 1900) && ++retry < 10) {
        vTaskDelay(pdMS_TO_TICKS(2000));
        time(&now);
        localtime_r(&now, &timeinfo);
    }
    ESP_LOGI(TAG, "Time synced: %s", asctime(&timeinfo));
}

// 原因2：CA证书不匹配
// 解决：确认使用正确的根CA证书
// 可以临时跳过验证（仅调试用，生产禁止）
esp_mqtt_client_config_t cfg = {
    .broker.verification.skip_cert_common_name_check = true,  // 调试用
};

// 原因3：证书格式错误（DER vs PEM）
// ESP-IDF需要PEM格式（-----BEGIN CERTIFICATE-----）
// 转换命令：
// openssl x509 -in cert.der -inform DER -out cert.pem -outform PEM
```

### 问题6：消息积压（Message Backlog）

**现象**：设备离线后重连，收到大量积压消息，处理不过来。

```c
// 解决方案1：限制离线消息队列深度
// emqx.conf
// mqtt.max_mqueue_len = 100  (默认1000，减小)

// 解决方案2：设置消息过期时间（MQTT 5.0）
// 发布时设置TTL，过期消息不投递

// 解决方案3：设备重连后主动清理积压
// 使用cleanSession=true（MQTT 3.1.1）
// 或sessionExpiryInterval=0（MQTT 5.0）
// 代价：丢失离线消息，但避免积压

// 解决方案4：批量处理积压消息
static int backlog_count = 0;

case MQTT_EVENT_DATA:
    backlog_count++;
    if (backlog_count > 50) {
        // 积压过多，只处理最新消息
        ESP_LOGW(TAG, "Backlog: %d messages, dropping old ones",
                 backlog_count);
        // 快速消费但不处理
    } else {
        process_message(event->data, event->data_len);
    }
    break;

case MQTT_EVENT_BEFORE_CONNECT:
    backlog_count = 0;  // 重置计数
    break;
```

### 调试工具使用

**MQTT Explorer（图形化）**：

```
功能：
- 可视化所有主题树
- 实时查看消息内容
- 发布测试消息
- 查看消息历史
- 支持TLS连接

连接配置：
  Host: broker.emqx.io
  Port: 1883
  Username/Password: 按需填写
  Advanced: 勾选 "Clean Session"
```

**Wireshark抓包分析**：

```bash
# 抓取MQTT流量（端口1883）
wireshark -i eth0 -f "tcp port 1883" -k

# 过滤MQTT报文
# Wireshark过滤器：mqtt
# 查看CONNECT报文：mqtt.msgtype == 1
# 查看PUBLISH报文：mqtt.msgtype == 3
# 查看特定主题：mqtt.topic contains "sensor"
```

**mosquitto_sub 高级用法**：

```bash
# 订阅所有主题（调试用）
mosquitto_sub -h broker.emqx.io -t "#" -v

# 发布测试消息
mosquitto_pub -h broker.emqx.io -t "iot/test" -m '{"value":42}' -q 1

# 查看保留消息
mosquitto_sub -h broker.emqx.io -t "device/status/+" -v --retained-only

# 测试QoS 2
mosquitto_pub -h localhost -t "test/qos2" -m "important" -q 2 -d

# 持久会话测试
mosquitto_sub -h localhost -t "test/#" -q 1 \
    --id "persistent_client" --disable-clean-session
```


## 测试与验证

### 单元测试：MQTT消息格式验证

```python
# tests/test_mqtt_payload.py
# pytest + hypothesis 属性测试
import json
import pytest
from hypothesis import given, strategies as st, settings

# 被测函数：构建传感器数据Payload
def build_sensor_payload(device_id: str, temperature: float,
                          humidity: float, timestamp: int) -> str:
    """构建符合规范的传感器数据JSON"""
    if not device_id or not device_id.strip():
        raise ValueError("device_id cannot be empty")
    if not (-40 <= temperature <= 85):
        raise ValueError(f"Temperature {temperature} out of range")
    if not (0 <= humidity <= 100):
        raise ValueError(f"Humidity {humidity} out of range")

    return json.dumps({
        "device_id": device_id,
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "timestamp": timestamp
    })

# 属性测试1：有效输入总能生成可解析的JSON
# Feature: embedded-docs-enrichment, Property 1: Length Invariant
@given(
    device_id=st.text(min_size=1, max_size=32,
                      alphabet=st.characters(whitelist_categories=('Lu','Ll','Nd'),
                                             whitelist_characters='_-')),
    temperature=st.floats(min_value=-40, max_value=85, allow_nan=False),
    humidity=st.floats(min_value=0, max_value=100, allow_nan=False),
    timestamp=st.integers(min_value=0, max_value=9999999999999)
)
@settings(max_examples=200)
def test_payload_always_valid_json(device_id, temperature, humidity, timestamp):
    """对任意有效输入，生成的Payload必须是合法JSON"""
    payload = build_sensor_payload(device_id, temperature, humidity, timestamp)
    parsed = json.loads(payload)  # 不应抛出异常

    assert parsed["device_id"] == device_id
    assert "temperature" in parsed
    assert "humidity" in parsed
    assert "timestamp" in parsed

# 属性测试2：无效温度范围必须拒绝
@given(
    temperature=st.one_of(
        st.floats(max_value=-40.01, allow_nan=False),
        st.floats(min_value=85.01, allow_nan=False)
    )
)
def test_invalid_temperature_rejected(temperature):
    """超出范围的温度值必须被拒绝"""
    with pytest.raises(ValueError, match="Temperature"):
        build_sensor_payload("node001", temperature, 50.0, 1000000)

# 属性测试3：序列化-反序列化往返
@given(
    temperature=st.floats(min_value=-40, max_value=85, allow_nan=False),
    humidity=st.floats(min_value=0, max_value=100, allow_nan=False),
)
def test_payload_round_trip(temperature, humidity):
    """序列化后反序列化，数值精度保持在0.01以内"""
    payload = build_sensor_payload("node001", temperature, humidity, 1000000)
    parsed = json.loads(payload)

    assert abs(parsed["temperature"] - round(temperature, 2)) < 0.001
    assert abs(parsed["humidity"] - round(humidity, 2)) < 0.001

# 示例测试：边界值
def test_temperature_boundary_values():
    """测试温度边界值"""
    # 最低温度
    p = json.loads(build_sensor_payload("n1", -40.0, 50.0, 0))
    assert p["temperature"] == -40.0

    # 最高温度
    p = json.loads(build_sensor_payload("n1", 85.0, 50.0, 0))
    assert p["temperature"] == 85.0

def test_empty_device_id_rejected():
    """空设备ID必须被拒绝"""
    with pytest.raises(ValueError):
        build_sensor_payload("", 25.0, 60.0, 1000000)

    with pytest.raises(ValueError):
        build_sensor_payload("   ", 25.0, 60.0, 1000000)
```

### 集成测试：MQTT连接验证

```python
# tests/test_mqtt_integration.py
import paho.mqtt.client as mqtt
import threading
import time
import json
import pytest

BROKER_HOST = "localhost"
BROKER_PORT = 1883

class MQTTTestClient:
    """测试用MQTT客户端"""
    def __init__(self, client_id):
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
        self.received_messages = []
        self.connected = threading.Event()

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected.set()

    def _on_message(self, client, userdata, msg):
        self.received_messages.append({
            "topic": msg.topic,
            "payload": msg.payload.decode(),
            "qos": msg.qos
        })

    def connect(self):
        self.client.connect(BROKER_HOST, BROKER_PORT)
        self.client.loop_start()
        return self.connected.wait(timeout=5)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

@pytest.fixture
def mqtt_clients():
    """创建发布者和订阅者"""
    publisher = MQTTTestClient("test_publisher")
    subscriber = MQTTTestClient("test_subscriber")

    assert publisher.connect(), "Publisher failed to connect"
    assert subscriber.connect(), "Subscriber failed to connect"

    yield publisher, subscriber

    publisher.disconnect()
    subscriber.disconnect()

def test_publish_subscribe_qos1(mqtt_clients):
    """QoS 1消息必须被订阅者收到"""
    publisher, subscriber = mqtt_clients
    test_topic = "test/integration/qos1"
    test_payload = '{"value": 42}'

    subscriber.client.subscribe(test_topic, qos=1)
    time.sleep(0.5)  # 等待订阅生效

    publisher.client.publish(test_topic, test_payload, qos=1)
    time.sleep(1)  # 等待消息传递

    assert len(subscriber.received_messages) == 1
    assert subscriber.received_messages[0]["payload"] == test_payload

def test_retained_message(mqtt_clients):
    """保留消息必须被新订阅者立即收到"""
    publisher, subscriber = mqtt_clients
    test_topic = "test/integration/retained"
    test_payload = '{"status": "online"}'

    # 发布保留消息
    publisher.client.publish(test_topic, test_payload, qos=1, retain=True)
    time.sleep(0.5)

    # 新订阅者订阅后应立即收到
    subscriber.client.subscribe(test_topic, qos=1)
    time.sleep(1)

    assert len(subscriber.received_messages) >= 1
    assert subscriber.received_messages[-1]["payload"] == test_payload

    # 清理保留消息
    publisher.client.publish(test_topic, "", qos=1, retain=True)
```

## 延伸阅读

- [NB-IoT窄带物联网](01-nb-iot.html) - 蜂窝物联网通信方案
- [5G嵌入式应用](02-5g-embedded.html) - 高速无线通信
<!-- 以下链接指向的文件路径不正确或文件不存在，待确认后修复
- [数据可视化（Grafana/InfluxDB）](../../../../../../../07-cloud-backend/03-data-analysis-visualization/beginner/03-data-visualization.html) - 传感器数据可视化展示
- [环境控制系统](../../../../../05-actuator-control/advanced/09-environment-control.html) - MQTT在环境控制中的应用
-->
<!-- 以下链接指向的文件不存在，待补充后取消注释
- [智能插座项目](../../../../../05-actuator-control/advanced/07-smart-socket-project.html) - ESP8266 MQTT控制实战
- [自动化控制系统](../../../../../05-actuator-control/advanced/08-automation-system.html) - Modbus与MQTT集成
-->

**外部参考资源**：
- [MQTT Version 5.0 OASIS标准](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- [EMQX官方文档](https://www.emqx.io/docs/zh/v5.0/)
- [ESP-IDF MQTT组件文档](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32/api-reference/protocols/mqtt.html)
- [Paho MQTT客户端库](https://www.eclipse.org/paho/)
- [HiveMQ MQTT Essentials系列教程](https://www.hivemq.com/mqtt-essentials/)

## 参考资料

1. MQTT Version 5.0 - OASIS Standard（官方规范，2019年3月）
2. MQTT Version 3.1.1 - OASIS Standard（ISO/IEC 20922:2016）
3. [EMQX文档](https://www.emqx.io/docs/) - 企业级MQTT Broker
4. [ESP-IDF MQTT API参考](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32/api-reference/protocols/mqtt.html)
5. [coreMQTT](https://github.com/FreeRTOS/coreMQTT) - AWS嵌入式MQTT库（MIT许可）
6. [PubSubClient库](https://pubsubclient.knolleary.net/) - Arduino MQTT库
7. [MQTT.js](https://github.com/mqttjs/MQTT.js) - Node.js/浏览器MQTT客户端
8. [Paho MQTT Python](https://pypi.org/project/paho-mqtt/) - Python MQTT客户端
9. 《MQTT Essentials》- HiveMQ官方教程系列（共11篇）
10. [MQTT Explorer](https://mqtt-explorer.com/) - 图形化MQTT调试工具
11. Sparkplug B规范 - Eclipse Foundation（工业IoT数据格式标准）
12. [AWS IoT Core开发者指南](https://docs.aws.amazon.com/iot/latest/developerguide/)
13. [阿里云IoT平台文档](https://help.aliyun.com/product/30520.html)
14. [Mosquitto文档](https://mosquitto.org/documentation/) - 轻量级MQTT Broker
15. RFC 8446 - TLS 1.3规范（MQTT TLS传输基础）
{% endraw %}
