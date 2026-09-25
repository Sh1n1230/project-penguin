using System.Globalization;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// 記録画面の CO₂ グラフを描く。今は仮の値で、SQLite の記録とつなぐときに値の出どころを差し替える。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class RecordScreenPresenter : MonoBehaviour
    {
        private const string ColumnClass = "pp-bar-chart__col";
        private const string BarClass = "pp-bar-chart__bar";
        private const string ValueClass = "pp-bar-chart__value";

        // 月〜日の CO₂e (kg)。仮データ。
        private static readonly float[] PlaceholderWeek = { 0.9f, 1.2f, 1.4f, 0.8f, 1.3f, 1.1f, 0.84f };

        private void OnEnable()
        {
            var screen = GetComponent<UIDocument>().rootVisualElement.Q(ScreenNavigator.ElementNameOf(AppScreen.Record));
            ShowWeek(screen.Q("co2Chart"), PlaceholderWeek);
        }

        private static void ShowWeek(VisualElement chart, float[] values)
        {
            var max = Mathf.Max(values);
            var columns = chart.Query(className: ColumnClass).ToList();
            for (var i = 0; i < columns.Count && i < values.Length; i++)
            {
                // 棒の高さはデータ次第で USS に書けないため、ここでだけ style に入れる。
                columns[i].Q(className: BarClass).style.height = Length.Percent(max > 0f ? values[i] / max * 100f : 0f);
                columns[i].Q<Label>(className: ValueClass).text = values[i].ToString("0.0", CultureInfo.InvariantCulture);
            }
        }
    }
}
