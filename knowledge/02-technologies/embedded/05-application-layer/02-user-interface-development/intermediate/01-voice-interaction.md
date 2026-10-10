---
title: "嵌入式语音交互技术应用实践"
description: "深入学习嵌入式系统中的语音交互技术，包括语音识别、语音合成、唤醒词检测和命令识别，通过实践项目掌握从硬件选型到应用开发的完整语音交互实现"
slug: "voice-interaction-implementation"

# 分类信息
domain: "应用层"
module: "用户界面开发"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 语音交互
  - 语音识别
  - 语音合成
  - 智能语音
  - ASR
  - TTS
  - 唤醒词
prerequisites:
  - "gui-frameworks-selection-guide"
  - "touch-interaction-design-implementation"
related_contents: []

# 学习信息
estimated_time: 85
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
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 嵌入式语音识别
  - 语音交互设计
  - 语音合成技术
  - 唤醒词检测
  - 智能语音助手
  - ASR技术
  - TTS引擎
cover_image: ""
---

# 嵌入式语音交互技术应用实践

## 学习目标

完成本教程后，你将能够：

- [ ] 理解语音交互的基本原理和技术架构
- [ ] 掌握语音识别(ASR)和语音合成(TTS)的实现方法
- [ ] 学会设计和实现唤醒词检测功能
- [ ] 实现完整的语音命令识别系统
- [ ] 优化语音交互的用户体验和识别准确率
- [ ] 处理噪声环境下的语音信号


## 前置要求

在开始本教程之前,你需要：

**知识要求**：
- 了解C/C++编程基础
- 熟悉基本的数字信号处理概念
- 理解音频采样和编码原理
- 掌握基本的嵌入式开发知识

**技能要求**：
- 能够使用嵌入式开发环境
- 会配置和使用I2S/I2C音频接口
- 了解基本的调试方法
- 熟悉网络通信基础(HTTP/MQTT)

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | 带音频接口的开发板 | ESP32-S3/STM32F7 |
| 麦克风模块 | 1 | 数字或模拟麦克风 | INMP441/MAX9814 |
| 扬声器/功放 | 1 | 音频输出 | MAX98357A |
| SD卡 | 1 | 存储音频数据 | 8GB+ |
| 调试器 | 1 | 程序下载和调试 | - |

**硬件选型建议**：
- **麦克风类型**：数字麦克风(I2S)优于模拟麦克风(ADC)
- **处理器**：建议使用带DSP或AI加速的芯片
- **内存**：至少512KB RAM用于音频缓冲
- **存储**：需要外部Flash或SD卡存储模型

### 软件准备

- **开发环境**：ESP-IDF / STM32CubeIDE
- **语音识别库**：PocketSphinx / Sherpa-ONNX
- **语音合成库**：eSpeak / Flite
- **音频处理库**：CMSIS-DSP / ESP-DSP
- **调试工具**：Audacity(音频分析)

### 环境配置

1. 安装开发环境和工具链
2. 配置音频接口驱动
3. 准备语音识别模型文件
4. 测试音频输入输出


## 语音交互技术基础

### 语音交互系统架构

语音交互系统通常包含以下核心模块：

```mermaid
graph LR
    A[麦克风] --> B[音频采集]
    B --> C[预处理]
    C --> D[唤醒词检测]
    D --> E[语音识别ASR]
    E --> F[意图理解NLU]
    F --> G[业务逻辑]
    G --> H[语音合成TTS]
    H --> I[音频播放]
    I --> J[扬声器]
```

**主要组件说明**：

1. **音频采集**：从麦克风获取原始音频信号
2. **预处理**：降噪、回声消除、增益控制
3. **唤醒词检测**：识别特定唤醒词(如"你好小智")
4. **语音识别(ASR)**：将语音转换为文本
5. **意图理解(NLU)**：理解用户意图和提取参数
6. **业务逻辑**：执行具体功能
7. **语音合成(TTS)**：将文本转换为语音
8. **音频播放**：通过扬声器输出

### 关键技术概念

#### 语音识别(ASR)

**Automatic Speech Recognition**，将语音信号转换为文本。

**主要方法**：
- **传统方法**：基于HMM-GMM的统计模型
- **深度学习**：基于DNN/RNN/Transformer的端到端模型
- **嵌入式方案**：轻量级模型(如Whisper Tiny、Vosk)

**识别流程**：
```
音频信号 → 特征提取(MFCC) → 声学模型 → 语言模型 → 文本输出
```

#### 语音合成(TTS)

**Text-to-Speech**，将文本转换为自然的语音。

**主要方法**：
- **拼接合成**：预录音频片段拼接
- **参数合成**：基于声码器的合成
- **神经网络**：基于Tacotron/FastSpeech的端到端合成

**嵌入式TTS方案**：
- **eSpeak**：开源、轻量、支持多语言
- **Flite**：CMU开发的轻量级TTS
- **云端TTS**：调用云服务API

#### 唤醒词检测

**Wake Word Detection**，持续监听并识别特定唤醒词。

**技术要点**：
- **低功耗**：需要持续运行，功耗要低
- **低延迟**：响应时间要快(< 500ms)
- **高准确率**：减少误唤醒和漏唤醒
- **小模型**：适合嵌入式设备运行

**常用方案**：
- **Porcupine**：Picovoice的唤醒词引擎
- **Snowboy**：开源唤醒词检测(已停止维护)
- **自定义模型**：基于CNN/RNN的轻量级模型


## 步骤1：音频采集与预处理

### 1.1 配置I2S音频接口

以ESP32为例，配置I2S接口连接数字麦克风：

```c
// audio_config.h
#ifndef AUDIO_CONFIG_H
#define AUDIO_CONFIG_H

#include "driver/i2s.h"

// I2S配置参数
#define I2S_NUM         I2S_NUM_0
#define SAMPLE_RATE     16000
#define BITS_PER_SAMPLE I2S_BITS_PER_SAMPLE_16BIT
#define CHANNEL_NUM     1

// I2S引脚定义
#define I2S_BCK_PIN     26
#define I2S_WS_PIN      25
#define I2S_DATA_PIN    33

// 音频缓冲区
#define BUFFER_SIZE     1024
#define DMA_BUF_COUNT   4
#define DMA_BUF_LEN     512

#endif
```

### 1.2 初始化I2S驱动

```c
// audio_driver.c
#include "audio_config.h"
#include "esp_log.h"

static const char *TAG = "AUDIO";

esp_err_t audio_init(void)
{
    // I2S配置结构
    i2s_config_t i2s_config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_RX,
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = BITS_PER_SAMPLE,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = DMA_BUF_COUNT,
        .dma_buf_len = DMA_BUF_LEN,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    // 引脚配置
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DATA_PIN
    };
    
    // 安装I2S驱动
    esp_err_t ret = i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to install I2S driver");
        return ret;
    }
    
    // 设置引脚
    ret = i2s_set_pin(I2S_NUM, &pin_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set I2S pins");
        return ret;
    }
    
    ESP_LOGI(TAG, "I2S initialized successfully");
    return ESP_OK;
}

// 读取音频数据
int audio_read(int16_t *buffer, size_t samples)
{
    size_t bytes_read = 0;
    size_t bytes_to_read = samples * sizeof(int16_t);
    
    esp_err_t ret = i2s_read(I2S_NUM, buffer, bytes_to_read, 
                             &bytes_read, portMAX_DELAY);
    
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2S read failed");
        return -1;
    }
    
    return bytes_read / sizeof(int16_t);
}
```

**代码说明**：
- 第9-21行：配置I2S为主模式接收，16kHz采样率，16位深度
- 第24-29行：配置I2S引脚连接
- 第32-38行：安装I2S驱动并分配DMA缓冲区
- 第48-59行：从I2S读取音频数据到缓冲区


### 1.3 音频预处理

实现基本的音频预处理功能：

```c
// audio_preprocess.c
#include <math.h>
#include <string.h>

// 音频预处理结构
typedef struct {
    float dc_offset;
    float prev_sample;
    int16_t *buffer;
    size_t buffer_size;
} audio_preprocess_t;

static audio_preprocess_t preprocess = {0};

// 初始化预处理
void audio_preprocess_init(size_t buffer_size)
{
    preprocess.dc_offset = 0.0f;
    preprocess.prev_sample = 0.0f;
    preprocess.buffer_size = buffer_size;
    preprocess.buffer = malloc(buffer_size * sizeof(int16_t));
}

// 去除直流分量
void remove_dc_offset(int16_t *samples, size_t count)
{
    float alpha = 0.95f;  // 高通滤波器系数
    
    for (size_t i = 0; i < count; i++) {
        float input = (float)samples[i];
        float output = input - preprocess.dc_offset;
        preprocess.dc_offset = preprocess.dc_offset * alpha + input * (1 - alpha);
        samples[i] = (int16_t)output;
    }
}

// 自动增益控制(AGC)
void apply_agc(int16_t *samples, size_t count, float target_level)
{
    // 计算当前音量
    float sum = 0.0f;
    for (size_t i = 0; i < count; i++) {
        sum += abs(samples[i]);
    }
    float avg_level = sum / count;
    
    // 计算增益
    float gain = 1.0f;
    if (avg_level > 100) {  // 避免除零
        gain = target_level / avg_level;
        // 限制增益范围
        if (gain > 4.0f) gain = 4.0f;
        if (gain < 0.25f) gain = 0.25f;
    }
    
    // 应用增益
    for (size_t i = 0; i < count; i++) {
        int32_t sample = (int32_t)(samples[i] * gain);
        // 防止溢出
        if (sample > 32767) sample = 32767;
        if (sample < -32768) sample = -32768;
        samples[i] = (int16_t)sample;
    }
}

// 简单降噪(门限法)
void apply_noise_gate(int16_t *samples, size_t count, int16_t threshold)
{
    for (size_t i = 0; i < count; i++) {
        if (abs(samples[i]) < threshold) {
            samples[i] = 0;
        }
    }
}

// 完整的预处理流程
void audio_preprocess(int16_t *samples, size_t count)
{
    // 1. 去除直流分量
    remove_dc_offset(samples, count);
    
    // 2. 降噪
    apply_noise_gate(samples, count, 200);
    
    // 3. 自动增益控制
    apply_agc(samples, count, 8000.0f);
}
```

**代码说明**：
- 第24-34行：使用一阶高通滤波器去除直流分量
- 第37-60行：实现自动增益控制，保持音量稳定
- 第63-69行：简单的噪声门限，过滤低于阈值的信号
- 第72-82行：组合所有预处理步骤

**预期结果**：
- 音频信号无直流偏移
- 音量保持在合适范围
- 背景噪声得到抑制


## 步骤2：唤醒词检测实现

### 2.1 集成Porcupine唤醒词引擎

Porcupine是Picovoice提供的轻量级唤醒词检测引擎。

```c
// wake_word.h
#ifndef WAKE_WORD_H
#define WAKE_WORD_H

#include <stdbool.h>
#include <stdint.h>

// 唤醒词回调函数类型
typedef void (*wake_word_callback_t)(void);

// 初始化唤醒词检测
bool wake_word_init(const char *model_path, wake_word_callback_t callback);

// 处理音频帧
bool wake_word_process(const int16_t *pcm, int num_samples);

// 清理资源
void wake_word_deinit(void);

#endif
```

### 2.2 实现唤醒词检测

```c
// wake_word.c
#include "wake_word.h"
#include "pv_porcupine.h"
#include "esp_log.h"

static const char *TAG = "WAKE_WORD";
static pv_porcupine_t *porcupine = NULL;
static wake_word_callback_t callback = NULL;

bool wake_word_init(const char *model_path, wake_word_callback_t cb)
{
    callback = cb;
    
    // 初始化Porcupine
    pv_status_t status = pv_porcupine_init(
        "YOUR_ACCESS_KEY",      // 访问密钥
        model_path,             // 模型文件路径
        1,                      // 关键词数量
        &(const char*[]){"你好小智"},  // 关键词
        &(const float[]){0.5f}, // 灵敏度(0-1)
        &porcupine
    );
    
    if (status != PV_STATUS_SUCCESS) {
        ESP_LOGE(TAG, "Failed to initialize Porcupine: %d", status);
        return false;
    }
    
    ESP_LOGI(TAG, "Porcupine initialized, frame length: %d", 
             pv_porcupine_frame_length());
    return true;
}

bool wake_word_process(const int16_t *pcm, int num_samples)
{
    if (!porcupine) return false;
    
    int32_t keyword_index = -1;
    pv_status_t status = pv_porcupine_process(porcupine, pcm, &keyword_index);
    
    if (status != PV_STATUS_SUCCESS) {
        ESP_LOGE(TAG, "Porcupine process failed: %d", status);
        return false;
    }
    
    // 检测到唤醒词
    if (keyword_index >= 0) {
        ESP_LOGI(TAG, "Wake word detected!");
        if (callback) {
            callback();
        }
        return true;
    }
    
    return false;
}

void wake_word_deinit(void)
{
    if (porcupine) {
        pv_porcupine_delete(porcupine);
        porcupine = NULL;
    }
}
```

### 2.3 创建唤醒词检测任务

```c
// wake_word_task.c
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "audio_driver.h"
#include "wake_word.h"

#define FRAME_LENGTH 512  // Porcupine帧长度

static bool is_listening = false;

// 唤醒词检测到的回调
void on_wake_word_detected(void)
{
    ESP_LOGI("WAKE", "唤醒词检测到，开始语音识别");
    is_listening = true;
    
    // 播放提示音
    play_beep();
    
    // 启动语音识别
    start_speech_recognition();
}

// 唤醒词检测任务
void wake_word_task(void *arg)
{
    int16_t audio_buffer[FRAME_LENGTH];
    
    // 初始化唤醒词检测
    if (!wake_word_init("/sdcard/porcupine_model.pv", on_wake_word_detected)) {
        ESP_LOGE("WAKE", "Failed to initialize wake word detection");
        vTaskDelete(NULL);
        return;
    }
    
    ESP_LOGI("WAKE", "Wake word detection started");
    
    while (1) {
        // 读取音频数据
        int samples_read = audio_read(audio_buffer, FRAME_LENGTH);
        
        if (samples_read == FRAME_LENGTH) {
            // 预处理音频
            audio_preprocess(audio_buffer, FRAME_LENGTH);
            
            // 检测唤醒词
            wake_word_process(audio_buffer, FRAME_LENGTH);
        }
        
        // 短暂延时，避免占用过多CPU
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// 启动唤醒词检测
void start_wake_word_detection(void)
{
    xTaskCreate(wake_word_task, "wake_word", 4096, NULL, 5, NULL);
}
```

**代码说明**：
- 第14-22行：唤醒词检测到后的回调处理
- 第25-50行：持续读取音频并检测唤醒词
- 第38-44行：读取音频帧，预处理后送入检测引擎

**预期结果**：
- 系统持续监听唤醒词
- 检测到唤醒词后触发回调
- CPU占用率低于10%


## 步骤3：语音识别实现

### 3.1 集成Vosk语音识别引擎

Vosk是一个开源的离线语音识别库，支持多种语言。

```c
// speech_recognition.h
#ifndef SPEECH_RECOGNITION_H
#define SPEECH_RECOGNITION_H

#include <stdbool.h>
#include <stdint.h>

// 识别结果回调
typedef void (*recognition_callback_t)(const char *text);

// 初始化语音识别
bool speech_recognition_init(const char *model_path);

// 开始识别会话
void speech_recognition_start(void);

// 处理音频数据
bool speech_recognition_process(const int16_t *pcm, int num_samples);

// 结束识别会话
const char* speech_recognition_finish(void);

// 清理资源
void speech_recognition_deinit(void);

#endif
```

### 3.2 实现语音识别

```c
// speech_recognition.c
#include "speech_recognition.h"
#include "vosk_api.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "ASR";
static VoskModel *model = NULL;
static VoskRecognizer *recognizer = NULL;
static recognition_callback_t callback = NULL;

bool speech_recognition_init(const char *model_path)
{
    // 加载模型
    model = vosk_model_new(model_path);
    if (!model) {
        ESP_LOGE(TAG, "Failed to load model from %s", model_path);
        return false;
    }
    
    // 创建识别器
    recognizer = vosk_recognizer_new(model, 16000.0);
    if (!recognizer) {
        ESP_LOGE(TAG, "Failed to create recognizer");
        vosk_model_free(model);
        return false;
    }
    
    ESP_LOGI(TAG, "Speech recognition initialized");
    return true;
}

void speech_recognition_start(void)
{
    if (recognizer) {
        vosk_recognizer_reset(recognizer);
        ESP_LOGI(TAG, "Recognition session started");
    }
}

bool speech_recognition_process(const int16_t *pcm, int num_samples)
{
    if (!recognizer) return false;
    
    // 送入音频数据
    int result = vosk_recognizer_accept_waveform(
        recognizer, 
        (const char*)pcm, 
        num_samples * sizeof(int16_t)
    );
    
    if (result) {
        // 获取识别结果
        const char *json_result = vosk_recognizer_result(recognizer);
        ESP_LOGI(TAG, "Recognition result: %s", json_result);
        
        // 解析JSON获取文本
        // 这里简化处理，实际应使用JSON解析库
        return true;
    }
    
    return false;
}

const char* speech_recognition_finish(void)
{
    if (!recognizer) return NULL;
    
    // 获取最终结果
    const char *final_result = vosk_recognizer_final_result(recognizer);
    ESP_LOGI(TAG, "Final result: %s", final_result);
    
    return final_result;
}

void speech_recognition_deinit(void)
{
    if (recognizer) {
        vosk_recognizer_free(recognizer);
        recognizer = NULL;
    }
    if (model) {
        vosk_model_free(model);
        model = NULL;
    }
}
```

### 3.3 实现语音命令识别

```c
// voice_command.c
#include <string.h>
#include "cJSON.h"

// 命令定义
typedef struct {
    const char *pattern;
    void (*handler)(const char *params);
} voice_command_t;

// 命令处理函数
void cmd_turn_on_light(const char *params)
{
    ESP_LOGI("CMD", "打开灯光: %s", params ? params : "全部");
    // 执行开灯操作
}

void cmd_turn_off_light(const char *params)
{
    ESP_LOGI("CMD", "关闭灯光: %s", params ? params : "全部");
    // 执行关灯操作
}

void cmd_set_temperature(const char *params)
{
    if (params) {
        int temp = atoi(params);
        ESP_LOGI("CMD", "设置温度: %d度", temp);
        // 执行温度设置
    }
}

void cmd_query_weather(const char *params)
{
    ESP_LOGI("CMD", "查询天气");
    // 查询天气信息
}

// 命令表
static const voice_command_t commands[] = {
    {"打开灯", cmd_turn_on_light},
    {"开灯", cmd_turn_on_light},
    {"关闭灯", cmd_turn_off_light},
    {"关灯", cmd_turn_off_light},
    {"设置温度", cmd_set_temperature},
    {"调节温度", cmd_set_temperature},
    {"查询天气", cmd_query_weather},
    {"天气怎么样", cmd_query_weather},
    {NULL, NULL}
};

// 解析识别结果
void parse_recognition_result(const char *json_result)
{
    cJSON *root = cJSON_Parse(json_result);
    if (!root) {
        ESP_LOGE("CMD", "Failed to parse JSON");
        return;
    }
    
    // 获取识别文本
    cJSON *text_item = cJSON_GetObjectItem(root, "text");
    if (!text_item || !cJSON_IsString(text_item)) {
        cJSON_Delete(root);
        return;
    }
    
    const char *text = text_item->valuestring;
    ESP_LOGI("CMD", "Recognized text: %s", text);
    
    // 匹配命令
    for (int i = 0; commands[i].pattern != NULL; i++) {
        if (strstr(text, commands[i].pattern) != NULL) {
            // 提取参数（简化处理）
            const char *params = text + strlen(commands[i].pattern);
            while (*params == ' ') params++;  // 跳过空格
            
            // 执行命令
            commands[i].handler(params[0] ? params : NULL);
            break;
        }
    }
    
    cJSON_Delete(root);
}
```

**代码说明**：
- 第12-35行：定义各种语音命令的处理函数
- 第38-48行：命令表，将语音模式映射到处理函数
- 第51-82行：解析JSON格式的识别结果并匹配命令


## 步骤4：语音合成实现

### 4.1 集成eSpeak语音合成

eSpeak是一个开源的轻量级TTS引擎。

```c
// text_to_speech.h
#ifndef TEXT_TO_SPEECH_H
#define TEXT_TO_SPEECH_H

#include <stdbool.h>

// 初始化TTS
bool tts_init(void);

// 合成语音
bool tts_speak(const char *text);

// 设置语速(80-450)
void tts_set_speed(int speed);

// 设置音量(0-200)
void tts_set_volume(int volume);

// 清理资源
void tts_deinit(void);

#endif
```

### 4.2 实现TTS功能

```c
// text_to_speech.c
#include "text_to_speech.h"
#include "espeak-ng/speak_lib.h"
#include "audio_driver.h"
#include "esp_log.h"

static const char *TAG = "TTS";
static int current_speed = 175;
static int current_volume = 100;

// 音频输出回调
static int audio_output_callback(short *wav, int numsamples, espeak_EVENT *events)
{
    if (numsamples > 0) {
        // 将合成的音频数据输出到扬声器
        audio_write((int16_t*)wav, numsamples);
    }
    return 0;
}

bool tts_init(void)
{
    // 初始化eSpeak
    int sample_rate = espeak_Initialize(
        AUDIO_OUTPUT_SYNCHRONOUS,
        0,  // 缓冲区长度(0=默认)
        NULL,  // 数据路径(NULL=默认)
        0   // 选项
    );
    
    if (sample_rate == -1) {
        ESP_LOGE(TAG, "Failed to initialize eSpeak");
        return false;
    }
    
    ESP_LOGI(TAG, "eSpeak initialized, sample rate: %d", sample_rate);
    
    // 设置音频输出回调
    espeak_SetSynthCallback(audio_output_callback);
    
    // 设置语言为中文
    espeak_SetVoiceByName("zh");
    
    // 设置默认参数
    espeak_SetParameter(espeakRATE, current_speed, 0);
    espeak_SetParameter(espeakVOLUME, current_volume, 0);
    
    return true;
}

bool tts_speak(const char *text)
{
    if (!text || strlen(text) == 0) {
        return false;
    }
    
    ESP_LOGI(TAG, "Speaking: %s", text);
    
    // 合成语音
    espeak_ERROR err = espeak_Synth(
        text,
        strlen(text) + 1,
        0,  // 位置
        POS_CHARACTER,
        0,  // 结束位置(0=全部)
        espeakCHARS_UTF8,
        NULL,  // 用户数据
        NULL   // 文本标识
    );
    
    if (err != EE_OK) {
        ESP_LOGE(TAG, "eSpeak synthesis failed: %d", err);
        return false;
    }
    
    // 等待合成完成
    espeak_Synchronize();
    
    return true;
}

void tts_set_speed(int speed)
{
    if (speed < 80) speed = 80;
    if (speed > 450) speed = 450;
    current_speed = speed;
    espeak_SetParameter(espeakRATE, speed, 0);
}

void tts_set_volume(int volume)
{
    if (volume < 0) volume = 0;
    if (volume > 200) volume = 200;
    current_volume = volume;
    espeak_SetParameter(espeakVOLUME, volume, 0);
}

void tts_deinit(void)
{
    espeak_Terminate();
}
```

### 4.3 实现语音反馈

```c
// voice_feedback.c
#include "text_to_speech.h"

// 预定义的反馈语音
typedef struct {
    const char *key;
    const char *text;
} feedback_message_t;

static const feedback_message_t feedback_messages[] = {
    {"wake", "我在"},
    {"listening", "请说"},
    {"processing", "正在处理"},
    {"done", "好的"},
    {"error", "抱歉，我没听清"},
    {"timeout", "没有听到您的指令"},
    {NULL, NULL}
};

// 播放反馈语音
void play_feedback(const char *key)
{
    for (int i = 0; feedback_messages[i].key != NULL; i++) {
        if (strcmp(feedback_messages[i].key, key) == 0) {
            tts_speak(feedback_messages[i].text);
            return;
        }
    }
}

// 播放自定义反馈
void play_custom_feedback(const char *format, ...)
{
    char buffer[256];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    tts_speak(buffer);
}

// 使用示例
void example_feedback(void)
{
    // 唤醒反馈
    play_feedback("wake");
    
    // 自定义反馈
    play_custom_feedback("当前温度是%d度", 25);
    
    // 错误反馈
    play_feedback("error");
}
```

**代码说明**：
- 第12-18行：音频输出回调，将合成的音频送到扬声器
- 第51-73行：调用eSpeak合成语音并等待完成
- 第108-120行：预定义常用反馈语音，提高响应速度


## 步骤5：完整交互流程实现

### 5.1 状态机设计

设计语音交互的状态机：

```c
// voice_interaction.h
typedef enum {
    STATE_IDLE,          // 空闲状态
    STATE_LISTENING,     // 监听唤醒词
    STATE_RECOGNIZING,   // 语音识别中
    STATE_PROCESSING,    // 处理命令
    STATE_RESPONDING,    // 语音反馈
    STATE_ERROR          // 错误状态
} voice_state_t;

typedef struct {
    voice_state_t current_state;
    uint32_t state_start_time;
    uint32_t timeout_ms;
    bool is_active;
} voice_interaction_t;
```

### 5.2 实现状态机

```c
// voice_interaction.c
#include "voice_interaction.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "VOICE_INT";
static voice_interaction_t interaction = {
    .current_state = STATE_IDLE,
    .timeout_ms = 5000,
    .is_active = false
};

// 状态转换
void set_state(voice_state_t new_state)
{
    ESP_LOGI(TAG, "State: %d -> %d", interaction.current_state, new_state);
    interaction.current_state = new_state;
    interaction.state_start_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
}

// 检查超时
bool is_timeout(void)
{
    uint32_t current_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
    return (current_time - interaction.state_start_time) > interaction.timeout_ms;
}

// 唤醒词检测回调
void on_wake_word(void)
{
    if (interaction.current_state == STATE_LISTENING) {
        set_state(STATE_RECOGNIZING);
        play_feedback("wake");
        speech_recognition_start();
    }
}

// 识别完成回调
void on_recognition_complete(const char *text)
{
    if (interaction.current_state == STATE_RECOGNIZING) {
        set_state(STATE_PROCESSING);
        
        // 解析并执行命令
        parse_recognition_result(text);
        
        set_state(STATE_RESPONDING);
        play_feedback("done");
        
        // 返回监听状态
        vTaskDelay(pdMS_TO_TICKS(1000));
        set_state(STATE_LISTENING);
    }
}

// 主交互循环
void voice_interaction_task(void *arg)
{
    int16_t audio_buffer[512];
    
    set_state(STATE_LISTENING);
    
    while (1) {
        switch (interaction.current_state) {
            case STATE_LISTENING:
                // 持续监听唤醒词
                if (audio_read(audio_buffer, 512) > 0) {
                    audio_preprocess(audio_buffer, 512);
                    wake_word_process(audio_buffer, 512);
                }
                break;
                
            case STATE_RECOGNIZING:
                // 进行语音识别
                if (audio_read(audio_buffer, 512) > 0) {
                    audio_preprocess(audio_buffer, 512);
                    
                    if (speech_recognition_process(audio_buffer, 512)) {
                        // 识别到完整语句
                        const char *result = speech_recognition_finish();
                        on_recognition_complete(result);
                    }
                }
                
                // 检查超时
                if (is_timeout()) {
                    ESP_LOGW(TAG, "Recognition timeout");
                    play_feedback("timeout");
                    set_state(STATE_LISTENING);
                }
                break;
                
            case STATE_PROCESSING:
            case STATE_RESPONDING:
                // 这些状态由回调处理
                vTaskDelay(pdMS_TO_TICKS(100));
                break;
                
            case STATE_ERROR:
                ESP_LOGE(TAG, "Error state, resetting");
                play_feedback("error");
                vTaskDelay(pdMS_TO_TICKS(1000));
                set_state(STATE_LISTENING);
                break;
                
            default:
                set_state(STATE_LISTENING);
                break;
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// 启动语音交互
void start_voice_interaction(void)
{
    // 初始化各个模块
    audio_init();
    wake_word_init("/sdcard/wake_model.pv", on_wake_word);
    speech_recognition_init("/sdcard/vosk_model");
    tts_init();
    
    // 创建交互任务
    xTaskCreate(voice_interaction_task, "voice_int", 8192, NULL, 5, NULL);
    
    ESP_LOGI(TAG, "Voice interaction started");
}
```

**代码说明**：
- 第15-20行：状态转换函数，记录状态和时间
- 第29-35行：唤醒词检测到后的处理
- 第38-51行：识别完成后的命令处理
- 第54-110行：主状态机循环，根据状态执行不同操作


## 步骤6：交互体验优化

### 6.1 端点检测(VAD)

实现语音活动检测，自动判断语音开始和结束：

```c
// vad.c - Voice Activity Detection
#include <math.h>

typedef struct {
    float energy_threshold;
    int silence_frames;
    int speech_frames;
    bool is_speech;
    int min_speech_frames;
    int min_silence_frames;
} vad_t;

static vad_t vad = {
    .energy_threshold = 500.0f,
    .min_speech_frames = 5,
    .min_silence_frames = 15,
    .is_speech = false
};

// 计算音频能量
float calculate_energy(const int16_t *samples, int count)
{
    float sum = 0.0f;
    for (int i = 0; i < count; i++) {
        sum += (float)samples[i] * samples[i];
    }
    return sqrt(sum / count);
}

// VAD处理
bool vad_process(const int16_t *samples, int count)
{
    float energy = calculate_energy(samples, count);
    
    if (energy > vad.energy_threshold) {
        // 检测到语音
        vad.speech_frames++;
        vad.silence_frames = 0;
        
        if (vad.speech_frames >= vad.min_speech_frames) {
            vad.is_speech = true;
        }
    } else {
        // 静音
        vad.silence_frames++;
        vad.speech_frames = 0;
        
        if (vad.silence_frames >= vad.min_silence_frames) {
            if (vad.is_speech) {
                // 语音结束
                vad.is_speech = false;
                return true;  // 返回true表示检测到语音结束
            }
        }
    }
    
    return false;
}

// 重置VAD状态
void vad_reset(void)
{
    vad.speech_frames = 0;
    vad.silence_frames = 0;
    vad.is_speech = false;
}

// 判断当前是否有语音
bool vad_is_speech(void)
{
    return vad.is_speech;
}
```

### 6.2 回声消除

实现简单的回声消除，避免扬声器输出影响麦克风：

```c
// aec.c - Acoustic Echo Cancellation
#define AEC_BUFFER_SIZE 1024

typedef struct {
    int16_t reference_buffer[AEC_BUFFER_SIZE];
    int write_pos;
    int read_pos;
    float attenuation;
} aec_t;

static aec_t aec = {
    .write_pos = 0,
    .read_pos = 0,
    .attenuation = 0.5f
};

// 添加参考信号(扬声器输出)
void aec_add_reference(const int16_t *samples, int count)
{
    for (int i = 0; i < count; i++) {
        aec.reference_buffer[aec.write_pos] = samples[i];
        aec.write_pos = (aec.write_pos + 1) % AEC_BUFFER_SIZE;
    }
}

// 处理麦克风信号
void aec_process(int16_t *samples, int count)
{
    for (int i = 0; i < count; i++) {
        // 简单的回声抵消：减去衰减的参考信号
        int16_t reference = aec.reference_buffer[aec.read_pos];
        int32_t output = samples[i] - (int32_t)(reference * aec.attenuation);
        
        // 限幅
        if (output > 32767) output = 32767;
        if (output < -32768) output = -32768;
        
        samples[i] = (int16_t)output;
        aec.read_pos = (aec.read_pos + 1) % AEC_BUFFER_SIZE;
    }
}
```

### 6.3 多轮对话支持

实现上下文管理，支持多轮对话：

```c
// dialog_context.c
#include <string.h>

#define MAX_CONTEXT_ITEMS 10

typedef struct {
    char key[32];
    char value[128];
} context_item_t;

typedef struct {
    context_item_t items[MAX_CONTEXT_ITEMS];
    int count;
    uint32_t last_update_time;
    uint32_t timeout_ms;
} dialog_context_t;

static dialog_context_t context = {
    .count = 0,
    .timeout_ms = 60000  // 60秒超时
};

// 设置上下文
void context_set(const char *key, const char *value)
{
    // 查找是否已存在
    for (int i = 0; i < context.count; i++) {
        if (strcmp(context.items[i].key, key) == 0) {
            strncpy(context.items[i].value, value, sizeof(context.items[i].value) - 1);
            context.last_update_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
            return;
        }
    }
    
    // 添加新项
    if (context.count < MAX_CONTEXT_ITEMS) {
        strncpy(context.items[context.count].key, key, sizeof(context.items[0].key) - 1);
        strncpy(context.items[context.count].value, value, sizeof(context.items[0].value) - 1);
        context.count++;
        context.last_update_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
    }
}

// 获取上下文
const char* context_get(const char *key)
{
    // 检查超时
    uint32_t current_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
    if (current_time - context.last_update_time > context.timeout_ms) {
        context_clear();
        return NULL;
    }
    
    // 查找
    for (int i = 0; i < context.count; i++) {
        if (strcmp(context.items[i].key, key) == 0) {
            return context.items[i].value;
        }
    }
    
    return NULL;
}

// 清除上下文
void context_clear(void)
{
    context.count = 0;
}

// 使用示例
void example_multi_turn_dialog(void)
{
    // 第一轮：用户说"打开客厅的灯"
    context_set("room", "客厅");
    context_set("device", "灯");
    cmd_turn_on_light("客厅");
    
    // 第二轮：用户说"把它调亮一点"
    const char *room = context_get("room");
    const char *device = context_get("device");
    if (room && device) {
        // 知道是要调节客厅的灯
        ESP_LOGI("DIALOG", "调节%s的%s亮度", room, device);
    }
}
```

**代码说明**：
- 第21-29行：计算音频能量，用于判断是否有语音
- 第32-56行：VAD处理逻辑，检测语音开始和结束
- 第88-100行：简单的回声消除算法
- 第125-145行：上下文管理，支持多轮对话


## 步骤7：测试与验证

### 7.1 功能测试

创建完整的测试用例：

```c
// test_voice_interaction.c
#include "unity.h"
#include "voice_interaction.h"

void test_wake_word_detection(void)
{
    // 测试唤醒词检测
    bool detected = false;
    
    // 播放包含唤醒词的音频
    int16_t test_audio[512];
    load_test_audio("wake_word_sample.wav", test_audio, 512);
    
    detected = wake_word_process(test_audio, 512);
    TEST_ASSERT_TRUE(detected);
}

void test_speech_recognition(void)
{
    // 测试语音识别
    speech_recognition_start();
    
    // 加载测试音频
    int16_t test_audio[16000];  // 1秒音频
    load_test_audio("command_sample.wav", test_audio, 16000);
    
    // 处理音频
    speech_recognition_process(test_audio, 16000);
    const char *result = speech_recognition_finish();
    
    TEST_ASSERT_NOT_NULL(result);
    TEST_ASSERT_TRUE(strlen(result) > 0);
}

void test_command_parsing(void)
{
    // 测试命令解析
    const char *test_commands[] = {
        "打开灯",
        "关闭灯",
        "设置温度25度",
        "查询天气"
    };
    
    for (int i = 0; i < 4; i++) {
        bool parsed = parse_voice_command(test_commands[i]);
        TEST_ASSERT_TRUE(parsed);
    }
}

void test_tts_synthesis(void)
{
    // 测试语音合成
    bool success = tts_speak("测试语音合成");
    TEST_ASSERT_TRUE(success);
}

void run_all_tests(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_wake_word_detection);
    RUN_TEST(test_speech_recognition);
    RUN_TEST(test_command_parsing);
    RUN_TEST(test_tts_synthesis);
    UNITY_END();
}
```

### 7.2 性能测试

```c
// performance_test.c
#include "esp_timer.h"

typedef struct {
    uint32_t wake_word_latency;
    uint32_t recognition_latency;
    uint32_t tts_latency;
    float cpu_usage;
    uint32_t memory_usage;
} performance_metrics_t;

static performance_metrics_t metrics = {0};

// 测量唤醒词延迟
void measure_wake_word_latency(void)
{
    uint64_t start = esp_timer_get_time();
    
    // 处理音频帧
    int16_t audio[512];
    audio_read(audio, 512);
    wake_word_process(audio, 512);
    
    uint64_t end = esp_timer_get_time();
    metrics.wake_word_latency = (end - start) / 1000;  // 转换为毫秒
    
    ESP_LOGI("PERF", "Wake word latency: %lu ms", metrics.wake_word_latency);
}

// 测量识别延迟
void measure_recognition_latency(void)
{
    uint64_t start = esp_timer_get_time();
    
    // 完整识别流程
    speech_recognition_start();
    // ... 处理音频 ...
    speech_recognition_finish();
    
    uint64_t end = esp_timer_get_time();
    metrics.recognition_latency = (end - start) / 1000;
    
    ESP_LOGI("PERF", "Recognition latency: %lu ms", metrics.recognition_latency);
}

// 测量CPU使用率
void measure_cpu_usage(void)
{
    // 使用FreeRTOS的任务统计功能
    TaskStatus_t *task_array;
    uint32_t total_runtime;
    uint32_t task_count;
    
    task_count = uxTaskGetNumberOfTasks();
    task_array = pvPortMalloc(task_count * sizeof(TaskStatus_t));
    
    if (task_array) {
        task_count = uxTaskGetSystemState(task_array, task_count, &total_runtime);
        
        // 计算语音任务的CPU占用
        for (int i = 0; i < task_count; i++) {
            if (strcmp(task_array[i].pcTaskName, "voice_int") == 0) {
                metrics.cpu_usage = (float)task_array[i].ulRunTimeCounter / total_runtime * 100;
                break;
            }
        }
        
        vPortFree(task_array);
    }
    
    ESP_LOGI("PERF", "CPU usage: %.2f%%", metrics.cpu_usage);
}

// 测量内存使用
void measure_memory_usage(void)
{
    metrics.memory_usage = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    ESP_LOGI("PERF", "Free memory: %lu bytes", metrics.memory_usage);
}

// 性能测试报告
void print_performance_report(void)
{
    ESP_LOGI("PERF", "=== Performance Report ===");
    ESP_LOGI("PERF", "Wake word latency: %lu ms", metrics.wake_word_latency);
    ESP_LOGI("PERF", "Recognition latency: %lu ms", metrics.recognition_latency);
    ESP_LOGI("PERF", "TTS latency: %lu ms", metrics.tts_latency);
    ESP_LOGI("PERF", "CPU usage: %.2f%%", metrics.cpu_usage);
    ESP_LOGI("PERF", "Free memory: %lu bytes", metrics.memory_usage);
}
```

### 7.3 测试检查表

- [ ] 唤醒词检测准确率 > 95%
- [ ] 唤醒词响应延迟 < 500ms
- [ ] 语音识别准确率 > 90%
- [ ] 识别延迟 < 2秒
- [ ] TTS合成自然流畅
- [ ] CPU占用率 < 30%
- [ ] 内存占用 < 2MB
- [ ] 在噪声环境下仍能工作
- [ ] 无误唤醒现象
- [ ] 多轮对话正常

**性能指标**：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 唤醒词延迟 | < 500ms | 从说出到检测到 |
| 识别延迟 | < 2s | 完整语句识别时间 |
| TTS延迟 | < 1s | 文本到开始播放 |
| CPU占用 | < 30% | 平均CPU使用率 |
| 内存占用 | < 2MB | RAM使用量 |
| 识别准确率 | > 90% | 正确识别率 |
| 误唤醒率 | < 1/小时 | 误触发频率 |


## 故障排除

### 问题1：唤醒词检测不灵敏

**可能原因**：
- 麦克风增益过低
- 环境噪声过大
- 唤醒词模型不匹配
- 灵敏度阈值设置不当

**解决方法**：

1. **调整麦克风增益**
```c
// 增加麦克风增益
void increase_mic_gain(void)
{
    // 调整AGC目标电平
    apply_agc(audio_buffer, count, 12000.0f);  // 提高目标电平
}
```

2. **降低噪声门限**
```c
// 降低噪声门限，提高灵敏度
apply_noise_gate(samples, count, 100);  // 从200降到100
```

3. **调整唤醒词灵敏度**
```c
// 降低灵敏度阈值(0.3-0.7)
pv_porcupine_init(
    access_key,
    model_path,
    1,
    keywords,
    &(const float[]){0.3f},  // 降低阈值提高灵敏度
    &porcupine
);
```

### 问题2：语音识别准确率低

**可能原因**：
- 音频质量差
- 模型不适合当前语言/口音
- 背景噪声干扰
- 说话速度过快或过慢

**解决方法**：

1. **改善音频质量**
```c
// 增强预处理
void enhanced_preprocess(int16_t *samples, size_t count)
{
    // 1. 去除直流分量
    remove_dc_offset(samples, count);
    
    // 2. 带通滤波(保留300-3400Hz)
    apply_bandpass_filter(samples, count, 300, 3400);
    
    // 3. 降噪
    apply_noise_reduction(samples, count);
    
    // 4. AGC
    apply_agc(samples, count, 10000.0f);
}
```

2. **使用更好的模型**
- 下载适合目标语言的模型
- 使用更大的模型(如果资源允许)
- 考虑使用云端识别API

3. **添加语言模型**
```c
// 使用自定义语法约束
const char *grammar = 
    "#JSGF V1.0;\n"
    "grammar commands;\n"
    "public <command> = 打开 | 关闭 | 设置 | 查询;\n"
    "public <device> = 灯 | 空调 | 电视;\n";

vosk_recognizer_set_grammar(recognizer, grammar);
```

### 问题3：TTS语音不自然

**可能原因**：
- TTS引擎质量限制
- 语速或音调设置不当
- 文本格式问题

**解决方法**：

1. **优化TTS参数**
```c
// 调整语速和音调
espeak_SetParameter(espeakRATE, 150, 0);     // 降低语速
espeak_SetParameter(espeakPITCH, 50, 0);     // 调整音调
espeak_SetParameter(espeakRANGE, 50, 0);     // 音调范围
```

2. **文本预处理**
```c
// 处理数字和特殊字符
char* preprocess_text(const char *text)
{
    // 将数字转换为中文
    // "25度" -> "二十五度"
    // 添加停顿标记
    // 处理多音字
    return processed_text;
}
```

3. **使用云端TTS**
- 调用百度、阿里云等TTS API
- 获得更自然的语音效果
- 需要网络连接

### 问题4：系统响应延迟高

**可能原因**：
- CPU负载过高
- 内存不足导致频繁GC
- 音频缓冲区设置不当
- 算法效率低

**解决方法**：

1. **优化任务优先级**
```c
// 提高语音任务优先级
xTaskCreate(voice_interaction_task, "voice_int", 
            8192, NULL, 
            configMAX_PRIORITIES - 1,  // 高优先级
            NULL);
```

2. **减少处理负载**
```c
// 降低采样率(如果可接受)
#define SAMPLE_RATE 8000  // 从16000降到8000

// 使用更小的模型
// 减少音频缓冲区大小
```

3. **使用硬件加速**
```c
// 启用DSP加速(如果硬件支持)
#ifdef CONFIG_ESP32_DSP_ENABLED
    dspi2s_init();
    use_dsp_for_preprocessing();
#endif
```

### 问题5：内存不足

**可能原因**：
- 模型文件过大
- 音频缓冲区过多
- 内存泄漏

**解决方法**：

1. **使用外部存储**
```c
// 模型文件放在SD卡
vosk_model_new("/sdcard/model");

// 使用PSRAM(如果有)
#ifdef CONFIG_SPIRAM_SUPPORT
    heap_caps_malloc(size, MALLOC_CAP_SPIRAM);
#endif
```

2. **优化缓冲区**
```c
// 减少DMA缓冲区数量
#define DMA_BUF_COUNT   2  // 从4减到2
#define DMA_BUF_LEN     256  // 从512减到256
```

3. **检查内存泄漏**
```c
// 定期检查内存
void check_memory_leak(void)
{
    static uint32_t last_free = 0;
    uint32_t current_free = esp_get_free_heap_size();
    
    if (last_free > 0 && current_free < last_free - 1024) {
        ESP_LOGW("MEM", "Possible memory leak: %lu bytes lost", 
                 last_free - current_free);
    }
    
    last_free = current_free;
}
```


## 进阶功能

### 云端语音服务集成

对于资源受限的设备，可以使用云端语音服务：

```c
// cloud_asr.c - 云端语音识别
#include "esp_http_client.h"
#include "cJSON.h"

// 百度语音识别API示例
char* baidu_asr(const int16_t *audio, size_t samples)
{
    // 1. 获取访问令牌
    char *access_token = get_baidu_access_token();
    
    // 2. 准备音频数据(转换为base64)
    char *audio_base64 = base64_encode((uint8_t*)audio, samples * 2);
    
    // 3. 构建请求
    cJSON *root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "format", "pcm");
    cJSON_AddNumberToObject(root, "rate", 16000);
    cJSON_AddNumberToObject(root, "channel", 1);
    cJSON_AddStringToObject(root, "cuid", "ESP32_DEVICE");
    cJSON_AddStringToObject(root, "token", access_token);
    cJSON_AddStringToObject(root, "speech", audio_base64);
    cJSON_AddNumberToObject(root, "len", samples * 2);
    
    char *json_str = cJSON_PrintUnformatted(root);
    
    // 4. 发送HTTP请求
    esp_http_client_config_t config = {
        .url = "https://vop.baidu.com/server_api",
        .method = HTTP_METHOD_POST,
    };
    
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, json_str, strlen(json_str));
    
    esp_err_t err = esp_http_client_perform(client);
    
    // 5. 解析响应
    char *result = NULL;
    if (err == ESP_OK) {
        int content_length = esp_http_client_get_content_length(client);
        char *response = malloc(content_length + 1);
        esp_http_client_read(client, response, content_length);
        response[content_length] = '\0';
        
        // 解析JSON获取识别结果
        cJSON *response_json = cJSON_Parse(response);
        cJSON *result_item = cJSON_GetObjectItem(response_json, "result");
        if (result_item && cJSON_IsArray(result_item)) {
            cJSON *first = cJSON_GetArrayItem(result_item, 0);
            if (first && cJSON_IsString(first)) {
                result = strdup(first->valuestring);
            }
        }
        
        cJSON_Delete(response_json);
        free(response);
    }
    
    // 清理
    esp_http_client_cleanup(client);
    cJSON_Delete(root);
    free(json_str);
    free(audio_base64);
    free(access_token);
    
    return result;
}
```

### 自然语言理解(NLU)

实现意图识别和实体提取：

```c
// nlu.c - Natural Language Understanding
typedef struct {
    char intent[32];
    char entities[5][64];
    int entity_count;
    float confidence;
} nlu_result_t;

// 简单的规则匹配NLU
nlu_result_t* parse_intent(const char *text)
{
    nlu_result_t *result = malloc(sizeof(nlu_result_t));
    memset(result, 0, sizeof(nlu_result_t));
    
    // 意图识别
    if (strstr(text, "打开") || strstr(text, "开")) {
        strcpy(result->intent, "turn_on");
    } else if (strstr(text, "关闭") || strstr(text, "关")) {
        strcpy(result->intent, "turn_off");
    } else if (strstr(text, "设置") || strstr(text, "调节")) {
        strcpy(result->intent, "set_value");
    } else if (strstr(text, "查询") || strstr(text, "怎么样")) {
        strcpy(result->intent, "query");
    }
    
    // 实体提取
    if (strstr(text, "灯")) {
        strcpy(result->entities[result->entity_count++], "device:light");
    }
    if (strstr(text, "空调")) {
        strcpy(result->entities[result->entity_count++], "device:ac");
    }
    if (strstr(text, "客厅")) {
        strcpy(result->entities[result->entity_count++], "location:living_room");
    }
    if (strstr(text, "卧室")) {
        strcpy(result->entities[result->entity_count++], "location:bedroom");
    }
    
    // 提取数字
    char *num_pos = text;
    while (*num_pos) {
        if (isdigit(*num_pos)) {
            char num_str[16];
            int i = 0;
            while (isdigit(*num_pos) && i < 15) {
                num_str[i++] = *num_pos++;
            }
            num_str[i] = '\0';
            sprintf(result->entities[result->entity_count++], "number:%s", num_str);
            break;
        }
        num_pos++;
    }
    
    result->confidence = 0.8f;
    return result;
}

// 使用NLU结果执行命令
void execute_intent(nlu_result_t *nlu)
{
    ESP_LOGI("NLU", "Intent: %s, Entities: %d", nlu->intent, nlu->entity_count);
    
    if (strcmp(nlu->intent, "turn_on") == 0) {
        // 查找设备实体
        for (int i = 0; i < nlu->entity_count; i++) {
            if (strncmp(nlu->entities[i], "device:", 7) == 0) {
                const char *device = nlu->entities[i] + 7;
                ESP_LOGI("NLU", "Turn on device: %s", device);
                // 执行开启操作
            }
        }
    }
    // 其他意图处理...
}
```

### 情感识别

添加简单的情感分析：

```c
// emotion.c - 情感识别
typedef enum {
    EMOTION_NEUTRAL,
    EMOTION_HAPPY,
    EMOTION_ANGRY,
    EMOTION_SAD
} emotion_t;

// 基于关键词的情感识别
emotion_t detect_emotion(const char *text)
{
    // 积极词汇
    const char *positive_words[] = {"好", "棒", "喜欢", "开心", "谢谢", NULL};
    // 消极词汇
    const char *negative_words[] = {"不好", "讨厌", "生气", "难过", "烦", NULL};
    
    int positive_count = 0;
    int negative_count = 0;
    
    // 统计情感词
    for (int i = 0; positive_words[i] != NULL; i++) {
        if (strstr(text, positive_words[i])) {
            positive_count++;
        }
    }
    
    for (int i = 0; negative_words[i] != NULL; i++) {
        if (strstr(text, negative_words[i])) {
            negative_count++;
        }
    }
    
    // 判断情感
    if (positive_count > negative_count) {
        return EMOTION_HAPPY;
    } else if (negative_count > positive_count) {
        return EMOTION_ANGRY;
    }
    
    return EMOTION_NEUTRAL;
}

// 根据情感调整回复
void respond_with_emotion(const char *text, emotion_t emotion)
{
    switch (emotion) {
        case EMOTION_HAPPY:
            tts_speak("很高兴为您服务");
            break;
        case EMOTION_ANGRY:
            tts_speak("抱歉让您不满意，我会改进的");
            break;
        case EMOTION_SAD:
            tts_speak("希望能帮到您");
            break;
        default:
            tts_speak(text);
            break;
    }
}
```


## 总结

通过本教程，你学习了：

- ✅ 语音交互系统的完整架构和工作流程
- ✅ 音频采集、预处理和信号处理技术
- ✅ 唤醒词检测的实现方法和优化技巧
- ✅ 离线语音识别引擎的集成和使用
- ✅ 语音合成(TTS)的实现和参数调优
- ✅ 完整的语音交互状态机设计
- ✅ VAD、AEC等音频处理算法
- ✅ 多轮对话和上下文管理
- ✅ 性能优化和故障排除方法

**关键要点**：

1. **音频质量是基础**：良好的音频采集和预处理直接影响识别准确率
2. **唤醒词要可靠**：低功耗、低延迟、高准确率是唤醒词的核心要求
3. **用户体验优先**：快速响应、自然反馈、容错处理提升用户满意度
4. **资源平衡**：在准确率、延迟和资源占用之间找到平衡点
5. **持续优化**：根据实际使用情况不断调整参数和算法

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现声纹识别，区分不同用户
2. **挑战2**：添加多语言支持，自动检测语言
3. **挑战3**：实现离线+在线混合模式，网络可用时使用云端识别
4. **挑战4**：优化功耗，实现超低功耗唤醒
5. **挑战5**：集成ChatGPT等大语言模型，实现智能对话

## 完整代码

完整的项目代码可以在这里下载：

- GitHub仓库：[voice-interaction-demo](https://github.com/embedded-platform/voice-interaction-demo)
- 包含所有源代码、模型文件和测试用例
- 支持ESP32-S3和STM32F7平台

## 下一步

建议继续学习：

- [手势识别与体感控制](02-gesture-recognition.html) - 学习多模态交互
- 嵌入式AI与机器学习 - 深入AI技术
- 应用框架设计 - 系统架构设计

## 参考资料

### 开源项目

1. **Porcupine** - https://github.com/Picovoice/porcupine
   - 轻量级唤醒词检测引擎
   
2. **Vosk** - https://github.com/alphacep/vosk-api
   - 离线语音识别工具包
   
3. **eSpeak NG** - https://github.com/espeak-ng/espeak-ng
   - 开源TTS引擎
   
4. **Sherpa-ONNX** - https://github.com/k2-fsa/sherpa-onnx
   - 端到端语音识别框架

### 技术文档

1. ESP-IDF Audio Development Framework
2. STM32 Audio Processing Library
3. CMSIS-DSP Documentation
4. WebRTC Audio Processing

### 学术论文

1. "Deep Speech: Scaling up end-to-end speech recognition" - Baidu Research
2. "Listen, Attend and Spell" - Google Brain
3. "WaveNet: A Generative Model for Raw Audio" - DeepMind
4. "Tacotron: Towards End-to-End Speech Synthesis" - Google

### 在线资源

1. [语音信号处理基础](https://www.coursera.org/learn/audio-signal-processing)
2. [深度学习语音识别](https://www.deeplearning.ai/courses/speech-recognition/)
3. [嵌入式AI开发指南](https://www.tensorflow.org/lite/microcontrollers)

---

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言或提交Issue！

**许可证**：本教程采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可协议。

