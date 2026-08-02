# app/stats.py
# Statistik gamifikasi — fungsi murni, tanpa DB/LLM (0 token).

from datetime import date, timedelta


def compute_streak(logged_dates: set[date], today: date) -> int:
    """Hitung hari beruntun (streak) user mencatat log, mundur dari `today`.

    - Hari ini sudah log → hari ini ikut dihitung.
    - Hari ini belum log → mulai hitung dari kemarin (grace: streak belum
      putus sebelum harinya benar-benar lewat).
    - Tanggal masa depan (anomali timezone) diabaikan.
    """
    if not logged_dates:
        return 0

    # Mulai dari hari ini jika sudah log; kalau belum, dari kemarin.
    cursor = today if today in logged_dates else today - timedelta(days=1)

    streak = 0
    while cursor in logged_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
