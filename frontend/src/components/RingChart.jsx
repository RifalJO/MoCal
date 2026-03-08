export default function RingChart({ label, value, unit, pct, color }) {
    const size = 80
    const stroke = 7
    const r = (size - stroke) / 2
    const circ = 2 * Math.PI * r
    const offset = circ - (pct / 100) * circ

    return (
        <div className="flex flex-col items-center gap-1">
            <div className="relative" style={{ width: size, height: size }}>
                <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                    {/* Track */}
                    <circle
                        cx={size / 2} cy={size / 2} r={r}
                        fill="none"
                        stroke="#E0E0E0"
                        strokeWidth={stroke}
                    />
                    {/* Progress */}
                    <circle
                        cx={size / 2} cy={size / 2} r={r}
                        fill="none"
                        stroke={color}
                        strokeWidth={stroke}
                        strokeDasharray={circ}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        transform={`rotate(-90 ${size / 2} ${size / 2})`}
                        style={{ transition: 'stroke-dashoffset 0.6s ease' }}
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-[15px] font-bold text-ink leading-none">
                        {value}
                    </span>
                    <span className="text-[10px] text-muted">{unit}</span>
                </div>
            </div>
            <span className="text-[12px] text-muted font-medium">{label}</span>
        </div>
    )
}
