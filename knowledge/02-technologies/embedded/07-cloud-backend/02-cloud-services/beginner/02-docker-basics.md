---
title: "Docker容器技术入门：从零开始学习容器化应用"
description: "全面介绍Docker容器技术的基本概念、核心功能和实践应用，包括Docker安装配置、镜像构建、容器运行、Docker Compose多容器编排以及应用部署的完整流程"
slug: "docker-basics-tutorial"

# 分类信息
domain: "云端与后台"
module: "云服务"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - Docker
  - 容器技术
  - 应用部署
  - 镜像构建
  - Docker Compose
prerequisites:
  - "cloud-computing-basics-guide"
related_contents: []

# 学习信息
estimated_time: 80
difficulty_score: 2

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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - Docker入门教程
  - 容器技术基础
  - Docker镜像构建
  - Docker Compose
  - 容器化部署
cover_image: ""
---

# Docker容器技术入门：从零开始学习容器化应用


## 学习目标

完成本教程后，你将能够：

- [ ] 理解Docker容器技术的基本概念和核心优势
- [ ] 在本地环境安装和配置Docker
- [ ] 掌握Docker镜像的拉取、构建和管理
- [ ] 熟练运行和管理Docker容器
- [ ] 使用Dockerfile构建自定义镜像
- [ ] 使用Docker Compose编排多容器应用
- [ ] 将实际应用容器化并部署

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解基本的Linux命令
- 熟悉命令行操作
- 了解基本的网络知识
- 了解云计算基础概念（建议先学习[云计算基础](../beginner/01-cloud-computing-basics.html)）

**技能要求**：
- 能够使用终端/命令行
- 会编写简单的配置文件
- 了解基本的应用部署流程

**硬件要求**：
- 64位操作系统（Windows 10/11、macOS、Linux）
- 至少4GB内存（推荐8GB）
- 至少20GB可用磁盘空间


## 概述

Docker是一个开源的容器化平台，它让开发者可以将应用及其依赖打包到一个轻量级、可移植的容器中，然后在任何支持Docker的环境中运行。

**为什么学习Docker？**

- **环境一致性**：开发、测试、生产环境完全一致
- **快速部署**：秒级启动，比虚拟机快得多
- **资源高效**：共享主机内核，资源占用少
- **易于扩展**：轻松实现应用的水平扩展
- **微服务架构**：容器是微服务的理想载体
- **DevOps实践**：CI/CD流程的重要组成部分

**Docker在物联网和嵌入式领域的应用**：
- 边缘计算节点的应用部署
- 物联网网关的服务容器化
- 开发环境的快速搭建
- 后端服务的容器化部署


## 什么是Docker

### Docker的核心概念

Docker使用容器技术来打包和运行应用。理解以下核心概念是学习Docker的基础：

#### 1. 容器 (Container)

容器是一个标准化的软件单元，它将代码及其所有依赖打包在一起，使应用能够快速可靠地在不同计算环境中运行。

**容器的特点**：
- 轻量级：共享主机操作系统内核
- 隔离性：每个容器独立运行，互不干扰
- 可移植性：在任何支持Docker的环境中运行
- 快速启动：秒级启动时间

**容器 vs 虚拟机**：

```
虚拟机架构：
┌─────────────────────────────────┐
│         应用A    应用B          │
│      ┌──────┐  ┌──────┐        │
│      │Guest │  │Guest │        │
│      │  OS  │  │  OS  │        │
│      └──────┘  └──────┘        │
│    ┌──────────────────┐        │
│    │   Hypervisor     │        │
│    └──────────────────┘        │
│    ┌──────────────────┐        │
│    │    Host OS       │        │
│    └──────────────────┘        │
│    ┌──────────────────┐        │
│    │   Infrastructure │        │
│    └──────────────────┘        │
└─────────────────────────────────┘

Docker容器架构：
┌─────────────────────────────────┐
│    应用A    应用B    应用C       │
│   ┌─────┐  ┌─────┐  ┌─────┐    │
│   │Bins/│  │Bins/│  │Bins/│    │
│   │Libs │  │Libs │  │Libs │    │
│   └─────┘  └─────┘  └─────┘    │
│    ┌──────────────────┐        │
│    │  Docker Engine   │        │
│    └──────────────────┘        │
│    ┌──────────────────┐        │
│    │    Host OS       │        │
│    └──────────────────┘        │
│    ┌──────────────────┐        │
│    │   Infrastructure │        │
│    └──────────────────┘        │
└─────────────────────────────────┘
```

| 特性 | 虚拟机 | Docker容器 |
|------|--------|-----------|
| 启动时间 | 分钟级 | 秒级 |
| 磁盘占用 | GB级 | MB级 |
| 性能 | 接近原生 | 原生性能 |
| 系统支持量 | 几十个 | 成百上千个 |
| 隔离性 | 完全隔离 | 进程级隔离 |


#### 2. 镜像 (Image)

镜像是一个只读的模板，包含了运行容器所需的所有内容：代码、运行时、库、环境变量和配置文件。

**镜像的特点**：
- 只读：镜像创建后不可修改
- 分层：由多个层组成，可以共享
- 可复用：一个镜像可以创建多个容器
- 版本化：通过标签(tag)管理不同版本

**镜像的分层结构**：

```
Docker镜像分层示例：
┌─────────────────────────────┐
│  应用层 (App Layer)         │  ← 你的应用代码
├─────────────────────────────┤
│  依赖层 (Dependencies)      │  ← npm install, pip install
├─────────────────────────────┤
│  运行时层 (Runtime)         │  ← Node.js, Python
├─────────────────────────────┤
│  基础层 (Base OS)           │  ← Ubuntu, Alpine
└─────────────────────────────┘

优势：
- 层可以被多个镜像共享
- 只需下载变化的层
- 节省存储空间
```

#### 3. 仓库 (Registry)

仓库是集中存储和分发镜像的地方。最常用的公共仓库是Docker Hub。

**常用仓库**：
- **Docker Hub**：官方公共仓库（https://hub.docker.com）
- **阿里云容器镜像服务**：国内镜像加速
- **腾讯云容器镜像服务**：国内镜像加速
- **私有仓库**：企业内部使用

#### 4. Dockerfile

Dockerfile是一个文本文件，包含了构建Docker镜像的所有指令。

**基本结构**：
```dockerfile
# 基础镜像
FROM ubuntu:20.04

# 维护者信息
LABEL maintainer="your-email@example.com"

# 安装软件
RUN apt-get update && apt-get install -y python3

# 设置工作目录
WORKDIR /app

# 复制文件
COPY . /app

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python3", "app.py"]
```

### Docker的工作原理

Docker使用客户端-服务器架构：

```
Docker架构：

┌──────────────┐
│ Docker Client│  ← 用户交互界面
│  (docker CLI)│
└──────┬───────┘
       │ REST API
       ↓
┌──────────────┐
│ Docker Daemon│  ← Docker引擎
│ (dockerd)    │
└──────┬───────┘
       │
       ├─→ 镜像管理
       ├─→ 容器管理
       ├─→ 网络管理
       └─→ 存储管理
```

**工作流程**：
1. 用户通过Docker CLI发送命令
2. Docker客户端通过REST API与Docker守护进程通信
3. Docker守护进程执行命令（拉取镜像、运行容器等）
4. 返回结果给客户端


## 准备工作

### 系统要求

**Windows**：
- Windows 10 64位：专业版、企业版或教育版（Build 19041或更高）
- 启用Hyper-V和容器功能
- WSL 2（Windows Subsystem for Linux 2）

**macOS**：
- macOS 10.15或更高版本
- 2010年或更新的Mac硬件

**Linux**：
- 64位系统
- 内核版本3.10或更高
- 支持的发行版：Ubuntu、Debian、CentOS、Fedora等

### 安装Docker

#### Windows安装

1. **下载Docker Desktop**
   - 访问 https://www.docker.com/products/docker-desktop
   - 下载Windows版本

2. **安装步骤**
   ```powershell
   # 1. 运行安装程序
   # 2. 按照向导完成安装
   # 3. 重启计算机
   
   # 4. 启动Docker Desktop
   # 5. 等待Docker启动完成
   ```

3. **验证安装**
   ```powershell
   # 打开PowerShell或CMD
   docker --version
   # 输出：Docker version 24.0.0, build xxx
   
   docker run hello-world
   # 如果看到 "Hello from Docker!" 说明安装成功
   ```

#### macOS安装

1. **下载Docker Desktop**
   - 访问 https://www.docker.com/products/docker-desktop
   - 根据芯片类型选择（Intel或Apple Silicon）

2. **安装步骤**
   ```bash
   # 1. 打开下载的.dmg文件
   # 2. 将Docker拖到Applications文件夹
   # 3. 启动Docker Desktop
   # 4. 授予必要的权限
   ```

3. **验证安装**
   ```bash
   docker --version
   docker run hello-world
   ```

#### Linux安装（以Ubuntu为例）

```bash
# 1. 更新软件包索引
sudo apt-get update

# 2. 安装必要的依赖
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. 验证安装
sudo docker --version
sudo docker run hello-world

# 7. 将当前用户添加到docker组（可选，避免每次使用sudo）
sudo usermod -aG docker $USER
# 注销并重新登录以使更改生效
```

### 配置镜像加速（国内用户推荐）

由于网络原因，国内拉取Docker Hub镜像可能很慢，建议配置镜像加速器。

#### 阿里云镜像加速

1. 登录阿里云容器镜像服务：https://cr.console.aliyun.com
2. 获取专属加速地址

**Docker Desktop配置**（Windows/macOS）：
```json
{
  "registry-mirrors": [
    "https://your-id.mirror.aliyuncs.com"
  ]
}
```

**Linux配置**：
```bash
# 创建或编辑daemon.json
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://your-id.mirror.aliyuncs.com"
  ]
}
EOF

# 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```


## 步骤1：Docker基本命令

### 1.1 查看Docker信息

```bash
# 查看Docker版本
docker --version
# 输出：Docker version 24.0.0, build xxx

# 查看详细信息
docker version
# 显示客户端和服务器版本信息

# 查看系统信息
docker info
# 显示容器数量、镜像数量、存储驱动等信息
```

### 1.2 镜像操作

#### 搜索镜像

```bash
# 在Docker Hub搜索镜像
docker search nginx
# 显示nginx相关的镜像列表

# 搜索官方镜像
docker search --filter "is-official=true" nginx
```

#### 拉取镜像

```bash
# 拉取最新版本
docker pull nginx
# 等同于 docker pull nginx:latest

# 拉取指定版本
docker pull nginx:1.21
docker pull ubuntu:20.04
docker pull python:3.9

# 拉取指定平台的镜像
docker pull --platform linux/amd64 nginx
```

#### 查看本地镜像

```bash
# 列出所有镜像
docker images
# 或
docker image ls

# 输出示例：
# REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
# nginx        latest    605c77e624dd   2 weeks ago    141MB
# ubuntu       20.04     ba6acccedd29   3 weeks ago    72.8MB
# python       3.9       a5d7930b60cc   4 weeks ago    917MB

# 查看镜像详细信息
docker image inspect nginx

# 查看镜像历史
docker history nginx
```

#### 删除镜像

```bash
# 删除指定镜像
docker rmi nginx:latest
# 或
docker image rm nginx:latest

# 删除多个镜像
docker rmi nginx ubuntu python

# 删除所有未使用的镜像
docker image prune

# 强制删除（即使有容器在使用）
docker rmi -f nginx
```

### 1.3 容器操作

#### 运行容器

```bash
# 基本运行
docker run nginx
# 前台运行，会占用终端

# 后台运行
docker run -d nginx
# 返回容器ID

# 指定容器名称
docker run -d --name my-nginx nginx

# 端口映射
docker run -d -p 8080:80 nginx
# 将容器的80端口映射到主机的8080端口

# 环境变量
docker run -d -e "ENV=production" nginx

# 挂载卷
docker run -d -v /host/path:/container/path nginx

# 完整示例
docker run -d \
  --name my-nginx \
  -p 8080:80 \
  -v $(pwd)/html:/usr/share/nginx/html \
  -e "NGINX_HOST=example.com" \
  nginx:latest
```

**常用参数说明**：
- `-d`: 后台运行（detached mode）
- `-p`: 端口映射 `主机端口:容器端口`
- `-v`: 挂载卷 `主机路径:容器路径`
- `-e`: 设置环境变量
- `--name`: 指定容器名称
- `--rm`: 容器停止后自动删除
- `-it`: 交互式终端

#### 查看容器

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 输出示例：
# CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                  NAMES
# abc123def456   nginx     "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp   my-nginx

# 查看容器详细信息
docker inspect my-nginx

# 查看容器日志
docker logs my-nginx

# 实时查看日志
docker logs -f my-nginx

# 查看最近100行日志
docker logs --tail 100 my-nginx
```

#### 管理容器

```bash
# 停止容器
docker stop my-nginx

# 启动已停止的容器
docker start my-nginx

# 重启容器
docker restart my-nginx

# 暂停容器
docker pause my-nginx

# 恢复容器
docker unpause my-nginx

# 删除容器
docker rm my-nginx

# 强制删除运行中的容器
docker rm -f my-nginx

# 删除所有已停止的容器
docker container prune
```

#### 进入容器

```bash
# 执行命令
docker exec my-nginx ls /usr/share/nginx/html

# 进入容器的交互式终端
docker exec -it my-nginx bash
# 或
docker exec -it my-nginx sh

# 在容器中执行多个命令
docker exec -it my-nginx bash -c "cd /app && ls -la"
```

### 1.4 实践练习：运行第一个Web服务

让我们运行一个Nginx Web服务器：

```bash
# 1. 拉取nginx镜像
docker pull nginx

# 2. 创建一个HTML文件
mkdir -p ~/docker-demo/html
echo "<h1>Hello Docker!</h1>" > ~/docker-demo/html/index.html

# 3. 运行nginx容器
docker run -d \
  --name my-web \
  -p 8080:80 \
  -v ~/docker-demo/html:/usr/share/nginx/html:ro \
  nginx

# 4. 查看容器状态
docker ps

# 5. 访问Web服务
# 在浏览器打开 http://localhost:8080
# 或使用curl
curl http://localhost:8080

# 6. 查看日志
docker logs my-web

# 7. 停止并删除容器
docker stop my-web
docker rm my-web
```

**预期结果**：
- 浏览器显示 "Hello Docker!"
- 日志显示访问记录


## 步骤2：构建自定义镜像

### 2.1 创建Dockerfile

Dockerfile是构建镜像的配置文件。让我们创建一个简单的Python Web应用。

#### 创建项目目录

```bash
mkdir -p ~/docker-demo/python-app
cd ~/docker-demo/python-app
```

#### 创建应用代码

创建 `app.py`：

```python
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return f"""
    <h1>Hello from Docker!</h1>
    <p>Hostname: {os.environ.get('HOSTNAME', 'unknown')}</p>
    <p>Environment: {os.environ.get('ENV', 'development')}</p>
    """

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

创建 `requirements.txt`：

```
Flask==2.3.0
```

### 2.2 编写Dockerfile

创建 `Dockerfile`：

```dockerfile
# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV ENV=production

# 运行应用
CMD ["python", "app.py"]
```

**Dockerfile指令说明**：

| 指令 | 说明 | 示例 |
|------|------|------|
| FROM | 指定基础镜像 | FROM python:3.9 |
| WORKDIR | 设置工作目录 | WORKDIR /app |
| COPY | 复制文件到镜像 | COPY . /app |
| ADD | 复制文件（支持URL和解压） | ADD file.tar.gz /app |
| RUN | 执行命令 | RUN apt-get update |
| ENV | 设置环境变量 | ENV PORT=8080 |
| EXPOSE | 声明端口 | EXPOSE 8080 |
| CMD | 容器启动命令 | CMD ["python", "app.py"] |
| ENTRYPOINT | 容器入口点 | ENTRYPOINT ["python"] |
| VOLUME | 定义挂载点 | VOLUME /data |
| USER | 指定用户 | USER appuser |
| ARG | 构建参数 | ARG VERSION=1.0 |

### 2.3 构建镜像

```bash
# 构建镜像
docker build -t my-python-app:1.0 .

# 参数说明：
# -t: 指定镜像名称和标签
# .: 指定Dockerfile所在目录（当前目录）

# 查看构建过程
docker build -t my-python-app:1.0 . --progress=plain

# 不使用缓存构建
docker build -t my-python-app:1.0 . --no-cache

# 指定Dockerfile
docker build -t my-python-app:1.0 -f Dockerfile.prod .
```

**构建过程**：
```
[+] Building 15.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.9-slim
 => [1/5] FROM docker.io/library/python:3.9-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY app.py .
 => exporting to image
 => => writing image sha256:abc123...
 => => naming to docker.io/library/my-python-app:1.0
```

### 2.4 运行自定义镜像

```bash
# 运行容器
docker run -d \
  --name my-app \
  -p 5000:5000 \
  -e ENV=production \
  my-python-app:1.0

# 测试应用
curl http://localhost:5000
curl http://localhost:5000/health

# 查看日志
docker logs my-app
```

### 2.5 优化Dockerfile

#### 多阶段构建

对于需要编译的应用，使用多阶段构建可以减小镜像大小：

```dockerfile
# 构建阶段
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 最佳实践

```dockerfile
# 1. 使用轻量级基础镜像
FROM python:3.9-slim  # 而不是 python:3.9

# 2. 合并RUN命令减少层数
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 利用构建缓存，先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # 代码变化不会导致重新安装依赖

# 4. 使用.dockerignore排除不需要的文件
# 创建.dockerignore文件：
# __pycache__
# *.pyc
# .git
# .env

# 5. 不要以root用户运行
RUN useradd -m appuser
USER appuser

# 6. 使用LABEL添加元数据
LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="My Python App"
```


## 步骤3：Docker网络

### 3.1 网络模式

Docker支持多种网络模式：

```bash
# 查看网络列表
docker network ls

# 输出示例：
# NETWORK ID     NAME      DRIVER    SCOPE
# abc123def456   bridge    bridge    local
# def456ghi789   host      host      local
# ghi789jkl012   none      null      local
```

**网络模式说明**：

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| bridge | 默认模式，容器有独立IP | 单机多容器通信 |
| host | 容器使用主机网络 | 需要高性能网络 |
| none | 无网络 | 完全隔离的容器 |
| container | 共享其他容器的网络 | 容器间紧密协作 |
| 自定义网络 | 用户自定义的网络 | 复杂的网络拓扑 |

### 3.2 创建自定义网络

```bash
# 创建bridge网络
docker network create my-network

# 创建指定子网的网络
docker network create \
  --driver bridge \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  my-custom-network

# 查看网络详情
docker network inspect my-network

# 删除网络
docker network rm my-network
```

### 3.3 容器网络连接

```bash
# 运行容器并连接到网络
docker run -d \
  --name app1 \
  --network my-network \
  nginx

# 将已有容器连接到网络
docker network connect my-network app2

# 断开网络连接
docker network disconnect my-network app2

# 容器间通信示例
docker run -d --name db --network my-network postgres
docker run -d --name web --network my-network nginx
# web容器可以通过 "db" 这个主机名访问数据库
```

### 3.4 端口映射

```bash
# 映射单个端口
docker run -d -p 8080:80 nginx

# 映射多个端口
docker run -d -p 8080:80 -p 8443:443 nginx

# 映射到随机端口
docker run -d -p 80 nginx

# 查看端口映射
docker port my-nginx

# 绑定到特定IP
docker run -d -p 127.0.0.1:8080:80 nginx
```


## 步骤4：Docker数据管理

### 4.1 数据卷 (Volumes)

数据卷是Docker推荐的数据持久化方式。

```bash
# 创建数据卷
docker volume create my-data

# 查看数据卷列表
docker volume ls

# 查看数据卷详情
docker volume inspect my-data

# 使用数据卷
docker run -d \
  --name db \
  -v my-data:/var/lib/postgresql/data \
  postgres

# 删除数据卷
docker volume rm my-data

# 删除所有未使用的数据卷
docker volume prune
```

### 4.2 绑定挂载 (Bind Mounts)

直接挂载主机目录到容器。

```bash
# Linux/macOS
docker run -d \
  -v /host/path:/container/path \
  nginx

# Windows (PowerShell)
docker run -d \
  -v C:\host\path:/container/path \
  nginx

# 只读挂载
docker run -d \
  -v /host/path:/container/path:ro \
  nginx
```

### 4.3 数据备份和恢复

```bash
# 备份数据卷
docker run --rm \
  -v my-data:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar czf /backup/backup.tar.gz /data

# 恢复数据卷
docker run --rm \
  -v my-data:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar xzf /backup/backup.tar.gz -C /
```


## 步骤5：Docker Compose

Docker Compose是用于定义和运行多容器Docker应用的工具。

### 5.1 安装Docker Compose

Docker Desktop已包含Docker Compose。Linux用户需要单独安装：

```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 5.2 创建docker-compose.yml

创建一个完整的Web应用栈（Web + 数据库 + Redis）：

```yaml
version: '3.8'

services:
  # Web应用
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app
    networks:
      - app-network

  # PostgreSQL数据库
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    networks:
      - app-network

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web
    networks:
      - app-network

volumes:
  db-data:

networks:
  app-network:
    driver: bridge
```

### 5.3 Docker Compose命令

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs

# 查看特定服务的日志
docker-compose logs web

# 实时查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、数据卷
docker-compose down -v

# 重启服务
docker-compose restart

# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up --build

# 扩展服务实例
docker-compose up -d --scale web=3

# 执行命令
docker-compose exec web bash

# 查看配置
docker-compose config
```

### 5.4 实践项目：完整的Web应用

让我们创建一个完整的Flask + PostgreSQL + Redis应用。

#### 项目结构

```
my-web-app/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app.py
└── nginx.conf
```

#### app.py

```python
from flask import Flask, jsonify
import psycopg2
import redis
import os

app = Flask(__name__)

# 数据库连接
def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

# Redis连接
redis_client = redis.from_url(os.environ['REDIS_URL'])

@app.route('/')
def index():
    # 增加访问计数
    count = redis_client.incr('visit_count')
    return jsonify({
        'message': 'Hello from Docker Compose!',
        'visit_count': count
    })

@app.route('/db-test')
def db_test():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({'database_version': version[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### requirements.txt

```
Flask==2.3.0
psycopg2-binary==2.9.6
redis==4.5.5
```

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### 运行应用

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 测试应用
curl http://localhost:5000
curl http://localhost:5000/db-test

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down
```


## 步骤6：实际应用部署

### 6.1 部署Node.js应用

#### 项目结构

```
node-app/
├── Dockerfile
├── docker-compose.yml
├── package.json
└── server.js
```

#### server.js

```javascript
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({
    message: 'Hello from Node.js in Docker!',
    environment: process.env.NODE_ENV,
    timestamp: new Date().toISOString()
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

#### package.json

```json
{
  "name": "node-docker-app",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

#### Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY server.js .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

### 6.2 部署物联网后端服务

一个典型的物联网后端服务架构：

```yaml
version: '3.8'

services:
  # MQTT Broker
  mqtt:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mqtt-data:/mosquitto/data
    networks:
      - iot-network

  # 时序数据库
  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password123
      - DOCKER_INFLUXDB_INIT_ORG=myorg
      - DOCKER_INFLUXDB_INIT_BUCKET=iot-data
    volumes:
      - influxdb-data:/var/lib/influxdb2
    networks:
      - iot-network

  # 数据处理服务
  processor:
    build: ./processor
    environment:
      - MQTT_BROKER=mqtt://mqtt:1883
      - INFLUXDB_URL=http://influxdb:8086
    depends_on:
      - mqtt
      - influxdb
    networks:
      - iot-network

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - influxdb
    networks:
      - iot-network

volumes:
  mqtt-data:
  influxdb-data:
  grafana-data:

networks:
  iot-network:
    driver: bridge
```


## 故障排除

### 问题1：容器无法启动

**现象**：
```bash
docker run nginx
# Error response from daemon: driver failed programming external connectivity
```

**可能原因**：
1. 端口已被占用
2. 防火墙阻止
3. Docker服务未正常运行

**解决方法**：

```bash
# 1. 检查端口占用
# Linux/macOS
sudo lsof -i :8080
# Windows
netstat -ano | findstr :8080

# 2. 更换端口
docker run -d -p 8081:80 nginx

# 3. 检查Docker服务
# Linux
sudo systemctl status docker
# Windows/macOS
# 检查Docker Desktop是否运行

# 4. 重启Docker服务
# Linux
sudo systemctl restart docker
# Windows/macOS
# 重启Docker Desktop
```

### 问题2：镜像拉取失败

**现象**：
```bash
docker pull nginx
# Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: TLS handshake timeout
```

**可能原因**：
1. 网络连接问题
2. Docker Hub访问受限
3. 镜像名称错误

**解决方法**：

```bash
# 1. 配置镜像加速器（见前面的配置部分）

# 2. 使用代理
# 在Docker Desktop设置中配置HTTP代理

# 3. 检查镜像名称
docker search nginx  # 确认镜像名称正确

# 4. 手动指定registry
docker pull docker.io/library/nginx:latest
```

### 问题3：容器内无法访问网络

**现象**：
容器内ping不通外网，无法下载软件包

**解决方法**：

```bash
# 1. 检查DNS配置
docker run --rm alpine ping -c 3 google.com

# 2. 指定DNS服务器
docker run --dns 8.8.8.8 --dns 8.8.4.4 alpine ping google.com

# 3. 修改Docker daemon配置
# 编辑 /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

# 重启Docker
sudo systemctl restart docker
```

### 问题4：磁盘空间不足

**现象**：
```bash
docker build -t myapp .
# no space left on device
```

**解决方法**：

```bash
# 1. 查看磁盘使用情况
docker system df

# 2. 清理未使用的资源
docker system prune

# 3. 清理所有未使用的资源（包括未使用的镜像）
docker system prune -a

# 4. 清理特定资源
docker container prune  # 清理容器
docker image prune      # 清理镜像
docker volume prune     # 清理数据卷
docker network prune    # 清理网络

# 5. 查看详细的空间使用
docker system df -v
```

### 问题5：容器性能问题

**现象**：
容器运行缓慢，响应时间长

**解决方法**：

```bash
# 1. 查看容器资源使用
docker stats

# 2. 限制容器资源
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  nginx

# 3. 查看容器进程
docker top my-container

# 4. 检查日志是否有错误
docker logs my-container

# 5. 进入容器检查
docker exec -it my-container bash
top  # 查看进程
df -h  # 查看磁盘
free -m  # 查看内存
```

### 问题6：Docker Compose服务无法通信

**现象**：
Web服务无法连接到数据库

**解决方法**：

```bash
# 1. 检查服务是否在同一网络
docker-compose ps
docker network ls

# 2. 检查服务名称
# 使用服务名作为主机名，而不是localhost
# 正确：postgresql://db:5432
# 错误：postgresql://localhost:5432

# 3. 检查depends_on配置
# 确保依赖关系正确

# 4. 查看网络配置
docker network inspect myapp_default

# 5. 测试网络连通性
docker-compose exec web ping db
```


## 最佳实践

### 1. 镜像构建最佳实践

```dockerfile
# ✅ 好的做法
FROM python:3.9-slim  # 使用轻量级镜像

# 合并RUN命令减少层数
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 利用缓存，先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# 使用非root用户
RUN useradd -m appuser
USER appuser

# ❌ 不好的做法
FROM python:3.9  # 镜像太大

# 每个命令一层
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get clean

# 先复制所有文件
COPY . .
RUN pip install -r requirements.txt  # 代码变化会导致重新安装依赖

# 使用root用户运行
```

### 2. 安全最佳实践

```dockerfile
# 1. 使用官方镜像
FROM python:3.9-slim  # 官方维护，及时更新

# 2. 扫描镜像漏洞
# docker scan my-image

# 3. 不要在镜像中存储敏感信息
# 使用环境变量或secrets
ENV DATABASE_URL=${DATABASE_URL}

# 4. 使用非root用户
USER appuser

# 5. 只暴露必要的端口
EXPOSE 8080

# 6. 使用只读文件系统（如果可能）
# docker run --read-only my-image
```

### 3. 性能优化

```dockerfile
# 1. 使用多阶段构建
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# 2. 使用.dockerignore
# .dockerignore内容：
# node_modules
# .git
# *.log
# .env

# 3. 优化层缓存
# 将不常变化的命令放在前面
COPY package*.json ./
RUN npm install
COPY . .  # 代码变化不影响依赖安装
```

### 4. 日志管理

```bash
# 1. 限制日志大小
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx

# 2. 使用日志驱动
docker run -d \
  --log-driver syslog \
  --log-opt syslog-address=tcp://192.168.0.42:123 \
  nginx

# 3. 在docker-compose中配置
services:
  web:
    image: nginx
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 健康检查

```dockerfile
# Dockerfile中添加健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

```yaml
# docker-compose.yml中配置
services:
  web:
    image: myapp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```


## 总结

通过本教程，你已经学习了Docker容器技术的核心内容：

### 核心要点回顾

**Docker基础概念**：
- ✅ 容器：轻量级、隔离的运行环境
- ✅ 镜像：只读的应用模板
- ✅ 仓库：镜像的存储和分发中心
- ✅ Dockerfile：构建镜像的配置文件

**基本操作**：
- ✅ 镜像管理：pull、build、push、rm
- ✅ 容器管理：run、start、stop、rm、exec
- ✅ 网络管理：创建网络、连接容器
- ✅ 数据管理：volumes、bind mounts

**高级功能**：
- ✅ Dockerfile：构建自定义镜像
- ✅ Docker Compose：多容器应用编排
- ✅ 网络配置：容器间通信
- ✅ 数据持久化：数据卷管理

**最佳实践**：
- ✅ 使用轻量级基础镜像
- ✅ 优化镜像层和缓存
- ✅ 使用非root用户
- ✅ 配置健康检查
- ✅ 管理日志和资源

### 实践成果

完成本教程后，你应该能够：
1. 在本地环境运行Docker容器
2. 构建自定义Docker镜像
3. 使用Docker Compose编排多容器应用
4. 将实际应用容器化并部署
5. 解决常见的Docker问题

### 下一步学习建议

1. **深入学习**
   - Kubernetes容器编排
   - Docker Swarm集群
   - 容器安全加固
   - 微服务架构

2. **实践项目**
   - 容器化现有应用
   - 构建CI/CD流程
   - 部署微服务应用
   - 搭建开发环境

3. **进阶主题**
   - 容器监控和日志
   - 服务网格（Service Mesh）
   - 无服务器容器（Fargate）
   - 边缘计算容器


## 进阶挑战

尝试以下挑战来巩固学习：

### 挑战1：容器化一个完整的Web应用（60分钟）

**任务**：
1. 创建一个包含前端、后端、数据库的完整应用
2. 编写Dockerfile和docker-compose.yml
3. 实现数据持久化
4. 配置健康检查
5. 实现零停机更新

**提示**：
- 使用React/Vue作为前端
- 使用Node.js/Python作为后端
- 使用PostgreSQL/MySQL作为数据库
- 使用Nginx作为反向代理

### 挑战2：优化镜像大小（30分钟）

**任务**：
1. 构建一个Node.js应用镜像
2. 记录初始镜像大小
3. 使用多阶段构建优化
4. 使用Alpine基础镜像
5. 对比优化前后的大小

**目标**：
- 将镜像大小减少50%以上

### 挑战3：搭建物联网数据采集系统（90分钟）

**任务**：
1. 使用MQTT Broker接收设备数据
2. 使用InfluxDB存储时序数据
3. 使用Grafana可视化数据
4. 编写数据处理服务
5. 使用Docker Compose编排所有服务

**要求**：
- 所有服务容器化
- 数据持久化
- 服务间正确通信
- 提供监控和日志


## 常见问题

### Q1: Docker和虚拟机有什么区别？

**A**: 主要区别：

| 特性 | Docker | 虚拟机 |
|------|--------|--------|
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | 低（MB级） | 高（GB级） |
| 性能 | 接近原生 | 有损耗 |
| 隔离性 | 进程级 | 系统级 |
| 可移植性 | 高 | 中 |

Docker更轻量、更快，但隔离性不如虚拟机。

### Q2: 容器停止后数据会丢失吗？

**A**: 取决于数据存储方式：

- **容器内数据**：会丢失
- **数据卷(Volume)**：不会丢失
- **绑定挂载(Bind Mount)**：不会丢失

建议使用数据卷存储重要数据：
```bash
docker run -v my-data:/data myapp
```

### Q3: 如何在容器间共享数据？

**A**: 有几种方法：

1. **使用数据卷**：
```bash
docker volume create shared-data
docker run -v shared-data:/data app1
docker run -v shared-data:/data app2
```

2. **使用绑定挂载**：
```bash
docker run -v /host/shared:/data app1
docker run -v /host/shared:/data app2
```

3. **使用volumes-from**：
```bash
docker run --name data-container -v /data busybox
docker run --volumes-from data-container app1
```

### Q4: Docker适合生产环境吗？

**A**: 完全适合！很多大公司在生产环境使用Docker：

**优势**：
- 环境一致性
- 快速部署
- 易于扩展
- 资源高效

**注意事项**：
- 使用编排工具（Kubernetes、Docker Swarm）
- 配置监控和日志
- 实施安全措施
- 做好备份和灾备

### Q5: 如何选择基础镜像？

**A**: 选择建议：

1. **优先使用官方镜像**
   - 维护良好
   - 安全更新及时
   - 文档完善

2. **选择合适的变体**
   - `alpine`: 最小（5MB），适合生产
   - `slim`: 较小（100MB），功能完整
   - `标准版`: 最大（1GB），包含所有工具

3. **考虑因素**
   - 镜像大小
   - 安全性
   - 兼容性
   - 维护状态

示例：
```dockerfile
# 开发环境
FROM python:3.9

# 生产环境
FROM python:3.9-slim

# 极致优化
FROM python:3.9-alpine
```

### Q6: 容器如何访问主机服务？

**A**: 使用特殊的主机名：

**Linux**：
```bash
# 使用host.docker.internal
docker run -e DB_HOST=host.docker.internal myapp
```

**Windows/macOS**：
```bash
# Docker Desktop自动支持
docker run -e DB_HOST=host.docker.internal myapp
```

**或使用host网络模式**：
```bash
docker run --network host myapp
```


## 延伸阅读

### 推荐资源

**官方文档**：
- [Docker官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)

**在线教程**：
- [Docker官方教程](https://www.docker.com/101-tutorial)
- [Play with Docker](https://labs.play-with-docker.com/) - 在线实验环境

**书籍推荐**：
- 《Docker实战》- Sean P. Kane, Karl Matthias
- 《Docker容器与容器云》- 浙江大学SEL实验室
- 《深入浅出Docker》- Nigel Poulton

**视频课程**：
- Docker官方YouTube频道
- Udemy Docker课程
- B站Docker教程

### 相关技术

**容器编排**：
- Kubernetes - 最流行的容器编排平台
- Docker Swarm - Docker原生编排工具
- Nomad - HashiCorp的编排工具

**CI/CD工具**：
- Jenkins - 持续集成
- GitLab CI/CD - 代码管理和部署
- GitHub Actions - 自动化工作流

**监控工具**：
- Prometheus - 监控系统
- Grafana - 数据可视化
- ELK Stack - 日志分析

**镜像仓库**：
- Harbor - 企业级镜像仓库
- Nexus - 制品仓库
- JFrog Artifactory - 通用仓库


## 参考资料

1. Docker官方文档 - https://docs.docker.com/
2. Docker最佳实践 - https://docs.docker.com/develop/dev-best-practices/
3. Dockerfile参考 - https://docs.docker.com/engine/reference/builder/
4. Docker Compose文件参考 - https://docs.docker.com/compose/compose-file/
5. Docker安全最佳实践 - https://docs.docker.com/engine/security/

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 发现文档错误或有改进建议，请提交Issue
- 想要分享你的Docker实践经验，欢迎投稿

**下一步学习**：
- [Kubernetes容器编排](../intermediate/01-kubernetes.html) - 学习K8s集群管理
- [Serverless无服务器架构](../intermediate/02-serverless.html) - 学习函数计算
- [云原生应用开发](../advanced/01-cloud-native-app.html) - 构建云原生应用
- [微服务架构设计](../../01-backend-development/intermediate/01-microservices.html) - 学习微服务

---

**版权声明**：
本文采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
