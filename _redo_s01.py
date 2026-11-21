import json, os, sys
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
import batch as B

DATA = json.load(open(os.path.join(P.ROOT, "shots.json"), encoding="utf-8"))
shot = [s for s in DATA["shots"] if s["ep"] == "01" and s["id"] == "s01"][0]
img = os.path.join(P.ROOT, "03_图片", "第01集", "s01.png")
rel = B.stage_first_frame("01", "s01", img)
r = P.gen_video(shot["h3"], rel, duration=5, resolution="768x1344", ratio="9:16",
                model=DATA["meta"]["video_model"])
dst = os.path.join(P.ROOT, "04_视频", "第01集", "s01.mp4")
P.copy_out(r["data"][0]["path"], dst)
log = B.load_log()
log.setdefault("ep01_s01", {})["video"] = r["data"][0]["path"]
B.save_log(log)
print("redo s01 ok", os.path.getsize(dst))
