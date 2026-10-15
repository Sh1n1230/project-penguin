# 生産の島：動作検証の要約

2026-10-11更新。個人環境のパス・Editor instance ID・大量の実測JSONは公開しない。再実行の詳しい数値はローカルの `.local-tools/` に保存する。

## 自動回帰テスト

`Assets/Tests/EditMode/FacilityProductionCycleTests.cs` で、全15種類の工程の境界時刻と Loading → Working → Output → Returning → 次周のLoadingを検査する。原料の変換時刻、複数周期後の段階、時刻の順序、未設定参照のエラー表示も対象とする。

`Assets/Tests/EditMode/FacilityGalleryInputTests.cs` で、Galleryの有効化・無効化がInput System設定とマウスの状態を変更しないことを検査する。

Unity Test RunnerのEditMode、または接続中EditorへUnity CLIの`run_tests --mode editor`を送って実行する。Unity Testsワークフローは同一リポジトリのPRでも実行対象となる。ライセンスが未設定の環境と外部forkではUnityテストをスキップする。

## 制作時の動作確認

- v002：15施設×8項目＝120項目の実フレーム検査を実施。仕分けの三方向、残量灯、水位・浮き、ガス弁の回転も比較した。
- UI：当時の仮想マウスによる50操作を確認。仮想入力の合格は、ユーザーの実マウスでの合格と同一視しない。
- v001：Play Modeのサンプリングで91 PASS / 0 FAIL / 2 BLOCKED。詳細な数値の要約は [動作結果](production-island-motion-results.md)。描画を見ていない条件は受入済みと扱わない。
- +1演出の再有効化時にalphaが戻らない問題を修正し、完了後と途中中断後の再表示を確認した。

旧Preview検査と、背面で時間が停止した試行は正常動作の合格証拠に含めない。JSONのコピーをGitに保持する代わりに、回帰検査をTest Frameworkへ移し、手動の結果はMarkdownに要約する。

## 手動で確認するもの

[確認手順](../production-island-review-user-guide.md) に従い、施設の識別しやすさ、原料と完成品の見分け、既存ペンギンの関与、施設ごとの動きの違いをGame画面で確認する。見た目と実マウスの最終確認は引き続き必要。
