# MoCal Login & Macro Tracking Setup

## Changes Made

### 1. ✅ Macro Breakdown Now Connected to Real Data

**Problem:** Macro breakdown (Carbs, Protein, Fat) was showing 0 even after adding food.

**Solution:** Updated calculation to use `items` data from API response instead of empty fields.

**Files Modified:**
- `frontend/src/stores/appStore.js` - Updated getters to calculate from `items.carbs_g`, `items.protein_g`, `items.fat_g`
- `frontend/src/pages/MainApp.jsx` - Updated desktop summary to use items data
- `frontend/src/services/api.js` - Already saving items data correctly

**How it works now:**
```javascript
// Before (wrong):
totalC = log.total_carbs || 0  // This was undefined from API

// After (correct):
totalC = log.items.reduce((sum, item) => sum + item.carbs_g, 0)  // Uses actual item data
```

---

### 2. ✅ Login/Register System (Embedded in Settings)

**Features:**
- Login/Register modal embedded in Settings (no separate page)
- Persistent login (stored in localStorage)
- Auto-fetch user's food logs on login
- User profile display in Settings

**Files Modified:**
- `frontend/src/stores/appStore.js` - Added auth state (user, token, isAuthenticated)
- `frontend/src/components/SettingsModal.jsx` - Added login/register UI
- `frontend/src/services/api.js` - Added login, register, logout, fetchUserLogs functions

**API Endpoints Used:**
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `GET /api/auth/me` - Get current user
- `GET /api/logs/all` - Fetch user's food logs

---

## How to Use Login Feature

### Via UI:
1. Open Settings (click gear icon)
2. Click "Login / Register" button
3. Enter email and password
4. Click Login (or Register if new user)
5. After login, your food logs will be saved to your account

### Test Account (via SQL):
```sql
-- Run this in your PostgreSQL database
-- Email: test@mocal.app
-- Password: test123

INSERT INTO users (id, email, password_hash, created_at)
VALUES (
    gen_random_uuid(),
    'test@mocal.app',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
    NOW()
) ON CONFLICT (email) DO NOTHING;
```

Or run the script:
```bash
psql -U postgres -d calorie_tracker -f scripts/add_test_user.sql
```

---

## Data Flow

### Without Login (Guest):
```
User inputs food → API estimates → Saved to food_logs (user_id = NULL) → Displayed in UI
Data stored in: localStorage (temporary, cleared daily)
```

### With Login (Authenticated):
```
User logs in → Fetch existing logs from DB → User inputs food → API estimates → 
Saved to food_logs (with user_id) → Displayed in UI
Data stored in: PostgreSQL database (persistent) + localStorage (cache)
```

---

## Testing

### Test Macro Breakdown:
1. Open the app
2. Input food: "nasi padang dengan tunjang"
3. Check Bottom Bar - should show C, P, F values
4. Click Bottom Bar to open Goals panel
5. Check ring charts - should show Carbs, Protein, Fat values

### Test Login:
1. Open Settings (gear icon)
2. Click "Login / Register"
3. Register with email: `test@example.com`, password: `test123`
4. After registration, login with same credentials
5. Check if user email appears in Settings
6. Input food - should be saved to database

### Test Persistent Data:
1. Login with your account
2. Add some food logs
3. Refresh the page
4. Login again
5. Your food logs should be fetched from database

---

## API Response Structure

### POST /api/estimate Response:
```json
{
  "total_kcal": 647.2,
  "total_protein_g": 15.3,
  "total_carbs_g": 89.7,
  "total_fat_g": 23.1,
  "items": [
    {
      "name_raw": "nasi padang",
      "name_matched": "nasi padang",
      "gram": 250.0,
      "kcal": 633.3,
      "protein_g": 10.8,
      "carbs_g": 29.3,
      "fat_g": 7.8,
      ...
    },
    {
      "name_raw": "tunjang",
      "gram": 100.0,
      "kcal": 13.9,
      "protein_g": 4.5,
      "carbs_g": 0.4,
      "fat_g": 0.1,
      ...
    }
  ]
}
```

**Note:** The `items` array contains the detailed macro data for each food item. This is what we now use to calculate total Carbs, Protein, and Fat.

---

## Troubleshooting

### Macros Still Showing 0:
1. Check browser console for errors
2. Verify API response has `items` array with `carbs_g`, `protein_g`, `fat_g` fields
3. Clear localStorage and refresh

### Login Not Working:
1. Check backend is running (`uvicorn app.main:app --reload`)
2. Verify database has `users` table
3. Check browser console for API errors
4. Ensure token is being saved in localStorage

### Logs Not Fetching:
1. Verify user is logged in (check Settings)
2. Check `/api/logs/all` endpoint returns data
3. Verify token is included in API requests

---

## Next Steps (Optional Improvements)

1. **Per-User Logs:** Update `/api/logs` endpoint to filter by `user_id`
2. **Password Reset:** Add forgot password functionality
3. **Email Verification:** Verify email on registration
4. **Social Login:** Add Google/Facebook login
5. **Multi-Day Tracking:** Show logs from previous days
6. **Export Data:** Allow users to export their food log history

---

## Files Changed Summary

| File | Changes |
|------|---------|
| `appStore.js` | Added auth state, updated macro calculation |
| `SettingsModal.jsx` | Added login/register UI |
| `api.js` | Added auth functions (login, register, logout, fetchUserLogs) |
| `MainApp.jsx` | Added useEffect to fetch logs on auth |
| `scripts/add_test_user.sql` | SQL script to add test user |

---

## Quick Test Commands

```bash
# Start backend
cd c:\Users\kinga\OneDrive\Dokumen\Gunadarma\Semester 8\Skripsi\TrackCalorieByType\MoCal
uvicorn app.main:app --reload

# Start frontend (new terminal)
cd c:\Users\kinga\OneDrive\Dokumen\Gunadarma\Semester 8\Skripsi\TrackCalorieByType\MoCal\frontend
npm run dev

# Add test user
psql -U postgres -d calorie_tracker -f scripts/add_test_user.sql

# View latest log with details
http://localhost:8000/api/logs/latest
```
