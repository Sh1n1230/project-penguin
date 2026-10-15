# かまぼこ工場 v002：施設の識別と加工の見える化

2026-10-08。まず、目視確認中のかまぼこ工場を新しい共通方針に合わせて制作した。

## デザイン

屋根そのものを、板に載った大きな半円形のかまぼこにする。外側はピンク、断面は白。正面には壁を置かず、青い魚の投入台、中央の蒸し器、ピンクの完成品受け台を左から右へ並べる。小さな魚の看板も投入側に付ける。文字を読まなくても完成品と加工設備がわかる構成。

## 表示工程

7.5秒のループで次の動作を見せる。

| 時間 | 表示 |
|---|---|
| 0〜1.3秒 | ふたが開いた蒸し器へ、左の台の魚が移動 |
| 1.3〜2秒 | 魚が蒸し器の中へ下がり、ふたが閉まる |
| 2〜4.3秒 | 魚が隠れ、白い蒸気が上昇 |
| 4.3〜4.9秒 | ふたが開き、ピンク・白のかまぼこが現れる |
| 4.9〜6.3秒 | 完成品が右の受け台へ移動 |
| 6.3〜7.5秒 | 完成品を見せてから、次のサイクルへ戻る |

`KamabokoProductionCycle.SetRunning(false)` で工程をその姿勢のまま止め、`true` で続きから再開する。`RestartCycle()` で投入からやり直す。FBXの軸・スケールを考慮し、上下動をUnity世界座標のメートルへ変換している。

## 作業するペンギン

ユーザー指定に合わせて、既存の `Assets/3Dmodel/Penguin_v002/Penguin_Static_v002.fbx` を使用する。体・目・くちばし・ヒレ・足の10メッシュと元のマテリアルを参照し、料理帽を追加した。工場用に新造した `Penguin_Production_v001` はこの工場では使用しない。

`KamabokoPenguinWorker` が工程時刻に合わせて、魚の運搬と投入、木製ハンドルによるふた操作、蒸し中の見守り、完成品の運搬、喜ぶ動作と投入側への戻りを表示する。既存モデルは静止素材なので、肩と足元に回転用の親Transformを追加し、ヒレの回転と小さな足踏みで動かす。帽子も体の上下動に追従する。姿勢の時刻は工場と共通で、停止・再開始も同期する。

これは生産工程の表示素材。魚を直接投入してかまぼこが出るというユーザー指定のわかりやすさを優先している。生産計算・在庫・レシピシステムへの接続は含まない。

## 参考イメージ

- [いらすとや：赤いかまぼこのイラスト](https://www.irasutoya.com/2015/05/blog-post_0.html)：板に載せた半円の形と、ピンク・白の配色を参考にした。
- [Roman Nabokin：Township production buildings](https://www.behance.net/gallery/32621255/Township-%28social-game%29)：商品や加工設備を大きな目印にして施設の用途を伝える見せ方を参考にした。

画像自体は素材へ取り込まず、Blenderで形状と配色を新規制作した。

## ファイルと再生成

- Prefab：`Assets/3Dmodel/Building_Kamaboko_2x2_v002/Building_Kamaboko_2x2_v002.prefab`
- FBX、アトラス、Unity材質：上記と同じフォルダ。
- 編集用Blender：`ArtSource/Building_Kamaboko_2x2_v002/Building_Kamaboko_2x2_v002.blend`
- 生成コード：`ArtSource/ProductionIsland_v002/generate_kamaboko.py`。v001のプリミティブと出力関数だけを再利用する。
- Unity生成コード：`Assets/Editor/ProductionIsland/KamabokoRevisionBuilder.cs` の `Build()`。
- 確認シーン：`Assets/Scenes/KamabokoDesignReview.unity`。

Blenderの生成コードを実行後、Unityの `Production Island > Build Kamaboko Design Revision` を実行する。確認シーンを開いている場合は別の保存済みシーンへ切り替えてから再生成する。v001は比較用に残している。

## 検証

Unity通常Play Modeで、6工程を異なるフレームで観測・撮影した。工程順、魚と完成品の表示切替、移動範囲、停止時の姿勢維持、再開始を検証する。数値証拠は [motion-verification.json](../ArtSource/ProductionIsland_v002/Review/motion-verification.json)。再撮影はレビューシーンのPlay Modeで `KamabokoRevisionBuilder.StartCapture()` をMCPから呼ぶ。背景での再生時は `Application.runInBackground` の元値を保存して一時的に有効にする。

既存ペンギンへ差し替え後の実測はframe320→679。6工程、表示の順序、世界座標での移動範囲、停止、再開始、作業役の工程同期、作業役の停止同期の7判定がPASS。運搬時のCarrySocketと魚・完成品の距離は各0.01m。6枚を再撮影し、投入・蒸し・運搬の画像を目視確認した。MCPで作業役の10メッシュすべてが既存v002 FBXを参照することを確認し、Consoleのエラー・警告は0件。確認のためGame画面は再生したままにしている。ペンギン追加前の証拠は `ArtSource/ProductionIsland_v002/Review/WithoutWorker/` に保存している。

- [投入](../ArtSource/ProductionIsland_v002/Review/0-Loading.png)
- [ふたを閉める](../ArtSource/ProductionIsland_v002/Review/1-Closing.png)
- [蒸す](../ArtSource/ProductionIsland_v002/Review/2-Steaming.png)
- [完成品が現れる](../ArtSource/ProductionIsland_v002/Review/3-Opening.png)
- [取り出す](../ArtSource/ProductionIsland_v002/Review/4-Output.png)
- [完成](../ArtSource/ProductionIsland_v002/Review/5-Finished.png)

三角形数2206、土台1.86×1.86m、静的モデル高さ1.69m。見た目の好みと用途の伝わりやすさの最終判断はユーザーによる確認待ち。
