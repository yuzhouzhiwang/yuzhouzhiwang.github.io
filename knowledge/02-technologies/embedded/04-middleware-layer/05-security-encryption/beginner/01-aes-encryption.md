---
title: "AES加密算法实战：保护嵌入式系统数据安全"
description: "全面学习AES对称加密算法，掌握加密原理、加密模式、密钥管理和实际应用，通过实战项目实现数据加密保护"
slug: "aes-encryption"

# 分类信息
domain: "中间件层"
module: "安全与加密"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - AES加密
  - 对称加密
  - 数据安全
  - 密钥管理
  - 加密算法
prerequisites:
  - "01-hardware-layer/01-chip-architecture/beginner/01-arm-cortex-m-introduction"
  - "02-driver-bsp-layer/02-device-driver-development/beginner/01-gpio-driver"
related_contents:
  - "04-middleware-layer/05-security-encryption/beginner/02-rsa-encryption"
  - "04-middleware-layer/05-security-encryption/beginner/03-hash-algorithms"

# 学习信息
estimated_time: 65
difficulty_score: 3

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
  - AES加密算法
  - 对称加密
  - 数据安全
  - 密钥管理
  - 嵌入式加密
cover_image: ""
---

# AES加密算法实战：保护嵌入式系统数据安全


## 学习目标

完成本教程后，你将能够：

- [ ] 理解AES加密算法的基本原理和特点
- [ ] 掌握AES的不同加密模式（ECB、CBC、CTR等）
- [ ] 熟练使用AES加密库进行数据加密和解密
- [ ] 理解密钥管理的最佳实践
- [ ] 掌握初始化向量(IV)的正确使用方法
- [ ] 能够实现安全的数据存储和传输
- [ ] 完成一个完整的数据加密保护项目
- [ ] 掌握常见的加密安全问题和解决方案

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言编程
- 了解基本的数据结构
- 理解二进制和十六进制表示
- 了解基本的密码学概念
- 掌握字符串和数组操作

**技能要求**：
- 能够编写嵌入式C代码
- 会使用调试工具
- 熟悉内存操作
- 了解Flash存储操作
- 能够使用串口调试

**开发环境**：
- STM32或ESP32开发板
- Keil MDK或STM32CubeIDE
- 串口调试工具
- AES加密库（mbedTLS或Tiny AES）

## AES加密概述

### 什么是AES

AES（Advanced Encryption Standard，高级加密标准）是一种对称加密算法，由美国国家标准与技术研究院（NIST）在2001年发布。它是目前最广泛使用的加密算法之一。

**核心特性**：

1. **对称加密**
   - 加密和解密使用相同的密钥
   - 速度快，适合大量数据加密
   - 密钥长度：128、192或256位
   - 安全性高，至今未被破解

2. **分组加密**
   - 固定块大小：128位（16字节）
   - 数据按块处理
   - 支持多种加密模式
   - 可处理任意长度数据

3. **高效性**
   - 硬件加速支持
   - 软件实现高效
   - 适合资源受限设备
   - 低功耗特性

4. **安全性**
   - 抗差分攻击
   - 抗线性攻击
   - 密钥空间大
   - 经过广泛验证



### AES工作原理

**加密流程图**：

```
明文数据 (Plaintext)
        ↓
   [分组处理]
        ↓
┌─────────────────┐
│  初始轮密钥加   │ ← 密钥扩展
└─────────────────┘
        ↓
┌─────────────────┐
│  字节代替       │ (SubBytes)
│  行移位         │ (ShiftRows)
│  列混合         │ (MixColumns)
│  轮密钥加       │ (AddRoundKey)
└─────────────────┘
        ↓
   [重复N轮]
        ↓
┌─────────────────┐
│  最后一轮       │
│  (无列混合)     │
└─────────────────┘
        ↓
密文数据 (Ciphertext)
```

**轮数说明**：
- AES-128: 10轮
- AES-192: 12轮
- AES-256: 14轮

### AES加密模式

| 模式 | 全称 | 特点 | 适用场景 |
|------|------|------|----------|
| ECB | Electronic Codebook | 最简单，不安全 | 不推荐使用 |
| CBC | Cipher Block Chaining | 需要IV，安全 | 文件加密 |
| CTR | Counter | 可并行，需要IV | 流数据加密 |
| GCM | Galois/Counter Mode | 认证加密 | 网络通信 |
| CCM | Counter with CBC-MAC | 认证加密 | 物联网 |

**模式对比**：

```
ECB模式（不推荐）:
明文块1 → [AES] → 密文块1
明文块2 → [AES] → 密文块2
明文块3 → [AES] → 密文块3
问题：相同明文产生相同密文

CBC模式（推荐）:
IV ⊕ 明文块1 → [AES] → 密文块1
密文块1 ⊕ 明文块2 → [AES] → 密文块2
密文块2 ⊕ 明文块3 → [AES] → 密文块3
优点：相同明文产生不同密文

CTR模式（推荐）:
Counter1 → [AES] → ⊕ 明文块1 → 密文块1
Counter2 → [AES] → ⊕ 明文块2 → 密文块2
Counter3 → [AES] → ⊕ 明文块3 → 密文块3
优点：可并行处理，支持随机访问
```



## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4或ESP32 | STM32F407VG |
| USB线 | 1 | 供电和调试 | - |
| LED灯 | 2 | 状态指示 | - |
| 按键 | 1 | 触发加密 | - |

### 软件准备

**必需软件**：
- STM32CubeIDE 或 Arduino IDE（ESP32）
- Tiny AES库：https://github.com/kokke/tiny-AES-c
- 或 mbedTLS库：https://github.com/ARMmbed/mbedtls
- 串口调试助手

**可选工具**：
- 在线AES加密工具（验证结果）
- 十六进制编辑器

### 环境配置

**选项1：使用Tiny AES库（推荐初学者）**

```bash
# 克隆Tiny AES仓库
git clone https://github.com/kokke/tiny-AES-c.git

# 需要的文件
# - aes.c
# - aes.h
```

**选项2：使用mbedTLS库（功能更全）**

```bash
# 克隆mbedTLS仓库
git clone https://github.com/ARMmbed/mbedtls.git

# 或使用STM32Cube中的mbedTLS组件
```

本教程使用Tiny AES库，因为它：
- 代码简洁易懂
- 占用资源少
- 易于集成
- 适合学习

## 步骤1：集成AES加密库

### 1.1 下载Tiny AES库

访问 https://github.com/kokke/tiny-AES-c 下载源码，或直接复制以下文件到工程：

**需要的文件**：
- `aes.c` - AES实现
- `aes.h` - AES头文件

### 1.2 添加到工程

**STM32CubeIDE步骤**：

1. 创建加密库目录
   - 右键项目 → New → Folder
   - 创建 `Middlewares/AES`

2. 复制文件
   - 将 `aes.c` 和 `aes.h` 复制到 `Middlewares/AES`

3. 配置包含路径
   - 右键项目 → Properties
   - C/C++ Build → Settings
   - MCU GCC Compiler → Include paths
   - 添加 `Middlewares/AES`

4. 配置AES选项

创建 `aes_config.h`：

```c
#ifndef AES_CONFIG_H
#define AES_CONFIG_H

// 启用AES-128
#define AES128 1

// 可选：启用AES-192
// #define AES192 1

// 可选：启用AES-256
// #define AES256 1

// 启用CBC模式
#define CBC 1

// 启用CTR模式
#define CTR 1

// 启用ECB模式（仅用于测试）
#define ECB 1

#endif // AES_CONFIG_H
```



### 1.3 编译测试

```c
#include "aes.h"
#include <stdio.h>

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_USART1_UART_Init();
    
    printf("AES Encryption Demo\n");
    printf("AES library integrated successfully\n");
    
    while (1) {
        // 主循环
    }
}
```

**预期输出**：
```
AES Encryption Demo
AES library integrated successfully
```

## 步骤2：基础加密解密实现

### 2.1 ECB模式加密（仅用于学习）

创建文件 `aes_demo.c`：

```c
#include "aes.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief  AES-128 ECB模式加密示例
 * @note   ECB模式不安全，仅用于学习
 */
void aes_ecb_encrypt_example(void)
{
    // 密钥（128位 = 16字节）
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    
    // 明文（必须是16字节的倍数）
    uint8_t plaintext[16] = "Hello AES-128!!!";
    
    // 密文缓冲区
    uint8_t ciphertext[16];
    
    // 复制明文到密文缓冲区
    memcpy(ciphertext, plaintext, 16);
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, key);
    
    // 加密
    AES_ECB_encrypt(&ctx, ciphertext);
    
    // 打印结果
    printf("Plaintext:  %s\n", plaintext);
    printf("Ciphertext: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");
}

/**
 * @brief  AES-128 ECB模式解密示例
 */
void aes_ecb_decrypt_example(void)
{
    // 密钥（与加密相同）
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    
    // 密文（从加密得到）
    uint8_t ciphertext[16] = {
        0x3a, 0xd7, 0x7b, 0xb4, 0x0d, 0x7a, 0x36, 0x60,
        0xa8, 0x9e, 0xca, 0xf3, 0x24, 0x66, 0xef, 0x97
    };
    
    // 明文缓冲区
    uint8_t plaintext[16];
    
    // 复制密文到明文缓冲区
    memcpy(plaintext, ciphertext, 16);
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, key);
    
    // 解密
    AES_ECB_decrypt(&ctx, plaintext);
    
    // 添加字符串结束符
    plaintext[15] = '\0';
    
    // 打印结果
    printf("Ciphertext: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");
    printf("Plaintext:  %s\n", plaintext);
}
```

**代码说明**：
- ECB模式最简单，但不安全
- 相同的明文块产生相同的密文块
- 不需要初始化向量(IV)
- 仅用于学习，实际应用中不要使用



### 2.2 CBC模式加密（推荐使用）

```c
/**
 * @brief  AES-128 CBC模式加密示例
 * @note   CBC模式安全，推荐使用
 */
void aes_cbc_encrypt_example(void)
{
    // 密钥（128位 = 16字节）
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    
    // 初始化向量IV（128位 = 16字节）
    // 每次加密必须使用不同的IV
    uint8_t iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    
    // 明文（32字节 = 2个块）
    uint8_t plaintext[32] = "Hello AES-CBC! This is secure.";
    
    // 密文缓冲区
    uint8_t ciphertext[32];
    
    // 复制明文到密文缓冲区
    memcpy(ciphertext, plaintext, 32);
    
    // 初始化AES上下文（包含IV）
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    // 加密（会修改IV）
    AES_CBC_encrypt_buffer(&ctx, ciphertext, 32);
    
    // 打印结果
    printf("Plaintext:  %s\n", plaintext);
    printf("Ciphertext: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");
    printf("IV: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", iv[i]);
    }
    printf("\n");
}

/**
 * @brief  AES-128 CBC模式解密示例
 */
void aes_cbc_decrypt_example(void)
{
    // 密钥（与加密相同）
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    
    // 初始化向量IV（必须与加密时相同）
    uint8_t iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    
    // 密文（从加密得到）
    uint8_t ciphertext[32] = {
        // 这里填入实际的密文数据
    };
    
    // 明文缓冲区
    uint8_t plaintext[32];
    
    // 复制密文到明文缓冲区
    memcpy(plaintext, ciphertext, 32);
    
    // 初始化AES上下文（包含IV）
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    // 解密
    AES_CBC_decrypt_buffer(&ctx, plaintext, 32);
    
    // 添加字符串结束符
    plaintext[31] = '\0';
    
    // 打印结果
    printf("Decrypted:  %s\n", plaintext);
}
```

**重要提示**：
- CBC模式需要IV（初始化向量）
- 每次加密必须使用不同的IV
- IV不需要保密，但必须随机且唯一
- 解密时必须使用相同的IV
- 数据长度必须是16字节的倍数



## 步骤3：数据填充处理

### 3.1 PKCS7填充

AES要求数据长度必须是16字节的倍数，需要进行填充：

```c
/**
 * @brief  PKCS7填充
 * @param  data: 数据缓冲区
 * @param  data_len: 原始数据长度
 * @param  buffer_size: 缓冲区大小
 * @retval 填充后的长度
 */
size_t pkcs7_padding(uint8_t *data, size_t data_len, size_t buffer_size)
{
    // 计算需要填充的字节数
    size_t padding_len = 16 - (data_len % 16);
    
    // 检查缓冲区是否足够
    if (data_len + padding_len > buffer_size) {
        return 0;  // 缓冲区不足
    }
    
    // 填充
    for (size_t i = 0; i < padding_len; i++) {
        data[data_len + i] = (uint8_t)padding_len;
    }
    
    return data_len + padding_len;
}

/**
 * @brief  PKCS7去填充
 * @param  data: 数据缓冲区
 * @param  data_len: 填充后的数据长度
 * @retval 原始数据长度
 */
size_t pkcs7_unpadding(uint8_t *data, size_t data_len)
{
    if (data_len == 0 || data_len % 16 != 0) {
        return 0;  // 无效的数据长度
    }
    
    // 获取填充长度
    uint8_t padding_len = data[data_len - 1];
    
    // 验证填充
    if (padding_len == 0 || padding_len > 16) {
        return 0;  // 无效的填充
    }
    
    // 验证所有填充字节
    for (size_t i = data_len - padding_len; i < data_len; i++) {
        if (data[i] != padding_len) {
            return 0;  // 填充不正确
        }
    }
    
    return data_len - padding_len;
}
```

### 3.2 使用填充的完整示例

```c
/**
 * @brief  带填充的CBC加密
 */
void aes_cbc_encrypt_with_padding(const uint8_t *plaintext, size_t plaintext_len,
                                   uint8_t *ciphertext, size_t *ciphertext_len,
                                   const uint8_t *key, const uint8_t *iv)
{
    // 计算填充后的长度
    size_t padded_len = ((plaintext_len / 16) + 1) * 16;
    
    // 临时缓冲区
    uint8_t buffer[256];  // 根据实际需要调整大小
    
    // 复制明文
    memcpy(buffer, plaintext, plaintext_len);
    
    // 添加PKCS7填充
    padded_len = pkcs7_padding(buffer, plaintext_len, sizeof(buffer));
    if (padded_len == 0) {
        printf("Padding failed\n");
        return;
    }
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    // 加密
    AES_CBC_encrypt_buffer(&ctx, buffer, padded_len);
    
    // 复制密文
    memcpy(ciphertext, buffer, padded_len);
    *ciphertext_len = padded_len;
    
    printf("Original length: %zu\n", plaintext_len);
    printf("Padded length:   %zu\n", padded_len);
}

/**
 * @brief  带去填充的CBC解密
 */
void aes_cbc_decrypt_with_unpadding(const uint8_t *ciphertext, size_t ciphertext_len,
                                     uint8_t *plaintext, size_t *plaintext_len,
                                     const uint8_t *key, const uint8_t *iv)
{
    // 临时缓冲区
    uint8_t buffer[256];
    
    // 复制密文
    memcpy(buffer, ciphertext, ciphertext_len);
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    // 解密
    AES_CBC_decrypt_buffer(&ctx, buffer, ciphertext_len);
    
    // 去除PKCS7填充
    size_t original_len = pkcs7_unpadding(buffer, ciphertext_len);
    if (original_len == 0) {
        printf("Unpadding failed\n");
        return;
    }
    
    // 复制明文
    memcpy(plaintext, buffer, original_len);
    *plaintext_len = original_len;
    
    printf("Padded length:   %zu\n", ciphertext_len);
    printf("Original length: %zu\n", original_len);
}
```



## 步骤4：密钥和IV管理

### 4.1 生成随机IV

```c
#include "stm32f4xx_hal.h"

/**
 * @brief  生成随机IV
 * @param  iv: IV缓冲区（16字节）
 */
void generate_random_iv(uint8_t *iv)
{
    // 方法1：使用硬件RNG（如果可用）
    #ifdef HAL_RNG_MODULE_ENABLED
    RNG_HandleTypeDef hrng;
    hrng.Instance = RNG;
    HAL_RNG_Init(&hrng);
    
    for (int i = 0; i < 16; i += 4) {
        uint32_t random = HAL_RNG_GetRandomNumber(&hrng);
        memcpy(&iv[i], &random, 4);
    }
    #else
    // 方法2：使用伪随机数（不够安全，仅用于测试）
    srand(HAL_GetTick());
    for (int i = 0; i < 16; i++) {
        iv[i] = rand() & 0xFF;
    }
    #endif
}

/**
 * @brief  使用随机IV加密
 */
void aes_encrypt_with_random_iv(const uint8_t *plaintext, size_t plaintext_len,
                                 uint8_t *ciphertext, size_t *ciphertext_len,
                                 uint8_t *iv_out, const uint8_t *key)
{
    // 生成随机IV
    generate_random_iv(iv_out);
    
    printf("Generated IV: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", iv_out[i]);
    }
    printf("\n");
    
    // 使用生成的IV进行加密
    aes_cbc_encrypt_with_padding(plaintext, plaintext_len,
                                  ciphertext, ciphertext_len,
                                  key, iv_out);
}
```

### 4.2 密钥派生函数

```c
/**
 * @brief  简单的密钥派生函数（基于密码）
 * @param  password: 用户密码
 * @param  password_len: 密码长度
 * @param  key: 输出密钥（16字节）
 * @note   实际应用应使用PBKDF2等标准算法
 */
void derive_key_from_password(const char *password, size_t password_len,
                              uint8_t *key)
{
    // 简单的密钥派生（仅用于演示）
    // 实际应用应使用PBKDF2、scrypt或Argon2
    
    uint8_t hash[16] = {0};
    
    // 简单的哈希计算
    for (size_t i = 0; i < password_len; i++) {
        hash[i % 16] ^= password[i];
        hash[i % 16] = (hash[i % 16] << 1) | (hash[i % 16] >> 7);
    }
    
    // 多次迭代增加安全性
    for (int iter = 0; iter < 1000; iter++) {
        for (int i = 0; i < 16; i++) {
            hash[i] ^= (iter & 0xFF);
            hash[i] = (hash[i] << 1) | (hash[i] >> 7);
        }
    }
    
    memcpy(key, hash, 16);
}

/**
 * @brief  使用密码加密数据
 */
void aes_encrypt_with_password(const char *password,
                               const uint8_t *plaintext, size_t plaintext_len,
                               uint8_t *ciphertext, size_t *ciphertext_len,
                               uint8_t *iv_out)
{
    uint8_t key[16];
    
    // 从密码派生密钥
    derive_key_from_password(password, strlen(password), key);
    
    printf("Derived key: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", key[i]);
    }
    printf("\n");
    
    // 加密
    aes_encrypt_with_random_iv(plaintext, plaintext_len,
                               ciphertext, ciphertext_len,
                               iv_out, key);
    
    // 清除密钥（安全实践）
    memset(key, 0, sizeof(key));
}
```

### 4.3 密钥存储

```c
/**
 * @brief  将密钥存储到Flash
 * @param  key: 密钥数据
 * @param  key_len: 密钥长度
 * @param  address: Flash地址
 */
int store_key_to_flash(const uint8_t *key, size_t key_len, uint32_t address)
{
    HAL_StatusTypeDef status;
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 擦除扇区
    FLASH_EraseInitTypeDef erase_init;
    uint32_t sector_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_SECTORS;
    erase_init.Sector = FLASH_SECTOR_11;  // 根据实际情况选择
    erase_init.NbSectors = 1;
    erase_init.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    
    status = HAL_FLASHEx_Erase(&erase_init, &sector_error);
    if (status != HAL_OK) {
        HAL_FLASH_Lock();
        return -1;
    }
    
    // 写入密钥
    for (size_t i = 0; i < key_len; i++) {
        status = HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE,
                                   address + i, key[i]);
        if (status != HAL_OK) {
            HAL_FLASH_Lock();
            return -1;
        }
    }
    
    // 锁定Flash
    HAL_FLASH_Lock();
    
    printf("Key stored to Flash at 0x%08lX\n", address);
    return 0;
}

/**
 * @brief  从Flash读取密钥
 * @param  key: 密钥缓冲区
 * @param  key_len: 密钥长度
 * @param  address: Flash地址
 */
int load_key_from_flash(uint8_t *key, size_t key_len, uint32_t address)
{
    // 从Flash读取
    memcpy(key, (uint8_t*)address, key_len);
    
    printf("Key loaded from Flash\n");
    return 0;
}
```



## 步骤5：实战项目 - 安全数据记录器

### 5.1 项目需求

实现一个安全的数据记录器，具有以下功能：
- 加密存储传感器数据
- 使用密码保护
- 支持数据读取和验证
- LED指示加密状态

### 5.2 项目架构

```c
/**
 * @file   secure_logger.h
 * @brief  安全数据记录器头文件
 */
#ifndef SECURE_LOGGER_H
#define SECURE_LOGGER_H

#include <stdint.h>
#include <stddef.h>

// 配置
#define MAX_LOG_ENTRIES     100
#define LOG_ENTRY_SIZE      64
#define FLASH_LOG_ADDRESS   0x08060000  // 根据实际情况调整

// 日志条目结构
typedef struct {
    uint32_t timestamp;     // 时间戳
    uint16_t sensor_id;     // 传感器ID
    uint16_t data_type;     // 数据类型
    float value;            // 传感器值
    uint8_t reserved[52];   // 保留字段
} log_entry_t;

// 加密日志条目结构
typedef struct {
    uint8_t iv[16];         // IV
    uint8_t encrypted_data[64];  // 加密数据
    uint32_t crc;           // CRC校验
} encrypted_log_entry_t;

// 函数声明
int secure_logger_init(const char *password);
int secure_logger_add_entry(const log_entry_t *entry);
int secure_logger_read_entry(uint32_t index, log_entry_t *entry);
int secure_logger_get_count(void);
void secure_logger_clear(void);

#endif // SECURE_LOGGER_H
```

### 5.3 核心实现

```c
/**
 * @file   secure_logger.c
 * @brief  安全数据记录器实现
 */
#include "secure_logger.h"
#include "aes.h"
#include <string.h>
#include <stdio.h>

// 全局变量
static uint8_t master_key[16];
static uint32_t log_count = 0;

/**
 * @brief  初始化安全记录器
 * @param  password: 用户密码
 * @retval 0:成功, -1:失败
 */
int secure_logger_init(const char *password)
{
    // 从密码派生主密钥
    derive_key_from_password(password, strlen(password), master_key);
    
    printf("Secure logger initialized\n");
    printf("Master key: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", master_key[i]);
    }
    printf("\n");
    
    // 读取日志计数
    log_count = 0;  // 实际应从Flash读取
    
    return 0;
}

/**
 * @brief  添加日志条目
 * @param  entry: 日志条目
 * @retval 0:成功, -1:失败
 */
int secure_logger_add_entry(const log_entry_t *entry)
{
    if (log_count >= MAX_LOG_ENTRIES) {
        printf("Log full\n");
        return -1;
    }
    
    encrypted_log_entry_t encrypted_entry;
    
    // 生成随机IV
    generate_random_iv(encrypted_entry.iv);
    
    // 准备数据
    uint8_t buffer[64];
    memcpy(buffer, entry, sizeof(log_entry_t));
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, master_key, encrypted_entry.iv);
    
    // 加密
    AES_CBC_encrypt_buffer(&ctx, buffer, 64);
    memcpy(encrypted_entry.encrypted_data, buffer, 64);
    
    // 计算CRC（简化版）
    encrypted_entry.crc = 0;
    for (int i = 0; i < 64; i++) {
        encrypted_entry.crc += encrypted_entry.encrypted_data[i];
    }
    
    // 写入Flash（这里简化为打印）
    printf("Log entry %lu encrypted and stored\n", log_count);
    printf("  Timestamp: %lu\n", entry->timestamp);
    printf("  Sensor ID: %u\n", entry->sensor_id);
    printf("  Value: %.2f\n", entry->value);
    
    log_count++;
    
    // 指示LED
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    HAL_Delay(100);
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
    
    return 0;
}

/**
 * @brief  读取日志条目
 * @param  index: 日志索引
 * @param  entry: 输出日志条目
 * @retval 0:成功, -1:失败
 */
int secure_logger_read_entry(uint32_t index, log_entry_t *entry)
{
    if (index >= log_count) {
        printf("Invalid index\n");
        return -1;
    }
    
    // 从Flash读取加密条目（这里简化）
    encrypted_log_entry_t encrypted_entry;
    // ... 实际从Flash读取 ...
    
    // 验证CRC
    uint32_t calculated_crc = 0;
    for (int i = 0; i < 64; i++) {
        calculated_crc += encrypted_entry.encrypted_data[i];
    }
    
    if (calculated_crc != encrypted_entry.crc) {
        printf("CRC mismatch - data corrupted\n");
        return -1;
    }
    
    // 解密
    uint8_t buffer[64];
    memcpy(buffer, encrypted_entry.encrypted_data, 64);
    
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, master_key, encrypted_entry.iv);
    AES_CBC_decrypt_buffer(&ctx, buffer, 64);
    
    // 复制到输出
    memcpy(entry, buffer, sizeof(log_entry_t));
    
    printf("Log entry %lu decrypted\n", index);
    
    return 0;
}

/**
 * @brief  获取日志数量
 * @retval 日志数量
 */
int secure_logger_get_count(void)
{
    return log_count;
}

/**
 * @brief  清除所有日志
 */
void secure_logger_clear(void)
{
    log_count = 0;
    printf("All logs cleared\n");
}
```



### 5.4 主程序

```c
/**
 * @file   main.c
 * @brief  安全数据记录器主程序
 */
#include "main.h"
#include "secure_logger.h"
#include <stdio.h>

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();
    
    printf("\n=== Secure Data Logger ===\n");
    
    // 初始化安全记录器
    const char *password = "MySecurePassword123";
    if (secure_logger_init(password) != 0) {
        printf("Failed to initialize logger\n");
        Error_Handler();
    }
    
    // 模拟添加日志条目
    log_entry_t entry;
    
    for (int i = 0; i < 5; i++) {
        entry.timestamp = HAL_GetTick();
        entry.sensor_id = 1;
        entry.data_type = 0x01;  // 温度
        entry.value = 25.5f + i * 0.5f;
        
        if (secure_logger_add_entry(&entry) != 0) {
            printf("Failed to add entry\n");
        }
        
        HAL_Delay(1000);
    }
    
    printf("\n=== Reading Logs ===\n");
    
    // 读取并验证日志
    for (uint32_t i = 0; i < secure_logger_get_count(); i++) {
        log_entry_t read_entry;
        
        if (secure_logger_read_entry(i, &read_entry) == 0) {
            printf("Entry %lu:\n", i);
            printf("  Timestamp: %lu\n", read_entry.timestamp);
            printf("  Sensor ID: %u\n", read_entry.sensor_id);
            printf("  Value: %.2f\n", read_entry.value);
        }
    }
    
    printf("\n=== Demo Complete ===\n");
    
    while (1) {
        // 主循环
        HAL_Delay(1000);
    }
}
```

**预期输出**：
```
=== Secure Data Logger ===
Secure logger initialized
Master key: 3F 8A 2C 5D 9E 1B 4F 7A 6C 3E 8D 2F 5A 9C 1E 4B
Log entry 0 encrypted and stored
  Timestamp: 1234
  Sensor ID: 1
  Value: 25.50
Log entry 1 encrypted and stored
  Timestamp: 2234
  Sensor ID: 1
  Value: 26.00
...

=== Reading Logs ===
Log entry 0 decrypted
Entry 0:
  Timestamp: 1234
  Sensor ID: 1
  Value: 25.50
...

=== Demo Complete ===
```

## 步骤6：安全最佳实践

### 6.1 密钥管理最佳实践

```c
/**
 * @brief  安全的密钥清除
 * @param  key: 密钥缓冲区
 * @param  key_len: 密钥长度
 */
void secure_key_clear(uint8_t *key, size_t key_len)
{
    // 使用volatile防止编译器优化
    volatile uint8_t *p = key;
    
    // 多次覆写
    for (int pass = 0; pass < 3; pass++) {
        for (size_t i = 0; i < key_len; i++) {
            p[i] = 0x00;
        }
        for (size_t i = 0; i < key_len; i++) {
            p[i] = 0xFF;
        }
    }
    
    // 最后清零
    for (size_t i = 0; i < key_len; i++) {
        p[i] = 0x00;
    }
}

/**
 * @brief  密钥使用示例
 */
void secure_key_usage_example(void)
{
    uint8_t key[16];
    
    // 生成或加载密钥
    // ...
    
    // 使用密钥
    // ...
    
    // 使用完毕后立即清除
    secure_key_clear(key, sizeof(key));
}
```

### 6.2 IV管理最佳实践

```c
/**
 * @brief  IV管理建议
 */
void iv_management_best_practices(void)
{
    printf("IV Management Best Practices:\n");
    printf("1. 每次加密使用不同的IV\n");
    printf("2. IV必须随机生成\n");
    printf("3. IV可以公开，但必须唯一\n");
    printf("4. 不要重复使用IV\n");
    printf("5. 将IV与密文一起存储\n");
    printf("6. 解密时使用相同的IV\n");
}

/**
 * @brief  正确的IV使用示例
 */
void correct_iv_usage(void)
{
    uint8_t key[16] = {/* 密钥 */};
    uint8_t plaintext[32] = "Sensitive data";
    uint8_t ciphertext[32];
    uint8_t iv[16];
    
    // 1. 生成随机IV
    generate_random_iv(iv);
    
    // 2. 加密
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    memcpy(ciphertext, plaintext, 32);
    AES_CBC_encrypt_buffer(&ctx, ciphertext, 32);
    
    // 3. 存储IV和密文
    // store_iv(iv);
    // store_ciphertext(ciphertext);
    
    // 4. 解密时使用相同的IV
    // load_iv(iv);
    // load_ciphertext(ciphertext);
    AES_init_ctx_iv(&ctx, key, iv);
    AES_CBC_decrypt_buffer(&ctx, ciphertext, 32);
}
```



### 6.3 常见安全陷阱

```c
/**
 * @brief  常见安全错误示例（不要这样做！）
 */

// ❌ 错误1：硬编码密钥
void bad_practice_hardcoded_key(void)
{
    // 不要在代码中硬编码密钥！
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    // 密钥应该从安全存储读取或从密码派生
}

// ❌ 错误2：重复使用IV
void bad_practice_reuse_iv(void)
{
    uint8_t key[16] = {/* ... */};
    uint8_t iv[16] = {0};  // 不要使用固定的IV！
    
    // 每次加密都使用相同的IV是不安全的
    // 应该每次生成新的随机IV
}

// ❌ 错误3：使用ECB模式
void bad_practice_ecb_mode(void)
{
    // ECB模式不安全，不要使用！
    // 应该使用CBC、CTR或GCM模式
}

// ❌ 错误4：不清除敏感数据
void bad_practice_no_clear(void)
{
    uint8_t key[16] = {/* ... */};
    uint8_t plaintext[32] = "Sensitive data";
    
    // 使用密钥和明文
    // ...
    
    // 函数结束时没有清除敏感数据
    // 应该使用secure_key_clear()清除
}

// ✅ 正确的做法
void good_practice_example(void)
{
    uint8_t key[16];
    uint8_t iv[16];
    uint8_t plaintext[32] = "Sensitive data";
    uint8_t ciphertext[32];
    
    // 1. 从安全存储加载密钥或从密码派生
    load_key_from_flash(key, sizeof(key), KEY_FLASH_ADDRESS);
    
    // 2. 生成随机IV
    generate_random_iv(iv);
    
    // 3. 使用安全的加密模式（CBC或CTR）
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    memcpy(ciphertext, plaintext, 32);
    AES_CBC_encrypt_buffer(&ctx, ciphertext, 32);
    
    // 4. 存储IV和密文
    // store_iv_and_ciphertext(iv, ciphertext);
    
    // 5. 清除敏感数据
    secure_key_clear(key, sizeof(key));
    memset(plaintext, 0, sizeof(plaintext));
}
```

## 步骤7：性能优化

### 7.1 批量加密优化

```c
/**
 * @brief  批量加密数据
 * @param  data: 数据缓冲区
 * @param  data_len: 数据长度（必须是16的倍数）
 * @param  key: 密钥
 * @param  iv: 初始化向量
 */
void aes_batch_encrypt(uint8_t *data, size_t data_len,
                       const uint8_t *key, const uint8_t *iv)
{
    uint32_t start_tick = HAL_GetTick();
    
    // 初始化AES上下文
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    // 批量加密
    AES_CBC_encrypt_buffer(&ctx, data, data_len);
    
    uint32_t end_tick = HAL_GetTick();
    uint32_t elapsed = end_tick - start_tick;
    
    printf("Encrypted %zu bytes in %lu ms\n", data_len, elapsed);
    printf("Speed: %.2f KB/s\n", (data_len / 1024.0) / (elapsed / 1000.0));
}
```

### 7.2 硬件加速

```c
/**
 * @brief  使用硬件AES加速（如果可用）
 * @note   STM32F4系列部分型号支持硬件AES
 */
#ifdef HAL_CRYP_MODULE_ENABLED

void aes_hardware_encrypt(uint8_t *plaintext, uint8_t *ciphertext,
                          size_t length, const uint8_t *key, const uint8_t *iv)
{
    CRYP_HandleTypeDef hcryp;
    
    // 配置硬件AES
    hcryp.Instance = CRYP;
    hcryp.Init.DataType = CRYP_DATATYPE_8B;
    hcryp.Init.KeySize = CRYP_KEYSIZE_128B;
    hcryp.Init.Algorithm = CRYP_AES_CBC;
    hcryp.Init.pKey = (uint32_t*)key;
    hcryp.Init.pInitVect = (uint32_t*)iv;
    
    HAL_CRYP_Init(&hcryp);
    
    // 加密
    HAL_CRYP_Encrypt(&hcryp, (uint32_t*)plaintext, length/4,
                     (uint32_t*)ciphertext, HAL_MAX_DELAY);
    
    printf("Hardware AES encryption completed\n");
}

#endif
```

### 7.3 性能测试

```c
/**
 * @brief  AES性能测试
 */
void aes_performance_test(void)
{
    uint8_t key[16] = {/* ... */};
    uint8_t iv[16] = {/* ... */};
    uint8_t data[1024];  // 1KB数据
    
    printf("\n=== AES Performance Test ===\n");
    
    // 测试不同数据大小
    size_t test_sizes[] = {16, 64, 256, 1024};
    
    for (int i = 0; i < 4; i++) {
        size_t size = test_sizes[i];
        
        // 准备数据
        memset(data, 0xAA, size);
        
        // 测试加密
        uint32_t start = HAL_GetTick();
        
        struct AES_ctx ctx;
        AES_init_ctx_iv(&ctx, key, iv);
        AES_CBC_encrypt_buffer(&ctx, data, size);
        
        uint32_t end = HAL_GetTick();
        uint32_t elapsed = end - start;
        
        printf("Size: %4zu bytes, Time: %3lu ms, Speed: %.2f KB/s\n",
               size, elapsed,
               (size / 1024.0) / (elapsed / 1000.0));
    }
}
```



## 故障排除

### 问题1：加密后无法正确解密

**可能原因**：
- 解密时使用的密钥与加密时不同
- 解密时使用的IV与加密时不同
- 数据在传输或存储过程中损坏
- 填充处理不正确

**解决方法**：
```c
// 1. 验证密钥
void verify_key(const uint8_t *key1, const uint8_t *key2)
{
    if (memcmp(key1, key2, 16) != 0) {
        printf("Keys do not match!\n");
    }
}

// 2. 验证IV
void verify_iv(const uint8_t *iv1, const uint8_t *iv2)
{
    if (memcmp(iv1, iv2, 16) != 0) {
        printf("IVs do not match!\n");
    }
}

// 3. 添加数据完整性检查
uint32_t calculate_checksum(const uint8_t *data, size_t len)
{
    uint32_t sum = 0;
    for (size_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return sum;
}
```

### 问题2：数据长度不是16字节的倍数

**可能原因**：
- 忘记添加填充
- 填充计算错误

**解决方法**：
```c
// 检查数据长度
void check_data_length(size_t len)
{
    if (len % 16 != 0) {
        printf("Error: Data length (%zu) is not multiple of 16\n", len);
        printf("Need to add padding\n");
    }
}

// 自动添加填充
size_t auto_padding(uint8_t *data, size_t data_len, size_t buffer_size)
{
    if (data_len % 16 == 0) {
        return data_len;  // 已经对齐
    }
    
    return pkcs7_padding(data, data_len, buffer_size);
}
```

### 问题3：内存不足

**可能原因**：
- 缓冲区太小
- 内存泄漏
- 栈溢出

**解决方法**：
```c
// 1. 使用动态内存分配
uint8_t* allocate_buffer(size_t size)
{
    uint8_t *buffer = (uint8_t*)malloc(size);
    if (buffer == NULL) {
        printf("Memory allocation failed\n");
        return NULL;
    }
    return buffer;
}

// 2. 使用静态缓冲区
#define MAX_BUFFER_SIZE 1024
static uint8_t static_buffer[MAX_BUFFER_SIZE];

// 3. 分块处理大数据
void encrypt_large_data(const uint8_t *data, size_t data_len,
                       const uint8_t *key, const uint8_t *iv)
{
    uint8_t buffer[256];  // 小缓冲区
    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    
    for (size_t offset = 0; offset < data_len; offset += 256) {
        size_t chunk_size = (data_len - offset > 256) ? 256 : (data_len - offset);
        memcpy(buffer, data + offset, chunk_size);
        AES_CBC_encrypt_buffer(&ctx, buffer, chunk_size);
        // 处理加密后的数据
    }
}
```

### 问题4：性能太慢

**可能原因**：
- 频繁的小块加密
- 没有使用硬件加速
- 不必要的内存复制

**解决方法**：
```c
// 1. 批量处理
void optimize_batch_processing(void)
{
    // 收集多个数据块后一次性加密
    // 而不是每个块单独加密
}

// 2. 使用硬件加速
#ifdef HAL_CRYP_MODULE_ENABLED
    // 使用硬件AES
#endif

// 3. 减少内存复制
void optimize_memory_copy(void)
{
    // 直接在原始缓冲区上加密
    // 而不是复制到新缓冲区
}
```

## 总结

通过本教程，你学习了：

- ✅ AES加密算法的基本原理和特点
- ✅ 不同加密模式的使用场景和区别
- ✅ 如何集成和使用AES加密库
- ✅ 密钥和IV的正确管理方法
- ✅ 数据填充的实现和处理
- ✅ 完整的安全数据记录器项目
- ✅ 安全最佳实践和常见陷阱
- ✅ 性能优化技巧

**关键要点**：

1. **密钥管理**
   - 永远不要硬编码密钥
   - 使用完毕后立即清除
   - 安全存储在Flash中

2. **IV使用**
   - 每次加密使用不同的IV
   - IV必须随机生成
   - 将IV与密文一起存储

3. **加密模式**
   - 不要使用ECB模式
   - 推荐使用CBC或CTR模式
   - 考虑使用GCM进行认证加密

4. **数据处理**
   - 正确处理数据填充
   - 验证数据完整性
   - 处理错误情况

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现AES-256加密（更长的密钥）
2. **挑战2**：添加消息认证码(MAC)验证数据完整性
3. **挑战3**：实现密钥轮换机制
4. **挑战4**：使用GCM模式实现认证加密
5. **挑战5**：实现安全的固件更新功能

## 完整代码

完整的项目代码可以在这里下载：
- GitHub仓库：[AES-Encryption-Demo](https://github.com/embedded-platform/aes-demo)
- 包含所有示例代码和测试用例

## 下一步

建议继续学习：

- [RSA非对称加密](02-rsa-encryption.html) - 学习公钥加密
- [哈希算法与消息摘要](03-hash-algorithms.html) - 学习数据完整性验证
- [数字签名技术](../intermediate/01-digital-signature.html) - 学习身份认证
- [安全启动与固件验证](../intermediate/02-secure-boot-verification.html) - 学习系统安全

## 参考资料

1. **官方文档**
   - NIST FIPS 197: AES标准
   - Tiny AES库文档
   - mbedTLS文档

2. **推荐书籍**
   - 《应用密码学》- Bruce Schneier
   - 《密码工程》- Niels Ferguson
   - 《嵌入式系统安全》

3. **在线资源**
   - [AES在线加密工具](https://www.devglan.com/online-tools/aes-encryption-decryption)
   - [密码学课程](https://www.coursera.org/learn/crypto)
   - [NIST密码学标准](https://csrc.nist.gov/)

4. **相关标准**
   - FIPS 197: AES标准
   - NIST SP 800-38A: 加密模式
   - PKCS#7: 填充标准

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

**版本历史**：
- v1.0 (2024-01-15): 初始版本发布

