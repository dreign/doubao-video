"""扫描本地 ComfyUI 工作流：用户工作流目录 + 各自定义节点自带示例。
输出结构化摘要（每条工作流用了哪些节点/模型/分辨率/步数）。
用法：python scan_workflows.py [--json out.json]
"""
import json, os, re, sys, collections

COMFY = r"C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI"
WF_DIR = os.path.join(COMFY, "user", "default", "workflows")
CN_DIR = os.path.join(COMFY, "custom_nodes")

MODEL_KEYS = {
    "unet_name": "UNET", "ckpt_name": "CKPT", "clip_name": "CLIP", "vae_name": "VAE",
    "lora_name": "LoRA", "model_name": "UPSCALE", "clip_name1": "CLIP", "clip_name2": "CLIP",
}
SIZE_KEYS = ("width", "height", "length", "frames", "resolution", "megapixels", "scale_by")


def walk_nodes(data, out):
    """兼容 UI 格式(nodes 数组) 与 API 格式(id->node) 两种。"""
    if isinstance(data, dict) and isinstance(data.get("nodes"), list):
        for n in data["nodes"]:
            out.append((n.get("type"), n.get("widgets_values") or [], n.get("title")))
        return "ui"
    if isinstance(data, dict) and "prompt" in data:
        return walk_nodes(data["prompt"], out)
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) and "class_type" in v:
                ins = v.get("inputs", {})
                vals = [x for x in ins.values() if isinstance(x, (int, float, str)) and not isinstance(x, bool)]
                out.append((v["class_type"], vals, None))
        return "api"
    return "unknown"


def scan(path):
    try:
        data = json.load(open(path, encoding="utf-8-sig"))
    except Exception as e:
        return {"file": os.path.basename(path), "error": str(e)[:80]}
    nodes = []
    fmt = walk_nodes(data, nodes)
    types = collections.Counter(t for t, _, _ in nodes if t)
    models = collections.defaultdict(set)
    nums = collections.defaultdict(set)
    for t, vals, _ in nodes:
        for v in vals:
            if isinstance(v, str) and v.lower().endswith((".safetensors", ".ckpt", ".pt", ".pth", ".gguf")):
                models["权重"].add(v)
    # 直接从原文抓 key:value 更稳
    text = json.dumps(data, ensure_ascii=False)
    for key, label in MODEL_KEYS.items():
        for m in re.findall(rf'"{key}"\s*:\s*"([^"]+)"', text):
            models[label].add(m)
    for key in ("steps", "cfg", "shift_video", "shift_audio", "noise_seed", "denoise", "audio_denoise"):
        vals = re.findall(rf'"{key}"\s*:\s*(\d+(?:\.\d+)?)', text)
        if vals:
            nums[key] = sorted(set(vals), key=float)[:6]
    sizes = re.findall(r'"(?:width|height)"\s*:\s*(\d+)', text)
    if sizes:
        nums["宽高出现值"] = sorted(set(sizes), key=int)[:8]
    return {
        "file": os.path.basename(path),
        "dir": "user" if os.path.dirname(path) == WF_DIR else os.path.basename(os.path.dirname(os.path.dirname(path))),
        "format": fmt,
        "node_count": len(nodes),
        "top_nodes": types.most_common(14),
        "models": {k: sorted(v) for k, v in models.items()},
        "nums": dict(nums),
        "has_h3": any("H3" in t or "Minimax" in t or "MiniMax" in t for t in types),
        "mtime": os.path.getmtime(path),
        "size": os.path.getsize(path),
    }


def main():
    items = []
    if os.path.isdir(WF_DIR):
        for f in sorted(os.listdir(WF_DIR)):
            if f.lower().endswith(".json"):
                items.append(scan(os.path.join(WF_DIR, f)))
    examples = []
    for pack in sorted(os.listdir(CN_DIR)) if os.path.isdir(CN_DIR) else []:
        pdir = os.path.join(CN_DIR, pack)
        if not os.path.isdir(pdir):
            continue
        for root, _, files in os.walk(pdir):
            if os.path.basename(root).lower() in ("example_workflows", "examples", "workflow", "workflows"):
                for f in files:
                    if f.lower().endswith(".json"):
                        examples.append(os.path.join(root, f))
    ex_items = [scan(p) for p in examples]
    out = {"user_workflows": items, "pack_examples": ex_items}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--json" in sys.argv:
        dest = sys.argv[sys.argv.index("--json") + 1]
        json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved", dest, file=sys.stderr)


if __name__ == "__main__":
    main()
