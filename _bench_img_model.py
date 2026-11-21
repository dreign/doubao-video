"""对比 Flux2-Klein 9b / 4b-distilled 在同一个分镜提示词上的耗时与形准。
只出图，不动产出目录，结果落 06_素材/check_model/。
"""
import os, sys, time, json, shutil
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import flux_edit as F
import ep01_shots as E

ROOT = r"D:\AAA\text\假钦差\短剧"
REF = os.path.join(ROOT, "06_素材", "参考库")
OUT = os.path.join(ROOT, "06_素材", "check_model")
COMFY_OUT = r"C:\Users\Administrator\ComfyUI-Shared\output"
os.makedirs(OUT, exist_ok=True)

CFG = {
    "9b": dict(unet="flux-2-klein-9b-fp8.safetensors", clip="qwen_3_8b_fp8mixed.safetensors",
               vae="full_encoder_small_decoder.safetensors", steps=4),
    "4b": dict(unet="flux-2-klein-4b-fp8.safetensors", clip="qwen_3_4b.safetensors",
               vae="flux2-vae.safetensors", steps=4),
    "4b_s8": dict(unet="flux-2-klein-4b-fp8.safetensors", clip="qwen_3_4b.safetensors",
                  vae="flux2-vae.safetensors", steps=8),
}
KEY = sys.argv[1] if len(sys.argv) > 1 else "01-s10"


def prompt_for(key):
    refs = E.REF[key]
    role = {"人物": "人物（严格保持面部五官、脸型、发型、体型与服装形制）",
            "场景": "场景（严格保持建筑形制、材质、陈设与光线方向）",
            "物品": "物品（严格保持形制、纹样、材质与比例）"}
    lines = [f"参考图{i}提供{role[r]}" for i, (_, r) in enumerate(refs, 1)]
    p = "；".join(lines) + "。"
    p += f"画面构图：{E.COMP[key]}。光线与色调：{E.LIGHT[key]}。"
    p += "电影感写实，35mm 胶片颗粒，浅景深，竖构图 9:16，画面中不出现任何文字、字幕、水印。"
    p += "只保留参考图中的主体特征，不要把参考图的背景、站姿、构图原样搬过来。"
    p += "画面中人物为唯一主角，不要出现重复的人或多余的人物。"
    return p, [n for n, _ in refs]


def edit_with(cfg, prompt, refs, prefix):
    import json as js, uuid, urllib.request
    ups = [F.upload(os.path.join(REF, n), n) for n in refs]
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": cfg["unet"], "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": cfg["clip"], "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": cfg["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": 768, "height": 1344, "batch_size": 1}},
        "8": {"class_type": "RandomNoise", "inputs": {"noise_seed": 20261122}},
        "9": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "10": {"class_type": "Flux2Scheduler", "inputs": {"steps": cfg["steps"], "width": 768, "height": 1344}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": prefix}},
    }
    positive = ["4", 0]
    for i, name in enumerate(ups):
        graph[f"r{i}l"] = {"class_type": "LoadImage", "inputs": {"image": name}}
        graph[f"r{i}s"] = {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": [f"r{i}l", 0], "upscale_method": "lanczos", "megapixels": 1, "resolution_steps": 1}}
        graph[f"r{i}e"] = {"class_type": "VAEEncode", "inputs": {"pixels": [f"r{i}s", 0], "vae": ["3", 0]}}
        graph[f"rl{i}"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": positive, "latent": [f"r{i}e", 0]}}
        positive = [f"rl{i}", 0]
    graph["11"] = {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": positive, "negative": ["5", 0], "cfg": 1}}
    graph["12"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["8", 0], "guider": ["11", 0], "sampler": ["9", 0], "sigmas": ["10", 0], "latent_image": ["6", 0]}}
    req = urllib.request.Request(F.COMFY + "/prompt", data=js.dumps({"prompt": graph, "client_id": "bench" + uuid.uuid4().hex[:6]}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    r = js.load(urllib.request.urlopen(req, timeout=60))
    if r.get("node_errors"):
        raise RuntimeError(js.dumps(r["node_errors"], ensure_ascii=False)[:400])
    pid = r["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 900:
        time.sleep(3)
        h = js.load(urllib.request.urlopen(F.COMFY + "/history/" + pid, timeout=30))
        if pid in h:
            st = h[pid]["status"]
            if st["status_str"] == "error":
                raise RuntimeError(js.dumps(st["messages"], ensure_ascii=False)[:600])
            if st.get("completed"):
                o = h[pid]["outputs"]
                f = list(o.values())[0]["images"][0]
                src = os.path.join(COMFY_OUT, f.get("subfolder", ""), f["filename"])
                dst = os.path.join(OUT, f"{KEY}_{os.path.basename(prefix).split('/')[-1]}.png")
                shutil.copy2(src, dst)
                return dst, round(time.time() - t0, 1)
    raise TimeoutError("timeout")


if __name__ == "__main__":
    prompt, refs = prompt_for(KEY)
    for name, cfg in CFG.items():
        try:
            dst, secs = edit_with(cfg, prompt, refs, f"modelbench/{name}")
            print(f"{name:6s} {secs:6.1f}s -> {dst}", flush=True)
        except Exception as e:
            print(f"{name:6s} FAIL {e}", flush=True)
