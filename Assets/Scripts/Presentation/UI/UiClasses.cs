namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// C# から付け外しする USS のクラス名。<c>AddToClassList("pp-hidden")</c> のように文字列で書かず、ここの定数を使う。
    /// 部品 (BEM のブロック) ごとに入れ子のクラスを 1 つ置き、ブロックそのものは <c>Root</c> にする。
    /// どの定数も USS のセレクタか UXML の class 属性に実在することを EditMode の UiNamesTests が確かめる。
    /// 部品の見た目と使い方は docs/design-system.md を参照。
    /// </summary>
    public static class UiClasses
    {
        /// <summary>要素を隠す (display: none)。</summary>
        public const string Hidden = "pp-hidden";

        public const string Card = "pp-card";
        public const string Elevated = "pp-elevated";
        public const string SectionTitle = "pp-section-title";

        /// <summary>文字の大きさ・太さ・色。</summary>
        public static class Text
        {
            public const string Title = "pp-text-title";
            public const string Label = "pp-text-label";
            public const string Caption = "pp-text-caption";
            public const string Bold = "pp-text-bold";
            public const string Heavy = "pp-text-heavy";
            public const string Sub = "pp-text-sub";
        }

        /// <summary>アイコンの形 (SVG)。色は <see cref="Tint"/> と組み合わせる。</summary>
        public static class Icon
        {
            public const string Root = "pp-icon";

            // 資源
            public const string Electricity = "pp-icon--electricity";
            public const string Water = "pp-icon--water";
            public const string Gas = "pp-icon--gas";
            public const string AllMighty = "pp-icon--allmighty";
            public const string Pearl = "pp-icon--pearl";

            // 品目
            public const string Fish = "pp-icon--fish";
            public const string Surimi = "pp-icon--surimi";
            public const string Salt = "pp-icon--salt";
            public const string Kelp = "pp-icon--kelp";
            public const string Kamaboko = "pp-icon--kamaboko";
            public const string Chikuwa = "pp-icon--chikuwa";
            public const string DriedFish = "pp-icon--dried-fish";
            public const string Oden = "pp-icon--oden";

            // 操作と施設
            public const string Build = "pp-icon--build";
            public const string Camera = "pp-icon--camera";
            public const string Deliver = "pp-icon--deliver";
            public const string ExpandIsland = "pp-icon--expand-island";
            public const string Flag = "pp-icon--flag";
            public const string Leaf = "pp-icon--leaf";
            public const string Penguin = "pp-icon--penguin";
            public const string Production = "pp-icon--production";
            public const string RecipeHigh = "pp-icon--recipe-high";
            public const string Research = "pp-icon--research";
            public const string TimeForward = "pp-icon--time-forward";

            // 状態 (止まった理由)
            public const string Check = "pp-icon--check";
            public const string Warning = "pp-icon--warning";
            public const string NoCoast = "pp-icon--no-coast";
            public const string WorkerShortage = "pp-icon--worker-shortage";
            public const string GasEmpty = "pp-icon--gas-empty";
            public const string MaterialWait = "pp-icon--material-wait";
            public const string StorageFull = "pp-icon--storage-full";
        }

        /// <summary>アイコンの色。</summary>
        public static class Tint
        {
            public const string Primary = "pp-icon--primary";
            public const string Eco = "pp-icon--eco";
            public const string Point = "pp-icon--point";

            /// <summary>SVG の色のまま (白で掛ける)。</summary>
            public const string Original = "pp-icon--original";

            public const string Electricity = "pp-icon--res-electricity";
            public const string Water = "pp-icon--res-water";
            public const string Gas = "pp-icon--res-gas";
            public const string AllMighty = "pp-icon--res-allmighty";
            public const string Fish = "pp-icon--res-fish";
            public const string Pearl = "pp-icon--res-pearl";
        }

        public static class IconBadge
        {
            public const string Root = "pp-icon-badge";
            public const string Eco = "pp-icon-badge--eco";
        }

        public static class Badge
        {
            public const string Root = "pp-badge";
            public const string Eco = "pp-badge--eco";
        }

        /// <summary>シートの 1 行。</summary>
        public static class Row
        {
            public const string Root = "pp-row";
            public const string Body = "pp-row__body";
            public const string Title = "pp-row__title";
            public const string Sub = "pp-row__sub";
            public const string Last = "pp-row--last";
            public const string Locked = "pp-row--locked";
        }

        /// <summary>コストの並び。</summary>
        public static class Cost
        {
            public const string Root = "pp-cost";
            public const string Item = "pp-cost__item";
            public const string ItemShort = "pp-cost__item--short";
            public const string Icon = "pp-cost__icon";
            public const string Value = "pp-cost__value";
        }

        /// <summary>施設の状態の札。</summary>
        public static class Status
        {
            public const string Root = "pp-status";
            public const string Icon = "pp-status__icon";
            public const string Label = "pp-status__label";
            public const string Warn = "pp-status--warn";
            public const string Bad = "pp-status--bad";
        }

        /// <summary>小さな丸いボタン。</summary>
        public static class Pill
        {
            public const string Root = "pp-pill";
            public const string Primary = "pp-pill--primary";
            public const string Danger = "pp-pill--danger";
            public const string Selected = "pp-pill--selected";
        }

        public static class Stepper
        {
            public const string Root = "pp-stepper";
            public const string Button = "pp-stepper__button";
            public const string Value = "pp-stepper__value";
        }

        public static class Progress
        {
            public const string Root = "pp-progress";
            public const string Eco = "pp-progress--eco";
            public const string Point = "pp-progress--point";
        }

        /// <summary>写真の判定中の段階。</summary>
        public static class Step
        {
            public const string Active = "pp-step--active";
            public const string Done = "pp-step--done";
        }

        /// <summary>記録画面の棒グラフ。</summary>
        public static class BarChart
        {
            public const string Column = "pp-bar-chart__col";
            public const string Bar = "pp-bar-chart__bar";
            public const string BarToday = "pp-bar-chart__bar--today";
            public const string Value = "pp-bar-chart__value";
        }

        /// <summary>ホームの資源の帯の 1 つ。</summary>
        public static class Resource
        {
            public const string Bump = "pp-resource--bump";
            public const string Empty = "pp-resource--empty";
        }

        /// <summary>受け取った資源が飛んでいく「+20」。</summary>
        public static class Gain
        {
            public const string Root = "pp-gain";
            public const string Value = "pp-gain__value";
            public const string Gone = "pp-gain--gone";
        }

        public static class Toast
        {
            public const string Root = "pp-toast";
            public const string Hidden = "pp-toast--hidden";
        }

        public static class Sheet
        {
            public const string Closed = "pp-sheet--closed";
        }

        public static class Screen
        {
            public const string Hidden = "pp-screen--hidden";
        }

        public static class Tab
        {
            public const string Active = "pp-tab--active";
        }

        public static class SafeArea
        {
            public const string Root = "pp-safe-area";
            public const string Bottom = "pp-safe-area__bottom";
        }

        public static class DexCard
        {
            public const string Root = "pp-dex-card";
            public const string Locked = "pp-dex-card--locked";
            public const string Image = "pp-dex-card__image";
            public const string Name = "pp-dex-card__name";
            public const string Fact = "pp-dex-card__fact";
            public const string Bonus = "pp-dex-card__bonus";
        }

        public static class MissionCard
        {
            public const string Root = "pp-mission-card";
            public const string Title = "pp-mission-card__title";
            public const string Body = "pp-mission-card__body";
        }

        // ---- 画面ごとのクラス (各画面の USS) ----

        /// <summary>HomeScreen.uss</summary>
        public static class Home
        {
            public const string DemoVisible = "home__demo--visible";

            /// <summary>生産の島のシーンでだけ出すデモの操作 (目印。見た目は付けていない)。</summary>
            public const string DemoIsland = "home__demo-island";

            public const string StatNoteDanger = "home__stat-note--danger";
        }

        /// <summary>HomeScreen.uss の「資源の集め方」シート。</summary>
        public static class IslandGuide
        {
            public const string Lead = "island-guide__lead";
            public const string Today = "island-guide__today";
            public const string Amount = "island-guide__amount";
        }

        /// <summary>MissionScreen.uss</summary>
        public static class Mission
        {
            public const string Card = "mission__card";
            public const string CardSelected = "mission__card--selected";
            public const string CardDone = "mission__card--done";
            public const string Hint = "mission__hint";
            public const string Answers = "mission__answers";
        }

        /// <summary>Onboarding.uss</summary>
        public static class Onboarding
        {
            public const string DotActive = "onboarding__dot--active";
        }

        /// <summary>FacilityReview.uss (施設のデザイン確認用の画面。開発用)。</summary>
        public static class FacilityReview
        {
            public const string Panel = "review-panel";
            public const string Choice = "facility-choice";
            public const string ChoiceSelected = "selected";
        }
    }
}
