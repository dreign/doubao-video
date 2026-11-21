import json, io

data = json.load(open("shots.json", encoding="utf-8"))
meta = ["第01集《放榜日》", "第02集《叫城》", "第03集《官腔》"]
idea = {
 "01": "昨天是会元，今天是死囚——他在石狮旁跪了一夜，然后捡到一件钦差服。",
 "02": "穿着蟒袍、踩着草鞋的人叫开了城门；一张通缉令、一个卖糖小童，雅间里一封湿墨帖子等着他。",
 "03": "一间雅间、一夜官腔；红衣女子三句话削掉他三处破绽，最后把答案塞进他手里。",
}

out = io.StringIO()
out.write("# 《假钦差》第 01–03 集 成片脚本（短剧版）\n\n")
out.write("> 竖屏 9:16 ｜ 每集 18 镜 × 5 秒（H3 实际 5.17 秒/段）≈ 93 秒 ｜ 768×1344 ｜ 24fps ｜ 冷调纪实 + 明代质感\n")
out.write("> 人物依据参考库定型稿：陈知白 22 岁清瘦书生，青布束发；后期乌纱 + 玄黑金线四爪蟒纹钦差服。\n")
out.write("> 本表由 `shots.json` 生成，与 `ep01_shots.py` / `ep02_shots.py` / `ep03_shots.py` 同源；改镜表后重跑本文即同步。\n\n---\n")
out.write("## 全集总览\n\n")
out.write("| 集 | 镜数 | 单片时长 | 台词句数 | 钩子 |\n|---|---|---|---|---|\n")
for ep in ("01", "02", "03"):
    shots = [s for s in data["shots"] if s["ep"] == ep]
    lines = [s for s in shots if s["line"].strip()]
    hook = lines[-1]["line"] if lines else ""
    out.write(f"| {meta[int(ep)-1]} | {len(shots)} | {round(len(shots)*5.17,2)} 秒 | {len(lines)} | {hook} |\n")

for ep in ("01", "02", "03"):
    shots = [s for s in data["shots"] if s["ep"] == ep]
    out.write("\n---\n\n## " + meta[int(ep)-1] + "\n\n")
    out.write("**一句话**：" + idea[ep] + "\n\n")
    out.write("| 镜 | 时长 | 画面节拍 | 台词 / 屏显 | 声音 |\n|---|---|---|---|---|\n")
    for s in shots:
        line = s["line"].strip().replace("\n", " ") or "—"
        snd = (s["snd"] or "").strip().replace("\n", " ") or "—"
        out.write(f"| {s['id'][1:]} | 5s | {s['title']} | {line} | {snd} |\n")
    lines = [s["line"].strip() for s in shots if s["line"].strip()]
    if lines:
        out.write("\n**钩子**：" + lines[-1] + "\n")

out.write("\n---\n\n## 制作规格\n\n")
out.write("- 图片：Z-Image-Turbo 4 步，768×1344，参考图锁形（人物定型稿 + 场景板 + 道具板），约 20–40 秒/张。\n")
out.write("- 视频：MiniMax H3（`h3_i2v_turbo`）以分镜图为首帧，5 秒 = 124 帧，约 4.3 分钟/段。\n")
out.write("- 字幕：ASS，PlayResX 768 / PlayResY 1344，微软雅黑 52 号，白字黑边，MarginV 100；时间轴按每段真实 5.17 秒累加。\n")
out.write("- 成片：18 段拼接 + 前 3 秒集标题 + 结尾淡出（淡出点取拼接产物真实时长）。\n")
out.write("- 单镜字幕一律 ≤14 字，长句在剧本阶段就压缩，避免压字。\n")

open("01_剧本/第01-03集成片脚本.md", "w", encoding="utf-8").write(out.getvalue())
print("wrote", len(out.getvalue()), "chars")
