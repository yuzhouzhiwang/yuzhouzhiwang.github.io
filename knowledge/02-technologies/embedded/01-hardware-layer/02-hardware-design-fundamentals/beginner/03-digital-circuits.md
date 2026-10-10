---
# 基础信息
title: "数字电路基础：逻辑门与时序电路"
description: "深入讲解数字电路的基本构建模块：逻辑门和时序电路，掌握组合逻辑和时序逻辑的设计原理，理解触发器的工作机制和时序分析方法"
slug: "digital-circuits-logic-gates-sequential"

# 分类信息
domain: "01-hardware-layer"
module: "02-hardware-design-fundamentals"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 数字电路
  - 逻辑门
  - 时序电路
  - 触发器
  - 组合逻辑
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 40
difficulty_score: 2

# 作者和版本
author: "嵌入式知识平台内容团队"
author_id: ""
created_at: "2026-03-07"
updated_at: "2026-03-07"
version: "1.0.0"

# 语言和本地化
language: "zh-CN"
translations: []

# 状态和可见性
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - 数字电路基础
  - 逻辑门电路
  - 时序逻辑
  - 触发器原理
  - 布尔代数
cover_image: ""
---

# 数字电路基础：逻辑门与时序电路

## 学习目标

完成本文学习后，你将能够：

- [ ] 理解数字电路的基本概念和二进制逻辑
- [ ] 掌握基本逻辑门（AND、OR、NOT、XOR等）的功能和真值表
- [ ] 理解组合逻辑电路的设计方法
- [ ] 掌握触发器的工作原理和类型
- [ ] 理解时序逻辑电路的基本概念
- [ ] 能够进行简单的时序分析


## 前置要求

在开始本文学习之前，你需要：

**知识要求**：
- 了解基本的电学概念（电压、电流）
- 理解二进制数制（0和1）
- 了解基本的布尔代数概念
- 熟悉基本的逻辑运算

**技能要求**：
- 能够阅读简单的电路图
- 了解基本的电路符号
- 理解真值表的概念

**推荐但非必需**：
- 有一定的编程基础（理解逻辑运算）
- 了解基本的电子元件
- 熟悉示波器的使用

## 概述

数字电路是现代电子系统的基础，从简单的逻辑门到复杂的微处理器，都是由数字电路构成的。与模拟电路处理连续信号不同，数字电路只处理离散的二进制信号（0和1），这使得数字电路具有抗干扰能力强、易于设计和集成的优点。

### 为什么要学习数字电路

1. **嵌入式系统基础**：微控制器内部都是数字电路
2. **接口设计**：GPIO、总线等都基于数字逻辑
3. **时序理解**：理解时钟、建立时间、保持时间等概念
4. **FPGA/CPLD开发**：数字电路是硬件描述语言的基础
5. **故障排查**：理解数字信号的特性有助于调试

### 数字电路的基本特点

| 特性 | 模拟电路 | 数字电路 |
|------|---------|---------|
| 信号类型 | 连续信号 | 离散信号（0/1） |
| 抗干扰性 | 较弱 | 较强 |
| 精度 | 受元件影响大 | 由位数决定 |
| 设计复杂度 | 较高 | 相对简单 |
| 集成度 | 较低 | 很高 |
| 功耗 | 相对较低 | 动态功耗较高 |


## 第一部分：数字逻辑基础

### 二进制与逻辑电平

数字电路使用二进制表示信息，只有两个状态：

**逻辑电平定义**：

```
逻辑1（高电平）：
- TTL：2.0V - 5.0V
- CMOS 3.3V：2.0V - 3.6V
- CMOS 5V：3.5V - 5.5V

逻辑0（低电平）：
- TTL：0V - 0.8V
- CMOS 3.3V：0V - 0.8V
- CMOS 5V：0V - 1.5V

不确定区域（禁区）：
- 介于逻辑0和逻辑1之间的电压
- 应避免信号停留在此区域
```

**正逻辑与负逻辑**：

```
正逻辑：
- 高电平 = 逻辑1
- 低电平 = 逻辑0
- 最常用的约定

负逻辑：
- 高电平 = 逻辑0
- 低电平 = 逻辑1
- 某些特殊应用使用
```

### 布尔代数基础

布尔代数是数字电路的数学基础，只有三种基本运算：

**1. 与运算（AND）**：
```
符号：A · B 或 A ∧ B 或 AB
C语言：A && B 或 A & B
规则：只有所有输入都为1时，输出才为1
```

**2. 或运算（OR）**：
```
符号：A + B 或 A ∨ B
C语言：A || B 或 A | B
规则：只要有一个输入为1，输出就为1
```

**3. 非运算（NOT）**：
```
符号：Ā 或 A' 或 ¬A
C语言：!A 或 ~A
规则：输入为1时输出为0，输入为0时输出为1
```

**基本定律**：

```
交换律：
A + B = B + A
A · B = B · A

结合律：
(A + B) + C = A + (B + C)
(A · B) · C = A · (B · C)

分配律：
A · (B + C) = A · B + A · C
A + (B · C) = (A + B) · (A + C)

德摩根定律：
(A + B)' = A' · B'
(A · B)' = A' + B'

恒等律：
A + 0 = A
A · 1 = A
A + 1 = 1
A · 0 = 0

互补律：
A + A' = 1
A · A' = 0

幂等律：
A + A = A
A · A = A
```


## 第二部分：基本逻辑门

### 1. 与门（AND Gate）

与门实现逻辑与运算，只有所有输入都为1时，输出才为1。

**电路符号**：
```
    A ──┐
        ├──D──── Y = A · B
    B ──┘
```

**真值表**：

| A | B | Y = A · B |
|---|---|-----------|
| 0 | 0 | 0         |
| 0 | 1 | 0         |
| 1 | 0 | 0         |
| 1 | 1 | 1         |

**C语言实现**：

```c
/**
 * @brief  与门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t and_gate(uint8_t a, uint8_t b) {
    return a & b;  // 位与运算
}

// 使用示例
void and_gate_example(void) {
    printf("AND Gate Truth Table:\n");
    printf("A | B | Y\n");
    printf("--|---|--\n");
    for (int a = 0; a <= 1; a++) {
        for (int b = 0; b <= 1; b++) {
            printf("%d | %d | %d\n", a, b, and_gate(a, b));
        }
    }
}
```

**应用场景**：
- 使能控制：只有使能信号有效时，数据才能通过
- 条件判断：多个条件同时满足时执行操作
- 位掩码：提取特定位的信息

### 2. 或门（OR Gate）

或门实现逻辑或运算，只要有一个输入为1，输出就为1。

**电路符号**：
```
    A ──┐
        ├≥1─── Y = A + B
    B ──┘
```

**真值表**：

| A | B | Y = A + B |
|---|---|-----------|
| 0 | 0 | 0         |
| 0 | 1 | 1         |
| 1 | 0 | 1         |
| 1 | 1 | 1         |

**C语言实现**：

```c
/**
 * @brief  或门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t or_gate(uint8_t a, uint8_t b) {
    return a | b;  // 位或运算
}
```

**应用场景**：
- 中断源合并：多个中断源触发同一个中断
- 错误标志：任何一个错误发生都置位错误标志
- 唤醒源：多个唤醒源中任一个有效都唤醒系统

### 3. 非门（NOT Gate / Inverter）

非门实现逻辑非运算，输出是输入的反相。

**电路符号**：
```
    A ──▷○─── Y = A'
```

**真值表**：

| A | Y = A' |
|---|--------|
| 0 | 1      |
| 1 | 0      |

**C语言实现**：

```c
/**
 * @brief  非门逻辑
 * @param  a: 输入A（0或1）
 * @retval 输出Y
 */
uint8_t not_gate(uint8_t a) {
    return !a;  // 逻辑非运算
    // 或者：return ~a & 0x01;  // 位非运算（需要屏蔽高位）
}
```

**应用场景**：
- 信号反相：将高电平有效信号转换为低电平有效
- 逻辑取反：实现相反的逻辑功能
- 时钟反相：产生反相时钟信号


### 4. 与非门（NAND Gate）

与非门是与门后接非门，是最基本的逻辑门之一（可以用它构造所有其他逻辑门）。

**电路符号**：
```
    A ──┐
        ├──D○─── Y = (A · B)'
    B ──┘
```

**真值表**：

| A | B | Y = (A · B)' |
|---|---|--------------|
| 0 | 0 | 1            |
| 0 | 1 | 1            |
| 1 | 0 | 1            |
| 1 | 1 | 0            |

**C语言实现**：

```c
/**
 * @brief  与非门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t nand_gate(uint8_t a, uint8_t b) {
    return !(a & b);  // 与非运算
}
```

**重要性**：
- NAND门是"功能完备"的，可以用它实现任何逻辑函数
- 在CMOS工艺中，NAND门比NOR门更容易实现
- 许多数字IC内部大量使用NAND门

### 5. 或非门（NOR Gate）

或非门是或门后接非门，也是功能完备的逻辑门。

**电路符号**：
```
    A ──┐
        ├≥1○─── Y = (A + B)'
    B ──┘
```

**真值表**：

| A | B | Y = (A + B)' |
|---|---|--------------|
| 0 | 0 | 1            |
| 0 | 1 | 0            |
| 1 | 0 | 0            |
| 1 | 1 | 0            |

**C语言实现**：

```c
/**
 * @brief  或非门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t nor_gate(uint8_t a, uint8_t b) {
    return !(a | b);  // 或非运算
}
```

### 6. 异或门（XOR Gate）

异或门输出两个输入不同时为1，相同时为0。

**电路符号**：
```
    A ──┐
        ├=1─── Y = A ⊕ B
    B ──┘
```

**真值表**：

| A | B | Y = A ⊕ B |
|---|---|-----------|
| 0 | 0 | 0         |
| 0 | 1 | 1         |
| 1 | 0 | 1         |
| 1 | 1 | 0         |

**C语言实现**：

```c
/**
 * @brief  异或门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t xor_gate(uint8_t a, uint8_t b) {
    return a ^ b;  // 异或运算
}
```

**应用场景**：
- 奇偶校验：检测数据传输错误
- 比较器：判断两个信号是否相同
- 加法器：实现二进制加法的基础
- 数据加密：简单的加密算法

### 7. 同或门（XNOR Gate）

同或门是异或门的反相，两个输入相同时输出为1。

**电路符号**：
```
    A ──┐
        ├=1○─── Y = (A ⊕ B)'
    B ──┘
```

**真值表**：

| A | B | Y = (A ⊕ B)' |
|---|---|--------------|
| 0 | 0 | 1            |
| 0 | 1 | 0            |
| 1 | 0 | 0            |
| 1 | 1 | 1            |

**C语言实现**：

```c
/**
 * @brief  同或门逻辑
 * @param  a: 输入A（0或1）
 * @param  b: 输入B（0或1）
 * @retval 输出Y
 */
uint8_t xnor_gate(uint8_t a, uint8_t b) {
    return !(a ^ b);  // 同或运算
}
```

**应用场景**：
- 相等比较：判断两个信号是否相等
- 数据校验：验证数据一致性


### 逻辑门总结

**逻辑门对比表**：

| 门类型 | 符号 | 逻辑表达式 | 特点 | 常用场景 |
|--------|------|-----------|------|---------|
| AND | D | Y = A · B | 全1出1 | 使能控制 |
| OR | ≥1 | Y = A + B | 有1出1 | 信号合并 |
| NOT | ▷○ | Y = A' | 反相 | 信号取反 |
| NAND | D○ | Y = (A · B)' | 功能完备 | 通用逻辑 |
| NOR | ≥1○ | Y = (A + B)' | 功能完备 | 通用逻辑 |
| XOR | =1 | Y = A ⊕ B | 不同出1 | 校验/比较 |
| XNOR | =1○ | Y = (A ⊕ B)' | 相同出1 | 相等判断 |

**逻辑门实现示例**：

```c
/**
 * @brief  完整的逻辑门库
 */
typedef struct {
    uint8_t (*and_gate)(uint8_t a, uint8_t b);
    uint8_t (*or_gate)(uint8_t a, uint8_t b);
    uint8_t (*not_gate)(uint8_t a);
    uint8_t (*nand_gate)(uint8_t a, uint8_t b);
    uint8_t (*nor_gate)(uint8_t a, uint8_t b);
    uint8_t (*xor_gate)(uint8_t a, uint8_t b);
    uint8_t (*xnor_gate)(uint8_t a, uint8_t b);
} logic_gates_t;

// 逻辑门测试函数
void test_all_logic_gates(void) {
    printf("Complete Logic Gates Truth Tables:\n\n");
    
    printf("AND | OR  | NOT | NAND| NOR | XOR | XNOR\n");
    printf("A B Y | A B Y | A Y | A B Y | A B Y | A B Y | A B Y\n");
    printf("------|-------|-----|-------|-------|-------|------\n");
    
    for (int a = 0; a <= 1; a++) {
        for (int b = 0; b <= 1; b++) {
            printf("%d %d %d | ", a, b, and_gate(a, b));
            printf("%d %d %d | ", a, b, or_gate(a, b));
            if (b == 0) printf("%d %d | ", a, not_gate(a));
            else printf("    | ");
            printf("%d %d %d | ", a, b, nand_gate(a, b));
            printf("%d %d %d | ", a, b, nor_gate(a, b));
            printf("%d %d %d | ", a, b, xor_gate(a, b));
            printf("%d %d %d\n", a, b, xnor_gate(a, b));
        }
    }
}
```


## 第三部分：组合逻辑电路

组合逻辑电路的输出只取决于当前输入，不依赖于历史状态。

### 1. 半加器（Half Adder）

半加器实现两个一位二进制数的加法，产生和（Sum）与进位（Carry）。

**逻辑表达式**：
```
Sum = A ⊕ B
Carry = A · B
```

**真值表**：

| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 | 0   | 0     |
| 0 | 1 | 1   | 0     |
| 1 | 0 | 1   | 0     |
| 1 | 1 | 0   | 1     |

**C语言实现**：

```c
/**
 * @brief  半加器
 * @param  a: 输入A
 * @param  b: 输入B
 * @param  sum: 输出和
 * @param  carry: 输出进位
 */
void half_adder(uint8_t a, uint8_t b, uint8_t *sum, uint8_t *carry) {
    *sum = a ^ b;      // 异或得到和
    *carry = a & b;    // 与得到进位
}

// 使用示例
void half_adder_example(void) {
    uint8_t sum, carry;
    
    printf("Half Adder Truth Table:\n");
    printf("A | B | Sum | Carry\n");
    printf("--|---|-----|------\n");
    
    for (int a = 0; a <= 1; a++) {
        for (int b = 0; b <= 1; b++) {
            half_adder(a, b, &sum, &carry);
            printf("%d | %d |  %d  |   %d\n", a, b, sum, carry);
        }
    }
}
```

### 2. 全加器（Full Adder）

全加器在半加器基础上增加了进位输入，可以实现多位加法。

**逻辑表达式**：
```
Sum = A ⊕ B ⊕ Cin
Cout = (A · B) + (Cin · (A ⊕ B))
```

**真值表**：

| A | B | Cin | Sum | Cout |
|---|---|-----|-----|------|
| 0 | 0 | 0   | 0   | 0    |
| 0 | 0 | 1   | 1   | 0    |
| 0 | 1 | 0   | 1   | 0    |
| 0 | 1 | 1   | 0   | 1    |
| 1 | 0 | 0   | 1   | 0    |
| 1 | 0 | 1   | 0   | 1    |
| 1 | 1 | 0   | 0   | 1    |
| 1 | 1 | 1   | 1   | 1    |

**C语言实现**：

```c
/**
 * @brief  全加器
 * @param  a: 输入A
 * @param  b: 输入B
 * @param  cin: 进位输入
 * @param  sum: 输出和
 * @param  cout: 输出进位
 */
void full_adder(uint8_t a, uint8_t b, uint8_t cin, 
                uint8_t *sum, uint8_t *cout) {
    *sum = a ^ b ^ cin;
    *cout = (a & b) | (cin & (a ^ b));
}

/**
 * @brief  4位二进制加法器
 * @param  a: 4位输入A
 * @param  b: 4位输入B
 * @retval 5位结果（包含进位）
 */
uint8_t adder_4bit(uint8_t a, uint8_t b) {
    uint8_t sum = 0;
    uint8_t carry = 0;
    uint8_t s, c;
    
    for (int i = 0; i < 4; i++) {
        uint8_t bit_a = (a >> i) & 0x01;
        uint8_t bit_b = (b >> i) & 0x01;
        
        full_adder(bit_a, bit_b, carry, &s, &c);
        
        sum |= (s << i);
        carry = c;
    }
    
    // 最高位是进位
    sum |= (carry << 4);
    
    return sum;
}

// 使用示例
void adder_example(void) {
    uint8_t a = 0b1010;  // 10
    uint8_t b = 0b0111;  // 7
    uint8_t result = adder_4bit(a, b);
    
    printf("4-bit Adder: %d + %d = %d\n", a, b, result);
    // 输出：4-bit Adder: 10 + 7 = 17
}
```


### 3. 多路选择器（Multiplexer, MUX）

多路选择器根据选择信号从多个输入中选择一个输出。

**2选1多路选择器**：

```
逻辑表达式：
Y = (S' · A) + (S · B)

当S=0时，Y=A
当S=1时，Y=B
```

**真值表**：

| S | A | B | Y |
|---|---|---|---|
| 0 | 0 | X | 0 |
| 0 | 1 | X | 1 |
| 1 | X | 0 | 0 |
| 1 | X | 1 | 1 |

**C语言实现**：

```c
/**
 * @brief  2选1多路选择器
 * @param  a: 输入A
 * @param  b: 输入B
 * @param  sel: 选择信号（0选A，1选B）
 * @retval 输出Y
 */
uint8_t mux_2to1(uint8_t a, uint8_t b, uint8_t sel) {
    return sel ? b : a;
    // 或者：return (!sel & a) | (sel & b);
}

/**
 * @brief  4选1多路选择器
 * @param  inputs: 4个输入的数组
 * @param  sel: 2位选择信号（0-3）
 * @retval 输出Y
 */
uint8_t mux_4to1(uint8_t inputs[4], uint8_t sel) {
    return inputs[sel & 0x03];
}

// 使用示例
void mux_example(void) {
    uint8_t inputs[4] = {0xAA, 0xBB, 0xCC, 0xDD};
    
    printf("4-to-1 Multiplexer:\n");
    for (int sel = 0; sel < 4; sel++) {
        printf("SEL=%d: Output=0x%02X\n", sel, mux_4to1(inputs, sel));
    }
}
```

**应用场景**：
- 数据选择：从多个数据源中选择一个
- 总线切换：在多个设备间切换总线访问
- 功能选择：根据配置选择不同的功能模块

### 4. 译码器（Decoder）

译码器将二进制编码转换为独热码（one-hot）输出。

**2-4译码器**：

```
输入：2位二进制（A1 A0）
输出：4个独热码输出（Y3 Y2 Y1 Y0）
```

**真值表**：

| A1 | A0 | Y3 | Y2 | Y1 | Y0 |
|----|----|----|----|----|-----|
| 0  | 0  | 0  | 0  | 0  | 1   |
| 0  | 1  | 0  | 0  | 1  | 0   |
| 1  | 0  | 0  | 1  | 0  | 0   |
| 1  | 1  | 1  | 0  | 0  | 0   |

**C语言实现**：

```c
/**
 * @brief  2-4译码器
 * @param  input: 2位输入（0-3）
 * @retval 4位独热码输出
 */
uint8_t decoder_2to4(uint8_t input) {
    return 1 << (input & 0x03);
}

/**
 * @brief  3-8译码器
 * @param  input: 3位输入（0-7）
 * @retval 8位独热码输出
 */
uint8_t decoder_3to8(uint8_t input) {
    return 1 << (input & 0x07);
}

// 使用示例
void decoder_example(void) {
    printf("2-to-4 Decoder:\n");
    printf("Input | Output (binary)\n");
    printf("------|----------------\n");
    
    for (int i = 0; i < 4; i++) {
        uint8_t output = decoder_2to4(i);
        printf("  %d   | ", i);
        for (int j = 3; j >= 0; j--) {
            printf("%d", (output >> j) & 0x01);
        }
        printf("\n");
    }
}
```

**应用场景**：
- 地址译码：将地址信号转换为片选信号
- 指令译码：CPU中将指令码转换为控制信号
- 显示驱动：驱动7段数码管等显示器件


## 第四部分：时序逻辑电路

时序逻辑电路的输出不仅取决于当前输入，还取决于电路的历史状态。时序电路的核心是存储元件——触发器。

### 时序电路的基本概念

**时钟信号（Clock）**：

```
时钟是时序电路的心跳，控制电路的状态变化时刻

     ┌───┐   ┌───┐   ┌───┐
CLK  │   │   │   │   │   │
   ──┘   └───┘   └───┘   └───

关键参数：
- 频率（Frequency）：每秒钟的周期数
- 周期（Period）：一个完整周期的时间
- 占空比（Duty Cycle）：高电平时间占周期的比例
- 上升沿（Rising Edge）：从低到高的跳变
- 下降沿（Falling Edge）：从高到低的跳变
```

**同步与异步**：

```
同步电路：
- 所有触发器共用同一个时钟
- 状态变化发生在时钟沿
- 易于设计和分析
- 现代数字系统的主流

异步电路：
- 没有统一的时钟
- 状态变化由输入信号直接触发
- 设计复杂，但速度可能更快
- 用于特殊场合
```


### 触发器类型

#### 1. SR锁存器（SR Latch）

SR锁存器是最基本的存储单元，有置位（Set）和复位（Reset）两个输入。

**逻辑表达式**：
```
Q = S + R' · Q
Q' = R + S' · Q'
```

**真值表**：

| S | R | Q(next) | 说明 |
|---|---|---------|------|
| 0 | 0 | Q(保持) | 保持当前状态 |
| 0 | 1 | 0       | 复位 |
| 1 | 0 | 1       | 置位 |
| 1 | 1 | X       | 禁止状态 |

**C语言模拟**：

```c
/**
 * @brief  SR锁存器状态
 */
typedef struct {
    uint8_t Q;      // 输出Q
    uint8_t Q_bar;  // 输出Q'
} sr_latch_t;

/**
 * @brief  SR锁存器更新
 * @param  latch: 锁存器状态
 * @param  S: 置位输入
 * @param  R: 复位输入
 */
void sr_latch_update(sr_latch_t *latch, uint8_t S, uint8_t R) {
    if (S && R) {
        // 禁止状态，不更新
        printf("Warning: S=1, R=1 is forbidden!\n");
        return;
    }
    
    if (S) {
        latch->Q = 1;
        latch->Q_bar = 0;
    } else if (R) {
        latch->Q = 0;
        latch->Q_bar = 1;
    }
    // S=0, R=0时保持不变
}
```

#### 2. D触发器（D Flip-Flop）

D触发器是最常用的触发器，在时钟沿到来时将D输入的值存储到Q输出。

**特性表**：

| CLK | D | Q(next) |
|-----|---|---------|
| ↑   | 0 | 0       |
| ↑   | 1 | 1       |
| 0/1 | X | Q(保持) |

**C语言模拟**：

```c
/**
 * @brief  D触发器状态
 */
typedef struct {
    uint8_t Q;          // 输出Q
    uint8_t clk_prev;   // 上一次时钟状态
} d_flipflop_t;

/**
 * @brief  D触发器初始化
 */
void d_flipflop_init(d_flipflop_t *ff) {
    ff->Q = 0;
    ff->clk_prev = 0;
}

/**
 * @brief  D触发器更新（上升沿触发）
 * @param  ff: 触发器状态
 * @param  D: 数据输入
 * @param  clk: 时钟输入
 */
void d_flipflop_update(d_flipflop_t *ff, uint8_t D, uint8_t clk) {
    // 检测上升沿
    if (clk && !ff->clk_prev) {
        ff->Q = D;  // 在上升沿锁存D的值
    }
    ff->clk_prev = clk;
}

// 使用示例
void d_flipflop_example(void) {
    d_flipflop_t ff;
    d_flipflop_init(&ff);
    
    printf("D Flip-Flop Simulation:\n");
    printf("CLK | D | Q\n");
    printf("----+---+---\n");
    
    // 模拟时钟序列
    uint8_t clk_seq[] = {0, 1, 0, 1, 0, 1, 0, 1};
    uint8_t d_seq[]   = {1, 1, 0, 0, 1, 1, 0, 0};
    
    for (int i = 0; i < 8; i++) {
        d_flipflop_update(&ff, d_seq[i], clk_seq[i]);
        printf(" %d  | %d | %d\n", clk_seq[i], d_seq[i], ff.Q);
    }
}
```

**应用场景**：
- 数据寄存：暂存数据
- 移位寄存器：串行数据传输
- 计数器：实现各种计数功能
- 状态机：存储状态信息

#### 3. JK触发器（JK Flip-Flop）

JK触发器是SR触发器的改进版本，消除了禁止状态。

**特性表**：

| CLK | J | K | Q(next) | 说明 |
|-----|---|---|---------|------|
| ↑   | 0 | 0 | Q       | 保持 |
| ↑   | 0 | 1 | 0       | 复位 |
| ↑   | 1 | 0 | 1       | 置位 |
| ↑   | 1 | 1 | Q'      | 翻转 |

**C语言模拟**：

```c
/**
 * @brief  JK触发器状态
 */
typedef struct {
    uint8_t Q;
    uint8_t clk_prev;
} jk_flipflop_t;

/**
 * @brief  JK触发器更新
 */
void jk_flipflop_update(jk_flipflop_t *ff, uint8_t J, uint8_t K, uint8_t clk) {
    if (clk && !ff->clk_prev) {  // 上升沿
        if (J && K) {
            ff->Q = !ff->Q;  // 翻转
        } else if (J) {
            ff->Q = 1;       // 置位
        } else if (K) {
            ff->Q = 0;       // 复位
        }
        // J=0, K=0时保持
    }
    ff->clk_prev = clk;
}
```

#### 4. T触发器（T Flip-Flop）

T触发器在T=1时翻转状态，T=0时保持状态。

**特性表**：

| CLK | T | Q(next) |
|-----|---|---------|
| ↑   | 0 | Q       |
| ↑   | 1 | Q'      |

**C语言模拟**：

```c
/**
 * @brief  T触发器更新
 */
void t_flipflop_update(d_flipflop_t *ff, uint8_t T, uint8_t clk) {
    if (clk && !ff->clk_prev) {  // 上升沿
        if (T) {
            ff->Q = !ff->Q;  // 翻转
        }
    }
    ff->clk_prev = clk;
}
```

**应用场景**：
- 分频器：将时钟频率除以2
- 计数器：实现二进制计数


### 时序电路应用

#### 1. 寄存器（Register）

寄存器是由多个D触发器组成的，用于存储多位数据。

**8位寄存器实现**：

```c
/**
 * @brief  8位寄存器
 */
typedef struct {
    uint8_t data;       // 存储的数据
    uint8_t clk_prev;   // 上一次时钟状态
} register_8bit_t;

/**
 * @brief  寄存器初始化
 */
void register_init(register_8bit_t *reg) {
    reg->data = 0;
    reg->clk_prev = 0;
}

/**
 * @brief  寄存器更新
 * @param  reg: 寄存器
 * @param  input: 输入数据
 * @param  clk: 时钟信号
 * @param  enable: 使能信号（1=允许写入，0=保持）
 */
void register_update(register_8bit_t *reg, uint8_t input, 
                     uint8_t clk, uint8_t enable) {
    if (clk && !reg->clk_prev && enable) {
        reg->data = input;
    }
    reg->clk_prev = clk;
}

// 使用示例
void register_example(void) {
    register_8bit_t reg;
    register_init(&reg);
    
    printf("8-bit Register Simulation:\n");
    printf("CLK | EN | Input | Output\n");
    printf("----+----+-------+-------\n");
    
    // 模拟写入序列
    uint8_t clk_seq[] = {0, 1, 0, 1, 0, 1, 0, 1};
    uint8_t en_seq[]  = {1, 1, 1, 1, 0, 0, 1, 1};
    uint8_t in_seq[]  = {0xAA, 0xAA, 0xBB, 0xBB, 0xCC, 0xCC, 0xDD, 0xDD};
    
    for (int i = 0; i < 8; i++) {
        register_update(&reg, in_seq[i], clk_seq[i], en_seq[i]);
        printf(" %d  | %d  | 0x%02X  | 0x%02X\n", 
               clk_seq[i], en_seq[i], in_seq[i], reg.data);
    }
}
```

#### 2. 移位寄存器（Shift Register）

移位寄存器可以将数据左移或右移，用于串并转换。

**4位移位寄存器**：

```c
/**
 * @brief  4位移位寄存器
 */
typedef struct {
    uint8_t data;       // 4位数据
    uint8_t clk_prev;
} shift_register_4bit_t;

/**
 * @brief  移位寄存器初始化
 */
void shift_register_init(shift_register_4bit_t *sr) {
    sr->data = 0;
    sr->clk_prev = 0;
}

/**
 * @brief  右移操作
 * @param  sr: 移位寄存器
 * @param  serial_in: 串行输入（从左边移入）
 * @param  clk: 时钟信号
 */
void shift_register_right(shift_register_4bit_t *sr, 
                          uint8_t serial_in, uint8_t clk) {
    if (clk && !sr->clk_prev) {
        sr->data = (sr->data >> 1) | ((serial_in & 0x01) << 3);
        sr->data &= 0x0F;  // 保持4位
    }
    sr->clk_prev = clk;
}

/**
 * @brief  左移操作
 */
void shift_register_left(shift_register_4bit_t *sr, 
                         uint8_t serial_in, uint8_t clk) {
    if (clk && !sr->clk_prev) {
        sr->data = ((sr->data << 1) | (serial_in & 0x01)) & 0x0F;
    }
    sr->clk_prev = clk;
}

// 使用示例
void shift_register_example(void) {
    shift_register_4bit_t sr;
    shift_register_init(&sr);
    
    printf("4-bit Shift Register (Right Shift):\n");
    printf("CLK | Serial_In | Data (binary)\n");
    printf("----+-----------+--------------\n");
    
    uint8_t clk_seq[] = {0, 1, 0, 1, 0, 1, 0, 1};
    uint8_t in_seq[]  = {1, 1, 0, 0, 1, 1, 0, 0};
    
    for (int i = 0; i < 8; i++) {
        shift_register_right(&sr, in_seq[i], clk_seq[i]);
        printf(" %d  |     %d     | ", clk_seq[i], in_seq[i]);
        for (int j = 3; j >= 0; j--) {
            printf("%d", (sr.data >> j) & 0x01);
        }
        printf("\n");
    }
}
```

**应用场景**：
- 串并转换：将串行数据转换为并行数据
- 并串转换：将并行数据转换为串行数据
- 延迟线：延迟数据若干个时钟周期
- LED驱动：级联驱动多个LED

#### 3. 计数器（Counter）

计数器是时序电路的重要应用，可以实现各种计数功能。

**4位二进制计数器**：

```c
/**
 * @brief  4位二进制计数器
 */
typedef struct {
    uint8_t count;      // 计数值（0-15）
    uint8_t clk_prev;
} counter_4bit_t;

/**
 * @brief  计数器初始化
 */
void counter_init(counter_4bit_t *cnt) {
    cnt->count = 0;
    cnt->clk_prev = 0;
}

/**
 * @brief  计数器更新（上升沿加1）
 * @param  cnt: 计数器
 * @param  clk: 时钟信号
 * @param  reset: 复位信号（1=复位）
 * @param  enable: 使能信号（1=计数，0=保持）
 */
void counter_update(counter_4bit_t *cnt, uint8_t clk, 
                    uint8_t reset, uint8_t enable) {
    if (reset) {
        cnt->count = 0;
    } else if (clk && !cnt->clk_prev && enable) {
        cnt->count = (cnt->count + 1) & 0x0F;  // 模16计数
    }
    cnt->clk_prev = clk;
}

/**
 * @brief  模N计数器
 */
void counter_mod_n(counter_4bit_t *cnt, uint8_t clk, 
                   uint8_t reset, uint8_t enable, uint8_t modulo) {
    if (reset) {
        cnt->count = 0;
    } else if (clk && !cnt->clk_prev && enable) {
        cnt->count++;
        if (cnt->count >= modulo) {
            cnt->count = 0;
        }
    }
    cnt->clk_prev = clk;
}

// 使用示例
void counter_example(void) {
    counter_4bit_t cnt;
    counter_init(&cnt);
    
    printf("4-bit Binary Counter:\n");
    printf("CLK | Count (dec) | Count (bin)\n");
    printf("----+-------------+------------\n");
    
    for (int i = 0; i < 20; i++) {
        uint8_t clk = i % 2;  // 生成时钟
        counter_update(&cnt, clk, 0, 1);
        
        if (clk) {  // 只在上升沿后打印
            printf(" %d  |     %2d      | ", clk, cnt.count);
            for (int j = 3; j >= 0; j--) {
                printf("%d", (cnt.count >> j) & 0x01);
            }
            printf("\n");
        }
    }
}
```

**应用场景**：
- 分频器：产生低频时钟
- 定时器：实现定时功能
- 地址生成：产生顺序地址
- 状态机：实现状态计数


## 第五部分：时序分析基础

### 时序参数

在设计时序电路时，必须考虑以下关键时序参数：

**1. 建立时间（Setup Time, tsu）**：

```
数据在时钟沿到来之前必须保持稳定的最小时间

     数据 ────┐         ┌────
              │  稳定   │
              └─────────┘
                 ↑
                tsu
                 ↑
     时钟 ───────┘ └─────────
```

**2. 保持时间（Hold Time, th）**：

```
数据在时钟沿到来之后必须保持稳定的最小时间

     数据 ────────┐         ┌
                  │  稳定   │
                  └─────────┘
                  ↑
                  th
                  ↑
     时钟 ────────┘ └────────
```

**3. 传播延迟（Propagation Delay, tpd）**：

```
从时钟沿到输出稳定的时间

     时钟 ────┐   ┌────
              │   │
              └───┘
              ↑
              │←─ tpd ─→│
              │         ↑
     输出 ─────X─────────┐
                         │
                         └────
```

**4. 时钟周期约束**：

```
时钟周期必须满足：
Tclk ≥ tpd(FF1) + tlogic + tsu(FF2)

其中：
- tpd(FF1)：第一个触发器的传播延迟
- tlogic：组合逻辑延迟
- tsu(FF2)：第二个触发器的建立时间
```

**时序分析示例**：

```c
/**
 * @brief  时序参数定义
 */
typedef struct {
    float t_setup;      // 建立时间（ns）
    float t_hold;       // 保持时间（ns）
    float t_prop;       // 传播延迟（ns）
    float t_clk_to_q;   // 时钟到输出延迟（ns）
} timing_params_t;

/**
 * @brief  计算最大时钟频率
 * @param  params: 时序参数
 * @param  t_logic: 组合逻辑延迟（ns）
 * @retval 最大时钟频率（MHz）
 */
float calculate_max_frequency(timing_params_t *params, float t_logic) {
    // 最小时钟周期 = tclk_to_q + tlogic + tsetup
    float t_min = params->t_clk_to_q + t_logic + params->t_setup;
    
    // 最大频率 = 1 / 最小周期
    float f_max = 1000.0 / t_min;  // MHz
    
    printf("时序分析：\n");
    printf("  时钟到输出延迟: %.2f ns\n", params->t_clk_to_q);
    printf("  组合逻辑延迟: %.2f ns\n", t_logic);
    printf("  建立时间: %.2f ns\n", params->t_setup);
    printf("  最小时钟周期: %.2f ns\n", t_min);
    printf("  最大时钟频率: %.2f MHz\n", f_max);
    
    return f_max;
}

// 使用示例
void timing_analysis_example(void) {
    timing_params_t params = {
        .t_setup = 0.5,      // 0.5ns
        .t_hold = 0.3,       // 0.3ns
        .t_prop = 1.0,       // 1.0ns
        .t_clk_to_q = 0.8    // 0.8ns
    };
    
    float t_logic = 2.0;  // 组合逻辑延迟2ns
    
    float f_max = calculate_max_frequency(&params, t_logic);
    // 输出：最大时钟频率约303 MHz
}
```

### 亚稳态（Metastability）

当输入信号在建立时间或保持时间窗口内变化时，触发器可能进入亚稳态。

**亚稳态特征**：
```
- 输出电压处于不确定状态（既不是0也不是1）
- 输出可能振荡
- 最终会稳定到0或1，但时间不确定
- 可能导致系统错误
```

**避免亚稳态的方法**：

```c
/**
 * @brief  双触发器同步器（防止亚稳态）
 * 
 * 异步信号 ──→ [FF1] ──→ [FF2] ──→ 同步信号
 *               ↑         ↑
 *              CLK       CLK
 * 
 * 原理：
 * - FF1可能进入亚稳态
 * - FF2有一个完整时钟周期来稳定
 * - 大大降低亚稳态传播的概率
 */
typedef struct {
    uint8_t ff1_q;
    uint8_t ff2_q;
    uint8_t clk_prev;
} synchronizer_t;

void synchronizer_init(synchronizer_t *sync) {
    sync->ff1_q = 0;
    sync->ff2_q = 0;
    sync->clk_prev = 0;
}

void synchronizer_update(synchronizer_t *sync, 
                         uint8_t async_input, uint8_t clk) {
    if (clk && !sync->clk_prev) {
        sync->ff2_q = sync->ff1_q;  // FF2锁存FF1的输出
        sync->ff1_q = async_input;   // FF1锁存异步输入
    }
    sync->clk_prev = clk;
}

uint8_t synchronizer_output(synchronizer_t *sync) {
    return sync->ff2_q;  // 输出经过两级同步的信号
}
```

**最佳实践**：
- 异步信号必须经过同步器
- 使用两级或三级触发器同步
- 关键信号可以使用更多级
- 注意同步器引入的延迟


## 第六部分：实际应用与设计技巧

### 1. 按键消抖电路

机械按键在按下和释放时会产生抖动，需要消抖处理。

**硬件消抖（SR锁存器）**：

```
按键按下时，通过SR锁存器锁定状态，避免抖动影响

     VCC
      │
      ├─── 按键 ──┬── R ──┐
      │           │       │
     10kΩ        10kΩ    SR锁存器
      │           │       │
     GND         GND     输出
```

**软件消抖**：

```c
/**
 * @brief  按键消抖状态机
 */
typedef enum {
    KEY_IDLE,           // 空闲状态
    KEY_PRESS_DEBOUNCE, // 按下消抖
    KEY_PRESSED,        // 已按下
    KEY_RELEASE_DEBOUNCE // 释放消抖
} key_state_t;

typedef struct {
    key_state_t state;
    uint16_t counter;
    uint8_t key_value;
} key_debounce_t;

#define DEBOUNCE_TIME_MS  20  // 消抖时间20ms

/**
 * @brief  按键消抖处理（每1ms调用一次）
 * @param  key: 按键状态
 * @param  key_input: 当前按键输入（0=按下，1=释放）
 * @retval 稳定的按键值
 */
uint8_t key_debounce_process(key_debounce_t *key, uint8_t key_input) {
    switch (key->state) {
        case KEY_IDLE:
            if (key_input == 0) {  // 检测到按下
                key->state = KEY_PRESS_DEBOUNCE;
                key->counter = 0;
            }
            break;
            
        case KEY_PRESS_DEBOUNCE:
            if (key_input == 0) {
                key->counter++;
                if (key->counter >= DEBOUNCE_TIME_MS) {
                    key->state = KEY_PRESSED;
                    key->key_value = 1;  // 确认按下
                }
            } else {
                key->state = KEY_IDLE;  // 误触发
            }
            break;
            
        case KEY_PRESSED:
            if (key_input == 1) {  // 检测到释放
                key->state = KEY_RELEASE_DEBOUNCE;
                key->counter = 0;
            }
            break;
            
        case KEY_RELEASE_DEBOUNCE:
            if (key_input == 1) {
                key->counter++;
                if (key->counter >= DEBOUNCE_TIME_MS) {
                    key->state = KEY_IDLE;
                    key->key_value = 0;  // 确认释放
                }
            } else {
                key->state = KEY_PRESSED;  // 误触发
            }
            break;
    }
    
    return key->key_value;
}
```


### 2. 分频器设计

分频器用于产生低频时钟信号。

**2分频器（T触发器）**：

```c
/**
 * @brief  2分频器
 * 使用T触发器实现，每个时钟沿翻转一次
 */
typedef struct {
    uint8_t output;
    uint8_t clk_prev;
} divider_by_2_t;

void divider_by_2_update(divider_by_2_t *div, uint8_t clk) {
    if (clk && !div->clk_prev) {
        div->output = !div->output;  // 翻转
    }
    div->clk_prev = clk;
}
```

**任意分频器**：

```c
/**
 * @brief  N分频器
 * @param  N: 分频系数
 */
typedef struct {
    uint16_t count;
    uint16_t modulo;
    uint8_t output;
    uint8_t clk_prev;
} divider_by_n_t;

void divider_by_n_init(divider_by_n_t *div, uint16_t N) {
    div->count = 0;
    div->modulo = N;
    div->output = 0;
    div->clk_prev = 0;
}

void divider_by_n_update(divider_by_n_t *div, uint8_t clk) {
    if (clk && !div->clk_prev) {
        div->count++;
        if (div->count >= div->modulo) {
            div->count = 0;
            div->output = !div->output;  // 翻转输出
        }
    }
    div->clk_prev = clk;
}

// 使用示例：10分频器
void divider_example(void) {
    divider_by_n_t div;
    divider_by_n_init(&div, 10);
    
    printf("10分频器输出：\n");
    for (int i = 0; i < 40; i++) {
        uint8_t clk = i % 2;
        divider_by_n_update(&div, clk);
        if (clk) {
            printf("输入时钟%2d, 输出=%d\n", i/2, div.output);
        }
    }
}
```

### 3. 脉冲展宽电路

将短脉冲展宽为较长的脉冲。

```c
/**
 * @brief  脉冲展宽器
 * @param  width: 展宽时间（时钟周期数）
 */
typedef struct {
    uint16_t counter;
    uint16_t width;
    uint8_t output;
    uint8_t clk_prev;
} pulse_extender_t;

void pulse_extender_init(pulse_extender_t *ext, uint16_t width) {
    ext->counter = 0;
    ext->width = width;
    ext->output = 0;
    ext->clk_prev = 0;
}

void pulse_extender_update(pulse_extender_t *ext, 
                           uint8_t pulse_in, uint8_t clk) {
    if (clk && !ext->clk_prev) {
        if (pulse_in) {
            ext->counter = ext->width;  // 检测到脉冲，重新计数
            ext->output = 1;
        } else if (ext->counter > 0) {
            ext->counter--;
            if (ext->counter == 0) {
                ext->output = 0;  // 计数结束，输出归零
            }
        }
    }
    ext->clk_prev = clk;
}
```

### 4. 边沿检测电路

检测信号的上升沿或下降沿。

```c
/**
 * @brief  边沿检测器
 */
typedef struct {
    uint8_t prev_value;
    uint8_t clk_prev;
} edge_detector_t;

void edge_detector_init(edge_detector_t *det) {
    det->prev_value = 0;
    det->clk_prev = 0;
}

/**
 * @brief  上升沿检测
 * @retval 1=检测到上升沿，0=无上升沿
 */
uint8_t detect_rising_edge(edge_detector_t *det, 
                           uint8_t signal, uint8_t clk) {
    uint8_t rising_edge = 0;
    
    if (clk && !det->clk_prev) {
        if (signal && !det->prev_value) {
            rising_edge = 1;  // 检测到上升沿
        }
        det->prev_value = signal;
    }
    det->clk_prev = clk;
    
    return rising_edge;
}

/**
 * @brief  下降沿检测
 */
uint8_t detect_falling_edge(edge_detector_t *det, 
                            uint8_t signal, uint8_t clk) {
    uint8_t falling_edge = 0;
    
    if (clk && !det->clk_prev) {
        if (!signal && det->prev_value) {
            falling_edge = 1;  // 检测到下降沿
        }
        det->prev_value = signal;
    }
    det->clk_prev = clk;
    
    return falling_edge;
}
```


## 总结

本文系统介绍了数字电路的基础知识，包括逻辑门和时序电路。

### 核心要点

1. **基本逻辑门**：
   - AND、OR、NOT：基本运算
   - NAND、NOR：功能完备
   - XOR、XNOR：比较和校验

2. **组合逻辑电路**：
   - 输出只取决于当前输入
   - 加法器、多路选择器、译码器
   - 无记忆功能

3. **时序逻辑电路**：
   - 输出取决于当前输入和历史状态
   - 触发器是基本存储单元
   - 寄存器、计数器、移位寄存器

4. **时序分析**：
   - 建立时间和保持时间
   - 传播延迟
   - 亚稳态问题

### 设计原则

1. **组合逻辑设计**：
   - 化简逻辑表达式
   - 减少门延迟
   - 避免竞争冒险

2. **时序逻辑设计**：
   - 同步设计优先
   - 注意时序约束
   - 异步信号必须同步

3. **实际应用**：
   - 按键消抖
   - 时钟分频
   - 边沿检测

### 最佳实践

1. **逻辑门使用**：
   - 优先使用NAND/NOR（工艺优势）
   - 注意扇出限制
   - 考虑传播延迟

2. **触发器使用**：
   - D触发器最常用
   - 统一使用上升沿或下降沿
   - 添加复位功能

3. **时序设计**：
   - 满足时序约束
   - 使用同步器处理异步信号
   - 避免组合逻辑环路

## 延伸阅读

推荐进一步学习的内容：

1. **进阶主题**：
   - [FPGA开发入门](../advanced/03-fpga-basics.html)
   - [Verilog硬件描述语言](../advanced/04-verilog-intro.html)
   - [状态机设计](../advanced/05-state-machine.html)

2. **相关知识**：
   - [嵌入式电路基础：电阻、电容、电感](01-basic-components.html)
   - [PCB设计入门：从原理图到PCB](02-pcb-design-intro.html)
   - [信号完整性分析基础](../intermediate/01-signal-integrity.html)

3. **实践项目**：
   - 数字时钟设计
   - 交通灯控制器

## 参考资料

1. 《数字电子技术基础》- 阎石
2. 《数字设计原理与实践》- John F. Wakerly
3. 《Digital Design》- M. Morris Mano
4. 《FPGA原理与应用》- 王金明

---

**练习题**：

1. 使用基本逻辑门实现以下功能：
   - 三输入多数表决器（输出为多数输入的值）
   - 4位奇偶校验生成器
   - 2-4译码器

2. 设计一个模10计数器：
   - 使用D触发器实现
   - 添加异步复位功能
   - 添加使能控制

3. 分析以下电路的时序：
   - 时钟频率：100MHz
   - 触发器tclk_to_q：0.5ns
   - 组合逻辑延迟：3ns
   - 建立时间：0.3ns
   - 计算最大工作频率

4. 设计一个按键检测电路：
   - 检测按键按下事件
   - 实现消抖功能
   - 输出单脉冲信号

**实践任务**：

1. 使用C语言模拟一个4位全加器
2. 实现一个8位移位寄存器
3. 设计一个60进制计数器（秒计数）
4. 实现一个简单的状态机（红绿灯控制）

**下一步**：建议学习 [电源电路设计：LDO与DC-DC选择](04-power-supply-design.html)，了解如何为数字电路提供稳定的电源。

---

**常见问题解答**：

**Q: 为什么NAND门和NOR门被称为"功能完备"？**

A: 因为可以仅使用NAND门或NOR门实现所有其他逻辑门：
- NOT: A NAND A = A'
- AND: (A NAND B) NAND (A NAND B) = A · B
- OR: (A NAND A) NAND (B NAND B) = A + B

这使得它们在IC设计中非常重要。

**Q: 什么时候会发生亚稳态？如何避免？**

A: 亚稳态发生在：
- 输入信号在建立时间或保持时间窗口内变化
- 异步信号直接连接到触发器

避免方法：
- 使用双触发器同步器
- 确保满足时序约束
- 关键信号使用三级同步

**Q: 组合逻辑和时序逻辑有什么区别？**

A: 主要区别：
- 组合逻辑：输出只取决于当前输入，无记忆
- 时序逻辑：输出取决于当前输入和历史状态，有记忆

实际应用中，大多数电路都是两者的结合。

**Q: 如何选择时钟频率？**

A: 考虑因素：
- 满足时序约束（建立时间、保持时间）
- 功耗要求（频率越高功耗越大）
- 系统性能需求
- 时钟分配网络的限制

通常留有20%-30%的时序余量。
