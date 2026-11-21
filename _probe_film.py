import subprocess, imageio_ffmpeg, os
FF = imageio_ffmpeg.get_ffmpeg_exe()
f = r"D:\AAA\text\假钦差\短剧\05_成片\第01集_成片.mp4"
out = r"D:\AAA\text\假钦差\短剧\06_素材\check_ep01v3"
r = subprocess.run([FF,"-i",f], capture_output=True, text=True)
for ln in r.stderr.splitlines():
    if "Duration" in ln or "Stream" in ln: print(ln.strip())
for t in (1, 7, 27, 52, 88):
    subprocess.run([FF,"-y","-loglevel","error","-ss",str(t),"-i",f,"-frames:v","1",os.path.join(out,f"film_{t}.png")])
print("frames ok")
