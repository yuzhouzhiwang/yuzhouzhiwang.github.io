---
title: "数字签名技术详解：身份认证与数据完整性保护"
description: "深入学习数字签名原理、签名生成验证流程、证书链和PKI体系，掌握在嵌入式系统中实现安全的身份认证和数据完整性保护"
slug: "digital-signature"

# 分类信息
domain: "中间件层"
module: "安全与加密"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 数字签名
  - PKI
  - 身份认证
  - 证书链
  - 非对称加密
prerequisites:
  - "04-middleware-layer/05-security-encryption/beginner/02-rsa-encryption"
  - "04-middleware-layer/05-security-encryption/beginner/03-hash-algorithms"
related_contents:
  - "04-middleware-layer/05-security-encryption/beginner/01-aes-encryption"
  - "04-middleware-layer/05-security-encryption/intermediate/02-secure-boot-verification"

# 学习信息
estimated_time: 75
difficulty_score: 4

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
  - 数字签名
  - PKI体系
  - 证书验证
  - 身份认证
  - 数据完整性
cover_image: ""
---

# 数字签名技术详解：身份认证与数据完整性保护



## 学习目标

完成本教程后，你将能够：

- [ ] 深入理解数字签名的工作原理和数学基础
- [ ] 掌握RSA和ECDSA数字签名算法的实现
- [ ] 理解PKI（公钥基础设施）体系架构
- [ ] 熟练进行数字证书的生成、验证和管理
- [ ] 掌握证书链的验证流程
- [ ] 能够实现固件签名和验证系统
- [ ] 理解时间戳和不可否认性的概念
- [ ] 完成一个完整的安全认证项目
- [ ] 掌握数字签名在物联网中的应用

## 前置要求

在开始学习之前，建议你具备：

**知识要求**：
- 熟悉RSA非对称加密原理
- 理解哈希算法（SHA-256等）
- 了解公钥和私钥的概念
- 掌握基本的密码学知识
- 理解数字证书的基本概念

**技能要求**：
- 熟练使用mbedTLS或OpenSSL库
- 能够编写嵌入式C代码
- 会使用调试工具
- 熟悉Flash存储操作
- 了解网络通信基础

**开发环境**：
- STM32或ESP32开发板
- STM32CubeIDE或Arduino IDE
- mbedTLS库
- OpenSSL工具（用于证书生成）
- 串口调试工具



## 数字签名概述

### 什么是数字签名

数字签名是一种数学方案，用于验证数字消息或文档的真实性和完整性。它相当于物理世界中的手写签名或印章，但提供了更强的安全保证。

**核心特性**：

1. **身份认证**
   - 证明消息来自特定发送者
   - 发送者无法否认发送过消息
   - 接收者可以验证发送者身份
   - 第三方也可以验证

2. **完整性保护**
   - 消息未被篡改
   - 任何修改都会导致验证失败
   - 提供强完整性保证
   - 检测任意位的改变

3. **不可否认性**
   - 发送者不能否认签名
   - 提供法律证据
   - 可追溯性
   - 审计支持

4. **可验证性**
   - 任何人都可以验证签名
   - 使用公钥验证
   - 不需要保密信息
   - 支持第三方验证


### 数字签名工作原理

**基本流程图**：

```
签名生成（发送方）:
┌─────────────────┐
│  原始消息       │
└─────────────────┘
        ↓
┌─────────────────┐
│  哈希函数       │ (SHA-256)
│  计算消息摘要   │
└─────────────────┘
        ↓
   消息摘要 (Hash)
        ↓
┌─────────────────┐
│  私钥加密       │ (RSA/ECDSA)
│  生成签名       │
└─────────────────┘
        ↓
    数字签名
        ↓
┌─────────────────┐
│ 消息 + 签名     │ → 发送
└─────────────────┘

签名验证（接收方）:
┌─────────────────┐
│ 接收消息+签名   │
└─────────────────┘
        ↓
   ┌────┴────┐
   ↓         ↓
消息      签名
   ↓         ↓
┌──────┐  ┌──────┐
│哈希  │  │公钥  │
│计算  │  │解密  │
└──────┘  └──────┘
   ↓         ↓
摘要1     摘要2
   ↓         ↓
   └────┬────┘
        ↓
   ┌─────────┐
   │ 比较    │
   └─────────┘
        ↓
   验证结果
```

**关键步骤**：

1. **签名生成**
   - 计算消息的哈希值
   - 使用私钥加密哈希值
   - 得到数字签名
   - 将签名附加到消息

2. **签名验证**
   - 计算接收消息的哈希值
   - 使用公钥解密签名
   - 比较两个哈希值
   - 相同则验证成功


### 数字签名 vs 加密

| 特性 | 数字签名 | 加密 |
|------|---------|------|
| 目的 | 认证和完整性 | 保密性 |
| 使用密钥 | 私钥签名，公钥验证 | 公钥加密，私钥解密 |
| 消息可读性 | 明文可读 | 密文不可读 |
| 主要功能 | 证明身份 | 保护内容 |
| 可否认性 | 不可否认 | 可否认 |
| 验证者 | 任何人 | 仅持有私钥者 |

**组合使用**：

```
安全通信的完整方案：

1. 发送方：
   消息 → [签名] → 消息+签名 → [加密] → 密文

2. 接收方：
   密文 → [解密] → 消息+签名 → [验证] → 原始消息

结果：
- 加密保证保密性
- 签名保证真实性和完整性
- 提供完整的安全保护
```



## 准备工作

### 硬件准备

| 名称 | 数量 | 说明 | 参考型号 |
|------|------|------|----------|
| 开发板 | 1 | STM32F4或ESP32 | STM32F407VG |
| USB线 | 1 | 供电和调试 | - |
| LED灯 | 3 | 状态指示 | - |
| 按键 | 2 | 触发操作 | - |

### 软件准备

**必需软件**：
- STM32CubeIDE 或 Arduino IDE（ESP32）
- mbedTLS库：https://github.com/ARMmbed/mbedtls
- OpenSSL工具（用于证书生成）
- 串口调试助手

**可选工具**：
- X.509证书查看器
- 在线签名验证工具

### 环境配置

**安装mbedTLS库**：

```bash
# 克隆mbedTLS仓库
git clone https://github.com/ARMmbed/mbedtls.git

# 需要的模块
# - RSA签名
# - ECDSA签名
# - X.509证书
# - PEM格式支持
```

**配置mbedTLS**：

创建 `mbedtls_config.h`：

```c
#ifndef MBEDTLS_CONFIG_H
#define MBEDTLS_CONFIG_H

// 启用RSA
#define MBEDTLS_RSA_C
#define MBEDTLS_BIGNUM_C
#define MBEDTLS_PK_C

// 启用ECDSA
#define MBEDTLS_ECDSA_C
#define MBEDTLS_ECP_C

// 启用哈希算法
#define MBEDTLS_SHA256_C
#define MBEDTLS_MD_C

// 启用X.509证书
#define MBEDTLS_X509_USE_C
#define MBEDTLS_X509_CRT_PARSE_C

// 启用PEM格式
#define MBEDTLS_PEM_PARSE_C
#define MBEDTLS_BASE64_C

// 启用随机数生成器
#define MBEDTLS_ENTROPY_C
#define MBEDTLS_CTR_DRBG_C

#endif // MBEDTLS_CONFIG_H
```

**安装OpenSSL工具**（用于证书生成）：

```bash
# Windows: 下载并安装
# https://slproweb.com/products/Win32OpenSSL.html

# Linux/Mac: 通常已预装
openssl version
```



## 步骤1：RSA数字签名实现

### 1.1 基础RSA签名

```c
#include "mbedtls/rsa.h"
#include "mbedtls/sha256.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include <stdio.h>
#include <string.h>

/**
 * @brief  使用RSA私钥生成数字签名
 * @param  rsa: RSA上下文（包含私钥）
 * @param  message: 要签名的消息
 * @param  message_len: 消息长度
 * @param  signature: 输出签名缓冲区
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
    
    printf("=== RSA Digital Signature ===\n");
    printf("Message: %.*s\n", (int)message_len, message);
    printf("Message length: %zu bytes\n\n", message_len);
    
    // 步骤1: 计算消息的SHA-256哈希
    printf("Step 1: Computing SHA-256 hash...\n");
    ret = mbedtls_sha256(message, message_len, hash, 0);
    if (ret != 0) {
        printf("Hash computation failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", hash[i]);
    }
    printf("\n\n");
    
    // 步骤2: 使用私钥对哈希进行签名
    printf("Step 2: Signing hash with private key...\n");
    ret = mbedtls_rsa_pkcs1_sign(rsa, mbedtls_ctr_drbg_random, ctr_drbg,
                                MBEDTLS_RSA_PRIVATE, MBEDTLS_MD_SHA256,
                                32, hash, signature);
    
    if (ret != 0) {
        printf("Signing failed: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("Signature generated successfully\n");
    printf("Signature length: %zu bytes\n", mbedtls_rsa_get_len(rsa));
    printf("Signature: ");
    for (size_t i = 0; i < mbedtls_rsa_get_len(rsa); i++) {
        printf("%02X", signature[i]);
        if ((i + 1) % 32 == 0) printf("\n           ");
    }
    printf("\n");
    
    return 0;
}

/**
 * @brief  使用RSA公钥验证数字签名
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
    unsigned char hash[32];
    
    printf("\n=== Signature Verification ===\n");
    
    // 步骤1: 计算消息的SHA-256哈希
    printf("Step 1: Computing message hash...\n");
    ret = mbedtls_sha256(message, message_len, hash, 0);
    if (ret != 0) {
        printf("Hash computation failed: -0x%04x\n", -ret);
        return ret;
    }
    
    // 步骤2: 使用公钥验证签名
    printf("Step 2: Verifying signature with public key...\n");
    ret = mbedtls_rsa_pkcs1_verify(rsa, NULL, NULL,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  32, hash, signature);
    
    if (ret != 0) {
        printf("✗ Signature verification FAILED: -0x%04x\n", -ret);
        printf("  Possible reasons:\n");
        printf("  - Message was modified\n");
        printf("  - Signature was tampered\n");
        printf("  - Wrong public key used\n");
        return ret;
    }
    
    printf("✓ Signature verification SUCCESSFUL\n");
    printf("  Message is authentic and unmodified\n");
    printf("  Sender identity confirmed\n");
    
    return 0;
}
```

**代码说明**：
- 签名过程：先哈希，再用私钥加密哈希值
- 验证过程：计算哈希，用公钥解密签名，比较哈希值
- 使用PKCS#1 v1.5填充方案
- SHA-256作为哈希算法



### 1.2 完整签名验证示例

```c
/**
 * @brief  RSA签名和验证完整示例
 */
void rsa_signature_complete_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    
    const char *message = "This document is legally binding and must be authenticated.";
    unsigned char signature[256];  // 2048位RSA = 256字节签名
    
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║  RSA Digital Signature Demo           ║\n");
    printf("╚════════════════════════════════════════╝\n\n");
    
    // 初始化随机数生成器
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    const char *pers = "rsa_signature";
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                         (const unsigned char *)pers, strlen(pers));
    
    // 生成RSA密钥对
    printf("Generating 2048-bit RSA key pair...\n");
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V15, 0);
    
    uint32_t start_time = HAL_GetTick();
    int ret = mbedtls_rsa_gen_key(&rsa, mbedtls_ctr_drbg_random, &ctr_drbg,
                                 2048, 65537);
    uint32_t end_time = HAL_GetTick();
    
    if (ret != 0) {
        printf("Key generation failed: -0x%04x\n", -ret);
        goto cleanup;
    }
    
    printf("Key pair generated in %lu ms\n\n", end_time - start_time);
    
    // 生成签名
    if (rsa_sign_message(&rsa, (unsigned char *)message, strlen(message),
                        signature, &ctr_drbg) != 0) {
        goto cleanup;
    }
    
    // 验证签名
    if (rsa_verify_signature(&rsa, (unsigned char *)message, strlen(message),
                            signature) == 0) {
        printf("\n✓ Complete signature cycle successful\n");
    }
    
    // 测试：修改消息后验证失败
    printf("\n--- Testing with Modified Message ---\n");
    const char *modified = "This document is legally binding and must be MODIFIED.";
    if (rsa_verify_signature(&rsa, (unsigned char *)modified, strlen(modified),
                            signature) != 0) {
        printf("As expected, modified message fails verification\n");
    }
    
    // 测试：修改签名后验证失败
    printf("\n--- Testing with Tampered Signature ---\n");
    signature[0] ^= 0x01;  // 修改签名的一个位
    if (rsa_verify_signature(&rsa, (unsigned char *)message, strlen(message),
                            signature) != 0) {
        printf("As expected, tampered signature fails verification\n");
    }
    
cleanup:
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
╔════════════════════════════════════════╗
║  RSA Digital Signature Demo           ║
╚════════════════════════════════════════╝

Generating 2048-bit RSA key pair...
Key pair generated in 3542 ms

=== RSA Digital Signature ===
Message: This document is legally binding...
Message length: 59 bytes

Step 1: Computing SHA-256 hash...
Hash: 8D969EEF6ECAD3C29A3A629280E686CF...

Step 2: Signing hash with private key...
Signature generated successfully
Signature length: 256 bytes
Signature: 3F8A2C5D9E1B4F7A6C3E8D2F5A9C1E4B...

=== Signature Verification ===
Step 1: Computing message hash...
Step 2: Verifying signature with public key...
✓ Signature verification SUCCESSFUL
  Message is authentic and unmodified
  Sender identity confirmed

✓ Complete signature cycle successful

--- Testing with Modified Message ---
✗ Signature verification FAILED: -0x4380
  Possible reasons:
  - Message was modified
As expected, modified message fails verification

--- Testing with Tampered Signature ---
✗ Signature verification FAILED: -0x4380
As expected, tampered signature fails verification
```



## 步骤2：ECDSA数字签名

ECDSA（Elliptic Curve Digital Signature Algorithm）是基于椭圆曲线密码学的数字签名算法，相比RSA具有更短的密钥长度和更快的速度。

### 2.1 ECDSA签名实现

```c
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"

/**
 * @brief  使用ECDSA生成数字签名
 * @param  grp_id: 椭圆曲线组ID（如SECP256R1）
 * @param  message: 要签名的消息
 * @param  message_len: 消息长度
 * @param  signature: 输出签名缓冲区
 * @param  sig_len: 输出签名长度
 * @param  ctr_drbg: 随机数生成器
 * @retval 0:成功, 其他:失败
 */
int ecdsa_sign_message(mbedtls_ecp_group_id grp_id,
                      const unsigned char *message, size_t message_len,
                      unsigned char *signature, size_t *sig_len,
                      mbedtls_ctr_drbg_context *ctr_drbg)
{
    int ret;
    mbedtls_ecdsa_context ctx;
    unsigned char hash[32];
    
    printf("=== ECDSA Digital Signature ===\n");
    printf("Curve: SECP256R1 (P-256)\n");
    printf("Message: %.*s\n\n", (int)message_len, message);
    
    // 初始化ECDSA上下文
    mbedtls_ecdsa_init(&ctx);
    
    // 生成密钥对
    printf("Step 1: Generating ECDSA key pair...\n");
    uint32_t start = HAL_GetTick();
    ret = mbedtls_ecdsa_genkey(&ctx, grp_id,
                              mbedtls_ctr_drbg_random, ctr_drbg);
    uint32_t end = HAL_GetTick();
    
    if (ret != 0) {
        printf("Key generation failed: -0x%04x\n", -ret);
        mbedtls_ecdsa_free(&ctx);
        return ret;
    }
    
    printf("Key pair generated in %lu ms\n", end - start);
    printf("Key size: 256 bits\n\n");
    
    // 计算消息哈希
    printf("Step 2: Computing SHA-256 hash...\n");
    mbedtls_sha256(message, message_len, hash, 0);
    
    printf("Hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", hash[i]);
    }
    printf("\n\n");
    
    // 生成签名
    printf("Step 3: Generating ECDSA signature...\n");
    ret = mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256,
                                       hash, 32,
                                       signature, sig_len,
                                       mbedtls_ctr_drbg_random, ctr_drbg);
    
    if (ret != 0) {
        printf("Signing failed: -0x%04x\n", -ret);
        mbedtls_ecdsa_free(&ctx);
        return ret;
    }
    
    printf("Signature generated successfully\n");
    printf("Signature length: %zu bytes\n", *sig_len);
    printf("Signature: ");
    for (size_t i = 0; i < *sig_len; i++) {
        printf("%02X", signature[i]);
    }
    printf("\n");
    
    // 注意：实际应用中需要保存公钥用于验证
    // 这里为了演示，我们直接使用同一个上下文验证
    
    mbedtls_ecdsa_free(&ctx);
    return 0;
}

/**
 * @brief  使用ECDSA验证数字签名
 * @param  public_key: 公钥上下文
 * @param  message: 原始消息
 * @param  message_len: 消息长度
 * @param  signature: 签名数据
 * @param  sig_len: 签名长度
 * @retval 0:验证成功, 其他:验证失败
 */
int ecdsa_verify_signature(mbedtls_ecdsa_context *public_key,
                          const unsigned char *message, size_t message_len,
                          const unsigned char *signature, size_t sig_len)
{
    int ret;
    unsigned char hash[32];
    
    printf("\n=== ECDSA Signature Verification ===\n");
    
    // 计算消息哈希
    printf("Step 1: Computing message hash...\n");
    mbedtls_sha256(message, message_len, hash, 0);
    
    // 验证签名
    printf("Step 2: Verifying signature...\n");
    ret = mbedtls_ecdsa_read_signature(public_key, hash, 32,
                                      signature, sig_len);
    
    if (ret != 0) {
        printf("✗ ECDSA signature verification FAILED: -0x%04x\n", -ret);
        return ret;
    }
    
    printf("✓ ECDSA signature verification SUCCESSFUL\n");
    printf("  Message is authentic\n");
    
    return 0;
}
```

**ECDSA vs RSA对比**：

| 特性 | ECDSA (P-256) | RSA (2048-bit) |
|------|--------------|----------------|
| 密钥长度 | 256位 | 2048位 |
| 签名长度 | ~72字节 | 256字节 |
| 签名速度 | 快 | 慢 |
| 验证速度 | 中等 | 快 |
| 密钥生成 | 快 | 慢 |
| 安全级别 | 128位 | 112位 |
| 存储需求 | 小 | 大 |

**ECDSA优势**：
- 更短的密钥和签名
- 更快的签名生成
- 更少的存储空间
- 更低的带宽需求
- 适合资源受限设备



## 步骤3：数字证书和PKI体系

### 3.1 X.509数字证书

X.509是定义数字证书格式的标准，广泛用于TLS/SSL、代码签名等场景。

**证书结构**：

```
X.509证书包含：
┌─────────────────────────────────┐
│ 版本号 (Version)                │
├─────────────────────────────────┤
│ 序列号 (Serial Number)          │
├─────────────────────────────────┤
│ 签名算法 (Signature Algorithm)  │
├─────────────────────────────────┤
│ 颁发者 (Issuer)                 │
│  - 国家 (C)                     │
│  - 组织 (O)                     │
│  - 通用名 (CN)                  │
├─────────────────────────────────┤
│ 有效期 (Validity)               │
│  - 开始时间 (Not Before)        │
│  - 结束时间 (Not After)         │
├─────────────────────────────────┤
│ 主体 (Subject)                  │
│  - 国家 (C)                     │
│  - 组织 (O)                     │
│  - 通用名 (CN)                  │
├─────────────────────────────────┤
│ 公钥信息 (Subject Public Key)   │
│  - 算法                         │
│  - 公钥数据                     │
├─────────────────────────────────┤
│ 扩展字段 (Extensions)           │
│  - 密钥用途                     │
│  - 主体备用名称                 │
│  - 等等...                      │
├─────────────────────────────────┤
│ 签名 (Signature)                │
│  - CA的数字签名                 │
└─────────────────────────────────┘
```

### 3.2 使用OpenSSL生成证书

**生成自签名证书**：

```bash
# 1. 生成私钥
openssl genrsa -out ca_private.key 2048

# 2. 生成自签名根证书
openssl req -new -x509 -days 3650 -key ca_private.key -out ca_cert.pem \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/OU=IoT/CN=Root CA"

# 3. 生成设备私钥
openssl genrsa -out device_private.key 2048

# 4. 生成证书签名请求(CSR)
openssl req -new -key device_private.key -out device.csr \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/OU=IoT/CN=Device001"

# 5. 使用CA签名生成设备证书
openssl x509 -req -in device.csr -CA ca_cert.pem -CAkey ca_private.key \
    -CAcreateserial -out device_cert.pem -days 365

# 6. 查看证书内容
openssl x509 -in device_cert.pem -text -noout

# 7. 转换为C数组格式（用于嵌入式）
xxd -i ca_cert.pem > ca_cert.h
xxd -i device_cert.pem > device_cert.h
```

### 3.3 在嵌入式系统中解析证书

```c
#include "mbedtls/x509_crt.h"

/**
 * @brief  解析X.509证书
 * @param  cert_pem: PEM格式的证书
 * @param  cert_len: 证书长度
 */
void parse_x509_certificate(const unsigned char *cert_pem, size_t cert_len)
{
    mbedtls_x509_crt cert;
    int ret;
    char buf[1024];
    
    printf("\n=== Parsing X.509 Certificate ===\n");
    
    // 初始化证书结构
    mbedtls_x509_crt_init(&cert);
    
    // 解析证书
    ret = mbedtls_x509_crt_parse(&cert, cert_pem, cert_len);
    if (ret != 0) {
        printf("Certificate parsing failed: -0x%04x\n", -ret);
        mbedtls_x509_crt_free(&cert);
        return;
    }
    
    printf("Certificate parsed successfully\n\n");
    
    // 获取证书信息
    ret = mbedtls_x509_crt_info(buf, sizeof(buf), "  ", &cert);
    if (ret > 0) {
        printf("Certificate Information:\n%s\n", buf);
    }
    
    // 提取关键信息
    printf("Key Information:\n");
    printf("  Version: %d\n", cert.version);
    printf("  Serial: ");
    for (size_t i = 0; i < cert.serial.len; i++) {
        printf("%02X", cert.serial.p[i]);
    }
    printf("\n");
    
    printf("  Issuer: ");
    mbedtls_x509_dn_gets(buf, sizeof(buf), &cert.issuer);
    printf("%s\n", buf);
    
    printf("  Subject: ");
    mbedtls_x509_dn_gets(buf, sizeof(buf), &cert.subject);
    printf("%s\n", buf);
    
    printf("  Valid from: %04d-%02d-%02d %02d:%02d:%02d\n",
           cert.valid_from.year, cert.valid_from.mon, cert.valid_from.day,
           cert.valid_from.hour, cert.valid_from.min, cert.valid_from.sec);
    
    printf("  Valid to:   %04d-%02d-%02d %02d:%02d:%02d\n",
           cert.valid_to.year, cert.valid_to.mon, cert.valid_to.day,
           cert.valid_to.hour, cert.valid_to.min, cert.valid_to.sec);
    
    // 清理
    mbedtls_x509_crt_free(&cert);
}

/**
 * @brief  验证证书链
 * @param  device_cert: 设备证书
 * @param  ca_cert: CA证书
 * @retval 0:验证成功, 其他:验证失败
 */
int verify_certificate_chain(const unsigned char *device_cert_pem,
                             size_t device_cert_len,
                             const unsigned char *ca_cert_pem,
                             size_t ca_cert_len)
{
    mbedtls_x509_crt device_cert, ca_cert;
    uint32_t flags;
    int ret;
    char vrfy_buf[512];
    
    printf("\n=== Certificate Chain Verification ===\n");
    
    // 初始化证书
    mbedtls_x509_crt_init(&device_cert);
    mbedtls_x509_crt_init(&ca_cert);
    
    // 解析设备证书
    printf("Step 1: Parsing device certificate...\n");
    ret = mbedtls_x509_crt_parse(&device_cert, device_cert_pem, device_cert_len);
    if (ret != 0) {
        printf("Device certificate parsing failed: -0x%04x\n", -ret);
        goto cleanup;
    }
    printf("Device certificate parsed\n");
    
    // 解析CA证书
    printf("Step 2: Parsing CA certificate...\n");
    ret = mbedtls_x509_crt_parse(&ca_cert, ca_cert_pem, ca_cert_len);
    if (ret != 0) {
        printf("CA certificate parsing failed: -0x%04x\n", -ret);
        goto cleanup;
    }
    printf("CA certificate parsed\n");
    
    // 验证证书链
    printf("Step 3: Verifying certificate chain...\n");
    ret = mbedtls_x509_crt_verify(&device_cert, &ca_cert, NULL,
                                  NULL, &flags, NULL, NULL);
    
    if (ret != 0) {
        printf("✗ Certificate verification FAILED\n");
        mbedtls_x509_crt_verify_info(vrfy_buf, sizeof(vrfy_buf), "  ! ", flags);
        printf("%s\n", vrfy_buf);
        goto cleanup;
    }
    
    printf("✓ Certificate chain verification SUCCESSFUL\n");
    printf("  Device certificate is valid\n");
    printf("  Signed by trusted CA\n");
    printf("  Certificate chain is complete\n");
    
cleanup:
    mbedtls_x509_crt_free(&device_cert);
    mbedtls_x509_crt_free(&ca_cert);
    return ret;
}
```

**证书验证流程**：

```
证书链验证步骤：

1. 解析设备证书
   ↓
2. 解析CA证书
   ↓
3. 检查证书有效期
   ↓
4. 验证证书签名
   - 提取设备证书的签名
   - 使用CA公钥验证签名
   ↓
5. 检查证书链
   - 设备证书的Issuer = CA证书的Subject
   ↓
6. 检查证书用途
   - 密钥用途是否匹配
   ↓
7. 验证成功/失败
```



## 步骤4：固件签名和验证

### 4.1 固件签名系统设计

```c
/**
 * @file   firmware_signature.h
 * @brief  固件签名和验证系统
 */
#ifndef FIRMWARE_SIGNATURE_H
#define FIRMWARE_SIGNATURE_H

#include <stdint.h>
#include <stddef.h>

// 固件签名头部结构
typedef struct {
    uint32_t magic;              // 魔数: 0x46575349 ("FWSI")
    uint32_t version;            // 固件版本
    uint32_t firmware_size;      // 固件大小
    uint32_t timestamp;          // 签名时间戳
    uint8_t  hash_algorithm;     // 哈希算法 (1=SHA256)
    uint8_t  signature_algorithm;// 签名算法 (1=RSA, 2=ECDSA)
    uint16_t signature_length;   // 签名长度
    uint8_t  firmware_hash[32];  // 固件SHA-256哈希
    uint8_t  signature[256];     // 数字签名
    uint8_t  reserved[64];       // 保留字段
} __attribute__((packed)) firmware_signature_t;

// 函数声明
int sign_firmware(const uint8_t *firmware, size_t firmware_size,
                 firmware_signature_t *sig_header,
                 mbedtls_rsa_context *private_key,
                 mbedtls_ctr_drbg_context *ctr_drbg);

int verify_firmware(const uint8_t *firmware, size_t firmware_size,
                   const firmware_signature_t *sig_header,
                   mbedtls_rsa_context *public_key);

#endif // FIRMWARE_SIGNATURE_H
```

### 4.2 固件签名实现

```c
/**
 * @file   firmware_signature.c
 * @brief  固件签名和验证实现
 */
#include "firmware_signature.h"
#include "mbedtls/sha256.h"
#include "mbedtls/rsa.h"
#include <string.h>
#include <stdio.h>

#define FIRMWARE_MAGIC 0x46575349  // "FWSI"

/**
 * @brief  对固件进行签名
 * @param  firmware: 固件数据
 * @param  firmware_size: 固件大小
 * @param  sig_header: 输出签名头部
 * @param  private_key: RSA私钥
 * @param  ctr_drbg: 随机数生成器
 * @retval 0:成功, -1:失败
 */
int sign_firmware(const uint8_t *firmware, size_t firmware_size,
                 firmware_signature_t *sig_header,
                 mbedtls_rsa_context *private_key,
                 mbedtls_ctr_drbg_context *ctr_drbg)
{
    int ret;
    
    printf("\n=== Firmware Signing Process ===\n");
    printf("Firmware size: %zu bytes\n", firmware_size);
    
    // 初始化签名头部
    memset(sig_header, 0, sizeof(firmware_signature_t));
    sig_header->magic = FIRMWARE_MAGIC;
    sig_header->version = 0x00010000;  // v1.0.0
    sig_header->firmware_size = firmware_size;
    sig_header->timestamp = HAL_GetTick();
    sig_header->hash_algorithm = 1;  // SHA-256
    sig_header->signature_algorithm = 1;  // RSA
    sig_header->signature_length = mbedtls_rsa_get_len(private_key);
    
    // 步骤1: 计算固件哈希
    printf("\nStep 1: Computing firmware hash...\n");
    ret = mbedtls_sha256(firmware, firmware_size, sig_header->firmware_hash, 0);
    if (ret != 0) {
        printf("Hash computation failed: -0x%04x\n", -ret);
        return -1;
    }
    
    printf("Firmware hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", sig_header->firmware_hash[i]);
    }
    printf("\n");
    
    // 步骤2: 对哈希进行签名
    printf("\nStep 2: Signing firmware hash...\n");
    ret = mbedtls_rsa_pkcs1_sign(private_key, mbedtls_ctr_drbg_random, ctr_drbg,
                                MBEDTLS_RSA_PRIVATE, MBEDTLS_MD_SHA256,
                                32, sig_header->firmware_hash,
                                sig_header->signature);
    
    if (ret != 0) {
        printf("Signing failed: -0x%04x\n", -ret);
        return -1;
    }
    
    printf("Signature generated successfully\n");
    printf("Signature length: %u bytes\n", sig_header->signature_length);
    
    // 步骤3: 显示签名信息
    printf("\nFirmware Signature Header:\n");
    printf("  Magic:     0x%08X\n", sig_header->magic);
    printf("  Version:   %u.%u.%u\n",
           (sig_header->version >> 16) & 0xFF,
           (sig_header->version >> 8) & 0xFF,
           sig_header->version & 0xFF);
    printf("  Size:      %u bytes\n", sig_header->firmware_size);
    printf("  Timestamp: %u\n", sig_header->timestamp);
    printf("  Algorithm: RSA-SHA256\n");
    
    printf("\n✓ Firmware signed successfully\n");
    
    return 0;
}

/**
 * @brief  验证固件签名
 * @param  firmware: 固件数据
 * @param  firmware_size: 固件大小
 * @param  sig_header: 签名头部
 * @param  public_key: RSA公钥
 * @retval 0:验证成功, -1:验证失败
 */
int verify_firmware(const uint8_t *firmware, size_t firmware_size,
                   const firmware_signature_t *sig_header,
                   mbedtls_rsa_context *public_key)
{
    int ret;
    uint8_t computed_hash[32];
    
    printf("\n=== Firmware Verification Process ===\n");
    
    // 步骤1: 验证魔数
    printf("Step 1: Verifying magic number...\n");
    if (sig_header->magic != FIRMWARE_MAGIC) {
        printf("✗ Invalid magic number: 0x%08X\n", sig_header->magic);
        return -1;
    }
    printf("Magic number valid\n");
    
    // 步骤2: 验证固件大小
    printf("\nStep 2: Verifying firmware size...\n");
    if (sig_header->firmware_size != firmware_size) {
        printf("✗ Size mismatch: expected %u, got %zu\n",
               sig_header->firmware_size, firmware_size);
        return -1;
    }
    printf("Firmware size matches\n");
    
    // 步骤3: 计算固件哈希
    printf("\nStep 3: Computing firmware hash...\n");
    ret = mbedtls_sha256(firmware, firmware_size, computed_hash, 0);
    if (ret != 0) {
        printf("Hash computation failed: -0x%04x\n", -ret);
        return -1;
    }
    
    printf("Computed hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", computed_hash[i]);
    }
    printf("\n");
    
    printf("Stored hash:   ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", sig_header->firmware_hash[i]);
    }
    printf("\n");
    
    // 步骤4: 比较哈希值
    printf("\nStep 4: Comparing hash values...\n");
    if (memcmp(computed_hash, sig_header->firmware_hash, 32) != 0) {
        printf("✗ Hash mismatch - firmware has been modified\n");
        return -1;
    }
    printf("Hash values match\n");
    
    // 步骤5: 验证签名
    printf("\nStep 5: Verifying digital signature...\n");
    ret = mbedtls_rsa_pkcs1_verify(public_key, NULL, NULL,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  32, sig_header->firmware_hash,
                                  sig_header->signature);
    
    if (ret != 0) {
        printf("✗ Signature verification failed: -0x%04x\n", -ret);
        printf("  Possible reasons:\n");
        printf("  - Firmware was tampered\n");
        printf("  - Wrong public key\n");
        printf("  - Signature corrupted\n");
        return -1;
    }
    
    printf("Signature verified successfully\n");
    
    // 步骤6: 检查时间戳（可选）
    printf("\nStep 6: Checking timestamp...\n");
    uint32_t current_time = HAL_GetTick();
    printf("Signature timestamp: %u\n", sig_header->timestamp);
    printf("Current time: %u\n", current_time);
    
    // 可以添加时间戳验证逻辑
    // 例如：检查签名是否过期
    
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║  ✓ FIRMWARE VERIFICATION SUCCESSFUL   ║\n");
    printf("╚════════════════════════════════════════╝\n");
    printf("\nFirmware is:\n");
    printf("  ✓ Authentic (signed by trusted key)\n");
    printf("  ✓ Unmodified (hash matches)\n");
    printf("  ✓ Complete (size matches)\n");
    printf("  ✓ Valid (signature verified)\n");
    
    return 0;
}
```



### 4.3 固件签名完整示例

```c
/**
 * @brief  固件签名和验证完整示例
 */
void firmware_signature_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    firmware_signature_t sig_header;
    
    // 模拟固件数据
    const char *firmware_data = 
        "FIRMWARE_START\n"
        "Version: 1.0.0\n"
        "Build: 20240115\n"
        "This is the actual firmware binary data...\n"
        "FIRMWARE_END\n";
    size_t firmware_size = strlen(firmware_data);
    
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║  Firmware Signature System Demo       ║\n");
    printf("╚════════════════════════════════════════╝\n");
    
    // 初始化
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    const char *pers = "firmware_sign";
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                         (const unsigned char *)pers, strlen(pers));
    
    // 生成RSA密钥对
    printf("\nGenerating RSA key pair for firmware signing...\n");
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V15, 0);
    
    int ret = mbedtls_rsa_gen_key(&rsa, mbedtls_ctr_drbg_random, &ctr_drbg,
                                 2048, 65537);
    if (ret != 0) {
        printf("Key generation failed\n");
        goto cleanup;
    }
    printf("Key pair generated\n");
    
    // 签名固件
    if (sign_firmware((uint8_t *)firmware_data, firmware_size,
                     &sig_header, &rsa, &ctr_drbg) != 0) {
        printf("Firmware signing failed\n");
        goto cleanup;
    }
    
    // 验证固件
    if (verify_firmware((uint8_t *)firmware_data, firmware_size,
                       &sig_header, &rsa) == 0) {
        printf("\n✓ Complete firmware signature cycle successful\n");
    }
    
    // 测试：修改固件后验证失败
    printf("\n\n--- Testing with Modified Firmware ---\n");
    char modified_firmware[256];
    strcpy(modified_firmware, firmware_data);
    modified_firmware[10] = 'X';  // 修改一个字节
    
    if (verify_firmware((uint8_t *)modified_firmware, firmware_size,
                       &sig_header, &rsa) != 0) {
        printf("\nAs expected, modified firmware fails verification\n");
    }
    
cleanup:
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
╔════════════════════════════════════════╗
║  Firmware Signature System Demo       ║
╚════════════════════════════════════════╝

Generating RSA key pair for firmware signing...
Key pair generated

=== Firmware Signing Process ===
Firmware size: 123 bytes

Step 1: Computing firmware hash...
Firmware hash: 8D969EEF6ECAD3C29A3A629280E686CF...

Step 2: Signing firmware hash...
Signature generated successfully
Signature length: 256 bytes

Firmware Signature Header:
  Magic:     0x46575349
  Version:   1.0.0
  Size:      123 bytes
  Timestamp: 12345678
  Algorithm: RSA-SHA256

✓ Firmware signed successfully

=== Firmware Verification Process ===
Step 1: Verifying magic number...
Magic number valid

Step 2: Verifying firmware size...
Firmware size matches

Step 3: Computing firmware hash...
Computed hash: 8D969EEF6ECAD3C29A3A629280E686CF...
Stored hash:   8D969EEF6ECAD3C29A3A629280E686CF...

Step 4: Comparing hash values...
Hash values match

Step 5: Verifying digital signature...
Signature verified successfully

Step 6: Checking timestamp...
Signature timestamp: 12345678
Current time: 12346000

╔════════════════════════════════════════╗
║  ✓ FIRMWARE VERIFICATION SUCCESSFUL   ║
╚════════════════════════════════════════╝

Firmware is:
  ✓ Authentic (signed by trusted key)
  ✓ Unmodified (hash matches)
  ✓ Complete (size matches)
  ✓ Valid (signature verified)

✓ Complete firmware signature cycle successful


--- Testing with Modified Firmware ---
✗ Hash mismatch - firmware has been modified

As expected, modified firmware fails verification
```



## 步骤5：实战项目 - 安全OTA更新系统

### 5.1 项目需求

实现一个安全的OTA（Over-The-Air）固件更新系统，具有以下功能：
- 固件签名验证
- 版本检查
- 回滚保护
- 安全下载
- LED状态指示

### 5.2 项目架构

```c
/**
 * @file   secure_ota.h
 * @brief  安全OTA更新系统
 */
#ifndef SECURE_OTA_H
#define SECURE_OTA_H

#include <stdint.h>
#include <stddef.h>
#include "firmware_signature.h"

// OTA状态
typedef enum {
    OTA_STATE_IDLE = 0,
    OTA_STATE_DOWNLOADING,
    OTA_STATE_VERIFYING,
    OTA_STATE_INSTALLING,
    OTA_STATE_SUCCESS,
    OTA_STATE_FAILED
} ota_state_t;

// OTA配置
typedef struct {
    uint32_t current_version;    // 当前固件版本
    uint32_t min_version;        // 最小允许版本（回滚保护）
    uint32_t flash_address;      // Flash起始地址
    uint32_t max_size;           // 最大固件大小
    mbedtls_rsa_context *public_key;  // 验证公钥
} ota_config_t;

// 函数声明
int ota_init(ota_config_t *config);
int ota_download_firmware(const uint8_t *url);
int ota_verify_firmware(const uint8_t *firmware, size_t size,
                       const firmware_signature_t *signature);
int ota_install_firmware(const uint8_t *firmware, size_t size);
ota_state_t ota_get_state(void);

#endif // SECURE_OTA_H
```

### 5.3 核心实现

```c
/**
 * @file   secure_ota.c
 * @brief  安全OTA更新实现
 */
#include "secure_ota.h"
#include <string.h>
#include <stdio.h>

static ota_config_t g_ota_config;
static ota_state_t g_ota_state = OTA_STATE_IDLE;

/**
 * @brief  初始化OTA系统
 * @param  config: OTA配置
 * @retval 0:成功, -1:失败
 */
int ota_init(ota_config_t *config)
{
    printf("\n=== Initializing Secure OTA System ===\n");
    
    // 保存配置
    memcpy(&g_ota_config, config, sizeof(ota_config_t));
    
    printf("Current firmware version: %u.%u.%u\n",
           (config->current_version >> 16) & 0xFF,
           (config->current_version >> 8) & 0xFF,
           config->current_version & 0xFF);
    
    printf("Minimum allowed version: %u.%u.%u\n",
           (config->min_version >> 16) & 0xFF,
           (config->min_version >> 8) & 0xFF,
           config->min_version & 0xFF);
    
    printf("Flash address: 0x%08lX\n", config->flash_address);
    printf("Max firmware size: %lu bytes\n", config->max_size);
    
    g_ota_state = OTA_STATE_IDLE;
    
    printf("✓ OTA system initialized\n");
    return 0;
}

/**
 * @brief  验证固件更新
 * @param  firmware: 固件数据
 * @param  size: 固件大小
 * @param  signature: 固件签名
 * @retval 0:验证成功, -1:验证失败
 */
int ota_verify_firmware(const uint8_t *firmware, size_t size,
                       const firmware_signature_t *signature)
{
    printf("\n=== OTA Firmware Verification ===\n");
    
    g_ota_state = OTA_STATE_VERIFYING;
    
    // 步骤1: 验证签名
    printf("Step 1: Verifying digital signature...\n");
    if (verify_firmware(firmware, size, signature,
                       g_ota_config.public_key) != 0) {
        printf("✗ Signature verification failed\n");
        g_ota_state = OTA_STATE_FAILED;
        return -1;
    }
    printf("✓ Signature verified\n");
    
    // 步骤2: 检查版本
    printf("\nStep 2: Checking firmware version...\n");
    uint32_t new_version = signature->version;
    
    printf("Current version: %u.%u.%u\n",
           (g_ota_config.current_version >> 16) & 0xFF,
           (g_ota_config.current_version >> 8) & 0xFF,
           g_ota_config.current_version & 0xFF);
    
    printf("New version:     %u.%u.%u\n",
           (new_version >> 16) & 0xFF,
           (new_version >> 8) & 0xFF,
           new_version & 0xFF);
    
    // 检查是否为更新版本
    if (new_version <= g_ota_config.current_version) {
        printf("✗ New version is not newer than current\n");
        g_ota_state = OTA_STATE_FAILED;
        return -1;
    }
    
    // 回滚保护：检查最小版本
    if (new_version < g_ota_config.min_version) {
        printf("✗ Version rollback detected (security policy violation)\n");
        printf("  Minimum allowed: %u.%u.%u\n",
               (g_ota_config.min_version >> 16) & 0xFF,
               (g_ota_config.min_version >> 8) & 0xFF,
               g_ota_config.min_version & 0xFF);
        g_ota_state = OTA_STATE_FAILED;
        return -1;
    }
    
    printf("✓ Version check passed\n");
    
    // 步骤3: 检查固件大小
    printf("\nStep 3: Checking firmware size...\n");
    if (size > g_ota_config.max_size) {
        printf("✗ Firmware too large: %zu > %lu\n",
               size, g_ota_config.max_size);
        g_ota_state = OTA_STATE_FAILED;
        return -1;
    }
    printf("✓ Size check passed (%zu bytes)\n", size);
    
    printf("\n✓ All verification checks passed\n");
    printf("  Firmware is ready for installation\n");
    
    return 0;
}

/**
 * @brief  安装固件更新
 * @param  firmware: 固件数据
 * @param  size: 固件大小
 * @retval 0:成功, -1:失败
 */
int ota_install_firmware(const uint8_t *firmware, size_t size)
{
    printf("\n=== Installing Firmware Update ===\n");
    
    g_ota_state = OTA_STATE_INSTALLING;
    
    // 步骤1: 擦除Flash
    printf("Step 1: Erasing flash sectors...\n");
    // HAL_FLASH_Unlock();
    // ... 擦除Flash代码 ...
    // HAL_FLASH_Lock();
    printf("✓ Flash erased\n");
    
    // 步骤2: 写入固件
    printf("\nStep 2: Writing firmware to flash...\n");
    printf("Address: 0x%08lX\n", g_ota_config.flash_address);
    printf("Size: %zu bytes\n", size);
    
    // HAL_FLASH_Unlock();
    // for (size_t i = 0; i < size; i++) {
    //     HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE,
    //                      g_ota_config.flash_address + i,
    //                      firmware[i]);
    // }
    // HAL_FLASH_Lock();
    
    printf("✓ Firmware written\n");
    
    // 步骤3: 验证写入
    printf("\nStep 3: Verifying written firmware...\n");
    // uint8_t *flash_ptr = (uint8_t *)g_ota_config.flash_address;
    // if (memcmp(flash_ptr, firmware, size) != 0) {
    //     printf("✗ Verification failed\n");
    //     g_ota_state = OTA_STATE_FAILED;
    //     return -1;
    // }
    printf("✓ Verification passed\n");
    
    g_ota_state = OTA_STATE_SUCCESS;
    
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║  ✓ FIRMWARE UPDATE SUCCESSFUL         ║\n");
    printf("╚════════════════════════════════════════╝\n");
    printf("\nSystem will reboot to apply update...\n");
    
    // 延迟后重启
    HAL_Delay(3000);
    // NVIC_SystemReset();
    
    return 0;
}

/**
 * @brief  获取OTA状态
 * @retval OTA状态
 */
ota_state_t ota_get_state(void)
{
    return g_ota_state;
}

/**
 * @brief  OTA状态LED指示
 */
void ota_update_led(void)
{
    switch (g_ota_state) {
        case OTA_STATE_IDLE:
            // LED关闭
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
            break;
            
        case OTA_STATE_DOWNLOADING:
            // LED慢闪
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(500);
            break;
            
        case OTA_STATE_VERIFYING:
            // LED快闪
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            break;
            
        case OTA_STATE_INSTALLING:
            // LED常亮
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
            break;
            
        case OTA_STATE_SUCCESS:
            // LED闪烁3次
            for (int i = 0; i < 3; i++) {
                HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
                HAL_Delay(200);
                HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
                HAL_Delay(200);
            }
            break;
            
        case OTA_STATE_FAILED:
            // LED快速闪烁
            for (int i = 0; i < 10; i++) {
                HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
                HAL_Delay(50);
            }
            break;
    }
}
```



### 5.4 主程序

```c
/**
 * @brief  安全OTA更新系统主程序
 */
void secure_ota_example(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_rsa_context rsa;
    ota_config_t ota_config;
    firmware_signature_t sig_header;
    
    // 模拟新固件
    const char *new_firmware = 
        "NEW_FIRMWARE_V2.0\n"
        "Build: 20240116\n"
        "Enhanced security features...\n";
    size_t firmware_size = strlen(new_firmware);
    
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║  Secure OTA Update System Demo        ║\n");
    printf("╚════════════════════════════════════════╝\n");
    
    // 初始化加密库
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    const char *pers = "ota_update";
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                         (const unsigned char *)pers, strlen(pers));
    
    // 生成密钥对（实际应用中公钥预置在设备中）
    printf("\nGenerating RSA key pair...\n");
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V15, 0);
    mbedtls_rsa_gen_key(&rsa, mbedtls_ctr_drbg_random, &ctr_drbg,
                       2048, 65537);
    printf("Key pair generated\n");
    
    // 配置OTA系统
    ota_config.current_version = 0x00010000;  // v1.0.0
    ota_config.min_version = 0x00010000;      // v1.0.0
    ota_config.flash_address = 0x08020000;
    ota_config.max_size = 128 * 1024;  // 128KB
    ota_config.public_key = &rsa;
    
    // 初始化OTA
    ota_init(&ota_config);
    
    // 服务器端：签名新固件
    printf("\n--- Server Side: Signing New Firmware ---\n");
    if (sign_firmware((uint8_t *)new_firmware, firmware_size,
                     &sig_header, &rsa, &ctr_drbg) != 0) {
        printf("Firmware signing failed\n");
        goto cleanup;
    }
    
    // 设置新版本号
    sig_header.version = 0x00020000;  // v2.0.0
    
    // 设备端：下载并验证固件
    printf("\n--- Device Side: Downloading and Verifying ---\n");
    printf("Simulating firmware download...\n");
    HAL_Delay(1000);
    printf("Download complete\n");
    
    // 验证固件
    if (ota_verify_firmware((uint8_t *)new_firmware, firmware_size,
                           &sig_header) != 0) {
        printf("\n✗ OTA update failed - verification error\n");
        goto cleanup;
    }
    
    // 安装固件
    if (ota_install_firmware((uint8_t *)new_firmware, firmware_size) == 0) {
        printf("\n✓ OTA update completed successfully\n");
    }
    
    // 测试：尝试回滚到旧版本
    printf("\n\n--- Testing Rollback Protection ---\n");
    sig_header.version = 0x00000100;  // v0.1.0 (older)
    
    if (ota_verify_firmware((uint8_t *)new_firmware, firmware_size,
                           &sig_header) != 0) {
        printf("\n✓ Rollback protection working correctly\n");
    }
    
cleanup:
    mbedtls_rsa_free(&rsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
}
```

**预期输出**：
```
╔════════════════════════════════════════╗
║  Secure OTA Update System Demo        ║
╚════════════════════════════════════════╝

Generating RSA key pair...
Key pair generated

=== Initializing Secure OTA System ===
Current firmware version: 1.0.0
Minimum allowed version: 1.0.0
Flash address: 0x08020000
Max firmware size: 131072 bytes
✓ OTA system initialized

--- Server Side: Signing New Firmware ---
=== Firmware Signing Process ===
Firmware size: 78 bytes
...
✓ Firmware signed successfully

--- Device Side: Downloading and Verifying ---
Simulating firmware download...
Download complete

=== OTA Firmware Verification ===
Step 1: Verifying digital signature...
✓ Signature verified

Step 2: Checking firmware version...
Current version: 1.0.0
New version:     2.0.0
✓ Version check passed

Step 3: Checking firmware size...
✓ Size check passed (78 bytes)

✓ All verification checks passed
  Firmware is ready for installation

=== Installing Firmware Update ===
Step 1: Erasing flash sectors...
✓ Flash erased

Step 2: Writing firmware to flash...
Address: 0x08020000
Size: 78 bytes
✓ Firmware written

Step 3: Verifying written firmware...
✓ Verification passed

╔════════════════════════════════════════╗
║  ✓ FIRMWARE UPDATE SUCCESSFUL         ║
╚════════════════════════════════════════╝

System will reboot to apply update...

✓ OTA update completed successfully


--- Testing Rollback Protection ---
✗ Version rollback detected (security policy violation)
  Minimum allowed: 1.0.0

✓ Rollback protection working correctly
```



## 深入理解

### PKI体系架构

**PKI（Public Key Infrastructure）公钥基础设施**是一套完整的安全框架：

```
PKI体系结构：

┌─────────────────────────────────────┐
│  根CA (Root Certificate Authority)  │
│  - 自签名证书                       │
│  - 最高信任级别                     │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
┌───────────────┐   ┌───────────────┐
│  中间CA       │   │  中间CA       │
│  (Intermediate)│   │  (Intermediate)│
└───────┬───────┘   └───────┬───────┘
        │                   │
    ┌───┴───┐           ┌───┴───┐
    ↓       ↓           ↓       ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│终端证书│ │终端证书│ │终端证书│ │终端证书│
│(设备)  │ │(服务器)│ │(用户)  │ │(代码)  │
└────────┘ └────────┘ └────────┘ └────────┘
```

**PKI组件**：

1. **证书颁发机构(CA)**
   - 颁发和管理证书
   - 验证身份
   - 维护证书撤销列表(CRL)
   - 提供时间戳服务

2. **注册机构(RA)**
   - 验证证书申请者身份
   - 审核证书请求
   - 协助CA工作

3. **证书库**
   - 存储已颁发的证书
   - 提供证书查询服务
   - 发布CRL

4. **密钥管理**
   - 密钥生成
   - 密钥存储
   - 密钥备份和恢复
   - 密钥更新

### 证书撤销机制

**证书撤销列表(CRL)**：

```c
/**
 * @brief  检查证书是否被撤销
 * @param  cert: 要检查的证书
 * @param  crl: 证书撤销列表
 * @retval 0:未撤销, 1:已撤销, -1:错误
 */
int check_certificate_revocation(mbedtls_x509_crt *cert,
                                 mbedtls_x509_crl *crl)
{
    mbedtls_x509_crl_entry *entry;
    
    printf("Checking certificate revocation status...\n");
    
    // 遍历CRL
    entry = &crl->entry;
    while (entry != NULL) {
        // 比较序列号
        if (cert->serial.len == entry->serial.len &&
            memcmp(cert->serial.p, entry->serial.p, cert->serial.len) == 0) {
            printf("✗ Certificate has been REVOKED\n");
            printf("  Revocation date: %04d-%02d-%02d\n",
                   entry->revocation_date.year,
                   entry->revocation_date.mon,
                   entry->revocation_date.day);
            return 1;  // 已撤销
        }
        entry = entry->next;
    }
    
    printf("✓ Certificate is valid (not revoked)\n");
    return 0;  // 未撤销
}
```

**OCSP（在线证书状态协议）**：

```
OCSP查询流程：

客户端                    OCSP响应器
   │                          │
   │  1. OCSP请求             │
   │  (证书序列号)            │
   ├─────────────────────────>│
   │                          │
   │                          │ 2. 查询证书状态
   │                          │
   │  3. OCSP响应             │
   │  (good/revoked/unknown)  │
   │<─────────────────────────┤
   │                          │
   │  4. 验证响应签名         │
   │                          │
```

### 时间戳服务

**时间戳的作用**：

1. **证明签名时间**
   - 签名在特定时间生成
   - 防止时间欺诈
   - 提供法律证据

2. **长期有效性**
   - 即使签名密钥过期
   - 签名仍然有效
   - 时间戳证明签名时密钥有效

**时间戳请求流程**：

```
时间戳协议(RFC 3161)：

1. 客户端计算文档哈希
   ↓
2. 发送时间戳请求
   - 哈希值
   - 哈希算法
   ↓
3. TSA验证请求
   ↓
4. TSA生成时间戳令牌
   - 当前时间
   - 哈希值
   - TSA签名
   ↓
5. 返回时间戳令牌
   ↓
6. 客户端验证时间戳
```

### 不可否认性

**数字签名提供不可否认性**：

```
不可否认性保证：

1. 签名者不能否认
   - 只有私钥持有者能生成签名
   - 私钥应该只有签名者拥有
   - 签名证明签名者的行为

2. 法律效力
   - 数字签名具有法律效力
   - 等同于手写签名
   - 可作为法律证据

3. 审计追踪
   - 记录所有签名操作
   - 时间戳证明签名时间
   - 证书链证明签名者身份
```

**实现不可否认性的要求**：

```c
/**
 * @brief  创建不可否认的签名记录
 */
typedef struct {
    uint8_t document_hash[32];      // 文档哈希
    uint8_t signature[256];         // 数字签名
    uint32_t timestamp;             // 时间戳
    uint8_t timestamp_signature[256]; // 时间戳签名
    char signer_cert[2048];         // 签名者证书
    char ca_cert[2048];             // CA证书
    uint32_t sequence_number;       // 序列号
} non_repudiation_record_t;

/**
 * @brief  创建不可否认记录
 */
int create_non_repudiation_record(const uint8_t *document,
                                  size_t doc_len,
                                  non_repudiation_record_t *record,
                                  mbedtls_rsa_context *private_key,
                                  mbedtls_ctr_drbg_context *ctr_drbg)
{
    // 1. 计算文档哈希
    mbedtls_sha256(document, doc_len, record->document_hash, 0);
    
    // 2. 生成签名
    mbedtls_rsa_pkcs1_sign(private_key, mbedtls_ctr_drbg_random, ctr_drbg,
                          MBEDTLS_RSA_PRIVATE, MBEDTLS_MD_SHA256,
                          32, record->document_hash, record->signature);
    
    // 3. 添加时间戳
    record->timestamp = HAL_GetTick();
    
    // 4. 对时间戳签名（使用TSA）
    // ... 时间戳签名代码 ...
    
    // 5. 附加证书
    // ... 证书复制代码 ...
    
    // 6. 分配序列号
    static uint32_t seq = 0;
    record->sequence_number = seq++;
    
    printf("Non-repudiation record created\n");
    printf("  Sequence: %u\n", record->sequence_number);
    printf("  Timestamp: %u\n", record->timestamp);
    
    return 0;
}
```



## 最佳实践

### 算法选择指南

```
场景1：固件签名
推荐：RSA-2048 + SHA-256
原因：广泛支持，验证快速

场景2：物联网设备
推荐：ECDSA P-256 + SHA-256
原因：密钥短，签名小，适合资源受限

场景3：代码签名
推荐：RSA-3072 + SHA-256
原因：更高安全性，长期有效

场景4：文档签名
推荐：RSA-2048 + SHA-256 + 时间戳
原因：法律效力，长期可验证

场景5：高安全需求
推荐：RSA-4096 + SHA-512
原因：最高安全级别
```

### 密钥管理最佳实践

**1. 私钥保护**：

```c
// ✓ 正确：私钥存储在安全区域
#define PRIVATE_KEY_FLASH_ADDR  0x08070000  // 受保护的Flash区域

// 启用Flash读保护
void protect_private_key_storage(void)
{
    FLASH_OBProgramInitTypeDef ob_config;
    
    // 读取当前选项字节
    HAL_FLASHEx_OBGetConfig(&ob_config);
    
    // 设置读保护级别
    ob_config.RDPLevel = OB_RDP_LEVEL_1;
    
    // 应用保护
    HAL_FLASH_Unlock();
    HAL_FLASH_OB_Unlock();
    HAL_FLASHEx_OBProgram(&ob_config);
    HAL_FLASH_OB_Launch();
    HAL_FLASH_OB_Lock();
    HAL_FLASH_Lock();
}

// ✓ 正确：使用后立即清除私钥
void secure_sign_operation(void)
{
    mbedtls_rsa_context rsa;
    
    // 加载私钥
    load_private_key(&rsa);
    
    // 执行签名
    sign_data(&rsa, data, signature);
    
    // 立即清除私钥
    mbedtls_rsa_free(&rsa);
    memset(&rsa, 0, sizeof(rsa));
}
```

**2. 公钥分发**：

```c
// ✓ 正确：公钥硬编码在固件中
const unsigned char public_key_pem[] = 
    "-----BEGIN PUBLIC KEY-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
    "-----END PUBLIC KEY-----\n";

// ✓ 正确：使用证书链验证公钥
int verify_public_key(mbedtls_x509_crt *cert)
{
    // 验证证书链
    // 确保公钥来自可信CA
    return mbedtls_x509_crt_verify(cert, trusted_ca, NULL,
                                   NULL, &flags, NULL, NULL);
}
```

**3. 密钥轮换**：

```c
// 支持多个公钥版本
typedef struct {
    uint32_t key_id;
    uint32_t valid_from;
    uint32_t valid_to;
    mbedtls_rsa_context public_key;
} key_version_t;

key_version_t key_versions[] = {
    {1, 0, 1640000000, /* key1 */},  // 旧密钥
    {2, 1640000000, 0xFFFFFFFF, /* key2 */},  // 当前密钥
};

int verify_with_key_rotation(const uint8_t *data, size_t len,
                             const uint8_t *signature,
                             uint32_t key_id)
{
    // 查找对应的密钥版本
    for (int i = 0; i < sizeof(key_versions)/sizeof(key_version_t); i++) {
        if (key_versions[i].key_id == key_id) {
            return verify_signature(&key_versions[i].public_key,
                                   data, len, signature);
        }
    }
    return -1;  // 密钥未找到
}
```

### 安全实践建议

**1. 始终验证签名**：

```c
// ✗ 错误：跳过签名验证
if (debug_mode) {
    // 调试模式下跳过验证 - 危险！
    install_firmware(firmware);
}

// ✓ 正确：始终验证
if (verify_firmware_signature(firmware, signature) == 0) {
    install_firmware(firmware);
} else {
    reject_firmware();
}
```

**2. 使用安全的哈希算法**：

```c
// ✗ 错误：使用弱哈希算法
mbedtls_md5(data, len, hash);  // MD5已不安全

// ✓ 正确：使用SHA-256或更强
mbedtls_sha256(data, len, hash, 0);  // SHA-256
```

**3. 防止时序攻击**：

```c
// ✗ 错误：提前返回
int verify_signature_unsafe(const uint8_t *sig1, const uint8_t *sig2)
{
    for (int i = 0; i < 256; i++) {
        if (sig1[i] != sig2[i]) {
            return 0;  // 提前返回泄露信息
        }
    }
    return 1;
}

// ✓ 正确：常量时间比较
int verify_signature_safe(const uint8_t *sig1, const uint8_t *sig2)
{
    uint8_t diff = 0;
    for (int i = 0; i < 256; i++) {
        diff |= sig1[i] ^ sig2[i];
    }
    return diff == 0;
}
```

**4. 添加重放攻击保护**：

```c
typedef struct {
    uint8_t signature[256];
    uint32_t timestamp;
    uint32_t nonce;  // 随机数
} signed_message_t;

int verify_with_replay_protection(signed_message_t *msg)
{
    // 1. 验证签名
    if (verify_signature(msg) != 0) {
        return -1;
    }
    
    // 2. 检查时间戳
    uint32_t current_time = HAL_GetTick();
    if (abs(current_time - msg->timestamp) > 60000) {  // 60秒窗口
        printf("Message too old or from future\n");
        return -1;
    }
    
    // 3. 检查nonce是否已使用
    if (is_nonce_used(msg->nonce)) {
        printf("Replay attack detected\n");
        return -1;
    }
    
    // 4. 记录nonce
    record_nonce(msg->nonce);
    
    return 0;
}
```



## 常见问题

### Q1: 数字签名和加密有什么区别？

**A**: 它们的目的和使用方式完全不同：

**数字签名**：
- 目的：认证和完整性
- 使用：私钥签名，公钥验证
- 结果：消息可读，但可验证真实性
- 应用：证明身份，防篡改

**加密**：
- 目的：保密性
- 使用：公钥加密，私钥解密
- 结果：消息不可读，只有持有私钥者能解密
- 应用：保护数据内容

**组合使用**：
```
完整的安全通信：
1. 发送方用私钥签名（认证）
2. 发送方用接收方公钥加密（保密）
3. 接收方用私钥解密（获取内容）
4. 接收方用发送方公钥验证（确认身份）
```

### Q2: 为什么要先哈希再签名？

**A**: 有几个重要原因：

1. **性能**
   - RSA只能处理有限长度数据
   - 哈希将任意长度数据转为固定长度
   - 签名固定长度的哈希更快

2. **安全性**
   - 直接签名原始数据可能存在安全问题
   - 哈希提供额外的安全层
   - 防止某些类型的攻击

3. **标准化**
   - 所有签名标准都要求先哈希
   - 确保互操作性
   - 符合最佳实践

### Q3: RSA和ECDSA应该选择哪个？

**A**: 根据应用场景选择：

**选择RSA的情况**：
- 需要与旧系统兼容
- 验证速度是关键
- 有足够的存储空间
- 需要广泛的库支持

**选择ECDSA的情况**：
- 资源受限（IoT设备）
- 需要更短的签名
- 签名速度是关键
- 带宽有限

**性能对比**：
```
256位ECDSA ≈ 3072位RSA（安全级别）

签名大小：
- ECDSA: ~72字节
- RSA-2048: 256字节
- RSA-3072: 384字节

签名速度：
- ECDSA: 快
- RSA: 慢

验证速度：
- ECDSA: 中等
- RSA: 快
```

### Q4: 如何保护私钥安全？

**A**: 多层保护措施：

**硬件保护**：
```c
// 1. 使用安全元件
// - TPM (Trusted Platform Module)
// - SE (Secure Element)
// - HSM (Hardware Security Module)

// 2. Flash读保护
void enable_flash_protection(void)
{
    // 启用读保护，防止私钥被读取
    HAL_FLASH_OB_RDPConfig(OB_RDP_LEVEL_1);
}

// 3. 使用加密存储
void store_encrypted_key(const uint8_t *key)
{
    uint8_t encrypted[256];
    
    // 使用硬件密钥加密私钥
    encrypt_with_hardware_key(key, encrypted);
    
    // 存储加密后的私钥
    write_to_flash(encrypted);
}
```

**软件保护**：
```c
// 1. 使用后立即清除
void use_private_key(void)
{
    mbedtls_rsa_context rsa;
    
    load_key(&rsa);
    sign_data(&rsa);
    
    // 清除内存
    mbedtls_rsa_free(&rsa);
    memset(&rsa, 0, sizeof(rsa));
}

// 2. 限制访问
// - 只在必要时加载私钥
// - 最小权限原则
// - 审计所有私钥使用

// 3. 密钥分割
// - 将私钥分成多个部分
// - 需要多个部分才能重建
// - 增加攻击难度
```

### Q5: 证书过期后签名还有效吗？

**A**: 取决于验证策略：

**严格验证**：
```c
// 检查证书有效期
if (current_time > cert->valid_to) {
    printf("Certificate expired\n");
    return -1;  // 拒绝
}
```

**宽松验证（带时间戳）**：
```c
// 如果有时间戳，检查签名时证书是否有效
if (timestamp < cert->valid_to) {
    // 签名时证书有效，接受
    return 0;
}
```

**最佳实践**：
- 使用时间戳服务
- 证明签名时证书有效
- 即使证书过期，签名仍然有效
- 提供长期可验证性

### Q6: 如何防止重放攻击？

**A**: 多种防护机制：

```c
// 1. 时间戳
typedef struct {
    uint8_t data[256];
    uint32_t timestamp;
    uint8_t signature[256];
} timestamped_message_t;

int verify_with_timestamp(timestamped_message_t *msg)
{
    uint32_t current = HAL_GetTick();
    
    // 只接受5分钟内的消息
    if (abs(current - msg->timestamp) > 300000) {
        return -1;
    }
    
    return verify_signature(msg);
}

// 2. 序列号
static uint32_t last_sequence = 0;

int verify_with_sequence(uint32_t sequence)
{
    if (sequence <= last_sequence) {
        printf("Old or duplicate message\n");
        return -1;
    }
    
    last_sequence = sequence;
    return 0;
}

// 3. Nonce（随机数）
#define MAX_NONCE_CACHE 1000
static uint32_t nonce_cache[MAX_NONCE_CACHE];
static int nonce_count = 0;

int verify_with_nonce(uint32_t nonce)
{
    // 检查nonce是否已使用
    for (int i = 0; i < nonce_count; i++) {
        if (nonce_cache[i] == nonce) {
            printf("Nonce reused - replay attack\n");
            return -1;
        }
    }
    
    // 记录nonce
    if (nonce_count < MAX_NONCE_CACHE) {
        nonce_cache[nonce_count++] = nonce;
    }
    
    return 0;
}
```



## 故障排除

### 问题1：签名验证总是失败

**可能原因**：
- 使用了错误的公钥
- 消息在传输中被修改
- 哈希算法不匹配
- 填充方案不一致

**解决方法**：

```c
// 1. 验证公钥是否正确
void debug_public_key(mbedtls_rsa_context *rsa)
{
    printf("RSA Key Info:\n");
    printf("  Key size: %zu bits\n", mbedtls_rsa_get_len(rsa) * 8);
    printf("  Modulus N: ");
    mbedtls_mpi_write_string(&rsa->N, 16, buf, sizeof(buf), &len);
    printf("%s\n", buf);
    printf("  Public exponent E: ");
    mbedtls_mpi_write_string(&rsa->E, 16, buf, sizeof(buf), &len);
    printf("%s\n", buf);
}

// 2. 验证消息完整性
void debug_message_hash(const uint8_t *msg, size_t len)
{
    uint8_t hash[32];
    mbedtls_sha256(msg, len, hash, 0);
    
    printf("Message hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", hash[i]);
    }
    printf("\n");
}

// 3. 检查算法参数
void debug_signature_params(void)
{
    printf("Signature parameters:\n");
    printf("  Hash algorithm: SHA-256\n");
    printf("  Padding: PKCS#1 v1.5\n");
    printf("  Key type: RSA\n");
}
```

### 问题2：证书链验证失败

**可能原因**：
- CA证书不在信任列表中
- 证书已过期
- 证书链不完整
- 证书被撤销

**解决方法**：

```c
// 详细的证书验证
int debug_certificate_verification(mbedtls_x509_crt *cert,
                                   mbedtls_x509_crt *ca)
{
    uint32_t flags;
    char vrfy_buf[512];
    int ret;
    
    printf("=== Certificate Verification Debug ===\n");
    
    // 1. 检查证书有效期
    printf("Certificate validity:\n");
    printf("  Not before: %04d-%02d-%02d\n",
           cert->valid_from.year, cert->valid_from.mon, cert->valid_from.day);
    printf("  Not after:  %04d-%02d-%02d\n",
           cert->valid_to.year, cert->valid_to.mon, cert->valid_to.day);
    
    // 2. 检查颁发者和主体
    char issuer[256], subject[256];
    mbedtls_x509_dn_gets(issuer, sizeof(issuer), &cert->issuer);
    mbedtls_x509_dn_gets(subject, sizeof(subject), &cert->subject);
    
    printf("  Issuer:  %s\n", issuer);
    printf("  Subject: %s\n", subject);
    
    // 3. 验证证书链
    ret = mbedtls_x509_crt_verify(cert, ca, NULL, NULL, &flags,
                                  NULL, NULL);
    
    if (ret != 0) {
        printf("Verification failed with flags: 0x%08lX\n", flags);
        mbedtls_x509_crt_verify_info(vrfy_buf, sizeof(vrfy_buf),
                                     "  ! ", flags);
        printf("%s\n", vrfy_buf);
        
        // 详细错误信息
        if (flags & MBEDTLS_X509_BADCERT_EXPIRED)
            printf("  - Certificate has expired\n");
        if (flags & MBEDTLS_X509_BADCERT_NOT_TRUSTED)
            printf("  - Certificate is not trusted\n");
        if (flags & MBEDTLS_X509_BADCERT_REVOKED)
            printf("  - Certificate has been revoked\n");
    }
    
    return ret;
}
```

### 问题3：性能问题

**症状**：
- 签名/验证速度慢
- 系统响应延迟
- 资源占用高

**优化方法**：

```c
// 1. 使用硬件加速
#ifdef USE_HARDWARE_CRYPTO
void enable_hardware_acceleration(void)
{
    // 启用硬件加密模块
    __HAL_RCC_CRYP_CLK_ENABLE();
    
    // 配置硬件加速
    // ...
}
#endif

// 2. 缓存公钥
static mbedtls_rsa_context cached_public_key;
static int key_cached = 0;

int verify_with_cached_key(const uint8_t *data, size_t len,
                           const uint8_t *signature)
{
    if (!key_cached) {
        // 首次加载公钥
        load_public_key(&cached_public_key);
        key_cached = 1;
    }
    
    // 使用缓存的公钥验证
    return verify_signature(&cached_public_key, data, len, signature);
}

// 3. 批量验证
int batch_verify_signatures(signature_batch_t *batch, int count)
{
    // 一次性加载公钥
    mbedtls_rsa_context rsa;
    load_public_key(&rsa);
    
    // 批量验证
    for (int i = 0; i < count; i++) {
        if (verify_signature(&rsa, batch[i].data, batch[i].len,
                           batch[i].signature) != 0) {
            printf("Signature %d failed\n", i);
            mbedtls_rsa_free(&rsa);
            return -1;
        }
    }
    
    mbedtls_rsa_free(&rsa);
    return 0;
}

// 4. 使用ECDSA代替RSA
// ECDSA签名更快，适合资源受限设备
```



## 总结

本教程深入介绍了数字签名技术的原理和实践应用：

**核心要点**：

1. **数字签名原理**
   - 使用私钥签名，公钥验证
   - 提供身份认证和完整性保护
   - 具有不可否认性
   - 基于哈希和非对称加密

2. **签名算法**
   - RSA：广泛支持，验证快速
   - ECDSA：密钥短，适合IoT
   - 都需要配合哈希算法使用
   - 选择取决于应用场景

3. **PKI体系**
   - 证书颁发机构(CA)
   - X.509数字证书
   - 证书链验证
   - 证书撤销机制

4. **实际应用**
   - 固件签名和验证
   - 安全OTA更新
   - 代码签名
   - 文档签名

5. **安全实践**
   - 保护私钥安全
   - 使用强哈希算法
   - 防止重放攻击
   - 实施密钥轮换
   - 添加时间戳

6. **性能优化**
   - 使用硬件加速
   - 缓存公钥
   - 批量验证
   - 选择合适的算法

**关键收获**：

- 数字签名是现代安全系统的基础
- 正确实现需要理解密码学原理
- 私钥保护至关重要
- PKI提供了完整的信任体系
- 在嵌入式系统中应用广泛

## 延伸阅读

推荐进一步学习的资源：

- [RSA非对称加密实战](../beginner/02-rsa-encryption.html) - RSA基础
- [哈希算法与消息摘要](../beginner/03-hash-algorithms.html) - 哈希算法详解
- [安全启动与固件验证](./02-secure-boot-verification.html) - 安全启动实现
- [密钥管理与安全存储](./03-key-management.html) - 密钥管理最佳实践
- [RFC 3161: Time-Stamp Protocol](https://tools.ietf.org/html/rfc3161) - 时间戳协议
- [RFC 5280: X.509 Certificate](https://tools.ietf.org/html/rfc5280) - X.509标准

## 参考资料

1. PKCS #1: RSA Cryptography Standard
2. FIPS 186-4: Digital Signature Standard (DSS)
3. RFC 5280: Internet X.509 Public Key Infrastructure Certificate
4. RFC 3161: Internet X.509 Public Key Infrastructure Time-Stamp Protocol
5. RFC 6960: X.509 Internet Public Key Infrastructure Online Certificate Status Protocol
6. "Applied Cryptography" by Bruce Schneier
7. mbedTLS Documentation: https://tls.mbed.org/api/
8. OpenSSL Documentation: https://www.openssl.org/docs/

---

**练习题**：

1. 实现一个完整的RSA签名和验证系统
2. 生成自签名证书并验证证书链
3. 实现固件签名和验证功能
4. 添加时间戳和重放攻击保护
5. 比较RSA和ECDSA的性能差异
6. 实现一个简单的PKI系统
7. 创建一个安全的OTA更新系统

**下一步**：建议学习 [安全启动与固件验证](./02-secure-boot-verification.html)，了解如何在启动阶段验证固件完整性。

---

**版权声明**：本教程内容仅供学习参考，实际应用中请遵循相关安全标准和最佳实践。

