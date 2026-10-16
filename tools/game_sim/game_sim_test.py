"""Tests for game_sim.py (run: python3 -m unittest game_sim_test -v)."""
import csv
import dataclasses as dc
import json
import os
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
        # v3 behaviour, kept reachable through Params.rollback_clamp=False (V3 / DECIDED)
        s = self.sess(p=g.V3)
        s.advance(T(2026, 10, 29, 12))
        self.assertFalse(s.scan_receipt(T(2026, 10, 28, 12), g.Receipt("a", 0)))
        self.assertEqual(s.s.ice, 100)

    def test_clock_rollback_clamps_to_last_seen_day(self):
        # v4 (17a §1): a rollback acts on the last seen app day instead of being ignored
        s = self.sess()
        d29 = s.advance(T(2026, 10, 29, 12))
        self.assertTrue(s.scan_receipt(T(2026, 10, 28, 12), g.Receipt("a", 0)))
        self.assertEqual(s.clock_status, g.CLOCK_BEHIND)
        self.assertEqual(s.s.clock_rollbacks, 1)
        self.assertIn(d29, s.recorded_days)
        self.assertNotIn(d29 - 1, s.recorded_days)        # old days are never refilled
        self.assertEqual(s.s.ice, 102)
        self.assertTrue(s.scan_receipt(T(2026, 10, 27, 12), g.Receipt("b", 0)))
        self.assertEqual(s.s.ice, 102)                     # still once per (last seen) day
        s.advance(T(2026, 10, 30, 12))
        self.assertEqual(s.clock_status, g.CLOCK_OK)

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


def honest_checkin(s, when, mid):
    s.select_mission(when, mid, g.VERIF_SELF)
    return s.check_in(when, mid, g.ANS_DONE)


class ClockV4(unittest.TestCase):
    """16d §5.1 A/B/C reproduced with an untrusted (device) clock, and the v4 fixes."""
    START = T(2026, 10, 27, 12)

    def test_A_forward_30_days_and_back_no_lockout(self):
        s = g.Session(self.START, bonus0, clock_trusted=False)
        s.scan_receipt(self.START, g.Receipt("r0", 0))
        self.assertIsNone(s.advance(self.START + timedelta(days=30)))
        self.assertEqual(s.clock_status, g.CLOCK_AHEAD_PENDING)
        self.assertEqual(s.s.ice, 102)                     # nothing melted for the fake 30 days
        rejected = 0
        for d in range(1, 32):
            if not s.scan_receipt(self.START + timedelta(days=d), g.Receipt(f"a{d}", 0)):
                rejected += 1
        self.assertEqual(rejected, 0)
        self.assertEqual(s.s.total_record_days, 32)

    def test_A_v3_lockout_reproduced(self):
        s = g.Session(self.START, bonus0, g.V3)
        s.scan_receipt(self.START, g.Receipt("r0", 0))
        s.advance(self.START + timedelta(days=30))
        rejected = sum(not s.scan_receipt(self.START + timedelta(days=d), g.Receipt(f"a{d}", 0)) for d in range(1, 32))
        self.assertEqual(rejected, 29)                     # the 16d probe result

    def test_C_jump_to_2099_is_held_then_released(self):
        s = g.Session(self.START, bonus0, clock_trusted=False)
        self.assertIsNone(s.advance(datetime(2099, 1, 1, tzinfo=g.JST)))
        self.assertEqual(s.s.ice, 100)
        self.assertTrue(s.scan_receipt(self.START + timedelta(days=1), g.Receipt("x", 0)))
        self.assertEqual(s.clock_status, g.CLOCK_OK)

    def test_jump_within_limit_is_processed(self):
        s = g.Session(self.START, bonus0, clock_trusted=False)
        self.assertIsNotNone(s.advance(self.START + timedelta(days=14)))
        self.assertIsNone(s.advance(self.START + timedelta(days=29)))   # 15 > 14 days ahead of last seen

    def test_confirm_clock_settles_a_real_long_absence(self):
        s = g.Session(self.START, bonus0, clock_trusted=False)
        later = self.START + timedelta(days=30)
        self.assertFalse(s.scan_receipt(later, g.Receipt("a", 0)))
        self.assertIsNotNone(s.confirm_clock(later))
        self.assertLess(s.s.ice, 100)
        before = s.s.ice
        self.assertTrue(s.scan_receipt(later, g.Receipt("a", 0)))
        self.assertEqual(s.s.ice, before + 2 + 10)          # comeback capped at 10

    def test_B_banking_days_ahead_gives_no_lasting_gain(self):
        cheat = g.Session(self.START, bonus0, clock_trusted=False)
        for d in range(7):                                  # step the clock 1 day at a time
            honest_checkin(cheat, self.START + timedelta(days=d), f"M{d}")
        self.assertEqual(cheat.s.ice, 114)
        honest = g.Session(self.START, bonus0)
        for d in range(14):                                 # real time; the cheater keeps playing honestly
            honest_checkin(cheat, self.START + timedelta(days=d, hours=1), f"N{d}")
            honest_checkin(honest, self.START + timedelta(days=d, hours=1), f"N{d}")
        end = self.START + timedelta(days=14)
        cheat.advance(end)
        honest.advance(end)
        self.assertEqual(cheat.s.ice, honest.s.ice)
        self.assertEqual(cheat.s.total_record_days, honest.s.total_record_days)


class ComebackV4(unittest.TestCase):
    def test_shield_only_gap_gives_no_comeback(self):
        # Tue start, record Tue..Fri, skip Sat Sun Mon: Sat/Sun shields, Monday refill shields Monday -> nothing melts
        for p, expect in ((g.V3, [0]), (g.DEFAULT, [])):
            s = g.Session(T(2026, 10, 27, 9), bonus0, p)
            for i in range(4):
                honest_checkin(s, T(2026, 10, 27, 20) + timedelta(days=i), f"E{i}")
            honest_checkin(s, T(2026, 11, 3, 20), "E9")
            self.assertEqual([x for _, x in s.comeback_log], expect, p)
            self.assertEqual(s.s.ice, 110)

    def test_one_melted_day_gives_plus_one(self):
        s = g.Session(T(2026, 10, 27, 9), bonus0)
        s.advance(T(2026, 10, 29, 12))          # Tue, Wed shielded (2 days)
        honest_checkin(s, T(2026, 10, 29, 20), "a")
        s.advance(T(2026, 10, 31, 12))          # Thu shield 0 -> Fri melts 2
        self.assertEqual(s.s.gap_melted, 2)
        honest_checkin(s, T(2026, 10, 31, 20), "b")
        self.assertEqual(s.comeback_log[-1][1], 1)
        self.assertEqual(s.s.ice, 100 + 2 - 2 + 2 + 1)
        r = g.run_persona("casual")
        self.assertEqual(r.session.comeback_log[0][0] - g.day_of_date(g.START) + 1, 12)   # 16a §4.1


class SaveRestore(unittest.TestCase):
    def test_round_trip_json(self):
        r = g.run_persona("cheater")
        js = r.session.export_json()
        x = g.Session.restore(js, g.standin_bonus)
        self.assertEqual(x.export_json(), js)
        self.assertEqual(json.loads(js)["version"], g.STATE_VERSION)

    def test_restore_does_not_add_a_second_adelie(self):
        s = g.Session(T(2026, 10, 27, 9), bonus0)
        x = g.Session.restore(s.export_json(), bonus0)
        x.advance(T(2026, 10, 28, 9))
        self.assertEqual([a.species for a in x.s.arrivals].count(g.M_ONBOARDING), 1)
        self.assertEqual(len(x.s.arrivals), 1)

    def test_unknown_version_rejected(self):
        st = g.Session(T(2026, 10, 27, 9), bonus0).export_state()
        st["version"] = 99
        with self.assertRaises(ValueError):
            g.Session.restore(st, bonus0)

    def test_save_restore_before_every_event_changes_nothing(self):
        for p in (g.DEFAULT, g.DEFERRED_B):
            for n in g.PERSONAS:
                base = g.run_events(g.persona_events(n), p)
                snaps = []
                first, last = g.day_of_date(g.START), g.day_of_date(g.START) + g.DAYS - 1

                def cb(sess, d):
                    if first <= d <= last:
                        snaps.append(sess.snapshot(d))

                sess = g.Session(g.at(0, 7), g.standin_bonus, p, cb)
                for t, op, a in g.persona_events(n):
                    sess = g.Session.restore(json.loads(json.dumps(sess.export_state())), g.standin_bonus, p, cb)
                    if op == "receipt":
                        sess.scan_receipt(t, g.Receipt(a[0], a[1], tuple(a[2])))
                    elif op == "select":
                        sess.select_mission(t, a[0], a[1])
                    else:
                        sess.check_in(t, a[0], a[1], a[2])
                sess = g.Session.restore(sess.export_json(), g.standin_bonus, p, cb)
                sess.advance(g.at(g.DAYS, 4))
                self.assertEqual(snaps, base.snaps, n)
                self.assertEqual(sess.export_json(), base.session.export_json(), n)


class LateReceiptBonus(unittest.TestCase):
    """16d §5.1 D: a Sunday receipt scanned on Tuesday."""

    def run_case(self, p, scan_at):
        calls = []
        s = g.Session(T(2026, 10, 27, 12), lambda w, rs: calls.append((w, len(rs))) or 2.5, p)
        sunday = g.day_of_date(g.START) + 5
        s.scan_receipt(scan_at, g.Receipt("late", sunday))
        s.advance(T(2026, 11, 10, 12))
        return s, calls

    def test_option_b_monday_counts_record_only(self):
        s, calls = self.run_case(g.DEFAULT, T(2026, 11, 3, 12))
        self.assertEqual(calls, [])
        self.assertEqual(s.s.late_bonus_receipts, 1)
        self.assertEqual(s.s.total_record_days, 1)

    def test_option_a_grace_counts_until_wednesday(self):
        s, calls = self.run_case(g.DEFERRED_B, T(2026, 11, 3, 12))   # Tuesday
        self.assertEqual(calls, [(g.week_of(g.day_of_date(g.START) + 5), 1)])
        self.assertEqual(s.s.late_bonus_receipts, 0)
        s, calls = self.run_case(g.DEFERRED_B, T(2026, 11, 4, 12))   # Wednesday: too late
        self.assertEqual(calls, [])
        self.assertEqual(s.s.late_bonus_receipts, 1)

    def test_deferred_b_passes_all_targets(self):
        res = g.run_all(g.DEFERRED_B)
        for name, ok, info in g.check_targets(res, g.DEFERRED_B):
            self.assertTrue(ok, f"{name}: {info}")


class SpeciesIds(unittest.TestCase):
    """19 §5 / 18a D18: species are keyed by the 17b-zukan.csv `id`, never by a Japanese name."""
    CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "17b-zukan.csv")

    def test_ids_and_display_names_match_17b_zukan(self):
        if not os.path.exists(self.CSV):
            self.skipTest("17b-zukan.csv not found next to v4/")
        with open(self.CSV, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([r["id"] for r in rows], g.SPECIES)
        self.assertEqual({r["id"]: r["name_ja"] for r in rows}, g.NAME_JA)

    def test_ids_are_ascii_snake_case(self):
        for sp in g.SPECIES:
            self.assertRegex(sp, r"^[a-z][a-z_]*$")

    def test_saved_state_holds_ids_only(self):
        for n in g.PERSONAS:
            st = g.run_persona(n).session.export_state()
            for sp in [a["species"] for a in st["arrivals"]] + list(st["milestoneQueue"]):
                self.assertIn(sp, g.SPECIES, n)

    def test_daily_arrival_order_in_ids(self):
        sp = [a.species for a in g.run_persona("daily").session.s.arrivals]
        self.assertEqual(sp, ["adelie", "little", "chinstrap", "magellanic", "king", "yellow_eyed", "emperor",
                              "gentoo", "humboldt", "macaroni"])

    def test_restore_rejects_japanese_species_name(self):
        st = g.Session(T(2026, 10, 27, 9), bonus0).export_state()
        st["arrivals"][0]["species"] = "アデリーペンギン"
        with self.assertRaises(ValueError):
            g.Session.restore(st, bonus0)
        st = g.Session(T(2026, 10, 27, 9), bonus0).export_state()
        st["milestoneQueue"] = ["コガタペンギン"]
        with self.assertRaises(ValueError):
            g.Session.restore(st, bonus0)


if __name__ == "__main__":
    unittest.main()
