using System;
using System.Linq;
using NUnit.Framework;
using ProjectPenguin.Data;
using ProjectPenguin.Domain.Clock;
using ProjectPenguin.Domain.Game;
using ProjectPenguin.Domain.Island;
using ProjectPenguin.Systems;
using UnityEngine;

namespace ProjectPenguin.Tests.EditMode
{
    /// <summary>保存と読み込み: 操作の記録を再生して、氷と島が同じ状態に戻ること。</summary>
    public sealed class GameStateSystemTests
    {
        private static readonly DateTimeOffset Start = new DateTimeOffset(2026, 10, 27, 12, 0, 0, TimeSpan.FromHours(9));

        private GameObject _go;

        [TearDown]
        public void TearDown()
        {
            if (_go != null)
            {
                UnityEngine.Object.DestroyImmediate(_go);
            }
        }

        private GameStateSystem New(IGameStore store, IClock clock)
        {
            if (_go != null)
            {
                UnityEngine.Object.DestroyImmediate(_go);
            }

            _go = new GameObject("GameState (test)");
            var system = _go.AddComponent<GameStateSystem>();
            system.Initialize(store, clock);
            return system;
        }

        [Test]
        public void 保存した操作を再生すると氷と島が同じになる()
        {
            var store = new MemoryGameStore();
            var clock = new ManualClock(Start);
            var a = New(store, clock);

            a.CompleteOnboarding("ペン");
            a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.SaveWater, "節水", "", 0.9));
            var mission = MissionCatalog.DailyFor(a.Today)[0];
            Assert.That(a.SelectMission(mission), Is.True);
            Assert.That(a.CheckIn(mission, CheckInAnswer.Done), Is.Not.Null);
            Assert.That(a.Build(FacilityKind.Fishery, new Cell(3, 2)), Is.EqualTo(IslandActionResult.Ok));
            Assert.That(a.Expand(new Cell(2, 2)), Is.EqualTo(IslandActionResult.Ok));

            clock.Advance(TimeSpan.FromDays(2));
            a.Refresh();
            a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.Goods, "マイボトル", "", 0.9));
            var ice = a.Session.Ice;
            var records = a.Session.TotalRecordDays;
            var fish = a.Island.Fish;

            var b = New(store, clock);

            Assert.That(b.Onboarded, Is.True);
            Assert.That(b.PlayerName, Is.EqualTo("ペン"));
            Assert.That(b.Session.Ice, Is.EqualTo(ice).Within(1e-9));
            Assert.That(b.Session.TotalRecordDays, Is.EqualTo(records));
            Assert.That(b.Island.Facilities.Select(f => f.Kind), Is.EqualTo(new[] { FacilityKind.Fishery }));
            Assert.That(b.Island.Board.Expansions, Is.EqualTo(new[] { new Cell(2, 2) }));
            Assert.That(b.Island.Fish, Is.EqualTo(fish));
            Assert.That(b.Activity.Count, Is.EqualTo(3), "写真 2 枚とミッション 1 件");
            Assert.That(b.CanReceivePhotoToday, Is.False, "今日の写真はもう受け取った");
        }

        [Test]
        public void 写真は1日1枚だけ資源になり_記録は1回目で付く()
        {
            var a = New(new MemoryGameStore(), new ManualClock(Start));
            var first = a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.SaveElectricity, "", "", 1));
            var second = a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.SaveElectricity, "", "", 1));

            Assert.That(first.NewRecordDay, Is.True);
            Assert.That(first.Granted, Is.Not.Null);
            Assert.That(second.NewRecordDay, Is.False);
            Assert.That(second.Granted, Is.Null);
        }

        [Test]
        public void 閉じていた間も島は進み_報告が残る()
        {
            var store = new MemoryGameStore();
            var clock = new ManualClock(Start);
            var a = New(store, clock);
            a.Build(FacilityKind.Fishery, new Cell(3, 2));
            var fish = a.Island.Fish;

            clock.Advance(TimeSpan.FromHours(2));
            var b = New(store, clock);

            // オンボーディングで来たアデリーペンギンが漁場を速くするので、速さを掛けて数える。
            var speed = b.Island.SpeedOf(b.Island.Facilities[0]);
            Assert.That(b.Island.Fish - fish, Is.EqualTo(Math.Floor(2 * 3600 * speed / 4)).Within(1));
            Assert.That(b.TakeOfflineReport(), Is.Not.Null);
        }

        [Test]
        public void データを消すと最初からになる()
        {
            var store = new MemoryGameStore();
            var a = New(store, new ManualClock(Start));
            a.CompleteOnboarding("ペン");
            a.Build(FacilityKind.Fishery, new Cell(3, 2));

            a.ResetAll();

            Assert.That(a.Onboarded, Is.False);
            Assert.That(a.Island.Facilities, Is.Empty);
            Assert.That(store.Load().onboarded, Is.False);
        }

        [Test]
        public void JSONの置き場は書いて読める()
        {
            var dir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "penguin-test-" + Guid.NewGuid().ToString("N"));
            System.IO.Directory.CreateDirectory(dir);
            try
            {
                var store = new JsonGameStore(dir);
                Assert.That(store.Load(), Is.Null);
                store.Save(new GameSave { createdUnixMs = 123, playerName = "ペン" });
                store.Save(new GameSave { createdUnixMs = 456, playerName = "ギン" });
                var loaded = store.Load();
                Assert.That(loaded.createdUnixMs, Is.EqualTo(456));
                Assert.That(loaded.playerName, Is.EqualTo("ギン"));
                store.Delete();
                Assert.That(store.Load(), Is.Null);
            }
            finally
            {
                System.IO.Directory.Delete(dir, true);
            }
        }

        [Test]
        public void SQLiteの置き場でも保存した状態に戻る()
        {
            var dir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "penguin-test-" + Guid.NewGuid().ToString("N"));
            System.IO.Directory.CreateDirectory(dir);
            try
            {
                var clock = new ManualClock(Start);
                var a = New(new SqliteGameStore(dir), clock);
                a.CompleteOnboarding("ペン");
                a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.SaveWater, "節水", "", 0.9));
                Assert.That(a.Build(FacilityKind.Fishery, new Cell(3, 2)), Is.EqualTo(IslandActionResult.Ok));
                clock.Advance(TimeSpan.FromDays(2));
                a.Refresh();
                a.RecordEcoPhoto(new EcoPhotoVerdict(EcoCategory.Goods, "マイボトル", "", 0.9));
                var ice = a.Session.Ice;
                var activity = a.Activity.Count;
                Assert.That(activity, Is.GreaterThan(0));

                // 別のシステムが、同じフォルダの DB から始める。
                var b = New(new SqliteGameStore(dir), clock);
                Assert.That(b.PlayerName, Is.EqualTo("ペン"));
                Assert.That(b.Onboarded, Is.True);
                Assert.That(b.Session.Ice, Is.EqualTo(ice).Within(1e-9));
                Assert.That(b.Activity.Count, Is.EqualTo(activity));
                Assert.That(b.Island.Facilities.Count, Is.EqualTo(1));
                Assert.That(b.LoadStatus, Is.EqualTo(ProjectPenguin.Data.Persistence.SaveLoadStatus.Loaded));
            }
            finally
            {
                System.IO.Directory.Delete(dir, true);
            }
        }
    }
}
