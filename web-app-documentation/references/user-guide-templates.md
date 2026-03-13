# User Guide Templates

Template panduan pengguna yang siap diisi dengan konten spesifik aplikasi.

---

## Template: Getting Started Guide

```markdown
# Panduan Memulai [NAMA APLIKASI]

Selamat datang! Panduan ini akan membantu Anda mulai menggunakan [NAMA APLIKASI] dalam [X] menit.

## Prasyarat
Sebelum memulai, pastikan Anda memiliki:
- [ ] Koneksi internet aktif
- [ ] Browser modern (Chrome, Firefox, Safari, Edge versi terbaru)
- [ ] [Prasyarat lain jika ada]

## Langkah 1: Buat Akun

1. Buka **[app.example.com](https://app.example.com)** di browser Anda
2. Klik tombol **"Daftar Gratis"** di pojok kanan atas

   [SCREENSHOT: Halaman utama dengan tombol Daftar]

3. Isi formulir pendaftaran:
   - **Nama**: Masukkan nama lengkap Anda
   - **Email**: Gunakan email yang aktif (akan dikirim verifikasi)
   - **Password**: Minimal 8 karakter

4. Centang "Saya menyetujui Syarat & Ketentuan"
5. Klik **"Buat Akun"**

   [SCREENSHOT: Formulir pendaftaran yang sudah diisi]

> ✉️ **Cek email Anda!** Kami mengirim link verifikasi. Cek juga folder Spam jika tidak ada di Inbox.

## Langkah 2: Verifikasi Email

1. Buka email dari noreply@example.com
2. Klik tombol **"Verifikasi Email Saya"**
3. Anda akan diarahkan kembali ke aplikasi — akun Anda sudah aktif!

## Langkah 3: Lengkapi Profil

1. Setelah login, klik nama Anda di pojok kanan atas
2. Pilih **"Pengaturan Profil"**
3. Lengkapi informasi:
   - Foto profil
   - Nomor telepon
   - [Informasi lain]
4. Klik **"Simpan Perubahan"**

## Anda Siap! 🎉

Sekarang Anda bisa mulai menggunakan [NAMA APLIKASI]. Coba mulai dengan:
- 📊 [Aksi pertama yang direkomendasikan]
- 🔧 [Konfigurasi dasar]
- 📖 [Tutorial lanjutan]
```

---

## Template: Feature How-To Guide

```markdown
# Cara [NAMA FITUR]

**Waktu**: ~[X] menit | **Tingkat**: Pemula / Menengah / Mahir

## Gambaran Singkat
[Jelaskan apa yang akan dicapai pengguna setelah mengikuti panduan ini]

## Sebelum Memulai
- ✅ Pastikan Anda sudah [prasyarat 1]
- ✅ Anda membutuhkan akses [role/permission]

## Langkah-langkah

### Langkah 1: [Nama Langkah]
[Deskripsi langkah]

1. Navigasi ke **Menu → Submenu**
2. Klik tombol **"[Nama Tombol]"**

   [SCREENSHOT: Tampilan halaman X]

3. Isi kolom yang diperlukan:
   | Kolom | Keterangan | Contoh |
   |-------|-----------|--------|
   | Nama | Nama item | Laporan Bulanan |
   | Tanggal | Format DD/MM/YYYY | 01/03/2024 |

> 💡 **Tips**: [Tip berguna untuk langkah ini]

### Langkah 2: [Nama Langkah]
[Lanjutkan pola yang sama]

## Hasil yang Diharapkan
Setelah mengikuti langkah di atas, Anda akan:
- ✅ [Hasil 1]
- ✅ [Hasil 2]

[SCREENSHOT: Tampilan akhir setelah fitur berhasil digunakan]

## Langkah Selanjutnya
- 📖 [Link ke panduan terkait]
- 🔗 [Fitur lanjutan yang relevan]
```

---

## Template: FAQ Section

```markdown
# Pertanyaan yang Sering Ditanyakan (FAQ)

## Akun & Login

**Q: Bagaimana cara reset password?**

A: 
1. Buka halaman login
2. Klik **"Lupa Password?"** di bawah tombol login
3. Masukkan email yang terdaftar
4. Cek email Anda dan klik link reset (berlaku 1 jam)
5. Masukkan password baru

---

**Q: Akun saya terkunci. Apa yang harus saya lakukan?**

A: Akun terkunci otomatis setelah 5 kali percobaan login yang gagal. Tunggu **15 menit** atau hubungi support di help@example.com.

---

**Q: Bagaimana cara mengganti email akun?**

A: Saat ini pergantian email tidak bisa dilakukan mandiri. Hubungi support kami dengan bukti identitas untuk mengubah email.

---

## Fitur & Penggunaan

**Q: [Pertanyaan tentang fitur 1]?**

A: [Jawaban]

---

**Q: Apakah ada versi mobile/aplikasi?**

A: [Ya/Tidak] — [Penjelasan dan link jika ada]

---

## Billing & Pembayaran

**Q: Metode pembayaran apa yang diterima?**

A: Kami menerima:
- Transfer bank (BCA, BNI, BRI, Mandiri)
- Kartu kredit/debit Visa & Mastercard
- GoPay, OVO, Dana

---

**Q: Bagaimana cara mendapatkan invoice?**

A: Invoice otomatis dikirim ke email setiap pembayaran berhasil. Anda juga bisa mengunduh invoice di **Pengaturan → Billing → Riwayat Pembayaran**.

---

## Privasi & Keamanan

**Q: Apakah data saya aman?**

A: Ya. Data Anda dienkripsi dengan standar AES-256 dan disimpan di server yang telah tersertifikasi ISO 27001. Kami tidak pernah menjual data pengguna kepada pihak ketiga.

---

**Q: Bagaimana cara menghapus akun dan data saya?**

A: Anda dapat menghapus akun di **Pengaturan → Akun → Hapus Akun**. Semua data akan dihapus permanen dalam 30 hari sesuai kebijakan privasi kami.
```

---

## Template: Troubleshooting Guide

```markdown
# Panduan Troubleshooting

Panduan ini membantu Anda mengatasi masalah umum yang mungkin terjadi.

## Masalah Login

### Tidak Bisa Login
**Gejala**: Muncul pesan "Email atau password salah" meskipun sudah benar

**Solusi**:
1. Pastikan Caps Lock tidak aktif
2. Coba reset password
3. Coba buka di tab incognito/private
4. Clear cache dan cookies browser
5. Jika masih gagal: hubungi support

---

### Halaman Login Tidak Muncul / Error
**Gejala**: Halaman kosong, loading terus, atau pesan error

**Solusi**:
1. Refresh halaman (Ctrl+R / Cmd+R)
2. Cek koneksi internet Anda
3. Coba browser yang berbeda
4. Disable ekstensi browser (adblocker, dll.)
5. Cek status layanan di [status.example.com](https://status.example.com)

---

## Masalah Performa

### Aplikasi Lambat
**Gejala**: Halaman lama loading, tombol tidak responsif

**Solusi**:
1. Refresh halaman
2. Clear cache browser
3. Cek kecepatan internet Anda di [speedtest.net](https://speedtest.net)
4. Tutup tab browser lain yang tidak diperlukan
5. Coba di browser lain

---

## Masalah Upload File

### File Tidak Bisa Diupload
**Gejala**: Muncul error saat upload, atau file tidak muncul setelah upload

**Solusi**:
1. Pastikan ukuran file tidak melebihi **[X] MB**
2. Pastikan format file yang didukung: **[jpg, png, pdf, dll.]**
3. Coba rename file tanpa karakter spesial
4. Coba kompres file terlebih dahulu

---

## Masih Butuh Bantuan?

Jika masalah Anda belum teratasi:
- 📧 Email: support@example.com (respons dalam 1x24 jam)
- 💬 Live chat: Tersedia Senin-Jumat, 09.00-18.00 WIB
- 📖 Help center: [help.example.com](https://help.example.com)

Saat menghubungi support, sertakan:
- Screenshot error yang muncul
- Browser dan versi yang digunakan
- Langkah-langkah yang sudah dicoba
```

---

## Template: Release Notes / Pembaruan

```markdown
# Pembaruan Terbaru

## Versi 1.2.0 — 15 Maret 2024

### ✨ Fitur Baru
- **Export CSV**: Kini Anda bisa mengekspor data ke format CSV dari menu laporan
- **Dark Mode**: Tambahkan opsi tampilan gelap di Pengaturan → Tampilan

### 🔧 Perbaikan
- Performa halaman dashboard meningkat 40% lebih cepat
- Filter tanggal kini berfungsi normal di Safari
- Perbaikan tampilan di layar mobile

### 🗑️ Dihapus
- Widget statistik lama digantikan dengan dashboard baru

---

## Versi 1.1.0 — 1 Februari 2024

### ✨ Fitur Baru
- **Pembayaran Midtrans**: Tambahkan metode pembayaran kartu kredit dan e-wallet
- **Notifikasi Email**: Dapatkan update otomatis via email

### 🔧 Perbaikan
- Perbaikan bug upload foto profil
- Tampilan tabel di layar kecil diperbaiki

---

*Lihat riwayat lengkap pembaruan di [changelog.example.com](https://changelog.example.com)*
```
