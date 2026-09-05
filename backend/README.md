# backend

Project Penguin のバックエンド (FastAPI)。

**現時点では未実装です。** このディレクトリには、実装を始める前に固めておくべき前提だけが置かれています。

## 役割

Unity クライアントから受け取ったレシート画像を Gemini で解析し、購買内容を CO₂e に換算して返します。API キーの保持はこの層の責務であり、クライアントには一切渡しません。

- **Receipt Service** — Image Validation / Gemini Client / JSON Validation
- **Carbon Service** — Category Mapping / Emission Factors / CO₂e Calculation
- **API Key Management**

## セットアップ

パッケージマネージャは [uv](https://docs.astral.sh/uv/)。

```bash
cd backend
uv sync                  # 依存のインストール (.venv を作る)
cp .env.example .env     # .env に GEMINI_API_KEY を記入
```

`.env` は `.gitignore` で除外されています。public リポジトリのため、実キーのコミットは事故として回復不能(履歴に残る)です。

## 開発コマンド

| 目的 | コマンド |
|---|---|
| 整形 | `uv run ruff format .` |
| lint | `uv run ruff check .` |
| 型検査 | `uv run mypy .` (strict) |
| テスト | `uv run pytest` |

CI でも同じ 4 つが回ります (`.github/workflows/ci.yml`)。

ruff の `S` (bandit) と `T20` (`print` 禁止) は、レシート画像や購買明細を標準出力・ログに漏らさない制約を機械的に守らせるために有効化しています。無効化する前に下記のプライバシー要件を確認してください。

## 構成

```
backend/
├─ pyproject.toml           # 依存とツール設定 (ruff / mypy / pytest)
├─ src/penguin_backend/     # 実装
└─ tests/                   # pytest
```

## 実装時に守ること (TODO)

レシートはユーザーの購買履歴そのものです。以下は実装後に追加する対策ではなく、**書き始める前の制約**として扱ってください。詳細はリポジトリルートの README「プライバシー方針」を参照。

- [ ] **レシート画像をディスクに書かない。** メモリ上で処理し、Gemini へのリクエスト完了後に破棄する。一時ファイル・アップロードディレクトリを作らない。
- [ ] **画像や解析結果をログに出力しない。** デバッグログにも店名・品目・金額を残さない。エラー時も同様。
- [ ] **レスポンスは CO₂e スコアと必要最小限のメタ情報に絞る。** 購買明細の生データをクライアント外に集約・保存しない。
- [ ] **API キーは環境変数からのみ読む。** コード中へのハードコードや、設定ファイルへの実値記入を禁止する。
- [ ] **エンドポイント認証を導入する。** 現状は未認証。クライアントへの固定シークレット埋め込みはビルドを展開すれば取り出せるため対策にならない。Firebase Auth 等の正規のユーザー認証を検討する。
