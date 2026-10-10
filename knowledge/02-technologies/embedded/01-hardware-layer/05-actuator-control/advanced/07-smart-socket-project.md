---
title: "WiFi智能插座项目：远程控制与能耗监测"
description: "完整的WiFi智能插座项目，基于ESP8266/ESP32实现MQTT远程控制、HLW8012能量计量、ACS712电流检测、OTA固件升级、零点检测调光、功率质量监测和过载保护，支持定时任务和App控制"
slug: "wifi-smart-socket-project"

domain: "底层硬件层"
module: "执行器控制"
content_type: "project"
skill_level: "advanced"

tags:
  - 智能插座
  - WiFi控制
  - 继电器
  - MQTT
  - 能耗监测
  - ESP8266
  - HLW8012
  - OTA升级
  - 零点检测
prerequisites:
  - "beginner/04-relay-control"
  - "intermediate/03-mqtt-protocol"
related_contents:
  - "advanced/08-automation-system"
  - "advanced/09-environment-control"
  - "intermediate/03-mqtt-protocol"

estimated_time: 240
difficulty_score: 5

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
  - WiFi智能插座
  - ESP8266继电器
  - MQTT远程控制
  - 能耗监测
  - HLW8012能量计
  - OTA固件升级
  - 零点检测
  - 智能家居
cover_image: ""
---

# WiFi智能插座项目：远程控制与能耗监测

## 概述

本文从零构建一个生产级WiFi智能插座，覆盖从交流电测量理论到完整固件实现的全栈知识。读者将学习：

| 学习目标 | 涉及技术 | 难度 |
|----------|----------|------|
| 交流电功率测量原理 | 真有效值(True RMS)、功率因数、无功功率 | ★★★★ |
| 专用能量计量芯片 | HLW8012/BL0937 脉冲输出计量 | ★★★★ |
| OTA固件升级 | MQTT触发 + HTTP下载 + 分区切换 | ★★★★ |
| 零点检测调光 | 相位角控制 + TRIAC驱动 | ★★★★★ |
| 电能质量监测 | 谐波失真(THD)、功率因数校正 | ★★★★★ |
| 完整项目集成 | 能耗监测 + 定时 + OTA + 本地Web配置 | ★★★★★ |

**前置知识**：
- [继电器控制基础](../beginner/04-relay-control.html)
- [MQTT协议详解](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html)
- C/C++ 基础，Arduino/ESP-IDF 开发环境

**安全警告**：本项目涉及220V/110V交流高压，必须做好绝缘隔离。建议先在低压仿真环境充分测试，再接入市电。所有高压部分须符合当地电气安全法规。


## 背景知识

### 交流电功率测量理论

#### 基本电量定义

交流电路中的功率分析比直流复杂得多，需要理解三种功率的概念：

```
交流电路功率三角形：

        S (视在功率, VA)
       /|
      / |
     /  |
    /θ  |
   /    |
  P-----Q
有功功率  无功功率
(W)      (VAR)

关系式：
  S² = P² + Q²
  P = S × cos(θ)   [有功功率，实际消耗]
  Q = S × sin(θ)   [无功功率，储能/释放]
  cos(θ) = PF      [功率因数 Power Factor]
```

**有功功率 P（Active Power，单位：W）**：
- 实际被负载消耗转化为热能、机械能的功率
- P = U_rms × I_rms × cos(θ)
- 纯电阻负载：cos(θ)=1，P=S

**无功功率 Q（Reactive Power，单位：VAR）**：
- 电感/电容与电源之间交换但不消耗的功率
- 感性负载（电机、变压器）：Q > 0，电流滞后电压
- 容性负载（电容补偿）：Q < 0，电流超前电压

**视在功率 S（Apparent Power，单位：VA）**：
- S = U_rms × I_rms
- 决定供电设备（变压器、导线）的容量需求

**功率因数 PF（Power Factor）**：
- PF = P / S = cos(θ)（纯正弦波情况下）
- 非线性负载（开关电源、变频器）：PF = P / S ≠ cos(θ)，需考虑谐波

#### 真有效值（True RMS）测量

**为什么需要 True RMS？**

普通万用表使用"平均值校正法"测量交流，仅对纯正弦波准确。现代电子设备（开关电源、LED驱动器、变频空调）产生非正弦电流波形，必须用 True RMS 方法：

```
True RMS 数学定义：

         ┌─────────────────────────────┐
         │         1  T              │
I_rms = │ ─── × ∫  i²(t) dt        │
         │         T  0              │
         └─────────────────────────────┘

离散采样实现：
         ┌──────────────────────────────────┐
         │      1   N-1              │
I_rms = │ ─── × Σ  i²[k]           │
         │      N   k=0             │
         └──────────────────────────────────┘

其中 N 为一个完整工频周期内的采样点数
工频50Hz，采样率10kHz → N=200点/周期
```

**采样率要求**：
- 奈奎斯特定理：采样率 ≥ 2 × 最高谐波频率
- 测量到第19次谐波（950Hz）：采样率 ≥ 2kHz
- 实际推荐：10kHz（覆盖到第100次谐波）

**ADC 精度影响**：

| ADC位数 | 分辨率 | 电流测量精度（20A量程） |
|---------|--------|------------------------|
| 10-bit  | 1/1024 | ±20mA（±0.1%）         |
| 12-bit  | 1/4096 | ±5mA（±0.025%）        |
| 16-bit  | 1/65536| ±0.3mA（±0.0015%）     |

ESP8266 内置 10-bit ADC，对于家用插座（0.1A精度要求）已足够。

#### 功率因数与谐波失真

**位移功率因数（Displacement PF）**：
- 仅考虑基波分量的相位差
- DPF = cos(θ₁)，θ₁为基波电压与基波电流的相位差

**总谐波失真（THD，Total Harmonic Distortion）**：

```
         ┌──────────────────────────────────────────┐
         │  √(I₂² + I₃² + I₄² + ... + Iₙ²)       │
THD_I = │ ─────────────────────────────────────── │
         │              I₁                         │
         └──────────────────────────────────────────┘

I₁ = 基波电流有效值
Iₙ = 第n次谐波电流有效值
```

**真功率因数（True PF）**：
- True PF = DPF / √(1 + THD²)
- 开关电源典型值：THD=100%，True PF ≈ 0.7

**谐波危害**：
- 增加线路损耗（I²R，谐波电流也产生热量）
- 导致中性线过载（三相系统中3次谐波叠加）
- 干扰其他设备（EMI）
- 降低变压器效率

### 电气安全标准概述

#### IEC 60884 — 家用插头插座标准

IEC 60884（国际电工委员会）规定了家用和类似用途插头插座的安全要求：

**主要技术要求**：

| 参数 | 要求 |
|------|------|
| 额定电压 | 最高 250V AC |
| 额定电流 | 最高 16A（家用） |
| 绝缘电阻 | ≥ 5MΩ（500V DC测试） |
| 介电强度 | 2000V AC，1分钟无击穿 |
| 接触电阻 | ≤ 5mΩ（每个接触点） |
| 温升限制 | 外壳 ≤ 35K，接线端子 ≤ 45K |
| 机械寿命 | ≥ 5000次插拔 |

**爬电距离与电气间隙**（250V AC，污染等级2）：

```
爬电距离（Creepage Distance）：沿绝缘表面的最短路径
电气间隙（Clearance）：通过空气的最短路径

250V AC 要求：
  爬电距离 ≥ 3.0mm（CTI ≥ 175）
  电气间隙 ≥ 3.0mm（过电压类别 II）

PCB设计中高压与低压之间必须保持足够间距！
```

#### UL 498 — 美国插座标准

UL 498（Underwriters Laboratories）是北美市场的强制认证标准：

**与 IEC 60884 主要差异**：

| 项目 | IEC 60884 | UL 498 |
|------|-----------|--------|
| 额定电压 | 250V | 125V/250V |
| 额定电流 | 16A | 15A/20A |
| 接地要求 | 可选 | 强制（NEMA 5-15） |
| 测试电压 | 2000V | 1500V |
| 温升测试 | 35K | 30°C |

#### GB 2099 — 中国插座标准

中国强制性国家标准，基于 IEC 60884 修改：
- GB 2099.1：家用和类似用途插头插座通用要求
- GB 2099.3：转换器的特殊要求
- 认证标志：CCC（中国强制认证）

**智能插座额外要求**：
- 软件控制的继电器必须有机械互锁或独立硬件过流保护
- 无线通信模块须通过 SRRC（无线电型号核准）
- 数据安全：用户数据不得明文传输

### 系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        智能插座系统架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  220V AC ──┬── HLK-PM01 ──→ 5V ──→ AMS1117-3.3 ──→ 3.3V       │
│            │   (AC/DC)                                           │
│            │                                                     │
│            ├── HLW8012 ──→ CF/CF1脉冲 ──→ ESP8266 GPIO         │
│            │   (能量计量)                                        │
│            │                                                     │
│            ├── 零点检测电路 ──→ ESP8266 INT引脚                  │
│            │   (过零检测)                                        │
│            │                                                     │
│            └── 继电器触点 ──→ 负载输出                           │
│                    ↑                                             │
│              ESP8266 GPIO ──→ ULN2003 ──→ 继电器线圈            │
│                                                                   │
│  ESP8266 ──WiFi──→ MQTT Broker ──→ 手机App/云平台               │
│           ──HTTP──→ OTA服务器 (固件升级)                         │
│           ──HTTP──→ 本地Web配置界面                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```


## 核心内容

### HLW8012/BL0937 能量计量芯片

#### 芯片概述与选型

HLW8012 是专为智能插座设计的单相电能计量 IC，广泛用于小米、公牛等品牌智能插座。BL0937 是其国产替代品，引脚兼容。

**主要特性对比**：

| 特性 | HLW8012 | BL0937 | ADE7953 |
|------|---------|--------|---------|
| 测量参数 | 电压/电流/功率 | 电压/电流/功率 | 电压/电流/功率/无功 |
| 输出方式 | 脉冲频率 | 脉冲频率 | SPI/I2C |
| 精度 | ±1% | ±1% | ±0.1% |
| 工作电压 | 5V | 5V | 3.3V |
| 封装 | SOP-8 | SOP-8 | LFCSP-28 |
| 价格 | ¥1.5 | ¥1.2 | ¥25 |
| 适用场景 | 消费级智能插座 | 消费级智能插座 | 工业电表 |

#### HLW8012 工作原理

```
HLW8012 内部框图：

        ┌─────────────────────────────────────────┐
        │              HLW8012                    │
        │                                         │
VCC ───→│ VCC                                     │
        │         ┌──────────┐                    │
IP+ ───→│ IP+     │          │    CF  ├───→ 功率脉冲
IP- ───→│ IP-     │  Σ-Δ ADC │    CF1 ├───→ 电流/电压脉冲
        │         │          │        │
VP  ───→│ VP      └──────────┘    SEL ├←── 选择输出
        │                              │
GND ───→│ GND                          │
        └─────────────────────────────┘

CF  引脚：功率脉冲输出，频率正比于有功功率
CF1 引脚：电流或电压脉冲输出（由SEL引脚选择）
SEL 引脚：HIGH=电流，LOW=电压
```

**脉冲频率与物理量的关系**：

```
功率计算（CF引脚）：
  P(W) = F_CF × K_P
  K_P = 1 / (F_CF_ref / P_ref)  [校准系数]

电流计算（CF1引脚，SEL=HIGH）：
  I(A) = F_CF1 × K_I

电压计算（CF1引脚，SEL=LOW）：
  U(V) = F_CF1 × K_U

典型参数（5V供电，参考电路）：
  1W  → CF  约 3.4Hz
  1A  → CF1 约 15.6Hz（SEL=HIGH）
  1V  → CF1 约 0.97Hz（SEL=LOW）
```

#### 硬件连接电路

```
HLW8012 参考电路（220V AC 输入）：

                    220V L线
                       │
              ┌────────┤
              │        │
           R1(1MΩ)  电流互感器CT
           R2(1MΩ)     │
           R3(1MΩ)  ┌──┴──┐
              │     │     │
              └──→ VP    IP+/IP-
                    │     │
                  HLW8012 │
                    │     │
                   GND   R_shunt(1mΩ)
                          │
                         GND

注意：
1. 分压电阻 R1+R2+R3 = 3MΩ，将220V分压到安全范围
2. 电流检测使用低阻值分流电阻（1mΩ）或电流互感器
3. 高压侧与低压侧必须保持 ≥ 3mm 爬电距离
4. 建议在 VP 引脚加 TVS 二极管防浪涌
```

#### ESP8266 驱动代码

```cpp
// HLW8012 驱动库（基于脉冲计数）
// 适用：ESP8266 Arduino Core 3.x，HLW8012/BL0937

#include <Arduino.h>

// 引脚定义
#define HLW_CF_PIN   D5   // 功率脉冲输入（中断）
#define HLW_CF1_PIN  D6   // 电流/电压脉冲输入（中断）
#define HLW_SEL_PIN  D7   // 选择引脚

// 校准系数（出厂后需用标准负载校准）
#define HLW_POWER_RATIO    1.0f    // 功率校准系数
#define HLW_CURRENT_RATIO  1.0f    // 电流校准系数
#define HLW_VOLTAGE_RATIO  1.0f    // 电压校准系数

// 测量窗口（毫秒）
#define MEASURE_WINDOW_MS  2000

class HLW8012Driver {
public:
    volatile uint32_t cf_count  = 0;   // 功率脉冲计数
    volatile uint32_t cf1_count = 0;   // 电流/电压脉冲计数
    bool sel_mode = true;               // true=电流，false=电压

    float power_w   = 0.0f;
    float current_a = 0.0f;
    float voltage_v = 0.0f;
    float energy_kwh = 0.0f;

    // 校准系数（通过已知负载校准后写入）
    float k_power   = 12530.0f;  // Hz/W（参考值，需校准）
    float k_current = 25740.0f;  // Hz/A
    float k_voltage = 15420.0f;  // Hz/V

    void begin() {
        pinMode(HLW_CF_PIN,  INPUT_PULLUP);
        pinMode(HLW_CF1_PIN, INPUT_PULLUP);
        pinMode(HLW_SEL_PIN, OUTPUT);
        digitalWrite(HLW_SEL_PIN, HIGH);  // 先测电流
        sel_mode = true;

        // 附加中断（上升沿计数）
        attachInterrupt(digitalPinToInterrupt(HLW_CF_PIN),
                        []() { instance->cf_count++; }, RISING);
        attachInterrupt(digitalPinToInterrupt(HLW_CF1_PIN),
                        []() { instance->cf1_count++; }, RISING);
        instance = this;
    }

    // 每 MEASURE_WINDOW_MS 调用一次，更新测量值
    void update() {
        static uint32_t last_ms = 0;
        static uint32_t last_cf = 0, last_cf1 = 0;
        static float last_power = 0;

        uint32_t now = millis();
        uint32_t dt  = now - last_ms;
        if (dt < MEASURE_WINDOW_MS) return;

        // 读取计数差值（关中断保证原子性）
        noInterrupts();
        uint32_t cf_delta  = cf_count  - last_cf;
        uint32_t cf1_delta = cf1_count - last_cf1;
        last_cf  = cf_count;
        last_cf1 = cf1_count;
        interrupts();

        float dt_s = dt / 1000.0f;

        // 计算功率（CF引脚）
        float cf_hz = cf_delta / dt_s;
        power_w = (cf_hz > 0.5f) ? (cf_hz / k_power * HLW_POWER_RATIO) : 0.0f;

        // 计算电流或电压（CF1引脚）
        float cf1_hz = cf1_delta / dt_s;
        if (sel_mode) {
            // 当前测电流
            current_a = (cf1_hz > 0.5f) ? (cf1_hz / k_current * HLW_CURRENT_RATIO) : 0.0f;
            // 切换到测电压
            sel_mode = false;
            digitalWrite(HLW_SEL_PIN, LOW);
        } else {
            // 当前测电压
            voltage_v = (cf1_hz > 0.5f) ? (cf1_hz / k_voltage * HLW_VOLTAGE_RATIO) : 0.0f;
            // 切换回测电流
            sel_mode = true;
            digitalWrite(HLW_SEL_PIN, HIGH);
        }

        // 累计电能（kWh）
        energy_kwh += power_w * (dt_s / 3600.0f) / 1000.0f;

        // 计算功率因数（需要同时有电压和电流）
        // PF = P / (U × I)
        float apparent = voltage_v * current_a;
        float pf = (apparent > 1.0f) ? (power_w / apparent) : 0.0f;
        pf = constrain(pf, 0.0f, 1.0f);

        last_ms = now;
        last_power = power_w;
    }

    // 校准：使用已知功率的纯电阻负载（如白炽灯）
    // known_power_w: 已知功率（W），known_voltage_v: 已知电压（V）
    void calibrate(float known_power_w, float known_voltage_v) {
        // 测量原始频率
        uint32_t start = millis();
        uint32_t cf_start = cf_count;
        delay(5000);  // 采集5秒
        float cf_hz = (cf_count - cf_start) / 5.0f;
        k_power = cf_hz / known_power_w;
        Serial.printf("校准完成: k_power=%.1f Hz/W\n", k_power);
    }

    float get_power_factor() {
        float apparent = voltage_v * current_a;
        return (apparent > 1.0f) ? constrain(power_w / apparent, 0.0f, 1.0f) : 0.0f;
    }

    static HLW8012Driver* instance;
};

HLW8012Driver* HLW8012Driver::instance = nullptr;
HLW8012Driver hlw;
```

### OTA 固件升级（MQTT触发）

#### OTA 升级流程

```
OTA 升级状态机：

  IDLE ──→ [收到MQTT OTA命令] ──→ DOWNLOADING
    ↑                                    │
    │                              [下载固件]
    │                                    │
    │                              [校验MD5]
    │                                    │
    │                         ┌──────────┴──────────┐
    │                         │                     │
    │                    [校验通过]            [校验失败]
    │                         │                     │
    │                    FLASHING              IDLE(报错)
    │                         │
    │                   [写入Flash]
    │                         │
    └──────────────── [重启完成] ←── REBOOTING
```

#### ESP8266 OTA 实现

```cpp
// OTA 固件升级模块
// 依赖：ESP8266HTTPUpdate 库（Arduino Core 内置）

#include <ESP8266HTTPUpdate.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// OTA 状态
enum OTAState {
    OTA_IDLE,
    OTA_DOWNLOADING,
    OTA_SUCCESS,
    OTA_FAILED
};

OTAState ota_state = OTA_IDLE;
String   ota_url   = "";
String   ota_md5   = "";

// MQTT 命令格式：
// Topic: socket/node001/ota
// Payload: {"url":"http://192.168.1.100/firmware.bin","md5":"abc123...","version":"2.1.0"}

void handle_ota_command(const JsonDocument& doc) {
    if (ota_state != OTA_IDLE) {
        Serial.println("[OTA] 升级进行中，忽略新命令");
        return;
    }
    ota_url = doc["url"].as<String>();
    ota_md5 = doc["md5"].as<String>();
    ota_state = OTA_DOWNLOADING;
    Serial.printf("[OTA] 开始升级: %s\n", ota_url.c_str());
}

// 在主循环中调用（非阻塞触发，实际下载在此函数内阻塞）
void process_ota() {
    if (ota_state != OTA_DOWNLOADING) return;

    // 发布升级开始通知
    mqtt.publish("socket/node001/ota_status",
                 "{\"status\":\"downloading\"}");

    // 设置 MD5 校验
    if (ota_md5.length() == 32) {
        ESPhttpUpdate.setMD5(ota_md5.c_str());
    }

    // 注册回调
    ESPhttpUpdate.onStart([]() {
        Serial.println("[OTA] 开始下载...");
    });
    ESPhttpUpdate.onProgress([](int cur, int total) {
        Serial.printf("[OTA] 进度: %d/%d bytes\n", cur, total);
    });
    ESPhttpUpdate.onEnd([]() {
        Serial.println("[OTA] 下载完成，准备重启");
    });
    ESPhttpUpdate.onError([](int err) {
        Serial.printf("[OTA] 错误: %d\n", err);
    });

    // 执行升级（阻塞直到完成或失败）
    t_httpUpdate_return ret = ESPhttpUpdate.update(wifiClient, ota_url);

    switch (ret) {
        case HTTP_UPDATE_FAILED:
            ota_state = OTA_FAILED;
            {
                char msg[128];
                snprintf(msg, sizeof(msg),
                         "{\"status\":\"failed\",\"error\":\"%s\"}",
                         ESPhttpUpdate.getLastErrorString().c_str());
                mqtt.publish("socket/node001/ota_status", msg);
            }
            break;

        case HTTP_UPDATE_NO_UPDATES:
            ota_state = OTA_IDLE;
            mqtt.publish("socket/node001/ota_status",
                         "{\"status\":\"no_update\"}");
            break;

        case HTTP_UPDATE_OK:
            ota_state = OTA_SUCCESS;
            mqtt.publish("socket/node001/ota_status",
                         "{\"status\":\"success\",\"rebooting\":true}");
            delay(500);
            ESP.restart();  // 重启加载新固件
            break;
    }
}
```

### 本地 Web 配置界面（Captive Portal）

#### 配网与配置流程

```
首次配置流程（Captive Portal）：

用户操作                    ESP8266 行为
─────────────────────────────────────────────────────
1. 长按配置按钮3秒     →  进入AP模式
                           SSID: SmartSocket_XXXX
                           IP:   192.168.4.1

2. 手机连接AP          →  DNS劫持所有域名到192.168.4.1
                           浏览器自动弹出配置页面

3. 填写WiFi/MQTT配置   →  保存到EEPROM/SPIFFS
   点击"保存并重启"

4. ESP8266重启         →  连接配置的WiFi
                           连接MQTT Broker
                           正常工作模式
```

#### Web 服务器实现

```cpp
// 本地 Web 配置服务器
// 依赖：ESP8266WebServer, DNSServer（Arduino Core 内置）

#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <EEPROM.h>

ESP8266WebServer webServer(80);
DNSServer        dnsServer;

// 配置数据结构（存储在 EEPROM）
struct Config {
    char magic[4];        // "CFG\0" 标识有效配置
    char wifi_ssid[32];
    char wifi_pass[64];
    char mqtt_host[64];
    uint16_t mqtt_port;
    char mqtt_user[32];
    char mqtt_pass[32];
    char device_id[16];
    float overload_a;     // 过载阈值（A）
    uint8_t checksum;     // 简单校验和
};

Config cfg;

// 配置页面 HTML（内嵌，无需文件系统）
const char CONFIG_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>智能插座配置</title>
  <style>
    body { font-family: Arial; max-width: 400px; margin: 20px auto; padding: 0 20px; }
    input { width: 100%; padding: 8px; margin: 5px 0 15px; box-sizing: border-box; }
    button { width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; cursor: pointer; }
    h2 { color: #333; }
  </style>
</head>
<body>
  <h2>智能插座配置</h2>
  <form action="/save" method="POST">
    <label>WiFi名称:</label>
    <input name="ssid" value="%SSID%" required>
    <label>WiFi密码:</label>
    <input name="pass" type="password" value="%PASS%">
    <label>MQTT服务器:</label>
    <input name="mqtt_host" value="%MQTT_HOST%" required>
    <label>MQTT端口:</label>
    <input name="mqtt_port" type="number" value="%MQTT_PORT%">
    <label>MQTT用户名:</label>
    <input name="mqtt_user" value="%MQTT_USER%">
    <label>MQTT密码:</label>
    <input name="mqtt_pass" type="password" value="%MQTT_PASS%">
    <label>设备ID:</label>
    <input name="device_id" value="%DEVICE_ID%">
    <label>过载阈值(A):</label>
    <input name="overload" type="number" step="0.1" value="%OVERLOAD%">
    <button type="submit">保存并重启</button>
  </form>
</body>
</html>
)rawliteral";

void start_config_portal() {
    // 启动 AP 模式
    char ap_ssid[32];
    snprintf(ap_ssid, sizeof(ap_ssid), "SmartSocket_%06X",
             (uint32_t)(ESP.getChipId() & 0xFFFFFF));
    WiFi.softAP(ap_ssid, "12345678");
    Serial.printf("[AP] SSID: %s, IP: %s\n",
                  ap_ssid, WiFi.softAPIP().toString().c_str());

    // DNS 劫持（Captive Portal）
    dnsServer.start(53, "*", WiFi.softAPIP());

    // 注册路由
    webServer.on("/", HTTP_GET, []() {
        String html = FPSTR(CONFIG_HTML);
        html.replace("%SSID%",      cfg.wifi_ssid);
        html.replace("%PASS%",      cfg.wifi_pass);
        html.replace("%MQTT_HOST%", cfg.mqtt_host);
        html.replace("%MQTT_PORT%", String(cfg.mqtt_port));
        html.replace("%MQTT_USER%", cfg.mqtt_user);
        html.replace("%MQTT_PASS%", cfg.mqtt_pass);
        html.replace("%DEVICE_ID%", cfg.device_id);
        html.replace("%OVERLOAD%",  String(cfg.overload_a, 1));
        webServer.send(200, "text/html", html);
    });

    webServer.on("/save", HTTP_POST, []() {
        strlcpy(cfg.wifi_ssid,  webServer.arg("ssid").c_str(),     sizeof(cfg.wifi_ssid));
        strlcpy(cfg.wifi_pass,  webServer.arg("pass").c_str(),     sizeof(cfg.wifi_pass));
        strlcpy(cfg.mqtt_host,  webServer.arg("mqtt_host").c_str(),sizeof(cfg.mqtt_host));
        cfg.mqtt_port = webServer.arg("mqtt_port").toInt();
        strlcpy(cfg.mqtt_user,  webServer.arg("mqtt_user").c_str(),sizeof(cfg.mqtt_user));
        strlcpy(cfg.mqtt_pass,  webServer.arg("mqtt_pass").c_str(),sizeof(cfg.mqtt_pass));
        strlcpy(cfg.device_id,  webServer.arg("device_id").c_str(),sizeof(cfg.device_id));
        cfg.overload_a = webServer.arg("overload").toFloat();
        memcpy(cfg.magic, "CFG", 4);
        save_config();
        webServer.send(200, "text/html",
                       "<h2>配置已保存，设备将在3秒后重启...</h2>");
        delay(3000);
        ESP.restart();
    });

    // 捕获所有未知路径（Captive Portal 重定向）
    webServer.onNotFound([]() {
        webServer.sendHeader("Location", "http://192.168.4.1/");
        webServer.send(302, "text/plain", "");
    });

    webServer.begin();
}

void save_config() {
    // 计算校验和
    uint8_t sum = 0;
    uint8_t* p = (uint8_t*)&cfg;
    for (size_t i = 0; i < sizeof(cfg) - 1; i++) sum += p[i];
    cfg.checksum = sum;

    EEPROM.begin(sizeof(Config));
    EEPROM.put(0, cfg);
    EEPROM.commit();
    EEPROM.end();
}

bool load_config() {
    EEPROM.begin(sizeof(Config));
    EEPROM.get(0, cfg);
    EEPROM.end();

    // 验证魔数和校验和
    if (memcmp(cfg.magic, "CFG", 4) != 0) return false;
    uint8_t sum = 0;
    uint8_t* p = (uint8_t*)&cfg;
    for (size_t i = 0; i < sizeof(cfg) - 1; i++) sum += p[i];
    return (sum == cfg.checksum);
}
```


## 深入原理

### 零点检测与相位角调光

#### 零点检测原理

相位角调光（Phase-Angle Dimming）通过在交流电每个半周期的特定时刻触发 TRIAC（双向可控硅），控制负载获得的有效电压，从而调节亮度或功率。

```
相位角调光波形图：

全功率（α=0°）：
  ┌──────────────────────────────────────────────────────┐
  │  正弦波                                              │
  │     ╭──────╮              ╭──────╮                  │
  │    ╱        ╲            ╱        ╲                  │
  │───╱──────────╲──────────╱──────────╲────────────────│
  │              ╲        ╱            ╲        ╱        │
  │               ╲──────╯              ╲──────╯         │
  └──────────────────────────────────────────────────────┘

50%功率（α=90°）：
  ┌──────────────────────────────────────────────────────┐
  │  正弦波（仅后半段导通）                               │
  │     ╭──────╮              ╭──────╮                  │
  │    ╱   ↑   ╲            ╱   ↑   ╲                  │
  │───╱  α=90° ╲──────────╱  α=90° ╲────────────────│
  │              ╲        ╱            ╲        ╱        │
  │               ╲──────╯              ╲──────╯         │
  │  ████████████████████████████████████████████████    │
  │  ↑导通区域（阴影部分）                               │
  └──────────────────────────────────────────────────────┘

有效功率与触发角关系：
  P(α) = P_max × (1 - α/π + sin(2α)/(2π))
  α=0°  → P=100%
  α=90° → P=50%
  α=180°→ P=0%
```

#### 零点检测电路

```
零点检测电路（光耦隔离）：

220V L ──┬── R1(100kΩ) ──┬── R2(100kΩ) ──┐
         │               │               │
         │              D1(1N4148)       │
         │               │               │
220V N ──┴───────────────┴──────────────→ PC817光耦阳极
                                          │
                                         LED
                                          │
                                         GND(高压侧)

PC817光耦集电极 ──→ 3.3V（通过10kΩ上拉）
PC817光耦发射极 ──→ GND（低压侧）
PC817光耦集电极 ──→ ESP8266 GPIO（中断引脚）

工作原理：
- 交流电过零时，光耦 LED 电流最小，输出高电平
- 交流电峰值时，光耦 LED 电流最大，输出低电平
- 每个过零点产生一个上升沿中断
- 50Hz交流：每秒100个过零点（正负各50个）
```

#### 相位角调光实现

```cpp
// 相位角调光控制器
// 注意：调光仅适用于白炽灯、卤素灯、部分调光LED
// 不适用于：开关电源、电机（需使用专用调速器）

#include <Arduino.h>

#define ZC_PIN     D2   // 零点检测输入（中断）
#define TRIAC_PIN  D3   // TRIAC 触发输出

// 调光参数
volatile uint8_t  dimmer_level = 100;  // 0-100%
volatile bool     zc_detected  = false;
volatile uint32_t zc_time_us   = 0;

// 零点检测中断服务程序
ICACHE_RAM_ATTR void zc_isr() {
    zc_time_us = micros();
    zc_detected = true;
}

// 定时器中断：在正确时刻触发 TRIAC
// 50Hz交流：半周期 = 10000μs
// 触发延迟 = (1 - level/100) × 10000μs
void setup_dimmer() {
    pinMode(ZC_PIN,    INPUT_PULLUP);
    pinMode(TRIAC_PIN, OUTPUT);
    digitalWrite(TRIAC_PIN, LOW);

    attachInterrupt(digitalPinToInterrupt(ZC_PIN), zc_isr, RISING);
}

void process_dimmer() {
    if (!zc_detected) return;
    zc_detected = false;

    if (dimmer_level == 0) {
        digitalWrite(TRIAC_PIN, LOW);
        return;
    }
    if (dimmer_level >= 100) {
        // 全功率：直接触发
        digitalWrite(TRIAC_PIN, HIGH);
        delayMicroseconds(100);
        digitalWrite(TRIAC_PIN, LOW);
        return;
    }

    // 计算触发延迟（μs）
    // level=100 → delay=0μs（立即触发）
    // level=50  → delay=5000μs（半周期后触发）
    // level=0   → delay=10000μs（不触发）
    uint32_t delay_us = (uint32_t)((100 - dimmer_level) * 100);  // 0-10000μs

    // 等待到触发时刻
    uint32_t target = zc_time_us + delay_us;
    while (micros() < target) {
        yield();  // 允许 ESP8266 处理 WiFi 任务
    }

    // 触发 TRIAC（脉冲宽度 100μs）
    digitalWrite(TRIAC_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(TRIAC_PIN, LOW);
}

// 设置调光级别（0-100%）
void set_dimmer_level(uint8_t level) {
    dimmer_level = constrain(level, 0, 100);
}
```

**重要限制**：
- 相位角调光会产生大量谐波，THD 可达 100%+
- 不适合容性/感性负载（开关电源、电机）
- 建议仅用于纯电阻负载（白炽灯、电热丝）
- 调光 LED 需要专门的"可调光"型号

### 电能质量监测（THD 与谐波分析）

#### 谐波分析原理

```
谐波分析（离散傅里叶变换 DFT）：

采集 N 个样本（覆盖整数个工频周期）：
  x[0], x[1], ..., x[N-1]

DFT 计算第 k 次谐波幅值：
         N-1
  X[k] = Σ  x[n] × e^(-j2πkn/N)
         n=0

谐波幅值：|X[k]| = √(Re²[k] + Im²[k])
谐波相位：∠X[k] = arctan(Im[k] / Re[k])

对于50Hz基波，N=200点（10kHz采样率）：
  k=1  → 50Hz  基波
  k=3  → 150Hz 3次谐波
  k=5  → 250Hz 5次谐波
  k=7  → 350Hz 7次谐波
  ...
```

#### 简化 THD 计算（ESP8266 实现）

```cpp
// 简化谐波分析（仅计算到第7次谐波）
// 使用 Goertzel 算法（比完整 FFT 更高效）

#define SAMPLE_RATE_HZ  10000   // 10kHz 采样率
#define FUNDAMENTAL_HZ  50      // 工频 50Hz
#define N_SAMPLES       200     // 一个工频周期的样本数

// Goertzel 算法计算单个频率的幅值
float goertzel_magnitude(int16_t* samples, int n, int target_freq, int sample_rate) {
    float k = (float)target_freq * n / sample_rate;
    float omega = 2.0f * M_PI * k / n;
    float coeff = 2.0f * cosf(omega);

    float s0 = 0, s1 = 0, s2 = 0;
    for (int i = 0; i < n; i++) {
        s0 = samples[i] + coeff * s1 - s2;
        s2 = s1;
        s1 = s0;
    }

    float real = s1 - s2 * cosf(omega);
    float imag = s2 * sinf(omega);
    return sqrtf(real * real + imag * imag) / (n / 2.0f);
}

struct PowerQuality {
    float fundamental_a;    // 基波电流（A）
    float harmonics[7];     // 2-8次谐波幅值（A）
    float thd_percent;      // 总谐波失真（%）
    float true_pf;          // 真功率因数
    float displacement_pf;  // 位移功率因数
};

PowerQuality analyze_power_quality(int16_t* current_samples, int n) {
    PowerQuality pq = {};

    // 计算基波和各次谐波
    pq.fundamental_a = goertzel_magnitude(current_samples, n,
                                          FUNDAMENTAL_HZ, SAMPLE_RATE_HZ);

    float harmonic_sum_sq = 0;
    for (int h = 2; h <= 8; h++) {
        pq.harmonics[h-2] = goertzel_magnitude(current_samples, n,
                                                h * FUNDAMENTAL_HZ, SAMPLE_RATE_HZ);
        harmonic_sum_sq += pq.harmonics[h-2] * pq.harmonics[h-2];
    }

    // THD 计算
    if (pq.fundamental_a > 0.01f) {
        pq.thd_percent = 100.0f * sqrtf(harmonic_sum_sq) / pq.fundamental_a;
    }

    // 真功率因数（考虑谐波）
    // True PF = 1 / sqrt(1 + (THD/100)^2) × DPF
    float thd_ratio = pq.thd_percent / 100.0f;
    pq.true_pf = pq.displacement_pf / sqrtf(1.0f + thd_ratio * thd_ratio);

    return pq;
}

// 电能质量报告（通过 MQTT 上报）
void report_power_quality(const PowerQuality& pq) {
    StaticJsonDocument<512> doc;
    doc["fundamental_a"] = serialized(String(pq.fundamental_a, 3));
    doc["thd_percent"]   = serialized(String(pq.thd_percent, 1));
    doc["true_pf"]       = serialized(String(pq.true_pf, 3));

    JsonArray harmonics = doc.createNestedArray("harmonics");
    for (int i = 0; i < 7; i++) {
        harmonics.add(serialized(String(pq.harmonics[i], 3)));
    }

    char buf[512];
    serializeJson(doc, buf);
    mqtt.publish("socket/node001/power_quality", buf);
}
```

#### 电能质量等级评估

```
IEC 61000-3-2 谐波电流限值（A类设备，16A以下）：

次数  限值(A)   典型开关电源  典型白炽灯
─────────────────────────────────────────
3     2.30      1.5A          0.01A
5     1.14      0.8A          0.01A
7     0.77      0.4A          0.01A
9     0.40      0.2A          0.01A
11    0.33      0.1A          0.01A
13    0.21      0.05A         0.01A

评估结论：
  THD < 5%   → 优秀（纯电阻负载）
  THD 5-20%  → 良好（高效LED灯）
  THD 20-50% → 一般（普通开关电源）
  THD > 50%  → 差（劣质充电器、调光器）
```


## 完整项目实战

### 项目规格与物料清单

**项目目标**：制作一个生产级WiFi智能插座，具备能耗监测、定时控制、OTA升级和本地Web配置功能。

**完整物料清单（BOM）**：

| 序号 | 器件 | 型号/规格 | 数量 | 参考价格 | 采购渠道 |
|------|------|-----------|------|----------|----------|
| 1 | 主控模块 | ESP8266 NodeMCU v3 | 1 | ¥12 | 淘宝/立创 |
| 2 | 能量计量IC | HLW8012 SOP-8 | 1 | ¥1.5 | 立创商城 |
| 3 | 继电器 | HF32F-G 5V 10A | 1 | ¥3 | 立创商城 |
| 4 | 继电器驱动 | ULN2003A SOP-16 | 1 | ¥0.5 | 立创商城 |
| 5 | AC/DC电源 | HLK-PM01 5V/600mA | 1 | ¥8 | 淘宝 |
| 6 | LDO稳压 | AMS1117-3.3 SOT-223 | 1 | ¥0.3 | 立创商城 |
| 7 | 零点检测光耦 | PC817 SOP-4 | 1 | ¥0.3 | 立创商城 |
| 8 | 分压电阻 | 1MΩ 1/4W × 3 | 3 | ¥0.1 | 立创商城 |
| 9 | 限流电阻 | 100kΩ 1/4W | 2 | ¥0.1 | 立创商城 |
| 10 | 滤波电容 | 100μF/16V 电解 | 2 | ¥0.5 | 立创商城 |
| 11 | 去耦电容 | 100nF 0805 × 10 | 10 | ¥0.5 | 立创商城 |
| 12 | TVS二极管 | P6KE250A | 1 | ¥1 | 立创商城 |
| 13 | 状态LED | 红/绿 3mm × 2 | 2 | ¥0.2 | 立创商城 |
| 14 | 按键 | 6×6mm 轻触开关 | 1 | ¥0.2 | 立创商城 |
| 15 | PCB | 双面板 50×80mm | 1 | ¥5 | 嘉立创 |
| 16 | 外壳 | 86型插座面板 | 1 | ¥15 | 淘宝 |
| **合计** | | | | **≈¥48** | |

### PCB 布局指南

```
PCB 分区布局（俯视图）：

┌─────────────────────────────────────────────────────────┐
│                    PCB 50×80mm                          │
│                                                         │
│  ┌──────────────┐  ┌──────────────────────────────┐    │
│  │   高压区域   │  │         低压区域              │    │
│  │  (220V AC)   │  │       (3.3V/5V DC)            │    │
│  │              │  │                               │    │
│  │  HLK-PM01    │  │  ESP8266    HLW8012           │    │
│  │  继电器      │  │  NodeMCU    能量计量           │    │
│  │  TVS二极管   │  │                               │    │
│  │              │  │  ULN2003    AMS1117           │    │
│  │  ← 3mm间距 →│  │  继电器驱动  LDO              │    │
│  └──────────────┘  └──────────────────────────────┘    │
│                                                         │
│  ← 高压区爬电距离 ≥ 3mm，建议开槽隔离 →                │
│                                                         │
│  接地平面：低压 GND 与高压 GND 单点连接（安全地）       │
└─────────────────────────────────────────────────────────┘

关键布局规则：
1. 高压区与低压区之间开 V 形槽（增加爬电距离）
2. HLW8012 分压电阻靠近 VP 引脚放置
3. 去耦电容紧靠 IC 电源引脚
4. 继电器线圈并联续流二极管（1N4007）
5. 零点检测光耦放在高低压边界处
```

### 完整固件实现

```cpp
// 智能插座完整固件
// 硬件：ESP8266 NodeMCU v3
// 依赖库：
//   - PubSubClient 2.8.0 (MQTT)
//   - ArduinoJson 6.21.0
//   - ESP8266HTTPUpdate (内置)
//   - ESP8266WebServer (内置)
//   - NTPClient 3.2.1 (时间同步)

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPUpdate.h>
#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <EEPROM.h>
#include <Ticker.h>

// ─── 引脚定义 ───────────────────────────────────────────
#define RELAY_PIN    D1   // 继电器（低电平触发）
#define LED_R_PIN    D4   // 红色LED（低电平亮）
#define LED_G_PIN    D0   // 绿色LED（低电平亮）
#define BTN_PIN      D3   // 配置按键（低电平按下）
#define HLW_CF_PIN   D5   // HLW8012 功率脉冲
#define HLW_CF1_PIN  D6   // HLW8012 电流/电压脉冲
#define HLW_SEL_PIN  D7   // HLW8012 选择引脚
#define ZC_PIN       D2   // 零点检测

// ─── 全局对象 ────────────────────────────────────────────
WiFiClient       wifiClient;
PubSubClient     mqtt(wifiClient);
ESP8266WebServer webServer(80);
DNSServer        dnsServer;
WiFiUDP          ntpUDP;
NTPClient        timeClient(ntpUDP, "pool.ntp.org", 28800);  // UTC+8
Ticker           reportTicker;
Ticker           timerTicker;

// ─── 状态变量 ────────────────────────────────────────────
bool     relay_state    = false;
bool     config_mode    = false;
uint32_t boot_time_ms   = 0;

// ─── HLW8012 测量数据 ────────────────────────────────────
volatile uint32_t hlw_cf_count  = 0;
volatile uint32_t hlw_cf1_count = 0;
bool     hlw_sel_mode   = true;   // true=电流，false=电压
float    meas_power_w   = 0;
float    meas_current_a = 0;
float    meas_voltage_v = 220.0f; // 默认220V（无电压测量时）
float    meas_energy_kwh = 0;
float    meas_pf        = 0;

// HLW8012 校准系数（出厂校准后存入EEPROM）
float k_power   = 12530.0f;
float k_current = 25740.0f;
float k_voltage = 15420.0f;

// ─── 定时任务 ────────────────────────────────────────────
struct TimerTask {
    uint8_t  hour, minute;
    bool     action;
    bool     enabled;
    uint8_t  weekdays;  // bit0=周日...bit6=周六
};
#define MAX_TIMERS 8
TimerTask timers[MAX_TIMERS] = {};

// ─── 配置结构 ────────────────────────────────────────────
struct Config {
    char     magic[4];
    char     wifi_ssid[32];
    char     wifi_pass[64];
    char     mqtt_host[64];
    uint16_t mqtt_port;
    char     mqtt_user[32];
    char     mqtt_pass[32];
    char     device_id[16];
    float    overload_a;
    float    k_power;
    float    k_current;
    float    k_voltage;
    TimerTask timers[MAX_TIMERS];
    uint8_t  checksum;
} cfg;

// ─── MQTT 主题 ───────────────────────────────────────────
char TOPIC_CTRL[64];
char TOPIC_STATUS[64];
char TOPIC_ALERT[64];
char TOPIC_OTA[64];
char TOPIC_POWER_QUALITY[64];

// ─── 中断服务程序 ────────────────────────────────────────
ICACHE_RAM_ATTR void hlw_cf_isr()  { hlw_cf_count++;  }
ICACHE_RAM_ATTR void hlw_cf1_isr() { hlw_cf1_count++; }

// ─── 继电器控制 ──────────────────────────────────────────
void relay_set(bool on) {
    relay_state = on;
    digitalWrite(RELAY_PIN, on ? LOW : HIGH);
    digitalWrite(LED_G_PIN, on ? LOW : HIGH);
    // 保存状态
    EEPROM.write(sizeof(Config), on ? 1 : 0);
    EEPROM.commit();
}

// ─── HLW8012 更新 ────────────────────────────────────────
void hlw_update() {
    static uint32_t last_ms  = 0;
    static uint32_t last_cf  = 0;
    static uint32_t last_cf1 = 0;

    uint32_t now = millis();
    uint32_t dt  = now - last_ms;
    if (dt < 2000) return;

    noInterrupts();
    uint32_t cf_d  = hlw_cf_count  - last_cf;
    uint32_t cf1_d = hlw_cf1_count - last_cf1;
    last_cf  = hlw_cf_count;
    last_cf1 = hlw_cf1_count;
    interrupts();

    float dt_s = dt / 1000.0f;
    float cf_hz  = cf_d  / dt_s;
    float cf1_hz = cf1_d / dt_s;

    meas_power_w = (cf_hz > 0.5f) ? (cf_hz / k_power) : 0.0f;

    if (hlw_sel_mode) {
        meas_current_a = (cf1_hz > 0.5f) ? (cf1_hz / k_current) : 0.0f;
        hlw_sel_mode = false;
        digitalWrite(HLW_SEL_PIN, LOW);
    } else {
        meas_voltage_v = (cf1_hz > 0.5f) ? (cf1_hz / k_voltage) : 220.0f;
        hlw_sel_mode = true;
        digitalWrite(HLW_SEL_PIN, HIGH);
    }

    // 累计电能
    meas_energy_kwh += meas_power_w * (dt_s / 3600.0f) / 1000.0f;

    // 功率因数
    float apparent = meas_voltage_v * meas_current_a;
    meas_pf = (apparent > 1.0f) ? constrain(meas_power_w / apparent, 0.0f, 1.0f) : 0.0f;

    last_ms = now;
}

// ─── 过载保护 ────────────────────────────────────────────
void check_overload() {
    static uint32_t overload_start = 0;
    if (!relay_state) { overload_start = 0; return; }

    if (meas_current_a > cfg.overload_a) {
        if (overload_start == 0) overload_start = millis();
        else if (millis() - overload_start > 2000) {
            relay_set(false);
            overload_start = 0;
            digitalWrite(LED_R_PIN, LOW);  // 红灯亮表示故障

            StaticJsonDocument<128> doc;
            doc["type"]    = "overload";
            doc["current"] = serialized(String(meas_current_a, 2));
            doc["limit"]   = cfg.overload_a;
            char buf[128];
            serializeJson(doc, buf);
            mqtt.publish(TOPIC_ALERT, buf);
        }
    } else {
        overload_start = 0;
        digitalWrite(LED_R_PIN, HIGH);  // 红灯灭
    }
}

// ─── 定时任务检查 ────────────────────────────────────────
void check_timers() {
    if (!timeClient.isTimeSet()) return;
    int hour    = timeClient.getHours();
    int minute  = timeClient.getMinutes();
    int weekday = timeClient.getDay();  // 0=周日

    for (int i = 0; i < MAX_TIMERS; i++) {
        if (!timers[i].enabled) continue;
        if (!(timers[i].weekdays & (1 << weekday))) continue;
        if (timers[i].hour == hour && timers[i].minute == minute) {
            // 防止同一分钟内重复触发
            static uint32_t last_trigger[MAX_TIMERS] = {};
            uint32_t now = millis();
            if (now - last_trigger[i] > 60000) {
                relay_set(timers[i].action);
                last_trigger[i] = now;
            }
        }
    }
}

// ─── 状态上报 ────────────────────────────────────────────
void report_status() {
    if (!mqtt.connected()) return;

    StaticJsonDocument<384> doc;
    doc["state"]    = relay_state;
    doc["current"]  = serialized(String(meas_current_a, 2));
    doc["voltage"]  = serialized(String(meas_voltage_v, 1));
    doc["power"]    = serialized(String(meas_power_w, 1));
    doc["energy"]   = serialized(String(meas_energy_kwh, 4));
    doc["pf"]       = serialized(String(meas_pf, 3));
    doc["uptime"]   = (millis() - boot_time_ms) / 1000;
    doc["rssi"]     = WiFi.RSSI();
    doc["ip"]       = WiFi.localIP().toString();

    char buf[384];
    serializeJson(doc, buf);
    mqtt.publish(TOPIC_STATUS, buf, true);  // 保留消息
}

// ─── MQTT 消息处理 ───────────────────────────────────────
void on_mqtt_message(char* topic, byte* payload, unsigned int len) {
    StaticJsonDocument<512> doc;
    if (deserializeJson(doc, payload, len) != DeserializationError::Ok) return;

    if (strcmp(topic, TOPIC_CTRL) == 0) {
        const char* cmd = doc["cmd"];
        if      (!cmd)                    return;
        else if (strcmp(cmd, "on")     == 0) relay_set(true);
        else if (strcmp(cmd, "off")    == 0) relay_set(false);
        else if (strcmp(cmd, "toggle") == 0) relay_set(!relay_state);
        else if (strcmp(cmd, "query")  == 0) report_status();
        else if (strcmp(cmd, "reset_energy") == 0) meas_energy_kwh = 0;
        else if (strcmp(cmd, "set_timer") == 0) {
            int id = doc["id"] | -1;
            if (id >= 0 && id < MAX_TIMERS) {
                timers[id].hour     = doc["hour"]     | 0;
                timers[id].minute   = doc["minute"]   | 0;
                timers[id].action   = doc["action"]   | false;
                timers[id].weekdays = doc["weekdays"] | 0x7F;
                timers[id].enabled  = true;
                memcpy(cfg.timers, timers, sizeof(timers));
                save_config();
            }
        }
    } else if (strcmp(topic, TOPIC_OTA) == 0) {
        handle_ota_command(doc);
    }
}

// ─── MQTT 重连 ───────────────────────────────────────────
void mqtt_reconnect() {
    if (mqtt.connected()) return;
    static uint32_t last_attempt = 0;
    if (millis() - last_attempt < 5000) return;
    last_attempt = millis();

    // 遗嘱消息（设备离线时自动发布）
    char will_msg[64];
    snprintf(will_msg, sizeof(will_msg),
             "{\"state\":\"offline\",\"id\":\"%s\"}", cfg.device_id);

    if (mqtt.connect(cfg.device_id, cfg.mqtt_user, cfg.mqtt_pass,
                     TOPIC_STATUS, 1, true, will_msg)) {
        mqtt.subscribe(TOPIC_CTRL);
        mqtt.subscribe(TOPIC_OTA);
        // 上线通知
        char online_msg[64];
        snprintf(online_msg, sizeof(online_msg),
                 "{\"state\":\"online\",\"id\":\"%s\"}", cfg.device_id);
        mqtt.publish(TOPIC_STATUS, online_msg, true);
        Serial.println("[MQTT] 已连接");
    }
}

// ─── 初始化 ──────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    boot_time_ms = millis();

    // GPIO 初始化
    pinMode(RELAY_PIN,   OUTPUT);
    pinMode(LED_R_PIN,   OUTPUT);
    pinMode(LED_G_PIN,   OUTPUT);
    pinMode(BTN_PIN,     INPUT_PULLUP);
    pinMode(HLW_CF_PIN,  INPUT_PULLUP);
    pinMode(HLW_CF1_PIN, INPUT_PULLUP);
    pinMode(HLW_SEL_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH);   // 继电器默认断开
    digitalWrite(LED_R_PIN, HIGH);   // LED 默认灭
    digitalWrite(LED_G_PIN, HIGH);
    digitalWrite(HLW_SEL_PIN, HIGH); // 先测电流

    // 加载配置
    if (!load_config()) {
        // 无有效配置，进入配置模式
        Serial.println("[CFG] 无配置，进入AP配置模式");
        config_mode = true;
        start_config_portal();
        return;
    }

    // 恢复上次继电器状态
    EEPROM.begin(sizeof(Config) + 1);
    bool saved_state = EEPROM.read(sizeof(Config));
    relay_set(saved_state);

    // 复制定时任务
    memcpy(timers, cfg.timers, sizeof(timers));

    // 设置 MQTT 主题
    snprintf(TOPIC_CTRL,          sizeof(TOPIC_CTRL),
             "socket/%s/control", cfg.device_id);
    snprintf(TOPIC_STATUS,        sizeof(TOPIC_STATUS),
             "socket/%s/status",  cfg.device_id);
    snprintf(TOPIC_ALERT,         sizeof(TOPIC_ALERT),
             "socket/%s/alert",   cfg.device_id);
    snprintf(TOPIC_OTA,           sizeof(TOPIC_OTA),
             "socket/%s/ota",     cfg.device_id);
    snprintf(TOPIC_POWER_QUALITY, sizeof(TOPIC_POWER_QUALITY),
             "socket/%s/power_quality", cfg.device_id);

    // 连接 WiFi
    WiFi.begin(cfg.wifi_ssid, cfg.wifi_pass);
    Serial.printf("[WiFi] 连接 %s ...\n", cfg.wifi_ssid);
    uint32_t wifi_start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - wifi_start < 15000) {
        delay(500);
        Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] 已连接，IP: %s\n",
                      WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[WiFi] 连接失败，进入配置模式");
        config_mode = true;
        start_config_portal();
        return;
    }

    // NTP 时间同步
    timeClient.begin();
    timeClient.update();

    // MQTT 初始化
    mqtt.setServer(cfg.mqtt_host, cfg.mqtt_port);
    mqtt.setCallback(on_mqtt_message);
    mqtt.setBufferSize(512);
    mqtt_reconnect();

    // HLW8012 中断
    attachInterrupt(digitalPinToInterrupt(HLW_CF_PIN),  hlw_cf_isr,  RISING);
    attachInterrupt(digitalPinToInterrupt(HLW_CF1_PIN), hlw_cf1_isr, RISING);

    // 定时上报（每10秒）
    reportTicker.attach(10, report_status);
    // 定时任务检查（每分钟）
    timerTicker.attach(60, check_timers);

    Serial.println("[INIT] 初始化完成");
}

// ─── 主循环 ──────────────────────────────────────────────
void loop() {
    if (config_mode) {
        dnsServer.processNextRequest();
        webServer.handleClient();
        return;
    }

    // 长按按键3秒进入配置模式
    static uint32_t btn_press_ms = 0;
    if (digitalRead(BTN_PIN) == LOW) {
        if (btn_press_ms == 0) btn_press_ms = millis();
        else if (millis() - btn_press_ms > 3000) {
            Serial.println("[BTN] 长按，进入配置模式");
            config_mode = true;
            start_config_portal();
            return;
        }
    } else {
        if (btn_press_ms > 0 && millis() - btn_press_ms < 1000) {
            // 短按：切换继电器
            relay_set(!relay_state);
        }
        btn_press_ms = 0;
    }

    // MQTT 维护
    if (!mqtt.connected()) mqtt_reconnect();
    mqtt.loop();

    // HLW8012 测量更新
    hlw_update();

    // 过载保护
    check_overload();

    // OTA 处理
    process_ota();

    // NTP 每小时同步一次
    static uint32_t last_ntp = 0;
    if (millis() - last_ntp > 3600000) {
        timeClient.update();
        last_ntp = millis();
    }
}
```

### 性能调优

#### WiFi 功耗优化

```cpp
// 降低 WiFi 发射功率（减少干扰，降低功耗）
WiFi.setOutputPower(17.5);  // 默认20.5dBm，降至17.5dBm

// 启用 Modem Sleep（MQTT 空闲时降低功耗）
// 注意：Modem Sleep 会增加 MQTT 延迟
WiFi.setSleepMode(WIFI_MODEM_SLEEP);

// 固定 IP（避免 DHCP 延迟）
IPAddress ip(192, 168, 1, 100);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
WiFi.config(ip, gateway, subnet);
```

#### MQTT 消息优化

```cpp
// 使用 QoS 0 减少握手开销（状态上报不需要可靠传输）
mqtt.publish(TOPIC_STATUS, buf, false);  // QoS 0，不保留

// 使用 QoS 1 保证控制命令可靠（继电器控制需要确认）
// PubSubClient 默认 QoS 0，控制命令建议在应用层加确认

// 批量上报（减少 MQTT 连接次数）
// 将多个测量值合并到一个 JSON 消息
```



### 完整项目集成测试

#### 功能测试清单

| 测试项 | 测试步骤 | 预期结果 | 通过标准 |
|--------|----------|----------|----------|
| 1. 基本开关 | MQTT发送 `{"cmd":"on"}` | 继电器吸合，绿灯亮 | 延迟 < 500ms |
| 2. 能耗测量 | 接入100W白炽灯 | 功率显示 95-105W | 误差 < 5% |
| 3. 过载保护 | 接入超过阈值负载 | 2秒后自动断开，红灯亮 | 保护动作正常 |
| 4. 定时任务 | 设置定时开关 | 到时自动执行 | 时间误差 < 1分钟 |
| 5. OTA升级 | 发送OTA命令 | 下载并重启，版本更新 | 升级成功率 > 95% |
| 6. 配网功能 | 长按按键3秒 | 进入AP模式，手机可连接 | 配置页面正常显示 |
| 7. 断电记忆 | 断电后重新上电 | 恢复断电前状态 | 状态保持一致 |
| 8. WiFi重连 | 路由器重启 | 自动重连 | 重连时间 < 30秒 |

#### 安全测试

```
电气安全测试（必须由专业人员使用专业设备进行）：

1. 绝缘电阻测试：
   - 测试仪器：兆欧表（500V DC）
   - 测试点：高压侧 ↔ 低压侧
   - 合格标准：≥ 5MΩ

2. 介电强度测试：
   - 测试仪器：耐压测试仪
   - 测试电压：2000V AC，持续1分钟
   - 合格标准：无击穿、无闪络

3. 接触电阻测试：
   - 测试仪器：微欧计
   - 测试点：继电器触点
   - 合格标准：≤ 5mΩ

4. 温升测试：
   - 测试条件：额定负载，连续运行2小时
   - 测试点：外壳、接线端子、继电器
   - 合格标准：外壳温升 ≤ 35K，端子温升 ≤ 45K

5. EMC测试（可选，认证必需）：
   - 传导骚扰：EN 55014-1
   - 辐射骚扰：EN 55014-1
   - 抗扰度：EN 55014-2
```

#### 长期稳定性测试

```
老化测试方案：

测试时长：7×24小时（168小时）
测试负载：额定功率的80%（如10A插座接8A负载）
测试周期：
  - 每小时开关一次（模拟日常使用）
  - 每6小时记录一次温度、功率、电流
  - 每24小时检查一次继电器触点

监测指标：
  ✓ 继电器动作次数：≥ 168次
  ✓ 测量精度漂移：< 2%
  ✓ WiFi断线次数：< 5次
  ✓ MQTT消息丢失率：< 0.1%
  ✓ 外壳最高温度：< 60°C
  ✓ 继电器触点电阻增长：< 10%

合格标准：
  - 所有监测指标在范围内
  - 无自动重启
  - 无功能异常
```


## 常见问题与调试

### WiFi 连接问题

#### 问题1：WiFi 连接失败或频繁断线

**症状**：
- 串口输出 `[WiFi] 连接失败`
- 设备反复重启
- MQTT 消息延迟或丢失

**可能原因与解决方案**：

| 原因 | 诊断方法 | 解决方案 |
|------|----------|----------|
| 信号弱 | 检查 RSSI < -75dBm | 移近路由器或增加中继器 |
| 信道拥挤 | 使用 WiFi 分析仪 | 路由器切换到1/6/11信道 |
| DHCP 冲突 | 检查路由器日志 | 设置静态 IP |
| 功耗不足 | 测量 3.3V 电压 | 更换更大容量电源模块 |
| 天线问题 | 对比其他 ESP8266 | 更换模块或外接天线 |

**调试代码**：

```cpp
// WiFi 诊断信息
void wifi_diagnostics() {
    Serial.printf("[WiFi] SSID: %s\n", WiFi.SSID().c_str());
    Serial.printf("[WiFi] RSSI: %d dBm\n", WiFi.RSSI());
    Serial.printf("[WiFi] Channel: %d\n", WiFi.channel());
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[WiFi] Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
    Serial.printf("[WiFi] DNS: %s\n", WiFi.dnsIP().toString().c_str());
    Serial.printf("[WiFi] MAC: %s\n", WiFi.macAddress().c_str());
}

// WiFi 事件监听
WiFi.onStationModeDisconnected([](const WiFiEventStationModeDisconnected& evt) {
    Serial.printf("[WiFi] 断开连接，原因: %d\n", evt.reason);
    // 原因代码：
    // 2  = AUTH_EXPIRE（认证超时）
    // 3  = AUTH_LEAVE（主动断开）
    // 4  = ASSOC_EXPIRE（关联超时）
    // 8  = ASSOC_LEAVE（AP 踢出）
    // 15 = 4WAY_HANDSHAKE_TIMEOUT（握手超时）
    // 201= NO_AP_FOUND（找不到AP）
});
```

#### 问题2：配网模式无法进入

**症状**：
- 长按按键3秒无反应
- 手机搜不到 AP

**解决方案**：

```cpp
// 强制进入配网模式（调试用）
// 在 setup() 开头添加：
if (digitalRead(BTN_PIN) == LOW) {
    delay(100);
    if (digitalRead(BTN_PIN) == LOW) {
        Serial.println("[DEBUG] 强制进入配网模式");
        config_mode = true;
        start_config_portal();
        while(1) {
            dnsServer.processNextRequest();
            webServer.handleClient();
            yield();
        }
    }
}

// 或者通过串口命令触发
if (Serial.available()) {
    char c = Serial.read();
    if (c == 'C' || c == 'c') {
        config_mode = true;
        start_config_portal();
    }
}
```

### 继电器控制问题

#### 问题3：继电器抖动或无法吸合

**症状**：
- 继电器发出"嗒嗒"声
- 继电器吸合后立即释放
- 负载无法正常工作

**可能原因**：

```
1. 驱动电流不足：
   - ULN2003 输出电流 < 继电器线圈电流
   - 解决：更换大电流驱动（如 ULN2803）或使用 MOSFET

2. 电源纹波过大：
   - 5V 电源带载能力不足
   - 解决：在继电器线圈并联 100μF 电容

3. 续流二极管缺失或反接：
   - 线圈断电时产生反向电动势
   - 解决：检查 1N4007 二极管方向（阴极接 VCC）

4. GPIO 输出电平错误：
   - 低电平触发继电器，但 GPIO 输出高电平
   - 解决：检查代码逻辑，确保 digitalWrite(RELAY_PIN, LOW) 吸合
```

**测试代码**：

```cpp
// 继电器测试程序（独立运行）
void relay_test() {
    Serial.println("[TEST] 继电器测试开始");
    for (int i = 0; i < 10; i++) {
        Serial.printf("[TEST] 第 %d 次吸合\n", i+1);
        digitalWrite(RELAY_PIN, LOW);   // 吸合
        delay(1000);
        Serial.printf("[TEST] 第 %d 次释放\n", i+1);
        digitalWrite(RELAY_PIN, HIGH);  // 释放
        delay(1000);
    }
    Serial.println("[TEST] 继电器测试完成");
}
```

### HLW8012 测量问题

#### 问题4：功率/电流测量不准确

**症状**：
- 测量值偏差 > 10%
- 空载时显示非零功率
- 电压显示异常

**校准步骤**：

```cpp
// HLW8012 校准程序
// 需要：标准功率计、纯电阻负载（如100W白炽灯）

void hlw_calibration() {
    Serial.println("[CAL] HLW8012 校准开始");
    Serial.println("[CAL] 请接入已知功率的纯电阻负载（如100W白炽灯）");
    Serial.println("[CAL] 使用标准功率计测量实际功率");
    Serial.println("[CAL] 输入实际功率值（W）：");

    while (!Serial.available()) delay(100);
    float actual_power = Serial.parseFloat();

    Serial.println("[CAL] 采集5秒数据...");
    uint32_t cf_start = hlw_cf_count;
    delay(5000);
    uint32_t cf_end = hlw_cf_count;
    float cf_hz = (cf_end - cf_start) / 5.0f;

    k_power = cf_hz / actual_power;
    cfg.k_power = k_power;
    save_config();

    Serial.printf("[CAL] 校准完成！k_power = %.1f Hz/W\n", k_power);
    Serial.printf("[CAL] 测量频率: %.1f Hz\n", cf_hz);
    Serial.printf("[CAL] 实际功率: %.1f W\n", actual_power);
}

// 在 setup() 中添加串口命令触发
if (Serial.available() && Serial.read() == 'K') {
    hlw_calibration();
}
```

**常见测量误差来源**：

| 误差来源 | 影响 | 解决方案 |
|----------|------|----------|
| 分压电阻误差 | 电压测量偏差 | 使用 1% 精度电阻 |
| 温度漂移 | 长期运行精度下降 | 定期重新校准 |
| 非线性负载 | 功率因数 < 1 | 使用真有效值测量 |
| 电源纹波 | 测量抖动 | 加强滤波电容 |
| PCB 布线 | 高频干扰 | 缩短 HLW8012 到采样点距离 |

#### 问题5：ACS712 电流传感器噪声大

**症状**：
- 电流读数跳动 ± 0.5A
- 空载时显示 0.2-0.3A

**解决方案**：

```cpp
// ACS712 软件滤波（移动平均）
#define ACS712_PIN A0
#define ACS712_SAMPLES 50

float read_acs712_current() {
    long sum = 0;
    for (int i = 0; i < ACS712_SAMPLES; i++) {
        sum += analogRead(ACS712_PIN);
        delayMicroseconds(100);
    }
    float avg = sum / (float)ACS712_SAMPLES;

    // ACS712-20A：2.5V = 0A，灵敏度 100mV/A
    // ESP8266 ADC：0-1V → 0-1023
    float voltage = avg * (1.0f / 1023.0f);  // 0-1V
    float current = (voltage - 0.5f) / 0.1f;  // (V - Vref) / 灵敏度

    // 死区处理（< 0.1A 视为 0）
    if (fabs(current) < 0.1f) current = 0.0f;

    return current;
}

// 硬件改进：
// 1. ACS712 输出端并联 0.1μF 电容（滤除高频噪声）
// 2. 使用差分放大器（如 INA240）替代 ACS712
// 3. 增加 RC 低通滤波器（R=10kΩ, C=1μF, fc=16Hz）
```

### OTA 升级问题

#### 问题6：OTA 升级失败

**症状**：
- 下载卡在某个百分比
- 提示 "MD5 校验失败"
- 升级后无法启动

**调试方法**：

```cpp
// OTA 详细日志
ESPhttpUpdate.onProgress([](int cur, int total) {
    static int last_percent = -1;
    int percent = (cur * 100) / total;
    if (percent != last_percent) {
        Serial.printf("[OTA] 进度: %d%% (%d/%d bytes)\n",
                      percent, cur, total);
        last_percent = percent;
    }
});

ESPhttpUpdate.onError([](int err) {
    Serial.printf("[OTA] 错误代码: %d\n", err);
    Serial.printf("[OTA] 错误信息: %s\n",
                  ESPhttpUpdate.getLastErrorString().c_str());
    // 错误代码：
    // -1 = HTTP_UPDATE_FAILED
    // -2 = HTTP_UPDATE_NO_UPDATES
    // -3 = HTTP_UPDATE_NO_PARTITION
});
```

**常见失败原因**：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| MD5 校验失败 | 固件损坏或传输错误 | 重新生成 MD5，检查网络 |
| 分区不足 | 固件大小 > OTA 分区 | 减小固件或使用 minimal SPIFFS |
| 下载超时 | 网络不稳定 | 增加超时时间或使用本地服务器 |
| 启动失败 | 固件与硬件不匹配 | 检查编译目标板型 |

```cpp
// 增加 OTA 超时时间
ESPhttpUpdate.setTimeout(60000);  // 60秒

// 使用本地 HTTP 服务器（Python）
// python -m http.server 8000
// OTA URL: http://192.168.1.100:8000/firmware.bin
```

### 电能质量监测问题

#### 问题7：THD 计算结果异常

**症状**：
- THD 显示 > 200%
- 谐波幅值大于基波

**可能原因**：

```
1. 采样率不足：
   - 10kHz 采样率无法捕捉高次谐波
   - 解决：降低分析的最高谐波次数（如仅到第7次）

2. 采样窗口不对齐：
   - 采样点数不是工频周期的整数倍
   - 解决：确保 N = 采样率 / 工频（如 10000/50 = 200）

3. ADC 噪声：
   - ESP8266 ADC 精度有限（10-bit）
   - 解决：使用外部 ADC（如 ADS1115，16-bit）

4. 算法错误：
   - Goertzel 算法参数错误
   - 解决：使用经过验证的 FFT 库（如 arduinoFFT）
```

**验证方法**：

```cpp
// 使用纯正弦波测试（如白炽灯）
// 预期结果：THD < 5%，仅基波有明显幅值

void test_thd_with_resistive_load() {
    Serial.println("[TEST] 请接入纯电阻负载（白炽灯）");
    delay(5000);

    // 采集数据
    int16_t samples[N_SAMPLES];
    for (int i = 0; i < N_SAMPLES; i++) {
        samples[i] = analogRead(A0);
        delayMicroseconds(100);  // 10kHz 采样
    }

    // 分析
    PowerQuality pq = analyze_power_quality(samples, N_SAMPLES);

    Serial.printf("[TEST] 基波: %.3f A\n", pq.fundamental_a);
    Serial.printf("[TEST] THD: %.1f%%\n", pq.thd_percent);
    Serial.println("[TEST] 各次谐波:");
    for (int h = 2; h <= 8; h++) {
        Serial.printf("  %d次: %.3f A\n", h, pq.harmonics[h-2]);
    }

    // 预期：白炽灯 THD < 5%，2-8次谐波 < 0.01A
}
```


## 测试与验证

### 单元测试

```cpp
// 单元测试框架（使用 AUnit 库）
#include <AUnit.h>

test(HLW8012_PowerCalculation) {
    // 模拟 CF 脉冲频率
    float cf_hz = 3400.0f;  // 对应 1W（假设 k_power=3400）
    float power = cf_hz / 3400.0f;
    assertEqual(power, 1.0f);
}

test(OverloadProtection) {
    meas_current_a = 15.0f;  // 超过阈值
    cfg.overload_a = 10.0f;
    check_overload();
    delay(2100);  // 等待2秒保护动作
    check_overload();
    assertFalse(relay_state);  // 继电器应断开
}

test(TimerTask) {
    timers[0].hour = 10;
    timers[0].minute = 30;
    timers[0].action = true;
    timers[0].enabled = true;
    timers[0].weekdays = 0x7F;  // 每天

    // 模拟时间到达
    // （需要 mock NTPClient）
    check_timers();
    assertTrue(relay_state);
}

void setup() {
    Serial.begin(115200);
    while (!Serial);
}

void loop() {
    aunit::TestRunner::run();
}
```

### 集成测试

```python
# MQTT 集成测试脚本（Python）
# 依赖：pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import time

BROKER = "192.168.1.100"
DEVICE_ID = "node001"

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] 已连接，返回码: {rc}")
    client.subscribe(f"socket/{DEVICE_ID}/status")

def on_message(client, userdata, msg):
    print(f"[MQTT] 收到消息: {msg.topic}")
    payload = json.loads(msg.payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()

# 测试用例
def test_relay_control():
    print("\n[TEST] 测试继电器控制")
    client.publish(f"socket/{DEVICE_ID}/control", json.dumps({"cmd": "on"}))
    time.sleep(2)
    client.publish(f"socket/{DEVICE_ID}/control", json.dumps({"cmd": "off"}))
    time.sleep(2)
    print("[TEST] 继电器控制测试完成")

def test_timer():
    print("\n[TEST] 测试定时任务")
    timer = {
        "cmd": "set_timer",
        "id": 0,
        "hour": 14,
        "minute": 30,
        "action": True,
        "weekdays": 0x7F
    }
    client.publish(f"socket/{DEVICE_ID}/control", json.dumps(timer))
    print("[TEST] 定时任务已设置")

def test_ota():
    print("\n[TEST] 测试 OTA 升级")
    ota_cmd = {
        "url": "http://192.168.1.100:8000/firmware.bin",
        "md5": "abc123...",
        "version": "2.1.0"
    }
    client.publish(f"socket/{DEVICE_ID}/ota", json.dumps(ota_cmd))
    print("[TEST] OTA 命令已发送")

# 运行测试
try:
    test_relay_control()
    time.sleep(5)
    test_timer()
    time.sleep(5)
    # test_ota()  # 谨慎使用
    time.sleep(60)
except KeyboardInterrupt:
    print("\n[TEST] 测试中断")
finally:
    client.loop_stop()
    client.disconnect()
```


## 延伸阅读

### 内部链接

- [继电器控制基础](../beginner/04-relay-control.html) — 继电器工作原理与驱动电路
- [MQTT协议详解](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html) — MQTT QoS、遗嘱消息、TLS加密
- [数据可视化](../../../07-cloud-backend/03-data-analysis-visualization/beginner/03-data-visualization.html) — Grafana仪表盘设计
- [自动化控制系统](./08-automation-system.html) — Modbus RTU 工业控制
- [环境监控系统](./09-environment-control.html) — 多传感器融合与规则引擎

### 外部资源

**芯片数据手册**：
- [HLW8012 Datasheet](https://www.hlktech.net/index.php?id=181) — 能量计量芯片完整规格
- [BL0937 Datasheet](http://www.belling.com.cn/media/file_object/bel_product/BL0937/datasheet/BL0937_V1.02_cn.pdf) — 国产替代方案
- [ESP8266 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp8266-technical_reference_en.pdf) — ESP8266 完整技术手册

**标准文档**：
- [IEC 60884-1:2002](https://webstore.iec.ch/publication/3790) — 家用插头插座标准
- [IEC 61000-3-2:2018](https://webstore.iec.ch/publication/28164) — 谐波电流限值
- [GB 2099.1-2008](http://www.gb688.cn/bzgk/gb/newGbInfo?hcno=0F2F5A0E6F3F8F8F8F8F8F8F8F8F8F8F) — 中国插座标准

**开源项目**：
- [Tasmota](https://github.com/arendst/Tasmota) — 开源智能插座固件（支持 HLW8012）
- [ESPHome](https://esphome.io/) — 声明式 ESP 固件框架
- [Sonoff-Tasmota](https://tasmota.github.io/docs/devices/Sonoff-Pow/) — Sonoff Pow 智能插座固件

**技术文章**：
- [True RMS vs Average RMS](https://www.fluke.com/en-us/learn/blog/digital-multimeters/true-rms) — Fluke 官方解释
- [Power Factor Correction](https://www.ti.com/lit/an/slua479a/slua479a.pdf) — TI 功率因数校正应用笔记
- [ESP8266 OTA Updates](https://arduino-esp8266.readthedocs.io/en/latest/ota_updates/readme.html) — 官方 OTA 文档


## 参考资料

1. **IEC 60884-1:2002** — Plugs and socket-outlets for household and similar purposes
2. **UL 498** — Standard for Safety Attachment Plugs and Receptacles
3. **GB 2099.1-2008** — 家用和类似用途插头插座 第1部分：通用要求
4. **IEC 61000-3-2:2018** — Electromagnetic compatibility (EMC) – Part 3-2: Limits for harmonic current emissions
5. **HLW8012 Datasheet** — Single Phase Energy Metering IC, Hilink Electronics
6. **ESP8266 Technical Reference** — Espressif Systems, v1.7, 2020
7. **IEEE Std 1459-2010** — IEEE Standard Definitions for the Measurement of Electric Power Quantities Under Sinusoidal, Nonsinusoidal, Balanced, or Unbalanced Conditions
8. **MQTT Version 5.0** — OASIS Standard, 2019
9. **Arduino ESP8266 Core Documentation** — https://arduino-esp8266.readthedocs.io/
10. **Tasmota Documentation** — https://tasmota.github.io/docs/

---

**版本历史**：
- v2.0 (2026-03-10)：完整重写，新增 HLW8012 能量计量、OTA 升级、零点检测调光、电能质量监测、完整项目实战和故障排查
- v1.0 (2025-12-15)：初始版本，基础 WiFi 继电器控制

**作者**：嵌入式知识平台  
**许可**：CC BY-NC-SA 4.0
