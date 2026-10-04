# -*- coding: utf-8 -*-
# 组装 index.html：_head.html + TOPICS/PAGE_DATA 数据 + _tail.html
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def read(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return f.read()

head = read("_head.html")
tail = read("_tail.html")
topics = __import__("topics_data").TOPICS
page_data = __import__("page_data")

data_js = ("<script>window.TOPICS=" + json.dumps(topics, ensure_ascii=False) + ";</script>"
           "<script>window.PAGE_DATA=" + json.dumps({
               "RECOMMEND": page_data.RECOMMEND,
               "CIRCUITS": page_data.CIRCUITS,
               "COMPONENTS": page_data.COMPONENTS,
               "BASIC": page_data.BASIC,
               "TIADI": page_data.TIADI,
           }, ensure_ascii=False) + ";</script>")

html = head + data_js + tail
with open(os.path.join(BASE, "..", "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("index.html 生成完成，大小:", len(html.encode("utf-8")), "字节")
print("数据条目:", len(topics), "| 电路模块:", len(page_data.CIRCUITS), "| 元器件:", len(page_data.COMPONENTS))
