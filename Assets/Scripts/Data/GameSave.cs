using System;
using ProjectPenguin.Domain.Island;

namespace ProjectPenguin.Data
{
    /// <summary>
    /// 端末に保存するプレイヤーの状態。写真そのものと購買の明細は入れない (.claude/rules/privacy.md)。
    /// JsonUtility で読み書きするため public フィールドにしている。フィールド名を変えると古い保存が読めなくなる。
    /// </summary>
    [Serializable]
    public sealed class GameSave
    {
        public const int CurrentVersion = 1;

        public int version = CurrentVersion;

        /// <summary>最初に起動した時刻。氷の状態機械 (GameSession) はここから操作を再生して戻す。</summary>
        public long createdUnixMs;

        /// <summary>開発ビルドで時計を進めた量。</summary>
        public long devOffsetMs;

        /// <summary>前回開いたアプリの日 (おかえりの判定)。</summary>
        public int lastOpenDay;

        public string playerName = "";
        public bool onboarded;

        /// <summary>氷の状態機械への操作 (起きた順)。</summary>
        public GameOp[] ops = Array.Empty<GameOp>();

        public IslandSave island;

        /// <summary>資源を受け取った記録 (記録画面)。新しいものが後ろ。</summary>
        public ActivityEntry[] activity = Array.Empty<ActivityEntry>();
    }

    /// <summary>氷の状態機械への操作 1 つ。</summary>
    [Serializable]
    public sealed class GameOp
    {
        public const string Photo = "photo";
        public const string Select = "select";
        public const string CheckIn = "checkin";

        public string kind;
        public long atMs;
        public string id;
        public int printDay;
        public int verification;
        public int answer;
        public bool noShopping;
    }

    /// <summary>現実の行動で資源を受け取った記録 1 件。</summary>
    [Serializable]
    public sealed class ActivityEntry
    {
        public const string Photo = "photo";
        public const string Steps = "steps";
        public const string Mission = "mission";

        public long atMs;
        public int day;
        public string kind;

        /// <summary>写真のカテゴリ (<see cref="EcoCategory"/>)。写真以外は -1。</summary>
        public int category = -1;

        /// <summary>写っていたもの・ミッション名・歩数など。</summary>
        public string label;

        public double electricity;
        public double water;
        public double gas;
        public double allMighty;
    }
}
