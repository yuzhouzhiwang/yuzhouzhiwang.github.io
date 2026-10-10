---
title: "设备树(Device Tree)详解：硬件描述的标准语言"
description: "深入讲解设备树的概念、DTS语法规则、设备树编译过程、在Linux驱动中的使用方法以及调试技巧，帮助你掌握嵌入式Linux硬件描述的核心技术"
slug: "device-tree"

# 分类信息
domain: "操作系统层"
module: "嵌入式Linux"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 设备树
  - DTS
  - Linux驱动
  - 硬件描述
  - 设备树编译
  - DTB
prerequisites:
  - "03-operating-system-layer/05-embedded-linux/beginner/01-embedded-linux-overview"
  - "03-operating-system-layer/05-embedded-linux/beginner/02-kernel-configuration"
related_contents:
  - "03-operating-system-layer/05-embedded-linux/intermediate/01-linux-driver-basics"
  - "02-driver-bsp-layer/06-device-tree-bsp/beginner/01-device-tree-basics"

# 学习信息
estimated_time: 50
difficulty_score: 3

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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - 设备树
  - Device Tree
  - DTS语法
  - DTB文件
  - Linux设备树
  - 硬件描述
  - 设备树编译
  - 设备树调试
cover_image: ""
---

# 设备树(Device Tree)详解：硬件描述的标准语言


## 概述

设备树(Device Tree)是一种描述硬件资源的数据结构和语言，它将硬件配置信息从Linux内核代码中分离出来，使得同一个内核可以支持多种硬件平台。完成本文学习后，你将能够：

- [ ] 理解设备树的概念和作用
- [ ] 掌握DTS语法和基本结构
- [ ] 学会编译和反编译设备树
- [ ] 了解设备树在Linux驱动中的使用
- [ ] 掌握设备树的调试方法
- [ ] 能够编写简单的设备树节点

## 为什么需要设备树？

### 传统方式的问题

在设备树出现之前，Linux内核使用板级文件(Board File)来描述硬件信息：

```c
// 传统的板级文件方式（arch/arm/mach-xxx/board-xxx.c）
static struct resource led_resources[] = {
    {
        .start = 0x20200000,
        .end   = 0x20200FFF,
        .flags = IORESOURCE_MEM,
    },
};

static struct platform_device led_device = {
    .name = "gpio-led",
    .id   = -1,
    .num_resources = ARRAY_SIZE(led_resources),
    .resource = led_resources,
};

static void __init board_init(void) {
    platform_device_register(&led_device);
}
```

**存在的问题**：

1. **代码耦合严重**：硬件信息硬编码在内核中
2. **维护困难**：每个板子都需要单独的板级文件
3. **内核膨胀**：大量板级文件导致内核代码庞大
4. **移植复杂**：更换硬件需要修改和重新编译内核
5. **灵活性差**：无法动态适配不同硬件配置

### 设备树的优势

设备树通过将硬件描述从内核代码中分离，带来了诸多优势：

```
┌─────────────────────────────────────────┐
│         设备树源文件 (DTS)               │
│    人类可读的硬件描述文本                 │
└─────────────────────────────────────────┘
                    ↓ 编译
┌─────────────────────────────────────────┐
│      设备树二进制文件 (DTB)              │
│    机器可读的二进制格式                   │
└─────────────────────────────────────────┘
                    ↓ 加载
┌─────────────────────────────────────────┐
│         Linux内核                        │
│    解析设备树，创建设备节点               │
└─────────────────────────────────────────┘
```

**主要优势**：

| 优势 | 说明 |
|------|------|
| 代码分离 | 硬件描述与内核代码分离 |
| 易于维护 | 修改硬件配置无需重新编译内核 |
| 内核精简 | 移除大量板级文件代码 |
| 灵活性高 | 同一内核支持多种硬件配置 |
| 标准化 | 统一的硬件描述语言 |
| 可移植性 | 便于跨平台移植 |



## 设备树基本概念

### 设备树的组成

设备树由以下几个部分组成：

```
设备树文件系统
├── DTS (Device Tree Source)      # 设备树源文件，人类可读
├── DTSI (Device Tree Source Include) # 设备树头文件，可被包含
├── DTB (Device Tree Blob)        # 设备树二进制文件，机器可读
└── DTC (Device Tree Compiler)    # 设备树编译器
```

**文件类型说明**：

| 文件类型 | 扩展名 | 说明 | 示例 |
|---------|--------|------|------|
| 设备树源文件 | `.dts` | 描述特定板子的硬件 | `imx6ull-myboard.dts` |
| 设备树包含文件 | `.dtsi` | 描述SoC通用硬件 | `imx6ull.dtsi` |
| 设备树二进制 | `.dtb` | 编译后的二进制文件 | `imx6ull-myboard.dtb` |
| 设备树头文件 | `.h` | C语言头文件定义 | `dt-bindings/gpio/gpio.h` |

### 设备树的层次结构

设备树采用树形结构来描述硬件：

```
/ (根节点)
├── chosen (启动参数)
├── aliases (别名)
├── memory (内存信息)
├── cpus (CPU信息)
│   ├── cpu@0
│   └── cpu@1
├── soc (片上系统)
│   ├── uart1 (串口1)
│   ├── i2c1 (I2C总线1)
│   │   ├── sensor@48 (传感器设备)
│   │   └── eeprom@50 (EEPROM设备)
│   ├── spi1 (SPI总线1)
│   └── gpio (GPIO控制器)
└── leds (LED设备)
    ├── led1
    └── led2
```

### 节点和属性

设备树由节点(Node)和属性(Property)组成：

**节点**：表示一个设备或总线
```dts
node-name@unit-address {
    // 属性
};
```

**属性**：描述节点的特性
```dts
property-name = <value>;
property-name = "string";
property-name;  // 空属性（布尔值）
```



## DTS语法详解

### 基本语法规则

**1. 节点定义**

```dts
// 基本节点
node_name {
    property1 = <value>;
    property2 = "string";
};

// 带地址的节点
node_name@address {
    reg = <address size>;
};

// 节点标签（用于引用）
label: node_name@address {
    // 属性
};
```

**2. 属性类型**

```dts
// 空属性（布尔值）
property-name;

// 字符串
string-property = "hello";

// 32位无符号整数
int-property = <123>;

// 64位整数（两个32位值）
int64-property = <0x12345678 0x9abcdef0>;

// 字符串列表
string-list = "string1", "string2", "string3";

// 整数数组
int-array = <1 2 3 4 5>;

// 字节序列
byte-sequence = [01 02 03 04];

// 混合类型
mixed-property = "string", <0x12345678>, [01 02];

// 引用其他节点
phandle-property = <&label>;
```

**3. 数值表示**

```dts
// 十进制
decimal = <123>;

// 十六进制
hexadecimal = <0x7B>;

// 二进制（不常用）
binary = <0b1111011>;

// 大数值（64位）
large-value = <0x0 0x100000000>;  // 4GB
```

### 标准属性

**1. compatible属性**

用于驱动匹配，最重要的属性：

```dts
compatible = "manufacturer,model";

// 示例
compatible = "fsl,imx6ull-uart", "fsl,imx6q-uart";
// 优先匹配 "fsl,imx6ull-uart"
// 如果没有，则匹配 "fsl,imx6q-uart"
```

**2. reg属性**

描述设备的地址和大小：

```dts
// 格式：reg = <address size>;
reg = <0x02020000 0x4000>;  // 地址0x02020000，大小0x4000

// 多个地址范围
reg = <0x02020000 0x4000>,  // 第一个范围
      <0x02024000 0x4000>;  // 第二个范围
```

**3. #address-cells和#size-cells**

定义子节点地址的格式：

```dts
soc {
    #address-cells = <1>;  // 地址用1个32位值表示
    #size-cells = <1>;     // 大小用1个32位值表示
    
    uart1: serial@02020000 {
        reg = <0x02020000 0x4000>;  // 1个地址值，1个大小值
    };
};

// 64位地址示例
soc {
    #address-cells = <2>;  // 地址用2个32位值表示（64位）
    #size-cells = <2>;     // 大小用2个32位值表示（64位）
    
    memory@80000000 {
        reg = <0x0 0x80000000 0x0 0x40000000>;  // 1GB内存
    };
};
```

**4. status属性**

表示设备状态：

```dts
status = "okay";      // 设备可用
status = "disabled";  // 设备禁用
status = "fail";      // 设备故障
status = "fail-sss";  // 设备故障，sss是具体原因
```

**5. interrupts属性**

描述中断信息：

```dts
interrupts = <0 26 IRQ_TYPE_LEVEL_HIGH>;
// 参数1：中断类型（0=SPI, 1=PPI）
// 参数2：中断号
// 参数3：中断触发类型
```



### 完整的DTS示例

```dts
/dts-v1/;  // 版本声明

#include "imx6ull.dtsi"  // 包含SoC通用定义
#include <dt-bindings/gpio/gpio.h>  // 包含GPIO定义

/ {
    model = "MyBoard i.MX6ULL Board";
    compatible = "mycompany,imx6ull-myboard", "fsl,imx6ull";
    
    // 选择的启动参数
    chosen {
        bootargs = "console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw";
        stdout-path = &uart1;
    };
    
    // 内存信息
    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x20000000>;  // 512MB
    };
    
    // 别名
    aliases {
        serial0 = &uart1;
        i2c0 = &i2c1;
        spi0 = &ecspi1;
    };
    
    // 自定义LED设备
    leds {
        compatible = "gpio-leds";
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_leds>;
        
        led1 {
            label = "sys-led";
            gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
            default-state = "on";
            linux,default-trigger = "heartbeat";
        };
        
        led2 {
            label = "user-led";
            gpios = <&gpio1 4 GPIO_ACTIVE_LOW>;
            default-state = "off";
        };
    };
    
    // 自定义按键设备
    gpio-keys {
        compatible = "gpio-keys";
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_keys>;
        
        key1 {
            label = "User Button";
            gpios = <&gpio1 18 GPIO_ACTIVE_LOW>;
            linux,code = <KEY_ENTER>;
            gpio-key,wakeup;
        };
    };
};

// 修改UART1配置
&uart1 {
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_uart1>;
    status = "okay";
};

// 修改I2C1配置
&i2c1 {
    clock-frequency = <100000>;
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_i2c1>;
    status = "okay";
    
    // I2C设备：温度传感器
    temp_sensor: lm75@48 {
        compatible = "national,lm75";
        reg = <0x48>;
    };
    
    // I2C设备：EEPROM
    eeprom: at24c02@50 {
        compatible = "atmel,24c02";
        reg = <0x50>;
        pagesize = <8>;
    };
};

// 修改SPI1配置
&ecspi1 {
    fsl,spi-num-chipselects = <1>;
    cs-gpios = <&gpio4 26 GPIO_ACTIVE_LOW>;
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_ecspi1>;
    status = "okay";
    
    // SPI设备：Flash
    flash: m25p80@0 {
        compatible = "jedec,spi-nor";
        spi-max-frequency = <20000000>;
        reg = <0>;
    };
};

// GPIO引脚配置
&iomuxc {
    pinctrl_uart1: uart1grp {
        fsl,pins = <
            MX6UL_PAD_UART1_TX_DATA__UART1_DCE_TX 0x1b0b1
            MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1
        >;
    };
    
    pinctrl_i2c1: i2c1grp {
        fsl,pins = <
            MX6UL_PAD_UART4_TX_DATA__I2C1_SCL 0x4001b8b0
            MX6UL_PAD_UART4_RX_DATA__I2C1_SDA 0x4001b8b0
        >;
    };
    
    pinctrl_leds: ledsgrp {
        fsl,pins = <
            MX6UL_PAD_GPIO1_IO03__GPIO1_IO03 0x17059
            MX6UL_PAD_GPIO1_IO04__GPIO1_IO04 0x17059
        >;
    };
    
    pinctrl_keys: keysgrp {
        fsl,pins = <
            MX6UL_PAD_UART1_CTS_B__GPIO1_IO18 0x80000000
        >;
    };
};
```



## 设备树编译

### 编译工具：DTC

**设备树编译器(Device Tree Compiler, DTC)**用于将DTS文件编译成DTB文件。

**安装DTC**：

```bash
# Ubuntu/Debian
sudo apt install device-tree-compiler

# 验证安装
dtc --version
# 输出：Version: DTC 1.6.0
```

### 编译DTS到DTB

**基本编译命令**：

```bash
# 编译DTS为DTB
dtc -I dts -O dtb -o output.dtb input.dts

# 参数说明：
# -I dts：输入格式为DTS
# -O dtb：输出格式为DTB
# -o output.dtb：输出文件名
# input.dts：输入文件名
```

**包含头文件的编译**：

```bash
# 使用C预处理器处理包含文件
cpp -nostdinc -I include -undef -x assembler-with-cpp input.dts output.dts.tmp
dtc -I dts -O dtb -o output.dtb output.dts.tmp
rm output.dts.tmp

# 或使用内核Makefile
cd linux-5.15
make ARCH=arm dtbs
# 编译所有设备树文件
```

**在内核源码中编译**：

```bash
# 编译特定的DTB
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- imx6ull-myboard.dtb

# 编译所有DTB
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- dtbs

# 输出位置
ls arch/arm/boot/dts/*.dtb
```

### 反编译DTB到DTS

**反编译命令**：

```bash
# 反编译DTB为DTS
dtc -I dtb -O dts -o output.dts input.dtb

# 参数说明：
# -I dtb：输入格式为DTB
# -O dts：输出格式为DTS
# -o output.dts：输出文件名
# input.dtb：输入文件名
```

**从运行系统中提取设备树**：

```bash
# 方法1：从/proc读取
dtc -I fs -O dts -o current.dts /proc/device-tree

# 方法2：从/sys读取
cat /sys/firmware/devicetree/base/model
cat /sys/firmware/devicetree/base/compatible

# 方法3：使用fdtdump
fdtdump /boot/dtb/imx6ull-myboard.dtb
```

### 编译选项详解

**常用编译选项**：

```bash
# 显示警告信息
dtc -I dts -O dtb -W all -o output.dtb input.dts

# 抑制特定警告
dtc -I dts -O dtb -W no-unit_address_vs_reg -o output.dtb input.dts

# 生成符号信息（用于overlay）
dtc -I dts -O dtb -@ -o output.dtb input.dts

# 指定输出版本
dtc -I dts -O dtb -V 17 -o output.dtb input.dts

# 详细输出
dtc -I dts -O dtb -v -o output.dtb input.dts
```

**警告类型说明**：

| 警告类型 | 说明 |
|---------|------|
| `unit_address_vs_reg` | 节点名地址与reg属性不匹配 |
| `simple_bus_reg` | simple-bus节点包含reg属性 |
| `avoid_default_addr_size` | 使用默认的address-cells/size-cells |
| `obsolete_chosen_interrupt_controller` | 过时的chosen中断控制器 |



## 设备树在Linux中的使用

### 启动流程

设备树在Linux启动过程中的作用：

```
┌─────────────────────────────────────────┐
│         Bootloader (U-Boot)             │
│    加载内核和DTB到内存                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         内核启动                         │
│    解析DTB，构建设备树数据结构            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         平台设备注册                     │
│    根据设备树创建platform_device         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         驱动匹配                         │
│    通过compatible属性匹配驱动            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         设备初始化                       │
│    驱动probe函数被调用                   │
└─────────────────────────────────────────┘
```

### 在驱动中使用设备树

**1. 驱动匹配**

```c
// 定义设备树匹配表
static const struct of_device_id mydev_of_match[] = {
    { .compatible = "mycompany,mydevice" },
    { .compatible = "mycompany,mydevice-v2" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, mydev_of_match);

// 平台驱动结构
static struct platform_driver mydev_driver = {
    .driver = {
        .name = "mydevice",
        .of_match_table = mydev_of_match,
    },
    .probe = mydev_probe,
    .remove = mydev_remove,
};
```

**2. 读取属性**

```c
static int mydev_probe(struct platform_device *pdev)
{
    struct device_node *np = pdev->dev.of_node;
    const char *string_val;
    u32 int_val;
    int ret;
    
    // 读取字符串属性
    ret = of_property_read_string(np, "label", &string_val);
    if (ret == 0) {
        dev_info(&pdev->dev, "Label: %s\n", string_val);
    }
    
    // 读取整数属性
    ret = of_property_read_u32(np, "clock-frequency", &int_val);
    if (ret == 0) {
        dev_info(&pdev->dev, "Clock: %u Hz\n", int_val);
    }
    
    // 检查属性是否存在
    if (of_property_read_bool(np, "enable-dma")) {
        dev_info(&pdev->dev, "DMA enabled\n");
    }
    
    return 0;
}
```

**3. 获取资源**

```c
static int mydev_probe(struct platform_device *pdev)
{
    struct resource *res;
    void __iomem *base;
    int irq;
    
    // 获取内存资源
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    if (!res) {
        dev_err(&pdev->dev, "Failed to get memory resource\n");
        return -ENODEV;
    }
    
    // 映射内存
    base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(base)) {
        return PTR_ERR(base);
    }
    
    // 获取中断号
    irq = platform_get_irq(pdev, 0);
    if (irq < 0) {
        dev_err(&pdev->dev, "Failed to get IRQ\n");
        return irq;
    }
    
    dev_info(&pdev->dev, "Base: 0x%px, IRQ: %d\n", base, irq);
    
    return 0;
}
```

**4. 解析GPIO**

```c
#include <linux/gpio/consumer.h>

static int mydev_probe(struct platform_device *pdev)
{
    struct gpio_desc *gpio;
    
    // 获取GPIO描述符
    gpio = devm_gpiod_get(&pdev->dev, "reset", GPIOD_OUT_LOW);
    if (IS_ERR(gpio)) {
        dev_err(&pdev->dev, "Failed to get reset GPIO\n");
        return PTR_ERR(gpio);
    }
    
    // 设置GPIO值
    gpiod_set_value(gpio, 1);  // 拉高
    msleep(10);
    gpiod_set_value(gpio, 0);  // 拉低
    
    return 0;
}
```

**5. 解析时钟**

```c
#include <linux/clk.h>

static int mydev_probe(struct platform_device *pdev)
{
    struct clk *clk;
    unsigned long rate;
    
    // 获取时钟
    clk = devm_clk_get(&pdev->dev, "ipg");
    if (IS_ERR(clk)) {
        dev_err(&pdev->dev, "Failed to get clock\n");
        return PTR_ERR(clk);
    }
    
    // 使能时钟
    clk_prepare_enable(clk);
    
    // 获取时钟频率
    rate = clk_get_rate(clk);
    dev_info(&pdev->dev, "Clock rate: %lu Hz\n", rate);
    
    return 0;
}
```



### 常用OF函数

**节点操作函数**：

```c
// 通过路径查找节点
struct device_node *of_find_node_by_path(const char *path);

// 通过名称查找节点
struct device_node *of_find_node_by_name(struct device_node *from, const char *name);

// 通过compatible查找节点
struct device_node *of_find_compatible_node(struct device_node *from,
                                            const char *type,
                                            const char *compatible);

// 通过phandle查找节点
struct device_node *of_find_node_by_phandle(phandle handle);

// 获取父节点
struct device_node *of_get_parent(const struct device_node *node);

// 获取子节点
struct device_node *of_get_next_child(const struct device_node *node,
                                      struct device_node *prev);
```

**属性读取函数**：

```c
// 读取字符串
int of_property_read_string(const struct device_node *np,
                            const char *propname,
                            const char **out_string);

// 读取u32整数
int of_property_read_u32(const struct device_node *np,
                         const char *propname,
                         u32 *out_value);

// 读取u32数组
int of_property_read_u32_array(const struct device_node *np,
                               const char *propname,
                               u32 *out_values,
                               size_t sz);

// 读取u64整数
int of_property_read_u64(const struct device_node *np,
                         const char *propname,
                         u64 *out_value);

// 检查属性是否存在
bool of_property_read_bool(const struct device_node *np,
                          const char *propname);

// 获取属性长度
int of_property_count_elems_of_size(const struct device_node *np,
                                    const char *propname,
                                    int elem_size);
```

**资源获取函数**：

```c
// 获取地址和大小
int of_address_to_resource(struct device_node *dev,
                          int index,
                          struct resource *r);

// 获取中断号
int of_irq_get(struct device_node *dev, int index);

// 解析phandle
struct device_node *of_parse_phandle(const struct device_node *np,
                                     const char *phandle_name,
                                     int index);
```



## 设备树调试方法

### 查看运行时设备树

**1. 通过/proc查看**

```bash
# 查看设备树根节点
ls /proc/device-tree/

# 查看model信息
cat /proc/device-tree/model

# 查看compatible信息
cat /proc/device-tree/compatible

# 查看特定节点
ls /proc/device-tree/soc/
cat /proc/device-tree/soc/uart@02020000/status
```

**2. 通过/sys查看**

```bash
# 查看设备树基础信息
ls /sys/firmware/devicetree/base/

# 查看model
cat /sys/firmware/devicetree/base/model

# 查看所有compatible
find /sys/firmware/devicetree/base -name compatible -exec cat {} \;
```

**3. 导出完整设备树**

```bash
# 方法1：使用dtc
dtc -I fs -O dts -o /tmp/current.dts /proc/device-tree

# 方法2：从内存导出
cat /sys/firmware/fdt > /tmp/current.dtb
dtc -I dtb -O dts -o /tmp/current.dts /tmp/current.dtb

# 查看导出的设备树
less /tmp/current.dts
```

### 调试技巧

**1. 检查设备树是否加载**

```bash
# 查看内核启动日志
dmesg | grep -i "device tree"
dmesg | grep -i "dtb"

# 输出示例：
# [    0.000000] Machine model: MyBoard i.MX6ULL Board
# [    0.000000] OF: fdt: Machine model: MyBoard i.MX6ULL Board
```

**2. 检查设备是否创建**

```bash
# 查看平台设备
ls /sys/bus/platform/devices/

# 查看特定设备
ls /sys/bus/platform/devices/2020000.serial/

# 查看设备的设备树节点
cat /sys/bus/platform/devices/2020000.serial/of_node/compatible
```

**3. 检查驱动是否匹配**

```bash
# 查看已加载的驱动
ls /sys/bus/platform/drivers/

# 查看驱动绑定的设备
ls /sys/bus/platform/drivers/imx-uart/

# 查看设备的驱动
readlink /sys/bus/platform/devices/2020000.serial/driver
```

**4. 使用内核调试选项**

```bash
# 在内核配置中启用
Device Drivers  --->
    Generic Driver Options  --->
        [*] Driver Core verbose debug messages

# 或在启动参数中添加
console=ttyS0,115200 debug

# 查看详细日志
dmesg | grep "of_platform"
dmesg | grep "compatible"
```

**5. 编写测试代码**

```c
// 测试设备树节点是否存在
static int __init test_dt_init(void)
{
    struct device_node *np;
    
    np = of_find_node_by_path("/leds/led1");
    if (np) {
        pr_info("Found LED1 node\n");
        of_node_put(np);
    } else {
        pr_err("LED1 node not found\n");
    }
    
    return 0;
}
module_init(test_dt_init);
```

### 常见错误排查

**错误1：设备树未加载**

```bash
症状：
- /proc/device-tree目录不存在
- dmesg中没有设备树相关信息

原因：
- DTB文件未传递给内核
- Bootloader配置错误

解决方案：
# 检查U-Boot配置
printenv
# 确保fdt_addr或fdt_file正确设置

# 手动加载DTB
fatload mmc 0:1 ${fdt_addr} imx6ull-myboard.dtb
bootz ${kernel_addr} - ${fdt_addr}
```

**错误2：设备未创建**

```bash
症状：
- /sys/bus/platform/devices/中没有对应设备

原因：
- compatible属性错误
- status = "disabled"
- 节点格式错误

解决方案：
# 检查设备树节点
cat /proc/device-tree/soc/uart@02020000/compatible
cat /proc/device-tree/soc/uart@02020000/status

# 确保status为"okay"
&uart1 {
    status = "okay";
};
```

**错误3：驱动未匹配**

```bash
症状：
- 设备存在但没有驱动

原因：
- compatible字符串不匹配
- 驱动未编译或加载

解决方案：
# 检查驱动的compatible
grep -r "mycompany,mydevice" drivers/

# 确保驱动已加载
lsmod | grep mydriver
modprobe mydriver

# 检查驱动匹配表
cat /sys/bus/platform/drivers/mydriver/uevent
```

**错误4：属性读取失败**

```bash
症状：
- of_property_read_xxx返回错误

原因：
- 属性名称错误
- 属性类型不匹配
- 属性不存在

解决方案：
# 检查属性是否存在
ls /proc/device-tree/path/to/node/

# 查看属性值
hexdump -C /proc/device-tree/path/to/node/property-name

# 确保属性格式正确
property-name = <0x12345678>;  // u32
property-name = "string";      // string
```



## 设备树Overlay

### Overlay概念

设备树Overlay允许在运行时动态修改设备树，无需重新编译和加载整个DTB。

**应用场景**：
- 动态添加/移除设备
- 支持可插拔硬件
- 开发板扩展模块
- 运行时配置修改

### Overlay语法

```dts
/dts-v1/;
/plugin/;  // 声明为overlay

/ {
    compatible = "mycompany,imx6ull-myboard";
    
    fragment@0 {
        target = <&i2c1>;  // 目标节点
        __overlay__ {
            // 要添加或修改的内容
            sensor@48 {
                compatible = "ti,tmp102";
                reg = <0x48>;
            };
        };
    };
    
    fragment@1 {
        target-path = "/";  // 使用路径指定目标
        __overlay__ {
            new_device {
                compatible = "mycompany,newdev";
                status = "okay";
            };
        };
    };
};
```

### 编译Overlay

```bash
# 编译overlay（需要符号支持）
dtc -@ -I dts -O dtb -o overlay.dtbo overlay.dts

# 基础DTB也需要符号支持
dtc -@ -I dts -O dtb -o base.dtb base.dts
```

### 应用Overlay

**方法1：使用configfs**

```bash
# 挂载configfs
mount -t configfs none /sys/kernel/config

# 创建overlay目录
mkdir /sys/kernel/config/device-tree/overlays/my_overlay

# 应用overlay
cat overlay.dtbo > /sys/kernel/config/device-tree/overlays/my_overlay/dtbo

# 检查状态
cat /sys/kernel/config/device-tree/overlays/my_overlay/status

# 移除overlay
rmdir /sys/kernel/config/device-tree/overlays/my_overlay
```

**方法2：使用U-Boot**

```bash
# 在U-Boot中加载overlay
fatload mmc 0:1 ${fdt_addr} base.dtb
fatload mmc 0:1 ${overlay_addr} overlay.dtbo
fdt addr ${fdt_addr}
fdt resize 8192
fdt apply ${overlay_addr}
bootz ${kernel_addr} - ${fdt_addr}
```



## 实战示例

### 示例1：添加LED设备

**设备树配置**：

```dts
/ {
    leds {
        compatible = "gpio-leds";
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_leds>;
        
        led_red {
            label = "red";
            gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
            default-state = "off";
        };
        
        led_green {
            label = "green";
            gpios = <&gpio1 4 GPIO_ACTIVE_LOW>;
            default-state = "off";
            linux,default-trigger = "heartbeat";
        };
    };
};

&iomuxc {
    pinctrl_leds: ledsgrp {
        fsl,pins = <
            MX6UL_PAD_GPIO1_IO03__GPIO1_IO03 0x17059
            MX6UL_PAD_GPIO1_IO04__GPIO1_IO04 0x17059
        >;
    };
};
```

**测试LED**：

```bash
# 查看LED设备
ls /sys/class/leds/

# 控制LED
echo 1 > /sys/class/leds/red/brightness
echo 0 > /sys/class/leds/red/brightness

# 设置触发器
echo timer > /sys/class/leds/green/trigger
echo 100 > /sys/class/leds/green/delay_on
echo 100 > /sys/class/leds/green/delay_off
```

### 示例2：添加I2C设备

**设备树配置**：

```dts
&i2c1 {
    clock-frequency = <100000>;
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_i2c1>;
    status = "okay";
    
    // 温度传感器
    temp_sensor: lm75@48 {
        compatible = "national,lm75";
        reg = <0x48>;
    };
    
    // RTC
    rtc: ds1307@68 {
        compatible = "dallas,ds1307";
        reg = <0x68>;
    };
    
    // EEPROM
    eeprom: at24c256@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;
        pagesize = <64>;
    };
};

&iomuxc {
    pinctrl_i2c1: i2c1grp {
        fsl,pins = <
            MX6UL_PAD_UART4_TX_DATA__I2C1_SCL 0x4001b8b0
            MX6UL_PAD_UART4_RX_DATA__I2C1_SDA 0x4001b8b0
        >;
    };
};
```

**测试I2C设备**：

```bash
# 扫描I2C总线
i2cdetect -y 1

# 读取温度传感器
cat /sys/class/hwmon/hwmon0/temp1_input

# 读取RTC时间
hwclock -r

# 读写EEPROM
echo "Hello" > /sys/bus/i2c/devices/1-0050/eeprom
hexdump -C /sys/bus/i2c/devices/1-0050/eeprom | head
```

### 示例3：添加SPI设备

**设备树配置**：

```dts
&ecspi1 {
    fsl,spi-num-chipselects = <2>;
    cs-gpios = <&gpio4 26 GPIO_ACTIVE_LOW>,
               <&gpio4 27 GPIO_ACTIVE_LOW>;
    pinctrl-names = "default";
    pinctrl-0 = <&pinctrl_ecspi1>;
    status = "okay";
    
    // SPI Flash
    flash: m25p80@0 {
        compatible = "jedec,spi-nor";
        spi-max-frequency = <20000000>;
        reg = <0>;
        
        partitions {
            compatible = "fixed-partitions";
            #address-cells = <1>;
            #size-cells = <1>;
            
            partition@0 {
                label = "bootloader";
                reg = <0x0 0x100000>;
                read-only;
            };
            
            partition@100000 {
                label = "kernel";
                reg = <0x100000 0x400000>;
            };
            
            partition@500000 {
                label = "rootfs";
                reg = <0x500000 0xb00000>;
            };
        };
    };
    
    // SPI设备
    spidev@1 {
        compatible = "rohm,dh2228fv";
        spi-max-frequency = <1000000>;
        reg = <1>;
    };
};

&iomuxc {
    pinctrl_ecspi1: ecspi1grp {
        fsl,pins = <
            MX6UL_PAD_CSI_DATA07__ECSPI1_MISO 0x100b1
            MX6UL_PAD_CSI_DATA06__ECSPI1_MOSI 0x100b1
            MX6UL_PAD_CSI_DATA04__ECSPI1_SCLK 0x100b1
            MX6UL_PAD_CSI_DATA05__GPIO4_IO26  0x100b1
            MX6UL_PAD_CSI_DATA08__GPIO4_IO27  0x100b1
        >;
    };
};
```

**测试SPI设备**：

```bash
# 查看SPI设备
ls /dev/spidev*

# 查看Flash分区
cat /proc/mtd

# 读取Flash
dd if=/dev/mtd0 of=/tmp/bootloader.bin bs=1M count=1

# 使用spidev
# 需要编写用户空间程序或使用spidev工具
```



## 最佳实践

### 1. 设备树组织

**分层结构**：

```
arch/arm/boot/dts/
├── imx6ull.dtsi              # SoC通用定义
├── imx6ull-14x14-evk.dtsi    # EVK板通用定义
├── imx6ull-14x14-evk.dts     # EVK板具体配置
└── imx6ull-myboard.dts       # 自定义板配置
```

**包含关系**：

```dts
// imx6ull-myboard.dts
#include "imx6ull.dtsi"
#include "imx6ull-14x14-evk.dtsi"

/ {
    model = "MyBoard i.MX6ULL";
    compatible = "mycompany,imx6ull-myboard", "fsl,imx6ull";
    
    // 板级特定配置
};
```

### 2. 命名规范

**节点命名**：

```dts
// 格式：device-type@unit-address
uart1: serial@02020000 { };
i2c1: i2c@021a0000 { };
gpio1: gpio@0209c000 { };

// 不带地址的节点
leds { };
gpio-keys { };
regulators { };
```

**属性命名**：

```dts
// 使用小写和连字符
compatible = "vendor,device";
clock-frequency = <100000>;
pinctrl-names = "default";

// 避免使用下划线或驼峰命名
// 错误：clockFrequency, clock_frequency
```

**标签命名**：

```dts
// 使用有意义的标签
uart1: serial@02020000 { };
temp_sensor: lm75@48 { };
led_red: led@0 { };

// 避免使用无意义的标签
// 错误：node1, dev2, label3
```

### 3. 文档化

**添加注释**：

```dts
/ {
    model = "MyBoard i.MX6ULL Board";
    compatible = "mycompany,imx6ull-myboard", "fsl,imx6ull";
    
    /*
     * LED配置
     * - led_red: GPIO1_IO03, 低电平有效
     * - led_green: GPIO1_IO04, 低电平有效，心跳触发
     */
    leds {
        compatible = "gpio-leds";
        
        led_red {
            label = "red";
            gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
            default-state = "off";
        };
    };
};
```

**创建绑定文档**：

```yaml
# Documentation/devicetree/bindings/leds/mycompany-leds.yaml
%YAML 1.2
---
$id: http://devicetree.org/schemas/leds/mycompany-leds.yaml#
$schema: http://devicetree.org/meta-schemas/core.yaml#

title: MyCompany LED Controller

maintainers:
  - Your Name <your.email@example.com>

properties:
  compatible:
    const: mycompany,led-controller

  reg:
    maxItems: 1

  num-leds:
    description: Number of LEDs
    $ref: /schemas/types.yaml#/definitions/uint32

required:
  - compatible
  - reg

examples:
  - |
    leds@40000000 {
        compatible = "mycompany,led-controller";
        reg = <0x40000000 0x1000>;
        num-leds = <4>;
    };
```

### 4. 版本控制

**使用Git管理**：

```bash
# 提交设备树修改
git add arch/arm/boot/dts/imx6ull-myboard.dts
git commit -m "ARM: dts: imx6ull: Add support for MyBoard"

# 查看历史
git log -- arch/arm/boot/dts/imx6ull-myboard.dts

# 比较版本
git diff v1.0..v2.0 arch/arm/boot/dts/imx6ull-myboard.dts
```

**版本标记**：

```dts
/ {
    model = "MyBoard i.MX6ULL Board v2.0";
    compatible = "mycompany,imx6ull-myboard-v2", 
                 "mycompany,imx6ull-myboard",
                 "fsl,imx6ull";
    
    // 硬件版本信息
    hardware {
        revision = "2.0";
        date = "2024-01-15";
    };
};
```

### 5. 测试验证

**编译检查**：

```bash
# 编译设备树
make ARCH=arm dtbs

# 检查警告
make ARCH=arm W=1 dtbs

# 使用dtc检查
dtc -I dts -O dtb -W all -o /dev/null myboard.dts
```

**运行时验证**：

```bash
# 检查设备树加载
dmesg | grep "OF:"
dmesg | grep "device tree"

# 验证设备创建
ls /sys/bus/platform/devices/

# 验证驱动匹配
ls /sys/bus/platform/drivers/

# 导出并检查
dtc -I fs -O dts -o /tmp/current.dts /proc/device-tree
diff -u original.dts /tmp/current.dts
```



## 常见问题

### Q1: 设备树和ACPI有什么区别？

**A**: 设备树(Device Tree)和ACPI(Advanced Configuration and Power Interface)都是硬件描述机制，但有不同的应用场景：

| 特性 | 设备树 | ACPI |
|------|--------|------|
| 主要平台 | ARM、PowerPC、RISC-V | x86、x86_64 |
| 复杂度 | 相对简单 | 复杂 |
| 动态性 | 静态描述 | 支持动态配置 |
| 电源管理 | 基础支持 | 完整的电源管理 |
| 热插拔 | 有限支持 | 完整支持 |
| 文件格式 | 文本+二进制 | 二进制表格 |

**选择建议**：
- 嵌入式ARM系统：使用设备树
- x86服务器/PC：使用ACPI
- ARM服务器：可能同时支持两者

### Q2: 为什么修改设备树后设备没有变化？

**A**: 可能的原因和解决方案：

1. **DTB未更新**
```bash
# 确保重新编译DTB
make ARCH=arm dtbs

# 确保复制到正确位置
cp arch/arm/boot/dts/myboard.dtb /boot/
```

2. **Bootloader未加载新DTB**
```bash
# 检查U-Boot配置
printenv fdt_file
printenv fdt_addr

# 确保加载正确的DTB
setenv fdt_file myboard.dtb
saveenv
```

3. **设备状态为disabled**
```dts
&uart1 {
    status = "okay";  // 确保是okay而不是disabled
};
```

4. **驱动未加载**
```bash
# 检查驱动是否存在
lsmod | grep driver_name

# 加载驱动
modprobe driver_name
```

### Q3: 如何在设备树中引用其他节点？

**A**: 使用phandle和标签：

```dts
// 方法1：使用标签引用
gpio1: gpio@0209c000 {
    // GPIO控制器定义
};

leds {
    led1 {
        gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;  // 引用gpio1
    };
};

// 方法2：使用phandle
/ {
    gpio-controller {
        phandle = <0x10>;
    };
    
    leds {
        led1 {
            gpios = <0x10 3 0>;  // 使用phandle值
        };
    };
};

// 方法3：使用路径
leds {
    led1 {
        gpio-controller = <&{/soc/gpio@0209c000}>;
    };
};
```

### Q4: 设备树中的地址如何确定？

**A**: 地址来源于硬件手册：

```dts
// 1. 查看芯片手册的Memory Map章节
// 例如：i.MX6ULL参考手册
// UART1: 0x02020000 - 0x02023FFF (16KB)

uart1: serial@02020000 {
    compatible = "fsl,imx6ul-uart";
    reg = <0x02020000 0x4000>;  // 地址和大小
};

// 2. 对于I2C/SPI设备，地址是设备地址
i2c1 {
    #address-cells = <1>;
    #size-cells = <0>;
    
    sensor@48 {  // I2C地址0x48
        compatible = "ti,tmp102";
        reg = <0x48>;
    };
};
```

### Q5: 如何调试设备树匹配问题？

**A**: 使用以下方法：

```bash
# 1. 检查compatible字符串
cat /proc/device-tree/path/to/node/compatible

# 2. 查看驱动的匹配表
grep -r "compatible_string" drivers/

# 3. 启用调试信息
echo 8 > /proc/sys/kernel/printk
dmesg -w

# 4. 检查设备和驱动
ls /sys/bus/platform/devices/
ls /sys/bus/platform/drivers/

# 5. 手动绑定驱动
echo "device_name" > /sys/bus/platform/drivers/driver_name/bind
```

### Q6: 设备树可以在运行时修改吗？

**A**: 有限支持，主要通过Overlay：

```bash
# 使用configfs动态加载overlay
mount -t configfs none /sys/kernel/config
mkdir /sys/kernel/config/device-tree/overlays/test
cat overlay.dtbo > /sys/kernel/config/device-tree/overlays/test/dtbo

# 但不能修改已存在的节点的某些属性
# 只能添加新节点或修改特定属性
```

**限制**：
- 不能删除已存在的节点
- 不能修改某些关键属性
- 需要内核支持CONFIG_OF_OVERLAY
- 基础DTB需要编译时包含符号信息(-@选项)



## 总结

通过本文的学习，你应该已经掌握了设备树的核心知识：

### 核心要点

1. **设备树的作用**
   - 将硬件描述从内核代码中分离
   - 提供统一的硬件描述语言
   - 支持一个内核适配多种硬件

2. **DTS语法**
   - 节点和属性的基本结构
   - 标准属性的使用方法
   - 节点引用和phandle机制

3. **设备树编译**
   - 使用dtc编译DTS到DTB
   - 反编译DTB查看内容
   - 在内核中编译设备树

4. **驱动中使用**
   - 通过compatible匹配驱动
   - 使用OF函数读取属性
   - 获取资源和GPIO

5. **调试方法**
   - 通过/proc和/sys查看设备树
   - 检查设备和驱动匹配
   - 排查常见问题

### 学习建议

**对于初学者**：
1. 从简单的LED、按键设备开始
2. 理解节点和属性的基本概念
3. 学会查看和修改现有设备树
4. 掌握基本的调试方法

**对于进阶开发者**：
1. 深入理解设备树绑定规范
2. 学习编写设备树文档
3. 掌握Overlay的使用
4. 了解设备树在内核中的实现

**对于驱动开发者**：
1. 熟练使用OF函数API
2. 理解设备树与驱动的匹配机制
3. 掌握资源获取方法
4. 学会编写设备树绑定文档

### 关键技能清单

完成本文学习后，你应该能够：

- [x] 理解设备树的概念和作用
- [x] 阅读和理解DTS文件
- [x] 编写简单的设备树节点
- [x] 编译和反编译设备树
- [x] 在驱动中使用设备树
- [x] 调试设备树相关问题
- [x] 使用设备树Overlay

## 延伸阅读

### 推荐学习路径

1. **Linux驱动开发**
   - [Linux驱动开发入门](../intermediate/01-linux-driver-basics.html)
   - 学习如何在驱动中使用设备树
   - 理解平台设备驱动框架

2. **BSP开发**
   - [设备树编写实战](../../../02-driver-bsp-layer/06-device-tree-bsp/intermediate/01-device-tree-writing.html)
   - 深入学习设备树编写技巧
   - 掌握复杂设备的描述方法

3. **内核移植**
   - [嵌入式Linux完整系统构建](../advanced/01-complete-linux-system.html)
   - 学习完整的系统移植流程
   - 理解设备树在系统中的位置

### 相关文档

**官方文档**：

1. **Linux内核设备树文档**
   - Documentation/devicetree/
   - Documentation/devicetree/bindings/
   - https://www.kernel.org/doc/Documentation/devicetree/

2. **设备树规范**
   - https://www.devicetree.org/
   - Device Tree Specification
   - ePAPR (Embedded Power Architecture Platform Requirements)

3. **内核源码**
   - drivers/of/ - OF核心代码
   - include/linux/of*.h - OF头文件
   - arch/arm/boot/dts/ - ARM设备树

**推荐书籍**：

1. **《Linux设备驱动程序》**
   - 第14章：Linux设备模型
   - 设备树相关内容

2. **《嵌入式Linux系统开发》**
   - 设备树章节
   - 实战案例

3. **《ARM Linux内核源码剖析》**
   - 设备树解析过程
   - 内核实现细节

**在线资源**：

1. **Bootlin培训材料**
   - https://bootlin.com/docs/
   - 免费的设备树教程

2. **eLinux.org**
   - https://elinux.org/Device_Tree
   - 设备树Wiki和示例

3. **内核邮件列表**
   - https://lkml.org/
   - 设备树相关讨论

### 实践项目建议

1. **基础项目**
   - 为自己的开发板编写设备树
   - 添加LED、按键等简单设备
   - 测试I2C、SPI设备

2. **进阶项目**
   - 编写设备树Overlay
   - 支持可插拔扩展模块
   - 实现运行时配置

3. **高级项目**
   - 移植新的SoC设备树
   - 编写设备树绑定文档
   - 贡献设备树到内核主线

## 参考资料

1. **Device Tree Specification v0.3** - devicetree.org
2. **Linux Kernel Documentation: Device Tree** - kernel.org
3. **ePAPR v1.1** - Power.org
4. **ARM Linux Device Tree** - ARM官方文档
5. **i.MX6ULL Reference Manual** - NXP
6. **Bootlin Device Tree Training** - bootlin.com

---

**练习题**：

1. 编写一个设备树节点，描述一个连接到I2C总线的温度传感器
2. 修改现有设备树，添加一个GPIO控制的LED
3. 编译设备树并在QEMU中测试
4. 编写一个简单的驱动，从设备树中读取配置信息
5. 创建一个设备树Overlay，动态添加一个SPI设备

**下一步**：建议学习 [Linux驱动开发入门](../intermediate/01-linux-driver-basics.html)，深入了解如何在驱动中使用设备树。
