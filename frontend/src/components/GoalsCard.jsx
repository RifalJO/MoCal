import { useAppStore } from '@/stores/appStore'
import RingChart from './RingChart'

export default function GoalsCard() {
    const { totalKcal, totalC, totalP, totalF,
        totalSugar, totalFiber, totalSodium,
        goals } = useAppStore()

    const kcalPct = Math.min((totalKcal / goals.kcal) * 100, 100)
    const carbsPct = Math.min((totalC / goals.carbs) * 100, 100)
    const proteinPct = Math.min((totalP / goals.protein) * 100, 100)
    const fatPct = Math.min((totalF / goals.fat) * 100, 100)
    const sugarPct = Math.min((totalSugar / goals.sugar) * 100, 100)
    const fiberPct = Math.min((totalFiber / goals.fiber) * 100, 100)
    const sodiumPct = Math.min((totalSodium / goals.sodium) * 100, 100)

    const ringColor = (pct) => pct >= 100 ? '#F44336' : '#4CAF50'

    return (
        <div className="bg-white rounded-2xl p-5 mt-4 shadow-sm border border-border/30">
            <h3 className="text-[17px] font-bold text-ink mb-4">Goals</h3>
            <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <span className="text-base">🔥</span>
                        <span className="text-[15px] font-medium text-ink">Calories</span>
                    </div>
                    <span className="text-[15px] font-semibold text-ink tabular-nums">
                        {totalKcal.toLocaleString('id-ID')} / {goals.kcal.toLocaleString('id-ID')}
                    </span>
                </div>
                <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-goal-yellow rounded-full transition-all duration-500"
                        style={{ width: `${kcalPct}%` }} />
                </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
                <RingChart label="Carbs" value={totalC} unit="g" pct={carbsPct} color={ringColor(carbsPct)} />
                <RingChart label="Protein" value={totalP} unit="g" pct={proteinPct} color={ringColor(proteinPct)} />
                <RingChart label="Fat" value={totalF} unit="g" pct={fatPct} color={ringColor(fatPct)} />
                <RingChart label="Sugar" value={totalSugar} unit="g" pct={sugarPct} color={ringColor(sugarPct)} />
                <RingChart label="Fiber" value={totalFiber} unit="g" pct={fiberPct} color={ringColor(fiberPct)} />
                <RingChart label="Sodium" value={totalSodium} unit="mg" pct={sodiumPct} color={ringColor(sodiumPct)} />
            </div>
        </div>
    )
}
