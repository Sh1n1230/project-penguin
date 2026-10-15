using System.Collections.Generic;

namespace ProjectPenguin.Domain.Game
{
    /// <summary>来訪の理由。</summary>
    public enum ArrivalReason
    {
        Onboarding,
        Milestone,
        Weekly,
    }

    /// <summary>来たペンギン 1 羽。来たペンギンは消えない。</summary>
    public readonly struct PenguinArrival
    {
        public PenguinArrival(string species, int day, ArrivalReason reason)
        {
            Species = species;
            Day = day;
            Reason = reason;
        }

        public string Species { get; }

        /// <summary>来たアプリの日。</summary>
        public int Day { get; }

        public ArrivalReason Reason { get; }
    }

    /// <summary>19 種と、節目・週ごとの順番 (15c §3.2・§3.3)。</summary>
    public static class PenguinCatalog
    {
        public const string Onboarding = "アデリーペンギン";
        public const string FirstRecord = "コガタペンギン";
        public const string AllKinds = "マゼランペンギン";
        public const string FirstComeback = "ガラパゴスペンギン";
        public const string FiveMissions = "ヒゲペンギン";
        public const string Total14 = "オウサマペンギン";
        public const string Total30 = "コウテイペンギン";
        public const string FourWeeks = "キガシラペンギン";

        /// <summary>節目の種 (表の順)。週の順番表を使い切った後はここから未着の種を出す。</summary>
        public static readonly IReadOnlyList<string> MilestoneOrder = new[]
        {
            Onboarding, FirstRecord, AllKinds, FirstComeback, FiveMissions, Total14, Total30, FourWeeks,
        };

        /// <summary>週ごとの来訪の順番 (節目の種を含まない 11 種)。</summary>
        public static readonly IReadOnlyList<string> WeeklyOrder = new[]
        {
            "ジェンツーペンギン", "フンボルトペンギン", "マカロニペンギン", "ロイヤルペンギン", "ケープペンギン",
            "フィヨルドランドペンギン", "スネアーズペンギン", "キタイワトビペンギン", "ミナミイワトビペンギン",
            "ヒガシイワトビペンギン", "シュレーターペンギン",
        };
    }
}
