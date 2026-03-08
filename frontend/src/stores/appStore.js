import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAppStore = create(
    persist(
        (set, get) => ({
            // Log makanan hari ini
            logs: [],
            isLoading: false,

            // Totals
            get totalKcal() { return get().logs.reduce((s, l) => s + (l.total_kcal || 0), 0) },
            get totalC() { return Math.round(get().logs.reduce((s, l) => s + (l.total_carbs || 0), 0)) },
            get totalP() { return Math.round(get().logs.reduce((s, l) => s + (l.total_protein || 0), 0)) },
            get totalF() { return Math.round(get().logs.reduce((s, l) => s + (l.total_fat || 0), 0)) },
            get totalSugar() { return Math.round(get().logs.reduce((s, l) => s + (l.total_sugar || 0), 0)) },
            get totalFiber() { return Math.round(get().logs.reduce((s, l) => s + (l.total_fiber || 0), 0)) },
            get totalSodium() { return Math.round(get().logs.reduce((s, l) => s + (l.total_sodium || 0), 0)) },
            get logCount() { return get().logs.length },

            // Goals 
            hasOnboarding: false,
            goals: {
                kcal: 2000, carbs: 250, protein: 150, fat: 67,
                sugar: 50, fiber: 25, sodium: 2300
            },

            // Actions
            addLog: (log) => set(s => ({ logs: [...s.logs, log] })),
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
                }
            }
        }
    )
)
