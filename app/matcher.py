# app/matcher.py
# Fuzzy matching engine — cocokkan nama makanan ke database lokal

import csv
from pathlib import Path
from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session
from app.database import Food, settings, SessionLocal
import requests


# ─── Cache nama makanan (lazy load — hanya saat pertama dibutuhkan) ───────────
_food_cache: list[dict] = []
_cache_loaded: bool = False

# CSV sumber data — sama dengan yang diimport ke Supabase. Dibaca langsung
# supaya cold start serverless tidak perlu menarik 1.500+ baris dari DB.
FOODS_CSV_PATH = Path(__file__).resolve().parent.parent / "dataset" / "foods_combined.csv"


def _parse_float(value, default=None):
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _load_cache_from_csv() -> list[dict] | None:
    """Baca cache makanan dari file CSV lokal (jauh lebih cepat dari query DB
    lintas region). Return None jika file tidak ada / tidak terbaca."""
    if not FOODS_CSV_PATH.exists():
        return None
    try:
        with open(FOODS_CSV_PATH, encoding="utf-8") as f:
            return [
                {
                    "id":      row.get("id", ""),
                    "name":    (row.get("name") or "").strip().lower(),
                    "aliases": [a.strip().lower() for a in (row.get("name_aliases") or "").split("|") if a.strip()],
                    "kcal":    _parse_float(row.get("cal")),
                    "protein_g": _parse_float(row.get("protein"), 0.0),
                    "carbs_g":   _parse_float(row.get("carbs"), 0.0),
                    "fat_g":     _parse_float(row.get("fat"), 0.0),
                    "default_portion_g": _parse_float(row.get("default_portion_g"), 100.0),
                    "source":  row.get("source", "unknown"),
                }
                for row in csv.DictReader(f)
                if (row.get("name") or "").strip()
            ]
    except Exception as e:
        print(f"[cache] Gagal baca CSV ({e}) - fallback ke DB")
        return None


def load_food_cache(db: Session | None = None):
    """Load semua nama makanan ke memory untuk fuzzy matching yang cepat.
    Dipanggil otomatis saat pertama kali find_food() dipanggil.

    Prioritas: CSV lokal (cepat, tanpa network) → query DB (fallback).
    """
    global _food_cache, _cache_loaded

    if _cache_loaded:
        return

    # Coba dari CSV dulu — tanpa koneksi database sama sekali
    csv_cache = _load_cache_from_csv()
    if csv_cache:
        _food_cache = csv_cache
        _cache_loaded = True
        print(f"[OK] Cache loaded dari CSV: {len(_food_cache)} makanan")
        return

    # Fallback: query database
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        # Hanya query kolom yang dibutuhkan (lebih cepat dari .all())
        foods = db.query(
            Food.id, Food.name, Food.name_aliases,
            Food.cal, Food.protein, Food.carbs, Food.fat,
            Food.default_portion_g, Food.source
        ).all()
        _food_cache = [
            {
                "id":    str(f.id),
                "name":  (f.name or "").strip().lower(),
                "aliases": [a.strip().lower() for a in f.name_aliases.split("|") if a.strip()] if f.name_aliases else [],
                "kcal":  f.cal,
                "protein_g":  f.protein,
                "carbs_g":    f.carbs,
                "fat_g":      f.fat,
                "default_portion_g": f.default_portion_g,
                "source": f.source,
            }
            for f in foods
        ]
        _cache_loaded = True
        print(f"[OK] Cache loaded dari DB: {len(_food_cache)} makanan")
    finally:
        if own_session:
            db.close()


def _all_searchable_names() -> list[tuple[str, dict]]:
    """Gabungkan name + aliases jadi satu flat list untuk pencarian"""
    result = []
    for food in _food_cache:
        result.append((food["name"], food))
        for alias in food["aliases"]:
            if alias.strip():
                result.append((alias.strip(), food))
    return result


# ─── Step 1: Exact match ──────────────────────────────────────────────────────
def exact_match(query: str) -> dict | None:
    q = query.lower().strip()
    for food in _food_cache:
        if food["name"] == q:
            return {**food, "match_method": "exact", "match_score": 1.0}
        if q in food["aliases"]:
            return {**food, "match_method": "exact", "match_score": 1.0}
    return None


# ─── Step 2: Fuzzy match ──────────────────────────────────────────────────────
def _combined_ratio(query: str, candidate: str, **kwargs) -> float:
    """Scorer gabungan untuk nama makanan.

    token_sort_ratio saja gagal pada pola umum "query pendek vs nama entri
    panjang" ('soto ayam' vs 'soto ayam jember' cuma 77.8). token_set_ratio
    saja terlalu longgar ('soto ayam' vs 'ayam' = 100). Rata-rata keduanya:
    set-ratio menangkap subset kata, sort-ratio menghukum kandidat yang
    kehilangan/kelebihan banyak kata.
    """
    return (
        0.5 * fuzz.token_set_ratio(query, candidate)
        + 0.5 * fuzz.token_sort_ratio(query, candidate)
    )


def fuzzy_match(query: str, expected_kcal: float | None = None) -> dict | None:
    """
    Fuzzy match dengan re-ranking berbasis kalori.

    Ambil top-5 kandidat di atas threshold. Jika ada beberapa kandidat dengan
    skor hampir sama (selisih ≤ 5 poin dari terbaik) dan expected_kcal tersedia,
    pilih kandidat yang kalorinya paling dekat dengan ekspektasi — mencegah
    "nasi goreng" match ke "nasi goreng seafood" yang kalorinya jauh berbeda.
    """
    searchable = _all_searchable_names()
    if not searchable:
        return None

    names  = [s[0] for s in searchable]
    foods  = [s[1] for s in searchable]

    candidates = process.extract(
        query.lower().strip(),
        names,
        scorer=_combined_ratio,
        score_cutoff=settings.FUZZY_THRESHOLD,
        limit=5
    )

    if not candidates:
        return None

    best_score = candidates[0][1]
    # Kandidat yang skornya nyaris seri dengan yang terbaik
    contenders = [c for c in candidates if best_score - c[1] <= 5]

    chosen = contenders[0]
    if expected_kcal and expected_kcal > 0 and len(contenders) > 1:
        def kcal_deviation(cand):
            kcal = foods[cand[2]].get("kcal")
            if kcal is None:
                return float("inf")
            return abs(kcal - expected_kcal)
        chosen = min(contenders, key=kcal_deviation)
        if chosen != contenders[0]:
            print(f"\n   [re-rank] fuzzy: '{contenders[0][0]}' -> '{chosen[0]}' (lebih dekat ke ~{expected_kcal} kcal/100g)", end=" ")

    matched_name, score, idx = chosen
    return {
        **foods[idx],
        "match_method": "fuzzy",
        "match_score": round(score / 100, 3)
    }


# ─── Step 3: USDA API fallback ────────────────────────────────────────────────

# Skor relevansi minimal (0-100) antara query dan deskripsi hasil USDA.
# Di bawah ini hasil dianggap tidak nyambung — lebih baik lempar ke LLM
# daripada pakai nutrisi makanan yang salah (uji: threshold 60 masih
# meloloskan 'steamed white rice' -> 'corn, white, steamed (navajo)').
USDA_MIN_RELEVANCE = 70.0


def _extract_usda_nutrients(food: dict) -> dict | None:
    """Ambil nutrisi per 100g dari satu hasil USDA.

    PENTING: entri "Energy" bisa muncul dua kali (kcal DAN kJ) dengan
    nutrientName sama persis. Tanpa cek unitName, nilai kJ bisa menimpa kcal
    sehingga kalori menggelembung ~4.2x. Hanya terima Energy berunit KCAL.

    Data Foundation sering tidak punya "Energy" polos, hanya
    "Energy (Atwater General Factors)" — dipakai sebagai fallback.
    """
    kcal, kcal_atwater, protein, carbs, fat = None, None, 0.0, 0.0, 0.0
    for n in food.get("foodNutrients", []):
        name  = n.get("nutrientName")
        unit  = (n.get("unitName") or "").upper()
        value = n.get("value")
        if value is None:
            continue
        if name == "Energy" and unit == "KCAL":
            kcal = value
        elif name == "Energy (Atwater General Factors)" and unit == "KCAL":
            kcal_atwater = value
        elif name == "Protein":
            protein = value
        elif name == "Carbohydrate, by difference":
            carbs = value
        elif name == "Total lipid (fat)":
            fat = value

    if kcal is None:
        kcal = kcal_atwater
    if kcal is None:
        return None
    return {"kcal": kcal, "protein_g": protein, "carbs_g": carbs, "fat_g": fat}


def usda_search(english_name: str) -> dict | None:
    """Search ke USDA API menggunakan nama bahasa Inggris.

    Ambil 5 kandidat, pilih yang deskripsinya paling relevan dengan query
    (bukan asal hasil pertama), dan tolak jika relevansi terlalu rendah.
    """
    if not settings.USDA_API_KEY:
        return None
    try:
        res = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "api_key":  settings.USDA_API_KEY,
                "query":    english_name,
                "pageSize": 5,
                "dataType": "SR Legacy,Foundation"
            },
            timeout=2.5
        ).json()

        query = english_name.lower().strip()
        best_food, best_score = None, 0.0
        for food in res.get("foods", []):
            desc  = (food.get("description") or "").lower()
            score = _combined_ratio(query, desc)
            if score > best_score:
                best_food, best_score = food, score

        if best_food is None or best_score < USDA_MIN_RELEVANCE:
            if best_food is not None:
                print(f"\n   [usda] hasil terbaik '{best_food.get('description')}' "
                      f"relevansi {best_score:.0f} < {USDA_MIN_RELEVANCE:.0f} -> ditolak", end=" ")
            return None

        nutrients = _extract_usda_nutrients(best_food)
        if nutrients is None:
            return None

        return {
            "name":     best_food["description"].lower(),
            **nutrients,
            "default_portion_g": 100.0,
            "source":   "usda_api",
            "match_method": "api",
            # Cap 0.85 supaya hasil USDA selalu melewati cek deviasi
            # expected_kcal di validator (weak match < 0.9).
            "match_score": round(min(best_score / 100, 0.85), 3)
        }
    except Exception as e:
        # ASCII saja — print emoji bisa UnicodeEncodeError di konsol Windows
        # (cp1252), yang membuat exception bocor keluar dari handler ini.
        print(f"[!] USDA API error: {e}")
        return None


# ─── Main: find_food ──────────────────────────────────────────────────────────
def find_food(name: str, english_name: str | None = None, expected_kcal: float | None = None) -> tuple[dict, dict]:
    """
    Urutan pencarian:
    1. Exact match di DB lokal
    2. Fuzzy match di DB lokal (re-rank pakai expected_kcal jika tersedia)
    3. USDA API (pakai nama Inggris jika tersedia)
    4. Tidak ditemukan

    Returns: (food_result, match_log)
    """
    # Pastikan cache sudah loaded (lazy load)
    load_food_cache()

    match_log = {
        "search_name": name,
        "search_name_en": english_name,
        "steps_tried": [],
        "match_found": False
    }

    print(f"\n🔎 Searching for: '{name}'" + (f" (EN: {english_name})" if english_name else ""))

    # Step 1: Exact match
    print(f"   Step 1/3: Exact match...", end=" ")
    match_log["steps_tried"].append("exact_match")
    result = exact_match(name)
    if result:
        print(f"✅ FOUND (exact match)")
        match_log["match_found"] = True
        match_log["matched_step"] = "exact_match"
        return result, match_log
    print("❌ Not found")

    # Step 2: Fuzzy match
    print(f"   Step 2/3: Fuzzy match...", end=" ")
    match_log["steps_tried"].append("fuzzy_match")
    result = fuzzy_match(name, expected_kcal)
    if result:
        print(f"✅ FOUND (fuzzy: {result.get('match_score', 0):.1%})")
        match_log["match_found"] = True
        match_log["matched_step"] = "fuzzy_match"
        match_log["fuzzy_score"] = result.get("match_score")
        return result, match_log
    print("❌ Not found")

    # Step 3: USDA API
    match_log["steps_tried"].append("usda_api")
    search_term = english_name or name
    print(f"   Step 3/3: USDA API search for '{search_term}'...", end=" ")
    result = usda_search(search_term)
    if result:
        print(f"✅ FOUND (USDA API)")
        match_log["match_found"] = True
        match_log["matched_step"] = "usda_api"
        match_log["usda_query"] = search_term
        return result, match_log
    print("❌ Not found")

    # Step 4: Not found
    print(f"   ❌ NOT FOUND - Will use LLM estimation")
    match_log["steps_tried"].append("not_found")
    match_log["matched_step"] = "not_found"
    return {
        "name": name,
        "kcal": None,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "default_portion_g": 100.0,
        "source": "unknown",
        "match_method": "not_found",
        "match_score": 0.0
    }, match_log
