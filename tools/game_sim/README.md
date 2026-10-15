# ゲームロジックの参照実装 (Python)

`docs/game-logic.md` の規則 (氷・盾・おかえり・かけら・段・ペンギンの来訪・スタンプ) を Python で書いたもの。C# の `Assets/Scripts/Domain/Game/` はこのファイルを写したもので、8 人の利用者を 8 週間動かした結果が 1 日ずつ一致することを EditMode テスト (`GameSimParityTests`) で確かめている。

| ファイル | 中身 |
|---|---|
| `game_sim.py` | 参照実装 (`Session`)、8 人の利用者の操作、目標の確認。標準ライブラリだけで動く |
| `game_sim_test.py` | 単体テスト 22 件 |
| `gen_game_golden.py` | `game_sim.py` の出力から C# の期待値 `Assets/Tests/EditMode/Domain/GameSimGolden.cs` を作る |

## 使い方 (リポジトリのルートで)

```bash
# 単体テスト
uv run --no-project --with pytest pytest tools/game_sim -q

# 8 人の結果と目標の合否 (決めたままの値と 15d の値の両方)
python3 tools/game_sim/game_sim.py

# C# の期待値を作り直す
python3 tools/game_sim/gen_game_golden.py > Assets/Tests/EditMode/Domain/GameSimGolden.cs
```

## 値や規則を変えるとき

1. `game_sim.py` の `Params` (または規則) を直し、`game_sim_test.py` を通す。
2. `gen_game_golden.py` で `GameSimGolden.cs` を作り直す。手で編集しない。
3. C# の `GameParameters` (または `GameSession`) を同じ値に直し、Unity の Test Runner で EditMode を回す。
4. `docs/game-logic.md` の表を直す。

CI は 1 のテストと、2 の生成結果がコミット済みの `GameSimGolden.cs` と一致するかを PR ごとに確かめる。C# 側 (3) は Unity のライセンスが要るため CI では回らない。
