"""Tests for game_sim.py (run from the repository root: python3 -m pytest tools/game_sim)."""
import dataclasses as dc
import unittest
from datetime import datetime, timedelta

import game_sim as g


def T(y, m, d, hh, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=g.JST)


def bonus0(w, rs):
    return 0.0


class Calendar(unittest.TestCase):
    def test_03_boundary(self):
        self.assertEqual(g.app_day(T(2026, 1, 2, 2, 59)), 0)
        self.assertEqual(g.app_day(T(2026, 1, 2, 3, 0)), 1)

    def test_monday(self):
        self.assertTrue(g.is_monday(g.day_of_date(g.START) + 6))   # 2026-11-02
        self.assertEqual(g.week_of(-3), 0)
        self.assertEqual(g.week_of(-4), -1)

    def test_round_half_up(self):
        self.assertEqual(g.round_half_up(2.5), 3)
        self.assertEqual(g.round_half_up(0.49), 0)


class Ice(unittest.TestCase):
    def sess(self, start=T(2026, 10, 27, 9), p=g.DEFAULT):
        return g.Session(start, bonus0, p)

    def test_record_once_per_day(self):
        s = self.sess()
        s.scan_receipt(T(2026, 10, 27, 10), g.Receipt("a", 0))
        s.scan_receipt(T(2026, 10, 27, 11), g.Receipt("b", 0))
        self.assertEqual(s.s.ice, 102)
        s.scan_receipt(T(2026, 10, 28, 2, 59), g.Receipt("c", 0))   # still the 27th app day
        self.assertEqual(s.s.ice, 102)
        s.scan_receipt(T(2026, 10, 28, 3, 1), g.Receipt("d", 0))
        self.assertEqual(s.s.ice, 104)

    def test_failed_checkin_records(self):
        s = self.sess()
        self.assertTrue(s.select_mission(T(2026, 10, 27, 8), "E01", g.VERIF_SELF))
        self.assertTrue(s.check_in(T(2026, 10, 27, 21), "E01", g.ANS_FAILED))
        self.assertEqual(s.s.ice, 102)
        self.assertEqual(s.s.white_counted, 0)

    def test_unselected_checkin_rejected(self):
        s = self.sess()
        self.assertFalse(s.check_in(T(2026, 10, 27, 21), "E01", g.ANS_DONE))
        self.assertEqual(s.s.ice, 100)

    def test_shields_then_melt_and_monday_refill(self):
        s = self.sess()                       # Tue
        s.advance(T(2026, 11, 1, 12))         # Sun: Tue..Sat idle = 5 days
        self.assertEqual(s.s.shields, 0)
        self.assertEqual(s.s.ice, 94)
        s.advance(T(2026, 11, 2, 12))         # Mon start: refill (Sun melted first)
        self.assertEqual(s.s.ice, 92)
        self.assertEqual(s.s.shields, 2)

    def test_comeback(self):
        s = self.sess()
        s.advance(T(2026, 11, 2, 12))         # gap Tue..Sun 6 days, 4 melted *2 = 8
        self.assertEqual(s.s.gap_melted, 8)
        s.scan_receipt(T(2026, 11, 2, 13), g.Receipt("a", 0))
        self.assertEqual(s.s.ice, 92 + 2 + 4)

    def test_comeback_capped(self):
        s = self.sess()
        s.advance(T(2026, 11, 30, 12))
        self.assertGreater(s.s.gap_melted, 20)
        before = s.s.ice
        s.scan_receipt(T(2026, 11, 30, 13), g.Receipt("a", 0))
        self.assertEqual(s.s.ice, before + (4 if before < 60 else 2) + 10)

    def test_rescue_and_floor(self):
        s = self.sess()
        s.advance(T(2027, 2, 1, 12))
        self.assertEqual(s.s.ice, 40)
        s.scan_receipt(T(2027, 2, 1, 13), g.Receipt("a", 0))
        self.assertEqual(s.s.ice, 40 + 4 + 10)

    def test_cap_to_shards(self):
        p = dc.replace(g.DEFAULT, initial=149.0)
        s = g.Session(T(2026, 10, 27, 9), lambda w, rs: 2.5, p)
        s.scan_receipt(T(2026, 10, 27, 10), g.Receipt("a", g.day_of_date(g.START)))
        self.assertEqual(s.s.ice, 150)
        self.assertEqual(s.s.shards_exact, 1)
        for i in range(1, 6):
            s.scan_receipt(T(2026, 10, 27, 10) + timedelta(days=i), g.Receipt(f"x{i}", 0))
        s.advance(T(2026, 11, 2, 12))         # Monday: B 2.5 all to shards
        self.assertAlmostEqual(s.s.shards_exact, 1 + 10 + 2.5)
        self.assertEqual(s.s.shards, 13)

    def test_clock_rollback_ignored(self):
        s = self.sess()
        s.advance(T(2026, 10, 29, 12))
        self.assertFalse(s.scan_receipt(T(2026, 10, 28, 12), g.Receipt("a", 0)))
        self.assertEqual(s.s.ice, 100)

    def test_dedup(self):
        s = self.sess()
        self.assertTrue(s.scan_receipt(T(2026, 10, 27, 10), g.Receipt("a", 0)))
        self.assertFalse(s.scan_receipt(T(2026, 10, 28, 10), g.Receipt("a", 0)))
        self.assertEqual(s.s.ice, 102)


class Tiers(unittest.TestCase):
    def test_hysteresis(self):
        p = g.DECIDED
        self.assertEqual(g.tier_next(2, 100, p), 3)
        self.assertEqual(g.tier_next(3, 96, p), 3)
        self.assertEqual(g.tier_next(3, 95.9, p), 2)
        self.assertEqual(g.tier_next(0, 130, p), 4)
        self.assertEqual(g.tier_next(4, 40, p), 0)
        self.assertEqual(g.tier_next(3, 94, g.DEFAULT), 3)
        self.assertEqual(g.tier_next(3, 93.9, g.DEFAULT), 2)


class Stamps(unittest.TestCase):
    def test_gold_window(self):
        s = g.Session(T(2026, 10, 27, 7), bonus0)
        d0 = g.day_of_date(g.START)
        s.select_mission(T(2026, 10, 27, 8), "F01", g.VERIF_RECEIPT)
        s.scan_receipt(T(2026, 10, 30, 10), g.Receipt("late", d0 + 3, ("F01",)))   # outside D..D+2
        self.assertEqual(s.s.gold, 0)
        s.scan_receipt(T(2026, 10, 30, 11), g.Receipt("ok", d0 + 2, ("F01",)))
        self.assertEqual(s.s.gold, 1)
        s.scan_receipt(T(2026, 10, 30, 12), g.Receipt("again", d0 + 2, ("F01",)))
        self.assertEqual(s.s.gold, 1)

    def test_white_caps(self):
        s = g.Session(T(2026, 11, 2, 7), bonus0)   # Monday
        for i in range(7):
            day = T(2026, 11, 2, 0) + timedelta(days=i)
            for m in ("E01", "E02"):
                s.select_mission(day + timedelta(hours=8), f"{m}{i}", g.VERIF_SELF)
                s.check_in(day + timedelta(hours=21), f"{m}{i}", g.ANS_DONE)
        self.assertEqual(s.s.white_pressed, 14)
        self.assertEqual(s.s.white_counted, 5)

    def test_selection_limit(self):
        s = g.Session(T(2026, 11, 2, 7), bonus0)
        self.assertTrue(s.select_mission(T(2026, 11, 2, 8), "a", g.VERIF_SELF))
        self.assertTrue(s.select_mission(T(2026, 11, 2, 8), "b", g.VERIF_SELF))
        self.assertFalse(s.select_mission(T(2026, 11, 2, 8), "c", g.VERIF_SELF))


class Penguins(unittest.TestCase):
    def test_max_one_per_week_never_lost(self):
        for p in (g.DEFAULT, g.DECIDED):
            for n in g.PERSONAS:
                r = g.run_persona(n, p)
                weeks = {}
                for a in r.session.s.arrivals:
                    if a.reason != "onboarding":
                        weeks[g.week_of(a.day)] = weeks.get(g.week_of(a.day), 0) + 1
                self.assertTrue(all(v <= 1 for v in weeks.values()), n)
                sp = [a.species for a in r.session.s.arrivals]
                self.assertEqual(len(sp), len(set(sp)))

    def test_decided_rule_misses_day3_target(self):
        r = g.run_persona("daily", g.DECIDED)
        self.assertEqual(r.snaps[2].penguins, 1)
        r = g.run_persona("daily", g.DEFAULT)
        self.assertEqual(r.snaps[2].penguins, 2)


class Targets(unittest.TestCase):
    def test_all_targets_pass_with_15d_params(self):
        res = g.run_all(g.DEFAULT)
        for name, ok, info in g.check_targets(res, g.DEFAULT):
            self.assertTrue(ok, f"{name}: {info}")

    def test_decided_params_fail_two_targets(self):
        res = g.run_all(g.DECIDED)
        failed = [n for n, ok, _ in g.check_targets(res, g.DECIDED) if not ok]
        self.assertEqual(len(failed), 2)

    def test_lapsed_recovery(self):
        self.assertLessEqual(g.recovery_days(g.run_persona("lapsed")), 7)


if __name__ == "__main__":
    unittest.main()
