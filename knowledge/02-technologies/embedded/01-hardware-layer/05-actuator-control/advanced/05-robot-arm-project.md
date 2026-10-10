---
title: "四自由度机械臂：运动学与轨迹控制"
description: "完整的四自由度串联机械臂项目，涵盖DH参数建模、正逆运动学推导、奇异性分析、关节空间与笛卡尔空间轨迹规划，以及基于STM32的视觉引导抓取实现"
slug: "four-dof-robot-arm-project"

domain: "底层硬件层"
module: "执行器控制"
content_type: "project"
skill_level: "advanced"

tags:
  - 机械臂
  - 运动学
  - 逆运动学
  - 舵机控制
  - 轨迹规划
  - 机器人
  - DH参数
  - 视觉引导
prerequisites:
  - "beginner/03-servo-motor-control"
  - "advanced/02-motion-control-algorithms"
related_contents:
  - "advanced/04-smart-gimbal-project"
  - "advanced/06-hexapod-robot"

estimated_time: 360
difficulty_score: 5

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "2.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: true
is_premium: false

keywords:
  - 四自由度机械臂
  - 机械臂运动学
  - 逆运动学
  - 机械臂控制
  - 舵机机械臂
  - DH参数
  - 视觉抓取
cover_image: ""
---

# 四自由度机械臂：运动学与轨迹控制

## 概述

本项目实现一个四自由度（4-DOF）串联机械臂的完整控制系统，从理论建模到实际抓取任务。读者将学习：

| 学习目标 | 难度 | 预计时间 |
|---------|------|---------|
| DH参数建模与齐次变换矩阵 | ★★★★☆ | 60分钟 |
| 几何法正逆运动学推导 | ★★★★☆ | 60分钟 |
| 工作空间分析与奇异性处理 | ★★★★★ | 45分钟 |
| 关节空间与笛卡尔空间轨迹规划 | ★★★★☆ | 45分钟 |
| 视觉引导抓取系统集成 | ★★★★★ | 90分钟 |

**前置知识**：三角函数、矩阵运算、STM32 PWM输出、基础C语言

**硬件清单（BOM）**：

| 器件 | 型号 | 数量 | 参考价格 | 购买渠道 |
|------|------|------|---------|---------|
| 主控 | STM32F103C8T6 | 1 | ¥15 | 立创商城 |
| 底座舵机 | MG996R (11kg·cm) | 1 | ¥18 | 淘宝 |
| 大臂舵机 | MG996R (11kg·cm) | 1 | ¥18 | 淘宝 |
| 小臂舵机 | MG996R (11kg·cm) | 1 | ¥18 | 淘宝 |
| 末端舵机 | SG90 (1.8kg·cm) | 1 | ¥5 | 淘宝 |
| 夹爪舵机 | SG90 (1.8kg·cm) | 1 | ¥5 | 淘宝 |
| 舵机电源 | 5V/5A开关电源 | 1 | ¥25 | 淘宝 |
| 机械臂套件 | 铝合金4DOF（LeArm兼容） | 1 | ¥120 | 淘宝 |
| 摄像头（可选） | OV7670 或 ESP32-CAM | 1 | ¥15 | 淘宝 |
| 逻辑电平转换 | TXS0108E | 1 | ¥3 | 立创商城 |

**连杆参数**（需根据实际机械臂测量）：

```
L0 = 80mm（底座高度，J1轴到地面）
L1 = 105mm（大臂长度，J2轴到J3轴）
L2 = 100mm（小臂长度，J3轴到J4轴）
L3 = 65mm（末端长度，J4轴到夹爪中心）
```

## 背景知识

### 机器人运动学基础

机械臂运动学（Kinematics）研究关节角度与末端位置/姿态之间的映射关系，不涉及力和质量。分为两类：

- **正运动学（Forward Kinematics, FK）**：已知关节角度 → 求末端位姿
- **逆运动学（Inverse Kinematics, IK）**：已知末端位姿 → 求关节角度

```
正运动学（唯一解）：
  [θ1, θ2, θ3, θ4] ──FK──→ [x, y, z, φ]

逆运动学（可能多解或无解）：
  [x, y, z, φ] ──IK──→ [θ1, θ2, θ3, θ4]（肘上/肘下解）
```

### DH参数（Denavit-Hartenberg Parameters）

DH参数是描述串联机器人连杆关系的标准方法，由 Denavit 和 Hartenberg 于1955年提出。每个连杆用4个参数描述：

| 参数 | 符号 | 含义 |
|------|------|------|
| 连杆长度 | aᵢ | 沿 xᵢ 轴，从 zᵢ₋₁ 到 zᵢ 的距离 |
| 连杆扭角 | αᵢ | 绕 xᵢ 轴，从 zᵢ₋₁ 到 zᵢ 的转角 |
| 关节偏距 | dᵢ | 沿 zᵢ₋₁ 轴，从 xᵢ₋₁ 到 xᵢ 的距离 |
| 关节角度 | θᵢ | 绕 zᵢ₋₁ 轴，从 xᵢ₋₁ 到 xᵢ 的转角（**变量**） |

**4-DOF机械臂DH参数表**（标准DH约定）：

| 关节 i | aᵢ (mm) | αᵢ (°) | dᵢ (mm) | θᵢ (变量范围) |
|--------|---------|--------|---------|--------------|
| 1 | 0 | 90 | L0=80 | θ1 (−90°~+90°) |
| 2 | L1=105 | 0 | 0 | θ2 (0°~135°) |
| 3 | L2=100 | 0 | 0 | θ3 (−135°~0°) |
| 4 | L3=65 | 0 | 0 | θ4 (−90°~+90°) |

**DH坐标系建立规则**：

```
步骤1：确定各关节旋转轴 z₀, z₁, z₂, z₃
步骤2：确定公垂线方向作为 x 轴
步骤3：按右手定则确定 y 轴
步骤4：测量 a, α, d, θ 四个参数
```

### 齐次变换矩阵（Homogeneous Transformation Matrix）

每个连杆的变换矩阵 Tᵢ₋₁ᵢ 由DH参数构造：

```
        ┌ cos θᵢ   -sin θᵢ cos αᵢ    sin θᵢ sin αᵢ   aᵢ cos θᵢ ┐
Tᵢ₋₁ᵢ = │ sin θᵢ    cos θᵢ cos αᵢ   -cos θᵢ sin αᵢ   aᵢ sin θᵢ │
        │    0          sin αᵢ            cos αᵢ          dᵢ    │
        └    0             0                 0              1    ┘
```

末端相对于基座的变换矩阵：

```
T₀₄ = T₀₁ · T₁₂ · T₂₃ · T₃₄

T₀₄ = ┌ R₃ₓ₃  p₃ₓ₁ ┐
      └  0₁ₓ₃   1   ┘

其中 R 是3×3旋转矩阵，p = [x, y, z]ᵀ 是末端位置向量
```

**C语言实现4×4矩阵乘法**：

```c
// 4x4齐次变换矩阵（行主序存储）
typedef float Mat4[4][4];

// 矩阵乘法：C = A * B
void mat4_mul(const Mat4 A, const Mat4 B, Mat4 C) {
    Mat4 tmp = {0};
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            for (int k = 0; k < 4; k++)
                tmp[i][j] += A[i][k] * B[k][j];
    // 避免原地修改时的别名问题
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            C[i][j] = tmp[i][j];
}

// 根据DH参数构造单个连杆变换矩阵
// theta_deg: 关节角(度), d: 偏距(mm), a: 连杆长(mm), alpha_deg: 扭角(度)
void dh_matrix(float theta_deg, float d, float a, float alpha_deg, Mat4 T) {
    float th = theta_deg * M_PI / 180.0f;
    float al = alpha_deg * M_PI / 180.0f;
    float ct = cosf(th), st = sinf(th);
    float ca = cosf(al), sa = sinf(al);

    T[0][0] = ct;    T[0][1] = -st*ca;  T[0][2] = st*sa;   T[0][3] = a*ct;
    T[1][0] = st;    T[1][1] =  ct*ca;  T[1][2] = -ct*sa;  T[1][3] = a*st;
    T[2][0] = 0.0f;  T[2][1] = sa;      T[2][2] = ca;      T[2][3] = d;
    T[3][0] = 0.0f;  T[3][1] = 0.0f;   T[3][2] = 0.0f;    T[3][3] = 1.0f;
}
```

### 工作空间分析（Workspace Analysis）

机械臂的工作空间分为两类：

**可达工作空间（Reachable Workspace）**：末端能到达的所有点的集合（至少一种姿态可达）

**灵巧工作空间（Dexterous Workspace）**：末端能以任意姿态到达的点的集合（通常是可达空间的子集）

```
4-DOF机械臂工作空间示意（侧视图，J1=0°平面）：

        z
        │    ┌──────────────────────────────┐
   L0+  │    │  可达工作空间（环形区域）      │
        │    │  ┌──────────────────────┐    │
        │    │  │  灵巧工作空间（较小）  │    │
        │    │  └──────────────────────┘    │
   L0   ├────┼──────────────────────────────┼──── r
        │    │                              │
        │    └──────────────────────────────┘
        │
        0   |L1-L2-L3|        L1+L2+L3

最大伸展半径 = L1 + L2 + L3 = 105 + 100 + 65 = 270mm
最小收缩半径 = |L1 - L2 - L3| ≈ 0mm（可折叠）
```

**工作空间数值计算（Python验证脚本）**：

```python
import numpy as np
import matplotlib.pyplot as plt

L1, L2, L3 = 105, 100, 65  # mm

# 采样关节角度空间
theta2 = np.linspace(0, 135, 50)    # 大臂
theta3 = np.linspace(-135, 0, 50)   # 小臂
theta4 = np.linspace(-90, 90, 20)   # 末端

points = []
for t2 in theta2:
    for t3 in theta3:
        for t4 in theta4:
            a1 = np.radians(t2)
            a2 = np.radians(t3)
            a3 = np.radians(t4)
            r = (L1*np.cos(a1) + L2*np.cos(a1+a2)
                 + L3*np.cos(a1+a2+a3))
            z = (L1*np.sin(a1) + L2*np.sin(a1+a2)
                 + L3*np.sin(a1+a2+a3))
            points.append((r, z))

r_vals, z_vals = zip(*points)
plt.scatter(r_vals, z_vals, s=0.1, alpha=0.3)
plt.xlabel('水平距离 r (mm)')
plt.ylabel('高度 z (mm)')
plt.title('4-DOF机械臂可达工作空间（侧视图）')
plt.axis('equal')
plt.savefig('workspace.png', dpi=150)
```

### 机械臂与其他运动系统对比

| 特性 | 4-DOF串联臂 | 6-DOF串联臂 | Delta并联臂 | SCARA |
|------|------------|------------|------------|-------|
| 自由度 | 4 | 6 | 3 | 4 |
| 末端姿态控制 | 部分（1轴） | 完整（3轴） | 无旋转 | 平面+旋转 |
| 工作空间 | 中等 | 大 | 小（圆柱） | 大（平面） |
| 奇异性 | 少 | 多 | 少 | 少 |
| 控制复杂度 | 中 | 高 | 中 | 低 |
| 典型应用 | 教学/小型抓取 | 工业焊接/装配 | 高速分拣 | PCB贴片 |
| 成本 | ¥200~500 | ¥5000+ | ¥1000+ | ¥2000+ |

## 核心内容

### 正运动学（Forward Kinematics）

基于DH矩阵的完整正运动学实现：

```c
#include <math.h>
#include <string.h>

#define L0  80.0f   // 底座高度(mm)
#define L1  105.0f  // 大臂长度(mm)
#define L2  100.0f  // 小臂长度(mm)
#define L3  65.0f   // 末端长度(mm)
#define DEG2RAD  (3.14159265358979f / 180.0f)
#define RAD2DEG  (180.0f / 3.14159265358979f)

typedef float Mat4[4][4];

typedef struct {
    float x, y, z;      // 末端位置(mm)
    float roll;          // 绕x轴旋转(度)，本臂固定为0
    float pitch;         // 绕y轴旋转(度)
    float yaw;           // 绕z轴旋转(度)
} EndEffectorPose;

typedef struct {
    float j1;  // 底座旋转(度)，范围 -90~+90
    float j2;  // 大臂俯仰(度)，范围 0~135
    float j3;  // 小臂俯仰(度)，范围 -135~0
    float j4;  // 末端俯仰(度)，范围 -90~+90
} JointAngles;

// DH矩阵构造（见背景知识章节）
static void dh_matrix(float theta_deg, float d,
                      float a, float alpha_deg, Mat4 T) {
    float th = theta_deg * DEG2RAD;
    float al = alpha_deg * DEG2RAD;
    float ct = cosf(th), st = sinf(th);
    float ca = cosf(al), sa = sinf(al);
    T[0][0]=ct;    T[0][1]=-st*ca; T[0][2]=st*sa;  T[0][3]=a*ct;
    T[1][0]=st;    T[1][1]=ct*ca;  T[1][2]=-ct*sa; T[1][3]=a*st;
    T[2][0]=0.0f;  T[2][1]=sa;     T[2][2]=ca;     T[2][3]=d;
    T[3][0]=0.0f;  T[3][1]=0.0f;   T[3][2]=0.0f;   T[3][3]=1.0f;
}

static void mat4_mul(const Mat4 A, const Mat4 B, Mat4 C) {
    Mat4 tmp;
    memset(tmp, 0, sizeof(tmp));
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            for (int k = 0; k < 4; k++)
                tmp[i][j] += A[i][k] * B[k][j];
    memcpy(C, tmp, sizeof(Mat4));
}

// 完整正运动学：输入关节角度，输出末端位姿
EndEffectorPose forward_kinematics(const JointAngles *q) {
    Mat4 T01, T12, T23, T34, T02, T03, T04;

    // 按DH参数表构造各连杆矩阵
    // 关节1：θ1变量，d=L0，a=0，α=90°
    dh_matrix(q->j1, L0, 0.0f, 90.0f, T01);
    // 关节2：θ2变量，d=0，a=L1，α=0°
    dh_matrix(q->j2, 0.0f, L1, 0.0f, T12);
    // 关节3：θ3变量，d=0，a=L2，α=0°
    dh_matrix(q->j3, 0.0f, L2, 0.0f, T23);
    // 关节4：θ4变量，d=0，a=L3，α=0°
    dh_matrix(q->j4, 0.0f, L3, 0.0f, T34);

    mat4_mul(T01, T12, T02);
    mat4_mul(T02, T23, T03);
    mat4_mul(T03, T34, T04);

    EndEffectorPose pose;
    pose.x = T04[0][3];
    pose.y = T04[1][3];
    pose.z = T04[2][3];
    // 从旋转矩阵提取欧拉角（ZYX约定）
    pose.yaw   = atan2f(T04[1][0], T04[0][0]) * RAD2DEG;
    pose.pitch = atan2f(-T04[2][0],
                  sqrtf(T04[2][1]*T04[2][1] + T04[2][2]*T04[2][2])) * RAD2DEG;
    pose.roll  = atan2f(T04[2][1], T04[2][2]) * RAD2DEG;
    return pose;
}
```

### 几何法逆运动学（Geometric IK）

几何法利用三角形余弦定理直接求解，计算量小，适合嵌入式实时控制：

```c
// IK求解结果
typedef struct {
    JointAngles q;      // 关节角度解
    int valid;          // 1=有效解，0=无解
    int elbow_up;       // 1=肘部向上解，0=肘部向下解
} IKResult;

// 关节限位检查
static int check_limits(const JointAngles *q) {
    if (q->j1 < -90.0f || q->j1 > 90.0f)  return 0;
    if (q->j2 <   0.0f || q->j2 > 135.0f) return 0;
    if (q->j3 < -135.0f|| q->j3 > 0.0f)   return 0;
    if (q->j4 < -90.0f || q->j4 > 90.0f)  return 0;
    return 1;
}

// 几何法IK：给定末端位置(x,y,z)和末端姿态角end_pitch(度)
// elbow_up=1求肘部向上解，=0求肘部向下解
IKResult inverse_kinematics(float x, float y, float z,
                             float end_pitch, int elbow_up) {
    IKResult result = {.valid = 0};

    // ── 步骤1：求J1（底座旋转角）──────────────────────────
    result.q.j1 = atan2f(y, x) * RAD2DEG;

    // ── 步骤2：计算腕部位置（去掉末端连杆L3的贡献）──────────
    float r_total = sqrtf(x*x + y*y);  // 水平投影距离
    float ep = end_pitch * DEG2RAD;
    float wx = r_total - L3 * cosf(ep);  // 腕部水平距离
    float wz = z - L0 - L3 * sinf(ep);  // 腕部高度（相对J2轴）

    // ── 步骤3：用余弦定理求J3 ─────────────────────────────
    float d2 = wx*wx + wz*wz;  // 腕部到J2轴距离的平方
    float d  = sqrtf(d2);

    // 可达性检查
    float reach_max = L1 + L2;
    float reach_min = fabsf(L1 - L2);
    if (d > reach_max + 1e-3f || d < reach_min - 1e-3f) {
        // 目标不可达
        return result;
    }
    // 夹紧到合法范围（浮点误差保护）
    float cos_j3 = (d2 - L1*L1 - L2*L2) / (2.0f * L1 * L2);
    cos_j3 = fmaxf(-1.0f, fminf(1.0f, cos_j3));

    float j3_abs = acosf(cos_j3) * RAD2DEG;  // 0~180°
    // 肘部向上：J3为负（小臂向后折）
    result.q.j3 = elbow_up ? -j3_abs : j3_abs;

    // ── 步骤4：求J2 ──────────────────────────────────────
    float alpha = atan2f(wz, wx);  // 腕部方向角
    float sin_j3 = sinf(result.q.j3 * DEG2RAD);
    float cos_j3v = cosf(result.q.j3 * DEG2RAD);
    // 用正弦定理辅助
    float beta = atan2f(L2 * sin_j3,
                        L1 + L2 * cos_j3v);
    result.q.j2 = (alpha - beta) * RAD2DEG;

    // ── 步骤5：求J4（末端姿态补偿）──────────────────────────
    result.q.j4 = end_pitch - result.q.j2 - result.q.j3;

    // 关节限位检查
    result.valid = check_limits(&result.q);
    result.elbow_up = elbow_up;
    return result;
}

// 自动选择最优解（优先肘部向上，关节角度变化最小）
IKResult ik_best_solution(float x, float y, float z,
                           float end_pitch,
                           const JointAngles *current) {
    IKResult up   = inverse_kinematics(x, y, z, end_pitch, 1);
    IKResult down = inverse_kinematics(x, y, z, end_pitch, 0);

    if (!up.valid && !down.valid) {
        IKResult none = {.valid = 0};
        return none;
    }
    if (!up.valid)   return down;
    if (!down.valid) return up;

    // 计算关节角度变化量（选变化最小的解）
    if (current == NULL) return up;  // 默认肘部向上

    float cost_up = fabsf(up.q.j1 - current->j1)
                  + fabsf(up.q.j2 - current->j2)
                  + fabsf(up.q.j3 - current->j3)
                  + fabsf(up.q.j4 - current->j4);
    float cost_down = fabsf(down.q.j1 - current->j1)
                    + fabsf(down.q.j2 - current->j2)
                    + fabsf(down.q.j3 - current->j3)
                    + fabsf(down.q.j4 - current->j4);
    return (cost_up <= cost_down) ? up : down;
}
```

### 舵机标定与驱动

```c
// 舵机标定参数（根据实际安装方向调整）
typedef struct {
    uint16_t pulse_min;   // 最小脉宽(us)，对应min_angle
    uint16_t pulse_max;   // 最大脉宽(us)，对应max_angle
    float    angle_min;   // 最小角度(度)
    float    angle_max;   // 最大角度(度)
    float    zero_offset; // 机械零位偏移(度)
    int8_t   direction;   // 方向：+1或-1
} ServoCalib;

// 5个舵机的标定参数（J1~J4 + 夹爪）
ServoCalib calib[5] = {
    {500, 2500, -90.0f,  90.0f,   0.0f, +1},  // J1 底座
    {500, 2500,   0.0f, 135.0f,   5.0f, +1},  // J2 大臂（+5°零位偏移）
    {500, 2500, -135.0f, 0.0f,   -3.0f, -1},  // J3 小臂（反向安装）
    {500, 2500, -90.0f,  90.0f,   0.0f, +1},  // J4 末端
    {500, 2500,   0.0f,  60.0f,   0.0f, +1},  // 夹爪
};

// 将关节角度转换为PWM脉宽(us)
uint16_t angle_to_pulse(uint8_t joint, float angle) {
    ServoCalib *c = &calib[joint];
    float adj = (angle + c->zero_offset) * c->direction;
    adj = fmaxf(c->angle_min, fminf(c->angle_max, adj));
    float ratio = (adj - c->angle_min) / (c->angle_max - c->angle_min);
    return (uint16_t)(c->pulse_min + ratio * (c->pulse_max - c->pulse_min));
}

// STM32 TIM2/TIM3 PWM输出（50Hz，20ms周期）
// CubeMX配置：TIM2, PSC=71, ARR=19999 → 50Hz @ 72MHz
void set_servo_pulse(uint8_t ch, uint16_t pulse_us) {
    // pulse_us范围500~2500，对应CCR值500~2500（1us/count）
    switch (ch) {
        case 0: TIM2->CCR1 = pulse_us; break;
        case 1: TIM2->CCR2 = pulse_us; break;
        case 2: TIM2->CCR3 = pulse_us; break;
        case 3: TIM2->CCR4 = pulse_us; break;
        case 4: TIM3->CCR1 = pulse_us; break;
    }
}

void arm_set_joints(const JointAngles *q) {
    set_servo_pulse(0, angle_to_pulse(0, q->j1));
    set_servo_pulse(1, angle_to_pulse(1, q->j2));
    set_servo_pulse(2, angle_to_pulse(2, q->j3));
    set_servo_pulse(3, angle_to_pulse(3, q->j4));
}
```

### 舵机扭矩计算与选型指南

选择舵机时需要计算各关节的负载扭矩：

```
扭矩计算公式：
  τ = F × d = m × g × L_arm

其中：
  m    = 负载质量 + 连杆质量 (kg)
  g    = 9.81 m/s²
  L_arm = 力臂长度 (m)（最坏情况：连杆水平伸展）

安全系数：选择额定扭矩 ≥ 计算值 × 2.0（动态载荷）
```

**各关节扭矩估算（4-DOF臂，负载200g）**：

| 关节 | 负载质量 | 力臂 | 计算扭矩 | 推荐舵机 | 额定扭矩 |
|------|---------|------|---------|---------|---------|
| J4末端 | 200g | 65mm | 0.13N·m | SG90 | 0.18N·m |
| J3小臂 | 350g | 100mm | 0.34N·m | MG996R | 1.08N·m |
| J2大臂 | 600g | 105mm | 0.62N·m | MG996R | 1.08N·m |
| J1底座 | 1200g | 旋转惯量 | 0.30N·m | MG996R | 1.08N·m |

**舵机选型对比**：

| 型号 | 扭矩 | 速度 | 电压 | 重量 | 价格 | 适用关节 |
|------|------|------|------|------|------|---------|
| SG90 | 1.8kg·cm | 0.1s/60° | 4.8V | 9g | ¥5 | 末端/夹爪 |
| MG996R | 11kg·cm | 0.17s/60° | 6V | 55g | ¥18 | 主要关节 |
| DS3218 | 20kg·cm | 0.16s/60° | 6V | 60g | ¥35 | 重载关节 |
| Dynamixel XL430 | 15kg·cm | 0.19s/60° | 12V | 82g | ¥350 | 精密控制 |

### 轨迹规划

#### 关节空间插补（Joint Space Interpolation）

在关节空间中插补，末端轨迹不是直线，但计算简单，不会经过奇异点：

```c
// 全局当前关节角度
static JointAngles g_current_joints = {0, 45, -45, 0};

void arm_get_current_joints(JointAngles *q) {
    *q = g_current_joints;
}

// 关节空间S曲线插补（正弦平滑）
void arm_move_joints(const JointAngles *target, uint32_t duration_ms) {
    JointAngles start = g_current_joints;
    uint32_t steps = duration_ms / 10;  // 10ms控制周期
    if (steps == 0) steps = 1;

    for (uint32_t i = 1; i <= steps; i++) {
        float t = (float)i / (float)steps;
        // S曲线：正弦平滑，加速度连续
        float s = (1.0f - cosf(t * 3.14159265f)) * 0.5f;

        JointAngles q = {
            .j1 = start.j1 + (target->j1 - start.j1) * s,
            .j2 = start.j2 + (target->j2 - start.j2) * s,
            .j3 = start.j3 + (target->j3 - start.j3) * s,
            .j4 = start.j4 + (target->j4 - start.j4) * s,
        };
        arm_set_joints(&q);
        g_current_joints = q;
        HAL_Delay(10);
    }
    g_current_joints = *target;
    arm_set_joints(target);
}
```

#### 笛卡尔空间直线插补（Cartesian Linear Interpolation）

末端沿直线运动，每步调用逆运动学，适合精确路径控制：

```c
// 末端从当前位置直线运动到目标位置
// 返回0成功，-1路径中有不可达点
int arm_move_linear(float tx, float ty, float tz,
                    float end_pitch, uint32_t duration_ms) {
    EndEffectorPose start_pose = forward_kinematics(&g_current_joints);
    float start_pitch = g_current_joints.j2
                      + g_current_joints.j3
                      + g_current_joints.j4;

    uint32_t steps = duration_ms / 10;
    if (steps == 0) steps = 1;

    for (uint32_t i = 1; i <= steps; i++) {
        float t = (float)i / (float)steps;
        float s = (1.0f - cosf(t * 3.14159265f)) * 0.5f;

        float cx = start_pose.x + (tx - start_pose.x) * s;
        float cy = start_pose.y + (ty - start_pose.y) * s;
        float cz = start_pose.z + (tz - start_pose.z) * s;
        float cp = start_pitch + (end_pitch - start_pitch) * s;

        IKResult ik = ik_best_solution(cx, cy, cz, cp, &g_current_joints);
        if (!ik.valid) {
            return -1;  // 路径中有不可达点
        }
        arm_set_joints(&ik.q);
        g_current_joints = ik.q;
        HAL_Delay(10);
    }
    return 0;
}
```

#### 关节空间 vs 笛卡尔空间对比

```
关节空间插补：
  优点：计算简单，不经过奇异点，速度均匀
  缺点：末端轨迹弯曲，不适合需要直线路径的任务
  适用：点到点运动，初始化，回零

笛卡尔空间插补：
  优点：末端走直线，路径可预测
  缺点：可能经过奇异点，计算量大（每步需IK）
  适用：抓取、焊接、涂胶等需要直线路径的任务

时序对比（100步插补，STM32F103 @ 72MHz）：
  关节空间：每步 ~5μs（纯数学运算）
  笛卡尔空间：每步 ~45μs（含IK求解）
  两者均满足10ms控制周期要求
```

## 深入原理

### 奇异性分析（Singularity Analysis）

奇异点（Singular Configuration）是机械臂失去一个或多个自由度的构型，此时雅可比矩阵（Jacobian）行列式为零，IK无唯一解。

**4-DOF臂的奇异构型**：

```
奇异类型1：肩部奇异（Shoulder Singularity）
  发生条件：末端目标在J1轴线上（x=0, y=0）
  现象：J1角度无法确定（atan2(0,0)未定义）
  检测：r = sqrt(x²+y²) < ε（ε≈5mm）

奇异类型2：肘部奇异（Elbow Singularity）
  发生条件：大臂和小臂完全伸展或完全折叠
  现象：J3=0°或J3=±180°，J2和J4有无穷多组合
  检测：|d - (L1+L2)| < ε 或 d < ε

奇异类型3：腕部奇异（Wrist Singularity）
  4-DOF臂无独立腕部，此类奇异不适用
```

**奇异性检测与处理**：

```c
#define SINGULARITY_THRESHOLD  5.0f  // mm

typedef enum {
    SING_NONE     = 0,
    SING_SHOULDER = 1,
    SING_ELBOW    = 2,
} SingularityType;

SingularityType check_singularity(float x, float y, float z,
                                   float end_pitch) {
    // 检查肩部奇异
    float r = sqrtf(x*x + y*y);
    if (r < SINGULARITY_THRESHOLD) {
        return SING_SHOULDER;
    }

    // 检查肘部奇异
    float ep = end_pitch * DEG2RAD;
    float wx = r - L3 * cosf(ep);
    float wz = z - L0 - L3 * sinf(ep);
    float d  = sqrtf(wx*wx + wz*wz);

    if (fabsf(d - (L1 + L2)) < SINGULARITY_THRESHOLD ||
        d < SINGULARITY_THRESHOLD) {
        return SING_ELBOW;
    }
    return SING_NONE;
}

// 奇异点附近的平滑处理：微小偏移避开奇异点
int arm_move_linear_safe(float tx, float ty, float tz,
                          float end_pitch, uint32_t duration_ms) {
    SingularityType sing = check_singularity(tx, ty, tz, end_pitch);
    if (sing == SING_SHOULDER) {
        // 肩部奇异：在目标点附近加微小偏移
        tx += (tx >= 0) ? SINGULARITY_THRESHOLD : -SINGULARITY_THRESHOLD;
    }
    return arm_move_linear(tx, ty, tz, end_pitch, duration_ms);
}
```

### 关节限位处理（Joint Limit Handling）

```c
// 关节软限位（比硬件限位留5°余量）
typedef struct {
    float min_soft;  // 软限位最小值
    float max_soft;  // 软限位最大值
    float min_hard;  // 硬件限位最小值
    float max_hard;  // 硬件限位最大值
} JointLimit;

const JointLimit JOINT_LIMITS[4] = {
    {-85.0f,  85.0f, -90.0f,  90.0f},  // J1
    {  5.0f, 130.0f,   0.0f, 135.0f},  // J2
    {-130.0f, -5.0f,-135.0f,   0.0f},  // J3
    {-85.0f,  85.0f, -90.0f,  90.0f},  // J4
};

// 将关节角度夹紧到软限位范围
float clamp_joint(uint8_t joint, float angle) {
    const JointLimit *lim = &JOINT_LIMITS[joint];
    return fmaxf(lim->min_soft, fminf(lim->max_soft, angle));
}

// 检查关节角度是否在软限位内
int joint_in_soft_limit(uint8_t joint, float angle) {
    const JointLimit *lim = &JOINT_LIMITS[joint];
    return (angle >= lim->min_soft && angle <= lim->max_soft);
}

// 带限位保护的关节运动
void arm_set_joints_safe(const JointAngles *q) {
    JointAngles safe = {
        .j1 = clamp_joint(0, q->j1),
        .j2 = clamp_joint(1, q->j2),
        .j3 = clamp_joint(2, q->j3),
        .j4 = clamp_joint(3, q->j4),
    };
    arm_set_joints(&safe);
    g_current_joints = safe;
}
```

### 简单碰撞检测（Collision Detection）

对于教学级机械臂，实现基于包围球（Bounding Sphere）的简化碰撞检测：

```c
// 连杆包围球（球心在连杆中点，半径为连杆长度/2 + 安全余量）
typedef struct {
    float cx, cy, cz;  // 球心坐标
    float radius;       // 半径
} BoundingSphere;

// 计算各连杆包围球（基于正运动学中间结果）
void compute_link_spheres(const JointAngles *q,
                           BoundingSphere spheres[4]) {
    // 计算各关节位置
    Mat4 T01, T12, T23, T34, T02, T03, T04;
    dh_matrix(q->j1, L0, 0.0f, 90.0f, T01);
    dh_matrix(q->j2, 0.0f, L1, 0.0f, T12);
    dh_matrix(q->j3, 0.0f, L2, 0.0f, T23);
    dh_matrix(q->j4, 0.0f, L3, 0.0f, T34);

    Mat4 T02_, T03_, T04_;
    mat4_mul(T01, T12, T02_);
    mat4_mul(T02_, T23, T03_);
    mat4_mul(T03_, T34, T04_);

    // 连杆1包围球（J1轴到J2轴中点）
    spheres[0].cx = T01[0][3] * 0.5f;
    spheres[0].cy = T01[1][3] * 0.5f;
    spheres[0].cz = (0 + T01[2][3]) * 0.5f;
    spheres[0].radius = L0 * 0.5f + 20.0f;

    // 连杆2包围球（J2轴到J3轴中点）
    spheres[1].cx = (T01[0][3] + T02_[0][3]) * 0.5f;
    spheres[1].cy = (T01[1][3] + T02_[1][3]) * 0.5f;
    spheres[1].cz = (T01[2][3] + T02_[2][3]) * 0.5f;
    spheres[1].radius = L1 * 0.5f + 15.0f;

    // 连杆3包围球
    spheres[2].cx = (T02_[0][3] + T03_[0][3]) * 0.5f;
    spheres[2].cy = (T02_[1][3] + T03_[1][3]) * 0.5f;
    spheres[2].cz = (T02_[2][3] + T03_[2][3]) * 0.5f;
    spheres[2].radius = L2 * 0.5f + 15.0f;

    // 连杆4包围球
    spheres[3].cx = (T03_[0][3] + T04_[0][3]) * 0.5f;
    spheres[3].cy = (T03_[1][3] + T04_[1][3]) * 0.5f;
    spheres[3].cz = (T03_[2][3] + T04_[2][3]) * 0.5f;
    spheres[3].radius = L3 * 0.5f + 10.0f;
}

// 检查两球是否相交
static int spheres_intersect(const BoundingSphere *a,
                              const BoundingSphere *b) {
    float dx = a->cx - b->cx;
    float dy = a->cy - b->cy;
    float dz = a->cz - b->cz;
    float dist2 = dx*dx + dy*dy + dz*dz;
    float r_sum = a->radius + b->radius;
    return dist2 < r_sum * r_sum;
}

// 自碰撞检测（检查非相邻连杆）
int check_self_collision(const JointAngles *q) {
    BoundingSphere spheres[4];
    compute_link_spheres(q, spheres);

    // 检查连杆1和连杆3（非相邻）
    if (spheres_intersect(&spheres[0], &spheres[2])) return 1;
    // 检查连杆1和连杆4
    if (spheres_intersect(&spheres[0], &spheres[3])) return 1;
    // 检查连杆2和连杆4
    if (spheres_intersect(&spheres[1], &spheres[3])) return 1;

    // 检查末端是否低于地面（z < 0）
    EndEffectorPose pose = forward_kinematics(q);
    if (pose.z < 0.0f) return 1;

    return 0;  // 无碰撞
}
```

## 完整项目实战：视觉引导抓取系统

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    视觉引导抓取系统                           │
│                                                             │
│  ┌──────────────┐    UART/SPI    ┌──────────────────────┐  │
│  │  ESP32-CAM   │ ─────────────→ │   STM32F103C8T6      │  │
│  │  OV2640摄像头 │  目标坐标(x,y) │   主控制器           │  │
│  │  颜色识别     │               │                      │  │
│  │  质心计算     │               │  ┌────────────────┐  │  │
│  └──────────────┘               │  │  运动学引擎     │  │  │
│                                 │  │  FK / IK       │  │  │
│  ┌──────────────┐               │  │  轨迹规划      │  │  │
│  │  上位机(可选) │ ←── UART ───  │  └────────────────┘  │  │
│  │  Python调试  │               │                      │  │
│  └──────────────┘               │  TIM2/TIM3 PWM×5    │  │
│                                 └──────────┬───────────┘  │
│                                            │               │
│                              ┌─────────────▼────────────┐  │
│                              │  5V/5A 舵机电源           │  │
│                              │  J1(MG996R) J2(MG996R)   │  │
│                              │  J3(MG996R) J4(SG90)     │  │
│                              │  夹爪(SG90)               │  │
│                              └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### ESP32-CAM 颜色识别模块

```cpp
// ESP32-CAM 颜色识别代码（Arduino框架）
// 识别红色物体质心，通过UART发送坐标给STM32
// 依赖：esp32-camera库（ESP-IDF内置）

#include "esp_camera.h"
#include "Arduino.h"

// AI-Thinker ESP32-CAM引脚定义
#define PWDN_GPIO_NUM  32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM   0
#define SIOD_GPIO_NUM  26
#define SIOC_GPIO_NUM  27
#define Y9_GPIO_NUM    35
#define Y8_GPIO_NUM    34
#define Y7_GPIO_NUM    39
#define Y6_GPIO_NUM    36
#define Y5_GPIO_NUM    21
#define Y4_GPIO_NUM    19
#define Y3_GPIO_NUM    18
#define Y2_GPIO_NUM     5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM  23
#define PCLK_GPIO_NUM  22

// 颜色阈值（HSV空间，红色）
#define H_MIN  0
#define H_MAX  15
#define S_MIN  100
#define V_MIN  80

// RGB转HSV（简化版）
void rgb_to_hsv(uint8_t r, uint8_t g, uint8_t b,
                float *h, float *s, float *v) {
    float rf = r / 255.0f, gf = g / 255.0f, bf = b / 255.0f;
    float cmax = fmaxf(rf, fmaxf(gf, bf));
    float cmin = fminf(rf, fminf(gf, bf));
    float delta = cmax - cmin;

    *v = cmax;
    *s = (cmax > 0.001f) ? (delta / cmax) : 0.0f;

    if (delta < 0.001f) { *h = 0; return; }
    if (cmax == rf)      *h = 60.0f * fmodf((gf-bf)/delta, 6.0f);
    else if (cmax == gf) *h = 60.0f * ((bf-rf)/delta + 2.0f);
    else                 *h = 60.0f * ((rf-gf)/delta + 4.0f);
    if (*h < 0) *h += 360.0f;
}

// 在RGB565帧中查找红色物体质心
// 返回1找到目标，cx/cy为归一化坐标[-1,1]
int find_red_object(camera_fb_t *fb, float *cx, float *cy) {
    uint32_t sum_x = 0, sum_y = 0, count = 0;
    uint16_t w = fb->width, h = fb->height;
    uint16_t *pixels = (uint16_t *)fb->buf;

    for (uint16_t y = 0; y < h; y++) {
        for (uint16_t x = 0; x < w; x++) {
            uint16_t px = pixels[y * w + x];
            // RGB565解包
            uint8_t r = (px >> 11) << 3;
            uint8_t g = ((px >> 5) & 0x3F) << 2;
            uint8_t b = (px & 0x1F) << 3;

            float hh, ss, vv;
            rgb_to_hsv(r, g, b, &hh, &ss, &vv);

            if ((hh <= H_MAX || hh >= 345) &&  // 红色（含环绕）
                ss * 255 >= S_MIN &&
                vv * 255 >= V_MIN) {
                sum_x += x;
                sum_y += y;
                count++;
            }
        }
    }

    if (count < 100) return 0;  // 目标太小，忽略

    // 归一化到[-1, 1]
    *cx = ((float)sum_x / count - w * 0.5f) / (w * 0.5f);
    *cy = ((float)sum_y / count - h * 0.5f) / (h * 0.5f);
    return 1;
}

void setup() {
    Serial.begin(115200);  // 与STM32通信

    camera_config_t config = {};
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk  = XCLK_GPIO_NUM;
    config.pin_pclk  = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href  = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn  = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_RGB565;
    config.frame_size   = FRAMESIZE_QVGA;  // 320x240
    config.fb_count     = 1;

    esp_camera_init(&config);
}

void loop() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) return;

    float cx, cy;
    if (find_red_object(fb, &cx, &cy)) {
        // 发送格式："V cx cy\n"（V=Vision）
        Serial.printf("V %.3f %.3f\n", cx, cy);
    }
    esp_camera_fb_return(fb);
    delay(50);  // 20fps
}
```

### STM32主控：视觉引导抓取状态机

```c
// STM32F103 主控代码
// 接收ESP32-CAM视觉坐标，执行视觉引导抓取

#include "stm32f1xx_hal.h"
#include <string.h>
#include <stdio.h>
#include <math.h>

// ── 视觉坐标到世界坐标的映射 ─────────────────────────────────
// 相机安装在机械臂正上方，俯视工作台
// 工作台范围：x: 100~200mm, y: -80~80mm, z: 0mm（桌面）
#define TABLE_Z       5.0f   // 桌面高度(mm)，略高于0避免碰撞
#define CAMERA_X_MIN  100.0f
#define CAMERA_X_MAX  200.0f
#define CAMERA_Y_MIN  -80.0f
#define CAMERA_Y_MAX   80.0f

void vision_to_world(float cx, float cy,
                     float *wx, float *wy) {
    // cx, cy 范围 [-1, 1]，映射到工作台坐标
    *wx = CAMERA_X_MIN + (cx + 1.0f) * 0.5f
          * (CAMERA_X_MAX - CAMERA_X_MIN);
    *wy = CAMERA_Y_MIN + (cy + 1.0f) * 0.5f
          * (CAMERA_Y_MAX - CAMERA_Y_MIN);
}

// ── 抓取状态机 ────────────────────────────────────────────────
typedef enum {
    STATE_IDLE = 0,
    STATE_HOME,
    STATE_SEARCH,       // 等待视觉目标
    STATE_APPROACH,     // 移动到目标上方
    STATE_DESCEND,      // 下降到抓取高度
    STATE_GRASP,        // 闭合夹爪
    STATE_LIFT,         // 提起物体
    STATE_PLACE,        // 移动到放置位置
    STATE_RELEASE,      // 张开夹爪
    STATE_DONE,
} ArmState;

static ArmState g_state = STATE_IDLE;
static float g_target_x, g_target_y;  // 视觉检测到的目标坐标
static int   g_target_valid = 0;

// 放置位置（固定）
#define PLACE_X  -120.0f
#define PLACE_Y   80.0f
#define PLACE_Z   30.0f

// 夹爪控制
void gripper_close(void) {
    set_servo_pulse(4, angle_to_pulse(4, 50));  // 50°=闭合
    HAL_Delay(600);
}
void gripper_open(void) {
    set_servo_pulse(4, angle_to_pulse(4, 0));   // 0°=张开
    HAL_Delay(400);
}

// 主状态机（在主循环中调用）
void arm_state_machine(void) {
    static JointAngles home = {0, 60, -60, 0};

    switch (g_state) {
    case STATE_IDLE:
        g_state = STATE_HOME;
        break;

    case STATE_HOME:
        gripper_open();
        arm_move_joints(&home, 1200);
        g_state = STATE_SEARCH;
        break;

    case STATE_SEARCH:
        // 等待视觉模块检测到目标
        if (g_target_valid) {
            g_target_valid = 0;
            g_state = STATE_APPROACH;
        }
        break;

    case STATE_APPROACH: {
        // 移动到目标正上方80mm处
        float wx, wy;
        vision_to_world(g_target_x, g_target_y, &wx, &wy);
        int ret = arm_move_linear(wx, wy, TABLE_Z + 80.0f, -70.0f, 1000);
        if (ret == 0) {
            g_state = STATE_DESCEND;
        } else {
            // IK失败，回到搜索状态
            g_state = STATE_HOME;
        }
        break;
    }

    case STATE_DESCEND: {
        // 下降到抓取高度（桌面+15mm）
        EndEffectorPose cur = forward_kinematics(&g_current_joints);
        int ret = arm_move_linear(cur.x, cur.y,
                                   TABLE_Z + 15.0f, -80.0f, 600);
        g_state = (ret == 0) ? STATE_GRASP : STATE_HOME;
        break;
    }

    case STATE_GRASP:
        gripper_close();
        g_state = STATE_LIFT;
        break;

    case STATE_LIFT: {
        EndEffectorPose cur = forward_kinematics(&g_current_joints);
        arm_move_linear(cur.x, cur.y, TABLE_Z + 80.0f, -70.0f, 600);
        g_state = STATE_PLACE;
        break;
    }

    case STATE_PLACE:
        arm_move_linear(PLACE_X, PLACE_Y, PLACE_Z + 60.0f, -70.0f, 1200);
        arm_move_linear(PLACE_X, PLACE_Y, PLACE_Z, -80.0f, 600);
        g_state = STATE_RELEASE;
        break;

    case STATE_RELEASE:
        gripper_open();
        g_state = STATE_DONE;
        break;

    case STATE_DONE:
        arm_move_joints(&home, 1000);
        HAL_Delay(500);
        g_state = STATE_SEARCH;  // 继续下一次抓取
        break;
    }
}

// UART接收回调（解析ESP32-CAM发来的视觉坐标）
// 格式："V cx cy\n"
void parse_vision_uart(const char *line) {
    float cx, cy;
    if (sscanf(line, "V %f %f", &cx, &cy) == 2) {
        g_target_x = cx;
        g_target_y = cy;
        g_target_valid = 1;
    }
}

// 主循环
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_TIM2_Init();   // PWM输出
    MX_TIM3_Init();
    MX_USART1_UART_Init();  // 与ESP32-CAM通信

    // 启动PWM
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_4);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);

    g_state = STATE_IDLE;

    while (1) {
        // 处理UART接收（非阻塞，使用DMA+空闲中断）
        process_uart_rx();
        // 执行状态机
        arm_state_machine();
    }
}
```

### 性能调优

**控制周期优化**：

```c
// 使用TIM6定时器中断实现精确10ms控制周期
// 避免HAL_Delay阻塞导致的UART数据丢失

volatile uint8_t g_control_tick = 0;

void TIM6_IRQHandler(void) {
    if (__HAL_TIM_GET_FLAG(&htim6, TIM_FLAG_UPDATE)) {
        __HAL_TIM_CLEAR_FLAG(&htim6, TIM_FLAG_UPDATE);
        g_control_tick = 1;
    }
}

// 主循环改为事件驱动
while (1) {
    process_uart_rx();  // 始终处理UART
    if (g_control_tick) {
        g_control_tick = 0;
        arm_state_machine();  // 每10ms执行一次
    }
}
```

**舵机平滑度优化**：

```
问题：舵机在目标位置附近抖动（死区效应）
原因：MG996R死区约5μs，对应约0.45°
解决：
  1. 到达目标后停止发送PWM（舵机自然保持）
  2. 或使用数字舵机（Dynamixel）替代模拟舵机
  3. 增加到位判断：|current - target| < 1°时停止插补

// 到位检测
int joints_reached(const JointAngles *target, float threshold_deg) {
    return (fabsf(g_current_joints.j1 - target->j1) < threshold_deg &&
            fabsf(g_current_joints.j2 - target->j2) < threshold_deg &&
            fabsf(g_current_joints.j3 - target->j3) < threshold_deg &&
            fabsf(g_current_joints.j4 - target->j4) < threshold_deg);
}
```

## 常见问题与调试

### 问题1：舵机抖动（Servo Jitter）

**现象**：舵机在目标位置附近持续小幅振动，无法稳定停止。

**原因分析**：

```
原因1：PWM信号干扰
  - 舵机电源与MCU共地，大电流引起地线噪声
  - PWM信号线过长，感应干扰
  诊断：用示波器测量PWM信号，观察是否有毛刺

原因2：控制算法问题
  - 插补步长过小，每步变化量小于舵机死区
  - 目标位置在两个PWM值之间反复切换
  诊断：打印每步的pulse_us值，观察是否在两值间跳变

原因3：机械问题
  - 舵机齿轮磨损，间隙过大
  - 连杆安装不牢固，产生共振
  诊断：手动转动舵机输出轴，感受间隙大小
```

**解决方案**：

```c
// 方案1：PWM滤波（低通滤波器）
static uint16_t pulse_filtered[5] = {1500, 1500, 1500, 1500, 1500};

void set_servo_pulse_filtered(uint8_t ch, uint16_t target) {
    // 一阶低通滤波：α=0.3（较慢但平滑）
    pulse_filtered[ch] = (uint16_t)(
        0.7f * pulse_filtered[ch] + 0.3f * target);
    set_servo_pulse(ch, pulse_filtered[ch]);
}

// 方案2：死区补偿（到位后停止更新PWM）
#define PULSE_DEADBAND  3  // us，小于此值不更新

void set_servo_pulse_deadband(uint8_t ch, uint16_t target) {
    static uint16_t last_pulse[5] = {1500,1500,1500,1500,1500};
    if (abs((int)target - (int)last_pulse[ch]) > PULSE_DEADBAND) {
        set_servo_pulse(ch, target);
        last_pulse[ch] = target;
    }
}

// 方案3：硬件滤波
// 在PWM信号线上串联100Ω电阻 + 并联100nF电容到地
// 截止频率 fc = 1/(2π×100×100e-9) ≈ 16kHz
// 可滤除高频干扰，不影响50Hz PWM信号
```

### 问题2：逆运动学无解（IK No-Solution）

**现象**：调用IK函数返回-1（无效解），机械臂无法到达目标位置。

**原因分析与处理**：

```c
// 完整的IK失败处理策略
typedef enum {
    IK_OK = 0,
    IK_OUT_OF_REACH,    // 目标超出工作空间
    IK_JOINT_LIMIT,     // 解存在但超出关节限位
    IK_SINGULARITY,     // 目标在奇异点附近
    IK_COLLISION,       // 解会导致碰撞
} IKStatus;

IKStatus ik_with_diagnosis(float x, float y, float z,
                            float end_pitch,
                            JointAngles *result) {
    // 1. 检查奇异性
    SingularityType sing = check_singularity(x, y, z, end_pitch);
    if (sing != SING_NONE) {
        // 尝试微小偏移
        float dx = (sing == SING_SHOULDER) ? 5.0f : 0.0f;
        IKResult ik = ik_best_solution(x + dx, y, z,
                                        end_pitch, &g_current_joints);
        if (ik.valid) {
            *result = ik.q;
            return IK_OK;
        }
        return IK_SINGULARITY;
    }

    // 2. 尝试求解
    IKResult ik = ik_best_solution(x, y, z, end_pitch,
                                    &g_current_joints);
    if (!ik.valid) {
        // 判断是超出范围还是关节限位
        float r = sqrtf(x*x + y*y);
        float ep = end_pitch * DEG2RAD;
        float wx = r - L3 * cosf(ep);
        float wz = z - L0 - L3 * sinf(ep);
        float d  = sqrtf(wx*wx + wz*wz);
        if (d > L1 + L2 + 5.0f) return IK_OUT_OF_REACH;
        return IK_JOINT_LIMIT;
    }

    // 3. 碰撞检测
    if (check_self_collision(&ik.q)) {
        return IK_COLLISION;
    }

    *result = ik.q;
    return IK_OK;
}

// 上层调用示例
void safe_move_to(float x, float y, float z, float pitch) {
    JointAngles target;
    IKStatus status = ik_with_diagnosis(x, y, z, pitch, &target);

    switch (status) {
    case IK_OK:
        arm_move_joints(&target, 1000);
        break;
    case IK_OUT_OF_REACH:
        // 记录日志，通知上位机
        uart_send("ERR: target out of reach\n");
        break;
    case IK_JOINT_LIMIT:
        // 尝试调整末端姿态角
        for (float dp = -10.0f; dp <= 10.0f; dp += 2.0f) {
            if (ik_with_diagnosis(x, y, z, pitch+dp,
                                   &target) == IK_OK) {
                arm_move_joints(&target, 1000);
                return;
            }
        }
        uart_send("ERR: joint limit, no solution\n");
        break;
    case IK_SINGULARITY:
        uart_send("WARN: near singularity, offset applied\n");
        break;
    case IK_COLLISION:
        uart_send("ERR: collision detected\n");
        break;
    }
}
```

### 问题3：机械间隙（Mechanical Backlash）

**现象**：机械臂在改变运动方向时，末端位置有明显偏差（通常2~5mm）。

**原因**：舵机齿轮组存在间隙，换向时需要先消除间隙才能传递力矩。

```
间隙影响分析：
  MG996R典型间隙：约1°
  J2关节（大臂）：1°间隙 → 末端位置误差 ≈ L1×sin(1°) ≈ 1.8mm
  J3关节（小臂）：1°间隙 → 末端位置误差 ≈ L2×sin(1°) ≈ 1.7mm
  累积误差：可达3~5mm

补偿方法：
  1. 预加载（Preload）：始终从同一方向接近目标
  2. 超调补偿：超过目标一定量后反向回来
  3. 使用无间隙舵机（Dynamixel系列）
```

```c
// 间隙补偿：始终从"正方向"接近目标
// 如果需要减小关节角度，先减小超过backlash量，再增加到目标
#define BACKLASH_DEG  1.5f  // 估计间隙量(度)

void arm_move_joints_backlash_comp(const JointAngles *target,
                                    uint32_t duration_ms) {
    JointAngles pre_target = *target;
    int need_preload = 0;

    // 检查哪些关节需要反向运动
    if (target->j2 < g_current_joints.j2 - 0.5f) {
        pre_target.j2 = target->j2 - BACKLASH_DEG;
        need_preload = 1;
    }
    if (target->j3 < g_current_joints.j3 - 0.5f) {
        pre_target.j3 = target->j3 - BACKLASH_DEG;
        need_preload = 1;
    }

    if (need_preload) {
        // 先运动到预加载位置
        arm_move_joints(&pre_target, duration_ms * 3 / 4);
        HAL_Delay(50);
    }
    // 再运动到目标位置
    arm_move_joints(target, duration_ms / 4);
}
```

### 问题4：舵机过热保护

```c
// 舵机温度监控（通过电流间接估算）
// MG996R额定电流500mA，堵转电流2.5A
// 使用ACS712-5A电流传感器监测总电流

#define CURRENT_OVERLOAD_MA  3000  // 3A触发保护
#define OVERLOAD_DURATION_MS  500  // 持续500ms才保护

static uint32_t overload_start = 0;

void check_servo_overload(void) {
    // ACS712输出：2.5V=0A，灵敏度185mV/A（5A版本）
    uint16_t adc = HAL_ADC_GetValue(&hadc1);
    float voltage = adc * 3.3f / 4096.0f;
    float current_ma = (voltage - 2.5f) / 0.185f * 1000.0f;

    if (current_ma > CURRENT_OVERLOAD_MA) {
        if (overload_start == 0) {
            overload_start = HAL_GetTick();
        } else if (HAL_GetTick() - overload_start > OVERLOAD_DURATION_MS) {
            // 触发保护：停止所有舵机
            for (int i = 0; i < 5; i++) {
                set_servo_pulse(i, 0);  // 0=关闭PWM
            }
            uart_send("ERR: servo overload protection triggered\n");
            g_state = STATE_IDLE;
        }
    } else {
        overload_start = 0;
    }
}
```

### 问题5：视觉坐标抖动

**现象**：ESP32-CAM检测到的目标坐标在每帧之间跳动，导致机械臂频繁微调。

```c
// 视觉坐标滤波（卡尔曼滤波简化版）
typedef struct {
    float x, y;      // 状态估计
    float p;         // 误差协方差
    float q;         // 过程噪声
    float r;         // 测量噪声
} KalmanFilter1D;

void kalman_init(KalmanFilter1D *kf, float q, float r) {
    kf->x = 0; kf->y = 0;
    kf->p = 1.0f;
    kf->q = q;  // 典型值：0.01（目标运动慢）
    kf->r = r;  // 典型值：0.1（摄像头噪声）
}

float kalman_update(KalmanFilter1D *kf, float measurement) {
    // 预测
    kf->p += kf->q;
    // 更新
    float k = kf->p / (kf->p + kf->r);  // 卡尔曼增益
    kf->x += k * (measurement - kf->x);
    kf->p *= (1.0f - k);
    return kf->x;
}

// 使用示例
static KalmanFilter1D kf_x, kf_y;

void init_vision_filter(void) {
    kalman_init(&kf_x, 0.01f, 0.1f);
    kalman_init(&kf_y, 0.01f, 0.1f);
}

void parse_vision_uart_filtered(const char *line) {
    float cx, cy;
    if (sscanf(line, "V %f %f", &cx, &cy) == 2) {
        g_target_x = kalman_update(&kf_x, cx);
        g_target_y = kalman_update(&kf_y, cy);
        g_target_valid = 1;
    }
}
```

## 测试与验证

### 运动学正确性验证

```c
// 验证FK和IK互为逆运算（round-trip测试）
// 在STM32上运行，通过UART输出结果
void test_kinematics_roundtrip(void) {
    // 测试用例：已知关节角度
    JointAngles test_cases[] = {
        {0,   60, -60,  0},   // 正前方伸展
        {45,  90, -90,  0},   // 右侧45°
        {-30, 45, -45, 10},   // 左侧30°，末端上翘
        {0,   30, -30, -20},  // 低位抓取
    };

    int n = sizeof(test_cases) / sizeof(test_cases[0]);
    int pass = 0;

    for (int i = 0; i < n; i++) {
        JointAngles *q_orig = &test_cases[i];

        // FK：关节角 → 末端位置
        EndEffectorPose pose = forward_kinematics(q_orig);

        // IK：末端位置 → 关节角
        float end_pitch = q_orig->j2 + q_orig->j3 + q_orig->j4;
        IKResult ik = ik_best_solution(pose.x, pose.y, pose.z,
                                        end_pitch, q_orig);

        if (!ik.valid) {
            uart_printf("FAIL case %d: IK returned invalid\n", i);
            continue;
        }

        // 检查误差（允许0.5°误差）
        float err = fabsf(ik.q.j1 - q_orig->j1)
                  + fabsf(ik.q.j2 - q_orig->j2)
                  + fabsf(ik.q.j3 - q_orig->j3)
                  + fabsf(ik.q.j4 - q_orig->j4);

        if (err < 2.0f) {  // 总误差 < 2°
            uart_printf("PASS case %d: err=%.3f deg\n", i, err);
            pass++;
        } else {
            uart_printf("FAIL case %d: err=%.3f deg\n", i, err);
            uart_printf("  orig: j1=%.1f j2=%.1f j3=%.1f j4=%.1f\n",
                q_orig->j1, q_orig->j2, q_orig->j3, q_orig->j4);
            uart_printf("  ik:   j1=%.1f j2=%.1f j3=%.1f j4=%.1f\n",
                ik.q.j1, ik.q.j2, ik.q.j3, ik.q.j4);
        }
    }
    uart_printf("Kinematics test: %d/%d passed\n", pass, n);
}
```

### 工作空间边界测试

```c
// 测试工作空间边界附近的IK行为
void test_workspace_boundary(void) {
    struct { float x, y, z, pitch; const char *desc; } cases[] = {
        {270, 0, 80, -30, "最大伸展"},
        {50,  0, 80, -30, "最小收缩"},
        {150, 0, 200, 0,  "最高点"},
        {150, 0, -10, -80,"低于桌面（应失败）"},
        {300, 0, 80, -30, "超出范围（应失败）"},
    };

    for (int i = 0; i < 5; i++) {
        JointAngles q;
        IKStatus s = ik_with_diagnosis(cases[i].x, cases[i].y,
                                        cases[i].z, cases[i].pitch, &q);
        uart_printf("[%s] status=%d\n", cases[i].desc, s);
    }
}
```

### 舵机标定验证程序

```c
// 交互式标定程序（通过UART命令控制）
// 命令格式：
//   "J1 45\n"  → 将J1移动到45°
//   "CAL 1\n"  → 进入J1标定模式
//   "ZERO\n"   → 设置当前位置为零位

void calibration_mode(void) {
    char cmd[32];
    uart_send("进入标定模式。命令：J<n> <angle> | ZERO | EXIT\n");

    while (1) {
        if (uart_readline(cmd, sizeof(cmd))) {
            int joint; float angle;
            if (sscanf(cmd, "J%d %f", &joint, &angle) == 2) {
                if (joint >= 1 && joint <= 4) {
                    uint16_t pulse = angle_to_pulse(joint-1, angle);
                    set_servo_pulse(joint-1, pulse);
                    uart_printf("J%d → %.1f° (pulse=%d)\n",
                                joint, angle, pulse);
                }
            } else if (strncmp(cmd, "ZERO", 4) == 0) {
                // 将当前PWM值记录为零位
                uart_send("零位已记录\n");
            } else if (strncmp(cmd, "EXIT", 4) == 0) {
                break;
            }
        }
    }
}
```

## 延伸阅读

- [运动控制算法](02-motion-control-algorithms.html) — 梯形/S曲线加减速，步进电机控制
- [智能云台项目](04-smart-gimbal-project.html) — 两轴云台，MPU6050姿态稳定，PID控制
- [六足机器人](06-hexapod-robot.html) — PCA9685多舵机驱动，步态规划，逆运动学
- [多轴同步控制](03-multi-axis-sync.html) — 多轴协调，G代码解析，直线/圆弧插补
- [舵机控制基础](../beginner/03-servo-motor-control.html) — PWM原理，舵机驱动，角度控制

**外部参考资源**：

- [MoveIt! 机器人运动规划框架](https://moveit.ros.org/) — 工业级机器人规划
- [Peter Corke Robotics Toolbox](https://petercorke.com/toolboxes/robotics-toolbox/) — MATLAB/Python机器人工具箱
- [LeArm开源机械臂](https://www.hiwonder.com/) — 本项目参考硬件平台

## 参考资料

1. Craig, J.J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson.
2. Lynch, K.M. & Park, F.C. (2017). *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press.
3. 熊有伦 (2011). 《机器人技术基础》. 华中科技大学出版社.
4. Spong, M.W., Hutchinson, S. & Vidyasagar, M. (2006). *Robot Modeling and Control*. Wiley.
5. MG996R舵机数据手册 — Tower Pro
6. STM32F103参考手册 (RM0008) — STMicroelectronics
7. ESP32-CAM技术规格书 — AI-Thinker
8. OV2640摄像头数据手册 — OmniVision Technologies
