import os, subprocess
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
p = r"D:\AAA\text\假钦差\短剧\06_素材\参考库\人物_沈照夜_定妆.png"
tmp = p.replace(".png","_tmp.png")
r = subprocess.run([FF,"-y","-loglevel","error","-i",p,
    "-vf","scale=768:1344:force_original_aspect_ratio=increase,crop=768:1344","-frames:v","1",tmp], capture_output=True, text=True)
print("rc", r.returncode, r.stderr[-300:])
if r.returncode==0:
    os.replace(tmp,p); print("ok", os.path.getsize(p))
