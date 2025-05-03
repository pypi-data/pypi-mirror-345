from pathlib import Path
from repo_migrator.cli import transform_github_url


def test_transform_https_url():
    url = "https://github.com/example/repo.git"
    assert transform_github_url(url) == "https://github.com/example/repo.git"


def test_transform_ssh_url():
    url = "git@github.com:example/repo.git"
    assert transform_github_url(url) == "git@github.com:example/repo.git"


def test_invalid_url():
    url = "git@gitlab.com:example/repo.git"
    assert transform_github_url(url) is None
