# ============================================================
# 时光 · 硬件基础打卡计划 · 云端数据库每日更新
# 由 GitHub Actions 每天北京时间 07:25（UTC 23:25）自动运行
# 功能：更新 /plan/data.js 的版本号、更新时间、当前阶段
# ============================================================
import re, os, json, datetime, sys

DATA_FP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.js')

def now_beijing():
    # GitHub Actions 环境为 UTC，手动换算北京时间 UTC+8
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)

def get_phase(today):
    """根据今天日期判断当前阶段：jinjiu(金九银十)/jinsan(金三银四)/休息期"""
    # 金九银十：2026-09-01 ~ 2026-11-30
    if '2026-09-01' <= today <= '2026-11-30':
        return 'jinjiu'
    # 金三银四：2027-03-01 ~ 2027-04-30
    if '2027-03-01' <= today <= '2027-04-30':
        return 'jinsan'
    return 'jinjiu'  # 过渡期默认金九银十

def main():
    c = open(DATA_FP, encoding='utf-8').read()
    now = now_beijing()
    today = now.strftime('%Y-%m-%d')
    ts = now.strftime('%Y-%m-%d %H:%M:%S')

    # 版本号 +1
    m = re.search(r'version:\s*(\d+)', c)
    ver = int(m.group(1)) + 1 if m else 1
    c = re.sub(r'version:\s*\d+', 'version: ' + str(ver), c, count=1)

    # 更新时间
    c = re.sub(r"lastUpdated:\s*'[^']*'", "lastUpdated: '" + ts + "'", c, count=1)

    # 当前阶段
    phase = get_phase(today)
    c = re.sub(r"phase:\s*'[^']*'", "phase: '" + phase + "'", c, count=1)

    open(DATA_FP, 'w', encoding='utf-8').write(c)
    print(f"OK data.js updated: version={ver}, lastUpdated={ts}, phase={phase}")

if __name__ == '__main__':
    main()
