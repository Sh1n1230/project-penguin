using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    public enum AppScreen
    {
        Home,
        Record,
        Mission,
        Scan,
        Analyzing,
        Result,
        Menu,
    }

    /// <summary>
    /// App.uxml に並べた画面のうち 1 つだけを表示する。シーンを分けずに画面を切り替えるための入口。
    /// 非表示の画面は破棄せず <see cref="HiddenClass"/> で隠すだけなので、戻ったときに状態が残る。
    /// 画面構成と遷移の考え方は docs/ui-structure.md を参照。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class ScreenNavigator : MonoBehaviour
    {
        public const string TabBarName = "tabBar";

        private const string HiddenClass = "pp-screen--hidden";
        private const string ActiveTabClass = "pp-tab--active";

        /// <summary>
        /// ボタンと行き先の対応。<see cref="Scope"/> の要素の中から <see cref="Button"/> を探す
        /// (closeButton のように画面をまたいで同じ名前があるため)。
        /// <see cref="Target"/> が null のボタンは直前のタブ画面へ戻る。
        /// </summary>
        public readonly struct Route
        {
            public Route(string scope, string button, AppScreen? target)
            {
                Scope = scope;
                Button = button;
                Target = target;
            }

            public string Scope { get; }
            public string Button { get; }
            public AppScreen? Target { get; }
        }

        public static readonly IReadOnlyList<Route> Routes = new[]
        {
            new Route(TabBarName, "tabHome", AppScreen.Home),
            new Route(TabBarName, "tabRecord", AppScreen.Record),
            new Route(TabBarName, "tabScan", AppScreen.Scan),
            new Route(TabBarName, "tabMission", AppScreen.Mission),
            new Route(TabBarName, "tabMenu", AppScreen.Menu),
            new Route(ElementNameOf(AppScreen.Scan), "closeButton", AppScreen.Home),
            new Route(ElementNameOf(AppScreen.Scan), "shutterButton", AppScreen.Analyzing),
            new Route(ElementNameOf(AppScreen.Analyzing), "closeButton", AppScreen.Home),
            new Route(ElementNameOf(AppScreen.Result), "backButton", AppScreen.Home),
            new Route(ElementNameOf(AppScreen.Result), "applyButton", AppScreen.Home),
            new Route(ElementNameOf(AppScreen.Menu), "closeBand", null),
            new Route(ElementNameOf(AppScreen.Menu), "menuRecord", AppScreen.Record),
            new Route(ElementNameOf(AppScreen.Menu), "menuMission", AppScreen.Mission),
        };

        [Tooltip("ホーム以外の不透明な画面の表示中に止める 3D ワールドのカメラ。見えない世界を描画し続けないため")]
        [SerializeField] private Camera _worldCamera;

        [SerializeField] private ReceiptCameraPreview _cameraPreview;

        [Tooltip("未設定なら解析中画面を飛ばして結果画面を出す")]
        [SerializeField] private AnalyzingScreenPresenter _analyzingPresenter;

        private readonly Dictionary<AppScreen, VisualElement> _screens = new();
        private readonly Dictionary<AppScreen, Button> _tabButtons = new();
        private readonly List<(Button Button, Action Handler)> _bindings = new();
        private VisualElement _tabBar;
        private AppScreen _lastTab = AppScreen.Home;

        public AppScreen Current { get; private set; }

        public static string ElementNameOf(AppScreen screen) => screen switch
        {
            AppScreen.Home => "homeScreen",
            AppScreen.Record => "recordScreen",
            AppScreen.Mission => "missionScreen",
            AppScreen.Scan => "scanScreen",
            AppScreen.Analyzing => "analyzingScreen",
            AppScreen.Result => "resultScreen",
            AppScreen.Menu => "menuScreen",
            _ => throw new ArgumentOutOfRangeException(nameof(screen), screen, null),
        };

        /// <summary>タブバーを出す画面と、そのときアクティブにするタブ。タブ画面でなければ null。</summary>
        public static string TabButtonOf(AppScreen screen) => screen switch
        {
            AppScreen.Home => "tabHome",
            AppScreen.Record => "tabRecord",
            AppScreen.Mission => "tabMission",
            _ => null,
        };

        private void OnEnable()
        {
            var root = GetComponent<UIDocument>().rootVisualElement;

            foreach (AppScreen screen in Enum.GetValues(typeof(AppScreen)))
            {
                _screens[screen] = Require(root, ElementNameOf(screen));

                var tabName = TabButtonOf(screen);
                if (tabName != null)
                {
                    _tabButtons[screen] = Require<Button>(root, tabName);
                }
            }

            _tabBar = Require(root, TabBarName);

            foreach (var route in Routes)
            {
                var button = Require<Button>(Require(root, route.Scope), route.Button);
                var target = route.Target;
                Action handler = target.HasValue ? () => Show(target.Value) : () => Show(_lastTab);
                button.clicked += handler;
                _bindings.Add((button, handler));
            }

            Show(AppScreen.Home);
        }

        private void OnDisable()
        {
            foreach (var (button, handler) in _bindings)
            {
                button.clicked -= handler;
            }

            _bindings.Clear();
            _screens.Clear();
            _tabButtons.Clear();
        }

        private void Update()
        {
            // Android の戻るキーは Input System では Escape キーとして届く。
            var keyboard = Keyboard.current;
            if (keyboard != null && keyboard.escapeKey.wasPressedThisFrame)
            {
                Back();
            }
        }

        public void Show(AppScreen screen)
        {
            var previous = Current;
            Current = screen;

            foreach (var (key, element) in _screens)
            {
                element.EnableInClassList(HiddenClass, key != screen);
            }

            var isTab = TabButtonOf(screen) != null;
            _tabBar.EnableInClassList(HiddenClass, !isTab);
            if (isTab)
            {
                _lastTab = screen;
                foreach (var (key, tab) in _tabButtons)
                {
                    tab.EnableInClassList(ActiveTabClass, key == screen);
                }
            }

            if (_worldCamera != null)
            {
                _worldCamera.enabled = screen == AppScreen.Home;
            }

            // カメラはスキャン画面を開いている間だけ起動する (電池とプライバシーのため)。
            if (_cameraPreview != null)
            {
                if (screen == AppScreen.Scan)
                {
                    _cameraPreview.StartPreview();
                }
                else
                {
                    _cameraPreview.StopPreview();
                }
            }

            if (previous == AppScreen.Analyzing && screen != AppScreen.Analyzing && _analyzingPresenter != null)
            {
                _analyzingPresenter.Cancel();
            }

            if (screen == AppScreen.Analyzing)
            {
                if (_analyzingPresenter != null)
                {
                    _analyzingPresenter.Begin(() => Show(AppScreen.Result));
                }
                else
                {
                    Show(AppScreen.Result);
                }
            }
        }

        /// <summary>戻るキー。フローの途中とタブ画面はホームへ、メニューは開く前のタブへ戻る。</summary>
        public void Back()
        {
            switch (Current)
            {
                case AppScreen.Home:
                    return;
                case AppScreen.Menu:
                    Show(_lastTab);
                    return;
                default:
                    Show(AppScreen.Home);
                    return;
            }
        }

        private static VisualElement Require(VisualElement scope, string name) =>
            scope.Q(name) ?? throw new InvalidOperationException($"App.uxml に '{name}' という要素がありません");

        private static T Require<T>(VisualElement scope, string name) where T : VisualElement =>
            scope.Q<T>(name) ?? throw new InvalidOperationException($"App.uxml に '{name}' という {typeof(T).Name} がありません");
    }
}
