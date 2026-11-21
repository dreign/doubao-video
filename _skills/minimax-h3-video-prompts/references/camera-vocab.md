# 运镜词表（官方词表 + 民间词映射）

> 依据 MiniMax H3 官方 Video Prompt Writing Guide §4.3。写法是**句中自然英文**：运动类型 + 幅度 + 速度，不要写成末尾标签串。
> 中介幅度（medium amplitude）与常速（normal speed）通常省略不写。

## 一、可用的运动类型（只用这些）

| 运动类型 | 含义 |
|---|---|
| `Zoom In` / `Zoom Out` | 机身不动，焦距变化 |
| `Push In` / `Pull Out` | 机身向前靠近 / 向后拉远 |
| `Pan Left` / `Pan Right` | 机身不动，镜头水平摇 |
| `Truck Left` / `Truck Right` | 机身水平平移 |
| `Tilt Up` / `Tilt Down` | 机身不动，镜头垂直摇 |
| `Pedestal Up` / `Pedestal Down` | 整机上升 / 下降 |
| `Arc Shot` | 绕主体弧线运动 |
| `Tracking Shot` | 跟随运动主体 |
| `Static Shot` | 机位与镜头完全静止 |
| `Shake Slightly` / `Shake Strongly` | 轻微 / 强烈晃动 |
| `POV` | 主体视角 |
| `Roll Clockwise` / `Roll Counterclockwise` | 绕镜头轴滚转 |

## 二、幅度与速度

| 维度 | 可用表达 |
|---|---|
| 幅度 | `with small amplitude`（小范围）/ `with large amplitude`（大范围） |
| 速度 | `at slow speed`（慢）/ `at fast speed`（快） |

## 三、正确写法

```text
The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.
The camera pans right with large amplitude at fast speed, revealing the open doorway.
The camera holds a static shot as the runner exits the frame.
The camera arcs around the table with small amplitude at slow speed, keeping his hands in frame.
```

每镜至多 1–2 个运镜指令；"环绕运镜"必须写成 `Arc Shot`，不能写"环绕运镜""绕着转"。

## 四、民间词 → 官方词映射

| 常见民间写法 | 改为 |
|---|---|
| dolly in / dolly out | `Push In` / `Pull Out`（若是变焦则 `Zoom In` / `Zoom Out`） |
| dolly zoom / vertigo effect | `Zoom In` 配合 `Pull Out` 不可同时写；改用 `Push In at slow speed` 或只用 `Zoom In` |
| crane up / crane down / boom up / boom down | `Pedestal Up` / `Pedestal Down` |
| whip pan | `Pan Left/Right at fast speed` |
| handheld / 手持晃动 | `Shake Slightly` / `Shake Strongly` |
| rack focus / follow focus / 移焦 | 官方词表无对应项；改写为可见结果："the focus settles on the letter in her hand"，或用 `Push In` 靠近主体 |
| 环绕运镜 / 绕拍 | `Arc Shot` |
| 拉镜头 / 推镜头（口语） | `Pull Out` / `Push In` |
| 摇镜头（未分方向） | `Pan Left` 或 `Pan Right`（必须给方向） |
| 跟随拍摄 | `Tracking Shot` |
| 固定镜头 / 机位不动 | `Static Shot` |
| 第一人称视角 | `POV` |

## 五、与切镜的分工

- 只改距离或轻微角度：**用运镜**，不要开新 `[Shot N]`。
- 引入了新主体、新空间、新状态、新视角或新时间：才允许切镜。
- 一镜到底：全文只能有一个 `[Shot 1]`，不得出现第二个 `[Shot N]`、不得写切镜/叠化/淡入淡出。
