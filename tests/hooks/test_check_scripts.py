"""scripts/check_secrets.py と scripts/check_unity_meta.py の判定。

一時ディレクトリに git リポジトリを作り、違反があれば 1、無ければ 0 を返すことを確かめる。
"""

from __future__ import annotations

from pathlib import Path

from conftest import git, run_script


def commit(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "add")


def test_secrets_clean_repo_passes(script_repo: Path) -> None:
    commit(
        script_repo, {"backend/.env.example": "GEMINI_API_KEY=\n", "README.md": "# x\n"}
    )
    assert run_script(script_repo, "check_secrets.py").returncode == 0


def test_secrets_forbidden_file_fails(script_repo: Path) -> None:
    commit(script_repo, {"Assets/Scripts/ApiKeys.cs": "class ApiKeys {}\n"})
    result = run_script(script_repo, "check_secrets.py")
    assert result.returncode == 1
    assert "ApiKeys.cs" in result.stderr


def test_secrets_key_in_content_fails(script_repo: Path) -> None:
    commit(script_repo, {"backend/config.py": "KEY = 'AIza" + "x" * 35 + "'\n"})
    result = run_script(script_repo, "check_secrets.py")
    assert result.returncode == 1
    assert "backend/config.py:1" in result.stderr


def test_meta_paired_assets_pass(script_repo: Path) -> None:
    commit(
        script_repo,
        {
            "Assets/Scripts.meta": "",
            "Assets/Scripts/A.cs": "",
            "Assets/Scripts/A.cs.meta": "",
        },
    )
    assert run_script(script_repo, "check_unity_meta.py").returncode == 0


def test_meta_missing_file_meta_fails(script_repo: Path) -> None:
    commit(script_repo, {"Assets/Scripts.meta": "", "Assets/Scripts/A.cs": ""})
    result = run_script(script_repo, "check_unity_meta.py")
    assert result.returncode == 1
    assert "Assets/Scripts/A.cs" in result.stderr


def test_meta_missing_directory_meta_fails(script_repo: Path) -> None:
    commit(script_repo, {"Assets/Scripts/A.cs": "", "Assets/Scripts/A.cs.meta": ""})
    result = run_script(script_repo, "check_unity_meta.py")
    assert result.returncode == 1
    assert "Assets/Scripts/" in result.stderr


def test_meta_orphan_meta_fails(script_repo: Path) -> None:
    commit(script_repo, {"Assets/Gone.cs.meta": ""})
    result = run_script(script_repo, "check_unity_meta.py")
    assert result.returncode == 1
    assert "対応するアセットが無い" in result.stderr
