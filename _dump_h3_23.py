"""把第02、03集共 36 条 h3 导出成单独文件，供 check_h3_prompt.py 逐条校验。"""
import json, os, sys
ROOT = r"D:\AAA\text\假钦差\短剧"
OUT = os.path.join(ROOT, "_h3chk")
os.makedirs(OUT, exist_ok=True)
data = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
n = 0
for s in data["shots"]:
    if s["ep"] not in ("02", "03"):
        continue
    p = os.path.join(OUT, f"ep{s['ep']}_{s['id']}.txt")
    open(p, "w", encoding="utf-8").write(s["h3"])
    n += 1
print("dumped", n)
