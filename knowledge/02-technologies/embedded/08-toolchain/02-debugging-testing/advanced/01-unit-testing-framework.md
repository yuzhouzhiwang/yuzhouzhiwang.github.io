---
title: "嵌入式系统单元测试框架搭建完全指南"
description: "深入讲解嵌入式系统中单元测试框架的选择、搭建、测试用例编写、Mock技术、覆盖率分析和CI集成，帮助开发者建立完整的测试体系"
slug: "unit-testing-framework"

# 分类信息
domain: "工具链"
module: "调试与测试"
content_type: "tutorial"
skill_level: "advanced"

# 标签和关联
tags:
  - 单元测试
  - 测试框架
  - 代码质量
  - Mock技术
  - 覆盖率分析
  - CI集成
prerequisites:
  - "熟悉C/C++编程"
  - "了解软件测试基础"
  - "掌握编译和构建流程"
  - "了解CI/CD概念"
related_contents:
  - "static-analysis"
  - "cicd-practice"
  - "memory-leak-detection"

# 学习信息
estimated_time: 100
difficulty_score: 5

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
  - 单元测试框架
  - 嵌入式测试
  - Unity测试框架
  - CppUTest
  - Mock技术
  - 测试覆盖率
cover_image: ""
---

# 嵌入式系统单元测试框架搭建完全指南

## 学习目标

完成本教程后，你将能够:

- [ ] 理解单元测试的重要性和基本原则
- [ ] 选择适合嵌入式项目的测试框架
- [ ] 搭建Unity/CppUTest测试环境
- [ ] 编写高质量的测试用例
- [ ] 掌握Mock和Stub技术
- [ ] 分析和提高代码覆盖率
- [ ] 将测试集成到CI/CD流程
- [ ] 建立完整的测试体系

## 前置要求

在开始本教程之前，你需要:

**知识要求**:
- 精通C/C++语言
- 理解软件测试概念
- 了解编译链接过程
- 熟悉Makefile或CMake
- 了解版本控制（Git）

**技能要求**:
- 能够编写模块化代码
- 会使用命令行工具
- 能够阅读和理解测试报告
- 了解持续集成概念

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| 开发板 | 1 | STM32或其他ARM开发板（可选） | - |
| 调试器 | 1 | 用于在目标硬件上运行测试（可选） | - |

### 软件准备

- **编译器**: GCC或ARM GCC工具链
- **测试框架**: Unity、CppUTest或Google Test
- **构建工具**: Make、CMake或SCons
- **覆盖率工具**: gcov、lcov
- **CI工具**: Jenkins、GitLab CI或GitHub Actions
- **IDE**: VS Code、CLion或Eclipse（可选）

### 系统要求

- **操作系统**: Linux、macOS或Windows（WSL）
- **内存**: 至少4GB RAM
- **磁盘空间**: 至少2GB可用空间


## 步骤1: 理解单元测试

### 1.1 什么是单元测试？

**单元测试（Unit Testing）** 是对软件中最小可测试单元进行检查和验证的过程。在嵌入式系统中，一个单元通常是一个函数或一个模块。

**单元测试的特点**:
- **独立性**: 每个测试独立运行，不依赖其他测试
- **自动化**: 可以自动执行，无需人工干预
- **快速**: 执行速度快，可以频繁运行
- **可重复**: 每次运行结果一致
- **明确**: 测试结果清晰（通过/失败）

**简单示例**:
```c
// 被测试的函数
int add(int a, int b) {
    return a + b;
}

// 测试用例
void test_add_positive_numbers(void) {
    int result = add(2, 3);
    assert(result == 5);  // 验证结果
}

void test_add_negative_numbers(void) {
    int result = add(-2, -3);
    assert(result == -5);
}

void test_add_zero(void) {
    int result = add(0, 5);
    assert(result == 5);
}
```

### 1.2 为什么需要单元测试？

**在嵌入式系统中的价值**:

1. **早期发现Bug**
   - 在开发阶段就发现问题
   - 修复成本低
   - 避免问题传播到集成阶段

2. **提高代码质量**
   - 强制模块化设计
   - 促进代码解耦
   - 提高可维护性

3. **支持重构**
   - 安全地修改代码
   - 快速验证修改正确性
   - 减少回归风险

4. **文档作用**
   - 测试用例展示如何使用代码
   - 说明预期行为
   - 补充技术文档

5. **提高开发效率**
   - 减少调试时间
   - 快速验证功能
   - 支持持续集成

**成本对比**:
```
发现阶段     修复成本     时间成本
开发阶段     1x          1小时
集成阶段     10x         1天
测试阶段     100x        1周
生产阶段     1000x       数月
```

### 1.3 单元测试的基本原则

**FIRST原则**:

1. **Fast（快速）**
   - 测试应该快速执行
   - 开发者可以频繁运行
   - 目标：整个测试套件在几秒内完成

2. **Independent（独立）**
   - 测试之间不应相互依赖
   - 可以任意顺序执行
   - 一个测试失败不影响其他测试

3. **Repeatable（可重复）**
   - 每次运行结果一致
   - 不依赖外部环境
   - 不依赖时间或随机数

4. **Self-Validating（自我验证）**
   - 测试自动判断通过或失败
   - 不需要人工检查输出
   - 结果明确（布尔值）

5. **Timely（及时）**
   - 在编写生产代码之前或同时编写测试
   - 支持测试驱动开发（TDD）
   - 不要等到项目结束才写测试

**AAA模式**:

每个测试用例应遵循AAA模式：

```c
void test_example(void) {
    // Arrange（准备）- 设置测试环境和输入
    int input1 = 5;
    int input2 = 3;
    int expected = 8;
    
    // Act（执行）- 调用被测试的函数
    int actual = add(input1, input2);
    
    // Assert（断言）- 验证结果
    assert(actual == expected);
}
```

### 1.4 单元测试 vs 其他测试

| 测试类型 | 范围 | 速度 | 隔离性 | 执行频率 |
|---------|------|------|--------|---------|
| **单元测试** | 单个函数/模块 | 非常快 | 完全隔离 | 每次提交 |
| **集成测试** | 多个模块交互 | 较快 | 部分隔离 | 每天 |
| **系统测试** | 整个系统 | 慢 | 真实环境 | 每周 |
| **验收测试** | 用户场景 | 很慢 | 真实环境 | 发布前 |

**测试金字塔**:
```
        /\
       /验收\      少量，慢，昂贵
      /------\
     /  系统  \    中等数量
    /----------\
   /   集成     \  较多
  /--------------\
 /    单元测试    \ 大量，快，便宜
/------------------\
```

**关键点**:
- 单元测试应该占测试的大部分（70-80%）
- 单元测试提供最快的反馈
- 单元测试最容易维护


## 步骤2: 选择测试框架

### 2.1 嵌入式测试框架对比

**主流框架对比**:

| 框架 | 语言 | 大小 | 学习曲线 | 特点 | 适用场景 |
|------|------|------|---------|------|---------|
| **Unity** | C | 很小 | 简单 | 轻量级，纯C | 资源受限的嵌入式 |
| **CppUTest** | C/C++ | 中等 | 中等 | 功能丰富，Mock支持 | 中大型嵌入式项目 |
| **Google Test** | C++ | 较大 | 较难 | 功能强大，生态好 | PC端或高端嵌入式 |
| **Ceedling** | C | 小 | 简单 | Unity+CMock+Rake | 快速搭建测试环境 |
| **CMocka** | C | 小 | 简单 | 纯C，Mock支持 | 需要Mock的C项目 |

### 2.2 Unity测试框架

**Unity** 是专为嵌入式系统设计的轻量级C测试框架。

**优势**:
- 极小的内存占用（<2KB）
- 纯C实现，无依赖
- 可以在目标硬件上运行
- 简单易学
- 广泛使用

**安装Unity**:
```bash
# 克隆Unity仓库
git clone https://github.com/ThrowTheSwitch/Unity.git

# 或者作为子模块添加到项目
git submodule add https://github.com/ThrowTheSwitch/Unity.git test/Unity
```

**基本使用**:
```c
// test_example.c
#include "unity.h"
#include "my_module.h"

// 每个测试前执行
void setUp(void) {
    // 初始化测试环境
}

// 每个测试后执行
void tearDown(void) {
    // 清理测试环境
}

// 测试用例
void test_add_should_return_sum(void) {
    TEST_ASSERT_EQUAL(5, add(2, 3));
}

void test_add_should_handle_negative(void) {
    TEST_ASSERT_EQUAL(-5, add(-2, -3));
}

// 主函数
int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_add_should_return_sum);
    RUN_TEST(test_add_should_handle_negative);
    return UNITY_END();
}
```

**常用断言**:
```c
// 相等性断言
TEST_ASSERT_EQUAL(expected, actual);
TEST_ASSERT_EQUAL_INT(expected, actual);
TEST_ASSERT_EQUAL_FLOAT(expected, actual);
TEST_ASSERT_EQUAL_STRING(expected, actual);

// 布尔断言
TEST_ASSERT_TRUE(condition);
TEST_ASSERT_FALSE(condition);
TEST_ASSERT_NULL(pointer);
TEST_ASSERT_NOT_NULL(pointer);

// 数组断言
TEST_ASSERT_EQUAL_INT_ARRAY(expected, actual, num_elements);
TEST_ASSERT_EQUAL_MEMORY(expected, actual, num_bytes);

// 范围断言
TEST_ASSERT_INT_WITHIN(delta, expected, actual);
TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual);
```

### 2.3 CppUTest框架

**CppUTest** 是功能更丰富的C/C++测试框架，支持Mock。

**安装CppUTest**:
```bash
# Ubuntu/Debian
sudo apt install cpputest

# 或从源码编译
git clone https://github.com/cpputest/cpputest.git
cd cpputest
mkdir build && cd build
cmake ..
make
sudo make install
```

**基本使用**:
```cpp
// test_example.cpp
#include "CppUTest/TestHarness.h"
#include "my_module.h"

// 测试组
TEST_GROUP(MyModule)
{
    void setup() {
        // 每个测试前执行
    }
    
    void teardown() {
        // 每个测试后执行
    }
};

// 测试用例
TEST(MyModule, AddShouldReturnSum)
{
    CHECK_EQUAL(5, add(2, 3));
}

TEST(MyModule, AddShouldHandleNegative)
{
    CHECK_EQUAL(-5, add(-2, -3));
}

// 主函数
int main(int argc, char** argv)
{
    return CommandLineTestRunner::RunAllTests(argc, argv);
}
```

**常用断言**:
```cpp
// 相等性检查
CHECK_EQUAL(expected, actual);
LONGS_EQUAL(expected, actual);
DOUBLES_EQUAL(expected, actual, tolerance);
STRCMP_EQUAL(expected, actual);

// 布尔检查
CHECK(condition);
CHECK_TRUE(condition);
CHECK_FALSE(condition);

// 指针检查
POINTERS_EQUAL(expected, actual);

// 失败检查
FAIL("Message");
```

### 2.4 框架选择建议

**选择Unity的场景**:
- 资源非常受限（RAM < 32KB）
- 需要在目标硬件上运行测试
- 团队主要使用C语言
- 项目规模较小
- 需要快速上手

**选择CppUTest的场景**:
- 需要Mock功能
- 项目使用C++
- 资源相对充足
- 需要更丰富的断言
- 项目规模中等到大型

**选择Google Test的场景**:
- 主要在PC上测试
- 项目使用现代C++
- 需要参数化测试
- 需要强大的生态系统
- 资源不是问题

**本教程选择**:
我们将主要使用Unity，因为它最适合嵌入式系统，同时也会介绍如何使用CppUTest的Mock功能。


## 步骤3: 搭建测试环境

### 3.1 项目结构设计

**推荐的项目结构**:
```
my_project/
├── src/                    # 源代码
│   ├── module1.c
│   ├── module1.h
│   ├── module2.c
│   └── module2.h
├── test/                   # 测试代码
│   ├── Unity/             # Unity框架
│   ├── test_module1.c     # module1的测试
│   ├── test_module2.c     # module2的测试
│   └── test_runner.c      # 测试运行器
├── build/                  # 构建输出
├── Makefile               # 构建脚本
└── README.md
```

### 3.2 使用Makefile构建

**基本Makefile**:
```makefile
# Makefile for Unity tests

# 编译器设置
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g

# 目录设置
SRC_DIR = src
TEST_DIR = test
BUILD_DIR = build
UNITY_DIR = $(TEST_DIR)/Unity/src

# 源文件
SRC_FILES = $(wildcard $(SRC_DIR)/*.c)
TEST_FILES = $(wildcard $(TEST_DIR)/test_*.c)

# 目标文件
SRC_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRC_FILES))
TEST_OBJS = $(patsubst $(TEST_DIR)/%.c,$(BUILD_DIR)/%.o,$(TEST_FILES))
UNITY_OBJ = $(BUILD_DIR)/unity.o

# 包含路径
INCLUDES = -I$(SRC_DIR) -I$(UNITY_DIR)

# 测试可执行文件
TEST_EXEC = $(BUILD_DIR)/test_runner

# 默认目标
all: test

# 创建构建目录
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# 编译源文件
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# 编译测试文件
$(BUILD_DIR)/%.o: $(TEST_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# 编译Unity
$(UNITY_OBJ): $(UNITY_DIR)/unity.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# 链接测试可执行文件
$(TEST_EXEC): $(SRC_OBJS) $(TEST_OBJS) $(UNITY_OBJ)
	$(CC) $(CFLAGS) $^ -o $@

# 运行测试
test: $(TEST_EXEC)
	./$(TEST_EXEC)

# 清理
clean:
	rm -rf $(BUILD_DIR)

# 伪目标
.PHONY: all test clean
```

### 3.3 使用CMake构建

**CMakeLists.txt**:
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject C)

# 设置C标准
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 编译选项
add_compile_options(-Wall -Wextra -g)

# 包含目录
include_directories(src)
include_directories(test/Unity/src)

# 源文件
file(GLOB SRC_FILES "src/*.c")
file(GLOB TEST_FILES "test/test_*.c")

# Unity库
add_library(unity STATIC test/Unity/src/unity.c)

# 测试可执行文件
add_executable(test_runner ${TEST_FILES} ${SRC_FILES})
target_link_libraries(test_runner unity)

# 启用测试
enable_testing()
add_test(NAME AllTests COMMAND test_runner)

# 自定义目标：运行测试
add_custom_target(run_tests
    COMMAND test_runner
    DEPENDS test_runner
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)
```

**使用CMake**:
```bash
# 创建构建目录
mkdir build && cd build

# 配置项目
cmake ..

# 编译
make

# 运行测试
make run_tests

# 或使用CTest
ctest --verbose
```

### 3.4 配置IDE集成

**VS Code配置** (`.vscode/tasks.json`):
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Tests",
            "type": "shell",
            "command": "make",
            "args": ["test"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": ["$gcc"]
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "./build/test_runner",
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "dependsOn": ["Build Tests"]
        },
        {
            "label": "Clean",
            "type": "shell",
            "command": "make",
            "args": ["clean"]
        }
    ]
}
```

**VS Code启动配置** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Tests",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/test_runner",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "preLaunchTask": "Build Tests"
        }
    ]
}
```


## 步骤4: 编写测试用例

### 4.1 测试用例设计原则

**好的测试用例特征**:

1. **单一职责**
   - 每个测试只验证一个行为
   - 测试失败时容易定位问题

2. **清晰的命名**
   - 使用描述性名称
   - 说明测试的内容和预期结果

3. **独立性**
   - 不依赖其他测试
   - 不依赖执行顺序

4. **完整性**
   - 测试正常情况
   - 测试边界条件
   - 测试错误情况

**命名约定**:
```c
// 格式：test_<function>_<scenario>_<expected_result>

void test_add_positive_numbers_returns_sum(void);
void test_add_with_zero_returns_other_number(void);
void test_add_negative_numbers_returns_negative_sum(void);
void test_divide_by_zero_returns_error(void);
```

### 4.2 实际示例：LED控制模块

**被测试的模块** (`led.h`):
```c
#ifndef LED_H
#define LED_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    LED_RED = 0,
    LED_GREEN = 1,
    LED_BLUE = 2,
    LED_COUNT
} LED_ID;

typedef enum {
    LED_OFF = 0,
    LED_ON = 1
} LED_State;

// 初始化LED模块
void LED_Init(void);

// 设置LED状态
void LED_SetState(LED_ID led, LED_State state);

// 获取LED状态
LED_State LED_GetState(LED_ID led);

// 切换LED状态
void LED_Toggle(LED_ID led);

// 设置所有LED
void LED_SetAll(LED_State state);

#endif // LED_H
```

**实现** (`led.c`):
```c
#include "led.h"
#include "gpio.h"  // 硬件抽象层

static LED_State led_states[LED_COUNT];

void LED_Init(void) {
    for (int i = 0; i < LED_COUNT; i++) {
        led_states[i] = LED_OFF;
        GPIO_SetPin(i, 0);
    }
}

void LED_SetState(LED_ID led, LED_State state) {
    if (led >= LED_COUNT) {
        return;  // 无效的LED ID
    }
    
    led_states[led] = state;
    GPIO_SetPin(led, state);
}

LED_State LED_GetState(LED_ID led) {
    if (led >= LED_COUNT) {
        return LED_OFF;
    }
    return led_states[led];
}

void LED_Toggle(LED_ID led) {
    if (led >= LED_COUNT) {
        return;
    }
    
    LED_State new_state = (led_states[led] == LED_OFF) ? LED_ON : LED_OFF;
    LED_SetState(led, new_state);
}

void LED_SetAll(LED_State state) {
    for (int i = 0; i < LED_COUNT; i++) {
        LED_SetState(i, state);
    }
}
```

**测试用例** (`test_led.c`):
```c
#include "unity.h"
#include "led.h"
#include "mock_gpio.h"  // Mock的GPIO接口

void setUp(void) {
    // 每个测试前初始化
    LED_Init();
}

void tearDown(void) {
    // 每个测试后清理
}

// 测试初始化
void test_LED_Init_should_turn_off_all_leds(void) {
    LED_Init();
    
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_RED));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_GREEN));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_BLUE));
}

// 测试设置状态
void test_LED_SetState_should_turn_on_led(void) {
    LED_SetState(LED_RED, LED_ON);
    
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_RED));
}

void test_LED_SetState_should_turn_off_led(void) {
    LED_SetState(LED_RED, LED_ON);
    LED_SetState(LED_RED, LED_OFF);
    
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_RED));
}

void test_LED_SetState_with_invalid_id_should_not_crash(void) {
    // 测试边界条件
    LED_SetState(LED_COUNT, LED_ON);  // 无效ID
    LED_SetState(255, LED_ON);        // 无效ID
    
    // 如果没有崩溃，测试通过
    TEST_PASS();
}

// 测试切换
void test_LED_Toggle_should_change_state_from_off_to_on(void) {
    LED_SetState(LED_GREEN, LED_OFF);
    LED_Toggle(LED_GREEN);
    
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_GREEN));
}

void test_LED_Toggle_should_change_state_from_on_to_off(void) {
    LED_SetState(LED_GREEN, LED_ON);
    LED_Toggle(LED_GREEN);
    
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_GREEN));
}

void test_LED_Toggle_twice_should_return_to_original_state(void) {
    LED_SetState(LED_BLUE, LED_OFF);
    LED_Toggle(LED_BLUE);
    LED_Toggle(LED_BLUE);
    
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_BLUE));
}

// 测试设置所有LED
void test_LED_SetAll_should_turn_on_all_leds(void) {
    LED_SetAll(LED_ON);
    
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_RED));
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_GREEN));
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_BLUE));
}

void test_LED_SetAll_should_turn_off_all_leds(void) {
    LED_SetAll(LED_ON);  // 先全部打开
    LED_SetAll(LED_OFF); // 再全部关闭
    
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_RED));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_GREEN));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_BLUE));
}

// 测试独立性
void test_LED_SetState_should_not_affect_other_leds(void) {
    LED_SetState(LED_RED, LED_ON);
    LED_SetState(LED_GREEN, LED_OFF);
    
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_RED));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_GREEN));
    TEST_ASSERT_EQUAL(LED_OFF, LED_GetState(LED_BLUE));
}

// 主函数
int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_LED_Init_should_turn_off_all_leds);
    RUN_TEST(test_LED_SetState_should_turn_on_led);
    RUN_TEST(test_LED_SetState_should_turn_off_led);
    RUN_TEST(test_LED_SetState_with_invalid_id_should_not_crash);
    RUN_TEST(test_LED_Toggle_should_change_state_from_off_to_on);
    RUN_TEST(test_LED_Toggle_should_change_state_from_on_to_off);
    RUN_TEST(test_LED_Toggle_twice_should_return_to_original_state);
    RUN_TEST(test_LED_SetAll_should_turn_on_all_leds);
    RUN_TEST(test_LED_SetAll_should_turn_off_all_leds);
    RUN_TEST(test_LED_SetState_should_not_affect_other_leds);
    
    return UNITY_END();
}
```

### 4.3 边界条件测试

**边界条件类型**:

1. **数值边界**
```c
void test_temperature_sensor_min_value(void) {
    int temp = read_temperature(-40);  // 最小值
    TEST_ASSERT_EQUAL(-40, temp);
}

void test_temperature_sensor_max_value(void) {
    int temp = read_temperature(125);  // 最大值
    TEST_ASSERT_EQUAL(125, temp);
}

void test_temperature_sensor_below_min_returns_error(void) {
    int result = read_temperature(-50);  // 超出范围
    TEST_ASSERT_EQUAL(ERROR_OUT_OF_RANGE, result);
}
```

2. **数组边界**
```c
void test_buffer_write_at_start(void) {
    buffer_write(0, 'A');  // 第一个位置
    TEST_ASSERT_EQUAL('A', buffer_read(0));
}

void test_buffer_write_at_end(void) {
    buffer_write(BUFFER_SIZE - 1, 'Z');  // 最后一个位置
    TEST_ASSERT_EQUAL('Z', buffer_read(BUFFER_SIZE - 1));
}

void test_buffer_write_beyond_end_returns_error(void) {
    int result = buffer_write(BUFFER_SIZE, 'X');  // 超出范围
    TEST_ASSERT_EQUAL(ERROR_INDEX_OUT_OF_BOUNDS, result);
}
```

3. **空值和NULL**
```c
void test_string_length_with_null_pointer(void) {
    int len = string_length(NULL);
    TEST_ASSERT_EQUAL(0, len);
}

void test_string_length_with_empty_string(void) {
    int len = string_length("");
    TEST_ASSERT_EQUAL(0, len);
}
```

4. **状态转换边界**
```c
void test_state_machine_invalid_transition(void) {
    set_state(STATE_IDLE);
    int result = transition_to(STATE_ERROR);  // 不允许的转换
    TEST_ASSERT_EQUAL(ERROR_INVALID_TRANSITION, result);
    TEST_ASSERT_EQUAL(STATE_IDLE, get_state());  // 状态不变
}
```

### 4.4 错误处理测试

**测试错误情况**:
```c
// 测试除零错误
void test_divide_by_zero_returns_error(void) {
    int result;
    int error = safe_divide(10, 0, &result);
    
    TEST_ASSERT_EQUAL(ERROR_DIVIDE_BY_ZERO, error);
}

// 测试内存分配失败
void test_create_object_with_no_memory_returns_null(void) {
    // 模拟内存耗尽
    mock_malloc_fail_next_call();
    
    Object *obj = create_object();
    
    TEST_ASSERT_NULL(obj);
}

// 测试超时
void test_wait_for_response_timeout(void) {
    int result = wait_for_response(100);  // 100ms超时
    
    TEST_ASSERT_EQUAL(ERROR_TIMEOUT, result);
}

// 测试资源竞争
void test_acquire_locked_resource_returns_busy(void) {
    acquire_resource();  // 第一次获取
    int result = acquire_resource();  // 第二次获取
    
    TEST_ASSERT_EQUAL(ERROR_RESOURCE_BUSY, result);
}
```


## 步骤5: Mock和Stub技术

### 5.1 理解Mock和Stub

**定义**:

- **Stub（桩）**: 提供预定义的返回值，用于替代真实依赖
- **Mock（模拟）**: 不仅提供返回值，还验证调用行为
- **Fake（伪造）**: 简化的实现，有实际逻辑但不适合生产

**为什么需要Mock？**

在嵌入式系统中，很多代码依赖硬件：
- GPIO操作
- 串口通信
- I2C/SPI总线
- 定时器
- 中断

这些依赖使得单元测试困难：
- 无法在PC上运行
- 测试速度慢
- 难以模拟错误情况
- 需要真实硬件

**解决方案**：使用Mock替代硬件依赖

### 5.2 手动创建Mock

**原始GPIO接口** (`gpio.h`):
```c
#ifndef GPIO_H
#define GPIO_H

#include <stdint.h>

void GPIO_Init(void);
void GPIO_SetPin(uint8_t pin, uint8_t value);
uint8_t GPIO_ReadPin(uint8_t pin);

#endif
```

**Mock实现** (`mock_gpio.c`):
```c
#include "gpio.h"
#include <string.h>

// Mock状态
static uint8_t mock_pin_states[32];
static int mock_set_pin_call_count = 0;
static uint8_t mock_last_pin_set = 0;
static uint8_t mock_last_value_set = 0;

// Mock初始化
void mock_gpio_init(void) {
    memset(mock_pin_states, 0, sizeof(mock_pin_states));
    mock_set_pin_call_count = 0;
    mock_last_pin_set = 0;
    mock_last_value_set = 0;
}

// Mock实现
void GPIO_Init(void) {
    // 什么都不做
}

void GPIO_SetPin(uint8_t pin, uint8_t value) {
    mock_pin_states[pin] = value;
    mock_set_pin_call_count++;
    mock_last_pin_set = pin;
    mock_last_value_set = value;
}

uint8_t GPIO_ReadPin(uint8_t pin) {
    return mock_pin_states[pin];
}

// Mock验证函数
int mock_gpio_get_set_pin_call_count(void) {
    return mock_set_pin_call_count;
}

uint8_t mock_gpio_get_last_pin_set(void) {
    return mock_last_pin_set;
}

uint8_t mock_gpio_get_last_value_set(void) {
    return mock_last_value_set;
}

uint8_t mock_gpio_get_pin_state(uint8_t pin) {
    return mock_pin_states[pin];
}
```

**使用Mock的测试**:
```c
#include "unity.h"
#include "led.h"
#include "mock_gpio.h"

void setUp(void) {
    mock_gpio_init();
    LED_Init();
}

void test_LED_SetState_should_call_GPIO_SetPin(void) {
    LED_SetState(LED_RED, LED_ON);
    
    // 验证GPIO_SetPin被调用
    TEST_ASSERT_EQUAL(1, mock_gpio_get_set_pin_call_count());
    TEST_ASSERT_EQUAL(LED_RED, mock_gpio_get_last_pin_set());
    TEST_ASSERT_EQUAL(LED_ON, mock_gpio_get_last_value_set());
}

void test_LED_SetAll_should_call_GPIO_SetPin_three_times(void) {
    LED_SetAll(LED_ON);
    
    // 验证GPIO_SetPin被调用3次（3个LED）
    TEST_ASSERT_EQUAL(3, mock_gpio_get_set_pin_call_count());
}
```

### 5.3 使用CMock自动生成Mock

**CMock** 是Unity的配套工具，可以自动生成Mock代码。

**安装CMock**:
```bash
git clone https://github.com/ThrowTheSwitch/CMock.git test/CMock
```

**CMock配置** (`project.yml`):
```yaml
:cmock:
  :mock_prefix: mock_
  :when_no_prototypes: :warn
  :enforce_strict_ordering: true
  :plugins:
    - :ignore
    - :callback
    - :return_thru_ptr
  :treat_as:
    uint8:    HEX8
    uint16:   HEX16
    uint32:   UINT32
  :includes:
    - <stdint.h>
    - <stdbool.h>
```

**生成Mock**:
```bash
# 从头文件生成Mock
ruby test/CMock/lib/cmock.rb gpio.h
```

**生成的Mock使用**:
```c
#include "unity.h"
#include "led.h"
#include "mock_gpio.h"  // CMock生成的

void setUp(void) {
    LED_Init();
}

void tearDown(void) {
}

void test_LED_SetState_should_call_GPIO_SetPin_with_correct_params(void) {
    // 设置期望：GPIO_SetPin将被调用，参数为(LED_RED, LED_ON)
    GPIO_SetPin_Expect(LED_RED, LED_ON);
    
    // 执行被测试的函数
    LED_SetState(LED_RED, LED_ON);
    
    // CMock自动验证GPIO_SetPin是否被正确调用
}

void test_LED_Toggle_should_read_then_write_GPIO(void) {
    // 设置期望：先读取当前状态
    GPIO_ReadPin_ExpectAndReturn(LED_GREEN, 0);
    
    // 然后设置新状态
    GPIO_SetPin_Expect(LED_GREEN, 1);
    
    // 执行
    LED_Toggle(LED_GREEN);
}
```

### 5.4 高级Mock技术

**回调Mock**:
```c
// 自定义回调函数
uint8_t custom_gpio_read(uint8_t pin, int num_calls) {
    // 第一次调用返回0，第二次返回1
    return (num_calls == 0) ? 0 : 1;
}

void test_with_callback(void) {
    // 使用回调
    GPIO_ReadPin_StubWithCallback(custom_gpio_read);
    
    uint8_t value1 = GPIO_ReadPin(0);  // 返回0
    uint8_t value2 = GPIO_ReadPin(0);  // 返回1
    
    TEST_ASSERT_EQUAL(0, value1);
    TEST_ASSERT_EQUAL(1, value2);
}
```

**序列Mock**（多次调用返回不同值）:
```c
void test_multiple_calls_different_returns(void) {
    // 第一次调用返回0
    GPIO_ReadPin_ExpectAndReturn(LED_RED, 0);
    
    // 第二次调用返回1
    GPIO_ReadPin_ExpectAndReturn(LED_RED, 1);
    
    // 执行
    uint8_t value1 = GPIO_ReadPin(LED_RED);
    uint8_t value2 = GPIO_ReadPin(LED_RED);
    
    TEST_ASSERT_EQUAL(0, value1);
    TEST_ASSERT_EQUAL(1, value2);
}
```

**忽略参数**:
```c
void test_ignore_parameters(void) {
    // 忽略pin参数，任何值都可以
    GPIO_SetPin_Ignore();
    
    // 这些调用都会通过
    GPIO_SetPin(0, 1);
    GPIO_SetPin(1, 0);
    GPIO_SetPin(99, 1);
}
```

**返回指针数据**:
```c
void test_return_data_through_pointer(void) {
    uint8_t expected_data[] = {1, 2, 3, 4};
    
    // 通过指针返回数据
    SPI_Read_ExpectAndReturn(NULL, 4, 0);
    SPI_Read_IgnoreArg_buffer();
    SPI_Read_ReturnArrayThruPtr_buffer(expected_data, 4);
    
    uint8_t actual_data[4];
    SPI_Read(actual_data, 4);
    
    TEST_ASSERT_EQUAL_UINT8_ARRAY(expected_data, actual_data, 4);
}
```

### 5.5 依赖注入

**依赖注入**是一种设计模式，使代码更容易测试。

**不好的设计**（硬编码依赖）:
```c
// led.c
#include "gpio.h"  // 硬编码依赖

void LED_SetState(LED_ID led, LED_State state) {
    GPIO_SetPin(led, state);  // 直接调用硬件
}
```

**好的设计**（依赖注入）:
```c
// led.h
typedef struct {
    void (*set_pin)(uint8_t pin, uint8_t value);
    uint8_t (*read_pin)(uint8_t pin);
} GPIO_Interface;

void LED_Init(GPIO_Interface *gpio);
void LED_SetState(LED_ID led, LED_State state);

// led.c
static GPIO_Interface *gpio_interface = NULL;

void LED_Init(GPIO_Interface *gpio) {
    gpio_interface = gpio;
}

void LED_SetState(LED_ID led, LED_State state) {
    if (gpio_interface && gpio_interface->set_pin) {
        gpio_interface->set_pin(led, state);
    }
}
```

**测试时注入Mock**:
```c
// Mock GPIO接口
static void mock_set_pin(uint8_t pin, uint8_t value) {
    // Mock实现
}

static uint8_t mock_read_pin(uint8_t pin) {
    // Mock实现
    return 0;
}

void test_with_dependency_injection(void) {
    // 创建Mock接口
    GPIO_Interface mock_gpio = {
        .set_pin = mock_set_pin,
        .read_pin = mock_read_pin
    };
    
    // 注入Mock
    LED_Init(&mock_gpio);
    
    // 测试
    LED_SetState(LED_RED, LED_ON);
    
    // 验证...
}
```

**生产代码注入真实接口**:
```c
// main.c
#include "led.h"
#include "gpio.h"

int main(void) {
    // 创建真实GPIO接口
    GPIO_Interface real_gpio = {
        .set_pin = GPIO_SetPin,
        .read_pin = GPIO_ReadPin
    };
    
    // 注入真实接口
    LED_Init(&real_gpio);
    
    // 正常使用
    LED_SetState(LED_RED, LED_ON);
    
    return 0;
}
```


## 步骤6: 代码覆盖率分析

### 6.1 理解代码覆盖率

**代码覆盖率（Code Coverage）** 衡量测试执行了多少代码。

**覆盖率类型**:

1. **行覆盖率（Line Coverage）**
   - 执行了多少行代码
   - 最基本的覆盖率指标

2. **函数覆盖率（Function Coverage）**
   - 调用了多少函数
   - 确保所有函数都被测试

3. **分支覆盖率（Branch Coverage）**
   - 执行了多少分支（if/else）
   - 比行覆盖率更严格

4. **条件覆盖率（Condition Coverage）**
   - 每个布尔表达式的真假情况
   - 最严格的覆盖率

**覆盖率目标**:
- 关键模块：90-100%
- 一般模块：70-80%
- 整体项目：60-70%

**注意**：高覆盖率不等于高质量测试！

### 6.2 使用gcov和lcov

**gcov** 是GCC的覆盖率工具，**lcov** 生成HTML报告。

**步骤1: 编译时启用覆盖率**:
```makefile
# Makefile
CFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lgcov --coverage

# 或使用--coverage选项（推荐）
CFLAGS += --coverage
LDFLAGS += --coverage
```

**步骤2: 运行测试**:
```bash
# 编译
make clean
make test

# 运行测试（生成.gcda文件）
./build/test_runner

# 生成覆盖率数据
gcov src/*.c
```

**步骤3: 生成HTML报告**:
```bash
# 安装lcov
sudo apt install lcov

# 捕获覆盖率数据
lcov --capture --directory . --output-file coverage.info

# 过滤系统文件和测试文件
lcov --remove coverage.info '/usr/*' '*/test/*' --output-file coverage_filtered.info

# 生成HTML报告
genhtml coverage_filtered.info --output-directory coverage_html

# 查看报告
xdg-open coverage_html/index.html
```

**完整的Makefile示例**:
```makefile
# Makefile with coverage support

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
COVERAGE_FLAGS = --coverage
LDFLAGS = --coverage

SRC_DIR = src
TEST_DIR = test
BUILD_DIR = build
UNITY_DIR = $(TEST_DIR)/Unity/src

SRC_FILES = $(wildcard $(SRC_DIR)/*.c)
TEST_FILES = $(wildcard $(TEST_DIR)/test_*.c)

SRC_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRC_FILES))
TEST_OBJS = $(patsubst $(TEST_DIR)/%.c,$(BUILD_DIR)/%.o,$(TEST_FILES))
UNITY_OBJ = $(BUILD_DIR)/unity.o

INCLUDES = -I$(SRC_DIR) -I$(UNITY_DIR)

TEST_EXEC = $(BUILD_DIR)/test_runner

.PHONY: all test coverage clean

all: test

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# 编译源文件（带覆盖率）
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(COVERAGE_FLAGS) $(INCLUDES) -c $< -o $@

# 编译测试文件
$(BUILD_DIR)/%.o: $(TEST_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# 编译Unity
$(UNITY_OBJ): $(UNITY_DIR)/unity.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# 链接
$(TEST_EXEC): $(SRC_OBJS) $(TEST_OBJS) $(UNITY_OBJ)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# 运行测试
test: $(TEST_EXEC)
	./$(TEST_EXEC)

# 生成覆盖率报告
coverage: test
	@echo "Generating coverage report..."
	lcov --capture --directory $(BUILD_DIR) --output-file coverage.info
	lcov --remove coverage.info '/usr/*' '*/test/*' '*/Unity/*' --output-file coverage_filtered.info
	genhtml coverage_filtered.info --output-directory coverage_html
	@echo "Coverage report generated in coverage_html/index.html"

# 清理
clean:
	rm -rf $(BUILD_DIR) *.gcov *.gcda *.gcno coverage.info coverage_filtered.info coverage_html
```

### 6.3 分析覆盖率报告

**查看未覆盖的代码**:
```bash
# 查看特定文件的覆盖率
gcov src/led.c

# 输出示例
File 'src/led.c'
Lines executed:85.71% of 14
Creating 'led.c.gcov'
```

**led.c.gcov文件内容**:
```
        -:    0:Source:src/led.c
        -:    1:#include "led.h"
        -:    2:#include "gpio.h"
        -:    3:
        3:    4:static LED_State led_states[LED_COUNT];
        -:    5:
        1:    6:void LED_Init(void) {
        4:    7:    for (int i = 0; i < LED_COUNT; i++) {
        3:    8:        led_states[i] = LED_OFF;
        3:    9:        GPIO_SetPin(i, 0);
        -:   10:    }
        1:   11:}
        -:   12:
        5:   13:void LED_SetState(LED_ID led, LED_State state) {
        5:   14:    if (led >= LED_COUNT) {
    #####:   15:        return;  // 未覆盖！
        -:   16:    }
        5:   17:    led_states[led] = state;
        5:   18:    GPIO_SetPin(led, state);
        5:   19:}
```

**解读**:
- 数字：该行被执行的次数
- `-`：非可执行行（注释、声明）
- `#####`：未执行的行（需要添加测试）

**添加测试覆盖未覆盖的代码**:
```c
void test_LED_SetState_with_invalid_id_should_return_early(void) {
    // 测试第15行的边界检查
    LED_SetState(LED_COUNT, LED_ON);
    LED_SetState(255, LED_ON);
    
    // 验证没有崩溃
    TEST_PASS();
}
```

### 6.4 提高覆盖率的策略

**1. 识别未覆盖的分支**:
```c
int process_data(int value) {
    if (value < 0) {
        return ERROR_NEGATIVE;  // 分支1
    } else if (value > 100) {
        return ERROR_TOO_LARGE; // 分支2
    } else {
        return value * 2;       // 分支3
    }
}

// 需要3个测试用例覆盖所有分支
void test_process_data_negative(void) {
    TEST_ASSERT_EQUAL(ERROR_NEGATIVE, process_data(-1));
}

void test_process_data_too_large(void) {
    TEST_ASSERT_EQUAL(ERROR_TOO_LARGE, process_data(101));
}

void test_process_data_normal(void) {
    TEST_ASSERT_EQUAL(10, process_data(5));
}
```

**2. 测试错误处理路径**:
```c
int read_sensor(void) {
    if (!sensor_is_ready()) {
        return ERROR_NOT_READY;  // 需要测试
    }
    
    int value = sensor_read();
    if (value < 0) {
        return ERROR_READ_FAILED;  // 需要测试
    }
    
    return value;
}

// 使用Mock模拟错误情况
void test_read_sensor_not_ready(void) {
    sensor_is_ready_ExpectAndReturn(false);
    TEST_ASSERT_EQUAL(ERROR_NOT_READY, read_sensor());
}

void test_read_sensor_read_failed(void) {
    sensor_is_ready_ExpectAndReturn(true);
    sensor_read_ExpectAndReturn(-1);
    TEST_ASSERT_EQUAL(ERROR_READ_FAILED, read_sensor());
}
```

**3. 测试循环边界**:
```c
void process_array(int *arr, int size) {
    for (int i = 0; i < size; i++) {
        arr[i] *= 2;
    }
}

// 测试不同的循环次数
void test_process_array_empty(void) {
    int arr[] = {};
    process_array(arr, 0);  // 循环0次
    TEST_PASS();
}

void test_process_array_one_element(void) {
    int arr[] = {5};
    process_array(arr, 1);  // 循环1次
    TEST_ASSERT_EQUAL(10, arr[0]);
}

void test_process_array_multiple_elements(void) {
    int arr[] = {1, 2, 3};
    process_array(arr, 3);  // 循环3次
    TEST_ASSERT_EQUAL(2, arr[0]);
    TEST_ASSERT_EQUAL(4, arr[1]);
    TEST_ASSERT_EQUAL(6, arr[2]);
}
```

### 6.5 覆盖率陷阱

**陷阱1: 追求100%覆盖率**
```c
// 有些代码不需要测试
void assert_handler(void) {
    while(1) {
        // 永远不应该到达这里
        // 不需要测试
    }
}
```

**陷阱2: 覆盖率高但测试质量低**
```c
// 坏的测试：只是执行代码，不验证结果
void bad_test(void) {
    LED_SetState(LED_RED, LED_ON);
    // 没有断言！覆盖率高但没有验证
}

// 好的测试：验证行为
void good_test(void) {
    LED_SetState(LED_RED, LED_ON);
    TEST_ASSERT_EQUAL(LED_ON, LED_GetState(LED_RED));
}
```

**陷阱3: 忽略边界条件**
```c
// 只测试正常情况
void incomplete_test(void) {
    TEST_ASSERT_EQUAL(5, add(2, 3));
    // 覆盖率可能很高，但没有测试边界
}

// 完整的测试
void complete_test(void) {
    TEST_ASSERT_EQUAL(5, add(2, 3));        // 正常
    TEST_ASSERT_EQUAL(0, add(0, 0));        // 零
    TEST_ASSERT_EQUAL(-5, add(-2, -3));     // 负数
    TEST_ASSERT_EQUAL(INT_MAX, add(INT_MAX, 0));  // 边界
}
```

**最佳实践**:
- 覆盖率是工具，不是目标
- 关注测试质量，不只是数量
- 优先测试关键路径
- 使用覆盖率发现遗漏的测试
- 不要为了覆盖率而写无意义的测试


## 步骤7: CI/CD集成

### 7.1 持续集成的重要性

**持续集成（CI）** 自动化测试流程，确保每次代码提交都经过测试。

**CI的好处**:
- 早期发现问题
- 自动化测试执行
- 保证代码质量
- 减少集成问题
- 提高团队信心

### 7.2 GitHub Actions集成

**创建工作流** (`.github/workflows/test.yml`):
```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        submodules: recursive  # 如果使用了子模块
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y gcc make lcov
    
    - name: Build tests
      run: make test
    
    - name: Run tests
      run: ./build/test_runner
    
    - name: Generate coverage report
      run: make coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage_filtered.info
        fail_ci_if_error: true
    
    - name: Archive coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: coverage_html/
```

**添加状态徽章到README**:
```markdown
# My Project

![Tests](https://github.com/username/repo/workflows/Unit%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)

## Description
...
```

### 7.3 GitLab CI集成

**创建配置** (`.gitlab-ci.yml`):
```yaml
image: gcc:latest

stages:
  - build
  - test
  - coverage

before_script:
  - apt-get update -qq
  - apt-get install -y -qq make lcov

build:
  stage: build
  script:
    - make clean
    - make test
  artifacts:
    paths:
      - build/
    expire_in: 1 hour

test:
  stage: test
  dependencies:
    - build
  script:
    - ./build/test_runner
  artifacts:
    reports:
      junit: test_results.xml

coverage:
  stage: coverage
  dependencies:
    - build
    - test
  script:
    - make coverage
    - lcov --summary coverage_filtered.info
  coverage: '/lines......: \d+\.\d+%/'
  artifacts:
    paths:
      - coverage_html/
    expire_in: 30 days
```

### 7.4 Jenkins集成

**Jenkinsfile**:
```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'make clean'
                sh 'make test'
            }
        }
        
        stage('Test') {
            steps {
                sh './build/test_runner'
            }
            post {
                always {
                    junit 'test_results.xml'
                }
            }
        }
        
        stage('Coverage') {
            steps {
                sh 'make coverage'
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
    
    post {
        failure {
            mail to: 'team@example.com',
                 subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                 body: "Check console output at ${env.BUILD_URL}"
        }
    }
}
```

### 7.5 预提交钩子

**Git预提交钩子** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

echo "Running unit tests before commit..."

# 运行测试
make test
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "❌ Tests failed! Commit aborted."
    echo "Please fix the failing tests before committing."
    exit 1
fi

echo "✅ All tests passed!"

# 检查覆盖率
make coverage > /dev/null 2>&1
COVERAGE=$(lcov --summary coverage_filtered.info 2>&1 | grep "lines" | awk '{print $2}' | sed 's/%//')

if (( $(echo "$COVERAGE < 70" | bc -l) )); then
    echo "⚠️  Warning: Coverage is below 70% ($COVERAGE%)"
    echo "Consider adding more tests."
    # 不阻止提交，只是警告
fi

exit 0
```

**安装钩子**:
```bash
# 使钩子可执行
chmod +x .git/hooks/pre-commit

# 或使用脚本自动安装
cat > install_hooks.sh << 'EOF'
#!/bin/bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Git hooks installed successfully!"
EOF

chmod +x install_hooks.sh
./install_hooks.sh
```

### 7.6 自动化测试报告

**生成JUnit格式报告**:

修改测试运行器以输出JUnit XML：

```c
// test_runner.c
#include "unity.h"
#include <stdio.h>
#include <time.h>

static FILE *xml_file = NULL;
static int test_count = 0;
static int failure_count = 0;
static time_t start_time;

void xml_start(const char *suite_name) {
    xml_file = fopen("test_results.xml", "w");
    if (xml_file) {
        fprintf(xml_file, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        fprintf(xml_file, "<testsuite name=\"%s\">\n", suite_name);
    }
    start_time = time(NULL);
}

void xml_test_result(const char *test_name, int passed, const char *message) {
    test_count++;
    if (!passed) {
        failure_count++;
    }
    
    if (xml_file) {
        fprintf(xml_file, "  <testcase name=\"%s\">\n", test_name);
        if (!passed) {
            fprintf(xml_file, "    <failure message=\"%s\"/>\n", message);
        }
        fprintf(xml_file, "  </testcase>\n");
    }
}

void xml_end(void) {
    if (xml_file) {
        time_t end_time = time(NULL);
        double duration = difftime(end_time, start_time);
        
        fprintf(xml_file, "  <system-out/>\n");
        fprintf(xml_file, "  <system-err/>\n");
        fprintf(xml_file, "</testsuite>\n");
        
        fclose(xml_file);
    }
    
    printf("\nTest Summary:\n");
    printf("  Total: %d\n", test_count);
    printf("  Passed: %d\n", test_count - failure_count);
    printf("  Failed: %d\n", failure_count);
}

int main(void) {
    xml_start("EmbeddedTests");
    
    UNITY_BEGIN();
    
    // 运行所有测试...
    RUN_TEST(test_example);
    
    int result = UNITY_END();
    
    xml_end();
    
    return result;
}
```

### 7.7 通知和报告

**Slack通知脚本**:
```bash
#!/bin/bash
# notify_slack.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

if [ $1 -eq 0 ]; then
    STATUS="✅ Success"
    COLOR="good"
else
    STATUS="❌ Failed"
    COLOR="danger"
fi

PAYLOAD=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$COLOR",
            "title": "Test Results",
            "text": "$STATUS",
            "fields": [
                {
                    "title": "Branch",
                    "value": "$(git branch --show-current)",
                    "short": true
                },
                {
                    "title": "Commit",
                    "value": "$(git rev-parse --short HEAD)",
                    "short": true
                }
            ]
        }
    ]
}
EOF
)

curl -X POST -H 'Content-type: application/json' --data "$PAYLOAD" $WEBHOOK_URL
```

**在Makefile中集成**:
```makefile
test: $(TEST_EXEC)
	./$(TEST_EXEC) && ./notify_slack.sh 0 || ./notify_slack.sh 1
```


## 步骤8: 高级测试技术

### 8.1 参数化测试

**问题**：需要用多组数据测试同一个函数

**Unity参数化测试**:
```c
// 测试数据结构
typedef struct {
    int input1;
    int input2;
    int expected;
} AddTestCase;

// 测试数据
static AddTestCase test_cases[] = {
    {2, 3, 5},
    {-2, -3, -5},
    {0, 0, 0},
    {100, 200, 300},
    {-10, 10, 0}
};

void test_add_parameterized(void) {
    int num_cases = sizeof(test_cases) / sizeof(test_cases[0]);
    
    for (int i = 0; i < num_cases; i++) {
        int result = add(test_cases[i].input1, test_cases[i].input2);
        
        char msg[100];
        snprintf(msg, sizeof(msg), "Case %d: add(%d, %d)", 
                 i, test_cases[i].input1, test_cases[i].input2);
        
        TEST_ASSERT_EQUAL_MESSAGE(test_cases[i].expected, result, msg);
    }
}
```

**CppUTest参数化测试**:
```cpp
TEST_GROUP(AddParameterized)
{
    struct TestCase {
        int input1;
        int input2;
        int expected;
    };
    
    static TestCase testCases[];
};

AddParameterized::TestCase AddParameterized::testCases[] = {
    {2, 3, 5},
    {-2, -3, -5},
    {0, 0, 0},
    {100, 200, 300},
    {-10, 10, 0}
};

TEST(AddParameterized, AllCases)
{
    for (auto& tc : testCases) {
        int result = add(tc.input1, tc.input2);
        CHECK_EQUAL(tc.expected, result);
    }
}
```

### 8.2 测试夹具（Fixtures）

**测试夹具**用于设置和清理测试环境。

**复杂的setUp/tearDown**:
```c
// 测试夹具
typedef struct {
    uint8_t *buffer;
    size_t buffer_size;
    SensorConfig config;
} TestFixture;

static TestFixture fixture;

void setUp(void) {
    // 分配资源
    fixture.buffer_size = 1024;
    fixture.buffer = malloc(fixture.buffer_size);
    
    // 初始化配置
    fixture.config.sample_rate = 100;
    fixture.config.resolution = 12;
    
    // 初始化模块
    sensor_init(&fixture.config);
}

void tearDown(void) {
    // 清理资源
    free(fixture.buffer);
    fixture.buffer = NULL;
    
    // 关闭模块
    sensor_deinit();
}

void test_sensor_read_with_fixture(void) {
    // 使用fixture中的资源
    int result = sensor_read(fixture.buffer, fixture.buffer_size);
    TEST_ASSERT_EQUAL(0, result);
}
```

### 8.3 测试替身（Test Doubles）

**五种测试替身**:

1. **Dummy**：传递但不使用的对象
```c
void test_with_dummy(void) {
    // NULL作为dummy，函数不会使用它
    process_data(NULL, 0);
}
```

2. **Stub**：提供固定返回值
```c
int stub_get_temperature(void) {
    return 25;  // 总是返回25
}
```

3. **Spy**：记录调用信息
```c
static int spy_call_count = 0;
static int spy_last_value = 0;

void spy_set_led(int value) {
    spy_call_count++;
    spy_last_value = value;
}

void test_with_spy(void) {
    set_led(1);
    TEST_ASSERT_EQUAL(1, spy_call_count);
    TEST_ASSERT_EQUAL(1, spy_last_value);
}
```

4. **Mock**：验证交互
```c
// 使用CMock
void test_with_mock(void) {
    GPIO_SetPin_Expect(LED_RED, 1);  // 期望被调用
    LED_SetState(LED_RED, LED_ON);
    // CMock自动验证
}
```

5. **Fake**：简化的实现
```c
// 真实的EEPROM操作很慢
// Fake使用内存数组模拟
static uint8_t fake_eeprom[256];

void fake_eeprom_write(uint8_t addr, uint8_t data) {
    fake_eeprom[addr] = data;
}

uint8_t fake_eeprom_read(uint8_t addr) {
    return fake_eeprom[addr];
}
```

### 8.4 测试驱动开发（TDD）

**TDD流程**：红-绿-重构

**步骤1: 红（写失败的测试）**
```c
// 先写测试
void test_calculate_average_should_return_correct_value(void) {
    int values[] = {10, 20, 30};
    int avg = calculate_average(values, 3);
    TEST_ASSERT_EQUAL(20, avg);
}

// 运行测试 -> 失败（函数还不存在）
```

**步骤2: 绿（写最简单的实现）**
```c
// 实现函数
int calculate_average(int *values, int count) {
    if (count == 0) return 0;
    
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += values[i];
    }
    
    return sum / count;
}

// 运行测试 -> 通过
```

**步骤3: 重构（优化代码）**
```c
// 重构：添加错误处理
int calculate_average(int *values, int count) {
    if (values == NULL || count <= 0) {
        return 0;
    }
    
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += values[i];
    }
    
    return sum / count;
}

// 运行测试 -> 仍然通过
```

**步骤4: 添加更多测试**
```c
void test_calculate_average_with_null_pointer(void) {
    int avg = calculate_average(NULL, 3);
    TEST_ASSERT_EQUAL(0, avg);
}

void test_calculate_average_with_zero_count(void) {
    int values[] = {10, 20, 30};
    int avg = calculate_average(values, 0);
    TEST_ASSERT_EQUAL(0, avg);
}

void test_calculate_average_with_negative_numbers(void) {
    int values[] = {-10, -20, -30};
    int avg = calculate_average(values, 3);
    TEST_ASSERT_EQUAL(-20, avg);
}
```

### 8.5 性能测试

**测量执行时间**:
```c
#include <time.h>

void test_performance_of_sort(void) {
    int data[1000];
    // 初始化数据...
    
    clock_t start = clock();
    
    // 执行被测试的函数
    sort_array(data, 1000);
    
    clock_t end = clock();
    double duration = (double)(end - start) / CLOCKS_PER_SEC;
    
    // 验证性能要求
    TEST_ASSERT_TRUE(duration < 0.001);  // 应该在1ms内完成
}
```

**嵌入式系统性能测试**:
```c
// 使用硬件定时器
void test_performance_embedded(void) {
    uint32_t start = get_tick_count();
    
    // 执行函数
    process_data();
    
    uint32_t end = get_tick_count();
    uint32_t duration_us = (end - start);
    
    // 验证实时性要求
    TEST_ASSERT_TRUE(duration_us < 100);  // 应该在100us内完成
}
```

### 8.6 内存测试

**检测内存泄漏**:
```c
void test_no_memory_leak(void) {
    size_t initial_free = get_free_heap_size();
    
    // 执行可能泄漏内存的操作
    for (int i = 0; i < 100; i++) {
        create_and_destroy_object();
    }
    
    size_t final_free = get_free_heap_size();
    
    // 验证内存没有泄漏
    TEST_ASSERT_EQUAL(initial_free, final_free);
}
```

**检测缓冲区溢出**:
```c
void test_no_buffer_overflow(void) {
    char buffer[10];
    
    // 设置保护字节
    buffer[9] = 0xAA;
    
    // 执行可能溢出的操作
    safe_strcpy(buffer, "test", 9);
    
    // 验证保护字节未被修改
    TEST_ASSERT_EQUAL(0xAA, buffer[9]);
}
```


## 故障排除

### 问题1: 链接错误 - 未定义的引用

**现象**:
```
undefined reference to `GPIO_SetPin'
```

**原因**:
- Mock文件未被编译
- 链接顺序错误
- 缺少库文件

**解决方法**:

**方法1: 检查Makefile**
```makefile
# 确保Mock文件被包含
MOCK_FILES = $(wildcard $(TEST_DIR)/mock_*.c)
MOCK_OBJS = $(patsubst $(TEST_DIR)/%.c,$(BUILD_DIR)/%.o,$(MOCK_FILES))

# 链接时包含Mock对象
$(TEST_EXEC): $(SRC_OBJS) $(TEST_OBJS) $(MOCK_OBJS) $(UNITY_OBJ)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)
```

**方法2: 使用弱符号**
```c
// 在源文件中使用弱符号
__attribute__((weak)) void GPIO_SetPin(uint8_t pin, uint8_t value) {
    // 默认实现（什么都不做）
}

// 测试时提供强符号覆盖
void GPIO_SetPin(uint8_t pin, uint8_t value) {
    // Mock实现
}
```

### 问题2: 测试在目标硬件上运行失败

**现象**:
- PC上测试通过
- 目标硬件上失败

**原因**:
- 字节序不同
- 数据类型大小不同
- 浮点运算精度不同
- 内存对齐问题

**解决方法**:

**使用固定大小类型**:
```c
// 避免
int value;      // 大小可能不同
long counter;   // 大小可能不同

// 推荐
int32_t value;
uint32_t counter;
```

**处理字节序**:
```c
// 测试时考虑字节序
void test_endianness_safe(void) {
    uint32_t value = 0x12345678;
    uint8_t *bytes = (uint8_t *)&value;
    
    #if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
        TEST_ASSERT_EQUAL(0x78, bytes[0]);
    #else
        TEST_ASSERT_EQUAL(0x12, bytes[0]);
    #endif
}
```

**浮点比较**:
```c
// 避免直接比较
TEST_ASSERT_EQUAL(1.0, calculate());  // 可能失败

// 使用容差
TEST_ASSERT_FLOAT_WITHIN(0.001, 1.0, calculate());
```

### 问题3: 测试运行很慢

**现象**:
- 测试套件需要几分钟才能完成
- 影响开发效率

**原因**:
- 测试不是真正的单元测试
- 包含了集成测试
- 使用了真实的延迟

**解决方法**:

**移除延迟**:
```c
// 不好：包含真实延迟
void test_with_delay(void) {
    start_operation();
    delay_ms(1000);  // 等待1秒！
    int result = get_result();
    TEST_ASSERT_EQUAL(EXPECTED, result);
}

// 好：使用Mock
void test_without_delay(void) {
    start_operation();
    // Mock时间流逝
    mock_advance_time(1000);
    int result = get_result();
    TEST_ASSERT_EQUAL(EXPECTED, result);
}
```

**分离单元测试和集成测试**:
```makefile
# 快速单元测试
test-unit: $(TEST_EXEC)
	./$(TEST_EXEC) --filter=unit

# 慢速集成测试
test-integration: $(TEST_EXEC)
	./$(TEST_EXEC) --filter=integration

# 所有测试
test-all: test-unit test-integration
```

### 问题4: Mock验证失败

**现象**:
```
Expected GPIO_SetPin to be called with (1, 1) but was called with (1, 0)
```

**原因**:
- 参数不匹配
- 调用次数不对
- 调用顺序错误

**解决方法**:

**检查参数**:
```c
// 调试Mock调用
void test_debug_mock(void) {
    // 启用详细输出
    mock_gpio_set_verbose(true);
    
    LED_SetState(LED_RED, LED_ON);
    
    // 打印实际调用
    mock_gpio_print_calls();
}
```

**放宽验证**:
```c
// 严格验证
GPIO_SetPin_Expect(LED_RED, LED_ON);

// 只验证被调用，不管参数
GPIO_SetPin_IgnoreAndReturn(0);

// 只验证某些参数
GPIO_SetPin_Expect(LED_RED, LED_ON);
GPIO_SetPin_IgnoreArg_value();  // 忽略value参数
```

### 问题5: 覆盖率数据不准确

**现象**:
- 覆盖率显示0%
- 覆盖率数据缺失

**原因**:
- 未使用覆盖率标志编译
- .gcda文件未生成
- 路径问题

**解决方法**:

**检查编译标志**:
```bash
# 查看编译命令
make -n test

# 应该看到 --coverage 或 -fprofile-arcs -ftest-coverage
```

**清理旧数据**:
```bash
# 删除旧的覆盖率数据
find . -name "*.gcda" -delete
find . -name "*.gcno" -delete

# 重新编译和测试
make clean
make test
./build/test_runner
```

**检查路径**:
```bash
# 确保在正确的目录运行
cd project_root
./build/test_runner

# 生成覆盖率时使用正确的路径
lcov --capture --directory build --output-file coverage.info
```

## 最佳实践总结

### 测试编写原则

1. **测试应该快速**
   - 单元测试应该在毫秒级完成
   - 整个测试套件应该在几秒内完成
   - 使用Mock替代慢速操作

2. **测试应该独立**
   - 每个测试独立运行
   - 不依赖其他测试
   - 不依赖执行顺序

3. **测试应该可重复**
   - 每次运行结果一致
   - 不依赖外部状态
   - 不依赖时间或随机数

4. **测试应该清晰**
   - 使用描述性名称
   - 遵循AAA模式
   - 一个测试一个断言（理想情况）

5. **测试应该全面**
   - 测试正常情况
   - 测试边界条件
   - 测试错误情况

### 项目组织

1. **目录结构**
```
project/
├── src/              # 源代码
├── include/          # 头文件
├── test/             # 测试代码
│   ├── Unity/       # 测试框架
│   ├── mocks/       # Mock文件
│   └── test_*.c     # 测试用例
├── build/            # 构建输出
└── docs/             # 文档
```

2. **命名约定**
   - 测试文件：`test_<module>.c`
   - Mock文件：`mock_<module>.c`
   - 测试函数：`test_<function>_<scenario>_<expected>`

3. **文档**
   - README说明如何运行测试
   - 测试覆盖率报告
   - CI/CD配置文档

### 团队协作

1. **代码审查**
   - 审查测试代码
   - 检查测试覆盖率
   - 验证测试质量

2. **持续集成**
   - 每次提交运行测试
   - 自动生成覆盖率报告
   - 测试失败阻止合并

3. **测试文化**
   - 先写测试再写代码（TDD）
   - 修复Bug时先写测试
   - 重构时保持测试通过

## 总结

通过本教程，你已经学习了:

- ✅ 单元测试的基本概念和重要性
- ✅ 选择和使用Unity/CppUTest测试框架
- ✅ 搭建完整的测试环境
- ✅ 编写高质量的测试用例
- ✅ 使用Mock和Stub技术
- ✅ 分析和提高代码覆盖率
- ✅ 集成测试到CI/CD流程
- ✅ 应用高级测试技术

**关键要点**:
1. 单元测试是保证代码质量的基础
2. 选择适合项目的测试框架
3. Mock技术使嵌入式代码可测试
4. 覆盖率是工具，不是目标
5. CI/CD自动化测试流程
6. 测试驱动开发提高代码质量

**实践建议**:
- 从小项目开始实践
- 逐步建立测试习惯
- 持续改进测试质量
- 分享经验和最佳实践
- 保持测试代码的可维护性

## 下一步学习

建议继续学习以下内容:

### 相关主题
- [硬件在环(HIL)测试系统](./02-hil-testing-system.html) - 系统级测试
- [代码静态分析工具使用](../../01-development-tools/intermediate/04-static-analysis.html) - 代码质量
- [持续集成CI/CD实践](../../01-development-tools/intermediate/03-cicd-practice.html) - 自动化流程

### 进阶主题
- 集成测试策略
- 系统测试方法
- 性能测试和基准测试
- 安全测试
- 模糊测试（Fuzzing）

## 参考资料

### 测试框架文档
1. [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
2. [CppUTest](https://cpputest.github.io/)
3. [CMock](https://github.com/ThrowTheSwitch/CMock)
4. [Google Test](https://github.com/google/googletest)

### 推荐书籍
1. "Test Driven Development for Embedded C" - James W. Grenning
2. "Embedded Software Development for Safety-Critical Systems" - Chris Hobbs
3. "Working Effectively with Legacy Code" - Michael Feathers
4. "xUnit Test Patterns" - Gerard Meszaros

### 在线资源
1. [Embedded Artistry - Testing](https://embeddedartistry.com/fieldatlas/testing/)
2. [Interrupt - Unit Testing](https://interrupt.memfault.com/blog/unit-testing-basics)
3. [Martin Fowler - Testing](https://martinfowler.com/testing/)

### 工具和库
1. [gcov/lcov](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html) - 覆盖率工具
2. [Ceedling](http://www.throwtheswitch.org/ceedling) - 测试构建工具
3. [Codecov](https://codecov.io/) - 覆盖率报告服务
4. [SonarQube](https://www.sonarqube.org/) - 代码质量平台

---

**练习项目**:

尝试为一个实际的嵌入式模块建立完整的测试体系：
1. 选择一个模块（如UART驱动、状态机等）
2. 设计测试用例
3. 实现Mock依赖
4. 达到80%以上覆盖率
5. 集成到CI/CD
6. 编写测试文档

祝你在嵌入式单元测试的道路上越走越远！
