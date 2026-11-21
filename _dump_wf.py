import json, os
COMFY = r"C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI"
WF = os.path.join(COMFY, "user", "default", "workflows")


def dump(name, keep=None):
    p = os.path.join(WF, name)
    d = json.load(open(p, encoding="utf-8-sig"))
    print("\n######", name, "| nodes:", len(d.get("nodes", [])))
    for n in d.get("nodes", []):
        t = n.get("type")
        if keep and t not in keep:
            continue
        w = n.get("widgets_values")
        if isinstance(w, dict):
            w = {k: v for k, v in w.items() if isinstance(v, (int, float, str)) and len(str(v)) < 60}
        elif isinstance(w, list):
            w = [x for x in w if isinstance(x, (int, float, str)) and len(str(x)) < 60]
        title = n.get("title") or ""
        print(" -", t, "|", title[:40], "|", json.dumps(w, ensure_ascii=False)[:220])


dump("（实验性）Minimax H3全能参考   二采工作流（实验性）.json")
dump("video_minimax_h3_r2v.json", keep={"KSamplerSelect", "BasicScheduler", "MiniMaxH3ReferenceToVideo", "MiniMaxH3LatentUpscaleCombined", "LoraLoaderModelOnly", "UNETLoader", "INTConstant", "PrimitiveInt", "ComfySwitchNode", "CLIPLoader", "VAELoader", "SamplerCustomAdvanced", "KSampler", "ResolutionSelector"})
dump("▶▷MiniMaxH3-加速视频流整合.json", keep={"UNETLoader", "UnetLoaderGGUF", "CLIPLoader", "CLIPLoaderGGUF", "MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo", "MiniMaxH3LatentUpscaleCombined", "LoraLoaderModelOnly", "BasicScheduler", "SamplerCustomAdvanced", "ResolutionSelector", "KSamplerSelect"})
