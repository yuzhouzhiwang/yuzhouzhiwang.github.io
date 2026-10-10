---
title: "工业机器人控制：从基础到实践的完整指南"
description: "全面学习工业机器人控制技术，包括机器人控制原理、运动规划、传感器集成、安全系统设计和编程开发，通过实践项目掌握工业机器人应用的核心技能"
slug: "industrial-robot-control"

# 分类信息
domain: "行业领域"
module: "工业自动化"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 工业机器人
  - 运动控制
  - 自动化
  - 机器人编程
  - 传感器集成
  - 安全系统
prerequisites:
  - "plc-programming"
  - "industrial-protocols"
  - "scada-system"
related_contents:
  - "industry-4.0"
  - "industrial-control-system"

# 学习信息
estimated_time: 95
difficulty_score: 4

# 作者和版本
author: "工业自动化专家"
author_id: "industrial_automation_expert"
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
  - 工业机器人控制
  - 机器人编程
  - 运动规划
  - 机器人安全
  - 自动化控制
  - 传感器集成
cover_image: "/images/domains/industry/industrial-robot.jpg"
---

# 工业机器人控制：从基础到实践的完整指南

## 学习目标

完成本教程后，你将能够：

- [ ] 理解工业机器人的基本结构和工作原理
- [ ] 掌握机器人坐标系统和运动学基础
- [ ] 熟悉机器人运动规划和轨迹控制方法
- [ ] 能够进行传感器集成和数据处理
- [ ] 掌握机器人安全系统的设计和实现
- [ ] 熟练使用机器人编程语言进行开发
- [ ] 能够完成机器人系统的调试和优化
- [ ] 理解工业机器人的实际应用场景

## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 掌握PLC编程基础（梯形图、指令系统）
- 了解工业通信协议（Modbus、Profibus等）
- 理解SCADA系统的基本概念
- 具备基本的数学知识（三角函数、向量运算）

**技能要求**：
- 能够配置和调试PLC系统
- 熟悉工业自动化设备的操作
- 具备基本的编程能力
- 了解电气控制原理


## 第一部分：工业机器人基础

### 1.1 什么是工业机器人？

**工业机器人（Industrial Robot）** 是一种可编程的自动化机械装置，能够在三维空间内完成各种作业任务。

**核心特点**：
- **可编程性**：通过编程实现不同的作业任务
- **多自由度**：通常具有4-6个运动自由度
- **高精度**：重复定位精度可达±0.02mm
- **高速度**：运动速度快，生产效率高
- **灵活性**：可快速切换不同的作业任务

**典型应用场景**：
- 焊接作业（点焊、弧焊）
- 搬运和码垛
- 装配作业
- 喷涂和涂胶
- 机械加工
- 检测和测量

### 1.2 工业机器人的分类

**按结构分类**：

```
┌─────────────────────────────────────────┐
│        工业机器人类型                    │
├─────────────────────────────────────────┤
│                                         │
│  1. 直角坐标机器人（Cartesian）         │
│     ┌─────┐                            │
│     │  Z  │                            │
│     │  ↕  │                            │
│     └──┬──┘                            │
│     X←─┼─→Y                            │
│        │                                │
│     特点：结构简单，精度高              │
│     应用：搬运、装配                    │
│                                         │
│  2. 圆柱坐标机器人（Cylindrical）       │
│        ┌─┐                             │
│        │Z│                             │
│        └┬┘                             │
│      ↻ θ                               │
│     ←─R─→                              │
│     特点：工作空间大                    │
│     应用：搬运、码垛                    │
│                                         │
│  3. 球坐标机器人（Spherical）           │
│        ┌─┐                             │
│       ↻│θ│                             │
│        └┬┘                             │
│      ↻ φ                               │
│     ←─R─→                              │
│     特点：工作空间最大                  │
│     应用：点焊、喷涂                    │
│                                         │
│  4. 关节型机器人（Articulated）         │
│        ┌─┐                             │
│        │6│ 手腕                        │
│        └┬┘                             │
│      ┌──┴──┐                          │
│      │  5  │ 小臂                      │
│      └──┬──┘                          │
│      ┌──┴──┐                          │
│      │  4  │ 大臂                      │
│      └──┬──┘                          │
│      ┌──┴──┐                          │
│      │1-3  │ 基座                      │
│      └─────┘                          │
│     特点：灵活性最高                    │
│     应用：焊接、装配、喷涂              │
│                                         │
│  5. SCARA机器人                         │
│        ┌─┐                             │
│        │Z│                             │
│        └┬┘                             │
│      ┌──┴──┐                          │
│      │  ↻  │                          │
│      └──┬──┘                          │
│      ┌──┴──┐                          │
│      │  ↻  │                          │
│      └─────┘                          │
│     特点：平面运动快速                  │
│     应用：装配、搬运                    │
│                                         │
│  6. 并联机器人（Delta/Parallel）        │
│      ┌───────┐                        │
│      │ ╱│╲ │                          │
│      │╱ │ ╲│                          │
│      └───┬───┘                        │
│          │                             │
│        ┌─┴─┐                          │
│        │末端│                          │
│        └───┘                          │
│     特点：速度极快                      │
│     应用：分拣、包装                    │
└─────────────────────────────────────────┘
```

**按应用分类**：
- 焊接机器人
- 搬运机器人
- 装配机器人
- 喷涂机器人
- 码垛机器人
- 协作机器人（Cobot）

### 1.3 工业机器人的组成

**系统架构**：

```
┌─────────────────────────────────────────────┐
│          工业机器人系统组成                  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────┐      │
│  │      1. 机械本体                 │      │
│  │  - 基座                          │      │
│  │  - 大臂                          │      │
│  │  - 小臂                          │      │
│  │  - 手腕                          │      │
│  │  - 末端执行器                    │      │
│  └────────────┬─────────────────────┘      │
│               │                             │
│  ┌────────────┴─────────────────────┐      │
│  │      2. 驱动系统                 │      │
│  │  - 伺服电机                      │      │
│  │  - 减速器                        │      │
│  │  - 传动机构                      │      │
│  │  - 制动器                        │      │
│  └────────────┬─────────────────────┘      │
│               │                             │
│  ┌────────────┴─────────────────────┐      │
│  │      3. 控制系统                 │      │
│  │  - 控制器（主控制器）            │      │
│  │  - 伺服驱动器                    │      │
│  │  - I/O接口                       │      │
│  │  - 通信接口                      │      │
│  └────────────┬─────────────────────┘      │
│               │                             │
│  ┌────────────┴─────────────────────┐      │
│  │      4. 传感系统                 │      │
│  │  - 位置传感器（编码器）          │      │
│  │  - 力/力矩传感器                 │      │
│  │  - 视觉传感器                    │      │
│  │  - 接近传感器                    │      │
│  └────────────┬─────────────────────┘      │
│               │                             │
│  ┌────────────┴─────────────────────┐      │
│  │      5. 示教系统                 │      │
│  │  - 示教器（手持编程器）          │      │
│  │  - 编程软件                      │      │
│  │  - 仿真软件                      │      │
│  └──────────────────────────────────┘      │
└─────────────────────────────────────────────┘
```

**关键部件说明**：

1. **机械本体**
   - 承载机器人的运动和负载
   - 决定工作空间和运动范围
   - 材料：铝合金、碳纤维等

2. **驱动系统**
   - 提供运动动力
   - 伺服电机：AC伺服、DC伺服
   - 减速器：谐波减速器、RV减速器

3. **控制系统**
   - 机器人的"大脑"
   - 实时运动控制
   - 轨迹规划和插补

4. **传感系统**
   - 提供位置、力、视觉等反馈
   - 实现闭环控制
   - 提高精度和安全性

5. **示教系统**
   - 编程和调试工具
   - 离线编程和仿真
   - 在线示教和修改


## 第二部分：机器人坐标系统与运动学

### 2.1 坐标系统

**基本坐标系**：

```
1. 世界坐标系（World Coordinate System）
   - 固定在地面或工作台上
   - 作为参考坐标系
   
        Z↑
         │
         │
         └────→ Y
        ╱
       ╱
      X

2. 基座坐标系（Base Coordinate System）
   - 固定在机器人基座上
   - 与世界坐标系可能有偏移
   
3. 工具坐标系（Tool Coordinate System）
   - 固定在末端执行器上
   - 描述工具的位置和姿态
   
        ┌─────┐
        │工具 │ ← 工具坐标系原点
        └──┬──┘
           │
        ┌──┴──┐
        │手腕 │
        └─────┘

4. 工件坐标系（Workpiece Coordinate System）
   - 固定在工件上
   - 方便编程和定位
```

**坐标变换**：

```
世界坐标 → 基座坐标 → 关节坐标 → 工具坐标
   ↓           ↓           ↓           ↓
 固定参考    机器人基座   各关节角度   末端位置
```

### 2.2 运动学基础

#### 2.2.1 正运动学（Forward Kinematics）

**定义**：已知各关节角度，求末端执行器的位置和姿态

**六轴机器人示例**：

```
关节角度：θ1, θ2, θ3, θ4, θ5, θ6
         ↓
      正运动学计算
         ↓
末端位置：X, Y, Z, Rx, Ry, Rz
```

**D-H参数法**：

```
关节 i 的变换矩阵：
T_i = Rot(Z, θ_i) × Trans(0, 0, d_i) × Trans(a_i, 0, 0) × Rot(X, α_i)

其中：
- θ_i: 关节角度
- d_i: 连杆偏距
- a_i: 连杆长度
- α_i: 连杆扭角
```

**计算示例（简化的3轴机器人）**：

```python
import numpy as np

def forward_kinematics(theta1, theta2, theta3, L1, L2, L3):
    """
    计算3轴机器人的正运动学
    theta1, theta2, theta3: 关节角度（弧度）
    L1, L2, L3: 连杆长度
    返回：末端位置 (x, y, z)
    """
    # 计算末端位置
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2) + \
        L3 * np.cos(theta1 + theta2 + theta3)
    
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2) + \
        L3 * np.sin(theta1 + theta2 + theta3)
    
    z = 0  # 平面机器人
    
    return x, y, z

# 示例
theta1 = np.radians(30)  # 30度
theta2 = np.radians(45)  # 45度
theta3 = np.radians(60)  # 60度
L1, L2, L3 = 300, 250, 150  # mm

x, y, z = forward_kinematics(theta1, theta2, theta3, L1, L2, L3)
print(f"末端位置: X={x:.2f}mm, Y={y:.2f}mm, Z={z:.2f}mm")
```

#### 2.2.2 逆运动学（Inverse Kinematics）

**定义**：已知末端执行器的位置和姿态，求各关节角度

**求解方法**：

```
目标位置：X, Y, Z, Rx, Ry, Rz
         ↓
      逆运动学计算
         ↓
关节角度：θ1, θ2, θ3, θ4, θ5, θ6
```

**特点**：
- 可能有多个解（多解性）
- 可能无解（奇异位置）
- 计算复杂度高

**求解示例（2轴平面机器人）**：

```python
import numpy as np

def inverse_kinematics_2dof(x, y, L1, L2):
    """
    计算2轴平面机器人的逆运动学
    x, y: 目标位置
    L1, L2: 连杆长度
    返回：关节角度 (theta1, theta2)
    """
    # 计算到目标点的距离
    d = np.sqrt(x**2 + y**2)
    
    # 检查是否可达
    if d > (L1 + L2) or d < abs(L1 - L2):
        raise ValueError("目标位置不可达")
    
    # 使用余弦定理计算theta2
    cos_theta2 = (d**2 - L1**2 - L2**2) / (2 * L1 * L2)
    theta2 = np.arccos(cos_theta2)
    
    # 计算theta1
    alpha = np.arctan2(y, x)
    beta = np.arctan2(L2 * np.sin(theta2), L1 + L2 * np.cos(theta2))
    theta1 = alpha - beta
    
    return np.degrees(theta1), np.degrees(theta2)

# 示例
x, y = 400, 300  # mm
L1, L2 = 300, 250  # mm

try:
    theta1, theta2 = inverse_kinematics_2dof(x, y, L1, L2)
    print(f"关节角度: θ1={theta1:.2f}°, θ2={theta2:.2f}°")
except ValueError as e:
    print(f"错误: {e}")
```

### 2.3 工作空间

**工作空间定义**：机器人末端执行器能够到达的所有点的集合

**工作空间类型**：

```
1. 可达工作空间（Reachable Workspace）
   - 末端至少能以一种姿态到达的点
   
2. 灵巧工作空间（Dexterous Workspace）
   - 末端能以任意姿态到达的点
   - 通常小于可达工作空间

┌─────────────────────────────────────┐
│    六轴机器人工作空间示例            │
│                                     │
│         ╱───────╲                  │
│        ╱         ╲                 │
│       │           │                │
│       │  灵巧空间 │                │
│       │           │                │
│        ╲         ╱                 │
│         ╲───────╱                  │
│      ╱─────────────╲               │
│     ╱               ╲              │
│    │   可达工作空间   │             │
│    │                 │             │
│     ╲               ╱              │
│      ╲─────────────╱               │
│           │                        │
│        ┌──┴──┐                     │
│        │基座 │                     │
│        └─────┘                     │
└─────────────────────────────────────┘
```

**工作空间参数**：
- 最大工作半径
- 最小工作半径
- 工作高度范围
- 死区（无法到达的区域）


## 第三部分：运动规划与轨迹控制

### 3.1 运动规划基础

**运动规划的目标**：
- 从起点到终点的平滑运动
- 避免碰撞和奇异点
- 满足速度和加速度约束
- 优化运动时间和能耗

**规划方法分类**：

```
┌─────────────────────────────────────┐
│        运动规划方法                  │
├─────────────────────────────────────┤
│                                     │
│  1. 关节空间规划                    │
│     - 在关节角度空间规划            │
│     - 计算简单，速度快              │
│     - 路径不是直线                  │
│                                     │
│  2. 笛卡尔空间规划                  │
│     - 在笛卡尔坐标空间规划          │
│     - 路径是直线或圆弧              │
│     - 需要实时逆运动学计算          │
│                                     │
│  3. 混合规划                        │
│     - 结合两种方法的优点            │
│     - 根据任务选择合适方法          │
└─────────────────────────────────────┘
```

### 3.2 轨迹插补

**插补方法**：

#### 3.2.1 直线插补（Linear Interpolation）

```
起点 P1(x1, y1, z1) → 终点 P2(x2, y2, z2)

插补点计算：
P(t) = P1 + t × (P2 - P1)
其中 t ∈ [0, 1]

示例代码：
```

```python
def linear_interpolation(P1, P2, num_points):
    """
    直线插补
    P1, P2: 起点和终点坐标 [x, y, z]
    num_points: 插补点数量
    返回：插补点列表
    """
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        x = P1[0] + t * (P2[0] - P1[0])
        y = P1[1] + t * (P2[1] - P1[1])
        z = P1[2] + t * (P2[2] - P1[2])
        points.append([x, y, z])
    return points

# 示例
P1 = [100, 200, 300]  # mm
P2 = [400, 500, 600]  # mm
points = linear_interpolation(P1, P2, 10)

for i, p in enumerate(points):
    print(f"点{i}: X={p[0]:.1f}, Y={p[1]:.1f}, Z={p[2]:.1f}")
```

#### 3.2.2 圆弧插补（Circular Interpolation）

```
通过三点定义圆弧：
- 起点 P1
- 中间点 P2
- 终点 P3

圆弧参数：
- 圆心 C
- 半径 R
- 起始角 θ1
- 终止角 θ2
```

```python
import numpy as np

def circular_interpolation(P1, P2, P3, num_points):
    """
    圆弧插补（简化版，仅XY平面）
    P1, P2, P3: 三个点定义圆弧
    num_points: 插补点数量
    """
    # 计算圆心（简化算法）
    # 实际应用中需要更复杂的计算
    
    # 这里提供概念性代码
    points = []
    # ... 圆弧插补计算 ...
    return points
```

#### 3.2.3 样条插补（Spline Interpolation）

```
使用样条曲线实现平滑过渡：
- 三次样条
- B样条
- NURBS曲线

优点：
- 曲线平滑
- 速度连续
- 加速度连续
```

### 3.3 速度规划

**速度曲线类型**：

```
1. 梯形速度曲线
   速度
    │    ┌────────┐
    │   ╱│        │╲
    │  ╱ │        │ ╲
    │ ╱  │        │  ╲
    └────┴────────┴────→ 时间
      加速  匀速  减速

2. S型速度曲线（更平滑）
   速度
    │      ╭────╮
    │     ╱      ╲
    │    ╱        ╲
    │   ╱          ╲
    └───────────────→ 时间
      加加速度限制

3. 多段速度曲线
   速度
    │  ┌──┐  ┌──┐
    │ ╱│  │╲╱│  │╲
    │╱ │  │  │  │ ╲
    └───┴──┴──┴──┴──→ 时间
      多个运动段
```

**速度规划算法**：

```python
def trapezoidal_velocity_profile(distance, v_max, a_max):
    """
    梯形速度规划
    distance: 运动距离
    v_max: 最大速度
    a_max: 最大加速度
    返回：加速时间、匀速时间、减速时间
    """
    # 加速到最大速度所需时间
    t_acc = v_max / a_max
    
    # 加速和减速的距离
    d_acc = 0.5 * a_max * t_acc**2
    d_dec = d_acc
    
    # 检查是否能达到最大速度
    if (d_acc + d_dec) > distance:
        # 三角形速度曲线
        t_acc = np.sqrt(distance / a_max)
        t_const = 0
        t_dec = t_acc
        v_actual = a_max * t_acc
    else:
        # 梯形速度曲线
        d_const = distance - d_acc - d_dec
        t_const = d_const / v_max
        t_dec = t_acc
        v_actual = v_max
    
    return t_acc, t_const, t_dec, v_actual

# 示例
distance = 1000  # mm
v_max = 500  # mm/s
a_max = 1000  # mm/s²

t_acc, t_const, t_dec, v_actual = trapezoidal_velocity_profile(
    distance, v_max, a_max
)

print(f"加速时间: {t_acc:.3f}s")
print(f"匀速时间: {t_const:.3f}s")
print(f"减速时间: {t_dec:.3f}s")
print(f"实际最大速度: {v_actual:.1f}mm/s")
print(f"总时间: {t_acc + t_const + t_dec:.3f}s")
```

### 3.4 路径规划示例

**完整的路径规划流程**：

```python
class RobotPathPlanner:
    def __init__(self, v_max=500, a_max=1000):
        """
        机器人路径规划器
        v_max: 最大速度 (mm/s)
        a_max: 最大加速度 (mm/s²)
        """
        self.v_max = v_max
        self.a_max = a_max
    
    def plan_point_to_point(self, start, end, num_points=100):
        """
        点到点运动规划
        start, end: 起点和终点 [x, y, z]
        num_points: 插补点数量
        返回：轨迹点列表和时间戳
        """
        # 1. 计算距离
        distance = np.linalg.norm(np.array(end) - np.array(start))
        
        # 2. 速度规划
        t_acc, t_const, t_dec, v_actual = self.trapezoidal_velocity_profile(
            distance, self.v_max, self.a_max
        )
        total_time = t_acc + t_const + t_dec
        
        # 3. 生成轨迹点
        trajectory = []
        timestamps = []
        
        for i in range(num_points):
            t = i * total_time / (num_points - 1)
            
            # 计算当前位置（基于速度曲线）
            if t <= t_acc:
                # 加速阶段
                s = 0.5 * self.a_max * t**2
            elif t <= (t_acc + t_const):
                # 匀速阶段
                s = 0.5 * self.a_max * t_acc**2 + \
                    v_actual * (t - t_acc)
            else:
                # 减速阶段
                t_in_dec = t - t_acc - t_const
                s = 0.5 * self.a_max * t_acc**2 + \
                    v_actual * t_const + \
                    v_actual * t_in_dec - \
                    0.5 * self.a_max * t_in_dec**2
            
            # 计算位置
            ratio = s / distance
            point = [
                start[0] + ratio * (end[0] - start[0]),
                start[1] + ratio * (end[1] - start[1]),
                start[2] + ratio * (end[2] - start[2])
            ]
            
            trajectory.append(point)
            timestamps.append(t)
        
        return trajectory, timestamps
    
    def trapezoidal_velocity_profile(self, distance, v_max, a_max):
        """梯形速度规划（同前面的函数）"""
        t_acc = v_max / a_max
        d_acc = 0.5 * a_max * t_acc**2
        d_dec = d_acc
        
        if (d_acc + d_dec) > distance:
            t_acc = np.sqrt(distance / a_max)
            t_const = 0
            t_dec = t_acc
            v_actual = a_max * t_acc
        else:
            d_const = distance - d_acc - d_dec
            t_const = d_const / v_max
            t_dec = t_acc
            v_actual = v_max
        
        return t_acc, t_const, t_dec, v_actual

# 使用示例
planner = RobotPathPlanner(v_max=500, a_max=1000)

start = [100, 200, 300]  # mm
end = [600, 700, 800]    # mm

trajectory, timestamps = planner.plan_point_to_point(start, end, 50)

print("轨迹规划完成:")
print(f"起点: {start}")
print(f"终点: {end}")
print(f"总时间: {timestamps[-1]:.3f}s")
print(f"轨迹点数: {len(trajectory)}")
```


## 第四部分：传感器集成

### 4.1 常用传感器类型

**机器人传感器分类**：

```
┌─────────────────────────────────────────┐
│        机器人传感器系统                  │
├─────────────────────────────────────────┤
│                                         │
│  1. 位置传感器                          │
│     - 编码器（增量式、绝对式）          │
│     - 旋转变压器                        │
│     - 光栅尺                            │
│     功能：测量关节角度和位置            │
│                                         │
│  2. 力/力矩传感器                       │
│     - 六维力传感器                      │
│     - 单轴力传感器                      │
│     - 压力传感器                        │
│     功能：测量接触力和力矩              │
│                                         │
│  3. 视觉传感器                          │
│     - 2D相机                            │
│     - 3D相机（结构光、TOF）             │
│     - 激光扫描仪                        │
│     功能：物体识别、定位、检测          │
│                                         │
│  4. 接近传感器                          │
│     - 电感式接近开关                    │
│     - 电容式接近开关                    │
│     - 光电传感器                        │
│     功能：检测物体存在和距离            │
│                                         │
│  5. 触觉传感器                          │
│     - 压力传感阵列                      │
│     - 触觉皮肤                          │
│     功能：检测接触和抓取状态            │
└─────────────────────────────────────────┘
```

### 4.2 编码器集成

**编码器类型和应用**：

```
1. 增量式编码器
   ┌─────────────┐
   │  A相 ─────  │
   │  B相 ─────  │  → 控制器
   │  Z相 ─────  │
   └─────────────┘
   
   特点：
   - 输出脉冲信号
   - 需要计数器
   - 断电丢失位置
   - 成本低

2. 绝对式编码器
   ┌─────────────┐
   │  数据总线   │  → 控制器
   │  (多位)     │
   └─────────────┘
   
   特点：
   - 输出绝对位置
   - 断电保持位置
   - 无需回零
   - 成本高
```

**编码器数据处理**：

```python
class EncoderReader:
    def __init__(self, resolution=2048, gear_ratio=100):
        """
        编码器读取器
        resolution: 编码器分辨率（脉冲/转）
        gear_ratio: 减速比
        """
        self.resolution = resolution
        self.gear_ratio = gear_ratio
        self.pulse_count = 0
        self.last_position = 0
    
    def read_pulse(self, pulse_increment):
        """
        读取编码器脉冲
        pulse_increment: 脉冲增量
        """
        self.pulse_count += pulse_increment
    
    def get_angle(self):
        """
        获取关节角度（度）
        """
        # 计算电机转数
        motor_revolutions = self.pulse_count / self.resolution
        
        # 计算关节转数（考虑减速比）
        joint_revolutions = motor_revolutions / self.gear_ratio
        
        # 转换为角度
        angle = joint_revolutions * 360
        
        return angle
    
    def get_velocity(self, dt):
        """
        计算角速度（度/秒）
        dt: 时间间隔（秒）
        """
        current_position = self.get_angle()
        velocity = (current_position - self.last_position) / dt
        self.last_position = current_position
        
        return velocity

# 使用示例
encoder = EncoderReader(resolution=2048, gear_ratio=100)

# 模拟读取脉冲
for i in range(10):
    encoder.read_pulse(100)  # 每次100个脉冲
    angle = encoder.get_angle()
    print(f"时刻{i}: 角度 = {angle:.3f}°")
```

### 4.3 力传感器集成

**六维力传感器**：

```
力传感器测量：
┌─────────────────────────────────┐
│  力分量：Fx, Fy, Fz             │
│  力矩分量：Mx, My, Mz           │
└─────────────────────────────────┘

应用场景：
- 装配作业（插入、拧紧）
- 打磨抛光（恒力控制）
- 碰撞检测
- 力控制
```

**力传感器数据处理**：

```python
class ForceSensor:
    def __init__(self, max_force=100, max_torque=10):
        """
        力传感器
        max_force: 最大力（N）
        max_torque: 最大力矩（Nm）
        """
        self.max_force = max_force
        self.max_torque = max_torque
        self.zero_offset = [0, 0, 0, 0, 0, 0]
    
    def calibrate(self, readings):
        """
        零点校准
        readings: 当前读数 [Fx, Fy, Fz, Mx, My, Mz]
        """
        self.zero_offset = readings.copy()
    
    def read_force(self, raw_data):
        """
        读取力和力矩
        raw_data: 原始数据 [Fx, Fy, Fz, Mx, My, Mz]
        返回：校准后的力和力矩
        """
        # 减去零点偏移
        calibrated = [
            raw_data[i] - self.zero_offset[i]
            for i in range(6)
        ]
        
        return {
            'force': calibrated[0:3],    # [Fx, Fy, Fz]
            'torque': calibrated[3:6]    # [Mx, My, Mz]
        }
    
    def check_overload(self, force_torque):
        """
        检查是否过载
        """
        force = force_torque['force']
        torque = force_torque['torque']
        
        # 检查力
        force_magnitude = np.sqrt(sum(f**2 for f in force))
        if force_magnitude > self.max_force:
            return True, "力过载"
        
        # 检查力矩
        torque_magnitude = np.sqrt(sum(t**2 for t in torque))
        if torque_magnitude > self.max_torque:
            return True, "力矩过载"
        
        return False, "正常"

# 使用示例
sensor = ForceSensor(max_force=100, max_torque=10)

# 零点校准
sensor.calibrate([0.5, -0.3, 0.2, 0.1, -0.1, 0.0])

# 读取力传感器
raw_data = [10.5, 5.3, -8.2, 0.5, 0.3, -0.2]
result = sensor.read_force(raw_data)

print(f"力: Fx={result['force'][0]:.2f}N, "
      f"Fy={result['force'][1]:.2f}N, "
      f"Fz={result['force'][2]:.2f}N")
print(f"力矩: Mx={result['torque'][0]:.2f}Nm, "
      f"My={result['torque'][1]:.2f}Nm, "
      f"Mz={result['torque'][2]:.2f}Nm")

# 检查过载
overload, message = sensor.check_overload(result)
print(f"状态: {message}")
```

### 4.4 视觉传感器集成

**视觉系统架构**：

```
┌─────────────────────────────────────────┐
│        机器人视觉系统                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐                          │
│  │  相机    │                          │
│  │          │                          │
│  └────┬─────┘                          │
│       │                                 │
│       ↓                                 │
│  ┌────────────┐                        │
│  │ 图像采集   │                        │
│  └────┬───────┘                        │
│       │                                 │
│       ↓                                 │
│  ┌────────────┐                        │
│  │ 图像处理   │                        │
│  │ - 滤波     │                        │
│  │ - 边缘检测 │                        │
│  │ - 特征提取 │                        │
│  └────┬───────┘                        │
│       │                                 │
│       ↓                                 │
│  ┌────────────┐                        │
│  │ 目标识别   │                        │
│  │ - 模板匹配 │                        │
│  │ - 深度学习 │                        │
│  └────┬───────┘                        │
│       │                                 │
│       ↓                                 │
│  ┌────────────┐                        │
│  │ 位置计算   │                        │
│  │ - 坐标转换 │                        │
│  │ - 姿态估计 │                        │
│  └────┬───────┘                        │
│       │                                 │
│       ↓                                 │
│  ┌────────────┐                        │
│  │ 机器人控制 │                        │
│  └────────────┘                        │
└─────────────────────────────────────────┘
```

**视觉定位示例（简化）**：

```python
import cv2
import numpy as np

class VisionSystem:
    def __init__(self, camera_matrix, dist_coeffs):
        """
        视觉系统
        camera_matrix: 相机内参矩阵
        dist_coeffs: 畸变系数
        """
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
    
    def detect_object(self, image):
        """
        检测物体（简化示例）
        image: 输入图像
        返回：物体中心坐标（像素）
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 查找轮廓
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if len(contours) > 0:
            # 找到最大轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 计算中心
            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                return (cx, cy)
        
        return None
    
    def pixel_to_world(self, pixel_coords, z_world):
        """
        像素坐标转世界坐标
        pixel_coords: 像素坐标 (u, v)
        z_world: 物体的世界坐标Z值（已知）
        返回：世界坐标 (x, y, z)
        """
        u, v = pixel_coords
        
        # 相机内参
        fx = self.camera_matrix[0, 0]
        fy = self.camera_matrix[1, 1]
        cx = self.camera_matrix[0, 2]
        cy = self.camera_matrix[1, 2]
        
        # 计算世界坐标
        x = (u - cx) * z_world / fx
        y = (v - cy) * z_world / fy
        z = z_world
        
        return (x, y, z)

# 使用示例（概念性）
camera_matrix = np.array([
    [800, 0, 320],
    [0, 800, 240],
    [0, 0, 1]
], dtype=float)

dist_coeffs = np.zeros(5)

vision = VisionSystem(camera_matrix, dist_coeffs)

# 假设检测到物体
pixel_coords = (350, 280)
z_world = 500  # mm

world_coords = vision.pixel_to_world(pixel_coords, z_world)
print(f"世界坐标: X={world_coords[0]:.2f}mm, "
      f"Y={world_coords[1]:.2f}mm, "
      f"Z={world_coords[2]:.2f}mm")
```


## 第五部分：安全系统设计

### 5.1 机器人安全标准

**主要安全标准**：

```
┌─────────────────────────────────────────┐
│        机器人安全标准                    │
├─────────────────────────────────────────┤
│                                         │
│  ISO 10218-1:2011                       │
│  - 机器人和机器人装置 - 工业机器人的    │
│    安全要求 - 第1部分：机器人           │
│                                         │
│  ISO 10218-2:2011                       │
│  - 机器人和机器人装置 - 工业机器人的    │
│    安全要求 - 第2部分：机器人系统和集成 │
│                                         │
│  ISO/TS 15066:2016                      │
│  - 协作机器人安全要求                   │
│                                         │
│  IEC 61508                              │
│  - 功能安全标准                         │
└─────────────────────────────────────────┘
```

**安全等级（Safety Integrity Level, SIL）**：

```
┌──────┬────────────┬──────────────┐
│ 等级 │ 失效概率   │ 应用场景     │
├──────┼────────────┼──────────────┤
│ SIL 1│ 10⁻² - 10⁻¹│ 轻微伤害     │
│ SIL 2│ 10⁻³ - 10⁻²│ 严重伤害     │
│ SIL 3│ 10⁻⁴ - 10⁻³│ 致命伤害     │
│ SIL 4│ 10⁻⁵ - 10⁻⁴│ 灾难性后果   │
└──────┴────────────┴──────────────┘
```

### 5.2 安全功能设计

**基本安全功能**：

```
1. 急停功能（Emergency Stop）
   ┌──────────┐
   │ 急停按钮 │ ──→ 立即停止所有运动
   └──────────┘     切断动力
                    进入安全状态

2. 安全限位（Safety Limits）
   - 软限位：软件检查关节角度
   - 硬限位：物理限位开关
   
3. 速度监控（Speed Monitoring）
   - 监控实际速度
   - 超速时触发安全停止
   
4. 力限制（Force Limiting）
   - 监控接触力
   - 超过阈值时停止

5. 安全区域（Safety Zones）
   - 定义禁止区域
   - 检测进入并停止
```

**安全系统架构**：

```
┌─────────────────────────────────────────┐
│        机器人安全系统                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────┐          │
│  │   安全输入设备           │          │
│  │  - 急停按钮              │          │
│  │  - 安全门开关            │          │
│  │  - 光栅/激光扫描仪       │          │
│  │  - 安全地毯              │          │
│  └────────┬─────────────────┘          │
│           │                             │
│           ↓                             │
│  ┌──────────────────────────┐          │
│  │   安全控制器（Safety PLC）│          │
│  │  - 双通道架构            │          │
│  │  - 自诊断功能            │          │
│  │  - 安全逻辑处理          │          │
│  └────────┬─────────────────┘          │
│           │                             │
│           ↓                             │
│  ┌──────────────────────────┐          │
│  │   安全输出               │          │
│  │  - 安全继电器            │          │
│  │  - 电机制动器            │          │
│  │  - 动力切断              │          │
│  └──────────────────────────┘          │
└─────────────────────────────────────────┘
```

### 5.3 碰撞检测

**碰撞检测方法**：

```python
class CollisionDetector:
    def __init__(self, torque_threshold=5.0):
        """
        碰撞检测器
        torque_threshold: 力矩阈值（Nm）
        """
        self.torque_threshold = torque_threshold
        self.nominal_torque = [0] * 6  # 6个关节
        self.collision_detected = False
    
    def update_nominal_torque(self, joint_angles, joint_velocities):
        """
        更新标称力矩（基于动力学模型）
        joint_angles: 关节角度
        joint_velocities: 关节速度
        """
        # 简化：实际应用中需要完整的动力学模型
        # 这里仅作示例
        self.nominal_torque = [
            self.calculate_nominal_torque(i, joint_angles, joint_velocities)
            for i in range(6)
        ]
    
    def calculate_nominal_torque(self, joint_id, angles, velocities):
        """
        计算标称力矩（简化）
        """
        # 实际应用中需要考虑：
        # - 重力补偿
        # - 惯性力
        # - 科里奥利力
        # - 摩擦力
        return 0.0  # 简化示例
    
    def detect_collision(self, measured_torque):
        """
        检测碰撞
        measured_torque: 测量的关节力矩
        返回：是否检测到碰撞
        """
        for i in range(6):
            # 计算力矩误差
            torque_error = abs(measured_torque[i] - self.nominal_torque[i])
            
            # 检查是否超过阈值
            if torque_error > self.torque_threshold:
                self.collision_detected = True
                return True, i  # 返回碰撞的关节编号
        
        self.collision_detected = False
        return False, -1
    
    def get_collision_response(self):
        """
        获取碰撞响应策略
        """
        if self.collision_detected:
            return {
                'action': 'stop',
                'retract': True,
                'alarm': True
            }
        return None

# 使用示例
detector = CollisionDetector(torque_threshold=5.0)

# 模拟运行
joint_angles = [0, 30, 45, 0, 90, 0]  # 度
joint_velocities = [0, 10, 15, 0, 20, 0]  # 度/秒

detector.update_nominal_torque(joint_angles, joint_velocities)

# 模拟测量力矩（正常情况）
measured_torque = [0.5, 1.2, 2.1, 0.3, 3.5, 0.8]
collision, joint = detector.detect_collision(measured_torque)
print(f"碰撞检测: {collision}")

# 模拟碰撞（关节2力矩异常）
measured_torque = [0.5, 8.5, 2.1, 0.3, 3.5, 0.8]
collision, joint = detector.detect_collision(measured_torque)
if collision:
    print(f"检测到碰撞！关节 {joint}")
    response = detector.get_collision_response()
    print(f"响应策略: {response}")
```

### 5.4 安全区域监控

**安全区域定义**：

```
工作空间划分：
┌─────────────────────────────────────┐
│                                     │
│  ┌─────────────────────────┐       │
│  │   禁止区域              │       │
│  │   (Forbidden Zone)      │       │
│  └─────────────────────────┘       │
│                                     │
│  ┌─────────────────────────┐       │
│  │   限制区域              │       │
│  │   (Restricted Zone)     │       │
│  │   - 降低速度            │       │
│  │   - 增加监控            │       │
│  └─────────────────────────┘       │
│                                     │
│  ┌─────────────────────────┐       │
│  │   正常工作区域          │       │
│  │   (Normal Zone)         │       │
│  └─────────────────────────┘       │
│                                     │
│        ┌──┐                        │
│        │机│                        │
│        │器│                        │
│        │人│                        │
│        └──┘                        │
└─────────────────────────────────────┘
```

**安全区域监控代码**：

```python
class SafetyZoneMonitor:
    def __init__(self):
        """
        安全区域监控器
        """
        self.zones = []
    
    def add_zone(self, zone_type, boundary, max_speed=None):
        """
        添加安全区域
        zone_type: 'forbidden', 'restricted', 'normal'
        boundary: 边界定义 {'min': [x, y, z], 'max': [x, y, z]}
        max_speed: 最大允许速度（仅限制区域）
        """
        zone = {
            'type': zone_type,
            'boundary': boundary,
            'max_speed': max_speed
        }
        self.zones.append(zone)
    
    def check_position(self, position):
        """
        检查位置是否在安全区域内
        position: [x, y, z]
        返回：区域类型和是否允许
        """
        for zone in self.zones:
            if self.is_inside_boundary(position, zone['boundary']):
                if zone['type'] == 'forbidden':
                    return 'forbidden', False
                elif zone['type'] == 'restricted':
                    return 'restricted', True
                else:
                    return 'normal', True
        
        return 'unknown', False
    
    def is_inside_boundary(self, position, boundary):
        """
        检查位置是否在边界内
        """
        min_bound = boundary['min']
        max_bound = boundary['max']
        
        for i in range(3):
            if position[i] < min_bound[i] or position[i] > max_bound[i]:
                return False
        
        return True
    
    def get_max_speed(self, position):
        """
        获取当前位置的最大允许速度
        """
        zone_type, allowed = self.check_position(position)
        
        if zone_type == 'forbidden':
            return 0  # 禁止区域，速度为0
        
        for zone in self.zones:
            if (self.is_inside_boundary(position, zone['boundary']) and
                zone['type'] == 'restricted'):
                return zone['max_speed']
        
        return None  # 正常区域，无速度限制

# 使用示例
monitor = SafetyZoneMonitor()

# 定义禁止区域
monitor.add_zone(
    'forbidden',
    {'min': [0, 0, 0], 'max': [200, 200, 200]}
)

# 定义限制区域
monitor.add_zone(
    'restricted',
    {'min': [200, 200, 0], 'max': [500, 500, 300]},
    max_speed=100  # mm/s
)

# 定义正常工作区域
monitor.add_zone(
    'normal',
    {'min': [500, 500, 0], 'max': [1000, 1000, 500]}
)

# 检查不同位置
test_positions = [
    [100, 100, 100],  # 禁止区域
    [300, 300, 150],  # 限制区域
    [700, 700, 250]   # 正常区域
]

for pos in test_positions:
    zone_type, allowed = monitor.check_position(pos)
    max_speed = monitor.get_max_speed(pos)
    print(f"位置 {pos}: 区域={zone_type}, "
          f"允许={allowed}, 最大速度={max_speed}")
```


## 第六部分：机器人编程

### 6.1 编程方法

**机器人编程方式**：

```
┌─────────────────────────────────────────┐
│        机器人编程方法                    │
├─────────────────────────────────────────┤
│                                         │
│  1. 示教编程（Teaching Programming）    │
│     - 手动示教                          │
│     - 示教器编程                        │
│     优点：直观、易学                    │
│     缺点：效率低、精度受限              │
│                                         │
│  2. 离线编程（Offline Programming）     │
│     - 使用仿真软件                      │
│     - 生成机器人程序                    │
│     优点：不占用机器人、可优化          │
│     缺点：需要精确模型                  │
│                                         │
│  3. 在线编程（Online Programming）      │
│     - 直接编写代码                      │
│     - 实时调试                          │
│     优点：灵活、功能强大                │
│     缺点：需要编程知识                  │
│                                         │
│  4. 视觉引导编程                        │
│     - 基于视觉定位                      │
│     - 自动生成路径                      │
│     优点：适应性强                      │
│     缺点：系统复杂                      │
└─────────────────────────────────────────┘
```

### 6.2 常用编程语言

**主流机器人编程语言**：

#### 6.2.1 RAPID（ABB）

```rapid
MODULE MainModule
    ! 定义工具数据
    PERS tooldata gripper := [TRUE, [[0, 0, 100], [1, 0, 0, 0]], [1, [0, 0, 50], [1, 0, 0, 0], 0, 0, 0]];
    
    ! 定义工件坐标系
    PERS wobjdata workpiece := [FALSE, TRUE, "", [[0, 0, 0], [1, 0, 0, 0]], [[0, 0, 0], [1, 0, 0, 0]]];
    
    ! 主程序
    PROC main()
        ! 移动到初始位置
        MoveJ home, v1000, z50, gripper\WObj:=workpiece;
        
        ! 移动到抓取位置
        MoveL pick_pos, v500, z10, gripper\WObj:=workpiece;
        
        ! 关闭夹爪
        SetDO gripper_close, 1;
        WaitTime 0.5;
        
        ! 移动到放置位置
        MoveL place_pos, v500, z10, gripper\WObj:=workpiece;
        
        ! 打开夹爪
        SetDO gripper_close, 0;
        WaitTime 0.5;
        
        ! 返回初始位置
        MoveJ home, v1000, z50, gripper\WObj:=workpiece;
    ENDPROC
ENDMODULE
```

#### 6.2.2 KRL（KUKA）

```krl
DEF PickAndPlace()
    ; 定义变量
    DECL AXIS HOME
    DECL POS PICK_POS, PLACE_POS
    
    ; 初始化位置
    HOME = {A1 0, A2 -90, A3 90, A4 0, A5 90, A6 0}
    PICK_POS = {X 500, Y 200, Z 300, A 0, B 90, C 0}
    PLACE_POS = {X 500, Y -200, Z 300, A 0, B 90, C 0}
    
    ; 移动到初始位置
    PTP HOME
    
    ; 移动到抓取位置
    LIN PICK_POS
    
    ; 关闭夹爪
    $OUT[1] = TRUE
    WAIT SEC 0.5
    
    ; 移动到放置位置
    LIN PLACE_POS
    
    ; 打开夹爪
    $OUT[1] = FALSE
    WAIT SEC 0.5
    
    ; 返回初始位置
    PTP HOME
END
```

#### 6.2.3 Python（通用/ROS）

```python
import rospy
from moveit_commander import MoveGroupCommander
from geometry_msgs.msg import Pose

class RobotController:
    def __init__(self):
        """初始化机器人控制器"""
        rospy.init_node('robot_controller')
        self.arm = MoveGroupCommander('manipulator')
        self.gripper = MoveGroupCommander('gripper')
    
    def move_to_pose(self, x, y, z, roll, pitch, yaw):
        """
        移动到指定位姿
        x, y, z: 位置（米）
        roll, pitch, yaw: 姿态（弧度）
        """
        target_pose = Pose()
        target_pose.position.x = x
        target_pose.position.y = y
        target_pose.position.z = z
        
        # 设置姿态（四元数）
        from tf.transformations import quaternion_from_euler
        q = quaternion_from_euler(roll, pitch, yaw)
        target_pose.orientation.x = q[0]
        target_pose.orientation.y = q[1]
        target_pose.orientation.z = q[2]
        target_pose.orientation.w = q[3]
        
        # 规划并执行
        self.arm.set_pose_target(target_pose)
        plan = self.arm.plan()
        self.arm.execute(plan, wait=True)
    
    def close_gripper(self):
        """关闭夹爪"""
        self.gripper.set_named_target('closed')
        self.gripper.go(wait=True)
    
    def open_gripper(self):
        """打开夹爪"""
        self.gripper.set_named_target('open')
        self.gripper.go(wait=True)
    
    def pick_and_place(self, pick_pose, place_pose):
        """
        抓取和放置
        pick_pose: 抓取位姿 [x, y, z, roll, pitch, yaw]
        place_pose: 放置位姿 [x, y, z, roll, pitch, yaw]
        """
        # 移动到抓取位置上方
        approach_pose = pick_pose.copy()
        approach_pose[2] += 0.1  # 上方10cm
        self.move_to_pose(*approach_pose)
        
        # 下降到抓取位置
        self.move_to_pose(*pick_pose)
        
        # 关闭夹爪
        self.close_gripper()
        rospy.sleep(0.5)
        
        # 上升
        self.move_to_pose(*approach_pose)
        
        # 移动到放置位置上方
        approach_pose = place_pose.copy()
        approach_pose[2] += 0.1
        self.move_to_pose(*approach_pose)
        
        # 下降到放置位置
        self.move_to_pose(*place_pose)
        
        # 打开夹爪
        self.open_gripper()
        rospy.sleep(0.5)
        
        # 上升
        self.move_to_pose(*approach_pose)

# 使用示例
if __name__ == '__main__':
    robot = RobotController()
    
    # 定义抓取和放置位姿
    pick_pose = [0.5, 0.2, 0.3, 0, 1.57, 0]
    place_pose = [0.5, -0.2, 0.3, 0, 1.57, 0]
    
    # 执行抓取和放置
    robot.pick_and_place(pick_pose, place_pose)
```

### 6.3 编程实例：搬运任务

**任务描述**：
从传送带A抓取工件，放置到传送带B

**完整程序示例**：

```python
class ConveyorPickPlace:
    def __init__(self, robot_controller, vision_system):
        """
        传送带搬运系统
        robot_controller: 机器人控制器
        vision_system: 视觉系统
        """
        self.robot = robot_controller
        self.vision = vision_system
        self.running = False
    
    def start(self):
        """启动搬运任务"""
        self.running = True
        
        while self.running:
            # 1. 等待工件到达
            if self.wait_for_workpiece():
                # 2. 视觉定位
                workpiece_pose = self.vision.detect_workpiece()
                
                if workpiece_pose is not None:
                    # 3. 抓取工件
                    success = self.pick_workpiece(workpiece_pose)
                    
                    if success:
                        # 4. 放置工件
                        self.place_workpiece()
                        
                        # 5. 返回初始位置
                        self.robot.move_to_home()
    
    def wait_for_workpiece(self):
        """
        等待工件到达抓取位置
        返回：是否检测到工件
        """
        # 检查传感器
        sensor_value = self.robot.read_digital_input(1)
        return sensor_value == 1
    
    def pick_workpiece(self, pose):
        """
        抓取工件
        pose: 工件位姿
        返回：是否成功
        """
        try:
            # 移动到抓取位置上方
            approach_pose = pose.copy()
            approach_pose[2] += 100  # 上方100mm
            self.robot.move_to_pose(*approach_pose)
            
            # 下降到抓取位置
            self.robot.move_to_pose(*pose)
            
            # 关闭夹爪
            self.robot.close_gripper()
            
            # 检查是否抓取成功
            if self.robot.check_gripper_closed():
                # 上升
                self.robot.move_to_pose(*approach_pose)
                return True
            else:
                # 抓取失败
                self.robot.open_gripper()
                return False
        
        except Exception as e:
            print(f"抓取失败: {e}")
            return False
    
    def place_workpiece(self):
        """放置工件"""
        # 预定义的放置位置
        place_pose = [600, -200, 300, 0, 90, 0]
        
        # 移动到放置位置上方
        approach_pose = place_pose.copy()
        approach_pose[2] += 100
        self.robot.move_to_pose(*approach_pose)
        
        # 下降到放置位置
        self.robot.move_to_pose(*place_pose)
        
        # 打开夹爪
        self.robot.open_gripper()
        
        # 上升
        self.robot.move_to_pose(*approach_pose)
    
    def stop(self):
        """停止搬运任务"""
        self.running = False

# 使用示例
robot = RobotController()
vision = VisionSystem()

conveyor_system = ConveyorPickPlace(robot, vision)
conveyor_system.start()
```

### 6.4 高级编程技巧

#### 6.4.1 力控制编程

```python
class ForceControlledAssembly:
    def __init__(self, robot, force_sensor):
        """
        力控制装配
        robot: 机器人控制器
        force_sensor: 力传感器
        """
        self.robot = robot
        self.force_sensor = force_sensor
        self.max_force = 50  # N
        self.target_force = 20  # N
    
    def insert_with_force_control(self, target_pose):
        """
        力控制插入
        target_pose: 目标位姿
        """
        # 移动到插入位置上方
        approach_pose = target_pose.copy()
        approach_pose[2] += 50  # 上方50mm
        self.robot.move_to_pose(*approach_pose)
        
        # 开始力控制下降
        current_pose = approach_pose
        step_size = 0.5  # mm
        
        while current_pose[2] > target_pose[2]:
            # 读取力传感器
            force = self.force_sensor.read_force()
            force_z = force['force'][2]
            
            # 检查力是否超过最大值
            if abs(force_z) > self.max_force:
                print("力过大，停止插入")
                break
            
            # 检查是否到达目标力
            if abs(force_z) >= self.target_force:
                print("到达目标力，插入完成")
                break
            
            # 继续下降
            current_pose[2] -= step_size
            self.robot.move_to_pose(*current_pose)
            
            # 短暂延时
            time.sleep(0.01)
```

#### 6.4.2 轨迹跟踪

```python
class TrajectoryFollower:
    def __init__(self, robot):
        """
        轨迹跟踪器
        robot: 机器人控制器
        """
        self.robot = robot
    
    def follow_trajectory(self, trajectory, timestamps):
        """
        跟踪轨迹
        trajectory: 轨迹点列表
        timestamps: 时间戳列表
        """
        start_time = time.time()
        
        for i, (point, timestamp) in enumerate(zip(trajectory, timestamps)):
            # 等待到达时间点
            while (time.time() - start_time) < timestamp:
                time.sleep(0.001)
            
            # 移动到轨迹点
            self.robot.move_to_pose(*point)
            
            # 记录实际位置（用于误差分析）
            actual_pose = self.robot.get_current_pose()
            error = self.calculate_error(point, actual_pose)
            
            if error > 5.0:  # mm
                print(f"警告：轨迹跟踪误差过大: {error:.2f}mm")
    
    def calculate_error(self, target, actual):
        """计算位置误差"""
        return np.linalg.norm(
            np.array(target[:3]) - np.array(actual[:3])
        )
```


## 第七部分：实践项目 - 装配工作站

### 7.1 项目概述

**项目目标**：
设计并实现一个自动化装配工作站，使用工业机器人完成零件的抓取、装配和检测。

**系统组成**：
```
┌─────────────────────────────────────────┐
│        装配工作站系统                    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐      ┌──────────┐       │
│  │ 零件料仓A│      │ 零件料仓B│       │
│  └────┬─────┘      └────┬─────┘       │
│       │                 │              │
│       └────────┬────────┘              │
│                │                        │
│           ┌────┴────┐                  │
│           │ 机器人  │                  │
│           │         │                  │
│           └────┬────┘                  │
│                │                        │
│       ┌────────┴────────┐              │
│       │                 │              │
│  ┌────┴─────┐     ┌────┴─────┐       │
│  │ 装配工位 │     │ 检测工位 │       │
│  └──────────┘     └──────────┘       │
│                                         │
│  ┌──────────────────────────┐         │
│  │ 控制系统                 │         │
│  │ - PLC                    │         │
│  │ - 机器人控制器           │         │
│  │ - 视觉系统               │         │
│  │ - HMI                    │         │
│  └──────────────────────────┘         │
└─────────────────────────────────────────┘
```

**技术要求**：
- 6轴工业机器人
- 视觉定位系统
- 力传感器
- PLC控制系统
- 安全防护系统

### 7.2 系统设计

#### 7.2.1 硬件配置

```
设备清单：
┌────────────────┬──────────┬────────┐
│ 设备名称       │ 型号     │ 数量   │
├────────────────┼──────────┼────────┤
│ 工业机器人     │ 6轴      │ 1      │
│ 机器人控制器   │ -        │ 1      │
│ 夹爪           │ 电动     │ 1      │
│ 力传感器       │ 6维      │ 1      │
│ 工业相机       │ 2D       │ 2      │
│ 光源           │ LED      │ 2      │
│ PLC            │ -        │ 1      │
│ 触摸屏HMI      │ 10寸     │ 1      │
│ 安全光栅       │ -        │ 2      │
│ 急停按钮       │ -        │ 2      │
│ 零件料仓       │ 振动盘   │ 2      │
└────────────────┴──────────┴────────┘
```

#### 7.2.2 工艺流程

```
装配流程：
┌─────────────────────────────────────┐
│  1. 初始化                          │
│     - 系统自检                      │
│     - 回零点                        │
│     - 相机标定                      │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│  2. 抓取零件A                       │
│     - 视觉定位                      │
│     - 移动到抓取位置                │
│     - 夹取零件                      │
│     - 检查抓取状态                  │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│  3. 抓取零件B                       │
│     - 视觉定位                      │
│     - 移动到抓取位置                │
│     - 夹取零件                      │
│     - 检查抓取状态                  │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│  4. 装配                            │
│     - 移动到装配位置                │
│     - 力控制插入                    │
│     - 检查装配质量                  │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│  5. 检测                            │
│     - 移动到检测位置                │
│     - 视觉检测                      │
│     - 判断合格/不合格               │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│  6. 分拣                            │
│     - 合格品 → 合格料仓             │
│     - 不合格品 → 不合格料仓         │
└─────────────────────────────────────┘
```

### 7.3 程序实现

#### 7.3.1 主控制程序

```python
class AssemblyStation:
    def __init__(self):
        """初始化装配工作站"""
        # 初始化各子系统
        self.robot = RobotController()
        self.vision = VisionSystem()
        self.force_sensor = ForceSensor()
        self.plc = PLCController()
        
        # 状态变量
        self.running = False
        self.cycle_count = 0
        self.good_count = 0
        self.bad_count = 0
    
    def initialize(self):
        """系统初始化"""
        print("系统初始化...")
        
        # 机器人回零
        self.robot.move_to_home()
        
        # 相机标定
        self.vision.calibrate()
        
        # 力传感器校准
        self.force_sensor.calibrate([0, 0, 0, 0, 0, 0])
        
        # PLC初始化
        self.plc.initialize()
        
        print("初始化完成")
    
    def run_cycle(self):
        """运行一个装配周期"""
        try:
            # 1. 抓取零件A
            part_a = self.pick_part_from_feeder('A')
            if part_a is None:
                raise Exception("抓取零件A失败")
            
            # 2. 抓取零件B
            part_b = self.pick_part_from_feeder('B')
            if part_b is None:
                raise Exception("抓取零件B失败")
            
            # 3. 装配
            assembly_success = self.assemble_parts(part_a, part_b)
            if not assembly_success:
                raise Exception("装配失败")
            
            # 4. 检测
            quality_ok = self.inspect_assembly()
            
            # 5. 分拣
            if quality_ok:
                self.place_to_good_bin()
                self.good_count += 1
            else:
                self.place_to_bad_bin()
                self.bad_count += 1
            
            # 更新计数
            self.cycle_count += 1
            
            return True
        
        except Exception as e:
            print(f"周期执行失败: {e}")
            self.handle_error()
            return False
    
    def pick_part_from_feeder(self, feeder_id):
        """
        从料仓抓取零件
        feeder_id: 'A' 或 'B'
        """
        print(f"从料仓{feeder_id}抓取零件...")
        
        # 等待零件到位
        if not self.wait_for_part(feeder_id):
            return None
        
        # 视觉定位
        part_pose = self.vision.detect_part(feeder_id)
        if part_pose is None:
            print("视觉定位失败")
            return None
        
        # 移动到抓取位置
        approach_pose = part_pose.copy()
        approach_pose[2] += 50  # 上方50mm
        self.robot.move_to_pose(*approach_pose)
        
        # 下降
        self.robot.move_to_pose(*part_pose)
        
        # 夹取
        self.robot.close_gripper()
        time.sleep(0.3)
        
        # 检查抓取
        if not self.robot.check_gripper_closed():
            print("抓取失败")
            self.robot.open_gripper()
            return None
        
        # 上升
        self.robot.move_to_pose(*approach_pose)
        
        return part_pose
    
    def assemble_parts(self, part_a, part_b):
        """
        装配零件
        part_a, part_b: 零件位姿
        """
        print("开始装配...")
        
        # 移动到装配位置
        assembly_pose = [400, 0, 300, 0, 90, 0]
        self.robot.move_to_pose(*assembly_pose)
        
        # 力控制插入
        success = self.force_controlled_insertion(
            target_force=20,  # N
            max_force=50,     # N
            insertion_depth=30  # mm
        )
        
        if success:
            print("装配完成")
            return True
        else:
            print("装配失败")
            return False
    
    def force_controlled_insertion(self, target_force, max_force, insertion_depth):
        """
        力控制插入
        target_force: 目标力（N）
        max_force: 最大力（N）
        insertion_depth: 插入深度（mm）
        """
        current_depth = 0
        step_size = 0.5  # mm
        
        while current_depth < insertion_depth:
            # 读取力传感器
            force_data = self.force_sensor.read_force()
            force_z = abs(force_data['force'][2])
            
            # 检查力
            if force_z > max_force:
                print(f"力过大: {force_z:.1f}N")
                return False
            
            if force_z >= target_force:
                print(f"到达目标力: {force_z:.1f}N")
                return True
            
            # 继续插入
            current_pose = self.robot.get_current_pose()
            current_pose[2] -= step_size
            self.robot.move_to_pose(*current_pose)
            
            current_depth += step_size
            time.sleep(0.01)
        
        return True
    
    def inspect_assembly(self):
        """检测装配质量"""
        print("检测装配质量...")
        
        # 移动到检测位置
        inspect_pose = [500, 0, 400, 0, 90, 0]
        self.robot.move_to_pose(*inspect_pose)
        
        # 视觉检测
        result = self.vision.inspect_quality()
        
        if result['ok']:
            print("检测合格")
            return True
        else:
            print(f"检测不合格: {result['reason']}")
            return False
    
    def place_to_good_bin(self):
        """放置到合格料仓"""
        print("放置到合格料仓")
        good_bin_pose = [600, 200, 300, 0, 90, 0]
        self.robot.move_to_pose(*good_bin_pose)
        self.robot.open_gripper()
        time.sleep(0.3)
    
    def place_to_bad_bin(self):
        """放置到不合格料仓"""
        print("放置到不合格料仓")
        bad_bin_pose = [600, -200, 300, 0, 90, 0]
        self.robot.move_to_pose(*bad_bin_pose)
        self.robot.open_gripper()
        time.sleep(0.3)
    
    def wait_for_part(self, feeder_id):
        """等待零件到位"""
        timeout = 10  # 秒
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            # 检查传感器
            sensor_id = 1 if feeder_id == 'A' else 2
            if self.plc.read_digital_input(sensor_id):
                return True
            time.sleep(0.1)
        
        print(f"等待料仓{feeder_id}超时")
        return False
    
    def handle_error(self):
        """错误处理"""
        print("处理错误...")
        
        # 打开夹爪
        self.robot.open_gripper()
        
        # 返回安全位置
        self.robot.move_to_home()
        
        # 等待操作员处理
        print("等待操作员确认...")
    
    def start(self):
        """启动工作站"""
        print("启动装配工作站...")
        
        # 初始化
        self.initialize()
        
        # 主循环
        self.running = True
        while self.running:
            # 检查启动信号
            if self.plc.read_digital_input(10):  # 启动按钮
                # 运行一个周期
                self.run_cycle()
                
                # 显示统计
                print(f"周期: {self.cycle_count}, "
                      f"合格: {self.good_count}, "
                      f"不合格: {self.bad_count}")
            
            # 检查停止信号
            if self.plc.read_digital_input(11):  # 停止按钮
                self.stop()
            
            time.sleep(0.1)
    
    def stop(self):
        """停止工作站"""
        print("停止装配工作站...")
        self.running = False
        self.robot.move_to_home()

# 主程序
if __name__ == '__main__':
    station = AssemblyStation()
    station.start()
```

### 7.4 调试与优化

#### 7.4.1 调试步骤

```
1. 单步调试
   - 逐个测试每个功能模块
   - 验证机器人运动
   - 验证传感器读取
   - 验证视觉定位

2. 集成测试
   - 测试完整流程
   - 检查各模块协调
   - 验证时序关系

3. 性能优化
   - 优化运动轨迹
   - 减少等待时间
   - 提高节拍

4. 安全测试
   - 测试急停功能
   - 测试安全光栅
   - 测试碰撞检测
   - 测试力限制
```

#### 7.4.2 常见问题

```
问题1：抓取失败
原因：
- 视觉定位不准
- 夹爪位置偏差
- 零件姿态异常

解决：
- 重新标定相机
- 调整夹爪参数
- 增加姿态检测

问题2：装配失败
原因：
- 零件对位不准
- 插入力过大
- 零件尺寸偏差

解决：
- 优化视觉定位
- 调整力控参数
- 增加柔性补偿

问题3：节拍慢
原因：
- 运动速度保守
- 等待时间过长
- 轨迹不优化

解决：
- 提高运动速度
- 减少不必要等待
- 优化运动轨迹
```


## 第八部分：维护与故障排除

### 8.1 日常维护

**维护计划**：

```
┌─────────────────────────────────────────┐
│        机器人维护计划                    │
├─────────────────────────────────────────┤
│                                         │
│  每日维护：                             │
│  - 检查外观和清洁                       │
│  - 检查急停按钮                         │
│  - 检查示教器                           │
│  - 检查夹爪动作                         │
│                                         │
│  每周维护：                             │
│  - 检查电缆和接头                       │
│  - 检查润滑状态                         │
│  - 检查传感器                           │
│  - 清理工作区域                         │
│                                         │
│  每月维护：                             │
│  - 检查减速器                           │
│  - 检查制动器                           │
│  - 检查电机                             │
│  - 备份程序和参数                       │
│                                         │
│  每季度维护：                           │
│  - 更换润滑油                           │
│  - 检查电池                             │
│  - 校准精度                             │
│  - 全面检查                             │
│                                         │
│  每年维护：                             │
│  - 大修和保养                           │
│  - 更换易损件                           │
│  - 性能测试                             │
│  - 安全认证                             │
└─────────────────────────────────────────┘
```

### 8.2 故障诊断

**常见故障及处理**：

```
故障1：机器人无法启动
┌─────────────────────────────────────┐
│ 可能原因：                          │
│ 1. 电源故障                         │
│ 2. 急停按下                         │
│ 3. 控制器故障                       │
│ 4. 通信故障                         │
│                                     │
│ 排查步骤：                          │
│ 1. 检查电源指示灯                   │
│ 2. 检查急停按钮状态                 │
│ 3. 检查控制器显示                   │
│ 4. 检查通信电缆                     │
│                                     │
│ 解决方法：                          │
│ 1. 检查电源供应                     │
│ 2. 复位急停按钮                     │
│ 3. 重启控制器                       │
│ 4. 重新连接电缆                     │
└─────────────────────────────────────┘

故障2：定位精度下降
┌─────────────────────────────────────┐
│ 可能原因：                          │
│ 1. 编码器故障                       │
│ 2. 减速器磨损                       │
│ 3. 机械松动                         │
│ 4. 校准参数丢失                     │
│                                     │
│ 排查步骤：                          │
│ 1. 检查编码器读数                   │
│ 2. 检查关节间隙                     │
│ 3. 检查紧固件                       │
│ 4. 检查校准数据                     │
│                                     │
│ 解决方法：                          │
│ 1. 更换编码器                       │
│ 2. 更换减速器                       │
│ 3. 紧固松动部件                     │
│ 4. 重新校准                         │
└─────────────────────────────────────┘

故障3：运动异常
┌─────────────────────────────────────┐
│ 可能原因：                          │
│ 1. 伺服驱动器故障                   │
│ 2. 电机故障                         │
│ 3. 制动器故障                       │
│ 4. 程序错误                         │
│                                     │
│ 排查步骤：                          │
│ 1. 检查驱动器报警                   │
│ 2. 检查电机温度                     │
│ 3. 检查制动器动作                   │
│ 4. 检查程序逻辑                     │
│                                     │
│ 解决方法：                          │
│ 1. 复位驱动器                       │
│ 2. 冷却或更换电机                   │
│ 3. 调整或更换制动器                 │
│ 4. 修正程序                         │
└─────────────────────────────────────┘
```

### 8.3 预防性维护

**状态监测系统**：

```python
class RobotHealthMonitor:
    def __init__(self, robot):
        """
        机器人健康监测系统
        robot: 机器人控制器
        """
        self.robot = robot
        self.health_data = {
            'temperature': [],
            'current': [],
            'vibration': [],
            'position_error': []
        }
        self.thresholds = {
            'temperature': 80,  # °C
            'current': 10,      # A
            'vibration': 5,     # mm/s
            'position_error': 0.5  # mm
        }
    
    def monitor(self):
        """监测机器人状态"""
        # 读取各关节温度
        temperatures = self.robot.get_joint_temperatures()
        
        # 读取各关节电流
        currents = self.robot.get_joint_currents()
        
        # 读取位置误差
        position_error = self.robot.get_position_error()
        
        # 存储数据
        self.health_data['temperature'].append(temperatures)
        self.health_data['current'].append(currents)
        self.health_data['position_error'].append(position_error)
        
        # 检查异常
        warnings = []
        
        # 检查温度
        for i, temp in enumerate(temperatures):
            if temp > self.thresholds['temperature']:
                warnings.append(f"关节{i}温度过高: {temp}°C")
        
        # 检查电流
        for i, current in enumerate(currents):
            if current > self.thresholds['current']:
                warnings.append(f"关节{i}电流过大: {current}A")
        
        # 检查位置误差
        if position_error > self.thresholds['position_error']:
            warnings.append(f"位置误差过大: {position_error}mm")
        
        return warnings
    
    def predict_maintenance(self):
        """预测维护需求"""
        predictions = []
        
        # 分析温度趋势
        if len(self.health_data['temperature']) > 100:
            temp_trend = self.analyze_trend(
                self.health_data['temperature']
            )
            if temp_trend > 0.1:  # 温度上升趋势
                predictions.append("建议检查冷却系统")
        
        # 分析电流趋势
        if len(self.health_data['current']) > 100:
            current_trend = self.analyze_trend(
                self.health_data['current']
            )
            if current_trend > 0.05:  # 电流上升趋势
                predictions.append("建议检查减速器润滑")
        
        # 分析位置误差趋势
        if len(self.health_data['position_error']) > 100:
            error_trend = self.analyze_trend(
                self.health_data['position_error']
            )
            if error_trend > 0.01:  # 误差增大趋势
                predictions.append("建议重新校准")
        
        return predictions
    
    def analyze_trend(self, data):
        """分析数据趋势（简化的线性回归）"""
        if len(data) < 2:
            return 0
        
        # 取最近100个数据点
        recent_data = data[-100:]
        
        # 计算平均值
        avg_first_half = np.mean(recent_data[:50])
        avg_second_half = np.mean(recent_data[50:])
        
        # 返回趋势（正值表示上升）
        return avg_second_half - avg_first_half

# 使用示例
monitor = RobotHealthMonitor(robot)

# 定期监测
while True:
    warnings = monitor.monitor()
    
    if warnings:
        print("警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # 预测维护
    predictions = monitor.predict_maintenance()
    if predictions:
        print("维护建议:")
        for prediction in predictions:
            print(f"  - {prediction}")
    
    time.sleep(60)  # 每分钟监测一次
```

## 总结

通过本教程的学习，你已经掌握了：

✅ **理论基础**
- 工业机器人的基本结构和分类
- 坐标系统和运动学原理
- 工作空间和运动范围

✅ **运动控制**
- 正运动学和逆运动学计算
- 轨迹规划和插补方法
- 速度规划和优化

✅ **传感器集成**
- 编码器、力传感器的应用
- 视觉系统的集成
- 传感器数据处理

✅ **安全系统**
- 安全标准和等级
- 碰撞检测和力限制
- 安全区域监控

✅ **编程开发**
- 多种编程语言和方法
- 力控制和轨迹跟踪
- 实际应用程序开发

✅ **实践应用**
- 完整的装配工作站项目
- 系统集成和调试
- 维护和故障排除

## 实践练习

为了巩固所学知识，建议完成以下练习：

### 练习1：运动学计算
**要求**：
- 实现3轴机器人的正运动学
- 实现2轴机器人的逆运动学
- 验证计算结果的正确性

### 练习2：轨迹规划
**要求**：
- 实现直线插补算法
- 实现梯形速度规划
- 生成平滑的运动轨迹

### 练习3：视觉定位
**要求**：
- 使用OpenCV检测物体
- 计算物体的位置和姿态
- 实现像素坐标到世界坐标的转换

### 练习4：力控制
**要求**：
- 实现简单的力控制算法
- 模拟力控制插入过程
- 处理力超限情况

## 常见问题解答（FAQ）

**Q1：如何选择合适的工业机器人？**

A：考虑因素：
- 负载能力（需要搬运的重量）
- 工作半径（工作空间大小）
- 重复定位精度（精度要求）
- 运动速度（节拍要求）
- 防护等级（工作环境）
- 预算限制

**Q2：机器人编程难学吗？**

A：
- 示教编程：相对简单，适合初学者
- 离线编程：需要一定的编程基础
- 在线编程：需要较强的编程能力
- 建议从示教编程开始，逐步深入

**Q3：如何提高机器人的定位精度？**

A：
- 定期校准机器人
- 使用高精度编码器
- 减少机械间隙
- 优化运动轨迹
- 使用视觉辅助定位

**Q4：机器人安全如何保证？**

A：
- 遵守安全标准（ISO 10218）
- 安装安全防护装置
- 定期安全检查
- 操作人员培训
- 建立应急预案

**Q5：如何优化机器人的工作节拍？**

A：
- 优化运动轨迹（减少不必要的运动）
- 提高运动速度（在安全范围内）
- 并行处理（多个动作同时进行）
- 减少等待时间
- 优化程序逻辑

## 下一步学习建议

完成本教程后，建议继续学习：

1. **[工业4.0与智能制造](../intermediate/03-industry-4.0.html)** - 了解智能制造的发展趋势
2. **[工业自动化控制系统项目](../advanced/01-industrial-control-system.html)** - 学习完整的自动化系统设计
3. **[SCADA系统应用](../intermediate/01-scada-system.html)** - 深入学习监控系统

## 参考资料

1. ISO 10218-1:2011 - 工业机器人安全标准
2. ISO/TS 15066:2016 - 协作机器人安全要求
3. 《机器人学导论》- John J. Craig
4. 《工业机器人编程与应用》
5. ROS官方文档：http://www.ros.org/
6. ABB机器人技术手册
7. KUKA机器人编程手册

---

**版权声明**：本教程内容仅供学习参考，实际项目应用请遵循相关安全规范和标准。

**反馈与建议**：如果你在学习过程中遇到问题或有改进建议，欢迎通过评论区反馈！

**最后更新**：2024-01-15
