# 短剧写作类 Skill：来源、安装与用法

安装日期：2026-11-22 ｜ 装到 `.user_skills\<name>`，同一份镜像在仓库 `_skills\<name>`。

## 已安装（7 个）

| 技能 | 来源仓库 | 许可 | 干什么 | 与现有链路的关系 |
|---|---|---|---|---|
| `novel-outline` | eternityspring/shuohao-skills | Apache-2.0 | 把小说/梗概拆成分集大纲，产出 `outline.json`（含每集爽点、时长、人群方案） | 前置于 `short-drama-develop`，补"结构可机检"这一层 |
| `novel-characters` | 同上 | Apache-2.0 | 角色设定，产出 `cast.json`（性情、说话方式、音色提示词） | 与 `short-drama-assets` 重叠，但它带 JSON 对账 |
| `novel-art` | 同上 | Apache-2.0 | 美术设定，产出 `art.json`（场景锚点、光照状态、道具） | 与参考图库互补：它管"状态"，我们管"图" |
| `novel-script` | 同上 | Apache-2.0 | 写剧本：场次 + 节拍流（动作/台词交替），**10 道质量门全部由 node 脚本机检**，输出 `script.json` + Markdown + 单页 HTML 评审 | 本项目现在的剧本是 md + 18 镜；它能补"时长预算、单句长度、钩子落点"的确定性校验 |
| `drama-planner` | GongLingRui/screen-creative-skills | 见仓库 | 竖屏短剧策划方案：情绪价值、黄金三秒钩子、三幕结构 | 立项/策划期的清单 |
| `script-evaluator` | 同上 | 见仓库 | 从思想性/艺术性/观赏性三维度给剧本打分 | 相当于"外部审稿人"视角 |
| `story-outline-evaluator` | 同上 | 见仓库 | 从市场潜力/创新性/亮点评估大纲 | 大纲阶段的市场检验 |

## 安装后怎么用（validated）

`novel-script` 零 npm 依赖，只要 Node ≥ 18（本机 v22.23.2）：

```powershell
$US='C:\Users\Administrator\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills'
cd "$US\novel-script"

# 1) 从大纲生成每集骨架
node scripts\novel-script.mjs seed "$US\novel-outline\examples\渡口-outline.json" --eps 1-3 > script.json

# 2) 逐集写戏（模型按 references/script-pass.md 与 references/schema.md 填 scenes）

# 3) 机检（10 道质量门，不能跳）
node scripts\novel-script.mjs validate script.json --outline ... --art ...

# 4) 出人类可读版 / 评审页
node scripts\novel-script.mjs render script.json --md --outline ... --art ... > 剧本.md
node scripts\novel-script.mjs render script.json --html --outline ... --art ... > report.html
```

**本机实测**：`node scripts\selftest.mjs` → 154 项全部通过；用 `渡口` 官方样例跑 `validate` → "6 集 / 9 场 / 123 句台词全部通过（预估 652.1s / 目标 720s）"，`render --md` 正常出中文剧本。

参数口径：台词 4.5 字/秒、动作 2.5 秒/拍、每集容差 ±15%、单句 ≤ 35 字、钩子具象必须落全集前 3 拍。

## 看过但没装的

| 仓库 / 条目 | 为什么没装 |
|---|---|
| `zenstory-ai/drama-skills` | 已装过它的 `short-drama-write` / `develop` / `review` / `storyboard` / `video-prompts` / `director`，写作层已覆盖，不再重复 |
| `UnderleveledBuilder/awesome-short-drama-skills` | 是 83 个 skill 项目的**索引页**，不是技能本体，留作找新技能的入口 |
| `smixs/screen-creative-skills` | 3 stars，README 为俄语，与 GongLingRui 同源内容重复 |
| `shuohao-skills` 的 `novel-staging` / `novel-storyboard` / `character-refs` / `novel-art` 图部分 | 分镜与出图我们已有 `short-drama-storyboard` + `shots_flux.py` 的参考图锁形链路，装进来会与现有流程争同一层 |

## 注意

- 新技能目录放进 `.user_skills` 后，**要重启会话（或重新加载技能清单）才会出现在技能列表里**；本轮的判断依据是我直接读 SKILL.md。
- `novel-script` 的时长口径是**估算**（4.5 字/秒），与 H3 实际 5 秒/镜的硬切法不是一回事。真要接本项目：`script.json` 里的"每拍"是戏的呼吸，落到 `shots.json` 还得按 5 秒一镜重新分。
- `screen-creative-skills` 那两个评分技能是纯提示词（1–2KB 的评分维度清单），价值在于"换一个非本项目的视角审稿"，不提供脚本。
