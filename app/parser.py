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
from app.database import settings, groq_extra_kwargs

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

5. SINGKATAN GAUL & TYPO — WAJIB diperbaiki ke nama standar, JANGAN disalin mentah:
   - "naspad"                  → "nasi padang"
   - "nasgor"                  → "nasi goreng"
   - "rendg" / "rendang" typo  → "rendang"
   - "krupuk"                  → "kerupuk"
   - "sambel ijo" / "sambel"   → "sambal ijo" / "sambal"
   - "miayam"                  → "mie ayam"
   - "esteh" / "es teh anget"  → "es teh" / "teh manis hangat"
   - "gado2"                   → "gado-gado"
   - Kata pengantar seperti "lauk", "sayurnya", "pakai" BUKAN bagian nama makanan
   - "sayurnya nasi padang" maksudnya sayur khas nasi padang → "gulai nangka"
   ⚠️ "name" TIDAK BOLEH berisi singkatan/typo. "name_en" HARUS bahasa Inggris
   sungguhan (terjemahan), BUKAN salinan kata Indonesia.

═══════════════════════════════════════════════
FORMAT OUTPUT — SANGAT PENTING!
═══════════════════════════════════════════════

⚠️ KEMBALIKAN HANYA JSON ARRAY — TANPA TEKS LAIN!
⚠️ JANGAN tulis penjelasan, pendahuluan, atau catatan apapun!
⚠️ JANGAN gunakan format seperti "Berikut adalah JSON..." atau "Output:"!

LANGSUNG MULAI DENGAN [ DAN AKHIRI DENGAN ]

Format:
[
  {
    "name": "nama makanan dalam bahasa Indonesia (standar)",
    "name_en": "nama dalam bahasa Inggris untuk USDA lookup",
    "qty": 1.0,
    "unit": "porsi",
    "estimated_grams": 200,
    "kcal_100g": 130
  }
]

"kcal_100g" = estimasi kalori PER 100 GRAM makanan itu dalam kondisi siap makan (bukan total porsi). Contoh: nasi putih 130, ayam goreng 260, teh manis 35, gorengan 300.

Jika input tidak mengandung makanan sama sekali (misalnya: "halo", "terima kasih"), kembalikan: []

═══════════════════════════════════════════════
CONTOH — PELAJARI DENGAN SEKSAMA
═══════════════════════════════════════════════

Contoh dipilih agar mencakup pola tersulit: topping/jeroan, multi-item +
minuman, slang/typo, dan item tunggal telanjang. Terapkan pola yang sama ke
input lain.

Input: "soto ayam pakai ceker sama nasi putih"
Output:
[
  {"name": "soto ayam", "name_en": "chicken soup", "qty": 1, "unit": "mangkok", "estimated_grams": 350, "kcal_100g": 65},
  {"name": "ceker ayam", "name_en": "chicken feet", "qty": 1, "unit": "porsi", "estimated_grams": 60, "kcal_100g": 200},
  {"name": "nasi putih", "name_en": "steamed white rice", "qty": 1, "unit": "porsi", "estimated_grams": 200, "kcal_100g": 130}
]

Input: "mie ayam bakso plus pangsit goreng, teh manis hangat"
Output:
[
  {"name": "mie ayam", "name_en": "chicken noodle", "qty": 1, "unit": "porsi", "estimated_grams": 300, "kcal_100g": 150},
  {"name": "bakso", "name_en": "meatball", "qty": 3, "unit": "butir", "estimated_grams": 60, "kcal_100g": 200},
  {"name": "pangsit goreng", "name_en": "fried wonton", "qty": 1, "unit": "porsi", "estimated_grams": 50, "kcal_100g": 350},
  {"name": "teh manis hangat", "name_en": "sweet hot tea", "qty": 1, "unit": "gelas", "estimated_grams": 250, "kcal_100g": 35}
]

Input: "Makan naspad dengan lauk rendg, krupuk, sayurnya nasi padang itu loh, sambel ijo"
Output:
[
  {"name": "nasi padang", "name_en": "padang style rice", "qty": 1, "unit": "porsi", "estimated_grams": 250, "kcal_100g": 165},
  {"name": "rendang", "name_en": "beef rendang", "qty": 1, "unit": "potong", "estimated_grams": 100, "kcal_100g": 195},
  {"name": "kerupuk", "name_en": "crackers", "qty": 1, "unit": "porsi", "estimated_grams": 20, "kcal_100g": 480},
  {"name": "gulai nangka", "name_en": "young jackfruit curry", "qty": 1, "unit": "porsi", "estimated_grams": 100, "kcal_100g": 90},
  {"name": "sambal ijo", "name_en": "green chili sambal", "qty": 1, "unit": "sendok makan", "estimated_grams": 15, "kcal_100g": 130}
]

Input: "udang"
Output:
[
  {"name": "udang", "name_en": "shrimp", "qty": 1, "unit": "porsi", "estimated_grams": 100, "kcal_100g": 100}
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
    "esteh":        "teh manis dingin",
    "teh tarik":    "teh susu",
    "kopi susu":    "kopi susu",
    "es kopi":      "kopi dingin",

    # Nasi & karbohidrat
    "nasi":         "nasi putih",
    "rice":         "nasi putih",
    "mie":          "mie",
    "mi":           "mie",

    # Singkatan gaul & ejaan pasar — jaring pengaman jika LLM parser
    # meneruskan slang mentah tanpa menormalisasi (sering terjadi di model 8B)
    "naspad":       "nasi padang",
    "nasi pada":    "nasi padang",
    "nasipada":     "nasi padang",
    "nasgor":       "nasi goreng",
    "miayam":       "mie ayam",
    "mie yamin":    "mie ayam",
    "gado2":        "gado-gado",
    "magbar":       "martabak",
    "krupuk":       "kerupuk",
    "sambel":       "sambal",
    "sambel ijo":   "sambal ijo",
    "sambal hijau": "sambal ijo",
    "rendg":        "rendang",
    "lauk rendg":   "rendang",
    "sayur nasipada": "gulai nangka",
    "sayur nasi padang": "gulai nangka",
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
# LOCAL FAST-PATH — parse tanpa LLM untuk input sederhana
# ─────────────────────────────────────────────
#
# Banyak input hanya berisi makanan yang SUDAH ada di database lokal
# (mis. "nasi goreng", "nasi putih sama es teh"). Untuk kasus ini LLM parser
# tidak diperlukan: pecah teks, exact-match tiap potongan ke CSV, pakai
# default_portion_g. Jika SATU potongan saja gagal exact-match, seluruh
# fast-path dibatalkan dan pipeline jatuh ke LLM parser (akurasi tetap sama).

# Pemisah antar item: koma/titik-koma/simbol + konjungsi umum bahasa Indonesia.
_SEPARATOR_RE = re.compile(
    r"\s*(?:,|;|\+|&|\bdan\b|\bsama\b|\bplus\b|\bserta\b|\bjuga\b|\bterus\b|\blalu\b)\s*",
    re.IGNORECASE,
)

# Kata pengisi yang boleh dibuang dari awal/akhir potongan tanpa mengubah makna
# makanan. Konservatif — kalau ragu, fast-path gagal dan jatuh ke LLM (aman).
_FILLER_WORDS = {
    "makan", "sarapan", "minum", "makanan", "aku", "saya", "gua", "gue",
    "tadi", "barusan", "pagi", "siang", "sore", "malam", "pesan", "beli",
    "order", "dengan", "pakai", "pake", "lauk", "menu", "mau", "habis",
    "seporsi", "porsi", "ini", "itu",
}

# "se-" + satuan → qty 1 (mis. "segelas" = 1 gelas).
_SE_UNIT = {
    "segelas": "gelas", "secangkir": "cup", "sepiring": "piring",
    "semangkok": "mangkok", "semangkuk": "mangkok", "sebutir": "butir",
    "sepotong": "potong", "selembar": "lembar", "seekor": "ekor",
    "sebuah": "buah", "sebiji": "biji", "sesendok": "sendok makan",
}

# Satuan yang dikenali unit converter (multi-kata dicoba dulu pada regex).
_KNOWN_UNITS = sorted(set(UNIT_TO_GRAMS.keys()) | {"cup"}, key=len, reverse=True)
_QTY_UNIT_RE = re.compile(
    r"(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>"
    + "|".join(re.escape(u) for u in _KNOWN_UNITS)
    + r")?\b",
    re.IGNORECASE,
)


def _extract_qty_unit(chunk: str) -> tuple[str, float, str]:
    """Pisahkan qty + unit dari potongan → (nama_bersih, qty, unit).

    Default (1, 'porsi') jika tidak ada angka/satuan eksplisit.
    """
    qty, unit = 1.0, "porsi"
    text = chunk

    # "se-" + satuan (segelas, sepiring, ...)
    for word, u in _SE_UNIT.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            unit = u
            text = re.sub(rf"\b{word}\b", " ", text, flags=re.IGNORECASE)
            break

    # angka + satuan opsional (mis. "5 ekor", "200 gram", "2")
    m = _QTY_UNIT_RE.search(text)
    if m:
        try:
            qty = float(m.group("qty").replace(",", "."))
        except ValueError:
            qty = 1.0
        if m.group("unit"):
            unit = m.group("unit").lower()
        text = text[:m.start()] + " " + text[m.end():]

    name = " ".join(text.split()).strip(" -")
    return name, qty, unit


def _clean_food_token(name: str) -> str:
    """Buang kata pengisi di awal/akhir potongan (konservatif)."""
    words = [w for w in name.lower().split() if w]
    while words and words[0] in _FILLER_WORDS:
        words.pop(0)
    while words and words[-1] in _FILLER_WORDS:
        words.pop()
    return " ".join(words)


# Satuan per-biji: berat 1 biji sangat bervariasi (1 ekor ikan ≠ 1 ekor udang).
# Fast-path TIDAK menebak — input dengan satuan ini diserahkan ke LLM.
_PIECE_UNITS = {"ekor", "butir", "lembar", "potong", "biji", "buah"}

# Porsi wajar per kategori (gram per 1 porsi) — meniru aturan porsi di
# SYSTEM_PROMPT ("1 porsi/piring 200-300g, 1 mangkok 300-350g, 1 gelas 250ml").
# Label kategori mengikuti CATEGORY_RULES di app/validator.py (DRY).
# Dipakai HANYA saat default_portion_g di DB masih nilai pengisi 100.
_CATEGORY_PORTION_G = {
    "nasi":        250.0,   # nasi goreng/uduk 1 piring
    "mie_pasta":   250.0,
    "bubur":       300.0,   # 1 mangkok
    "sup_berkuah": 350.0,   # 1 mangkok kuah
    "minuman":     250.0,   # 1 gelas
    "air_tawar":   250.0,
    "sayur":       150.0,
    "kerupuk":      20.0,   # pelengkap, bukan 100g kerupuk
    "minyak_lemak": 15.0,   # 1 sdm
    "gula_sirup":   15.0,
}

_FILLER_PORTION = 100.0     # nilai default_portion_g yang berarti "tidak dikurasi"

# Hidangan utuh yang keyword-nya masuk kategori 'sayur' di validator padahal
# porsinya sekelas makanan utama, bukan lauk sayur pendamping.
_PORTION_OVERRIDES = {
    "gado-gado": 250.0,
    "pecel":     250.0,
    "ketoprak":  250.0,
    "capcay":    200.0,
}


def _resolve_portion_g(name: str, default_g: float) -> float:
    """Porsi (gram) untuk 1 porsi makanan `name`.

    default_portion_g yang terkurasi (≠100) dipercaya; nilai pengisi 100
    diganti porsi wajar per kategori supaya total kalori tidak terlalu kecil
    (mis. nasi goreng 100g=276 kcal padahal 1 piring ~250g=690 kcal).
    """
    if abs(default_g - _FILLER_PORTION) > 1e-9:
        return default_g                      # nilai kurasi → pakai apa adanya

    for dish, grams in _PORTION_OVERRIDES.items():
        if dish in name.lower():
            return grams

    from app.validator import get_category    # import lokal, hindari siklus
    cat = get_category(name)
    if cat:
        return _CATEGORY_PORTION_G.get(cat[0], default_g)
    return default_g


def try_local_parse(text: str) -> list[dict] | None:
    """Coba parse SEPENUHNYA di lokal tanpa LLM.

    Return list item (format sama dengan parse_food_text) HANYA jika SETIAP
    potongan berhasil exact-match ke database lokal DAN porsinya bisa
    ditentukan dengan yakin. Jika tidak → return None agar caller memakai
    LLM parser (perilaku lama, akurasi tetap).
    """
    if not text or not text.strip():
        return None

    # Import lokal supaya tak ada siklus import saat modul dimuat.
    from app.matcher import load_food_cache, exact_match
    load_food_cache()

    chunks = [c.strip() for c in _SEPARATOR_RE.split(text) if c and c.strip()]
    if not chunks:
        return None

    items: list[dict] = []
    for chunk in chunks:
        base, qty, unit = _extract_qty_unit(chunk)
        base = _clean_food_token(base)
        if not base or len(base.split()) > 5:
            return None                       # kosong/terlalu panjang → serah ke LLM
        if unit in _PIECE_UNITS:
            return None                       # berat per-biji tak pasti → serah ke LLM

        food = None
        for cand in (base, normalize_food_name(base)):
            food = exact_match(cand)
            if food:
                break
        if not food:
            return None                       # satu gagal → batalkan fast-path

        multiplier = UNIT_TO_GRAMS.get(unit)
        if multiplier:
            grams = qty * multiplier          # satuan eksplisit (gram, gelas, sdm...)
        else:
            default_g = food.get("default_portion_g") or _FILLER_PORTION
            grams = qty * _resolve_portion_g(food["name"], default_g)

        items.append({
            "name":          food["name"],
            "name_en":       None,
            "qty":           qty,
            "unit":          unit,
            "grams":         round(grams, 1),
            "expected_kcal": None,            # exact match dipercaya; tak perlu expected
        })

    return items or None


# ─────────────────────────────────────────────
# CACHE HASIL PARSE — input identik tak di-parse ulang (warm instance)
# ─────────────────────────────────────────────
from collections import OrderedDict

_PARSE_CACHE_MAX = 256
_parse_cache: "OrderedDict[str, list[dict]]" = OrderedDict()


def _parse_cache_key(text: str) -> str:
    return " ".join(text.lower().split())


def get_cached_parse(text: str) -> list[dict] | None:
    """Ambil hasil parse yang sudah di-cache (salinan, agar cache tak termutasi)."""
    key = _parse_cache_key(text)
    items = _parse_cache.get(key)
    if items is None:
        return None
    _parse_cache.move_to_end(key)
    return [dict(it) for it in items]


def set_cached_parse(text: str, items: list[dict]) -> None:
    """Simpan hasil parse (fast-path maupun LLM) untuk input identik berikutnya."""
    if not items:
        return
    key = _parse_cache_key(text)
    _parse_cache[key] = [dict(it) for it in items]
    _parse_cache.move_to_end(key)
    while len(_parse_cache) > _PARSE_CACHE_MAX:
        _parse_cache.popitem(last=False)


# ─────────────────────────────────────────────
# PARSER UTAMA
# ─────────────────────────────────────────────

def parse_food_text(text: str) -> tuple[list[dict], dict]:
    """
    Parse input teks bebas → list item makanan + log detail.

    Returns:
        (
            [
                {
                    "name": str,
                    "name_en": str,
                    "qty": float,
                    "unit": str,
                    "grams": float,
                },
                ...
            ],
            {
                "llm_raw_response": str,
                "parsed_items_count": int,
                "parse_time_ms": float,
                "errors": list[str]
            }
        )
    """
    import time
    start_time = time.time()
    
    log_detail = {
        "llm_raw_response": None,
        "parsed_items_count": 0,
        "parse_time_ms": 0,
        "errors": [],
        "llm_model": settings.GROQ_MODEL,
        "input_length": len(text)
    }
    
    if not text or not text.strip():
        log_detail["errors"].append("Empty input")
        return [], log_detail

    print("\n" + "="*80)
    print("🔍 PARSING STARTED")
    print("="*80)
    print(f"📝 Input text: {text}")
    print(f"⏱️  Start time: {time.strftime('%H:%M:%S')}")

    # ── Panggil LLM ──
    try:
        print(f"\n🤖 Calling LLM ({log_detail['llm_model']})...")
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            **groq_extra_kwargs(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": text.strip()},
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        print("✅ LLM response received")
    except Exception as e:
        error_msg = f"LLM error: {e}"
        print(f"❌ {error_msg}")
        log_detail["errors"].append(error_msg)
        log_detail["parse_time_ms"] = (time.time() - start_time) * 1000
        return [], log_detail

    raw = response.choices[0].message.content.strip()
    log_detail["llm_raw_response"] = raw  # Store full response
    
    print("\n📄 RAW LLM OUTPUT:")
    print("-"*80)
    print(raw)
    print("-"*80)

    # ── Bersihkan output ──
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = re.sub(r"```", "", raw).strip()

    # ── Parse JSON (robust: handles multiple arrays from LLM) ──
    items = None

    # Attempt 1: Direct parse
    try:
        items = json.loads(raw)
        print("✅ JSON parsed successfully (direct)")
    except json.JSONDecodeError:
        pass

    # Attempt 2: Fix back-to-back arrays  ][  →  ,
    if items is None:
        try:
            fixed = re.sub(r'\]\s*\[', ',', raw)
            # Wrap in array if the fix removed outer brackets
            start_idx = fixed.find('[')
            end_idx = fixed.rfind(']')
            if start_idx != -1 and end_idx != -1:
                json_str = fixed[start_idx:end_idx + 1]
                items = json.loads(json_str)
                print("✅ JSON parsed after merging back-to-back arrays")
        except json.JSONDecodeError:
            pass

    # Attempt 3: Extract all [...] blocks via regex and merge
    if items is None:
        try:
            blocks = re.findall(r'\[.*?\]', raw, re.DOTALL)
            if blocks:
                merged = []
                for block in blocks:
                    parsed_block = json.loads(block)
                    if isinstance(parsed_block, list):
                        merged.extend(parsed_block)
                    else:
                        merged.append(parsed_block)
                if merged:
                    items = merged
                    print(f"✅ JSON parsed by merging {len(blocks)} separate arrays")
        except json.JSONDecodeError:
            pass

    # Attempt 4: Extract between first [ and last ]
    if items is None:
        start_idx = raw.find('[')
        end_idx = raw.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = raw[start_idx:end_idx + 1]
            try:
                items = json.loads(json_str)
                print("✅ JSON extracted from text and parsed successfully")
            except json.JSONDecodeError as e:
                error_msg = f"JSON parse failed: {e}"
                print(f"❌ {error_msg}")
                log_detail["errors"].append(error_msg)
                log_detail["parse_time_ms"] = (time.time() - start_time) * 1000
                return [], log_detail
        else:
            error_msg = "No JSON array found"
            print(f"❌ {error_msg}")
            log_detail["errors"].append(error_msg)
            log_detail["parse_time_ms"] = (time.time() - start_time) * 1000
            return [], log_detail

    if not isinstance(items, list):
        error_msg = "Parsed result is not a list"
        print(f"❌ {error_msg}")
        log_detail["errors"].append(error_msg)
        return [], log_detail

    # ── Validasi & normalize setiap item ──
    result = []
    print(f"\n📦 Parsed {len(items)} items from LLM:")
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue

        name = item.get("name", "").strip()
        if not name:
            continue

        name = normalize_food_name(name)
        name_en        = item.get("name_en", name)
        qty            = float(item.get("qty", 1))
        unit           = item.get("unit", "porsi")
        estimated_grams= float(item.get("estimated_grams", 100))

        # Ekspektasi kalori per 100g dari LLM — dipakai untuk validasi & re-rank fuzzy
        try:
            expected_kcal = float(item.get("kcal_100g") or 0) or None
        except (TypeError, ValueError):
            expected_kcal = None

        grams = convert_to_gram(qty, unit, estimated_grams)

        parsed_item = {
            "name":          name,
            "name_en":       name_en,
            "qty":           qty,
            "unit":          unit,
            "grams":         round(grams, 1),
            "expected_kcal": expected_kcal,
        }
        result.append(parsed_item)

        print(f"   {i}. {name} (EN: {name_en}) - {qty} {unit} ≈ {round(grams, 1)}g (~{expected_kcal or '?'} kcal/100g)")

    log_detail["parsed_items_count"] = len(result)
    log_detail["parse_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    print(f"\n✅ PARSING COMPLETED")
    print(f"   Total items: {len(result)}")
    print(f"   Parse time: {log_detail['parse_time_ms']}ms")
    print("="*80 + "\n")
    
    return result, log_detail


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
            model=settings.GROQ_MODEL,
            **groq_extra_kwargs(),
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
        result, log = parse_food_text(tc)
        print(f"Output: {json.dumps(result, ensure_ascii=False, indent=2)}")