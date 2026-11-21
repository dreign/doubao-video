# H3 运镜指令词表（按官方提示词写作指南校正）

> 依据 MiniMax H3 官方 Video Prompt Writing Guide 的运镜词表与三段式写法整理。
> 官方允许自然语言描述相机动作；显式指令词控制更精确。词表之外的民间词（dolly、crane、boom、whip pan、handheld、rack focus、dolly zoom 等）**不在官方词表内**，按下表映射到官方意图后再写。

## 三段式写法（强制）

一条运镜指令 = **运动类型 + 幅度 + 速度**，写成镜头句内的自然英文，不要堆在句尾当标签：

- 幅度：`with small amplitude`（克制构图变化，保留原构图可读性）/ `with large amplitude`（揭示更多空间或大幅改变构图）；中幅可省略。
- 速度：`at slow speed`（缓慢移动，留时间看清主体或产品细节）/ `at fast speed`（快速揭示或有活力的过渡，但动作仍须物理可读）；常速可省略。
- 每个镜头至多 1–2 个运镜指令，多了互相抵消。

示例：

```text
The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.
The camera pans right with large amplitude at fast speed, revealing the open doorway.
The camera holds a static shot as the runner exits the frame.
```

## 官方运动类型词表

| 意图 | 官方词 | 画面变化 |
|---|---|---|
| 变焦 | `Zoom In` / `Zoom Out` | 机位不动，焦距变化 |
| 纵深移动 | `Push In` / `Pull Out` | 机位本体靠近或远离主体，有透视变化 |
| 横向移动 | `Truck Left` / `Truck Right` | 整机位侧移，不是单纯旋转，有视差 |
| 垂直移动 | `Pedestal Up` / `Pedestal Down` | 整机位在空间中升起或下降 |
| 水平旋转 | `Pan Left` / `Pan Right` | 机位不动，镜头水平摇转 |
| 垂直旋转 | `Tilt Up` / `Tilt Down` | 机位不动，镜头俯仰摇转 |
| 环绕主体 | `Arc Shot` | 机位沿弧线绕主体运动 |
| 跟随主体 | `Tracking Shot` | 机位跟随移动主体并保持相对关系 |
| 主体视角 | `POV` | 构图采用某主体所见视角 |
| 光轴旋转 | `Roll Clockwise` / `Roll Counterclockwise` | 机位绕镜头轴旋转 |
| 受控晃动 | `Shake Slightly` / `Shake Strongly` | 受控手持感，改变画面稳定度 |
| 固定不动 | `Static Shot` | 机位与焦距均保持静止 |

## 民间词到官方词的映射

| 旧写法（非官方） | 校正为 | 说明 |
|---|---|---|
| `dolly in` / `dolly out` | `Push In` / `Pull Out` | 机位纵深移动 |
| `crane up` / `crane down` / `boom up` / `boom down` | `Pedestal Up` / `Pedestal Down` | 机位垂直升降 |
| `whip pan left/right` | `Pan Left` / `Pan Right` + `at fast speed` | 快速甩摇用速度限定表达 |
| `handheld` / `steady` | `Shake Slightly` / `Static Shot` | 晃动或固定二选一 |
| `rack focus to <主体>` / `follow focus` | 写进构图描述：`focus shifts to <主体>` / `the subject stays in focus` | 焦点不是官方相机命令 |
| `dolly zoom` | 拆成 `Push In` 与 `Zoom Out` 两个动作并注明反向；H3 不保证同时执行，慎用 | 希区柯克变焦非官方命令 |
| `truck left + pan right` 拼环绕 | `Arc Shot` | 环绕主体优先直接用 `Arc Shot` |

## 景别与视角（构图信息，不是运镜命令）

景别、角度写在构图分句里，不要混进运镜三段式：

- 景别：`extreme wide shot` / `wide shot` / `medium shot` / `medium close-up` / `close-up` / `extreme close-up`
- 角度：`low angle` / `high angle` / `eye level` / `over-the-shoulder`
- 视角：`POV`（同时属于运动类型词表）

## 组合示例（校正后）

- 逼近压迫：`The camera pushes in with small amplitude at slow speed, low angle, medium close-up.`
- 揭示全貌：`The camera pedestal up with large amplitude, wide shot.`
- 人物出场环绕：`The camera uses an Arc Shot, medium shot.`
- 追兵逼近的慌乱：`The camera Shake Slightly, trucks right, tilts up.`
- 情绪定格：`Static shot, close-up, focus shifts to <Subject 1>.`
