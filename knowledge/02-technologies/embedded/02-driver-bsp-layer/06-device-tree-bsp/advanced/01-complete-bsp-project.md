---
title: "完整BSP开发实战项目"
description: "通过完整的实战项目，从零开始为自定义硬件板卡开发完整的BSP包，包括Bootloader移植、内核适配、驱动集成、文件系统构建和系统测试验证"
slug: "complete-bsp-project"

# 分类信息
domain: "驱动与BSP层"
module: "设备树与板级支持"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - BSP项目
  - 板卡开发
  - 系统集成
  - 完整开发流程
  - 实战项目
prerequisites:
  - "device-tree-basics"
  - "device-tree-writing"
  - "bsp-development"
related_contents: []

# 学习信息
estimated_time: 220
difficulty_score: 9

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2024-01-15"
updated_at: "2024-01-15"
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
  - BSP开发项目
  - 完整BSP
  - 板卡开发
  - 系统集成
  - 嵌入式Linux
cover_image: ""
---

# 完整BSP开发实战项目

## 项目概述

本项目将带你完成一个真实的BSP开发全流程，为一块基于NXP i.MX6UL处理器的自定义工业控制板开发完整的板级支持包。通过本项目，你将：

- 从硬件原理图分析开始，完成完整的BSP开发
- 移植U-Boot Bootloader并实现自定义功能
- 适配Linux内核并编写完整的设备树
- 开发和集成所有外设驱动程序
- 构建定制化的根文件系统
- 进行系统集成测试和性能优化
- 交付可直接部署的完整BSP包

### 项目目标

**最终交付物**：
- 完整的BSP源码包
- 可启动的系统镜像
- 完整的技术文档
- 测试报告和验证结果

**技能提升**：
- 掌握完整的BSP开发流程
- 具备独立开发新板卡BSP的能力
- 理解硬件与软件的协同开发
- 积累实际项目经验

## 项目背景

### 硬件平台介绍

**目标板卡：MY-IMX6UL 工业控制板 v1.0**

这是一块专为工业自动化设计的控制板，具有以下特点：

**核心配置**：
```
处理器：NXP i.MX6UL (ARM Cortex-A7, 528MHz)
内存：512MB DDR3L (16-bit, MT41K256M16TW-107)
存储：8GB eMMC (MTFC8GACAECN-4M)
电源：PMIC PF3000 (多路输出，支持动态调压)
```

**通信接口**：
```
以太网：10/100M (RMII, LAN8720A PHY)
串口：2x UART (调试串口 + RS485)
CAN总线：2x CAN2.0B (TJA1050收发器)
USB：1x USB OTG + 1x USB Host
```

**工业接口**：
```
数字IO：16路隔离数字输入 + 8路继电器输出
模拟输入：4路12-bit ADC (0-10V)
SPI：1x SPI (外部Flash W25Q128)
I2C：2x I2C (EEPROM AT24C256 + RTC DS1307 + 传感器扩展)
```

**其他特性**：
```
显示：RGB LCD接口 (支持800x480)
存储扩展：SD卡槽
看门狗：硬件看门狗
RTC：带备用电池的实时时钟
工作温度：-40°C ~ +85°C
```

### 开发环境要求

**硬件要求**：
- 开发主机（Ubuntu 20.04/22.04 LTS）
- 目标板卡（MY-IMX6UL v1.0）
- USB转串口线（用于调试）
- 网线（用于网络调试）
- SD卡（8GB以上，用于系统启动）
- 电源适配器（12V/2A）

**软件要求**：

```bash
# 安装交叉编译工具链
sudo apt-get update
sudo apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# 安装开发工具
sudo apt-get install -y build-essential git vim device-tree-compiler \
    u-boot-tools bison flex libssl-dev libncurses5-dev bc

# 安装调试工具
sudo apt-get install -y minicom picocom screen \
    i2c-tools can-utils mtd-utils

# 安装网络服务
sudo apt-get install -y tftpd-hpa nfs-kernel-server

# 验证工具链
arm-linux-gnueabihf-gcc --version
```

## 项目阶段规划

本项目分为7个主要阶段，预计总工时220分钟（约3.5小时）：

### 阶段1：项目准备与硬件分析（30分钟）
- 搭建开发环境
- 分析硬件原理图
- 制定开发计划
- 准备参考代码

### 阶段2：U-Boot移植（40分钟）
- 配置U-Boot
- 适配板级代码
- 编写U-Boot设备树
- 测试基本启动功能

### 阶段3：Linux内核移植（40分钟）
- 配置内核
- 编写内核设备树
- 编译内核和模块
- 测试内核启动

### 阶段4：驱动开发与集成（50分钟）
- 开发自定义驱动
- 集成标准驱动
- 调试所有外设
- 验证驱动功能

### 阶段5：根文件系统构建（30分钟）
- 使用Buildroot构建
- 添加应用程序
- 配置系统服务
- 制作文件系统镜像

### 阶段6：系统集成与测试（20分钟）
- 制作完整系统镜像
- 功能测试
- 性能测试
- 稳定性测试

### 阶段7：文档编写与交付（10分钟）
- 编写技术文档
- 整理源码包
- 准备交付物
- 项目总结

## 阶段1：项目准备与硬件分析

### 1.1 创建项目目录结构

首先创建规范的项目目录结构：

```bash
# 创建项目根目录
mkdir -p ~/bsp-project/my-imx6ul-bsp
cd ~/bsp-project/my-imx6ul-bsp

# 创建目录结构
mkdir -p {bootloader,kernel,rootfs,drivers,tools,docs,output}
mkdir -p output/{images,logs,temp}
mkdir -p docs/{hardware,software,test}

# 创建README
cat > README.md << 'EOF'
# MY-IMX6UL BSP v1.0

## 项目简介
本BSP为MY-IMX6UL工业控制板提供完整的软件支持。

## 目录结构
- bootloader/  : U-Boot源码和配置
- kernel/      : Linux内核源码和配置
- rootfs/      : 根文件系统
- drivers/     : 自定义驱动
- tools/       : 开发工具和脚本
- docs/        : 项目文档
- output/      : 编译输出

## 快速开始
详见 docs/software/quick-start.md

## 版本信息
- BSP版本：v1.0
- U-Boot版本：2023.10
- 内核版本：6.1.0
- Buildroot版本：2023.11

## 联系方式
技术支持：support@example.com
EOF

echo "项目目录结构创建完成"
tree -L 2
```

### 1.2 下载源码

下载所需的源码包：

```bash
# 下载U-Boot
cd bootloader
git clone https://github.com/u-boot/u-boot.git
cd u-boot
git checkout v2023.10
cd ../..

# 下载Linux内核
cd kernel
git clone --depth=1 --branch v6.1 \
    https://github.com/torvalds/linux.git linux-6.1
cd ..

# 下载Buildroot
cd rootfs
git clone https://github.com/buildroot/buildroot.git
cd buildroot
git checkout 2023.11
cd ../..

echo "源码下载完成"
```

### 1.3 硬件原理图分析

创建硬件分析文档：

```bash
cat > docs/hardware/hardware-analysis.md << 'EOF'
# MY-IMX6UL 硬件分析文档

## 1. 处理器配置

### CPU
- 型号：i.MX6UL (MCIMX6G2CVM05AB)
- 架构：ARM Cortex-A7
- 主频：528MHz
- 封装：289-pin MAPBGA

### 内存系统
- DDR3L：MT41K256M16TW-107
- 容量：512MB (256M x 16bit)
- 频率：533MHz
- 位宽：16-bit
- 电压：1.35V

### 存储
- eMMC：MTFC8GACAECN-4M
- 容量：8GB
- 接口：USDHC2 (4-bit)
- 速度：HS200

## 2. 电源系统

### PMIC
- 型号：PF3000
- 输入：12V DC
- 输出：
  - SW1A: 1.375V (VDD_ARM_CAP)
  - SW1B: 1.375V (VDD_SOC_CAP)
  - SW2: 3.15V (NVCC_SD2)
  - SW3: 1.5V (NVCC_ENET)
  - VGEN1: 1.5V (NVCC_SD1)
  - VGEN2: 2.8V (NVCC_EPDC)
  - VGEN3: 2.5V (V_2P5)
  - VGEN4: 1.8V (NVCC_EPDC)
  - VGEN5: 2.8V (NVCC_EPDC)
  - VGEN6: 3.3V (V_3P3)

## 3. 时钟系统

### 晶振
- 主晶振：24MHz (Y1)
- RTC晶振：32.768KHz (Y2)

### PLL配置
- PLL1 (ARM): 528MHz
- PLL2 (System): 528MHz
- PLL3 (USB): 480MHz
- PLL4 (Audio): 650MHz
- PLL5 (Video): 650MHz
- PLL6 (ENET): 50MHz
- PLL7 (USB Host): 480MHz

## 4. 外设配置

### 以太网
- PHY：LAN8720A
- 接口：RMII
- 地址：0x00
- 复位：GPIO5_IO07
- 中断：GPIO5_IO08
- 时钟：50MHz (来自PLL6)

### 串口
- UART1 (调试)：
  - TX: UART1_TX_DATA (GPIO1_IO16)
  - RX: UART1_RX_DATA (GPIO1_IO17)
  - 波特率：115200
  
- UART2 (RS485)：
  - TX: UART2_TX_DATA (GPIO1_IO20)
  - RX: UART2_RX_DATA (GPIO1_IO21)
  - RTS: UART2_RTS_B (GPIO1_IO22)
  - CTS: UART2_CTS_B (GPIO1_IO23)
  - DE: GPIO1_IO24 (RS485方向控制)

### CAN总线
- CAN1：
  - TX: FLEXCAN1_TX (GPIO1_IO06)
  - RX: FLEXCAN1_RX (GPIO1_IO07)
  - 收发器：TJA1050
  
- CAN2：
  - TX: FLEXCAN2_TX (GPIO1_IO14)
  - RX: FLEXCAN2_RX (GPIO1_IO15)
  - 收发器：TJA1050

### USB
- USB OTG1：
  - DP/DM: USB_OTG1_DP/DM
  - VBUS: GPIO1_IO04 (控制)
  - ID: USB_OTG1_ID
  
- USB Host：
  - DP/DM: USB_OTG2_DP/DM
  - VBUS: 固定供电

### I2C
- I2C1 (系统)：
  - SCL: I2C1_SCL (GPIO1_IO02)
  - SDA: I2C1_SDA (GPIO1_IO03)
  - 设备：
    - EEPROM (AT24C256): 0x50
    - RTC (DS1307): 0x68
    - PMIC (PF3000): 0x08
  
- I2C2 (扩展)：
  - SCL: I2C2_SCL (GPIO1_IO30)
  - SDA: I2C2_SDA (GPIO1_IO31)
  - 设备：
    - 温度传感器 (TMP102): 0x48
    - 湿度传感器 (SHT31): 0x44

### SPI
- ECSPI1：
  - MISO: ECSPI1_MISO (GPIO4_IO22)
  - MOSI: ECSPI1_MOSI (GPIO4_IO23)
  - SCLK: ECSPI1_SCLK (GPIO4_IO24)
  - CS0: GPIO4_IO26
  - 设备：W25Q128 (16MB SPI Flash)

### GPIO
- 数字输入：GPIO3_IO00 ~ GPIO3_IO15 (16路，光耦隔离)
- 继电器输出：GPIO4_IO00 ~ GPIO4_IO07 (8路)
- LED指示：
  - 电源LED：固定点亮
  - 状态LED：GPIO1_IO09 (心跳)
  - 用户LED1：GPIO1_IO10
  - 用户LED2：GPIO1_IO11
- 按键：
  - 复位按键：RESET_B (硬件复位)
  - 用户按键：GPIO1_IO18

### ADC
- ADC1：
  - CH0: GPIO1_IO00 (0-10V输入，分压)
  - CH1: GPIO1_IO01 (0-10V输入，分压)
  - CH2: GPIO1_IO08 (0-10V输入，分压)
  - CH3: GPIO1_IO09 (0-10V输入，分压)

### LCD
- LCD接口：RGB888
- 分辨率：800x480
- 背光：PWM1 (GPIO1_IO08)

### SD卡
- USDHC1：
  - CLK: SD1_CLK
  - CMD: SD1_CMD
  - DATA0-3: SD1_DATA0-3
  - CD: GPIO1_IO19 (卡检测)

## 5. 引脚复用总结

| 功能 | 引脚 | 复用 | 备注 |
|------|------|------|------|
| UART1_TX | GPIO1_IO16 | ALT0 | 调试串口 |
| UART1_RX | GPIO1_IO17 | ALT0 | 调试串口 |
| ENET1_MDIO | GPIO2_IO03 | ALT4 | 以太网 |
| ENET1_MDC | GPIO2_IO02 | ALT4 | 以太网 |
| I2C1_SCL | GPIO1_IO02 | ALT0 | 系统I2C |
| I2C1_SDA | GPIO1_IO03 | ALT0 | 系统I2C |

## 6. 参考平台

选择NXP官方的i.MX6UL EVK作为参考平台：
- 相同的SoC型号
- 相似的外设配置
- 完善的BSP支持

主要差异：
- PHY芯片不同（EVK使用KSZ8081，我们使用LAN8720A）
- 内存容量不同（EVK 256MB，我们512MB）
- 增加了工业接口（数字IO、继电器、RS485）

EOF

echo "硬件分析文档创建完成"
```

### 1.4 制定开发计划

创建开发计划文档：

```bash
cat > docs/software/development-plan.md << 'EOF'
# BSP开发计划

## 开发任务清单

### U-Boot移植任务
- [ ] 复制参考板配置文件
- [ ] 修改板级配置（DDR、时钟、电源）
- [ ] 创建板级目录和代码
- [ ] 编写U-Boot设备树
- [ ] 适配PHY驱动（LAN8720A）
- [ ] 测试基本启动
- [ ] 测试网络功能
- [ ] 测试eMMC读写

### 内核移植任务
- [ ] 配置内核选项
- [ ] 编写内核设备树
- [ ] 配置所有外设节点
- [ ] 编译内核和模块
- [ ] 测试内核启动
- [ ] 验证设备树加载

### 驱动开发任务
- [ ] 以太网驱动适配
- [ ] 串口驱动测试
- [ ] I2C设备驱动
- [ ] SPI Flash驱动
- [ ] CAN总线驱动
- [ ] GPIO驱动（LED、按键、数字IO）
- [ ] ADC驱动
- [ ] USB驱动
- [ ] SD卡驱动
- [ ] RTC驱动
- [ ] 看门狗驱动

### 文件系统任务
- [ ] 配置Buildroot
- [ ] 添加必要的软件包
- [ ] 创建启动脚本
- [ ] 添加测试工具
- [ ] 编译文件系统

### 测试任务
- [ ] 功能测试
- [ ] 性能测试
- [ ] 稳定性测试
- [ ] 文档编写

EOF

echo "开发计划创建完成"
```

## 阶段2：U-Boot移植

### 2.1 创建板级配置

```bash
cd ~/bsp-project/my-imx6ul-bsp/bootloader/u-boot

# 复制参考配置
cp configs/mx6ul_14x14_evk_defconfig configs/my_imx6ul_defconfig

# 编辑配置文件
cat > configs/my_imx6ul_defconfig << 'EOF'
CONFIG_ARM=y
CONFIG_ARCH_MX6=y
CONFIG_SYS_TEXT_BASE=0x87800000
CONFIG_SYS_MALLOC_LEN=0x2000000
CONFIG_SPL_LIBCOMMON_SUPPORT=y
CONFIG_SPL_LIBGENERIC_SUPPORT=y
CONFIG_NR_DRAM_BANKS=1
CONFIG_ENV_SIZE=0x2000
CONFIG_ENV_OFFSET=0x100000
CONFIG_MX6UL=y
CONFIG_TARGET_MY_IMX6UL=y
CONFIG_DM_GPIO=y
CONFIG_DEFAULT_DEVICE_TREE="my-imx6ul"
CONFIG_SPL_TEXT_BASE=0x00908000
CONFIG_SPL_MMC=y
CONFIG_SPL_SERIAL=y
CONFIG_SPL=y
CONFIG_SPL_LIBDISK_SUPPORT=y
CONFIG_DISTRO_DEFAULTS=y
CONFIG_SYS_EXTRA_OPTIONS="IMX_CONFIG=board/myvendor/my_imx6ul/imximage.cfg"
CONFIG_BOOTDELAY=3
CONFIG_BOOTCOMMAND="run findfdt; run findtee; run distro_bootcmd"
CONFIG_BOARD_EARLY_INIT_F=y
CONFIG_SPL_USB_HOST=y
CONFIG_SPL_USB_GADGET=y
CONFIG_SPL_USB_SDP_SUPPORT=y
CONFIG_SYS_MEMTEST_START=0x80000000
CONFIG_SYS_MEMTEST_END=0xa0000000
CONFIG_CMD_MEMTEST=y
CONFIG_CMD_GPIO=y
CONFIG_CMD_I2C=y
CONFIG_CMD_MMC=y
CONFIG_CMD_USB=y
CONFIG_CMD_DHCP=y
CONFIG_CMD_MII=y
CONFIG_CMD_PING=y
CONFIG_CMD_CACHE=y
CONFIG_CMD_EXT2=y
CONFIG_CMD_EXT4=y
CONFIG_CMD_EXT4_WRITE=y
CONFIG_CMD_FAT=y
CONFIG_CMD_FS_GENERIC=y
CONFIG_OF_CONTROL=y
CONFIG_ENV_OVERWRITE=y
CONFIG_ENV_IS_IN_MMC=y
CONFIG_SYS_RELOC_GD_ENV_ADDR=y
CONFIG_DM=y
CONFIG_FSL_USDHC=y
CONFIG_PHYLIB=y
CONFIG_PHY_SMSC=y
CONFIG_FEC_MXC=y
CONFIG_MII=y
CONFIG_PINCTRL=y
CONFIG_PINCTRL_IMX6=y
CONFIG_DM_REGULATOR=y
CONFIG_DM_REGULATOR_FIXED=y
CONFIG_DM_REGULATOR_GPIO=y
CONFIG_MXC_UART=y
CONFIG_USB=y
CONFIG_DM_USB=y
CONFIG_USB_EHCI_HCD=y
CONFIG_USB_STORAGE=y
CONFIG_USB_GADGET=y
CONFIG_USB_GADGET_MANUFACTURER="FSL"
CONFIG_USB_GADGET_VENDOR_NUM=0x0525
CONFIG_USB_GADGET_PRODUCT_NUM=0xa4a5
CONFIG_CI_UDC=y
CONFIG_USB_GADGET_DOWNLOAD=y
CONFIG_USB_ETHER=y
CONFIG_USB_ETH_CDC=y
CONFIG_USB_HOST_ETHER=y
CONFIG_USB_ETHER_ASIX=y
CONFIG_USB_ETHER_SMSC95XX=y
CONFIG_OF_LIBFDT=y
EOF
```

### 2.2 创建板级目录和代码

```bash
# 创建板级目录
mkdir -p board/myvendor/my_imx6ul

# 创建Makefile
cat > board/myvendor/my_imx6ul/Makefile << 'EOF'
# SPDX-License-Identifier: GPL-2.0+

obj-y := my_imx6ul.o

ifdef CONFIG_SPL_BUILD
obj-y += spl.o
endif
EOF

# 创建Kconfig
cat > board/myvendor/my_imx6ul/Kconfig << 'EOF'
if TARGET_MY_IMX6UL

config SYS_BOARD
	default "my_imx6ul"

config SYS_VENDOR
	default "myvendor"

config SYS_CONFIG_NAME
	default "my_imx6ul"

endif
EOF

# 创建MAINTAINERS
cat > board/myvendor/my_imx6ul/MAINTAINERS << 'EOF'
MY-IMX6UL BOARD
M:	Your Name <your.email@example.com>
S:	Maintained
F:	board/myvendor/my_imx6ul/
F:	include/configs/my_imx6ul.h
F:	configs/my_imx6ul_defconfig
EOF
```

### 2.3 创建板级初始化代码

```bash
cat > board/myvendor/my_imx6ul/my_imx6ul.c << 'EOF'
// SPDX-License-Identifier: GPL-2.0+
/*
 * Copyright (C) 2024 Your Company
 */

#include <common.h>
#include <init.h>
#include <asm/arch/clock.h>
#include <asm/arch/iomux.h>
#include <asm/arch/imx-regs.h>
#include <asm/arch/crm_regs.h>
#include <asm/arch/mx6-pins.h>
#include <asm/arch/sys_proto.h>
#include <asm/gpio.h>
#include <asm/mach-imx/iomux-v3.h>
#include <asm/mach-imx/boot_mode.h>
#include <asm/io.h>
#include <linux/sizes.h>
#include <mmc.h>
#include <fsl_esdhc_imx.h>
#include <miiphy.h>
#include <netdev.h>
#include <usb.h>
#include <usb/ehci-ci.h>

DECLARE_GLOBAL_DATA_PTR;

#define UART_PAD_CTRL  (PAD_CTL_PKE | PAD_CTL_PUE |		\
	PAD_CTL_PUS_100K_UP | PAD_CTL_SPEED_MED |		\
	PAD_CTL_DSE_40ohm   | PAD_CTL_SRE_FAST  | PAD_CTL_HYS)

#define USDHC_PAD_CTRL (PAD_CTL_PKE | PAD_CTL_PUE |		\
	PAD_CTL_PUS_22K_UP  | PAD_CTL_SPEED_LOW |		\
	PAD_CTL_DSE_80ohm   | PAD_CTL_SRE_FAST  | PAD_CTL_HYS)

#define ENET_PAD_CTRL  (PAD_CTL_PUS_100K_UP | PAD_CTL_PUE |     \
	PAD_CTL_SPEED_HIGH   |                                   \
	PAD_CTL_DSE_48ohm   | PAD_CTL_SRE_FAST)

#define ENET_CLK_PAD_CTRL  (PAD_CTL_DSE_40ohm   | PAD_CTL_SRE_FAST)

#define ENET_RX_PAD_CTRL  (PAD_CTL_PKE | PAD_CTL_PUE |          \
	PAD_CTL_SPEED_HIGH   | PAD_CTL_SRE_FAST)

int dram_init(void)
{
	gd->ram_size = imx_ddr_size();
	return 0;
}

static iomux_v3_cfg_t const uart1_pads[] = {
	MX6_PAD_UART1_TX_DATA__UART1_DCE_TX | MUX_PAD_CTRL(UART_PAD_CTRL),
	MX6_PAD_UART1_RX_DATA__UART1_DCE_RX | MUX_PAD_CTRL(UART_PAD_CTRL),
};

static iomux_v3_cfg_t const usdhc2_pads[] = {
	MX6_PAD_NAND_RE_B__USDHC2_CLK | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_WE_B__USDHC2_CMD | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA00__USDHC2_DATA0 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA01__USDHC2_DATA1 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA02__USDHC2_DATA2 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA03__USDHC2_DATA3 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
};

static iomux_v3_cfg_t const fec1_pads[] = {
	MX6_PAD_GPIO1_IO06__ENET1_MDIO | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_GPIO1_IO07__ENET1_MDC | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_EN__ENET1_RX_EN | MUX_PAD_CTRL(ENET_RX_PAD_CTRL),
	MX6_PAD_ENET1_RX_ER__ENET1_RX_ER | MUX_PAD_CTRL(ENET_RX_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA0__ENET1_RDATA00 | MUX_PAD_CTRL(ENET_RX_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA1__ENET1_RDATA01 | MUX_PAD_CTRL(ENET_RX_PAD_CTRL),
	MX6_PAD_ENET1_TX_EN__ENET1_TX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA0__ENET1_TDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA1__ENET1_TDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_CLK__ENET1_REF_CLK1 | MUX_PAD_CTRL(ENET_CLK_PAD_CTRL),
	/* PHY Reset */
	MX6_PAD_SNVS_TAMPER7__GPIO5_IO07 | MUX_PAD_CTRL(NO_PAD_CTRL),
};

static void setup_iomux_uart(void)
{
	imx_iomux_v3_setup_multiple_pads(uart1_pads, ARRAY_SIZE(uart1_pads));
}

static void setup_iomux_fec(int fec_id)
{
	imx_iomux_v3_setup_multiple_pads(fec1_pads, ARRAY_SIZE(fec1_pads));
	
	/* Reset PHY */
	gpio_request(IMX_GPIO_NR(5, 7), "enet_rst");
	gpio_direction_output(IMX_GPIO_NR(5, 7), 0);
	mdelay(10);
	gpio_set_value(IMX_GPIO_NR(5, 7), 1);
	mdelay(50);
}

int board_early_init_f(void)
{
	setup_iomux_uart();
	return 0;
}

int board_init(void)
{
	/* Address of boot parameters */
	gd->bd->bi_boot_params = PHYS_SDRAM + 0x100;

	setup_iomux_fec(CONFIG_FEC_ENET_DEV);

	return 0;
}

int board_mmc_get_env_dev(int devno)
{
	return devno;
}

int board_late_init(void)
{
	return 0;
}

int checkboard(void)
{
	puts("Board: MY-IMX6UL v1.0\n");
	return 0;
}
EOF
```

### 2.4 创建U-Boot设备树

```bash
cat > arch/arm/dts/my-imx6ul.dts << 'EOF'
// SPDX-License-Identifier: GPL-2.0+

/dts-v1/;

#include "imx6ul.dtsi"

/ {
	model = "MY-IMX6UL Industrial Control Board";
	compatible = "myvendor,my-imx6ul", "fsl,imx6ul";

	chosen {
		stdout-path = &uart1;
	};

	memory@80000000 {
		device_type = "memory";
		reg = <0x80000000 0x20000000>;
	};
};

&uart1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart1>;
	status = "okay";
};

&usdhc2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_usdhc2>;
	bus-width = <4>;
	non-removable;
	status = "okay";
};

&fec1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet1>;
	phy-mode = "rmii";
	phy-handle = <&ethphy0>;
	status = "okay";

	mdio {
		#address-cells = <1>;
		#size-cells = <0>;

		ethphy0: ethernet-phy@0 {
			compatible = "ethernet-phy-ieee802.3-c22";
			reg = <0>;
			smsc,disable-energy-detect;
		};
	};
};

&iomuxc {
	pinctrl_uart1: uart1grp {
		fsl,pins = <
			MX6UL_PAD_UART1_TX_DATA__UART1_DCE_TX 0x1b0b1
			MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1
		>;
	};

	pinctrl_usdhc2: usdhc2grp {
		fsl,pins = <
			MX6UL_PAD_NAND_RE_B__USDHC2_CLK     0x10069
			MX6UL_PAD_NAND_WE_B__USDHC2_CMD     0x17059
			MX6UL_PAD_NAND_DATA00__USDHC2_DATA0 0x17059
			MX6UL_PAD_NAND_DATA01__USDHC2_DATA1 0x17059
			MX6UL_PAD_NAND_DATA02__USDHC2_DATA2 0x17059
			MX6UL_PAD_NAND_DATA03__USDHC2_DATA3 0x17059
		>;
	};

	pinctrl_enet1: enet1grp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO06__ENET1_MDIO        0x1b0b0
			MX6UL_PAD_GPIO1_IO07__ENET1_MDC         0x1b0b0
			MX6UL_PAD_ENET1_RX_EN__ENET1_RX_EN      0x1b0b0
			MX6UL_PAD_ENET1_RX_ER__ENET1_RX_ER      0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA0__ENET1_RDATA00 0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA1__ENET1_RDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_EN__ENET1_TX_EN      0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA0__ENET1_TDATA00 0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA1__ENET1_TDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_CLK__ENET1_REF_CLK1  0x4001b031
			MX6UL_PAD_SNVS_TAMPER7__GPIO5_IO07      0x79
		>;
	};
};
EOF
```

### 2.5 编译和测试U-Boot

```bash
# 设置环境变量
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-

# 配置
make my_imx6ul_defconfig

# 编译
make -j$(nproc)

# 检查输出
ls -lh u-boot.imx

echo "U-Boot编译完成，可以烧录测试"
```

## 阶段3：Linux内核移植

### 3.1 配置内核

```bash
cd ~/bsp-project/my-imx6ul-bsp/kernel/linux-6.1

# 使用imx_v6_v7_defconfig作为基础
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- imx_v6_v7_defconfig

# 进行定制配置
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig

# 保存配置
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- savedefconfig
cp defconfig arch/arm/configs/my_imx6ul_defconfig
```

### 3.2 创建内核设备树

由于设备树文件较大，这里展示关键部分的创建：

```bash
cat > arch/arm/boot/dts/my-imx6ul.dts << 'EOF'
// SPDX-License-Identifier: (GPL-2.0 OR MIT)

/dts-v1/;

#include "imx6ul.dtsi"

/ {
	model = "MY-IMX6UL Industrial Control Board";
	compatible = "myvendor,my-imx6ul", "fsl,imx6ul";

	chosen {
		stdout-path = &uart1;
	};

	memory@80000000 {
		device_type = "memory";
		reg = <0x80000000 0x20000000>;
	};

	regulators {
		compatible = "simple-bus";
		#address-cells = <1>;
		#size-cells = <0>;

		reg_3v3: regulator@0 {
			compatible = "regulator-fixed";
			reg = <0>;
			regulator-name = "3V3";
			regulator-min-microvolt = <3300000>;
			regulator-max-microvolt = <3300000>;
			regulator-always-on;
		};
	};

	leds {
		compatible = "gpio-leds";
		pinctrl-names = "default";
		pinctrl-0 = <&pinctrl_leds>;

		led-status {
			label = "status";
			gpios = <&gpio1 9 GPIO_ACTIVE_LOW>;
			linux,default-trigger = "heartbeat";
		};

		led-user1 {
			label = "user1";
			gpios = <&gpio1 10 GPIO_ACTIVE_LOW>;
			default-state = "off";
		};

		led-user2 {
			label = "user2";
			gpios = <&gpio1 11 GPIO_ACTIVE_LOW>;
			default-state = "off";
		};
	};

	gpio-keys {
		compatible = "gpio-keys";
		pinctrl-names = "default";
		pinctrl-0 = <&pinctrl_keys>;

		user-button {
			label = "User Button";
			gpios = <&gpio1 18 GPIO_ACTIVE_LOW>;
			linux,code = <KEY_ENTER>;
			debounce-interval = <50>;
		};
	};
};

/* 串口配置 */
&uart1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart1>;
	status = "okay";
};

&uart2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart2>;
	uart-has-rtscts;
	linux,rs485-enabled-at-boot-time;
	status = "okay";
};

/* eMMC配置 */
&usdhc2 {
	pinctrl-names = "default", "state_100mhz", "state_200mhz";
	pinctrl-0 = <&pinctrl_usdhc2>;
	pinctrl-1 = <&pinctrl_usdhc2_100mhz>;
	pinctrl-2 = <&pinctrl_usdhc2_200mhz>;
	bus-width = <4>;
	non-removable;
	status = "okay";
};

/* 以太网配置 */
&fec1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet1>;
	phy-mode = "rmii";
	phy-handle = <&ethphy0>;
	phy-reset-gpios = <&gpio5 7 GPIO_ACTIVE_LOW>;
	phy-reset-duration = <26>;
	status = "okay";

	mdio {
		#address-cells = <1>;
		#size-cells = <0>;

		ethphy0: ethernet-phy@0 {
			compatible = "ethernet-phy-ieee802.3-c22";
			reg = <0>;
			smsc,disable-energy-detect;
			clocks = <&clks IMX6UL_CLK_ENET_REF>;
			clock-names = "rmii-ref";
		};
	};
};

/* I2C配置 */
&i2c1 {
	clock-frequency = <400000>;
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_i2c1>;
	status = "okay";

	eeprom@50 {
		compatible = "atmel,24c256";
		reg = <0x50>;
		pagesize = <64>;
	};

	rtc@68 {
		compatible = "dallas,ds1307";
		reg = <0x68>;
	};
};

&i2c2 {
	clock-frequency = <100000>;
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_i2c2>;
	status = "okay";

	temp-sensor@48 {
		compatible = "ti,tmp102";
		reg = <0x48>;
	};
};

/* SPI配置 */
&ecspi1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_ecspi1>;
	cs-gpios = <&gpio4 26 GPIO_ACTIVE_LOW>;
	status = "okay";

	flash@0 {
		compatible = "jedec,spi-nor";
		reg = <0>;
		spi-max-frequency = <20000000>;
	};
};

/* CAN配置 */
&can1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_flexcan1>;
	status = "okay";
};

&can2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_flexcan2>;
	status = "okay";
};

/* USB配置 */
&usbotg1 {
	dr_mode = "otg";
	status = "okay";
};

&usbotg2 {
	dr_mode = "host";
	status = "okay";
};

/* ADC配置 */
&adc1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_adc1>;
	vref-supply = <&reg_3v3>;
	status = "okay";
};

/* 引脚配置 */
&iomuxc {
	pinctrl_uart1: uart1grp {
		fsl,pins = <
			MX6UL_PAD_UART1_TX_DATA__UART1_DCE_TX 0x1b0b1
			MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1
		>;
	};

	pinctrl_uart2: uart2grp {
		fsl,pins = <
			MX6UL_PAD_UART2_TX_DATA__UART2_DCE_TX 0x1b0b1
			MX6UL_PAD_UART2_RX_DATA__UART2_DCE_RX 0x1b0b1
			MX6UL_PAD_UART2_CTS_B__UART2_DCE_CTS  0x1b0b1
			MX6UL_PAD_UART2_RTS_B__UART2_DCE_RTS  0x1b0b1
		>;
	};

	pinctrl_usdhc2: usdhc2grp {
		fsl,pins = <
			MX6UL_PAD_NAND_RE_B__USDHC2_CLK     0x10069
			MX6UL_PAD_NAND_WE_B__USDHC2_CMD     0x17059
			MX6UL_PAD_NAND_DATA00__USDHC2_DATA0 0x17059
			MX6UL_PAD_NAND_DATA01__USDHC2_DATA1 0x17059
			MX6UL_PAD_NAND_DATA02__USDHC2_DATA2 0x17059
			MX6UL_PAD_NAND_DATA03__USDHC2_DATA3 0x17059
		>;
	};

	pinctrl_usdhc2_100mhz: usdhc2grp100mhz {
		fsl,pins = <
			MX6UL_PAD_NAND_RE_B__USDHC2_CLK     0x100b9
			MX6UL_PAD_NAND_WE_B__USDHC2_CMD     0x170b9
			MX6UL_PAD_NAND_DATA00__USDHC2_DATA0 0x170b9
			MX6UL_PAD_NAND_DATA01__USDHC2_DATA1 0x170b9
			MX6UL_PAD_NAND_DATA02__USDHC2_DATA2 0x170b9
			MX6UL_PAD_NAND_DATA03__USDHC2_DATA3 0x170b9
		>;
	};

	pinctrl_usdhc2_200mhz: usdhc2grp200mhz {
		fsl,pins = <
			MX6UL_PAD_NAND_RE_B__USDHC2_CLK     0x100f9
			MX6UL_PAD_NAND_WE_B__USDHC2_CMD     0x170f9
			MX6UL_PAD_NAND_DATA00__USDHC2_DATA0 0x170f9
			MX6UL_PAD_NAND_DATA01__USDHC2_DATA1 0x170f9
			MX6UL_PAD_NAND_DATA02__USDHC2_DATA2 0x170f9
			MX6UL_PAD_NAND_DATA03__USDHC2_DATA3 0x170f9
		>;
	};

	pinctrl_enet1: enet1grp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO06__ENET1_MDIO        0x1b0b0
			MX6UL_PAD_GPIO1_IO07__ENET1_MDC         0x1b0b0
			MX6UL_PAD_ENET1_RX_EN__ENET1_RX_EN      0x1b0b0
			MX6UL_PAD_ENET1_RX_ER__ENET1_RX_ER      0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA0__ENET1_RDATA00 0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA1__ENET1_RDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_EN__ENET1_TX_EN      0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA0__ENET1_TDATA00 0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA1__ENET1_TDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_CLK__ENET1_REF_CLK1  0x4001b031
			MX6UL_PAD_SNVS_TAMPER7__GPIO5_IO07      0x79
		>;
	};

	pinctrl_i2c1: i2c1grp {
		fsl,pins = <
			MX6UL_PAD_UART4_TX_DATA__I2C1_SCL 0x4001b8b0
			MX6UL_PAD_UART4_RX_DATA__I2C1_SDA 0x4001b8b0
		>;
	};

	pinctrl_i2c2: i2c2grp {
		fsl,pins = <
			MX6UL_PAD_UART5_TX_DATA__I2C2_SCL 0x4001b8b0
			MX6UL_PAD_UART5_RX_DATA__I2C2_SDA 0x4001b8b0
		>;
	};

	pinctrl_ecspi1: ecspi1grp {
		fsl,pins = <
			MX6UL_PAD_CSI_DATA07__ECSPI1_MISO 0x100b1
			MX6UL_PAD_CSI_DATA06__ECSPI1_MOSI 0x100b1
			MX6UL_PAD_CSI_DATA04__ECSPI1_SCLK 0x100b1
			MX6UL_PAD_CSI_DATA05__GPIO4_IO26  0x10b0
		>;
	};

	pinctrl_flexcan1: flexcan1grp {
		fsl,pins = <
			MX6UL_PAD_UART3_RTS_B__FLEXCAN1_RX 0x1b020
			MX6UL_PAD_UART3_CTS_B__FLEXCAN1_TX 0x1b020
		>;
	};

	pinctrl_flexcan2: flexcan2grp {
		fsl,pins = <
			MX6UL_PAD_UART2_RTS_B__FLEXCAN2_RX 0x1b020
			MX6UL_PAD_UART2_CTS_B__FLEXCAN2_TX 0x1b020
		>;
	};

	pinctrl_adc1: adc1grp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO00__GPIO1_IO00 0xb0
			MX6UL_PAD_GPIO1_IO01__GPIO1_IO01 0xb0
			MX6UL_PAD_GPIO1_IO08__GPIO1_IO08 0xb0
			MX6UL_PAD_GPIO1_IO09__GPIO1_IO09 0xb0
		>;
	};

	pinctrl_leds: ledsgrp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO09__GPIO1_IO09  0x17059
			MX6UL_PAD_GPIO1_IO10__GPIO1_IO10  0x17059
			MX6UL_PAD_GPIO1_IO11__GPIO1_IO11  0x17059
		>;
	};

	pinctrl_keys: keysgrp {
		fsl,pins = <
			MX6UL_PAD_UART1_CTS_B__GPIO1_IO18 0x80000000
		>;
	};
};
EOF

# 添加到Makefile
echo "dtb-\$(CONFIG_SOC_IMX6UL) += my-imx6ul.dtb" >> arch/arm/boot/dts/Makefile
```

### 3.3 编译内核

```bash
# 编译内核
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j$(nproc) zImage

# 编译设备树
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- dtbs

# 编译模块
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- modules

echo "内核编译完成"
ls -lh arch/arm/boot/zImage
ls -lh arch/arm/boot/dts/my-imx6ul.dtb
```

## 阶段4：驱动开发与集成

### 4.1 创建自定义GPIO驱动（数字IO和继电器）

```bash
mkdir -p ~/bsp-project/my-imx6ul-bsp/drivers/industrial-io

cat > ~/bsp-project/my-imx6ul-bsp/drivers/industrial-io/my-industrial-io.c << 'EOF'
// SPDX-License-Identifier: GPL-2.0
/*
 * Industrial I/O Driver for MY-IMX6UL
 * Provides 16 digital inputs and 8 relay outputs
 */

#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/of.h>
#include <linux/cdev.h>
#include <linux/fs.h>

#define DRIVER_NAME "my-industrial-io"
#define NUM_DI 16
#define NUM_DO 8

struct my_industrial_io {
	struct device *dev;
	struct gpio_descs *di_gpios;
	struct gpio_descs *do_gpios;
	struct cdev cdev;
	dev_t devt;
	struct class *class;
};

static int my_industrial_io_probe(struct platform_device *pdev)
{
	struct my_industrial_io *priv;
	int ret;

	priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = &pdev->dev;
	platform_set_drvdata(pdev, priv);

	/* Get digital input GPIOs */
	priv->di_gpios = devm_gpiod_get_array(&pdev->dev, "di", GPIOD_IN);
	if (IS_ERR(priv->di_gpios)) {
		dev_err(&pdev->dev, "Failed to get DI GPIOs\n");
		return PTR_ERR(priv->di_gpios);
	}

	/* Get digital output GPIOs */
	priv->do_gpios = devm_gpiod_get_array(&pdev->dev, "do", GPIOD_OUT_LOW);
	if (IS_ERR(priv->do_gpios)) {
		dev_err(&pdev->dev, "Failed to get DO GPIOs\n");
		return PTR_ERR(priv->do_gpios);
	}

	dev_info(&pdev->dev, "Industrial I/O driver probed successfully\n");
	dev_info(&pdev->dev, "DI: %d channels, DO: %d channels\n",
		 priv->di_gpios->ndescs, priv->do_gpios->ndescs);

	return 0;
}

static int my_industrial_io_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "Industrial I/O driver removed\n");
	return 0;
}

static const struct of_device_id my_industrial_io_of_match[] = {
	{ .compatible = "myvendor,industrial-io", },
	{ }
};
MODULE_DEVICE_TABLE(of, my_industrial_io_of_match);

static struct platform_driver my_industrial_io_driver = {
	.driver = {
		.name = DRIVER_NAME,
		.of_match_table = my_industrial_io_of_match,
	},
	.probe = my_industrial_io_probe,
	.remove = my_industrial_io_remove,
};

module_platform_driver(my_industrial_io_driver);

MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Industrial I/O Driver for MY-IMX6UL");
MODULE_LICENSE("GPL v2");
EOF

# 创建Makefile
cat > ~/bsp-project/my-imx6ul-bsp/drivers/industrial-io/Makefile << 'EOF'
obj-m += my-industrial-io.o

KDIR := ~/bsp-project/my-imx6ul-bsp/kernel/linux-6.1
PWD := $(shell pwd)

all:
	$(MAKE) ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
EOF
```

### 4.2 驱动测试脚本

```bash
mkdir -p ~/bsp-project/my-imx6ul-bsp/tools/test

cat > ~/bsp-project/my-imx6ul-bsp/tools/test/test-drivers.sh << 'EOF'
#!/bin/bash

echo "========================================="
echo "MY-IMX6UL 驱动测试脚本"
echo "========================================="

# 测试串口
echo -e "\n[1] 测试串口..."
if [ -c /dev/ttyS0 ]; then
    echo "✓ UART1 (调试串口) 存在"
else
    echo "✗ UART1 不存在"
fi

if [ -c /dev/ttyS1 ]; then
    echo "✓ UART2 (RS485) 存在"
else
    echo "✗ UART2 不存在"
fi

# 测试网络
echo -e "\n[2] 测试以太网..."
if ip link show eth0 &>/dev/null; then
    echo "✓ eth0 接口存在"
    ip addr show eth0 | grep "inet "
else
    echo "✗ eth0 接口不存在"
fi

# 测试I2C
echo -e "\n[3] 测试I2C设备..."
if command -v i2cdetect &>/dev/null; then
    echo "I2C1 总线扫描:"
    i2cdetect -y 0
    echo "I2C2 总线扫描:"
    i2cdetect -y 1
else
    echo "i2c-tools 未安装"
fi

# 测试SPI Flash
echo -e "\n[4] 测试SPI Flash..."
if [ -e /dev/mtd0 ]; then
    echo "✓ SPI Flash 设备存在"
    cat /proc/mtd
else
    echo "✗ SPI Flash 设备不存在"
fi

# 测试CAN
echo -e "\n[5] 测试CAN总线..."
if ip link show can0 &>/dev/null; then
    echo "✓ CAN0 接口存在"
fi
if ip link show can1 &>/dev/null; then
    echo "✓ CAN1 接口存在"
fi

# 测试USB
echo -e "\n[6] 测试USB..."
lsusb

# 测试GPIO LED
echo -e "\n[7] 测试LED..."
if [ -d /sys/class/leds/status ]; then
    echo "✓ 状态LED存在"
    echo "闪烁测试..."
    for i in {1..3}; do
        echo 1 > /sys/class/leds/status/brightness
        sleep 0.5
        echo 0 > /sys/class/leds/status/brightness
        sleep 0.5
    done
fi

# 测试ADC
echo -e "\n[8] 测试ADC..."
if [ -d /sys/bus/iio/devices/iio:device0 ]; then
    echo "✓ ADC设备存在"
    echo "ADC通道值:"
    for ch in {0..3}; do
        if [ -f /sys/bus/iio/devices/iio:device0/in_voltage${ch}_raw ]; then
            val=$(cat /sys/bus/iio/devices/iio:device0/in_voltage${ch}_raw)
            echo "  CH${ch}: $val"
        fi
    done
fi

# 测试RTC
echo -e "\n[9] 测试RTC..."
if command -v hwclock &>/dev/null; then
    hwclock -r
else
    echo "hwclock 命令不可用"
fi

# 测试存储
echo -e "\n[10] 测试存储设备..."
df -h

echo -e "\n========================================="
echo "测试完成"
echo "========================================="
EOF

chmod +x ~/bsp-project/my-imx6ul-bsp/tools/test/test-drivers.sh
```

## 阶段5：根文件系统构建

### 5.1 配置Buildroot

```bash
cd ~/bsp-project/my-imx6ul-bsp/rootfs/buildroot

# 使用基础配置
make imx6ulevk_defconfig

# 自定义配置
make menuconfig

# 关键配置项：
# Target options -> Target Architecture: ARM (little endian)
# Target options -> Target Architecture Variant: cortex-A7
# Toolchain -> Toolchain type: External toolchain
# System configuration -> System hostname: my-imx6ul
# System configuration -> Root password: (设置密码)
# Kernel -> Linux Kernel: 不选（我们使用自己编译的内核）
# Target packages -> Networking applications -> [*] dropbear
# Target packages -> Networking applications -> [*] can-utils
# Target packages -> Hardware handling -> [*] i2c-tools
# Target packages -> Hardware handling -> [*] mtd-utils
# Filesystem images -> [*] ext2/3/4 root filesystem
```

### 5.2 添加自定义文件

```bash
# 创建overlay目录
mkdir -p board/myvendor/my-imx6ul/rootfs-overlay/etc/init.d
mkdir -p board/myvendor/my-imx6ul/rootfs-overlay/usr/bin

# 创建启动脚本
cat > board/myvendor/my-imx6ul/rootfs-overlay/etc/init.d/S99custom << 'EOF'
#!/bin/sh

case "$1" in
  start)
        echo "Starting MY-IMX6UL custom services..."
        
        # 配置网络
        ifconfig eth0 up
        udhcpc -i eth0 -b
        
        # 配置CAN
        ip link set can0 type can bitrate 500000
        ip link set can0 up
        ip link set can1 type can bitrate 500000
        ip link set can1 up
        
        # 挂载数据分区
        if [ -b /dev/mmcblk1p3 ]; then
            mount /dev/mmcblk1p3 /data
        fi
        
        echo "Custom services started"
        ;;
  stop)
        echo "Stopping custom services..."
        ip link set can0 down
        ip link set can1 down
        ;;
  *)
        echo "Usage: $0 {start|stop}"
        exit 1
esac

exit 0
EOF

chmod +x board/myvendor/my-imx6ul/rootfs-overlay/etc/init.d/S99custom

# 复制测试脚本
cp ~/bsp-project/my-imx6ul-bsp/tools/test/test-drivers.sh \
   board/myvendor/my-imx6ul/rootfs-overlay/usr/bin/
chmod +x board/myvendor/my-imx6ul/rootfs-overlay/usr/bin/test-drivers.sh

# 配置Buildroot使用overlay
make menuconfig
# System configuration -> Root filesystem overlay directories
# 设置为: board/myvendor/my-imx6ul/rootfs-overlay
```

### 5.3 编译文件系统

```bash
# 编译
make -j$(nproc)

# 检查输出
ls -lh output/images/
# rootfs.ext4 - ext4格式根文件系统
# rootfs.tar - tar格式根文件系统

echo "根文件系统构建完成"
```

## 阶段6：系统集成与测试

### 6.1 创建完整系统镜像

```bash
cd ~/bsp-project/my-imx6ul-bsp

# 创建镜像制作脚本
cat > tools/make-sdcard.sh << 'EOF'
#!/bin/bash

DEVICE=$1

if [ -z "$DEVICE" ]; then
    echo "用法: $0 <设备>"
    echo "示例: $0 /dev/sdb"
    exit 1
fi

echo "警告: 这将擦除 $DEVICE 上的所有数据"
read -p "继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

set -e

echo "卸载分区..."
umount ${DEVICE}* 2>/dev/null || true

echo "创建分区表..."
sudo parted -s $DEVICE mklabel msdos
sudo parted -s $DEVICE mkpart primary fat32 1MiB 33MiB
sudo parted -s $DEVICE mkpart primary ext4 33MiB 545MiB
sudo parted -s $DEVICE mkpart primary ext4 545MiB 100%
sudo parted -s $DEVICE set 1 boot on

echo "格式化分区..."
sudo mkfs.vfat -F 32 -n BOOT ${DEVICE}1
sudo mkfs.ext4 -L rootfs ${DEVICE}2
sudo mkfs.ext4 -L data ${DEVICE}3

echo "烧录U-Boot..."
sudo dd if=bootloader/u-boot/u-boot.imx of=$DEVICE bs=1k seek=1 conv=fsync

echo "复制boot文件..."
mkdir -p /tmp/boot
sudo mount ${DEVICE}1 /tmp/boot
sudo cp kernel/linux-6.1/arch/arm/boot/zImage /tmp/boot/
sudo cp kernel/linux-6.1/arch/arm/boot/dts/my-imx6ul.dtb /tmp/boot/

# 创建boot脚本
cat > /tmp/boot.cmd << 'BOOTEOF'
setenv bootargs console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw
load mmc 1:1 ${loadaddr} zImage
load mmc 1:1 ${fdt_addr} my-imx6ul.dtb
bootz ${loadaddr} - ${fdt_addr}
BOOTEOF

mkimage -C none -A arm -T script -d /tmp/boot.cmd /tmp/boot/boot.scr
sudo cp /tmp/boot/boot.scr /tmp/boot/
sudo umount /tmp/boot

echo "复制rootfs..."
mkdir -p /tmp/rootfs
sudo mount ${DEVICE}2 /tmp/rootfs
sudo tar -xf rootfs/buildroot/output/images/rootfs.tar -C /tmp/rootfs
sudo umount /tmp/rootfs

echo "创建data目录..."
mkdir -p /tmp/data
sudo mount ${DEVICE}3 /tmp/data
sudo mkdir -p /tmp/data/{logs,config,backup}
sudo umount /tmp/data

rm -rf /tmp/boot /tmp/rootfs /tmp/data /tmp/boot.cmd

echo "========================================="
echo "SD卡制作完成!"
echo "可以将SD卡插入板子并启动"
echo "========================================="
EOF

chmod +x tools/make-sdcard.sh
```

### 6.2 制作SD卡

```bash
# 插入SD卡，确认设备名（如/dev/sdb）
lsblk

# 制作SD卡
sudo ./tools/make-sdcard.sh /dev/sdb
```

### 6.3 系统测试

启动系统后，运行测试脚本：

```bash
# 登录系统
# 用户名: root
# 密码: (你在Buildroot中设置的密码)

# 运行测试脚本
test-drivers.sh

# 手动测试网络
ping -c 4 192.168.1.1

# 测试CAN
cansend can0 123#1122334455667788
candump can0

# 测试I2C
i2cdetect -y 0
i2cdetect -y 1

# 测试GPIO
echo 1 > /sys/class/leds/user1/brightness
echo 0 > /sys/class/leds/user1/brightness
```

## 阶段7：文档编写与交付

### 7.1 创建技术文档

```bash
cat > docs/software/quick-start.md << 'EOF'
# MY-IMX6UL BSP 快速开始指南

## 1. 硬件准备

- MY-IMX6UL工业控制板
- 12V/2A电源适配器
- USB转串口线
- 网线
- 8GB以上SD卡

## 2. 烧录系统

### 方法1：使用预编译镜像

```bash
# 下载镜像
wget https://example.com/my-imx6ul-sdcard.img.gz

# 解压
gunzip my-imx6ul-sdcard.img.gz

# 烧录到SD卡
sudo dd if=my-imx6ul-sdcard.img of=/dev/sdX bs=1M status=progress
sync
```

### 方法2：从源码编译

参见 docs/software/build-guide.md

## 3. 启动系统

1. 将SD卡插入板子
2. 连接串口线（115200 8N1）
3. 连接电源
4. 打开串口终端，观察启动日志

## 4. 登录系统

```
my-imx6ul login: root
Password: (你设置的密码)
```

## 5. 基本配置

### 配置网络

```bash
# DHCP
udhcpc -i eth0

# 静态IP
ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up
route add default gw 192.168.1.1
```

### 配置CAN

```bash
ip link set can0 type can bitrate 500000
ip link set can0 up
```

## 6. 测试功能

```bash
# 运行测试脚本
test-drivers.sh
```

## 7. 常见问题

### Q: 系统无法启动
A: 检查SD卡是否正确烧录，检查串口连接

### Q: 网络不通
A: 检查网线连接，检查PHY是否正确识别

### Q: CAN无法通信
A: 检查CAN收发器连接，检查波特率配置

## 8. 技术支持

- 邮箱: support@example.com
- 文档: https://docs.example.com
- 论坛: https://forum.example.com
EOF
```

### 7.2 打包交付

```bash
cd ~/bsp-project

# 创建发布目录
mkdir -p my-imx6ul-bsp-v1.0-release

# 复制源码
cp -r my-imx6ul-bsp/bootloader my-imx6ul-bsp-v1.0-release/
cp -r my-imx6ul-bsp/kernel my-imx6ul-bsp-v1.0-release/
cp -r my-imx6ul-bsp/drivers my-imx6ul-bsp-v1.0-release/
cp -r my-imx6ul-bsp/tools my-imx6ul-bsp-v1.0-release/
cp -r my-imx6ul-bsp/docs my-imx6ul-bsp-v1.0-release/
cp my-imx6ul-bsp/README.md my-imx6ul-bsp-v1.0-release/

# 复制镜像
mkdir -p my-imx6ul-bsp-v1.0-release/images
cp my-imx6ul-bsp/bootloader/u-boot/u-boot.imx my-imx6ul-bsp-v1.0-release/images/
cp my-imx6ul-bsp/kernel/linux-6.1/arch/arm/boot/zImage my-imx6ul-bsp-v1.0-release/images/
cp my-imx6ul-bsp/kernel/linux-6.1/arch/arm/boot/dts/my-imx6ul.dtb my-imx6ul-bsp-v1.0-release/images/
cp my-imx6ul-bsp/rootfs/buildroot/output/images/rootfs.tar my-imx6ul-bsp-v1.0-release/images/

# 打包
tar -czf my-imx6ul-bsp-v1.0-release.tar.gz my-imx6ul-bsp-v1.0-release/

echo "BSP打包完成: my-imx6ul-bsp-v1.0-release.tar.gz"
```

## 项目总结

### 完成的工作

通过本项目，我们完成了：

1. ✅ 完整的U-Boot移植，支持eMMC启动和网络功能
2. ✅ Linux内核适配，包含完整的设备树配置
3. ✅ 所有外设驱动的集成和测试
4. ✅ 定制化根文件系统的构建
5. ✅ 系统集成测试和验证
6. ✅ 完整的技术文档和交付物

### 技能提升

- 掌握了完整的BSP开发流程
- 理解了硬件与软件的协同开发
- 熟悉了设备树的编写和调试
- 积累了实际项目经验

### 后续优化方向

1. **性能优化**
   - 启动时间优化
   - 网络性能调优
   - 内存使用优化

2. **功能扩展**
   - 添加LCD显示支持
   - 实现OTA升级功能
   - 增加安全启动

3. **稳定性提升**
   - 长时间稳定性测试
   - 温度测试
   - 压力测试

## 延伸学习

- [U-Boot开发详解](../../01-bootloader-development/)
- [Linux设备驱动开发](../../02-device-driver-development/)
- [嵌入式Linux系统优化](../../03-operating-system-layer/)

## 参考资料

1. i.MX6UL Reference Manual - NXP
2. U-Boot Documentation - https://u-boot.readthedocs.io/
3. Linux Kernel Documentation - https://www.kernel.org/doc/
4. Device Tree Specification - https://www.devicetree.org/
5. Buildroot User Manual - https://buildroot.org/docs.html

---

**项目完成！** 恭喜你完成了完整的BSP开发项目。现在你已经具备了独立开发新板卡BSP的能力。

**下一步建议**：
1. 在实际硬件上测试和验证
2. 根据实际需求进行功能扩展
3. 持续优化性能和稳定性
4. 积累更多不同平台的BSP开发经验
