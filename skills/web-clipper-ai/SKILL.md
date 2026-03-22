---
name: web-clipper-ai
description: |
  抓取任意网页正文（自动去广告），提取核心内容并生成摘要（TL;DR），支持一键保存至飞书多维表格（Bitable）。
  当用户要求「剪藏网页」「总结这个网址」「稍后阅读」时调用。
---

# 稍后阅读与网页剪藏助手 (Web Clipper AI)

本 Skill 旨在帮你将冗长的文章、技术博客变成高质量的“太长不看版（TL;DR）”并自动化整理到稍后阅读清单中。

## 适用场景

当你看到以下用户指令时，应立即启用本 Skill：
- "帮我剪藏这个网页: https://..."
- "总结一下这篇博客的核心观点"
- "把这个链接加到我的稍后阅读清单里"

## 工作流程

1. **依赖检查与安装**
   在使用前，请检查环境中是否已安装 `trafilatura`。
   ```bash
   python3 -c "import trafilatura" || pip3 install -r skills/web-clipper-ai/requirements.txt
   ```

2. **抓取网页正文**
   使用 `RunCommand` (Bash) 调用 `clipper.py` 脚本，并传入 `--print-prompt`。该脚本会自动剔除网页的侧边栏、广告等无关内容。
   ```bash
   python3 skills/web-clipper-ai/scripts/clipper.py "<URL>" --print-prompt
   ```

3. **生成 AI 摘要**
   读取 `clipper.py` 的输出后，利用你作为 Agent 的强大总结能力，根据 `# Prompt For Agent` 的提示，生成结构化的 Markdown 摘要（包含 TL;DR 和 Key Takeaways）。

4. **保存到稍后阅读库（可选）**
   如果用户提到“保存到多维表格”或“稍后阅读”，并且当前项目中有可用的 `feishu-bitable` 技能配置，请主动提示用户是否需要调用 `feishu-bitable` 将提取到的标题、URL、摘要等信息自动插入多维表格的待办/稍后阅读清单中。

## 注意事项

- 有些网站可能会限制爬虫（如反爬机制），遇到此情况请如实告知用户“该网页内容受到保护，无法提取正文”。
- 对于极长的长文，生成的摘要要尽量保持信息密度，不要遗漏最重要的结论。
