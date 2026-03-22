---
name: github
description: Use when working with GitHub repositories, issues, pull requests, code review, or any GitHub operations. Provides remote GitHub API/CLI access for browsing, creating, and managing resources. Requires user to provide GitHub authentication.
---

# GitHub Skill

## Overview

Complete GitHub workflow support via `gh` CLI and GitHub API. **All operations are remote** - no local repository needed.

**Key Capabilities:**
- Browse code, issues, PRs on any public/private repo
- Create issues, PRs, comments
- Review and merge PRs
- Search repositories and users
- View repository metadata and analytics

---

## Authentication (Required)

You **MUST** ask the user for GitHub credentials before performing any write operations (create issue/PR/comment). Read operations on public repos may work without auth.

### Method 1: GitHub Token (Recommended)

Ask user for a Personal Access Token:

> "To create this issue, I need a GitHub Personal Access Token. You can create one at https://github.com/settings/tokens with `repo` and `write:discussion` permissions. Please provide your token:"

```bash
# Set token for gh CLI
echo "YOUR_TOKEN" | gh auth login --with-token

# Or set as environment variable
export GH_TOKEN="your_token_here"
```

### Method 2: Browser Login

```bash
gh auth login
# Follow the prompts to authenticate via browser
```

### Verify Authentication

```bash
gh auth status
# Should show: "Logged in to github.com as USERNAME"
```

---

## Core Commands

### Read Operations (Public repos often work without auth)

**View repository info:**
```bash
gh repo view owner/repo --json name,description,stargazerCount,primaryLanguage
```

**List files in directory:**
```bash
gh api repos/owner/repo/contents/path/to/dir | jq -r '.[].name'
```

**View file content:**
```bash
gh api repos/owner/repo/contents/README.md | jq -r '.content' | base64 -d
```

**List issues:**
```bash
gh issue list --repo owner/repo --limit 20 --state open
```

**View issue with comments:**
```bash
gh issue view 123 --repo owner/repo --comments
```

**View PR diff:**
```bash
gh pr view 456 --repo owner/repo --patch
```

**List changed files in PR:**
```bash
gh pr view 456 --repo owner/repo --json files | jq '.files[].path'
```

**Search repositories:**
```bash
gh search repos "react state management" --language typescript --sort stars
```

### Write Operations (Require authentication)

**Create an issue:**
```bash
gh issue create --repo owner/repo \
  --title "Bug: memory leak in retry logic" \
  --body "## Description

The fibonacci backoff uses recursive implementation..."
```

**Create issue from file:**
```bash
cat > /tmp/issue.md << 'EOF'
## Performance Issue

Fibonacci calculation is O(2^n)...
EOF

gh issue create --repo owner/repo --title "Title" --body-file /tmp/issue.md
```

**Comment on issue:**
```bash
gh issue comment 123 --repo owner/repo --body "Thanks for reporting! Fixed in v2.0.0"
```

**Create PR:**
```bash
git checkout -b feature-branch
# ... make changes and commit ...
gh pr create --title "Fix: handle edge case" --body "## Changes
- Added validation
- Updated tests"
```

**Review PR:**
```bash
gh pr review 456 --repo owner/repo --approve --body "LGTM!"
gh pr review 456 --repo owner/repo --request-changes --body "Please add tests"
```

**Merge PR:**
```bash
gh pr merge 456 --repo owner/repo --squash
```

---

## Complete Workflows

### Workflow 1: Analyze Repository and Create Issue

```
1. Ask user: "I need a GitHub token to create issues. Please provide one or run 'gh auth login' first."

2. Verify auth: gh auth status

3. Analyze the repository (read operations):
   - View repo info
   - Read key files
   - Check existing issues to avoid duplicates

4. Create issue:
   gh issue create --repo owner/repo --title "..." --body "..."
```

### Workflow 2: Review and Merge PR

```bash
# 1. View PR overview
gh pr view 456 --repo owner/repo

# 2. See what changed
gh pr view 456 --repo owner/repo --json files

# 3. View the diff
gh pr view 456 --repo owner/repo --patch

# 4. Check CI status
gh pr checks 456 --repo owner/repo

# 5. Approve
gh pr review 456 --repo owner/repo --approve

# 6. Merge
gh pr merge 456 --repo owner/repo --squash
```

### Workflow 3: Create PR with Code Changes

**⚠️ Warning: PR body may contain special characters (like `[T]` for generics) that bash will interpret. Use `--body-file` approach.**

```bash
# Step 1: Clone and create branch
gh repo clone owner/repo /tmp/work-repo
cd /tmp/work-repo
git checkout -b feature/my-changes

# Step 2: Make changes to files...
# ... edit files ...

# Step 3: Commit and push
git add -A
git commit -m "feat: my changes"
git push origin feature/my-changes

# Step 4: Create PR description file
cat > /tmp/pr-body.md << 'ENDOFBODY'
## Summary

Description here...

## Changes
- Change 1
- Change 2

Closes #1
ENDOFBODY

# Step 5: Create PR using file (avoids bash escaping issues)
gh pr create \
  --repo owner/repo \
  --title "feat: my changes" \
  --body-file /tmp/pr-body.md \
  --base main \
  --head feature/my-changes

# Step 6: Cleanup
rm -rf /tmp/work-repo /tmp/pr-body.md
```

**Alternative: Use the safe-create-pr.py helper:**
```bash
python3 skills/github/scripts/safe-create-pr.py \
  --repo owner/repo \
  --title "feat: my changes" \
  --body-file /tmp/pr-body.md \
  --base main \
  --head feature/my-changes
```

### Workflow 4: Check My Issues/PRs

```bash
# Issues assigned to me
gh issue list --assignee "@me" --state open

# My PRs
gh pr list --author "@me" --state open

# PRs awaiting my review
gh pr list --repo owner/repo --review-requested "@me"
```

---

## Common Patterns

### Handle base64 encoded content

```bash
# macOS
gh api repos/owner/repo/contents/file.go | jq -r '.content' | base64 -d

# Linux
gh api repos/owner/repo/contents/file.go | jq -r '.content' | base64 -di
```

### Parse JSON output

```bash
# Get specific fields
gh issue view 123 --json title,body,author | jq -r '.title'

# Format output
gh search repos "react" --json fullName,stargazerCount | \
  jq -r '.[] | "\(.fullName): \(.stargazerCount) stars"'
```

### Batch operations

```bash
# Close all stale issues
gh issue list --repo owner/repo --label "stale" --json number | \
  jq -r '.[].number' | \
  xargs -I {} gh issue close {} --repo owner/repo

# Add label to multiple issues
gh issue list --repo owner/repo --state open --json number | \
  jq -r '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "triage" --repo owner/repo
```

---

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| `HTTP 401: Bad credentials` | Token invalid or expired | Ask user for new token |
| `HTTP 403: Resource not accessible` | No permission | Token needs more scopes |
| `HTTP 404: Not Found` | Repo/issue doesn't exist | Check owner/repo name |
| `Could not resolve to a Repository` | Wrong repo name | Verify format: owner/repo |
| `gh: command not found` | CLI not installed | `brew install gh` or equivalent |

---

## Helper Scripts

### github-helper.py - General operations

```bash
GH_SCRIPT="skills/github/scripts/github-helper.py"

# Check environment
python3 $GH_SCRIPT check-install

# View file
python3 $GH_SCRIPT view-file owner/repo path/to/file.go

# Create issue
python3 $GH_SCRIPT create-issue owner/repo \
  --title "Bug report" \
  --body "Description here..."

# List issues
python3 $GH_SCRIPT list-issues owner/repo --limit 10

# View PR
python3 $GH_SCRIPT view-pr owner/repo 456 --patch
```

### safe-create-pr.py - Create PRs safely

**Use this instead of `gh pr create` when body contains special characters.**

```bash
# From file (safest for complex descriptions)
echo 'Description with `code`, $vars, <html> tags' > /tmp/pr-body.md
python3 skills/github/scripts/safe-create-pr.py \
  --repo owner/repo \
  --title "feat: my changes" \
  --body-file /tmp/pr-body.md \
  --base main \
  --head feature-branch

# From stdin
cat description.md | python3 skills/github/scripts/safe-create-pr.py \
  --repo owner/repo \
  --title "feat: changes" \
  --body-stdin \
  --base main \
  --head feature-branch

# Simple inline (no special chars)
python3 skills/github/scripts/safe-create-pr.py \
  --repo owner/repo \
  --title "fix: typo" \
  --body "Fixed typo in README" \
  --base main \
  --head fix-typo
```

### pr-manager.py - Manage PRs

```bash
# View PR details (JSON)
python3 skills/github/scripts/pr-manager.py view \
  --repo owner/repo --number 123

# Close PR with comment
python3 skills/github/scripts/pr-manager.py close \
  --repo owner/repo --number 123 \
  --comment "Closing to make improvements"

# Reopen PR
python3 skills/github/scripts/pr-manager.py reopen \
  --repo owner/repo --number 123

# List PRs
python3 skills/github/scripts/pr-manager.py list \
  --repo owner/repo --state open --limit 20

# Check PR status and CI
python3 skills/github/scripts/pr-manager.py status \
  --repo owner/repo --number 123
python3 $GH_SCRIPT view-pr owner/repo 456 --patch
```

---

## User Input Requirements

Before performing **write operations**, you MUST ask the user:

1. **For authentication:**
   > "I need a GitHub Personal Access Token to create this issue. You can create one at https://github.com/settings/tokens with `repo` scope. Please provide your token:"

2. **For confirmation (destructive operations):**
   > "I will close issue #123. Is that OK?"

3. **For content:**
   > "What title should I use for this issue?"
   > "What should the issue description say?"

---

## Common Pitfalls

### 1. JSON Field Names

gh CLI 的 JSON 字段名可能和直觉不同：

```bash
# ❌ 错误
gh repo view owner/repo --json stargazersCount  # 报错

# ✅ 正确
gh repo view owner/repo --json stargazerCount   # 注意单数
```

**常见易错字段：**
- `stargazersCount` → `stargazerCount` (单数)
- `forksCount` → `forkCount` (单数)
- `defaultBranch` → `defaultBranchRef` (返回对象)

**参考**: `references/gh-json-fields.md`

### 2. Fork 限制

不能 fork 自己的仓库：
```bash
gh repo fork myuser/myrepo
# Error: A single user account cannot own both a parent and fork
```

**解决方案**：直接 clone 原仓库，创建分支推送。

### 3. Bash 转义问题

PR/Issue 描述包含特殊字符时：

```bash
# ❌ 危险：泛型语法 [T] 会被 bash 解释为通配符
gh pr create --body "Use LoadFunc[T] for generics"

# ✅ 安全：使用 Python 脚本
python3 skills/github/scripts/safe-create-pr.py \
  --repo owner/repo --title "PR Title" \
  --body-file description.md --head feature-branch
```

**Heredoc 注意事项：**

```bash
# ❌ 错误：<<> 是无效的
 cat > file <<> 'EOF'

# ❌ 错误：<< 'EOF' 后面的内容会被当作命令
 cat > file << 'EOF'
 Use `code` here
 EOF

# ✅ 正确：使用文件或 Python 脚本
 echo '内容' > file
 # 或
 python3 safe-create-pr.py --body-file file ...
```

### 4. 本地环境检查

提交代码前检查本地环境：
```bash
# 检查是否有需要的语言环境
which go
which python3
which node

# 如果可以，运行测试
cd /tmp/repo && go test ./...
```

### 5. 临时目录管理

Clone 仓库时：
```bash
# 使用 /tmp 避免污染工作目录
REPO_DIR=$(mktemp -d)
gh repo clone owner/repo "$REPO_DIR/repo"
cd "$REPO_DIR/repo"

# ... 工作 ...

# 完成后清理
cd /tmp
rm -rf "$REPO_DIR"
```

---

## External References

- GitHub CLI docs: https://cli.github.com/manual/
- Creating tokens: https://github.com/settings/tokens
- GitHub REST API: https://docs.github.com/en/rest
- Token scopes: https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps
- **JSON Fields Reference**: `references/gh-json-fields.md`
