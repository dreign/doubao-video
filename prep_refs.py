"""把角色定妆稿（左特写+右三视图）切成 Flux2 可用的人物参考图。"""
import os
from PIL import Image

SRC = r"D:\AAA\text\假钦差"
OUT = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
os.makedirs(OUT, exist_ok=True)

def cut(src_name, tag):
    im = Image.open(os.path.join(SRC, src_name))
    w, h = im.size
    face = im.crop((0, 0, int(w * 0.38), h))
    body = im.crop((int(w * 0.425), 0, int(w * 0.60), h))
    for sub, box in (("面部", face), ("全身", body)):
        p = os.path.join(OUT, f"人物_陈知白_{tag}_{sub}.png")
        im2 = box.copy()
        im2.thumbnail((1400, 1400), Image.LANCZOS)
        im2.save(p)
        print("saved", p, im2.size)

cut("陈知白 · 青衫穷秀才版.png", "青衫")
cut("陈知白 · 钦差服版.png", "钦差")
