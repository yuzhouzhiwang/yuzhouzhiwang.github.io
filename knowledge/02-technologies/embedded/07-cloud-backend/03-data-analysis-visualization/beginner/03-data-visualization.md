---
title: "数据可视化入门：Grafana看板搭建实践"
description: "从零开始搭建IoT数据可视化看板，涵盖Grafana安装配置、连接InfluxDB/MQTT数据源、设计传感器监控面板、配置告警规则，实现嵌入式设备数据的实时可视化"
slug: "data-visualization-grafana-dashboard"

domain: "云端与后台"
module: "数据分析与可视化"
content_type: "tutorial"
skill_level: "beginner"

tags:
  - 数据可视化
  - Grafana
  - InfluxDB
  - 物联网监控
  - 看板设计
prerequisites:
  - "beginner/01-time-series-db"
related_contents:
  - "beginner/02-data-analysis-tools"

estimated_time: 60
difficulty_score: 2

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "1.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - Grafana教程
  - 数据可视化
  - IoT看板
  - InfluxDB可视化
  - 传感器监控
cover_image: ""
---
{% raw %}

# 数据可视化入门：Grafana看板搭建实践

## 概述

Grafana 是目前最流行的开源数据可视化平台，广泛用于 IoT 传感器数据监控、服务器性能监控和业务指标展示。它支持 InfluxDB、Prometheus、MySQL 等数十种数据源，通过拖拽即可构建专业的实时监控看板。

完成本文学习后，你将能够：

- 在本地或服务器上安装并配置 Grafana
- 连接 InfluxDB 时序数据库作为数据源
- 创建温湿度、气压等传感器数据的实时监控面板
- 配置告警规则，在数据异常时发送通知
- 将看板嵌入到 Web 页面或分享给团队

## 背景知识

### 典型 IoT 数据可视化架构

```
传感器设备
    │ MQTT上报
    ▼
MQTT Broker（Mosquitto/EMQX）
    │ 订阅消息
    ▼
数据写入服务（Telegraf / 自定义脚本）
    │ 写入
    ▼
时序数据库（InfluxDB）
    │ 查询
    ▼
Grafana 看板
    │ 展示
    ▼
浏览器 / 大屏
```

**各组件职责**：
- **Telegraf**：InfluxDB 官方数据采集代理，支持直接订阅 MQTT 并写入 InfluxDB，无需编写代码
- **InfluxDB**：专为时序数据优化的数据库，高效存储和查询带时间戳的传感器数据
- **Grafana**：纯展示层，从数据库查询数据并渲染图表

### 时序数据核心概念

理解时序数据（Time-Series Data）的特性是构建高效监控系统的基础。

#### 基数（Cardinality）

**基数**是指数据库中唯一时间序列（Series）的数量。在 InfluxDB 中，一条时间序列由 measurement + 所有 tag 的组合唯一确定。

```
measurement: environment
tags: device_id=node_001, location=room_a
→ 这是一条独立的时间序列

measurement: environment
tags: device_id=node_002, location=room_b
→ 这是另一条独立的时间序列
```

**高基数问题（High Cardinality）**：

```
┌─────────────────────────────────────────────────────────┐
│                    基数爆炸示例                           │
├─────────────────────────────────────────────────────────┤
│ 错误做法：将用户ID作为tag                                  │
│   tags: user_id=10001, user_id=10002, ...               │
│   → 100万用户 = 100万条时间序列 → 内存耗尽                 │
├─────────────────────────────────────────────────────────┤
│ 正确做法：将高基数字段作为field而非tag                      │
│   tags: device_type=sensor                              │
│   fields: user_id="10001", value=25.3                   │
│   → 基数保持可控                                          │
└─────────────────────────────────────────────────────────┘
```

**基数控制原则**：
- Tag 应使用低基数字段（设备类型、地区、状态等枚举值）
- 高基数标识符（用户ID、订单号、UUID）应放入 field
- 单个 bucket 的时间序列数量建议控制在 100 万以内

#### 数据保留策略（Retention Policy）

时序数据随时间增长会占用大量存储空间。**保留策略（Retention Policy，RP）**定义数据的存活时间，过期数据自动删除。

**InfluxDB 2.x 保留策略配置**：

```bash
# 创建 bucket 时设置保留时间（30天）
influx bucket create \
  --name sensor-data \
  --org iot-org \
  --retention 720h   # 720小时 = 30天

# 修改现有 bucket 的保留时间
influx bucket update \
  --name sensor-data \
  --retention 2160h  # 90天
```

**多级保留策略设计**（生产环境推荐）：

```
原始数据 bucket（raw-data）：保留 7 天，每秒一条
    │ Flux Task 每小时聚合
    ▼
小时聚合 bucket（hourly-data）：保留 90 天，每小时一条
    │ Flux Task 每天聚合
    ▼
日聚合 bucket（daily-data）：保留 3 年，每天一条
```

这种分层存储策略在保留历史趋势的同时大幅降低存储成本。

#### 降采样（Downsampling）

**降采样**是将高频原始数据聚合为低频摘要数据的过程，是解决存储增长和查询性能问题的核心手段。

```
原始数据（每5秒）：25.1, 25.3, 25.0, 24.9, 25.2, 25.4, ...
                              ↓ 降采样（每分钟取均值）
分钟数据：25.15, 25.17, ...
                              ↓ 降采样（每小时取均值/最大/最小）
小时数据：{mean: 25.2, max: 26.1, min: 24.3}
```

**降采样的收益**：

| 时间跨度 | 原始数据点数 | 降采样后（1分钟） | 存储节省 |
|---------|------------|----------------|---------|
| 1天     | 17,280     | 1,440          | 91.7%   |
| 1周     | 120,960    | 10,080         | 91.7%   |
| 1年     | 6,307,200  | 525,600        | 91.7%   |

### Grafana 架构详解

Grafana 采用前后端分离架构，理解其内部结构有助于进行高级配置和二次开发。

```
┌─────────────────────────────────────────────────────────┐
│                    Grafana 架构                           │
├─────────────────────────────────────────────────────────┤
│  浏览器（Frontend）                                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  React 应用                                       │   │
│  │  ├── Dashboard 渲染引擎                            │   │
│  │  ├── Panel 插件系统（图表库：Echarts/D3.js）        │   │
│  │  ├── 变量插值引擎                                   │   │
│  │  └── 告警状态展示                                   │   │
│  └──────────────────────────────────────────────────┘   │
│                         │ HTTP/WebSocket                 │
├─────────────────────────────────────────────────────────┤
│  Grafana Server（Backend - Go语言）                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  HTTP API 层                                      │   │
│  │  ├── Dashboard CRUD API                           │   │
│  │  ├── 数据源代理（避免跨域，保护凭证）                 │   │
│  │  ├── 告警引擎（Alertmanager 兼容）                  │   │
│  │  └── 用户/权限管理                                  │   │
│  │                                                   │   │
│  │  插件系统                                          │   │
│  │  ├── 数据源插件（InfluxDB/Prometheus/MySQL/...）    │   │
│  │  ├── Panel 插件（图表类型）                         │   │
│  │  └── App 插件（完整应用）                           │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                               │
├─────────────────────────────────────────────────────────┤
│  内置 SQLite / 外部 MySQL / PostgreSQL                    │
│  （存储 Dashboard 配置、用户、告警规则等元数据）             │
└─────────────────────────────────────────────────────────┘
```

**关键设计特点**：

1. **数据源代理**：前端查询不直接访问数据库，而是通过 Grafana 后端代理，保护数据库凭证不暴露给浏览器
2. **插件化架构**：所有图表类型和数据源都是插件，可热加载，无需重启
3. **元数据存储**：Dashboard JSON、用户配置、告警规则存储在关系型数据库中（默认 SQLite，生产环境推荐 PostgreSQL）
4. **无状态设计**：Grafana 本身不存储时序数据，只存储配置元数据，便于水平扩展

**Grafana 目录结构**（Linux 安装）：

```bash
/etc/grafana/
├── grafana.ini          # 主配置文件
└── provisioning/        # 预配置目录（GitOps）
    ├── datasources/     # 数据源配置 YAML
    ├── dashboards/      # Dashboard 配置 YAML
    └── alerting/        # 告警规则配置 YAML

/var/lib/grafana/
├── grafana.db           # SQLite 元数据库
└── plugins/             # 已安装插件目录

/var/log/grafana/
└── grafana.log          # 日志文件
```

## 核心内容

### 安装 Grafana

**Docker 安装（推荐，最简单）**：

```bash
# 拉取并启动 Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana-oss:latest

# 访问：http://localhost:3000
# 默认账号：admin / admin（首次登录会要求修改密码）
```

**配合 InfluxDB 的完整 docker-compose**：

```yaml
# docker-compose.yml
version: '3'
services:
  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    volumes:
      - influxdb-data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password123
      - DOCKER_INFLUXDB_INIT_ORG=iot-org
      - DOCKER_INFLUXDB_INIT_BUCKET=sensor-data
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-token

  grafana:
    image: grafana/grafana-oss:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - influxdb

volumes:
  influxdb-data:
  grafana-data:
```

```bash
docker-compose up -d
```

**Linux 直接安装**：

```bash
# Ubuntu/Debian
sudo apt install -y apt-transport-https software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update && sudo apt install grafana
sudo systemctl enable --now grafana-server
```

### 配置 InfluxDB 数据源

1. 登录 Grafana（`http://localhost:3000`）
2. 左侧菜单 → **Connections** → **Data sources** → **Add data source**
3. 选择 **InfluxDB**
4. 配置参数：

```
Query Language: Flux（InfluxDB 2.x 推荐）
URL: http://influxdb:8086
Organization: iot-org
Token: my-super-secret-token
Default Bucket: sensor-data
```

5. 点击 **Save & test**，显示绿色 "Data source is working" 即成功

### 写入测试数据

用 Python 脚本模拟传感器数据写入 InfluxDB：

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time

INFLUXDB_URL   = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-token"
INFLUXDB_ORG   = "iot-org"
INFLUXDB_BUCKET = "sensor-data"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

print("Writing sensor data to InfluxDB...")
while True:
    point = (
        Point("environment")           # measurement名称
        .tag("device_id", "node_001")  # 标签（用于过滤和分组）
        .tag("location", "room_a")
        .field("temperature", round(20.0 + random.uniform(-2, 5), 1))
        .field("humidity",    round(55.0 + random.uniform(-10, 10), 1))
        .field("pressure",    round(1013.0 + random.uniform(-5, 5), 1))
    )
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    print(f"Written: {point.to_line_protocol()}")
    time.sleep(5)
```

```bash
pip install influxdb-client
python write_sensor_data.py
```

### 创建监控看板

#### 新建 Dashboard

1. 左侧菜单 → **Dashboards** → **New** → **New dashboard**
2. 点击 **Add visualization**

#### 添加温度折线图

在 Panel 编辑器中：

**Query（Flux 语法）**：

```flux
from(bucket: "sensor-data")
  |> range(start: -1h)                          // 查询最近1小时
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
  |> filter(fn: (r) => r.device_id == "node_001")
  |> aggregateWindow(every: 1m, fn: mean)       // 每分钟取平均值
  |> yield(name: "temperature")
```

**Panel 配置**：
- Visualization：**Time series**（折线图）
- Title：`室内温度`
- Unit：`Celsius (°C)`（在 Standard options → Unit 中设置）
- Min/Max：0 / 50
- Thresholds：添加阈值线，如 28°C 显示橙色警告，35°C 显示红色

#### 添加湿度仪表盘（Gauge）

```flux
from(bucket: "sensor-data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "humidity")
  |> last()
```

- Visualization：**Gauge**
- Unit：`Humidity (%H)`
- Min：0，Max：100
- Thresholds：60（绿）→ 80（黄）→ 90（红）

#### 添加多设备对比图

```flux
from(bucket: "sensor-data")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 5m, fn: mean)
  |> group(columns: ["device_id"])   // 按设备分组，每个设备一条线
```

- Visualization：**Time series**
- Legend：显示 `device_id` 标签

#### 添加统计卡片（Stat）

显示当前温度的最新值：

```flux
from(bucket: "sensor-data")
  |> range(start: -1m)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
```

- Visualization：**Stat**
- Color mode：**Background**（根据阈值变色背景）

### 配置告警规则

Grafana 支持在数据超出阈值时发送告警通知。

**创建告警规则**：

1. 在 Panel 编辑器 → **Alert** 标签页
2. 点击 **Create alert rule from this panel**
3. 配置条件：

```
条件：temperature 的 last() 值 > 30
评估间隔：每 1 分钟检查一次
持续时间：超过 5 分钟才触发（避免瞬间抖动误报）
```

**配置通知渠道**（以钉钉 Webhook 为例）：

1. 左侧菜单 → **Alerting** → **Contact points** → **Add contact point**
2. 类型选择 **DingDing**，填入 Webhook URL
3. 在告警规则中关联此通知渠道

**常用通知渠道**：Email、钉钉、企业微信、Slack、PagerDuty、Telegram

### 使用 Telegraf 自动采集 MQTT 数据

Telegraf 可以直接订阅 MQTT 并写入 InfluxDB，无需编写代码：

```toml
# telegraf.conf

# 输出到 InfluxDB 2.x
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "my-super-secret-token"
  organization = "iot-org"
  bucket = "sensor-data"

# 从 MQTT 订阅数据
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  topics  = ["iot/sensor/+/data"]
  qos     = 0
  data_format = "json"

  # JSON 字段映射
  json_string_fields = ["device_id", "location"]
  tag_keys = ["device_id", "location"]
```

```bash
# 启动 Telegraf
docker run -d \
  --name telegraf \
  -v $(pwd)/telegraf.conf:/etc/telegraf/telegraf.conf \
  telegraf:latest
```

### Prometheus 数据源与 PromQL

Prometheus 是云原生监控的事实标准，与 Grafana 深度集成。在嵌入式/IoT 场景中，Prometheus 常用于监控边缘网关、容器化服务的运行状态。

#### 添加 Prometheus 数据源

```bash
# 启动 Prometheus（docker-compose 片段）
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

```yaml
# prometheus.yml - 抓取配置
global:
  scrape_interval: 15s      # 默认抓取间隔

scrape_configs:
  - job_name: 'iot-gateway'
    static_configs:
      - targets: ['gateway:8080']   # 被监控服务的 /metrics 端点

  - job_name: 'node-exporter'       # 主机系统指标
    static_configs:
      - targets: ['node-exporter:9100']
```

在 Grafana 中添加 Prometheus 数据源：
- URL：`http://prometheus:9090`
- 无需认证（内网环境）

#### PromQL 基础语法

PromQL（Prometheus Query Language）是即时查询语言，与 Flux 的流式处理风格不同，PromQL 更接近函数式表达式。

**即时向量查询（Instant Vector）**：

```promql
# 查询当前所有设备的温度值
iot_temperature_celsius

# 按标签过滤
iot_temperature_celsius{device_id="node_001", location="room_a"}

# 正则匹配
iot_temperature_celsius{location=~"room_.*"}
```

**范围向量查询（Range Vector）**：

```promql
# 过去5分钟的温度样本
iot_temperature_celsius[5m]

# 计算5分钟内的平均值
avg_over_time(iot_temperature_celsius[5m])

# 计算每秒变化率（适用于计数器类型指标）
rate(http_requests_total[5m])
```

**聚合操作**：

```promql
# 按 location 分组求平均温度
avg by (location) (iot_temperature_celsius)

# 所有设备中的最高温度
max(iot_temperature_celsius)

# 统计在线设备数量（up 指标为1表示在线）
count(up{job="iot-gateway"} == 1)
```

**常用函数**：

```promql
# 预测4小时后的磁盘使用量（线性预测）
predict_linear(node_filesystem_free_bytes[1h], 4 * 3600)

# 计算百分位数（P95响应时间）
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 变化量（适用于温度突变检测）
delta(iot_temperature_celsius[10m])
```

**InfluxDB vs Prometheus 对比**：

| 特性 | InfluxDB 2.x (Flux) | Prometheus (PromQL) |
|------|---------------------|---------------------|
| 数据模型 | measurement + tags + fields | metric_name + labels |
| 采集方式 | Push（主动推送） | Pull（主动拉取） |
| 查询语言 | Flux（管道式） | PromQL（函数式） |
| 适用场景 | IoT传感器、高写入量 | 微服务监控、云原生 |
| 长期存储 | 内置（含降采样） | 需外部方案（Thanos/Cortex） |
| 告警 | 内置 | 需 Alertmanager |

### Grafana 统一告警（Alerting v2）

Grafana 9.x 引入了统一告警系统（Unified Alerting），取代了旧版的 Panel-level 告警，提供更强大的告警管理能力。

#### 告警架构

```
┌─────────────────────────────────────────────────────────┐
│                  Grafana 统一告警架构                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  告警规则（Alert Rules）                                  │
│  ├── 评估组（Evaluation Group）：共享评估间隔              │
│  └── 告警规则：查询 + 条件 + 标签                          │
│                    │ 触发                               │
│                    ▼                                    │
│  告警实例（Alert Instances）                              │
│  ├── Pending（等待持续时间）                              │
│  ├── Firing（已触发）                                    │
│  └── Resolved（已恢复）                                  │
│                    │                                    │
│  通知策略（Notification Policies）                        │
│  ├── 路由规则（基于标签匹配）                              │
│  └── 分组、静默、抑制                                     │
│                    │                                    │
│  联系点（Contact Points）                                 │
│  ├── Email                                              │
│  ├── DingDing / 企业微信 / Slack                         │
│  └── Webhook（自定义）                                   │
└─────────────────────────────────────────────────────────┘
```

#### 创建告警规则

**通过 UI 创建**：

1. 左侧菜单 → **Alerting** → **Alert rules** → **New alert rule**
2. 配置查询（支持多数据源混合查询）：

```flux
# 查询A：获取温度数据
from(bucket: "sensor-data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature")
  |> mean()
```

3. 配置条件表达式：

```
条件：WHEN last() OF query(A) IS ABOVE 30
```

4. 设置评估行为：
   - **Evaluate every**：`1m`（每分钟评估一次）
   - **For**：`5m`（持续5分钟才触发，避免抖动）

5. 添加标签（用于通知路由）：

```yaml
labels:
  severity: warning
  team: iot-ops
  location: room_a
```

#### 通知策略配置

```yaml
# 通知策略树（Notification Policy Tree）
# 根策略：所有告警默认发送到 ops-team
route:
  receiver: ops-team
  group_by: [alertname, location]
  group_wait: 30s        # 等待30秒收集同组告警
  group_interval: 5m     # 同组告警最少间隔5分钟
  repeat_interval: 4h    # 持续告警每4小时重复通知

  # 子路由：严重告警额外发送到 on-call
  routes:
    - matchers:
        - severity = critical
      receiver: on-call-pagerduty
      continue: true     # 继续匹配父路由
```

#### 配置 Webhook 联系点（企业微信机器人）

```json
// 企业微信机器人 Webhook 消息格式
{
  "msgtype": "markdown",
  "markdown": {
    "content": "## 🚨 IoT 告警通知\n**告警名称**：{{ .CommonLabels.alertname }}\n**严重程度**：{{ .CommonLabels.severity }}\n**位置**：{{ .CommonLabels.location }}\n**当前值**：{{ .CommonAnnotations.value }}\n**触发时间**：{{ .StartsAt }}"
  }
}
```

在 Grafana 中配置：
- Contact point type：**Webhook**
- URL：企业微信机器人 Webhook 地址
- HTTP Method：POST

#### 告警静默（Silences）

在维护窗口期间临时屏蔽告警：

```
Alerting → Silences → Add silence
匹配条件：location="room_a"
持续时间：2026-03-10 02:00 ~ 2026-03-10 04:00
注释：夜间维护窗口
```

### Dashboard 预配置（GitOps 方式）

将 Dashboard 配置纳入版本控制，实现基础设施即代码（Infrastructure as Code）。

#### 数据源预配置

```yaml
# /etc/grafana/provisioning/datasources/influxdb.yaml
apiVersion: 1

datasources:
  - name: InfluxDB-IoT
    type: influxdb
    access: proxy
    url: http://influxdb:8086
    jsonData:
      version: Flux
      organization: iot-org
      defaultBucket: sensor-data
      tlsSkipVerify: true
    secureJsonData:
      token: ${INFLUXDB_TOKEN}    # 从环境变量读取，不硬编码
    isDefault: true
    editable: false               # 禁止 UI 修改，保持配置一致性

  - name: Prometheus-IoT
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    jsonData:
      timeInterval: "15s"
    editable: false
```

#### Dashboard 预配置

```yaml
# /etc/grafana/provisioning/dashboards/iot-dashboards.yaml
apiVersion: 1

providers:
  - name: IoT Dashboards
    orgId: 1
    folder: IoT监控
    type: file
    disableDeletion: true         # 防止通过 UI 删除
    updateIntervalSeconds: 30     # 每30秒检查文件变更
    allowUiUpdates: false         # 禁止 UI 修改（只读）
    options:
      path: /etc/grafana/dashboards   # Dashboard JSON 文件目录
```

```json
// /etc/grafana/dashboards/environment-monitor.json
// （Dashboard JSON 导出格式，通过 UI 的 Share → Export 获取）
{
  "__inputs": [
    {
      "name": "DS_INFLUXDB",
      "label": "InfluxDB",
      "type": "datasource",
      "pluginId": "influxdb"
    }
  ],
  "title": "IoT 环境监控",
  "uid": "iot-env-monitor-v1",
  "version": 1,
  "panels": [
    {
      "type": "timeseries",
      "title": "温度趋势",
      "datasource": "${DS_INFLUXDB}",
      "targets": [
        {
          "query": "from(bucket: \"sensor-data\") |> range(start: v.timeRangeStart) |> filter(fn: (r) => r._field == \"temperature\")"
        }
      ]
    }
  ]
}
```

**GitOps 工作流**：

```
开发者修改 Dashboard JSON
    │ git commit & push
    ▼
CI/CD Pipeline
    │ 验证 JSON 格式
    ▼
部署到服务器
    │ 更新 /etc/grafana/dashboards/
    ▼
Grafana 自动热加载（无需重启）
```

### 看板美化技巧

**布局建议**：
```
┌─────────────────────────────────────────────────┐
│  当前温度 [Stat]  当前湿度 [Stat]  当前气压 [Stat] │  ← 顶部状态栏
├─────────────────────────────────────────────────┤
│                                                 │
│         温度趋势（24小时）[Time series]           │  ← 主图
│                                                 │
├──────────────────────┬──────────────────────────┤
│  湿度仪表 [Gauge]    │  各设备温度对比 [Bar chart]│  ← 底部详情
└──────────────────────┴──────────────────────────┘
```

**变量（Variables）**：让看板支持动态筛选设备：

1. Dashboard Settings → Variables → Add variable
2. 类型：**Query**，名称：`device_id`
3. Query：
```flux
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "sensor-data", tag: "device_id")
```
4. 在 Panel 的 Flux 查询中使用 `r.device_id == "${device_id}"`

**时间范围快捷键**：看板右上角可设置自动刷新间隔（如每 10 秒刷新），适合实时监控大屏。

## 深入原理

### InfluxDB 2.x Tasks：定时 Flux 脚本

InfluxDB Tasks 是内置的定时任务系统，可以定期执行 Flux 脚本，实现自动化降采样、数据转换和告警检查。

#### Task 基本结构

```flux
// Task 元数据（必须在脚本顶部）
option task = {
  name: "downsample-temperature-1h",
  every: 1h,          // 执行间隔
  offset: 5m,         // 延迟偏移（等待数据写入完成）
}

// 降采样逻辑：将原始数据聚合为1小时粒度
from(bucket: "sensor-data")
  |> range(start: -task.every)          // 只处理上一个周期的数据
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> aggregateWindow(
      every: 1h,
      fn: (tables=<-, column) => tables
        |> mean()                        // 计算均值
  )
  |> to(bucket: "sensor-data-hourly")   // 写入目标 bucket
```

#### 多统计量降采样

生产环境中，降采样不仅需要均值，还需要保留最大值、最小值和标准差：

```flux
option task = {
  name: "downsample-multi-stats",
  every: 1h,
  offset: 5m,
}

// 定义时间范围
timeRange = {start: -task.every, stop: now()}

// 计算均值
meanData = from(bucket: "sensor-data")
  |> range(start: timeRange.start, stop: timeRange.stop)
  |> filter(fn: (r) => r._measurement == "environment")
  |> aggregateWindow(every: 1h, fn: mean)
  |> map(fn: (r) => ({r with _field: r._field + "_mean"}))

// 计算最大值
maxData = from(bucket: "sensor-data")
  |> range(start: timeRange.start, stop: timeRange.stop)
  |> filter(fn: (r) => r._measurement == "environment")
  |> aggregateWindow(every: 1h, fn: max)
  |> map(fn: (r) => ({r with _field: r._field + "_max"}))

// 计算最小值
minData = from(bucket: "sensor-data")
  |> range(start: timeRange.start, stop: timeRange.stop)
  |> filter(fn: (r) => r._measurement == "environment")
  |> aggregateWindow(every: 1h, fn: min)
  |> map(fn: (r) => ({r with _field: r._field + "_min"}))

// 合并并写入
union(tables: [meanData, maxData, minData])
  |> to(bucket: "sensor-data-hourly")
```

#### 通过 CLI 管理 Tasks

```bash
# 创建 Task
influx task create --file downsample.flux --org iot-org

# 列出所有 Tasks
influx task list --org iot-org

# 查看 Task 运行历史
influx task run list --task-id <task-id>

# 手动触发 Task（调试用）
influx task run retry --task-id <task-id> --run-id <run-id>

# 查看 Task 日志
influx task log list --task-id <task-id>
```

#### 数据过期检测 Task

```flux
// 检测长时间未上报的设备（超过10分钟无数据）
option task = {
  name: "detect-offline-devices",
  every: 5m,
}

import "influxdata/influxdb/monitor"
import "slack"

// 查询每个设备最后一次上报时间
lastSeen = from(bucket: "sensor-data")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "environment")
  |> last()
  |> map(fn: (r) => ({
      device_id: r.device_id,
      last_seen: r._time,
      minutes_ago: float(v: int(v: now()) - int(v: r._time)) / 60000000000.0
  }))

// 过滤出超过10分钟未上报的设备
offlineDevices = lastSeen
  |> filter(fn: (r) => r.minutes_ago > 10.0)

// 写入告警 bucket
offlineDevices
  |> map(fn: (r) => ({
      _time: now(),
      _measurement: "device_alerts",
      _field: "offline_minutes",
      _value: r.minutes_ago,
      device_id: r.device_id
  }))
  |> to(bucket: "alerts")
```

### Grafana 插件开发基础

Grafana 插件系统允许开发自定义 Panel（图表类型）、数据源和 App。以下介绍 Panel 插件的基本结构。

#### 插件目录结构

```
my-panel-plugin/
├── src/
│   ├── module.ts          # 插件入口，注册 Panel
│   ├── panel.tsx          # React 组件，渲染图表
│   ├── types.ts           # 选项类型定义
│   └── editor.tsx         # 配置面板（可选项编辑器）
├── dist/                  # 构建输出
├── plugin.json            # 插件元数据
└── package.json
```

#### plugin.json 元数据

```json
{
  "type": "panel",
  "name": "IoT Gauge Panel",
  "id": "mycompany-iot-gauge-panel",
  "info": {
    "description": "Custom gauge for IoT sensor data",
    "author": { "name": "IoT Team" },
    "version": "1.0.0",
    "updated": "2026-03-10"
  },
  "dependencies": {
    "grafanaVersion": "9.0.0",
    "plugins": []
  }
}
```

#### 最简 Panel 插件实现

```typescript
// src/module.ts
import { PanelPlugin } from '@grafana/data';
import { SimplePanel } from './panel';
import { PanelOptions } from './types';

export const plugin = new PanelPlugin<PanelOptions>(SimplePanel)
  .setPanelOptions(builder => {
    builder
      .addNumberInput({
        path: 'warningThreshold',
        name: '警告阈值',
        defaultValue: 30,
      })
      .addColorPicker({
        path: 'warningColor',
        name: '警告颜色',
        defaultValue: 'orange',
      });
  });
```

```typescript
// src/panel.tsx
import React from 'react';
import { PanelProps } from '@grafana/data';
import { PanelOptions } from './types';

export const SimplePanel: React.FC<PanelProps<PanelOptions>> = ({
  data,
  width,
  height,
  options,
}) => {
  // 从 data.series 中提取最新值
  const lastValue = data.series[0]?.fields[1]?.values.get(
    data.series[0].length - 1
  ) ?? 0;

  const isWarning = lastValue > options.warningThreshold;

  return (
    <div style={{
      width,
      height,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '48px',
      color: isWarning ? options.warningColor : 'green',
    }}>
      {lastValue.toFixed(1)}°C
    </div>
  );
};
```

#### 本地开发与调试

```bash
# 安装 Grafana 插件开发工具
npm install -g @grafana/create-plugin

# 创建新插件
npx @grafana/create-plugin@latest

# 启动开发服务器（热重载）
npm run dev

# 将插件目录挂载到 Grafana
docker run -d \
  -p 3000:3000 \
  -v $(pwd)/dist:/var/lib/grafana/plugins/my-panel-plugin \
  -e GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=mycompany-iot-gauge-panel \
  grafana/grafana-oss:latest
```

### Flux 高级查询技巧

#### 联表查询（Join）

将两个不同 measurement 的数据关联分析：

```flux
// 计算温度与湿度的相关性
temperature = from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 5m, fn: mean)
  |> rename(columns: {_value: "temperature"})

humidity = from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._field == "humidity")
  |> aggregateWindow(every: 5m, fn: mean)
  |> rename(columns: {_value: "humidity"})

join(
  tables: {temp: temperature, hum: humidity},
  on: ["_time", "device_id"]
)
|> map(fn: (r) => ({
    _time: r._time,
    device_id: r.device_id,
    // 计算热指数（Heat Index 简化公式）
    heat_index: r.temperature + 0.33 * (r.humidity / 100.0 * 6.105 * math.exp(x: 17.27 * r.temperature / (237.7 + r.temperature))) - 4.0
}))
```

#### 异常检测

```flux
import "math"

// 使用3σ原则检测温度异常
data = from(bucket: "sensor-data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._field == "temperature")

// 计算均值和标准差
stats = data
  |> reduce(
      identity: {count: 0.0, sum: 0.0, sumSq: 0.0},
      fn: (r, accumulator) => ({
          count: accumulator.count + 1.0,
          sum: accumulator.sum + r._value,
          sumSq: accumulator.sumSq + r._value * r._value,
      })
  )
  |> map(fn: (r) => ({
      mean: r.sum / r.count,
      stddev: math.sqrt(x: r.sumSq / r.count - (r.sum / r.count) * (r.sum / r.count))
  }))

// 标记超出3σ范围的异常点
// （实际使用时需要将 stats 结果参数化传入）
data
  |> map(fn: (r) => ({r with
      is_anomaly: r._value > 25.0 + 3.0 * 2.0 or r._value < 25.0 - 3.0 * 2.0
  }))
  |> filter(fn: (r) => r.is_anomaly)
```

## 完整项目：生产级 IoT 监控栈

本项目构建一套完整的生产级 IoT 数据监控系统，包含数据采集、存储、可视化、告警和自动降采样全链路。

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    完整 IoT 监控栈架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IoT 设备层                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ ESP32    │  │ STM32    │  │ 树莓派   │                      │
│  │ 温湿度   │  │ 电机状态 │  │ 网关     │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │ MQTT (TLS)  │             │                             │
│       └─────────────┴─────────────┘                             │
│                         │                                       │
│  消息层                  ▼                                       │
│  ┌──────────────────────────────────────┐                       │
│  │  Mosquitto MQTT Broker               │                       │
│  │  端口：1883（明文）/ 8883（TLS）       │                       │
│  └──────────────────┬───────────────────┘                       │
│                     │ 订阅 iot/#                                 │
│  采集层             ▼                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  Telegraf 数据采集代理                │                       │
│  │  输入：MQTT Consumer                 │                       │
│  │  输出：InfluxDB v2                   │                       │
│  └──────────────────┬───────────────────┘                       │
│                     │ Line Protocol                             │
│  存储层             ▼                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  InfluxDB 2.7                        │                       │
│  │  ├── sensor-data（原始，7天）          │                       │
│  │  ├── sensor-hourly（小时聚合，90天）   │                       │
│  │  └── alerts（告警记录，30天）          │                       │
│  │  Tasks：自动降采样                    │                       │
│  └──────────────────┬───────────────────┘                       │
│                     │ Flux 查询                                  │
│  展示层             ▼                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  Grafana 10.x                        │                       │
│  │  ├── 实时监控看板                     │                       │
│  │  ├── 历史趋势分析                     │                       │
│  │  └── 统一告警 → 企业微信/钉钉         │                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### 项目文件结构

```
iot-monitoring/
├── docker-compose.yml          # 主编排文件
├── .env                        # 环境变量（不提交到 git）
├── mosquitto/
│   ├── config/
│   │   └── mosquitto.conf      # Broker 配置
│   └── data/                   # 持久化数据
├── telegraf/
│   └── telegraf.conf           # 采集配置
├── influxdb/
│   └── tasks/
│       └── downsample.flux     # 降采样 Task
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── influxdb.yaml
│   │   └── dashboards/
│   │       ├── dashboards.yaml
│   │       └── iot-monitor.json
│   └── grafana.ini
└── scripts/
    ├── init-influxdb.sh        # 初始化脚本
    └── test-mqtt.py            # 测试数据发送脚本
```

### docker-compose.yml（完整版）

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ─── MQTT Broker ───────────────────────────────────────────
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"    # WebSocket 端口（浏览器客户端用）
    volumes:
      - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto-data:/mosquitto/data
      - mosquitto-log:/mosquitto/log
    networks:
      - iot-net

  # ─── 数据采集代理 ────────────────────────────────────────────
  telegraf:
    image: telegraf:1.29
    container_name: telegraf
    restart: unless-stopped
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    environment:
      - INFLUXDB_TOKEN=${INFLUXDB_TOKEN}
    depends_on:
      - mosquitto
      - influxdb
    networks:
      - iot-net

  # ─── 时序数据库 ──────────────────────────────────────────────
  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: unless-stopped
    ports:
      - "8086:8086"
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USERNAME}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD}
      - DOCKER_INFLUXDB_INIT_ORG=${INFLUXDB_ORG}
      - DOCKER_INFLUXDB_INIT_BUCKET=sensor-data
      - DOCKER_INFLUXDB_INIT_RETENTION=168h    # 7天
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}
    networks:
      - iot-net

  # ─── 可视化平台 ──────────────────────────────────────────────
  grafana:
    image: grafana/grafana-oss:10.2.0
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/grafana.ini:/etc/grafana/grafana.ini:ro
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SMTP_ENABLED=true
      - GF_SMTP_HOST=${SMTP_HOST}
      - GF_SMTP_USER=${SMTP_USER}
      - GF_SMTP_PASSWORD=${SMTP_PASSWORD}
    depends_on:
      - influxdb
    networks:
      - iot-net

networks:
  iot-net:
    driver: bridge

volumes:
  mosquitto-data:
  mosquitto-log:
  influxdb-data:
  influxdb-config:
  grafana-data:
```

### 环境变量文件

```bash
# .env（不提交到 git，加入 .gitignore）
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=StrongPassword123!
INFLUXDB_ORG=iot-org
INFLUXDB_TOKEN=my-super-secret-influxdb-token-change-this

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=GrafanaAdmin123!

SMTP_HOST=smtp.example.com:587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=smtp-password
```

### Mosquitto 配置

```conf
# mosquitto/config/mosquitto.conf
listener 1883
listener 9001
protocol websockets

# 允许匿名连接（生产环境应启用认证）
allow_anonymous true

# 持久化配置
persistence true
persistence_location /mosquitto/data/

# 日志
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type information

# 消息大小限制
message_size_limit 65536

# 连接保活
keepalive_interval 60
```

### Telegraf 完整配置

```toml
# telegraf/telegraf.conf

# ─── 全局配置 ────────────────────────────────────────────────
[global_tags]
  environment = "production"

[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = ""
  hostname = "telegraf-agent"
  omit_hostname = false

# ─── 输出：InfluxDB 2.x ──────────────────────────────────────
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${INFLUXDB_TOKEN}"
  organization = "iot-org"
  bucket = "sensor-data"
  timeout = "5s"
  # 写入失败时重试
  retry_buffer_limit = 10000

# ─── 输入：MQTT Consumer ─────────────────────────────────────
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  
  # 订阅主题列表
  topics = [
    "iot/sensor/+/environment",    # 环境传感器
    "iot/sensor/+/power",          # 电源监控
    "iot/device/+/status",         # 设备状态
  ]
  
  qos = 1
  connection_timeout = "30s"
  
  # 数据格式：JSON
  data_format = "json"
  json_time_key = "timestamp"
  json_time_format = "unix"
  
  # 从主题路径提取标签
  # 主题格式：iot/sensor/{device_id}/environment
  topic_tag = "topic"
  
  # 标签字段
  tag_keys = ["device_id", "location", "firmware_version"]

# ─── 输入：系统指标（监控 Telegraf 自身）────────────────────────
[[inputs.internal]]
  collect_memstats = false
```

### 初始化脚本

```bash
#!/bin/bash
# scripts/init-influxdb.sh
# 在 InfluxDB 启动后创建额外的 bucket 和 Task

set -e

INFLUX_URL="http://localhost:8086"
TOKEN="${INFLUXDB_TOKEN}"
ORG="iot-org"

echo "等待 InfluxDB 启动..."
until curl -sf "${INFLUX_URL}/health" > /dev/null; do
  sleep 2
done
echo "InfluxDB 已就绪"

# 创建小时聚合 bucket（保留90天）
echo "创建 sensor-hourly bucket..."
influx bucket create \
  --name sensor-hourly \
  --org "${ORG}" \
  --retention 2160h \
  --host "${INFLUX_URL}" \
  --token "${TOKEN}" 2>/dev/null || echo "bucket 已存在，跳过"

# 创建告警 bucket（保留30天）
echo "创建 alerts bucket..."
influx bucket create \
  --name alerts \
  --org "${ORG}" \
  --retention 720h \
  --host "${INFLUX_URL}" \
  --token "${TOKEN}" 2>/dev/null || echo "bucket 已存在，跳过"

# 创建降采样 Task
echo "创建降采样 Task..."
influx task create \
  --file /influxdb/tasks/downsample.flux \
  --org "${ORG}" \
  --host "${INFLUX_URL}" \
  --token "${TOKEN}" 2>/dev/null || echo "Task 已存在，跳过"

echo "初始化完成！"
```

### 测试数据发送脚本

```python
#!/usr/bin/env python3
# scripts/test-mqtt.py
# 模拟多个 IoT 设备发送传感器数据

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

# 模拟设备配置
DEVICES = [
    {"device_id": "node_001", "location": "room_a", "firmware_version": "v2.1.0"},
    {"device_id": "node_002", "location": "room_b", "firmware_version": "v2.1.0"},
    {"device_id": "node_003", "location": "outdoor", "firmware_version": "v2.0.5"},
    {"device_id": "node_004", "location": "server_room", "firmware_version": "v2.1.0"},
    {"device_id": "node_005", "location": "warehouse", "firmware_version": "v1.9.2"},
]

def generate_sensor_data(device: dict) -> dict:
    """生成模拟传感器数据"""
    base_temp = {
        "room_a": 22.0, "room_b": 23.5,
        "outdoor": 15.0, "server_room": 18.0, "warehouse": 20.0
    }.get(device["location"], 20.0)
    
    return {
        "device_id": device["device_id"],
        "location": device["location"],
        "firmware_version": device["firmware_version"],
        "timestamp": int(time.time()),
        "temperature": round(base_temp + random.gauss(0, 1.5), 2),
        "humidity": round(55.0 + random.gauss(0, 8), 2),
        "pressure": round(1013.25 + random.gauss(0, 3), 2),
        "battery_voltage": round(3.7 + random.uniform(-0.3, 0.1), 3),
        "rssi": random.randint(-90, -40),
    }

def main():
    client = mqtt.Client(client_id="test-publisher")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    
    print(f"开始向 {BROKER_HOST}:{BROKER_PORT} 发送测试数据...")
    print("按 Ctrl+C 停止\n")
    
    try:
        while True:
            for device in DEVICES:
                data = generate_sensor_data(device)
                topic = f"iot/sensor/{device['device_id']}/environment"
                payload = json.dumps(data)
                
                result = client.publish(topic, payload, qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"✓ {topic}: T={data['temperature']}°C H={data['humidity']}%")
                else:
                    print(f"✗ 发送失败: {topic}")
            
            print(f"--- 批次完成，等待10秒 ---")
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n停止发送")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
```

### 部署与验证步骤

```bash
# 1. 克隆项目并配置环境变量
cp .env.example .env
# 编辑 .env，修改所有密码

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务就绪（约30秒）
docker-compose ps

# 4. 初始化 InfluxDB（创建额外 bucket 和 Task）
bash scripts/init-influxdb.sh

# 5. 发送测试数据
pip install paho-mqtt
python scripts/test-mqtt.py &

# 6. 验证数据写入
curl -s "http://localhost:8086/api/v2/query" \
  -H "Authorization: Token ${INFLUXDB_TOKEN}" \
  -H "Content-Type: application/vnd.flux" \
  -d 'from(bucket:"sensor-data") |> range(start:-5m) |> count()'

# 7. 访问 Grafana
# http://localhost:3000
# 用户名/密码：见 .env 文件

# 8. 查看服务日志
docker-compose logs -f telegraf    # 检查数据采集
docker-compose logs -f influxdb    # 检查数据库
docker-compose logs -f grafana     # 检查可视化平台
```

### 告警规则配置（完整示例）

```yaml
# grafana/provisioning/alerting/rules.yaml
apiVersion: 1

groups:
  - orgId: 1
    name: IoT 传感器告警
    folder: IoT告警
    interval: 1m    # 评估间隔
    rules:
      # 高温告警
      - uid: temp-high-alert
        title: 温度过高告警
        condition: C
        data:
          - refId: A
            datasourceUid: influxdb-iot
            model:
              query: |
                from(bucket: "sensor-data")
                  |> range(start: -5m)
                  |> filter(fn: (r) => r._field == "temperature")
                  |> mean()
          - refId: C
            datasourceUid: "-100"
            model:
              type: classic_conditions
              conditions:
                - evaluator:
                    params: [30]
                    type: gt
                  operator:
                    type: and
                  query:
                    params: [A]
                  reducer:
                    type: last
        noDataState: NoData
        execErrState: Error
        for: 5m    # 持续5分钟才触发
        labels:
          severity: warning
          team: iot-ops
        annotations:
          summary: "设备 {{ $labels.device_id }} 温度过高"
          description: "当前温度 {{ $values.A }}°C，超过阈值 30°C"

      # 设备离线告警
      - uid: device-offline-alert
        title: 设备离线告警
        condition: C
        data:
          - refId: A
            datasourceUid: influxdb-iot
            model:
              query: |
                from(bucket: "sensor-data")
                  |> range(start: -15m)
                  |> filter(fn: (r) => r._measurement == "environment")
                  |> last()
                  |> count()
          - refId: C
            datasourceUid: "-100"
            model:
              type: classic_conditions
              conditions:
                - evaluator:
                    params: [5]    # 期望至少5个设备在线
                    type: lt
                  operator:
                    type: and
                  query:
                    params: [A]
                  reducer:
                    type: last
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "在线设备数量不足"
          description: "当前在线设备 {{ $values.A }} 台，低于预期 5 台"
```

## 性能调优

### InfluxDB 查询优化

```flux
// ❌ 低效查询：扫描全量数据后过滤
from(bucket: "sensor-data")
  |> range(start: -30d)
  |> filter(fn: (r) => r.device_id == "node_001")

// ✅ 高效查询：先缩小时间范围，再过滤标签
from(bucket: "sensor-data")
  |> range(start: -1h)                              // 先限制时间范围
  |> filter(fn: (r) => r._measurement == "environment")  // 再过滤 measurement
  |> filter(fn: (r) => r.device_id == "node_001")   // 最后过滤标签
  |> filter(fn: (r) => r._field == "temperature")   // 字段过滤放最后
```

**查询优化原则**：
1. 时间范围越小越好，避免 `range(start: -30d)` 这类大范围查询
2. `filter` 中优先过滤 measurement 和 tag（有索引），再过滤 field（无索引）
3. 对历史数据查询使用降采样后的 bucket（`sensor-hourly`）而非原始 bucket
4. 使用 `aggregateWindow` 而非 `window` + `mean()`，前者性能更好

### Grafana 看板性能优化

```
优化策略：
1. 合理设置刷新间隔
   - 实时监控：5-10秒
   - 历史分析：手动刷新或30分钟
   - 避免所有 Panel 同时刷新（使用 staggered refresh）

2. 使用模板变量减少查询数量
   - 用变量 $device_id 替代为每个设备创建独立 Panel
   - 一个 Panel + 变量 = N 个设备的数据

3. 启用查询缓存（Grafana Enterprise）
   - 相同查询在缓存有效期内直接返回缓存结果

4. 合理使用 aggregateWindow
   - 时间范围1小时：every: 1m
   - 时间范围24小时：every: 10m
   - 时间范围7天：every: 1h
```

## 常见问题与调试

## 常见问题与调试

### 数据源连接错误

#### 问题1：Grafana 无法连接 InfluxDB

**症状**：数据源测试显示 "connection refused" 或 "timeout"

**排查步骤**：

```bash
# 1. 检查 InfluxDB 容器是否运行
docker ps | grep influxdb

# 2. 检查端口是否监听
docker exec influxdb netstat -tlnp | grep 8086

# 3. 从 Grafana 容器内测试连通性
docker exec grafana curl -v http://influxdb:8086/health

# 4. 检查 Token 是否有效
curl -H "Authorization: Token ${INFLUXDB_TOKEN}" \
  http://localhost:8086/api/v2/buckets?org=iot-org
```

**常见原因与解决方案**：

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `connection refused` | InfluxDB 未启动或端口错误 | 检查容器状态，确认端口映射 |
| `unauthorized` | Token 无效或过期 | 重新生成 Token，更新 Grafana 配置 |
| `organization not found` | Org 名称拼写错误 | 检查 InfluxDB 中实际的 Org 名称 |
| `bucket not found` | Bucket 不存在 | 在 InfluxDB UI 中创建对应 Bucket |
| `i/o timeout` | 网络不通或防火墙 | 检查 Docker 网络配置，确认同一 network |

#### 问题2：Telegraf 无法连接 MQTT Broker

```bash
# 查看 Telegraf 日志
docker logs telegraf --tail 50

# 常见错误：
# E! [inputs.mqtt_consumer] Error connecting to broker: dial tcp: connection refused
# → Mosquitto 未启动，或 depends_on 未生效

# 手动测试 MQTT 连接
docker exec telegraf mosquitto_sub -h mosquitto -t "test/#" -v
```

**Telegraf 调试模式**：

```toml
# 在 telegraf.conf 中临时开启调试
[agent]
  debug = true
  quiet = false
```

### 高基数问题

**症状**：InfluxDB 内存持续增长，查询变慢，出现 OOM

**诊断**：

```bash
# 查看各 measurement 的 series 数量
influx query '
import "influxdata/influxdb/schema"
schema.measurementTagValues(bucket: "sensor-data", measurement: "environment", tag: "device_id")
  |> count()
' --org iot-org --token ${INFLUXDB_TOKEN}

# 查看总 series 数量
influx query '
import "influxdata/influxdb/schema"
schema.measurements(bucket: "sensor-data")
' --org iot-org --token ${INFLUXDB_TOKEN}
```

**解决方案**：

```flux
// 1. 找出高基数 tag，将其改为 field
// 错误：将 session_id 作为 tag（每次会话都不同）
// 修改前的写入代码（伪代码）：
// Point("requests").tag("session_id", uuid).field("latency", 100)

// 修改后：session_id 改为 field
// Point("requests").tag("endpoint", "/api/data").field("session_id", uuid).field("latency", 100)

// 2. 删除高基数 measurement（谨慎操作）
from(bucket: "sensor-data")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "bad-high-cardinality-measurement")
  |> drop()
  // 注意：实际删除需要使用 DELETE API，Flux 不能直接删除数据
```

```bash
# 使用 InfluxDB DELETE API 删除特定数据
curl -X POST "http://localhost:8086/api/v2/delete?org=iot-org&bucket=sensor-data" \
  -H "Authorization: Token ${INFLUXDB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2026-01-01T00:00:00Z",
    "stop": "2026-03-01T00:00:00Z",
    "predicate": "_measurement=\"bad-measurement\""
  }'
```

### 查询缓慢

**症状**：Grafana 面板加载超时，InfluxDB CPU 飙升

**诊断**：

```bash
# 查看 InfluxDB 慢查询日志
docker logs influxdb 2>&1 | grep "query duration"

# 在 InfluxDB UI 中使用 Data Explorer 分析查询性能
# 点击 "Script Editor" → 执行查询 → 查看执行时间
```

**优化策略**：

```flux
// 策略1：使用 pushdown 过滤（让过滤在存储层执行）
// ✅ 好：measurement 和 tag 过滤会被 pushdown
from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "environment" and r.device_id == "node_001")

// ❌ 差：自定义函数无法 pushdown
from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => strings.hasPrefix(v: r.device_id, prefix: "node_"))

// 策略2：对长时间范围查询使用聚合 bucket
// 查询7天数据时，使用小时聚合 bucket
from(bucket: "sensor-hourly")   // 而非 sensor-data
  |> range(start: -7d)
  |> filter(fn: (r) => r._field == "temperature_mean")

// 策略3：限制返回数据点数量
from(bucket: "sensor-data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 5m, fn: mean)   // 每5分钟一个点，而非每秒
  |> limit(n: 1000)                          // 最多返回1000个点
```

### 告警抖动（Alert Flapping）

**症状**：告警频繁在 Firing 和 Resolved 之间切换，产生大量噪音通知

**原因分析**：

```
时间线：
t=0:  温度 = 29.8°C  → 正常
t=1:  温度 = 30.2°C  → 触发告警 (Firing)
t=2:  温度 = 29.9°C  → 恢复 (Resolved)
t=3:  温度 = 30.1°C  → 再次触发 (Firing)
→ 每分钟发送通知，运维人员被淹没
```

**解决方案1：增加 `For` 持续时间**

```yaml
# 告警规则配置
for: 10m    # 连续10分钟超阈值才触发，而非立即触发
```

**解决方案2：添加滞回（Hysteresis）**

```flux
// 使用不同的触发和恢复阈值
// 触发条件：温度 > 30°C
// 恢复条件：温度 < 28°C（而非 < 30°C）
// 在 Grafana 中通过两个条件实现：
// Condition A: last(temperature) > 30  → Firing
// Condition B: last(temperature) < 28  → Resolved
```

**解决方案3：使用 Grafana 静默（Silences）**

```
在已知会产生抖动的时间段（如设备启动期间）：
Alerting → Silences → Add silence
Duration: 30 minutes
Matchers: device_id = node_001
```

**解决方案4：告警分组与抑制**

```yaml
# 通知策略：相同 location 的告警合并为一条通知
route:
  group_by: [location]
  group_wait: 2m       # 等待2分钟收集同组告警
  group_interval: 10m  # 同组告警最少间隔10分钟通知
  repeat_interval: 6h  # 持续告警每6小时重复一次
```

### Grafana 面板常见问题

#### 问题：面板显示 "No data"

```
排查顺序：
1. 检查时间范围：右上角时间选择器是否覆盖有数据的时间段
2. 检查数据源：Panel → Edit → 数据源是否正确选择
3. 执行查询：点击 "Run query" 查看原始返回数据
4. 检查 Flux 语法：在 InfluxDB Data Explorer 中单独测试查询
5. 检查 bucket 名称：大小写敏感，"Sensor-Data" ≠ "sensor-data"
```

#### 问题：时间序列图表时区错误

```bash
# Grafana 配置文件中设置时区
# /etc/grafana/grafana.ini
[date_formats]
default_timezone = Asia/Shanghai

# 或在 Dashboard Settings → Time zones 中设置
```

#### 问题：变量下拉列表为空

```flux
// 检查变量查询是否正确
// 正确的设备列表查询：
import "influxdata/influxdb/schema"
schema.tagValues(
  bucket: "sensor-data",
  tag: "device_id",
  start: -7d    // 必须指定时间范围
)
```

## 测试与验证

### 验证数据流完整性

```bash
# 1. 发送测试消息
mosquitto_pub -h localhost -p 1883 \
  -t "iot/sensor/test_device/environment" \
  -m '{"device_id":"test_device","location":"test","timestamp":'"$(date +%s)"',"temperature":25.5,"humidity":60.0}'

# 2. 验证 Telegraf 接收到消息（查看日志）
docker logs telegraf --tail 10

# 3. 验证数据写入 InfluxDB
curl -s "http://localhost:8086/api/v2/query?org=iot-org" \
  -H "Authorization: Token ${INFLUXDB_TOKEN}" \
  -H "Content-Type: application/vnd.flux" \
  -d 'from(bucket:"sensor-data") |> range(start:-1m) |> filter(fn:(r) => r.device_id == "test_device")'

# 4. 验证 Grafana 可以查询到数据
# 在 Grafana UI 中：Explore → 选择 InfluxDB 数据源 → 执行查询
```

### 自动化验证脚本

```python
#!/usr/bin/env python3
# scripts/verify-stack.py
"""验证整个监控栈的数据流完整性"""

import json
import time
import requests
import paho.mqtt.client as mqtt

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-influxdb-token-change-this"
INFLUXDB_ORG = "iot-org"
GRAFANA_URL = "http://localhost:3000"

def test_influxdb_health():
    """测试 InfluxDB 健康状态"""
    resp = requests.get(f"{INFLUXDB_URL}/health", timeout=5)
    assert resp.status_code == 200, f"InfluxDB 不健康: {resp.text}"
    print("✓ InfluxDB 健康检查通过")

def test_grafana_health():
    """测试 Grafana 健康状态"""
    resp = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
    assert resp.status_code == 200, f"Grafana 不健康: {resp.text}"
    print("✓ Grafana 健康检查通过")

def test_data_pipeline():
    """测试完整数据管道：MQTT → Telegraf → InfluxDB"""
    test_device_id = f"verify_test_{int(time.time())}"
    test_value = 99.9
    
    # 发送测试数据
    client = mqtt.Client()
    client.connect("localhost", 1883)
    payload = json.dumps({
        "device_id": test_device_id,
        "location": "test",
        "timestamp": int(time.time()),
        "temperature": test_value,
        "humidity": 50.0,
    })
    client.publish(f"iot/sensor/{test_device_id}/environment", payload, qos=1)
    client.disconnect()
    print(f"✓ 测试数据已发送 (device_id={test_device_id})")
    
    # 等待数据写入
    time.sleep(15)
    
    # 查询验证
    query = f'''
from(bucket: "sensor-data")
  |> range(start: -1m)
  |> filter(fn: (r) => r.device_id == "{test_device_id}")
  |> filter(fn: (r) => r._field == "temperature")
  |> last()
'''
    resp = requests.post(
        f"{INFLUXDB_URL}/api/v2/query?org={INFLUXDB_ORG}",
        headers={
            "Authorization": f"Token {INFLUXDB_TOKEN}",
            "Content-Type": "application/vnd.flux",
        },
        data=query,
        timeout=10,
    )
    assert resp.status_code == 200, f"查询失败: {resp.text}"
    assert str(test_value) in resp.text, f"未找到测试数据，响应: {resp.text}"
    print(f"✓ 数据管道验证通过 (temperature={test_value}°C 已写入 InfluxDB)")

if __name__ == "__main__":
    print("=== IoT 监控栈验证 ===\n")
    test_influxdb_health()
    test_grafana_health()
    test_data_pipeline()
    print("\n✅ 所有验证通过！")
```

## 延伸阅读

- [时序数据库入门](01-time-series-db.html) - InfluxDB 深入使用，包含 Flux 语言完整教程
- [数据分析工具](02-data-analysis-tools.html) - Python 数据分析与 Pandas 时序处理
- [MQTT协议详解](../../../06-communication-networking/01-wireless-communication/intermediate/03-mqtt-protocol.html) - MQTT 数据上报协议深入解析
- [IoT 云端集成](../../../06-communication-networking/03-iot-cloud-integration/index.html) - AWS IoT Core、阿里云 IoT 平台集成

## 参考资料

1. [Grafana 官方文档](https://grafana.com/docs/) - 完整的 Grafana 配置和使用指南
2. [InfluxDB Flux 查询语言参考](https://docs.influxdata.com/flux/) - Flux 函数完整参考
3. [Telegraf 插件文档](https://docs.influxdata.com/telegraf/v1/plugins/) - 所有输入/输出插件配置
4. [Prometheus 官方文档](https://prometheus.io/docs/) - PromQL 语法和最佳实践
5. [Grafana Alerting 文档](https://grafana.com/docs/grafana/latest/alerting/) - 统一告警系统配置
6. [InfluxDB 高基数最佳实践](https://docs.influxdata.com/influxdb/v2/write-data/best-practices/schema-design/) - Schema 设计指南
7. [Grafana Dashboard 最佳实践](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/) - 看板设计规范
8. [Eclipse Mosquitto 文档](https://mosquitto.org/documentation/) - MQTT Broker 配置参考
9. 《数据可视化》- 陈为 - 数据可视化理论基础
10. Edward Tufte - "The Visual Display of Quantitative Information" - 信息可视化经典著作
{% endraw %}
