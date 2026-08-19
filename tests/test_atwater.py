"""Tes konsistensi kcal vs makro (Atwater) — murni lokal, tanpa LLM/DB."""

from app.validator import atwater_kcal, is_kcal_consistent


def test_atwater_menghitung_4_4_9():
    assert atwater_kcal(10, 20, 5) == 4 * 10 + 4 * 20 + 9 * 5


def test_nilai_wajar_dianggap_konsisten():
    # nasi goreng: 168 kkal, makro menghasilkan ~173 -> selisih kecil
    assert is_kcal_consistent(168, 4, 28, 5) is True


def test_kasus_cireng_umami_terdeteksi_tidak_konsisten():
    # Data nyata: kcal tersimpan 32.2 tapi makronya menghasilkan ~129 kkal
    assert is_kcal_consistent(32.2, 1.8, 15.7, 6.6) is False


def test_makro_ngawur_terdeteksi():
    # soto madura: kcal 139 tapi Atwater ~9665
    assert is_kcal_consistent(139, 500, 1000, 700) is False


def test_air_putih_nol_kalori_tetap_lolos():
    assert is_kcal_consistent(0, 0, 0, 0) is True


def test_makro_kosong_tidak_bisa_dinilai_maka_lolos():
    # Banyak entri lama hanya punya kcal tanpa rincian makro
    assert is_kcal_consistent(200, 0, 0, 0) is True


def test_kcal_bukan_angka_ditolak():
    assert is_kcal_consistent(None, 1, 2, 3) is False
    assert is_kcal_consistent("abc", 1, 2, 3) is False


def test_makanan_rendah_kalori_tidak_kena_positif_palsu():
    # teh manis 35 kkal, makro ~34 kkal -> harus lolos berkat lantai absolut
    assert is_kcal_consistent(35, 0, 8.5, 0) is True
