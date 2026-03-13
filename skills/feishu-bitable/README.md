# Feishu Bitable Skill

飞书多维表格 CLI 工具 - 将多维表格作为零代码关系型数据库使用。

## 核心思想

**多维表格 = 零代码关系型数据库**

- **App** = Database（数据库）
- **Table** = Table（表）
- **Field** = Column（列）
- **Record** = Row（行）

## 快速开始

### 1. 配置凭证

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### 2. 使用 CLI

```bash
# 智能分析多维表格
./script/bitable summary "https://bytedance.larkoffice.com/wiki/xxx"

# 查询记录
./script/bitable query "https://..." --filter "状态=进行中"

# 创建记录
./script/bitable create-record "https://..." --data '{"名称":"任务1"}'
```

## 工程结构

```
.
├── script/
│   └── bitable          # CLI 工具（自包含，单一文件）
├── SKILL.md             # Skill 文档
├── requirements.txt     # 依赖：requests
└── README.md           # 本文件
```

## 依赖

- Python 3.8+
- requests >= 2.28.0

## 完整功能

### 库的维度
- `create-app` - 创建多维表格
- `list-tables` - 列出所有数据表
- `create-table` - 创建数据表
- `update-table` - 更新数据表
- `delete-table` - 删除数据表

### 字段维度
- `create-field` - 创建字段
- `update-field` - 更新字段
- `delete-field` - 删除字段

### 记录维度
- `create-record` - 创建记录
- `batch-create` - 批量创建记录
- `get-record` - 获取单条记录
- `update-record` - 更新记录
- `delete-record` - 删除记录

### 查询和分析
- `summary` - 智能分析多维表格
- `query` - 查询记录（支持筛选、分页）
- `count` - 统计记录数
- `export` - 导出数据（JSON/CSV）

## 特性

- **完整 CRUD**：库/表/字段/记录 四个维度全覆盖
- **自动分页**：查询自动处理分页
- **批量操作**：每批最多 500 条
- **Wiki Token 转换**：自动识别 wiki URL
- **Token 自动管理**：自动获取、缓存、刷新
- **智能分析**：自动识别字段类型，生成查询建议
- **写操作序列化**：防止并发冲突

## 详细文档

参见 [SKILL.md](./SKILL.md)
