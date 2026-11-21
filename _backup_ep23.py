"""重做第02、03集前的备份：旧 9 镜图片与视频整体挪到 06_素材\旧_文生图版\。"""
import os, shutil

ROOT = r"D:\AAA\text\假钦差\短剧"
BK = os.path.join(ROOT, "06_素材", "旧_文生图版")
os.makedirs(BK, exist_ok=True)

for ep in ("02", "03"):
    for kind, sub in (("图片", "03_图片"), ("视频", "04_视频")):
        src = os.path.join(ROOT, sub, f"第{ep}集")
        dst = os.path.join(BK, f"{kind}_旧_第{ep}集")
        os.makedirs(dst, exist_ok=True)
        if os.path.isdir(src):
            for f in os.listdir(src):
                shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
                print("bak", ep, kind, f)
print("done")
