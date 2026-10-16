using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectPenguin.Domain.Island
{
    /// <summary>
    /// 島で作る品目。お魚 (<see cref="Fish"/>) は通貨を兼ね、置き場の上限が無い。
    /// </summary>
    public enum Item
    {
        Fish,
        Surimi,
        Salt,
        Kelp,
        Kamaboko,
        Chikuwa,
        DriedFish,
        Oden,
    }

    /// <summary>現実の行動から得る資源。島の中では作らない (増幅施設で受け取る量を増やす)。</summary>
    public enum Resource
    {
        /// <summary>建てるのに使う。</summary>
        Electricity,

        /// <summary>海を凍らせて島を広げるのに使う。</summary>
        Water,

        /// <summary>施設を動かすのに使う (時間とともに減る)。</summary>
        Gas,

        /// <summary>ミッションで得る。電気・水・ガスのどれの代わりにもなる。</summary>
        AllMighty,

        /// <summary>研究所で作り、施設を速くする。</summary>
        Pearl,
    }

    /// <summary>施設の種類。素材は `Assets/3Dmodel/Building_*_v002`。</summary>
    public enum FacilityKind
    {
        Fishery,
        Preparation,
        Saltworks,
        KelpFarm,
        Kamaboko,
        Chikuwa,
        Drying,
        Oden,
        Warehouse,
        Dormitory,
        Research,
        Sorter,
        ElectricAmplifier,
        WaterAmplifier,
        GasAmplifier,
    }

    /// <summary>施設の役割。</summary>
    public enum FacilityRole
    {
        /// <summary>レシピに沿って品目を作る。</summary>
        Producer,

        /// <summary>置き場を増やす。</summary>
        Storage,

        /// <summary>住める働き手を増やす。</summary>
        Housing,

        /// <summary>港の注文を、そろった時点で自動で納品する。</summary>
        AutoDeliver,

        /// <summary>現実から得る資源の量を増やす。</summary>
        Amplifier,
    }

    /// <summary>品目の個数の組。</summary>
    public readonly struct ItemAmount
    {
        public ItemAmount(Item item, int count)
        {
            Item = item;
            Count = count;
        }

        public Item Item { get; }
        public int Count { get; }
    }

    /// <summary>作り方 1 つ。</summary>
    public sealed class Recipe
    {
        public Recipe(string name, double seconds, IReadOnlyList<ItemAmount> inputs, ItemAmount output, double gasPerHour)
        {
            Name = name;
            Seconds = seconds;
            Inputs = inputs ?? Array.Empty<ItemAmount>();
            Output = output;
            GasPerHour = gasPerHour;
        }

        /// <summary>画面に出す名前 (「強火」など)。1 つしか無いときは空。</summary>
        public string Name { get; }

        /// <summary>1 回にかかる秒数 (速さ 1 倍のとき)。</summary>
        public double Seconds { get; }

        public IReadOnlyList<ItemAmount> Inputs { get; }
        public ItemAmount Output { get; }

        /// <summary>動いている間に使うガス (毎時)。</summary>
        public double GasPerHour { get; }
    }

    /// <summary>施設の定義 (マスターデータ)。</summary>
    public sealed class FacilityDef
    {
        public FacilityDef(FacilityKind kind, string name, string description, int size, FacilityRole role, int unlockLevel,
            double electricityCost, double fishCost, int workers, bool needsCoast, IReadOnlyList<Recipe> recipes,
            Item? qualityItem = null, Resource? amplifies = null, int maxCount = int.MaxValue)
        {
            Kind = kind;
            Name = name;
            Description = description;
            Size = size;
            Role = role;
            UnlockLevel = unlockLevel;
            ElectricityCost = electricityCost;
            FishCost = fishCost;
            Workers = workers;
            NeedsCoast = needsCoast;
            Recipes = recipes ?? Array.Empty<Recipe>();
            QualityItem = qualityItem;
            Amplifies = amplifies;
            MaxCount = maxCount;
        }

        public FacilityKind Kind { get; }
        public string Name { get; }
        public string Description { get; }

        /// <summary>1 なら 1×1、2 なら 2×2。</summary>
        public int Size { get; }

        public FacilityRole Role { get; }
        public int UnlockLevel { get; }
        public double ElectricityCost { get; }
        public double FishCost { get; }

        /// <summary>動かすのに要るペンギンの数。0 なら要らない。</summary>
        public int Workers { get; }

        /// <summary>海に面していないと動かない。</summary>
        public bool NeedsCoast { get; }

        public IReadOnlyList<Recipe> Recipes { get; }

        /// <summary>この品目の質の良いマスの上に建てると速くなる。</summary>
        public Item? QualityItem { get; }

        /// <summary>増幅施設が増やす資源。</summary>
        public Resource? Amplifies { get; }

        /// <summary>島に建てられる上限。</summary>
        public int MaxCount { get; }
    }

    /// <summary>品目と施設のマスターデータ。</summary>
    public static class IslandCatalog
    {
        private static readonly Dictionary<Item, (string Name, int Value)> ItemInfo = new Dictionary<Item, (string, int)>
        {
            { Item.Fish, ("お魚", 1) },
            { Item.Surimi, ("すり身", 5) },
            { Item.Salt, ("塩", 3) },
            { Item.Kelp, ("海藻", 3) },
            { Item.Kamaboko, ("かまぼこ", 15) },
            { Item.Chikuwa, ("ちくわ", 15) },
            { Item.DriedFish, ("干物", 12) },
            { Item.Oden, ("おでん", 80) },
        };

        public static readonly IReadOnlyList<Item> Items = (Item[])Enum.GetValues(typeof(Item));

        public static readonly IReadOnlyList<FacilityDef> Facilities = new[]
        {
            new FacilityDef(FacilityKind.Fishery, "漁場", "海から魚を引き上げる。海に面して建てる", 2, FacilityRole.Producer, 1,
                10, 0, 1, true,
                new[] { new Recipe("", 4, null, new ItemAmount(Item.Fish, 1), 0.25) }, qualityItem: Item.Fish),
            new FacilityDef(FacilityKind.Warehouse, "倉庫", "品目の置き場を増やす", 1, FacilityRole.Storage, 1,
                5, 20, 0, false, null),
            new FacilityDef(FacilityKind.Dormitory, "宿舎", "住めるペンギンを増やす", 1, FacilityRole.Housing, 2,
                10, 50, 0, false, null),
            new FacilityDef(FacilityKind.Preparation, "さばき場", "魚をすり身にする", 2, FacilityRole.Producer, 2,
                20, 30, 1, false,
                new[] { new Recipe("", 6, new[] { new ItemAmount(Item.Fish, 3) }, new ItemAmount(Item.Surimi, 1), 0.25) }),
            new FacilityDef(FacilityKind.Saltworks, "製塩所", "海水から塩をとる。海に面して建てる", 2, FacilityRole.Producer, 3,
                25, 60, 1, true,
                new[] { new Recipe("", 8, null, new ItemAmount(Item.Salt, 1), 0.25) }, qualityItem: Item.Salt),
            new FacilityDef(FacilityKind.ElectricAmplifier, "電気の増幅所", "写真で受け取る電気を増やす", 2, FacilityRole.Amplifier, 3,
                30, 80, 0, false, null, amplifies: Resource.Electricity, maxCount: 2),
            new FacilityDef(FacilityKind.KelpFarm, "海藻場", "海藻を育てて巻き上げる。海に面して建てる", 2, FacilityRole.Producer, 4,
                30, 100, 1, true,
                new[] { new Recipe("", 8, null, new ItemAmount(Item.Kelp, 1), 0.25) }, qualityItem: Item.Kelp),
            new FacilityDef(FacilityKind.WaterAmplifier, "水の増幅所", "写真で受け取る水を増やす", 2, FacilityRole.Amplifier, 4,
                30, 120, 0, false, null, amplifies: Resource.Water, maxCount: 2),
            new FacilityDef(FacilityKind.Kamaboko, "かまぼこ工場", "すり身を蒸してかまぼこにする", 2, FacilityRole.Producer, 5,
                40, 200, 1, false,
                new[] { new Recipe("", 10, new[] { new ItemAmount(Item.Surimi, 2) }, new ItemAmount(Item.Kamaboko, 1), 0.5) }),
            new FacilityDef(FacilityKind.Chikuwa, "ちくわ工場", "すり身を棒に巻いて焼く。強火なら速いがガスを多く使う", 2,
                FacilityRole.Producer, 5, 40, 200, 1, false,
                new[]
                {
                    new Recipe("とろ火", 10, new[] { new ItemAmount(Item.Surimi, 2) }, new ItemAmount(Item.Chikuwa, 1), 0.5),
                    new Recipe("強火", 6, new[] { new ItemAmount(Item.Surimi, 2) }, new ItemAmount(Item.Chikuwa, 1), 1.5),
                }),
            new FacilityDef(FacilityKind.GasAmplifier, "ガスの増幅所", "歩いて受け取るガスを増やす", 2, FacilityRole.Amplifier, 5,
                30, 150, 0, false, null, amplifies: Resource.Gas, maxCount: 2),
            new FacilityDef(FacilityKind.Drying, "干物場", "魚に塩をして干す", 2, FacilityRole.Producer, 6,
                50, 300, 1, false,
                new[]
                {
                    new Recipe("", 12, new[] { new ItemAmount(Item.Fish, 2), new ItemAmount(Item.Salt, 1) },
                        new ItemAmount(Item.DriedFish, 1), 0.5),
                }),
            new FacilityDef(FacilityKind.Research, "研究所", "お魚と海藻を調べて真珠を作る。真珠は施設を速くする", 2,
                FacilityRole.Producer, 6, 60, 400, 1, false,
                new[] { new Recipe("", 60, new[] { new ItemAmount(Item.Fish, 20), new ItemAmount(Item.Kelp, 2) }, default, 0.5) },
                maxCount: 1),
            new FacilityDef(FacilityKind.Sorter, "仕分け所", "そろった注文を港へ自動で届ける", 1, FacilityRole.AutoDeliver, 7,
                40, 500, 1, false, null, maxCount: 1),
            new FacilityDef(FacilityKind.Oden, "おでん屋台", "かまぼこ・ちくわ・海藻を煮込む", 2, FacilityRole.Producer, 8,
                120, 2000, 2, false,
                new[]
                {
                    new Recipe("", 20,
                        new[] { new ItemAmount(Item.Kamaboko, 1), new ItemAmount(Item.Chikuwa, 1), new ItemAmount(Item.Kelp, 1) },
                        new ItemAmount(Item.Oden, 1), 1.0),
                }),
        };

        private static readonly Dictionary<FacilityKind, FacilityDef> ByKind = Facilities.ToDictionary(f => f.Kind);

        public static FacilityDef Get(FacilityKind kind) => ByKind[kind];

        public static string NameOf(Item item) => ItemInfo[item].Name;

        /// <summary>港での品目の値 (お魚何匹ぶんか)。</summary>
        public static int ValueOf(Item item) => ItemInfo[item].Value;

        public static string NameOf(Resource resource) => resource switch
        {
            Resource.Electricity => "電気",
            Resource.Water => "水",
            Resource.Gas => "ガス",
            Resource.AllMighty => "オールマイティ",
            Resource.Pearl => "真珠",
            _ => resource.ToString(),
        };

        /// <summary>研究所のレシピは真珠を作る (出力の品目は使わない)。</summary>
        public static bool ProducesPearl(FacilityKind kind) => kind == FacilityKind.Research;
    }
}
