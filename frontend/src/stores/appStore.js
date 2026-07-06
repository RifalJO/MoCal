import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAppStore = create(
    persist(
        (set) => ({
            // Authentication
            user: null,
            token: null,
            isAuthenticated: false,

            // Log makanan hari ini
            logs: [],
            isLoading: false,

            // Goals
            hasOnboarding: false,
            goals: {
                kcal: 2000, carbs: 250, protein: 150, fat: 67,
                sugar: 50, fiber: 25, sodium: 2300
            },
            // Data isian onboarding (nama, usia, berat, dll.) — untuk prefill form Settings
            profile: null,

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
            setProfile: (profile) => set({ profile }),
            setHasOnboarding: (v) => set({ hasOnboarding: v }),
            setIsAuthenticated: (v) => set({ isAuthenticated: v }),

            // Guest trial
            guestTrialUsed: false,
            showAuthWarning: false,
            setGuestTrialUsed: (v) => set({ guestTrialUsed: v }),
            setShowAuthWarning: (v) => set({ showAuthWarning: v }),
        }),
        {
            name: 'mocal-storage',
            // Simpan hanya data — state UI sementara (isLoading, showAuthWarning) tidak ikut
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
                logs: state.logs,
                goals: state.goals,
                profile: state.profile,
                hasOnboarding: state.hasOnboarding,
                guestTrialUsed: state.guestTrialUsed,
            }),
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
                    } else {
                        // No auth token — clear cached logs so guests don't see stale data
                        state.logs = []
                        state.isAuthenticated = false
                    }
                }
            }
        }
    )
)
