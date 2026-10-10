---
title: "lwIP协议栈移植与应用开发"
description: "深入学习lwIP轻量级TCP/IP协议栈的架构原理、移植方法、配置优化和实战应用，掌握嵌入式系统网络通信开发技术"
slug: "lwip-stack-porting-guide"

# 分类信息
domain: "通信与网络"
module: "网络协议"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - lwIP
  - TCP/IP协议栈
  - 网络编程
  - 以太网
  - 嵌入式网络
prerequisites:
  - "01-websocket.md"
  - "../../01-wireless-communication/intermediate/01-wifi-basics.md"
related_contents:
  - "05-modbus-tcp.md"
  - "03-can-protocol.md"

# 学习信息
estimated_time: 120
difficulty_score: 4

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-04-05"
updated_at: "2026-04-05"
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
  - lwIP协议栈
  - TCP/IP移植
  - 嵌入式网络
  - 以太网驱动
  - Socket编程
cover_image: ""
---

# lwIP协议栈移植与应用开发

## 学习目标

完成本教程后，你将能够：

- [ ] 理解lwIP协议栈的架构设计和工作原理
- [ ] 掌握lwIP在不同平台上的移植方法
- [ ] 熟悉lwIP的内存管理和线程模型
- [ ] 能够配置和优化lwIP性能参数
- [ ] 使用lwIP API进行网络应用开发
- [ ] 集成以太网驱动和实现网络通信
- [ ] 调试和解决lwIP常见问题

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 熟悉TCP/IP协议基础知识
- 了解C语言编程和指针操作
- 理解操作系统基本概念（任务、信号量、互斥锁）
- 掌握嵌入式系统开发基础

**技能要求**：
- 能够使用STM32CubeMX或类似工具配置外设
- 会使用调试工具（JTAG/SWD、串口）
- 了解以太网硬件接口（MAC/PHY）
- 熟悉RTOS基本使用（FreeRTOS或其他）

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| STM32开发板 | 1 | 带以太网MAC的MCU | STM32F407/F429/H743 |
| 以太网PHY模块 | 1 | 物理层收发器 | LAN8720/DP83848 |
| 网线 | 1 | Cat5e或更高 | - |
| 路由器/交换机 | 1 | 用于网络连接 | - |
| USB调试器 | 1 | ST-Link V2或J-Link | - |
| Micro USB线 | 1 | 供电和串口调试 | - |

### 软件准备

- **开发环境**：
  - STM32CubeIDE 1.10+ 或 Keil MDK 5.36+
  - STM32CubeMX 6.6+（用于配置生成）
  - Git（用于获取lwIP源码）
- **lwIP源码**：
  - lwIP 2.1.3或更高版本
  - 官方仓库：https://git.savannah.nongnu.org/git/lwip.git
- **调试工具**：
  - Wireshark（网络抓包分析）
  - Tera Term或PuTTY（串口调试）
  - Ping/Telnet/HTTP客户端工具

### 环境配置

#### 1. 安装STM32开发环境

```bash
# 下载STM32CubeIDE
# 访问 https://www.st.com/stm32cubeide
# 安装对应操作系统版本

# 安装STM32CubeMX（如果单独使用）
# 访问 https://www.st.com/stm32cubemx
```

#### 2. 获取lwIP源码

```bash
# 克隆lwIP官方仓库
git clone https://git.savannah.nongnu.org/git/lwip.git
cd lwip
git checkout STABLE-2_1_3_RELEASE

# 或者下载压缩包
wget http://download.savannah.nongnu.org/releases/lwip/lwip-2.1.3.zip
unzip lwip-2.1.3.zip
```

#### 3. 安装Wireshark

```bash
# Ubuntu/Debian
sudo apt-get install wireshark

# Windows
# 访问 https://www.wireshark.org/download.html
# 下载并安装

# macOS
brew install wireshark
```

## lwIP协议栈概述

### 什么是lwIP？

lwIP（Lightweight IP）是一个开源的轻量级TCP/IP协议栈，专为嵌入式系统设计。由瑞典计算机科学研究所（SICS）的Adam Dunkels开发，现在由社区维护。

**核心特点**：
- **轻量级**：代码量小（约40KB），RAM需求低（几十KB）
- **完整性**：实现了完整的TCP/IP协议族
- **可移植性**：易于移植到各种嵌入式平台
- **灵活性**：支持多种API接口和配置选项
- **开源免费**：BSD许可证，可商用

### lwIP支持的协议

| 协议层 | 支持的协议 |
|--------|-----------|
| 应用层 | HTTP, HTTPS, SMTP, SNMP, TFTP, DNS, DHCP, mDNS |
| 传输层 | TCP, UDP, UDP-Lite |
| 网络层 | IPv4, IPv6, ICMP, ICMPv6, IGMP |
| 链路层 | ARP, Ethernet, PPP, PPPoE, 6LoWPAN |

### lwIP版本历史

| 版本 | 发布时间 | 主要特性 |
|------|----------|----------|
| 0.1 | 2001 | 初始版本，基本TCP/IP功能 |
| 1.0 | 2003 | 稳定版本，广泛应用 |
| 1.4.1 | 2012 | 性能优化，IPv6支持 |
| 2.0.0 | 2015 | 架构重构，API改进 |
| 2.1.0 | 2018 | 安全增强，性能提升 |
| 2.1.3 | 2021 | 当前稳定版本 |

### lwIP应用场景

- **工业控制**：PLC、HMI、工业网关
- **物联网设备**：智能家居、传感器节点
- **网络设备**：路由器、交换机、网关
- **消费电子**：打印机、摄像头、音响
- **汽车电子**：车载娱乐、诊断系统

## lwIP架构设计

### 整体架构

```text
+----------------------------------------------------------+
|                    应用程序                                |
+----------------------------------------------------------+
|                    应用层API                               |
|  +------------------+  +------------------+               |
|  |  Socket API      |  |  Netconn API     |               |
|  +------------------+  +------------------+               |
|  |           Raw API (Callback)           |               |
+----------------------------------------------------------+
|                    协议栈核心                              |
|  +------------------+  +------------------+               |
|  |       TCP        |  |       UDP        |               |
|  +------------------+  +------------------+               |
|  |                   IP层                  |               |
|  +------------------+  +------------------+               |
|  |       ARP        |  |      ICMP        |               |
+----------------------------------------------------------+
|                    网络接口层                              |
|  +------------------+  +------------------+               |
|  |   Ethernet IF    |  |     PPP IF       |               |
+----------------------------------------------------------+
|                    硬件驱动层                              |
|  +------------------+  +------------------+               |
|  |    MAC Driver    |  |    PHY Driver    |               |
+----------------------------------------------------------+
```

### 核心模块

#### 1. 协议栈核心（Core）

**IP模块**：
- IP数据包的接收和发送
- IP分片和重组
- IP路由选择
- 支持IPv4和IPv6

**TCP模块**：
- 可靠的面向连接传输
- 流量控制和拥塞控制
- 超时重传机制
- 滑动窗口协议

**UDP模块**：
- 无连接的数据报传输
- 轻量级，开销小
- 支持广播和组播

**ICMP模块**：
- Ping功能实现
- 错误报告和诊断
- 路径MTU发现

#### 2. API接口层

**Raw API（回调API）**：
- 最底层的API接口
- 基于回调函数机制
- 零拷贝，性能最高
- 适合资源受限的系统
- 编程复杂度较高

**Netconn API**：
- 基于消息传递的API
- 需要操作系统支持
- 使用更简单
- 性能略低于Raw API

**Socket API**：
- 标准BSD Socket接口
- 兼容性最好
- 需要操作系统支持
- 适合移植现有应用

#### 3. 网络接口层（Netif）

- 抽象的网络接口
- 支持多个网络接口
- 处理链路层协议
- 管理MAC地址和IP地址

#### 4. 内存管理

**三种内存池**：

1. **Heap内存池**：
   - 使用标准C库的malloc/free
   - 灵活但可能产生碎片
   - 适合内存充足的系统

2. **Pool内存池**：
   - 固定大小的内存块
   - 无碎片，分配快速
   - 适合实时系统

3. **Pbuf内存池**：
   - 专门用于数据包缓冲
   - 支持链式缓冲区
   - 零拷贝优化

### lwIP线程模型

#### 1. NO_SYS模式（无操作系统）

```text
主循环:
  while(1) {
    检查网络接口
    处理接收数据
    处理定时器
    处理应用逻辑
  }
```

**特点**：
- 不需要操作系统
- 单线程运行
- 只能使用Raw API
- 资源占用最小

#### 2. RTOS模式（有操作系统）

```text
线程1: tcpip_thread
  - 处理协议栈核心逻辑
  - 接收来自驱动的数据包
  - 处理定时器事件

线程2: ethernetif_input
  - 从网卡接收数据
  - 将数据包传递给tcpip_thread

线程3-N: 应用线程
  - 使用Netconn或Socket API
  - 通过消息队列与tcpip_thread通信
```

**特点**：
- 需要RTOS支持
- 多线程并发
- 支持所有API
- 更好的实时性

### lwIP数据包处理流程

#### 接收流程

```text
1. 网卡中断 → 驱动接收数据
2. 驱动分配pbuf → 复制数据到pbuf
3. 调用netif->input() → 传递给IP层
4. IP层处理 → 检查目的地址、分片重组
5. 传输层处理 → TCP/UDP协议处理
6. 应用层回调 → 通知应用程序
```

#### 发送流程

```text
1. 应用调用发送函数 → 传递数据
2. 传输层处理 → 添加TCP/UDP头
3. IP层处理 → 添加IP头、路由选择
4. ARP解析 → 获取目的MAC地址
5. 链路层处理 → 添加以太网头
6. 驱动发送 → 通过网卡发送数据
```

## 步骤1：STM32硬件准备

### 1.1 以太网硬件架构

```text
+-------------+     RMII/MII      +-------------+     RJ45      +----------+
|   STM32     |<----------------->|  PHY芯片    |<------------->|  网线    |
| (MAC控制器) |                   | (LAN8720)   |               |          |
+-------------+                   +-------------+               +----------+
```

**MAC（Media Access Control）**：
- 集成在STM32内部
- 负责数据帧的组装和解析
- 实现CSMA/CD协议
- 支持RMII/MII接口

**PHY（Physical Layer）**：
- 外部独立芯片
- 负责物理信号的收发
- 实现编码解码
- 常用芯片：LAN8720、DP83848、RTL8201

### 1.2 RMII接口信号

| 信号名 | 方向 | 说明 |
|--------|------|------|
| REF_CLK | PHY→MAC | 50MHz参考时钟 |
| TXD0/TXD1 | MAC→PHY | 发送数据（2位） |
| TX_EN | MAC→PHY | 发送使能 |
| RXD0/RXD1 | PHY→MAC | 接收数据（2位） |
| CRS_DV | PHY→MAC | 载波侦听/数据有效 |
| MDIO | 双向 | 管理数据输入输出 |
| MDC | MAC→PHY | 管理时钟 |

### 1.3 STM32F407引脚连接

| STM32引脚 | 功能 | LAN8720引脚 |
|-----------|------|-------------|
| PA1 | ETH_RMII_REF_CLK | REFCLK |
| PA2 | ETH_MDIO | MDIO |
| PC1 | ETH_MDC | MDC |
| PA7 | ETH_RMII_CRS_DV | CRS_DV |
| PC4 | ETH_RMII_RXD0 | RXD0 |
| PC5 | ETH_RMII_RXD1 | RXD1 |
| PG11 | ETH_RMII_TX_EN | TXEN |
| PG13 | ETH_RMII_TXD0 | TXD0 |
| PG14 | ETH_RMII_TXD1 | TXD1 |

**注意事项**：
- REF_CLK必须由PHY提供（外部时钟模式）
- 需要配置PHY的时钟输出模式
- 某些引脚可能与其他外设复用，需要注意冲突

### 1.4 硬件电路设计要点

#### PHY电源设计

```text
3.3V ──┬── 10μF ──┬── LAN8720 VDD
       │          │
       └── 0.1μF ─┘

1.2V ── 10μF ── 0.1μF ── LAN8720 VDDCR (内核电压)
```

#### 晶振电路

```text
        ┌─────────┐
25MHz ──┤ Crystal ├── LAN8720 XTAL1/XTAL2
        └─────────┘
         │       │
        22pF    22pF
         │       │
        GND     GND
```

#### 网络变压器

- 必须使用网络变压器（隔离变压器）
- 提供电气隔离和共模抑制
- 推荐型号：HR911105A、HanRun等
- 集成RJ45接口和LED指示灯

#### PCB布线建议

1. **差分信号**：
   - TXD+/TXD-、RXD+/RXD-保持等长
   - 差分阻抗控制在100Ω±10%
   - 避免直角走线

2. **时钟信号**：
   - REF_CLK走线尽量短
   - 远离高速信号和电源
   - 可以串联22Ω电阻抑制振铃

3. **电源去耦**：
   - 每个电源引脚靠近放置0.1μF电容
   - 电源输入端放置10μF电容
   - 使用多层板，独立电源层和地层

## 步骤2：STM32CubeMX配置

### 2.1 创建新工程

1. 打开STM32CubeMX
2. 选择芯片型号：STM32F407ZGT6
3. 配置时钟：
   - HSE: 8MHz外部晶振
   - PLL: 168MHz系统时钟
   - HCLK: 168MHz
   - APB1: 42MHz
   - APB2: 84MHz

### 2.2 配置以太网外设

#### 启用ETH外设

1. 在Connectivity中选择ETH
2. Mode: RMII
3. 配置参数：
   - PHY Address: 0（LAN8720默认地址）
   - Media Interface: RMII
   - Auto Negotiation: Enabled
   - Checksum by Hardware: Enabled

#### 配置GPIO

CubeMX会自动配置以太网相关GPIO：
- PA1: ETH_RMII_REF_CLK
- PA2: ETH_MDIO
- PC1: ETH_MDC
- PA7: ETH_RMII_CRS_DV
- PC4: ETH_RMII_RXD0
- PC5: ETH_RMII_RXD1
- PG11: ETH_RMII_TX_EN
- PG13: ETH_RMII_TXD0
- PG14: ETH_RMII_TXD1

### 2.3 配置FreeRTOS

1. 在Middleware中启用FREERTOS
2. 配置参数：
   - Interface: CMSIS_V2
   - TOTAL_HEAP_SIZE: 15360 bytes
   - Minimal Stack Size: 128 words
   - Timer Task Stack Depth: 256 words

3. 创建默认任务：
   - Task Name: defaultTask
   - Priority: Normal
   - Stack Size: 128 words

### 2.4 配置lwIP

1. 在Middleware中启用LWIP
2. 配置General Settings：
   - LWIP_DHCP: Enabled（启用DHCP客户端）
   - LWIP_DNS: Enabled（启用DNS）
   - IP_ADDRESS: 192.168.1.100（静态IP，DHCP失败时使用）
   - NETMASK_ADDRESS: 255.255.255.0
   - GATEWAY_ADDRESS: 192.168.1.1

3. 配置Key Options：
   - MEM_SIZE: 10240（内存堆大小）
   - MEMP_NUM_PBUF: 10（pbuf数量）
   - MEMP_NUM_TCP_PCB: 5（TCP连接数）
   - MEMP_NUM_TCP_SEG: 8（TCP段数量）
   - PBUF_POOL_SIZE: 8（pbuf池大小）

4. 配置Checksum：
   - CHECKSUM_BY_HARDWARE: Enabled
   - CHECKSUM_GEN_IP: Disabled（硬件计算）
   - CHECKSUM_GEN_UDP: Disabled
   - CHECKSUM_GEN_TCP: Disabled
   - CHECKSUM_CHECK_IP: Disabled
   - CHECKSUM_CHECK_UDP: Disabled
   - CHECKSUM_CHECK_TCP: Disabled

### 2.5 生成代码

1. 配置Project Manager：
   - Project Name: lwip_demo
   - Toolchain: STM32CubeIDE
   - Generate peripheral initialization as pair of '.c/.h'

2. 点击"GENERATE CODE"生成工程

3. 生成的重要文件：
   - `Core/Src/main.c`: 主程序
   - `LWIP/App/lwip.c`: lwIP初始化
   - `LWIP/Target/ethernetif.c`: 以太网驱动接口
   - `Middlewares/Third_Party/LwIP/`: lwIP源码

## 步骤3：lwIP移植实现

### 3.1 理解ethernetif.c

`ethernetif.c`是lwIP与硬件驱动的接口层，主要包含：

#### 关键函数

```c
// 初始化网络接口
err_t ethernetif_init(struct netif *netif);

// 接收数据包（从网卡读取）
static void ethernetif_input(void *argument);

// 发送数据包（写入网卡）
static err_t low_level_output(struct netif *netif, struct pbuf *p);

// 初始化底层硬件
static void low_level_init(struct netif *netif);
```

### 3.2 修改PHY地址（如果需要）

在`ethernetif.c`中找到PHY地址定义：

```c
// LAN8720的默认地址通常是0或1
#define PHY_ADDRESS       0x00  // 根据硬件原理图确定
```

如果PHY地址不正确，会导致初始化失败。可以通过MDIO扫描所有地址：

```c
void PHY_Scan(void)
{
    uint32_t phyreg;
    for(uint8_t addr = 0; addr < 32; addr++)
    {
        if(HAL_ETH_ReadPHYRegister(&heth, addr, PHY_BCR, &phyreg) == HAL_OK)
        {
            printf("Found PHY at address: 0x%02X\r\n", addr);
        }
    }
}
```

### 3.3 配置PHY时钟模式

LAN8720需要配置为输出50MHz时钟给STM32：

```c
static void LAN8720_Init(void)
{
    uint32_t regvalue = 0;
    
    // 读取PHY特殊控制/状态寄存器
    HAL_ETH_ReadPHYRegister(&heth, PHY_ADDRESS, PHY_SR, &regvalue);
    
    // 配置为50MHz时钟输出模式
    regvalue |= (1 << 7);  // 设置时钟输出使能位
    HAL_ETH_WritePHYRegister(&heth, PHY_ADDRESS, PHY_SR, regvalue);
    
    // 软复位PHY
    HAL_ETH_WritePHYRegister(&heth, PHY_ADDRESS, PHY_BCR, PHY_RESET);
    
    // 等待复位完成
    HAL_Delay(100);
}
```

### 3.4 优化接收性能

#### 使用DMA接收

STM32的以太网MAC支持DMA，可以大幅提升性能：

```c
// 在ethernetif.c的low_level_init()中
static void low_level_init(struct netif *netif)
{
    // ... 其他初始化代码 ...
    
    // 配置DMA接收描述符
    HAL_ETH_DescriptorsConfigTypeDef dmaconf;
    dmaconf.RxDescLength = ETH_RX_DESC_CNT;
    dmaconf.TxDescLength = ETH_TX_DESC_CNT;
    dmaconf.RxBuffLen = 1536;  // 每个缓冲区大小
    
    HAL_ETH_DescriptorsConfig(&heth, &dmaconf);
    
    // 启动以太网
    HAL_ETH_Start(&heth);
}
```

#### 接收任务优化

```c
void ethernetif_input(void *argument)
{
    struct pbuf *p;
    struct netif *netif = (struct netif *) argument;
    
    for(;;)
    {
        // 等待接收信号量（由中断触发）
        if(osSemaphoreAcquire(RxPktSemaphore, osWaitForever) == osOK)
        {
            do
            {
                // 从网卡读取数据包
                p = low_level_input(netif);
                
                if(p != NULL)
                {
                    // 传递给lwIP协议栈
                    if(netif->input(p, netif) != ERR_OK)
                    {
                        pbuf_free(p);
                    }
                }
            } while(p != NULL);
        }
    }
}
```

### 3.5 实现零拷贝接收

为了提高性能，可以实现零拷贝接收：

```c
static struct pbuf *low_level_input(struct netif *netif)
{
    struct pbuf *p = NULL;
    ETH_BufferTypeDef RxBuff;
    uint32_t framelength = 0;
    
    // 获取接收到的数据帧
    if(HAL_ETH_GetRxDataBuffer(&heth, &RxBuff) == HAL_OK)
    {
        HAL_ETH_GetRxDataLength(&heth, &framelength);
        
        // 分配pbuf，使用PBUF_REF类型（引用外部缓冲区）
        p = pbuf_alloc(PBUF_RAW, framelength, PBUF_REF);
        
        if(p != NULL)
        {
            // 直接引用DMA缓冲区，避免拷贝
            p->payload = RxBuff.buffer;
            p->len = framelength;
        }
        
        // 构建接收描述符
        HAL_ETH_BuildRxDescriptors(&heth);
    }
    
    return p;
}
```

### 3.6 配置lwipopts.h

`lwipopts.h`是lwIP的配置文件，需要根据应用需求调整：

```c
// ========== 内存配置 ==========
#define MEM_ALIGNMENT           4           // 内存对齐（字节）
#define MEM_SIZE                (10*1024)   // 堆内存大小
#define MEMP_NUM_PBUF           10          // pbuf结构数量
#define MEMP_NUM_TCP_PCB        5           // TCP连接数
#define MEMP_NUM_TCP_PCB_LISTEN 5           // TCP监听连接数
#define MEMP_NUM_TCP_SEG        8           // TCP段数量
#define MEMP_NUM_UDP_PCB        4           // UDP连接数
#define PBUF_POOL_SIZE          8           // pbuf池大小
#define PBUF_POOL_BUFSIZE       1536        // pbuf缓冲区大小

// ========== TCP配置 ==========
#define TCP_MSS                 1460        // TCP最大段大小
#define TCP_WND                 (4*TCP_MSS) // TCP接收窗口
#define TCP_SND_BUF             (4*TCP_MSS) // TCP发送缓冲区
#define TCP_SND_QUEUELEN        (2*TCP_SND_BUF/TCP_MSS) // 发送队列长度

// ========== 性能优化 ==========
#define LWIP_CHECKSUM_ON_COPY   1           // 拷贝时计算校验和
#define LWIP_NETIF_TX_SINGLE_PBUF 1         // 单pbuf发送优化

// ========== 功能开关 ==========
#define LWIP_DHCP               1           // 启用DHCP
#define LWIP_DNS                1           // 启用DNS
#define LWIP_IGMP               1           // 启用IGMP（组播）
#define LWIP_NETIF_HOSTNAME     1           // 支持主机名

// ========== 调试选项 ==========
#define LWIP_DEBUG              1           // 启用调试
#define ETHARP_DEBUG            LWIP_DBG_OFF
#define NETIF_DEBUG             LWIP_DBG_OFF
#define PBUF_DEBUG              LWIP_DBG_OFF
#define IP_DEBUG                LWIP_DBG_OFF
#define TCP_DEBUG               LWIP_DBG_OFF
#define TCP_INPUT_DEBUG         LWIP_DBG_OFF
#define TCP_OUTPUT_DEBUG        LWIP_DBG_OFF
```

**配置建议**：
- 内存受限系统：减小MEM_SIZE、PBUF_POOL_SIZE
- 高性能需求：增大TCP_WND、TCP_SND_BUF
- 多连接应用：增大MEMP_NUM_TCP_PCB
- 调试阶段：启用相关DEBUG选项

## 步骤4：lwIP应用开发

### 4.1 Raw API示例 - TCP服务器

Raw API是最底层的接口，性能最高但编程复杂：

```c
#include "lwip/tcp.h"

// TCP服务器PCB
static struct tcp_pcb *tcp_server_pcb;

// 接收回调函数
static err_t tcp_server_recv(void *arg, struct tcp_pcb *tpcb, 
                              struct pbuf *p, err_t err)
{
    if(p == NULL)
    {
        // 连接关闭
        tcp_close(tpcb);
        return ERR_OK;
    }
    
    // 处理接收到的数据
    printf("Received %d bytes\r\n", p->tot_len);
    
    // 回显数据
    tcp_write(tpcb, p->payload, p->len, TCP_WRITE_FLAG_COPY);
    tcp_output(tpcb);
    
    // 释放pbuf
    pbuf_free(p);
    
    return ERR_OK;
}

// 接受连接回调
static err_t tcp_server_accept(void *arg, struct tcp_pcb *newpcb, err_t err)
{
    printf("New connection accepted\r\n");
    
    // 设置接收回调
    tcp_recv(newpcb, tcp_server_recv);
    
    return ERR_OK;
}

// 初始化TCP服务器
void tcp_server_init(void)
{
    // 创建PCB
    tcp_server_pcb = tcp_new();
    
    // 绑定到端口8080
    tcp_bind(tcp_server_pcb, IP_ADDR_ANY, 8080);
    
    // 开始监听
    tcp_server_pcb = tcp_listen(tcp_server_pcb);
    
    // 设置接受回调
    tcp_accept(tcp_server_pcb, tcp_server_accept);
    
    printf("TCP server started on port 8080\r\n");
}
```

### 4.2 Netconn API示例 - TCP客户端

Netconn API基于消息传递，使用更简单：

```c
#include "lwip/api.h"

void tcp_client_thread(void *arg)
{
    struct netconn *conn;
    struct netbuf *buf;
    ip_addr_t server_ip;
    uint16_t server_port = 8080;
    err_t err;
    
    // 设置服务器IP
    IP4_ADDR(&server_ip, 192, 168, 1, 100);
    
    // 创建TCP连接
    conn = netconn_new(NETCONN_TCP);
    
    if(conn != NULL)
    {
        // 连接到服务器
        err = netconn_connect(conn, &server_ip, server_port);
        
        if(err == ERR_OK)
        {
            printf("Connected to server\r\n");
            
            // 发送数据
            const char *data = "Hello from STM32!";
            netconn_write(conn, data, strlen(data), NETCONN_COPY);
            
            // 接收响应
            err = netconn_recv(conn, &buf);
            if(err == ERR_OK)
            {
                char *recv_data;
                uint16_t len;
                
                netbuf_data(buf, (void**)&recv_data, &len);
                printf("Received: %.*s\r\n", len, recv_data);
                
                netbuf_delete(buf);
            }
            
            // 关闭连接
            netconn_close(conn);
        }
        
        // 删除连接
        netconn_delete(conn);
    }
    
    vTaskDelete(NULL);
}
```

### 4.3 Socket API示例 - HTTP服务器

Socket API是标准BSD接口，兼容性最好：

```c
#include "lwip/sockets.h"

void http_server_thread(void *arg)
{
    int sock, newsock;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;
    char recv_buf[512];
    int recv_len;
    
    // 创建socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    
    if(sock < 0)
    {
        printf("Socket creation failed\r\n");
        vTaskDelete(NULL);
        return;
    }
    
    // 绑定地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(80);
    
    if(bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Bind failed\r\n");
        close(sock);
        vTaskDelete(NULL);
        return;
    }
    
    // 监听
    listen(sock, 5);
    printf("HTTP server listening on port 80\r\n");
    
    while(1)
    {
        // 接受连接
        client_len = sizeof(client_addr);
        newsock = accept(sock, (struct sockaddr*)&client_addr, &client_len);
        
        if(newsock < 0)
        {
            continue;
        }
        
        printf("Client connected\r\n");
        
        // 接收HTTP请求
        recv_len = recv(newsock, recv_buf, sizeof(recv_buf)-1, 0);
        
        if(recv_len > 0)
        {
            recv_buf[recv_len] = '\0';
            printf("Request: %s\r\n", recv_buf);
            
            // 发送HTTP响应
            const char *response = 
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n"
                "\r\n"
                "<html><body>"
                "<h1>Hello from STM32!</h1>"
                "<p>lwIP HTTP Server</p>"
                "</body></html>";
            
            send(newsock, response, strlen(response), 0);
        }
        
        // 关闭连接
        close(newsock);
    }
}
```

### 4.4 UDP通信示例

```c
#include "lwip/sockets.h"

void udp_echo_thread(void *arg)
{
    int sock;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;
    char recv_buf[512];
    int recv_len;
    
    // 创建UDP socket
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    
    if(sock < 0)
    {
        printf("UDP socket creation failed\r\n");
        vTaskDelete(NULL);
        return;
    }
    
    // 绑定地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(5000);
    
    if(bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("UDP bind failed\r\n");
        close(sock);
        vTaskDelete(NULL);
        return;
    }
    
    printf("UDP echo server started on port 5000\r\n");
    
    while(1)
    {
        // 接收数据
        client_len = sizeof(client_addr);
        recv_len = recvfrom(sock, recv_buf, sizeof(recv_buf)-1, 0,
                           (struct sockaddr*)&client_addr, &client_len);
        
        if(recv_len > 0)
        {
            recv_buf[recv_len] = '\0';
            printf("UDP received: %s\r\n", recv_buf);
            
            // 回显数据
            sendto(sock, recv_buf, recv_len, 0,
                  (struct sockaddr*)&client_addr, client_len);
        }
    }
}
```

### 4.5 DHCP客户端使用

lwIP内置DHCP客户端，自动获取IP地址：

```c
#include "lwip/dhcp.h"

void dhcp_check_thread(void *arg)
{
    struct netif *netif = &gnetif;  // 全局网络接口
    
    while(1)
    {
        if(dhcp_supplied_address(netif))
        {
            // DHCP成功获取IP
            printf("DHCP IP: %s\r\n", ip4addr_ntoa(&netif->ip_addr));
            printf("Netmask: %s\r\n", ip4addr_ntoa(&netif->netmask));
            printf("Gateway: %s\r\n", ip4addr_ntoa(&netif->gw));
            break;
        }
        else
        {
            printf("Waiting for DHCP...\r\n");
        }
        
        vTaskDelay(1000);
    }
    
    vTaskDelete(NULL);
}

// 在main.c中启动DHCP
void MX_LWIP_Init(void)
{
    // ... lwIP初始化代码 ...
    
    // 启动DHCP
    dhcp_start(&gnetif);
    
    // 创建DHCP检查任务
    osThreadNew(dhcp_check_thread, NULL, &dhcp_check_attributes);
}
```

### 4.6 DNS客户端使用

```c
#include "lwip/dns.h"

// DNS查询回调函数
static void dns_found_callback(const char *name, const ip_addr_t *ipaddr, void *callback_arg)
{
    if(ipaddr != NULL)
    {
        printf("DNS resolved: %s -> %s\r\n", name, ip4addr_ntoa(ipaddr));
    }
    else
    {
        printf("DNS resolution failed for %s\r\n", name);
    }
}

// 执行DNS查询
void dns_query_example(void)
{
    ip_addr_t server_ip;
    err_t err;
    
    // 异步DNS查询
    err = dns_gethostbyname("www.example.com", &server_ip, dns_found_callback, NULL);
    
    if(err == ERR_OK)
    {
        // 立即返回（已缓存）
        printf("DNS cached: %s\r\n", ip4addr_ntoa(&server_ip));
    }
    else if(err == ERR_INPROGRESS)
    {
        // 查询进行中，等待回调
        printf("DNS query in progress...\r\n");
    }
    else
    {
        printf("DNS query failed\r\n");
    }
}
```

### 4.7 SNTP时间同步

```c
#include "lwip/apps/sntp.h"

void sntp_init_example(void)
{
    // 设置SNTP服务器
    sntp_setservername(0, "pool.ntp.org");
    sntp_setservername(1, "time.nist.gov");
    
    // 设置时区（东八区）
    sntp_set_timezone(8);
    
    // 初始化SNTP
    sntp_init();
    
    printf("SNTP client started\r\n");
}

// 获取当前时间
void get_current_time(void)
{
    time_t now;
    struct tm timeinfo;
    
    time(&now);
    localtime_r(&now, &timeinfo);
    
    printf("Current time: %04d-%02d-%02d %02d:%02d:%02d\r\n",
           timeinfo.tm_year + 1900,
           timeinfo.tm_mon + 1,
           timeinfo.tm_mday,
           timeinfo.tm_hour,
           timeinfo.tm_min,
           timeinfo.tm_sec);
}
```

## 步骤5：内存管理优化

### 5.1 理解lwIP内存管理

lwIP提供三种内存管理方式：

#### 1. Heap内存（mem_malloc/mem_free）

```c
// 在lwipopts.h中配置
#define MEM_LIBC_MALLOC     0       // 不使用标准库malloc
#define MEM_SIZE            10240   // 堆大小（字节）

// 使用示例
void *ptr = mem_malloc(100);
if(ptr != NULL)
{
    // 使用内存
    mem_free(ptr);
}
```

**特点**：
- 动态分配，灵活
- 可能产生内存碎片
- 分配速度较慢

#### 2. Pool内存（memp_malloc/memp_free）

```c
// 在lwipopts.h中配置
#define MEMP_NUM_TCP_PCB    5   // TCP PCB数量
#define MEMP_NUM_UDP_PCB    4   // UDP PCB数量
#define MEMP_NUM_PBUF       10  // PBUF数量

// 使用示例（内部使用）
struct tcp_pcb *pcb = memp_malloc(MEMP_TCP_PCB);
if(pcb != NULL)
{
    // 使用PCB
    memp_free(MEMP_TCP_PCB, pcb);
}
```

**特点**：
- 固定大小内存块
- 无碎片问题
- 分配速度快
- 适合实时系统

#### 3. Pbuf内存池

```c
// 在lwipopts.h中配置
#define PBUF_POOL_SIZE      8       // pbuf池大小
#define PBUF_POOL_BUFSIZE   1536    // 每个pbuf大小

// 使用示例
struct pbuf *p = pbuf_alloc(PBUF_RAW, 1500, PBUF_POOL);
if(p != NULL)
{
    // 使用pbuf
    pbuf_free(p);
}
```

### 5.2 内存使用监控

```c
#include "lwip/stats.h"

void print_memory_stats(void)
{
    printf("=== Memory Statistics ===\r\n");
    
    // Heap内存统计
    printf("Heap:\r\n");
    printf("  Available: %d bytes\r\n", stats.mem.avail);
    printf("  Used: %d bytes\r\n", stats.mem.used);
    printf("  Max: %d bytes\r\n", stats.mem.max);
    printf("  Errors: %d\r\n", stats.mem.err);
    
    // Pool内存统计
    printf("\nPools:\r\n");
    printf("  TCP PCB: %d/%d\r\n", 
           stats.memp[MEMP_TCP_PCB]->used,
           stats.memp[MEMP_TCP_PCB]->max);
    printf("  UDP PCB: %d/%d\r\n",
           stats.memp[MEMP_UDP_PCB]->used,
           stats.memp[MEMP_UDP_PCB]->max);
    printf("  PBUF: %d/%d\r\n",
           stats.memp[MEMP_PBUF]->used,
           stats.memp[MEMP_PBUF]->max);
}
```

### 5.3 内存优化策略

#### 减少内存占用

```c
// lwipopts.h配置建议

// 1. 减少连接数
#define MEMP_NUM_TCP_PCB        3   // 根据实际需要设置
#define MEMP_NUM_TCP_PCB_LISTEN 2
#define MEMP_NUM_UDP_PCB        2

// 2. 减少缓冲区
#define TCP_MSS                 536 // 减小MSS
#define TCP_WND                 (2*TCP_MSS)
#define TCP_SND_BUF             (2*TCP_MSS)

// 3. 减少pbuf池
#define PBUF_POOL_SIZE          4
#define MEMP_NUM_PBUF           6

// 4. 禁用不需要的功能
#define LWIP_IGMP               0   // 不需要组播
#define LWIP_SNMP               0   // 不需要SNMP
#define LWIP_DHCP_AUTOIP_COOP   0   // 不需要AutoIP
```

#### 避免内存泄漏

```c
// 正确的pbuf使用
void correct_pbuf_usage(void)
{
    struct pbuf *p = pbuf_alloc(PBUF_RAW, 100, PBUF_RAM);
    
    if(p != NULL)
    {
        // 使用pbuf
        // ...
        
        // 必须释放
        pbuf_free(p);
    }
}

// 错误示例：忘记释放
void wrong_pbuf_usage(void)
{
    struct pbuf *p = pbuf_alloc(PBUF_RAW, 100, PBUF_RAM);
    
    if(p != NULL)
    {
        // 使用pbuf
        // ...
        
        // 忘记释放 - 内存泄漏！
    }
}

// 链式pbuf的正确处理
void chain_pbuf_usage(void)
{
    struct pbuf *p = pbuf_alloc(PBUF_RAW, 2000, PBUF_POOL);
    
    if(p != NULL)
    {
        // p可能是链式pbuf（多个pbuf链接）
        struct pbuf *q;
        
        for(q = p; q != NULL; q = q->next)
        {
            // 处理每个pbuf
            printf("Pbuf len: %d\r\n", q->len);
        }
        
        // 只需要释放头部，会自动释放整个链
        pbuf_free(p);
    }
}
```

## 步骤6：性能优化

### 6.1 TCP性能优化

#### 调整TCP窗口大小

```c
// lwipopts.h配置
#define TCP_WND                 (8*TCP_MSS)     // 接收窗口
#define TCP_SND_BUF             (8*TCP_MSS)     // 发送缓冲区
#define TCP_SND_QUEUELEN        ((4*TCP_SND_BUF)/TCP_MSS)

// 窗口缩放选项（支持大窗口）
#define LWIP_WND_SCALE          1
#define TCP_RCV_SCALE           2   // 窗口缩放因子
```

**原理**：
- 更大的窗口允许更多数据在途
- 提高带宽利用率
- 适合高延迟网络

#### 启用TCP快速重传

```c
#define LWIP_TCP_SACK_OUT       1   // 启用SACK
#define TCP_QUEUE_OOSEQ         1   // 队列乱序段
```

#### Nagle算法控制

```c
// 禁用Nagle算法（减少延迟）
tcp_pcb->flags |= TF_NODELAY;

// 或在socket中设置
int flag = 1;
setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
```

### 6.2 零拷贝技术

#### 使用PBUF_REF类型

```c
// 发送静态数据（如网页内容）
const char *html_page = "<html>...</html>";

void send_static_data(struct tcp_pcb *pcb)
{
    struct pbuf *p;
    
    // 使用PBUF_REF引用静态数据，避免拷贝
    p = pbuf_alloc(PBUF_RAW, strlen(html_page), PBUF_REF);
    
    if(p != NULL)
    {
        p->payload = (void*)html_page;
        
        // 发送（不拷贝）
        tcp_write(pcb, p->payload, p->len, TCP_WRITE_FLAG_MORE);
        tcp_output(pcb);
        
        pbuf_free(p);
    }
}
```

#### 使用TCP_WRITE_FLAG_COPY

```c
// 发送动态数据
void send_dynamic_data(struct tcp_pcb *pcb, char *data, uint16_t len)
{
    // TCP_WRITE_FLAG_COPY: lwIP会拷贝数据，函数返回后可以释放data
    tcp_write(pcb, data, len, TCP_WRITE_FLAG_COPY);
    tcp_output(pcb);
}

// 发送静态数据（不拷贝）
void send_static_data_nocopy(struct tcp_pcb *pcb, const char *data, uint16_t len)
{
    // 不使用COPY标志，data必须保持有效直到数据发送完成
    tcp_write(pcb, data, len, 0);
    tcp_output(pcb);
}
```

### 6.3 DMA优化

#### 配置以太网DMA

```c
// 在ethernetif.c中优化DMA配置
static void low_level_init(struct netif *netif)
{
    // 增加DMA描述符数量
    #define ETH_RX_DESC_CNT     8   // 接收描述符
    #define ETH_TX_DESC_CNT     4   // 发送描述符
    
    // 配置DMA突发长度
    heth.Init.DMAArbitration = ETH_DMAARBITRATION_ROUNDROBIN_RXTX_1_1;
    
    // 启用DMA增强描述符
    heth.Init.DescriptorSkipLength = 0;
    
    // 配置接收缓冲区大小
    #define ETH_RX_BUF_SIZE     1536
}
```

#### 使用DMA缓存一致性

```c
// STM32H7等带缓存的MCU需要处理缓存一致性
void cache_maintenance(void)
{
    // 发送前：清除D-Cache
    SCB_CleanDCache_by_Addr((uint32_t*)tx_buffer, length);
    
    // 接收后：使D-Cache无效
    SCB_InvalidateDCache_by_Addr((uint32_t*)rx_buffer, length);
}
```

### 6.4 中断优化

#### 配置以太网中断优先级

```c
// 在main.c中设置中断优先级
void HAL_ETH_MspInit(ETH_HandleTypeDef* ethHandle)
{
    // 以太网中断优先级应高于FreeRTOS最低优先级
    // 但低于关键中断
    HAL_NVIC_SetPriority(ETH_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(ETH_IRQn);
}
```

#### 减少中断处理时间

```c
// 在中断中只做必要的工作
void ETH_IRQHandler(void)
{
    HAL_ETH_IRQHandler(&heth);
}

// HAL回调函数
void HAL_ETH_RxCpltCallback(ETH_HandleTypeDef *heth)
{
    // 只发送信号量，不处理数据
    osSemaphoreRelease(RxPktSemaphore);
}

// 在任务中处理数据
void ethernetif_input(void *argument)
{
    while(1)
    {
        if(osSemaphoreAcquire(RxPktSemaphore, osWaitForever) == osOK)
        {
            // 在任务上下文中处理数据包
            process_received_packets();
        }
    }
}
```

### 6.5 性能测试

#### iperf测试

lwIP支持iperf服务器，用于测试网络性能：

```c
// 在lwipopts.h中启用
#define LWIP_IPERF_SERVER   1

// 在应用中启动
#include "lwip/apps/lwiperf.h"

void start_iperf_server(void)
{
    lwiperf_start_tcp_server_default(NULL, NULL);
    printf("iPerf server started\r\n");
}
```

在PC上运行iperf客户端：

```bash
# 测试下载速度（STM32发送）
iperf -c 192.168.1.100 -t 30

# 测试上传速度（STM32接收）
iperf -c 192.168.1.100 -t 30 -r

# UDP测试
iperf -c 192.168.1.100 -u -b 100M
```

#### 吞吐量测试代码

```c
void throughput_test_server(void)
{
    int sock, newsock;
    struct sockaddr_in server_addr;
    char recv_buf[1460];
    int recv_len;
    uint32_t total_bytes = 0;
    uint32_t start_time, elapsed_time;
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(5001);
    
    bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
    listen(sock, 1);
    
    printf("Throughput test server started\r\n");
    
    newsock = accept(sock, NULL, NULL);
    
    start_time = HAL_GetTick();
    
    while(1)
    {
        recv_len = recv(newsock, recv_buf, sizeof(recv_buf), 0);
        
        if(recv_len <= 0)
            break;
        
        total_bytes += recv_len;
        
        elapsed_time = HAL_GetTick() - start_time;
        
        if(elapsed_time >= 10000)  // 10秒
        {
            float throughput = (total_bytes * 8.0) / (elapsed_time / 1000.0) / 1000000.0;
            printf("Throughput: %.2f Mbps\r\n", throughput);
            
            total_bytes = 0;
            start_time = HAL_GetTick();
        }
    }
    
    close(newsock);
    close(sock);
}
```

## 步骤7：调试与故障排除

### 7.1 启用lwIP调试输出

#### 配置调试选项

```c
// 在lwipopts.h中启用调试
#define LWIP_DEBUG              1

// 重定向调试输出到串口
#define LWIP_PLATFORM_DIAG(x)   do {printf x;} while(0)

// 启用各模块调试
#define ETHARP_DEBUG            LWIP_DBG_ON
#define NETIF_DEBUG             LWIP_DBG_ON
#define PBUF_DEBUG              LWIP_DBG_ON
#define IP_DEBUG                LWIP_DBG_ON
#define ICMP_DEBUG              LWIP_DBG_ON
#define DHCP_DEBUG              LWIP_DBG_ON
#define TCP_DEBUG               LWIP_DBG_ON
#define TCP_INPUT_DEBUG         LWIP_DBG_ON
#define TCP_OUTPUT_DEBUG        LWIP_DBG_ON
#define TCP_RTO_DEBUG           LWIP_DBG_ON
#define UDP_DEBUG               LWIP_DBG_ON

// 调试级别
#define LWIP_DBG_MIN_LEVEL      LWIP_DBG_LEVEL_ALL
```

#### 实现printf重定向

```c
// 在usart.c中实现
#include <stdio.h>

int fputc(int ch, FILE *f)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, 0xFFFF);
    return ch;
}

int fgetc(FILE *f)
{
    uint8_t ch;
    HAL_UART_Receive(&huart1, &ch, 1, 0xFFFF);
    return ch;
}
```

### 7.2 常见问题诊断

#### 问题1：无法获取IP地址

**症状**：
- DHCP一直失败
- 静态IP也无法通信

**诊断步骤**：

```c
// 1. 检查PHY状态
void check_phy_status(void)
{
    uint32_t phyreg;
    
    // 读取PHY基本状态寄存器
    HAL_ETH_ReadPHYRegister(&heth, PHY_ADDRESS, PHY_BSR, &phyreg);
    
    printf("PHY Status: 0x%04X\r\n", phyreg);
    printf("Link Status: %s\r\n", (phyreg & PHY_LINKED_STATUS) ? "UP" : "DOWN");
    printf("Auto-negotiation: %s\r\n", (phyreg & PHY_AUTONEGO_COMPLETE) ? "Complete" : "In progress");
}

// 2. 检查网络接口状态
void check_netif_status(void)
{
    struct netif *netif = &gnetif;
    
    printf("Netif Status:\r\n");
    printf("  Link: %s\r\n", netif_is_link_up(netif) ? "UP" : "DOWN");
    printf("  Up: %s\r\n", netif_is_up(netif) ? "YES" : "NO");
    printf("  IP: %s\r\n", ip4addr_ntoa(&netif->ip_addr));
}

// 3. 检查以太网MAC状态
void check_eth_status(void)
{
    printf("ETH Status:\r\n");
    printf("  State: %d\r\n", heth.gState);
    printf("  Error: 0x%08X\r\n", heth.ErrorCode);
}
```

**可能原因**：
- PHY地址配置错误
- PHY时钟未正确配置
- 网线未连接
- 路由器DHCP服务未启用

#### 问题2：Ping不通

**症状**：
- 设备有IP地址
- 但无法ping通

**诊断步骤**：

```c
// 1. 检查ICMP是否启用
#define LWIP_ICMP   1  // 在lwipopts.h中

// 2. 检查防火墙
// 确保PC防火墙允许ICMP

// 3. 测试ARP
void test_arp(void)
{
    ip4_addr_t target_ip;
    IP4_ADDR(&target_ip, 192, 168, 1, 1);
    
    // 发送ARP请求
    etharp_request(&gnetif, &target_ip);
    
    // 等待并检查ARP表
    vTaskDelay(1000);
    
    const struct eth_addr *eth_ret;
    const ip4_addr_t *ip_ret;
    
    for(int i = 0; i < ARP_TABLE_SIZE; i++)
    {
        if(etharp_get_entry(i, &ip_ret, &gnetif, &eth_ret))
        {
            printf("ARP Entry %d: %s -> %02X:%02X:%02X:%02X:%02X:%02X\r\n",
                   i, ip4addr_ntoa(ip_ret),
                   eth_ret->addr[0], eth_ret->addr[1], eth_ret->addr[2],
                   eth_ret->addr[3], eth_ret->addr[4], eth_ret->addr[5]);
        }
    }
}
```

#### 问题3：TCP连接失败

**症状**：
- 无法建立TCP连接
- 连接超时

**诊断步骤**：

```c
// 1. 检查端口是否监听
void list_tcp_pcbs(void)
{
    struct tcp_pcb *pcb;
    
    printf("=== TCP Listen PCBs ===\r\n");
    for(pcb = tcp_listen_pcbs.pcbs; pcb != NULL; pcb = pcb->next)
    {
        printf("Port: %d\r\n", pcb->local_port);
    }
    
    printf("\n=== TCP Active PCBs ===\r\n");
    for(pcb = tcp_active_pcbs; pcb != NULL; pcb = pcb->next)
    {
        printf("Local: %s:%d\r\n", 
               ip4addr_ntoa(&pcb->local_ip), pcb->local_port);
        printf("Remote: %s:%d\r\n",
               ip4addr_ntoa(&pcb->remote_ip), pcb->remote_port);
        printf("State: %d\r\n", pcb->state);
    }
}

// 2. 使用Wireshark抓包分析
// 检查TCP三次握手是否完成
// 检查是否有RST包
```

#### 问题4：内存不足

**症状**：
- 连接失败
- 数据丢失
- 系统崩溃

**诊断步骤**：

```c
// 1. 监控内存使用
void monitor_memory(void)
{
    printf("=== Memory Usage ===\r\n");
    printf("Heap available: %d\r\n", mem_stats.avail);
    printf("Heap used: %d\r\n", mem_stats.used);
    printf("Heap max: %d\r\n", mem_stats.max);
    printf("Heap errors: %d\r\n", mem_stats.err);
    
    printf("\n=== Pool Usage ===\r\n");
    printf("TCP PCB: %d/%d\r\n",
           memp_stats[MEMP_TCP_PCB].used,
           MEMP_NUM_TCP_PCB);
    printf("PBUF: %d/%d\r\n",
           memp_stats[MEMP_PBUF].used,
           MEMP_NUM_PBUF);
    printf("PBUF_POOL: %d/%d\r\n",
           memp_stats[MEMP_PBUF_POOL].used,
           PBUF_POOL_SIZE);
}

// 2. 增加内存配置
// 在lwipopts.h中增大相关参数
```

### 7.3 使用Wireshark分析

#### 抓包分析TCP连接

1. **启动Wireshark**：
   - 选择网络接口
   - 开始捕获

2. **过滤规则**：
   ```
   # 只显示与STM32通信的包
   ip.addr == 192.168.1.100
   
   # 只显示TCP包
   tcp
   
   # 显示特定端口
   tcp.port == 8080
   
   # 显示TCP错误
   tcp.analysis.flags
   ```

3. **分析TCP三次握手**：
   ```
   客户端 -> 服务器: SYN
   服务器 -> 客户端: SYN+ACK
   客户端 -> 服务器: ACK
   ```

4. **检查常见问题**：
   - **RST包**：连接被重置，可能是端口未监听
   - **重传**：数据包丢失，检查网络质量
   - **零窗口**：接收缓冲区满，增大TCP_WND
   - **乱序**：网络延迟不稳定

#### 导出统计信息

```
Statistics -> Conversations -> TCP
  - 查看每个连接的统计信息
  - 吞吐量、丢包率、延迟

Statistics -> IO Graphs
  - 绘制流量图表
  - 分析流量模式
```

### 7.4 性能分析工具

#### CPU使用率监控

```c
#include "FreeRTOS.h"
#include "task.h"

void print_task_stats(void)
{
    TaskStatus_t *pxTaskStatusArray;
    volatile UBaseType_t uxArraySize, x;
    uint32_t ulTotalRunTime, ulStatsAsPercentage;
    
    // 获取任务数量
    uxArraySize = uxTaskGetNumberOfTasks();
    
    // 分配内存
    pxTaskStatusArray = pvPortMalloc(uxArraySize * sizeof(TaskStatus_t));
    
    if(pxTaskStatusArray != NULL)
    {
        // 获取任务状态
        uxArraySize = uxTaskGetSystemState(pxTaskStatusArray, uxArraySize, &ulTotalRunTime);
        
        printf("Task Name\t\tStatus\tPrio\tStack\tCPU%%\r\n");
        printf("========================================================\r\n");
        
        for(x = 0; x < uxArraySize; x++)
        {
            // 计算CPU使用率
            ulStatsAsPercentage = pxTaskStatusArray[x].ulRunTimeCounter / (ulTotalRunTime / 100);
            
            printf("%-16s\t%c\t%u\t%u\t%u%%\r\n",
                   pxTaskStatusArray[x].pcTaskName,
                   pxTaskStatusArray[x].eCurrentState == eRunning ? 'R' : 'B',
                   pxTaskStatusArray[x].uxCurrentPriority,
                   pxTaskStatusArray[x].usStackHighWaterMark,
                   ulStatsAsPercentage);
        }
        
        vPortFree(pxTaskStatusArray);
    }
}
```

## 步骤8：实战项目 - Web服务器

### 8.1 项目需求

实现一个功能完整的Web服务器：
- 提供静态网页服务
- 显示系统状态（CPU、内存、网络）
- 支持LED控制
- 实时数据更新（使用AJAX）

### 8.2 项目结构

```text
project/
├── Core/
│   ├── Src/
│   │   ├── main.c
│   │   └── web_server.c
│   └── Inc/
│       └── web_server.h
├── LWIP/
│   ├── App/
│   └── Target/
└── Web/
    ├── index.html
    ├── style.css
    └── script.js
```

### 8.3 Web服务器实现

#### web_server.h

```c
#ifndef WEB_SERVER_H
#define WEB_SERVER_H

#include "lwip/api.h"

// 初始化Web服务器
void web_server_init(void);

// Web服务器任务
void web_server_thread(void *arg);

// 处理HTTP请求
void http_process_request(struct netconn *conn, char *buf, uint16_t buflen);

// 发送HTTP响应
void http_send_response(struct netconn *conn, const char *content_type, 
                        const char *content, uint16_t content_len);

// 生成JSON状态数据
void generate_status_json(char *buf, uint16_t buflen);

#endif
```

#### web_server.c

```c
#include "web_server.h"
#include "lwip/api.h"
#include <string.h>
#include <stdio.h>

// HTML页面内容
const char html_page[] = 
"<!DOCTYPE html>"
"<html>"
"<head>"
"<meta charset='UTF-8'>"
"<title>STM32 Web Server</title>"
"<style>"
"body { font-family: Arial; margin: 20px; background: #f0f0f0; }"
".container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }"
"h1 { color: #333; }"
".status { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }"
".control { background: #fff3e0; padding: 15px; border-radius: 5px; margin: 10px 0; }"
"button { padding: 10px 20px; font-size: 16px; cursor: pointer; border: none; border-radius: 5px; }"
".btn-on { background: #4caf50; color: white; }"
".btn-off { background: #f44336; color: white; }"
"</style>"
"</head>"
"<body>"
"<div class='container'>"
"<h1>STM32 Web Server</h1>"
"<div class='status'>"
"<h2>System Status</h2>"
"<p>CPU Usage: <span id='cpu'>--</span>%</p>"
"<p>Free Memory: <span id='memory'>--</span> KB</p>"
"<p>Uptime: <span id='uptime'>--</span> seconds</p>"
"<p>IP Address: <span id='ip'>--</span></p>"
"</div>"
"<div class='control'>"
"<h2>LED Control</h2>"
"<button class='btn-on' onclick='controlLED(1)'>LED ON</button>"
"<button class='btn-off' onclick='controlLED(0)'>LED OFF</button>"
"<p>LED Status: <span id='led-status'>--</span></p>"
"</div>"
"</div>"
"<script>"
"function updateStatus() {"
"  fetch('/api/status')"
"    .then(response => response.json())"
"    .then(data => {"
"      document.getElementById('cpu').textContent = data.cpu;"
"      document.getElementById('memory').textContent = data.memory;"
"      document.getElementById('uptime').textContent = data.uptime;"
"      document.getElementById('ip').textContent = data.ip;"
"      document.getElementById('led-status').textContent = data.led ? 'ON' : 'OFF';"
"    });"
"}"
"function controlLED(state) {"
"  fetch('/api/led?state=' + state)"
"    .then(() => updateStatus());"
"}"
"setInterval(updateStatus, 1000);"
"updateStatus();"
"</script>"
"</body>"
"</html>";

// LED状态
static uint8_t led_state = 0;

void web_server_init(void)
{
    sys_thread_new("web_server", web_server_thread, NULL, 
                   DEFAULT_THREAD_STACKSIZE, osPriorityNormal);
}
```

```c
void web_server_thread(void *arg)
{
    struct netconn *conn, *newconn;
    err_t err;
    
    // 创建TCP连接
    conn = netconn_new(NETCONN_TCP);
    
    if(conn == NULL)
    {
        printf("Failed to create netconn\r\n");
        vTaskDelete(NULL);
        return;
    }
    
    // 绑定到端口80
    err = netconn_bind(conn, IP_ADDR_ANY, 80);
    
    if(err != ERR_OK)
    {
        printf("Failed to bind: %d\r\n", err);
        netconn_delete(conn);
        vTaskDelete(NULL);
        return;
    }
    
    // 开始监听
    netconn_listen(conn);
    printf("Web server started on port 80\r\n");
    
    while(1)
    {
        // 接受新连接
        err = netconn_accept(conn, &newconn);
        
        if(err == ERR_OK)
        {
            // 处理HTTP请求
            struct netbuf *buf;
            char *data;
            uint16_t len;
            
            err = netconn_recv(newconn, &buf);
            
            if(err == ERR_OK)
            {
                netbuf_data(buf, (void**)&data, &len);
                
                // 处理请求
                http_process_request(newconn, data, len);
                
                netbuf_delete(buf);
            }
            
            // 关闭连接
            netconn_close(newconn);
            netconn_delete(newconn);
        }
    }
}

void http_process_request(struct netconn *conn, char *buf, uint16_t buflen)
{
    char *method, *uri, *params;
    
    // 解析HTTP请求行
    method = strtok(buf, " ");
    uri = strtok(NULL, " ");
    
    if(method == NULL || uri == NULL)
        return;
    
    printf("HTTP Request: %s %s\r\n", method, uri);
    
    // 处理不同的URI
    if(strcmp(uri, "/") == 0 || strncmp(uri, "/index", 6) == 0)
    {
        // 返回主页
        http_send_response(conn, "text/html", html_page, strlen(html_page));
    }
    else if(strcmp(uri, "/api/status") == 0)
    {
        // 返回状态JSON
        char json_buf[256];
        generate_status_json(json_buf, sizeof(json_buf));
        http_send_response(conn, "application/json", json_buf, strlen(json_buf));
    }
    else if(strncmp(uri, "/api/led", 8) == 0)
    {
        // LED控制
        params = strchr(uri, '?');
        if(params != NULL)
        {
            params++;  // 跳过'?'
            
            if(strncmp(params, "state=1", 7) == 0)
            {
                led_state = 1;
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
            }
            else if(strncmp(params, "state=0", 7) == 0)
            {
                led_state = 0;
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
            }
        }
        
        http_send_response(conn, "text/plain", "OK", 2);
    }
    else
    {
        // 404 Not Found
        const char *response = "HTTP/1.1 404 Not Found\r\n\r\n";
        netconn_write(conn, response, strlen(response), NETCONN_COPY);
    }
}

void http_send_response(struct netconn *conn, const char *content_type,
                        const char *content, uint16_t content_len)
{
    char header[256];
    
    // 构建HTTP响应头
    snprintf(header, sizeof(header),
             "HTTP/1.1 200 OK\r\n"
             "Content-Type: %s\r\n"
             "Content-Length: %d\r\n"
             "Connection: close\r\n"
             "\r\n",
             content_type, content_len);
    
    // 发送响应头
    netconn_write(conn, header, strlen(header), NETCONN_COPY);
    
    // 发送响应体
    netconn_write(conn, content, content_len, NETCONN_COPY);
}

void generate_status_json(char *buf, uint16_t buflen)
{
    extern struct netif gnetif;
    uint32_t uptime = HAL_GetTick() / 1000;
    uint32_t free_heap = xPortGetFreeHeapSize();
    
    // 简化的CPU使用率（实际应该使用FreeRTOS统计）
    uint32_t cpu_usage = 50;
    
    snprintf(buf, buflen,
             "{"
             "\"cpu\":%u,"
             "\"memory\":%u,"
             "\"uptime\":%u,"
             "\"ip\":\"%s\","
             "\"led\":%d"
             "}",
             cpu_usage,
             free_heap / 1024,
             uptime,
             ip4addr_ntoa(&gnetif.ip_addr),
             led_state);
}
```

### 8.4 在main.c中集成

```c
#include "web_server.h"

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();
    MX_ETH_Init();
    
    // 初始化FreeRTOS
    osKernelInitialize();
    
    // 初始化lwIP
    MX_LWIP_Init();
    
    // 启动Web服务器
    web_server_init();
    
    // 启动调度器
    osKernelStart();
    
    while(1)
    {
        // 不应该到达这里
    }
}
```

### 8.5 测试Web服务器

1. **编译并下载程序到STM32**

2. **查看串口输出获取IP地址**：
   ```
   DHCP IP: 192.168.1.100
   Web server started on port 80
   ```

3. **在浏览器中访问**：
   ```
   http://192.168.1.100
   ```

4. **测试功能**：
   - 查看系统状态（自动更新）
   - 点击LED控制按钮
   - 观察LED状态变化

### 8.6 项目扩展

#### 添加文件上传功能

```c
void handle_file_upload(struct netconn *conn, char *buf, uint16_t buflen)
{
    // 解析multipart/form-data
    char *boundary = strstr(buf, "boundary=");
    if(boundary == NULL)
        return;
    
    boundary += 9;  // 跳过"boundary="
    
    // 查找文件数据
    char *file_data = strstr(buf, "\r\n\r\n");
    if(file_data == NULL)
        return;
    
    file_data += 4;  // 跳过"\r\n\r\n"
    
    // 保存文件到Flash或SD卡
    // ...
    
    http_send_response(conn, "text/plain", "Upload successful", 17);
}
```

#### 添加WebSocket支持

```c
// 需要启用lwIP的WebSocket支持
#define LWIP_HTTPD_SUPPORT_WEBSOCKET  1

// 实现WebSocket回调
void websocket_callback(struct tcp_pcb *pcb, uint8_t *data, uint16_t len)
{
    // 处理WebSocket消息
    printf("WebSocket data: %.*s\r\n", len, data);
    
    // 发送响应
    websocket_write(pcb, data, len, WS_TEXT_MODE);
}
```

## 高级主题

### 9.1 多网络接口

lwIP支持多个网络接口（如以太网+WiFi）：

```c
struct netif eth_netif;  // 以太网接口
struct netif wifi_netif; // WiFi接口

void multi_netif_init(void)
{
    ip4_addr_t ipaddr, netmask, gw;
    
    // 初始化以太网接口
    IP4_ADDR(&ipaddr, 192, 168, 1, 100);
    IP4_ADDR(&netmask, 255, 255, 255, 0);
    IP4_ADDR(&gw, 192, 168, 1, 1);
    
    netif_add(&eth_netif, &ipaddr, &netmask, &gw, NULL,
              ethernetif_init, tcpip_input);
    
    netif_set_default(&eth_netif);
    netif_set_up(&eth_netif);
    
    // 初始化WiFi接口
    IP4_ADDR(&ipaddr, 192, 168, 2, 100);
    IP4_ADDR(&netmask, 255, 255, 255, 0);
    IP4_ADDR(&gw, 192, 168, 2, 1);
    
    netif_add(&wifi_netif, &ipaddr, &netmask, &gw, NULL,
              wifiif_init, tcpip_input);
    
    netif_set_up(&wifi_netif);
}

// 路由选择
void set_default_route(struct netif *netif)
{
    netif_set_default(netif);
}
```

### 9.2 IPv6支持

启用IPv6：

```c
// 在lwipopts.h中
#define LWIP_IPV6               1
#define LWIP_IPV6_DHCP6         1
#define LWIP_IPV6_AUTOCONFIG    1

// 配置IPv6地址
void ipv6_init(void)
{
    ip6_addr_t ip6addr;
    
    // 设置链路本地地址
    netif_create_ip6_linklocal_address(&gnetif, 1);
    
    // 设置全局地址
    IP6_ADDR(&ip6addr, 0x2001, 0x0db8, 0, 0, 0, 0, 0, 0x0001);
    netif_ip6_addr_set(&gnetif, 1, &ip6addr);
    netif_ip6_addr_set_state(&gnetif, 1, IP6_ADDR_VALID);
    
    printf("IPv6 Address: %s\r\n", ip6addr_ntoa(&gnetif.ip6_addr[0]));
}
```

### 9.3 TLS/SSL支持

使用mbedTLS实现HTTPS：

```c
// 在lwipopts.h中
#define LWIP_ALTCP              1
#define LWIP_ALTCP_TLS          1

// 包含mbedTLS
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

// HTTPS服务器示例
void https_server_init(void)
{
    struct altcp_tls_config *tls_config;
    struct altcp_pcb *pcb;
    
    // 创建TLS配置
    tls_config = altcp_tls_create_config_server_privkey_cert(
        server_key, server_key_len,
        server_cert, server_cert_len);
    
    // 创建TLS PCB
    pcb = altcp_tls_new(tls_config, IPADDR_TYPE_ANY);
    
    // 绑定和监听
    altcp_bind(pcb, IP_ADDR_ANY, 443);
    pcb = altcp_listen(pcb);
    
    // 设置回调
    altcp_accept(pcb, https_accept_callback);
}
```

### 9.4 PPP支持

lwIP支持PPP协议，可用于串口拨号或4G模块：

```c
// 在lwipopts.h中
#define PPP_SUPPORT             1
#define PPPOS_SUPPORT           1

// PPP初始化
#include "netif/ppp/pppos.h"

ppp_pcb *ppp;

void ppp_init_example(void)
{
    // 创建PPP控制块
    ppp = pppos_create(&ppp_netif, ppp_output_callback, 
                       ppp_link_status_cb, NULL);
    
    if(ppp == NULL)
    {
        printf("Failed to create PPP\r\n");
        return;
    }
    
    // 设置认证信息
    ppp_set_auth(ppp, PPPAUTHTYPE_PAP, "username", "password");
    
    // 连接
    ppp_connect(ppp, 0);
}

// PPP输出回调（发送到串口）
uint32_t ppp_output_callback(ppp_pcb *pcb, uint8_t *data, uint32_t len, void *ctx)
{
    HAL_UART_Transmit(&huart2, data, len, 1000);
    return len;
}

// PPP状态回调
void ppp_link_status_cb(ppp_pcb *pcb, int err_code, void *ctx)
{
    switch(err_code)
    {
        case PPPERR_NONE:
            printf("PPP connected\r\n");
            printf("IP: %s\r\n", ipaddr_ntoa(&ppp_netif.ip_addr));
            break;
            
        case PPPERR_CONNECT:
            printf("PPP connection failed\r\n");
            break;
            
        case PPPERR_AUTHFAIL:
            printf("PPP authentication failed\r\n");
            break;
            
        default:
            printf("PPP error: %d\r\n", err_code);
            break;
    }
}

// 接收PPP数据（从串口）
void ppp_input_data(uint8_t *data, uint16_t len)
{
    pppos_input(ppp, data, len);
}
```

### 9.5 MQTT客户端

使用lwIP实现MQTT客户端：

```c
#include "lwip/apps/mqtt.h"

mqtt_client_t *mqtt_client;

// MQTT连接回调
static void mqtt_connection_cb(mqtt_client_t *client, void *arg, 
                                mqtt_connection_status_t status)
{
    if(status == MQTT_CONNECT_ACCEPTED)
    {
        printf("MQTT connected\r\n");
        
        // 订阅主题
        mqtt_subscribe(client, "sensor/temperature", 0, 
                      mqtt_sub_request_cb, arg);
    }
    else
    {
        printf("MQTT connection failed: %d\r\n", status);
    }
}

// MQTT消息接收回调
static void mqtt_incoming_data_cb(void *arg, const uint8_t *data, 
                                   uint16_t len, uint8_t flags)
{
    printf("MQTT received: %.*s\r\n", len, data);
}

// MQTT发布回调
static void mqtt_pub_request_cb(void *arg, err_t result)
{
    if(result == ERR_OK)
    {
        printf("MQTT publish successful\r\n");
    }
}

// 初始化MQTT客户端
void mqtt_client_init(void)
{
    struct mqtt_connect_client_info_t ci;
    ip_addr_t mqtt_server_ip;
    
    // 创建MQTT客户端
    mqtt_client = mqtt_client_new();
    
    // 配置连接信息
    memset(&ci, 0, sizeof(ci));
    ci.client_id = "stm32_client";
    ci.client_user = "username";
    ci.client_pass = "password";
    ci.keep_alive = 60;
    
    // 设置服务器IP
    IP4_ADDR(&mqtt_server_ip, 192, 168, 1, 10);
    
    // 连接到MQTT服务器
    mqtt_client_connect(mqtt_client, &mqtt_server_ip, 1883,
                       mqtt_connection_cb, NULL, &ci);
}

// 发布MQTT消息
void mqtt_publish_example(void)
{
    const char *topic = "sensor/temperature";
    const char *payload = "25.5";
    
    mqtt_publish(mqtt_client, topic, payload, strlen(payload),
                0, 0, mqtt_pub_request_cb, NULL);
}
```

## 最佳实践

### 10.1 代码组织

#### 模块化设计

```text
project/
├── network/
│   ├── lwip_init.c/h       # lwIP初始化
│   ├── ethernetif.c/h      # 以太网驱动
│   └── network_config.h    # 网络配置
├── applications/
│   ├── web_server.c/h      # Web服务器
│   ├── tcp_client.c/h      # TCP客户端
│   └── udp_server.c/h      # UDP服务器
└── utils/
    ├── http_parser.c/h     # HTTP解析
    └── json_builder.c/h    # JSON构建
```

#### 配置管理

```c
// network_config.h
#ifndef NETWORK_CONFIG_H
#define NETWORK_CONFIG_H

// 网络配置
#define USE_DHCP                1
#define STATIC_IP_ADDRESS       "192.168.1.100"
#define STATIC_NETMASK          "255.255.255.0"
#define STATIC_GATEWAY          "192.168.1.1"

// 应用配置
#define WEB_SERVER_PORT         80
#define TCP_SERVER_PORT         8080
#define UDP_SERVER_PORT         5000

// 性能配置
#define ENABLE_ZERO_COPY        1
#define ENABLE_CHECKSUM_OFFLOAD 1

#endif
```

### 10.2 错误处理

#### 统一错误处理

```c
typedef enum {
    NET_OK = 0,
    NET_ERR_TIMEOUT,
    NET_ERR_CONN_FAILED,
    NET_ERR_NO_MEMORY,
    NET_ERR_INVALID_PARAM,
    NET_ERR_NOT_CONNECTED
} net_error_t;

// 错误处理函数
void handle_network_error(net_error_t error, const char *context)
{
    printf("[ERROR] %s: ", context);
    
    switch(error)
    {
        case NET_ERR_TIMEOUT:
            printf("Timeout\r\n");
            break;
        case NET_ERR_CONN_FAILED:
            printf("Connection failed\r\n");
            break;
        case NET_ERR_NO_MEMORY:
            printf("Out of memory\r\n");
            break;
        default:
            printf("Unknown error %d\r\n", error);
            break;
    }
}

// 使用示例
net_error_t tcp_connect_with_retry(const char *host, uint16_t port, int retries)
{
    int attempt = 0;
    
    while(attempt < retries)
    {
        if(tcp_connect(host, port) == NET_OK)
        {
            return NET_OK;
        }
        
        attempt++;
        printf("Connection attempt %d/%d failed\r\n", attempt, retries);
        vTaskDelay(1000);
    }
    
    return NET_ERR_CONN_FAILED;
}
```

### 10.3 安全考虑

#### 输入验证

```c
// HTTP请求验证
bool validate_http_request(const char *request, uint16_t len)
{
    // 检查长度
    if(len > MAX_HTTP_REQUEST_SIZE)
    {
        printf("HTTP request too large\r\n");
        return false;
    }
    
    // 检查方法
    if(strncmp(request, "GET ", 4) != 0 &&
       strncmp(request, "POST ", 5) != 0)
    {
        printf("Invalid HTTP method\r\n");
        return false;
    }
    
    // 检查路径遍历攻击
    if(strstr(request, "..") != NULL)
    {
        printf("Path traversal attempt detected\r\n");
        return false;
    }
    
    return true;
}

// SQL注入防护（如果使用数据库）
void sanitize_input(char *input)
{
    char *dangerous_chars = "';\"\\";
    char *p = input;
    
    while(*p)
    {
        if(strchr(dangerous_chars, *p) != NULL)
        {
            *p = '_';  // 替换危险字符
        }
        p++;
    }
}
```

#### 访问控制

```c
// 简单的IP白名单
bool is_ip_allowed(ip4_addr_t *ip)
{
    // 允许的IP列表
    const ip4_addr_t allowed_ips[] = {
        IPADDR4_INIT_BYTES(192, 168, 1, 10),
        IPADDR4_INIT_BYTES(192, 168, 1, 20),
    };
    
    for(int i = 0; i < sizeof(allowed_ips)/sizeof(allowed_ips[0]); i++)
    {
        if(ip4_addr_cmp(ip, &allowed_ips[i]))
        {
            return true;
        }
    }
    
    return false;
}

// 在接受连接时检查
err_t tcp_accept_with_acl(void *arg, struct tcp_pcb *newpcb, err_t err)
{
    if(!is_ip_allowed(&newpcb->remote_ip))
    {
        printf("Connection from %s denied\r\n", 
               ip4addr_ntoa(&newpcb->remote_ip));
        tcp_abort(newpcb);
        return ERR_ABRT;
    }
    
    // 继续处理连接
    return tcp_accept_callback(arg, newpcb, err);
}
```

#### 防止DoS攻击

```c
// 连接限制
#define MAX_CONNECTIONS     10
static uint8_t active_connections = 0;

err_t tcp_accept_with_limit(void *arg, struct tcp_pcb *newpcb, err_t err)
{
    if(active_connections >= MAX_CONNECTIONS)
    {
        printf("Max connections reached, rejecting\r\n");
        tcp_abort(newpcb);
        return ERR_ABRT;
    }
    
    active_connections++;
    
    // 设置关闭回调以减少计数
    tcp_arg(newpcb, NULL);
    tcp_err(newpcb, tcp_error_callback);
    
    return ERR_OK;
}

void tcp_error_callback(void *arg, err_t err)
{
    if(active_connections > 0)
    {
        active_connections--;
    }
}
```

### 10.4 资源管理

#### 连接池管理

```c
#define CONNECTION_POOL_SIZE    5

typedef struct {
    struct tcp_pcb *pcb;
    bool in_use;
    uint32_t last_activity;
} connection_t;

static connection_t connection_pool[CONNECTION_POOL_SIZE];

// 获取空闲连接
connection_t* get_free_connection(void)
{
    for(int i = 0; i < CONNECTION_POOL_SIZE; i++)
    {
        if(!connection_pool[i].in_use)
        {
            connection_pool[i].in_use = true;
            connection_pool[i].last_activity = HAL_GetTick();
            return &connection_pool[i];
        }
    }
    
    return NULL;  // 无空闲连接
}

// 释放连接
void release_connection(connection_t *conn)
{
    if(conn != NULL)
    {
        if(conn->pcb != NULL)
        {
            tcp_close(conn->pcb);
            conn->pcb = NULL;
        }
        conn->in_use = false;
    }
}

// 超时清理
void cleanup_idle_connections(void)
{
    uint32_t now = HAL_GetTick();
    const uint32_t timeout = 30000;  // 30秒超时
    
    for(int i = 0; i < CONNECTION_POOL_SIZE; i++)
    {
        if(connection_pool[i].in_use)
        {
            if(now - connection_pool[i].last_activity > timeout)
            {
                printf("Closing idle connection %d\r\n", i);
                release_connection(&connection_pool[i]);
            }
        }
    }
}
```

#### 内存泄漏检测

```c
// 定期检查内存使用
void memory_leak_detector(void)
{
    static uint32_t last_free_heap = 0;
    static uint32_t check_count = 0;
    
    uint32_t current_free_heap = xPortGetFreeHeapSize();
    
    if(last_free_heap > 0)
    {
        int32_t diff = (int32_t)current_free_heap - (int32_t)last_free_heap;
        
        if(diff < -1024)  // 减少超过1KB
        {
            printf("WARNING: Possible memory leak detected\r\n");
            printf("Free heap decreased by %d bytes\r\n", -diff);
            
            // 打印内存统计
            print_memory_stats();
        }
    }
    
    last_free_heap = current_free_heap;
    check_count++;
    
    if(check_count % 10 == 0)
    {
        printf("Memory check #%u: %u bytes free\r\n", 
               check_count, current_free_heap);
    }
}
```

## 总结

通过本教程，你学习了：

- ✅ lwIP协议栈的架构设计和核心模块
- ✅ STM32平台上的lwIP移植方法
- ✅ 以太网硬件接口和驱动开发
- ✅ lwIP的三种API接口（Raw、Netconn、Socket）
- ✅ 内存管理和性能优化技术
- ✅ TCP/UDP网络应用开发
- ✅ DHCP、DNS、SNTP等协议的使用
- ✅ Web服务器实战项目开发
- ✅ 调试技巧和故障排除方法
- ✅ 安全和资源管理最佳实践

**关键要点**：

1. **架构理解**：lwIP采用分层设计，支持多种API和配置选项
2. **移植要点**：正确配置PHY、实现驱动接口、调整内存参数
3. **API选择**：Raw API性能最高，Socket API兼容性最好
4. **内存管理**：合理配置三种内存池，避免内存泄漏
5. **性能优化**：使用DMA、零拷贝、硬件校验和
6. **调试方法**：启用调试输出、使用Wireshark抓包分析
7. **安全考虑**：输入验证、访问控制、防DoS攻击

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现一个FTP服务器，支持文件上传下载
2. **挑战2**：添加HTTPS支持，使用mbedTLS加密通信
3. **挑战3**：实现MQTT客户端，连接到云平台
4. **挑战4**：优化TCP性能，达到100Mbps吞吐量
5. **挑战5**：实现网络配置Web界面，支持动态修改IP地址

## 完整代码

完整的项目代码可以在GitHub上找到：

```text
GitHub仓库: https://github.com/embedded-knowledge/lwip-tutorial
```

项目包含：
- STM32F407完整工程代码
- lwIP 2.1.3移植代码
- Web服务器示例
- TCP/UDP客户端服务器示例
- 性能测试代码
- 调试工具脚本

## 下一步

建议继续学习：

- **Modbus TCP协议** - 学习工业以太网通信
- **OPC UA协议** - 学习工业4.0通信标准
- **CoAP协议** - 学习物联网轻量级协议
- **WebSocket协议** - 学习实时双向通信
- **MQTT协议深入** - 学习物联网消息队列

## 参考资料

1. **lwIP官方文档**
   - 官网：https://savannah.nongnu.org/projects/lwip/
   - Wiki：https://lwip.wikia.com/

2. **STM32以太网应用笔记**
   - AN3966: LwIP TCP/IP stack demonstration for STM32F4x7 microcontrollers
   - AN4044: Ethernet on STM32F107 microcontroller

3. **TCP/IP协议书籍**
   - 《TCP/IP详解 卷1：协议》- W. Richard Stevens
   - 《嵌入式网络那些事》- 朱晓明

4. **在线资源**
   - lwIP邮件列表：https://lists.nongnu.org/mailman/listinfo/lwip-users
   - STM32社区：https://community.st.com/
   - Stack Overflow lwIP标签

5. **开源项目参考**
   - FreeRTOS+TCP：https://www.freertos.org/FreeRTOS-Plus/FreeRTOS_Plus_TCP/
   - uIP：http://www.sics.se/~adam/uip/
   - picoTCP：https://github.com/tass-belgium/picotcp

## 常见问题FAQ

**Q1: lwIP和FreeRTOS+TCP有什么区别？**

A: lwIP是独立的协议栈，可以在有无操作系统下运行；FreeRTOS+TCP是专门为FreeRTOS设计的，集成度更高但只能在FreeRTOS上运行。lwIP社区更活跃，支持更广泛。

**Q2: 如何选择合适的内存配置？**

A: 根据应用需求：
- 简单应用（1-2个连接）：MEM_SIZE=5KB, TCP_PCB=2
- 中等应用（5-10个连接）：MEM_SIZE=10KB, TCP_PCB=5
- 复杂应用（>10个连接）：MEM_SIZE=20KB, TCP_PCB=10+

**Q3: lwIP能达到多高的吞吐量？**

A: 在STM32F4上，优化后可以达到：
- 10/100M以太网：80-95Mbps
- 受限因素：CPU频率、DMA配置、内存带宽

**Q4: 如何处理lwIP的线程安全问题？**

A: 使用RTOS模式时，lwIP内部已经处理了线程安全。应用层需要注意：
- 不要在多个任务中同时操作同一个PCB
- 使用消息队列在任务间传递数据
- 使用互斥锁保护共享资源

**Q5: lwIP支持哪些RTOS？**

A: lwIP支持多种RTOS：
- FreeRTOS（最常用）
- RT-Thread
- μC/OS-II/III
- ThreadX
- 也可以在裸机上运行（NO_SYS模式）

---

*本教程持续更新中，欢迎反馈和建议！*

