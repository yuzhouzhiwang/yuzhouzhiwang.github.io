---
title: "云原生应用开发实战：构建可扩展的微服务系统"
description: "从零开始构建一个完整的云原生应用，涵盖微服务架构、容器化部署、服务编排、CI/CD流程和监控告警，掌握现代云原生开发的核心技术和最佳实践"
slug: "cloud-native-application-development"

# 分类信息
domain: "云端与后台"
module: "云服务"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - 云原生
  - 微服务
  - Docker
  - Kubernetes
  - DevOps
  - CI/CD
prerequisites:
  - "docker-basics-tutorial"
  - "kubernetes-container-orchestration"
  - "microservices-architecture"
related_contents:
  - "serverless-architecture-guide"
  - "iot-backend-system-development"

# 学习信息
estimated_time: 220
difficulty_score: 4

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
status: "published"
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - 云原生开发
  - 微服务架构
  - Kubernetes部署
  - Docker容器化
  - CI/CD流程
  - DevOps实践
cover_image: ""

# 项目特定信息
project_type: "software"
repository: ""
demo_video: ""
---
{% raw %}

# 云原生应用开发实战：构建可扩展的微服务系统


## 项目概述

### 项目简介

本项目将带你从零开始构建一个生产级的云原生应用系统，实现一个完整的IoT设备管理平台。该系统采用微服务架构，使用Docker容器化部署，通过Kubernetes进行服务编排，集成完整的CI/CD流程，并配备监控告警系统。

这是一个真实的云原生应用案例，涵盖了从开发、测试、部署到运维的完整生命周期，适合作为学习云原生技术和实践DevOps理念的综合项目。

### 项目演示

完成后的系统将提供以下功能：

```
云原生IoT平台架构
┌─────────────────────────────────────────────────────────────┐
│  前端层 (Frontend)                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React SPA + Nginx                                   │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  API网关层 (API Gateway)                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Kong / Nginx Ingress                                │  │
│  │  - 路由转发  - 认证授权  - 限流熔断                   │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  微服务层 (Microservices)                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 用户服务 │  │ 设备服务 │  │ 数据服务 │  │ 通知服务 │  │
│  │ (Node.js)│  │ (Python) │  │ (Go)     │  │ (Node.js)│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  数据层 (Data Layer)                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │  MongoDB │  │  Redis   │  │  Kafka   │  │
│  │ 关系数据 │  │ 文档数据 │  │  缓存    │  │ 消息队列 │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  基础设施层 (Infrastructure)                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Kubernetes Cluster                                  │  │
│  │  - 服务编排  - 自动扩展  - 健康检查  - 滚动更新      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 学习目标

完成本项目后，你将掌握：

- [ ] **微服务架构设计**：理解微服务的设计原则和拆分策略
- [ ] **容器化技术**：掌握Docker镜像构建和容器管理
- [ ] **服务编排**：使用Kubernetes部署和管理微服务
- [ ] **API网关**：实现统一的API入口和流量管理
- [ ] **服务通信**：掌握REST API和消息队列通信模式
- [ ] **CI/CD流程**：构建自动化的持续集成和部署流程
- [ ] **监控告警**：实现系统监控和日志管理
- [ ] **DevOps实践**：掌握现代化的开发运维一体化流程


## 项目特点

- ✨ **真实场景**：基于IoT设备管理的实际业务场景
- ✨ **微服务架构**：采用主流的微服务设计模式
- ✨ **多语言实现**：展示不同语言的微服务协作
- ✨ **容器化部署**：完全容器化，易于部署和扩展
- ✨ **自动化运维**：完整的CI/CD流程和监控体系
- ✨ **高可用设计**：支持水平扩展和故障自愈
- ✨ **生产级别**：包含安全、性能、可观测性等生产要素
- ✨ **最佳实践**：遵循云原生和12-Factor应用原则

## 技术栈

### 微服务技术
- **用户服务**：Node.js + Express + JWT
- **设备服务**：Python + FastAPI + SQLAlchemy
- **数据服务**：Go + Gin + GORM
- **通知服务**：Node.js + Express + WebSocket

### 容器和编排
- **容器化**：Docker 20.10+
- **编排工具**：Kubernetes 1.25+
- **包管理**：Helm 3.0+
- **服务网格**：Istio (可选)

### 数据存储
- **关系数据库**：PostgreSQL 14+
- **文档数据库**：MongoDB 6.0+
- **缓存**：Redis 7.0+
- **消息队列**：Apache Kafka 3.0+

### DevOps工具
- **CI/CD**：GitHub Actions / GitLab CI
- **镜像仓库**：Docker Hub / Harbor
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack (Elasticsearch + Logstash + Kibana)
- **追踪**：Jaeger

### 开发工具
- **IDE**：VS Code / IntelliJ IDEA
- **API测试**：Postman / Insomnia
- **K8s管理**：kubectl + k9s / Lens
- **版本控制**：Git + GitHub/GitLab

## 硬件清单

### 开发环境（最小配置）

| 组件 | 配置 | 说明 |
|------|------|------|
| CPU | 4核 | 支持虚拟化 |
| 内存 | 16GB | 运行K8s集群 |
| 硬盘 | 100GB SSD | 存储镜像和数据 |
| 操作系统 | Linux/macOS/Windows | 支持Docker |

**参考成本**：使用本地开发环境，无额外成本

### 生产环境（推荐配置）

| 组件 | 配置 | 说明 |
|------|------|------|
| K8s节点 | 3台 × 4核8GB | 高可用集群 |
| 存储 | 500GB SSD | 持久化存储 |
| 网络 | 100Mbps+ | 稳定网络 |
| 负载均衡 | 云服务商LB | 流量分发 |

**参考成本**：云服务器约 ¥1000-2000/月

### 云服务选项

可选择以下云服务商的托管Kubernetes服务：
- **阿里云**：ACK (Alibaba Cloud Container Service for Kubernetes)
- **腾讯云**：TKE (Tencent Kubernetes Engine)
- **AWS**：EKS (Elastic Kubernetes Service)
- **Azure**：AKS (Azure Kubernetes Service)
- **Google Cloud**：GKE (Google Kubernetes Engine)

## 软件要求

### 必需软件

```bash
# 容器和编排
Docker 20.10+
Kubernetes 1.25+ (Minikube/Kind/K3s用于本地开发)
kubectl 1.25+
Helm 3.0+

# 开发语言
Node.js 18+
Python 3.10+
Go 1.20+

# 版本控制
Git 2.30+
```

### 推荐工具

```bash
# K8s管理工具
k9s - 终端UI管理工具
Lens - 桌面管理工具

# 监控工具
Prometheus
Grafana

# 日志工具
Elasticsearch
Kibana

# API测试
Postman
HTTPie
```


## 系统架构

### 整体架构

```mermaid
graph TB
    subgraph "客户端层"
        WEB[Web应用]
        MOBILE[移动应用]
        IOT[IoT设备]
    end
    
    subgraph "接入层"
        INGRESS[Ingress Controller]
        LB[负载均衡]
    end
    
    subgraph "微服务层"
        USER[用户服务]
        DEVICE[设备服务]
        DATA[数据服务]
        NOTIFY[通知服务]
    end
    
    subgraph "数据层"
        PG[(PostgreSQL)]
        MONGO[(MongoDB)]
        REDIS[(Redis)]
        KAFKA[Kafka]
    end
    
    WEB --> LB
    MOBILE --> LB
    IOT --> LB
    LB --> INGRESS
    
    INGRESS --> USER
    INGRESS --> DEVICE
    INGRESS --> DATA
    INGRESS --> NOTIFY
    
    USER --> PG
    USER --> REDIS
    DEVICE --> MONGO
    DEVICE --> KAFKA
    DATA --> MONGO
    DATA --> REDIS
    NOTIFY --> KAFKA
    NOTIFY --> REDIS
```

### 核心模块说明

#### 1. 用户服务 (User Service)
- **功能**：用户注册、登录、认证、权限管理
- **技术栈**：Node.js + Express + JWT + PostgreSQL
- **端口**：3001
- **API端点**：
  - POST /api/users/register - 用户注册
  - POST /api/users/login - 用户登录
  - GET /api/users/profile - 获取用户信息
  - PUT /api/users/profile - 更新用户信息

#### 2. 设备服务 (Device Service)
- **功能**：设备注册、管理、状态监控
- **技术栈**：Python + FastAPI + MongoDB
- **端口**：3002
- **API端点**：
  - POST /api/devices - 注册设备
  - GET /api/devices - 获取设备列表
  - GET /api/devices/{id} - 获取设备详情
  - PUT /api/devices/{id} - 更新设备信息
  - DELETE /api/devices/{id} - 删除设备

#### 3. 数据服务 (Data Service)
- **功能**：设备数据采集、存储、查询
- **技术栈**：Go + Gin + MongoDB + Redis
- **端口**：3003
- **API端点**：
  - POST /api/data - 上报数据
  - GET /api/data/{deviceId} - 查询设备数据
  - GET /api/data/{deviceId}/latest - 获取最新数据
  - GET /api/data/{deviceId}/stats - 获取统计数据

#### 4. 通知服务 (Notification Service)
- **功能**：实时通知、告警推送、WebSocket连接
- **技术栈**：Node.js + Express + WebSocket + Kafka
- **端口**：3004
- **功能**：
  - WebSocket实时推送
  - 邮件通知
  - 短信通知（可选）
  - 告警规则引擎

### 服务间通信

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Gateway as API网关
    participant User as 用户服务
    participant Device as 设备服务
    participant Data as 数据服务
    participant Notify as 通知服务
    participant Kafka as Kafka
    
    Client->>Gateway: 1. 登录请求
    Gateway->>User: 2. 转发登录
    User-->>Gateway: 3. 返回Token
    Gateway-->>Client: 4. 返回Token
    
    Client->>Gateway: 5. 上报数据(带Token)
    Gateway->>Data: 6. 验证并转发
    Data->>Kafka: 7. 发布数据事件
    Data-->>Gateway: 8. 返回成功
    Gateway-->>Client: 9. 返回成功
    
    Kafka->>Notify: 10. 消费数据事件
    Notify->>Client: 11. WebSocket推送
```

### 数据模型

#### 用户表 (PostgreSQL)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 设备文档 (MongoDB)

```javascript
{
  _id: ObjectId,
  deviceId: String,
  name: String,
  type: String,
  userId: Number,
  status: String,  // online, offline, error
  config: {
    interval: Number,
    threshold: Object
  },
  location: {
    latitude: Number,
    longitude: Number
  },
  createdAt: Date,
  updatedAt: Date
}
```

#### 数据文档 (MongoDB)

```javascript
{
  _id: ObjectId,
  deviceId: String,
  timestamp: Date,
  data: {
    temperature: Number,
    humidity: Number,
    // 其他传感器数据
  },
  metadata: {
    quality: String,
    source: String
  }
}
```


## 实现步骤

### 阶段1：环境准备 (预计30分钟)

#### 1.1 安装Docker和Kubernetes

**安装Docker**：

```bash
# Linux (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
# 下载并安装 Docker Desktop for Mac

# Windows
# 下载并安装 Docker Desktop for Windows

# 验证安装
docker --version
docker run hello-world
```

**安装Kubernetes (本地开发)**：

```bash
# 选项1: Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start --driver=docker --cpus=4 --memory=8192

# 选项2: Kind (Kubernetes in Docker)
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind create cluster --name cloud-native-demo

# 选项3: K3s (轻量级K8s)
curl -sfL https://get.k3s.io | sh -

# 验证安装
kubectl version
kubectl get nodes
```

**安装Helm**：

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

#### 1.2 创建项目结构

```bash
# 创建项目根目录
mkdir cloud-native-iot-platform
cd cloud-native-iot-platform

# 创建服务目录
mkdir -p services/{user-service,device-service,data-service,notification-service}
mkdir -p k8s/{base,overlays/{dev,prod}}
mkdir -p monitoring
mkdir -p ci-cd

# 项目结构
tree -L 2
```

项目结构：
```
cloud-native-iot-platform/
├── services/
│   ├── user-service/          # Node.js用户服务
│   ├── device-service/        # Python设备服务
│   ├── data-service/          # Go数据服务
│   └── notification-service/  # Node.js通知服务
├── k8s/
│   ├── base/                  # 基础K8s配置
│   └── overlays/              # 环境特定配置
│       ├── dev/
│       └── prod/
├── monitoring/                # 监控配置
│   ├── prometheus/
│   └── grafana/
├── ci-cd/                     # CI/CD配置
│   ├── .github/
│   └── .gitlab-ci.yml
├── docker-compose.yml         # 本地开发环境
└── README.md
```

#### 1.3 配置本地开发环境

创建 `docker-compose.yml` 用于本地开发：

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: iot_platform
      POSTGRES_USER: iot_user
      POSTGRES_PASSWORD: iot_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # MongoDB
  mongodb:
    image: mongo:6.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin_password
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Kafka
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

volumes:
  postgres_data:
  mongodb_data:
  redis_data:

networks:
  default:
    name: iot-network
```

启动基础设施：

```bash
docker-compose up -d
docker-compose ps
```

### 阶段2：微服务开发 (预计4小时)

#### 2.1 用户服务 (Node.js)

创建 `services/user-service/package.json`：

```json
{
  "name": "user-service",
  "version": "1.0.0",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.0",
    "bcrypt": "^5.1.0",
    "jsonwebtoken": "^9.0.0",
    "dotenv": "^16.0.3",
    "cors": "^2.8.5"
  }
}
```

创建 `services/user-service/src/index.js`：

```javascript
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(require('cors')());

// 数据库连接
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'iot_platform',
  user: process.env.DB_USER || 'iot_user',
  password: process.env.DB_PASSWORD || 'iot_password'
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'user-service' });
});

// 用户注册
app.post('/api/users/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // 密码加密
    const passwordHash = await bcrypt.hash(password, 10);
    
    // 插入用户
    const result = await pool.query(
      'INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING id, username, email',
      [username, email, passwordHash]
    );
    
    res.status(201).json({
      message: 'User registered successfully',
      user: result.rows[0]
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

// 用户登录
app.post('/api/users/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // 查询用户
    const result = await pool.query(
      'SELECT * FROM users WHERE username = $1',
      [username]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const user = result.rows[0];
    
    // 验证密码
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // 生成JWT
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );
    
    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// 获取用户信息
app.get('/api/users/profile', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT id, username, email, role, created_at FROM users WHERE id = $1',
      [req.user.userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ error: 'Failed to get profile' });
  }
});

// JWT认证中间件
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
}

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`User service running on port ${PORT}`);
});
```

创建 `services/user-service/Dockerfile`：

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY src ./src

EXPOSE 3001

CMD ["node", "src/index.js"]
```

#### 2.2 设备服务 (Python)

创建 `services/device-service/requirements.txt`：

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pydantic==2.5.0
python-dotenv==1.0.0
```

创建 `services/device-service/main.py`：

```python
from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(title="Device Service")

# MongoDB连接
MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:admin_password@localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.iot_platform
devices_collection = db.devices

# 数据模型
class DeviceCreate(BaseModel):
    name: str
    type: str
    userId: int
    config: Optional[dict] = {}
    location: Optional[dict] = None

class Device(BaseModel):
    deviceId: str
    name: str
    type: str
    userId: int
    status: str = "offline"
    config: dict = {}
    location: Optional[dict] = None
    createdAt: datetime
    updatedAt: datetime

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "device-service"}

# 注册设备
@app.post("/api/devices", response_model=Device)
async def create_device(device: DeviceCreate):
    import uuid
    
    device_doc = {
        "deviceId": str(uuid.uuid4()),
        "name": device.name,
        "type": device.type,
        "userId": device.userId,
        "status": "offline",
        "config": device.config,
        "location": device.location,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await devices_collection.insert_one(device_doc)
    device_doc["_id"] = str(result.inserted_id)
    
    return device_doc

# 获取设备列表
@app.get("/api/devices", response_model=List[Device])
async def list_devices(userId: Optional[int] = None, status: Optional[str] = None):
    query = {}
    if userId:
        query["userId"] = userId
    if status:
        query["status"] = status
    
    cursor = devices_collection.find(query).limit(100)
    devices = await cursor.to_list(length=100)
    
    return devices

# 获取设备详情
@app.get("/api/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    device = await devices_collection.find_one({"deviceId": device_id})
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device

# 更新设备
@app.put("/api/devices/{device_id}", response_model=Device)
async def update_device(device_id: str, update_data: dict):
    update_data["updatedAt"] = datetime.utcnow()
    
    result = await devices_collection.find_one_and_update(
        {"deviceId": device_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return result

# 删除设备
@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    result = await devices_collection.delete_one({"deviceId": device_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {"message": "Device deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
```

创建 `services/device-service/Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 3002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3002"]
```

#### 2.3 数据服务 (Go)

创建 `services/data-service/go.mod`：

```go
module data-service

go 1.20

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/go-redis/redis/v8 v8.11.5
    go.mongodb.org/mongo-driver v1.12.1
)
```

创建 `services/data-service/main.go`：

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

var (
    mongoClient *mongo.Client
    redisClient *redis.Client
    ctx         = context.Background()
)

type DataPoint struct {
    DeviceID  string                 `json:"deviceId" bson:"deviceId"`
    Timestamp time.Time              `json:"timestamp" bson:"timestamp"`
    Data      map[string]interface{} `json:"data" bson:"data"`
    Metadata  map[string]interface{} `json:"metadata" bson:"metadata"`
}

func main() {
    // 连接MongoDB
    mongoURL := getEnv("MONGO_URL", "mongodb://admin:admin_password@localhost:27017")
    var err error
    mongoClient, err = mongo.Connect(ctx, options.Client().ApplyURI(mongoURL))
    if err != nil {
        log.Fatal("MongoDB connection failed:", err)
    }
    defer mongoClient.Disconnect(ctx)

    // 连接Redis
    redisClient = redis.NewClient(&redis.Options{
        Addr: getEnv("REDIS_URL", "localhost:6379"),
    })
    defer redisClient.Close()

    // 创建Gin路由
    r := gin.Default()

    // 健康检查
    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status":  "healthy",
            "service": "data-service",
        })
    })

    // 上报数据
    r.POST("/api/data", postData)

    // 查询设备数据
    r.GET("/api/data/:deviceId", getDeviceData)

    // 获取最新数据
    r.GET("/api/data/:deviceId/latest", getLatestData)

    // 启动服务
    port := getEnv("PORT", "3003")
    log.Printf("Data service running on port %s", port)
    r.Run(":" + port)
}

func postData(c *gin.Context) {
    var dataPoint DataPoint
    if err := c.ShouldBindJSON(&dataPoint); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    dataPoint.Timestamp = time.Now()

    // 存储到MongoDB
    collection := mongoClient.Database("iot_platform").Collection("data")
    _, err := collection.InsertOne(ctx, dataPoint)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to store data"})
        return
    }

    // 缓存最新数据到Redis
    cacheKey := "latest:" + dataPoint.DeviceID
    redisClient.Set(ctx, cacheKey, dataPoint.Data, 1*time.Hour)

    c.JSON(http.StatusCreated, gin.H{
        "message": "Data stored successfully",
        "data":    dataPoint,
    })
}

func getDeviceData(c *gin.Context) {
    deviceID := c.Param("deviceId")

    collection := mongoClient.Database("iot_platform").Collection("data")
    cursor, err := collection.Find(ctx, bson.M{"deviceId": deviceID})
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Query failed"})
        return
    }
    defer cursor.Close(ctx)

    var results []DataPoint
    if err = cursor.All(ctx, &results); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse results"})
        return
    }

    c.JSON(http.StatusOK, results)
}

func getLatestData(c *gin.Context) {
    deviceID := c.Param("deviceId")

    // 先从Redis缓存获取
    cacheKey := "latest:" + deviceID
    val, err := redisClient.Get(ctx, cacheKey).Result()
    if err == nil {
        c.JSON(http.StatusOK, gin.H{"data": val, "source": "cache"})
        return
    }

    // 缓存未命中，从MongoDB查询
    collection := mongoClient.Database("iot_platform").Collection("data")
    var result DataPoint
    err = collection.FindOne(
        ctx,
        bson.M{"deviceId": deviceID},
        options.FindOne().SetSort(bson.D{{"timestamp", -1}}),
    ).Decode(&result)

    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "No data found"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": result, "source": "database"})
}

func getEnv(key, defaultValue string) string {
    value := os.Getenv(key)
    if value == "" {
        return defaultValue
    }
    return value
}
```

创建 `services/data-service/Dockerfile`：

```dockerfile
FROM golang:1.20-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY main.go .
RUN go build -o data-service main.go

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/data-service .

EXPOSE 3003

CMD ["./data-service"]
```

### 阶段3：容器化和编排 (预计2小时)

#### 3.1 构建Docker镜像

为每个服务构建Docker镜像：

```bash
# 用户服务
cd services/user-service
docker build -t user-service:v1.0 .

# 设备服务
cd ../device-service
docker build -t device-service:v1.0 .

# 数据服务
cd ../data-service
docker build -t data-service:v1.0 .

# 验证镜像
docker images | grep service
```

#### 3.2 创建Kubernetes配置

创建 `k8s/base/namespace.yaml`：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: iot-platform
```

创建 `k8s/base/user-service.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: iot-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:v1.0
        ports:
        - containerPort: 3001
        env:
        - name: DB_HOST
          value: postgres
        - name: DB_PORT
          value: "5432"
        - name: DB_NAME
          value: iot_platform
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: iot-platform
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 3001
  type: ClusterIP
```

创建 `k8s/base/device-service.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: device-service
  namespace: iot-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: device-service
  template:
    metadata:
      labels:
        app: device-service
    spec:
      containers:
      - name: device-service
        image: device-service:v1.0
        ports:
        - containerPort: 3002
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "400m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3002
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: device-service
  namespace: iot-platform
spec:
  selector:
    app: device-service
  ports:
  - port: 80
    targetPort: 3002
  type: ClusterIP
```

创建 `k8s/base/data-service.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-service
  namespace: iot-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-service
  template:
    metadata:
      labels:
        app: data-service
    spec:
      containers:
      - name: data-service
        image: data-service:v1.0
        ports:
        - containerPort: 3003
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: url
        - name: REDIS_URL
          value: redis:6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3003
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: data-service
  namespace: iot-platform
spec:
  selector:
    app: data-service
  ports:
  - port: 80
    targetPort: 3003
  type: ClusterIP
```

#### 3.3 创建Secrets

创建 `k8s/base/secrets.yaml`：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: iot-platform
type: Opaque
stringData:
  username: iot_user
  password: iot_password
---
apiVersion: v1
kind: Secret
metadata:
  name: mongo-secret
  namespace: iot-platform
type: Opaque
stringData:
  url: mongodb://admin:admin_password@mongodb:27017
---
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: iot-platform
type: Opaque
stringData:
  secret: your-super-secret-jwt-key-change-in-production
```

#### 3.4 创建Ingress

创建 `k8s/base/ingress.yaml`：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: iot-platform-ingress
  namespace: iot-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: iot-platform.local
    http:
      paths:
      - path: /api/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
      - path: /api/devices
        pathType: Prefix
        backend:
          service:
            name: device-service
            port:
              number: 80
      - path: /api/data
        pathType: Prefix
        backend:
          service:
            name: data-service
            port:
              number: 80
```

#### 3.5 部署到Kubernetes

```bash
# 创建命名空间
kubectl apply -f k8s/base/namespace.yaml

# 创建Secrets
kubectl apply -f k8s/base/secrets.yaml

# 部署服务
kubectl apply -f k8s/base/user-service.yaml
kubectl apply -f k8s/base/device-service.yaml
kubectl apply -f k8s/base/data-service.yaml

# 部署Ingress
kubectl apply -f k8s/base/ingress.yaml

# 查看部署状态
kubectl get pods -n iot-platform
kubectl get services -n iot-platform
kubectl get ingress -n iot-platform

# 查看日志
kubectl logs -f deployment/user-service -n iot-platform
```

#### 3.6 配置水平自动扩展

创建 `k8s/base/hpa.yaml`：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-service-hpa
  namespace: iot-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

应用HPA配置：

```bash
kubectl apply -f k8s/base/hpa.yaml
kubectl get hpa -n iot-platform
```

### 阶段4：CI/CD流程 (预计1.5小时)

#### 4.1 GitHub Actions配置

创建 `.github/workflows/ci-cd.yml`：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: docker.io
  IMAGE_PREFIX: your-dockerhub-username

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Test User Service
      run: |
        cd services/user-service
        npm ci
        npm test
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Test Device Service
      run: |
        cd services/device-service
        pip install -r requirements.txt
        pytest
    
    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.20'
    
    - name: Test Data Service
      run: |
        cd services/data-service
        go test ./...

  build-and-push:
    name: Build and Push Images
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    strategy:
      matrix:
        service: [user-service, device-service, data-service]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=semver,pattern={{version}}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: ./services/${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    name: Deploy to Kubernetes
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.25.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to Kubernetes
      run: |
        export KUBECONFIG=kubeconfig
        kubectl apply -f k8s/base/
        kubectl rollout status deployment/user-service -n iot-platform
        kubectl rollout status deployment/device-service -n iot-platform
        kubectl rollout status deployment/data-service -n iot-platform
    
    - name: Verify deployment
      run: |
        export KUBECONFIG=kubeconfig
        kubectl get pods -n iot-platform
        kubectl get services -n iot-platform
```

#### 4.2 GitLab CI配置

创建 `.gitlab-ci.yml`：

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

# 测试阶段
test-user-service:
  stage: test
  image: node:18
  script:
    - cd services/user-service
    - npm ci
    - npm test

test-device-service:
  stage: test
  image: python:3.10
  script:
    - cd services/device-service
    - pip install -r requirements.txt
    - pytest

test-data-service:
  stage: test
  image: golang:1.20
  script:
    - cd services/data-service
    - go test ./...

# 构建阶段
.build-template: &build-template
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd services/$SERVICE_NAME
    - docker build -t $CI_REGISTRY_IMAGE/$SERVICE_NAME:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/$SERVICE_NAME:$CI_COMMIT_SHA
  only:
    - main

build-user-service:
  <<: *build-template
  variables:
    SERVICE_NAME: user-service

build-device-service:
  <<: *build-template
  variables:
    SERVICE_NAME: device-service

build-data-service:
  <<: *build-template
  variables:
    SERVICE_NAME: data-service

# 部署阶段
deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - kubectl apply -f k8s/base/
    - kubectl set image deployment/user-service user-service=$CI_REGISTRY_IMAGE/user-service:$CI_COMMIT_SHA -n iot-platform
    - kubectl set image deployment/device-service device-service=$CI_REGISTRY_IMAGE/device-service:$CI_COMMIT_SHA -n iot-platform
    - kubectl set image deployment/data-service data-service=$CI_REGISTRY_IMAGE/data-service:$CI_COMMIT_SHA -n iot-platform
    - kubectl rollout status deployment/user-service -n iot-platform
    - kubectl rollout status deployment/device-service -n iot-platform
    - kubectl rollout status deployment/data-service -n iot-platform
  only:
    - main
  when: manual
```

### 阶段5：监控和日志 (预计1.5小时)

#### 5.1 部署Prometheus

创建 `monitoring/prometheus/values.yaml`：

```yaml
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    retention: 30d
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

grafana:
  enabled: true
  adminPassword: admin
  persistence:
    enabled: true
    size: 10Gi
```

使用Helm安装Prometheus Stack：

```bash
# 添加Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 安装Prometheus Stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/prometheus/values.yaml

# 查看部署状态
kubectl get pods -n monitoring
```

#### 5.2 创建ServiceMonitor

创建 `monitoring/servicemonitor.yaml`：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: iot-platform-services
  namespace: iot-platform
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      monitoring: enabled
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

为服务添加监控标签：

```bash
kubectl label service user-service monitoring=enabled -n iot-platform
kubectl label service device-service monitoring=enabled -n iot-platform
kubectl label service data-service monitoring=enabled -n iot-platform
```

#### 5.3 配置Grafana仪表板

访问Grafana：

```bash
# 获取Grafana密码
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# 端口转发
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 访问 http://localhost:3000
# 用户名: admin
# 密码: 上面获取的密码
```

导入预设仪表板：
- Kubernetes Cluster Monitoring (ID: 7249)
- Node Exporter Full (ID: 1860)
- Kubernetes Deployment Statefulset Daemonset metrics (ID: 8588)

#### 5.4 部署ELK Stack

创建 `monitoring/elasticsearch.yaml`：

```yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: logging
spec:
  version: 8.10.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 50Gi
```

创建 `monitoring/kibana.yaml`：

```yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: logging
spec:
  version: 8.10.0
  count: 1
  elasticsearchRef:
    name: elasticsearch
```

部署ELK：

```bash
# 安装ECK Operator
kubectl create -f https://download.elastic.co/downloads/eck/2.9.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/2.9.0/operator.yaml

# 创建命名空间
kubectl create namespace logging

# 部署Elasticsearch和Kibana
kubectl apply -f monitoring/elasticsearch.yaml
kubectl apply -f monitoring/kibana.yaml

# 查看状态
kubectl get elasticsearch -n logging
kubectl get kibana -n logging
```

## 测试验证

### 功能测试

#### 1. 用户服务测试

```bash
# 注册用户
curl -X POST http://iot-platform.local/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 用户登录
curl -X POST http://iot-platform.local/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 保存返回的token
export TOKEN="your-jwt-token"

# 获取用户信息
curl -X GET http://iot-platform.local/api/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. 设备服务测试

```bash
# 注册设备
curl -X POST http://iot-platform.local/api/devices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Temperature Sensor 1",
    "type": "temperature",
    "userId": 1,
    "config": {
      "interval": 60,
      "threshold": {"min": 0, "max": 50}
    }
  }'

# 获取设备列表
curl -X GET http://iot-platform.local/api/devices \
  -H "Authorization: Bearer $TOKEN"

# 获取设备详情
curl -X GET http://iot-platform.local/api/devices/{deviceId} \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. 数据服务测试

```bash
# 上报数据
curl -X POST http://iot-platform.local/api/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "deviceId": "your-device-id",
    "data": {
      "temperature": 25.5,
      "humidity": 60.0
    }
  }'

# 查询设备数据
curl -X GET http://iot-platform.local/api/data/{deviceId} \
  -H "Authorization: Bearer $TOKEN"

# 获取最新数据
curl -X GET http://iot-platform.local/api/data/{deviceId}/latest \
  -H "Authorization: Bearer $TOKEN"
```

### 性能测试

使用Apache Bench进行压力测试：

```bash
# 安装ab
sudo apt-get install apache2-utils

# 测试用户登录接口
ab -n 1000 -c 10 -p login.json -T application/json \
  http://iot-platform.local/api/users/login

# 测试数据上报接口
ab -n 10000 -c 100 -p data.json -T application/json \
  -H "Authorization: Bearer $TOKEN" \
  http://iot-platform.local/api/data
```

### 负载测试

使用k6进行负载测试：

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // 2分钟内增加到100用户
    { duration: '5m', target: 100 },  // 保持100用户5分钟
    { duration: '2m', target: 200 },  // 增加到200用户
    { duration: '5m', target: 200 },  // 保持200用户5分钟
    { duration: '2m', target: 0 },    // 逐渐减少到0
  ],
};

export default function () {
  // 登录
  let loginRes = http.post('http://iot-platform.local/api/users/login', 
    JSON.stringify({
      username: 'testuser',
      password: 'password123'
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });
  
  let token = loginRes.json('token');
  
  // 上报数据
  let dataRes = http.post('http://iot-platform.local/api/data',
    JSON.stringify({
      deviceId: 'test-device',
      data: {
        temperature: Math.random() * 50,
        humidity: Math.random() * 100
      }
    }),
    { 
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      } 
    }
  );
  
  check(dataRes, {
    'data posted': (r) => r.status === 201,
  });
  
  sleep(1);
}
```

运行负载测试：

```bash
k6 run load-test.js
```

### 监控验证

#### 1. 查看Prometheus指标

```bash
# 端口转发Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# 访问 http://localhost:9090
# 查询示例：
# - rate(http_requests_total[5m])
# - container_memory_usage_bytes
# - kube_pod_status_phase
```

#### 2. 查看Grafana仪表板

```bash
# 端口转发Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 访问 http://localhost:3000
# 查看预设仪表板
```

#### 3. 查看日志

```bash
# 查看服务日志
kubectl logs -f deployment/user-service -n iot-platform
kubectl logs -f deployment/device-service -n iot-platform
kubectl logs -f deployment/data-service -n iot-platform

# 查看所有Pod日志
kubectl logs -l app=user-service -n iot-platform --tail=100
```


## 故障排除

### 常见问题

#### 问题1：Pod无法启动

**症状**：Pod状态为CrashLoopBackOff或ImagePullBackOff

**排查步骤**：

```bash
# 查看Pod状态
kubectl get pods -n iot-platform

# 查看Pod详情
kubectl describe pod <pod-name> -n iot-platform

# 查看Pod日志
kubectl logs <pod-name> -n iot-platform

# 查看事件
kubectl get events -n iot-platform --sort-by='.lastTimestamp'
```

**常见原因**：
- 镜像拉取失败：检查镜像名称和仓库权限
- 配置错误：检查环境变量和Secret
- 资源不足：检查节点资源使用情况
- 健康检查失败：调整探针配置

#### 问题2：服务无法访问

**症状**：无法通过Ingress访问服务

**排查步骤**：

```bash
# 检查Service
kubectl get svc -n iot-platform
kubectl describe svc user-service -n iot-platform

# 检查Ingress
kubectl get ingress -n iot-platform
kubectl describe ingress iot-platform-ingress -n iot-platform

# 检查Ingress Controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx <ingress-controller-pod>

# 测试Service内部访问
kubectl run test-pod --image=curlimages/curl -it --rm -- sh
curl http://user-service.iot-platform.svc.cluster.local/health
```

**常见原因**：
- Ingress Controller未安装
- DNS解析问题
- Service选择器不匹配
- 端口配置错误

#### 问题3：数据库连接失败

**症状**：服务日志显示数据库连接错误

**排查步骤**：

```bash
# 检查数据库Pod
kubectl get pods -l app=postgres -n iot-platform
kubectl logs <postgres-pod> -n iot-platform

# 检查Secret
kubectl get secret postgres-secret -n iot-platform -o yaml

# 测试数据库连接
kubectl run psql-test --image=postgres:14 -it --rm -- \
  psql -h postgres -U iot_user -d iot_platform
```

**常见原因**：
- 数据库未就绪
- 连接字符串错误
- 认证信息错误
- 网络策略限制

#### 问题4：性能问题

**症状**：响应时间长，请求超时

**排查步骤**：

```bash
# 查看资源使用
kubectl top pods -n iot-platform
kubectl top nodes

# 查看HPA状态
kubectl get hpa -n iot-platform

# 查看Pod事件
kubectl describe pod <pod-name> -n iot-platform

# 查看Prometheus指标
# 访问Grafana查看CPU、内存、网络使用情况
```

**优化建议**：
- 增加副本数
- 调整资源限制
- 优化数据库查询
- 添加缓存层
- 启用HPA自动扩展


## 扩展思路

### 功能扩展

#### 1. 服务网格集成

使用Istio实现高级流量管理：

```bash
# 安装Istio
istioctl install --set profile=demo -y

# 启用自动注入
kubectl label namespace iot-platform istio-injection=enabled

# 重启Pod以注入Sidecar
kubectl rollout restart deployment -n iot-platform
```

功能：
- 流量管理（金丝雀发布、A/B测试）
- 安全通信（mTLS）
- 可观测性（分布式追踪）
- 熔断和重试

#### 2. API网关增强

使用Kong或Ambassador：

```bash
# 安装Kong
helm install kong kong/kong -n kong --create-namespace

# 配置插件
# - 限流
# - 认证
# - 日志
# - 监控
```

#### 3. 消息队列集成

完整的事件驱动架构：

```yaml
# Kafka配置
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: iot-kafka
  namespace: iot-platform
spec:
  kafka:
    version: 3.5.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    storage:
      type: persistent-claim
      size: 100Gi
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
```

#### 4. 数据分析服务

添加实时数据分析：

- 使用Apache Flink进行流处理
- 使用ClickHouse进行OLAP分析
- 使用Grafana展示实时仪表板

### 性能优化

#### 1. 缓存策略

多级缓存架构：

```
客户端缓存 (浏览器)
    ↓
CDN缓存
    ↓
API网关缓存
    ↓
应用缓存 (Redis)
    ↓
数据库
```

#### 2. 数据库优化

- 读写分离
- 分库分表
- 索引优化
- 查询优化

#### 3. 微服务优化

- 服务拆分细化
- 异步通信
- 批量处理
- 连接池优化

### 安全加固

#### 1. 网络安全

```yaml
# NetworkPolicy示例
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: iot-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### 2. 密钥管理

使用Vault管理敏感信息：

```bash
# 安装Vault
helm install vault hashicorp/vault -n vault --create-namespace

# 配置Vault
vault secrets enable -path=iot-platform kv-v2
vault kv put iot-platform/database username=iot_user password=secret
```

#### 3. 镜像安全

- 使用私有镜像仓库
- 镜像签名验证
- 漏洞扫描
- 最小化镜像


## 项目总结

### 技术要点

本项目涵盖的核心技术：

1. **微服务架构**：服务拆分、服务通信、服务治理
2. **容器化**：Docker镜像构建、多阶段构建、镜像优化
3. **Kubernetes**：Pod、Deployment、Service、Ingress、HPA
4. **CI/CD**：自动化测试、构建、部署流程
5. **监控告警**：Prometheus、Grafana、ELK Stack
6. **DevOps**：基础设施即代码、GitOps、自动化运维

### 学习收获

通过本项目，你应该掌握：

- ✅ 云原生应用的完整开发流程
- ✅ 微服务架构的设计和实现
- ✅ Docker和Kubernetes的实战应用
- ✅ CI/CD流程的搭建和优化
- ✅ 监控和日志系统的部署
- ✅ 生产环境的运维实践
- ✅ 问题排查和性能优化技巧

### 最佳实践总结

#### 1. 12-Factor应用原则

- 代码库：一份代码，多处部署
- 依赖：显式声明依赖
- 配置：环境变量存储配置
- 后端服务：把后端服务当作附加资源
- 构建、发布、运行：严格分离
- 进程：无状态进程
- 端口绑定：通过端口绑定提供服务
- 并发：通过进程模型进行扩展
- 易处理：快速启动和优雅终止
- 开发环境与生产环境等价
- 日志：把日志当作事件流
- 管理进程：后台管理任务当作一次性进程运行

#### 2. 云原生设计模式

- **Sidecar模式**：辅助容器提供额外功能
- **Ambassador模式**：代理容器处理网络通信
- **Adapter模式**：适配器容器标准化输出
- **健康检查**：Liveness和Readiness探针
- **优雅关闭**：处理SIGTERM信号
- **配置外部化**：ConfigMap和Secret
- **服务发现**：Kubernetes Service
- **负载均衡**：Service和Ingress

### 改进建议

项目可以进一步改进的方向：

1. **安全性**：
   - 实现OAuth2.0认证
   - 添加API限流
   - 启用mTLS
   - 实施RBAC

2. **可靠性**：
   - 实现熔断器
   - 添加重试机制
   - 实现降级策略
   - 多区域部署

3. **可观测性**：
   - 分布式追踪
   - 业务指标监控
   - 告警规则优化
   - 日志聚合分析

4. **性能**：
   - 缓存优化
   - 数据库优化
   - 异步处理
   - CDN加速


## 相关资源

### 官方文档
- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Docker官方文档](https://docs.docker.com/)
- [Helm官方文档](https://helm.sh/docs/)
- [Prometheus文档](https://prometheus.io/docs/)

### 学习资源
- [云原生技术公开课](https://edu.aliyun.com/roadmap/cloudnative)
- [Kubernetes中文社区](https://www.kubernetes.org.cn/)
- [CNCF Cloud Native Interactive Landscape](https://landscape.cncf.io/)

### 开源项目
- [Istio服务网格](https://github.com/istio/istio)
- [Linkerd服务网格](https://github.com/linkerd/linkerd2)
- [Argo CD GitOps](https://github.com/argoproj/argo-cd)
- [Flux GitOps](https://github.com/fluxcd/flux2)

### 书籍推荐
- 《Kubernetes权威指南》
- 《云原生应用架构实践》
- 《微服务设计》
- 《DevOps实践指南》


## 下一步

完成本项目后，建议继续学习：

- [服务网格技术](link) - 深入学习Istio
- [GitOps实践](link) - 学习ArgoCD和Flux
- [可观测性](link) - 深入学习监控和追踪
- [云原生安全](link) - 学习安全最佳实践


## 参考资料

1. Kubernetes Documentation - Kubernetes Authors
2. Docker Documentation - Docker Inc.
3. Cloud Native Patterns - Cornelia Davis
4. Kubernetes Patterns - Bilgin Ibryam & Roland Huß
5. The Twelve-Factor App - Adam Wiggins
6. Site Reliability Engineering - Google
7. Building Microservices - Sam Newman

---

**项目难度**：⭐⭐⭐⭐☆ (高级)  
**完成时间**：约220分钟  
**技术栈**：Kubernetes, Docker, Node.js, Python, Go  
**适合人群**：有一定后端开发经验，想学习云原生技术的开发者

**反馈与讨论**：欢迎在评论区分享你的项目成果和遇到的问题！

{% endraw %}
