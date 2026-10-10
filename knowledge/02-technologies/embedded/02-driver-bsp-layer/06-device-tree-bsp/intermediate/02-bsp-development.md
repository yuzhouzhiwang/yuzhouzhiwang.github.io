---
title: "板级支持包(BSP)开发"
description: "深入学习板级支持包(BSP)的开发流程，包括BSP架构设计、板级初始化、外设配置、驱动适配和系统移植，掌握完整的BSP开发技能"
slug: "bsp-development"

# 分类信息
domain: "驱动与BSP层"
module: "设备树与板级支持"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - BSP开发
  - 板级支持
  - 系统移植
  - 驱动适配
  - 板级初始化
prerequisites:
  - "device-tree-basics"
  - "device-tree-writing"
related_contents: []

# 学习信息
estimated_time: 90
difficulty_score: 7

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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - BSP开发
  - Board Support Package
  - 板级支持包
  - 系统移植
  - 驱动适配
cover_image: ""
---

# 板级支持包(BSP)开发

## 概述

板级支持包(Board Support Package, BSP)是连接硬件和操作系统的关键软件层，为特定硬件平台提供底层支持。本教程将带你深入学习BSP的开发流程，从架构设计到实际实现。完成本教程后，你将能够：

- 理解BSP的架构和组成部分
- 掌握板级初始化的完整流程
- 熟练配置和适配各种外设驱动
- 独立完成新硬件平台的BSP开发
- 解决BSP开发中的常见问题

## 前置知识

在开始本教程之前，你应该：

- 理解设备树的基本概念和编写方法
- 熟悉嵌入式Linux系统的启动流程
- 了解常见外设的工作原理
- 具备C语言和Makefile编程能力
- 熟悉交叉编译工具链的使用

建议先完成 [设备树基础概念](../beginner/01-device-tree-basics.html) 和 [设备树编写与调试](01-device-tree-writing.html) 的学习。

## 实验环境准备

### 所需工具

1. **交叉编译工具链**
```bash
# ARM工具链（以ARM Cortex-A为例）
sudo apt-get install gcc-arm-linux-gnueabihf
sudo apt-get install g++-arm-linux-gnueabihf

# 验证安装
arm-linux-gnueabihf-gcc --version
```

2. **U-Boot源码**
```bash
# 下载U-Boot
git clone https://github.com/u-boot/u-boot.git
cd u-boot
git checkout v2023.10  # 使用稳定版本
```

3. **Linux内核源码**
```bash
# 下载Linux内核
git clone https://github.com/torvalds/linux.git
cd linux
git checkout v6.1  # 使用LTS版本
```

4. **设备树编译器**
```bash
sudo apt-get install device-tree-compiler
```

### 实验目录结构

创建BSP开发的工作目录：

```bash
mkdir -p bsp-tutorial/{bootloader,kernel,rootfs,tools,output}
cd bsp-tutorial
```

目录说明：
- `bootloader/`：U-Boot相关文件
- `kernel/`：Linux内核相关文件
- `rootfs/`：根文件系统
- `tools/`：开发工具和脚本
- `output/`：编译输出文件


## 核心内容

### 1. BSP架构概述

#### 1.1 BSP的组成部分

BSP是一个软件包，包含了硬件平台所需的所有底层支持代码。

**BSP的主要组成**：

```
BSP
├── Bootloader (U-Boot)
│   ├── 板级配置文件
│   ├── 设备树文件
│   ├── 启动脚本
│   └── 驱动代码
├── Linux Kernel
│   ├── 板级配置
│   ├── 设备树文件
│   ├── 驱动程序
│   └── 内核配置
├── Root Filesystem
│   ├── 基础文件系统
│   ├── 应用程序
│   ├── 库文件
│   └── 配置文件
└── Tools & Scripts
    ├── 编译脚本
    ├── 烧录工具
    ├── 调试工具
    └── 测试脚本
```

**BSP的功能层次**：

```
+------------------+
|   应用层         |  用户应用程序
+------------------+
|   系统层         |  Linux内核、文件系统
+------------------+
|   驱动层         |  设备驱动程序
+------------------+
|   BSP层          |  板级初始化、硬件抽象
+------------------+
|   硬件层         |  CPU、外设、接口
+------------------+
```

#### 1.2 BSP开发流程

**完整的BSP开发流程**：

```
1. 硬件分析
   ├─ 阅读硬件原理图
   ├─ 确认芯片型号和外设
   ├─ 分析引脚连接
   └─ 确认电源和时钟

2. 参考平台选择
   ├─ 寻找相似的参考板
   ├─ 分析参考BSP代码
   └─ 确定移植策略

3. Bootloader移植
   ├─ 配置U-Boot
   ├─ 适配板级代码
   ├─ 编写设备树
   └─ 测试启动

4. 内核移植
   ├─ 配置内核
   ├─ 编写设备树
   ├─ 适配驱动
   └─ 测试启动

5. 驱动开发
   ├─ 开发外设驱动
   ├─ 集成到内核
   ├─ 测试验证
   └─ 性能优化

6. 文件系统制作
   ├─ 选择文件系统类型
   ├─ 构建根文件系统
   ├─ 添加应用程序
   └─ 配置启动脚本

7. 系统集成测试
   ├─ 功能测试
   ├─ 稳定性测试
   ├─ 性能测试
   └─ 文档编写
```

#### 1.3 BSP目录结构设计

**推荐的BSP目录结构**：

```
my-board-bsp/
├── README.md                    # BSP说明文档
├── docs/                        # 文档目录
│   ├── hardware-spec.md         # 硬件规格说明
│   ├── build-guide.md           # 编译指南
│   ├── flash-guide.md           # 烧录指南
│   └── troubleshooting.md       # 故障排除
├── bootloader/                  # Bootloader目录
│   ├── u-boot/                  # U-Boot源码
│   ├── configs/                 # 配置文件
│   │   └── my_board_defconfig
│   ├── dts/                     # 设备树文件
│   │   └── my-board.dts
│   └── patches/                 # 补丁文件
├── kernel/                      # 内核目录
│   ├── linux/                   # 内核源码
│   ├── configs/                 # 内核配置
│   │   └── my_board_defconfig
│   ├── dts/                     # 设备树文件
│   │   ├── my-board.dts
│   │   └── my-soc.dtsi
│   ├── drivers/                 # 驱动代码
│   └── patches/                 # 补丁文件
├── rootfs/                      # 根文件系统
│   ├── base/                    # 基础文件系统
│   ├── apps/                    # 应用程序
│   └── configs/                 # 配置文件
├── tools/                       # 工具目录
│   ├── build.sh                 # 编译脚本
│   ├── flash.sh                 # 烧录脚本
│   ├── mkimage.sh               # 镜像制作脚本
│   └── test.sh                  # 测试脚本
├── output/                      # 输出目录
│   ├── images/                  # 镜像文件
│   ├── logs/                    # 编译日志
│   └── temp/                    # 临时文件
└── Makefile                     # 顶层Makefile
```

### 2. 硬件分析与准备

#### 2.1 硬件原理图分析

在开始BSP开发前，必须深入分析硬件原理图。

**分析要点**：

1. **CPU和内存配置**
```
关键信息：
- CPU型号：如i.MX6UL、STM32MP1、RK3568等
- CPU主频：如528MHz、800MHz、1.8GHz
- 内存类型：DDR3、DDR4、LPDDR4
- 内存容量：256MB、512MB、1GB、2GB等
- 内存位宽：16位、32位
- 内存时序参数：CL、tRCD、tRP等
```

2. **存储器配置**
```
关键信息：
- NAND Flash：容量、页大小、块大小
- NOR Flash：容量、扇区大小
- eMMC：容量、版本（4.5、5.0、5.1）
- SD卡：支持的卡类型和速度等级
```

3. **外设接口**
```
需要确认的外设：
- UART：数量、引脚、波特率
- I2C：数量、引脚、速率
- SPI：数量、引脚、模式
- USB：类型（Host/Device/OTG）、数量
- 以太网：PHY芯片型号、接口类型（RMII/RGMII）
- CAN：数量、收发器型号
- GPIO：可用引脚数量
- ADC/DAC：通道数、精度
```

4. **电源管理**
```
关键信息：
- 电源芯片型号：PMIC型号
- 电压域：各电压轨的电压值
- 电源时序：上电顺序和延时
- 电源控制引脚：使能引脚、复位引脚
```

5. **时钟配置**
```
关键信息：
- 晶振频率：主晶振、RTC晶振
- 时钟源：外部时钟、内部时钟
- PLL配置：倍频系数、分频系数
- 时钟树：各外设的时钟来源
```

**原理图分析示例**：

假设我们有一个基于i.MX6UL的板子：

```
硬件配置清单：
┌─────────────────────────────────────┐
│ CPU: i.MX6UL (ARM Cortex-A7, 528MHz)│
│ RAM: 512MB DDR3 (16-bit)            │
│ Flash: 8GB eMMC                     │
│ Ethernet: 10/100M (RMII, LAN8720A) │
│ UART: 2x (Debug + RS485)           │
│ USB: 1x OTG, 1x Host                │
│ I2C: 2x (EEPROM, RTC, Sensors)     │
│ SPI: 1x (Flash)                     │
│ CAN: 2x (TJA1050)                   │
│ GPIO: 20+ available                 │
│ ADC: 4 channels                     │
└─────────────────────────────────────┘
```

#### 2.2 参考平台选择

选择合适的参考平台可以大大加速BSP开发。

**选择参考平台的原则**：

1. **相同或相似的SoC**
   - 最好是完全相同的SoC型号
   - 或者是同系列的SoC（如i.MX6UL和i.MX6ULL）
   - 内核版本相近

2. **相似的外设配置**
   - 使用相同的PHY芯片
   - 使用相同的PMIC
   - 外设类型相似

3. **官方支持的评估板**
   - 厂商提供的EVK（Evaluation Kit）
   - 代码质量有保证
   - 文档完善

**参考平台查找方法**：

```bash
# 在U-Boot源码中查找参考板
cd u-boot
find . -name "*imx6ul*" -type d

# 在Linux内核中查找参考板
cd linux
find arch/arm/boot/dts -name "*imx6ul*.dts"

# 查看参考板的配置
cat arch/arm/boot/dts/imx6ul-14x14-evk.dts
```

#### 2.3 开发工具准备

**必需的开发工具**：

1. **串口调试工具**
```bash
# Linux下使用minicom
sudo apt-get install minicom

# 配置串口
sudo minicom -s
# 设置：115200 8N1, 无流控

# 或使用picocom
sudo apt-get install picocom
sudo picocom -b 115200 /dev/ttyUSB0
```

2. **网络调试工具**
```bash
# TFTP服务器（用于网络启动）
sudo apt-get install tftpd-hpa

# 配置TFTP
sudo vim /etc/default/tftpd-hpa
# TFTP_DIRECTORY="/tftpboot"
# TFTP_OPTIONS="--secure"

# 创建TFTP目录
sudo mkdir -p /tftpboot
sudo chmod 777 /tftpboot

# 重启服务
sudo systemctl restart tftpd-hpa
```

3. **NFS服务器**（用于网络文件系统）
```bash
# 安装NFS服务器
sudo apt-get install nfs-kernel-server

# 配置NFS导出
sudo vim /etc/exports
# /nfsroot *(rw,sync,no_root_squash,no_subtree_check)

# 创建NFS目录
sudo mkdir -p /nfsroot
sudo chmod 777 /nfsroot

# 重启服务
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
```

4. **烧录工具**
```bash
# SD卡烧录（使用dd命令）
sudo dd if=sdcard.img of=/dev/sdX bs=1M status=progress

# eMMC烧录（使用厂商工具）
# 如NXP的mfgtools、Rockchip的rkdeveloptool等
```


### 3. Bootloader移植

#### 3.1 U-Boot配置

**创建板级配置文件**：

```bash
# 进入U-Boot目录
cd u-boot

# 复制参考板配置
cp configs/mx6ul_14x14_evk_defconfig configs/my_board_defconfig

# 编辑配置文件
vim configs/my_board_defconfig
```

**配置文件示例**（my_board_defconfig）：

```makefile
# 架构和CPU配置
CONFIG_ARM=y
CONFIG_ARCH_MX6=y
CONFIG_TARGET_MY_BOARD=y
CONFIG_MX6UL=y

# 内存配置
CONFIG_SYS_MALLOC_LEN=0x1000000
CONFIG_SYS_MEMTEST_START=0x80000000
CONFIG_SYS_MEMTEST_END=0xa0000000

# 启动配置
CONFIG_BOOTDELAY=3
CONFIG_USE_BOOTCOMMAND=y
CONFIG_BOOTCOMMAND="run mmcboot"

# 存储设备支持
CONFIG_MMC=y
CONFIG_FSL_USDHC=y
CONFIG_MMC_IO_VOLTAGE=y
CONFIG_MMC_UHS_SUPPORT=y

# 网络支持
CONFIG_FEC_MXC=y
CONFIG_MII=y
CONFIG_PHYLIB=y
CONFIG_PHY_MICREL=y
CONFIG_PHY_MICREL_KSZ8XXX=y

# 串口配置
CONFIG_MXC_UART=y
CONFIG_CONS_INDEX=1

# 命令支持
CONFIG_CMD_BOOTZ=y
CONFIG_CMD_MMC=y
CONFIG_CMD_I2C=y
CONFIG_CMD_GPIO=y
CONFIG_CMD_DHCP=y
CONFIG_CMD_PING=y
CONFIG_CMD_EXT4=y
CONFIG_CMD_FAT=y

# 设备树支持
CONFIG_OF_CONTROL=y
CONFIG_OF_SEPARATE=y
CONFIG_DEFAULT_DEVICE_TREE="my-board"

# 环境变量存储
CONFIG_ENV_IS_IN_MMC=y
CONFIG_ENV_SIZE=0x2000
CONFIG_ENV_OFFSET=0x100000
```

#### 3.2 板级代码适配

**创建板级目录**：

```bash
# 创建板级目录
mkdir -p board/myvendor/myboard

# 创建必需文件
cd board/myvendor/myboard
touch Makefile myboard.c Kconfig MAINTAINERS
```

**板级Makefile**：

```makefile
# board/myvendor/myboard/Makefile

obj-y := myboard.o

# 如果有PMIC配置
obj-$(CONFIG_POWER) += power.o

# 如果有DDR配置
obj-y += ddr.o
```

**板级初始化代码**（myboard.c）：

```c
// board/myvendor/myboard/myboard.c

#include <common.h>
#include <asm/io.h>
#include <asm/arch/clock.h>
#include <asm/arch/imx-regs.h>
#include <asm/arch/iomux.h>
#include <asm/arch/mx6-pins.h>
#include <asm/arch/crm_regs.h>
#include <asm/arch/sys_proto.h>
#include <asm/gpio.h>
#include <asm/mach-imx/iomux-v3.h>
#include <asm/mach-imx/boot_mode.h>
#include <mmc.h>
#include <fsl_esdhc_imx.h>
#include <netdev.h>

DECLARE_GLOBAL_DATA_PTR;

/* UART引脚配置 */
#define UART_PAD_CTRL  (PAD_CTL_PKE | PAD_CTL_PUE |		\
	PAD_CTL_PUS_100K_UP | PAD_CTL_SPEED_MED |		\
	PAD_CTL_DSE_40ohm   | PAD_CTL_SRE_FAST  | PAD_CTL_HYS)

static iomux_v3_cfg_t const uart1_pads[] = {
	MX6_PAD_UART1_TX_DATA__UART1_DCE_TX | MUX_PAD_CTRL(UART_PAD_CTRL),
	MX6_PAD_UART1_RX_DATA__UART1_DCE_RX | MUX_PAD_CTRL(UART_PAD_CTRL),
};

/* eMMC引脚配置 */
#define USDHC_PAD_CTRL (PAD_CTL_PKE | PAD_CTL_PUE |		\
	PAD_CTL_PUS_22K_UP  | PAD_CTL_SPEED_LOW |		\
	PAD_CTL_DSE_80ohm   | PAD_CTL_SRE_FAST  | PAD_CTL_HYS)

static iomux_v3_cfg_t const usdhc2_pads[] = {
	MX6_PAD_NAND_RE_B__USDHC2_CLK | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_WE_B__USDHC2_CMD | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA00__USDHC2_DATA0 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA01__USDHC2_DATA1 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA02__USDHC2_DATA2 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
	MX6_PAD_NAND_DATA03__USDHC2_DATA3 | MUX_PAD_CTRL(USDHC_PAD_CTRL),
};

/* 以太网引脚配置 */
#define ENET_PAD_CTRL  (PAD_CTL_PUS_100K_UP | PAD_CTL_PUE |     \
	PAD_CTL_SPEED_HIGH   |                                   \
	PAD_CTL_DSE_48ohm   | PAD_CTL_SRE_FAST)

static iomux_v3_cfg_t const fec1_pads[] = {
	MX6_PAD_ENET1_RX_EN__ENET1_RX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_ER__ENET1_RX_ER | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA0__ENET1_RDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA1__ENET1_RDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_EN__ENET1_TX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA0__ENET1_TDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA1__ENET1_TDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_CLK__ENET1_REF_CLK1 | MUX_PAD_CTRL(ENET_PAD_CTRL),
};

/* 板级初始化 */
int board_early_init_f(void)
{
	/* 配置UART引脚 */
	imx_iomux_v3_setup_multiple_pads(uart1_pads, ARRAY_SIZE(uart1_pads));

	return 0;
}

int board_init(void)
{
	/* 设置启动参数地址 */
	gd->bd->bi_boot_params = PHYS_SDRAM + 0x100;

	return 0;
}

/* DDR初始化 */
int dram_init(void)
{
	gd->ram_size = PHYS_SDRAM_SIZE;
	return 0;
}

/* eMMC初始化 */
int board_mmc_init(struct bd_info *bis)
{
	imx_iomux_v3_setup_multiple_pads(usdhc2_pads, ARRAY_SIZE(usdhc2_pads));
	
	usdhc_cfg[1].sdhc_clk = mxc_get_clock(MXC_ESDHC2_CLK);
	return fsl_esdhc_initialize(bis, &usdhc_cfg[1]);
}

/* 以太网初始化 */
int board_eth_init(struct bd_info *bis)
{
	imx_iomux_v3_setup_multiple_pads(fec1_pads, ARRAY_SIZE(fec1_pads));
	
	/* 配置PHY复位引脚 */
	gpio_request(IMX_GPIO_NR(5, 7), "enet_rst");
	gpio_direction_output(IMX_GPIO_NR(5, 7), 0);
	mdelay(10);
	gpio_set_value(IMX_GPIO_NR(5, 7), 1);
	mdelay(50);
	
	return fecmxc_initialize(bis);
}

/* 板级后期初始化 */
int board_late_init(void)
{
	/* 设置环境变量 */
	env_set("board_name", "myboard");
	env_set("board_rev", "v1.0");
	
	return 0;
}
```

#### 3.3 U-Boot设备树编写

**创建U-Boot设备树**（arch/arm/dts/my-board.dts）：

```dts
/dts-v1/;

#include "imx6ul.dtsi"

/ {
	model = "My Board v1.0";
	compatible = "myvendor,myboard", "fsl,imx6ul";

	chosen {
		stdout-path = &uart1;
	};

	memory@80000000 {
		device_type = "memory";
		reg = <0x80000000 0x20000000>;  /* 512MB */
	};
};

/* UART1 - 调试串口 */
&uart1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart1>;
	status = "okay";
};

/* USDHC2 - eMMC */
&usdhc2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_usdhc2>;
	bus-width = <4>;
	non-removable;
	status = "okay";
};

/* FEC1 - 以太网 */
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
			micrel,led-mode = <1>;
		};
	};
};

/* 引脚配置 */
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
			MX6UL_PAD_ENET1_RX_EN__ENET1_RX_EN      0x1b0b0
			MX6UL_PAD_ENET1_RX_ER__ENET1_RX_ER      0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA0__ENET1_RDATA00 0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA1__ENET1_RDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_EN__ENET1_TX_EN      0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA0__ENET1_TDATA00 0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA1__ENET1_TDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_CLK__ENET1_REF_CLK1  0x4001b031
		>;
	};
};
```

#### 3.4 编译和测试U-Boot

**编译U-Boot**：

```bash
# 设置交叉编译工具链
export CROSS_COMPILE=arm-linux-gnueabihf-
export ARCH=arm

# 配置
make my_board_defconfig

# 编译
make -j$(nproc)

# 编译结果
ls -lh u-boot.imx  # 用于烧录的镜像
```

**烧录到SD卡**：

```bash
# 烧录U-Boot到SD卡
sudo dd if=u-boot.imx of=/dev/sdX bs=1k seek=1 conv=fsync

# 注意：seek=1表示跳过第一个1KB（MBR）
```

**测试U-Boot**：

```bash
# 连接串口，启动板子
# 应该看到U-Boot启动信息

U-Boot 2023.10 (Jan 15 2024 - 10:00:00 +0800)

CPU:   Freescale i.MX6UL rev1.1 528 MHz (running at 396 MHz)
Reset cause: POR
Board: My Board v1.0
DRAM:  512 MiB
MMC:   FSL_SDHC: 1
Loading Environment from MMC... OK
In:    serial
Out:   serial
Err:   serial
Net:   FEC0
Hit any key to stop autoboot:  3

# 测试命令
=> printenv
=> mmc list
=> mmc dev 1
=> mmc info
=> ping 192.168.1.1
```


### 4. Linux内核移植

#### 4.1 内核配置

**创建内核配置文件**：

```bash
# 进入内核目录
cd linux

# 复制参考配置
cp arch/arm/configs/imx_v6_v7_defconfig arch/arm/configs/my_board_defconfig

# 配置内核
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- my_board_defconfig

# 图形化配置（可选）
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig
```

**关键配置项**：

```
System Type  --->
    [*] Freescale i.MX family  --->
        [*] i.MX6 UltraLite support

Device Drivers  --->
    [*] Network device support  --->
        [*] Ethernet driver support  --->
            [*] Freescale devices
            [*] FEC ethernet controller
    
    [*] MMC/SD/SDIO card support  --->
        [*] Secure Digital Host Controller Interface support
        [*] SDHCI platform and OF driver helper
        [*] Freescale i.MX SDHCI support
    
    Character devices  --->
        Serial drivers  --->
            [*] IMX serial port support
            [*] Console on IMX serial port
    
    [*] I2C support  --->
        I2C Hardware Bus support  --->
            [*] IMX I2C interface
    
    [*] SPI support  --->
        [*] Freescale i.MX SPI controllers
    
    [*] USB support  --->
        [*] ChipIdea Highspeed Dual Role Controller
        [*] ChipIdea host controller
        [*] ChipIdea device controller
```

#### 4.2 内核设备树编写

**创建内核设备树**（arch/arm/boot/dts/my-board.dts）：

```dts
/dts-v1/;

#include "imx6ul.dtsi"

/ {
	model = "My Board v1.0";
	compatible = "myvendor,myboard", "fsl,imx6ul";

	chosen {
		stdout-path = &uart1;
	};

	memory@80000000 {
		device_type = "memory";
		reg = <0x80000000 0x20000000>;  /* 512MB */
	};

	/* 电源调节器 */
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

		reg_usb_otg_vbus: regulator@1 {
			compatible = "regulator-fixed";
			reg = <1>;
			regulator-name = "usb_otg_vbus";
			regulator-min-microvolt = <5000000>;
			regulator-max-microvolt = <5000000>;
			gpio = <&gpio1 4 GPIO_ACTIVE_HIGH>;
			enable-active-high;
		};
	};

	/* LED设备 */
	leds {
		compatible = "gpio-leds";
		pinctrl-names = "default";
		pinctrl-0 = <&pinctrl_leds>;

		led-status {
			label = "status";
			gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
			default-state = "on";
			linux,default-trigger = "heartbeat";
		};

		led-user {
			label = "user";
			gpios = <&gpio1 5 GPIO_ACTIVE_LOW>;
			default-state = "off";
		};
	};

	/* 按键设备 */
	gpio-keys {
		compatible = "gpio-keys";
		pinctrl-names = "default";
		pinctrl-0 = <&pinctrl_keys>;

		button-user {
			label = "User Button";
			gpios = <&gpio1 18 GPIO_ACTIVE_LOW>;
			linux,code = <KEY_ENTER>;
			debounce-interval = <50>;
		};
	};
};

/* CPU配置 */
&cpu0 {
	arm-supply = <&reg_arm>;
	soc-supply = <&reg_soc>;
	operating-points = <
		/* kHz    uV */
		528000  1175000
		396000  1025000
		198000   950000
	>;
};

/* UART1 - 调试串口 */
&uart1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart1>;
	status = "okay";
};

/* UART2 - RS485 */
&uart2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_uart2>;
	uart-has-rtscts;
	linux,rs485-enabled-at-boot-time;
	status = "okay";
};

/* USDHC2 - eMMC */
&usdhc2 {
	pinctrl-names = "default", "state_100mhz", "state_200mhz";
	pinctrl-0 = <&pinctrl_usdhc2>;
	pinctrl-1 = <&pinctrl_usdhc2_100mhz>;
	pinctrl-2 = <&pinctrl_usdhc2_200mhz>;
	bus-width = <4>;
	non-removable;
	no-1-8-v;
	keep-power-in-suspend;
	status = "okay";
};

/* FEC1 - 以太网 */
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
			micrel,led-mode = <1>;
			clocks = <&clks IMX6UL_CLK_ENET_REF>;
			clock-names = "rmii-ref";
		};
	};
};

/* I2C1 */
&i2c1 {
	clock-frequency = <400000>;
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_i2c1>;
	status = "okay";

	/* EEPROM */
	eeprom@50 {
		compatible = "atmel,24c256";
		reg = <0x50>;
		pagesize = <64>;
	};

	/* RTC */
	rtc@68 {
		compatible = "dallas,ds1307";
		reg = <0x68>;
	};
};

/* I2C2 */
&i2c2 {
	clock-frequency = <100000>;
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_i2c2>;
	status = "okay";

	/* 温度传感器 */
	temp-sensor@48 {
		compatible = "ti,tmp102";
		reg = <0x48>;
		#thermal-sensor-cells = <0>;
	};
};

/* SPI1 */
&ecspi1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_ecspi1>;
	cs-gpios = <&gpio4 26 GPIO_ACTIVE_LOW>;
	status = "okay";

	/* SPI Flash */
	flash@0 {
		compatible = "jedec,spi-nor";
		reg = <0>;
		spi-max-frequency = <20000000>;

		partitions {
			compatible = "fixed-partitions";
			#address-cells = <1>;
			#size-cells = <1>;

			partition@0 {
				label = "bootloader";
				reg = <0x000000 0x100000>;
				read-only;
			};

			partition@100000 {
				label = "env";
				reg = <0x100000 0x010000>;
			};

			partition@110000 {
				label = "data";
				reg = <0x110000 0x6f0000>;
			};
		};
	};
};

/* CAN1 */
&can1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_flexcan1>;
	status = "okay";
};

/* CAN2 */
&can2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_flexcan2>;
	status = "okay";
};

/* USB OTG */
&usbotg1 {
	vbus-supply = <&reg_usb_otg_vbus>;
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_usb_otg1>;
	dr_mode = "otg";
	srp-disable;
	hnp-disable;
	adp-disable;
	status = "okay";
};

/* USB Host */
&usbotg2 {
	dr_mode = "host";
	disable-over-current;
	status = "okay";
};

/* ADC */
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
			MX6UL_PAD_ENET1_RX_EN__ENET1_RX_EN      0x1b0b0
			MX6UL_PAD_ENET1_RX_ER__ENET1_RX_ER      0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA0__ENET1_RDATA00 0x1b0b0
			MX6UL_PAD_ENET1_RX_DATA1__ENET1_RDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_EN__ENET1_TX_EN      0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA0__ENET1_TDATA00 0x1b0b0
			MX6UL_PAD_ENET1_TX_DATA1__ENET1_TDATA01 0x1b0b0
			MX6UL_PAD_ENET1_TX_CLK__ENET1_REF_CLK1  0x4001b031
			MX6UL_PAD_SNVS_TAMPER7__GPIO5_IO07      0x79  /* PHY RST */
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
			MX6UL_PAD_CSI_DATA05__GPIO4_IO26  0x10b0  /* CS */
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

	pinctrl_usb_otg1: usbotg1grp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO04__GPIO1_IO04  0x10b0  /* VBUS */
		>;
	};

	pinctrl_adc1: adc1grp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO00__GPIO1_IO00  0xb0
			MX6UL_PAD_GPIO1_IO01__GPIO1_IO01  0xb0
			MX6UL_PAD_GPIO1_IO08__GPIO1_IO08  0xb0
			MX6UL_PAD_GPIO1_IO09__GPIO1_IO09  0xb0
		>;
	};

	pinctrl_leds: ledsgrp {
		fsl,pins = <
			MX6UL_PAD_GPIO1_IO03__GPIO1_IO03  0x17059
			MX6UL_PAD_GPIO1_IO05__GPIO1_IO05  0x17059
		>;
	};

	pinctrl_keys: keysgrp {
		fsl,pins = <
			MX6UL_PAD_UART1_CTS_B__GPIO1_IO18 0x80000000
		>;
	};
};
```

#### 4.3 编译内核

**编译内核和设备树**：

```bash
# 设置环境变量
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-

# 编译内核
make -j$(nproc) zImage

# 编译设备树
make dtbs

# 编译模块
make modules

# 编译结果
ls -lh arch/arm/boot/zImage
ls -lh arch/arm/boot/dts/my-board.dtb
```

**安装模块到根文件系统**：

```bash
# 安装模块
make INSTALL_MOD_PATH=/path/to/rootfs modules_install
```


### 5. 驱动适配

#### 5.1 驱动检查清单

在BSP开发中，需要确保所有外设驱动正常工作。

**驱动检查清单**：

```
□ 串口驱动
  □ 调试串口可用
  □ 通信串口可用
  □ 波特率配置正确
  □ 流控功能正常

□ 存储驱动
  □ eMMC/SD卡识别
  □ 读写功能正常
  □ 分区表正确
  □ 文件系统挂载

□ 网络驱动
  □ 以太网PHY识别
  □ 网络连接正常
  □ DHCP功能
  □ 网络性能测试

□ USB驱动
  □ USB Host功能
  □ USB Device功能
  □ USB OTG切换
  □ USB存储设备

□ I2C驱动
  □ I2C总线扫描
  □ EEPROM读写
  □ RTC功能
  □ 传感器数据读取

□ SPI驱动
  □ SPI Flash识别
  □ Flash读写
  □ Flash分区

□ CAN驱动
  □ CAN总线初始化
  □ CAN报文收发
  □ CAN错误处理

□ GPIO驱动
  □ GPIO输入输出
  □ GPIO中断
  □ LED控制
  □ 按键检测

□ ADC驱动
  □ ADC通道配置
  □ ADC采样
  □ 数据精度验证
```

#### 5.2 驱动调试方法

**查看驱动加载情况**：

```bash
# 查看已加载的驱动模块
lsmod

# 查看设备树节点
ls /proc/device-tree/

# 查看平台设备
ls /sys/bus/platform/devices/

# 查看驱动绑定情况
ls /sys/bus/platform/drivers/

# 查看设备信息
cat /proc/devices
cat /proc/interrupts
cat /proc/iomem
```

**测试串口**：

```bash
# 查看串口设备
ls /dev/tty*

# 测试串口回环
echo "test" > /dev/ttyS1
cat /dev/ttyS1

# 使用minicom测试
minicom -D /dev/ttyS1 -b 115200
```

**测试网络**：

```bash
# 查看网络接口
ifconfig -a

# 配置IP地址
ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up

# 测试连接
ping 192.168.1.1

# 查看网络统计
ifconfig eth0
ethtool eth0
```

**测试I2C**：

```bash
# 安装i2c-tools
apt-get install i2c-tools

# 扫描I2C总线
i2cdetect -y 0
i2cdetect -y 1

# 读取EEPROM
i2cdump -y 0 0x50

# 读取RTC
hwclock -r
```

**测试SPI Flash**：

```bash
# 查看MTD设备
cat /proc/mtd

# 读取Flash信息
mtdinfo /dev/mtd0

# 擦除Flash
flash_erase /dev/mtd2 0 0

# 写入数据
dd if=/dev/zero of=/dev/mtd2 bs=1k count=100

# 读取数据
dd if=/dev/mtd2 of=/tmp/test.bin bs=1k count=100
```

**测试CAN**：

```bash
# 安装can-utils
apt-get install can-utils

# 配置CAN接口
ip link set can0 type can bitrate 500000
ip link set can0 up

# 发送CAN报文
cansend can0 123#1122334455667788

# 接收CAN报文
candump can0

# 查看CAN统计
ip -details -statistics link show can0
```

**测试GPIO**：

```bash
# 导出GPIO
echo 3 > /sys/class/gpio/export

# 设置方向
echo out > /sys/class/gpio/gpio3/direction

# 设置值
echo 1 > /sys/class/gpio/gpio3/value
echo 0 > /sys/class/gpio/gpio3/value

# 读取值
cat /sys/class/gpio/gpio3/value

# 取消导出
echo 3 > /sys/class/gpio/unexport
```

**测试ADC**：

```bash
# 查看ADC设备
ls /sys/bus/iio/devices/

# 读取ADC值
cat /sys/bus/iio/devices/iio:device0/in_voltage0_raw

# 读取ADC电压（如果支持）
cat /sys/bus/iio/devices/iio:device0/in_voltage0_scale
```

### 6. 根文件系统制作

#### 6.1 选择文件系统类型

**常见文件系统类型**：

| 文件系统 | 特点 | 适用场景 |
|---------|------|---------|
| ext4 | 功能完整，支持日志 | eMMC、SD卡、硬盘 |
| ubifs | 专为Flash设计，支持压缩 | NAND Flash |
| jffs2 | 老牌Flash文件系统 | NOR Flash |
| squashfs | 只读压缩文件系统 | 只读根文件系统 |
| tmpfs | 内存文件系统 | 临时文件、/tmp目录 |
| ramfs | 简单内存文件系统 | initramfs |

#### 6.2 使用Buildroot构建根文件系统

**安装Buildroot**：

```bash
# 下载Buildroot
git clone https://github.com/buildroot/buildroot.git
cd buildroot
git checkout 2023.11  # 使用稳定版本
```

**配置Buildroot**：

```bash
# 使用默认配置
make list-defconfigs | grep arm
make imx6ulevk_defconfig

# 自定义配置
make menuconfig
```

**关键配置项**：

```
Target options  --->
    Target Architecture (ARM (little endian))
    Target Architecture Variant (cortex-A7)
    Target ABI (EABIhf)
    Floating point strategy (VFPv4)

Toolchain  --->
    Toolchain type (External toolchain)
    Toolchain (Linaro ARM)

System configuration  --->
    System hostname (myboard)
    System banner (Welcome to My Board)
    Init system (BusyBox)
    /dev management (Dynamic using devtmpfs + eudev)
    [*] Enable root login with password
    Root password (your_password)

Kernel  --->
    [*] Linux Kernel
    Kernel version (Custom tarball)
    URL of custom kernel tarball (file:///path/to/linux-6.1.tar.gz)
    Kernel configuration (Using a custom config file)
    Configuration file path (board/myvendor/myboard/linux.config)
    [*] Build a Device Tree Blob (DTB)
    Device Tree Source file names (my-board)

Target packages  --->
    Networking applications  --->
        [*] dropbear (SSH server)
        [*] ethtool
        [*] iperf3
        [*] iproute2
        [*] openssh
    
    Hardware handling  --->
        [*] i2c-tools
        [*] can-utils
        [*] mtd-utils
    
    System tools  --->
        [*] htop
        [*] procps-ng

Filesystem images  --->
    [*] ext2/3/4 root filesystem
        ext2/3/4 variant (ext4)
    [*] tar the root filesystem
```

**编译根文件系统**：

```bash
# 编译
make -j$(nproc)

# 编译结果
ls -lh output/images/
# rootfs.ext4  - ext4格式的根文件系统
# rootfs.tar   - tar格式的根文件系统
# zImage       - 内核镜像
# my-board.dtb - 设备树
```

#### 6.3 自定义根文件系统

**创建overlay目录**：

```bash
# 创建overlay目录
mkdir -p board/myvendor/myboard/rootfs-overlay

# 添加自定义文件
mkdir -p board/myvendor/myboard/rootfs-overlay/etc/init.d
mkdir -p board/myvendor/myboard/rootfs-overlay/usr/bin
```

**添加启动脚本**（board/myvendor/myboard/rootfs-overlay/etc/init.d/S99custom）：

```bash
#!/bin/sh

case "$1" in
  start)
        echo "Starting custom services..."
        
        # 配置网络
        ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up
        route add default gw 192.168.1.1
        
        # 启动CAN
        ip link set can0 type can bitrate 500000
        ip link set can0 up
        
        # 挂载数据分区
        mount /dev/mmcblk1p3 /data
        
        echo "Custom services started"
        ;;
  stop)
        echo "Stopping custom services..."
        ;;
  *)
        echo "Usage: $0 {start|stop}"
        exit 1
esac

exit 0
```

**添加自定义应用**：

```bash
# 复制应用程序
cp /path/to/myapp board/myvendor/myboard/rootfs-overlay/usr/bin/

# 设置权限
chmod +x board/myvendor/myboard/rootfs-overlay/usr/bin/myapp
```

**配置Buildroot使用overlay**：

```bash
make menuconfig

# System configuration  --->
#     Root filesystem overlay directories
#     (board/myvendor/myboard/rootfs-overlay)
```

### 7. 系统集成与测试

#### 7.1 创建SD卡镜像

**SD卡分区方案**：

```
SD卡布局：
┌──────────────────────────────────────┐
│ MBR (512B)                           │
├──────────────────────────────────────┤
│ U-Boot (1MB, offset 1KB)             │
├──────────────────────────────────────┤
│ Partition 1: boot (FAT32, 32MB)     │
│   - zImage                           │
│   - my-board.dtb                     │
│   - boot.scr                         │
├──────────────────────────────────────┤
│ Partition 2: rootfs (ext4, 512MB)   │
│   - 根文件系统                        │
├──────────────────────────────────────┤
│ Partition 3: data (ext4, 剩余空间)   │
│   - 用户数据                          │
└──────────────────────────────────────┘
```

**创建分区脚本**（tools/make-sdcard.sh）：

```bash
#!/bin/bash

# SD卡设备
DEVICE=$1

if [ -z "$DEVICE" ]; then
    echo "Usage: $0 <device>"
    echo "Example: $0 /dev/sdb"
    exit 1
fi

echo "WARNING: This will erase all data on $DEVICE"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 卸载所有分区
umount ${DEVICE}* 2>/dev/null

# 创建分区表
sudo parted -s $DEVICE mklabel msdos
sudo parted -s $DEVICE mkpart primary fat32 1MiB 33MiB
sudo parted -s $DEVICE mkpart primary ext4 33MiB 545MiB
sudo parted -s $DEVICE mkpart primary ext4 545MiB 100%
sudo parted -s $DEVICE set 1 boot on

# 格式化分区
sudo mkfs.vfat -F 32 -n BOOT ${DEVICE}1
sudo mkfs.ext4 -L rootfs ${DEVICE}2
sudo mkfs.ext4 -L data ${DEVICE}3

# 烧录U-Boot
sudo dd if=output/images/u-boot.imx of=$DEVICE bs=1k seek=1 conv=fsync

# 挂载boot分区
mkdir -p /tmp/boot
sudo mount ${DEVICE}1 /tmp/boot

# 复制内核和设备树
sudo cp output/images/zImage /tmp/boot/
sudo cp output/images/my-board.dtb /tmp/boot/

# 创建boot脚本
cat > /tmp/boot.cmd << EOF
setenv bootargs console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw
load mmc 1:1 \${loadaddr} zImage
load mmc 1:1 \${fdt_addr} my-board.dtb
bootz \${loadaddr} - \${fdt_addr}
EOF

# 编译boot脚本
mkimage -C none -A arm -T script -d /tmp/boot.cmd /tmp/boot/boot.scr
sudo cp /tmp/boot/boot.scr /tmp/boot/

# 卸载boot分区
sudo umount /tmp/boot

# 挂载rootfs分区
mkdir -p /tmp/rootfs
sudo mount ${DEVICE}2 /tmp/rootfs

# 解压根文件系统
sudo tar -xf output/images/rootfs.tar -C /tmp/rootfs

# 卸载rootfs分区
sudo umount /tmp/rootfs

# 清理
rm -rf /tmp/boot /tmp/rootfs /tmp/boot.cmd

echo "SD card created successfully!"
echo "You can now insert it into the board and boot."
```

**使用脚本**：

```bash
chmod +x tools/make-sdcard.sh
sudo ./tools/make-sdcard.sh /dev/sdb
```

#### 7.2 系统启动测试

**连接串口，启动系统**：

```
U-Boot 2023.10 (Jan 15 2024 - 10:00:00 +0800)

CPU:   Freescale i.MX6UL rev1.1 528 MHz
Board: My Board v1.0
DRAM:  512 MiB
MMC:   FSL_SDHC: 1
Loading Environment from MMC... OK
Net:   FEC0
Hit any key to stop autoboot:  0

Loading kernel from mmc...
Loading device tree...
Starting kernel ...

[    0.000000] Booting Linux on physical CPU 0x0
[    0.000000] Linux version 6.1.0 (user@host) (gcc version 11.2.0)
[    0.000000] CPU: ARMv7 Processor [410fc075] revision 5 (ARMv7)
[    0.000000] Machine model: My Board v1.0
[    0.000000] Memory policy: Data cache writeback
[    0.000000] Reserved memory: created DMA memory pool at 0x90000000
[    0.000000] OF: reserved mem: initialized node linux,cma
...
[    2.345678] EXT4-fs (mmcblk1p2): mounted filesystem with ordered data mode
[    2.456789] VFS: Mounted root (ext4 filesystem) on device 179:2.
[    2.567890] devtmpfs: mounted
[    2.678901] Freeing unused kernel memory: 1024K
[    2.789012] Run /sbin/init as init process

Welcome to My Board
myboard login: root
Password:

# uname -a
Linux myboard 6.1.0 #1 SMP Mon Jan 15 10:00:00 CST 2024 armv7l GNU/Linux

# cat /proc/cpuinfo
processor       : 0
model name      : ARMv7 Processor rev 5 (v7l)
BogoMIPS        : 49.93
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x0
CPU part        : 0xc07
CPU revision    : 5

# free -h
              total        used        free      shared  buff/cache   available
Mem:          489Mi        45Mi       398Mi       0.0Ki        45Mi       434Mi
Swap:            0B          0B          0B

# df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       489M  156M  308M  34% /
devtmpfs        239M     0  239M   0% /dev
tmpfs           245M     0  245M   0% /dev/shm
tmpfs           245M  4.5M  240M   2% /run
tmpfs           245M     0  245M   0% /tmp
/dev/mmcblk1p1   31M  5.2M   26M  17% /boot
/dev/mmcblk1p3  6.9G   24M  6.5G   1% /data
```

#### 7.3 功能测试

**测试网络**：

```bash
# 配置网络
ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up
route add default gw 192.168.1.1

# 测试连接
ping -c 4 192.168.1.1
ping -c 4 www.baidu.com

# 测试性能
iperf3 -c 192.168.1.10
```

**测试存储**：

```bash
# 测试eMMC读写速度
dd if=/dev/zero of=/tmp/test.bin bs=1M count=100
dd if=/tmp/test.bin of=/dev/null bs=1M

# 测试文件系统
bonnie++ -u root -d /data
```

**测试外设**：

```bash
# 测试I2C
i2cdetect -y 0
i2cdetect -y 1

# 测试SPI Flash
cat /proc/mtd
mtdinfo /dev/mtd0

# 测试CAN
ip link set can0 type can bitrate 500000
ip link set can0 up
candump can0 &
cansend can0 123#1122334455667788

# 测试GPIO LED
echo 1 > /sys/class/leds/status/brightness
echo 0 > /sys/class/leds/status/brightness

# 测试ADC
cat /sys/bus/iio/devices/iio:device0/in_voltage0_raw
```


## 深入理解

### BSP开发的关键要点

1. **硬件理解是基础**
   - 深入阅读硬件原理图和数据手册
   - 理解每个外设的工作原理和配置方法
   - 掌握引脚复用和电气特性

2. **参考代码的重要性**
   - 选择合适的参考平台可以节省大量时间
   - 理解参考代码的实现逻辑，而不是盲目复制
   - 根据实际硬件差异进行适配

3. **设备树的核心作用**
   - 设备树是硬件描述的标准方法
   - 正确的设备树配置是驱动工作的前提
   - 设备树的调试技巧至关重要

4. **分层开发策略**
   - 先让Bootloader启动
   - 再让内核启动到shell
   - 最后逐个调试外设驱动
   - 每一步都要充分测试

5. **调试工具的使用**
   - 串口是最基本的调试工具
   - 网络调试可以大大提高效率
   - 熟练使用各种测试工具

### BSP开发常见问题

**问题1：U-Boot无法启动**

可能原因：
- DDR配置错误
- 时钟配置错误
- 引脚配置错误
- 镜像烧录位置错误

排查方法：
```bash
# 检查DDR配置
# 参考芯片数据手册和DDR芯片规格书
# 确认时序参数正确

# 检查时钟配置
# 确认晶振频率
# 检查PLL配置

# 检查烧录位置
# 确认offset正确
# 使用正确的烧录命令
```

**问题2：内核启动卡住**

可能原因：
- 设备树错误
- 内核配置错误
- 根文件系统问题
- 启动参数错误

排查方法：
```bash
# 检查内核日志
# 看最后一条日志在哪里

# 检查设备树
dtc -I dtb -O dts -o check.dts my-board.dtb
# 查看设备树是否正确

# 检查启动参数
# console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw
# 确认串口、根设备路径正确

# 简化测试
# 使用initramfs启动
# 排除根文件系统问题
```

**问题3：网络不通**

可能原因：
- PHY未识别
- PHY复位时序错误
- 引脚配置错误
- 时钟配置错误

排查方法：
```bash
# 检查PHY是否识别
dmesg | grep -i phy
dmesg | grep -i eth

# 检查网络接口
ifconfig -a

# 检查PHY寄存器
ethtool eth0
mii-tool eth0

# 检查设备树配置
# 确认phy-mode正确（rmii/rgmii）
# 确认phy-handle引用正确
# 确认复位引脚和时序正确
```

**问题4：I2C设备无法访问**

可能原因：
- I2C地址错误
- 上拉电阻问题
- 引脚配置错误
- 时钟配置错误

排查方法：
```bash
# 扫描I2C总线
i2cdetect -y 0

# 检查I2C时钟
# 确认SCL频率正确

# 检查硬件
# 使用示波器查看SCL和SDA波形
# 确认上拉电阻存在（通常4.7K）

# 检查设备树
# 确认I2C地址正确
# 确认引脚配置正确
```

### BSP性能优化

**启动时间优化**：

1. **U-Boot优化**
```bash
# 减少启动延时
setenv bootdelay 0

# 禁用不需要的功能
# 在defconfig中禁用USB、网络等不需要的功能

# 使用Falcon模式
# 直接从SPL跳转到内核，跳过U-Boot
```

2. **内核优化**
```bash
# 禁用不需要的驱动
# 在内核配置中禁用不使用的驱动

# 使用静态编译
# 将常用驱动编译进内核，减少模块加载时间

# 优化启动参数
# quiet loglevel=3  # 减少日志输出
# lpj=xxx           # 预设loops_per_jiffy
```

3. **文件系统优化**
```bash
# 使用只读根文件系统
# 减少文件系统检查时间

# 使用压缩文件系统
# squashfs可以减小镜像大小

# 延迟挂载
# 将非关键分区延迟挂载
```

**运行时性能优化**：

1. **CPU频率调整**
```bash
# 查看当前频率
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# 设置性能模式
echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# 设置节能模式
echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

2. **内存优化**
```bash
# 调整内存回收策略
echo 10 > /proc/sys/vm/swappiness

# 调整缓存策略
echo 3 > /proc/sys/vm/drop_caches
```

3. **网络优化**
```bash
# 调整网络缓冲区
echo 262144 > /proc/sys/net/core/rmem_max
echo 262144 > /proc/sys/net/core/wmem_max

# 启用TCP优化
echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
```

## 实践示例

### 完整的BSP开发流程示例

假设我们要为一个基于i.MX6UL的自定义板子开发BSP，以下是完整的开发流程：

**第1步：硬件分析**（1-2天）
- 阅读原理图，记录所有外设配置
- 确认与参考板的差异
- 制定移植计划

**第2步：U-Boot移植**（3-5天）
- 复制参考板配置
- 修改板级代码
- 编写设备树
- 测试启动和基本功能

**第3步：内核移植**（3-5天）
- 配置内核
- 编写设备树
- 编译测试
- 验证基本启动

**第4步：驱动调试**（5-10天）
- 逐个调试外设驱动
- 串口 → 网络 → 存储 → I2C → SPI → CAN → USB
- 每个驱动都要充分测试

**第5步：文件系统制作**（2-3天）
- 使用Buildroot构建
- 添加必要的应用和工具
- 制作SD卡镜像

**第6步：系统集成测试**（3-5天）
- 功能测试
- 稳定性测试
- 性能测试
- 文档编写

**总计：17-30天**

## 常见问题

### Q1: 如何选择合适的参考平台？

**A**: 选择参考平台的优先级：

1. 完全相同的SoC型号
2. 同系列的SoC（如i.MX6UL和i.MX6ULL）
3. 相同厂商的其他SoC
4. 官方评估板优先于第三方板子

关键是要找到外设配置相似的板子，特别是PHY芯片、PMIC等关键器件。

### Q2: 设备树和板级代码如何分工？

**A**: 分工原则：

**设备树负责**：
- 硬件资源描述（地址、中断、时钟）
- 引脚配置
- 设备属性配置
- 设备间的连接关系

**板级代码负责**：
- 早期硬件初始化（DDR、时钟）
- 复杂的初始化逻辑
- 运行时的硬件控制
- 与Bootloader相关的特殊处理

现代BSP开发趋势是尽量使用设备树，减少板级代码。

### Q3: 如何调试设备树问题？

**A**: 调试方法：

1. **编译时检查**
```bash
# 使用dtc检查语法
dtc -I dts -O dtb -o test.dtb my-board.dts

# 反编译查看
dtc -I dtb -O dts -o check.dts test.dtb
```

2. **运行时检查**
```bash
# 查看设备树内容
ls /proc/device-tree/
cat /proc/device-tree/model

# 查看设备匹配情况
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/
```

3. **内核日志**
```bash
# 查看设备树相关日志
dmesg | grep -i "device tree"
dmesg | grep -i "of:"

# 查看设备probe日志
dmesg | grep -i "probe"
```

### Q4: BSP开发需要哪些技能？

**A**: 必备技能：

1. **硬件知识**
   - 能够阅读原理图
   - 理解常见外设的工作原理
   - 了解电气特性和时序

2. **软件技能**
   - C语言编程
   - Makefile和Kconfig
   - Shell脚本
   - Git版本控制

3. **Linux知识**
   - Linux启动流程
   - 设备驱动模型
   - 设备树语法
   - 内核配置和编译

4. **调试能力**
   - 串口调试
   - 网络调试
   - 使用示波器和逻辑分析仪
   - 阅读内核日志

## 总结

BSP开发是嵌入式Linux系统开发的基础，涉及Bootloader、内核、驱动、文件系统等多个方面。本教程介绍的核心要点包括：

- **BSP架构**：理解BSP的组成和开发流程
- **硬件分析**：深入分析硬件原理图和选择参考平台
- **Bootloader移植**：U-Boot的配置、板级代码和设备树
- **内核移植**：内核配置、设备树编写和编译
- **驱动适配**：各种外设驱动的调试方法
- **文件系统**：使用Buildroot构建根文件系统
- **系统集成**：制作完整的系统镜像和测试

掌握这些技能后，你将能够独立完成新硬件平台的BSP开发工作。

## 延伸阅读

推荐进一步学习的资源：

- [完整BSP开发实战项目](../../06-device-tree-bsp/advanced/01-complete-bsp-project.html) - 完整的BSP项目实战
- [U-Boot开发详解](../../01-bootloader-development/) - 深入学习Bootloader开发
- [Linux设备驱动开发](../../02-device-driver-development/) - 驱动开发详解
- [嵌入式Linux系统构建](../../03-operating-system-layer/) - 系统构建和优化

## 参考资料

1. U-Boot Documentation - https://u-boot.readthedocs.io/
2. Linux Kernel Documentation - https://www.kernel.org/doc/
3. Device Tree Specification - https://www.devicetree.org/
4. Buildroot User Manual - https://buildroot.org/docs.html
5. Embedded Linux Primer - Christopher Hallinan
6. Mastering Embedded Linux Programming - Chris Simmonds

---

**练习题**：

1. 为一个虚拟的硬件平台创建完整的BSP目录结构
2. 编写一个简单的板级初始化代码
3. 创建一个包含常用外设的设备树文件
4. 使用Buildroot构建一个最小的根文件系统
5. 编写一个自动化的SD卡镜像制作脚本

**下一步**：建议学习 [完整BSP开发实战项目](../../06-device-tree-bsp/advanced/01-complete-bsp-project.html)，通过完整的项目实践巩固BSP开发技能。

**实践建议**：
1. 从简单的板子开始，逐步增加复杂度
2. 充分利用参考代码，但要理解原理
3. 建立自己的BSP开发模板和工具集
4. 记录开发过程中遇到的问题和解决方案
5. 多实践，多总结，形成自己的开发流程

