import json, os
ROOT = r"D:\AAA\text\假钦差\短剧"
D = os.path.join(ROOT, "_h3chk")
data = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
for s in data["shots"]:
    if s["ep"] != "01": continue
    open(os.path.join(D, f"{s['ep']}-{s['id']}.txt"), "w", encoding="utf-8").write(s["h3"])
print("dumped")
