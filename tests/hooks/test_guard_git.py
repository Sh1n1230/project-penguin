"""guard_git.py: 取り返しのつかない git 操作だけを止めること。

push の表は #29 の確認表をそのまま写した。
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import git, run_hook

MAIN = "main への直接 push"
FORCE = "force push"
PASS = None


def decide(repo: Path, command: str) -> str | None:
    return run_hook(
        "guard_git.py", {"cwd": str(repo), "tool_input": {"command": command}}
    )


def expect(reason: str | None, kind: str | None) -> None:
    if kind is None:
        assert reason is None
    else:
        assert reason is not None and kind in reason


@pytest.mark.parametrize(
    ("command", "kind"),
    [
        ("git push origin HEAD", MAIN),
        ("git push -u origin HEAD", MAIN),
        ("git push origin HEAD:refs/heads/main", MAIN),
        ("git push origin +HEAD", FORCE),
        ("git push origin main", MAIN),
        ("git push", MAIN),
        ("git push origin", MAIN),
        ("git push --force", FORCE),
        ("git push origin :main", MAIN),
        ("git push --delete origin main", MAIN),
        ("git push origin feat/x", PASS),
        ("git push -u origin feat/x", PASS),
    ],
)
def test_push_on_main(repo: Path, command: str, kind: str | None) -> None:
    expect(decide(repo, command), kind)


@pytest.mark.parametrize(
    ("command", "kind"),
    [
        ("git push origin feat/x:refs/heads/main", MAIN),
        ("git push -uf origin feat/x", FORCE),
        ("git push origin +feat/x", FORCE),
        ("git push --all origin", MAIN),
        ("git push --mirror", FORCE),
        ("git push origin :", MAIN),
        ("git push -u origin HEAD", PASS),
        ("git push", PASS),
        ("git push -o ci.skip origin feat/x", PASS),
        ("git push -n origin feat/x", PASS),
        ("git push origin --tags", PASS),
        ("git push --force-with-lease origin feat/x", FORCE),
        ("git push origin feat/x:main", MAIN),
        ("git status && git push origin HEAD:main", MAIN),
    ],
)
def test_push_on_work_branch(repo: Path, command: str, kind: str | None) -> None:
    git(repo, "switch", "-q", "-c", "feat/x")
    expect(decide(repo, command), kind)


@pytest.mark.parametrize(
    "command",
    ["git filter-branch --tree-filter true HEAD", "git filter-repo --path x"],
)
def test_history_rewrite_is_denied(repo: Path, command: str) -> None:
    expect(decide(repo, command), "履歴の一括改変")


@pytest.mark.parametrize(
    ("command", "denied"),
    [
        ("git commit --no-verify -m x", True),
        ("git commit -n -m x", True),
        ("git commit -m 'no-verify は使わない'", False),
    ],
)
def test_commit_no_verify(repo: Path, command: str, denied: bool) -> None:
    assert (decide(repo, command) is not None) == denied


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        "backend/.env.local",
        "penguin.db",
        "Library/state.sqlite3-wal",
        "keys/dev.p12",
        "ios/App.mobileprovision",
        "android/release.keystore",
        "secrets.json",
        "Assets/Scripts/ApiKeys.cs",
    ],
)
def test_add_of_secret_files_is_denied(repo: Path, path: str) -> None:
    expect(decide(repo, f"git add {path}"), "秘密情報またはローカル DB")


@pytest.mark.parametrize(
    "command",
    [
        "git add .env.example",
        "git add Assets/Scripts/Domain/Game/GameSession.cs",
        "git add -A",
        "git status",
        "git log --oneline",
        "git switch -c feat/y",
        "ls .env",
    ],
)
def test_ordinary_commands_pass(repo: Path, command: str) -> None:
    assert decide(repo, command) is None
