import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainApp from '@/pages/MainApp'
import HistoryPage from '@/pages/HistoryPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="*" element={<MainApp />} />
      </Routes>
    </BrowserRouter>
  )
}
