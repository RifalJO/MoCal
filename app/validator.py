# app/validator.py
# Validasi nilai nutrisi hasil matching (exact/fuzzy/USDA) sebelum dipakai.
#
# Strategi hemat token:
#   1. Rule-based check dulu (0 token): hard bound + range kalori per kategori
#      + deviasi terhadap expected_kcal dari parser (LLM call #1).
#   2. Hanya item yang terdeteksi anomali dikirim ke LLM — dalam SATU call batch.
#      Call batch ini juga menangani item not_found (menggantikan
#      estimate_nutrition_llm per-item).

import json
import re
from groq import Groq
from app.database import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# ─── Batas absolut kcal per 100g ──────────────────────────────────────────────
# Makanan terpadat kalori = lemak murni ≈ 900 kcal/100g. Di luar ini pasti salah.
HARD_MIN_KCAL = 0.0
HARD_MAX_KCAL = 900.0

# ─── Range kalori wajar per kategori (kcal per 100g, siap saji) ───────────────
# Urutan penting: keyword lebih spesifik ditaruh lebih atas (first match wins).
# Range sengaja dibuat lebar agar false positive (yang memicu LLM call) minim.
CATEGORY_RULES: list[tuple[str, tuple[str, ...], float, float]] = [
    ("minyak_lemak",   ("minyak", "margarin", "mentega", "butter", "santan kental"), 300, 900),
    ("susu_kental",    ("susu kental", "kental manis", "krimer"),                    250, 400),
    ("gula_sirup",     ("gula", "sirup", "madu", "selai"),                           200, 450),
    ("kerupuk",        ("kerupuk", "keripik", "kripik", "emping", "rempeyek"),       300, 600),
    ("bubur",          ("bubur",),                                                    30, 150),
    ("nasi",           ("nasi", "lontong", "ketupat", "ketan"),                       90, 300),
    ("mie_pasta",      ("mie", "mi ", "bihun", "kwetiau", "pasta", "spageti", "spaghetti", "makaroni"), 80, 350),
    ("minuman",        ("teh", "kopi", "jus", "es ", "soda", "susu", "boba", "smoothie", "air kelapa", "sirop"), 0, 160),
    ("air_tawar",      ("air putih", "air mineral", "air"),                            0,  10),
    ("gorengan",       ("goreng", "bakwan", "risol", "cireng", "mendoan", "molen", "pastel"), 120, 500),
    ("roti_kue",       ("roti", "kue", "cake", "donat", "martabak", "bolu", "biskuit", "cookie", "wafer"), 150, 550),
    ("buah",           ("pisang", "apel", "jeruk", "mangga", "pepaya", "semangka", "melon", "buah", "anggur", "salak", "alpukat", "durian"), 15, 200),
    ("sayur",          ("sayur", "tumis", "capcay", "pecel", "lalapan", "urap", "gado-gado", "salad", "cah "), 15, 250),
    ("sup_berkuah",    ("soto", "sop", "sup", "rawon", "bakso", "seblak", "tekwan", "sekoteng", "gulai", "opor", "kari", "semur"), 30, 250),
    ("tahu_tempe",     ("tahu", "tempe"),                                              60, 400),
    ("protein_hewani", ("ayam", "daging", "sapi", "ikan", "udang", "cumi", "telur", "bebek", "kambing", "rendang", "sate", "kerang", "kepiting", "ceker", "kikil", "babat", "paru", "usus"), 80, 450),
]


def get_category(name: str) -> tuple[str, float, float] | None:
    """Cari kategori makanan berdasar keyword. Return (label, min, max) atau None.

    Keyword dicocokkan per kata utuh (word boundary), BUKAN substring —
    substring membuat "gula" match di dalam "gulai nangka" sehingga sayur
    90 kcal dianggap sirup 200-450 kcal dan memicu LLM call sia-sia.
    """
    n = name.lower().strip()
    for label, keywords, lo, hi in CATEGORY_RULES:
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw.strip())}\b", n):
                return label, lo, hi
    return None


def is_plausible_kcal(kcal) -> bool:
    """Cek apakah nilai kcal/100g berada dalam batas fisik yang mungkin."""
    try:
        return kcal is not None and HARD_MIN_KCAL <= float(kcal) <= HARD_MAX_KCAL
    except (TypeError, ValueError):
        return False


def rule_check(
    name: str,
    kcal_100g: float | None,
    expected_kcal: float | None = None,
    match_method: str = "exact",
    match_score: float = 1.0,
) -> tuple[bool, list[str]]:
    """
    Sanity check TANPA LLM. Return (suspicious, reasons).

    Sinyal yang dipakai:
    - Hard bound: kcal di luar 0-900 → pasti salah, method apapun.
    - Category range: kcal di luar range wajar kategori → mencurigakan.
    - Deviasi expected_kcal: hanya untuk match lemah (fuzzy score < 0.9 / USDA),
      karena exact match di DB lokal terkurasi lebih layak dipercaya daripada
      tebakan kalori LLM parser.
    """
    if kcal_100g is None:
        return True, ["kcal_missing"]

    if not is_plausible_kcal(kcal_100g):
        return True, [f"hard_bound:{kcal_100g}"]

    reasons = []

    cat = get_category(name)
    if cat:
        label, lo, hi = cat
        if not (lo <= kcal_100g <= hi):
            reasons.append(f"category_{label}:expected_{lo}-{hi}_got_{round(kcal_100g, 1)}")

    weak_match = match_method in ("fuzzy", "api") and (match_score or 0) < 0.9
    if weak_match and expected_kcal and expected_kcal > 0:
        deviation = abs(kcal_100g - expected_kcal) / expected_kcal
        if deviation > 0.6 and abs(kcal_100g - expected_kcal) > 80:
            reasons.append(f"expected_dev:llm_{round(expected_kcal)}_vs_db_{round(kcal_100g, 1)}")

    return (len(reasons) > 0), reasons


# ─── Validasi batch via LLM (conditional, 1 call untuk semua suspect) ─────────
#
# Desain penting: LLM TIDAK diberi nilai DB. Model kecil (8B) cenderung
# meng-echo/menyetujui angka yang disodorkan padanya. Jadi LLM diminta
# mengestimasi nutrisi secara independen, lalu perbandingan estimasi vs DB
# dilakukan deterministik di kode: selisih dalam toleransi → DB dipakai,
# di luar toleransi → estimasi LLM dipakai sebagai koreksi.

NUTRITION_SYSTEM_PROMPT = """Kamu ahli gizi makanan Indonesia. Berikan estimasi nutrisi PER 100 GRAM (kondisi siap makan, BUKAN per porsi) untuk setiap makanan dalam daftar.

Kalibrasi — nilai kcal per 100g yang benar untuk makanan umum:
nasi putih 130, nasi goreng 168, bubur ayam 75, mie goreng 170, mie ayam 150, ayam goreng 245, rendang sapi 195, telur ceplok 190, tempe goreng 225, tahu goreng 115, bakso kuah 80, soto ayam 65, sayur asem 30, teh manis 35, es jeruk 45, kopi susu 55, pisang goreng 250, martabak manis 320, kerupuk 480, keripik kentang 540.

Balas HANYA JSON array tanpa teks lain, satu objek per makanan, "i" sesuai index input:
[{"i": 0, "kcal": <angka>, "protein_g": <angka>, "carbs_g": <angka>, "fat_g": <angka>}]"""

# Toleransi kesepakatan LLM vs DB: relatif 35%, dengan floor absolut 30 kcal
# supaya makanan rendah kalori (teh manis 35 vs 37) tidak dianggap konflik.
AGREEMENT_REL_TOLERANCE = 0.35
AGREEMENT_ABS_FLOOR = 30.0

# Cache in-process: estimasi nutrisi per nama makanan, agar request berulang
# untuk makanan yang sama tidak memanggil LLM lagi (berguna di warm instance).
_estimate_cache: dict[str, dict] = {}


def _strip_code_fences(raw: str) -> str:
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    return re.sub(r"```", "", raw).strip()


def _fetch_estimates_llm(names: list[str]) -> dict[int, dict]:
    """SATU LLM call: estimasi nutrisi/100g untuk banyak makanan sekaligus.
    Returns {posisi_input: {"kcal", "protein_g", "carbs_g", "fat_g"}}."""
    payload = [{"i": pos, "name": name} for pos, name in enumerate(names)]

    print(f"\n   🤖 Batch validation LLM call: {len(names)} item ({names})")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": NUTRITION_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0,
        max_tokens=min(100 + 60 * len(names), 1500),
    )
    raw = _strip_code_fences(response.choices[0].message.content.strip())

    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array in validation response")
    parsed = json.loads(raw[start:end + 1])
    if not isinstance(parsed, list):
        raise ValueError("Validation response is not a list")

    estimates: dict[int, dict] = {}
    for pos, entry in enumerate(parsed):
        if not isinstance(entry, dict):
            continue
        # Pakai field "i" dari LLM, fallback ke posisi urutan
        epos = entry.get("i", pos)
        if not isinstance(epos, int) or not (0 <= epos < len(names)):
            epos = pos
        if epos >= len(names):
            continue
        if not is_plausible_kcal(entry.get("kcal")):
            continue
        estimates[epos] = {
            "kcal": float(entry["kcal"]),
            "protein_g": float(entry.get("protein_g") or 0),
            "carbs_g": float(entry.get("carbs_g") or 0),
            "fat_g": float(entry.get("fat_g") or 0),
        }
    return estimates


def validate_batch_llm(items: list[dict]) -> dict[int, dict] | None:
    """
    Validasi semua item mencurigakan dalam SATU LLM call.

    items: [{"name": str, "kcal_db": float | None}, ...]
    Returns: {index: {"verdict": "ok"}                        → nilai DB dipakai
                     | {"verdict": "fix", "kcal": ..., ...}}  → estimasi LLM dipakai
             atau None jika LLM gagal total dan tidak ada cache.
    """
    if not items:
        return {}

    # Kumpulkan nama yang belum ada di cache estimasi
    names_to_ask: list[str] = []
    for item in items:
        key = item["name"].lower().strip()
        if key not in _estimate_cache and key not in names_to_ask:
            names_to_ask.append(key)

    if names_to_ask:
        try:
            fetched = _fetch_estimates_llm(names_to_ask)
            for pos, est in fetched.items():
                _estimate_cache[names_to_ask[pos]] = est
        except Exception as e:
            print(f"   ⚠️ Batch validation LLM error: {e}")
    else:
        print(f"   💾 Validation: semua {len(items)} item dari cache (0 LLM call)")

    # Bandingkan estimasi LLM vs nilai DB — deterministik, tanpa LLM
    results: dict[int, dict] = {}
    for idx, item in enumerate(items):
        est = _estimate_cache.get(item["name"].lower().strip())
        if est is None:
            continue  # LLM gagal untuk item ini → caller tandai "unavailable"

        kcal_db = item.get("kcal_db")
        if is_plausible_kcal(kcal_db):
            tolerance = max(est["kcal"] * AGREEMENT_REL_TOLERANCE, AGREEMENT_ABS_FLOOR)
            if abs(float(kcal_db) - est["kcal"]) <= tolerance:
                results[idx] = {"verdict": "ok"}
                continue

        results[idx] = {"verdict": "fix", **est}

    return results if results else None
