using ProjectPenguin.Systems;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// はじめての起動の案内 (docs/game-logic.md §7)。名前 → 3 つの決まり → 資源の集め方 → 最初の写真。
    /// 終わったら保存し、次からは出さない。データを消したときはまた出す。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class OnboardingPresenter : MonoBehaviour
    {
        private static readonly string[] PageNames =
            { UiNames.Onboarding.Page0, UiNames.Onboarding.Page1, UiNames.Onboarding.Page2, UiNames.Onboarding.Page3 };

        private static readonly string[] DotNames =
            { UiNames.Onboarding.Dot0, UiNames.Onboarding.Dot1, UiNames.Onboarding.Dot2, UiNames.Onboarding.Dot3 };

        private static int PageCount => PageNames.Length;

        [SerializeField] private GameStateSystem _game;
        [SerializeField] private ScreenNavigator _navigator;

        private VisualElement _overlay;
        private VisualElement[] _pages;
        private VisualElement[] _dots;
        private Button _next;
        private Button _later;
        private TextField _name;
        private int _page;

        private void OnEnable()
        {
            if (_game == null || _navigator == null)
            {
                Debug.LogError($"{nameof(OnboardingPresenter)}: 参照が未設定です。", this);
                enabled = false;
                return;
            }

            _overlay = GetComponent<UIDocument>().rootVisualElement.Q(UiNames.App.Onboarding);
            _pages = new VisualElement[PageCount];
            _dots = new VisualElement[PageCount];
            for (var i = 0; i < PageCount; i++)
            {
                _pages[i] = _overlay.Q(PageNames[i]);
                _dots[i] = _overlay.Q(DotNames[i]);
            }

            _next = _overlay.Q<Button>(UiNames.Onboarding.OnboardingNext);
            _later = _overlay.Q<Button>(UiNames.Onboarding.OnboardingLater);
            _name = _overlay.Q<TextField>(UiNames.Onboarding.IslandName);
            _next.clicked += Next;
            _later.clicked += Later;
            ShowIfNeeded();
        }

        private void OnDisable()
        {
            if (_next != null)
            {
                _next.clicked -= Next;
                _later.clicked -= Later;
            }
        }

        /// <summary>まだ案内を終えていなければ出す (データを消した後も呼ぶ)。</summary>
        public void ShowIfNeeded()
        {
            if (_overlay == null || _game.Onboarded)
            {
                IslandUi.SetVisible(_overlay, false);
                return;
            }

            _name.value = "";
            Show(0);
            IslandUi.SetVisible(_overlay, true);
        }

        private void Show(int page)
        {
            _page = page;
            for (var i = 0; i < PageCount; i++)
            {
                IslandUi.SetVisible(_pages[i], i == page);
                _dots[i].EnableInClassList(UiClasses.Onboarding.DotActive, i == page);
            }

            var last = page == PageCount - 1;
            _next.text = last ? "エコ写真を撮る" : "次へ";
            IslandUi.SetVisible(_later, last);
        }

        private void Next()
        {
            if (_page < PageCount - 1)
            {
                Show(_page + 1);
                return;
            }

            Finish();
            _navigator.Show(AppScreen.Scan);
        }

        private void Later()
        {
            Finish();
            _navigator.Show(AppScreen.Home);
        }

        private void Finish()
        {
            _game.CompleteOnboarding(_name.value);
            IslandUi.SetVisible(_overlay, false);
        }
    }
}
