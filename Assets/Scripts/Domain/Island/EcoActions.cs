using System;
using System.Collections.Generic;
using System.Linq;
using ProjectPenguin.Domain.Game;

namespace ProjectPenguin.Domain.Island
{
    /// <summary>写真に写ったエコ活動の分類。AI (Hack Day で作る backend) かモックが決める。</summary>
    public enum EcoCategory
    {
        /// <summary>電気を節約する (消灯・冷暖房・待機電力)。</summary>
        SaveElectricity,

        /// <summary>水を節約する (シャワー・洗い物・節水)。</summary>
        SaveWater,

        /// <summary>移動を変える (徒歩・自転車・公共交通)。</summary>
        Move,

        /// <summary>食べ物 (食べきり・地元の食材・植物性の食事)。</summary>
        Food,

        /// <summary>物を大事にする (マイボトル・エコバッグ・リユース・分別)。</summary>
        Goods,

        /// <summary>エコ活動が写っていない、または判定できない。</summary>
        Unknown,
    }

    /// <summary>写真の判定結果。画像そのものは持たない (端末の外にも残さない)。</summary>
    public sealed class EcoPhotoVerdict
    {
        public EcoPhotoVerdict(EcoCategory category, string label, string comment, double confidence)
        {
            Category = category;
            Label = label ?? "";
            Comment = comment ?? "";
            Confidence = confidence;
        }

        public EcoCategory Category { get; }

        /// <summary>写っていたもの (「マイボトル」など)。</summary>
        public string Label { get; }

        /// <summary>ペンギンのひとこと。</summary>
        public string Comment { get; }

        public double Confidence { get; }

        public bool IsEco => Category != EcoCategory.Unknown;
    }

    /// <summary>資源の増減の組。</summary>
    public sealed class ResourceBundle
    {
        private readonly double[] _values = new double[Enum.GetValues(typeof(Resource)).Length];

        public double this[Resource r]
        {
            get => _values[(int)r];
            set => _values[(int)r] = value;
        }

        public bool IsEmpty => _values.All(v => Math.Abs(v) < 1e-9);

        public IEnumerable<KeyValuePair<Resource, double>> NonZero()
        {
            for (var i = 0; i < _values.Length; i++)
            {
                if (Math.Abs(_values[i]) > 1e-9)
                {
                    yield return new KeyValuePair<Resource, double>((Resource)i, _values[i]);
                }
            }
        }

        public static ResourceBundle Of(Resource r, double v)
        {
            var b = new ResourceBundle();
            b[r] = v;
            return b;
        }
    }

    /// <summary>カテゴリごとの説明と、どの資源に効くか。</summary>
    public static class EcoCategories
    {
        public static string NameOf(EcoCategory c) => c switch
        {
            EcoCategory.SaveElectricity => "電気の節約",
            EcoCategory.SaveWater => "水の節約",
            EcoCategory.Move => "エコな移動",
            EcoCategory.Food => "食べ物を大切に",
            EcoCategory.Goods => "物を大切に",
            _ => "エコ活動",
        };

        /// <summary>主に増える資源。食べ物と物はどれにでも使えるオールマイティ。</summary>
        public static Resource MainResource(EcoCategory c) => c switch
        {
            EcoCategory.SaveElectricity => Resource.Electricity,
            EcoCategory.SaveWater => Resource.Water,
            EcoCategory.Move => Resource.Gas,
            _ => Resource.AllMighty,
        };
    }

    /// <summary>ミッション 1 件 (アプリ独自の文言。値の出典を要するものは載せない)。</summary>
    public sealed class MissionDef
    {
        public MissionDef(string id, string title, string hint, EcoCategory category)
        {
            Id = id;
            Title = title;
            Hint = hint;
            Category = category;
        }

        public string Id { get; }
        public string Title { get; }
        public string Hint { get; }
        public EcoCategory Category { get; }
    }

    /// <summary>ミッションの一覧と、日付で決まる今日の 3 件。</summary>
    public static class MissionCatalog
    {
        public const int DailyChoices = 3;

        public static readonly IReadOnlyList<MissionDef> All = new[]
        {
            new MissionDef("M01", "マイボトルを持ち歩く", "飲み物はボトルに入れて出かけよう", EcoCategory.Goods),
            new MissionDef("M02", "エコバッグで買い物する", "レジ袋をもらわずに帰ろう", EcoCategory.Goods),
            new MissionDef("M03", "使っていない部屋の電気を消す", "出るときにスイッチを確かめよう", EcoCategory.SaveElectricity),
            new MissionDef("M04", "シャワーを 1 分短くする", "髪を洗う間はお湯を止めよう", EcoCategory.SaveWater),
            new MissionDef("M05", "ごはんを食べきる", "食べられる分だけよそおう", EcoCategory.Food),
            new MissionDef("M06", "ひと駅ぶん歩く", "天気が良ければ歩いてみよう", EcoCategory.Move),
            new MissionDef("M07", "エレベーターより階段を使う", "2〜3 階なら階段で", EcoCategory.Move),
            new MissionDef("M08", "冷暖房の温度を 1℃ ゆるめる", "服で調整してみよう", EcoCategory.SaveElectricity),
            new MissionDef("M09", "肉の代わりに豆腐や豆を食べる", "1 食だけ植物のたんぱく質に", EcoCategory.Food),
            new MissionDef("M10", "地元でとれた野菜を選ぶ", "産地の表示を見てみよう", EcoCategory.Food),
            new MissionDef("M11", "コンセントを抜いて待機電力を減らす", "使わない家電のプラグを抜こう", EcoCategory.SaveElectricity),
            new MissionDef("M12", "洗い物のときに水を流しっぱなしにしない", "おけにためて洗おう", EcoCategory.SaveWater),
            new MissionDef("M13", "ペットボトルを分別して出す", "キャップとラベルを外そう", EcoCategory.Goods),
            new MissionDef("M14", "自転車で出かける", "近い所は自転車で", EcoCategory.Move),
            new MissionDef("M15", "冷蔵庫を開ける回数を減らす", "何を取るか決めてから開けよう", EcoCategory.SaveElectricity),
            new MissionDef("M16", "歯みがき中に水を止める", "コップに水をくもう", EcoCategory.SaveWater),
        };

        private static readonly Dictionary<string, MissionDef> ById = All.ToDictionary(m => m.Id);

        public static MissionDef Find(string id) => id != null && ById.TryGetValue(id, out var m) ? m : null;

        /// <summary>その日の 3 件。日付を種にするので何度開いても同じ (docs/game-logic.md §3)。</summary>
        public static IReadOnlyList<MissionDef> DailyFor(int appDay)
        {
            var rng = new SplitMix64((ulong)(appDay * 7919L + 17));
            var pool = All.ToList();
            var picked = new List<MissionDef>();
            while (picked.Count < DailyChoices && pool.Count > 0)
            {
                var i = rng.NextInt(pool.Count);
                picked.Add(pool[i]);
                pool.RemoveAt(i);
            }

            return picked;
        }
    }

    /// <summary>現実の行動から資源を決める。倍率 (増幅施設・ペンギン) は <see cref="IslandGame"/> が掛ける。</summary>
    public static class EcoGrant
    {
        /// <summary>写真 1 枚の基本の資源。主の資源に多く、ほかの電気・水・ガスに少し。</summary>
        public static ResourceBundle ForPhoto(EcoPhotoVerdict verdict, IslandParameters p)
        {
            var b = new ResourceBundle();
            if (verdict == null)
            {
                return b;
            }

            var main = verdict.IsEco ? EcoCategories.MainResource(verdict.Category) : Resource.AllMighty;
            var mainAmount = verdict.IsEco ? p.PhotoMainGrant : p.PhotoSideGrant;
            b[main] += mainAmount;
            foreach (var r in new[] { Resource.Electricity, Resource.Water, Resource.Gas })
            {
                if (r != main)
                {
                    b[r] += p.PhotoSideGrant;
                }
            }

            return b;
        }

        /// <summary>歩数から得るガス。その日にすでに受け取った分を引いて、上限までにする。</summary>
        public static double GasForSteps(int stepsToday, double alreadyGranted, IslandParameters p)
        {
            var total = Math.Min(p.StepGasPerDayMax, Math.Floor(Math.Max(0, stepsToday) / (double)p.StepsPerGas));
            return Math.Max(0.0, total - alreadyGranted);
        }

        /// <summary>ミッションの振り返り 1 件。正直に「できなかった」と答えても少しもらえる。</summary>
        public static ResourceBundle ForCheckIn(CheckInAnswer answer, IslandParameters p) =>
            ResourceBundle.Of(Resource.AllMighty, answer == CheckInAnswer.Done ? p.MissionAllMighty : p.MissionTriedAllMighty);
    }

    /// <summary>決定的な乱数 (実行環境によらず同じ列)。注文と今日のミッションに使う。</summary>
    public sealed class SplitMix64
    {
        private ulong _state;

        public SplitMix64(ulong seed)
        {
            _state = seed;
        }

        public ulong Next()
        {
            unchecked
            {
                _state += 0x9E3779B97F4A7C15UL;
                var z = _state;
                z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
                z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
                return z ^ (z >> 31);
            }
        }

        /// <summary>0 以上 <paramref name="max"/> 未満。</summary>
        public int NextInt(int max) => max <= 0 ? 0 : (int)(Next() % (ulong)max);
    }
}
