# 🔥 MoCal — AI-Powered Calorie Tracker

**MoCal** (Monitoring Calorie) is a full-stack web application that estimates calories and macronutrients from free-text food descriptions in **Bahasa Indonesia**. Simply type what you ate in natural language — like *"makan nasi goreng sama es teh manis"* — and MoCal will break it down into individual food items, match each one to a nutrition database, and give you a complete calorie and macro summary.

## ✨ Key Features

- **Natural Language Input** — Describe your meals in everyday Bahasa Indonesia. No need to search a food database manually.
- **LLM-Powered Parsing** — Uses Groq's Llama 3.1 to intelligently extract food items, quantities, and portion sizes from any text input.
- **Multi-Layer Food Matching** — A 4-step nutrition lookup pipeline:
  1. **Exact match** against a local database of Indonesian foods (TKPI-based)
  2. **Fuzzy match** using RapidFuzz for approximate name matching
  3. **USDA API** fallback for international foods
  4. **LLM estimation** as a last resort when no database match is found
- **Macro Tracking** — Tracks calories (kcal), protein, carbohydrates, and fat for every meal.
- **Personalized Goals** — Onboarding flow that calculates your BMR, TDEE, and daily macro targets based on age, weight, height, activity level, and goal (lose / maintain / gain).
- **Daily Log & History** — View and manage your food logs by date, with the ability to delete entries.
- **User Authentication** — Secure JWT-based registration and login system.

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + Vite |
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL (Supabase) |
| **LLM Provider** | Groq (Llama 3.1 8B Instant) |
| **Food Data** | Local Indonesian food DB + USDA FoodData Central API |
| **Matching Engine** | RapidFuzz (fuzzy string matching) |
| **Deployment** | Vercel |

## 📱 How It Works

1. **You type what you ate** — e.g., *"sarapan roti bakar 2 lembar, telur ceplok, dan segelas susu"*
2. **MoCal parses your text** — The LLM identifies each food item with its quantity and unit
3. **Nutrition is matched** — Each item is looked up through the multi-layer matching pipeline
4. **You get a full breakdown** — Calories, protein, carbs, and fat per item and totals
5. **Your meal is logged** — Saved to your account for daily tracking against your goals

## 📄 License

This project was built as part of a thesis (Skripsi) at Universitas Gunadarma.
