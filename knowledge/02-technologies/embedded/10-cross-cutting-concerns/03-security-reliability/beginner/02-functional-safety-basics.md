---
title: "功能安全基础(IEC 61508)"
description: "深入介绍功能安全的核心概念和IEC 61508标准，包括安全完整性等级、安全生命周期、风险评估方法和功能安全管理，为开发安全关键系统奠定基础"
slug: "functional-safety-basics"

# 分类信息
domain: "横切关注点"
module: "安全性与可靠性"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 功能安全
  - IEC 61508
  - 安全标准
  - SIL等级
  - 安全生命周期
prerequisites:
  - "embedded-security-overview"
related_contents: []

# 学习信息
estimated_time: 55
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
  - 功能安全
  - IEC 61508
  - 安全完整性等级
  - SIL
  - 安全生命周期
  - 风险评估
  - 功能安全管理
  - 安全关键系统
cover_image: ""
---

# 功能安全基础(IEC 61508)


## 概述

功能安全(Functional Safety)是指通过正确实现安全功能来避免或控制系统性故障和随机硬件故障，从而使系统在可接受的风险水平下运行。IEC 61508是功能安全领域最重要的国际标准，被广泛应用于工业控制、交通运输、医疗设备等安全关键领域。完成本文学习后，你将能够：

- 理解功能安全的基本概念和重要性
- 掌握IEC 61508标准的核心内容
- 了解安全完整性等级(SIL)的划分和应用
- 熟悉功能安全生命周期的各个阶段
- 掌握基本的风险评估方法
- 了解功能安全管理的要求

## 背景知识

### 什么是功能安全？

功能安全关注的是系统在故障情况下的安全性，而不是系统的正常功能。

**核心概念**：

**1. 安全(Safety) vs 可靠性(Reliability)**
- **可靠性**：系统正常工作的能力
- **安全性**：系统在故障时不造成危害的能力
- 高可靠性不等于高安全性

**2. 功能安全 vs 信息安全**
- **功能安全**：防止系统故障导致的危害
- **信息安全**：防止恶意攻击导致的危害
- 两者相互关联，需要综合考虑

**3. 安全功能(Safety Function)**
- 用于降低风险的功能
- 检测危险状态
- 将系统置于安全状态
- 维持安全状态

### 为什么需要功能安全？

**历史教训**：

1. **Therac-25事故(1985-1987)**
   - 医疗放射治疗设备
   - 软件缺陷导致过量辐射
   - 至少6人死亡或严重受伤
   - 教训：软件也需要功能安全

2. **阿丽亚娜5号火箭爆炸(1996)**
   - 软件异常导致火箭偏离轨道
   - 损失约5亿美元
   - 教训：软件复用需要安全评估

3. **丰田汽车召回事件(2009-2010)**
   - 电子油门控制系统故障
   - 导致意外加速
   - 召回数百万辆汽车
   - 教训：电子系统需要功能安全设计

**应用领域**：
- 工业过程控制
- 铁路信号系统
- 汽车电子系统
- 医疗设备
- 航空航天
- 核电站控制

### 前置知识要求

本文假设你已经掌握：
- 嵌入式系统基础知识
- 系统安全概述
- 基本的风险管理概念


## 核心内容

### 1. IEC 61508标准概述

#### 1.1 标准结构

IEC 61508《电气/电子/可编程电子安全相关系统的功能安全》由7个部分组成：

**Part 1: 总体要求**
- 功能安全的基本概念
- 安全生命周期
- 管理要求

**Part 2: 电气/电子/可编程电子安全相关系统的要求**
- 硬件安全要求
- 硬件架构约束
- 硬件故障分析

**Part 3: 软件要求**
- 软件安全要求
- 软件开发流程
- 软件验证和确认

**Part 4: 定义和缩略语**
- 术语定义
- 标准化术语

**Part 5: 确定安全完整性等级的方法示例**
- 风险评估方法
- SIL确定方法

**Part 6: Part 2和Part 3的应用指南**
- 实施指导
- 最佳实践

**Part 7: 技术和措施概述**
- 技术措施汇总
- 选择指导

#### 1.2 核心概念

**E/E/PE系统**
- **E**: Electrical (电气)
- **E**: Electronic (电子)
- **PE**: Programmable Electronic (可编程电子)

**安全相关系统(Safety-Related System)**
- 实现安全功能的系统
- 包括传感器、逻辑处理、执行器
- 故障可能导致危险

**安全功能(Safety Function)**
- 用于实现或维持安全状态的功能
- 必须在规定时间内响应
- 必须达到规定的可靠性

**安全完整性(Safety Integrity)**
- 安全功能在所有规定条件下正确执行的概率
- 包括硬件安全完整性和系统安全完整性

#### 1.3 标准适用范围

**适用于**：
- 工业过程控制
- 机械安全
- 电力系统
- 医疗设备
- 通用安全系统

**不直接适用但可参考**：
- 汽车（有ISO 26262）
- 铁路（有EN 50128）
- 航空（有DO-178C）
- 核电（有IEC 61513）

### 2. 安全完整性等级(SIL)

#### 2.1 SIL等级定义

安全完整性等级(Safety Integrity Level, SIL)是衡量安全功能可靠性的指标。

**SIL等级划分**：

| SIL等级 | 低要求模式(PFD) | 高要求/连续模式(PFH) | 风险降低因子 |
|---------|----------------|---------------------|-------------|
| SIL 4 | 10⁻⁵ ≤ PFD < 10⁻⁴ | 10⁻⁹ ≤ PFH < 10⁻⁸ | 10,000 - 100,000 |
| SIL 3 | 10⁻⁴ ≤ PFD < 10⁻³ | 10⁻⁸ ≤ PFH < 10⁻⁷ | 1,000 - 10,000 |
| SIL 2 | 10⁻³ ≤ PFD < 10⁻² | 10⁻⁷ ≤ PFH < 10⁻⁶ | 100 - 1,000 |
| SIL 1 | 10⁻² ≤ PFD < 10⁻¹ | 10⁻⁶ ≤ PFH < 10⁻⁵ | 10 - 100 |

**术语解释**：
- **PFD** (Probability of Failure on Demand): 按需失效概率
- **PFH** (Probability of dangerous Failure per Hour): 每小时危险失效概率

**操作模式**：

1. **低要求模式(Low Demand Mode)**
   - 安全功能不经常被要求
   - 每年要求次数 < 1次
   - 例如：紧急停机系统

2. **高要求/连续模式(High Demand/Continuous Mode)**
   - 安全功能经常被要求
   - 每年要求次数 > 1次
   - 例如：防抱死制动系统(ABS)

#### 2.2 SIL等级确定

确定SIL等级需要进行风险评估。

**方法1：风险图(Risk Graph)**

```
风险参数：
- C: 后果严重程度(Consequence)
- F: 暴露频率(Frequency of exposure)
- P: 避免可能性(Possibility of avoidance)
- W: 无保护时的风险(Risk without protection)

风险图示例：
        C1(轻伤)  C2(重伤)  C3(死亡)  C4(多人死亡)
F1(罕见)    -        SIL1     SIL2      SIL3
F2(频繁)   SIL1      SIL2     SIL3      SIL4
```

**方法2：风险矩阵(Risk Matrix)**

基于严重程度和发生概率确定风险等级。

```
严重程度 vs 发生概率矩阵：

           可忽略  边缘  严重  灾难
几乎确定    低     中    高    极高
很可能      低     中    高    极高
可能        低     中    中    高
不太可能    低     低    中    中
罕见        低     低    低    中

风险等级对应SIL：
- 极高风险 → SIL 3/4
- 高风险 → SIL 2/3
- 中风险 → SIL 1/2
- 低风险 → 无需SIL或SIL 1
```

**方法3：定量风险评估**

计算可容忍风险率，确定所需的风险降低。

```
步骤：
1. 确定无保护时的风险率(R₀)
2. 确定可容忍风险率(R_tolerable)
3. 计算所需风险降低因子: RRF = R₀ / R_tolerable
4. 根据RRF确定SIL等级
```

#### 2.3 SIL等级应用示例

**示例1：工业压力容器保护系统**
- **后果**: 爆炸可能导致多人死亡(C4)
- **暴露频率**: 工人经常在附近工作(F2)
- **避免可能性**: 爆炸发生突然，难以避免(P2)
- **确定SIL**: SIL 3

**示例2：电梯门安全系统**
- **后果**: 可能导致重伤(C2)
- **暴露频率**: 每天多次使用(F2)
- **避免可能性**: 用户可能注意到并避免(P1)
- **确定SIL**: SIL 2

**示例3：家用燃气灶熄火保护**
- **后果**: 可能导致火灾或中毒(C2)
- **暴露频率**: 每天使用(F2)
- **避免可能性**: 用户可能闻到气味(P1)
- **确定SIL**: SIL 1


### 3. 功能安全生命周期

#### 3.1 生命周期概述

IEC 61508定义了完整的安全生命周期，确保从概念到退役的每个阶段都考虑安全。

**V模型生命周期**：

```
概念 → 总体范围定义 → 危害和风险分析 → 总体安全要求
                                              ↓
                                        安全要求分配
                                              ↓
                    ┌─────────────────────────┴─────────────────────────┐
                    ↓                                                   ↓
            E/E/PE系统设计                                        其他技术设计
                    ↓                                                   ↓
            硬件设计 + 软件设计                                    实施
                    ↓                                                   ↓
            硬件实现 + 软件实现                                    集成
                    ↓                                                   ↓
            硬件集成 + 软件集成                                    验证
                    ↓                                                   ↓
            E/E/PE系统集成 ←─────────────────────────────────────┘
                    ↓
            总体安全确认
                    ↓
            安装和调试
                    ↓
            运行和维护
                    ↓
            修改和改造
                    ↓
            退役或处置
```

#### 3.2 主要阶段详解

**阶段1：概念(Concept)**
- 定义系统用途和边界
- 识别利益相关方
- 初步风险评估

**阶段2：总体范围定义(Overall Scope Definition)**
- 定义系统功能
- 确定操作模式
- 识别环境条件

**阶段3：危害和风险分析(Hazard and Risk Analysis)**
- 识别所有危害
- 评估风险等级
- 确定安全功能

**阶段4：总体安全要求(Overall Safety Requirements)**
- 定义安全功能要求
- 确定SIL等级
- 分配安全要求

**阶段5：安全要求分配(Safety Requirements Allocation)**
- 将要求分配到子系统
- E/E/PE系统要求
- 其他技术要求

**阶段6：设计和开发(Design and Development)**
- 硬件设计和实现
- 软件设计和实现
- 遵循SIL等级要求

**阶段7：集成和测试(Integration and Testing)**
- 单元测试
- 集成测试
- 系统测试

**阶段8：安全确认(Safety Validation)**
- 验证安全要求
- 确认SIL等级
- 第三方评估

**阶段9：运行和维护(Operation and Maintenance)**
- 定期检查和测试
- 故障记录和分析
- 预防性维护

**阶段10：修改和改造(Modification and Retrofit)**
- 变更管理
- 影响分析
- 重新评估

**阶段11：退役(Decommissioning)**
- 安全停用
- 数据保存
- 经验总结

#### 3.3 文档要求

每个阶段都需要产生相应的文档：

**规划文档**：
- 功能安全计划
- 质量保证计划
- 验证和确认计划

**分析文档**：
- 危害和风险分析报告
- 安全要求规格说明
- 安全分析报告

**设计文档**：
- 系统架构设计
- 硬件设计规格
- 软件设计规格

**验证文档**：
- 测试计划和报告
- 验证报告
- 确认报告

**管理文档**：
- 配置管理记录
- 变更管理记录
- 审计记录

### 4. 硬件安全要求

#### 4.1 硬件架构约束

根据SIL等级，IEC 61508对硬件架构有不同要求。

**架构约束表**：

| SIL等级 | 类型A系统 | 类型B系统 |
|---------|----------|----------|
| SIL 4 | 不允许 | HFT ≥ 1 |
| SIL 3 | HFT ≥ 1 | HFT ≥ 1 |
| SIL 2 | HFT ≥ 0 | HFT ≥ 1 |
| SIL 1 | HFT ≥ 0 | HFT ≥ 0 |

**术语解释**：
- **类型A系统**: 所有故障模式都是明确定义的
- **类型B系统**: 至少有一个故障模式不能明确定义
- **HFT** (Hardware Fault Tolerance): 硬件故障容错度

**HFT示例**：
- **HFT = 0**: 单通道，无冗余
- **HFT = 1**: 双通道，1oo2(2取1)或2oo2(2取2)
- **HFT = 2**: 三通道，2oo3(3取2)

#### 4.2 安全失效分数(SFF)

安全失效分数(Safe Failure Fraction)衡量安全失效的比例。

**SFF计算公式**：

```
SFF = (λS + λDD) / (λS + λDD + λDU)

其中：
λS  : 安全失效率
λDD : 检测到的危险失效率
λDU : 未检测到的危险失效率
```

**SFF要求**：

| SIL等级 | HFT=0 | HFT=1 | HFT=2 |
|---------|-------|-------|-------|
| SIL 4 | - | ≥99% | ≥90% |
| SIL 3 | ≥99% | ≥90% | ≥60% |
| SIL 2 | ≥90% | ≥60% | ≥60% |
| SIL 1 | ≥60% | ≥60% | ≥60% |

#### 4.3 硬件设计技术

**避免故障的技术**：
- 使用成熟的组件
- 降额设计(Derating)
- 环境应力筛选
- 设计审查

**控制故障的技术**：
- 冗余设计
- 多样性设计
- 故障检测
- 诊断覆盖

**故障检测方法**：
- 双通道比较
- 看门狗定时器
- 内存测试(RAM/ROM)
- 时钟监控
- 电源监控
- 温度监控

#### 4.4 随机硬件失效分析

**失效率数据来源**：
- 组件制造商数据
- 失效率数据库(如SN 29500)
- 现场数据
- 加速寿命测试

**可靠性计算**：

1. **串联系统**：
   ```
   λ_total = λ₁ + λ₂ + ... + λn
   ```

2. **并联系统(冗余)**：
   ```
   对于1oo2系统：
   λ_total ≈ λ₁ × λ₂ × t
   (假设λ₁ = λ₂ = λ)
   λ_total ≈ λ² × t
   ```

3. **诊断覆盖率(DC)**：
   ```
   DC = λDD / (λDD + λDU)
   
   高诊断覆盖率: DC ≥ 99%
   中诊断覆盖率: 90% ≤ DC < 99%
   低诊断覆盖率: 60% ≤ DC < 90%
   ```


### 5. 软件安全要求

#### 5.1 软件安全完整性

软件不会随机失效，但会有系统性故障。

**系统性故障来源**：
- 需求错误
- 设计缺陷
- 编码错误
- 工具链问题
- 人为错误

**软件SIL要求**：
- 软件被认为是类型B系统
- 不能通过冗余降低SIL要求
- 必须通过开发过程保证质量

#### 5.2 软件开发要求

根据SIL等级，对开发过程有不同要求。

**开发方法推荐度**：

| 技术/措施 | SIL 1 | SIL 2 | SIL 3 | SIL 4 |
|----------|-------|-------|-------|-------|
| 结构化方法 | HR | HR | HR | HR |
| 半形式化方法 | R | HR | HR | HR |
| 形式化方法 | - | R | HR | HR |
| 面向对象 | R | R | R | R |
| 计算机辅助设计 | R | R | HR | HR |

**推荐度说明**：
- **HR** (Highly Recommended): 强烈推荐
- **R** (Recommended): 推荐
- **-**: 无特殊推荐

#### 5.3 软件架构设计

**模块化设计**：
- 高内聚低耦合
- 清晰的接口定义
- 限制模块大小和复杂度

**防御性编程**：
- 输入验证
- 边界检查
- 断言使用
- 错误处理

**资源管理**：
- 内存管理
- 栈使用监控
- 资源限制
- 死锁预防

**时序和同步**：
- 确定性行为
- 优先级管理
- 中断处理
- 任务调度

#### 5.4 编码标准

**MISRA C规则**：
- 避免未定义行为
- 限制语言特性
- 提高可读性
- 便于静态分析

**关键规则示例**：

1. **避免动态内存分配**
   ```c
   // 不推荐
   int *ptr = malloc(size);
   
   // 推荐
   static int buffer[MAX_SIZE];
   ```

2. **限制函数复杂度**
   ```c
   // 圈复杂度应 ≤ 10
   // 函数长度应 ≤ 50行
   ```

3. **禁止递归**
   ```c
   // 不允许
   void recursive_func(int n) {
       if (n > 0) recursive_func(n-1);
   }
   ```

4. **强制类型转换检查**
   ```c
   // 显式类型转换
   uint32_t value = (uint32_t)input;
   ```

#### 5.5 软件验证

**静态分析**：
- 代码审查
- 静态分析工具
- 复杂度分析
- 数据流分析

**动态测试**：
- 单元测试
- 集成测试
- 系统测试
- 回归测试

**测试覆盖率要求**：

| SIL等级 | 语句覆盖 | 分支覆盖 | MC/DC覆盖 |
|---------|---------|---------|-----------|
| SIL 1 | HR | R | - |
| SIL 2 | HR | HR | R |
| SIL 3 | HR | HR | HR |
| SIL 4 | HR | HR | HR |

**覆盖率说明**：
- **语句覆盖**: 每条语句至少执行一次
- **分支覆盖**: 每个分支至少执行一次
- **MC/DC**: 修改条件/判定覆盖

#### 5.6 软件工具分类

**工具分类(Tool Classification)**：

**T1类工具**: 生成输出，可能引入错误
- 编译器
- 链接器
- 代码生成器

**T2类工具**: 支持测试或验证，错误可能被检测到
- 静态分析工具
- 测试工具
- 仿真器

**T3类工具**: 不影响安全
- 编辑器
- 版本控制
- 文档工具

**工具确认要求**：

| 工具类别 | SIL 1 | SIL 2 | SIL 3 | SIL 4 |
|---------|-------|-------|-------|-------|
| T1 | TCL 1 | TCL 1 | TCL 2 | TCL 3 |
| T2 | - | TCL 1 | TCL 1 | TCL 2 |
| T3 | - | - | - | - |

**TCL (Tool Confidence Level)**: 工具置信度等级

### 6. 功能安全管理

#### 6.1 功能安全管理体系

**管理要素**：

1. **功能安全政策**
   - 组织承诺
   - 安全文化
   - 持续改进

2. **组织结构**
   - 角色和职责
   - 能力要求
   - 独立性要求

3. **资源管理**
   - 人员配备
   - 培训计划
   - 工具和设施

4. **过程管理**
   - 标准流程
   - 过程监控
   - 过程改进

#### 6.2 功能安全评估

**评估类型**：

1. **内部评估**
   - 自我评估
   - 同行评审
   - 管理评审

2. **外部评估**
   - 第三方认证
   - 独立评估
   - 客户审核

**评估内容**：
- 文档完整性
- 过程符合性
- 技术正确性
- 可追溯性

#### 6.3 配置管理

**配置项管理**：
- 需求文档
- 设计文档
- 源代码
- 测试用例
- 工具和环境

**版本控制**：
- 版本标识
- 基线管理
- 变更控制
- 发布管理

**可追溯性**：
- 需求到设计
- 设计到实现
- 实现到测试
- 测试到需求

#### 6.4 变更管理

**变更流程**：

```
变更请求 → 影响分析 → 风险评估 → 批准/拒绝
                                    ↓
                                  实施
                                    ↓
                                  验证
                                    ↓
                                  发布
```

**影响分析内容**：
- 安全影响
- 功能影响
- 性能影响
- 成本和进度影响

**回归测试**：
- 受影响的功能
- 相关的安全功能
- 系统级测试

#### 6.5 能力和培训

**能力要求**：

**功能安全工程师**：
- 功能安全标准知识
- 风险评估能力
- 系统工程经验
- 相关领域经验

**开发人员**：
- 编码标准
- 安全设计原则
- 测试方法
- 工具使用

**管理人员**：
- 功能安全概念
- 管理要求
- 审核能力

**培训计划**：
- 入职培训
- 定期培训
- 专项培训
- 培训记录


## 实践示例

### 示例1：简单的安全功能实现

以下是一个压力监控安全功能的简化实现：

```c
#include <stdint.h>
#include <stdbool.h>

// 系统配置
#define PRESSURE_THRESHOLD_HIGH  1000  // 高压阈值(kPa)
#define PRESSURE_THRESHOLD_LOW   50    // 低压阈值(kPa)
#define SENSOR_FAULT_THRESHOLD   3     // 传感器故障阈值

// 系统状态
typedef enum {
    STATE_NORMAL,
    STATE_HIGH_PRESSURE,
    STATE_SENSOR_FAULT,
    STATE_SAFE_SHUTDOWN
} system_state_t;

// 传感器数据
typedef struct {
    uint32_t pressure_value;
    bool is_valid;
    uint32_t fault_count;
} sensor_data_t;

// 全局状态
static system_state_t current_state = STATE_NORMAL;
static sensor_data_t sensor1;
static sensor_data_t sensor2;

// 读取传感器(双通道冗余)
void read_sensors(void) {
    // 读取传感器1
    sensor1.pressure_value = read_pressure_sensor_1();
    sensor1.is_valid = validate_sensor_reading(sensor1.pressure_value);
    
    // 读取传感器2
    sensor2.pressure_value = read_pressure_sensor_2();
    sensor2.is_valid = validate_sensor_reading(sensor2.pressure_value);
}

// 验证传感器读数
bool validate_sensor_reading(uint32_t value) {
    // 检查读数是否在合理范围内
    if (value < PRESSURE_THRESHOLD_LOW || 
        value > PRESSURE_THRESHOLD_HIGH * 2) {
        return false;
    }
    return true;
}

// 诊断传感器故障
bool diagnose_sensor_fault(void) {
    // 如果两个传感器都无效
    if (!sensor1.is_valid && !sensor2.is_valid) {
        return true;
    }
    
    // 如果两个传感器读数差异过大(>10%)
    if (sensor1.is_valid && sensor2.is_valid) {
        uint32_t diff = (sensor1.pressure_value > sensor2.pressure_value) ?
                       (sensor1.pressure_value - sensor2.pressure_value) :
                       (sensor2.pressure_value - sensor1.pressure_value);
        
        uint32_t avg = (sensor1.pressure_value + sensor2.pressure_value) / 2;
        if (diff > avg / 10) {
            return true;
        }
    }
    
    return false;
}

// 获取有效压力值(1oo2投票)
uint32_t get_valid_pressure(void) {
    // 如果两个传感器都有效，取平均值
    if (sensor1.is_valid && sensor2.is_valid) {
        return (sensor1.pressure_value + sensor2.pressure_value) / 2;
    }
    
    // 如果只有一个传感器有效，使用该值
    if (sensor1.is_valid) {
        return sensor1.pressure_value;
    }
    if (sensor2.is_valid) {
        return sensor2.pressure_value;
    }
    
    // 两个传感器都无效
    return 0;
}

// 安全功能主循环
void safety_function_main(void) {
    // 读取传感器
    read_sensors();
    
    // 诊断传感器故障
    if (diagnose_sensor_fault()) {
        sensor1.fault_count++;
        sensor2.fault_count++;
        
        // 如果故障次数超过阈值，进入故障状态
        if (sensor1.fault_count >= SENSOR_FAULT_THRESHOLD) {
            current_state = STATE_SENSOR_FAULT;
            trigger_safe_shutdown();
            return;
        }
    } else {
        // 重置故障计数
        sensor1.fault_count = 0;
        sensor2.fault_count = 0;
    }
    
    // 获取有效压力值
    uint32_t pressure = get_valid_pressure();
    
    // 检查压力是否超过阈值
    if (pressure > PRESSURE_THRESHOLD_HIGH) {
        current_state = STATE_HIGH_PRESSURE;
        trigger_safe_shutdown();
    } else {
        current_state = STATE_NORMAL;
    }
}

// 触发安全停机
void trigger_safe_shutdown(void) {
    // 关闭主阀门
    close_main_valve();
    
    // 激活报警
    activate_alarm();
    
    // 记录事件
    log_safety_event(current_state);
    
    // 进入安全状态
    current_state = STATE_SAFE_SHUTDOWN;
}
```

**代码说明**：
- 双通道传感器冗余(1oo2)
- 传感器读数验证
- 故障诊断和计数
- 安全停机功能
- 符合SIL 2要求

### 示例2：看门狗实现

```c
#include <stdint.h>
#include <stdbool.h>

// 看门狗配置
#define WATCHDOG_TIMEOUT_MS  1000
#define WATCHDOG_WINDOW_MS   100

// 看门狗状态
typedef struct {
    uint32_t last_kick_time;
    uint32_t kick_count;
    bool is_enabled;
} watchdog_t;

static watchdog_t watchdog;

// 初始化看门狗
void watchdog_init(void) {
    watchdog.last_kick_time = get_system_time_ms();
    watchdog.kick_count = 0;
    watchdog.is_enabled = true;
    
    // 配置硬件看门狗
    configure_hardware_watchdog(WATCHDOG_TIMEOUT_MS);
}

// 喂狗(窗口看门狗)
bool watchdog_kick(void) {
    if (!watchdog.is_enabled) {
        return false;
    }
    
    uint32_t current_time = get_system_time_ms();
    uint32_t elapsed = current_time - watchdog.last_kick_time;
    
    // 检查是否在窗口期内
    if (elapsed < WATCHDOG_WINDOW_MS) {
        // 喂狗太频繁，可能是软件异常
        return false;
    }
    
    if (elapsed > WATCHDOG_TIMEOUT_MS) {
        // 超时，看门狗会复位系统
        return false;
    }
    
    // 喂狗
    kick_hardware_watchdog();
    watchdog.last_kick_time = current_time;
    watchdog.kick_count++;
    
    return true;
}

// 主任务循环
void main_task(void) {
    watchdog_init();
    
    while (1) {
        // 执行正常任务
        perform_normal_tasks();
        
        // 自检
        if (!perform_self_test()) {
            // 自检失败，不喂狗，让系统复位
            while(1);
        }
        
        // 喂狗
        if (!watchdog_kick()) {
            // 喂狗失败，记录错误
            log_error("Watchdog kick failed");
        }
        
        // 延时
        delay_ms(500);
    }
}
```

**代码说明**：
- 窗口看门狗(防止喂狗太频繁)
- 自检机制
- 故障时不喂狗，触发复位
- 提高系统可靠性

### 示例3：内存测试

```c
#include <stdint.h>
#include <stdbool.h>

// RAM测试(March算法)
bool test_ram(uint32_t *start_addr, uint32_t size) {
    uint32_t *addr;
    uint32_t i;
    
    // Phase 1: 写0
    for (i = 0; i < size; i++) {
        start_addr[i] = 0x00000000;
    }
    
    // Phase 2: 读0，写1
    for (i = 0; i < size; i++) {
        if (start_addr[i] != 0x00000000) {
            return false;
        }
        start_addr[i] = 0xFFFFFFFF;
    }
    
    // Phase 3: 读1，写0
    for (i = 0; i < size; i++) {
        if (start_addr[i] != 0xFFFFFFFF) {
            return false;
        }
        start_addr[i] = 0x00000000;
    }
    
    // Phase 4: 读0
    for (i = 0; i < size; i++) {
        if (start_addr[i] != 0x00000000) {
            return false;
        }
    }
    
    return true;
}

// ROM/Flash测试(CRC校验)
bool test_rom(uint32_t *start_addr, uint32_t size, uint32_t expected_crc) {
    uint32_t calculated_crc = calculate_crc32(start_addr, size);
    return (calculated_crc == expected_crc);
}

// 启动时内存测试
bool startup_memory_test(void) {
    // 测试RAM
    if (!test_ram(RAM_START_ADDR, RAM_SIZE)) {
        log_error("RAM test failed");
        return false;
    }
    
    // 测试ROM
    if (!test_rom(ROM_START_ADDR, ROM_SIZE, EXPECTED_ROM_CRC)) {
        log_error("ROM test failed");
        return false;
    }
    
    return true;
}

// 运行时内存测试(分段测试)
void runtime_memory_test(void) {
    static uint32_t test_segment = 0;
    const uint32_t segment_size = 256;  // 每次测试256字节
    
    uint32_t *test_addr = RAM_START_ADDR + (test_segment * segment_size);
    
    // 保存数据
    uint32_t backup[segment_size];
    memcpy(backup, test_addr, segment_size * sizeof(uint32_t));
    
    // 测试内存
    bool result = test_ram(test_addr, segment_size);
    
    // 恢复数据
    memcpy(test_addr, backup, segment_size * sizeof(uint32_t));
    
    if (!result) {
        log_error("Runtime RAM test failed at segment %d", test_segment);
        trigger_safe_shutdown();
    }
    
    // 移动到下一段
    test_segment++;
    if (test_segment >= (RAM_SIZE / segment_size)) {
        test_segment = 0;
    }
}
```

**代码说明**：
- March算法RAM测试
- CRC校验ROM完整性
- 启动时完整测试
- 运行时分段测试
- 提高故障检测覆盖率


## 深入理解

### 功能安全 vs 网络安全

随着物联网和工业4.0的发展，功能安全和网络安全的交叉越来越重要。

**关系和区别**：

| 方面 | 功能安全 | 网络安全 |
|------|---------|---------|
| 关注点 | 系统故障 | 恶意攻击 |
| 威胁来源 | 随机故障、系统性故障 | 黑客、恶意软件 |
| 目标 | 避免危害 | 保护资产 |
| 方法 | 冗余、诊断、安全状态 | 加密、认证、访问控制 |
| 标准 | IEC 61508, ISO 26262 | ISO 27001, IEC 62443 |

**交叉影响**：

1. **网络攻击可能导致安全功能失效**
   - 攻击者禁用安全功能
   - 篡改传感器数据
   - 阻止安全停机

2. **安全功能可能被网络攻击利用**
   - 触发不必要的停机
   - 拒绝服务攻击
   - 降低系统可用性

**综合考虑**：
- 安全功能需要防护网络攻击
- 网络安全措施不能影响安全功能
- 需要综合的风险评估
- 两个领域的专家需要协作

### SIL等级的实际意义

**SIL等级不是越高越好**：

1. **成本考虑**
   - SIL 4系统成本可能是SIL 1的10倍以上
   - 需要更多的冗余和验证
   - 开发周期更长

2. **复杂度考虑**
   - 高SIL系统更复杂
   - 可能引入新的故障模式
   - 维护难度增加

3. **合理性考虑**
   - 根据实际风险确定SIL
   - 过度设计浪费资源
   - 欠设计存在风险

**SIL等级选择原则**：
- 基于风险评估
- 考虑成本效益
- 符合法规要求
- 行业最佳实践

### 功能安全认证

**认证的价值**：

1. **市场准入**
   - 某些市场要求认证
   - 客户信任
   - 竞争优势

2. **质量保证**
   - 独立评估
   - 发现问题
   - 持续改进

3. **法律保护**
   - 尽职调查证明
   - 降低法律风险
   - 保险优惠

**认证流程**：

```
准备阶段 → 文档审查 → 现场审核 → 测试验证 → 认证决定
    ↓          ↓          ↓          ↓          ↓
  计划      提交文档    回答问题    修正问题    获得证书
```

**认证成本**：
- 认证机构费用
- 内部准备成本
- 修正问题成本
- 时间成本

**常见认证机构**：
- TÜV (德国技术监督协会)
- Exida
- SGS
- UL

### 功能安全的挑战

**技术挑战**：

1. **软件复杂度**
   - 现代软件越来越复杂
   - 难以完全验证
   - 工具链可靠性

2. **硬件集成度**
   - 芯片集成度高
   - 故障模式复杂
   - 诊断困难

3. **系统互联**
   - 系统间交互
   - 接口复杂
   - 故障传播

**管理挑战**：

1. **成本压力**
   - 功能安全增加成本
   - 市场竞争激烈
   - 需要平衡

2. **时间压力**
   - 上市时间要求
   - 功能安全需要时间
   - 需要提前规划

3. **能力建设**
   - 专业人才短缺
   - 培训成本高
   - 经验积累慢

**应对策略**：
- 早期介入功能安全
- 使用成熟的工具和方法
- 建立功能安全文化
- 持续学习和改进

## 常见问题

### Q1: 功能安全和质量管理有什么区别？

**A**: 主要区别在于关注点和方法：

**质量管理(如ISO 9001)**：
- 关注产品符合规格
- 预防缺陷
- 客户满意度
- 持续改进

**功能安全(如IEC 61508)**：
- 关注安全相关功能
- 量化风险
- 避免危害
- 安全生命周期

**关系**：
- 功能安全建立在质量管理基础上
- 质量管理是必要但不充分的
- 功能安全有更严格的要求
- 两者可以整合

### Q2: 如何确定系统需要达到哪个SIL等级？

**A**: 确定SIL等级需要进行风险评估：

**步骤1：识别危害**
- 系统可能造成的伤害
- 考虑所有操作模式
- 包括误用场景

**步骤2：评估风险**
- 后果严重程度
- 发生概率
- 暴露频率
- 避免可能性

**步骤3：确定可容忍风险**
- 法规要求
- 行业标准
- 社会接受度

**步骤4：计算所需风险降低**
- 当前风险 / 可容忍风险
- 确定风险降低因子

**步骤5：映射到SIL等级**
- 使用风险图或风险矩阵
- 考虑其他风险降低措施
- 确定最终SIL等级

### Q3: 软件可以通过冗余提高SIL等级吗？

**A**: 不能简单地通过软件冗余提高SIL等级。

**原因**：
- 软件是确定性的
- 相同输入产生相同输出
- 相同的bug会在所有副本中存在
- 不能降低系统性故障

**例外情况**：
- **多样性设计**：不同团队、不同语言、不同算法
- **N版本编程**：独立开发多个版本
- **成本高、难度大**：实际应用较少

**正确做法**：
- 通过开发过程保证质量
- 严格的验证和确认
- 使用成熟的工具和方法
- 充分的测试覆盖

### Q4: 如何在敏捷开发中实施功能安全？

**A**: 敏捷开发和功能安全可以结合：

**挑战**：
- 功能安全强调文档和计划
- 敏捷强调灵活和快速迭代
- 看似矛盾

**解决方案**：

1. **安全敏捷(Safe Agile)**
   - 在迭代中包含安全活动
   - 增量式文档
   - 持续验证

2. **分层方法**
   - 安全关键部分：传统方法
   - 非安全关键部分：敏捷方法
   - 清晰的接口定义

3. **工具支持**
   - 自动化测试
   - 持续集成
   - 可追溯性工具

4. **团队能力**
   - 团队成员具备功能安全知识
   - 安全专家参与迭代
   - 定期安全审查

### Q5: 功能安全认证是强制的吗？

**A**: 取决于应用领域和市场：

**强制认证**：
- 某些行业有法规要求
- 特定市场准入条件
- 例如：铁路、医疗设备

**非强制但推荐**：
- 工业控制系统
- 汽车电子
- 消费电子

**不认证的风险**：
- 市场准入困难
- 客户不信任
- 法律责任风险
- 保险费用高

**认证的替代方案**：
- 自我评估
- 客户审核
- 第三方评审(非认证)

**建议**：
- 了解目标市场要求
- 评估成本效益
- 至少遵循标准要求
- 保留完整文档


## 总结

### 核心要点

1. **功能安全基本概念**
   - 关注系统故障导致的危害
   - 通过安全功能降低风险
   - 不同于可靠性和信息安全
   - 需要系统化的方法

2. **IEC 61508标准**
   - 功能安全的基础标准
   - 7个部分，涵盖全生命周期
   - 适用于E/E/PE安全相关系统
   - 其他行业标准的基础

3. **安全完整性等级(SIL)**
   - SIL 1到SIL 4四个等级
   - 基于风险评估确定
   - 不同等级有不同要求
   - 需要平衡成本和风险

4. **功能安全生命周期**
   - 从概念到退役的完整过程
   - V模型开发流程
   - 每个阶段都有安全要求
   - 强调验证和确认

5. **硬件安全要求**
   - 架构约束(HFT)
   - 安全失效分数(SFF)
   - 故障检测和诊断
   - 随机硬件失效分析

6. **软件安全要求**
   - 系统性故障预防
   - 严格的开发过程
   - 编码标准(MISRA C)
   - 高测试覆盖率要求

7. **功能安全管理**
   - 管理体系建设
   - 配置和变更管理
   - 能力和培训
   - 独立评估

### 实践建议

**项目启动阶段**：
- 尽早考虑功能安全
- 进行初步风险评估
- 确定SIL等级
- 制定功能安全计划

**设计阶段**：
- 遵循安全设计原则
- 选择合适的架构
- 定义安全功能
- 进行设计审查

**实现阶段**：
- 遵循编码标准
- 使用合格的工具
- 进行代码审查
- 实施配置管理

**测试阶段**：
- 充分的测试覆盖
- 故障注入测试
- 安全功能验证
- 文档完整性检查

**运行阶段**：
- 定期维护和测试
- 故障记录和分析
- 变更管理
- 持续改进

### 常见误区

**误区1：功能安全只是增加冗余**
- **错误**：简单地复制组件
- **正确**：系统化的安全设计，包括故障检测、诊断和安全状态

**误区2：功能安全只是硬件问题**
- **错误**：忽视软件的系统性故障
- **正确**：软件同样重要，需要严格的开发过程

**误区3：功能安全可以后期添加**
- **错误**：产品完成后再考虑安全
- **正确**：从概念阶段就开始考虑

**误区4：通过测试可以达到任何SIL**
- **错误**：依赖测试发现所有问题
- **正确**：需要整个生命周期的质量保证

**误区5：功能安全认证就是安全的**
- **错误**：认证后就不管了
- **正确**：需要持续的维护和改进

### 下一步学习

掌握功能安全基础后，建议继续学习：
- 信息安全基础知识 - 了解网络安全
- 安全启动与固件验证 - 实现安全启动
- 故障检测与诊断技术 - 提高诊断覆盖率
- ISO 26262汽车功能安全 - 行业特定标准
- 高可靠性系统设计实战 - 综合应用

## 延伸阅读

### 推荐书籍

- 《IEC 61508标准解读》- 标准详细解释
- 《功能安全实践指南》- 实施指导
- 《嵌入式系统功能安全》- 嵌入式应用
- 《软件安全工程》- 软件安全方法

### 在线资源

- [IEC官网](https://www.iec.ch/) - 标准信息
- [Functional Safety.net](https://www.functional-safety.net/) - 功能安全社区
- [Safety Critical Systems Club](https://scsc.uk/) - 安全关键系统俱乐部
- [Exida](https://www.exida.com/) - 功能安全咨询和认证

### 相关标准

- **IEC 61508**: 通用功能安全标准
- **ISO 26262**: 汽车功能安全
- **EN 50128**: 铁路软件
- **IEC 62304**: 医疗设备软件
- **IEC 62443**: 工业自动化安全
- **DO-178C**: 航空软件

### 相关文章

- 嵌入式系统安全概述 - 安全基础知识
- 信息安全基础知识 - 网络安全
- 可靠性设计原则 - 可靠性工程
- 故障检测与诊断技术 - 诊断方法
- ISO 26262汽车功能安全 - 汽车标准

## 参考资料

1. IEC 61508:2010 - 电气/电子/可编程电子安全相关系统的功能安全
2. IEC 61511 - 过程工业领域安全仪表系统
3. ISO 26262 - 道路车辆功能安全
4. EN 50128 - 铁路应用-通信、信号和处理系统-软件
5. Smith, D.J., Simpson, K.G.L. (2016). "Functional Safety: A Straightforward Guide to IEC 61508"
6. Braband, J. (2014). "Creating Safety-Critical Software and Systems"

---

**思考题**：

1. 分析你正在开发的系统，确定是否需要功能安全，如果需要，应该达到哪个SIL等级？
2. 使用风险图方法，为一个具体的安全功能确定SIL等级
3. 设计一个双通道冗余的传感器系统，包括故障检测机制
4. 制定一个功能安全项目的文档清单

**实践项目**：

设计一个简单的安全关键系统，要求：
- 进行危害和风险分析
- 确定安全功能和SIL等级
- 设计硬件架构(包括冗余和诊断)
- 设计软件架构(符合MISRA C)
- 制定测试计划(包括覆盖率要求)
- 编写功能安全计划

**下一步**：建议学习 [信息安全基础知识](03-information-security-basics.html)

