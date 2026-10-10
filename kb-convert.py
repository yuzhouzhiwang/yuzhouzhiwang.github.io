# -*- coding: utf-8 -*-
"""
工程师知识库 md -> HTML 优化转换脚本（博客静态版）
将 knowledge/ 下的 markdown 批量转换为深色科技风 HTML 页面：
- 解析 front matter 标题、删除 liquid raw 标签
- markdown -> HTML（表格/代码块/目录/提示卡/脚注等扩展）
- 生成页面模板（共享 kb-style.css + highlight.js/mermaid/mathjax CDN + 面包屑 + 目录 + 返回顶部）
- 输出同名 .html（index.md -> index.html），删除原 .md
用法：python kb-convert.py
"""
import os
import re
import sys
import markdown

ROOT = r"D:\GitHub个人主页项目\yuzhouzhiwang.github.io\knowledge"

# 面包屑中文映射（常用目录）
CRUMB_MAP = {
    "01-foundations": "基础层", "01-hardware-layer": "硬件层",
    "02-technologies": "技术层", "03-architecture": "架构层",
    "04-projects": "项目层", "05-insights": "洞察层",
    "embedded": "嵌入式", "ai": "AI", "cloud": "云计算",
}

PAGE_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="generator" content="工程师知识库静态转换">
<title>{TITLE} · 工程师知识库</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/knowledge/kb-style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
<div class="kb-page">
  <div class="kb-topbar">
    <a class="kb-home" href="/knowledge/">← 知识库首页</a>
    <span class="kb-crumb">{CRUMB}</span>
  </div>
  <details class="kb-toc" open><summary>📑 本页目录</summary>{TOC}</details>
  <article class="kb-article">
{CONTENT}
  </article>
  <div class="kb-footer"><a href="/knowledge/">← 返回工程师知识库</a></div>
</div>
<script>
document.querySelectorAll('code.language-mermaid').forEach(function(c){{var p=c.parentNode;var m=document.createElement('pre');m.className='mermaid';m.textContent=c.textContent;p.parentNode.replaceChild(m,p);}});
hljs.highlightAll();
mermaid.initialize({{startOnLoad:true,theme:'dark'}});
var bt=document.createElement('div');bt.className='kb-backtop';bt.textContent='↑';document.body.appendChild(bt);
window.addEventListener('scroll',function(){{bt.classList.toggle('show',window.scrollY>400);}});
bt.addEventListener('click',function(){{window.scrollTo({{top:0,behavior:'smooth'}});}});
</script>
</body>
</html>
"""

def parse_frontmatter(text):
    """返回 (meta_dict, body)。front matter 为文件头 --- ... --- 的 YAML 块。"""
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

def build_crumb(rel_dir):
    """从相对目录生成面包屑 HTML"""
    parts = rel_dir.split(os.sep) if rel_dir else []
    parts = [p for p in parts if p]
    accum = []
    html = []
    for p in parts:
        accum.append(p)
        name = CRUMB_MAP.get(p, p)
        html.append('<a href="/knowledge/%s/">%s</a>' % ("/".join(accum), name))
    if html:
        return " / ".join(html)
    return '<a href="/knowledge/">知识库</a>'

def convert_file(md_path, rel):
    text = open(md_path, encoding="utf-8-sig").read()
    meta, body = parse_frontmatter(text)
    body = re.sub(r"\{%\s*raw\s*%\}", "", body)
    body = re.sub(r"\{%\s*endraw\s*%\}", "", body)
    md = markdown.Markdown(extensions=[
        "fenced_code", "tables", "toc", "admonition", "footnotes",
        "attr_list", "def_list", "abbr", "md_in_html", "sane_lists",
    ], extension_configs={
        "toc": {"permalink": False, "toc_depth": "2-4"},
    })
    content = md.convert(body)
    toc = md.toc if hasattr(md, "toc") else ""
    title = meta.get("title") or first_h1(body) or os.path.basename(md_path)
    title = title.strip().strip('"')
    rel_dir = os.path.dirname(rel)
    crumb = build_crumb(rel_dir)
    html = (PAGE_TPL.replace("{TITLE}", title)
            .replace("{CRUMB}", crumb)
            .replace("{TOC}", toc)
            .replace("{CONTENT}", content))
    out_path = md_path[:-3] + ".html"  # .md -> .html（index.md -> index.html 自然成立）
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    os.remove(md_path)
    return title

def main():
    md_files = []
    for r, d, fs in os.walk(ROOT):
        for fn in fs:
            if fn.lower().endswith(".md"):
                md_files.append(os.path.join(r, fn))
    ok = 0
    fail = []
    for p in md_files:
        rel = os.path.relpath(p, ROOT)
        try:
            convert_file(p, rel)
            ok += 1
        except Exception as e:
            fail.append((rel, str(e)))
    print("converted:", ok, "/", len(md_files))
    if fail:
        print("FAILED:")
        for rel, err in fail[:20]:
            print("  ", rel, "->", err)
    left = 0
    for r, d, fs in os.walk(ROOT):
        for fn in fs:
            if fn.lower().endswith(".md"):
                left += 1
    print("remaining md:", left)

if __name__ == "__main__":
    main()
