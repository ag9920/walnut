#!/usr/bin/env python3
"""Web Clipper AI Skill Script

职责：
- 从指定的 URL 中抓取网页正文文本（去广告、去侧边栏等）；
- 以纯文本形式输出正文内容，供上层 Skill / Agent 进行摘要提取和分析；
- 如传入 `--print-prompt`，则额外输出一段可直接给大模型使用的提示词，要求其总结并存入 Bitable 或输出 Markdown。

依赖：
- trafilatura
"""

import argparse
import sys
import json
import trafilatura

def fetch_article(url: str) -> str:
    """获取网页内容并提取正文。"""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception(f"无法下载网页内容或网页不存在: {url}")
    
    # 提取正文，保留基本换行
    result = trafilatura.extract(downloaded, include_links=False, include_images=False, include_tables=True)
    if not result:
        raise Exception("无法从该网页中提取有效正文内容（可能是纯图片/视频页面或受到反爬限制）")
    
    return result

def build_prompt(content: str, url: str) -> str:
    """构造大模型总结提示词。"""
    return (
        f"你是一个智能网页剪藏助手。请阅读以下从网页（URL: {url}）抓取的正文内容，"
        "并输出一份高质量的「太长不看版（TL;DR）」摘要：\n"
        "- 用 1-3 句话总结核心思想或事件；\n"
        "- 提取 3-5 个关键点（Key Takeaways）；\n"
        "- 以 Markdown 格式输出；\n"
        "- （如果用户要求存入稍后阅读）请指导用户或自动调用 `feishu-bitable` 技能将标题、URL、摘要存入表格中。\n\n"
        "下面是网页正文：\n\n"
        f"```text\n{content}\n```\n"
    )

def main():
    parser = argparse.ArgumentParser(description="Fetch and extract main text from a web page.")
    parser.add_argument("url", help="要剪藏的网页 URL")
    parser.add_argument("--print-prompt", action="store_true", help="打印供大模型使用的总结提示词")
    
    args = parser.parse_args()
    
    try:
        content = fetch_article(args.url)
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)
        
    print("# Raw Web Content\n")
    print(content)
    
    if args.print_prompt:
        print("\n\n# Prompt For Agent\n")
        print(build_prompt(content, args.url))

if __name__ == "__main__":
    main()
