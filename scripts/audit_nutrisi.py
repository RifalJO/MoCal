# -*- coding: utf-8 -*-
"""Audit konsistensi nilai gizi di tabel foods — deterministik, tanpa token.

Nilai gizi yang benar harus konsisten dengan dirinya sendiri:
kcal ~ 4*protein + 4*karbohidrat + 9*lemak (faktor Atwater).
Selisih liar menandakan salah satu angkanya rusak.

Rentang wajar per kategori (dari app/validator.py) dipakai sebagai wasit
untuk menentukan MANA yang rusak. Tanpa wasit ini, makanan yang memang
rendah kalori (sayur, buah) akan salah dikoreksi.

Klasifikasi:
  [B] KCAL RUSAK     kcal di LUAR rentang kategori, Atwater di DALAM
                     -> kcal dihitung ulang dari makro
  [D] MAKRO MELESET  kcal di DALAM rentang kategori, Atwater di LUAR
                     -> makro diskalakan agar totalnya cocok dengan kcal,
                        komposisi P:K:L dipertahankan
  [A] MAKRO MUSTAHIL Atwater > 900 kkal/100g -> perlu tinjauan manual
  [C] AMBIGU         tidak ada dasar memutuskan -> perlu tinjauan manual

[A] dan [C] ditulis ke dataset/audit_perlu_tinjauan.csv.

Jalankan: python scripts/audit_nutrisi.py [--apply]
Tanpa --apply hanya menampilkan laporan (dry-run).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, Food                             # noqa: E402
from app.validator import atwater_kcal, is_kcal_consistent, get_category  # noqa: E402

ATWATER_MAX = 900.0
LAPORAN = Path(__file__).resolve().parent.parent / "dataset" / "audit_perlu_tinjauan.csv"


def klasifikasi(nama, kcal, atw):
    if atw > ATWATER_MAX:
        return "A"
    cat = get_category(nama)
    if cat:
        _, lo, hi = cat
        kcal_masuk = lo <= kcal <= hi
        atw_masuk = lo <= atw <= hi
        if not kcal_masuk and atw_masuk:
            return "B"
        if kcal_masuk and not atw_masuk:
            return "D"
    return "C"


def tulis_laporan(baris):
    with open(LAPORAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "source", "kcal_tersimpan", "kcal_atwater",
                    "rasio", "protein", "carbs", "fat"])
        for f, atw in sorted(baris, key=lambda x: x[0].name):
            w.writerow([f.name, f.source, f.cal, round(atw, 1),
                        round(atw / f.cal, 2) if f.cal else "",
                        f.protein, f.carbs, f.fat])
    print(f"[laporan] {len(baris)} baris perlu tinjauan manual -> {LAPORAN.name}")


def main(apply):
    db = SessionLocal()
    try:
        rows = db.query(Food).all()
        ember = {"A": [], "B": [], "C": [], "D": []}

        for f in rows:
            if f.cal is None or is_kcal_consistent(f.cal, f.protein, f.carbs, f.fat):
                continue
            atw = atwater_kcal(f.protein, f.carbs, f.fat)
            ember[klasifikasi(f.name, f.cal, atw)].append((f, atw))

        total = sum(len(v) for v in ember.values())
        print(f"Diperiksa      : {len(rows)} baris")
        print(f"Tidak konsisten: {total}")
        print(f"   [B] kcal rusak (dihitung ulang)   : {len(ember['B'])}")
        print(f"   [D] makro meleset (diskalakan)    : {len(ember['D'])}")
        print(f"   [A] makro mustahil (tinjau manual): {len(ember['A'])}")
        print(f"   [C] ambigu (tinjau manual)        : {len(ember['C'])}")

        for kode, judul in [("B", "KCAL DIHITUNG ULANG"), ("D", "MAKRO DISKALAKAN")]:
            if not ember[kode]:
                continue
            print(f"\n[{kode}] {judul}:")
            for f, atw in sorted(ember[kode], key=lambda x: x[0].name)[:12]:
                aksi = f"kcal -> {atw:.1f}" if kode == "B" else f"makro x{f.cal / atw:.2f}"
                print(f"   {f.name[:34]:<36} kcal={f.cal:>7.1f} Atwater={atw:>7.1f}  {aksi}  [{f.source}]")
            if len(ember[kode]) > 12:
                print(f"   ... dan {len(ember[kode]) - 12} lainnya")

        print()
        tulis_laporan(ember["A"] + ember["C"])

        bisa = len(ember["B"]) + len(ember["D"])
        if not bisa:
            print("Tidak ada yang bisa diperbaiki otomatis.")
            return 0
        if not apply:
            print(f"\n[DRY-RUN] {len(ember['B'])} kcal + {len(ember['D'])} makro siap diperbaiki."
                  " Jalankan ulang dengan --apply.")
            return 0

        for f, atw in ember["B"]:
            f.cal = round(atw, 1)
        for f, atw in ember["D"]:
            faktor = f.cal / atw
            f.protein = round((f.protein or 0) * faktor, 2)
            f.carbs = round((f.carbs or 0) * faktor, 2)
            f.fat = round((f.fat or 0) * faktor, 2)
        db.commit()
        print(f"\n[OK] {len(ember['B'])} kcal dihitung ulang, {len(ember['D'])} makro diskalakan.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[GAGAL] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
