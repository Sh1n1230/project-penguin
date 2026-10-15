"""フック (.claude/hooks) と検査スクリプト (scripts) のテストの共通部品。

どちらも標準ライブラリだけで書かれているので、backend の依存とは混ぜずに
`uv run --no-project --with pytest pytest tests/hooks` で回す。
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"
SCRIPTS = ROOT / "scripts"


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_hook(hook: str, payload: dict) -> str | None:
    """フックに PreToolUse の入力を渡し、deny の理由 (通すなら None) を返す。"""
    out = subprocess.run(
        [sys.executable, str(HOOKS / hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
    )
    if not out.stdout.strip():
        return None
    decision = json.loads(out.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    return decision["permissionDecisionReason"]


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """空のコミットが 1 つある git リポジトリ (ブランチは main)。"""
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "init")
    return tmp_path


@pytest.fixture
def script_repo(repo: Path) -> Path:
    """検査スクリプトとフックを複製したリポジトリ。スクリプトは自分の位置からルートを求めるため。"""
    shutil.copytree(
        SCRIPTS, repo / "scripts", ignore=shutil.ignore_patterns("__pycache__")
    )
    shutil.copytree(
        HOOKS, repo / ".claude" / "hooks", ignore=shutil.ignore_patterns("__pycache__")
    )
    return repo


def run_script(repo: Path, name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / name)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,  # 終了コードそのものを検査するため
    )
