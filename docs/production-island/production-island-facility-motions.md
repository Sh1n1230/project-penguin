# 施設ごとの特徴と動き

2026-10-08。屋根・のぼりで用途がわかり、原料が加工で完成品へ変わるという方針に、施設固有の道具・作業リズムを加えた。調査した動作を、既存Penguin_v002と簡略化した自作メッシュで表現する。秒数、回数、振幅はゲーム用の演出設計であり、実際の作業時間ではない。

## すぐに確認する

Unityで `Assets/Scenes/ProductionIslandFacilityReview.unity` を開き、Playを押す。Game画面の「施設を選ぶ」→施設名をクリックすると、21項目の好きな施設へ直接移動できる。港の各段階も選べる。小さな画面では一覧をスクロールする。「全体表示」で同時に動く施設を比較でき、「停止」「再開」で工程を止めたり続けたりできる。施設名の下には現在の作業を表示する。

## 調査とモデルへの反映

| 施設 | 参考にした特徴・一次資料 | モデルに反映した動き | 周期 |
|---|---|---|---|
| 漁場 | [水産庁：定置網の揚網](https://www.jfa.maff.go.jp/j/study/kenkyusidoka/teichi.html) | 水中で泳ぐ魚、間を挟む二度の網の引き上げ、ヒレを引き寄せる作業、水切り | 7秒 |
| さばき場 | [紀文：練りものができるまで](https://www.kibun.co.jp/knowledge/neri/basics/dekirumade/index.html)の魚肉加工・すり混ぜ | 包丁を三回刻む動きと、続くすり混ぜを別の道具で表現。青い魚→白いすり身 | 5.5秒 |
| ちくわ工場 | 同資料の棒に巻き付けて焼く工程 | 棒を横軸で回転、白い生地→焼き色、最後に仕上がりを確認 | 7.4秒 |
| かまぼこ工場 | 同資料の成形・蒸す工程。ユーザー確認済み | 魚→蓋の開閉・蒸気→ピンクと白のかまぼこ。既存v002の動きを継続 | 7.5秒 |
| 製塩所 | [西尾市・塩の体験館：塩づくり](https://www.aibajio.jp/about/method/)の蒸発・かき集める道具 | 青い水の面積・高さが減り、白い結晶へ変化。熊手を二度引いて山に寄せる | 8.8秒 |
| 干物場 | [東京書籍：水産加工の仕事](https://ashitane.edutown.jp/umikawa/worker/4/)の塩漬け・乾燥 | 掛ける→ペンギンが脇へ退いて待つ→風にゆっくり揺れる→乾き具合を確認。青→オレンジ | 10秒 |
| 海藻場 | [日本昆布協会：羅臼昆布漁](https://kombu.or.jp/column/5862)のかぎ竿「マッカ」をねじる採取 | かぎ竿が一回転しながら上がり、海藻を水面から持ち上げる。その後、ヒレを上げて束ねる | 6秒 |
| おでん屋台 | [紀文：おいしいおでんの作り方](https://www.kibun.co.jp/knowledge/oden/basics/howto/)の静かな弱火 | 最初と最後だけ軽く混ぜ、途中は待つ。蒸気がゆっくり上がり、最後におたまを持ち上げる | 9秒 |
| 倉庫 | [ダイフク：自動倉庫](https://www.daifuku.com/jp/solution/intralogistics/products/automated-warehouse/)のラックへの入出庫 | 扉の開閉に加え、トレーで箱を上の棚へ上げ、搬出時に下ろす | 4.5秒 |
| 仕分け所 | [ダイフク：仕分けシステム](https://www.daifuku.com/jp/solution/intralogistics/products/sort/)の行き先ごとの振り分け | 分岐板が左・中央・右へ切り替わる。魚も三方向へ順番に搬出する | 3秒 |
| 研究所 | [紀文：塩と熱を加えると](https://www.kibun.co.jp/knowledge/neri/basics/siokanetsu/)の物性研究 | レンズを動かす→止めて考える→判定印を押す。印付き資料へ変化。押印はゲーム独自の成果表現 | 7.5秒 |
| 宿舎 | [海響館：ペンギンの寝姿](https://www.kaikyokan.com/cms/cp_sealife/190729/)を休息の参考にする | 元のペンギンの目を閉じて長く休み、毛布の小さな呼吸、起きてヒレを広げる | 12.8秒 |
| 電気の増幅施設 | [Panasonic：電池残量表示](https://jpn.faq.panasonic.com/app/answers/detail/a_id/89117/p/3000) | スイッチを押す短い動作→三つの残量灯が順に点く→確認して待つ | 4.4秒 |
| 水の増幅施設 | [SANEI：ボールタップのカタログ](https://www.sanei.ltd/library/support/download/img/2020_377-392.pdf)の浮玉と水位 | 水位窓が下から満ち、黄色い浮きが一緒に上がる。ペンギンが観察する | 6.8秒 |
| ガスの増幅施設 | [CKD：圧力調整器](https://www.ckd.co.jp/kiki/jp/product/detail/396/)の手動ノブと圧力計 | 赤い弁を回す→針が振れて落ち着く→確認。メーターの外枠は固定 | 6秒 |
| 港・最終段階 | [三井E&S：港湾クレーン](https://www.mes.co.jp/products/logistics-system/)の吊り上げ・船への荷役 | 吊り具と箱が上がる→桟橋へ納品→舟が出発。ペンギンはヒレを振って見送る | 6.5秒 |

製塩は実際の砂からかん水を取って煮詰める工程を省略し、蒸発と熊手を組み合わせた表現。増幅施設は現実で得た資源を増幅する架空設備で、資料からは操作と表示の見せ方を採用した。研究所の押印や港の祭りも独自の演出。屋根の目印と加工による色・形の変化を保ちながら、回す、引く、刻む、集める、待つ、休む、振り分けるという行動を分けている。

## 実装と検証

- モデルとPrefab：`Assets/3Dmodel/Building_*_v002/`、`Harbor_Stage*_v002/`。
- Blender生成：`ArtSource/ProductionIsland_v002/generate_facilities.py`。
- 工程と可動部品：`Assets/Scripts/Presentation/World/FacilityProductionCycle.cs`。
- 既存ペンギンの姿勢：`WorkshopPenguin.cs`。元のFBX・画像は変更していない。
- 直接選択画面：`FacilityDesignGallery.cs`、`Assets/UI/ProductionIslandReview/FacilityReview.uxml` と `.uss`。
- 通常Play Modeの観測：`FacilityRevisionCapture.Start()`。工程、原料/完成品、停止中の全Transform、再開始、元のペンギン参照、子付け、道具等の変化を実フレームで確認する。手動でUpdateを呼んだり時刻を書き換えたりしない。
- 結果と工程画像：`ArtSource/ProductionIsland_v002/Facilities/Review/`。

通常Play Modeで動く15施設の8項目ずつ、計120項目がPASS。21項目の直接選択と停止・再開・全体表示もボタン経由で確認した。追加観測では、仕分けの三方向への搬出、電気の残量灯0〜3個、水位の上昇と浮きの0.10m上昇、ガス弁135度の回転を確認（individual-motion-verification.txt）。ユーザーによる各施設のデザイン確認と、大量配置時の実機性能測定は別途必要。表示専用で、生産計算・在庫には接続していない。
