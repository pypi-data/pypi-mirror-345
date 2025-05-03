# 🧭 GitHub Repo Migrator

`repo_migrator` is a cross-platform Python CLI tool that:

- 🔍 Finds all Git repositories on your local machine
- 🔁 Updates GitHub remotes with a new GitHub username
- 👤 Updates your global Git config (`user.name`, `user.email`)
- 🚫 Supports excluding specific repositories
- 📄 Lists all repositories in your home directory
- 🐳 Includes Docker support and GitHub Actions workflows

[![Docker Image Build](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/docker-build.yml/badge.svg)](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/docker-build.yml)
[![Docker Publish to GHCR](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/docker-publish.yml)
[![Pylint](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/pylint.yml/badge.svg)](https://github.com/Richard-Barrett/repo_migrator/actions/workflows/pylint.yml)

---

## 🚀 Features

- Compatible with **macOS**, **Linux**, and **Windows**
- Works with both **HTTPS** and **SSH** GitHub remotes
- Supports `--dry-run` mode for safe previews
- Cleanly structured and ready for CI/CD pipelines
- Includes pre-commit hooks, linting, formatting, and tests

---

## 📦 Installation

### Option 1: With pip (editable mode for local dev)

```bash
git clone https://github.com/Richard-Barrett/repo_migrator.git
cd repo_migrator
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Option 2: Install via Docker (prebuilt image)

```bash
docker run --rm -v $HOME:$HOME ghcr.io/richard-barrett/repo-migrator:latest --list-repositories
```

---

## 🧪 CLI Usage

### List all GitHub repositories in your home directory

```bash
repo-migrator --list-repositories
```

### Update global Git config + GitHub remotes

```bash
repo-migrator \
  --new-github-username your-username \
  --new-email you@example.com
```

### Simulate the changes (dry run)

```bash
repo-migrator \
  --new-github-username your-username \
  --new-email you@example.com \
  --dry-run
```

### Exclude specific repositories by name

```bash
repo-migrator \
  --new-github-username your-username \
  --new-email you@example.com \
  --exclude-repositories repo1,repo2
```

---

## 🧰 Developer Guide

### Run Tests

```bash
make test
```

### Format with Black

```bash
make format
```

### Run Pylint

```bash
make lint
```

### Install Pre-commit Hooks

```bash
make hooks
```

---

## 🐳 Docker Build & Publish

To build the Docker image locally:

```bash
docker build -t repo-migrator .
```

To push to GitHub Container Registry (GHCR):

```bash
docker tag repo-migrator ghcr.io/richard-barrett/repo-migrator:latest
docker push ghcr.io/richard-barrett/repo-migrator:latest
```

A GitHub Actions workflow will automatically build and publish the image on push to `main`.

---

## 🔧 GitHub Actions Workflows Included

- ✅ `python.yml` for testing, linting, and formatting
- ✅ `docker-publish.yml` to build & push Docker images to GHCR
- ✅ `tag-release.yml` to auto-bump versions with Git tags

---

## 🧼 Pre-commit Hooks

Install and run:

```bash
pre-commit install
pre-commit run --all-files
```

Hooks included:
- `black`
- `pylint`
- `check-yaml`
- `end-of-file-fixer`
- `trailing-whitespace`
- `pyupgrade`

---

## 📝 License

MIT © Richard Barrett
