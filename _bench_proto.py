import json, os, time, sys
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline

ROOT = r"D:\AAA\text\假钦差\短剧"
res = sys.argv[1] if len(sys.argv) > 1 else "512x896"
img = os.path.join(ROOT, "03_图片", "第02集", "s01.png")
prompt = "近景过肩，守城兵背影虚焦持枪，枪尖指向左侧男子胸前一掌宽空隙，男子玄黑蟒袍不动，冷灰晨光，镜头缓慢推近"
t0 = time.time()
r = pipeline.gen_video(prompt, img, duration=5, resolution=res, model="h3_i2v_turbo")
print("elapsed", round(time.time() - t0, 1), "s")
print(json.dumps(r, ensure_ascii=False)[:600])
os.makedirs(os.path.join(ROOT, "06_素材", "bench"), exist_ok=True)
try:
    out = pipeline.copy_out(r["data"][0]["path"], os.path.join(ROOT, "06_素材", "bench", "proto_" + res + ".mp4"))
    print("saved", out)
except Exception as e:
    print("copy failed", e)
