#!/usr/bin/env python3
"""Tech Daily Digest Skill Script

职责：
- 从预设的 RSS Feed 中抓取最新的 N 条技术资讯；
- 将资讯整理为纯文本输出；
- 如传入 `--print-prompt`，则额外输出一段可直接给大模型使用的提示词，要求其进行翻译和总结。

依赖：
- feedparser
"""

import argparse
import sys
import feedparser

FEEDS = {
    "hn": "https://hnrss.org/frontpage",
    "github": "https://github.rsshub.app/trending/daily/any",
    "v2ex": "https://www.v2ex.com/index.xml"
}

def fetch_rss(feed_url: str, limit: int = 10) -> str:
    """获取 RSS Feed 并提取最新的条目"""
    feed = feedparser.parse(feed_url)
    if feed.bozo:
        raise Exception(f"无法解析 RSS 源: {feed_url} ({feed.bozo_exception})")
    
    entries = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "No Title")
        link = entry.get("link", "")
        # 有些 feed 没有 summary，用 description 或 title 代替
        summary = entry.get("summary", entry.get("description", ""))
        
        # 简单清理 HTML 标签
        import re
        summary_clean = re.sub(r'<[^>]+>', '', summary).strip()
        # 限制长度
        if len(summary_clean) > 500:
            summary_clean = summary_clean[:500] + "..."
            
        entries.append(f"Title: {title}\nLink: {link}\nSummary: {summary_clean}\n")
    
    if not entries:
        return "未能从该源获取到内容。"
        
    return "\n---\n".join(entries)

def build_prompt(content: str, source_name: str) -> str:
    """构造大模型总结提示词。"""
    return (
        f"你是一个资深的技术编辑。请阅读以下从【{source_name}】抓取的最新技术资讯：\n\n"
        f"```text\n{content}\n```\n\n"
        "请帮我生成一份高质量的「技术晨报（Daily Digest）」，要求：\n"
        "- 筛选出 3-5 条最有价值的资讯进行深度解读；\n"
        "- 给出中文的标题和一句话核心亮点（Why it matters）；\n"
        "- 附上原始链接；\n"
        "- 以结构清晰、排版精美的 Markdown 格式输出。\n"
        "- （如果用户有配置 `feishu-docs` 技能）请提示用户可以将晨报一键写入飞书文档中。\n"
    )

def main():
    parser = argparse.ArgumentParser(description="Fetch latest tech news from RSS feeds.")
    parser.add_argument("--source", choices=list(FEEDS.keys()) + ["all"], default="hn", help="资讯来源 (hn: HackerNews, github: GitHub Trending, v2ex: V2EX, all: 所有)")
    parser.add_argument("--limit", type=int, default=5, help="每个源提取的条目数量")
    parser.add_argument("--custom-url", type=str, help="自定义 RSS URL")
    parser.add_argument("--print-prompt", action="store_true", help="打印供大模型使用的总结提示词")
    
    args = parser.parse_args()
    
    sources = []
    if args.custom_url:
        sources.append(("Custom", args.custom_url))
    elif args.source == "all":
        sources = [(k, v) for k, v in FEEDS.items()]
    else:
        sources = [(args.source, FEEDS[args.source])]
    
    all_content = []
    
    for name, url in sources:
        try:
            content = fetch_rss(url, limit=args.limit)
            all_content.append(f"### Source: {name}\n{content}")
        except Exception as exc:
            print(f"警告: 抓取 {name} ({url}) 失败 - {exc}", file=sys.stderr)
            
    if not all_content:
        print("错误: 所有源抓取均失败。", file=sys.stderr)
        sys.exit(1)
        
    combined_content = "\n\n====================\n\n".join(all_content)
    
    print("# Raw RSS Content\n")
    print(combined_content)
    
    if args.print_prompt:
        print("\n\n# Prompt For Agent\n")
        source_names = ", ".join([name for name, _ in sources])
        print(build_prompt(combined_content, source_names))

if __name__ == "__main__":
    main()
