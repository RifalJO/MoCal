import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '@/stores/appStore'
import { logout, saveOnboarding } from '@/services/api'
import AuthModal from './AuthModal'

// Modal Pengaturan Profil (Gambar 3.9) — terpusat di desktop, max-width 512px
export default function SettingsModal({ onClose }) {
    const { goals, setGoals, hasOnboarding, setHasOnboarding,
            profile, setProfile, isAuthenticated, user } = useAppStore()
    const { t, i18n } = useTranslation()
    const [showAuth, setShowAuth] = useState(false)

    // Prefill dari profil tersimpan agar user tidak perlu mengisi ulang
    const [form, setForm] = useState(() => profile ?? {
        name: '', age: '', gender: 'male',
        weight: '', height: '', activity: 'light', goal: 'maintain'
    })

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
        setProfile({ ...form })
        setHasOnboarding(true)

        // Sync to server if authenticated
        if (isAuthenticated) {
            saveOnboarding(form)
        }

        onClose()
    }

    const handleLogout = () => {
        logout()
        onClose()
    }

    if (showAuth) {
        return <AuthModal onClose={() => setShowAuth(false)} />
    }

    return (
        <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center md:p-4" onClick={onClose}>
            {/* overlay / scrim — bg-black/20 + blur */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />

            <div className="relative w-full max-w-[430px] md:max-w-lg bg-white rounded-t-3xl md:rounded-2xl p-6 md:p-8 pb-10 md:pb-8 shadow-2xl max-h-[90vh] overflow-y-auto"
                onClick={e => e.stopPropagation()}>

                {/* Drag handle (mobile only) */}
                <div className="w-10 h-1 bg-border rounded-full mx-auto mb-6 md:hidden" />

                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-[20px] font-bold text-ink">{t('settings.title')}</h2>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                {/* Profil / Auth */}
                {isAuthenticated ? (
                    <div className="mb-6 p-4 bg-bg rounded-xl border border-border/30">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-fire/10 rounded-full flex items-center justify-center">
                                    <span className="text-lg">👤</span>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-ink">{user?.email || 'User'}</p>
                                    <p className="text-xs text-muted">{t('settings.loggedIn')}</p>
                                </div>
                            </div>
                            <button onClick={handleLogout}
                                className="text-sm text-red-500 hover:text-red-600 font-medium">
                                {t('settings.logout')}
                            </button>
                        </div>
                    </div>
                ) : (
                    <button onClick={() => setShowAuth(true)}
                        className="w-full flex items-center justify-between py-4 px-4 mb-6 bg-bg rounded-xl border border-border/30 hover:bg-bg/80 transition-colors">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-fire/10 rounded-full flex items-center justify-center">
                                <span className="text-lg">👤</span>
                            </div>
                            <span className="text-[15px] font-medium text-ink">{t('settings.loginRegister')}</span>
                        </div>
                        <span className="text-muted">›</span>
                    </button>
                )}

                {/* Language */}
                <div className="flex items-center justify-between py-4 border-b border-border/40">
                    <span className="text-[15px] font-medium text-ink">{t('settings.language')}</span>
                    <div className="flex items-center bg-gray-100 rounded-full p-1">
                        <button onClick={() => { i18n.changeLanguage('id'); localStorage.setItem('mocal_lang', 'id') }}
                            className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${i18n.language === 'id' ? 'bg-[#df6620] text-white shadow' : 'text-muted'}`}>
                            ID
                        </button>
                        <button onClick={() => { i18n.changeLanguage('en'); localStorage.setItem('mocal_lang', 'en') }}
                            className={`px-3 py-1 rounded-full text-sm font-semibold transition-all ${i18n.language === 'en' ? 'bg-[#df6620] text-white shadow' : 'text-muted'}`}>
                            EN
                        </button>
                    </div>
                </div>

                {/* Set Your Goals */}
                <div className="mt-4">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-[17px] font-bold text-ink">
                            {hasOnboarding ? t('settings.editGoals') : t('settings.setYourGoals')}
                        </h3>
                        {!hasOnboarding && (
                            <span className="text-xs bg-fire/10 text-fire px-2 py-1 rounded-full font-medium">
                                {t('settings.optional')}
                            </span>
                        )}
                    </div>

                    <div className="flex flex-col gap-3">
                        <input type="text" placeholder={t('settings.name')} value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                            className="w-full h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />

                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder={t('settings.age')} value={form.age} onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                            <select value={form.gender} onChange={e => setForm(f => ({ ...f, gender: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                                <option value="male">{t('settings.male')}</option>
                                <option value="female">{t('settings.female')}</option>
                            </select>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder={t('settings.weight')} value={form.weight} onChange={e => setForm(f => ({ ...f, weight: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                            <input type="number" placeholder={t('settings.height')} value={form.height} onChange={e => setForm(f => ({ ...f, height: e.target.value }))}
                                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors" />
                        </div>

                        <select value={form.activity} onChange={e => setForm(f => ({ ...f, activity: e.target.value }))}
                            className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                            <option value="sedentary">{t('settings.activitySedentary')}</option>
                            <option value="light">{t('settings.activityLight')}</option>
                            <option value="moderate">{t('settings.activityModerate')}</option>
                            <option value="active">{t('settings.activityActive')}</option>
                        </select>

                        <select value={form.goal} onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}
                            className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50 text-sm focus:border-fire focus:outline-none transition-colors">
                            <option value="lose">{t('settings.goalLose')}</option>
                            <option value="maintain">{t('settings.goalMaintain')}</option>
                            <option value="gain">{t('settings.goalGain')}</option>
                        </select>

                        <button onClick={calcAndSave}
                            className="w-full h-12 bg-[#df6620] text-white rounded-xl font-bold text-[15px] shadow-lg shadow-[#df6620]/20 hover:opacity-90 active:scale-95 transition-all mt-1">
                            {t('settings.saveGoals')}
                        </button>

                        {hasOnboarding && (
                            <button onClick={() => { setGoals(null); setProfile(null); setHasOnboarding(false); onClose() }}
                                className="w-full h-10 text-sm text-red-500 hover:text-red-600 font-medium transition-colors">
                                {t('settings.deleteGoals')}
                            </button>
                        )}
                    </div>
                </div>

            </div>
        </div>
    )
}
