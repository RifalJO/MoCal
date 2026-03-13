---
name: web-app-documentation
description: >
  Membuat dokumentasi lengkap dan profesional untuk aplikasi berbasis website.
  Gunakan skill ini setiap kali pengguna meminta dokumentasi aplikasi web, technical docs,
  user guide, API docs, panduan deployment, atau dokumen apapun yang berkaitan dengan
  mendokumentasikan sebuah website/web application — bahkan jika mereka hanya bilang
  "buatkan dokumentasi project saya", "buat tech spec", "tulis user manual", atau
  "dokumentasikan API ini". Skill ini mencakup seluruh siklus dokumentasi:
  overview, arsitektur, frontend, backend, API reference, database schema,
  autentikasi & keamanan, deployment, user guide, testing, dan changelog.
---

# Web Application Documentation Skill

Skill ini memandu Claude untuk menghasilkan dokumentasi web application yang **lengkap, terstruktur, dan profesional** — mencakup semua lapisan dari sudut pandang teknis maupun pengguna akhir.

---

## 🔍 Langkah 1: Kumpulkan Informasi dari Pengguna

Sebelum mulai menulis, **tanyakan atau ekstrak dari konteks** informasi berikut:

### Pertanyaan Wajib
1. **Nama & deskripsi singkat aplikasi** — Apa yang dilakukan aplikasi ini?
2. **Tech stack** — Frontend (React, Vue, Angular, dll.), Backend (Node, Laravel, Django, dll.), Database?
3. **Siapa audiensnya?** — Developer, end-user, stakeholder bisnis, atau semuanya?
4. **Jenis dokumentasi yang dibutuhkan** — Teknis penuh, user guide saja, API saja, atau semuanya?
5. **Apakah ada kode / file / endpoint yang bisa disertakan?** — Jika ada, minta pengguna upload atau paste.

### Informasi Opsional (tapi memperkaya)
- URL produksi / staging
- Diagram arsitektur yang sudah ada
- Daftar fitur utama
- Tim/roles yang terlibat
- Versi saat ini dan changelog

> Jika pengguna tidak memberikan detail, **gunakan placeholder** yang jelas seperti `[NAMA_APLIKASI]`, `[TECH_STACK]`, dll., dan tandai bagian yang perlu dilengkapi.

---

## 📐 Struktur Dokumentasi Lengkap

Dokumentasi web app yang baik terdiri dari **12 bagian utama** berikut. Sesuaikan dengan kebutuhan pengguna — tidak semua proyek butuh semua bagian.

Lihat panduan detail tiap bagian di: `references/sections-guide.md`

### Ringkasan Bagian

| # | Bagian | Prioritas | Target Audiens |
|---|--------|-----------|----------------|
| 1 | Project Overview | ⭐ Wajib | Semua |
| 2 | Architecture Overview | ⭐ Wajib | Developer |
| 3 | Tech Stack | ⭐ Wajib | Developer |
| 4 | Frontend Documentation | Tinggi | Frontend Dev |
| 5 | Backend Documentation | Tinggi | Backend Dev |
| 6 | API Reference | ⭐ Wajib (jika ada API) | Developer |
| 7 | Database & Data Model | Tinggi | Backend Dev / DBA |
| 8 | Authentication & Security | ⭐ Wajib | Developer |
| 9 | Deployment & Infrastructure | Tinggi | DevOps / Dev |
| 10 | User Guide | Tinggi | End User |
| 11 | Testing Documentation | Sedang | QA / Dev |
| 12 | Changelog & Versioning | Sedang | Semua |

---

## ✍️ Langkah 2: Tulis Dokumentasi

### Format Output

- **Format default**: Markdown (`.md`) — cocok untuk GitHub, GitBook, Notion, dsb.
- **Format alternatif**: Jika pengguna minta Word (.docx), PDF, atau HTML — gunakan skill `docx`, `pdf`, atau buat HTML artifact.
- **Bahasa**: Sesuaikan dengan bahasa yang digunakan pengguna (Indonesia atau Inggris).

### Aturan Penulisan

1. **Clarity first** — Gunakan bahasa yang jelas, hindari jargon tidak perlu
2. **Consistent terminology** — Gunakan istilah yang sama di seluruh dokumen
3. **Show, don't just tell** — Sertakan contoh kode, screenshot placeholder, atau diagram ASCII bila perlu
4. **Structure properly** — Gunakan heading hierarki (H1 > H2 > H3), jangan melompat level
5. **Include examples** — Setiap endpoint API harus punya contoh request/response
6. **Mark TODOs** — Tandai bagian yang perlu diisi pengguna dengan `> ⚠️ TODO: ...`

### Template Cepat per Tipe Request

**Jika hanya minta API docs** → Buat bagian 6 (API Reference) saja secara mendalam  
**Jika hanya minta user guide** → Buat bagian 10 (User Guide) dengan screenshot placeholder  
**Jika minta full dokumentasi** → Buat semua 12 bagian, mulai dari bagian 1-3 dulu  
**Jika minta technical spec** → Fokus pada bagian 2, 3, 4, 5, 7, 8  

---

## 📦 Langkah 3: Struktur File yang Dihasilkan

Untuk dokumentasi lengkap, buat struktur folder berikut:

```
docs/
├── README.md                    # Project overview + navigation
├── 01-project-overview.md       # Deskripsi, goals, audience
├── 02-architecture.md           # Diagram & penjelasan arsitektur
├── 03-tech-stack.md             # Semua teknologi yang digunakan
├── 04-frontend.md               # Komponen, routing, state management
├── 05-backend.md                # Services, business logic, middleware
├── 06-api-reference.md          # Semua endpoint API
├── 07-database.md               # Schema, relasi, ERD
├── 08-auth-security.md          # Autentikasi, autorisasi, keamanan
├── 09-deployment.md             # CI/CD, environment, hosting
├── 10-user-guide.md             # Panduan pengguna akhir
├── 11-testing.md                # Test plan, test cases
└── 12-changelog.md              # Versi dan riwayat perubahan
```

> Untuk proyek kecil atau quick docs, cukup buat satu file `documentation.md` yang menggabungkan semua bagian.

---

## 🔑 Panduan Khusus: API Reference

API Reference adalah bagian terpenting dalam dokumentasi teknis. Setiap endpoint **harus** memiliki:

```markdown
### [METHOD] /path/to/endpoint

**Deskripsi**: Apa yang dilakukan endpoint ini

**Authentication**: Required / Not Required / Bearer Token

**Request**
- Headers:
  | Key | Value | Required |
  |-----|-------|----------|
  | Content-Type | application/json | ✅ |
  | Authorization | Bearer {token} | ✅ |

- Body Parameters:
  | Field | Type | Required | Deskripsi |
  |-------|------|----------|-----------|
  | name | string | ✅ | Nama pengguna |

- Query Parameters: (jika ada)

**Contoh Request**
```http
POST /api/v1/users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "name": "Budi Santoso",
  "email": "budi@example.com"
}
```

**Response**
- `200 OK` — Sukses
- `400 Bad Request` — Validasi gagal
- `401 Unauthorized` — Token tidak valid
- `500 Internal Server Error` — Error server

**Contoh Response (200)**
```json
{
  "status": "success",
  "data": {
    "id": "usr_123",
    "name": "Budi Santoso"
  }
}
```
```

---

## 🗺️ Panduan Khusus: Architecture Diagram

Jika pengguna tidak punya diagram, buat **ASCII/text diagram** sebagai placeholder:

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT LAYER                      │
│  Browser / Mobile  ←→  CDN (Cloudflare/CloudFront)   │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────┐
│                 APPLICATION LAYER                    │
│  Load Balancer  →  Web Server (Nginx/Apache)         │
│                 →  App Server (Node/Laravel/Django)  │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                    DATA LAYER                        │
│  Primary DB (PostgreSQL/MySQL)  +  Cache (Redis)     │
│  Object Storage (S3/MinIO)      +  Search (Elastic)  │
└─────────────────────────────────────────────────────┘
```

Sesuaikan dengan tech stack yang diberikan pengguna.

---

## ✅ Checklist Kualitas Dokumentasi

Sebelum menyerahkan hasil, pastikan:

- [ ] Semua bagian yang diminta sudah ada
- [ ] Tidak ada placeholder yang terlupakan (selain yang memang perlu diisi pengguna)
- [ ] Semua contoh kode/API bisa dijalankan atau masuk akal
- [ ] Terminologi konsisten di seluruh dokumen
- [ ] Ada navigasi / daftar isi di bagian atas
- [ ] Bahasa sesuai permintaan (Indonesia / Inggris)
- [ ] Format file sesuai (Markdown, DOCX, PDF, dll.)

---

## 📚 Referensi Tambahan

- `references/sections-guide.md` — Panduan detail untuk setiap bagian dokumentasi
- `references/api-templates.md` — Template siap pakai untuk berbagai pola API
- `references/user-guide-templates.md` — Template panduan pengguna dengan screenshot placeholder
