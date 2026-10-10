---
title: "生物信号处理基础：ECG/EEG信号采集与分析"
description: "全面介绍医疗设备中的生物信号处理技术，包括ECG心电信号和EEG脑电信号的采集原理、滤波处理、特征提取和算法实现，通过实践教程掌握生物信号处理的核心技能"
slug: "biosignal-processing-basics"

# 分类信息
domain: "行业领域"
module: "医疗设备"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - 生物信号处理
  - ECG心电图
  - EEG脑电图
  - 信号采集
  - 数字滤波
  - 特征提取
prerequisites:
  - "medical-device-standards-regulations"
related_contents: []

# 学习信息
estimated_time: 80
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
  - 生物信号处理
  - ECG信号采集
  - EEG信号分析
  - 医疗信号处理
  - 数字滤波算法
  - 心电图处理
cover_image: ""
---

# 生物信号处理基础：ECG/EEG信号采集与分析

## 学习目标

完成本教程后，你将能够：

- [ ] 理解生物信号的基本特征和采集原理
- [ ] 掌握ECG和EEG信号的生理学基础
- [ ] 实现模拟前端电路的信号调理
- [ ] 应用数字滤波算法去除噪声和干扰
- [ ] 提取生物信号的关键特征参数
- [ ] 开发完整的生物信号采集和处理系统

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 了解基本的电路原理和模拟电子技术
- 掌握C语言编程基础
- 理解数字信号处理的基本概念
- 熟悉ADC（模数转换器）的工作原理
- 了解医疗设备的基本安全要求

**技能要求**：
- 能够使用示波器观察和分析信号
- 会使用嵌入式开发工具（如STM32CubeIDE）
- 能够进行基本的电路焊接和调试
- 熟悉Python或MATLAB进行数据分析（可选）

**推荐预习**：
- [医疗设备标准与法规](./01-medical-device-standards.html) - 了解医疗设备开发的合规要求

## 准备工作

### 硬件准备

| 名称 | 数量 | 规格说明 | 参考型号 |
|------|------|----------|----------|
| 微控制器开发板 | 1 | STM32F4系列，带12位ADC | STM32F407 Discovery |
| 生物信号采集模块 | 1 | AD8232心电采集模块 | AD8232 ECG模块 |
| 运算放大器 | 2 | 低噪声、高CMRR | OPA2134, INA128 |
| 滤波电容 | 若干 | 0.1μF, 1μF, 10μF | 陶瓷/钽电容 |
| 电阻 | 若干 | 1kΩ-1MΩ | 1%精度金属膜电阻 |
| 电极片 | 3 | 一次性医用电极 | Ag/AgCl电极 |
| 面包板 | 1 | 标准面包板 | - |
| 杜邦线 | 若干 | 公对公、公对母 | - |
| USB转串口模块 | 1 | 用于数据传输 | CH340, CP2102 |

### 软件准备

**开发环境**：
- STM32CubeIDE v1.10+ 或 Keil MDK
- Python 3.8+ （用于数据分析和可视化）
- MATLAB R2020a+ （可选，用于信号分析）

**Python库**：
```bash
pip install numpy scipy matplotlib pandas
pip install pyserial  # 用于串口通信
```

**辅助工具**：
- 串口调试助手（如PuTTY、Tera Term）
- 示波器或逻辑分析仪（用于信号调试）
- ST-Link驱动程序

### 环境配置

1. **安装开发环境**
   - 下载并安装STM32CubeIDE
   - 安装ST-Link驱动
   - 配置Python开发环境

2. **测试硬件连接**
   - 连接开发板到电脑
   - 验证ST-Link连接正常
   - 测试串口通信

3. **准备测试信号**
   - 下载标准ECG测试数据（MIT-BIH数据库）
   - 准备信号发生器（可选）

## 背景知识

### 什么是生物信号？

**生物信号（Biosignal）**是指从生物体中测量到的电信号、机械信号或化学信号，这些信号携带了生理状态和病理信息。

**常见的生物电信号**：

1. **ECG（心电图，Electrocardiogram）**
   - 记录心脏电活动
   - 频率范围：0.05-100 Hz
   - 幅度范围：0.5-4 mV
   - 应用：心脏疾病诊断、心率监测

2. **EEG（脑电图，Electroencephalogram）**
   - 记录大脑电活动
   - 频率范围：0.5-100 Hz
   - 幅度范围：10-100 μV
   - 应用：癫痫诊断、睡眠研究、脑机接口

3. **EMG（肌电图，Electromyogram）**
   - 记录肌肉电活动
   - 频率范围：10-500 Hz
   - 幅度范围：0.1-5 mV
   - 应用：神经肌肉疾病诊断、康复评估

4. **EOG（眼电图，Electrooculogram）**
   - 记录眼球运动
   - 频率范围：0.1-10 Hz
   - 幅度范围：50-3500 μV
   - 应用：睡眠研究、眼动追踪

### ECG信号基础

**心电图的生理学原理**：

心脏的电活动由窦房结（SA节点）产生，电信号依次传导到心房、房室结、希氏束、浦肯野纤维，最后到达心室，引起心肌收缩。

**ECG波形组成**：

```
      R
      |
      |
  P   |   T
 / \  |  / \
/   \ | /   \
-----\|/-----\___
      Q      S
```

- **P波**：心房去极化（0.08-0.12秒）
- **QRS波群**：心室去极化（0.06-0.10秒）
  - Q波：室间隔去极化
  - R波：心室主要去极化
  - S波：心室基底部去极化
- **T波**：心室复极化（0.16-0.20秒）
- **U波**：浦肯野纤维复极化（可能不明显）

**重要时间间期**：
- **PR间期**：0.12-0.20秒（心房到心室传导时间）
- **QRS时限**：0.06-0.10秒（心室去极化时间）
- **QT间期**：0.35-0.44秒（心室电活动总时间）
- **RR间期**：心跳周期，用于计算心率

**心率计算**：
```
心率(bpm) = 60 / RR间期(秒)
```

### EEG信号基础

**脑电图的生理学原理**：

EEG记录的是大脑皮层神经元的突触后电位的总和。数百万个神经元同步活动产生的电场可以在头皮表面检测到。

**EEG频段分类**：

| 频段 | 频率范围 | 特征 | 相关状态 |
|------|---------|------|----------|
| Delta (δ) | 0.5-4 Hz | 高幅度 | 深度睡眠、婴儿 |
| Theta (θ) | 4-8 Hz | 中等幅度 | 浅睡眠、冥想 |
| Alpha (α) | 8-13 Hz | 节律性 | 放松、闭眼清醒 |
| Beta (β) | 13-30 Hz | 低幅度 | 警觉、思考 |
| Gamma (γ) | 30-100 Hz | 极低幅度 | 认知处理、注意力 |

**EEG电极位置**：

国际10-20系统定义了标准的电极位置：
- Fp（额极）、F（额）、C（中央）、P（顶）、O（枕）、T（颞）
- 奇数：左半球，偶数：右半球
- z：中线位置

### 信号采集的挑战

**1. 信号微弱**：
- ECG：毫伏级（mV）
- EEG：微伏级（μV）
- 需要高增益放大器

**2. 噪声干扰**：
- **工频干扰**：50/60 Hz电源干扰
- **肌电干扰**：肌肉活动产生的高频噪声
- **运动伪迹**：电极移动产生的低频漂移
- **电极接触噪声**：电极与皮肤接触不良

**3. 共模干扰**：
- 人体作为天线接收环境电磁干扰
- 需要高共模抑制比（CMRR > 80 dB）

**4. 安全要求**：
- 患者隔离（电气隔离）
- 漏电流限制
- 除颤保护

## 步骤1：信号采集电路设计

### 1.1 模拟前端架构

生物信号采集的典型信号链：

```
电极 → 保护电路 → 仪表放大器 → 高通滤波 → 增益放大 → 低通滤波 → ADC → MCU
```

**各级功能**：

1. **保护电路**：防止除颤脉冲和静电损坏
2. **仪表放大器**：高输入阻抗、高CMRR、低噪声
3. **高通滤波**：去除直流偏置和低频漂移（0.05 Hz）
4. **增益放大**：将微弱信号放大到ADC输入范围
5. **低通滤波**：抗混叠滤波，防止高频噪声（100 Hz）
6. **ADC**：模数转换，通常12位或更高

### 1.2 使用AD8232 ECG模块

**AD8232特点**：
- 集成仪表放大器和滤波器
- 高CMRR（80 dB @ 60 Hz）
- 低功耗（170 μA）
- 内置右腿驱动（RLD）
- 导联脱落检测

**电路连接**：

```
AD8232模块引脚：
- RA (Right Arm)  → 右臂电极
- LA (Left Arm)   → 左臂电极
- RL (Right Leg)  → 右腿电极（参考）
- OUTPUT          → MCU ADC输入
- LO+ / LO-       → 导联脱落检测
- 3.3V / GND      → 电源
```

**与STM32连接**：

| AD8232引脚 | STM32引脚 | 说明 |
|-----------|----------|------|
| OUTPUT | PA0 (ADC1_IN0) | ECG信号输出 |
| LO+ | PA1 | 导联脱落检测+ |
| LO- | PA2 | 导联脱落检测- |
| 3.3V | 3.3V | 电源 |
| GND | GND | 地 |

### 1.3 电极放置

**标准三导联ECG配置**：

```
        RA (右臂)
         |
         |
    LA--心脏--RL
   (左臂)    (右腿)
```

**电极位置**：
- **RA（右臂）**：右锁骨下方
- **LA（左臂）**：左锁骨下方
- **RL（右腿）**：左下腹部或左腿（参考电极）

**注意事项**：
- 清洁皮肤，去除油脂和死皮
- 确保电极与皮肤良好接触
- 避免电极线缠绕和拉扯
- 保持患者放松，减少肌电干扰

### 1.4 电路测试

**使用示波器验证**：

1. **检查电源**：
   - 测量3.3V电源是否稳定
   - 检查地线连接

2. **观察输出**：
   - 将示波器探头连接到OUTPUT引脚
   - 设置时基：200 ms/div
   - 设置电压：500 mV/div
   - 应该看到周期性的ECG波形

3. **检查噪声**：
   - 断开电极，观察噪声水平
   - 噪声应小于10 mV峰峰值
   - 如果噪声过大，检查接地和屏蔽

**预期结果**：
- 清晰的QRS波群
- P波和T波可见
- 基线稳定，无明显漂移
- 心率约60-100 bpm

## 步骤2：ADC配置和数据采集

### 2.1 创建STM32项目

1. **新建工程**：
   - 打开STM32CubeIDE
   - File → New → STM32 Project
   - 选择STM32F407VGT6
   - 项目名称：`ECG_Signal_Processing`

2. **配置时钟**：
   - 在Clock Configuration中设置系统时钟为168 MHz
   - APB1时钟：42 MHz
   - APB2时钟：84 MHz

### 2.2 配置ADC

**ADC参数设置**：

1. **在Pinout视图中配置PA0**：
   - 右键PA0 → ADC1_IN0

2. **ADC1配置**：
   ```
   Mode:
   - IN0: Single-ended
   
   Configuration:
   - Resolution: 12 bits
   - Data Alignment: Right alignment
   - Scan Conversion Mode: Disabled
   - Continuous Conversion Mode: Enabled
   - Discontinuous Conversion Mode: Disabled
   - DMA Continuous Requests: Enabled
   
   Regular Conversion:
   - Number of Conversion: 1
   - External Trigger: Disabled
   - Rank 1: Channel 0, Sampling Time: 84 Cycles
   ```

3. **计算采样率**：
   ```
   ADC时钟 = APB2 / 2 = 84 MHz / 2 = 42 MHz
   转换时间 = (采样时间 + 12周期) / ADC时钟
            = (84 + 12) / 42 MHz
            = 2.29 μs
   采样率 = 1 / 2.29 μs ≈ 437 kHz
   ```

   对于ECG信号，我们需要降低采样率到500 Hz左右。

### 2.3 配置DMA

**DMA设置**（用于高效数据传输）：

1. **添加DMA请求**：
   - DMA Settings → Add
   - DMA Request: ADC1
   - Stream: DMA2 Stream 0
   - Direction: Peripheral to Memory
   - Priority: High
   - Mode: Circular
   - Data Width: Half Word (16 bits)

2. **配置DMA参数**：
   ```
   Increment Address:
   - Peripheral: Disabled
   - Memory: Enabled
   
   Data Width:
   - Peripheral: Half Word
   - Memory: Half Word
   ```

### 2.4 配置定时器（用于精确采样）

**使用TIM2触发ADC采样**：

1. **配置TIM2**：
   ```
   Clock Source: Internal Clock
   Prescaler: 8399 (84 MHz / 8400 = 10 kHz)
   Counter Period: 19 (10 kHz / 20 = 500 Hz)
   Trigger Output (TRGO): Update Event
   ```

2. **修改ADC触发源**：
   ```
   External Trigger Conversion Source: Timer 2 Trigger Out event
   External Trigger Conversion Edge: Rising edge
   ```

### 2.5 编写采集代码

**在main.c中添加代码**：

```c
/* USER CODE BEGIN Includes */
#include <string.h>
#include <stdio.h>
/* USER CODE END Includes */

/* USER CODE BEGIN PV */
#define BUFFER_SIZE 1000  // 2秒数据 (500 Hz × 2)
uint16_t adc_buffer[BUFFER_SIZE];
volatile uint8_t buffer_full = 0;
/* USER CODE END PV */

/* USER CODE BEGIN 2 */
// 启动ADC和DMA
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUFFER_SIZE);

// 启动定时器
HAL_TIM_Base_Start(&htim2);

printf("ECG采集系统启动\r\n");
printf("采样率: 500 Hz\r\n");
printf("缓冲区大小: %d 样本\r\n", BUFFER_SIZE);
/* USER CODE END 2 */

/* USER CODE BEGIN 4 */
// DMA传输完成回调
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
    if (hadc->Instance == ADC1) {
        buffer_full = 1;  // 标记缓冲区已满
    }
}

// 串口重定向（用于printf）
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart2, (uint8_t*)ptr, len, HAL_MAX_DELAY);
    return len;
}
/* USER CODE END 4 */
```

**主循环处理**：

```c
/* USER CODE BEGIN WHILE */
while (1)
{
    if (buffer_full) {
        buffer_full = 0;
        
        // 处理数据（后续步骤实现）
        process_ecg_data(adc_buffer, BUFFER_SIZE);
        
        // 发送数据到PC（可选）
        send_data_to_pc(adc_buffer, BUFFER_SIZE);
    }
    
    HAL_Delay(10);
    /* USER CODE END WHILE */
}
```

**代码说明**：
- 使用DMA循环模式自动采集数据
- TIM2以500 Hz触发ADC转换
- 缓冲区满时触发回调函数
- 数据存储在`adc_buffer`中供后续处理

### 2.6 验证数据采集

**编译和下载**：
1. 点击Build按钮编译项目
2. 连接ST-Link
3. 点击Run按钮下载程序

**测试采集**：
1. 连接电极到身体
2. 打开串口终端（115200波特率）
3. 观察输出信息
4. 验证数据采集正常

**预期结果**：
- 串口输出启动信息
- ADC持续采集数据
- 无错误提示

## 步骤3：数字滤波算法实现

### 3.1 滤波器设计原理

**为什么需要滤波？**

原始ECG信号包含：
- **有用信号**：0.05-100 Hz
- **工频干扰**：50/60 Hz
- **基线漂移**：< 0.5 Hz
- **肌电噪声**：> 100 Hz
- **高频噪声**：> 500 Hz

**滤波器类型**：

1. **高通滤波器（HPF）**：去除基线漂移
   - 截止频率：0.5 Hz
   - 保留：> 0.5 Hz

2. **低通滤波器（LPF）**：去除高频噪声
   - 截止频率：100 Hz
   - 保留：< 100 Hz

3. **陷波滤波器（Notch）**：去除工频干扰
   - 中心频率：50 Hz 或 60 Hz
   - 带宽：1-2 Hz

### 3.2 实现移动平均滤波器

**移动平均滤波器**是最简单的低通滤波器，适合去除高频噪声。

**原理**：
```
y[n] = (x[n] + x[n-1] + ... + x[n-N+1]) / N
```

**代码实现**：

```c
/* USER CODE BEGIN 0 */
#define MA_WINDOW_SIZE 5  // 移动平均窗口大小

// 移动平均滤波器
float moving_average_filter(float *buffer, int size, int index)
{
    float sum = 0;
    int count = 0;
    
    // 计算窗口内的平均值
    for (int i = 0; i < MA_WINDOW_SIZE && i <= index; i++) {
        sum += buffer[index - i];
        count++;
    }
    
    return sum / count;
}

// 批量滤波
void apply_moving_average(uint16_t *input, float *output, int size)
{
    for (int i = 0; i < size; i++) {
        // 转换ADC值到电压 (假设3.3V参考电压)
        float voltage = (input[i] * 3.3f) / 4096.0f;
        
        // 应用移动平均滤波
        if (i < MA_WINDOW_SIZE) {
            output[i] = voltage;  // 前几个样本直接使用
        } else {
            float sum = 0;
            for (int j = 0; j < MA_WINDOW_SIZE; j++) {
                sum += (input[i-j] * 3.3f) / 4096.0f;
            }
            output[i] = sum / MA_WINDOW_SIZE;
        }
    }
}
/* USER CODE END 0 */
```

### 3.3 实现IIR低通滤波器

**IIR（无限脉冲响应）滤波器**效率更高，适合实时处理。

**一阶低通滤波器**：
```
y[n] = α × x[n] + (1-α) × y[n-1]
```

其中，α = Δt / (RC + Δt)，Δt是采样周期。

**代码实现**：

```c
/* USER CODE BEGIN 0 */
#define ALPHA 0.1f  // 滤波系数 (0 < α < 1)

typedef struct {
    float prev_output;
    float alpha;
} IIR_LPF_t;

// 初始化IIR低通滤波器
void IIR_LPF_Init(IIR_LPF_t *filter, float alpha)
{
    filter->prev_output = 0;
    filter->alpha = alpha;
}

// IIR低通滤波
float IIR_LPF_Update(IIR_LPF_t *filter, float input)
{
    float output = filter->alpha * input + 
                   (1.0f - filter->alpha) * filter->prev_output;
    filter->prev_output = output;
    return output;
}

// 批量滤波
void apply_iir_lpf(uint16_t *input, float *output, int size)
{
    IIR_LPF_t filter;
    IIR_LPF_Init(&filter, ALPHA);
    
    for (int i = 0; i < size; i++) {
        float voltage = (input[i] * 3.3f) / 4096.0f;
        output[i] = IIR_LPF_Update(&filter, voltage);
    }
}
/* USER CODE END 0 */
```

**参数选择**：
- α = 0.1：强滤波，响应慢
- α = 0.5：中等滤波
- α = 0.9：弱滤波，响应快

### 3.4 实现高通滤波器

**高通滤波器**用于去除基线漂移。

**一阶高通滤波器**：
```
y[n] = α × (y[n-1] + x[n] - x[n-1])
```

**代码实现**：

```c
/* USER CODE BEGIN 0 */
typedef struct {
    float prev_input;
    float prev_output;
    float alpha;
} IIR_HPF_t;

// 初始化IIR高通滤波器
void IIR_HPF_Init(IIR_HPF_t *filter, float alpha)
{
    filter->prev_input = 0;
    filter->prev_output = 0;
    filter->alpha = alpha;
}

// IIR高通滤波
float IIR_HPF_Update(IIR_HPF_t *filter, float input)
{
    float output = filter->alpha * (filter->prev_output + 
                                    input - filter->prev_input);
    filter->prev_input = input;
    filter->prev_output = output;
    return output;
}

// 批量滤波
void apply_iir_hpf(float *input, float *output, int size)
{
    IIR_HPF_t filter;
    IIR_HPF_Init(&filter, 0.95f);  // α接近1，截止频率低
    
    for (int i = 0; i < size; i++) {
        output[i] = IIR_HPF_Update(&filter, input[i]);
    }
}
/* USER CODE END 0 */
```

### 3.5 实现陷波滤波器

**陷波滤波器**用于去除50/60 Hz工频干扰。

**二阶陷波滤波器**：
```
y[n] = b0×x[n] + b1×x[n-1] + b2×x[n-2] - a1×y[n-1] - a2×y[n-2]
```

**代码实现**（50 Hz陷波）：

```c
/* USER CODE BEGIN 0 */
typedef struct {
    float x1, x2;  // 输入历史
    float y1, y2;  // 输出历史
    float b0, b1, b2;  // 分子系数
    float a1, a2;      // 分母系数
} Notch_Filter_t;

// 初始化50Hz陷波滤波器 (采样率500Hz)
void Notch_Filter_Init(Notch_Filter_t *filter)
{
    // 50 Hz陷波滤波器系数 (Q=30)
    filter->b0 = 0.9802f;
    filter->b1 = -1.5557f;
    filter->b2 = 0.9802f;
    filter->a1 = -1.5557f;
    filter->a2 = 0.9604f;
    
    filter->x1 = 0;
    filter->x2 = 0;
    filter->y1 = 0;
    filter->y2 = 0;
}

// 陷波滤波
float Notch_Filter_Update(Notch_Filter_t *filter, float input)
{
    float output = filter->b0 * input + 
                   filter->b1 * filter->x1 + 
                   filter->b2 * filter->x2 -
                   filter->a1 * filter->y1 - 
                   filter->a2 * filter->y2;
    
    // 更新历史
    filter->x2 = filter->x1;
    filter->x1 = input;
    filter->y2 = filter->y1;
    filter->y1 = output;
    
    return output;
}

// 批量滤波
void apply_notch_filter(float *input, float *output, int size)
{
    Notch_Filter_t filter;
    Notch_Filter_Init(&filter);
    
    for (int i = 0; i < size; i++) {
        output[i] = Notch_Filter_Update(&filter, input[i]);
    }
}
/* USER CODE END 0 */
```

### 3.6 完整的滤波流程

**组合多个滤波器**：

```c
/* USER CODE BEGIN 0 */
void process_ecg_data(uint16_t *raw_data, int size)
{
    static float temp_buffer1[BUFFER_SIZE];
    static float temp_buffer2[BUFFER_SIZE];
    static float filtered_data[BUFFER_SIZE];
    
    // 步骤1：低通滤波 (去除高频噪声)
    apply_iir_lpf(raw_data, temp_buffer1, size);
    
    // 步骤2：高通滤波 (去除基线漂移)
    apply_iir_hpf(temp_buffer1, temp_buffer2, size);
    
    // 步骤3：陷波滤波 (去除50Hz干扰)
    apply_notch_filter(temp_buffer2, filtered_data, size);
    
    // 步骤4：特征提取 (下一步实现)
    extract_ecg_features(filtered_data, size);
}
/* USER CODE END 0 */
```

**代码说明**：
- 使用多个临时缓冲区存储中间结果
- 按顺序应用不同的滤波器
- 最终得到干净的ECG信号

## 步骤4：特征提取算法

### 4.1 R波检测（Pan-Tompkins算法）

**Pan-Tompkins算法**是经典的QRS波检测算法，包含以下步骤：

1. 带通滤波（5-15 Hz）
2. 微分
3. 平方
4. 移动窗口积分
5. 自适应阈值检测

**算法实现**：

```c
/* USER CODE BEGIN 0 */
#define WINDOW_SIZE 30  // 积分窗口大小 (60ms @ 500Hz)

typedef struct {
    float threshold;
    float peak_value;
    int refractory_period;  // 不应期 (样本数)
    int last_qrs_index;
} QRS_Detector_t;

// 初始化QRS检测器
void QRS_Detector_Init(QRS_Detector_t *detector)
{
    detector->threshold = 0.5f;
    detector->peak_value = 0;
    detector->refractory_period = 100;  // 200ms @ 500Hz
    detector->last_qrs_index = -1000;
}

// 微分运算
void derivative(float *input, float *output, int size)
{
    for (int i = 2; i < size - 2; i++) {
        // 五点微分: y[n] = (2x[n+2] + x[n+1] - x[n-1] - 2x[n-2]) / 8
        output[i] = (2*input[i+2] + input[i+1] - 
                     input[i-1] - 2*input[i-2]) / 8.0f;
    }
}

// 平方运算
void square(float *input, float *output, int size)
{
    for (int i = 0; i < size; i++) {
        output[i] = input[i] * input[i];
    }
}

// 移动窗口积分
void moving_window_integration(float *input, float *output, int size)
{
    for (int i = 0; i < size; i++) {
        float sum = 0;
        int count = 0;
        
        for (int j = 0; j < WINDOW_SIZE && (i - j) >= 0; j++) {
            sum += input[i - j];
            count++;
        }
        
        output[i] = sum / count;
    }
}

// R波检测
int detect_r_peaks(float *signal, int size, int *peak_indices, int max_peaks)
{
    static float derivative_signal[BUFFER_SIZE];
    static float squared_signal[BUFFER_SIZE];
    static float integrated_signal[BUFFER_SIZE];
    
    // 步骤1：微分
    derivative(signal, derivative_signal, size);
    
    // 步骤2：平方
    square(derivative_signal, squared_signal, size);
    
    // 步骤3：移动窗口积分
    moving_window_integration(squared_signal, integrated_signal, size);
    
    // 步骤4：自适应阈值检测
    QRS_Detector_t detector;
    QRS_Detector_Init(&detector);
    
    int peak_count = 0;
    float max_value = 0;
    
    // 找到最大值用于初始化阈值
    for (int i = 0; i < size; i++) {
        if (integrated_signal[i] > max_value) {
            max_value = integrated_signal[i];
        }
    }
    detector.threshold = max_value * 0.3f;  // 初始阈值为最大值的30%
    
    // 检测峰值
    for (int i = 1; i < size - 1; i++) {
        // 检查是否在不应期内
        if (i - detector.last_qrs_index < detector.refractory_period) {
            continue;
        }
        
        // 检测局部最大值
        if (integrated_signal[i] > integrated_signal[i-1] &&
            integrated_signal[i] > integrated_signal[i+1] &&
            integrated_signal[i] > detector.threshold) {
            
            if (peak_count < max_peaks) {
                peak_indices[peak_count++] = i;
                detector.last_qrs_index = i;
                
                // 更新阈值 (自适应)
                detector.threshold = 0.7f * detector.threshold + 
                                    0.3f * integrated_signal[i];
            }
        }
    }
    
    return peak_count;
}
/* USER CODE END 0 */
```

### 4.2 心率计算

**从R波间期计算心率**：

```c
/* USER CODE BEGIN 0 */
typedef struct {
    float heart_rate;      // 心率 (bpm)
    float rr_interval;     // RR间期 (ms)
    float hrv;             // 心率变异性 (ms)
} ECG_Features_t;

// 计算心率和HRV
void calculate_heart_rate(int *peak_indices, int peak_count, 
                         float sampling_rate, ECG_Features_t *features)
{
    if (peak_count < 2) {
        features->heart_rate = 0;
        features->rr_interval = 0;
        features->hrv = 0;
        return;
    }
    
    // 计算RR间期 (样本数转换为毫秒)
    float *rr_intervals = malloc(sizeof(float) * (peak_count - 1));
    float sum_rr = 0;
    
    for (int i = 0; i < peak_count - 1; i++) {
        rr_intervals[i] = (peak_indices[i+1] - peak_indices[i]) * 
                         1000.0f / sampling_rate;
        sum_rr += rr_intervals[i];
    }
    
    // 平均RR间期
    float avg_rr = sum_rr / (peak_count - 1);
    features->rr_interval = avg_rr;
    
    // 心率 (bpm)
    features->heart_rate = 60000.0f / avg_rr;
    
    // 心率变异性 (SDNN - 标准差)
    float sum_squared_diff = 0;
    for (int i = 0; i < peak_count - 1; i++) {
        float diff = rr_intervals[i] - avg_rr;
        sum_squared_diff += diff * diff;
    }
    features->hrv = sqrtf(sum_squared_diff / (peak_count - 1));
    
    free(rr_intervals);
}
/* USER CODE END 0 */
```

### 4.3 波形特征提取

**提取P波、QRS波群、T波的特征**：

```c
/* USER CODE BEGIN 0 */
typedef struct {
    int p_wave_index;
    int q_wave_index;
    int r_wave_index;
    int s_wave_index;
    int t_wave_index;
    
    float pr_interval;   // PR间期 (ms)
    float qrs_duration;  // QRS时限 (ms)
    float qt_interval;   // QT间期 (ms)
    
    float r_amplitude;   // R波幅度 (mV)
    float t_amplitude;   // T波幅度 (mV)
} ECG_Waveform_t;

// 在R波附近查找Q波和S波
void find_qrs_complex(float *signal, int r_index, 
                     ECG_Waveform_t *waveform, float sampling_rate)
{
    int search_window = (int)(0.08f * sampling_rate);  // 80ms搜索窗口
    
    // 查找Q波 (R波前的最小值)
    float min_value = signal[r_index];
    int q_index = r_index;
    for (int i = r_index - search_window; i < r_index; i++) {
        if (i >= 0 && signal[i] < min_value) {
            min_value = signal[i];
            q_index = i;
        }
    }
    waveform->q_wave_index = q_index;
    
    // 查找S波 (R波后的最小值)
    min_value = signal[r_index];
    int s_index = r_index;
    for (int i = r_index; i < r_index + search_window; i++) {
        if (i < BUFFER_SIZE && signal[i] < min_value) {
            min_value = signal[i];
            s_index = i;
        }
    }
    waveform->s_wave_index = s_index;
    
    // 查找P波 (Q波前的峰值)
    float max_value = signal[q_index];
    int p_index = q_index;
    int p_search_window = (int)(0.2f * sampling_rate);  // 200ms
    for (int i = q_index - p_search_window; i < q_index; i++) {
        if (i >= 0 && signal[i] > max_value) {
            max_value = signal[i];
            p_index = i;
        }
    }
    waveform->p_wave_index = p_index;
    
    // 查找T波 (S波后的峰值)
    max_value = signal[s_index];
    int t_index = s_index;
    int t_search_window = (int)(0.3f * sampling_rate);  // 300ms
    for (int i = s_index; i < s_index + t_search_window; i++) {
        if (i < BUFFER_SIZE && signal[i] > max_value) {
            max_value = signal[i];
            t_index = i;
        }
    }
    waveform->t_wave_index = t_index;
    
    // 计算时间间期
    waveform->pr_interval = (q_index - p_index) * 1000.0f / sampling_rate;
    waveform->qrs_duration = (s_index - q_index) * 1000.0f / sampling_rate;
    waveform->qt_interval = (t_index - q_index) * 1000.0f / sampling_rate;
    
    // 计算幅度
    waveform->r_amplitude = signal[r_index];
    waveform->t_amplitude = signal[t_index];
    
    waveform->r_wave_index = r_index;
}
/* USER CODE END 0 */
```

### 4.4 完整的特征提取流程

```c
/* USER CODE BEGIN 0 */
void extract_ecg_features(float *filtered_signal, int size)
{
    static int peak_indices[100];  // 最多存储100个R波
    ECG_Features_t features;
    ECG_Waveform_t waveform;
    
    // 检测R波
    int peak_count = detect_r_peaks(filtered_signal, size, 
                                    peak_indices, 100);
    
    if (peak_count > 0) {
        // 计算心率
        calculate_heart_rate(peak_indices, peak_count, 500.0f, &features);
        
        // 提取第一个心跳的波形特征
        find_qrs_complex(filtered_signal, peak_indices[0], &waveform, 500.0f);
        
        // 输出结果
        printf("\r\n=== ECG分析结果 ===\r\n");
        printf("检测到 %d 个心跳\r\n", peak_count);
        printf("心率: %.1f bpm\r\n", features.heart_rate);
        printf("平均RR间期: %.1f ms\r\n", features.rr_interval);
        printf("心率变异性: %.1f ms\r\n", features.hrv);
        printf("\r\n波形特征:\r\n");
        printf("PR间期: %.1f ms\r\n", waveform.pr_interval);
        printf("QRS时限: %.1f ms\r\n", waveform.qrs_duration);
        printf("QT间期: %.1f ms\r\n", waveform.qt_interval);
        printf("R波幅度: %.3f V\r\n", waveform.r_amplitude);
        printf("==================\r\n\r\n");
    }
}
/* USER CODE END 0 */
```

**代码说明**：
- 使用Pan-Tompkins算法检测R波
- 计算心率和心率变异性
- 提取完整的ECG波形特征
- 通过串口输出分析结果

## 步骤5：数据可视化和分析

### 5.1 数据传输到PC

**通过串口发送数据**：

```c
/* USER CODE BEGIN 0 */
// 发送原始数据到PC
void send_data_to_pc(uint16_t *data, int size)
{
    // 发送数据包头
    uint8_t header[] = {0xFF, 0xFE, 0xFD, 0xFC};
    HAL_UART_Transmit(&huart2, header, 4, HAL_MAX_DELAY);
    
    // 发送数据长度
    uint16_t length = size;
    HAL_UART_Transmit(&huart2, (uint8_t*)&length, 2, HAL_MAX_DELAY);
    
    // 发送数据
    HAL_UART_Transmit(&huart2, (uint8_t*)data, size * 2, HAL_MAX_DELAY);
    
    // 发送校验和
    uint32_t checksum = 0;
    for (int i = 0; i < size; i++) {
        checksum += data[i];
    }
    HAL_UART_Transmit(&huart2, (uint8_t*)&checksum, 4, HAL_MAX_DELAY);
}

// 发送滤波后的数据 (浮点数)
void send_filtered_data(float *data, int size)
{
    // 转换为16位整数发送 (节省带宽)
    static uint16_t temp_buffer[BUFFER_SIZE];
    
    for (int i = 0; i < size; i++) {
        // 将电压值映射到0-4095范围
        temp_buffer[i] = (uint16_t)((data[i] / 3.3f) * 4095.0f);
    }
    
    send_data_to_pc(temp_buffer, size);
}
/* USER CODE END 0 */
```

### 5.2 Python数据接收和可视化

**创建Python脚本接收和显示数据**：

```python
# ecg_visualizer.py
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import struct

class ECGVisualizer:
    def __init__(self, port='COM3', baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.buffer_size = 1000
        self.data_buffer = np.zeros(self.buffer_size)
        self.time_axis = np.arange(self.buffer_size) / 500.0  # 500 Hz采样率
        
        # 创建图形
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.line1, = self.ax1.plot(self.time_axis, self.data_buffer, 'b-')
        self.line2, = self.ax2.plot(self.time_axis, self.data_buffer, 'r-')
        
        # 设置图形属性
        self.ax1.set_title('原始ECG信号')
        self.ax1.set_xlabel('时间 (秒)')
        self.ax1.set_ylabel('电压 (V)')
        self.ax1.set_ylim(0, 3.3)
        self.ax1.grid(True)
        
        self.ax2.set_title('滤波后ECG信号')
        self.ax2.set_xlabel('时间 (秒)')
        self.ax2.set_ylabel('电压 (V)')
        self.ax2.set_ylim(0, 3.3)
        self.ax2.grid(True)
        
        plt.tight_layout()
    
    def receive_data(self):
        """接收一帧数据"""
        try:
            # 查找数据包头
            header = self.ser.read(4)
            if header != b'\xFF\xFE\xFD\xFC':
                return None
            
            # 读取数据长度
            length_bytes = self.ser.read(2)
            length = struct.unpack('<H', length_bytes)[0]
            
            # 读取数据
            data_bytes = self.ser.read(length * 2)
            data = np.frombuffer(data_bytes, dtype=np.uint16)
            
            # 读取校验和
            checksum_bytes = self.ser.read(4)
            checksum = struct.unpack('<I', checksum_bytes)[0]
            
            # 验证校验和
            if np.sum(data) != checksum:
                print("校验和错误!")
                return None
            
            # 转换为电压值
            voltage = (data / 4095.0) * 3.3
            return voltage
            
        except Exception as e:
            print(f"接收数据错误: {e}")
            return None
    
    def update_plot(self, frame):
        """更新图形"""
        data = self.receive_data()
        if data is not None and len(data) == self.buffer_size:
            self.data_buffer = data
            self.line1.set_ydata(self.data_buffer)
            
            # 应用简单的滤波显示
            filtered = self.apply_filter(self.data_buffer)
            self.line2.set_ydata(filtered)
        
        return self.line1, self.line2
    
    def apply_filter(self, data):
        """应用移动平均滤波"""
        window_size = 5
        filtered = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        return filtered
    
    def start(self):
        """启动可视化"""
        ani = FuncAnimation(self.fig, self.update_plot, 
                          interval=100, blit=True)
        plt.show()
    
    def close(self):
        """关闭串口"""
        self.ser.close()

if __name__ == '__main__':
    # 创建可视化器
    visualizer = ECGVisualizer(port='COM3', baudrate=115200)
    
    try:
        print("ECG可视化启动...")
        print("按Ctrl+C停止")
        visualizer.start()
    except KeyboardInterrupt:
        print("\n停止可视化")
    finally:
        visualizer.close()
```

### 5.3 高级数据分析

**频谱分析**：

```python
# ecg_analysis.py
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class ECGAnalyzer:
    def __init__(self, sampling_rate=500):
        self.fs = sampling_rate
    
    def frequency_analysis(self, ecg_data):
        """频谱分析"""
        # 计算功率谱密度
        frequencies, psd = signal.welch(ecg_data, self.fs, 
                                       nperseg=256)
        
        # 绘制频谱
        plt.figure(figsize=(10, 6))
        plt.semilogy(frequencies, psd)
        plt.xlabel('频率 (Hz)')
        plt.ylabel('功率谱密度 (V²/Hz)')
        plt.title('ECG信号频谱分析')
        plt.grid(True)
        plt.xlim(0, 100)
        plt.show()
        
        return frequencies, psd
    
    def heart_rate_variability(self, rr_intervals):
        """心率变异性分析"""
        # 时域指标
        sdnn = np.std(rr_intervals)  # 标准差
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals)**2))  # 均方根
        
        # 频域指标
        # 重采样到均匀时间间隔
        time = np.cumsum(rr_intervals) / 1000.0  # 转换为秒
        uniform_time = np.arange(0, time[-1], 1.0/4.0)  # 4 Hz重采样
        uniform_rr = np.interp(uniform_time, time, rr_intervals)
        
        # 计算功率谱
        frequencies, psd = signal.welch(uniform_rr, 4.0, nperseg=256)
        
        # 计算频段功率
        vlf_power = np.trapz(psd[(frequencies >= 0.003) & (frequencies < 0.04)])
        lf_power = np.trapz(psd[(frequencies >= 0.04) & (frequencies < 0.15)])
        hf_power = np.trapz(psd[(frequencies >= 0.15) & (frequencies < 0.4)])
        
        results = {
            'SDNN': sdnn,
            'RMSSD': rmssd,
            'VLF_Power': vlf_power,
            'LF_Power': lf_power,
            'HF_Power': hf_power,
            'LF_HF_Ratio': lf_power / hf_power if hf_power > 0 else 0
        }
        
        return results
    
    def detect_arrhythmia(self, rr_intervals):
        """简单的心律失常检测"""
        mean_rr = np.mean(rr_intervals)
        std_rr = np.std(rr_intervals)
        
        # 检测异常心跳
        abnormal_beats = []
        for i, rr in enumerate(rr_intervals):
            # 如果RR间期偏离平均值超过2个标准差
            if abs(rr - mean_rr) > 2 * std_rr:
                abnormal_beats.append(i)
        
        # 检测心动过速 (心率 > 100 bpm)
        tachycardia = mean_rr < 600  # 600ms对应100bpm
        
        # 检测心动过缓 (心率 < 60 bpm)
        bradycardia = mean_rr > 1000  # 1000ms对应60bpm
        
        results = {
            'abnormal_beats': abnormal_beats,
            'abnormal_count': len(abnormal_beats),
            'tachycardia': tachycardia,
            'bradycardia': bradycardia
        }
        
        return results
    
    def generate_report(self, ecg_data, rr_intervals):
        """生成分析报告"""
        print("\n" + "="*50)
        print("ECG信号分析报告")
        print("="*50)
        
        # 基本统计
        print(f"\n信号统计:")
        print(f"  采样点数: {len(ecg_data)}")
        print(f"  信号时长: {len(ecg_data)/self.fs:.2f} 秒")
        print(f"  平均值: {np.mean(ecg_data):.3f} V")
        print(f"  标准差: {np.std(ecg_data):.3f} V")
        
        # 心率分析
        mean_hr = 60000.0 / np.mean(rr_intervals)
        print(f"\n心率分析:")
        print(f"  平均心率: {mean_hr:.1f} bpm")
        print(f"  最小心率: {60000.0/np.max(rr_intervals):.1f} bpm")
        print(f"  最大心率: {60000.0/np.min(rr_intervals):.1f} bpm")
        
        # HRV分析
        hrv_results = self.heart_rate_variability(rr_intervals)
        print(f"\n心率变异性:")
        print(f"  SDNN: {hrv_results['SDNN']:.2f} ms")
        print(f"  RMSSD: {hrv_results['RMSSD']:.2f} ms")
        print(f"  LF/HF比值: {hrv_results['LF_HF_Ratio']:.2f}")
        
        # 心律失常检测
        arrhythmia = self.detect_arrhythmia(rr_intervals)
        print(f"\n心律失常检测:")
        print(f"  异常心跳数: {arrhythmia['abnormal_count']}")
        print(f"  心动过速: {'是' if arrhythmia['tachycardia'] else '否'}")
        print(f"  心动过缓: {'是' if arrhythmia['bradycardia'] else '否'}")
        
        print("\n" + "="*50 + "\n")

# 使用示例
if __name__ == '__main__':
    # 加载数据
    ecg_data = np.load('ecg_data.npy')
    rr_intervals = np.load('rr_intervals.npy')
    
    # 创建分析器
    analyzer = ECGAnalyzer(sampling_rate=500)
    
    # 频谱分析
    analyzer.frequency_analysis(ecg_data)
    
    # 生成报告
    analyzer.generate_report(ecg_data, rr_intervals)
```

### 5.4 数据存储

**保存数据到文件**：

```python
# data_logger.py
import numpy as np
import datetime
import json

class ECGDataLogger:
    def __init__(self, base_path='./ecg_data'):
        self.base_path = base_path
        self.session_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def save_raw_data(self, data, metadata=None):
        """保存原始数据"""
        filename = f"{self.base_path}/raw_{self.session_id}.npy"
        np.save(filename, data)
        
        # 保存元数据
        if metadata:
            meta_filename = f"{self.base_path}/meta_{self.session_id}.json"
            with open(meta_filename, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        print(f"数据已保存: {filename}")
    
    def save_features(self, features):
        """保存特征数据"""
        filename = f"{self.base_path}/features_{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(features, f, indent=2)
        
        print(f"特征已保存: {filename}")
    
    def load_session(self, session_id):
        """加载会话数据"""
        raw_file = f"{self.base_path}/raw_{session_id}.npy"
        meta_file = f"{self.base_path}/meta_{session_id}.json"
        
        data = np.load(raw_file)
        
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        return data, metadata
```

## 步骤6：系统集成和测试

### 6.1 完整系统代码

**main.c完整实现**：

```c
/* Includes */
#include "main.h"
#include <stdio.h>
#include <math.h>

/* Private defines */
#define BUFFER_SIZE 1000
#define SAMPLING_RATE 500.0f

/* Private variables */
uint16_t adc_buffer[BUFFER_SIZE];
volatile uint8_t buffer_full = 0;

/* Function prototypes */
void SystemClock_Config(void);
void process_ecg_data(uint16_t *raw_data, int size);
void send_data_to_pc(uint16_t *data, int size);

int main(void)
{
    /* MCU Configuration */
    HAL_Init();
    SystemClock_Config();
    
    /* Initialize peripherals */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_ADC1_Init();
    MX_TIM2_Init();
    MX_USART2_UART_Init();
    
    /* Start ADC with DMA */
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUFFER_SIZE);
    
    /* Start Timer */
    HAL_TIM_Base_Start(&htim2);
    
    printf("\r\n=================================\r\n");
    printf("ECG信号采集与处理系统\r\n");
    printf("=================================\r\n");
    printf("采样率: %.0f Hz\r\n", SAMPLING_RATE);
    printf("缓冲区大小: %d 样本\r\n", BUFFER_SIZE);
    printf("系统就绪，开始采集...\r\n");
    printf("=================================\r\n\r\n");
    
    /* Infinite loop */
    while (1)
    {
        if (buffer_full) {
            buffer_full = 0;
            
            // 处理ECG数据
            process_ecg_data(adc_buffer, BUFFER_SIZE);
            
            // 发送数据到PC
            send_data_to_pc(adc_buffer, BUFFER_SIZE);
        }
        
        HAL_Delay(10);
    }
}

/* DMA transfer complete callback */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
    if (hadc->Instance == ADC1) {
        buffer_full = 1;
    }
}

/* Printf redirection */
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart2, (uint8_t*)ptr, len, HAL_MAX_DELAY);
    return len;
}
```

### 6.2 性能优化

**优化内存使用**：

```c
/* USER CODE BEGIN 0 */
// 使用静态内存避免频繁分配
static float temp_buffer1[BUFFER_SIZE];
static float temp_buffer2[BUFFER_SIZE];
static float filtered_data[BUFFER_SIZE];
static int peak_indices[100];

// 使用定点数代替浮点数（可选，提高性能）
typedef int32_t fixed_point_t;
#define FIXED_POINT_SHIFT 16
#define FLOAT_TO_FIXED(x) ((fixed_point_t)((x) * (1 << FIXED_POINT_SHIFT)))
#define FIXED_TO_FLOAT(x) ((float)(x) / (1 << FIXED_POINT_SHIFT))

// 定点数乘法
fixed_point_t fixed_multiply(fixed_point_t a, fixed_point_t b)
{
    return (fixed_point_t)(((int64_t)a * b) >> FIXED_POINT_SHIFT);
}
/* USER CODE END 0 */
```

**优化滤波器性能**：

```c
/* USER CODE BEGIN 0 */
// 使用查找表加速三角函数计算
#define LUT_SIZE 256
static float sin_lut[LUT_SIZE];
static float cos_lut[LUT_SIZE];

void init_trig_lut(void)
{
    for (int i = 0; i < LUT_SIZE; i++) {
        float angle = 2.0f * M_PI * i / LUT_SIZE;
        sin_lut[i] = sinf(angle);
        cos_lut[i] = cosf(angle);
    }
}

// 快速三角函数
float fast_sin(float angle)
{
    int index = (int)(angle * LUT_SIZE / (2.0f * M_PI)) % LUT_SIZE;
    return sin_lut[index];
}
/* USER CODE END 0 */
```

### 6.3 功能测试

**测试清单**：

1. **硬件测试**：
   - [ ] 电源电压正常（3.3V ± 0.1V）
   - [ ] ADC采样正常
   - [ ] 串口通信正常
   - [ ] 电极连接良好

2. **信号质量测试**：
   - [ ] 基线稳定，无明显漂移
   - [ ] QRS波群清晰可见
   - [ ] P波和T波可识别
   - [ ] 噪声水平可接受（< 10 mV）

3. **算法测试**：
   - [ ] R波检测准确率 > 95%
   - [ ] 心率计算误差 < 5 bpm
   - [ ] 滤波效果良好
   - [ ] 特征提取正确

4. **性能测试**：
   - [ ] CPU占用率 < 50%
   - [ ] 内存使用合理
   - [ ] 实时处理无延迟
   - [ ] 长时间运行稳定

### 6.4 故障排除

**常见问题和解决方法**：

**问题1：无法检测到ECG信号**

**可能原因**：
- 电极连接不良
- 电极位置不正确
- 电路连接错误
- AD8232模块损坏

**解决方法**：
1. 检查电极是否贴紧皮肤
2. 清洁皮肤，去除油脂
3. 验证电极位置是否正确
4. 用示波器检查AD8232输出
5. 检查电源和地线连接

**问题2：信号噪声过大**

**可能原因**：
- 工频干扰（50/60 Hz）
- 肌电干扰
- 电极接触不良
- 接地不良

**解决方法**：
1. 启用陷波滤波器
2. 保持身体放松，减少肌肉紧张
3. 更换电极或重新贴附
4. 改善接地连接
5. 远离电源线和电器

**问题3：R波检测不准确**

**可能原因**：
- 阈值设置不当
- 信号质量差
- 算法参数不合适

**解决方法**：
1. 调整检测阈值
2. 改善信号质量
3. 调整滤波器参数
4. 增加信号预处理步骤

**问题4：心率计算错误**

**可能原因**：
- R波漏检或误检
- RR间期计算错误
- 采样率设置错误

**解决方法**：
1. 改进R波检测算法
2. 验证采样率设置
3. 检查时间计算公式
4. 使用中值滤波去除异常值

**问题5：数据传输丢失**

**可能原因**：
- 串口波特率不匹配
- 缓冲区溢出
- 数据包格式错误

**解决方法**：
1. 确认波特率设置一致
2. 增加缓冲区大小
3. 添加流控制
4. 验证数据包格式和校验和

## 扩展功能

### 7.1 EEG信号处理

**EEG信号采集的特殊要求**：

```c
/* EEG特定配置 */
#define EEG_SAMPLING_RATE 250.0f  // EEG通常使用较低采样率
#define EEG_CHANNELS 8            // 多通道EEG

// EEG频段滤波器
typedef struct {
    float delta[BUFFER_SIZE];  // 0.5-4 Hz
    float theta[BUFFER_SIZE];  // 4-8 Hz
    float alpha[BUFFER_SIZE];  // 8-13 Hz
    float beta[BUFFER_SIZE];   // 13-30 Hz
    float gamma[BUFFER_SIZE];  // 30-100 Hz
} EEG_Bands_t;

// 带通滤波器提取特定频段
void extract_eeg_bands(float *signal, int size, EEG_Bands_t *bands)
{
    // 使用IIR带通滤波器提取各频段
    // Delta波段 (0.5-4 Hz)
    apply_bandpass_filter(signal, bands->delta, size, 0.5f, 4.0f);
    
    // Theta波段 (4-8 Hz)
    apply_bandpass_filter(signal, bands->theta, size, 4.0f, 8.0f);
    
    // Alpha波段 (8-13 Hz)
    apply_bandpass_filter(signal, bands->alpha, size, 8.0f, 13.0f);
    
    // Beta波段 (13-30 Hz)
    apply_bandpass_filter(signal, bands->beta, size, 13.0f, 30.0f);
    
    // Gamma波段 (30-100 Hz)
    apply_bandpass_filter(signal, bands->gamma, size, 30.0f, 100.0f);
}

// 计算频段功率
float calculate_band_power(float *band_signal, int size)
{
    float power = 0;
    for (int i = 0; i < size; i++) {
        power += band_signal[i] * band_signal[i];
    }
    return power / size;
}
```

### 7.2 实时心率监测

**实现心率趋势监测**：

```c
/* 心率趋势监测 */
#define HR_HISTORY_SIZE 60  // 保存60秒历史

typedef struct {
    float hr_history[HR_HISTORY_SIZE];
    int history_index;
    float hr_trend;  // 心率趋势 (bpm/min)
    uint8_t alert_flag;
} HR_Monitor_t;

void HR_Monitor_Init(HR_Monitor_t *monitor)
{
    memset(monitor->hr_history, 0, sizeof(monitor->hr_history));
    monitor->history_index = 0;
    monitor->hr_trend = 0;
    monitor->alert_flag = 0;
}

void HR_Monitor_Update(HR_Monitor_t *monitor, float current_hr)
{
    // 更新历史记录
    monitor->hr_history[monitor->history_index] = current_hr;
    monitor->history_index = (monitor->history_index + 1) % HR_HISTORY_SIZE;
    
    // 计算趋势 (线性回归)
    float sum_x = 0, sum_y = 0, sum_xy = 0, sum_xx = 0;
    int n = HR_HISTORY_SIZE;
    
    for (int i = 0; i < n; i++) {
        float x = i;
        float y = monitor->hr_history[i];
        sum_x += x;
        sum_y += y;
        sum_xy += x * y;
        sum_xx += x * x;
    }
    
    // 斜率 = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    monitor->hr_trend = (n * sum_xy - sum_x * sum_y) / 
                       (n * sum_xx - sum_x * sum_x);
    
    // 检查异常
    if (current_hr > 120 || current_hr < 50) {
        monitor->alert_flag = 1;
        printf("警告: 心率异常 (%.1f bpm)\r\n", current_hr);
    } else {
        monitor->alert_flag = 0;
    }
}
```

### 7.3 多导联ECG

**12导联ECG系统**：

```c
/* 12导联ECG配置 */
#define ECG_LEADS 12

typedef enum {
    LEAD_I = 0,    // I导联: LA - RA
    LEAD_II,       // II导联: LL - RA
    LEAD_III,      // III导联: LL - LA
    LEAD_aVR,      // aVR: RA - (LA+LL)/2
    LEAD_aVL,      // aVL: LA - (RA+LL)/2
    LEAD_aVF,      // aVF: LL - (RA+LA)/2
    LEAD_V1,       // V1: 胸导联1
    LEAD_V2,       // V2: 胸导联2
    LEAD_V3,       // V3: 胸导联3
    LEAD_V4,       // V4: 胸导联4
    LEAD_V5,       // V5: 胸导联5
    LEAD_V6        // V6: 胸导联6
} ECG_Lead_t;

typedef struct {
    float ra;  // 右臂
    float la;  // 左臂
    float ll;  // 左腿
    float v1;  // 胸导联1
    float v2;  // 胸导联2
    float v3;  // 胸导联3
    float v4;  // 胸导联4
    float v5;  // 胸导联5
    float v6;  // 胸导联6
} ECG_Electrodes_t;

// 计算12导联信号
void calculate_12_leads(ECG_Electrodes_t *electrodes, float *leads)
{
    // 肢体导联
    leads[LEAD_I] = electrodes->la - electrodes->ra;
    leads[LEAD_II] = electrodes->ll - electrodes->ra;
    leads[LEAD_III] = electrodes->ll - electrodes->la;
    
    // 加压肢体导联
    float wct = (electrodes->ra + electrodes->la + electrodes->ll) / 3.0f;
    leads[LEAD_aVR] = electrodes->ra - wct;
    leads[LEAD_aVL] = electrodes->la - wct;
    leads[LEAD_aVF] = electrodes->ll - wct;
    
    // 胸导联
    leads[LEAD_V1] = electrodes->v1 - wct;
    leads[LEAD_V2] = electrodes->v2 - wct;
    leads[LEAD_V3] = electrodes->v3 - wct;
    leads[LEAD_V4] = electrodes->v4 - wct;
    leads[LEAD_V5] = electrodes->v5 - wct;
    leads[LEAD_V6] = electrodes->v6 - wct;
}
```

### 7.4 云端数据上传

**通过WiFi上传数据到云端**：

```c
/* WiFi模块配置 (ESP8266) */
#define WIFI_SSID "YourWiFi"
#define WIFI_PASSWORD "YourPassword"
#define SERVER_URL "http://your-server.com/api/ecg"

// 初始化WiFi连接
void WiFi_Init(void)
{
    // 发送AT命令配置ESP8266
    HAL_UART_Transmit(&huart3, "AT+CWMODE=1\r\n", 13, 1000);
    HAL_Delay(1000);
    
    char cmd[100];
    sprintf(cmd, "AT+CWJAP=\"%s\",\"%s\"\r\n", WIFI_SSID, WIFI_PASSWORD);
    HAL_UART_Transmit(&huart3, (uint8_t*)cmd, strlen(cmd), 1000);
    HAL_Delay(5000);
}

// 上传ECG数据
void upload_ecg_data(ECG_Features_t *features)
{
    char json_data[256];
    sprintf(json_data, 
            "{\"heart_rate\":%.1f,\"rr_interval\":%.1f,\"hrv\":%.1f}",
            features->heart_rate, 
            features->rr_interval, 
            features->hrv);
    
    // 构建HTTP POST请求
    char http_request[512];
    sprintf(http_request,
            "POST /api/ecg HTTP/1.1\r\n"
            "Host: your-server.com\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: %d\r\n"
            "\r\n"
            "%s",
            strlen(json_data), json_data);
    
    // 发送数据
    HAL_UART_Transmit(&huart3, (uint8_t*)http_request, 
                     strlen(http_request), 5000);
}
```

### 7.5 移动应用集成

**蓝牙BLE数据传输**：

```c
/* BLE配置 (HM-10模块) */
#define BLE_SERVICE_UUID "FFE0"
#define BLE_CHAR_UUID "FFE1"

// 初始化BLE模块
void BLE_Init(void)
{
    // 设置设备名称
    HAL_UART_Transmit(&huart3, "AT+NAME=ECG_Monitor\r\n", 20, 1000);
    HAL_Delay(500);
    
    // 设置为从机模式
    HAL_UART_Transmit(&huart3, "AT+ROLE=0\r\n", 11, 1000);
    HAL_Delay(500);
}

// 通过BLE发送心率数据
void BLE_Send_HeartRate(float heart_rate)
{
    uint8_t hr_data[2];
    hr_data[0] = 0x00;  // 标志位
    hr_data[1] = (uint8_t)heart_rate;  // 心率值
    
    HAL_UART_Transmit(&huart3, hr_data, 2, 100);
}
```

## 总结

通过本教程，你已经学习了：

- ✅ 生物信号的基本特征和生理学原理
- ✅ ECG和EEG信号的采集方法
- ✅ 模拟前端电路的设计和实现
- ✅ ADC配置和高效数据采集
- ✅ 数字滤波算法的原理和实现
- ✅ R波检测和特征提取算法
- ✅ 心率和心率变异性的计算
- ✅ 数据可视化和分析方法
- ✅ 完整系统的集成和测试

**关键要点**：

1. **信号质量是关键**：良好的电极接触和适当的滤波是获得高质量信号的基础
2. **算法选择要合理**：根据实际需求选择合适的滤波器和检测算法
3. **实时性能很重要**：优化代码以满足实时处理要求
4. **安全性不可忽视**：医疗设备必须符合安全标准和法规要求
5. **测试验证要充分**：使用标准数据库验证算法性能

**实际应用场景**：

- 便携式心电监护仪
- 运动健康监测设备
- 睡眠质量分析系统
- 远程医疗监护平台
- 脑机接口研究
- 情绪识别系统

## 进阶挑战

尝试以下挑战来巩固和扩展你的技能：

1. **挑战1：实现实时心律失常检测**
   - 检测房颤、室颤等常见心律失常
   - 实现自动报警功能
   - 提示：研究MIT-BIH心律失常数据库

2. **挑战2：开发多通道EEG采集系统**
   - 实现8通道或16通道EEG采集
   - 实现频段功率分析
   - 提示：使用ADS1299芯片

3. **挑战3：实现自适应滤波器**
   - 使用LMS或RLS算法
   - 自动调整滤波器参数
   - 提示：研究自适应信号处理理论

4. **挑战4：开发移动端应用**
   - 通过蓝牙连接设备
   - 实时显示ECG波形
   - 提示：使用React Native或Flutter

5. **挑战5：实现机器学习分类**
   - 使用深度学习进行心律失常分类
   - 训练CNN或LSTM模型
   - 提示：使用TensorFlow Lite for Microcontrollers

## 完整代码

完整的项目代码可以在GitHub上获取：

- **STM32代码**：[github.com/embedded-platform/ecg-signal-processing](https://github.com/embedded-platform/ecg-signal-processing)
- **Python分析工具**：[github.com/embedded-platform/ecg-analyzer](https://github.com/embedded-platform/ecg-analyzer)
- **测试数据**：[physionet.org/content/mitdb/](https://physionet.org/content/mitdb/)

## 下一步学习

建议继续学习以下内容：

- [医疗数据安全与隐私](../intermediate/01-medical-data-security.html) - 了解医疗数据的安全保护
- [便携式医疗设备开发](../advanced/01-portable-medical-device.html) - 开发完整的医疗设备产品
- [嵌入式机器学习](../../10-cross-cutting-concerns/05-embedded-ml/) - 在嵌入式设备上运行AI模型
- [低功耗设计](../../10-cross-cutting-concerns/02-power-management/) - 优化便携设备的功耗

## 参考资料

### 标准和指南

1. **IEC 60601-2-27** - 心电监护设备的特殊要求
2. **IEC 60601-2-26** - 脑电图设备的特殊要求
3. **ANSI/AAMI EC11** - 诊断心电图设备标准
4. **ANSI/AAMI EC13** - 心电监护仪标准

### 学术资源

1. **Pan J, Tompkins WJ.** "A Real-Time QRS Detection Algorithm." IEEE Trans Biomed Eng. 1985.
2. **Hamilton PS, Tompkins WJ.** "Quantitative Investigation of QRS Detection Rules Using the MIT/BIH Arrhythmia Database." IEEE Trans Biomed Eng. 1986.
3. **Task Force of ESC and NASPE.** "Heart Rate Variability: Standards of Measurement." Circulation. 1996.

### 在线资源

1. [PhysioNet](https://physionet.org/) - 生理信号数据库和工具
2. [MIT-BIH数据库](https://physionet.org/content/mitdb/) - 标准ECG数据库
3. [BioSPPy](https://github.com/PIA-Group/BioSPPy) - Python生物信号处理库
4. [NeuroKit2](https://neuropsychology.github.io/NeuroKit/) - 神经生理信号处理工具

### 书籍推荐

1. **《生物医学信号处理》** - 张元亭著
2. **《心电图学》** - 郭继鸿著
3. **"Biomedical Signal Processing and Signal Modeling"** - Eugene N. Bruce
4. **"Digital Signal Processing in Modern Communication Systems"** - Andreas Schwarzinger

### 开发工具

1. **MATLAB Signal Processing Toolbox** - 信号处理工具箱
2. **Python SciPy** - 科学计算库
3. **GNU Octave** - 开源MATLAB替代品
4. **Sigview** - 信号分析软件

---

**练习题**：

1. 解释ECG信号中P波、QRS波群和T波分别代表什么生理过程？
2. 为什么生物信号采集需要高共模抑制比（CMRR）？如何实现？
3. 比较IIR滤波器和FIR滤波器在生物信号处理中的优缺点。
4. Pan-Tompkins算法的核心步骤是什么？为什么要进行微分和平方运算？
5. 心率变异性（HRV）有什么临床意义？如何计算时域和频域HRV指标？

**实验任务**：

1. 使用MIT-BIH数据库测试你的R波检测算法，计算检测准确率
2. 实现一个自适应阈值算法，能够适应不同幅度的ECG信号
3. 比较不同滤波器（移动平均、IIR、FIR）对ECG信号的滤波效果
4. 实现一个简单的心律失常检测算法，能够识别心动过速和心动过缓
5. 开发一个Python GUI应用，实时显示ECG波形和心率

---

**反馈与支持**：

如果你在学习过程中遇到问题或有任何建议，欢迎：
- 在评论区留言讨论
- 提交GitHub Issue
- 加入我们的技术社区
- 联系作者获取帮助

**免责声明**：本教程仅用于教育和学习目的。开发实际的医疗设备需要遵守相关法规和标准，并获得必要的认证。请勿将本教程中的设备用于临床诊断或治疗。
