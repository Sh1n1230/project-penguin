# Project Penguin

現実の消費行動を CO₂e に換算し、その結果でゲーム内の氷とペンギンの生息状況が変化する Unity アプリ。コンセプトと設計判断は `@README.md` を参照。

## 技術スタック

| 領域 | 使用技術 |
|---|---|
| クライアント | Unity 6000.6.0f1 / URP 17.6 / Input System 1.20 |
| ローカルデータ | SQLite |
| バックエンド | FastAPI (Python 3.11+) |
| LLM | Gemini (レシート解析) |
| バイナリ管理 | Git LFS |

## ディレクトリ

| パス | 内容 |
|---|---|
| `Assets/Scripts/` | ゲームコード (asmdef 単位で分割) |
| `Assets/Tests/` | EditMode / PlayMode テスト |
| `Assets/Scenes/`, `Assets/Settings/` | シーン・URP 設定 |
| `backend/` | FastAPI (`src/penguin_backend/`, `tests/`) |
| `scripts/` | CI とローカル共用の検査スクリプト |
| `.claude/rules/` | 領域別ルール (該当ファイルを読むと自動適用される) |
| `.claude/hooks/` | 破壊的操作を機械的に止める PreToolUse フック |

## コマンド

| 目的 | コマンド |
|---|---|
| backend の整形 | `cd backend && uv run ruff format .` |
| backend の lint | `cd backend && uv run ruff check .` |
| backend の型検査 | `cd backend && uv run mypy .` |
| backend のテスト | `cd backend && uv run pytest` |
| `.meta` の整合性検査 | `python scripts/check_unity_meta.py` |
| 秘密情報の検査 | `python scripts/check_secrets.py` |
| Unity のテスト | Unity Editor の Test Runner (EditMode / PlayMode) |

CI (`.github/workflows/ci.yml`) はこのうち Unity テスト以外を PR ごとに回す。

## 絶対規則

1. **レシート画像と購買明細をディスク・ログ・レスポンスに残さない。** 端末外に出してよいのは CO₂e 値だけ。→ `.claude/rules/privacy.md`
2. **API キーをクライアントコードにも設定ファイルにも書かない。** backend が環境変数から読む。
3. **`.unity` / `.prefab` / `.asset` / `.meta` をテキストとして編集しない。** Unity Editor 経由で変更する。→ `.claude/rules/unity.md`
4. **`Library/` `Temp/` `Logs/` `*.csproj` `*.slnx` は生成物。** 読む必要も編集する必要もない。
5. **コードを読まずに書かない。** 変更前に既存の実装・命名・近い責務のクラスを必ず確認する。
6. **3 ステップ以上のタスクは Plan モードで開始する。**

## Git

**commit・push・PR 作成はユーザーが明示的に指示したときだけ実行する。** 指示がなければメッセージ案の提示にとどめる。

### ブランチ

`main` に直接コミット・push しない。`<prefix>/<内容>` の作業ブランチを切る (例: `feat/ice-melt-system`)。prefix は下のコミット type と同じ語を使う。

### コミットメッセージ

`<type>(<scope>): <日本語の要約>` — **prefix は英語、要約は日本語**で書く。

```
feat(unity): 氷の減少システムを追加
fix(backend): レシート解析のレスポンス検証が空配列を通す問題を修正
docs: プライバシー方針に認証の未実装状態を明記
```

| type | 用途 |
|---|---|
| `feat` | 機能追加 |
| `fix` | バグ修正 |
| `refactor` | 挙動を変えない内部変更 |
| `perf` | パフォーマンス改善 |
| `test` | テストの追加・修正 |
| `docs` | ドキュメントのみ |
| `chore` | 依存更新・雑務 |
| `ci` | CI 設定 |

scope は `unity` / `backend` / `docs` / `ci`。プロジェクト全体にまたがる場合は省略する。

- 要約は 50 字程度まで。「なぜ」を書くべきときは本文に日本語で 1〜2 段落続ける。
- 1 コミット 1 論点。無関係な変更を混ぜない。

### その他

- アセットと対応する `.meta` は必ず同一コミットに含める。
- `.gitattributes` の LFS 追跡パターンは後から変えると履歴の書き換えが要る。変更提案は必ず理由とともに事前確認する。

## 現状

Unity 6 URP プロジェクトの初期化のみ完了。GameState / PenguinSystem / IceSystem / DailyMission / Pokedex / Reward、SQLite、FastAPI はいずれも未実装。実装を探して見つからない場合は「まだ存在しない」が正しい答えであり、既存実装を推測で仮定しないこと。
