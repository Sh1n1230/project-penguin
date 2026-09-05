# Project Penguin

> 何もしないと、ペンギンの氷が溶けていく。

## コンセプト

環境問題は、誰もが「大事だ」と思いながら、自分の日常と結びつかないまま忘れられていきます。数字やグラフでは人は動かない。でも、自分が育てたペンギンの足場が日に日に小さくなっていくのを見たら、人は動くと信じています。

ゲーム内の氷は、ユーザーの現実の行動と連動します。レシートを撮影するだけで日々の消費を CO2 換算でスコアリングし、環境負荷の低い選択を続けるほど氷が守られ、新しい種類のペンギンが住み着く。朝に選んだデイリーミッションを夜に振り返ることで、「今日はちゃんとやれた」という小さな達成が、ペンギンの居場所を増やしていきます。

放置すると失われる、という「現実と地続きの緊張感」こそが、このプロダクトの核です。

## アーキテクチャ

```
┌────────────────────────────────┐
│            Unity 6             │
│                                │
│  Presentation                  │
│  ├─ 3D Antarctic World         │
│  ├─ Penguins                   │
│  ├─ Animation                  │
│  └─ UI                         │
│                                │
│  Game Logic                    │
│  ├─ GameState                  │
│  ├─ PenguinSystem              │
│  ├─ IceSystem                  │
│  ├─ DailyMission               │
│  ├─ Pokedex                    │
│  └─ Reward                     │
│                                │
│  Local Data                    │
│  └─ SQLite                     │
└───────────────┬────────────────┘
                │
             REST API
                │
                ▼
┌────────────────────────────────┐
│            FastAPI             │
│                                │
│  Receipt Service               │
│  ├─ Image Validation           │
│  ├─ Gemini Client              │
│  └─ JSON Validation            │
│                                │
│  Carbon Service                │
│  ├─ Category Mapping           │
│  ├─ Emission Factors           │
│  └─ CO₂e Calculation           │
│                                │
│  API Key Management            │
└───────────────┬────────────────┘
                │
                ▼
          Gemini / OpenRouter
```

## プライバシー方針

本プロジェクトはレシート、すなわち**ユーザーの購買履歴そのもの**を扱います。これは実装が始まる前に決めておくべき設計制約であり、後から思い出すものではありません。以下を前提として実装します。

1. **レシート画像はサーバに保存しない。** FastAPI 側では画像をメモリ上で処理して Gemini に渡し、レスポンスを得た時点で破棄する。ディスクへの永続化やログへの出力を行わない。
2. **ローカル DB はリポジトリにコミットしない。** 端末上の SQLite には購買履歴が入りうるため、`.gitignore` で `*.db` / `*.sqlite*` を除外している。
3. **端末外に出すのは CO₂e スコアのみ。** 購買明細の生データ(店名・品目・金額)を端末外へ送信・集約しない。サーバとやり取りするのは解析に必要な最小限の入力と、算出済みの CO₂e 値に限る。
4. **API キーを Unity クライアントに埋め込まない。** Gemini / OpenRouter のキーは FastAPI 側でのみ保持し、クライアントはバックエンドを経由する。ビルド成果物を展開してもキーが取り出せないようにするため。

なお、バックエンドのエンドポイント認証は現時点で未実装です。クライアントに固定シークレットを埋め込む方式は、ビルドを展開すれば取り出せてしまうため対策になりません。開発中はエンドポイントを非公開に留め、本格運用時に Firebase Auth 等の正規のユーザー認証を導入します。

## セットアップ

### 必要環境

| | バージョン | 備考 |
|---|---|---|
| Unity | 6000.6.0f1 | 別バージョンで開くとアセットが一斉アップグレードされます |
| Git LFS | 3.x 以上 | クローン前に `git lfs install` |
| uv | 0.5 以上 | backend の依存管理と、Claude Code のフック実行に使います |
| Python | 3.11 | uv が `backend/.python-version` を見て自動で用意するため、個別のインストールは不要です |

Windows と macOS のどちらでも同じ手順で動きます。backend は uv が管理する `.venv` の中で完結し、Unity Editor は各自のネイティブ環境で動かします (Unity は GUI アプリのためコンテナ化していません)。

### 1. クローン

```bash
git lfs install
git clone https://github.com/Sh1n1230/project-penguin.git
cd project-penguin
```

3D モデルやテクスチャは Git LFS で管理しているため、`git lfs install` を先に済ませてからクローンしてください。

### 2. UnityYAMLMerge の登録

シーンやプレハブのコンフリクトを Unity のマージツールで構造的に解決するための設定です。`.gitattributes` に `merge=unityyaml` を指定していますが、マージドライバの実体は各自の `.git/config` に登録する必要があります。

Windows の場合:

```bash
git config merge.unityyaml.name "Unity SmartMerge"
git config merge.unityyaml.driver '"C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/Tools/UnityYAMLMerge.exe" merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"'
git config merge.unityyaml.recursive binary
```

macOS の場合は、ドライバのパスを `/Applications/Unity/Hub/Editor/6000.6.0f1/Unity.app/Contents/Tools/UnityYAMLMerge` に置き換えてください。

未登録でも通常のテキストマージにフォールバックするだけなので、動作しなくなることはありません。

### 3. Unity プロジェクトを開く

Unity Hub からリポジトリのルートディレクトリを開きます。初回は `Library/` の生成に時間がかかります。

### 4. バックエンド

`backend/` を参照してください。API キーの設定方法は `backend/.env.example` に記載しています。

## 現状

**Unity 6 URP プロジェクトの初期化のみが完了しています。** Game Logic (GameState / PenguinSystem / IceSystem / DailyMission / Pokedex / Reward)、SQLite によるローカルデータ、FastAPI バックエンドはいずれも未実装です。

上記アーキテクチャ図は実装済みの構成ではなく、これから作るものの設計を表しています。
