---
title: "分布式存储系统设计：构建高可用嵌入式存储集群"
description: "通过完整的项目实战，学习如何设计和实现一个分布式存储系统，掌握分布式架构、数据分片、冗余备份、一致性协议等核心技术，构建高可用的嵌入式存储解决方案"
slug: "distributed-storage-system"

# 分类信息
domain: "中间件层"
module: "存储技术"
content_type: "project"
skill_level: "advanced"

# 标签和关联
tags:
  - 分布式存储
  - 系统架构
  - 数据管理
  - 高可用性
  - 数据冗余
  - 一致性协议
prerequisites:
  - "04-middleware-layer/02-storage-technology/beginner/01-flash-technology"
  - "04-middleware-layer/02-storage-technology/intermediate/01-wear-leveling"
  - "04-middleware-layer/02-storage-technology/intermediate/02-data-persistence"
  - "06-communication-networking/01-network-protocols/intermediate/01-tcp-ip-stack"
related_contents:
  - "04-middleware-layer/01-file-systems/advanced/01-high-performance-fs"
  - "06-communication-networking/02-wireless-communication/advanced/01-mesh-network"
  - "10-cross-cutting-concerns/02-reliability-fault-tolerance/advanced/01-fault-tolerant-system"

# 学习信息
estimated_time: 200
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
  - 分布式存储系统
  - 嵌入式集群
  - 数据分片技术
  - 高可用架构
  - 一致性算法
  - 故障恢复
cover_image: ""
---

# 分布式存储系统设计：构建高可用嵌入式存储集群

## 项目概述

本项目将带你从零开始设计和实现一个分布式存储系统（DSS - Distributed Storage System），专门针对嵌入式设备和IoT场景优化。这是一个完整的分布式系统项目，涵盖架构设计、网络通信、数据分片、一致性保证、故障恢复等核心技术。

### 项目特点

- **分布式架构**：多节点协同工作，无单点故障
- **数据冗余**：多副本机制保证数据安全
- **自动恢复**：节点故障自动检测和数据恢复
- **负载均衡**：智能数据分布和访问负载均衡
- **可扩展性**：支持动态添加和移除节点
- **轻量级**：针对嵌入式设备优化，资源占用小

### 学习目标

完成本项目后，你将能够：

- [ ] 理解分布式系统的核心概念和设计原则
- [ ] 掌握数据分片和副本管理技术
- [ ] 实现分布式一致性协议
- [ ] 设计故障检测和自动恢复机制
- [ ] 实现负载均衡和数据迁移
- [ ] 掌握分布式系统的测试和调试方法
- [ ] 构建完整的分布式存储解决方案

### 项目成果

**核心功能**：
- 支持3-10个存储节点的集群
- 数据自动分片和多副本存储
- 节点故障自动检测和恢复
- 数据一致性保证
- 负载均衡和性能优化

**交付物**：
- 完整的分布式存储系统代码
- 节点管理和监控工具
- 性能测试和压力测试套件
- 部署和运维文档

## 技术栈

### 硬件要求

**开发板**（每个节点）：
- STM32F407或ESP32（推荐）
- 至少256KB RAM
- 至少1MB Flash
- 以太网或WiFi模块

**存储设备**：
- SPI Flash（16MB+）或
- SD卡（4GB+）

**网络设备**：
- 以太网交换机或WiFi路由器
- 至少3个开发板组成集群

### 软件要求

**开发环境**：
- STM32CubeIDE / ESP-IDF
- GCC ARM编译器
- Python 3.8+（用于测试工具）

**网络协议**：
- TCP/IP协议栈（LwIP）
- 自定义分布式协议

**测试工具**：
- Wireshark（网络分析）
- 性能监控工具

### 技术选型

**分布式算法**：
- 一致性哈希（Consistent Hashing）
- Raft共识算法（简化版）
- Gossip协议（节点发现）

**数据管理**：
- 数据分片（Sharding）
- 多副本复制（Replication）
- 版本控制（Versioning）


## 系统架构

### 整体架构设计

分布式存储系统采用对等节点（Peer-to-Peer）架构，每个节点既是客户端也是服务器：

```
                    分布式存储集群
        ┌─────────────────────────────────┐
        │                                 │
    ┌───┴───┐      ┌───────┐      ┌───────┴──┐
    │ Node1 │◄────►│ Node2 │◄────►│  Node3   │
    │ (主)  │      │       │      │          │
    └───┬───┘      └───┬───┘      └───┬──────┘
        │              │              │
        │              │              │
        └──────────────┼──────────────┘
                       │
                   ┌───▼───┐
                   │ Node4 │
                   │       │
                   └───────┘

每个节点包含：
┌─────────────────────────────────────┐
│           应用接口层                 │
│    (PUT/GET/DELETE/LIST API)        │
├─────────────────────────────────────┤
│          分布式协调层                │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │节点  │ │数据  │ │一致性│        │
│  │管理  │ │路由  │ │协议  │        │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│          数据管理层                  │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │分片  │ │副本  │ │版本  │        │
│  │管理  │ │管理  │ │控制  │        │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│          存储引擎层                  │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │本地  │ │缓存  │ │索引  │        │
│  │存储  │ │管理  │ │管理  │        │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│          网络通信层                  │
│    (TCP/IP, 自定义协议)             │
└─────────────────────────────────────┘
```

### 核心概念

#### 1. 数据分片（Sharding）

将数据空间划分为多个分片，每个分片由不同节点负责：

```
数据键空间: [0x00000000 - 0xFFFFFFFF]

分片策略（一致性哈希）:
┌────────────────────────────────────┐
│         哈希环 (Hash Ring)          │
│                                    │
│         Node1 (0x20000000)         │
│              ↓                     │
│    ┌─────────────────────┐        │
│    │                     │        │
│ Node4 ←              → Node2      │
│(0xE0000000)        (0x60000000)   │
│    │                     │        │
│    └─────────────────────┘        │
│              ↑                     │
│         Node3 (0xA0000000)         │
│                                    │
└────────────────────────────────────┘

数据分配:
- Key的哈希值落在哪个节点区间，就存储在该节点
- 例如: hash("file1.txt") = 0x45000000 → 存储在Node2
```

#### 2. 数据副本（Replication）

每份数据存储多个副本，提高可靠性：

```
副本策略（3副本）:
数据 "file1.txt" (hash = 0x45000000)

主副本: Node2 (0x60000000) - 负责该区间
副本1: Node3 (0xA0000000) - 顺时针下一个节点
副本2: Node4 (0xE0000000) - 顺时针再下一个节点

写入流程:
Client → Node2 (主) → Node3 (副本1) → Node4 (副本2)
                ↓
            确认写入成功
```

#### 3. 一致性保证

使用简化的Raft协议保证数据一致性：

```
写入一致性流程:
1. 客户端发送写请求到主节点
2. 主节点写入本地
3. 主节点并行复制到副本节点
4. 等待多数副本确认（2/3）
5. 返回成功给客户端

读取一致性:
- 强一致性: 从主节点读取
- 最终一致性: 从任意副本读取
```


## 阶段1：基础框架搭建

### 1.1 项目结构设计

```
distributed-storage/
├── src/
│   ├── core/
│   │   ├── node.c/h              # 节点管理
│   │   ├── cluster.c/h           # 集群管理
│   │   └── config.c/h            # 配置管理
│   ├── network/
│   │   ├── protocol.c/h          # 通信协议
│   │   ├── message.c/h           # 消息处理
│   │   └── connection.c/h        # 连接管理
│   ├── storage/
│   │   ├── local_storage.c/h     # 本地存储
│   │   ├── cache.c/h             # 缓存管理
│   │   └── index.c/h             # 索引管理
│   ├── distributed/
│   │   ├── hash_ring.c/h         # 一致性哈希
│   │   ├── replication.c/h       # 副本管理
│   │   └── consistency.c/h       # 一致性协议
│   └── api/
│       └── dss_api.c/h           # 对外API
├── tests/
│   ├── unit_tests/               # 单元测试
│   └── integration_tests/        # 集成测试
├── tools/
│   ├── monitor.py                # 监控工具
│   └── benchmark.py              # 性能测试
└── docs/
    ├── architecture.md           # 架构文档
    └── api_reference.md          # API文档
```

### 1.2 核心数据结构

```c
// node.h - 节点定义
#ifndef NODE_H
#define NODE_H

#include <stdint.h>
#include <stdbool.h>

// 节点ID类型
typedef uint32_t node_id_t;

// 节点状态
typedef enum {
    NODE_STATE_INIT,        // 初始化
    NODE_STATE_JOINING,     // 加入中
    NODE_STATE_ACTIVE,      // 活跃
    NODE_STATE_LEAVING,     // 离开中
    NODE_STATE_FAILED       // 故障
} node_state_t;

// 节点信息
typedef struct {
    node_id_t id;           // 节点ID（哈希值）
    char ip_addr[16];       // IP地址
    uint16_t port;          // 端口号
    node_state_t state;     // 节点状态
    uint32_t last_heartbeat;// 最后心跳时间
    uint64_t storage_used;  // 已用存储空间
    uint64_t storage_total; // 总存储空间
} node_info_t;

// 节点操作接口
int node_init(node_info_t *node, const char *ip, uint16_t port);
int node_start(node_info_t *node);
int node_stop(node_info_t *node);
int node_send_heartbeat(node_info_t *node);
bool node_is_alive(node_info_t *node, uint32_t timeout_ms);

#endif // NODE_H
```

```c
// cluster.h - 集群管理
#ifndef CLUSTER_H
#define CLUSTER_H

#include "node.h"

#define MAX_NODES 10        // 最大节点数
#define REPLICATION_FACTOR 3 // 副本因子

// 集群信息
typedef struct {
    node_info_t nodes[MAX_NODES];   // 节点列表
    uint8_t node_count;             // 节点数量
    node_id_t local_node_id;        // 本地节点ID
    uint32_t cluster_version;       // 集群版本号
} cluster_info_t;

// 集群操作接口
int cluster_init(cluster_info_t *cluster);
int cluster_add_node(cluster_info_t *cluster, node_info_t *node);
int cluster_remove_node(cluster_info_t *cluster, node_id_t node_id);
node_info_t* cluster_find_node(cluster_info_t *cluster, node_id_t node_id);
int cluster_get_replicas(cluster_info_t *cluster, uint32_t key_hash, 
                         node_id_t *replicas, int count);

#endif // CLUSTER_H
```

```c
// protocol.h - 通信协议
#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

// 消息类型
typedef enum {
    MSG_HEARTBEAT = 1,      // 心跳
    MSG_JOIN_REQUEST,       // 加入请求
    MSG_JOIN_RESPONSE,      // 加入响应
    MSG_PUT_REQUEST,        // 写入请求
    MSG_PUT_RESPONSE,       // 写入响应
    MSG_GET_REQUEST,        // 读取请求
    MSG_GET_RESPONSE,       // 读取响应
    MSG_DELETE_REQUEST,     // 删除请求
    MSG_DELETE_RESPONSE,    // 删除响应
    MSG_REPLICATE,          // 副本复制
    MSG_SYNC_REQUEST,       // 同步请求
    MSG_SYNC_RESPONSE       // 同步响应
} message_type_t;

// 消息头
typedef struct __attribute__((packed)) {
    uint32_t magic;         // 魔数 0x44535321 ("DSS!")
    uint16_t version;       // 协议版本
    uint16_t type;          // 消息类型
    uint32_t sequence;      // 序列号
    node_id_t sender_id;    // 发送者ID
    node_id_t receiver_id;  // 接收者ID
    uint32_t payload_len;   // 负载长度
    uint32_t checksum;      // 校验和
} message_header_t;

// 完整消息
typedef struct {
    message_header_t header;
    uint8_t *payload;       // 负载数据
} message_t;

// 协议操作接口
int protocol_init(void);
int protocol_create_message(message_t *msg, message_type_t type, 
                            const void *payload, uint32_t len);
int protocol_send_message(int sockfd, message_t *msg);
int protocol_receive_message(int sockfd, message_t *msg);
void protocol_free_message(message_t *msg);

#endif // PROTOCOL_H
```

### 1.3 节点初始化实现

```c
// node.c - 节点实现
#include "node.h"
#include <string.h>
#include <time.h>

// 计算节点ID（使用IP和端口的哈希）
static uint32_t calculate_node_id(const char *ip, uint16_t port) {
    uint32_t hash = 5381;
    
    // 哈希IP地址
    for (const char *p = ip; *p != '\0'; p++) {
        hash = ((hash << 5) + hash) + *p;
    }
    
    // 哈希端口
    hash = ((hash << 5) + hash) + (port & 0xFF);
    hash = ((hash << 5) + hash) + ((port >> 8) & 0xFF);
    
    return hash;
}

/**
 * @brief 初始化节点
 */
int node_init(node_info_t *node, const char *ip, uint16_t port) {
    if (!node || !ip) {
        return -1;
    }
    
    memset(node, 0, sizeof(node_info_t));
    
    // 设置节点信息
    node->id = calculate_node_id(ip, port);
    strncpy(node->ip_addr, ip, sizeof(node->ip_addr) - 1);
    node->port = port;
    node->state = NODE_STATE_INIT;
    node->last_heartbeat = time(NULL);
    node->storage_total = 16 * 1024 * 1024;  // 16MB
    node->storage_used = 0;
    
    return 0;
}

/**
 * @brief 启动节点
 */
int node_start(node_info_t *node) {
    if (!node) {
        return -1;
    }
    
    node->state = NODE_STATE_ACTIVE;
    node->last_heartbeat = time(NULL);
    
    return 0;
}

/**
 * @brief 停止节点
 */
int node_stop(node_info_t *node) {
    if (!node) {
        return -1;
    }
    
    node->state = NODE_STATE_LEAVING;
    
    return 0;
}

/**
 * @brief 发送心跳
 */
int node_send_heartbeat(node_info_t *node) {
    if (!node) {
        return -1;
    }
    
    node->last_heartbeat = time(NULL);
    
    return 0;
}

/**
 * @brief 检查节点是否存活
 */
bool node_is_alive(node_info_t *node, uint32_t timeout_ms) {
    if (!node) {
        return false;
    }
    
    uint32_t current_time = time(NULL);
    uint32_t elapsed = (current_time - node->last_heartbeat) * 1000;
    
    return (elapsed < timeout_ms) && (node->state == NODE_STATE_ACTIVE);
}
```


## 阶段2：一致性哈希实现

### 2.1 哈希环数据结构

```c
// hash_ring.h - 一致性哈希环
#ifndef HASH_RING_H
#define HASH_RING_H

#include "node.h"

#define VIRTUAL_NODES 150   // 每个物理节点的虚拟节点数

// 虚拟节点
typedef struct {
    uint32_t hash;          // 哈希值
    node_id_t node_id;      // 对应的物理节点ID
} virtual_node_t;

// 哈希环
typedef struct {
    virtual_node_t *vnodes; // 虚拟节点数组
    int vnode_count;        // 虚拟节点数量
    int capacity;           // 容量
} hash_ring_t;

// 哈希环操作接口
int hash_ring_init(hash_ring_t *ring);
void hash_ring_destroy(hash_ring_t *ring);
int hash_ring_add_node(hash_ring_t *ring, node_id_t node_id);
int hash_ring_remove_node(hash_ring_t *ring, node_id_t node_id);
node_id_t hash_ring_get_node(hash_ring_t *ring, uint32_t key_hash);
int hash_ring_get_replicas(hash_ring_t *ring, uint32_t key_hash,
                           node_id_t *replicas, int count);

#endif // HASH_RING_H
```

### 2.2 哈希环实现

```c
// hash_ring.c - 一致性哈希环实现
#include "hash_ring.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// 哈希函数（MurmurHash3简化版）
static uint32_t murmur_hash(const void *key, int len, uint32_t seed) {
    const uint8_t *data = (const uint8_t*)key;
    uint32_t h = seed;
    
    for (int i = 0; i < len; i++) {
        h ^= data[i];
        h *= 0x5bd1e995;
        h ^= h >> 15;
    }
    
    return h;
}

// 虚拟节点比较函数（用于排序）
static int vnode_compare(const void *a, const void *b) {
    const virtual_node_t *va = (const virtual_node_t*)a;
    const virtual_node_t *vb = (const virtual_node_t*)b;
    
    if (va->hash < vb->hash) return -1;
    if (va->hash > vb->hash) return 1;
    return 0;
}

/**
 * @brief 初始化哈希环
 */
int hash_ring_init(hash_ring_t *ring) {
    if (!ring) {
        return -1;
    }
    
    ring->capacity = MAX_NODES * VIRTUAL_NODES;
    ring->vnodes = (virtual_node_t*)malloc(ring->capacity * sizeof(virtual_node_t));
    if (!ring->vnodes) {
        return -1;
    }
    
    ring->vnode_count = 0;
    
    return 0;
}

/**
 * @brief 销毁哈希环
 */
void hash_ring_destroy(hash_ring_t *ring) {
    if (ring && ring->vnodes) {
        free(ring->vnodes);
        ring->vnodes = NULL;
        ring->vnode_count = 0;
    }
}

/**
 * @brief 添加节点到哈希环
 */
int hash_ring_add_node(hash_ring_t *ring, node_id_t node_id) {
    if (!ring || !ring->vnodes) {
        return -1;
    }
    
    // 为该节点创建虚拟节点
    for (int i = 0; i < VIRTUAL_NODES; i++) {
        if (ring->vnode_count >= ring->capacity) {
            return -1;  // 容量不足
        }
        
        // 生成虚拟节点的哈希值
        char key[32];
        snprintf(key, sizeof(key), "%u-%d", node_id, i);
        uint32_t hash = murmur_hash(key, strlen(key), 0);
        
        // 添加虚拟节点
        ring->vnodes[ring->vnode_count].hash = hash;
        ring->vnodes[ring->vnode_count].node_id = node_id;
        ring->vnode_count++;
    }
    
    // 排序虚拟节点（按哈希值）
    qsort(ring->vnodes, ring->vnode_count, sizeof(virtual_node_t), vnode_compare);
    
    return 0;
}

/**
 * @brief 从哈希环移除节点
 */
int hash_ring_remove_node(hash_ring_t *ring, node_id_t node_id) {
    if (!ring || !ring->vnodes) {
        return -1;
    }
    
    // 移除该节点的所有虚拟节点
    int write_pos = 0;
    for (int read_pos = 0; read_pos < ring->vnode_count; read_pos++) {
        if (ring->vnodes[read_pos].node_id != node_id) {
            if (write_pos != read_pos) {
                ring->vnodes[write_pos] = ring->vnodes[read_pos];
            }
            write_pos++;
        }
    }
    
    ring->vnode_count = write_pos;
    
    return 0;
}

/**
 * @brief 获取键对应的节点
 */
node_id_t hash_ring_get_node(hash_ring_t *ring, uint32_t key_hash) {
    if (!ring || ring->vnode_count == 0) {
        return 0;
    }
    
    // 二分查找第一个哈希值 >= key_hash 的虚拟节点
    int left = 0;
    int right = ring->vnode_count - 1;
    
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (ring->vnodes[mid].hash < key_hash) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    
    // 如果所有节点的哈希值都小于key_hash，则回到第一个节点（环形）
    if (left == ring->vnode_count - 1 && ring->vnodes[left].hash < key_hash) {
        left = 0;
    }
    
    return ring->vnodes[left].node_id;
}

/**
 * @brief 获取键的副本节点列表
 */
int hash_ring_get_replicas(hash_ring_t *ring, uint32_t key_hash,
                           node_id_t *replicas, int count) {
    if (!ring || !replicas || count <= 0 || ring->vnode_count == 0) {
        return -1;
    }
    
    // 找到第一个节点
    int start_idx = 0;
    for (int i = 0; i < ring->vnode_count; i++) {
        if (ring->vnodes[i].hash >= key_hash) {
            start_idx = i;
            break;
        }
    }
    
    // 收集不同的物理节点
    int replica_count = 0;
    int checked = 0;
    
    for (int i = 0; i < ring->vnode_count && replica_count < count; i++) {
        int idx = (start_idx + i) % ring->vnode_count;
        node_id_t node_id = ring->vnodes[idx].node_id;
        
        // 检查是否已经添加过该物理节点
        bool already_added = false;
        for (int j = 0; j < replica_count; j++) {
            if (replicas[j] == node_id) {
                already_added = true;
                break;
            }
        }
        
        if (!already_added) {
            replicas[replica_count++] = node_id;
        }
        
        checked++;
        if (checked > ring->vnode_count) {
            break;  // 防止无限循环
        }
    }
    
    return replica_count;
}
```

### 2.3 测试哈希环

```c
// test_hash_ring.c - 哈希环测试
#include "hash_ring.h"
#include <stdio.h>
#include <assert.h>

void test_hash_ring_basic(void) {
    printf("Testing hash ring basic operations...\n");
    
    hash_ring_t ring;
    assert(hash_ring_init(&ring) == 0);
    
    // 添加3个节点
    node_id_t node1 = 0x10000000;
    node_id_t node2 = 0x50000000;
    node_id_t node3 = 0x90000000;
    
    assert(hash_ring_add_node(&ring, node1) == 0);
    assert(hash_ring_add_node(&ring, node2) == 0);
    assert(hash_ring_add_node(&ring, node3) == 0);
    
    printf("Added 3 nodes, total vnodes: %d\n", ring.vnode_count);
    
    // 测试键分配
    uint32_t test_keys[] = {0x20000000, 0x60000000, 0xA0000000};
    for (int i = 0; i < 3; i++) {
        node_id_t node = hash_ring_get_node(&ring, test_keys[i]);
        printf("Key 0x%08X -> Node 0x%08X\n", test_keys[i], node);
    }
    
    // 测试副本分配
    node_id_t replicas[3];
    int count = hash_ring_get_replicas(&ring, 0x20000000, replicas, 3);
    printf("Replicas for key 0x20000000: ");
    for (int i = 0; i < count; i++) {
        printf("0x%08X ", replicas[i]);
    }
    printf("\n");
    
    // 移除一个节点
    assert(hash_ring_remove_node(&ring, node2) == 0);
    printf("Removed node2, remaining vnodes: %d\n", ring.vnode_count);
    
    hash_ring_destroy(&ring);
    printf("Test passed!\n\n");
}

void test_hash_ring_distribution(void) {
    printf("Testing hash ring distribution...\n");
    
    hash_ring_t ring;
    hash_ring_init(&ring);
    
    // 添加4个节点
    node_id_t nodes[] = {0x10000000, 0x40000000, 0x80000000, 0xC0000000};
    for (int i = 0; i < 4; i++) {
        hash_ring_add_node(&ring, nodes[i]);
    }
    
    // 统计1000个键的分布
    int distribution[4] = {0};
    for (int i = 0; i < 1000; i++) {
        uint32_t key = murmur_hash(&i, sizeof(i), 0);
        node_id_t node = hash_ring_get_node(&ring, key);
        
        // 找到节点索引
        for (int j = 0; j < 4; j++) {
            if (node == nodes[j]) {
                distribution[j]++;
                break;
            }
        }
    }
    
    printf("Distribution of 1000 keys:\n");
    for (int i = 0; i < 4; i++) {
        printf("  Node%d: %d keys (%.1f%%)\n", 
               i, distribution[i], distribution[i] / 10.0);
    }
    
    hash_ring_destroy(&ring);
    printf("Test passed!\n\n");
}

int main(void) {
    test_hash_ring_basic();
    test_hash_ring_distribution();
    
    printf("All hash ring tests passed!\n");
    return 0;
}
```


## 阶段3：本地存储引擎

### 3.1 键值存储接口

```c
// local_storage.h - 本地存储引擎
#ifndef LOCAL_STORAGE_H
#define LOCAL_STORAGE_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_KEY_SIZE 256
#define MAX_VALUE_SIZE 4096

// 存储项
typedef struct {
    char key[MAX_KEY_SIZE];
    uint8_t *value;
    uint32_t value_len;
    uint32_t version;       // 版本号
    uint64_t timestamp;     // 时间戳
} storage_item_t;

// 存储引擎
typedef struct {
    storage_item_t *items;
    int item_count;
    int capacity;
    uint64_t total_size;
} local_storage_t;

// 存储操作接口
int storage_init(local_storage_t *storage, int capacity);
void storage_destroy(local_storage_t *storage);
int storage_put(local_storage_t *storage, const char *key, 
                const void *value, uint32_t value_len);
int storage_get(local_storage_t *storage, const char *key,
                void *value, uint32_t *value_len);
int storage_delete(local_storage_t *storage, const char *key);
bool storage_exists(local_storage_t *storage, const char *key);
int storage_list_keys(local_storage_t *storage, char **keys, int max_keys);

#endif // LOCAL_STORAGE_H
```

### 3.2 存储引擎实现

```c
// local_storage.c - 本地存储实现
#include "local_storage.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

/**
 * @brief 初始化存储引擎
 */
int storage_init(local_storage_t *storage, int capacity) {
    if (!storage || capacity <= 0) {
        return -1;
    }
    
    storage->items = (storage_item_t*)calloc(capacity, sizeof(storage_item_t));
    if (!storage->items) {
        return -1;
    }
    
    storage->item_count = 0;
    storage->capacity = capacity;
    storage->total_size = 0;
    
    return 0;
}

/**
 * @brief 销毁存储引擎
 */
void storage_destroy(local_storage_t *storage) {
    if (!storage) {
        return;
    }
    
    // 释放所有值的内存
    for (int i = 0; i < storage->item_count; i++) {
        if (storage->items[i].value) {
            free(storage->items[i].value);
        }
    }
    
    free(storage->items);
    storage->items = NULL;
    storage->item_count = 0;
}

/**
 * @brief 查找键
 */
static int storage_find_key(local_storage_t *storage, const char *key) {
    for (int i = 0; i < storage->item_count; i++) {
        if (strcmp(storage->items[i].key, key) == 0) {
            return i;
        }
    }
    return -1;
}

/**
 * @brief 存储键值对
 */
int storage_put(local_storage_t *storage, const char *key,
                const void *value, uint32_t value_len) {
    if (!storage || !key || !value || value_len == 0 || value_len > MAX_VALUE_SIZE) {
        return -1;
    }
    
    // 检查键是否已存在
    int idx = storage_find_key(storage, key);
    
    if (idx >= 0) {
        // 更新现有项
        storage_item_t *item = &storage->items[idx];
        
        // 释放旧值
        if (item->value) {
            storage->total_size -= item->value_len;
            free(item->value);
        }
        
        // 分配新值
        item->value = (uint8_t*)malloc(value_len);
        if (!item->value) {
            return -1;
        }
        
        memcpy(item->value, value, value_len);
        item->value_len = value_len;
        item->version++;
        item->timestamp = time(NULL);
        storage->total_size += value_len;
        
    } else {
        // 添加新项
        if (storage->item_count >= storage->capacity) {
            return -1;  // 容量不足
        }
        
        storage_item_t *item = &storage->items[storage->item_count];
        
        strncpy(item->key, key, MAX_KEY_SIZE - 1);
        item->key[MAX_KEY_SIZE - 1] = '\0';
        
        item->value = (uint8_t*)malloc(value_len);
        if (!item->value) {
            return -1;
        }
        
        memcpy(item->value, value, value_len);
        item->value_len = value_len;
        item->version = 1;
        item->timestamp = time(NULL);
        
        storage->item_count++;
        storage->total_size += value_len;
    }
    
    return 0;
}

/**
 * @brief 获取键值
 */
int storage_get(local_storage_t *storage, const char *key,
                void *value, uint32_t *value_len) {
    if (!storage || !key || !value || !value_len) {
        return -1;
    }
    
    int idx = storage_find_key(storage, key);
    if (idx < 0) {
        return -1;  // 键不存在
    }
    
    storage_item_t *item = &storage->items[idx];
    
    if (*value_len < item->value_len) {
        *value_len = item->value_len;
        return -2;  // 缓冲区太小
    }
    
    memcpy(value, item->value, item->value_len);
    *value_len = item->value_len;
    
    return 0;
}

/**
 * @brief 删除键
 */
int storage_delete(local_storage_t *storage, const char *key) {
    if (!storage || !key) {
        return -1;
    }
    
    int idx = storage_find_key(storage, key);
    if (idx < 0) {
        return -1;  // 键不存在
    }
    
    // 释放值内存
    storage_item_t *item = &storage->items[idx];
    if (item->value) {
        storage->total_size -= item->value_len;
        free(item->value);
    }
    
    // 移动后续项
    for (int i = idx; i < storage->item_count - 1; i++) {
        storage->items[i] = storage->items[i + 1];
    }
    
    storage->item_count--;
    
    return 0;
}

/**
 * @brief 检查键是否存在
 */
bool storage_exists(local_storage_t *storage, const char *key) {
    if (!storage || !key) {
        return false;
    }
    
    return storage_find_key(storage, key) >= 0;
}

/**
 * @brief 列出所有键
 */
int storage_list_keys(local_storage_t *storage, char **keys, int max_keys) {
    if (!storage || !keys || max_keys <= 0) {
        return -1;
    }
    
    int count = (storage->item_count < max_keys) ? storage->item_count : max_keys;
    
    for (int i = 0; i < count; i++) {
        keys[i] = storage->items[i].key;
    }
    
    return count;
}
```

### 3.3 持久化支持

```c
// storage_persistence.c - 存储持久化
#include "local_storage.h"
#include <stdio.h>

#define STORAGE_FILE "storage.dat"
#define STORAGE_MAGIC 0x44535344  // "DSSD"

// 文件头
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t item_count;
    uint64_t total_size;
} storage_file_header_t;

/**
 * @brief 保存存储到文件
 */
int storage_save_to_file(local_storage_t *storage, const char *filename) {
    if (!storage || !filename) {
        return -1;
    }
    
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        return -1;
    }
    
    // 写入文件头
    storage_file_header_t header = {
        .magic = STORAGE_MAGIC,
        .version = 1,
        .item_count = storage->item_count,
        .total_size = storage->total_size
    };
    
    if (fwrite(&header, sizeof(header), 1, fp) != 1) {
        fclose(fp);
        return -1;
    }
    
    // 写入每个项
    for (int i = 0; i < storage->item_count; i++) {
        storage_item_t *item = &storage->items[i];
        
        // 写入键长度和键
        uint32_t key_len = strlen(item->key) + 1;
        fwrite(&key_len, sizeof(key_len), 1, fp);
        fwrite(item->key, 1, key_len, fp);
        
        // 写入值长度和值
        fwrite(&item->value_len, sizeof(item->value_len), 1, fp);
        fwrite(item->value, 1, item->value_len, fp);
        
        // 写入元数据
        fwrite(&item->version, sizeof(item->version), 1, fp);
        fwrite(&item->timestamp, sizeof(item->timestamp), 1, fp);
    }
    
    fclose(fp);
    return 0;
}

/**
 * @brief 从文件加载存储
 */
int storage_load_from_file(local_storage_t *storage, const char *filename) {
    if (!storage || !filename) {
        return -1;
    }
    
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        return -1;
    }
    
    // 读取文件头
    storage_file_header_t header;
    if (fread(&header, sizeof(header), 1, fp) != 1) {
        fclose(fp);
        return -1;
    }
    
    // 验证魔数
    if (header.magic != STORAGE_MAGIC) {
        fclose(fp);
        return -1;
    }
    
    // 清空现有存储
    storage_destroy(storage);
    storage_init(storage, header.item_count + 100);
    
    // 读取每个项
    for (uint32_t i = 0; i < header.item_count; i++) {
        char key[MAX_KEY_SIZE];
        uint32_t key_len;
        uint32_t value_len;
        uint8_t *value;
        uint32_t version;
        uint64_t timestamp;
        
        // 读取键
        fread(&key_len, sizeof(key_len), 1, fp);
        fread(key, 1, key_len, fp);
        
        // 读取值
        fread(&value_len, sizeof(value_len), 1, fp);
        value = (uint8_t*)malloc(value_len);
        fread(value, 1, value_len, fp);
        
        // 读取元数据
        fread(&version, sizeof(version), 1, fp);
        fread(&timestamp, sizeof(timestamp), 1, fp);
        
        // 添加到存储
        storage_put(storage, key, value, value_len);
        
        // 更新元数据
        int idx = storage_find_key(storage, key);
        if (idx >= 0) {
            storage->items[idx].version = version;
            storage->items[idx].timestamp = timestamp;
        }
        
        free(value);
    }
    
    fclose(fp);
    return 0;
}
```


## 阶段4：网络通信实现

### 4.1 TCP服务器

```c
// connection.c - 网络连接管理
#include "connection.h"
#include "protocol.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

/**
 * @brief 创建TCP服务器
 */
int connection_create_server(uint16_t port) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        return -1;
    }
    
    // 设置地址重用
    int opt = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // 绑定地址
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    
    if (bind(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(sockfd);
        return -1;
    }
    
    // 监听
    if (listen(sockfd, 10) < 0) {
        close(sockfd);
        return -1;
    }
    
    return sockfd;
}

/**
 * @brief 连接到服务器
 */
int connection_connect(const char *ip, uint16_t port) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        return -1;
    }
    
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {
        close(sockfd);
        return -1;
    }
    
    if (connect(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(sockfd);
        return -1;
    }
    
    return sockfd;
}

/**
 * @brief 设置非阻塞模式
 */
int connection_set_nonblocking(int sockfd) {
    int flags = fcntl(sockfd, F_GETFL, 0);
    if (flags < 0) {
        return -1;
    }
    
    return fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);
}
```

### 4.2 消息处理

```c
// message.c - 消息处理
#include "message.h"
#include "protocol.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// 消息序列号（全局）
static uint32_t g_message_sequence = 0;

/**
 * @brief 创建消息
 */
int message_create(message_t *msg, message_type_t type,
                   node_id_t sender, node_id_t receiver,
                   const void *payload, uint32_t payload_len) {
    if (!msg) {
        return -1;
    }
    
    memset(msg, 0, sizeof(message_t));
    
    // 设置消息头
    msg->header.magic = 0x44535321;  // "DSS!"
    msg->header.version = 1;
    msg->header.type = type;
    msg->header.sequence = ++g_message_sequence;
    msg->header.sender_id = sender;
    msg->header.receiver_id = receiver;
    msg->header.payload_len = payload_len;
    
    // 复制负载
    if (payload_len > 0 && payload) {
        msg->payload = (uint8_t*)malloc(payload_len);
        if (!msg->payload) {
            return -1;
        }
        memcpy(msg->payload, payload, payload_len);
    }
    
    // 计算校验和（简单的累加和）
    uint32_t checksum = 0;
    uint8_t *header_bytes = (uint8_t*)&msg->header;
    for (size_t i = 0; i < sizeof(message_header_t) - sizeof(uint32_t); i++) {
        checksum += header_bytes[i];
    }
    if (msg->payload) {
        for (uint32_t i = 0; i < payload_len; i++) {
            checksum += msg->payload[i];
        }
    }
    msg->header.checksum = checksum;
    
    return 0;
}

/**
 * @brief 发送消息
 */
int message_send(int sockfd, message_t *msg) {
    if (sockfd < 0 || !msg) {
        return -1;
    }
    
    // 发送消息头
    ssize_t sent = send(sockfd, &msg->header, sizeof(message_header_t), 0);
    if (sent != sizeof(message_header_t)) {
        return -1;
    }
    
    // 发送负载
    if (msg->header.payload_len > 0 && msg->payload) {
        sent = send(sockfd, msg->payload, msg->header.payload_len, 0);
        if (sent != msg->header.payload_len) {
            return -1;
        }
    }
    
    return 0;
}

/**
 * @brief 接收消息
 */
int message_receive(int sockfd, message_t *msg) {
    if (sockfd < 0 || !msg) {
        return -1;
    }
    
    memset(msg, 0, sizeof(message_t));
    
    // 接收消息头
    ssize_t received = recv(sockfd, &msg->header, sizeof(message_header_t), 0);
    if (received != sizeof(message_header_t)) {
        return -1;
    }
    
    // 验证魔数
    if (msg->header.magic != 0x44535321) {
        return -1;
    }
    
    // 接收负载
    if (msg->header.payload_len > 0) {
        msg->payload = (uint8_t*)malloc(msg->header.payload_len);
        if (!msg->payload) {
            return -1;
        }
        
        received = recv(sockfd, msg->payload, msg->header.payload_len, 0);
        if (received != msg->header.payload_len) {
            free(msg->payload);
            msg->payload = NULL;
            return -1;
        }
    }
    
    // 验证校验和
    uint32_t checksum = 0;
    uint8_t *header_bytes = (uint8_t*)&msg->header;
    for (size_t i = 0; i < sizeof(message_header_t) - sizeof(uint32_t); i++) {
        checksum += header_bytes[i];
    }
    if (msg->payload) {
        for (uint32_t i = 0; i < msg->header.payload_len; i++) {
            checksum += msg->payload[i];
        }
    }
    
    if (checksum != msg->header.checksum) {
        message_free(msg);
        return -1;
    }
    
    return 0;
}

/**
 * @brief 释放消息
 */
void message_free(message_t *msg) {
    if (msg && msg->payload) {
        free(msg->payload);
        msg->payload = NULL;
    }
}

/**
 * @brief 打印消息信息（调试用）
 */
void message_print(message_t *msg) {
    if (!msg) {
        return;
    }
    
    printf("Message:\n");
    printf("  Type: %d\n", msg->header.type);
    printf("  Sequence: %u\n", msg->header.sequence);
    printf("  Sender: 0x%08X\n", msg->header.sender_id);
    printf("  Receiver: 0x%08X\n", msg->header.receiver_id);
    printf("  Payload Length: %u\n", msg->header.payload_len);
    printf("  Checksum: 0x%08X\n", msg->header.checksum);
}
```

### 4.3 心跳机制

```c
// heartbeat.c - 心跳机制
#include "node.h"
#include "cluster.h"
#include "message.h"
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>

#define HEARTBEAT_INTERVAL 5    // 心跳间隔（秒）
#define HEARTBEAT_TIMEOUT 15    // 心跳超时（秒）

// 心跳负载
typedef struct {
    node_id_t node_id;
    uint64_t storage_used;
    uint64_t storage_total;
    uint32_t timestamp;
} heartbeat_payload_t;

/**
 * @brief 发送心跳到所有节点
 */
static int send_heartbeat_to_all(cluster_info_t *cluster, node_info_t *local_node) {
    heartbeat_payload_t payload = {
        .node_id = local_node->id,
        .storage_used = local_node->storage_used,
        .storage_total = local_node->storage_total,
        .timestamp = time(NULL)
    };
    
    for (int i = 0; i < cluster->node_count; i++) {
        node_info_t *remote_node = &cluster->nodes[i];
        
        // 跳过自己
        if (remote_node->id == local_node->id) {
            continue;
        }
        
        // 连接到远程节点
        int sockfd = connection_connect(remote_node->ip_addr, remote_node->port);
        if (sockfd < 0) {
            printf("Failed to connect to node 0x%08X\n", remote_node->id);
            continue;
        }
        
        // 创建心跳消息
        message_t msg;
        message_create(&msg, MSG_HEARTBEAT, local_node->id, remote_node->id,
                      &payload, sizeof(payload));
        
        // 发送消息
        if (message_send(sockfd, &msg) < 0) {
            printf("Failed to send heartbeat to node 0x%08X\n", remote_node->id);
        }
        
        message_free(&msg);
        close(sockfd);
    }
    
    return 0;
}

/**
 * @brief 检查节点健康状态
 */
static void check_node_health(cluster_info_t *cluster) {
    uint32_t current_time = time(NULL);
    
    for (int i = 0; i < cluster->node_count; i++) {
        node_info_t *node = &cluster->nodes[i];
        
        // 跳过本地节点
        if (node->id == cluster->local_node_id) {
            continue;
        }
        
        // 检查心跳超时
        uint32_t elapsed = current_time - node->last_heartbeat;
        if (elapsed > HEARTBEAT_TIMEOUT && node->state == NODE_STATE_ACTIVE) {
            printf("Node 0x%08X timeout, marking as failed\n", node->id);
            node->state = NODE_STATE_FAILED;
            
            // TODO: 触发数据恢复流程
        }
    }
}

/**
 * @brief 心跳线程
 */
static void* heartbeat_thread(void *arg) {
    cluster_info_t *cluster = (cluster_info_t*)arg;
    node_info_t *local_node = cluster_find_node(cluster, cluster->local_node_id);
    
    if (!local_node) {
        return NULL;
    }
    
    printf("Heartbeat thread started\n");
    
    while (1) {
        // 发送心跳
        send_heartbeat_to_all(cluster, local_node);
        
        // 检查节点健康
        check_node_health(cluster);
        
        // 等待下一个心跳间隔
        sleep(HEARTBEAT_INTERVAL);
    }
    
    return NULL;
}

/**
 * @brief 启动心跳服务
 */
int heartbeat_start(cluster_info_t *cluster) {
    pthread_t thread;
    
    if (pthread_create(&thread, NULL, heartbeat_thread, cluster) != 0) {
        return -1;
    }
    
    pthread_detach(thread);
    
    return 0;
}
```


## 阶段5：分布式API实现

### 5.1 分布式存储API

```c
// dss_api.h - 分布式存储系统API
#ifndef DSS_API_H
#define DSS_API_H

#include "cluster.h"
#include "local_storage.h"
#include "hash_ring.h"

// DSS上下文
typedef struct {
    cluster_info_t cluster;
    local_storage_t storage;
    hash_ring_t ring;
    int server_sockfd;
    bool running;
} dss_context_t;

// API接口
int dss_init(dss_context_t *ctx, const char *ip, uint16_t port);
int dss_start(dss_context_t *ctx);
int dss_stop(dss_context_t *ctx);
int dss_join_cluster(dss_context_t *ctx, const char *seed_ip, uint16_t seed_port);

// 数据操作
int dss_put(dss_context_t *ctx, const char *key, const void *value, uint32_t value_len);
int dss_get(dss_context_t *ctx, const char *key, void *value, uint32_t *value_len);
int dss_delete(dss_context_t *ctx, const char *key);
bool dss_exists(dss_context_t *ctx, const char *key);

#endif // DSS_API_H
```

### 5.2 PUT操作实现

```c
// dss_put.c - 分布式PUT操作
#include "dss_api.h"
#include "message.h"
#include <string.h>
#include <stdio.h>

// PUT请求负载
typedef struct {
    char key[MAX_KEY_SIZE];
    uint32_t value_len;
    uint8_t value[];  // 柔性数组
} put_request_t;

// PUT响应负载
typedef struct {
    int status;  // 0=成功, -1=失败
    char message[64];
} put_response_t;

/**
 * @brief 计算键的哈希值
 */
static uint32_t calculate_key_hash(const char *key) {
    uint32_t hash = 5381;
    for (const char *p = key; *p != '\0'; p++) {
        hash = ((hash << 5) + hash) + *p;
    }
    return hash;
}

/**
 * @brief 本地PUT操作
 */
static int dss_put_local(dss_context_t *ctx, const char *key,
                         const void *value, uint32_t value_len) {
    return storage_put(&ctx->storage, key, value, value_len);
}

/**
 * @brief 远程PUT操作
 */
static int dss_put_remote(dss_context_t *ctx, node_id_t node_id,
                          const char *key, const void *value, uint32_t value_len) {
    // 查找目标节点
    node_info_t *node = cluster_find_node(&ctx->cluster, node_id);
    if (!node) {
        return -1;
    }
    
    // 连接到目标节点
    int sockfd = connection_connect(node->ip_addr, node->port);
    if (sockfd < 0) {
        printf("Failed to connect to node 0x%08X\n", node_id);
        return -1;
    }
    
    // 创建PUT请求
    size_t request_size = sizeof(put_request_t) + value_len;
    put_request_t *request = (put_request_t*)malloc(request_size);
    if (!request) {
        close(sockfd);
        return -1;
    }
    
    strncpy(request->key, key, MAX_KEY_SIZE - 1);
    request->value_len = value_len;
    memcpy(request->value, value, value_len);
    
    // 发送消息
    message_t msg;
    message_create(&msg, MSG_PUT_REQUEST, ctx->cluster.local_node_id,
                  node_id, request, request_size);
    
    int result = message_send(sockfd, &msg);
    message_free(&msg);
    free(request);
    
    if (result < 0) {
        close(sockfd);
        return -1;
    }
    
    // 接收响应
    message_t response;
    if (message_receive(sockfd, &response) < 0) {
        close(sockfd);
        return -1;
    }
    
    put_response_t *resp = (put_response_t*)response.payload;
    result = resp->status;
    
    message_free(&response);
    close(sockfd);
    
    return result;
}

/**
 * @brief 分布式PUT操作
 */
int dss_put(dss_context_t *ctx, const char *key,
            const void *value, uint32_t value_len) {
    if (!ctx || !key || !value || value_len == 0) {
        return -1;
    }
    
    // 计算键的哈希值
    uint32_t key_hash = calculate_key_hash(key);
    
    // 获取副本节点列表
    node_id_t replicas[REPLICATION_FACTOR];
    int replica_count = hash_ring_get_replicas(&ctx->ring, key_hash,
                                               replicas, REPLICATION_FACTOR);
    
    if (replica_count == 0) {
        return -1;
    }
    
    printf("PUT key='%s' to %d replicas\n", key, replica_count);
    
    // 写入所有副本
    int success_count = 0;
    for (int i = 0; i < replica_count; i++) {
        int result;
        
        if (replicas[i] == ctx->cluster.local_node_id) {
            // 本地写入
            result = dss_put_local(ctx, key, value, value_len);
            printf("  Local write: %s\n", result == 0 ? "OK" : "FAILED");
        } else {
            // 远程写入
            result = dss_put_remote(ctx, replicas[i], key, value, value_len);
            printf("  Remote write to 0x%08X: %s\n", replicas[i],
                   result == 0 ? "OK" : "FAILED");
        }
        
        if (result == 0) {
            success_count++;
        }
    }
    
    // 需要多数副本写入成功
    int required = (replica_count / 2) + 1;
    if (success_count >= required) {
        printf("PUT succeeded (%d/%d replicas)\n", success_count, replica_count);
        return 0;
    } else {
        printf("PUT failed (%d/%d replicas, need %d)\n",
               success_count, replica_count, required);
        return -1;
    }
}
```

### 5.3 GET操作实现

```c
// dss_get.c - 分布式GET操作
#include "dss_api.h"
#include "message.h"
#include <string.h>
#include <stdio.h>

// GET请求负载
typedef struct {
    char key[MAX_KEY_SIZE];
} get_request_t;

// GET响应负载
typedef struct {
    int status;  // 0=成功, -1=失败
    uint32_t value_len;
    uint8_t value[];  // 柔性数组
} get_response_t;

/**
 * @brief 本地GET操作
 */
static int dss_get_local(dss_context_t *ctx, const char *key,
                         void *value, uint32_t *value_len) {
    return storage_get(&ctx->storage, key, value, value_len);
}

/**
 * @brief 远程GET操作
 */
static int dss_get_remote(dss_context_t *ctx, node_id_t node_id,
                          const char *key, void *value, uint32_t *value_len) {
    // 查找目标节点
    node_info_t *node = cluster_find_node(&ctx->cluster, node_id);
    if (!node) {
        return -1;
    }
    
    // 连接到目标节点
    int sockfd = connection_connect(node->ip_addr, node->port);
    if (sockfd < 0) {
        return -1;
    }
    
    // 创建GET请求
    get_request_t request;
    strncpy(request.key, key, MAX_KEY_SIZE - 1);
    
    // 发送消息
    message_t msg;
    message_create(&msg, MSG_GET_REQUEST, ctx->cluster.local_node_id,
                  node_id, &request, sizeof(request));
    
    int result = message_send(sockfd, &msg);
    message_free(&msg);
    
    if (result < 0) {
        close(sockfd);
        return -1;
    }
    
    // 接收响应
    message_t response;
    if (message_receive(sockfd, &response) < 0) {
        close(sockfd);
        return -1;
    }
    
    get_response_t *resp = (get_response_t*)response.payload;
    
    if (resp->status == 0 && resp->value_len > 0) {
        if (*value_len >= resp->value_len) {
            memcpy(value, resp->value, resp->value_len);
            *value_len = resp->value_len;
            result = 0;
        } else {
            result = -2;  // 缓冲区太小
        }
    } else {
        result = -1;
    }
    
    message_free(&response);
    close(sockfd);
    
    return result;
}

/**
 * @brief 分布式GET操作
 */
int dss_get(dss_context_t *ctx, const char *key,
            void *value, uint32_t *value_len) {
    if (!ctx || !key || !value || !value_len) {
        return -1;
    }
    
    // 计算键的哈希值
    uint32_t key_hash = calculate_key_hash(key);
    
    // 获取主节点
    node_id_t primary_node = hash_ring_get_node(&ctx->ring, key_hash);
    
    printf("GET key='%s' from node 0x%08X\n", key, primary_node);
    
    // 尝试从主节点读取
    int result;
    if (primary_node == ctx->cluster.local_node_id) {
        result = dss_get_local(ctx, key, value, value_len);
    } else {
        result = dss_get_remote(ctx, primary_node, key, value, value_len);
    }
    
    if (result == 0) {
        printf("GET succeeded from primary node\n");
        return 0;
    }
    
    // 主节点失败，尝试副本节点
    printf("Primary node failed, trying replicas...\n");
    
    node_id_t replicas[REPLICATION_FACTOR];
    int replica_count = hash_ring_get_replicas(&ctx->ring, key_hash,
                                               replicas, REPLICATION_FACTOR);
    
    for (int i = 1; i < replica_count; i++) {  // 跳过主节点（i=0）
        if (replicas[i] == ctx->cluster.local_node_id) {
            result = dss_get_local(ctx, key, value, value_len);
        } else {
            result = dss_get_remote(ctx, replicas[i], key, value, value_len);
        }
        
        if (result == 0) {
            printf("GET succeeded from replica %d\n", i);
            return 0;
        }
    }
    
    printf("GET failed from all replicas\n");
    return -1;
}
```

### 5.4 服务器消息处理

```c
// dss_server.c - 服务器消息处理
#include "dss_api.h"
#include "message.h"
#include <pthread.h>
#include <stdio.h>

/**
 * @brief 处理PUT请求
 */
static void handle_put_request(dss_context_t *ctx, int client_sockfd, message_t *request) {
    put_request_t *req = (put_request_t*)request->payload;
    
    // 执行本地PUT
    int status = storage_put(&ctx->storage, req->key, req->value, req->value_len);
    
    // 创建响应
    put_response_t response = {
        .status = status
    };
    
    if (status == 0) {
        strcpy(response.message, "OK");
    } else {
        strcpy(response.message, "Failed");
    }
    
    // 发送响应
    message_t msg;
    message_create(&msg, MSG_PUT_RESPONSE, ctx->cluster.local_node_id,
                  request->header.sender_id, &response, sizeof(response));
    message_send(client_sockfd, &msg);
    message_free(&msg);
}

/**
 * @brief 处理GET请求
 */
static void handle_get_request(dss_context_t *ctx, int client_sockfd, message_t *request) {
    get_request_t *req = (get_request_t*)request->payload;
    
    // 读取数据
    uint8_t value[MAX_VALUE_SIZE];
    uint32_t value_len = MAX_VALUE_SIZE;
    int status = storage_get(&ctx->storage, req->key, value, &value_len);
    
    // 创建响应
    size_t response_size = sizeof(get_response_t) + (status == 0 ? value_len : 0);
    get_response_t *response = (get_response_t*)malloc(response_size);
    
    response->status = status;
    response->value_len = (status == 0) ? value_len : 0;
    if (status == 0) {
        memcpy(response->value, value, value_len);
    }
    
    // 发送响应
    message_t msg;
    message_create(&msg, MSG_GET_RESPONSE, ctx->cluster.local_node_id,
                  request->header.sender_id, response, response_size);
    message_send(client_sockfd, &msg);
    message_free(&msg);
    free(response);
}

/**
 * @brief 处理客户端连接
 */
static void* handle_client(void *arg) {
    struct {
        dss_context_t *ctx;
        int sockfd;
    } *params = arg;
    
    dss_context_t *ctx = params->ctx;
    int client_sockfd = params->sockfd;
    free(params);
    
    // 接收消息
    message_t msg;
    if (message_receive(client_sockfd, &msg) < 0) {
        close(client_sockfd);
        return NULL;
    }
    
    // 根据消息类型处理
    switch (msg.header.type) {
        case MSG_PUT_REQUEST:
            handle_put_request(ctx, client_sockfd, &msg);
            break;
            
        case MSG_GET_REQUEST:
            handle_get_request(ctx, client_sockfd, &msg);
            break;
            
        case MSG_HEARTBEAT:
            // 更新节点心跳时间
            {
                heartbeat_payload_t *hb = (heartbeat_payload_t*)msg.payload;
                node_info_t *node = cluster_find_node(&ctx->cluster, hb->node_id);
                if (node) {
                    node->last_heartbeat = time(NULL);
                    node->storage_used = hb->storage_used;
                }
            }
            break;
            
        default:
            printf("Unknown message type: %d\n", msg.header.type);
            break;
    }
    
    message_free(&msg);
    close(client_sockfd);
    
    return NULL;
}

/**
 * @brief 服务器主循环
 */
static void* server_thread(void *arg) {
    dss_context_t *ctx = (dss_context_t*)arg;
    
    printf("Server thread started on port %d\n",
           cluster_find_node(&ctx->cluster, ctx->cluster.local_node_id)->port);
    
    while (ctx->running) {
        // 接受客户端连接
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        
        int client_sockfd = accept(ctx->server_sockfd,
                                   (struct sockaddr*)&client_addr, &addr_len);
        if (client_sockfd < 0) {
            continue;
        }
        
        // 创建线程处理客户端
        struct {
            dss_context_t *ctx;
            int sockfd;
        } *params = malloc(sizeof(*params));
        
        params->ctx = ctx;
        params->sockfd = client_sockfd;
        
        pthread_t thread;
        pthread_create(&thread, NULL, handle_client, params);
        pthread_detach(thread);
    }
    
    return NULL;
}

/**
 * @brief 启动服务器
 */
int dss_start_server(dss_context_t *ctx) {
    pthread_t thread;
    
    if (pthread_create(&thread, NULL, server_thread, ctx) != 0) {
        return -1;
    }
    
    pthread_detach(thread);
    
    return 0;
}
```


## 阶段6：系统集成与测试

### 6.1 完整示例程序

```c
// main.c - 主程序
#include "dss_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/**
 * @brief 打印使用说明
 */
void print_usage(const char *prog_name) {
    printf("Usage: %s <mode> <ip> <port> [seed_ip] [seed_port]\n", prog_name);
    printf("  mode: 'seed' for first node, 'join' for joining node\n");
    printf("  ip: local IP address\n");
    printf("  port: local port\n");
    printf("  seed_ip: seed node IP (for join mode)\n");
    printf("  seed_port: seed node port (for join mode)\n");
}

/**
 * @brief 交互式命令行
 */
void interactive_cli(dss_context_t *ctx) {
    char command[256];
    char key[MAX_KEY_SIZE];
    char value[MAX_VALUE_SIZE];
    
    printf("\nDistributed Storage System CLI\n");
    printf("Commands: put <key> <value>, get <key>, delete <key>, list, quit\n\n");
    
    while (1) {
        printf("dss> ");
        fflush(stdout);
        
        if (!fgets(command, sizeof(command), stdin)) {
            break;
        }
        
        // 移除换行符
        command[strcspn(command, "\n")] = 0;
        
        if (strncmp(command, "put ", 4) == 0) {
            // PUT命令
            if (sscanf(command + 4, "%s %s", key, value) == 2) {
                int result = dss_put(ctx, key, value, strlen(value) + 1);
                if (result == 0) {
                    printf("OK\n");
                } else {
                    printf("ERROR: PUT failed\n");
                }
            } else {
                printf("Usage: put <key> <value>\n");
            }
            
        } else if (strncmp(command, "get ", 4) == 0) {
            // GET命令
            if (sscanf(command + 4, "%s", key) == 1) {
                uint8_t buffer[MAX_VALUE_SIZE];
                uint32_t len = MAX_VALUE_SIZE;
                
                int result = dss_get(ctx, key, buffer, &len);
                if (result == 0) {
                    printf("Value: %s\n", (char*)buffer);
                } else {
                    printf("ERROR: Key not found\n");
                }
            } else {
                printf("Usage: get <key>\n");
            }
            
        } else if (strncmp(command, "delete ", 7) == 0) {
            // DELETE命令
            if (sscanf(command + 7, "%s", key) == 1) {
                int result = dss_delete(ctx, key);
                if (result == 0) {
                    printf("OK\n");
                } else {
                    printf("ERROR: DELETE failed\n");
                }
            } else {
                printf("Usage: delete <key>\n");
            }
            
        } else if (strcmp(command, "list") == 0) {
            // LIST命令
            char *keys[100];
            int count = storage_list_keys(&ctx->storage, keys, 100);
            
            printf("Local keys (%d):\n", count);
            for (int i = 0; i < count; i++) {
                printf("  %s\n", keys[i]);
            }
            
        } else if (strcmp(command, "status") == 0) {
            // STATUS命令
            printf("Cluster Status:\n");
            printf("  Nodes: %d\n", ctx->cluster.node_count);
            printf("  Local Node ID: 0x%08X\n", ctx->cluster.local_node_id);
            printf("  Storage: %lu / %lu bytes\n",
                   ctx->storage.total_size,
                   cluster_find_node(&ctx->cluster, ctx->cluster.local_node_id)->storage_total);
            
            printf("\nNode List:\n");
            for (int i = 0; i < ctx->cluster.node_count; i++) {
                node_info_t *node = &ctx->cluster.nodes[i];
                printf("  Node 0x%08X: %s:%d [%s]\n",
                       node->id, node->ip_addr, node->port,
                       node->state == NODE_STATE_ACTIVE ? "ACTIVE" : "INACTIVE");
            }
            
        } else if (strcmp(command, "quit") == 0 || strcmp(command, "exit") == 0) {
            break;
            
        } else if (strlen(command) > 0) {
            printf("Unknown command: %s\n", command);
        }
    }
}

/**
 * @brief 主函数
 */
int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_usage(argv[0]);
        return 1;
    }
    
    const char *mode = argv[1];
    const char *local_ip = argv[2];
    uint16_t local_port = atoi(argv[3]);
    
    // 初始化DSS
    dss_context_t ctx;
    if (dss_init(&ctx, local_ip, local_port) < 0) {
        printf("Failed to initialize DSS\n");
        return 1;
    }
    
    // 启动服务器
    if (dss_start(&ctx) < 0) {
        printf("Failed to start DSS\n");
        return 1;
    }
    
    printf("DSS started on %s:%d\n", local_ip, local_port);
    printf("Node ID: 0x%08X\n", ctx.cluster.local_node_id);
    
    // 加入集群或作为种子节点
    if (strcmp(mode, "join") == 0) {
        if (argc < 6) {
            printf("Join mode requires seed_ip and seed_port\n");
            return 1;
        }
        
        const char *seed_ip = argv[4];
        uint16_t seed_port = atoi(argv[5]);
        
        printf("Joining cluster via %s:%d...\n", seed_ip, seed_port);
        
        if (dss_join_cluster(&ctx, seed_ip, seed_port) < 0) {
            printf("Failed to join cluster\n");
            return 1;
        }
        
        printf("Successfully joined cluster\n");
        
    } else if (strcmp(mode, "seed") == 0) {
        printf("Running as seed node\n");
    } else {
        printf("Unknown mode: %s\n", mode);
        return 1;
    }
    
    // 启动心跳服务
    heartbeat_start(&ctx.cluster);
    
    // 进入交互式命令行
    interactive_cli(&ctx);
    
    // 停止DSS
    dss_stop(&ctx);
    
    printf("DSS stopped\n");
    
    return 0;
}
```

### 6.2 编译和运行

```bash
# Makefile
CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread
LDFLAGS = -pthread

SRCS = main.c node.c cluster.c hash_ring.c local_storage.c \
       connection.c message.c heartbeat.c dss_api.c dss_put.c dss_get.c dss_server.c

OBJS = $(SRCS:.c=.o)
TARGET = dss

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
```

**编译**：
```bash
make
```

**运行种子节点**：
```bash
./dss seed 192.168.1.100 8001
```

**运行加入节点**：
```bash
# 终端2
./dss join 192.168.1.101 8002 192.168.1.100 8001

# 终端3
./dss join 192.168.1.102 8003 192.168.1.100 8001
```

### 6.3 功能测试

**测试1：基本读写**

在节点1上：
```
dss> put user1 Alice
OK
dss> get user1
Value: Alice
```

在节点2上：
```
dss> get user1
Value: Alice
```

**测试2：数据分布**

```
dss> put key1 value1
dss> put key2 value2
dss> put key3 value3
dss> status
```

观察数据在不同节点的分布情况。

**测试3：节点故障**

1. 启动3个节点
2. 写入数据
3. 停止一个节点
4. 从其他节点读取数据（应该成功）

**测试4：负载均衡**

```python
# test_load_balance.py
import socket
import struct
import random

def send_put(ip, port, key, value):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    
    # 构造PUT请求
    # ... (省略协议细节)
    
    sock.close()

# 发送1000个请求
nodes = [
    ('192.168.1.100', 8001),
    ('192.168.1.101', 8002),
    ('192.168.1.102', 8003)
]

for i in range(1000):
    key = f"key{i}"
    value = f"value{i}"
    node = random.choice(nodes)
    send_put(node[0], node[1], key, value)

print("Load balance test completed")
```

### 6.4 性能测试

```c
// benchmark.c - 性能测试
#include "dss_api.h"
#include <time.h>
#include <stdio.h>

void benchmark_put(dss_context_t *ctx, int count) {
    clock_t start = clock();
    
    for (int i = 0; i < count; i++) {
        char key[32];
        char value[64];
        snprintf(key, sizeof(key), "bench_key_%d", i);
        snprintf(value, sizeof(value), "bench_value_%d", i);
        
        dss_put(ctx, key, value, strlen(value) + 1);
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("PUT Benchmark:\n");
    printf("  Operations: %d\n", count);
    printf("  Time: %.2f seconds\n", elapsed);
    printf("  Throughput: %.2f ops/sec\n", count / elapsed);
}

void benchmark_get(dss_context_t *ctx, int count) {
    clock_t start = clock();
    
    for (int i = 0; i < count; i++) {
        char key[32];
        uint8_t value[64];
        uint32_t len = sizeof(value);
        
        snprintf(key, sizeof(key), "bench_key_%d", i);
        dss_get(ctx, key, value, &len);
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("GET Benchmark:\n");
    printf("  Operations: %d\n", count);
    printf("  Time: %.2f seconds\n", elapsed);
    printf("  Throughput: %.2f ops/sec\n", count / elapsed);
}

int main(void) {
    dss_context_t ctx;
    
    // 初始化
    dss_init(&ctx, "127.0.0.1", 8001);
    dss_start(&ctx);
    
    // 运行基准测试
    printf("Running benchmarks...\n\n");
    
    benchmark_put(&ctx, 1000);
    printf("\n");
    benchmark_get(&ctx, 1000);
    
    dss_stop(&ctx);
    
    return 0;
}
```


## 故障排除

### 问题1：节点无法加入集群

**现象**：
- 新节点启动后无法连接到种子节点
- 加入集群失败

**可能原因**：
- 网络连接问题
- 防火墙阻止连接
- 种子节点未运行
- IP地址或端口配置错误

**解决方法**：
1. 检查网络连接：`ping <seed_ip>`
2. 检查端口是否开放：`telnet <seed_ip> <seed_port>`
3. 检查防火墙设置
4. 验证IP和端口配置

```bash
# 检查端口监听
netstat -an | grep 8001

# 测试连接
nc -zv 192.168.1.100 8001
```

### 问题2：数据不一致

**现象**：
- 从不同节点读取同一键得到不同的值
- 写入后立即读取失败

**可能原因**：
- 副本同步延迟
- 网络分区
- 节点故障未及时检测

**解决方法**：
1. 检查网络延迟
2. 增加写入确认超时时间
3. 实现读修复机制

```c
// 读修复：比较多个副本的版本
int dss_get_with_repair(dss_context_t *ctx, const char *key,
                        void *value, uint32_t *value_len) {
    // 从所有副本读取
    // 比较版本号
    // 使用最新版本
    // 修复过期副本
}
```

### 问题3：性能下降

**现象**：
- 读写操作变慢
- 系统响应时间增加

**可能原因**：
- 网络拥塞
- 节点负载不均
- 存储空间不足
- 缓存未命中率高

**解决方法**：
1. 监控网络带宽使用
2. 检查节点负载分布
3. 增加虚拟节点数量改善负载均衡
4. 实现本地缓存

```c
// 添加缓存层
typedef struct {
    char key[MAX_KEY_SIZE];
    uint8_t *value;
    uint32_t value_len;
    time_t expire_time;
} cache_entry_t;

// 缓存查找
int cache_get(cache_t *cache, const char *key, void *value, uint32_t *len);
```

### 问题4：内存泄漏

**现象**：
- 长时间运行后内存占用持续增长
- 系统最终崩溃

**可能原因**：
- 消息未正确释放
- 存储项未清理
- 连接未关闭

**解决方法**：
1. 使用valgrind检测内存泄漏
2. 确保所有malloc都有对应的free
3. 实现资源自动清理

```bash
# 使用valgrind检测
valgrind --leak-check=full ./dss seed 127.0.0.1 8001
```

## 扩展功能

### 1. 数据压缩

```c
// compression.h - 数据压缩
#include <zlib.h>

int compress_data(const void *src, size_t src_len,
                  void *dst, size_t *dst_len) {
    return compress2(dst, dst_len, src, src_len, Z_DEFAULT_COMPRESSION);
}

int decompress_data(const void *src, size_t src_len,
                    void *dst, size_t *dst_len) {
    return uncompress(dst, dst_len, src, src_len);
}
```

### 2. 数据加密

```c
// encryption.h - 数据加密
#include <openssl/aes.h>

typedef struct {
    AES_KEY encrypt_key;
    AES_KEY decrypt_key;
    uint8_t iv[AES_BLOCK_SIZE];
} encryption_context_t;

int encrypt_data(encryption_context_t *ctx, const void *plaintext,
                 size_t len, void *ciphertext);
int decrypt_data(encryption_context_t *ctx, const void *ciphertext,
                 size_t len, void *plaintext);
```

### 3. 数据迁移

```c
// migration.c - 数据迁移
typedef struct {
    node_id_t from_node;
    node_id_t to_node;
    uint32_t key_hash_start;
    uint32_t key_hash_end;
    int status;  // 0=pending, 1=in_progress, 2=completed
} migration_task_t;

/**
 * @brief 执行数据迁移
 */
int execute_migration(dss_context_t *ctx, migration_task_t *task) {
    // 1. 标记迁移开始
    task->status = 1;
    
    // 2. 遍历本地存储，找到需要迁移的键
    for (int i = 0; i < ctx->storage.item_count; i++) {
        storage_item_t *item = &ctx->storage.items[i];
        uint32_t key_hash = calculate_key_hash(item->key);
        
        // 检查是否在迁移范围内
        if (key_hash >= task->key_hash_start && key_hash <= task->key_hash_end) {
            // 复制到目标节点
            dss_put_remote(ctx, task->to_node, item->key,
                          item->value, item->value_len);
        }
    }
    
    // 3. 标记迁移完成
    task->status = 2;
    
    return 0;
}
```

### 4. 监控和统计

```c
// monitoring.h - 监控统计
typedef struct {
    uint64_t put_count;
    uint64_t get_count;
    uint64_t delete_count;
    uint64_t put_success;
    uint64_t get_success;
    uint64_t network_bytes_sent;
    uint64_t network_bytes_received;
    double avg_put_latency;
    double avg_get_latency;
} statistics_t;

void statistics_update_put(statistics_t *stats, bool success, double latency);
void statistics_update_get(statistics_t *stats, bool success, double latency);
void statistics_print(statistics_t *stats);
```

## 最佳实践

### 1. 容量规划

**节点数量**：
- 最少3个节点（保证高可用）
- 推荐5-7个节点（平衡性能和成本）
- 根据数据量和访问量扩展

**副本因子**：
- 生产环境：3副本
- 测试环境：2副本
- 关键数据：5副本

**存储容量**：
```
总容量 = 单节点容量 × 节点数 / 副本因子
例如：16MB × 5节点 / 3副本 = 26.7MB 可用容量
```

### 2. 性能优化

**网络优化**：
- 使用连接池减少连接开销
- 批量操作减少网络往返
- 启用TCP_NODELAY减少延迟

**存储优化**：
- 使用SSD提高I/O性能
- 实现写缓冲合并小写入
- 定期压缩和清理过期数据

**并发优化**：
- 使用读写锁提高并发度
- 实现无锁数据结构
- 异步I/O减少阻塞

### 3. 可靠性保证

**数据备份**：
```bash
# 定期备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/dss-$DATE"

mkdir -p $BACKUP_DIR
cp storage.dat $BACKUP_DIR/
cp cluster.conf $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

**故障恢复**：
1. 检测节点故障（心跳超时）
2. 标记节点为失败状态
3. 从副本节点恢复数据
4. 重新平衡数据分布

**数据校验**：
```c
// 定期校验数据完整性
void verify_data_integrity(dss_context_t *ctx) {
    for (int i = 0; i < ctx->storage.item_count; i++) {
        storage_item_t *item = &ctx->storage.items[i];
        
        // 计算校验和
        uint32_t checksum = calculate_checksum(item->value, item->value_len);
        
        // 验证校验和
        if (checksum != item->checksum) {
            printf("Data corruption detected: %s\n", item->key);
            // 从副本恢复
            recover_from_replica(ctx, item->key);
        }
    }
}
```

## 项目总结

### 学到的技能

通过完成本项目，你已经掌握了：

1. **分布式系统设计**
   - 一致性哈希算法
   - 数据分片和副本管理
   - 节点发现和故障检测

2. **网络编程**
   - TCP/IP通信
   - 自定义协议设计
   - 消息序列化和反序列化

3. **存储系统**
   - 键值存储实现
   - 数据持久化
   - 缓存管理

4. **系统优化**
   - 性能测试和分析
   - 负载均衡
   - 并发控制

### 进一步学习

**推荐阅读**：
- 《Designing Data-Intensive Applications》
- 《Distributed Systems: Principles and Paradigms》
- Cassandra、Redis Cluster源码

**扩展项目**：
- 实现Raft完整共识算法
- 添加事务支持（ACID）
- 实现分布式查询引擎
- 支持多数据中心部署

### 实际应用

本项目的技术可应用于：

- **IoT数据存储**：传感器数据分布式存储
- **边缘计算**：边缘节点协同存储
- **智能家居**：设备配置分布式管理
- **工业监控**：生产数据高可用存储

## 参考资源

### 开源项目

- **Cassandra**：分布式NoSQL数据库
- **Redis Cluster**：分布式内存数据库
- **Ceph**：分布式对象存储
- **etcd**：分布式键值存储

### 学习资源

- [Raft共识算法可视化](https://raft.github.io/)
- [一致性哈希详解](https://www.toptal.com/big-data/consistent-hashing)
- [分布式系统课程](https://pdos.csail.mit.edu/6.824/)

### 工具和库

- **ZeroMQ**：高性能消息队列
- **Protocol Buffers**：数据序列化
- **RocksDB**：嵌入式键值存储引擎

---

**恭喜你完成了分布式存储系统项目！** 这是一个复杂但非常有价值的项目，你已经掌握了构建分布式系统的核心技能。继续探索和优化，将这些技术应用到实际项目中！
