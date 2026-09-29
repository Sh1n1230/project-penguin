using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// 解析中画面の 3 段階 (読み取り → 分類 → CO₂ 計算) の進み具合を表示する。
    /// 今はバックエンドにつながっていないので、一定時間ごとに段階を進める仮の実装。
    /// FastAPI のクライアントができたら、<see cref="Begin"/> の中身をその応答待ちに差し替える。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class AnalyzingScreenPresenter : MonoBehaviour
    {
        private const string ActiveClass = "pp-step--active";
        private const string DoneClass = "pp-step--done";

        private static readonly string[] StepNames = { "stepRead", "stepClassify", "stepCalculate" };

        [Tooltip("仮の進行で 1 段階にかける秒数")]
        [SerializeField] private float _secondsPerStep = 0.8f;

        private VisualElement[] _steps;
        private Coroutine _routine;

        private void OnEnable()
        {
            var screen = GetComponent<UIDocument>().rootVisualElement.Q(ScreenNavigator.ElementNameOf(AppScreen.Analyzing));
            _steps = new VisualElement[StepNames.Length];
            for (var i = 0; i < StepNames.Length; i++)
            {
                _steps[i] = screen.Q(StepNames[i]);
            }
        }

        private void OnDisable() => Cancel();

        /// <summary>最初の段階から進め、すべて終わったら <paramref name="onCompleted"/> を呼ぶ。</summary>
        public void Begin(Action onCompleted)
        {
            Cancel();
            _routine = StartCoroutine(Run(onCompleted));
        }

        /// <summary>途中でやめる。表示は最初の状態に戻す。</summary>
        public void Cancel()
        {
            if (_routine != null)
            {
                StopCoroutine(_routine);
                _routine = null;
            }

            ShowStep(-1);
        }

        private IEnumerator Run(Action onCompleted)
        {
            for (var i = 0; i < _steps.Length; i++)
            {
                ShowStep(i);
                yield return new WaitForSeconds(_secondsPerStep);
            }

            ShowStep(_steps.Length);
            yield return new WaitForSeconds(_secondsPerStep / 2f);

            _routine = null;
            onCompleted?.Invoke();
        }

        // current より前は完了、current は進行中、それ以降は未着手。-1 ならすべて未着手。
        private void ShowStep(int current)
        {
            if (_steps == null)
            {
                return;
            }

            for (var i = 0; i < _steps.Length; i++)
            {
                _steps[i].EnableInClassList(DoneClass, current >= 0 && i < current);
                _steps[i].EnableInClassList(ActiveClass, i == current);
            }
        }
    }
}
