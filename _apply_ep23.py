import json, os, sys
ROOT = r"D:\AAA\text\假钦差\短剧"
sys.path.insert(0, ROOT)
import ep02_shots as E2
import ep03_shots as E3

p = os.path.join(ROOT, "shots.json")
data = json.load(open(p, encoding="utf-8"))
keep = [s for s in data["shots"] if s["ep"] == "01"]
new = []
for mod, ep in ((E2, "02"), (E3, "03")):
    for sid, title, image, video, line, snd, h3 in mod.SHOTS:
        new.append({"ep": ep, "id": sid, "dur": 5, "title": title, "image": image,
                    "video": video, "line": line, "snd": snd, "h3": h3})
data["shots"] = keep + new
data["meta"]["ep02_pipeline"] = "短剧版 18 拍 × 5 秒 = 90 秒（第02集《叫城》）"
data["meta"]["ep03_pipeline"] = "短剧版 18 拍 × 5 秒 = 90 秒（第03集《官腔》）"
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
eps = {}
for s in data["shots"]:
    eps[s["ep"]] = eps.get(s["ep"], 0) + 1
print("shots:", eps, "total", len(data["shots"]))
