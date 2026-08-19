# -*- coding: utf-8 -*-
"""Sinkronkan makanan yang ada di CSV tapi belum ada di Supabase.

AMAN: hanya INSERT baris yang namanya belum ada. Tidak pernah UPDATE
maupun DELETE, sehingga baris hasil belajar (source='llm_estimate')
tidak akan tersentuh.

Jalankan: python scripts/sync_csv_to_supabase.py [--apply]
Tanpa --apply hanya menampilkan rencana (dry-run).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, Food  # noqa: E402

CSV_PATH = Path(__file__).resolve().parent.parent / "dataset" / "foods_combined.csv"


def _f(v, default=None):
    try:
        return float(v) if v not in (None, "") else default
    except (TypeError, ValueError):
        return default


def main(apply: bool) -> int:
    with open(CSV_PATH, encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("name") or "").strip()]

    db = SessionLocal()
    try:
        ada = {(n or "").strip().lower() for (n,) in db.query(Food.name).all() if n}
        kurang = [r for r in rows if r["name"].strip().lower() not in ada]

        print(f"CSV            : {len(rows)} baris")
        print(f"Supabase       : {len(ada)} nama")
        print(f"Belum ada di DB: {len(kurang)}")
        for r in kurang:
            print(f"   + {r['name']}  ({r.get('cal')} kkal, {r.get('source')})")

        if not kurang:
            print("\nSudah sinkron, tidak ada yang perlu ditambahkan.")
            return 0
        if not apply:
            print("\n[DRY-RUN] Tidak ada yang ditulis. Jalankan ulang dengan --apply.")
            return 0

        for r in kurang:
            db.add(Food(
                name=r["name"].strip().lower(),
                name_aliases=(r.get("name_aliases") or "").strip() or None,
                cal=_f(r.get("cal")),
                protein=_f(r.get("protein"), 0.0),
                carbs=_f(r.get("carbs"), 0.0),
                fat=_f(r.get("fat"), 0.0),
                default_portion_g=_f(r.get("default_portion_g"), 100.0),
                source=(r.get("source") or "unknown").strip(),
                is_indonesian=str(r.get("is_indonesian", "")).strip().lower() == "true",
            ))
        db.commit()
        print(f"\n[OK] {len(kurang)} makanan ditambahkan.")
        print(f"     Total baris Supabase sekarang: {db.query(Food).count()}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[GAGAL] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
