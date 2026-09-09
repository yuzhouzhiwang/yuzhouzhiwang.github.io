# ⏳ 时光 · 个人主页

> 基于 Hexo + Butterfly 的个人博客网站，托管于 **GitHub Pages**，现已全面优化并扩展为「博客 + 数据分析 + 传感器 + 后台管理」的一体化个人知识站。

线上地址：**https://yuzhouzhiwang.github.io/**

---

## 📁 站点结构

```
├── index.html                     # 首页（时光精选板块 + 最新文章）
├── archives/                      # 文章归档（时间轴）
├── tags/                          # 标签
├── categories/                    # 分类
├── about/                         # 关于我
├── link/                          # 友链
├── movies/ books/ games/ music/   # 娱乐板块
├── bangumis/                      # 追番
├── data-analyst/                  # 📊 数据分析师成长路线（独立板块）
│   ├── index.html                 #   板块首页
│   ├── roadmap.html               #   学习路线
│   ├── books.html                 #   书籍推荐
│   ├── software.html              #   软件与安装
│   ├── resources.html             #   资源聚合
│   └── css/style.css              #   板块样式
├── sensor/                        # 📡 传感器知识中心（独立板块）
│   ├── index.html                 #   知识中心
│   ├── pressure-sensor.html       #   压力传感器
│   ├── flow-sensor.html           #   流量传感器
│   ├── fluid-sensor.html          #   流体传感
│   ├── learning-path.html         #   学习路径
│   ├── algorithm.html             #   算法演示（交互式）
│   └── standards.html             #   标准规范
├── jobs/                          # 💼 求职资讯（10个岗位分页 + BOSS直聘 + 招聘季倒计时）
│   ├── index.html                 #   求职总页（金九银十/金三银四精确倒计时）
│   ├── mes.html it-ops.html erp.html dropship.html      # 岗位分页
│   ├── embedded.html electronics.html data-analyst.html # 岗位分页
│   └── no-experience.html customer-service.html archive-scanner.html
├── peripherals.html               # 🔌 嵌入式常用外设速查（聚合页，首页入口）
│   └── peripherals/               #   18个外设详情页：原理/时序图/配置/项目示例/面试自查
├── protocols.html                 # 📡 嵌入式常用协议速查（含对比表，首页入口）
│   └── protocols/                 #   22个协议详情页：原理/时序图/帧结构/示例/面试自查
├── plan/                          # ⏳ 硬件基础打卡计划（日历打卡应用）
│   ├── index.html                 #   日历视图 · 完成打钩 · 不足/备注/复盘 · 金九银十/金三银四 · 八股题库
│   ├── priority.html              #   社招双优先级总览
│   ├── job-priority.html          #   岗位优先级详情（9岗位四梯队）
│   ├── knowledge-priority.html    #   知识优先级详情（P0/P1/P2）
│   └── schedule.html              #   大小周排班说明
├── posts/                         # 🆕 后台发布的新文章（自动生成）
├── admin/                         # 🔐 后台管理系统（发布文章用）
│   └── index.html                 #   写文章 / 管理文章 / 设置
├── css/                           # 站点样式
│   ├── index.css                  #   主站样式（含全站响应式增强）
│   └── article.css                #   后台发布文章的页面样式
├── img/                           # 图片资源（封面、头像、横幅等）
└── libs/                          # 本地化第三方库（国内加速）
```

---

## 🚀 后台发布文章（推荐）

通过 **后台管理系统** 直接在浏览器里写文章并发布，一键推送到 GitHub，GitHub Pages 自动更新线上。

### 访问入口
- 首页页脚「管理」链接，或直接访问 `https://yuzhouzhiwang.github.io/admin/`

### 首次使用
1. 打开后台会先进入 **设置管理员账号** 页面，填写姓名/用户名 + 密码（至少 4 位），点击「设置并进入」。
   > 凭据仅保存在**你自己的浏览器 localStorage**，请妥善保管；再次登录需输入相同姓名与密码。
2. 进入「设置」页，填写 **GitHub Personal Access Token（发布用）**。

### 获取 GitHub Token
1. 打开 https://github.com/settings/personal-access-tokens/new （Fine-grained token）
2. **Repository access** → 选「Only select repositories」→ 勾选 `yuzhouzhiwang.github.io`
3. **Permissions** → **Contents** 设为 `Read and write`，**Metadata** 设为 `Read`
4. 生成后把令牌粘贴到后台「设置」页的令牌框，点「保存设置」→「测试连接」显示成功即可
5. 令牌只存在你的浏览器 localStorage，**不要泄露、不要提交到仓库**

### 发布流程
1. 「写文章」页填写：标题、分类、标签、日期、封面（可选）、摘要（可选）、正文（Markdown）
2. 点「预览」查看渲染效果
3. 点「发布到 GitHub」→ 自动创建文章页，并更新首页「最新文章」、归档、分类、标签页
4. 约 1–3 分钟后 GitHub Pages 构建完成，线上即可访问 `https://yuzhouzhiwang.github.io/posts/文章名/`

### 管理文章
- 「管理文章」页列出所有已发布文章，可「查看」或「删除」
- 删除会同步从首页 / 归档 / 分类 / 标签移除

---

## 🌐 部署到 GitHub Pages

站点为纯静态，直接推送到 GitHub 即可自动部署：

```bash
git add -A
git commit -m "更新内容"
git push origin master
```

> 仓库：`yuzhouzhiwang/yuzhouzhiwang.github.io`，分支：`master`。GitHub Pages 检测到推送后自动构建。

**本地预览：**
```bash
# 在仓库根目录
python -m http.server 8000
# 浏览器打开 http://127.0.0.1:8000/
```

---

## ✨ 已做的优化

- **站名与品牌**：站名「时光」，作者信息、SEO meta、页脚版权统一更新
- **硬件基础打卡计划**：新增 `/plan/` 打卡应用——基于 Excel 计划生成 152 天日历，金九银十（2026.9–11）/ 金三银四（2027.3–4）两阶段切换，任务打钩、今日不足、备注、周日复盘，localStorage 本地持久化，支持导出 JSON 备份
- **国内访问加速**：所有 jsdelivr CDN 静态资源已下载到 `libs/` 本地自托管；图片懒加载、预连接国内服务
- **封面图体系**：失效的第三方图床图片已全部替换为本地分类封面（数据库 / 网页设计 / markdown / 21天 等）
- **旧文章归档**：2023.12 之前的旧文章已从首页 / 归档 / 标签 / 分类隐藏（文件仍在，可直接访问），待新内容通过后台发布
- **嵌入式外设/协议聚合页**：新增 /peripherals.html（GPIO/TIM/ADC/PWM/UART/SPI/I2C/CAN/USB 等外设速查）与 /protocols.html（板内/工业/无线/网络协议 + 对比表），首页速查横条入口
- **40个详情页**：每个外设/协议独立页面——核心原理、SVG时序图（波形/帧结构/流程图）、配置要点、项目示例代码、面试高频问答、可勾选自查清单（localStorage）
- **打卡页八股题库**：新增「📖 八股题库」tab——5 大分组 27 道高频面试题，带要点提示、勾选背诵进度（localStorage）、一键重置
- **全站响应式**：新增全站响应式增强，手机 / 平板 / 电脑全适配，修复横向溢出
- **SEO**：canonical / og 链接指向正式域名，补充站点描述

---

## 📜 说明

- 旧文章为 2022 年的技能抽考笔记，已隐藏归档；新内容建议通过后台发布
- 微信图标当前无跳转，如需扫码可提供二维码图片替换
- 后台登录凭据由站长自行设置，仅存于个人浏览器
