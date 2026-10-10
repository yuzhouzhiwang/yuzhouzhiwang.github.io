---
title: "Python在嵌入式开发中的应用"
description: "深入学习如何使用Python进行嵌入式开发，包括MicroPython、CircuitPython的使用，以及Python在测试自动化和上位机开发中的应用"
slug: "python-for-embedded-development"

# 分类信息
domain: "横切关注点"
module: "编程语言"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - Python
  - MicroPython
  - CircuitPython
  - 嵌入式开发
  - 脚本自动化
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 70
difficulty_score: 3

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-10"
updated_at: "2026-03-10"
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
  - Python嵌入式
  - MicroPython
  - CircuitPython
  - 测试自动化
  - 上位机开发
cover_image: ""
---

# Python在嵌入式开发中的应用

## 学习目标

完成本教程后，你将能够：

- [ ] 理解Python在嵌入式开发中的应用场景和优势
- [ ] 掌握MicroPython的基本使用方法
- [ ] 学会使用CircuitPython进行快速原型开发
- [ ] 使用Python编写测试脚本和自动化工具
- [ ] 开发基于Python的上位机应用程序


## 前置要求

在开始本教程之前，你需要：

**知识要求**：
- 掌握Python基础语法（变量、函数、类、模块）
- 了解基本的嵌入式系统概念
- 熟悉GPIO、I2C、SPI等基本外设接口

**技能要求**：
- 能够使用Python编写简单程序
- 会使用命令行工具
- 了解基本的电路连接

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考链接 |
|------|------|------|----------|
| ESP32开发板 | 1 | 支持MicroPython | [购买链接](https://example.com) |
| Adafruit Circuit Playground Express | 1 | 用于CircuitPython示例 | [购买链接](https://example.com) |
| LED灯 | 3 | 红、绿、蓝各一个 | - |
| 电阻 | 3 | 220Ω | - |
| 面包板 | 1 | - | - |
| USB数据线 | 2 | Type-C和Micro-USB | - |

### 软件准备

- **Python环境**：Python 3.8+ (用于上位机开发)
- **MicroPython固件**：ESP32 MicroPython固件
- **CircuitPython固件**：Circuit Playground Express固件
- **开发工具**：
  - Thonny IDE (推荐用于MicroPython)
  - Mu Editor (推荐用于CircuitPython)
  - VS Code + Python扩展
- **烧录工具**：esptool.py (用于ESP32)
- **串口工具**：PuTTY或screen

### 环境配置

#### 1. 安装Python和必要的库

```bash
# 安装Python (如果尚未安装)
# Windows: 从python.org下载安装包
# macOS: brew install python3
# Linux: sudo apt-get install python3 python3-pip

# 安装必要的Python库
pip install esptool adafruit-ampy pyserial
```

#### 2. 安装Thonny IDE

```bash
# Windows/macOS: 从thonny.org下载安装包
# Linux:
sudo apt-get install thonny
```

#### 3. 烧录MicroPython固件到ESP32

```bash
# 下载ESP32 MicroPython固件
# 从 micropython.org/download/esp32/ 下载最新固件

# 擦除Flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# 烧录固件
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```


## 步骤1：MicroPython基础入门

### 1.1 连接到MicroPython REPL

MicroPython提供了一个交互式的REPL (Read-Eval-Print Loop)环境，类似于标准Python的交互式解释器。

**使用串口工具连接**：

```bash
# Linux/macOS
screen /dev/ttyUSB0 115200

# 或使用PuTTY (Windows)
# 配置: 串口 COM3, 波特率 115200
```

**测试连接**：

```python
>>> print("Hello, MicroPython!")
Hello, MicroPython!

>>> import sys
>>> sys.implementation
(name='micropython', version=(1, 20, 0))
```

### 1.2 GPIO控制 - LED闪烁

让我们从最基本的LED控制开始：

```python
from machine import Pin
import time

# 配置GPIO2为输出模式（ESP32板载LED）
led = Pin(2, Pin.OUT)

# LED闪烁循环
while True:
    led.on()      # 点亮LED
    time.sleep(0.5)  # 延时500ms
    led.off()     # 熄灭LED
    time.sleep(0.5)
```

**代码说明**：
- `machine.Pin`: MicroPython的GPIO控制类
- `Pin.OUT`: 配置引脚为输出模式
- `led.on()` / `led.off()`: 控制LED状态
- `time.sleep()`: 延时函数，单位为秒

### 1.3 读取按键输入

```python
from machine import Pin
import time

# 配置GPIO0为输入模式，启用上拉电阻
button = Pin(0, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)

while True:
    if button.value() == 0:  # 按键按下（低电平）
        led.on()
        print("Button pressed!")
    else:
        led.off()
    time.sleep(0.1)  # 防抖延时
```

**预期结果**：
- 按下按键时LED点亮
- 释放按键时LED熄灭
- 串口输出"Button pressed!"


## 步骤2：MicroPython高级功能

### 2.1 PWM控制 - LED呼吸灯

使用PWM (脉宽调制) 实现LED亮度渐变效果：

```python
from machine import Pin, PWM
import time

# 创建PWM对象，频率1000Hz
led_pwm = PWM(Pin(2), freq=1000)

def breathing_led():
    """呼吸灯效果"""
    while True:
        # 逐渐变亮
        for duty in range(0, 1024, 10):
            led_pwm.duty(duty)
            time.sleep(0.01)
        
        # 逐渐变暗
        for duty in range(1023, -1, -10):
            led_pwm.duty(duty)
            time.sleep(0.01)

breathing_led()
```

**代码说明**：
- `PWM()`: 创建PWM对象
- `freq`: 设置PWM频率
- `duty()`: 设置占空比 (0-1023)
- 占空比越大，LED越亮

### 2.2 I2C通信 - 读取传感器

使用I2C接口读取温湿度传感器（以SHT31为例）：

```python
from machine import Pin, I2C
import time

# 初始化I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# 扫描I2C设备
devices = i2c.scan()
print("I2C devices found:", [hex(device) for device in devices])

# SHT31传感器地址
SHT31_ADDR = 0x44

def read_sht31():
    """读取SHT31温湿度数据"""
    # 发送测量命令
    i2c.writeto(SHT31_ADDR, b'\x2C\x06')
    time.sleep(0.5)  # 等待测量完成
    
    # 读取6字节数据
    data = i2c.readfrom(SHT31_ADDR, 6)
    
    # 解析温度数据
    temp_raw = (data[0] << 8) | data[1]
    temp = -45 + (175 * temp_raw / 65535.0)
    
    # 解析湿度数据
    hum_raw = (data[3] << 8) | data[4]
    humidity = 100 * hum_raw / 65535.0
    
    return temp, humidity

# 持续读取并显示
while True:
    temp, hum = read_sht31()
    print(f"Temperature: {temp:.2f}°C, Humidity: {hum:.2f}%")
    time.sleep(2)
```

### 2.3 WiFi连接和HTTP请求

MicroPython支持WiFi连接，可以实现物联网应用：

```python
import network
import urequests
import time

# 连接WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        
        # 等待连接
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    
    print('\nWiFi connected!')
    print('IP address:', wlan.ifconfig()[0])

# 发送HTTP GET请求
def get_weather(city):
    url = f"http://api.example.com/weather?city={city}"
    response = urequests.get(url)
    data = response.json()
    response.close()
    return data

# 使用示例
connect_wifi('your_ssid', 'your_password')
weather = get_weather('Beijing')
print(f"Weather: {weather['temp']}°C, {weather['description']}")
```


## 步骤3：CircuitPython快速开发

### 3.1 CircuitPython简介

CircuitPython是Adafruit基于MicroPython开发的Python变体，专注于教育和快速原型开发。

**CircuitPython的优势**：
- 即插即用，无需编译器
- 丰富的库支持
- 友好的错误提示
- 自动重载代码

### 3.2 第一个CircuitPython程序

将Circuit Playground Express连接到电脑，它会显示为一个USB驱动器。

创建 `code.py` 文件：

```python
import board
import digitalio
import time

# 配置板载LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# LED闪烁
while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```

**保存文件后，程序会自动运行！**

### 3.3 使用NeoPixel彩色LED

Circuit Playground Express板载10个NeoPixel RGB LED：

```python
import board
import neopixel
import time

# 初始化NeoPixel (10个LED)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.3)

# 定义颜色 (R, G, B)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

# 彩虹效果
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(10):
            pixel_index = (i * 256 // 10) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    """生成彩虹颜色"""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

# 运行彩虹效果
while True:
    rainbow_cycle(0.01)
```

### 3.4 读取加速度计和按键

```python
import board
import digitalio
import adafruit_lis3dh
import time

# 初始化加速度计
i2c = board.I2C()
accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

# 初始化按键
button_a = digitalio.DigitalInOut(board.BUTTON_A)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.DOWN

button_b = digitalio.DigitalInOut(board.BUTTON_B)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.DOWN

while True:
    # 读取加速度
    x, y, z = accelerometer.acceleration
    print(f"X: {x:.2f} Y: {y:.2f} Z: {z:.2f} m/s^2")
    
    # 检测按键
    if button_a.value:
        print("Button A pressed!")
    if button_b.value:
        print("Button B pressed!")
    
    time.sleep(0.1)
```


## 步骤4：Python测试自动化

### 4.1 串口通信测试脚本

使用Python编写自动化测试脚本，通过串口与嵌入式设备通信：

```python
import serial
import time

class EmbeddedTester:
    """嵌入式设备测试类"""
    
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # 等待连接稳定
    
    def send_command(self, cmd):
        """发送命令"""
        self.ser.write(f"{cmd}\r\n".encode())
        time.sleep(0.1)
    
    def read_response(self, timeout=1):
        """读取响应"""
        start_time = time.time()
        response = ""
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                response += self.ser.read(self.ser.in_waiting).decode()
            time.sleep(0.01)
        
        return response
    
    def test_led_control(self):
        """测试LED控制"""
        print("Testing LED control...")
        
        # 测试LED开
        self.send_command("LED ON")
        response = self.read_response()
        assert "LED: ON" in response, "LED ON command failed"
        print("✓ LED ON test passed")
        
        # 测试LED关
        self.send_command("LED OFF")
        response = self.read_response()
        assert "LED: OFF" in response, "LED OFF command failed"
        print("✓ LED OFF test passed")
    
    def test_sensor_reading(self):
        """测试传感器读取"""
        print("Testing sensor reading...")
        
        self.send_command("READ TEMP")
        response = self.read_response()
        
        # 解析温度值
        if "TEMP:" in response:
            temp_str = response.split("TEMP:")[1].strip()
            temp = float(temp_str)
            assert -40 < temp < 85, f"Temperature out of range: {temp}"
            print(f"✓ Temperature reading: {temp}°C")
        else:
            raise AssertionError("Failed to read temperature")
    
    def close(self):
        """关闭串口"""
        self.ser.close()

# 使用示例
if __name__ == "__main__":
    tester = EmbeddedTester('/dev/ttyUSB0')
    
    try:
        tester.test_led_control()
        tester.test_sensor_reading()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    finally:
        tester.close()
```

### 4.2 自动化固件烧录脚本

```python
import subprocess
import os
import sys

class FirmwareFlasher:
    """固件烧录工具"""
    
    def __init__(self, port, chip='esp32'):
        self.port = port
        self.chip = chip
    
    def erase_flash(self):
        """擦除Flash"""
        print("Erasing flash...")
        cmd = [
            'esptool.py',
            '--chip', self.chip,
            '--port', self.port,
            'erase_flash'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Flash erased successfully")
            return True
        else:
            print(f"✗ Flash erase failed: {result.stderr}")
            return False
    
    def flash_firmware(self, firmware_path):
        """烧录固件"""
        if not os.path.exists(firmware_path):
            print(f"✗ Firmware file not found: {firmware_path}")
            return False
        
        print(f"Flashing firmware: {firmware_path}")
        cmd = [
            'esptool.py',
            '--chip', self.chip,
            '--port', self.port,
            'write_flash',
            '-z', '0x1000',
            firmware_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Firmware flashed successfully")
            return True
        else:
            print(f"✗ Firmware flash failed: {result.stderr}")
            return False
    
    def verify_firmware(self):
        """验证固件"""
        print("Verifying firmware...")
        # 这里可以添加验证逻辑
        return True

# 使用示例
if __name__ == "__main__":
    flasher = FirmwareFlasher('/dev/ttyUSB0')
    
    if flasher.erase_flash():
        if flasher.flash_firmware('firmware.bin'):
            flasher.verify_firmware()
            print("\n✓ Firmware update completed!")
```


## 步骤5：Python上位机开发

### 5.1 使用Tkinter创建GUI监控工具

创建一个简单的串口监控工具：

```python
import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import threading
import time

class SerialMonitor:
    """串口监控GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("嵌入式设备监控工具")
        self.root.geometry("800x600")
        
        self.serial_port = None
        self.is_running = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 连接设置框架
        conn_frame = ttk.LabelFrame(self.root, text="连接设置", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(conn_frame, text="串口:").grid(row=0, column=0, padx=5)
        self.port_entry = ttk.Entry(conn_frame, width=20)
        self.port_entry.insert(0, "/dev/ttyUSB0")
        self.port_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="波特率:").grid(row=0, column=2, padx=5)
        self.baudrate_combo = ttk.Combobox(conn_frame, width=15,
                                           values=[9600, 115200, 230400])
        self.baudrate_combo.set(115200)
        self.baudrate_combo.grid(row=0, column=3, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="连接",
                                      command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=5)
        
        # 数据显示区域
        data_frame = ttk.LabelFrame(self.root, text="数据监控", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.data_text = scrolledtext.ScrolledText(data_frame, height=20)
        self.data_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮框架
        ctrl_frame = ttk.Frame(self.root, padding=10)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(ctrl_frame, text="清空", 
                  command=self.clear_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="LED开", 
                  command=lambda: self.send_command("LED ON")).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="LED关", 
                  command=lambda: self.send_command("LED OFF")).pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_label = ttk.Label(self.root, text="未连接", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_running:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """连接串口"""
        try:
            port = self.port_entry.get()
            baudrate = int(self.baudrate_combo.get())
            
            self.serial_port = serial.Serial(port, baudrate, timeout=0.1)
            self.is_running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            self.connect_btn.config(text="断开")
            self.status_label.config(text=f"已连接: {port} @ {baudrate}")
            self.append_text(f"[系统] 已连接到 {port}\n", "green")
            
        except Exception as e:
            self.append_text(f"[错误] 连接失败: {e}\n", "red")
    
    def disconnect(self):
        """断开连接"""
        self.is_running = False
        if self.serial_port:
            self.serial_port.close()
        
        self.connect_btn.config(text="连接")
        self.status_label.config(text="未连接")
        self.append_text("[系统] 已断开连接\n", "orange")
    
    def receive_data(self):
        """接收数据线程"""
        while self.is_running:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    self.append_text(text)
            except Exception as e:
                self.append_text(f"[错误] 接收数据失败: {e}\n", "red")
            time.sleep(0.01)
    
    def send_command(self, cmd):
        """发送命令"""
        if self.serial_port and self.is_running:
            try:
                self.serial_port.write(f"{cmd}\r\n".encode())
                self.append_text(f"[发送] {cmd}\n", "blue")
            except Exception as e:
                self.append_text(f"[错误] 发送失败: {e}\n", "red")
    
    def append_text(self, text, color="black"):
        """添加文本到显示区域"""
        self.data_text.insert(tk.END, text)
        self.data_text.see(tk.END)
    
    def clear_display(self):
        """清空显示"""
        self.data_text.delete(1.0, tk.END)

# 运行应用
if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
```


### 5.2 使用PyQt5创建专业级上位机

PyQt5提供更强大的GUI功能：

```python
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QComboBox, QLineEdit, QGroupBox)
from PyQt5.QtCore import QThread, pyqtSignal
import serial
import sys

class SerialThread(QThread):
    """串口接收线程"""
    data_received = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.is_running = True
    
    def run(self):
        while self.is_running:
            if self.serial_port.in_waiting:
                data = self.serial_port.read(self.serial_port.in_waiting)
                text = data.decode('utf-8', errors='ignore')
                self.data_received.emit(text)
            self.msleep(10)
    
    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.serial_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('嵌入式设备监控系统')
        self.setGeometry(100, 100, 900, 700)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 连接设置组
        conn_group = QGroupBox("连接设置")
        conn_layout = QHBoxLayout()
        
        conn_layout.addWidget(QLabel("串口:"))
        self.port_input = QLineEdit("/dev/ttyUSB0")
        conn_layout.addWidget(self.port_input)
        
        conn_layout.addWidget(QLabel("波特率:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['9600', '115200', '230400'])
        self.baudrate_combo.setCurrentText('115200')
        conn_layout.addWidget(self.baudrate_combo)
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # 数据显示区
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        layout.addWidget(self.data_display)
        
        # 控制按钮组
        ctrl_layout = QHBoxLayout()
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.data_display.clear)
        ctrl_layout.addWidget(clear_btn)
        
        led_on_btn = QPushButton("LED开")
        led_on_btn.clicked.connect(lambda: self.send_command("LED ON"))
        ctrl_layout.addWidget(led_on_btn)
        
        led_off_btn = QPushButton("LED关")
        led_off_btn.clicked.connect(lambda: self.send_command("LED OFF"))
        ctrl_layout.addWidget(led_off_btn)
        
        layout.addLayout(ctrl_layout)
        
        # 状态栏
        self.statusBar().showMessage('未连接')
    
    def toggle_connection(self):
        if self.serial_port is None:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        try:
            port = self.port_input.text()
            baudrate = int(self.baudrate_combo.currentText())
            
            self.serial_port = serial.Serial(port, baudrate, timeout=0.1)
            
            # 启动接收线程
            self.serial_thread = SerialThread(self.serial_port)
            self.serial_thread.data_received.connect(self.on_data_received)
            self.serial_thread.start()
            
            self.connect_btn.setText("断开")
            self.statusBar().showMessage(f'已连接: {port} @ {baudrate}')
            self.data_display.append(f"[系统] 已连接到 {port}\n")
            
        except Exception as e:
            self.data_display.append(f"[错误] 连接失败: {e}\n")
    
    def disconnect(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
        
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        
        self.connect_btn.setText("连接")
        self.statusBar().showMessage('未连接')
        self.data_display.append("[系统] 已断开连接\n")
    
    def send_command(self, cmd):
        if self.serial_port:
            try:
                self.serial_port.write(f"{cmd}\r\n".encode())
                self.data_display.append(f"[发送] {cmd}\n")
            except Exception as e:
                self.data_display.append(f"[错误] 发送失败: {e}\n")
    
    def on_data_received(self, data):
        self.data_display.append(data)
        self.data_display.ensureCursorVisible()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```


## 步骤6：实战项目 - 智能温度监控系统

### 6.1 项目概述

创建一个完整的温度监控系统，包括：
- ESP32 + 温度传感器（嵌入式端）
- Python上位机（数据采集和可视化）
- 数据存储和历史记录

### 6.2 嵌入式端代码（MicroPython）

```python
# main.py - 运行在ESP32上
from machine import Pin, I2C
import network
import socket
import time
import json

# 初始化I2C和传感器
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
SHT31_ADDR = 0x44

def read_temperature():
    """读取温度"""
    i2c.writeto(SHT31_ADDR, b'\x2C\x06')
    time.sleep(0.5)
    data = i2c.readfrom(SHT31_ADDR, 6)
    temp_raw = (data[0] << 8) | data[1]
    temp = -45 + (175 * temp_raw / 65535.0)
    hum_raw = (data[3] << 8) | data[4]
    humidity = 100 * hum_raw / 65535.0
    return temp, humidity

def connect_wifi(ssid, password):
    """连接WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep(1)
    
    print('WiFi connected:', wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def start_server():
    """启动HTTP服务器"""
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Server listening on', addr)
    
    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        
        request = cl.recv(1024).decode()
        
        if '/data' in request:
            # 读取传感器数据
            temp, hum = read_temperature()
            
            # 构造JSON响应
            data = {
                'temperature': round(temp, 2),
                'humidity': round(hum, 2),
                'timestamp': time.time()
            }
            
            response = json.dumps(data)
            
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: application/json\r\n')
            cl.send('Access-Control-Allow-Origin: *\r\n')
            cl.send('\r\n')
            cl.send(response)
        
        cl.close()

# 主程序
if __name__ == '__main__':
    ip = connect_wifi('your_ssid', 'your_password')
    print(f'Access the data at: http://{ip}/data')
    start_server()
```

### 6.3 上位机代码（Python + Matplotlib）

```python
# monitor.py - 运行在PC上
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import json

class TemperatureMonitor:
    """温度监控类"""
    
    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.url = f"http://{device_ip}/data"
        
        # 数据存储
        self.timestamps = []
        self.temperatures = []
        self.humidities = []
        
        # 设置图表
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.suptitle('实时温湿度监控')
    
    def fetch_data(self):
        """获取数据"""
        try:
            response = requests.get(self.url, timeout=2)
            data = response.json()
            
            # 添加数据
            self.timestamps.append(datetime.now())
            self.temperatures.append(data['temperature'])
            self.humidities.append(data['humidity'])
            
            # 只保留最近100个数据点
            if len(self.timestamps) > 100:
                self.timestamps.pop(0)
                self.temperatures.pop(0)
                self.humidities.pop(0)
            
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False
    
    def update_plot(self, frame):
        """更新图表"""
        if self.fetch_data():
            # 清空图表
            self.ax1.clear()
            self.ax2.clear()
            
            # 绘制温度
            self.ax1.plot(self.timestamps, self.temperatures, 'r-', label='温度')
            self.ax1.set_ylabel('温度 (°C)')
            self.ax1.legend()
            self.ax1.grid(True)
            
            # 绘制湿度
            self.ax2.plot(self.timestamps, self.humidities, 'b-', label='湿度')
            self.ax2.set_ylabel('湿度 (%)')
            self.ax2.set_xlabel('时间')
            self.ax2.legend()
            self.ax2.grid(True)
            
            # 格式化x轴
            self.fig.autofmt_xdate()
    
    def start(self):
        """启动监控"""
        ani = animation.FuncAnimation(
            self.fig, self.update_plot, interval=2000, cache_frame_data=False
        )
        plt.show()
    
    def save_data(self, filename='temperature_log.json'):
        """保存数据到文件"""
        data = {
            'timestamps': [t.isoformat() for t in self.timestamps],
            'temperatures': self.temperatures,
            'humidities': self.humidities
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filename}")

# 使用示例
if __name__ == '__main__':
    monitor = TemperatureMonitor('192.168.1.100')  # 替换为你的ESP32 IP
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.save_data()
        print("\nMonitoring stopped")
```


## 故障排除

### 问题1：无法连接到MicroPython REPL

**可能原因**：
- 串口驱动未安装
- 串口被其他程序占用
- 波特率设置错误
- USB线缆质量问题

**解决方法**：
1. 检查设备管理器中的串口设备
2. 关闭其他串口工具（Arduino IDE、PuTTY等）
3. 尝试不同的波特率（115200、9600）
4. 更换USB线缆或USB端口
5. 重新烧录MicroPython固件

### 问题2：MicroPython程序运行异常

**可能原因**：
- 内存不足
- 语法错误
- 模块导入失败
- 硬件连接问题

**解决方法**：
```python
# 检查可用内存
import gc
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# 捕获异常
try:
    # 你的代码
    pass
except Exception as e:
    print(f"Error: {e}")
    import sys
    sys.print_exception(e)
```

### 问题3：CircuitPython代码不自动运行

**可能原因**：
- 文件名不是code.py
- 语法错误导致程序崩溃
- 文件保存失败

**解决方法**：
1. 确保文件名为`code.py`
2. 检查`boot_out.txt`查看错误信息
3. 使用串口连接查看详细错误
4. 尝试重新保存文件

### 问题4：Python上位机无法连接设备

**可能原因**：
- 串口权限不足（Linux）
- 防火墙阻止连接
- IP地址错误
- 设备未连接到网络

**解决方法**：
```bash
# Linux: 添加用户到dialout组
sudo usermod -a -G dialout $USER
# 需要重新登录

# 检查串口权限
ls -l /dev/ttyUSB0

# 测试网络连接
ping 192.168.1.100
```

### 问题5：数据传输不稳定

**可能原因**：
- 串口缓冲区溢出
- 数据格式错误
- 网络延迟

**解决方法**：
```python
# 增加串口缓冲区
ser = serial.Serial(port, baudrate, timeout=1)
ser.set_buffer_size(rx_size=4096, tx_size=4096)

# 添加数据校验
import hashlib

def send_with_checksum(data):
    checksum = hashlib.md5(data.encode()).hexdigest()[:8]
    return f"{data}|{checksum}"

def verify_checksum(received):
    data, checksum = received.rsplit('|', 1)
    expected = hashlib.md5(data.encode()).hexdigest()[:8]
    return checksum == expected
```

## 总结

通过本教程，你学习了：

- ✅ MicroPython的基本使用和GPIO控制
- ✅ CircuitPython的快速开发方法
- ✅ Python在测试自动化中的应用
- ✅ 使用Python开发上位机应用
- ✅ 完整的温度监控系统实战项目

**Python在嵌入式开发中的优势**：
- 快速原型开发
- 丰富的库支持
- 易于学习和使用
- 强大的数据处理能力
- 跨平台支持

**适用场景**：
- 教育和学习
- 快速原型验证
- 测试和调试工具
- 数据采集和分析
- 上位机应用开发


## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1：MQTT物联网通信**
   - 在ESP32上实现MQTT客户端
   - 发布传感器数据到MQTT服务器
   - 使用Python订阅并处理数据

2. **挑战2：Web界面控制**
   - 在ESP32上创建Web服务器
   - 实现HTML/CSS/JavaScript前端
   - 通过浏览器控制LED和读取传感器

3. **挑战3：数据库存储**
   - 使用SQLite或MySQL存储历史数据
   - 实现数据查询和统计功能
   - 生成数据报表

4. **挑战4：机器学习应用**
   - 收集传感器数据训练模型
   - 使用TensorFlow Lite在ESP32上运行模型
   - 实现异常检测功能

## 完整代码和资源

### 代码仓库

完整的项目代码可以在GitHub上找到：
- MicroPython示例：[github.com/example/micropython-examples](https://github.com)
- CircuitPython示例：[github.com/example/circuitpython-examples](https://github.com)
- 上位机代码：[github.com/example/python-host-tools](https://github.com)

### 推荐资源

**官方文档**：
- [MicroPython官方文档](https://docs.micropython.org/)
- [CircuitPython官方文档](https://docs.circuitpython.org/)
- [Adafruit学习系统](https://learn.adafruit.com/)

**开发板推荐**：
- ESP32系列：性价比高，WiFi/蓝牙支持
- Raspberry Pi Pico：低成本，易于使用
- Circuit Playground Express：教育友好，功能丰富
- PyBoard：MicroPython官方开发板

**Python库推荐**：
- `pyserial`：串口通信
- `matplotlib`：数据可视化
- `tkinter`/`PyQt5`：GUI开发
- `requests`：HTTP通信
- `paho-mqtt`：MQTT通信

## 下一步

建议继续学习：

- [Rust嵌入式开发入门](../intermediate/05-rust-embedded-intro.html) - 学习内存安全的嵌入式编程
- [汇编语言在嵌入式中的应用](../intermediate/06-assembly-in-embedded.html) - 深入底层优化
- [多语言混合编程实践](../advanced/01-multi-language-programming.html) - 结合多种语言的优势

## 参考资料

1. MicroPython官方文档 - [docs.micropython.org](https://docs.micropython.org/)
2. CircuitPython官方文档 - [docs.circuitpython.org](https://docs.circuitpython.org/)
3. ESP32 MicroPython教程 - [randomnerdtutorials.com](https://randomnerdtutorials.com/)
4. Adafruit CircuitPython指南 - [learn.adafruit.com](https://learn.adafruit.com/)
5. Python Serial通信指南 - [pyserial.readthedocs.io](https://pyserial.readthedocs.io/)
6. 《MicroPython for the Internet of Things》- Charles Bell
7. 《Programming with MicroPython》- Nicholas H. Tollervey

---

**反馈**：如果你在学习过程中遇到问题或有改进建议，欢迎在评论区留言！

**版权声明**：本教程中的代码示例采用MIT许可证，可自由使用和修改。
