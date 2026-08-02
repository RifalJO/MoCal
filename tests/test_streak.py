"""Tes compute_streak — fungsi murni penghitung hari beruntun mencatat log.

Semantik streak:
- Dihitung mundur dari `today`.
- Kalau hari ini SUDAH mencatat → hari ini ikut dihitung.
- Kalau hari ini BELUM mencatat → streak dihitung mundur dari kemarin
  (grace: streak tidak putus sebelum hari benar-benar lewat).
- Ada hari bolong → streak berhenti di situ.
"""

from datetime import date, timedelta

from app.stats import compute_streak

TODAY = date(2026, 8, 2)


def _days_back(*offsets: int) -> set[date]:
    """Helper: {TODAY - offset for offset in offsets}"""
    return {TODAY - timedelta(days=o) for o in offsets}


def test_no_logs_returns_zero():
    assert compute_streak(set(), TODAY) == 0


def test_logged_today_only():
    assert compute_streak(_days_back(0), TODAY) == 1


def test_logged_today_and_yesterday():
    assert compute_streak(_days_back(0, 1), TODAY) == 2


def test_yesterday_only_grace_still_counts():
    # Belum log hari ini (baru pagi) — streak kemarin belum putus
    assert compute_streak(_days_back(1), TODAY) == 1


def test_gap_breaks_streak():
    # Hari ini log, kemarin bolong, lusa kemarin log → streak cuma 1
    assert compute_streak(_days_back(0, 2, 3), TODAY) == 1


def test_two_days_ago_only_is_broken():
    # Terakhir log 2 hari lalu → streak sudah putus
    assert compute_streak(_days_back(2, 3, 4), TODAY) == 0


def test_long_consecutive_run():
    assert compute_streak(_days_back(0, 1, 2, 3, 4, 5, 6), TODAY) == 7


def test_future_dates_ignored():
    # Data anomali (jam server/timezone salah) tidak boleh menambah streak
    assert compute_streak(_days_back(0, -1), TODAY) == 1
