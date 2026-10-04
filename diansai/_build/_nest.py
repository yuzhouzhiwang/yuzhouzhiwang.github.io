# -*- coding: utf-8 -*-
import io
from html.parser import HTMLParser

p = r"D:\公司正式项目【舅舅交代】\TI\电赛真题三大电子筛选\PRD\PRD_总览.html"
s = io.open(p, encoding='utf-8').read()

# Find wrap open and close tag positions
open_mark = '<div class="year-groups-wrap">'
close_mark = '</div>'
i_open = s.find(open_mark)
# locate the wrap's own closing div: walk from i_open with depth counting
depth = 0
i = i_open
j = -1
while i < len(s):
    nxt_o = s.find('<div', i)
    nxt_c = s.find('</div>', i)
    if nxt_c == -1: break
    if nxt_o != -1 and nxt_o < nxt_c:
        depth += 1
        i = nxt_o + 4
    else:
        depth -= 1
        i = nxt_c + 6
        if depth == 0:
            j = i - 6
            break
print("wrap open at:", i_open)
print("wrap close at:", j)
seg = s[i_open:j+6]
print("groups inside wrap:", seg.count('<div class="year-group'))
print("wrap nesting after close: ...", s[j+6:j+6+80].replace('\n',' '))
# what follows wrap close
tail = s[j+6:j+6+120]
print("TAIL:", tail)
