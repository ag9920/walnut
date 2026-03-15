---
name: feishu-bitable
description: 飞书多维表格（Lark Base / Bitable）完整数据操作工具。当用户提到飞书表格、多维表格、lark base、bitable，或者给出包含 larkoffice.com/base、feishu.cn/base 或 feishu.cn/wiki 的 URL 时，务必使用此 skill。支持查询、筛选、创建、更新、删除记录，表结构分析，批量数据导入导出。即使用户只是想"看看表格里有什么"或"往表格里写点数据"，也应该触发此 skill。
---

# Feishu Bitable Skill

飞书多维表格 = 零代码关系型数据库。单字段 10 万字、单表 20 万行。

## 脚本路径

```bash
BITABLE=$([ -x "$HOME/.claude/skills/feishu-bitable/script/bitable" ] && echo "$HOME/.claude/skills/feishu-bitable/script/bitable" || echo "$(git rev-parse --show-toplevel)/skills/feishu-bitable/script/bitable")
```

后续所有命令用 `$BITABLE` 替代。

## 操作规范（必须遵循）

### 1. 读操作：先 analyze，再 query

对一个不熟悉的表，永远先 analyze 拿到字段名和类型，再决定怎么查。不要凭猜测构造 filter。

```bash
# 第一步：了解表结构
$BITABLE analyze "<URL>?table=tblXXX"

# 第二步：根据 analyze 输出的字段名精确查询
$BITABLE query "<URL>?table=tblXXX" --filter "状态=进行中" --field "标题" --field "负责人" --limit 20
```

### 2. 写操作：直接传值，脚本处理格式

URL 和 Email 字段传裸字符串即可，脚本自动转换为飞书要求的对象格式。其他字段直接传原始值。

```bash
$BITABLE create-record "<URL>?table=tblXXX" --data '{
  "标题": "任务名称",
  "源链接": "https://example.com",
  "标签": ["标签A", "标签B"],
  "进度": 75,
  "完成": true
}'
```

### 3. 权限问题：先 health-check

遇到 Forbidden 或权限错误时，先跑 health-check 定位问题层级：

```bash
$BITABLE health-check "<URL>"
```

## 命令速查

| 命令 | 用途 | 需要 ?table= |
|------|------|:---:|
| `health-check <URL>` | 检查认证/连接/权限 | 否 |
| `analyze <URL>` | 深度 Schema 分析 | 是 |
| `list-tables <URL>` | 列出所有数据表 | 否 |
| `query <URL>` | 结构化查询 `--filter --field --limit --json` | 是 |
| `smart-query <URL> "自然语言"` | 自然语言查询 | 是 |
| `count <URL>` | 统计记录数 `--filter` | 是 |
| `create-table <URL> "表名"` | 创建表 `--field 字段名:类型` | 否 |
| `delete-table <URL>` | 删除表 `--table-id` | 否 |
| `create-field <URL> "字段名" 类型` | 创建字段 `--options` | 是 |
| `update-field <URL>` | 更新字段名 `--field-id --name` | 是 |
| `delete-field <URL>` | 删除字段 `--field-id` | 是 |
| `create-record <URL>` | 创建记录 `--data JSON [--json]` | 是 |
| `batch-create <URL>` | 批量创建 `--file JSONL [--json]` | 是 |
| `get-record <URL>` | 获取记录 `--record-id` | 是 |
| `update-record <URL>` | 更新记录 `--record-id --data JSON` | 是 |
| `delete-record <URL>` | 删除记录 `--record-id` | 是 |
| `export <URL> 文件` | 导出 `--format json\|csv --filter` | 是 |

## 筛选语法

```bash
--filter "字段名=值"     # 精确匹配
--filter "字段名:关键词"  # 模糊搜索（包含）
```

多个 `--filter` 自动 AND。字段名含 `=` 或 `:` 时用 `\` 转义。

## 字段值写入格式

| 字段类型 | --data 中的写法 | 脚本自动处理 |
|----------|----------------|:---:|
| text | `"文本内容"` | |
| number / currency | `42` / `99.9` | |
| single_select | `"选项名"` | |
| multi_select | `["A", "B"]` | |
| checkbox | `true` / `false` | |
| date | `1704067200000`（Unix 毫秒） | |
| url | `"https://..."` | ✓ 自动包装 |
| email | `"a@b.com"` | ✓ 自动包装 |
| phone | `"13800138000"` | |
| rating | `3` | |
| progress | `75` | |
| percent | `0.75` | |

## 可创建的字段类型

`create-field` 和 `create-table --field` 支持：
`text` `number` `single_select` `multi_select` `date` `checkbox` `url` `email` `phone` `rating` `progress` `currency` `percent`

## 常见错误速查

| 错误信息 | 原因与解决 |
|---------|-----------|
| `必须提供 app_id 和 app_secret` | 未设置 FEISHU_APP_ID / FEISHU_APP_SECRET 环境变量 |
| `Forbidden` / `没有权限访问此资源` | 应用未被添加为多维表格协作者，需用户在飞书中手动添加 |
| `URL 中缺少 table 参数` | URL 需要 `?table=tblXXX`，先用 `list-tables` 获取 table ID |
| `字段不存在` | 字段名拼写错误，先用 `analyze` 确认准确字段名 |
| `URLFieldConvFail` | 脚本已自动处理；若仍报错，检查字段名是否正确 |
| `TextFieldConvFail` | text 字段应传裸字符串，不要传 `[{text:..., type:...}]` 数组 |
| `字段值格式错误` | 类型不匹配，参考上方字段值写入格式表 |

## 详细参考

- 完整 CLI 参数 → [references/cli-reference.md](references/cli-reference.md)
- 典型场景 → [references/scenarios.md](references/scenarios.md)
