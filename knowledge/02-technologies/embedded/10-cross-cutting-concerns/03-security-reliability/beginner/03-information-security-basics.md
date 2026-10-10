---
title: "信息安全基础知识"
description: "深入讲解信息安全的核心概念，包括机密性、完整性、可用性三要素，认证授权机制，加密技术基础，以及常用安全协议，为嵌入式系统安全开发打下坚实基础"
slug: "information-security-basics"

# 分类信息
domain: "横切关注点"
module: "安全性与可靠性"
content_type: "article"
skill_level: "beginner"

# 标签和关联
tags:
  - 信息安全
  - 加密
  - 安全协议
  - 认证授权
  - CIA三要素
prerequisites:
  - "embedded-security-overview"
related_contents:
  - "secure-boot-firmware-verification"
  - "key-management-storage"

# 学习信息
estimated_time: 50
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
  - 信息安全
  - 机密性
  - 完整性
  - 可用性
  - 加密技术
  - 认证授权
  - 安全协议
  - 数字签名
cover_image: ""
---

# 信息安全基础知识


## 概述

信息安全是保护信息系统和数据免受未授权访问、使用、披露、破坏、修改或销毁的实践。在嵌入式系统中，信息安全不仅关系到数据保护，还涉及系统的可靠运行和用户隐私。完成本文学习后，你将能够：

- 深入理解信息安全的CIA三要素
- 掌握认证和授权的基本概念和实现方法
- 了解对称加密和非对称加密的原理和应用
- 理解哈希函数和数字签名的作用
- 熟悉常用的安全协议及其应用场景
- 能够为嵌入式系统设计基本的安全方案

## 背景知识

### 为什么信息安全如此重要？

在现代嵌入式系统中，信息安全的重要性体现在：

**1. 数据价值提升**
- 个人隐私数据（健康、位置、行为）
- 商业机密（算法、配置、密钥）
- 控制指令（工业控制、车辆控制）

**2. 互联互通增加**
- 物联网设备广泛联网
- 远程访问和控制
- 数据云端存储和处理

**3. 攻击手段进化**
- 自动化攻击工具
- 大规模漏洞利用
- 供应链攻击

**4. 法规要求严格**
- GDPR（欧盟数据保护条例）
- CCPA（加州消费者隐私法案）
- 网络安全法（中国）
- 行业特定标准

### 前置知识要求

本文假设你已经掌握：
- 嵌入式系统基础知识
- C语言编程基础
- 基本的数学概念（模运算、异或等）
- 计算机网络基础


## 核心内容

### 1. CIA三要素

CIA三要素是信息安全的基石，代表了信息安全的三个核心目标。

#### 1.1 机密性（Confidentiality）

机密性确保信息只能被授权的实体访问。

**威胁示例**：
- 窃听网络通信
- 未授权读取存储数据
- 内存转储获取敏感信息
- 侧信道攻击推断密钥

**保护措施**：

1. **加密技术**
   - 数据传输加密（TLS/DTLS）
   - 数据存储加密（AES）
   - 端到端加密

2. **访问控制**
   - 身份认证
   - 权限管理
   - 最小权限原则

3. **物理保护**
   - 防篡改封装
   - 安全芯片
   - 调试接口保护

**实现示例**：

```c
// 使用AES加密保护机密数据
#include <stdint.h>

typedef struct {
    uint8_t encrypted_data[256];
    uint8_t iv[16];  // 初始化向量
} confidential_data_t;

// 加密敏感数据
int protect_confidentiality(const uint8_t *plaintext,
                            uint32_t len,
                            const uint8_t *key,
                            confidential_data_t *output) {
    // 生成随机IV
    generate_random_iv(output->iv, 16);
    
    // 使用AES-256-CBC加密
    return aes_256_cbc_encrypt(plaintext, len, key,
                              output->iv,
                              output->encrypted_data);
}
```


#### 1.2 完整性（Integrity）

完整性确保信息在存储和传输过程中未被篡改。

**威胁示例**：
- 中间人攻击修改数据
- 恶意软件篡改配置
- 存储介质损坏
- 固件被替换

**保护措施**：

1. **哈希函数**
   - 计算数据摘要
   - 检测数据变化
   - 常用算法：SHA-256、SHA-3

2. **消息认证码（MAC）**
   - HMAC（基于哈希的MAC）
   - CMAC（基于分组密码的MAC）
   - 验证数据来源和完整性

3. **数字签名**
   - 使用私钥签名
   - 使用公钥验证
   - 不可否认性

**实现示例**：

```c
// 使用HMAC保护数据完整性
#include <stdint.h>

typedef struct {
    uint8_t data[256];
    uint32_t data_len;
    uint8_t hmac[32];  // SHA-256 HMAC
} integrity_protected_data_t;

// 生成HMAC保护完整性
int protect_integrity(const uint8_t *data,
                     uint32_t len,
                     const uint8_t *key,
                     integrity_protected_data_t *output) {
    // 复制数据
    memcpy(output->data, data, len);
    output->data_len = len;
    
    // 计算HMAC-SHA256
    return hmac_sha256(data, len, key, 32, output->hmac);
}

// 验证数据完整性
int verify_integrity(const integrity_protected_data_t *input,
                    const uint8_t *key) {
    uint8_t calculated_hmac[32];
    
    // 重新计算HMAC
    hmac_sha256(input->data, input->data_len,
               key, 32, calculated_hmac);
    
    // 比较HMAC（使用常量时间比较防止时序攻击）
    return constant_time_compare(input->hmac,
                                calculated_hmac, 32);
}
```


#### 1.3 可用性（Availability）

可用性确保授权用户能够及时访问信息和资源。

**威胁示例**：
- 拒绝服务攻击（DoS）
- 资源耗尽
- 系统崩溃
- 硬件故障

**保护措施**：

1. **冗余设计**
   - 硬件冗余
   - 数据备份
   - 故障切换

2. **资源管理**
   - 限流和配额
   - 优先级调度
   - 看门狗机制

3. **监控和恢复**
   - 健康检查
   - 自动重启
   - 故障隔离

**实现示例**：

```c
// 看门狗保护系统可用性
#include <stdint.h>

#define WATCHDOG_TIMEOUT_MS 5000

typedef struct {
    uint32_t last_feed_time;
    uint32_t timeout_ms;
    uint8_t enabled;
} watchdog_t;

static watchdog_t system_watchdog = {
    .timeout_ms = WATCHDOG_TIMEOUT_MS,
    .enabled = 1
};

// 喂狗
void watchdog_feed(void) {
    if (system_watchdog.enabled) {
        system_watchdog.last_feed_time = get_system_time_ms();
        hardware_watchdog_reset();
    }
}

// 检查看门狗状态
void watchdog_check(void) {
    if (!system_watchdog.enabled) {
        return;
    }
    
    uint32_t current_time = get_system_time_ms();
    uint32_t elapsed = current_time - system_watchdog.last_feed_time;
    
    if (elapsed > system_watchdog.timeout_ms) {
        // 超时，系统将重启
        log_error("Watchdog timeout, system will reset");
        // 硬件看门狗会触发重启
    }
}
```

**CIA三要素的关系**：

```
        机密性
         /  \
        /    \
       /      \
  完整性 ---- 可用性
```

- 三者相互关联，需要平衡
- 过度强调一个可能影响其他
- 根据应用场景确定优先级


### 2. 认证与授权

认证和授权是访问控制的两个关键环节。

#### 2.1 认证（Authentication）

认证是验证实体身份的过程，回答"你是谁？"的问题。

**认证因素**：

1. **知识因素（Something You Know）**
   - 密码
   - PIN码
   - 安全问题答案

2. **所有因素（Something You Have）**
   - 智能卡
   - 硬件令牌
   - 手机（接收验证码）

3. **生物因素（Something You Are）**
   - 指纹
   - 面部识别
   - 虹膜扫描

**多因素认证（MFA）**：
- 结合两个或更多因素
- 显著提高安全性
- 即使一个因素泄露，仍然安全

**密码认证实现**：

```c
#include <stdint.h>
#include <string.h>

// 密码哈希存储结构
typedef struct {
    uint8_t salt[16];        // 盐值
    uint8_t hash[32];        // 密码哈希（SHA-256）
    uint32_t iterations;     // PBKDF2迭代次数
} password_hash_t;

// 生成密码哈希（使用PBKDF2）
int hash_password(const char *password,
                 password_hash_t *output) {
    // 生成随机盐值
    generate_random(output->salt, sizeof(output->salt));
    
    // 设置迭代次数（增加暴力破解难度）
    output->iterations = 100000;
    
    // 使用PBKDF2派生密钥
    return pbkdf2_sha256(password, strlen(password),
                        output->salt, sizeof(output->salt),
                        output->iterations,
                        output->hash, sizeof(output->hash));
}

// 验证密码
int verify_password(const char *password,
                   const password_hash_t *stored) {
    uint8_t calculated_hash[32];
    
    // 使用相同的盐值和迭代次数计算哈希
    pbkdf2_sha256(password, strlen(password),
                 stored->salt, sizeof(stored->salt),
                 stored->iterations,
                 calculated_hash, sizeof(calculated_hash));
    
    // 常量时间比较（防止时序攻击）
    return constant_time_compare(calculated_hash,
                                stored->hash,
                                sizeof(stored->hash));
}
```

**证书认证实现**：

```c
// X.509证书认证
typedef struct {
    uint8_t *cert_data;
    uint32_t cert_len;
    uint8_t *public_key;
    uint32_t key_len;
} certificate_t;

// 验证证书
int verify_certificate(const certificate_t *cert,
                      const certificate_t *ca_cert) {
    // 1. 验证证书签名
    if (!verify_cert_signature(cert, ca_cert->public_key)) {
        return -1;  // 签名无效
    }
    
    // 2. 检查证书有效期
    if (!check_cert_validity(cert)) {
        return -2;  // 证书过期
    }
    
    // 3. 检查证书撤销状态（CRL或OCSP）
    if (is_cert_revoked(cert)) {
        return -3;  // 证书已撤销
    }
    
    return 0;  // 验证成功
}
```


#### 2.2 授权（Authorization）

授权是确定已认证实体可以访问哪些资源，回答"你能做什么？"的问题。

**授权模型**：

1. **自主访问控制（DAC）**
   - 资源所有者控制访问权限
   - 灵活但难以管理
   - 适用于小型系统

2. **强制访问控制（MAC）**
   - 系统强制执行安全策略
   - 基于安全标签
   - 适用于高安全需求

3. **基于角色的访问控制（RBAC）**
   - 用户分配到角色
   - 角色拥有权限
   - 易于管理，广泛应用

4. **基于属性的访问控制（ABAC）**
   - 基于属性和策略
   - 灵活且细粒度
   - 适用于复杂场景

**RBAC实现示例**：

```c
#include <stdint.h>
#include <stdbool.h>

// 权限定义
typedef enum {
    PERM_READ    = 0x01,
    PERM_WRITE   = 0x02,
    PERM_EXECUTE = 0x04,
    PERM_DELETE  = 0x08,
    PERM_ADMIN   = 0x10
} permission_t;

// 角色定义
typedef enum {
    ROLE_GUEST,
    ROLE_USER,
    ROLE_OPERATOR,
    ROLE_ADMIN
} role_t;

// 用户结构
typedef struct {
    uint32_t user_id;
    role_t role;
    uint8_t permissions;
} user_t;

// 角色权限映射
static const uint8_t role_permissions[] = {
    [ROLE_GUEST]    = PERM_READ,
    [ROLE_USER]     = PERM_READ | PERM_WRITE,
    [ROLE_OPERATOR] = PERM_READ | PERM_WRITE | PERM_EXECUTE,
    [ROLE_ADMIN]    = PERM_READ | PERM_WRITE | PERM_EXECUTE | 
                      PERM_DELETE | PERM_ADMIN
};

// 检查用户权限
bool check_permission(const user_t *user, permission_t required) {
    uint8_t user_perms = role_permissions[user->role];
    return (user_perms & required) == required;
}

// 访问控制示例
int access_resource(const user_t *user,
                   const char *resource,
                   permission_t required) {
    // 1. 检查用户是否已认证
    if (user == NULL) {
        log_security_event("Unauthenticated access attempt");
        return -1;
    }
    
    // 2. 检查权限
    if (!check_permission(user, required)) {
        log_security_event("Unauthorized access: user %d, resource %s",
                          user->user_id, resource);
        return -2;
    }
    
    // 3. 记录访问日志
    log_access("User %d accessed %s with permission 0x%02x",
              user->user_id, resource, required);
    
    return 0;  // 授权成功
}
```


### 3. 加密技术基础

加密是信息安全的核心技术，用于保护数据的机密性。

#### 3.1 对称加密

对称加密使用相同的密钥进行加密和解密。

**特点**：
- 加密速度快
- 密钥管理复杂
- 适合大量数据加密

**常用算法**：

| 算法 | 密钥长度 | 分组大小 | 特点 |
|------|---------|---------|------|
| **AES** | 128/192/256位 | 128位 | 标准算法，硬件支持好 |
| **ChaCha20** | 256位 | 流密码 | 软件实现快 |
| **3DES** | 168位 | 64位 | 已过时，不推荐 |

**AES加密模式**：

1. **ECB（电子密码本）**
   - 最简单，不推荐
   - 相同明文产生相同密文
   - 不隐藏数据模式

2. **CBC（密码分组链接）**
   - 需要IV（初始化向量）
   - 前一个密文块影响后一个
   - 常用模式

3. **CTR（计数器）**
   - 将分组密码转为流密码
   - 可并行加密
   - 需要唯一的nonce

4. **GCM（伽罗瓦计数器）**
   - 认证加密（AEAD）
   - 同时提供机密性和完整性
   - 推荐使用

**AES-GCM实现示例**：

```c
#include <stdint.h>

// AES-GCM加密结构
typedef struct {
    uint8_t nonce[12];           // 96位随机数
    uint8_t ciphertext[256];     // 密文
    uint32_t ciphertext_len;
    uint8_t tag[16];             // 认证标签
} aes_gcm_encrypted_t;

// AES-GCM加密
int aes_gcm_encrypt(const uint8_t *plaintext,
                   uint32_t plaintext_len,
                   const uint8_t *key,        // 256位密钥
                   const uint8_t *aad,        // 附加认证数据
                   uint32_t aad_len,
                   aes_gcm_encrypted_t *output) {
    // 1. 生成随机nonce
    generate_random(output->nonce, sizeof(output->nonce));
    
    // 2. 加密数据
    int ret = aes_256_gcm_encrypt(
        plaintext, plaintext_len,
        aad, aad_len,
        key,
        output->nonce, sizeof(output->nonce),
        output->ciphertext,
        output->tag
    );
    
    if (ret == 0) {
        output->ciphertext_len = plaintext_len;
    }
    
    return ret;
}

// AES-GCM解密
int aes_gcm_decrypt(const aes_gcm_encrypted_t *input,
                   const uint8_t *key,
                   const uint8_t *aad,
                   uint32_t aad_len,
                   uint8_t *plaintext) {
    // 解密并验证认证标签
    return aes_256_gcm_decrypt(
        input->ciphertext, input->ciphertext_len,
        aad, aad_len,
        input->tag,
        key,
        input->nonce, sizeof(input->nonce),
        plaintext
    );
}
```


#### 3.2 非对称加密

非对称加密使用公钥加密、私钥解密（或反之）。

**特点**：
- 密钥分发简单
- 加密速度慢
- 适合密钥交换和数字签名

**常用算法**：

| 算法 | 密钥长度 | 特点 | 应用 |
|------|---------|------|------|
| **RSA** | 2048/3072/4096位 | 成熟稳定 | 签名、密钥交换 |
| **ECC** | 256/384/521位 | 密钥短、速度快 | 嵌入式推荐 |
| **Ed25519** | 256位 | 签名专用 | 高性能签名 |

**RSA加密示例**：

```c
#include <stdint.h>

// RSA密钥对
typedef struct {
    uint8_t *n;          // 模数
    uint32_t n_len;
    uint8_t *e;          // 公钥指数
    uint32_t e_len;
    uint8_t *d;          // 私钥指数（仅私钥）
    uint32_t d_len;
} rsa_key_t;

// RSA公钥加密（用于加密对称密钥）
int rsa_encrypt(const uint8_t *plaintext,
               uint32_t plaintext_len,
               const rsa_key_t *public_key,
               uint8_t *ciphertext) {
    // 使用OAEP填充
    return rsa_oaep_encrypt(plaintext, plaintext_len,
                           public_key->n, public_key->n_len,
                           public_key->e, public_key->e_len,
                           ciphertext);
}

// RSA私钥解密
int rsa_decrypt(const uint8_t *ciphertext,
               uint32_t ciphertext_len,
               const rsa_key_t *private_key,
               uint8_t *plaintext,
               uint32_t *plaintext_len) {
    return rsa_oaep_decrypt(ciphertext, ciphertext_len,
                           private_key->n, private_key->n_len,
                           private_key->d, private_key->d_len,
                           plaintext, plaintext_len);
}
```

**混合加密方案**：

实际应用中通常结合对称和非对称加密：

```c
// 混合加密：RSA + AES
typedef struct {
    uint8_t encrypted_key[256];    // RSA加密的AES密钥
    aes_gcm_encrypted_t data;      // AES-GCM加密的数据
} hybrid_encrypted_t;

// 混合加密
int hybrid_encrypt(const uint8_t *plaintext,
                  uint32_t plaintext_len,
                  const rsa_key_t *recipient_public_key,
                  hybrid_encrypted_t *output) {
    uint8_t aes_key[32];  // 256位AES密钥
    
    // 1. 生成随机AES密钥
    generate_random(aes_key, sizeof(aes_key));
    
    // 2. 使用RSA加密AES密钥
    rsa_encrypt(aes_key, sizeof(aes_key),
               recipient_public_key,
               output->encrypted_key);
    
    // 3. 使用AES-GCM加密数据
    aes_gcm_encrypt(plaintext, plaintext_len,
                   aes_key, NULL, 0,
                   &output->data);
    
    // 4. 清除内存中的密钥
    secure_zero(aes_key, sizeof(aes_key));
    
    return 0;
}
```


#### 3.3 哈希函数

哈希函数将任意长度的数据映射为固定长度的摘要。

**特性**：
- 单向性：无法从哈希值还原原始数据
- 确定性：相同输入产生相同输出
- 雪崩效应：输入微小变化导致输出巨大变化
- 抗碰撞：难以找到两个不同输入产生相同哈希

**常用算法**：

| 算法 | 输出长度 | 安全性 | 应用 |
|------|---------|--------|------|
| **MD5** | 128位 | 已破解 | 不推荐 |
| **SHA-1** | 160位 | 已破解 | 不推荐 |
| **SHA-256** | 256位 | 安全 | 推荐使用 |
| **SHA-3** | 可变 | 安全 | 新标准 |
| **BLAKE2** | 可变 | 安全 | 高性能 |

**哈希应用示例**：

```c
#include <stdint.h>

// 计算文件哈希
int calculate_file_hash(const char *filename,
                       uint8_t *hash_output) {
    uint8_t buffer[1024];
    sha256_context_t ctx;
    
    // 1. 初始化哈希上下文
    sha256_init(&ctx);
    
    // 2. 逐块读取文件并更新哈希
    FILE *fp = fopen(filename, "rb");
    if (!fp) return -1;
    
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        sha256_update(&ctx, buffer, bytes_read);
    }
    
    fclose(fp);
    
    // 3. 完成哈希计算
    sha256_final(&ctx, hash_output);
    
    return 0;
}

// 验证数据完整性
bool verify_data_integrity(const uint8_t *data,
                          uint32_t data_len,
                          const uint8_t *expected_hash) {
    uint8_t calculated_hash[32];
    
    // 计算数据哈希
    sha256(data, data_len, calculated_hash);
    
    // 比较哈希值
    return constant_time_compare(calculated_hash,
                                expected_hash, 32) == 0;
}
```

#### 3.4 数字签名

数字签名用于验证数据来源和完整性，提供不可否认性。

**工作原理**：

```
签名过程：
数据 → 哈希 → 私钥加密 → 签名

验证过程：
数据 → 哈希 ┐
签名 → 公钥解密 → 比较
```

**数字签名实现**：

```c
#include <stdint.h>

// 生成数字签名
int sign_data(const uint8_t *data,
             uint32_t data_len,
             const rsa_key_t *private_key,
             uint8_t *signature,
             uint32_t *signature_len) {
    uint8_t hash[32];
    
    // 1. 计算数据哈希
    sha256(data, data_len, hash);
    
    // 2. 使用私钥签名哈希（RSA-PSS）
    return rsa_pss_sign(hash, sizeof(hash),
                       private_key->n, private_key->n_len,
                       private_key->d, private_key->d_len,
                       signature, signature_len);
}

// 验证数字签名
int verify_signature(const uint8_t *data,
                    uint32_t data_len,
                    const uint8_t *signature,
                    uint32_t signature_len,
                    const rsa_key_t *public_key) {
    uint8_t hash[32];
    
    // 1. 计算数据哈希
    sha256(data, data_len, hash);
    
    // 2. 使用公钥验证签名
    return rsa_pss_verify(hash, sizeof(hash),
                         signature, signature_len,
                         public_key->n, public_key->n_len,
                         public_key->e, public_key->e_len);
}
```


### 4. 安全协议

安全协议定义了安全通信的规则和流程。

#### 4.1 TLS/SSL协议

TLS（传输层安全）是最广泛使用的安全通信协议。

**TLS握手过程**：

```
客户端                                服务器
  |                                     |
  |--- ClientHello ------------------>|
  |    (支持的密码套件、随机数)         |
  |                                     |
  |<-- ServerHello -------------------|
  |    (选择的密码套件、随机数、证书)   |
  |                                     |
  |--- ClientKeyExchange ------------>|
  |    (加密的预主密钥)                 |
  |                                     |
  |--- ChangeCipherSpec ------------->|
  |--- Finished --------------------->|
  |                                     |
  |<-- ChangeCipherSpec --------------|
  |<-- Finished ----------------------|
  |                                     |
  |=== 加密通信开始 ===================|
```

**TLS 1.3改进**：
- 更快的握手（1-RTT）
- 移除不安全的密码套件
- 前向保密（Forward Secrecy）
- 0-RTT模式（会话恢复）

**嵌入式TLS实现考虑**：

```c
#include <stdint.h>

// TLS配置
typedef struct {
    uint8_t *ca_cert;           // CA证书
    uint32_t ca_cert_len;
    uint8_t *client_cert;       // 客户端证书（可选）
    uint32_t client_cert_len;
    uint8_t *client_key;        // 客户端私钥（可选）
    uint32_t client_key_len;
    uint16_t min_tls_version;   // 最低TLS版本
    uint8_t verify_peer;        // 是否验证对端证书
} tls_config_t;

// 初始化TLS连接
int tls_connect(const char *hostname,
               uint16_t port,
               const tls_config_t *config,
               tls_context_t *ctx) {
    // 1. 建立TCP连接
    int sock = tcp_connect(hostname, port);
    if (sock < 0) return -1;
    
    // 2. 初始化TLS上下文
    tls_init(ctx);
    
    // 3. 设置CA证书
    tls_set_ca_cert(ctx, config->ca_cert, config->ca_cert_len);
    
    // 4. 设置客户端证书（如果需要）
    if (config->client_cert) {
        tls_set_client_cert(ctx,
                           config->client_cert,
                           config->client_cert_len,
                           config->client_key,
                           config->client_key_len);
    }
    
    // 5. 执行TLS握手
    int ret = tls_handshake(ctx, sock, hostname);
    if (ret != 0) {
        close(sock);
        return -2;
    }
    
    return sock;
}

// TLS发送数据
int tls_send(tls_context_t *ctx,
            const uint8_t *data,
            uint32_t len) {
    return tls_write(ctx, data, len);
}

// TLS接收数据
int tls_receive(tls_context_t *ctx,
               uint8_t *buffer,
               uint32_t buffer_size) {
    return tls_read(ctx, buffer, buffer_size);
}
```


#### 4.2 DTLS协议

DTLS（数据报传输层安全）是TLS的UDP版本。

**特点**：
- 基于UDP，适合实时通信
- 处理数据包丢失和重排序
- 适用于物联网设备

**DTLS vs TLS**：

| 特性 | TLS | DTLS |
|------|-----|------|
| 传输层 | TCP | UDP |
| 可靠性 | 保证顺序 | 允许丢包 |
| 延迟 | 较高 | 较低 |
| 应用 | Web、邮件 | VoIP、IoT |

#### 4.3 IPsec协议

IPsec在网络层提供安全保护。

**组成部分**：
- **AH（认证头）**：提供完整性和认证
- **ESP（封装安全载荷）**：提供机密性、完整性和认证
- **IKE（密钥交换）**：协商安全参数

**工作模式**：
- **传输模式**：只加密数据部分
- **隧道模式**：加密整个IP包

#### 4.4 MQTT安全

MQTT是物联网常用的消息协议。

**安全措施**：

```c
// MQTT over TLS配置
typedef struct {
    char *broker_host;
    uint16_t broker_port;
    char *client_id;
    char *username;
    char *password;
    tls_config_t tls_config;
    uint8_t use_tls;
} mqtt_config_t;

// 安全连接到MQTT代理
int mqtt_secure_connect(const mqtt_config_t *config,
                       mqtt_client_t *client) {
    // 1. 建立TLS连接
    if (config->use_tls) {
        int sock = tls_connect(config->broker_host,
                              config->broker_port,
                              &config->tls_config,
                              &client->tls_ctx);
        if (sock < 0) return -1;
        client->socket = sock;
    } else {
        // 不推荐：明文连接
        client->socket = tcp_connect(config->broker_host,
                                    config->broker_port);
    }
    
    // 2. 发送MQTT CONNECT包
    mqtt_connect_packet_t connect_pkt = {
        .client_id = config->client_id,
        .username = config->username,
        .password = config->password,
        .clean_session = 1,
        .keep_alive = 60
    };
    
    return mqtt_send_connect(client, &connect_pkt);
}
```

**MQTT安全最佳实践**：
- 始终使用TLS加密
- 使用强密码或证书认证
- 实施访问控制（ACL）
- 定期更新凭证
- 监控异常连接


## 实践示例

### 示例1：完整的安全通信流程

以下示例展示了一个完整的安全通信实现：

```c
#include <stdint.h>
#include <string.h>

// 安全会话结构
typedef struct {
    uint32_t session_id;
    uint8_t session_key[32];     // AES-256密钥
    uint8_t hmac_key[32];        // HMAC密钥
    uint32_t tx_counter;         // 发送计数器（防重放）
    uint32_t rx_counter;         // 接收计数器
    uint8_t authenticated;       // 是否已认证
} secure_session_t;

// 安全消息格式
typedef struct {
    uint32_t counter;            // 消息计数器
    uint8_t iv[12];              // GCM nonce
    uint8_t encrypted_data[256]; // 加密数据
    uint32_t data_len;
    uint8_t tag[16];             // GCM认证标签
} secure_message_t;

// 建立安全会话
int establish_secure_session(const uint8_t *peer_public_key,
                             const uint8_t *my_private_key,
                             secure_session_t *session) {
    uint8_t shared_secret[32];
    
    // 1. ECDH密钥交换
    ecdh_compute_shared_secret(my_private_key,
                              peer_public_key,
                              shared_secret);
    
    // 2. 从共享密钥派生会话密钥
    uint8_t salt[16];
    generate_random(salt, sizeof(salt));
    
    hkdf_sha256(shared_secret, sizeof(shared_secret),
               salt, sizeof(salt),
               "session key", 11,
               session->session_key, sizeof(session->session_key));
    
    hkdf_sha256(shared_secret, sizeof(shared_secret),
               salt, sizeof(salt),
               "hmac key", 8,
               session->hmac_key, sizeof(session->hmac_key));
    
    // 3. 初始化计数器
    session->tx_counter = 0;
    session->rx_counter = 0;
    session->authenticated = 1;
    
    // 4. 清除敏感数据
    secure_zero(shared_secret, sizeof(shared_secret));
    
    return 0;
}

// 发送安全消息
int send_secure_message(secure_session_t *session,
                       const uint8_t *data,
                       uint32_t data_len,
                       secure_message_t *output) {
    if (!session->authenticated) {
        return -1;  // 未认证
    }
    
    // 1. 设置消息计数器
    output->counter = session->tx_counter++;
    
    // 2. 生成随机IV
    generate_random(output->iv, sizeof(output->iv));
    
    // 3. 使用AES-GCM加密
    aes_256_gcm_encrypt(
        data, data_len,
        (uint8_t*)&output->counter, sizeof(output->counter),  // AAD
        session->session_key,
        output->iv, sizeof(output->iv),
        output->encrypted_data,
        output->tag
    );
    
    output->data_len = data_len;
    
    return 0;
}

// 接收安全消息
int receive_secure_message(secure_session_t *session,
                          const secure_message_t *input,
                          uint8_t *data,
                          uint32_t *data_len) {
    if (!session->authenticated) {
        return -1;  // 未认证
    }
    
    // 1. 检查消息计数器（防重放）
    if (input->counter <= session->rx_counter) {
        log_security_event("Replay attack detected");
        return -2;
    }
    
    // 2. 使用AES-GCM解密并验证
    int ret = aes_256_gcm_decrypt(
        input->encrypted_data, input->data_len,
        (uint8_t*)&input->counter, sizeof(input->counter),  // AAD
        input->tag,
        session->session_key,
        input->iv, sizeof(input->iv),
        data
    );
    
    if (ret != 0) {
        log_security_event("Message authentication failed");
        return -3;
    }
    
    // 3. 更新接收计数器
    session->rx_counter = input->counter;
    *data_len = input->data_len;
    
    return 0;
}
```

**代码说明**：
- 使用ECDH进行密钥交换
- 使用HKDF派生会话密钥
- 使用AES-GCM提供机密性和完整性
- 使用计数器防止重放攻击
- 及时清除敏感数据


### 示例2：安全的固件更新

```c
#include <stdint.h>

// 固件更新包结构
typedef struct {
    uint32_t version;            // 固件版本
    uint32_t size;               // 固件大小
    uint8_t hash[32];            // SHA-256哈希
    uint8_t signature[256];      // RSA-2048签名
    uint8_t *firmware_data;      // 固件数据
} firmware_update_t;

// 验证并安装固件更新
int secure_firmware_update(const firmware_update_t *update,
                          const rsa_key_t *vendor_public_key) {
    // 1. 检查版本（防回滚）
    uint32_t current_version = get_current_firmware_version();
    if (update->version <= current_version) {
        log_error("Firmware version rollback attempt");
        return -1;
    }
    
    // 2. 验证固件哈希
    uint8_t calculated_hash[32];
    sha256(update->firmware_data, update->size, calculated_hash);
    
    if (memcmp(calculated_hash, update->hash, 32) != 0) {
        log_error("Firmware hash mismatch");
        return -2;
    }
    
    // 3. 验证数字签名
    int sig_valid = rsa_pss_verify(
        update->hash, sizeof(update->hash),
        update->signature, sizeof(update->signature),
        vendor_public_key->n, vendor_public_key->n_len,
        vendor_public_key->e, vendor_public_key->e_len
    );
    
    if (sig_valid != 0) {
        log_error("Firmware signature verification failed");
        return -3;
    }
    
    // 4. 写入固件到备份分区
    if (write_firmware_to_backup(update->firmware_data,
                                 update->size) != 0) {
        log_error("Failed to write firmware");
        return -4;
    }
    
    // 5. 验证写入的固件
    uint8_t verify_hash[32];
    calculate_partition_hash(BACKUP_PARTITION, verify_hash);
    
    if (memcmp(verify_hash, update->hash, 32) != 0) {
        log_error("Firmware verification after write failed");
        erase_partition(BACKUP_PARTITION);
        return -5;
    }
    
    // 6. 标记新固件为待启动
    set_boot_partition(BACKUP_PARTITION);
    
    // 7. 记录更新日志
    log_info("Firmware update successful, version %u", update->version);
    
    // 8. 重启系统
    system_reboot();
    
    return 0;
}
```

**安全要点**：
- 版本检查防止回滚攻击
- 哈希验证确保数据完整性
- 数字签名验证固件来源
- 双分区设计支持回滚
- 写入后再次验证


## 深入理解

### 密钥管理的重要性

密钥管理是信息安全的核心，再强的加密算法，如果密钥管理不当，也会导致系统不安全。

**密钥生命周期**：

```
生成 → 分发 → 存储 → 使用 → 更新 → 撤销 → 销毁
```

**密钥管理最佳实践**：

1. **密钥生成**
   - 使用硬件随机数生成器
   - 足够的密钥长度
   - 在安全环境中生成

2. **密钥存储**
   - 使用安全芯片（SE/TEE）
   - 加密存储
   - 访问控制
   - 防止物理提取

3. **密钥分发**
   - 使用安全通道
   - 密钥交换协议（DH/ECDH）
   - 证书管理

4. **密钥使用**
   - 最小权限原则
   - 密钥分离（加密密钥 vs 签名密钥）
   - 使用后清除内存

5. **密钥更新**
   - 定期轮换
   - 前向保密
   - 平滑过渡

6. **密钥撤销**
   - 证书撤销列表（CRL）
   - 在线证书状态协议（OCSP）
   - 及时通知

7. **密钥销毁**
   - 安全擦除
   - 多次覆写
   - 物理销毁（如需要）

### 性能与安全的权衡

嵌入式系统资源有限，需要在性能和安全之间找到平衡。

**优化策略**：

1. **算法选择**
   - 对称加密：AES（硬件加速）或ChaCha20（软件快）
   - 非对称加密：ECC（比RSA快且密钥短）
   - 哈希：SHA-256（标准）或BLAKE2（快）

2. **硬件加速**
   - 使用MCU内置的加密引擎
   - 降低CPU负载
   - 提高吞吐量

3. **分层安全**
   - 关键数据：高安全级别
   - 一般数据：中等安全级别
   - 公开数据：低安全级别

4. **批处理**
   - 批量加密减少开销
   - 减少握手次数
   - 会话复用

### 常见安全陷阱

**陷阱1：自己实现加密算法**
- **问题**：容易出错，难以发现漏洞
- **解决**：使用成熟的加密库（mbedTLS、wolfSSL）

**陷阱2：硬编码密钥**
- **问题**：密钥泄露，无法更新
- **解决**：使用密钥派生、安全存储

**陷阱3：忽视时序攻击**
- **问题**：通过执行时间推断密钥
- **解决**：使用常量时间比较

**陷阱4：不验证证书**
- **问题**：容易受到中间人攻击
- **解决**：严格验证证书链

**陷阱5：使用弱随机数**
- **问题**：密钥可预测
- **解决**：使用硬件随机数生成器

**陷阱6：明文存储敏感数据**
- **问题**：数据泄露
- **解决**：加密存储，访问控制


## 常见问题

### Q1: 对称加密和非对称加密应该如何选择？

**A**: 根据应用场景选择：

**对称加密适用于**：
- 大量数据加密（文件、数据库）
- 实时通信（加密速度快）
- 双方已共享密钥的场景

**非对称加密适用于**：
- 密钥交换
- 数字签名
- 身份认证
- 无法预先共享密钥的场景

**实际应用**：
- 通常结合使用（混合加密）
- 用非对称加密交换对称密钥
- 用对称加密加密实际数据

### Q2: 如何选择合适的密钥长度？

**A**: 密钥长度选择需要考虑安全性和性能：

**对称加密**：
- **AES-128**：足够安全，性能好
- **AES-256**：更高安全性，略慢
- 推荐：AES-256（长期安全）

**非对称加密**：
- **RSA-2048**：当前标准
- **RSA-3072/4096**：长期安全
- **ECC-256**：等效RSA-3072，推荐嵌入式使用

**哈希**：
- **SHA-256**：标准选择
- **SHA-384/512**：更高安全性

### Q3: 什么是前向保密（Forward Secrecy）？

**A**: 前向保密确保即使长期密钥泄露，过去的通信仍然安全。

**实现方法**：
- 使用临时密钥（Ephemeral Keys）
- 每次会话生成新的密钥对
- 会话结束后销毁密钥

**TLS中的前向保密**：
- 使用DHE或ECDHE密钥交换
- 不使用RSA密钥交换
- TLS 1.3强制前向保密

**重要性**：
- 保护历史通信
- 限制密钥泄露影响
- 符合隐私法规要求

### Q4: 如何防止重放攻击？

**A**: 重放攻击是指攻击者捕获并重新发送合法消息。

**防护方法**：

1. **时间戳**
   - 消息包含时间戳
   - 接收方检查时间窗口
   - 拒绝过期消息

2. **随机数（Nonce）**
   - 每条消息包含唯一随机数
   - 接收方记录已使用的随机数
   - 拒绝重复的随机数

3. **序列号/计数器**
   - 消息包含递增序列号
   - 接收方检查序列号
   - 拒绝旧的或重复的序列号

4. **挑战-响应**
   - 接收方发送随机挑战
   - 发送方用挑战生成响应
   - 每次挑战不同

**实现示例**：
```c
// 使用计数器防重放
typedef struct {
    uint32_t last_counter;
    uint8_t initialized;
} replay_protection_t;

int check_replay(replay_protection_t *state, uint32_t counter) {
    if (!state->initialized) {
        state->last_counter = counter;
        state->initialized = 1;
        return 0;  // 首次消息
    }
    
    if (counter <= state->last_counter) {
        return -1;  // 重放攻击
    }
    
    state->last_counter = counter;
    return 0;  // 合法消息
}
```

### Q5: 嵌入式系统如何安全存储密钥？

**A**: 密钥存储是嵌入式安全的关键挑战。

**存储方案**：

1. **安全芯片（Secure Element）**
   - 专用安全芯片
   - 防篡改保护
   - 密钥不可导出
   - 最安全但成本高

2. **可信执行环境（TEE）**
   - CPU内的安全区域
   - 隔离执行
   - 硬件保护
   - 平衡安全性和成本

3. **加密存储**
   - 使用设备唯一密钥加密
   - 存储在Flash
   - 需要保护根密钥

4. **OTP（一次性可编程）**
   - 芯片内部OTP区域
   - 只能写入一次
   - 读保护
   - 适合根密钥

**最佳实践**：
- 分层密钥管理
- 根密钥存储在安全芯片
- 工作密钥从根密钥派生
- 定期轮换工作密钥


## 总结

### 核心要点

1. **CIA三要素**
   - **机密性**：保护信息不被未授权访问
   - **完整性**：确保信息未被篡改
   - **可用性**：确保授权用户能访问资源
   - 三者需要平衡，根据场景确定优先级

2. **认证与授权**
   - **认证**：验证身份（你是谁）
   - **授权**：确定权限（你能做什么）
   - 多因素认证提高安全性
   - RBAC是常用的授权模型

3. **加密技术**
   - **对称加密**：快速，适合大量数据（AES）
   - **非对称加密**：密钥分发简单，适合签名（RSA/ECC）
   - **哈希函数**：验证完整性（SHA-256）
   - **数字签名**：验证来源和完整性
   - 实际应用通常结合使用

4. **安全协议**
   - **TLS/DTLS**：安全通信标准
   - **IPsec**：网络层安全
   - **MQTT over TLS**：物联网消息安全
   - 选择合适的协议和配置

5. **密钥管理**
   - 密钥生命周期管理
   - 安全存储（SE/TEE）
   - 定期轮换
   - 前向保密

### 实践建议

**设计阶段**：
- 进行威胁建模
- 确定安全需求
- 选择合适的算法和协议
- 设计密钥管理方案

**实现阶段**：
- 使用成熟的加密库
- 遵循安全编码规范
- 实施输入验证
- 及时清除敏感数据

**测试阶段**：
- 安全功能测试
- 渗透测试
- 密钥管理测试
- 性能测试

**部署阶段**：
- 安全配置
- 密钥注入
- 禁用调试功能
- 建立更新机制

**维护阶段**：
- 监控安全事件
- 及时修补漏洞
- 定期安全审计
- 密钥轮换

### 下一步学习

掌握信息安全基础后，建议继续学习：
- 安全启动与固件验证 - 实现安全启动流程
- 密钥管理与存储 - 深入密钥管理实践
- 安全通信协议实现 - TLS/DTLS详细实现
- 渗透测试与漏洞分析 - 安全测试方法
- 安全芯片应用 - SE/TEE使用指南

## 延伸阅读

### 推荐书籍

- 《应用密码学》（Applied Cryptography）- Bruce Schneier
- 《密码工程》（Cryptography Engineering）- 实践导向
- 《网络安全基础》- 全面的安全知识
- 《物联网安全》- IoT特定的安全实践

### 在线资源

- [NIST Cryptographic Standards](https://csrc.nist.gov/) - 密码学标准
- [OWASP](https://owasp.org/) - Web和IoT安全指南
- [Crypto101](https://www.crypto101.io/) - 密码学入门
- [mbedTLS Documentation](https://tls.mbed.org/) - 嵌入式TLS库

### 加密库推荐

**嵌入式友好的加密库**：
- **mbedTLS**：轻量级，模块化，广泛使用
- **wolfSSL**：高性能，支持多平台
- **BearSSL**：极小内存占用
- **TinyCrypt**：超轻量级，适合MCU

### 相关文章

- 嵌入式系统安全概述 - 安全威胁和防护措施
- 功能安全基础（IEC 61508）- 功能安全标准
- 安全启动与固件验证 - 实现安全启动
- 密钥管理与存储 - 密钥安全管理实践

## 参考资料

1. NIST SP 800-175B - Guideline for Using Cryptographic Standards
2. RFC 8446 - The Transport Layer Security (TLS) Protocol Version 1.3
3. RFC 6347 - Datagram Transport Layer Security Version 1.2
4. FIPS 140-2 - Security Requirements for Cryptographic Modules
5. ISO/IEC 19790 - Security requirements for cryptographic modules

---

**思考题**：

1. 分析你的嵌入式系统，确定哪些数据需要保护机密性、完整性和可用性
2. 设计一个认证和授权方案，包括用户角色和权限
3. 选择合适的加密算法和密钥长度，说明理由
4. 设计一个安全的通信协议，包括密钥交换和数据加密
5. 制定一个密钥管理方案，包括生成、存储、分发和更新

**实践项目**：

实现一个安全的物联网设备通信系统，要求：
- 设备认证（证书或密钥）
- 安全通信（TLS/DTLS）
- 数据加密存储
- 安全固件更新
- 密钥管理方案
- 防重放攻击
- 访问控制

**下一步**：建议学习 [安全启动与固件验证](04-secure-boot-firmware-verification.html)

