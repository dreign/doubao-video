# 本机 ComfyUI 环境与权重清单

本仓库所有脚本都跑在这一套本地环境上。换机器复现时，先对齐这一节，再看 `00_全链路总览.md`。

## 1. 运行环境

| 项 | 值 |
|---|---|
| 系统 | Windows 11（本机执行环境名 DREIGN） |
| ComfyUI | 0.46.2，`http://127.0.0.1:8188` |
| 安装路径 | `C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI` |
| ComfyUI venv python | `C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe`（`make_docs.py` / `assemble.py` 必须用它，系统 python 缺 PIL / imageio_ffmpeg） |
| Python | 3.13.12 |
| torch | 2.12.1+cu130 |
| GPU | RTX 5080 Laptop 16GB |
| 输出目录 | `C:\Users\Administrator\ComfyUI-Shared\output`（`shots_flux.py` 从这里取图） |

**启动必须带一个环境变量**，否则 Desktop 控制台抓到无效句柄、任务全部 `Errno 22`：

```powershell
$env:TQDM_DISABLE = '1'
```

## 2. 权重根目录

`D:\ai\models`（`C:\Users\Administrator\ComfyUI-Shared\models` 只是空骨架，靠 junction 指过来）。

## 3. 本项目实际用到的权重

| 用途 | 文件 | 放置目录 | 大小 |
|---|---|---|---|
| 分镜图（主力） | `flux-2-klein-9b-fp8.safetensors` | `diffusion_models` | 8.8 GB |
| 分镜图（快速档） | `z_image_turbo_bf16.safetensors` | `diffusion_models` | 11.5 GB |
| z-image 文本编码 | `qwen_3_4b`（CLIPLoader，type=lumina2） | `text_encoders` | — |
| z-image VAE | `ae.safetensors` | `vae` | 320 MB |
| H3 视频（首尾帧 I2V） | `minimax_h3_fl2va_int8_convrot.safetensors` | `diffusion_models` | 31.7 GB |
| H3 视频（参考图 R2V） | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `diffusion_models` | 19.5 GB |
| H3 加速 LoRA（4 步 turbo） | `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` | `loras` | 1.8 GB |
| H3 加速 LoRA（R2V 4 步） | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | `loras` | 1.8 GB |

## 4. 直连约束（踩过的坑，别重复）

- 宽高必须是 **32 的倍数**（`720×1280` 必失败，根因是 Toonflow 的 `round16`）。
- 5 秒 = **124 帧**（17k+5 吸附）；`MiniMaxH3ImageToVideo` 支持 `first_frame` / `last_frame`。
- turbo 参数：`lightx2v 4step @0.75`。
- 一采 0.4MP 后二采约 1.5 倍；**不要**从 `768×1344` 二采到 `1024×1792`（1.8MP 必 OOM）。

## 5. 可选：Toonflow-app

早期版本经 `:3000` 中转调 ComfyUI。现在 `pipeline.py` 默认直连，`H3_BACKEND=toonflow` 才回退，Toonflow 可不再启动。

## 6. 工作流快照

`_comfyui/workflows/` 下是 ComfyUI `user\default\workflows` 的 17 份 JSON 快照，判读见 `01_ComfyUI工作流清单.md`。
其中 `▶▷MiniMaxH3-加速视频流整合` 缺 GGUF 权重，本机跑不了。
