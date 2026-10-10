# 生産の島 素材パック v001

依頼書 `docs/asset-requests/production-island-assets.md` に沿った初版。制作ブランチは `codex/production-island-assets`。依頼書自体は Git の対象から除外している。

## 納品

| 種類 | 内容 | 場所 |
|---|---|---|
| 地形 | 氷・ひび・沈みかけ・海・水路・岸・良質マスの印、15モデル | `Assets/3Dmodel/Tile_*`, `Shore_*`, `Marker_*` |
| 建物 | 漁場から仕分け所まで14モデル、港の6段階 | `Assets/3Dmodel/Building_*`, `Harbor_Stage*` |
| 小物 | 真珠・魚・すり身・塩・海藻・かまぼこ・ちくわ・干物・おでん、9モデル | `Assets/3Dmodel/Item_*` |
| 接続 | 矢印2モデル、入口／出口×3状態、5状態の線Prefab | `Assets/3Dmodel/Link_*`, `Assets/ProductionIsland/Prefabs` |
| ペンギン | CarryWalk / WorkLoop / Idle / Cheer、4クリップとAnimator | `Assets/3Dmodel/Penguin_Production_v001`, `Assets/ProductionIsland/Animations` |
| UI | 白一色、24×24の34 SVG。人数アイコンは既存penguin.svgを流用 | `Assets/UI/DesignSystem/Icons/icon-*.svg` |
| VFX | +1、雪煙2サイズ、接続光、紙吹雪、氷の沈み、真珠の輪、7Prefab | `Assets/VFX/ProductionIsland` |
| 編集元 | モデルごとの.blendと生成スクリプト | `ArtSource/<名前>_v001`, `ArtSource/ProductionIsland_v001` |
| 見本 | 全モデルを並べた新規シーン | `Assets/Scenes/ProductionIslandAssetCatalog.unity` |

全52モデル＋ペンギン1モデルに、Unity生成の`.meta`を付けている。既存のモデル・ゲームシーンは変更していない。

## 取り込みと使い方

生成済みPrefabをシーンに置く。再生成が必要な場合は、Unityの **Production Island > Build Asset Pack** を実行する。`.mat`、`.prefab`、`.controller`、`.unity`、`.meta`はEditor APIで生成しており、YAMLを手書きしていない。

- 1マス=1m。1×1建物は0.9m以内、2×2建物は1.9m以内。足元中心が原点、Y=0が地面、正面は-Z。
- 建物の稼働状態は `ProductionIslandMotion.SetRunning(bool)`。動く部品の名前は `_Anim`。停止中は専用の低彩度アトラスを使用する。ちくわ工場の炎は `SetHighHeat(bool)` で切り替える。
- 線は `ProductionIslandLink.SetPath(Vector3[])` でワールド座標を指定する。`SetState` で5状態を切り替える。`SetFlow(Color, float)` は品目色と毎秒の流量を受け取り、粒の数・間隔・速度を変える。入口／出口ポートは建物の辺に別Prefabとして付ける。
- ペンギンは `ProductionIslandPenguinView.SetActivity(Activity)` で動作を切り替える。`CarrySocket` に付ける小物はサンプルの魚から差し替えられる。歩行はその場で動き、経路移動を含まない。
- +1のVFXには差し替え用の魚アイコンを付けている。生成した品目に合わせて小物を差し替える。紙吹雪にも魚メッシュが混ざる。
- 稼働中の湯気、宿舎の煙、港の発光マテリアル、接続口の点滅をPrefabに含める。

## ペンギンの互換性

元の `Penguin_v001/Penguin_Waddle_1p3m.fbx` はボーンを使わず、親Transformと足のブレンドシェイプで歩くモデルだった。その親子階層と足のキーを維持し、ヒレと頭のキーを追加した。新しいボーンリグへの置き換えではない。

v002は静止モデルなので、今回のクリップのみをv002に割り当てても動かない。今回の `Penguin_Production_v001.prefab` を使う。元FBXと元テクスチャは変更していない。

## 制作しないものと実装範囲

依頼書で条件付きのそり道・そり乗り（B-16 / P-05）は、有向の線へ移る前提で作っていない。任意の効果音は今回に含めていない。おすそわけ箱と独立した飾りも作っていない。港の完成段階に必要な灯り・のぼりは港モデルに含める。

これは素材パック。10×10盤面、建設、資源消費、配属、接続の操作、研究、納品判定、生産量タブの画面と計算などのゲーム実装は含めない。

## 再制作

Blender 4.3.2で次のスクリプトを実行する。モデル生成は元の既存素材を上書きしない。Unityに取り込んだ後、Build Asset Packを実行する。

```powershell
blender --background --python ArtSource/ProductionIsland_v001/generate_models.py
blender --background --python ArtSource/ProductionIsland_v001/generate_penguin.py
python ArtSource/ProductionIsland_v001/generate_icons.py
```

`generate_models.py -- --skip-render` はFBXと.blendのみ、`-- --render-only` は一覧画像のみ作る。制作環境の `.local-tools/` はGit対象外。

## 検証

- Blender側で床200三角形、1×1建物1,500三角形、2×2建物3,000三角形の上限と足元サイズを検査。
- Unity 6000.6.0f1のEditorでコンパイル、Prefab・マテリアル参照、シェーダー、-Zの正面方向、4クリップの長さとカーブを検査。
- モデル・ペンギンのレンダーとSVGの一覧を `ArtSource/ProductionIsland_v001/` に保存。
- 実機での描画性能、ゲームへの組み込み、アートの最終調整は未検証。
