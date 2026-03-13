# Feishu Bitable Skill - Agent 开发文档

## 项目概述

这是一个将飞书多维表格作为零代码关系型数据库使用的 CLI 工具 Skill。通过命令行接口，Agent 可以完整操作多维表格的库/表/字段/记录四个维度。

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
├── SKILL.md                 # 面向用户的 Skill 使用文档
├── AGENTS.md               # 本文档：Agent 开发维护指南
├── insight.md              # 原始需求文档（核心思想来源）
└── requirements.txt        # Python 依赖：requests>=2.28.0
```

## CLI 工具架构

### 文件说明
- `script/bitable`: 单一文件自包含所有功能，1342 行 Python 代码
- 包含：数据模型、异常处理、HTTP 客户端、四个维度的操作类、CLI 命令解析
- 依赖：仅 `requests` 一个外部库

### 核心模块

1. **数据模型** (行 32-130)
   - `FieldType`, `UIType`, `Operator` - 枚举类型
   - `Field`, `Record`, `Table`, `App` - 数据实体
   - `Filter`, `FilterCondition`, `Sort` - 查询条件
   - `BitableRef` - URL 解析结果

2. **异常体系** (行 133-200)
   - `BitableError` - 基础异常
   - `AuthenticationError`, `TokenExpiredError` - 认证相关
   - `ResourceNotFoundError` 及其子类 - 资源不存在
   - `RateLimitError`, `ConflictError` - 限流和并发冲突

3. **WikiResolver** (行 203-220)
   - 将 Wiki Token 转换为 Bitable Token

4. **BitableClient** (行 223-350)
   - Token 自动获取和刷新
   - HTTP 请求封装（含重试机制）
   - URL 解析（支持 wiki 和 base 两种 URL）

5. **四个维度的操作类**
   - `AppOperations` (行 353-400): create, get_metadata, list_tables
   - `TableOperations` (行 403-440): create, update, delete
   - `FieldOperations` (行 443-500): list, create, update, delete
   - `RecordOperations` (行 503-680): CRUD + search + iter_all + count

6. **CLI 命令处理** (行 683-900)
   - argparse 命令解析
   - 命令分发到对应操作

## 能力清单

### 已实现（对应 insight.md 要求）

**库的维度**
- ✅ `create-app` - 创建多维表格
- ✅ `list-tables` - 列出所有表
- ✅ `create-table` - 创建表（支持初始字段）
- ✅ `update-table` - 更新表名
- ✅ `delete-table` - 删除表

**表的维度**
- ✅ `create-field` - 创建字段
- ✅ `create-record` / `batch-create` - 写入数据
- ✅ `query` / `get-record` - 查询数据（支持分页、筛选）
- ✅ `update-record` - 更新数据
- ✅ `delete-record` - 删除数据

**字段维度**
- ✅ `create-field` - 创建字段
- ✅ `update-field` - 更新字段
- ✅ `delete-field` - 删除字段

**记录维度**
- ✅ `create-record` / `batch-create` - 创建
- ✅ `query` / `get-record` - 查询
- ✅ `update-record` - 更新
- ✅ `delete-record` - 删除

**智能功能**
- ✅ `summary` - 智能分析表结构、字段分类、生成查询建议
- ✅ `count` - 统计记录数
- ✅ `export` - 导出 JSON/CSV

### 未实现（insight.md 提及但未要求 CLI）
- 转移协作人/添加用户/移除用户（需要额外的权限管理 API）

## 关键设计决策

### 1. 单一文件自包含
- 所有功能在一个 `script/bitable` 文件中
- 不依赖 src/ 目录或其他模块
- 便于分发和部署

### 2. Token 自动管理
- 自动获取 tenant_access_token
- 自动刷新过期 token
- 线程安全的 token 缓存

### 3. 写操作序列化
- 每个表有独立的写锁
- 防止并发冲突（错误码 2001254291）

### 4. 渐进式信息获取
- `summary` 命令智能分析字段类型
- 识别状态字段、分类字段、人员字段、内容字段
- 生成针对性的查询建议

### 5. 筛选条件简化
- `字段=值` - 等于（精确匹配）
- `字段:值` - 包含（模糊搜索）
- 多条件自动 AND 组合

## 扩展指南

### 添加新命令

1. 在 `main()` 函数中添加子命令解析器
2. 在 `handle_command()` 中添加命令处理逻辑
3. 如有需要，在对应 Operations 类中添加方法

### 添加新字段类型

1. 在 `FieldType` 枚举中添加类型
2. 在 `UIType` 枚举中添加 UI 类型
3. 在 `_parse_field_type()` 函数中添加映射

### 添加新筛选操作符

1. 在 `Operator` 枚举中添加操作符
2. 在 `_build_filter()` 函数中添加解析逻辑

## 测试建议

由于 CLI 工具依赖飞书 API，建议：

1. **单元测试**：使用 mock 测试数据模型和工具函数
2. **集成测试**：使用测试用的 app_id/app_secret 进行端到端测试
3. **手动测试**：使用提供的测试凭证
   - App ID: `cli_a5f96efe323dd013`
   - App Secret: `nNqZPi5NCVttBw8opCnthgXVMJjZ1J8A`

## 常见问题

### Q: 为什么 CLI 文件没有 .py 扩展名？
A: Unix 惯例，通过 shebang (`#!/usr/bin/env python3`) 指定解释器，使命令看起来像系统工具。

### Q: 如何处理 API 限流？
A: 已内置指数退避重试机制，遇到 429 错误会自动重试。

### Q: 如何支持新的飞书 API 功能？
A: 在对应 Operations 类中添加方法，遵循现有模式：构建 URL -> 构建 payload -> 调用 `_request()` -> 解析响应。

## 参考资料

- [飞书多维表格 OpenAPI 文档](https://open.larkoffice.com/document/server-docs/docs/bitable-v1/bitable-overview)
- [insight.md](./insight.md) - 原始需求文档
- [SKILL.md](./SKILL.md) - 用户使用文档
