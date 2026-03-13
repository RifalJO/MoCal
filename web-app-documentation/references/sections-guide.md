# Panduan Detail Tiap Bagian Dokumentasi

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Tech Stack](#3-tech-stack)
4. [Frontend Documentation](#4-frontend-documentation)
5. [Backend Documentation](#5-backend-documentation)
6. [API Reference](#6-api-reference)
7. [Database & Data Model](#7-database--data-model)
8. [Authentication & Security](#8-authentication--security)
9. [Deployment & Infrastructure](#9-deployment--infrastructure)
10. [User Guide](#10-user-guide)
11. [Testing Documentation](#11-testing-documentation)
12. [Changelog & Versioning](#12-changelog--versioning)

---

## 1. Project Overview

**Tujuan**: Memberikan gambaran awal yang bisa dipahami siapa saja — dari developer baru hingga stakeholder non-teknis.

**Wajib ada**:
- Nama & tagline aplikasi
- Deskripsi singkat (2-3 kalimat)
- Problem yang diselesaikan
- Target pengguna / persona
- Fitur-fitur utama (bullet list)
- Status proyek (In Development / Beta / Production)
- Link penting (repo, demo, staging, production)

**Template**:
```markdown
# [NAMA APLIKASI]

> [Tagline singkat — 1 kalimat]

## Tentang Aplikasi
[Deskripsi 2-3 kalimat tentang apa yang dilakukan aplikasi]

## Masalah yang Diselesaikan
[Jelaskan pain point yang diatasi]

## Pengguna Sasaran
- [Persona 1]
- [Persona 2]

## Fitur Utama
- ✅ [Fitur 1]
- ✅ [Fitur 2]
- 🚧 [Fitur dalam pengembangan]

## Status
**Versi**: 1.0.0 | **Status**: Production

## Link
- 🌐 [Production](https://app.example.com)
- 🧪 [Staging](https://staging.example.com)
- 💻 [Repository](https://github.com/org/repo)
```

---

## 2. Architecture Overview

**Tujuan**: Menggambarkan bagaimana komponen sistem berinteraksi satu sama lain.

**Wajib ada**:
- Diagram arsitektur sistem (minimal ASCII/text diagram)
- Penjelasan tiap layer (client, server, database, external services)
- Alur data utama (data flow)
- Keputusan arsitektur penting (mengapa memilih arsitektur ini)
- Integrasi eksternal (third-party services, webhooks, dll.)

**Pola Umum yang Harus Dikenali**:
- **Monolith**: Single deployment unit — cocok untuk tim kecil
- **Microservices**: Multiple services — cocok untuk skala besar
- **Serverless**: Functions as a Service — cocok untuk workload tak menentu
- **JAMstack**: Static frontend + API — cocok untuk website content-heavy
- **MVC / MVC-like**: Model-View-Controller — pola klasik Laravel/Django

**Template Section**:
```markdown
## Arsitektur Sistem

### Gambaran Umum
Aplikasi menggunakan arsitektur [TIPE] dengan [N] layer utama.

### Diagram
[ASCII Diagram atau link ke gambar]

### Komponen Utama
| Komponen | Teknologi | Tanggung Jawab |
|----------|-----------|----------------|
| Frontend | React.js | UI & UX |
| Backend API | Node.js + Express | Business Logic |
| Database | PostgreSQL | Penyimpanan Data |
| Cache | Redis | Session & Cache |
| CDN | Cloudflare | Asset Delivery |

### Alur Data
1. User request masuk melalui CDN
2. Request diteruskan ke Load Balancer
3. Load Balancer mendistribusikan ke App Server
4. App Server memproses dan query ke Database
5. Response dikembalikan ke user
```

---

## 3. Tech Stack

**Tujuan**: Daftar lengkap semua teknologi, library, dan tools yang digunakan.

**Wajib ada**:
- Frontend stack (framework, UI library, state management)
- Backend stack (language, framework, ORM)
- Database (primary, cache, search)
- Infrastructure (cloud, hosting, CDN)
- DevOps tools (CI/CD, monitoring, logging)
- Development tools (package manager, linting, formatting)
- External services & integrations

**Template**:
```markdown
## Tech Stack

### Frontend
| Teknologi | Versi | Kegunaan |
|-----------|-------|---------|
| React | 18.x | UI Framework |
| TypeScript | 5.x | Type Safety |
| Tailwind CSS | 3.x | Styling |
| Zustand | 4.x | State Management |
| React Query | 5.x | Server State |
| Vite | 5.x | Build Tool |

### Backend
| Teknologi | Versi | Kegunaan |
|-----------|-------|---------|
| Node.js | 20.x | Runtime |
| Express | 4.x | Web Framework |
| Prisma | 5.x | ORM |
| JWT | - | Authentication |
| Zod | 3.x | Validation |

### Database & Storage
| Teknologi | Kegunaan |
|-----------|---------|
| PostgreSQL 15 | Primary Database |
| Redis 7 | Cache & Session |
| AWS S3 | File Storage |

### Infrastructure
| Teknologi | Kegunaan |
|-----------|---------|
| AWS EC2 | App Server |
| AWS RDS | Managed Database |
| Cloudflare | CDN & DNS |
| GitHub Actions | CI/CD |
| Datadog | Monitoring |
```

---

## 4. Frontend Documentation

**Tujuan**: Panduan lengkap untuk developer yang bekerja di sisi frontend.

**Wajib ada**:
- Struktur folder & file
- Konvensi penamaan
- Komponen utama (component tree)
- Routing / navigation structure
- State management (global vs local)
- Environment variables yang dibutuhkan
- Cara menjalankan di lokal

**Template**:
```markdown
## Frontend

### Instalasi & Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Struktur Folder
```
src/
├── components/         # Reusable UI components
│   ├── common/         # Button, Input, Modal, dll.
│   └── features/       # Feature-specific components
├── pages/              # Page components (route-based)
├── hooks/              # Custom React hooks
├── store/              # State management (Zustand/Redux)
├── services/           # API call functions
├── utils/              # Helper functions
├── types/              # TypeScript type definitions
└── assets/             # Images, fonts, icons
```

### Routing
| Route | Komponen | Deskripsi | Auth? |
|-------|----------|-----------|-------|
| `/` | HomePage | Halaman utama | ❌ |
| `/dashboard` | Dashboard | Dashboard user | ✅ |
| `/settings` | Settings | Pengaturan akun | ✅ |

### Environment Variables
| Variable | Required | Default | Deskripsi |
|----------|----------|---------|-----------|
| VITE_API_URL | ✅ | - | Base URL Backend API |
| VITE_GOOGLE_CLIENT_ID | ✅ | - | Google OAuth Client ID |
```

---

## 5. Backend Documentation

**Tujuan**: Panduan untuk developer yang bekerja di sisi server/API.

**Wajib ada**:
- Struktur folder & file
- Cara kerja middleware
- Service layer dan business logic utama
- Error handling strategy
- Logging approach
- Environment variables
- Cara menjalankan di lokal

**Template**:
```markdown
## Backend

### Instalasi & Setup
```bash
cd backend
npm install
cp .env.example .env
npx prisma migrate dev
npm run dev
```

### Struktur Folder
```
src/
├── routes/             # Route definitions
├── controllers/        # Request handlers
├── services/           # Business logic
├── models/             # Database models
├── middleware/         # Auth, logging, validation
├── utils/              # Helper functions
├── config/             # Configuration files
└── types/              # TypeScript interfaces
```

### Middleware Stack
Request → Rate Limiter → CORS → Auth Validator → Route Handler → Error Handler

### Environment Variables
| Variable | Required | Deskripsi |
|----------|----------|-----------|
| DATABASE_URL | ✅ | PostgreSQL connection string |
| JWT_SECRET | ✅ | Secret key untuk JWT |
| REDIS_URL | ✅ | Redis connection string |
| PORT | ❌ | Port server (default: 3000) |
```

---

## 6. API Reference

*(Lihat panduan khusus di SKILL.md — bagian "Panduan Khusus: API Reference")*

**Tambahan yang harus ada**:
- Base URL untuk setiap environment
- Versi API dan cara versioning (v1, v2, dsb.)
- Format response standar (sukses & error)
- Rate limiting policy
- Pagination pattern (offset, cursor, dsb.)
- Authentication method (Bearer, API Key, OAuth)
- Daftar semua error code global

**Format Response Standar**:
```json
// Success
{
  "status": "success",
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}

// Error
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email sudah digunakan",
    "details": [...]
  }
}
```

---

## 7. Database & Data Model

**Tujuan**: Mendokumentasikan struktur data, relasi, dan keputusan desain database.

**Wajib ada**:
- ERD (Entity Relationship Diagram) — minimal teks/ASCII
- Deskripsi tiap tabel/collection
- Field penting beserta tipe data dan constraint
- Relasi antar tabel
- Index yang digunakan dan alasannya
- Strategi migrasi

**Template**:
```markdown
## Database

### ERD (Ringkasan)
```
users ──< orders >── products
  |                     |
  └──< addresses    categories ──< products
```

### Tabel: users
| Field | Tipe | Constraint | Deskripsi |
|-------|------|-----------|-----------|
| id | UUID | PK, NOT NULL | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email login |
| name | VARCHAR(100) | NOT NULL | Nama lengkap |
| role | ENUM | NOT NULL, DEFAULT 'user' | Role akses |
| created_at | TIMESTAMP | NOT NULL | Waktu dibuat |

### Relasi
- `users` 1:N `orders` — Satu user bisa punya banyak order
- `orders` N:M `products` melalui `order_items`

### Index
| Tabel | Kolom | Alasan |
|-------|-------|--------|
| users | email | Sering diquery untuk login |
| orders | user_id, status | Filter order per user |
```

---

## 8. Authentication & Security

**Tujuan**: Mendokumentasikan semua mekanisme keamanan aplikasi.

**Wajib ada**:
- Metode autentikasi (JWT, Session, OAuth, API Key)
- Alur login/logout
- Role & permission matrix
- Kebijakan password
- Proteksi terhadap ancaman umum (CSRF, XSS, SQL Injection)
- HTTPS & enkripsi data
- Audit log

**Template**:
```markdown
## Authentication & Security

### Metode Autentikasi
Aplikasi menggunakan **JWT (JSON Web Token)** dengan refresh token.

### Alur Login
1. User POST `/auth/login` dengan email & password
2. Server validasi kredensial
3. Server generate access token (15 menit) + refresh token (7 hari)
4. Client simpan di httpOnly cookie / localStorage
5. Setiap request sertakan `Authorization: Bearer {token}`
6. Jika access token expired, gunakan refresh token untuk dapat token baru

### Role & Permission
| Role | Dashboard | Manajemen User | Admin Panel |
|------|-----------|---------------|-------------|
| admin | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ❌ |
| user | ✅ | ❌ | ❌ |

### Security Measures
- ✅ HTTPS enforced (HSTS header)
- ✅ Input validation dengan Zod/Joi
- ✅ Parameterized queries (via ORM)
- ✅ Rate limiting (100 req/15min per IP)
- ✅ CORS whitelist
- ✅ Helmet.js security headers
- ✅ Password hashing dengan bcrypt (cost 12)
```

---

## 9. Deployment & Infrastructure

**Tujuan**: Panduan lengkap untuk men-deploy dan mengelola infrastruktur.

**Wajib ada**:
- Daftar environment (local, staging, production)
- Cara deploy (manual / otomatis via CI/CD)
- Environment variables per environment
- Health check & monitoring
- Rollback procedure
- Backup & recovery

**Template**:
```markdown
## Deployment

### Environments
| Environment | URL | Branch | Auto Deploy |
|-------------|-----|--------|-------------|
| Local | localhost:3000 | - | - |
| Staging | staging.app.com | develop | ✅ |
| Production | app.com | main | ✅ |

### CI/CD Pipeline (GitHub Actions)
1. **Test**: Run unit & integration tests
2. **Build**: Build Docker image
3. **Push**: Push ke container registry
4. **Deploy**: Deploy ke server via SSH/K8s
5. **Notify**: Kirim notif ke Slack

### Deploy Manual
```bash
# Staging
git push origin develop

# Production (via PR + merge ke main)
git checkout main && git merge develop
git push origin main
```

### Rollback
```bash
# Rollback ke versi sebelumnya
docker pull registry/app:previous-tag
docker tag registry/app:previous-tag registry/app:latest
docker-compose up -d
```

### Monitoring
- **Uptime**: UptimeRobot (alert via email + Slack)
- **APM**: Datadog / New Relic
- **Logs**: CloudWatch / Papertrail
- **Error tracking**: Sentry
```

---

## 10. User Guide

**Tujuan**: Panduan penggunaan untuk pengguna akhir (non-teknis).

**Wajib ada**:
- Cara mendaftar dan login
- Fitur utama dengan langkah-langkah step-by-step
- Screenshot placeholder (tandai dengan `[SCREENSHOT: deskripsi]`)
- FAQ
- Troubleshooting umum
- Cara menghubungi support

**Prinsip Penulisan User Guide**:
- Gunakan bahasa sehari-hari, bukan jargon teknis
- Setiap langkah harus spesifik dan actionable
- Gunakan format: Klik → Isi → Submit
- Sertakan catatan/peringatan penting di blok `> ⚠️ Penting:`

**Template**:
```markdown
## Panduan Pengguna

### Daftar Akun Baru
1. Buka [app.example.com](https://app.example.com)
2. Klik tombol **"Daftar Sekarang"** di pojok kanan atas
3. Isi formulir pendaftaran:
   - **Nama Lengkap**: Masukkan nama Anda
   - **Email**: Gunakan email aktif
   - **Password**: Minimal 8 karakter, harus mengandung huruf dan angka
4. Klik **"Buat Akun"**
5. Cek email Anda untuk verifikasi
6. Klik link verifikasi → akun aktif!

[SCREENSHOT: Halaman formulir pendaftaran]

> ⚠️ **Penting**: Link verifikasi hanya berlaku 24 jam.

### FAQ
**Q: Saya lupa password, bagaimana cara reset?**
A: Klik "Lupa Password" di halaman login, masukkan email, dan ikuti petunjuk di email yang dikirim.

**Q: Apakah data saya aman?**
A: Ya, semua data dienkripsi dan disimpan di server yang aman.
```

---

## 11. Testing Documentation

**Tujuan**: Mendokumentasikan strategi dan implementasi testing.

**Wajib ada**:
- Strategi testing (unit, integration, e2e)
- Cara menjalankan test
- Coverage target
- Test cases untuk fitur kritis
- Tools yang digunakan

**Template**:
```markdown
## Testing

### Strategi
| Level | Tools | Coverage Target |
|-------|-------|----------------|
| Unit Test | Jest / Vitest | > 80% |
| Integration Test | Supertest | API endpoints kritis |
| E2E Test | Playwright / Cypress | User flows utama |

### Menjalankan Test
```bash
# Unit tests
npm run test

# Test dengan coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# Semua tests
npm run test:all
```

### Test Cases Kritis
| Fitur | Skenario | Expected | Status |
|-------|----------|----------|--------|
| Login | Email & password valid | Redirect ke dashboard | ✅ |
| Login | Password salah 5x | Akun terkunci 15 menit | ✅ |
| Checkout | Item out of stock | Tampilkan error | 🚧 |
```

---

## 12. Changelog & Versioning

**Tujuan**: Melacak semua perubahan versi secara terstruktur.

**Format**: Gunakan [Keep a Changelog](https://keepachangelog.com) + [Semantic Versioning](https://semver.org)

**Semantic Versioning**: `MAJOR.MINOR.PATCH`
- **MAJOR**: Perubahan breaking (tidak backward compatible)
- **MINOR**: Fitur baru (backward compatible)
- **PATCH**: Bug fix (backward compatible)

**Template**:
```markdown
# Changelog

Semua perubahan signifikan pada proyek ini didokumentasikan di sini.

## [Unreleased]
### Added
- [Fitur baru yang belum di-release]

## [1.2.0] - 2024-03-15
### Added
- Fitur export data ke CSV
- Dark mode

### Changed
- Tampilan dashboard di-redesign

### Fixed
- Bug: filter tanggal tidak berfungsi di Safari

## [1.1.0] - 2024-02-01
### Added
- Integrasi payment gateway Midtrans
- Notifikasi email otomatis

### Deprecated
- API v1 akan dihapus di v2.0.0

## [1.0.0] - 2024-01-01
### Added
- Initial release
- Fitur autentikasi
- Dashboard utama
- Manajemen produk
```
