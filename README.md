# Project Penguin

> 何もしないと、ペンギンの氷が溶けていく。

## コンセプト

環境問題は、誰もが「大事だ」と思いながら、自分の日常と結びつかないまま忘れられていきます。数字やグラフでは人は動かない。でも、自分が育てたペンギンの足場が日に日に小さくなっていくのを見たら、人は動くと信じています。

ゲーム内の氷は、ユーザーの現実の行動と連動します。1 日 1 回、マイボトルや消した電気など、何でもよいエコな行動の写真を撮ると、それが今日の記録になって氷が守られ、AI が写真を見分けて電気・水などの資源が島に届きます。歩いた歩数はガスに、夜のミッションの振り返りはどれにでも使える資源になります。集めた資源とペンギンたちで施設を建て、お魚を作って港に届け、島を広げていく「生産の島」がゲームの主軸です。記録を休むと氷が溶けて、広げた島の端から沈んでいきます (記録すれば浮かびます)。

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
│  Game Logic (Domain)           │
│  ├─ GameSession (氷・来訪)     │
│  ├─ IslandGame (生産の島)      │
│  ├─ DailyMission               │
│  └─ PenguinDex (図鑑)          │
│                                │
│  Local Data                    │
│  └─ JSON → SQLite (Hack Day)   │
└───────────────┬────────────────┘
                │
             REST API
                │
                ▼
┌────────────────────────────────┐
│            FastAPI             │
│                                │
│  Eco Photo Service             │
│  ├─ Image Validation           │
│  ├─ Gemini Client              │
│  └─ JSON Validation            │
│     (カテゴリ・写っていたもの) │
│                                │
│  API Key Management            │
└───────────────┬────────────────┘
                │
                ▼
          Gemini / OpenRouter
```

## プライバシー方針

本プロジェクトはユーザーの日常を写した写真 (と、以前の設計ではレシート、すなわち購買履歴) を扱います。これは実装が始まる前に決めておくべき設計制約であり、後から思い出すものではありません。以下を前提として実装します。

1. **写真は端末にもサーバにも保存しない。** クライアントはカメラ映像の 1 フレームをメモリ上で JPEG にして判定に渡し、結果を受け取ったら捨てる。FastAPI 側も画像をメモリ上で Gemini に渡し、レスポンスを得た時点で破棄する。ディスクへの永続化やログへの出力を行わない。
2. **ローカルのデータはリポジトリにコミットしない。** 端末上の保存 (今は JSON、Hack Day に SQLite) には行動の記録が入るため、`.gitignore` で `*.db` / `*.sqlite*` を除外している。
3. **端末外に出すのは判定に要る写真 1 枚と、その分類結果だけ。** 記録に残すのは分類・写っていたものの名前・受け取った資源の量で、写真そのものは残さない。
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

上記アーキテクチャ図のうち、クライアントはほぼ一通りできています。backend と SQLite は Hack Day に作ります。

**実装済み**

- ビルド・署名・CI の土台 (`Assets/Editor/Build/`、`.github/workflows/`、`scripts/`)。iOS の歩数 (CoreMotion) のためのビルド後処理 (`IosPostprocess`)
- 生産の島 (`Assets/Scripts/Domain/Island/`): 10×10 の盤面、開拓、15 種の施設と生産の連鎖、ペンギンの配属、港の注文とレベル、真珠、放置中の生産、氷が足りないと後から広げた土地から沈む規則。仕様は [`docs/production-island/game-design.md`](docs/production-island/game-design.md)
- ゲームロジック v3 の状態機械 (`Assets/Scripts/Domain/Game/`)。氷・盾・おかえり・氷のかけら・見た目の段・ペンギンの来訪・スタンプ。仕様は [`docs/game-logic.md`](docs/game-logic.md)、Python の参照実装は `tools/game_sim/`
- ホームの 3D の島 (`Assets/Scenes/ProductionIslandHome.unity`。`HomeWorld.unity` を複製したシーンで、元の `HomeWorld.unity` は氷山と小屋のまま残してある。`Assets/Scripts/Presentation/World/`)。施設が動き、ペンギンが働き、沈む・浮かぶ・建てる・作ったの演出が出る。ドラッグで移動、ピンチで寄り引き、タップで選ぶ・建てる・広げる
- UI Toolkit の画面 (`Assets/UI/`、`Assets/Scripts/Presentation/UI/`): ホームの資源と道具・下から出るシート (建てる・施設・港・生産量)、エコ写真の撮影 → 解析中 → 結果、ミッション (選ぶ・夜の振り返り)、記録、図鑑、メニュー、はじめての案内
- 保存 (`Assets/Scripts/Data/`、`GameStateSystem`)。氷は操作の記録を再生して戻し、島は状態を保存する。今は JSON
- 写真の判定の口 (`IEcoPhotoJudge`) とモック。歩数 (iOS は CMPedometer、Editor は開発用の操作)
- 上記の EditMode テスト (`Assets/Tests/EditMode/`)。開発ビルドと Editor ではホームに早送りなどの操作が出る

**未実装 (Hack Day に作る)**

- FastAPI バックエンド (`backend/`) の写真判定と、Unity 側の HTTP クライアント (`HttpEcoPhotoJudge`)。API の形は game-design.md §12
- SQLite による保存 (`IGameStore` の差し替え)
- スポンサー賞に向けた連携 (未決。`docs/decisions.md`)

## ライセンス

チーム **ueco** (UEC + ECO、読みは「ユーエコ」) が作ったソースコード・ドキュメント・素材は [MIT ライセンス](LICENSE) で提供します。Project Penguin はこのプロダクトの開発コード名です。

外部から取り込んだフォント・パッケージ・データ (排出係数やミッションの値の出典など) は MIT の対象外で、それぞれの元のライセンスや利用規約に従います。一覧は [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) にあります。
