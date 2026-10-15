# 生産の島 (ペンギン村)

ペンギンが施設で食べ物を作る「生産の島」の素材と確認シーンの文書。Web 試作 `penguin-village` で試した遊びを Unity に持ってきたもので、**MVP のホーム (`HomeWorld.unity`) にはまだ組み込まれていない。** 確認用のシーンだけで動く。

| 文書 | 中身 |
|---|---|
| [production-island-review-user-guide.md](production-island-review-user-guide.md) | Unity で施設を確認する手順 (まずこれ) |
| [production-island-asset-pack.md](production-island-asset-pack.md) | 素材パック v001 (地形・建物・小物・接続・VFX) と使い方 |
| [production-island-facilities-v002.md](production-island-facilities-v002.md) | 施設 v002 の仕様 |
| [production-island-facility-motions.md](production-island-facility-motions.md) | 施設ごとの特徴と動き |
| [kamaboko-design-v002.md](kamaboko-design-v002.md) | かまぼこ工場の設計 |
| [production-island-v002/](production-island-v002/README.md) | v002 のファイル一覧と SHA-256 (`scripts/package_production_island_v002.py` が生成) |
| [testing/](testing/) | 動きのテスト仕様・結果と目視確認の記録 |

## 置き場所

| もの | 場所 |
|---|---|
| モデル (FBX・プレハブ) | `Assets/3Dmodel/{Building,Harbor,Item,Link,Marker,Shore,Tile}_*`、`Penguin_Production_v001` |
| 共有のアトラスとマテリアル | v001 は `Assets/3Dmodel/ProductionIsland_v001/`、v002 は `Assets/3Dmodel/ProductionIsland_v002/` |
| マテリアル・プレハブ・アニメーション | `Assets/ProductionIsland/` |
| VFX・シェーダー・確認用 UI | `Assets/VFX/ProductionIsland/`、`Assets/Shaders/ProductionIsland*.shader`、`Assets/UI/ProductionIslandReview/` |
| 確認シーン | `Assets/Scenes/ProductionIslandAssetCatalog.unity`・`ProductionIslandFacilityReview.unity`・`KamabokoDesignReview.unity` |
| 表示コード | `Assets/Scripts/Presentation/World/` (`Facility*`・`Kamaboko*`・`ProductionIsland*`・`WorkshopPenguin`) |
| 生成用の Editor ツール | `Assets/Editor/ProductionIsland/` |
| 編集元 (.blend・生成スクリプト・確認画像) | `ArtSource/` |
