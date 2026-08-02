import { useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '@/stores/appStore'
import { useCountUp } from '@/hooks/useCountUp'
import { celebrateGoal } from '@/lib/celebrate'
import RingChart from './RingChart'

export default function GoalsCard() {
    const { t } = useTranslation()
    const { logs, goals, hasOnboarding } = useAppStore()

    // Calculate totals directly from logs items
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

    // Angka beranimasi (count-up) — hook dipanggil sebelum early-return
    // agar urutan hooks konsisten antar render
    const shownKcal = useCountUp(Math.round(totalKcal))
    const shownC = useCountUp(totalC)
    const shownP = useCountUp(totalP)
    const shownF = useCountUp(totalF)

    // Konfeti saat total kalori MENYEBERANGI target dalam sesi ini
    // (bukan saat halaman di-load dengan target yang sudah tercapai)
    const prevKcalRef = useRef(null)
    const goalKcal = goals?.kcal || 0
    useEffect(() => {
        const prev = prevKcalRef.current
        prevKcalRef.current = totalKcal
        if (prev === null || !goalKcal) return
        if (prev < goalKcal && totalKcal >= goalKcal) celebrateGoal()
    }, [totalKcal, goalKcal])

    if (!hasOnboarding || !goals) return null

    const kcalPct = Math.min((totalKcal / goals.kcal) * 100, 100)
    const carbsPct = Math.min((totalC / goals.carbs) * 100, 100)
    const proteinPct = Math.min((totalP / goals.protein) * 100, 100)
    const fatPct = Math.min((totalF / goals.fat) * 100, 100)

    const ringColor = (pct) => pct >= 100 ? '#F44336' : '#4CAF50'

    return (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-border/30">
            <h3 className="text-[17px] font-bold text-ink mb-4">{t('goals.title')}</h3>
            <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <span className="text-base">🔥</span>
                        <span className="text-[15px] font-medium text-ink">{t('goals.calories')}</span>
                    </div>
                    <span className="text-[15px] font-semibold text-ink tabular-nums">
                        {shownKcal.toLocaleString('id-ID')} / {goals.kcal.toLocaleString('id-ID')}
                    </span>
                </div>
                <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-goal-yellow rounded-full transition-all duration-500"
                        style={{ width: `${kcalPct}%` }} />
                </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
                <RingChart label={t('goals.carbs')} value={shownC} unit="g" pct={carbsPct} color={ringColor(carbsPct)} />
                <RingChart label={t('goals.protein')} value={shownP} unit="g" pct={proteinPct} color={ringColor(proteinPct)} />
                <RingChart label={t('goals.fat')} value={shownF} unit="g" pct={fatPct} color={ringColor(fatPct)} />
            </div>
        </div>
    )
}
