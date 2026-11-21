# 本地 ComfyUI 工作流清单（全量扫描）

> 扫描时间：2026-11-22 ｜ 扫描脚本：`scan_workflows.py` ｜ 原始数据：`06_素材\workflows_scan.json`
> 范围：`C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI\user\default\workflows`（用户手存工作流 12 份）
> 　　　+ `custom_nodes\*\example_workflows\*`（节点包自带示例 27 份）

---

## 一、结论先说

1. **我们自己只用 3 条图**（Z-Image、Flux2 编辑、H3 i2v），但本地其实有 **7 条 H3 视频工作流**，其中两条是关键资产：
   - **`（实验性）Minimax H3全能参考 二采工作流`**：9 张参考图 + 3 段参考音频 + **两段采样（一采 4 步 → 1.25 倍 latent 放大 → 二采精修）**。这就是"高清不闪脸"的正确姿势，官方/社区已验证过的参数都写好了。
   - **`▶▷MiniMaxH3-加速视频流整合`**：124 节点大杂烩，含 GGUF 量化加载、rgthree 分组开关，但**引用的两个 GGUF 权重本机没有**（见第四节），直接加载会报错。
2. **`video_minimax_h3_r2v`** 是现成的 Ref2VA 入口（9 张参考图），配 4 步 turbo LoRA 开关；这是我们之前讨论"问题镜切 Ref2VA"的落地载体，不用自己搭图。
3. 节点包里还有两套比自建脚本更省事的批产方案：**`generate_batch_forloop_175shots`（一次跑 175 镜）** 和 **`preencode_multi_chain`（先编码、后逐镜复用）**。
4. 8 月还留了 3 份 `h3_i2v` 旧版（含 `(2)` `(3)`），模型组合与主版重复，属于可清理的历史文件。

---

## 二、用户工作流 12 份（实际会用到的）

| 文件 | 节点 | 权重组合 | 参数 | 判断 |
|---|---|---|---|---|
| `image_z_image_turbo.json` | 3 | z_image_turbo_bf16 + qwen_3_4b + ae | — | 与我们 `pipeline.gen_image` 等价，参考图/概念图用 |
| `image_flux2_klein_image_edit_9b_distilled.json` | 7 | flux-2-klein-9b-fp8 + qwen_3_8b + full_encoder_small_decoder | — | 与 `flux_edit.py` 等价，分镜图主路径；UI 版更方便手动试参考图组合 |
| `video_minimax_h3_i2v.json` | 9 | fl2va_pruned_int8 + qwen3vl_32b_nvfp4 + video_vae_**int8** + audio_vae_fp32 + **8步 turbo bf16 LoRA** | steps 4, 768×1344, seed 固定 | **主生产图**，和 `localComfy.ts` 的 h3Graph 一致；比我们多用了 int8 视频 VAE（更省显存）和 ResolutionSelector（按 0.4MP + 32 对齐算尺寸） |
| `video_minimax_h3_t2v.json` | 6 | 同上 | steps 4, 768×1344 | 空镜/纯文生视频，本项目基本用不到 |
| `video_minimax_h3_r2v.json` | 29 | **ref2va_pruned_int8** + **ref2v_turbo_4step LoRA** | `MiniMaxH3ReferenceToVideo` 1344×768 / 124 帧 / `ref_image_size=match`；两个 `ComfySwitchNode` 在"20 步全量"和"4 步 Lightning"间切换 | **Ref2VA 入口，✅ 直接可用**。权重 `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16` 本机有（1.82 GB） |
| `（实验性）Minimax H3全能参考   二采工作流（实验性）.json` | 56 | ref2va + qwen3vl_nvfp4 + video_vae_fp16 + audio_vae_fp32 + `minimax_h3_turbo_4step_diffusion_model`(0.65) | `BasicScheduler(beta, 20)` 出 20 步 sigma，用 `SplitSigmas(4)` 在第 4 步切开：前 4 步一采 → `MiniMaxH3LatentUpscaleCombined`(scale 1.25, bicubic, audio_denoise 0.75) → 后 16 步二采精修；`ResolutionSelector` 0.4MP/32 对齐；`UniBlockSwap` + `ReservedVRAMSetter(0.2)` + `EasyCache(0.3/0.35/0.9)` 防爆显存 | **高清二采的参考实现，✅ 可用**（作者原注：二采输出约输入的 1.5 倍，别把基础分辨率填太大，会爆显存） |
| `▶▷MiniMaxH3-加速视频流整合.json` | 124 | 同时挂 safetensors 与 **GGUF**（`MiniMax-H3-FL2VA-Q4_K_M.gguf`、`qwen3vl_32b_minimax_h3-Q4_K_M.gguf`）；rgthree 分组开关切换 i2v/t2v/r2v 四条分支 | 各分支 steps 4，9:16，0.4MP | **⚠ 缺权重，跑不起来**；但分组开关的设计值得抄 |
| `audio_minimax_music_3.json` | 4 | minimax_music3_dit_fp16 + text_encoder + dav | steps 30, cfg 1.7 | 配乐生成，BGM 可用 |
| `audio_yue2_text2music.json` | 3 | yue2_3b_int8_convrot | steps 32, cfg 1 | 风格化配乐/人声合成参考 |
| `audio_yue2_music_cover.json` | 4 | yue2 + sheetsage2_bf16 | steps 32 | 翻唱/改编，本项目用不到 |
| `video_minimax_h3_i2v (2).json` / `(3).json` | 9 / 9 | fl2va + nvfp4，无 LoRA | — | 8 月旧版（8/15、8/11），与主版重复，**建议归档**；主版 `i2v` / `t2v` / `r2v` 三份的修改时间是 2026-11-21 23:36 |


---

## 三、节点包示例 27 份（按包分组，只列值得用的）

### 3.1 H3 Director（`ComfyUI_MiniMaxH3_Director`）
`minimax_h3_director_{i2v,r2v,fl2v,rv2v,v2v,t2v}.json` 各 11–24 节点，外加 `_external_groups_{i2v,r2v}.json` 和 `_加速版.json`。
用途：**一次任务里跑一组镜头**（`MiniMaxH3DirectorGroupImageToVideo` 管一组，`GroupsCombine` 合并输出）。适合替代现在"Python 循环 + 每镜一次 HTTP"的做法。

### 3.2 H3 音频/双时钟（`comfyui-minimax-h3-audio-T8-main` + `examples`）
- `H3_Turbo_Stable_4V4A（AV各4步）.json`（17 节点）与 `examples\H3_Turbo_Stable_4V4A.json`（12 节点）：**视频与音频各 4 步分离采样**，是目前最稳的音频方案。
- `H3_Turbo_EXP_4V10A.json` / `4V8A`：视频 4 步 + 音频 8–10 步，音频更细但更慢。
- `dual_clock_4step_api.json`、`multirate_exp_api.json`、`双时钟采样步数分离Exp.json`：双时钟采样实验。
- `audio_lock_api.json`：锁音频（`MiniMaxH3AudioLatentControlT8`），做"音色不漂"时有用。
- `still_image_edit_api.json`：单帧图编辑（T8 的 still 分支）。

### 3.3 批产/缓存（`ComfyUI-H3-Conditioning-Cache-AI-Drama-Production-Suite`）
- `generate_batch_forloop_175shots.json`（20 节点）：**175 镜一次跑完**，靠 `H3ForLoop*` 循环 + `H3LoadConditioningList`/`H3ConditioningIndex` 逐镜取缓存条件。这是"一整集甚至多集连跑"的现成骨架。
- `preencode_multi_chain_黑猫.json`（47 节点）：先把多条提示词/参考图**预编码成 conditioning 链**，再逐镜复用。省掉 32B 文本编码器反复前向，是我们最想省的那段时间。

### 3.4 其他
- `ComfyUI-MiniMax-H3-Turbo\minimax_h3_t2v_turbo.json`（21 节点）：turbo 分支参考实现。
- `ComfyUI-MiniMaxH3-Easy\MiniMaxH3_Easy_T8_Stable_4V4A.json`（11）/ `MiniMax_H3_Easy.json`（14）：把 H3 收成"一个 Easy 节点"，适合快速试镜头，不适合精调。
- `comfyui_nvidia_rtx_nodes\rtx_image_upscale.json` / `rtx_video_upscale.json`：NVIDIA RTX 硬件上采样，出片前做 1.5–2 倍轻量放大可当"穷人版高清"。
- `ComfyUI_UniBlockSwap\swap.json` / `uniblockswap\swap.json`：显存块交换模板，二采工作流里就用了这个。

---

## 四、缺失权重（会让工作流直接报错）

`▶▷MiniMaxH3-加速视频流整合.json` 里引用了但 `D:\ai\models` 里**没有**的：

- `Minimax_H3\MiniMax-H3-FL2VA-Q4_K_M.gguf`（GGUF 量化主模型）
- `qwen3vl_32b_minimax_h3-Q4_K_M.gguf`（GGUF 文本编码器）
- 另外它的 UNETLoader 还有个 `"default"` 占位，属于作者未删的空槽。

本机实际存在的 GGUF 只有：`flux-2-klein-9b-Q6_K.gguf`(7.33 GB)、`gemma-3-12b-it-heretic.Q4_K_M`(6.8 GB)、`gemma-4-12b-*`(6.87/9.11 GB)。
→ 结论：**这份整合图当设计参考看，不要直接跑**；要用 GGUF 省显存得先补 H3 与 Qwen3VL 的 GGUF 权重（你说过不下载新模型，那就先放着）。

---

## 五、据此要改的三件事

1. **高清二采照抄 `二采工作流` 的参数，而不是我上一轮说的 768×1344→1024×1792**。
   它的一采是 0.4MP（9:16 约 768×1344 的 60% 像素量），二采 ×1.25；作者原注"二采输出≈输入 1.5 倍，别填太大"。16 GB 卡上把基础给到 1MP 再放大到 1.8MP 风险很高，更稳的组合是**一采 512×896 → ×1.5 → 768×1344**，或**一采 768×1344 → ×1.25 → 960×1680**，再 Lanczos 到 1080×1920 交付。配合 `UniBlockSwap` + `ReservedVRAMSetter(0.2)` + `EasyCache` 防爆显存。
2. **Ref2VA 直接用 `video_minimax_h3_r2v.json` 改**：把提示词换成我们 `ep03_shots.py` 里的 h3 原文，参考图槽换成定妆面部/全身/场景/道具，`ref_image_size` 保持 `match`（要更准再切 `max`，但会慢数倍），turbo 开关打在"4 步 Lightning"位。
3. **批产优先试 `generate_batch_forloop_175shots` 和 `preencode_multi_chain`**：前者解决"18 镜一任务跑完"，后者解决"32B 编码器只跑一次"。两者叠加，理论上一集的固定开销只剩采样。

---

## 六、与上一版《全链路总览》第 4 节的关系

第 4 节写的是"我们的生产路径实际发出的三条节点图"，本节写的是"机器上存在的工作流文件全量"。
两者交集：Z-Image、Flux2 编辑、H3 i2v；本节新增的：二采、r2v、Director 分组、T8 音频、forloop 批产、RTX 上采样。



---

## 七、2026-11-22 复扫：目录从 12 份涨到 19 份，新增 7 份逐条判读

重跑 `python scan_workflows.py --json 06_素材\workflows_scan.json`（旧快照留在 `workflows_scan_prev.json`），新增文件与结论：

| 工作流 | 关键结构 | 判读 |
|---|---|---|
| `MINIMAX-H3_多图参考生视频.json` | `MiniMaxH3ReferenceToVideo` + 9×`LoadImage`，768×1344 / 124 帧，`BasicScheduler(simple,24)`，**不带 turbo LoRA**，`ref_image_size=match` | 官方口径的多图参考。24 步满血太慢，只适合精修单镜；已按它的节点结构自建 4 步 turbo 版做对比（见 §7.1） |
| `MINIMAX-H3工作流合集_多流程整合版.json` | 61 节点、3 套管线并置；`MiniMaxH3MultiRateSamplerEXPT8`（多速率采样）+ `MiniMaxH3AudioConditioningT8`（音频条件）+ `minimax_h3_turbo_4步加速` + `qwen3vl_32b nvfp4_awq` | **最值得挖的一份**：`AudioConditioning` 可能是"给定声音生成对应口型/表演"的入口，正好对上短剧台词口型这一痛点。未验证，列为下一轮实验 |
| `image_flux2_klein_image_edit_4b_distilled.json` | 4b-fp8 + `qwen_3_4b` + `flux2-vae` | 速度档，实测可用，但会往纸上写假字、构图往远景漂（见 §7.2） |
| `image_flux2_klein_image_edit_9b_base.json` | 9b **base**（非 distilled）+ `qwen_3_8b_fp8mixed` + `full_encoder_small_decoder` | 质量档备选；base 版需要更多步数，本机未测 |
| `image_flux2_text_to_image_9b.json` | 纯文生图 1024 边长 | **不用**：与本项目"参考图锁形"原则直接冲突 |
| `image_minimax_h3_image_edit.json` | `minimax_h3_image_pruned_int8` + `qwen3.5_9b_w4a8_gptq` + `qwen3vl_32b`，`KSampler 6` 步，带 `ComfySwitchNode` 开关与自动改写（`TextGenerateV2`） | 语义编辑候选：改服装/改场景可能比 Flux2 更懂"古代服制"。未验证，且要额外加载 20GB 主模型，占显存 |
| `image_minimax_h3_image_t2i.json` | 同上的文生图分支，`ResolutionSelector 0.4MP` | **不用**，理由同上 |

`▶▷MiniMaxH3-加速视频流整合.json` 仍在，缺 `MiniMax-H3-FL2VA-Q4_K_M.gguf` 与 `Qwen3.5-4B-*.gguf`，本机跑不了的状态不变。

### 7.1 多图参考（R2V）实测：不如首帧 i2v 稳

同一镜 `01-s16`（换蟒袍）三张参考图（青衫全身 + 蟒袍 + 乱葬岗），384×672、turbo 4 步：

| 方案 | 耗时 | 结果 |
|---|---|---|
| 首帧 i2v（现用） | 58–68 秒 | 黑金蟒纹、帽翅、站姿与资产一致 |
| 多图 R2V（3 ref） | 76.4 秒 | 袍子自己长出了彩色刺绣和红内衬，与 `物品_蟒袍.png` 不符；脸被帽子压住看不出 |

结论：**首帧 i2v 仍是主力**。R2V 留给"没有合适首帧、但有 2–3 张角色参考"的新镜（例如第 03 集沈照夜首次对脸），且必须接受它更爱自由发挥。

### 7.2 出图分档实测（同一镜 `01-s10`，768×1344）

| 模型 | 冷启（含加载） | 热跑 | 画面 |
|---|---|---|---|
| 9b-fp8 + qwen_3_8b（质量档） | 42.1 秒 | 21–24 秒 | 人物占画面足、脸可用 |
| 4b-fp8 + qwen_3_4b（速度档） | 18.1 秒 | 约 15 秒 | 乱葬岗坟头更准，但人物缩小、脸糊 |
| 4b，8 步 | 15.0 秒 | — | 与 4 步差别不大，加步数不划算 |

顺带踩到一个坑：拿 4b 重出 `01-s01`（红榜特写）时，它给红纸自己写了"科考告示"三个假字，构图也漂成了另一种。所以分档规则收紧为：

- **9b 一律用在**：人物特写/近景、告示·画像·纸片·玉玺等"物证镜"、所有定型图。
- **4b 只用在**：远景、俯拍、空镜，且画面里没有文字载体。
- 实现：`shots_flux.py` 的 `FAST_KEYS` 白名单（当前 10 个镜号），或整集强制 `--fast` / `IMG_FAST=1`；`flux_shots.json` 会记录每张用的哪个模型。
