#!/usr/bin/env python3
"""Build an offline, printable HTML catalog for episodic MiniMax H3 prompts."""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


BRAND_LABEL = "程序Y造物记"
IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def load_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取输入 JSON：{exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("JSON 顶层必须是对象")
    episodes = payload.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        raise ValueError("episodes 必须是非空数组")
    return payload


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def anchor_for(number: str, index: int, used: set[str]) -> str:
    token = re.sub(r"[^a-zA-Z0-9_-]+", "-", number).strip("-").lower()
    base = f"episode-{token or index + 1:}"
    anchor = base
    suffix = 2
    while anchor in used:
        anchor = f"{base}-{suffix}"
        suffix += 1
    used.add(anchor)
    return anchor


def image_data_url(raw_path: str, base_dir: Path, label: str) -> str:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    if not path.is_file():
        raise ValueError(f"资产“{label}”的缩略图文件不存在：{raw_path}")
    mime_type = IMAGE_MIME_TYPES.get(path.suffix.lower())
    if mime_type is None:
        supported = ", ".join(sorted(IMAGE_MIME_TYPES))
        raise ValueError(f"资产“{label}”的缩略图格式不支持：{path.suffix or '无扩展名'}；支持 {supported}")
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError as exc:
        raise ValueError(f"无法读取资产“{label}”的缩略图：{exc}") from exc
    return f"data:{mime_type};base64,{encoded}"


def render_assets(raw: Any, base_dir: Path) -> str:
    if isinstance(raw, list):
        items = raw
    elif raw is None or raw == "":
        items = []
    else:
        items = [raw]

    text_items: list[str] = []
    cards: list[str] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            if item.strip():
                text_items.append(item.strip())
            continue
        if not isinstance(item, dict):
            raise ValueError(f"assets[{index - 1}] 必须是文字或对象")
        label = text(item.get("label") or item.get("name"), f"资产 {index}")
        thumbnail = text(item.get("thumbnail"))
        if not thumbnail:
            raise ValueError(f"资产“{label}”缺少 thumbnail 路径")
        alt = text(item.get("alt"), label)
        data_url = image_data_url(thumbnail, base_dir, label)
        cards.append(
            '<figure class="asset-card">'
            f'<img class="asset-thumb" src="{data_url}" alt="{html.escape(alt, quote=True)}">'
            f'<figcaption>{html.escape(label)}</figcaption>'
            "</figure>"
        )

    if not text_items and not cards:
        return '<span class="muted">无</span>'
    parts = []
    if cards:
        parts.append('<div class="asset-grid">' + "".join(cards) + "</div>")
    if text_items:
        parts.append('<div class="asset-lines">' + "<br>".join(html.escape(item) for item in text_items) + "</div>")
    return "".join(parts)


def render(payload: dict[str, Any], base_dir: Path) -> str:
    title = text(payload.get("title"), "MiniMax H3 视频提示词")
    used: set[str] = set()
    episodes: list[dict[str, Any]] = []

    for index, raw in enumerate(payload["episodes"]):
        if not isinstance(raw, dict):
            raise ValueError(f"episodes[{index}] 必须是对象")
        number = text(raw.get("number"), f"{index + 1:02d}")
        raw_clips = raw.get("clips")
        if raw_clips is None:
            raw_clips = [raw]
        elif not isinstance(raw_clips, list) or not raw_clips:
            raise ValueError(f"第 {number} 集的 clips 必须是非空数组")

        clips: list[dict[str, str]] = []
        for clip_index, raw_clip in enumerate(raw_clips):
            if not isinstance(raw_clip, dict):
                raise ValueError(f"第 {number} 集 clips[{clip_index}] 必须是对象")
            clip_number = text(raw_clip.get("number"), f"{clip_index + 1:02d}")
            prompt = text(raw_clip.get("prompt"))
            if not prompt:
                raise ValueError(f"第 {number} 集片段 {clip_number} 缺少 prompt")
            clip_assets = raw_clip.get("assets") if "assets" in raw_clip else raw.get("assets")
            clips.append(
                {
                    "number": clip_number,
                    "title": text(raw_clip.get("title")),
                    "duration": text(raw_clip.get("duration"), "未标注"),
                    "aspect_ratio": text(raw_clip.get("aspect_ratio"), text(raw.get("aspect_ratio"), "未标注")),
                    "mode": text(raw_clip.get("mode"), text(raw.get("mode"), "未标注")),
                    "assets": render_assets(clip_assets, base_dir),
                    "prompt": prompt,
                    "check_status": text(
                        raw_clip.get("check_status"), text(raw.get("check_status"), "未标注")
                    ),
                }
            )
        episodes.append(
            {
                "anchor": anchor_for(number, index, used),
                "number": number,
                "title": text(raw.get("title"), f"第{number}集"),
                "duration": text(raw.get("duration"), "未标注"),
                "aspect_ratio": text(raw.get("aspect_ratio"), "未标注"),
                "summary": text(raw.get("summary")),
                "clips": clips,
            }
        )

    toc = "\n".join(
        f'<a href="#{episode["anchor"]}">第{html.escape(episode["number"])}集 · '
        f'{html.escape(episode["title"])}</a>'
        for episode in episodes
    )
    sections = []
    for episode in episodes:
        clip_sections = []
        for clip_index, clip in enumerate(episode["clips"], start=1):
            clip_title = f"片段 {clip['number']}"
            if clip["title"]:
                clip_title += f" · {clip['title']}"
            prompt_id = f"prompt-{episode['anchor']}-{clip_index}"
            clip_sections.append(
                f"""
  <article class="clip">
    <div class="clip-heading">
      <h3>{html.escape(clip_title)}</h3>
    </div>
    <table>
      <tbody>
        <tr>
          <th>片段时长</th><td>{html.escape(clip['duration'])}</td>
          <th>画幅</th><td>{html.escape(clip['aspect_ratio'])}</td>
        </tr>
        <tr>
          <th>生成模式</th><td>{html.escape(clip['mode'])}</td>
          <th>检查状态</th><td>{html.escape(clip['check_status'])}</td>
        </tr>
        <tr><th>素材映射</th><td colspan="3">{clip['assets']}</td></tr>
        <tr>
          <th>H3 提示词</th>
          <td colspan="3">
            <div class="prompt-tools">
              <button class="copy-prompt" type="button" data-copy-target="{prompt_id}">复制整段提示词</button>
              <span class="copy-status" role="status" aria-live="polite"></span>
            </div>
            <pre id="{prompt_id}">{html.escape(clip['prompt'])}</pre>
          </td>
        </tr>
      </tbody>
    </table>
  </article>"""
            )
        summary = (
            f'<p class="episode-summary">{html.escape(episode["summary"])}</p>'
            if episode["summary"]
            else ""
        )
        sections.append(
            f"""
<section class="episode" id="{episode['anchor']}">
  <div class="episode-heading">
    <h2>第{html.escape(episode['number'])}集 · {html.escape(episode['title'])}</h2>
    <a class="back" href="#top">返回目录</a>
  </div>
  <div class="episode-meta">
    <span>成片时长：{html.escape(episode['duration'])}</span>
    <span>画幅：{html.escape(episode['aspect_ratio'])}</span>
    <span>H3 片段：{len(episode['clips'])} 条</span>
  </div>
  {summary}
  {''.join(clip_sections)}
</section>"""
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#1f2937; --line:#cbd5e1; --soft:#f8fafc; --accent:#1d4ed8; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:#eef2f7; color:var(--ink); font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    main {{ width:min(1180px,calc(100% - 32px)); margin:28px auto 64px; }}
    header,.episode {{ background:#fff; border:1px solid var(--line); border-radius:14px; box-shadow:0 8px 28px rgba(15,23,42,.06); }}
    header {{ padding:24px; }}
    h1,h2,h3 {{ margin:0; line-height:1.3; }}
    .toolbar {{ display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .title-group {{ display:flex; align-items:center; flex-wrap:wrap; gap:10px; }}
    .brand-mark {{ display:inline-flex; align-items:center; min-height:30px; padding:4px 10px; border:1px solid #fed7aa; border-radius:999px; background:#fff7ed; color:#9a3412; font-size:13px; font-weight:800; letter-spacing:.04em; white-space:nowrap; }}
    .print-watermark {{ display:none; }}
    button {{ border:0; border-radius:9px; padding:10px 16px; color:#fff; background:var(--accent); font-weight:700; cursor:pointer; }}
    nav {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
    nav a,.back {{ color:var(--accent); text-decoration:none; }}
    nav a {{ padding:7px 11px; border:1px solid #bfdbfe; border-radius:999px; background:#eff6ff; }}
    .episode {{ margin-top:22px; padding:22px; scroll-margin-top:16px; }}
    .episode-heading {{ display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:14px; }}
    .episode-meta {{ display:flex; flex-wrap:wrap; gap:8px 20px; margin-bottom:12px; color:#475569; }}
    .episode-summary {{ margin:0 0 14px; padding:10px 12px; border-left:3px solid #93c5fd; background:#eff6ff; }}
    .clip {{ margin-top:16px; }}
    .clip-heading {{ margin-bottom:8px; }}
    .clip-heading h3 {{ font-size:17px; }}
    .asset-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }}
    .asset-card {{ margin:0; overflow:hidden; border:1px solid var(--line); border-radius:10px; background:#fff; }}
    .asset-thumb {{ display:block; width:100%; aspect-ratio:4/3; object-fit:cover; background:var(--soft); }}
    .asset-card figcaption {{ padding:7px 9px; color:#475569; font-size:12px; line-height:1.4; }}
    .asset-lines + .asset-grid,.asset-grid + .asset-lines {{ margin-top:10px; }}
    .prompt-tools {{ display:flex; align-items:center; gap:10px; margin-bottom:10px; }}
    .copy-prompt {{ padding:7px 12px; font-size:13px; }}
    .copy-prompt.is-error {{ background:#b91c1c; }}
    .copy-status {{ min-height:1.5em; color:#475569; font-size:13px; }}
    table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
    th,td {{ border:1px solid var(--line); padding:10px 12px; vertical-align:top; text-align:left; }}
    th {{ width:116px; background:var(--soft); white-space:nowrap; }}
    pre {{ margin:0; white-space:pre-wrap; overflow-wrap:anywhere; font:14px/1.7 ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace; }}
    .muted {{ color:#64748b; }}
    @page {{ size:A4; margin:12mm; }}
    @media print {{
      body {{ background:#fff; font-size:10pt; }}
      main {{ width:100%; margin:0; }}
      header,.episode {{ border:0; border-radius:0; box-shadow:none; padding:0; }}
      header {{ margin-bottom:8mm; }}
      button,.back,.brand-mark,.prompt-tools {{ display:none !important; }}
      .print-watermark {{ display:block; position:fixed; top:3mm; right:0; color:#64748b; font-size:8pt; font-weight:700; letter-spacing:.08em; }}
      nav a {{ border:0; padding:0 8px 0 0; background:none; }}
      .episode {{ break-before:page; margin:0; }}
      .episode:first-of-type {{ break-before:auto; }}
      .clip,table,tr,td,th,pre {{ break-inside:avoid; }}
      .asset-grid {{ grid-template-columns:repeat(3,1fr); gap:6px; }}
      .asset-card {{ break-inside:avoid; }}
      .asset-thumb {{ max-height:38mm; }}
      th,td {{ padding:6px 8px; }}
      pre {{ font-size:8.5pt; line-height:1.45; }}
    }}
  </style>
</head>
<body>
  <main id="top">
    <header>
      <div class="toolbar">
        <div class="title-group"><h1>{html.escape(title)}</h1><span class="brand-mark" aria-label="品牌标记">✨ {BRAND_LABEL}</span></div>
        <button type="button" onclick="window.print()">打印 / 保存 PDF</button>
      </div>
      <nav aria-label="每集目录">{toc}</nav>
    </header>
    {''.join(sections)}
  </main>
  <div class="print-watermark" aria-hidden="true">{BRAND_LABEL}</div>
  <script>
    function fallbackCopy(value) {{
      const field = document.createElement("textarea");
      field.value = value;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.left = "-9999px";
      field.style.opacity = "0";
      document.body.appendChild(field);
      field.focus();
      field.select();
      field.setSelectionRange(0, field.value.length);
      const copied = document.execCommand("copy");
      field.remove();
      if (!copied) throw new Error("copy command failed");
    }}

    async function writeClipboard(value) {{
      if (navigator.clipboard && window.isSecureContext) {{
        try {{
          await navigator.clipboard.writeText(value);
          return;
        }} catch (error) {{
          // 本地文件或浏览器权限限制时继续使用兼容方案。
        }}
      }}
      fallbackCopy(value);
    }}

    function showCopyResult(button, label, message, failed) {{
      const status = button.parentElement.querySelector(".copy-status");
      if (button.copyResetTimer) window.clearTimeout(button.copyResetTimer);
      button.textContent = label;
      button.classList.toggle("is-error", failed);
      status.textContent = message;
      button.copyResetTimer = window.setTimeout(() => {{
        button.textContent = "复制整段提示词";
        button.classList.remove("is-error");
        status.textContent = "";
      }}, 1800);
    }}

    async function copyPrompt(button) {{
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) {{
        showCopyResult(button, "复制失败", "没有找到对应提示词", true);
        return;
      }}
      try {{
        await writeClipboard(target.textContent);
        showCopyResult(button, "已复制", "整段提示词已复制", false);
      }} catch (error) {{
        showCopyResult(button, "复制失败", "请手动选择提示词复制", true);
      }}
    }}

    document.addEventListener("click", (event) => {{
      const button = event.target.closest(".copy-prompt");
      if (button) void copyPrompt(button);
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 episode JSON")
    parser.add_argument("--out", required=True, type=Path, help="output HTML path")
    args = parser.parse_args()
    try:
        output = render(load_payload(args.input), args.input.resolve().parent)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"WROTE: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
