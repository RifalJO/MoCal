# Panduan Deployment MoCal (Full-Stack)

Ikuti langkah-langkah ini untuk memindahkan aplikasi MoCal dari komputer lokal ke internet.

## 1. Persiapan Database (Supabase)

Aplikasi ini menggunakan PostgreSQL. Cara termudah adalah menggunakan **Supabase**.

1. Buat akun di [supabase.com](https://supabase.com).
2. Buat project baru bernama `MoCal`.
3. Buka **Project Settings** > **Database**.
4. Cari bagian **Connection String**.
5. **PENTING UNTUK VERCEL:** Cari tab/opsian **Connection Pooler** (Proxy).
   - Pastikan **Mode** diatur ke **Transaction** atau **Session**.
   - Gunakan URL yang diberikan (biasanya menggunakan port **6543**).
   - Contoh: `postgres://postgres.xxxx:[PASSWORD]@aws-0-xxxx.pooler.supabase.com:6543/postgres?pgbouncer=true`
6. Ganti `[PASSWORD]` dengan password database kamu.
7. Simpan URL ini untuk dimasukkan ke Vercel Environment Variables.

---

## 2. Deploy ke Vercel

Kita akan menggunakan Vercel untuk menjalankan Backend (FastAPI) dan Frontend (React) secara bersamaan.

1. Simpan semua perubahan code kamu:
   ```bash
   git add .
   git commit -m "Fix: production API URL and database connection"
   git push origin main
   ```
2. Masuk ke [vercel.com](https://vercel.com) dan klik **Add New** > **Project**.
3. Pilih repository GitHub kamu.
4. Vercel akan mendeteksi file `vercel.json`. Klik **Deploy**.

---

## 3. Konfigurasi Environment Variables

Buka project kamu di Dashboard Vercel, masuk ke **Settings** > **Environment Variables**, lalu tambahkan:

### Required Variables:
| Key | Value | Keterangan |
|---|---|---|
| `DATABASE_URL` | URL dari Supabase tadi | Database production |
| `GROQ_API_KEY` | API Key dari console.groq.com | Untuk AI Parsing |
| `USDA_API_KEY` | API Key dari fdc.nal.usda.gov | Untuk Nutrition Data |
| `APP_ENV` | `production` | Mode aplikasi |
| `SECRET_KEY` | Deretan karakter acak | Contoh: `mocal_secure_123` |

> [!NOTE]
> Kamu **tidak perlu** menyetel `VITE_API_URL`. Aplikasi sudah dikonfigurasi untuk menggunakan relative path `/api` yang secara otomatis mengarah ke backend Vercel kamu.

---

## 4. Import Data ke Database Cloud

Karena database Supabase masih kosong, kamu perlu mengimport data CSV dari lokal ke Supabase.

1. Buka file `.env` di lokal kamu.
2. Ganti `DATABASE_URL` sementara dengan URL Supabase tadi.
3. Jalankan script import di terminal lokal:
   ```bash
   python scripts/import_dataset.py dataset/foods_cleaned_nutrients.csv
   ```
4. Jika muncul `✅ Import selesai!`, data sekarang sudah ada di cloud!

---

## 5. Verifikasi

1. Buka URL yang diberikan oleh Vercel (contoh: `mocal.vercel.app`).
2. Coba login atau hitung kalori.
3. Jika masih error, cek tab **Logs** di Vercel Dashboard untuk melihat pesan error dari FastAPI.
