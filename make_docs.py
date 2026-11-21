import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline as P
from shots_flux import R as REFMAP

ROOT = P.ROOT
DATA = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
SHOTS = DATA["shots"]
_DUR = {}
TITLES = {"01": "第01集 放榜日", "02": "第02集 叫城", "03": "第03集 官腔"}


def refs_of(s):
    return " + ".join(n.replace(".png", "") for n, _ in REFMAP.get(f"{s['ep']}-{s['id']}", []))


def first_line(h3):
    for ln in h3.splitlines():
        if ln.strip().startswith("【核心创意】"):
            continue
        if ln.strip().startswith("5 秒"):
            return ln.strip()
    return ""


def make_storyboard_md():
    out = ["# 《假钦差》第01–03集 分镜表", "",
           "口径：9:16 竖屏 768×1344，单镜 5 秒，H3 四段式提示词（完整版见 shots.json 的 h3 字段）。", "",
           "| 集 | 镜 | 时长 | 标题 | 锁定参考图 | 核心创意 | 台词 | 音效 |", "|---|---|---|---|---|---|---|---|"]
    for s in SHOTS:
        out.append(f"| {s['ep']} | {s['id']} | {s['dur']}s | {s['title']} | {refs_of(s)} | {first_line(s['h3']).replace('|', '/')} | {s['line'] or '—'} | {s['snd']} |")
    open(os.path.join(ROOT, "02_分镜", "分镜表.md"), "w", encoding="utf-8").write("\n".join(out))


def make_csv():
    import csv
    with open(os.path.join(ROOT, "02_分镜", "分镜表.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["集", "镜号", "时长(秒)", "标题", "锁定参考图", "H3完整提示词", "台词", "音效", "图片路径", "视频路径"])
        for s in SHOTS:
            w.writerow([s["ep"], s["id"], s["dur"], s["title"], refs_of(s), s["h3"], s["line"], s["snd"],
                        f"03_图片/第{s['ep']}集/{s['id']}.png", f"04_视频/第{s['ep']}集/{s['id']}.mp4"])


def clip_dur(ep, sid):
    """读真实片段时长（H3 出来是 5.17s，不是整 5s），字幕按真实时长累加，避免越到后面越错位。"""
    global _DUR
    key = (ep, sid)
    if key in _DUR:
        return _DUR[key]
    d = 5.0
    p = os.path.join(ROOT, "04_视频", f"第{ep}集", sid + ".mp4")
    if os.path.exists(p):
        try:
            import subprocess, imageio_ffmpeg, re
            r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", p], capture_output=True, text=True)
            m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
            if m:
                d = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        except Exception:
            pass
    _DUR[key] = d
    return d


def make_srt(ep):
    lines = []
    idx = 0
    t = 0.0
    for s in [x for x in SHOTS if x["ep"] == ep]:
        dur = clip_dur(ep, s["id"])
        if s["line"]:
            idx += 1
            lines.append(f"{idx}\n{ts(t + 0.4)} --> {ts(t + dur - 0.35)}\n{s['line']}\n")
        t += dur
    path = os.path.join(ROOT, "05_成片", f"第{ep}集_字幕.srt")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return path


def ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def ts_ass(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def make_ass(ep):
    """生成 ASS 字幕：白字黑边、底部居中，样式可控（避免 ffmpeg force_style 的逗号转义问题）。"""
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 768
PlayResY: 1344
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,52,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,2.5,1.2,2,40,40,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    rows = []
    t = 0.0
    for s in [x for x in SHOTS if x["ep"] == ep]:
        dur = clip_dur(ep, s["id"])
        if s["line"]:
            rows.append(f"Dialogue: 0,{ts_ass(t + 0.4)},{ts_ass(t + dur - 0.3)},Default,,0,0,0,,{s['line']}")
        t += dur
    path = os.path.join(ROOT, "05_成片", f"第{ep}集_字幕.ass")
    open(path, "w", encoding="utf-8").write(head + "\n".join(rows) + "\n")
    return path


if __name__ == "__main__":
    make_storyboard_md(); make_csv()
    for ep in ("01", "02", "03"):
        make_srt(ep)
        make_ass(ep)
    print("docs ok")

