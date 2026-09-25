# Design System

Project Penguin の UI Toolkit 用デザインシステム。見た目の出典は `docs/reference/UI_ref.png` (主)、足りない部分を `docs/reference/UI_ref_proto.png` で補っている。

## ファイル構成

| パス | 役割 |
|---|---|
| `Assets/UI/DesignSystem/Tokens.uss` | デザイントークン (`:root` 変数) とテキスト用ユーティリティ |
| `Assets/UI/DesignSystem/Components.uss` | `.pp-*` コンポーネント。Unity 既定テーマの代わりになる最小限のベース指定もここに置く |
| `Assets/UI/DesignSystem/PenguinTheme.tss` | 上の 2 つを `@import` するテーマ。PanelSettings に設定している |
| `Assets/UI/DesignSystem/Icons/*.svg` | アイコン (VectorImage としてインポートされる) |
| `Assets/UI/DesignSystem/Catalog/DesignSystemCatalog.uxml` | 全コンポーネントの見本。UI Builder で開いて確認する |
| `Assets/UI/Fonts/` | 日本語フォント (仮) の `.ttf` とライセンス文書 |
| `Assets/UI/PanelSettings.asset` | 全画面共通の PanelSettings |
| `Assets/UI/Screens/<Screen>/` | 画面ごとの UXML と、その画面のレイアウト専用 USS |
| `Assets/UI/App/App.uxml` | 全画面を並べるルート。UIDocument のソースはこれ |
| `Assets/Scripts/Presentation/UI/ScreenNavigator.cs` | 表示する画面を 1 つに切り替える |
| `Assets/Scripts/Presentation/UI/ReceiptCameraPreview.cs` | スキャン画面にカメラ映像を映す |
| `Assets/Scripts/Presentation/UI/SafeAreaApplier.cs` | `Screen.safeArea` を UI に反映する |

テーマは PanelSettings 経由で全画面に自動で効く。画面の UXML から `Tokens.uss` / `Components.uss` を `<ui:Style>` で読み直す必要はない。UI Builder で編集するときは、Canvas 右上のテーマ選択で **PenguinTheme** を選ぶ。

## 基本方針

- **基準解像度は 1080×1920 (縦画面)**。PanelSettings は Scale With Screen Size、Match = 0 (幅基準)。縦長端末では縦方向に余りが出るが、横方向のレイアウトは端末によらず同じになる。設計上の 1pt はおよそ 2.75px。
- **値は必ずトークン経由で指定する。** 色・余白・角丸・文字サイズを USS に直書きしない。トークンに無い値が必要になったら、先に `Tokens.uss` に足す。
- **画面の USS にはレイアウトだけを書く。** 見た目 (色・角丸・文字) はコンポーネントのクラスに任せる。
- **Unity 既定テーマ (`UnityDefaultRuntimeTheme.tss`) は読まない。** そのため `Button` や `ScrollView` の既定スタイルは付かない。必要な最小限の指定は `Components.uss` の Base 節にある (UIDocument のルートを画面いっぱいに広げる指定、ScrollView の伸縮)。`TextField` など、まだ使っていない組み込み要素を使うときは、同じ Base 節にスタイルを足す。

## トークン

### 色

| トークン | 値 | 用途 |
|---|---|---|
| `--color-primary` | `#1F8BEA` | 主要ボタン、アクティブなタブ、氷のメーター |
| `--color-primary-dark` | `#1565C0` | primary の押下・ホバー |
| `--color-ice-50` / `-100` / `-200` | `#EEF7FF` / `#D8EDFC` / `#B5DBF7` | 淡い背景、メーターの未達部分、枠線 |
| `--color-eco` / `--color-eco-soft` | `#2EB872` / `#DDF5E8` | CO₂ 削減、良い変化 (+3% など) |
| `--color-accent` / `-dark` | `#FFC928` / `#E0A800` | 「すみかに反映」など、1 画面に 1 つだけ置く強調ボタン |
| `--color-point` | `#F5A623` | ポイント・報酬 |
| `--color-danger` / `-soft` | `#E5534B` / `#FCE3E1` | 負荷が高い、氷が減る |
| `--color-text` | `#17385F` | 本文 |
| `--color-text-sub` | `#6B8199` | 補足、非アクティブのタブ |
| `--color-surface` / `-glass` | 白 95% / 白 80% | カード / ワールドの上に重ねる半透明のカード |
| `--color-divider` | `#E3EEF7` | 区切り線 |
| `--color-elevation` | 紺 12% | `.pp-elevated` の擬似的な影 |
| `--color-camera-bg` | `#0E1A26` | カメラ画面の背景 |
| `--color-on-dark-button` / `-hover` | 白 18% / 白 30% | 暗い背景の上に置くボタン |
| `--color-scrim` | 背景色 55% | 暗い背景の上に文字を置くときの下敷き |

### 余白・角丸・サイズ

| 種類 | トークン |
|---|---|
| 余白 | `--space-1` 8 / `-2` 16 / `-3` 24 / `-4` 32 / `-5` 40 / `-6` 48 / `-7` 64 / `-8` 96 (px) |
| 角丸 | `--radius-sm` 16 / `--radius-md` 28 (カード) / `--radius-lg` 44 (吹き出し・タブバー) / `--radius-full` 999 (**正方形の要素専用**) |
| ピル型部品 | `--control-height-sm` 48 + `--radius-pill-sm` 24、`-md` 72 + 36、`-lg` 112 + 56 |
| アイコン | `--icon-sm` 40 / `--icon-md` 56 / `--icon-lg` 80 / `--icon-xl` 112 |

UI Toolkit は、角丸が短辺の半分を超えると角が楕円に潰れる (CSS のように円に丸めない)。ピル型の部品は高さを固定し、半分の値の角丸を組にして使う。

### 文字

| トークン | px | 用途 |
|---|---|---|
| `--font-size-caption` | 28 | 補足、タブのラベル、バッジ |
| `--font-size-body` | 34 | 本文 (`:root` の既定) |
| `--font-size-label` | 38 | ボタン |
| `--font-size-title` | 46 | セクション見出し |
| `--font-size-headline` | 60 | 画面タイトル |
| `--font-size-display` | 96 | CO₂ 量など、画面の主役になる数値 |

太さは `--font-regular` / `--font-bold` / `--font-heavy` の 3 種類。ユーティリティクラスは `.pp-text-{caption,body,label,title,headline,display}`、`.pp-text-{bold,heavy}`、`.pp-text-{sub,primary,eco,point,danger,inverse}`、`.pp-text-center`。

## フォントの差し替え

いま入っている **M PLUS Rounded 1c (OFL) は仮置き**。UI Toolkit は OS のフォントを代わりに使ってくれないため、日本語を表示するにはフォントをプロジェクトに同梱する必要がある。

差し替えの手順:

1. 新しい `.ttf` / `.otf` を `Assets/UI/Fonts/` に置く (`.gitattributes` で LFS の対象になっている)
2. `Tokens.uss` の `--font-regular` / `--font-bold` / `--font-heavy` の 3 行を、新しい `.ttf` に向ける
3. 古い `.ttf` と `OFL.txt` を消す (新しいフォントのライセンス文書を代わりに置く)

コンポーネント側はトークン経由でしか参照していないので、ほかのファイルは変更しなくてよい。

**FontAsset (`.asset`) は作らない。** トークンには `.ttf` を直接指定する。UI Toolkit は `.ttf` を渡されると、表示に使う FontAsset を実行時にメモリ上で作るので、プロジェクトのファイルは変わらない。一方、Dynamic の FontAsset をアセットとして置くと、Play や画面表示で使った文字のグリフがそのアセット自身に書き込まれ、開発者全員の `git status` に毎回差分が出る。アトラスの大きさなどを細かく調整したくなった場合も、アセットとして保存しない方法 (実行時に `FontAsset.CreateFontAsset` で作る等) を先に検討する。

## コンポーネント

名前は `.pp-<block>__<element>--<modifier>` の形にする。UXML の `name` 属性は camelCase にする。

| クラス | 使う場所 | 備考 |
|---|---|---|
| `.pp-card` (`--glass`) | 情報のまとまり | `.pp-elevated` と組み合わせると下辺に影が付く |
| `.pp-icon` + `--{sm,lg,xl}` + `--{primary,eco,point,sub,inverse,original}` + `--<name>` | アイコン | 白い SVG に tint で色を付ける。多色の SVG には `--original` を使う |
| `.pp-icon-badge` (`--eco`) | アイコンを淡い円で囲む | |
| `.pp-icon-button` | 歯車など、円形のアイコンボタン | `ui:Button` の子に `.pp-icon` を入れる |
| `.pp-btn` + `--{accent,ghost,block}` | 通常のボタン | accent は 1 画面に 1 つまで |
| `.pp-badge` (`--{eco,accent,danger}`) / `.pp-chip` | カテゴリ、「Good!」、食材のタグ | |
| `.pp-progress` (`--{eco,point}`) | `ui:ProgressBar` | 値は UXML の `value` 属性か C# の `value` で渡す。タイトル表示は隠している |
| `.pp-stat-card` | 氷の量 / CO₂ 削減などの指標 | 構造は下の例を参照 |
| `.pp-speech` + `.pp-avatar` | ペンギンの吹き出し | DOM 上は吹き出し → アバターの順に置く (`row-reverse` で、アバターを左側・前面に描くため) |
| `.pp-segmented` / `__item--active` | デイリー / ウィークリーの切り替え | |
| `.pp-list-item` (`--last`) | 解析結果の品目行 | UI Toolkit には `:last-child` が無いので、最後の行に `--last` を付ける |
| `.pp-tab-bar` / `.pp-tab` (`--active`) / `.pp-tab__fab` | 下部ナビ | 最後の子に `.pp-safe-area__bottom` を置くと、ジェスチャーバー分の余白が入る |
| `.pp-icon-button--dark` | カメラ画面の閉じるボタンなど | 暗い背景用の `.pp-icon-button` |
| `.pp-scan-frame` + `__corner--{top-left,top-right,bottom-left,bottom-right}` | 撮影枠 | 四隅の L 字だけを描き、中は透かす |
| `.pp-shutter` / `__core` | シャッターボタン | |
| `.pp-screen` (`--hidden`) / `.pp-hidden` | 画面の切り替え / 要素の非表示 | 下の「画面の切り替え」を参照 |

### 例: 指標カード

```xml
<ui:VisualElement class="pp-card pp-elevated pp-stat-card">
    <ui:VisualElement class="pp-icon-badge">
        <ui:VisualElement class="pp-icon pp-icon--snowflake pp-icon--primary" />
    </ui:VisualElement>
    <ui:VisualElement class="pp-stat-card__body">
        <ui:Label text="氷の量" class="pp-stat-card__label" />
        <ui:VisualElement class="pp-stat-card__meter">
            <ui:ProgressBar name="iceProgress" value="72" class="pp-progress" />
            <ui:Label name="iceValue" text="72%" class="pp-stat-card__value pp-text-primary" />
        </ui:VisualElement>
    </ui:VisualElement>
</ui:VisualElement>
```

## アイコンを追加する

1. `viewBox="0 0 24 24"` で、塗りと線を `#FFFFFF` にした SVG を `Icons/` に置く (色は USS の tint で付ける)
2. `Components.uss` に `.pp-icon--<name> { background-image: url("project://database/Assets/UI/DesignSystem/Icons/<name>.svg"); }` を追加する
3. カタログの Icon 節に並べる

## 3D ワールドの上に UI を重ねる

- PanelSettings の Clear Color はオフにしてある。UI の後ろには 3D カメラの描画がそのまま見える。
- ワールドを見せる領域と、その親の要素には `picking-mode="Ignore"` を付ける。付けないと、タッチが UI に吸われてワールドに届かない (例: `HomeScreen.uxml` の `worldViewport`)。
- 画面の端に置く UI は `.pp-safe-area` を付けた要素の子にする。`SafeAreaApplier` が、このクラスを持つ全要素に上・左・右の余白を入れ、`.pp-safe-area__bottom` を持つ全要素の高さを下端の余白に合わせる。

## 画面の切り替え

シーンは分けず、`App.uxml` に全画面を `<ui:Instance>` で並べておき、表示中の 1 つ以外に `.pp-screen--hidden` (`display: none`) を付ける。隠した画面は破棄されないので、戻ったときに状態が残る。

- 切り替えは `ScreenNavigator.Show(AppScreen)` を呼ぶ。ホームの `tabScan` でスキャン画面へ、スキャン画面の `closeButton` と Android の戻るキー (Input System では Escape キーとして届く) でホームへ戻る。
- スキャン画面の表示中は 3D ワールドのカメラを止め、カメラ映像は `ReceiptCameraPreview` がスキャン画面を開いている間だけ動かす。アプリが裏に回ったときも止める。
- 画面を足すときは、`Screens/<Screen>/` に UXML を作って `App.uxml` に `<ui:Template>` と `<ui:Instance class="pp-screen pp-screen--hidden">` を追加し、`AppScreen` と `ScreenNavigator` に分岐を足す。
- カメラ映像は表示するだけで、フレームの保存もログ出力もしない。撮影処理を足すときは `.claude/rules/privacy.md` に従い、メモリ上だけで扱う。

## USS で使えない CSS

`gap`、`box-shadow`、`z-index`、`linear-gradient()`、`:nth-child` / `:first-child` / `:last-child`、属性セレクタ、`border` の一括指定は使えない。代わりに子要素の margin、`.pp-elevated`、DOM の順序、明示的な修飾クラスを使う。`transition-property` は指定せず、`transition-duration` だけを基底クラスに書く。UXML に `style="..."` を書かない。

## 試作画面

`Assets/Scenes/UITest.unity` の `AppUI` が `App.uxml` を表示し、ホーム画面は仮置きの 3D ワールド (`World`) の上に重なる。3D の要素は Capsule / Quad / Cylinder / Cube の仮モデルで、マテリアルは `Assets/Prototype/UITest/Materials/` にある。表示している値 (72% など) は固定のモックで、ゲームの状態とはまだつながっていない。スキャン画面のシャッターは見た目だけで、撮影処理はまだつないでいない。
