import axios from 'axios'
import { useAppStore } from '@/stores/appStore'

// Use relative path for production (works with Vercel routing), fallback for local dev
const API_URL = import.meta.env.VITE_API_URL || ""

const api = axios.create({ baseURL: API_URL })

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

        console.log('✅ Auth session restored successfully')
        return { authenticated: true, user: data }
    } catch (error) {
        console.log('❌ Auth validation failed - token expired or invalid')
        // Token invalid/expired, clear session
        localStorage.removeItem('mocal-token')
        localStorage.removeItem('mocal-user')
        store.setToken(null)
        store.setUser(null)
        store.setIsAuthenticated(false)
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
        const url = date ? `/api/logs?date=${date}` : '/api/logs'
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

// Submit food log
export async function submitLog(text) {
    const store = useAppStore.getState()
    store.setLoading(true)
    try {
        const { data } = await api.post('/api/estimate', { text })

        // Debug: Log the API response
        console.log('📡 API Response:', data)
        console.log('📡 Items data:', data.items)
        if (data.items && data.items.length > 0) {
            console.log('📡 First item macros:', {
                carbs_g: data.items[0].carbs_g,
                protein_g: data.items[0].protein_g,
                fat_g: data.items[0].fat_g
            })
        }

        store.addLog({
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
