"""H3 多图参考（R2V）直连测试：3 张参考图 + turbo 4 步，384×672 原型档。
用途：判断"锁形"是否比"首帧图生视频"更稳，输出对比帧。
用法：python _bench_r2v.py 01-s16
"""
import json, os, sys, time, uuid, urllib.request, urllib.parse
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import h3_direct as H

ROOT = r"D:\AAA\text\假钦差\短剧"
REF = os.path.join(ROOT, "06_素材", "参考库")
OUT = os.path.join(ROOT, "06_素材", "check_r2v")
UNET = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VAE_V = "minimax_h3_video_vae_fp16.safetensors"
VAE_A = "minimax_h3_audio_vae_fp32.safetensors"
LORA = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"

KEY = sys.argv[1] if len(sys.argv) > 1 else "01-s16"
REFS = sys.argv[2:] or ["人物_陈知白_青衫_全身.png", "物品_蟒袍.png", "场景_乱葬岗.png"]
W, Hgt, FRAMES, STEPS = 384, 672, 124, 4

d = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
shot = next(s for s in d["shots"] if s["ep"] == "01" and s["id"] == KEY.split("-")[1])
prompt = shot["h3"].replace("@图片1", "<Picture 1>").replace("@图片2", "<Picture 2>").replace("@图片3", "<Picture 3>")
prompt = prompt.replace("【参考素材说明】", "【参考素材说明】\n用 <Picture 1> / <Picture 2> / <Picture 3> 指代三张参考图；" +
                        "把 <Picture 1> 的人物做成主角，服装取 <Picture 2>，环境取 <Picture 3>；")

ups = [H.upload(os.path.join(REF, n)) for n in REFS]

g = {
    "6": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
    "7": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": LORA, "strength_model": 0.75}},
    "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
    "11": {"class_type": "VAELoader", "inputs": {"vae_name": VAE_V}},
    "24": {"class_type": "VAELoader", "inputs": {"vae_name": VAE_A}},
    "104": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
        "clip": ["13", 0], "vae": ["11", 0], "audio_vae": ["24", 0], "prompt": prompt,
        "width": W, "height": Hgt, "length": FRAMES, "ref_image_size": "match"}},
    "16": {"class_type": "BasicGuider", "inputs": {"model": ["7", 0], "conditioning": ["104", 0]}},
    "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
    "9": {"class_type": "BasicScheduler", "inputs": {"model": ["7", 0], "scheduler": "simple", "steps": STEPS, "denoise": 1}},
    "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": 20261122}},
    "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0],
                                                             "sigmas": ["9", 0], "latent_image": ["104", 1]}},
    "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
    "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
    "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "fps": 24, "audio": ["23", 0]}},
    "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": "video/r2v", "format": "auto", "codec": "auto"}},
}
for i, name in enumerate(ups):
    g[f"r{i}"] = {"class_type": "LoadImage", "inputs": {"image": name}}
    g["104"]["inputs"][f"ref_images.ref_image_{i}"] = [f"r{i}", 0]

f, secs = H.run(g)
os.makedirs(OUT, exist_ok=True)
dest = os.path.join(OUT, f"{KEY}_r2v_{W}x{Hgt}.mp4")
H.download(f, dest)
print(f"{KEY} r2v {W}x{Hgt} steps={STEPS} {secs}s")
print(dest)
