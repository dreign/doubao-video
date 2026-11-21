import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline as P
import imageio_ffmpeg

ROOT = P.ROOT
FF = imageio_ffmpeg.get_ffmpeg_exe()
DATA = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
TITLES = {"01": "假钦差 · 第01集 放榜日", "02": "假钦差 · 第02集 叫城", "03": "假钦差 · 第03集 官腔"}
FONT = "C\\:/Windows/Fonts/msyh.ttc"
PROTO = "--proto" in sys.argv


def video_wh(path):
    """从 ffmpeg 输出里读第一条视频的宽高，用于原型版按比例缩放标题字号。"""
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r", (\d{2,5})x(\d{3,5})[,\s]", r.stderr)
    return (int(m.group(1)), int(m.group(2))) if m else (768, 1344)


def shots_of(ep):
    return [s for s in DATA["shots"] if s["ep"] == ep]


def build(ep, subtitle=True, proto=None):
    proto = PROTO if proto is None else proto
    base = "04_视频_原型" if proto else "04_视频"
    vdir = os.path.join(ROOT, base, f"第{ep}集")
    files = [os.path.join(vdir, s["id"] + ".mp4") for s in shots_of(ep)]
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        print(f"ep{ep} 缺 {len(missing)} 段，跳过"); return None
    lst = os.path.join(vdir, "concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in files:
            f.write("file '" + p.replace("\\", "/").replace("'", "'\\''") + "'\n")
    tmp = os.path.join(vdir, "ep_concat.mp4")
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", tmp], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print("concat 失败，尝试重编码", r.stderr[-400:])
        subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-r", "24", "-c:a", "aac", "-b:a", "192k", tmp], check=True)
    total = len(files) * 5.0
    # 用真实拼接时长算淡出点（H3 单段是 5.17s，不是整 5s，否则最后几秒会被淡出吃成黑屏）
    import re as _re
    _r = subprocess.run([FF, "-i", tmp], capture_output=True, text=True)
    _m = _re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", _r.stderr)
    if _m:
        total = int(_m.group(1)) * 3600 + int(_m.group(2)) * 60 + float(_m.group(3))
    filters = []
    # 集标题：前 3 秒居中；原型版按视频高度等比缩放字号与纵向位置
    vw, vh = video_wh(files[0])
    scale = vh / 1344.0
    filters.append(
        "drawtext=fontfile='%s':text='%s':fontcolor=white:fontsize=%d:x=(w-text_w)/2:y=%d:"
        "alpha=0.92:enable='lt(t,3)'" % (FONT, TITLES[ep], max(16, int(38 * scale)), max(40, int(160 * scale)))
    )
    srt = os.path.join(ROOT, "05_成片", f"第{ep}集_字幕.ass")
    if subtitle and os.path.exists(srt):
        srt_use = os.path.join(vdir, "sub.ass")
        open(srt_use, "w", encoding="utf-8").write(open(srt, encoding="utf-8").read())
        filters.append("subtitles=sub.ass")
    filters.append("fade=t=out:st=%.2f:d=0.4" % (total - 0.4))
    suffix = f"_原型{vh}" if proto else ""
    out = os.path.join(ROOT, "05_成片", f"第{ep}集_成片{suffix}.mp4")
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-vf", ",".join(filters),
                        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "copy", "-movflags", "+faststart", out], capture_output=True, text=True, cwd=vdir)
    if r.returncode != 0:
        print(f"ep{ep} 合成失败：", r.stderr[-600:]); return None
    print(f"ep{ep} 成片：", out, round(os.path.getsize(out) / 1048576, 2), "MB")
    return out

if __name__ == "__main__":
    eps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["01", "02", "03"]
    for ep in eps:
        build(ep)

