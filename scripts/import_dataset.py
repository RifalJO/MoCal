# scripts/import_dataset.py
# Import CSV dataset ke PostgreSQL
# Jalankan SEKALI setelah database dibuat

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db, Food


# ─── Konfigurasi ──────────────────────────────────────────────────────────────
CSV_PATH = "dataset_clean/foods_cleaned_nutrients.csv"   # ← nama file terbaru

# Kolom CSV sudah sesuai struktur DB — tidak perlu mapping tambahan
# Kolom: id, name, name_aliases, cal, protein, carbs, fat, default_portion_g, source, is_indonesian


def import_csv(csv_path: str):
    print(f"📂 Membaca file: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")

    print(f"📊 Total baris di CSV: {len(df)}")
    print(f"📋 Kolom tersedia: {list(df.columns)}")

    # ── Normalisasi nama kolom ─────────────────────────────────────────────
    df.columns = df.columns.str.strip().str.lower()

    # ── Cleaning dasar ────────────────────────────────────────────────────
    df["name"] = df["name"].astype(str).str.lower().str.strip()
    df = df.dropna(subset=["name"])
    df = df[df["name"] != ""]
    df = df.drop_duplicates(subset=["name"], keep="first")

    # ── Isi nilai default jika kolom kosong ───────────────────────────────
    df["protein"]         = pd.to_numeric(df.get("protein", 0), errors="coerce").fillna(0.0)
    df["carbs"]           = pd.to_numeric(df.get("carbs", 0), errors="coerce").fillna(0.0)
    df["fat"]             = pd.to_numeric(df.get("fat", 0), errors="coerce").fillna(0.0)
    df["cal"]             = pd.to_numeric(df.get("cal"), errors="coerce")  # NULL jika kosong
    df["default_portion_g"] = pd.to_numeric(df.get("default_portion_g", 100), errors="coerce").fillna(100.0)
    df["source"]          = df.get("source", "manual").fillna("manual")
    df["is_indonesian"]   = df.get("is_indonesian", False).fillna(False).astype(bool)
    df["name_aliases"]    = df.get("name_aliases", None)

    print(f"✅ Setelah cleaning: {len(df)} baris")
    print(f"⚠️  Baris dengan cal NULL: {df['cal'].isna().sum()}")

    # ── Import ke database ────────────────────────────────────────────────
    db = SessionLocal()
    success, skipped = 0, 0

    try:
        for _, row in df.iterrows():
            # Cek apakah sudah ada
            exists = db.query(Food).filter(Food.name == row["name"]).first()
            if exists:
                skipped += 1
                continue

            food = Food(
                name              = row["name"],
                name_aliases      = row.get("name_aliases") if pd.notna(row.get("name_aliases", None)) else None,
                cal               = float(row["cal"])  if pd.notna(row["cal"]) else None,
                protein           = float(row["protein"]),
                carbs             = float(row["carbs"]),
                fat               = float(row["fat"]),
                default_portion_g = float(row["default_portion_g"]),
                source            = str(row["source"]),
                is_indonesian     = bool(row["is_indonesian"]),
            )
            db.add(food)
            success += 1

            # Commit per 500 baris agar tidak berat
            if success % 500 == 0:
                db.commit()
                print(f"   → {success} baris diimport...")

        db.commit()
        print(f"\n✅ Import selesai!")
        print(f"   Berhasil diimport : {success} baris")
        print(f"   Dilewati (duplikat): {skipped} baris")
        print(f"   Total di DB        : {db.query(Food).count()} makanan")

    except Exception as e:
        db.rollback()
        print(f"❌ Error saat import: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Inisialisasi tabel dulu
    init_db()

    # Jalankan import
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    import_csv(path)
