using System;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>この名前の定数が、指定した UXML に要素名として実在することを UiNamesTests が確かめる。</summary>
    [AttributeUsage(AttributeTargets.Class)]
    public sealed class UxmlFileAttribute : Attribute
    {
        public UxmlFileAttribute(string path) => Path = path;

        public string Path { get; }
    }

    /// <summary>
    /// UXML の要素名 (name 属性)。<c>Q("islandBar")</c> のように文字列で書かず、ここの定数を使う。
    /// UXML ごとに入れ子のクラスを 1 つ置く。UXML に要素を足したり名前を変えたりしたら、ここも直す
    /// (食い違うと EditMode の UiNamesTests が落ちる)。
    /// </summary>
    public static class UiNames
    {
        /// <summary>画面の入れ物 (各画面の Instance とタブバー・はじめての案内)。<c>Assets/UI/App/App.uxml</c></summary>
        [UxmlFile("Assets/UI/App/App.uxml")]
        public static class App
        {
            public const string AppRoot = "app";
            public const string HomeScreen = "homeScreen";
            public const string RecordScreen = "recordScreen";
            public const string MissionScreen = "missionScreen";
            public const string ScanScreen = "scanScreen";
            public const string AnalyzingScreen = "analyzingScreen";
            public const string ResultScreen = "resultScreen";
            public const string MenuScreen = "menuScreen";
            public const string DexScreen = "dexScreen";
            public const string TabBar = "tabBar";
            public const string Onboarding = "onboarding";
        }

        /// <summary>下のタブ。<c>Assets/UI/App/TabBar.uxml</c></summary>
        [UxmlFile("Assets/UI/App/TabBar.uxml")]
        public static class TabBar
        {
            public const string TabBarRoot = "tabBarRoot";
            public const string TabHome = "tabHome";
            public const string TabRecord = "tabRecord";
            public const string TabScan = "tabScan";
            public const string TabMission = "tabMission";
            public const string TabMenu = "tabMenu";
        }

        /// <summary>ホーム (島の HUD・シート・知らせ)。<c>Assets/UI/Screens/Home/HomeScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Home/HomeScreen.uxml")]
        public static class Home
        {
            public const string Root = "root";
            public const string SafeArea = "safeArea";
            public const string Header = "header";
            public const string IslandBar = "islandBar";
            public const string Level = "level";
            public const string LevelValue = "levelValue";
            public const string ResFish = "resFish";
            public const string ResFishValue = "resFishValue";
            public const string ResElectricity = "resElectricity";
            public const string ResElectricityValue = "resElectricityValue";
            public const string ResWater = "resWater";
            public const string ResWaterValue = "resWaterValue";
            public const string ResGas = "resGas";
            public const string ResGasValue = "resGasValue";
            public const string ResAllMighty = "resAllMighty";
            public const string ResAllMightyValue = "resAllMightyValue";
            public const string SettingsButton = "settingsButton";
            public const string Stats = "stats";
            public const string IceStat = "iceStat";
            public const string IceLabel = "iceLabel";
            public const string IceProgress = "iceProgress";
            public const string IceValue = "iceValue";
            public const string LandValue = "landValue";
            public const string WeekStat = "weekStat";
            public const string TodayIcon = "todayIcon";
            public const string WeekLabel = "weekLabel";
            public const string WeekProgress = "weekProgress";
            public const string WeekValue = "weekValue";
            public const string DemoControls = "demoControls";
            public const string DemoBadge = "demoBadge";
            public const string DemoRecordButton = "demoRecordButton";
            public const string DemoAdvanceButton = "demoAdvanceButton";
            public const string DemoHourButton = "demoHourButton";
            public const string DemoGrantButton = "demoGrantButton";
            public const string DemoStepsButton = "demoStepsButton";
            public const string WorldViewport = "worldViewport";
            public const string PlacementBanner = "placementBanner";
            public const string BannerIcon = "bannerIcon";
            public const string BannerText = "bannerText";
            public const string BannerCancel = "bannerCancel";
            public const string BannerConfirm = "bannerConfirm";
            public const string Tools = "tools";
            public const string ToolBuild = "toolBuild";
            public const string ToolHarbor = "toolHarbor";
            public const string HarborDot = "harborDot";
            public const string ToolProduction = "toolProduction";
            public const string Speech = "speech";
            public const string SpeechText = "speechText";
            public const string NextActionButton = "nextActionButton";
            public const string NextActionIcon = "nextActionIcon";
            public const string NextActionLabel = "nextActionLabel";
            public const string GainLayer = "gainLayer";
            public const string ToastLayer = "toastLayer";
            public const string Sheet = "sheet";
            public const string SheetScrim = "sheetScrim";
            public const string SheetPanel = "sheetPanel";
            public const string SheetTitle = "sheetTitle";
            public const string SheetClose = "sheetClose";
            public const string SheetBody = "sheetBody";
            public const string SheetFooter = "sheetFooter";
            public const string Modal = "modal";
            public const string ModalTitle = "modalTitle";
            public const string ModalText = "modalText";
            public const string ModalBody = "modalBody";
            public const string ModalButton = "modalButton";
            public const string ModalCancel = "modalCancel";
        }

        /// <summary>エコ写真の撮影。<c>Assets/UI/Screens/Scan/ScanScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Scan/ScanScreen.uxml")]
        public static class Scan
        {
            public const string Root = "root";
            public const string PreviewViewport = "previewViewport";
            public const string CameraPreview = "cameraPreview";
            public const string CloseButton = "closeButton";
            public const string ScanGuide = "scanGuide";
            public const string ScanFrame = "scanFrame";
            public const string CameraStatus = "cameraStatus";
            public const string ShutterButton = "shutterButton";
        }

        /// <summary>写真の判定中。<c>Assets/UI/Screens/Analyzing/AnalyzingScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Analyzing/AnalyzingScreen.uxml")]
        public static class Analyzing
        {
            public const string Root = "root";
            public const string CloseButton = "closeButton";
            public const string AnalyzingCaption = "analyzingCaption";
            public const string Steps = "steps";
            public const string StepRead = "stepRead";
            public const string StepClassify = "stepClassify";
            public const string StepCalculate = "stepCalculate";
        }

        /// <summary>写真の判定の結果。<c>Assets/UI/Screens/Result/ResultScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Result/ResultScreen.uxml")]
        public static class Result
        {
            public const string Root = "root";
            public const string BackButton = "backButton";
            public const string CategoryBadge = "categoryBadge";
            public const string CategoryIcon = "categoryIcon";
            public const string ScannedAt = "scannedAt";
            public const string PhotoLabel = "photoLabel";
            public const string CategoryName = "categoryName";
            public const string CommentText = "commentText";
            public const string GrantTitle = "grantTitle";
            public const string GrantList = "grantList";
            public const string RecordCard = "recordCard";
            public const string RecordTitle = "recordTitle";
            public const string IceGain = "iceGain";
            public const string RecordNote = "recordNote";
            public const string TipText = "tipText";
            public const string ApplyButton = "applyButton";
        }

        /// <summary>記録。<c>Assets/UI/Screens/Record/RecordScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Record/RecordScreen.uxml")]
        public static class Record
        {
            public const string Root = "root";
            public const string WeekSummary = "weekSummary";
            public const string ResourceChart = "resourceChart";
            public const string TotalValue = "totalValue";
            public const string StreakValue = "streakValue";
            public const string PenguinValue = "penguinValue";
            public const string DeliveredValue = "deliveredValue";
            public const string History = "history";
        }

        /// <summary>ミッション。<c>Assets/UI/Screens/Mission/MissionScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Mission/MissionScreen.uxml")]
        public static class Mission
        {
            public const string Root = "root";
            public const string MissionContent = "missionContent";
            public const string MissionSpeech = "missionSpeech";
            public const string SelectionCount = "selectionCount";
            public const string MissionList = "missionList";
        }

        /// <summary>メニュー。<c>Assets/UI/Screens/Menu/MenuScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Menu/MenuScreen.uxml")]
        public static class Menu
        {
            public const string Root = "root";
            public const string MenuPlayer = "menuPlayer";
            public const string MenuPokedex = "menuPokedex";
            public const string MenuRecord = "menuRecord";
            public const string MenuMission = "menuMission";
            public const string MenuHelp = "menuHelp";
            public const string MenuCamera = "menuCamera";
            public const string MenuReset = "menuReset";
            public const string CloseBand = "closeBand";
            public const string MenuModal = "menuModal";
            public const string MenuModalTitle = "menuModalTitle";
            public const string MenuModalText = "menuModalText";
            public const string MenuModalOk = "menuModalOk";
            public const string MenuModalCancel = "menuModalCancel";
        }

        /// <summary>図鑑。<c>Assets/UI/Screens/Dex/DexScreen.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Dex/DexScreen.uxml")]
        public static class Dex
        {
            public const string Root = "root";
            public const string BackButton = "backButton";
            public const string DexCount = "dexCount";
            public const string DexHint = "dexHint";
            public const string DexGrid = "dexGrid";
        }

        /// <summary>はじめての案内。<c>Assets/UI/Screens/Onboarding/Onboarding.uxml</c></summary>
        [UxmlFile("Assets/UI/Screens/Onboarding/Onboarding.uxml")]
        public static class Onboarding
        {
            public const string Root = "root";
            public const string Dot0 = "dot0";
            public const string Dot1 = "dot1";
            public const string Dot2 = "dot2";
            public const string Dot3 = "dot3";
            public const string Page0 = "page0";
            public const string IslandName = "islandName";
            public const string Page1 = "page1";
            public const string Page2 = "page2";
            public const string Page3 = "page3";
            public const string OnboardingNext = "onboardingNext";
            public const string OnboardingLater = "onboardingLater";
        }

        /// <summary>施設のデザイン確認用の画面 (開発用)。<c>Assets/UI/ProductionIslandReview/FacilityReview.uxml</c></summary>
        [UxmlFile("Assets/UI/ProductionIslandReview/FacilityReview.uxml")]
        public static class FacilityReview
        {
            public const string FacilityTitle = "FacilityTitle";
            public const string FacilityRecipe = "FacilityRecipe";
            public const string FacilityAction = "FacilityAction";
            public const string PickerButton = "PickerButton";
            public const string PreviousButton = "PreviousButton";
            public const string NextButton = "NextButton";
            public const string OverviewButton = "OverviewButton";
            public const string RunningButton = "RunningButton";
            public const string FacilityPicker = "FacilityPicker";
            public const string ClosePickerButton = "ClosePickerButton";
            public const string FacilityChoices = "FacilityChoices";
        }
    }
}
