"""生成第01集 v2 镜表（ep01_shots.py）：台词具体化 + s08 塞纸留假线索 + s10 指认青衫。
读旧模块做锚点替换，避免手写 18 条长提示词出错。
"""
import importlib.util as u
import json, os, sys

ROOT = r"D:\AAA\text\假钦差\短剧"
sys.path.insert(0, ROOT)
_spec = u.spec_from_file_location("ep01_v1", r"D:\AAA\text\假钦差\短剧\06_素材\ep01_shots_v1_备份.py")
E = u.module_from_spec(_spec); _spec.loader.exec_module(E)

# sid: (字幕行, h3 里的台词句)
DIA = {
    "01": ("会元陈知白，着即通缉", "今科会元陈知白，夹带舞弊，着即通缉！"),
    "02": ("三天前，我还在这榜下笑", "三天前，我在这榜下，笑了半个时辰。"),
    "03": ("三年寒窑，砚台结冰", "三年寒窑，冬天砚台结冰，我哈着气写。"),
    "04": ("墙里是梦，墙外是我这种人", "墙里头是读书人的梦。墙外头，是我这种人。"),
    "06": ("连画都懒得画准", "连画都懒得画准。他们要的不是我，是我的死。"),
    "07": ("考场门都没进，成了逃犯", "考场门都没进，就成了逃犯。"),
    "08": ("你们要这张纸，拿去", "你们要这张纸，拿去。"),
    "10": ("那件青衫，是有人送来的", "那件青衫……是有人送来的。"),
    "15": ("断口是刀切的", "断口是刀切的——有人比我更需要它藏起来。"),
    "16": ("大小正好，像给我做的", "大小……正好。像给我做的。"),
}

S08_IMAGE = ("中景贴地，青石窄巷的墙根，二十二岁书生陈知白半跪着，把一张卷起的皱黄纸塞进两砖之间的缝隙，"
             "掌心在砖面上抹出一道血痕，另一只手撑地，粗麻青灰长衫下摆沾泥，两侧灰砖墙夹出纵深，冷调，35mm胶片颗粒，竖构图")
S08_VIDEO = "他跌倒后跪起半身，把黄纸卷成一卷塞进墙根的砖缝，掌心在砖上抹出一道血痕，随即撑地起身跑开，镜头贴地跟拍晃动。"
S08_SND = "跌倒、塞纸、脚步"
S08_H3 = (
    "【参考素材说明】\n"
    "@图片1：首帧，严格保持人物的脸型五官、发型、体型与青灰粗麻长衫的形制；@图片2：青石窄巷的砖墙苔痕与纵深；"
    "@图片3：皱黄纸的纸色、褶皱与卷曲形态。不参考图片中的任何文字、字幕与水印。\n\n"
    "【核心创意】\n"
    "5 秒，9:16 竖屏。青石窄巷墙根，摔了一跤的逃犯把那张「罪证」塞进砖缝，留下一条会被追错的线。"
    "写实历史剧情片质感，明代背景，冷灰蓝低饱和，35mm 胶片颗粒，浅景深，贴地冷光。\n\n"
    "【画面过程说明】\n"
    "Shot 1（0—2 秒）：中景贴地，他踉跄奔逃时脚下一滑，重重摔在湿滑的青石板上，掌心擦过地面渗出血丝，黄纸仍攥在手里。"
    "镜头：手持晃动，贴地跟拍。\n"
    "Shot 2（2—5 秒）：他跪起半身，把那张皱黄纸卷成一卷塞进墙根两砖之间的缝隙，掌心在砖面上抹了一下留下血痕，随即撑地起身往巷子深处跑。"
    "台词为他的喘息自语：“你们要这张纸，拿去。”。镜头：手持晃动，横移。\n"
    "环境音与动作音效：身体砸在石板上的闷响，纸被卷起的沙沙声，砖面被血手抹过的涩响，急促脚步。\n\n"
    "【整体要求补充】\n"
    "画面中只有他一个跌倒又起身的人，不出现第二个人或追兵，不出现任何可辨认字样与水印；"
    "砖缝里的纸必须始终卡在原处、不得卷出、翻面或被风吹走；人物服装与巷子结构保持与首帧一致。非叙事性音乐：N/A。"
)

S10_ANCHOR = "草叶刮过耳侧。镜头：固定机位。"
S10_INSERT = ("草叶刮过耳侧。台词为他的气音独白：“那件青衫……是有人送来的。”。镜头：固定机位。")

out_ref = dict(E.REF)
out_ref["01-s08"] = [("人物_陈知白_青衫_全身.png", "人物"), ("场景_青石窄巷.png", "场景"), ("物品_告示红榜.png", "物品")]
out_comp = dict(E.COMP)
out_comp["01-s08"] = ("中景贴地，青石窄巷墙根，人物半跪着把一张卷起的皱黄纸塞进两砖之间的缝隙，"
                      "掌心在砖面上抹出一道血痕，另一只手撑地，两侧灰砖墙夹出纵深，冷调")
out_light = dict(E.LIGHT)
out_light["01-s08"] = "贴地冷光，湿石板反出微光，砖面血痕发暗"

shots = []
for ep, sid, title, image, video, line, snd, h3 in E.SHOTS:
    key = sid[1:]
    if sid == "s08":
        image, video, snd, h3 = S08_IMAGE, S08_VIDEO, S08_SND, S08_H3
    if sid == "s10":
        assert h3.count(S10_ANCHOR) == 1, "s10 锚点不唯一"
        h3 = h3.replace(S10_ANCHOR, S10_INSERT)
    if key in DIA:
        new_line, new_sentence = DIA[key]
        if line and h3.count(line) == 1:
            h3 = h3.replace(line, new_sentence)
        elif sid == "s01":
            anchor = "远处宣读声带回声"
            assert h3.count(anchor) == 1, "s01 宣读锚点不唯一"
            h3 = h3.replace(anchor, "远处宣读声带回声，画外宣读：“%s”" % new_sentence)
        line = new_line
    shots.append((ep, sid, title, image, video, line, snd, h3))

def q(s):
    return json.dumps(s, ensure_ascii=False)

lines = []
lines.append('"""第01集（短剧版 18 拍，v2 台词强化版）镜表 + 参考图映射 + 构图/光线表。')
lines.append("shots.json 的 ep01 段与 shots_flux.py 的 ep01 映射都由本文件生成，保证三处一致。")
lines.append("v2 改动：台词具体化；s08 改为把黄纸塞进砖缝留假线索；s10 补「那件青衫是有人送来的」独白。")
lines.append('"""')
lines.append("")
lines.append("STYLE = " + q(E.STYLE))
lines.append("")
lines.append("REF = {")
for k in sorted(out_ref):
    items = ", ".join("(%s, %s)" % (q(a), q(b)) for a, b in out_ref[k])
    lines.append("%s: [%s]," % (q(k), items))
lines.append("}")
lines.append("")
lines.append("COMP = {")
for k in sorted(out_comp):
    lines.append("%s: %s," % (q(k), q(out_comp[k])))
lines.append("}")
lines.append("")
lines.append("LIGHT = {")
for k in sorted(out_light):
    lines.append("%s: %s," % (q(k), q(out_light[k])))
lines.append("}")
lines.append("")
lines.append("# (ep, id, title, image, video, line, snd, h3)")
lines.append("SHOTS = [")
for ep, sid, title, image, video, line, snd, h3 in shots:
    lines.append("(%s, %s, %s," % (q(ep), q(sid), q(title)))
    lines.append(" " + q(image) + ",")
    lines.append(" " + q(video) + ",")
    lines.append(" " + q(line) + ", " + q(snd) + ",")
    lines.append(" " + q(h3) + "),")
    lines.append("")
lines.append("]")
open(os.path.join(ROOT, "ep01_shots.py"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

print("written, shots:", len(shots))
for s in shots:
    print(s[1], "|", s[5], "|", s[2])


