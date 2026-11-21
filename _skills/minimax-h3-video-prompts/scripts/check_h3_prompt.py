#!/usr/bin/env python3
"""Static checks for common MiniMax H3 prompt mistakes.

兼容两种写法：
- 中文草稿四段式（【参考素材说明】/【核心创意】/【画面过程说明】/【整体要求补充】）；
- 官方结构：Base 三字段（integrated_multimodal_description / overall_soundscape /
  non_diegetic_music）或 Full-Reference 六段。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"【([^】]+)】")
# 兼容中文草稿 @图片1/@视频1/@音频1 与官方 <Picture 1>/<Video 1>/<Audio 1>
REFERENCE_RE = re.compile(
    r"@(?P<cn>图片|视频|音频)(?P<num1>\d+)|<(?P<en>Picture|Video|Audio)\s+(?P<num2>\d+)>",
    re.I,
)
_CN_KIND = {"图片": "图片", "视频": "视频", "音频": "音频"}
_EN_KIND = {"PICTURE": "图片", "VIDEO": "视频", "AUDIO": "音频"}


def extract_references(prompt: str) -> list[tuple[str, int]]:
    refs: list[tuple[str, int]] = []
    for match in REFERENCE_RE.finditer(prompt):
        if match.group("cn"):
            refs.append((_CN_KIND[match.group("cn")], int(match.group("num1"))))
        else:
            refs.append((_EN_KIND[match.group("en").upper()], int(match.group("num2"))))
    return refs
TIME_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:-|~|〜|—|至)\s*(\d+(?:\.\d+)?)\s*秒")
SHOT_RE = re.compile(r"\[Shot\s+(\d+)\]")
ROLE_WORDS = (
    "参考",
    "锁定",
    "首帧",
    "尾帧",
    "复用",
    "编辑",
    "保持",
    "人物",
    "物体",
    "场景",
    "构图",
    "风格",
    "动作",
    "运镜",
    "音色",
    "节奏",
    "情绪",
    "关键帧",
    "故事板",
)

# 官方结构相关正则
SHOT_TS_RE = re.compile(r"At\s+(?:(\d{1,2}):(\d{2})\.(\d{3})|(\d+(?:\.\d+)?))")
SPEAKER_RE = re.compile(r"\(S\d+(?:,S\d+)*\)")
DIALOGUE_RE = re.compile(r"<d>.*?</d>", re.S)
BASE_FIELDS = (
    "integrated_multimodal_description",
    "overall_soundscape",
    "non_diegetic_music",
)
REF_SECTIONS = (
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
)
# 非官方运镜/相机词（官方词表之外的民间写法）
NON_OFFICIAL_CAMERA = (
    "dolly in",
    "dolly out",
    "dolly zoom",
    "crane up",
    "crane down",
    "boom up",
    "boom down",
    "whip pan",
    "handheld",
    "rack focus",
    "follow focus",
    "环绕运镜",
    "绕拍",
    "拉镜头",
    "推镜头",
    "摇镜头",
    "手持晃动",
)
# 官方风格词（[Shot 1] 开头应显式给出）
STYLE_WORDS = (
    "cinematic",
    "live-action",
    "2d-animated",
    "3d cg",
    "claymation",
    "watercolor",
    "vintage film",
    "电影感",
    "写实",
    "实拍",
    "动画",
    "水彩",
)
# 官方对齐行（逐字）
ALIGN_I2VA = (
    "For the target video, at 0.00 seconds into the target video, "
    "<Picture 1> (from [Shot 1]) is fully referenced."
)
ALIGN_HEAD = "How the reference pictures align with the target video"
RETENTION_MARKS = {
    "fully_preserved",
    "partially_preserved",
    "attribute_transfer",
    "weak_reference",
    "fully_copy",
    "partially_copy",
    "reference",
}
TASK_TYPES = (
    "keyframe completion",
    "reference generation",
    "video editing",
    "video continuation",
    "audio reuse",
    "audio reference",
)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")



def read_prompt(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def section_text(prompt: str, name: str) -> str:
    match = re.search(rf"【{re.escape(name)}】\s*(.*?)(?=\n\s*【|\Z)", prompt, re.S)
    return match.group(1).strip() if match else ""


def add_numbering_warnings(prompt: str, warnings: list[str]) -> None:
    grouped: dict[str, set[int]] = {"图片": set(), "视频": set(), "音频": set()}
    for kind, raw_number in extract_references(prompt):
        grouped[kind].add(raw_number)
    for kind, values in grouped.items():
        if not values:
            continue
        expected = set(range(1, max(values) + 1))
        missing = sorted(expected - values)
        if missing:
            warnings.append(f"@{kind} 编号不连续，缺少：{', '.join(map(str, missing))}")


def check_shot_timestamps(prompt: str, duration: float | None, errors: list[str], warnings: list[str]) -> None:
    """校验官方 Shot 时间戳规则：[Shot 1] 无时间戳；后续切点 At MM:SS.mmm 严格递增。"""
    matches = list(SHOT_RE.finditer(prompt))
    if not matches:
        return

    shot_times: list[tuple[int, float | None]] = []
    for shot_idx, match in enumerate(matches):
        index = int(match.group(1))
        window_end = matches[shot_idx + 1].start() if shot_idx + 1 < len(matches) else len(prompt)
        window = prompt[match.end():window_end]
        ts = SHOT_TS_RE.search(window)
        seconds: float | None = None
        if ts:
            if ts.group(1) is not None:
                seconds = int(ts.group(1)) * 60 + int(ts.group(2)) + int(ts.group(3)) / 1000
            else:
                seconds = float(ts.group(4))
        shot_times.append((index, seconds))

    # Shot 1 不应带时间戳
    first_index, first_ts = shot_times[0]
    if first_index == 1 and first_ts is not None:
        warnings.append("[Shot 1] 不应带时间戳；时间戳只写在后续切点上")

    prev: float | None = None
    for index, seconds in shot_times:
        if index == 1:
            continue
        if seconds is None:
            warnings.append(f"[Shot {index}] 缺少切点时间，格式应为 At MM:SS.mmm")
            continue
        if duration is not None and (seconds < 0 or seconds > duration):
            errors.append(f"[Shot {index}] 切点 {seconds:g} 秒超出 0-{duration:g} 秒范围")
        if prev is not None and seconds <= prev:
            errors.append(f"[Shot {index}] 切点时间 {seconds:g} 秒未严格递增（上一切点 {prev:g} 秒）")
        prev = seconds


def check_official_structure(prompt: str, errors: list[str], warnings: list[str], mode: str) -> None:
    lowered = prompt.lower()

    # Full-Reference 六段完整性
    is_ref = "subject_definitions" in lowered
    if is_ref:
        missing = [section for section in REF_SECTIONS if section not in lowered]
        if missing:
            errors.append(f"参考模式缺少六段中的：{', '.join(missing)}")
        check_ref_details(prompt, errors, warnings)
    else:
        first = prompt.strip().splitlines()[0].strip() if prompt.strip() else ""
        if (first.startswith(ALIGN_HEAD) or ("is fully referenced" in first)) and not any(
            field in lowered for field in BASE_FIELDS
        ):
            warnings.append("发现对齐行但没有三字段；Base 任务必须同时给出 integrated_multimodal_description / overall_soundscape / non_diegetic_music")

    # Base 三字段：出现官方字段迹象且非参考模式时检查齐全
    is_base = any(field in lowered for field in BASE_FIELDS)
    if not is_ref and is_base:
        missing = [field for field in BASE_FIELDS if field not in lowered]
        if missing:
            warnings.append(f"检测到官方结构，但字段不完整，缺少：{', '.join(missing)}")

    if is_base:
        check_base_official(prompt, mode, errors, warnings)

    # 台词与说话人绑定
    has_dialogue = bool(DIALOGUE_RE.search(prompt))
    has_speaker = bool(SPEAKER_RE.search(prompt))
    if has_dialogue and not has_speaker:
        warnings.append("存在 <d> 台词块，但未给说话人稳定 ID（如 (S1)）")

    # 非官方运镜词（中文草稿允许中文运镜表述，只对官方结构报词表外英文民间词）
    official = any(field in lowered for field in BASE_FIELDS) or is_ref
    for word in NON_OFFICIAL_CAMERA:
        if word in lowered and (official or re.search(r"[A-Za-z]", word)):
            warnings.append(
                f"运镜词 “{word}” 不在官方词表内，请按 references/camera-vocab.md 映射为官方指令"
            )


def check_base_official(prompt: str, mode: str, errors: list[str], warnings: list[str]) -> None:
    """官方 Base 结构专项：对齐行、首镜风格词、soundscape 不重复台词、正文语言。"""
    lowered = prompt.lower()
    body = prompt.strip()
    first = body.splitlines()[0].strip()
    has_align = first.startswith(ALIGN_HEAD) or ("is fully referenced" in first)

    if mode == "single-image":
        if not has_align:
            errors.append(
                "I2VA 缺少官方对齐行，首行必须是："
                + ALIGN_I2VA
            )
        elif first.replace("  ", " ") != ALIGN_I2VA.replace("  ", " ") and "<Picture 1>" not in first:
            warnings.append("I2VA 对齐行与官方原文不一致，请逐字照抄")
    if mode == "first-last":
        if not first.startswith(ALIGN_HEAD):
            errors.append("FL2VA 缺少官方对齐行：以 “" + ALIGN_HEAD + " — Picture 1 (from Shot 1) aligns with the 0.00-second mark …” 开头")
        else:
            if "Picture 1" not in first or "0.00" not in first:
                errors.append("FL2VA 对齐行未写明 Picture 1 对齐 0.00 秒")
            if "Picture 2" not in first:
                errors.append("FL2VA 对齐行未写明 Picture 2 的对齐时刻")
    if mode in {"single-image", "first-last"} and has_align:
        lines = body.splitlines()
        if len(lines) > 1 and lines[1].strip():
            warnings.append("对齐行之后应空一行再写三字段")

    # soundscape 不得重复台词/音乐
    ss = re.search(r"overall_soundscape\s*:\s*(.*?)(?=\n\s*non_diegetic_music\s*:|\Z)", prompt, re.S)
    if ss:
        text = ss.group(1)
        if DIALOGUE_RE.search(text):
            errors.append("overall_soundscape 里出现了 <d> 台词块：台词只能写在时间轴字段")
        if re.search(r"dialogue|says|歌声|台词", text, re.I):
            warnings.append("overall_soundscape 可能在复述台词，请移除，只留环境音与物理声")
        if re.search(r"music|score|配乐|音乐", text, re.I):
            warnings.append("overall_soundscape 里出现了音乐描述，观众向配乐应写在 non_diegetic_music")

    # 静默用错
    if re.search(r"overall_soundscape\s*:\s*N/?A", prompt, re.I):
        warnings.append("overall_soundscape: N/A 只在用户明确要求整段完全静默时使用")

    # [Shot 1] 风格词：Base 模式看 [Shot 1] 之后；Ref 模式看 [Shot 1] 之前（官方要求风格句在前）
    if "subject_definitions" in lowered:
        dd = re.search(r"detailed_description\s*:\s*(.*?)(?=\n\s*overall_soundscape\s*:|\Z)", prompt, re.S)
        pre = dd.group(1).split("[Shot 1]")[0].lower() if dd else ""
        if not any(word in pre for word in STYLE_WORDS):
            warnings.append("Ref2VA 的 detailed_description 在 [Shot 1] 之前缺少风格句")
    shot1 = re.search(r"\[Shot\s+1\](.*?)(?=\[Shot\s+2\]|\Z)", prompt, re.S)
    if shot1 and "subject_definitions" not in lowered:
        head = shot1.group(1)[:160].lower()
        if not any(word in head for word in STYLE_WORDS):
            warnings.append("[Shot 1] 开头缺少风格词（Cinematic / live-action / 2D-animated / 3D CG …）")

    # 官方结构下正文语言：<d> 外不应夹大段中文
    outside = DIALOGUE_RE.sub("", prompt)
    cjk = CJK_RE.findall(outside)
    if len(cjk) > 20:
        warnings.append(f"官方结构字段正文应为英文；<d> 之外检测到 {len(cjk)} 个中文字符，请把描述翻成英文（台词/屏显文字保留原语言）")

    # 字符上限
    if len(prompt.strip()) > 7000:
        warnings.append("官方结构下建议再核对一次 7000 字符上限")


def check_ref_details(prompt: str, errors: list[str], warnings: list[str]) -> None:
    """Ref2VA 专项：summary 任务类型前缀、retention 标记。"""
    summary = re.search(r"summary\s*:\s*(.*?)(?=\n\s*retention_analysis\s*:|\Z)", prompt, re.S)
    if summary:
        text = summary.group(1).strip()
        if not text.startswith("["):
            errors.append("Ref2VA 的 summary 必须以方括号任务类型开头，如 [reference generation]")
        elif not any(t in text.lower() for t in TASK_TYPES):
            errors.append("summary 的任务类型不在官方清单内：keyframe completion / reference generation / video editing / video continuation / audio reuse / audio reference")
    else:
        errors.append("Ref2VA 缺少 summary 段")

    ret = re.search(r"retention_analysis\s*:\s*(.*?)(?=\n\s*detailed_description\s*:|\Z)", prompt, re.S)
    if ret:
        marked = re.findall(r"(" + "|".join(sorted(RETENTION_MARKS, key=len, reverse=True)) + r")", ret.group(1))
        if not marked:
            errors.append("retention_analysis 没有使用固定英文标记（fully_preserved 等）")
        if SPEAKER_RE.search(ret.group(1)):
            warnings.append("retention_analysis 里不应出现说话人 (Sx) 编号")
    else:
        errors.append("Ref2VA 缺少 retention_analysis 段")

    # detailed_description 词量提示
    dd = re.search(r"detailed_description\s*:\s*(.*?)(?=\n\s*overall_soundscape\s*:|\Z)", prompt, re.S)
    if dd:
        words = len(re.findall(r"[A-Za-z']+", dd.group(1)))
        if words and words < 200:
            warnings.append(f"detailed_description 只有约 {words} 个英文词，生成类任务建议 350–500 词")



def check_prompt(
    prompt: str,
    mode: str,
    duration: float | None,
    min_duration: int = 5,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    compact = prompt.strip()

    if not compact:
        return ["提示词为空"], []
    if len(compact) > 7000:
        errors.append(f"提示词为 {len(compact)} 字符，超过 7000 字符上限")
    if duration is not None and not min_duration <= duration <= 15:
        errors.append(f"时长 {duration:g} 秒不在 {min_duration}-15 秒范围内")

    sections = set(SECTION_RE.findall(prompt))
    # 中文草稿结构检查（官方结构不含【】段落时跳过）
    if sections:
        if "核心创意" not in sections:
            warnings.append("草稿缺少【核心创意】")
        if "画面过程说明" not in sections:
            warnings.append("草稿缺少【画面过程说明】")
        if mode != "text" and "参考素材说明" not in sections:
            warnings.append("当前模式存在素材，但草稿缺少【参考素材说明】")

    references = extract_references(prompt)
    if mode == "text" and references:
        warnings.append("纯文生模式出现了素材标签，请确认模式选择")
    if mode in {"single-image", "first-last", "multimodal", "edit"} and not references:
        errors.append("当前模式未找到 @图片N、@视频N、@音频N 或 <Picture/Video/Audio N> 标签")

    ref_section = section_text(prompt, "参考素材说明")
    if ref_section:
        for line in ref_section.splitlines():
            if REFERENCE_RE.search(line) and not any(word in line for word in ROLE_WORDS):
                warnings.append(f"素材行未明确用途：{line.strip()}")

    if mode == "single-image":
        image_numbers = {number for kind, number in references if kind == "图片"}
        if image_numbers and image_numbers != {1}:
            warnings.append("单图模式通常只应映射 @图片1")
        if "首帧" not in ref_section and "尾帧" not in ref_section and ref_section:
            errors.append("单图模式必须明确 @图片1 是首帧还是尾帧")

    if mode == "first-last":
        image_numbers = {number for kind, number in references if kind == "图片"}
        if not {1, 2}.issubset(image_numbers):
            errors.append("首尾帧模式必须包含 @图片1 和 @图片2")
        if ("首帧" not in ref_section or "尾帧" not in ref_section) and ref_section:
            errors.append("首尾帧模式必须分别标明首帧和尾帧")
        if re.search(r"切镜到|硬切|快切|叠化切镜|普通切镜|hard cut", prompt, re.I):
            warnings.append("首尾帧模式出现切镜指令；手册建议聚焦两帧之间的连续变化")

    if mode == "edit":
        if not re.search(r"修改|替换|删除|增加|改为", prompt):
            warnings.append("编辑模式没有清晰列出修改项")
        if not re.search(r"保持|保留|不变", prompt):
            warnings.append("编辑模式没有清晰列出保持项")

    shot_count = len(set(SHOT_RE.findall(prompt)))
    if "一镜到底" in prompt and (shot_count >= 2 or re.search(r"切镜到|硬切|叠化|fade", prompt, re.I)):
        errors.append("一镜到底与多 Shot 或切镜指令冲突")

    no_music = bool(re.search(r"非叙事性音乐\s*[：:]\s*N/?A|non_diegetic_music\s*[\"']?\s*:\s*N/?A|不要(?:额外)?(?:添加)?背景音乐|不要\s*BGM", prompt, re.I))
    music_lines = []
    for line in prompt.splitlines():
        if re.search(r"N/?A|不要.*(?:背景音乐|BGM)", line, re.I):
            continue
        if re.search(r"背景音乐|BGM|配乐|音乐参考|复用.*音频", line, re.I):
            music_lines.append(line.strip())
    if no_music and music_lines:
        warnings.append("禁止背景音乐与音乐/音频要求可能冲突，请确认声音设计")

    process = section_text(prompt, "画面过程说明")
    if process and not re.search(r"全景|中景|近景|特写|景别|镜头|固定机位", process):
        warnings.append("画面过程未写景别或镜头构图")

    if re.search(r"台词|说[：:]|说道|对白", prompt) and not re.search(r"[“\"]\s*[^”\"\n]+[”\"]", prompt):
        warnings.append("提到了台词/对白，但没有检测到明确原文")

    screen_text_request = re.search(
        r"出现(?:具体)?文字|显示(?:标题|标语|按钮|字幕|Logo|logo|文字)|"
        r"(?:标题|标语|按钮文字|字幕|Logo|logo|文字)\s*(?:为|改为|替换为|写为|[：:])",
        prompt,
    )
    if screen_text_request and not re.search(r"[“\"]\s*[^”\"\n]+[”\"]", prompt):
        warnings.append("提到了屏幕文字或 Logo，但没有检测到逐字原文")

    ranges = [(float(start), float(end)) for start, end in TIME_RE.findall(prompt)]
    for start, end in ranges:
        if end <= start:
            errors.append(f"时间段 {start:g}-{end:g} 秒不是正向区间")
        upper = duration if duration is not None else 15
        if start < 0 or end > upper:
            errors.append(f"时间段 {start:g}-{end:g} 秒超出 0-{upper:g} 秒范围")

    add_numbering_warnings(prompt, warnings)
    # 官方结构只校验时间轴字段里的 Shot 切点，避免把 retention_analysis 里的 [Shot N] 引用当成切镜
    timeline = prompt
    for fld in ("integrated_multimodal_description:", "detailed_description:"):
        idx = prompt.find(fld)
        if idx >= 0:
            end = len(prompt)
            j = prompt.find("overall_soundscape:", idx)
            if j > 0:
                end = j
            timeline = prompt[idx:end]
            break
    check_shot_timestamps(timeline, duration, errors, warnings)
    if timeline != prompt:
        # 检查的是切片，切点越界仍按原时长判断
        pass
    check_official_structure(prompt, errors, warnings, mode)
    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="-", help="UTF-8 prompt file, or - for stdin")
    parser.add_argument(
        "--mode",
        choices=("text", "single-image", "first-last", "multimodal", "edit"),
        default="text",
    )
    parser.add_argument("--duration", type=float, help="intended duration in seconds")
    parser.add_argument(
        "--min-duration",
        type=int,
        choices=(4, 5),
        default=5,
        help="片段时长下限：默认 5（H3-Max 与本分镜工作流）；标准版 H3 可传 4",
    )
    args = parser.parse_args()

    try:
        prompt = read_prompt(args.prompt)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: 无法读取提示词：{exc}")
        return 1

    errors, warnings = check_prompt(prompt, args.mode, args.duration, args.min_duration)
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")
    if not errors and not warnings:
        print("PASS: 未发现 H3 提示词结构或常见冲突问题")
    else:
        print(f"SUMMARY: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
