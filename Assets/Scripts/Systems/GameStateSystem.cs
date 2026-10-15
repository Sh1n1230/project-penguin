using System;
using ProjectPenguin.Domain.Clock;
using ProjectPenguin.Domain.Game;
using ProjectPenguin.Domain.World;
using UnityEngine;

namespace ProjectPenguin.Systems
{
    /// <summary>操作の前後のホームの状態。</summary>
    public readonly struct GameStateChange
    {
        public GameStateChange(HomeState before, HomeState after, bool isComeback, bool isFirstOpenToday)
        {
            Before = before;
            After = after;
            IsComeback = isComeback;
            IsFirstOpenToday = isFirstOpenToday;
        }

        public HomeState Before { get; }
        public HomeState After { get; }

        /// <summary>前回開いてから 3 日以上あいた。</summary>
        public bool IsComeback { get; }

        /// <summary>この操作がその日に初めて開いたとき。</summary>
        public bool IsFirstOpenToday { get; }

        public SpeechEvent Events => HomeState.EventsBetween(Before, After);
    }

    /// <summary>
    /// ゲームの状態 (<see cref="GameSession"/>) を持ち、起動・復帰・操作のたびに日を進めて変化を知らせる。
    /// 計算は Domain が行い、ここは時計を渡して呼ぶだけ (.claude/rules/unity.md)。
    ///
    /// 保存はまだ無い (SQLite は Hack Day で作る)。アプリを再起動すると初期状態から始まる。
    /// </summary>
    public sealed class GameStateSystem : MonoBehaviour
    {
        /// <summary>この日数以上あけて開いたら「おかえり」(15c §2.2)。</summary>
        public const int ComebackDays = 3;

        private OffsetClock _clock;
        private GameSession _session;
        private int _lastOpenDay;

        /// <summary>状態が変わりうる操作のたびに呼ばれる (変化が無くても呼ぶ)。</summary>
        public event Action<GameStateChange> Changed;

        public GameSession Session
        {
            get
            {
                EnsureCreated();
                return _session;
            }
        }

        public HomeState Current => HomeState.Of(Session);

        /// <summary>今の時刻。開発ビルドで「時間を進める」を押した分を含む。</summary>
        public DateTimeOffset Now
        {
            get
            {
                EnsureCreated();
                return _clock.UtcNow;
            }
        }

        /// <summary>「時間を進める」で進めた日数。0 でなければ画面に「デモ用」と出す。</summary>
        public int DemoDaysAdvanced => _clock == null ? 0 : (int)_clock.Offset.TotalDays;

        // 他のコンポーネントの OnEnable が先に呼ばれても使えるよう、最初に触られたときに作る。
        private void EnsureCreated()
        {
            if (_session != null)
            {
                return;
            }

            _clock = new OffsetClock(new SystemClock());
            _session = new GameSession(_clock, NoWeeklyBonus);

            // 起動した日を「その日に初めて開いた」として挨拶させるため、前日に開いたことにしておく。
            _lastOpenDay = _session.Today - 1;
        }

        private void OnApplicationPause(bool paused)
        {
            // 閉じている間の進行 (氷の融解など) は、復帰時に経過日数からまとめて計算する。
            if (!paused)
            {
                Refresh();
            }
        }

        /// <summary>経過した日を確定させて今日を始める。起動・復帰・画面を開いたときに呼ぶ。</summary>
        public void Refresh()
        {
            Apply(() => _session.Advance());
        }

        /// <summary>
        /// 見本のレシートを 1 枚記録する (ダミーデータ)。中身の解析と採点は Hack Day で作るので、
        /// 今は「今日レシートを記録した」ことだけを伝える。
        /// </summary>
        public bool RecordSampleReceipt()
        {
            var result = false;
            Apply(() => result = _session.ScanReceipt(new ReceiptRecord("sample-" + Guid.NewGuid().ToString("N"), _session.Today)));
            return result;
        }

#if DEVELOPMENT_BUILD || UNITY_EDITOR
        /// <summary>デモ用に時計を進める。開発ビルドと Editor だけ。</summary>
        public void AdvanceDays(int days)
        {
            if (days <= 0)
            {
                return;
            }

            EnsureCreated();
            _clock.AdvanceDays(days);
            Refresh();
        }
#endif

        private void Apply(Action action)
        {
            EnsureCreated();
            var before = HomeState.Of(_session);
            action();
            var today = _session.Today;
            var isFirstOpenToday = today > _lastOpenDay;
            var isComeback = today - _lastOpenDay >= ComebackDays;
            _lastOpenDay = Math.Max(_lastOpenDay, today);
            Changed?.Invoke(new GameStateChange(before, HomeState.Of(_session), isComeback, isFirstOpenToday));
        }

        /// <summary>週の選び方の氷 B。レシートの採点ができるまでは 0。</summary>
        private static double NoWeeklyBonus(int week, System.Collections.Generic.IReadOnlyList<ReceiptRecord> receipts)
        {
            return 0.0;
        }
    }
}
