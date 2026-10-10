---
title: "Android驱动开发实战：深入理解Binder与驱动框架"
description: "全面学习Android驱动开发，掌握Android驱动框架、Binder机制、设备节点管理和权限控制，通过实战项目理解Android驱动的设计与实现"
slug: "android-driver"

# 分类信息
domain: "操作系统层"
module: "Android系统"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Android驱动
  - Binder
  - 驱动开发
  - 设备节点
  - 权限管理
prerequisites:
  - "03-operating-system-layer/06-android-system/intermediate/01-android-hal"
  - "03-operating-system-layer/05-embedded-linux/intermediate/01-linux-driver-basics"
related_contents:
  - "03-operating-system-layer/06-android-system/beginner/01-android-architecture"
  - "03-operating-system-layer/05-embedded-linux/beginner/03-device-tree"

# 学习信息
estimated_time: 90
difficulty_score: 7

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
  - Android驱动开发
  - Binder机制
  - 驱动框架
  - 设备节点管理
  - SELinux权限
cover_image: ""
---

# Android驱动开发实战：深入理解Binder与驱动框架


## 学习目标

完成本教程后，你将能够：

- [ ] 理解Android驱动框架的整体架构
- [ ] 掌握Binder驱动的工作原理和通信机制
- [ ] 学会开发Android字符设备驱动
- [ ] 掌握设备节点的创建和管理
- [ ] 理解SELinux权限配置和管理
- [ ] 掌握Android驱动的调试方法
- [ ] 能够集成驱动到Android系统
- [ ] 完成一个完整的Android驱动开发项目

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言编程
- 了解Linux内核驱动开发基础
- 理解Android系统架构
- 掌握HAL层开发知识
- 了解进程间通信机制

**技能要求**：
- 能够编写Linux内核模块
- 会使用内核调试工具
- 熟悉Android开发环境
- 了解设备树配置
- 能够阅读内核日志

**开发环境**：
- Ubuntu 18.04或更高版本
- Android内核源码
- 交叉编译工具链
- ADB调试工具
- 内核调试工具（kgdb、ftrace等）

## Android驱动框架概述

### Android驱动的特点

Android驱动在标准Linux驱动基础上，增加了一些Android特有的机制和要求。


**Android驱动架构图**：

```
┌─────────────────────────────────────────────────┐
│    Android Framework (Java)                     │
│    SystemService, Manager Classes                │
└─────────────────────────────────────────────────┘
                        ↕ Binder IPC
┌─────────────────────────────────────────────────┐
│    Native Services (C/C++)                       │
│    ServiceManager, Native Daemons                │
└─────────────────────────────────────────────────┘
                        ↕ HAL Interface
┌─────────────────────────────────────────────────┐
│    HAL Layer (Vendor Specific)                   │
│    Hardware Abstraction Layer                    │
└─────────────────────────────────────────────────┘
                        ↕ ioctl/read/write
┌─────────────────────────────────────────────────┐
│    Kernel Drivers                                │
│    Character Device, Platform Device             │
│    ┌──────────────┐  ┌──────────────┐          │
│    │ Binder Driver│  │ Custom Driver│          │
│    └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Hardware                                      │
└─────────────────────────────────────────────────┘
```

**Android驱动的关键特性**：

1. **Binder IPC机制**
   - Android特有的进程间通信机制
   - 高效的数据传输
   - 支持同步和异步调用
   - 内置安全机制

2. **SELinux权限控制**
   - 强制访问控制（MAC）
   - 细粒度的权限管理
   - 设备节点访问控制
   - 进程隔离和保护

3. **设备节点管理**
   - ueventd自动创建设备节点
   - 统一的设备节点命名规范
   - 权限和所有者配置
   - 动态设备管理

4. **电源管理集成**
   - Wakelock机制
   - 休眠唤醒支持
   - 低功耗模式
   - 电源状态通知


### Android驱动类型

**1. 字符设备驱动**
- 最常用的驱动类型
- 提供字节流访问接口
- 支持read/write/ioctl操作
- 适用于传感器、LED、GPIO等

**2. 平台设备驱动**
- 基于设备树的驱动模型
- 自动设备匹配和绑定
- 支持热插拔
- 适用于SoC集成外设

**3. Binder驱动**
- Android IPC核心驱动
- 内核态实现
- 支持进程间通信
- 提供安全机制

**4. 输入设备驱动**
- 触摸屏、按键、传感器
- 使用input子系统
- 事件上报机制
- 多点触控支持

**5. 显示驱动**
- Framebuffer驱动
- DRM/KMS驱动
- 图形加速支持
- 多显示器支持

## Binder驱动深入解析

Binder是Android系统中最重要的驱动之一，是Android IPC机制的核心。

### Binder驱动架构

**Binder通信模型**：

```
Client进程                    Server进程
    │                            │
    │  1. 打开/dev/binder        │
    ├──────────────────────────►│
    │                            │
    │  2. mmap映射内存           │
    ├──────────────────────────►│
    │                            │
    │  3. ioctl(BINDER_WRITE_READ)
    ├──────────────────────────►│
    │                            │
    │     Binder驱动             │
    │  ┌──────────────────┐     │
    │  │  数据拷贝        │     │
    │  │  权限检查        │     │
    │  │  线程调度        │     │
    │  │  内存管理        │     │
    │  └──────────────────┘     │
    │                            │
    │  4. 唤醒Server线程         │
    │                            ├──►处理请求
    │                            │
    │  5. 返回结果               │
    │◄───────────────────────────┤
```


### Binder驱动核心数据结构

**1. binder_proc - 进程结构**

```c
/**
 * Binder进程结构
 * 每个使用Binder的进程都有一个binder_proc结构
 */
struct binder_proc {
    struct hlist_node proc_node;      // 全局进程链表节点
    struct rb_root threads;           // 进程的线程红黑树
    struct rb_root nodes;             // Binder节点红黑树
    struct rb_root refs_by_desc;      // 引用描述符红黑树
    struct rb_root refs_by_node;      // 引用节点红黑树
    
    int pid;                          // 进程ID
    struct task_struct *tsk;          // 进程task结构
    
    struct vm_area_struct *vma;       // mmap映射区域
    struct mm_struct *vma_vm_mm;      // 内存管理结构
    
    void *buffer;                     // 内核缓冲区地址
    size_t buffer_size;               // 缓冲区大小
    
    struct list_head buffers;         // 缓冲区链表
    struct rb_root free_buffers;      // 空闲缓冲区红黑树
    struct rb_root allocated_buffers; // 已分配缓冲区红黑树
    
    int max_threads;                  // 最大线程数
    int requested_threads;            // 请求的线程数
    int requested_threads_started;    // 已启动的线程数
    int ready_threads;                // 就绪线程数
    
    long default_priority;            // 默认优先级
};
```

**2. binder_thread - 线程结构**

```c
/**
 * Binder线程结构
 * 每个参与Binder通信的线程都有一个binder_thread结构
 */
struct binder_thread {
    struct binder_proc *proc;         // 所属进程
    struct rb_node rb_node;           // 红黑树节点
    int pid;                          // 线程ID
    
    int looper;                       // 线程状态标志
    struct binder_transaction *transaction_stack; // 事务栈
    struct list_head todo;            // 待处理工作队列
    
    uint32_t return_error;            // 返回错误码
    uint32_t return_error2;           // 第二个错误码
    
    wait_queue_head_t wait;           // 等待队列
    struct binder_stats stats;        // 统计信息
};
```

**3. binder_node - Binder实体节点**

```c
/**
 * Binder实体节点
 * 代表一个Binder服务对象
 */
struct binder_node {
    int debug_id;                     // 调试ID
    struct binder_work work;          // 工作项
    
    union {
        struct rb_node rb_node;       // 红黑树节点
        struct hlist_node dead_node;  // 死亡节点
    };
    
    struct binder_proc *proc;         // 所属进程
    struct hlist_head refs;           // 引用链表
    
    int internal_strong_refs;         // 内部强引用计数
    int local_weak_refs;              // 本地弱引用计数
    int local_strong_refs;            // 本地强引用计数
    
    binder_uintptr_t ptr;             // 用户空间指针
    binder_uintptr_t cookie;          // 用户空间cookie
    
    unsigned has_strong_ref:1;        // 是否有强引用
    unsigned pending_strong_ref:1;    // 是否有待处理的强引用
    unsigned has_weak_ref:1;          // 是否有弱引用
    unsigned pending_weak_ref:1;      // 是否有待处理的弱引用
    
    unsigned has_async_transaction:1; // 是否有异步事务
    unsigned accept_fds:1;            // 是否接受文件描述符
    
    int min_priority;                 // 最小优先级
    struct list_head async_todo;      // 异步待处理队列
};
```


**4. binder_transaction - 事务结构**

```c
/**
 * Binder事务结构
 * 代表一次Binder调用
 */
struct binder_transaction {
    int debug_id;                     // 调试ID
    struct binder_work work;          // 工作项
    
    struct binder_thread *from;       // 发起线程
    struct binder_transaction *from_parent; // 父事务
    
    struct binder_proc *to_proc;      // 目标进程
    struct binder_thread *to_thread;  // 目标线程
    struct binder_transaction *to_parent; // 目标父事务
    
    unsigned need_reply:1;            // 是否需要回复
    unsigned is_dead:1;               // 是否已死亡
    
    struct binder_buffer *buffer;     // 数据缓冲区
    unsigned int code;                // 事务代码
    unsigned int flags;               // 事务标志
    
    long priority;                    // 优先级
    long saved_priority;              // 保存的优先级
    
    kuid_t sender_euid;               // 发送者UID
};
```

### Binder驱动主要操作

**1. 打开设备**

```c
static int binder_open(struct inode *nodp, struct file *filp)
{
    struct binder_proc *proc;
    
    // 分配进程结构
    proc = kzalloc(sizeof(*proc), GFP_KERNEL);
    if (proc == NULL)
        return -ENOMEM;
    
    // 初始化进程结构
    get_task_struct(current);
    proc->tsk = current;
    proc->pid = current->group_leader->pid;
    
    INIT_LIST_HEAD(&proc->todo);
    init_waitqueue_head(&proc->wait);
    proc->default_priority = task_nice(current);
    
    // 初始化红黑树
    proc->threads = RB_ROOT;
    proc->nodes = RB_ROOT;
    proc->refs_by_desc = RB_ROOT;
    proc->refs_by_node = RB_ROOT;
    
    // 添加到全局进程列表
    binder_lock(__func__);
    hlist_add_head(&proc->proc_node, &binder_procs);
    binder_unlock(__func__);
    
    // 保存到文件私有数据
    filp->private_data = proc;
    
    return 0;
}
```

**2. 内存映射**

```c
static int binder_mmap(struct file *filp, struct vm_area_struct *vma)
{
    int ret;
    struct binder_proc *proc = filp->private_data;
    const char *failure_string;
    struct binder_buffer *buffer;
    
    // 检查映射大小
    if ((vma->vm_end - vma->vm_start) > SZ_4M)
        vma->vm_end = vma->vm_start + SZ_4M;
    
    // 检查是否已经映射
    if (proc->buffer) {
        ret = -EBUSY;
        failure_string = "already mapped";
        goto err_already_mapped;
    }
    
    // 分配内核缓冲区
    proc->buffer = kzalloc(vma->vm_end - vma->vm_start, GFP_KERNEL);
    if (!proc->buffer) {
        ret = -ENOMEM;
        failure_string = "alloc buffer failed";
        goto err_alloc_buffer_failed;
    }
    
    proc->buffer_size = vma->vm_end - vma->vm_start;
    
    // 设置VMA属性
    vma->vm_flags = (vma->vm_flags | VM_DONTCOPY) & ~VM_MAYWRITE;
    vma->vm_ops = &binder_vm_ops;
    vma->vm_private_data = proc;
    
    // 初始化缓冲区管理
    proc->free_buffers = RB_ROOT;
    proc->allocated_buffers = RB_ROOT;
    INIT_LIST_HEAD(&proc->buffers);
    
    // 创建初始空闲缓冲区
    buffer = kzalloc(sizeof(*buffer), GFP_KERNEL);
    if (!buffer) {
        ret = -ENOMEM;
        failure_string = "alloc buffer struct failed";
        goto err_alloc_buf_struct_failed;
    }
    
    buffer->data = proc->buffer;
    buffer->data_size = proc->buffer_size;
    list_add(&buffer->entry, &proc->buffers);
    buffer->free = 1;
    binder_insert_free_buffer(proc, buffer);
    
    return 0;
    
err_alloc_buf_struct_failed:
    kfree(proc->buffer);
    proc->buffer = NULL;
err_alloc_buffer_failed:
err_already_mapped:
    return ret;
}
```


**3. ioctl操作**

```c
static long binder_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    int ret;
    struct binder_proc *proc = filp->private_data;
    struct binder_thread *thread;
    unsigned int size = _IOC_SIZE(cmd);
    void __user *ubuf = (void __user *)arg;
    
    // 获取或创建线程结构
    thread = binder_get_thread(proc);
    if (thread == NULL) {
        ret = -ENOMEM;
        goto err;
    }
    
    switch (cmd) {
    case BINDER_WRITE_READ: {
        struct binder_write_read bwr;
        
        // 从用户空间拷贝数据
        if (copy_from_user(&bwr, ubuf, sizeof(bwr))) {
            ret = -EFAULT;
            goto err;
        }
        
        // 处理写操作
        if (bwr.write_size > 0) {
            ret = binder_thread_write(proc, thread,
                                     bwr.write_buffer,
                                     bwr.write_size,
                                     &bwr.write_consumed);
            if (ret < 0) {
                bwr.read_consumed = 0;
                if (copy_to_user(ubuf, &bwr, sizeof(bwr)))
                    ret = -EFAULT;
                goto err;
            }
        }
        
        // 处理读操作
        if (bwr.read_size > 0) {
            ret = binder_thread_read(proc, thread,
                                    bwr.read_buffer,
                                    bwr.read_size,
                                    &bwr.read_consumed,
                                    filp->f_flags & O_NONBLOCK);
            if (!list_empty(&proc->todo))
                wake_up_interruptible(&proc->wait);
            if (ret < 0) {
                if (copy_to_user(ubuf, &bwr, sizeof(bwr)))
                    ret = -EFAULT;
                goto err;
            }
        }
        
        // 拷贝结果到用户空间
        if (copy_to_user(ubuf, &bwr, sizeof(bwr))) {
            ret = -EFAULT;
            goto err;
        }
        break;
    }
    
    case BINDER_SET_MAX_THREADS:
        if (copy_from_user(&proc->max_threads, ubuf, sizeof(proc->max_threads))) {
            ret = -EINVAL;
            goto err;
        }
        break;
    
    case BINDER_SET_CONTEXT_MGR:
        ret = binder_ioctl_set_ctx_mgr(filp);
        if (ret)
            goto err;
        break;
    
    case BINDER_THREAD_EXIT:
        binder_free_thread(proc, thread);
        thread = NULL;
        break;
    
    case BINDER_VERSION: {
        struct binder_version __user *ver = ubuf;
        if (put_user(BINDER_CURRENT_PROTOCOL_VERSION, &ver->protocol_version)) {
            ret = -EINVAL;
            goto err;
        }
        break;
    }
    
    default:
        ret = -EINVAL;
        goto err;
    }
    
    ret = 0;
err:
    if (thread)
        thread->looper &= ~BINDER_LOOPER_STATE_NEED_RETURN;
    return ret;
}
```

### Binder通信流程

**完整的Binder调用流程**：

1. **Client端发起调用**
   ```c
   // 1. 打开Binder设备
   int fd = open("/dev/binder", O_RDWR);
   
   // 2. 映射内存
   void *mapped = mmap(NULL, BINDER_VM_SIZE, PROT_READ,
                       MAP_PRIVATE | MAP_NORESERVE, fd, 0);
   
   // 3. 构造事务数据
   struct binder_write_read bwr;
   struct binder_transaction_data tr;
   
   tr.target.handle = service_handle;
   tr.code = TRANSACTION_CODE;
   tr.flags = TF_ACCEPT_FDS;
   tr.data_size = data_len;
   tr.data.ptr.buffer = data_buffer;
   
   // 4. 发送请求
   ioctl(fd, BINDER_WRITE_READ, &bwr);
   ```

2. **Binder驱动处理**
   - 查找目标进程和线程
   - 分配内核缓冲区
   - 拷贝数据（只拷贝一次）
   - 唤醒目标线程
   - 阻塞等待回复

3. **Server端处理**
   ```c
   // 1. 等待请求
   ioctl(fd, BINDER_WRITE_READ, &bwr);
   
   // 2. 处理请求
   handle_transaction(&tr);
   
   // 3. 发送回复
   struct binder_transaction_data reply;
   reply.target.handle = 0;
   reply.code = BC_REPLY;
   reply.data_size = reply_len;
   reply.data.ptr.buffer = reply_buffer;
   
   ioctl(fd, BINDER_WRITE_READ, &bwr);
   ```

4. **返回结果给Client**
   - 唤醒Client线程
   - 拷贝返回数据
   - 释放内核缓冲区


## 实战项目：开发Android字符设备驱动

现在我们通过一个完整的实例来学习Android驱动开发。我们将实现一个温度传感器驱动。

### 项目需求

**功能需求**：
1. 读取温度传感器数据
2. 设置温度阈值
3. 温度超限告警
4. 支持多个传感器
5. 电源管理支持

**系统架构**：
```
Java应用
    ↓ Binder
SystemService
    ↓ JNI
Native Service
    ↓ HAL
Temperature HAL
    ↓ ioctl
Temperature Driver
    ↓ I2C/SPI
Temperature Sensor
```

### 步骤1：定义驱动接口

**文件：drivers/misc/temp_sensor.h**

```c
#ifndef _TEMP_SENSOR_H_
#define _TEMP_SENSOR_H_

#include <linux/ioctl.h>

/**
 * 温度数据结构
 */
struct temp_data {
    int sensor_id;        // 传感器ID
    int temperature;      // 温度值（摄氏度 * 100）
    unsigned long timestamp; // 时间戳
};

/**
 * 温度阈值结构
 */
struct temp_threshold {
    int sensor_id;        // 传感器ID
    int high_threshold;   // 高温阈值
    int low_threshold;    // 低温阈值
};

/**
 * 传感器信息结构
 */
struct sensor_info {
    int sensor_id;        // 传感器ID
    char name[32];        // 传感器名称
    int min_temp;         // 最小温度
    int max_temp;         // 最大温度
    int resolution;       // 分辨率
};

/**
 * ioctl命令定义
 */
#define TEMP_IOC_MAGIC  'T'

#define TEMP_IOC_GET_TEMP       _IOR(TEMP_IOC_MAGIC, 1, struct temp_data)
#define TEMP_IOC_SET_THRESHOLD  _IOW(TEMP_IOC_MAGIC, 2, struct temp_threshold)
#define TEMP_IOC_GET_THRESHOLD  _IOR(TEMP_IOC_MAGIC, 3, struct temp_threshold)
#define TEMP_IOC_GET_INFO       _IOR(TEMP_IOC_MAGIC, 4, struct sensor_info)
#define TEMP_IOC_ENABLE_ALERT   _IOW(TEMP_IOC_MAGIC, 5, int)
#define TEMP_IOC_GET_COUNT      _IOR(TEMP_IOC_MAGIC, 6, int)

#define TEMP_IOC_MAXNR  6

#endif /* _TEMP_SENSOR_H_ */
```


### 步骤2：实现驱动核心功能

**文件：drivers/misc/temp_sensor.c**

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/i2c.h>
#include <linux/delay.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/platform_device.h>
#include <linux/wakelock.h>

#include "temp_sensor.h"

#define DRIVER_NAME "temp_sensor"
#define MAX_SENSORS 4

/**
 * 传感器设备结构
 */
struct temp_sensor_dev {
    int sensor_id;
    struct i2c_client *client;
    struct temp_data current_data;
    struct temp_threshold threshold;
    bool alert_enabled;
    int alert_gpio;
    int alert_irq;
    struct work_struct alert_work;
};

/**
 * 驱动私有数据
 */
struct temp_driver_data {
    dev_t devno;
    struct cdev cdev;
    struct class *class;
    struct device *device;
    
    struct temp_sensor_dev *sensors[MAX_SENSORS];
    int sensor_count;
    
    struct mutex lock;
    struct wake_lock wake_lock;
};

static struct temp_driver_data *g_driver_data = NULL;

/**
 * 从I2C读取温度
 */
static int temp_sensor_read_i2c(struct temp_sensor_dev *sensor)
{
    struct i2c_client *client = sensor->client;
    u8 buf[2];
    int ret;
    s16 raw_temp;
    
    // 读取温度寄存器
    ret = i2c_master_recv(client, buf, 2);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to read temperature: %d\n", ret);
        return ret;
    }
    
    // 转换为温度值
    raw_temp = (buf[0] << 8) | buf[1];
    sensor->current_data.temperature = (raw_temp * 625) / 100; // 转换为摄氏度*100
    sensor->current_data.timestamp = jiffies;
    
    return 0;
}

/**
 * 设置温度阈值
 */
static int temp_sensor_set_threshold(struct temp_sensor_dev *sensor,
                                    struct temp_threshold *threshold)
{
    struct i2c_client *client = sensor->client;
    u8 buf[3];
    int ret;
    
    // 设置高温阈值
    buf[0] = 0x02; // 高温阈值寄存器
    buf[1] = (threshold->high_threshold * 100 / 625) >> 8;
    buf[2] = (threshold->high_threshold * 100 / 625) & 0xFF;
    
    ret = i2c_master_send(client, buf, 3);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to set high threshold: %d\n", ret);
        return ret;
    }
    
    // 设置低温阈值
    buf[0] = 0x03; // 低温阈值寄存器
    buf[1] = (threshold->low_threshold * 100 / 625) >> 8;
    buf[2] = (threshold->low_threshold * 100 / 625) & 0xFF;
    
    ret = i2c_master_send(client, buf, 3);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to set low threshold: %d\n", ret);
        return ret;
    }
    
    // 保存阈值
    memcpy(&sensor->threshold, threshold, sizeof(*threshold));
    
    return 0;
}

/**
 * 告警中断处理
 */
static irqreturn_t temp_sensor_alert_irq(int irq, void *dev_id)
{
    struct temp_sensor_dev *sensor = dev_id;
    
    // 获取wakelock，防止系统休眠
    wake_lock_timeout(&g_driver_data->wake_lock, HZ * 5);
    
    // 调度工作队列处理
    schedule_work(&sensor->alert_work);
    
    return IRQ_HANDLED;
}

/**
 * 告警工作队列处理函数
 */
static void temp_sensor_alert_work(struct work_struct *work)
{
    struct temp_sensor_dev *sensor = container_of(work,
                                                  struct temp_sensor_dev,
                                                  alert_work);
    int ret;
    
    // 读取当前温度
    ret = temp_sensor_read_i2c(sensor);
    if (ret < 0) {
        dev_err(&sensor->client->dev, "Failed to read temperature in alert\n");
        return;
    }
    
    // 发送uevent通知用户空间
    char *envp[] = {
        "TEMP_ALERT=1",
        NULL
    };
    kobject_uevent_env(&g_driver_data->device->kobj, KOBJ_CHANGE, envp);
    
    dev_info(&sensor->client->dev, "Temperature alert: %d.%02d°C\n",
             sensor->current_data.temperature / 100,
             sensor->current_data.temperature % 100);
}
```


/**
 * 打开设备
 */
static int temp_sensor_open(struct inode *inode, struct file *filp)
{
    filp->private_data = g_driver_data;
    return 0;
}

/**
 * 关闭设备
 */
static int temp_sensor_release(struct inode *inode, struct file *filp)
{
    return 0;
}

/**
 * 读取设备
 */
static ssize_t temp_sensor_read(struct file *filp, char __user *buf,
                               size_t count, loff_t *f_pos)
{
    struct temp_driver_data *data = filp->private_data;
    struct temp_data temp;
    int ret;
    
    if (count < sizeof(struct temp_data))
        return -EINVAL;
    
    mutex_lock(&data->lock);
    
    // 读取第一个传感器的温度
    if (data->sensor_count > 0) {
        ret = temp_sensor_read_i2c(data->sensors[0]);
        if (ret < 0) {
            mutex_unlock(&data->lock);
            return ret;
        }
        
        memcpy(&temp, &data->sensors[0]->current_data, sizeof(temp));
    } else {
        mutex_unlock(&data->lock);
        return -ENODEV;
    }
    
    mutex_unlock(&data->lock);
    
    // 拷贝到用户空间
    if (copy_to_user(buf, &temp, sizeof(temp)))
        return -EFAULT;
    
    return sizeof(temp);
}

/**
 * ioctl操作
 */
static long temp_sensor_ioctl(struct file *filp, unsigned int cmd,
                             unsigned long arg)
{
    struct temp_driver_data *data = filp->private_data;
    struct temp_sensor_dev *sensor;
    int ret = 0;
    
    // 检查命令有效性
    if (_IOC_TYPE(cmd) != TEMP_IOC_MAGIC)
        return -ENOTTY;
    if (_IOC_NR(cmd) > TEMP_IOC_MAXNR)
        return -ENOTTY;
    
    mutex_lock(&data->lock);
    
    switch (cmd) {
    case TEMP_IOC_GET_TEMP: {
        struct temp_data temp;
        
        if (copy_from_user(&temp, (void __user *)arg, sizeof(temp))) {
            ret = -EFAULT;
            break;
        }
        
        // 检查传感器ID
        if (temp.sensor_id >= data->sensor_count) {
            ret = -EINVAL;
            break;
        }
        
        sensor = data->sensors[temp.sensor_id];
        
        // 读取温度
        ret = temp_sensor_read_i2c(sensor);
        if (ret < 0)
            break;
        
        // 拷贝到用户空间
        if (copy_to_user((void __user *)arg, &sensor->current_data,
                        sizeof(sensor->current_data))) {
            ret = -EFAULT;
        }
        break;
    }
    
    case TEMP_IOC_SET_THRESHOLD: {
        struct temp_threshold threshold;
        
        if (copy_from_user(&threshold, (void __user *)arg, sizeof(threshold))) {
            ret = -EFAULT;
            break;
        }
        
        // 检查传感器ID
        if (threshold.sensor_id >= data->sensor_count) {
            ret = -EINVAL;
            break;
        }
        
        sensor = data->sensors[threshold.sensor_id];
        
        // 设置阈值
        ret = temp_sensor_set_threshold(sensor, &threshold);
        break;
    }
    
    case TEMP_IOC_GET_THRESHOLD: {
        struct temp_threshold threshold;
        
        if (copy_from_user(&threshold, (void __user *)arg, sizeof(threshold))) {
            ret = -EFAULT;
            break;
        }
        
        // 检查传感器ID
        if (threshold.sensor_id >= data->sensor_count) {
            ret = -EINVAL;
            break;
        }
        
        sensor = data->sensors[threshold.sensor_id];
        
        // 拷贝到用户空间
        if (copy_to_user((void __user *)arg, &sensor->threshold,
                        sizeof(sensor->threshold))) {
            ret = -EFAULT;
        }
        break;
    }
    
    case TEMP_IOC_GET_INFO: {
        struct sensor_info info;
        
        if (copy_from_user(&info, (void __user *)arg, sizeof(info))) {
            ret = -EFAULT;
            break;
        }
        
        // 检查传感器ID
        if (info.sensor_id >= data->sensor_count) {
            ret = -EINVAL;
            break;
        }
        
        sensor = data->sensors[info.sensor_id];
        
        // 填充传感器信息
        info.sensor_id = sensor->sensor_id;
        snprintf(info.name, sizeof(info.name), "TempSensor%d", sensor->sensor_id);
        info.min_temp = -4000;  // -40°C
        info.max_temp = 12500;  // 125°C
        info.resolution = 6;    // 0.0625°C
        
        // 拷贝到用户空间
        if (copy_to_user((void __user *)arg, &info, sizeof(info))) {
            ret = -EFAULT;
        }
        break;
    }
    
    case TEMP_IOC_ENABLE_ALERT: {
        int sensor_id;
        
        if (copy_from_user(&sensor_id, (void __user *)arg, sizeof(sensor_id))) {
            ret = -EFAULT;
            break;
        }
        
        // 检查传感器ID
        if (sensor_id >= data->sensor_count) {
            ret = -EINVAL;
            break;
        }
        
        sensor = data->sensors[sensor_id];
        sensor->alert_enabled = true;
        
        // 使能中断
        if (sensor->alert_irq > 0)
            enable_irq(sensor->alert_irq);
        
        break;
    }
    
    case TEMP_IOC_GET_COUNT: {
        if (copy_to_user((void __user *)arg, &data->sensor_count,
                        sizeof(data->sensor_count))) {
            ret = -EFAULT;
        }
        break;
    }
    
    default:
        ret = -ENOTTY;
        break;
    }
    
    mutex_unlock(&data->lock);
    return ret;
}

/**
 * 文件操作结构
 */
static const struct file_operations temp_sensor_fops = {
    .owner = THIS_MODULE,
    .open = temp_sensor_open,
    .release = temp_sensor_release,
    .read = temp_sensor_read,
    .unlocked_ioctl = temp_sensor_ioctl,
    .compat_ioctl = temp_sensor_ioctl,
};
```


### 步骤3：实现平台设备驱动

```c
/**
 * I2C设备探测
 */
static int temp_sensor_i2c_probe(struct i2c_client *client,
                                const struct i2c_device_id *id)
{
    struct temp_sensor_dev *sensor;
    struct device_node *np = client->dev.of_node;
    int ret;
    
    dev_info(&client->dev, "Probing temperature sensor\n");
    
    // 分配传感器设备结构
    sensor = devm_kzalloc(&client->dev, sizeof(*sensor), GFP_KERNEL);
    if (!sensor)
        return -ENOMEM;
    
    sensor->client = client;
    sensor->sensor_id = g_driver_data->sensor_count;
    
    // 从设备树读取GPIO配置
    sensor->alert_gpio = of_get_named_gpio(np, "alert-gpio", 0);
    if (gpio_is_valid(sensor->alert_gpio)) {
        ret = devm_gpio_request_one(&client->dev, sensor->alert_gpio,
                                   GPIOF_IN, "temp_alert");
        if (ret < 0) {
            dev_err(&client->dev, "Failed to request alert GPIO: %d\n", ret);
            return ret;
        }
        
        // 申请中断
        sensor->alert_irq = gpio_to_irq(sensor->alert_gpio);
        if (sensor->alert_irq > 0) {
            INIT_WORK(&sensor->alert_work, temp_sensor_alert_work);
            
            ret = devm_request_irq(&client->dev, sensor->alert_irq,
                                  temp_sensor_alert_irq,
                                  IRQF_TRIGGER_FALLING,
                                  "temp_alert", sensor);
            if (ret < 0) {
                dev_err(&client->dev, "Failed to request IRQ: %d\n", ret);
                return ret;
            }
            
            // 默认禁用中断
            disable_irq(sensor->alert_irq);
        }
    }
    
    // 初始化传感器
    sensor->threshold.sensor_id = sensor->sensor_id;
    sensor->threshold.high_threshold = 8000;  // 80°C
    sensor->threshold.low_threshold = 0;      // 0°C
    sensor->alert_enabled = false;
    
    // 添加到传感器列表
    mutex_lock(&g_driver_data->lock);
    if (g_driver_data->sensor_count < MAX_SENSORS) {
        g_driver_data->sensors[g_driver_data->sensor_count] = sensor;
        g_driver_data->sensor_count++;
    } else {
        mutex_unlock(&g_driver_data->lock);
        dev_err(&client->dev, "Too many sensors\n");
        return -ENOSPC;
    }
    mutex_unlock(&g_driver_data->lock);
    
    i2c_set_clientdata(client, sensor);
    
    dev_info(&client->dev, "Temperature sensor %d probed successfully\n",
             sensor->sensor_id);
    
    return 0;
}

/**
 * I2C设备移除
 */
static int temp_sensor_i2c_remove(struct i2c_client *client)
{
    struct temp_sensor_dev *sensor = i2c_get_clientdata(client);
    int i;
    
    // 从传感器列表中移除
    mutex_lock(&g_driver_data->lock);
    for (i = 0; i < g_driver_data->sensor_count; i++) {
        if (g_driver_data->sensors[i] == sensor) {
            g_driver_data->sensors[i] = NULL;
            break;
        }
    }
    mutex_unlock(&g_driver_data->lock);
    
    // 取消工作队列
    if (sensor->alert_irq > 0)
        cancel_work_sync(&sensor->alert_work);
    
    dev_info(&client->dev, "Temperature sensor removed\n");
    
    return 0;
}

/**
 * 设备树匹配表
 */
static const struct of_device_id temp_sensor_of_match[] = {
    { .compatible = "vendor,temp-sensor" },
    { }
};
MODULE_DEVICE_TABLE(of, temp_sensor_of_match);

/**
 * I2C设备ID表
 */
static const struct i2c_device_id temp_sensor_i2c_id[] = {
    { "temp_sensor", 0 },
    { }
};
MODULE_DEVICE_TABLE(i2c, temp_sensor_i2c_id);

/**
 * I2C驱动结构
 */
static struct i2c_driver temp_sensor_i2c_driver = {
    .driver = {
        .name = DRIVER_NAME,
        .owner = THIS_MODULE,
        .of_match_table = temp_sensor_of_match,
    },
    .probe = temp_sensor_i2c_probe,
    .remove = temp_sensor_i2c_remove,
    .id_table = temp_sensor_i2c_id,
};
```


### 步骤4：实现电源管理

```c
#ifdef CONFIG_PM
/**
 * 挂起操作
 */
static int temp_sensor_suspend(struct device *dev)
{
    struct i2c_client *client = to_i2c_client(dev);
    struct temp_sensor_dev *sensor = i2c_get_clientdata(client);
    
    dev_info(dev, "Suspending temperature sensor %d\n", sensor->sensor_id);
    
    // 禁用中断
    if (sensor->alert_enabled && sensor->alert_irq > 0)
        disable_irq(sensor->alert_irq);
    
    // 可以在这里关闭传感器电源
    
    return 0;
}

/**
 * 恢复操作
 */
static int temp_sensor_resume(struct device *dev)
{
    struct i2c_client *client = to_i2c_client(dev);
    struct temp_sensor_dev *sensor = i2c_get_clientdata(client);
    
    dev_info(dev, "Resuming temperature sensor %d\n", sensor->sensor_id);
    
    // 可以在这里重新打开传感器电源
    
    // 重新使能中断
    if (sensor->alert_enabled && sensor->alert_irq > 0)
        enable_irq(sensor->alert_irq);
    
    return 0;
}

static const struct dev_pm_ops temp_sensor_pm_ops = {
    .suspend = temp_sensor_suspend,
    .resume = temp_sensor_resume,
};
#endif

/**
 * 模块初始化
 */
static int __init temp_sensor_init(void)
{
    int ret;
    
    pr_info("Temperature sensor driver initializing\n");
    
    // 分配驱动数据
    g_driver_data = kzalloc(sizeof(*g_driver_data), GFP_KERNEL);
    if (!g_driver_data)
        return -ENOMEM;
    
    // 初始化互斥锁
    mutex_init(&g_driver_data->lock);
    
    // 初始化wakelock
    wake_lock_init(&g_driver_data->wake_lock, WAKE_LOCK_SUSPEND,
                  "temp_sensor_wakelock");
    
    // 分配设备号
    ret = alloc_chrdev_region(&g_driver_data->devno, 0, 1, DRIVER_NAME);
    if (ret < 0) {
        pr_err("Failed to allocate device number: %d\n", ret);
        goto err_alloc_chrdev;
    }
    
    // 初始化字符设备
    cdev_init(&g_driver_data->cdev, &temp_sensor_fops);
    g_driver_data->cdev.owner = THIS_MODULE;
    
    // 添加字符设备
    ret = cdev_add(&g_driver_data->cdev, g_driver_data->devno, 1);
    if (ret < 0) {
        pr_err("Failed to add character device: %d\n", ret);
        goto err_cdev_add;
    }
    
    // 创建设备类
    g_driver_data->class = class_create(THIS_MODULE, DRIVER_NAME);
    if (IS_ERR(g_driver_data->class)) {
        ret = PTR_ERR(g_driver_data->class);
        pr_err("Failed to create device class: %d\n", ret);
        goto err_class_create;
    }
    
    // 创建设备节点
    g_driver_data->device = device_create(g_driver_data->class, NULL,
                                         g_driver_data->devno, NULL,
                                         DRIVER_NAME);
    if (IS_ERR(g_driver_data->device)) {
        ret = PTR_ERR(g_driver_data->device);
        pr_err("Failed to create device: %d\n", ret);
        goto err_device_create;
    }
    
    // 注册I2C驱动
    ret = i2c_add_driver(&temp_sensor_i2c_driver);
    if (ret < 0) {
        pr_err("Failed to register I2C driver: %d\n", ret);
        goto err_i2c_add_driver;
    }
    
    pr_info("Temperature sensor driver initialized successfully\n");
    return 0;
    
err_i2c_add_driver:
    device_destroy(g_driver_data->class, g_driver_data->devno);
err_device_create:
    class_destroy(g_driver_data->class);
err_class_create:
    cdev_del(&g_driver_data->cdev);
err_cdev_add:
    unregister_chrdev_region(g_driver_data->devno, 1);
err_alloc_chrdev:
    wake_lock_destroy(&g_driver_data->wake_lock);
    kfree(g_driver_data);
    return ret;
}

/**
 * 模块退出
 */
static void __exit temp_sensor_exit(void)
{
    pr_info("Temperature sensor driver exiting\n");
    
    // 注销I2C驱动
    i2c_del_driver(&temp_sensor_i2c_driver);
    
    // 销毁设备
    device_destroy(g_driver_data->class, g_driver_data->devno);
    class_destroy(g_driver_data->class);
    
    // 删除字符设备
    cdev_del(&g_driver_data->cdev);
    
    // 释放设备号
    unregister_chrdev_region(g_driver_data->devno, 1);
    
    // 销毁wakelock
    wake_lock_destroy(&g_driver_data->wake_lock);
    
    // 释放驱动数据
    kfree(g_driver_data);
    
    pr_info("Temperature sensor driver exited\n");
}

module_init(temp_sensor_init);
module_exit(temp_sensor_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Embedded Platform");
MODULE_DESCRIPTION("Temperature Sensor Driver for Android");
MODULE_VERSION("1.0");
```


### 步骤5：配置设备树

**文件：arch/arm64/boot/dts/vendor/board.dts**

```dts
/ {
    /* I2C总线配置 */
    i2c@78b6000 {
        compatible = "qcom,i2c-msm-v2";
        #address-cells = <1>;
        #size-cells = <0>;
        reg = <0x78b6000 0x1000>;
        interrupts = <0 96 0>;
        clocks = <&clock_gcc clk_gcc_blsp1_ahb_clk>,
                 <&clock_gcc clk_gcc_blsp1_qup2_i2c_apps_clk>;
        clock-names = "iface_clk", "core_clk";
        
        /* 温度传感器设备 */
        temp_sensor@48 {
            compatible = "vendor,temp-sensor";
            reg = <0x48>;
            
            /* 告警GPIO配置 */
            alert-gpio = <&tlmm 42 0>;
            
            /* 中断配置 */
            interrupt-parent = <&tlmm>;
            interrupts = <42 IRQ_TYPE_EDGE_FALLING>;
            
            /* 电源配置 */
            vdd-supply = <&pm8953_l10>;
            vio-supply = <&pm8953_l5>;
            
            /* 其他配置 */
            sensor-id = <0>;
            sensor-name = "cpu_temp";
        };
        
        temp_sensor@49 {
            compatible = "vendor,temp-sensor";
            reg = <0x49>;
            alert-gpio = <&tlmm 43 0>;
            interrupt-parent = <&tlmm>;
            interrupts = <43 IRQ_TYPE_EDGE_FALLING>;
            vdd-supply = <&pm8953_l10>;
            vio-supply = <&pm8953_l5>;
            sensor-id = <1>;
            sensor-name = "battery_temp";
        };
    };
};
```

### 步骤6：配置Makefile和Kconfig

**文件：drivers/misc/Kconfig**

```kconfig
config TEMP_SENSOR
    tristate "Temperature Sensor Driver"
    depends on I2C
    help
      This driver provides support for temperature sensors.
      It supports multiple sensors and provides temperature
      reading, threshold configuration, and alert functionality.
      
      To compile this driver as a module, choose M here: the
      module will be called temp_sensor.
```

**文件：drivers/misc/Makefile**

```makefile
obj-$(CONFIG_TEMP_SENSOR) += temp_sensor.o
```

**文件：kernel/configs/android-base.config**

```
CONFIG_TEMP_SENSOR=y
```


## 设备节点管理

### ueventd配置

Android使用ueventd来管理设备节点的创建和权限。

**文件：device/vendor/board/ueventd.rc**

```
# 温度传感器设备节点
/dev/temp_sensor          0666   system     system

# 其他传感器设备
/dev/sensor/*             0660   system     system

# GPIO设备
/sys/class/gpio/export    0220   root       system
/sys/class/gpio/unexport  0220   root       system
/sys/class/gpio/gpio*/direction  0660  root  system
/sys/class/gpio/gpio*/value      0660  root  system
```

**配置说明**：
- 第一列：设备节点路径
- 第二列：权限（八进制）
- 第三列：所有者
- 第四列：组

**权限说明**：
- 0666：所有用户可读写
- 0660：所有者和组可读写
- 0644：所有者可读写，其他用户只读
- 0600：只有所有者可读写

### SELinux权限配置

Android使用SELinux进行强制访问控制，需要配置相应的策略。

**文件：device/vendor/board/sepolicy/file_contexts**

```
# 设备节点上下文
/dev/temp_sensor          u:object_r:temp_sensor_device:s0

# sysfs节点上下文
/sys/devices/platform/soc/78b6000\.i2c/i2c-[0-9]+/[0-9]+-[0-9]+/temp_sensor(/.*)? u:object_r:sysfs_temp_sensor:s0
```

**文件：device/vendor/board/sepolicy/temp_sensor_device.te**

```
# 定义设备类型
type temp_sensor_device, dev_type;

# 定义sysfs类型
type sysfs_temp_sensor, sysfs_type, fs_type;
```

**文件：device/vendor/board/sepolicy/system_app.te**

```
# 允许system_app访问温度传感器设备
allow system_app temp_sensor_device:chr_file rw_file_perms;

# 允许读取sysfs节点
allow system_app sysfs_temp_sensor:dir r_dir_perms;
allow system_app sysfs_temp_sensor:file r_file_perms;
```

**文件：device/vendor/board/sepolicy/hal_sensors_default.te**

```
# 允许HAL访问温度传感器设备
allow hal_sensors_default temp_sensor_device:chr_file rw_file_perms;

# 允许HAL读取和写入sysfs节点
allow hal_sensors_default sysfs_temp_sensor:dir rw_dir_perms;
allow hal_sensors_default sysfs_temp_sensor:file rw_file_perms;

# 允许HAL使用wakelock
wakelock_use(hal_sensors_default)
```

**文件：device/vendor/board/sepolicy/init.te**

```
# 允许init创建设备节点
allow init temp_sensor_device:chr_file create_file_perms;

# 允许init设置设备节点权限
allow init temp_sensor_device:chr_file setattr;
```


### SELinux策略编译

**编译SELinux策略**：

```bash
# 进入Android源码目录
cd $ANDROID_BUILD_TOP

# 编译SELinux策略
make selinux_policy

# 或者编译整个系统
make -j$(nproc)
```

**验证SELinux策略**：

```bash
# 检查策略文件
ls -l out/target/product/<device>/system/etc/selinux/

# 查看策略内容
sesearch -A -s system_app -t temp_sensor_device \
    out/target/product/<device>/system/etc/selinux/plat_sepolicy.cil

# 在设备上查看SELinux状态
adb shell getenforce

# 查看SELinux拒绝日志
adb shell dmesg | grep avc
adb logcat | grep avc
```

**临时禁用SELinux（仅用于调试）**：

```bash
# 设置为宽容模式
adb shell setenforce 0

# 恢复强制模式
adb shell setenforce 1
```

## Android驱动调试方法

### 1. 内核日志调试

**查看内核日志**：

```bash
# 查看所有内核日志
adb shell dmesg

# 过滤温度传感器相关日志
adb shell dmesg | grep temp_sensor

# 实时查看内核日志
adb shell "dmesg -w"

# 查看特定级别的日志
adb shell dmesg -l err,warn

# 清除内核日志缓冲区
adb shell dmesg -c
```

**在驱动中添加日志**：

```c
// 不同级别的日志
pr_emerg("Emergency message\n");
pr_alert("Alert message\n");
pr_crit("Critical message\n");
pr_err("Error message\n");
pr_warning("Warning message\n");
pr_notice("Notice message\n");
pr_info("Info message\n");
pr_debug("Debug message\n");

// 设备相关日志
dev_err(&client->dev, "Device error: %d\n", ret);
dev_warn(&client->dev, "Device warning\n");
dev_info(&client->dev, "Device info\n");
dev_dbg(&client->dev, "Device debug\n");
```

**动态调试**：

```bash
# 启用动态调试
adb shell "echo 'file temp_sensor.c +p' > /sys/kernel/debug/dynamic_debug/control"

# 启用特定函数的调试
adb shell "echo 'func temp_sensor_read_i2c +p' > /sys/kernel/debug/dynamic_debug/control"

# 查看当前调试设置
adb shell cat /sys/kernel/debug/dynamic_debug/control | grep temp_sensor
```


### 2. sysfs调试接口

**添加sysfs属性**：

```c
/**
 * 显示温度
 */
static ssize_t temperature_show(struct device *dev,
                               struct device_attribute *attr,
                               char *buf)
{
    struct temp_sensor_dev *sensor = dev_get_drvdata(dev);
    int ret;
    
    ret = temp_sensor_read_i2c(sensor);
    if (ret < 0)
        return ret;
    
    return sprintf(buf, "%d.%02d\n",
                  sensor->current_data.temperature / 100,
                  sensor->current_data.temperature % 100);
}

/**
 * 设置高温阈值
 */
static ssize_t high_threshold_store(struct device *dev,
                                   struct device_attribute *attr,
                                   const char *buf, size_t count)
{
    struct temp_sensor_dev *sensor = dev_get_drvdata(dev);
    int threshold;
    int ret;
    
    ret = kstrtoint(buf, 10, &threshold);
    if (ret < 0)
        return ret;
    
    sensor->threshold.high_threshold = threshold;
    ret = temp_sensor_set_threshold(sensor, &sensor->threshold);
    if (ret < 0)
        return ret;
    
    return count;
}

/**
 * 显示高温阈值
 */
static ssize_t high_threshold_show(struct device *dev,
                                  struct device_attribute *attr,
                                  char *buf)
{
    struct temp_sensor_dev *sensor = dev_get_drvdata(dev);
    
    return sprintf(buf, "%d\n", sensor->threshold.high_threshold);
}

// 定义设备属性
static DEVICE_ATTR_RO(temperature);
static DEVICE_ATTR_RW(high_threshold);

// 属性组
static struct attribute *temp_sensor_attrs[] = {
    &dev_attr_temperature.attr,
    &dev_attr_high_threshold.attr,
    NULL,
};

static const struct attribute_group temp_sensor_attr_group = {
    .attrs = temp_sensor_attrs,
};

// 在probe函数中创建sysfs属性
ret = sysfs_create_group(&client->dev.kobj, &temp_sensor_attr_group);
if (ret < 0) {
    dev_err(&client->dev, "Failed to create sysfs group: %d\n", ret);
    return ret;
}

// 在remove函数中删除sysfs属性
sysfs_remove_group(&client->dev.kobj, &temp_sensor_attr_group);
```

**使用sysfs调试**：

```bash
# 查找sysfs节点
adb shell find /sys -name "*temp_sensor*"

# 读取温度
adb shell cat /sys/devices/platform/soc/78b6000.i2c/i2c-2/2-0048/temperature

# 设置阈值
adb shell "echo 8000 > /sys/devices/platform/soc/78b6000.i2c/i2c-2/2-0048/high_threshold"

# 查看所有属性
adb shell ls -l /sys/devices/platform/soc/78b6000.i2c/i2c-2/2-0048/
```


### 3. ftrace跟踪

**使用ftrace跟踪驱动执行**：

```bash
# 进入ftrace目录
adb shell cd /sys/kernel/debug/tracing

# 设置跟踪器
adb shell "echo function > /sys/kernel/debug/tracing/current_tracer"

# 设置过滤器（只跟踪温度传感器相关函数）
adb shell "echo 'temp_sensor_*' > /sys/kernel/debug/tracing/set_ftrace_filter"

# 启用跟踪
adb shell "echo 1 > /sys/kernel/debug/tracing/tracing_on"

# 执行测试操作
adb shell cat /dev/temp_sensor

# 停止跟踪
adb shell "echo 0 > /sys/kernel/debug/tracing/tracing_on"

# 查看跟踪结果
adb shell cat /sys/kernel/debug/tracing/trace

# 清除跟踪缓冲区
adb shell "echo > /sys/kernel/debug/tracing/trace"
```

**跟踪特定事件**：

```bash
# 启用I2C事件跟踪
adb shell "echo 1 > /sys/kernel/debug/tracing/events/i2c/enable"

# 启用中断事件跟踪
adb shell "echo 1 > /sys/kernel/debug/tracing/events/irq/enable"

# 启用GPIO事件跟踪
adb shell "echo 1 > /sys/kernel/debug/tracing/events/gpio/enable"

# 查看可用事件
adb shell cat /sys/kernel/debug/tracing/available_events | grep -E "i2c|irq|gpio"
```

### 4. 使用kgdb调试

**配置内核支持kgdb**：

```kconfig
CONFIG_KGDB=y
CONFIG_KGDB_SERIAL_CONSOLE=y
CONFIG_KGDB_KDB=y
CONFIG_DEBUG_INFO=y
```

**通过串口连接kgdb**：

```bash
# 在设备上启动kgdb
adb shell "echo ttyMSM0,115200 > /sys/module/kgdboc/parameters/kgdboc"
adb shell "echo g > /proc/sysrq-trigger"

# 在主机上连接gdb
gdb vmlinux
(gdb) target remote /dev/ttyUSB0
(gdb) set remotebaud 115200

# 设置断点
(gdb) break temp_sensor_read_i2c

# 继续执行
(gdb) continue

# 查看变量
(gdb) print sensor->current_data

# 单步执行
(gdb) step
(gdb) next

# 查看调用栈
(gdb) backtrace
```

### 5. 内存泄漏检测

**使用kmemleak检测内存泄漏**：

```bash
# 启用kmemleak
adb shell "echo scan > /sys/kernel/debug/kmemleak"

# 触发扫描
adb shell "echo scan > /sys/kernel/debug/kmemleak"

# 查看泄漏报告
adb shell cat /sys/kernel/debug/kmemleak

# 清除报告
adb shell "echo clear > /sys/kernel/debug/kmemleak"
```

**在代码中添加内存跟踪**：

```c
// 分配内存时添加标记
void *ptr = kmalloc(size, GFP_KERNEL);
kmemleak_alloc(ptr, size, 1, GFP_KERNEL);

// 释放内存时移除标记
kmemleak_free(ptr);
kfree(ptr);

// 忽略特定内存
kmemleak_ignore(ptr);
```


## 驱动集成到Android系统

### 1. 编译驱动

**配置内核**：

```bash
# 进入内核目录
cd kernel

# 配置内核
make ARCH=arm64 vendor_defconfig

# 启用温度传感器驱动
make ARCH=arm64 menuconfig
# Device Drivers -> Misc devices -> Temperature Sensor Driver

# 或直接修改defconfig
echo "CONFIG_TEMP_SENSOR=y" >> arch/arm64/configs/vendor_defconfig

# 编译内核
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j$(nproc)
```

**编译为模块**：

```bash
# 配置为模块
echo "CONFIG_TEMP_SENSOR=m" >> arch/arm64/configs/vendor_defconfig

# 编译模块
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- M=drivers/misc modules

# 生成的模块文件
ls drivers/misc/temp_sensor.ko
```

### 2. 安装驱动

**安装到系统**：

```bash
# 推送内核镜像
adb reboot bootloader
fastboot flash boot boot.img
fastboot reboot

# 或推送模块
adb root
adb remount
adb push drivers/misc/temp_sensor.ko /vendor/lib/modules/
adb shell insmod /vendor/lib/modules/temp_sensor.ko
```

**配置自动加载**：

**文件：device/vendor/board/init.board.rc**

```
# 加载温度传感器驱动模块
on boot
    insmod /vendor/lib/modules/temp_sensor.ko
    
    # 等待设备节点创建
    wait /dev/temp_sensor
    
    # 设置设备节点权限
    chmod 0666 /dev/temp_sensor
    chown system system /dev/temp_sensor
```

### 3. 验证驱动

**检查驱动加载**：

```bash
# 查看已加载的模块
adb shell lsmod | grep temp_sensor

# 查看设备节点
adb shell ls -l /dev/temp_sensor

# 查看sysfs节点
adb shell find /sys -name "*temp_sensor*"

# 查看驱动信息
adb shell cat /proc/devices | grep temp_sensor

# 查看设备树节点
adb shell cat /proc/device-tree/soc/i2c@78b6000/temp_sensor@48/compatible
```

**测试驱动功能**：

```bash
# 读取温度
adb shell cat /dev/temp_sensor | od -An -t d4

# 使用ioctl测试
adb shell /vendor/bin/temp_sensor_test

# 查看内核日志
adb shell dmesg | grep temp_sensor
```


### 4. 编写测试程序

**文件：vendor/bin/temp_sensor_test.c**

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <string.h>

#include "temp_sensor.h"

int main(int argc, char *argv[])
{
    int fd;
    int ret;
    struct temp_data temp;
    struct temp_threshold threshold;
    struct sensor_info info;
    int sensor_count;
    
    printf("Temperature Sensor Test Program\n");
    printf("================================\n\n");
    
    // 打开设备
    fd = open("/dev/temp_sensor", O_RDWR);
    if (fd < 0) {
        perror("Failed to open device");
        return 1;
    }
    
    // 获取传感器数量
    ret = ioctl(fd, TEMP_IOC_GET_COUNT, &sensor_count);
    if (ret < 0) {
        perror("Failed to get sensor count");
        close(fd);
        return 1;
    }
    
    printf("Found %d temperature sensor(s)\n\n", sensor_count);
    
    // 遍历所有传感器
    for (int i = 0; i < sensor_count; i++) {
        // 获取传感器信息
        info.sensor_id = i;
        ret = ioctl(fd, TEMP_IOC_GET_INFO, &info);
        if (ret < 0) {
            perror("Failed to get sensor info");
            continue;
        }
        
        printf("Sensor %d: %s\n", i, info.name);
        printf("  Range: %d.%02d°C to %d.%02d°C\n",
               info.min_temp / 100, abs(info.min_temp % 100),
               info.max_temp / 100, info.max_temp % 100);
        printf("  Resolution: 0.%04d°C\n", info.resolution);
        
        // 读取温度
        temp.sensor_id = i;
        ret = ioctl(fd, TEMP_IOC_GET_TEMP, &temp);
        if (ret < 0) {
            perror("Failed to read temperature");
            continue;
        }
        
        printf("  Current Temperature: %d.%02d°C\n",
               temp.temperature / 100, temp.temperature % 100);
        
        // 获取阈值
        threshold.sensor_id = i;
        ret = ioctl(fd, TEMP_IOC_GET_THRESHOLD, &threshold);
        if (ret < 0) {
            perror("Failed to get threshold");
            continue;
        }
        
        printf("  High Threshold: %d.%02d°C\n",
               threshold.high_threshold / 100, threshold.high_threshold % 100);
        printf("  Low Threshold: %d.%02d°C\n",
               threshold.low_threshold / 100, threshold.low_threshold % 100);
        
        printf("\n");
    }
    
    // 测试设置阈值
    if (sensor_count > 0) {
        printf("Testing threshold setting...\n");
        
        threshold.sensor_id = 0;
        threshold.high_threshold = 8500;  // 85°C
        threshold.low_threshold = 500;    // 5°C
        
        ret = ioctl(fd, TEMP_IOC_SET_THRESHOLD, &threshold);
        if (ret < 0) {
            perror("Failed to set threshold");
        } else {
            printf("Threshold set successfully\n");
            
            // 验证设置
            threshold.sensor_id = 0;
            ret = ioctl(fd, TEMP_IOC_GET_THRESHOLD, &threshold);
            if (ret == 0) {
                printf("Verified - High: %d.%02d°C, Low: %d.%02d°C\n",
                       threshold.high_threshold / 100, threshold.high_threshold % 100,
                       threshold.low_threshold / 100, threshold.low_threshold % 100);
            }
        }
        
        printf("\n");
    }
    
    // 测试告警使能
    if (sensor_count > 0) {
        printf("Enabling alert for sensor 0...\n");
        
        int sensor_id = 0;
        ret = ioctl(fd, TEMP_IOC_ENABLE_ALERT, &sensor_id);
        if (ret < 0) {
            perror("Failed to enable alert");
        } else {
            printf("Alert enabled successfully\n");
        }
        
        printf("\n");
    }
    
    // 持续监控温度
    if (argc > 1 && strcmp(argv[1], "-m") == 0) {
        printf("Monitoring temperature (Ctrl+C to stop)...\n\n");
        
        while (1) {
            for (int i = 0; i < sensor_count; i++) {
                temp.sensor_id = i;
                ret = ioctl(fd, TEMP_IOC_GET_TEMP, &temp);
                if (ret == 0) {
                    printf("Sensor %d: %d.%02d°C  ",
                           i, temp.temperature / 100, temp.temperature % 100);
                }
            }
            printf("\r");
            fflush(stdout);
            
            sleep(1);
        }
    }
    
    close(fd);
    printf("Test completed\n");
    
    return 0;
}
```

**编译测试程序**：

**文件：vendor/bin/Android.bp**

```bp
cc_binary {
    name: "temp_sensor_test",
    vendor: true,
    
    srcs: ["temp_sensor_test.c"],
    
    shared_libs: [
        "liblog",
        "libcutils",
    ],
    
    cflags: [
        "-Wall",
        "-Werror",
    ],
}
```

**运行测试**：

```bash
# 编译
make temp_sensor_test

# 推送到设备
adb push out/target/product/<device>/vendor/bin/temp_sensor_test /vendor/bin/

# 运行测试
adb shell /vendor/bin/temp_sensor_test

# 监控模式
adb shell /vendor/bin/temp_sensor_test -m
```


## Android驱动开发最佳实践

### 1. 错误处理

**完善的错误处理**：

```c
static int temp_sensor_probe(struct i2c_client *client,
                             const struct i2c_device_id *id)
{
    struct temp_sensor_dev *sensor;
    int ret;
    
    // 检查I2C功能
    if (!i2c_check_functionality(client->adapter, I2C_FUNC_I2C)) {
        dev_err(&client->dev, "I2C adapter doesn't support I2C_FUNC_I2C\n");
        return -ENODEV;
    }
    
    // 分配内存
    sensor = devm_kzalloc(&client->dev, sizeof(*sensor), GFP_KERNEL);
    if (!sensor) {
        dev_err(&client->dev, "Failed to allocate memory\n");
        return -ENOMEM;
    }
    
    // 初始化传感器
    ret = temp_sensor_init_hardware(sensor);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize hardware: %d\n", ret);
        goto err_init_hw;
    }
    
    // 注册设备
    ret = temp_sensor_register_device(sensor);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to register device: %d\n", ret);
        goto err_register;
    }
    
    return 0;
    
err_register:
    temp_sensor_deinit_hardware(sensor);
err_init_hw:
    return ret;
}
```

### 2. 资源管理

**使用devm_*系列函数自动管理资源**：

```c
// 自动管理的内存分配
sensor = devm_kzalloc(&client->dev, sizeof(*sensor), GFP_KERNEL);

// 自动管理的GPIO申请
ret = devm_gpio_request_one(&client->dev, gpio, flags, label);

// 自动管理的中断申请
ret = devm_request_irq(&client->dev, irq, handler, flags, name, dev_id);

// 自动管理的时钟获取
clk = devm_clk_get(&client->dev, "core_clk");

// 自动管理的regulator获取
regulator = devm_regulator_get(&client->dev, "vdd");

// 自动管理的ioremap
base = devm_ioremap_resource(&pdev->dev, res);
```

**优势**：
- 自动释放资源
- 减少错误处理代码
- 避免资源泄漏
- 简化remove函数

### 3. 并发控制

**使用合适的锁机制**：

```c
struct temp_sensor_dev {
    struct mutex lock;          // 保护设备状态
    spinlock_t irq_lock;        // 保护中断相关数据
    struct rw_semaphore rw_sem; // 读写信号量
};

// 互斥锁（可睡眠）
mutex_lock(&sensor->lock);
// 访问共享资源
mutex_unlock(&sensor->lock);

// 自旋锁（不可睡眠）
spin_lock_irqsave(&sensor->irq_lock, flags);
// 访问中断相关数据
spin_unlock_irqrestore(&sensor->irq_lock, flags);

// 读写信号量
down_read(&sensor->rw_sem);   // 读锁
// 读取数据
up_read(&sensor->rw_sem);

down_write(&sensor->rw_sem);  // 写锁
// 修改数据
up_write(&sensor->rw_sem);
```


### 4. 电源管理

**实现完整的电源管理**：

```c
#ifdef CONFIG_PM
static int temp_sensor_suspend(struct device *dev)
{
    struct temp_sensor_dev *sensor = dev_get_drvdata(dev);
    
    // 保存当前状态
    sensor->saved_state = sensor->current_state;
    
    // 禁用中断
    if (sensor->alert_irq > 0)
        disable_irq(sensor->alert_irq);
    
    // 关闭电源
    if (sensor->vdd_regulator)
        regulator_disable(sensor->vdd_regulator);
    
    return 0;
}

static int temp_sensor_resume(struct device *dev)
{
    struct temp_sensor_dev *sensor = dev_get_drvdata(dev);
    int ret;
    
    // 打开电源
    if (sensor->vdd_regulator) {
        ret = regulator_enable(sensor->vdd_regulator);
        if (ret < 0)
            return ret;
    }
    
    // 等待电源稳定
    msleep(10);
    
    // 恢复状态
    ret = temp_sensor_restore_state(sensor);
    if (ret < 0)
        return ret;
    
    // 使能中断
    if (sensor->alert_irq > 0)
        enable_irq(sensor->alert_irq);
    
    return 0;
}

static const struct dev_pm_ops temp_sensor_pm_ops = {
    SET_SYSTEM_SLEEP_PM_OPS(temp_sensor_suspend, temp_sensor_resume)
    SET_RUNTIME_PM_OPS(temp_sensor_runtime_suspend,
                      temp_sensor_runtime_resume,
                      NULL)
};
#endif
```

### 5. 性能优化

**减少不必要的操作**：

```c
// 缓存读取结果
struct temp_sensor_dev {
    struct temp_data cached_data;
    unsigned long cache_time;
    unsigned long cache_timeout;  // 缓存超时时间（jiffies）
};

static int temp_sensor_read_cached(struct temp_sensor_dev *sensor,
                                  struct temp_data *data)
{
    unsigned long now = jiffies;
    int ret;
    
    // 检查缓存是否有效
    if (time_before(now, sensor->cache_time + sensor->cache_timeout)) {
        memcpy(data, &sensor->cached_data, sizeof(*data));
        return 0;
    }
    
    // 缓存过期，重新读取
    ret = temp_sensor_read_i2c(sensor);
    if (ret < 0)
        return ret;
    
    // 更新缓存
    memcpy(&sensor->cached_data, &sensor->current_data, sizeof(*data));
    sensor->cache_time = now;
    
    memcpy(data, &sensor->cached_data, sizeof(*data));
    return 0;
}
```

**批量操作**：

```c
// 批量读取多个传感器
static int temp_sensor_read_all(struct temp_driver_data *data,
                               struct temp_data *temps, int count)
{
    int i;
    int ret;
    
    if (count > data->sensor_count)
        count = data->sensor_count;
    
    mutex_lock(&data->lock);
    
    for (i = 0; i < count; i++) {
        ret = temp_sensor_read_i2c(data->sensors[i]);
        if (ret < 0) {
            mutex_unlock(&data->lock);
            return ret;
        }
        
        memcpy(&temps[i], &data->sensors[i]->current_data, sizeof(temps[i]));
    }
    
    mutex_unlock(&data->lock);
    return count;
}
```


### 6. 代码规范

**遵循Linux内核编码规范**：

```c
// 正确的缩进（使用Tab，宽度为8）
static int temp_sensor_probe(struct i2c_client *client,
			     const struct i2c_device_id *id)
{
	struct temp_sensor_dev *sensor;
	int ret;
	
	// 函数体使用Tab缩进
	sensor = devm_kzalloc(&client->dev, sizeof(*sensor), GFP_KERNEL);
	if (!sensor)
		return -ENOMEM;
	
	return 0;
}

// 正确的命名
static int temp_sensor_read_temperature(struct temp_sensor_dev *sensor);  // 函数名
struct temp_sensor_dev;  // 结构体名
int sensor_count;        // 变量名

// 正确的注释
/**
 * temp_sensor_read_i2c - 从I2C读取温度
 * @sensor: 传感器设备指针
 *
 * 从I2C总线读取温度传感器的原始数据，并转换为摄氏度。
 *
 * Return: 成功返回0，失败返回负数错误码
 */
static int temp_sensor_read_i2c(struct temp_sensor_dev *sensor)
{
	// 实现代码
}

// 正确的错误处理
ret = temp_sensor_init(sensor);
if (ret < 0) {
	dev_err(&client->dev, "Failed to initialize: %d\n", ret);
	goto err_init;
}

// 正确的goto标签
err_init:
	temp_sensor_cleanup(sensor);
	return ret;
```

**使用checkpatch.pl检查代码**：

```bash
# 检查单个文件
scripts/checkpatch.pl -f drivers/misc/temp_sensor.c

# 检查补丁
scripts/checkpatch.pl 0001-add-temp-sensor-driver.patch

# 严格模式
scripts/checkpatch.pl --strict -f drivers/misc/temp_sensor.c
```

## 总结

通过本教程，你应该已经掌握了：

- ✅ Android驱动框架的整体架构
- ✅ Binder驱动的工作原理和通信机制
- ✅ Android字符设备驱动的开发流程
- ✅ 设备节点的创建和权限管理
- ✅ SELinux权限配置方法
- ✅ Android驱动的调试技巧
- ✅ 驱动集成到Android系统的方法
- ✅ Android驱动开发的最佳实践

### 关键要点

1. **Android驱动特点**
   - Binder IPC机制
   - SELinux权限控制
   - ueventd设备节点管理
   - 电源管理集成

2. **Binder驱动**
   - 进程间通信核心
   - 一次拷贝机制
   - 内核态实现
   - 安全机制完善

3. **开发流程**
   - 定义驱动接口
   - 实现核心功能
   - 配置设备树
   - 配置权限
   - 集成测试

4. **调试方法**
   - 内核日志
   - sysfs接口
   - ftrace跟踪
   - kgdb调试

5. **最佳实践**
   - 完善错误处理
   - 自动资源管理
   - 正确并发控制
   - 电源管理支持
   - 性能优化
   - 代码规范


## 实践练习

### 练习1：实现GPIO驱动

**任务**：实现一个GPIO控制驱动

**要求**：
1. 支持GPIO输入输出配置
2. 支持GPIO电平读写
3. 支持GPIO中断
4. 提供sysfs接口
5. 配置SELinux权限

**提示**：
- 使用GPIO子系统API
- 实现中断处理函数
- 添加设备树配置
- 测试中断功能

### 练习2：扩展温度传感器驱动

**任务**：为温度传感器驱动添加新功能

**要求**：
1. 添加温度历史记录功能
2. 实现温度变化通知
3. 添加温度校准功能
4. 实现数据过滤算法
5. 添加性能统计

**提示**：
- 使用环形缓冲区存储历史数据
- 使用netlink或uevent通知
- 实现校准参数存储
- 使用滑动平均滤波
- 统计读取次数和时间

### 练习3：实现Binder服务

**任务**：基于Binder实现一个简单的系统服务

**要求**：
1. 定义AIDL接口
2. 实现Native服务
3. 注册到ServiceManager
4. 实现客户端调用
5. 添加权限检查

**提示**：
- 参考现有系统服务
- 使用libbinder库
- 配置SELinux策略
- 测试IPC性能

## 下一步学习

建议按以下顺序继续学习：

### 1. Android系统定制
- [Android系统定制与移植](../advanced/01-android-customization.html)
- AOSP编译和定制
- BSP适配
- 系统优化

### 2. 深入学习
- Linux内核驱动高级主题
- Android Framework源码分析
- Binder通信机制详解
- Android性能优化

### 3. 相关主题
- [Linux驱动开发入门](../../05-embedded-linux/intermediate/01-linux-driver-basics.html)
- [设备树详解](../../05-embedded-linux/beginner/03-device-tree.html)
- [Android HAL层开发](./01-android-hal.html)

## 参考资料

### 官方文档

1. **Android内核文档**
   - https://source.android.com/devices/architecture/kernel
   - 内核开发指南

2. **Linux内核文档**
   - https://www.kernel.org/doc/html/latest/
   - 驱动开发文档

3. **Binder文档**
   - https://source.android.com/devices/architecture/hidl/binder-ipc
   - Binder IPC机制

### 推荐书籍

1. **《Linux设备驱动程序》**
   - 作者：Jonathan Corbet等
   - Linux驱动开发经典

2. **《深入理解Android内核设计思想》**
   - 作者：林学森
   - Android内核详解

3. **《Android系统源代码情景分析》**
   - 作者：罗升阳
   - Binder机制详解

### 在线资源

1. **Linux内核源码**
   - https://git.kernel.org/
   - 内核源码浏览

2. **Android源码在线浏览**
   - https://cs.android.com/
   - Android源码搜索

3. **LWN.net**
   - https://lwn.net/
   - Linux内核新闻和文章

### 开发工具

**必备工具**：
- Android Studio
- Android NDK
- ADB（Android Debug Bridge）
- 交叉编译工具链

**调试工具**：
- kgdb（内核调试器）
- ftrace（内核跟踪）
- dmesg（内核日志）
- strace（系统调用跟踪）

**分析工具**：
- systrace（系统跟踪）
- simpleperf（性能分析）
- kmemleak（内存泄漏检测）
- lockdep（死锁检测）

## 常见问题解答

### Q1: Android驱动和标准Linux驱动有什么区别？

**A**: 

**主要区别**：

1. **Binder支持**：Android驱动需要考虑Binder IPC机制
2. **SELinux**：必须配置SELinux权限策略
3. **ueventd**：使用ueventd管理设备节点
4. **电源管理**：需要支持Android的电源管理机制（wakelock等）
5. **设备树**：广泛使用设备树配置硬件

**相同点**：
- 基本的驱动框架相同
- 使用相同的内核API
- 遵循相同的编码规范

### Q2: 如何调试SELinux权限问题？

**A**: 

**调试步骤**：

1. **查看拒绝日志**：
```bash
adb shell dmesg | grep avc
adb logcat | grep avc
```

2. **临时禁用SELinux**：
```bash
adb shell setenforce 0
```

3. **分析拒绝原因**：
```bash
# 查看拒绝详情
adb shell cat /sys/fs/selinux/avc/cache_stats

# 使用audit2allow生成策略
adb shell dmesg | grep avc | audit2allow
```

4. **添加策略**：
```
# 在.te文件中添加
allow source_type target_type:class { permissions };
```

5. **验证策略**：
```bash
# 重新编译并测试
make selinux_policy
adb reboot
```

### Q3: 如何优化驱动性能？

**A**: 

**优化策略**：

1. **减少系统调用**：
   - 批量操作
   - 缓存数据
   - 使用mmap

2. **优化中断处理**：
   - 使用中断下半部
   - 减少中断处理时间
   - 使用工作队列

3. **内存优化**：
   - 使用内存池
   - 避免频繁分配
   - 使用DMA

4. **并发优化**：
   - 减少锁竞争
   - 使用无锁算法
   - 细化锁粒度

5. **I/O优化**：
   - 使用异步I/O
   - 批量传输
   - 使用DMA

### Q4: 驱动崩溃如何定位问题？

**A**: 

**定位方法**：

1. **查看内核日志**：
```bash
adb shell dmesg
adb shell cat /proc/last_kmsg
```

2. **分析调用栈**：
```
Unable to handle kernel NULL pointer dereference at virtual address 00000000
PC is at temp_sensor_read_i2c+0x24/0x80
LR is at temp_sensor_ioctl+0x48/0x120
```

3. **使用addr2line定位代码**：
```bash
addr2line -e vmlinux -f 0xc0123456
```

4. **使用kgdb调试**：
```bash
# 设置断点
(gdb) break temp_sensor_read_i2c
(gdb) continue
```

5. **添加调试信息**：
```c
pr_info("Before operation: ptr=%p\n", ptr);
// 操作
pr_info("After operation\n");
```

### Q5: 如何实现驱动的热插拔支持？

**A**: 

**实现方法**：

1. **使用平台设备驱动**：
```c
static struct platform_driver temp_sensor_driver = {
    .probe = temp_sensor_probe,
    .remove = temp_sensor_remove,
    .driver = {
        .name = "temp_sensor",
        .of_match_table = temp_sensor_of_match,
    },
};
```

2. **实现probe和remove**：
```c
static int temp_sensor_probe(struct platform_device *pdev)
{
    // 设备插入时调用
    // 初始化设备
}

static int temp_sensor_remove(struct platform_device *pdev)
{
    // 设备移除时调用
    // 清理资源
}
```

3. **发送uevent通知**：
```c
kobject_uevent(&dev->kobj, KOBJ_ADD);    // 设备添加
kobject_uevent(&dev->kobj, KOBJ_REMOVE); // 设备移除
```

4. **在用户空间监听**：
```c
// 使用netlink监听uevent
int fd = socket(PF_NETLINK, SOCK_DGRAM, NETLINK_KOBJECT_UEVENT);
```

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
