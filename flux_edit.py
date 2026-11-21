import json, os, sys, time, urllib.request, uuid
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
COMFY = "http://127.0.0.1:8188"

def upload(path, name=None):
    name = name or os.path.basename(path)
    boundary = "----toonflow" + uuid.uuid4().hex
    data = open(path, "rb").read()
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode()
    mid = (f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n"
           f"--{boundary}--\r\n").encode()
    body = head + data + mid
    req = urllib.request.Request(COMFY + "/upload/image", data=body,
                                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=60))["name"]

def edit(prompt, refs, width=768, height=1344, steps=4, prefix="toonflow/flux2edit"):
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux-2-klein-9b-fp8.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_8b_fp8mixed.safetensors", "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "full_encoder_small_decoder.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "8": {"class_type": "RandomNoise", "inputs": {"noise_seed": int(time.time() * 1000) % 999999999}},
        "9": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "10": {"class_type": "Flux2Scheduler", "inputs": {"steps": steps, "width": width, "height": height}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": prefix}},
    }
    positive = ["4", 0]
    for i, name in enumerate(refs):
        graph[f"r{i}l"] = {"class_type": "LoadImage", "inputs": {"image": name}}
        graph[f"r{i}s"] = {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": [f"r{i}l", 0], "upscale_method": "lanczos", "megapixels": 1, "resolution_steps": 1}}
        graph[f"r{i}e"] = {"class_type": "VAEEncode", "inputs": {"pixels": [f"r{i}s", 0], "vae": ["3", 0]}}
        graph[f"rl{i}"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": positive, "latent": [f"r{i}e", 0]}}
        positive = [f"rl{i}", 0]
    graph["11"] = {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": positive, "negative": ["5", 0], "cfg": 1}}
    graph["12"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["8", 0], "guider": ["11", 0], "sampler": ["9", 0], "sigmas": ["10", 0], "latent_image": ["6", 0]}}
    req = urllib.request.Request(COMFY + "/prompt", data=json.dumps({"prompt": graph, "client_id": "onf" + uuid.uuid4().hex}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    r = json.load(urllib.request.urlopen(req, timeout=60))
    if r.get("node_errors"):
        raise RuntimeError("node errors: " + json.dumps(r["node_errors"])[:500])
    pid = r["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 600:
        time.sleep(3)
        h = json.load(urllib.request.urlopen(COMFY + "/history/" + pid, timeout=30))
        if pid in h:
            e = h[pid]
            st = e["status"]
            if st["status_str"] == "error":
                raise RuntimeError("comfy error: " + json.dumps(st["messages"])[:800])
            if st.get("completed"):
                return e["outputs"], round(time.time() - t0, 1)
    raise TimeoutError("timeout")

if __name__ == "__main__":
    a = upload(r"D:\AAA\text\假钦差\陈知白 · 青衫穷秀才版.png", "ref_chen.png")
    b = upload(r"D:\AAA\text\假钦差\短剧\03_图片\第01集\s01.png", "ref_gongyuan.png")
    out, secs = edit("让参考图1中的书生跪在参考图2场景的石狮子旁边，清晨薄雾，仰拍低角度，人物占画面下半部，全身入画，冷灰蓝调电影感，竖构图", [a, b])
    print("done", secs, "s", json.dumps(out, ensure_ascii=False)[:300])
