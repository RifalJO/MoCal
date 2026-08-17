import confetti from 'canvas-confetti'

const STORAGE_KEY = 'mocal-celebrated'

/**
 * Konfeti saat target kalori harian tercapai.
 * Guard: maksimal SEKALI per hari (localStorage), dan tidak menyala
 * untuk user yang mengaktifkan prefers-reduced-motion.
 *
 * @returns {boolean} true jika konfeti benar-benar ditembakkan
 */
export function celebrateGoal() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false

    const today = new Date().toDateString()
    if (localStorage.getItem(STORAGE_KEY) === today) return false
    localStorage.setItem(STORAGE_KEY, today)

    confetti({
        particleCount: 120,
        spread: 75,
        startVelocity: 38,
        origin: { y: 0.7 },
    })
    return true
}
