---
name: minimax-h3-video-prompts
description: 将故事、剧本、分镜、角色设定、图片、视频、音频或修改需求整理成可直接用于 MiniMax H3 的中文视频提示词；先用三项简短选择确认大概时长、画幅和片段连接方式，再由 Agent 根据剧情在 5–15 秒内动态安排片段，按需生成和归档人物、场景、道具资产，最后以逐集文本或带目录、可打印为 PDF 的 HTML 页面交付。Use when the user asks to create, optimize, self-check, troubleshoot, organize, or export H3 prompts for single clips, multi-episode sequences, multimodal reference generation, continuation, video editing, dialogue, sound design, asset consistency, or printable prompt catalogs.
---

# 程序杨 · MiniMax H3 视频提示词

将用户资料转成 H3 可执行的视听指令。优先保证素材角色清楚、空间与时间连续、动作可拍、台词长度合理、声音无冲突，再追求文采。

## 强制交互流程

按以下顺序工作。用户已在当前请求中明确选择某项时不要重复询问；否则不得替用户默认选择。

运行本技能附带脚本时，先定位本文件所在的技能目录，并把脚本路径解析为该目录下的 `scripts/`。不要假设 Agent 当前工作目录就是技能目录。优先使用环境中可用的 Python 3 启动方式，例如 macOS/Linux 的 `python3`、Windows 的 `py -3` 或 `python`。

### 1. 解析资料

通读资料并识别：生成新视频、连续多段、首尾帧衔接、多模态参考或编辑已有视频。检查所有附件，按用户实际上传顺序映射为 `@图片N`、`@视频N`、`@音频N`，不要凭文件名虚构未看见的内容。

### 2. 三项快速选择

在生成资产或编写提示词前，只确认大概时长、画幅和片段连接方式。用户已经明确提供的选项直接沿用，只询问缺项；每一项都允许选择“由 Agent 推荐”。不要再逐项询问剧集类型、总集数、固定片段时长、视角、是否露脸、声音、语言、平台或观众，直接依据资料判断；信息不足时给出合理推荐，不新增问卷。

推荐一次性提问：

> 请选 3 项，回复内容或选项即可：
> 1）大概成片时长：直接写，例如“每集约 2 分钟”或“全片约 5 分钟”；也可选“由 Agent 推荐”。
> 2）画幅：A. 16:9 横版；B. 9:16 竖版；C. 1:1 或其他；D. 由 Agent 推荐。
> 3）片段连接：A. 无缝连续；B. 自然剪辑；C. 混合连接；D. 由 Agent 推荐。

连接方式含义：

- 无缝连续：下一段承接上一段的尾帧、动作、方向、光线和环境音，适合第一视角或连续探索；
- 自然剪辑：允许按剧情切换景别、机位、时间或地点，但保持叙事因果清楚；
- 混合连接：关键动作使用无缝续接，过场、转场或时间推进使用自然剪辑。

不要询问或设定统一的 H3 片段时长。先按剧情动作、台词、转折和场景变化拆分，再为每个片段动态决定 5–15 秒的实际时长：短反应或快速动作取 5 秒附近，连续探索、对白或完整动作可取更长。相邻片段可以长短不同，但不得留下不足 5 秒的尾段；通过微调相邻片段使总成片时长接近用户选择的大概时长。（仅当明确使用 MiniMax-H3 标准版且需要 4 秒片段时，下限可放宽到 4 秒；H3-Max 不支持 4 秒。）

收到选择后只交付一行简版方案，不生成复杂规格卡：

```text
生成方案：约 <大概时长>｜<画幅>｜<连接方式>｜H3 片段按剧情动态安排 5–15 秒
```

剧集类型、集数、视角、声音和具体片段数量由 Agent 根据资料决定，并在后续剧情拆分中直接体现。用户选择“由 Agent 推荐”时，在简版方案中填入一个明确推荐，不再反问。简版方案交付后执行“通过 / 自检”门禁；只有用户明确通过，才能询问资产需求。

### 3. 询问是否先生成资产

在编写最终提示词前必须询问：

> 是否需要先生成资产？可多选：人物资产 / 场景资产 / 道具资产 / 都不需要。

- 选择“都不需要”：直接进入交付格式选择。
- 选择任一资产类别：先完成所选资产的清单、生成、检查和归类保存，再进入提示词阶段。
- 不要擅自生成用户未选择的资产类别。
- 缺少生成工具或关键参考时，不要用文字文件冒充成品资产；说明阻碍并询问是改为资产提示词还是跳过。

#### 资产生成与归档

先跨集去重，给资产分配稳定编号和文件名，再生成。默认使用用户指定项目目录；未指定保存位置且需要写文件时，只问一次目录。

```text
<项目目录>/
├── assets/
│   ├── characters/
│   ├── scenes/
│   ├── props/
│   ├── source/
│   └── manifest.md
├── prompts/
└── deliverables/
```

`manifest.md` 至少记录：资产编号、名称、类别、出现集数、来源、最终文件、H3 上传用途。推荐命名：

- `character-01-<name>.png`
- `scene-01-<name>.png`
- `prop-01-<name>.png`

人物资产锁定脸、发型、身材、服装和关键装备；场景资产锁定建筑结构、入口、楼层、门窗与动线；道具资产锁定比例、材质、磨损和可交互部分。作为模型参考图时优先使用明亮、中性、细节清楚的资产照；夜景、惊悚或特殊光效放进 H3 提示词，除非用户明确要求资产本身采用最终光线。

资产交付后执行“通过 / 自检”门禁，通过后才能写最终提示词。

### 4. 询问最终交付方式

资产通过或用户选择不生成资产后，必须询问：

> 请选择最终交付方式：1）HTML 表格目录页，可点击每集并直接打印/保存为 PDF；2）直接生成每集提示词。

用户选择两者都要时同时交付。无论选择哪一种，都按“剧集 → H3 片段”组织；每个 5–15 秒片段必须拥有一条可独立提交给 H3 的完整提示词，不能用一条提示词代替数分钟的整集成片。

#### 方式 1：HTML 表格目录页

为每集生成一组完整的 H3 片段提示词，并用 [scripts/build_h3_prompt_html.py](scripts/build_h3_prompt_html.py) 构建一个离线可打开的单文件 HTML：

- 页面顶部显示每集目录，点击跳转到对应集；
- 每集显示集数、标题、最终成片时长、画幅和 H3 片段总数；
- 每集下面按顺序显示所有片段，每个片段独立展示时长、画幅、模式、素材映射、提示词和检查状态；
- 片段使用已生成资产时，在该片段的素材映射中显示对应缩略图；把图片嵌入 HTML，确保离线打开和保存 PDF 时不丢失；
- 提供“打印 / 保存 PDF”按钮并调用浏览器打印；
- 每个 H3 片段提供“复制整段提示词”按钮，只复制该片段完整 `prompt` 内容，并显示复制成功或失败反馈；
- 内嵌 CSS 和 JavaScript，不依赖网络资源；
- 提供 A4 打印样式，打印时隐藏按钮，并尽量避免提示词表格跨页断裂。

先写一个 UTF-8 JSON 文件，再从技能目录解析脚本路径并运行：

```bash
python3 "<技能目录>/scripts/build_h3_prompt_html.py" --input episodes.json --out deliverables/h3-prompts.html
```

JSON 结构：

```json
{
  "title": "项目标题",
  "episodes": [
    {
      "number": "01",
      "title": "本集标题",
      "duration": "20秒",
      "aspect_ratio": "16:9",
      "summary": "本集剧情摘要",
      "clips": [
        {
          "number": "01",
          "title": "发现入口",
          "duration": "7秒",
          "mode": "多模态参考",
          "assets": [
            {
              "label": "@图片1：林研人物资产",
              "thumbnail": "assets/characters/character-01-linyan.png",
              "alt": "林研人物资产缩略图"
            },
            "@视频1：运镜参考"
          ],
          "prompt": "本片段完整 H3 提示词",
          "check_status": "基础检查通过"
        },
        {
          "number": "02",
          "title": "推门进入",
          "duration": "13秒",
          "mode": "多模态参考",
          "assets": ["@图片1：林研人物资产"],
          "prompt": "承接上一片段的完整 H3 提示词",
          "check_status": "基础检查通过"
        }
      ]
    }
  ]
}
```

`episodes` 表示最终成片的集，`clips` 表示该集内按播放顺序排列的 H3 片段。`thumbnail` 支持 PNG、JPG、JPEG、WEBP 和 GIF，路径相对于输入 JSON 文件所在目录。已生成并用于某片段的每项人物、场景或道具资产都必须写成带 `thumbnail` 的对象；若整集共用相同素材，可把 `assets` 放在该集层级让片段继承。没有生成资产时可继续使用文字素材映射。生成器会把图片转成 Base64 写入 HTML，不依赖外部图片文件。缩略图文件缺失或格式不支持时先修复，不要交付空白图片。旧版“一集只有一条 `prompt`”的 JSON 仍可导入，但新的多分钟剧集必须使用 `clips`。

#### 方式 2：逐集提示词

按集建立 `prompts/episode-NN/`，每个 H3 片段使用 `NN-CC-<slug>.txt`，其中 `NN` 是集号，`CC` 是本集片段序号。每个文件先给出可直接复制的完整 H3 提示词，再附极短参数和素材上传顺序；不要把整集多个片段合并成一条提示词，也不要把分析过程混进提示词文件。只有单集单片段任务可继续使用旧式 `NN-<slug>.txt`。

### 5. “通过 / 自检”门禁

每次交付一个可审核结果后必须停止并询问：

> 本轮请选择：通过 / 自检。

- 用户选择“通过”：锁定当前版本，不再擅自修改，进入下一阶段或结束。
- 用户选择“自检”：执行基础检查与完整自检，修复问题，重新交付，并再次询问“通过 / 自检”。
- 逐集工作时逐集询问；批量多集交付时默认按本批次询问一次，用户要求逐集确认时逐集停下。
- 不要把沉默、模糊称赞或新修改意见解释成“通过”。新修改意见表示继续修订当前版本。

## 选择生成模式

- 没有附件：纯文字生成，写清人物、场景、动作、风格和声音。
- 一张图片：明确它是首帧还是尾帧；无法可靠推断且差异会改变结果时只问这一点。
- 两张关键帧：明确首帧与尾帧，只描述两帧之间的连续变化，默认不切镜。
- 图片、视频、音频混合：多模态参考，为每个素材只分配真实需要的用途。
- 修改已有视频：标明编辑对象、修改项和必须保持不变的内容。

参数和模式限制见 [references/h3-model-and-modes.md](references/h3-model-and-modes.md)。涉及复杂台词、声音或多镜头时读取 [references/h3-prompt-guide.md](references/h3-prompt-guide.md)；需要模式范例时读取 [references/examples.md](references/examples.md)。

## 提示词结构

```text
【参考素材说明】
@图片1：人物参考，保持……
@视频1：动作参考，只参考……
@音频1：音色/节奏/复用范围……

【核心创意】
时长、画幅、主体、地点、事件、题材风格和特殊镜头规则。

【画面过程说明】
按 Shot、时间轴或连续故事线写景别、动作、运镜、台词、环境音和音效。

【整体要求补充】
贯穿全片的一致性、声音、文字、节奏、保留项和禁止项。
```

没有素材时省略【参考素材说明】。不要为了凑格式写“无参考素材”。

### 提交 H3 前转官方结构

- Base 任务（T2VA / I2VA / FL2VA / L2VA）：三字段 `integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`；带图任务先写固定对齐行，**逐字照抄，不得改写**：
  - I2VA：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
  - FL2VA：`How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  - L2VA：`How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
  - 对齐行必须是整条提示词的第一行，其后空一行再写三字段；`S.SS` 用两位小数的实际时长，`N` 为最后一镜序号。
- 参考任务（Ref2VA）：六段 `subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`；`summary` 必须以方括号任务类型开头（`keyframe completion` / `reference generation` / `video editing` / `video continuation` / `audio reuse` / `audio reference`，多类型用 ` + `），`retention_analysis` 只用固定英文标记（可见内容 `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`；音频 `fully_copy` / `partially_copy` / `reference` / `weak_reference`）。
- 字段正文用英文；台词、歌词、画面可见文字保留原语言。完整模板见 `references/templates.md`，官方原文摘要与差异对照见 `references/official-guide-notes.md`。

### 写画面与声音（官方分镜规范）

- `[Shot 1]` 开头先给风格词与初始构图（`Cinematic` / `live-action` / `2D-animated` / `3D CG` / `claymation` / `watercolor` / `vintage film`）；`[Shot 1]` 不带时间戳，后续镜头以 `[Shot N] At MM:SS.mmm` 起头，切点严格递增且不越界。
- 一次切镜必须引入新主体、新空间、新状态、新视角或新时间；仅距离/角度微调改用运镜，不开新 Shot。
- 一镜到底保持一条连续动作链，不写多个 Shot 或切镜指令。
- 多镜头明确新景别、主体、动作延续和空间关系。
- 运镜只写官方词表内的运动类型，按"运动类型 + 幅度 + 速度"写成句中自然英文（如 `The camera pushes in with small amplitude at slow speed toward…`），每镜至多 1–2 个；民间词映射见 `references/camera-vocab.md`。
- 台词长度适合镜头时长；说话人给稳定 ID `(S1)`/`(S2)`（多人齐声 `(S1,S2)`），跨镜不变；台词包进 `<d>[Chinese] 原文</d>`，身份、语气、画内/画外来源和口型同步写在标签外；旁白固定写 `says in an off-screen voiceover` 并注明画内角色嘴唇闭合；跨切点续说标 `<scenetrans>`，被结尾截断标 `<cutoff>`，不可辨认写 `[unclear]`。
- 把抽象概念改成可见、可听、可拍的动作和环境，不堆比喻。
- 屏幕文字、标题、标语、按钮或 Logo 必须逐字给出，放进英文双引号。
- H3 原生带声音；画内同步音留在主时间轴，环境音与非语言人声归 `overall_soundscape`（1–4 句，不重复台词与音乐），观众向配乐归 `non_diegetic_music`（1–3 句，只写乐器/速度/节奏/动态，不写抽象情绪词）。
- 不要观众向配乐时写 `non_diegetic_music: N/A`，删除所有冲突的配乐要求；`overall_soundscape: N/A` **只在用户明确要求整段完全静默时**使用。

## 检查规则

### 基础检查：始终执行

每个 H3 片段在首次交付前都使用该片段的实际时长运行：

```bash
python3 "<技能目录>/scripts/check_h3_prompt.py" --mode multimodal --duration 12 prompt.txt
```

片段时长默认按 5–15 秒校验——这是**本工作流约定**（官方指南未规定片段时长，只要求切点落在时长内、台词说得完）；仅当明确使用 MiniMax-H3 标准版、片段为 4 秒时，追加 `--min-duration 4`。

修复全部 `ERROR`，逐项判断 `WARN`。即使用户选择“通过”，也不能交付存在基础结构错误、越界时间或无效素材编号的版本。

提交官方结构时额外跑一次官方层检查（不带 `--duration` 也行）：

```bash
python3 "<技能目录>/scripts/check_h3_prompt.py" --mode single-image --duration 5 prompt.txt
```

它会核对：带图任务的对齐行是否逐字存在且在第一行、Ref2VA 六段与 `summary` 任务类型前缀、`retention_analysis` 标记是否合法、官方结构下字段正文是否夹了中文、`overall_soundscape` 是否重复了台词。`--mode` 与任务对应：T2VA→`text`，I2VA→`single-image`，FL2VA→`first-last`，Ref2VA→`multimodal`，改片→`edit`。

### 完整自检：用户选择“自检”时执行

逐项检查并报告修正结果：

- 人物、服装、装备、场景结构和道具跨集一致；
- 同一集相邻片段以及上一集尾段与下一集首段，在姿态、方向、光线、声音和空间关系上连续；
- 每个素材编号与实际上传顺序一致且用途明确；
- 时长为 5–15 秒（工作流约定；标准版明确要求时可放宽到 4 秒），所有时间段不越界，台词能在对应时间内说完；
- 带图任务的对齐行逐字正确且位于第一行、后接空行；`S.SS` 与实际时长一致；
- `[Shot 1]` 带风格词且无时间戳，后续切点 `At MM:SS.mmm` 严格递增且不越界；每次切镜引入新信息，小构图变化已改用运镜；
- 说话人 `(Sx)` 跨镜稳定，台词在 `<d>` 内且带语言标签；`<scenetrans>` / `<cutoff>` / `[unclear]` 用在正确位置；屏幕文字进双引号并逐字保留；
- 运镜使用官方词表内指令并按三段式书写，未残留 dolly/crane/handheld 等词表外民间词（映射见 `references/camera-vocab.md`）；
- 一镜到底、切镜、首尾帧、声音和音乐要求互不冲突；台词/画内音乐未混入 `overall_soundscape`；`non_diegetic_music: N/A` 与 `overall_soundscape: N/A` 未用混；
- 画面描述具体可见，不出现模型无法执行的抽象要求；
- 资产文件存在、分类正确，并在 `manifest.md` 中有对应记录；
- 成片大概时长、画幅和连接方式与通过的简版方案一致；集数和片段数量符合剧情拆分，片段时长有合理变化且全部为 5–15 秒（标准版放宽情形除外）；
- HTML 目录链接、逐集片段层级、一键复制、打印按钮和 PDF 打印样式可用；若片段使用已生成资产，缩略图存在、对应正确且已嵌入 HTML；或 TXT 目录数与集数一致、TXT 文件总数与 H3 片段总数一致。

自检完成后交付修订版，再次询问“通过 / 自检”。

## 文件索引

| 文件 | 用途 |
|---|---|
| `references/official-guide-notes.md` | 官方两份指南的规则摘要 + 旧版技能差异对照（先读这个） |
| `references/official-base-en.txt` | 官方 Base 指南原文存档（T2VA / I2VA / FL2VA / L2VA） |
| `references/templates.md` | 提交模板：Base 三字段（含三种对齐行）/ Ref2VA 六段 |
| `references/camera-vocab.md` | 官方运镜词表 + 民间词映射 |
| `references/h3-prompt-guide.md` | 中文草稿层写法规程 |
| `references/examples.md` | 各模式范例 |
| `references/h3-model-and-modes.md` | 模型能力与模式限制 |
| `scripts/check_h3_prompt.py` | 静态校验器（草稿层 + 官方层两套检查） |
| `scripts/_fixtures/` | 校验器回归样例（good_i2va / good_ref / bad_i2va） |

> 校正记录：2026-11-20 依据官方 `base-en.txt` / `ref-en.txt` 校正——补三种带图任务的对齐行原文、补运镜词表与民间词映射、补 Ref2VA 的 summary 任务类型前缀与 retention 固定标记、区分 `non_diegetic_music: N/A` 与 `overall_soundscape: N/A`、把“5–15 秒”明确标为本工作流约定而非官方规则；校验器同步新增对齐行、summary 前缀、retention 标记、正文语言、soundscape 重复台词等检查。
