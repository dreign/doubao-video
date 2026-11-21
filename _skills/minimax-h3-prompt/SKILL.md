---
name: minimax-h3-prompt
description: 为 MiniMax H3（本地 ComfyUI 的 MiniMaxH3ImageToVideo / MiniMaxH3ReferenceToVideo / 文生视频）撰写与改写提示词。当需要生成 H3 视频提示词、修正 H3 输出不听指令（画面不跟随描述、缺台词、缺音效、运镜无效）、把旧式"文生图式长描述"改写成 H3 原生结构、或用首尾帧/多参考图锁定主体时使用。涵盖三字段/六段结构、参考模式标签、台词语法、官方运镜词表与三段式、Shot 时间戳与切镜规则、帧数与时长换算。
---

# MiniMax H3 提示词技能

## 核心认知

H3 不是在"图片模型顺手出视频"，它按提示词构建整条视听时间轴：镜头切分、运镜、谁在第几秒说话、环境音、配乐都受控。用写图片提示词的写法喂它，绝大多数意图会被丢掉。

## 任务先选对（Base 四种 + Reference 一种）

| 任务 | 触发条件 | 结构 |
|---|---|---|
| T2VA（文生视频） | 不给图 | 直接 `integrated_multimodal_description` 起头，无对齐行 |
| I2VA（图生视频） | 给首帧 | 首帧对齐行 + 完整视听时间轴 |
| FL2VA（首尾帧） | 给首帧 + 末帧 | 双帧对齐行 + 两帧之间的连续变化，默认一镜到底 |
| L2VA（末帧反推） | 只给末帧 | 末帧对齐行 + 推断合理开场并收敛到末帧 |
| Ref2VA（参考生视频） | 给人物/场景/风格/动作/音频参考 | 六段：`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music` |

**给了首帧就必须走 I2VA 结构**：参考图当"身份/场景锚"，不要再用文字重复描述它的长相细节（重复描述会引发二次重绘、脸飘）。

## 三个内容字段各管一件事，不要混写

1. `integrated_multimodal_description` — 视觉时间轴。风格、构图、主体、动作、镜头切分、说话人、台词、歌唱、画内同步音。
2. `overall_soundscape` — 环境底噪、物理动作声、非语言人声（呼吸、脚步、喘息）。**不写台词、不写歌唱、不写画内音乐**。
3. `non_diegetic_music` — 只有角色听不到的观众向配乐。按乐器、节拍、节奏型、动态变化写；不要配乐就写 `N/A`。

## Shot 与切镜规则（官方分镜规范）

- `[Shot 1]` 不带时间戳；后续镜头以 `[Shot N] At MM:SS.mmm` 起头，切点时间严格递增且落在所选时长内。
- 一次切镜必须引入新信息：新主体、新空间、新状态、新视角或新时间。仅距离拉近或角度微调，用运镜完成，不开新 Shot。
- 切镜短语用自然英文：`the camera cuts to` / `the shot transitions to` / `the shot changes to`。
- 一镜到底写成同一空间的连续因果链，全文不出现多个 Shot、硬切或叠化。
- 首尾帧任务聚焦两帧之间的连续变化，默认不切镜。

## 台词语法（关键）

- 按发声顺序给每个说话人稳定 ID：`(S1)`、`(S2)`，群言 `(S1,S2)`；**跨镜头 ID 不变**；不说话的角色不给 ID。
- 说话人身份、音色、语气、动作放在 `<d>` 外面；`<d>` 内部只放语言标签和逐字台词：`<d>[Chinese] 具体台词</d>`。
- 只有台词进 `<d>`；叹气、笑声、脚步放 `overall_soundscape`。
- 画外音固定措辞 `says in an off-screen voiceover`，并写明画内角色嘴唇闭合。
- 台词跨切镜连续说完用 `<scenetrans>` 标注；视频结束台词被截断用 `<cutoff>` 标注；不可辨认的源词标 `[unclear]`，不要猜。
- 屏幕可见文字（招牌、标签、字幕、横幅、界面、Logo）放进英文双引号，逐字保留原语言与标点，不翻译不改写。
- 情绪靠动作和声音描写传达，不要写"他很愤怒"这种心理描述——H3 只认可见可听。

## 运镜：官方词表 + 三段式，不写形容词

- 三段式 = 运动类型 + 幅度（`with small/large amplitude`，中幅可省）+ 速度（`at slow/fast speed`，常速可省），写成镜头句内自然英文，不堆句尾标签。
- 官方运动类型：`Zoom In/Out`、`Push In/Pull Out`、`Truck Left/Right`、`Pedestal Up/Down`、`Pan Left/Right`、`Tilt Up/Down`、`Arc Shot`、`Tracking Shot`、`POV`、`Roll Clockwise/Counterclockwise`、`Shake Slightly/Strongly`、`Static Shot`。
- 每镜至多 1–2 个运镜指令，多了互相抵消；词表外民间词（dolly、crane、boom、whip pan、handheld、rack focus 等）按 `references/camera-vocab.md` 的映射表校正。
- 想环绕别写"环绕运镜"，写 `Arc Shot`；想逼近写 `Push In`。

## 参考模式六段怎么写

- `subject_definitions`：先定义每个主体，ID + 外观锚点，只写下文要引用的。标签只有四类：`<Subject N>`（可复用可见内容）、`<Picture N>`（具体帧锚点/故事板）、`<Video N>`（整段视频编辑/续接/结构）、`<Audio N>`（被复制或参考的音频信号）；**没有 Prop 标签**，道具并入 Subject。
- `summary`：一句话锁住任务类型（`keyframe completion` / `reference generation` / `video editing` / `video continuation` / `audio reuse` / `audio reference`，可 `+` 组合）与全片创意，不铺细节。
- `retention_analysis`：声明参考素材哪些必须保留、哪些允许变。视觉关系词：`fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`；音频关系词：`fully_copy` / `partially_copy` / `reference` / `weak_reference`。**取满足需求的最窄关系**——只要构图节奏就写 `weak_reference`，别写 `fully_preserved`。`(Sx)` 说话人 ID 不进本段。
- `detailed_description`：按播放顺序写成紧凑导演稿；与 Base 不同，整体风格 1–2 句写在 `[Shot 1]` 之前。每镜写构图、主体位置、环境、光线、可见动作、状态变化、相机行为、同步音、引向下一镜的事件；标签在生效处插入并复用。
- `overall_soundscape` / `non_diegetic_music`：同上。
- **语言规范**：六段与三字段正文用英文；只有台词、歌词、画面可见文字保留原语言。

模板与逐段范例见 `references/templates.md`；运镜词表与映射见 `references/camera-vocab.md`。

## 时长与帧数（本地 ComfyUI 硬约束）

- 线上时长：MiniMax-H3 标准版 4–15 秒、H3-Max 5–15 秒（不支持 4 秒），24 FPS；本 skill 分镜默认按 5–15 秒规划。本地 `length` 帧数须 ≡ 5 (mod 17)，最小 5：5 秒 = 124 帧，10 秒 = 243 帧。
- `width/height` 需 64 对齐（步进 32 会过校验但出图报 reshape 错）：竖屏用 768×1344，横屏 1344×768。
- 单条提示词覆盖多镜头时，用 `[Shot 1]` `[Shot 2]` 标注，逐镜写在主时间轴字段内，与帧数预算对齐（每镜至少 3 秒，否则动作做不完）。

## 交付前自检

1. 任务类型与结构是否匹配：Base 三字段 / Ref2VA 六段；带图任务是否有对齐行。
2. 三个字段是否都在，且没有互相越界写内容（台词/画内音乐不进 soundscape）。
3. `[Shot 1]` 是否无时间戳；后续切点是否严格递增、不越界。
4. 每次切镜是否引入了新信息；小构图变化是否误用了切镜而非运镜。
5. 台词是否带 `<d>[Chinese] …</d>`，说话人 `(Sx)` 是否全程唯一稳定；画外音是否注明嘴唇闭合。
6. 屏幕文字是否进双引号且逐字保留。
7. 是否还在用文字重复描述首帧/参考图里已有的长相与服装（应删除）。
8. 运镜是否为官方词表内指令、三段式完整、数量 ≤2；是否残留词表外民间词。
9. 帧数是否 ≡5 (mod 17)，分辨率是否 64 对齐。
10. 是否出现心理描写、"电影感""高级感"等空形容词——全部替换成可见可听事实。
