#!/usr/bin/env python3
"""YouTube Transcript Skill Script

职责：
- 使用 `youtube-transcript-api` 从指定的 YouTube 视频链接中获取完整字幕；
- 以纯文本形式输出字幕，供上层 Skill / Agent 进行轻度润色和 Markdown 整理；
- 如传入 `--print-prompt`，则额外输出一段可直接给大模型使用的润色提示词。
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Iterable, List, Optional

from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)


class TranscriptError(Exception):
    """与字幕抓取相关的错误。"""


_YOUTUBE_VIDEO_ID_PATTERN = re.compile(
    r"""
    (?:v=|/)([0-9A-Za-z_-]{11})
    """,
    re.VERBOSE,
)


def extract_video_id(url_or_id: str) -> str:
    """从完整链接或直接的 video id 中解析出视频 ID。"""

    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
        return url_or_id

    match = _YOUTUBE_VIDEO_ID_PATTERN.search(url_or_id)
    if not match:
        raise TranscriptError(f"无法从输入中解析 YouTube 视频 ID: {url_or_id!r}")
    return match.group(1)


def get_youtube_transcript(
    url_or_id: str,
    languages: Optional[Iterable[str]] = None,
) -> str:
    """获取指定 YouTube 视频的完整字幕文本。"""

    video_id = extract_video_id(url_or_id)

    # 默认按常见的中英文顺序尝试
    lang_list: List[str]
    if languages is None:
        lang_list = ["zh-Hans", "zh-Hant", "zh", "en"]
    else:
        lang_list = list(languages)

    try:
        segments = YouTubeTranscriptApi().fetch(video_id, languages=lang_list)
    except (NoTranscriptFound, TranscriptsDisabled) as exc:
        raise TranscriptError(f"该视频没有可用字幕或字幕被关闭: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise TranscriptError(f"获取字幕失败: {exc}") from exc

    # 兼容不同版本的返回结构：
    texts: List[str] = []
    for seg in segments:
        if hasattr(seg, "text"):
            text = str(seg.text)
        elif isinstance(seg, dict):  # type: ignore[deprecated-type]
            text = str(seg.get("text", ""))
        else:
            text = str(seg)

        text = text.replace("\n", " ").strip()
        if text:
            texts.append(text)

    return " ".join(texts)


def build_polish_prompt(transcript: str) -> str:
    """构造给大模型使用的提示词，用于轻度润色并输出 Markdown。"""

    return (
        "你是一名专业的中英文写作编辑。\n"
        "请对下面这篇 YouTube 视频的完整字幕进行 *轻度润色*：\n"
        "- 不改变原文事实和观点；\n"
        "- 保持口语风格，但修正语法和用词错误；\n"
        "- 适当合并重复内容，使逻辑更连贯；\n"
        "- 用 Markdown 形式输出，按合理的层级拆分成小节和段落；\n"
        "- 不要加入视频中没有的新信息。\n\n"
        "下面是字幕原文：\n\n"
        f"```text\n{transcript}\n```\n"
    )


def _cli(argv: Optional[Iterable[str]] = None) -> int:
    """简单的命令行入口，便于本地调试 skill。"""

    parser = argparse.ArgumentParser(
        description="Fetch YouTube transcript via youtube-transcript-api",
    )
    parser.add_argument("url", help="YouTube 视频链接或 11 位视频 ID")
    parser.add_argument(
        "-l",
        "--lang",
        dest="languages",
        action="append",
        help="字幕语言代码，可多次指定，例如: -l zh-Hans -l en",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="除了字幕本身外，同时打印给大模型使用的润色提示词",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        transcript = get_youtube_transcript(args.url, languages=args.languages)
    except TranscriptError as exc:  # noqa: BLE001
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    print("# Raw Transcript\n")
    print(transcript)

    if args.print_prompt:
        print("\n\n# Prompt For Agent\n")
        print(build_polish_prompt(transcript))

    return 0


def main() -> None:
    raise SystemExit(_cli())


if __name__ == "__main__":  # pragma: no cover - 手动执行入口
    main()

