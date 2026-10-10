---
title: "C++11/14/17新特性应用实践"
description: "深入学习现代C++的核心特性，包括智能指针、Lambda表达式、移动语义、constexpr和类型推导，掌握在嵌入式系统中高效使用现代C++的方法"
slug: "modern-cpp-features"

# 分类信息
domain: "横切关注点"
module: "编程语言"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - C++
  - 现代C++
  - 智能指针
  - Lambda表达式
  - 移动语义
  - constexpr
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 85
difficulty_score: 4

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
status: "draft"
is_featured: false
is_premium: false

# SEO和元数据
keywords:
  - C++11
  - C++14
  - C++17
  - 智能指针
  - Lambda
  - 移动语义
  - 现代C++特性
cover_image: ""
---

# C++11/14/17新特性应用实践


## 学习目标

完成本教程后，你将能够：

- 使用智能指针管理动态内存，避免内存泄漏
- 编写Lambda表达式实现回调和函数式编程
- 理解并应用移动语义优化性能
- 使用constexpr进行编译期计算
- 掌握auto和decltype进行类型推导
- 在嵌入式项目中合理使用现代C++特性

## 前置要求

### 知识要求
- 熟悉C++基础语法
- 理解指针和引用
- 了解面向对象编程概念
- 具备基本的嵌入式开发经验

### 环境要求
- 支持C++11/14/17的编译器（GCC 7+, Clang 5+, ARM Compiler 6+）
- 嵌入式开发板（可选，用于实际测试）
- IDE或文本编辑器

## 准备工作

### 编译器配置

确保你的编译器支持C++11/14/17标准：

```bash
# GCC编译器
g++ -std=c++17 -o program program.cpp

# ARM编译器
armclang --target=arm-arm-none-eabi -std=c++17 -c program.cpp
```

### 项目设置

创建测试项目结构：

```
modern-cpp-demo/
├── src/
│   ├── main.cpp
│   ├── smart_ptr_demo.cpp
│   ├── lambda_demo.cpp
│   └── move_semantics_demo.cpp
├── include/
│   └── demos.h
└── CMakeLists.txt
```


## 步骤1：智能指针 - 自动内存管理

### 1.1 理解智能指针

智能指针是C++11引入的自动内存管理工具，通过RAII（Resource Acquisition Is Initialization）机制自动管理动态内存。

**三种智能指针**：
- `std::unique_ptr`：独占所有权
- `std::shared_ptr`：共享所有权
- `std::weak_ptr`：弱引用，配合shared_ptr使用

### 1.2 unique_ptr - 独占所有权

`unique_ptr`保证同一时刻只有一个指针拥有对象，适合大多数场景。

```cpp
#include <memory>
#include <iostream>

// 传感器数据结构
struct SensorData {
    uint32_t timestamp;
    float temperature;
    float humidity;
    
    SensorData(uint32_t ts, float temp, float hum)
        : timestamp(ts), temperature(temp), humidity(hum) {
        std::cout << "SensorData created\n";
    }
    
    ~SensorData() {
        std::cout << "SensorData destroyed\n";
    }
};

// 使用unique_ptr管理传感器数据
void process_sensor_data() {
    // 创建unique_ptr
    std::unique_ptr<SensorData> data = 
        std::make_unique<SensorData>(1000, 25.5f, 60.0f);
    
    // 访问成员
    std::cout << "Temperature: " << data->temperature << "°C\n";
    
    // 转移所有权
    std::unique_ptr<SensorData> data2 = std::move(data);
    // data现在为nullptr
    
    if (!data) {
        std::cout << "data is now null\n";
    }
    
    // data2离开作用域时自动释放内存
}

int main() {
    process_sensor_data();
    return 0;
}
```

**代码说明**：
- `std::make_unique`：推荐的创建方式，异常安全
- `std::move`：转移所有权，原指针变为nullptr
- 离开作用域自动调用析构函数

**预期输出**：
```
SensorData created
Temperature: 25.5°C
data is now null
SensorData destroyed
```


### 1.3 shared_ptr - 共享所有权

`shared_ptr`使用引用计数管理对象，多个指针可以共享同一对象。

```cpp
#include <memory>
#include <iostream>
#include <vector>

// 设备驱动类
class DeviceDriver {
public:
    DeviceDriver(const std::string& name) : name_(name) {
        std::cout << "Driver " << name_ << " created\n";
    }
    
    ~DeviceDriver() {
        std::cout << "Driver " << name_ << " destroyed\n";
    }
    
    void operate() {
        std::cout << "Driver " << name_ << " operating\n";
    }
    
private:
    std::string name_;
};

// 多个模块共享同一个驱动
void shared_driver_example() {
    // 创建shared_ptr
    std::shared_ptr<DeviceDriver> driver = 
        std::make_shared<DeviceDriver>("UART1");
    
    std::cout << "Reference count: " << driver.use_count() << "\n";
    
    // 多个模块共享驱动
    std::vector<std::shared_ptr<DeviceDriver>> modules;
    modules.push_back(driver);  // 引用计数+1
    modules.push_back(driver);  // 引用计数+1
    
    std::cout << "Reference count: " << driver.use_count() << "\n";
    
    driver->operate();
    
    // 清空vector，引用计数-2
    modules.clear();
    std::cout << "Reference count: " << driver.use_count() << "\n";
    
    // driver离开作用域，引用计数归零，对象被销毁
}

int main() {
    shared_driver_example();
    return 0;
}
```

**预期输出**：
```
Driver UART1 created
Reference count: 1
Reference count: 3
Driver UART1 operating
Reference count: 1
Driver UART1 destroyed
```

### 1.4 weak_ptr - 打破循环引用

`weak_ptr`不增加引用计数，用于打破`shared_ptr`的循环引用。

```cpp
#include <memory>
#include <iostream>

// 观察者模式示例
class Subject;

class Observer {
public:
    Observer(const std::string& name) : name_(name) {}
    
    void set_subject(std::shared_ptr<Subject> subject) {
        subject_ = subject;  // 使用weak_ptr避免循环引用
    }
    
    void notify() {
        // 使用lock()获取shared_ptr
        if (auto subject = subject_.lock()) {
            std::cout << name_ << " notified by subject\n";
        } else {
            std::cout << name_ << ": subject no longer exists\n";
        }
    }
    
private:
    std::string name_;
    std::weak_ptr<Subject> subject_;  // 弱引用
};

class Subject {
public:
    void add_observer(std::shared_ptr<Observer> observer) {
        observers_.push_back(observer);
    }
    
    void notify_all() {
        for (auto& obs : observers_) {
            obs->notify();
        }
    }
    
private:
    std::vector<std::shared_ptr<Observer>> observers_;
};

int main() {
    auto subject = std::make_shared<Subject>();
    auto observer1 = std::make_shared<Observer>("Observer1");
    auto observer2 = std::make_shared<Observer>("Observer2");
    
    observer1->set_subject(subject);
    observer2->set_subject(subject);
    
    subject->add_observer(observer1);
    subject->add_observer(observer2);
    
    subject->notify_all();
    
    return 0;
}
```

**关键点**：
- `weak_ptr`不增加引用计数
- 使用`lock()`获取`shared_ptr`
- 检查对象是否仍然存在


## 步骤2：Lambda表达式 - 匿名函数

### 2.1 Lambda基础语法

Lambda表达式提供了一种简洁的方式定义匿名函数，特别适合回调和算法。

**基本语法**：
```cpp
[capture](parameters) -> return_type { body }
```

### 2.2 简单Lambda示例

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

void lambda_basics() {
    // 最简单的Lambda
    auto hello = []() {
        std::cout << "Hello from Lambda!\n";
    };
    hello();
    
    // 带参数的Lambda
    auto add = [](int a, int b) {
        return a + b;
    };
    std::cout << "Sum: " << add(5, 3) << "\n";
    
    // 显式指定返回类型
    auto divide = [](double a, double b) -> double {
        return (b != 0) ? a / b : 0.0;
    };
    std::cout << "Division: " << divide(10.0, 3.0) << "\n";
}

int main() {
    lambda_basics();
    return 0;
}
```

**预期输出**：
```
Hello from Lambda!
Sum: 8
Division: 3.33333
```

### 2.3 捕获外部变量

Lambda可以捕获外部作用域的变量，有多种捕获方式。

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

void capture_examples() {
    int threshold = 50;
    int count = 0;
    
    std::vector<int> sensor_values = {30, 60, 45, 70, 55, 40};
    
    // [=] 值捕获：捕获所有外部变量的副本
    auto count_above_threshold = [=]() {
        int local_count = 0;
        for (int val : sensor_values) {
            if (val > threshold) {
                local_count++;
            }
        }
        return local_count;
    };
    
    std::cout << "Values above threshold: " 
              << count_above_threshold() << "\n";
    
    // [&] 引用捕获：捕获所有外部变量的引用
    auto increment_count = [&]() {
        for (int val : sensor_values) {
            if (val > threshold) {
                count++;  // 可以修改外部变量
            }
        }
    };
    
    increment_count();
    std::cout << "Count: " << count << "\n";
    
    // [threshold, &count] 混合捕获
    auto mixed_capture = [threshold, &count](int value) {
        if (value > threshold) {
            count++;
            return true;
        }
        return false;
    };
    
    // [this] 捕获this指针（在类成员函数中）
    // [=, &count] 默认值捕获，count引用捕获
    // [&, threshold] 默认引用捕获，threshold值捕获
}

int main() {
    capture_examples();
    return 0;
}
```

**捕获方式总结**：
- `[]`：不捕获任何变量
- `[=]`：值捕获所有变量
- `[&]`：引用捕获所有变量
- `[var]`：值捕获特定变量
- `[&var]`：引用捕获特定变量
- `[this]`：捕获this指针


### 2.4 Lambda在嵌入式中的应用

Lambda表达式在嵌入式系统中特别适合事件处理和回调。

```cpp
#include <iostream>
#include <functional>
#include <vector>
#include <cstdint>

// 事件管理器
class EventManager {
public:
    using EventCallback = std::function<void(uint32_t)>;
    
    void register_event(uint32_t event_id, EventCallback callback) {
        callbacks_[event_id] = callback;
    }
    
    void trigger_event(uint32_t event_id, uint32_t data) {
        auto it = callbacks_.find(event_id);
        if (it != callbacks_.end()) {
            it->second(data);  // 调用回调
        }
    }
    
private:
    std::map<uint32_t, EventCallback> callbacks_;
};

// 使用Lambda注册事件处理
void event_handling_example() {
    EventManager event_mgr;
    
    // 按钮事件处理
    event_mgr.register_event(1, [](uint32_t data) {
        std::cout << "Button pressed: " << data << "\n";
    });
    
    // 定时器事件处理
    uint32_t timer_count = 0;
    event_mgr.register_event(2, [&timer_count](uint32_t data) {
        timer_count++;
        std::cout << "Timer tick: " << timer_count << "\n";
    });
    
    // 传感器数据处理
    float temperature_sum = 0.0f;
    int sample_count = 0;
    event_mgr.register_event(3, [&](uint32_t data) {
        float temp = static_cast<float>(data) / 10.0f;
        temperature_sum += temp;
        sample_count++;
        float avg = temperature_sum / sample_count;
        std::cout << "Temperature: " << temp 
                  << "°C, Average: " << avg << "°C\n";
    });
    
    // 触发事件
    event_mgr.trigger_event(1, 100);
    event_mgr.trigger_event(2, 0);
    event_mgr.trigger_event(3, 255);  // 25.5°C
    event_mgr.trigger_event(3, 280);  // 28.0°C
}

int main() {
    event_handling_example();
    return 0;
}
```

**预期输出**：
```
Button pressed: 100
Timer tick: 1
Temperature: 25.5°C, Average: 25.5°C
Temperature: 28°C, Average: 26.75°C
```

**应用场景**：
- 中断服务程序回调
- 定时器事件处理
- 传感器数据处理
- 状态机转换动作


## 步骤3：移动语义 - 性能优化

### 3.1 理解移动语义

移动语义允许资源从一个对象"移动"到另一个对象，避免不必要的拷贝，提高性能。

**核心概念**：
- 右值引用：`T&&`
- 移动构造函数
- 移动赋值运算符
- `std::move`：将左值转换为右值

### 3.2 移动构造和移动赋值

```cpp
#include <iostream>
#include <cstring>
#include <utility>

// 缓冲区类，演示移动语义
class Buffer {
public:
    // 构造函数
    Buffer(size_t size) : size_(size), data_(new uint8_t[size]) {
        std::cout << "Constructor: allocated " << size_ << " bytes\n";
    }
    
    // 拷贝构造函数
    Buffer(const Buffer& other) : size_(other.size_), 
                                   data_(new uint8_t[other.size_]) {
        std::memcpy(data_, other.data_, size_);
        std::cout << "Copy constructor: copied " << size_ << " bytes\n";
    }
    
    // 移动构造函数
    Buffer(Buffer&& other) noexcept 
        : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;
        std::cout << "Move constructor: moved " << size_ << " bytes\n";
    }
    
    // 拷贝赋值运算符
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new uint8_t[size_];
            std::memcpy(data_, other.data_, size_);
            std::cout << "Copy assignment: copied " << size_ << " bytes\n";
        }
        return *this;
    }
    
    // 移动赋值运算符
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = other.data_;
            other.size_ = 0;
            other.data_ = nullptr;
            std::cout << "Move assignment: moved " << size_ << " bytes\n";
        }
        return *this;
    }
    
    // 析构函数
    ~Buffer() {
        if (data_) {
            std::cout << "Destructor: freed " << size_ << " bytes\n";
        }
        delete[] data_;
    }
    
    size_t size() const { return size_; }
    
private:
    size_t size_;
    uint8_t* data_;
};

void move_semantics_demo() {
    std::cout << "=== Creating buffer1 ===\n";
    Buffer buffer1(1024);
    
    std::cout << "\n=== Copy construction ===\n";
    Buffer buffer2 = buffer1;  // 拷贝构造
    
    std::cout << "\n=== Move construction ===\n";
    Buffer buffer3 = std::move(buffer1);  // 移动构造
    // buffer1现在处于有效但未定义的状态
    
    std::cout << "\n=== Move assignment ===\n";
    Buffer buffer4(512);
    buffer4 = std::move(buffer2);  // 移动赋值
    
    std::cout << "\n=== End of scope ===\n";
}

int main() {
    move_semantics_demo();
    return 0;
}
```

**预期输出**：
```
=== Creating buffer1 ===
Constructor: allocated 1024 bytes

=== Copy construction ===
Copy constructor: copied 1024 bytes

=== Move construction ===
Move constructor: moved 1024 bytes

=== Move assignment ===
Constructor: allocated 512 bytes
Destructor: freed 512 bytes
Move assignment: moved 1024 bytes

=== End of scope ===
Destructor: freed 1024 bytes
Destructor: freed 1024 bytes
```

**关键点**：
- 移动构造/赋值应标记为`noexcept`
- 移动后的对象应处于有效状态
- 使用`std::move`显式触发移动


### 3.3 完美转发

完美转发允许函数模板将参数原封不动地转发给另一个函数。

```cpp
#include <iostream>
#include <utility>
#include <memory>

// 工厂函数，完美转发参数
template<typename T, typename... Args>
std::unique_ptr<T> make_device(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}

class Device {
public:
    Device(int id, const std::string& name) 
        : id_(id), name_(name) {
        std::cout << "Device created: " << name_ << "\n";
    }
    
    Device(Device&& other) noexcept 
        : id_(other.id_), name_(std::move(other.name_)) {
        std::cout << "Device moved\n";
    }
    
private:
    int id_;
    std::string name_;
};

int main() {
    // 完美转发参数到Device构造函数
    auto device1 = make_device<Device>(1, "Sensor");
    
    std::string name = "Actuator";
    auto device2 = make_device<Device>(2, name);
    
    return 0;
}
```

**关键点**：
- `std::forward`保持参数的值类别
- 用于实现通用工厂函数
- 避免不必要的拷贝

## 步骤4：constexpr - 编译期计算

### 4.1 constexpr函数

`constexpr`允许在编译期计算值，提高运行时性能。

```cpp
#include <iostream>
#include <array>

// constexpr函数：编译期计算
constexpr int factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

// constexpr函数：计算数组大小
constexpr size_t calculate_buffer_size(size_t base, size_t multiplier) {
    return base * multiplier;
}

// 编译期计算CRC表
constexpr uint32_t crc32_table_entry(uint8_t index) {
    uint32_t crc = index;
    for (int i = 0; i < 8; ++i) {
        crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
    }
    return crc;
}

// 生成CRC32查找表
template<size_t... Is>
constexpr auto make_crc_table_impl(std::index_sequence<Is...>) {
    return std::array<uint32_t, sizeof...(Is)>{crc32_table_entry(Is)...};
}

constexpr auto make_crc_table() {
    return make_crc_table_impl(std::make_index_sequence<256>{});
}

int main() {
    // 编译期计算
    constexpr int fact5 = factorial(5);
    std::cout << "5! = " << fact5 << "\n";
    
    // 编译期确定数组大小
    constexpr size_t buffer_size = calculate_buffer_size(32, 4);
    std::array<uint8_t, buffer_size> buffer;
    std::cout << "Buffer size: " << buffer.size() << "\n";
    
    // 编译期生成CRC表
    constexpr auto crc_table = make_crc_table();
    std::cout << "CRC table[0]: 0x" << std::hex << crc_table[0] << "\n";
    std::cout << "CRC table[255]: 0x" << crc_table[255] << "\n";
    
    return 0;
}
```

**预期输出**：
```
5! = 120
Buffer size: 128
CRC table[0]: 0x0
CRC table[255]: 0x2d02ef8d
```


### 4.2 constexpr if (C++17)

`constexpr if`允许在编译期进行条件判断，实现零开销的分支。

```cpp
#include <iostream>
#include <type_traits>

// 根据类型选择不同的处理方式
template<typename T>
void process_value(T value) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "Processing integer: " << value << "\n";
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "Processing float: " << value << "\n";
    } else {
        std::cout << "Processing other type\n";
    }
}

// 编译期配置选择
template<bool UseHardwareAcceleration>
class DataProcessor {
public:
    void process(const uint8_t* data, size_t size) {
        if constexpr (UseHardwareAcceleration) {
            // 使用硬件加速
            std::cout << "Using hardware acceleration\n";
            process_with_hardware(data, size);
        } else {
            // 使用软件实现
            std::cout << "Using software implementation\n";
            process_with_software(data, size);
        }
    }
    
private:
    void process_with_hardware(const uint8_t* data, size_t size) {
        // 硬件加速实现
    }
    
    void process_with_software(const uint8_t* data, size_t size) {
        // 软件实现
    }
};

int main() {
    process_value(42);
    process_value(3.14);
    process_value("Hello");
    
    DataProcessor<true> hw_processor;
    DataProcessor<false> sw_processor;
    
    uint8_t data[10] = {0};
    hw_processor.process(data, 10);
    sw_processor.process(data, 10);
    
    return 0;
}
```

**优势**：
- 编译期分支，零运行时开销
- 避免模板特化的复杂性
- 代码更清晰易读

## 步骤5：类型推导 - auto和decltype

### 5.1 auto类型推导

`auto`让编译器自动推导变量类型，简化代码。

```cpp
#include <iostream>
#include <vector>
#include <map>

void auto_examples() {
    // 基本类型推导
    auto i = 42;              // int
    auto d = 3.14;            // double
    auto s = "Hello";         // const char*
    
    // 容器迭代器
    std::vector<int> vec = {1, 2, 3, 4, 5};
    
    // 传统方式
    for (std::vector<int>::iterator it = vec.begin(); 
         it != vec.end(); ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";
    
    // 使用auto
    for (auto it = vec.begin(); it != vec.end(); ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";
    
    // 范围for循环
    for (auto value : vec) {
        std::cout << value << " ";
    }
    std::cout << "\n";
    
    // 复杂类型
    std::map<std::string, std::vector<int>> data_map;
    data_map["sensor1"] = {10, 20, 30};
    
    // 传统方式
    for (std::map<std::string, std::vector<int>>::iterator it = data_map.begin();
         it != data_map.end(); ++it) {
        std::cout << it->first << ": ";
        for (auto val : it->second) {
            std::cout << val << " ";
        }
        std::cout << "\n";
    }
    
    // 使用auto
    for (auto& pair : data_map) {
        std::cout << pair.first << ": ";
        for (auto val : pair.second) {
            std::cout << val << " ";
        }
        std::cout << "\n";
    }
}

int main() {
    auto_examples();
    return 0;
}
```


### 5.2 decltype类型推导

`decltype`推导表达式的类型，常用于模板编程。

```cpp
#include <iostream>
#include <vector>

// 使用decltype推导返回类型
template<typename T, typename U>
auto add(T t, U u) -> decltype(t + u) {
    return t + u;
}

// C++14简化版本
template<typename T, typename U>
auto multiply(T t, U u) {
    return t * u;
}

// decltype(auto) - 保持引用
template<typename Container, typename Index>
decltype(auto) get_element(Container& c, Index i) {
    return c[i];  // 返回引用
}

void decltype_examples() {
    // 推导变量类型
    int x = 10;
    decltype(x) y = 20;  // y的类型是int
    
    // 推导表达式类型
    decltype(x + y) z = x + y;  // z的类型是int
    
    // 使用auto推导返回类型
    auto result1 = add(10, 3.14);  // double
    std::cout << "add result: " << result1 << "\n";
    
    auto result2 = multiply(5, 2.5);  // double
    std::cout << "multiply result: " << result2 << "\n";
    
    // decltype(auto)保持引用
    std::vector<int> vec = {1, 2, 3, 4, 5};
    decltype(auto) elem = get_element(vec, 2);
    elem = 100;  // 修改vector中的元素
    std::cout << "vec[2] = " << vec[2] << "\n";
}

int main() {
    decltype_examples();
    return 0;
}
```

**使用场景**：
- 模板函数返回类型推导
- 保持表达式的值类别（左值/右值）
- 泛型编程

## 验证

### 编译和运行

编译所有示例代码：

```bash
# 编译智能指针示例
g++ -std=c++17 -o smart_ptr smart_ptr_demo.cpp

# 编译Lambda示例
g++ -std=c++17 -o lambda lambda_demo.cpp

# 编译移动语义示例
g++ -std=c++17 -o move move_semantics_demo.cpp

# 编译constexpr示例
g++ -std=c++17 -o constexpr constexpr_demo.cpp

# 编译类型推导示例
g++ -std=c++17 -o auto auto_demo.cpp
```

### 性能测试

测试移动语义的性能优势：

```cpp
#include <iostream>
#include <vector>
#include <chrono>

class LargeObject {
public:
    LargeObject() : data_(new int[1000000]) {}
    
    ~LargeObject() { delete[] data_; }
    
    // 拷贝构造
    LargeObject(const LargeObject& other) 
        : data_(new int[1000000]) {
        std::copy(other.data_, other.data_ + 1000000, data_);
    }
    
    // 移动构造
    LargeObject(LargeObject&& other) noexcept 
        : data_(other.data_) {
        other.data_ = nullptr;
    }
    
private:
    int* data_;
};

void test_copy() {
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<LargeObject> vec;
    for (int i = 0; i < 100; ++i) {
        LargeObject obj;
        vec.push_back(obj);  // 拷贝
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        end - start);
    std::cout << "Copy time: " << duration.count() << "ms\n";
}

void test_move() {
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<LargeObject> vec;
    for (int i = 0; i < 100; ++i) {
        LargeObject obj;
        vec.push_back(std::move(obj));  // 移动
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        end - start);
    std::cout << "Move time: " << duration.count() << "ms\n";
}

int main() {
    test_copy();
    test_move();
    return 0;
}
```

**预期结果**：移动操作应该明显快于拷贝操作。


## 故障排除

### 问题1：智能指针编译错误

**错误信息**：
```
error: 'make_unique' is not a member of 'std'
```

**原因**：`make_unique`是C++14引入的，需要C++14或更高版本。

**解决方案**：
```bash
# 使用C++14或C++17标准
g++ -std=c++14 -o program program.cpp
```

或者自己实现`make_unique`（C++11）：
```cpp
template<typename T, typename... Args>
std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

### 问题2：Lambda捕获导致的悬空引用

**错误场景**：
```cpp
std::function<void()> create_callback() {
    int local_var = 42;
    return [&local_var]() {  // 危险！捕获局部变量的引用
        std::cout << local_var << "\n";
    };
}  // local_var被销毁，Lambda持有悬空引用
```

**解决方案**：使用值捕获
```cpp
std::function<void()> create_callback() {
    int local_var = 42;
    return [local_var]() {  // 安全：值捕获
        std::cout << local_var << "\n";
    };
}
```

### 问题3：移动后使用对象

**错误场景**：
```cpp
Buffer buf1(1024);
Buffer buf2 = std::move(buf1);
buf1.size();  // 危险！buf1已被移动
```

**解决方案**：
- 不要使用已移动的对象
- 或者重新赋值
```cpp
Buffer buf1(1024);
Buffer buf2 = std::move(buf1);
buf1 = Buffer(512);  // 重新赋值
buf1.size();  // 现在安全了
```

### 问题4：constexpr函数限制

**C++11 constexpr限制**：
- 只能包含一个return语句
- 不能有循环

**C++14放宽限制**：
- 可以有多个语句
- 可以有循环和条件

**示例**：
```cpp
// C++11：只能单行
constexpr int factorial_cpp11(int n) {
    return (n <= 1) ? 1 : n * factorial_cpp11(n - 1);
}

// C++14：可以多行
constexpr int factorial_cpp14(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}
```

### 问题5：auto推导意外类型

**问题场景**：
```cpp
auto x = {1, 2, 3};  // x的类型是std::initializer_list<int>
```

**解决方案**：明确指定类型
```cpp
std::vector<int> x = {1, 2, 3};  // 明确类型
auto x = std::vector<int>{1, 2, 3};  // 或使用auto
```

## 总结

### 核心要点

本教程介绍了C++11/14/17的关键特性：

1. **智能指针**
   - `unique_ptr`：独占所有权，零开销
   - `shared_ptr`：共享所有权，引用计数
   - `weak_ptr`：打破循环引用
   - 使用`make_unique`/`make_shared`创建

2. **Lambda表达式**
   - 简洁的匿名函数语法
   - 灵活的捕获机制
   - 适合回调和事件处理
   - 配合`std::function`使用

3. **移动语义**
   - 避免不必要的拷贝
   - 提高性能
   - 实现移动构造和移动赋值
   - 使用`std::move`和`std::forward`

4. **constexpr**
   - 编译期计算
   - 零运行时开销
   - 生成查找表和常量
   - C++17的`constexpr if`

5. **类型推导**
   - `auto`简化代码
   - `decltype`推导表达式类型
   - `decltype(auto)`保持引用
   - 提高代码可维护性

### 嵌入式应用建议

在嵌入式系统中使用现代C++特性时，需要注意：

**推荐使用**：
- `unique_ptr`：零开销的内存管理
- Lambda：简洁的回调实现
- 移动语义：优化性能
- `constexpr`：编译期计算
- `auto`：简化代码

**谨慎使用**：
- `shared_ptr`：有引用计数开销
- 异常：可能增加代码大小
- RTTI：增加内存占用
- 虚函数：有虚表开销

**编译器支持**：
- GCC 7+：完整支持C++17
- Clang 5+：完整支持C++17
- ARM Compiler 6+：支持C++14/17
- IAR：部分支持C++11/14

### 性能考虑

现代C++特性的性能影响：

| 特性 | 性能影响 | 建议 |
|------|---------|------|
| unique_ptr | 零开销 | 推荐使用 |
| shared_ptr | 引用计数开销 | 必要时使用 |
| Lambda | 内联后零开销 | 推荐使用 |
| 移动语义 | 提高性能 | 推荐使用 |
| constexpr | 零运行时开销 | 推荐使用 |
| auto | 零开销 | 推荐使用 |


### 最佳实践

1. **优先使用智能指针**
   ```cpp
   // 好
   auto ptr = std::make_unique<Device>();
   
   // 避免
   Device* ptr = new Device();
   ```

2. **合理使用Lambda**
   ```cpp
   // 好：简短的回调
   event_mgr.register([](int data) {
       process(data);
   });
   
   // 避免：复杂逻辑应该使用函数
   ```

3. **显式使用std::move**
   ```cpp
   // 好：明确意图
   vec.push_back(std::move(obj));
   
   // 避免：隐式移动可能不清晰
   ```

4. **constexpr用于常量计算**
   ```cpp
   // 好：编译期计算
   constexpr int buffer_size = 1024 * 4;
   
   // 避免：运行时计算
   const int buffer_size = calculate_size();
   ```

5. **auto用于复杂类型**
   ```cpp
   // 好：简化代码
   auto it = map.find(key);
   
   // 避免：基本类型使用auto可能降低可读性
   auto x = 42;  // 不如 int x = 42; 清晰
   ```

## 下一步

### 继续学习

掌握这些现代C++特性后，建议继续学习：

1. **嵌入式C++最佳实践** - 在资源受限环境中使用C++
2. **C++模板编程** - 泛型编程和元编程
3. **C++并发编程** - 多线程和异步编程
4. **C++20新特性** - Concepts、Ranges、Coroutines

### 实践项目

通过实践巩固所学知识：

**项目1：智能设备管理器**
- 使用`unique_ptr`管理设备对象
- 使用Lambda实现事件回调
- 使用移动语义优化性能

**项目2：数据处理管道**
- 使用Lambda实现数据转换
- 使用`constexpr`生成查找表
- 使用移动语义传递大对象

**项目3：配置管理系统**
- 使用`shared_ptr`共享配置
- 使用`constexpr`验证配置
- 使用auto简化代码

## 延伸阅读

### 推荐书籍

- 《Effective Modern C++》- Scott Meyers
  - 42条使用C++11/14的最佳实践
  - 深入理解现代C++特性

- 《C++ Primer (第5版)》- Stanley B. Lippman
  - 全面介绍C++11/14特性
  - 适合系统学习

- 《C++17 STL Cookbook》- Jacek Galowicz
  - C++17实用技巧
  - 大量实例代码

### 在线资源

- [cppreference.com](https://en.cppreference.com/) - C++标准库参考
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) - C++核心指南
- [Compiler Explorer](https://godbolt.org/) - 在线查看编译结果
- [C++ Weekly](https://www.youtube.com/c/lefticus1) - C++视频教程

### 相关文章

- C++在嵌入式中的应用 - C++优势和应用场景
- 嵌入式C++最佳实践 - 资源管理和性能优化
- C++模板编程入门 - 泛型编程基础

## 参考资料

1. ISO/IEC 14882:2011 - C++11标准
2. ISO/IEC 14882:2014 - C++14标准
3. ISO/IEC 14882:2017 - C++17标准
4. Effective Modern C++ - Scott Meyers
5. C++ Core Guidelines - Bjarne Stroustrup & Herb Sutter

---

**练习题**：

1. 实现一个使用`unique_ptr`管理的缓冲池类
2. 使用Lambda表达式实现一个简单的任务调度器
3. 编写一个支持移动语义的字符串类
4. 使用`constexpr`实现编译期的位操作工具
5. 使用auto和decltype实现一个泛型容器包装器

**实践项目**：

设计一个现代C++的嵌入式框架，要求：
- 使用智能指针管理资源
- 使用Lambda实现事件系统
- 使用移动语义优化性能
- 使用constexpr进行编译期配置
- 使用auto简化代码

**下一步**：建议学习 [嵌入式C++最佳实践](03-embedded-cpp-best-practices.html)
