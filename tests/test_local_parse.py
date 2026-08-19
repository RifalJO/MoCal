"""Tes untuk fast-path lokal — TIDAK memanggil LLM/Groq.

Semua tes di sini murni lokal (regex + exact match ke CSV),
sehingga bisa dijalankan berulang tanpa membakar token.
"""

from app.parser import (
    _extract_qty_unit,
    _clean_food_token,
    try_local_parse,
    normalize_food_name,
    convert_to_gram,
)


# ─── _extract_qty_unit ────────────────────────────────────────────────────────
def test_extract_trailing_number_and_unit():
    name, qty, unit = _extract_qty_unit("udang goreng 5 ekor")
    assert name == "udang goreng"
    assert qty == 5.0
    assert unit == "ekor"


def test_extract_se_prefix_unit():
    name, qty, unit = _extract_qty_unit("segelas susu")
    assert name == "susu"
    assert qty == 1.0
    assert unit == "gelas"


def test_extract_defaults_when_no_qty():
    name, qty, unit = _extract_qty_unit("nasi goreng")
    assert name == "nasi goreng"
    assert qty == 1.0
    assert unit == "porsi"


def test_extract_decimal_with_comma():
    name, qty, unit = _extract_qty_unit("gula 1,5 sendok makan")
    assert name == "gula"
    assert qty == 1.5
    assert unit == "sendok makan"


# ─── _clean_food_token ────────────────────────────────────────────────────────
def test_clean_strips_leading_filler():
    assert _clean_food_token("makan abon") == "abon"


def test_clean_keeps_real_name():
    assert _clean_food_token("nasi goreng") == "nasi goreng"


# ─── try_local_parse (pakai CSV asli, tanpa LLM) ──────────────────────────────
def test_fast_path_single_known_food():
    # 'abon' ada di dataset/foods_combined.csv
    items = try_local_parse("abon")
    assert items is not None
    assert len(items) == 1
    assert items[0]["name"] == "abon"
    assert items[0]["grams"] > 0


def test_fast_path_multi_known_food():
    items = try_local_parse("abon sama abon haruwan")
    assert items is not None
    assert len(items) == 2
    names = {it["name"] for it in items}
    assert "abon" in names and "abon haruwan" in names


def test_fast_path_with_filler_prefix():
    items = try_local_parse("makan abon")
    assert items is not None
    assert items[0]["name"] == "abon"


def test_fast_path_bails_on_unknown_food():
    # Kata sampah yang tidak ada di DB → None (pipeline harus fallback ke LLM)
    assert try_local_parse("zzqqx makanan tidak ada di database") is None


def test_fast_path_bails_when_any_chunk_unknown():
    # Satu dikenal, satu tidak → seluruh fast-path dibatalkan
    assert try_local_parse("abon sama zzqqx-notafood") is None


def test_fast_path_empty_input():
    assert try_local_parse("") is None
    assert try_local_parse("   ") is None


# ─── akurasi porsi (regresi: default_portion_g=100 adalah nilai pengisi) ─────
def test_fast_path_plate_dish_uses_category_portion():
    # nasi goreng: default_portion_g=100 (pengisi) → kategori 'nasi' → 250g
    items = try_local_parse("nasi goreng")
    assert items is not None
    assert items[0]["grams"] == 250.0


def test_fast_path_curated_portion_wins():
    # soto ayam: default_portion_g=350 terkurasi → dipakai apa adanya
    items = try_local_parse("soto ayam")
    assert items is not None
    assert items[0]["grams"] == 350.0


def test_fast_path_qty_multiplies_portion():
    items = try_local_parse("2 nasi goreng")
    assert items is not None
    assert items[0]["qty"] == 2.0
    assert items[0]["grams"] == 500.0


def test_fast_path_explicit_grams_respected():
    items = try_local_parse("nasi goreng 150 gram")
    assert items is not None
    assert items[0]["grams"] == 150.0


def test_fast_path_bails_on_piece_units():
    # Berat per-biji (ekor/butir/lembar) bervariasi → wajib ke LLM
    assert try_local_parse("udang goreng 5 ekor") is None


def test_fast_path_full_dish_override_beats_sayur_category():
    # gado-gado kategori 'sayur' (150g) tapi ia hidangan utuh → override 250g
    items = try_local_parse("gado-gado")
    assert items is not None
    assert items[0]["grams"] == 250.0


# ─── helper lama tetap konsisten ──────────────────────────────────────────────
def test_normalize_alias():
    assert normalize_food_name("nasgor") == "nasi goreng"


def test_convert_to_gram_known_unit():
    assert convert_to_gram(2, "gelas", 100) == 500  # 2 × 250


def test_convert_to_gram_portion_uses_estimate():
    assert convert_to_gram(1, "porsi", 175) == 175
