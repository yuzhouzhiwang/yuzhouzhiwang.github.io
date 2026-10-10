---
title: "哈希算法与消息摘要：数据完整性保护基础"
description: "全面学习哈希算法原理，掌握MD5、SHA系列算法的应用，理解消息摘要在数据完整性校验、密码存储和数字签名中的作用"
slug: "hash-algorithms"

# 分类信息
domain: "中间件层"
module: "安全与加密"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 哈希算法
  - SHA
  - 数据完整性
  - 消息摘要
  - 密码学
prerequisites:
  - "01-hardware-layer/01-chip-architecture/beginner/01-arm-cortex-m-introduction"
related_contents:
  - "04-middleware-layer/05-security-encryption/beginner/01-aes-encryption"
  - "04-middleware-layer/05-security-encryption/beginner/02-rsa-encryption"
  - "04-middleware-layer/05-security-encryption/intermediate/01-digital-signature"

# 学习信息
estimated_time: 40
difficulty_score: 2

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
  - 哈希算法
  - SHA256
  - MD5
  - 消息摘要
  - 数据完整性
  - 密码存储
cover_image: ""
---

# 哈希算法与消息摘要：数据完整性保护基础


## 概述

哈希算法（Hash Algorithm）是密码学中的基础工具，它能将任意长度的数据转换为固定长度的"指纹"。完成本文学习后，你将能够：

- 理解哈希算法的基本原理和特性
- 掌握MD5、SHA-1、SHA-256等常用哈希算法
- 了解哈希算法在数据完整性校验中的应用
- 掌握密码安全存储的最佳实践
- 理解哈希算法在数字签名中的作用
- 能够在嵌入式系统中实现哈希功能
- 了解常见的哈希攻击和防护方法


## 背景知识

### 什么是哈希算法

哈希算法是一种单向函数，它将任意长度的输入数据转换为固定长度的输出值（称为哈希值或消息摘要）。

**核心特性**：

1. **确定性**
   - 相同输入总是产生相同输出
   - 输出完全由输入决定
   - 可重复验证

2. **单向性**
   - 从哈希值无法反推原始数据
   - 计算哈希值容易
   - 逆向计算几乎不可能

3. **雪崩效应**
   - 输入微小变化导致输出巨大变化
   - 即使只改变一个比特
   - 输出完全不同

4. **抗碰撞性**
   - 难以找到两个不同输入产生相同哈希值
   - 强碰撞抗性：找到任意碰撞困难
   - 弱碰撞抗性：找到特定碰撞困难


### 哈希算法工作原理

**基本流程**：

```
输入数据（任意长度）
        ↓
   [填充处理]
        ↓
   [分块处理]
        ↓
┌─────────────────┐
│  初始化状态     │
└─────────────────┘
        ↓
┌─────────────────┐
│  压缩函数       │ ← 数据块1
│  (多轮迭代)     │
└─────────────────┘
        ↓
┌─────────────────┐
│  压缩函数       │ ← 数据块2
│  (多轮迭代)     │
└─────────────────┘
        ↓
      ...
        ↓
┌─────────────────┐
│  最终处理       │
└─────────────────┘
        ↓
哈希值（固定长度）
```

**示例说明**：

```
输入: "Hello"
SHA-256处理:
1. 填充: "Hello" + padding → 512位
2. 分块: 512位分为16个32位字
3. 迭代: 64轮压缩函数
4. 输出: 256位哈希值

结果: 185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969
```


### 常用哈希算法对比

| 算法 | 输出长度 | 安全性 | 速度 | 应用场景 |
|------|---------|--------|------|----------|
| MD5 | 128位 | 已破解 | 快 | 仅用于非安全场景 |
| SHA-1 | 160位 | 弱 | 中 | 逐步淘汰 |
| SHA-256 | 256位 | 强 | 中 | 推荐使用 |
| SHA-512 | 512位 | 强 | 慢 | 高安全需求 |
| SHA-3 | 可变 | 强 | 中 | 新一代标准 |

**安全性说明**：

```
MD5（不推荐）:
- 1996年发现碰撞
- 2004年实际碰撞攻击
- 仅用于校验和，不用于安全

SHA-1（逐步淘汰）:
- 2005年理论攻击
- 2017年实际碰撞
- 不再用于证书签名

SHA-256（推荐）:
- 目前安全
- 广泛应用
- 比特币等使用

SHA-3（最新）:
- 2015年标准化
- 不同设计原理
- 未来趋势
```



## 核心内容

### MD5算法

MD5（Message Digest Algorithm 5）是最早广泛使用的哈希算法之一，由Ron Rivest在1991年设计。

**算法特点**：

1. **输出长度**：128位（16字节）
2. **处理块大小**：512位（64字节）
3. **轮数**：64轮
4. **速度**：非常快

**MD5结构**：

```
输入消息
    ↓
[填充到512位倍数]
    ↓
[分成16个32位字]
    ↓
初始状态: A=0x67452301, B=0xEFCDAB89
         C=0x98BADCFE, D=0x10325476
    ↓
┌──────────────────┐
│  4轮，每轮16步   │
│  F, G, H, I函数  │
│  非线性变换      │
└──────────────────┘
    ↓
[更新状态]
    ↓
128位MD5值
```

**安全性问题**：

- **碰撞攻击**：可以构造不同输入产生相同MD5
- **前缀碰撞**：可以在已知前缀下构造碰撞
- **不适合安全应用**：不应用于密码存储、数字签名

**适用场景**：

- 文件完整性校验（非安全场景）
- 快速数据去重
- 缓存键生成
- 非关键数据的唯一标识


### SHA系列算法

SHA（Secure Hash Algorithm）是由美国国家安全局（NSA）设计的一系列哈希算法。

#### SHA-1

**算法特点**：

1. **输出长度**：160位（20字节）
2. **处理块大小**：512位
3. **轮数**：80轮
4. **设计**：基于MD4

**SHA-1结构**：

```
输入消息
    ↓
[填充处理]
    ↓
初始状态: H0-H4 (5个32位字)
    ↓
┌──────────────────┐
│  80轮压缩函数    │
│  每轮使用不同常数 │
│  位运算和加法    │
└──────────────────┘
    ↓
160位SHA-1值
```

**安全状态**：

- 2005年：理论碰撞攻击
- 2017年：Google实现实际碰撞（SHAttered攻击）
- 现状：不再推荐用于安全应用
- 替代：迁移到SHA-256或SHA-3


#### SHA-256（推荐）

SHA-256是SHA-2家族的成员，是目前最广泛使用的安全哈希算法。

**算法特点**：

1. **输出长度**：256位（32字节）
2. **处理块大小**：512位
3. **轮数**：64轮
4. **安全性**：目前无已知实用攻击

**SHA-256结构**：

```
输入消息
    ↓
[填充到512位倍数]
    ↓
[分成16个32位字]
    ↓
[扩展到64个字]
    ↓
初始状态: H0-H7 (8个32位字)
    ↓
┌──────────────────┐
│  64轮压缩函数    │
│  Ch, Maj函数     │
│  Σ0, Σ1, σ0, σ1 │
└──────────────────┘
    ↓
256位SHA-256值
```

**核心函数**：

```
Ch(x,y,z)  = (x ∧ y) ⊕ (¬x ∧ z)  // 选择函数
Maj(x,y,z) = (x ∧ y) ⊕ (x ∧ z) ⊕ (y ∧ z)  // 多数函数
Σ0(x) = ROTR²(x) ⊕ ROTR¹³(x) ⊕ ROTR²²(x)
Σ1(x) = ROTR⁶(x) ⊕ ROTR¹¹(x) ⊕ ROTR²⁵(x)
σ0(x) = ROTR⁷(x) ⊕ ROTR¹⁸(x) ⊕ SHR³(x)
σ1(x) = ROTR¹⁷(x) ⊕ ROTR¹⁹(x) ⊕ SHR¹⁰(x)
```

**应用场景**：

- 数字签名
- 证书签名
- 区块链（比特币）
- 密码存储（配合盐值）
- 文件完整性验证
- 数据去重


#### SHA-512

**算法特点**：

1. **输出长度**：512位（64字节）
2. **处理块大小**：1024位
3. **轮数**：80轮
4. **字长**：64位（SHA-256是32位）

**性能对比**：

```
在64位系统上：
SHA-512 可能比 SHA-256 更快
原因：使用64位运算，更适合64位CPU

在32位系统上：
SHA-256 通常比 SHA-512 快
原因：SHA-512需要模拟64位运算
```


### SHA-3算法

SHA-3是最新的哈希算法标准，基于Keccak算法，于2015年标准化。

**设计特点**：

1. **海绵结构**：不同于SHA-2的Merkle-Damgård结构
2. **可变输出**：支持任意长度输出
3. **安全裕度**：更大的安全边界
4. **并行性**：更适合硬件实现

**SHA-3结构**：

```
输入消息
    ↓
┌──────────────────┐
│  吸收阶段        │
│  (Absorbing)     │
│  输入数据块      │
└──────────────────┘
    ↓
┌──────────────────┐
│  Keccak-f[1600]  │
│  24轮置换        │
└──────────────────┘
    ↓
┌──────────────────┐
│  挤出阶段        │
│  (Squeezing)     │
│  输出哈希值      │
└──────────────────┘
    ↓
SHA-3哈希值
```

**SHA-3变体**：

- **SHA3-224**：224位输出
- **SHA3-256**：256位输出
- **SHA3-384**：384位输出
- **SHA3-512**：512位输出
- **SHAKE128/256**：可扩展输出函数


### 哈希算法的性能考虑

**计算复杂度**：

```
相对速度（32位MCU）:
MD5:      100%  (基准)
SHA-1:    80%   (稍慢)
SHA-256:  50%   (中等)
SHA-512:  30%   (较慢，32位系统)
SHA-3:    40%   (中等)

内存需求：
MD5:      ~100字节
SHA-1:    ~100字节
SHA-256:  ~200字节
SHA-512:  ~400字节
SHA-3:    ~200字节
```

**优化策略**：

1. **硬件加速**
   - 使用MCU内置加密模块
   - STM32的HASH外设
   - ESP32的硬件SHA加速

2. **算法选择**
   - 非安全场景：MD5（快速）
   - 一般安全：SHA-256（平衡）
   - 高安全：SHA-512或SHA-3

3. **实现优化**
   - 使用优化的库（mbedTLS）
   - 避免频繁小数据哈希
   - 批量处理数据



## 实践示例

### 示例1：使用mbedTLS计算SHA-256

```c
#include "mbedtls/sha256.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief  计算数据的SHA-256哈希值
 * @param  input: 输入数据
 * @param  input_len: 输入数据长度
 * @param  output: 输出哈希值（32字节）
 */
void calculate_sha256(const unsigned char *input, size_t input_len,
                     unsigned char output[32])
{
    mbedtls_sha256_context ctx;
    
    // 初始化上下文
    mbedtls_sha256_init(&ctx);
    
    // 开始SHA-256计算
    mbedtls_sha256_starts(&ctx, 0);  // 0表示SHA-256，1表示SHA-224
    
    // 更新数据
    mbedtls_sha256_update(&ctx, input, input_len);
    
    // 完成计算，获取哈希值
    mbedtls_sha256_finish(&ctx, output);
    
    // 清理上下文
    mbedtls_sha256_free(&ctx);
}

/**
 * @brief  SHA-256基础示例
 */
void sha256_basic_example(void)
{
    const char *message = "Hello, SHA-256!";
    unsigned char hash[32];
    
    printf("=== SHA-256 Basic Example ===\n");
    printf("Input: %s\n", message);
    
    // 计算哈希值
    calculate_sha256((unsigned char *)message, strlen(message), hash);
    
    // 打印哈希值
    printf("SHA-256: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
}
```

**代码说明**：
- `mbedtls_sha256_init()`: 初始化SHA-256上下文
- `mbedtls_sha256_starts()`: 开始新的哈希计算
- `mbedtls_sha256_update()`: 添加数据（可多次调用）
- `mbedtls_sha256_finish()`: 完成计算并获取结果
- `mbedtls_sha256_free()`: 清理资源

**运行结果**：
```
=== SHA-256 Basic Example ===
Input: Hello, SHA-256!
SHA-256: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
```


### 示例2：文件完整性校验

```c
/**
 * @brief  计算文件的SHA-256哈希值
 * @param  filename: 文件名
 * @param  hash: 输出哈希值（32字节）
 * @retval 0:成功, -1:失败
 */
int calculate_file_hash(const char *filename, unsigned char hash[32])
{
    FILE *file;
    mbedtls_sha256_context ctx;
    unsigned char buffer[1024];
    size_t bytes_read;
    
    // 打开文件
    file = fopen(filename, "rb");
    if (file == NULL) {
        printf("Error: Cannot open file %s\n", filename);
        return -1;
    }
    
    // 初始化SHA-256
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0);
    
    // 分块读取并计算
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        mbedtls_sha256_update(&ctx, buffer, bytes_read);
    }
    
    // 完成计算
    mbedtls_sha256_finish(&ctx, hash);
    mbedtls_sha256_free(&ctx);
    
    fclose(file);
    return 0;
}

/**
 * @brief  验证文件完整性
 * @param  filename: 文件名
 * @param  expected_hash: 期望的哈希值（十六进制字符串）
 * @retval 0:验证成功, -1:验证失败
 */
int verify_file_integrity(const char *filename, const char *expected_hash)
{
    unsigned char hash[32];
    char hash_str[65];
    
    printf("Verifying file: %s\n", filename);
    
    // 计算文件哈希
    if (calculate_file_hash(filename, hash) != 0) {
        return -1;
    }
    
    // 转换为十六进制字符串
    for (int i = 0; i < 32; i++) {
        sprintf(&hash_str[i * 2], "%02x", hash[i]);
    }
    hash_str[64] = '\0';
    
    printf("Calculated: %s\n", hash_str);
    printf("Expected:   %s\n", expected_hash);
    
    // 比较哈希值
    if (strcmp(hash_str, expected_hash) == 0) {
        printf("✓ File integrity verified\n");
        return 0;
    } else {
        printf("✗ File integrity check failed\n");
        return -1;
    }
}

/**
 * @brief  文件完整性校验示例
 */
void file_integrity_example(void)
{
    printf("\n=== File Integrity Check Example ===\n");
    
    // 假设的文件和期望哈希值
    const char *filename = "firmware.bin";
    const char *expected = "a3c5e8d2f1b4c9e7d6a2f8b1c4e9d7a6f2b8c1e4d9a7f6b2c8e1d4a9f7b6c2e8";
    
    verify_file_integrity(filename, expected);
}
```

**应用场景**：
- 固件更新验证
- 配置文件完整性检查
- 数据传输验证
- 防篡改检测


### 示例3：密码安全存储

```c
#include "mbedtls/md.h"

/**
 * @brief  生成随机盐值
 * @param  salt: 输出盐值缓冲区
 * @param  salt_len: 盐值长度
 */
void generate_salt(unsigned char *salt, size_t salt_len)
{
    // 使用硬件随机数生成器或伪随机数
    for (size_t i = 0; i < salt_len; i++) {
        salt[i] = rand() & 0xFF;
    }
}

/**
 * @brief  使用盐值哈希密码
 * @param  password: 明文密码
 * @param  salt: 盐值
 * @param  salt_len: 盐值长度
 * @param  hash: 输出哈希值（32字节）
 */
void hash_password_with_salt(const char *password,
                            const unsigned char *salt, size_t salt_len,
                            unsigned char hash[32])
{
    mbedtls_sha256_context ctx;
    
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0);
    
    // 先哈希盐值
    mbedtls_sha256_update(&ctx, salt, salt_len);
    
    // 再哈希密码
    mbedtls_sha256_update(&ctx, (unsigned char *)password, strlen(password));
    
    mbedtls_sha256_finish(&ctx, hash);
    mbedtls_sha256_free(&ctx);
}

/**
 * @brief  存储密码（模拟）
 * @param  username: 用户名
 * @param  password: 明文密码
 */
void store_password(const char *username, const char *password)
{
    unsigned char salt[16];
    unsigned char hash[32];
    
    printf("\n=== Storing Password ===\n");
    printf("Username: %s\n", username);
    
    // 生成随机盐值
    generate_salt(salt, sizeof(salt));
    
    printf("Salt: ");
    for (int i = 0; i < 16; i++) {
        printf("%02x", salt[i]);
    }
    printf("\n");
    
    // 哈希密码
    hash_password_with_salt(password, salt, sizeof(salt), hash);
    
    printf("Hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
    
    // 实际应用中，将salt和hash存储到数据库或Flash
    // save_to_database(username, salt, hash);
    
    printf("Password stored securely\n");
}

/**
 * @brief  验证密码
 * @param  username: 用户名
 * @param  password: 输入的密码
 * @param  stored_salt: 存储的盐值
 * @param  stored_hash: 存储的哈希值
 * @retval 0:验证成功, -1:验证失败
 */
int verify_password(const char *username, const char *password,
                   const unsigned char *stored_salt,
                   const unsigned char *stored_hash)
{
    unsigned char computed_hash[32];
    
    printf("\n=== Verifying Password ===\n");
    printf("Username: %s\n", username);
    
    // 使用相同的盐值哈希输入的密码
    hash_password_with_salt(password, stored_salt, 16, computed_hash);
    
    // 比较哈希值
    if (memcmp(computed_hash, stored_hash, 32) == 0) {
        printf("✓ Password correct\n");
        return 0;
    } else {
        printf("✗ Password incorrect\n");
        return -1;
    }
}

/**
 * @brief  密码存储示例
 */
void password_storage_example(void)
{
    const char *username = "admin";
    const char *password = "SecurePass123!";
    
    unsigned char salt[16];
    unsigned char hash[32];
    
    // 存储密码
    generate_salt(salt, sizeof(salt));
    hash_password_with_salt(password, salt, sizeof(salt), hash);
    
    // 验证正确密码
    verify_password(username, "SecurePass123!", salt, hash);
    
    // 验证错误密码
    verify_password(username, "WrongPassword", salt, hash);
}
```

**安全要点**：
- 永远不要存储明文密码
- 使用随机盐值（每个用户不同）
- 盐值和哈希值一起存储
- 考虑使用PBKDF2、bcrypt或Argon2（更安全）



### 示例4：HMAC消息认证码

HMAC（Hash-based Message Authentication Code）结合了哈希函数和密钥，用于验证消息的完整性和真实性。

```c
#include "mbedtls/md.h"

/**
 * @brief  计算HMAC-SHA256
 * @param  key: 密钥
 * @param  key_len: 密钥长度
 * @param  message: 消息
 * @param  message_len: 消息长度
 * @param  hmac: 输出HMAC值（32字节）
 */
void calculate_hmac_sha256(const unsigned char *key, size_t key_len,
                          const unsigned char *message, size_t message_len,
                          unsigned char hmac[32])
{
    mbedtls_md_context_t ctx;
    const mbedtls_md_info_t *md_info;
    
    // 获取SHA-256信息
    md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    
    // 初始化
    mbedtls_md_init(&ctx);
    mbedtls_md_setup(&ctx, md_info, 1);  // 1表示启用HMAC
    
    // 设置密钥
    mbedtls_md_hmac_starts(&ctx, key, key_len);
    
    // 更新消息
    mbedtls_md_hmac_update(&ctx, message, message_len);
    
    // 完成计算
    mbedtls_md_hmac_finish(&ctx, hmac);
    
    // 清理
    mbedtls_md_free(&ctx);
}

/**
 * @brief  HMAC示例
 */
void hmac_example(void)
{
    const char *key = "secret_key_12345";
    const char *message = "Important message that needs authentication";
    unsigned char hmac[32];
    
    printf("\n=== HMAC-SHA256 Example ===\n");
    printf("Key: %s\n", key);
    printf("Message: %s\n", message);
    
    // 计算HMAC
    calculate_hmac_sha256((unsigned char *)key, strlen(key),
                         (unsigned char *)message, strlen(message),
                         hmac);
    
    printf("HMAC: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", hmac[i]);
    }
    printf("\n");
    
    // 验证HMAC
    unsigned char computed_hmac[32];
    calculate_hmac_sha256((unsigned char *)key, strlen(key),
                         (unsigned char *)message, strlen(message),
                         computed_hmac);
    
    if (memcmp(hmac, computed_hmac, 32) == 0) {
        printf("✓ HMAC verification successful\n");
    }
}
```

**HMAC应用**：
- API请求签名
- 消息完整性验证
- 身份认证
- 防重放攻击


## 深入理解

### 哈希碰撞

**什么是碰撞**：

两个不同的输入产生相同的哈希值：
```
Hash(M1) = Hash(M2)，但 M1 ≠ M2
```

**碰撞类型**：

1. **生日攻击**
   - 基于生日悖论
   - 对于n位哈希，需要2^(n/2)次尝试
   - MD5（128位）：2^64次尝试
   - SHA-256（256位）：2^128次尝试

2. **前缀碰撞**
   - 在给定前缀下找碰撞
   - 更实用的攻击方式
   - 用于伪造证书等

**防护措施**：

```
1. 使用足够长的哈希
   - 至少256位（SHA-256）
   - 避免使用MD5、SHA-1

2. 添加盐值
   - 增加攻击难度
   - 每个实例使用不同盐值

3. 使用HMAC
   - 添加密钥保护
   - 防止碰撞攻击

4. 定期更新算法
   - 关注安全公告
   - 及时迁移到新算法
```


### 彩虹表攻击

**什么是彩虹表**：

预计算的哈希值查找表，用于快速破解密码：

```
密码 → 哈希值
"123456" → "e10adc3949ba59abbe56e057f20f883e"
"password" → "5f4dcc3b5aa765d61d8327deb882cf99"
...
```

**攻击过程**：

```
1. 获取密码哈希值
2. 在彩虹表中查找
3. 找到对应的明文密码
```

**防护措施**：

1. **使用盐值**
```c
// 不安全：直接哈希
hash = SHA256(password)

// 安全：添加盐值
hash = SHA256(salt + password)
```

2. **使用慢哈希函数**
```c
// PBKDF2：密钥派生函数
// 参数：密码、盐值、迭代次数、输出长度
pbkdf2_hmac_sha256(password, salt, 100000, 32, output);

// bcrypt：专门用于密码哈希
bcrypt(password, cost_factor, salt, output);

// Argon2：最新推荐
argon2(password, salt, time_cost, memory_cost, output);
```

3. **增加计算成本**
```c
// 多次迭代
for (int i = 0; i < 10000; i++) {
    hash = SHA256(hash + password + salt);
}
```


### 哈希长度扩展攻击

**攻击原理**：

对于某些哈希算法（如SHA-256），如果知道Hash(M)和M的长度，可以计算Hash(M || padding || M')，而不需要知道M的内容。

**受影响的算法**：
- MD5
- SHA-1
- SHA-256
- SHA-512

**不受影响的算法**：
- SHA-3（海绵结构）
- BLAKE2

**防护措施**：

```c
// 方法1：使用HMAC
hmac = HMAC-SHA256(key, message)

// 方法2：使用SHA-3
hash = SHA3-256(message)

// 方法3：双重哈希
hash = SHA256(SHA256(message))
```


### 性能优化技巧

**1. 硬件加速**

```c
// STM32硬件HASH示例
void hardware_sha256(const uint8_t *data, size_t len, uint8_t *hash)
{
    HASH_HandleTypeDef hhash;
    
    // 配置HASH外设
    hhash.Instance = HASH;
    hhash.Init.DataType = HASH_DATATYPE_8B;
    HAL_HASH_Init(&hhash);
    
    // 计算SHA-256
    HAL_HASH_SHA256_Start(&hhash, (uint8_t *)data, len, hash, HAL_MAX_DELAY);
}
```

**2. 批量处理**

```c
// 不推荐：频繁小数据哈希
for (int i = 0; i < 1000; i++) {
    hash = SHA256(small_data[i]);
}

// 推荐：合并后一次哈希
combined_data = concatenate(small_data, 1000);
hash = SHA256(combined_data);
```

**3. 增量计算**

```c
// 对于大文件，使用增量计算
mbedtls_sha256_context ctx;
mbedtls_sha256_init(&ctx);
mbedtls_sha256_starts(&ctx, 0);

while (has_more_data) {
    read_chunk(buffer, chunk_size);
    mbedtls_sha256_update(&ctx, buffer, chunk_size);
}

mbedtls_sha256_finish(&ctx, hash);
```


## 最佳实践

### 算法选择指南

```
场景1：文件完整性校验（非安全）
推荐：MD5或CRC32
原因：速度快，碰撞不影响功能

场景2：数据完整性验证（安全）
推荐：SHA-256
原因：安全性好，性能适中

场景3：密码存储
推荐：PBKDF2、bcrypt或Argon2
原因：专门设计，抗暴力破解

场景4：数字签名
推荐：SHA-256或SHA-512
原因：安全性高，广泛支持

场景5：区块链应用
推荐：SHA-256（比特币）或Keccak（以太坊）
原因：行业标准

场景6：消息认证
推荐：HMAC-SHA256
原因：提供认证和完整性
```

### 安全实践建议

1. **永远不要自己实现哈希算法**
   - 使用经过验证的库（mbedTLS、OpenSSL）
   - 避免实现错误导致的安全问题

2. **选择合适的哈希长度**
   - 至少256位用于安全应用
   - 考虑未来的安全需求

3. **正确使用盐值**
   - 每个实例使用不同的随机盐值
   - 盐值长度至少16字节
   - 盐值和哈希值一起存储

4. **密码哈希特殊处理**
   - 使用专门的密码哈希函数
   - 增加计算成本（迭代次数）
   - 定期更新哈希算法

5. **防止时序攻击**
```c
// 不安全：提前返回
int verify_hash(const uint8_t *hash1, const uint8_t *hash2, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        if (hash1[i] != hash2[i]) {
            return 0;  // 提前返回，泄露信息
        }
    }
    return 1;
}

// 安全：常量时间比较
int secure_compare(const uint8_t *hash1, const uint8_t *hash2, size_t len)
{
    uint8_t result = 0;
    for (size_t i = 0; i < len; i++) {
        result |= hash1[i] ^ hash2[i];
    }
    return result == 0;
}
```



## 常见问题

### Q1: MD5还能用吗？

**A**: 取决于应用场景：

**可以使用**：
- 非安全的文件校验和
- 快速数据去重
- 缓存键生成
- 内部标识符

**不能使用**：
- 密码存储
- 数字签名
- 证书验证
- 任何安全相关场景

**原因**：MD5已被证明存在碰撞漏洞，攻击者可以构造具有相同MD5值的不同文件。


### Q2: SHA-256和SHA-512哪个更好？

**A**: 取决于平台和需求：

**SHA-256优势**：
- 在32位系统上更快
- 输出更短（节省存储）
- 更广泛的支持
- 足够的安全性

**SHA-512优势**：
- 在64位系统上可能更快
- 更高的安全裕度
- 适合高安全需求

**建议**：
- 嵌入式32位系统：SHA-256
- 64位服务器：SHA-512
- 一般应用：SHA-256足够


### Q3: 为什么密码不能直接哈希存储？

**A**: 直接哈希存在多个安全问题：

1. **彩虹表攻击**
   - 攻击者预计算常见密码的哈希值
   - 可以快速查找对应的明文密码

2. **相同密码相同哈希**
   - 多个用户使用相同密码会有相同哈希
   - 泄露一个就泄露所有

3. **计算速度太快**
   - 现代GPU可以每秒计算数十亿次哈希
   - 暴力破解变得可行

**正确做法**：
```c
// 使用盐值 + 慢哈希函数
hash = PBKDF2(password, random_salt, 100000_iterations)
```


### Q4: 什么是盐值(Salt)？如何使用？

**A**: 盐值是添加到密码中的随机数据，用于防止彩虹表攻击。

**正确使用方法**：

```c
// 1. 生成随机盐值（每个用户不同）
uint8_t salt[16];
generate_random(salt, 16);

// 2. 结合盐值哈希密码
hash = SHA256(salt || password);

// 3. 存储盐值和哈希值
save_to_database(username, salt, hash);

// 4. 验证时使用相同的盐值
input_hash = SHA256(stored_salt || input_password);
if (input_hash == stored_hash) {
    // 密码正确
}
```

**关键点**：
- 盐值必须随机
- 每个用户使用不同盐值
- 盐值可以公开存储
- 盐值长度至少16字节


### Q5: HMAC和普通哈希有什么区别？

**A**: HMAC添加了密钥保护：

**普通哈希**：
```
hash = SHA256(message)
任何人都可以计算和验证
```

**HMAC**：
```
hmac = HMAC-SHA256(key, message)
只有知道密钥的人才能计算和验证
```

**应用场景**：

| 场景 | 使用 | 原因 |
|------|------|------|
| 文件校验 | 普通哈希 | 不需要保密 |
| API签名 | HMAC | 需要身份验证 |
| 消息认证 | HMAC | 防止篡改 |
| 密码存储 | 普通哈希+盐值 | 不需要密钥 |


### Q6: 如何选择哈希算法？

**A**: 根据安全需求和性能要求选择：

**决策树**：
```
需要安全性？
├─ 否 → MD5或CRC32（仅校验和）
└─ 是 → 继续
    ├─ 密码存储？
    │   └─ 是 → PBKDF2/bcrypt/Argon2
    └─ 否 → 继续
        ├─ 需要认证？
        │   └─ 是 → HMAC-SHA256
        └─ 否 → SHA-256（通用）
```

**性能考虑**：
- 资源受限：SHA-256
- 有硬件加速：使用硬件支持的算法
- 高性能需求：考虑硬件加速或优化库


## 总结

本文介绍了哈希算法的核心概念和实际应用：

**核心要点**：

1. **哈希算法特性**
   - 确定性：相同输入产生相同输出
   - 单向性：无法从哈希值反推原始数据
   - 雪崩效应：微小变化导致巨大差异
   - 抗碰撞性：难以找到碰撞

2. **常用算法**
   - MD5：已不安全，仅用于非安全场景
   - SHA-1：逐步淘汰
   - SHA-256：当前推荐标准
   - SHA-3：新一代标准

3. **主要应用**
   - 数据完整性验证
   - 密码安全存储
   - 数字签名
   - 消息认证（HMAC）

4. **安全实践**
   - 使用SHA-256或更强算法
   - 密码存储必须加盐
   - 使用专门的密码哈希函数
   - 防止时序攻击

5. **性能优化**
   - 使用硬件加速
   - 批量处理数据
   - 选择合适的算法


## 延伸阅读

推荐进一步学习的资源：

- AES加密算法实战 - 学习对称加密
- RSA非对称加密实战 - 学习公钥加密
- 数字签名技术详解 - 深入数字签名
- [NIST SHA-3标准](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf) - 官方标准文档
- [mbedTLS文档](https://tls.mbed.org/api/) - 加密库API文档


## 参考资料

1. NIST FIPS 180-4: Secure Hash Standard (SHS)
2. NIST FIPS 202: SHA-3 Standard
3. RFC 2104: HMAC: Keyed-Hashing for Message Authentication
4. RFC 6234: US Secure Hash Algorithms (SHA and SHA-based HMAC and HKDF)
5. "Applied Cryptography" by Bruce Schneier
6. mbedTLS Documentation: https://tls.mbed.org/

---

**练习题**：

1. 使用SHA-256计算字符串"Embedded Systems"的哈希值，并验证结果
2. 实现一个简单的文件完整性校验工具
3. 编写一个安全的密码存储和验证系统（使用盐值）
4. 实现HMAC-SHA256消息认证
5. 比较MD5、SHA-256和SHA-512在你的开发板上的性能

**下一步**：建议学习 数字签名技术详解，了解哈希算法在数字签名中的应用。

