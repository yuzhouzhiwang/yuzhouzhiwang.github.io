---
title: "多轴同步控制：协调运动与插补算法"
description: "深入讲解多电机协调运动的实现方法，涵盖CNC坐标系、G代码、Bresenham推导、3D线性插补、圆弧插补、前瞻算法、GRBL架构分析、电子齿轮，以及完整的2轴XY绘图仪项目"
slug: "multi-axis-synchronization-control"

domain: "底层硬件层"
module: "执行器控制"
content_type: "article"
skill_level: "advanced"

tags:
  - 多轴控制
  - 同步控制
  - 插补算法
  - 电子齿轮
  - CNC
  - 运动控制
  - G代码
  - GRBL
prerequisites:
  - "advanced/02-motion-control-algorithms"
  - "beginner/02-stepper-motor-control"
related_contents:
  - "advanced/01-smart-car-control"
  - "advanced/04-smart-gimbal-project"
  - "advanced/05-robot-arm-project"

estimated_time: 180
difficulty_score: 5

author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
version: "2.0"

language: "zh-CN"
translations: []

status: "published"
is_featured: false
is_premium: false

keywords:
  - 多轴同步
  - 插补算法
  - 电子齿轮
  - CNC控制
  - 协调运动
  - Bresenham算法
  - 圆弧插补
  - 前瞻算法
cover_image: ""
---

# 多轴同步控制：协调运动与插补算法

## 概述

单轴运动控制只需控制一个电机，而多轴系统需要多个电机在时间上精确协调，使末端执行器（刀具、打印头、机械臂末端）沿预定轨迹运动。这是CNC（Computer Numerical Control，计算机数控）机床、3D打印机、工业机器人的核心技术。

**本文学习目标**：

| 目标 | 技能等级 |
|------|---------|
| 理解CNC三种坐标系及G代码结构 | 中级 |
| 推导并实现Bresenham线性插补算法 | 高级 |
| 实现3D线性插补与速度混合 | 高级 |
| 实现圆弧插补与弦误差控制 | 高级 |
| 理解前瞻缓冲区与连续路径执行 | 高级 |
| 分析GRBL架构与实时运动规划 | 专家 |
| 实现电子齿轮同步轴 | 高级 |
| 完成2轴XY绘图仪完整项目 | 项目实战 |

**前置知识**：
- [运动控制算法](02-motion-control-algorithms.html)：梯形/S曲线加减速
- [步进电机控制](../beginner/02-stepper-motor-control.html)：步进电机基础驱动
- FreeRTOS任务与队列基础


## 背景知识

### CNC三种坐标系详解

CNC系统中存在三个相互关联的坐标系，理解它们的关系是编程和调试的基础。

```
┌─────────────────────────────────────────────────────────────────┐
│                    CNC坐标系层次关系                              │
│                                                                   │
│  机械坐标系 (MCS)                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  原点：机器回零后的固定参考点（行程开关位置）               │   │
│  │  范围：机器的物理行程极限                                   │   │
│  │  用途：机器内部位置管理、行程保护                           │   │
│  │                                                            │   │
│  │  工件坐标系 (WCS) G54~G59                                  │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │  原点：工件上的参考点（通常是工件角点或中心）       │    │   │
│  │  │  偏移：相对于机械坐标系的偏移量                    │    │   │
│  │  │  用途：G代码编程的基准                             │    │   │
│  │  │                                                    │    │   │
│  │  │  刀具坐标系 (TCS)                                  │    │   │
│  │  │  ┌──────────────────────────────────────────┐    │    │   │
│  │  │  │  原点：刀尖点                              │    │    │   │
│  │  │  │  补偿：刀具长度补偿(G43)、半径补偿(G41/42)│    │    │   │
│  │  │  │  用途：实际切削路径计算                    │    │    │   │
│  │  │  └──────────────────────────────────────────┘    │    │   │
│  │  └──────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

坐标变换链：
  G代码坐标 → (+WCS偏移) → 机械坐标 → (+刀具补偿) → 实际刀尖位置
```

**机械坐标系 (Machine Coordinate System, MCS)**：
- 以机器回零（Homing）后的参考点为原点
- 坐标值反映各轴电机的绝对位置
- 用于行程限位保护（软限位）
- 断电重启后必须重新回零

**工件坐标系 (Work Coordinate System, WCS)**：
- G54~G59提供6个可存储的工件坐标系
- 通过`G10 L2 P1 X10 Y20`设置G54偏移
- 操作员对刀后设定，编程人员使用WCS编写G代码
- 换工件时只需更新WCS偏移，G代码无需修改

**刀具坐标系 (Tool Coordinate System, TCS)**：
- 刀具长度补偿（G43 H1）：补偿不同刀具的长度差异
- 刀具半径补偿（G41左补偿/G42右补偿）：自动偏移刀具半径
- 使编程人员按工件轮廓编程，无需手动计算刀具偏移

```c
// 坐标系变换实现（嵌入式CNC控制器）
typedef struct {
    float wcs_offset[6][3];   // G54~G59的XYZ偏移（mm）
    float tool_length[32];    // 刀具长度补偿表（mm）
    float tool_radius[32];    // 刀具半径补偿表（mm）
    uint8_t active_wcs;       // 当前激活的工件坐标系（0=G54）
    uint8_t active_tool;      // 当前刀具号
} CoordSystem;

// 工件坐标 → 机械坐标
void wcs_to_mcs(CoordSystem *cs, float wx, float wy, float wz,
                float *mx, float *my, float *mz) {
    uint8_t w = cs->active_wcs;
    *mx = wx + cs->wcs_offset[w][0];
    *my = wy + cs->wcs_offset[w][1];
    *mz = wz + cs->wcs_offset[w][2] + cs->tool_length[cs->active_tool];
}

// 机械坐标 → 工件坐标（用于位置显示）
void mcs_to_wcs(CoordSystem *cs, float mx, float my, float mz,
                float *wx, float *wy, float *wz) {
    uint8_t w = cs->active_wcs;
    *wx = mx - cs->wcs_offset[w][0];
    *wy = my - cs->wcs_offset[w][1];
    *wz = mz - cs->wcs_offset[w][2] - cs->tool_length[cs->active_tool];
}
```

### G代码结构与常用指令

G代码（RS274/NGC标准）是CNC机床的通用编程语言，每行称为一个"程序块"（Block）。

```
G代码程序块结构：
  N10 G01 X100.0 Y50.0 Z-5.0 F1000 S3000 M03

  N10   → 行号（可选）
  G01   → 准备功能（G功能）：直线插补
  X/Y/Z → 坐标字：目标位置（mm）
  F1000 → 进给速度（mm/min）
  S3000 → 主轴转速（RPM）
  M03   → 辅助功能：主轴正转
```

**常用G代码指令**：

| 代码 | 功能 | 示例 |
|------|------|------|
| G00 | 快速定位（不切削） | `G00 X0 Y0 Z5` |
| G01 | 直线插补（切削） | `G01 X100 Y50 F500` |
| G02 | 顺时针圆弧插补 | `G02 X50 Y50 I25 J0 F300` |
| G03 | 逆时针圆弧插补 | `G03 X0 Y50 I-25 J0 F300` |
| G04 | 暂停 | `G04 P500`（暂停500ms） |
| G17 | 选择XY平面（圆弧） | `G17` |
| G20/G21 | 英制/公制单位 | `G21`（毫米） |
| G28 | 回机械原点 | `G28 Z0` |
| G54~G59 | 选择工件坐标系 | `G54` |
| G90/G91 | 绝对/增量坐标 | `G90` |
| G92 | 设置当前位置 | `G92 X0 Y0` |
| M00 | 程序暂停 | `M00` |
| M03/M04/M05 | 主轴正/反/停 | `M03 S2000` |
| M06 | 换刀 | `M06 T2` |
| M30 | 程序结束 | `M30` |

**圆弧指令参数说明**：
```
G02 X50 Y50 I25 J0 F300
     ↑    ↑   ↑   ↑
     终点X 终点Y 圆心相对起点的X偏移 圆心相对起点的Y偏移

或使用半径格式：
G02 X50 Y50 R25 F300
                ↑
                半径（正值=小弧，负值=大弧）
```

**一个完整的G代码程序示例**（铣削矩形轮廓）：
```gcode
%                          ; 程序开始标记
O0001                      ; 程序号
G21 G90 G17                ; 公制，绝对坐标，XY平面
G54                        ; 使用G54工件坐标系
M06 T1                     ; 换1号刀（直径6mm立铣刀）
G43 H1                     ; 刀具长度补偿
M03 S3000                  ; 主轴正转3000RPM
G00 Z5.0                   ; 快速抬刀到Z5
G00 X-3.0 Y-3.0            ; 快速移到起点（含刀具半径偏移）
G01 Z-3.0 F100             ; 下刀到Z-3（切削深度3mm）
G41 D1                     ; 左刀补（刀具半径3mm）
G01 X0 Y0 F500             ; 切入
G01 X100.0 Y0              ; 铣底边
G01 X100.0 Y60.0           ; 铣右边
G01 X0 Y60.0               ; 铣顶边
G01 X0 Y0                  ; 铣左边（回起点）
G40                        ; 取消刀补
G01 Z5.0 F500              ; 抬刀
G00 X0 Y0                  ; 回原点
M05                        ; 主轴停
M30                        ; 程序结束
%
```

### Bresenham线性插补算法推导

Bresenham算法（1965年由Jack Bresenham在IBM提出）是CNC中最经典的插补算法，核心思想是用整数运算近似实数直线，避免浮点运算。

**二维推导过程**：

设从点 P0(x0, y0) 到 P1(x1, y1) 画一条直线，假设 dx > dy > 0（第一象限，斜率 < 1）。

```
理想直线方程：y = y0 + (dy/dx) × (x - x0)

在x = xi时，理想y值为：
  y_ideal = y0 + (dy/dx) × (xi - x0)

实际只能取整数，选择 yi 或 yi+1：
  误差 = y_ideal - yi

Bresenham的关键洞察：
  定义误差项 e = 2×dy×x - 2×dx×y - (2×dy×x0 - 2×dx×y0 - dx)
  
  初始值：e0 = 2×dy - dx
  
  每步x+1时：
    e += 2×dy
    如果 e > 0：y += 1，e -= 2×dx
  
  全程只用整数加减法！
```

**完整推导验证**（以从(0,0)到(7,3)为例）：

```
dx=7, dy=3, e_init = 2×3 - 7 = -1

步骤  x  y  e(步前)  操作
  0   0  0    -1     初始
  1   1  0    -1+6=5  e>0: y+1, e=5-14=-9
  2   2  1    -9+6=-3
  3   3  1    -3+6=3  e>0: y+1, e=3-14=-11
  4   4  2    -11+6=-5
  5   5  2    -5+6=1  e>0: y+1, e=1-14=-13
  6   6  3    -13+6=-7
  7   7  3    完成

轨迹：(0,0)→(1,0)→(2,1)→(3,1)→(4,2)→(5,2)→(6,3)→(7,3) ✓
```


## 核心内容

### 主从同步与电子齿轮

电子齿轮（Electronic Gearing）是用软件模拟机械齿轮传动比的技术，广泛用于龙门结构双驱动、螺纹切削、差速驱动等场景。

```
机械齿轮传动：
  主齿轮（20齿）→ 从齿轮（30齿）
  传动比 = 30/20 = 1.5
  主轴转1圈 → 从轴转1.5圈

电子齿轮等效：
  主轴每发出1个脉冲 → 从轴发出1.5个脉冲
  用累加器处理非整数比：
    累加器 += 1500（比例×1000）
    每当累加器 ≥ 1000：从轴步进1步，累加器 -= 1000
```

**电子齿轮完整实现**：

```c
// 电子齿轮结构体（支持分数齿轮比）
// 文件：electronic_gear.h
// 芯片：STM32F4，HAL库 v1.27
#include <stdint.h>

typedef struct {
    int32_t  master_pos;      // 主轴累计位置（步）
    int32_t  slave_pos;       // 从轴累计位置（步）
    int32_t  numerator;       // 齿轮比分子
    int32_t  denominator;     // 齿轮比分母
    int32_t  accumulator;     // 余数累加器
    int8_t   slave_dir;       // 从轴当前方向
    uint8_t  enabled;         // 使能标志
} ElectronicGear;

// 初始化电子齿轮
// ratio = numerator/denominator（从轴步数/主轴步数）
// 例：ratio=3/2 表示主轴走2步，从轴走3步
void gear_init(ElectronicGear *eg, int32_t numerator, int32_t denominator) {
    eg->master_pos   = 0;
    eg->slave_pos    = 0;
    eg->numerator    = numerator;
    eg->denominator  = denominator;
    eg->accumulator  = 0;
    eg->slave_dir    = 1;
    eg->enabled      = 1;
}

// 主轴步进一步时调用（在主轴步进中断中调用）
// 返回：从轴需要步进的步数（正=正向，负=反向，0=不步进）
int8_t gear_master_step(ElectronicGear *eg, int8_t master_dir) {
    if (!eg->enabled) return 0;

    eg->master_pos += master_dir;
    eg->accumulator += master_dir * eg->numerator;

    int8_t slave_steps = 0;

    // 正向步进
    while (eg->accumulator >= eg->denominator) {
        eg->accumulator -= eg->denominator;
        slave_steps++;
    }
    // 反向步进
    while (eg->accumulator <= -eg->denominator) {
        eg->accumulator += eg->denominator;
        slave_steps--;
    }

    eg->slave_pos += slave_steps;
    return slave_steps;
}

// 使用示例：龙门双驱动（两个电机驱动同一轴）
// 主电机：X轴左侧，从电机：X轴右侧，齿轮比1:1
ElectronicGear gantry_gear;
gear_init(&gantry_gear, 1, 1);  // 1:1同步

// 在X轴步进中断中：
void X_STEP_IRQHandler(void) {
    int8_t dir = gpio_read(X_DIR_PIN) ? 1 : -1;
    int8_t slave_steps = gear_master_step(&gantry_gear, dir);
    
    for (int8_t i = 0; i < abs(slave_steps); i++) {
        // 输出从轴（X2）步进脉冲
        gpio_write(X2_DIR_PIN, slave_steps > 0 ? 1 : 0);
        gpio_pulse(X2_STEP_PIN, 2);  // 2μs脉冲
    }
}
```

**电子齿轮应用场景对比**：

| 应用 | 齿轮比 | 说明 |
|------|--------|------|
| 龙门双驱 | 1:1 | 两侧电机完全同步 |
| 螺纹切削 | 螺距/导程 | 主轴转速与Z轴进给同步 |
| 差速转向 | 可变 | 左右轮速度差控制转向 |
| 凸轮仿形 | 非线性 | 从轴按凸轮曲线跟随主轴 |
| 飞剪 | 速度匹配 | 剪切时与材料速度同步 |

### Bresenham线性插补实现

基于前面的推导，实现完整的2D和3D Bresenham插补器：

```c
// Bresenham 2D线性插补器
// 文件：bresenham.h
// 适用：STM32 + 步进电机驱动器

#include <stdint.h>
#include <stdlib.h>  // abs()

typedef struct {
    int32_t dx, dy;        // 各轴绝对位移（步数）
    int32_t steps;         // 总步数（主轴步数）
    int32_t step;          // 当前步计数
    int32_t err;           // Bresenham误差项
    int8_t  dir_x, dir_y;  // 各轴方向（+1或-1）
    uint8_t done;          // 完成标志
} Bresenham2D;

// 初始化：从(x0,y0)到(x1,y1)，坐标单位为步
void bresenham2d_init(Bresenham2D *b,
                      int32_t x0, int32_t y0,
                      int32_t x1, int32_t y1) {
    int32_t raw_dx = x1 - x0;
    int32_t raw_dy = y1 - y0;

    b->dir_x = (raw_dx >= 0) ? 1 : -1;
    b->dir_y = (raw_dy >= 0) ? 1 : -1;
    b->dx    = abs(raw_dx);
    b->dy    = abs(raw_dy);

    // 以较大轴为主轴（步数更多的轴）
    b->steps = (b->dx > b->dy) ? b->dx : b->dy;
    b->step  = 0;
    b->done  = (b->steps == 0) ? 1 : 0;

    // 初始误差项（Bresenham推导结果）
    if (b->dx >= b->dy) {
        b->err = b->dx - b->dy;  // 主轴为X
    } else {
        b->err = b->dy - b->dx;  // 主轴为Y
    }
}

// 计算下一步各轴步进量
// sx, sy：输出各轴步进（+dir, -dir, 或0）
// 返回：0=还有步骤，1=已完成
uint8_t bresenham2d_step(Bresenham2D *b, int8_t *sx, int8_t *sy) {
    *sx = 0; *sy = 0;
    if (b->done) return 1;

    if (b->dx >= b->dy) {
        // X为主轴：X每步必走，Y按误差决定
        *sx = b->dir_x;
        int32_t e2 = 2 * b->err;
        if (e2 >= -b->dy) { b->err -= b->dy; }
        if (e2 <=  b->dx) { b->err += b->dx; *sy = b->dir_y; }
        // 注意：当e2同时满足两个条件时，X和Y同时步进（对角步）
    } else {
        // Y为主轴
        *sy = b->dir_y;
        int32_t e2 = 2 * b->err;
        if (e2 >= -b->dx) { b->err -= b->dx; }
        if (e2 <=  b->dy) { b->err += b->dy; *sx = b->dir_x; }
    }

    b->step++;
    if (b->step >= b->steps) b->done = 1;
    return b->done;
}

// Bresenham 3D线性插补器
typedef struct {
    int32_t dx, dy, dz;
    int32_t steps;
    int32_t step;
    int32_t err_1, err_2;  // 两个误差项
    int8_t  dir_x, dir_y, dir_z;
    uint8_t dominant;      // 主轴：0=X, 1=Y, 2=Z
    uint8_t done;
} Bresenham3D;

void bresenham3d_init(Bresenham3D *b,
                      int32_t x0, int32_t y0, int32_t z0,
                      int32_t x1, int32_t y1, int32_t z1) {
    b->dx = abs(x1 - x0); b->dir_x = (x1 >= x0) ? 1 : -1;
    b->dy = abs(y1 - y0); b->dir_y = (y1 >= y0) ? 1 : -1;
    b->dz = abs(z1 - z0); b->dir_z = (z1 >= z0) ? 1 : -1;

    // 确定主轴（位移最大的轴）
    if (b->dx >= b->dy && b->dx >= b->dz) {
        b->dominant = 0;  // X为主轴
        b->steps = b->dx;
        b->err_1 = 2 * b->dy - b->dx;
        b->err_2 = 2 * b->dz - b->dx;
    } else if (b->dy >= b->dx && b->dy >= b->dz) {
        b->dominant = 1;  // Y为主轴
        b->steps = b->dy;
        b->err_1 = 2 * b->dx - b->dy;
        b->err_2 = 2 * b->dz - b->dy;
    } else {
        b->dominant = 2;  // Z为主轴
        b->steps = b->dz;
        b->err_1 = 2 * b->dx - b->dz;
        b->err_2 = 2 * b->dy - b->dz;
    }

    b->step = 0;
    b->done = (b->steps == 0) ? 1 : 0;
}

uint8_t bresenham3d_step(Bresenham3D *b,
                         int8_t *sx, int8_t *sy, int8_t *sz) {
    *sx = 0; *sy = 0; *sz = 0;
    if (b->done) return 1;

    switch (b->dominant) {
        case 0:  // X主轴
            *sx = b->dir_x;
            if (b->err_1 > 0) { *sy = b->dir_y; b->err_1 -= 2 * b->dx; }
            if (b->err_2 > 0) { *sz = b->dir_z; b->err_2 -= 2 * b->dx; }
            b->err_1 += 2 * b->dy;
            b->err_2 += 2 * b->dz;
            break;
        case 1:  // Y主轴
            *sy = b->dir_y;
            if (b->err_1 > 0) { *sx = b->dir_x; b->err_1 -= 2 * b->dy; }
            if (b->err_2 > 0) { *sz = b->dir_z; b->err_2 -= 2 * b->dy; }
            b->err_1 += 2 * b->dx;
            b->err_2 += 2 * b->dz;
            break;
        case 2:  // Z主轴
            *sz = b->dir_z;
            if (b->err_1 > 0) { *sx = b->dir_x; b->err_1 -= 2 * b->dz; }
            if (b->err_2 > 0) { *sy = b->dir_y; b->err_2 -= 2 * b->dz; }
            b->err_1 += 2 * b->dx;
            b->err_2 += 2 * b->dy;
            break;
    }

    b->step++;
    if (b->step >= b->steps) b->done = 1;
    return b->done;
}
```


### 3D线性插补与速度混合

在实际CNC系统中，插补不仅要计算路径，还要控制合成速度（进给速度）。速度混合（Velocity Blending）是指在两段路径的连接点处平滑过渡速度，避免完全停止。

```
速度混合示意图：

  段1（F=1000mm/min）    段2（F=800mm/min）
  ─────────────────→ ●─────────────────→
                     ↑
                  转角点
  
  不混合：在●处减速到0，再加速
  ┌─────────────────────────────────────┐
  │速度                                  │
  │ ████████                  ████████  │
  │         ████          ████          │
  │              ████████               │
  │                  0                  │
  └─────────────────────────────────────┘
  
  速度混合：在●处保持一定速度
  ┌─────────────────────────────────────┐
  │速度                                  │
  │ ████████████████████████████████    │
  │          ████████████████           │
  │                                     │
  └─────────────────────────────────────┘
```

**转角速度计算**：

```c
#include <math.h>

// 计算两段路径在连接点的最大安全过渡速度
// v1_dir[3]: 段1的单位方向向量
// v2_dir[3]: 段2的单位方向向量
// v_max: 最大允许速度（mm/min）
// junction_deviation: 允许的路径偏差（mm），通常0.05~0.1mm
float calc_junction_speed(float v1_dir[3], float v2_dir[3],
                          float v_max, float junction_deviation) {
    // 计算两段方向向量的点积（cos θ）
    float cos_theta = -(v1_dir[0] * v2_dir[0] +
                        v1_dir[1] * v2_dir[1] +
                        v1_dir[2] * v2_dir[2]);

    // 限制在[-1, 1]范围内（防止浮点误差）
    if (cos_theta < -1.0f) cos_theta = -1.0f;
    if (cos_theta >  1.0f) cos_theta =  1.0f;

    // 如果方向几乎相同（cos_theta ≈ -1），可以全速通过
    if (cos_theta <= -0.999f) return v_max;

    // 如果方向完全相反（180°转弯），必须停止
    if (cos_theta >= 0.999f) return 0.0f;

    // 基于junction_deviation的速度限制
    // 推导：圆弧半径 r = junction_deviation / (1 - cos_theta)
    // 向心加速度 a = v² / r ≤ a_max
    // 简化公式（GRBL使用）：
    float sin_half = sqrtf((1.0f - cos_theta) / 2.0f);
    if (sin_half < 1e-6f) return v_max;

    float r = junction_deviation * sin_half / (1.0f - sin_half);
    // 假设最大加速度 a_max = 500 mm/s²
    float a_max = 500.0f / 3600.0f;  // 转换为 mm/min²
    float v_junction = sqrtf(a_max * r) * 60.0f;  // mm/min

    return (v_junction < v_max) ? v_junction : v_max;
}

// 运动段结构（含速度规划信息）
typedef struct {
    float  target[3];        // 目标位置（mm）
    float  feed_rate;        // 编程进给速度（mm/min）
    float  entry_speed;      // 段入口速度（mm/min）
    float  exit_speed;       // 段出口速度（mm/min）
    float  max_junction_speed; // 最大过渡速度（mm/min）
    float  length;           // 段长度（mm）
    uint8_t motion_type;     // 0=G00, 1=G01, 2=G02, 3=G03
    uint8_t recalculate;     // 需要重新规划标志
} MotionBlock;

// 计算段长度
float block_length(float *start, float *end) {
    float dx = end[0] - start[0];
    float dy = end[1] - start[1];
    float dz = end[2] - start[2];
    return sqrtf(dx*dx + dy*dy + dz*dz);
}
```

### 圆弧插补与弦误差控制

圆弧插补需要将圆弧离散化为小线段，弦误差（Chord Error）是圆弧与近似折线之间的最大偏差。

```
弦误差示意图：

        圆弧（理想路径）
       ╭──────────────╮
      ╱                ╲
     ╱    弦误差δ        ╲
    ●──────────────────────●
    起点        弦          终点
    
    δ = R - R×cos(θ/2) = R×(1 - cos(θ/2))
    
    给定最大允许弦误差 δ_max：
    θ_max = 2×arccos(1 - δ_max/R)
    
    每段圆弧的步进角度不超过 θ_max
```

```c
// 圆弧插补器（支持弦误差控制）
// 文件：arc_interp.c
#include <math.h>
#include <stdint.h>

#define ARC_CHORD_ERROR_MAX  0.002f  // 最大弦误差：0.002mm（2μm）
#define PI                   3.14159265358979f

typedef struct {
    float    cx, cy;          // 圆心坐标（mm）
    float    radius;          // 半径（mm）
    float    start_angle;     // 起始角度（rad）
    float    end_angle;       // 终止角度（rad）
    float    angle_step;      // 每步角度增量（rad）
    float    current_angle;   // 当前角度（rad）
    int32_t  total_steps;     // 总步数
    int32_t  step;            // 当前步
    float    last_x, last_y;  // 上一步坐标（mm）
    int8_t   clockwise;       // 1=顺时针(G02), 0=逆时针(G03)
    uint8_t  done;
} ArcInterp;

// 初始化圆弧插补器
// start[2]: 起点坐标（mm）
// end[2]:   终点坐标（mm）
// center[2]: 圆心坐标（mm）
// clockwise: 1=G02顺时针, 0=G03逆时针
void arc_init(ArcInterp *arc,
              float start[2], float end[2], float center[2],
              int8_t clockwise) {
    arc->cx = center[0];
    arc->cy = center[1];
    arc->clockwise = clockwise;

    // 计算半径（验证起点和终点到圆心距离相等）
    float r_start = sqrtf((start[0]-center[0])*(start[0]-center[0]) +
                          (start[1]-center[1])*(start[1]-center[1]));
    float r_end   = sqrtf((end[0]-center[0])*(end[0]-center[0]) +
                          (end[1]-center[1])*(end[1]-center[1]));
    arc->radius = (r_start + r_end) / 2.0f;  // 取平均（容错）

    // 计算起止角度
    arc->start_angle = atan2f(start[1] - center[1], start[0] - center[0]);
    arc->end_angle   = atan2f(end[1]   - center[1], end[0]   - center[0]);

    // 根据方向调整角度范围
    float total_angle;
    if (clockwise) {
        // G02顺时针：角度递减
        total_angle = arc->start_angle - arc->end_angle;
        if (total_angle <= 0) total_angle += 2 * PI;
        total_angle = -total_angle;  // 负值表示顺时针
    } else {
        // G03逆时针：角度递增
        total_angle = arc->end_angle - arc->start_angle;
        if (total_angle <= 0) total_angle += 2 * PI;
    }

    // 根据弦误差计算最大步进角度
    // δ = R(1 - cos(θ/2)) → θ = 2×arccos(1 - δ/R)
    float max_angle_step = 2.0f * acosf(1.0f - ARC_CHORD_ERROR_MAX / arc->radius);
    if (max_angle_step > 0.1f) max_angle_step = 0.1f;  // 最大5.7°

    // 计算总步数
    arc->total_steps = (int32_t)(fabsf(total_angle) / max_angle_step) + 1;
    arc->angle_step  = total_angle / arc->total_steps;

    arc->current_angle = arc->start_angle;
    arc->last_x = start[0];
    arc->last_y = start[1];
    arc->step = 0;
    arc->done = 0;
}

// 获取下一步的位移增量（mm）
// dx, dy: 输出位移增量
uint8_t arc_step(ArcInterp *arc, float *dx, float *dy) {
    *dx = 0; *dy = 0;
    if (arc->done) return 1;

    arc->current_angle += arc->angle_step;
    arc->step++;

    float new_x = arc->cx + arc->radius * cosf(arc->current_angle);
    float new_y = arc->cy + arc->radius * sinf(arc->current_angle);

    *dx = new_x - arc->last_x;
    *dy = new_y - arc->last_y;

    arc->last_x = new_x;
    arc->last_y = new_y;

    if (arc->step >= arc->total_steps) arc->done = 1;
    return arc->done;
}

// 将mm位移转换为步数（考虑各轴分辨率）
// steps_per_mm: 各轴的步/mm分辨率
void mm_to_steps(float dx, float dy,
                 float steps_per_mm_x, float steps_per_mm_y,
                 int32_t *sx, int32_t *sy) {
    *sx = (int32_t)(dx * steps_per_mm_x);
    *sy = (int32_t)(dy * steps_per_mm_y);
}
```

### 前瞻缓冲区与连续路径执行

前瞻（Look-ahead）算法预先分析后续多个运动段，在转角处计算安全过渡速度，实现连续平滑运动。

```
前瞻缓冲区工作原理：

  G代码解析 → [段1][段2][段3][段4][段5] → 运动执行
                ↑                    ↑
              最旧段              最新段
  
  规划过程（反向传播）：
  1. 段5出口速度 = 0（最后一段必须停止）
  2. 段4出口速度 = min(段5入口速度, 段4最大速度)
  3. 段3出口速度 = min(段4入口速度, 段3最大速度)
  4. ...依此类推
  
  每次新段加入时重新规划
```

```c
// 前瞻缓冲区实现
#define LOOKAHEAD_BUFFER_SIZE  32  // 前瞻段数

typedef struct {
    MotionBlock blocks[LOOKAHEAD_BUFFER_SIZE];
    uint8_t     head;          // 写入位置
    uint8_t     tail;          // 执行位置
    uint8_t     count;         // 当前段数
    float       current_pos[3]; // 当前位置（mm）
} LookaheadBuffer;

LookaheadBuffer la_buf;

// 添加新运动段到前瞻缓冲区
// 返回：0=成功，1=缓冲区满
uint8_t lookahead_add_block(LookaheadBuffer *buf,
                             float target[3], float feed_rate,
                             uint8_t motion_type) {
    if (buf->count >= LOOKAHEAD_BUFFER_SIZE) return 1;  // 缓冲区满

    MotionBlock *block = &buf->blocks[buf->head];
    block->target[0] = target[0];
    block->target[1] = target[1];
    block->target[2] = target[2];
    block->feed_rate = feed_rate;
    block->motion_type = motion_type;
    block->length = block_length(buf->current_pos, target);
    block->exit_speed = 0;  // 初始假设停止
    block->recalculate = 1;

    // 计算与前一段的过渡速度
    if (buf->count > 0) {
        uint8_t prev_idx = (buf->head - 1 + LOOKAHEAD_BUFFER_SIZE) % LOOKAHEAD_BUFFER_SIZE;
        MotionBlock *prev = &buf->blocks[prev_idx];

        // 计算方向向量
        float v1[3], v2[3];
        float prev_len = prev->length;
        float curr_len = block->length;

        if (prev_len > 1e-6f && curr_len > 1e-6f) {
            for (int i = 0; i < 3; i++) {
                // 注意：prev->target是终点，需要知道起点
                // 简化：使用当前位置作为当前段起点
                v2[i] = (target[i] - buf->current_pos[i]) / curr_len;
            }
            // 实际实现需要存储每段的起点
            block->max_junction_speed = calc_junction_speed(v1, v2,
                                                             feed_rate, 0.05f);
        } else {
            block->max_junction_speed = 0;
        }
    } else {
        block->max_junction_speed = 0;  // 第一段从静止开始
    }

    // 更新当前位置
    buf->current_pos[0] = target[0];
    buf->current_pos[1] = target[1];
    buf->current_pos[2] = target[2];

    buf->head = (buf->head + 1) % LOOKAHEAD_BUFFER_SIZE;
    buf->count++;

    // 触发速度规划（反向传播）
    lookahead_recalculate(buf);

    return 0;
}

// 反向传播速度规划
void lookahead_recalculate(LookaheadBuffer *buf) {
    if (buf->count < 2) return;

    // 从最新段向最旧段反向传播
    uint8_t idx = (buf->head - 1 + LOOKAHEAD_BUFFER_SIZE) % LOOKAHEAD_BUFFER_SIZE;
    float next_entry_speed = 0;  // 最后一段出口速度为0

    for (uint8_t i = 0; i < buf->count; i++) {
        MotionBlock *block = &buf->blocks[idx];

        // 计算该段能达到的最大出口速度
        // 基于加速度限制：v² = v0² + 2×a×d
        float a_max = 500.0f;  // mm/min²（简化）
        float v_max_exit = sqrtf(next_entry_speed * next_entry_speed +
                                  2.0f * a_max * block->length);
        if (v_max_exit > block->feed_rate) v_max_exit = block->feed_rate;
        if (v_max_exit > block->max_junction_speed)
            v_max_exit = block->max_junction_speed;

        block->exit_speed = v_max_exit;
        next_entry_speed = v_max_exit;

        idx = (idx - 1 + LOOKAHEAD_BUFFER_SIZE) % LOOKAHEAD_BUFFER_SIZE;
    }
}
```


### FreeRTOS多轴任务架构

在实际系统中，多轴控制采用三层任务分离架构，各层通过队列通信：

```
┌─────────────────────────────────────────────────────────────────┐
│                    多轴控制任务架构                               │
│                                                                   │
│  ┌─────────────────┐                                             │
│  │  G代码解析任务   │  优先级：1（最低）                          │
│  │  (gcode_task)   │  从串口/SD卡读取G代码                       │
│  └────────┬────────┘                                             │
│           │ xQueueSend(motion_queue)                             │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │  运动规划任务   │  优先级：2（中）                             │
│  │  (planner_task) │  前瞻算法、速度规划                         │
│  └────────┬────────┘                                             │
│           │ xQueueSend(step_queue)                               │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │  步进输出任务   │  优先级：3（最高）                           │
│  │  (stepper_task) │  定时器中断精确输出脉冲                      │
│  └─────────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

```c
// FreeRTOS多轴控制完整框架
// 文件：motion_control.c
// 芯片：STM32F407，FreeRTOS v10.4，HAL v1.27
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include <math.h>
#include <string.h>

// 队列句柄
QueueHandle_t motion_queue;   // G代码解析 → 运动规划
QueueHandle_t step_queue;     // 运动规划 → 步进输出

// 步进输出条目
typedef struct {
    uint8_t  step_mask;    // 步进位掩码（bit0=X, bit1=Y, bit2=Z）
    uint8_t  dir_mask;     // 方向位掩码
    uint32_t delay_us;     // 到下一步的延时（μs）
} StepEntry;

// 步进缓冲区（环形，DMA友好）
#define STEP_BUF_SIZE  512
StepEntry step_buf[STEP_BUF_SIZE];
volatile uint16_t step_buf_head = 0;
volatile uint16_t step_buf_tail = 0;

// 当前轴位置（步）
volatile int32_t axis_pos[3] = {0, 0, 0};

// G代码解析任务
void gcode_task(void *pvParameters) {
    MotionBlock block;
    char line[128];

    for (;;) {
        // 从串口读取一行G代码
        if (uart_readline(line, sizeof(line), portMAX_DELAY) == 0) {
            // 解析G代码行
            if (gcode_parse(line, &block) == 0) {
                // 发送到运动规划队列（阻塞等待空间）
                xQueueSend(motion_queue, &block, portMAX_DELAY);
            }
        }
    }
}

// 运动规划任务
void planner_task(void *pvParameters) {
    MotionBlock block;
    static float current_pos[3] = {0, 0, 0};

    for (;;) {
        // 从队列获取运动段
        if (xQueueReceive(motion_queue, &block, portMAX_DELAY) == pdTRUE) {
            // 添加到前瞻缓冲区
            lookahead_add_block(&la_buf, block.target,
                                block.feed_rate, block.motion_type);

            // 如果前瞻缓冲区有足够段，开始执行
            if (la_buf.count >= 4 || /* 最后一段 */ block.motion_type == 0xFF) {
                execute_next_block(&la_buf, current_pos);
            }
        }
    }
}

// 执行下一个运动段（生成步进序列）
void execute_next_block(LookaheadBuffer *buf, float *current_pos) {
    if (buf->count == 0) return;

    MotionBlock *block = &buf->blocks[buf->tail];

    // 计算各轴步数
    float steps_per_mm[3] = {160.0f, 160.0f, 400.0f};  // X/Y/Z步/mm
    int32_t target_steps[3];
    for (int i = 0; i < 3; i++) {
        target_steps[i] = (int32_t)(block->target[i] * steps_per_mm[i]);
    }

    // 初始化Bresenham 3D插补器
    Bresenham3D bres;
    bresenham3d_init(&bres,
                     (int32_t)(current_pos[0] * steps_per_mm[0]),
                     (int32_t)(current_pos[1] * steps_per_mm[1]),
                     (int32_t)(current_pos[2] * steps_per_mm[2]),
                     target_steps[0], target_steps[1], target_steps[2]);

    // 梯形速度规划
    float v_entry = block->entry_speed;
    float v_exit  = block->exit_speed;
    float v_max   = block->feed_rate;
    float length  = block->length;
    float a_max   = 500.0f;  // mm/min²

    // 生成步进序列
    int8_t sx, sy, sz;
    uint32_t step_count = 0;

    while (!bresenham3d_step(&bres, &sx, &sy, &sz)) {
        // 计算当前位置（步）
        float progress = (float)step_count / bres.steps;
        float current_speed = trapezoid_speed(v_entry, v_exit, v_max,
                                               a_max, length, progress);

        // 计算步进延时（μs）
        // 合成速度 → 主轴步进频率
        float step_freq = current_speed * steps_per_mm[bres.dominant] / 60.0f;
        uint32_t delay_us = (step_freq > 0) ?
                            (uint32_t)(1000000.0f / step_freq) : 10000;

        // 构建步进条目
        StepEntry entry;
        entry.step_mask = (sx ? 0x01 : 0) | (sy ? 0x02 : 0) | (sz ? 0x04 : 0);
        entry.dir_mask  = (sx > 0 ? 0x01 : 0) | (sy > 0 ? 0x02 : 0) | (sz > 0 ? 0x04 : 0);
        entry.delay_us  = delay_us;

        // 写入步进缓冲区（等待空间）
        uint16_t next_head = (step_buf_head + 1) % STEP_BUF_SIZE;
        while (next_head == step_buf_tail) {
            vTaskDelay(1);  // 等待步进输出消耗缓冲区
        }
        step_buf[step_buf_head] = entry;
        step_buf_head = next_head;

        step_count++;
    }

    // 更新当前位置
    current_pos[0] = block->target[0];
    current_pos[1] = block->target[1];
    current_pos[2] = block->target[2];

    buf->tail = (buf->tail + 1) % LOOKAHEAD_BUFFER_SIZE;
    buf->count--;
}

// 步进输出定时器中断（最高优先级）
// 定时器：TIM2，预分频使1计数=1μs
void TIM2_IRQHandler(void) {
    __HAL_TIM_CLEAR_IT(&htim2, TIM_IT_UPDATE);

    if (step_buf_head == step_buf_tail) {
        // 缓冲区空，停止定时器
        HAL_TIM_Base_Stop_IT(&htim2);
        return;
    }

    StepEntry *entry = &step_buf[step_buf_tail];
    step_buf_tail = (step_buf_tail + 1) % STEP_BUF_SIZE;

    // 设置方向（在步进脉冲前至少2μs）
    HAL_GPIO_WritePin(X_DIR_GPIO, X_DIR_PIN,
                      (entry->dir_mask & 0x01) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(Y_DIR_GPIO, Y_DIR_PIN,
                      (entry->dir_mask & 0x02) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(Z_DIR_GPIO, Z_DIR_PIN,
                      (entry->dir_mask & 0x04) ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // 输出步进脉冲（最小2μs高电平）
    if (entry->step_mask & 0x01) {
        HAL_GPIO_WritePin(X_STEP_GPIO, X_STEP_PIN, GPIO_PIN_SET);
        axis_pos[0] += (entry->dir_mask & 0x01) ? 1 : -1;
    }
    if (entry->step_mask & 0x02) {
        HAL_GPIO_WritePin(Y_STEP_GPIO, Y_STEP_PIN, GPIO_PIN_SET);
        axis_pos[1] += (entry->dir_mask & 0x02) ? 1 : -1;
    }
    if (entry->step_mask & 0x04) {
        HAL_GPIO_WritePin(Z_STEP_GPIO, Z_STEP_PIN, GPIO_PIN_SET);
        axis_pos[2] += (entry->dir_mask & 0x04) ? 1 : -1;
    }

    // 2μs后清除步进脉冲（通过软件延时或第二个定时器）
    // 简化：直接清除（实际应用需要精确2μs延时）
    HAL_GPIO_WritePin(X_STEP_GPIO, X_STEP_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(Y_STEP_GPIO, Y_STEP_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(Z_STEP_GPIO, Z_STEP_PIN, GPIO_PIN_RESET);

    // 设置下次中断时间
    __HAL_TIM_SET_AUTORELOAD(&htim2, entry->delay_us - 1);
    __HAL_TIM_SET_COUNTER(&htim2, 0);
}
```


## 深入原理

### GRBL架构深度分析

GRBL是最广泛使用的开源CNC固件，运行在Arduino Uno（ATmega328P）上，代码约10,000行C语言。理解GRBL架构对设计自己的CNC控制器有重要参考价值。

```
GRBL整体架构（v1.1）：

┌─────────────────────────────────────────────────────────────────┐
│                        GRBL架构图                                │
│                                                                   │
│  串口输入                                                         │
│  ┌──────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │Serial│───▶│ 串口接收缓冲  │───▶│      G代码解析器          │   │
│  │ RX   │    │ (128字节)    │    │  (gcode.c ~1500行)       │   │
│  └──────┘    └──────────────┘    └────────────┬─────────────┘   │
│                                               │                   │
│                                               ▼                   │
│                                  ┌──────────────────────────┐   │
│                                  │      运动规划器            │   │
│                                  │  (planner.c ~600行)      │   │
│                                  │  - 前瞻缓冲区(16段)       │   │
│                                  │  - 梯形速度规划           │   │
│                                  │  - 转角速度计算           │   │
│                                  └────────────┬─────────────┘   │
│                                               │                   │
│                                               ▼                   │
│                                  ┌──────────────────────────┐   │
│                                  │      步进执行器            │   │
│                                  │  (stepper.c ~800行)      │   │
│                                  │  - 段缓冲区(6段)          │   │
│                                  │  - Bresenham插补          │   │
│                                  │  - 定时器中断(TIMER1)     │   │
│                                  └────────────┬─────────────┘   │
│                                               │                   │
│                                               ▼                   │
│                                  ┌──────────────────────────┐   │
│                                  │      步进电机驱动          │   │
│                                  │  X/Y/Z STEP/DIR引脚       │   │
│                                  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**GRBL关键设计决策分析**：

**1. 双缓冲区设计**：
```
规划器缓冲区（planner buffer）：16个运动段
  - 存储完整的运动参数（位置、速度、加速度）
  - 用于前瞻速度规划
  - 由主循环填充

步进器缓冲区（stepper buffer）：6个段
  - 存储已规划好的段，等待执行
  - 由步进中断消耗
  - 解耦规划和执行的时序
```

**2. 梯形速度规划（GRBL实现）**：

```c
// GRBL梯形速度规划核心（简化版）
// 原始代码：planner.c中的planner_recalculate_trapezoid_block()

typedef struct {
    float nominal_speed;      // 编程速度（mm/min）
    float entry_speed;        // 入口速度（mm/min）
    float exit_speed;         // 出口速度（mm/min）
    float max_entry_speed;    // 最大入口速度（由转角决定）
    float acceleration;       // 加速度（mm/min²）
    float millimeters;        // 段长度（mm）

    // 梯形参数（步数）
    uint32_t accelerate_until;  // 加速阶段结束步数
    uint32_t decelerate_after;  // 减速阶段开始步数
    uint32_t total_steps;       // 总步数
    float    initial_rate;      // 初始步频（步/s）
    float    nominal_rate;      // 额定步频（步/s）
    float    final_rate;        // 最终步频（步/s）
    float    rate_delta;        // 每步的速率变化量
} PlannerBlock;

// 计算梯形参数
void calculate_trapezoid(PlannerBlock *block,
                          float entry_factor,  // entry_speed / nominal_speed
                          float exit_factor) { // exit_speed / nominal_speed
    float initial_rate = block->nominal_rate * entry_factor;
    float final_rate   = block->nominal_rate * exit_factor;

    // 加速距离（步）
    // v² = v0² + 2×a×d → d = (v² - v0²) / (2×a)
    int32_t accel_steps = (int32_t)ceil(
        (block->nominal_rate * block->nominal_rate -
         initial_rate * initial_rate) /
        (2.0f * block->rate_delta * block->nominal_rate));

    // 减速距离（步）
    int32_t decel_steps = (int32_t)ceil(
        (block->nominal_rate * block->nominal_rate -
         final_rate * final_rate) /
        (2.0f * block->rate_delta * block->nominal_rate));

    // 检查是否有匀速段
    int32_t plateau_steps = block->total_steps - accel_steps - decel_steps;

    if (plateau_steps < 0) {
        // 没有匀速段（三角形速度曲线）
        // 找到加减速交汇点
        accel_steps = (int32_t)ceil(
            (2.0f * block->acceleration * block->millimeters +
             final_rate * final_rate - initial_rate * initial_rate) /
            (4.0f * block->acceleration));
        if (accel_steps > (int32_t)block->total_steps)
            accel_steps = block->total_steps;
        decel_steps = block->total_steps - accel_steps;
        plateau_steps = 0;
    }

    block->accelerate_until = accel_steps;
    block->decelerate_after = accel_steps + plateau_steps;
    block->initial_rate = initial_rate;
    block->final_rate   = final_rate;
}
```

**3. GRBL步进中断（核心执行引擎）**：

```c
// GRBL步进中断简化版（原始：stepper.c中的TIMER1_COMPA_vect）
// 运行在ATmega328P的TIMER1比较匹配中断

// 步进器状态机
typedef enum {
    STEPPER_IDLE,
    STEPPER_ACCELERATING,
    STEPPER_CRUISING,
    STEPPER_DECELERATING
} StepperState;

static StepperState stepper_state = STEPPER_IDLE;
static uint32_t step_count = 0;
static float current_rate = 0;  // 当前步频（步/s）

// 中断服务程序（每次步进时调用）
ISR(TIMER1_COMPA_vect) {
    // 1. 输出步进脉冲
    STEP_PORT |= step_mask;  // 置高

    // 2. 更新Bresenham计数器，确定哪些轴步进
    // （GRBL使用位操作优化的Bresenham）

    // 3. 更新速度（梯形曲线）
    step_count++;
    if (step_count < current_block->accelerate_until) {
        // 加速阶段：每步增加速率
        current_rate += current_block->rate_delta;
        stepper_state = STEPPER_ACCELERATING;
    } else if (step_count < current_block->decelerate_after) {
        // 匀速阶段
        current_rate = current_block->nominal_rate;
        stepper_state = STEPPER_CRUISING;
    } else {
        // 减速阶段：每步减少速率
        current_rate -= current_block->rate_delta;
        if (current_rate < current_block->final_rate)
            current_rate = current_block->final_rate;
        stepper_state = STEPPER_DECELERATING;
    }

    // 4. 设置下次中断时间（OCR1A = F_CPU / (步频 × 预分频)）
    OCR1A = (uint16_t)(F_CPU / (current_rate * TIMER_PRESCALER));

    // 5. 清除步进脉冲（2μs后，通过TIMER0延时）
    STEP_PORT &= ~step_mask;  // 置低
}
```

### 实时运动规划：数学基础

**梯形速度曲线的完整数学推导**：

```
速度-时间图：
  v(mm/min)
  │
  │    v_max ─────────────────
  │         ╱                 ╲
  │        ╱                   ╲
  │  v_entry                   v_exit
  │       ╱                     ╲
  └──────────────────────────────── t(s)
       t_accel  t_cruise  t_decel

加速阶段：
  v(t) = v_entry + a×t
  d_accel = (v_max² - v_entry²) / (2×a)

匀速阶段：
  d_cruise = d_total - d_accel - d_decel

减速阶段：
  d_decel = (v_max² - v_exit²) / (2×a)

约束条件：
  d_accel + d_decel ≤ d_total（否则为三角形曲线）
  
三角形曲线（无匀速段）：
  v_peak = sqrt((2×a×d_total + v_entry² + v_exit²) / 2)
  如果 v_peak > v_max，则截断为梯形
```

```c
// 梯形速度曲线：给定进度(0~1)返回当前速度
// v_entry: 入口速度（mm/min）
// v_exit:  出口速度（mm/min）
// v_max:   最大速度（mm/min）
// a:       加速度（mm/s²）
// length:  总长度（mm）
// progress: 当前进度（0.0~1.0）
float trapezoid_speed(float v_entry, float v_exit, float v_max,
                      float a, float length, float progress) {
    // 转换单位：mm/min → mm/s
    float ve = v_entry / 60.0f;
    float vx = v_exit  / 60.0f;
    float vm = v_max   / 60.0f;

    float d = progress * length;  // 当前位移（mm）

    // 加速距离
    float d_accel = (vm*vm - ve*ve) / (2.0f * a);
    // 减速距离
    float d_decel = (vm*vm - vx*vx) / (2.0f * a);

    float v;
    if (d_accel + d_decel > length) {
        // 三角形曲线
        float v_peak = sqrtf((2.0f * a * length + ve*ve + vx*vx) / 2.0f);
        float d_peak = (v_peak*v_peak - ve*ve) / (2.0f * a);
        if (d <= d_peak) {
            v = sqrtf(ve*ve + 2.0f * a * d);
        } else {
            v = sqrtf(v_peak*v_peak - 2.0f * a * (d - d_peak));
        }
    } else {
        // 梯形曲线
        if (d <= d_accel) {
            v = sqrtf(ve*ve + 2.0f * a * d);
        } else if (d <= length - d_decel) {
            v = vm;
        } else {
            float d_from_end = length - d;
            v = sqrtf(vx*vx + 2.0f * a * d_from_end);
        }
    }

    return v * 60.0f;  // 转回mm/min
}
```

### 电子齿轮进阶：非线性凸轮仿形

标准电子齿轮实现线性传动比，但工业应用中常需要非线性凸轮仿形（Cam Profile）：

```c
// 凸轮仿形电子齿轮
// 主轴位置 → 从轴位置的非线性映射
// 使用查找表 + 线性插值

#define CAM_TABLE_SIZE  360  // 每度一个点

typedef struct {
    float    cam_table[CAM_TABLE_SIZE];  // 凸轮曲线（从轴位置，mm）
    float    master_range;               // 主轴一圈的步数
    int32_t  master_pos;                 // 主轴当前位置（步）
    float    slave_pos_mm;               // 从轴当前位置（mm）
    float    steps_per_mm;               // 从轴步/mm
} CamGear;

// 初始化凸轮（示例：正弦凸轮）
void cam_init_sine(CamGear *cam, float amplitude, float steps_per_rev) {
    cam->master_range = steps_per_rev;
    cam->steps_per_mm = 160.0f;

    for (int i = 0; i < CAM_TABLE_SIZE; i++) {
        float angle = 2.0f * 3.14159f * i / CAM_TABLE_SIZE;
        cam->cam_table[i] = amplitude * sinf(angle);
    }
    cam->master_pos = 0;
    cam->slave_pos_mm = 0;
}

// 主轴步进时更新从轴位置
// 返回：从轴需要步进的步数
int32_t cam_update(CamGear *cam, int32_t master_delta) {
    cam->master_pos += master_delta;

    // 计算主轴在凸轮表中的位置（0~360度）
    float master_angle = fmodf(
        (float)cam->master_pos / cam->master_range * CAM_TABLE_SIZE,
        CAM_TABLE_SIZE);
    if (master_angle < 0) master_angle += CAM_TABLE_SIZE;

    // 线性插值
    int idx0 = (int)master_angle % CAM_TABLE_SIZE;
    int idx1 = (idx0 + 1) % CAM_TABLE_SIZE;
    float frac = master_angle - (int)master_angle;
    float new_slave_mm = cam->cam_table[idx0] * (1.0f - frac) +
                         cam->cam_table[idx1] * frac;

    // 计算从轴步进量
    float delta_mm = new_slave_mm - cam->slave_pos_mm;
    int32_t delta_steps = (int32_t)(delta_mm * cam->steps_per_mm);

    cam->slave_pos_mm = new_slave_mm;
    return delta_steps;
}
```


## 完整项目实战：2轴XY绘图仪

### 项目概述

本项目实现一个完整的2轴XY绘图仪，支持G代码输入，能够绘制直线、圆弧和复杂图形。

```
┌─────────────────────────────────────────────────────────────────┐
│                    XY绘图仪系统架构                               │
│                                                                   │
│  ┌──────────┐    USB/串口    ┌──────────────────────────────┐   │
│  │  PC端    │──────────────▶│      STM32F407控制器          │   │
│  │ G代码    │               │                              │   │
│  │ 发送器   │               │  ┌──────────┐ ┌──────────┐  │   │
│  └──────────┘               │  │ X轴驱动  │ │ Y轴驱动  │  │   │
│                              │  │ DRV8825  │ │ DRV8825  │  │   │
│                              │  └────┬─────┘ └────┬─────┘  │   │
│                              └───────┼─────────────┼────────┘   │
│                                      │             │             │
│                              ┌───────▼─────────────▼────────┐   │
│                              │  X轴步进电机    Y轴步进电机    │   │
│                              │  NEMA17 42mm   NEMA17 42mm   │   │
│                              │  200步/转      200步/转       │   │
│                              └──────────────────────────────┘   │
│                                                                   │
│  机械结构：CoreXY（H-Bot变体）                                    │
│  行程：200mm × 200mm                                              │
│  分辨率：0.0125mm（16细分，2mm皮带齿距，20齿同步轮）              │
│  最大速度：3000mm/min                                             │
│  最大加速度：500mm/s²                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 物料清单（BOM）

| 序号 | 名称 | 规格 | 数量 | 参考价格 |
|------|------|------|------|---------|
| 1 | 主控板 | STM32F407VET6最小系统板 | 1 | ¥35 |
| 2 | 步进电机驱动 | DRV8825模块（16细分） | 2 | ¥8×2 |
| 3 | 步进电机 | NEMA17 42×40mm，1.8°，1.5A | 2 | ¥25×2 |
| 4 | 同步带 | GT2，2mm齿距，6mm宽，1m | 2 | ¥5×2 |
| 5 | 同步轮 | GT2，20齿，5mm孔 | 4 | ¥3×4 |
| 6 | 光轴 | 8mm直径，300mm长 | 4 | ¥8×4 |
| 7 | 直线轴承 | LM8UU | 8 | ¥3×8 |
| 8 | 限位开关 | 机械式微动开关 | 2 | ¥1×2 |
| 9 | 舵机 | SG90（笔抬起/放下） | 1 | ¥8 |
| 10 | 电源 | 12V/3A开关电源 | 1 | ¥20 |
| 11 | 铝型材 | 2020铝型材，300mm | 4 | ¥5×4 |
| **合计** | | | | **约¥220** |

### CoreXY运动学

CoreXY是一种特殊的XY运动机构，两个电机都固定在机架上，通过交叉皮带驱动打印头：

```
CoreXY运动学：

  电机A（左上）    电机B（右上）
      ┌──────────────────────┐
      │  ╲                ╱  │
      │   ╲              ╱   │
      │    ╲            ╱    │
      │     ●──────────●     │  ← 打印头
      │    ╱            ╲    │
      │   ╱              ╲   │
      └──────────────────────┘

运动关系：
  X方向移动：A和B同向旋转（A+, B+）
  Y方向移动：A和B反向旋转（A+, B-）
  
  A电机步数 = X步数 + Y步数
  B电机步数 = X步数 - Y步数
  
  反解：
  X步数 = (A步数 + B步数) / 2
  Y步数 = (A步数 - B步数) / 2
```

```c
// CoreXY运动学变换
// 文件：corexy.c
// 将XY坐标步数转换为A/B电机步数

typedef struct {
    int32_t a_steps;  // A电机步数
    int32_t b_steps;  // B电机步数
} CoreXYSteps;

// XY步数 → AB电机步数
CoreXYSteps corexy_forward(int32_t x_steps, int32_t y_steps) {
    CoreXYSteps result;
    result.a_steps = x_steps + y_steps;
    result.b_steps = x_steps - y_steps;
    return result;
}

// AB电机步数 → XY步数（用于位置反馈）
void corexy_inverse(int32_t a_steps, int32_t b_steps,
                    int32_t *x_steps, int32_t *y_steps) {
    *x_steps = (a_steps + b_steps) / 2;
    *y_steps = (a_steps - b_steps) / 2;
}

// CoreXY Bresenham插补（同时驱动A/B两个电机）
void corexy_move_to(int32_t x0, int32_t y0,
                    int32_t x1, int32_t y1,
                    float feed_rate_mm_min) {
    // 计算XY位移
    int32_t dx = x1 - x0;
    int32_t dy = y1 - y0;

    // 转换为AB电机步数
    int32_t da = dx + dy;
    int32_t db = dx - dy;

    // 对AB电机使用Bresenham插补
    Bresenham2D bres;
    bresenham2d_init(&bres, 0, 0, da, db);

    // 计算步进延时（基于进给速度）
    float length_mm = sqrtf((float)(dx*dx + dy*dy)) / STEPS_PER_MM;
    float total_steps = bres.steps;
    float step_freq = (feed_rate_mm_min / 60.0f) * STEPS_PER_MM;
    uint32_t delay_us = (uint32_t)(1000000.0f / step_freq);

    int8_t sa, sb;
    while (!bresenham2d_step(&bres, &sa, &sb)) {
        // 输出A电机步进
        if (sa) {
            gpio_write(A_DIR_PIN, sa > 0 ? 1 : 0);
            gpio_pulse(A_STEP_PIN, 2);
        }
        // 输出B电机步进
        if (sb) {
            gpio_write(B_DIR_PIN, sb > 0 ? 1 : 0);
            gpio_pulse(B_STEP_PIN, 2);
        }
        delay_us_func(delay_us);
    }
}
```

### G代码解析器实现

```c
// 轻量级G代码解析器
// 文件：gcode_parser.c
// 支持：G00, G01, G02, G03, G04, G28, G90, G91, M03, M05, M30

#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>

typedef struct {
    float x, y, z;      // 坐标（mm）
    float i, j, k;      // 圆弧圆心偏移（mm）
    float f;            // 进给速度（mm/min）
    float r;            // 圆弧半径（mm）
    float p;            // 暂停时间（ms）
    int   g_code;       // G功能码（0, 1, 2, 3...）
    int   m_code;       // M功能码（-1=无）
    uint8_t has_x, has_y, has_z;
    uint8_t has_i, has_j, has_r;
    uint8_t absolute;   // 1=绝对坐标(G90), 0=增量坐标(G91)
} GCodeBlock;

// 解析一行G代码
// 返回：0=成功，-1=错误，1=空行/注释
int gcode_parse_line(const char *line, GCodeBlock *block) {
    memset(block, 0, sizeof(GCodeBlock));
    block->g_code = -1;
    block->m_code = -1;
    block->f = -1;  // -1表示未指定（使用上次速度）

    const char *p = line;

    // 跳过空白
    while (*p && isspace(*p)) p++;

    // 空行或注释
    if (*p == '\0' || *p == ';' || *p == '(') return 1;

    // 跳过行号（N字）
    if (*p == 'N' || *p == 'n') {
        p++;
        while (*p && isdigit(*p)) p++;
        while (*p && isspace(*p)) p++;
    }

    // 解析各字
    while (*p) {
        char letter = toupper(*p);
        p++;

        // 跳过空白
        while (*p && isspace(*p)) p++;

        // 解析数值
        char *end;
        float value = strtof(p, &end);
        if (end == p) {
            // 无数值，跳过
            if (*p) p++;
            continue;
        }
        p = end;

        switch (letter) {
            case 'G': block->g_code = (int)value; break;
            case 'M': block->m_code = (int)value; break;
            case 'X': block->x = value; block->has_x = 1; break;
            case 'Y': block->y = value; block->has_y = 1; break;
            case 'Z': block->z = value; block->has_z = 1; break;
            case 'I': block->i = value; block->has_i = 1; break;
            case 'J': block->j = value; block->has_j = 1; break;
            case 'R': block->r = value; block->has_r = 1; break;
            case 'F': block->f = value; break;
            case 'P': block->p = value; break;
        }

        while (*p && isspace(*p)) p++;
    }

    return 0;
}

// G代码执行器
typedef struct {
    float    pos[3];         // 当前位置（mm）
    float    feed_rate;      // 当前进给速度（mm/min）
    uint8_t  absolute;       // 坐标模式
    uint8_t  pen_down;       // 笔状态（1=落笔，0=抬笔）
    uint32_t line_count;     // 已执行行数
} GCodeState;

int gcode_execute(GCodeState *state, GCodeBlock *block) {
    // 更新进给速度
    if (block->f > 0) state->feed_rate = block->f;

    // 计算目标位置
    float target[3];
    if (state->absolute) {
        target[0] = block->has_x ? block->x : state->pos[0];
        target[1] = block->has_y ? block->y : state->pos[1];
        target[2] = block->has_z ? block->z : state->pos[2];
    } else {
        // 增量坐标
        target[0] = state->pos[0] + (block->has_x ? block->x : 0);
        target[1] = state->pos[1] + (block->has_y ? block->y : 0);
        target[2] = state->pos[2] + (block->has_z ? block->z : 0);
    }

    switch (block->g_code) {
        case 0:  // G00：快速定位
            motion_move_linear(state->pos, target, RAPID_FEED_RATE);
            break;

        case 1:  // G01：直线插补
            motion_move_linear(state->pos, target, state->feed_rate);
            break;

        case 2:  // G02：顺时针圆弧
        case 3: {  // G03：逆时针圆弧
            float center[2];
            if (block->has_r) {
                // 半径格式：计算圆心
                float dx = target[0] - state->pos[0];
                float dy = target[1] - state->pos[1];
                float d = sqrtf(dx*dx + dy*dy);
                float h = sqrtf(block->r*block->r - d*d/4.0f);
                // 选择正确的圆心（正R=小弧，负R=大弧）
                float sign = (block->g_code == 2) ? 1.0f : -1.0f;
                if (block->r < 0) sign = -sign;
                center[0] = state->pos[0] + dx/2.0f - sign * h * dy/d;
                center[1] = state->pos[1] + dy/2.0f + sign * h * dx/d;
            } else {
                // IJ格式：圆心相对起点的偏移
                center[0] = state->pos[0] + block->i;
                center[1] = state->pos[1] + block->j;
            }
            motion_move_arc(state->pos, target, center,
                            block->g_code == 2, state->feed_rate);
            break;
        }

        case 4:  // G04：暂停
            HAL_Delay((uint32_t)block->p);
            break;

        case 28:  // G28：回原点
            motion_home();
            target[0] = target[1] = target[2] = 0;
            break;

        case 90:  // G90：绝对坐标
            state->absolute = 1;
            break;

        case 91:  // G91：增量坐标
            state->absolute = 0;
            break;

        case -1:  // 无G代码，处理M代码
            break;
    }

    // 处理M代码
    switch (block->m_code) {
        case 3:   // M03：笔落下
            servo_set_angle(PEN_SERVO, PEN_DOWN_ANGLE);
            state->pen_down = 1;
            HAL_Delay(200);  // 等待舵机到位
            break;
        case 5:   // M05：笔抬起
            servo_set_angle(PEN_SERVO, PEN_UP_ANGLE);
            state->pen_down = 0;
            HAL_Delay(200);
            break;
        case 30:  // M30：程序结束
            return -1;  // 通知调用者程序结束
    }

    // 更新当前位置
    state->pos[0] = target[0];
    state->pos[1] = target[1];
    state->pos[2] = target[2];
    state->line_count++;

    return 0;
}
```

### 回零（Homing）程序

```c
// 回零程序：使用限位开关确定机械原点
// 文件：homing.c

#define HOMING_FEED_RATE    600.0f   // 回零速度（mm/min）
#define HOMING_PULLOFF      5.0f     // 触发后回退距离（mm）
#define HOMING_SEEK_RATE    1200.0f  // 快速搜索速度（mm/min）

// 单轴回零
// axis: 0=X, 1=Y
// direction: 1=正向, -1=负向
void home_axis(uint8_t axis, int8_t direction) {
    // 第一阶段：快速移动直到触发限位开关
    while (!limit_switch_triggered(axis)) {
        step_axis(axis, direction, HOMING_SEEK_RATE);
    }

    // 第二阶段：回退5mm
    float pulloff_steps = HOMING_PULLOFF * STEPS_PER_MM;
    for (int32_t i = 0; i < (int32_t)pulloff_steps; i++) {
        step_axis(axis, -direction, HOMING_FEED_RATE);
    }

    // 第三阶段：慢速精确触发
    while (!limit_switch_triggered(axis)) {
        step_axis(axis, direction, HOMING_FEED_RATE);
    }

    // 设置当前位置为0
    axis_pos[axis] = 0;
}

// 完整回零序列
void motion_home(void) {
    // 先抬笔
    servo_set_angle(PEN_SERVO, PEN_UP_ANGLE);
    HAL_Delay(300);

    // Z轴（如果有）先回零
    // home_axis(2, -1);

    // X轴回零
    home_axis(0, -1);

    // Y轴回零
    home_axis(1, -1);

    // 移动到工作原点（避开限位开关）
    float work_origin[3] = {5.0f, 5.0f, 0};
    motion_move_linear((float[]){0,0,0}, work_origin, HOMING_FEED_RATE);
}
```

### 主程序

```c
// 主程序：XY绘图仪
// 文件：main.c
// 芯片：STM32F407VET6，HAL v1.27，FreeRTOS v10.4

#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 系统参数
#define STEPS_PER_MM      160.0f   // 步/mm（200步/转×16细分÷20齿÷2mm齿距）
#define MAX_FEED_RATE     3000.0f  // mm/min
#define RAPID_FEED_RATE   3000.0f  // mm/min
#define MAX_ACCEL         500.0f   // mm/s²
#define PEN_UP_ANGLE      90       // 舵机角度（抬笔）
#define PEN_DOWN_ANGLE    45       // 舵机角度（落笔）

// 全局状态
GCodeState gcode_state = {
    .pos = {0, 0, 0},
    .feed_rate = 500.0f,
    .absolute = 1,
    .pen_down = 0,
    .line_count = 0
};

// G代码处理任务
void gcode_task(void *pvParameters) {
    char line[128];
    GCodeBlock block;

    // 系统初始化
    stepper_init();
    servo_init();
    limit_switch_init();

    // 回零
    motion_home();

    // 发送就绪信号
    uart_send_string("ok\r\n");

    for (;;) {
        // 读取一行G代码（阻塞）
        if (uart_readline(line, sizeof(line), portMAX_DELAY) == 0) {
            // 解析
            int ret = gcode_parse_line(line, &block);
            if (ret == 0) {
                // 执行
                ret = gcode_execute(&gcode_state, &block);
                if (ret == -1) {
                    // M30：程序结束
                    uart_send_string("Program complete\r\n");
                } else {
                    uart_send_string("ok\r\n");
                }
            } else if (ret == 1) {
                // 空行/注释
                uart_send_string("ok\r\n");
            } else {
                uart_send_string("error\r\n");
            }
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();  // 168MHz

    // 外设初始化
    MX_GPIO_Init();
    MX_USART1_UART_Init();  // 115200bps，连接PC
    MX_TIM2_Init();         // 步进定时器
    MX_TIM3_Init();         // 舵机PWM

    // 创建任务
    xTaskCreate(gcode_task, "GCode", 1024, NULL, 2, NULL);

    // 启动调度器
    vTaskStartScheduler();

    while (1) {}
}
```

### 测试程序：绘制测试图案

```gcode
; 测试程序：绘制五角星
; 文件：star.gcode
G21 G90          ; 公制，绝对坐标
G28              ; 回零
M05              ; 确保笔抬起
G00 X100 Y50     ; 移到起点

; 绘制五角星（外接圆半径40mm，中心100,100）
; 五角星顶点角度：90°, 162°, 234°, 306°, 18°
M03              ; 落笔
G01 X100.0 Y140.0 F800   ; 顶点1（90°）
G01 X84.7 Y95.1          ; 顶点2（162°）
G01 X138.0 Y69.1         ; 顶点3（234°）
G01 X62.0 Y69.1          ; 顶点4（306°）
G01 X115.3 Y95.1         ; 顶点5（18°）
G01 X100.0 Y140.0        ; 回顶点1
M05              ; 抬笔

; 绘制圆（测试圆弧插补）
G00 X140 Y100    ; 移到圆弧起点
M03              ; 落笔
G02 X140 Y100 I-40 J0 F600  ; 完整圆（顺时针）
M05              ; 抬笔

G00 X0 Y0        ; 回原点
M30              ; 程序结束
```


## 性能调优

### 插补精度优化

**提高圆弧精度**：

```c
// 自适应弦误差：根据速度动态调整步进角度
// 高速时允许较大弦误差，低速时要求更精确
float adaptive_chord_error(float feed_rate_mm_min) {
    // 速度越高，允许的弦误差越大（但不超过0.01mm）
    float base_error = 0.001f;  // 基础弦误差1μm
    float speed_factor = feed_rate_mm_min / 1000.0f;  // 归一化速度
    float chord_error = base_error * (1.0f + speed_factor * 9.0f);
    if (chord_error > 0.01f) chord_error = 0.01f;  // 最大10μm
    return chord_error;
}
```

**步进脉冲时序优化**：

```
步进驱动器时序要求（DRV8825）：
  
  DIR ─────────────────────────────────────
       ↑ 方向建立时间
       650ns最小
  
  STEP ─────┐    ┌────────────────────────
            │    │
            └────┘
            ↑    ↑
          1.9μs  1.9μs
          高电平  低电平最小宽度
  
  两步之间最小间隔：3.8μs（最大步频约263kHz）
  
  实际建议：
  - 方向建立时间：≥2μs
  - 步进脉冲宽度：≥5μs（留余量）
  - 最大步频：100kHz（安全值）
```

### 速度规划调优参数

```c
// 运动控制参数配置
typedef struct {
    float max_feed_rate[3];    // 各轴最大速度（mm/min）
    float max_acceleration[3]; // 各轴最大加速度（mm/s²）
    float junction_deviation;  // 转角偏差（mm），影响转角速度
    float arc_tolerance;       // 圆弧弦误差（mm）
    float homing_feed_rate;    // 回零速度（mm/min）
    float homing_seek_rate;    // 回零搜索速度（mm/min）
    float homing_pulloff;      // 回零回退距离（mm）
} MotionConfig;

// 推荐配置（XY绘图仪）
MotionConfig plotter_config = {
    .max_feed_rate     = {3000.0f, 3000.0f, 500.0f},
    .max_acceleration  = {500.0f,  500.0f,  100.0f},
    .junction_deviation = 0.05f,   // 较小值=更平滑但更慢
    .arc_tolerance      = 0.002f,  // 2μm弦误差
    .homing_feed_rate   = 600.0f,
    .homing_seek_rate   = 1200.0f,
    .homing_pulloff     = 5.0f
};
```

## 常见问题与调试

### 问题1：圆弧变椭圆

**现象**：绘制圆形时，实际轨迹是椭圆，X/Y方向尺寸不一致。

**原因分析**：
```
X轴分辨率 ≠ Y轴分辨率

例如：
  X轴：200步/转 × 16细分 ÷ 20齿 ÷ 2mm = 80步/mm
  Y轴：200步/转 × 16细分 ÷ 16齿 ÷ 2mm = 100步/mm（同步轮齿数不同）
  
  编程100mm圆：
  X轴实际走：100mm × 80步/mm = 8000步 → 实际100mm ✓
  Y轴实际走：100mm × 100步/mm = 10000步 → 实际100mm ✓
  
  但如果steps_per_mm配置错误：
  X配置为80，Y配置为80（错误）
  Y轴实际走：100mm × 80步/mm = 8000步 → 实际80mm ✗
  → 圆变成椭圆（X=100mm, Y=80mm）
```

**解决方法**：
```c
// 精确测量各轴分辨率
// 方法：命令移动100mm，用游标卡尺测量实际位移
// 实际分辨率 = 命令步数 / 实际位移(mm)

// 校准程序
void calibrate_axis(uint8_t axis) {
    float test_distance = 100.0f;  // 命令移动100mm
    int32_t test_steps = (int32_t)(test_distance * STEPS_PER_MM_NOMINAL);

    printf("移动%d步，请测量实际位移后输入(mm): ", test_steps);
    float actual_mm;
    scanf("%f", &actual_mm);

    float actual_steps_per_mm = test_steps / actual_mm;
    printf("轴%d实际分辨率: %.4f 步/mm\n", axis, actual_steps_per_mm);
    // 更新配置并保存到Flash
}
```

### 问题2：圆弧弦误差过大

**现象**：圆弧看起来是多边形，不够圆滑。

**原因**：弦误差设置过大，或圆弧半径很小时步进角度过大。

```
弦误差与步进角度的关系：
  δ = R × (1 - cos(θ/2))
  
  R=10mm, θ=10°: δ = 10 × (1 - cos5°) = 10 × 0.0038 = 0.038mm
  R=10mm, θ=5°:  δ = 10 × (1 - cos2.5°) = 10 × 0.00095 = 0.0095mm
  R=10mm, θ=2°:  δ = 10 × (1 - cos1°) = 10 × 0.000152 = 0.00152mm
  
  对于R=10mm，要达到0.002mm弦误差：
  θ = 2×arccos(1 - 0.002/10) = 2×arccos(0.9998) ≈ 1.15°
  → 每圆需要360/1.15 ≈ 313步
```

**解决方法**：减小`ARC_CHORD_ERROR_MAX`参数（代价是计算量增加）。

### 问题3：速度不连续（转角处抖动）

**现象**：在路径转角处，机器明显减速甚至停顿，然后再加速，运动不流畅。

**原因**：前瞻缓冲区未启用，或`junction_deviation`设置过小。

```
转角速度与junction_deviation的关系：
  junction_deviation = 0.01mm → 转角速度很低（过于保守）
  junction_deviation = 0.1mm  → 转角速度较高（更流畅）
  junction_deviation = 0.5mm  → 转角速度很高（可能过冲）
  
  90°转角时的过渡速度（a=500mm/s²）：
  jd=0.01: v = sqrt(500 × 0.01 × sin45°/(1-sin45°)) × 60 ≈ 130mm/min
  jd=0.05: v = sqrt(500 × 0.05 × sin45°/(1-sin45°)) × 60 ≈ 290mm/min
  jd=0.10: v = sqrt(500 × 0.10 × sin45°/(1-sin45°)) × 60 ≈ 410mm/min
```

**解决方法**：
1. 增大`junction_deviation`（从0.05增到0.1）
2. 确保前瞻缓冲区有足够段数（≥8段）
3. 检查速度规划是否正确实现反向传播

### 问题4：轴失步（Axis Desync）

**现象**：长时间运行后，实际位置与命令位置不符，图形出现偏移或变形。

**原因分析**：

```
失步原因：
1. 加速度过大：电机转矩不足以跟上加速要求
   → 减小max_acceleration

2. 速度过高：超过电机最大转速
   → 减小max_feed_rate

3. 电流不足：DRV8825电流设置过低
   → 调整VREF电压（VREF = I_max × 0.5）
   → NEMA17 1.5A电机：VREF = 1.5 × 0.5 = 0.75V

4. 步进脉冲丢失：中断优先级冲突或CPU过载
   → 提高步进中断优先级
   → 减少中断中的计算量

5. 机械问题：皮带打滑、同步轮松动
   → 检查皮带张力（按压皮带应有弹性）
   → 检查同步轮紧固螺丝
```

**失步检测（使用编码器）**：
```c
// 如果有编码器，可以检测失步
void check_position_error(void) {
    int32_t encoder_pos = read_encoder();
    int32_t commanded_pos = axis_pos[0];  // 命令位置（步）

    int32_t error = abs(encoder_pos - commanded_pos);
    if (error > MAX_POSITION_ERROR) {
        // 失步报警
        emergency_stop();
        printf("ERROR: Position error %d steps on X axis\n", error);
    }
}
```

### 问题5：圆弧起终点不闭合

**现象**：绘制完整圆后，起点和终点之间有明显缝隙。

**原因**：圆弧插补的累积误差，或起终点坐标计算精度不足。

```c
// 解决方案：强制最后一步到达精确终点
void arc_force_endpoint(ArcInterp *arc, float end[2],
                        float steps_per_mm, int32_t *final_sx, int32_t *final_sy) {
    // 计算当前位置与终点的差值
    float dx = end[0] - arc->last_x;
    float dy = end[1] - arc->last_y;

    // 如果差值超过半步，输出补偿步进
    *final_sx = (int32_t)(dx * steps_per_mm + 0.5f);
    *final_sy = (int32_t)(dy * steps_per_mm + 0.5f);
}
```

### 问题6：G代码解析错误

**常见G代码格式问题**：

```
错误示例及修复：

1. 缺少空格（某些解析器要求）：
   错误：G01X100Y50F500
   正确：G01 X100 Y50 F500

2. 圆弧IJ格式与R格式混用：
   错误：G02 X50 Y50 I25 J0 R25  （不能同时指定IJ和R）
   正确：G02 X50 Y50 I25 J0      （使用IJ格式）
   或：  G02 X50 Y50 R25          （使用R格式）

3. 增量坐标下的圆弧：
   G91模式下，X/Y是相对位移，但I/J始终是相对圆心偏移
   G91 G02 X10 Y0 I5 J0  → 终点在当前位置+10mm处，圆心在当前位置+5mm处

4. 完整圆（起终点相同）：
   G02 X0 Y0 I25 J0  → 起终点相同，R格式无法表示完整圆，必须用IJ格式
```

### 调试工具推荐

| 工具 | 用途 | 推荐 |
|------|------|------|
| Universal Gcode Sender | PC端G代码发送，实时位置显示 | 免费 |
| Candle (GRBL Controller) | GRBL专用控制软件，支持可视化 | 免费 |
| Inkscape + G代码插件 | 将SVG图形转换为G代码 | 免费 |
| OpenSCAM | G代码仿真，预览刀具路径 | 免费 |
| 逻辑分析仪 | 分析STEP/DIR信号时序 | ¥50起 |

## 测试与验证

### 插补精度测试

```python
# 验证Bresenham插补精度的Python脚本
# 文件：test_bresenham.py

import math

def bresenham_2d(x0, y0, x1, y1):
    """生成Bresenham直线的所有点"""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    dir_x = 1 if x1 >= x0 else -1
    dir_y = 1 if y1 >= y0 else -1

    if dx >= dy:
        err = dx - dy
        x, y = x0, y0
        for _ in range(dx + 1):
            points.append((x, y))
            e2 = 2 * err
            if e2 >= -dy:
                err -= dy
                x += dir_x
            if e2 <= dx:
                err += dx
                y += dir_y
    else:
        err = dy - dx
        x, y = x0, y0
        for _ in range(dy + 1):
            points.append((x, y))
            e2 = 2 * err
            if e2 >= -dx:
                err -= dx
                y += dir_y
            if e2 <= dy:
                err += dy
                x += dir_x

    return points

def max_deviation(points, x0, y0, x1, y1):
    """计算Bresenham直线与理想直线的最大偏差"""
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return 0

    max_dev = 0
    for px, py in points:
        # 点到直线的距离
        dist = abs(dy * px - dx * py + x1*y0 - y1*x0) / length
        if dist > max_dev:
            max_dev = dist

    return max_dev

# 测试多种斜率
test_cases = [
    (0, 0, 100, 0),    # 水平线
    (0, 0, 0, 100),    # 垂直线
    (0, 0, 100, 100),  # 45度
    (0, 0, 100, 37),   # 任意斜率
    (0, 0, 7, 3),      # 文中推导示例
]

print("Bresenham插补精度测试")
print("-" * 50)
for x0, y0, x1, y1 in test_cases:
    points = bresenham_2d(x0, y0, x1, y1)
    dev = max_deviation(points, x0, y0, x1, y1)
    print(f"({x0},{y0})→({x1},{y1}): {len(points)}点, 最大偏差={dev:.4f}步")

# 验证：最大偏差应 < 1步（Bresenham保证）
print("\n所有偏差应 < 1.0步 ✓")
```

### 圆弧弦误差验证

```python
# 验证圆弧插补弦误差
import math

def arc_chord_error(radius, angle_step_deg):
    """计算给定步进角度的弦误差"""
    theta = math.radians(angle_step_deg)
    return radius * (1 - math.cos(theta / 2))

def required_angle_step(radius, max_error):
    """给定最大弦误差，计算所需步进角度"""
    return 2 * math.degrees(math.acos(1 - max_error / radius))

print("圆弧弦误差分析")
print("-" * 60)
print(f"{'半径(mm)':<12} {'步进角(°)':<12} {'弦误差(mm)':<15} {'每圆步数':<10}")
print("-" * 60)

for radius in [5, 10, 20, 50, 100]:
    max_error = 0.002  # 2μm
    angle_step = required_angle_step(radius, max_error)
    steps_per_circle = int(360 / angle_step) + 1
    actual_error = arc_chord_error(radius, angle_step)
    print(f"{radius:<12} {angle_step:<12.3f} {actual_error:<15.6f} {steps_per_circle:<10}")
```

## 延伸阅读

- [运动控制算法](02-motion-control-algorithms.html) — 梯形/S曲线加减速，单轴运动基础
- [智能小车控制](01-smart-car-control.html) — 差速驱动的多轴协调应用
- [智能云台项目](04-smart-gimbal-project.html) — 多轴PID协调控制
- [机械臂项目](05-robot-arm-project.html) — 多轴运动学与轨迹规划
- [步进电机控制](../beginner/02-stepper-motor-control.html) — 步进电机基础驱动

## 参考资料

1. Grbl开源CNC固件 v1.1 — [github.com/gnea/grbl](https://github.com/gnea/grbl)
2. Marlin 3D打印固件 — [marlinfw.org](https://marlinfw.org/)
3. Bresenham, J.E. — "Algorithm for computer control of a digital plotter", IBM Systems Journal, 1965
4. RS274/NGC G代码标准 — NIST Technical Note 1349
5. 《数控技术》第3版 — 廖效果，华中科技大学出版社
6. 《运动控制系统》— 阮毅，陈伯时，机械工业出版社
7. DRV8825步进电机驱动器数据手册 — Texas Instruments SLVSA73E
8. STM32F4参考手册 — RM0090，ST Microelectronics
9. CoreXY运动学分析 — [corexy.com](http://corexy.com/)
10. 《计算机数控系统》— 王永章，机械工业出版社

