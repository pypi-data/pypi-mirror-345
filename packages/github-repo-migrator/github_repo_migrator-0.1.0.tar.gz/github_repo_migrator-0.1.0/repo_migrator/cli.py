#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
import re
import argparse


def run_git_command(args, cwd=None):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            check=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {' '.join(e.cmd)}\n{e.stderr.strip()}")
        return None


def check_git_installed():
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        print("❌ Git is not installed or not in PATH.")
        exit(1)


def update_git_global_config(new_username, new_email, dry_run):
    print("🛠️ Checking global Git config...")

    name = run_git_command(["config", "--global", "user.name"])
    email = run_git_command(["config", "--global", "user.email"])

    if name != new_username:
        print(f"🔄 Updating user.name: {name} → {new_username}")
        if not dry_run:
            run_git_command(["config", "--global", "user.name", new_username])

    if email != new_email:
        print(f"🔄 Updating user.email: {email} → {new_email}")
        if not dry_run:
            run_git_command(["config", "--global", "user.email", new_email])


def find_git_repositories(base_path):
    print(f"🔍 Searching for Git repositories under {base_path}")
    git_repos = []
    for root, dirs, files in os.walk(base_path):
        if ".git" in dirs:
            git_repos.append(Path(root))
            dirs[:] = []  # Don't recurse further
    return git_repos


def list_repositories(repo_paths):
    print("\n📄 List of Git repositories:")
    for repo in repo_paths:
        print(f"- {repo.name}  →  {repo.resolve()}")


def update_github_remotes(repo_path, dry_run):
    print(f"\n📦 Processing repo: {repo_path}")
    remotes = run_git_command(["remote", "-v"], cwd=repo_path)
    if not remotes:
        return

    for line in remotes.splitlines():
        match = re.match(r"(\S+)\s+(\S+)\s+\((fetch|push)\)", line)
        if not match:
            continue
        remote_name, url, direction = match.groups()
        updated_url = transform_github_url(url)

        if updated_url and updated_url != url:
            print(
                f"🔁 Updating {remote_name} {direction} URL:\n   {url}\n → {updated_url}"
            )
            if not dry_run:
                run_git_command(
                    ["remote", "set-url", remote_name, updated_url], cwd=repo_path
                )


def transform_github_url(url):
    ssh_match = re.match(r"git@github\.com:(?P<org>[^/]+)/(?P<repo>.+?)(\.git)?$", url)
    if ssh_match:
        org, repo = ssh_match.group("org"), ssh_match.group("repo")
        return f"git@github.com:{org}/{repo}.git"

    https_match = re.match(
        r"https://github\.com/(?P<org>[^/]+)/(?P<repo>.+?)(\.git)?$", url
    )
    if https_match:
        org, repo = https_match.group("org"), https_match.group("repo")
        return f"https://github.com/{org}/{repo}.git"

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Migrate GitHub repositories, update remotes, and global Git config."
    )
    parser.add_argument(
        "--new-github-username",
        help="New GitHub username for remotes and global config",
    )
    parser.add_argument("--new-email", help="New GitHub email for global config")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate changes without applying them"
    )
    parser.add_argument(
        "--list-repositories",
        action="store_true",
        help="Only list all local GitHub repositories",
    )
    parser.add_argument(
        "--exclude-repositories",
        help="Comma-separated list of local folder names of repositories to exclude",
    )

    args = parser.parse_args()
    check_git_installed()
    base_dir = str(Path.home())

    excluded = set()
    if args.exclude_repositories:
        excluded = {name.strip() for name in args.exclude_repositories.split(",")}

    all_repos = [r for r in find_git_repositories(base_dir) if r.name not in excluded]

    if args.list_repositories:
        list_repositories(all_repos)
        return

    if not args.new_github_username or not args.new_email:
        parser.error(
            "The following arguments are required unless using --list-repositories: --new-github-username, --new-email"
        )

    update_git_global_config(args.new_github_username, args.new_email, args.dry_run)

    print(f"\n📁 Found {len(all_repos)} Git repositories.")
    for repo in all_repos:
        update_github_remotes(repo, args.dry_run)

    print("\n✅ Migration complete.")


if __name__ == "__main__":
    main()
