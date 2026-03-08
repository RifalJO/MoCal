import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '@/stores/appStore'
import { login, register, logout, fetchUserLogs } from '@/services/api'

export default function SettingsModal({ onClose }) {
    const navigate = useNavigate()
    const { goals, setGoals, hasOnboarding, setHasOnboarding, 
            isAuthenticated, user, setUser, setToken } = useAppStore()
    const { i18n } = useTranslation()
    const [showBMR, setShowBMR] = useState(!hasOnboarding)
    const [showAuth, setShowAuth] = useState(false)
    const [authMode, setAuthMode] = useState('login') // 'login' or 'register'
    const [authError, setAuthError] = useState('')
    const [authLoading, setAuthLoading] = useState(false)

    const [form, setForm] = useState({
        name: '', age: '', gender: 'male',
        weight: '', height: '', activity: 'light', goal: 'maintain'
    })

    const [authForm, setAuthForm] = useState({ email: '', password: '' })

    const calcAndSave = () => {
        const w = parseFloat(form.weight)
        const h = parseFloat(form.height)
        const a = parseInt(form.age)
        if (!w || !h || !a) return;

        const bmr = form.gender === 'male'
            ? 10 * w + 6.25 * h - 5 * a + 5
            : 10 * w + 6.25 * h - 5 * a - 161

        const mult = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725 }
        const adj = { lose: -500, maintain: 0, gain: +300 }
        const tdee = bmr * mult[form.activity]
        const kcal = Math.round(tdee + adj[form.goal])

        setGoals({
            kcal,
            carbs: Math.round((kcal * 0.50) / 4),
            protein: Math.round((kcal * 0.30) / 4),
            fat: Math.round((kcal * 0.20) / 9),
            sugar: 50,
            fiber: 25,
            sodium: 2300,
        })
        setHasOnboarding(true)
        setShowBMR(false)
        onClose()
    }

    const handleAuth = async () => {
        setAuthLoading(true)
        setAuthError('')
        try {
            if (authMode === 'login') {
                await login(authForm.email, authForm.password)
                await fetchUserLogs()
            } else {
                await register(authForm.email, authForm.password)
                setAuthMode('login')
                setAuthError('Registration successful! Please login.')
                return
            }
            setShowAuth(false)
            onClose()
        } catch (err) {
            setAuthError(err.message || 'Authentication failed')
        } finally {
            setAuthLoading(false)
        }
    }

    const handleLogout = () => {
        logout()
        onClose()
    }

    return (
        <div className="fixed inset-0 z-50 flex items-end justify-center" onClick={onClose}>
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />

            <div className="relative w-full max-w-[430px] bg-white rounded-t-3xl p-6 pb-10 shadow-2xl max-h-[90vh] overflow-y-auto"
                onClick={e => e.stopPropagation()}>

                <div className="w-10 h-1 bg-border rounded-full mx-auto mb-6" />

                <h2 className="text-[20px] font-bold text-ink mb-6">Settings</h2>

                {/* Auth Section */}
                {isAuthenticated ? (
                    <div className="mb-6 p-4 bg-bg rounded-xl border border-border/30">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-fire/10 rounded-full flex items-center justify-center">
                                    <span className="text-lg">👤</span>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-ink">{user?.email || 'User'}</p>
                                    <p className="text-xs text-muted">Logged in</p>
                                </div>
                            </div>
                            <button onClick={handleLogout}
                                className="text-sm text-red-500 hover:text-red-600 font-medium">
                                Logout
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="mb-6">
                        {showAuth ? (
                            <div className="p-4 bg-bg rounded-xl border border-border/30">
                                <h3 className="text-lg font-bold text-ink mb-4">
                                    {authMode === 'login' ? 'Login' : 'Register'}
                                </h3>
                                
                                {authError && (
                                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                                        <p className="text-sm text-red-700">{authError}</p>
                                    </div>
                                )}

                                <input
                                    type="email"
                                    placeholder="Email"
                                    value={authForm.email}
                                    onChange={e => setAuthForm(f => ({ ...f, email: e.target.value }))}
                                    className="w-full h-11 px-4 bg-white rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors mb-3"
                                />
                                <input
                                    type="password"
                                    placeholder="Password"
                                    value={authForm.password}
                                    onChange={e => setAuthForm(f => ({ ...f, password: e.target.value }))}
                                    className="w-full h-11 px-4 bg-white rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors mb-4"
                                />

                                <button
                                    onClick={handleAuth}
                                    disabled={authLoading || !authForm.email || !authForm.password}
                                    className="w-full h-12 bg-fire text-white rounded-xl font-bold text-[15px] hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all mb-3"
                                >
                                    {authLoading ? 'Please wait...' : (authMode === 'login' ? 'Login' : 'Register')}
                                </button>

                                <button
                                    onClick={() => {
                                        setAuthMode(authMode === 'login' ? 'register' : 'login')
                                        setAuthError('')
                                    }}
                                    className="w-full text-sm text-muted hover:text-ink transition-colors"
                                >
                                    {authMode === 'login' ? "Don't have an account? Register" : "Already have an account? Login"}
                                </button>

                                <button
                                    onClick={() => setShowAuth(false)}
                                    className="w-full text-sm text-muted hover:text-ink transition-colors mt-2"
                                >
                                    Cancel
                                </button>
                            </div>
                        ) : (
                            <button onClick={() => setShowAuth(true)}
                                className="w-full flex items-center justify-between py-4 px-4 bg-bg rounded-xl border border-border/30 hover:bg-bg/80 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-fire/10 rounded-full flex items-center justify-center">
                                        <span className="text-lg">👤</span>
                                    </div>
                                    <span className="text-[15px] font-medium text-ink">Login / Register</span>
                                </div>
                                <span className="text-muted">›</span>
                            </button>
                        )}
                    </div>
                )}

                {/* Language */}
                <div className="flex items-center justify-between py-4 border-b border-border/40">
                    <span className="text-[15px] font-medium text-ink">Language</span>
                    <div className="flex items-center bg-gray-100 rounded-full p-1">
                        <button onClick={() => { i18n.changeLanguage('id'); localStorage.setItem('mocal_lang', 'id') }}
                            className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${i18n.language === 'id' ? 'bg-white shadow text-ink' : 'text-muted'}`}>
                            ID
                        </button>
                        <button onClick={() => { i18n.changeLanguage('en'); localStorage.setItem('mocal_lang', 'en') }}
                            className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${i18n.language === 'en' ? 'bg-white shadow text-ink' : 'text-muted'}`}>
                            EN
                        </button>
                    </div>
                </div>

                {/* History link */}
                <button onClick={() => { navigate('/history'); onClose() }}
                    className="w-full flex items-center justify-between py-4 border-b border-border/40">
                    <span className="text-[15px] font-medium text-ink">Riwayat / History</span>
                    <span className="text-muted">›</span>
                </button>

                {/* BMR / Goals section */}
                <div className="mt-4">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-[17px] font-bold text-ink">
                            {hasOnboarding ? 'Edit Goals' : 'Set Your Goals'}
                        </h3>
                        {!hasOnboarding && (
                            <span className="text-xs bg-fire/10 text-fire px-2 py-1 rounded-full font-medium">
                                Opsional
                            </span>
                        )}
                    </div>

                    <div className="flex flex-col gap-3">
                        <input type="text" placeholder="Nama" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                            className="w-full h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />

                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder="Usia" value={form.age} onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                            <select value={form.gender} onChange={e => setForm(f => ({ ...f, gender: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                                <option value="male">Laki-laki</option>
                                <option value="female">Perempuan</option>
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder="Berat (kg)" value={form.weight} onChange={e => setForm(f => ({ ...f, weight: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                            <input type="number" placeholder="Tinggi (cm)" value={form.height} onChange={e => setForm(f => ({ ...f, height: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                        </div>

                        <select value={form.activity} onChange={e => setForm(f => ({ ...f, activity: e.target.value }))}
                            className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                            <option value="sedentary">Sedentary — Jarang bergerak</option>
                            <option value="light">Ringan — Olahraga 1–3x/minggu</option>
                            <option value="moderate">Moderat — Olahraga 3–5x/minggu</option>
                            <option value="active">Aktif — Latihan berat</option>
                        </select>

                        <select value={form.goal} onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}
                            className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                            <option value="lose">Turun Berat — Defisit 500 kkal</option>
                            <option value="maintain">Jaga Berat — Sesuai TDEE</option>
                            <option value="gain">Naik Berat — Surplus 300 kkal</option>
                        </select>

                        <button onClick={calcAndSave}
                            className="w-full h-12 bg-fire text-white rounded-xl font-bold text-[15px] hover:opacity-90 active:scale-95 transition-all mt-1">
                            Simpan Goals 🔥
                        </button>

                        {hasOnboarding && (
                            <button onClick={() => { setGoals(null); setHasOnboarding(false); onClose() }}
                                className="w-full h-10 text-sm text-muted hover:text-ink transition-colors">
                                Hapus Goals
                            </button>
                        )}
                    </div>
                </div>

            </div>
        </div>
    )
}
