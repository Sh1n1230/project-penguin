---
paths:
  - "Assets/**"
  - "ProjectSettings/**"
  - "Packages/**"
---

# Unity 作業ルール

## 触ってはいけないファイル

`.unity` `.prefab` `.asset` `.meta` `.mat` `.anim` `.controller` `.mask` `.playable` は Unity が管理する YAML。**テキストとして直接書き換えない。** GUID の整合性が壊れて参照が全部外れる。変更が必要なら Unity Editor 経由の手順を提示する。

`Library/` `Temp/` `Logs/` `obj/` `*.csproj` `*.slnx` は Unity と IDE が再生成する。読む必要も編集する必要もない。

`.asmdef` `.asmref` `.json` (Packages/manifest.json 等) は通常のテキストとして編集してよい。

## `.meta` ファイル

アセットを追加・移動・削除したら、対応する `.meta` も必ず同じコミットに含める。`.meta` が欠けると別環境で GUID が振り直され、参照が壊れる。`.meta` だけが残った状態も同様に壊れる。

## アセンブリ構成

`Assets/Scripts/` は asmdef 単位で分割する。

| asmdef | 責務 | UnityEngine 依存 |
|---|---|---|
| `Domain` | 氷の減少・CO₂e 換算・報酬判定などの純粋なルール | **なし** |
| `Systems` | MonoBehaviour によるゲーム進行 | あり |
| `Data` | SQLite アクセス | あり |
| `Backend` | FastAPI クライアント | あり |
| `Presentation` | UI・アニメーション | あり |

**ゲームのルール計算は `Domain` に置き、`UnityEngine` に依存させない。** EditMode テストで検証でき、Editor を起動せずに正しさを確認できる。MonoBehaviour に計算ロジックを書かない。

テストは `Assets/Tests/EditMode/`(`Domain` 中心)と `Assets/Tests/PlayMode/`。

## C# の書き方

- private フィールドは `_camelCase`、public メンバーは `PascalCase`、ローカル変数は `camelCase`。
- Inspector に出すフィールドは `[SerializeField] private`。`public` フィールドで公開しない。
- **シリアライズ済みフィールドの名前を変えるときは `[FormerlySerializedAs]` を付ける。** 付けないと既存のシーン・プレハブの値が失われる。
- `Update()` 内で `GetComponent` / `Find` / `Camera.main` を呼ばない。キャッシュする。
- `async void` を避け、`UniTask` 未導入のうちはコルーチンか `async Task` + 呼び出し側での例外処理にする。

## シーンとプレハブ

`.unity` / `.prefab` のマージは構造的に壊れやすい。`.gitattributes` で UnityYAMLMerge を指定しているが**同じシーンを複数ブランチで同時に編集しない**方針を優先する。シーンを触る作業は 1 ブランチに閉じる。

## パッケージ

`Packages/manifest.json` を手で編集したら `packages-lock.json` も一緒にコミットする。パッケージ追加は提案にとどめ、勝手に増やさない。
