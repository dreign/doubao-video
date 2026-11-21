"""生成后端封装。

默认 H3_BACKEND=direct：直接打 ComfyUI（127.0.0.1:8188），不经过 Toonflow。
设 H3_BACKEND=toonflow 可切回原来的 /api/ai/media/generate 路径。

对外接口保持不变（gen_image / gen_video / copy_out / ROOT / WORKSPACE），
上层 batch.py、refs.py、_newrefs*.py 无需改动。
"""
import json, os, random, re, shutil, sys, time, urllib.parse, urllib.request, uuid

ROOT = r"D:\AAA\text\假钦差\短剧"
WORKSPACE = r"D:\github\Toonflow-app\data\workspaces\myProject"
TOONFLOW = "http://127.0.0.1:3000"
COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
BACKEND = os.environ.get("H3_BACKEND", "direct").lower()
TMP = os.path.join(ROOT, "_tmp_out")

TURBO_LORA = "minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors"


# ---------------------------------------------------------------- 通用
def copy_out(rel_path, dest):
    """rel_path 可以是工作区相对路径（toonflow 模式）或绝对路径（direct 模式）。"""
    src = rel_path if os.path.isabs(rel_path) else os.path.join(WORKSPACE, rel_path.replace("/", os.sep))
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def post(path, payload, timeout=1200):
    """Toonflow 后端专用。"""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(TOONFLOW + path, data=data,
                                 headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------------------------------------------------------------- ComfyUI 直连
def _cpost(path, payload, timeout=120):
    req = urllib.request.Request(COMFY + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _upload(path):
    boundary = "----py" + uuid.uuid4().hex
    name = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\n'
            f'Content-Type: image/png\r\n\r\n').encode() + data + \
           (f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
            f'--{boundary}--\r\n').encode()
    req = urllib.request.Request(COMFY + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())["name"]


def _wait(pid, timeout=2400):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30) as r:
                hist = json.loads(r.read().decode())
        except Exception:
            continue
        if pid in hist:
            e = hist[pid]
            st = e.get("status", {}) or {}
            if st.get("status_str") == "error":
                msgs = [m[1] for m in st.get("messages", []) if m and len(m) > 1]
                raise RuntimeError("ComfyUI 执行失败：" + str(msgs)[:800])
            for node in (e.get("outputs") or {}).values():
                for key in ("images", "videos", "gifs"):
                    fs = node.get(key) or []
                    if fs:
                        return fs[0], time.time() - t0
    raise TimeoutError("ComfyUI 超时")


def _download(f, dest):
    q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""),
                                "type": f.get("type", "output")})
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(f"{COMFY}/view?{q}", timeout=300) as r, open(dest, "wb") as w:
        w.write(r.read())
    return dest


def _snap32(v):
    return max(32, int(round(v / 32.0)) * 32)


def _wh(size):
    m = re.search(r"(\d+)\s*[xX×]\s*(\d+)", str(size))
    if not m:
        return 768, 1344
    return _snap32(int(m.group(1))), _snap32(int(m.group(2)))


def h3_frames(seconds, fps=24):
    """H3 帧数：round(sec*fps) 后吸附到 17k+5 网格（124 = ~5s）。"""
    f = int(round(float(seconds) * fps))
    k = max(0, (f - 5 + 16) // 17)
    return 17 * k + 5


def zimage_graph(prompt, w, h, steps=8, seed=None):
    seed = seed if seed is not None else random.randint(1, 10 ** 12)
    return {
        "30": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "29": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "28": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["28", 0], "shift": 3}},
        "27": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["30", 0]}},
        "33": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["27", 0]}},
        "13": {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"model": ["11", 0], "seed": seed, "steps": steps, "cfg": 1,
                                                   "sampler_name": "res_multistep", "scheduler": "simple",
                                                   "positive": ["27", 0], "negative": ["33", 0],
                                                   "latent_image": ["13", 0], "denoise": 1}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["29", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "toonflow/zimage"}},
    }


def h3_graph(prompt, w, h, frames, first_name, steps=4, seed=None, turbo=True, last_name=None):
    seed = seed if seed is not None else random.randint(1, 10 ** 9)
    g = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt,
                                                                  "width": w, "height": h, "length": frames}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["7", 0], "conditioning": ["104", 0]}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["7", 0], "scheduler": "simple", "steps": steps, "denoise": 1}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0],
                                                                "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "114": {"class_type": "LoadImage", "inputs": {"image": first_name}},
    }
    if not turbo:
        g["16"]["inputs"]["model"] = ["6", 0]
        g["9"]["inputs"]["model"] = ["6", 0]
    else:
        g["7"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": TURBO_LORA, "strength_model": 0.75}}
    if last_name:
        g["115"] = {"class_type": "LoadImage", "inputs": {"image": last_name}}
        g["104"]["inputs"]["last_frame"] = ["115", 0]
    g["104"]["inputs"]["first_frame"] = ["114", 0]
    g["23"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}}
    g["91"] = {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "fps": 24, "audio": ["23", 0]}}
    g["92"] = {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": "video/toonflow", "format": "auto", "codec": "auto"}}
    return g


def _run_graph(graph, suffix):
    os.makedirs(TMP, exist_ok=True)
    pid = _cpost("/prompt", {"prompt": graph, "client_id": "pipeline-" + uuid.uuid4().hex[:8]})["prompt_id"]
    f, secs = _wait(pid)
    dest = os.path.join(TMP, f"{time.strftime('%H%M%S')}_{uuid.uuid4().hex[:6]}{suffix}")
    _download(f, dest)
    return {"path": dest, "secs": round(secs, 1), "prompt_id": pid}


# ---------------------------------------------------------------- 对外接口
def gen_image(prompt, size="768x1344", ratio="9:16", seed_note="", steps=8):
    if BACKEND != "direct":
        body = {"directory": WORKSPACE, "mediaType": "image", "providerId": "localComfy", "modelId": "zimage_t2i",
                "prompt": prompt, "ratio": ratio, "size": size}
        return post("/api/ai/media/generate", body, 400)
    w, h = _wh(size)
    r = _run_graph(zimage_graph(prompt, w, h, steps=steps), ".png")
    print(f"[zimage] {w}x{h} {r['secs']}s", flush=True)
    return {"data": [{"path": r["path"]}]}


def gen_video(prompt, first_frame_path, duration=5, resolution="768x1344", ratio="9:16",
              model="h3_i2v_turbo", last_frame_path=None):
    if BACKEND != "direct":
        body = {"directory": WORKSPACE, "mediaType": "video", "providerId": "localComfy", "modelId": model,
                "prompt": prompt, "mode": "singleImage", "ratio": ratio, "resolution": resolution,
                "duration": duration, "generateAudio": True,
                "firstFrame": {"path": first_frame_path, "mimeType": "image/png"}}
        return post("/api/ai/media/generate", body, 1800)
    src = first_frame_path if os.path.isabs(first_frame_path) else os.path.join(WORKSPACE, first_frame_path.replace("/", os.sep))
    w, h = _wh(resolution)
    frames = h3_frames(duration)
    turbo = "turbo" in str(model).lower()
    steps = 4 if turbo else 20
    first = _upload(src)
    last = _upload(last_frame_path) if last_frame_path else None
    g = h3_graph(prompt, w, h, frames, first, steps=steps, turbo=turbo, last_name=last)
    r = _run_graph(g, ".mp4")
    print(f"[h3] {w}x{h} {frames}f steps={steps} {r['secs']}s", flush=True)
    return {"data": [{"path": r["path"]}]}


if __name__ == "__main__":
    print("backend:", BACKEND, "| comfy:", COMFY)
    t0 = time.time()
    r = gen_video("镜头缓慢推近，人物不动，尘埃浮动", os.path.join(ROOT, "03_图片", "第01集", "s01.png"),
                  duration=5, resolution="384x672", model="h3_i2v_turbo")
    out = copy_out(r["data"][0]["path"], os.path.join(ROOT, "06_素材", "bench", "pipeline_direct_384.mp4"))
    print("saved:", out, round(time.time() - t0, 1), "s")
