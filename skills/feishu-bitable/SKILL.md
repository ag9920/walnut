---
name: feishu-bitable
description: 飞书多维表格数据操作工具。支持在现有 base 内查询、筛选、分页读取记录，创建数据表和字段，批量写入数据。提供表结构分析和健康检查功能。单次查询上限 500 条，单表支持 20 万行，单个字段支持 10 万字。
---

# Feishu Bitable Skill - 专业级多维表格数据库

## 核心定位：零代码关系型数据库

**不是表格，是数据库！**

飞书多维表格 = 零代码关系型数据库，具备以下特性：

| 特性 | 能力 | 使用场景 |
|------|------|----------|
| **大文本存储** | 单个格子 10 万字 | 存储完整文档、代码、日志 |
| **大数据量** | 单表 20 万行 | 聊天记录、操作日志、事件追踪 |
| **结构化查询** | 类 SQL 筛选 | 精准数据检索、统计分析 |
| **零运维** | 无需部署、自动备份 | 快速原型、临时数据存储 |

**本 Skill 专注于：**
- ✅ 在**用户提供的多维表格**内完成完整数据操作闭环
- ✅ 深度 Schema 分析，智能识别字段类型和查询策略
- ✅ 充分利用大文本、大数据量特性
- ❌ 不涉及：创建新的多维表格、权限转移

---

## 专业级使用流程

### Step 0: 健康检查（推荐）

**任何操作前，先确认连接和权限：**

```bash
# 检查认证和连接
./script/bitable health-check "https://bytedance.larkoffice.com/base/xxx"

# 输出示例：
# ✅ 健康检查报告
# ✓ authentication: 认证成功 (延迟: 245ms)
# ✓ connection: 连接成功 (延迟: 120ms)
# ✓ permissions: 权限正常 (表数量: 5)
# ✓ table_access: 表访问正常 (字段数: 9, 记录数: 2360)
# 总体状态: HEALTHY
```

### Step 1: 深度 Schema 分析（必须）

**使用 `analyze` 命令获取表结构深度洞察：**

```bash
./script/bitable analyze "https://bytedance.larkoffice.com/base/xxx?table=tblxxx"
```

**输出包含：**
- 字段分类（状态/人员/日期/内容/标题）
- 填充率统计
- 文本字段平均长度（判断是否适合存大文本）
- 高频值统计
- 智能查询建议

### Step 2: 根据数据特征选择查询策略

#### 场景 A：大文本模糊搜索（自然语言方式）
```bash
# 方式 1: 使用 smart-query 自然语言查询（推荐）
./script/bitable smart-query "<URL>" "查找张三关于 openclaw 的讨论" --limit 20

# 方式 2: 使用传统 query 命令
./script/bitable query "<URL>" \
  --filter "聊天记录:openclaw" \
  --field "聊天记录" \
  --field "发送人" \
  --field "发送时间" \
  --limit 20
```

**smart-query 会自动：**
- 识别 "张三" → 匹配人员字段（发送人/负责人/作者）
- 识别 "openclaw" → 匹配内容字段（聊天记录/内容/描述）
- 自动选择返回字段（内容 + 人员 + 时间）
- 构建并执行筛选查询

#### 场景 B：结构化筛选
```bash
# 筛选状态为"进行中"且优先级为"高"的任务
./script/bitable query "<URL>" \
  --filter "状态=进行中" \
  --filter "优先级=高" \
  --limit 50
```

#### 场景 C：分页获取大数据量
```bash
# 先统计总数
./script/bitable count "<URL>" --filter "类型=错误日志"

# 分页获取（每次 500 条，自动处理分页）
./script/bitable query "<URL>" \
  --filter "类型=错误日志" \
  --limit 1000
```

### Step 3: 数据写入（充分利用大文本特性）

#### 写入大段文本（文档、代码、日志）
```bash
# 存储完整文档
./script/bitable create-record "<URL>" \
  --data '{
    "文档标题": "API 设计文档",
    "文档内容": "<这里可以放 10 万字的完整文档...>",
    "作者": "张三",
    "版本": "v1.0"
  }'

# 存储代码片段
./script/bitable create-record "<URL>" \
  --data '{
    "函数名": "process_data",
    "代码": "<完整代码，可长达数千行...>",
    "说明": "<详细的功能说明和使用示例...>"
  }'
```

#### 批量写入大数据量
```bash
# 准备 JSONL 文件（每行一个记录）
# data.jsonl:
# {"日志内容": "...", "时间": "2024-01-01", "级别": "INFO"}
# {"日志内容": "...", "时间": "2024-01-01", "级别": "ERROR"}

./script/bitable batch-create "<URL>" --file data.jsonl
```

---

## 完整 CLI 参考

### 前置检查
```bash
./script/bitable health-check "<URL>"          # 健康检查
```

### 智能分析
```bash
./script/bitable analyze "<URL>"               # 深度 Schema 分析
./script/bitable analyze "<URL>" --sample-size 200  # 采样 200 条分析
./script/bitable list-tables "<URL>"           # 列出所有表
```

### 数据查询
```bash
./script/bitable query "<URL>" [--filter <条件>] [--field <字段>] [--limit <数量>]
./script/bitable smart-query "<URL>" "<自然语言查询>" [--limit <数量>]  # 自然语言智能查询
./script/bitable count "<URL>" [--filter <条件>]
```

### 数据表管理
```bash
./script/bitable create-table "<URL>" "<表名>" [--field <字段定义>...]
./script/bitable delete-table "<URL>" --table-id <id>
```

### 字段管理
```bash
./script/bitable create-field "<URL>" "<字段名>" <类型> [--options <选项>]
./script/bitable delete-field "<URL>" --field-id <id>
```

### 记录管理
```bash
./script/bitable create-record "<URL>" --data '<JSON>'
./script/bitable batch-create "<URL>" --file <jsonl文件>
./script/bitable update-record "<URL>" --record-id <id> --data '<JSON>'
./script/bitable delete-record "<URL>" --record-id <id>
```

---

## 筛选语法

| 格式 | 含义 | 示例 | 适用场景 |
|------|------|------|----------|
| `字段=值` | 等于 | `--filter "状态=进行中"` | 状态、分类、人员等精确匹配 |
| `字段:值` | 包含 | `--filter "聊天记录:关键词"` | 文本内容的模糊搜索 |

**多条件组合：** 多个 `--filter` 自动使用 AND 逻辑

---

## 典型专业场景

### 场景 1：聊天记录分析（大数据量 + 大文本）

```bash
# 1. 健康检查
./script/bitable health-check "<URL>"

# 2. 深度分析表结构
./script/bitable analyze "<URL>"

# 3. 统计关于 openclaw 的讨论数量
./script/bitable count "<URL>" --filter "聊天记录:openclaw"

# 4. 获取具体讨论内容
./script/bitable query "<URL>" \
  --filter "聊天记录:openclaw" \
  --field "聊天记录" \
  --field "发送人" \
  --field "发送时间" \
  --limit 20
```

**关键点：**
- 聊天记录字段可能包含数千字，充分利用大文本特性
- 使用模糊搜索 `:openclaw` 而非精确匹配
- 只获取需要的字段，减少数据传输

### 场景 2：知识库管理（大文本存储）

```bash
# 创建知识库表
./script/bitable create-table "<URL>" "技术文档库" \
  --field "文档标题:text" \
  --field "文档内容:text" \
  --field "作者:text" \
  --field "标签:multi_select" \
  --field "版本:text"

# 写入完整文档（内容可长达 10 万字）
./script/bitable create-record "<URL>?table=tblxxx" \
  --data '{
    "文档标题": "系统架构设计",
    "文档内容": "<完整的架构文档，包含设计思路、技术选型、部署方案...>",
    "作者": "张三",
    "标签": ["架构", "设计文档"],
    "版本": "v2.0"
  }'

# 搜索文档
./script/bitable query "<URL>" \
  --filter "文档内容:微服务" \
  --field "文档标题" \
  --field "作者"
```

### 场景 3：日志分析（大数据量写入）

```bash
# 创建日志表
./script/bitable create-table "<URL>" "应用日志" \
  --field "时间:date" \
  --field "级别:single_select" \
  --field "内容:text" \
  --field "服务:text"

# 添加级别选项
./script/bitable create-field "<URL>" "级别" single_select \
  --options "DEBUG,INFO,WARN,ERROR,FATAL"

# 批量导入日志（支持 20 万行）
./script/bitable batch-create "<URL>" --file app_logs.jsonl

# 查询错误日志
./script/bitable query "<URL>" \
  --filter "级别=ERROR" \
  --filter "内容:数据库连接" \
  --limit 100
```

---

## 数据库思维最佳实践

### 1. 把多维表格当作 NoSQL 数据库

**不要：** 只存短文本，当作 Excel 用
**要：** 充分利用大文本特性，存储完整文档、代码、日志

```bash
# ❌ 不好：只存摘要
{"文档": "架构设计文档的摘要..."}

# ✅ 好：存完整内容
{"文档": "<完整的 5 万字架构设计文档>"}
```

### 2. 利用 Schema 分析优化查询

**先 analyze，再 query：**

```bash
# 1. 分析表结构
./script/bitable analyze "<URL>"

# 2. 根据分析结果选择最佳查询字段
# 如果 analyze 显示 "发送人" 字段填充率 100%，优先用它筛选
./script/bitable query "<URL>" --filter "发送人=张三"
```

### 3. 大数据量处理策略

| 数据量 | 策略 | 命令 |
|--------|------|------|
| < 1000 条 | 直接查询 | `query --limit 1000` |
| 1000-10000 条 | 分页获取 | `query --limit 500` 多次执行 |
| > 10000 条 | 先筛选再获取 | `count` 统计后 `query --filter` |

### 4. 字段命名规范

**利于智能识别的命名：**
- 状态字段：包含 "状态/status/进度/stage"
- 人员字段：包含 "人/负责人/owner"
- 日期字段：包含 "日期/时间/date/time"
- 内容字段：包含 "内容/描述/详情/content"

---

## 限制说明

### 本 Skill 不支持
- ❌ 创建新的多维表格（`create-app`）
- ❌ 删除整个多维表格
- ❌ 权限转移、协作者管理

### 技术限制
- 单次查询最多 500 条（自动分页可获取更多）
- 单表建议不超过 20 万行
- 不支持事务回滚
- 不支持跨表 JOIN

---

## 错误处理

### 认证错误
```
错误: tenant access token 无效
→ 运行 ./script/bitable health-check 检查凭证
→ 确认 FEISHU_APP_ID 和 FEISHU_APP_SECRET 已配置
```

### 权限错误
```
错误: 没有权限访问此资源
→ 请将应用添加为多维表格的协作者
→ 检查多维表格的分享设置
```

### 字段不存在
```
错误: InvalidFilter - 字段 '对话内容' 不存在
→ 运行 ./script/bitable analyze "<URL>" 查看准确字段名
→ 可能实际字段名为 '聊天记录'
```

---

## 快速开始

```bash
# 1. 配置凭证
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"

# 2. 健康检查
./script/bitable health-check "https://bytedance.larkoffice.com/base/xxx"

# 3. 分析表结构
./script/bitable analyze "https://bytedance.larkoffice.com/base/xxx"

# 4. 开始查询
./script/bitable query "<URL>" --limit 10
```
