---
title: "设备树编写与调试"
description: "深入学习设备树的编写技巧、节点定义、属性配置、引用关系、覆盖机制和调试方法，掌握实际项目中的设备树开发和问题排查技能"
slug: "device-tree-writing"

# 分类信息
domain: "驱动与BSP层"
module: "设备树与板级支持"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 设备树编写
  - DTS调试
  - 节点配置
  - 设备树覆盖
  - 引用机制
prerequisites:
  - "device-tree-basics"
related_contents: []

# 学习信息
estimated_time: 80
difficulty_score: 6

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
  - 设备树编写
  - Device Tree
  - DTS调试
  - 节点配置
  - 设备树覆盖
cover_image: ""
---

# 设备树编写与调试

## 概述

设备树编写是嵌入式Linux开发中的重要技能。本教程将带你深入学习如何编写、修改和调试设备树，掌握节点定义、属性配置、引用关系和覆盖机制等核心技术。完成本教程后，你将能够：

- 熟练编写设备树节点和属性
- 掌握设备树的引用和覆盖机制
- 理解设备树的编译和部署流程
- 使用多种工具调试设备树问题
- 解决常见的设备树配置错误

## 前置知识

在开始本教程之前，你应该：

- 理解设备树的基本概念和作用
- 熟悉DTS的基本语法
- 了解Linux设备驱动的基本原理
- 具备基本的嵌入式Linux开发经验

建议先完成 [设备树基础概念](../beginner/01-device-tree-basics.html) 的学习。

## 实验环境准备

### 所需工具

1. **设备树编译器（DTC）**
```bash
# Ubuntu/Debian安装
sudo apt-get install device-tree-compiler

# 验证安装
dtc --version
```

2. **文本编辑器**
```bash
# 推荐使用支持语法高亮的编辑器
# vim, vscode, sublime text等
```

3. **交叉编译工具链**（如果需要在目标板上测试）
```bash
# ARM工具链示例
sudo apt-get install gcc-arm-linux-gnueabihf
```


### 实验文件结构

创建以下目录结构用于本教程的实验：

```bash
mkdir -p dts-tutorial/{include,output}
cd dts-tutorial
```

目录说明：
- `include/`：存放.dtsi包含文件
- `output/`：存放编译生成的.dtb文件

## 核心内容

### 1. 节点定义详解

#### 1.1 节点命名规范

设备树节点的命名遵循特定的规范，正确的命名有助于代码的可读性和维护性。

**节点命名格式**：
```dts
node-name[@unit-address] {
    // 节点内容
};
```

**命名规则**：
- 节点名使用小写字母、数字和连字符（-）
- 不要使用下划线（_）
- 如果节点有地址，使用@分隔名称和地址
- 地址使用十六进制，不带0x前缀

**正确的命名示例**：
```dts
// 好的命名
serial@12340000 { };
i2c@21a0000 { };
gpio-controller@209c000 { };
ethernet@30be0000 { };

// 不推荐的命名
Serial@12340000 { };      // 大写字母
i2c_controller@21a0000 { }; // 使用下划线
gpio@0x209c000 { };        // 地址带0x前缀
```

**特殊节点名称**：
```dts
/ {              // 根节点
    chosen { };  // 启动参数节点
    aliases { }; // 别名节点
    memory { };  // 内存节点（可以不带地址）
    cpus { };    // CPU节点
};
```


#### 1.2 节点标签的使用

标签（Label）是设备树中引用节点的重要机制。

**标签定义语法**：
```dts
label: node-name@address {
    // 节点内容
};
```

**标签使用示例**：
```dts
// 定义带标签的节点
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;
    status = "disabled";
};

gpio1: gpio@0209c000 {
    compatible = "fsl,imx6ul-gpio";
    reg = <0x0209c000 0x4000>;
    gpio-controller;
    #gpio-cells = <2>;
};

// 使用标签引用节点
&uart1 {
    status = "okay";  // 修改状态
};

// 在属性中引用标签
leds {
    led0 {
        gpios = <&gpio1 3 0>;  // 引用gpio1节点
    };
};
```

**标签命名建议**：
```dts
// 使用有意义的标签名
uart1: serial@02020000 { };     // 好
i2c_sensor: i2c@021a0000 { };   // 好
main_clk: clock { };            // 好

// 避免无意义的标签名
node1: serial@02020000 { };     // 不好
dev: i2c@021a0000 { };          // 不好
```


#### 1.3 节点层次结构设计

合理的节点层次结构能够清晰地表达硬件的组织关系。

**层次结构示例**：
```dts
/ {
    model = "Custom Board";
    compatible = "vendor,board";
    
    // 第一层：系统级节点
    cpus {
        // CPU节点
    };
    
    memory@80000000 {
        // 内存节点
    };
    
    // 第二层：SoC节点
    soc {
        compatible = "simple-bus";
        #address-cells = <1>;
        #size-cells = <1>;
        ranges;
        
        // 第三层：SoC内部外设
        aips1: aips-bus@02000000 {
            compatible = "fsl,aips-bus", "simple-bus";
            #address-cells = <1>;
            #size-cells = <1>;
            ranges;
            
            // 第四层：总线上的设备
            uart1: serial@02020000 {
                // UART设备
            };
            
            i2c1: i2c@021a0000 {
                #address-cells = <1>;
                #size-cells = <0>;
                
                // 第五层：I2C总线上的设备
                eeprom@50 {
                    compatible = "atmel,24c256";
                    reg = <0x50>;
                };
            };
        };
    };
    
    // 板级外设（不在SoC内部）
    regulators {
        // 电源管理
    };
    
    leds {
        // LED设备
    };
    
    gpio-keys {
        // 按键设备
    };
};
```

**层次设计原则**：
1. 根节点包含系统级信息
2. SoC节点包含片上外设
3. 总线节点包含总线上的设备
4. 板级外设独立于SoC节点
5. 使用`simple-bus`表示简单总线


### 2. 属性配置详解

#### 2.1 标准属性详解

设备树定义了一组标准属性，理解这些属性对于正确配置设备至关重要。

**compatible属性**：

这是最重要的属性，用于驱动匹配。

```dts
uart1: serial@02020000 {
    // 从最具体到最通用的顺序列出
    compatible = "fsl,imx6ul-uart",    // 最具体的型号
                 "fsl,imx6q-uart",     // 兼容的型号
                 "fsl,imx21-uart";     // 通用的型号
};
```

**compatible属性规则**：
- 格式：`"manufacturer,model"`
- 可以包含多个字符串（按优先级排序）
- 驱动会按顺序尝试匹配
- 第一个匹配成功的会被使用

**reg属性**：

定义设备的寄存器地址和大小。

```dts
soc {
    #address-cells = <1>;  // 地址用1个32位整数
    #size-cells = <1>;     // 大小用1个32位整数
    
    uart1: serial@02020000 {
        reg = <0x02020000 0x4000>;
        // 地址：0x02020000
        // 大小：0x4000 (16KB)
    };
    
    // 多个寄存器区域
    ethernet@30be0000 {
        reg = <0x30be0000 0x10000>,  // 主寄存器
              <0x30bf0000 0x10000>;  // 辅助寄存器
    };
};
```

**64位地址示例**：
```dts
soc {
    #address-cells = <2>;  // 地址用2个32位整数
    #size-cells = <2>;     // 大小用2个32位整数
    
    pcie@0x8000000000 {
        reg = <0x80 0x00000000  0x0 0x10000000>;
        // 地址：0x80_00000000
        // 大小：0x0_10000000 (256MB)
    };
};
```


**status属性**：

控制设备的启用状态。

```dts
// SoC dtsi中默认禁用
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;
    status = "disabled";  // 默认禁用
};

// 板级dts中选择性启用
&uart1 {
    status = "okay";  // 启用设备
};

// 其他可能的值
status = "disabled";  // 禁用
status = "okay";      // 启用
status = "fail";      // 设备有问题
status = "fail-sss";  // 设备有问题，sss是原因
```

**interrupts属性**：

定义设备的中断配置。

```dts
// 中断控制器
intc: interrupt-controller@00a01000 {
    compatible = "arm,cortex-a7-gic";
    #interrupt-cells = <3>;
    interrupt-controller;
    reg = <0x00a01000 0x1000>,
          <0x00a02000 0x100>;
};

// 使用中断的设备
uart1: serial@02020000 {
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    // 参数1：中断类型（GIC_SPI=共享外设中断）
    // 参数2：中断号（26）
    // 参数3：触发方式（高电平触发）
    interrupt-parent = <&intc>;
};

// 多个中断
gpio1: gpio@0209c000 {
    interrupts = <GIC_SPI 66 IRQ_TYPE_LEVEL_HIGH>,
                 <GIC_SPI 67 IRQ_TYPE_LEVEL_HIGH>;
};
```

**中断触发类型**：
```dts
#include <dt-bindings/interrupt-controller/irq.h>

IRQ_TYPE_NONE           // 无特定类型
IRQ_TYPE_EDGE_RISING    // 上升沿触发
IRQ_TYPE_EDGE_FALLING   // 下降沿触发
IRQ_TYPE_EDGE_BOTH      // 双边沿触发
IRQ_TYPE_LEVEL_HIGH     // 高电平触发
IRQ_TYPE_LEVEL_LOW      // 低电平触发
```


**clocks和clock-names属性**：

定义设备使用的时钟。

```dts
// 时钟控制器
clks: ccm@020c4000 {
    compatible = "fsl,imx6ul-ccm";
    reg = <0x020c4000 0x4000>;
    #clock-cells = <1>;
};

// 使用时钟的设备
uart1: serial@02020000 {
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    clock-names = "ipg", "per";
    // ipg: 接口时钟
    // per: 外设时钟
};

// 单个时钟
i2c1: i2c@021a0000 {
    clocks = <&clks IMX6UL_CLK_I2C1>;
    clock-names = "i2c";
};
```

**pinctrl属性**：

定义引脚复用配置。

```dts
// 引脚控制器
iomuxc: iomuxc@020e0000 {
    compatible = "fsl,imx6ul-iomuxc";
    reg = <0x020e0000 0x4000>;
    
    // 定义引脚组
    pinctrl_uart1: uart1grp {
        fsl,pins = <
            MX6UL_PAD_UART1_TX_DATA__UART1_DCE_TX 0x1b0b1
            MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1
        >;
    };
};

// 使用引脚配置
&uart1 {
    pinctrl-names = "default", "sleep";
    pinctrl-0 = <&pinctrl_uart1>;        // default状态
    pinctrl-1 = <&pinctrl_uart1_sleep>;  // sleep状态
};
```


#### 2.2 自定义属性

除了标准属性，还可以定义设备特定的自定义属性。

**自定义属性示例**：
```dts
// 字符串属性
uart1: serial@02020000 {
    compatible = "vendor,uart";
    label = "Debug Console";
    uart-has-rtscts;  // 布尔属性
};

// 整数属性
i2c1: i2c@021a0000 {
    compatible = "vendor,i2c";
    clock-frequency = <400000>;  // 400kHz
    scl-gpios = <&gpio1 2 0>;
    sda-gpios = <&gpio1 3 0>;
};

// 整数数组
adc: adc@02198000 {
    compatible = "vendor,adc";
    vref-supply = <&reg_vref_3v3>;
    channel-mask = <0x0f>;  // 使用通道0-3
    resolution-bits = <12>;
};

// 字符串列表
spi1: spi@02008000 {
    compatible = "vendor,spi";
    dma-names = "tx", "rx";
    dmas = <&sdma 3 7 1>, <&sdma 4 7 2>;
};
```

**属性命名规范**：
- 使用小写字母和连字符
- 使用描述性的名称
- 遵循设备树规范的命名约定
- 厂商特定属性使用厂商前缀

**常见自定义属性**：
```dts
// GPIO相关
reset-gpios = <&gpio1 5 GPIO_ACTIVE_LOW>;
enable-gpios = <&gpio2 10 GPIO_ACTIVE_HIGH>;

// 电源相关
vdd-supply = <&reg_3v3>;
vddio-supply = <&reg_1v8>;

// 频率相关
clock-frequency = <100000>;
max-frequency = <50000000>;

// 布尔标志
dma-coherent;
interrupt-controller;
gpio-controller;
```


### 3. 引用关系详解

#### 3.1 节点引用（Phandle）

Phandle是设备树中节点间引用的机制。

**显式phandle**：
```dts
// 定义phandle
intc: interrupt-controller@00a01000 {
    compatible = "arm,cortex-a7-gic";
    interrupt-controller;
    #interrupt-cells = <3>;
    phandle = <1>;  // 显式定义phandle
};

// 使用phandle引用
uart1: serial@02020000 {
    interrupt-parent = <1>;  // 引用phandle=1的节点
};
```

**隐式phandle（推荐）**：
```dts
// 使用标签自动生成phandle
intc: interrupt-controller@00a01000 {
    compatible = "arm,cortex-a7-gic";
    interrupt-controller;
    #interrupt-cells = <3>;
    // 编译器自动生成phandle
};

// 使用标签引用
uart1: serial@02020000 {
    interrupt-parent = <&intc>;  // 使用标签引用
};
```

**引用示例**：
```dts
// GPIO控制器
gpio1: gpio@0209c000 {
    compatible = "fsl,imx6ul-gpio";
    gpio-controller;
    #gpio-cells = <2>;
};

// 时钟控制器
clks: ccm@020c4000 {
    compatible = "fsl,imx6ul-ccm";
    #clock-cells = <1>;
};

// 电源调节器
reg_3v3: regulator-3v3 {
    compatible = "regulator-fixed";
    regulator-name = "3V3";
};

// 使用多个引用
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    clocks = <&clks IMX6UL_CLK_UART1_IPG>;  // 引用时钟
    vdd-supply = <&reg_3v3>;                // 引用电源
    rts-gpios = <&gpio1 18 GPIO_ACTIVE_LOW>; // 引用GPIO
};
```


#### 3.2 #cells属性

`#cells`属性定义了引用该节点时需要的参数个数。

**#gpio-cells示例**：
```dts
gpio1: gpio@0209c000 {
    compatible = "fsl,imx6ul-gpio";
    gpio-controller;
    #gpio-cells = <2>;
    // 参数1：GPIO引脚号
    // 参数2：标志位（极性等）
};

// 使用GPIO
leds {
    led0 {
        gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
        // gpio1: 引用的GPIO控制器
        // 3: GPIO引脚号
        // GPIO_ACTIVE_LOW: 低电平有效
    };
};
```

**#clock-cells示例**：
```dts
clks: ccm@020c4000 {
    compatible = "fsl,imx6ul-ccm";
    #clock-cells = <1>;
    // 参数1：时钟ID
};

// 使用时钟
uart1: serial@02020000 {
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    // clks: 引用的时钟控制器
    // IMX6UL_CLK_UART1_IPG: 时钟ID
};
```

**#interrupt-cells示例**：
```dts
intc: interrupt-controller@00a01000 {
    compatible = "arm,cortex-a7-gic";
    interrupt-controller;
    #interrupt-cells = <3>;
    // 参数1：中断类型
    // 参数2：中断号
    // 参数3：触发方式
};

// 使用中断
uart1: serial@02020000 {
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    // GIC_SPI: 中断类型
    // 26: 中断号
    // IRQ_TYPE_LEVEL_HIGH: 触发方式
};
```

**#address-cells和#size-cells**：
```dts
i2c1: i2c@021a0000 {
    compatible = "fsl,imx6ul-i2c";
    #address-cells = <1>;  // I2C设备地址用1个单元
    #size-cells = <0>;     // I2C设备没有大小
    
    // I2C总线上的设备
    eeprom@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;  // 只有地址，没有大小
    };
    
    sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
    };
};
```


### 4. 覆盖机制详解

#### 4.1 节点覆盖

使用标签引用可以覆盖或扩展已定义的节点。

**基本覆盖**：
```dts
// SoC dtsi文件中的定义
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    clock-names = "ipg", "per";
    status = "disabled";  // 默认禁用
};

// 板级dts文件中的覆盖
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_uart1>;
    status = "okay";  // 启用设备
    // 其他属性保持不变
};
```

**添加子节点**：
```dts
// SoC dtsi中的I2C定义
i2c1: i2c@021a0000 {
    compatible = "fsl,imx6ul-i2c";
    reg = <0x021a0000 0x4000>;
    #address-cells = <1>;
    #size-cells = <0>;
    status = "disabled";
};

// 板级dts中添加I2C设备
&i2c1 {
    clock-frequency = <400000>;
    status = "okay";
    
    // 添加EEPROM设备
    eeprom@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;
        pagesize = <64>;
    };
    
    // 添加RTC设备
    rtc@68 {
        compatible = "dallas,ds1307";
        reg = <0x68>;
    };
};
```

**修改属性值**：
```dts
// SoC dtsi中的定义
spi1: spi@02008000 {
    compatible = "fsl,imx6ul-ecspi";
    reg = <0x02008000 0x4000>;
    #address-cells = <1>;
    #size-cells = <0>;
    spi-max-frequency = <20000000>;  // 默认20MHz
    status = "disabled";
};

// 板级dts中修改
&spi1 {
    spi-max-frequency = <10000000>;  // 修改为10MHz
    cs-gpios = <&gpio1 16 GPIO_ACTIVE_LOW>;
    status = "okay";
};
```


#### 4.2 删除节点和属性

使用`/delete-node/`和`/delete-property/`删除不需要的内容。

**删除属性**：
```dts
// SoC dtsi中的定义
uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;
    dmas = <&sdma 25 4 0>, <&sdma 26 4 0>;
    dma-names = "rx", "tx";
    status = "disabled";
};

// 板级dts中删除DMA属性（不使用DMA）
&uart1 {
    /delete-property/ dmas;
    /delete-property/ dma-names;
    status = "okay";
};
```

**删除子节点**：
```dts
// SoC dtsi中的定义
i2c1: i2c@021a0000 {
    compatible = "fsl,imx6ul-i2c";
    #address-cells = <1>;
    #size-cells = <0>;
    
    // 默认包含的设备
    codec@1a {
        compatible = "wlf,wm8960";
        reg = <0x1a>;
    };
};

// 板级dts中删除不需要的设备
&i2c1 {
    /delete-node/ codec@1a;  // 删除codec设备
    
    // 添加实际使用的设备
    sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
    };
};
```

**批量删除**：
```dts
&spi1 {
    /delete-property/ dmas;
    /delete-property/ dma-names;
    /delete-property/ dma-channels;
    
    /delete-node/ flash@0;
    /delete-node/ spidev@1;
};
```


#### 4.3 设备树覆盖（Device Tree Overlay）

设备树覆盖允许在运行时动态修改设备树，常用于可插拔硬件。

**覆盖文件示例**：
```dts
/dts-v1/;
/plugin/;

// 覆盖文件：spi-flash-overlay.dts
/ {
    compatible = "vendor,board";
    
    fragment@0 {
        target = <&spi1>;
        __overlay__ {
            #address-cells = <1>;
            #size-cells = <0>;
            
            flash@0 {
                compatible = "jedec,spi-nor";
                reg = <0>;
                spi-max-frequency = <20000000>;
            };
        };
    };
};
```

**编译覆盖文件**：
```bash
# 编译覆盖文件
dtc -@ -I dts -O dtb -o spi-flash-overlay.dtbo spi-flash-overlay.dts

# -@: 生成符号信息（必需）
# .dtbo: 覆盖文件扩展名
```

**应用覆盖**：
```bash
# 在Linux运行时应用覆盖
mkdir /sys/kernel/config/device-tree/overlays/spi-flash
cat spi-flash-overlay.dtbo > /sys/kernel/config/device-tree/overlays/spi-flash/dtbo

# 移除覆盖
rmdir /sys/kernel/config/device-tree/overlays/spi-flash
```

**多片段覆盖**：
```dts
/dts-v1/;
/plugin/;

/ {
    compatible = "vendor,board";
    
    // 片段1：配置SPI
    fragment@0 {
        target = <&spi1>;
        __overlay__ {
            status = "okay";
        };
    };
    
    // 片段2：配置引脚
    fragment@1 {
        target = <&iomuxc>;
        __overlay__ {
            pinctrl_spi1: spi1grp {
                fsl,pins = <
                    MX6UL_PAD_CSI_DATA07__ECSPI1_MISO 0x100b1
                    MX6UL_PAD_CSI_DATA06__ECSPI1_MOSI 0x100b1
                    MX6UL_PAD_CSI_DATA04__ECSPI1_SCLK 0x100b1
                >;
            };
        };
    };
    
    // 片段3：添加SPI设备
    fragment@2 {
        target = <&spi1>;
        __overlay__ {
            #address-cells = <1>;
            #size-cells = <0>;
            
            flash@0 {
                compatible = "jedec,spi-nor";
                reg = <0>;
                spi-max-frequency = <20000000>;
            };
        };
    };
};
```


### 5. 实践项目：创建完整的板级设备树

#### 5.1 项目目标

创建一个完整的板级设备树，包含：
- 基本系统配置
- UART串口
- I2C总线和设备
- SPI总线和Flash
- GPIO LED和按键
- 网络接口

#### 5.2 创建SoC dtsi文件

首先创建SoC的通用配置文件。

**文件：include/vendor-soc.dtsi**
```dts
/dts-v1/;

/ {
    #address-cells = <1>;
    #size-cells = <1>;
    
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
        
        // 中断控制器
        intc: interrupt-controller@00a01000 {
            compatible = "arm,cortex-a7-gic";
            #interrupt-cells = <3>;
            interrupt-controller;
            reg = <0x00a01000 0x1000>,
                  <0x00a02000 0x100>;
        };
        
        // 时钟控制器
        clks: ccm@020c4000 {
            compatible = "vendor,ccm";
            reg = <0x020c4000 0x4000>;
            #clock-cells = <1>;
        };
        
        // GPIO控制器
        gpio1: gpio@0209c000 {
            compatible = "vendor,gpio";
            reg = <0x0209c000 0x4000>;
            interrupts = <0 66 4>, <0 67 4>;
            gpio-controller;
            #gpio-cells = <2>;
            interrupt-controller;
            #interrupt-cells = <2>;
        };
        
        gpio2: gpio@020a0000 {
            compatible = "vendor,gpio";
            reg = <0x020a0000 0x4000>;
            interrupts = <0 68 4>, <0 69 4>;
            gpio-controller;
            #gpio-cells = <2>;
            interrupt-controller;
            #interrupt-cells = <2>;
        };
```


        // UART控制器
        uart1: serial@02020000 {
            compatible = "vendor,uart";
            reg = <0x02020000 0x4000>;
            interrupts = <0 26 4>;
            clocks = <&clks 100>, <&clks 101>;
            clock-names = "ipg", "per";
            status = "disabled";
        };
        
        uart2: serial@021e8000 {
            compatible = "vendor,uart";
            reg = <0x021e8000 0x4000>;
            interrupts = <0 27 4>;
            clocks = <&clks 102>, <&clks 103>;
            clock-names = "ipg", "per";
            status = "disabled";
        };
        
        // I2C控制器
        i2c1: i2c@021a0000 {
            compatible = "vendor,i2c";
            reg = <0x021a0000 0x4000>;
            interrupts = <0 36 4>;
            clocks = <&clks 110>;
            #address-cells = <1>;
            #size-cells = <0>;
            status = "disabled";
        };
        
        i2c2: i2c@021a4000 {
            compatible = "vendor,i2c";
            reg = <0x021a4000 0x4000>;
            interrupts = <0 37 4>;
            clocks = <&clks 111>;
            #address-cells = <1>;
            #size-cells = <0>;
            status = "disabled";
        };
        
        // SPI控制器
        spi1: spi@02008000 {
            compatible = "vendor,spi";
            reg = <0x02008000 0x4000>;
            interrupts = <0 31 4>;
            clocks = <&clks 112>, <&clks 113>;
            clock-names = "ipg", "per";
            #address-cells = <1>;
            #size-cells = <0>;
            status = "disabled";
        };
        
        // 以太网控制器
        ethernet: ethernet@30be0000 {
            compatible = "vendor,fec";
            reg = <0x30be0000 0x10000>;
            interrupts = <0 118 4>, <0 119 4>;
            clocks = <&clks 120>, <&clks 121>, <&clks 122>;
            clock-names = "ipg", "ahb", "ptp";
            status = "disabled";
        };
    };
};
```

保存此文件为 `include/vendor-soc.dtsi`。


#### 5.3 创建板级dts文件

基于SoC dtsi创建板级配置。

**文件：my-board.dts**
```dts
/dts-v1/;

#include "include/vendor-soc.dtsi"

/ {
    model = "My Custom Board v1.0";
    compatible = "vendor,my-board", "vendor,soc";
    
    // 别名定义
    aliases {
        serial0 = &uart1;
        serial1 = &uart2;
        ethernet0 = &ethernet;
        i2c0 = &i2c1;
        i2c1 = &i2c2;
        spi0 = &spi1;
    };
    
    // 启动参数
    chosen {
        bootargs = "console=ttyS0,115200 root=/dev/mmcblk0p2 rootwait rw";
        stdout-path = "serial0:115200n8";
    };
    
    // 内存配置
    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;  // 1GB DDR3
    };
    
    // 电源调节器
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
        
        reg_1v8: regulator@1 {
            compatible = "regulator-fixed";
            reg = <1>;
            regulator-name = "1V8";
            regulator-min-microvolt = <1800000>;
            regulator-max-microvolt = <1800000>;
            regulator-always-on;
        };
    };
    
    // LED设备
    leds {
        compatible = "gpio-leds";
        
        led-status {
            label = "status";
            gpios = <&gpio1 3 0>;
            default-state = "on";
            linux,default-trigger = "heartbeat";
        };
        
        led-user {
            label = "user";
            gpios = <&gpio1 4 0>;
            default-state = "off";
        };
    };
```


    // 按键设备
    gpio-keys {
        compatible = "gpio-keys";
        
        button-user {
            label = "User Button";
            gpios = <&gpio1 5 1>;  // GPIO_ACTIVE_LOW
            linux,code = <28>;     // KEY_ENTER
            debounce-interval = <50>;
        };
        
        button-reset {
            label = "Reset Button";
            gpios = <&gpio1 6 1>;
            linux,code = <116>;    // KEY_POWER
            debounce-interval = <50>;
        };
    };
};

// 配置UART1（调试串口）
&uart1 {
    status = "okay";
};

// 配置UART2（通信串口）
&uart2 {
    status = "okay";
    uart-has-rtscts;
};

// 配置I2C1
&i2c1 {
    clock-frequency = <400000>;  // 400kHz
    status = "okay";
    
    // EEPROM
    eeprom@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;
        pagesize = <64>;
    };
    
    // RTC
    rtc@68 {
        compatible = "dallas,ds1307";
        reg = <0x68>;
    };
    
    // 温度传感器
    temp-sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
        #thermal-sensor-cells = <0>;
    };
};

// 配置I2C2
&i2c2 {
    clock-frequency = <100000>;  // 100kHz
    status = "okay";
    
    // 加速度传感器
    accelerometer@1d {
        compatible = "st,lis3dh-accel";
        reg = <0x1d>;
        interrupt-parent = <&gpio2>;
        interrupts = <10 2>;  // IRQ_TYPE_EDGE_FALLING
    };
};
```


// 配置SPI1
&spi1 {
    cs-gpios = <&gpio1 16 0>;
    status = "okay";
    
    // SPI Flash
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
                reg = <0x000000 0x100000>;  // 1MB
                read-only;
            };
            
            partition@100000 {
                label = "kernel";
                reg = <0x100000 0x500000>;  // 5MB
            };
            
            partition@600000 {
                label = "rootfs";
                reg = <0x600000 0xa00000>;  // 10MB
            };
        };
    };
};

// 配置以太网
&ethernet {
    phy-mode = "rmii";
    phy-handle = <&ethphy0>;
    status = "okay";
    
    mdio {
        #address-cells = <1>;
        #size-cells = <0>;
        
        ethphy0: ethernet-phy@0 {
            compatible = "ethernet-phy-ieee802.3-c22";
            reg = <0>;
            max-speed = <100>;
        };
    };
};
```

保存此文件为 `my-board.dts`。


#### 5.4 编译和验证

**编译设备树**：
```bash
# 编译设备树
dtc -I dts -O dtb -o output/my-board.dtb my-board.dts

# 如果有警告，可以选择性忽略
dtc -I dts -O dtb -o output/my-board.dtb my-board.dts \
    -W no-unit_address_vs_reg

# 查看编译结果
ls -lh output/my-board.dtb
```

**反编译验证**：
```bash
# 反编译DTB查看结果
dtc -I dtb -O dts -o output/my-board-check.dts output/my-board.dtb

# 查看反编译的文件
less output/my-board-check.dts
```

**使用fdtdump查看结构**：
```bash
# 查看DTB的详细结构
fdtdump output/my-board.dtb

# 查看特定节点
fdtdump output/my-board.dtb | grep -A 10 "uart1"
```

### 6. 调试技巧

#### 6.1 编译时调试

**常见编译错误**：

1. **语法错误**
```bash
Error: my-board.dts:45.1-2 syntax error
FATAL ERROR: Unable to parse input tree
```

解决方法：检查第45行附近的语法，常见问题：
- 缺少分号
- 括号不匹配
- 引号不匹配

2. **引用错误**
```bash
Error: my-board.dts:60.15-20 Reference to non-existent node or label "gpio3"
```

解决方法：
- 检查标签是否正确定义
- 确认包含的dtsi文件中有该节点
- 检查标签名称拼写

3. **地址格式错误**
```bash
Warning: my-board.dts:30.5-15 node has a unit name, but no reg property
```

解决方法：
- 节点名有@地址，必须有reg属性
- 或者移除节点名中的@地址部分


**使用详细输出**：
```bash
# 显示所有警告
dtc -I dts -O dtb -o output/my-board.dtb my-board.dts -W all

# 将警告视为错误
dtc -I dts -O dtb -o output/my-board.dtb my-board.dts -W error

# 忽略特定警告
dtc -I dts -O dtb -o output/my-board.dtb my-board.dts \
    -W no-unit_address_vs_reg \
    -W no-simple_bus_reg
```

**预处理检查**：
```bash
# 查看预处理后的DTS（展开所有include）
cpp -nostdinc -I include -undef -x assembler-with-cpp \
    my-board.dts -o output/my-board-preprocessed.dts

# 查看预处理结果
less output/my-board-preprocessed.dts
```

#### 6.2 运行时调试

**查看设备树内容**：
```bash
# 查看设备树根节点
ls /proc/device-tree/

# 查看model属性
cat /proc/device-tree/model

# 查看compatible属性
cat /proc/device-tree/compatible

# 查看特定节点
ls /proc/device-tree/soc/serial@02020000/

# 查看节点属性
cat /proc/device-tree/soc/serial@02020000/status
hexdump -C /proc/device-tree/soc/serial@02020000/reg
```

**使用sysfs查看**：
```bash
# 查看设备树
cat /sys/firmware/devicetree/base/model

# 查看设备状态
cat /sys/firmware/devicetree/base/soc/serial@02020000/status
```

**查看设备匹配情况**：
```bash
# 查看平台设备
ls /sys/bus/platform/devices/

# 查看设备的compatible
cat /sys/bus/platform/devices/2020000.serial/modalias

# 查看驱动绑定情况
ls /sys/bus/platform/drivers/

# 查看特定驱动绑定的设备
ls /sys/bus/platform/drivers/imx-uart/
```


**内核日志调试**：
```bash
# 查看设备树相关日志
dmesg | grep -i "device tree"
dmesg | grep -i "of:"

# 查看设备probe日志
dmesg | grep -i "probe"

# 查看特定设备的日志
dmesg | grep "2020000.serial"

# 实时查看日志
dmesg -w
```

**使能设备树调试**：
```bash
# 在内核配置中使能
CONFIG_OF_DYNAMIC=y
CONFIG_OF_UNITTEST=y
CONFIG_DEBUG_DRIVER=y

# 动态调试
echo "file drivers/of/* +p" > /sys/kernel/debug/dynamic_debug/control
```

#### 6.3 常见问题排查

**问题1：设备未被识别**

症状：
```bash
dmesg | grep "2020000.serial"
# 没有输出
```

排查步骤：
```bash
# 1. 检查设备树中是否有该节点
ls /proc/device-tree/soc/serial@02020000/

# 2. 检查status属性
cat /proc/device-tree/soc/serial@02020000/status
# 应该输出: okay

# 3. 检查compatible属性
cat /proc/device-tree/soc/serial@02020000/compatible
# 应该有驱动支持的字符串

# 4. 检查是否有匹配的驱动
ls /sys/bus/platform/drivers/ | grep uart

# 5. 手动绑定设备到驱动
echo "2020000.serial" > /sys/bus/platform/drivers/imx-uart/bind
```

**问题2：设备probe失败**

症状：
```bash
dmesg | grep "2020000.serial"
# 输出: probe failed with error -22
```

排查步骤：
```bash
# 1. 检查reg属性是否正确
hexdump -C /proc/device-tree/soc/serial@02020000/reg

# 2. 检查中断配置
hexdump -C /proc/device-tree/soc/serial@02020000/interrupts

# 3. 检查时钟配置
cat /proc/device-tree/soc/serial@02020000/clock-names

# 4. 查看详细错误信息
dmesg | grep -A 5 "2020000.serial"
```


**问题3：GPIO引用错误**

症状：
```bash
dmesg | grep gpio
# 输出: Failed to get GPIO
```

排查步骤：
```bash
# 1. 检查GPIO控制器是否存在
ls /proc/device-tree/soc/gpio@0209c000/

# 2. 检查#gpio-cells
cat /proc/device-tree/soc/gpio@0209c000/#gpio-cells
# 应该输出: 2

# 3. 检查GPIO引用格式
# gpios = <&gpio1 3 0>;
# 参数1: GPIO控制器引用
# 参数2: GPIO引脚号
# 参数3: 标志位

# 4. 查看可用的GPIO
cat /sys/kernel/debug/gpio
```

**问题4：I2C设备未检测到**

症状：
```bash
i2cdetect -y 0
# 设备地址处显示 --
```

排查步骤：
```bash
# 1. 检查I2C总线是否存在
ls /dev/i2c-*

# 2. 检查I2C节点配置
cat /proc/device-tree/soc/i2c@021a0000/status

# 3. 检查设备地址
hexdump -C /proc/device-tree/soc/i2c@021a0000/eeprom@50/reg

# 4. 手动扫描I2C总线
i2cdetect -y 0

# 5. 尝试读取设备
i2cget -y 0 0x50 0x00
```

### 7. 最佳实践

#### 7.1 代码组织

**文件组织建议**：
```
dts/
├── include/
│   ├── vendor-soc.dtsi          # SoC通用配置
│   ├── vendor-soc-pinctrl.dtsi  # 引脚配置
│   └── vendor-soc-clocks.dtsi   # 时钟配置
├── boards/
│   ├── board-v1.dts             # 板子v1配置
│   ├── board-v2.dts             # 板子v2配置
│   └── board-common.dtsi        # 板子通用配置
└── overlays/
    ├── spi-flash.dts            # SPI Flash覆盖
    └── i2c-sensors.dts          # I2C传感器覆盖
```


**命名规范**：
```dts
// 好的命名
uart1: serial@02020000 { };
i2c_main: i2c@021a0000 { };
gpio_leds: leds { };

// 不好的命名
UART1: serial@02020000 { };      // 大写
i2c_1: i2c@021a0000 { };         // 数字分隔
node1: leds { };                 // 无意义名称
```

**注释规范**：
```dts
/ {
    model = "My Board v1.0";
    
    /* 
     * 内存配置
     * 板子使用1GB DDR3 RAM
     * 起始地址: 0x80000000
     */
    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;
    };
    
    // LED设备配置
    leds {
        compatible = "gpio-leds";
        
        led-status {
            label = "status";
            gpios = <&gpio1 3 0>;  // GPIO1_3, 低电平有效
            default-state = "on";
        };
    };
};
```

#### 7.2 属性配置建议

**使用宏定义**：
```dts
// 包含头文件
#include <dt-bindings/gpio/gpio.h>
#include <dt-bindings/interrupt-controller/irq.h>
#include <dt-bindings/clock/imx6ul-clock.h>

// 使用宏提高可读性
leds {
    led0 {
        gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;  // 而不是 <&gpio1 3 1>
    };
};

&uart1 {
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;  // 而不是 <0 26 4>
    clocks = <&clks IMX6UL_CLK_UART1_IPG>;          // 而不是 <&clks 100>
};
```

**属性顺序建议**：
```dts
uart1: serial@02020000 {
    // 1. compatible（最重要）
    compatible = "fsl,imx6ul-uart";
    
    // 2. reg
    reg = <0x02020000 0x4000>;
    
    // 3. interrupts
    interrupts = <GIC_SPI 26 IRQ_TYPE_LEVEL_HIGH>;
    
    // 4. clocks
    clocks = <&clks IMX6UL_CLK_UART1_IPG>,
             <&clks IMX6UL_CLK_UART1_SERIAL>;
    clock-names = "ipg", "per";
    
    // 5. 其他标准属性
    dmas = <&sdma 25 4 0>, <&sdma 26 4 0>;
    dma-names = "rx", "tx";
    
    // 6. 设备特定属性
    uart-has-rtscts;
    
    // 7. status（最后）
    status = "disabled";
};
```


#### 7.3 版本控制

**使用Git管理设备树**：
```bash
# 初始化仓库
git init

# 添加.gitignore
cat > .gitignore << EOF
output/
*.dtb
*.dtbo
*-preprocessed.dts
*-check.dts
EOF

# 提交初始版本
git add include/ boards/
git commit -m "Initial device tree for board v1.0"

# 创建分支用于新功能
git checkout -b feature/add-can-support

# 提交更改
git add boards/my-board.dts
git commit -m "Add CAN bus support"
```

**版本标记**：
```dts
/ {
    model = "My Board v1.0";
    compatible = "vendor,my-board-v1", "vendor,my-board", "vendor,soc";
    
    // 添加版本信息
    board-version = "1.0";
    board-revision = "A";
    build-date = "2024-01-15";
};
```

### 8. 进阶技巧

#### 8.1 条件编译

虽然设备树不直接支持条件编译，但可以通过C预处理器实现。

**使用预处理器宏**：
```dts
// 定义配置宏
#define ENABLE_UART2
#define ENABLE_SPI_FLASH

/ {
    model = "My Board";
    
#ifdef ENABLE_UART2
    // UART2配置
    &uart2 {
        status = "okay";
    };
#endif

#ifdef ENABLE_SPI_FLASH
    &spi1 {
        status = "okay";
        
        flash@0 {
            compatible = "jedec,spi-nor";
            reg = <0>;
        };
    };
#endif
};
```

**编译时指定宏**：
```bash
# 使用cpp预处理
cpp -DENABLE_UART2 -DENABLE_SPI_FLASH \
    -nostdinc -I include -undef -x assembler-with-cpp \
    my-board.dts -o output/my-board-preprocessed.dts

# 然后编译
dtc -I dts -O dtb -o output/my-board.dtb output/my-board-preprocessed.dts
```


#### 8.2 设备树验证脚本

创建自动化验证脚本。

**验证脚本示例**：
```bash
#!/bin/bash
# validate-dts.sh

DTS_FILE=$1
OUTPUT_DIR="output"

if [ -z "$DTS_FILE" ]; then
    echo "Usage: $0 <dts-file>"
    exit 1
fi

echo "=== Validating $DTS_FILE ==="

# 1. 编译检查
echo "Step 1: Compiling..."
dtc -I dts -O dtb -o $OUTPUT_DIR/temp.dtb $DTS_FILE 2>&1 | tee $OUTPUT_DIR/compile.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "ERROR: Compilation failed"
    exit 1
fi

echo "✓ Compilation successful"

# 2. 反编译验证
echo "Step 2: Decompiling..."
dtc -I dtb -O dts -o $OUTPUT_DIR/temp-check.dts $OUTPUT_DIR/temp.dtb

if [ $? -ne 0 ]; then
    echo "ERROR: Decompilation failed"
    exit 1
fi

echo "✓ Decompilation successful"

# 3. 检查必需节点
echo "Step 3: Checking required nodes..."
REQUIRED_NODES=("/" "/chosen" "/memory")

for node in "${REQUIRED_NODES[@]}"; do
    if ! grep -q "^${node}" $OUTPUT_DIR/temp-check.dts; then
        echo "ERROR: Missing required node: $node"
        exit 1
    fi
done

echo "✓ All required nodes present"

# 4. 检查compatible属性
echo "Step 4: Checking compatible properties..."
if ! grep -q "compatible" $OUTPUT_DIR/temp-check.dts; then
    echo "WARNING: No compatible properties found"
fi

echo "✓ Validation complete"

# 清理临时文件
rm -f $OUTPUT_DIR/temp.dtb $OUTPUT_DIR/temp-check.dts

echo "=== Validation passed ==="
```

**使用验证脚本**：
```bash
chmod +x validate-dts.sh
./validate-dts.sh my-board.dts
```


#### 8.3 设备树文档生成

从设备树生成文档。

**文档生成脚本**：
```bash
#!/bin/bash
# generate-dts-doc.sh

DTS_FILE=$1
OUTPUT_FILE="output/device-tree-doc.md"

echo "# Device Tree Documentation" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Generated from: $DTS_FILE" >> $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# 提取model
echo "## Board Information" >> $OUTPUT_FILE
MODEL=$(grep "model = " $DTS_FILE | sed 's/.*"\(.*\)".*/\1/')
echo "- Model: $MODEL" >> $OUTPUT_FILE

# 提取compatible
COMPAT=$(grep "compatible = " $DTS_FILE | head -1 | sed 's/.*"\(.*\)".*/\1/')
echo "- Compatible: $COMPAT" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# 提取内存配置
echo "## Memory Configuration" >> $OUTPUT_FILE
grep -A 2 "memory@" $DTS_FILE | grep "reg = " | \
    sed 's/.*<\(.*\)>.*/\1/' >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# 提取启用的设备
echo "## Enabled Devices" >> $OUTPUT_FILE
grep -B 5 'status = "okay"' $DTS_FILE | grep "^&" | \
    sed 's/&\(.*\) {/- \1/' >> $OUTPUT_FILE

echo "Documentation generated: $OUTPUT_FILE"
```

## 总结

本教程深入讲解了设备树的编写和调试技术，涵盖了：

1. **节点定义**：命名规范、标签使用、层次结构设计
2. **属性配置**：标准属性和自定义属性的正确使用
3. **引用关系**：Phandle机制和#cells属性的理解
4. **覆盖机制**：节点覆盖、属性修改、设备树overlay
5. **实践项目**：完整的板级设备树开发流程
6. **调试技巧**：编译时和运行时的问题排查方法
7. **最佳实践**：代码组织、命名规范、版本控制
8. **进阶技巧**：条件编译、自动化验证、文档生成

掌握这些技能后，你将能够：
- 独立编写和维护设备树文件
- 快速定位和解决设备树相关问题
- 为新硬件平台创建设备树配置
- 优化设备树的组织和可维护性


## 练习题

### 基础练习

1. **节点定义练习**
   - 创建一个包含UART、I2C和GPIO的简单设备树
   - 为每个节点添加适当的标签
   - 确保节点命名符合规范

2. **属性配置练习**
   - 为UART节点添加中断和时钟配置
   - 为I2C节点添加两个设备（EEPROM和传感器）
   - 为GPIO节点配置LED设备

3. **引用练习**
   - 创建一个时钟控制器节点
   - 让UART和I2C节点引用该时钟控制器
   - 使用GPIO控制LED

### 进阶练习

4. **覆盖练习**
   - 创建一个SoC dtsi文件，包含所有外设（默认禁用）
   - 创建一个板级dts文件，选择性启用需要的外设
   - 使用覆盖机制修改某些外设的配置

5. **调试练习**
   - 故意在设备树中引入几个错误
   - 使用dtc编译并分析错误信息
   - 修复所有错误并验证

6. **Overlay练习**
   - 创建一个设备树overlay，添加SPI Flash支持
   - 编译overlay文件
   - 编写脚本自动应用和移除overlay

### 综合项目

7. **完整板级设备树项目**
   - 为一个虚拟的嵌入式板子创建完整的设备树
   - 包含：CPU、内存、UART、I2C、SPI、GPIO、以太网
   - 添加LED、按键、传感器等外设
   - 编写验证脚本
   - 生成文档

## 延伸阅读

推荐进一步学习的资源：

- [板级支持包开发](02-bsp-development.html) - 完整的BSP开发流程
- [Linux设备驱动开发](../../02-device-driver-development/) - 驱动如何使用设备树
- [U-Boot设备树支持](../../01-bootloader-development/) - Bootloader中的设备树
- [Device Tree Specification](https://www.devicetree.org/) - 官方设备树规范
- [Linux Kernel Device Tree Documentation](https://www.kernel.org/doc/Documentation/devicetree/) - 内核文档

## 参考资料

1. Device Tree Specification v0.3 - devicetree.org
2. Linux Kernel Documentation - Device Tree Usage
3. Device Tree for Dummies - Thomas Petazzoni
4. Mastering Embedded Linux Programming - Device Tree Chapter
5. ARM Device Tree Bindings Documentation

---

**下一步**：建议学习 [板级支持包开发](02-bsp-development.html)，了解如何将设备树集成到完整的BSP中。

**实践建议**：
1. 从简单的设备树开始，逐步增加复杂度
2. 多使用调试工具，理解设备树的运行时行为
3. 参考Linux内核中的设备树示例
4. 建立自己的设备树模板库
5. 养成良好的代码组织和文档习惯

