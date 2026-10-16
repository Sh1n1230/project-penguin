"""Project Penguin integrated game logic + 8-week persona simulator (15d, v4 fixes of 17a).

v4 (2026-10-16, 17a-logic-fixes.md) changes on top of the 15d rules:
  * clock rollback: an action whose app day is before the last seen day is treated
    as happening on the last seen day (high-water mark) instead of being ignored
  * large forward jump: more than max_catch_up_days ahead of the last seen day is
    held (not settled, actions rejected) until the clock is trusted / confirmed
  * comeback ("おかえり") fires on the first record after >= 1 day that melted
    (unshielded and gap_melted > 0), instead of after >= 3 non-record days
  * state export / restore as versioned JSON (STATE_VERSION)
  * weekly choice bonus B: bonus_grace_days (0 = Monday, as in the spec; 2 =
    settle on Wednesday 03:00 so receipts scanned late still count)

19 (2026-10-16, 19-game-logic-spec-v4.md §5): penguin species are keyed by the
`id` column of 17b-zukan.csv ("adelie", "little", ...) in code and in saved
state; NAME_JA holds the 17b display names. Restore rejects unknown species ids.
No rule or value changed, so every number is the same as 17a.

Implements the integrated rules decided on 2026-10-15 (see 15d-simulation.md):
  * app day boundary 03:00 JST; record day = app day the user acted
  * record = receipt scan OR evening mission check-in (any answer); 1/day
  * +2 ice (+4 when ice < 60); non-record day -2 unless a shield absorbs it
  * shields start 2, refill to 2 every Monday 03:00, max 2
  * comeback: first record after a gap in which ice melted (v4; 15d: >= 3 non-record days) gets
    min(10, round_half_up(0.5 * ice melted during the gap))
  * floor 40, cap 150; any gain above the cap -> shards 1:1 (no cap)
  * weekly choice bonus B (0..4, receipts only) applied at Monday start
  * mission stamps: receipt-verified gold 2pt; self/photo "done" white 1pt
    (counted max 1/day, 5/week); missions never add ice
  * visual tiers with hysteresis 4
  * penguin arrivals: weekly (prev week >= 3 record days) + milestones,
    max 1 arrival per week overall, milestone first, weekly queues

Pure Python, no dependencies.  The C# port in csharp/Assets/Scripts/Domain/Game
mirrors this file; tools/gen_game_golden.py freezes this file's output for the
C# parity tests.
"""
from __future__ import annotations

import dataclasses
import json
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Sequence, Tuple

JST = timezone(timedelta(hours=9))
EPOCH = date(2026, 1, 1)          # app day 0 (Thursday), same as JstCalendar
DAY_BOUNDARY_HOURS = 3            # 03:00 JST


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

def app_day(instant: datetime) -> int:
    """App day number: the JST calendar day of (instant - 3h)."""
    j = instant.astimezone(JST) - timedelta(hours=DAY_BOUNDARY_HOURS)
    return (j.date() - EPOCH).days


def week_of(day: int) -> int:
    """Monday-based week number (2025-12-29 Mon .. 2026-01-04 Sun = 0)."""
    return (day + 3) // 7


def is_monday(day: int) -> bool:
    return (day + 3) % 7 == 0


def day_of_date(d: date) -> int:
    return (d - EPOCH).days


def round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Params:
    initial: float = 100.0
    floor: float = 40.0
    cap: float = 150.0
    record_gain: float = 2.0
    melt: float = 2.0
    rescue_below: float = 60.0
    rescue_mult: float = 2.0
    shields_start: int = 2
    shields_max: int = 2
    comeback_min_gap: int = 3
    comeback_ratio: float = 0.5
    comeback_max: int = 10
    tier_bounds: Tuple[float, ...] = (60.0, 80.0, 100.0, 125.0)
    tier_hysteresis: float = 6.0              # 15d change: decided 4 flickers for 週2 (md §4)
    weekly_arrival_min_days: int = 3
    weekly_bonus_max: float = 4.0
    max_arrivals_per_week: int = 1
    onboarding_exempt_from_cap: bool = True   # 15d change (see md §4); False = rule as first decided
    selections_per_day: int = 2
    gold_points: int = 2
    white_points: int = 1
    white_per_day: int = 1
    white_per_week: int = 5
    # ---- v4 (17a) ----
    comeback_requires_melt: bool = True       # 16a §4.1: fire after >= 1 day that actually melted
    rollback_clamp: bool = True               # clock behind the last seen day -> act on the last seen day
    max_catch_up_days: Optional[int] = 14     # bigger untrusted forward jumps are held (None = no limit)
    bonus_grace_days: int = 0                 # B for week W settles on Monday(W+1) + this many days


DEFAULT = Params()
# the 15d rules (v3) exactly as shipped on 2026-10-15: old comeback trigger, rollback ignored, no jump limit
V3 = Params(comeback_requires_melt=False, rollback_clamp=False, max_catch_up_days=None)
# the rules exactly as decided on 2026-10-15, before the two 15d changes (and before v4)
DECIDED = dataclasses.replace(V3, tier_hysteresis=4.0, onboarding_exempt_from_cap=False)
# 16d §5.2-3 option (a): B settles on Wednesday 03:00 so late-scanned receipts still count
DEFERRED_B = Params(bonus_grace_days=2)

STATE_VERSION = 1
CLOCK_OK, CLOCK_BEHIND, CLOCK_AHEAD_PENDING = "ok", "behind", "ahead_pending"
INT_MIN = -2 ** 31                          # "no arrival yet" week sentinel (same as C# int.MinValue)

# 15c §3.2 / §3.3. Species keys are the `id` column of 17b-zukan.csv (19 §5, 18a C26 / D18).
# Japanese names are for display only and never go into code paths or saved state.
SPECIES = [
    "emperor", "king", "adelie", "chinstrap", "gentoo",
    "little", "galapagos", "humboldt", "magellanic", "african",
    "yellow_eyed", "macaroni", "royal", "northern_rockhopper", "western_rockhopper",
    "eastern_rockhopper", "fiordland", "snares", "erect_crested",
]
# Display names (17b-zukan.csv `name_ja`, IOC 15.2 Japanese column). Not used by the logic.
NAME_JA = {
    "emperor": "コウテイペンギン", "king": "オウサマペンギン", "adelie": "アデリーペンギン",
    "chinstrap": "ヒゲペンギン", "gentoo": "ジェンツーペンギン", "little": "コビトペンギン",
    "galapagos": "ガラパゴスペンギン", "humboldt": "フンボルトペンギン", "magellanic": "マゼランペンギン",
    "african": "ケープペンギン", "yellow_eyed": "キンメペンギン", "macaroni": "マカロニペンギン",
    "royal": "ロイヤルペンギン", "northern_rockhopper": "キタイワトビペンギン",
    "western_rockhopper": "ミナミイワトビペンギン", "eastern_rockhopper": "ヒガシイワトビペンギン（仮称）",
    "fiordland": "キマユペンギン", "snares": "ハシブトペンギン", "erect_crested": "マユダチペンギン",
}
M_ONBOARDING = "adelie"
M_FIRST_RECORD = "little"
M_ALL_KINDS = "magellanic"
M_FIRST_COMEBACK = "galapagos"
M_FIVE_MISSIONS = "chinstrap"
M_TOTAL_14 = "king"
M_TOTAL_30 = "emperor"
M_FOUR_WEEKS = "yellow_eyed"
MILESTONE_ORDER = [M_ONBOARDING, M_FIRST_RECORD, M_ALL_KINDS, M_FIRST_COMEBACK,
                   M_FIVE_MISSIONS, M_TOTAL_14, M_TOTAL_30, M_FOUR_WEEKS]
WEEKLY_ORDER = ["gentoo", "humboldt", "macaroni", "royal", "african",
                "fiordland", "snares", "northern_rockhopper", "western_rockhopper",
                "eastern_rockhopper", "erect_crested"]
assert len(set(MILESTONE_ORDER + WEEKLY_ORDER)) == 19 == len(SPECIES) == len(NAME_JA)
assert set(MILESTONE_ORDER + WEEKLY_ORDER) == set(SPECIES) == set(NAME_JA)

KIND_RECEIPT, KIND_MISSION, KIND_NO_SHOPPING = "receipt", "mission", "no_shopping_mission"
VERIF_RECEIPT, VERIF_SELF, VERIF_PHOTO = "receipt", "self", "photo"
ANS_DONE, ANS_PARTIAL, ANS_FAILED = "done", "partial", "failed"


def tier_next(current: int, ice: float, p: Params = DEFAULT) -> int:
    """Next visual tier. Up immediately at a bound, down only below bound - hysteresis."""
    t = current
    while t < len(p.tier_bounds) and ice >= p.tier_bounds[t]:
        t += 1
    while t > 0 and ice < p.tier_bounds[t - 1] - p.tier_hysteresis:
        t -= 1
    return t


def tier_of(ice: float, p: Params = DEFAULT) -> int:
    return sum(1 for b in p.tier_bounds if ice >= b)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

@dataclass
class Arrival:
    species: str
    day: int
    reason: str            # onboarding | milestone | weekly


@dataclass
class Snapshot:
    day: int
    ice: float
    shields: int
    shards_exact: float
    shards: int
    tier: int
    total_record_days: int
    penguins: int
    gold: int
    white_counted: int
    stamp_points: int
    shields_used: int
    recorded: bool


@dataclass
class GameState:
    ice: float
    shields: int
    tier: int
    shards_exact: float = 0.0
    total_record_days: int = 0
    streak: int = 0
    gap_days: int = 0
    gap_melted: float = 0.0
    comebacks: int = 0
    shields_used: int = 0
    gold: int = 0
    white_pressed: int = 0
    white_counted: int = 0
    kinds_used: set = field(default_factory=set)
    done_missions: set = field(default_factory=set)
    week_record_days: Dict[int, int] = field(default_factory=dict)
    consecutive_weeks: int = 0
    arrivals: List[Arrival] = field(default_factory=list)
    milestone_queue: List[str] = field(default_factory=list)
    weekly_pending: int = 0
    weekly_index: int = 0
    last_arrival_week: int = -2 ** 31
    clock_rollbacks: int = 0
    late_bonus_receipts: int = 0

    @property
    def shards(self) -> int:
        return int(math.floor(self.shards_exact + 1e-9))

    @property
    def stamp_points(self) -> int:
        return self.gold * DEFAULT.gold_points + self.white_counted * DEFAULT.white_points


@dataclass
class Receipt:
    receipt_id: str
    print_day: int
    verifies: Tuple[str, ...] = ()   # mission ids whose receipt_rule this receipt satisfies
    scan_day: Optional[int] = None   # app day it was scanned (set by the session)


BonusFn = Callable[[int, List[Receipt]], float]


class Session:
    """Clock-driven game session (mirror of C# GameSession)."""

    def __init__(self, now: Optional[datetime], bonus_fn: BonusFn, p: Params = DEFAULT,
                 on_day_settled: Optional[Callable[["Session", int], None]] = None,
                 clock_trusted: bool = True, _restoring: bool = False):
        self.p = p
        self.bonus_fn = bonus_fn
        self.on_day_settled = on_day_settled
        # True: the instants passed in are trusted (server-anchored clock, tests, simulation)
        self.clock_trusted = clock_trusted
        self.clock_status = CLOCK_OK          # transient: result of the last advance()
        self.pending_ahead_day: Optional[int] = None
        self.s = GameState(ice=p.initial, shields=p.shields_start, tier=tier_of(p.initial, p))
        self.recorded_days: set = set()
        self.receipts: Dict[str, Receipt] = {}
        self.selected: Dict[int, List[Tuple[str, str]]] = {}
        self.checked: set = set()
        self.verified: set = set()
        self.white_by_day: Dict[int, int] = {}
        self.white_by_week: Dict[int, int] = {}
        self.tier_log: List[Tuple[int, int, int]] = []   # (day, from, to)
        self.comeback_log: List[Tuple[int, int]] = []    # (day, extra)
        if _restoring:
            return
        self.first_day = app_day(now)
        self.last_started = self.first_day - 1
        self.last_settled = self.first_day - 1
        self._start_day(self.first_day, first=True)

    # ----- time -----
    def _today(self, now: datetime, force: bool = False) -> Optional[int]:
        d = app_day(now)
        if d < self.last_started:
            self.s.clock_rollbacks += 1
            self.pending_ahead_day = None
            self.clock_status = CLOCK_BEHIND
            if not self.p.rollback_clamp:
                return None      # v3: ignore the action entirely
            return self.last_started   # v4: the last seen day (high-water mark); old days are never refilled
        lim = self.p.max_catch_up_days
        if lim is not None and d - self.last_started > lim and not (self.clock_trusted or force):
            self.pending_ahead_day = d  # v4: hold the jump; nothing settles, the action does nothing
            self.clock_status = CLOCK_AHEAD_PENDING
            return None
        self.pending_ahead_day = None
        self.clock_status = CLOCK_OK
        return d

    def confirm_clock(self, now: datetime) -> Optional[int]:
        """Settle a held forward jump once the caller has confirmed the time (e.g. server Date header)."""
        return self.advance(now, force=True)

    def advance(self, now: datetime, force: bool = False) -> Optional[int]:
        today = self._today(now, force)
        if today is None:
            return None
        for d in range(self.last_settled + 1, today):
            if d > self.last_started:
                self._start_day(d)
            if d not in self.recorded_days:
                self._non_record(d)
            self.last_settled = d
            if self.on_day_settled:
                self.on_day_settled(self, d)
        if today > self.last_started:
            self._start_day(today)
        return today

    # ----- ice helpers -----
    def _set_tier(self, day: int) -> None:
        nt = tier_next(self.s.tier, self.s.ice, self.p)
        if nt != self.s.tier:
            self.tier_log.append((day, self.s.tier, nt))
            self.s.tier = nt

    def _add_ice(self, amount: float) -> None:
        new = self.s.ice + amount
        if new > self.p.cap:
            self.s.shards_exact += new - self.p.cap
            new = self.p.cap
        self.s.ice = new

    def _start_day(self, d: int, first: bool = False) -> None:
        self.last_started = d
        s, p = self.s, self.p
        if first:
            if p.onboarding_exempt_from_cap:
                s.arrivals.append(Arrival(M_ONBOARDING, d, "onboarding"))
            else:
                self._enqueue(M_ONBOARDING)
                self._try_deliver(d)
        if first:
            return
        monday = is_monday(d)
        if monday:
            s.shields = p.shields_max
        if is_monday(d - p.bonus_grace_days):
            self._apply_bonus(d, week_of(d - p.bonus_grace_days) - 1)
        if not monday:
            return
        prev = week_of(d) - 1
        if prev >= week_of(self.first_day):
            if s.week_record_days.get(prev, 0) >= p.weekly_arrival_min_days:
                s.weekly_pending += 1
                s.consecutive_weeks += 1
                if s.consecutive_weeks >= 4:
                    self._enqueue(M_FOUR_WEEKS)
            else:
                s.consecutive_weeks = 0
        self._try_deliver(d)

    def _apply_bonus(self, d: int, week: int) -> None:
        """Weekly choice bonus B for a closed week, from receipts printed in it and scanned so far."""
        if week < week_of(self.first_day):
            return
        rs = [r for r in self.receipts.values() if week_of(r.print_day) == week]
        b = max(0.0, min(self.p.weekly_bonus_max, self.bonus_fn(week, rs))) if rs else 0.0
        if b > 0:
            self._add_ice(b)
            self._set_tier(d)

    def bonus_settle_day(self, week: int) -> int:
        """App day on whose start B for `week` is added (Monday of the next week + grace)."""
        return (week + 1) * 7 - 3 + self.p.bonus_grace_days

    def _non_record(self, d: int) -> None:
        s, p = self.s, self.p
        s.gap_days += 1
        s.streak = 0
        if s.shields > 0:
            s.shields -= 1
            s.shields_used += 1
            return
        m = max(0.0, min(p.melt, s.ice - p.floor))
        s.ice -= m
        s.gap_melted += m
        self._set_tier(d)

    def _record(self, d: int, kind: str) -> bool:
        s, p = self.s, self.p
        if kind not in s.kinds_used:
            s.kinds_used.add(kind)
            if len(s.kinds_used) == 3:
                self._enqueue(M_ALL_KINDS)
        if d in self.recorded_days:
            self._try_deliver(d)
            return False
        self.recorded_days.add(d)
        gain = p.record_gain * (p.rescue_mult if s.ice < p.rescue_below else 1.0)
        fires = s.gap_melted > 0 if p.comeback_requires_melt else s.gap_days >= p.comeback_min_gap
        if fires:
            extra = min(p.comeback_max, round_half_up(p.comeback_ratio * s.gap_melted))
            gain += extra
            s.comebacks += 1
            self.comeback_log.append((d, extra))
            if s.comebacks == 1:
                self._enqueue(M_FIRST_COMEBACK)
        s.gap_days = 0
        s.gap_melted = 0.0
        self._add_ice(gain)
        self._set_tier(d)
        s.streak += 1
        s.total_record_days += 1
        w = week_of(d)
        s.week_record_days[w] = s.week_record_days.get(w, 0) + 1
        if s.total_record_days == 1:
            self._enqueue(M_FIRST_RECORD)
        if s.total_record_days == 14:
            self._enqueue(M_TOTAL_14)
        if s.total_record_days == 30:
            self._enqueue(M_TOTAL_30)
        self._try_deliver(d)
        return True

    # ----- penguins -----
    def _enqueue(self, sp: str) -> None:
        s = self.s
        if sp in s.milestone_queue or any(a.species == sp for a in s.arrivals):
            return
        s.milestone_queue.append(sp)

    def _next_weekly(self) -> Optional[str]:
        s = self.s
        have = {a.species for a in s.arrivals} | set(s.milestone_queue)
        while s.weekly_index < len(WEEKLY_ORDER):
            sp = WEEKLY_ORDER[s.weekly_index]
            s.weekly_index += 1
            if sp not in have:
                return sp
        for sp in MILESTONE_ORDER:           # weekly order exhausted: un-arrived milestone species
            if sp not in have:
                return sp
        return None

    def _try_deliver(self, d: int) -> None:
        s = self.s
        w = week_of(d)
        if s.last_arrival_week == w:
            return
        if s.milestone_queue:
            sp = s.milestone_queue.pop(0)
            s.arrivals.append(Arrival(sp, d, "milestone"))
            s.last_arrival_week = w
        elif s.weekly_pending > 0:
            sp = self._next_weekly()
            s.weekly_pending -= 1
            if sp is not None:
                s.arrivals.append(Arrival(sp, d, "weekly"))
                s.last_arrival_week = w

    def _mark_done_mission(self, mid: str) -> None:
        s = self.s
        if mid not in s.done_missions:
            s.done_missions.add(mid)
            if len(s.done_missions) == 5:
                self._enqueue(M_FIVE_MISSIONS)

    # ----- user actions -----
    def scan_receipt(self, now: datetime, r: Receipt) -> bool:
        d = self.advance(now)
        if d is None or r.receipt_id in self.receipts:
            return False
        r = dataclasses.replace(r, scan_day=d)
        self.receipts[r.receipt_id] = r
        if self.bonus_settle_day(week_of(r.print_day)) <= d:
            self.s.late_bonus_receipts += 1     # its week's B is already settled: counts as a record only
        for sd in sorted(self.selected):
            for mid, verif in self.selected[sd]:
                if verif != VERIF_RECEIPT or (sd, mid) in self.verified:
                    continue
                if sd <= r.print_day <= sd + 2 and mid in r.verifies:
                    self.verified.add((sd, mid))
                    self.s.gold += 1
                    self._mark_done_mission(mid)
        self._record(d, KIND_RECEIPT)
        return True

    def select_mission(self, now: datetime, mid: str, verification: str) -> bool:
        d = self.advance(now)
        if d is None:
            return False
        sel = self.selected.setdefault(d, [])
        if len(sel) >= self.p.selections_per_day or any(m == mid for m, _ in sel):
            return False
        sel.append((mid, verification))
        return True

    def check_in(self, now: datetime, mid: str, answer: str, no_shopping: bool = False) -> bool:
        d = self.advance(now)
        if d is None:
            return False
        sel = dict(self.selected.get(d, []))
        if mid not in sel or (d, mid) in self.checked:
            return False
        self.checked.add((d, mid))
        if answer == ANS_DONE and sel[mid] != VERIF_RECEIPT:
            self.s.white_pressed += 1
            w = week_of(d)
            if (self.white_by_day.get(d, 0) < self.p.white_per_day
                    and self.white_by_week.get(w, 0) < self.p.white_per_week):
                self.white_by_day[d] = self.white_by_day.get(d, 0) + 1
                self.white_by_week[w] = self.white_by_week.get(w, 0) + 1
                self.s.white_counted += 1
            self._mark_done_mission(mid)
        self._record(d, KIND_NO_SHOPPING if no_shopping else KIND_MISSION)
        return True

    def snapshot(self, d: int) -> Snapshot:
        s = self.s
        return Snapshot(d, s.ice, s.shields, s.shards_exact, s.shards, s.tier, s.total_record_days,
                        len(s.arrivals), s.gold, s.white_counted,
                        s.gold * self.p.gold_points + s.white_counted * self.p.white_points,
                        s.shields_used, d in self.recorded_days)


    # ----- save / restore (v4, 17a §3) -----
    def export_state(self) -> dict:
        """Everything needed to continue the session, as JSON-ready primitives (schema STATE_VERSION).

        Parameters, the bonus function and the clock are not saved: the caller passes them again on restore.
        Lists that come from sets are sorted so that the same state always gives the same JSON.
        """
        s = self.s

        def kv(m: Dict[int, int]) -> list:
            return [{"key": k, "value": m[k]} for k in sorted(m)]

        return {
            "version": STATE_VERSION,
            "firstDay": self.first_day,
            "lastStartedDay": self.last_started,
            "lastSettledDay": self.last_settled,
            "ice": s.ice,
            "shields": s.shields,
            "tier": s.tier,
            "shardsExact": s.shards_exact,
            "totalRecordDays": s.total_record_days,
            "streak": s.streak,
            "gapDays": s.gap_days,
            "gapMelted": s.gap_melted,
            "comebacks": s.comebacks,
            "shieldsUsed": s.shields_used,
            "gold": s.gold,
            "whitePressed": s.white_pressed,
            "whiteCounted": s.white_counted,
            "consecutiveWeeks": s.consecutive_weeks,
            "weeklyPending": s.weekly_pending,
            "weeklyIndex": s.weekly_index,
            "lastArrivalWeek": s.last_arrival_week,
            "clockRollbacks": s.clock_rollbacks,
            "lateBonusReceipts": s.late_bonus_receipts,
            "kindsUsed": sorted(s.kinds_used),
            "doneMissions": sorted(s.done_missions),
            "recordedDays": sorted(self.recorded_days),
            "weekRecordDays": kv(s.week_record_days),
            "whiteByDay": kv(self.white_by_day),
            "whiteByWeek": kv(self.white_by_week),
            "arrivals": [{"species": a.species, "day": a.day, "reason": a.reason} for a in s.arrivals],
            "milestoneQueue": list(s.milestone_queue),
            "receipts": [{"receiptId": r.receipt_id, "printDay": r.print_day,
                          "scanDay": r.scan_day if r.scan_day is not None else r.print_day,
                          "verifies": list(r.verifies)} for r in self.receipts.values()],
            "selected": [{"day": d, "missionId": m, "verification": v}
                         for d in sorted(self.selected) for m, v in self.selected[d]],
            "checked": [{"day": d, "missionId": m} for d, m in sorted(self.checked)],
            "verified": [{"day": d, "missionId": m} for d, m in sorted(self.verified)],
            "tierLog": [{"day": d, "fromTier": a, "toTier": b} for d, a, b in self.tier_log],
            "comebackLog": [{"day": d, "amount": x} for d, x in self.comeback_log],
        }

    def export_json(self) -> str:
        return json.dumps(self.export_state(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def restore(cls, state, bonus_fn: BonusFn, p: Params = DEFAULT,
                on_day_settled: Optional[Callable[["Session", int], None]] = None,
                clock_trusted: bool = True) -> "Session":
        """Rebuild a session from export_state() / export_json(). Does not re-run onboarding."""
        if isinstance(state, str):
            state = json.loads(state)
        if state.get("version") != STATE_VERSION:
            raise ValueError(f"unsupported state version {state.get('version')!r} (expected {STATE_VERSION})")
        x = cls(None, bonus_fn, p, on_day_settled, clock_trusted, _restoring=True)
        s = x.s
        x.first_day = int(state["firstDay"])
        x.last_started = int(state["lastStartedDay"])
        x.last_settled = int(state["lastSettledDay"])
        s.ice = float(state["ice"])
        s.shields = int(state["shields"])
        s.tier = int(state["tier"])
        s.shards_exact = float(state["shardsExact"])
        for k in ("totalRecordDays", "streak", "gapDays", "comebacks", "shieldsUsed", "gold", "whitePressed",
                  "whiteCounted", "consecutiveWeeks", "weeklyPending", "weeklyIndex", "lastArrivalWeek",
                  "clockRollbacks", "lateBonusReceipts"):
            setattr(s, _snake(k), int(state[k]))
        s.gap_melted = float(state["gapMelted"])
        s.kinds_used = set(state["kindsUsed"])
        s.done_missions = set(state["doneMissions"])
        x.recorded_days = set(int(d) for d in state["recordedDays"])
        s.week_record_days = {int(e["key"]): int(e["value"]) for e in state["weekRecordDays"]}
        x.white_by_day = {int(e["key"]): int(e["value"]) for e in state["whiteByDay"]}
        x.white_by_week = {int(e["key"]): int(e["value"]) for e in state["whiteByWeek"]}
        unknown = sorted(({a["species"] for a in state["arrivals"]} | set(state["milestoneQueue"])) - set(SPECIES))
        if unknown:   # e.g. a Japanese name from a pre-id build; the caller decides whether to start over
            raise ValueError(f"unknown species id(s) in state: {unknown}")
        s.arrivals = [Arrival(a["species"], int(a["day"]), a["reason"]) for a in state["arrivals"]]
        s.milestone_queue = list(state["milestoneQueue"])
        x.receipts = {}
        for r in state["receipts"]:
            x.receipts[r["receiptId"]] = Receipt(r["receiptId"], int(r["printDay"]), tuple(r["verifies"]),
                                                 int(r["scanDay"]))
        x.selected = {}
        for e in state["selected"]:
            x.selected.setdefault(int(e["day"]), []).append((e["missionId"], e["verification"]))
        x.checked = {(int(e["day"]), e["missionId"]) for e in state["checked"]}
        x.verified = {(int(e["day"]), e["missionId"]) for e in state["verified"]}
        x.tier_log = [(int(e["day"]), int(e["fromTier"]), int(e["toTier"])) for e in state["tierLog"]]
        x.comeback_log = [(int(e["day"]), int(e["amount"])) for e in state["comebackLog"]]
        return x


def _snake(name: str) -> str:
    return "".join("_" + c.lower() if c.isupper() else c for c in name)


# ---------------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------------

START = date(2026, 10, 27)   # Tuesday -> day 7 of the run is the first Monday
DAYS = 56
B_STANDIN = 2.5              # weekly B stand-in when the week has >= 1 receipt (see md §2)
S_MISSIONS = ["F07", "F08", "L01", "L05", "P01", "P04", "E01", "E02", "E03", "E04", "E06", "E07",
              "E08", "E09", "E10", "M01", "M02", "M03", "M04", "M05", "S02", "S03"]
R_MISSIONS = ["F01", "F02", "F03", "F04", "F05", "F06", "F09", "L04", "P02", "P03", "S01"]

Event = Tuple[datetime, str, tuple]   # (instant, op, args)


def at(i: int, hh: int, mm: int = 0) -> datetime:
    """Instant on calendar day START+i at hh:mm JST (hh may be >= 24 for after midnight)."""
    return datetime.combine(START + timedelta(days=i), datetime.min.time(), JST) + timedelta(hours=hh, minutes=mm)


class EventBuilder:
    def __init__(self) -> None:
        self.ev: List[Event] = []
        self.si = 0
        self.ri = 0
        self.rc = 0

    def s_mission(self) -> str:
        m = S_MISSIONS[self.si % len(S_MISSIONS)]
        self.si += 1
        return m

    def r_mission(self) -> str:
        m = R_MISSIONS[self.ri % len(R_MISSIONS)]
        self.ri += 1
        return m

    def rid(self) -> str:
        self.rc += 1
        return f"r{self.rc:03d}"

    def shop_day(self, i: int, with_mission: bool = True, late: bool = False) -> None:
        """Select an R mission in the morning, scan a receipt that verifies it, check in."""
        pd = day_of_date(START) + i
        if with_mission:
            m = self.r_mission()
            self.ev.append((at(i, 8), "select", (m, VERIF_RECEIPT)))
            self.ev.append((at(i, 18, 30), "receipt", (self.rid(), pd, (m,))))
            self.ev.append((at(i, 25, 30) if late else at(i, 21), "checkin", (m, ANS_DONE, False)))
        else:
            self.ev.append((at(i, 18, 30), "receipt", (self.rid(), pd, ())))

    def mission_day(self, i: int, answer: str = ANS_DONE, no_shopping: bool = False, late: bool = False) -> None:
        m = self.s_mission()
        self.ev.append((at(i, 8), "select", (m, VERIF_SELF)))
        self.ev.append((at(i, 25, 30) if late else at(i, 21), "checkin", (m, answer, no_shopping)))

    def honest_day(self, i: int) -> None:
        """The 'daily' persona's day: shop Tue/Fri/Sun, no-shopping check-in Mon, missions otherwise."""
        wd = (START + timedelta(days=i)).weekday()   # Mon=0
        if wd in (1, 4, 6):
            self.shop_day(i)
        elif wd == 0:
            self.mission_day(i, no_shopping=True)
        else:
            self.mission_day(i)


def persona_events(name: str) -> List[Event]:
    b = EventBuilder()
    if name == "daily":
        for i in range(DAYS):
            b.honest_day(i)
    elif name == "casual":
        rng = random.Random(15)
        for w in range(DAYS // 7):
            days = sorted(rng.sample(range(7), 4))
            for k, j in enumerate(days):
                i = w * 7 + j
                if k % 2 == 0:
                    b.shop_day(i, late=(k == 2))
                else:
                    b.mission_day(i, answer=[ANS_DONE, ANS_FAILED, ANS_PARTIAL][(w + k) % 3],
                                  late=(w % 2 == 1), no_shopping=(w % 3 == 0))
    elif name == "twice_weekly":
        for i in range(DAYS):
            if (START + timedelta(days=i)).weekday() in (0, 3):
                b.shop_day(i, with_mission=False)
    elif name == "weekday_only":
        for i in range(DAYS):
            wd = (START + timedelta(days=i)).weekday()
            if wd == 2:
                b.shop_day(i)
            elif wd < 5:
                b.mission_day(i, answer=ANS_DONE if wd != 4 else ANS_FAILED, no_shopping=(wd == 0))
    elif name == "lapsed":
        for i in list(range(0, 21)) + list(range(35, DAYS)):
            b.honest_day(i)
    elif name == "returner":
        for i in list(range(0, 7)) + list(range(37, DAYS)):
            b.honest_day(i)
    elif name == "onboarding_quitter":
        for i in range(3):
            b.honest_day(i)
    elif name == "cheater":
        for i in range(DAYS):
            pd = day_of_date(START) + i
            ms = [b.s_mission() for _ in range(5)]
            for m in ms:                                   # only 2 selections accepted
                b.ev.append((at(i, 7), "select", (m, VERIF_SELF)))
            for m in ms + ms:                              # lies "done" twice on everything
                b.ev.append((at(i, 21), "checkin", (m, ANS_DONE, False)))
            b.ev.append((at(i, 21, 5), "checkin", ("F01", ANS_DONE, False)))   # never selected
            for k in range(4):                             # receipt spam, incl. a duplicate id
                rid = f"c{i:02d}-{min(k, 2)}"
                b.ev.append((at(i, 12 + k), "receipt", (rid, pd - (k % 2) * 3, ("F01", "F02"))))
            b.ev.append((at(i, 26, 30), "receipt", (f"c{i:02d}-late", pd, ())))  # 02:30 -> same app day
            b.ev.append((at(i, 26, 59), "checkin", (ms[0], ANS_DONE, True)))      # 02:59 -> same app day
    else:
        raise KeyError(name)
    b.ev.sort(key=lambda e: e[0])
    return b.ev


PERSONAS = ["daily", "casual", "twice_weekly", "weekday_only", "lapsed", "returner", "cheater",
            "onboarding_quitter"]
PERSONA_JA = {"daily": "毎日（7/7）", "casual": "気まぐれ（週4・乱数）", "twice_weekly": "週2（月木のまとめ買い）",
              "weekday_only": "平日のみ（5/7）", "lapsed": "3週→14日休み→毎日", "returner": "1週→30日休み→毎日",
              "cheater": "ずる（連打・嘘）", "onboarding_quitter": "3日で離脱"}
LAPSE = {"lapsed": (21, 35), "returner": (7, 37)}   # [first off day, return day) as run indices


def standin_bonus(week: int, receipts: List[Receipt]) -> float:
    return B_STANDIN if receipts else 0.0


@dataclass
class RunResult:
    name: str
    snaps: List[Snapshot]
    session: Session


def run_events(events: Sequence[Event], p: Params = DEFAULT, bonus_fn: BonusFn = standin_bonus) -> RunResult:
    snaps: List[Snapshot] = []
    first = day_of_date(START)
    last = first + DAYS - 1

    def cb(sess: Session, d: int) -> None:
        if first <= d <= last:
            snaps.append(sess.snapshot(d))

    sess = Session(at(0, 7), bonus_fn, p, cb)
    for t, op, a in events:
        if op == "receipt":
            sess.scan_receipt(t, Receipt(a[0], a[1], tuple(a[2])))
        elif op == "select":
            sess.select_mission(t, a[0], a[1])
        elif op == "checkin":
            sess.check_in(t, a[0], a[1], a[2])
    sess.advance(at(DAYS, 4))
    assert [s.day for s in snaps] == list(range(first, last + 1)), "every day settled exactly once"
    return RunResult("", snaps, sess)


def run_persona(name: str, p: Params = DEFAULT) -> RunResult:
    r = run_events(persona_events(name), p)
    r.name = name
    return r


# ---------------------------------------------------------------------------
# Metrics and target checks
# ---------------------------------------------------------------------------

def recovery_days(r: RunResult) -> Optional[int]:
    if r.name not in LAPSE:
        return None
    off, back = LAPSE[r.name]
    pre = r.snaps[off - 1].ice
    for i in range(back, DAYS):
        if r.snaps[i].ice >= pre - 1e-9:
            return i - back + 1
    return None


def flicker_min_gap(r: RunResult) -> Optional[int]:
    """Smallest number of days between two opposite-direction tier changes."""
    log = r.session.tier_log
    best = None
    for (d1, a1, b1), (d2, a2, b2) in zip(log, log[1:]):
        if (b1 > a1) != (b2 > a2):
            g = d2 - d1
            best = g if best is None else min(best, g)
    return best


def summarize(r: RunResult) -> dict:
    s = r.session
    first = day_of_date(START)
    return {
        "persona": r.name,
        "ice_d1_3_7_14_28_56": [r.snaps[i].ice for i in (0, 2, 6, 13, 27, 55)],
        "final_ice": r.snaps[-1].ice,
        "min_ice": min(x.ice for x in r.snaps),
        "record_days": r.snaps[-1].total_record_days,
        "shards": r.snaps[-1].shards,
        "shields_used": r.snaps[-1].shields_used,
        "penguins": r.snaps[-1].penguins,
        "arrivals": [(a.day - first + 1, a.species, a.reason) for a in s.s.arrivals],
        "queued": list(s.s.milestone_queue) + (["weekly×%d" % s.s.weekly_pending] if s.s.weekly_pending else []),
        "tier_changes": [(d - first + 1, a, b) for d, a, b in s.tier_log if first <= d < first + DAYS],
        "stamp_points": r.snaps[-1].stamp_points,
        "gold": r.snaps[-1].gold,
        "white": r.snaps[-1].white_counted,
        "comebacks": [(d - first + 1, x) for d, x in s.comeback_log],
        "recovery_days": recovery_days(r),
        "flicker_min_gap": flicker_min_gap(r),
    }


def remove_day(events: Sequence[Event], i: int) -> List[Event]:
    lo, hi = at(i, 3), at(i + 1, 3)
    return [e for e in events if not (lo <= e[0] < hi)]


def skip_never_beats(name: str, p: Params = DEFAULT) -> List[str]:
    """Remove each record day in turn; ice and ice+shards must never end up higher on any later day."""
    ev = persona_events(name)
    base = run_events(ev, p)
    bad = []
    for i, snap in enumerate(base.snaps):
        if not snap.recorded:
            continue
        alt = run_events(remove_day(ev, i), p)
        for j in range(i, DAYS):
            a, b = alt.snaps[j], base.snaps[j]
            if a.ice > b.ice + 1e-9 or a.ice + a.shards_exact > b.ice + b.shards_exact + 1e-9:
                bad.append(f"{name}: skipping day {i + 1} gives more ice on day {j + 1}")
                break
    return bad


def check_targets(results: Dict[str, RunResult], p: Params = DEFAULT) -> List[Tuple[str, bool, str]]:
    out = []
    d = results["daily"]
    sn = d.snaps
    vis = (sn[0].ice > p.initial and sn[0].penguins >= 1 and sn[2].penguins >= 2
           and sn[6].ice >= 106 and sn[13].ice >= 112 and sn[13].penguins >= 3)
    out.append(("毎日の人に 1/3/7/14 日目の目に見える進み（15a §2.2：1 日目に氷+、3 日目までに 2 羽目、14 日目に 3 羽以上）", vis,
                f"ice={[sn[i].ice for i in (0, 2, 6, 13)]} penguins={[sn[i].penguins for i in (0, 2, 6, 13)]}"))
    c = results["casual"].snaps
    out.append(("気まぐれの人も 7・14 日目に氷が初期以上", c[6].ice >= p.initial and c[13].ice >= p.initial,
                f"ice d7={c[6].ice} d14={c[13].ice}"))
    rd = recovery_days(results["lapsed"])
    out.append(("14 日休んだ人が休む前の氷に戻るまで 7 日以内（15a §2.3 の目安 5 日）", rd is not None and rd <= 7, f"{rd} 日"))
    ch, da = results["cheater"].snaps, results["daily"].snaps
    ok = all(x.ice <= y.ice + 1e-9 and x.shards <= y.shards and x.penguins <= y.penguins
             and x.stamp_points <= y.stamp_points for x, y in zip(ch, da))
    out.append(("ずるは毎日の人を超えない（氷・かけら・ペンギン・スタンプ点、全日）", ok,
                f"final ice {ch[-1].ice} vs {da[-1].ice}, stamps {ch[-1].stamp_points} vs {da[-1].stamp_points}, "
                f"penguins {ch[-1].penguins} vs {da[-1].penguins}"))
    bad = []
    for n in PERSONAS:
        bad += skip_never_beats(n, p)
    out.append(("記録を 1 日抜いても、その後の氷（＋かけら）が増える日はない（全人物・全記録日）", not bad,
                "; ".join(bad[:3]) or "違反 0"))
    gaps = [flicker_min_gap(r) for r in results.values()]
    gaps = [g for g in gaps if g is not None]
    out.append(("段のちらつきなし（逆向きの段の変化の間隔が 3 日以上）", all(g >= 3 for g in gaps),
                f"最小間隔 {min(gaps) if gaps else 'なし'} 日"))
    return out


def run_all(p: Params = DEFAULT) -> Dict[str, RunResult]:
    return {n: run_persona(n, p) for n in PERSONAS}


if __name__ == "__main__":
    import dataclasses
    import json
    import sys
    for label, p in (("decided", DECIDED), ("v3 (15d)", V3), ("v4 default (17a)", DEFAULT), ("v4 deferred B", DEFERRED_B)):
        res = run_all(p)
        print("==", label)
        for n, r in res.items():
            print(json.dumps(summarize(r), ensure_ascii=False))
        for t, ok, info in check_targets(res, p):
            print("PASS" if ok else "FAIL", t, "|", info)
    sys.exit(0)
