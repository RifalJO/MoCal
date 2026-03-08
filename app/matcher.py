# app/matcher.py
# Fuzzy matching engine — cocokkan nama makanan ke database lokal

from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session
from app.database import Food, settings
import requests


# ─── Cache nama makanan (load sekali saat startup) ────────────────────────────
_food_cache: list[dict] = []

def load_food_cache(db: Session):
    """Load semua nama makanan ke memory untuk fuzzy matching yang cepat"""
    global _food_cache
    foods = db.query(Food).all()
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
    print(f"✅ Cache loaded: {len(_food_cache)} makanan")


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
def find_food(name: str, english_name: str | None = None) -> dict:
    """
    Urutan pencarian:
    1. Exact match di DB lokal
    2. Fuzzy match di DB lokal
    3. USDA API (pakai nama Inggris jika tersedia)
    4. Tidak ditemukan
    """

    # Step 1
    result = exact_match(name)
    if result:
        return result

    # Step 2
    result = fuzzy_match(name)
    if result:
        return result

    # Step 3 — pakai nama Inggris kalau ada, fallback ke nama asli
    search_term = english_name or name
    result = usda_search(search_term)
    if result:
        return result

    # Step 4
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
    }
