import { useState, useEffect } from 'react'
import { useAppStore } from '@/stores/appStore'
import { submitLog, fetchUserLogs, deleteLog } from '@/services/api'
import TopBar from '@/components/TopBar'
import BottomBar from '@/components/BottomBar'
import LogItem from '@/components/LogItem'
import GoalsCard from '@/components/GoalsCard'
import LoadingRow from '@/components/LoadingRow'
import SettingsModal from '@/components/SettingsModal'

export default function MainApp() {
    const { logs, isLoading, hasOnboarding, goals, isAuthenticated, deleteLog: deleteLogAction } = useAppStore()
    const [inputText, setInputText] = useState('')
    const [showSettings, setShowSettings] = useState(false)
    const [showGoals, setShowGoals] = useState(false)
    const [error, setError] = useState('')

    // Fetch logs on mount if authenticated
    useEffect(() => {
        if (isAuthenticated) {
            fetchUserLogs()
        }
    }, [isAuthenticated])

    const handleSubmit = async () => {
        if (!inputText.trim() || isLoading) return
        try {
            await submitLog(inputText)
            setInputText('')
            setError('')
        } catch (err) {
            setError(err.message || 'Terjadi kesalahan saat memproses makanan')
            setTimeout(() => setError(''), 5000)
        }
    }

    const handleDelete = (loggedAt) => {
        deleteLogAction(loggedAt)
    }

    // Calculate totals for desktop summary - from items data
    const totalKcal = logs.reduce((sum, log) => sum + (log.total_kcal || 0), 0)
    const totalC = Math.round(logs.reduce((sum, log) => {
        // Calculate from items if available
        if (log.items && log.items.length > 0) {
            return sum + log.items.reduce((s, item) => s + (item.carbs_g || 0), 0)
        }
        return sum + (log.total_carbs || 0)
    }, 0))
    const totalP = Math.round(logs.reduce((sum, log) => {
        if (log.items && log.items.length > 0) {
            return sum + log.items.reduce((s, item) => s + (item.protein_g || 0), 0)
        }
        return sum + (log.total_protein || 0)
    }, 0))
    const totalF = Math.round(logs.reduce((sum, log) => {
        if (log.items && log.items.length > 0) {
            return sum + log.items.reduce((s, item) => s + (item.fat_g || 0), 0)
        }
        return sum + (log.total_fat || 0)
    }, 0))

    const kcalPct = goals ? Math.min((totalKcal / goals.kcal) * 100, 100) : 0
    const proteinPct = goals ? Math.min((totalP / goals.protein) * 100, 100) : 0
    const carbsPct = goals ? Math.min((totalC / goals.carbs) * 100, 100) : 0
    const fatPct = goals ? Math.min((totalF / goals.fat) * 100, 100) : 0

    return (
        <div className="min-h-screen bg-[#f8f7f6]">
            {/* Mobile View - max 430px width */}
            <div className="md:hidden flex flex-col min-h-screen max-w-[430px] mx-auto w-full relative">
                <TopBar />
                <div className="flex-1 overflow-y-auto px-5 pt-6 pb-4 flex flex-col gap-1">
                    {/* Textarea input - always visible at top */}
                    <textarea
                        className="w-full bg-transparent border-none outline-none resize-none
                     text-[17px] text-slate-900 leading-relaxed
                     placeholder:text-slate-400 caret-[#df6620]
                     min-h-[80px]"
                        placeholder="Sudah makan apa hari ini? ..."
                        value={inputText}
                        onChange={e => setInputText(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault()
                                handleSubmit()
                            }
                        }}
                    />

                    {/* Log items */}
                    {logs.length === 0 && !isLoading && (
                        <p className="text-slate-400 text-lg mt-2">
                            
                        </p>
                    )}
                    {logs.map((log, i) => <LogItem key={i} log={log} />)}
                    {isLoading && <LoadingRow />}
                </div>

                {/* BottomBar */}
                <div className="relative z-10">
                    <BottomBar onClick={() => setShowGoals(!showGoals)} />
                </div>

                {/* Goals Panel Overlay - pops up from bottom */}
                {showGoals && (
                    <>
                        {/* Backdrop */}
                        <div
                            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                            onClick={() => setShowGoals(false)}
                        />
                        {/* Goals Card - slide up from bottom */}
                        <div className="fixed bottom-24 left-0 right-0 z-50 flex justify-center px-4">
                            <div className="w-full max-w-[430px]">
                                {hasOnboarding && <GoalsCard />}
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Desktop View - Reference Design */}
            <div className="hidden md:block max-w-5xl mx-auto px-6 py-8">
                {/* Header */}
                <header className="flex items-center justify-between mb-12 border-b border-[#df6620]/10 pb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-[#df6620] rounded-xl flex items-center justify-center">
                            <img src="/logo.png" alt="MoCal" className="w-7 h-7 object-contain" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight text-[#df6620]">MoCal</h1>
                            <p className="text-xs uppercase tracking-widest opacity-60 font-medium">Every calorie tells a story...</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-medium opacity-60">Today</p>
                            <p className="text-lg font-bold">
                                {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                            </p>
                        </div>
                        <button onClick={() => setShowSettings(true)}
                            className="w-10 h-10 rounded-full bg-[#df6620]/10 flex items-center justify-center border border-[#df6620]/20 hover:bg-[#df6620]/20 transition-colors">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" strokeWidth="2" className="text-[#df6620]">
                                <circle cx="12" cy="12" r="3" />
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                            </svg>
                        </button>
                    </div>
                </header>

                <main className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Main Writing Area */}
                    <div className="lg:col-span-8 flex flex-col gap-6">
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200 min-h-[600px] flex flex-col p-8 transition-all hover:shadow-md">
                            {/* Toolbar */}
                            <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
                                <div className="flex items-center gap-4">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="2" className="text-slate-400">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                        <polyline points="14 2 14 8 20 8" />
                                        <line x1="16" y1="13" x2="8" y2="13" />
                                        <line x1="16" y1="17" x2="8" y2="17" />
                                        <polyline points="10 9 9 9 8 9" />
                                    </svg>
                                    <span className="text-sm font-medium text-slate-400">Daily Journal</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-slate-400 mr-2">
                                        {logs.length} {logs.length === 1 ? 'meal' : 'meals'} logged
                                    </span>
                                </div>
                            </div>

                            {/* Writing Area */}
                            <textarea
                                className="w-full flex-1 bg-transparent resize-none text-lg leading-relaxed placeholder:text-slate-300 focus:ring-0 border-none outline-none ring-0 font-mono"
                                placeholder="Pagi ini saya makan nasi padang pakai kerupuk putih 1"
                                value={inputText}
                                onChange={e => setInputText(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault()
                                        handleSubmit()
                                    }
                                }}
                            />

                            {/* Error Toast */}
                            {error && (
                                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                                    <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <circle cx="12" cy="12" r="10"/>
                                        <line x1="12" y1="8" x2="12" y2="12"/>
                                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                                    </svg>
                                    <p className="text-sm text-red-700">{error}</p>
                                </div>
                            )}

                            {/* Footer */}
                            <div className="mt-8 pt-6 border-t border-slate-100 flex justify-between items-center">
                                <p className="text-xs text-slate-400 font-mono">
                                    {logs.length > 0 ? `Last entry: ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Start your food journal...'}
                                </p>
                                <button
                                    onClick={handleSubmit}
                                    disabled={!inputText.trim() || isLoading}
                                    className="bg-[#df6620] text-white px-8 py-2.5 rounded-lg font-bold shadow-lg shadow-[#df6620]/20 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all active:scale-95"
                                >
                                    Add Entry
                                </button>
                            </div>

                            {/* Log Items */}
                            {logs.length > 0 && (
                                <div className="mt-6 pt-6 border-t border-slate-100">
                                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-widest mb-4">Today's Entries</h3>
                                    <div className="space-y-0">
                                        {logs.map((log, i) => (
                                            <div key={i} className="group flex items-center justify-between py-3 px-4 bg-slate-50 rounded-lg mb-2 hover:bg-slate-100 transition-colors">
                                                <div className="flex-1 pr-4">
                                                    <p className="text-slate-700 font-medium">{log.raw_input}</p>
                                                    <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                                                        <span className="flex items-center gap-1">
                                                            <span className="text-carbs font-semibold">C</span>
                                                            <span>{Math.round(log.items?.reduce((s, item) => s + (item.carbs_g || 0), 0) || 0)}g</span>
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <span className="text-protein font-semibold">P</span>
                                                            <span>{Math.round(log.items?.reduce((s, item) => s + (item.protein_g || 0), 0) || 0)}g</span>
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <span className="text-fat font-semibold">F</span>
                                                            <span>{Math.round(log.items?.reduce((s, item) => s + (item.fat_g || 0), 0) || 0)}g</span>
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span className="text-lg font-bold text-[#df6620] min-w-[80px] text-right">
                                                        {log.total_kcal} kcal
                                                    </span>
                                                    <button
                                                        onClick={() => handleDelete(log.logged_at)}
                                                        className="opacity-0 group-hover:opacity-100 p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                                        title="Delete entry"
                                                    >
                                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                                                        </svg>
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    {isLoading && <LoadingRow />}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Floating Sidebar Stats */}
                    <div className="lg:col-span-4 flex flex-col gap-6">
                        <div className="sticky top-8 flex flex-col gap-6">
                            {/* Calorie Tally Card */}
                            <div className="bg-[#df6620] text-white p-8 rounded-xl shadow-xl shadow-[#df6620]/20 relative overflow-hidden group">
                                <div className="relative z-10">
                                    <p className="text-sm font-medium opacity-80 uppercase tracking-widest mb-1">Meowlorie</p>
                                    <h2 className="text-5xl font-bold mb-4">{totalKcal.toLocaleString()}</h2>
                                    <p className="text-lg opacity-90 mb-6 font-medium">kcal consumed</p>
                                    <div className="w-full bg-white/20 rounded-full h-2 mb-2">
                                        <div className="bg-white h-2 rounded-full transition-all" style={{ width: `${kcalPct}%` }} />
                                    </div>
                                    <div className="flex justify-between text-xs font-mono opacity-80">
                                        <span>{kcalPct.toFixed(0)}% of daily goal</span>
                                        <span>Target: {goals?.kcal.toLocaleString()}</span>
                                    </div>
                                </div>
                                <div className="absolute -right-4 -bottom-4 text-white/10 text-9xl rotate-12 group-hover:rotate-0 transition-transform duration-500">
                                    🍽️
                                </div>
                            </div>

                            {/* Macro Breakdown */}
                            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                                <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="2" className="text-[#df6620]">
                                        <circle cx="12" cy="12" r="10" />
                                        <path d="M12 2a10 10 0 0 1 10 10" />
                                    </svg>
                                    Macro Breakdown
                                </h3>
                                <div className="space-y-4">
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="opacity-60">Protein</span>
                                            <span className="font-mono font-medium">{totalP}g / {goals?.protein}g</span>
                                        </div>
                                        <div className="w-full bg-slate-100 rounded-full h-1.5">
                                            <div className="bg-blue-400 h-1.5 rounded-full transition-all" style={{ width: `${proteinPct}%` }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="opacity-60">Carbs</span>
                                            <span className="font-mono font-medium">{totalC}g / {goals?.carbs}g</span>
                                        </div>
                                        <div className="w-full bg-slate-100 rounded-full h-1.5">
                                            <div className="bg-emerald-400 h-1.5 rounded-full transition-all" style={{ width: `${carbsPct}%` }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="opacity-60">Fats</span>
                                            <span className="font-mono font-medium">{totalF}g / {goals?.fat}g</span>
                                        </div>
                                        <div className="w-full bg-slate-100 rounded-full h-1.5">
                                            <div className="bg-amber-400 h-1.5 rounded-full transition-all" style={{ width: `${fatPct}%` }} />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Goals Panel - Toggle */}
                            {hasOnboarding && (
                                <button
                                    onClick={() => setShowGoals(true)}
                                    className="bg-slate-50 p-6 rounded-xl border border-dashed border-slate-300 hover:border-[#df6620] hover:bg-[#df6620]/5 transition-all group"
                                >
                                    <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2 group-hover:text-[#df6620]">
                                        View Detailed Goals
                                    </h3>
                                    <p className="text-sm text-slate-500">
                                        See your complete macro and micronutrient breakdown
                                    </p>
                                </button>
                            )}

                            {!hasOnboarding && (
                                <div className="bg-slate-50 p-6 rounded-xl border border-dashed border-slate-300">
                                    <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">Get Started</h3>
                                    <p className="text-sm text-slate-500 mb-4">
                                        Set your daily calorie and macro goals based on your personal info
                                    </p>
                                    <button onClick={() => setShowSettings(true)}
                                        className="w-full py-3 bg-[#df6620] text-white rounded-lg font-bold hover:opacity-90 transition-opacity">
                                        Set Goals →
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </main>
            </div>

            {/* Goals Modal for Desktop */}
            {showGoals && (
                <>
                    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                        onClick={() => setShowGoals(false)}
                    />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
                        onClick={() => setShowGoals(false)}
                    >
                        <div className="w-full max-w-lg" onClick={e => e.stopPropagation()}>
                            {hasOnboarding && <GoalsCard />}
                        </div>
                    </div>
                </>
            )}

            {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
        </div>
    )
}
