---
title: "IoT后端系统开发实战"
description: "从零开始构建一个完整的IoT后端系统，包括设备管理、数据采集、RESTful API、MQTT通信和数据可视化，适合后端开发进阶学习"
slug: "iot-backend-system-development"

# 分类信息
domain: "云端与后台"
module: "后端开发"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - IoT后端
  - 系统开发
  - RESTful API
  - MQTT
  - 数据库设计
  - 后端架构
prerequisites:
  - "restful-api-design-development-guide"
  - "database-design"
  - "authentication-authorization"
related_contents:
  - "microservices"
  - "message-queue"

# 学习信息
estimated_time: 240
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
  - IoT后端开发
  - 物联网系统
  - Python FastAPI
  - MQTT服务器
  - 设备管理系统
  - 时序数据库
cover_image: ""

# 项目特定信息
project_type: "software"
repository: ""
demo_video: ""
---

# IoT后端系统开发实战


## 项目概述

### 项目简介

本项目将带你从零开始构建一个功能完整的IoT后端系统，实现设备接入、数据采集、存储、处理和可视化等核心功能。该系统采用现代化的微服务架构，使用Python FastAPI框架开发RESTful API，集成MQTT协议实现设备通信，使用PostgreSQL和InfluxDB分别存储关系数据和时序数据。

这是一个生产级别的IoT后端系统，包含完整的设备管理、用户认证、数据处理、API接口等功能，适合作为实际IoT项目的基础架构。

### 项目演示

完成后的系统将提供以下功能：

```
IoT后端系统架构
┌─────────────────────────────────────────────────┐
│  设备层 (IoT Devices)                            │
│  ┌──────┐  ┌──────┐  ┌──────┐                  │
│  │设备1 │  │设备2 │  │设备N │                  │
│  └──┬───┘  └──┬───┘  └──┬───┘                  │
│     │         │         │                        │
│     └─────────┴─────────┘                        │
│              MQTT                                 │
├─────────────────────────────────────────────────┤
│  接入层 (MQTT Broker)                            │
│  ┌─────────────────────────────────────┐        │
│  │  EMQX / Mosquitto                   │        │
│  │  - 设备认证                          │        │
│  │  - 消息路由                          │        │
│  │  - QoS保证                           │        │
│  └─────────────────────────────────────┘        │
├─────────────────────────────────────────────────┤
│  应用层 (Backend Services)                       │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ API服务      │  │ 数据处理服务  │            │
│  │ (FastAPI)    │  │ (Python)     │            │
│  └──────────────┘  └──────────────┘            │
├─────────────────────────────────────────────────┤
│  数据层 (Databases)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │PostgreSQL│  │ InfluxDB │  │  Redis   │     │
│  │设备信息  │  │时序数据  │  │  缓存    │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
```

### 学习目标

完成本项目后，你将掌握：

- [ ] **系统架构设计**：理解IoT后端系统的整体架构和各组件的作用
- [ ] **RESTful API开发**：使用FastAPI框架开发高性能的RESTful API
- [ ] **数据库设计**：设计合理的关系型数据库和时序数据库模型
- [ ] **MQTT协议应用**：实现MQTT客户端，处理设备消息
- [ ] **认证授权机制**：实现JWT认证和基于角色的权限控制
- [ ] **异步编程**：掌握Python异步编程和并发处理
- [ ] **数据处理**：实现数据验证、转换和存储
- [ ] **系统部署**：使用Docker容器化部署整个系统


## 项目特点

- ✨ **现代化技术栈**：使用FastAPI、PostgreSQL、InfluxDB等主流技术
- ✨ **异步高性能**：基于异步编程，支持高并发请求
- ✨ **完整的功能**：涵盖设备管理、数据采集、用户认证、API接口
- ✨ **RESTful设计**：遵循REST架构风格，API设计规范
- ✨ **数据库优化**：合理的数据模型设计和索引优化
- ✨ **安全可靠**：JWT认证、密码加密、输入验证
- ✨ **容器化部署**：使用Docker Compose一键部署
- ✨ **可扩展性强**：模块化设计，易于扩展新功能

## 技术栈

### 后端技术
- **开发语言**：Python 3.9+
- **Web框架**：FastAPI 0.104+ (高性能异步框架)
- **ORM框架**：SQLAlchemy 2.0+ (数据库ORM)
- **数据验证**：Pydantic 2.0+ (数据模型和验证)
- **认证授权**：python-jose (JWT), passlib (密码加密)
- **MQTT客户端**：paho-mqtt 1.6+
- **异步支持**：asyncio, asyncpg

### 数据库
- **关系数据库**：PostgreSQL 14+ (存储设备信息、用户数据)
- **时序数据库**：InfluxDB 2.x (存储设备遥测数据)
- **缓存数据库**：Redis 7.0+ (缓存和会话管理)

### 开发工具
- **IDE**：VS Code / PyCharm
- **API测试**：Postman / Insomnia / HTTPie
- **MQTT测试**：MQTTX / MQTT Explorer
- **数据库管理**：DBeaver / pgAdmin
- **容器化**：Docker + Docker Compose

### 可选组件
- **MQTT Broker**：EMQX / Mosquitto (设备接入)
- **监控工具**：Prometheus + Grafana
- **日志管理**：ELK Stack

## 硬件清单

### 服务器要求

本项目可以在本地开发环境或云服务器上运行。

#### 开发环境（最小配置）

| 组件 | 配置 | 说明 |
|------|------|------|
| CPU | 2核 | 支持基本开发测试 |
| 内存 | 4GB | 运行所有服务 |
| 硬盘 | 20GB | 存储代码和数据 |
| 操作系统 | Windows/Linux/macOS | 支持Docker |

**参考成本**：使用本地电脑，无额外成本

#### 生产环境（推荐配置）

| 组件 | 配置 | 说明 |
|------|------|------|
| CPU | 4核+ | 支持100+设备 |
| 内存 | 8GB+ | 保证性能 |
| 硬盘 | 100GB SSD | 存储数据 |
| 网络 | 100Mbps+ | 稳定网络 |
| 操作系统 | Ubuntu 22.04 LTS | 推荐Linux |

**参考成本**：云服务器约 ¥200-400/月

### 测试设备（可选）

用于测试系统功能的IoT设备：

| 设备 | 型号 | 数量 | 用途 | 参考价格 |
|------|------|------|------|----------|
| 开发板 | ESP32 | 1-2 | 模拟IoT设备 | ¥30/个 |
| 传感器 | DHT22 | 1 | 温湿度数据 | ¥15/个 |

**总成本**：约 ¥50-100（可选）

## 软件要求

### 必需软件

```bash
# Python环境
Python 3.9+

# 数据库
PostgreSQL 14+
Redis 7.0+

# 容器化（推荐）
Docker 20.10+
Docker Compose 2.0+

# 版本控制
Git 2.30+
```

### 推荐工具

```bash
# Python包管理
pip 21+
virtualenv / venv

# API测试
Postman / HTTPie

# 数据库管理
DBeaver / pgAdmin

# MQTT测试
MQTTX
```


## 系统架构

### 整体架构

```mermaid
graph TB
    subgraph "设备层"
        D1[IoT设备1]
        D2[IoT设备2]
        D3[IoT设备N]
    end
    
    subgraph "接入层"
        MQTT[MQTT Broker]
    end
    
    subgraph "应用层"
        API[API服务<br/>FastAPI]
        PROC[数据处理服务]
        AUTH[认证服务]
    end
    
    subgraph "数据层"
        PG[(PostgreSQL<br/>设备/用户)]
        INFLUX[(InfluxDB<br/>时序数据)]
        REDIS[(Redis<br/>缓存)]
    end
    
    D1 -->|MQTT| MQTT
    D2 -->|MQTT| MQTT
    D3 -->|MQTT| MQTT
    
    MQTT -->|消息| PROC
    PROC --> INFLUX
    PROC --> REDIS
    
    API --> PG
    API --> INFLUX
    API --> REDIS
    API --> AUTH
    
    AUTH --> PG
```

### 核心模块说明

#### 1. API服务模块
- **功能**：提供RESTful API接口
- **技术**：FastAPI + SQLAlchemy
- **端口**：8000
- **主要接口**：
  - 设备管理：CRUD操作
  - 用户管理：注册、登录、权限
  - 数据查询：历史数据、实时数据
  - 统计分析：数据聚合、报表

#### 2. 数据处理模块
- **功能**：处理MQTT消息，存储数据
- **技术**：paho-mqtt + InfluxDB Client
- **处理流程**：
  1. 订阅MQTT主题
  2. 接收设备消息
  3. 数据验证和转换
  4. 存储到InfluxDB
  5. 更新设备状态

#### 3. 认证授权模块
- **功能**：用户认证和权限控制
- **技术**：JWT + passlib
- **功能点**：
  - 用户注册和登录
  - JWT令牌生成和验证
  - 基于角色的权限控制
  - 密码加密存储

#### 4. 数据存储模块
- **PostgreSQL**：
  - 用户表（users）
  - 设备表（devices）
  - 设备类型表（device_types）
  - 权限表（roles, permissions）
  
- **InfluxDB**：
  - 设备遥测数据（telemetry）
  - 设备事件（events）
  - 系统指标（metrics）
  
- **Redis**：
  - 用户会话
  - API缓存
  - 设备在线状态

### 数据流图

```mermaid
sequenceDiagram
    participant Device as IoT设备
    participant MQTT as MQTT Broker
    participant Processor as 数据处理服务
    participant API as API服务
    participant DB as 数据库
    participant Client as 客户端
    
    Device->>MQTT: 1. 发布遥测数据
    MQTT->>Processor: 2. 转发消息
    Processor->>DB: 3. 存储到InfluxDB
    Processor->>DB: 4. 更新设备状态(Redis)
    
    Client->>API: 5. 请求设备数据
    API->>API: 6. 验证JWT令牌
    API->>DB: 7. 查询数据
    DB-->>API: 8. 返回数据
    API-->>Client: 9. 返回JSON响应
```


## 数据库设计

### PostgreSQL数据模型

#### 用户表 (users)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### 设备表 (devices)

```sql
CREATE TABLE devices (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    device_type VARCHAR(64) NOT NULL,
    product_key VARCHAR(64) NOT NULL,
    device_secret VARCHAR(128) NOT NULL,
    status VARCHAR(32) DEFAULT 'offline',
    last_online TIMESTAMP,
    last_offline TIMESTAMP,
    config JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_owner ON devices(owner_id);
```

#### 设备类型表 (device_types)

```sql
CREATE TABLE device_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    description TEXT,
    schema JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### InfluxDB数据模型

#### 遥测数据 (telemetry)

```
measurement: telemetry
tags:
  - device_id: 设备ID
  - device_type: 设备类型
fields:
  - temperature: 温度值
  - humidity: 湿度值
  - voltage: 电压值
  - (其他传感器数据)
timestamp: 时间戳
```

#### 设备事件 (events)

```
measurement: events
tags:
  - device_id: 设备ID
  - event_type: 事件类型
fields:
  - message: 事件消息
  - severity: 严重程度
timestamp: 时间戳
```

## 实现步骤

### 阶段1：环境搭建 (预计30分钟)

#### 1.1 创建项目目录

```bash
# 创建项目根目录
mkdir iot-backend
cd iot-backend

# 创建目录结构
mkdir -p app/{api,models,schemas,services,core,db}
mkdir -p app/api/v1/endpoints
mkdir -p tests
mkdir -p docker
mkdir -p scripts

# 项目结构
tree -L 3
```

项目结构：
```
iot-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── devices.py
│   │       │   ├── users.py
│   │       │   └── telemetry.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── deps.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── user.py
│   │   └── device.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── device.py
│   ├── services/
│   │   ├── device_service.py
│   │   ├── telemetry_service.py
│   │   └── mqtt_service.py
│   └── main.py
├── tests/
├── docker/
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

#### 1.2 创建Python虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

#### 1.3 安装依赖包

创建 `requirements.txt`：

```txt
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.12.1

# InfluxDB
influxdb-client==1.38.0

# Redis
redis==5.0.1

# MQTT
paho-mqtt==1.6.1

# 认证和安全
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 数据验证
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# 工具库
python-dotenv==1.0.0
loguru==0.7.2
```

安装依赖：

```bash
pip install -r requirements.txt
```


#### 1.4 配置Docker Compose

创建 `docker/docker-compose.yml`：

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:14-alpine
    container_name: iot-postgres
    environment:
      POSTGRES_DB: iot_platform
      POSTGRES_USER: iot_user
      POSTGRES_PASSWORD: iot_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - iot-network
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: iot-redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - iot-network
    restart: unless-stopped

  # InfluxDB时序数据库
  influxdb:
    image: influxdb:2.7-alpine
    container_name: iot-influxdb
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: adminpassword
      DOCKER_INFLUXDB_INIT_ORG: iot-org
      DOCKER_INFLUXDB_INIT_BUCKET: iot-data
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: my-super-secret-auth-token
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2
    networks:
      - iot-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  influxdb_data:

networks:
  iot-network:
    driver: bridge
```

启动数据库服务：

```bash
cd docker
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 1.5 创建配置文件

创建 `.env.example`：

```env
# 应用配置
APP_NAME=IoT Backend System
DEBUG=True
API_V1_PREFIX=/api/v1

# 数据库配置
DATABASE_URL=postgresql+asyncpg://iot_user:iot_password@localhost:5432/iot_platform

# Redis配置
REDIS_URL=redis://localhost:6379/0

# InfluxDB配置
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-super-secret-auth-token
INFLUXDB_ORG=iot-org
INFLUXDB_BUCKET=iot-data

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT配置（可选）
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

复制为实际配置文件：

```bash
cp .env.example .env
```

### 阶段2：核心模块开发 (预计2小时)

#### 2.1 配置管理

创建 `app/core/config.py`：

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "IoT Backend System"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str
    
    # Redis配置
    REDIS_URL: str
    
    # InfluxDB配置
    INFLUXDB_URL: str
    INFLUXDB_TOKEN: str
    INFLUXDB_ORG: str
    INFLUXDB_BUCKET: str
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MQTT配置
    MQTT_BROKER_HOST: Optional[str] = None
    MQTT_BROKER_PORT: int = 1883
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 2.2 数据库连接

创建 `app/db/session.py`：

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖注入：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

创建 `app/db/base.py`：

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 导入所有模型，确保它们被注册
from app.models.user import User
from app.models.device import Device
```


#### 2.3 数据模型

创建 `app/models/user.py`：

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

创建 `app/models/device.py`：

```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Device(Base):
    """设备模型"""
    __tablename__ = "devices"
    
    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    device_type = Column(String(64), nullable=False, index=True)
    product_key = Column(String(64), nullable=False)
    device_secret = Column(String(128), nullable=False)
    
    # 状态信息
    status = Column(String(32), default="offline", index=True)
    last_online = Column(DateTime(timezone=True))
    last_offline = Column(DateTime(timezone=True))
    
    # 配置信息
    config = Column(JSON, default={})
    tags = Column(JSON, default=[])
    
    # 所有者
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
```

#### 2.4 Pydantic模式

创建 `app/schemas/user.py`：

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """用户创建模式"""
    password: str

class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    """用户响应模式"""
    pass

class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None
```

创建 `app/schemas/device.py`：

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class DeviceBase(BaseModel):
    """设备基础模式"""
    name: str
    device_type: str
    product_key: str

class DeviceCreate(DeviceBase):
    """设备创建模式"""
    config: Optional[Dict] = {}
    tags: Optional[List[str]] = []

class DeviceUpdate(BaseModel):
    """设备更新模式"""
    name: Optional[str] = None
    config: Optional[Dict] = None
    tags: Optional[List[str]] = None

class DeviceInDB(DeviceBase):
    """数据库中的设备模式"""
    id: str
    device_secret: str
    status: str
    last_online: Optional[datetime] = None
    config: Dict
    tags: List[str]
    owner_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Device(DeviceInDB):
    """设备响应模式"""
    pass

class TelemetryData(BaseModel):
    """遥测数据模式"""
    device_id: str
    timestamp: datetime
    data: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "device-001",
                "timestamp": "2024-01-01T12:00:00Z",
                "data": {
                    "temperature": 25.5,
                    "humidity": 65.0
                }
            }
        }
```


#### 2.5 安全认证

创建 `app/core/security.py`：

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

创建 `app/core/deps.py`：

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### 阶段3：业务服务开发 (预计2小时)

#### 3.1 设备管理服务

创建 `app/services/device_service.py`：

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import secrets
from datetime import datetime

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

class DeviceService:
    """设备管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_device(
        self,
        device_in: DeviceCreate,
        owner_id: int
    ) -> Device:
        """创建设备"""
        # 生成设备ID和密钥
        device_id = f"device-{secrets.token_hex(8)}"
        device_secret = secrets.token_urlsafe(32)
        
        device = Device(
            id=device_id,
            name=device_in.name,
            device_type=device_in.device_type,
            product_key=device_in.product_key,
            device_secret=device_secret,
            config=device_in.config,
            tags=device_in.tags,
            owner_id=owner_id
        )
        
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        
        return device
    
    async def get_device(self, device_id: str) -> Optional[Device]:
        """获取设备"""
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()
    
    async def list_devices(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        device_type: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[Device]:
        """获取设备列表"""
        query = select(Device)
        
        if status:
            query = query.where(Device.status == status)
        if device_type:
            query = query.where(Device.device_type == device_type)
        if owner_id:
            query = query.where(Device.owner_id == owner_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_device(
        self,
        device_id: str,
        device_in: DeviceUpdate
    ) -> Optional[Device]:
        """更新设备"""
        device = await self.get_device(device_id)
        if not device:
            return None
        
        update_data = device_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)
        
        await self.db.commit()
        await self.db.refresh(device)
        
        return device
    
    async def update_device_status(
        self,
        device_id: str,
        status: str
    ) -> Optional[Device]:
        """更新设备状态"""
        device = await self.get_device(device_id)
        if not device:
            return None
        
        device.status = status
        if status == "online":
            device.last_online = datetime.utcnow()
        elif status == "offline":
            device.last_offline = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(device)
        
        return device
    
    async def delete_device(self, device_id: str) -> bool:
        """删除设备"""
        device = await self.get_device(device_id)
        if not device:
            return False
        
        await self.db.delete(device)
        await self.db.commit()
        
        return True
```


#### 3.2 遥测数据服务

创建 `app/services/telemetry_service.py`：

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from typing import List, Dict, Any
from app.core.config import settings

class TelemetryService:
    """遥测数据服务"""
    
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = settings.INFLUXDB_BUCKET
        self.org = settings.INFLUXDB_ORG
    
    async def write_telemetry(
        self,
        device_id: str,
        device_type: str,
        data: Dict[str, Any],
        timestamp: datetime = None
    ):
        """写入遥测数据"""
        point = Point("telemetry") \
            .tag("device_id", device_id) \
            .tag("device_type", device_type) \
            .time(timestamp or datetime.utcnow())
        
        # 添加所有数据字段
        for key, value in data.items():
            if isinstance(value, (int, float)):
                point = point.field(key, float(value))
            elif isinstance(value, str):
                point = point.field(key, value)
            elif isinstance(value, bool):
                point = point.field(key, value)
        
        self.write_api.write(bucket=self.bucket, record=point)
    
    async def query_latest(
        self,
        device_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """查询最新数据"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "telemetry")
          |> filter(fn: (r) => r["device_id"] == "{device_id}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
        '''
        
        result = self.query_api.query(query=query, org=self.org)
        
        # 解析结果
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    "time": record.get_time().isoformat(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "device_id": record.values.get("device_id")
                })
        
        return data_points
    
    async def query_range(
        self,
        device_id: str,
        start: datetime,
        end: datetime,
        field: str = None
    ) -> List[Dict]:
        """查询时间范围数据"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start.isoformat()}Z, stop: {end.isoformat()}Z)
          |> filter(fn: (r) => r["_measurement"] == "telemetry")
          |> filter(fn: (r) => r["device_id"] == "{device_id}")
        '''
        
        if field:
            query += f'  |> filter(fn: (r) => r["_field"] == "{field}")'
        
        result = self.query_api.query(query=query, org=self.org)
        
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    "time": record.get_time().isoformat(),
                    "field": record.get_field(),
                    "value": record.get_value()
                })
        
        return data_points
    
    async def query_aggregated(
        self,
        device_id: str,
        start: datetime,
        end: datetime,
        field: str,
        window: str = "1h",
        aggregation: str = "mean"
    ) -> List[Dict]:
        """查询聚合数据"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start.isoformat()}Z, stop: {end.isoformat()}Z)
          |> filter(fn: (r) => r["_measurement"] == "telemetry")
          |> filter(fn: (r) => r["device_id"] == "{device_id}")
          |> filter(fn: (r) => r["_field"] == "{field}")
          |> aggregateWindow(every: {window}, fn: {aggregation})
        '''
        
        result = self.query_api.query(query=query, org=self.org)
        
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value()
                })
        
        return data_points
    
    def close(self):
        """关闭连接"""
        self.client.close()
```

#### 3.3 MQTT消息处理服务

创建 `app/services/mqtt_service.py`：

```python
import paho.mqtt.client as mqtt
import json
from loguru import logger
from typing import Callable, Dict
from app.core.config import settings

class MQTTService:
    """MQTT服务"""
    
    def __init__(self):
        self.broker_host = settings.MQTT_BROKER_HOST
        self.broker_port = settings.MQTT_BROKER_PORT
        self.client = mqtt.Client()
        
        # 设置回调
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # 消息处理器
        self.message_handlers: Dict[str, Callable] = {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker: {self.broker_host}")
            # 订阅设备上行主题
            self.client.subscribe("device/+/telemetry")
            self.client.subscribe("device/+/event")
            self.client.subscribe("device/+/status")
        else:
            logger.error(f"Failed to connect to MQTT broker, code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """消息回调"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.info(f"Received message on topic: {topic}")
            
            # 解析设备ID和消息类型
            parts = topic.split('/')
            if len(parts) >= 3:
                device_id = parts[1]
                message_type = parts[2]
                
                # 调用对应的处理器
                if message_type in self.message_handlers:
                    self.message_handlers[message_type](device_id, payload)
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        logger.warning(f"Disconnected from MQTT broker, code: {rc}")
    
    def connect(self):
        """连接到MQTT Broker"""
        if self.broker_host:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info("MQTT service started")
    
    def disconnect(self):
        """断开连接"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT service stopped")
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def publish(self, topic: str, payload: dict):
        """发布消息"""
        self.client.publish(topic, json.dumps(payload))
    
    def send_command(self, device_id: str, command: dict):
        """发送命令到设备"""
        topic = f"device/{device_id}/command"
        self.publish(topic, command)
```


### 阶段4：API接口开发 (预计1.5小时)

#### 4.1 认证接口

创建 `app/api/v1/endpoints/auth.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查找用户
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

#### 4.2 设备管理接口

创建 `app/api/v1/endpoints/devices.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.schemas.device import Device, DeviceCreate, DeviceUpdate
from app.services.device_service import DeviceService
from app.core.deps import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建设备"""
    service = DeviceService(db)
    device = await service.create_device(device_in, current_user.id)
    return device

@router.get("/", response_model=List[Device])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备列表"""
    service = DeviceService(db)
    
    # 非超级用户只能查看自己的设备
    owner_id = None if current_user.is_superuser else current_user.id
    
    devices = await service.list_devices(
        skip=skip,
        limit=limit,
        status=status,
        device_type=device_type,
        owner_id=owner_id
    )
    return devices

@router.get("/{device_id}", response_model=Device)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备详情"""
    service = DeviceService(db)
    device = await service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return device

@router.patch("/{device_id}", response_model=Device)
async def update_device(
    device_id: str,
    device_in: DeviceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新设备"""
    service = DeviceService(db)
    device = await service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    device = await service.update_device(device_id, device_in)
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除设备"""
    service = DeviceService(db)
    device = await service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await service.delete_device(device_id)
```


#### 4.3 遥测数据接口

创建 `app/api/v1/endpoints/telemetry.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.user import User
from app.schemas.device import TelemetryData
from app.services.telemetry_service import TelemetryService
from app.services.device_service import DeviceService
from app.db.session import get_db
from app.core.deps import get_current_active_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# 创建全局遥测服务实例
telemetry_service = TelemetryService()

@router.get("/{device_id}/latest")
async def get_latest_telemetry(
    device_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备最新数据"""
    # 验证设备存在且有权限
    device_service = DeviceService(db)
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    data = await telemetry_service.query_latest(device_id, limit)
    return {"device_id": device_id, "data": data}

@router.get("/{device_id}/history")
async def get_telemetry_history(
    device_id: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    field: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备历史数据"""
    # 验证设备存在且有权限
    device_service = DeviceService(db)
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 默认查询最近24小时
    if not start:
        start = datetime.utcnow() - timedelta(hours=24)
    if not end:
        end = datetime.utcnow()
    
    data = await telemetry_service.query_range(device_id, start, end, field)
    return {
        "device_id": device_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "data": data
    }

@router.get("/{device_id}/aggregated")
async def get_aggregated_telemetry(
    device_id: str,
    field: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    window: str = Query("1h"),
    aggregation: str = Query("mean"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取聚合数据"""
    # 验证设备存在且有权限
    device_service = DeviceService(db)
    device = await device_service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if not current_user.is_superuser and device.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 默认查询最近24小时
    if not start:
        start = datetime.utcnow() - timedelta(hours=24)
    if not end:
        end = datetime.utcnow()
    
    data = await telemetry_service.query_aggregated(
        device_id, start, end, field, window, aggregation
    )
    return {
        "device_id": device_id,
        "field": field,
        "window": window,
        "aggregation": aggregation,
        "data": data
    }
```

#### 4.4 API路由汇总

创建 `app/api/v1/api.py`：

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, devices, telemetry

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
```

### 阶段5：主应用集成 (预计30分钟)

#### 5.1 创建主应用

创建 `app/main.py`：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.mqtt_service import MQTTService
from app.services.telemetry_service import TelemetryService
from app.services.device_service import DeviceService

# 全局服务实例
mqtt_service = None
telemetry_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global mqtt_service, telemetry_service
    
    # 启动时初始化
    logger.info("Starting IoT Backend System...")
    
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化遥测服务
    telemetry_service = TelemetryService()
    
    # 初始化MQTT服务（如果配置了）
    if settings.MQTT_BROKER_HOST:
        mqtt_service = MQTTService()
        
        # 注册消息处理器
        async def handle_telemetry(device_id: str, payload: dict):
            """处理遥测数据"""
            try:
                # 获取设备信息
                from app.db.session import AsyncSessionLocal
                async with AsyncSessionLocal() as db:
                    device_service = DeviceService(db)
                    device = await device_service.get_device(device_id)
                    
                    if device:
                        # 存储遥测数据
                        await telemetry_service.write_telemetry(
                            device_id,
                            device.device_type,
                            payload
                        )
                        
                        # 更新设备在线状态
                        await device_service.update_device_status(device_id, "online")
                        
                        logger.info(f"Stored telemetry from {device_id}")
            except Exception as e:
                logger.error(f"Error handling telemetry: {e}")
        
        mqtt_service.register_handler("telemetry", handle_telemetry)
        mqtt_service.connect()
    
    logger.info("IoT Backend System started successfully")
    
    yield
    
    # 关闭时清理
    logger.info("Shutting down IoT Backend System...")
    if mqtt_service:
        mqtt_service.disconnect()
    if telemetry_service:
        telemetry_service.close()
    await engine.dispose()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="IoT后端系统API接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```


### 阶段6：测试和部署 (预计30分钟)

#### 6.1 数据库迁移

创建 `scripts/init_db.py`：

```python
import asyncio
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

async def init_db():
    """初始化数据库"""
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建默认管理员用户
    async with AsyncSessionLocal() as session:
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrator",
            is_superuser=True
        )
        session.add(admin)
        await session.commit()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
```

运行初始化脚本：

```bash
python scripts/init_db.py
```

#### 6.2 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 6.3 API测试

使用HTTPie测试API：

```bash
# 1. 用户注册
http POST http://localhost:8000/api/v1/auth/register \
  username=testuser \
  email=test@example.com \
  password=test123 \
  full_name="Test User"

# 2. 用户登录
http -f POST http://localhost:8000/api/v1/auth/login \
  username=testuser \
  password=test123

# 保存返回的access_token
TOKEN="your-access-token-here"

# 3. 创建设备
http POST http://localhost:8000/api/v1/devices/ \
  "Authorization: Bearer $TOKEN" \
  name="温湿度传感器" \
  device_type="sensor" \
  product_key="product-001"

# 4. 获取设备列表
http GET http://localhost:8000/api/v1/devices/ \
  "Authorization: Bearer $TOKEN"

# 5. 获取设备详情
http GET http://localhost:8000/api/v1/devices/device-xxx \
  "Authorization: Bearer $TOKEN"

# 6. 查询设备数据
http GET http://localhost:8000/api/v1/telemetry/device-xxx/latest \
  "Authorization: Bearer $TOKEN" \
  limit==10
```

使用Postman测试：

1. 创建新的Collection
2. 添加环境变量：`base_url = http://localhost:8000`
3. 创建请求并测试各个接口
4. 使用Collection Runner批量测试

#### 6.4 Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY scripts/ ./scripts/

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

更新 `docker/docker-compose.yml` 添加API服务：

```yaml
  # API服务
  api:
    build: ..
    container_name: iot-api
    environment:
      DATABASE_URL: postgresql+asyncpg://iot_user:iot_password@postgres:5432/iot_platform
      REDIS_URL: redis://redis:6379/0
      INFLUXDB_URL: http://influxdb:8086
      INFLUXDB_TOKEN: my-super-secret-auth-token
      INFLUXDB_ORG: iot-org
      INFLUXDB_BUCKET: iot-data
      SECRET_KEY: your-secret-key-change-this
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - influxdb
    networks:
      - iot-network
    restart: unless-stopped
```

构建和启动：

```bash
cd docker
docker-compose up -d --build

# 查看日志
docker-compose logs -f api
```

## 完整代码

### 项目结构

```
iot-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── devices.py
│   │       │   └── telemetry.py
│   │       └── api.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── deps.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── device.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── device.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── device_service.py
│   │   ├── telemetry_service.py
│   │   └── mqtt_service.py
│   └── main.py
├── docker/
│   └── docker-compose.yml
├── scripts/
│   └── init_db.py
├── tests/
├── .env
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

### 代码仓库

完整代码可以在GitHub上找到：[仓库链接]

## 测试验证

### 功能测试清单

- [ ] 用户注册和登录
- [ ] JWT令牌验证
- [ ] 设备CRUD操作
- [ ] 设备权限控制
- [ ] 遥测数据写入
- [ ] 遥测数据查询
- [ ] 数据聚合查询
- [ ] MQTT消息处理（如果配置）

### 性能测试

使用Apache Bench进行压力测试：

```bash
# 测试登录接口
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/v1/auth/login

# 测试设备列表接口
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/devices/
```

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API响应时间 | <100ms | 95%请求 |
| 并发请求 | 100+ | 同时处理 |
| 数据写入 | 1000+/s | InfluxDB |
| 数据查询 | <200ms | 时序数据 |


## 故障排除

### 常见问题

#### 问题1：数据库连接失败

**症状**：应用启动时报错 "could not connect to server"

**可能原因**：
- PostgreSQL服务未启动
- 数据库连接配置错误
- 网络连接问题

**解决方法**：
1. 检查PostgreSQL服务状态
   ```bash
   docker-compose ps postgres
   ```
2. 验证数据库连接字符串
   ```bash
   # 测试连接
   psql postgresql://iot_user:iot_password@localhost:5432/iot_platform
   ```
3. 检查防火墙设置

#### 问题2：JWT令牌验证失败

**症状**：API请求返回401 Unauthorized

**可能原因**：
- 令牌已过期
- SECRET_KEY配置错误
- 令牌格式不正确

**解决方法**：
1. 重新登录获取新令牌
2. 检查.env文件中的SECRET_KEY配置
3. 确保请求头格式正确：`Authorization: Bearer <token>`

#### 问题3：InfluxDB写入失败

**症状**：遥测数据无法写入

**可能原因**：
- InfluxDB服务未启动
- Token配置错误
- Bucket不存在

**解决方法**：
1. 检查InfluxDB服务状态
   ```bash
   docker-compose ps influxdb
   ```
2. 验证Token和Bucket配置
   ```bash
   curl http://localhost:8086/health
   ```
3. 使用InfluxDB UI检查配置（http://localhost:8086）

#### 问题4：MQTT连接失败

**症状**：无法连接到MQTT Broker

**可能原因**：
- MQTT Broker未启动
- 连接配置错误
- 网络问题

**解决方法**：
1. 检查MQTT Broker状态
2. 使用MQTTX测试连接
3. 检查防火墙和端口配置

## 扩展思路

### 功能扩展

1. **设备影子**
   - 实现设备影子机制
   - 支持设备离线时的状态同步
   - 提供设备期望状态管理

2. **规则引擎**
   - 添加数据处理规则
   - 实现告警规则
   - 支持设备联动

3. **数据可视化**
   - 开发Web前端界面
   - 实时数据大屏
   - 历史数据图表

4. **设备分组**
   - 实现设备分组管理
   - 批量操作设备
   - 分组权限控制

5. **OTA升级**
   - 固件版本管理
   - 远程升级功能
   - 升级进度跟踪

### 性能优化

1. **缓存优化**
   - 使用Redis缓存热点数据
   - 实现查询结果缓存
   - 设备状态缓存

2. **数据库优化**
   - 添加合适的索引
   - 优化查询语句
   - 实现读写分离

3. **异步处理**
   - 使用消息队列处理耗时任务
   - 异步数据写入
   - 批量数据处理

4. **负载均衡**
   - 部署多个API实例
   - 使用Nginx负载均衡
   - 实现服务高可用

### 安全增强

1. **设备认证**
   - 实现设备证书认证
   - 支持设备密钥轮换
   - 设备黑白名单

2. **API安全**
   - 实现API限流
   - 添加请求签名验证
   - IP白名单

3. **数据加密**
   - 传输层加密（TLS/SSL）
   - 敏感数据加密存储
   - 数据脱敏

## 项目总结

### 技术要点

本项目涉及的关键技术：

1. **FastAPI框架**：异步Web框架，高性能API开发
2. **SQLAlchemy ORM**：数据库操作和模型管理
3. **JWT认证**：无状态的用户认证机制
4. **InfluxDB**：时序数据存储和查询
5. **MQTT协议**：设备消息通信
6. **Docker容器化**：应用部署和环境管理

### 学习收获

通过本项目，你应该掌握：

- ✅ IoT后端系统的完整架构设计
- ✅ RESTful API的设计和实现
- ✅ 异步编程和并发处理
- ✅ 数据库设计和优化
- ✅ 用户认证和权限控制
- ✅ 时序数据的存储和查询
- ✅ MQTT协议的应用
- ✅ Docker容器化部署

### 最佳实践

1. **代码组织**：模块化设计，职责分离
2. **错误处理**：统一的异常处理机制
3. **日志记录**：完善的日志系统
4. **API文档**：自动生成的API文档（FastAPI自带）
5. **配置管理**：环境变量和配置文件分离
6. **安全性**：密码加密、JWT认证、输入验证

## 相关资源

### 官方文档
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [InfluxDB文档](https://docs.influxdata.com/)
- [Paho MQTT文档](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)

### 学习资源
- [Python异步编程指南](https://docs.python.org/3/library/asyncio.html)
- [RESTful API设计最佳实践](https://restfulapi.net/)
- [JWT认证详解](https://jwt.io/introduction)
- [时序数据库原理](https://www.influxdata.com/time-series-database/)

### 开源项目
- [FastAPI示例项目](https://github.com/tiangolo/full-stack-fastapi-postgresql)
- [IoT平台参考实现](https://github.com/thingsboard/thingsboard)

## 下一步

完成本项目后，建议继续学习：

- [微服务架构设计](link) - 学习微服务拆分和治理
- [消息队列应用](link) - 深入学习异步消息处理
- [云原生应用开发](link) - 学习Kubernetes部署

## 参考资料

1. FastAPI官方文档 - Sebastián Ramírez
2. SQLAlchemy 2.0文档 - SQLAlchemy Team
3. InfluxDB 2.x文档 - InfluxData
4. 《Python异步编程》- Caleb Hattingh
5. 《RESTful Web APIs》- Leonard Richardson

---

**项目难度**：⭐⭐⭐⭐☆ (高级)  
**完成时间**：约4小时  
**技术栈**：Python, FastAPI, PostgreSQL, InfluxDB, Redis  
**适用场景**：IoT平台、数据采集系统、设备管理系统

**反馈与讨论**：欢迎在评论区分享你的项目成果和遇到的问题！如果你在实现过程中有任何疑问，可以参考完整代码仓库或在社区提问。
