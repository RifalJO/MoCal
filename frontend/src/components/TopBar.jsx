import { useState } from 'react'
import { useAppStore } from '@/stores/appStore'
import SettingsModal from './SettingsModal'

export default function TopBar() {
    const { logCount } = useAppStore()
    const [showSettings, setShowSettings] = useState(false)

    return (
        <>
            <div className="flex items-center justify-between px-5 pt-4 pb-2">
                <div className="w-12 h-12">
                    <img src="/logo.png" alt="MoCal"
                        className="w-full h-full object-contain" />
                </div>

                <button className="
          bg-white rounded-full px-6 py-2
          text-[15px] font-semibold text-ink
          shadow-sm border border-border/40
        ">
                    Today
                </button>

                <div className="
          flex items-center gap-2
          bg-white rounded-full px-4 py-2
          shadow-sm border border-border/40
        ">
                    <span className="text-base">🔥</span>
                    <span className="text-[15px] font-semibold text-ink">{logCount}</span>
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
