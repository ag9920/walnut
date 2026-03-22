---
name: youtube-transcript-polish
description: |
  使用 Supadata API 从指定的 YouTube 视频链接中获取完整字幕，
  然后对全文进行轻度润色，输出结构清晰、语法正确的 Markdown 文本。
  当用户提到「YouTube 视频脚本/字幕整理、润色、转成 Markdown」等需求时使用。
---

# YouTube 视频字幕抓取与轻度润色 Skill

本 Skill 负责指导你完成下面这件事情：

- 从用户给出的 YouTube 视频链接中，使用 **Supadata API** 可靠地抓取全文字幕；
- 将字幕交给大模型进行「轻度润色」，保证语义不变、语法正确；
- 最终输出一份结构合理、适合阅读和二次创作的 Markdown 文本。

> 实现依赖：
> - Python 库：`requests`
> - Supadata API Key（默认从环境变量 `SUPADATA_API_KEY` 读取）
> - 本 Skill 目录下的脚本：`scripts/fetch_youtube_transcript.py`

## 前置要求

使用本 Skill 前，用户需要：

1. **获取 Supadata API Key**
   - 访问 [dash.supadata.ai](https://dash.supadata.ai) 注册账号
   - API Key 会在注册完成后自动生成，可在 Dashboard 中查看

2. **设置环境变量**（推荐）
   - 将 API Key 设置为环境变量 `SUPADATA_API_KEY`
   - 或在调用脚本时通过 `-k` 参数传入

## 触发场景

当用户的需求满足以下任一条件时，优先考虑启用本 Skill：

- 明确提到「YouTube 视频脚本」或「YouTube 字幕」；
- 希望对某个 YouTube 视频做「整理/润色/转成文章/转成 Markdown」；
- 提供了一个 YouTube 视频链接，并要求生成可读性更强的文字稿。

## 整体流程

当本 Skill 被触发时，请遵循如下步骤完成任务：

### 1. 获取视频链接

- 如果用户尚未提供视频链接，先用中文向用户确认需要处理的 YouTube 视频 URL。
- 接受以下几种形式：
  - `https://www.youtube.com/watch?v=...`
  - `https://youtu.be/...`
  - 直接的 11 位 `video_id`。

### 2. 确保依赖可用

- 使用 `Bash` 工具检查是否已安装 `requests`：

  ```bash
  python3 - << 'EOF'
  try:
      import requests  # noqa: F401
      print('OK')
  except Exception as e:
      print('MISSING', e)
  EOF
  ```

- 如果输出中包含 `MISSING`，使用 `Bash` 工具安装依赖：

  ```bash
  pip3 install --user requests
  ```

### 3. 抓取完整字幕

- 使用 `Bash` 工具运行本 Skill 目录中的脚本 `scripts/fetch_youtube_transcript.py`，
  通过其中的 `get_youtube_transcript` 函数获取字幕。

- **使用环境变量方式**（推荐）：

  ```bash
  python3 skills/youtube-transcript-polish/scripts/fetch_youtube_transcript.py "<USER_YOUTUBE_URL>"
  ```

- **使用命令行参数方式**：

  ```bash
  python3 skills/youtube-transcript-polish/scripts/fetch_youtube_transcript.py -k "用户的_api_key" "<USER_YOUTUBE_URL>"
  ```

- 该函数会：
  - 自动从 URL 中解析 `video_id`；
  - 调用 Supadata API 获取字幕（支持多语言，API 会自动选择合适的语言）；
  - 将所有字幕片段按时间顺序拼接为一段完整文本；
  - 出现错误时抛出清晰的中文异常信息（如 API Key 无效、视频无字幕等）。

- 如果该步骤失败（例如视频没有字幕或被关闭）：
  - 清晰地向用户说明原因；
  - 不要捏造内容；
  - 可以询问用户是否改为仅基于已有信息进行摘要或评论，而不是还原逐字稿。

### 4. 轻度润色并生成 Markdown

一旦拿到完整字幕，请作为写作编辑对全文进行「轻度润色」，遵循以下原则：

- **不改变事实与观点**：保留原视频中的信息、论点和结论；
- **修正语法与用词**：修复口误、语病、明显的错别字与语法错误；
- **提升可读性**：适度合并重复表达，拆分过长句子，使逻辑更清晰、段落更工整；
- **保持口语风格**：保留演讲/分享的口语感，不要改写成过于书面化的论文风格；
- **仅限原始信息**：不要引入视频中没有的事实或观点，不要胡编细节。

在输出格式上：

- 使用合法、语法正确的 Markdown；
- 为主要部分添加合适的一级/二级小节标题（如「引言」「核心观点」「案例与说明」「总结」等）；
- 用短段落组织内容，避免过长的大段文本；
- 如有自然的小列表（步骤、要点），可以使用有序/无序列表呈现；
- 不需要保留每一句的时间戳，也不要输出原始的字幕时间信息。

### 5. 结果校对

在给出最终答案前，快速自查一次：

- 是否存在明显的语法错误或中英文混排问题；
- 是否有逻辑跳跃或语义缺失（例如丢失了关键前后文）；
- Markdown 语法是否闭合正确（标题、列表、代码块等）。

## 与用户的交互说明

- 用中文向用户解释你将做的事情：
  - 先抓取字幕（默认从环境变量读取 SUPADATA_API_KEY，如未设置会提示用户提供）；
  - 再进行轻度润色；
  - 最后输出 Markdown 文本。
- 在遇到无法获取字幕的情况时，要明确说明限制，不要假装成功。
- 最终答案中不需要展示中间执行过的 Bash 或 Python 命令，只呈现整理好的结果。

## 常见问题

**Q: 为什么需要 Supadata API Key？**
A: 本 Skill 使用 Supadata 服务获取 YouTube 字幕，该服务需要 API Key 进行身份验证和计费。用户可以免费注册获取 API Key。

**Q: API 有使用限制吗？**
A: Supadata 根据订阅计划有相应的速率限制，具体请参考 [Supadata 定价页面](https://supadata.ai/pricing)。

**Q: 支持哪些语言的字幕？**
A: Supadata 支持 YouTube 视频的所有可用字幕语言。API 会自动选择最合适的语言，也可以通过 `-l` 参数指定特定语言代码（如 `zh-Hans`、`en` 等）。
