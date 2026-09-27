using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    public enum AppScreen
    {
        Home,
        Scan,
    }

    /// <summary>
    /// App.uxml に並べた画面のうち 1 つだけを表示する。シーンを分けずに画面を切り替えるための入口。
    /// 非表示の画面は破棄せず <see cref="HiddenClass"/> で隠すだけなので、戻ったときに状態が残る。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class ScreenNavigator : MonoBehaviour
    {
        private const string HiddenClass = "pp-screen--hidden";

        [Tooltip("スキャン画面の表示中に止める 3D ワールドのカメラ。不透明な画面の裏で描画し続けないため")]
        [SerializeField] private Camera _worldCamera;

        [SerializeField] private ReceiptCameraPreview _cameraPreview;

        private VisualElement _homeScreen;
        private VisualElement _scanScreen;
        private Button _scanTab;
        private Button _closeScanButton;

        public AppScreen Current { get; private set; }

        private void OnEnable()
        {
            var root = GetComponent<UIDocument>().rootVisualElement;
            _homeScreen = root.Q("homeScreen");
            _scanScreen = root.Q("scanScreen");
            _scanTab = _homeScreen.Q<Button>("tabScan");
            _closeScanButton = _scanScreen.Q<Button>("closeButton");

            _scanTab.clicked += ShowScan;
            _closeScanButton.clicked += ShowHome;

            Show(AppScreen.Home);
        }

        private void OnDisable()
        {
            if (_scanTab != null)
            {
                _scanTab.clicked -= ShowScan;
            }

            if (_closeScanButton != null)
            {
                _closeScanButton.clicked -= ShowHome;
            }
        }

        private void Update()
        {
            // Android の戻るキーは Input System では Escape キーとして届く。
            var keyboard = Keyboard.current;
            if (Current != AppScreen.Home && keyboard != null && keyboard.escapeKey.wasPressedThisFrame)
            {
                Show(AppScreen.Home);
            }
        }

        public void Show(AppScreen screen)
        {
            Current = screen;
            _homeScreen.EnableInClassList(HiddenClass, screen != AppScreen.Home);
            _scanScreen.EnableInClassList(HiddenClass, screen != AppScreen.Scan);

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
        }

        private void ShowHome() => Show(AppScreen.Home);

        private void ShowScan() => Show(AppScreen.Scan);
    }
}
