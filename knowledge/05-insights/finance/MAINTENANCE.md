# 维护文档

本文档定义金融知识体系的维护计划、内容审查周期、数据更新流程和故障排除指南。

## 内容审查周期

### 每月审查（Monthly Review）

**目标**：保持内容时效性，修复发现的问题

**检查项目**：
- [ ] 运行链接检查脚本，修复断链
- [ ] 检查最近添加的文件的元数据完整性
- [ ] 更新重大市场事件相关内容（如有）
- [ ] 检查并修复读者反馈的错误

**执行命令**：
```bash
python check_links.py
python validate_metadata.py
```

### 季度审查（Quarterly Review）

**目标**：更新数据，确保内容准确性

**检查项目**：
- [ ] 更新公司财务数据（年报、季报数据）
- [ ] 更新宏观经济数据（GDP、CPI、利率等）
- [ ] 审查投资大师的最新观点和动态
- [ ] 检查行业分析的最新发展
- [ ] 运行完整的内容结构验证
- [ ] 更新参考文献中的失效链接

**执行命令**：
```bash
python validate_content_structure.py
python validate_citations.py
python validate_word_count.py
```

### 年度审查（Annual Review）

**目标**：全面评估知识体系的完整性和质量

**检查项目**：
- [ ] 运行所有 8 个 Property 测试
- [ ] 评估知识覆盖完整性（对照 24 个需求点）
- [ ] 审查学习路径的合理性
- [ ] 添加年度重要事件的案例分析
- [ ] 更新推荐书单和学习资源
- [ ] 评估是否需要新增学习阶段或子模块
- [ ] 生成年度质量报告

**执行命令**：
```bash
python validate_coverage.py
python check_consistency.py
python check_bidirectional_links.py
```

---

## 数据更新流程

### 公司财务数据更新

当公司发布年报或季报时：

1. **定位相关文件**：找到对应的公司研究文件（如 `05-global-perspective/us-market/technology/semiconductors/nvidia.md`）
2. **更新财务数据**：更新收入、利润、现金流等关键指标
3. **更新分析结论**：根据新数据调整投资论点
4. **更新元数据**：修改 `updated_at` 字段
5. **记录更新**：在文件末尾的"更新历史"部分记录变更

**数据来源优先级**：
1. 公司官方年报/季报（最权威）
2. SEC/港交所/上交所官方披露
3. Bloomberg、FactSet 等专业数据库
4. Wind、同花顺等国内数据平台

### 宏观经济数据更新

**关键数据更新频率**：

| 数据类型 | 更新频率 | 主要来源 |
|----------|----------|----------|
| GDP 数据 | 季度 | 国家统计局、美联储 |
| CPI/PPI | 月度 | BLS、国家统计局 |
| 利率数据 | 实时 | 美联储、央行官网 |
| 就业数据 | 月度 | BLS、国家统计局 |
| 贸易数据 | 月度 | 海关总署、商务部 |

### 投资大师内容更新

当投资大师发表重要观点或有重大投资动作时：

1. 在对应的投资大师档案中添加"最新动态"部分
2. 更新投资组合数据（如有公开披露）
3. 添加新的经典语录
4. 更新业绩数据

---

## 故障排除指南

### 问题 1：Mermaid 图表无法渲染

**症状**：图表显示为原始代码而非图形

**解决方案**：
1. 确认使用支持 Mermaid 的渲染器（MkDocs、Obsidian 等）
2. 检查 Mermaid 代码语法是否正确
3. 运行 `python validate_mermaid.py` 检查语法错误
4. 确认 MkDocs 配置中已启用 Mermaid 插件

### 问题 2：内部链接失效（404）

**症状**：点击链接后显示"页面不存在"

**解决方案**：
1. 运行 `python check_links.py` 生成断链报告
2. 检查目标文件是否存在
3. 检查链接路径是否正确（相对路径 vs 绝对路径）
4. 如果文件已移动，更新所有指向该文件的链接
5. 运行 `python fix_broken_links.py` 尝试自动修复

### 问题 3：元数据验证失败

**症状**：`validate_metadata.py` 报告字段缺失或格式错误

**解决方案**：
1. 查看验证报告，确认缺失的字段
2. 参考 [CONTRIBUTING.md](./CONTRIBUTING.html) 中的元数据模板
3. 补充缺失字段，修正格式错误
4. 重新运行验证脚本确认修复

### 问题 4：双向链接不一致

**症状**：`check_bidirectional_links.py` 报告单向链接

**解决方案**：
1. 查看报告，找到缺少反向链接的文件对
2. 在目标文件的 `related_contents` 中添加源文件的链接
3. 运行 `python fix_bidirectional_links.py` 尝试自动修复
4. 重新运行检查脚本确认修复

### 问题 5：字数不足

**症状**：`validate_word_count.py` 报告文件字数低于要求

**解决方案**：
1. 查看报告，确认哪些文件需要扩充
2. 根据文件的 `skill_level` 确定目标字数
3. 扩充内容：增加案例、深化分析、补充数据
4. 运行 `python expand_short_files.py` 获取扩充建议
5. 重新运行字数验证确认达标

### 问题 6：MkDocs 构建失败

**症状**：运行 `mkdocs build` 时报错

**解决方案**：
1. 检查 `mkdocs.yml` 配置文件语法
2. 确认所有在 `nav` 中引用的文件存在
3. 检查 Markdown 文件中是否有语法错误
4. 查看构建日志中的具体错误信息
5. 尝试 `mkdocs build --strict` 获取更详细的错误信息

---

## 版本管理

### 版本号规则

使用语义化版本号（`major.minor.patch`）：

- **major**（主版本）：知识体系重大重构，如新增学习阶段
- **minor**（次版本）：新增重要文章或模块，如新增 20+ 个文件
- **patch**（修订版本）：错误修正、数据更新、小改进

### 当前版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 1.0.0 | 2024-01 | 初始版本，建立完整知识体系框架 |

### 版本更新流程

1. 完成内容变更
2. 更新受影响文件的 `version` 元数据字段
3. 在本文档的"版本历史"表格中记录变更
4. 更新 `README.md` 中的"最后更新"信息

---

## 维护工具清单

所有维护脚本位于 `knowledge/05-insights/finance/` 目录：

| 脚本 | 功能 | 使用频率 |
|------|------|----------|
| `validate_metadata.py` | 验证元数据完整性 | 月度 |
| `check_links.py` | 检查内部链接有效性 | 月度 |
| `fix_broken_links.py` | 自动修复断链 | 按需 |
| `validate_citations.py` | 验证引用格式 | 季度 |
| `validate_content_structure.py` | 检查内容结构 | 季度 |
| `validate_word_count.py` | 验证字数要求 | 季度 |
| `check_bidirectional_links.py` | 检查双向链接 | 季度 |
| `fix_bidirectional_links.py` | 修复双向链接 | 按需 |
| `validate_mermaid.py` | 验证 Mermaid 语法 | 按需 |
| `check_consistency.py` | 检查内容一致性 | 年度 |
| `validate_coverage.py` | 验证知识覆盖完整性 | 年度 |
| `generate_knowledge_map.py` | 生成知识图谱 | 年度 |

---

*维护文档版本：1.0 | 最后更新：2024 年*
