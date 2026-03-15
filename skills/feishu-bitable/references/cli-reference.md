# Feishu Bitable CLI 完整参考

## 前置检查

### health-check — 健康检查

```bash
./script/bitable health-check "<URL>" [--json]
```

| 参数 | 说明 |
|------|------|
| `<URL>` | 多维表格 URL（可选，不提供则只检查认证） |
| `--json` | 以 JSON 格式输出 |

检查项：认证状态、连接延迟、权限、表访问。

---

## 智能分析

### analyze — 深度 Schema 分析

```bash
./script/bitable analyze "<URL>" [--sample-size N] [--json]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<URL>` | 包含 `?table=tblXXX` 的完整 URL | 必填 |
| `--sample-size` | 采样记录数 | 100 |
| `--json` | JSON 格式输出 | 否 |

输出：字段分类（状态/人员/日期/内容/标题）、填充率、文本平均长度、高频值、智能查询建议。

### list-tables — 列出所有表

```bash
./script/bitable list-tables "<URL>"
```

只需 base URL，不需要 `?table=` 参数。

---

## 数据查询

### query — 结构化查询

```bash
./script/bitable query "<URL>" [--filter <条件>...] [--field <字段>...] [--limit N] [--json]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--filter` | 筛选条件，可多次指定（AND 逻辑） | 无 |
| `--field` | 只返回指定字段，可多次指定 | 全部字段 |
| `--limit` | 最大返回记录数 | 无限制 |
| `--json` | JSON 格式输出 | 否 |

### smart-query — 自然语言查询

```bash
./script/bitable smart-query "<URL>" "<自然语言查询>" [--limit N] [--json]
```

自动解析查询意图：
- 识别人员名 → 匹配人员字段
- 识别关键词 → 匹配内容字段
- 识别状态词 → 匹配状态字段
- 识别时间词 → 匹配日期字段

### count — 统计记录数

```bash
./script/bitable count "<URL>" [--filter <条件>...]
```

---

## 数据表管理

### create-table — 创建数据表

```bash
./script/bitable create-table "<URL>" "<表名>" [--field <字段名:类型>...] [--description <描述>]
```

字段类型：`text`, `number`, `single_select`, `multi_select`, `date`, `checkbox`, `url`, `email`, `phone`, `rating`, `progress`, `currency`, `percent`

示例：
```bash
./script/bitable create-table "<URL>" "任务表" \
  --field "标题:text" \
  --field "状态:single_select" \
  --field "截止日期:date" \
  --field "参考链接:url"
```

### delete-table — 删除数据表

```bash
./script/bitable delete-table "<URL>" --table-id <id>
```

---

## 字段管理

### create-field — 创建字段

```bash
./script/bitable create-field "<URL>" "<字段名>" <类型> [--options <选项>] [--formatter <格式>]
```

| 参数 | 说明 |
|------|------|
| `--options` | 单选/多选字段的选项，逗号分隔 |
| `--formatter` | 数字字段的格式化方式 |

支持的字段类型：`text`, `number`, `single_select`, `multi_select`, `date`, `checkbox`, `url`, `email`, `phone`, `rating`, `progress`, `currency`, `percent`

示例：
```bash
./script/bitable create-field "<URL>" "优先级" single_select --options "高,中,低"
./script/bitable create-field "<URL>" "官网" url
./script/bitable create-field "<URL>" "联系邮箱" email
```

### update-field — 更新字段名

```bash
./script/bitable update-field "<URL>" --field-id <id> --name <新名称>
```

### delete-field — 删除字段

```bash
./script/bitable delete-field "<URL>" --field-id <id>
```

---

## 记录管理

### create-record — 创建单条记录

```bash
./script/bitable create-record "<URL>" --data '<JSON>'
```

示例：
```bash
./script/bitable create-record "<URL>" \
  --data '{"标题": "新任务", "状态": "待处理", "描述": "详细说明..."}'
```

### batch-create — 批量创建记录

```bash
./script/bitable batch-create "<URL>" --file <JSONL文件>
```

JSONL 文件格式（每行一个 JSON 对象）：
```
{"标题": "任务1", "状态": "待处理"}
{"标题": "任务2", "状态": "进行中"}
```

### get-record — 获取单条记录

```bash
./script/bitable get-record "<URL>" --record-id <id>
```

### update-record — 更新记录

```bash
./script/bitable update-record "<URL>" --record-id <id> --data '<JSON>'
```

### delete-record — 删除记录

```bash
./script/bitable delete-record "<URL>" --record-id <id>
```

---

## 导出

### export — 导出数据

```bash
./script/bitable export "<URL>" <输出文件> [--format json|csv] [--filter <条件>...]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<输出文件>` | 输出文件路径 | 必填 |
| `--format` | 输出格式 | json |
| `--filter` | 筛选条件 | 无 |

---

## 筛选语法详解

### 基本格式

| 格式 | 含义 | 示例 |
|------|------|------|
| `字段=值` | 精确匹配 | `--filter "状态=进行中"` |
| `字段:值` | 包含（模糊搜索） | `--filter "聊天记录:关键词"` |

字段名本身含 `=` 或 `:` 时，用反斜杠转义：`--filter "字段\\=名=值"`

### 多条件组合

多个 `--filter` 自动使用 AND 逻辑：

```bash
./script/bitable query "<URL>" \
  --filter "状态=进行中" \
  --filter "优先级=高"
```

### 选择策略

| 场景 | 用法 |
|------|------|
| 精确匹配状态/分类/人员 | `字段=值` |
| 文本内容模糊搜索 | `字段:关键词` |
| 组合多个条件 | 多个 `--filter` |

---

## 字段值写入格式

`create-record` / `update-record` 的 `--data` JSON 中，各字段类型的正确写法：

| 字段类型 | 正确写法 | 说明 |
|----------|----------|------|
| text | `"标题"` | 普通字符串 |
| number | `42` 或 `3.14` | 数字，不要加引号 |
| single_select | `"进行中"` | 选项名字符串 |
| multi_select | `["标签A", "标签B"]` | 选项名数组 |
| checkbox | `true` / `false` | 布尔值 |
| date | `1704067200000` | Unix 毫秒时间戳 |
| url | `"https://..."` | 裸字符串，脚本自动转换为 `{"link":..., "text":...}` |
| email | `"user@example.com"` | 裸字符串，脚本自动转换 |
| phone | `"13800138000"` | 字符串 |
| rating | `3` | 整数（1-5） |
| progress | `75` | 整数（0-100） |
| currency | `99.9` | 数字 |
| percent | `0.75` | 小数（0-1） |

> URL 和 Email 字段传裸字符串时，脚本会自动包装为飞书要求的对象格式，无需手动处理。

---

## URL 格式

支持两种 URL 格式：

1. **Base URL**: `https://bghijixdo5.feishu.cn/base/appXXX?table=tblXXX`
2. **Wiki URL**: `https://bghijixdo5.feishu.cn/wiki/wikiXXX?table=tblXXX`

大部分命令需要 `?table=tblXXX` 参数，`list-tables` 和 `health-check` 除外。

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret |
