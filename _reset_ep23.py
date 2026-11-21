"""清掉第02、03集的出图/视频完成记录，让两集按新镜表重跑。"""
import json, os

ROOT = r"D:\AAA\text\假钦差\短剧"

fs = os.path.join(ROOT, "flux_shots.json")
if os.path.exists(fs):
    d = json.load(open(fs, encoding="utf-8"))
    for k in [k for k in d if k.startswith(("02-", "03-"))]:
        d.pop(k)
    json.dump(d, open(fs, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("flux keys left:", list(d.keys()))

pg = os.path.join(ROOT, "progress.json")
if os.path.exists(pg):
    d = json.load(open(pg, encoding="utf-8"))
    for k in [k for k in d if k.startswith(("ep02_", "ep03_"))]:
        d.pop(k)
    json.dump(d, open(pg, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("progress keys left:", list(d.keys()))
