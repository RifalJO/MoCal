"""
app/parser.py — MoCal Food Parser (Versi Diperkuat)

Perubahan utama:
- System prompt jauh lebih kuat dan eksplisit soal apa yang dianggap makanan
- Tambah contoh kalimat ambigu (udang, ceker, kerang, dll)
- Tambah fallback normalisasi nama makanan
- Tambah validasi hasil JSON sebelum dikembalikan
- Tambah alias Indonesia → nama standar
"""

import json
import re
from groq import Groq
from app.database import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# ─────────────────────────────────────────────
# SYSTEM PROMPT — versi diperkuat
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah parser makanan yang sangat pintar dan memahami bahasa Indonesia sehari-hari.

TUGASMU: Ekstrak SEMUA item makanan dan minuman dari teks input, lalu kembalikan sebagai JSON array.

═══════════════════════════════════════════════
ATURAN PENTING — BACA SEMUA SEBELUM MEMPROSES
═══════════════════════════════════════════════

1. SEMUA bahan makanan adalah makanan, termasuk:
   - Bahan mentah: udang, cumi, kepiting, ceker, babat, jeroan, ikan, daging, sayuran, buah
   - Olahan: gorengan, tumisan, bakar, rebus, kukus
   - Minuman: teh, kopi, jus, susu, air kelapa
   - Snack: keripik, biskuit, kue, roti
   - Makanan lengkap: nasi goreng, mie ayam, soto, dll

2. JANGAN PERNAH melewatkan bahan makanan meskipun:
   - Disebutkan sebagai topping: "mie dengan udang" → udang HARUS masuk
   - Disebutkan sebagai pelengkap: "soto plus ceker" → ceker HARUS masuk
   - Namanya tidak umum: ceker, kikil, babat, paru, usus → TETAP makanan
   - Disebutkan dalam jumlah kecil: "sedikit kecap", "seujung sendok garam" → masukkan saja
   - Nama tidak lengkap: "udang" tanpa kata "goreng/rebus/dll" → tetap parse sebagai makanan

3. PORSI — konversi semua satuan ke gram (default_portion_g jika tidak ada info):
   - 1 porsi, 1 piring, 1 mangkok     → 200–300g (tergantung jenis makanan)
   - 1 ekor ikan                       → 100–150g
   - 1 ekor udang besar / udang galah  → 50–80g
   - 5 ekor udang sedang               → 75g
   - 1 potong daging                   → 80–100g
   - 1 butir telur                     → 55g
   - 1 gelas minuman                   → 200–250ml
   - 1 sendok makan                    → 15g
   - 1 sendok teh                      → 5g
   - secukupnya / sedikit              → 10g

4. NAMA — normalisasi ke nama standar Indonesia:
   - "udang" / "shrimp" / "udang segar"    → "udang"
   - "ceker" / "ceker ayam" / "cakar"      → "ceker ayam"
   - "cumi" / "cumi-cumi" / "sotong"       → "cumi-cumi"
   - "kerang" / "kerang hijau" / "remis"   → "kerang"
   - "kikil" / "kili-kili"                 → "kikil sapi"
   - "babat" / "babat sapi"                → "babat sapi"
   - "paru" / "paru sapi"                  → "paru sapi"
   - "usus" / "usus ayam"                  → "usus ayam"
   - "darah" / "saren" / "marus"           → "darah ayam"

═══════════════════════════════════════════════
FORMAT OUTPUT — WAJIB JSON SAJA, TIDAK ADA TEKS LAIN
═══════════════════════════════════════════════

[
  {
    "name": "nama makanan dalam bahasa Indonesia (standar)",
    "name_en": "nama dalam bahasa Inggris untuk USDA lookup",
    "qty": 1.0,
    "unit": "porsi",
    "estimated_grams": 200
  }
]

Jika input tidak mengandung makanan sama sekali (misalnya: "halo", "terima kasih"), kembalikan: []

═══════════════════════════════════════════════
CONTOH — PELAJARI DENGAN SEKSAMA
═══════════════════════════════════════════════

Input: "makan siang nasi uduk sama udang goreng 5 ekor"
Output:
[
  {"name": "nasi uduk", "name_en": "steamed coconut rice", "qty": 1, "unit": "porsi", "estimated_grams": 250},
  {"name": "udang goreng", "name_en": "fried shrimp", "qty": 5, "unit": "ekor", "estimated_grams": 75}
]

Input: "soto ayam pakai ceker sama nasi putih"
Output:
[
  {"name": "soto ayam", "name_en": "chicken soup", "qty": 1, "unit": "mangkok", "estimated_grams": 350},
  {"name": "ceker ayam", "name_en": "chicken feet", "qty": 1, "unit": "porsi", "estimated_grams": 60},
  {"name": "nasi putih", "name_en": "steamed white rice", "qty": 1, "unit": "porsi", "estimated_grams": 200}
]

Input: "mie ayam bakso plus pangsit goreng, teh manis hangat"
Output:
[
  {"name": "mie ayam", "name_en": "chicken noodle", "qty": 1, "unit": "porsi", "estimated_grams": 300},
  {"name": "bakso", "name_en": "meatball", "qty": 3, "unit": "butir", "estimated_grams": 60},
  {"name": "pangsit goreng", "name_en": "fried wonton", "qty": 1, "unit": "porsi", "estimated_grams": 50},
  {"name": "teh manis hangat", "name_en": "sweet hot tea", "qty": 1, "unit": "gelas", "estimated_grams": 250}
]

Input: "udang"
Output:
[
  {"name": "udang", "name_en": "shrimp", "qty": 1, "unit": "porsi", "estimated_grams": 100}
]

Input: "sarapan roti bakar 2 lembar, telur ceplok, dan segelas susu"
Output:
[
  {"name": "roti bakar", "name_en": "toast", "qty": 2, "unit": "lembar", "estimated_grams": 60},
  {"name": "telur ceplok", "name_en": "fried egg sunny side up", "qty": 1, "unit": "butir", "estimated_grams": 55},
  {"name": "susu", "name_en": "milk", "qty": 1, "unit": "gelas", "estimated_grams": 250}
]

Input: "rawon kikil komplit sama nasi"
Output:
[
  {"name": "rawon", "name_en": "black beef soup", "qty": 1, "unit": "mangkok", "estimated_grams": 400},
  {"name": "kikil sapi", "name_en": "beef tendon", "qty": 1, "unit": "porsi", "estimated_grams": 80},
  {"name": "nasi putih", "name_en": "steamed white rice", "qty": 1, "unit": "porsi", "estimated_grams": 200}
]

Input: "semur jengkol 1 porsi"
Output:
[
  {"name": "semur jengkol", "name_en": "braised jengkol beans", "qty": 1, "unit": "porsi", "estimated_grams": 150}
]
"""

# ─────────────────────────────────────────────
# ALIAS NORMALISASI — fallback jika LLM tidak normalize
# ─────────────────────────────────────────────

FOOD_ALIASES = {
    # Seafood
    "shrimp":       "udang",
    "prawn":        "udang",
    "udang segar":  "udang",
    "sotong":       "cumi-cumi",
    "squid":        "cumi-cumi",
    "cumi":         "cumi-cumi",
    "remis":        "kerang",
    "kerang hijau": "kerang hijau",

    # Jeroan & olahan daging
    "cakar":        "ceker ayam",
    "cakar ayam":   "ceker ayam",
    "kili-kili":    "kikil sapi",
    "kikil":        "kikil sapi",
    "babat":        "babat sapi",
    "paru":         "paru sapi",
    "usus":         "usus ayam",
    "saren":        "darah ayam",
    "marus":        "darah ayam",

    # Minuman
    "es teh":       "teh manis dingin",
    "teh tarik":    "teh susu",
    "kopi susu":    "kopi susu",
    "es kopi":      "kopi dingin",

    # Nasi & karbohidrat
    "nasi":         "nasi putih",
    "rice":         "nasi putih",
    "mie":          "mie",
    "mi":           "mie",
}


def normalize_food_name(name: str) -> str:
    """Normalisasi nama makanan menggunakan alias dict."""
    lower = name.lower().strip()
    return FOOD_ALIASES.get(lower, name)


# ─────────────────────────────────────────────
# UNIT CONVERTER — qty + unit → grams
# ─────────────────────────────────────────────

UNIT_TO_GRAMS = {
    "gram": 1,
    "g": 1,
    "kg": 1000,
    "ml": 1,
    "liter": 1000,
    "l": 1000,
    "sendok makan": 15,
    "sdm": 15,
    "sendok teh": 5,
    "sdt": 5,
    "gelas": 250,
    "cup": 240,
    "mangkok": 300,
    "piring": 250,
    "porsi": None,   # gunakan estimated_grams dari LLM
    "ekor": None,    # gunakan estimated_grams dari LLM
    "butir": None,
    "lembar": None,
    "potong": None,
    "biji": None,
    "buah": None,
}


def convert_to_gram(qty: float, unit: str, estimated_grams: float) -> float:
    """
    Konversi qty + unit → total gram.
    Jika unit tidak diketahui atau None, gunakan estimated_grams dari LLM.
    """
    unit_lower = unit.lower().strip()
    multiplier = UNIT_TO_GRAMS.get(unit_lower)
    if multiplier is not None:
        return qty * multiplier
    # Fallback ke estimated_grams
    return estimated_grams if estimated_grams else 100.0


# ─────────────────────────────────────────────
# PARSER UTAMA
# ─────────────────────────────────────────────

def parse_food_text(text: str) -> list[dict]:
    """
    Parse input teks bebas → list item makanan.

    Returns:
        [
            {
                "name": str,
                "name_en": str,
                "qty": float,
                "unit": str,
                "grams": float,
            },
            ...
        ]
    """
    if not text or not text.strip():
        return []

    # ── Panggil LLM ──
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": text.strip()},
            ],
            temperature=0.1,   # rendah = lebih konsisten
            max_tokens=1000,
        )
    except Exception as e:
        print(f"[parser] LLM error: {e}")
        return []

    raw = response.choices[0].message.content.strip()

    # ── Bersihkan output ──
    # Hapus markdown code block jika ada
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = re.sub(r"```", "", raw).strip()

    # ── Parse JSON ──
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        # Coba ekstrak array dari teks
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                items = json.loads(match.group())
            except json.JSONDecodeError:
                print(f"[parser] JSON parse failed. Raw: {raw[:200]}")
                return []
        else:
            print(f"[parser] No JSON array found. Raw: {raw[:200]}")
            return []

    if not isinstance(items, list):
        return []

    # ── Validasi & normalize setiap item ──
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue

        name = item.get("name", "").strip()
        if not name:
            continue

        # Normalisasi nama via alias dict
        name = normalize_food_name(name)

        name_en        = item.get("name_en", name)
        qty            = float(item.get("qty", 1))
        unit           = item.get("unit", "porsi")
        estimated_grams= float(item.get("estimated_grams", 100))

        grams = convert_to_gram(qty, unit, estimated_grams)

        result.append({
            "name":       name,
            "name_en":    name_en,
            "qty":        qty,
            "unit":       unit,
            "grams":      round(grams, 1),
        })

    return result


def estimate_nutrition_llm(food_name: str) -> dict:
    """
    Gunakan LLM untuk menebak nutrisi per 100g jika tidak ada di DB.
    """
    prompt = f"""Kamu adalah ahli gizi. Berikan estimasi nutrisi PER 100 GRAM untuk makanan: '{food_name}'.
    
    Kembalikan HANYA JSON dengan format:
    {{
        "kcal": float,
        "protein_g": float,
        "carbs_g": float,
        "fat_g": float,
        "default_portion_g": 100
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        raw = re.sub(r"```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        print(f"[parser] Nutrition estimate error: {e}")
        return {
            "kcal": 150,
            "protein_g": 5,
            "carbs_g": 20,
            "fat_g": 5,
            "default_portion_g": 100
        }


# ─────────────────────────────────────────────
# TEST — jalankan: python -m app.parser
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        "udang",
        "makan siang nasi uduk sama udang goreng 5 ekor",
        "soto ayam pakai ceker sama nasi putih",
        "rawon kikil komplit",
        "mie ayam bakso pangsit goreng teh manis",
        "semur jengkol",
        "cumi-cumi bakar 1 porsi",
        "sarapan roti bakar 2 lembar telur ceplok susu",
        "es teh sama kerupuk",
        "halo apa kabar",   # bukan makanan → []
    ]

    for tc in test_cases:
        print(f"\nInput : {tc}")
        result = parse_food_input(tc)
        print(f"Output: {json.dumps(result, ensure_ascii=False, indent=2)}")