---
title: "视频编解码技术详解：H.264/H.265原理与应用"
description: "本文深入介绍视频编解码技术的核心原理，包括H.264/H.265编码标准、编解码流程、硬件加速技术以及在嵌入式系统中的应用场景"
slug: "video-codec-h264-h265"

# 分类信息
domain: "中间件层"
module: "多媒体处理"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 视频编解码
  - H.264
  - H.265
  - 多媒体
  - 硬件加速
  - 视频压缩
prerequisites:
  - "audio-basics"
  - "dma-basics"
related_contents:
  - "streaming-media"
  - "hardware-acceleration"

# 学习信息
estimated_time: 55
difficulty_score: 6

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
  - 视频编解码
  - H.264编码
  - H.265/HEVC
  - 视频压缩算法
  - 硬件编解码
  - 嵌入式视频处理
cover_image: ""
---

# 视频编解码技术详解：H.264/H.265原理与应用

## 概述

视频编解码（Video Codec）是数字视频处理的核心技术，通过压缩算法将原始视频数据转换为更小的文件大小，同时在解码时恢复视频内容。本文将深入探讨H.264和H.265两种主流视频编码标准的原理、特点及其在嵌入式系统中的应用。

**为什么需要视频编解码？**

原始视频数据量巨大。以1080p@30fps视频为例：
- 分辨率：1920×1080像素
- 帧率：30帧/秒
- 色深：24位（RGB各8位）
- 数据率：1920 × 1080 × 30 × 24 = 1.49 Gbps ≈ 186 MB/s

这样的数据量对存储和传输都是巨大挑战。通过视频编解码技术，可以将数据压缩到原始大小的1%甚至更小，使得视频应用成为可能。

## 视频编解码基础概念

### 视频压缩原理

视频压缩利用了三种冗余：

**1. 空间冗余（Spatial Redundancy）**
- 同一帧内相邻像素往往相似
- 通过帧内预测和变换编码消除
- 例如：蓝天区域的像素值变化很小

**2. 时间冗余（Temporal Redundancy）**
- 连续帧之间内容高度相似
- 通过运动估计和运动补偿消除
- 例如：静止背景在多帧中保持不变

**3. 视觉冗余（Perceptual Redundancy）**
- 人眼对某些信息不敏感
- 通过量化过程去除
- 例如：高频细节、色度信息

### 关键术语

**帧类型**：
- **I帧（Intra Frame）**：关键帧，独立编码，不依赖其他帧
- **P帧（Predicted Frame）**：预测帧，参考前面的I帧或P帧
- **B帧（Bidirectional Frame）**：双向预测帧，参考前后帧

**GOP（Group of Pictures）**：
- 一组连续的视频帧，以I帧开始
- 典型结构：IBBPBBPBBPBBI...
- GOP越长，压缩率越高，但随机访问性能越差

**码率控制**：
- **CBR（Constant Bit Rate）**：恒定码率，适合流媒体传输
- **VBR（Variable Bit Rate）**：可变码率，适合本地存储
- **ABR（Average Bit Rate）**：平均码率，兼顾质量和大小

**分辨率与帧率**：
- 常见分辨率：720p (1280×720)、1080p (1920×1080)、4K (3840×2160)
- 常见帧率：24fps（电影）、30fps（标清）、60fps（高清）

## H.264/AVC编码标准

### H.264简介

H.264（也称为AVC - Advanced Video Coding）是目前应用最广泛的视频编码标准，由ITU-T和ISO/IEC联合制定。

**主要特点**：
- 相比MPEG-2，压缩效率提高50%以上
- 支持多种应用场景（广播、流媒体、存储）
- 良好的网络适应性
- 广泛的硬件支持

**应用场景**：
- 蓝光光盘
- 数字电视广播
- 视频会议
- 网络视频（YouTube、Netflix等）
- 监控摄像头
- 移动设备视频

### H.264编码流程

H.264编码器的基本处理流程：

```
原始视频
    ↓
[帧内/帧间预测] → 预测块
    ↓
[残差计算] → 残差数据
    ↓
[变换编码] → DCT系数
    ↓
[量化] → 量化系数
    ↓
[熵编码] → 压缩码流
    ↓
编码视频
```

**详细步骤说明**：

1. **预测（Prediction）**
   - 帧内预测：利用当前帧已编码的相邻块预测当前块
   - 帧间预测：利用参考帧通过运动估计预测当前块
   - 生成预测块，计算残差（原始块 - 预测块）

2. **变换（Transform）**
   - 对残差数据进行整数DCT变换
   - 将空间域信号转换到频率域
   - H.264使用4×4或8×8整数变换

3. **量化（Quantization）**
   - 将变换系数除以量化步长
   - 这是有损压缩的主要来源
   - 量化参数（QP）控制压缩质量和码率

4. **熵编码（Entropy Coding）**
   - 使用CAVLC或CABAC算法
   - 无损压缩，进一步减小数据量
   - CABAC效率更高但计算复杂度更大

5. **环路滤波（Loop Filter）**
   - 去块滤波，消除块效应
   - 提高主观视觉质量
   - 改善参考帧质量

### H.264解码流程

解码过程是编码的逆过程：

```
编码码流
    ↓
[熵解码] → 量化系数
    ↓
[反量化] → DCT系数
    ↓
[反变换] → 残差数据
    ↓
[预测重建] → 预测块
    ↓
[相加] → 重建块
    ↓
[去块滤波] → 输出帧
    ↓
解码视频
```

### H.264 Profile和Level

**Profile（档次）**定义了编码工具集：

| Profile | 特点 | 应用 |
|---------|------|------|
| Baseline | 基本工具，低复杂度 | 视频会议、移动设备 |
| Main | 支持B帧和CABAC | 数字电视广播 |
| High | 支持8×8变换 | 蓝光、HDTV |
| High 10 | 支持10位色深 | 专业视频 |

**Level（级别）**定义了性能限制：

| Level | 最大分辨率 | 最大帧率 | 应用 |
|-------|-----------|---------|------|
| 3.0 | 720×576 | 30fps | SD视频 |
| 3.1 | 1280×720 | 30fps | 720p HD |
| 4.0 | 1920×1080 | 30fps | 1080p HD |
| 5.1 | 1920×1080 | 60fps | 1080p 60fps |

## H.265/HEVC编码标准

### H.265简介

H.265（也称为HEVC - High Efficiency Video Coding）是H.264的继任者，于2013年发布。

**主要改进**：
- 相比H.264，压缩效率提高约50%
- 更好地支持4K/8K超高清视频
- 改进的并行处理能力
- 更灵活的编码结构

**应用场景**：
- 4K/8K超高清视频
- 流媒体服务（Netflix 4K）
- 新一代广播标准
- VR/AR视频
- 监控系统（节省存储空间）

### H.265关键技术改进

**1. 更大的编码单元**
- H.264：最大宏块16×16
- H.265：编码树单元（CTU）最大64×64
- 更适合高分辨率视频

**2. 更灵活的分割方式**
- 支持非对称分割
- 四叉树递归分割
- 更好地适应图像内容

**3. 改进的帧内预测**
- H.264：9种预测模式
- H.265：35种预测模式
- 预测更准确，残差更小

**4. 改进的运动补偿**
- 支持更大的运动矢量
- 改进的插值滤波器
- 更精确的运动估计

**5. 并行处理支持**
- Tiles（瓦片）：将帧分割为独立区域
- WPP（波前并行处理）：行级并行
- 更好地利用多核处理器

### H.264 vs H.265对比

| 特性 | H.264 | H.265 |
|------|-------|-------|
| 压缩效率 | 基准 | 提高50% |
| 最大块大小 | 16×16 | 64×64 |
| 帧内预测模式 | 9种 | 35种 |
| 变换大小 | 4×4, 8×8 | 4×4到32×32 |
| 并行处理 | 有限 | 良好支持 |
| 编码复杂度 | 中等 | 高 |
| 解码复杂度 | 低 | 中等 |
| 硬件支持 | 广泛 | 逐渐普及 |

**实际效果对比**：
- 相同质量下，H.265文件大小约为H.264的50%
- 相同码率下，H.265视觉质量明显优于H.264
- H.265编码时间约为H.264的2-3倍
- H.265解码复杂度约为H.264的1.5倍

## 编解码性能参数

### 码率与质量关系

不同分辨率的推荐码率（H.264）：

| 分辨率 | 帧率 | 低质量 | 中等质量 | 高质量 |
|--------|------|--------|---------|--------|
| 480p | 30fps | 1 Mbps | 2.5 Mbps | 4 Mbps |
| 720p | 30fps | 2.5 Mbps | 5 Mbps | 8 Mbps |
| 1080p | 30fps | 5 Mbps | 8 Mbps | 12 Mbps |
| 1080p | 60fps | 8 Mbps | 12 Mbps | 20 Mbps |
| 4K | 30fps | 15 Mbps | 25 Mbps | 45 Mbps |

H.265可以在相同质量下使用约50%的码率。

### 编解码性能指标

**编码性能**：
- **编码速度**：帧/秒（fps），实时编码需要≥视频帧率
- **压缩比**：原始大小/压缩后大小，通常50:1到200:1
- **编码延迟**：从输入到输出的时间，实时应用要求<100ms

**解码性能**：
- **解码速度**：必须≥视频帧率才能流畅播放
- **解码延迟**：通常比编码延迟小得多
- **内存占用**：参考帧缓存、解码缓冲区

**质量评估**：
- **PSNR（峰值信噪比）**：客观质量指标，单位dB，越高越好
- **SSIM（结构相似性）**：更符合人眼感知的质量指标
- **主观质量**：人眼观看评分，最终标准

## 硬件加速技术

### 为什么需要硬件加速

视频编解码计算量巨大：
- 1080p@30fps H.264编码：需要约10 GOPS（十亿次操作/秒）
- 纯软件实现对CPU负担很重
- 功耗高，发热大
- 难以满足实时性要求

硬件加速的优势：
- **性能提升**：10-100倍加速
- **低功耗**：专用硬件能效比高
- **释放CPU**：CPU可处理其他任务
- **实时性**：满足实时编解码需求

### 硬件加速方案

**1. GPU加速**
- 利用GPU的并行计算能力
- 适合运动估计、变换等并行任务
- 例如：NVIDIA NVENC/NVDEC、AMD VCE/UVD

**2. 专用编解码芯片**
- 集成在SoC中的硬件编解码器
- 功耗最低，性能最优
- 例如：高通Adreno、联发科、海思

**3. DSP加速**
- 使用数字信号处理器
- 适合嵌入式系统
- 例如：TI C6000系列DSP

**4. FPGA实现**
- 可编程硬件加速
- 灵活性高，可定制
- 适合特殊应用场景

### 常见硬件编解码器

**移动平台**：
- **高通Snapdragon**：集成Adreno GPU，支持H.264/H.265硬编解码
- **联发科Dimensity**：支持4K H.265编解码
- **苹果A系列**：高效的硬件编解码器

**嵌入式平台**：
- **Rockchip RK3588**：支持8K H.265解码
- **NXP i.MX8**：支持多路H.264/H.265
- **Amlogic S905**：支持4K H.265解码

**PC平台**：
- **Intel Quick Sync**：集成在CPU中
- **NVIDIA NVENC/NVDEC**：独立GPU加速
- **AMD VCE/VCN**：AMD GPU加速

## 嵌入式系统中的应用

### 应用场景

**1. 视频监控系统**
- 实时H.264/H.265编码
- 多路视频同时编码
- 网络传输和本地存储
- 典型方案：海思Hi3516、安霸A12

**2. 行车记录仪**
- 高清视频录制
- 循环录像
- 碰撞检测触发录像
- 典型方案：联咏NT96660、安凯AK3918

**3. 无人机/运动相机**
- 4K高清录制
- 实时图传
- 低延迟要求
- 典型方案：Ambarella H22、海思Hi3559

**4. 视频会议终端**
- 实时双向编解码
- 低延迟要求（<200ms）
- 网络自适应码率
- 典型方案：TI DM8168、NXP i.MX8

**5. 智能门铃/可视对讲**
- 低功耗编解码
- 移动端推流
- 云端存储
- 典型方案：海思Hi3518、君正T31

### 系统架构示例

典型的嵌入式视频编码系统架构：

```
[摄像头] → [ISP] → [内存] → [视频编码器] → [网络/存储]
   ↓                  ↑            ↓
[传感器]          [CPU控制]    [码流输出]
```

**关键组件**：
1. **ISP（图像信号处理器）**：处理原始传感器数据
2. **视频编码器**：H.264/H.265硬件编码
3. **内存管理**：DMA传输，减少CPU干预
4. **网络接口**：RTSP/RTMP流媒体传输
5. **存储接口**：SD卡/eMMC本地存储

### 软件框架

**常用开源库**：

1. **FFmpeg**
   - 功能最全面的多媒体框架
   - 支持几乎所有视频格式
   - 可调用硬件加速
   - 命令行工具和库接口

2. **x264/x265**
   - 高质量的H.264/H.265软件编码器
   - 开源免费
   - 性能优秀
   - 广泛应用

3. **OpenMAX IL**
   - 多媒体硬件抽象层
   - 统一的硬件加速接口
   - 嵌入式系统常用

4. **GStreamer**
   - 流媒体框架
   - 插件化架构
   - 支持硬件加速
   - 适合复杂管道处理

### 实现示例：使用FFmpeg进行编解码

**编码示例**（将YUV转换为H.264）：

```c
#include <libavcodec/avcodec.h>
#include <libavutil/opt.h>
#include <libavutil/imgutils.h>

// 初始化编码器
AVCodec *codec = avcodec_find_encoder(AV_CODEC_ID_H264);
AVCodecContext *ctx = avcodec_alloc_context3(codec);

// 设置编码参数
ctx->width = 1920;
ctx->height = 1080;
ctx->time_base = (AVRational){1, 30};  // 30fps
ctx->framerate = (AVRational){30, 1};
ctx->pix_fmt = AV_PIX_FMT_YUV420P;
ctx->bit_rate = 4000000;  // 4Mbps
ctx->gop_size = 30;  // GOP大小
ctx->max_b_frames = 2;  // B帧数量

// 设置H.264特定参数
av_opt_set(ctx->priv_data, "preset", "medium", 0);
av_opt_set(ctx->priv_data, "profile", "high", 0);

// 打开编码器
avcodec_open2(ctx, codec, NULL);

// 编码一帧
AVFrame *frame = av_frame_alloc();
frame->format = ctx->pix_fmt;
frame->width = ctx->width;
frame->height = ctx->height;
av_frame_get_buffer(frame, 0);

// 填充YUV数据到frame...

AVPacket *pkt = av_packet_alloc();
int ret = avcodec_send_frame(ctx, frame);
if (ret >= 0) {
    ret = avcodec_receive_packet(ctx, pkt);
    if (ret >= 0) {
        // pkt包含编码后的H.264数据
        // 可以写入文件或发送到网络
    }
}

// 清理资源
av_packet_free(&pkt);
av_frame_free(&frame);
avcodec_free_context(&ctx);
```

**解码示例**（将H.264解码为YUV）：

```c
// 初始化解码器
AVCodec *codec = avcodec_find_decoder(AV_CODEC_ID_H264);
AVCodecContext *ctx = avcodec_alloc_context3(codec);
avcodec_open2(ctx, codec, NULL);

// 解码
AVPacket *pkt = av_packet_alloc();
AVFrame *frame = av_frame_alloc();

// 填充H.264数据到pkt...

int ret = avcodec_send_packet(ctx, pkt);
if (ret >= 0) {
    ret = avcodec_receive_frame(ctx, frame);
    if (ret >= 0) {
        // frame包含解码后的YUV数据
        // 可以显示或进一步处理
    }
}

// 清理资源
av_frame_free(&frame);
av_packet_free(&pkt);
avcodec_free_context(&ctx);
```

### 性能优化建议

**编码优化**：
1. **选择合适的preset**：
   - ultrafast：最快，质量最低
   - medium：平衡速度和质量
   - veryslow：最慢，质量最高

2. **调整GOP大小**：
   - 较大GOP：压缩率高，但随机访问慢
   - 较小GOP：便于seek，但文件较大
   - 推荐：1-2秒（30-60帧）

3. **使用硬件加速**：
   - 检测并使用可用的硬件编码器
   - 例如：h264_nvenc（NVIDIA）、h264_qsv（Intel）

4. **多线程编码**：
   - 设置threads参数
   - 利用多核CPU

**解码优化**：
1. **使用硬件解码**：
   - 优先使用硬件解码器
   - 降低CPU占用和功耗

2. **缓冲管理**：
   - 合理设置解码缓冲区大小
   - 避免频繁内存分配

3. **零拷贝技术**：
   - 直接使用硬件解码器输出
   - 减少内存拷贝开销

## 实际应用考虑

### 选择H.264还是H.265？

**选择H.264的情况**：
- 需要广泛的设备兼容性
- 实时性要求高（编码延迟敏感）
- 硬件资源有限
- 带宽充足
- 成本敏感（H.265可能有专利费）

**选择H.265的情况**：
- 需要更高的压缩率
- 4K/8K超高清视频
- 带宽受限
- 存储空间有限
- 设备支持H.265硬件加速
- 长期存储（节省空间）

### 编码参数配置建议

**通用配置**：
```
分辨率：根据应用需求（720p/1080p/4K）
帧率：30fps（标准）或60fps（高质量）
码率控制：VBR（质量优先）或CBR（流媒体）
GOP大小：30-60帧（1-2秒）
B帧数量：2-4帧（平衡压缩率和延迟）
Profile：High（最佳压缩）
Level：根据分辨率和帧率选择
```

**低延迟配置**（视频会议、直播）：
```
GOP大小：15-30帧（0.5-1秒）
B帧数量：0（禁用B帧）
编码preset：fast或faster
码率控制：CBR
缓冲区：最小化
```

**高质量配置**（存档、专业视频）：
```
码率：高码率或无损
编码preset：slow或veryslow
B帧数量：4-8帧
GOP大小：60-120帧
Profile：High 10（10位色深）
```

### 常见问题与解决方案

**问题1：编码速度慢**
- 解决：降低preset级别、使用硬件加速、减少分辨率
- 权衡：质量可能下降

**问题2：文件太大**
- 解决：降低码率、增加GOP大小、使用H.265
- 权衡：质量可能下降、兼容性可能降低

**问题3：画面有块效应**
- 解决：提高码率、降低量化参数、启用去块滤波
- 权衡：文件变大、编码变慢

**问题4：延迟太高**
- 解决：减小GOP、禁用B帧、减小缓冲区
- 权衡：压缩率降低

**问题5：硬件加速不工作**
- 解决：检查驱动、确认硬件支持、正确配置FFmpeg
- 备选：使用软件编码

## 未来发展趋势

### 新一代编码标准

**AV1**：
- 开源免费的视频编码标准
- 压缩效率优于H.265约30%
- 无专利费用
- 逐渐获得硬件支持
- 适合互联网视频应用

**VVC/H.266**：
- H.265的继任者
- 压缩效率再提升50%
- 针对4K/8K和360°视频优化
- 2020年发布，硬件支持逐步推出

### 技术发展方向

**1. AI辅助编码**
- 使用深度学习优化编码决策
- 智能码率分配
- 内容感知编码

**2. 云端编码**
- 利用云计算资源
- 弹性扩展
- 降低终端设备要求

**3. 实时编码优化**
- 更低的延迟
- 更好的网络适应性
- 支持WebRTC等实时通信

**4. 超高清视频**
- 8K视频编码
- HDR（高动态范围）
- 高帧率（120fps+）

## 总结

本文深入介绍了视频编解码技术的核心概念和实际应用：

**关键要点**：

1. **视频压缩原理**：
   - 利用空间、时间和视觉冗余
   - 通过预测、变换、量化和熵编码实现压缩
   - 典型压缩比可达50:1到200:1

2. **H.264/AVC标准**：
   - 目前应用最广泛的视频编码标准
   - 良好的压缩效率和兼容性
   - 广泛的硬件支持

3. **H.265/HEVC标准**：
   - 压缩效率比H.264提高约50%
   - 更适合4K/8K超高清视频
   - 编码复杂度更高

4. **硬件加速**：
   - 大幅提升编解码性能
   - 降低功耗和CPU占用
   - 是实时视频应用的关键

5. **实际应用**：
   - 根据场景选择合适的编码标准和参数
   - 平衡质量、性能和兼容性
   - 充分利用硬件加速能力

**技术选择建议**：
- 通用应用：H.264 + 硬件加速
- 高清/4K应用：H.265 + 硬件加速
- 互联网视频：考虑AV1
- 实时通信：H.264 + 低延迟配置
- 专业视频：H.265 High Profile + 高码率

视频编解码技术仍在快速发展，新的标准和技术不断涌现。掌握基础原理和实践经验，能够帮助你在实际项目中做出正确的技术选择。

## 扩展阅读

### 技术标准文档

1. **H.264/AVC标准**
   - ITU-T Recommendation H.264
   - ISO/IEC 14496-10 (MPEG-4 Part 10)
   - [ITU-T H.264官方文档](https://www.itu.int/rec/T-REC-H.264)

2. **H.265/HEVC标准**
   - ITU-T Recommendation H.265
   - ISO/IEC 23008-2 (MPEG-H Part 2)
   - [ITU-T H.265官方文档](https://www.itu.int/rec/T-REC-H.265)

3. **AV1标准**
   - [AV1 Specification](https://aomedia.org/av1-features/)
   - Alliance for Open Media

### 推荐书籍

1. **《视频编码技术详解》**
   - 作者：毕厚杰
   - 系统介绍H.264/H.265技术
   - 适合深入学习

2. **"The H.264 Advanced Video Compression Standard"**
   - 作者：Iain E. Richardson
   - H.264标准权威指南
   - 英文原版

3. **"High Efficiency Video Coding (HEVC)"**
   - 作者：Vivienne Sze等
   - H.265/HEVC详细解析
   - 学术性强

### 开源项目

1. **FFmpeg**
   - [https://ffmpeg.org/](https://ffmpeg.org/)
   - 最全面的多媒体框架
   - 包含编解码、转码、流媒体等功能

2. **x264**
   - [https://www.videolan.org/developers/x264.html](https://www.videolan.org/developers/x264.html)
   - 高质量H.264编码器
   - 开源免费

3. **x265**
   - [https://x265.readthedocs.io/](https://x265.readthedocs.io/)
   - 高质量H.265编码器
   - 开源免费

4. **OpenH264**
   - [https://github.com/cisco/openh264](https://github.com/cisco/openh264)
   - Cisco开源的H.264编解码器
   - 免专利费

### 在线资源

1. **视频编码学习网站**
   - [VideoLAN Wiki](https://wiki.videolan.org/)
   - [Doom9 Forum](https://forum.doom9.org/)
   - 丰富的技术讨论和教程

2. **测试视频序列**
   - [Xiph.org Test Media](https://media.xiph.org/)
   - [Derf's Test Media Collection](https://media.xiph.org/video/derf/)
   - 用于编码测试的标准视频

3. **性能测试工具**
   - [MSU Video Quality Measurement Tool](http://www.compression.ru/video/)
   - [VMAF (Video Multimethod Assessment Fusion)](https://github.com/Netflix/vmaf)
   - 视频质量评估工具

### 相关课程

1. **视频处理进阶**
   - [流媒体处理技术](../intermediate/02-streaming-media.html)
   - [音视频同步技术](../intermediate/03-av-sync.html)
   - [硬件加速与优化](../advanced/01-hardware-acceleration.html)

2. **多媒体基础**
   - [音频采集与播放基础](../beginner/01-audio-basics.html)
   - 图像处理基础

3. **系统集成**
   - 嵌入式Linux多媒体开发
   - RTSP流媒体服务器

### 技术社区

1. **VideoLAN社区**
   - VLC和x264/x265开发者社区
   - 活跃的技术讨论

2. **FFmpeg社区**
   - 邮件列表和IRC频道
   - 丰富的开发资源

3. **GitHub**
   - 大量开源视频项目
   - 学习和贡献代码

## 实践练习

为了巩固所学知识，建议完成以下练习：

### 练习1：基础编解码

**目标**：使用FFmpeg命令行工具进行视频编解码

**任务**：
1. 下载测试视频（如Big Buck Bunny）
2. 使用FFmpeg将视频转换为H.264格式
3. 尝试不同的码率和preset参数
4. 比较输出文件大小和质量
5. 测量编码时间

**参考命令**：
```bash
# H.264编码，中等质量
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 output_h264.mp4

# H.265编码，高质量
ffmpeg -i input.mp4 -c:v libx265 -preset slow -crf 20 output_h265.mp4

# 查看视频信息
ffprobe -v error -show_format -show_streams output_h264.mp4
```

### 练习2：参数调优

**目标**：理解编码参数对质量和性能的影响

**任务**：
1. 固定分辨率，测试不同码率的效果
2. 固定码率，测试不同preset的效果
3. 测试不同GOP大小的影响
4. 比较启用/禁用B帧的差异
5. 记录并分析结果

### 练习3：硬件加速

**目标**：使用硬件加速进行编解码

**任务**：
1. 检测系统可用的硬件编码器
2. 使用硬件编码器进行编码
3. 比较软件编码和硬件编码的性能
4. 测量CPU占用率和编码速度
5. 评估质量差异

**参考命令**：
```bash
# 列出可用的硬件编码器
ffmpeg -encoders | grep h264

# NVIDIA硬件编码
ffmpeg -i input.mp4 -c:v h264_nvenc -preset fast output_nvenc.mp4

# Intel Quick Sync编码
ffmpeg -i input.mp4 -c:v h264_qsv -preset fast output_qsv.mp4
```

### 练习4：编程实现

**目标**：使用FFmpeg库编写简单的编解码程序

**任务**：
1. 编写程序读取YUV文件并编码为H.264
2. 编写程序解码H.264文件为YUV
3. 添加错误处理和日志输出
4. 测试不同参数配置
5. 优化性能

### 练习5：实际应用

**目标**：实现一个简单的视频处理应用

**任务选择**：
- 视频转码工具（支持多种格式）
- 视频监控录像系统
- 简单的视频播放器
- 视频流推送工具
- 视频质量分析工具

## 常见问题FAQ

**Q1：H.264和H.265哪个更好？**

A：没有绝对的"更好"，取决于应用场景：
- H.265压缩效率更高，但编码复杂度更大
- H.264兼容性更好，硬件支持更广泛
- 对于4K视频，H.265优势明显
- 对于实时应用，H.264可能更合适

**Q2：为什么硬件编码质量不如软件编码？**

A：硬件编码为了追求速度，通常会：
- 简化编码算法
- 减少编码决策的复杂度
- 使用固定的编码策略
- 但差距在不断缩小，新一代硬件编码器质量已经很好

**Q3：如何选择合适的码率？**

A：考虑以下因素：
- 分辨率和帧率
- 内容复杂度（运动剧烈的内容需要更高码率）
- 传输带宽限制
- 存储空间限制
- 可以参考本文的推荐码率表，然后根据实际效果调整

**Q4：GOP大小如何选择？**

A：权衡考虑：
- 较大GOP（2-4秒）：压缩率高，但seek慢
- 较小GOP（0.5-1秒）：便于随机访问，但文件较大
- 实时应用：建议0.5-1秒
- 点播视频：可以使用2-4秒

**Q5：B帧是否应该使用？**

A：取决于应用：
- 优点：提高压缩率10-20%
- 缺点：增加编码复杂度和延迟
- 实时应用（直播、会议）：建议禁用
- 点播视频：建议启用

**Q6：如何降低编码延迟？**

A：采取以下措施：
- 使用硬件编码
- 减小GOP大小
- 禁用B帧
- 使用faster preset
- 减小编码缓冲区
- 使用slice级并行

**Q7：视频编码需要多少CPU/GPU资源？**

A：大致参考：
- 1080p@30fps H.264软件编码：需要中高端CPU（如i5/i7）
- 1080p@30fps H.264硬件编码：几乎不占用CPU
- 4K@30fps H.265软件编码：需要高端CPU或GPU
- 多路编码：建议使用硬件加速

---

**文章更新日志**：
- 2024-01-15：初始版本发布
- 内容涵盖H.264/H.265基础、硬件加速、实际应用

**作者信息**：
- 嵌入式知识平台内容团队
- 如有问题或建议，欢迎反馈

**版权声明**：
本文采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。
