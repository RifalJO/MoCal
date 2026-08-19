# -*- coding: utf-8 -*-
"""Audit konsistensi nilai gizi di tabel foods — deterministik, tanpa token.

Nilai gizi yang benar harus konsisten dengan dirinya sendiri:
kcal ≈ 4*protein + 4*karbohidrat + 9*lemak (faktor Atwater).
Selisih liar menandakan salah satu angkanya rusak.

Klasifikasi:
  [A] MAKRO RUSAK      Atwater > 900 kkal/100g (mustahil secara fisik)
                       -> hanya dilaporkan, perlu tinjauan manual
  [B] KCAL RUSAK       kcal tersimpan DI LUAR rentang wajar kategorinya,
                       sementara Atwater justru DI DALAM rentang itu
                       -> aman diperbaiki: kcal := Atwater
  [C] AMBIGU           tidak konsisten tapi tak jelas mana yang salah
                       -> hanya dilaporkan

Jalankan: python scripts/audit_nutrisi.py [--apply]
Tanpa --apply hanya menampilkan laporan (dry-run).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, Food          # noqa: E402
from app.validator import atwater_kcal, is_kcal_consistent, get_category  # noqa: E402

ATWATER_MAX = 900.0     # batas fisik kkal per 100 g


def klasifikasi(nama, kcal, atw):
    """Tentukan mana yang rusak: kcal atau makronya.

    Rentang kategori dipakai sebagai wasit. Nilai yang jatuh DI LUAR rentang
    wajar kategorinya adalah yang mencurigakan; kalau nilai satunya justru
    masuk rentang, ia dipakai sebagai koreksi. Tanpa wasit ini, makanan yang
    memang rendah kalori (sayur, buah) akan salah dikoreksi.
    """
    if atw > ATWATER_MAX:
        return "A"                       # makro mustahil secara fisik

    cat = get_category(nama)
    if cat:
        _, lo, hi = cat
        kcal_masuk = lo <= kcal <= hi
        atw_masuk = lo <= atw <= hi
        if not kcal_masuk and atw_masuk:
            return "B"                   # kcal meleset, Atwater masuk akal
    return "C"


def main(apply: bool) -> int:
    db = SessionLocal()
    try:
        rows = db.query(Food).all()
        ember = {"A": [], "B": [], "C": []}

        for f in rows:
            if f.cal is None:
                continue
            atw = atwater_kcal(f.protein, f.carbs, f.fat)
            if is_kcal_consistent(f.cal, f.protein, f.carbs, f.fat):
                continue
            ember[klasifikasi(f.name, f.cal, atw)].append((f, atw))

        total = sum(len(v) for v in ember.values())
        print(f"Diperiksa   : {len(rows)} baris")
        print(f"Tidak konsisten: {total}")
        print(f"   [A] makro rusak (perlu tinjauan) : {len(ember['A'])}")
        print(f"   [B] kcal rusak (aman diperbaiki) : {len(ember['B'])}")
        print(f"   [C] ambigu (perlu tinjauan)      : {len(ember['C'])}")

        for kode, judul in [("B", "AKAN DIPERBAIKI"), ("A", "PERLU TINJAUAN MANUAL"), ("C", "AMBIGU")]:
            if not ember[kode]:
                continue
            print(f"\n[{kode}] {judul}:")
            for f, atw in sorted(ember[kode], key=lambda x: x[0].name)[:15]:
                panah = f"-> {atw:.1f}" if kode == "B" else ""
                print(f"   {f.name[:38]:<40} kcal={f.cal:>7.1f}  Atwater={atw:>7.1f}  {panah}  [{f.source}]")
            if len(ember[kode]) > 15:
                print(f"   ... dan {len(ember[kode]) - 15} lainnya")

        if not ember["B"]:
            print("\nTidak ada yang bisa diperbaiki otomatis.")
            return 0
        if not apply:
            print(f"\n[DRY-RUN] {len(ember['B'])} baris siap diperbaiki. Jalankan ulang dengan --apply.")
            return 0

        for f, atw in ember["B"]:
            f.cal = round(atw, 1)
        db.commit()
        print(f"\n[OK] {len(ember['B'])} baris diperbaiki (kcal dihitung ulang dari makro).")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[GAGAL] {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
