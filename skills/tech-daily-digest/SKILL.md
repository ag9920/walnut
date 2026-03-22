---
name: tech-daily-digest
description: |
  聚合 HackerNews、GitHub Trending、V2EX 等高质量信息源的 RSS，利用 AI 筛选并生成中文技术晨报。
  当用户要求「生成技术晨报」「今天有什么行业新闻」「看看 HackerNews」时调用。
---

# 技术晨报 / RSS 聚合器 (Tech Daily Digest)

本 Skill 旨在帮你每天早晨快速获取科技圈和开源界的高质量信息，打破信息茧房并节省阅读时间。

## 适用场景

当你看到以下用户指令时，应立即启用本 Skill：
- "生成今天的技术晨报"
- "看看今天 HackerNews / GitHub 有什么好玩的"
- "给我推荐 5 篇最新的技术资讯"

## 工作流程

1. **依赖检查与安装**
   在使用前，请检查环境中是否已安装 `feedparser`。
   ```bash
   python3 -c "import feedparser" || pip3 install -r skills/tech-daily-digest/requirements.txt
   ```

2. **抓取 RSS 资讯**
   使用 `RunCommand` (Bash) 调用 `digest.py` 脚本，并传入 `--print-prompt`。默认会抓取 HackerNews，你也可以根据用户需求指定源。
   ```bash
   # 抓取 HackerNews
   python3 skills/tech-daily-digest/scripts/digest.py --source hn --print-prompt
   
   # 抓取所有预设源 (HN, GitHub, V2EX)
   python3 skills/tech-daily-digest/scripts/digest.py --source all --print-prompt
   
   # 抓取自定义 RSS
   python3 skills/tech-daily-digest/scripts/digest.py --custom-url "https://..." --print-prompt
   ```

3. **生成 AI 晨报**
   读取 `digest.py` 的输出后，利用你作为 Agent 的总结与翻译能力，根据 `# Prompt For Agent` 的提示，筛选出最有价值的几条资讯，生成一份排版精美、带点评的中文 Markdown 晨报。

4. **保存到飞书文档（可选）**
   如果用户配置了 `feishu-docs` 技能，请主动提示用户是否需要调用 `feishu-docs` 将生成的晨报写入到指定的飞书文档中，方便分享或团队阅读。
