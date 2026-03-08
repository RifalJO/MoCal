import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAppStore = create(
    persist(
        (set, get) => ({
            // Authentication
            user: null,
            token: null,
            isAuthenticated: false,

            // Log makanan hari ini
            logs: [],
            isLoading: false,

            // Totals - calculated from items data (more accurate)
            get totalKcal() { 
                return get().logs.reduce((s, l) => s + (l.total_kcal || 0), 0) 
            },
            get totalC() { 
                return Math.round(get().logs.reduce((s, l) => {
                    // Prefer calculating from items if available
                    if (l.items && l.items.length > 0) {
                        return s + l.items.reduce((sum, item) => sum + (item.carbs_g || 0), 0)
                    }
                    return s + (l.total_carbs || 0)
                }, 0))
            },
            get totalP() { 
                return Math.round(get().logs.reduce((s, l) => {
                    if (l.items && l.items.length > 0) {
                        return s + l.items.reduce((sum, item) => sum + (item.protein_g || 0), 0)
                    }
                    return s + (l.total_protein || 0)
                }, 0))
            },
            get totalF() { 
                return Math.round(get().logs.reduce((s, l) => {
                    if (l.items && l.items.length > 0) {
                        return s + l.items.reduce((sum, item) => sum + (item.fat_g || 0), 0)
                    }
                    return s + (l.total_fat || 0)
                }, 0))
            },
            get totalSugar() { 
                return Math.round(get().logs.reduce((s, l) => s + (l.total_sugar || 0), 0)) 
            },
            get totalFiber() { 
                return Math.round(get().logs.reduce((s, l) => s + (l.total_fiber || 0), 0)) 
            },
            get totalSodium() { 
                return Math.round(get().logs.reduce((s, l) => s + (l.total_sodium || 0), 0)) 
            },
            get logCount() { return get().logs.length },

            // Goals
            hasOnboarding: false,
            goals: {
                kcal: 2000, carbs: 250, protein: 150, fat: 67,
                sugar: 50, fiber: 25, sodium: 2300
            },

            // Actions
            setUser: (user) => set({ user, isAuthenticated: !!user }),
            setToken: (token) => set({ token }),
            logout: () => {
                localStorage.removeItem('mocal-token')
                localStorage.removeItem('mocal-user')
                set({ user: null, token: null, isAuthenticated: false, logs: [] })
            },
            addLog: (log) => set(s => ({ logs: [...s.logs, log] })),
            setLogs: (logs) => set({ logs }),
            deleteLog: (loggedAt) => set(s => ({ logs: s.logs.filter(l => l.logged_at !== loggedAt) })),
            clearToday: () => set({ logs: [] }),
            setLoading: (v) => set({ isLoading: v }),
            setGoals: (goals) => set({ goals }),
            setHasOnboarding: (v) => set({ hasOnboarding: v }),
        }),
        {
            name: 'mocal-storage',
            onRehydrateStorage: () => (state) => {
                if (state) {
                    const today = new Date().toDateString()
                    const saved = localStorage.getItem('mocal-date')
                    if (saved !== today) {
                        state.logs = []
                        localStorage.setItem('mocal-date', today)
                    }
                    // Restore auth state
                    const token = localStorage.getItem('mocal-token')
                    const user = localStorage.getItem('mocal-user')
                    if (token && user) {
                        state.token = token
                        state.user = JSON.parse(user)
                        state.isAuthenticated = true
                    }
                }
            }
        }
    )
)
