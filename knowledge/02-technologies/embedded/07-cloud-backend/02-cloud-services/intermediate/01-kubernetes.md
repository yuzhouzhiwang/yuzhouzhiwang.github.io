---
title: "Kubernetes容器编排实战：从入门到部署完整应用"
description: "深入学习Kubernetes容器编排平台，掌握K8s架构、Pod管理、Service服务、Deployment部署、集群管理等核心概念，通过实践项目学会在生产环境中部署和管理容器化应用"
slug: "kubernetes-container-orchestration"

# 分类信息
domain: "云端与后台"
module: "云服务"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Kubernetes
  - K8s
  - 容器编排
  - 集群管理
  - 微服务部署
prerequisites:
  - "docker-basics-tutorial"
  - "cloud-computing-basics-guide"
related_contents:
  - "microservices-architecture"
  - "cloud-native-app-development"

# 学习信息
estimated_time: 100
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
status: "published"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - Kubernetes教程
  - K8s入门
  - 容器编排
  - Pod管理
  - Kubernetes部署
cover_image: ""
---

# Kubernetes容器编排实战：从入门到部署完整应用


## 学习目标

完成本教程后，你将能够：

- [ ] 理解Kubernetes的核心架构和设计理念
- [ ] 掌握Kubernetes集群的安装和配置
- [ ] 熟练使用kubectl命令行工具
- [ ] 创建和管理Pod、Deployment、Service等核心资源
- [ ] 理解Kubernetes的网络和存储机制
- [ ] 使用ConfigMap和Secret管理配置
- [ ] 实现应用的滚动更新和回滚
- [ ] 配置自动扩缩容和健康检查
- [ ] 部署完整的微服务应用到K8s集群

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉Docker容器技术（必须先学习[Docker容器技术入门](../beginner/02-docker-basics.html)）
- 了解Linux基本命令
- 理解基本的网络概念
- 了解YAML配置文件格式

**技能要求**：
- 能够使用命令行工具
- 会编写Dockerfile
- 了解容器化应用的基本概念
- 熟悉基本的应用部署流程

**硬件要求**：
- 64位操作系统（Linux、macOS、Windows）
- 至少8GB内存（推荐16GB）
- 至少40GB可用磁盘空间
- 支持虚拟化的CPU


## 概述

Kubernetes（简称K8s）是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。它最初由Google设计，现在由Cloud Native Computing Foundation（CNCF）维护。

**为什么需要Kubernetes？**

当你有大量容器需要管理时，手动操作Docker会变得非常困难：
- 如何在多台服务器上部署容器？
- 如何实现负载均衡和服务发现？
- 如何处理容器故障和自动恢复？
- 如何实现零停机更新？
- 如何管理配置和密钥？

Kubernetes解决了这些问题，提供了：
- **自动化部署和回滚**：声明式配置，自动管理应用状态
- **服务发现和负载均衡**：自动分配IP和DNS，内置负载均衡
- **存储编排**：自动挂载存储系统
- **自我修复**：自动重启失败的容器，替换和重新调度
- **密钥和配置管理**：安全地存储和管理敏感信息
- **水平扩展**：通过命令或自动扩展应用

**Kubernetes在物联网和嵌入式领域的应用**：
- 边缘计算节点的应用编排
- 物联网平台的微服务部署
- 数据处理管道的自动化管理
- 多租户物联网应用的隔离和管理


## 什么是Kubernetes

### Kubernetes核心概念

#### 1. 集群架构

Kubernetes集群由控制平面（Control Plane）和工作节点（Worker Nodes）组成：

```
Kubernetes集群架构：

┌─────────────────────────────────────────────────────────┐
│                    Control Plane                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ API Server   │  │  Scheduler   │  │  Controller  │ │
│  │              │  │              │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────────────────────────────────────────┐  │
│  │              etcd (集群数据存储)                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
│  Worker Node 1 │  │  Worker Node 2 │  │  Worker Node 3 │
│  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │
│  │ kubelet  │  │  │  │ kubelet  │  │  │  │ kubelet  │  │
│  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │
│  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │
│  │kube-proxy│  │  │  │kube-proxy│  │  │  │kube-proxy│  │
│  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │
│  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │
│  │Container │  │  │  │Container │  │  │  │Container │  │
│  │ Runtime  │  │  │  │ Runtime  │  │  │  │ Runtime  │  │
│  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │
│  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │
│  │  Pods    │  │  │  │  Pods    │  │  │  │  Pods    │  │
│  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │
└────────────────┘  └────────────────┘  └────────────────┘
```

**控制平面组件**：
- **API Server**：集群的前端，所有操作都通过它
- **etcd**：分布式键值存储，保存集群所有数据
- **Scheduler**：负责将Pod调度到合适的节点
- **Controller Manager**：运行控制器进程，维护集群状态

**工作节点组件**：
- **kubelet**：节点代理，确保容器在Pod中运行
- **kube-proxy**：网络代理，维护网络规则
- **Container Runtime**：容器运行时（Docker、containerd等）


#### 2. 核心资源对象

**Pod**：
- Kubernetes中最小的部署单元
- 包含一个或多个容器
- 共享网络和存储
- 同一Pod中的容器总是被调度到同一节点

```
Pod结构：
┌─────────────────────────────┐
│          Pod                │
│  ┌─────────┐  ┌─────────┐  │
│  │Container│  │Container│  │
│  │   A     │  │   B     │  │
│  └─────────┘  └─────────┘  │
│  ┌─────────────────────┐   │
│  │  Shared Network     │   │
│  │  (localhost)        │   │
│  └─────────────────────┘   │
│  ┌─────────────────────┐   │
│  │  Shared Volumes     │   │
│  └─────────────────────┘   │
└─────────────────────────────┘
```

**Deployment**：
- 管理Pod的副本数量
- 支持滚动更新和回滚
- 确保指定数量的Pod始终运行

**Service**：
- 为Pod提供稳定的网络端点
- 实现负载均衡
- 服务发现

**ConfigMap和Secret**：
- ConfigMap：存储非敏感配置
- Secret：存储敏感信息（密码、密钥等）

**Namespace**：
- 虚拟集群，用于资源隔离
- 多租户环境的逻辑分组

#### 3. Kubernetes工作流程

```
应用部署流程：

1. 用户提交配置
   kubectl apply -f deployment.yaml
          │
          ▼
2. API Server接收请求
   验证和存储到etcd
          │
          ▼
3. Controller Manager检测到新的Deployment
   创建ReplicaSet
          │
          ▼
4. Scheduler选择合适的节点
   将Pod调度到节点
          │
          ▼
5. kubelet在节点上创建容器
   启动应用
          │
          ▼
6. kube-proxy配置网络规则
   实现服务访问
```


## 准备工作

### 系统要求

**开发环境**（单节点集群）：
- CPU：2核心或更多
- 内存：4GB或更多
- 磁盘：20GB可用空间

**生产环境**（多节点集群）：
- 控制平面：4核心、8GB内存
- 工作节点：2核心、4GB内存（每个节点）
- 网络：节点间可以互相通信

### 安装Kubernetes

我们将介绍几种常用的安装方式：

#### 方式1：Minikube（推荐用于学习）

Minikube在本地运行单节点Kubernetes集群，非常适合学习和开发。

**安装Minikube**：

```bash
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Windows (使用PowerShell管理员权限)
choco install minikube
```

**启动Minikube**：

```bash
# 启动集群
minikube start

# 指定资源
minikube start --cpus=4 --memory=8192

# 指定容器运行时
minikube start --driver=docker

# 查看状态
minikube status

# 停止集群
minikube stop

# 删除集群
minikube delete
```

#### 方式2：Kind（Kubernetes in Docker）

Kind在Docker容器中运行Kubernetes集群，轻量且快速。

```bash
# 安装Kind
# Linux/macOS
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# 创建集群
kind create cluster

# 创建多节点集群
kind create cluster --config kind-config.yaml

# 删除集群
kind delete cluster
```

**kind-config.yaml示例**：
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```

#### 方式3：Docker Desktop（Windows/macOS）

Docker Desktop内置Kubernetes支持：

1. 打开Docker Desktop设置
2. 进入Kubernetes选项卡
3. 勾选"Enable Kubernetes"
4. 点击"Apply & Restart"

### 安装kubectl

kubectl是Kubernetes的命令行工具。

```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS
brew install kubectl

# Windows (PowerShell管理员权限)
choco install kubernetes-cli

# 验证安装
kubectl version --client

# 查看集群信息
kubectl cluster-info

# 查看节点
kubectl get nodes
```

### 配置kubectl自动补全

```bash
# Bash
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'alias k=kubectl' >>~/.bashrc
echo 'complete -o default -F __start_kubectl k' >>~/.bashrc

# Zsh
echo 'source <(kubectl completion zsh)' >>~/.zshrc
echo 'alias k=kubectl' >>~/.zshrc
```


## 步骤1：kubectl基本命令

### 1.1 查看集群信息

```bash
# 查看集群信息
kubectl cluster-info

# 查看节点
kubectl get nodes

# 查看节点详细信息
kubectl describe node <node-name>

# 查看所有命名空间
kubectl get namespaces

# 查看当前上下文
kubectl config current-context

# 查看所有上下文
kubectl config get-contexts
```

### 1.2 资源操作命令

```bash
# 查看资源（get）
kubectl get pods                    # 查看Pod
kubectl get deployments             # 查看Deployment
kubectl get services                # 查看Service
kubectl get all                     # 查看所有资源

# 查看详细信息（describe）
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>

# 查看日志（logs）
kubectl logs <pod-name>
kubectl logs <pod-name> -f          # 实时查看
kubectl logs <pod-name> -c <container-name>  # 多容器Pod

# 执行命令（exec）
kubectl exec <pod-name> -- ls /app
kubectl exec -it <pod-name> -- bash  # 进入容器

# 端口转发（port-forward）
kubectl port-forward <pod-name> 8080:80

# 删除资源（delete）
kubectl delete pod <pod-name>
kubectl delete deployment <deployment-name>
kubectl delete -f deployment.yaml
```

### 1.3 常用选项

```bash
# 指定命名空间
kubectl get pods -n kube-system

# 查看所有命名空间
kubectl get pods --all-namespaces
kubectl get pods -A

# 输出格式
kubectl get pods -o wide           # 更多信息
kubectl get pods -o yaml           # YAML格式
kubectl get pods -o json           # JSON格式

# 标签选择器
kubectl get pods -l app=nginx
kubectl get pods -l 'env in (prod,staging)'

# 监听变化
kubectl get pods --watch
kubectl get pods -w
```



## 步骤2：Pod管理

### 2.1 创建第一个Pod

创建 `nginx-pod.yaml`：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

**部署Pod**：

```bash
# 创建Pod
kubectl apply -f nginx-pod.yaml

# 查看Pod
kubectl get pods

# 查看Pod详细信息
kubectl describe pod nginx-pod

# 查看Pod日志
kubectl logs nginx-pod

# 进入Pod
kubectl exec -it nginx-pod -- bash

# 删除Pod
kubectl delete pod nginx-pod
```

### 2.2 多容器Pod

创建 `multi-container-pod.yaml`：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-data
      mountPath: /usr/share/nginx/html
  
  - name: content-generator
    image: busybox
    command: ["/bin/sh"]
    args:
      - -c
      - >
        while true; do
          echo "Hello from Kubernetes! $(date)" > /data/index.html;
          sleep 10;
        done
    volumeMounts:
    - name: shared-data
      mountPath: /data
  
  volumes:
  - name: shared-data
    emptyDir: {}
```

**测试多容器Pod**：

```bash
# 创建Pod
kubectl apply -f multi-container-pod.yaml

# 查看Pod状态
kubectl get pod multi-container-pod

# 查看特定容器的日志
kubectl logs multi-container-pod -c content-generator

# 端口转发测试
kubectl port-forward multi-container-pod 8080:80

# 在另一个终端测试
curl http://localhost:8080
```

### 2.3 Pod生命周期

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: lifecycle-pod
spec:
  containers:
  - name: app
    image: nginx:1.21
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo 'Container started' > /tmp/started"]
      preStop:
        exec:
          command: ["/bin/sh", "-c", "nginx -s quit; while killall -0 nginx; do sleep 1; done"]
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 3
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

**探针类型**：
- **livenessProbe**：检查容器是否存活，失败则重启
- **readinessProbe**：检查容器是否就绪，失败则不接收流量
- **startupProbe**：检查容器是否启动完成


## 步骤3：Deployment管理

### 3.1 创建Deployment

Deployment是管理Pod的推荐方式，提供声明式更新和回滚功能。

创建 `nginx-deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

**部署和管理**：

```bash
# 创建Deployment
kubectl apply -f nginx-deployment.yaml

# 查看Deployment
kubectl get deployments

# 查看ReplicaSet
kubectl get replicasets

# 查看Pod
kubectl get pods

# 查看详细信息
kubectl describe deployment nginx-deployment

# 查看部署状态
kubectl rollout status deployment/nginx-deployment
```

### 3.2 扩缩容

```bash
# 手动扩容
kubectl scale deployment nginx-deployment --replicas=5

# 查看扩容结果
kubectl get pods

# 缩容
kubectl scale deployment nginx-deployment --replicas=2

# 自动扩缩容（HPA）
kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80

# 查看HPA
kubectl get hpa
```

### 3.3 滚动更新

```bash
# 更新镜像
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# 查看更新状态
kubectl rollout status deployment/nginx-deployment

# 查看更新历史
kubectl rollout history deployment/nginx-deployment

# 查看特定版本详情
kubectl rollout history deployment/nginx-deployment --revision=2

# 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment

# 回滚到特定版本
kubectl rollout undo deployment/nginx-deployment --to-revision=1

# 暂停更新
kubectl rollout pause deployment/nginx-deployment

# 恢复更新
kubectl rollout resume deployment/nginx-deployment
```

### 3.4 更新策略

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 更新时最多可以超出期望副本数的数量
      maxUnavailable: 1  # 更新时最多可以不可用的副本数
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**更新策略类型**：
- **RollingUpdate**（默认）：逐步替换旧Pod
- **Recreate**：先删除所有旧Pod，再创建新Pod


## 步骤4：Service服务

### 4.1 ClusterIP Service

ClusterIP是默认的Service类型，只能在集群内部访问。

创建 `nginx-service.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

**部署和测试**：

```bash
# 创建Service
kubectl apply -f nginx-service.yaml

# 查看Service
kubectl get services
kubectl get svc

# 查看Service详细信息
kubectl describe service nginx-service

# 查看Endpoints
kubectl get endpoints nginx-service

# 测试Service（在集群内）
kubectl run test-pod --image=busybox --rm -it -- wget -O- nginx-service
```

### 4.2 NodePort Service

NodePort在每个节点上开放一个端口，可以从集群外部访问。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 30080  # 可选，范围30000-32767
```

**访问NodePort Service**：

```bash
# 创建Service
kubectl apply -f nginx-nodeport.yaml

# 查看Service
kubectl get svc nginx-nodeport

# 获取节点IP
kubectl get nodes -o wide

# 访问服务（Minikube）
minikube service nginx-nodeport --url

# 浏览器访问
# http://<node-ip>:30080
```

### 4.3 LoadBalancer Service

LoadBalancer类型在云环境中创建外部负载均衡器。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

**注意**：LoadBalancer类型需要云提供商支持（AWS、GCP、Azure等）。在Minikube中可以使用`minikube tunnel`模拟。

### 4.4 Headless Service

Headless Service不分配ClusterIP，用于直接访问Pod。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None  # Headless Service
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```



## 步骤5：配置管理

### 5.1 ConfigMap

ConfigMap用于存储非敏感的配置数据。

**创建ConfigMap**：

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgresql://db:5432/myapp"
  log_level: "info"
  config.json: |
    {
      "server": {
        "port": 8080,
        "host": "0.0.0.0"
      },
      "features": {
        "cache": true,
        "debug": false
      }
    }
```

**使用ConfigMap**：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    # 方式1：环境变量
    env:
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_url
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: log_level
    # 方式2：挂载为文件
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

**命令行创建ConfigMap**：

```bash
# 从字面值创建
kubectl create configmap app-config \
  --from-literal=database_url=postgresql://db:5432/myapp \
  --from-literal=log_level=info

# 从文件创建
kubectl create configmap app-config --from-file=config.json

# 从目录创建
kubectl create configmap app-config --from-file=./config/

# 查看ConfigMap
kubectl get configmap
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml
```

### 5.2 Secret

Secret用于存储敏感信息，如密码、密钥等。

**创建Secret**：

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  # Base64编码的值
  username: YWRtaW4=        # admin
  password: cGFzc3dvcmQxMjM=  # password123
```

**使用Secret**：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: password
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: app-secret
```

**命令行创建Secret**：

```bash
# 从字面值创建
kubectl create secret generic app-secret \
  --from-literal=username=admin \
  --from-literal=password=password123

# 从文件创建
kubectl create secret generic app-secret \
  --from-file=username.txt \
  --from-file=password.txt

# 创建Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry-server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>

# 查看Secret
kubectl get secrets
kubectl describe secret app-secret

# Base64编码/解码
echo -n 'admin' | base64        # 编码
echo 'YWRtaW4=' | base64 -d     # 解码
```


## 步骤6：存储管理

### 6.1 Volume类型

Kubernetes支持多种Volume类型：

**emptyDir**：临时存储，Pod删除时数据丢失

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: cache
      mountPath: /cache
  volumes:
  - name: cache
    emptyDir: {}
```

**hostPath**：挂载主机目录

```yaml
volumes:
- name: host-volume
  hostPath:
    path: /data
    type: Directory
```

**configMap和secret**：前面已介绍

### 6.2 PersistentVolume (PV) 和 PersistentVolumeClaim (PVC)

**创建PersistentVolume**：

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
```

**创建PersistentVolumeClaim**：

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
  storageClassName: manual
```

**在Pod中使用PVC**：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /usr/share/nginx/html
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: my-pvc
```

**管理PV和PVC**：

```bash
# 创建PV和PVC
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml

# 查看PV
kubectl get pv

# 查看PVC
kubectl get pvc

# 查看PVC详情
kubectl describe pvc my-pvc

# 删除PVC
kubectl delete pvc my-pvc
```

### 6.3 StorageClass

StorageClass提供动态存储供应。

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
```

**使用StorageClass的PVC**：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-storage
  resources:
    requests:
      storage: 10Gi
```


## 步骤7：命名空间和资源配额

### 7.1 Namespace

Namespace用于资源隔离和多租户管理。

```bash
# 查看命名空间
kubectl get namespaces

# 创建命名空间
kubectl create namespace dev
kubectl create namespace prod

# 使用YAML创建
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: staging
EOF

# 在特定命名空间创建资源
kubectl apply -f deployment.yaml -n dev

# 设置默认命名空间
kubectl config set-context --current --namespace=dev

# 删除命名空间
kubectl delete namespace dev
```

### 7.2 ResourceQuota

限制命名空间的资源使用。

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "10"
    persistentvolumeclaims: "10"
```

```bash
# 创建ResourceQuota
kubectl apply -f resource-quota.yaml

# 查看配额
kubectl get resourcequota -n dev
kubectl describe resourcequota dev-quota -n dev
```

### 7.3 LimitRange

设置Pod和容器的默认资源限制。

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: dev
spec:
  limits:
  - max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: "100m"
      memory: 128Mi
    default:
      cpu: "500m"
      memory: 512Mi
    defaultRequest:
      cpu: "250m"
      memory: 256Mi
    type: Container
```


## 步骤8：部署完整应用

让我们部署一个完整的Web应用栈（前端 + 后端 + 数据库）。

### 8.1 项目结构

```
k8s-app/
├── namespace.yaml
├── database/
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
├── backend/
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   ├── backend-deployment.yaml
│   └── backend-service.yaml
└── frontend/
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

### 8.2 创建命名空间

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
```

### 8.3 部署数据库

**PVC**：
```yaml
# database/postgres-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: myapp
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

**Deployment**：
```yaml
# database/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: myapp
        - name: POSTGRES_USER
          value: appuser
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

**Service**：
```yaml
# database/postgres-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: myapp
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
```


### 8.4 部署后端

**Secret**：
```yaml
# backend/backend-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: myapp
type: Opaque
stringData:
  password: "mypassword123"
```

**ConfigMap**：
```yaml
# backend/backend-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: myapp
data:
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "myapp"
  LOG_LEVEL: "info"
```

**Deployment**：
```yaml
# backend/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: myapp/backend:1.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: DATABASE_HOST
        - name: DATABASE_PORT
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: DATABASE_PORT
        - name: DATABASE_NAME
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: DATABASE_NAME
        - name: DATABASE_USER
          value: "appuser"
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Service**：
```yaml
# backend/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: myapp
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
```

### 8.5 部署前端

**Deployment**：
```yaml
# frontend/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: myapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: myapp/frontend:1.0
        ports:
        - containerPort: 80
        env:
        - name: BACKEND_URL
          value: "http://backend:8080"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

**Service**：
```yaml
# frontend/frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: myapp
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 30080
```

### 8.6 部署应用

```bash
# 创建命名空间
kubectl apply -f namespace.yaml

# 部署数据库
kubectl apply -f database/

# 部署后端
kubectl apply -f backend/

# 部署前端
kubectl apply -f frontend/

# 查看所有资源
kubectl get all -n myapp

# 查看Pod状态
kubectl get pods -n myapp

# 查看Service
kubectl get svc -n myapp

# 访问应用（Minikube）
minikube service frontend -n myapp --url

# 查看日志
kubectl logs -f deployment/backend -n myapp
```


## 步骤9：Ingress控制器

Ingress提供HTTP和HTTPS路由到集群内服务。

### 9.1 安装Ingress Controller

```bash
# Minikube启用Ingress
minikube addons enable ingress

# 或使用Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 查看Ingress Controller
kubectl get pods -n ingress-nginx
```

### 9.2 创建Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: myapp
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8080
```

**配置和测试**：

```bash
# 创建Ingress
kubectl apply -f ingress.yaml

# 查看Ingress
kubectl get ingress -n myapp

# 配置hosts文件
# Linux/macOS: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts
# 添加：
# <minikube-ip> myapp.local

# 获取Minikube IP
minikube ip

# 测试访问
curl http://myapp.local
curl http://myapp.local/api/health
```

### 9.3 TLS/HTTPS配置

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
  namespace: myapp
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress-tls
  namespace: myapp
spec:
  tls:
  - hosts:
    - myapp.local
    secretName: tls-secret
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```


## 步骤10：监控和日志

### 10.1 查看资源使用

```bash
# 查看节点资源使用
kubectl top nodes

# 查看Pod资源使用
kubectl top pods -n myapp

# 查看特定Pod的资源使用
kubectl top pod <pod-name> -n myapp
```

### 10.2 查看日志

```bash
# 查看Pod日志
kubectl logs <pod-name> -n myapp

# 实时查看日志
kubectl logs -f <pod-name> -n myapp

# 查看多容器Pod的特定容器日志
kubectl logs <pod-name> -c <container-name> -n myapp

# 查看之前容器的日志
kubectl logs <pod-name> --previous -n myapp

# 查看最近的日志
kubectl logs <pod-name> --tail=100 -n myapp

# 查看带时间戳的日志
kubectl logs <pod-name> --timestamps -n myapp
```

### 10.3 事件查看

```bash
# 查看所有事件
kubectl get events -n myapp

# 按时间排序
kubectl get events -n myapp --sort-by='.lastTimestamp'

# 监听事件
kubectl get events -n myapp --watch
```


## 故障排除

### 问题1：Pod一直处于Pending状态

**现象**：
```bash
kubectl get pods
# NAME                    READY   STATUS    RESTARTS   AGE
# my-pod                  0/1     Pending   0          5m
```

**可能原因**：
1. 资源不足（CPU、内存）
2. PVC未绑定
3. 节点选择器不匹配

**解决方法**：

```bash
# 查看Pod详情
kubectl describe pod my-pod

# 检查事件
kubectl get events --sort-by='.lastTimestamp'

# 检查节点资源
kubectl top nodes

# 检查PVC状态
kubectl get pvc

# 临时解决：降低资源请求
# 编辑deployment，减少resources.requests
```

### 问题2：Pod一直重启

**现象**：
```bash
kubectl get pods
# NAME                    READY   STATUS             RESTARTS   AGE
# my-pod                  0/1     CrashLoopBackOff   5          10m
```

**可能原因**：
1. 应用启动失败
2. 健康检查失败
3. 配置错误

**解决方法**：

```bash
# 查看日志
kubectl logs my-pod
kubectl logs my-pod --previous  # 查看上次运行的日志

# 查看Pod详情
kubectl describe pod my-pod

# 进入容器调试
kubectl exec -it my-pod -- sh

# 检查健康检查配置
kubectl get pod my-pod -o yaml | grep -A 10 livenessProbe
```

### 问题3：Service无法访问

**现象**：
无法通过Service访问Pod

**解决方法**：

```bash
# 检查Service
kubectl get svc
kubectl describe svc my-service

# 检查Endpoints
kubectl get endpoints my-service

# 检查Pod标签
kubectl get pods --show-labels

# 检查Service选择器
kubectl get svc my-service -o yaml | grep -A 5 selector

# 测试Pod直接访问
kubectl run test --image=busybox --rm -it -- wget -O- <pod-ip>:80
```

### 问题4：镜像拉取失败

**现象**：
```bash
kubectl get pods
# NAME                    READY   STATUS         RESTARTS   AGE
# my-pod                  0/1     ImagePullBackOff   0      2m
```

**解决方法**：

```bash
# 查看详细错误
kubectl describe pod my-pod

# 检查镜像名称
kubectl get pod my-pod -o yaml | grep image:

# 使用imagePullSecrets
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>

# 在Pod中使用
spec:
  imagePullSecrets:
  - name: regcred
```

### 问题5：PVC无法绑定

**现象**：
```bash
kubectl get pvc
# NAME      STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# my-pvc    Pending                                      standard       5m
```

**解决方法**：

```bash
# 查看PVC详情
kubectl describe pvc my-pvc

# 检查PV
kubectl get pv

# 检查StorageClass
kubectl get storageclass

# 手动创建PV（如果需要）
# 或使用动态供应
```



## 最佳实践

### 1. 资源管理

```yaml
# ✅ 好的做法：始终设置资源请求和限制
spec:
  containers:
  - name: app
    image: myapp:1.0
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"

# ❌ 不好的做法：不设置资源限制
spec:
  containers:
  - name: app
    image: myapp:1.0
    # 没有resources配置
```

### 2. 健康检查

```yaml
# ✅ 好的做法：配置健康检查
spec:
  containers:
  - name: app
    image: myapp:1.0
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5

# ❌ 不好的做法：不配置健康检查
```

### 3. 标签和选择器

```yaml
# ✅ 好的做法：使用有意义的标签
metadata:
  labels:
    app: myapp
    component: backend
    version: v1.0
    environment: production

# ❌ 不好的做法：标签不清晰
metadata:
  labels:
    name: pod1
```

### 4. 配置管理

```yaml
# ✅ 好的做法：使用ConfigMap和Secret
env:
- name: DATABASE_URL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: database_url
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secret
      key: password

# ❌ 不好的做法：硬编码配置
env:
- name: DATABASE_URL
  value: "postgresql://db:5432/myapp"
- name: DATABASE_PASSWORD
  value: "password123"  # 不要这样做！
```

### 5. 镜像管理

```yaml
# ✅ 好的做法：使用特定版本标签
spec:
  containers:
  - name: app
    image: myapp:1.2.3
    imagePullPolicy: IfNotPresent

# ❌ 不好的做法：使用latest标签
spec:
  containers:
  - name: app
    image: myapp:latest  # 避免使用latest
```

### 6. 命名空间隔离

```bash
# ✅ 好的做法：使用命名空间隔离环境
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace prod

# 在特定命名空间部署
kubectl apply -f app.yaml -n dev

# ❌ 不好的做法：所有资源都在default命名空间
```

### 7. 滚动更新策略

```yaml
# ✅ 好的做法：配置合理的更新策略
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # 确保服务不中断

# ❌ 不好的做法：使用Recreate策略（除非必要）
spec:
  strategy:
    type: Recreate  # 会导致服务中断
```

### 8. 安全实践

```yaml
# ✅ 好的做法：使用非root用户
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true

# ❌ 不好的做法：以root用户运行
```


## 总结

通过本教程，你已经学习了Kubernetes容器编排的核心内容：

### 核心要点回顾

**Kubernetes架构**：
- ✅ 控制平面：API Server、Scheduler、Controller Manager、etcd
- ✅ 工作节点：kubelet、kube-proxy、Container Runtime
- ✅ 核心资源：Pod、Deployment、Service、ConfigMap、Secret

**基本操作**：
- ✅ kubectl命令：get、describe、logs、exec、apply、delete
- ✅ Pod管理：创建、查看、调试、删除
- ✅ Deployment：部署、扩缩容、滚动更新、回滚
- ✅ Service：ClusterIP、NodePort、LoadBalancer

**高级功能**：
- ✅ 配置管理：ConfigMap、Secret
- ✅ 存储管理：Volume、PV、PVC、StorageClass
- ✅ 命名空间：资源隔离、ResourceQuota、LimitRange
- ✅ Ingress：HTTP路由、TLS配置

**实践项目**：
- ✅ 部署完整的三层应用（前端+后端+数据库）
- ✅ 配置服务发现和负载均衡
- ✅ 实现滚动更新和健康检查
- ✅ 配置Ingress和域名访问

### 实践成果

完成本教程后，你应该能够：
1. 搭建和管理Kubernetes集群
2. 使用kubectl进行日常操作
3. 部署和管理容器化应用
4. 配置服务发现和负载均衡
5. 实现应用的自动化运维
6. 解决常见的Kubernetes问题

### 下一步学习建议

1. **深入学习**
   - Helm包管理器
   - Kubernetes Operator
   - 服务网格（Istio、Linkerd）
   - GitOps（ArgoCD、Flux）

2. **实践项目**
   - 部署微服务应用
   - 实现CI/CD流程
   - 配置监控和告警
   - 实现多集群管理

3. **进阶主题**
   - 集群安全加固
   - 性能优化
   - 灾难恢复
   - 多云部署


## 进阶挑战

尝试以下挑战来巩固学习：

### 挑战1：部署有状态应用（45分钟）

**任务**：
1. 使用StatefulSet部署MongoDB集群
2. 配置持久化存储
3. 实现数据备份和恢复
4. 配置Headless Service

**提示**：
- 使用StatefulSet而不是Deployment
- 配置volumeClaimTemplates
- 使用init容器进行初始化

### 挑战2：实现蓝绿部署（30分钟）

**任务**：
1. 部署应用的两个版本（蓝色和绿色）
2. 使用Service切换流量
3. 验证新版本后完全切换
4. 实现快速回滚

**目标**：
- 零停机部署
- 快速回滚能力

### 挑战3：搭建物联网数据处理平台（90分钟）

**任务**：
1. 部署MQTT Broker（Mosquitto）
2. 部署数据处理服务（Python/Node.js）
3. 部署时序数据库（InfluxDB）
4. 部署可视化服务（Grafana）
5. 配置Ingress访问

**要求**：
- 所有服务使用Deployment
- 配置持久化存储
- 实现服务间通信
- 配置资源限制
- 实现健康检查


## 常见问题

### Q1: Kubernetes和Docker Swarm有什么区别？

**A**: 主要区别：

| 特性 | Kubernetes | Docker Swarm |
|------|-----------|--------------|
| 复杂度 | 较高 | 较低 |
| 功能 | 非常丰富 | 基础功能 |
| 社区 | 非常活跃 | 较小 |
| 学习曲线 | 陡峭 | 平缓 |
| 生产就绪 | 是 | 是 |
| 生态系统 | 庞大 | 有限 |

Kubernetes功能更强大，适合大规模生产环境；Docker Swarm更简单，适合小型项目。

### Q2: 什么时候使用Deployment，什么时候使用StatefulSet？

**A**: 

**使用Deployment**：
- 无状态应用
- 可以随意替换的Pod
- 不需要稳定的网络标识
- 例如：Web服务器、API服务

**使用StatefulSet**：
- 有状态应用
- 需要稳定的网络标识
- 需要持久化存储
- 需要有序部署和扩展
- 例如：数据库、消息队列、分布式系统

### Q3: 如何选择Service类型？

**A**: 

**ClusterIP**（默认）：
- 只需要集群内部访问
- 通过Ingress暴露服务

**NodePort**：
- 需要从集群外部访问
- 开发和测试环境
- 不需要负载均衡器

**LoadBalancer**：
- 生产环境
- 需要云提供商的负载均衡器
- 需要固定的外部IP

**Headless**：
- 需要直接访问Pod
- 有状态应用
- 服务发现

### Q4: 如何调试Pod启动失败？

**A**: 按以下步骤排查：

```bash
# 1. 查看Pod状态
kubectl get pods

# 2. 查看Pod详情和事件
kubectl describe pod <pod-name>

# 3. 查看容器日志
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # 查看上次运行的日志

# 4. 进入容器调试（如果容器在运行）
kubectl exec -it <pod-name> -- sh

# 5. 查看集群事件
kubectl get events --sort-by='.lastTimestamp'

# 6. 检查资源配置
kubectl get pod <pod-name> -o yaml
```

### Q5: 如何实现零停机部署？

**A**: 

1. **使用滚动更新**：
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0  # 关键：确保始终有Pod可用
```

2. **配置就绪探针**：
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

3. **优雅关闭**：
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]
```

4. **足够的副本数**：
```yaml
replicas: 3  # 至少3个副本
```

### Q6: 如何在Kubernetes中管理密钥？

**A**: 

**方法1：使用Secret**（基础）：
```bash
kubectl create secret generic app-secret \
  --from-literal=password=mypassword
```

**方法2：使用外部密钥管理**（推荐）：
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

**方法3：使用Sealed Secrets**：
- 加密Secret后存储在Git
- 集群中自动解密

**最佳实践**：
- 不要将Secret提交到Git
- 使用RBAC限制访问
- 定期轮换密钥
- 使用外部密钥管理系统


## 延伸阅读

### 推荐资源

**官方文档**：
- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Kubernetes中文文档](https://kubernetes.io/zh-cn/docs/)
- [kubectl命令参考](https://kubernetes.io/docs/reference/kubectl/)

**在线教程**：
- [Kubernetes官方教程](https://kubernetes.io/docs/tutorials/)
- [Katacoda Kubernetes课程](https://www.katacoda.com/courses/kubernetes)
- [Play with Kubernetes](https://labs.play-with-k8s.com/)

**书籍推荐**：
- 《Kubernetes权威指南》- 龚正等
- 《Kubernetes in Action》- Marko Lukša
- 《深入剖析Kubernetes》- 张磊

**视频课程**：
- Kubernetes官方YouTube频道
- CNCF YouTube频道
- 极客时间《深入剖析Kubernetes》

### 相关技术

**容器编排**：
- Docker Swarm - Docker原生编排
- Nomad - HashiCorp的编排工具
- Rancher - Kubernetes管理平台

**服务网格**：
- Istio - 功能最丰富的服务网格
- Linkerd - 轻量级服务网格
- Consul Connect - HashiCorp的服务网格

**包管理**：
- Helm - Kubernetes包管理器
- Kustomize - Kubernetes配置管理
- Operator Framework - 自定义控制器

**CI/CD**：
- ArgoCD - GitOps持续交付
- Flux - GitOps工具
- Tekton - Kubernetes原生CI/CD

**监控和日志**：
- Prometheus - 监控系统
- Grafana - 可视化平台
- ELK/EFK Stack - 日志分析
- Jaeger - 分布式追踪


## 参考资料

1. Kubernetes官方文档 - https://kubernetes.io/docs/
2. Kubernetes最佳实践 - https://kubernetes.io/docs/concepts/configuration/overview/
3. kubectl命令参考 - https://kubernetes.io/docs/reference/kubectl/
4. Kubernetes API参考 - https://kubernetes.io/docs/reference/kubernetes-api/
5. CNCF云原生技术栈 - https://landscape.cncf.io/

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 发现文档错误或有改进建议，请提交Issue
- 想要分享你的Kubernetes实践经验，欢迎投稿

**下一步学习**：
- [Serverless无服务器架构](../intermediate/02-serverless.html) - 学习函数计算
- [云原生应用开发](../advanced/01-cloud-native-app.html) - 构建云原生应用
- [微服务架构设计](../../01-backend-development/intermediate/01-microservices.html) - 学习微服务
- [消息队列应用](../../01-backend-development/intermediate/02-message-queue.html) - 学习异步通信

---

**版权声明**：
本文采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
