# MoCal — Frontend Prompt (Fresh Start)
# Berdasarkan 3 foto referensi yang diberikan

> Bangun frontend MoCal dari nol mengikuti foto referensi secara persis.
> Tidak ada login. Langsung bisa pakai. Data tersimpan di localStorage.
> Backend FastAPI sudah berjalan di http://localhost:8000

---

## TECH STACK

```
React 18 + Vite
Tailwind CSS
React Router v6
Axios
Zustand (state management)
i18next + react-i18next (ID/EN)
```

---

## DESIGN TOKENS

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg:      '#F5F0EB',   // cream background — warna dari foto
        surface: '#FFFFFF',
        border:  '#E8E0D8',
        ink:     '#1A1A1A',
        muted:   '#9B9B9B',   // warna teks kalori di kanan (abu-abu)
        fire:    '#FF6B00',   // warna kalori & icon 🔥
        carbs:   '#4CAF50',   // hijau — C
        protein: '#9C27B0',   // ungu — P
        fat:     '#FF9800',   // oranye — F
        goal: {
          green:  '#4CAF50',
          red:    '#F44336',
          gray:   '#E0E0E0',
          yellow: '#FFC107',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        full: '9999px',
        xl:   '1.5rem',
        '2xl':'2rem',
      }
    }
  }
}
```

```html
<!-- index.html <head> -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
```

```css
/* index.css */
body {
  font-family: 'Inter', sans-serif;
  background-color: #F5F0EB;
}
```

---

## STRUKTUR FOLDER

```
src/
├── components/
│   ├── TopBar.jsx          ← header semua halaman
│   ├── BottomBar.jsx       ← summary bar bawah (🔥 C P F)
│   ├── LogItem.jsx         ← satu baris log makanan
│   ├── GoalsCard.jsx       ← card Goals dengan ring charts
│   ├── RingChart.jsx       ← satu ring chart (SVG)
│   ├── SettingsModal.jsx   ← modal settings + onboarding BMR
│   ├── LoadingRow.jsx      ← loading state inline
│   └── LangToggle.jsx
├── pages/
│   ├── MainApp.jsx         ← halaman utama (foto 1 & 2 & 3)
│   └── HistoryPage.jsx     ← riwayat
├── stores/
│   └── appStore.js         ← Zustand store
├── services/
│   └── api.js
└── i18n/
    ├── index.js
    ├── id.json
    └── en.json
```

---

## HALAMAN UTAMA — MainApp.jsx
### Mengikuti PERSIS foto 1, 2, 3

```
┌─────────────────────────────────────┐
│  [LOGO]    [  Today  ]   [🔥N] [⚙️] │  ← TopBar
├─────────────────────────────────────┤
│                                     │
│  teks input user          797 cal   │  ← LogItem (foto 2)
│                                     │
│  Noodles with Chicken     940 cal   │
│                                     │
│  Fried Noodles...         820 cal   │
│                                     │
│  [loading cat saat API]             │
│                                     │
│  [textarea — transparan]            │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Goals                       │    │  ← GoalsCard (foto 3)
│  │ 🔥 Calories    2557 / 2751  │    │    muncul jika onboarding selesai
│  │ [progress bar kuning]       │    │
│  │ [ring] [ring] [ring]        │    │
│  │ Carbs  Protein Fat          │    │
│  │ [ring] [ring] [ring]        │    │
│  │ Sugar  Fiber  Sodium        │    │
│  └─────────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│  🔥 2.557 · C 279 · P 111 · F 104  │  ← BottomBar
└─────────────────────────────────────┘
```

```jsx
// MainApp.jsx
export default function MainApp() {
  const { logs, isLoading, totalKcal, totalC, totalP, totalF,
          goals, hasOnboarding } = useAppStore()
  const [inputText, setInputText] = useState('')

  const handleSubmit = async () => {
    if (!inputText.trim() || isLoading) return
    await submitLog(inputText)
    setInputText('')
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col max-w-[430px] mx-auto">
      <TopBar />

      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto px-5 pt-6 pb-4 flex flex-col gap-1">

        {/* Empty state */}
        {logs.length === 0 && !isLoading && (
          <p className="text-muted text-lg mt-2">
            Start logging your meals...
          </p>
        )}

        {/* Log items */}
        {logs.map((log, i) => <LogItem key={i} log={log} />)}

        {/* Loading state */}
        {isLoading && <LoadingRow />}

        {/* Textarea input — invisible, di bawah log */}
        <textarea
          className="w-full bg-transparent border-none outline-none resize-none
                     text-[17px] text-ink leading-relaxed mt-2
                     placeholder:text-muted/50 caret-fire
                     min-h-[80px]"
          placeholder=""
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit()
            }
          }}
        />

        {/* Goals Card — muncul jika onboarding sudah diisi */}
        {hasOnboarding && <GoalsCard />}
      </div>

      <BottomBar />
    </div>
  )
}
```

---

## KOMPONEN 1 — TopBar.jsx
### Persis foto 1, 2, 3

```jsx
// TopBar.jsx
// Tiga bagian: logo | Today pill | 🔥N ⚙️

export default function TopBar() {
  const { logCount } = useAppStore()
  const [showSettings, setShowSettings] = useState(false)

  return (
    <>
      <div className="flex items-center justify-between px-5 pt-4 pb-2">

        {/* Kiri: Logo */}
        <div className="w-12 h-12">
          <img src="/logo.png" alt="MoCal"
               className="w-full h-full object-contain" />
        </div>

        {/* Tengah: Today pill */}
        <button className="
          bg-white rounded-full px-6 py-2
          text-[15px] font-semibold text-ink
          shadow-sm border border-border/40
        ">
          Today
        </button>

        {/* Kanan: 🔥 count + settings */}
        <div className="
          flex items-center gap-2
          bg-white rounded-full px-4 py-2
          shadow-sm border border-border/40
        ">
          <span className="text-base">🔥</span>
          <span className="text-[15px] font-semibold text-ink">{logCount}</span>
          <button onClick={() => setShowSettings(true)}
            className="ml-1 text-muted hover:text-ink transition-colors">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2">
              <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83
                       2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0
                       0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9
                       19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83
                       -2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0
                       0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a
                       1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83
                       l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51
                       V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65
                       0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A
                       1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2
                       0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>
        </div>
      </div>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  )
}
```

---

## KOMPONEN 2 — BottomBar.jsx
### Persis foto 1 & 2: `🔥 N · C N · P N · F N`

```jsx
// BottomBar.jsx
// Foto 1: 🔥 0 · C 0 · P 0 · F 0
// Foto 2: 🔥 2.557 · C 279 · P 111 · F 104

export default function BottomBar() {
  const { totalKcal, totalC, totalP, totalF } = useAppStore()

  return (
    <div className="
      mx-4 mb-6 mt-2
      bg-white rounded-full
      px-6 py-4
      shadow-sm border border-border/30
      flex items-center justify-center gap-4
    ">
      {/* Kalori */}
      <div className="flex items-center gap-1.5">
        <span className="text-base">🔥</span>
        <span className="text-[15px] font-semibold text-ink">
          {totalKcal > 0 ? totalKcal.toLocaleString('id-ID') : '0'}
        </span>
      </div>

      <span className="text-muted/40 text-lg">·</span>

      {/* Carbs */}
      <div className="flex items-center gap-1">
        <span className="text-[13px] font-bold text-carbs">C</span>
        <span className="text-[15px] font-semibold text-ink">{totalC}</span>
      </div>

      <span className="text-muted/40 text-lg">·</span>

      {/* Protein */}
      <div className="flex items-center gap-1">
        <span className="text-[13px] font-bold text-protein">P</span>
        <span className="text-[15px] font-semibold text-ink">{totalP}</span>
      </div>

      <span className="text-muted/40 text-lg">·</span>

      {/* Fat */}
      <div className="flex items-center gap-1">
        <span className="text-[13px] font-bold text-fat">F</span>
        <span className="text-[15px] font-semibold text-ink">{totalF}</span>
      </div>
    </div>
  )
}
```

---

## KOMPONEN 3 — LogItem.jsx
### Persis foto 2: teks kiri + `XXX cal` kanan (abu-abu)

```jsx
// LogItem.jsx
export default function LogItem({ log }) {
  return (
    <div className="flex items-start justify-between py-3
                    border-b border-border/30 last:border-0">

      {/* Teks input — kiri, bisa multiline */}
      <p className="text-[17px] text-ink leading-relaxed flex-1 pr-6">
        {log.raw_input}
      </p>

      {/* Kalori — kanan, abu-abu, satu baris */}
      <span className="text-[17px] text-muted font-normal whitespace-nowrap
                       tabular-nums pt-0.5">
        {log.total_kcal.toLocaleString('id-ID')} cal
      </span>
    </div>
  )
}
```

---

## KOMPONEN 4 — GoalsCard.jsx
### Persis foto 3: Goals card dengan progress bar + 6 ring chart

```jsx
// GoalsCard.jsx
export default function GoalsCard() {
  const { totalKcal, totalC, totalP, totalF,
          totalSugar, totalFiber, totalSodium,
          goals } = useAppStore()

  const kcalPct    = Math.min((totalKcal  / goals.kcal)   * 100, 100)
  const carbsPct   = Math.min((totalC     / goals.carbs)  * 100, 100)
  const proteinPct = Math.min((totalP     / goals.protein)* 100, 100)
  const fatPct     = Math.min((totalF     / goals.fat)    * 100, 100)
  const sugarPct   = Math.min((totalSugar / goals.sugar)  * 100, 100)
  const fiberPct   = Math.min((totalFiber / goals.fiber)  * 100, 100)
  const sodiumPct  = Math.min((totalSodium/ goals.sodium) * 100, 100)

  // Warna ring: hijau jika di bawah target, merah jika over
  const ringColor = (pct) => pct >= 100 ? '#F44336' : '#4CAF50'

  return (
    <div className="bg-white rounded-2xl p-5 mt-4 shadow-sm border border-border/30">

      {/* Header */}
      <h3 className="text-[17px] font-bold text-ink mb-4">Goals</h3>

      {/* Calories progress */}
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
        {/* Progress bar kuning — PERSIS foto 3 */}
        <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full bg-goal-yellow rounded-full transition-all duration-500"
               style={{ width: `${kcalPct}%` }} />
        </div>
      </div>

      {/* Ring charts — 3 kolom, 2 baris */}
      <div className="grid grid-cols-3 gap-4">
        <RingChart label="Carbs"   value={totalC}      unit="g"
                   pct={carbsPct}   color={ringColor(carbsPct)} />
        <RingChart label="Protein" value={totalP}      unit="g"
                   pct={proteinPct} color={ringColor(proteinPct)} />
        <RingChart label="Fat"     value={totalF}      unit="g"
                   pct={fatPct}     color={ringColor(fatPct)} />
        <RingChart label="Sugar"   value={totalSugar}  unit="g"
                   pct={sugarPct}   color={ringColor(sugarPct)} />
        <RingChart label="Fiber"   value={totalFiber}  unit="g"
                   pct={fiberPct}   color={ringColor(fiberPct)} />
        <RingChart label="Sodium"  value={totalSodium} unit="mg"
                   pct={sodiumPct}  color={ringColor(sodiumPct)} />
      </div>
    </div>
  )
}
```

---

## KOMPONEN 5 — RingChart.jsx
### SVG donut ring — persis foto 3

```jsx
// RingChart.jsx
// Satu ring chart: angka di tengah, label di bawah
// Warna: hijau jika normal, merah jika over target

export default function RingChart({ label, value, unit, pct, color }) {
  const size    = 80
  const stroke  = 7
  const r       = (size - stroke) / 2
  const circ    = 2 * Math.PI * r
  const offset  = circ - (pct / 100) * circ

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Track — abu-abu */}
          <circle
            cx={size/2} cy={size/2} r={r}
            fill="none"
            stroke="#E0E0E0"
            strokeWidth={stroke}
          />
          {/* Progress — warna dari prop */}
          <circle
            cx={size/2} cy={size/2} r={r}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform={`rotate(-90 ${size/2} ${size/2})`}
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        {/* Angka di tengah */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[15px] font-bold text-ink leading-none">
            {value}
          </span>
          <span className="text-[10px] text-muted">{unit}</span>
        </div>
      </div>
      {/* Label di bawah */}
      <span className="text-[12px] text-muted font-medium">{label}</span>
    </div>
  )
}
```

---

## KOMPONEN 6 — SettingsModal.jsx
### Modal overlay — settings + onboarding BMR opsional

```jsx
// SettingsModal.jsx
// Muncul saat icon ⚙️ diklik
// Berisi: Language toggle, Dark mode, BMR onboarding (opsional)

export default function SettingsModal({ onClose }) {
  const { goals, setGoals, hasOnboarding, setHasOnboarding } = useAppStore()
  const { i18n } = useTranslation()
  const [showBMR, setShowBMR] = useState(!hasOnboarding)

  // BMR form state
  const [form, setForm] = useState({
    name: '', age: '', gender: 'male',
    weight: '', height: '', activity: 'light', goal: 'maintain'
  })

  const calcAndSave = () => {
    // Mifflin-St Jeor
    const w = parseFloat(form.weight)
    const h = parseFloat(form.height)
    const a = parseInt(form.age)
    const bmr = form.gender === 'male'
      ? 10*w + 6.25*h - 5*a + 5
      : 10*w + 6.25*h - 5*a - 161

    const mult = { sedentary:1.2, light:1.375, moderate:1.55, active:1.725 }
    const adj  = { lose:-500, maintain:0, gain:+300 }
    const tdee = bmr * mult[form.activity]
    const kcal = Math.round(tdee + adj[form.goal])

    setGoals({
      kcal,
      carbs:   Math.round((kcal * 0.50) / 4),
      protein: Math.round((kcal * 0.30) / 4),
      fat:     Math.round((kcal * 0.20) / 9),
      sugar:   50,    // WHO recommendation default
      fiber:   25,
      sodium:  2300,
    })
    setHasOnboarding(true)
    setShowBMR(false)
  }

  return (
    // Overlay
    <div className="fixed inset-0 z-50 flex items-end justify-center"
         onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />

      {/* Sheet — slide dari bawah */}
      <div className="relative w-full max-w-[430px] bg-white rounded-t-3xl
                      p-6 pb-10 shadow-2xl max-h-[90vh] overflow-y-auto"
           onClick={e => e.stopPropagation()}>

        {/* Handle bar */}
        <div className="w-10 h-1 bg-border rounded-full mx-auto mb-6" />

        {/* ── Settings utama ── */}
        <h2 className="text-[20px] font-bold text-ink mb-6">Settings</h2>

        {/* Language */}
        <div className="flex items-center justify-between py-4
                        border-b border-border/40">
          <span className="text-[15px] font-medium text-ink">Language</span>
          <div className="flex items-center bg-gray-100 rounded-full p-1">
            <button onClick={() => { i18n.changeLanguage('id'); localStorage.setItem('mocal_lang','id') }}
              className={`px-3 py-1 rounded-full text-sm font-semibold transition-all
                ${i18n.language === 'id' ? 'bg-white shadow text-ink' : 'text-muted'}`}>
              ID
            </button>
            <button onClick={() => { i18n.changeLanguage('en'); localStorage.setItem('mocal_lang','en') }}
              className={`px-3 py-1 rounded-full text-sm font-semibold transition-all
                ${i18n.language === 'en' ? 'bg-white shadow text-ink' : 'text-muted'}`}>
              EN
            </button>
          </div>
        </div>

        {/* History link */}
        <button onClick={() => { navigate('/history'); onClose() }}
          className="w-full flex items-center justify-between py-4
                     border-b border-border/40">
          <span className="text-[15px] font-medium text-ink">Riwayat / History</span>
          <span className="text-muted">›</span>
        </button>

        {/* BMR / Goals section */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-[17px] font-bold text-ink">
              {hasOnboarding ? 'Edit Goals' : 'Set Your Goals'}
            </h3>
            {!hasOnboarding && (
              <span className="text-xs bg-fire/10 text-fire px-2 py-1 rounded-full font-medium">
                Opsional
              </span>
            )}
          </div>

          {/* BMR Form */}
          <div className="flex flex-col gap-3">
            {/* Nama */}
            <input type="text" placeholder="Nama"
              value={form.name}
              onChange={e => setForm(f=>({...f, name:e.target.value}))}
              className="w-full h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                         text-sm focus:border-fire focus:outline-none transition-colors"/>

            {/* Usia + Gender */}
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="Usia"
                value={form.age}
                onChange={e => setForm(f=>({...f, age:e.target.value}))}
                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                           text-sm focus:border-fire focus:outline-none transition-colors"/>
              <select value={form.gender}
                onChange={e => setForm(f=>({...f, gender:e.target.value}))}
                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                           text-sm focus:border-fire focus:outline-none transition-colors">
                <option value="male">Laki-laki</option>
                <option value="female">Perempuan</option>
              </select>
            </div>

            {/* Berat + Tinggi */}
            <div className="grid grid-cols-2 gap-3">
              <input type="number" placeholder="Berat (kg)"
                value={form.weight}
                onChange={e => setForm(f=>({...f, weight:e.target.value}))}
                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                           text-sm focus:border-fire focus:outline-none transition-colors"/>
              <input type="number" placeholder="Tinggi (cm)"
                value={form.height}
                onChange={e => setForm(f=>({...f, height:e.target.value}))}
                className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                           text-sm focus:border-fire focus:outline-none transition-colors"/>
            </div>

            {/* Aktivitas */}
            <select value={form.activity}
              onChange={e => setForm(f=>({...f, activity:e.target.value}))}
              className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                         text-sm focus:border-fire focus:outline-none transition-colors">
              <option value="sedentary">Sedentary — Jarang bergerak</option>
              <option value="light">Ringan — Olahraga 1–3x/minggu</option>
              <option value="moderate">Moderat — Olahraga 3–5x/minggu</option>
              <option value="active">Aktif — Latihan berat</option>
            </select>

            {/* Goal */}
            <select value={form.goal}
              onChange={e => setForm(f=>({...f, goal:e.target.value}))}
              className="h-11 px-4 bg-gray-50 rounded-xl border border-border/50
                         text-sm focus:border-fire focus:outline-none transition-colors">
              <option value="lose">Turun Berat — Defisit 500 kkal</option>
              <option value="maintain">Jaga Berat — Sesuai TDEE</option>
              <option value="gain">Naik Berat — Surplus 300 kkal</option>
            </select>

            <button onClick={calcAndSave}
              className="w-full h-12 bg-fire text-white rounded-xl
                         font-bold text-[15px]
                         hover:opacity-90 active:scale-95 transition-all mt-1">
              Simpan Goals 🔥
            </button>

            {hasOnboarding && (
              <button onClick={() => { setGoals(null); setHasOnboarding(false) }}
                className="w-full h-10 text-sm text-muted hover:text-ink transition-colors">
                Hapus Goals
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}
```

---

## KOMPONEN 7 — LoadingRow.jsx

```jsx
// LoadingRow.jsx — inline di antara log items dan textarea
export default function LoadingRow() {
  const { i18n } = useTranslation()
  const msgs = {
    id: ['Meownggu...', 'Lagi nyari di dapur...', 'Ngitung kalorinya...', 'Bentar ya... 🐟'],
    en: ['Miaww...', 'Sniffing calories...', 'One paw at a time...', 'Almost there, meow...']
  }
  const lang = i18n.language.startsWith('id') ? 'id' : 'en'
  const [msg] = useState(() => {
    const arr = msgs[lang]
    return arr[Math.floor(Math.random() * arr.length)]
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
        {[0,150,300].map(d => (
          <div key={d} className="w-1.5 h-1.5 rounded-full bg-fire/30 animate-bounce"
               style={{ animationDelay: `${d}ms` }} />
        ))}
      </div>
    </div>
  )
}
```

---

## ZUSTAND STORE — appStore.js

```js
// src/stores/appStore.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAppStore = create(
  persist(
    (set, get) => ({
      // Log makanan hari ini
      logs: [],            // [{ raw_input, total_kcal, items, logged_at }]
      isLoading: false,

      // Totals (dihitung dari logs)
      get totalKcal()  { return get().logs.reduce((s,l) => s + (l.total_kcal || 0), 0) },
      get totalC()     { return Math.round(get().logs.reduce((s,l) => s + (l.total_carbs  || 0), 0)) },
      get totalP()     { return Math.round(get().logs.reduce((s,l) => s + (l.total_protein|| 0), 0)) },
      get totalF()     { return Math.round(get().logs.reduce((s,l) => s + (l.total_fat    || 0), 0)) },
      get totalSugar() { return Math.round(get().logs.reduce((s,l) => s + (l.total_sugar  || 0), 0)) },
      get totalFiber() { return Math.round(get().logs.reduce((s,l) => s + (l.total_fiber  || 0), 0)) },
      get totalSodium(){ return Math.round(get().logs.reduce((s,l) => s + (l.total_sodium || 0), 0)) },
      get logCount()   { return get().logs.length },

      // Goals dari onboarding BMR
      hasOnboarding: false,
      goals: {
        kcal: 2000, carbs: 250, protein: 150, fat: 67,
        sugar: 50, fiber: 25, sodium: 2300
      },

      // Actions
      addLog:         (log)    => set(s => ({ logs: [...s.logs, log] })),
      clearToday:     ()       => set({ logs: [] }),
      setLoading:     (v)      => set({ isLoading: v }),
      setGoals:       (goals)  => set({ goals }),
      setHasOnboarding:(v)     => set({ hasOnboarding: v }),
    }),
    {
      name: 'mocal-storage',   // key di localStorage
      // Reset logs setiap hari baru
      onRehydrateStorage: () => (state) => {
        if (state) {
          const today = new Date().toDateString()
          const saved = localStorage.getItem('mocal-date')
          if (saved !== today) {
            state.logs = []
            localStorage.setItem('mocal-date', today)
          }
        }
      }
    }
  )
)
```

---

## API SERVICE — api.js

```js
// src/services/api.js
import axios from 'axios'
import { useAppStore } from '@/stores/appStore'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export async function submitLog(text) {
  const store = useAppStore.getState()
  store.setLoading(true)
  try {
    const { data } = await api.post('/api/estimate', { text })
    // data: { items: [{name, kcal, protein_g, carbs_g, fat_g, ...}], total_kcal }
    store.addLog({
      raw_input:     text,
      total_kcal:    data.total_kcal    || 0,
      total_carbs:   data.total_carbs   || 0,
      total_protein: data.total_protein || 0,
      total_fat:     data.total_fat     || 0,
      total_sugar:   data.total_sugar   || 0,
      total_fiber:   data.total_fiber   || 0,
      total_sodium:  data.total_sodium  || 0,
      items:         data.items         || [],
      logged_at:     new Date().toISOString(),
    })
    return data
  } finally {
    store.setLoading(false)
  }
}
```

---

## HISTORY PAGE — HistoryPage.jsx

```jsx
// Tampilan list semua log — diakses dari Settings modal
export default function HistoryPage() {
  return (
    <div className="min-h-screen bg-bg max-w-[430px] mx-auto">
      <TopBar />

      <div className="px-5 pt-4 pb-24">
        <h2 className="text-[20px] font-bold text-ink mb-4">Riwayat</h2>

        {/* Group by date */}
        {groupedLogs.map(group => (
          <div key={group.date} className="mb-6">
            <p className="text-xs font-semibold text-muted uppercase
                          tracking-widest mb-2">
              {group.dateLabel}
            </p>
            {group.logs.map((log, i) => (
              <div key={i} className="flex items-start justify-between
                                      py-3 border-b border-border/30">
                <p className="text-[15px] text-ink flex-1 pr-4 leading-relaxed
                               line-clamp-2">
                  {log.raw_input}
                </p>
                <span className="text-[15px] text-muted tabular-nums whitespace-nowrap">
                  {log.total_kcal} cal
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## DESKTOP LAYOUT

Di desktop (≥ 768px), layout berubah dari full-width menjadi dua kolom:

```
┌─────────────────────────────────────────────────────────┐
│              TopBar (max-width 1200px centered)          │
├──────────────────────────┬──────────────────────────────┤
│   LOG AREA (flex-1)      │   GOALS PANEL (380px)        │
│                          │   sticky top                 │
│   LogItem                │   GoalsCard selalu tampil    │
│   LogItem                │   (jika onboarding selesai)  │
│   LoadingRow             │                              │
│   textarea               │   Jika belum onboarding:     │
│                          │   prompt "Set your goals →"  │
│   BottomBar              │                              │
└──────────────────────────┴──────────────────────────────┘
```

```jsx
// MainApp.jsx — desktop wrapper
<div className="min-h-screen bg-bg">
  <div className="max-w-[1100px] mx-auto">
    <TopBar />

    <div className="flex gap-6 px-6 pt-4">
      {/* Kiri: log area */}
      <div className="flex-1 flex flex-col min-h-[calc(100vh-80px)]">
        {/* ... log items + textarea ... */}
        <div className="mt-auto">
          <BottomBar />
        </div>
      </div>

      {/* Kanan: goals panel — hanya desktop */}
      <div className="hidden md:block w-[360px] flex-shrink-0">
        <div className="sticky top-6">
          {hasOnboarding
            ? <GoalsCard />
            : <div className="bg-white rounded-2xl p-5 border border-border/30
                              text-center">
                <p className="text-muted text-sm mb-3">
                  Set your goals to track macros
                </p>
                <button onClick={() => setShowSettings(true)}
                  className="text-fire font-semibold text-sm hover:underline">
                  Set Goals →
                </button>
              </div>
          }
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## ROUTING — App.jsx

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainApp     from '@/pages/MainApp'
import HistoryPage from '@/pages/HistoryPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"        element={<MainApp />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="*"        element={<MainApp />} />
      </Routes>
    </BrowserRouter>
  )
}
```

**Tidak ada login. Tidak ada route guard. Langsung bisa pakai.**

---

## CHECKLIST

- [ ] Tailwind config dengan warna: bg, surface, muted, fire, carbs, protein, fat, goal.*
- [ ] Font Inter dari Google Fonts
- [ ] wiggle keyframe di tailwind.config
- [ ] logo.png di `public/`
- [ ] i18n setup (id.json + en.json) — loading messages dalam dua bahasa
- [ ] `zustand` + `zustand/middleware` terinstall
- [ ] Auto-reset logs setiap hari baru (cek localStorage date)
- [ ] TopBar: logo | Today | 🔥N ⚙️ — **persis foto 1**
- [ ] LogItem: teks kiri + `XXX cal` kanan abu-abu — **persis foto 2**
- [ ] BottomBar: `🔥 N · C N · P N · F N` — **persis foto 1 & 2**
- [ ] GoalsCard: progress bar kuning + 6 ring chart — **persis foto 3**
- [ ] RingChart: hijau jika normal, merah jika over target
- [ ] SettingsModal: sheet dari bawah, berisi language + history + BMR form
- [ ] BMR form di Settings: opsional, bisa skip
- [ ] LoadingRow: 🐱 animasi wiggle + bounce dots + pesan random
- [ ] Desktop: dua kolom (log kiri + goals panel kanan sticky)
- [ ] Tidak ada login, tidak ada route guard