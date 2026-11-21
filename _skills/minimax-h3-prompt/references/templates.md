# H3 提示词模板与改写范例（按官方结构校正）

> 依据官方 Video Prompt Writing Guide 与 Full-Reference Rewrite Output Format Guide。
> **语言规范**：结构化字段正文用英文，保证镜头、运镜、标签语法无歧义；只有台词、歌词和画面中可见文字保留其原始语言（中文台词写 `<d>[Chinese] …</d>`）。

## 一、Base 模式三字段

所有 Base 任务（T2VA / I2VA / FL2VA / L2VA）共用同一视听正文；带图任务在正文前加一行对齐指令，对齐行后空一行。

```text
integrated_multimodal_description:
[Shot 1] [Style and initial framing]. [Subject identity, position, action, camera motion]. [Speaker (S1) and <d>[Language] exact dialogue</d> when needed]. [Shot 2] At 00:SS.mmm, the camera cuts to [new information].

overall_soundscape:
[Ambience, physical action sounds, and non-verbal human sounds across the clip.]

non_diegetic_music:
[Instrumentation, tempo, rhythm, and dynamic change, or N/A.]
```

### Shot 与时间戳规则

- `[Shot 1]` **不带时间戳**；后续每个镜头以 `[Shot N] At MM:SS.mmm` 起头，切点时间严格递增，且落在所选时长内。
- 一次切镜必须引入新信息：新主体、新空间、新状态、新视角或新时间；仅距离拉近或角度微调，用运镜完成，不开新 Shot。
- 切镜短语用自然英文：`the camera cuts to` / `the shot transitions to` / `the shot changes to`。
- 首尾帧任务通常一镜到底；多镜头时仍受上述切点规则约束。

## 二、四种 Base 任务的起手式

### T2VA（纯文生视频）

无对齐行，直接从 `integrated_multimodal_description` 起头，用文字补全主体外观、空间、动作、风格、声音和镜头层次。

### I2VA（首帧图生视频）

对齐行固定句式，置于三字段之前：

```text
For the target video, at 0.00 seconds, <Picture 1> from [Shot 1] is fully referenced.

integrated_multimodal_description:
[Shot 1] Develop forward from the anchored style, identity, clothing, composition and space; describe the action onset and continuous development. Do not repaint features already visible in the frame.
```

要点：首帧已给出的长相、服装、构图、场景，**不要再用文字重述**，只写随后发生的变化；重复描述会引发二次重绘、脸飘。

### FL2VA（首尾帧）

```text
Picture 1 from [Shot 1] aligns to 0.00 seconds; Picture 2 from the actual final [Shot N] aligns to the exact S.SS-second end time.

integrated_multimodal_description:
Describe the visible, continuous path between the two anchors: pose, object state, composition, lighting and camera motion narrowing onto Picture 2. Default to one continuous shot; do not invent extra cuts unless explicitly requested.
```

### L2VA（末帧反推）

```text
<Picture 1> from the actual final [Shot N] aligns to the exact S.SS-second end time.

integrated_multimodal_description:
Infer a plausible earlier state, then make every change converge on the final image: pose, object arrangement, composition, lighting and framing settle onto <Picture 1> by the end.
```

## 三、说话人与台词（关键语法）

- 按发声顺序给每个说话人稳定 ID：`(S1)`、`(S2)`，群言 `(S1,S2)`；**跨镜头 ID 不变**；不说话的角色不分配 ID。
- 说话人身份、音色、语气、动作放在 `<d>` **外面**；`<d>` 内部只放语言标签和逐字台词：

```text
The young woman with a quiet, breathy voice (S1) turns to camera and says: <d>[Chinese] 我在下一站下车。</d>
The two children (S1,S2) shout together: <d>[English] Wait for us!</d>
```

- 画外音（旁白）固定措辞，并写明画内角色嘴唇闭合：

```text
The man (S1) says in an off-screen voiceover: <d>[English] I still remember that road.</d> while his lips remain completely closed.
```

- 台词跨过一次切镜连续说完：在接缝处用 `<scenetrans>` 标注，并说明声音跨切镜延续；视频结束时台词被截断：用 `<cutoff>` 标注。
- 不可辨认的源语音标 `[unclear]`，不要猜测补全。
- 屏幕可见文字（招牌、标签、字幕、横幅、界面、产品边框）放进英文双引号，逐字保留原语言、大小写和标点，不翻译不改写：

```text
A red neon sign above the door reads "营业中" and remains unobstructed.
```

## 四、Full-Reference 六段（Ref2VA）

参考模式不是把 Base 提示词写长，而是先定义每个素材贡献什么，再在时间轴上追踪其使用与保留程度。六段顺序固定：

```text
subject_definitions:
<Subject 1> is [reusable visible content] from <Picture 1>, preserving [identity-defining features].
<Picture 2> is [concrete frame / keyframe / last frame anchor] when applicable.
<Video 1> is [editing, continuation, or whole-video structural role] when applicable.
<Audio 1> is [copy or reference role] for <Subject 1> (S1) when applicable.

summary:
[task type] [Target video and main reference relationships.]

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - [features retained].
<Audio 1>: reference - [audio characteristic followed without copying the signal].

detailed_description:
[One or two sentences of overall visual style, before [Shot 1].]
[Shot 1] [Composition, references, subject action, camera, synchronized sound, dialogue, and the event leading to the next shot.]
[Shot 2] At 00:SS.mmm, [cut and new information].

overall_soundscape: [Ambience, physical sounds, and audio relationship.]

non_diegetic_music: [Score and audio relationship, or N/A.]
```

### 标签体系（只有四类，没有 Prop 标签）

| 标签 | 指代 |
|---|---|
| `<Subject N>` | 从一个或多个素材提取的可复用可见内容：人物、物体、场景、服装、道具、界面、风格、动作、姿势、效果 |
| `<Picture N>` | 图片本身作为具体首帧/关键帧/尾帧/编辑关键帧/构图锚点或故事板规划 |
| `<Video N>` | 整段源视频被直接编辑、续接，或提供全局相机、切镜、节奏、速度、时长结构；从视频里提取的人物或动作仍是 Subject |
| `<Audio N>` | 被主动使用的音频信号：完整/部分复制，或参考音色、演唱风格、歌词、音效、节拍、节奏、连续性；含声音的视频不自动产生 Audio 标签 |

### 任务类型（summary 前缀，可 `+` 组合，不重复）

`keyframe completion`（关键帧补全）/ `reference generation`（参考生成）/ `video editing`（视频编辑）/ `video continuation`（视频续接）/ `audio reuse`（音频复用）/ `audio reference`（音频参考）。

### 保留关系词

- 视觉：`fully_preserved`（完整保留定义性身份）/ `partially_preserved`（保留但改动或省略部分外观、状态、结构、用途）/ `attribute_transfer`（把运动、风格、姿势、构图、效果等属性迁移到不同目标主体）/ `weak_reference`（只跟随大类、氛围、构图族或风格相似性，不暗示身份级保真）。
- 音频：`fully_copy`（整条复用为最终音轨）/ `partially_copy`（只复制选定时间段或轨道，或增删改其他声音）/ `reference`（跟随音色、表达、节拍、音乐风格、台词内容或声音质感，不复制信号）/ `weak_reference`（只保留宽泛声音类别或氛围，不做信号或表演级匹配）。
- 取满足需求的**最窄关系**：只要构图节奏就写 `weak_reference`，不要写 `fully_preserved`。

### detailed_description 写法

- 与 Base 不同：整体视觉风格的 1–2 句写在 `[Shot 1]` **之前**。
- 每镜写清：当前构图、主体外观与位置、环境、光线、可见动作、状态变化、相机行为、同步音、引向下一镜的事件；标签在其角色实际生效处插入，后文复用同一标签不再重新定义。
- 参考主体说话时，视觉与声音身份合并写为 `<Subject N> (Sx)`；`(Sx)` 不进 `retention_analysis`。
- 普通生成任务正文 350–500 英文词是有用的细节区间，不是配额；重对白片段优先保证完整台词时间轴。

## 五、改写范例（同一镜头，坏 vs 好）

**坏（图片式写法，H3 会丢意图）**

> 一个古代书生跪在贡院门口，很悲伤，电影感，高级质感，8K，超写实，氛围感强，光影绝美。

**好（可见可听 + 时间轴 + 运镜 + 声音，Base 结构）**

```text
integrated_multimodal_description:
Live-action historical drama, cold grey-blue palette, 35mm film grain. [Shot 1] Low-angle medium shot, a thin scholar in a blue cloth headband kneels beside a stone lion against a red wall; both knees strike the frost-covered flagstones, his shoulders slump first then brace up. The camera pushes in with small amplitude at slow speed. Cold white slanted morning fog outlines his profile and the breath he exhales.
[Shot 2] At 00:04.000, close-up on his right hand, knuckles digging into the brick joints, blood seeping between his fingernails. He (S1) says: <d>[Chinese] 我陈知白，十年寒窗，就换了这张榜？</d>

overall_soundscape: Two distant morning bells, wind through eave bells, the dull thud of knees on stone, heavy suppressed breathing and nasal restraint.

non_diegetic_music: N/A
```

## 六、分镜串接规则（一条提示词多镜头）

- 每镜用 `[Shot N]` 起头，按播放顺序写，禁止倒叙；`[Shot 1]` 无时间戳，后续切点严格递增。
- 5 秒最多 2 镜；10 秒最多 3–4 镜；单镜至少留出动作与台词可完成的时间。
- 同一主体跨镜时 ID 不变；服装/道具状态变化要显式写"此刻已换上……"。
- 切镜用可见的过渡事实承接（人影入画、声音先到、光线变化），不要写空洞的"然后切镜"。

## 七、常见失效原因对照

| 现象 | 原因 | 修法 |
|---|---|---|
| 台词没出现 | 台词没包 `<d>`，或说话人没给稳定 ID | 补 `<d>[Chinese] …</d>` + `(S1)`，身份语气放标签外 |
| 脸飘、服装变 | 首帧/参考图已给的信息被文字重复描述 | 删掉重复外观描述，只写变化 |
| 运镜没动 | 写了形容词"环绕""推近"，或词表外命令 | 换官方运动类型词，按 类型+幅度+速度 写成句内英文 |
| 动作做不完 | 短镜头塞了多个动作 | 减到每镜一个主要动作，或延长/合并镜头 |
| 出现配乐但不要 | `non_diegetic_music` 空着 | 明确写 `N/A` |
| 音效串到台词区 | 环境音写进了主时间轴字段 | 移到 `overall_soundscape`；画内同步音留在主时间轴 |
| 切镜后画面碎裂、背景乱跳 | 为小构图变化开了新 Shot | 距离/角度变化改用运镜；cut 只留给新信息 |
| 旁白角色嘴唇在动 | 画外音规则未执行 | 用 off-screen voiceover 措辞，并写明嘴唇闭合 |
