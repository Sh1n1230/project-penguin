"""Unity の .meta 整合性チェック。

アセットと .meta のどちらか片方だけがコミットされていると、別環境で GUID が
振り直されて参照が壊れる。git の追跡対象を正としてその対応を検証する。

    python scripts/check_unity_meta.py
"""

from __future__ import annotations

import subprocess
import sys

ASSETS = "Assets"
# Unity が .meta を作らないもの。
IGNORED_NAMES = {".gitkeep", ".gitignore", ".ds_store", "thumbs.db"}


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", ASSETS],
        capture_output=True,
        text=True,
        check=True,
    )
    return [p for p in out.stdout.split("\0") if p]


def main() -> int:
    files = tracked_files()
    if not files:
        print(f"{ASSETS}/ に追跡対象がありません。")
        return 0

    file_set = set(files)
    assets = {p for p in files if not p.endswith(".meta")}
    metas = {p for p in files if p.endswith(".meta")}

    # 追跡対象のファイルから、Unity が .meta を作る対象のディレクトリを復元する。
    dirs: set[str] = set()
    for path in assets:
        parts = path.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    dirs.discard(ASSETS)  # Assets 自身に .meta は無い

    errors: list[str] = []

    for path in sorted(assets):
        if path.rsplit("/", 1)[-1].lower() in IGNORED_NAMES:
            continue
        if path + ".meta" not in file_set:
            errors.append(f"  .meta が無い          : {path}")

    for path in sorted(dirs):
        if path + ".meta" not in file_set:
            errors.append(f"  ディレクトリの .meta が無い: {path}/")

    for meta in sorted(metas):
        target = meta[: -len(".meta")]
        if target not in file_set and target not in dirs:
            errors.append(f"  対応するアセットが無い    : {meta}")

    if errors:
        print("Unity の .meta 整合性エラー:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        print(
            "\nアセットと .meta は必ず同じコミットに含めてください。"
            "片方だけだと別環境で GUID が振り直され、シーンやプレハブの参照が壊れます。",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(assets)} 件のアセットと .meta が対応しています。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
