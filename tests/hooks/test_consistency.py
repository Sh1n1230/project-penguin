"""複数の場所に書かれた一覧が食い違っていないこと。

- git add を止めるファイル名: guard_git.py の _FORBIDDEN_ADD と check_secrets.py の FORBIDDEN_PATHS
- Unity YAML の拡張子: guard_write.py の UNITY_YAML、.gitattributes の merge=unityyaml、.editorconfig
"""

from __future__ import annotations

import re

import pytest
from conftest import HOOKS, ROOT, SCRIPTS, load_module

guard_git = load_module(HOOKS / "guard_git.py")
guard_write = load_module(HOOKS / "guard_write.py")
check_secrets = load_module(SCRIPTS / "check_secrets.py")

FILE_NAMES = [
    ".env",
    ".env.local",
    ".env.production",
    ".env.example",
    "penguin.db",
    "penguin.sqlite",
    "penguin.sqlite3",
    "penguin.db-journal",
    "penguin.sqlite-wal",
    "penguin.sqlite3-shm",
    "dev.pem",
    "dev.key",
    "dev.p12",
    "dev.pfx",
    "release.keystore",
    "release.jks",
    "App.mobileprovision",
    "secrets.json",
    "ApiKeys.cs",
    "GameSession.cs",
    "README.md",
    "envelope.json",
]


@pytest.mark.parametrize("name", FILE_NAMES)
def test_forbidden_add_matches_check_secrets(name: str) -> None:
    by_hook = guard_git._FORBIDDEN_ADD.search(name) is not None
    by_ci = check_secrets.FORBIDDEN_PATHS.search(name) is not None
    assert by_hook == by_ci, f"{name}: guard_git={by_hook}, check_secrets={by_ci}"


def gitattributes_unity_yaml() -> set[str]:
    text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    return {
        m.group(1).lower()
        for m in re.finditer(r"^\*(\.\S+)\s+.*\bmerge=unityyaml\b", text, re.MULTILINE)
    }


def editorconfig_unity_yaml() -> set[str]:
    text = (ROOT / ".editorconfig").read_text(encoding="utf-8")
    match = re.search(
        r"# Unity が生成する YAML.*?\n(?:#.*\n)*\[\*\.\{([^}]*)\}\]", text
    )
    assert match is not None, ".editorconfig に Unity YAML の節が見つかりません"
    return {"." + ext.strip().lower() for ext in match.group(1).split(",")}


def test_unity_yaml_lists_agree() -> None:
    hook = set(guard_write.UNITY_YAML)
    assert gitattributes_unity_yaml() == hook
    assert editorconfig_unity_yaml() == hook
