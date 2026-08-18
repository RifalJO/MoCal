# app/database.py
# Koneksi PostgreSQL + definisi tabel menggunakan SQLAlchemy

from sqlalchemy import create_engine, Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import func
from pydantic_settings import BaseSettings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import uuid


# ─── Settings ─────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str | None = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "calorie_tracker"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    GROQ_API_KEY: str = ""
    # Model Groq. llama-3.1-8b-instant dimatikan Groq pada 16 Agustus 2026;
    # bisa ditimpa lewat env var GROQ_MODEL tanpa mengubah kode.
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    # Model reasoning (gpt-oss-*) memakai completion token untuk "berpikir".
    # "low" menekan token tanpa menurunkan kualitas ekstraksi. Kosongkan
    # ("") bila memakai model non-reasoning yang menolak parameter ini.
    GROQ_REASONING_EFFORT: str = "low"
    USDA_API_KEY: str = ""
    SECRET_KEY: str = ""  # WAJIB diisi lewat environment variable
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FUZZY_THRESHOLD: int = 80

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()


def groq_extra_kwargs() -> dict:
    """Parameter tambahan untuk setiap pemanggilan Groq.

    Dipisah agar konfigurasi reasoning_effort cukup diatur di satu tempat
    dan otomatis hilang bila diganti model non-reasoning.
    """
    effort = (settings.GROQ_REASONING_EFFORT or "").strip()
    return {"reasoning_effort": effort} if effort else {}

# Di produksi, kunci penandatangan JWT wajib berasal dari environment variable.
# Gagal keras di sini lebih aman daripada diam-diam menandatangani token dengan
# kunci kosong. Di lingkungan pengembangan lokal, kunci kosong dibiarkan.
if settings.APP_ENV == "production" and not settings.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY belum diset. Tambahkan sebagai environment variable "
        "sebelum menjalankan aplikasi di lingkungan produksi."
    )

# ─── Engine ───────────────────────────────────────────────────────────────────
def _clean_database_url(url: str) -> str:
    """Clean database URL for psycopg2 compatibility."""
    # Fix for Supabase/SQLAlchemy: postgres:// -> postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Strip ?pgbouncer=true — psycopg2 doesn't recognize it
    if "pgbouncer" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs.pop("pgbouncer", None)
        clean_query = urlencode(qs, doseq=True)
        url = urlunparse(parsed._replace(query=clean_query))
    return url

if settings.DATABASE_URL:
    DATABASE_URL = _clean_database_url(settings.DATABASE_URL)
else:
    DATABASE_URL = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

# Use NullPool for serverless (Vercel) to avoid stale connections
_is_serverless = settings.APP_ENV == "production"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool if _is_serverless else None,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────
class Food(Base):
    __tablename__ = "foods"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(255), nullable=False, index=True)
    name_aliases    = Column(Text, nullable=True)       # dipisah tanda |
    cal             = Column(Float, nullable=True)       # kalori per 100g
    protein         = Column(Float, default=0.0)
    carbs           = Column(Float, default=0.0)
    fat             = Column(Float, default=0.0)
    default_portion_g = Column(Float, default=100.0)
    source          = Column(String(50), nullable=False) # indo_nutrition/dapur_umami/daily_nutrition/usda
    is_indonesian   = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    password_hash   = Column(String(255), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    name             = Column(String(100), nullable=False)
    age              = Column(Float, nullable=False) # Changed to Float or Integer (Integer needs import)
    gender           = Column(String(10), nullable=False)
    weight_kg        = Column(Float, nullable=False)
    height_cm        = Column(Float, nullable=False)

    activity_level   = Column(String(20), nullable=False)
    goal             = Column(String(20), nullable=False)

    bmr              = Column(Float)
    tdee             = Column(Float)
    daily_kcal_target= Column(Float)
    protein_target_g = Column(Float)
    carbs_target_g   = Column(Float)
    fat_target_g     = Column(Float)

    onboarding_completed = Column(Boolean, default=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FoodLog(Base):
    __tablename__ = "food_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    raw_input   = Column(Text, nullable=False)
    items       = Column(JSONB, nullable=False)
    total_kcal  = Column(Float, nullable=False)
    log_detail  = Column(JSONB, nullable=True)        # detail lengkap proses parsing & matching
    logged_at   = Column(DateTime(timezone=True), server_default=func.now())


# ─── Dependency ───────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Buat semua tabel jika belum ada (skip di production — tabel sudah ada)"""
    if settings.APP_ENV == "production":
        print("[SKIP] Production mode - skip create_all (tabel sudah ada di Supabase)")
        return
    Base.metadata.create_all(bind=engine)
    print("[OK] Tabel berhasil dibuat")
