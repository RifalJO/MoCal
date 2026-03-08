export default function LogItem({ log }) {
    return (
        <div className="flex items-start justify-between py-3
                    border-b border-border/30 last:border-0">
            <p className="text-[17px] text-ink leading-relaxed flex-1 pr-6">
                {log.raw_input}
            </p>
            <span className="text-[17px] text-muted font-normal whitespace-nowrap
                       tabular-nums pt-0.5">
                {log.total_kcal.toLocaleString('id-ID')} cal
            </span>
        </div>
    )
}
