# gh CLI JSON 字段参考

常见字段名（gh CLI 的命名可能和直觉不同）

## Repository

| 常用名 | gh CLI 字段名 | 说明 |
|--------|--------------|------|
| Stars | `stargazerCount` | ❌ 不是 `stargazersCount` |
| Forks | `forkCount` | ❌ 不是 `forksCount` |
| Default Branch | `defaultBranchRef` | ❌ 不是 `defaultBranch`，返回对象 |
| Created At | `createdAt` | ✅ |
| Pushed At | `pushedAt` | ✅ |
| Language | `primaryLanguage` | 返回对象，取 `.name` |
| Description | `description` | ✅ |
| URL | `url` | ✅ |
| SSH URL | `sshUrl` | ✅ |

### Repository 查询示例

```bash
# 正确
gh repo view owner/repo --json name,description,stargazerCount,forkCount

# 获取语言名称
gh repo view owner/repo --json primaryLanguage --jq '.primaryLanguage.name'
```

## Search Results

| 常用名 | gh CLI 字段名 | 说明 |
|--------|--------------|------|
| Full Name | `fullName` | ✅ |
| Stars | `stargazerCount` | ❌ 注意单数 |
| Language | `language` | ✅ (字符串) |

### Search 查询示例

```bash
gh search repos "go" --json fullName,stargazerCount,language
```

## Issues

| 常用名 | gh CLI 字段名 | 说明 |
|--------|--------------|------|
| Number | `number` | ✅ |
| Title | `title` | ✅ |
| State | `state` | ✅ (OPEN/CLOSED) |
| Author | `author` | 返回对象，取 `.login` |
| Created At | `createdAt` | ✅ |
| Labels | `labels` | 数组 |

## PRs

| 常用名 | gh CLI 字段名 | 说明 |
|--------|--------------|------|
| Number | `number` | ✅ |
| Title | `title` | ✅ |
| State | `state` | ✅ |
| Files | `files` | 数组 |
| Additions | `additions` | 在 files 中 |
| Deletions | `deletions` | 在 files 中 |

### PR 文件查询

```bash
gh pr view 123 --json files --jq '.files[].path'
```

## 查看所有可用字段

```bash
# 查看某个资源的所有可用字段
gh repo view owner/repo --json 2>&1 | grep -E '^\s+-' | head -30
```

## 常见错误

```bash
# ❌ 错误
gh repo view owner/repo --json stargazersCount
# Error: Unknown JSON field: "stargazersCount"

# ✅ 正确
gh repo view owner/repo --json stargazerCount
```
