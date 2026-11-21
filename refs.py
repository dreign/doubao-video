"""建参考图库：人物定妆、场景板、道具板。全部落在 06_素材\参考库。
用法：python refs.py [--force]
"""
import json, os, shutil, sys, time
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
import flux_edit as F

REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
COMFY_OUT = r"C:\Users\Administrator\ComfyUI-Shared\output"
os.makedirs(REF, exist_ok=True)

# 场景/道具：文生图（干净的中性参考板，不带戏剧化构图）
T2I = {
    "场景_贡院.png": ("9:16 竖构图场景参考图，仰视角度，中国古代贡院朱红宫墙与门楼自上而下铺满画面，两侧各一尊巨大石狮，青石台阶与地面结霜，右侧一盏昏黄灯笼，清晨冷青灰光，薄雾贴地，无人物，写实历史剧质感，无文字", "768x1344", "9:16"),
    "场景_青石窄巷.png": ("9:16 竖构图场景参考图，中国古代县城狭窄青石小巷的纵深视角，两侧斑驳青灰砖墙向上收窄，墙面苔痕，地面湿滑青石板，巷口透进冷白晨光，无人物，写实历史剧质感，无文字", "768x1344", "9:16"),
    "场景_乱葬岗.png": ("9:16 竖构图场景参考图，荒芜乱葬岗，齐腰枯黄荒草，枯死黑树向上伸出画面，散落断碑与浅土坑，远处起伏土包，灰白阴天薄雾，无人物，写实历史剧质感，无文字", "768x1344", "9:16"),
    "场景_清河城门.png": ("9:16 竖构图场景参考图，中国古代县城青灰砖城墙与拱形城门洞，城墙自下向上占据画面上部，城门半开，门洞内透出暖黄晨光，墙砖斑驳，无人物，写实历史剧质感，无文字", "768x1344", "9:16"),
    "场景_城内小巷.png": ("9:16 竖构图场景参考图，中国古代县城内僻静小巷，斑驳青砖墙在画面两侧，斜射晨光切过墙面形成明暗分割，地面青石板，墙角堆着柴草，无人物，写实历史剧质感，无文字", "768x1344", "9:16"),
    "物品_半枚玉玺.png": ("道具特写参考图，半枚残缺的和田白玉玺置于深灰粗麻布上，断口整齐如刀切，正面浮雕残缺龙纹与一颗极小血红宝石，玉质乳白温润半透，柔和侧光，微距，写实，无文字", "768x1344", "9:16"),
    "物品_蟒袍.png": ("道具参考图，玄黑缎面明代钦差蟒袍正面平铺展开，金线绣四爪蟒纹自右肩盘绕至左腰，下摆云纹，玉带置于其上，深灰背景，均匀柔光，写实，无文字", "768x1344", "9:16"),
    "物品_告示红榜.png": ("道具参考图，一张皱巴巴的黄纸科举告示平铺在结霜青石上，纸边毛糙，墨迹被浓黑墨划穿一道，画面中文字不可辨认，柔和冷光，俯拍，写实", "768x1344", "9:16"),
    "物品_枣红马.png": ("动物参考图，一匹枣红色骏马侧身站立于浅灰背景，马背驮着鼓胀的黑色粗布包袱，简陋缰绳，全身入画，均匀柔光，写实，无文字", "768x1344", "9:16"),
}

def exists(n):
    p = os.path.join(REF, n)
    return os.path.exists(p) and os.path.getsize(p) > 100000

def t2i():
    for name, (prompt, size, ratio) in T2I.items():
        if exists(name):
            print("skip", name); continue
        t0 = time.time()
        r = P.gen_image(prompt, size=size, ratio=ratio)
        P.copy_out(r["data"][0]["path"], os.path.join(REF, name))
        print("ok", name, round(time.time() - t0, 1), "s", flush=True)

def costume_swap():
    """用青衫版的脸换钦差服，保证同一张脸。"""
    name = "人物_陈知白_钦差_定妆.png"
    if exists(name):
        print("skip", name); return
    a = F.upload(os.path.join(REF, "人物_陈知白_青衫_全身.png"), "ref_chen_qing.png")
    b = F.upload(os.path.join(REF, "人物_陈知白_钦差_全身.png"), "ref_chen_costume.png")
    prompt = ("把参考图1中的人物换上参考图2的服装：玄黑缎面钦差袍，胸前与下摆金线绣四爪蟒纹，"
              "头戴黑色乌纱帽，腰束镶玉带，脚蹬黑皂靴。严格保留参考图1的面部五官、脸型、发型与体型身高，"
              "正面全身站姿，纯浅灰无缝背景，均匀柔光，定妆参考照，写实历史剧质感，无文字")
    outs, secs = F.edit(prompt, [a, b], width=768, height=1344, steps=4, prefix="toonflow/refs")
    o = list(outs.values())[0]["images"][0]
    src = os.path.join(COMFY_OUT, o.get("subfolder", ""), o["filename"])
    shutil.copy2(src, os.path.join(REF, name))
    print("ok", name, secs, "s ->", src)

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "t2i"):
        t2i()
    if only in ("all", "swap"):
        costume_swap()
    print("library:", len([f for f in os.listdir(REF) if f.endswith(".png")]), "files")
