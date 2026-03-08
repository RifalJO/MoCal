import { useState } from 'react'
import { useAppStore } from '@/stores/appStore'
import { submitLog } from '@/services/api'
import TopBar from '@/components/TopBar'
import BottomBar from '@/components/BottomBar'
import LogItem from '@/components/LogItem'
import GoalsCard from '@/components/GoalsCard'
import LoadingRow from '@/components/LoadingRow'
import SettingsModal from '@/components/SettingsModal'

export default function MainApp() {
    const { logs, isLoading, hasOnboarding } = useAppStore()
    const [inputText, setInputText] = useState('')
    const [showSettings, setShowSettings] = useState(false)

    const handleSubmit = async () => {
        if (!inputText.trim() || isLoading) return
        await submitLog(inputText)
        setInputText('')
    }

    return (
        <div className="min-h-screen bg-bg">
            <div className="max-w-[1100px] mx-auto flex flex-col md:block">

                {/* Mobile View Wrapper (default) */}
                <div className="md:hidden flex flex-col min-h-screen max-w-[430px] mx-auto w-full">
                    <TopBar />
                    <div className="flex-1 overflow-y-auto px-5 pt-6 pb-4 flex flex-col gap-1">
                        {logs.length === 0 && !isLoading && (
                            <p className="text-muted text-lg mt-2">
                                Start logging your meals...
                            </p>
                        )}
                        {logs.map((log, i) => <LogItem key={i} log={log} />)}
                        {isLoading && <LoadingRow />}
                        <textarea
                            className="w-full bg-transparent border-none outline-none resize-none
                         text-[17px] text-ink leading-relaxed mt-2
                         placeholder:text-muted/50 caret-fire
                         min-h-[80px]"
                            placeholder=""
                            value={inputText}
                            onChange={e => setInputText(e.target.value)}
                            onKeyDown={e => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleSubmit()
                                }
                            }}
                        />
                        {hasOnboarding && <GoalsCard />}
                    </div>
                    <BottomBar />
                </div>

                {/* Desktop View Wrapper */}
                <div className="hidden md:block w-full">
                    <TopBar />
                    <div className="flex gap-6 px-6 pt-4">
                        <div className="flex-1 flex flex-col min-h-[calc(100vh-80px)]">
                            {logs.length === 0 && !isLoading && (
                                <p className="text-muted text-lg mt-2 mb-4">
                                    Start logging your meals...
                                </p>
                            )}
                            {logs.map((log, i) => <LogItem key={i} log={log} />)}
                            {isLoading && <LoadingRow />}
                            <textarea
                                className="w-full bg-transparent border-none outline-none resize-none
                           text-[17px] text-ink leading-relaxed mt-4
                           placeholder:text-muted/50 caret-fire
                           min-h-[120px]"
                                placeholder=""
                                value={inputText}
                                onChange={e => setInputText(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault()
                                        handleSubmit()
                                    }
                                }}
                            />
                            <div className="mt-auto">
                                <BottomBar />
                            </div>
                        </div>

                        <div className="w-[380px] flex-shrink-0">
                            <div className="sticky top-6">
                                {hasOnboarding
                                    ? <GoalsCard />
                                    : <div className="bg-white rounded-2xl p-5 border border-border/30 text-center mt-4">
                                        <p className="text-muted text-sm mb-3">
                                            Set your goals to track macros
                                        </p>
                                        <button onClick={() => setShowSettings(true)}
                                            className="text-fire font-semibold text-sm hover:underline">
                                            Set Goals →
                                        </button>
                                    </div>
                                }
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
        </div>
    )
}
