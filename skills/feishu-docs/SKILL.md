---
name: feishu-docs
description: 飞书云文档（Lark Docs）全能管理工具。支持创建、读取、编辑（Markdown）、权限管理。自动兼容 Wiki 链接。Agent 必须使用此工具来处理飞书/Lark 文档请求。
---

# Feishu Docs Skill

> **⚠️ CRITICAL INSTRUCTION**
>
> 1.  **MUST USE `RunCommand`**: All operations must be executed via the `RunCommand` (Bash) tool.
> 2.  **FORBIDDEN TOOLS**: Do **NOT** use `Write`, `SearchReplace`, or `Edit` tools on Feishu URLs. These tools are for local files only.
> 3.  **STRICT URL HANDLING**: Always pass the full URL (e.g., `https://feishu.cn/docx/...` or `https://feishu.cn/wiki/...`). The tool handles token extraction and Wiki resolution automatically.

## 1. 快速开始

当用户请求“写文档”、“更新文档”或“保存到飞书”时，请使用以下标准流程：

### 步骤 1: 环境准备 (一次性)

```bash
# 1. 加载环境变量 (如果存在 .env)
if [ -f .env ]; then export $(grep -v '^#' .env | xargs); fi

# 2. 定位脚本并设置别名 $DOCS
DOCS_SCRIPT=$(find . -path "*/skills/feishu-docs/script/docs" -print -quit)
if [ -z "$DOCS_SCRIPT" ]; then DOCS_SCRIPT="$HOME/.claude/skills/feishu-docs/script/docs"; fi

# 3. 确保使用 Python3 执行
if [ -x "$DOCS_SCRIPT" ]; then DOCS=$DOCS_SCRIPT; else DOCS="python3 $DOCS_SCRIPT"; fi
```

### 步骤 2: 执行操作

**场景 A: 追加内容 (Append)**
```bash
$DOCS append "https://feishu.cn/docx/token..." "## 新会议记录\n- 讨论了架构重构..."
```

**场景 B: 覆盖文档 (Overwrite)**
```bash
$DOCS overwrite "https://feishu.cn/wiki/token..." "# 完整技术方案\n..."
```

**场景 C: 读取内容**
```bash
$DOCS get-content "https://feishu.cn/docx/token..."
```

---

## 2. 核心能力详解

### 智能编辑 (Smart Editing)

无需手动查找 Block ID，直接通过**标题**定位，实现语义化编辑。

| 操作 | 命令示例 | 说明 |
| :--- | :--- | :--- |
| **插入** | `$DOCS insert <URL> "内容" --after "项目背景"` | 在指定标题**后**插入内容 |
| **替换** | `$DOCS replace <URL> "新内容" --section "本周进展"` | 替换指定标题下的**整个章节** |
| **删除** | `$DOCS delete <URL> --section "过时章节"` | 删除指定标题及其下属内容 |
| **大纲** | `$DOCS structure <URL>` | 查看文档标题结构和 ID |

### 基础编辑 (Basic Editing)

| 操作 | 命令示例 | 说明 |
| :--- | :--- | :--- |
| **追加** | `$DOCS append <URL> "内容"` | 在文档末尾追加 |
| **覆盖** | `$DOCS overwrite <URL> "内容"` | 清空并重写整个文档 |
| **插(ID)**| `$DOCS insert <URL> "内容" --parent-id "id"` | 在指定 Block ID 下插入 |
| **删(ID)**| `$DOCS delete <URL> --block-id "id"` | 删除指定 Block ID |

### 权限与管理 (Management)

| 操作 | 命令示例 | 说明 |
| :--- | :--- | :--- |
| **新建** | `$DOCS create-doc "标题"` | 创建新文档 |
| **加人** | `$DOCS add-member <URL> "ou_..." edit` | 添加协作者 (支持 openid/email/chat) |
| **转让** | `$DOCS transfer-owner <URL> "ou_..."` | 转移文档所有者 |

---

## 3. 高级特性

### Wiki 支持
完全兼容 `feishu.cn/wiki/...` 链接。工具会自动调用 API 将 Wiki Token 解析为底层的 Docx Token，对用户透明。
**新增**: 即使传入的是原始 Wiki Token（非 URL），工具也能智能识别并解析，无需人工干预。

### 智能参数
- **Member ID 自动识别**: `ou_` 开头识别为 openid，`@` 识别为 email，无需手动指定类型。
- **流式输入**: 支持管道操作，例如 `cat report.md | $DOCS append <URL>`。

### 错误处理
如果遇到 API 限制（如根节点无法批量删除子节点），工具内置了自动降级策略（Fallback），会尝试循环逐个删除，确保操作成功。

## 4. 常见问题排查

**Q: 报错 `InputValidationError: command is missing`?**
A: 你错误地使用了 IDE 的 `Write` 工具。请务必使用 `RunCommand` (Bash) 执行 `$DOCS` 命令。

**Q: 报错 `unrecognized arguments`?**
A: 检查参数顺序。建议将 `--app-id` 等全局参数放在命令最前方，或者确保 `markdown` 内容被正确引用（建议使用引号包裹）。

**Q: Wiki 链接无法读取?**
A: 确保你的应用（App ID）已开启 **Wiki 知识库** 相关的权限 scopes。
