#!/usr/bin/env python3
"""
安全创建 PR - 避免 bash 转义问题

Usage:
    # From file (recommended for multi-line descriptions)
    python3 safe-create-pr.py --repo owner/repo \
        --title "Title" \
        --body-file description.md \
        --base main \
        --head feature-branch

    # From stdin (useful for piping)
    cat description.md | python3 safe-create-pr.py --repo owner/repo \
        --title "Title" --body-stdin --base main --head feature-branch

    # Inline (only for simple text without special chars)
    python3 safe-create-pr.py --repo owner/repo \
        --title "Title" --body "Simple description" \
        --base main --head feature-branch

Note: Use --body-file or --body-stdin for descriptions containing:
    - Backticks (`)
    - Dollar signs ($)
    - Angle brackets (< >)
    - Quotes (" ')
    - Newlines
"""

import argparse
import subprocess
import sys
from pathlib import Path


def create_pr(repo: str, title: str, body: str, base: str, head: str, draft: bool = False) -> int:
    """Create PR using gh CLI"""
    cmd = [
        "gh", "pr", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
        "--base", base,
        "--head", head
    ]

    if draft:
        cmd.append("--draft")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating PR: {e.stderr}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Safe PR creation (avoids bash escaping issues)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read from file (safest for complex descriptions)
  python3 safe-create-pr.py --repo owner/repo --title "Fix bug" \\
      --body-file pr-description.md --head feature-branch

  # Read from stdin
  echo "Description" | python3 safe-create-pr.py --repo owner/repo \\
      --title "Fix bug" --body-stdin --head feature-branch

  # Simple inline body (no special characters)
  python3 safe-create-pr.py --repo owner/repo --title "Fix bug" \\
      --body "Fixed the issue" --head feature-branch
        """
    )
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--title", required=True, help="PR title")

    body_group = parser.add_mutually_exclusive_group(required=True)
    body_group.add_argument("--body", help="PR body (inline - avoid special chars)")
    body_group.add_argument("--body-file", help="PR body from file")
    body_group.add_argument("--body-stdin", action="store_true", help="PR body from stdin")

    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--head", required=True, help="Head branch (e.g., feature-branch or owner:feature-branch)")
    parser.add_argument("--draft", action="store_true", help="Create as draft PR")

    args = parser.parse_args()

    # Get body content
    body = ""
    if args.body_stdin:
        try:
            body = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nCancelled.", file=sys.stderr)
            return 130
        if not body.strip():
            print("Error: No input provided via stdin", file=sys.stderr)
            return 1
    elif args.body_file:
        path = Path(args.body_file)
        if not path.exists():
            print(f"Error: Body file not found: {args.body_file}", file=sys.stderr)
            return 1
        try:
            body = path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            print(f"Error: Failed to read file (encoding issue): {e}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"Error: Failed to read file: {e}", file=sys.stderr)
            return 1
    else:
        body = args.body

    if not body.strip():
        print("Error: PR body cannot be empty", file=sys.stderr)
        return 1

    return create_pr(args.repo, args.title, body, args.base, args.head, args.draft)


if __name__ == "__main__":
    sys.exit(main())
