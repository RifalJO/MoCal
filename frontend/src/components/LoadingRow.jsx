import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

export default function LoadingRow() {
    const { i18n, t } = useTranslation()
    const messages = t('loading.messages', { returnObjects: true })

    const [msg] = useState(() => {
        return Array.isArray(messages) && messages.length > 0
            ? messages[Math.floor(Math.random() * messages.length)]
            : "Loading..."
    })

    const [dots, setDots] = useState('')

    useEffect(() => {
        const iv = setInterval(() => setDots(d => d.length >= 3 ? '' : d + '.'), 400)
        return () => clearInterval(iv)
    }, [])

    return (
        <div className="flex items-center gap-3 py-3 text-muted text-[15px]">
            <span className="animate-[wiggle_1s_ease-in-out_infinite] inline-block">🐱</span>
            <span>{msg.replace(/\.+$/, '')}{dots}</span>
            <div className="flex gap-1 ml-1">
                {[0, 150, 300].map(d => (
                    <div key={d} className="w-1.5 h-1.5 rounded-full bg-fire/30 animate-bounce"
                        style={{ animationDelay: `${d}ms` }} />
                ))}
            </div>
        </div>
    )
}
