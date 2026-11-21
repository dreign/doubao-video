"""把 9:16 三视图定型稿切成 Flux2 用的单视图参考图。
版式固定：上 1/2 面部特写；下方左=正面全身，右=背面全身。
"""
import os
from PIL import Image

REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"

SHEETS = {
    "人物_陈知白_青衫_定型稿.png": "人物_陈知白_青衫",
    "人物_陈知白_钦差_定型稿.png": "人物_陈知白_钦差",
    "人物_玄甲禁军_定型稿.png": "人物_玄甲禁军",
    "人物_守城兵_定型稿.png": "人物_守城兵",
    "人物_白龙马_定妆.png": "人物_白龙马",
}

for f, tag in SHEETS.items():
    p = os.path.join(REF, f)
    if not os.path.exists(p):
        print("missing", p); continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    mid = int(h * 0.47)
    parts = {
        "面部": im.crop((0, 0, w, mid)),
        "全身": im.crop((0, mid, int(w * 0.5), h)),
        "背面": im.crop((int(w * 0.5), mid, w, h)),
    }
    for sub, box in parts.items():
        # 去白边
        g = box.convert("L").point(lambda v: 0 if v > 244 else 255)
        bbox = g.getbbox()
        if bbox:
            pad = 6
            box = box.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
                            min(bbox[2] + pad, box.width), min(bbox[3] + pad, box.height)))
        out = os.path.join(REF, f"{tag}_{sub}.png")
        box.thumbnail((1400, 1400), Image.LANCZOS)
        box.save(out)
        print("saved", os.path.basename(out), box.size)
