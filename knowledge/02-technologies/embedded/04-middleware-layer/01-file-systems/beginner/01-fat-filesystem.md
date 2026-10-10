---
title: "FAT文件系统原理与应用"
description: "深入理解FAT12/16/32文件系统的工作原理、目录结构、文件分配表机制和簇管理方法，掌握FAT文件系统在嵌入式系统中的应用场景和实现技巧。"
slug: "fat-filesystem-principles-and-applications"

# 分类信息
domain: "中间件层"
module: "文件系统"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - FAT文件系统
  - 文件管理
  - 存储
  - 嵌入式文件系统
  - SD卡
prerequisites: []
related_contents: []

# 学习信息
estimated_time: 40
difficulty_score: 2

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
  - FAT文件系统
  - FAT12
  - FAT16
  - FAT32
  - 文件分配表
  - 簇管理
  - 嵌入式存储
cover_image: ""
---

# FAT文件系统原理与应用


## 概述

FAT（File Allocation Table，文件分配表）文件系统是一种简单而广泛使用的文件系统，由微软在1977年为软盘开发。由于其结构简单、兼容性好、资源占用少，FAT文件系统在嵌入式系统中得到了广泛应用，特别是在SD卡、U盘等可移动存储设备上。

完成本文学习后，你将能够：

- 理解FAT12/16/32三种文件系统的区别和特点
- 掌握FAT文件系统的核心数据结构
- 了解文件分配表的工作原理和簇管理机制
- 理解目录结构和文件存储方式
- 掌握FAT文件系统在嵌入式系统中的应用场景

## 背景知识

### 什么是文件系统

文件系统是操作系统用于组织和管理存储设备上数据的方法。它提供了一种将数据组织成文件和目录的方式，使得用户和应用程序可以方便地存储、检索和管理数据。

### FAT文件系统的发展历程

- **FAT12** (1977)：最早的FAT版本，用于软盘，最大支持32MB
- **FAT16** (1984)：扩展版本，最大支持2GB（后期扩展到4GB）
- **FAT32** (1996)：现代版本，最大支持2TB，广泛用于SD卡和U盘

### 为什么选择FAT

在嵌入式系统中，FAT文件系统具有以下优势：

1. **简单易实现**：数据结构简单，代码量小
2. **兼容性好**：几乎所有操作系统都支持
3. **资源占用少**：适合资源受限的嵌入式系统
4. **无需授权**：微软已公开FAT规范，可免费使用


## 核心内容

### FAT文件系统的整体结构

FAT文件系统将存储设备划分为以下几个区域：

```
+------------------+
| 引导扇区 (Boot)  |  <- 包含文件系统参数
+------------------+
| 保留扇区         |  <- 预留空间
+------------------+
| FAT1            |  <- 文件分配表1
+------------------+
| FAT2            |  <- 文件分配表2（备份）
+------------------+
| 根目录区         |  <- 根目录（仅FAT12/16）
+------------------+
| 数据区           |  <- 实际文件数据
+------------------+
```

#### 各区域功能说明

1. **引导扇区（Boot Sector）**
   - 位于第一个扇区（扇区0）
   - 包含文件系统类型、扇区大小、簇大小等关键参数
   - 包含引导代码（用于启动操作系统）

2. **文件分配表（FAT）**
   - 记录每个簇的使用状态和链接关系
   - 通常有两份（FAT1和FAT2），互为备份
   - FAT表的大小取决于数据区的簇数量

3. **根目录区**
   - 仅在FAT12/16中存在，位置和大小固定
   - FAT32中根目录存储在数据区，可动态增长

4. **数据区**
   - 存储实际的文件和目录数据
   - 以簇（Cluster）为单位进行分配


### 引导扇区（Boot Sector）详解

引导扇区是FAT文件系统的"身份证"，包含了文件系统的所有关键参数。

#### 引导扇区结构（FAT32示例）

```c
typedef struct {
    uint8_t  BS_jmpBoot[3];        // 跳转指令
    uint8_t  BS_OEMName[8];        // OEM名称
    uint16_t BPB_BytsPerSec;       // 每扇区字节数（通常512）
    uint8_t  BPB_SecPerClus;       // 每簇扇区数
    uint16_t BPB_RsvdSecCnt;       // 保留扇区数
    uint8_t  BPB_NumFATs;          // FAT表数量（通常2）
    uint16_t BPB_RootEntCnt;       // 根目录项数（FAT32为0）
    uint16_t BPB_TotSec16;         // 总扇区数（小于65536时使用）
    uint8_t  BPB_Media;            // 媒体描述符
    uint16_t BPB_FATSz16;          // FAT表大小（FAT12/16）
    uint16_t BPB_SecPerTrk;        // 每磁道扇区数
    uint16_t BPB_NumHeads;         // 磁头数
    uint32_t BPB_HiddSec;          // 隐藏扇区数
    uint32_t BPB_TotSec32;         // 总扇区数（大于65536时使用）
    
    // FAT32特有字段
    uint32_t BPB_FATSz32;          // FAT表大小
    uint16_t BPB_ExtFlags;         // 扩展标志
    uint16_t BPB_FSVer;            // 文件系统版本
    uint32_t BPB_RootClus;         // 根目录起始簇号
    uint16_t BPB_FSInfo;           // FSInfo扇区号
    uint16_t BPB_BkBootSec;        // 备份引导扇区号
    uint8_t  BPB_Reserved[12];     // 保留
    uint8_t  BS_DrvNum;            // 驱动器号
    uint8_t  BS_Reserved1;         // 保留
    uint8_t  BS_BootSig;           // 扩展引导标志
    uint32_t BS_VolID;             // 卷序列号
    uint8_t  BS_VolLab[11];        // 卷标
    uint8_t  BS_FilSysType[8];     // 文件系统类型
} __attribute__((packed)) FAT32_BootSector;
```

#### 关键参数说明

- **BPB_BytsPerSec**：扇区大小，通常为512字节
- **BPB_SecPerClus**：簇大小（以扇区为单位），常见值：1, 2, 4, 8, 16, 32, 64
- **BPB_RsvdSecCnt**：保留扇区数，FAT32通常为32
- **BPB_NumFATs**：FAT表数量，通常为2（一个主表，一个备份）
- **BPB_RootClus**：FAT32根目录起始簇号，通常为2


### 文件分配表（FAT）原理

文件分配表是FAT文件系统的核心，它记录了每个簇的使用状态和文件的簇链。

#### FAT表项的含义

FAT表中的每个表项对应数据区的一个簇，表项的值表示：

| 表项值 | 含义 |
|--------|------|
| 0x00000000 | 空闲簇 |
| 0x00000002 - 0x0FFFFFEF | 下一个簇的簇号 |
| 0x0FFFFFF0 - 0x0FFFFFF6 | 保留值 |
| 0x0FFFFFF7 | 坏簇 |
| 0x0FFFFFF8 - 0x0FFFFFFF | 文件结束标志（EOF） |

**注意**：FAT12使用12位，FAT16使用16位，FAT32使用28位（高4位保留）

#### 簇链示例

假设一个文件占用簇2、簇5、簇6，FAT表的内容如下：

```
簇号    FAT表项值    说明
0       0xFFFFFFF8  (媒体描述符)
1       0xFFFFFFFF  (分区结束标志)
2       0x00000005  -> 指向簇5
3       0x00000000  (空闲)
4       0x00000000  (空闲)
5       0x00000006  -> 指向簇6
6       0x0FFFFFFF  (文件结束)
```

文件的簇链为：2 -> 5 -> 6 -> EOF


### 目录结构

FAT文件系统中，目录也是一种特殊的文件，包含目录项（Directory Entry）的列表。

#### 目录项结构

每个目录项占32字节，包含文件的元数据：

```c
typedef struct {
    uint8_t  DIR_Name[11];         // 文件名（8.3格式）
    uint8_t  DIR_Attr;             // 文件属性
    uint8_t  DIR_NTRes;            // 保留
    uint8_t  DIR_CrtTimeTenth;     // 创建时间（十分之一秒）
    uint16_t DIR_CrtTime;          // 创建时间
    uint16_t DIR_CrtDate;          // 创建日期
    uint16_t DIR_LstAccDate;       // 最后访问日期
    uint16_t DIR_FstClusHI;        // 起始簇号高16位（FAT32）
    uint16_t DIR_WrtTime;          // 修改时间
    uint16_t DIR_WrtDate;          // 修改日期
    uint16_t DIR_FstClusLO;        // 起始簇号低16位
    uint32_t DIR_FileSize;         // 文件大小（字节）
} __attribute__((packed)) FAT_DirEntry;
```

#### 文件属性（DIR_Attr）

```c
#define ATTR_READ_ONLY  0x01  // 只读
#define ATTR_HIDDEN     0x02  // 隐藏
#define ATTR_SYSTEM     0x04  // 系统
#define ATTR_VOLUME_ID  0x08  // 卷标
#define ATTR_DIRECTORY  0x10  // 目录
#define ATTR_ARCHIVE    0x20  // 归档
#define ATTR_LONG_NAME  0x0F  // 长文件名
```

#### 8.3文件名格式

传统FAT使用8.3格式：
- 文件名最多8个字符
- 扩展名最多3个字符
- 不足部分用空格填充
- 全部大写

示例：
- "README.TXT" -> "README  TXT"
- "TEST.C" -> "TEST    C  "


### 簇（Cluster）管理

簇是FAT文件系统分配存储空间的基本单位。

#### 什么是簇

- **簇**是由一个或多个连续扇区组成的逻辑单元
- 文件系统以簇为单位分配空间，而不是以扇区为单位
- 簇的大小 = 扇区大小 × 每簇扇区数

#### 簇大小的影响

**较小的簇**：
- 优点：减少空间浪费（内部碎片少）
- 缺点：FAT表更大，文件碎片更多

**较大的簇**：
- 优点：FAT表更小，减少碎片
- 缺点：空间浪费增加（内部碎片多）

#### 典型簇大小配置

| 分区大小 | FAT16簇大小 | FAT32簇大小 |
|---------|------------|------------|
| < 128MB | 2KB | 512B |
| 128MB - 256MB | 4KB | 4KB |
| 256MB - 512MB | 8KB | 4KB |
| 512MB - 1GB | 16KB | 4KB |
| 1GB - 2GB | 32KB | 4KB |
| 2GB - 8GB | - | 4KB |
| 8GB - 16GB | - | 8KB |
| 16GB - 32GB | - | 16KB |
| > 32GB | - | 32KB |


### FAT12/16/32的区别

#### 主要区别对比

| 特性 | FAT12 | FAT16 | FAT32 |
|------|-------|-------|-------|
| FAT表项大小 | 12位 | 16位 | 28位（32位中的28位） |
| 最大簇数 | 4,084 | 65,524 | 268,435,444 |
| 最大分区大小 | 32MB | 2GB（4GB） | 2TB |
| 根目录位置 | 固定区域 | 固定区域 | 数据区（可增长） |
| 根目录大小 | 固定 | 固定 | 动态 |
| 典型应用 | 软盘 | 小容量存储 | SD卡、U盘 |

#### 如何判断FAT类型

根据簇数量判断：

```c
uint32_t CountofClusters;  // 数据区簇的总数

if (CountofClusters < 4085) {
    // FAT12
} else if (CountofClusters < 65525) {
    // FAT16
} else {
    // FAT32
}
```

**计算公式**：

```
数据区扇区数 = 总扇区数 - (保留扇区数 + FAT表扇区数 × FAT表数量 + 根目录扇区数)
簇数量 = 数据区扇区数 / 每簇扇区数
```


## 实践示例

### 示例1：读取引导扇区

```c
#include <stdint.h>
#include <stdio.h>

// 引导扇区结构（简化版）
typedef struct {
    uint8_t  BS_jmpBoot[3];
    uint8_t  BS_OEMName[8];
    uint16_t BPB_BytsPerSec;
    uint8_t  BPB_SecPerClus;
    uint16_t BPB_RsvdSecCnt;
    uint8_t  BPB_NumFATs;
    uint16_t BPB_RootEntCnt;
    uint16_t BPB_TotSec16;
    uint8_t  BPB_Media;
    uint16_t BPB_FATSz16;
    // ... 其他字段
} __attribute__((packed)) FAT_BootSector;

// 读取并解析引导扇区
void parse_boot_sector(uint8_t *sector_data) {
    FAT_BootSector *bs = (FAT_BootSector *)sector_data;
    
    printf("OEM Name: %.8s\n", bs->BS_OEMName);
    printf("Bytes per Sector: %d\n", bs->BPB_BytsPerSec);
    printf("Sectors per Cluster: %d\n", bs->BPB_SecPerClus);
    printf("Reserved Sectors: %d\n", bs->BPB_RsvdSecCnt);
    printf("Number of FATs: %d\n", bs->BPB_NumFATs);
    printf("Root Entries: %d\n", bs->BPB_RootEntCnt);
    
    // 计算簇大小
    uint32_t cluster_size = bs->BPB_BytsPerSec * bs->BPB_SecPerClus;
    printf("Cluster Size: %d bytes\n", cluster_size);
}
```

**代码说明**：
- 使用`__attribute__((packed))`确保结构体紧凑排列
- 直接将扇区数据映射到结构体
- 计算簇大小用于后续操作


### 示例2：遍历FAT表查找文件簇链

```c
#include <stdint.h>
#include <stdio.h>

#define FAT32_EOF 0x0FFFFFFF

// 读取FAT32表项
uint32_t read_fat32_entry(uint32_t *fat_table, uint32_t cluster) {
    return fat_table[cluster] & 0x0FFFFFFF;  // 只取低28位
}

// 获取文件的所有簇
void get_file_clusters(uint32_t *fat_table, uint32_t start_cluster) {
    uint32_t current_cluster = start_cluster;
    int cluster_count = 0;
    
    printf("File cluster chain: ");
    
    while (current_cluster < FAT32_EOF) {
        printf("%d ", current_cluster);
        cluster_count++;
        
        // 读取下一个簇号
        current_cluster = read_fat32_entry(fat_table, current_cluster);
        
        // 防止死循环（检测循环链）
        if (cluster_count > 10000) {
            printf("\nError: Possible circular chain detected!\n");
            break;
        }
    }
    
    printf("\nTotal clusters: %d\n", cluster_count);
}

// 使用示例
int main(void) {
    // 假设已经读取了FAT表到内存
    uint32_t fat_table[1000];  // 简化示例
    
    // 假设文件起始簇号为2
    uint32_t start_cluster = 2;
    
    get_file_clusters(fat_table, start_cluster);
    
    return 0;
}
```

**代码说明**：
- FAT32使用28位表示簇号，需要屏蔽高4位
- 通过FAT表项的链接关系遍历整个文件
- 添加循环检测防止FAT表损坏导致的死循环


### 示例3：解析目录项

```c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint8_t  DIR_Name[11];
    uint8_t  DIR_Attr;
    uint8_t  DIR_NTRes;
    uint8_t  DIR_CrtTimeTenth;
    uint16_t DIR_CrtTime;
    uint16_t DIR_CrtDate;
    uint16_t DIR_LstAccDate;
    uint16_t DIR_FstClusHI;
    uint16_t DIR_WrtTime;
    uint16_t DIR_WrtDate;
    uint16_t DIR_FstClusLO;
    uint32_t DIR_FileSize;
} __attribute__((packed)) FAT_DirEntry;

#define ATTR_DIRECTORY  0x10
#define ATTR_VOLUME_ID  0x08

// 解析文件名（8.3格式转为可读格式）
void parse_filename(uint8_t *dir_name, char *output) {
    int i, j = 0;
    
    // 复制文件名部分（去除尾部空格）
    for (i = 0; i < 8 && dir_name[i] != ' '; i++) {
        output[j++] = dir_name[i];
    }
    
    // 如果有扩展名，添加点号和扩展名
    if (dir_name[8] != ' ') {
        output[j++] = '.';
        for (i = 8; i < 11 && dir_name[i] != ' '; i++) {
            output[j++] = dir_name[i];
        }
    }
    
    output[j] = '\0';
}

// 解析并显示目录项
void parse_directory_entry(FAT_DirEntry *entry) {
    char filename[13];
    
    // 跳过已删除的文件和特殊项
    if (entry->DIR_Name[0] == 0x00) {
        return;  // 目录结束
    }
    if (entry->DIR_Name[0] == 0xE5) {
        return;  // 已删除的文件
    }
    if (entry->DIR_Attr == ATTR_VOLUME_ID) {
        return;  // 卷标
    }
    
    // 解析文件名
    parse_filename(entry->DIR_Name, filename);
    
    // 获取起始簇号
    uint32_t start_cluster = ((uint32_t)entry->DIR_FstClusHI << 16) | 
                             entry->DIR_FstClusLO;
    
    // 显示信息
    printf("%-12s ", filename);
    if (entry->DIR_Attr & ATTR_DIRECTORY) {
        printf("<DIR>     ");
    } else {
        printf("%10d ", entry->DIR_FileSize);
    }
    printf("Cluster: %d\n", start_cluster);
}
```

**代码说明**：
- 8.3格式文件名需要去除空格并添加点号
- 起始簇号由高16位和低16位组合而成
- 需要检查特殊的目录项（删除、卷标等）


## 深入理解

### 文件读写流程

#### 读取文件的完整流程

1. **定位文件**：
   - 从根目录开始，逐级查找目录
   - 在目录中查找匹配的文件名
   - 获取文件的起始簇号和文件大小

2. **读取数据**：
   - 根据起始簇号计算第一个簇的扇区位置
   - 读取簇中的数据
   - 通过FAT表找到下一个簇
   - 重复直到读取完整个文件

3. **扇区位置计算**：
```c
// 计算簇对应的第一个扇区号
uint32_t cluster_to_sector(uint32_t cluster, FAT_BootSector *bs) {
    uint32_t first_data_sector = bs->BPB_RsvdSecCnt + 
                                 (bs->BPB_NumFATs * bs->BPB_FATSz32) +
                                 bs->root_dir_sectors;
    
    return ((cluster - 2) * bs->BPB_SecPerClus) + first_data_sector;
}
```

#### 写入文件的流程

1. **分配簇**：
   - 在FAT表中查找空闲簇
   - 更新FAT表建立簇链
   - 标记最后一个簇为EOF

2. **写入数据**：
   - 将数据写入分配的簇
   - 更新目录项（文件大小、修改时间等）

3. **更新FAT表**：
   - 更新主FAT表
   - 同步更新备份FAT表


### 性能考虑

#### 碎片问题

**产生原因**：
- 文件频繁创建和删除
- 文件大小变化导致簇重新分配
- 簇分配不连续

**影响**：
- 读写性能下降（需要频繁移动读写头）
- FAT表访问次数增加

**优化方法**：
1. 预分配连续空间
2. 定期进行碎片整理
3. 使用较大的簇（权衡空间利用率）

#### 缓存策略

**FAT表缓存**：
- 将FAT表缓存到RAM中
- 减少存储设备访问次数
- 注意：写入时需要同步到存储设备

**目录缓存**：
- 缓存常用目录的内容
- 加速文件查找速度

**扇区缓存**：
- 实现读写缓冲区
- 合并多次小的读写操作


### 最佳实践

#### 嵌入式系统中使用FAT的建议

1. **选择合适的FAT类型**
   - 小容量（< 2GB）：FAT16
   - 大容量（> 2GB）：FAT32
   - 考虑兼容性需求

2. **合理配置簇大小**
   - 小文件多：使用较小的簇（减少浪费）
   - 大文件多：使用较大的簇（减少碎片）
   - 平衡空间利用率和性能

3. **实现缓存机制**
   - 至少缓存FAT表的一部分
   - 实现目录项缓存
   - 使用扇区缓冲区

4. **错误处理**
   - 检查FAT表的一致性
   - 使用备份FAT表恢复
   - 实现掉电保护机制

5. **优化读写性能**
   - 批量读写操作
   - 预读取下一个簇
   - 延迟写入（注意数据安全）

6. **使用成熟的库**
   - FatFs：轻量级、功能完整
   - EFSL：嵌入式友好
   - 避免重复造轮子


## 常见问题

### Q1: FAT32为什么不能存储大于4GB的单个文件？

**A**: 这是由FAT32的目录项结构决定的。目录项中的`DIR_FileSize`字段是32位无符号整数，最大值为2^32 - 1 = 4,294,967,295字节（约4GB）。这是FAT32的固有限制，与分区大小无关。如果需要存储更大的文件，应该使用exFAT或NTFS等文件系统。

### Q2: 为什么FAT文件系统需要两个FAT表？

**A**: 两个FAT表互为备份，提高数据可靠性：
- 如果主FAT表损坏，可以使用备份FAT表恢复
- 写入时通常同时更新两个表
- 某些实现可以通过比较两个表来检测错误
- 这是一种简单有效的冗余机制

### Q3: 如何计算FAT文件系统的实际可用空间？

**A**: 可用空间计算需要考虑多个因素：

```
总空间 = 总扇区数 × 扇区大小
系统开销 = (保留扇区 + FAT表扇区 + 根目录扇区) × 扇区大小
可用空间 = 总空间 - 系统开销
```

另外，由于簇分配的特性，小文件会造成空间浪费（内部碎片）。

### Q4: FAT文件系统支持长文件名吗？

**A**: 支持。通过VFAT（Virtual FAT）扩展实现：
- 使用多个连续的目录项存储长文件名
- 每个长文件名目录项存储13个Unicode字符
- 最后一个目录项是标准的8.3格式短文件名
- 长文件名最多支持255个字符
- 向后兼容：不支持长文件名的系统仍能看到短文件名

### Q5: 如何判断FAT文件系统是否损坏？

**A**: 常见的检查方法：
1. 检查引导扇区的签名（0x55AA）
2. 验证关键参数的合理性（扇区大小、簇大小等）
3. 比较两个FAT表是否一致
4. 检查簇链是否存在循环
5. 验证文件大小与簇链长度是否匹配
6. 检查目录结构的完整性


## 应用场景

### 嵌入式系统中的典型应用

1. **SD卡数据记录**
   - 数据采集系统
   - 行车记录仪
   - 工业监控设备
   - 优势：可直接在PC上读取数据

2. **U盘存储**
   - 固件升级
   - 配置文件存储
   - 日志记录
   - 优势：通用性好，易于维护

3. **Flash存储**
   - 嵌入式数据库
   - 文件系统
   - 配置管理
   - 注意：需要考虑Flash的磨损均衡

4. **多媒体设备**
   - MP3播放器
   - 数码相框
   - 便携式设备
   - 优势：兼容性好，易于实现

### 选择FAT的考虑因素

**适合使用FAT的场景**：
- 需要与PC交换数据
- 存储容量较小（< 32GB）
- 资源受限的嵌入式系统
- 需要简单可靠的文件系统

**不适合使用FAT的场景**：
- 需要存储大于4GB的单个文件
- 需要文件权限管理
- 需要日志功能（防止掉电损坏）
- 对性能要求很高的应用


## 总结

本文深入介绍了FAT文件系统的原理和应用，核心要点包括：

- **FAT文件系统结构**：由引导扇区、FAT表、根目录区和数据区组成，结构简单清晰
- **文件分配表（FAT）**：记录簇的使用状态和文件的簇链，是文件系统的核心
- **簇管理机制**：以簇为单位分配空间，簇大小影响空间利用率和性能
- **目录结构**：使用32字节的目录项存储文件元数据，支持8.3格式和长文件名
- **三种FAT类型**：FAT12/16/32的主要区别在于FAT表项大小和支持的最大容量
- **性能优化**：通过缓存、合理配置簇大小和减少碎片来提升性能
- **应用场景**：适合SD卡、U盘等可移动存储设备，在嵌入式系统中广泛应用

FAT文件系统虽然简单，但在嵌入式系统中仍然是最常用的文件系统之一。理解其工作原理对于开发可靠的嵌入式存储应用至关重要。

## 延伸阅读

推荐进一步学习的资源：

- [LittleFS轻量级文件系统](02-littlefs.html) - 专为嵌入式Flash设计的现代文件系统
- [SPIFFS文件系统实战](03-spiffs.html) - ESP32常用的Flash文件系统
- [文件系统移植与集成](../intermediate/01-filesystem-porting.html) - 学习如何移植FAT文件系统
- [FatFs官方文档](http://elm-chan.org/fsw/ff/) - 最流行的嵌入式FAT库
- [Microsoft FAT规范](https://www.microsoft.com/en-us/download/details.aspx?id=55984) - 官方技术规范


## 参考资料

1. Microsoft FAT Specification - Microsoft Corporation
2. "FAT32 File System Specification" - Microsoft Hardware Dev Center
3. "Practical File System Design" - Dominic Giampaolo
4. FatFs Generic FAT Filesystem Module - ChaN (elm-chan.org)
5. "Understanding the Linux Kernel" - Daniel P. Bovet & Marco Cesati
6. SD Card Association - SD Specifications
7. "Embedded Systems: Real-Time Operating Systems for ARM Cortex-M Microcontrollers" - Jonathan Valvano

---

**练习题**：

1. 计算一个16GB的SD卡使用FAT32格式化后，如果簇大小为8KB，最多可以有多少个簇？FAT表需要占用多少空间？

2. 编写代码实现一个函数，给定文件的起始簇号和文件大小，计算该文件占用了多少个簇。

3. 假设一个文件占用簇号为 5, 8, 9, 12，请画出对应的FAT表内容（假设使用FAT32）。

4. 为什么FAT文件系统在删除文件时只是修改目录项的第一个字节为0xE5，而不是立即清除FAT表和数据区？这种设计有什么优缺点？

5. 设计一个简单的FAT文件系统检查工具，能够检测并报告以下问题：
   - 簇链循环
   - 孤立的簇（在FAT表中标记为已使用，但没有文件引用）
   - 交叉链接（多个文件引用同一个簇）

**下一步**：建议学习 [LittleFS轻量级文件系统](02-littlefs.html)，了解专为嵌入式Flash设计的现代文件系统。
