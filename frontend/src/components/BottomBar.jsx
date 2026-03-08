import { useAppStore } from '@/stores/appStore'

export default function BottomBar({ onClick }) {
    const { totalKcal, totalC, totalP, totalF } = useAppStore()

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
                <span className="text-[15px] font-semibold text-ink">{totalC}</span>
            </div>

            <span className="text-muted/40 text-lg">·</span>

            <div className="flex items-center gap-1">
                <span className="text-[13px] font-bold text-protein">P</span>
                <span className="text-[15px] font-semibold text-ink">{totalP}</span>
            </div>

            <span className="text-muted/40 text-lg">·</span>

            <div className="flex items-center gap-1">
                <span className="text-[13px] font-bold text-fat">F</span>
                <span className="text-[15px] font-semibold text-ink">{totalF}</span>
            </div>
        </div>
    )
}
