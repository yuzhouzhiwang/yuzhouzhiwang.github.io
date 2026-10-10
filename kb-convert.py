# -*- coding: utf-8 -*-
"""
工程师知识库 md -> HTML 转换脚本 v2（Material 风格）
- 输入：Desktop knowledge-system/knowledge（md 源，排除 templates/.obsidian 等）
- 输出：博客仓库 knowledge/（HTML + kb-nav.json 导航树 + search_index.json 搜索索引）
- 模板：顶栏(logo+面包屑+搜索) / 左侧导航树 / 正文 / 右侧TOC / 上下页分页
- 链接：相对 .md 链接改写为 .html
用法：python kb-convert.py
"""
import os
import re
import json
from html.parser import HTMLParser

SRC = r"C:\Users\Administrator\Desktop\knowledge-system\knowledge"
OUT = r"D:\GitHub个人主页项目\yuzhouzhiwang.github.io\knowledge"
EXCLUDE_DIRS = {"templates", ".obsidian", ".git", ".github"}

import markdown

DIR_NAMES = {
    "01-foundations": "基础层", "01-hardware-layer": "硬件层", "02-technologies": "技术层",
    "03-architecture": "架构层", "04-projects": "项目层", "05-insights": "洞察层",
    "embedded": "嵌入式", "ai": "AI", "cloud": "云计算", "finance": "金融认知",
    "02-driver-bsp-layer": "驱动与BSP层", "03-operating-system-layer": "操作系统层",
    "04-application-layer": "应用层", "05-cross-domain-integration": "跨域集成",
    "06-communication-networking": "通信与网络", "07-cloud-backend": "云端与后台",
    "08-toolchain": "工具链与DevOps", "09-project-practice": "项目实践",
    "10-cross-cutting-concerns": "横切关注点",
    "01-chip-architecture": "芯片架构", "02-hardware-design-fundamentals": "硬件设计基础",
    "03-power-management": "电源管理", "04-sensor-technology": "传感器技术",
    "05-actuator-control": "执行器控制", "06-communication-interface-hardware": "通信接口硬件",
    "01-bare-metal": "裸机编程", "02-rtos-basics": "RTOS基础", "03-freertos": "FreeRTOS",
    "04-rt-thread": "RT-Thread", "05-embedded-linux": "嵌入式Linux", "06-android": "Android",
    "01-programming-languages": "编程语言", "02-software-architecture": "软件架构与设计模式",
    "03-security-reliability": "安全与可靠性", "04-project-management": "项目管理与职业",
    "05-application-frameworks": "应用框架", "06-ota-remote-management": "OTA与远程管理",
    "07-ui-development": "用户界面开发", "08-database-data-management": "数据库与数据管理",
    "09-multimedia": "多媒体", "10-embedded-ai-ml": "嵌入式AI/ML",
    "01-wireless-communication": "无线通信", "02-network-protocols": "网络协议", "03-iot-cloud": "IoT云接入",
    "01-backend-development": "后端开发", "02-cloud-computing": "云计算", "03-data-visualization": "数据可视化",
    "04-testing": "测试与验证", "05-performance-optimization": "性能优化",
    "01-basic": "入门", "02-intermediate": "进阶", "03-advanced": "高级",
    "01-macro-economics": "宏观经济学", "02-monetary-policy": "货币政策", "03-risk-management": "风险管理",
    "04-asset-allocation": "资产配置", "05-investment-masters": "投资大师", "06-macro-framework": "宏观框架",
    "07-financial-history": "金融历史", "08-practical-tools": "实践工具",
    "01-company-research": "公司研究", "02-industry-analysis": "行业分析", "03-global-perspective": "全球视野",
    "01-us-market": "美股市场", "02-china-market": "中国市场", "03-emerging-markets": "新兴市场",
    "01-technology": "科技板块", "02-consumer": "消费板块", "03-energy": "能源板块",
    "04-finance": "金融板块", "05-healthcare": "医疗保健", "06-industrials": "工业",
    "01-semiconductor": "半导体", "02-software": "软件", "03-internet": "互联网",
    "01-banks": "银行", "02-insurance": "保险", "03-payments": "支付",
    "01-crises": "金融危机", "02-monetary-history": "货币历史", "03-market-evolution": "市场演变",
    "04-ideas": "思想演进", "01-macro-indicators": "宏观指标",
    "01-analysis-tools": "分析工具", "02-checklists": "检查清单", "03-data-sources": "数据源",
    "04-learning-resources": "学习资源", "05-practice": "实践", "06-psychology": "投资心理", "07-tools": "工具",
    "05-insights": "洞察层",
}

PAGE_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="generator" content="工程师知识库静态转换 v2">
<title>{TITLE} · 工程师知识库</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/knowledge/kb-style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
</head>
<body>
<div class="kb-progress" id="kb-progress"></div>
<header class="kb-header">
  <a class="kb-logo" href="/knowledge/"><span class="dot"></span>工程师知识库</a>
  <div class="kb-crumbs">{CRUMB}</div>
  <div class="kb-search">
    <input id="kb-search-input" type="text" placeholder="搜索知识库…（按 / 聚焦）" autocomplete="off">
    <span class="hotkey">/</span>
  </div>
</header>
<div class="kb-search-panel" id="kb-search-panel">
  <div id="kb-search-results"><div class="kb-search-empty">输入关键词开始搜索</div></div>
</div>
<div class="kb-layout">
  <aside class="kb-side" id="kb-side"></aside>
  <main class="kb-main">
    <details class="kb-toc-inline" open><summary>📑 本页目录</summary>{TOC}</details>
    <article class="kb-article">
{CONTENT}
    </article>
    <div class="kb-prevnext">
      <a class="prev" href="{PREV_URL}"><span class="lbl">← 上一篇</span>{PREV_TITLE}</a>
      <a class="next" href="{NEXT_URL}"><span class="lbl">下一篇 →</span>{NEXT_TITLE}</a>
    </div>
    <div class="kb-footer">© 工程师知识库 · <a href="/">返回博客首页</a></div>
  </main>
  <aside class="kb-toc-rt"><div class="h">本页目录</div>{TOC}</aside>
</div>
<button class="kb-backtop" id="kb-backtop">↑</button>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
<script src="/knowledge/kb-app.js"></script>
<script>
mermaid.initialize({{startOnLoad:true,theme:'dark'}});
document.querySelectorAll('code.language-mermaid').forEach(function(c){{var p=c.parentNode;var m=document.createElement('pre');m.className='mermaid';m.textContent=c.textContent;p.parentNode.replaceChild(m,p);}});
hljs.highlightAll();
</script>
</body>
</html>
"""


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "h1", "h2", "h3", "h4", "li", "pre", "tr", "br", "blockquote"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in ("p", "h1", "h2", "h3", "h4", "li", "pre", "tr", "blockquote"):
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(html):
    p = TextExtractor()
    try:
        p.feed(html)
    except Exception:
        return ""
    text = "".join(p.parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm = "".join(lines[1:end])
    body = "".join(lines[end + 1:])
    meta = {}
    for line in fm.splitlines():
        m = re.match(r'^([\w\-]+)\s*:\s*"?([^"]*?)"?\s*$', line.strip())
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
    return meta, body


def first_h1(body):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def fix_links(body):
    body = re.sub(r'(\[[^\]]*\]\()([^)#]+?)\.md(#[^)]*)?(\))', r'\1\2.html\3\4', body)
    body = re.sub(r'(href|src)="([^"]*?)\.md(#[^"]*)?"', r'\1="\2.html\3"', body)
    return body


def display_name(name):
    return DIR_NAMES.get(name, name)


# ---------- 构建导航树 ----------
def build_tree():
    root = {"type": "dir", "name": "工程师知识库", "url": "/knowledge/", "children": [], "has_index": True}

    def walk(dirpath, node, rel):
        entries = []
        try:
            for e in os.scandir(dirpath):
                entries.append(e)
        except OSError:
            return
        entries.sort(key=lambda e: e.name.lower())
        for e in entries:
            if e.name in EXCLUDE_DIRS:
                continue
            relpath = rel + "/" + e.name if rel else e.name
            if e.is_dir():
                child = {"type": "dir", "name": display_name(e.name), "url": "/knowledge/" + relpath + "/",
                         "children": [], "has_index": False}
                walk(e.path, child, relpath)
                node["children"].append(child)
            elif e.name.lower().endswith(".md"):
                if e.name.lower() == "index.md":
                    node["has_index"] = True
                    node["index_md_path"] = e.path
                    node["index_rel"] = relpath
                else:
                    page = {"type": "page", "name": e.name[:-3], "url": "/knowledge/" + relpath[:-3] + ".html",
                            "md_path": e.path, "rel": relpath[:-3]}
                    node["children"].append(page)

    walk(SRC, root, "")
    return root


# ---------- 线性化 + prev/next ----------
def flatten(root):
    order = []
    if root["type"] == "dir" and root.get("has_index"):
        order.append(root)
    for c in root.get("children", []):
        if c["type"] == "dir":
            order.extend(flatten(c))
        else:
            order.append(c)
    return order


def build_pages_meta(root, order):
    pages = {}
    for i, node in enumerate(order):
        url = node["url"]
        prev = order[i - 1]["url"] if i > 0 else ""
        nxt = order[i + 1]["url"] if i < len(order) - 1 else ""
        pages[url] = {"p": prev, "n": nxt}
    return pages


def crumb_text(rel):
    parts = [p for p in rel.split("/") if p]
    if not parts:
        return "工程师知识库"
    names = ["工程师知识库"] + [display_name(p) for p in parts]
    return " / ".join(names)


# ---------- 主流程 ----------
def main():
    root = build_tree()
    order = flatten(root)
    pages_meta = build_pages_meta(root, order)

    # 清理旧产物（全量删除，保证模板一致）
    for r, d, fs in os.walk(OUT):
        for fn in fs:
            if fn.lower().endswith(".html"):
                os.remove(os.path.join(r, fn))
    for extra in ("kb-nav.json", "search_index.json"):
        p = os.path.join(OUT, extra)
        if os.path.exists(p):
            os.remove(p)

    search_index = []
    tree_pages = {}
    converted = 0
    failed = []

    for node in order:
        if node["type"] == "dir":
            if not node.get("has_index"):
                continue
            md_path = node.get("index_md_path")
            rel = node.get("index_rel")
        else:
            md_path = node["md_path"]
            rel = node["rel"]
        try:
            text = open(md_path, encoding="utf-8-sig").read()
        except Exception as e:
            failed.append((rel, str(e)))
            continue
        meta, body = parse_frontmatter(text)
        body = re.sub(r"\{%\s*raw\s*%\}", "", body)
        body = re.sub(r"\{%\s*endraw\s*%\}", "", body)
        body = fix_links(body)
        md = markdown.Markdown(extensions=[
            "fenced_code", "tables", "toc", "admonition", "footnotes",
            "attr_list", "def_list", "abbr", "md_in_html", "sane_lists",
        ], extension_configs={"toc": {"permalink": False, "toc_depth": "2-4"}})
        content = md.convert(body)
        toc = md.toc if hasattr(md, "toc") else ""
        title = meta.get("title") or first_h1(body) or os.path.basename(md_path)
        title = title.strip().strip('"')
        rel_dir = os.path.dirname(rel)
        crumb_html = build_crumb_html(rel_dir)
        url = node["url"]
        pm = pages_meta.get(url, {"p": "", "n": ""})
        prev_title = ""
        if pm["p"]:
            prev_title = title_of(pm["p"], order)
        next_title = ""
        if pm["n"]:
            next_title = title_of(pm["n"], order)
        page = (PAGE_TPL.replace("{TITLE}", title)
                .replace("{CRUMB}", crumb_html)
                .replace("{TOC}", toc)
                .replace("{CONTENT}", content)
                .replace("{PREV_URL}", pm["p"])
                .replace("{PREV_TITLE}", prev_title)
                .replace("{NEXT_URL}", pm["n"])
                .replace("{NEXT_TITLE}", next_title))
        out_path = os.path.join(OUT, rel, "index.html") if node["type"] == "dir" else os.path.join(OUT, rel + ".html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
        # 搜索索引与树元数据
        plain = html_to_text(content)
        search_index.append({"t": title, "u": url, "c": crumb_text(rel_dir), "x": plain[:4000]})
        tree_pages[url] = {"t": title}
        converted += 1

    # 首页（index.md -> index.html）特殊处理：由外部手写版覆盖，这里仅转换占位
    # 导航树写出（剔除本地路径等内部字段）
    nav = {"tree": clean_node(root), "pages": tree_pages}
    with open(os.path.join(OUT, "kb-nav.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(nav, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "search_index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(search_index, f, ensure_ascii=False, separators=(",", ":"))

    print("converted:", converted)
    print("search_index:", len(search_index), "entries")
    if failed:
        print("FAILED:")
        for rel, err in failed[:20]:
            print("  ", rel, "->", err)


def build_crumb_html(rel_dir):
    parts = [p for p in rel_dir.split("/") if p]
    html = []
    accum = []
    for p in parts:
        accum.append(p)
        html.append('<a href="/knowledge/%s/">%s</a>' % ("/".join(accum), display_name(p)))
    if html:
        return " / ".join(html)
    return '<a href="/knowledge/">工程师知识库</a>'


def clean_node(n):
    """剔除导航树中的本地路径等内部字段，仅保留公开展示字段"""
    return {"type": n["type"], "name": n["name"], "url": n["url"],
            "children": [clean_node(c) for c in n.get("children", [])]}


def title_of(url, order):
    for node in order:
        if node["url"] == url:
            if node["type"] == "dir":
                return node["name"]
            return node["name"]
    return ""


if __name__ == "__main__":
    main()
