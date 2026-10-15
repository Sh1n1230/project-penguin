using System.Collections.Generic;
using System.Globalization;
using ProjectPenguin.Domain.Game;
using ProjectPenguin.Domain.World;
using ProjectPenguin.Systems;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// ホーム画面の氷の量のカードとペンギンの吹き出しを、ゲームの状態 (<see cref="GameStateSystem"/>) に合わせる。
    /// CO₂ のカードは採点ができるまで仮の値のまま。
    /// 開発ビルドと Editor では、ダミーの記録と時計の早送りの操作を出す。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class HomeStatusPresenter : MonoBehaviour
    {
        private const string DemoVisibleClass = "home__demo--visible";

        [SerializeField] private GameStateSystem _game;

        private readonly Queue<string> _recentLines = new();
        private int _iceLowShownDay = int.MinValue;
        private bool _shownOnce;

        private ProgressBar _iceProgress;
        private Label _iceValue;
        private Label _speech;
        private VisualElement _demo;
        private Label _demoBadge;
        private Button _demoRecord;
        private Button _demoAdvance;

        private void OnEnable()
        {
            if (_game == null)
            {
                Debug.LogError($"{nameof(HomeStatusPresenter)}: {nameof(GameStateSystem)} が未設定です。", this);
                enabled = false;
                return;
            }

            var home = GetComponent<UIDocument>().rootVisualElement.Q(ScreenNavigator.ElementNameOf(AppScreen.Home));
            _iceProgress = home.Q<ProgressBar>("iceProgress");
            _iceValue = home.Q<Label>("iceValue");
            _speech = home.Q<Label>("speechText");
            _demo = home.Q("demoControls");
            _demoBadge = home.Q<Label>("demoBadge");
            _demoRecord = home.Q<Button>("demoRecordButton");
            _demoAdvance = home.Q<Button>("demoAdvanceButton");

            _game.Changed += OnChanged;
            BindDemoControls(true);
            _game.Refresh();
        }

        private void OnDisable()
        {
            if (_game != null)
            {
                _game.Changed -= OnChanged;
            }

            BindDemoControls(false);
        }

        private void BindDemoControls(bool bind)
        {
#if DEVELOPMENT_BUILD || UNITY_EDITOR
            if (_demo == null)
            {
                return;
            }

            _demo.EnableInClassList(DemoVisibleClass, bind);
            if (bind)
            {
                _demoRecord.clicked += RecordSample;
                _demoAdvance.clicked += AdvanceOneDay;
            }
            else
            {
                _demoRecord.clicked -= RecordSample;
                _demoAdvance.clicked -= AdvanceOneDay;
            }
#endif
        }

        private void RecordSample() => _game.RecordSampleReceipt();

#if DEVELOPMENT_BUILD || UNITY_EDITOR
        private void AdvanceOneDay() => _game.AdvanceDays(1);
#else
        private void AdvanceOneDay()
        {
        }
#endif

        private void OnChanged(GameStateChange change)
        {
            var state = change.After;
            ShowIce(state);
            ShowSpeech(change);

            if (_demoBadge != null)
            {
                var days = _game.DemoDaysAdvanced;
                _demoBadge.text = days > 0 ? $"デモ用：{days} 日進めています" : "デモ用の操作";
            }
        }

        private void ShowIce(HomeState state)
        {
            // 氷の値は下限 40〜上限 150。メーターは上限に対する割合で見せる。
            _iceProgress.value = (float)(state.Ice / GameParameters.Default.Cap * 100.0);
            _iceValue.text = state.Ice.ToString("0", CultureInfo.InvariantCulture);
        }

        private void ShowSpeech(GameStateChange change)
        {
            // 何も起きていない再描画 (同じ日のうちの復帰など) では、今の行を出し続ける。
            if (_shownOnce && change.Events == SpeechEvent.None && !change.IsFirstOpenToday && !change.IsComeback)
            {
                return;
            }

            _shownOnce = true;
            var state = change.After;
            var context = new SpeechContext(
                state.Tier,
                PenguinSpeech.DayPartOf(_game.Now),
                change.Events,
                change.IsComeback,
                change.IsFirstOpenToday,
                state.LastRecord,
                _iceLowShownDay == state.Day);
            var line = PenguinSpeech.Pick(context, _recentLines, n => Random.Range(0, n));
            _speech.text = line.Text;
            _recentLines.Enqueue(line.Id);
            while (_recentLines.Count > PenguinSpeech.RecentLimit)
            {
                _recentLines.Dequeue();
            }

            if (line.Category == SpeechCategory.IceLow)
            {
                _iceLowShownDay = state.Day;
            }
        }
    }
}
