import { useState, useEffect } from 'react'

export default function DatePickerModal({ isOpen, onClose, onSelectDate, selectedDate }) {
    const [viewDate, setViewDate] = useState(selectedDate || new Date())

    // Reset view date when modal opens or selectedDate changes
    useEffect(() => {
        if (isOpen) {
            setViewDate(selectedDate || new Date())
        }
    }, [isOpen, selectedDate])

    // Get days in month
    const getDaysInMonth = (date) => {
        const year = date.getFullYear()
        const month = date.getMonth()
        const firstDay = new Date(year, month, 1)
        const lastDay = new Date(year, month + 1, 0)
        const daysInMonth = lastDay.getDate()
        const startingDay = firstDay.getDay()
        
        return { daysInMonth, startingDay, year, month }
    }

    const { daysInMonth, startingDay, year, month } = getDaysInMonth(viewDate)

    // Month names
    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    // Day names
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    // Navigate to previous month
    const prevMonth = () => {
        setViewDate(new Date(year, month - 1, 1))
    }

    // Navigate to next month
    const nextMonth = () => {
        setViewDate(new Date(year, month + 1, 1))
    }

    // Check if date is today
    const isToday = (day) => {
        const today = new Date()
        return day === today.getDate() && 
               month === today.getMonth() && 
               year === today.getFullYear()
    }

    // Check if date is selected
    const isSelected = (day) => {
        if (!selectedDate) return false
        return day === selectedDate.getDate() && 
               month === selectedDate.getMonth() && 
               year === selectedDate.getFullYear()
    }

    // Handle date selection
    const handleDateClick = (day) => {
        const newDate = new Date(year, month, day)
        onSelectDate(newDate)
        onClose()
    }

    // Go to today
    const goToToday = () => {
        const today = new Date()
        setViewDate(today)
        onSelectDate(today)
        onClose()
    }

    // Generate calendar days
    const renderDays = () => {
        const days = []
        
        // Empty cells for days before the first day of the month
        for (let i = 0; i < startingDay; i++) {
            days.push(<div key={`empty-${i}`} className="h-10"></div>)
        }
        
        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const isTodayDate = isToday(day)
            const isSelectedDate = isSelected(day)
            
            days.push(
                <button
                    key={day}
                    onClick={() => handleDateClick(day)}
                    className={`
                        h-10 w-full rounded-lg font-medium text-sm
                        transition-all duration-200
                        hover:bg-[#df6620]/10
                        ${isSelectedDate 
                            ? 'bg-[#df6620] text-white font-bold' 
                            : isTodayDate 
                                ? 'border-2 border-[#df6620] text-[#df6620] font-bold' 
                                : 'text-slate-700'
                        }
                    `}
                >
                    {day}
                </button>
            )
        }
        
        return days
    }

    if (!isOpen) return null

    return (
        <>
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                onClick={onClose}
            />
            
            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div 
                    className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden"
                    onClick={e => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="bg-[#df6620] text-white p-4">
                        <div className="flex items-center justify-between">
                            <button 
                                onClick={prevMonth}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <polyline points="15 18 9 12 15 6"></polyline>
                                </svg>
                            </button>
                            
                            <h3 className="text-lg font-bold">
                                {monthNames[month]} {year}
                            </h3>
                            
                            <button 
                                onClick={nextMonth}
                                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <polyline points="9 18 15 12 9 6"></polyline>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    {/* Day names */}
                    <div className="grid grid-cols-7 gap-1 p-4 pb-2">
                        {dayNames.map(day => (
                            <div key={day} className="h-10 flex items-center justify-center text-xs font-medium text-slate-400">
                                {day}
                            </div>
                        ))}
                    </div>
                    
                    {/* Calendar grid */}
                    <div className="grid grid-cols-7 gap-1 px-4 pb-4">
                        {renderDays()}
                    </div>
                    
                    {/* Footer */}
                    <div className="border-t border-slate-100 p-4 bg-slate-50">
                        <div className="flex items-center justify-between">
                            <button
                                onClick={goToToday}
                                className="text-sm font-medium text-[#df6620] hover:text-[#df6620]/80 transition-colors"
                            >
                                Go to Today
                            </button>
                            <button
                                onClick={onClose}
                                className="text-sm font-medium text-slate-500 hover:text-slate-700 transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
