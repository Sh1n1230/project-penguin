# 生産の島素材：LLMによる動きテスト仕様

作成日：2026-10-07。対象は素材パック v001 の表示動作。ゲームの生産計算、経路移動、実機性能は対象外。

本書は期待値と実行手順を定義する仕様書。ソースから得た期待値と実測を区別する。実際のMCP接続・Play Modeサンプリング・後始末は [`production-island-motion-test-results.md`](production-island-motion-test-results.md) を参照。素材一覧は [`../production-island-asset-pack.md`](../production-island-asset-pack.md) を参照。

## 判定と証拠の共通規則

- 結果は `PASS` / `FAIL` / `BLOCKED` / `NOT_RUN`。期待値を測定できた場合のみPASSとする。接続失敗や証拠不足をPASSにしない。
- ID、対象Prefab/実行時階層、操作、Unity時刻またはframeCount、実測値、期待値、判定理由、証拠ファイルを残す。複数Prefabは子IDを付け、未実施を隠さない。
- 「動く」は異なるPlay Modeフレームの位置・回転・スケール・BlendShape・Animator状態等の比較と、可能な場合は同じ視点の連続画像で判定する。静止画像1枚やクリップの存在だけで動作合格にしない。
- 操作直後のAnimator状態はまだ更新されない場合があるため、最低1フレーム進めてから確認する。Editor停止中の値からUpdateの実行を推測しない。
- Transform位置の許容差は0.002m、線幅は0.001m、色/alphaは0.02を目安とする。時間差には実測deltaTimeを使い、外部ツールの待機秒数だけで期待値を計算しない。
- 見た目（炎の違い、低彩度、矢印向き、文字の読める状態）は画面証拠も必要。数値のみ確認できた項目は「数値PASS／視覚NOT_RUN」と分ける。画面が取れない場合、素材全体の視覚合格とは書かない。
- 操作前後のConsoleを比較し、今回発生した例外・Missing参照・シェーダーエラーはIDへ紐付ける。既存ログは消去せず区別する。

## 再実行手順と接続ゲート

1. `CLAUDE.md` と適用される `AGENTS.md`、実際に利用するUnity MCP/Unity CLIのスキルを読む。`.unity` / `.prefab` / `.asset` / `.meta`をテキスト編集しない。
2. 利用可能なMCPツールを発見し、接続中Editorのプロジェクト絶対パス、Unityバージョン、アクティブシーン、Play/Pause/コンパイル状態を読み取りで確認する。`.mcp.json` に設定があるだけでは接続成功としない。親または実行担当が実在するツール名と応答、CLIを併用した場合は正確なコマンドを結果書へ記録する。本書は未確認のツール名や接続コマンドを定義しない。
3. プロジェクトが `このリポジトリのルート`、バージョンが `ProjectSettings/ProjectVersion.txt` と一致することを確認する。別Editorなら操作を止めBLOCKED。コンパイル中は完了を待つ。
4. コンパイルエラー、必要Prefab・コンポーネント・Animator・マテリアルの欠落を検査する。欠落は原因を記録し該当IDをBLOCKEDとする。テストのためにBuild Asset Packを無断再生成しない。
5. 下の保存・復元手順を実施し、隔離した一時テスト環境を用意する。生成済みPrefabからEditor APIでインスタンス化し、Play Modeで公開APIを呼ぶ。MCPで必要なC#実行ができない場合は実在するCLI接続を確認して補助し、MCPの接続結果自体も記録する。
6. 全IDを実施する。時間サンプルはコルーチン等のフレームをまたぐ観測か、時刻付き複数回の読み取りを使う。同期C#内のループやSleepではUnityのUpdateは進まない。
7. 証拠を結果書へ保存してから後始末し、復元結果と未解決事項を記録する。

### 今回追加したサンプリングコードの再実行

`Assets/Editor/ProductionIsland/ProductionIslandMotionTestRunner.cs` の `Start()` は実測を ローカルの `.local-tools/production-island-motion-results.json` と `.md` に出力する。実行前に前回結果を別名へ保存する。

全シーンが保存済みで、Prefab Modeを開いておらず、Editorが停止中の場合に限り、シーンsetup・選択・timeScaleを記録し、Editor APIでCameraとDirectional Lightのある一時シーンへ単独切替する。元のゲームシーンを開いたままPlayに入らない。Play開始・コンパイル完了後、MCP `execute_code` から `Start()` を呼び、`.running` が消えてJSONが更新されるまで待つ。Play中は実際のUnity Update/Animatorを観測し、手動Update呼出は行わない。実行後はPlayを止め、一時シーンを保存せず元のシーンsetupを復元する。未保存変更がある場合は単独切替を行わず、Preview検査の結果と通常Play Mode未実施を区別する。

このコードは数値検査を行う。以下の全受入条件を自動で網羅するわけではなく、画像による見た目の検査や動作則の定量比較は結果書の未実施範囲を確認して補完する。

背面Editorでは `Application.runInBackground=False` によりPlayerLoopが停止する場合がある。開始直後にframeCount/Time.timeが進むことを確認する。必要なら元値を保存してテスト中だけTrueに変更し、終了時に復元する。停止中に取得した動作判定は退避し、進行復旧後に最初から再実行する。

### 実行前状態の保存と後始末

- 最初にgit差分一覧、開いているシーンのパス/順序/active/dirty、Prefab Mode、選択、Play/Pause、timeScale、テストが変更するカメラ設定を記録する。個人情報を含むゲーム入力は使用しない。
- 既存シーンがdirtyなら閉じたり保存したりしない。一時シーンをAdditiveに開いて検査するなど、変更を保護できる経路を選ぶ。最初からPlay中の場合も元の状態を勝手に停止せず、隔離方法が成立しなければBLOCKEDとして理由を書く。
- テスト用GameObject・カメラ・補助コンポーネントは専用ルートにまとめる。共有マテリアル資産を変更せず、必要な変更はインスタンスのMaterialPropertyBlockまたは複製に行う。SetStateのsharedMaterial代入は参照切替であり資産の色を書き換える操作とは異なる。
- テスト終了時は開始したPlay Modeを終了し、一時ルート/シーン/補助生成物だけを除去する。既存シーンを保存しない。activeシーン、選択、timeScale、カメラ等を復元し、git差分を開始時と比較する。以前からある変更を巻き戻さない。シーンや資産の削除はEditor API経由で行う。
- 復元不能・新規差分・残留オブジェクトがあれば結果書に対象と理由を残す。テスト用ソースを作成した場合は作成/削除の両方を記録する。

## テストケース

### 接続・準備

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| ENV-01 | MCPでEditor情報を取得 | 対象プロジェクト・バージョン・状態を確認できる | ツール名、日時、応答、パス、バージョン |
| ENV-02 | Prefabを読み取り、隔離環境にインスタンス化 | Motion/Link/PenguinView/PortPulse/Burst参照が有効。コンパイル成功 | 資産/参照一覧、Console差分 |
| ENV-03 | Play Modeで2回以上frameCount/Time.timeを観測 | フレームと時刻が進行し、Pause解除・timeScale>0 | フレームと時刻のサンプル |

### 建物の稼働・停止・再開

対象は `Assets/3Dmodel/Building_*/*.prefab` 相当の全14建物と `Harbor_Stage0`〜`Harbor_Stage5` の計20Prefab（実際のパスを列挙する）。`_Anim`部品や粒子がない建物に存在しない動きを要求せず、部品数・粒子数も報告する。

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| BLD-01 | 各対象で `SetRunning(true)`、0.2〜0.5秒間隔で3サンプル | `_Anim`のTransformが名前の動作則に従って変化。保持していた元マテリアル参照を使用。対象粒子は再生 | 部品名とTransform、材質参照、粒子isPlaying/isEmitting、画像対 |
| BLD-02 | 動作中に `SetRunning(false)`、直後と0.3秒後 | 部品Transformが停止時の値で固定。ParticleSystemRenderer以外の材質スロットはStopped材質。炎2種は非active。粒子は新規放出を停止 | 固定値の比較、材質全スロット、炎active、粒子状態、停止画像 |
| BLD-03 | BLD-02後 `SetRunning(true)`、複数フレーム観測 | 部品が再び変化し、各Rendererの元の材質スロットを復元。粒子再生、選択熱量の炎のみ復帰 | 停止/復帰値、材質参照比較、画像対 |

動作則：RotorはZ軸90度/秒、WaterwheelはX軸90度/秒、Grill/SortingPlateはY軸65度/秒。Knife/Net/Lidは基準位置からY=0〜0.08mの上下動、DoorはY軸±12度、Flameはスケール1±0.08、その他はZ軸±4度。振動位相は3rad/秒。停止で位相・姿勢を初期化しない。角度はQuaternion差で比較し360度境界を考慮する。粒子停止は `StopEmitting` のため、既存粒子が寿命まで残ることは正常。即時消滅を要求しない。

### ちくわ工場の炎2種

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| HEAT-01 | Chikuwaでrunning=true、`SetHighHeat(false)` | FlameLow*のみactive、FlameHigh*非active。低炎が脈動 | 両炎の階層/active/scale、低炎画像対 |
| HEAT-02 | `SetHighHeat(true)` | FlameHigh*のみactive、FlameLow*非active。高炎が脈動し低炎との差が見える | 両炎の値、高炎画像対 |
| HEAT-03 | highHeat=trueのまま停止→熱量falseへ変更→再開 | 停止中は両炎非active、再開後はLowのみactive。trueに戻すとHighへ切替 | 操作順、各段階active、画像 |

### 入口・出口ポート

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| PORT-01 | Input/Output Selectableを1.2秒以上観測 | 各RendererのPropertyBlock `_BaseColor` RGBが `0.65+0.35*sin(Time.time*6)` に従い約0.30〜1.00で点滅、alpha=1 | 6点以上の時刻/色、明暗画像対 |
| PORT-02 | 同じInput/OutputのFree/Connectedを比較 | SelectableだけPortPulseあり。Free/Connectedは同じ明暗パルスが発生しない | 6PrefabのComponentと色/画像比較 |

周期は約1.047秒。たまたま同じ位相の2点だけで静止と判定しない。

### 線の5状態・流量・色・方向

対象：`Assets/ProductionIsland/Prefabs/Link_{Normal,Flowing,Blocked,Selected,Drawing}.prefab`。世界座標の折れ線を `SetPath(new[] { (0,.16,0), (1,.16,0), (1,.16,1) })` 相当で設定（長さ2m）。Prefab初期状態と1インスタンス上の切替を両方確認する。

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| LINK-01 | 各5状態で `SetState` | enumに対応する材質が線と矢印へ設定。Selected幅0.12m、他0.08m。Flowingのみ粒がactive。Normal通常線、Blocked赤、Selected淡青太線、Drawing破線、Flowing脈動と粒移動 | 5状態の材質/幅/active、各画像、Flowing連続画像 |
| LINK-02 | 赤で `SetFlow(Color.red, .5f)` | Flowing、粒1個、速度0.075m/秒、PropertyBlock色=赤。経路に沿い始点から終点へ進む | 粒数、色、時刻/粒位置、画像対 |
| LINK-03 | 緑で `SetFlow(Color.green, 2f)` | Flowing、粒4個、速度0.30m/秒。間隔=経路長/4。色が緑へ変更 | 粒数/色、経路距離/時間、画像対 |
| LINK-04 | 青で `SetFlow(Color.blue, 10f)` | 粒数はPrefab容量6で上限、速度1.50m/秒。間隔=経路長/6。LINK-02/03より密で速い | 6粒、色、速度、画像対 |
| LINK-05 | `SetFlow(Color.red, 0f)`、続けて負値 | Normalへ切替、active粒0、速度0。負値でも流れず例外なし | 状態/粒数/速度、Console差分 |
| LINK-06 | 非対称折れ線を反転して `SetPath` | 矢印が最終点に置かれ、矢印モデルの先端が最終区間の進行方向を向く。粒の進行も反転。角で線外へ飛ばず終点で始点へ周回 | 頂点/矢印位置・向き、正逆の連続画像と粒位置 |
| LINK-07 | Flowing→Blocked→Selected→Drawing→Normal→Flowing | 切替直後から粒のactiveと幅/材質が状態に一致。Flowing復帰後は移動再開 | 遷移ごとの値、復帰位置差 |

`SetFlow`は正値でFlowing、0以下でNormalを自動設定する。BlockedやSelectedの確認後にSetFlowを呼ぶと状態が変わるため、5状態の証拠採取時は混同しない。SetFlowの品目色は粒のみへ適用し、線/矢印の状態色まで変更する期待値にしない。速度判定は折れ線上の弧長の差で行い、末端のwrapを補正する。矢印のTransformは `Quaternion.LookRotation(-direction, Vector3.up)` を使うが、モデル正面は-Zなので画面上の先端で向きを検証する。

### ペンギン4動作とcarry表示

対象：`Assets/3Dmodel/Penguin_Production_v001/Penguin_Production_v001.prefab`。v002へクリップを付ける試験ではない。観測は少なくとも各クリップ1周期、Cheerは終端後も含む。クリップ長を実測し、定数の待機秒だけに依存しない。

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| PEN-01 | `SetActivity(CarryWalk)` | AnimatorがCarryWalk、足/胴体が歩行、CarrySocketの魚がactive。ループしても表示維持。ルートは経路移動しない | 状態/normalizedTime、Transform/BlendShape、魚active、連続画像 |
| PEN-02 | `SetActivity(WorkLoop)` | WorkLoop、作業のヒレ/胴体が繰返し変化、魚非active | 状態/時間、変形値、連続画像 |
| PEN-03 | `SetActivity(Idle)` | Idle、頭の傾き/小さな呼吸変形が繰返し変化、魚非active | 状態/時間、変形値、連続画像 |
| PEN-04 | `SetActivity(Cheer)` | Cheer、ヒレを上げ跳ねる一回動作、魚非active。終端でループしない。同じAPIを再度呼ぶと先頭から再生 | 終端を含む状態/時間/変形、連続画像、再呼出後値 |
| PEN-05 | CarryWalk→WorkLoop→CarryWalk→Idle→Cheer→CarryWalk | 各遷移の更新後、魚はCarryWalkのときだけactive。CarrySocketへ付いている | 全遷移のAnimator状態/魚active、親Transform |

### +1と氷沈みVFX・再有効化

対象：`Assets/VFX/ProductionIsland/Prefabs/ProductionPlusOne.prefab` と `IceMelt.prefab`。インスタンス化済みPrefabを使い、Awake前の未設定状態でConfigureする即席オブジェクトと混同しない。時刻0、約0.3秒、0.6秒、1.2秒超を実測する。

| ID | 入力/操作 | 観測と期待値 | 必須証拠 |
|---|---|---|---|
| VFX-01 | ProductionPlusOneを初回有効化 | FloatingRewardが基準位置からY+0.4mへ約1.2秒で上昇。文字「+1」と魚が表示され、alphaが1→0へ減少しvisualが非active | localPosition/alpha/activeの時系列、開始/途中/終了画像 |
| VFX-02 | VFX-01完了後、ルートをfalse→true | visualの位置/activeが復元、文字が開始時から読め、初回と同じ上昇・フェードを再実行。粒子も再開 | 再有効化直後と1フレーム後のalpha、位置/active、画像対、粒子状態 |
| VFX-03 | IceMeltを初回有効化 | 氷visualが基準位置からY-0.35mへ約1.2秒で沈み非active。氷片粒子が発生 | localPosition/active時系列、粒子状態、連続画像 |
| VFX-04 | VFX-03完了後、ルートをfalse→true | 氷が基準位置・activeへ復元し再度沈む。粒子も再開 | 復元/中間/終了値と画像、粒子状態 |
| VFX-05 | 両VFXを途中（約0.4秒）でfalse→true | 中間位置からではなく基準位置から再開始。+1文字のopacityも初回同様。二度目完了後visual非active | 中断前/直後/次フレーム/終了の値と画像 |

VFX再有効化の開始alpha=1は利用者から見た再生契約として検証する。現ソースのOnEnableは位置・active・時間を戻すがTextMesh.colorは戻していないため、開始時に前回のalphaが残る可能性がある。これは**ソース上の懸念であり実測FAILではない**。直後の値と次フレームの値を分け、初期透明/途中alpha残留が実際に見えるかを記録する。親ルートを再有効化せずvisual子だけをtrueにする操作はBurstのタイマーをリセットしないので、再生操作と見なさない。

2026-10-07追記：初回Preview数値検査で再有効化直後alpha=0を確認した（初回Preview検査の `BURST_ALPHA_RESET:ProductionPlusOne`）。`ProductionIslandBurst.OnEnable` にalpha=1の復元を追加した。上の懸念は修正前の根拠として残し、修正後の通常Play Mode再試験は結果書に記録する。

## 完了条件と結果書の必須項目

全IDと対象Prefabの子IDが判定され、未実施範囲が列挙され、証拠リンクがあり、後始末を検証した時点で実行報告を完成とする。FAIL/BLOCKEDがあっても報告は完成できるが、素材の動作合格とは区別する。

結果書には実行日時、実行者（LLM）、接続方法/実応答、Unityバージョン/プロジェクト/シーン、開始時状態、実行したC#または操作履歴、ID別期待値と実測、画像/数値証拠、Console差分、制約、復元状態、修正提案を含める。修正した場合は修正前と再試験結果を別に残す。

仕様の根拠：`Assets/Scripts/Presentation/World/ProductionIslandMotion.cs`、`ProductionIslandPortPulse.cs`、`ProductionIslandLink.cs`、`ProductionIslandPenguinView.cs`、`ProductionIslandBurst.cs`、`Assets/Editor/ProductionIsland/ProductionIslandAssetBuilder.cs`、`Assets/Shaders/ProductionIslandLine.shader`、`ArtSource/ProductionIsland_v001/generate_penguin.py`。
