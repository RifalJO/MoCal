# app/database.py
# Koneksi PostgreSQL + definisi tabel menggunakan SQLAlchemy

from sqlalchemy import create_engine, Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from pydantic_settings import BaseSettings
import uuid


# ─── Settings ─────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    APP_ENV: str = "development"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "calorie_tracker"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    GROQ_API_KEY: str = ""
    USDA_API_KEY: str = ""
    SECRET_KEY: str = "super_secret_key_mocal_123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FUZZY_THRESHOLD: int = 80

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# ─── Engine ───────────────────────────────────────────────────────────────────
DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False)
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
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # made nullable=True initially to allow dropping/recreating or altering existing db easier, but ideally user_id is required
    raw_input   = Column(Text, nullable=False)          # teks asli user
    items       = Column(JSONB, nullable=False)          # detail tiap makanan
    total_kcal  = Column(Float, nullable=False)
    logged_at   = Column(DateTime(timezone=True), server_default=func.now())


# ─── Dependency ───────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Buat semua tabel jika belum ada"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel berhasil dibuat")
