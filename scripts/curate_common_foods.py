"""
Kurasi makanan umum Indonesia ke dataset/foods_combined.csv.

Masalah yang diselesaikan:
1. Makanan sehari-hari yang paling sering di-log justru tidak ada di dataset
   (nasi putih, teh manis, kopi susu, udang goreng, ayam goreng, dll) sehingga
   jatuh ke USDA/LLM — boros token dan hasilnya sering tidak masuk akal.
2. Kolom name_aliases kosong di semua baris — sistem alias di matcher mati.
3. Beberapa baris makanan umum punya kalori jelas salah (mis. rendang sapi
   601.5 kcal/100g) yang memicu LLM validation call setiap kali dicocokkan.

Nilai gizi per 100g siap-makan, diselaraskan dengan tabel kalibrasi di
app/validator.py (NUTRITION_SYSTEM_PROMPT) dan TKPI/referensi umum.

Idempotent — aman dijalankan berulang:
    python scripts/curate_common_foods.py

Setelah CSV berubah, sinkronkan ke Supabase (opsional, CSV adalah sumber
utama cache matcher):
    python scripts/import_dataset.py dataset/foods_combined.csv replace
"""

import csv
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'foods_combined.csv')
SOURCE = "curated_common"

# ─── Makanan baru: (name, aliases, kcal, protein, carbs, fat, portion_g) ─────
# Aliases dipisah "|" — dicek exact match oleh matcher (case-insensitive).
NEW_FOODS: list[tuple[str, str, float, float, float, float, float]] = [
    # Makanan pokok / karbohidrat
    ("nasi putih",      "nasi hangat|nasi putih hangat|steamed rice",          130, 2.4, 28.6, 0.2, 200),
    ("nasi kuning",     "",                                                    150, 2.7, 26.0, 3.5, 200),
    ("lontong",         "lontong sayur polos",                                 110, 2.0, 23.0, 0.3, 200),
    ("ketupat",         "",                                                    110, 2.0, 23.0, 0.3, 200),
    ("mie instan",      "indomie|mi instan|mie instant|indomie goreng",        185, 4.0, 25.0, 8.0, 200),
    ("mie rebus",       "mi rebus|mie kuah",                                   120, 4.0, 18.0, 3.5, 300),
    ("roti tawar",      "roti putih|roti tawar putih",                         265, 8.0, 50.0, 3.0, 70),
    ("kentang goreng",  "french fries",                                        312, 3.4, 41.0, 15.0, 100),

    # Protein hewani
    ("ayam goreng",     "ayam goreng biasa|fried chicken",                     245, 28.0, 1.5, 14.0, 100),
    ("ayam bakar",      "",                                                    210, 28.0, 2.0, 10.0, 100),
    ("ayam geprek",     "",                                                    250, 20.0, 10.0, 16.0, 150),
    ("telur ceplok",    "telor ceplok|telur mata sapi|ceplok telur",           190, 13.6, 0.8, 14.5, 55),
    ("telur balado",    "telor balado",                                        190, 11.0, 5.0, 14.0, 70),
    ("udang",           "udang segar|udang rebus|shrimp",                       91, 21.0, 0.1, 1.0, 100),
    ("udang goreng",    "udang goreng tepung",                                 240, 18.0, 12.0, 13.0, 75),
    ("cumi-cumi",       "cumi|sotong",                                          92, 15.6, 3.1, 1.4, 100),
    ("kerang hijau",    "",                                                     86, 14.0, 3.0, 2.0, 100),
    ("ceker ayam",      "ceker|cakar ayam",                                    215, 19.0, 0.2, 15.0, 60),
    ("kikil sapi",      "kikil",                                               150, 23.0, 0.0, 6.5, 80),
    ("babat sapi",      "babat",                                               113, 16.0, 0.0, 5.0, 80),
    ("paru sapi",       "paru",                                                120, 17.0, 0.0, 5.0, 80),
    ("usus ayam",       "usus",                                                130, 18.0, 0.0, 6.0, 80),
    ("darah ayam",      "saren|marus|darah",                                   105, 16.0, 1.0, 4.0, 50),
    ("ikan goreng",     "",                                                    220, 22.0, 8.0, 11.0, 100),
    ("lele goreng",     "pecel lele",                                          204, 18.0, 4.0, 13.0, 100),
    ("rendang",         "rendang daging",                                      195, 19.0, 5.0, 11.0, 100),

    # Berkuah
    ("soto ayam",       "soto|soto ayam bening",                                65, 4.5, 5.0, 2.5, 350),
    ("bakso kuah",      "bakso sapi kuah",                                      80, 5.0, 6.0, 3.5, 350),
    ("opor ayam",       "",                                                    163, 12.0, 4.0, 11.0, 200),
    ("gulai ayam",      "",                                                    165, 13.0, 3.0, 11.0, 200),

    # Sayur & pelengkap
    ("capcay",          "capcai|cap cay",                                       55, 3.0, 6.0, 2.0, 200),
    ("sayur lodeh",     "lodeh",                                                60, 2.0, 6.0, 3.5, 200),
    ("tempe orek",      "orek tempe|tempe kering",                             210, 12.0, 12.0, 12.0, 50),
    ("sambal",          "sambel|sambal terasi",                                120, 2.0, 10.0, 8.0, 15),
    ("kerupuk",         "krupuk|kerupuk putih",                                480, 1.0, 60.0, 25.0, 20),
    ("pisang",          "pisang ambon|banana",                                  89, 1.1, 23.0, 0.3, 100),

    # Minuman
    ("teh manis",       "teh manis hangat|teh manis panas|es teh|es teh manis|teh manis dingin|teh es", 35, 0.0, 9.0, 0.0, 250),
    ("teh susu",        "teh tarik",                                            55, 1.5, 9.0, 1.5, 250),
    ("kopi susu",       "es kopi susu|kopi susu gula aren",                     55, 1.5, 8.0, 2.0, 250),
    ("kopi dingin",     "es kopi",                                              40, 0.5, 8.0, 0.5, 250),
    ("kopi hitam",      "kopi|kopi pahit|americano",                             2, 0.1, 0.4, 0.0, 250),
    ("es jeruk",        "jus jeruk|jeruk peras",                                45, 0.3, 11.0, 0.0, 250),
    ("jus alpukat",     "",                                                     95, 1.0, 8.0, 6.5, 300),
    ("air putih",       "air mineral|air",                                       0, 0.0, 0.0, 0.0, 250),
]

# ─── Tambah alias ke baris yang sudah ada: {name: "alias1|alias2"} ────────────
ALIAS_UPDATES: dict[str, str] = {
    "kangkung tumis":    "tumis kangkung|cah kangkung",
    "susu sapi":         "susu|susu putih|susu segar",
    "telur dadar":       "telor dadar|omelet",
    "nasi":              "nasi biasa",
    "bakso":             "baso|bakso sapi",
    "cumi-cumi goreng":  "cumi goreng",
}

# ─── Koreksi kalori yang jelas salah pada makanan umum ────────────────────────
# {name: (kcal, protein, carbs, fat)} — nilai per 100g siap-makan, mengikuti
# kalibrasi validator.py. Nilai lama memicu LLM validation call setiap match.
VALUE_FIXES: dict[str, tuple[float, float, float, float]] = {
    "rendang sapi":      (195, 19.0, 5.0, 11.0),   # sebelumnya 601.5 kcal/100g
    "telur ayam ceplok": (190, 13.6, 0.8, 14.5),   # sebelumnya 383 kcal/100g
    "mie goreng":        (170, 4.5, 24.0, 6.5),    # sebelumnya 468 kcal/100g
}


def merge_aliases(existing: str, new: str) -> str:
    seen, merged = set(), []
    for part in (existing or "").split("|") + (new or "").split("|"):
        p = part.strip()
        if p and p.lower() not in seen:
            seen.add(p.lower())
            merged.append(p)
    return "|".join(merged)


def main():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    by_name = {(r["name"] or "").strip().lower(): r for r in rows}
    added, aliased, fixed = 0, 0, 0

    # 1. Koreksi nilai salah
    for name, (kcal, p, c, fat) in VALUE_FIXES.items():
        row = by_name.get(name)
        if row and float(row["cal"] or 0) != kcal:
            print(f"[fix]   {name}: {row['cal']} -> {kcal} kcal/100g")
            row.update(cal=str(kcal), protein=str(p), carbs=str(c), fat=str(fat))
            fixed += 1

    # 2. Tambah alias ke baris existing
    for name, aliases in ALIAS_UPDATES.items():
        row = by_name.get(name)
        if row:
            merged = merge_aliases(row.get("name_aliases", ""), aliases)
            if merged != (row.get("name_aliases") or ""):
                print(f"[alias] {name}: '{row.get('name_aliases', '')}' -> '{merged}'")
                row["name_aliases"] = merged
                aliased += 1
        else:
            print(f"[alias] SKIP '{name}' — tidak ditemukan di CSV")

    # 3. Tambah makanan baru (skip jika nama sudah ada)
    for name, aliases, kcal, p, c, fat, portion in NEW_FOODS:
        if name.lower() in by_name:
            print(f"[new]   SKIP '{name}' — sudah ada")
            continue
        row = {
            "id": str(uuid.uuid4()),
            "name": name,
            "name_aliases": aliases,
            "cal": str(float(kcal)),
            "protein": str(float(p)),
            "carbs": str(float(c)),
            "fat": str(float(fat)),
            "default_portion_g": str(float(portion)),
            "source": SOURCE,
            "is_indonesian": "True",
        }
        rows.append(row)
        by_name[name.lower()] = row
        added += 1
        print(f"[new]   + {name} ({kcal} kcal/100g)" + (f" alias: {aliases}" if aliases else ""))

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSelesai: +{added} makanan baru, {aliased} baris dapat alias, "
          f"{fixed} nilai dikoreksi. Total {len(rows)} baris.")


if __name__ == "__main__":
    main()
