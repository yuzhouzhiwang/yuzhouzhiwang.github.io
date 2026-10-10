---
title: "密钥管理与安全存储：保护嵌入式系统的核心机密"
description: "全面学习密钥管理的核心概念和最佳实践，掌握密钥生成、存储、分发和更新的安全方法，了解硬件安全模块和密钥保护技术，构建安全可靠的密钥管理体系"
slug: "key-management"

# 分类信息
domain: "中间件层"
module: "安全与加密"
content_type: "article"
skill_level: "intermediate"

# 标签和关联
tags:
  - 密钥管理
  - 安全存储
  - 密码学
  - HSM
  - 密钥保护
prerequisites:
  - "04-middleware-layer/05-security-encryption/beginner/01-aes-encryption"
  - "04-middleware-layer/05-security-encryption/beginner/02-rsa-encryption"
related_contents:
  - "04-middleware-layer/05-security-encryption/intermediate/01-digital-signature"
  - "04-middleware-layer/05-security-encryption/intermediate/02-secure-boot-verification"

# 学习信息
estimated_time: 50
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
  - 密钥管理
  - 安全存储
  - 密钥生成
  - 密钥分发
  - 硬件安全模块
cover_image: ""
---

# 密钥管理与安全存储：保护嵌入式系统的核心机密


## 概述

密钥是加密系统的核心，就像房门的钥匙一样重要。无论加密算法多么强大，如果密钥管理不当，整个系统的安全性都会受到威胁。本文将深入探讨嵌入式系统中的密钥管理策略和安全存储技术。

完成本文学习后，你将能够：

- 理解密钥管理的核心概念和生命周期
- 掌握安全的密钥生成方法和随机数生成技术
- 了解密钥存储的各种方案及其安全性对比
- 熟悉密钥分发和交换的安全协议
- 掌握密钥更新和轮换的最佳实践
- 了解硬件安全模块(HSM)和安全元件的应用
- 能够设计和实现安全的密钥管理系统
- 掌握密钥管理的常见安全陷阱和防范措施

## 背景知识

### 为什么密钥管理如此重要

在密码学中有一个著名的原则：**Kerckhoffs原则**（Kerckhoffs's Principle）

> "密码系统的安全性应该依赖于密钥的保密性，而不是算法的保密性"

这意味着：
- 即使攻击者知道你使用的加密算法
- 只要密钥保密，系统仍然是安全的
- 但如果密钥泄露，再强的算法也无法保护数据

**现实案例**：


```
案例1：硬编码密钥泄露
某智能门锁产品在固件中硬编码了AES密钥，
攻击者通过逆向工程提取密钥，
导致所有使用该产品的用户都面临安全风险。

案例2：密钥存储不当
某物联网设备将密钥明文存储在Flash中，
攻击者通过物理访问读取Flash内容，
获取密钥后可以伪造设备身份。

案例3：密钥未及时更新
某系统使用同一密钥多年未更新，
攻击者通过长期监听积累足够数据，
最终通过密码分析破解密钥。
```

### 密钥管理的挑战

嵌入式系统面临的特殊挑战：

1. **资源受限**
   - 有限的存储空间
   - 有限的计算能力
   - 有限的功耗预算
   - 难以实现复杂的安全机制

2. **物理访问风险**
   - 设备可能被物理接触
   - Flash内容可能被读取
   - 调试接口可能被利用
   - 侧信道攻击风险

3. **长生命周期**
   - 设备可能运行多年
   - 难以进行固件更新
   - 密钥需要长期有效
   - 安全威胁不断演变

4. **大规模部署**
   - 每个设备需要唯一密钥
   - 密钥分发和管理复杂
   - 难以追踪和撤销
   - 批量生产的安全性

## 密钥生命周期管理

密钥管理是一个完整的生命周期过程：

```
密钥生命周期：

┌─────────────┐
│  密钥生成   │ ← 使用安全随机数生成器
└──────┬──────┘
       ↓
┌─────────────┐
│  密钥存储   │ ← 加密存储或硬件保护
└──────┬──────┘
       ↓
┌─────────────┐
│  密钥分发   │ ← 安全通道传输
└──────┬──────┘
       ↓
┌─────────────┐
│  密钥使用   │ ← 访问控制和审计
└──────┬──────┘
       ↓
┌─────────────┐
│  密钥更新   │ ← 定期轮换
└──────┬──────┘
       ↓
┌─────────────┐
│  密钥销毁   │ ← 安全擦除
└─────────────┘
```

### 密钥生成

**核心原则**：密钥必须具有足够的随机性和不可预测性。

#### 随机数生成器类型

| 类型 | 特点 | 适用场景 | 安全性 |
|------|------|----------|--------|
| TRNG | 真随机数，基于物理噪声 | 密钥生成 | 最高 |
| PRNG | 伪随机数，算法生成 | 一般应用 | 中等 |
| CSPRNG | 密码学安全的伪随机数 | 密码学应用 | 高 |

**TRNG（真随机数生成器）**：


```c
/**
 * @brief  使用硬件TRNG生成密钥
 * @note   STM32F4系列部分型号支持硬件RNG
 */
#include "stm32f4xx_hal.h"

int generate_key_with_trng(uint8_t *key, size_t key_len)
{
    RNG_HandleTypeDef hrng;
    
    // 初始化硬件RNG
    hrng.Instance = RNG;
    if (HAL_RNG_Init(&hrng) != HAL_OK) {
        return -1;
    }
    
    // 生成随机密钥
    for (size_t i = 0; i < key_len; i += 4) {
        uint32_t random;
        if (HAL_RNG_GenerateRandomNumber(&hrng, &random) != HAL_OK) {
            HAL_RNG_DeInit(&hrng);
            return -1;
        }
        
        // 复制到密钥缓冲区
        size_t copy_len = (key_len - i) < 4 ? (key_len - i) : 4;
        memcpy(&key[i], &random, copy_len);
    }
    
    HAL_RNG_DeInit(&hrng);
    
    printf("Generated %zu-byte key using TRNG\n", key_len);
    return 0;
}
```

**CSPRNG（密码学安全的伪随机数生成器）**：

```c
/**
 * @brief  使用CSPRNG生成密钥
 * @note   基于mbedTLS的CTR_DRBG
 */
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

int generate_key_with_csprng(uint8_t *key, size_t key_len)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    const char *personalization = "key_generation";
    int ret;
    
    // 初始化熵源和DRBG
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    // 种子化DRBG
    ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                (const unsigned char *)personalization,
                                strlen(personalization));
    if (ret != 0) {
        printf("DRBG seed failed: -0x%04x\n", -ret);
        goto cleanup;
    }
    
    // 生成随机密钥
    ret = mbedtls_ctr_drbg_random(&ctr_drbg, key, key_len);
    if (ret != 0) {
        printf("Random generation failed: -0x%04x\n", -ret);
        goto cleanup;
    }
    
    printf("Generated %zu-byte key using CSPRNG\n", key_len);
    
cleanup:
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return ret;
}
```

**密钥派生函数（KDF）**：

从主密钥派生子密钥：

```c
/**
 * @brief  使用PBKDF2从密码派生密钥
 * @param  password: 用户密码
 * @param  salt: 盐值（随机数）
 * @param  iterations: 迭代次数
 * @param  key: 输出密钥
 */
#include "mbedtls/pkcs5.h"

int derive_key_from_password(const char *password,
                             const uint8_t *salt, size_t salt_len,
                             uint32_t iterations,
                             uint8_t *key, size_t key_len)
{
    mbedtls_md_context_t md_ctx;
    int ret;
    
    // 初始化MD上下文
    mbedtls_md_init(&md_ctx);
    
    // 设置哈希算法（SHA-256）
    const mbedtls_md_info_t *md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    ret = mbedtls_md_setup(&md_ctx, md_info, 1);
    if (ret != 0) {
        printf("MD setup failed: -0x%04x\n", -ret);
        mbedtls_md_free(&md_ctx);
        return ret;
    }
    
    // 使用PBKDF2派生密钥
    ret = mbedtls_pkcs5_pbkdf2_hmac(&md_ctx,
                                    (const unsigned char *)password, strlen(password),
                                    salt, salt_len,
                                    iterations,
                                    key_len, key);
    
    if (ret != 0) {
        printf("PBKDF2 failed: -0x%04x\n", -ret);
    } else {
        printf("Derived %zu-byte key from password\n", key_len);
        printf("Iterations: %u\n", iterations);
    }
    
    mbedtls_md_free(&md_ctx);
    return ret;
}
```

**密钥生成最佳实践**：

1. **使用硬件RNG**
   - 优先使用芯片内置的TRNG
   - 确保RNG已正确初始化
   - 检查RNG的健康状态

2. **足够的熵源**
   - 使用多个熵源
   - 混合不同来源的随机性
   - 定期重新种子化

3. **密钥长度**
   - AES-128: 128位密钥
   - AES-256: 256位密钥
   - RSA: 至少2048位
   - ECDSA: 至少256位

4. **避免弱密钥**
   - 不使用全0或全1
   - 不使用简单模式
   - 验证密钥的随机性

### 密钥存储

密钥存储是密钥管理中最关键的环节。

#### 存储方案对比

| 方案 | 安全性 | 成本 | 复杂度 | 适用场景 |
|------|--------|------|--------|----------|
| 明文存储 | 极低 | 低 | 低 | 不推荐 |
| 加密存储 | 中等 | 低 | 中 | 一般应用 |
| OTP存储 | 高 | 中 | 中 | 设备唯一密钥 |
| 安全元件 | 很高 | 高 | 高 | 高安全应用 |
| HSM | 最高 | 很高 | 高 | 关键基础设施 |

#### 方案1：加密存储

使用主密钥加密存储的密钥：


```c
/**
 * @brief  密钥加密存储系统
 */
#include "mbedtls/aes.h"

// 密钥存储结构
typedef struct {
    uint8_t encrypted_key[32];  // 加密后的密钥
    uint8_t iv[16];             // 初始化向量
    uint32_t crc;               // CRC校验
    uint32_t version;           // 版本号
} encrypted_key_storage_t;

/**
 * @brief  存储加密密钥到Flash
 * @param  key: 要存储的密钥
 * @param  key_len: 密钥长度
 * @param  master_key: 主密钥（用于加密）
 * @param  storage_addr: Flash存储地址
 */
int store_encrypted_key(const uint8_t *key, size_t key_len,
                       const uint8_t *master_key,
                       uint32_t storage_addr)
{
    encrypted_key_storage_t storage;
    mbedtls_aes_context aes;
    uint8_t padded_key[32] = {0};
    
    printf("Storing encrypted key...\n");
    
    // 准备数据
    memcpy(padded_key, key, key_len);
    
    // 生成随机IV
    generate_key_with_trng(storage.iv, 16);
    
    // 初始化AES
    mbedtls_aes_init(&aes);
    mbedtls_aes_setkey_enc(&aes, master_key, 256);
    
    // 加密密钥
    mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, 32,
                         storage.iv, padded_key, storage.encrypted_key);
    
    // 计算CRC
    storage.crc = calculate_crc32(storage.encrypted_key, 32);
    storage.version = 1;
    
    // 写入Flash
    int ret = write_to_flash(storage_addr, (uint8_t*)&storage, sizeof(storage));
    
    mbedtls_aes_free(&aes);
    
    if (ret == 0) {
        printf("Key stored successfully at 0x%08lX\n", storage_addr);
    }
    
    return ret;
}

/**
 * @brief  从Flash读取并解密密钥
 * @param  key: 输出密钥缓冲区
 * @param  key_len: 密钥长度
 * @param  master_key: 主密钥（用于解密）
 * @param  storage_addr: Flash存储地址
 */
int load_encrypted_key(uint8_t *key, size_t key_len,
                      const uint8_t *master_key,
                      uint32_t storage_addr)
{
    encrypted_key_storage_t storage;
    mbedtls_aes_context aes;
    uint8_t decrypted[32];
    
    printf("Loading encrypted key...\n");
    
    // 从Flash读取
    memcpy(&storage, (void*)storage_addr, sizeof(storage));
    
    // 验证CRC
    uint32_t calculated_crc = calculate_crc32(storage.encrypted_key, 32);
    if (calculated_crc != storage.crc) {
        printf("CRC mismatch - data corrupted\n");
        return -1;
    }
    
    // 初始化AES
    mbedtls_aes_init(&aes);
    mbedtls_aes_setkey_dec(&aes, master_key, 256);
    
    // 解密密钥
    mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_DECRYPT, 32,
                         storage.iv, storage.encrypted_key, decrypted);
    
    // 复制到输出缓冲区
    memcpy(key, decrypted, key_len);
    
    mbedtls_aes_free(&aes);
    
    printf("Key loaded successfully\n");
    return 0;
}
```

**主密钥保护**：

主密钥本身需要特殊保护：

```c
/**
 * @brief  从设备唯一ID派生主密钥
 * @note   利用芯片的唯一ID作为密钥材料
 */
int derive_master_key_from_uid(uint8_t *master_key)
{
    // 读取STM32的唯一ID（96位）
    uint32_t uid[3];
    uid[0] = *(uint32_t*)(UID_BASE);
    uid[1] = *(uint32_t*)(UID_BASE + 4);
    uid[2] = *(uint32_t*)(UID_BASE + 8);
    
    // 添加应用特定的盐值
    const char *app_salt = "MySecureApp_v1.0";
    
    // 使用PBKDF2派生主密钥
    uint8_t salt[32];
    memcpy(salt, uid, 12);
    memcpy(salt + 12, app_salt, strlen(app_salt));
    
    return derive_key_from_password("", salt, 32, 10000, master_key, 32);
}
```

#### 方案2：OTP（一次性可编程）存储

使用芯片的OTP区域存储密钥：

```c
/**
 * @brief  将密钥写入OTP区域
 * @note   OTP只能写入一次，无法修改
 */
int write_key_to_otp(const uint8_t *key, size_t key_len)
{
    // STM32F4的OTP区域地址
    #define OTP_BASE_ADDR 0x1FFF7800
    #define OTP_KEY_OFFSET 0x20  // 使用偏移地址
    
    uint32_t otp_addr = OTP_BASE_ADDR + OTP_KEY_OFFSET;
    
    printf("Writing key to OTP...\n");
    printf("WARNING: This operation is irreversible!\n");
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 写入密钥到OTP
    for (size_t i = 0; i < key_len; i++) {
        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_BYTE,
                             otp_addr + i, key[i]) != HAL_OK) {
            printf("OTP write failed at offset %zu\n", i);
            HAL_FLASH_Lock();
            return -1;
        }
    }
    
    // 锁定Flash
    HAL_FLASH_Lock();
    
    printf("Key written to OTP successfully\n");
    printf("Address: 0x%08lX\n", otp_addr);
    
    return 0;
}

/**
 * @brief  从OTP区域读取密钥
 */
int read_key_from_otp(uint8_t *key, size_t key_len)
{
    #define OTP_BASE_ADDR 0x1FFF7800
    #define OTP_KEY_OFFSET 0x20
    
    uint32_t otp_addr = OTP_BASE_ADDR + OTP_KEY_OFFSET;
    
    // 直接从OTP读取
    memcpy(key, (void*)otp_addr, key_len);
    
    printf("Key read from OTP\n");
    return 0;
}
```

**OTP存储优势**：
- 物理上不可修改
- 抗篡改能力强
- 适合存储设备唯一密钥
- 不需要额外的安全芯片

**OTP存储限制**：
- 只能写入一次
- 容量有限（通常512字节）
- 写入错误无法纠正
- 需要谨慎规划使用

#### 方案3：安全元件（Secure Element）

使用专用的安全芯片存储密钥：


```c
/**
 * @brief  使用ATECC608安全元件存储密钥
 * @note   ATECC608是Microchip的安全认证芯片
 */

// ATECC608密钥槽配置
typedef struct {
    uint8_t slot_id;        // 密钥槽ID (0-15)
    uint8_t key_type;       // 密钥类型
    uint16_t key_config;    // 密钥配置
    bool is_secret;         // 是否为私密密钥
    bool can_generate;      // 是否可以生成密钥
} atecc608_key_slot_t;

/**
 * @brief  在ATECC608中生成密钥
 * @param  slot_id: 密钥槽ID
 */
int atecc608_generate_key(uint8_t slot_id)
{
    printf("Generating key in ATECC608 slot %d...\n", slot_id);
    
    // 发送生成密钥命令
    // 密钥在芯片内部生成，永不离开芯片
    uint8_t cmd[] = {0x03, 0x07, 0x00, slot_id};
    
    // 通过I2C发送命令
    if (i2c_write(ATECC608_ADDR, cmd, sizeof(cmd)) != 0) {
        printf("Command send failed\n");
        return -1;
    }
    
    // 等待命令完成
    HAL_Delay(50);
    
    // 读取响应
    uint8_t response[4];
    if (i2c_read(ATECC608_ADDR, response, sizeof(response)) != 0) {
        printf("Response read failed\n");
        return -1;
    }
    
    if (response[0] == 0x00) {
        printf("Key generated successfully in slot %d\n", slot_id);
        printf("Note: Key never leaves the secure element\n");
        return 0;
    }
    
    printf("Key generation failed: 0x%02X\n", response[0]);
    return -1;
}

/**
 * @brief  使用ATECC608中的密钥进行加密
 * @param  slot_id: 密钥槽ID
 * @param  data: 要加密的数据
 * @param  encrypted: 输出加密数据
 */
int atecc608_encrypt(uint8_t slot_id, const uint8_t *data, uint8_t *encrypted)
{
    printf("Encrypting with ATECC608 slot %d...\n", slot_id);
    
    // 构建加密命令
    uint8_t cmd[64];
    cmd[0] = 0x03;  // 命令码：加密
    cmd[1] = 0x47;  // 参数
    cmd[2] = slot_id;
    memcpy(&cmd[3], data, 32);
    
    // 发送命令
    if (i2c_write(ATECC608_ADDR, cmd, 35) != 0) {
        return -1;
    }
    
    // 等待加密完成
    HAL_Delay(20);
    
    // 读取加密结果
    if (i2c_read(ATECC608_ADDR, encrypted, 32) != 0) {
        return -1;
    }
    
    printf("Encryption completed\n");
    return 0;
}
```

**安全元件的优势**：

1. **物理隔离**
   - 密钥存储在独立芯片中
   - 主MCU无法直接访问密钥
   - 抗物理攻击能力强

2. **硬件保护**
   - 防篡改检测
   - 侧信道攻击防护
   - 安全启动验证

3. **密钥不出芯片**
   - 密钥在芯片内生成
   - 加密操作在芯片内完成
   - 密钥永不暴露

4. **认证功能**
   - 支持设备认证
   - 支持安全通信
   - 符合行业标准

**常见安全元件**：

| 型号 | 厂商 | 接口 | 特点 |
|------|------|------|------|
| ATECC608 | Microchip | I2C | 低成本，易集成 |
| SE050 | NXP | I2C/SPI | 功能丰富 |
| OPTIGA Trust | Infineon | I2C | 高安全等级 |
| A71CH | NXP | I2C | IoT专用 |

### 密钥分发

密钥分发是将密钥安全地传递给需要使用它的设备或用户。

#### 分发方案

**方案1：预置密钥（Pre-shared Key）**

在生产阶段注入密钥：

```c
/**
 * @brief  生产阶段密钥注入流程
 */
void production_key_injection(void)
{
    printf("=== Production Key Injection ===\n");
    
    // 步骤1：生成设备唯一密钥
    uint8_t device_key[32];
    generate_key_with_trng(device_key, 32);
    
    printf("Step 1: Generated unique device key\n");
    
    // 步骤2：读取设备唯一ID
    uint32_t device_id[3];
    device_id[0] = *(uint32_t*)(UID_BASE);
    device_id[1] = *(uint32_t*)(UID_BASE + 4);
    device_id[2] = *(uint32_t*)(UID_BASE + 8);
    
    printf("Step 2: Device ID: %08lX-%08lX-%08lX\n",
           device_id[0], device_id[1], device_id[2]);
    
    // 步骤3：将密钥写入OTP或安全元件
    write_key_to_otp(device_key, 32);
    
    printf("Step 3: Key written to secure storage\n");
    
    // 步骤4：将设备ID和密钥记录到数据库
    // 在实际生产中，这一步在生产服务器上完成
    printf("Step 4: Record device ID and key in database\n");
    
    // 步骤5：锁定配置，防止修改
    lock_security_configuration();
    
    printf("Step 5: Security configuration locked\n");
    printf("Device provisioning completed\n");
}
```

**方案2：密钥交换协议**

使用Diffie-Hellman密钥交换：

```c
/**
 * @brief  ECDH密钥交换示例
 * @note   使用椭圆曲线Diffie-Hellman
 */
#include "mbedtls/ecdh.h"

int ecdh_key_exchange_demo(void)
{
    mbedtls_ecdh_context ctx_cli, ctx_srv;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    unsigned char cli_to_srv[65], srv_to_cli[65];
    unsigned char shared_secret_cli[32], shared_secret_srv[32];
    size_t olen;
    int ret;
    
    printf("=== ECDH Key Exchange Demo ===\n");
    
    // 初始化
    mbedtls_ecdh_init(&ctx_cli);
    mbedtls_ecdh_init(&ctx_srv);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    // 种子化随机数生成器
    const char *pers = "ecdh_demo";
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                         (const unsigned char *)pers, strlen(pers));
    
    // 客户端：生成密钥对
    printf("\nClient: Generating key pair...\n");
    ret = mbedtls_ecdh_setup(&ctx_cli, MBEDTLS_ECP_DP_SECP256R1);
    ret = mbedtls_ecdh_make_public(&ctx_cli, &olen, cli_to_srv, 65,
                                   mbedtls_ctr_drbg_random, &ctr_drbg);
    printf("Client: Public key generated (%zu bytes)\n", olen);
    
    // 服务器：生成密钥对
    printf("\nServer: Generating key pair...\n");
    ret = mbedtls_ecdh_setup(&ctx_srv, MBEDTLS_ECP_DP_SECP256R1);
    ret = mbedtls_ecdh_make_public(&ctx_srv, &olen, srv_to_cli, 65,
                                   mbedtls_ctr_drbg_random, &ctr_drbg);
    printf("Server: Public key generated (%zu bytes)\n", olen);
    
    // 客户端：计算共享密钥
    printf("\nClient: Computing shared secret...\n");
    ret = mbedtls_ecdh_read_public(&ctx_cli, srv_to_cli, olen);
    ret = mbedtls_ecdh_calc_secret(&ctx_cli, &olen, shared_secret_cli, 32,
                                   mbedtls_ctr_drbg_random, &ctr_drbg);
    printf("Client: Shared secret computed (%zu bytes)\n", olen);
    
    // 服务器：计算共享密钥
    printf("\nServer: Computing shared secret...\n");
    ret = mbedtls_ecdh_read_public(&ctx_srv, cli_to_srv, 65);
    ret = mbedtls_ecdh_calc_secret(&ctx_srv, &olen, shared_secret_srv, 32,
                                   mbedtls_ctr_drbg_random, &ctr_drbg);
    printf("Server: Shared secret computed (%zu bytes)\n", olen);
    
    // 验证共享密钥是否相同
    printf("\nVerifying shared secrets...\n");
    if (memcmp(shared_secret_cli, shared_secret_srv, 32) == 0) {
        printf("✓ Shared secrets match!\n");
        printf("Shared secret: ");
        for (int i = 0; i < 32; i++) {
            printf("%02X", shared_secret_cli[i]);
        }
        printf("\n");
    } else {
        printf("✗ Shared secrets do not match!\n");
    }
    
    // 清理
    mbedtls_ecdh_free(&ctx_cli);
    mbedtls_ecdh_free(&ctx_srv);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    
    return 0;
}
```

**ECDH密钥交换的优势**：
- 不需要预共享密钥
- 公钥可以在不安全信道传输
- 抗中间人攻击（配合认证）
- 前向保密性

### 密钥更新和轮换

定期更新密钥可以降低密钥泄露的风险。

#### 密钥轮换策略


```c
/**
 * @brief  密钥轮换管理系统
 */

// 密钥版本管理
typedef struct {
    uint32_t version;           // 密钥版本号
    uint32_t created_at;        // 创建时间
    uint32_t expires_at;        // 过期时间
    uint8_t key[32];            // 密钥数据
    uint8_t status;             // 状态：0=活跃, 1=已过期, 2=已撤销
} key_version_t;

// 密钥管理器
typedef struct {
    key_version_t current_key;  // 当前密钥
    key_version_t previous_key; // 前一个密钥（用于解密旧数据）
    uint32_t rotation_interval; // 轮换间隔（秒）
} key_manager_t;

static key_manager_t key_mgr;

/**
 * @brief  初始化密钥管理器
 */
int key_manager_init(uint32_t rotation_interval)
{
    printf("Initializing key manager...\n");
    
    memset(&key_mgr, 0, sizeof(key_mgr));
    key_mgr.rotation_interval = rotation_interval;
    
    // 生成初始密钥
    generate_key_with_trng(key_mgr.current_key.key, 32);
    key_mgr.current_key.version = 1;
    key_mgr.current_key.created_at = HAL_GetTick();
    key_mgr.current_key.expires_at = key_mgr.current_key.created_at + rotation_interval;
    key_mgr.current_key.status = 0;  // 活跃
    
    printf("Key manager initialized\n");
    printf("Initial key version: %lu\n", key_mgr.current_key.version);
    printf("Rotation interval: %lu seconds\n", rotation_interval / 1000);
    
    return 0;
}

/**
 * @brief  检查是否需要轮换密钥
 */
bool key_manager_needs_rotation(void)
{
    uint32_t current_time = HAL_GetTick();
    return (current_time >= key_mgr.current_key.expires_at);
}

/**
 * @brief  执行密钥轮换
 */
int key_manager_rotate(void)
{
    printf("\n=== Key Rotation ===\n");
    printf("Current key version: %lu\n", key_mgr.current_key.version);
    
    // 保存当前密钥为前一个密钥
    memcpy(&key_mgr.previous_key, &key_mgr.current_key, sizeof(key_version_t));
    key_mgr.previous_key.status = 1;  // 标记为已过期
    
    printf("Previous key saved (version %lu)\n", key_mgr.previous_key.version);
    
    // 生成新密钥
    generate_key_with_trng(key_mgr.current_key.key, 32);
    key_mgr.current_key.version++;
    key_mgr.current_key.created_at = HAL_GetTick();
    key_mgr.current_key.expires_at = key_mgr.current_key.created_at + key_mgr.rotation_interval;
    key_mgr.current_key.status = 0;  // 活跃
    
    printf("New key generated (version %lu)\n", key_mgr.current_key.version);
    printf("Expires at: %lu\n", key_mgr.current_key.expires_at);
    
    // 持久化密钥
    store_encrypted_key(key_mgr.current_key.key, 32,
                       master_key, KEY_STORAGE_ADDR);
    
    printf("Key rotation completed\n");
    
    return 0;
}

/**
 * @brief  获取用于加密的密钥
 */
const uint8_t* key_manager_get_encryption_key(void)
{
    // 检查是否需要轮换
    if (key_manager_needs_rotation()) {
        printf("Key expired, rotating...\n");
        key_manager_rotate();
    }
    
    return key_mgr.current_key.key;
}

/**
 * @brief  获取用于解密的密钥
 * @param  version: 密钥版本号
 */
const uint8_t* key_manager_get_decryption_key(uint32_t version)
{
    if (version == key_mgr.current_key.version) {
        return key_mgr.current_key.key;
    } else if (version == key_mgr.previous_key.version) {
        // 允许使用前一个密钥解密旧数据
        printf("Using previous key (version %lu) for decryption\n", version);
        return key_mgr.previous_key.key;
    } else {
        printf("Key version %lu not available\n", version);
        return NULL;
    }
}

/**
 * @brief  密钥轮换示例
 */
void key_rotation_example(void)
{
    // 初始化密钥管理器（30秒轮换间隔）
    key_manager_init(30000);
    
    // 模拟加密操作
    const char *data = "Sensitive data";
    uint8_t encrypted[32];
    
    printf("\n--- Encrypting with current key ---\n");
    const uint8_t *enc_key = key_manager_get_encryption_key();
    uint32_t key_version = key_mgr.current_key.version;
    
    // 加密数据（简化示例）
    printf("Encrypted with key version %lu\n", key_version);
    
    // 等待密钥过期
    printf("\nWaiting for key expiration...\n");
    HAL_Delay(31000);
    
    // 尝试加密，会触发密钥轮换
    printf("\n--- Encrypting with new key ---\n");
    enc_key = key_manager_get_encryption_key();
    
    // 解密旧数据
    printf("\n--- Decrypting old data ---\n");
    const uint8_t *dec_key = key_manager_get_decryption_key(key_version);
    if (dec_key != NULL) {
        printf("Successfully retrieved old key for decryption\n");
    }
}
```

**密钥轮换最佳实践**：

1. **定期轮换**
   - 根据风险评估确定轮换周期
   - 高安全应用：每天或每周
   - 一般应用：每月或每季度
   - 低风险应用：每年

2. **保留旧密钥**
   - 保留前N个版本的密钥
   - 用于解密旧数据
   - 设置旧密钥的过期时间

3. **平滑过渡**
   - 新旧密钥并存一段时间
   - 逐步迁移到新密钥
   - 避免服务中断

4. **审计和监控**
   - 记录密钥轮换事件
   - 监控密钥使用情况
   - 检测异常访问

### 密钥销毁

密钥不再需要时，必须安全地销毁。

```c
/**
 * @brief  安全擦除密钥
 * @param  key: 密钥缓冲区
 * @param  key_len: 密钥长度
 */
void secure_key_erase(uint8_t *key, size_t key_len)
{
    volatile uint8_t *p = key;
    
    printf("Securely erasing key...\n");
    
    // 多次覆写，防止数据恢复
    for (int pass = 0; pass < 3; pass++) {
        // 写入0x00
        for (size_t i = 0; i < key_len; i++) {
            p[i] = 0x00;
        }
        
        // 写入0xFF
        for (size_t i = 0; i < key_len; i++) {
            p[i] = 0xFF;
        }
        
        // 写入随机数
        for (size_t i = 0; i < key_len; i++) {
            p[i] = (uint8_t)(rand() & 0xFF);
        }
    }
    
    // 最后清零
    for (size_t i = 0; i < key_len; i++) {
        p[i] = 0x00;
    }
    
    printf("Key erased securely\n");
}

/**
 * @brief  擦除Flash中的密钥
 * @param  address: Flash地址
 * @param  size: 擦除大小
 */
int secure_flash_erase(uint32_t address, size_t size)
{
    printf("Erasing Flash at 0x%08lX...\n", address);
    
    // 解锁Flash
    HAL_FLASH_Unlock();
    
    // 确定要擦除的扇区
    uint32_t sector = get_flash_sector(address);
    
    // 擦除扇区
    FLASH_EraseInitTypeDef erase_init;
    uint32_t sector_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_SECTORS;
    erase_init.Sector = sector;
    erase_init.NbSectors = 1;
    erase_init.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    
    HAL_StatusTypeDef status = HAL_FLASHEx_Erase(&erase_init, &sector_error);
    
    // 锁定Flash
    HAL_FLASH_Lock();
    
    if (status == HAL_OK) {
        printf("Flash erased successfully\n");
        return 0;
    } else {
        printf("Flash erase failed\n");
        return -1;
    }
}
```

## 安全最佳实践

### 密钥管理的黄金法则

1. **永不硬编码密钥**
   ```c
   // ❌ 错误：硬编码密钥
   const uint8_t key[] = {0x2b, 0x7e, 0x15, 0x16, ...};
   
   // ✅ 正确：从安全存储加载
   uint8_t key[32];
   load_key_from_secure_storage(key, 32);
   ```

2. **永不明文存储密钥**
   ```c
   // ❌ 错误：明文存储
   write_to_flash(addr, key, 32);
   
   // ✅ 正确：加密存储
   store_encrypted_key(key, 32, master_key, addr);
   ```

3. **使用后立即清除密钥**
   ```c
   // ✅ 正确的密钥使用流程
   uint8_t key[32];
   load_key(key, 32);
   
   // 使用密钥
   encrypt_data(data, key);
   
   // 立即清除
   secure_key_erase(key, 32);
   ```

4. **限制密钥访问权限**
   ```c
   // 使用访问控制
   if (!check_permission(current_user, KEY_ACCESS)) {
       printf("Access denied\n");
       return -1;
   }
   ```

5. **记录密钥操作**
   ```c
   // 审计日志
   log_key_operation("KEY_LOAD", key_id, user_id, timestamp);
   ```

### 常见安全陷阱

#### 陷阱1：使用弱随机数生成器

```c
// ❌ 错误：使用标准rand()
srand(time(NULL));
for (int i = 0; i < 16; i++) {
    key[i] = rand() & 0xFF;
}

// ✅ 正确：使用硬件RNG或CSPRNG
generate_key_with_trng(key, 16);
```

#### 陷阱2：密钥重用

```c
// ❌ 错误：所有设备使用相同密钥
const uint8_t global_key[32] = {...};

// ✅ 正确：每个设备唯一密钥
uint8_t device_key[32];
derive_device_key(device_id, device_key);
```

#### 陷阱3：不安全的密钥传输

```c
// ❌ 错误：明文传输密钥
send_over_network(key, 32);

// ✅ 正确：使用密钥交换协议
ecdh_key_exchange(&shared_key);
```

#### 陷阱4：忘记清除密钥

```c
// ❌ 错误：函数结束时密钥仍在内存中
void encrypt_function(void) {
    uint8_t key[32];
    load_key(key, 32);
    encrypt_data(data, key);
    // 函数结束，key仍在栈上
}

// ✅ 正确：显式清除
void encrypt_function(void) {
    uint8_t key[32];
    load_key(key, 32);
    encrypt_data(data, key);
    secure_key_erase(key, 32);  // 清除密钥
}
```

## 实际应用场景

### 场景1：IoT设备认证

```c
/**
 * @brief  IoT设备认证系统
 */
typedef struct {
    uint8_t device_id[16];      // 设备ID
    uint8_t device_key[32];     // 设备密钥
    uint8_t server_cert[512];   // 服务器证书
} iot_device_credentials_t;

int iot_device_authenticate(void)
{
    iot_device_credentials_t creds;
    
    printf("=== IoT Device Authentication ===\n");
    
    // 步骤1：从安全存储加载凭证
    printf("Step 1: Loading device credentials...\n");
    read_key_from_otp(creds.device_key, 32);
    load_device_id(creds.device_id, 16);
    
    // 步骤2：建立TLS连接
    printf("Step 2: Establishing TLS connection...\n");
    // 使用设备密钥和证书建立安全连接
    
    // 步骤3：发送认证请求
    printf("Step 3: Sending authentication request...\n");
    uint8_t challenge[32];
    receive_challenge(challenge, 32);
    
    // 步骤4：使用设备密钥签名挑战
    printf("Step 4: Signing challenge...\n");
    uint8_t signature[64];
    sign_with_device_key(challenge, 32, creds.device_key, signature);
    
    // 步骤5：发送签名
    printf("Step 5: Sending signature...\n");
    send_signature(signature, 64);
    
    // 步骤6：接收认证结果
    printf("Step 6: Receiving authentication result...\n");
    if (receive_auth_result() == AUTH_SUCCESS) {
        printf("✓ Device authenticated successfully\n");
        return 0;
    } else {
        printf("✗ Authentication failed\n");
        return -1;
    }
}
```

### 场景2：固件加密存储

```c
/**
 * @brief  加密固件存储系统
 */
int store_encrypted_firmware(const uint8_t *firmware, size_t firmware_size)
{
    printf("=== Storing Encrypted Firmware ===\n");
    
    // 步骤1：生成固件加密密钥
    printf("Step 1: Generating firmware encryption key...\n");
    uint8_t fw_key[32];
    generate_key_with_trng(fw_key, 32);
    
    // 步骤2：加密固件
    printf("Step 2: Encrypting firmware (%zu bytes)...\n", firmware_size);
    uint8_t *encrypted_fw = malloc(firmware_size);
    encrypt_firmware(firmware, firmware_size, fw_key, encrypted_fw);
    
    // 步骤3：使用设备主密钥加密固件密钥
    printf("Step 3: Encrypting firmware key...\n");
    uint8_t master_key[32];
    derive_master_key_from_uid(master_key);
    
    uint8_t encrypted_fw_key[48];  // 32字节密钥 + 16字节IV
    encrypt_key(fw_key, 32, master_key, encrypted_fw_key);
    
    // 步骤4：存储加密的固件和密钥
    printf("Step 4: Storing encrypted firmware and key...\n");
    write_to_flash(FIRMWARE_ADDR, encrypted_fw, firmware_size);
    write_to_flash(FW_KEY_ADDR, encrypted_fw_key, 48);
    
    // 步骤5：清除临时密钥
    printf("Step 5: Clearing temporary keys...\n");
    secure_key_erase(fw_key, 32);
    secure_key_erase(master_key, 32);
    
    free(encrypted_fw);
    
    printf("Firmware stored securely\n");
    return 0;
}
```

## 总结

密钥管理是信息安全的基石，本文介绍了密钥管理的核心概念和最佳实践：

**密钥生命周期**：
- 生成：使用TRNG或CSPRNG生成高质量随机密钥
- 存储：采用加密存储、OTP或安全元件保护密钥
- 分发：使用预置密钥或密钥交换协议安全分发
- 更新：定期轮换密钥，保留旧版本用于解密
- 销毁：安全擦除不再需要的密钥

**安全原则**：
- 永不硬编码密钥
- 永不明文存储密钥
- 使用后立即清除密钥
- 限制密钥访问权限
- 记录密钥操作审计

**技术方案**：
- 硬件RNG提供真随机数
- 密钥派生函数从密码生成密钥
- 安全元件提供物理隔离保护
- ECDH实现安全的密钥交换
- 密钥轮换降低泄露风险

**实践建议**：
- 根据安全需求选择合适的存储方案
- 在生产阶段注入设备唯一密钥
- 实施密钥版本管理和轮换策略
- 建立完善的密钥审计机制
- 定期进行安全评估和渗透测试

## 延伸阅读

推荐进一步学习的资源：

- [NIST密钥管理指南](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final) - 权威的密钥管理标准
- 安全启动与固件验证 - 密钥在安全启动中的应用
- TLS/SSL协议详解 - 密钥在安全通信中的应用
- [硬件安全模块(HSM)技术](https://www.cryptomathic.com/news-events/blog/what-is-a-hardware-security-module-hsm) - HSM深入介绍

## 参考资料

1. NIST SP 800-57 - Recommendation for Key Management
2. FIPS 140-2 - Security Requirements for Cryptographic Modules
3. Common Criteria - Security Evaluation Standards
4. Microchip ATECC608 Datasheet
5. mbedTLS Documentation - https://tls.mbed.org/

---

**练习题**：

1. 设计一个密钥管理系统，支持密钥生成、存储、轮换和销毁
2. 实现一个基于ECDH的密钥交换协议
3. 使用安全元件（如ATECC608）实现设备认证
4. 设计一个固件加密存储方案，确保固件的机密性和完整性
5. 实现一个密钥审计系统，记录所有密钥操作

**下一步**：建议学习 安全启动与固件验证，了解密钥在系统启动安全中的应用。
