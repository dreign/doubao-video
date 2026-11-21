import os, subprocess, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
vdir = r"D:\AAAText".replace("AAAText", r"AAA\text")
vdir = r"D:\AAA\text\假钦差\短剧\04_视频\第01集"
out = r"D:\AAA\text\假钦差\短剧\06_素材\check_ep01v3"
os.makedirs(out, exist_ok=True)
for sid in ("s01","s09","s16"):
    f = os.path.join(vdir, sid+".mp4")
    if not os.path.exists(f): print("miss", sid); continue
    for t in (1,4):
        dst = os.path.join(out, f"{sid}_{t}.png")
        subprocess.run([FF,"-y","-loglevel","error","-ss",str(t),"-i",f,"-frames:v","1",dst])
    print("ok", sid)
