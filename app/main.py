# app/main.py
# FastAPI — entry point utama backend calorie tracker

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db, init_db, settings
from app.matcher import find_food, load_food_cache
from app.parser import parse_food_text, estimate_nutrition_llm, convert_to_gram
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import get_db, init_db, settings, User, UserProfile
import uuid


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Calorie Tracker API",
    description="Estimasi kalori makanan dari input teks bebas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ganti dengan domain frontend saat production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_db()
    db = next(get_db())
    load_food_cache(db)
    print("🚀 Server siap!")


# ─── Schemas ──────────────────────────────────────────────────────────────────
class LogRequest(BaseModel):
    text: str                   # teks bebas dari user

class FoodItemResult(BaseModel):
    name_raw:     str           # nama asli dari input user
    name_matched: str           # nama makanan yang ditemukan di DB
    qty:          float
    unit:         str
    gram:         float
    kcal:         float | None
    protein_g:    float
    carbs_g:      float
    fat_g:        float
    match_method: str           # exact / fuzzy / api / llm_estimate / not_found
    match_score:  float
    source:       str
    is_estimate:  bool          # True jika dari LLM estimasi

class LogResponse(BaseModel):
    log_id:      str
    raw_input:   str
    items:       list[FoodItemResult]
    total_kcal:  float
    total_protein_g: float
    total_carbs_g:   float
    total_fat_g:     float
    unknown_items:   list[str]  # makanan yang tidak ditemukan sama sekali

class UserAuth(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class OnboardingRequest(BaseModel):
    name: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    activity_level: str
    goal: str

class OnboardingResponse(BaseModel):
    bmr: float
    tdee: float
    daily_kcal_target: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    onboarding_completed: bool

# ─── Auth Endpoints ───────────────────────────────────────────────────────────
@app.post("/api/auth/register")
def register(user_data: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserAuth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "onboarding_completed": profile.onboarding_completed if profile else False
    }

# ─── BMR calculation logic duplicate from bmr.js ──────────────────────────────
def calculate_bmr_macros(data: OnboardingRequest):
    if data.gender == 'male':
        bmr = 10 * data.weight_kg + 6.25 * data.height_cm - 5 * data.age + 5
    else:
        bmr = 10 * data.weight_kg + 6.25 * data.height_cm - 5 * data.age - 161
        
    activity_multiplier = {
        'sedentary': 1.2,
        'light':     1.375,
        'moderate':  1.55,
        'active':    1.725,
    }
    
    goal_adjustment = {
        'lose':     -500,
        'maintain': 0,
        'gain':     +300,
    }
    
    tdee = bmr * activity_multiplier.get(data.activity_level, 1.2)
    daily_kcal_target = tdee + goal_adjustment.get(data.goal, 0)
    
    protein_g = round((daily_kcal_target * 0.30) / 4, 2)
    carbs_g = round((daily_kcal_target * 0.50) / 4, 2)
    fat_g = round((daily_kcal_target * 0.20) / 9, 2)
    
    return {
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "daily_kcal_target": round(daily_kcal_target, 2),
        "protein_target_g": protein_g,
        "carbs_target_g": carbs_g,
        "fat_target_g": fat_g
    }

# ─── Onboarding Endpoints ─────────────────────────────────────────────────────
@app.post("/api/onboarding", response_model=OnboardingResponse)
def create_onboarding(data: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")
        
    calc = calculate_bmr_macros(data)
    
    new_profile = UserProfile(
        user_id=current_user.id,
        name=data.name,
        age=data.age,
        gender=data.gender,
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        activity_level=data.activity_level,
        goal=data.goal,
        onboarding_completed=True,
        **calc
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return calc | {"onboarding_completed": True}

@app.get("/api/onboarding")
def get_onboarding(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/api/onboarding", response_model=OnboardingResponse)
def update_onboarding(data: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    calc = calculate_bmr_macros(data)
    
    profile.name = data.name
    profile.age = data.age
    profile.gender = data.gender
    profile.weight_kg = data.weight_kg
    profile.height_cm = data.height_cm
    profile.activity_level = data.activity_level
    profile.goal = data.goal
    profile.bmr = calc['bmr']
    profile.tdee = calc['tdee']
    profile.daily_kcal_target = calc['daily_kcal_target']
    profile.protein_target_g = calc['protein_target_g']
    profile.carbs_target_g = calc['carbs_target_g']
    profile.fat_target_g = calc['fat_target_g']
    profile.onboarding_completed = True
    
    db.commit()
    
    return calc | {"onboarding_completed": True}
        


# ─── Endpoint: Health check ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Calorie Tracker API is running"}


# ─── Endpoint: Estimate kalori ────────────────────────────────────────────────
@app.post("/api/estimate", response_model=LogResponse)
def estimate_calories(req: LogRequest, db: Session = Depends(get_db)):
    """
    Endpoint utama:
    1. Parse teks bebas → daftar makanan (LLM)
    2. Cari nutrisi tiap makanan (DB lokal → USDA API → LLM estimasi)
    3. Hitung total kalori
    4. Return hasil lengkap
    """

    # Validasi input
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input teks tidak boleh kosong")
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Input terlalu panjang (max 2000 karakter)")

    # ── Step 1: Parse teks → daftar makanan ───────────────────────────────────
    parsed_items = parse_food_text(text)

    if not parsed_items:
        raise HTTPException(status_code=422, detail="Tidak ada makanan yang terdeteksi dari teks")

    # ── Step 2: Cari nutrisi tiap makanan ─────────────────────────────────────
    results      = []
    unknown_items = []

    for item in parsed_items:
        name_raw  = item.get("name", "").strip()
        name_en   = item.get("name_en", None)
        qty       = float(item.get("qty", 1))
        unit      = item.get("unit", "porsi")

        if not name_raw:
            continue

        # Cari di DB lokal + USDA API
        food = find_food(name_raw, name_en)

        # Fallback LLM estimasi jika benar-benar tidak ketemu
        is_estimate = False
        if food["match_method"] == "not_found":
            llm_result = estimate_nutrition_llm(name_raw)
            if llm_result:
                food = {**food, **llm_result}
                is_estimate = True
            else:
                unknown_items.append(name_raw)

        # Konversi porsi ke gram
        gram = convert_to_gram(qty, unit, food.get("default_portion_g", 100.0))

        # Hitung kalori berdasarkan gram (pakai field 'kcal' yang sudah di-map dari 'cal')
        kcal_100g = food.get("kcal")
        kcal      = round((gram / 100) * kcal_100g, 1) if kcal_100g else None
        protein   = round((gram / 100) * (food.get("protein_g") or 0), 1)
        carbs     = round((gram / 100) * (food.get("carbs_g") or 0), 1)
        fat       = round((gram / 100) * (food.get("fat_g") or 0), 1)

        results.append(FoodItemResult(
            name_raw     = name_raw,
            name_matched = food.get("name", name_raw),
            qty          = qty,
            unit         = unit,
            gram         = round(gram, 1),
            kcal         = kcal,
            protein_g    = protein,
            carbs_g      = carbs,
            fat_g        = fat,
            match_method = food.get("match_method", "not_found"),
            match_score  = food.get("match_score", 0.0),
            source       = food.get("source", "unknown"),
            is_estimate  = is_estimate,
        ))

    # ── Step 3: Hitung total ───────────────────────────────────────────────────
    total_kcal    = round(sum(r.kcal    or 0 for r in results), 1)
    total_protein = round(sum(r.protein_g   for r in results), 1)
    total_carbs   = round(sum(r.carbs_g     for r in results), 1)
    total_fat     = round(sum(r.fat_g       for r in results), 1)

    # ── Step 4: Simpan log ke DB ──────────────────────────────────────────────
    from app.database import FoodLog
    log = FoodLog(
        user_id    = None,
        raw_input  = text,
        items      = [r.model_dump() for r in results],
        total_kcal = total_kcal,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return LogResponse(
        log_id          = str(log.id),
        raw_input       = text,
        items           = results,
        total_kcal      = total_kcal,
        total_protein_g = total_protein,
        total_carbs_g   = total_carbs,
        total_fat_g     = total_fat,
        unknown_items   = unknown_items,
    )


# ─── Endpoint: Cari makanan manual ───────────────────────────────────────────
@app.get("/api/foods/search")
def search_food(q: str, db: Session = Depends(get_db)):
    """Search makanan di database lokal — untuk keperluan testing"""
    from app.matcher import fuzzy_match, exact_match
    result = exact_match(q) or fuzzy_match(q)
    if not result:
        raise HTTPException(status_code=404, detail=f"Makanan '{q}' tidak ditemukan")
    return result


# ─── Endpoint: Get Logs ──────────────────────────────────────────────────────
@app.get("/api/logs")
def get_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.database import FoodLog
    # Ambil logs hari ini
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Ambil semua log user ini desc
    logs = db.query(FoodLog).filter(FoodLog.user_id == current_user.id).order_by(FoodLog.logged_at.desc()).all()
    
    # Convert ke response schema
    result = []
    for log in logs:
        result.append({
            "log_id": str(log.id),
            "raw_input": log.raw_input,
            "items": log.items,
            "total_kcal": log.total_kcal,
            "logged_at": log.logged_at.isoformat() if log.logged_at else None
        })
    return result


# ─── Endpoint: Stats DB ───────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Info jumlah data di database — untuk verifikasi"""
    from app.database import Food, FoodLog
    return {
        "total_foods":    db.query(Food).count(),
        "total_indonesian": db.query(Food).filter(Food.is_indonesian == True).count(),
        "total_logs":     db.query(FoodLog).count(),
    }


# ─── Endpoint: Test USDA API ──────────────────────────────────────────────────
@app.get("/api/test/usda")
def test_usda_api(q: str = "apple"):
    """
    Test apakah USDA API Key valid dan bisa digunakan.
    Contoh: /api/test/usda?q=rice
    """
    from app.database import settings
    import requests

    if not settings.USDA_API_KEY:
        return {
            "status": "error",
            "message": "USDA_API_KEY belum diset di file .env",
            "api_key_present": False,
        }

    try:
        res = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "api_key":  settings.USDA_API_KEY,
                "query":    q,
                "pageSize": 3,
                "dataType": "SR Legacy,Foundation"
            },
            timeout=10
        )

        if res.status_code == 403:
            return {
                "status": "error",
                "message": "API Key ditolak (403 Forbidden). Periksa kembali nilai USDA_API_KEY di file .env",
                "api_key_present": True,
                "http_status": 403,
            }
        
        if res.status_code != 200:
            return {
                "status": "error",
                "message": f"USDA API merespons dengan status {res.status_code}",
                "api_key_present": True,
                "http_status": res.status_code,
            }

        data = res.json()
        foods = data.get("foods", [])

        if not foods:
            return {
                "status": "ok",
                "message": f"API berjalan normal, tapi tidak ada hasil untuk query '{q}'",
                "api_key_present": True,
                "total_hits": data.get("totalHits", 0),
                "results": []
            }

        # Ambil ringkasan hasil
        results = []
        for food in foods:
            nutr = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}
            results.append({
                "fdcId":       food.get("fdcId"),
                "description": food.get("description"),
                "dataType":    food.get("dataType"),
                "energy_kcal": nutr.get("Energy"),
                "protein_g":   nutr.get("Protein"),
                "carbs_g":     nutr.get("Carbohydrate, by difference"),
                "fat_g":       nutr.get("Total lipid (fat)"),
            })

        return {
            "status": "ok",
            "message": f"USDA API bekerja! Ditemukan {data.get('totalHits', 0)} hasil untuk '{q}'",
            "api_key_present": True,
            "total_hits": data.get("totalHits", 0),
            "showing": len(results),
            "results": results
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Koneksi ke USDA API timeout (>10 detik). Cek koneksi internet.",
            "api_key_present": True,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error tidak terduga: {str(e)}",
            "api_key_present": True,
        }

