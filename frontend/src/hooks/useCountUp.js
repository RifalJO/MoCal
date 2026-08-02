import { useEffect, useRef, useState } from 'react'

/**
 * Animasi angka naik/turun menuju `target` (ease-out, requestAnimationFrame).
 * Render pertama mulai dari 0 supaya angka "terisi" saat halaman dibuka.
 * Menghormati prefers-reduced-motion: langsung lompat ke target.
 *
 * @param {number} target nilai akhir
 * @param {number} duration durasi ms (default 600)
 * @returns {number} nilai yang sedang ditampilkan
 */
export function useCountUp(target, duration = 600) {
    const [display, setDisplay] = useState(0)
    const fromRef = useRef(0)
    const rafRef = useRef(null)

    useEffect(() => {
        const from = fromRef.current
        const to = Number(target) || 0
        if (from === to) return undefined

        fromRef.current = to

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            // Lewat rAF supaya setState tidak sinkron di badan effect
            rafRef.current = requestAnimationFrame(() => setDisplay(to))
            return () => cancelAnimationFrame(rafRef.current)
        }

        const start = performance.now()
        const tick = (now) => {
            const p = Math.min((now - start) / duration, 1)
            const eased = 1 - Math.pow(1 - p, 3)   // ease-out cubic
            setDisplay(Math.round(from + (to - from) * eased))
            if (p < 1) rafRef.current = requestAnimationFrame(tick)
        }
        rafRef.current = requestAnimationFrame(tick)
        return () => cancelAnimationFrame(rafRef.current)
    }, [target, duration])

    return display
}
