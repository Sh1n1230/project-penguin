---
name: build
description: Project Penguin を Android (APK / AAB) または iOS (Xcode プロジェクト) にビルドする。ビルド・build・APK・AAB・実機・配布・リリース・Xcode・署名・keystore の話が出たら使う。ビルドが失敗したときの切り分けもここ。
---

# ビルド

実体は `Assets/Editor/Build/`。Editor メニューと CLI が同じ `ProjectBuilder.Run()` を通るので、**どちらで作っても成果物は同じ**。

## まず確認すること

1. **Unity Editor でそのプロジェクトを開いていないか。** Unity は同一プロジェクトを二重に開けない。CLI ビルドの前に Editor を閉じる。
2. **`Assets/Editor/` の `.meta` が生成済みか。** 新規スクリプトを足した直後は `.meta` が無い。Editor を一度開けば作られる。`python scripts/check_unity_meta.py` で確認できる。
3. **対象プラットフォームのモジュールが入っているか。** Unity Hub > インストール > 6000.6.0f1 > モジュールを加える に Android Build Support (OpenJDK / Android SDK & NDK 込み) と iOS Build Support。

## Editor から

メニュー `Build/` に 4 つ並んでいる。

| メニュー | 出力 | 用途 |
|---|---|---|
| `Android APK (Development)` | `Builds/Android/<product>-<version>-dev.apk` | 実機で動かして確認する。プロファイラ接続あり |
| `Android APK` | `Builds/Android/<product>-<version>.apk` | 動作確認用のリリース構成 |
| `Android AAB (配布用)` | `Builds/Android/<product>-<version>.aab` | Google Play へ上げる。**署名鍵の環境変数が必須** |
| `iOS Xcode プロジェクト` | `Builds/iOS/` | macOS 上の Xcode で開いて実機ビルド |

成功すると出力先が開く。失敗は Console と、入力不備の場合はダイアログに出る。

## CLI から

`-quit` は付けない (終了コードは `BuildEntry` 側が `EditorApplication.Exit` で返す)。

```bash
# Windows
"C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe" \
  -batchmode -nographics -projectPath . -logFile - \
  -executeMethod ProjectPenguin.Editor.Build.BuildEntry.AndroidApk -- --dev

# macOS
/Applications/Unity/Hub/Editor/6000.6.0f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -nographics -projectPath . -logFile - \
  -executeMethod ProjectPenguin.Editor.Build.BuildEntry.IosXcode
```

`-executeMethod` に渡せるのは `BuildEntry.AndroidApk` / `BuildEntry.AndroidAab` / `BuildEntry.IosXcode`。

| 追加引数 | 意味 |
|---|---|
| `--dev` | Development Build (プロファイラ / デバッガ接続) |
| `--output <dir>` | 出力ルート。既定は `Builds` |
| `--bundle-version <x.y.z>` | この回だけ bundleVersion を上書き |
| `--version-code <n>` | この回だけ Android の versionCode を上書き |

初回は IL2CPP のビルドで 20〜40 分かかる。バックグラウンド実行にして、進捗はログで見る。

## 署名

**鍵ファイルもパスワードもリポジトリに置かない。** 環境変数からしか読まない。

| 環境変数 | 内容 |
|---|---|
| `PENGUIN_ANDROID_KEYSTORE` | `.keystore` / `.jks` へのパス |
| `PENGUIN_ANDROID_KEYSTORE_PASS` | キーストアのパスワード |
| `PENGUIN_ANDROID_KEYALIAS` | エイリアス名 |
| `PENGUIN_ANDROID_KEYALIAS_PASS` | エイリアスのパスワード |
| `PENGUIN_IOS_TEAM_ID` | iOS の Apple Developer Team ID (任意) |

未設定なら APK は debug 鍵で通り、AAB は明示的に失敗する。`PlayerSettingsScope` がビルド後に PlayerSettings を必ず元へ戻すので、**パスワードが `ProjectSettings.asset` に残ることはない**。ビルド後に `git status` が汚れていたらそれ自体がバグなので報告する。

## ProjectSettings 側でまだ直っていないもの

これらは `.asset` の直接編集が禁止されているため、**Unity Editor 上での操作をユーザーに依頼する**。勝手に書き換えない。

- `companyName` が `DefaultCompany` のまま
- `applicationIdentifier` が URP テンプレートの既定値 (`com.UnityTechnologies.com.unity.template.urpblank`) のまま。配布前に自前のものへ変える
- `AndroidTargetSdkVersion` が `0` (= Automatic / インストール済みの最新)

## よくある失敗

| 症状 | 原因 |
|---|---|
| `Build Settings に有効なシーンが 1 つもありません` | File > Build Profiles のシーンリストが空。`EditorBuildSettings.asset` を手で書かず Editor から追加する |
| `<target> へ切り替えられませんでした` | ビルドモジュール未インストール |
| `AAB のビルドには署名鍵が要ります` | 上の環境変数が未設定 |
| CLI が無言で終わる / ロックで止まる | Editor がそのプロジェクトを開いている |
| IL2CPP のリンクエラー | `Library/` を消して作り直すと直ることがある (再生成に時間がかかる) |
