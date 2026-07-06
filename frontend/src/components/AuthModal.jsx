import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { login, register, fetchUserLogs } from '@/services/api'

// Modal Autentikasi terpusat (Gambar 3.9) — Login / Buat Akun
export default function AuthModal({ onClose, initialMode = 'login' }) {
    const { t } = useTranslation()
    const [mode, setMode] = useState(initialMode) // 'login' | 'register'
    const [form, setForm] = useState({ email: '', password: '' })
    const [error, setError] = useState('')
    const [info, setInfo] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async () => {
        if (!form.email || !form.password || loading) return
        setLoading(true)
        setError('')
        setInfo('')
        try {
            if (mode === 'login') {
                await login(form.email, form.password)
                await fetchUserLogs()
                onClose()
            } else {
                await register(form.email, form.password)
                setMode('login')
                setInfo(t('auth.registerSuccess'))
            }
        } catch (err) {
            setError(err.message || t('auth.failed'))
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4" onClick={onClose}>
            {/* overlay / scrim — bg-black/20 + blur */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />

            <div
                className="relative w-full max-w-sm bg-white rounded-2xl shadow-2xl p-8"
                onClick={e => e.stopPropagation()}
            >
                {/* Close */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>

                {/* Logo */}
                <div className="w-20 h-20 mx-auto mb-3">
                    <img src="/logo.png" alt="MoCal" className="w-full h-full object-contain" />
                </div>

                <h2 className="text-xl font-bold text-slate-900 text-center mb-6">{t('auth.title')}</h2>

                {/* Segmented control Login | Register */}
                <div className="flex bg-slate-100 rounded-full p-1 mb-5">
                    <button
                        onClick={() => { setMode('login'); setError(''); setInfo('') }}
                        className={`flex-1 py-2 rounded-full text-sm font-semibold transition-all ${mode === 'login' ? 'bg-[#df6620] text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        {t('auth.login')}
                    </button>
                    <button
                        onClick={() => { setMode('register'); setError(''); setInfo('') }}
                        className={`flex-1 py-2 rounded-full text-sm font-semibold transition-all ${mode === 'register' ? 'bg-[#df6620] text-white shadow' : 'text-slate-500 hover:text-slate-700'}`}
                    >
                        {t('auth.register')}
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl">
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}
                {info && (
                    <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                        <p className="text-sm text-emerald-700">{info}</p>
                    </div>
                )}

                <input
                    type="email"
                    placeholder={t('auth.email')}
                    value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    className="w-full h-12 px-4 bg-slate-50 rounded-xl border border-slate-200 text-sm focus:border-[#df6620] focus:outline-none transition-colors mb-3"
                />
                <input
                    type="password"
                    placeholder={t('auth.password')}
                    value={form.password}
                    onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                    onKeyDown={e => { if (e.key === 'Enter') handleSubmit() }}
                    className="w-full h-12 px-4 bg-slate-50 rounded-xl border border-slate-200 text-sm focus:border-[#df6620] focus:outline-none transition-colors mb-5"
                />

                <button
                    onClick={handleSubmit}
                    disabled={loading || !form.email || !form.password}
                    className="w-full h-12 bg-[#df6620] text-white rounded-xl font-bold text-[15px] shadow-lg shadow-[#df6620]/20 hover:opacity-90 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {loading ? t('auth.wait') : (mode === 'login' ? t('auth.submitLogin') : t('auth.submitRegister'))}
                </button>

                <p className="text-center text-sm text-slate-400 mt-4">
                    {mode === 'login' ? (
                        <>{t('auth.noAccount')}{' '}
                            <button onClick={() => { setMode('register'); setError(''); setInfo('') }}
                                className="text-[#df6620] font-semibold hover:underline">
                                {t('auth.createAccount')}
                            </button>
                        </>
                    ) : (
                        <>{t('auth.haveAccount')}{' '}
                            <button onClick={() => { setMode('login'); setError(''); setInfo('') }}
                                className="text-[#df6620] font-semibold hover:underline">
                                {t('auth.login')}
                            </button>
                        </>
                    )}
                </p>
            </div>
        </div>
    )
}
