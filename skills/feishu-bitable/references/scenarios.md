# 典型场景与最佳实践

## 场景 1：聊天记录分析（大数据量 + 大文本）

```bash
# 1. 健康检查
./script/bitable health-check "<URL>"

# 2. 深度分析表结构
./script/bitable analyze "<URL>?table=tblXXX"

# 3. 统计关于某话题的讨论数量
./script/bitable count "<URL>?table=tblXXX" --filter "聊天记录:openclaw"

# 4. 获取具体讨论内容
./script/bitable query "<URL>?table=tblXXX" \
  --filter "聊天记录:openclaw" \
  --field "聊天记录" \
  --field "发送人" \
  --field "发送时间" \
  --limit 20

# 5. 或者用自然语言查询
./script/bitable smart-query "<URL>?table=tblXXX" "查找张三关于 openclaw 的讨论" --limit 20
```

要点：
- 聊天记录字段可能包含数千字，充分利用大文本特性
- 使用模糊搜索 `:关键词` 而非精确匹配
- 只获取需要的字段，减少数据传输

---

## 场景 2：知识库管理（大文本存储）

```bash
# 创建知识库表（支持 url 字段类型）
./script/bitable create-table "<URL>" "技术文档库" \
  --field "文档标题:text" \
  --field "文档内容:text" \
  --field "作者:text" \
  --field "标签:multi_select" \
  --field "版本:text" \
  --field "参考链接:url"

# 写入完整文档（内容可长达 10 万字，url 字段传裸字符串即可）
./script/bitable create-record "<URL>?table=tblxxx" \
  --data '{
    "文档标题": "系统架构设计",
    "文档内容": "<完整的架构文档，包含设计思路、技术选型、部署方案...>",
    "作者": "张三",
    "标签": ["架构", "设计文档"],
    "版本": "v2.0",
    "参考链接": "https://example.com/arch-doc"
  }'

# 搜索文档
./script/bitable query "<URL>?table=tblxxx" \
  --filter "文档内容:微服务" \
  --field "文档标题" \
  --field "作者"
```

---

## 场景 3：日志分析（大数据量写入）

```bash
# 创建日志表
./script/bitable create-table "<URL>" "应用日志" \
  --field "时间:date" \
  --field "级别:single_select" \
  --field "内容:text" \
  --field "服务:text"

# 添加级别选项
./script/bitable create-field "<URL>?table=tblxxx" "级别" single_select \
  --options "DEBUG,INFO,WARN,ERROR,FATAL"

# 批量导入日志（JSONL 格式，date 字段用 Unix 毫秒时间戳）
# app_logs.jsonl 示例：
# {"时间": 1704067200000, "级别": "ERROR", "内容": "数据库连接失败", "服务": "api"}
./script/bitable batch-create "<URL>?table=tblxxx" --file app_logs.jsonl

# 查询错误日志
./script/bitable query "<URL>?table=tblxxx" \
  --filter "级别=ERROR" \
  --filter "内容:数据库连接" \
  --limit 100

# 导出分析（CSV 使用 utf-8-sig 编码，可直接用 Excel 打开）
./script/bitable export "<URL>?table=tblxxx" errors.csv --format csv --filter "级别=ERROR"
```

---

## 场景 4：阅读笔记 / 内容管理

```bash
# 写入带 URL 来源的笔记（url 字段传裸字符串，脚本自动转换格式）
./script/bitable create-record "<URL>?table=tblxxx" \
  --data '{
    "知识点": "文章标题",
    "说明": "核心观点和笔记内容...",
    "源链接": "https://example.com/article"
  }'

# 按关键词搜索笔记
./script/bitable query "<URL>?table=tblxxx" \
  --filter "说明:Agent" \
  --field "知识点" \
  --field "说明"
```

---

## 最佳实践

### 1. 把多维表格当作 NoSQL 数据库

不要只存短文本当 Excel 用，充分利用大文本特性存储完整文档、代码、日志。

```bash
# ❌ 只存摘要
{"文档": "架构设计文档的摘要..."}

# ✅ 存完整内容（单字段支持 10 万字）
{"文档": "<完整的 5 万字架构设计文档>"}
```

### 2. 先 analyze 再 query

```bash
# 1. 分析表结构，了解字段分类和填充率
./script/bitable analyze "<URL>?table=tblxxx"

# 2. 根据分析结果选择最佳查询字段
# 如果 analyze 显示 "发送人" 字段填充率 100%，优先用它筛选
./script/bitable query "<URL>?table=tblxxx" --filter "发送人=张三"
```

### 3. 大数据量处理策略

| 数据量 | 策略 | 命令 |
|--------|------|------|
| < 1000 条 | 直接查询 | `query --limit 1000` |
| 1000-10000 条 | 加筛选条件 | `query --filter "状态=进行中"` |
| > 10000 条 | 先统计再筛选 | `count` 后 `query --filter` |
| 全量导出 | 导出文件 | `export output.json` |

### 4. 字段命名规范

利于智能识别的命名：
- 状态字段：包含 "状态/status/进度/stage"
- 人员字段：包含 "人/负责人/owner"
- 日期字段：包含 "日期/时间/date/time"
- 内容字段：包含 "内容/描述/详情/content/记录/聊天"

### 5. 字段值写入要点

| 字段类型 | 写法 | 注意 |
|----------|------|------|
| url | `"https://..."` | 脚本自动转换，直接传字符串 |
| email | `"user@example.com"` | 脚本自动转换，直接传字符串 |
| date | `1704067200000` | 必须是 Unix 毫秒时间戳，不能传字符串 |
| multi_select | `["A", "B"]` | 数组格式，不能传逗号分隔字符串 |
| number | `42` | 数字类型，不要加引号 |
