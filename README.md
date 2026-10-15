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

macOS の場合:

```bash
git config merge.unityyaml.name "Unity SmartMerge"
git config merge.unityyaml.driver '"/Applications/Unity/Hub/Editor/6000.6.0f1/Unity.app/Contents/Helpers/UnityYAMLMerge" merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"'
git config merge.unityyaml.recursive binary
```

未登録でも通常のテキストマージにフォールバックするだけなので、動作しなくなることはありません。

### 3. Unity プロジェクトを開く

Unity Hub からリポジトリのルートディレクトリを開きます。初回は `Library/` の生成に時間がかかります。

### 4. Unity MCP (Claude Code から Editor を操作する場合)

接続先はリポジトリの `.mcp.json` で共有しています (`http://127.0.0.1:8080/mcp`)。OS に依存しないため、各自の登録は不要です。

1. Unity で **Window → MCP for Unity** を開き、Transport を HTTP にしてサーバを起動する
2. Claude Code をリポジトリで起動し直し、`/mcp` で `UnityMCP` が connected になっていることを確認する

MCP for Unity ウィンドウの Configure ボタンは、個人設定 (`~/.claude.json` の local スコープ) に登録するのと同時に **`.mcp.json` から `UnityMCP` を消します**。押した場合は `.mcp.json` の変更をコミットせず `git restore .mcp.json` で戻してください。個人設定に同名の `UnityMCP` がある場合はそちらが優先されるだけで、衝突はしません。

### 5. バックエンド

`backend/` を参照してください。API キーの設定方法は `backend/.env.example` に記載しています。

## ビルド

**MVP の配布対象は iOS のみです** (チーム全員の実機が iOS で、Android の実機確認ができないため。`docs/decisions.md` の 2026-10-13 の決定)。Android のビルド経路も残してありますが、MVP では動作確認の対象外です。

ビルドスクリプトは `Assets/Editor/Build/` にあり、Editor メニューと CLI が同じ経路を通ります。成果物は `Builds/` (git 管理外) に出ます。

| メニュー (`Build/`) | 出力 | MVP |
|---|---|---|
| iOS Xcode プロジェクト | `Builds/iOS/` | 対象 |
| Android APK (Development) | `Builds/Android/<product>-<version>-dev.apk` | 対象外 |
| Android APK | `Builds/Android/<product>-<version>.apk` | 対象外 |
| Android AAB (配布用) | `Builds/Android/<product>-<version>.aab` | 対象外 |

Unity Hub の 6000.6.0f1 に **iOS Build Support** を追加しておいてください。iOS は Xcode プロジェクトを出力するところまでで、実機へのインストールと配布は macOS 上の Xcode で行います。Android を試すときだけ **Android Build Support (OpenJDK / SDK & NDK 込み)** を追加します。

CLI から回す場合は Editor でプロジェクトを閉じてから実行します。`-quit` は付けません (終了コードはビルドスクリプト側が返します)。

```bash
# iOS の Xcode プロジェクト (macOS)
/Applications/Unity/Hub/Editor/6000.6.0f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -nographics -projectPath . -logFile - \
  -executeMethod ProjectPenguin.Editor.Build.BuildEntry.IosXcode -- --bundle-version 0.1.0 --build-number 5

# Android の APK (MVP 後に Android を再開するとき用。Windows の例)
"C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe" \
  -batchmode -nographics -projectPath . -logFile - \
  -executeMethod ProjectPenguin.Editor.Build.BuildEntry.AndroidApk -- --dev
```

`--` の後ろに渡せるオプション:

| オプション | 内容 |
|---|---|
| `--dev` | Development Build にする |
| `--output <dir>` | 出力先のルート (既定は `Builds/`) |
| `--bundle-version <x.y.z>` | 表示用のバージョン (iOS の `CFBundleShortVersionString`、Android の versionName) |
| `--build-number <n>` | iOS のビルド番号 (`CFBundleVersion`)。`5` や `1.0.3` のようにピリオド区切りで最大 3 つの数字。TestFlight に上げるたびに増やす |
| `--version-code <n>` | Android の versionCode |

### 署名

**証明書・キーストア・パスワードはリポジトリに置きません。** 環境変数からのみ読み込み、ビルド後は `PlayerSettings` を元の値へ戻すため `ProjectSettings.asset` に残りません。

iOS は Xcode 側で署名します。`PENGUIN_IOS_TEAM_ID` を設定すると、出力した Xcode プロジェクトに Team ID が入ります (任意)。

| 環境変数 | 内容 |
|---|---|
| `PENGUIN_IOS_TEAM_ID` | Apple Developer Team ID (任意) |

Android (MVP 後に再開するとき用):

| 環境変数 | 内容 |
|---|---|
| `PENGUIN_ANDROID_KEYSTORE` | キーストアのファイルへのパス |
| `PENGUIN_ANDROID_KEYSTORE_PASS` | キーストアのパスワード |
| `PENGUIN_ANDROID_KEYALIAS` | エイリアス名 |
| `PENGUIN_ANDROID_KEYALIAS_PASS` | エイリアスのパスワード |

未設定の場合、APK は debug 鍵でビルドされ (配布不可)、AAB は明示的に失敗します。

会社名は `ueco`、アプリ ID (Bundle Identifier) は iOS・Android とも `com.ueco.projectpenguin` です。TestFlight やストアに一度上げると変えられないので、変えるときはチームで決めてからにしてください。

## 現状

上記アーキテクチャ図のうち、実装済みなのは Presentation の一部です。図はこれから作るものを含めた設計を表しています。

**実装済み (ゲームの状態とはまだつながっていない)**

- ビルド・署名・CI の土台 (`Assets/Editor/Build/`、`.github/workflows/`、`scripts/`)
- UI Toolkit による 7 画面 (ホーム / 記録 / ミッション / スキャン / 解析中 / 結果 / メニュー) と画面遷移、SafeArea 対応 (`Assets/UI/`、`Assets/Scripts/Presentation/UI/`)。デザインシステムは `docs/design-system.md`、画面構成は `docs/ui-structure.md`
- スキャン画面のカメラプレビュー。撮影・解析はまだ行わず、解析中画面の進行と記録画面のグラフは仮の値で動く
- ホームの 3D ワールド (`Assets/Scenes/HomeWorld.unity`)。氷山と小屋のモデル、円周上を歩くペンギン、端末の縦横比に合わせたカメラの画角調整 (`Assets/Scripts/Presentation/World/`)
- ゲームロジック v3 の状態機械 (`Assets/Scripts/Domain/Game/`)。氷・盾・おかえり・氷のかけら・見た目の段・ペンギンの来訪・スタンプを、時計を注入して 1 日ずつ進める。仕様は [`docs/game-logic.md`](docs/game-logic.md)、Python の参照実装と 8 人の利用者のシミュレーションは `tools/game_sim/`。ホームの氷の量・吹き出し・氷山の大きさ・ペンギンの数はこの状態につながっており、開発ビルドでは「記録する」「1 日進める」で動かせる
- 上記の EditMode テスト (`Assets/Tests/EditMode/`)

**未実装**

- ゲームの状態の保存 (今はアプリを再起動すると初期状態に戻る)、ミッションの一覧と選び方、図鑑、CO₂ の採点 (週の選び方の氷)
- SQLite によるローカルデータ (`Data`)
- FastAPI バックエンド (`backend/`) とその Unity 側のクライアント (`Backend`)

## ライセンス

チーム **ueco** (UEC + ECO、読みは「ユーエコ」) が作ったソースコード・ドキュメント・素材は [MIT ライセンス](LICENSE) で提供します。Project Penguin はこのプロダクトの開発コード名です。

外部から取り込んだフォント・パッケージ・データ (排出係数やミッションの値の出典など) は MIT の対象外で、それぞれの元のライセンスや利用規約に従います。一覧は [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) にあります。
