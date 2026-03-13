# API Documentation Templates

Template siap pakai untuk berbagai pola dan method API yang umum digunakan.

---

## Template: REST API Overview Section

```markdown
# API Reference

## Base URL
| Environment | URL |
|-------------|-----|
| Production | `https://api.example.com/v1` |
| Staging | `https://api-staging.example.com/v1` |
| Local | `http://localhost:3000/api/v1` |

## Authentication
Semua endpoint (kecuali yang ditandai `public`) membutuhkan Bearer Token.

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Format Response
### Sukses
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Error
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Pesan error yang readable",
    "details": []
  }
}
```

## HTTP Status Codes
| Code | Arti |
|------|------|
| 200 | OK — Request berhasil |
| 201 | Created — Resource berhasil dibuat |
| 400 | Bad Request — Validasi gagal |
| 401 | Unauthorized — Tidak terautentikasi |
| 403 | Forbidden — Tidak punya izin |
| 404 | Not Found — Resource tidak ditemukan |
| 422 | Unprocessable Entity — Data tidak valid |
| 429 | Too Many Requests — Rate limit exceeded |
| 500 | Internal Server Error — Error server |

## Rate Limiting
- 100 request per 15 menit per IP (endpoint publik)
- 1000 request per 15 menit per user (endpoint authenticated)
- Header: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Pagination
```http
GET /users?page=2&per_page=20
```

## Versioning
API menggunakan versioning di URL path: `/v1/`, `/v2/`
```

---

## Template: GET List Endpoint

```markdown
### GET /resource

Mendapatkan daftar [resource] dengan pagination dan filter.

**Authentication**: Required

**Query Parameters**
| Parameter | Type | Required | Default | Deskripsi |
|-----------|------|----------|---------|-----------|
| page | integer | ❌ | 1 | Nomor halaman |
| per_page | integer | ❌ | 20 | Item per halaman (max: 100) |
| search | string | ❌ | - | Cari berdasarkan nama |
| status | string | ❌ | - | Filter: `active`, `inactive` |
| sort_by | string | ❌ | created_at | Field untuk sorting |
| sort_order | string | ❌ | desc | `asc` atau `desc` |

**Contoh Request**
```http
GET /api/v1/users?page=1&per_page=10&status=active
Authorization: Bearer {token}
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": [
    {
      "id": "usr_123abc",
      "name": "Budi Santoso",
      "email": "budi@example.com",
      "status": "active",
      "created_at": "2024-01-15T08:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 85,
    "total_pages": 9
  }
}
```
```

---

## Template: GET Single Endpoint

```markdown
### GET /resource/:id

Mendapatkan detail [resource] berdasarkan ID.

**Authentication**: Required

**Path Parameters**
| Parameter | Type | Required | Deskripsi |
|-----------|------|----------|-----------|
| id | string | ✅ | ID unik resource |

**Contoh Request**
```http
GET /api/v1/users/usr_123abc
Authorization: Bearer {token}
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "id": "usr_123abc",
    "name": "Budi Santoso",
    "email": "budi@example.com",
    "role": "user",
    "profile": {
      "avatar": "https://cdn.example.com/avatars/123.jpg",
      "phone": "+62812345678"
    },
    "created_at": "2024-01-15T08:30:00Z",
    "updated_at": "2024-02-20T14:00:00Z"
  }
}
```

**Response 404 Not Found**
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User dengan ID tersebut tidak ditemukan"
  }
}
```
```

---

## Template: POST Create Endpoint

```markdown
### POST /resource

Membuat [resource] baru.

**Authentication**: Required

**Request Headers**
| Header | Value | Required |
|--------|-------|----------|
| Content-Type | application/json | ✅ |
| Authorization | Bearer {token} | ✅ |

**Request Body**
| Field | Type | Required | Validasi | Deskripsi |
|-------|------|----------|---------|-----------|
| name | string | ✅ | min: 2, max: 100 | Nama lengkap |
| email | string | ✅ | format email, unique | Email address |
| password | string | ✅ | min: 8, ada angka & huruf | Password |
| role | string | ❌ | enum: user, admin | Role (default: user) |

**Contoh Request**
```http
POST /api/v1/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Siti Rahayu",
  "email": "siti@example.com",
  "password": "SecurePass123",
  "role": "user"
}
```

**Response 201 Created**
```json
{
  "status": "success",
  "data": {
    "id": "usr_456def",
    "name": "Siti Rahayu",
    "email": "siti@example.com",
    "role": "user",
    "created_at": "2024-03-01T09:00:00Z"
  }
}
```

**Response 400 Bad Request**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Data tidak valid",
    "details": [
      { "field": "email", "message": "Email sudah digunakan" },
      { "field": "password", "message": "Password minimal 8 karakter" }
    ]
  }
}
```
```

---

## Template: PUT/PATCH Update Endpoint

```markdown
### PATCH /resource/:id

Memperbarui sebagian data [resource].

> **Note**: Gunakan `PATCH` untuk update parsial, `PUT` untuk replace penuh.

**Authentication**: Required

**Path Parameters**
| Parameter | Type | Deskripsi |
|-----------|------|-----------|
| id | string | ID resource yang akan diupdate |

**Request Body** *(semua field opsional)*
| Field | Type | Validasi | Deskripsi |
|-------|------|---------|-----------|
| name | string | min: 2, max: 100 | Nama baru |
| phone | string | format: +62xxx | Nomor telepon |

**Contoh Request**
```http
PATCH /api/v1/users/usr_123abc
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Budi S. Updated",
  "phone": "+628987654321"
}
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "id": "usr_123abc",
    "name": "Budi S. Updated",
    "phone": "+628987654321",
    "updated_at": "2024-03-10T11:30:00Z"
  }
}
```
```

---

## Template: DELETE Endpoint

```markdown
### DELETE /resource/:id

Menghapus [resource] berdasarkan ID.

**Authentication**: Required
**Authorization**: Admin only

**Path Parameters**
| Parameter | Type | Deskripsi |
|-----------|------|-----------|
| id | string | ID resource yang akan dihapus |

**Contoh Request**
```http
DELETE /api/v1/users/usr_123abc
Authorization: Bearer {token}
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "message": "User berhasil dihapus"
  }
}
```

**Response 403 Forbidden**
```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_PERMISSION",
    "message": "Hanya admin yang dapat menghapus user"
  }
}
```
```

---

## Template: Authentication Endpoints

```markdown
### POST /auth/login

Login dan dapatkan access token.

**Authentication**: Not Required (Public)

**Request Body**
| Field | Type | Required | Deskripsi |
|-------|------|----------|-----------|
| email | string | ✅ | Email terdaftar |
| password | string | ✅ | Password |

**Contoh Request**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "budi@example.com",
  "password": "SecurePass123"
}
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900,
    "token_type": "Bearer",
    "user": {
      "id": "usr_123abc",
      "name": "Budi Santoso",
      "email": "budi@example.com",
      "role": "user"
    }
  }
}
```

**Response 401 Unauthorized**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email atau password salah"
  }
}
```

---

### POST /auth/refresh

Refresh access token menggunakan refresh token.

**Request Body**
| Field | Type | Required | Deskripsi |
|-------|------|----------|-----------|
| refresh_token | string | ✅ | Refresh token yang valid |

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900
  }
}
```

---

### POST /auth/logout

Invalidate token dan logout.

**Authentication**: Required

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "message": "Berhasil logout"
  }
}
```
```

---

## Template: File Upload Endpoint

```markdown
### POST /resource/upload

Upload file untuk [resource].

**Authentication**: Required

**Request Headers**
| Header | Value |
|--------|-------|
| Content-Type | multipart/form-data |
| Authorization | Bearer {token} |

**Form Data**
| Field | Type | Required | Batasan | Deskripsi |
|-------|------|----------|---------|-----------|
| file | file | ✅ | Max 5MB, jpg/png/pdf | File yang diupload |
| type | string | ✅ | avatar, document | Tipe file |

**Contoh Request**
```http
POST /api/v1/users/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file=[binary data]
type=avatar
```

**Response 200 OK**
```json
{
  "status": "success",
  "data": {
    "url": "https://cdn.example.com/uploads/abc123.jpg",
    "filename": "avatar.jpg",
    "size": 102400,
    "mime_type": "image/jpeg"
  }
}
```
```

---

## Template: Webhook Documentation

```markdown
## Webhooks

Aplikasi mengirim webhook ke URL yang dikonfigurasi ketika event tertentu terjadi.

### Setup Webhook
1. Masuk ke Settings → Integrations → Webhooks
2. Klik "Add Webhook"
3. Masukkan URL endpoint Anda
4. Pilih events yang ingin didengarkan
5. Simpan dan catat Secret Key

### Verifikasi Signature
Setiap request webhook menyertakan header `X-Webhook-Signature` untuk verifikasi:

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = hmac.update(JSON.stringify(payload)).digest('hex');
  return `sha256=${digest}` === signature;
}
```

### Events yang Tersedia
| Event | Trigger | Payload |
|-------|---------|---------|
| user.created | User baru mendaftar | User object |
| order.paid | Pembayaran sukses | Order + Payment object |
| order.cancelled | Order dibatalkan | Order object |

### Contoh Payload
```json
{
  "event": "order.paid",
  "timestamp": "2024-03-01T09:00:00Z",
  "data": {
    "order_id": "ord_789",
    "amount": 150000,
    "status": "paid"
  }
}
```
```
