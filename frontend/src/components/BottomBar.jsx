import { useAppStore } from '@/stores/appStore'

export default function BottomBar({ onClick }) {
    const logs = useAppStore(state => state.logs)
    
    // Calculate totals directly from logs
    const totalKcal = logs.reduce((sum, log) => sum + (log.total_kcal || 0), 0)
    
    const totalC = Math.round(logs.reduce((sum, log) => {
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

    // Debug log
    console.log('🔥 BottomBar - Logs:', logs)
    console.log('🔥 BottomBar - Calculated Totals:', { totalKcal, totalC, totalP, totalF })

    return (
        <div
            onClick={onClick}
            className="
      mx-4 mb-6 mt-2
      bg-white rounded-full
      px-6 py-4
      shadow-sm border border-border/30
      flex items-center justify-center gap-4
      cursor-pointer hover:opacity-90 active:scale-95
      transition-all duration-200
    "
        >
            <div className="flex items-center gap-1.5">
                <span className="text-base">🔥</span>
                <span className="text-[15px] font-semibold text-ink">
                    {totalKcal > 0 ? totalKcal.toLocaleString('id-ID') : '0'}
                </span>
            </div>

            <span className="text-muted/40 text-lg">·</span>

            <div className="flex items-center gap-1">
                <span className="text-[13px] font-bold text-carbs">C</span>
                <span className="text-[15px] font-semibold text-ink">{totalC > 0 ? totalC : '0'}</span>
            </div>

            <span className="text-muted/40 text-lg">·</span>

            <div className="flex items-center gap-1">
                <span className="text-[13px] font-bold text-protein">P</span>
                <span className="text-[15px] font-semibold text-ink">{totalP > 0 ? totalP : '0'}</span>
            </div>

            <span className="text-muted/40 text-lg">·</span>

            <div className="flex items-center gap-1">
                <span className="text-[13px] font-bold text-fat">F</span>
                <span className="text-[15px] font-semibold text-ink">{totalF > 0 ? totalF : '0'}</span>
            </div>
        </div>
    )
}
