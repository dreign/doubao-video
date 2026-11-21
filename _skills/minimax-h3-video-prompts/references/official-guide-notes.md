# 官方指南校正对照（MiniMax H3 · 2026-11 快照）

> 校正依据（官方原始文件，MiniMax-AI 官方仓库）：
> - Base 任务（T2VA / I2VA / FL2VA / L2VA）：`MiniMax-AI/MiniMax-H3 → skills/h3-prompt-writing/references/base-en.txt`，本目录已存档为 `official-base-en.txt`。
> - 全参考任务（Ref2VA）：`…/references/ref-en.txt`（原文本约 23KB，在线地址 `https://raw.githubusercontent.com/MiniMax-AI/MiniMax-H3/main/skills/h3-prompt-writing/references/ref-en.txt`；本文件第三、六、八节为其规则要点与固定标记清单）。
> 本文件只做"用于写提示词的规则摘要 + 与旧版技能的差异"，不替代官方原文。规则冲突时以官方原文为准。

## 一、结构：先选任务，再定格式

| 任务 | 结构 | 首行 |
|---|---|---|
| T2VA（纯文生） | 三字段 | 无对齐行，直接 `integrated_multimodal_description:` |
| I2VA（首帧） | 三字段 | **必须**原样首行：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.` |
| FL2VA（首尾帧） | 三字段 | `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.` |
| L2VA（尾帧） | 三字段 | `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.` |
| Ref2VA（多参考） | 六段 | `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music` |

三字段：`integrated_multimodal_description`（视觉时间轴 + 台词 + 画内同步声）、`overall_soundscape`（环境音/物理动作声/非语言人声，1–4 句，**不得重复台词、歌词与音乐**）、`non_diegetic_music`（观众向配乐，1–3 句，只写乐器/速度/节奏/动态，**不写抽象情绪词**，不用写「N/A」以外的解释）。

`N/A` 的用法：
- `non_diegetic_music: N/A` = 不要观众向配乐（环境音与音效照常）。
- `overall_soundscape: N/A` **仅当用户明确要求整段完全静默**。
- 旧版技能把"不要 BGM"和"静默"混为一谈，已在本轮修正。

## 二、语言与文字

- 字段正文**用英文**；只有台词、歌词、画面可见文字保留原语言（逐字，不改写、不翻译）。
- 画面可见文字（招牌、标语、字幕、按钮、Logo）放英文双引号内逐字给出，例如 `A red neon sign reading "营业中" glows above the doorway.`
- 台词统一 `<d>[Language] 原文</d>`，`<d>` 内只放语言标签与原文；身份、语气、口型、画内外都写在 `<d>` 外。
- 乱码不可辨认用 `[unclear]`，不猜、不改写。

## 三、镜头与切点

- `[Shot 1]` **不带时间戳**；后续 `[Shot N] At MM:SS.mmm, the camera cuts to…`，切点严格递增且落在时长内。
- 切镜短语只用地道英文：`the camera cuts to` / `the shot cuts to` / `the shot transitions to` / `the shot changes to` / `the shot switches to`；叠化/淡入淡出/划像仅在用户明确要求时用。
- **一次切镜必须引入新信息**：新主体 / 新空间 / 新状态 / 新视角 / 新时间。只改距离或角度用运镜，不开新 Shot。
- `[Shot 1]` 开头先给风格与初始构图，常用风格词：`Cinematic`、`live-action`、`2D-animated`、`3D CG`、`claymation`、`watercolor`、`vintage film`。关键帧任务从参考图推导风格，T2VA 从用户文本选风格。
- 首尾帧任务默认单镜，聚焦两帧之间的连续路径（首帧态 → 中间可见变化 → 逐步收窄差异 → 尾帧态）；不要自行加切镜。
- 尾帧任务从"合理的先前状态"推向参考图，参考图属于最后一镜，不属于第 1 镜。

## 四、运镜写法（官方三段式）

运动类型 + 幅度 + 速度，写成句中自然英文；中等幅度、常规速度一般省略。完整词表见 `camera-vocab.md`。

```text
The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.
The camera pans right with large amplitude at fast speed, revealing the open doorway.
The camera holds a static shot as the runner exits the frame.
```

## 五、说话人与声音

- 发声者首次出现时给稳定 ID `(S1)`、`(S2)`，跨镜不变；直到有真实发声事件才给 ID，不发声的角色**不给** ID。
- 首次出现要给足身份/音色线索：角色类型、年龄、性别、画内/画外、音高、音色、语速、口音。
- 多人合唱/齐声用复合 ID `(S1,S2)`。
- 旁白固定措辞 `says in an off-screen voiceover`，且紧跟一句"画内角色嘴唇完全闭合（lips remain completely closed）"。
- 台词跨切点：两处都标 `<scenetrans>` 并说明声音跨切继续（`continues seamlessly across the cut` 等）；被时长截断标 `<cutoff>`。
- 音色复用：`<Audio N>` 明确绑定到说话人时写 `<Subject N> (Sx)`，ID 按目标视频发声顺序分配，不在音频定义里另起编号。

## 六、全参考模式（Ref2VA）四类标签

| 标签 | 含义 |
|---|---|
| `<Subject N>` | 可复用/可改动的可见内容（人、动物、物、场景、服装、道具、界面、特效、风格、动作、表情、姿势）。道具并入 Subject，不另设 Prop 标签 |
| `<Picture N>` | 作为具体帧锚点/故事板锚点的参考图（首帧、关键帧、尾帧、构图基准、分镜规划） |
| `<Video N>` | 整段结构来源：被编辑的原片、续接起点、或运镜/剪辑/节奏参考 |
| `<Audio N>` | 被复制或参考的音频信号（音色、节奏、音乐风格、台词/歌词内容、音效质感、音画连续性） |

- 只用于"定义某个 Subject"的图片，**不要**单独开 `<Picture N>` 条目，在 Subject 定义里引用即可。
- 标签一经分配，在六段中含义固定。
- `summary` 必须以方括号任务类型开头，多类型用 ` + ` 连接且不重复：`keyframe completion`、`reference generation`、`video editing`、`video continuation`、`audio reuse`、`audio reference`。
- `retention_analysis` 每个标签一行，只用固定英文标记：可见内容 `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`；音频 `fully_copy` / `partially_copy` / `reference` / `weak_reference`。
- `detailed_description`：风格句写在 `[Shot 1]` **之前**（与 Base 模式不同）；生成类任务正文约 350–500 英文词，台词密集时优先保证台词完整而非凑字数。
- `overall_soundscape` / `non_diegetic_music` 里只描述对应的声音层，不要重复 `<d>` 台词。

## 七、时长与句数

- 官方两份指南**没有**给出"5–15 秒"这类片段时长硬规则；时长是产品参数（H3 支持 4/5…秒档），不是提示词规则。
- 本技能沿用的"单片段 5–15 秒、默认按实际时长校验"是**本工作流约定**，不是官方规则；不得再把它写成"官方要求"。
- 唯一与时长相关的官方规则是：切点必须落在时长内、台词要能在该镜时长内说完、不要在 3 秒镜头里塞长台词。

## 八、旧版技能 → 本轮校正清单

| 项 | 旧写法（错/缺） | 校正后 |
|---|---|---|
| 带图对齐行 | 只说"先写固定对齐行"，没有原文 | 三种任务的对齐行原文入 `templates.md`，校验器强制检查 |
| 运镜词表 | 引用 `camera-vocab.md` 但文件不存在 | 新增 `camera-vocab.md`：13 类运动类型 + 幅度 + 速度 + 民间词映射 |
| 模板文件 | 指向不存在的 `minimax-h3-prompt/references/templates.md` | 新增本目录 `templates.md`（Base 三字段 / Ref2VA 六段 / 对齐行） |
| `N/A` | "不要 BGM 就写 N/A"，与"静默"混淆 | 区分 `non_diegetic_music: N/A` 与 `overall_soundscape: N/A`（后者仅在明确要求全程静默时） |
| 声音句数 | 未规定 | soundscape 1–4 句、music 1–3 句，且不得重复台词与音乐 |
| 首镜风格 | 未要求 | `[Shot 1]` 开头必须给风格词 + 初始构图 |
| Ref2VA | 只说六段顺序 | 补 summary 任务类型前缀、retention 固定标记、`<Picture N>` 不为纯定义开条目、350–500 词 |
| 时长口径 | 写成"官方 5–15 秒" | 标为本工作流约定，官方只约束切点与台词可行性 |
| 校验 | 只查中文四段式与几个冲突 | 增加对齐行、summary 前缀、retention 标记、官方结构下正文中文、soundscape 重复台词等检查 |
