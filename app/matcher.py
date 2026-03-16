# app/matcher.py
# Fuzzy matching engine — cocokkan nama makanan ke database lokal

from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import Food, settings, SessionLocal
import requests


# ─── Cache nama makanan (lazy load — hanya saat pertama dibutuhkan) ───────────
_food_cache: list[dict] = []
_cache_loaded: bool = False

def load_food_cache(db: Session | None = None):
    """Load semua nama makanan ke memory untuk fuzzy matching yang cepat.
    Dipanggil otomatis saat pertama kali find_food() dipanggil.
    """
    global _food_cache, _cache_loaded

    if _cache_loaded:
        return

    # Gunakan session yang diberikan atau buat baru
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
                "name":  f.name,
                "aliases": f.name_aliases.split("|") if f.name_aliases else [],
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
        print(f"✅ Cache loaded: {len(_food_cache)} makanan")
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
def fuzzy_match(query: str) -> dict | None:
    searchable = _all_searchable_names()
    if not searchable:
        return None

    names  = [s[0] for s in searchable]
    foods  = [s[1] for s in searchable]

    result = process.extractOne(
        query.lower().strip(),
        names,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=settings.FUZZY_THRESHOLD
    )

    if result:
        matched_name, score, idx = result
        return {
            **foods[idx],
            "match_method": "fuzzy",
            "match_score": round(score / 100, 3)
        }
    return None


# ─── Step 3: USDA API fallback ────────────────────────────────────────────────
def usda_search(english_name: str) -> dict | None:
    """Search ke USDA API menggunakan nama bahasa Inggris"""
    if not settings.USDA_API_KEY:
        return None
    try:
        res = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "api_key":  settings.USDA_API_KEY,
                "query":    english_name,
                "pageSize": 1,
                "dataType": "SR Legacy,Foundation"
            },
            timeout=5
        ).json()

        if not res.get("foods"):
            return None

        food  = res["foods"][0]
        nutr  = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}

        return {
            "name":     food["description"].lower(),
            "kcal":     nutr.get("Energy", None),
            "protein_g": nutr.get("Protein", 0.0),
            "carbs_g":  nutr.get("Carbohydrate, by difference", 0.0),
            "fat_g":    nutr.get("Total lipid (fat)", 0.0),
            "default_portion_g": 100.0,
            "source":   "usda_api",
            "match_method": "api",
            "match_score": 0.7
        }
    except Exception as e:
        print(f"⚠️ USDA API error: {e}")
        return None


# ─── Main: find_food ──────────────────────────────────────────────────────────
def find_food(name: str, english_name: str | None = None) -> tuple[dict, dict]:
    """
    Urutan pencarian:
    1. Exact match di DB lokal
    2. Fuzzy match di DB lokal
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
    result = fuzzy_match(name)
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
