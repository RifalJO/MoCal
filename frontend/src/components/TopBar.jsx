import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '@/stores/appStore'
import SettingsModal from './SettingsModal'

export default function TopBar() {
    const navigate = useNavigate()
    const { t } = useTranslation()
    const logCount = useAppStore(s => s.logs.length)
    const streak = useAppStore(s => s.streak)
    const isAuthenticated = useAppStore(s => s.isAuthenticated)
    const [showSettings, setShowSettings] = useState(false)

    // 🔥 = streak hari beruntun (user login); guest fallback ke jumlah log hari ini.
    // streak null (belum termuat/gagal fetch) juga fallback — jangan tampil 0 palsu.
    const showStreak = isAuthenticated && streak !== null && streak !== undefined
    const flameValue = showStreak ? streak : logCount

    return (
        <>
            <div className="flex items-center justify-between px-5 pt-4 pb-2">
                {/* Logo - No border, larger size */}
                <div className="w-16 h-16">
                    <img src="/logo.png" alt="MoCal"
                        className="w-full h-full object-contain" />
                </div>

                <button
                    onClick={() => navigate('/riwayat')}
                    className="
          bg-white rounded-full px-6 py-2
          text-[15px] font-semibold text-ink
          shadow-sm border border-border/40
          active:scale-95 transition-transform
        ">
                    {t('common.today')}
                </button>

                <div
                    className="
          flex items-center gap-2
          bg-white rounded-full px-4 py-2
          shadow-sm border border-border/40
        "
                    title={showStreak ? `${streak} hari beruntun` : undefined}
                >
                    <span className="text-base">🔥</span>
                    {/* key={flameValue}: re-mount span saat angka berubah → animasi pop */}
                    <span key={flameValue} className="streak-pop text-[15px] font-semibold text-ink">
                        {flameValue}
                    </span>
                    <button onClick={() => setShowSettings(true)}
                        className="ml-1 text-muted hover:text-ink transition-colors">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2">
                            <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>
                    </button>
                </div>
            </div>
            {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
        </>
    )
}
