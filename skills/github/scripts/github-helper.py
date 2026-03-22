#!/usr/bin/env python3
"""
GitHub Helper Script - Remote GitHub operations via gh CLI

All operations are REMOTE - no local file system operations.
Requires: gh CLI installed and authenticated

Usage:
    python3 github-helper.py check-install
    python3 github-helper.py view-file owner/repo path/to/file
    python3 github-helper.py create-issue owner/repo --title "..." --body "..."

Environment:
    GH_TOKEN    - GitHub Personal Access Token
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from typing import List, Optional, Tuple


def run_gh(args: List[str], capture_output: bool = True, check: bool = True) -> Tuple[str, int]:
    """Execute gh CLI command and return (output, exit_code)"""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result.stdout, 0
    except subprocess.CalledProcessError as e:
        if capture_output:
            return e.stderr, e.returncode
        return "", e.returncode
    except FileNotFoundError:
        return "Error: 'gh' CLI not found.", 127


def check_gh_installed() -> bool:
    """Check if gh CLI is installed"""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def print_install_instructions():
    """Print installation instructions"""
    print("❌ GitHub CLI (gh) is not installed.")
    print()
    print("Please install it:")
    print()

    import platform
    system = platform.system()

    if system == "Darwin":
        print("  macOS (Homebrew):")
        print("    brew install gh")
    elif system == "Linux":
        print("  Ubuntu/Debian:")
        print("    sudo apt install gh")
        print()
        print("  Or for the latest version:")
        print("    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg")
        print("    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg")
        print('    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null')
        print("    sudo apt update")
        print("    sudo apt install gh")
    else:
        print("  See: https://github.com/cli/cli#installation")

    print()
    print("After installation, authenticate with:")
    print("  gh auth login")
    print("  # Or set GH_TOKEN environment variable")
    print()


def check_auth() -> Tuple[bool, str]:
    """Check if authenticated, return (is_auth, username_or_error)"""
    output, code = run_gh(["auth", "status"], check=False)
    if code != 0:
        return False, "Not authenticated"

    # Parse username from output
    for line in output.split('\n'):
        if 'Logged in to github.com as' in line:
            parts = line.split()
            if len(parts) >= 6:
                return True, parts[5]
    return True, "unknown"


def validate_repo_spec(repo_spec: str) -> bool:
    """Validate owner/repo format"""
    parts = repo_spec.split("/")
    return len(parts) == 2 and all(parts)


# ==============================================================================
# Read Operations
# ==============================================================================

def view_file(owner_repo: str, path: str, ref: Optional[str] = None):
    """View content of a file in a repository"""
    args = ["api", f"repos/{owner_repo}/contents/{path}"]
    if ref:
        args.extend(["--ref", ref])
    args.extend(["--jq", ".content"])

    content, code = run_gh(args, check=False)
    if code != 0:
        print(content, file=sys.stderr)
        return 1

    content = content.strip().strip('"')
    if content:
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            print(decoded)
        except Exception as e:
            print(f"Error decoding content: {e}", file=sys.stderr)
            return 1
    else:
        print("File not found or empty", file=sys.stderr)
        return 1
    return 0


def list_files(owner_repo: str, path: str = ""):
    """List files in a directory"""
    api_path = f"repos/{owner_repo}/contents"
    if path:
        api_path += f"/{path}"

    output, code = run_gh(["api", api_path], check=False)
    if code != 0:
        print(output, file=sys.stderr)
        return 1

    try:
        items = json.loads(output)
        for item in items:
            item_type = "📁" if item["type"] == "dir" else "📄"
            print(f"{item_type} {item['name']}")
    except json.JSONDecodeError:
        print("Failed to parse response", file=sys.stderr)
        return 1
    return 0


def list_issues(owner_repo: str, state: str = "open", limit: int = 30):
    """List issues in a repository"""
    output, code = run_gh([
        "issue", "list",
        "--repo", owner_repo,
        "--state", state,
        "--limit", str(limit),
        "--json", "number,title,author,createdAt,labels,state"
    ], check=False)

    if code != 0:
        print(output, file=sys.stderr)
        return 1

    try:
        issues = json.loads(output)
    except json.JSONDecodeError:
        print("Failed to parse issues", file=sys.stderr)
        return 1

    if not issues:
        print(f"No {state} issues found in {owner_repo}")
        return 0

    for issue in issues:
        labels = ", ".join([l["name"] for l in issue.get("labels", [])])
        state_emoji = "🟢" if issue.get("state") == "OPEN" else "🔴"
        print(f"{state_emoji} #{issue['number']}: {issue['title']}")
        print(f"   Author: {issue['author']['login']} | Created: {issue['createdAt'][:10]}")
        if labels:
            print(f"   Labels: {labels}")
        print()
    return 0


def view_issue(owner_repo: str, number: int, with_comments: bool = False):
    """View issue details"""
    args = ["issue", "view", str(number), "--repo", owner_repo]
    if with_comments:
        args.append("--comments")

    output, code = run_gh(args, check=False)
    if code != 0:
        print(output, file=sys.stderr)
        return 1
    print(output)
    return 0


def view_pr(owner_repo: str, number: int, patch: bool = False):
    """View PR details"""
    args = ["pr", "view", str(number), "--repo", owner_repo]
    if patch:
        args.append("--patch")

    output, code = run_gh(args, check=False)
    if code != 0:
        print(output, file=sys.stderr)
        return 1
    print(output)
    return 0


def list_pr_files(owner_repo: str, number: int):
    """List files changed in a PR"""
    output, code = run_gh([
        "pr", "view", str(number),
        "--repo", owner_repo,
        "--json", "files"
    ], check=False)

    if code != 0:
        print(output, file=sys.stderr)
        return 1

    try:
        data = json.loads(output)
        files = data.get("files", [])
    except json.JSONDecodeError:
        print("Failed to parse PR files", file=sys.stderr)
        return 1

    if not files:
        print("No files changed in this PR")
        return 0

    print(f"Files changed in PR #{number}:")
    for f in files:
        status = f.get("changeType", "M")
        emoji = {"ADDED": "+", "DELETED": "-", "MODIFIED": "~"}.get(status, "~")
        print(f"  {emoji} {f['path']} (+{f['additions']}/-{f['deletions']})")
    return 0


def repo_info(owner_repo: str):
    """View repository information"""
    output, code = run_gh([
        "repo", "view", owner_repo,
        "--json", "name,description,stargazerCount,forkCount,primaryLanguage,pushedAt"
    ], check=False)

    if code != 0:
        print(output, file=sys.stderr)
        return 1

    try:
        info = json.loads(output)
        print(f"📦 {info['name']}")
        if info.get("description"):
            print(f"   {info['description']}")
        print(f"   ⭐ {info['stargazerCount']} stars | 🍴 {info['forkCount']} forks")
        print(f"   Language: {info.get('primaryLanguage', {}).get('name', 'N/A')}")
        print(f"   Last push: {info.get('pushedAt', 'N/A')[:10] if info.get('pushedAt') else 'N/A'}")
    except json.JSONDecodeError:
        print(output)
    return 0


def search_repos(query: str, language: Optional[str] = None, sort: str = "stars", limit: int = 10):
    """Search for repositories"""
    args = [
        "search", "repos", query,
        "--sort", sort,
        "--limit", str(limit),
        "--json", "fullName,description,stargazerCount,language,updatedAt"
    ]
    if language:
        args.extend(["--language", language])

    output, code = run_gh(args, check=False)
    if code != 0:
        print(output, file=sys.stderr)
        return 1

    try:
        repos = json.loads(output)
    except json.JSONDecodeError:
        print("Failed to parse search results", file=sys.stderr)
        return 1

    if not repos:
        print("No repositories found")
        return 0

    print(f"Found {len(repos)} repositories:")
    print()
    for repo in repos:
        print(f"📦 {repo['fullName']}  ⭐ {repo['stargazerCount']}")
        if repo.get("description"):
            desc = repo['description'][:80] + "..." if len(repo['description']) > 80 else repo['description']
            print(f"   {desc}")
        print()
    return 0


# ==============================================================================
# Write Operations (Require Auth)
# ==============================================================================

def create_issue(owner_repo: str, title: str, body: str, label: Optional[str] = None, dry_run: bool = False):
    """Create a new issue"""
    # Check auth first
    is_auth, username = check_auth()
    if not is_auth:
        print("❌ Not authenticated with GitHub.", file=sys.stderr)
        print("   Run: gh auth login", file=sys.stderr)
        print("   Or set GH_TOKEN environment variable", file=sys.stderr)
        return 1

    if dry_run:
        print("🔍 DRY RUN - Would create issue with:")
        print(f"   Repo: {owner_repo}")
        print(f"   Title: {title}")
        print(f"   Body: {body[:100]}..." if len(body) > 100 else f"   Body: {body}")
        if label:
            print(f"   Label: {label}")
        return 0

    cmd = ["issue", "create", "--repo", owner_repo, "--title", title, "--body", body]
    if label:
        cmd.extend(["--label", label])

    output, code = run_gh(cmd, check=False)
    if code == 0:
        print(f"✅ Issue created: {output.strip()}")
    else:
        print(f"❌ Failed to create issue: {output}", file=sys.stderr)
        return 1
    return 0


def comment_issue(owner_repo: str, number: int, comment: str, dry_run: bool = False):
    """Add comment to an issue"""
    is_auth, _ = check_auth()
    if not is_auth:
        print("❌ Not authenticated with GitHub.", file=sys.stderr)
        return 1

    if dry_run:
        print(f"🔍 DRY RUN - Would comment on issue #{number}:")
        print(f"   {comment[:100]}..." if len(comment) > 100 else f"   {comment}")
        return 0

    _, code = run_gh([
        "issue", "comment", str(number),
        "--repo", owner_repo,
        "--body", comment
    ], check=False)

    if code == 0:
        print(f"✅ Comment added to issue #{number}")
    else:
        print(f"❌ Failed to add comment", file=sys.stderr)
        return 1
    return 0


def close_issue(owner_repo: str, number: int, comment: Optional[str] = None, dry_run: bool = False):
    """Close an issue"""
    is_auth, _ = check_auth()
    if not is_auth:
        print("❌ Not authenticated with GitHub.", file=sys.stderr)
        return 1

    if dry_run:
        print(f"🔍 DRY RUN - Would close issue #{number}")
        if comment:
            print(f"   With comment: {comment}")
        return 0

    # Optionally add comment first
    if comment:
        comment_issue(owner_repo, number, comment, dry_run=False)

    _, code = run_gh(["issue", "close", str(number), "--repo", owner_repo], check=False)
    if code == 0:
        print(f"✅ Issue #{number} closed")
    else:
        print(f"❌ Failed to close issue", file=sys.stderr)
        return 1
    return 0


def review_pr(owner_repo: str, number: int, action: str, body: str = "", dry_run: bool = False):
    """Review a PR"""
    is_auth, _ = check_auth()
    if not is_auth:
        print("❌ Not authenticated with GitHub.", file=sys.stderr)
        return 1

    actions = {
        "approve": "--approve",
        "request-changes": "--request-changes",
        "comment": "--comment"
    }

    if action not in actions:
        print(f"Invalid action: {action}. Use: approve, request-changes, comment", file=sys.stderr)
        return 1

    if dry_run:
        print(f"🔍 DRY RUN - Would {action} PR #{number}")
        if body:
            print(f"   Comment: {body[:100]}...")
        return 0

    cmd = ["pr", "review", str(number), "--repo", owner_repo, actions[action]]
    if body:
        cmd.extend(["--body", body])

    _, code = run_gh(cmd, check=False)
    if code == 0:
        print(f"✅ Review submitted on PR #{number}")
    else:
        print(f"❌ Failed to submit review", file=sys.stderr)
        return 1
    return 0


# ==============================================================================
# Utility Commands
# ==============================================================================

def check_install():
    """Check installation status and provide guidance"""
    print("GitHub Skill Environment Check")
    print("=" * 40)
    print()

    if check_gh_installed():
        output, _ = run_gh(["--version"])
        print(f"✅ gh CLI: {output.strip()}")

        is_auth, username = check_auth()
        if is_auth:
            print(f"✅ Authentication: Logged in as {username}")
        else:
            print("❌ Authentication: Not logged in")
            print("   Run: gh auth login")
            print("   Or: export GH_TOKEN='your_token'")
    else:
        print_install_instructions()
        return 1

    return 0


def interactive_setup():
    """Interactive setup guide"""
    print("🚀 GitHub Skill Setup")
    print()

    if not check_gh_installed():
        print("Step 1: Install gh CLI")
        print("-" * 30)
        print_install_instructions()
        return 1

    print("✅ gh CLI is installed")
    print()

    is_auth, username = check_auth()
    if not is_auth:
        print("Step 2: Authenticate")
        print("-" * 30)
        print()
        print("Option A - Browser login (recommended for personal use):")
        print("  gh auth login")
        print()
        print("Option B - Token (recommended for automation):")
        print("  1. Create token at: https://github.com/settings/tokens")
        print("  2. Set environment variable:")
        print("     export GH_TOKEN='your_token_here'")
        print()
        return 1

    print(f"✅ Authenticated as {username}")
    print()
    print("You're all set! Example commands:")
    print('  github-helper.py repo-info owner/repo')
    print('  github-helper.py list-issues owner/repo')
    print('  github-helper.py create-issue owner/repo --title "Bug" --body "Description"')
    return 0


# ==============================================================================
# Main
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GitHub Helper - Remote GitHub operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup and check commands
    subparsers.add_parser("check-install", help="Check gh CLI installation")
    subparsers.add_parser("setup", help="Interactive setup guide")

    # Read commands
    view_file_parser = subparsers.add_parser("view-file", help="View file content")
    view_file_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    view_file_parser.add_argument("path", help="File path within repository")
    view_file_parser.add_argument("--ref", help="Git ref (branch/tag/commit)")

    list_files_parser = subparsers.add_parser("list-files", help="List directory contents")
    list_files_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    list_files_parser.add_argument("--path", default="", help="Directory path")

    repo_info_parser = subparsers.add_parser("repo-info", help="View repository information")
    repo_info_parser.add_argument("owner_repo", help="Repository in format owner/repo")

    list_issues_parser = subparsers.add_parser("list-issues", help="List repository issues")
    list_issues_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    list_issues_parser.add_argument("--state", choices=["open", "closed", "all"], default="open")
    list_issues_parser.add_argument("--limit", type=int, default=30)

    view_issue_parser = subparsers.add_parser("view-issue", help="View issue details")
    view_issue_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    view_issue_parser.add_argument("number", type=int, help="Issue number")
    view_issue_parser.add_argument("--with-comments", action="store_true", help="Include comments")

    view_pr_parser = subparsers.add_parser("view-pr", help="View PR details")
    view_pr_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    view_pr_parser.add_argument("number", type=int, help="PR number")
    view_pr_parser.add_argument("--patch", action="store_true", help="Show diff patch")

    list_pr_files_parser = subparsers.add_parser("list-pr-files", help="List PR changed files")
    list_pr_files_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    list_pr_files_parser.add_argument("number", type=int, help="PR number")

    search_parser = subparsers.add_parser("search-repos", help="Search repositories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--language", help="Filter by programming language")
    search_parser.add_argument("--sort", choices=["stars", "forks", "updated"], default="stars")
    search_parser.add_argument("--limit", type=int, default=10)

    # Write commands
    create_issue_parser = subparsers.add_parser("create-issue", help="Create a new issue")
    create_issue_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    create_issue_parser.add_argument("--title", required=True, help="Issue title")
    create_issue_parser.add_argument("--body", required=True, help="Issue body")
    create_issue_parser.add_argument("--label", help="Label to apply")

    comment_parser = subparsers.add_parser("comment-issue", help="Comment on an issue")
    comment_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    comment_parser.add_argument("number", type=int, help="Issue number")
    comment_parser.add_argument("comment", help="Comment text")

    close_parser = subparsers.add_parser("close-issue", help="Close an issue")
    close_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    close_parser.add_argument("number", type=int, help="Issue number")
    close_parser.add_argument("--comment", help="Comment to add before closing")

    review_parser = subparsers.add_parser("review-pr", help="Review a PR")
    review_parser.add_argument("owner_repo", help="Repository in format owner/repo")
    review_parser.add_argument("number", type=int, help="PR number")
    review_parser.add_argument("--action", choices=["approve", "request-changes", "comment"], required=True)
    review_parser.add_argument("--body", default="", help="Review comment")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dry_run = args.dry_run

    # Route commands
    commands = {
        "check-install": lambda: check_install(),
        "setup": lambda: interactive_setup(),
        "view-file": lambda: view_file(args.owner_repo, args.path, args.ref),
        "list-files": lambda: list_files(args.owner_repo, args.path),
        "repo-info": lambda: repo_info(args.owner_repo),
        "list-issues": lambda: list_issues(args.owner_repo, args.state, args.limit),
        "view-issue": lambda: view_issue(args.owner_repo, args.number, args.with_comments),
        "view-pr": lambda: view_pr(args.owner_repo, args.number, args.patch),
        "list-pr-files": lambda: list_pr_files(args.owner_repo, args.number),
        "search-repos": lambda: search_repos(args.query, args.language, args.sort, args.limit),
        "create-issue": lambda: create_issue(args.owner_repo, args.title, args.body, args.label, dry_run),
        "comment-issue": lambda: comment_issue(args.owner_repo, args.number, args.comment, dry_run),
        "close-issue": lambda: close_issue(args.owner_repo, args.number, args.comment, dry_run),
        "review-pr": lambda: review_pr(args.owner_repo, args.number, args.action, args.body, dry_run),
    }

    if args.command in commands:
        sys.exit(commands[args.command]())
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
