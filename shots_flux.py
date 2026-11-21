"""用参考图库锁定人物/场景/物品，逐镜重生成分镜图（Flux2-Klein 9B 多参考改图）。
用法：
  python shots_flux.py            全量（已有则跳过）
  python shots_flux.py 01         只做第01集
  python shots_flux.py 01 --force 强制重做
"""
import json, os, re, shutil, sys, time
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import flux_edit as F

ROOT = r"D:\AAA\text\假钦差\短剧"
REF = os.path.join(ROOT, "06_素材", "参考库")
OLD = os.path.join(ROOT, "06_素材", "旧_文生图版")
COMFY_OUT = r"C:\Users\Administrator\ComfyUI-Shared\output"
LOG = os.path.join(ROOT, "flux_shots.json")

ROLE = {
    "人物": "人物（唯一主角，严格保持面部五官、脸型、发型、体型与服装形制）",
    "场景": "场景（严格保持建筑形制、材质、陈设与光线方向）",
    "物品": "物品（严格保持形制、纹样、材质与比例）",
}

R = {
"01-s01": [("场景_贡院.png", "场景")],
"01-s02": [("人物_陈知白_青衫_全身.png", "人物"), ("场景_贡院.png", "场景")],
"01-s03": [("物品_告示红榜.png", "物品"), ("场景_贡院.png", "场景")],
"01-s04": [("人物_陈知白_青衫_面部.png", "人物"), ("场景_贡院.png", "场景")],
"01-s05": [("物品_告示红榜.png", "物品"), ("场景_贡院.png", "场景")],
"01-s06": [("人物_玄甲禁军.png", "人物"), ("场景_青石窄巷.png", "场景")],
"01-s07": [("人物_陈知白_青衫_全身.png", "人物"), ("场景_青石窄巷.png", "场景")],
"01-s08": [("人物_陈知白_青衫_全身.png", "人物"), ("场景_乱葬岗.png", "场景")],
"01-s09": [("人物_陈知白_青衫_全身.png", "人物"), ("场景_乱葬岗.png", "场景"), ("物品_蟒袍.png", "物品")],
}

COMP = {
"01-s01": "全景，晨雾中的贡院朱红宫墙与一对巨大石狮，青石台阶结霜，右侧一盏昏黄灯笼，画面无人",
"01-s02": "俯拍全景，人物跪在石狮旁，身形极小，双手攥着一张皱黄纸，地面积霜",
"01-s03": "大特写，一双冻红的手攥着皱巴巴的黄纸，纸边毛糙，墨迹晕开，背景虚化的结霜石板与石狮底座",
"01-s04": "中近景仰拍，人物跪地抬头望向高耸的朱红宫墙，眼眶发红，不流泪",
"01-s05": "特写，朱红墙上一张朱砂红榜，一行墨迹被浓黑划穿，浆糊未干泛白，纸角被风掀起",
"01-s06": "低角度广角，一队禁军骑黑马自晨雾中疾驰冲出，马蹄扬起尘雾，最前一人高举一张通缉画像",
"01-s07": "中景，人物跌倒在狭窄青石巷里，一手撑住湿滑石板，掌心擦破渗血，另一手仍攥着黄纸",
"01-s08": "全景，人物翻过半塌土墙落在荒草丛中，几只乌鸦从枯树惊起飞向灰白天际",
"01-s09": "俯拍特写，土坑里一只沾满泥的手扯出一角玄黑缎面金线蟒袍，旁边散着碎骨与破布",
}

LIGHT = {k: "冷灰蓝晨雾，低饱和，光源来自画面左上方" for k in COMP}
LIGHT.update({
"01-s06": "晨雾透出的冷白光，逆光勾边，尘雾发亮",
})

# 第01集（短剧版 18 拍）的映射统一由 ep01_shots.py 提供
import ep01_shots as E01
R.update(E01.REF)
COMP.update(E01.COMP)
LIGHT.update(E01.LIGHT)

# 第02、03集（短剧版 18 拍）的映射同样由各自模块提供
import ep02_shots as E02
import ep03_shots as E03
for _k, _v in E02.REF.items():
    R["02-" + _k] = _v
for _k, _v in E02.COMP.items():
    COMP["02-" + _k] = _v
for _k, _v in E02.LIGHT.items():
    LIGHT["02-" + _k] = _v
for _k, _v in E03.REF.items():
    R["03-" + _k] = _v
for _k, _v in E03.COMP.items():
    COMP["03-" + _k] = _v
for _k, _v in E03.LIGHT.items():
    LIGHT["03-" + _k] = _v

STYLE_TAIL = "电影感写实，35mm 胶片颗粒，浅景深，竖构图 9:16，画面中不出现任何文字、字幕、水印"

# 速度档（4b distilled，热跑约 15s/张）只给远景、空镜、无面部大特写的镜用；
# 面部/近景/物品细节一律留在质量档（9b，热跑约 21-24s/张）。
FAST_KEYS = {
    # 只放"远景/俯拍/空镜且画面里没有文字载体（告示、画像、纸片）"的镜；
    # 实测 4b 会自作主张往纸上写假字、把构图往外景漂，物证镜一律 9b。
    "01-s02", "01-s06", "01-s09", "01-s10", "01-s11", "02-s02", "02-s10", "02-s12", "03-s02", "03-s18",
}


def build_prompt(key):
    refs = R[key]
    lines = []
    for i, (name, role) in enumerate(refs, 1):
        lines.append(f"参考图{i}提供{ROLE[role]}")
    p = "；".join(lines) + "。"
    p += f"画面构图：{COMP[key]}。"
    p += f"光线与色调：{LIGHT[key]}。"
    p += STYLE_TAIL + "。"
    p += "只保留参考图中的主体特征，不要把参考图的背景、站姿、构图原样搬过来。"
    if key != "01-s01":
        p += "画面中人物为唯一主角，不要出现重复的人或多余的人物。"
    return p

def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    keys = [a for a in only if re.fullmatch(r"\d\d-s\d\d", a)]
    eps = [a for a in only if a not in keys]
    force = "--force" in sys.argv
    FAST_ALL = "--fast" in sys.argv or os.environ.get("IMG_FAST") == "1"
    data = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else {}
    os.makedirs(OLD, exist_ok=True)
    cache = {}
    for s in data["shots"]:
        ep, sid = s["ep"], s["id"]
        key = f"{ep}-{sid}"
        if keys and key not in keys:
            continue
        if eps and ep not in eps:
            continue
        if key in log and not force:
            print("skip", key); continue
        for name, _ in R[key]:
            if name not in cache:
                cache[name] = F.upload(os.path.join(REF, name), name)
        t0 = time.time()
        fast = FAST_ALL or key in FAST_KEYS
        outs, _ = F.edit(build_prompt(key), [cache[n] for n, _ in R[key]],
                         width=768, height=1344, prefix=f"toonflow/fluxshots/{ep}_{sid}",
                         model="4b" if fast else "9b")
        o = list(outs.values())[0]["images"][0]
        src = os.path.join(COMFY_OUT, o.get("subfolder", ""), o["filename"])
        dst_dir = os.path.join(ROOT, "03_图片", f"第{ep}集")
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, f"{sid}.png")
        if os.path.exists(dst):
            shutil.copy2(dst, os.path.join(OLD, f"ep{ep}_{sid}.png"))
        shutil.copy2(src, dst)
        log[key] = {"src": src, "secs": round(time.time() - t0, 1), "model": "4b" if fast else "9b"}
        json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("ok", key, "4b" if fast else "9b", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
