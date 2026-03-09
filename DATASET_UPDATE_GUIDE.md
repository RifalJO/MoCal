# 📦 Dataset Update Guide

## Cara Update Dataset Makanan

### **Opsi 1: Replace Semua Dataset (Recommended)**

Jika ingin mengganti **semua** data makanan dengan dataset baru:

#### **Step 1: Prepare File CSV**

Format file CSV harus seperti ini:

```csv
id,name,name_aliases,cal,protein,carbs,fat,default_portion_g,source,is_indonesian
uuid-generate-1,nasi padang,nasi padang padang,250.0,8.5,35.0,10.0,250.0,indo_nutrition,True
uuid-generate-2,ayam bakar,,180.0,25.0,0.0,8.0,150.0,dapur_umami,True
```

**Kolom yang wajib ada:**
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | UUID | Unique ID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) |
| `name` | String | Nama makanan (harus unik) |
| `name_aliases` | String | Alias nama, pisahkan dengan `|` (optional) |
| `cal` | Float | Kalori per 100g |
| `protein` | Float | Protein per 100g (gram) |
| `carbs` | Float | Karbohidrat per 100g (gram) |
| `fat` | Float | Lemak per 100g (gram) |
| `default_portion_g` | Float | Berat porsi default (gram) |
| `source` | String | Sumber data (e.g., `indo_nutrition`, `dapur_umami`) |
| `is_indonesian` | Boolean | `True` untuk makanan Indonesia |

#### **Step 2: Generate UUID (Optional)**

Jika tidak ada kolom `id`, script akan auto-generate UUID.

Atau generate manual:
```python
import uuid
print(str(uuid.uuid4()))
# Output: 5a8e0d63-1989-4462-91ea-173a25433fa9
```

#### **Step 3: Backup Dataset Lama**

```bash
cd c:\Users\kinga\OneDrive\Dokumen\Gunadarma\Semester 8\Skripsi\TrackCalorieByType\MoCal

# Backup
copy dataset\foods_combined.csv dataset\foods_combined_backup.csv
```

#### **Step 4: Replace File Dataset**

```bash
# Copy file CSV baru ke folder dataset/
# Replace file yang lama
```

#### **Step 5: Jalankan Script Import**

```bash
# Activate virtual environment
cd c:\Users\kinga\OneDrive\Dokumen\Gunadarma\Semester 8\Skripsi\TrackCalorieByType\MoCal
.\venv\Scripts\Activate

# Import dataset (replace mode)
python scripts\import_dataset.py dataset\foods_combined.csv
```

**Output:**
```
================================================================================
📦 DATASET IMPORT TOOL
================================================================================

📊 Dataset info:
   File: dataset/foods_combined.csv
   Total rows: 3,015
   Mode: replace

⚠️  REPLACE MODE: Menghapus semua data makanan yang ada...
✅ Semua data makanan dihapus

📥 Importing data...
   Processed 100/3015 rows...
   Processed 200/3015 rows...
   ...

================================================================================
✅ IMPORT COMPLETED
================================================================================
   ✅ Inserted: 3,015 foods
   ⚠️  Duplicates: 0
   ❌ Errors: 0
   📊 Total in file: 3,015
================================================================================

📦 Total foods in database: 3,015
```

#### **Step 6: Restart Backend**

```bash
# Stop backend (Ctrl+C)
# Restart
uvicorn app.main:app --reload
```

---

### **Opsi 2: Append (Tambah Data Baru)**

Jika ingin **menambah** data tanpa menghapus yang lama:

```bash
python scripts\import_dataset.py dataset\foods_baru.csv append
```

**Catatan:**
- Data yang sama (nama sama) akan di-skip
- Data baru akan ditambahkan

---

### **Opsi 3: Manual via SQL**

Untuk advanced users:

```sql
-- Backup existing data
CREATE TABLE foods_backup AS SELECT * FROM foods;

-- Delete all
DELETE FROM foods;

-- Import from CSV (using pgAdmin or psql)
\copy foods(id, name, name_aliases, cal, protein, carbs, fat, default_portion_g, source, is_indonesian) 
FROM 'C:/path/to/dataset/foods_combined.csv' 
DELIMITER ',' 
CSV HEADER;

-- Verify
SELECT COUNT(*) FROM foods;
```

---

## 📋 Template CSV

Download template kosong:

```csv
id,name,name_aliases,cal,protein,carbs,fat,default_portion_g,source,is_indonesian
,nasi goreng,,175.0,5.0,30.0,4.0,200.0,indo_nutrition,True
,rendang daging,rendang,210.0,20.0,5.0,12.0,150.0,dapur_umami,True
```

**Tips:**
- Kolom `id` boleh kosong, akan di-auto-generate
- Gunakan titik (`.`) untuk desimal, bukan koma
- Food names harus unik

---

## 🧪 Testing

Setelah import, test:

```bash
# 1. Check database
psql -U postgres -d calorie_tracker
SELECT COUNT(*) FROM foods;
SELECT * FROM foods WHERE name = 'nasi padang';

# 2. Test API
http://localhost:8000/api/foods/search?q=nasi%20padang

# 3. Test di frontend
# Input: "nasi padang"
# Should show matching food from new dataset
```

---

## ❗ Troubleshooting

### Error: "Column mismatch"
**Solusi:** Pastikan urutan kolom di CSV sama dengan template.

### Error: "Duplicate key"
**Solusi:** Gunakan mode `append` atau hapus data lama dulu.

### Error: "Invalid UUID"
**Solusi:** Format UUID harus `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` atau kosongkan untuk auto-generate.

### Data tidak muncul setelah import
**Solusi:** 
1. Restart backend
2. Clear cache browser
3. Check log import script

---

## 📊 Script Commands Summary

| Command | Deskripsi |
|---------|-----------|
| `python scripts/import_dataset.py dataset/foods_combined.csv` | Replace semua data |
| `python scripts/import_dataset.py dataset/foods_baru.csv append` | Tambah data baru |
| `copy dataset\foods_combined.csv dataset\backup.csv` | Backup dataset |

---

## 🎯 Best Practices

1. **Selalu backup** sebelum replace dataset
2. **Test** dengan dataset kecil dulu
3. **Validate** CSV format sebelum import
4. **Check log** import script untuk errors
5. **Restart backend** setelah import besar

---

## 📝 Contoh File CSV Lengkap

```csv
id,name,name_aliases,cal,protein,carbs,fat,default_portion_g,source,is_indonesian
,nasi padang,nasi padang padang,250.0,8.5,35.0,10.0,250.0,indo_nutrition,True
,tunjang,kikil sapi,150.0,25.0,0.0,5.0,100.0,dapur_umami,True
,ceker ayam,,60.0,20.0,0.0,1.0,50.0,indo_nutrition,True
,es kelapa muda,,45.0,0.0,10.0,0.0,250.0,daily_nutrition,True
```

**Note:** Kolom `id` dikosongkan untuk auto-generate UUID.
