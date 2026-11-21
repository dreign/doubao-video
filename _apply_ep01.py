import json, os, sys
ROOT = r"D:\AAA\text\假钦差\短剧"
sys.path.insert(0, ROOT)
import ep01_shots as E

p = os.path.join(ROOT, "shots.json")
data = json.load(open(p, encoding="utf-8"))
keep = [s for s in data["shots"] if s["ep"] != "01"]
new = []
for ep, sid, title, image, video, line, snd, h3 in E.SHOTS:
    new.append({"ep": ep, "id": sid, "dur": 5, "title": title, "image": image,
                "video": video, "line": line, "snd": snd, "h3": h3})
# 保持 01 在最前
data["shots"] = new + keep
data["meta"]["format"] = "竖屏 9:16 / 768×1344 / 24fps"
data["meta"]["ep01_pipeline"] = "短剧版 18 拍 × 5 秒 = 90 秒"
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
eps = {}
for s in data["shots"]:
    eps[s["ep"]] = eps.get(s["ep"], 0) + 1
print("shots:", eps, "total", len(data["shots"]))
