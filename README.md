# Calorie Tracker — Backend Setup Guide
# Ikuti langkah-langkah ini BERURUTAN

## Struktur Folder
```
calorie-tracker/
├── app/
│   ├── main.py          ← FastAPI app + semua endpoint
│   ├── database.py      ← koneksi PostgreSQL + model tabel
│   ├── matcher.py       ← fuzzy matching engine
│   └── parser.py        ← LLM parser (Groq) + konversi porsi
├── scripts/
│   └── import_dataset.py ← import CSV ke database
├── requirements.txt
├── .env.example
└── README.md
```

---

## LANGKAH 1 — Buat Virtual Environment

Buka terminal / CMD di folder calorie-tracker, lalu jalankan:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

---

## LANGKAH 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## LANGKAH 3 — Setup Database PostgreSQL

Buka pgAdmin atau psql, buat database baru:

```sql
CREATE DATABASE calorie_tracker;
```

---

## LANGKAH 4 — Isi File .env

Copy file .env.example menjadi .env:
```bash
copy .env.example .env     # Windows
# cp .env.example .env     # Mac/Linux
```

Lalu buka .env dan isi:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=calorie_tracker
DB_USER=postgres
DB_PASSWORD=password_postgresql_kamu

GROQ_API_KEY=gsk_xxxxxxxxxxxx     # dari console.groq.com
USDA_API_KEY=xxxxxxxxxxxx         # dari fdc.nal.usda.gov/api-guide
```

---

## LANGKAH 5 — Import Dataset

Pastikan file CSV kamu sudah ada, lalu jalankan:

```bash
python scripts/import_dataset.py path/ke/foods_combined.csv
```

Contoh output yang diharapkan:
```
✅ Tabel berhasil dibuat
📂 Membaca file: foods_combined.csv
📊 Total baris di CSV: 3015
✅ Setelah cleaning: 2987 baris
✅ Import selesai!
   Berhasil diimport : 2987 baris
   Dilewati (duplikat): 0 baris
   Total di DB        : 2987 makanan
```

---

## LANGKAH 6 — Jalankan Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server berjalan di: http://localhost:8000

---

## LANGKAH 7 — Test API

### Cek server hidup:
```
GET http://localhost:8000/
```

### Cek stats database:
```
GET http://localhost:8000/api/stats
```

### Test estimasi kalori:
```
POST http://localhost:8000/api/estimate
Content-Type: application/json

{
  "text": "tadi siang makan nasi goreng 1 porsi sama es teh manis"
}
```

### Contoh response:
```json
{
  "log_id": "uuid...",
  "raw_input": "tadi siang makan nasi goreng 1 porsi sama es teh manis",
  "items": [
    {
      "name_raw": "nasi goreng",
      "name_matched": "nasi goreng",
      "qty": 1,
      "unit": "porsi",
      "gram": 250.0,
      "kcal": 350.0,
      "protein_g": 8.5,
      "carbs_g": 55.2,
      "fat_g": 11.3,
      "match_method": "fuzzy",
      "match_score": 0.95,
      "source": "tkpi",
      "is_estimate": false
    }
  ],
  "total_kcal": 430.0,
  "total_protein_g": 9.5,
  "total_carbs_g": 68.2,
  "total_fat_g": 11.3,
  "unknown_items": []
}
```

---

## Dokumentasi API Otomatis

FastAPI menyediakan dokumentasi interaktif di:
- Swagger UI : http://localhost:8000/docs
- ReDoc      : http://localhost:8000/redoc

Kamu bisa test semua endpoint langsung dari browser!

---

## Troubleshooting

| Error | Solusi |
|-------|--------|
| `connection refused` di DB | Pastikan PostgreSQL service berjalan |
| `GROQ_API_KEY not set` | Isi .env dengan API key yang benar |
| `ModuleNotFoundError` | Pastikan venv aktif dan `pip install -r requirements.txt` sudah dijalankan |
| `column not found` saat import | Sesuaikan COLUMN_MAP di scripts/import_dataset.py |
