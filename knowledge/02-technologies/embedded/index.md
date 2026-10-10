# 嵌入式系统开发

欢迎来到嵌入式系统开发知识库！本知识库按照嵌入式系统的层次架构组织，涵盖从硬件到云端的完整技术栈。

## 📚 知识体系结构

### 1. 硬件层 (Hardware Layer)
- [芯片架构](01-hardware-layer/01-chip-architecture/) - ARM、RISC-V、AVR等处理器架构
- [硬件设计基础](01-hardware-layer/02-hardware-design-fundamentals/) - 电路设计、PCB设计
- [电源管理](01-hardware-layer/03-power-management/) - 低功耗设计、电源方案
- [传感器技术](01-hardware-layer/04-sensor-technology/) - 各类传感器应用
- [执行器控制](01-hardware-layer/05-actuator-control/) - 电机、舵机控制
- [通信接口硬件](01-hardware-layer/06-communication-interface-hardware/) - UART、SPI、I2C等

### 2. 驱动与BSP层 (Driver & BSP Layer)
- [Bootloader开发](02-driver-bsp-layer/01-bootloader-development/) - 引导程序、固件升级
- [设备驱动开发](02-driver-bsp-layer/02-device-driver-development/) - 外设驱动编写
- [内存管理](02-driver-bsp-layer/03-memory-management/) - 内存分配、优化
- [中断与异常处理](02-driver-bsp-layer/04-interrupt-exception-handling/) - 中断机制
- [时钟与定时器管理](02-driver-bsp-layer/05-clock-timer-management/) - 时钟配置
- [设备树与BSP](02-driver-bsp-layer/06-device-tree-bsp/) - 设备树、板级支持包

### 3. 操作系统层 (Operating System Layer)
- [裸机编程](03-operating-system-layer/01-bare-metal-programming/) - 无操作系统开发
- [RTOS基础](03-operating-system-layer/02-rtos-fundamentals/) - 实时操作系统原理
- [FreeRTOS](03-operating-system-layer/03-freertos/) - FreeRTOS应用开发
- [RT-Thread](03-operating-system-layer/04-rt-thread/) - RT-Thread应用开发
- [嵌入式Linux](03-operating-system-layer/05-embedded-linux/) - Linux系统开发
- [Android系统](03-operating-system-layer/06-android-system/) - Android底层开发

### 4. 中间件层 (Middleware Layer)
- [文件系统](04-middleware-layer/01-file-systems/) - FAT、LittleFS等
- [存储技术](04-middleware-layer/02-storage-technology/) - Flash、EEPROM管理
- [图形显示](04-middleware-layer/03-graphics-display/) - GUI、LVGL
- [多媒体处理](04-middleware-layer/04-multimedia-processing/) - 音视频处理
- [安全加密](04-middleware-layer/05-security-encryption/) - 加密算法、安全启动
- [数据库与数据管理](04-middleware-layer/06-database-data-management/) - 嵌入式数据库

### 5. 应用层 (Application Layer)
- [嵌入式AI/ML](05-application-layer/01-embedded-ai-ml/) - 边缘计算、TinyML
- [用户界面开发](05-application-layer/02-user-interface-development/) - 交互设计
- [应用框架](05-application-layer/03-application-frameworks/) - 软件架构
- [OTA与远程管理](05-application-layer/04-ota-remote-management/) - 远程升级

### 6. 通信与网络 (Communication & Networking)
- [无线通信](06-communication-networking/01-wireless-communication/) - WiFi、BLE、LoRa
- [网络协议](06-communication-networking/02-network-protocols/) - TCP/IP、MQTT
- [物联网云平台集成](06-communication-networking/03-iot-cloud-integration/) - AWS IoT、阿里云

### 7. 云端后台 (Cloud Backend)
- [后端开发](07-cloud-backend/01-backend-development/) - RESTful API、微服务
- [云服务](07-cloud-backend/02-cloud-services/) - Docker、Kubernetes
- [数据分析与可视化](07-cloud-backend/03-data-analysis-visualization/) - 数据处理

### 8. 工具链 (Toolchain)
- [开发工具](08-toolchain/01-development-tools/) - IDE、编译器
- [调试与测试](08-toolchain/02-debugging-testing/) - JTAG、单元测试
- [性能优化](08-toolchain/03-performance-optimization/) - 代码优化
- [CI/CD与DevOps](08-toolchain/04-cicd-devops/) - 持续集成

### 9. 行业领域 (Industry Domains)
- [汽车电子](09-industry-domains/01-automotive-electronics/) - AUTOSAR、CAN
- [工业自动化](09-industry-domains/02-industrial-automation/) - PLC、SCADA
- [医疗设备](09-industry-domains/03-medical-devices/) - 医疗标准
- [消费电子](09-industry-domains/04-consumer-electronics/) - 智能家居
- [航空航天与国防](09-industry-domains/05-aerospace-defense/) - 航空电子

### 10. 横切关注点 (Cross-cutting Concerns)
- [编程语言](10-cross-cutting-concerns/01-programming-languages/) - C/C++、Rust
- [软件架构与设计模式](10-cross-cutting-concerns/02-software-architecture-design-patterns/) - 架构设计
- [安全与可靠性](10-cross-cutting-concerns/03-security-reliability/) - 功能安全
- [项目管理与职业发展](10-cross-cutting-concerns/04-project-management-career/) - 项目管理

## 🎯 学习路径

### 初学者路径
1. 从硬件层的基础知识开始
2. 学习裸机编程
3. 掌握基本的驱动开发
4. 了解RTOS基础

### 进阶路径
1. 深入RTOS应用开发
2. 学习通信协议
3. 掌握中间件技术
4. 了解行业应用

### 高级路径
1. 系统架构设计
2. 性能优化
3. 安全与可靠性
4. 云端集成

## 📖 使用说明

每个主题都包含三个难度级别：
- **beginner** - 入门级教程
- **intermediate** - 中级进阶
- **advanced** - 高级实战

建议按照难度循序渐进学习，每个主题都配有实践项目和代码示例。

## 🔗 相关资源

- 项目实践 - 完整的项目案例
- 技术洞察 - 技术趋势和最佳实践
- 基础知识 - 计算机基础知识

---

*持续更新中，欢迎贡献内容！*
