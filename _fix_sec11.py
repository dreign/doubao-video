import io, os, re

PATH = r"D:\AAA\text\假钦差\短剧\00_全链路总览.md"
txt = open(PATH, encoding="utf-8").read()

NEW = """## 11. 优化建议（2026-11-21 实测 + 11-22 工作流复扫修订）

### 11.1 两档出片：原型 384×672（54 秒/段）→ 交付走"二采"而不是重新生成

H3 的 width/height 只要求 **32 的倍数**（节点：min 32 / step 32），768×1344 不是硬限制——720×1280 失败是因为 Toonflow 的 `round16` 把 720 圆成了 720（非 32 倍数）。

实测（同一张 02-s01 首帧、124 帧、turbo 4 步）：

| 分辨率 | 像素量 | 单段耗时 | 一集 18 段 | 用途 |
|---|---|---|---|---|
| 384×672 | 0.26 MP | **54 秒** | 约 16 分钟 | 过构图 / 验运镜 / 验台词长度 |
| 512×896 | 0.46 MP | **93 秒** | 约 28 分钟 | 二采的"一采底版" |
| 768×1344 | 1.03 MP | 约 260 秒 | 约 78 分钟 | 当前生产规格 |

原型阶段的正确用法不是"18 镜全跑一遍低清"，而是**只跑 5–7 个关键镜**：第 1 镜（钩子）、台词最密的镜、走位最复杂的镜、每集最后一镜。6 分钟就能判断这版镜表能不能用。

高清参照本机 `（实验性）Minimax H3全能参考 二采工作流` 的真实参数（社区已验证，别自己发明）：

- `BasicScheduler(beta, 20)` 出 20 步 sigma，`SplitSigmas(4)` 在第 4 步切开：**前 4 步一采 → `MiniMaxH3LatentUpscaleCombined`(scale 1.25, bicubic, audio_denoise 0.75) → 后 16 步二采精修**
- 一采 `ResolutionSelector` 给 **0.4 MP / 32 对齐**，作者原注：**二采输出≈输入 1.5 倍，基础填太大会爆显存**
- 防爆显存三件套：`UniBlockSwap` + `ReservedVRAMSetter(0.2)` + `EasyCache(0.3 / 0.35 / 0.9)`

因此 16 GB 卡上的现实组合是 **一采 512×896 → ×1.5 → 768×1344**，或 **一采 768×1344 → ×1.25 → 960×1680**，再 Lanczos 到 1080×1920 交付。**不要**按"768×1344 直接 1.33 倍到 1024×1792"来想，那是 1.8 MP，二采阶段极易 OOM（此条为 11-21 原建议的修正）。

二采的价值不在像素数，而在**同一动作轨迹上的二次重采样**——不会出现"第二次生成脸变了"，比重新跑一条高清更省也更稳。

### 11.2 人物一致性：三级防线

1. **参考图锁形**（当前已在做）：每镜 3–4 张，人物参考放第 1 位；有人的镜头必须挂人物参考图。
2. **Ref2VA 兜底**（问题镜）：本机已有现成工作流 `video_minimax_h3_r2v.json`，`MiniMaxH3ReferenceToVideo` 支持 **9 张参考图 + 3 段参考视频 + 3 段参考音频**，`ref_image_size=match`（快）/`max`（2048 短边，最准但慢数倍），配 4 步 Lightning LoRA 开关。适合正脸特写、情绪镜，以及被参考图带偏的镜（03-s17/s18）。
3. **首尾帧连戏**（同场反打）：`MiniMaxH3ImageToVideo` 的 `last_frame` 槽已支持，同场两个镜可以拿上一镜尾帧当下一镜首帧约束。

### 11.3 速度与显存：按收益排序的四件事

1. **批产搬进 ComfyUI**：`generate_batch_forloop_175shots`（一次跑 175 镜）和 `preencode_multi_chain`（预编码 conditioning 再逐镜复用）。省掉的是"每镜一次 HTTP + 一次模型重载 + 一次 32B 编码器前向"。
2. **文本编码器只跑一次**：`H3SaveConditioning` / `H3LoadConditioning`，或直接用上面的 preencode 链。
3. **VAE 换 int8**：本机 `video_minimax_h3_i2v.json` 用的是 `minimax_h3_video_vae_int8_convrot`，比 fp16 版省显存；我们脚本里还是 fp16。
4. **加 LoRA 的两种选法**：`minimax_h3_fl2v_lightx2v_turbo_4step`(0.75，当前) vs `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16`(官方 i2v 工作流就是 8 步 LoRA 跑 4 步)；后者细节略稳、速度几乎一样，值得 A/B。

另外 `MiniMaxH3SigmaShift` 的 `shift_video` 默认 12，4 步下试 8–10；`TESpeedMiniMaxH3`(mode=`4-step LoRA`) + `MiniMaxChunkFeedForward` + `MiniMaxLowVRAMAttention` 是显存吃紧时的稳态组合。

### 11.4 中文文字不要交给模型

告示、纸帖、牌匾上的汉字，H3 和 Flux Klein 都写不对（02-s18 的帖子就出了手写体墨字）。做法：分镜图只要纸的形状、留白、光照，提示词明写"无可辨认文字"；成片阶段用 PIL/ASS 把字贴上去（`C:/Windows/Fonts/msyh.ttc`），还能做"墨迹渗开"。

### 11.5 音轨：先按双时钟，再谈配音

本机 `H3_Turbo_Stable_4V4A（AV各4步）` 把**视频 4 步、音频 4 步分开采样**，是目前最稳的音画组合；`4V8A` / `4V10A` 是音频更细的变体。若仍有人声音色漂移，再上"台词镜 H3 音轨只当环境底、人声单独 TTS/实录 + `assemble.py` ducking"，配乐用 `ace_step_v1_3.5b`。

### 11.6 B 引擎：LTX 2.3 跑空镜与转场

`ltx-2.3-22b-distilled-fp8` 全套 + 身份 LoRA（`LTX-2.3-ID-LoRA-CelebVHQ`）+ 转场 LoRA（`ltx2.3-transition`）都在。城门空镜、雨夜街道、转场这类"没人脸要保"的镜头交给它；有台词保脸的继续 H3，两条引擎别混在同一场戏的连续镜里。

### 11.7 工程侧

- **可以去掉 Toonflow**：分镜图早就直连 8188，视频只差把 `h3_direct.py` 的图接进 `pipeline.py`。依赖面只有 `gen_video` / `gen_image` 两个函数（`make_docs.py`、`assemble.py` 只用 `P.ROOT` 常量）。去掉后分辨率白名单、`round16` bug、"500 被截断"三个问题一起消失。建议先做双后端开关，跑一集验证再翻默认。
- `localComfy.ts` 留着当节点图说明书，`round16` 若要继续用就改 `round32`。
- D 盘只剩 20.7 GB：HD 母版按 960×1680 估 8–10 MB/段、一集 150 MB；先清 `ComfyUI-Shared\\output` 里的历史产物。
- 成片输出改 H.265 CRF 22，比现在 H.264 省近一半体积。

### 11.8 不建议做的事

- **不要下载新模型**：GGUF 量化（`MiniMax-H3-FL2VA-Q4_K_M` 等）能把 19.53 GB 压到 ~10 GB、换来更高的二采分辨率，但那是唯一值得破例的方向，其余换模型收益都不如调参。
- **不要追 1536×2688**：16 GB 卡上二采阶段必爆，且手机端 1080×1920 已够。
- **不要把多个动作塞进一个 5 秒镜**：H3 对"一镜一动作"最稳，两个动作容易出中间态怪帧。
- **不要用倒影/镜面构图**：第01集 s17 连废三版，改大特写抬眼解决。
"""

start = txt.find("## 11. ")
assert start > 0, "未找到第 11 节"
txt = txt[:start] + NEW
open(PATH, "w", encoding="utf-8").write(txt)

bad = [c for c in txt if ord(c) == 7]
print("剩余控制字符:", len(bad), "| 新长度:", len(txt))
