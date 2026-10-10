---
title: "Linux驱动开发入门：从零开始编写字符设备驱动"
description: "深入讲解Linux驱动框架、字符设备驱动开发、模块编程、设备文件操作和驱动调试技巧，帮助你掌握嵌入式Linux驱动开发的核心技能"
slug: "linux-driver-basics"

# 分类信息
domain: "操作系统层"
module: "嵌入式Linux"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Linux驱动
  - 驱动开发
  - 字符设备
  - 内核模块
  - 设备文件
  - 驱动调试
prerequisites:
  - "03-operating-system-layer/05-embedded-linux/beginner/01-embedded-linux-overview"
  - "03-operating-system-layer/05-embedded-linux/beginner/02-kernel-configuration"
  - "03-operating-system-layer/05-embedded-linux/beginner/03-device-tree"
related_contents:
  - "03-operating-system-layer/05-embedded-linux/intermediate/02-rootfs"
  - "02-driver-bsp-layer/01-gpio-driver/beginner/01-gpio-basics"

# 学习信息
estimated_time: 100
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
is_featured: true
is_premium: false

# SEO和元数据
keywords:
  - Linux驱动开发
  - 字符设备驱动
  - 内核模块编程
  - 设备文件操作
  - 驱动调试
  - file_operations
  - cdev
cover_image: ""
---

# Linux驱动开发入门：从零开始编写字符设备驱动


## 学习目标

完成本教程后,你将能够：

- [ ] 理解Linux驱动框架和设备模型
- [ ] 掌握内核模块的编写和编译
- [ ] 独立开发字符设备驱动程序
- [ ] 实现设备文件的基本操作（open、read、write、ioctl）
- [ ] 使用设备树配置驱动
- [ ] 掌握驱动调试的常用方法
- [ ] 理解用户空间与内核空间的交互
- [ ] 处理并发和同步问题

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟练掌握C语言编程
- 了解Linux系统编程基础
- 理解进程、文件系统等操作系统概念
- 掌握指针、结构体等高级C语言特性
- 了解设备树基本概念

**技能要求**：
- 能够编译和加载Linux内核
- 会使用Makefile构建项目
- 熟悉Linux命令行操作
- 了解交叉编译流程

**硬件和软件准备**：
- Linux开发主机（Ubuntu 20.04+推荐）
- 目标开发板或QEMU模拟器
- 交叉编译工具链
- 内核源码（与目标系统版本匹配）
- 串口调试工具

## Linux驱动框架概述

### 驱动在系统中的位置

Linux驱动程序是连接硬件和应用程序的桥梁：

```
┌─────────────────────────────────────────┐
│         用户空间 (User Space)            │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │ 应用程序1 │  │ 应用程序2 │           │
│  └──────────┘  └──────────┘           │
└─────────────────────────────────────────┘
         ↕ 系统调用 (System Call)
┌─────────────────────────────────────────┐
│         内核空间 (Kernel Space)          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    虚拟文件系统 (VFS)             │  │
│  └──────────────────────────────────┘  │
│         ↕                               │
│  ┌──────────────────────────────────┐  │
│  │    设备驱动程序 (Driver)          │  │
│  │  - 字符设备驱动                   │  │
│  │  - 块设备驱动                     │  │
│  │  - 网络设备驱动                   │  │
│  └──────────────────────────────────┘  │
│         ↕                               │
│  ┌──────────────────────────────────┐  │
│  │    硬件抽象层 (HAL)               │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         ↕ 硬件访问
┌─────────────────────────────────────────┐
│         硬件层 (Hardware)                │
│  CPU、内存、外设、传感器等               │
└─────────────────────────────────────────┘
```

### 设备分类

Linux将设备分为三大类：

**1. 字符设备 (Character Device)**

- **特点**：按字节流顺序访问，不支持随机访问
- **示例**：串口、键盘、鼠标、LED、传感器
- **设备文件**：/dev/ttyS0、/dev/input/event0
- **主设备号范围**：通常为1-255

**2. 块设备 (Block Device)**
- **特点**：以块为单位访问，支持随机访问
- **示例**：硬盘、SD卡、U盘、SSD
- **设备文件**：/dev/sda、/dev/mmcblk0
- **主设备号范围**：通常为8、179等

**3. 网络设备 (Network Device)**
- **特点**：通过套接字接口访问，不使用设备文件
- **示例**：以太网卡、WiFi、蓝牙
- **接口名称**：eth0、wlan0、lo
- **访问方式**：socket API

**设备号说明**：

| 概念 | 说明 | 示例 |
|------|------|------|
| 主设备号 | 标识设备类型/驱动 | 4 (tty设备) |
| 次设备号 | 标识具体设备实例 | 0 (ttyS0), 1 (ttyS1) |
| 设备号 | 主设备号 + 次设备号 | (4, 0) |
| 设备文件 | 用户空间访问接口 | /dev/ttyS0 |

### 驱动程序的作用

驱动程序主要完成以下任务：

**1. 硬件初始化**
```c
// 配置寄存器
// 申请资源（内存、中断、DMA等）
// 初始化硬件状态
```

**2. 提供访问接口**
```c
// 实现 open、read、write、ioctl 等操作
// 处理用户空间的请求
// 数据传输和转换
```

**3. 中断处理**
```c
// 注册中断处理函数
// 响应硬件中断
// 数据缓冲和同步
```

**4. 电源管理**
```c
// 实现 suspend、resume 接口
// 节能模式控制
// 运行时电源管理
```

**5. 错误处理**
```c
// 检测硬件错误
// 错误恢复机制
// 日志记录
```

## 内核模块编程基础

### 什么是内核模块

**内核模块 (Kernel Module)** 是可以动态加载和卸载的内核代码，无需重新编译整个内核。

**优势**：
- 按需加载，节省内存
- 便于开发和调试
- 支持热插拔
- 模块化设计

**限制**：
- 运行在内核空间，权限最高
- 错误可能导致系统崩溃
- 不能使用标准C库
- 必须使用内核API

### 最简单的内核模块

**hello.c**：

```c
#include <linux/module.h>    // 所有模块都需要
#include <linux/kernel.h>    // KERN_INFO等
#include <linux/init.h>      // __init和__exit宏

// 模块加载函数
static int __init hello_init(void)
{
    printk(KERN_INFO "Hello, Kernel!\n");
    return 0;  // 返回0表示成功
}

// 模块卸载函数
static void __exit hello_exit(void)
{
    printk(KERN_INFO "Goodbye, Kernel!\n");
}

// 注册模块入口和出口
module_init(hello_init);
module_exit(hello_exit);

// 模块信息
MODULE_LICENSE("GPL");                    // 许可证
MODULE_AUTHOR("Your Name");               // 作者
MODULE_DESCRIPTION("A simple hello module");  // 描述
MODULE_VERSION("1.0");                    // 版本
```

**Makefile**：

```makefile
# 内核源码路径
KERNEL_DIR := /lib/modules/$(shell uname -r)/build
# 当前目录
PWD := $(shell pwd)

# 模块名称
obj-m := hello.o

# 编译目标
all:
	make -C $(KERNEL_DIR) M=$(PWD) modules

# 清理
clean:
	make -C $(KERNEL_DIR) M=$(PWD) clean

# 安装模块
install:
	make -C $(KERNEL_DIR) M=$(PWD) modules_install
```

**编译和测试**：

```bash
# 编译模块
make

# 查看生成的文件
ls -lh
# hello.c  hello.ko  hello.mod.c  hello.mod.o  hello.o  Makefile

# 加载模块
sudo insmod hello.ko

# 查看模块信息
lsmod | grep hello
modinfo hello.ko

# 查看内核日志
dmesg | tail
# 输出：Hello, Kernel!

# 卸载模块
sudo rmmod hello

# 再次查看日志
dmesg | tail
# 输出：Goodbye, Kernel!
```

### 模块参数

模块可以接受参数，在加载时配置：

```c
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/kernel.h>

// 定义模块参数
static int count = 1;
static char *name = "World";

// 声明参数（变量名、类型、权限）
module_param(count, int, S_IRUGO);
module_param(name, charp, S_IRUGO);

// 参数描述
MODULE_PARM_DESC(count, "Number of times to print");
MODULE_PARM_DESC(name, "Name to print");

static int __init param_init(void)
{
    int i;
    for (i = 0; i < count; i++) {
        printk(KERN_INFO "Hello, %s! (%d/%d)\n", name, i+1, count);
    }
    return 0;
}

static void __exit param_exit(void)
{
    printk(KERN_INFO "Goodbye!\n");
}

module_init(param_init);
module_exit(param_exit);

MODULE_LICENSE("GPL");
```

**使用参数**：

```bash
# 加载时指定参数
sudo insmod param.ko count=3 name="Linux"

# 查看参数
cat /sys/module/param/parameters/count
cat /sys/module/param/parameters/name

# 查看日志
dmesg | tail
# 输出：
# Hello, Linux! (1/3)
# Hello, Linux! (2/3)
# Hello, Linux! (3/3)
```

### printk日志级别

printk是内核的打印函数，支持不同的日志级别：

```c
#include <linux/kern_levels.h>

// 日志级别（从高到低）
printk(KERN_EMERG   "Emergency: system is unusable\n");      // 0
printk(KERN_ALERT   "Alert: action must be taken\n");        // 1
printk(KERN_CRIT    "Critical: critical conditions\n");      // 2
printk(KERN_ERR     "Error: error conditions\n");            // 3
printk(KERN_WARNING "Warning: warning conditions\n");        // 4
printk(KERN_NOTICE  "Notice: normal but significant\n");     // 5
printk(KERN_INFO    "Info: informational\n");                // 6
printk(KERN_DEBUG   "Debug: debug-level messages\n");        // 7

// 简化写法
pr_emerg("Emergency message\n");
pr_alert("Alert message\n");
pr_crit("Critical message\n");
pr_err("Error message\n");
pr_warn("Warning message\n");
pr_notice("Notice message\n");
pr_info("Info message\n");
pr_debug("Debug message\n");  // 需要定义DEBUG才会输出
```

**查看和设置日志级别**：

```bash
# 查看当前日志级别
cat /proc/sys/kernel/printk
# 输出：4  4  1  7
# 含义：console_loglevel  default_message_loglevel  minimum_console_loglevel  default_console_loglevel

# 设置日志级别（临时）
echo "8" > /proc/sys/kernel/printk

# 查看所有内核日志
dmesg

# 实时查看日志
dmesg -w

# 清空日志缓冲区
sudo dmesg -c
```

## 字符设备驱动开发

### 字符设备驱动框架

字符设备驱动的核心是实现 `file_operations` 结构体：

```
用户空间                内核空间
  │                      │
  │  open("/dev/mydev")  │
  ├─────────────────────>│ mydev_open()
  │                      │
  │  read(fd, buf, len)  │
  ├─────────────────────>│ mydev_read()
  │                      │
  │  write(fd, buf, len) │
  ├─────────────────────>│ mydev_write()
  │                      │
  │  ioctl(fd, cmd, arg) │
  ├─────────────────────>│ mydev_ioctl()
  │                      │
  │  close(fd)           │
  ├─────────────────────>│ mydev_release()
  │                      │
```

### 注册字符设备的方法

Linux提供了两种注册字符设备的方法：

**方法1：旧式API（不推荐）**

```c
// 注册设备号
int register_chrdev(unsigned int major, const char *name,
                   const struct file_operations *fops);

// 注销设备号
void unregister_chrdev(unsigned int major, const char *name);
```

**方法2：新式API（推荐）**

```c
// 1. 分配设备号
int alloc_chrdev_region(dev_t *dev, unsigned baseminor,
                       unsigned count, const char *name);

// 2. 初始化cdev
void cdev_init(struct cdev *cdev, const struct file_operations *fops);

// 3. 添加cdev到系统
int cdev_add(struct cdev *p, dev_t dev, unsigned count);

// 4. 删除cdev
void cdev_del(struct cdev *p);

// 5. 释放设备号
void unregister_chrdev_region(dev_t from, unsigned count);
```

### 完整的字符设备驱动示例

**mychardev.c**：

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>  // copy_to_user, copy_from_user

#define DEVICE_NAME "mychardev"
#define BUF_SIZE 1024

// 设备结构体
struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
};

static struct mychar_dev *mydev;
static dev_t dev_num;  // 设备号
static struct class *mydev_class;  // 设备类

// open函数
static int mydev_open(struct inode *inode, struct file *file)
{
    struct mychar_dev *dev;
    
    // 从inode获取设备结构体
    dev = container_of(inode->i_cdev, struct mychar_dev, cdev);
    file->private_data = dev;  // 保存到file结构体
    
    pr_info("mychardev: Device opened\n");
    return 0;
}

// release函数
static int mydev_release(struct inode *inode, struct file *file)
{
    pr_info("mychardev: Device closed\n");
    return 0;
}

// read函数
static ssize_t mydev_read(struct file *file, char __user *buf,
                         size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    int bytes_to_read;
    
    // 检查读取位置
    if (*ppos >= dev->buf_len)
        return 0;  // EOF
    
    // 计算实际读取字节数
    bytes_to_read = min(count, (size_t)(dev->buf_len - *ppos));
    
    // 复制数据到用户空间
    if (copy_to_user(buf, dev->buffer + *ppos, bytes_to_read)) {
        return -EFAULT;
    }
    
    *ppos += bytes_to_read;
    pr_info("mychardev: Read %d bytes\n", bytes_to_read);
    
    return bytes_to_read;
}

// write函数
static ssize_t mydev_write(struct file *file, const char __user *buf,
                          size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    int bytes_to_write;
    
    // 检查写入位置
    if (*ppos >= BUF_SIZE)
        return -ENOSPC;  // 缓冲区满
    
    // 计算实际写入字节数
    bytes_to_write = min(count, (size_t)(BUF_SIZE - *ppos));
    
    // 从用户空间复制数据
    if (copy_from_user(dev->buffer + *ppos, buf, bytes_to_write)) {
        return -EFAULT;
    }
    
    *ppos += bytes_to_write;
    dev->buf_len = *ppos;
    
    pr_info("mychardev: Wrote %d bytes\n", bytes_to_write);
    
    return bytes_to_write;
}

// file_operations结构体
static struct file_operations mydev_fops = {
    .owner = THIS_MODULE,
    .open = mydev_open,
    .release = mydev_release,
    .read = mydev_read,
    .write = mydev_write,
};

// 模块初始化
static int __init mydev_init(void)
{
    int ret;
    struct device *device;
    
    // 1. 分配设备号
    ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        pr_err("mychardev: Failed to allocate device number\n");
        return ret;
    }
    pr_info("mychardev: Device number: major=%d, minor=%d\n",
            MAJOR(dev_num), MINOR(dev_num));
    
    // 2. 分配设备结构体
    mydev = kzalloc(sizeof(struct mychar_dev), GFP_KERNEL);
    if (!mydev) {
        ret = -ENOMEM;
        goto fail_alloc;
    }
    
    // 3. 初始化cdev
    cdev_init(&mydev->cdev, &mydev_fops);
    mydev->cdev.owner = THIS_MODULE;
    
    // 4. 添加cdev到系统
    ret = cdev_add(&mydev->cdev, dev_num, 1);
    if (ret < 0) {
        pr_err("mychardev: Failed to add cdev\n");
        goto fail_cdev;
    }
    
    // 5. 创建设备类
    mydev_class = class_create(THIS_MODULE, DEVICE_NAME);
    if (IS_ERR(mydev_class)) {
        ret = PTR_ERR(mydev_class);
        pr_err("mychardev: Failed to create class\n");
        goto fail_class;
    }
    
    // 6. 创建设备文件
    device = device_create(mydev_class, NULL, dev_num, NULL, DEVICE_NAME);
    if (IS_ERR(device)) {
        ret = PTR_ERR(device);
        pr_err("mychardev: Failed to create device\n");
        goto fail_device;
    }
    
    pr_info("mychardev: Module loaded successfully\n");
    return 0;

fail_device:
    class_destroy(mydev_class);
fail_class:
    cdev_del(&mydev->cdev);
fail_cdev:
    kfree(mydev);
fail_alloc:
    unregister_chrdev_region(dev_num, 1);
    return ret;
}

// 模块清理
static void __exit mydev_exit(void)
{
    // 删除设备文件
    device_destroy(mydev_class, dev_num);
    
    // 删除设备类
    class_destroy(mydev_class);
    
    // 删除cdev
    cdev_del(&mydev->cdev);
    
    // 释放设备结构体
    kfree(mydev);
    
    // 释放设备号
    unregister_chrdev_region(dev_num, 1);
    
    pr_info("mychardev: Module unloaded\n");
}

module_init(mydev_init);
module_exit(mydev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple character device driver");
MODULE_VERSION("1.0");
```

**Makefile**：

```makefile
obj-m := mychardev.o

KERNEL_DIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	make -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	make -C $(KERNEL_DIR) M=$(PWD) clean

load:
	sudo insmod mychardev.ko
	sudo chmod 666 /dev/mychardev

unload:
	sudo rmmod mychardev
```

**测试程序 test.c**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define DEVICE "/dev/mychardev"

int main(int argc, char *argv[])
{
    int fd;
    char write_buf[] = "Hello from user space!";
    char read_buf[1024] = {0};
    ssize_t ret;
    
    // 打开设备
    fd = open(DEVICE, O_RDWR);
    if (fd < 0) {
        perror("Failed to open device");
        return 1;
    }
    printf("Device opened successfully\n");
    
    // 写入数据
    ret = write(fd, write_buf, strlen(write_buf));
    if (ret < 0) {
        perror("Failed to write");
        close(fd);
        return 1;
    }
    printf("Wrote %zd bytes: %s\n", ret, write_buf);
    
    // 重置文件位置
    lseek(fd, 0, SEEK_SET);
    
    // 读取数据
    ret = read(fd, read_buf, sizeof(read_buf));
    if (ret < 0) {
        perror("Failed to read");
        close(fd);
        return 1;
    }
    printf("Read %zd bytes: %s\n", ret, read_buf);
    
    // 关闭设备
    close(fd);
    printf("Device closed\n");
    
    return 0;
}
```

**编译和测试**：

```bash
# 编译驱动
make

# 加载驱动
make load

# 查看设备文件
ls -l /dev/mychardev
# 输出：crw-rw-rw- 1 root root 240, 0 Jan 15 10:00 /dev/mychardev

# 编译测试程序
gcc -o test test.c

# 运行测试
./test
# 输出：
# Device opened successfully
# Wrote 22 bytes: Hello from user space!
# Read 22 bytes: Hello from user space!
# Device closed

# 查看内核日志
dmesg | tail
# 输出：
# mychardev: Device opened
# mychardev: Wrote 22 bytes
# mychardev: Read 22 bytes
# mychardev: Device closed

# 卸载驱动
make unload
```



## ioctl实现

ioctl用于设备特定的控制操作：

**定义ioctl命令**：

```c
#include <linux/ioctl.h>

// 定义魔数（唯一标识）
#define MYDEV_IOC_MAGIC 'k'

// 定义命令
#define MYDEV_IOCRESET    _IO(MYDEV_IOC_MAGIC, 0)
#define MYDEV_IOCGETVAL   _IOR(MYDEV_IOC_MAGIC, 1, int)
#define MYDEV_IOCSETVAL   _IOW(MYDEV_IOC_MAGIC, 2, int)
#define MYDEV_IOCXCHGVAL  _IOWR(MYDEV_IOC_MAGIC, 3, int)

#define MYDEV_IOC_MAXNR 3

// 宏说明：
// _IO(type, nr)         - 无参数命令
// _IOR(type, nr, size)  - 读取数据
// _IOW(type, nr, size)  - 写入数据
// _IOWR(type, nr, size) - 读写数据
```

**实现ioctl函数**：

```c
static long mydev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    struct mychar_dev *dev = file->private_data;
    int val;
    int ret = 0;
    
    // 检查命令有效性
    if (_IOC_TYPE(cmd) != MYDEV_IOC_MAGIC) return -ENOTTY;
    if (_IOC_NR(cmd) > MYDEV_IOC_MAXNR) return -ENOTTY;
    
    switch (cmd) {
    case MYDEV_IOCRESET:
        // 重置设备
        memset(dev->buffer, 0, BUF_SIZE);
        dev->buf_len = 0;
        pr_info("mychardev: Device reset\n");
        break;
        
    case MYDEV_IOCGETVAL:
        // 读取值
        val = dev->buf_len;
        if (copy_to_user((int __user *)arg, &val, sizeof(val)))
            return -EFAULT;
        pr_info("mychardev: Get value: %d\n", val);
        break;
        
    case MYDEV_IOCSETVAL:
        // 设置值
        if (copy_from_user(&val, (int __user *)arg, sizeof(val)))
            return -EFAULT;
        if (val < 0 || val > BUF_SIZE)
            return -EINVAL;
        dev->buf_len = val;
        pr_info("mychardev: Set value: %d\n", val);
        break;
        
    case MYDEV_IOCXCHGVAL:
        // 交换值
        if (copy_from_user(&val, (int __user *)arg, sizeof(val)))
            return -EFAULT;
        if (val < 0 || val > BUF_SIZE)
            return -EINVAL;
        // 交换
        {
            int old_val = dev->buf_len;
            dev->buf_len = val;
            val = old_val;
        }
        if (copy_to_user((int __user *)arg, &val, sizeof(val)))
            return -EFAULT;
        pr_info("mychardev: Exchange value: %d\n", val);
        break;
        
    default:
        return -ENOTTY;
    }
    
    return ret;
}

// 更新file_operations
static struct file_operations mydev_fops = {
    .owner = THIS_MODULE,
    .open = mydev_open,
    .release = mydev_release,
    .read = mydev_read,
    .write = mydev_write,
    .unlocked_ioctl = mydev_ioctl,  // 添加ioctl
};
```

**用户空间测试**：

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

// 包含相同的ioctl定义
#define MYDEV_IOC_MAGIC 'k'
#define MYDEV_IOCRESET    _IO(MYDEV_IOC_MAGIC, 0)
#define MYDEV_IOCGETVAL   _IOR(MYDEV_IOC_MAGIC, 1, int)
#define MYDEV_IOCSETVAL   _IOW(MYDEV_IOC_MAGIC, 2, int)
#define MYDEV_IOCXCHGVAL  _IOWR(MYDEV_IOC_MAGIC, 3, int)

int main()
{
    int fd, val;
    
    fd = open("/dev/mychardev", O_RDWR);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    
    // 重置设备
    if (ioctl(fd, MYDEV_IOCRESET) < 0) {
        perror("ioctl reset");
    }
    
    // 设置值
    val = 100;
    if (ioctl(fd, MYDEV_IOCSETVAL, &val) < 0) {
        perror("ioctl set");
    }
    
    // 获取值
    if (ioctl(fd, MYDEV_IOCGETVAL, &val) < 0) {
        perror("ioctl get");
    }
    printf("Current value: %d\n", val);
    
    // 交换值
    val = 200;
    if (ioctl(fd, MYDEV_IOCXCHGVAL, &val) < 0) {
        perror("ioctl exchange");
    }
    printf("Old value: %d\n", val);
    
    close(fd);
    return 0;
}
```

## 并发和同步

### 为什么需要同步

驱动程序可能被多个进程同时访问，需要保护共享资源：

```
进程A                驱动程序              进程B
  │                    │                    │
  │  open()            │                    │
  ├───────────────────>│                    │
  │                    │  open()            │
  │                    │<───────────────────┤
  │  write()           │                    │
  ├───────────────────>│                    │
  │                    │  write()           │
  │                    │<───────────────────┤
  │                    │                    │
  │         竞态条件！  │                    │
  │    需要同步机制保护 │                    │
```

### 同步机制

**1. 互斥锁 (Mutex)**

```c
#include <linux/mutex.h>

struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
    struct mutex lock;  // 添加互斥锁
};

// 初始化
static int __init mydev_init(void)
{
    // ...
    mutex_init(&mydev->lock);
    // ...
}

// 使用互斥锁
static ssize_t mydev_write(struct file *file, const char __user *buf,
                          size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    int bytes_to_write;
    int ret;
    
    // 获取锁
    if (mutex_lock_interruptible(&dev->lock))
        return -ERESTARTSYS;
    
    // 临界区代码
    if (*ppos >= BUF_SIZE) {
        ret = -ENOSPC;
        goto out;
    }
    
    bytes_to_write = min(count, (size_t)(BUF_SIZE - *ppos));
    
    if (copy_from_user(dev->buffer + *ppos, buf, bytes_to_write)) {
        ret = -EFAULT;
        goto out;
    }
    
    *ppos += bytes_to_write;
    dev->buf_len = *ppos;
    ret = bytes_to_write;
    
out:
    // 释放锁
    mutex_unlock(&dev->lock);
    return ret;
}
```

**2. 自旋锁 (Spinlock)**

```c
#include <linux/spinlock.h>

struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
    spinlock_t lock;  // 自旋锁
};

// 初始化
static int __init mydev_init(void)
{
    // ...
    spin_lock_init(&mydev->lock);
    // ...
}

// 使用自旋锁
static ssize_t mydev_read(struct file *file, char __user *buf,
                         size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    unsigned long flags;
    int bytes_to_read;
    
    // 获取锁（禁用中断）
    spin_lock_irqsave(&dev->lock, flags);
    
    // 临界区代码
    if (*ppos >= dev->buf_len) {
        bytes_to_read = 0;
        goto out;
    }
    
    bytes_to_read = min(count, (size_t)(dev->buf_len - *ppos));
    
    if (copy_to_user(buf, dev->buffer + *ppos, bytes_to_read)) {
        bytes_to_read = -EFAULT;
        goto out;
    }
    
    *ppos += bytes_to_read;
    
out:
    // 释放锁（恢复中断）
    spin_unlock_irqrestore(&dev->lock, flags);
    return bytes_to_read;
}
```

**3. 信号量 (Semaphore)**

```c
#include <linux/semaphore.h>

struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
    struct semaphore sem;  // 信号量
};

// 初始化（初始值为1，相当于互斥锁）
static int __init mydev_init(void)
{
    // ...
    sema_init(&mydev->sem, 1);
    // ...
}

// 使用信号量
static ssize_t mydev_write(struct file *file, const char __user *buf,
                          size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    int ret;
    
    // P操作（down）
    if (down_interruptible(&dev->sem))
        return -ERESTARTSYS;
    
    // 临界区代码
    // ...
    
    // V操作（up）
    up(&dev->sem);
    return ret;
}
```

**同步机制对比**：

| 机制 | 适用场景 | 可睡眠 | 开销 | 使用建议 |
|------|---------|--------|------|---------|
| Mutex | 进程上下文 | 是 | 中等 | 推荐用于一般情况 |
| Spinlock | 中断上下文 | 否 | 低 | 临界区很短时使用 |
| Semaphore | 进程上下文 | 是 | 高 | 需要计数功能时使用 |
| RW Lock | 读多写少 | 否 | 低 | 读写分离场景 |

## 中断处理

### 注册中断处理函数

```c
#include <linux/interrupt.h>

// 中断处理函数
static irqreturn_t mydev_irq_handler(int irq, void *dev_id)
{
    struct mychar_dev *dev = dev_id;
    
    // 读取硬件状态
    // 清除中断标志
    // 处理数据
    
    pr_info("mychardev: Interrupt occurred\n");
    
    return IRQ_HANDLED;  // 或 IRQ_NONE
}

// 注册中断
static int __init mydev_init(void)
{
    int irq = 25;  // 中断号
    int ret;
    
    // ...
    
    // 请求中断
    ret = request_irq(irq, mydev_irq_handler,
                     IRQF_SHARED,  // 中断标志
                     DEVICE_NAME,  // 设备名
                     mydev);       // dev_id
    if (ret < 0) {
        pr_err("mychardev: Failed to request IRQ %d\n", irq);
        goto fail_irq;
    }
    
    pr_info("mychardev: IRQ %d registered\n", irq);
    
    // ...
}

// 释放中断
static void __exit mydev_exit(void)
{
    int irq = 25;
    
    // 释放中断
    free_irq(irq, mydev);
    
    // ...
}
```

### 中断上下文和下半部

**中断处理分为两部分**：

**上半部 (Top Half)**：
- 在中断上下文中执行
- 必须快速完成
- 不能睡眠
- 不能调用可能睡眠的函数

**下半部 (Bottom Half)**：
- 延迟处理耗时操作
- 可以睡眠
- 常用机制：tasklet、workqueue

**使用tasklet**：

```c
#include <linux/interrupt.h>

// tasklet处理函数
static void mydev_tasklet_func(unsigned long data)
{
    struct mychar_dev *dev = (struct mychar_dev *)data;
    
    // 耗时的数据处理
    pr_info("mychardev: Tasklet executed\n");
}

// 声明tasklet
static DECLARE_TASKLET(mydev_tasklet, mydev_tasklet_func, 0);

// 中断处理函数
static irqreturn_t mydev_irq_handler(int irq, void *dev_id)
{
    struct mychar_dev *dev = dev_id;
    
    // 快速处理
    // 读取硬件状态
    // 清除中断标志
    
    // 调度tasklet
    mydev_tasklet.data = (unsigned long)dev;
    tasklet_schedule(&mydev_tasklet);
    
    return IRQ_HANDLED;
}

// 清理
static void __exit mydev_exit(void)
{
    // 杀死tasklet
    tasklet_kill(&mydev_tasklet);
    
    // ...
}
```

**使用workqueue**：

```c
#include <linux/workqueue.h>

// work处理函数
static void mydev_work_func(struct work_struct *work)
{
    struct mychar_dev *dev = container_of(work, struct mychar_dev, work);
    
    // 可以睡眠的耗时操作
    msleep(100);
    
    pr_info("mychardev: Work executed\n");
}

struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
    struct work_struct work;  // work结构
};

// 初始化
static int __init mydev_init(void)
{
    // ...
    INIT_WORK(&mydev->work, mydev_work_func);
    // ...
}

// 中断处理函数
static irqreturn_t mydev_irq_handler(int irq, void *dev_id)
{
    struct mychar_dev *dev = dev_id;
    
    // 快速处理
    
    // 调度work
    schedule_work(&dev->work);
    
    return IRQ_HANDLED;
}

// 清理
static void __exit mydev_exit(void)
{
    // 取消work
    cancel_work_sync(&mydev->work);
    
    // ...
}
```

## 内存管理

### 内核内存分配

**kmalloc和kfree**：

```c
#include <linux/slab.h>

// 分配内存
void *ptr = kmalloc(size, GFP_KERNEL);
if (!ptr) {
    pr_err("Failed to allocate memory\n");
    return -ENOMEM;
}

// 使用内存
memset(ptr, 0, size);

// 释放内存
kfree(ptr);
```

**GFP标志**：

| 标志 | 说明 | 使用场景 |
|------|------|---------|
| GFP_KERNEL | 可能睡眠 | 进程上下文 |
| GFP_ATOMIC | 不能睡眠 | 中断上下文 |
| GFP_DMA | DMA内存 | DMA操作 |
| GFP_HIGHUSER | 高端内存 | 用户空间 |

**kzalloc**：

```c
// 分配并清零
void *ptr = kzalloc(size, GFP_KERNEL);
// 等价于：
// void *ptr = kmalloc(size, GFP_KERNEL);
// memset(ptr, 0, size);
```

**vmalloc**：

```c
#include <linux/vmalloc.h>

// 分配虚拟连续内存（物理可能不连续）
void *ptr = vmalloc(size);
if (!ptr) {
    pr_err("Failed to allocate memory\n");
    return -ENOMEM;
}

// 使用内存

// 释放内存
vfree(ptr);
```

**kmalloc vs vmalloc**：

| 特性 | kmalloc | vmalloc |
|------|---------|---------|
| 物理内存 | 连续 | 可能不连续 |
| 虚拟内存 | 连续 | 连续 |
| 大小限制 | 较小（通常<128KB） | 较大 |
| 性能 | 快 | 慢 |
| 使用场景 | 小块内存 | 大块内存 |

### 用户空间和内核空间数据交换

**copy_to_user和copy_from_user**：

```c
#include <linux/uaccess.h>

// 从内核复制到用户空间
unsigned long copy_to_user(void __user *to, const void *from, unsigned long n);

// 从用户空间复制到内核
unsigned long copy_from_user(void *to, const void __user *from, unsigned long n);

// 返回值：未复制的字节数（0表示成功）
```

**示例**：

```c
static ssize_t mydev_read(struct file *file, char __user *buf,
                         size_t count, loff_t *ppos)
{
    char kernel_buf[100] = "Hello from kernel";
    size_t len = strlen(kernel_buf);
    
    if (count < len)
        len = count;
    
    // 复制到用户空间
    if (copy_to_user(buf, kernel_buf, len)) {
        return -EFAULT;  // 错误
    }
    
    return len;  // 成功复制的字节数
}
```

**get_user和put_user**：

```c
// 读取单个简单类型
int get_user(x, ptr);  // x = *ptr

// 写入单个简单类型
int put_user(x, ptr);  // *ptr = x

// 示例
static long mydev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    int val;
    
    switch (cmd) {
    case MYDEV_IOCGETVAL:
        val = 100;
        if (put_user(val, (int __user *)arg))
            return -EFAULT;
        break;
        
    case MYDEV_IOCSETVAL:
        if (get_user(val, (int __user *)arg))
            return -EFAULT;
        pr_info("Received value: %d\n", val);
        break;
    }
    
    return 0;
}
```

## 设备树集成

### 在设备树中定义设备

**设备树节点**：

```dts
/ {
    mychardev {
        compatible = "mycompany,mychardev";
        reg = <0x40000000 0x1000>;
        interrupts = <0 25 IRQ_TYPE_LEVEL_HIGH>;
        clock-frequency = <100000>;
        status = "okay";
    };
};
```

### 在驱动中解析设备树

```c
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/platform_device.h>

// 设备树匹配表
static const struct of_device_id mydev_of_match[] = {
    { .compatible = "mycompany,mychardev" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, mydev_of_match);

// probe函数
static int mydev_probe(struct platform_device *pdev)
{
    struct device_node *np = pdev->dev.of_node;
    struct resource *res;
    void __iomem *base;
    int irq;
    u32 clock_freq;
    
    pr_info("mychardev: Probing device\n");
    
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
    
    // 读取设备树属性
    if (of_property_read_u32(np, "clock-frequency", &clock_freq)) {
        dev_warn(&pdev->dev, "Using default clock frequency\n");
        clock_freq = 100000;
    }
    
    dev_info(&pdev->dev, "Base: 0x%px, IRQ: %d, Clock: %u Hz\n",
             base, irq, clock_freq);
    
    // 初始化设备...
    
    return 0;
}

// remove函数
static int mydev_remove(struct platform_device *pdev)
{
    pr_info("mychardev: Removing device\n");
    
    // 清理资源...
    
    return 0;
}

// 平台驱动结构
static struct platform_driver mydev_platform_driver = {
    .probe = mydev_probe,
    .remove = mydev_remove,
    .driver = {
        .name = "mychardev",
        .of_match_table = mydev_of_match,
    },
};

// 注册平台驱动
module_platform_driver(mydev_platform_driver);

MODULE_LICENSE("GPL");
```



## 驱动调试技巧

### printk调试

**基本用法**：

```c
// 不同级别的日志
pr_emerg("Emergency: system is unusable\n");
pr_alert("Alert: action must be taken immediately\n");
pr_crit("Critical: critical conditions\n");
pr_err("Error: error conditions\n");
pr_warn("Warning: warning conditions\n");
pr_notice("Notice: normal but significant condition\n");
pr_info("Info: informational\n");
pr_debug("Debug: debug-level messages\n");

// 带设备信息的日志
dev_err(&pdev->dev, "Failed to initialize device\n");
dev_warn(&pdev->dev, "Device in low power mode\n");
dev_info(&pdev->dev, "Device initialized successfully\n");
dev_dbg(&pdev->dev, "Register value: 0x%08x\n", val);
```

**动态调试**：

```bash
# 启用动态调试
echo "file mychardev.c +p" > /sys/kernel/debug/dynamic_debug/control

# 启用特定函数的调试
echo "func mydev_read +p" > /sys/kernel/debug/dynamic_debug/control

# 启用特定行的调试
echo "file mychardev.c line 100-200 +p" > /sys/kernel/debug/dynamic_debug/control

# 查看当前设置
cat /sys/kernel/debug/dynamic_debug/control | grep mychardev

# 禁用调试
echo "file mychardev.c -p" > /sys/kernel/debug/dynamic_debug/control
```

### proc文件系统调试

**创建proc文件**：

```c
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

// seq_file show函数
static int mydev_proc_show(struct seq_file *m, void *v)
{
    struct mychar_dev *dev = m->private;
    
    seq_printf(m, "Device Status:\n");
    seq_printf(m, "  Buffer length: %d\n", dev->buf_len);
    seq_printf(m, "  Buffer content: %s\n", dev->buffer);
    
    return 0;
}

// open函数
static int mydev_proc_open(struct inode *inode, struct file *file)
{
    return single_open(file, mydev_proc_show, PDE_DATA(inode));
}

// proc文件操作
static const struct proc_ops mydev_proc_fops = {
    .proc_open = mydev_proc_open,
    .proc_read = seq_read,
    .proc_lseek = seq_lseek,
    .proc_release = single_release,
};

// 创建proc文件
static int __init mydev_init(void)
{
    struct proc_dir_entry *entry;
    
    // ...
    
    // 创建/proc/mychardev
    entry = proc_create_data("mychardev", 0444, NULL,
                            &mydev_proc_fops, mydev);
    if (!entry) {
        pr_err("Failed to create proc entry\n");
        return -ENOMEM;
    }
    
    // ...
}

// 删除proc文件
static void __exit mydev_exit(void)
{
    // 删除/proc/mychardev
    remove_proc_entry("mychardev", NULL);
    
    // ...
}
```

**读取proc文件**：

```bash
# 查看设备状态
cat /proc/mychardev
# 输出：
# Device Status:
#   Buffer length: 22
#   Buffer content: Hello from user space!
```

### debugfs调试

**创建debugfs文件**：

```c
#include <linux/debugfs.h>

static struct dentry *mydev_debugfs_dir;

static int __init mydev_init(void)
{
    // ...
    
    // 创建debugfs目录
    mydev_debugfs_dir = debugfs_create_dir("mychardev", NULL);
    if (!mydev_debugfs_dir) {
        pr_err("Failed to create debugfs directory\n");
        return -ENOMEM;
    }
    
    // 创建debugfs文件
    debugfs_create_u32("buf_len", 0644, mydev_debugfs_dir, &mydev->buf_len);
    debugfs_create_file("buffer", 0644, mydev_debugfs_dir, mydev, &mydev_debug_fops);
    
    // ...
}

static void __exit mydev_exit(void)
{
    // 删除debugfs目录（会递归删除所有文件）
    debugfs_remove_recursive(mydev_debugfs_dir);
    
    // ...
}
```

**使用debugfs**：

```bash
# 挂载debugfs（通常已自动挂载）
mount -t debugfs none /sys/kernel/debug

# 查看debugfs文件
ls /sys/kernel/debug/mychardev/

# 读取值
cat /sys/kernel/debug/mychardev/buf_len

# 写入值
echo 50 > /sys/kernel/debug/mychardev/buf_len
```

### 使用ftrace跟踪

**启用函数跟踪**：

```bash
# 挂载tracefs
mount -t tracefs nodev /sys/kernel/tracing

# 设置跟踪器
echo function > /sys/kernel/tracing/current_tracer

# 设置过滤器（只跟踪mydev_*函数）
echo 'mydev_*' > /sys/kernel/tracing/set_ftrace_filter

# 启用跟踪
echo 1 > /sys/kernel/tracing/tracing_on

# 执行测试程序
./test

# 查看跟踪结果
cat /sys/kernel/tracing/trace

# 停止跟踪
echo 0 > /sys/kernel/tracing/tracing_on

# 清空跟踪缓冲区
echo > /sys/kernel/tracing/trace
```

### 使用KGDB调试

**配置内核**：

```bash
# 内核配置
Kernel hacking  --->
    [*] KGDB: kernel debugger  --->
        <*>   KGDB: use kgdb over the serial console
```

**启动参数**：

```bash
# 添加内核启动参数
console=ttyS0,115200 kgdboc=ttyS0,115200 kgdbwait
```

**使用GDB连接**：

```bash
# 在开发主机上
arm-linux-gnueabihf-gdb vmlinux

# 在GDB中连接
(gdb) target remote /dev/ttyUSB0
(gdb) continue

# 设置断点
(gdb) break mydev_open
(gdb) continue

# 查看变量
(gdb) print dev->buf_len
(gdb) print dev->buffer

# 单步执行
(gdb) step
(gdb) next

# 查看调用栈
(gdb) backtrace
```

## 常见问题和解决方案

### 问题1：模块加载失败

**错误信息**：

```bash
insmod: ERROR: could not insert module mychardev.ko: Invalid module format
```

**原因分析**：
- 内核版本不匹配
- 编译器版本不匹配
- 配置选项不一致

**解决方案**：

```bash
# 检查内核版本
uname -r
modinfo mychardev.ko | grep vermagic

# 使用正确的内核源码重新编译
make -C /lib/modules/$(uname -r)/build M=$(pwd) clean
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
```

### 问题2：设备文件未创建

**症状**：
- /dev/mychardev不存在
- 手动创建设备文件后可以工作

**原因**：
- 未使用udev/mdev自动创建
- class_create或device_create失败

**解决方案**：

```c
// 确保正确创建设备类和设备
mydev_class = class_create(THIS_MODULE, DEVICE_NAME);
if (IS_ERR(mydev_class)) {
    pr_err("Failed to create class\n");
    return PTR_ERR(mydev_class);
}

device = device_create(mydev_class, NULL, dev_num, NULL, DEVICE_NAME);
if (IS_ERR(device)) {
    pr_err("Failed to create device\n");
    class_destroy(mydev_class);
    return PTR_ERR(device);
}
```

**手动创建设备文件**：

```bash
# 查看设备号
cat /proc/devices | grep mychardev
# 输出：240 mychardev

# 手动创建设备文件
sudo mknod /dev/mychardev c 240 0
sudo chmod 666 /dev/mychardev
```

### 问题3：内核崩溃（Oops）

**错误信息**：

```
Unable to handle kernel NULL pointer dereference at virtual address 00000000
...
PC is at mydev_read+0x10/0x50 [mychardev]
```

**调试方法**：

```bash
# 1. 查看完整的Oops信息
dmesg

# 2. 使用addr2line定位代码行
addr2line -e mychardev.ko 0x10

# 3. 使用objdump反汇编
arm-linux-gnueabihf-objdump -d mychardev.ko > mychardev.asm

# 4. 检查代码
# 常见原因：
# - 空指针解引用
# - 访问已释放的内存
# - 数组越界
# - 未初始化的变量
```

**预防措施**：

```c
// 检查指针
if (!dev) {
    pr_err("Device pointer is NULL\n");
    return -EINVAL;
}

// 检查参数
if (!buf || count == 0) {
    return -EINVAL;
}

// 边界检查
if (*ppos >= BUF_SIZE) {
    return -ENOSPC;
}
```

### 问题4：内存泄漏

**检测方法**：

```bash
# 使用kmemleak检测
echo scan > /sys/kernel/debug/kmemleak
cat /sys/kernel/debug/kmemleak

# 使用valgrind（用户空间程序）
valgrind --leak-check=full ./test
```

**常见原因**：

```c
// 错误：分配后未释放
static int mydev_open(struct inode *inode, struct file *file)
{
    char *buf = kmalloc(1024, GFP_KERNEL);
    // 使用buf...
    // 忘记kfree(buf)
    return 0;
}

// 正确：使用devm_*函数自动管理
static int mydev_probe(struct platform_device *pdev)
{
    char *buf = devm_kmalloc(&pdev->dev, 1024, GFP_KERNEL);
    // 使用buf...
    // 设备移除时自动释放
    return 0;
}
```

### 问题5：竞态条件

**症状**：
- 偶尔出现数据错误
- 多进程访问时崩溃
- 数据不一致

**解决方案**：

```c
// 使用互斥锁保护共享资源
struct mychar_dev {
    struct cdev cdev;
    char buffer[BUF_SIZE];
    int buf_len;
    struct mutex lock;  // 添加锁
};

static ssize_t mydev_write(struct file *file, const char __user *buf,
                          size_t count, loff_t *ppos)
{
    struct mychar_dev *dev = file->private_data;
    int ret;
    
    // 获取锁
    if (mutex_lock_interruptible(&dev->lock))
        return -ERESTARTSYS;
    
    // 临界区代码
    // ...
    
    // 释放锁
    mutex_unlock(&dev->lock);
    return ret;
}
```

## 最佳实践

### 1. 错误处理

**完整的错误处理流程**：

```c
static int __init mydev_init(void)
{
    int ret;
    
    // 分配设备号
    ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        pr_err("Failed to allocate device number\n");
        return ret;
    }
    
    // 分配设备结构体
    mydev = kzalloc(sizeof(struct mychar_dev), GFP_KERNEL);
    if (!mydev) {
        ret = -ENOMEM;
        goto fail_alloc;
    }
    
    // 初始化cdev
    cdev_init(&mydev->cdev, &mydev_fops);
    ret = cdev_add(&mydev->cdev, dev_num, 1);
    if (ret < 0) {
        pr_err("Failed to add cdev\n");
        goto fail_cdev;
    }
    
    // 创建设备类
    mydev_class = class_create(THIS_MODULE, DEVICE_NAME);
    if (IS_ERR(mydev_class)) {
        ret = PTR_ERR(mydev_class);
        pr_err("Failed to create class\n");
        goto fail_class;
    }
    
    // 创建设备文件
    device = device_create(mydev_class, NULL, dev_num, NULL, DEVICE_NAME);
    if (IS_ERR(device)) {
        ret = PTR_ERR(device);
        pr_err("Failed to create device\n");
        goto fail_device;
    }
    
    pr_info("Module loaded successfully\n");
    return 0;

// 错误处理：按相反顺序清理
fail_device:
    class_destroy(mydev_class);
fail_class:
    cdev_del(&mydev->cdev);
fail_cdev:
    kfree(mydev);
fail_alloc:
    unregister_chrdev_region(dev_num, 1);
    return ret;
}
```

### 2. 资源管理

**使用devm_*函数自动管理资源**：

```c
static int mydev_probe(struct platform_device *pdev)
{
    struct mychar_dev *dev;
    struct resource *res;
    void __iomem *base;
    int irq;
    
    // 使用devm_kzalloc，设备移除时自动释放
    dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;
    
    // 使用devm_ioremap_resource，自动管理内存映射
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(base))
        return PTR_ERR(base);
    
    // 使用devm_request_irq，自动管理中断
    irq = platform_get_irq(pdev, 0);
    if (irq < 0)
        return irq;
    
    if (devm_request_irq(&pdev->dev, irq, mydev_irq_handler,
                        0, dev_name(&pdev->dev), dev))
        return -ENODEV;
    
    // 不需要在remove函数中手动释放资源
    return 0;
}
```

### 3. 代码风格

**遵循Linux内核编码规范**：

```c
// 使用tab缩进（8个空格）
// 行长度不超过80字符
// 函数名使用小写加下划线
// 宏使用大写

// 正确的代码风格
static int mydev_open(struct inode *inode, struct file *file)
{
    struct mychar_dev *dev;
    
    dev = container_of(inode->i_cdev, struct mychar_dev, cdev);
    if (!dev)
        return -EINVAL;
    
    file->private_data = dev;
    return 0;
}

// 检查代码风格
scripts/checkpatch.pl --file mychardev.c
```

### 4. 文档化

**添加注释和文档**：

```c
/**
 * mydev_read - Read data from device
 * @file: File pointer
 * @buf: User space buffer
 * @count: Number of bytes to read
 * @ppos: File position
 *
 * This function reads data from the device buffer and copies it to
 * user space. It returns the number of bytes read or a negative
 * error code on failure.
 *
 * Return: Number of bytes read on success, negative error code on failure
 */
static ssize_t mydev_read(struct file *file, char __user *buf,
                         size_t count, loff_t *ppos)
{
    // 实现...
}
```

### 5. 测试

**编写完整的测试程序**：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define DEVICE "/dev/mychardev"

void test_open_close(void)
{
    int fd;
    
    printf("Test: open/close\n");
    
    fd = open(DEVICE, O_RDWR);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    close(fd);
    printf("  PASS\n");
}

void test_read_write(void)
{
    int fd;
    char write_buf[] = "Test data";
    char read_buf[100] = {0};
    ssize_t ret;
    
    printf("Test: read/write\n");
    
    fd = open(DEVICE, O_RDWR);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    // 写入
    ret = write(fd, write_buf, strlen(write_buf));
    if (ret < 0) {
        perror("write");
        close(fd);
        return;
    }
    
    // 读取
    lseek(fd, 0, SEEK_SET);
    ret = read(fd, read_buf, sizeof(read_buf));
    if (ret < 0) {
        perror("read");
        close(fd);
        return;
    }
    
    // 验证
    if (strcmp(write_buf, read_buf) == 0) {
        printf("  PASS\n");
    } else {
        printf("  FAIL: data mismatch\n");
    }
    
    close(fd);
}

void test_concurrent_access(void)
{
    // 测试多进程并发访问
    // ...
}

int main(void)
{
    printf("=== Driver Test Suite ===\n");
    
    test_open_close();
    test_read_write();
    test_concurrent_access();
    
    printf("=== Test Complete ===\n");
    return 0;
}
```

## 实战项目：LED驱动

### 项目目标

开发一个完整的LED字符设备驱动，支持：
- 通过write控制LED开关
- 通过read读取LED状态
- 通过ioctl设置闪烁频率
- 使用设备树配置GPIO

### 设备树配置

```dts
/ {
    leds {
        compatible = "mycompany,led-driver";
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_leds>;
        
        led0 {
            label = "led0";
            gpios = <&gpio1 3 GPIO_ACTIVE_LOW>;
        };
        
        led1 {
            label = "led1";
            gpios = <&gpio1 4 GPIO_ACTIVE_LOW>;
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

### 驱动实现

**led_driver.c**（完整代码见附录）

### 测试程序

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

#define LED_IOC_MAGIC 'L'
#define LED_IOC_ON     _IO(LED_IOC_MAGIC, 0)
#define LED_IOC_OFF    _IO(LED_IOC_MAGIC, 1)
#define LED_IOC_BLINK  _IOW(LED_IOC_MAGIC, 2, int)

int main(void)
{
    int fd;
    int freq = 2;  // 2Hz
    
    fd = open("/dev/led0", O_RDWR);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    
    // 打开LED
    printf("Turn on LED\n");
    ioctl(fd, LED_IOC_ON);
    sleep(2);
    
    // 关闭LED
    printf("Turn off LED\n");
    ioctl(fd, LED_IOC_OFF);
    sleep(2);
    
    // 闪烁LED
    printf("Blink LED at %d Hz\n", freq);
    ioctl(fd, LED_IOC_BLINK, &freq);
    sleep(5);
    
    // 停止闪烁
    ioctl(fd, LED_IOC_OFF);
    
    close(fd);
    return 0;
}
```

## 总结

通过本教程，你应该已经掌握了：

- ✅ Linux驱动框架和设备模型
- ✅ 内核模块的编写和编译
- ✅ 字符设备驱动的完整开发流程
- ✅ file_operations的实现
- ✅ ioctl命令的定义和使用
- ✅ 并发控制和同步机制
- ✅ 中断处理和下半部机制
- ✅ 内存管理和用户空间数据交换
- ✅ 设备树集成
- ✅ 驱动调试的各种方法
- ✅ 常见问题的解决方案
- ✅ 驱动开发的最佳实践

### 关键要点

1. **驱动是内核的一部分**
   - 运行在内核空间，权限最高
   - 错误可能导致系统崩溃
   - 必须谨慎处理所有情况

2. **字符设备驱动核心**
   - 实现file_operations结构体
   - 注册设备号和cdev
   - 创建设备文件

3. **用户空间交互**
   - 使用copy_to_user/copy_from_user
   - 检查所有用户空间指针
   - 验证所有输入参数

4. **并发控制**
   - 保护共享资源
   - 选择合适的同步机制
   - 避免死锁

5. **调试技巧**
   - printk是最基本的调试方法
   - 使用proc/debugfs暴露内部状态
   - 掌握ftrace和KGDB等高级工具

### 学习建议

**对于初学者**：
1. 从简单的hello模块开始
2. 逐步添加功能
3. 多看内核源码中的示例驱动
4. 在虚拟机或QEMU中测试
5. 保持代码简单清晰

**对于进阶开发者**：
1. 深入学习内核API
2. 研究复杂驱动的实现
3. 学习设备模型和总线驱动
4. 掌握DMA和高级特性
5. 参与开源社区

## 下一步学习

建议按以下顺序继续学习：

### 1. 块设备驱动
- 块设备驱动框架
- 请求队列处理
- 文件系统集成

### 2. 网络设备驱动
- 网络设备驱动框架
- sk_buff处理
- 网络协议栈集成

### 3. 平台设备驱动
- 平台总线和设备
- 资源管理
- 电源管理

### 4. 总线驱动
- I2C驱动开发
- SPI驱动开发
- USB驱动开发

### 5. 高级主题
- DMA操作
- 中断线程化
- 实时性优化
- 驱动移植

## 参考资料

### 官方文档

1. **Linux内核文档**
   - https://www.kernel.org/doc/html/latest/
   - Documentation/driver-api/
   - Documentation/process/coding-style.rst

2. **Linux设备驱动程序（LDD3）**
   - https://lwn.net/Kernel/LDD3/
   - 经典的驱动开发教材

### 推荐书籍

1. **《Linux设备驱动程序》（第3版）**
   - 作者：Jonathan Corbet等
   - 驱动开发圣经

2. **《Linux内核设计与实现》**
   - 作者：Robert Love
   - 深入理解内核机制

3. **《深入Linux设备驱动程序内核机制》**
   - 作者：陈学松
   - 中文驱动开发教材

### 在线资源

1. **Bootlin培训材料**
   - https://bootlin.com/docs/
   - 免费的驱动开发教程

2. **Linux内核邮件列表**
   - https://lkml.org/
   - 驱动开发讨论

3. **Elixir Cross Referencer**
   - https://elixir.bootlin.com/linux/latest/source
   - 在线浏览内核源码

### 示例代码

1. **内核源码drivers目录**
   - drivers/char/ - 字符设备驱动
   - drivers/block/ - 块设备驱动
   - drivers/net/ - 网络设备驱动

2. **GitHub示例**
   - 搜索"linux driver example"
   - 学习他人的实现

## 常见问题解答

### Q1: 驱动开发需要什么基础？

**A**: 
- 扎实的C语言基础（指针、结构体、函数指针）
- Linux系统编程经验
- 操作系统原理知识
- 硬件基础知识
- 耐心和细心

### Q2: 如何选择同步机制？

**A**: 
- **Mutex**：进程上下文，可能睡眠，推荐用于一般情况
- **Spinlock**：中断上下文，不能睡眠，临界区很短
- **Semaphore**：需要计数功能时使用
- **RW Lock**：读多写少的场景

### Q3: 驱动崩溃如何调试？

**A**: 
1. 查看dmesg中的Oops信息
2. 使用addr2line定位代码行
3. 检查空指针和数组越界
4. 使用printk添加调试信息
5. 使用KGDB进行源码级调试

### Q4: 如何提高驱动性能？

**A**: 
- 减少锁的持有时间
- 使用无锁数据结构
- 优化中断处理
- 使用DMA传输大数据
- 避免不必要的内存复制

### Q5: 驱动如何移植到不同平台？

**A**: 
- 使用设备树描述硬件差异
- 抽象硬件相关代码
- 使用平台设备驱动框架
- 测试不同的硬件配置

---

**反馈与支持**：

如果你在学习过程中遇到问题：
- 💬 在评论区留言讨论
- 📧 发送邮件到：support@embedded-platform.com
- 🐛 报告问题：[GitHub Issues](https://github.com/your-repo/issues)

**贡献内容**：
欢迎提交改进建议和补充内容！

---

**版权声明**：本文采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

**最后更新**：2024-01-15  
**文档版本**：1.0
