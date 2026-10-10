---
title: "命令行接口(CLI)实现：构建交互式嵌入式系统"
description: "深入学习命令行接口的设计与实现方法。掌握CLI架构设计、命令解析、参数处理、帮助系统、交互界面等核心技术，学会构建专业的嵌入式系统调试和配置工具。"
slug: "cli-implementation"

# 分类信息
domain: "操作系统层"
module: "裸机编程"
content_type: "tutorial"
skill_level: "intermediate"

# 标签和关联
tags:
  - CLI
  - 命令行
  - 交互界面
  - 命令解析
  - 调试工具
  - 系统配置
prerequisites:
  - "beginner/01-bare-metal-basics.md"
  - "beginner/02-super-loop.md"
  - "intermediate/02-event-driven-architecture.md"
related_contents:
  - "intermediate/04-logging-system.md"
  - "beginner/08-bare-metal-debugging.md"

# 学习信息
estimated_time: 80
difficulty_score: 6

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
  - 命令行接口
  - CLI实现
  - 命令解析
  - 嵌入式调试
  - 交互界面
  - Shell实现
cover_image: ""
---

# 命令行接口(CLI)实现：构建交互式嵌入式系统

## 概述

命令行接口（Command Line Interface, CLI）是嵌入式系统中常用的人机交互方式，通过串口或其他通信接口提供文本命令交互功能。CLI广泛应用于系统调试、参数配置、功能测试和运维管理等场景。

完成本教程学习后，你将能够：

- 理解CLI系统的架构设计原理
- 掌握命令解析和参数处理技术
- 实现完整的命令注册和执行机制
- 设计用户友好的帮助系统
- 构建专业的交互式命令行界面
- 集成历史记录和自动补全功能

## 背景知识

### 什么是CLI？

**命令行接口（CLI）**是一种基于文本的用户界面，用户通过输入命令字符串与系统交互，系统解析命令并执行相应操作，然后返回文本结果。

**典型应用场景**：
- **系统调试**：查看寄存器、内存、变量值
- **参数配置**：设置系统参数、网络配置
- **功能测试**：测试硬件模块、驱动功能
- **运维管理**：查看系统状态、日志信息
- **生产测试**：执行测试命令、读取测试结果

### CLI vs GUI

| 特性 | CLI | GUI |
|------|-----|-----|
| 资源占用 | 极小（几KB） | 大（几十KB到MB） |
| 开发复杂度 | 低 | 高 |
| 学习曲线 | 陡峭 | 平缓 |
| 自动化 | 容易（脚本） | 困难 |
| 远程访问 | 容易（串口/网络） | 需要额外支持 |
| 适用场景 | 调试、配置、专业用户 | 日常操作、普通用户 |

### CLI系统架构

一个完整的CLI系统包含以下核心组件：

```
┌─────────────────────────────────────────┐
│          输入层（Input Layer）           │
│    UART/USB/Telnet/SSH 接收字符         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       输入处理（Input Processing）       │
│  字符回显、退格处理、行编辑、历史记录    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       命令解析（Command Parsing）        │
│  分词、参数提取、命令查找、参数验证      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       命令执行（Command Execution）      │
│  调用命令处理函数、传递参数、返回结果    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       输出层（Output Layer）             │
│    格式化输出、UART/USB 发送字符         │
└─────────────────────────────────────────┘
```

## 核心内容

### 数据结构设计

#### 命令定义

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// 命令处理函数类型
typedef int (*CommandHandler_t)(int argc, char *argv[]);

// 命令结构
typedef struct {
    const char *name;           // 命令名称
    const char *help;           // 帮助信息
    CommandHandler_t handler;   // 处理函数
    uint8_t min_args;          // 最少参数数量
    uint8_t max_args;          // 最多参数数量
} Command_t;

// CLI配置
#define CLI_MAX_COMMANDS    32      // 最大命令数
#define CLI_MAX_LINE_LENGTH 128     // 最大输入行长度
#define CLI_MAX_ARGS        16      // 最大参数数量
#define CLI_HISTORY_SIZE    10      // 历史记录数量
#define CLI_PROMPT          "$ "    // 命令提示符
```

#### CLI上下文

```c
// CLI状态
typedef struct {
    char line_buffer[CLI_MAX_LINE_LENGTH];  // 当前输入行
    uint16_t line_pos;                      // 当前光标位置
    uint16_t line_len;                      // 当前行长度
    
    char history[CLI_HISTORY_SIZE][CLI_MAX_LINE_LENGTH];  // 历史记录
    uint8_t history_count;                  // 历史记录数量
    uint8_t history_index;                  // 当前历史索引
    
    Command_t commands[CLI_MAX_COMMANDS];   // 命令表
    uint8_t command_count;                  // 已注册命令数
    
    bool echo_enabled;                      // 回显使能
    bool running;                           // 运行状态
} CLI_Context_t;

// 全局CLI上下文
static CLI_Context_t g_cli = {0};
```

### CLI初始化

```c
/**
 * @brief 初始化CLI系统
 */
void CLI_Init(void) {
    memset(&g_cli, 0, sizeof(CLI_Context_t));
    g_cli.echo_enabled = true;
    g_cli.running = true;
    
    // 注册内置命令
    CLI_RegisterCommand("help", "显示帮助信息", CMD_Help, 0, 1);
    CLI_RegisterCommand("clear", "清屏", CMD_Clear, 0, 0);
    CLI_RegisterCommand("history", "显示历史命令", CMD_History, 0, 0);
    CLI_RegisterCommand("echo", "回显控制 [on|off]", CMD_Echo, 0, 1);
    
    // 显示欢迎信息
    CLI_Printf("\r\n");
    CLI_Printf("========================================\r\n");
    CLI_Printf("  嵌入式系统命令行接口 v1.0\r\n");
    CLI_Printf("  输入 'help' 查看可用命令\r\n");
    CLI_Printf("========================================\r\n");
    CLI_Printf("\r\n");
    
    // 显示提示符
    CLI_Printf(CLI_PROMPT);
}
```


### 命令注册

```c
/**
 * @brief 注册命令
 * @param name 命令名称
 * @param help 帮助信息
 * @param handler 处理函数
 * @param min_args 最少参数数量
 * @param max_args 最多参数数量
 * @return true: 成功, false: 失败
 */
bool CLI_RegisterCommand(const char *name, const char *help,
                         CommandHandler_t handler,
                         uint8_t min_args, uint8_t max_args) {
    // 检查命令表是否已满
    if(g_cli.command_count >= CLI_MAX_COMMANDS) {
        return false;
    }
    
    // 检查命令是否已存在
    for(uint8_t i = 0; i < g_cli.command_count; i++) {
        if(strcmp(g_cli.commands[i].name, name) == 0) {
            return false;  // 命令已存在
        }
    }
    
    // 添加命令
    Command_t *cmd = &g_cli.commands[g_cli.command_count];
    cmd->name = name;
    cmd->help = help;
    cmd->handler = handler;
    cmd->min_args = min_args;
    cmd->max_args = max_args;
    
    g_cli.command_count++;
    
    return true;
}

/**
 * @brief 注销命令
 * @param name 命令名称
 * @return true: 成功, false: 未找到
 */
bool CLI_UnregisterCommand(const char *name) {
    for(uint8_t i = 0; i < g_cli.command_count; i++) {
        if(strcmp(g_cli.commands[i].name, name) == 0) {
            // 移动后续命令
            for(uint8_t j = i; j < g_cli.command_count - 1; j++) {
                g_cli.commands[j] = g_cli.commands[j + 1];
            }
            g_cli.command_count--;
            return true;
        }
    }
    return false;
}

/**
 * @brief 查找命令
 * @param name 命令名称
 * @return 命令指针，未找到返回NULL
 */
static Command_t* CLI_FindCommand(const char *name) {
    for(uint8_t i = 0; i < g_cli.command_count; i++) {
        if(strcmp(g_cli.commands[i].name, name) == 0) {
            return &g_cli.commands[i];
        }
    }
    return NULL;
}
```

### 输入处理

```c
/**
 * @brief 处理输入字符
 * @param ch 输入字符
 */
void CLI_ProcessChar(char ch) {
    switch(ch) {
        case '\r':  // 回车
        case '\n':  // 换行
            if(g_cli.line_len > 0) {
                // 回显换行
                if(g_cli.echo_enabled) {
                    CLI_Printf("\r\n");
                }
                
                // 添加字符串结束符
                g_cli.line_buffer[g_cli.line_len] = '\0';
                
                // 处理命令
                CLI_ProcessLine(g_cli.line_buffer);
                
                // 添加到历史记录
                CLI_AddHistory(g_cli.line_buffer);
                
                // 清空缓冲区
                g_cli.line_pos = 0;
                g_cli.line_len = 0;
                
                // 显示提示符
                CLI_Printf(CLI_PROMPT);
            } else {
                // 空行，只显示提示符
                if(g_cli.echo_enabled) {
                    CLI_Printf("\r\n");
                }
                CLI_Printf(CLI_PROMPT);
            }
            break;
            
        case '\b':  // 退格
        case 0x7F:  // DEL
            if(g_cli.line_pos > 0) {
                // 移动后续字符
                for(uint16_t i = g_cli.line_pos - 1; i < g_cli.line_len - 1; i++) {
                    g_cli.line_buffer[i] = g_cli.line_buffer[i + 1];
                }
                g_cli.line_pos--;
                g_cli.line_len--;
                
                // 回显退格
                if(g_cli.echo_enabled) {
                    CLI_Printf("\b \b");
                }
            }
            break;
            
        case '\t':  // Tab - 自动补全
            CLI_AutoComplete();
            break;
            
        case 0x1B:  // ESC - 可能是方向键序列
            // 处理ANSI转义序列（方向键等）
            CLI_ProcessEscapeSequence();
            break;
            
        default:
            // 可打印字符
            if(ch >= 0x20 && ch <= 0x7E) {
                if(g_cli.line_len < CLI_MAX_LINE_LENGTH - 1) {
                    // 插入字符
                    if(g_cli.line_pos < g_cli.line_len) {
                        // 在中间插入，移动后续字符
                        for(uint16_t i = g_cli.line_len; i > g_cli.line_pos; i--) {
                            g_cli.line_buffer[i] = g_cli.line_buffer[i - 1];
                        }
                    }
                    
                    g_cli.line_buffer[g_cli.line_pos] = ch;
                    g_cli.line_pos++;
                    g_cli.line_len++;
                    
                    // 回显字符
                    if(g_cli.echo_enabled) {
                        CLI_Printf("%c", ch);
                    }
                }
            }
            break;
    }
}

/**
 * @brief 处理转义序列（方向键等）
 */
static void CLI_ProcessEscapeSequence(void) {
    char seq[3];
    
    // 读取转义序列
    // 注意：这里需要非阻塞读取或超时机制
    if(UART_ReadTimeout(&seq[0], 1, 100) != 1) return;
    if(UART_ReadTimeout(&seq[1], 1, 100) != 1) return;
    
    if(seq[0] == '[') {
        switch(seq[1]) {
            case 'A':  // 上箭头 - 历史记录上一条
                CLI_HistoryUp();
                break;
            case 'B':  // 下箭头 - 历史记录下一条
                CLI_HistoryDown();
                break;
            case 'C':  // 右箭头 - 光标右移
                if(g_cli.line_pos < g_cli.line_len) {
                    g_cli.line_pos++;
                    CLI_Printf("\x1B[C");  // 发送光标右移序列
                }
                break;
            case 'D':  // 左箭头 - 光标左移
                if(g_cli.line_pos > 0) {
                    g_cli.line_pos--;
                    CLI_Printf("\x1B[D");  // 发送光标左移序列
                }
                break;
        }
    }
}
```

### 命令解析

```c
/**
 * @brief 解析命令行
 * @param line 命令行字符串
 */
static void CLI_ProcessLine(char *line) {
    char *argv[CLI_MAX_ARGS];
    int argc = 0;
    
    // 跳过前导空格
    while(*line == ' ' || *line == '\t') {
        line++;
    }
    
    // 如果是空行，直接返回
    if(*line == '\0') {
        return;
    }
    
    // 分词
    char *token = line;
    bool in_quotes = false;
    
    while(*line != '\0' && argc < CLI_MAX_ARGS) {
        if(*line == '"') {
            // 处理引号
            in_quotes = !in_quotes;
            *line = '\0';  // 移除引号
        } else if((*line == ' ' || *line == '\t') && !in_quotes) {
            // 空格分隔符（不在引号内）
            *line = '\0';
            if(token != line) {
                argv[argc++] = token;
            }
            token = line + 1;
        }
        line++;
    }
    
    // 添加最后一个参数
    if(token != line && *token != '\0') {
        argv[argc++] = token;
    }
    
    // 执行命令
    if(argc > 0) {
        CLI_ExecuteCommand(argc, argv);
    }
}

/**
 * @brief 执行命令
 * @param argc 参数数量
 * @param argv 参数数组
 */
static void CLI_ExecuteCommand(int argc, char *argv[]) {
    // 查找命令
    Command_t *cmd = CLI_FindCommand(argv[0]);
    
    if(cmd == NULL) {
        CLI_Printf("错误: 未知命令 '%s'\r\n", argv[0]);
        CLI_Printf("输入 'help' 查看可用命令\r\n");
        return;
    }
    
    // 检查参数数量
    int arg_count = argc - 1;  // 不包括命令名
    
    if(arg_count < cmd->min_args) {
        CLI_Printf("错误: 参数太少，至少需要 %d 个参数\r\n", cmd->min_args);
        CLI_Printf("用法: %s %s\r\n", cmd->name, cmd->help);
        return;
    }
    
    if(cmd->max_args != 255 && arg_count > cmd->max_args) {
        CLI_Printf("错误: 参数太多，最多 %d 个参数\r\n", cmd->max_args);
        CLI_Printf("用法: %s %s\r\n", cmd->name, cmd->help);
        return;
    }
    
    // 调用命令处理函数
    int result = cmd->handler(argc, argv);
    
    if(result != 0) {
        CLI_Printf("命令执行失败，错误码: %d\r\n", result);
    }
}
```


### 历史记录功能

```c
/**
 * @brief 添加命令到历史记录
 * @param line 命令行字符串
 */
static void CLI_AddHistory(const char *line) {
    // 不记录空命令
    if(line[0] == '\0') {
        return;
    }
    
    // 不记录重复命令
    if(g_cli.history_count > 0) {
        uint8_t last_index = (g_cli.history_count - 1) % CLI_HISTORY_SIZE;
        if(strcmp(g_cli.history[last_index], line) == 0) {
            return;
        }
    }
    
    // 添加到历史记录
    uint8_t index = g_cli.history_count % CLI_HISTORY_SIZE;
    strncpy(g_cli.history[index], line, CLI_MAX_LINE_LENGTH - 1);
    g_cli.history[index][CLI_MAX_LINE_LENGTH - 1] = '\0';
    
    g_cli.history_count++;
    g_cli.history_index = g_cli.history_count;
}

/**
 * @brief 历史记录上一条
 */
static void CLI_HistoryUp(void) {
    if(g_cli.history_count == 0) {
        return;
    }
    
    if(g_cli.history_index > 0) {
        g_cli.history_index--;
        
        // 清除当前行
        CLI_ClearLine();
        
        // 显示历史命令
        uint8_t index = g_cli.history_index % CLI_HISTORY_SIZE;
        strcpy(g_cli.line_buffer, g_cli.history[index]);
        g_cli.line_len = strlen(g_cli.line_buffer);
        g_cli.line_pos = g_cli.line_len;
        
        CLI_Printf("%s", g_cli.line_buffer);
    }
}

/**
 * @brief 历史记录下一条
 */
static void CLI_HistoryDown(void) {
    if(g_cli.history_count == 0) {
        return;
    }
    
    if(g_cli.history_index < g_cli.history_count) {
        g_cli.history_index++;
        
        // 清除当前行
        CLI_ClearLine();
        
        if(g_cli.history_index < g_cli.history_count) {
            // 显示历史命令
            uint8_t index = g_cli.history_index % CLI_HISTORY_SIZE;
            strcpy(g_cli.line_buffer, g_cli.history[index]);
            g_cli.line_len = strlen(g_cli.line_buffer);
            g_cli.line_pos = g_cli.line_len;
            
            CLI_Printf("%s", g_cli.line_buffer);
        } else {
            // 到达最新，清空行
            g_cli.line_len = 0;
            g_cli.line_pos = 0;
        }
    }
}

/**
 * @brief 清除当前行
 */
static void CLI_ClearLine(void) {
    // 移动光标到行首
    CLI_Printf("\r");
    // 显示提示符
    CLI_Printf(CLI_PROMPT);
    // 清除到行尾
    CLI_Printf("\x1B[K");
}
```

### 自动补全功能

```c
/**
 * @brief 自动补全命令
 */
static void CLI_AutoComplete(void) {
    if(g_cli.line_len == 0) {
        return;
    }
    
    // 只补全第一个单词（命令名）
    char *space = strchr(g_cli.line_buffer, ' ');
    if(space != NULL) {
        return;  // 已经有空格，不补全
    }
    
    // 查找匹配的命令
    Command_t *matches[CLI_MAX_COMMANDS];
    uint8_t match_count = 0;
    
    for(uint8_t i = 0; i < g_cli.command_count; i++) {
        if(strncmp(g_cli.commands[i].name, g_cli.line_buffer, g_cli.line_len) == 0) {
            matches[match_count++] = &g_cli.commands[i];
        }
    }
    
    if(match_count == 0) {
        // 没有匹配
        return;
    } else if(match_count == 1) {
        // 唯一匹配，自动补全
        const char *cmd_name = matches[0]->name;
        uint16_t cmd_len = strlen(cmd_name);
        
        // 补全剩余字符
        for(uint16_t i = g_cli.line_len; i < cmd_len; i++) {
            g_cli.line_buffer[i] = cmd_name[i];
            if(g_cli.echo_enabled) {
                CLI_Printf("%c", cmd_name[i]);
            }
        }
        
        // 添加空格
        g_cli.line_buffer[cmd_len] = ' ';
        if(g_cli.echo_enabled) {
            CLI_Printf(" ");
        }
        
        g_cli.line_len = cmd_len + 1;
        g_cli.line_pos = g_cli.line_len;
    } else {
        // 多个匹配，显示所有可能
        CLI_Printf("\r\n");
        for(uint8_t i = 0; i < match_count; i++) {
            CLI_Printf("  %s\r\n", matches[i]->name);
        }
        
        // 找到公共前缀
        uint16_t common_len = g_cli.line_len;
        bool done = false;
        
        while(!done) {
            char ch = matches[0]->name[common_len];
            if(ch == '\0') {
                break;
            }
            
            for(uint8_t i = 1; i < match_count; i++) {
                if(matches[i]->name[common_len] != ch) {
                    done = true;
                    break;
                }
            }
            
            if(!done) {
                common_len++;
            }
        }
        
        // 补全公共前缀
        if(common_len > g_cli.line_len) {
            for(uint16_t i = g_cli.line_len; i < common_len; i++) {
                g_cli.line_buffer[i] = matches[0]->name[i];
            }
            g_cli.line_len = common_len;
            g_cli.line_pos = g_cli.line_len;
        }
        
        // 重新显示提示符和当前输入
        CLI_Printf(CLI_PROMPT);
        g_cli.line_buffer[g_cli.line_len] = '\0';
        CLI_Printf("%s", g_cli.line_buffer);
    }
}
```

### 输出函数

```c
/**
 * @brief CLI格式化输出
 * @param format 格式字符串
 * @param ... 可变参数
 */
void CLI_Printf(const char *format, ...) {
    char buffer[256];
    va_list args;
    
    va_start(args, format);
    int len = vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    if(len > 0) {
        // 通过UART发送
        UART_SendString(buffer);
    }
}

/**
 * @brief 发送字符串到CLI
 * @param str 字符串
 */
void CLI_Print(const char *str) {
    UART_SendString(str);
}

/**
 * @brief 发送字符到CLI
 * @param ch 字符
 */
void CLI_PutChar(char ch) {
    UART_SendByte(ch);
}
```

## 内置命令实现

### help命令

```c
/**
 * @brief help命令处理函数
 * @param argc 参数数量
 * @param argv 参数数组
 * @return 0: 成功
 */
static int CMD_Help(int argc, char *argv[]) {
    if(argc == 1) {
        // 显示所有命令
        CLI_Printf("\r\n可用命令:\r\n");
        CLI_Printf("----------------------------------------\r\n");
        
        for(uint8_t i = 0; i < g_cli.command_count; i++) {
            CLI_Printf("  %-12s - %s\r\n",
                      g_cli.commands[i].name,
                      g_cli.commands[i].help);
        }
        
        CLI_Printf("----------------------------------------\r\n");
        CLI_Printf("提示: 使用 Tab 键自动补全命令\r\n");
        CLI_Printf("      使用 ↑↓ 键浏览历史命令\r\n");
    } else {
        // 显示特定命令的帮助
        Command_t *cmd = CLI_FindCommand(argv[1]);
        if(cmd != NULL) {
            CLI_Printf("\r\n命令: %s\r\n", cmd->name);
            CLI_Printf("说明: %s\r\n", cmd->help);
            CLI_Printf("参数: %d - %d\r\n", cmd->min_args, cmd->max_args);
        } else {
            CLI_Printf("错误: 未找到命令 '%s'\r\n", argv[1]);
        }
    }
    
    return 0;
}
```

### clear命令

```c
/**
 * @brief clear命令处理函数
 * @param argc 参数数量
 * @param argv 参数数组
 * @return 0: 成功
 */
static int CMD_Clear(int argc, char *argv[]) {
    // 发送ANSI清屏序列
    CLI_Printf("\x1B[2J");    // 清屏
    CLI_Printf("\x1B[H");     // 光标移到左上角
    return 0;
}
```

### history命令

```c
/**
 * @brief history命令处理函数
 * @param argc 参数数量
 * @param argv 参数数组
 * @return 0: 成功
 */
static int CMD_History(int argc, char *argv[]) {
    CLI_Printf("\r\n历史命令:\r\n");
    
    if(g_cli.history_count == 0) {
        CLI_Printf("  (空)\r\n");
        return 0;
    }
    
    uint8_t start = 0;
    uint8_t count = g_cli.history_count;
    
    if(count > CLI_HISTORY_SIZE) {
        start = count - CLI_HISTORY_SIZE;
        count = CLI_HISTORY_SIZE;
    }
    
    for(uint8_t i = 0; i < count; i++) {
        uint8_t index = (start + i) % CLI_HISTORY_SIZE;
        CLI_Printf("  %3d  %s\r\n", start + i + 1, g_cli.history[index]);
    }
    
    return 0;
}
```

### echo命令

```c
/**
 * @brief echo命令处理函数
 * @param argc 参数数量
 * @param argv 参数数组
 * @return 0: 成功
 */
static int CMD_Echo(int argc, char *argv[]) {
    if(argc == 1) {
        // 显示当前状态
        CLI_Printf("回显: %s\r\n", g_cli.echo_enabled ? "开启" : "关闭");
    } else {
        // 设置回显状态
        if(strcmp(argv[1], "on") == 0) {
            g_cli.echo_enabled = true;
            CLI_Printf("回显已开启\r\n");
        } else if(strcmp(argv[1], "off") == 0) {
            g_cli.echo_enabled = false;
            CLI_Printf("回显已关闭\r\n");
        } else {
            CLI_Printf("用法: echo [on|off]\r\n");
            return -1;
        }
    }
    return 0;
}
```


## 实践示例

### 示例1：系统信息命令

实现一组系统信息查询命令：

```c
/**
 * @brief version命令 - 显示系统版本
 */
static int CMD_Version(int argc, char *argv[]) {
    CLI_Printf("\r\n");
    CLI_Printf("系统版本信息:\r\n");
    CLI_Printf("  固件版本: v%d.%d.%d\r\n", FW_MAJOR, FW_MINOR, FW_PATCH);
    CLI_Printf("  编译日期: %s %s\r\n", __DATE__, __TIME__);
    CLI_Printf("  MCU型号: %s\r\n", MCU_MODEL);
    CLI_Printf("  时钟频率: %lu MHz\r\n", SystemCoreClock / 1000000);
    return 0;
}

/**
 * @brief status命令 - 显示系统状态
 */
static int CMD_Status(int argc, char *argv[]) {
    CLI_Printf("\r\n");
    CLI_Printf("系统状态:\r\n");
    CLI_Printf("  运行时间: %lu 秒\r\n", GetSystemTick() / 1000);
    CLI_Printf("  CPU使用率: %d%%\r\n", GetCPUUsage());
    CLI_Printf("  内存使用: %lu / %lu 字节\r\n", GetUsedMemory(), GetTotalMemory());
    CLI_Printf("  任务数量: %d\r\n", GetTaskCount());
    return 0;
}

/**
 * @brief reset命令 - 系统复位
 */
static int CMD_Reset(int argc, char *argv[]) {
    CLI_Printf("系统将在3秒后复位...\r\n");
    
    for(int i = 3; i > 0; i--) {
        CLI_Printf("%d...\r\n", i);
        Delay_Ms(1000);
    }
    
    CLI_Printf("复位中...\r\n");
    NVIC_SystemReset();
    
    return 0;
}

// 注册系统命令
void RegisterSystemCommands(void) {
    CLI_RegisterCommand("version", "显示系统版本", CMD_Version, 0, 0);
    CLI_RegisterCommand("status", "显示系统状态", CMD_Status, 0, 0);
    CLI_RegisterCommand("reset", "系统复位", CMD_Reset, 0, 0);
}
```

### 示例2：GPIO控制命令

实现GPIO读写控制命令：

```c
/**
 * @brief gpio命令 - GPIO控制
 * 用法: gpio read <port> <pin>
 *       gpio write <port> <pin> <value>
 *       gpio mode <port> <pin> <mode>
 */
static int CMD_GPIO(int argc, char *argv[]) {
    if(argc < 2) {
        CLI_Printf("用法:\r\n");
        CLI_Printf("  gpio read <port> <pin>\r\n");
        CLI_Printf("  gpio write <port> <pin> <value>\r\n");
        CLI_Printf("  gpio mode <port> <pin> <mode>\r\n");
        CLI_Printf("参数:\r\n");
        CLI_Printf("  port: A-E\r\n");
        CLI_Printf("  pin: 0-15\r\n");
        CLI_Printf("  value: 0/1\r\n");
        CLI_Printf("  mode: in/out/af/analog\r\n");
        return -1;
    }
    
    const char *action = argv[1];
    
    if(strcmp(action, "read") == 0) {
        if(argc != 4) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        char port = argv[2][0];
        int pin = atoi(argv[3]);
        
        if(pin < 0 || pin > 15) {
            CLI_Printf("错误: 引脚号无效 (0-15)\r\n");
            return -1;
        }
        
        int value = GPIO_ReadPin(port, pin);
        CLI_Printf("GPIO%c%d = %d\r\n", port, pin, value);
        
    } else if(strcmp(action, "write") == 0) {
        if(argc != 5) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        char port = argv[2][0];
        int pin = atoi(argv[3]);
        int value = atoi(argv[4]);
        
        if(pin < 0 || pin > 15) {
            CLI_Printf("错误: 引脚号无效 (0-15)\r\n");
            return -1;
        }
        
        if(value != 0 && value != 1) {
            CLI_Printf("错误: 值必须是 0 或 1\r\n");
            return -1;
        }
        
        GPIO_WritePin(port, pin, value);
        CLI_Printf("GPIO%c%d 设置为 %d\r\n", port, pin, value);
        
    } else if(strcmp(action, "mode") == 0) {
        if(argc != 5) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        char port = argv[2][0];
        int pin = atoi(argv[3]);
        const char *mode = argv[4];
        
        if(pin < 0 || pin > 15) {
            CLI_Printf("错误: 引脚号无效 (0-15)\r\n");
            return -1;
        }
        
        if(strcmp(mode, "in") == 0) {
            GPIO_SetMode(port, pin, GPIO_MODE_INPUT);
            CLI_Printf("GPIO%c%d 设置为输入模式\r\n", port, pin);
        } else if(strcmp(mode, "out") == 0) {
            GPIO_SetMode(port, pin, GPIO_MODE_OUTPUT);
            CLI_Printf("GPIO%c%d 设置为输出模式\r\n", port, pin);
        } else if(strcmp(mode, "af") == 0) {
            GPIO_SetMode(port, pin, GPIO_MODE_AF);
            CLI_Printf("GPIO%c%d 设置为复用模式\r\n", port, pin);
        } else if(strcmp(mode, "analog") == 0) {
            GPIO_SetMode(port, pin, GPIO_MODE_ANALOG);
            CLI_Printf("GPIO%c%d 设置为模拟模式\r\n", port, pin);
        } else {
            CLI_Printf("错误: 未知模式 '%s'\r\n", mode);
            return -1;
        }
    } else {
        CLI_Printf("错误: 未知操作 '%s'\r\n", action);
        return -1;
    }
    
    return 0;
}

// 注册GPIO命令
void RegisterGPIOCommands(void) {
    CLI_RegisterCommand("gpio", "GPIO控制", CMD_GPIO, 1, 4);
}
```

### 示例3：内存操作命令

实现内存读写和转储命令：

```c
/**
 * @brief mem命令 - 内存操作
 * 用法: mem read <address> [count]
 *       mem write <address> <value>
 *       mem dump <address> <length>
 */
static int CMD_Memory(int argc, char *argv[]) {
    if(argc < 2) {
        CLI_Printf("用法:\r\n");
        CLI_Printf("  mem read <address> [count]\r\n");
        CLI_Printf("  mem write <address> <value>\r\n");
        CLI_Printf("  mem dump <address> <length>\r\n");
        return -1;
    }
    
    const char *action = argv[1];
    
    if(strcmp(action, "read") == 0) {
        if(argc < 3) {
            CLI_Printf("错误: 缺少地址参数\r\n");
            return -1;
        }
        
        uint32_t address = strtoul(argv[2], NULL, 0);
        int count = (argc >= 4) ? atoi(argv[3]) : 1;
        
        CLI_Printf("读取地址 0x%08lX:\r\n", address);
        
        for(int i = 0; i < count; i++) {
            uint32_t value = *(volatile uint32_t *)(address + i * 4);
            CLI_Printf("  [0x%08lX] = 0x%08lX\r\n", address + i * 4, value);
        }
        
    } else if(strcmp(action, "write") == 0) {
        if(argc != 4) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        uint32_t address = strtoul(argv[2], NULL, 0);
        uint32_t value = strtoul(argv[3], NULL, 0);
        
        *(volatile uint32_t *)address = value;
        CLI_Printf("写入 0x%08lX 到地址 0x%08lX\r\n", value, address);
        
    } else if(strcmp(action, "dump") == 0) {
        if(argc != 4) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        uint32_t address = strtoul(argv[2], NULL, 0);
        uint32_t length = strtoul(argv[3], NULL, 0);
        
        CLI_Printf("内存转储 0x%08lX - 0x%08lX:\r\n", address, address + length - 1);
        
        uint8_t *ptr = (uint8_t *)address;
        for(uint32_t i = 0; i < length; i += 16) {
            // 显示地址
            CLI_Printf("%08lX: ", address + i);
            
            // 显示十六进制
            for(uint32_t j = 0; j < 16 && (i + j) < length; j++) {
                CLI_Printf("%02X ", ptr[i + j]);
            }
            
            // 填充空格
            for(uint32_t j = length - i; j < 16; j++) {
                CLI_Printf("   ");
            }
            
            // 显示ASCII
            CLI_Printf(" |");
            for(uint32_t j = 0; j < 16 && (i + j) < length; j++) {
                char ch = ptr[i + j];
                CLI_Printf("%c", (ch >= 0x20 && ch <= 0x7E) ? ch : '.');
            }
            CLI_Printf("|\r\n");
        }
    } else {
        CLI_Printf("错误: 未知操作 '%s'\r\n", action);
        return -1;
    }
    
    return 0;
}

// 注册内存命令
void RegisterMemoryCommands(void) {
    CLI_RegisterCommand("mem", "内存操作", CMD_Memory, 1, 3);
}
```

### 示例4：配置管理命令

实现系统配置的读取和设置：

```c
// 配置项结构
typedef struct {
    const char *name;
    void *value;
    enum {CONFIG_TYPE_INT, CONFIG_TYPE_FLOAT, CONFIG_TYPE_STRING} type;
    const char *description;
} ConfigItem_t;

// 配置表
static int g_config_baudrate = 115200;
static float g_config_threshold = 3.3f;
static char g_config_device_name[32] = "Device-001";

static ConfigItem_t g_config_items[] = {
    {"baudrate", &g_config_baudrate, CONFIG_TYPE_INT, "串口波特率"},
    {"threshold", &g_config_threshold, CONFIG_TYPE_FLOAT, "阈值电压"},
    {"device_name", g_config_device_name, CONFIG_TYPE_STRING, "设备名称"},
};

#define CONFIG_ITEM_COUNT (sizeof(g_config_items) / sizeof(ConfigItem_t))

/**
 * @brief config命令 - 配置管理
 * 用法: config list
 *       config get <name>
 *       config set <name> <value>
 */
static int CMD_Config(int argc, char *argv[]) {
    if(argc < 2) {
        CLI_Printf("用法:\r\n");
        CLI_Printf("  config list\r\n");
        CLI_Printf("  config get <name>\r\n");
        CLI_Printf("  config set <name> <value>\r\n");
        return -1;
    }
    
    const char *action = argv[1];
    
    if(strcmp(action, "list") == 0) {
        CLI_Printf("\r\n配置项列表:\r\n");
        CLI_Printf("----------------------------------------\r\n");
        
        for(uint8_t i = 0; i < CONFIG_ITEM_COUNT; i++) {
            ConfigItem_t *item = &g_config_items[i];
            CLI_Printf("  %-15s : ", item->name);
            
            switch(item->type) {
                case CONFIG_TYPE_INT:
                    CLI_Printf("%d", *(int *)item->value);
                    break;
                case CONFIG_TYPE_FLOAT:
                    CLI_Printf("%.2f", *(float *)item->value);
                    break;
                case CONFIG_TYPE_STRING:
                    CLI_Printf("%s", (char *)item->value);
                    break;
            }
            
            CLI_Printf(" (%s)\r\n", item->description);
        }
        
    } else if(strcmp(action, "get") == 0) {
        if(argc != 3) {
            CLI_Printf("错误: 缺少配置项名称\r\n");
            return -1;
        }
        
        const char *name = argv[2];
        ConfigItem_t *item = NULL;
        
        for(uint8_t i = 0; i < CONFIG_ITEM_COUNT; i++) {
            if(strcmp(g_config_items[i].name, name) == 0) {
                item = &g_config_items[i];
                break;
            }
        }
        
        if(item == NULL) {
            CLI_Printf("错误: 未找到配置项 '%s'\r\n", name);
            return -1;
        }
        
        CLI_Printf("%s = ", item->name);
        switch(item->type) {
            case CONFIG_TYPE_INT:
                CLI_Printf("%d\r\n", *(int *)item->value);
                break;
            case CONFIG_TYPE_FLOAT:
                CLI_Printf("%.2f\r\n", *(float *)item->value);
                break;
            case CONFIG_TYPE_STRING:
                CLI_Printf("%s\r\n", (char *)item->value);
                break;
        }
        
    } else if(strcmp(action, "set") == 0) {
        if(argc != 4) {
            CLI_Printf("错误: 参数数量不正确\r\n");
            return -1;
        }
        
        const char *name = argv[2];
        const char *value_str = argv[3];
        ConfigItem_t *item = NULL;
        
        for(uint8_t i = 0; i < CONFIG_ITEM_COUNT; i++) {
            if(strcmp(g_config_items[i].name, name) == 0) {
                item = &g_config_items[i];
                break;
            }
        }
        
        if(item == NULL) {
            CLI_Printf("错误: 未找到配置项 '%s'\r\n", name);
            return -1;
        }
        
        switch(item->type) {
            case CONFIG_TYPE_INT:
                *(int *)item->value = atoi(value_str);
                CLI_Printf("%s 设置为 %d\r\n", item->name, *(int *)item->value);
                break;
            case CONFIG_TYPE_FLOAT:
                *(float *)item->value = atof(value_str);
                CLI_Printf("%s 设置为 %.2f\r\n", item->name, *(float *)item->value);
                break;
            case CONFIG_TYPE_STRING:
                strncpy((char *)item->value, value_str, 31);
                ((char *)item->value)[31] = '\0';
                CLI_Printf("%s 设置为 %s\r\n", item->name, (char *)item->value);
                break;
        }
        
        // 保存配置到Flash
        SaveConfigToFlash();
        
    } else {
        CLI_Printf("错误: 未知操作 '%s'\r\n", action);
        return -1;
    }
    
    return 0;
}

// 注册配置命令
void RegisterConfigCommands(void) {
    CLI_RegisterCommand("config", "配置管理", CMD_Config, 1, 3);
}
```


## 主程序集成

### 完整示例

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// UART接收中断处理
void UART_IRQHandler(void) {
    if(UART_GetFlag(UART_FLAG_RXNE)) {
        char ch = UART_ReceiveByte();
        CLI_ProcessChar(ch);
    }
}

// 主函数
int main(void) {
    // 系统初始化
    SystemInit();
    UART_Init(115200);
    
    // 初始化CLI
    CLI_Init();
    
    // 注册应用命令
    RegisterSystemCommands();
    RegisterGPIOCommands();
    RegisterMemoryCommands();
    RegisterConfigCommands();
    
    // 使能UART接收中断
    UART_EnableIRQ();
    
    // 主循环
    while(1) {
        // 其他任务处理
        ProcessBackgroundTasks();
        
        // 可选：轮询方式处理CLI输入
        // if(UART_DataAvailable()) {
        //     char ch = UART_ReceiveByte();
        //     CLI_ProcessChar(ch);
        // }
    }
    
    return 0;
}
```

### 与事件驱动结合

```c
// 事件类型
typedef enum {
    EVENT_CLI_CHAR_RECEIVED,
    EVENT_CLI_COMMAND_COMPLETE,
    // 其他事件...
} EventType_t;

// UART中断中发布事件
void UART_IRQHandler(void) {
    if(UART_GetFlag(UART_FLAG_RXNE)) {
        char ch = UART_ReceiveByte();
        Event_Post(EVENT_CLI_CHAR_RECEIVED, &ch, sizeof(char));
    }
}

// CLI字符事件处理器
void OnCLICharReceived(Event_t *event) {
    char ch = *(char *)event->data;
    CLI_ProcessChar(ch);
}

// 主函数
int main(void) {
    SystemInit();
    UART_Init(115200);
    EventQueue_Init();
    CLI_Init();
    
    // 注册事件处理器
    Event_RegisterHandler(EVENT_CLI_CHAR_RECEIVED, OnCLICharReceived);
    
    // 注册命令
    RegisterSystemCommands();
    RegisterGPIOCommands();
    
    UART_EnableIRQ();
    
    // 事件循环
    while(1) {
        Event_t event;
        if(Event_Get(&event)) {
            Event_Dispatch(&event);
        }
    }
    
    return 0;
}
```

## 深入理解

### 高级特性

#### 1. 命令别名

```c
// 命令别名表
typedef struct {
    const char *alias;
    const char *command;
} CommandAlias_t;

static CommandAlias_t g_aliases[] = {
    {"?", "help"},
    {"ls", "list"},
    {"cls", "clear"},
    {"q", "quit"},
};

#define ALIAS_COUNT (sizeof(g_aliases) / sizeof(CommandAlias_t))

/**
 * @brief 解析命令别名
 * @param name 命令名或别名
 * @return 实际命令名
 */
static const char* CLI_ResolveAlias(const char *name) {
    for(uint8_t i = 0; i < ALIAS_COUNT; i++) {
        if(strcmp(g_aliases[i].alias, name) == 0) {
            return g_aliases[i].command;
        }
    }
    return name;
}
```

#### 2. 命令管道

```c
/**
 * @brief 处理命令管道
 * @param line 命令行（可能包含 | 符号）
 */
static void CLI_ProcessPipeline(char *line) {
    char *commands[8];
    int cmd_count = 0;
    
    // 分割管道命令
    char *token = strtok(line, "|");
    while(token != NULL && cmd_count < 8) {
        commands[cmd_count++] = token;
        token = strtok(NULL, "|");
    }
    
    // 执行管道
    for(int i = 0; i < cmd_count; i++) {
        // 重定向输出到缓冲区（如果不是最后一个命令）
        if(i < cmd_count - 1) {
            CLI_RedirectOutput(true);
        }
        
        CLI_ProcessLine(commands[i]);
        
        if(i < cmd_count - 1) {
            // 将输出作为下一个命令的输入
            CLI_RedirectOutput(false);
        }
    }
}
```

#### 3. 输出重定向

```c
// 输出缓冲区
static char g_output_buffer[1024];
static uint16_t g_output_pos = 0;
static bool g_output_redirected = false;

/**
 * @brief 重定向输出
 * @param enable true: 重定向到缓冲区, false: 恢复正常输出
 */
void CLI_RedirectOutput(bool enable) {
    g_output_redirected = enable;
    if(enable) {
        g_output_pos = 0;
        memset(g_output_buffer, 0, sizeof(g_output_buffer));
    }
}

/**
 * @brief 修改后的输出函数
 */
void CLI_Printf(const char *format, ...) {
    char buffer[256];
    va_list args;
    
    va_start(args, format);
    int len = vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    if(g_output_redirected) {
        // 输出到缓冲区
        if(g_output_pos + len < sizeof(g_output_buffer)) {
            memcpy(&g_output_buffer[g_output_pos], buffer, len);
            g_output_pos += len;
        }
    } else {
        // 正常输出
        UART_SendString(buffer);
    }
}

/**
 * @brief 获取重定向的输出
 * @return 输出字符串
 */
const char* CLI_GetRedirectedOutput(void) {
    return g_output_buffer;
}
```

#### 4. 脚本执行

```c
/**
 * @brief 执行脚本文件
 * @param filename 脚本文件名
 * @return 0: 成功, -1: 失败
 */
int CLI_ExecuteScript(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if(fp == NULL) {
        CLI_Printf("错误: 无法打开文件 '%s'\r\n", filename);
        return -1;
    }
    
    char line[CLI_MAX_LINE_LENGTH];
    int line_num = 0;
    
    while(fgets(line, sizeof(line), fp) != NULL) {
        line_num++;
        
        // 移除换行符
        line[strcspn(line, "\r\n")] = '\0';
        
        // 跳过空行和注释
        if(line[0] == '\0' || line[0] == '#') {
            continue;
        }
        
        CLI_Printf("[%d] %s\r\n", line_num, line);
        CLI_ProcessLine(line);
    }
    
    fclose(fp);
    return 0;
}

/**
 * @brief script命令 - 执行脚本
 */
static int CMD_Script(int argc, char *argv[]) {
    if(argc != 2) {
        CLI_Printf("用法: script <filename>\r\n");
        return -1;
    }
    
    return CLI_ExecuteScript(argv[1]);
}
```

### 性能优化

#### 1. 命令查找优化

使用哈希表加速命令查找：

```c
#define HASH_TABLE_SIZE 32

// 哈希表节点
typedef struct HashNode {
    Command_t *command;
    struct HashNode *next;
} HashNode_t;

static HashNode_t *g_hash_table[HASH_TABLE_SIZE];

/**
 * @brief 简单哈希函数
 */
static uint32_t CLI_Hash(const char *str) {
    uint32_t hash = 5381;
    int c;
    
    while((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    
    return hash % HASH_TABLE_SIZE;
}

/**
 * @brief 添加命令到哈希表
 */
static void CLI_HashInsert(Command_t *cmd) {
    uint32_t index = CLI_Hash(cmd->name);
    
    HashNode_t *node = (HashNode_t *)malloc(sizeof(HashNode_t));
    node->command = cmd;
    node->next = g_hash_table[index];
    g_hash_table[index] = node;
}

/**
 * @brief 从哈希表查找命令
 */
static Command_t* CLI_HashFind(const char *name) {
    uint32_t index = CLI_Hash(name);
    HashNode_t *node = g_hash_table[index];
    
    while(node != NULL) {
        if(strcmp(node->command->name, name) == 0) {
            return node->command;
        }
        node = node->next;
    }
    
    return NULL;
}
```

#### 2. 输入缓冲优化

使用DMA接收减少中断开销：

```c
#define RX_BUFFER_SIZE 256

static uint8_t g_rx_buffer[RX_BUFFER_SIZE];
static volatile uint16_t g_rx_head = 0;
static volatile uint16_t g_rx_tail = 0;

/**
 * @brief 初始化DMA接收
 */
void CLI_InitDMA(void) {
    // 配置DMA循环接收
    DMA_Config(UART_RX_DMA, g_rx_buffer, RX_BUFFER_SIZE, DMA_MODE_CIRCULAR);
    DMA_Start(UART_RX_DMA);
}

/**
 * @brief 处理DMA接收的数据
 */
void CLI_ProcessDMA(void) {
    // 获取DMA当前位置
    uint16_t dma_pos = RX_BUFFER_SIZE - DMA_GetCounter(UART_RX_DMA);
    
    // 处理新接收的数据
    while(g_rx_tail != dma_pos) {
        char ch = g_rx_buffer[g_rx_tail];
        g_rx_tail = (g_rx_tail + 1) % RX_BUFFER_SIZE;
        
        CLI_ProcessChar(ch);
    }
}
```

### 安全性考虑

#### 1. 命令权限控制

```c
// 权限级别
typedef enum {
    PERMISSION_USER = 0,
    PERMISSION_ADMIN = 1,
    PERMISSION_ROOT = 2
} Permission_t;

// 扩展命令结构
typedef struct {
    const char *name;
    const char *help;
    CommandHandler_t handler;
    uint8_t min_args;
    uint8_t max_args;
    Permission_t required_permission;  // 所需权限
} SecureCommand_t;

// 当前用户权限
static Permission_t g_current_permission = PERMISSION_USER;

/**
 * @brief 检查命令权限
 */
static bool CLI_CheckPermission(SecureCommand_t *cmd) {
    if(g_current_permission < cmd->required_permission) {
        CLI_Printf("错误: 权限不足，需要 %s 权限\r\n",
                  cmd->required_permission == PERMISSION_ADMIN ? "管理员" : "超级用户");
        return false;
    }
    return true;
}

/**
 * @brief login命令 - 用户登录
 */
static int CMD_Login(int argc, char *argv[]) {
    if(argc != 3) {
        CLI_Printf("用法: login <username> <password>\r\n");
        return -1;
    }
    
    const char *username = argv[1];
    const char *password = argv[2];
    
    // 验证用户名和密码
    if(strcmp(username, "admin") == 0 && strcmp(password, "admin123") == 0) {
        g_current_permission = PERMISSION_ADMIN;
        CLI_Printf("登录成功，权限: 管理员\r\n");
    } else if(strcmp(username, "root") == 0 && strcmp(password, "root123") == 0) {
        g_current_permission = PERMISSION_ROOT;
        CLI_Printf("登录成功，权限: 超级用户\r\n");
    } else {
        CLI_Printf("登录失败: 用户名或密码错误\r\n");
        return -1;
    }
    
    return 0;
}
```

#### 2. 输入验证

```c
/**
 * @brief 验证参数是否为有效数字
 */
static bool CLI_IsValidNumber(const char *str) {
    if(*str == '\0') return false;
    
    if(*str == '-' || *str == '+') str++;
    
    while(*str) {
        if(*str < '0' || *str > '9') {
            return false;
        }
        str++;
    }
    
    return true;
}

/**
 * @brief 验证参数范围
 */
static bool CLI_ValidateRange(int value, int min, int max) {
    if(value < min || value > max) {
        CLI_Printf("错误: 值超出范围 [%d, %d]\r\n", min, max);
        return false;
    }
    return true;
}

/**
 * @brief 安全的字符串复制
 */
static void CLI_SafeStrCopy(char *dest, const char *src, size_t dest_size) {
    strncpy(dest, src, dest_size - 1);
    dest[dest_size - 1] = '\0';
}
```


## 常见问题

### Q1: CLI和Shell有什么区别？

**A**: CLI和Shell是相关但不同的概念：

**CLI（Command Line Interface）**：
- 命令行接口，是一种交互方式
- 提供命令输入和输出的基础功能
- 通常是嵌入式系统中的简化实现
- 功能相对简单（命令解析、执行）

**Shell**：
- 是一个完整的命令解释器
- 包含CLI的所有功能
- 额外提供：变量、脚本、管道、重定向、作业控制等
- 功能强大但资源占用大

**嵌入式系统中的选择**：
- 资源受限：使用简单CLI
- 资源充足：可以实现完整Shell
- 折中方案：CLI + 部分Shell特性（如脚本执行）

### Q2: 如何处理长命令输入？

**A**: 有几种方法处理超长命令：

**方法1：限制输入长度**
```c
void CLI_ProcessChar(char ch) {
    if(g_cli.line_len >= CLI_MAX_LINE_LENGTH - 1) {
        // 缓冲区已满，忽略新字符
        CLI_Printf("\a");  // 发出蜂鸣
        return;
    }
    // 正常处理
}
```

**方法2：动态缓冲区**
```c
typedef struct {
    char *buffer;
    uint16_t capacity;
    uint16_t length;
} DynamicBuffer_t;

void CLI_ExpandBuffer(DynamicBuffer_t *buf) {
    if(buf->length >= buf->capacity - 1) {
        buf->capacity *= 2;
        buf->buffer = realloc(buf->buffer, buf->capacity);
    }
}
```

**方法3：多行输入**
```c
// 支持 \ 续行符
void CLI_ProcessLine(char *line) {
    static char multi_line[512];
    static uint16_t multi_pos = 0;
    
    uint16_t len = strlen(line);
    
    // 检查续行符
    if(len > 0 && line[len - 1] == '\\') {
        // 移除续行符
        line[len - 1] = '\0';
        // 追加到多行缓冲区
        strcpy(&multi_line[multi_pos], line);
        multi_pos += len - 1;
        CLI_Printf("> ");  // 显示续行提示符
        return;
    }
    
    // 完整命令
    if(multi_pos > 0) {
        strcpy(&multi_line[multi_pos], line);
        CLI_ExecuteCommand(multi_line);
        multi_pos = 0;
    } else {
        CLI_ExecuteCommand(line);
    }
}
```

### Q3: 如何实现命令的异步执行？

**A**: 对于耗时命令，可以使用异步执行：

```c
// 异步命令状态
typedef struct {
    bool running;
    CommandHandler_t handler;
    int argc;
    char *argv[CLI_MAX_ARGS];
    uint32_t start_time;
} AsyncCommand_t;

static AsyncCommand_t g_async_cmd = {0};

/**
 * @brief 启动异步命令
 */
void CLI_StartAsyncCommand(CommandHandler_t handler, int argc, char *argv[]) {
    g_async_cmd.running = true;
    g_async_cmd.handler = handler;
    g_async_cmd.argc = argc;
    
    // 复制参数
    for(int i = 0; i < argc; i++) {
        g_async_cmd.argv[i] = strdup(argv[i]);
    }
    
    g_async_cmd.start_time = GetSystemTick();
    
    CLI_Printf("命令在后台执行中...\r\n");
    CLI_Printf(CLI_PROMPT);
}

/**
 * @brief 处理异步命令（在主循环中调用）
 */
void CLI_ProcessAsyncCommand(void) {
    if(!g_async_cmd.running) {
        return;
    }
    
    // 执行命令的一小部分工作
    int result = g_async_cmd.handler(g_async_cmd.argc, g_async_cmd.argv);
    
    if(result == 0) {
        // 命令完成
        CLI_Printf("\r\n命令执行完成\r\n");
        CLI_Printf(CLI_PROMPT);
        
        // 释放参数
        for(int i = 0; i < g_async_cmd.argc; i++) {
            free(g_async_cmd.argv[i]);
        }
        
        g_async_cmd.running = false;
    }
}

/**
 * @brief 耗时命令示例
 */
static int CMD_LongTask(int argc, char *argv[]) {
    static int progress = 0;
    
    if(progress < 100) {
        // 执行一部分工作
        DoSomeWork();
        progress += 10;
        
        CLI_Printf("\r进度: %d%%", progress);
        
        return -1;  // 未完成
    }
    
    progress = 0;
    return 0;  // 完成
}
```

### Q4: 如何调试CLI系统？

**A**: 常用的调试方法：

**1. 日志输出**
```c
#ifdef CLI_DEBUG
#define CLI_DEBUG_PRINT(fmt, ...) printf("[CLI] " fmt, ##__VA_ARGS__)
#else
#define CLI_DEBUG_PRINT(fmt, ...)
#endif

void CLI_ProcessChar(char ch) {
    CLI_DEBUG_PRINT("Received char: 0x%02X ('%c')\r\n", ch, ch);
    // 处理字符
}
```

**2. 命令跟踪**
```c
void CLI_ExecuteCommand(int argc, char *argv[]) {
    CLI_DEBUG_PRINT("Executing command: %s\r\n", argv[0]);
    CLI_DEBUG_PRINT("Arguments: %d\r\n", argc - 1);
    
    for(int i = 1; i < argc; i++) {
        CLI_DEBUG_PRINT("  argv[%d] = '%s'\r\n", i, argv[i]);
    }
    
    // 执行命令
}
```

**3. 状态监控**
```c
/**
 * @brief debug命令 - 显示CLI调试信息
 */
static int CMD_Debug(int argc, char *argv[]) {
    CLI_Printf("\r\nCLI调试信息:\r\n");
    CLI_Printf("  命令数量: %d\r\n", g_cli.command_count);
    CLI_Printf("  历史记录: %d\r\n", g_cli.history_count);
    CLI_Printf("  当前行长度: %d\r\n", g_cli.line_len);
    CLI_Printf("  光标位置: %d\r\n", g_cli.line_pos);
    CLI_Printf("  回显状态: %s\r\n", g_cli.echo_enabled ? "开启" : "关闭");
    
    CLI_Printf("\r\n已注册命令:\r\n");
    for(uint8_t i = 0; i < g_cli.command_count; i++) {
        CLI_Printf("  [%d] %s\r\n", i, g_cli.commands[i].name);
    }
    
    return 0;
}
```

**4. 单元测试**
```c
// 测试命令解析
void Test_CommandParsing(void) {
    char line[] = "gpio write A 5 1";
    char *argv[CLI_MAX_ARGS];
    int argc = 0;
    
    // 解析命令
    CLI_ParseLine(line, &argc, argv);
    
    // 验证结果
    assert(argc == 5);
    assert(strcmp(argv[0], "gpio") == 0);
    assert(strcmp(argv[1], "write") == 0);
    assert(strcmp(argv[2], "A") == 0);
    assert(strcmp(argv[3], "5") == 0);
    assert(strcmp(argv[4], "1") == 0);
    
    printf("命令解析测试通过\r\n");
}
```

## 总结

命令行接口（CLI）是嵌入式系统中重要的调试和配置工具。通过本教程学习，你应该掌握了：

### 核心知识点

1. **CLI架构设计**
   - 输入处理、命令解析、命令执行、输出显示
   - 模块化设计，易于扩展

2. **命令系统**
   - 命令注册和查找机制
   - 参数解析和验证
   - 命令处理函数设计

3. **交互功能**
   - 字符回显和行编辑
   - 历史记录浏览
   - 自动补全
   - 帮助系统

4. **高级特性**
   - 命令别名
   - 脚本执行
   - 权限控制
   - 异步执行

### 关键要点

- **简洁高效**：CLI应该占用最少的资源
- **用户友好**：提供清晰的提示和帮助信息
- **可扩展性**：易于添加新命令
- **安全性**：输入验证和权限控制
- **调试友好**：提供详细的错误信息

### 适用场景

CLI特别适合：
- 系统调试和测试
- 参数配置和管理
- 生产测试和标定
- 远程运维和监控
- 开发阶段的功能验证

### 实现建议

1. **从简单开始**：先实现基本功能，再逐步添加高级特性
2. **模块化设计**：将命令按功能分组，便于管理
3. **统一风格**：保持命令命名和参数格式的一致性
4. **完善文档**：为每个命令提供清晰的帮助信息
5. **充分测试**：测试各种输入情况，包括异常输入

### 下一步学习

掌握CLI实现后，建议继续学习：

1. **日志系统设计与实现** - 配合CLI使用的调试工具
2. **事件驱动架构设计** - 将CLI集成到事件系统
3. **RTOS基础** - 在多任务环境中使用CLI
4. **网络通信** - 实现远程CLI（Telnet/SSH）

## 延伸阅读

推荐进一步学习的资源：

- [日志系统设计与实现](04-logging-system.html) - 配合CLI的调试工具
- [事件驱动架构设计](02-event-driven-architecture.html) - CLI与事件系统集成
- [裸机程序调试技巧](../beginner/08-bare-metal-debugging.html) - CLI在调试中的应用
- [RTOS基础](../../02-rtos-fundamentals/beginner/01-rtos-overview.html) - 多任务环境中的CLI

## 参考资料

1. "Embedded Systems Programming" - Michael Barr
2. "The Art of Unix Programming" - Eric S. Raymond
3. "Writing Solid Code" - Steve Maguire
4. "Embedded C Coding Standard" - Michael Barr
5. GNU Readline Library Documentation

## 练习题

### 基础练习

1. **简单CLI实现**：实现一个包含5个基本命令的CLI系统
   - help, clear, echo, version, reset
   - 支持命令解析和执行
   - 实现字符回显和退格处理

2. **参数处理**：为CLI添加参数解析功能
   - 支持多个参数
   - 支持引号包围的参数
   - 参数数量验证

3. **帮助系统**：实现完整的帮助系统
   - 显示所有命令列表
   - 显示单个命令的详细帮助
   - 格式化输出

### 进阶练习

4. **历史记录**：实现命令历史功能
   - 使用环形缓冲区存储历史
   - 支持上下箭头浏览
   - 避免重复命令

5. **自动补全**：实现Tab自动补全
   - 单个匹配自动补全
   - 多个匹配显示列表
   - 公共前缀补全

6. **GPIO控制命令**：实现完整的GPIO控制
   - gpio read <port> <pin>
   - gpio write <port> <pin> <value>
   - gpio mode <port> <pin> <mode>
   - 参数验证和错误处理

### 项目练习

7. **系统监控CLI**：
   - 系统信息查询（CPU、内存、温度）
   - 实时数据显示
   - 配置参数管理
   - 日志查看

8. **测试工具CLI**：
   - 硬件模块测试命令
   - 自动化测试脚本
   - 测试结果记录
   - 报告生成

### 挑战练习

9. **完整Shell实现**：
   - 变量支持
   - 条件语句（if/else）
   - 循环语句（for/while）
   - 管道和重定向
   - 脚本执行

10. **网络CLI**：
    - Telnet服务器
    - 多用户支持
    - 权限管理
    - 会话管理

---

**下一步**：建议学习 [日志系统设计与实现](04-logging-system.html)，了解如何构建配合CLI使用的调试工具，或者学习 [裸机程序性能优化](05-bare-metal-optimization.html)，提升系统整体性能。

**反馈**：如果你在学习过程中遇到问题，欢迎在讨论区提问，或者通过邮件联系我们。

**版权声明**：本教程采用 CC BY-NC-SA 4.0 许可协议，欢迎分享和改编，但请注明出处。
