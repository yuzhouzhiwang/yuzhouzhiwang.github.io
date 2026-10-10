---
title: "数据分析工具入门：Pandas与NumPy实践应用"
description: "全面介绍Python数据分析工具Pandas和NumPy的基本概念、核心功能和实践应用，包括数据清洗、统计分析、数据处理以及在物联网和嵌入式系统中的应用"
slug: "data-analysis-tools-tutorial"

# 分类信息
domain: "云端与后台"
module: "数据分析与可视化"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 数据分析
  - Pandas
  - NumPy
  - Python
  - 数据处理
prerequisites:
  - "python-basics"
related_contents:
  - "time-series-database-tutorial"
  - "visualization-frameworks-tutorial"

# 学习信息
estimated_time: 50
difficulty_score: 2

# 作者和版本
author: "嵌入式知识平台"
author_id: ""
created_at: "2026-03-08"
updated_at: "2026-03-08"
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
  - Pandas教程
  - NumPy入门
  - Python数据分析
  - 数据清洗
  - 统计分析
cover_image: ""
---

# 数据分析工具入门：Pandas与NumPy实践应用


## 学习目标

完成本文章后，你将能够：

- [ ] 理解Pandas和NumPy的基本概念和应用场景
- [ ] 掌握NumPy数组的创建和基本操作
- [ ] 掌握Pandas的DataFrame和Series数据结构
- [ ] 熟练进行数据清洗和预处理
- [ ] 掌握常用的统计分析方法
- [ ] 理解数据处理的最佳实践
- [ ] 在物联网和嵌入式场景中应用数据分析

## 前置要求

在开始本文章之前，你需要：

**知识要求**：
- 了解Python基础语法
- 熟悉基本的数学和统计概念
- 了解数据结构基础（列表、字典）

**技能要求**：
- 能够编写简单的Python程序
- 会使用pip安装Python包
- 了解基本的命令行操作

**软件要求**：
- Python 3.8或更高版本
- Jupyter Notebook或其他Python IDE
- 至少2GB可用内存


## 概述

Pandas和NumPy是Python数据分析的核心工具库，广泛应用于数据科学、机器学习和数据工程领域。

**为什么学习Pandas和NumPy？**

- **物联网数据分析**：处理传感器数据、设备日志
- **系统监控**：分析性能指标、资源使用情况
- **质量控制**：分析生产数据、检测异常
- **预测性维护**：分析设备状态、预测故障
- **数据可视化**：为可视化工具准备数据

**核心优势**：
- 高性能的数值计算
- 丰富的数据处理功能
- 简洁的API设计
- 与其他工具良好集成
- 活跃的社区支持


## NumPy基础

### 什么是NumPy

NumPy（Numerical Python）是Python科学计算的基础库，提供高性能的多维数组对象和相关工具。

**核心特性**：
- 强大的N维数组对象（ndarray）
- 广播功能（broadcasting）
- 线性代数、傅里叶变换等数学函数
- C/C++集成工具
- 比Python原生列表快10-100倍

### 安装NumPy

```bash
# 使用pip安装
pip install numpy

# 或使用conda安装
conda install numpy

# 验证安装
python -c "import numpy; print(numpy.__version__)"
```

### NumPy数组基础

#### 创建数组

```python
import numpy as np

# 从列表创建数组
arr1 = np.array([1, 2, 3, 4, 5])
print("一维数组:", arr1)
print("数据类型:", arr1.dtype)

# 创建二维数组
arr2 = np.array([[1, 2, 3], [4, 5, 6]])
print("二维数组:\n", arr2)
print("形状:", arr2.shape)

# 创建特殊数组
zeros = np.zeros((3, 4))  # 全0数组
ones = np.ones((2, 3))    # 全1数组
empty = np.empty((2, 2))  # 未初始化数组
arange = np.arange(0, 10, 2)  # 等差数列 [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)  # 均匀分布 [0, 0.25, 0.5, 0.75, 1]

# 创建随机数组
random_arr = np.random.rand(3, 3)  # 0-1之间的随机数
random_int = np.random.randint(0, 100, (3, 3))  # 随机整数

print("随机数组:\n", random_arr)
```

#### 数组属性

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

print("维度:", arr.ndim)        # 2
print("形状:", arr.shape)       # (2, 3)
print("大小:", arr.size)        # 6
print("数据类型:", arr.dtype)   # int64
print("每个元素字节数:", arr.itemsize)  # 8
```

#### 数组索引和切片

```python
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# 基本索引
print("第一个元素:", arr[0])
print("最后一个元素:", arr[-1])

# 切片
print("前5个元素:", arr[:5])
print("后5个元素:", arr[5:])
print("步长为2:", arr[::2])

# 二维数组索引
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print("第2行第3列:", arr2d[1, 2])  # 6
print("第1行:", arr2d[0, :])
print("第2列:", arr2d[:, 1])

# 布尔索引
arr = np.array([1, 2, 3, 4, 5])
mask = arr > 3
print("大于3的元素:", arr[mask])  # [4, 5]
```


### NumPy数组运算

#### 基本运算

```python
import numpy as np

a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# 算术运算（元素级）
print("加法:", a + b)      # [11, 22, 33, 44]
print("减法:", a - b)      # [-9, -18, -27, -36]
print("乘法:", a * b)      # [10, 40, 90, 160]
print("除法:", b / a)      # [10, 10, 10, 10]
print("幂运算:", a ** 2)   # [1, 4, 9, 16]

# 标量运算
print("数组 + 10:", a + 10)  # [11, 12, 13, 14]
print("数组 * 2:", a * 2)    # [2, 4, 6, 8]

# 比较运算
print("a > 2:", a > 2)  # [False, False, True, True]
print("b == 20:", b == 20)  # [False, True, False, False]
```

#### 统计函数

```python
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

print("总和:", np.sum(data))          # 55
print("平均值:", np.mean(data))       # 5.5
print("中位数:", np.median(data))     # 5.5
print("标准差:", np.std(data))        # 2.87
print("方差:", np.var(data))          # 8.25
print("最小值:", np.min(data))        # 1
print("最大值:", np.max(data))        # 10
print("最小值索引:", np.argmin(data)) # 0
print("最大值索引:", np.argmax(data)) # 9

# 二维数组统计
arr2d = np.array([[1, 2, 3], [4, 5, 6]])
print("按列求和:", np.sum(arr2d, axis=0))  # [5, 7, 9]
print("按行求和:", np.sum(arr2d, axis=1))  # [6, 15]
```

#### 数组变形

```python
arr = np.arange(12)
print("原始数组:", arr)

# 改变形状
reshaped = arr.reshape(3, 4)
print("3x4数组:\n", reshaped)

# 转置
transposed = reshaped.T
print("转置:\n", transposed)

# 展平
flattened = reshaped.flatten()
print("展平:", flattened)

# 拼接
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
print("垂直拼接:\n", np.vstack((a, b)))
print("水平拼接:\n", np.hstack((a, b)))
```

### NumPy实践：传感器数据处理

```python
import numpy as np

# 模拟传感器数据（温度读数，单位：摄氏度）
np.random.seed(42)
temperature_readings = np.random.normal(25, 2, 1000)  # 均值25，标准差2

# 基本统计
print("=== 温度数据统计 ===")
print(f"平均温度: {np.mean(temperature_readings):.2f}°C")
print(f"最高温度: {np.max(temperature_readings):.2f}°C")
print(f"最低温度: {np.min(temperature_readings):.2f}°C")
print(f"标准差: {np.std(temperature_readings):.2f}°C")

# 异常检测（3-sigma原则）
mean = np.mean(temperature_readings)
std = np.std(temperature_readings)
outliers = temperature_readings[(temperature_readings < mean - 3*std) | 
                                (temperature_readings > mean + 3*std)]
print(f"\n异常值数量: {len(outliers)}")
print(f"异常值: {outliers}")

# 数据分箱
bins = np.array([0, 20, 25, 30, 100])
bin_indices = np.digitize(temperature_readings, bins)
print(f"\n温度分布:")
print(f"<20°C: {np.sum(bin_indices == 1)} 次")
print(f"20-25°C: {np.sum(bin_indices == 2)} 次")
print(f"25-30°C: {np.sum(bin_indices == 3)} 次")
print(f">30°C: {np.sum(bin_indices == 4)} 次")

# 移动平均（平滑数据）
window_size = 10
moving_avg = np.convolve(temperature_readings, 
                         np.ones(window_size)/window_size, 
                         mode='valid')
print(f"\n移动平均后数据点数: {len(moving_avg)}")
```


## Pandas基础

### 什么是Pandas

Pandas是基于NumPy构建的数据分析库，提供高效的数据结构和数据分析工具。

**核心数据结构**：
- **Series**：一维标记数组
- **DataFrame**：二维标记数据结构（类似表格）

**核心功能**：
- 数据读取和写入（CSV、Excel、SQL等）
- 数据清洗和预处理
- 数据筛选和聚合
- 时间序列处理
- 数据合并和连接

### 安装Pandas

```bash
# 使用pip安装
pip install pandas

# 或使用conda安装
conda install pandas

# 验证安装
python -c "import pandas; print(pandas.__version__)"
```

### Series数据结构

```python
import pandas as pd
import numpy as np

# 从列表创建Series
s1 = pd.Series([1, 2, 3, 4, 5])
print("Series:\n", s1)

# 指定索引
s2 = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
print("\n带索引的Series:\n", s2)

# 从字典创建
data_dict = {'device1': 23.5, 'device2': 24.1, 'device3': 22.8}
s3 = pd.Series(data_dict)
print("\n从字典创建:\n", s3)

# 访问元素
print("\n访问元素:")
print("第一个元素:", s2[0])
print("索引'a'的值:", s2['a'])
print("前两个元素:\n", s2[:2])

# Series运算
print("\nSeries运算:")
print("s2 + 5:\n", s2 + 5)
print("s2 * 2:\n", s2 * 2)
print("s2 > 15:\n", s2 > 15)
```

### DataFrame数据结构

```python
import pandas as pd

# 从字典创建DataFrame
data = {
    'device_id': ['dev001', 'dev002', 'dev003', 'dev004'],
    'temperature': [23.5, 24.1, 22.8, 25.3],
    'humidity': [65.2, 63.8, 67.5, 61.9],
    'location': ['room1', 'room2', 'room3', 'room1']
}
df = pd.DataFrame(data)
print("DataFrame:\n", df)

# 查看基本信息
print("\n数据形状:", df.shape)
print("列名:", df.columns.tolist())
print("索引:", df.index.tolist())
print("\n数据类型:\n", df.dtypes)
print("\n基本统计:\n", df.describe())

# 访问列
print("\n温度列:\n", df['temperature'])
print("\n多列:\n", df[['device_id', 'temperature']])

# 访问行
print("\n第一行:\n", df.iloc[0])
print("\n前两行:\n", df.head(2))
print("\n最后两行:\n", df.tail(2))

# 访问特定单元格
print("\n第2行第3列:", df.iloc[1, 2])
print("\ndevice_id为dev002的温度:", df.loc[df['device_id'] == 'dev002', 'temperature'].values[0])
```


## 数据读取和写入

### 读取CSV文件

```python
import pandas as pd

# 读取CSV文件
df = pd.read_csv('sensor_data.csv')
print(df.head())

# 指定分隔符
df = pd.read_csv('data.txt', sep='\t')

# 指定列名
df = pd.read_csv('data.csv', names=['col1', 'col2', 'col3'])

# 跳过行
df = pd.read_csv('data.csv', skiprows=2)

# 只读取特定列
df = pd.read_csv('data.csv', usecols=['device_id', 'temperature'])

# 解析日期
df = pd.read_csv('data.csv', parse_dates=['timestamp'])
```

### 写入CSV文件

```python
# 写入CSV
df.to_csv('output.csv', index=False)

# 指定分隔符
df.to_csv('output.txt', sep='\t', index=False)

# 只写入特定列
df[['device_id', 'temperature']].to_csv('temp_only.csv', index=False)

# 追加模式
df.to_csv('output.csv', mode='a', header=False, index=False)
```

### 其他格式

```python
# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
df.to_excel('output.xlsx', sheet_name='Results', index=False)

# JSON
df = pd.read_json('data.json')
df.to_json('output.json', orient='records')

# SQL数据库
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql('SELECT * FROM sensor_data', conn)
df.to_sql('new_table', conn, if_exists='replace', index=False)
```

## 数据清洗

### 处理缺失值

```python
import pandas as pd
import numpy as np

# 创建包含缺失值的数据
data = {
    'device_id': ['dev001', 'dev002', 'dev003', 'dev004', 'dev005'],
    'temperature': [23.5, np.nan, 22.8, 25.3, np.nan],
    'humidity': [65.2, 63.8, np.nan, 61.9, 64.5],
    'location': ['room1', 'room2', None, 'room1', 'room2']
}
df = pd.DataFrame(data)
print("原始数据:\n", df)

# 检查缺失值
print("\n缺失值统计:\n", df.isnull().sum())
print("\n是否有缺失值:", df.isnull().any().any())

# 删除包含缺失值的行
df_dropped = df.dropna()
print("\n删除缺失值后:\n", df_dropped)

# 删除特定列的缺失值
df_dropped_col = df.dropna(subset=['temperature'])
print("\n删除temperature缺失值:\n", df_dropped_col)

# 填充缺失值
df_filled = df.fillna(0)  # 用0填充
print("\n用0填充:\n", df_filled)

# 用均值填充
df['temperature'].fillna(df['temperature'].mean(), inplace=True)
print("\n用均值填充temperature:\n", df)

# 前向填充
df_ffill = df.fillna(method='ffill')
print("\n前向填充:\n", df_ffill)

# 后向填充
df_bfill = df.fillna(method='bfill')
print("\n后向填充:\n", df_bfill)
```

### 处理重复值

```python
# 创建包含重复值的数据
data = {
    'device_id': ['dev001', 'dev002', 'dev001', 'dev003', 'dev002'],
    'temperature': [23.5, 24.1, 23.5, 22.8, 24.1]
}
df = pd.DataFrame(data)
print("原始数据:\n", df)

# 检查重复值
print("\n重复行:", df.duplicated().sum())

# 删除重复值
df_unique = df.drop_duplicates()
print("\n删除重复后:\n", df_unique)

# 基于特定列删除重复
df_unique_device = df.drop_duplicates(subset=['device_id'])
print("\n基于device_id删除重复:\n", df_unique_device)

# 保留最后一个重复值
df_keep_last = df.drop_duplicates(keep='last')
print("\n保留最后一个:\n", df_keep_last)
```

### 数据类型转换

```python
# 创建数据
data = {
    'device_id': ['1', '2', '3'],
    'temperature': ['23.5', '24.1', '22.8'],
    'timestamp': ['2026-03-08 10:00:00', '2026-03-08 10:01:00', '2026-03-08 10:02:00']
}
df = pd.DataFrame(data)
print("原始数据类型:\n", df.dtypes)

# 转换为数值类型
df['device_id'] = df['device_id'].astype(int)
df['temperature'] = df['temperature'].astype(float)

# 转换为日期时间类型
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("\n转换后数据类型:\n", df.dtypes)
print("\n转换后数据:\n", df)
```


## 数据筛选和过滤

### 条件筛选

```python
import pandas as pd

# 创建示例数据
data = {
    'device_id': ['dev001', 'dev002', 'dev003', 'dev004', 'dev005'],
    'temperature': [23.5, 24.1, 22.8, 25.3, 21.9],
    'humidity': [65.2, 63.8, 67.5, 61.9, 68.1],
    'location': ['room1', 'room2', 'room3', 'room1', 'room2']
}
df = pd.DataFrame(data)

# 单条件筛选
high_temp = df[df['temperature'] > 24]
print("温度>24的数据:\n", high_temp)

# 多条件筛选（AND）
filtered = df[(df['temperature'] > 23) & (df['humidity'] < 65)]
print("\n温度>23且湿度<65:\n", filtered)

# 多条件筛选（OR）
filtered_or = df[(df['temperature'] > 25) | (df['humidity'] > 67)]
print("\n温度>25或湿度>67:\n", filtered_or)

# 使用isin筛选
room1_2 = df[df['location'].isin(['room1', 'room2'])]
print("\nroom1或room2的数据:\n", room1_2)

# 字符串匹配
dev00x = df[df['device_id'].str.startswith('dev00')]
print("\ndevice_id以dev00开头:\n", dev00x)

# 使用query方法
result = df.query('temperature > 23 and humidity < 65')
print("\n使用query方法:\n", result)
```

### 排序

```python
# 按单列排序
sorted_temp = df.sort_values('temperature')
print("按温度升序:\n", sorted_temp)

# 降序排序
sorted_temp_desc = df.sort_values('temperature', ascending=False)
print("\n按温度降序:\n", sorted_temp_desc)

# 多列排序
sorted_multi = df.sort_values(['location', 'temperature'])
print("\n按location和temperature排序:\n", sorted_multi)

# 按索引排序
sorted_index = df.sort_index()
print("\n按索引排序:\n", sorted_index)
```

## 数据聚合和分组

### 基本聚合

```python
import pandas as pd

# 创建示例数据
data = {
    'device_id': ['dev001', 'dev001', 'dev002', 'dev002', 'dev003', 'dev003'],
    'timestamp': pd.date_range('2026-03-08 10:00', periods=6, freq='10min'),
    'temperature': [23.5, 23.7, 24.1, 24.3, 22.8, 23.0],
    'humidity': [65.2, 65.0, 63.8, 63.5, 67.5, 67.2]
}
df = pd.DataFrame(data)
print("原始数据:\n", df)

# 基本统计
print("\n温度统计:")
print("平均值:", df['temperature'].mean())
print("中位数:", df['temperature'].median())
print("标准差:", df['temperature'].std())
print("最小值:", df['temperature'].min())
print("最大值:", df['temperature'].max())
print("总和:", df['temperature'].sum())
print("计数:", df['temperature'].count())
```

### 分组聚合

```python
# 按设备分组
grouped = df.groupby('device_id')

# 计算每个设备的平均值
avg_by_device = grouped.mean()
print("\n每个设备的平均值:\n", avg_by_device)

# 多种聚合函数
agg_result = grouped.agg({
    'temperature': ['mean', 'min', 'max', 'std'],
    'humidity': ['mean', 'min', 'max']
})
print("\n多种聚合:\n", agg_result)

# 自定义聚合函数
def temp_range(x):
    return x.max() - x.min()

custom_agg = grouped['temperature'].agg(['mean', temp_range])
print("\n自定义聚合:\n", custom_agg)

# 分组后筛选
high_avg_temp = grouped.filter(lambda x: x['temperature'].mean() > 23.5)
print("\n平均温度>23.5的组:\n", high_avg_temp)
```

### 数据透视表

```python
# 创建更复杂的数据
data = {
    'date': ['2026-03-08', '2026-03-08', '2026-03-09', '2026-03-09'] * 2,
    'device': ['dev001', 'dev002', 'dev001', 'dev002'] * 2,
    'location': ['room1', 'room2', 'room1', 'room2'] * 2,
    'temperature': [23.5, 24.1, 23.7, 24.3, 22.8, 23.0, 23.2, 23.8]
}
df = pd.DataFrame(data)

# 创建数据透视表
pivot = df.pivot_table(
    values='temperature',
    index='date',
    columns='device',
    aggfunc='mean'
)
print("数据透视表:\n", pivot)

# 多个聚合函数
pivot_multi = df.pivot_table(
    values='temperature',
    index='date',
    columns='device',
    aggfunc=['mean', 'min', 'max']
)
print("\n多聚合函数透视表:\n", pivot_multi)
```


## 时间序列处理

### 日期时间操作

```python
import pandas as pd
import numpy as np

# 创建日期范围
dates = pd.date_range('2026-03-08', periods=10, freq='H')
print("日期范围:\n", dates)

# 创建时间序列数据
ts_data = pd.Series(np.random.randn(10), index=dates)
print("\n时间序列:\n", ts_data)

# 日期时间属性
df = pd.DataFrame({
    'timestamp': pd.date_range('2026-03-08 10:00', periods=5, freq='H'),
    'value': [23.5, 24.1, 22.8, 25.3, 21.9]
})

df['year'] = df['timestamp'].dt.year
df['month'] = df['timestamp'].dt.month
df['day'] = df['timestamp'].dt.day
df['hour'] = df['timestamp'].dt.hour
df['dayofweek'] = df['timestamp'].dt.dayofweek
df['dayname'] = df['timestamp'].dt.day_name()

print("\n日期时间属性:\n", df)
```

### 时间序列重采样

```python
# 创建分钟级数据
dates = pd.date_range('2026-03-08 10:00', periods=60, freq='1min')
df = pd.DataFrame({
    'timestamp': dates,
    'temperature': np.random.normal(25, 2, 60)
})
df.set_index('timestamp', inplace=True)

# 重采样为5分钟平均值
resampled_5min = df.resample('5min').mean()
print("5分钟重采样:\n", resampled_5min.head())

# 重采样为小时数据
resampled_hour = df.resample('H').agg({
    'temperature': ['mean', 'min', 'max', 'std']
})
print("\n小时重采样:\n", resampled_hour)

# 向前填充
resampled_ffill = df.resample('10min').ffill()
print("\n向前填充:\n", resampled_ffill.head())
```

### 滚动窗口

```python
# 创建数据
dates = pd.date_range('2026-03-08', periods=20, freq='D')
df = pd.DataFrame({
    'date': dates,
    'temperature': np.random.normal(25, 3, 20)
})
df.set_index('date', inplace=True)

# 计算移动平均
df['MA_3'] = df['temperature'].rolling(window=3).mean()
df['MA_7'] = df['temperature'].rolling(window=7).mean()

print("移动平均:\n", df.head(10))

# 计算移动标准差
df['rolling_std'] = df['temperature'].rolling(window=7).std()

# 指数加权移动平均
df['EWMA'] = df['temperature'].ewm(span=7).mean()

print("\n包含EWMA:\n", df.head(10))
```

## 数据合并和连接

### 合并DataFrame

```python
import pandas as pd

# 创建两个DataFrame
df1 = pd.DataFrame({
    'device_id': ['dev001', 'dev002', 'dev003'],
    'temperature': [23.5, 24.1, 22.8]
})

df2 = pd.DataFrame({
    'device_id': ['dev001', 'dev002', 'dev004'],
    'humidity': [65.2, 63.8, 61.9]
})

# 内连接（交集）
inner_join = pd.merge(df1, df2, on='device_id', how='inner')
print("内连接:\n", inner_join)

# 左连接
left_join = pd.merge(df1, df2, on='device_id', how='left')
print("\n左连接:\n", left_join)

# 右连接
right_join = pd.merge(df1, df2, on='device_id', how='right')
print("\n右连接:\n", right_join)

# 外连接（并集）
outer_join = pd.merge(df1, df2, on='device_id', how='outer')
print("\n外连接:\n", outer_join)
```

### 拼接DataFrame

```python
# 创建数据
df1 = pd.DataFrame({
    'device_id': ['dev001', 'dev002'],
    'temperature': [23.5, 24.1]
})

df2 = pd.DataFrame({
    'device_id': ['dev003', 'dev004'],
    'temperature': [22.8, 25.3]
})

# 垂直拼接
vertical = pd.concat([df1, df2], ignore_index=True)
print("垂直拼接:\n", vertical)

# 水平拼接
df3 = pd.DataFrame({
    'humidity': [65.2, 63.8]
})
horizontal = pd.concat([df1, df3], axis=1)
print("\n水平拼接:\n", horizontal)
```


## 实践案例：物联网传感器数据分析

### 案例背景

假设我们有一个智能建筑系统，部署了多个温湿度传感器，需要分析一周的数据来：
1. 识别异常读数
2. 计算每个房间的平均环境参数
3. 分析时间趋势
4. 生成统计报告

### 生成模拟数据

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置随机种子以便复现
np.random.seed(42)

# 生成一周的时间序列（每5分钟一条记录）
start_date = datetime(2026, 3, 1)
dates = pd.date_range(start=start_date, periods=2016, freq='5min')  # 7天 * 24小时 * 12(每小时12条)

# 设备列表
devices = ['dev001', 'dev002', 'dev003', 'dev004', 'dev005']
locations = ['room1', 'room2', 'room3', 'room1', 'room2']

# 生成数据
data_list = []
for timestamp in dates:
    for i, device in enumerate(devices):
        # 基础温度随时间变化（模拟昼夜温差）
        hour = timestamp.hour
        base_temp = 22 + 3 * np.sin((hour - 6) * np.pi / 12)
        
        # 添加随机噪声
        temperature = base_temp + np.random.normal(0, 0.5)
        humidity = 60 + np.random.normal(0, 3)
        
        # 偶尔添加异常值（1%概率）
        if np.random.random() < 0.01:
            temperature += np.random.choice([-10, 10])
        
        data_list.append({
            'timestamp': timestamp,
            'device_id': device,
            'location': locations[i],
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2)
        })

# 创建DataFrame
df = pd.DataFrame(data_list)

# 保存到CSV
df.to_csv('sensor_data_week.csv', index=False)
print(f"生成了 {len(df)} 条记录")
print("\n前10条数据:")
print(df.head(10))
print("\n数据信息:")
print(df.info())
```

### 数据探索和清洗

```python
# 读取数据
df = pd.read_csv('sensor_data_week.csv', parse_dates=['timestamp'])

# 基本信息
print("=== 数据基本信息 ===")
print(f"数据形状: {df.shape}")
print(f"时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
print(f"设备数量: {df['device_id'].nunique()}")
print(f"位置数量: {df['location'].nunique()}")

# 检查缺失值
print("\n=== 缺失值检查 ===")
print(df.isnull().sum())

# 检查重复值
print(f"\n重复记录数: {df.duplicated().sum()}")

# 数据类型
print("\n=== 数据类型 ===")
print(df.dtypes)

# 基本统计
print("\n=== 基本统计 ===")
print(df[['temperature', 'humidity']].describe())
```

### 异常检测

```python
# 使用3-sigma原则检测异常
def detect_outliers(df, column, n_sigma=3):
    mean = df[column].mean()
    std = df[column].std()
    lower_bound = mean - n_sigma * std
    upper_bound = mean + n_sigma * std
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers

# 检测温度异常
temp_outliers = detect_outliers(df, 'temperature')
print(f"\n=== 温度异常检测 ===")
print(f"异常记录数: {len(temp_outliers)}")
print(f"异常比例: {len(temp_outliers)/len(df)*100:.2f}%")
print("\n异常记录示例:")
print(temp_outliers.head())

# 按设备统计异常
outlier_by_device = temp_outliers.groupby('device_id').size()
print("\n各设备异常数量:")
print(outlier_by_device)

# 可视化异常分布（如果有matplotlib）
try:
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 6))
    plt.scatter(df['timestamp'], df['temperature'], alpha=0.3, s=1, label='正常')
    plt.scatter(temp_outliers['timestamp'], temp_outliers['temperature'], 
                color='red', s=10, label='异常')
    plt.xlabel('时间')
    plt.ylabel('温度 (°C)')
    plt.title('温度数据及异常点')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('temperature_outliers.png')
    print("\n异常可视化已保存到 temperature_outliers.png")
except ImportError:
    print("\n提示: 安装matplotlib可以生成可视化图表")
```

### 分组统计分析

```python
# 按设备分组统计
device_stats = df.groupby('device_id').agg({
    'temperature': ['mean', 'min', 'max', 'std'],
    'humidity': ['mean', 'min', 'max', 'std']
}).round(2)

print("\n=== 各设备统计 ===")
print(device_stats)

# 按位置分组统计
location_stats = df.groupby('location').agg({
    'temperature': ['mean', 'min', 'max', 'std'],
    'humidity': ['mean', 'min', 'max', 'std']
}).round(2)

print("\n=== 各位置统计 ===")
print(location_stats)

# 按小时统计（分析昼夜变化）
df['hour'] = df['timestamp'].dt.hour
hourly_stats = df.groupby('hour').agg({
    'temperature': 'mean',
    'humidity': 'mean'
}).round(2)

print("\n=== 每小时平均值 ===")
print(hourly_stats)
```

### 时间序列分析

```python
# 设置时间为索引
df_ts = df.set_index('timestamp')

# 按小时重采样
hourly_data = df_ts.groupby('device_id').resample('H').agg({
    'temperature': 'mean',
    'humidity': 'mean'
}).round(2)

print("\n=== 小时重采样数据 ===")
print(hourly_data.head(24))

# 计算移动平均（平滑数据）
df_device = df[df['device_id'] == 'dev001'].set_index('timestamp')
df_device['temp_ma_12'] = df_device['temperature'].rolling(window=12).mean()  # 1小时移动平均
df_device['temp_ma_144'] = df_device['temperature'].rolling(window=144).mean()  # 12小时移动平均

print("\n=== dev001移动平均 ===")
print(df_device[['temperature', 'temp_ma_12', 'temp_ma_144']].head(20))

# 计算日平均值
daily_avg = df_ts.groupby([df_ts.index.date, 'device_id']).agg({
    'temperature': 'mean',
    'humidity': 'mean'
}).round(2)

print("\n=== 每日平均值 ===")
print(daily_avg.head(14))
```


### 生成分析报告

```python
# 生成综合报告
def generate_report(df):
    report = []
    report.append("=" * 60)
    report.append("智能建筑传感器数据分析报告")
    report.append("=" * 60)
    
    # 基本信息
    report.append(f"\n【数据概览】")
    report.append(f"分析时间段: {df['timestamp'].min()} 至 {df['timestamp'].max()}")
    report.append(f"总记录数: {len(df):,}")
    report.append(f"监测设备: {df['device_id'].nunique()} 个")
    report.append(f"监测位置: {df['location'].nunique()} 个")
    
    # 温度统计
    report.append(f"\n【温度统计】")
    report.append(f"平均温度: {df['temperature'].mean():.2f}°C")
    report.append(f"最高温度: {df['temperature'].max():.2f}°C")
    report.append(f"最低温度: {df['temperature'].min():.2f}°C")
    report.append(f"温度标准差: {df['temperature'].std():.2f}°C")
    
    # 湿度统计
    report.append(f"\n【湿度统计】")
    report.append(f"平均湿度: {df['humidity'].mean():.2f}%")
    report.append(f"最高湿度: {df['humidity'].max():.2f}%")
    report.append(f"最低湿度: {df['humidity'].min():.2f}%")
    report.append(f"湿度标准差: {df['humidity'].std():.2f}%")
    
    # 异常检测
    temp_outliers = detect_outliers(df, 'temperature')
    report.append(f"\n【异常检测】")
    report.append(f"温度异常记录: {len(temp_outliers)} 条 ({len(temp_outliers)/len(df)*100:.2f}%)")
    
    # 各位置统计
    report.append(f"\n【各位置环境统计】")
    location_stats = df.groupby('location').agg({
        'temperature': 'mean',
        'humidity': 'mean'
    }).round(2)
    for location, row in location_stats.iterrows():
        report.append(f"{location}: 温度 {row['temperature']:.2f}°C, 湿度 {row['humidity']:.2f}%")
    
    # 舒适度评估
    report.append(f"\n【舒适度评估】")
    comfortable = df[(df['temperature'] >= 20) & (df['temperature'] <= 26) & 
                     (df['humidity'] >= 40) & (df['humidity'] <= 70)]
    comfort_rate = len(comfortable) / len(df) * 100
    report.append(f"舒适环境比例: {comfort_rate:.2f}%")
    report.append(f"(标准: 温度20-26°C, 湿度40-70%)")
    
    # 建议
    report.append(f"\n【建议】")
    if df['temperature'].mean() > 26:
        report.append("- 平均温度偏高，建议加强通风或降低空调设定温度")
    elif df['temperature'].mean() < 20:
        report.append("- 平均温度偏低，建议提高供暖温度")
    
    if df['humidity'].mean() > 70:
        report.append("- 平均湿度偏高，建议使用除湿设备")
    elif df['humidity'].mean() < 40:
        report.append("- 平均湿度偏低，建议使用加湿设备")
    
    if len(temp_outliers) > len(df) * 0.05:
        report.append("- 异常数据较多，建议检查传感器工作状态")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)

# 生成并打印报告
report = generate_report(df)
print(report)

# 保存报告到文件
with open('sensor_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)
print("\n报告已保存到 sensor_analysis_report.txt")
```

### 导出处理后的数据

```python
# 移除异常值后的数据
df_cleaned = df[~df.index.isin(temp_outliers.index)]

# 添加计算列
df_cleaned['hour'] = df_cleaned['timestamp'].dt.hour
df_cleaned['day_of_week'] = df_cleaned['timestamp'].dt.day_name()
df_cleaned['is_comfortable'] = (
    (df_cleaned['temperature'] >= 20) & 
    (df_cleaned['temperature'] <= 26) & 
    (df_cleaned['humidity'] >= 40) & 
    (df_cleaned['humidity'] <= 70)
)

# 导出清洗后的数据
df_cleaned.to_csv('sensor_data_cleaned.csv', index=False)
print(f"\n清洗后数据已保存，共 {len(df_cleaned)} 条记录")

# 导出统计摘要
summary = df.groupby(['device_id', 'location']).agg({
    'temperature': ['mean', 'min', 'max', 'std'],
    'humidity': ['mean', 'min', 'max', 'std']
}).round(2)
summary.to_csv('sensor_summary.csv')
print("统计摘要已保存到 sensor_summary.csv")
```

## 性能优化技巧

### 内存优化

```python
import pandas as pd
import numpy as np

# 查看DataFrame内存使用
print("原始内存使用:")
print(df.memory_usage(deep=True))
print(f"总内存: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# 优化数据类型
df_optimized = df.copy()

# 将object类型转换为category（适用于重复值多的列）
df_optimized['device_id'] = df_optimized['device_id'].astype('category')
df_optimized['location'] = df_optimized['location'].astype('category')

# 降低数值精度
df_optimized['temperature'] = df_optimized['temperature'].astype('float32')
df_optimized['humidity'] = df_optimized['humidity'].astype('float32')

print("\n优化后内存使用:")
print(df_optimized.memory_usage(deep=True))
print(f"总内存: {df_optimized.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# 计算节省的内存
original_memory = df.memory_usage(deep=True).sum()
optimized_memory = df_optimized.memory_usage(deep=True).sum()
savings = (1 - optimized_memory / original_memory) * 100
print(f"\n节省内存: {savings:.2f}%")
```

### 计算优化

```python
# 使用向量化操作而不是循环
import time

# ❌ 慢速方法：使用循环
start = time.time()
result_slow = []
for temp in df['temperature']:
    result_slow.append(temp * 1.8 + 32)  # 转换为华氏度
end = time.time()
print(f"循环方法耗时: {end - start:.4f}秒")

# ✅ 快速方法：向量化操作
start = time.time()
result_fast = df['temperature'] * 1.8 + 32
end = time.time()
print(f"向量化方法耗时: {end - start:.4f}秒")

# 使用apply时指定raw=True可以提高性能
start = time.time()
result_apply = df['temperature'].apply(lambda x: x * 1.8 + 32)
end = time.time()
print(f"apply方法耗时: {end - start:.4f}秒")
```

### 大数据处理

```python
# 分块读取大文件
chunk_size = 10000
chunks = []

for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # 处理每个块
    processed_chunk = chunk[chunk['temperature'] > 20]
    chunks.append(processed_chunk)

# 合并所有块
result = pd.concat(chunks, ignore_index=True)

# 使用迭代器节省内存
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # 逐块处理，不保存在内存中
    print(f"处理 {len(chunk)} 条记录")
    # 进行分析或写入数据库
```


## 最佳实践

### 数据分析工作流

```
1. 数据获取
   ↓
2. 数据探索（查看基本信息、统计、分布）
   ↓
3. 数据清洗（处理缺失值、重复值、异常值）
   ↓
4. 数据转换（类型转换、特征工程）
   ↓
5. 数据分析（统计、分组、聚合）
   ↓
6. 结果可视化
   ↓
7. 报告生成
```

### 代码规范

```python
# ✅ 好的做法

# 1. 使用有意义的变量名
temperature_data = df['temperature']
avg_temperature = temperature_data.mean()

# 2. 链式操作保持可读性
result = (df
    .query('temperature > 20')
    .groupby('device_id')
    .agg({'temperature': 'mean'})
    .sort_values('temperature', ascending=False)
)

# 3. 使用inplace=False（默认），保持数据不可变
df_sorted = df.sort_values('temperature')  # 不修改原数据

# 4. 添加注释说明复杂操作
# 计算每个设备的温度异常率（超过3-sigma）
outlier_rate = (df
    .groupby('device_id')
    .apply(lambda x: ((x['temperature'] - x['temperature'].mean()).abs() 
                      > 3 * x['temperature'].std()).sum() / len(x))
)

# ❌ 避免的做法

# 1. 使用无意义的变量名
x = df['temperature']
y = x.mean()

# 2. 过长的链式操作
result = df.query('temperature > 20').groupby('device_id').agg({'temperature': 'mean'}).sort_values('temperature', ascending=False).reset_index()

# 3. 过度使用inplace=True
df.sort_values('temperature', inplace=True)  # 修改原数据，可能导致问题

# 4. 没有注释的复杂操作
outlier_rate = df.groupby('device_id').apply(lambda x: ((x['temperature'] - x['temperature'].mean()).abs() > 3 * x['temperature'].std()).sum() / len(x))
```

### 常见陷阱

```python
# 陷阱1: SettingWithCopyWarning
# ❌ 错误做法
subset = df[df['temperature'] > 20]
subset['new_column'] = 0  # 可能触发警告

# ✅ 正确做法
subset = df[df['temperature'] > 20].copy()
subset['new_column'] = 0

# 陷阱2: 链式索引
# ❌ 错误做法
df[df['temperature'] > 20]['humidity'] = 0  # 不会修改原数据

# ✅ 正确做法
df.loc[df['temperature'] > 20, 'humidity'] = 0

# 陷阱3: 忘记重置索引
# ❌ 可能导致问题
filtered = df[df['temperature'] > 20]
# 索引不连续，可能导致后续操作出错

# ✅ 重置索引
filtered = df[df['temperature'] > 20].reset_index(drop=True)

# 陷阱4: 混淆axis参数
# axis=0: 按行操作（沿着列方向）
# axis=1: 按列操作（沿着行方向）
df.drop('column_name', axis=1)  # 删除列
df.drop(0, axis=0)  # 删除行
```

## 总结

### 核心要点回顾

**NumPy核心内容**：
- ✅ NumPy数组的创建和操作
- ✅ 数组索引、切片和布尔索引
- ✅ 数组运算和广播机制
- ✅ 统计函数和数学运算
- ✅ 数组变形和拼接

**Pandas核心内容**：
- ✅ Series和DataFrame数据结构
- ✅ 数据读取和写入（CSV、Excel、JSON、SQL）
- ✅ 数据清洗（缺失值、重复值、类型转换）
- ✅ 数据筛选和排序
- ✅ 数据聚合和分组
- ✅ 时间序列处理
- ✅ 数据合并和连接

**实践应用**：
- ✅ 物联网传感器数据分析
- ✅ 异常检测
- ✅ 统计分析和报告生成
- ✅ 性能优化技巧

### 学习成果

完成本文章后，你应该能够：
1. 熟练使用NumPy进行数值计算
2. 使用Pandas进行数据清洗和预处理
3. 进行数据探索和统计分析
4. 处理时间序列数据
5. 生成数据分析报告
6. 在物联网场景中应用数据分析

### 下一步学习建议

1. **深入学习**
   - 数据可视化（Matplotlib、Seaborn）
   - 机器学习（Scikit-learn）
   - 大数据处理（Dask、PySpark）
   - 数据库操作（SQLAlchemy）

2. **实践项目**
   - 设备故障预测系统
   - 能源消耗分析
   - 质量控制分析
   - 用户行为分析

3. **进阶主题**
   - 高级数据清洗技术
   - 特征工程
   - 时间序列预测
   - 实时数据处理

## 常见问题

### Q1: Pandas和NumPy有什么区别？

**A**: 
- **NumPy**: 专注于数值计算，提供高性能的多维数组
- **Pandas**: 基于NumPy，提供更高级的数据结构和数据分析工具

**使用场景**：
- NumPy: 数值计算、矩阵运算、科学计算
- Pandas: 数据清洗、数据分析、表格数据处理

**关系**：
- Pandas底层使用NumPy数组
- 可以互相转换：`df.values` 返回NumPy数组

### Q2: 如何选择合适的数据类型？

**A**: 根据数据特点选择：

```python
# 分类数据（重复值多）
df['category_col'] = df['category_col'].astype('category')

# 整数
df['int_col'] = df['int_col'].astype('int32')  # 或 int64

# 浮点数
df['float_col'] = df['float_col'].astype('float32')  # 或 float64

# 日期时间
df['date_col'] = pd.to_datetime(df['date_col'])

# 布尔值
df['bool_col'] = df['bool_col'].astype('bool')
```

### Q3: 如何处理大数据文件？

**A**: 使用分块处理：

```python
# 方法1: 分块读取
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process(chunk)

# 方法2: 只读取需要的列
df = pd.read_csv('large_file.csv', usecols=['col1', 'col2'])

# 方法3: 使用Dask处理超大文件
import dask.dataframe as dd
ddf = dd.read_csv('large_file.csv')
result = ddf.groupby('column').mean().compute()
```

### Q4: 如何提高Pandas性能？

**A**: 多种优化方法：

1. **使用向量化操作**
```python
# ❌ 慢
df['new'] = df['col'].apply(lambda x: x * 2)

# ✅ 快
df['new'] = df['col'] * 2
```

2. **优化数据类型**
```python
df['category'] = df['category'].astype('category')
```

3. **使用query方法**
```python
# ✅ 更快
df.query('temperature > 20 and humidity < 70')
```

4. **避免循环**
```python
# ❌ 慢
for i in range(len(df)):
    df.loc[i, 'new'] = df.loc[i, 'col'] * 2

# ✅ 快
df['new'] = df['col'] * 2
```

### Q5: 如何调试Pandas代码？

**A**: 使用以下方法：

```python
# 1. 查看数据类型
print(df.dtypes)

# 2. 查看数据形状
print(df.shape)

# 3. 查看前几行
print(df.head())

# 4. 查看统计信息
print(df.describe())

# 5. 查看内存使用
print(df.memory_usage(deep=True))

# 6. 查看缺失值
print(df.isnull().sum())

# 7. 使用断言验证假设
assert df['temperature'].min() >= -50, "温度值异常"
assert df['temperature'].max() <= 100, "温度值异常"
```

## 延伸阅读

### 推荐资源

**官方文档**：
- [NumPy官方文档](https://numpy.org/doc/)
- [Pandas官方文档](https://pandas.pydata.org/docs/)
- [Python数据科学手册](https://jakevdp.github.io/PythonDataScienceHandbook/)

**在线教程**：
- [Pandas教程](https://pandas.pydata.org/docs/getting_started/tutorials.html)
- [NumPy教程](https://numpy.org/doc/stable/user/quickstart.html)

**书籍推荐**：
- 《利用Python进行数据分析》（Wes McKinney）
- 《Python数据科学手册》（Jake VanderPlas）
- 《Python for Data Analysis》

**视频课程**：
- Coursera: Applied Data Science with Python
- DataCamp: Pandas Foundations
- YouTube: Corey Schafer的Pandas教程

### 相关技术

**数据可视化**：
- Matplotlib - 基础绘图库
- Seaborn - 统计可视化
- Plotly - 交互式可视化

**机器学习**：
- Scikit-learn - 机器学习库
- TensorFlow - 深度学习
- PyTorch - 深度学习

**大数据处理**：
- Dask - 并行计算
- PySpark - 大数据处理
- Vaex - 超大数据集处理

## 参考资料

1. NumPy官方文档 - https://numpy.org/doc/
2. Pandas官方文档 - https://pandas.pydata.org/docs/
3. Python数据科学手册 - https://jakevdp.github.io/PythonDataScienceHandbook/
4. Pandas用户指南 - https://pandas.pydata.org/docs/user_guide/
5. NumPy用户指南 - https://numpy.org/doc/stable/user/

---

**反馈与支持**：
- 如果你在学习过程中遇到问题，欢迎在评论区留言
- 发现文档错误或有改进建议，请提交Issue
- 想要分享你的数据分析经验，欢迎投稿

**下一步学习**：
- [时序数据库入门](../beginner/01-time-series-db.html) - 学习InfluxDB和TimescaleDB
- [可视化框架应用](../intermediate/01-visualization-frameworks.html) - 学习Grafana和Kibana
- [大数据处理技术](../intermediate/02-big-data-processing.html) - 学习Hadoop和Spark
- [实时数据流处理](../advanced/01-real-time-stream-processing.html) - 学习Kafka Streams和Flink

---

**版权声明**：
本文采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
