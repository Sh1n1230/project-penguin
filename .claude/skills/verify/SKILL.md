---
name: verify
description: コミット・PR の前に、CI が回すのと同じ検査をローカルで一括実行する。検査・チェック・確認・コミット前・PR 前・CI が落ちた・レビュー前と言われたら使う。
---

# 出す前の検査

`.github/workflows/ci.yml` が PR ごとに回すものと同じ内容を、ローカルで先に通す。**CI で落ちてから直すより速い。**

## 手順

上から順に実行し、**落ちたものがあっても最後まで走らせてから**まとめて報告する。1 つ目で止めると他の失敗が隠れる。

### 1. 秘密情報

```bash
python scripts/check_secrets.py
```

レシート画像・購買履歴・API キーを扱うプロジェクトなので最優先。落ちたら**直す前に、それが既にコミット済みかを確認する**。コミット済みなら履歴からの除去とキーの失効が要る (`.claude/rules/privacy.md`)。

### 2. Unity プロジェクトの整合性

```bash
python scripts/check_unity_meta.py
python scripts/check_unity_version.py
```

- `.meta` 欠けは、**新しくスクリプトやアセットを足した直後に必ず出る**。Unity Editor を一度開けば生成されるので、ユーザーに開いてもらう。エージェント側で `.meta` を書いて埋めてはいけない。
- バージョン不一致は `ProjectSettings/ProjectVersion.txt` と `README.md` / `.github/workflows/unity-tests.yml` の食い違い。Editor を上げたなら参照側を揃える。

### 3. backend

`backend/pyproject.toml` があるときだけ。

```bash
cd backend
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest -q
```

`pytest` の終了コード 5 (テストが 1 件も無い) は CI 上では失敗扱いにしていない。整形だけの差分なら `uv run ruff format .` を先に流してよい。

### 4. Unity のテスト

CI では回らない (ライセンス認証が要るため `main` への push と手動起動に限定)。**`Assets/Scripts/` や `Assets/Tests/` を触ったなら、Unity Editor の Test Runner で EditMode を回すようユーザーに依頼する。** 特に `Domain` は `UnityEngine` 非依存なので EditMode だけで検証できる。

## 報告のしかた

検査ごとに 通った / 落ちた と、落ちたものは原因と次の一手を書く。全部通ったなら、`CLAUDE.md` の規約に沿ったコミットメッセージ案まで出す (**commit は指示があるまで実行しない**)。
