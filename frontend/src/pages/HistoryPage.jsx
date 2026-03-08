import { useAppStore } from '@/stores/appStore'
import TopBar from '@/components/TopBar'

export default function HistoryPage() {
    const { logs } = useAppStore()

    // In a real application, HistoryPage would fetch logs from the server grouped by date
    // For this local storage MVP, we will only have today's logs available locally.
    const groupedLogs = logs.length > 0 ? [
        {
            date: new Date().toISOString(),
            dateLabel: 'Today',
            logs: logs
        }
    ] : [];

    return (
        <div className="min-h-screen bg-bg max-w-[430px] mx-auto md:max-w-[1100px]">
            <TopBar />

            <div className="px-5 pt-4 pb-24 md:px-6">
                <h2 className="text-[20px] font-bold text-ink mb-4">Riwayat</h2>

                {groupedLogs.length === 0 && (
                    <p className="text-muted text-sm">Belum ada riwayat tersimpan.</p>
                )}

                {groupedLogs.map(group => (
                    <div key={group.date} className="mb-6">
                        <p className="text-xs font-semibold text-muted uppercase tracking-widest mb-2">
                            {group.dateLabel}
                        </p>
                        {group.logs.map((log, i) => (
                            <div key={i} className="flex items-start justify-between py-3 border-b border-border/30">
                                <p className="text-[15px] text-ink flex-1 pr-4 leading-relaxed line-clamp-2">
                                    {log.raw_input}
                                </p>
                                <span className="text-[15px] text-muted tabular-nums whitespace-nowrap">
                                    {log.total_kcal} cal
                                </span>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    )
}
