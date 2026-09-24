using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// Screen.safeArea をパネル座標に変換し、ノッチ・ジェスチャーバーを避ける余白を UI Toolkit の要素に反映する。
    /// 上・左・右は <c>_safeAreaName</c> の padding に、下は <c>_bottomInsetName</c> の高さに入れる
    /// (タブバーの背景を画面下端まで伸ばしたまま、ボタンだけをジェスチャーバーの上に置くため)。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class SafeAreaApplier : MonoBehaviour
    {
        [SerializeField] private string _safeAreaName = "safeArea";
        [SerializeField] private string _bottomInsetName = "bottomInset";

        private UIDocument _document;
        private VisualElement _root;
        private VisualElement _safeArea;
        private VisualElement _bottomInset;
        private Rect _appliedSafeArea;
        private Vector2Int _appliedScreenSize;

        private void OnEnable()
        {
            _document = GetComponent<UIDocument>();
            _root = _document.rootVisualElement;
            _safeArea = _root.Q(_safeAreaName);
            _bottomInset = _root.Q(_bottomInsetName);

            _appliedScreenSize = Vector2Int.zero;
            _root.RegisterCallback<GeometryChangedEvent>(OnRootGeometryChanged);
            Apply();
        }

        private void OnDisable()
        {
            _root?.UnregisterCallback<GeometryChangedEvent>(OnRootGeometryChanged);
        }

        // 回転や解像度変更ではルートの大きさが変わるので、ここで取り直せば毎フレーム監視しなくて済む。
        private void OnRootGeometryChanged(GeometryChangedEvent evt) => Apply();

        private void Apply()
        {
            var panel = _root.panel;
            if (panel == null)
            {
                return;
            }

            var safeArea = Screen.safeArea;
            var screenSize = new Vector2Int(Screen.width, Screen.height);
            if (safeArea == _appliedSafeArea && screenSize == _appliedScreenSize)
            {
                return;
            }

            _appliedSafeArea = safeArea;
            _appliedScreenSize = screenSize;

            var leftTop = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(safeArea.xMin, Screen.height - safeArea.yMax));
            var rightBottom = RuntimePanelUtils.ScreenToPanel(panel, new Vector2(Screen.width - safeArea.xMax, safeArea.yMin));

            // 端末ごとに変わる実測値なので USS では表せず、インラインスタイルで入れる。
            if (_safeArea != null)
            {
                _safeArea.style.paddingTop = leftTop.y;
                _safeArea.style.paddingLeft = leftTop.x;
                _safeArea.style.paddingRight = rightBottom.x;
            }

            if (_bottomInset != null)
            {
                _bottomInset.style.height = rightBottom.y;
            }
        }
    }
}
