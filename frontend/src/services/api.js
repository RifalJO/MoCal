import axios from 'axios'
import { useAppStore } from '@/stores/appStore'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export async function submitLog(text) {
    const store = useAppStore.getState()
    store.setLoading(true)
    try {
        const { data } = await api.post('/api/estimate', { text })
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
        return data
    } finally {
        store.setLoading(false)
    }
}
