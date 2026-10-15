using System;

namespace ProjectPenguin.Domain.Clock
{
    /// <summary>
    /// 現在時刻の注入口。Domain は DateTime.Now / UtcNow を直接呼ばない (.claude/rules/unity.md)。
    /// 本番は Systems 側で DateTimeOffset.UtcNow を返す実装を渡し、デモと EditMode テストは <see cref="ManualClock"/> を渡す。
    /// </summary>
    public interface IClock
    {
        /// <summary>現在の UTC 時刻。</summary>
        DateTimeOffset UtcNow { get; }
    }

    /// <summary>
    /// 手で進める時計。EditMode テストと、Development ビルドの「時間を進める」ボタン用。
    /// 自分では現在時刻を読まないので、開始時刻は呼び出し側が渡す。
    /// </summary>
    public sealed class ManualClock : IClock
    {
        public ManualClock(DateTimeOffset start)
        {
            UtcNow = start.ToUniversalTime();
        }

        public DateTimeOffset UtcNow { get; private set; }

        public void Advance(TimeSpan delta)
        {
            if (delta < TimeSpan.Zero)
            {
                throw new ArgumentOutOfRangeException(nameof(delta), delta, "ManualClock only moves forward");
            }

            UtcNow = UtcNow + delta;
        }

        public void AdvanceDays(int days)
        {
            Advance(TimeSpan.FromDays(days));
        }

        public void Set(DateTimeOffset utcNow)
        {
            UtcNow = utcNow.ToUniversalTime();
        }
    }

    /// <summary>
    /// 早送りできる時計。実時計 (inner) に、デモで進めた分のずれを足して返す。
    /// 「時間を進める」を押したあとも実時間は流れ続けるので、録画中の操作が自然に見える。
    /// </summary>
    public sealed class OffsetClock : IClock
    {
        private readonly IClock _inner;

        public OffsetClock(IClock inner)
        {
            _inner = inner ?? throw new ArgumentNullException(nameof(inner));
        }

        /// <summary>進めた合計。保存しておけば再起動後も同じずれを再現できる。</summary>
        public TimeSpan Offset { get; private set; }

        public DateTimeOffset UtcNow => _inner.UtcNow + Offset;

        public void Advance(TimeSpan delta)
        {
            if (delta < TimeSpan.Zero)
            {
                throw new ArgumentOutOfRangeException(nameof(delta), delta, "OffsetClock only moves forward");
            }

            Offset += delta;
        }

        public void AdvanceDays(int days)
        {
            Advance(TimeSpan.FromDays(days));
        }

        public void Reset()
        {
            Offset = TimeSpan.Zero;
        }
    }
}
