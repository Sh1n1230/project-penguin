# セキュリティポリシー

Project Penguin はレシート (ユーザーの購買履歴) と外部 LLM の API キーを扱います。脆弱性を見つけた場合は、以下の方法で非公開で報告してください。

## 報告のしかた

**public な issue・PR・Discussions には書かないでください。** 修正前に内容が公開されると、悪用される前に対処できなくなります。

GitHub の非公開の脆弱性報告 (Private vulnerability reporting) を使ってください。

1. リポジトリの **Security** タブを開く
2. **Report a vulnerability** を押す
3. 下の「書いてほしいこと」を記入して送信する

直接のリンク: <https://github.com/Sh1n1230/project-penguin/security/advisories/new>

### 書いてほしいこと

- 影響を受けるファイル・機能 (例: `backend/`、`Assets/Scripts/Presentation/UI/ReceiptCameraPreview.cs`)
- 再現手順と、確認したコミット (`git rev-parse HEAD`)
- 想定される影響 (例: API キーの漏えい、購買情報の端末外への流出)
- わかる範囲での修正案

**実際のレシート画像・購買明細・API キーなど、本物の個人情報や秘密情報は報告に含めないでください。** 再現にはダミーの値を使ってください。

## 対象

| 対象 | 例 |
|---|---|
| Unity クライアント (`Assets/`、`ProjectSettings/`、`Packages/`) | レシート画像や購買情報がログ・ディスク・端末外に残る、権限の扱いの不備 |
| バックエンド (`backend/`) | API キーの漏えい、認証の不備、入力検証の不備 |
| ビルド・署名 (`Assets/Editor/Build/`) | 署名鍵やパスワードが成果物・設定ファイルに残る |
| CI と開発用の安全装置 (`.github/`、`scripts/`、`.claude/hooks/`) | 秘密情報の検査をすり抜ける、ワークフローの権限の過剰 |

### 対象外

- このリポジトリが取り込んでいるサードパーティのパッケージ・スキル (`Packages/manifest.json` の依存、`.agents/skills/`・`.claude/skills/` の外部スキル、`Assets/TextMesh Pro/`) そのものの脆弱性は、それぞれの提供元に報告してください。このプロジェクトでの使い方に問題がある場合は対象です。

## 対応するバージョン

まだリリースはなく、`main` ブランチの最新のコミットだけを対象にします。

## 報告を受けた後の流れ

1. 報告を受け取ったことを、GitHub の Security Advisory 上で返信します
2. 再現と影響範囲を確認します
3. 修正を非公開のブランチ (Security Advisory の一時フォーク) で作り、`main` に取り込みます
4. 必要に応じて Security Advisory を公開します。報告者の名前を載せてよいかは事前に確認します

漏えいした秘密情報が見つかった場合は、履歴からの削除より先に、該当するキーの失効と再発行を行います。
