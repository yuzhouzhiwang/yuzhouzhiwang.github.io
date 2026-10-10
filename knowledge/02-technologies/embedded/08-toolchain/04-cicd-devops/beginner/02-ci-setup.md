---
title: "持续集成环境搭建：从零开始构建CI系统"
description: "详细讲解如何搭建持续集成环境，包括Jenkins和GitLab CI的安装配置、Runner设置、任务创建和自动化构建流程"
slug: "ci-setup-tutorial"

# 分类信息
domain: "工具链"
module: "CI/CD与DevOps"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 持续集成
  - CI搭建
  - 自动化
  - Jenkins
  - GitLab CI
  - DevOps
prerequisites:
  - "git-advanced-techniques"
related_contents:
  - "cd-pipeline-design"
  - "automated-testing-integration"
  - "devops-best-practices"

# 学习信息
estimated_time: 85
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: "embedded-platform"
created_at: "2024-01-15"
updated_at: "2024-01-15"
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
  - CI环境搭建
  - Jenkins安装
  - GitLab CI配置
  - 持续集成教程
  - 自动化构建
cover_image: ""
---

# 持续集成环境搭建：从零开始构建CI系统


## 概述

持续集成（Continuous Integration, CI）是现代软件开发的基础实践之一。通过自动化构建、测试和验证，CI能够帮助团队快速发现问题、提高代码质量、加速开发迭代。本教程将手把手教你搭建完整的CI环境。

### 什么是持续集成？

**持续集成的核心理念**:
- 开发者频繁地将代码集成到主分支（每天多次）
- 每次集成都通过自动化构建和测试验证
- 快速发现和修复集成问题
- 保持代码库始终处于可工作状态

**CI的价值**:
- ✅ 自动化重复性工作，节省时间
- ✅ 快速发现代码问题，降低修复成本
- ✅ 提高代码质量和可靠性
- ✅ 加速开发和发布节奏
- ✅ 增强团队协作效率
- ✅ 提供可视化的构建和测试报告

### 为什么嵌入式开发需要CI？

**传统嵌入式开发的痛点**:
- ❌ 手动编译耗时且容易出错
- ❌ 多平台交叉编译配置复杂
- ❌ 代码集成时经常出现冲突
- ❌ 测试依赖硬件，难以自动化
- ❌ 固件版本管理混乱
- ❌ 团队协作效率低下

**CI带来的改进**:
- ✅ 自动化编译和构建流程
- ✅ 多平台并行构建
- ✅ 自动运行单元测试
- ✅ 代码质量自动检查
- ✅ 自动生成固件和文档
- ✅ 规范化的版本管理

### 学习目标

完成本教程后，你将能够:

- [ ] 理解CI的核心概念和工作原理
- [ ] 选择适合项目的CI工具
- [ ] 搭建Jenkins CI服务器
- [ ] 配置GitLab CI/CD环境
- [ ] 创建第一个自动化构建任务
- [ ] 配置构建触发器和通知
- [ ] 集成代码质量检查工具


## CI工具选择

### 主流CI工具对比

| 工具 | 类型 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **Jenkins** | 自托管 | 功能强大、插件丰富、免费 | 配置复杂、需要维护 | 企业级项目、复杂流程 |
| **GitLab CI** | 集成/自托管 | 与GitLab深度集成、配置简单 | 依赖GitLab | GitLab用户 |
| **GitHub Actions** | 云服务 | 与GitHub集成、免费额度 | 公共仓库限制 | GitHub项目 |
| **Travis CI** | 云服务 | 配置简单、云端运行 | 免费版限制多 | 开源项目 |
| **CircleCI** | 云服务 | 性能好、Docker支持 | 价格较高 | 商业项目 |

### 选择建议

**选择Jenkins的理由**:
- 需要完全控制CI环境
- 有复杂的构建流程
- 需要集成多种工具
- 预算有限（完全免费）
- 有专人维护CI系统

**选择GitLab CI的理由**:
- 已经使用GitLab
- 希望配置简单
- 需要与代码仓库深度集成
- 团队规模中小型

**选择GitHub Actions的理由**:
- 项目托管在GitHub
- 开源项目（免费）
- 不想维护CI服务器

**嵌入式项目推荐**:
1. **首选**: Jenkins（灵活性高，适合复杂构建）
2. **次选**: GitLab CI（配置简单，易于上手）
3. **备选**: 自建GitLab + GitLab CI（完全自主可控）


## 环境准备

### 硬件要求

**最低配置**:
- CPU: 2核心
- 内存: 4GB RAM
- 硬盘: 50GB可用空间
- 网络: 稳定的互联网连接

**推荐配置**:
- CPU: 4核心或更多
- 内存: 8GB RAM或更多
- 硬盘: 100GB SSD
- 网络: 千兆网络

### 软件要求

**操作系统**:
- Linux: Ubuntu 20.04/22.04 LTS（推荐）
- Windows: Windows 10/11 Pro
- macOS: 10.15或更高版本

**必备软件**:
- Git 2.x
- Docker 20.x（推荐）
- Java JDK 11或17（Jenkins需要）
- Python 3.8+（用于脚本）

### 网络配置

**防火墙规则**:
```bash
# Jenkins默认端口
8080/tcp  # Web界面
50000/tcp # Agent通信

# GitLab CI默认端口
80/tcp    # HTTP
443/tcp   # HTTPS
22/tcp    # SSH
```

**域名配置**（可选）:
- Jenkins: `jenkins.yourdomain.com`
- GitLab: `gitlab.yourdomain.com`


## Jenkins安装与配置

### 方法1: Docker安装（推荐）

Docker安装是最简单、最快速的方式，适合快速搭建和测试。

#### 步骤1: 安装Docker

**Ubuntu/Debian**:
```bash
# 更新软件包索引
sudo apt update

# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

**Windows**:
1. 下载Docker Desktop: https://www.docker.com/products/docker-desktop
2. 运行安装程序
3. 重启计算机
4. 启动Docker Desktop

#### 步骤2: 运行Jenkins容器

```bash
# 创建Jenkins数据卷（持久化数据）
docker volume create jenkins_home

# 运行Jenkins容器
docker run -d \
  --name jenkins \
  --restart=always \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# 查看容器状态
docker ps

# 查看Jenkins日志
docker logs jenkins

# 获取初始管理员密码
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**输出示例**:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

保存这个密码，稍后需要用到。


### 方法2: Linux系统直接安装

适合生产环境，性能更好，但配置稍复杂。

#### Ubuntu/Debian安装

```bash
# 安装Java（Jenkins依赖）
sudo apt update
sudo apt install -y openjdk-11-jdk

# 验证Java安装
java -version

# 添加Jenkins仓库密钥
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# 添加Jenkins仓库
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# 更新软件包列表
sudo apt update

# 安装Jenkins
sudo apt install -y jenkins

# 启动Jenkins服务
sudo systemctl start jenkins
sudo systemctl enable jenkins

# 检查服务状态
sudo systemctl status jenkins

# 查看初始管理员密码
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### CentOS/RHEL安装

```bash
# 安装Java
sudo yum install -y java-11-openjdk

# 添加Jenkins仓库
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# 安装Jenkins
sudo yum install -y jenkins

# 启动Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# 查看初始密码
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 方法3: Windows安装

#### 步骤1: 安装Java

1. 下载Java JDK 11: https://adoptium.net/
2. 运行安装程序
3. 配置环境变量 `JAVA_HOME`

#### 步骤2: 安装Jenkins

```cmd
# 下载Jenkins WAR文件
# 访问: https://www.jenkins.io/download/

# 运行Jenkins
java -jar jenkins.war --httpPort=8080

# 或者下载Windows安装程序
# 访问: https://www.jenkins.io/download/
# 下载jenkins.msi并安装
```


### Jenkins初始配置

#### 步骤1: 访问Jenkins

打开浏览器，访问:
```
http://localhost:8080
```

或者如果是远程服务器:
```
http://your-server-ip:8080
```

#### 步骤2: 解锁Jenkins

1. 在"Unlock Jenkins"页面，输入之前获取的初始管理员密码
2. 点击"Continue"

#### 步骤3: 安装插件

选择"Install suggested plugins"（安装推荐的插件）

Jenkins会自动安装以下插件:
- Git plugin
- Pipeline
- Credentials
- SSH Slaves
- Email Extension
- 等等...

这个过程需要几分钟，请耐心等待。

#### 步骤4: 创建管理员用户

填写以下信息:
- Username: `admin`
- Password: `your-secure-password`
- Confirm password: `your-secure-password`
- Full name: `Administrator`
- E-mail address: `admin@example.com`

点击"Save and Continue"

#### 步骤5: 配置Jenkins URL

确认Jenkins URL:
```
http://localhost:8080/
```

点击"Save and Finish"

#### 步骤6: 开始使用Jenkins

点击"Start using Jenkins"，进入Jenkins主界面。

恭喜！Jenkins已经成功安装并配置完成。


### 安装必要插件

进入 "Manage Jenkins" → "Manage Plugins" → "Available"

#### 基础插件

搜索并安装以下插件:

**版本控制**:
- ☑ Git plugin（通常已安装）
- ☑ GitHub plugin
- ☑ GitLab plugin

**构建工具**:
- ☑ Pipeline
- ☑ Blue Ocean（现代化UI）
- ☑ Workspace Cleanup

**通知**:
- ☑ Email Extension Plugin
- ☑ Slack Notification Plugin

**报告**:
- ☑ HTML Publisher
- ☑ JUnit Plugin
- ☑ Cobertura Plugin

**代码质量**:
- ☑ Warnings Next Generation
- ☑ SonarQube Scanner

#### 嵌入式开发专用插件

- ☑ Embunit Plugin（嵌入式单元测试）
- ☑ Cppcheck Plugin（C/C++静态分析）

安装完成后，点击"Restart Jenkins when installation is complete and no jobs are running"


### 配置全局工具

进入 "Manage Jenkins" → "Global Tool Configuration"

#### 配置Git

```
Name: Default
Path to Git executable: git
```

如果Git不在系统PATH中，需要指定完整路径:
- Linux: `/usr/bin/git`
- Windows: `C:\Program Files\Git\bin\git.exe`

#### 配置JDK（如果需要）

```
Name: JDK11
JAVA_HOME: /usr/lib/jvm/java-11-openjdk-amd64
```

或者选择"Install automatically"让Jenkins自动安装。

#### 配置构建工具

**对于嵌入式开发，配置ARM工具链**:

进入 "Manage Jenkins" → "Configure System" → "Global properties"

勾选"Environment variables"，添加:

```
Name: ARM_TOOLCHAIN_PATH
Value: /usr/local/gcc-arm-none-eabi/bin

Name: PATH
Value: $ARM_TOOLCHAIN_PATH:$PATH
```

点击"Save"保存配置。


### 创建第一个Jenkins任务

#### 自由风格项目

**步骤1: 创建新任务**

1. 在Jenkins主页，点击"New Item"
2. 输入任务名称: `STM32_Build_Test`
3. 选择"Freestyle project"
4. 点击"OK"

**步骤2: 配置源代码管理**

在"Source Code Management"部分:

1. 选择"Git"
2. Repository URL: `https://github.com/your-username/stm32-project.git`
3. Credentials: 
   - 点击"Add" → "Jenkins"
   - Kind: "Username with password"
   - Username: 你的GitHub用户名
   - Password: 你的GitHub Personal Access Token
   - ID: `github-credentials`
   - Description: `GitHub Credentials`
   - 点击"Add"
4. 选择刚创建的凭据
5. Branch Specifier: `*/main`

**步骤3: 配置构建触发器**

选择以下一个或多个触发方式:

1. **Poll SCM**（定期检查代码变化）:
   ```
   H/5 * * * *
   ```
   这表示每5分钟检查一次代码仓库

2. **GitHub hook trigger**（推荐）:
   - 勾选"GitHub hook trigger for GITScm polling"
   - 需要在GitHub仓库设置Webhook

3. **Build periodically**（定时构建）:
   ```
   H 2 * * *
   ```
   这表示每天凌晨2点构建

**步骤4: 配置构建环境**

勾选以下选项:

- ☑ Delete workspace before build starts（构建前清理工作空间）
- ☑ Add timestamps to the Console Output（添加时间戳）

**步骤5: 添加构建步骤**

点击"Add build step" → "Execute shell"

输入构建脚本:

```bash
#!/bin/bash
set -e

echo "========================================="
echo "开始构建 STM32 项目"
echo "========================================="

# 显示环境信息
echo "构建编号: $BUILD_NUMBER"
echo "工作空间: $WORKSPACE"
echo "Git分支: $GIT_BRANCH"
echo "Git提交: $GIT_COMMIT"

# 设置工具链路径
export PATH=$ARM_TOOLCHAIN_PATH:$PATH

# 验证工具链
echo "验证ARM工具链..."
arm-none-eabi-gcc --version

# 清理之前的构建
echo "清理构建目录..."
make clean

# 编译项目
echo "开始编译..."
make all -j4

# 检查编译结果
if [ -f build/firmware.bin ]; then
    echo "✓ 固件构建成功"
    ls -lh build/firmware.*
    
    # 显示固件大小
    arm-none-eabi-size build/firmware.elf
else
    echo "✗ 固件构建失败"
    exit 1
fi

echo "========================================="
echo "构建完成"
echo "========================================="
```

**步骤6: 添加构建后操作**

1. **归档构建产物**:
   - 点击"Add post-build action" → "Archive the artifacts"
   - Files to archive: `build/*.bin, build/*.hex, build/*.elf, build/*.map`
   - 勾选"Fingerprint artifacts"

2. **邮件通知**:
   - 点击"Add post-build action" → "E-mail Notification"
   - Recipients: `team@example.com`
   - 勾选"Send e-mail for every unstable build"
   - 勾选"Send separate e-mails to individuals who broke the build"

**步骤7: 保存并构建**

1. 点击"Save"保存配置
2. 点击"Build Now"开始第一次构建
3. 在"Build History"中查看构建进度
4. 点击构建编号查看详细日志


## GitLab CI/CD配置

### GitLab Runner安装

GitLab Runner是执行CI/CD任务的程序，需要单独安装。

#### Linux安装

**Ubuntu/Debian**:
```bash
# 添加GitLab官方仓库
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

# 安装GitLab Runner
sudo apt install gitlab-runner

# 验证安装
gitlab-runner --version
```

**CentOS/RHEL**:
```bash
# 添加GitLab官方仓库
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" | sudo bash

# 安装GitLab Runner
sudo yum install gitlab-runner

# 验证安装
gitlab-runner --version
```

#### Docker安装

```bash
# 运行GitLab Runner容器
docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest

# 验证安装
docker exec gitlab-runner gitlab-runner --version
```

#### Windows安装

1. 下载GitLab Runner: https://docs.gitlab.com/runner/install/windows.html
2. 创建目录: `C:\GitLab-Runner`
3. 将下载的文件重命名为 `gitlab-runner.exe`
4. 以管理员身份运行PowerShell:

```powershell
cd C:\GitLab-Runner
.\gitlab-runner.exe install
.\gitlab-runner.exe start
```


### 注册GitLab Runner

#### 获取注册信息

1. 登录GitLab
2. 进入你的项目
3. 导航到 "Settings" → "CI/CD"
4. 展开"Runners"部分
5. 记录以下信息:
   - GitLab URL: `https://gitlab.com/` 或你的GitLab实例URL
   - Registration token: 类似 `GR1348941...`

#### 注册Runner

**交互式注册**:

```bash
# 运行注册命令
sudo gitlab-runner register

# 按提示输入信息:
# Enter the GitLab instance URL:
https://gitlab.com/

# Enter the registration token:
GR1348941...

# Enter a description for the runner:
embedded-builder

# Enter tags for the runner (comma-separated):
arm,embedded,stm32,docker

# Enter an executor:
docker

# Enter the default Docker image:
gcc:latest
```

**非交互式注册**:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "GR1348941..." \
  --executor "docker" \
  --docker-image "gcc:latest" \
  --description "embedded-builder" \
  --tag-list "arm,embedded,stm32,docker" \
  --run-untagged="false" \
  --locked="false"
```

#### 验证Runner

1. 返回GitLab项目的"Settings" → "CI/CD" → "Runners"
2. 应该能看到刚注册的Runner，状态为绿色（在线）

#### Runner配置文件

配置文件位置:
- Linux: `/etc/gitlab-runner/config.toml`
- Windows: `C:\GitLab-Runner\config.toml`

示例配置:
```toml
concurrent = 4
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "embedded-builder"
  url = "https://gitlab.com/"
  token = "your-runner-token"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "gcc:latest"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
```


### 创建.gitlab-ci.yml文件

在项目根目录创建 `.gitlab-ci.yml` 文件，这是GitLab CI的配置文件。

#### 基础配置示例

```yaml
# 定义构建阶段
stages:
  - build
  - test

# 全局变量
variables:
  GIT_SUBMODULE_STRATEGY: recursive

# 构建任务
build_firmware:
  stage: build
  image: gcc:latest
  before_script:
    - apt-get update && apt-get install -y make
  script:
    - echo "开始构建固件..."
    - make --version
    - make clean
    - make all
  artifacts:
    paths:
      - build/*.bin
      - build/*.hex
      - build/*.elf
    expire_in: 1 week
  only:
    - main
    - develop
  tags:
    - docker

# 测试任务
test_firmware:
  stage: test
  image: gcc:latest
  script:
    - echo "运行测试..."
    - make test
  only:
    - main
    - develop
  tags:
    - docker
```

#### 嵌入式项目完整示例

```yaml
# 定义构建阶段
stages:
  - prepare
  - build
  - test
  - deploy

# 全局变量
variables:
  GIT_SUBMODULE_STRATEGY: recursive
  ARM_TOOLCHAIN_PATH: /usr/local/gcc-arm-none-eabi/bin
  FIRMWARE_VERSION: "1.0.${CI_PIPELINE_ID}"

# 准备阶段
prepare:
  stage: prepare
  image: alpine:latest
  script:
    - echo "Pipeline ID: $CI_PIPELINE_ID"
    - echo "Commit SHA: $CI_COMMIT_SHA"
    - echo "Branch: $CI_COMMIT_REF_NAME"
    - echo "Firmware Version: $FIRMWARE_VERSION"
  tags:
    - docker

# 构建STM32固件
build_stm32:
  stage: build
  image: arm-toolchain:latest
  before_script:
    - export PATH=$ARM_TOOLCHAIN_PATH:$PATH
    - arm-none-eabi-gcc --version
  script:
    - echo "构建STM32固件 v$FIRMWARE_VERSION"
    - make clean
    - make all -j4 VERSION=$FIRMWARE_VERSION
    - ls -lh build/
    - arm-none-eabi-size build/*.elf
  after_script:
    - echo "构建完成"
  artifacts:
    name: "firmware-$CI_COMMIT_REF_NAME-$CI_COMMIT_SHORT_SHA"
    paths:
      - build/*.bin
      - build/*.hex
      - build/*.elf
      - build/*.map
    expire_in: 30 days
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .cache/
  only:
    - main
    - develop
    - merge_requests
  tags:
    - arm
    - docker

# 单元测试
unit_test:
  stage: test
  image: gcc:latest
  dependencies:
    - build_stm32
  script:
    - echo "运行单元测试..."
    - make test
  artifacts:
    reports:
      junit: test-results.xml
  only:
    - main
    - develop
  tags:
    - docker

# 代码质量检查
code_quality:
  stage: test
  image: cppcheck:latest
  script:
    - cppcheck --enable=all --xml --xml-version=2 src/ 2> cppcheck.xml
  artifacts:
    paths:
      - cppcheck.xml
  allow_failure: true
  tags:
    - docker

# 部署到测试环境
deploy_test:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
  script:
    - echo "部署到测试服务器..."
    - echo "固件版本: $FIRMWARE_VERSION"
  environment:
    name: test
    url: http://test-server.example.com
  only:
    - develop
  when: manual
  tags:
    - docker
```

#### 提交配置文件

```bash
# 添加配置文件
git add .gitlab-ci.yml

# 提交
git commit -m "ci: 添加GitLab CI配置"

# 推送到GitLab
git push origin main
```

推送后，GitLab会自动检测 `.gitlab-ci.yml` 文件并触发CI流水线。


### 查看CI流水线

#### 在GitLab界面查看

1. 进入项目主页
2. 点击左侧菜单的"CI/CD" → "Pipelines"
3. 可以看到所有的流水线执行记录
4. 点击某个流水线查看详细信息
5. 点击某个任务查看执行日志

#### Pipeline状态

- 🟢 **Passed**: 所有任务成功
- 🔴 **Failed**: 有任务失败
- 🟡 **Running**: 正在执行
- ⚪ **Pending**: 等待执行
- 🔵 **Manual**: 需要手动触发
- ⚫ **Canceled**: 已取消

#### 下载构建产物

1. 进入Pipeline详情页
2. 点击右侧的"Download"按钮
3. 选择要下载的artifacts


## 配置构建触发器

### Jenkins触发器配置

#### 1. GitHub Webhook配置

**在GitHub仓库中配置**:

1. 进入GitHub仓库
2. 点击"Settings" → "Webhooks" → "Add webhook"
3. 填写信息:
   - Payload URL: `http://your-jenkins-url:8080/github-webhook/`
   - Content type: `application/json`
   - Secret: （可选）设置一个密钥
   - Which events: 选择"Just the push event"
4. 点击"Add webhook"

**在Jenkins中配置**:

1. 进入任务配置
2. 在"Build Triggers"部分
3. 勾选"GitHub hook trigger for GITScm polling"
4. 保存配置

现在，每次推送代码到GitHub，Jenkins会自动触发构建。

#### 2. 定时构建

在"Build Triggers"部分，勾选"Build periodically"

**Cron语法**:
```
分钟 小时 日 月 星期
```

**示例**:
```bash
# 每天凌晨2点构建
0 2 * * *

# 每小时构建一次
0 * * * *

# 每周一早上9点构建
0 9 * * 1

# 每15分钟构建一次
H/15 * * * *
```

**H符号**: Jenkins使用H（Hash）来分散负载，避免所有任务同时执行。

#### 3. 轮询SCM

在"Build Triggers"部分，勾选"Poll SCM"

```bash
# 每5分钟检查一次代码变化
H/5 * * * *

# 每小时检查一次
H * * * *
```

**注意**: 轮询会增加服务器负载，推荐使用Webhook方式。

#### 4. 参数化构建

允许用户在触发构建时选择参数。

1. 勾选"This project is parameterized"
2. 点击"Add Parameter"
3. 选择参数类型:

**String Parameter**:
```
Name: TARGET_BOARD
Default Value: STM32F4
Description: 目标开发板
```

**Choice Parameter**:
```
Name: BUILD_TYPE
Choices:
  Debug
  Release
Description: 构建类型
```

**Boolean Parameter**:
```
Name: RUN_TESTS
Default Value: true
Description: 是否运行测试
```

在构建脚本中使用参数:
```bash
echo "目标板: $TARGET_BOARD"
echo "构建类型: $BUILD_TYPE"

if [ "$RUN_TESTS" = "true" ]; then
    make test
fi
```


### GitLab CI触发器配置

#### 1. Push触发（默认）

默认情况下，推送代码会触发CI。可以通过 `only` 和 `except` 控制:

```yaml
build:
  script:
    - make all
  only:
    - main
    - develop
  except:
    - tags
```

#### 2. Merge Request触发

```yaml
build:
  script:
    - make all
  only:
    - merge_requests
```

#### 3. Tag触发

```yaml
release:
  script:
    - make release
  only:
    - tags
```

#### 4. 定时触发

在GitLab界面配置:

1. 进入项目
2. "CI/CD" → "Schedules"
3. 点击"New schedule"
4. 填写信息:
   - Description: `Nightly Build`
   - Interval Pattern: `0 2 * * *`（每天凌晨2点）
   - Target Branch: `main`
5. 点击"Save pipeline schedule"

#### 5. 手动触发

```yaml
deploy:
  script:
    - echo "部署..."
  when: manual
```

#### 6. 条件触发

使用 `rules` 实现复杂的触发条件:

```yaml
build:
  script:
    - make all
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'
    - if: '$CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "main"'
```


## 配置通知机制

### Jenkins邮件通知

#### 配置SMTP服务器

1. 进入 "Manage Jenkins" → "Configure System"
2. 找到"E-mail Notification"部分
3. 填写SMTP服务器信息:

**Gmail示例**:
```
SMTP server: smtp.gmail.com
Use SMTP Authentication: ☑
User Name: your-email@gmail.com
Password: your-app-password
Use SSL: ☑
SMTP Port: 465
```

**企业邮箱示例**:
```
SMTP server: smtp.company.com
Use SMTP Authentication: ☑
User Name: jenkins@company.com
Password: your-password
Use SSL: ☑
SMTP Port: 465
```

4. 测试配置:
   - Test e-mail recipient: `your-email@example.com`
   - 点击"Test configuration"

#### 配置Extended E-mail

1. 在"Extended E-mail Notification"部分
2. 配置默认收件人: `team@example.com`
3. 配置邮件模板:

**成功邮件模板**:
```
Subject: ✓ 构建成功 - ${PROJECT_NAME} #${BUILD_NUMBER}

Body:
项目: ${PROJECT_NAME}
构建编号: ${BUILD_NUMBER}
状态: 成功
分支: ${GIT_BRANCH}
提交: ${GIT_COMMIT}
作者: ${GIT_AUTHOR_NAME}

查看详情: ${BUILD_URL}
```

**失败邮件模板**:
```
Subject: ✗ 构建失败 - ${PROJECT_NAME} #${BUILD_NUMBER}

Body:
项目: ${PROJECT_NAME}
构建编号: ${BUILD_NUMBER}
状态: 失败
分支: ${GIT_BRANCH}
提交: ${GIT_COMMIT}
作者: ${GIT_AUTHOR_NAME}

错误日志: ${BUILD_URL}console
```

#### 在任务中配置邮件

在任务配置的"Post-build Actions"中:

1. 添加"Editable Email Notification"
2. 配置触发条件:
   - ☑ Failure - Any
   - ☑ Success
   - ☑ Unstable - Any
3. 配置收件人:
   - To: `$DEFAULT_RECIPIENTS, ${GIT_AUTHOR_EMAIL}`


### GitLab邮件通知

GitLab默认会发送邮件通知，可以在个人设置中配置:

1. 点击右上角头像 → "Preferences"
2. 左侧菜单选择"Notifications"
3. 配置通知级别:
   - **Global**: 全局设置
   - **Watch**: 接收所有通知
   - **Participate**: 只接收参与的通知
   - **Mention**: 只接收@提及的通知
   - **Disabled**: 禁用通知

### Slack集成

#### Jenkins Slack通知

1. 安装Slack Notification插件
2. 在Slack中创建Incoming Webhook
3. 在Jenkins中配置:
   - "Manage Jenkins" → "Configure System"
   - 找到"Slack"部分
   - Workspace: `your-workspace`
   - Credential: 添加Slack Token
   - Default channel: `#ci-notifications`

4. 在任务中添加Slack通知:
```groovy
post {
    success {
        slackSend (
            color: 'good',
            message: "✓ 构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
    failure {
        slackSend (
            color: 'danger',
            message: "✗ 构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
}
```

#### GitLab Slack通知

1. 进入项目 "Settings" → "Integrations"
2. 选择"Slack notifications"
3. 填写Webhook URL
4. 选择触发事件:
   - ☑ Push
   - ☑ Merge request
   - ☑ Pipeline
5. 点击"Save changes"


## 常见问题与解决方案

### Jenkins常见问题

#### 问题1: Jenkins无法启动

**症状**: 访问8080端口无响应

**解决方案**:
```bash
# 检查Jenkins服务状态
sudo systemctl status jenkins

# 查看Jenkins日志
sudo journalctl -u jenkins -f

# 检查端口占用
sudo netstat -tulpn | grep 8080

# 如果端口被占用，修改Jenkins端口
sudo vim /etc/default/jenkins
# 修改 HTTP_PORT=8080 为其他端口

# 重启Jenkins
sudo systemctl restart jenkins
```

#### 问题2: 构建失败 - 权限问题

**症状**: `Permission denied` 错误

**解决方案**:
```bash
# 将Jenkins用户添加到docker组
sudo usermod -aG docker jenkins

# 重启Jenkins
sudo systemctl restart jenkins

# 或者修改文件权限
sudo chown -R jenkins:jenkins /var/lib/jenkins
```

#### 问题3: 插件安装失败

**症状**: 插件下载超时或失败

**解决方案**:
```bash
# 方法1: 更换插件源
# 进入 Manage Jenkins → Manage Plugins → Advanced
# Update Site: https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json

# 方法2: 手动下载插件
# 1. 从 https://plugins.jenkins.io/ 下载.hpi文件
# 2. 上传到 Manage Jenkins → Manage Plugins → Advanced → Upload Plugin
```

#### 问题4: 构建卡住不动

**症状**: 构建一直处于运行状态

**解决方案**:
```bash
# 检查是否有交互式命令
# 避免使用需要用户输入的命令

# 检查是否有长时间运行的进程
# 添加超时设置
timeout: 30  # 30分钟超时
```

### GitLab CI常见问题

#### 问题1: Runner无法连接

**症状**: Runner显示离线

**解决方案**:
```bash
# 检查Runner状态
sudo gitlab-runner status

# 重启Runner
sudo gitlab-runner restart

# 检查网络连接
ping gitlab.com

# 检查配置文件
sudo cat /etc/gitlab-runner/config.toml

# 重新注册Runner
sudo gitlab-runner unregister --all-runners
sudo gitlab-runner register
```

#### 问题2: Pipeline一直Pending

**症状**: 任务一直等待，不执行

**解决方案**:
```yaml
# 检查tags是否匹配
# 确保任务的tags与Runner的tags一致

build:
  tags:
    - docker  # 确保Runner有这个tag
  script:
    - make all

# 或者允许Runner运行无tag的任务
# 在Runner配置中设置 run_untagged = true
```

#### 问题3: Docker镜像拉取失败

**症状**: `Error response from daemon: pull access denied`

**解决方案**:
```yaml
# 方法1: 使用公共镜像
image: gcc:latest

# 方法2: 配置镜像仓库认证
# 在GitLab项目中添加变量:
# CI_REGISTRY_USER
# CI_REGISTRY_PASSWORD

before_script:
  - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD

# 方法3: 使用国内镜像源
image: registry.cn-hangzhou.aliyuncs.com/library/gcc:latest
```

#### 问题4: 构建产物丢失

**症状**: 后续任务找不到前面任务的产物

**解决方案**:
```yaml
# 确保使用dependencies或needs

build:
  stage: build
  artifacts:
    paths:
      - build/
    expire_in: 1 hour

test:
  stage: test
  dependencies:
    - build  # 明确指定依赖
  script:
    - ls build/  # 现在可以访问build目录
```


## 最佳实践

### CI/CD设计原则

#### 1. 快速反馈

**目标**: 构建应该在10分钟内完成

**实践**:
- 使用增量编译
- 并行执行任务
- 缓存依赖和中间产物
- 优化测试执行时间

```yaml
# GitLab CI缓存示例
build:
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .cache/
      - build/obj/
  script:
    - make all
```

#### 2. 保持构建简单

**原则**: 一个任务只做一件事

**示例**:
```yaml
stages:
  - build    # 只负责编译
  - test     # 只负责测试
  - deploy   # 只负责部署

# 不要在一个任务中混合多个职责
```

#### 3. 构建应该是幂等的

**含义**: 相同的输入应该产生相同的输出

**实践**:
- 使用固定版本的依赖
- 清理构建环境
- 避免依赖外部状态

```bash
# 每次构建前清理
make clean
rm -rf build/

# 使用固定版本
apt-get install -y gcc-arm-none-eabi=10.3.1
```

#### 4. 版本化所有配置

**实践**:
- CI配置文件纳入版本控制
- 构建脚本纳入版本控制
- 依赖版本明确指定

```yaml
# .gitlab-ci.yml
image: gcc:10.3.0  # 明确版本，不使用latest
```

#### 5. 失败快速

**原则**: 尽早发现问题，尽早失败

**实践**:
```bash
#!/bin/bash
set -e  # 任何命令失败立即退出

# 先执行快速检查
make lint
make format-check

# 再执行耗时的编译
make all

# 最后执行测试
make test
```

### 安全最佳实践

#### 1. 保护敏感信息

**不要在代码中硬编码密码**:

```yaml
# ❌ 错误做法
script:
  - scp firmware.bin user:password@server:/path/

# ✅ 正确做法 - 使用环境变量
script:
  - scp firmware.bin $DEPLOY_USER:$DEPLOY_PASSWORD@$DEPLOY_SERVER:/path/
```

**Jenkins凭据管理**:
1. "Manage Jenkins" → "Manage Credentials"
2. 添加凭据（用户名密码、SSH密钥等）
3. 在任务中引用凭据ID

**GitLab CI/CD变量**:
1. "Settings" → "CI/CD" → "Variables"
2. 添加变量，勾选"Masked"和"Protected"
3. 在.gitlab-ci.yml中使用 `$VARIABLE_NAME`

#### 2. 限制权限

**Jenkins**:
- 启用基于角色的访问控制（RBAC）
- 不同团队使用不同的凭据
- 定期审查权限

**GitLab**:
- 使用Protected Branches
- 使用Protected Tags
- 限制Runner的访问权限

#### 3. 审计日志

**启用审计**:
- 记录所有构建活动
- 记录配置更改
- 定期审查日志

### 性能优化

#### 1. 使用缓存

**Jenkins**:
```groovy
pipeline {
    agent any
    options {
        // 保留最近10次构建
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
}
```

**GitLab CI**:
```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/
    - node_modules/
    - build/obj/
```

#### 2. 并行执行

**Jenkins**:
```groovy
stage('Parallel Build') {
    parallel {
        stage('STM32F4') {
            steps {
                sh 'make TARGET=STM32F4'
            }
        }
        stage('STM32F7') {
            steps {
                sh 'make TARGET=STM32F7'
            }
        }
    }
}
```

**GitLab CI**:
```yaml
build_stm32f4:
  stage: build
  script:
    - make TARGET=STM32F4

build_stm32f7:
  stage: build
  script:
    - make TARGET=STM32F7
```

#### 3. 增量构建

```makefile
# Makefile支持增量编译
.PHONY: all clean

# 只重新编译修改的文件
all: $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```


## 实战演练

### 演练1: 搭建完整的Jenkins环境

**目标**: 从零开始搭建Jenkins并创建第一个构建任务

**步骤**:

1. **安装Jenkins**（使用Docker）:
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

2. **初始配置**:
   - 访问 http://localhost:8080
   - 输入初始密码
   - 安装推荐插件
   - 创建管理员账户

3. **安装必要插件**:
   - Git plugin
   - Pipeline
   - Blue Ocean

4. **创建测试项目**:
   - 新建Freestyle项目
   - 配置Git仓库
   - 添加构建脚本
   - 执行构建

5. **验证**:
   - 检查构建日志
   - 下载构建产物
   - 查看构建历史

### 演练2: 配置GitLab CI流水线

**目标**: 为嵌入式项目配置完整的CI/CD流水线

**步骤**:

1. **准备项目**:
```bash
# 创建测试项目
mkdir stm32-ci-demo
cd stm32-ci-demo
git init

# 创建简单的Makefile
cat > Makefile << 'EOF'
all:
	@echo "Building firmware..."
	@mkdir -p build
	@echo "Firmware built successfully" > build/firmware.bin

test:
	@echo "Running tests..."
	@echo "All tests passed"

clean:
	@rm -rf build/
EOF

# 提交代码
git add Makefile
git commit -m "Initial commit"
```

2. **创建.gitlab-ci.yml**:
```yaml
stages:
  - build
  - test

build:
  stage: build
  script:
    - make all
  artifacts:
    paths:
      - build/
    expire_in: 1 day

test:
  stage: test
  dependencies:
    - build
  script:
    - make test
```

3. **推送到GitLab**:
```bash
git remote add origin https://gitlab.com/username/stm32-ci-demo.git
git push -u origin main
```

4. **配置Runner**:
```bash
# 安装Runner
sudo apt install gitlab-runner

# 注册Runner
sudo gitlab-runner register
```

5. **验证流水线**:
   - 在GitLab查看Pipeline
   - 检查每个任务的日志
   - 下载构建产物

### 演练3: 集成代码质量检查

**目标**: 在CI中集成静态代码分析

**Jenkins Pipeline**:
```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/username/project.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'make all'
            }
        }
        
        stage('Code Quality') {
            steps {
                sh 'cppcheck --enable=all --xml src/ 2> cppcheck.xml'
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'cppcheck.xml',
                    reportName: 'Cppcheck Report'
                ])
            }
        }
        
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
    }
}
```

**GitLab CI**:
```yaml
stages:
  - build
  - quality
  - test

build:
  stage: build
  script:
    - make all
  artifacts:
    paths:
      - build/

code_quality:
  stage: quality
  image: cppcheck:latest
  script:
    - cppcheck --enable=all --xml src/ 2> cppcheck.xml
  artifacts:
    paths:
      - cppcheck.xml
  allow_failure: true

test:
  stage: test
  dependencies:
    - build
  script:
    - make test
```


## 进阶主题

### Docker化CI环境

#### 创建自定义构建镜像

**Dockerfile示例**:
```dockerfile
FROM ubuntu:22.04

# 安装基础工具
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 安装ARM工具链
RUN wget https://developer.arm.com/-/media/Files/downloads/gnu-rm/10.3-2021.10/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 \
    && tar -xjf gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 -C /opt/ \
    && rm gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2

# 设置环境变量
ENV PATH="/opt/gcc-arm-none-eabi-10.3-2021.10/bin:${PATH}"

# 安装Python工具
RUN pip3 install pytest pyserial

# 设置工作目录
WORKDIR /workspace

# 验证安装
RUN arm-none-eabi-gcc --version
```

**构建镜像**:
```bash
docker build -t arm-toolchain:latest .
```

**在CI中使用**:
```yaml
# .gitlab-ci.yml
build:
  image: arm-toolchain:latest
  script:
    - make all
```

### 多分支流水线

#### Jenkins多分支Pipeline

1. 创建"Multibranch Pipeline"项目
2. 配置Branch Sources（Git）
3. Jenkins会自动为每个分支创建Pipeline

**Jenkinsfile**:
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        sh 'make BUILD_TYPE=Release'
                    } else {
                        sh 'make BUILD_TYPE=Debug'
                    }
                }
            }
        }
    }
}
```

#### GitLab分支策略

```yaml
# 主分支 - 完整流程
build_main:
  script:
    - make BUILD_TYPE=Release
  only:
    - main

# 开发分支 - 快速验证
build_develop:
  script:
    - make BUILD_TYPE=Debug
  only:
    - develop

# 功能分支 - 基础检查
build_feature:
  script:
    - make lint
    - make build
  only:
    - /^feature\/.*/
```

### CI/CD监控

#### Jenkins监控

**安装Prometheus插件**:
1. 安装"Prometheus metrics"插件
2. 访问 `http://jenkins:8080/prometheus/`
3. 配置Prometheus抓取指标

**关键指标**:
- 构建成功率
- 构建时长
- 队列等待时间
- 节点使用率

#### GitLab CI监控

**内置监控**:
1. "CI/CD" → "Pipelines" → "Charts"
2. 查看:
   - Pipeline成功率
   - Pipeline时长趋势
   - 任务失败统计

### 成本优化

#### 减少构建时间

1. **使用缓存**:
```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/
    - build/obj/
```

2. **并行执行**:
```yaml
test:
  parallel: 4
  script:
    - make test
```

3. **增量构建**:
```bash
# 只编译修改的文件
make -j4
```

#### 优化Runner使用

1. **使用标签分类**:
```yaml
build:
  tags:
    - docker
    - fast

deploy:
  tags:
    - production
```

2. **限制并发**:
```toml
# config.toml
concurrent = 4  # 最多同时运行4个任务
```

3. **自动清理**:
```yaml
after_script:
  - rm -rf build/
  - docker system prune -f
```


## 总结

通过本教程，你已经学习了:

### 核心知识点

- ✅ **CI/CD概念**: 理解持续集成和持续部署的价值
- ✅ **工具选择**: 了解主流CI工具的特点和适用场景
- ✅ **Jenkins搭建**: 掌握Jenkins的安装、配置和使用
- ✅ **GitLab CI**: 掌握GitLab CI/CD的配置和流水线设计
- ✅ **触发器配置**: 学会配置各种构建触发方式
- ✅ **通知机制**: 配置邮件和Slack通知
- ✅ **最佳实践**: 了解CI/CD的设计原则和优化方法

### 关键要点

1. **选择合适的工具**:
   - Jenkins: 功能强大，适合复杂场景
   - GitLab CI: 配置简单，与GitLab深度集成

2. **自动化一切**:
   - 编译构建自动化
   - 测试自动化
   - 部署自动化
   - 通知自动化

3. **快速反馈**:
   - 构建应该快速完成（< 10分钟）
   - 失败应该快速通知
   - 问题应该快速定位

4. **持续改进**:
   - 定期审查CI流程
   - 优化构建时间
   - 提高构建成功率
   - 收集团队反馈

### 下一步学习

完成本教程后，建议继续学习:

1. **持续部署流程设计**: 学习如何自动化部署流程
2. **自动化测试集成**: 深入学习测试自动化
3. **DevOps最佳实践**: 了解完整的DevOps工作流
4. **容器化与编排**: 学习Docker和Kubernetes
5. **监控与日志**: 学习应用监控和日志分析

### 实践建议

1. **从简单开始**: 先搭建基础的构建流程
2. **逐步完善**: 逐步添加测试、质量检查等
3. **持续优化**: 根据实际情况优化流程
4. **团队协作**: 与团队一起制定CI/CD规范
5. **文档记录**: 记录CI/CD配置和流程

### 常用资源

**官方文档**:
- [Jenkins官方文档](https://www.jenkins.io/doc/)
- [GitLab CI/CD文档](https://docs.gitlab.com/ee/ci/)
- [Docker官方文档](https://docs.docker.com/)

**学习资源**:
- [Jenkins Pipeline教程](https://www.jenkins.io/doc/book/pipeline/)
- [GitLab CI/CD示例](https://docs.gitlab.com/ee/ci/examples/)
- [CI/CD最佳实践](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)

**社区支持**:
- [Jenkins社区](https://community.jenkins.io/)
- [GitLab论坛](https://forum.gitlab.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/jenkins)

记住：CI/CD不是一次性的工作，而是需要持续维护和优化的过程。随着项目的发展，你的CI/CD流程也应该不断演进。


## 练习题

### 练习1: Jenkins基础配置

**任务**: 搭建Jenkins环境并创建第一个构建任务

**要求**:
1. 使用Docker安装Jenkins
2. 安装Git和Pipeline插件
3. 创建一个Freestyle项目
4. 配置Git仓库
5. 添加简单的构建脚本
6. 执行构建并查看日志

**验证**:
- Jenkins能够正常访问
- 构建任务能够成功执行
- 能够查看构建历史和日志

### 练习2: GitLab CI配置

**任务**: 为项目配置GitLab CI流水线

**要求**:
1. 创建.gitlab-ci.yml文件
2. 定义build和test两个阶段
3. 配置artifacts保存构建产物
4. 推送代码触发流水线
5. 查看流水线执行结果

**验证**:
- 流水线能够自动触发
- 所有任务都能成功执行
- 能够下载构建产物

### 练习3: 配置构建触发器

**任务**: 配置多种构建触发方式

**要求**:
1. 配置GitHub Webhook触发
2. 配置定时构建（每天凌晨2点）
3. 配置轮询SCM（每5分钟）
4. 测试各种触发方式

**验证**:
- 推送代码能够触发构建
- 定时构建能够按时执行
- 轮询能够检测到代码变化

### 练习4: 集成邮件通知

**任务**: 配置构建结果邮件通知

**要求**:
1. 配置SMTP服务器
2. 配置邮件模板
3. 配置成功和失败通知
4. 测试邮件发送

**验证**:
- 构建成功时收到邮件
- 构建失败时收到邮件
- 邮件内容包含构建信息

### 练习5: 多平台构建

**任务**: 配置多个目标平台的并行构建

**要求**:
1. 配置STM32F4构建
2. 配置STM32F7构建
3. 配置ESP32构建
4. 使用并行执行

**验证**:
- 三个平台能够并行构建
- 每个平台生成独立的固件
- 构建时间明显缩短

## 参考资料

### 配置文件示例

**Jenkins Declarative Pipeline**:
```groovy
pipeline {
    agent any
    
    environment {
        ARM_TOOLCHAIN = '/usr/local/gcc-arm-none-eabi/bin'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make all'
            }
        }
        
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
    }
    
    post {
        success {
            archiveArtifacts 'build/*.bin'
        }
        failure {
            mail to: 'team@example.com',
                 subject: "Build Failed: ${env.JOB_NAME}",
                 body: "Build failed. Check ${env.BUILD_URL}"
        }
    }
}
```

**GitLab CI完整示例**:
```yaml
stages:
  - build
  - test
  - deploy

variables:
  GIT_SUBMODULE_STRATEGY: recursive

before_script:
  - echo "Starting CI/CD pipeline..."

build:
  stage: build
  image: gcc:latest
  script:
    - make clean
    - make all -j4
  artifacts:
    paths:
      - build/
    expire_in: 1 week
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .cache/
  only:
    - main
    - develop
  tags:
    - docker

test:
  stage: test
  image: gcc:latest
  dependencies:
    - build
  script:
    - make test
  artifacts:
    reports:
      junit: test-results.xml
  only:
    - main
    - develop
  tags:
    - docker

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying..."
  environment:
    name: production
    url: http://example.com
  only:
    - main
  when: manual
  tags:
    - docker
```

### 相关命令速查

**Jenkins CLI**:
```bash
# 重启Jenkins
java -jar jenkins-cli.jar -s http://localhost:8080/ restart

# 安装插件
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin git

# 列出任务
java -jar jenkins-cli.jar -s http://localhost:8080/ list-jobs
```

**GitLab Runner**:
```bash
# 查看Runner状态
gitlab-runner status

# 启动Runner
gitlab-runner start

# 停止Runner
gitlab-runner stop

# 重启Runner
gitlab-runner restart

# 注册Runner
gitlab-runner register

# 注销Runner
gitlab-runner unregister --all-runners

# 验证配置
gitlab-runner verify
```

**Docker**:
```bash
# 查看容器
docker ps

# 查看日志
docker logs jenkins

# 进入容器
docker exec -it jenkins bash

# 停止容器
docker stop jenkins

# 启动容器
docker start jenkins

# 删除容器
docker rm jenkins
```

---

**作者**: 嵌入式知识平台  
**最后更新**: 2024-01-15  
**版本**: 1.0  
**许可**: CC BY-NC-SA 4.0
