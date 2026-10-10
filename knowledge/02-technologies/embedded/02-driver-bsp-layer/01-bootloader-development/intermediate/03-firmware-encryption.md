---
title: "固件加密与防护技术实战"
description: "深入讲解固件加密技术的原理与实现，包括固件加密、读保护、防回滚机制、密钥管理和安全存储，帮助开发者构建安全可靠的固件防护系统"
slug: "firmware-encryption"

# 分类信息
domain: "驱动与BSP层"
module: "Bootloader开发"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - 固件加密
  - 读保护
  - 安全防护
  - 密钥管理
  - Flash保护
  - 防篡改
prerequisites:
  - "beginner/01-bootloader-basics"
  - "beginner/02-simple-bootloader"
  - "intermediate/02-secure-boot"
related_contents:
  - "intermediate/01-iap-implementation"
  - "intermediate/04-dual-bank-upgrade"

# 学习信息
estimated_time: 85
difficulty_score: 7

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
  - 固件加密
  - Flash读保护
  - 防回滚
  - 密钥管理
  - 安全存储
cover_image: ""
---

# 固件加密与防护技术实战

## 概述

固件加密是保护嵌入式系统知识产权和防止恶意攻击的重要手段。通过对固件进行加密，即使攻击者获取了固件文件，也无法直接读取和分析其中的代码和数据。结合Flash读保护、防回滚机制和安全密钥管理，可以构建多层次的固件防护体系。

本教程将带你从零开始实现完整的固件加密和防护方案，包括：

- 固件加密的基本原理和算法选择
- AES加密算法的实现和应用
- Flash读保护和写保护机制
- 防回滚和版本控制
- 密钥的安全生成、存储和管理
- 加密固件的启动流程

完成本教程后，你将能够：

- 理解固件加密的核心原理和重要性
- 掌握AES加密算法的使用方法
- 实现固件的加密和解密功能
- 配置Flash保护机制防止固件泄露
- 设计安全的密钥管理方案
- 构建完整的固件防护系统

## 前置知识

在开始本教程之前，你需要：

- 理解Bootloader的基本概念和工作原理
- 熟悉C语言编程和指针操作
- 了解基本的密码学概念（对称加密、非对称加密）
- 掌握Flash存储器的操作方法
- 了解安全启动的基本原理

## 学习目标

通过本教程，你将学会：

1. 选择合适的加密算法保护固件
2. 实现AES-128/256加密和解密
3. 配置STM32的Flash读保护机制
4. 实现防回滚和版本管理
5. 安全地生成、存储和使用密钥
6. 构建加密固件的完整启动流程


## 准备工作

### 硬件准备

- STM32开发板（本教程使用STM32F407）
- USB转串口模块（用于调试输出）
- ST-Link调试器（用于固件烧录）
- 杜邦线若干

### 软件准备

- Keil MDK或STM32CubeIDE开发环境
- STM32CubeMX配置工具
- Python 3.x（用于固件加密工具）
- pycryptodome库（Python加密库）

```bash
# 安装Python加密库
pip install pycryptodome
```

### 环境配置

1. 安装并配置STM32开发环境
2. 创建新的STM32项目
3. 配置UART用于调试输出
4. 配置系统时钟和基本外设

## 背景知识

### 为什么需要固件加密

在嵌入式系统中，固件包含了产品的核心算法和商业机密。如果固件被轻易读取，会带来严重后果：

**常见威胁**：

1. **知识产权泄露**：竞争对手可以逆向工程，窃取核心算法
2. **产品克隆**：攻击者可以复制固件，制造山寨产品
3. **恶意篡改**：修改固件植入后门或恶意代码
4. **密钥泄露**：固件中的密钥和证书被提取
5. **调试信息泄露**：符号表和调试信息暴露系统细节

**固件加密的价值**：

- **保护知识产权**：防止核心算法被窃取
- **防止产品克隆**：增加复制产品的难度
- **提高安全性**：即使固件被获取也无法直接使用
- **满足合规要求**：符合行业安全标准
- **增强竞争力**：保护技术优势

### 加密算法选择

选择合适的加密算法需要平衡安全性、性能和资源消耗：

| 算法 | 密钥长度 | 安全性 | 速度 | 资源消耗 | 适用场景 |
|------|---------|--------|------|---------|---------|
| AES-128 | 128位 | 高 | 快 | 低 | 通用场景 |
| AES-256 | 256位 | 很高 | 较快 | 中等 | 高安全要求 |
| ChaCha20 | 256位 | 很高 | 很快 | 低 | 软件实现 |
| SM4 | 128位 | 高 | 中等 | 中等 | 国密标准 |

**推荐选择**：

- **资源受限设备**：AES-128（硬件加速）
- **高安全要求**：AES-256
- **纯软件实现**：ChaCha20
- **国密合规**：SM4

### AES加密原理

AES (Advanced Encryption Standard) 是目前最广泛使用的对称加密算法。

**核心特性**：

- **分组加密**：将数据分成128位（16字节）的块
- **密钥长度**：支持128、192、256位密钥
- **加密轮数**：AES-128为10轮，AES-256为14轮
- **安全性高**：目前没有有效的攻击方法

**加密模式**：

1. **ECB (Electronic Codebook)**：
   - 最简单的模式
   - 相同明文产生相同密文
   - 不推荐使用（不安全）

2. **CBC (Cipher Block Chaining)**：
   - 每个块与前一个密文块异或
   - 需要初始化向量(IV)
   - 适合加密大量数据

3. **CTR (Counter)**：
   - 将块密码转换为流密码
   - 可以并行加密
   - 适合随机访问

4. **GCM (Galois/Counter Mode)**：
   - 提供加密和认证
   - 性能好，安全性高
   - 推荐用于现代系统


## 核心内容

### 1. AES加密实现

我们首先实现AES加密的核心功能，使用mbedTLS库提供的AES接口。

#### AES加密基础函数

```c
#include "mbedtls/aes.h"
#include "mbedtls/gcm.h"
#include <string.h>

// AES密钥长度
#define AES_KEY_SIZE 16  // 128位
#define AES_BLOCK_SIZE 16  // 128位块

/**
 * @brief AES-128 ECB模式加密
 * @param key 密钥（16字节）
 * @param input 输入数据（16字节）
 * @param output 输出数据（16字节）
 * @return 0成功，-1失败
 */
int AES_Encrypt_ECB(const uint8_t *key, const uint8_t *input, uint8_t *output) {
    mbedtls_aes_context aes_ctx;
    int ret;
    
    // 初始化AES上下文
    mbedtls_aes_init(&aes_ctx);
    
    // 设置加密密钥
    ret = mbedtls_aes_setkey_enc(&aes_ctx, key, AES_KEY_SIZE * 8);
    if (ret != 0) {
        mbedtls_aes_free(&aes_ctx);
        return -1;
    }
    
    // 加密一个块
    ret = mbedtls_aes_crypt_ecb(&aes_ctx, MBEDTLS_AES_ENCRYPT, input, output);
    
    // 释放资源
    mbedtls_aes_free(&aes_ctx);
    
    return (ret == 0) ? 0 : -1;
}

/**
 * @brief AES-128 ECB模式解密
 * @param key 密钥（16字节）
 * @param input 输入数据（16字节）
 * @param output 输出数据（16字节）
 * @return 0成功，-1失败
 */
int AES_Decrypt_ECB(const uint8_t *key, const uint8_t *input, uint8_t *output) {
    mbedtls_aes_context aes_ctx;
    int ret;
    
    // 初始化AES上下文
    mbedtls_aes_init(&aes_ctx);
    
    // 设置解密密钥
    ret = mbedtls_aes_setkey_dec(&aes_ctx, key, AES_KEY_SIZE * 8);
    if (ret != 0) {
        mbedtls_aes_free(&aes_ctx);
        return -1;
    }
    
    // 解密一个块
    ret = mbedtls_aes_crypt_ecb(&aes_ctx, MBEDTLS_AES_DECRYPT, input, output);
    
    // 释放资源
    mbedtls_aes_free(&aes_ctx);
    
    return (ret == 0) ? 0 : -1;
}
```

#### AES-CBC模式加密

CBC模式更安全，适合加密大量数据：

```c
/**
 * @brief AES-128 CBC模式加密
 * @param key 密钥（16字节）
 * @param iv 初始化向量（16字节）
 * @param input 输入数据
 * @param input_len 输入数据长度（必须是16的倍数）
 * @param output 输出数据
 * @return 0成功，-1失败
 */
int AES_Encrypt_CBC(const uint8_t *key, const uint8_t *iv,
                    const uint8_t *input, size_t input_len,
                    uint8_t *output) {
    mbedtls_aes_context aes_ctx;
    uint8_t iv_copy[AES_BLOCK_SIZE];
    int ret;
    
    // 检查输入长度
    if (input_len % AES_BLOCK_SIZE != 0) {
        return -1;
    }
    
    // 复制IV（因为加密过程会修改它）
    memcpy(iv_copy, iv, AES_BLOCK_SIZE);
    
    // 初始化AES上下文
    mbedtls_aes_init(&aes_ctx);
    
    // 设置加密密钥
    ret = mbedtls_aes_setkey_enc(&aes_ctx, key, AES_KEY_SIZE * 8);
    if (ret != 0) {
        mbedtls_aes_free(&aes_ctx);
        return -1;
    }
    
    // CBC模式加密
    ret = mbedtls_aes_crypt_cbc(&aes_ctx, MBEDTLS_AES_ENCRYPT,
                                input_len, iv_copy, input, output);
    
    // 释放资源
    mbedtls_aes_free(&aes_ctx);
    
    return (ret == 0) ? 0 : -1;
}

/**
 * @brief AES-128 CBC模式解密
 * @param key 密钥（16字节）
 * @param iv 初始化向量（16字节）
 * @param input 输入数据
 * @param input_len 输入数据长度（必须是16的倍数）
 * @param output 输出数据
 * @return 0成功，-1失败
 */
int AES_Decrypt_CBC(const uint8_t *key, const uint8_t *iv,
                    const uint8_t *input, size_t input_len,
                    uint8_t *output) {
    mbedtls_aes_context aes_ctx;
    uint8_t iv_copy[AES_BLOCK_SIZE];
    int ret;
    
    // 检查输入长度
    if (input_len % AES_BLOCK_SIZE != 0) {
        return -1;
    }
    
    // 复制IV
    memcpy(iv_copy, iv, AES_BLOCK_SIZE);
    
    // 初始化AES上下文
    mbedtls_aes_init(&aes_ctx);
    
    // 设置解密密钥
    ret = mbedtls_aes_setkey_dec(&aes_ctx, key, AES_KEY_SIZE * 8);
    if (ret != 0) {
        mbedtls_aes_free(&aes_ctx);
        return -1;
    }
    
    // CBC模式解密
    ret = mbedtls_aes_crypt_cbc(&aes_ctx, MBEDTLS_AES_DECRYPT,
                                input_len, iv_copy, input, output);
    
    // 释放资源
    mbedtls_aes_free(&aes_ctx);
    
    return (ret == 0) ? 0 : -1;
}
```

#### 数据填充处理

由于AES是分组加密，需要对不足16字节的数据进行填充：

```c
/**
 * @brief PKCS7填充
 * @param data 数据缓冲区
 * @param data_len 实际数据长度
 * @param buffer_size 缓冲区大小
 * @return 填充后的长度
 */
size_t PKCS7_Pad(uint8_t *data, size_t data_len, size_t buffer_size) {
    // 计算需要填充的字节数
    size_t padding_len = AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE);
    
    // 检查缓冲区是否足够
    if (data_len + padding_len > buffer_size) {
        return 0;
    }
    
    // 填充
    for (size_t i = 0; i < padding_len; i++) {
        data[data_len + i] = (uint8_t)padding_len;
    }
    
    return data_len + padding_len;
}

/**
 * @brief 移除PKCS7填充
 * @param data 数据缓冲区
 * @param data_len 数据长度
 * @return 移除填充后的实际数据长度
 */
size_t PKCS7_Unpad(uint8_t *data, size_t data_len) {
    if (data_len == 0 || data_len % AES_BLOCK_SIZE != 0) {
        return 0;
    }
    
    // 读取最后一个字节（填充长度）
    uint8_t padding_len = data[data_len - 1];
    
    // 验证填充
    if (padding_len == 0 || padding_len > AES_BLOCK_SIZE) {
        return 0;
    }
    
    // 检查所有填充字节是否正确
    for (size_t i = data_len - padding_len; i < data_len; i++) {
        if (data[i] != padding_len) {
            return 0;
        }
    }
    
    return data_len - padding_len;
}
```


### 2. 固件加密工具

创建一个Python工具用于加密固件文件：

```python
#!/usr/bin/env python3
"""
固件加密工具
使用AES-128 CBC模式加密固件
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct
import sys
import os

class FirmwareEncryptor:
    def __init__(self, key=None, iv=None):
        """初始化加密器"""
        self.key = key if key else get_random_bytes(16)  # 128位密钥
        self.iv = iv if iv else get_random_bytes(16)  # 128位IV
    
    def save_key(self, key_path):
        """保存密钥到文件"""
        with open(key_path, 'wb') as f:
            f.write(self.key)
            f.write(self.iv)
        print(f"Key saved to {key_path}")
    
    def load_key(self, key_path):
        """从文件加载密钥"""
        with open(key_path, 'rb') as f:
            self.key = f.read(16)
            self.iv = f.read(16)
        print(f"Key loaded from {key_path}")
    
    def encrypt_firmware(self, firmware_path, output_path):
        """加密固件"""
        # 读取固件
        with open(firmware_path, 'rb') as f:
            firmware_data = f.read()
        
        print(f"Original firmware size: {len(firmware_data)} bytes")
        
        # PKCS7填充
        padded_data = pad(firmware_data, AES.block_size)
        print(f"Padded firmware size: {len(padded_data)} bytes")
        
        # 创建AES加密器
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        
        # 加密
        encrypted_data = cipher.encrypt(padded_data)
        
        # 构建加密固件格式
        # [魔数(4字节)][原始大小(4字节)][IV(16字节)][加密数据]
        encrypted_firmware = struct.pack('<I', 0x45435246)  # "FRCE"
        encrypted_firmware += struct.pack('<I', len(firmware_data))
        encrypted_firmware += self.iv
        encrypted_firmware += encrypted_data
        
        # 保存加密固件
        with open(output_path, 'wb') as f:
            f.write(encrypted_firmware)
        
        print(f"Encrypted firmware saved to {output_path}")
        print(f"Total size: {len(encrypted_firmware)} bytes")
        
        # 打印密钥和IV（用于嵌入Bootloader）
        print("\nKey (hex):")
        print(' '.join(f'0x{b:02X},' for b in self.key))
        print("\nIV (hex):")
        print(' '.join(f'0x{b:02X},' for b in self.iv))
    
    def decrypt_firmware(self, encrypted_path, output_path):
        """解密固件（用于验证）"""
        # 读取加密固件
        with open(encrypted_path, 'rb') as f:
            encrypted_firmware = f.read()
        
        # 解析格式
        magic = struct.unpack('<I', encrypted_firmware[0:4])[0]
        if magic != 0x45435246:
            print("Invalid encrypted firmware format")
            return False
        
        original_size = struct.unpack('<I', encrypted_firmware[4:8])[0]
        iv = encrypted_firmware[8:24]
        encrypted_data = encrypted_firmware[24:]
        
        print(f"Original size: {original_size} bytes")
        print(f"Encrypted size: {len(encrypted_data)} bytes")
        
        # 创建AES解密器
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # 解密
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 移除填充
        firmware_data = unpad(decrypted_data, AES.block_size)
        
        # 验证大小
        if len(firmware_data) != original_size:
            print(f"Size mismatch: expected {original_size}, got {len(firmware_data)}")
            return False
        
        # 保存解密固件
        with open(output_path, 'wb') as f:
            f.write(firmware_data)
        
        print(f"Decrypted firmware saved to {output_path}")
        return True

# 使用示例
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Encrypt: python firmware_encryptor.py encrypt <firmware.bin> <output.enc>")
        print("  Decrypt: python firmware_encryptor.py decrypt <firmware.enc> <output.bin>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'encrypt':
        if len(sys.argv) != 4:
            print("Usage: python firmware_encryptor.py encrypt <firmware.bin> <output.enc>")
            sys.exit(1)
        
        firmware_path = sys.argv[2]
        output_path = sys.argv[3]
        
        # 创建加密器
        encryptor = FirmwareEncryptor()
        
        # 加密固件
        encryptor.encrypt_firmware(firmware_path, output_path)
        
        # 保存密钥
        key_path = output_path + '.key'
        encryptor.save_key(key_path)
        
    elif command == 'decrypt':
        if len(sys.argv) != 5:
            print("Usage: python firmware_encryptor.py decrypt <firmware.enc> <key_file> <output.bin>")
            sys.exit(1)
        
        encrypted_path = sys.argv[2]
        key_path = sys.argv[3]
        output_path = sys.argv[4]
        
        # 创建解密器
        encryptor = FirmwareEncryptor()
        encryptor.load_key(key_path)
        
        # 解密固件
        encryptor.decrypt_firmware(encrypted_path, output_path)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
```

**使用方法**：

```bash
# 加密固件
python firmware_encryptor.py encrypt application.bin application.enc

# 解密固件（验证）
python firmware_encryptor.py decrypt application.enc application.enc.key application_dec.bin
```


### 3. Bootloader固件解密

在Bootloader中实现固件解密功能：

```c
#include "stm32f4xx.h"
#include "mbedtls/aes.h"
#include <string.h>

// 加密固件格式
#define ENCRYPTED_MAGIC 0x45435246  // "FRCE"

// 嵌入的AES密钥（由加密工具生成）
const uint8_t aes_key[16] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// 加密固件信息
typedef struct {
    uint32_t magic;
    uint32_t original_size;
    uint8_t iv[16];
    uint8_t *encrypted_data;
    uint32_t encrypted_size;
} EncryptedFirmware_t;

/**
 * @brief 解析加密固件
 * @param address 加密固件地址
 * @param info 输出的固件信息
 * @return 0成功，-1失败
 */
int ParseEncryptedFirmware(uint32_t address, EncryptedFirmware_t *info) {
    uint8_t *data = (uint8_t*)address;
    
    // 读取魔数
    memcpy(&info->magic, data, 4);
    if (info->magic != ENCRYPTED_MAGIC) {
        printf("Invalid encrypted firmware magic: 0x%08X\r\n", info->magic);
        return -1;
    }
    
    // 读取原始大小
    memcpy(&info->original_size, data + 4, 4);
    
    // 读取IV
    memcpy(info->iv, data + 8, 16);
    
    // 加密数据指针
    info->encrypted_data = data + 24;
    
    // 计算加密数据大小（向上取整到16字节）
    info->encrypted_size = ((info->original_size + 15) / 16) * 16;
    
    printf("Encrypted firmware info:\r\n");
    printf("  Original size: %u bytes\r\n", info->original_size);
    printf("  Encrypted size: %u bytes\r\n", info->encrypted_size);
    
    return 0;
}

/**
 * @brief 解密固件到RAM
 * @param encrypted_info 加密固件信息
 * @param output_buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @return 0成功，-1失败
 */
int DecryptFirmware(EncryptedFirmware_t *encrypted_info,
                    uint8_t *output_buffer, uint32_t buffer_size) {
    // 检查缓冲区大小
    if (buffer_size < encrypted_info->encrypted_size) {
        printf("Output buffer too small\r\n");
        return -1;
    }
    
    printf("Decrypting firmware...\r\n");
    
    // 使用AES-CBC解密
    int ret = AES_Decrypt_CBC(
        aes_key,
        encrypted_info->iv,
        encrypted_info->encrypted_data,
        encrypted_info->encrypted_size,
        output_buffer
    );
    
    if (ret != 0) {
        printf("Decryption failed\r\n");
        return -1;
    }
    
    // 移除填充
    size_t actual_size = PKCS7_Unpad(output_buffer, encrypted_info->encrypted_size);
    if (actual_size != encrypted_info->original_size) {
        printf("Padding removal failed\r\n");
        return -1;
    }
    
    printf("Firmware decrypted successfully\r\n");
    return 0;
}

/**
 * @brief 就地解密固件（直接在Flash中解密）
 * @param encrypted_info 加密固件信息
 * @param output_address 输出地址（Flash）
 * @return 0成功，-1失败
 * @note 需要足够的RAM作为临时缓冲区
 */
int DecryptFirmwareInPlace(EncryptedFirmware_t *encrypted_info,
                           uint32_t output_address) {
    // 分配临时缓冲区（使用RAM）
    #define DECRYPT_BUFFER_SIZE (16 * 1024)  // 16KB缓冲区
    static uint8_t decrypt_buffer[DECRYPT_BUFFER_SIZE];
    
    uint32_t remaining = encrypted_info->encrypted_size;
    uint32_t offset = 0;
    
    // 解锁Flash
    FLASH_Unlock();
    
    // 擦除目标区域
    printf("Erasing target flash...\r\n");
    uint32_t erase_addr = output_address;
    uint32_t end_addr = output_address + encrypted_info->original_size;
    
    while (erase_addr < end_addr) {
        if (!FLASH_EraseSector(erase_addr)) {
            printf("Flash erase failed\r\n");
            FLASH_Lock();
            return -1;
        }
        
        // 移动到下一个扇区
        uint8_t sector = FLASH_GetSector(erase_addr);
        if (sector < 4) {
            erase_addr += 0x4000;  // 16KB
        } else if (sector == 4) {
            erase_addr += 0x10000;  // 64KB
        } else {
            erase_addr += 0x20000;  // 128KB
        }
    }
    
    // 分块解密并写入Flash
    printf("Decrypting and writing to flash...\r\n");
    
    while (remaining > 0) {
        uint32_t chunk_size = (remaining > DECRYPT_BUFFER_SIZE) ? 
                              DECRYPT_BUFFER_SIZE : remaining;
        
        // 解密一块数据
        int ret = AES_Decrypt_CBC(
            aes_key,
            encrypted_info->iv,
            encrypted_info->encrypted_data + offset,
            chunk_size,
            decrypt_buffer
        );
        
        if (ret != 0) {
            printf("Decryption failed at offset %u\r\n", offset);
            FLASH_Lock();
            return -1;
        }
        
        // 写入Flash
        uint32_t write_size = chunk_size;
        if (offset + chunk_size > encrypted_info->original_size) {
            // 最后一块，移除填充
            write_size = encrypted_info->original_size - offset;
        }
        
        if (!FLASH_WriteData(output_address + offset,
                            (uint32_t*)decrypt_buffer,
                            write_size / 4)) {
            printf("Flash write failed at offset %u\r\n", offset);
            FLASH_Lock();
            return -1;
        }
        
        offset += chunk_size;
        remaining -= chunk_size;
        
        // 打印进度
        uint8_t progress = (offset * 100) / encrypted_info->encrypted_size;
        printf("Progress: %u%%\r", progress);
    }
    
    printf("\nDecryption complete\r\n");
    
    // 锁定Flash
    FLASH_Lock();
    
    return 0;
}
```


### 4. Flash读保护机制

STM32提供了多级Flash读保护，防止固件被读取。

#### 读保护级别

STM32 Flash读保护分为三个级别：

| 级别 | 说明 | 调试接口 | Flash读取 | 可恢复性 |
|------|------|---------|----------|---------|
| Level 0 | 无保护 | 可用 | 可读 | - |
| Level 1 | 调试保护 | 禁用 | 不可读 | 可恢复（擦除Flash） |
| Level 2 | 永久保护 | 禁用 | 不可读 | 不可恢复 |

**注意**：Level 2是不可逆的，一旦设置无法恢复，请谨慎使用！

#### 读保护配置

```c
#include "stm32f4xx.h"

/**
 * @brief 获取当前读保护级别
 * @return 0=Level0, 1=Level1, 2=Level2
 */
uint8_t FLASH_GetReadProtectionLevel(void) {
    uint8_t rdp = (FLASH->OPTCR & FLASH_OPTCR_RDP) >> 8;
    
    if (rdp == 0xAA) {
        return 0;  // Level 0
    } else if (rdp == 0xCC) {
        return 2;  // Level 2
    } else {
        return 1;  // Level 1
    }
}

/**
 * @brief 设置读保护级别1
 * @note 设置后需要复位才能生效
 * @warning 这会禁用调试接口！
 */
void FLASH_SetReadProtectionLevel1(void) {
    // 检查当前级别
    uint8_t current_level = FLASH_GetReadProtectionLevel();
    if (current_level == 1) {
        printf("Already at Level 1\r\n");
        return;
    }
    
    if (current_level == 2) {
        printf("Cannot change from Level 2\r\n");
        return;
    }
    
    printf("Setting read protection to Level 1...\r\n");
    
    // 解锁Flash和选项字节
    FLASH_Unlock();
    FLASH_OB_Unlock();
    
    // 等待操作完成
    while (FLASH->SR & FLASH_SR_BSY);
    
    // 设置RDP为Level 1（任何非0xAA和0xCC的值）
    FLASH->OPTCR &= ~FLASH_OPTCR_RDP;
    FLASH->OPTCR |= (0x33 << 8);  // Level 1
    
    // 启动选项字节编程
    FLASH->OPTCR |= FLASH_OPTCR_OPTSTRT;
    
    // 等待完成
    while (FLASH->SR & FLASH_SR_BSY);
    
    // 锁定
    FLASH_OB_Lock();
    FLASH_Lock();
    
    printf("Read protection Level 1 set\r\n");
    printf("System will reset to apply changes\r\n");
    
    HAL_Delay(1000);
    NVIC_SystemReset();
}

/**
 * @brief 移除读保护（Level 1 -> Level 0）
 * @warning 这会擦除整个Flash！
 */
void FLASH_RemoveReadProtection(void) {
    uint8_t current_level = FLASH_GetReadProtectionLevel();
    
    if (current_level == 0) {
        printf("Already at Level 0\r\n");
        return;
    }
    
    if (current_level == 2) {
        printf("Cannot remove Level 2 protection\r\n");
        return;
    }
    
    printf("WARNING: Removing read protection will erase all Flash!\r\n");
    printf("Press any key to continue or reset to cancel...\r\n");
    
    // 等待用户确认
    // ...
    
    // 解锁
    FLASH_Unlock();
    FLASH_OB_Unlock();
    
    // 设置RDP为Level 0
    FLASH->OPTCR &= ~FLASH_OPTCR_RDP;
    FLASH->OPTCR |= (0xAA << 8);
    
    // 启动选项字节编程
    FLASH->OPTCR |= FLASH_OPTCR_OPTSTRT;
    
    // 等待完成
    while (FLASH->SR & FLASH_SR_BSY);
    
    // 锁定
    FLASH_OB_Lock();
    FLASH_Lock();
    
    printf("Read protection removed\r\n");
    printf("Flash has been erased\r\n");
    
    HAL_Delay(1000);
    NVIC_SystemReset();
}
```

#### 写保护配置

除了读保护，还可以配置写保护防止特定扇区被修改：

```c
/**
 * @brief 启用Bootloader区域写保护
 * @note 保护Sector 0-1（Bootloader区域）
 */
void FLASH_EnableBootloaderWriteProtection(void) {
    printf("Enabling Bootloader write protection...\r\n");
    
    // 解锁
    FLASH_Unlock();
    FLASH_OB_Unlock();
    
    // 读取当前写保护状态
    uint32_t wrp = FLASH->OPTCR & 0x0FFF;
    
    // 设置Sector 0-1写保护
    wrp &= ~(FLASH_OPTCR_nWRP_0 | FLASH_OPTCR_nWRP_1);
    
    // 更新选项字节
    FLASH->OPTCR = (FLASH->OPTCR & ~0x0FFF) | wrp;
    
    // 启动选项字节编程
    FLASH->OPTCR |= FLASH_OPTCR_OPTSTRT;
    
    // 等待完成
    while (FLASH->SR & FLASH_SR_BSY);
    
    // 锁定
    FLASH_OB_Lock();
    FLASH_Lock();
    
    printf("Bootloader write protection enabled\r\n");
}

/**
 * @brief 检查扇区是否被写保护
 * @param sector 扇区号（0-11）
 * @return 1=受保护，0=未保护
 */
uint8_t FLASH_IsSectorWriteProtected(uint8_t sector) {
    if (sector > 11) {
        return 0;
    }
    
    uint32_t wrp = FLASH->OPTCR & 0x0FFF;
    return ((wrp & (1 << sector)) == 0) ? 1 : 0;
}
```


### 5. 密钥管理

密钥的安全管理是整个加密系统的关键。

#### 密钥存储方案

**方案1：嵌入Bootloader（最简单）**

```c
// 直接在代码中定义密钥
const uint8_t aes_key[16] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};
```

**优点**：实现简单，无需额外存储
**缺点**：密钥固定，所有设备使用相同密钥

**方案2：使用设备唯一ID派生密钥**

```c
#include "mbedtls/md.h"

/**
 * @brief 从设备唯一ID派生密钥
 * @param derived_key 输出的派生密钥（16字节）
 */
void DeriveKeyFromUID(uint8_t *derived_key) {
    // 读取STM32唯一ID（96位）
    uint32_t uid[3];
    uid[0] = *(uint32_t*)0x1FFF7A10;
    uid[1] = *(uint32_t*)0x1FFF7A14;
    uid[2] = *(uint32_t*)0x1FFF7A18;
    
    // 主密钥（存储在Bootloader中）
    const uint8_t master_key[16] = {
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
    };
    
    // 使用HMAC-SHA256派生密钥
    mbedtls_md_context_t md_ctx;
    const mbedtls_md_info_t *md_info;
    
    mbedtls_md_init(&md_ctx);
    md_info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    
    mbedtls_md_setup(&md_ctx, md_info, 1);  // 1 = HMAC
    mbedtls_md_hmac_starts(&md_ctx, master_key, 16);
    mbedtls_md_hmac_update(&md_ctx, (uint8_t*)uid, 12);
    
    uint8_t hash[32];
    mbedtls_md_hmac_finish(&md_ctx, hash);
    mbedtls_md_free(&md_ctx);
    
    // 取前16字节作为派生密钥
    memcpy(derived_key, hash, 16);
    
    printf("Derived key from UID:\r\n");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", derived_key[i]);
    }
    printf("\r\n");
}
```

**优点**：每个设备有唯一密钥
**缺点**：需要为每个设备生成专用固件

**方案3：使用OTP区域存储密钥**

```c
// OTP区域地址（STM32F4）
#define OTP_BASE_ADDRESS 0x1FFF7800
#define OTP_KEY_OFFSET 0x00

/**
 * @brief 从OTP读取密钥
 * @param key 输出的密钥（16字节）
 * @return 0成功，-1失败
 */
int ReadKeyFromOTP(uint8_t *key) {
    uint32_t *otp_addr = (uint32_t*)(OTP_BASE_ADDRESS + OTP_KEY_OFFSET);
    
    // 读取4个32位字（16字节）
    for (int i = 0; i < 4; i++) {
        uint32_t word = otp_addr[i];
        key[i * 4 + 0] = (word >> 0) & 0xFF;
        key[i * 4 + 1] = (word >> 8) & 0xFF;
        key[i * 4 + 2] = (word >> 16) & 0xFF;
        key[i * 4 + 3] = (word >> 24) & 0xFF;
    }
    
    // 检查密钥是否为空（全0xFF表示未编程）
    uint8_t is_empty = 1;
    for (int i = 0; i < 16; i++) {
        if (key[i] != 0xFF) {
            is_empty = 0;
            break;
        }
    }
    
    if (is_empty) {
        printf("OTP key is empty\r\n");
        return -1;
    }
    
    printf("Key read from OTP\r\n");
    return 0;
}

/**
 * @brief 将密钥写入OTP
 * @param key 密钥（16字节）
 * @warning OTP只能写入一次，不可修改！
 */
void WriteKeyToOTP(const uint8_t *key) {
    printf("WARNING: Writing to OTP is irreversible!\r\n");
    printf("Press any key to continue or reset to cancel...\r\n");
    
    // 等待用户确认
    // ...
    
    // 解锁Flash
    FLASH_Unlock();
    
    uint32_t *otp_addr = (uint32_t*)(OTP_BASE_ADDRESS + OTP_KEY_OFFSET);
    
    // 写入4个32位字
    for (int i = 0; i < 4; i++) {
        uint32_t word = (key[i * 4 + 0] << 0) |
                       (key[i * 4 + 1] << 8) |
                       (key[i * 4 + 2] << 16) |
                       (key[i * 4 + 3] << 24);
        
        // 编程OTP
        *(__IO uint32_t*)(otp_addr + i) = word;
        
        // 等待完成
        while (FLASH->SR & FLASH_SR_BSY);
    }
    
    // 锁定Flash
    FLASH_Lock();
    
    printf("Key written to OTP\r\n");
}
```

**优点**：密钥安全存储，不易被读取
**缺点**：只能写入一次，无法更改

#### 密钥轮换

为了提高安全性，可以实现密钥轮换机制：

```c
// 密钥版本管理
typedef struct {
    uint8_t version;
    uint8_t key[16];
    uint32_t valid_from;  // 生效时间戳
    uint32_t valid_until;  // 失效时间戳
} KeyInfo_t;

// 存储多个密钥版本
#define MAX_KEY_VERSIONS 4
static KeyInfo_t key_store[MAX_KEY_VERSIONS];

/**
 * @brief 获取当前有效的密钥
 * @param current_time 当前时间戳
 * @return 密钥指针，NULL表示无有效密钥
 */
const uint8_t* GetCurrentKey(uint32_t current_time) {
    for (int i = 0; i < MAX_KEY_VERSIONS; i++) {
        if (key_store[i].valid_from <= current_time &&
            current_time < key_store[i].valid_until) {
            printf("Using key version %u\r\n", key_store[i].version);
            return key_store[i].key;
        }
    }
    
    printf("No valid key found\r\n");
    return NULL;
}

/**
 * @brief 添加新密钥版本
 * @param version 密钥版本号
 * @param key 密钥数据
 * @param valid_from 生效时间
 * @param valid_until 失效时间
 */
void AddKeyVersion(uint8_t version, const uint8_t *key,
                   uint32_t valid_from, uint32_t valid_until) {
    // 找到空闲槽位
    for (int i = 0; i < MAX_KEY_VERSIONS; i++) {
        if (key_store[i].version == 0) {
            key_store[i].version = version;
            memcpy(key_store[i].key, key, 16);
            key_store[i].valid_from = valid_from;
            key_store[i].valid_until = valid_until;
            
            printf("Key version %u added\r\n", version);
            return;
        }
    }
    
    printf("Key store full\r\n");
}
```


### 6. 防回滚机制

防回滚机制防止攻击者将固件降级到存在漏洞的旧版本。

#### 版本号管理

```c
// 固件版本信息
typedef struct {
    uint32_t magic;          // 魔数：0x56455253 ("VERS")
    uint16_t major;          // 主版本号
    uint16_t minor;          // 次版本号
    uint32_t build;          // 编译号
    uint32_t timestamp;      // 编译时间戳
    uint32_t security_version;  // 安全版本号（单调递增）
} FirmwareVersion_t;

// 最低安全版本存储地址
#define MIN_SECURITY_VERSION_ADDR 0x080FC000

/**
 * @brief 读取最低安全版本
 * @return 最低安全版本号
 */
uint32_t ReadMinSecurityVersion(void) {
    uint32_t min_version = *(__IO uint32_t*)MIN_SECURITY_VERSION_ADDR;
    
    // 如果是0xFFFFFFFF（未初始化），返回0
    if (min_version == 0xFFFFFFFF) {
        return 0;
    }
    
    return min_version;
}

/**
 * @brief 更新最低安全版本
 * @param new_version 新的最低版本
 * @return 0成功，-1失败
 */
int UpdateMinSecurityVersion(uint32_t new_version) {
    uint32_t current_min = ReadMinSecurityVersion();
    
    // 只能递增，不能降低
    if (new_version <= current_min) {
        printf("Cannot downgrade security version\r\n");
        return -1;
    }
    
    printf("Updating minimum security version: %u -> %u\r\n",
           current_min, new_version);
    
    // 解锁Flash
    FLASH_Unlock();
    
    // 擦除扇区
    if (!FLASH_EraseSector(MIN_SECURITY_VERSION_ADDR)) {
        FLASH_Lock();
        return -1;
    }
    
    // 写入新版本
    if (!FLASH_ProgramWord(MIN_SECURITY_VERSION_ADDR, new_version)) {
        FLASH_Lock();
        return -1;
    }
    
    // 锁定Flash
    FLASH_Lock();
    
    printf("Security version updated successfully\r\n");
    return 0;
}

/**
 * @brief 验证固件版本
 * @param firmware_version 固件版本信息
 * @return 0允许，-1拒绝
 */
int VerifyFirmwareVersion(FirmwareVersion_t *firmware_version) {
    // 检查魔数
    if (firmware_version->magic != 0x56455253) {
        printf("Invalid version magic\r\n");
        return -1;
    }
    
    // 读取最低安全版本
    uint32_t min_security_version = ReadMinSecurityVersion();
    
    printf("Firmware version: %u.%u.%u (security: %u)\r\n",
           firmware_version->major,
           firmware_version->minor,
           firmware_version->build,
           firmware_version->security_version);
    
    printf("Minimum security version: %u\r\n", min_security_version);
    
    // 检查安全版本
    if (firmware_version->security_version < min_security_version) {
        printf("Firmware security version too old\r\n");
        return -1;
    }
    
    printf("Firmware version check passed\r\n");
    return 0;
}
```

#### 单调计数器

使用OTP区域实现真正的单调计数器：

```c
// OTP单调计数器地址
#define OTP_COUNTER_BASE 0x1FFF7820
#define OTP_COUNTER_SIZE 32  // 32个字节，每个字节一个计数

/**
 * @brief 读取单调计数器
 * @return 当前计数值
 */
uint32_t ReadMonotonicCounter(void) {
    uint8_t *counter_addr = (uint8_t*)OTP_COUNTER_BASE;
    uint32_t count = 0;
    
    // 计算已编程的字节数
    for (int i = 0; i < OTP_COUNTER_SIZE; i++) {
        if (counter_addr[i] != 0xFF) {
            count++;
        } else {
            break;
        }
    }
    
    return count;
}

/**
 * @brief 递增单调计数器
 * @return 0成功，-1失败（计数器已满）
 */
int IncrementMonotonicCounter(void) {
    uint32_t current = ReadMonotonicCounter();
    
    if (current >= OTP_COUNTER_SIZE) {
        printf("Monotonic counter full\r\n");
        return -1;
    }
    
    // 解锁Flash
    FLASH_Unlock();
    
    // 编程下一个字节
    uint8_t *counter_addr = (uint8_t*)(OTP_COUNTER_BASE + current);
    *counter_addr = 0x00;  // 将0xFF变为0x00
    
    // 等待完成
    while (FLASH->SR & FLASH_SR_BSY);
    
    // 锁定Flash
    FLASH_Lock();
    
    printf("Monotonic counter incremented to %u\r\n", current + 1);
    return 0;
}

/**
 * @brief 验证固件的单调计数器
 * @param firmware_counter 固件中的计数器值
 * @return 0验证成功，-1验证失败
 */
int VerifyMonotonicCounter(uint32_t firmware_counter) {
    uint32_t device_counter = ReadMonotonicCounter();
    
    printf("Firmware counter: %u\r\n", firmware_counter);
    printf("Device counter: %u\r\n", device_counter);
    
    if (firmware_counter < device_counter) {
        printf("Firmware counter too old (rollback detected)\r\n");
        return -1;
    }
    
    // 如果固件计数器更新，递增设备计数器
    if (firmware_counter > device_counter) {
        printf("Updating device counter...\r\n");
        
        // 递增到固件计数器值
        while (ReadMonotonicCounter() < firmware_counter) {
            if (IncrementMonotonicCounter() != 0) {
                printf("Failed to update counter\r\n");
                return -1;
            }
        }
    }
    
    printf("Monotonic counter verification passed\r\n");
    return 0;
}
```


### 7. 完整的加密启动流程

将所有组件整合到完整的加密启动系统中：

```c
#include "stm32f4xx.h"
#include "firmware_encryption.h"
#include "flash_protection.h"
#include "version_control.h"

// 加密固件地址
#define ENCRYPTED_FIRMWARE_ADDR 0x08010000
// 解密后的应用程序地址
#define DECRYPTED_APP_ADDR 0x08020000

/**
 * @brief 加密固件启动主流程
 * @return 0成功，-1失败
 */
int EncryptedBoot_Main(void) {
    EncryptedFirmware_t encrypted_info;
    FirmwareVersion_t firmware_version;
    int ret;
    
    printf("\r\n");
    printf("========================================\r\n");
    printf("  Encrypted Firmware Boot\r\n");
    printf("========================================\r\n");
    
    // 1. 检查Flash读保护状态
    uint8_t rdp_level = FLASH_GetReadProtectionLevel();
    printf("Read protection level: %u\r\n", rdp_level);
    
    if (rdp_level == 0) {
        printf("WARNING: Flash is not protected!\r\n");
        printf("Consider enabling read protection for production\r\n");
    }
    
    // 2. 解析加密固件
    printf("\r\nParsing encrypted firmware...\r\n");
    ret = ParseEncryptedFirmware(ENCRYPTED_FIRMWARE_ADDR, &encrypted_info);
    if (ret != 0) {
        printf("Failed to parse encrypted firmware\r\n");
        return -1;
    }
    
    // 3. 提取固件版本信息（假设在固件开头）
    memcpy(&firmware_version, encrypted_info.encrypted_data, 
           sizeof(FirmwareVersion_t));
    
    // 4. 验证固件版本
    printf("\r\nVerifying firmware version...\r\n");
    ret = VerifyFirmwareVersion(&firmware_version);
    if (ret != 0) {
        printf("Firmware version verification failed\r\n");
        return -1;
    }
    
    // 5. 验证单调计数器
    printf("\r\nVerifying monotonic counter...\r\n");
    ret = VerifyMonotonicCounter(firmware_version.security_version);
    if (ret != 0) {
        printf("Monotonic counter verification failed\r\n");
        return -1;
    }
    
    // 6. 解密固件
    printf("\r\nDecrypting firmware...\r\n");
    ret = DecryptFirmwareInPlace(&encrypted_info, DECRYPTED_APP_ADDR);
    if (ret != 0) {
        printf("Firmware decryption failed\r\n");
        return -1;
    }
    
    // 7. 验证解密后的固件（可选：CRC或签名）
    printf("\r\nVerifying decrypted firmware...\r\n");
    // ... CRC或签名验证代码 ...
    
    // 8. 更新最低安全版本
    if (firmware_version.security_version > ReadMinSecurityVersion()) {
        printf("\r\nUpdating minimum security version...\r\n");
        UpdateMinSecurityVersion(firmware_version.security_version);
    }
    
    printf("\r\n========================================\r\n");
    printf("  All security checks passed!\r\n");
    printf("  Jumping to application...\r\n");
    printf("========================================\r\n");
    
    return 0;
}

/**
 * @brief Bootloader主函数
 */
int main(void) {
    // 系统初始化
    SystemInit();
    HAL_Init();
    SystemClock_Config();
    
    // 初始化UART
    UART_Init();
    
    // 初始化LED
    LED_Init();
    
    printf("\r\n");
    printf("========================================\r\n");
    printf("  Secure Bootloader v1.0\r\n");
    printf("  Build: %s %s\r\n", __DATE__, __TIME__);
    printf("========================================\r\n");
    
    // LED快速闪烁表示Bootloader运行
    for (int i = 0; i < 3; i++) {
        LED_On();
        HAL_Delay(100);
        LED_Off();
        HAL_Delay(100);
    }
    
    // 执行加密固件启动
    int ret = EncryptedBoot_Main();
    
    if (ret == 0) {
        // 启动成功，LED常亮2秒
        LED_On();
        HAL_Delay(2000);
        LED_Off();
        
        // 跳转到解密后的应用程序
        JumpToApplication(DECRYPTED_APP_ADDR);
    } else {
        // 启动失败，LED快速闪烁表示错误
        printf("\r\nBoot failed! System halted.\r\n");
        
        while (1) {
            LED_Toggle();
            HAL_Delay(200);
        }
    }
    
    // 永远不会执行到这里
    while (1);
}
```

## 实践示例

### 示例1：完整的固件加密和部署流程

**步骤1：编译应用程序**

```bash
cd application
make clean
make
```

**步骤2：加密固件**

```bash
# 使用Python工具加密固件
python firmware_encryptor.py encrypt application.bin application.enc

# 输出：
# Original firmware size: 32768 bytes
# Padded firmware size: 32768 bytes
# Encrypted firmware saved to application.enc
# Total size: 32792 bytes
#
# Key (hex):
# 0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
# 0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C,
#
# IV (hex):
# 0x91, 0x28, 0x13, 0x40, 0x3A, 0x8C, 0x5F, 0x2D,
# 0xE7, 0xB1, 0x49, 0x9C, 0x73, 0x6A, 0x8E, 0x2F,
```

**步骤3：将密钥嵌入Bootloader**

```c
// 在Bootloader代码中更新密钥
const uint8_t aes_key[16] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};
```

**步骤4：编译并烧录Bootloader**

```bash
cd bootloader
make clean
make
st-flash write bootloader.bin 0x08000000
```

**步骤5：烧录加密固件**

```bash
st-flash write application.enc 0x08010000
```

**步骤6：启用Flash读保护（生产环境）**

```c
// 在Bootloader中调用
FLASH_SetReadProtectionLevel1();
```

**步骤7：测试启动**

设备上电后，Bootloader会：
1. 解析加密固件
2. 验证版本号
3. 验证单调计数器
4. 解密固件到RAM或另一个Flash区域
5. 验证解密后的固件
6. 跳转到应用程序


### 示例2：使用硬件AES加速

STM32F4部分型号支持硬件AES加速，可以显著提高加密解密速度：

```c
#include "stm32f4xx_hal.h"

// 硬件AES句柄
CRYP_HandleTypeDef hcryp;

/**
 * @brief 初始化硬件AES
 * @param key 密钥（16字节）
 * @param iv 初始化向量（16字节）
 * @return 0成功，-1失败
 */
int HW_AES_Init(const uint8_t *key, const uint8_t *iv) {
    // 使能AES时钟
    __HAL_RCC_CRYP_CLK_ENABLE();
    
    // 配置AES
    hcryp.Instance = CRYP;
    hcryp.Init.DataType = CRYP_DATATYPE_8B;
    hcryp.Init.KeySize = CRYP_KEYSIZE_128B;
    hcryp.Init.pKey = (uint32_t*)key;
    hcryp.Init.pInitVect = (uint32_t*)iv;
    hcryp.Init.Algorithm = CRYP_AES_CBC;
    hcryp.Init.DataWidthUnit = CRYP_DATAWIDTHUNIT_BYTE;
    
    if (HAL_CRYP_Init(&hcryp) != HAL_OK) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 硬件AES解密
 * @param input 输入数据
 * @param input_len 输入长度（必须是16的倍数）
 * @param output 输出数据
 * @return 0成功，-1失败
 */
int HW_AES_Decrypt(const uint8_t *input, uint32_t input_len, uint8_t *output) {
    if (input_len % 16 != 0) {
        return -1;
    }
    
    // 执行解密
    if (HAL_CRYP_Decrypt(&hcryp, (uint32_t*)input, input_len,
                         (uint32_t*)output, 5000) != HAL_OK) {
        return -1;
    }
    
    return 0;
}

/**
 * @brief 使用硬件AES解密固件
 * @param encrypted_info 加密固件信息
 * @param output_address 输出地址
 * @return 0成功，-1失败
 */
int DecryptFirmware_HW(EncryptedFirmware_t *encrypted_info,
                       uint32_t output_address) {
    // 初始化硬件AES
    if (HW_AES_Init(aes_key, encrypted_info->iv) != 0) {
        printf("Hardware AES init failed\r\n");
        return -1;
    }
    
    // 分配临时缓冲区
    #define HW_DECRYPT_BUFFER_SIZE (16 * 1024)
    static uint8_t decrypt_buffer[HW_DECRYPT_BUFFER_SIZE];
    
    uint32_t remaining = encrypted_info->encrypted_size;
    uint32_t offset = 0;
    
    // 解锁Flash
    FLASH_Unlock();
    
    // 擦除目标区域
    // ... 擦除代码 ...
    
    // 分块解密
    while (remaining > 0) {
        uint32_t chunk_size = (remaining > HW_DECRYPT_BUFFER_SIZE) ?
                              HW_DECRYPT_BUFFER_SIZE : remaining;
        
        // 硬件解密
        if (HW_AES_Decrypt(encrypted_info->encrypted_data + offset,
                          chunk_size, decrypt_buffer) != 0) {
            printf("Hardware decryption failed\r\n");
            FLASH_Lock();
            return -1;
        }
        
        // 写入Flash
        uint32_t write_size = chunk_size;
        if (offset + chunk_size > encrypted_info->original_size) {
            write_size = encrypted_info->original_size - offset;
        }
        
        if (!FLASH_WriteData(output_address + offset,
                            (uint32_t*)decrypt_buffer,
                            write_size / 4)) {
            FLASH_Lock();
            return -1;
        }
        
        offset += chunk_size;
        remaining -= chunk_size;
        
        printf("Progress: %u%%\r", (offset * 100) / encrypted_info->encrypted_size);
    }
    
    printf("\nHardware decryption complete\r\n");
    
    FLASH_Lock();
    return 0;
}
```

**性能对比**：

| 方法 | 解密速度 | CPU占用 | 功耗 |
|------|---------|---------|------|
| 软件AES | ~1 MB/s | 100% | 高 |
| 硬件AES | ~10 MB/s | <10% | 低 |

### 示例3：混合加密方案

对于大型固件，可以使用混合加密方案：使用RSA加密AES密钥，使用AES加密固件：

```c
/**
 * @brief 混合加密固件格式
 * [魔数(4字节)]
 * [原始大小(4字节)]
 * [加密的AES密钥(256字节，RSA-2048)]
 * [IV(16字节)]
 * [加密的固件数据]
 */

/**
 * @brief 解密AES密钥
 * @param encrypted_key 加密的AES密钥（256字节）
 * @param decrypted_key 输出的解密密钥（16字节）
 * @return 0成功，-1失败
 */
int DecryptAESKey(const uint8_t *encrypted_key, uint8_t *decrypted_key) {
    mbedtls_rsa_context rsa;
    int ret;
    
    // 初始化RSA上下文
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V15, 0);
    
    // 设置RSA私钥（存储在安全区域）
    // ... 设置私钥代码 ...
    
    // 解密AES密钥
    size_t olen;
    ret = mbedtls_rsa_pkcs1_decrypt(&rsa, NULL, NULL,
                                    MBEDTLS_RSA_PRIVATE,
                                    &olen, encrypted_key,
                                    decrypted_key, 16);
    
    mbedtls_rsa_free(&rsa);
    
    if (ret != 0 || olen != 16) {
        printf("Failed to decrypt AES key\r\n");
        return -1;
    }
    
    printf("AES key decrypted successfully\r\n");
    return 0;
}

/**
 * @brief 解密混合加密固件
 * @param firmware_address 固件地址
 * @param output_address 输出地址
 * @return 0成功，-1失败
 */
int DecryptHybridFirmware(uint32_t firmware_address, uint32_t output_address) {
    uint8_t *data = (uint8_t*)firmware_address;
    uint8_t aes_key[16];
    uint8_t iv[16];
    
    // 解析格式
    uint32_t magic = *(uint32_t*)data;
    if (magic != 0x48594252) {  // "HYBR"
        printf("Invalid hybrid firmware format\r\n");
        return -1;
    }
    
    uint32_t original_size = *(uint32_t*)(data + 4);
    uint8_t *encrypted_key = data + 8;
    memcpy(iv, data + 264, 16);
    uint8_t *encrypted_data = data + 280;
    
    // 1. 解密AES密钥
    printf("Decrypting AES key...\r\n");
    if (DecryptAESKey(encrypted_key, aes_key) != 0) {
        return -1;
    }
    
    // 2. 使用解密的AES密钥解密固件
    printf("Decrypting firmware...\r\n");
    EncryptedFirmware_t encrypted_info;
    encrypted_info.original_size = original_size;
    encrypted_info.encrypted_size = ((original_size + 15) / 16) * 16;
    memcpy(encrypted_info.iv, iv, 16);
    encrypted_info.encrypted_data = encrypted_data;
    
    // 使用解密的密钥
    const uint8_t *old_key = aes_key;  // 临时保存
    // ... 解密固件 ...
    
    return 0;
}
```

**优点**：
- AES密钥每次可以不同（随机生成）
- 即使AES密钥泄露，只影响单个固件
- 可以使用不同的RSA密钥对管理不同产品线

**缺点**：
- 需要在设备中存储RSA私钥
- 解密过程更复杂
- 需要更多的存储空间


## 验证与测试

### 测试加密解密功能

```c
/**
 * @brief 测试AES加密解密
 */
void Test_AES_Encryption(void) {
    printf("\r\n=== AES Encryption Test ===\r\n");
    
    // 测试数据
    const uint8_t key[16] = {
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
    };
    
    const uint8_t iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
    };
    
    const char *plaintext = "Hello, Encrypted World! This is a test message.";
    uint8_t encrypted[64];
    uint8_t decrypted[64];
    
    // 填充
    size_t padded_len = PKCS7_Pad((uint8_t*)plaintext, strlen(plaintext), 64);
    printf("Original length: %u\r\n", strlen(plaintext));
    printf("Padded length: %u\r\n", padded_len);
    
    // 加密
    if (AES_Encrypt_CBC(key, iv, (uint8_t*)plaintext, padded_len, encrypted) == 0) {
        printf("Encryption successful\r\n");
        
        // 打印密文
        printf("Encrypted data: ");
        for (size_t i = 0; i < padded_len; i++) {
            printf("%02X ", encrypted[i]);
        }
        printf("\r\n");
    } else {
        printf("Encryption failed\r\n");
        return;
    }
    
    // 解密
    if (AES_Decrypt_CBC(key, iv, encrypted, padded_len, decrypted) == 0) {
        printf("Decryption successful\r\n");
        
        // 移除填充
        size_t original_len = PKCS7_Unpad(decrypted, padded_len);
        decrypted[original_len] = '\0';
        
        // 打印明文
        printf("Decrypted data: %s\r\n", decrypted);
        
        // 验证
        if (memcmp(plaintext, decrypted, strlen(plaintext)) == 0) {
            printf("✓ Test PASSED\r\n");
        } else {
            printf("✗ Test FAILED\r\n");
        }
    } else {
        printf("Decryption failed\r\n");
    }
}

/**
 * @brief 测试Flash保护
 */
void Test_FlashProtection(void) {
    printf("\r\n=== Flash Protection Test ===\r\n");
    
    // 检查读保护级别
    uint8_t rdp_level = FLASH_GetReadProtectionLevel();
    printf("Current RDP level: %u\r\n", rdp_level);
    
    // 检查写保护
    for (uint8_t sector = 0; sector < 8; sector++) {
        uint8_t protected = FLASH_IsSectorWriteProtected(sector);
        printf("Sector %u: %s\r\n", sector,
               protected ? "Write Protected" : "Not Protected");
    }
}

/**
 * @brief 测试版本控制
 */
void Test_VersionControl(void) {
    printf("\r\n=== Version Control Test ===\r\n");
    
    // 读取当前最低版本
    uint32_t min_version = ReadMinSecurityVersion();
    printf("Current minimum security version: %u\r\n", min_version);
    
    // 测试版本验证
    FirmwareVersion_t test_version = {
        .magic = 0x56455253,
        .major = 1,
        .minor = 2,
        .build = 345,
        .timestamp = 1234567890,
        .security_version = min_version + 1
    };
    
    if (VerifyFirmwareVersion(&test_version) == 0) {
        printf("✓ Version verification PASSED\r\n");
    } else {
        printf("✗ Version verification FAILED\r\n");
    }
    
    // 测试单调计数器
    uint32_t counter = ReadMonotonicCounter();
    printf("Monotonic counter: %u\r\n", counter);
}
```

### 性能测试

```c
/**
 * @brief 测试加密解密性能
 */
void Test_Performance(void) {
    printf("\r\n=== Performance Test ===\r\n");
    
    const uint8_t key[16] = {
        0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
        0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
    };
    
    const uint8_t iv[16] = {0};
    
    // 测试不同大小的数据
    uint32_t test_sizes[] = {1024, 4096, 16384, 65536};
    
    for (int i = 0; i < 4; i++) {
        uint32_t size = test_sizes[i];
        uint8_t *data = malloc(size);
        uint8_t *encrypted = malloc(size);
        uint8_t *decrypted = malloc(size);
        
        if (!data || !encrypted || !decrypted) {
            printf("Memory allocation failed\r\n");
            continue;
        }
        
        // 填充测试数据
        for (uint32_t j = 0; j < size; j++) {
            data[j] = j & 0xFF;
        }
        
        // 测试加密
        uint32_t start_time = HAL_GetTick();
        AES_Encrypt_CBC(key, iv, data, size, encrypted);
        uint32_t encrypt_time = HAL_GetTick() - start_time;
        
        // 测试解密
        start_time = HAL_GetTick();
        AES_Decrypt_CBC(key, iv, encrypted, size, decrypted);
        uint32_t decrypt_time = HAL_GetTick() - start_time;
        
        // 计算速度
        float encrypt_speed = (float)size / encrypt_time;  // KB/s
        float decrypt_speed = (float)size / decrypt_time;  // KB/s
        
        printf("Size: %u bytes\r\n", size);
        printf("  Encrypt: %u ms (%.2f KB/s)\r\n", encrypt_time, encrypt_speed);
        printf("  Decrypt: %u ms (%.2f KB/s)\r\n", decrypt_time, decrypt_speed);
        
        // 验证
        if (memcmp(data, decrypted, size) == 0) {
            printf("  ✓ Verification PASSED\r\n");
        } else {
            printf("  ✗ Verification FAILED\r\n");
        }
        
        free(data);
        free(encrypted);
        free(decrypted);
    }
}
```

## 故障排除

### 常见问题

**问题1：解密后的固件无法运行**

可能原因：
- 密钥不匹配
- IV不正确
- 填充处理错误
- Flash写入错误

解决方法：
```c
// 添加详细的调试输出
printf("Encrypted data (first 32 bytes):\r\n");
for (int i = 0; i < 32; i++) {
    printf("%02X ", encrypted_data[i]);
}
printf("\r\n");

printf("Decrypted data (first 32 bytes):\r\n");
for (int i = 0; i < 32; i++) {
    printf("%02X ", decrypted_data[i]);
}
printf("\r\n");

// 验证解密后的栈指针
uint32_t sp = *(uint32_t*)decrypted_address;
printf("Stack pointer: 0x%08X\r\n", sp);
if ((sp & 0x2FFE0000) != 0x20000000) {
    printf("Invalid stack pointer!\r\n");
}
```

**问题2：Flash读保护后无法调试**

这是正常现象。解决方法：
- 开发阶段不启用读保护
- 使用串口输出调试信息
- 预留调试命令接口
- 使用LED指示状态

**问题3：单调计数器用完**

OTP区域有限，计数器会用完。解决方法：
```c
// 使用更大的计数器空间
#define OTP_COUNTER_SIZE 128  // 增加到128字节

// 或使用Flash模拟
#define COUNTER_FLASH_ADDR 0x080FC000
// 每次擦除扇区，重新写入递增的值
```

**问题4：加密固件太大**

加密会增加文件大小（填充）。解决方法：
- 优化固件大小
- 使用压缩（先压缩后加密）
- 分段加密
- 使用流密码模式（CTR）

## 总结

本教程介绍了固件加密与防护的完整技术体系：

1. **加密算法**：AES-128/256 CBC模式，平衡安全性和性能
2. **Flash保护**：读保护和写保护，防止固件被读取和篡改
3. **防回滚**：版本号管理和单调计数器，防止降级攻击
4. **密钥管理**：多种密钥存储方案，确保密钥安全
5. **完整流程**：从固件加密到安全启动的完整实现

通过这些技术的组合使用，可以构建一个安全可靠的固件防护系统，有效保护知识产权和防止恶意攻击。

## 延伸阅读

- [安全启动(Secure Boot)技术详解](./02-secure-boot.html)
- [IAP在线升级功能实现](./01-iap-implementation.html)
- [双区升级与A/B分区策略](./04-dual-bank-upgrade.html)
- NIST Special Publication 800-38A: Recommendation for Block Cipher Modes of Operation
- STM32 Flash保护机制应用笔记
- mbedTLS加密库文档

## 下一步

学习完本教程后，建议继续学习：

1. 双区升级技术，实现更可靠的固件更新
2. OTA升级系统，实现远程固件管理
3. 安全元件的使用，进一步提高系统安全性
4. 密码学高级主题，如椭圆曲线加密、同态加密等
