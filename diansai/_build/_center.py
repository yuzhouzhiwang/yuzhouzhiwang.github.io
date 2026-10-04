# -*- coding: utf-8 -*-
import io
p = r"D:\公司正式项目【舅舅交代】\TI\电赛真题三大电子筛选\PRD\PRD_总览.html"
s = io.open(p, encoding='utf-8').read()

repl = [
  # base year-group: centered max-width 720, vertical stacking
  ('.year-group{margin:24px 0}.year-group.compact{margin:8px 0}.year-group.compact .year-title{margin-bottom:8px}',
   '.year-group{margin:24px auto;max-width:720px}.year-group.compact{margin:8px auto;max-width:720px}.year-group.compact .year-title{margin-bottom:8px}'),
  # desktop media: no float, keep vertical (rule now redundant but harmless)
  ('@media(min-width:769px){.year-group{display:block;width:auto;margin:24px 0}}',
   '@media(min-width:769px){.year-group{display:block;width:auto}}'),
]

for old, new in repl:
    assert s.count(old) == 1, "missing: " + old[:60]
    s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("OK: centered single column")
