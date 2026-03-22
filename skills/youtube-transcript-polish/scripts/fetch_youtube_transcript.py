#!/usr/bin/env python3
"""YouTube Transcript Skill Script (Supadata 版本)

职责：
- 使用 Supadata API 从指定的 YouTube 视频链接中获取完整字幕；
- 以纯文本形式输出字幕，供上层 Skill / Agent 进行轻度润色和 Markdown 整理；
- 如传入 `--print-prompt`，则额外输出一段可直接给大模型使用的润色提示词。

环境变量：
- SUPADATA_API_KEY: Supadata API Key (必需，默认从环境变量读取)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable, List, Optional

import requests


class TranscriptError(Exception):
    """与字幕抓取相关的错误。"""


_YOUTUBE_VIDEO_ID_PATTERN = re.compile(
    r"""
    (?:v=|/)([0-9A-Za-z_-]{11})
    """,
    re.VERBOSE,
)

SUPADATA_BASE_URL = "https://api.supadata.ai/v1"


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
    api_key: Optional[str] = None,
    languages: Optional[Iterable[str]] = None,
) -> str:
    """使用 Supadata API 获取指定 YouTube 视频的完整字幕文本。

    Args:
        url_or_id: YouTube 视频链接或 11 位视频 ID
        api_key: Supadata API Key，如未提供则从环境变量 SUPADATA_API_KEY 读取
        languages: 字幕语言代码列表，如未提供则使用 API 默认行为

    Returns:
        完整的字幕文本

    Raises:
        TranscriptError: 当无法获取字幕时抛出
    """
    video_id = extract_video_id(url_or_id)

    # 获取 API Key：优先使用传入的参数，否则从环境变量读取
    key = api_key or os.environ.get("SUPADATA_API_KEY")
    if not key:
        raise TranscriptError(
            "未找到 Supadata API Key。请通过以下方式之一提供：\n"
            "1. 设置环境变量 SUPADATA_API_KEY\n"
            "2. 调用函数时传入 api_key 参数\n"
            "获取 API Key: https://dash.supadata.ai"
        )

    # 构建请求
    headers = {
        "x-api-key": key,
        "Accept": "application/json",
    }

    params: dict = {"videoId": video_id}
    if languages:
        # Supadata 支持 lang 参数指定语言
        lang_list = list(languages)
        if lang_list:
            params["lang"] = lang_list[0]  # 优先使用第一个语言

    try:
        response = requests.get(
            f"{SUPADATA_BASE_URL}/youtube/transcript",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 401:
            raise TranscriptError("API Key 无效或已过期，请检查 SUPADATA_API_KEY") from exc
        elif exc.response.status_code == 404:
            raise TranscriptError("该视频没有可用字幕或视频不存在") from exc
        elif exc.response.status_code == 429:
            raise TranscriptError("API 请求频率超限，请稍后再试") from exc
        else:
            raise TranscriptError(f"API 请求失败: {exc}") from exc
    except requests.exceptions.RequestException as exc:
        raise TranscriptError(f"网络请求失败: {exc}") from exc
    except Exception as exc:
        raise TranscriptError(f"获取字幕失败: {exc}") from exc

    # 解析响应数据
    # Supadata 返回格式: {"content": [{"text": "...", "start": 0.0, "duration": 1.0}, ...]}
    content = data.get("content", [])
    if not content:
        raise TranscriptError("API 返回的字幕内容为空")

    texts: List[str] = []
    for segment in content:
        if isinstance(segment, dict):
            text = str(segment.get("text", ""))
        else:
            text = str(segment)

        text = text.replace("\n", " ").strip()
        if text:
            texts.append(text)

    if not texts:
        raise TranscriptError("未能从响应中提取到有效字幕文本")

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
        description="Fetch YouTube transcript via Supadata API",
    )
    parser.add_argument("url", help="YouTube 视频链接或 11 位视频 ID")
    parser.add_argument(
        "-k",
        "--api-key",
        dest="api_key",
        help="Supadata API Key，也可通过环境变量 SUPADATA_API_KEY 设置",
    )
    parser.add_argument(
        "-l",
        "--lang",
        dest="language",
        help="字幕语言代码，例如: zh-Hans, en",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="除了字幕本身外，同时打印给大模型使用的润色提示词",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    # 优先使用命令行传入的 api_key，否则使用环境变量
    api_key = args.api_key or os.environ.get("SUPADATA_API_KEY")

    languages = [args.language] if args.language else None

    try:
        transcript = get_youtube_transcript(
            args.url,
            api_key=api_key,
            languages=languages,
        )
    except TranscriptError as exc:
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
