---
title: "Android系统定制与移植：从AOSP到产品化"
description: "全面学习Android系统定制与移植，掌握AOSP编译、系统定制、BSP适配、系统优化和OTA升级，通过实战项目理解Android系统的完整开发流程"
slug: "android-customization"

# 分类信息
domain: "操作系统层"
module: "Android系统"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - Android定制
  - AOSP
  - 系统移植
  - BSP适配
  - OTA升级
prerequisites:
  - "03-operating-system-layer/06-android-system/intermediate/02-android-driver"
  - "03-operating-system-layer/06-android-system/intermediate/01-android-hal"
  - "03-operating-system-layer/05-embedded-linux/advanced/01-complete-linux-system"
related_contents:
  - "03-operating-system-layer/06-android-system/beginner/01-android-architecture"
  - "03-operating-system-layer/05-embedded-linux/intermediate/02-rootfs"

# 学习信息
estimated_time: 120
difficulty_score: 9

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
  - Android系统定制
  - AOSP编译
  - 系统移植
  - BSP适配
  - OTA升级
cover_image: ""
---

# Android系统定制与移植：从AOSP到产品化


## 学习目标

完成本教程后，你将能够：

- [ ] 理解Android系统架构和AOSP项目结构
- [ ] 掌握AOSP源码下载和编译流程
- [ ] 学会Android系统定制和功能裁剪
- [ ] 掌握BSP（Board Support Package）适配方法
- [ ] 理解Android启动流程和优化技术
- [ ] 掌握系统性能优化和调试方法
- [ ] 学会OTA升级系统的设计与实现
- [ ] 能够完成一个完整的Android产品定制项目

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉Linux系统和命令行操作
- 了解Android系统架构
- 掌握Android驱动开发
- 理解Linux内核编译
- 熟悉Git版本控制

**技能要求**：
- 能够编译Linux内核
- 会使用Android开发工具
- 熟悉Shell脚本编程
- 了解设备树配置
- 能够阅读和修改Makefile

**开发环境**：
- Ubuntu 20.04或更高版本（推荐）
- 至少250GB可用磁盘空间
- 至少16GB RAM（推荐32GB）
- 高速网络连接
- Git、Repo、Python等工具

## Android系统架构概述

### AOSP项目结构

AOSP（Android Open Source Project）是Android的开源版本，包含了完整的Android系统源码。



**Android系统层次架构**：

```
┌─────────────────────────────────────────────────┐
│    Applications (应用层)                         │
│    System Apps, Third-party Apps                │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Application Framework (应用框架层)            │
│    Activity Manager, Window Manager, etc.       │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Android Runtime & Libraries                   │
│    ART, Native Libraries, System Services        │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Hardware Abstraction Layer (HAL)              │
│    Camera HAL, Audio HAL, Sensor HAL, etc.       │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Linux Kernel                                  │
│    Drivers, Power Management, Security           │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│    Hardware                                      │
└─────────────────────────────────────────────────┘
```

**AOSP源码目录结构**：

```
aosp/
├── art/                    # Android Runtime
├── bionic/                 # C库、数学库、动态链接器
├── bootable/               # 启动相关（bootloader、recovery）
├── build/                  # 编译系统
├── cts/                    # 兼容性测试套件
├── dalvik/                 # Dalvik虚拟机
├── developers/             # 开发者资源
├── development/            # 开发工具
├── device/                 # 设备相关配置
│   ├── generic/           # 通用设备配置
│   └── vendor/            # 厂商设备配置
├── external/               # 外部开源项目
├── frameworks/             # 框架层
│   ├── base/              # 核心框架
│   ├── native/            # Native框架
│   └── av/                # 音视频框架
├── hardware/               # HAL层
│   ├── interfaces/        # HAL接口定义
│   └── libhardware/       # HAL库
├── kernel/                 # Linux内核
├── packages/               # 应用程序
│   ├── apps/              # 系统应用
│   └── services/          # 系统服务
├── prebuilts/              # 预编译工具
├── sdk/                    # SDK
├── system/                 # 系统组件
│   ├── core/              # 核心系统
│   ├── sepolicy/          # SELinux策略
│   └── vold/              # 卷管理守护进程
├── tools/                  # 开发工具
└── vendor/                 # 厂商专有代码
```

### Android启动流程

**完整启动流程**：

```
1. Bootloader
   ↓
2. Linux Kernel
   ↓
3. Init进程
   ↓
4. Zygote进程
   ↓
5. System Server
   ↓
6. Home Launcher
```

**详细启动流程**：

1. **Bootloader阶段**
   - 硬件初始化
   - 加载内核到内存
   - 传递启动参数
   - 跳转到内核入口

2. **Kernel阶段**
   - 内核初始化
   - 驱动加载
   - 挂载根文件系统
   - 启动init进程

3. **Init阶段**
   - 解析init.rc配置
   - 挂载文件系统
   - 启动系统服务
   - 启动Zygote

4. **Zygote阶段**
   - 创建虚拟机
   - 预加载类和资源
   - 启动System Server
   - 监听应用启动请求

5. **System Server阶段**
   - 启动系统服务
   - 启动各种Manager
   - 发送BOOT_COMPLETED广播

6. **Home Launcher阶段**
   - 显示桌面
   - 系统就绪



## AOSP源码下载与编译

### 环境准备

**1. 安装必要的软件包**

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade

# 安装编译依赖
sudo apt-get install -y git-core gnupg flex bison build-essential \
    zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 \
    libncurses5 lib32ncurses5-dev x11proto-core-dev libx11-dev \
    lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip \
    fontconfig python3 python3-pip

# 安装Repo工具
mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
export PATH=~/bin:$PATH

# 配置Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**2. 配置编译环境**

```bash
# 创建工作目录
mkdir -p ~/aosp
cd ~/aosp

# 设置环境变量
echo 'export USE_CCACHE=1' >> ~/.bashrc
echo 'export CCACHE_DIR=~/.ccache' >> ~/.bashrc
source ~/.bashrc

# 配置ccache（加速编译）
ccache -M 50G
```

### 下载AOSP源码

**1. 初始化Repo仓库**

```bash
# 进入工作目录
cd ~/aosp

# 初始化仓库（选择Android版本）
repo init -u https://android.googlesource.com/platform/manifest -b android-13.0.0_r1

# 或使用国内镜像（清华大学）
repo init -u https://mirrors.tuna.tsinghua.edu.cn/git/AOSP/platform/manifest \
    -b android-13.0.0_r1
```

**2. 同步源码**

```bash
# 开始同步（需要很长时间，取决于网络速度）
repo sync -c -j8

# 参数说明：
# -c: 只下载当前分支
# -j8: 使用8个并行任务
```

**常见Android版本代号**：

| 版本号 | 代号 | API Level | 发布时间 |
|--------|------|-----------|----------|
| 13 | Tiramisu | 33 | 2022 |
| 12 | Snow Cone | 31-32 | 2021 |
| 11 | Red Velvet Cake | 30 | 2020 |
| 10 | Quince Tart | 29 | 2019 |
| 9 | Pie | 28 | 2018 |

### 编译AOSP

**1. 设置编译环境**

```bash
# 进入源码目录
cd ~/aosp

# 初始化编译环境
source build/envsetup.sh

# 选择编译目标
lunch aosp_arm64-eng

# 编译目标格式：<product_name>-<build_variant>
# product_name: aosp_arm64, aosp_x86_64等
# build_variant: user, userdebug, eng
```

**编译变体说明**：

- **user**: 生产版本，权限受限，性能优化
- **userdebug**: 开发版本，root权限，可调试
- **eng**: 工程版本，所有调试功能，开发使用

**2. 开始编译**

```bash
# 编译整个系统（使用所有CPU核心）
make -j$(nproc)

# 或指定核心数
make -j16

# 编译特定模块
make framework
make services
make systemui
```

**3. 编译输出**

编译完成后，输出文件位于：

```
out/target/product/<device_name>/
├── system.img          # 系统分区镜像
├── vendor.img          # 厂商分区镜像
├── boot.img            # 启动镜像
├── recovery.img        # 恢复镜像
├── userdata.img        # 用户数据镜像
├── cache.img           # 缓存镜像
└── ramdisk.img         # 内存盘镜像
```

### 编译常见问题

**问题1：内存不足**

```bash
# 解决方法：减少并行任务数
make -j4

# 或增加swap空间
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**问题2：磁盘空间不足**

```bash
# 清理编译输出
make clean

# 清理所有（包括配置）
make clobber

# 检查磁盘使用
du -sh out/
```

**问题3：编译错误**

```bash
# 查看详细错误信息
make showcommands

# 单独编译失败的模块
make <module_name>

# 查看编译日志
less out/verbose.log.gz
```



## Android系统定制

### 创建设备配置

**1. 设备目录结构**

```bash
# 创建设备配置目录
mkdir -p device/vendor/product_name

# 目录结构
device/vendor/product_name/
├── AndroidProducts.mk      # 产品定义
├── BoardConfig.mk          # 板级配置
├── device.mk               # 设备配置
├── product_name.mk         # 产品配置
├── system.prop             # 系统属性
├── init.rc                 # 初始化脚本
├── fstab.device            # 文件系统表
├── ueventd.rc              # 设备节点配置
├── sepolicy/               # SELinux策略
├── overlay/                # 资源覆盖
└── proprietary/            # 专有文件
```

**2. 产品定义文件**

**文件：device/vendor/product_name/AndroidProducts.mk**

```makefile
#
# Copyright (C) 2024 Vendor Inc.
#

PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/product_name.mk

COMMON_LUNCH_CHOICES := \
    product_name-user \
    product_name-userdebug \
    product_name-eng
```

**3. 产品配置文件**

**文件：device/vendor/product_name/product_name.mk**

```makefile
#
# Product Configuration
#

# 继承基础配置
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base.mk)

# 产品信息
PRODUCT_NAME := product_name
PRODUCT_DEVICE := product_name
PRODUCT_BRAND := Vendor
PRODUCT_MODEL := Product Name
PRODUCT_MANUFACTURER := Vendor Inc.

# 设备配置
$(call inherit-product, device/vendor/product_name/device.mk)

# 系统属性
PRODUCT_PROPERTY_OVERRIDES += \
    ro.product.name=product_name \
    ro.product.device=product_name \
    ro.product.brand=Vendor \
    ro.product.model=Product_Name \
    ro.product.manufacturer=Vendor

# 包含的应用
PRODUCT_PACKAGES += \
    Settings \
    SystemUI \
    Launcher3 \
    Camera2 \
    Gallery2 \
    Music \
    Calculator \
    Calendar \
    Contacts \
    Dialer \
    Messaging

# 权限配置
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.camera.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.xml \
    frameworks/native/data/etc/android.hardware.bluetooth.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.bluetooth.xml

# 覆盖资源
DEVICE_PACKAGE_OVERLAYS += device/vendor/product_name/overlay
```

**4. 设备配置文件**

**文件：device/vendor/product_name/device.mk**

```makefile
#
# Device Configuration
#

# 架构配置
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_VARIANT := generic

# 内核配置
BOARD_KERNEL_CMDLINE := console=ttyMSM0,115200n8 \
    androidboot.console=ttyMSM0 \
    androidboot.hardware=product_name \
    user_debug=31 \
    msm_rtb.filter=0x237 \
    ehci-hcd.park=3 \
    androidboot.bootdevice=7824900.sdhci \
    androidboot.selinux=permissive

BOARD_KERNEL_BASE := 0x80000000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_MKBOOTIMG_ARGS := --ramdisk_offset 0x01000000 --tags_offset 0x00000100

# 分区大小
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 67108864
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 3221225472
BOARD_USERDATAIMAGE_PARTITION_SIZE := 10737418240
BOARD_CACHEIMAGE_PARTITION_SIZE := 268435456
BOARD_VENDORIMAGE_PARTITION_SIZE := 536870912

# 文件系统类型
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_CACHEIMAGE_FILE_SYSTEM_TYPE := ext4

# HAL配置
PRODUCT_PACKAGES += \
    android.hardware.audio@6.0-impl \
    android.hardware.camera.provider@2.4-impl \
    android.hardware.graphics.composer@2.1-impl \
    android.hardware.sensors@1.0-impl \
    android.hardware.wifi@1.0-service

# 媒体配置
PRODUCT_COPY_FILES += \
    device/vendor/product_name/media_codecs.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs.xml \
    device/vendor/product_name/media_profiles.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_profiles.xml

# 音频配置
PRODUCT_COPY_FILES += \
    device/vendor/product_name/audio_policy.conf:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy.conf \
    device/vendor/product_name/mixer_paths.xml:$(TARGET_COPY_OUT_VENDOR)/etc/mixer_paths.xml
```

**5. 板级配置文件**

**文件：device/vendor/product_name/BoardConfig.mk**

```makefile
#
# Board Configuration
#

# 平台配置
TARGET_BOARD_PLATFORM := msm8953
TARGET_BOOTLOADER_BOARD_NAME := product_name

# 内核源码路径
TARGET_KERNEL_SOURCE := kernel/vendor/msm8953
TARGET_KERNEL_CONFIG := product_name_defconfig

# 编译内核
BOARD_KERNEL_IMAGE_NAME := Image.gz-dtb

# Recovery配置
TARGET_RECOVERY_FSTAB := device/vendor/product_name/fstab.device
BOARD_HAS_NO_SELECT_BUTTON := true
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# SELinux配置
BOARD_SEPOLICY_DIRS += \
    device/vendor/product_name/sepolicy

# Treble支持
PRODUCT_FULL_TREBLE_OVERRIDE := true
BOARD_VNDK_VERSION := current

# 加密支持
BOARD_USES_METADATA_PARTITION := true
```

### 系统属性定制

**文件：device/vendor/product_name/system.prop**

```properties
# 系统属性配置

# 性能优化
ro.config.low_ram=false
ro.config.max_starting_bg=8
dalvik.vm.heapsize=512m
dalvik.vm.heapstartsize=8m
dalvik.vm.heapgrowthlimit=192m
dalvik.vm.heaptargetutilization=0.75

# 显示配置
ro.sf.lcd_density=320
debug.sf.hw=1
debug.egl.hw=1
debug.composition.type=c2d
persist.hwc.mdpcomp.enable=true

# 音频配置
ro.audio.flinger_standbytime_ms=300
persist.audio.fluence.speaker=true
persist.audio.fluence.voicecall=true

# 网络配置
ro.telephony.default_network=9,9
persist.radio.multisim.config=dsds
persist.data.netmgrd.qos.enable=true

# 电源管理
pm.sleep_mode=1
ro.ril.disable.power.collapse=0
persist.sys.purgeable_assets=1

# 调试配置
persist.sys.usb.config=mtp,adb
ro.adb.secure=0
ro.debuggable=1

# 定制属性
ro.vendor.product.version=1.0
ro.vendor.build.date=2024-01-15
```



### 初始化脚本定制

**文件：device/vendor/product_name/init.rc**

```
# Android Init Script

on early-init
    # 设置SELinux
    write /sys/fs/selinux/checkreqprot 0
    
    # 挂载调试文件系统
    mount debugfs /sys/kernel/debug /sys/kernel/debug mode=0755

on init
    # 创建目录
    mkdir /mnt/vendor 0755 root system
    mkdir /mnt/vendor/persist 0771 system system
    
    # 设置权限
    chmod 0664 /sys/class/leds/lcd-backlight/brightness
    chown system system /sys/class/leds/lcd-backlight/brightness
    
    # 启动服务
    start vendor.hwcomposer-2-1

on boot
    # 设置CPU调度器
    write /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor interactive
    
    # 设置I/O调度器
    write /sys/block/mmcblk0/queue/scheduler cfq
    
    # 启动自定义服务
    start custom_service

# 自定义服务
service custom_service /vendor/bin/custom_daemon
    class main
    user system
    group system
    disabled
    oneshot

# 硬件服务
service vendor.hwcomposer-2-1 /vendor/bin/hw/android.hardware.graphics.composer@2.1-service
    class hal animation
    user system
    group graphics drmrpc
    capabilities SYS_NICE
    onrestart restart surfaceflinger

# 传感器服务
service vendor.sensors-hal-1-0 /vendor/bin/hw/android.hardware.sensors@1.0-service
    class hal
    user system
    group system input
```

### 文件系统表配置

**文件：device/vendor/product_name/fstab.device**

```
# Android fstab file
# <src>                                    <mnt_point>  <type>  <mnt_flags and options>  <fs_mgr_flags>

/dev/block/bootdevice/by-name/system      /system      ext4    ro,barrier=1             wait,slotselect,avb=vbmeta_system,logical,first_stage_mount
/dev/block/bootdevice/by-name/vendor      /vendor      ext4    ro,barrier=1             wait,slotselect,avb=vbmeta_system,logical,first_stage_mount
/dev/block/bootdevice/by-name/product     /product     ext4    ro,barrier=1             wait,slotselect,avb=vbmeta_system,logical,first_stage_mount
/dev/block/bootdevice/by-name/userdata    /data        ext4    noatime,nosuid,nodev,barrier=1,noauto_da_alloc  wait,check,fileencryption=ice,keydirectory=/metadata/vold/metadata_encryption,quota,reservedsize=128M
/dev/block/bootdevice/by-name/cache       /cache       ext4    noatime,nosuid,nodev,barrier=1  wait,check
/dev/block/bootdevice/by-name/persist     /mnt/vendor/persist  ext4    noatime,nosuid,nodev,barrier=1  wait
/dev/block/bootdevice/by-name/boot        /boot        emmc    defaults                 defaults
/dev/block/bootdevice/by-name/recovery    /recovery    emmc    defaults                 defaults
/dev/block/bootdevice/by-name/misc        /misc        emmc    defaults                 defaults

# SD卡
/devices/platform/soc/7864900.sdhci/mmc_host*  auto  auto  defaults  voldmanaged=sdcard1:auto,encryptable=userdata

# USB存储
/devices/platform/soc/7000000.ssusb/7000000.dwc3/xhci-hcd.0.auto*  auto  auto  defaults  voldmanaged=usb:auto
```

### 资源覆盖定制

**目录结构**：

```
device/vendor/product_name/overlay/
├── frameworks/
│   └── base/
│       ├── core/
│       │   └── res/
│       │       └── res/
│       │           ├── values/
│       │           │   ├── config.xml
│       │           │   └── strings.xml
│       │           └── drawable/
│       │               └── custom_icon.png
│       └── packages/
│           └── SystemUI/
│               └── res/
│                   └── values/
│                       └── config.xml
└── vendor/
    └── custom/
        └── res/
            └── values/
                └── config.xml
```

**文件：overlay/frameworks/base/core/res/res/values/config.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- 状态栏高度 -->
    <dimen name="status_bar_height">24dp</dimen>
    
    <!-- 导航栏高度 -->
    <dimen name="navigation_bar_height">48dp</dimen>
    
    <!-- 屏幕亮度配置 -->
    <integer-array name="config_autoBrightnessLevels">
        <item>10</item>
        <item>50</item>
        <item>100</item>
        <item>200</item>
        <item>400</item>
        <item>800</item>
        <item>1600</item>
    </integer-array>
    
    <!-- 电池容量 -->
    <integer name="config_batteryCapacity">4000</integer>
    
    <!-- 支持的网络类型 -->
    <string-array name="networkAttributes">
        <item>wifi,1,1,1,-1,true</item>
        <item>mobile,0,0,0,-1,true</item>
        <item>mobile_mms,2,0,2,60000,true</item>
        <item>mobile_supl,3,0,2,60000,true</item>
        <item>mobile_dun,4,0,2,60000,true</item>
        <item>mobile_hipri,5,0,3,60000,true</item>
        <item>bluetooth,7,7,2,-1,true</item>
    </string-array>
    
    <!-- 默认壁纸 -->
    <string name="default_wallpaper_component">com.android.wallpaper/.CustomWallpaper</string>
</resources>
```

**文件：overlay/frameworks/base/core/res/res/values/strings.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- 设备名称 -->
    <string name="device_name">Custom Device</string>
    
    <!-- 系统版本 -->
    <string name="build_version">1.0.0</string>
    
    <!-- 定制字符串 -->
    <string name="custom_feature_title">Custom Feature</string>
    <string name="custom_feature_summary">This is a custom feature</string>
</resources>
```



## BSP适配

### 内核适配

**1. 内核配置**

```bash
# 进入内核目录
cd kernel/vendor/msm8953

# 创建设备配置
cp arch/arm64/configs/msm8953_defconfig arch/arm64/configs/product_name_defconfig

# 编辑配置
vim arch/arm64/configs/product_name_defconfig
```

**添加必要的配置项**：

```kconfig
# 基础配置
CONFIG_LOCALVERSION="-product_name"
CONFIG_DEFAULT_HOSTNAME="product_name"

# 驱动配置
CONFIG_CUSTOM_DRIVER=y
CONFIG_CUSTOM_SENSOR=y
CONFIG_CUSTOM_CAMERA=y

# 文件系统
CONFIG_EXT4_FS=y
CONFIG_F2FS_FS=y
CONFIG_FUSE_FS=y

# 网络
CONFIG_NETFILTER=y
CONFIG_IP_NF_IPTABLES=y
CONFIG_WIRELESS=y
CONFIG_CFG80211=y

# 安全
CONFIG_SECURITY_SELINUX=y
CONFIG_SECURITY_SELINUX_BOOTPARAM=y
CONFIG_SECURITY_SELINUX_DEVELOP=y

# 调试
CONFIG_DEBUG_INFO=y
CONFIG_MAGIC_SYSRQ=y
CONFIG_DEBUG_KERNEL=y
```

**2. 设备树配置**

**文件：arch/arm64/boot/dts/vendor/product_name.dts**

```dts
/dts-v1/;

#include "msm8953.dtsi"
#include "msm8953-pinctrl.dtsi"

/ {
    model = "Vendor Product Name";
    compatible = "vendor,product-name", "qcom,msm8953";
    qcom,board-id = <8 0>;
    
    aliases {
        serial0 = &blsp1_uart2;
    };
    
    chosen {
        bootargs = "console=ttyMSM0,115200n8";
        stdout-path = "serial0:115200n8";
    };
    
    memory@80000000 {
        device_type = "memory";
        reg = <0x0 0x80000000 0x0 0x80000000>;
    };
    
    reserved-memory {
        #address-cells = <2>;
        #size-cells = <2>;
        ranges;
        
        modem_mem: modem@86800000 {
            reg = <0x0 0x86800000 0x0 0x6a00000>;
            no-map;
        };
        
        adsp_fw_mem: adsp_fw@8d200000 {
            reg = <0x0 0x8d200000 0x0 0x1100000>;
            no-map;
        };
    };
    
    soc {
        /* I2C配置 */
        i2c@78b6000 {
            status = "okay";
            
            touchscreen@38 {
                compatible = "vendor,touchscreen";
                reg = <0x38>;
                interrupt-parent = <&tlmm>;
                interrupts = <65 IRQ_TYPE_EDGE_FALLING>;
                reset-gpios = <&tlmm 64 GPIO_ACTIVE_LOW>;
                vdd-supply = <&pm8953_l10>;
                vio-supply = <&pm8953_l5>;
            };
            
            accelerometer@68 {
                compatible = "vendor,accelerometer";
                reg = <0x68>;
                interrupt-parent = <&tlmm>;
                interrupts = <42 IRQ_TYPE_EDGE_RISING>;
                vdd-supply = <&pm8953_l10>;
            };
        };
        
        /* SPI配置 */
        spi@78b7000 {
            status = "okay";
            
            spidev@0 {
                compatible = "vendor,spidev";
                reg = <0>;
                spi-max-frequency = <50000000>;
            };
        };
        
        /* GPIO配置 */
        gpio-keys {
            compatible = "gpio-keys";
            
            vol-up {
                label = "volume_up";
                gpios = <&tlmm 85 GPIO_ACTIVE_LOW>;
                linux,code = <KEY_VOLUMEUP>;
                debounce-interval = <15>;
            };
            
            vol-down {
                label = "volume_down";
                gpios = <&tlmm 86 GPIO_ACTIVE_LOW>;
                linux,code = <KEY_VOLUMEDOWN>;
                debounce-interval = <15>;
            };
        };
        
        /* LED配置 */
        leds {
            compatible = "gpio-leds";
            
            led-red {
                label = "red";
                gpios = <&tlmm 45 GPIO_ACTIVE_HIGH>;
                default-state = "off";
            };
            
            led-green {
                label = "green";
                gpios = <&tlmm 46 GPIO_ACTIVE_HIGH>;
                default-state = "off";
            };
            
            led-blue {
                label = "blue";
                gpios = <&tlmm 47 GPIO_ACTIVE_HIGH>;
                default-state = "off";
            };
        };
    };
};

/* 显示配置 */
&mdss_dsi0 {
    qcom,dsi-pref-prim-pan = <&dsi_panel>;
    pinctrl-names = "mdss_default", "mdss_sleep";
    pinctrl-0 = <&mdss_dsi_active &mdss_te_active>;
    pinctrl-1 = <&mdss_dsi_suspend &mdss_te_suspend>;
    
    qcom,platform-reset-gpio = <&tlmm 61 0>;
    qcom,platform-te-gpio = <&tlmm 24 0>;
};

/* 触摸屏配置 */
&i2c_3 {
    status = "okay";
    
    touchscreen@38 {
        compatible = "vendor,touchscreen";
        reg = <0x38>;
        interrupt-parent = <&tlmm>;
        interrupts = <65 IRQ_TYPE_EDGE_FALLING>;
        vdd-supply = <&pm8953_l10>;
        vio-supply = <&pm8953_l5>;
        
        touchscreen-size-x = <1080>;
        touchscreen-size-y = <1920>;
        touchscreen-max-pressure = <255>;
    };
};

/* 摄像头配置 */
&cci {
    actuator0: qcom,actuator@0 {
        cell-index = <0>;
        reg = <0x0>;
        compatible = "qcom,actuator";
        qcom,cci-master = <0>;
    };
    
    eeprom0: qcom,eeprom@0 {
        cell-index = <0>;
        reg = <0x0>;
        compatible = "qcom,eeprom";
        qcom,cci-master = <0>;
        qcom,eeprom-name = "vendor_eeprom";
        qcom,slave-addr = <0xa0>;
    };
    
    qcom,camera@0 {
        cell-index = <0>;
        compatible = "qcom,camera";
        reg = <0x0>;
        qcom,csiphy-sd-index = <0>;
        qcom,csid-sd-index = <0>;
        qcom,mount-angle = <90>;
        qcom,led-flash-src = <&led_flash0>;
        qcom,actuator-src = <&actuator0>;
        qcom,eeprom-src = <&eeprom0>;
        cam_vdig-supply = <&pm8953_l23>;
        cam_vio-supply = <&pm8953_l6>;
        cam_vana-supply = <&pm8953_l22>;
        qcom,cam-vreg-name = "cam_vdig", "cam_vio", "cam_vana";
        qcom,cam-vreg-min-voltage = <1200000 0 2800000>;
        qcom,cam-vreg-max-voltage = <1200000 0 2800000>;
        qcom,cam-vreg-op-mode = <105000 0 80000>;
        pinctrl-names = "cam_default", "cam_suspend";
        pinctrl-0 = <&cam_sensor_mclk0_default &cam_sensor_rear_default>;
        pinctrl-1 = <&cam_sensor_mclk0_sleep &cam_sensor_rear_sleep>;
        gpios = <&tlmm 26 0>,
                <&tlmm 36 0>,
                <&tlmm 35 0>;
        qcom,gpio-reset = <1>;
        qcom,gpio-standby = <2>;
        qcom,gpio-req-tbl-num = <0 1 2>;
        qcom,gpio-req-tbl-flags = <1 0 0>;
        qcom,gpio-req-tbl-label = "CAMIF_MCLK0",
                                  "CAM_RESET0",
                                  "CAM_STANDBY0";
        qcom,sensor-position = <0>;
        qcom,sensor-mode = <0>;
        qcom,cci-master = <0>;
        status = "ok";
        clocks = <&clock_gcc clk_mclk0_clk_src>,
                 <&clock_gcc clk_gcc_camss_mclk0_clk>;
        clock-names = "cam_src_clk", "cam_clk";
        qcom,clock-rates = <24000000 0>;
    };
};
```

### HAL层适配

**1. Audio HAL适配**

**文件：device/vendor/product_name/audio/audio_hw.c**

```c
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <sys/time.h>
#include <stdlib.h>
#include <math.h>

#include <cutils/log.h>
#include <cutils/str_parms.h>
#include <cutils/properties.h>

#include <hardware/hardware.h>
#include <system/audio.h>
#include <hardware/audio.h>

#define LOG_TAG "AudioHAL"

struct audio_device {
    struct audio_hw_device hw_device;
    
    pthread_mutex_t lock;
    audio_devices_t out_device;
    audio_devices_t in_device;
    bool mic_mute;
    
    struct audio_stream_out *active_output;
    struct audio_stream_in *active_input;
};

struct audio_stream_out {
    struct audio_stream_out stream;
    
    pthread_mutex_t lock;
    uint32_t sample_rate;
    audio_channel_mask_t channel_mask;
    audio_format_t format;
    size_t frame_count;
    
    struct audio_device *dev;
};

static uint32_t out_get_sample_rate(const struct audio_stream *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    return out->sample_rate;
}

static int out_set_sample_rate(struct audio_stream *stream, uint32_t rate)
{
    return -ENOSYS;
}

static size_t out_get_buffer_size(const struct audio_stream *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    size_t size = (out->frame_count * audio_stream_out_frame_size(stream));
    return size;
}

static audio_channel_mask_t out_get_channels(const struct audio_stream *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    return out->channel_mask;
}

static audio_format_t out_get_format(const struct audio_stream *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    return out->format;
}

static int out_set_format(struct audio_stream *stream, audio_format_t format)
{
    return -ENOSYS;
}

static int out_standby(struct audio_stream *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    struct audio_device *adev = out->dev;
    
    pthread_mutex_lock(&out->lock);
    pthread_mutex_lock(&adev->lock);
    
    // 实现standby逻辑
    
    pthread_mutex_unlock(&adev->lock);
    pthread_mutex_unlock(&out->lock);
    
    return 0;
}

static ssize_t out_write(struct audio_stream_out *stream, const void* buffer,
                        size_t bytes)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    struct audio_device *adev = out->dev;
    
    pthread_mutex_lock(&out->lock);
    
    // 实现音频输出逻辑
    // 写入音频数据到硬件
    
    pthread_mutex_unlock(&out->lock);
    
    return bytes;
}

static int out_get_render_position(const struct audio_stream_out *stream,
                                   uint32_t *dsp_frames)
{
    return -EINVAL;
}

static int adev_open_output_stream(struct audio_hw_device *dev,
                                   audio_io_handle_t handle,
                                   audio_devices_t devices,
                                   audio_output_flags_t flags,
                                   struct audio_config *config,
                                   struct audio_stream_out **stream_out,
                                   const char *address)
{
    struct audio_device *adev = (struct audio_device *)dev;
    struct audio_stream_out *out;
    int ret;
    
    out = (struct audio_stream_out *)calloc(1, sizeof(struct audio_stream_out));
    if (!out)
        return -ENOMEM;
    
    out->stream.common.get_sample_rate = out_get_sample_rate;
    out->stream.common.set_sample_rate = out_set_sample_rate;
    out->stream.common.get_buffer_size = out_get_buffer_size;
    out->stream.common.get_channels = out_get_channels;
    out->stream.common.get_format = out_get_format;
    out->stream.common.set_format = out_set_format;
    out->stream.common.standby = out_standby;
    out->stream.write = out_write;
    out->stream.get_render_position = out_get_render_position;
    
    out->dev = adev;
    out->sample_rate = config->sample_rate;
    out->channel_mask = config->channel_mask;
    out->format = config->format;
    out->frame_count = 1024;
    
    pthread_mutex_init(&out->lock, NULL);
    
    *stream_out = &out->stream;
    
    return 0;
}

static void adev_close_output_stream(struct audio_hw_device *dev,
                                    struct audio_stream_out *stream)
{
    struct audio_stream_out *out = (struct audio_stream_out *)stream;
    
    pthread_mutex_destroy(&out->lock);
    free(stream);
}

static int adev_set_parameters(struct audio_hw_device *dev, const char *kvpairs)
{
    struct audio_device *adev = (struct audio_device *)dev;
    struct str_parms *parms;
    char *str;
    char value[32];
    int ret;
    
    parms = str_parms_create_str(kvpairs);
    
    // 处理参数
    
    str_parms_destroy(parms);
    return ret;
}

static char * adev_get_parameters(const struct audio_hw_device *dev,
                                 const char *keys)
{
    return strdup("");
}

static int adev_init_check(const struct audio_hw_device *dev)
{
    return 0;
}

static int adev_set_voice_volume(struct audio_hw_device *dev, float volume)
{
    return -ENOSYS;
}

static int adev_set_master_volume(struct audio_hw_device *dev, float volume)
{
    return -ENOSYS;
}

static int adev_set_mode(struct audio_hw_device *dev, audio_mode_t mode)
{
    return 0;
}

static int adev_set_mic_mute(struct audio_hw_device *dev, bool state)
{
    struct audio_device *adev = (struct audio_device *)dev;
    
    pthread_mutex_lock(&adev->lock);
    adev->mic_mute = state;
    pthread_mutex_unlock(&adev->lock);
    
    return 0;
}

static int adev_get_mic_mute(const struct audio_hw_device *dev, bool *state)
{
    struct audio_device *adev = (struct audio_device *)dev;
    
    *state = adev->mic_mute;
    
    return 0;
}

static int adev_close(hw_device_t *device)
{
    struct audio_device *adev = (struct audio_device *)device;
    
    pthread_mutex_destroy(&adev->lock);
    free(device);
    
    return 0;
}

static int adev_open(const hw_module_t* module, const char* name,
                    hw_device_t** device)
{
    struct audio_device *adev;
    
    if (strcmp(name, AUDIO_HARDWARE_INTERFACE) != 0)
        return -EINVAL;
    
    adev = calloc(1, sizeof(struct audio_device));
    if (!adev)
        return -ENOMEM;
    
    adev->hw_device.common.tag = HARDWARE_DEVICE_TAG;
    adev->hw_device.common.version = AUDIO_DEVICE_API_VERSION_2_0;
    adev->hw_device.common.module = (struct hw_module_t *) module;
    adev->hw_device.common.close = adev_close;
    
    adev->hw_device.init_check = adev_init_check;
    adev->hw_device.set_voice_volume = adev_set_voice_volume;
    adev->hw_device.set_master_volume = adev_set_master_volume;
    adev->hw_device.set_mode = adev_set_mode;
    adev->hw_device.set_mic_mute = adev_set_mic_mute;
    adev->hw_device.get_mic_mute = adev_get_mic_mute;
    adev->hw_device.set_parameters = adev_set_parameters;
    adev->hw_device.get_parameters = adev_get_parameters;
    adev->hw_device.open_output_stream = adev_open_output_stream;
    adev->hw_device.close_output_stream = adev_close_output_stream;
    
    pthread_mutex_init(&adev->lock, NULL);
    
    *device = &adev->hw_device.common;
    
    return 0;
}

static struct hw_module_methods_t hal_module_methods = {
    .open = adev_open,
};

struct audio_module HAL_MODULE_INFO_SYM = {
    .common = {
        .tag = HARDWARE_MODULE_TAG,
        .module_api_version = AUDIO_MODULE_API_VERSION_0_1,
        .hal_api_version = HARDWARE_HAL_API_VERSION,
        .id = AUDIO_HARDWARE_MODULE_ID,
        .name = "Custom Audio HW HAL",
        .author = "Vendor Inc.",
        .methods = &hal_module_methods,
    },
};
```



## 系统优化

### 启动优化

**1. 分析启动时间**

```bash
# 使用bootchart分析启动
adb shell 'echo 1 > /data/bootchart/enabled'
adb reboot

# 等待启动完成后获取数据
adb pull /data/bootchart bootchart/
bootchart bootchart/

# 使用systrace分析
systrace.py --time=10 -o trace.html sched freq idle am wm gfx view binder_driver hal dalvik camera input res
```

**2. 优化init.rc**

```
# 并行启动服务
service service1 /system/bin/service1
    class early_hal
    user system
    group system
    
service service2 /system/bin/service2
    class early_hal
    user system
    group system

# 延迟启动非关键服务
service non_critical /system/bin/non_critical
    class late_start
    user system
    group system
    disabled
    
on property:sys.boot_completed=1
    start non_critical
```

**3. 预加载优化**

**文件：frameworks/base/config/preloaded-classes**

```
# 预加载常用类
java.lang.String
java.lang.Integer
java.util.ArrayList
java.util.HashMap
android.app.Activity
android.view.View
android.widget.TextView
```

### 性能优化

**1. CPU调度优化**

```bash
# 设置CPU调度器
echo "interactive" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# 设置CPU频率范围
echo 300000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
echo 2016000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq

# 设置interactive调度器参数
echo 20000 > /sys/devices/system/cpu/cpufreq/interactive/timer_rate
echo 80 > /sys/devices/system/cpu/cpufreq/interactive/go_hispeed_load
echo 1401600 > /sys/devices/system/cpu/cpufreq/interactive/hispeed_freq
```

**2. 内存优化**

```properties
# system.prop配置
dalvik.vm.heapstartsize=8m
dalvik.vm.heapgrowthlimit=192m
dalvik.vm.heapsize=512m
dalvik.vm.heaptargetutilization=0.75
dalvik.vm.heapminfree=512k
dalvik.vm.heapmaxfree=8m

# Low Memory Killer配置
ro.config.low_ram=false
ro.lmk.critical=0
ro.lmk.critical_upgrade=false
ro.lmk.upgrade_pressure=100
ro.lmk.downgrade_pressure=100
ro.lmk.kill_heaviest_task=true
```

**3. I/O优化**

```bash
# 设置I/O调度器
echo "cfq" > /sys/block/mmcblk0/queue/scheduler

# 设置读写缓存
echo 2048 > /sys/block/mmcblk0/queue/read_ahead_kb
echo 128 > /sys/block/mmcblk0/queue/nr_requests

# 禁用I/O统计（提升性能）
echo 0 > /sys/block/mmcblk0/queue/iostats
```

### 电源管理优化

**1. 休眠策略**

```
# init.rc配置
on boot
    # 设置休眠模式
    write /sys/power/mem_sleep deep
    
    # 配置wakelock超时
    write /sys/power/wake_lock_timeout 5000
    
    # 配置自动休眠延迟
    write /sys/power/autosleep_delay 30000
```

**2. 动态电压频率调节（DVFS）**

```c
// 实现DVFS策略
static void dvfs_update_policy(int load)
{
    if (load > 80) {
        // 高负载：提升频率
        set_cpu_freq(MAX_FREQ);
        set_gpu_freq(MAX_FREQ);
    } else if (load > 50) {
        // 中等负载：中等频率
        set_cpu_freq(MID_FREQ);
        set_gpu_freq(MID_FREQ);
    } else {
        // 低负载：降低频率
        set_cpu_freq(MIN_FREQ);
        set_gpu_freq(MIN_FREQ);
    }
}
```

## OTA升级系统

### OTA包制作

**1. 生成OTA包**

```bash
# 编译目标版本
cd ~/aosp
source build/envsetup.sh
lunch product_name-userdebug
make -j$(nproc)

# 生成完整OTA包
make otapackage

# 输出文件
ls out/target/product/product_name/product_name-ota-*.zip
```

**2. 生成增量OTA包**

```bash
# 需要旧版本的target_files
OLD_TARGET_FILES=out/target/product/product_name/obj/PACKAGING/target_files_intermediates/product_name-target_files-old.zip
NEW_TARGET_FILES=out/target/product/product_name/obj/PACKAGING/target_files_intermediates/product_name-target_files-new.zip

# 生成增量包
./build/tools/releasetools/ota_from_target_files \
    -i $OLD_TARGET_FILES \
    $NEW_TARGET_FILES \
    incremental_ota.zip
```

**3. OTA包签名**

```bash
# 生成密钥
development/tools/make_key releasekey '/C=US/ST=California/L=Mountain View/O=Android/OU=Android/CN=Android/emailAddress=android@android.com'

# 签名OTA包
java -Xmx2048m -jar out/host/linux-x86/framework/signapk.jar \
    -w build/target/product/security/testkey.x509.pem \
    build/target/product/security/testkey.pk8 \
    unsigned_ota.zip \
    signed_ota.zip
```

### OTA升级实现

**1. Recovery模式配置**

**文件：bootable/recovery/recovery.cpp**

```cpp
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "recovery.h"
#include "install.h"
#include "roots.h"
#include "ui.h"

static const char *COMMAND_FILE = "/cache/recovery/command";
static const char *LOG_FILE = "/cache/recovery/log";
static const char *LAST_INSTALL_FILE = "/cache/recovery/last_install";

int main(int argc, char **argv) {
    // 初始化Recovery UI
    RecoveryUI* ui = device_ui;
    ui->Init();
    ui->SetBackground(RecoveryUI::NONE);
    
    // 加载volume表
    load_volume_table();
    
    // 确保/cache挂载
    ensure_path_mounted("/cache");
    
    // 读取命令
    std::vector<std::string> args;
    get_args(&args);
    
    // 处理命令
    int status = INSTALL_SUCCESS;
    
    if (args.size() > 1 && args[0] == "--update_package") {
        // OTA升级
        status = install_package(args[1].c_str(), &should_wipe_cache, 
                                TEMPORARY_INSTALL_FILE, true, 0);
        
        if (status == INSTALL_SUCCESS && should_wipe_cache) {
            wipe_cache(false, ui);
        }
        
        if (status != INSTALL_SUCCESS) {
            ui->SetBackground(RecoveryUI::ERROR);
            ui->Print("Installation aborted.\n");
        } else if (!ui->IsTextVisible()) {
            return 0;  // 重启到系统
        } else {
            ui->Print("\nInstall from %s complete.\n", args[1].c_str());
        }
    }
    
    // 显示菜单
    for (;;) {
        finish_recovery(NULL);
        ui->SetBackground(RecoveryUI::NO_COMMAND);
        
        int chosen_item = get_menu_selection(headers, items, 0, 0, device);
        
        switch (chosen_item) {
            case ITEM_REBOOT:
                return 0;
                
            case ITEM_WIPE_DATA:
                wipe_data(ui->IsTextVisible(), device);
                if (!ui->IsTextVisible()) return 0;
                break;
                
            case ITEM_WIPE_CACHE:
                wipe_cache(ui->IsTextVisible(), device);
                if (!ui->IsTextVisible()) return 0;
                break;
                
            case ITEM_APPLY_UPDATE:
                apply_from_sdcard(device, &should_wipe_cache);
                break;
        }
    }
    
    return 0;
}
```

**2. OTA升级脚本**

**文件：device/vendor/product_name/ota/updater-script**

```
# OTA升级脚本

ui_print("========================================");
ui_print("  Custom ROM OTA Update");
ui_print("  Version: 1.0.0");
ui_print("========================================");

# 检查设备
assert(getprop("ro.product.device") == "product_name" || 
       getprop("ro.build.product") == "product_name");

ui_print("Mounting partitions...");
mount("ext4", "EMMC", "/dev/block/bootdevice/by-name/system", "/system");
mount("ext4", "EMMC", "/dev/block/bootdevice/by-name/vendor", "/vendor");

ui_print("Extracting files...");
package_extract_dir("system", "/system");
package_extract_dir("vendor", "/vendor");

ui_print("Setting permissions...");
set_perm_recursive(0, 0, 0755, 0644, "/system");
set_perm_recursive(0, 2000, 0755, 0755, "/system/bin");
set_perm(0, 3003, 02750, "/system/bin/netcfg");
set_perm(0, 3004, 02755, "/system/bin/ping");

ui_print("Installing boot image...");
package_extract_file("boot.img", "/dev/block/bootdevice/by-name/boot");

ui_print("Unmounting partitions...");
unmount("/system");
unmount("/vendor");

ui_print("========================================");
ui_print("  Update complete!");
ui_print("========================================");
```

**3. 应用层OTA触发**

**文件：packages/apps/Settings/src/com/android/settings/system/SystemUpdatePreferenceController.java**

```java
package com.android.settings.system;

import android.content.Context;
import android.content.Intent;
import android.os.RecoverySystem;
import android.os.UpdateEngine;
import android.os.UpdateEngineCallback;

import androidx.preference.Preference;

public class SystemUpdatePreferenceController {
    private Context mContext;
    private UpdateEngine mUpdateEngine;
    
    public SystemUpdatePreferenceController(Context context) {
        mContext = context;
        mUpdateEngine = new UpdateEngine();
    }
    
    public void checkForUpdates() {
        // 检查更新
        String updateUrl = "https://update.example.com/check";
        // 实现更新检查逻辑
    }
    
    public void downloadUpdate(String updateUrl) {
        // 下载OTA包
        // 实现下载逻辑
    }
    
    public void installUpdate(String otaPackagePath) {
        try {
            // 验证OTA包
            RecoverySystem.verifyPackage(new File(otaPackagePath), 
                                        null, null);
            
            // 安装OTA包
            RecoverySystem.installPackage(mContext, 
                                         new File(otaPackagePath));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private class UpdateCallback extends UpdateEngineCallback {
        @Override
        public void onStatusUpdate(int status, float percent) {
            // 更新进度回调
        }
        
        @Override
        public void onPayloadApplicationComplete(int errorCode) {
            // 更新完成回调
            if (errorCode == UpdateEngine.ErrorCodeConstants.SUCCESS) {
                // 重启到recovery
                rebootToRecovery();
            }
        }
    }
    
    private void rebootToRecovery() {
        try {
            RecoverySystem.rebootWipeUserData(mContext);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```



## 调试与测试

### 系统调试

**1. Logcat日志分析**

```bash
# 查看所有日志
adb logcat

# 过滤特定标签
adb logcat -s TAG_NAME

# 保存日志到文件
adb logcat > logcat.txt

# 清除日志缓冲区
adb logcat -c

# 查看特定级别日志
adb logcat *:E  # 只显示Error级别

# 查看特定进程日志
adb logcat --pid=<pid>
```

**2. 系统跟踪**

```bash
# 使用systrace
systrace.py --time=10 -o trace.html \
    sched freq idle am wm gfx view binder_driver hal dalvik

# 使用perfetto
adb shell perfetto \
    -c - --txt \
    -o /data/misc/perfetto-traces/trace \
    < trace_config.pbtxt

# 获取trace文件
adb pull /data/misc/perfetto-traces/trace
```

**3. 性能分析**

```bash
# CPU性能分析
adb shell top -m 10

# 内存分析
adb shell dumpsys meminfo <package_name>

# 查看进程信息
adb shell ps -A

# 查看系统服务
adb shell dumpsys

# 查看特定服务
adb shell dumpsys activity
adb shell dumpsys window
adb shell dumpsys package
```

### CTS/VTS测试

**1. CTS测试**

```bash
# 下载CTS测试套件
# https://source.android.com/compatibility/cts/downloads

# 运行CTS测试
cd android-cts
./tools/cts-tradefed

# 在cts-tf控制台中
run cts --plan CTS

# 运行特定模块
run cts -m CtsMediaTestCases

# 查看测试结果
ls results/
```

**2. VTS测试**

```bash
# 运行VTS测试
cd android-vts
./tools/vts-tradefed

# 在vts-tf控制台中
run vts

# 运行特定HAL测试
run vts -m VtsHalAudioV6_0Target
```

## 总结

通过本教程，你应该已经掌握了：

- ✅ Android系统架构和AOSP项目结构
- ✅ AOSP源码下载和编译流程
- ✅ Android系统定制和功能裁剪
- ✅ BSP适配方法和HAL层开发
- ✅ 系统性能优化技术
- ✅ OTA升级系统的设计与实现
- ✅ 系统调试和测试方法

### 关键要点

1. **AOSP编译**
   - 环境准备和依赖安装
   - 源码下载和同步
   - 编译配置和优化
   - 常见问题解决

2. **系统定制**
   - 设备配置创建
   - 产品属性定制
   - 资源覆盖机制
   - 初始化脚本配置

3. **BSP适配**
   - 内核配置和编译
   - 设备树配置
   - HAL层实现
   - 驱动集成

4. **系统优化**
   - 启动时间优化
   - 性能调优
   - 内存管理
   - 电源管理

5. **OTA升级**
   - OTA包制作
   - 升级脚本编写
   - Recovery实现
   - 应用层触发

## 实践练习

### 练习1：编译AOSP

**任务**：下载并编译AOSP源码

**要求**：
1. 配置编译环境
2. 下载Android 13源码
3. 选择合适的编译目标
4. 成功编译系统镜像
5. 在模拟器中运行

**提示**：
- 确保足够的磁盘空间
- 使用ccache加速编译
- 记录编译时间和遇到的问题

### 练习2：创建自定义设备

**任务**：创建一个自定义Android设备配置

**要求**：
1. 创建设备配置目录
2. 编写产品配置文件
3. 定制系统属性
4. 添加自定义应用
5. 编译并测试

**提示**：
- 参考现有设备配置
- 使用overlay覆盖资源
- 测试所有功能

### 练习3：实现OTA升级

**任务**：实现完整的OTA升级功能

**要求**：
1. 制作OTA升级包
2. 实现升级检查功能
3. 实现下载和安装
4. 测试升级流程
5. 处理升级失败情况

**提示**：
- 使用增量OTA减小包大小
- 实现断点续传
- 添加升级进度显示
- 实现回滚机制

## 下一步学习

建议按以下顺序继续学习：

### 1. 深入学习
- Android Framework源码分析
- Android性能优化高级技术
- Android安全机制详解
- Android虚拟化技术

### 2. 相关主题
- [Android驱动开发](../intermediate/02-android-driver.html)
- [Android HAL层开发](../intermediate/01-android-hal.html)
- [Linux系统构建](../../05-embedded-linux/advanced/01-complete-linux-system.html)

### 3. 实战项目
- 定制Android车载系统
- 开发Android IoT设备
- 实现Android TV系统
- 构建Android工业控制系统

## 参考资料

### 官方文档

1. **Android开源项目**
   - https://source.android.com/
   - AOSP官方文档

2. **Android兼容性**
   - https://source.android.com/compatibility
   - CTS/VTS测试文档

3. **Android安全**
   - https://source.android.com/security
   - 安全最佳实践

### 推荐书籍

1. **《深入理解Android内核设计思想》**
   - 作者：林学森
   - Android内核详解

2. **《Android系统源代码情景分析》**
   - 作者：罗升阳
   - 源码分析经典

3. **《Android Internals》**
   - 作者：Jonathan Levin
   - 系统内部机制

### 在线资源

1. **AOSP源码在线浏览**
   - https://cs.android.com/
   - 源码搜索和浏览

2. **Android开发者社区**
   - https://developer.android.com/
   - 官方开发文档

3. **XDA Developers**
   - https://www.xda-developers.com/
   - ROM开发社区

### 开发工具

**必备工具**：
- Android Studio
- Android SDK
- Android NDK
- Repo工具

**编译工具**：
- GCC/Clang交叉编译器
- Make/Ninja构建系统
- Python脚本工具
- Git版本控制

**调试工具**：
- ADB（Android Debug Bridge）
- Logcat日志工具
- Systrace性能分析
- Perfetto跟踪工具

**测试工具**：
- CTS（Compatibility Test Suite）
- VTS（Vendor Test Suite）
- GTS（GMS Test Suite）
- Monkey压力测试

## 常见问题解答

### Q1: AOSP编译需要多长时间？

**A**: 

编译时间取决于多个因素：

**硬件配置影响**：
- CPU核心数：越多越快
- 内存大小：建议32GB以上
- 硬盘类型：SSD比HDD快很多
- 网络速度：影响源码下载

**典型编译时间**：
- 高配置（32核/64GB/NVMe SSD）：1-2小时
- 中配置（16核/32GB/SATA SSD）：2-4小时
- 低配置（8核/16GB/HDD）：6-12小时

**加速方法**：
- 使用ccache缓存
- 增量编译
- 使用预编译工具链
- 分布式编译

### Q2: 如何解决编译错误？

**A**: 

**常见错误类型**：

1. **依赖缺失**：
```bash
# 安装缺失的依赖
sudo apt-get install <package_name>
```

2. **内存不足**：
```bash
# 减少并行任务
make -j4

# 增加swap
sudo fallocate -l 16G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. **磁盘空间不足**：
```bash
# 清理编译输出
make clean

# 删除不需要的文件
rm -rf out/target/common/obj/JAVA_LIBRARIES
```

4. **代码错误**：
```bash
# 查看详细错误
make showcommands

# 单独编译失败模块
make <module_name>
```

### Q3: 如何定制系统UI？

**A**: 

**定制方法**：

1. **使用Overlay**：
```
device/vendor/product/overlay/
└── frameworks/base/core/res/res/
    ├── values/
    │   ├── colors.xml
    │   ├── dimens.xml
    │   └── styles.xml
    └── drawable/
        └── custom_icon.png
```

2. **修改SystemUI**：
```java
// frameworks/base/packages/SystemUI/src/
// 修改状态栏、导航栏等
```

3. **自定义Launcher**：
```
// 开发自己的Launcher应用
// 设置为默认Launcher
```

4. **主题定制**：
```xml
<!-- 定义主题 -->
<style name="CustomTheme" parent="@android:style/Theme.Material">
    <item name="android:colorPrimary">@color/custom_primary</item>
    <item name="android:colorAccent">@color/custom_accent</item>
</style>
```

### Q4: 如何优化系统性能？

**A**: 

**优化策略**：

1. **启动优化**：
   - 并行启动服务
   - 延迟加载非关键组件
   - 优化预加载类列表
   - 减少启动动画时间

2. **运行时优化**：
   - 调整虚拟机参数
   - 优化内存管理
   - 配置CPU调度器
   - 优化I/O调度

3. **应用优化**：
   - 移除不需要的系统应用
   - 优化应用启动
   - 减少后台服务
   - 限制自启动应用

4. **图形优化**：
   - 启用硬件加速
   - 优化渲染管线
   - 减少过度绘制
   - 使用GPU合成

### Q5: 如何保证系统安全？

**A**: 

**安全措施**：

1. **SELinux配置**：
   - 使用enforcing模式
   - 编写完善的策略
   - 定期审计策略
   - 测试策略有效性

2. **权限管理**：
   - 最小权限原则
   - 运行时权限检查
   - 签名验证
   - 权限审计

3. **加密保护**：
   - 全盘加密
   - 文件级加密
   - 安全启动
   - 密钥管理

4. **更新机制**：
   - 及时安全更新
   - OTA签名验证
   - 回滚保护
   - 更新日志

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
