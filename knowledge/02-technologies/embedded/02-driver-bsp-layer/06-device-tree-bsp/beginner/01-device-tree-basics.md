---
title: "设备树基础概念"
description: "深入讲解设备树（Device Tree）的基本概念、DTS语法、DTB编译过程和设备树结构，帮助开发者理解设备树在嵌入式Linux系统中的作用和应用场景"
slug: "device-tree-basics"

# 分类信息
domain: "驱动与BSP层"
module: "设备树与板级支持"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 设备树
  - DTS
  - DTB
  - 嵌入式Linux
  - 板级支持
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 40
difficulty_score: 3

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
  - 设备树
  - Device Tree
  - DTS语法
  - DTB编译
  - 嵌入式Linux
cover_image: ""
---

# 设备树基础概念

## 概述

设备树（Device Tree）是一种描述硬件资源的数据结构，用于将硬件配置信息与Linux内核代码分离。在嵌入式Linux系统中，设备树已成为描述硬件平台的标准方法。完成本文学习后，你将能够：

- 理解设备树的概念和作用
- 掌握DTS（Device Tree Source）的基本语法
- 了解DTB（Device Tree Blob）的编译过程
- 理解设备树的层次结构和组织方式
- 掌握设备树在嵌入式Linux中的应用场景

## 背景知识

### 为什么需要设备树？

在设备树出现之前，Linux内核使用板级文件（Board File）来描述硬件信息。这种方式存在以下问题：

**传统板级文件的问题**：
- **代码耦合**：硬件信息硬编码在内核代码中
- **维护困难**：每个板子需要单独的C代码文件
- **内核膨胀**：大量板级文件导致内核体积增大
- **移植复杂**：更换硬件需要修改和重新编译内核
- **灵活性差**：无法在运行时动态配置硬件

**设备树的优势**：
```
传统方式：硬件信息 → 板级C代码 → 编译进内核
设备树方式：硬件信息 → DTS文件 → 编译成DTB → 启动时加载
```

- **硬件软件分离**：硬件描述独立于内核代码
- **易于维护**：修改硬件配置只需修改DTS文件
- **内核通用**：同一内核可支持多个硬件平台
- **灵活配置**：无需重新编译内核即可更换硬件
- **标准化**：统一的硬件描述格式

### 设备树的基本概念

**设备树的三种形式**：

1. **DTS（Device Tree Source）**
   - 人类可读的源文件格式
   - 使用类似C语言的语法
   - 文件扩展名：.dts 和 .dtsi

2. **DTB（Device Tree Blob）**
   - 二进制格式的设备树
   - 由DTS编译生成
   - 在系统启动时被加载

3. **内核中的设备树**
   - DTB被解析后的内存数据结构
   - 驱动程序通过API访问

**设备树的工作流程**：
```
编写DTS → 编译成DTB → Bootloader加载 → 内核解析 → 驱动使用
  ↓          ↓            ↓             ↓          ↓
.dts文件   .dtb文件    内存中        设备节点    硬件访问
```

## 核心内容

### 1. DTS基本语法

#### 1.1 设备树的基本结构

设备树采用树形结构，由节点（Node）和属性（Property）组成。


**基本结构示例**：
```dts
/dts-v1/;  // 版本声明

/ {  // 根节点
    model = "My Board";
    compatible = "vendor,board-name";
    
    cpus {  // CPU节点
        cpu@0 {
            device_type = "cpu";
            compatible = "arm,cortex-a7";
            reg = <0>;
        };
    };
    
    memory@80000000 {  // 内存节点
        device_type = "memory";
        reg = <0x80000000 0x20000000>;  // 起始地址 大小
    };
};
```

**语法要点**：
- `/dts-v1/;`：设备树版本声明（必须）
- `/`：根节点，所有其他节点都是它的子节点
- `{}`：节点内容，包含属性和子节点
- `node-name@address`：节点命名格式
- `property = value;`：属性定义

#### 1.2 节点（Node）

节点是设备树的基本单元，代表一个硬件设备或总线。

**节点命名规则**：
```dts
// 格式：node-name@unit-address
uart0: serial@12340000 {  // uart0是标签，serial是节点名，12340000是地址
    // 节点内容
};

// 不带地址的节点
cpus {
    // 节点内容
};

// 带标签的节点（可以被引用）
gpio1: gpio@209c000 {
    // 节点内容
};
```

**节点命名规范**：
- 节点名使用小写字母、数字和连字符
- 如果节点有地址，使用`@`分隔名称和地址
- 标签（Label）用于引用节点，使用冒号`:`定义
- 地址通常是寄存器基地址或总线地址

**节点层次结构**：
```dts
/ {
    soc {  // SoC节点
        aips1: aips-bus@02000000 {  // 总线节点
            uart1: serial@02020000 {  // UART设备节点
                compatible = "fsl,imx6ul-uart";
                reg = <0x02020000 0x4000>;
                // 更多属性...
            };
            
            i2c1: i2c@021a0000 {  // I2C设备节点
                compatible = "fsl,imx6ul-i2c";
                reg = <0x021a0000 0x4000>;
                // 更多属性...
            };
        };
    };
};
```

#### 1.3 属性（Property）

属性是节点的键值对，描述设备的特性。

**属性类型**：

1. **字符串属性**
```dts
compatible = "vendor,device-name";
model = "Board Name v1.0";
status = "okay";  // 或 "disabled"
```

2. **整数属性**
```dts
reg = <0x02020000 0x4000>;  // 32位整数数组
clock-frequency = <100000>;  // 单个整数
interrupts = <0 26 4>;  // 中断号数组
```

3. **布尔属性**
```dts
interrupt-controller;  // 存在即为true
dma-coherent;
```

4. **字符串列表**
```dts
clock-names = "ipg", "per";
pinctrl-names = "default", "sleep";
```

5. **引用属性**
```dts
clocks = <&clks IMX6UL_CLK_UART1_IPG>,
         <&clks IMX6UL_CLK_UART1_SERIAL>;
interrupt-parent = <&intc>;
```

**标准属性说明**：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| compatible | 字符串列表 | 设备兼容性标识，驱动匹配的关键 |
| reg | 整数数组 | 寄存器地址和大小 |
| interrupts | 整数数组 | 中断号配置 |
| status | 字符串 | 设备状态："okay"或"disabled" |
| #address-cells | 整数 | 子节点地址单元数 |
| #size-cells | 整数 | 子节点大小单元数 |


#### 1.4 地址和大小单元

`#address-cells`和`#size-cells`定义子节点地址的格式。

**地址单元示例**：
```dts
soc {
    #address-cells = <1>;  // 地址用1个32位整数表示
    #size-cells = <1>;     // 大小用1个32位整数表示
    
    uart1: serial@02020000 {
        reg = <0x02020000 0x4000>;
        // 地址：0x02020000（1个单元）
        // 大小：0x4000（1个单元）
    };
};

// 64位地址示例
memory {
    #address-cells = <2>;  // 地址用2个32位整数表示
    #size-cells = <2>;     // 大小用2个32位整数表示
    
    ram@0 {
        reg = <0x0 0x80000000  0x0 0x40000000>;
        // 地址：0x0_80000000（2个单元）
        // 大小：0x0_40000000（2个单元，1GB）
    };
};
```

**理解要点**：
- `#address-cells`和`#size-cells`影响子节点的`reg`属性格式
- 值为1表示32位，值为2表示64位
- 这些属性定义在父节点中，应用于子节点

### 2. 设备树编译

#### 2.1 DTS文件组织

设备树源文件通常分为多个文件：

**文件类型**：
- **.dts**：设备树源文件，描述特定板子
- **.dtsi**：设备树包含文件，描述SoC或通用配置

**文件组织示例**：
```
arch/arm/boot/dts/
├── imx6ul.dtsi              # SoC通用配置
├── imx6ul-14x14-evk.dts     # 具体板子配置
└── imx6ul-pinfunc.h         # 引脚定义头文件
```

**包含文件语法**：
```dts
/dts-v1/;

#include "imx6ul.dtsi"  // 包含SoC配置
#include "imx6ul-pinfunc.h"  // 包含引脚定义

/ {
    model = "Freescale i.MX6 UltraLite 14x14 EVK Board";
    compatible = "fsl,imx6ul-14x14-evk", "fsl,imx6ul";
    
    // 板级特定配置
};
```

#### 2.2 编译过程

**编译工具**：Device Tree Compiler (DTC)

**编译命令**：
```bash
# 编译DTS到DTB
dtc -I dts -O dtb -o output.dtb input.dts

# 反编译DTB到DTS（用于调试）
dtc -I dtb -O dts -o output.dts input.dtb

# 使用内核编译系统
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- dtbs
```

**编译选项说明**：
- `-I`：输入格式（dts或dtb）
- `-O`：输出格式（dtb或dts）
- `-o`：输出文件名
- `-@`：生成符号信息（用于overlay）

**编译过程**：
```
DTS源文件 → 预处理（#include展开）→ DTC编译 → DTB二进制文件
   ↓              ↓                    ↓            ↓
.dts文件      展开的DTS            语法检查      .dtb文件
```

#### 2.3 DTB文件格式

DTB是设备树的二进制表示，包含三个主要部分：

**DTB结构**：
```
+------------------+
|   DTB Header     |  文件头（版本、大小等信息）
+------------------+
|  Memory Reserve  |  保留内存区域
+------------------+
|  Structure Block |  设备树结构（节点和属性）
+------------------+
|  Strings Block   |  字符串表（属性名和值）
+------------------+
```

**查看DTB信息**：
```bash
# 查看DTB文件信息
fdtdump output.dtb

# 使用hexdump查看二进制内容
hexdump -C output.dtb | head -20
```

### 3. 设备树结构详解

#### 3.1 根节点属性

根节点包含系统级别的信息。

**必需属性**：
```dts
/ {
    model = "Vendor Board Name";  // 板子型号
    compatible = "vendor,board", "vendor,soc";  // 兼容性列表
    
    #address-cells = <1>;  // 根节点地址单元
    #size-cells = <1>;     // 根节点大小单元
};
```

**可选属性**：
```dts
/ {
    serial-number = "1234567890";  // 序列号
    chassis-type = "embedded";     // 设备类型
};
```

#### 3.2 CPU节点

描述系统中的CPU信息。

**CPU节点示例**：
```dts
cpus {
    #address-cells = <1>;
    #size-cells = <0>;
    
    cpu0: cpu@0 {
        device_type = "cpu";
        compatible = "arm,cortex-a7";
        reg = <0>;
        clock-frequency = <528000000>;  // 528MHz
        operating-points = <
            /* kHz    uV */
            528000  1175000
            396000  1025000
            198000   950000
        >;
    };
    
    cpu1: cpu@1 {
        device_type = "cpu";
        compatible = "arm,cortex-a7";
        reg = <1>;
        clock-frequency = <528000000>;
    };
};
```


#### 3.3 内存节点

描述系统内存配置。

**内存节点示例**：
```dts
memory@80000000 {
    device_type = "memory";
    reg = <0x80000000 0x20000000>;  // 起始地址0x80000000，大小512MB
};

// 多个内存区域
memory {
    device_type = "memory";
    reg = <0x80000000 0x20000000>,  // 第一块：512MB
        <0xc0000000 0x20000000>;    // 第二块：512MB
};
```

#### 3.4 设备节点

描述具体的硬件设备。

**UART设备示例**：
```dts
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart", "fsl,imx6q-uart";
    reg = <0x02020000 0x4000>;
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    clock-names = "ipg", "per";
    dmas = <&sdma 25 4 0>, <&sdma 26 4 0>;
    dma-names = "rx", "tx";
    status = "disabled";  // 默认禁用，板级DTS中使能
};
```

**GPIO设备示例**：
```dts
gpio1: gpio@0209c000 {
    compatible = "fsl,imx6ul-gpio", "fsl,imx35-gpio";
    reg = <0x0209c000 0x4000>;
    interrupts = <GIC_SPI 66 IRQ_TYPE_LEVEL_HIGH>,
                 <GIC_SPI 67 IRQ_TYPE_LEVEL_HIGH>;
    gpio-controller;
    #gpio-cells = <2>;
    interrupt-controller;
    #interrupt-cells = <2>;
};
```

**I2C设备示例**：
```dts
i2c1: i2c@021a0000 {
    compatible = "fsl,imx6ul-i2c", "fsl,imx21-i2c";
    reg = <0x021a0000 0x4000>;
    interrupts = <GIC_SPI 36 IRQ_TYPE_LEVEL_HIGH>;
    clocks = <&clks IMX6UL_CLK_I2C1>;
    #address-cells = <1>;
    #size-cells = <0>;
    status = "disabled";
    
    // I2C总线上的设备
    eeprom@50 {
        compatible = "atmel,24c02";
        reg = <0x50>;
        pagesize = <16>;
    };
};
```

### 4. 设备树的引用和覆盖

#### 4.1 节点引用

使用标签引用已定义的节点。

**引用语法**：
```dts
// 在SoC的dtsi文件中定义
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;
    status = "disabled";  // 默认禁用
};

// 在板级dts文件中引用和修改
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_uart1>;
    status = "okay";  // 使能UART1
};
```

**引用的作用**：
- 避免重复定义节点
- 在板级DTS中定制SoC配置
- 保持SoC dtsi的通用性

#### 4.2 属性覆盖

后定义的属性会覆盖先定义的属性。

**覆盖示例**：
```dts
// SoC dtsi中的定义
i2c1: i2c@021a0000 {
    compatible = "fsl,imx6ul-i2c";
    clock-frequency = <100000>;  // 默认100kHz
    status = "disabled";
};

// 板级dts中的覆盖
&i2c1 {
    clock-frequency = <400000>;  // 修改为400kHz
    status = "okay";
    
    // 添加I2C设备
    sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
    };
};
```

#### 4.3 删除节点和属性

使用`/delete-node/`和`/delete-property/`删除不需要的内容。

**删除语法**：
```dts
&i2c1 {
    /delete-property/ dmas;  // 删除DMA属性
    /delete-property/ dma-names;
    
    /delete-node/ eeprom@50;  // 删除EEPROM设备节点
};
```

### 5. 常用设备树模式

#### 5.1 GPIO引脚配置

**引脚复用配置**：
```dts
iomuxc: iomuxc@020e0000 {
    compatible = "fsl,imx6ul-iomuxc";
    reg = <0x020e0000 0x4000>;
    
    pinctrl_uart1: uart1grp {
        fsl,pins = <
            MX6UL_PAD_UART1_TX_DATA__UART1_DCE_TX 0x1b0b1
            MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1
        >;
    };
    
    pinctrl_gpio_leds: gpioledsgrp {
        fsl,pins = <
            MX6UL_PAD_GPIO1_IO03__GPIO1_IO03 0x17059
        >;
    };
};

// 在设备节点中引用
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_uart1>;
    status = "okay";
};
```

#### 5.2 时钟配置

**时钟引用**：
```dts
clks: ccm@020c4000 {
    compatible = "fsl,imx6ul-ccm";
    reg = <0x020c4000 0x4000>;
    #clock-cells = <1>;
    clocks = <&ckil>, <&osc>, <&ipp_di0>, <&ipp_di1>;
    clock-names = "ckil", "osc", "ipp_di0", "ipp_di1";
};

// 设备使用时钟
&uart1 {
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    clock-names = "ipg", "per";
};
```

#### 5.3 中断配置

**中断控制器和中断配置**：
```dts
intc: interrupt-controller@00a01000 {
    compatible = "arm,cortex-a7-gic";
    #interrupt-cells = <3>;
    interrupt-controller;
    reg = <0x00a01000 0x1000>,
          <0x00a02000 0x100>;
};

// 设备使用中断
&uart1 {
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    interrupt-parent = <&intc>;
};
```

**中断属性说明**：
```dts
interrupts = <中断类型 中断号 触发方式>;

// 中断类型
GIC_SPI  // 共享外设中断
GIC_PPI  // 私有外设中断

// 触发方式
IRQ_TYPE_LEVEL_HIGH   // 高电平触发
IRQ_TYPE_LEVEL_LOW    // 低电平触发
IRQ_TYPE_EDGE_RISING  // 上升沿触发
IRQ_TYPE_EDGE_FALLING // 下降沿触发
```


## 实践示例

### 示例1：创建简单的设备树

从零开始创建一个简单的设备树文件：

```dts
/dts-v1/;

/ {
    model = "My Custom Board";
    compatible = "vendor,my-board";
    
    #address-cells = <1>;
    #size-cells = <1>;
    
    chosen {
        bootargs = "console=ttyS0,115200 root=/dev/mmcblk0p2 rootwait rw";
        stdout-path = &uart0;
    };
    
    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x20000000>;  // 512MB RAM
    };
    
    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        
        cpu@0 {
            device_type = "cpu";
            compatible = "arm,cortex-a7";
            reg = <0>;
            clock-frequency = <528000000>;
        };
    };
    
    soc {
        #address-cells = <1>;
        #size-cells = <1>;
        compatible = "simple-bus";
        ranges;
        
        uart0: serial@02020000 {
            compatible = "vendor,uart";
            reg = <0x02020000 0x4000>;
            interrupts = <0 26 4>;
            clock-frequency = <24000000>;
            status = "okay";
        };
        
        gpio1: gpio@0209c000 {
            compatible = "vendor,gpio";
            reg = <0x0209c000 0x4000>;
            gpio-controller;
            #gpio-cells = <2>;
            interrupts = <0 66 4>, <0 67 4>;
        };
    };
    
    leds {
        compatible = "gpio-leds";
        
        led0 {
            label = "status";
            gpios = <&gpio1 3 0>;  // GPIO1_3, 低电平有效
            default-state = "on";
        };
    };
};
```

**代码说明**：
- `chosen`节点：包含启动参数和控制台配置
- `memory`节点：定义512MB内存，起始地址0x80000000
- `cpus`节点：定义单核Cortex-A7处理器
- `soc`节点：包含SoC内部外设
- `leds`节点：定义GPIO控制的LED

### 示例2：板级DTS定制

基于SoC的dtsi文件创建板级配置：

**SoC dtsi文件（vendor-soc.dtsi）**：
```dts
/ {
    soc {
        uart1: serial@02020000 {
            compatible = "vendor,uart";
            reg = <0x02020000 0x4000>;
            interrupts = <0 26 4>;
            clocks = <&clks 100>, <&clks 101>;
            clock-names = "ipg", "per";
            status = "disabled";  // 默认禁用
        };
        
        i2c1: i2c@021a0000 {
            compatible = "vendor,i2c";
            reg = <0x021a0000 0x4000>;
            interrupts = <0 36 4>;
            #address-cells = <1>;
            #size-cells = <0>;
            status = "disabled";
        };
        
        spi1: spi@02008000 {
            compatible = "vendor,spi";
            reg = <0x02008000 0x4000>;
            interrupts = <0 31 4>;
            #address-cells = <1>;
            #size-cells = <0>;
            status = "disabled";
        };
    };
};
```

**板级DTS文件（my-board.dts）**：
```dts
/dts-v1/;

#include "vendor-soc.dtsi"

/ {
    model = "My Custom Board v1.0";
    compatible = "vendor,my-board", "vendor,soc";
    
    aliases {
        serial0 = &uart1;
        i2c0 = &i2c1;
    };
    
    chosen {
        stdout-path = "serial0:115200n8";
    };
    
    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;  // 1GB RAM
    };
    
    regulators {
        compatible = "simple-bus";
        
        reg_3v3: regulator-3v3 {
            compatible = "regulator-fixed";
            regulator-name = "3V3";
            regulator-min-microvolt = <3300000>;
            regulator-max-microvolt = <3300000>;
            regulator-always-on;
        };
    };
};

// 使能并配置UART1
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_uart1>;
    status = "okay";
};

// 使能并配置I2C1
&i2c1 {
    clock-frequency = <400000>;  // 400kHz
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_i2c1>;
    status = "okay";
    
    // 添加I2C设备
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

// 使能并配置SPI1
&spi1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_spi1>;
    cs-gpios = <&gpio1 16 0>;
    status = "okay";
    
    // 添加SPI设备
    flash@0 {
        compatible = "jedec,spi-nor";
        reg = <0>;
        spi-max-frequency = <20000000>;
    };
};
```

### 示例3：设备树调试

**查看运行时设备树**：
```bash
# 在Linux系统中查看设备树
ls /proc/device-tree/

# 查看特定节点
cat /proc/device-tree/model
cat /proc/device-tree/compatible

# 查看设备树的完整结构
ls -R /proc/device-tree/

# 使用sysfs查看设备树
cat /sys/firmware/devicetree/base/model
```

**编译和测试**：
```bash
# 编译设备树
dtc -I dts -O dtb -o my-board.dtb my-board.dts

# 检查编译错误
dtc -I dts -O dtb -o my-board.dtb my-board.dts -W no-unit_address_vs_reg

# 反编译查看结果
dtc -I dtb -O dts -o my-board-check.dts my-board.dtb

# 比较原始和反编译的文件
diff my-board.dts my-board-check.dts
```

**常见编译警告处理**：
```bash
# 忽略特定警告
dtc -I dts -O dtb -o output.dtb input.dts \
    -W no-unit_address_vs_reg \
    -W no-simple_bus_reg

# 显示所有警告
dtc -I dts -O dtb -o output.dtb input.dts -W all

# 将警告视为错误
dtc -I dts -O dtb -o output.dtb input.dts -W error
```

## 深入理解

### compatible属性的匹配机制

`compatible`属性是驱动和设备匹配的关键。

**匹配规则**：
```dts
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart", "fsl,imx6q-uart", "fsl,imx21-uart";
    // 驱动会按顺序尝试匹配
};
```

**驱动匹配过程**：
1. 内核遍历设备树中的所有设备节点
2. 对每个节点，读取`compatible`属性
3. 在已注册的驱动中查找匹配的`compatible`字符串
4. 找到匹配后，调用驱动的probe函数

**驱动中的匹配表**：
```c
static const struct of_device_id uart_dt_ids[] = {
    { .compatible = "fsl,imx6ul-uart", },
    { .compatible = "fsl,imx6q-uart", },
    { .compatible = "fsl,imx21-uart", },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, uart_dt_ids);

static struct platform_driver uart_driver = {
    .driver = {
        .name = "imx-uart",
        .of_match_table = uart_dt_ids,
    },
    .probe = uart_probe,
    .remove = uart_remove,
};
```

### reg属性的地址转换

`reg`属性的解析依赖于父节点的`#address-cells`和`#size-cells`。

**地址转换示例**：
```dts
soc {
    #address-cells = <1>;
    #size-cells = <1>;
    ranges = <0x0 0x02000000 0x100000>;  // 地址映射
    
    uart1: serial@20000 {
        reg = <0x20000 0x4000>;
        // 实际物理地址 = 0x02000000 + 0x20000 = 0x02020000
    };
};
```

**ranges属性说明**：
```dts
ranges = <子地址 父地址 大小>;

// 示例
ranges = <0x0 0x02000000 0x100000>;
// 子地址0x0映射到父地址0x02000000，范围1MB

// 空ranges表示1:1映射
ranges;

// 没有ranges属性表示不可寻址
```


### 设备树的启动流程

**完整启动流程**：
```
1. Bootloader加载
   ├─ 加载内核镜像到内存
   ├─ 加载DTB到内存
   └─ 将DTB地址传递给内核

2. 内核启动
   ├─ 解析DTB文件头
   ├─ 展开设备树到内存
   └─ 构建设备树数据结构

3. 设备初始化
   ├─ 遍历设备树节点
   ├─ 匹配驱动
   └─ 调用probe函数

4. 系统运行
   └─ 驱动通过API访问设备树
```

**U-Boot中的设备树操作**：
```bash
# 查看设备树地址
fdt addr

# 打印设备树
fdt print

# 修改设备树
fdt set /chosen bootargs "console=ttyS0,115200"

# 启动内核并传递设备树
bootz ${kernel_addr} - ${fdt_addr}
```

### 最佳实践

1. **保持SoC dtsi的通用性**
   ```dts
   // SoC dtsi中：定义所有可能的外设，默认禁用
   uart1: serial@02020000 {
       compatible = "vendor,uart";
       reg = <0x02020000 0x4000>;
       status = "disabled";  // 默认禁用
   };
   
   // 板级dts中：只使能需要的外设
   &uart1 {
       status = "okay";  // 使能
   };
   ```

2. **使用有意义的标签**
   ```dts
   // 好的标签命名
   uart1: serial@02020000 { };
   i2c_sensor: i2c@021a0000 { };
   
   // 避免无意义的标签
   node1: serial@02020000 { };
   device: i2c@021a0000 { };
   ```

3. **合理组织节点层次**
   ```dts
   / {
       soc {  // SoC内部外设
           uart1: serial@02020000 { };
           i2c1: i2c@021a0000 { };
       };
       
       // 板级外设（不在SoC内部）
       leds {
           compatible = "gpio-leds";
       };
       
       regulators {
           compatible = "simple-bus";
       };
   };
   ```

4. **使用宏定义提高可读性**
   ```dts
   #include <dt-bindings/gpio/gpio.h>
   #include <dt-bindings/interrupt-controller/irq.h>
   
   leds {
       led0 {
           gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;  // 使用宏
       };
   };
   
   &uart1 {
       interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;  // 使用宏
   };
   ```

5. **添加注释说明**
   ```dts
   memory@80000000 {
       device_type = "memory";
       reg = <0x80000000 0x40000000>;  /* 1GB DDR3 RAM */
   };
   
   &i2c1 {
       clock-frequency = <400000>;  /* 400kHz fast mode */
       
       /* Temperature sensor */
       sensor@48 {
           compatible = "ti,tmp102";
           reg = <0x48>;
       };
   };
   ```

## 常见问题

### Q1: 设备树和驱动如何匹配？

**A**: 通过`compatible`属性匹配。

**匹配过程**：
```c
// 设备树中
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
};

// 驱动中
static const struct of_device_id uart_dt_ids[] = {
    { .compatible = "fsl,imx6ul-uart", },
    { }
};

// 内核会自动匹配并调用probe函数
static int uart_probe(struct platform_device *pdev) {
    // 获取设备树信息
    struct device_node *np = pdev->dev.of_node;
    // ...
}
```

**匹配优先级**：
- `compatible`属性可以包含多个字符串
- 驱动按顺序尝试匹配
- 第一个匹配成功的会被使用

### Q2: 如何在驱动中读取设备树信息？

**A**: 使用内核提供的OF（Open Firmware）API。

**常用API**：
```c
#include <linux/of.h>
#include <linux/of_device.h>

// 读取属性
int of_property_read_u32(struct device_node *np, const char *propname, u32 *out_value);
int of_property_read_string(struct device_node *np, const char *propname, const char **out_string);

// 读取GPIO
int of_get_named_gpio(struct device_node *np, const char *propname, int index);

// 读取中断
int of_irq_get(struct device_node *np, int index);

// 读取时钟
struct clk *of_clk_get(struct device_node *np, int index);
```

**使用示例**：
```c
static int my_driver_probe(struct platform_device *pdev) {
    struct device_node *np = pdev->dev.of_node;
    u32 clock_freq;
    const char *name;
    int gpio, irq;
    
    // 读取时钟频率
    if (of_property_read_u32(np, "clock-frequency", &clock_freq)) {
        dev_err(&pdev->dev, "Failed to read clock-frequency\n");
        return -EINVAL;
    }
    
    // 读取字符串属性
    if (of_property_read_string(np, "label", &name)) {
        name = "default";
    }
    
    // 读取GPIO
    gpio = of_get_named_gpio(np, "reset-gpios", 0);
    if (gpio_is_valid(gpio)) {
        gpio_request(gpio, "reset");
    }
    
    // 读取中断
    irq = of_irq_get(np, 0);
    if (irq > 0) {
        request_irq(irq, my_irq_handler, 0, "my-device", NULL);
    }
    
    return 0;
}
```

### Q3: 设备树修改后需要重新编译内核吗？

**A**: 不需要，只需重新编译设备树。

**修改流程**：
```bash
# 1. 修改DTS文件
vim arch/arm/boot/dts/my-board.dts

# 2. 只编译设备树
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- dtbs

# 3. 复制新的DTB到启动分区
cp arch/arm/boot/dts/my-board.dtb /boot/

# 4. 重启系统
reboot
```

**注意事项**：
- 内核镜像不需要重新编译
- 只需要更新DTB文件
- 某些Bootloader支持从网络或SD卡加载DTB

### Q4: 如何调试设备树问题？

**A**: 使用多种调试方法。

**调试方法**：

1. **编译时检查**
```bash
# 使用dtc检查语法
dtc -I dts -O dtb -o output.dtb input.dts

# 查看详细警告
dtc -I dts -O dtb -o output.dtb input.dts -W all
```

2. **运行时检查**
```bash
# 查看设备树内容
ls /proc/device-tree/
cat /proc/device-tree/model

# 查看设备匹配情况
cat /sys/bus/platform/devices/*/modalias
cat /sys/bus/platform/drivers/*/uevent
```

3. **内核日志**
```bash
# 查看设备树相关日志
dmesg | grep -i "device tree"
dmesg | grep -i "of:"

# 查看设备probe日志
dmesg | grep -i "probe"
```

4. **使用内核配置选项**
```bash
# 使能设备树调试
CONFIG_OF_DYNAMIC=y
CONFIG_OF_UNITTEST=y
```

## 总结

设备树是现代嵌入式Linux系统的核心组件，掌握设备树的基本概念和使用方法对于嵌入式开发至关重要。本文介绍的核心要点包括：

- **设备树概念**：硬件描述与软件分离的标准方法
- **DTS语法**：节点、属性、引用和覆盖的基本语法
- **编译过程**：从DTS到DTB的编译和使用流程
- **设备树结构**：根节点、CPU、内存和设备节点的组织
- **实践应用**：板级定制、设备配置和调试方法

## 延伸阅读

推荐进一步学习的资源：

- 设备树编写与调试 - 深入学习设备树编写技巧
- 板级支持包开发 - 完整的BSP开发流程
- [Linux设备驱动开发](../02-device-driver-development/) - 驱动如何使用设备树
- [Device Tree Specification](https://www.devicetree.org/) - 官方设备树规范

## 参考资料

1. Device Tree Specification - devicetree.org
2. Linux Kernel Documentation - Device Tree
3. U-Boot Device Tree Documentation
4. ARM Device Tree Bindings

---

**练习题**：

1. 创建一个包含UART、I2C和GPIO的简单设备树文件
2. 编译设备树并使用fdtdump查看结构
3. 修改现有设备树，添加一个LED设备节点
4. 使用设备树引用机制，在板级DTS中使能SoC的外设

**下一步**：建议学习 设备树编写与调试，深入掌握设备树的高级用法和调试技巧。
