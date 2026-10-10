---
title: "RSA非对称加密实战：公钥密码学入门"
description: "全面学习RSA非对称加密算法，掌握公钥加密原理、密钥对生成、数字签名和实际应用，通过实战项目实现安全通信"
slug: "rsa-encryption"

# 分类信息
domain: "中间件层"
module: "安全与加密"
content_type: "tutorial"
skill_level: "beginner"

# 标签和关联
tags:
  - RSA加密
  - 非对称加密
  - 公钥加密
  - 数字签名
  - 密钥对
prerequisites:
  - "04-middleware-layer/05-security-encryption/beginner/01-aes-encryption"
  - "01-hardware-layer/01-chip-architecture/beginner/01-arm-cortex-m-introduction"
related_contents:
  - "04-middleware-layer/05-security-encryption/beginner/03-hash-algorithms"
  - "04-middleware-layer/05-security-encryption/intermediate/01-digital-signature"

# 学习信息
estimated_time: 70
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
  - RSA加密算法
  - 非对称加密
  - 公钥密码学
  - 数字签名
  - 嵌入式安全
cover_image: ""
---

# RSA非对称加密实战：公钥密码学入门


## 学习目标

完成本教程后，你将能够：

- [ ] 理解RSA非对称加密的基本原理和数学基础
- [ ] 掌握公钥和私钥的概念及其应用场景
- [ ] 熟练使用RSA库进行密钥对生成
- [ ] 掌握RSA加密和解密的实现方法
- [ ] 理解数字签名的原理和实现
- [ ] 能够实现安全的密钥交换机制
- [ ] 完成一个完整的安全通信项目
- [ ] 掌握RSA与AES的混合加密方案

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉C语言编程
- 了解基本的密码学概念
- 理解对称加密原理（建议先学习AES）
- 了解二进制和十六进制表示
- 掌握基本的数学概念（模运算、质数）

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
- mbedTLS库或Tiny RSA库


## RSA加密概述

### 什么是RSA

RSA是一种非对称加密算法，由Ron Rivest、Adi Shamir和Leonard Adleman在1977年提出。它是目前应用最广泛的公钥加密算法。

**核心特性**：

1. **非对称加密**
   - 使用公钥加密，私钥解密
   - 公钥可以公开，私钥必须保密
   - 加密和解密使用不同的密钥
   - 安全性基于大数分解难题

2. **密钥对**
   - 公钥(Public Key)：用于加密和验证签名
   - 私钥(Private Key)：用于解密和生成签名
   - 密钥长度：1024、2048或4096位
   - 密钥对数学上相关但无法互推

3. **应用场景**
   - 密钥交换：安全传输对称密钥
   - 数字签名：验证身份和完整性
   - 身份认证：证明身份
   - 安全通信：建立加密通道

4. **安全性**
   - 基于大数分解难题
   - 2048位密钥目前安全
   - 计算量大，速度较慢
   - 通常与对称加密混合使用


### RSA工作原理

**加密解密流程图**：

```
密钥生成阶段：
┌─────────────────┐
│  选择两个大质数  │
│    p 和 q       │
└─────────────────┘
        ↓
┌─────────────────┐
│  计算 n = p × q │
│  φ(n)=(p-1)(q-1)│
└─────────────────┘
        ↓
┌─────────────────┐
│  选择公钥指数 e  │
│  计算私钥指数 d  │
└─────────────────┘
        ↓
┌─────────────────┐
│ 公钥: (n, e)    │
│ 私钥: (n, d)    │
└─────────────────┘

加密阶段：
明文 M → C = M^e mod n → 密文 C

解密阶段：
密文 C → M = C^d mod n → 明文 M
```

**数学原理**：

1. **密钥生成**
   - 选择两个大质数 p 和 q
   - 计算 n = p × q（模数）
   - 计算 φ(n) = (p-1) × (q-1)（欧拉函数）
   - 选择公钥指数 e，满足 1 < e < φ(n) 且 gcd(e, φ(n)) = 1
   - 计算私钥指数 d，满足 d × e ≡ 1 (mod φ(n))

2. **加密过程**
   - 密文 C = M^e mod n
   - M 是明文（必须 < n）
   - e 和 n 是公钥

3. **解密过程**
   - 明文 M = C^d mod n
   - C 是密文
   - d 和 n 是私钥


### RSA vs AES对比

| 特性 | RSA（非对称） | AES（对称） |
|------|--------------|------------|
| 密钥类型 | 公钥+私钥 | 单一密钥 |
| 加密速度 | 慢（100-1000倍） | 快 |
| 密钥长度 | 2048-4096位 | 128-256位 |
| 数据量 | 小数据（<密钥长度） | 任意大小 |
| 密钥分发 | 公钥可公开 | 密钥需保密传输 |
| 主要用途 | 密钥交换、签名 | 数据加密 |
| 计算复杂度 | 高 | 低 |
| 资源消耗 | 大 | 小 |

**混合加密方案**：

```
实际应用中的最佳实践：

1. 使用RSA加密AES密钥
   ┌──────────┐
   │ AES密钥  │
   └──────────┘
        ↓ RSA公钥加密
   ┌──────────┐
   │ 加密密钥 │ → 传输
   └──────────┘
        ↓ RSA私钥解密
   ┌──────────┐
   │ AES密钥  │
   └──────────┘

2. 使用AES加密实际数据
   ┌──────────┐
   │ 大量数据 │
   └──────────┘
        ↓ AES加密
   ┌──────────┐
   │ 加密数据 │ → 传输
   └──────────┘
        ↓ AES解密
   ┌──────────┐
   │ 原始数据 │
   └──────────┘

优点：
- 结合两者优势
- RSA保护密钥安全
- AES提供高效加密
- 适合大数据传输
```

## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4或ESP32 | STM32F407VG |
| USB线 | 1 | 供电和调试 | - |
| LED灯 | 2 | 状态指示 | - |

### 软件准备

**必需软件**：
- STM32CubeIDE 或 Arduino IDE（ESP32）
- mbedTLS库：https://github.com/ARMmbed/mbedtls
- 或 Tiny RSA库（简化版）
- 串口调试助手

**可选工具**：
- OpenSSL（生成和验证密钥）
- 在线RSA工具（验证结果）

### 环境配置

**使用mbedTLS库（推荐）**

```bash
# 克隆mbedTLS仓库
git clone https://github.com/ARMmbed/mbedtls.git

# 需要的文件
# - library/rsa.c
# - library/bignum.c
# - library/pk.c
# - include/mbedtls/*.h
```

**配置说明**：

1. 将mbedTLS源码添加到工程
2. 配置包含路径
3. 启用必要的模块

创建 `mbedtls_config.h`：

```c
#ifndef MBEDTLS_CONFIG_H
#define MBEDTLS_CONFIG_H

// 启用RSA
#define MBEDTLS_RSA_C
#define MBEDTLS_BIGNUM_C
#define MBEDTLS_PK_C

// 启用随机数生成器
#define MBEDTLS_ENTROPY_C
#define MBEDTLS_CTR_DRBG_C

// 启用哈希算法（RSA需要）
#define MBEDTLS_SHA256_C
#define MBEDTLS_MD_C

// 密钥长度
#define MBEDTLS_MPI_MAX_SIZE 1024

#endif // MBEDTLS_CONFIG_H
```


## 步骤1：生成RSA密钥对

### 1.1 初始化随机数生成器

RSA密钥生成需要高质量的随机数：

```c
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/rsa.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief  初始化随机数生成器
 * @param  entropy: 熵源上下文
 * @param  ctr_drbg: 随机数生成器上下文
 * @retval 0:成功, 其他:失败
 */
int init_random_generator(mbedtls_entropy_context *entropy,
                         mbedtls_ctr_drbg_context *ctr_drbg)
{
    int ret;
    const char *pers = "rsa_keygen";
    
    // 初始化熵源
    mbedtls_entropy_init(entropy);
    
    // 初始化随机数生成器
    mbedtls_ctr_drbg_init(ctr_drbg);
    
    // 种子化随机数生成器
    ret = mbedtls_ctr_drbg_seed(ctr_drbg, mbedtls_entropy_func, entropy,
                                (const unsigned char *)pers, strlen(pers));
    if (ret != 0) {
        printf("Failed to seed random generator: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Random generator initialized\n");
    return 0;
}
```

### 1.2 生成密钥对

```c
/**
 * @brief  生成RSA密钥对
 * @param  rsa: RSA上下文
 * @param  ctr_drbg: 随机数生成器
 * @param  key_size: 密钥长度（位），推荐2048
 * @param  exponent: 公钥指数，通常使用65537
 * @retval 0:成功, 其他:失败
 */
int generate_rsa_keypair(mbedtls_rsa_context *rsa,
                        mbedtls_ctr_drbg_context *ctr_drbg,
                        unsigned int key_size,
                        int exponent)
{
    int ret;
    
    // 初始化RSA上下文
    mbedtls_rsa_init(rsa, MBEDTLS_RSA_PKCS_V15, 0);
    
    printf("Generating %d-bit RSA key pair...\n", key_size);
    printf("This may take a while...\n");
    
    uint32_t start_time = HAL_GetTick();
    
    // 生成密钥对
    ret = mbedtls_rsa_gen_key(rsa, mbedtls_ctr_drbg_random, ctr_drbg,
                             key_size, exponent);
    
    uint32_t end_time = HAL_GetTick();
    
    if (ret != 0) {
        printf("Failed to generate key pair: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Key pair generated successfully\n");
    printf("Time taken: %lu ms\n", end_time - start_time);
    
    return 0;
}
```

**代码说明**：
- `key_size`: 密钥长度，2048位是当前推荐值
- `exponent`: 公钥指数，65537是标准值
- 密钥生成是计算密集型操作，可能需要几秒钟
- 生成时间取决于MCU性能和密钥长度

### 1.3 导出密钥

```c
/**
 * @brief  导出公钥（PEM格式）
 * @param  rsa: RSA上下文
 * @param  buf: 输出缓冲区
 * @param  buf_len: 缓冲区长度
 * @retval 0:成功, 其他:失败
 */
int export_public_key(mbedtls_rsa_context *rsa, char *buf, size_t buf_len)
{
    int ret;
    mbedtls_pk_context pk;
    
    mbedtls_pk_init(&pk);
    mbedtls_pk_setup(&pk, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    
    // 关联RSA上下文
    mbedtls_rsa_context *rsa_ctx = mbedtls_pk_rsa(pk);
    mbedtls_rsa_copy(rsa_ctx, rsa);
    
    // 导出公钥
    ret = mbedtls_pk_write_pubkey_pem(&pk, (unsigned char *)buf, buf_len);
    
    mbedtls_pk_free(&pk);
    
    if (ret != 0) {
        printf("Failed to export public key: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Public key exported:\n%s\n", buf);
    return 0;
}

/**
 * @brief  导出私钥（PEM格式）
 * @param  rsa: RSA上下文
 * @param  buf: 输出缓冲区
 * @param  buf_len: 缓冲区长度
 * @retval 0:成功, 其他:失败
 */
int export_private_key(mbedtls_rsa_context *rsa, char *buf, size_t buf_len)
{
    int ret;
    mbedtls_pk_context pk;
    
    mbedtls_pk_init(&pk);
    mbedtls_pk_setup(&pk, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    
    // 关联RSA上下文
    mbedtls_rsa_context *rsa_ctx = mbedtls_pk_rsa(pk);
    mbedtls_rsa_copy(rsa_ctx, rsa);
    
    // 导出私钥
    ret = mbedtls_pk_write_key_pem(&pk, (unsigned char *)buf, buf_len);
    
    mbedtls_pk_free(&pk);
    
    if (ret != 0) {
        printf("Failed to export private key: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Private key exported (keep it secret!)\n");
    return 0;
}
```

### 1.4 完整示例

```c
/**
 * @brief  密钥生成完整示例
 */
void rsa_keygen_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    char pub_key_buf[1024];
    char priv_key_buf[2048];
    
    // 初始化随机数生成器
    if (init_random_generator(&entropy, &ctr_drbg) != 0) {
        return;
    }
    
    // 生成2048位密钥对
    if (generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537) != 0) {
        goto cleanup;
    }
    
    // 导出公钥
    export_public_key(&rsa, pub_key_buf, sizeof(pub_key_buf));
    
    // 导出私钥（注意：私钥必须保密！）
    export_private_key(&rsa, priv_key_buf, sizeof(priv_key_buf));
    
    // 可以将密钥保存到Flash
    // save_key_to_flash(pub_key_buf, priv_key_buf);
    
cleanup:
    // 清理资源
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
Random generator initialized
Generating 2048-bit RSA key pair...
This may take a while...
Key pair generated successfully
Time taken: 3542 ms
Public key exported:
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
Private key exported (keep it secret!)
```


## 步骤2：RSA加密和解密

### 2.1 公钥加密

```c
/**
 * @brief  使用公钥加密数据
 * @param  rsa: RSA上下文（包含公钥）
 * @param  plaintext: 明文数据
 * @param  plaintext_len: 明文长度
 * @param  ciphertext: 密文缓冲区
 * @param  ctr_drbg: 随机数生成器
 * @retval 0:成功, 其他:失败
 */
int rsa_public_encrypt(mbedtls_rsa_context *rsa,
                      const unsigned char *plaintext, size_t plaintext_len,
                      unsigned char *ciphertext,
                      mbedtls_ctr_drbg_context *ctr_drbg)
{
    int ret;
    
    // 检查数据长度
    size_t max_len = mbedtls_rsa_get_len(rsa) - 11;  // PKCS#1 v1.5填充
    if (plaintext_len > max_len) {
        printf("Error: Data too long (%zu bytes, max %zu bytes)\n",
               plaintext_len, max_len);
        return -1;
    }
    
    printf("Encrypting %zu bytes with public key...\n", plaintext_len);
    
    // 使用公钥加密
    ret = mbedtls_rsa_pkcs1_encrypt(rsa, mbedtls_ctr_drbg_random, ctr_drbg,
                                   MBEDTLS_RSA_PUBLIC,
                                   plaintext_len, plaintext, ciphertext);
    
    if (ret != 0) {
        printf("Encryption failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Encryption successful\n");
    printf("Ciphertext (%zu bytes): ", mbedtls_rsa_get_len(rsa));
    for (size_t i = 0; i < mbedtls_rsa_get_len(rsa); i++) {
        printf("%02X ", ciphertext[i]);
    }
    printf("\n");
    
    return 0;
}
```

**重要提示**：
- RSA加密的数据长度有限制
- 对于2048位密钥，最大明文长度约为245字节
- 超过限制需要分块或使用混合加密

### 2.2 私钥解密

```c
/**
 * @brief  使用私钥解密数据
 * @param  rsa: RSA上下文（包含私钥）
 * @param  ciphertext: 密文数据
 * @param  plaintext: 明文缓冲区
 * @param  plaintext_len: 输出明文长度
 * @retval 0:成功, 其他:失败
 */
int rsa_private_decrypt(mbedtls_rsa_context *rsa,
                       const unsigned char *ciphertext,
                       unsigned char *plaintext, size_t *plaintext_len)
{
    int ret;
    
    printf("Decrypting with private key...\n");
    
    // 使用私钥解密
    ret = mbedtls_rsa_pkcs1_decrypt(rsa, NULL, NULL,
                                   MBEDTLS_RSA_PRIVATE,
                                   plaintext_len, ciphertext,
                                   plaintext, 256);
    
    if (ret != 0) {
        printf("Decryption failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Decryption successful\n");
    printf("Plaintext (%zu bytes): %.*s\n",
           *plaintext_len, (int)*plaintext_len, plaintext);
    
    return 0;
}
```

### 2.3 完整加密解密示例

```c
/**
 * @brief  RSA加密解密完整示例
 */
void rsa_encrypt_decrypt_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    
    // 明文数据
    const char *message = "Hello RSA! This is a secret message.";
    size_t message_len = strlen(message);
    
    // 密文缓冲区（大小为密钥长度）
    unsigned char ciphertext[256];  // 2048位 = 256字节
    
    // 解密后的明文缓冲区
    unsigned char decrypted[256];
    size_t decrypted_len;
    
    printf("\n=== RSA Encryption/Decryption Demo ===\n");
    printf("Original message: %s\n", message);
    printf("Message length: %zu bytes\n\n", message_len);
    
    // 初始化
    init_random_generator(&entropy, &ctr_drbg);
    
    // 生成密钥对
    if (generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537) != 0) {
        goto cleanup;
    }
    
    // 加密
    if (rsa_public_encrypt(&rsa, (unsigned char *)message, message_len,
                          ciphertext, &ctr_drbg) != 0) {
        goto cleanup;
    }
    
    printf("\n");
    
    // 解密
    if (rsa_private_decrypt(&rsa, ciphertext, decrypted, &decrypted_len) != 0) {
        goto cleanup;
    }
    
    // 验证
    if (decrypted_len == message_len &&
        memcmp(message, decrypted, message_len) == 0) {
        printf("\n✓ Verification successful: Decrypted message matches original\n");
    } else {
        printf("\n✗ Verification failed: Messages do not match\n");
    }
    
cleanup:
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
=== RSA Encryption/Decryption Demo ===
Original message: Hello RSA! This is a secret message.
Message length: 37 bytes

Generating 2048-bit RSA key pair...
Key pair generated successfully
Time taken: 3542 ms
Encrypting 37 bytes with public key...
Encryption successful
Ciphertext (256 bytes): 8A 3F 2C 5D ...

Decrypting with private key...
Decryption successful
Plaintext (37 bytes): Hello RSA! This is a secret message.

✓ Verification successful: Decrypted message matches original
```


## 步骤3：数字签名

### 3.1 生成数字签名

数字签名用于验证数据的完整性和发送者身份：

```c
/**
 * @brief  使用私钥生成数字签名
 * @param  rsa: RSA上下文（包含私钥）
 * @param  message: 要签名的消息
 * @param  message_len: 消息长度
 * @param  signature: 签名缓冲区
 * @param  ctr_drbg: 随机数生成器
 * @retval 0:成功, 其他:失败
 */
int rsa_sign_message(mbedtls_rsa_context *rsa,
                    const unsigned char *message, size_t message_len,
                    unsigned char *signature,
                    mbedtls_ctr_drbg_context *ctr_drbg)
{
    int ret;
    unsigned char hash[32];  // SHA-256哈希
    
    printf("Signing message (%zu bytes)...\n", message_len);
    
    // 1. 计算消息的SHA-256哈希
    mbedtls_sha256(message, message_len, hash, 0);
    
    printf("Message hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X ", hash[i]);
    }
    printf("\n");
    
    // 2. 使用私钥对哈希进行签名
    ret = mbedtls_rsa_pkcs1_sign(rsa, mbedtls_ctr_drbg_random, ctr_drbg,
                                MBEDTLS_RSA_PRIVATE, MBEDTLS_MD_SHA256,
                                32, hash, signature);
    
    if (ret != 0) {
        printf("Signing failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Signature generated successfully\n");
    printf("Signature (%zu bytes): ", mbedtls_rsa_get_len(rsa));
    for (size_t i = 0; i < mbedtls_rsa_get_len(rsa); i++) {
        printf("%02X ", signature[i]);
    }
    printf("\n");
    
    return 0;
}
```

### 3.2 验证数字签名

```c
/**
 * @brief  使用公钥验证数字签名
 * @param  rsa: RSA上下文（包含公钥）
 * @param  message: 原始消息
 * @param  message_len: 消息长度
 * @param  signature: 签名数据
 * @retval 0:验证成功, 其他:验证失败
 */
int rsa_verify_signature(mbedtls_rsa_context *rsa,
                        const unsigned char *message, size_t message_len,
                        const unsigned char *signature)
{
    int ret;
    unsigned char hash[32];  // SHA-256哈希
    
    printf("Verifying signature...\n");
    
    // 1. 计算消息的SHA-256哈希
    mbedtls_sha256(message, message_len, hash, 0);
    
    // 2. 使用公钥验证签名
    ret = mbedtls_rsa_pkcs1_verify(rsa, NULL, NULL,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  32, hash, signature);
    
    if (ret != 0) {
        printf("✗ Signature verification failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("✓ Signature verified successfully\n");
    printf("  Message is authentic and unmodified\n");
    
    return 0;
}
```

### 3.3 数字签名完整示例

```c
/**
 * @brief  数字签名完整示例
 */
void rsa_signature_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    
    // 要签名的消息
    const char *message = "This is an important message that needs authentication.";
    size_t message_len = strlen(message);
    
    // 签名缓冲区
    unsigned char signature[256];
    
    printf("\n=== RSA Digital Signature Demo ===\n");
    printf("Message: %s\n\n", message);
    
    // 初始化
    init_random_generator(&entropy, &ctr_drbg);
    
    // 生成密钥对
    if (generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537) != 0) {
        goto cleanup;
    }
    
    printf("\n");
    
    // 生成签名（使用私钥）
    if (rsa_sign_message(&rsa, (unsigned char *)message, message_len,
                        signature, &ctr_drbg) != 0) {
        goto cleanup;
    }
    
    printf("\n");
    
    // 验证签名（使用公钥）
    if (rsa_verify_signature(&rsa, (unsigned char *)message, message_len,
                            signature) == 0) {
        printf("\n✓ Digital signature is valid\n");
    }
    
    // 测试：修改消息后验证失败
    printf("\n--- Testing with modified message ---\n");
    const char *modified = "This is a MODIFIED message that needs authentication.";
    if (rsa_verify_signature(&rsa, (unsigned char *)modified, strlen(modified),
                            signature) != 0) {
        printf("As expected, modified message fails verification\n");
    }
    
cleanup:
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
=== RSA Digital Signature Demo ===
Message: This is an important message that needs authentication.

Generating 2048-bit RSA key pair...
Key pair generated successfully

Signing message (56 bytes)...
Message hash: 3F 8A 2C 5D 9E 1B 4F 7A ...
Signature generated successfully
Signature (256 bytes): 8A 3F 2C 5D ...

Verifying signature...
✓ Signature verified successfully
  Message is authentic and unmodified

✓ Digital signature is valid

--- Testing with modified message ---
Verifying signature...
✗ Signature verification failed: -0x4380
As expected, modified message fails verification
```


## 步骤4：混合加密方案

### 4.1 RSA + AES混合加密

实际应用中，通常使用RSA加密AES密钥，然后用AES加密数据：

```c
/**
 * @brief  混合加密：RSA加密AES密钥
 * @param  rsa: RSA上下文
 * @param  aes_key: AES密钥（16字节）
 * @param  encrypted_key: 加密后的密钥缓冲区
 * @param  ctr_drbg: 随机数生成器
 * @retval 0:成功, 其他:失败
 */
int hybrid_encrypt_key(mbedtls_rsa_context *rsa,
                      const unsigned char *aes_key,
                      unsigned char *encrypted_key,
                      mbedtls_ctr_drbg_context *ctr_drbg)
{
    printf("Encrypting AES key with RSA...\n");
    
    // 使用RSA公钥加密AES密钥
    return rsa_public_encrypt(rsa, aes_key, 16, encrypted_key, ctr_drbg);
}

/**
 * @brief  混合解密：RSA解密AES密钥
 * @param  rsa: RSA上下文
 * @param  encrypted_key: 加密的密钥
 * @param  aes_key: 解密后的AES密钥缓冲区
 * @param  key_len: 输出密钥长度
 * @retval 0:成功, 其他:失败
 */
int hybrid_decrypt_key(mbedtls_rsa_context *rsa,
                      const unsigned char *encrypted_key,
                      unsigned char *aes_key, size_t *key_len)
{
    printf("Decrypting AES key with RSA...\n");
    
    // 使用RSA私钥解密AES密钥
    return rsa_private_decrypt(rsa, encrypted_key, aes_key, key_len);
}
```

### 4.2 完整混合加密示例

```c
#include "aes.h"  // 假设已有AES实现

/**
 * @brief  混合加密完整示例
 */
void hybrid_encryption_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    
    // 大量数据（模拟）
    const char *large_data = "This is a large amount of data that needs to be "
                            "encrypted efficiently. RSA alone would be too slow "
                            "for this amount of data, so we use hybrid encryption.";
    size_t data_len = strlen(large_data);
    
    // AES密钥和IV
    unsigned char aes_key[16];
    unsigned char aes_iv[16];
    
    // RSA加密的AES密钥
    unsigned char encrypted_aes_key[256];
    
    // AES加密的数据
    unsigned char encrypted_data[256];
    unsigned char decrypted_data[256];
    
    printf("\n=== Hybrid Encryption Demo ===\n");
    printf("Data to encrypt: %s\n", large_data);
    printf("Data length: %zu bytes\n\n", data_len);
    
    // 初始化
    init_random_generator(&entropy, &ctr_drbg);
    generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537);
    
    // 1. 生成随机AES密钥和IV
    mbedtls_ctr_drbg_random(&ctr_drbg, aes_key, 16);
    mbedtls_ctr_drbg_random(&ctr_drbg, aes_iv, 16);
    
    printf("Generated AES key: ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", aes_key[i]);
    }
    printf("\n\n");
    
    // 2. 使用RSA加密AES密钥
    printf("Step 1: Encrypt AES key with RSA\n");
    hybrid_encrypt_key(&rsa, aes_key, encrypted_aes_key, &ctr_drbg);
    printf("\n");
    
    // 3. 使用AES加密数据
    printf("Step 2: Encrypt data with AES\n");
    struct AES_ctx aes_ctx;
    AES_init_ctx_iv(&aes_ctx, aes_key, aes_iv);
    
    // 准备数据（需要填充到16字节倍数）
    size_t padded_len = ((data_len / 16) + 1) * 16;
    memcpy(encrypted_data, large_data, data_len);
    memset(encrypted_data + data_len, 0, padded_len - data_len);
    
    AES_CBC_encrypt_buffer(&aes_ctx, encrypted_data, padded_len);
    printf("Data encrypted with AES (%zu bytes)\n\n", padded_len);
    
    // --- 传输加密的AES密钥和加密的数据 ---
    
    // 4. 使用RSA解密AES密钥
    printf("Step 3: Decrypt AES key with RSA\n");
    unsigned char decrypted_aes_key[16];
    size_t key_len;
    hybrid_decrypt_key(&rsa, encrypted_aes_key, decrypted_aes_key, &key_len);
    
    // 验证密钥
    if (memcmp(aes_key, decrypted_aes_key, 16) == 0) {
        printf("✓ AES key decrypted correctly\n\n");
    }
    
    // 5. 使用解密的AES密钥解密数据
    printf("Step 4: Decrypt data with AES\n");
    AES_init_ctx_iv(&aes_ctx, decrypted_aes_key, aes_iv);
    memcpy(decrypted_data, encrypted_data, padded_len);
    AES_CBC_decrypt_buffer(&aes_ctx, decrypted_data, padded_len);
    
    // 去除填充
    decrypted_data[data_len] = '\0';
    
    printf("Decrypted data: %s\n", decrypted_data);
    
    // 验证
    if (strcmp((char *)decrypted_data, large_data) == 0) {
        printf("\n✓ Hybrid encryption/decryption successful!\n");
    }
    
    // 清理
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
=== Hybrid Encryption Demo ===
Data to encrypt: This is a large amount of data...
Data length: 152 bytes

Generating 2048-bit RSA key pair...
Key pair generated successfully
Generated AES key: 3F 8A 2C 5D 9E 1B 4F 7A 6C 3E 8D 2F 5A 9C 1E 4B

Step 1: Encrypt AES key with RSA
Encrypting AES key with RSA...
Encryption successful

Step 2: Encrypt data with AES
Data encrypted with AES (160 bytes)

Step 3: Decrypt AES key with RSA
Decrypting AES key with RSA...
Decryption successful
✓ AES key decrypted correctly

Step 4: Decrypt data with AES
Decrypted data: This is a large amount of data...

✓ Hybrid encryption/decryption successful!
```

### 4.3 混合加密的优势

```c
/**
 * @brief  性能对比：纯RSA vs 混合加密
 */
void performance_comparison(void)
{
    printf("\n=== Performance Comparison ===\n\n");
    
    printf("Scenario: Encrypt 1KB of data\n\n");
    
    printf("Pure RSA:\n");
    printf("  - Need to split into ~245 byte chunks\n");
    printf("  - Requires 5 RSA operations\n");
    printf("  - Time: ~500ms (estimated)\n");
    printf("  - Output size: 1280 bytes (5 × 256)\n\n");
    
    printf("Hybrid (RSA + AES):\n");
    printf("  - 1 RSA operation (encrypt AES key)\n");
    printf("  - 1 AES operation (encrypt data)\n");
    printf("  - Time: ~110ms (estimated)\n");
    printf("  - Output size: 1280 bytes (256 + 1024)\n\n");
    
    printf("Advantage: ~4.5x faster!\n");
}
```


## 步骤5：实战项目 - 安全消息系统

### 5.1 项目需求

实现一个安全的消息传输系统，具有以下功能：
- 使用RSA进行身份认证
- 使用混合加密保护消息内容
- 支持数字签名验证消息完整性
- LED指示通信状态

### 5.2 项目架构

```c
/**
 * @file   secure_messaging.h
 * @brief  安全消息系统头文件
 */
#ifndef SECURE_MESSAGING_H
#define SECURE_MESSAGING_H

#include <stdint.h>
#include <stddef.h>
#include "mbedtls/rsa.h"
#include "mbedtls/ctr_drbg.h"

// 消息结构
typedef struct {
    uint8_t encrypted_aes_key[256];  // RSA加密的AES密钥
    uint8_t aes_iv[16];              // AES初始化向量
    uint8_t encrypted_data[512];     // AES加密的消息内容
    size_t encrypted_data_len;       // 加密数据长度
    uint8_t signature[256];          // 消息签名
    uint32_t timestamp;              // 时间戳
} secure_message_t;

// 用户密钥对
typedef struct {
    mbedtls_rsa_context rsa;         // RSA上下文
    char user_id[32];                // 用户ID
} user_keypair_t;

// 函数声明
int secure_messaging_init(void);
int create_user_keypair(user_keypair_t *user, const char *user_id);
int send_secure_message(user_keypair_t *sender,
                       mbedtls_rsa_context *receiver_public_key,
                       const char *message,
                       secure_message_t *output);
int receive_secure_message(user_keypair_t *receiver,
                          mbedtls_rsa_context *sender_public_key,
                          const secure_message_t *input,
                          char *message, size_t *message_len);

#endif // SECURE_MESSAGING_H
```

### 5.3 核心实现

```c
/**
 * @file   secure_messaging.c
 * @brief  安全消息系统实现
 */
#include "secure_messaging.h"
#include "aes.h"
#include <string.h>
#include <stdio.h>

// 全局随机数生成器
static mbedtls_entropy_context entropy;
static mbedtls_ctr_drbg_context ctr_drbg;

/**
 * @brief  初始化安全消息系统
 * @retval 0:成功, -1:失败
 */
int secure_messaging_init(void)
{
    int ret;
    const char *pers = "secure_messaging";
    
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                (const unsigned char *)pers, strlen(pers));
    if (ret != 0) {
        printf("Failed to initialize: -0x%04x\n", -ret);
        return -1;
    }
    
    printf("Secure messaging system initialized\n");
    return 0;
}

/**
 * @brief  创建用户密钥对
 * @param  user: 用户密钥对结构
 * @param  user_id: 用户ID
 * @retval 0:成功, -1:失败
 */
int create_user_keypair(user_keypair_t *user, const char *user_id)
{
    int ret;
    
    strncpy(user->user_id, user_id, sizeof(user->user_id) - 1);
    
    printf("Creating keypair for user: %s\n", user_id);
    
    ret = generate_rsa_keypair(&user->rsa, &ctr_drbg, 2048, 65537);
    if (ret != 0) {
        return -1;
    }
    
    printf("Keypair created for %s\n", user_id);
    return 0;
}

/**
 * @brief  发送安全消息
 * @param  sender: 发送者密钥对
 * @param  receiver_public_key: 接收者公钥
 * @param  message: 消息内容
 * @param  output: 输出的安全消息
 * @retval 0:成功, -1:失败
 */
int send_secure_message(user_keypair_t *sender,
                       mbedtls_rsa_context *receiver_public_key,
                       const char *message,
                       secure_message_t *output)
{
    int ret;
    uint8_t aes_key[16];
    size_t message_len = strlen(message);
    
    printf("\n--- Sending Secure Message ---\n");
    printf("From: %s\n", sender->user_id);
    printf("Message: %s\n", message);
    
    // 1. 生成随机AES密钥和IV
    mbedtls_ctr_drbg_random(&ctr_drbg, aes_key, 16);
    mbedtls_ctr_drbg_random(&ctr_drbg, output->aes_iv, 16);
    
    // 2. 使用接收者公钥加密AES密钥
    ret = rsa_public_encrypt(receiver_public_key, aes_key, 16,
                            output->encrypted_aes_key, &ctr_drbg);
    if (ret != 0) {
        return -1;
    }
    
    // 3. 使用AES加密消息
    struct AES_ctx aes_ctx;
    AES_init_ctx_iv(&aes_ctx, aes_key, output->aes_iv);
    
    // 填充到16字节倍数
    size_t padded_len = ((message_len / 16) + 1) * 16;
    memcpy(output->encrypted_data, message, message_len);
    memset(output->encrypted_data + message_len, 0, padded_len - message_len);
    
    AES_CBC_encrypt_buffer(&aes_ctx, output->encrypted_data, padded_len);
    output->encrypted_data_len = padded_len;
    
    // 4. 添加时间戳
    output->timestamp = HAL_GetTick();
    
    // 5. 使用发送者私钥签名整个消息
    unsigned char hash[32];
    mbedtls_sha256(output->encrypted_data, padded_len, hash, 0);
    
    ret = mbedtls_rsa_pkcs1_sign(&sender->rsa, mbedtls_ctr_drbg_random,
                                &ctr_drbg, MBEDTLS_RSA_PRIVATE,
                                MBEDTLS_MD_SHA256, 32, hash,
                                output->signature);
    if (ret != 0) {
        printf("Signing failed: -0x%04x\n", -ret);
        return -1;
    }
    
    printf("Message encrypted and signed\n");
    printf("Encrypted data size: %zu bytes\n", output->encrypted_data_len);
    
    // 清除AES密钥
    memset(aes_key, 0, sizeof(aes_key));
    
    return 0;
}

/**
 * @brief  接收安全消息
 * @param  receiver: 接收者密钥对
 * @param  sender_public_key: 发送者公钥
 * @param  input: 接收到的安全消息
 * @param  message: 输出的消息内容
 * @param  message_len: 输出的消息长度
 * @retval 0:成功, -1:失败
 */
int receive_secure_message(user_keypair_t *receiver,
                          mbedtls_rsa_context *sender_public_key,
                          const secure_message_t *input,
                          char *message, size_t *message_len)
{
    int ret;
    uint8_t aes_key[16];
    size_t key_len;
    
    printf("\n--- Receiving Secure Message ---\n");
    printf("To: %s\n", receiver->user_id);
    
    // 1. 验证签名
    unsigned char hash[32];
    mbedtls_sha256(input->encrypted_data, input->encrypted_data_len, hash, 0);
    
    ret = mbedtls_rsa_pkcs1_verify(sender_public_key, NULL, NULL,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  32, hash, input->signature);
    if (ret != 0) {
        printf("✗ Signature verification failed: -0x%04x\n", -ret);
        printf("Message may be tampered or from untrusted source\n");
        return -1;
    }
    
    printf("✓ Signature verified - message is authentic\n");
    
    // 2. 使用接收者私钥解密AES密钥
    ret = rsa_private_decrypt(&receiver->rsa, input->encrypted_aes_key,
                             aes_key, &key_len);
    if (ret != 0) {
        return -1;
    }
    
    // 3. 使用AES密钥解密消息
    struct AES_ctx aes_ctx;
    AES_init_ctx_iv(&aes_ctx, aes_key, (uint8_t *)input->aes_iv);
    
    memcpy(message, input->encrypted_data, input->encrypted_data_len);
    AES_CBC_decrypt_buffer(&aes_ctx, (uint8_t *)message,
                          input->encrypted_data_len);
    
    // 查找实际消息长度（去除填充）
    *message_len = strlen(message);
    
    printf("Message decrypted: %s\n", message);
    printf("Timestamp: %lu ms\n", input->timestamp);
    
    // 清除AES密钥
    memset(aes_key, 0, sizeof(aes_key));
    
    return 0;
}
```


### 5.4 主程序

```c
/**
 * @file   main.c
 * @brief  安全消息系统主程序
 */
#include "main.h"
#include "secure_messaging.h"
#include <stdio.h>

int main(void)
{
    // 系统初始化
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();
    
    printf("\n=== Secure Messaging System ===\n");
    
    // 初始化安全消息系统
    if (secure_messaging_init() != 0) {
        printf("Failed to initialize system\n");
        Error_Handler();
    }
    
    // 创建两个用户
    user_keypair_t alice, bob;
    
    printf("\n--- Creating Users ---\n");
    create_user_keypair(&alice, "Alice");
    create_user_keypair(&bob, "Bob");
    
    // Alice发送消息给Bob
    secure_message_t message1;
    const char *text1 = "Hello Bob! This is a secret message from Alice.";
    
    if (send_secure_message(&alice, &bob.rsa, text1, &message1) != 0) {
        printf("Failed to send message\n");
        Error_Handler();
    }
    
    // Bob接收并验证消息
    char received1[256];
    size_t received1_len;
    
    if (receive_secure_message(&bob, &alice.rsa, &message1,
                               received1, &received1_len) != 0) {
        printf("Failed to receive message\n");
        Error_Handler();
    }
    
    // 验证消息内容
    if (strcmp(received1, text1) == 0) {
        printf("\n✓ Message transmission successful!\n");
        HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
    }
    
    // Bob回复Alice
    printf("\n\n");
    secure_message_t message2;
    const char *text2 = "Hi Alice! Message received. Thanks!";
    
    send_secure_message(&bob, &alice.rsa, text2, &message2);
    
    char received2[256];
    size_t received2_len;
    
    receive_secure_message(&alice, &bob.rsa, &message2,
                          received2, &received2_len);
    
    if (strcmp(received2, text2) == 0) {
        printf("\n✓ Reply received successfully!\n");
    }
    
    // 测试：篡改消息
    printf("\n\n--- Testing Message Tampering ---\n");
    secure_message_t tampered = message1;
    tampered.encrypted_data[0] ^= 0xFF;  // 修改一个字节
    
    char tampered_msg[256];
    size_t tampered_len;
    
    if (receive_secure_message(&bob, &alice.rsa, &tampered,
                               tampered_msg, &tampered_len) != 0) {
        printf("✓ Tampered message correctly rejected\n");
        HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, GPIO_PIN_SET);
    }
    
    printf("\n=== Demo Complete ===\n");
    
    // 清理
    mbedtls_rsa_free(&alice.rsa);
    mbedtls_rsa_free(&bob.rsa);
    
    while (1) {
        // 主循环
        HAL_Delay(1000);
    }
}
```

**预期输出**：
```
=== Secure Messaging System ===
Secure messaging system initialized

--- Creating Users ---
Creating keypair for user: Alice
Generating 2048-bit RSA key pair...
Key pair generated successfully
Keypair created for Alice
Creating keypair for user: Bob
Generating 2048-bit RSA key pair...
Key pair generated successfully
Keypair created for Bob

--- Sending Secure Message ---
From: Alice
Message: Hello Bob! This is a secret message from Alice.
Encrypting AES key with RSA...
Encryption successful
Message encrypted and signed
Encrypted data size: 64 bytes

--- Receiving Secure Message ---
To: Bob
✓ Signature verified - message is authentic
Decrypting AES key with RSA...
Decryption successful
Message decrypted: Hello Bob! This is a secret message from Alice.
Timestamp: 12345 ms

✓ Message transmission successful!

--- Sending Secure Message ---
From: Bob
Message: Hi Alice! Message received. Thanks!
...

--- Testing Message Tampering ---
--- Receiving Secure Message ---
To: Bob
✗ Signature verification failed: -0x4380
Message may be tampered or from untrusted source
✓ Tampered message correctly rejected

=== Demo Complete ===
```

## 步骤6：密钥管理

### 6.1 密钥存储

```c
/**
 * @brief  将RSA密钥保存到Flash
 * @param  rsa: RSA上下文
 * @param  address: Flash地址
 * @retval 0:成功, -1:失败
 */
int save_rsa_key_to_flash(mbedtls_rsa_context *rsa, uint32_t address)
{
    HAL_StatusTypeDef status;
    unsigned char key_buffer[2048];
    int ret;
    
    // 导出密钥到DER格式
    mbedtls_pk_context pk;
    mbedtls_pk_init(&pk);
    mbedtls_pk_setup(&pk, mbedtls_pk_info_from_type(MBEDTLS_PK_RSA));
    
    mbedtls_rsa_context *rsa_ctx = mbedtls_pk_rsa(pk);
    mbedtls_rsa_copy(rsa_ctx, rsa);
    
    ret = mbedtls_pk_write_key_der(&pk, key_buffer, sizeof(key_buffer));
    mbedtls_pk_free(&pk);
    
    if (ret < 0) {
        printf("Failed to export key: -0x%04x\n", -ret);
        return -1;
    }
    
    size_t key_len = ret;
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 擦除扇区
    FLASH_EraseInitTypeDef erase_init;
    uint32_t sector_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_SECTORS;
    erase_init.Sector = FLASH_SECTOR_11;
    erase_init.NbSectors = 1;
    erase_init.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    
    status = HAL_FLASHEx_Erase(&erase_init, &sector_error);
    if (status != HAL_OK) {
        HAL_FLASH_Lock();
        return -1;
    }
    
    // 写入密钥长度
    HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, address, key_len);
    
    // 写入密钥数据
    for (size_t i = 0; i < key_len; i++) {
        HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE, address + 4 + i,
                         key_buffer[sizeof(key_buffer) - key_len + i]);
    }
    
    HAL_FLASH_Lock();
    
    printf("RSA key saved to Flash at 0x%08lX\n", address);
    return 0;
}

/**
 * @brief  从Flash加载RSA密钥
 * @param  rsa: RSA上下文
 * @param  address: Flash地址
 * @retval 0:成功, -1:失败
 */
int load_rsa_key_from_flash(mbedtls_rsa_context *rsa, uint32_t address)
{
    int ret;
    
    // 读取密钥长度
    uint32_t key_len = *(uint32_t *)address;
    
    if (key_len == 0 || key_len > 2048) {
        printf("Invalid key length: %lu\n", key_len);
        return -1;
    }
    
    // 读取密钥数据
    unsigned char *key_data = (unsigned char *)(address + 4);
    
    // 解析密钥
    mbedtls_pk_context pk;
    mbedtls_pk_init(&pk);
    
    ret = mbedtls_pk_parse_key(&pk, key_data, key_len, NULL, 0);
    if (ret != 0) {
        printf("Failed to parse key: -0x%04x\n", -ret);
        mbedtls_pk_free(&pk);
        return -1;
    }
    
    // 复制到RSA上下文
    mbedtls_rsa_context *rsa_ctx = mbedtls_pk_rsa(pk);
    mbedtls_rsa_copy(rsa, rsa_ctx);
    
    mbedtls_pk_free(&pk);
    
    printf("RSA key loaded from Flash\n");
    return 0;
}
```

### 6.2 密钥导入导出

```c
/**
 * @brief  从PEM字符串导入公钥
 * @param  rsa: RSA上下文
 * @param  pem_str: PEM格式的公钥字符串
 * @retval 0:成功, -1:失败
 */
int import_public_key_from_pem(mbedtls_rsa_context *rsa, const char *pem_str)
{
    int ret;
    mbedtls_pk_context pk;
    
    mbedtls_pk_init(&pk);
    
    ret = mbedtls_pk_parse_public_key(&pk,
                                     (const unsigned char *)pem_str,
                                     strlen(pem_str) + 1);
    if (ret != 0) {
        printf("Failed to parse public key: -0x%04x\n", -ret);
        mbedtls_pk_free(&pk);
        return -1;
    }
    
    // 复制到RSA上下文
    mbedtls_rsa_context *rsa_ctx = mbedtls_pk_rsa(pk);
    mbedtls_rsa_copy(rsa, rsa_ctx);
    
    mbedtls_pk_free(&pk);
    
    printf("Public key imported successfully\n");
    return 0;
}

/**
 * @brief  密钥交换示例
 */
void key_exchange_example(void)
{
    // 模拟：Alice和Bob交换公钥
    
    // Alice生成密钥对并导出公钥
    user_keypair_t alice;
    create_user_keypair(&alice, "Alice");
    
    char alice_public_key[1024];
    export_public_key(&alice.rsa, alice_public_key, sizeof(alice_public_key));
    
    // Bob生成密钥对并导出公钥
    user_keypair_t bob;
    create_user_keypair(&bob, "Bob");
    
    char bob_public_key[1024];
    export_public_key(&bob.rsa, bob_public_key, sizeof(bob_public_key));
    
    // Alice导入Bob的公钥
    mbedtls_rsa_context bob_pub;
    mbedtls_rsa_init(&bob_pub, MBEDTLS_RSA_PKCS_V15, 0);
    import_public_key_from_pem(&bob_pub, bob_public_key);
    
    // Bob导入Alice的公钥
    mbedtls_rsa_context alice_pub;
    mbedtls_rsa_init(&alice_pub, MBEDTLS_RSA_PKCS_V15, 0);
    import_public_key_from_pem(&alice_pub, alice_public_key);
    
    printf("✓ Public keys exchanged successfully\n");
    printf("Alice and Bob can now communicate securely\n");
    
    // 清理
    mbedtls_rsa_free(&alice.rsa);
    mbedtls_rsa_free(&bob.rsa);
    mbedtls_rsa_free(&bob_pub);
    mbedtls_rsa_free(&alice_pub);
}
```


## 故障排除

### 问题1：密钥生成太慢

**可能原因**：
- MCU性能不足
- 密钥长度太大
- 随机数生成慢

**解决方法**：
```c
// 1. 使用较短的密钥（仅用于测试）
generate_rsa_keypair(&rsa, &ctr_drbg, 1024, 65537);  // 1024位更快

// 2. 预生成密钥并存储
void pregenerate_keys(void)
{
    // 在工厂或首次启动时生成
    // 然后保存到Flash
}

// 3. 使用硬件随机数生成器
#ifdef HAL_RNG_MODULE_ENABLED
void use_hardware_rng(void)
{
    // 配置使用硬件RNG
    // 可以显著加快密钥生成
}
#endif

// 4. 显示进度
void generate_with_progress(void)
{
    printf("Generating key");
    for (int i = 0; i < 10; i++) {
        printf(".");
        HAL_Delay(100);
    }
    printf("\n");
}
```

### 问题2：加密数据太大

**可能原因**：
- 数据超过RSA密钥长度限制
- 没有使用混合加密

**解决方法**：
```c
// 检查数据大小
void check_data_size(size_t data_len, mbedtls_rsa_context *rsa)
{
    size_t max_len = mbedtls_rsa_get_len(rsa) - 11;
    
    if (data_len > max_len) {
        printf("Error: Data too large (%zu bytes)\n", data_len);
        printf("Maximum: %zu bytes\n", max_len);
        printf("Solution: Use hybrid encryption (RSA + AES)\n");
    }
}

// 自动选择加密方式
int smart_encrypt(const unsigned char *data, size_t data_len,
                 mbedtls_rsa_context *rsa, unsigned char *output)
{
    size_t max_len = mbedtls_rsa_get_len(rsa) - 11;
    
    if (data_len <= max_len) {
        // 直接使用RSA
        return rsa_public_encrypt(rsa, data, data_len, output, &ctr_drbg);
    } else {
        // 使用混合加密
        printf("Data too large, using hybrid encryption\n");
        // 实现混合加密逻辑
        return 0;
    }
}
```

### 问题3：签名验证失败

**可能原因**：
- 使用了错误的公钥
- 消息被篡改
- 哈希算法不匹配

**解决方法**：
```c
// 详细的验证过程
int verify_with_details(mbedtls_rsa_context *rsa,
                       const unsigned char *message, size_t message_len,
                       const unsigned char *signature)
{
    int ret;
    unsigned char hash[32];
    
    // 1. 计算消息哈希
    mbedtls_sha256(message, message_len, hash, 0);
    
    printf("Message hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X ", hash[i]);
    }
    printf("\n");
    
    // 2. 验证签名
    ret = mbedtls_rsa_pkcs1_verify(rsa, NULL, NULL,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  32, hash, signature);
    
    if (ret != 0) {
        printf("Verification failed: -0x%04x\n", -ret);
        
        // 诊断
        if (ret == MBEDTLS_ERR_RSA_VERIFY_FAILED) {
            printf("Possible causes:\n");
            printf("  - Wrong public key\n");
            printf("  - Message was modified\n");
            printf("  - Signature was corrupted\n");
        }
        
        return ret;
    }
    
    printf("✓ Signature valid\n");
    return 0;
}
```

### 问题4：内存不足

**可能原因**：
- RSA操作需要大量内存
- 栈空间不足
- 堆空间不足

**解决方法**：
```c
// 1. 增加栈大小
// 在启动文件中修改：
// Stack_Size      EQU     0x2000  ; 增加到8KB

// 2. 使用静态缓冲区
static unsigned char static_buffer[2048];

void use_static_buffer(void)
{
    // 使用静态缓冲区而不是栈
}

// 3. 分步处理
void process_in_steps(void)
{
    // 生成密钥
    generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537);
    
    // 释放不需要的资源
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    
    // 然后进行加密操作
}

// 4. 检查可用内存
void check_memory(void)
{
    extern uint8_t _end;
    extern uint8_t _estack;
    uint32_t stack_size = (uint32_t)&_estack - (uint32_t)&_end;
    
    printf("Available stack: %lu bytes\n", stack_size);
    
    if (stack_size < 8192) {
        printf("Warning: Low stack space for RSA operations\n");
    }
}
```

### 问题5：性能优化

**可能原因**：
- 频繁的密钥生成
- 不必要的加密操作
- 没有使用硬件加速

**解决方法**：
```c
// 1. 缓存密钥对
static mbedtls_rsa_context cached_rsa;
static int key_cached = 0;

mbedtls_rsa_context* get_cached_key(void)
{
    if (!key_cached) {
        generate_rsa_keypair(&cached_rsa, &ctr_drbg, 2048, 65537);
        key_cached = 1;
    }
    return &cached_rsa;
}

// 2. 批量处理
void batch_encrypt(const unsigned char **messages, int count)
{
    // 一次性初始化
    mbedtls_rsa_context rsa;
    generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537);
    
    // 批量加密
    for (int i = 0; i < count; i++) {
        // 加密每条消息
    }
    
    // 清理
    mbedtls_rsa_free(&rsa);
}

// 3. 使用硬件加速（如果可用）
#ifdef MBEDTLS_HARDWARE_ACCELERATION
void enable_hardware_acceleration(void)
{
    // 配置硬件加速
    // STM32F4系列部分型号支持
}
#endif

// 4. 性能测试
void performance_test(void)
{
    uint32_t start, end;
    
    // 测试密钥生成
    start = HAL_GetTick();
    generate_rsa_keypair(&rsa, &ctr_drbg, 2048, 65537);
    end = HAL_GetTick();
    printf("Key generation: %lu ms\n", end - start);
    
    // 测试加密
    start = HAL_GetTick();
    rsa_public_encrypt(&rsa, data, data_len, ciphertext, &ctr_drbg);
    end = HAL_GetTick();
    printf("Encryption: %lu ms\n", end - start);
    
    // 测试解密
    start = HAL_GetTick();
    rsa_private_decrypt(&rsa, ciphertext, plaintext, &plaintext_len);
    end = HAL_GetTick();
    printf("Decryption: %lu ms\n", end - start);
}
```

## 总结

通过本教程，你学习了：

- ✅ RSA非对称加密的基本原理和数学基础
- ✅ 公钥和私钥的概念及其应用
- ✅ 如何生成和管理RSA密钥对
- ✅ RSA加密和解密的实现方法
- ✅ 数字签名的原理和实现
- ✅ 混合加密方案（RSA + AES）
- ✅ 完整的安全消息传输系统
- ✅ 密钥存储和交换机制

**关键要点**：

1. **RSA特点**
   - 非对称加密，公钥加密私钥解密
   - 计算量大，速度慢
   - 适合小数据和密钥交换
   - 可用于数字签名

2. **密钥管理**
   - 私钥必须严格保密
   - 公钥可以公开分发
   - 定期更新密钥对
   - 安全存储在Flash中

3. **混合加密**
   - RSA加密AES密钥
   - AES加密实际数据
   - 结合两者优势
   - 适合大数据传输

4. **数字签名**
   - 验证身份和完整性
   - 私钥签名，公钥验证
   - 防止消息篡改
   - 不可否认性

## 进阶挑战

尝试以下挑战来巩固学习：

1. **挑战1**：实现RSA-OAEP填充模式（更安全）
2. **挑战2**：添加证书链验证功能
3. **挑战3**：实现密钥协商协议（如Diffie-Hellman）
4. **挑战4**：添加密钥过期和自动更新机制
5. **挑战5**：实现完整的PKI（公钥基础设施）系统

## 完整代码

完整的项目代码可以在这里下载：
- GitHub仓库：[RSA-Encryption-Demo](https://github.com/embedded-platform/rsa-demo)
- 包含所有示例代码和测试用例

## 下一步

建议继续学习：

- [哈希算法与消息摘要](03-hash-algorithms.html) - 学习数据完整性验证
- [数字签名技术详解](../intermediate/01-digital-signature.html) - 深入学习签名
- [安全启动与固件验证](../intermediate/02-secure-boot-verification.html) - 学习系统安全
- [密钥管理与安全存储](../intermediate/03-key-management.html) - 学习密钥管理

## 参考资料

1. **官方文档**
   - RSA Laboratories: RSA标准
   - mbedTLS文档
   - PKCS#1标准

2. **推荐书籍**
   - 《应用密码学》- Bruce Schneier
   - 《密码工程》- Niels Ferguson
   - 《公钥密码学》- Douglas Stinson

3. **在线资源**
   - [RSA在线工具](https://www.devglan.com/online-tools/rsa-encryption-decryption)
   - [密码学课程](https://www.coursera.org/learn/crypto)
   - [NIST密码学标准](https://csrc.nist.gov/)

4. **相关标准**
   - PKCS#1: RSA加密标准
   - X.509: 数字证书标准
   - RFC 8017: PKCS#1 v2.2

---

**反馈**：如果你在学习过程中遇到问题，欢迎在评论区留言或提交Issue！

**版本历史**：
- v1.0 (2024-01-15): 初始版本发布
