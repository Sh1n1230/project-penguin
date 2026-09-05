"""Unity Editor バージョンの一致を検証する。

Unity Hub が別バージョンでプロジェクトを開くと ProjectVersion.txt が
書き換わり、アセットが一斉にアップグレードされて巨大な差分が出る。
バージョンを書いている全ての箇所が食い違っていないかを機械的に確認する。

    python scripts/check_unity_version.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_VERSION = ROOT / "ProjectSettings" / "ProjectVersion.txt"

# (表示名, ファイル, バージョンを取り出す正規表現)
REFERENCES: list[tuple[str, Path, re.Pattern[str]]] = [
    (
        "Unity テストのワークフロー",
        ROOT / ".github" / "workflows" / "unity-tests.yml",
        re.compile(r"^\s*unityVersion:\s*(\S+)\s*$", re.MULTILINE),
    ),
    (
        "README のセットアップ表",
        ROOT / "README.md",
        re.compile(r"^\|\s*Unity\s*\|\s*(\S+)\s*\|", re.MULTILINE),
    ),
    (
        "CLAUDE.md の技術スタック",
        ROOT / "CLAUDE.md",
        re.compile(r"Unity\s+(\d+\.\d+\.\d+[a-z]\d+)"),
    ),
]


def project_version() -> str:
    if not PROJECT_VERSION.exists():
        raise SystemExit(f"{PROJECT_VERSION} がありません。")
    match = re.search(
        r"^m_EditorVersion:\s*(\S+)\s*$",
        PROJECT_VERSION.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise SystemExit("ProjectVersion.txt から m_EditorVersion を読めません。")
    return match.group(1)


def main() -> int:
    expected = project_version()
    print(f"ProjectVersion.txt: {expected}")

    errors: list[str] = []
    for label, path, pattern in REFERENCES:
        if not path.exists():
            continue
        match = pattern.search(path.read_text(encoding="utf-8"))
        if match is None:
            errors.append(f"  {label} ({path.relative_to(ROOT)}) にバージョンの記述が見つかりません")
            continue
        found = match.group(1)
        status = "OK " if found == expected else "NG "
        print(f"  {status}{label}: {found}")
        if found != expected:
            errors.append(
                f"  {label} ({path.relative_to(ROOT)}) が {found} で、"
                f"ProjectVersion.txt の {expected} と一致しません"
            )

    if errors:
        print("\nUnity バージョンの記述が食い違っています:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        print(
            "\nProjectVersion.txt が意図せず書き換わっている場合、"
            "別バージョンの Editor でプロジェクトを開いた可能性があります。"
            "アセットが一斉にアップグレードされていないか差分を確認してください。",
            file=sys.stderr,
        )
        return 1

    print("\nOK: Unity バージョンの記述は全て一致しています。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
