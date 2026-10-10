using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.World
{
    /// <summary>Review controls visible in Game view; no movement controls required.</summary>
    public sealed class FacilityDesignGallery : MonoBehaviour
    {
        [SerializeField] private Camera _camera;
        [SerializeField] private Transform[] _facilities;
        [SerializeField] private string[] _labels, _recipes;
        private int _index;
        private bool _overview, _running = true;
        private Label _title, _recipe, _action;
        private string _lastAction;
        private Button _overviewButton, _runningButton;
        private VisualElement _picker, _choices;
        public int SelectedIndex => _index;
        public string SelectedLabel => _labels[_index];
        public int FacilityCount => _facilities.Length;
        public Transform GetFacility(int index) => _facilities[index];

        public void Configure(Camera camera, Transform[] facilities, string[] labels, string[] recipes)
        { _camera = camera; _facilities = facilities; _labels = labels; _recipes = recipes; }

        private void Start()
        {
            var root = GetComponent<UIDocument>().rootVisualElement;
            var reviewPanel = root.Q<VisualElement>(className: "review-panel");
            reviewPanel.RegisterCallback<GeometryChangedEvent>(_ => FitCameraBelowControls(root, reviewPanel));
            root.RegisterCallback<GeometryChangedEvent>(_ => FitCameraBelowControls(root, reviewPanel));
            _title = root.Q<Label>("FacilityTitle"); _recipe = root.Q<Label>("FacilityRecipe");
            _action = root.Q<Label>("FacilityAction");
            root.Q<Button>("PreviousButton").clicked += () => Select(_index - 1);
            root.Q<Button>("NextButton").clicked += () => Select(_index + 1);
            _overviewButton = root.Q<Button>("OverviewButton");
            _overviewButton.clicked += () => { if (_overview) Select(_index); else ShowOverview(); };
            _runningButton = root.Q<Button>("RunningButton");
            _runningButton.clicked += () => SetRunning(!_running);
            _picker = root.Q<VisualElement>("FacilityPicker");
            _choices = root.Q<VisualElement>("FacilityChoices");
            root.Q<Button>("PickerButton").clicked += () => _picker.style.display = DisplayStyle.Flex;
            root.Q<Button>("ClosePickerButton").clicked += () => _picker.style.display = DisplayStyle.None;
            for (var i = 0; i < _facilities.Length; i++)
            {
                var facilityIndex = i;
                var button = new Button(() => Select(facilityIndex)) { text = (i + 1) + "  " + _labels[i], userData = i, name = "ChooseFacility" + i };
                button.AddToClassList("facility-choice");
                _choices.Add(button);
            }
            Select(0);
        }

        private void Update()
        {
            if (_action == null || _overview) return;
            var cycle = _facilities[_index].GetComponent<FacilityProductionCycle>();
            var text = cycle != null ? cycle.ActionLabel : _facilities[_index].GetComponent<KamabokoProductionCycle>() != null
                ? "蒸し器の蓋・蒸気・完成品を確認" : "港の建設段階";
            if (_lastAction == text) return;
            _lastAction = text;
            _action.text = text;
        }

        private void FitCameraBelowControls(VisualElement root, VisualElement panel)
        {
            if (root.resolvedStyle.height <= 0) return;
            _camera.rect = new Rect(0, 0, 1, Mathf.Clamp(1 - (panel.worldBound.yMax + 12) / root.resolvedStyle.height, .45f, 1));
            if (_overview) ShowOverview();
        }
        public void Select(int index)
        {
            _index = (index % _facilities.Length + _facilities.Length) % _facilities.Length;
            _overview = false;
            if (_picker != null) _picker.style.display = DisplayStyle.None;
            // Isolate the selected facility so its neighbour doesn't enter the close view.
            for (var i = 0; i < _facilities.Length; i++) _facilities[i].gameObject.SetActive(i == _index);
            var small = _facilities[_index].name.Contains("_1x1");
            var center = _facilities[_index].position + Vector3.up * (small ? .48f : .68f);
            _camera.orthographicSize = small ? .92f : 1.4f;
            _camera.transform.position = center + new Vector3(2.7f, 1.8f, -4.5f);
            _camera.transform.LookAt(center);
            RefreshLabels();
        }

        public void ShowOverview()
        {
            _overview = true;
            foreach (var facility in _facilities) facility.gameObject.SetActive(true);
            var bounds = new Bounds(_facilities[0].position, Vector3.zero);
            foreach (var facility in _facilities) bounds.Encapsulate(facility.position);
            var center = bounds.center;
            _camera.orthographicSize = Mathf.Max(bounds.size.z * .58f + 2, (bounds.size.x + 3) / (2 * _camera.aspect));
            _camera.transform.position = center + new Vector3(2f, 20f, -12f);
            _camera.transform.LookAt(center + Vector3.up * .4f);
            RefreshLabels();
        }

        public void SetRunning(bool running)
        {
            _running = running;
            foreach (var facility in _facilities)
            {
                var cycle = facility.GetComponent<FacilityProductionCycle>();
                if (cycle != null) cycle.SetRunning(running);
                var kamaboko = facility.GetComponent<KamabokoProductionCycle>();
                if (kamaboko != null) kamaboko.SetRunning(running);
            }
            RefreshLabels();
        }

        private void RefreshLabels()
        {
            if (_title == null) return;
            _title.text = _overview ? "施設一覧" : (_index + 1) + "/" + _facilities.Length + "  " + _labels[_index];
            _recipe.text = _overview ? "全施設の動きを比較。「施設を選ぶ」で拡大表示" : _recipes[_index];
            _overviewButton.text = _overview ? "個別表示" : "全体表示";
            _runningButton.text = _running ? "停止" : "再開";
            _lastAction = null;
            if (_action != null && _overview) _action.text = "施設ごとに異なる周期で動きます";
            if (_choices != null)
                foreach (var choice in _choices.Children()) choice.EnableInClassList("selected", !_overview && (int)choice.userData == _index);
        }
    }
}
