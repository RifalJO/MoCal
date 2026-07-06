import axios from 'axios'
import { useAppStore } from '@/stores/appStore'

// Use relative path for production (works with Vercel routing), fallback for local dev
const API_URL = import.meta.env.VITE_API_URL || ""

const api = axios.create({ baseURL: API_URL })

// Offset zona waktu klien dalam menit di timur UTC (WIB = 420).
// Dipakai backend untuk menghitung batas hari lokal karena logged_at disimpan dalam UTC.
const tzOffsetMinutes = () => -new Date().getTimezoneOffset()

// Add token to requests if available
api.interceptors.request.use(config => {
    const store = useAppStore.getState()
    if (store.token) {
        config.headers.Authorization = `Bearer ${store.token}`
    }
    return config
})

// Auth functions
export async function login(email, password) {
    try {
        const { data } = await api.post('/api/auth/login', { email, password })
        const store = useAppStore.getState()
        store.setToken(data.access_token)
        store.setUser({ email })
        localStorage.setItem('mocal-token', data.access_token)
        localStorage.setItem('mocal-user', JSON.stringify({ email }))

        // Clear local logs and fetch user's logs from server
        store.setLogs([])
        await fetchUserLogs()

        // Restore onboarding/profile data from server
        await fetchOnboarding()

        return { success: true }
    } catch (error) {
        console.error('Login error:', error)
        throw new Error(error.response?.data?.detail || 'Login failed')
    }
}

export async function register(email, password) {
    try {
        const { data } = await api.post('/api/auth/register', { email, password })
        return { success: true, message: data.message }
    } catch (error) {
        console.error('Register error:', error)
        throw new Error(error.response?.data?.detail || 'Registration failed')
    }
}

export async function logout() {
    const store = useAppStore.getState()
    // Clear local logs on logout
    store.setLogs([])
    store.logout()
}

// Validate and restore auth session
export async function validateAuth() {
    const store = useAppStore.getState()
    const token = localStorage.getItem('mocal-token')
    const userStr = localStorage.getItem('mocal-user')

    // If no token, not authenticated
    if (!token || !userStr) {
        console.log('ℹ️ No token found in localStorage')
        return { authenticated: false }
    }

    try {
        // Set token in store for API calls
        store.setToken(token)
        store.setUser(JSON.parse(userStr))
        store.setIsAuthenticated(true)

        // Verify token is still valid
        const { data } = await api.get('/api/auth/me')

        // Token valid, restore session
        store.setUser(data)
        store.setIsAuthenticated(true)

        // Restore onboarding/profile data from server
        await fetchOnboarding()

        console.log('✅ Auth session restored successfully')
        return { authenticated: true, user: data }
    } catch (error) {
        console.log('❌ Auth validation failed - token expired or invalid')
        // Token invalid/expired — bersihkan seluruh sesi termasuk profile/goals,
        // supaya data onboarding akun lama tidak bocor ke akun yang login berikutnya
        store.logout()
        return { authenticated: false }
    }
}

export async function getCurrentUser() {
    try {
        const { data } = await api.get('/api/auth/me')
        const store = useAppStore.getState()
        store.setUser(data)
        return data
    } catch (error) {
        // Token invalid, clear auth
        logout()
        return null
    }
}

// Delete food log
export async function deleteLog(logId) {
    try {
        // Call backend delete endpoint
        await api.delete(`/api/logs/${logId}`)

        // Remove from local state after successful deletion
        const store = useAppStore.getState()
        const newLogs = store.logs.filter(log => log.log_id !== logId)
        store.setLogs(newLogs)

        return { success: true }
    } catch (error) {
        console.error('Delete log error:', error)
        throw new Error(error.response?.data?.detail || 'Failed to delete entry')
    }
}

// Fetch user logs (authenticated - gets only current user's logs)
export async function fetchUserLogs(date = null) {
    const store = useAppStore.getState()

    // If not authenticated, don't fetch
    if (!store.isAuthenticated || !store.token) {
        console.log('ℹ️ Not authenticated, skipping log fetch')
        return []
    }

    try {
        // Use authenticated endpoint that filters by user_id
        // Optional date parameter (YYYY-MM-DD) to filter by specific date
        const tz = tzOffsetMinutes()
        const url = date ? `/api/logs?date=${date}&tz_offset=${tz}` : `/api/logs?tz_offset=${tz}`
        const { data } = await api.get(url)

        console.log('📥 Fetched user logs:', data.length, 'entries', date ? `for ${date}` : '')

        store.setLogs(data.map(log => ({
            log_id: log.log_id,
            raw_input: log.raw_input,
            total_kcal: log.total_kcal,
            total_carbs: log.total_carbs_g || 0,
            total_protein: log.total_protein_g || 0,
            total_fat: log.total_fat_g || 0,
            total_sugar: 0,
            total_fiber: 0,
            total_sodium: 0,
            items: log.items || [],
            logged_at: log.logged_at,
        })))
        return data
    } catch (error) {
        console.error('Fetch logs error:', error)
        return []
    }
}

// ─── Onboarding sync ─────────────────────────────────────────────────────────

// Fetch onboarding/profile data from server and restore to store
export async function fetchOnboarding() {
    const store = useAppStore.getState()
    if (!store.isAuthenticated || !store.token) return

    try {
        const { data } = await api.get('/api/onboarding')

        // Restore profile to store (field names match SettingsModal form)
        store.setProfile({
            name: data.name || '',
            age: String(data.age || ''),
            gender: data.gender || 'male',
            weight: String(data.weight_kg || ''),
            height: String(data.height_cm || ''),
            activity: data.activity_level || 'light',
            goal: data.goal || 'maintain',
        })

        // Restore calculated goals
        store.setGoals({
            kcal: Math.round(data.daily_kcal_target || 2000),
            carbs: Math.round(data.carbs_target_g || 250),
            protein: Math.round(data.protein_target_g || 150),
            fat: Math.round(data.fat_target_g || 67),
            sugar: 50,
            fiber: 25,
            sodium: 2300,
        })

        store.setHasOnboarding(true)
        console.log('✅ Onboarding data restored from server')
    } catch (error) {
        if (error.response?.status === 404) {
            // No profile on server yet. If goals were set as guest (local only),
            // push them to the server now so onboarding follows the account.
            if (store.hasOnboarding && store.profile) {
                console.log('⬆️ Syncing local onboarding to server...')
                await saveOnboarding(store.profile)
            } else {
                console.log('ℹ️ No onboarding data found on server')
            }
        } else {
            console.error('Fetch onboarding error:', error)
        }
    }
}

// Save onboarding/profile data to server (POST if new, PUT if exists)
export async function saveOnboarding(formData) {
    const store = useAppStore.getState()
    if (!store.isAuthenticated || !store.token) return

    const payload = {
        name: formData.name || '',
        age: parseInt(formData.age) || 0,
        gender: formData.gender || 'male',
        weight_kg: parseFloat(formData.weight) || 0,
        height_cm: parseFloat(formData.height) || 0,
        activity_level: formData.activity || 'light',
        goal: formData.goal || 'maintain',
    }

    try {
        // Try POST first (create new profile)
        await api.post('/api/onboarding', payload)
        console.log('✅ Onboarding saved to server (created)')
    } catch (error) {
        if (error.response?.status === 400) {
            // Profile already exists — update instead
            try {
                await api.put('/api/onboarding', payload)
                console.log('✅ Onboarding saved to server (updated)')
            } catch (putError) {
                console.error('Update onboarding error:', putError)
            }
        } else {
            console.error('Save onboarding error:', error)
        }
    }
}

// Fetch logs for a specific date (Riwayat page) — returns data without mutating global store
export async function fetchLogsByDate(date) {
    const store = useAppStore.getState()

    if (!store.isAuthenticated || !store.token) {
        return []
    }

    try {
        const { data } = await api.get(`/api/logs?date=${date}&tz_offset=${tzOffsetMinutes()}`)
        return data.map(log => ({
            log_id: log.log_id,
            raw_input: log.raw_input,
            total_kcal: log.total_kcal,
            total_carbs: log.total_carbs_g || 0,
            total_protein: log.total_protein_g || 0,
            total_fat: log.total_fat_g || 0,
            items: log.items || [],
            logged_at: log.logged_at,
        }))
    } catch (error) {
        console.error('Fetch logs by date error:', error)
        return []
    }
}

// Submit food log (handles both authenticated and guest trial)
export async function submitLog(text) {
    const store = useAppStore.getState()
    
    // Guest trial flow
    if (!store.isAuthenticated) {
        const trialUsed = localStorage.getItem('mocal-guest-trial') === 'true'
        
        if (trialUsed) {
            // Trial already used — trigger auth warning
            store.setShowAuthWarning(true)
            throw new Error('GUEST_TRIAL_EXCEEDED')
        }
        
        // First try — use guest endpoint
        return await submitGuestLog(text)
    }
    
    // Authenticated flow (original)
    store.setLoading(true)
    try {
        const { data } = await api.post('/api/estimate', { text })

        console.log('📡 API Response:', data)

        store.addLog({
            log_id: data.log_id,
            raw_input: text,
            total_kcal: data.total_kcal || 0,
            total_carbs: data.total_carbs || 0,
            total_protein: data.total_protein || 0,
            total_fat: data.total_fat || 0,
            total_sugar: data.total_sugar || 0,
            total_fiber: data.total_fiber || 0,
            total_sodium: data.total_sodium || 0,
            items: data.items || [],
            logged_at: new Date().toISOString(),
        })
        return { success: true, data }
    } catch (error) {
        console.error('API Error:', error)
        if (error.response?.status === 422) {
            throw new Error('Tidak ada makanan yang terdeteksi. Pastikan Anda memasukkan nama makanan.')
        } else if (error.response?.status === 400) {
            throw new Error(error.response.data.detail || 'Input tidak valid')
        } else {
            throw new Error('Gagal memproses makanan. Coba lagi.')
        }
    } finally {
        store.setLoading(false)
    }
}

// Guest trial submit (no auth, no DB save)
async function submitGuestLog(text) {
    const store = useAppStore.getState()
    store.setLoading(true)
    try {
        const { data } = await api.post('/api/estimate/guest', { text })

        console.log('🧪 Guest Trial Response:', data)

        store.addLog({
            log_id: 'guest-trial',
            raw_input: text,
            total_kcal: data.total_kcal || 0,
            total_carbs: data.total_carbs || 0,
            total_protein: data.total_protein || 0,
            total_fat: data.total_fat || 0,
            total_sugar: 0,
            total_fiber: 0,
            total_sodium: 0,
            items: data.items || [],
            logged_at: new Date().toISOString(),
        })

        // Mark trial as used
        localStorage.setItem('mocal-guest-trial', 'true')
        store.setGuestTrialUsed(true)

        return { success: true, data }
    } catch (error) {
        console.error('Guest API Error:', error)
        if (error.response?.status === 422) {
            throw new Error('Tidak ada makanan yang terdeteksi. Pastikan Anda memasukkan nama makanan.')
        } else if (error.response?.status === 400) {
            throw new Error(error.response.data.detail || 'Input tidak valid')
        } else {
            throw new Error('Gagal memproses makanan. Coba lagi.')
        }
    } finally {
        store.setLoading(false)
    }
}
