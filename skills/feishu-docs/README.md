# Feishu Docs Skill

A high-quality Feishu (Lark) Docs management skill for AI Agents.

## Features

- **Create Docs**: Create new documents in specific folders.
- **Read Docs**: Get raw text content and **block structures (headings/outlines)**.
- **Write Docs**: Convert Markdown to Feishu Blocks and write to documents.
- **Semantic Editing**: **Insert**, **Replace**, or **Delete** content by referencing **Headings** directly (Agent-friendly).
- **Precise Editing**: Modify specific blocks by ID.
- **Update Docs**: Append content or clear and overwrite.
- **Permission Management**: Transfer ownership and add collaborators.

## Installation

Ensure `requests` is installed:

```bash
pip install -r requirements.txt
```

## Usage

Set environment variables:

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

Run the script:

```bash
python3 script/docs --help
```

See [SKILL.md](SKILL.md) for detailed command reference.
