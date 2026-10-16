# Project Penguin

毎日 1 枚のエコ写真・歩数・ミッションで資源を集め、ペンギンたちと「生産の島」を育てる Unity アプリ。記録を休むと氷が溶け、広げた島の端から沈む。コンセプトと設計判断は `@README.md` を参照。

## 応答の言語

**ユーザーへの返答・説明・質問はすべて日本語で書く。** 途中で英語に切り替えない。コード・識別子・コマンド・ログの引用は原文のままでよい。

## 作業の姿勢

**デモで見せる最小限ではなく、製品として完成させるつもりで作る。** 「デモが動けば十分」と範囲を絞ると、結局完成しない。

- 頼まれたことの周辺まで気を回す。演出・空の状態・エラー時・保存・テストなど、完成品に要るものは言われる前に入れる。やりすぎ・気が利きすぎくらいでよい。
- 見た目は最優先の品質項目として扱う。仮データ・仮の見た目のまま「動く」で止めない。
- 範囲を削る提案は、締切などの具体的な制約があるときだけ、理由を添えて行う。

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
| `Assets/UI/` | UI Toolkit の画面 (UXML / USS)、デザインシステム、フォント |
| `Assets/3Dmodel/` | ゲームで使う 3D モデル (FBX とテクスチャ。LFS 管理) |
| `Assets/Prototype/` | 試作用のアセット (`UITest.unity` の仮モデル用マテリアル。`HomeWorld.unity` も氷・海・小屋のマテリアルを使っている) |
| `ArtSource/` | UV レイアウトなど、ゲームには読み込まない制作素材。Unity に取り込ませないため `Assets/` の外に置く |
| `backend/` | FastAPI (`src/penguin_backend/`, `tests/`) |
| `scripts/` | CI とローカル共用の検査スクリプト |
| `tests/hooks/` | `.claude/hooks/` と `scripts/` の判定のテスト (pytest、標準ライブラリのみ) |
| `docs/` | 設計メモ (`ui-structure.md` 画面構成、`design-system.md` 見た目の決まりごと) と参考画像 |
| `docs/production-island/` | 生産の島 (ゲームの主軸のインクリメンタル型の遊び) の仕様 (`game-design.md`)・素材・確認手順・テスト記録 |
| `docs/game-logic.md` | 氷の規則の仕様 (氷・盾・おかえり・段・来訪・スタンプ)。値と規則はこれを正とする。生産の島の値と規則は `docs/production-island/game-design.md` を正とする |
| `tools/game_sim/` | ゲームロジックの Python 参照実装。C# の期待値 (`GameSimGolden.cs`) を生成する |
| `docs/decisions.md` | チームの決定事項 (Discord・JPHACKS の Notion と Slack から抽出)。仕様や前提を確かめるときに読む |
| `.claude/rules/` | 領域別ルール (該当ファイルを読むと自動適用される) |
| `.claude/hooks/` | 破壊的操作を機械的に止める PreToolUse フック |
| `.mcp.json` | Unity MCP の接続先 (OS 非依存の localhost HTTP) |

## コマンド

| 目的 | コマンド |
|---|---|
| backend の整形 | `cd backend && uv run ruff format .` |
| backend の lint | `cd backend && uv run ruff check .` |
| backend の型検査 | `cd backend && uv run mypy .` |
| backend のテスト | `cd backend && uv run pytest` |
| ゲームロジックの参照実装のテスト | `uv run --no-project --with pytest pytest tools/game_sim` |
| `.meta` の整合性検査 | `uv run --no-project python scripts/check_unity_meta.py` |
| Editor バージョンの一致検査 | `uv run --no-project python scripts/check_unity_version.py` |
| 秘密情報の検査 | `uv run --no-project python scripts/check_secrets.py` |
| フックと検査スクリプトのテスト | `uv run --no-project --with pytest pytest tests/hooks` |
| Unity のテスト | Unity Editor の Test Runner (EditMode / PlayMode) |
| アプリのビルド | Editor の `Build/` メニュー、または `/build` |

CI (`.github/workflows/ci.yml`) はこのうち Unity テスト以外を PR ごとに回す。

## スキルの使い分け

**下の表に当てはまる作業は、ユーザーの明示的な指示を待たずに該当スキルを読んでから着手する。** 表にないものは通常どおり進める。

| 作業 | 使うもの |
|---|---|
| ビルド・署名・実機確認・配布 | `/build` |
| コミット / PR の前の検査 | `/verify` |
| 変更のレビュー | `/code-review` |
| UI を作る・直す | `ui` (Canvas なら `ui-ugui`、UI Toolkit なら `ui-uitk`) |
| シーン・GameObject・アセットを Editor 経由で操作 | `unity-mcp-skill` |
| Editor の起動・テスト実行を CLI から | `unity-cli` |
| パッケージの追加・更新 | `unity-package-management` (追加は提案どまり) |
| 多言語対応・日本語フォント | `localization` / `optimize-text-mesh-pro` |
| 音声・WebGL の最適化 | `optimize-audio` / `optimize-web` |

`.claude/rules/` は path スコープ付きで**該当ファイルを読んだ時点で自動適用される**ので、明示的に読みに行く必要はない。

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

- **実装済み**: ビルド・CI の土台。生産の島の規則 (`Assets/Scripts/Domain/Island/`、仕様は `docs/production-island/game-design.md`) と氷の状態機械 (`Assets/Scripts/Domain/Game/`、仕様は `docs/game-logic.md`)。ホームの 3D の島 (`ProductionIslandHome.unity`、`Assets/Scripts/Presentation/World/`。`HomeWorld.unity` を複製したシーンで、組み込みは **Production Island > Setup Home Island**。`HomeWorld.unity` は元の氷山と小屋のまま変えない)。UI Toolkit の全画面 (ホームのシート・エコ写真の撮影〜結果・ミッション・記録・図鑑・メニュー・はじめての案内)。保存 (JSON、`Assets/Scripts/Data/`)。写真判定の口 (`IEcoPhotoJudge`) とモック。iOS の歩数。EditMode テスト。開発ビルドと Editor ではホームに早送りなどのデモ用の操作が出る。
- **未実装 (Hack Day に作る)**: FastAPI の写真判定と Unity 側の HTTP クライアント、SQLite (`IGameStore` の差し替え)、スポンサー賞に向けた連携 (未決)。

UI や画面遷移を触る前に、既存の Presenter と `docs/ui-structure.md` を読むこと。未実装の領域で実装を探して見つからない場合は「まだ存在しない」が正しい答えであり、既存実装を推測で仮定しないこと。
