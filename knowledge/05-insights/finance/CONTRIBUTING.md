# 贡献指南

感谢你对金融知识体系的贡献！本文档说明如何参与内容创建、更新和改进。

## 贡献方式

### 1. 修正错误

发现内容错误（数据错误、逻辑错误、链接失效等）时：

1. 定位到具体文件
2. 直接修改错误内容
3. 在文件的 `updated_at` 元数据字段更新日期
4. 在文件末尾的"更新历史"部分记录修改内容

### 2. 补充内容

为现有文章添加新内容时：

1. 确保新内容符合文章的 `skill_level`（难度级别）
2. 遵循文章现有的结构和风格
3. 为新增的引用添加完整的参考文献
4. 更新元数据中的 `updated_at` 字段

### 3. 创建新文章

创建全新的内容文件时，请遵循以下流程：

**步骤 1：确认选题**
- 检查是否已有相关文章（避免重复）
- 确认选题符合知识体系的范围和定位
- 确定文章所属的学习阶段和子目录

**步骤 2：使用标准模板**
- 复制 [article-template.md](../../templates/article-template.html)
- 填写完整的 YAML frontmatter 元数据
- 按照内容结构模板组织文章

**步骤 3：完成内容**
- 确保字数符合难度级别要求
- 包含至少 1 个 Mermaid 可视化图表
- 提供至少 2 个真实案例
- 添加完整的参考文献（10-20 个）

**步骤 4：更新索引**
- 在所属目录的 `index.md` 中添加文章链接
- 在相关文章的 `related_contents` 中添加双向链接

---

## 内容质量标准

### 元数据要求

每个内容文件必须包含完整的 YAML frontmatter：

```yaml
---
title: "文章标题"
description: "简要描述（50-100字）"
slug: "url-friendly-slug"

domain: "金融洞察"
module: "具体模块名"
content_type: "article"
skill_level: "beginner"  # beginner / intermediate / advanced

tags:
  - 金融
  - 具体主题标签

prerequisites: ["前置知识1", "前置知识2"]
related_contents: ["相关文章路径1", "相关文章路径2"]

estimated_time: 45  # 阅读时间（分钟）
difficulty_score: 2  # 难度评分 1-5

author: "作者名"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
version: "1.0"
language: "zh-CN"

status: "published"
is_featured: false
---
```

**必填字段**：`title`, `description`, `domain`, `module`, `content_type`, `skill_level`, `tags`, `estimated_time`, `difficulty_score`, `author`, `created_at`, `updated_at`, `version`, `language`, `status`

### 内容深度要求

| 难度级别 | 字数要求 | 案例数量 | 参考文献 |
|----------|----------|----------|----------|
| beginner | 2000-3000 字 | 1-2 个 | 5-10 个 |
| intermediate | 3000-5000 字 | 3-5 个 | 10-20 个 |
| advanced | 5000-8000+ 字 | 5-10 个 | 20-50 个 |

### 必需内容章节

每篇文章必须包含以下章节：

1. **概述**（200-300 字）：主题介绍、学习目标、重要性说明
2. **核心内容**：理论讲解、框架模型、逻辑关系
3. **实践案例**：至少 2 个真实案例，包含数据支持
4. **可视化**：至少 1 个 Mermaid 图表
5. **实战应用**：如何使用、注意事项、常见错误
6. **延伸学习**：推荐书籍（3-5 本）、相关文章链接
7. **参考文献**：完整引用格式，分类组织

### 可视化规范

使用 Mermaid 图表，根据内容选择合适类型：

- **流程图**（`graph TD`）：流程和决策
- **时序图**（`sequenceDiagram`）：时间序列和因果关系
- **状态图**（`stateDiagram-v2`）：周期和状态转换
- **思维导图**（`mindmap`）：知识结构
- **象限图**（`quadrantChart`）：分类和比较

### 引用格式标准

统一使用 APA 格式：

```
作者姓, 名. (年份). 书名/文章名. 出版社/期刊名. ISBN/URL
```

示例：
```
Graham, B., & Dodd, D. (1934). Security Analysis. McGraw-Hill. ISBN: 978-0071592536
Dalio, R. (2018). A Template for Understanding Big Debt Crises. Bridgewater Associates.
```

---

## 标签词汇表

使用标准化标签，避免创建重复或相似的标签：

### 主题标签
- `value-investing` - 价值投资
- `growth-investing` - 成长投资
- `macro-investing` - 宏观投资
- `quantitative-investing` - 量化投资
- `index-investing` - 指数投资
- `asset-allocation` - 资产配置
- `risk-management` - 风险管理

### 分析方法标签
- `financial-analysis` - 财务分析
- `valuation` - 估值
- `competitive-analysis` - 竞争分析
- `industry-analysis` - 行业分析
- `technical-analysis` - 技术分析
- `fundamental-analysis` - 基本面分析

### 市场标签
- `us-market` - 美国市场
- `china-market` - 中国市场
- `global-markets` - 全球市场
- `emerging-markets` - 新兴市场

### 资产类别标签
- `equities` - 股票
- `fixed-income` - 固定收益
- `commodities` - 大宗商品
- `real-estate` - 房地产
- `derivatives` - 衍生品

### 经济学标签
- `macroeconomics` - 宏观经济学
- `monetary-policy` - 货币政策
- `fiscal-policy` - 财政政策
- `economic-cycles` - 经济周期
- `inflation` - 通货膨胀

---

## 文件命名规范

- 使用 **kebab-case**（小写字母，单词间用连字符）
- 示例：`value-investing.md`，`dcf-valuation.md`，`warren-buffett.md`
- 避免使用下划线、空格或大写字母
- 文件名应简洁且能反映内容主题

---

## 验证工具

提交内容前，建议运行以下验证脚本：

```bash
# 验证元数据完整性
python validate_metadata.py

# 检查内部链接有效性
python check_links.py

# 验证引用格式
python validate_citations.py

# 检查内容结构
python validate_content_structure.py

# 验证字数要求
python validate_word_count.py
```

所有脚本位于 `knowledge/05-insights/finance/` 目录下。

---

*感谢你的贡献，让这个知识体系更加完善！*
