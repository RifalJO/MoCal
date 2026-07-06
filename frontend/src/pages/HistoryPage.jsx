import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '@/stores/appStore'
import { fetchLogsByDate, deleteLog } from '@/services/api'

// Halaman Riwayat (Gambar 3.8) — kalender bulan + total harian + daftar entri per tanggal
export default function HistoryPage() {
    const navigate = useNavigate()
    const { t, i18n } = useTranslation()
    const locale = i18n.language === 'id' ? 'id-ID' : 'en-US'
    const { isAuthenticated } = useAppStore()

    const [selectedDate, setSelectedDate] = useState(new Date())
    const [viewDate, setViewDate] = useState(new Date())
    const [dayLogs, setDayLogs] = useState([])
    const [isLoading, setIsLoading] = useState(false)

    const formatDateForAPI = (date) => {
        const y = date.getFullYear()
        const m = String(date.getMonth() + 1).padStart(2, '0')
        const d = String(date.getDate()).padStart(2, '0')
        return `${y}-${m}-${d}`
    }

    // pilih tanggal → daftar entri di kanan mengikuti tanggal terpilih
    useEffect(() => {
        if (!isAuthenticated) return
        let cancelled = false
        const load = async () => {
            setIsLoading(true)
            const data = await fetchLogsByDate(formatDateForAPI(selectedDate))
            if (!cancelled) {
                setDayLogs(data)
                setIsLoading(false)
            }
        }
        load()
        return () => { cancelled = true }
    }, [selectedDate, isAuthenticated])

    const handleDelete = async (logId) => {
        try {
            await deleteLog(logId)
            const data = await fetchLogsByDate(formatDateForAPI(selectedDate))
            setDayLogs(data)
        } catch {
            // biarkan daftar apa adanya jika gagal hapus
        }
    }

    // ── Kalender ──────────────────────────────────────────────────────────────
    // Senin dulu — ID: S S R K J S M, EN: M T W T F S S
    const dayInitials = t('history.dayInitials', { returnObjects: true })
    const monthLabel = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1)
        .toLocaleDateString(locale, { month: 'long', year: 'numeric' })

    const year = viewDate.getFullYear()
    const month = viewDate.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    const startOffset = (new Date(year, month, 1).getDay() + 6) % 7 // Monday-first

    const isToday = (day) => {
        const t = new Date()
        return day === t.getDate() && month === t.getMonth() && year === t.getFullYear()
    }
    const isSelected = (day) =>
        day === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear()

    const isFuture = (day) => new Date(year, month, day) > new Date()

    const totalKcal = dayLogs.reduce((sum, log) => sum + (log.total_kcal || 0), 0)

    const dateLabel = selectedDate.toLocaleDateString(locale, {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    })

    return (
        <div className="min-h-screen bg-[#f8f7f6]">
            <div className="max-w-5xl mx-auto px-4 py-5 sm:px-6 sm:py-8">
                {/* Header */}
                <header className="flex items-center justify-between mb-6 sm:mb-10 border-b border-[#df6620]/10 pb-4 sm:pb-6">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/')}
                            className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:border-[#df6620] hover:text-[#df6620] transition-colors shadow-sm"
                            title={t('history.back')}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="15 18 9 12 15 6" />
                            </svg>
                        </button>
                        <h1 className="text-2xl font-bold tracking-tight text-ink">{t('history.title')}</h1>
                    </div>
                    <button
                        onClick={() => { const t = new Date(); setViewDate(t); setSelectedDate(t) }}
                        className="w-10 h-10 rounded-full bg-[#df6620]/10 flex items-center justify-center border border-[#df6620]/20 hover:bg-[#df6620]/20 transition-colors"
                        title={t('history.goToToday')}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-[#df6620]">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                            <line x1="16" y1="2" x2="16" y2="6" />
                            <line x1="8" y1="2" x2="8" y2="6" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                    </button>
                </header>

                <main className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8 pb-8">
                    {/* Kolom kiri — kalender + total */}
                    <div className="md:col-span-5 lg:col-span-4 flex flex-col gap-6">
                        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                            {/* Navigasi bulan */}
                            <div className="flex items-center justify-between mb-4">
                                <button
                                    onClick={() => setViewDate(new Date(year, month - 1, 1))}
                                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-100 hover:text-[#df6620] transition-colors"
                                >
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polyline points="15 18 9 12 15 6" />
                                    </svg>
                                </button>
                                <p className="font-bold text-ink capitalize">{monthLabel}</p>
                                <button
                                    onClick={() => setViewDate(new Date(year, month + 1, 1))}
                                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-100 hover:text-[#df6620] transition-colors"
                                >
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polyline points="9 18 15 12 9 6" />
                                    </svg>
                                </button>
                            </div>

                            {/* Inisial hari */}
                            <div className="grid grid-cols-7 gap-1 mb-1">
                                {dayInitials.map((d, i) => (
                                    <div key={i} className="h-8 flex items-center justify-center text-xs font-medium text-slate-400">
                                        {d}
                                    </div>
                                ))}
                            </div>

                            {/* Grid tanggal */}
                            <div className="grid grid-cols-7 gap-1">
                                {Array.from({ length: startOffset }).map((_, i) => (
                                    <div key={`e-${i}`} className="h-9" />
                                ))}
                                {Array.from({ length: daysInMonth }).map((_, i) => {
                                    const day = i + 1
                                    return (
                                        <button
                                            key={day}
                                            onClick={() => setSelectedDate(new Date(year, month, day))}
                                            disabled={isFuture(day)}
                                            className={`h-9 rounded-lg text-sm font-medium transition-all
                                                ${isSelected(day)
                                                    ? 'bg-[#df6620] text-white font-bold shadow-md shadow-[#df6620]/30'
                                                    : isToday(day)
                                                        ? 'border-2 border-[#df6620] text-[#df6620] font-bold'
                                                        : isFuture(day)
                                                            ? 'text-slate-300 cursor-not-allowed'
                                                            : 'text-slate-700 hover:bg-[#df6620]/10'}`}
                                        >
                                            {day}
                                        </button>
                                    )
                                })}
                            </div>

                            <p className="text-xs text-slate-400 mt-4">
                                {t('history.pickDate')}
                            </p>
                        </div>

                        {/* Total kalori tanggal terpilih */}
                        <div className="bg-[#df6620] text-white p-6 rounded-xl shadow-xl shadow-[#df6620]/20 relative overflow-hidden group">
                            <div className="relative z-10">
                                <h2 className="text-4xl font-bold mb-1">
                                    {totalKcal.toLocaleString(locale)} <span className="text-2xl">kcal</span> 🔥
                                </h2>
                                <p className="text-sm opacity-90 font-medium">{t('history.totalSelected')}</p>
                            </div>
                            <div className="absolute -right-4 -bottom-4 text-white/10 text-8xl rotate-12 group-hover:rotate-0 transition-transform duration-500">
                                🍽️
                            </div>
                        </div>
                    </div>

                    {/* Kolom kanan — daftar entri */}
                    <div className="md:col-span-7 lg:col-span-8">
                        <div className="flex items-baseline justify-between mb-4">
                            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-widest">{t('history.entriesTitle')}</h3>
                            <span className="text-xs text-slate-400 capitalize">{dateLabel}</span>
                        </div>

                        {!isAuthenticated ? (
                            <div className="bg-slate-50 p-10 rounded-xl border border-dashed border-slate-300 text-center">
                                <div className="text-4xl mb-3">🐱</div>
                                <p className="text-sm text-slate-500">
                                    {t('history.loginPrompt')}
                                </p>
                            </div>
                        ) : isLoading ? (
                            <div className="flex items-center gap-3 py-6 text-slate-400 text-sm">
                                <span className="animate-[wiggle_1s_ease-in-out_infinite] inline-block">🐱</span>
                                <span>{t('history.loading')}</span>
                            </div>
                        ) : dayLogs.length === 0 ? (
                            <div className="bg-slate-50 p-10 rounded-xl border border-dashed border-slate-300 text-center">
                                <p className="text-sm text-slate-400">{t('history.empty')}</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {dayLogs.map((log, i) => (
                                    <div key={log.log_id || i}
                                        className="group flex items-center justify-between py-4 px-5 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all">
                                        <div className="flex-1 pr-4">
                                            <p className="text-slate-700 font-medium">{log.raw_input}</p>
                                            <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                                                <span className="flex items-center gap-1">
                                                    <span className="text-carbs font-semibold">C</span>
                                                    <span>{Math.round(log.items?.reduce((s, item) => s + (item.carbs_g || 0), 0) || log.total_carbs || 0)}g</span>
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <span className="text-protein font-semibold">P</span>
                                                    <span>{Math.round(log.items?.reduce((s, item) => s + (item.protein_g || 0), 0) || log.total_protein || 0)}g</span>
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <span className="text-fat font-semibold">F</span>
                                                    <span>{Math.round(log.items?.reduce((s, item) => s + (item.fat_g || 0), 0) || log.total_fat || 0)}g</span>
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm font-bold text-[#df6620] bg-[#df6620]/5 border border-[#df6620]/20 rounded-full px-3 py-1 whitespace-nowrap">
                                                {Math.round(log.total_kcal).toLocaleString(locale)} kcal
                                            </span>
                                            <button
                                                onClick={() => handleDelete(log.log_id)}
                                                className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                                title={t('journal.deleteEntry')}
                                            >
                                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    )
}
