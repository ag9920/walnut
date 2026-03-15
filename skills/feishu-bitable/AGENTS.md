# Feishu Bitable Skill - Agent 开发文档

## 项目概述

飞书多维表格 CLI 工具 Skill，通过命令行接口完整操作多维表格的库/表/字段/记录四个维度。

## 核心概念映射

| 多维表格概念 | 数据库概念 | CLI 操作层级 |
|-------------|-----------|-------------|
| App (多维表格) | Database | 库的维度 |
| Table (数据表) | Table | 表的维度 |
| Field (字段) | Column | 字段维度 |
| Record (记录) | Row | 记录维度 |

## 工程结构

```
skills/feishu-bitable/
├── script/
│   └── bitable              # CLI 工具主文件（Python，无扩展名）
├── references/
│   ├── cli-reference.md     # 完整 CLI 命令参考（参数、示例）
│   └── scenarios.md         # 典型场景与最佳实践
├── SKILL.md                 # 面向 Agent 的 Skill 使用文档（精简版）
├── AGENTS.md                # 本文档：Agent 开发维护指南
└── requirements.txt         # Python 依赖：requests>=2.28.0
```

## CLI 工具架构

### 文件说明
- `script/bitable`: 单一文件自包含所有功能，约 2134 行 Python 代码
- 依赖：仅 `requests` 一个外部库

### 核心模块

1. **数据模型** (行 35-205)
   - `FieldType`, `UIType`, `Operator` — 枚举类型
   - `Field`, `Record`, `Table`, `App`, `BitableRef` — 数据实体
   - `Filter`, `FilterCondition`, `Sort` — 查询条件
   - `PaginatedResult` — 分页结果泛型

2. **异常体系** (行 212-315)
   - `BitableError` — 基础异常
   - `AuthenticationError`, `TokenExpiredError` — 认证相关
   - `ResourceNotFoundError` 及子类 — 资源不存在
   - `RateLimitError`, `ConflictError`, `ServerError` — 限流/冲突/服务端
   - `ValidationError` — 字段格式错误（含 URLFieldConvFail 等）
   - `raise_for_error()` — 统一错误码映射，优先使用中文提示

3. **WikiResolver** (行 320) — 将 Wiki Token 转换为 Bitable Token

4. **BitableClient** (行 352) — Token 自动获取和刷新（线程安全）、HTTP 请求封装（含重试机制）、URL 解析

5. **四个维度的操作类** (行 498-945)
   - `AppOperations` (行 498): create, get_metadata, list_tables
   - `TableOperations` (行 558): create, update, delete
   - `FieldOperations` (行 604): list, get_schema, create, update, delete
   - `RecordOperations` (行 696): CRUD + search + iter_all + count + batch_create/update/delete
     - `_get_schema()`: 带进程内缓存的 schema 获取
     - `_coerce_fields()`: 字段值自动类型转换（URL/Email 裸字符串 → 对象）

6. **CLI 命令处理** (行 946-1295)
   - `main()`: argparse 命令解析，所有子命令定义
   - `handle_command()`: 命令分发，含 table_id 校验和 JSON 输入校验

7. **工具函数** (行 1296-1370)
   - `_parse_field_type()`: 字段类型字符串映射（支持 13 种类型，未知类型抛 ValueError）
   - `_require_table_id()`: URL 中 table_id 必填校验
   - `_build_filter()`: 筛选条件构建（支持 `=`/`:` 操作符，支持反斜杠转义）

8. **命令处理函数** (行 1372-2134)
   - `_handle_health_check()` (行 1372): 健康检查（认证/连接/权限/表访问）
   - `_serialize_field_value()` (行 1538): 字段值序列化（富文本/人员/URL/附件 → 可读字符串）
   - `_handle_query()` (行 1579): 结构化查询
   - `_handle_smart_query()` (行 1611): 自然语言查询（含 `_parse_natural_language`）
   - `_handle_analyze()` (行 1800): 深度 Schema 分析（含 `_analyze_field_statistics`、`_categorize_field`）
   - `_handle_export()` (行 2099): JSON/CSV 导出（CSV 使用 utf-8-sig 编码）

## 关键设计决策

1. **单一文件自包含** — 所有功能在 `script/bitable` 一个文件中，便于分发
2. **Token 自动管理** — 自动获取/刷新 tenant_access_token，线程安全缓存，Token 刷新最多重试 1 次防止无限循环
3. **写操作序列化** — 每个表独立写锁，防止并发冲突
4. **Schema 缓存** — `RecordOperations._get_schema()` 在同一次 CLI 调用内缓存字段 schema，batch_create 不会重复拉取
5. **字段值自动转换** — `_coerce_fields()` 在写入前自动将 URL/Email 裸字符串包装为飞书要求的对象格式
6. **类型感知分类** — `_categorize_field()` 优先按 `field.type` 判断，再按字段名关键词兜底
7. **输入校验** — table_id 必填校验、JSON 格式校验（含 JSONL 逐行报错）、字段定义格式校验、筛选条件格式警告

## 支持的字段类型

| 类型标识 | FieldType | 说明 |
|---------|-----------|------|
| text | TEXT | 文本，支持最多 10 万字 |
| number | NUMBER | 数字 |
| single_select | SINGLE_SELECT | 单选 |
| multi_select | MULTI_SELECT | 多选 |
| date | DATE | 日期（Unix 毫秒时间戳） |
| checkbox | CHECKBOX | 复选框 |
| url | URL | 链接（自动转换裸字符串） |
| email | EMAIL | 邮箱（自动转换裸字符串） |
| phone | PHONE | 电话 |
| rating | RATING | 评分 |
| progress | PROGRESS | 进度 |
| currency | CURRENCY | 货币 |
| percent | PERCENT | 百分比 |

只读/系统字段（USER、ATTACHMENT、LINK、DUPLEX_LINK、FORMULA 等）可读取但不支持通过 CLI 创建。

## 扩展指南

### 添加新命令
1. 在 `main()` 中添加子命令解析器
2. 在 `handle_command()` 中添加命令处理逻辑
3. 如需 table_id，调用 `_require_table_id(ref)`

### 添加新字段类型（可创建）
1. 在 `FieldType` 枚举中确认类型已存在
2. 在 `UIType` 枚举中确认 UI 类型已存在
3. 在 `_parse_field_type()` 中添加映射
4. 在 `create-field` 的 `choices` 列表中添加

### 添加字段值自动转换
在 `RecordOperations._coerce_fields()` 中添加对应 `FieldType` 的转换逻辑。

### 添加新筛选操作符
1. 在 `Operator` 枚举中添加操作符
2. 在 `_build_filter()` 中添加解析逻辑（当前只支持 `=` 和 `:`，可扩展为 `>=`、`<=` 等）

## 已知限制

- 不支持创建新的多维表格（只能在现有 base 内操作）
- 不支持权限转移、事务回滚、跨表 JOIN
- USER/ATTACHMENT/LINK 字段写入需手动构造正确格式（脚本不自动转换）
- `smart-query` 的自然语言解析基于正则，复杂查询建议用 `query --filter`

## 参考资料

- [飞书多维表格 OpenAPI 文档](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview)
- [SKILL.md](./SKILL.md) — Agent 使用文档
- [references/cli-reference.md](./references/cli-reference.md) — 完整 CLI 参考
- [references/scenarios.md](./references/scenarios.md) — 典型场景
