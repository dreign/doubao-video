import json, os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline as P

DATA = json.load(open(os.path.join(P.ROOT, "shots.json"), encoding="utf-8"))
LOG = os.path.join(P.ROOT, "progress.json")
UP = os.path.join(P.WORKSPACE, "uploads")

# 原型模式：低分辨率重跑，产物落独立目录，不覆盖正式成片素材
PROTO = ("--proto" in sys.argv) or os.environ.get("VID_PROTO") == "1"
PROTO_RES = os.environ.get("PROTO_RES", "384x672")
RES = PROTO_RES if PROTO else "768x1344"


def load_log():
    return json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else {}


def save_log(log):
    json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def ep_dir(ep):
    return os.path.join(P.ROOT, "03_图片", f"第{ep}集")


def vid_dir(ep):
    base = "04_视频_原型" if PROTO else "04_视频"
    return os.path.join(P.ROOT, base, f"第{ep}集")


def stage_first_frame(ep, sid, img_path):
    """把新分镜图放进工作区，返回可给 provider 的相对路径。"""
    os.makedirs(UP, exist_ok=True)
    name = f"ff_ep{ep}_{sid}.png"
    shutil.copy2(img_path, os.path.join(UP, name))
    return f"uploads/{name}"


def run(stage="videos", only_ep=None):
    log = load_log()
    t0 = time.time()
    print(f"[vid] backend={P.BACKEND} res={RES} proto={PROTO}", flush=True)
    for shot in DATA["shots"]:
        if only_ep and shot["ep"] != only_ep:
            continue
        key = ("proto_" if PROTO else "") + f"ep{shot['ep']}_{shot['id']}"
        rec = log.setdefault(key, {})
        img_path = os.path.join(ep_dir(shot["ep"]), f"{shot['id']}.png")
        vid_path = os.path.join(vid_dir(shot["ep"]), f"{shot['id']}.mp4")
        if not os.path.exists(img_path):
            print(f"[vid] {key} SKIP 无分镜图", flush=True); continue
        if rec.get("video") and os.path.exists(vid_path):
            print(f"[vid] {key} skip done", flush=True); continue
        try:
            rel = stage_first_frame(shot["ep"], shot["id"], img_path)
            prompt = shot.get("h3") or shot["video"]
            r = P.gen_video(prompt, rel, duration=5, resolution=RES, ratio="9:16",
                            model=DATA["meta"]["video_model"])
            P.copy_out(r["data"][0]["path"], vid_path)
            rec["video"] = r["data"][0]["path"]
            rec["video_at"] = time.strftime("%H:%M:%S")
            rec["res"] = RES
            rec.pop("video_error", None)
            save_log(log)
            print(f"[vid] {key} ok  {round((time.time()-t0)/60,1)}min", flush=True)
        except Exception as e:
            rec["video_error"] = str(e)[:300]
            save_log(log)
            print(f"[vid] {key} FAIL {e}", flush=True)
    print("done", stage, only_ep, round((time.time()-t0)/60, 1), "min", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    stage = args[0] if args else "videos"
    ep = args[1] if len(args) > 1 else None
    if ep in (None, "all"):
        ep = None
    if stage == "reset-videos":
        log = load_log()
        for k in log:
            for f in ("video", "video_at", "video_error"):
                log[k].pop(f, None)
        save_log(log)
        print("cleared video records")
        raise SystemExit(0)
    run(stage, ep)
