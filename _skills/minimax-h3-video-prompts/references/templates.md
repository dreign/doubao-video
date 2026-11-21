# 提交模板（官方结构）

> 中文四段式草稿（`【参考素材说明】/【核心创意】/【画面过程说明】/【整体要求补充】`）只用于内部沟通与拆镜。
> **提交给 H3 时**必须换成下面的官方结构：字段正文英文，台词/歌词/屏显文字保留原语言。

## 一、Base 三字段 · T2VA（纯文生，无素材）

```text
integrated_multimodal_description: [Shot 1] Cinematic, live-action, a medium shot frames ... [Shot 2] At 00:03.500, the camera cuts to ...

overall_soundscape: <1–4 句：环境底噪 + 物理动作声 + 非语言人声；不写台词、歌词、音乐>

non_diegetic_music: <1–3 句：乐器、速度、节奏、动态变化；不要观众向配乐则 N/A>
```

## 二、Base 三字段 · I2VA（首帧图）

首行必须原样（`<Picture 1>` 指上传的第一张图，`[Shot 1]` 指目标视频第一镜）：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Cinematic, live-action, the ... shown in <Picture 1> remains ... preserving appearance, clothing, position, and scene layout. The camera pushes in with small amplitude at slow speed as ...
```

`[Shot 1]` 先复述图里的风格、主体、构图、场景锚点，再往下写动作：**首帧锚点 → 动作起始 → 连续发展 → 结果或反应**。

## 三、Base 三字段 · FL2VA（首尾帧）

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic, live-action, the ... begins in the position and framing established by Picture 1, ... and settles into the pose, spacing, and composition established by Picture 2 at the end of the shot.
```

- `S.SS` 用视频实际时长，两位小数；`N` 是最后一镜序号。
- 默认单镜；不要自行加切镜，只写两帧之间的连续路径。

## 四、Base 三字段 · L2VA（尾帧）

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic, live-action, a close shot begins with an intact ... Toward the end, the moving pieces lose momentum and settle into the exact ... established by <Picture 1>.
```

参考图属于**最后一镜**，不属于第 1 镜；先给合理先前状态，再逐步收敛到图。

## 五、Ref2VA 六段（多素材参考）

```text
subject_definitions:
<Subject 1> is the young woman in <Picture 1>, with long dark hair, a blue cardigan, and a thin silver necklace.
<Subject 2> is the courtyard in <Picture 2>, featuring ...
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).

summary:
[reference generation + audio reference] The target video shows <Subject 1> ...

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - ...
<Audio 1>: reference - its vocal timbre guides the dialogue delivery of <Subject 1> without copying the original signal.

detailed_description:
Cinematic, live-action, warm indoor lighting with soft falloff.
[Shot 1] A medium shot establishes <Subject 1>, ...
[Shot 2] At 00:03.000, the shot cuts to ...
[Shot 3] At 00:05.000, the shot cuts to ...

overall_soundscape:
<1–4 句，只写环境音与物理声>

non_diegetic_music:
N/A
```

硬规则：

- `summary` 首字必须是方括号任务类型：`keyframe completion` / `reference generation` / `video editing` / `video continuation` / `audio reuse` / `audio reference`，多类型 ` + ` 连接。
- `retention_analysis` 每个标签一行，只用固定标记：可见内容 `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`；音频 `fully_copy` / `partially_copy` / `reference` / `weak_reference`。
- 风格句写在 `[Shot 1]` **之前**（这是与 Base 模式唯一的位置差异）。
- 生成类 `detailed_description` 约 350–500 英文词；台词密集时优先保证台词完整。
- 只用来定义某个 Subject 的图片，不单独开 `<Picture N>` 条目，在 Subject 定义里引用。

## 六、台词与屏显文字写法

```text
The young woman with a quiet, breathy voice (S1) says: <d>[Chinese] 我下一站下车。</d>
The two children (S1,S2) shout together, <d>[Chinese] 等等我们！</d>
The man (S1) says in an off-screen voiceover: <d>[Chinese] 我还记得那条路。</d> while his lips remain completely closed.
The red neon sign reading "营业中" glows above the doorway.
```

跨切点续说：两处都标 `<scenetrans>` 并写 `continues seamlessly across the cut`；被视频结尾截断标 `<cutoff>`；不可辨认写 `[unclear]`。

## 七、转换自检（草稿 → 官方）

1. 三字段/六段是否齐全、顺序正确？
2. 带图任务的对齐行是否是原文、是否在第一行、后面是否空一行？
3. 字段正文是否英文；`<d>` 内是否只有语言标签 + 原文？
4. `[Shot 1]` 是否有风格词且无时间戳；后续切点是否严格递增、落在时长内？
5. 每个素材是否有唯一编号、明确用途与保持维度？
6. 台词字数是否塞得进该镜时长？
7. `non_diegetic_music: N/A` 与 `overall_soundscape: N/A` 是否用对了？
8. 全文字符数是否 ≤ 7000。
