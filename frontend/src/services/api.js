import axios from 'axios'
import { useAppStore } from '@/stores/appStore'

const api = axios.create({ baseURL: 'http://localhost:8000' })

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
        // For now, just remove from local state since backend doesn't have delete endpoint
        const store = useAppStore.getState()
        const newLogs = store.getState().logs.filter(log => log.logged_at !== logId)
        store.setLogs(newLogs)
        return { success: true }
    } catch (error) {
        console.error('Delete log error:', error)
        throw new Error('Failed to delete entry')
    }
}

// Fetch user logs
export async function fetchUserLogs() {
    const store = useAppStore.getState()
    try {
        // Try authenticated endpoint first
        const { data } = await api.get('/api/logs/all') // Using public endpoint for now
        store.setLogs(data.map(log => ({
            raw_input: log.raw_input,
            total_kcal: log.total_kcal,
            total_carbs: log.items?.reduce((s, i) => s + (i.carbs_g || 0), 0) || 0,
            total_protein: log.items?.reduce((s, i) => s + (i.protein_g || 0), 0) || 0,
            total_fat: log.items?.reduce((s, i) => s + (i.fat_g || 0), 0) || 0,
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
