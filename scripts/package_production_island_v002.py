"""Index the canonical v002 files without duplicating Unity assets or source."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "docs/production-island-v002"


def selected_paths() -> list[Path]:
    paths: list[Path] = []
    for parent in (ROOT / "Assets/3Dmodel", ROOT / "ArtSource"):
        paths.extend(
            p for p in parent.iterdir()
            if p.is_dir() and p.name.endswith("_v002")
            and (p.name.startswith(("Building_", "Harbor_")) or p.name == "ProductionIsland_v002")
        )
    paths.extend(ROOT / p for p in (
        "Assets/3Dmodel/Penguin_v002",
        "Assets/UI/ProductionIslandReview",
        "Assets/UI/Fonts/MPLUSRounded1c-Regular.ttf",
        "Assets/InputSystem_Actions.inputactions",
        "Assets/Scenes/ProductionIslandFacilityReview.unity",
        "Assets/Scenes/KamabokoDesignReview.unity",
        "ArtSource/ProductionIsland_v001/generate_models.py",
        "docs/production-island-facilities-v002.md",
        "docs/production-island-facility-motions.md",
        "docs/production-island-review-user-guide.md",
        "docs/kamaboko-design-v002.md",
        "docs/testing/production-island-visual-review.md",
        "scripts/package_production_island_v002.py",
    ))
    paths.extend(ROOT / "Assets/Scripts/Presentation/World" / (name + ".cs") for name in (
        "FacilityDesignGallery", "FacilityProductionCycle", "WorkshopPenguin",
        "KamabokoProductionCycle", "KamabokoPenguinWorker",
    ))
    paths.extend(ROOT / "Assets/Editor/ProductionIsland" / (name + ".cs") for name in (
        "FacilityRevisionBuilder", "FacilityRevisionCapture", "KamabokoRevisionBuilder", "FacilityReviewFocus",
    ))
    return paths


def digest(path: Path) -> str:
    data = path.read_bytes()
    # Match Git's LF checkout for text while preserving binary checksums.
    if b"\0" not in data[:8000]:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    assert DESTINATION.resolve().is_relative_to(ROOT.resolve())
    DESTINATION.mkdir(parents=True, exist_ok=True)
    files: dict[Path, Path] = {}
    for source in selected_paths():
        if not source.exists():
            raise FileNotFoundError(source)
        if source.is_dir():
            for item in source.rglob("*"):
                if item.is_file():
                    if item.name in {"native-mouse-diagnostic.cs", "native-mouse-diagnostic.cs.txt",
                                     "native-mouse-diagnostic.png", "pointer-input-test.cs.txt", "motion-verification.json"}:
                        continue
                    files[item] = item
        else:
            files[source] = source
        meta = Path(str(source) + ".meta")
        if meta.exists():
            files[meta] = meta

    records = []
    for source in sorted(files):
        checksum = digest(source)
        records.append({"path": source.relative_to(ROOT).as_posix(),
                        "bytes": source.stat().st_size, "sha256": checksum})
    report = {"date": "2026-10-11", "kind": "v002 canonical file index",
              "sha256_text_newlines": "LF",
              "original_unity_assets_kept": True, "verified_files": len(records),
              "total_bytes": sum(record["bytes"] for record in records), "files": records}
    (DESTINATION / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DESTINATION / "README.md").write_text(
        "# 生産の島・施設v002 一覧\n\n"
        "素材、制作元、確認シーン、動作コードへの入口です。ファイルは元の場所に一つだけ保持します。\n\n"
        "**[Unityで確認する手順](../production-island-review-user-guide.md)**\n\n"
        "Unity Hubではこのリポジトリのルートを開き、"
        "Projectの `Assets/Scenes/ProductionIslandFacilityReview` をダブルクリックして▶を押します。\n"
        "GameでScaleを1xにし、「施設を選ぶ」から名前をクリックしてください。MCPは不要です。\n\n"
        "- [全施設の仕様](../production-island-facilities-v002.md)\n"
        "- [調査した特徴と動き](../production-island-facility-motions.md)\n"
        "- [確認・修正記録](../testing/production-island-visual-review.md)\n"
        "- [ファイル一覧・SHA-256](manifest.json)（テキストはLF改行を基準）\n\n"
        "manifestのパスはリポジトリのルートからの相対パスです。モデルはAssets/3Dmodel、"
        "制作元はArtSource、動作コードはAssets/Scripts/Presentation/Worldにあります。\n",
        encoding="utf-8")
    print(json.dumps({"folder": str(DESTINATION), "verified_files": len(records),
                      "megabytes": round(report["total_bytes"] / 1024**2, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
