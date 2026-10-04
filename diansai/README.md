# 电赛真题 × 三大电子 公司化筛选

全国大学生电子设计竞赛 1994–2026 历年真题，按 **消费电子 / 工业电子 / 车规电子** 三大行业方向归类筛选的独立站点。

## 目录结构

```
电赛真题三大电子筛选/
├── index.html                  # 站点入口（单文件自包含，直接双击打开）
├── 选型策略_总览.html           # 关联页：芯片选型策略（导航「选型策略」指向）
├── 芯片包替代分析_总览.html      # 关联页：芯片包替代分析（导航「芯片包替代分析」指向）
├── 2016-D_简易电子秤_PRD.html   # 关联页：示例 PRD（PRD_总览 引用 ../2016-D_...）
├── V2.2_芯片包升级交付说明.md    # 芯片包 V2.2 升级交付说明
├── PRD/                        # PRD 文档库（按年份/题号命名，PRD_总览.html 为入口）
│   └── PRD_总览.html
├── PDF_真题/                   # 1994–2007 真题 PDF 资料（含裁切清单）
├── _build/                     # 构建链（模板 + 数据 + 组装脚本）
│   ├── build_page.py           #   组装脚本：_head + 数据 + _tail → 根目录 index.html
│   ├── _head.html              #   页面头部模板
│   ├── _tail.html              #   页面尾部模板
│   ├── topics_data.py          #   真题数据（TOPICS）
│   ├── page_data.py            #   页面数据（推荐/电路/元器件等）
│   └── _nest.py / _center.py   #   历史一次性调试脚本（勿删）
└── _backup/                    # 版本备份（index_日期-vN.html + 历史 PRD 体系快照）
```

## 构建方式

重新生成 `index.html`（数据变更后）：

```bash
cd _build
python build_page.py
```

产物输出到**站点根目录** `index.html`。

## 维护注意

- `index.html` 是单文件自包含产物，**直接双击即可打开**，不依赖网络（图表除外）。
- **警告**：重新运行 `build_page.py` 会用 `_head.html` / `_tail.html` 模板**整体覆盖**根目录 `index.html`。若曾手工优化过 `index.html`（如导航层级、主题色、favicon），请先把当前版本复制进 `_backup/` 再构建。
- 三行业主题色、导航层级等视觉配置在 `index.html` 的 CSS 变量与 `.nav-top / .nav-bottom` 结构中维护。
- 历史 PRD 体系快照（`_backup/PRD体系_*`）保留备份用途，非必要不动。

## 线上部署（GitHub Pages）

- 站点同步部署在个人博客：`https://yuzhouzhiwang.github.io/diansai/`（仓库 `yuzhouzhiwang/yuzhouzhiwang.github.io`）。
- 线上模式自动适配：真题 PDF 走 GitHub Pages 直链（`https://yuzhouzhiwang.github.io/真题/...`），PRD 页面已批量注入适配脚本（标记 `ds-online-fix`，2026-10-04），线上打开即可预览真题 PDF。
- 本地双击 `index.html` 仍走本地路径（`NUEDC_TOPIC-master/`），本地与线上互不干扰。
- 上传范围：站点文件 + `PRD/` + `PDF_真题/` + `_build/`（构建链）；`_backup/` 仅本地保留，不同步到线上。

## 版本

- 当前：V2.3（2026-10-04）
