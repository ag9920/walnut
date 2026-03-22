#!/usr/bin/env python3
"""
PR Manager - Manage pull requests safely

Usage:
    # View PR details (JSON format)
    python3 pr-manager.py view --repo owner/repo --number 123

    # Close PR
    python3 pr-manager.py close --repo owner/repo --number 123 \
        --comment "Closing to make improvements"

    # List PRs
    python3 pr-manager.py list --repo owner/repo --state open

    # Check PR status
    python3 pr-manager.py status --repo owner/repo --number 123
"""

import argparse
import json
import subprocess
import sys
from typing import Any, Optional


def run_gh(args: list[str]) -> tuple[str, int]:
    """Run gh CLI command and return (output, exit_code)"""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout + result.stderr, result.returncode
    except FileNotFoundError:
        return "Error: gh CLI not found", 127


def view_pr(repo: str, number: int, json_format: bool = True) -> int:
    """View PR details"""
    if json_format:
        output, code = run_gh([
            "pr", "view", str(number),
            "--repo", repo,
            "--json", "number,title,state,author,createdAt,updatedAt,url,additions,deletions,headRefName,baseRefName,body"
        ])
        if code == 0:
            try:
                data = json.loads(output)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(output)
        else:
            print(output, file=sys.stderr)
    else:
        output, code = run_gh(["pr", "view", str(number), "--repo", repo])
        print(output)
    return code


def close_pr(repo: str, number: int, comment: Optional[str] = None) -> int:
    """Close a PR with optional comment"""
    # Add comment first if provided
    if comment:
        output, code = run_gh([
            "pr", "comment", str(number),
            "--repo", repo,
            "--body", comment
        ])
        if code != 0:
            print(f"Failed to add comment: {output}", file=sys.stderr)
            return code
        print(f"Added comment to PR #{number}")

    # Close the PR
    output, code = run_gh(["pr", "close", str(number), "--repo", repo])
    if code == 0:
        print(f"Closed PR #{number}")
        print(output)
    else:
        print(f"Failed to close PR: {output}", file=sys.stderr)
    return code


def list_prs(repo: str, state: str = "open", limit: int = 30) -> int:
    """List PRs"""
    output, code = run_gh([
        "pr", "list",
        "--repo", repo,
        "--state", state,
        "--limit", str(limit),
        "--json", "number,title,author,state,createdAt,headRefName"
    ])
    if code == 0:
        try:
            prs = json.loads(output)
            if not prs:
                print(f"No {state} PRs found")
                return 0
            for pr in prs:
                print(f"#{pr['number']}: {pr['title']}")
                print(f"   Author: {pr['author']['login']} | State: {pr['state']} | Branch: {pr['headRefName']}")
                print()
        except json.JSONDecodeError:
            print(output)
    else:
        print(output, file=sys.stderr)
    return code


def check_status(repo: str, number: int) -> int:
    """Check PR status including checks"""
    # Get PR info
    output, code = run_gh([
        "pr", "view", str(number),
        "--repo", repo,
        "--json", "number,title,state,mergeStateStatus"
    ])
    if code != 0:
        print(output, file=sys.stderr)
        return code

    try:
        pr = json.loads(output)
        print(f"PR #{pr['number']}: {pr['title']}")
        print(f"State: {pr['state']}")
        print(f"Merge Status: {pr.get('mergeStateStatus', 'unknown')}")
    except json.JSONDecodeError:
        print(output)

    # Check CI status
    print("\nChecks:")
    output, code = run_gh(["pr", "checks", str(number), "--repo", repo])
    if code == 0:
        print(output)
    else:
        print("No checks or failed to fetch checks")

    return 0


def reopen_pr(repo: str, number: int) -> int:
    """Reopen a closed PR"""
    output, code = run_gh(["pr", "reopen", str(number), "--repo", repo])
    if code == 0:
        print(f"Reopened PR #{number}")
        print(output)
    else:
        print(f"Failed to reopen PR: {output}", file=sys.stderr)
    return code


def main():
    parser = argparse.ArgumentParser(
        description="PR Manager - Manage pull requests",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # view command
    view_parser = subparsers.add_parser("view", help="View PR details")
    view_parser.add_argument("--number", "-n", type=int, required=True, help="PR number")
    view_parser.add_argument("--raw", action="store_true", help="Show raw output instead of JSON")

    # close command
    close_parser = subparsers.add_parser("close", help="Close a PR")
    close_parser.add_argument("--number", "-n", type=int, required=True, help="PR number")
    close_parser.add_argument("--comment", "-c", help="Comment to add before closing")

    # reopen command
    reopen_parser = subparsers.add_parser("reopen", help="Reopen a closed PR")
    reopen_parser.add_argument("--number", "-n", type=int, required=True, help="PR number")

    # list command
    list_parser = subparsers.add_parser("list", help="List PRs")
    list_parser.add_argument("--state", choices=["open", "closed", "merged", "all"], default="open")
    list_parser.add_argument("--limit", "-l", type=int, default=30)

    # status command
    status_parser = subparsers.add_parser("status", help="Check PR status and CI checks")
    status_parser.add_argument("--number", "-n", type=int, required=True, help="PR number")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "view": lambda: view_pr(args.repo, args.number, not args.raw),
        "close": lambda: close_pr(args.repo, args.number, args.comment),
        "reopen": lambda: reopen_pr(args.repo, args.number),
        "list": lambda: list_prs(args.repo, args.state, args.limit),
        "status": lambda: check_status(args.repo, args.number),
    }

    if args.command in commands:
        return commands[args.command]()
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
