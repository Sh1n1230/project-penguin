# .claude/

Claude Code (および互換エージェント) 向けの設定。**個人設定は `settings.local.json` に書く** (`.gitignore` 済み)。

## 構成

| ファイル | 役割 | 読み込まれるタイミング |
|---|---|---|
| `../CLAUDE.md` | プロジェクト全体の前提と絶対規則 | 毎セッション開始時 |
| `rules/unity.md` | Unity アセット・asmdef・C# 規約 | `Assets/` `ProjectSettings/` `Packages/` のファイルを読んだとき |
| `rules/privacy.md` | レシート・購買履歴・API キーの扱い | `backend/` `Assets/Scripts/{Data,Backend}/` を読んだとき |
| `rules/backend.md` | FastAPI / Python 実装規約 | `backend/` を読んだとき |
| `settings.json` | permissions と hooks | 毎セッション |
| `hooks/*.py` | 破壊的操作の機械的ブロック | 該当ツール呼び出しの直前 |

`CLAUDE.md` は長いほど守られなくなるため短く保ち、領域別の詳細は `rules/` の path スコープ付きルールに逃がしている。該当ファイルを読んだ時点で会話の直近位置に注入されるので、セッション後半でも効く。

## permissions

- **allow** — 読み取り系の git / lint / test。確認プロンプトを出さない。
- **ask** — commit・push・履歴操作・`.gitattributes` 編集など、実行前に人が見るべきもの。
- **deny** — `.env` や `*.db` (購買履歴) の読み取り、force push、`filter-branch`。

`CLAUDE.md` の記述は「文脈」であって強制力がない。**確実に止めたいものは permissions か hooks に書く。**

## hooks

Python 標準ライブラリのみで書いてある (Windows で bash / jq に依存しないため)。`python` が PATH にあれば動く。

| フック | イベント | ブロックするもの |
|---|---|---|
| `guard_git.py` | PreToolUse / Bash | force push、`main` への直接 push、`filter-branch`、`commit --no-verify`、`.env` や `*.db` の `git add` |
| `guard_write.py` | PreToolUse / Write・Edit | Unity YAML (`.unity` `.prefab` `.asset` `.meta` …) の直接編集、生成物への書き込み、`.env` への書き込み、API キー実値の混入 |

いずれも「確認すれば通してよい」操作は扱わない (それは `permissions.ask` の役割)。ここで止めるのは**確認しても許可しないもの**だけ。

### 動作確認

```bash
echo '{"cwd":".","tool_input":{"command":"git push --force"}}' | python .claude/hooks/guard_git.py
```

`permissionDecision: "deny"` を含む JSON が返れば動いている。何も出力されなければ通過 (= 通常の権限フローに従う)。フックが読み込まれているかは `/context`、ルールの読み込み状況は `/memory` で確認できる。
