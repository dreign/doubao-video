"""绕开 Toonflow 的 H3 直连封装：任意 32 倍数分辨率 / 首尾帧 / 步数，用于原型与高清实验。
用法：
  python h3_direct.py --image 03_图片\\第02集\\s01.png --w 512 --h 896 --prompt "..." --out 06_素材\\bench\\t512.mp4
"""
import argparse, json, os, time, urllib.request, urllib.parse, uuid

BASE = "http://127.0.0.1:8188"
TURBO_LORA = "minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors"


def post_json(path, payload, timeout=60):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def upload(path):
    boundary = "----h3" + uuid.uuid4().hex
    with open(path, "rb") as f:
        data = f.read()
    name = os.path.basename(path)
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\n'
            f'Content-Type: image/png\r\n\r\n').encode() + data + \
           f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(BASE + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())["name"]


def build(prompt, w, h, frames, fps, first, last=None, steps=4, seed=None, audio=True, turbo=True):
    seed = seed if seed is not None else 123456789
    g = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt,
                                                                  "width": w, "height": h, "length": frames, "first_frame": ["114", 0]}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["7", 0] if turbo else ["6", 0], "conditioning": ["104", 0]}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["7", 0] if turbo else ["6", 0], "scheduler": "simple",
                                                        "steps": steps, "denoise": 1}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0],
                                                                "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "114": {"class_type": "LoadImage", "inputs": {"image": first}},
    }
    if turbo:
        g["7"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": TURBO_LORA, "strength_model": 0.75}}
    if last:
        g["115"] = {"class_type": "LoadImage", "inputs": {"image": last}}
        g["104"]["inputs"]["last_frame"] = ["115", 0]
    vin = {"images": ["10", 0], "fps": fps}
    if audio:
        g["23"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}}
        vin["audio"] = ["23", 0]
    g["91"] = {"class_type": "CreateVideo", "inputs": vin}
    g["92"] = {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": "video/proto", "format": "auto", "codec": "auto"}}
    return g


def run(graph, wait_s=1800):
    pid = post_json("/prompt", {"prompt": graph, "client_id": "direct-" + uuid.uuid4().hex[:8]})["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < wait_s:
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"{BASE}/history/{pid}", timeout=30) as r:
                hist = json.loads(r.read().decode())
        except Exception:
            continue
        if pid in hist:
            e = hist[pid]
            st = e.get("status", {})
            if st.get("status_str") == "error" or st.get("completed") is False and st.get("status_str") == "error":
                raise RuntimeError(json.dumps(st, ensure_ascii=False)[:800])
            outs = e.get("outputs", {})
            for node in outs.values():
                for key in ("images", "videos", "gifs"):
                    for f in node.get(key, []):
                        return f, round(time.time() - t0, 1)
    raise TimeoutError("超时")


def download(f, dest):
    q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(f"{BASE}/view?{q}", timeout=300) as r, open(dest, "wb") as w:
        w.write(r.read())
    return dest


if __name__ == "__main__":
    import urllib.parse
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--last", default="")
    ap.add_argument("--w", type=int, default=768)
    ap.add_argument("--h", type=int, default=1344)
    ap.add_argument("--frames", type=int, default=124)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--prompt", default="镜头缓慢推近，人物不动，尘埃浮动")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    a.w = (a.w // 32) * 32
    a.h = (a.h // 32) * 32
    first = upload(a.image)
    last = upload(a.last) if a.last else None
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.image)), f"bench_{a.w}x{a.h}.mp4")
    f, ms = run(build(a.prompt, a.w, a.h, a.frames, a.fps, first, last, a.steps))
    print(f"{a.w}x{a.h} steps={a.steps} elapsed={ms}s")
    print(download(f, out))
