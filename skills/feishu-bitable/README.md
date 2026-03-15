# Feishu Bitable Skill

飞书多维表格 CLI 工具 - 将多维表格作为零代码关系型数据库使用。

## 核心思想

**多维表格 = 零代码关系型数据库**

- **App** = Database（数据库）
- **Table** = Table（表）
- **Field** = Column（列）
- **Record** = Row（行）

单字段支持 10 万字、单表 20 万行、类 SQL 筛选。

## 快速开始

### 1. 配置凭证

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### 2. 使用 CLI

```bash
# 健康检查
./script/bitable health-check "https://bghijixdo5.feishu.cn/base/xxx"

# 深度分析表结构
./script/bitable analyze "https://...?table=tblXXX"

# 查询记录
./script/bitable query "https://...?table=tblXXX" --filter "状态=进行中"

# 创建记录（URL 字段传裸字符串，自动转换格式）
./script/bitable create-record "https://...?table=tblXXX" \
  --data '{"标题": "任务1", "源链接": "https://example.com"}'

# 批量导入
./script/bitable batch-create "https://...?table=tblXXX" --file data.jsonl

# 导出 CSV（utf-8-sig 编码，Excel 可直接打开）
./script/bitable export "https://...?table=tblXXX" output.csv --format csv
```

## 工程结构

```
.
├── script/
│   └── bitable              # CLI 工具（自包含，单一 Python 文件，~2100 行）
├── references/
│   ├── cli-reference.md     # 完整 CLI 参数说明
│   └── scenarios.md         # 典型场景与最佳实践
├── SKILL.md                 # 面向 Agent 的使用文档
├── AGENTS.md                # 开发维护指南
├── requirements.txt         # 依赖：requests>=2.28.0
└── README.md                # 本文件
```

## 依赖

- Python 3.8+
- requests >= 2.28.0

## 完整功能

### 库的维度
- `list-tables` — 列出所有数据表
- `create-table` — 创建数据表（支持初始字段定义）
- `update-table` — 更新数据表名
- `delete-table` — 删除数据表

### 字段维度
- `create-field` — 创建字段（支持 13 种类型）
- `update-field` — 更新字段名
- `delete-field` — 删除字段

支持的字段类型：`text`, `number`, `single_select`, `multi_select`, `date`, `checkbox`, `url`, `email`, `phone`, `rating`, `progress`, `currency`, `percent`

### 记录维度
- `create-record` — 创建单条记录
- `batch-create` — 批量创建（JSONL，每批 500 条）
- `get-record` — 获取单条记录
- `update-record` — 更新记录
- `delete-record` — 删除记录

### 查询和分析
- `health-check` — 认证/连接/权限/表访问四层检查
- `analyze` — 深度 Schema 分析（字段分类、填充率、高频值、查询建议）
- `query` — 结构化查询（筛选 + 分页 + 字段选择）
- `smart-query` — 自然语言智能查询
- `count` — 统计记录数
- `export` — 导出 JSON/CSV

## 核心特性

- **字段值自动转换**：URL/Email 字段传裸字符串，脚本自动包装为飞书要求的对象格式
- **Schema 缓存**：同一次调用内缓存字段 schema，batch_create 不重复拉取
- **类型感知分类**：`analyze` 优先按字段类型分类，URL 字段显示 🔗，数字字段显示 🔢
- **智能输出**：富文本/人员/附件字段自动提取可读文本，不显示原始 dict
- **Token 自动管理**：自动获取、缓存、刷新，Token 刷新最多重试 1 次防止无限循环
- **写操作序列化**：每个表独立写锁，防止并发冲突
- **CSV 兼容性**：使用 utf-8-sig 编码，Excel 可直接打开中文内容
- **筛选转义**：字段名含 `=` 或 `:` 时支持反斜杠转义

## 详细文档

- 完整 CLI 参数说明 → [references/cli-reference.md](./references/cli-reference.md)
- 典型场景与最佳实践 → [references/scenarios.md](./references/scenarios.md)
- Agent 使用文档 → [SKILL.md](./SKILL.md)
- 开发维护指南 → [AGENTS.md](./AGENTS.md)
