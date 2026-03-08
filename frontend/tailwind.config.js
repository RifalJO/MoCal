/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                bg: '#F5F0EB',
                surface: '#FFFFFF',
                border: '#E8E0D8',
                ink: '#1A1A1A',
                muted: '#9B9B9B',
                fire: '#FF6B00',
                carbs: '#4CAF50',
                protein: '#9C27B0',
                fat: '#FF9800',
                goal: {
                    green: '#4CAF50',
                    red: '#F44336',
                    gray: '#E0E0E0',
                    yellow: '#FFC107',
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            borderRadius: {
                full: '9999px',
                xl: '1.5rem',
                '2xl': '2rem',
            },
            keyframes: {
                wiggle: {
                    '0%, 100%': { transform: 'rotate(-8deg) scale(1)' },
                    '25%': { transform: 'rotate(8deg)  scale(1.15)' },
                    '75%': { transform: 'rotate(-4deg) scale(1.05)' },
                },
            },
            animation: {
                wiggle: 'wiggle 1s ease-in-out infinite',
            },
        }
    },
    plugins: [],
}
