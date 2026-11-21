import json, os, shutil
ROOT = r"D:\AAA\text\假钦差\短剧"
# 1) 备份并清空第01集旧视频
src = os.path.join(ROOT, "04_视频", "第01集")
bak = os.path.join(ROOT, "06_素材", "旧_文生图版", "视频_旧_第01集")
os.makedirs(bak, exist_ok=True)
moved = 0
for f in os.listdir(src):
    p = os.path.join(src, f)
    if os.path.isfile(p) and (f.endswith(".mp4") or f in ("sub.ass", "sub.srt")):
        shutil.move(p, os.path.join(bak, f)); moved += 1
print("moved", moved)
# 2) 清 progress.json 里 ep01 的 video 记录
log = os.path.join(ROOT, "progress.json")
d = json.load(open(log, encoding="utf-8")) if os.path.exists(log) else {}
for k in list(d):
    if k.startswith("ep01_"):
        for f in ("video", "video_at", "video_error"):
            d[k].pop(f, None)
        if not d[k]:
            d.pop(k)
json.dump(d, open(log, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("progress keys", len(d))
