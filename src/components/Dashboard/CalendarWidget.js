import React, { useState } from "react";

function CalendarWidget({ onNavigate }) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Sample events data
  const events = [
    { id: 1, title: "Monthly Group Meeting", date: "2024-04-15", type: "meeting" },
    { id: 2, title: "Loan Committee Review", date: "2024-04-18", type: "committee" },
    { id: 3, title: "Loan Disbursement", date: "2024-04-20", type: "finance" },
    { id: 4, title: "Executive Committee", date: "2024-04-25", type: "meeting" },
    { id: 5, title: "Financial Training", date: "2024-04-28", type: "training" },
  ];
  
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  
  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  
  // Get days in month for the calendar
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayOfMonth = new Date(year, month, 1).getDay();
    
    const days = [];
    
    // Previous month days
    for (let i = firstDayOfMonth - 1; i >= 0; i--) {
      const prevMonthDay = new Date(year, month, 0).getDate() - i;
      days.push({ 
        day: prevMonthDay, 
        currentMonth: false, 
        date: new Date(year, month - 1, prevMonthDay) 
      });
    }
    
    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({ 
        day: i, 
        currentMonth: true, 
        date: new Date(year, month, i),
        today: new Date(year, month, i).toDateString() === new Date().toDateString()
      });
    }
    
    // Next month days
    const totalCells = Math.ceil(days.length / 7) * 7;
    const nextMonthDays = totalCells - days.length;
    
    for (let i = 1; i <= nextMonthDays; i++) {
      days.push({ 
        day: i, 
        currentMonth: false, 
        date: new Date(year, month + 1, i) 
      });
    }
    
    return days;
  };

  const days = getDaysInMonth(currentMonth);
  
  // Format date for comparison with events
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  // Get events for a specific day
  const getEventsForDay = (date) => {
    const formattedDate = formatDate(date);
    return events.filter(event => event.date === formattedDate);
  };
  
  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };
  
  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };
  
  // Get upcoming events (next 7 days)
  const today = new Date();
  const nextWeek = new Date(today);
  nextWeek.setDate(nextWeek.getDate() + 7);
  
  const upcomingEvents = events.filter(event => {
    const eventDate = new Date(event.date);
    return eventDate >= today && eventDate <= nextWeek;
  }).sort((a, b) => new Date(a.date) - new Date(b.date));

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-white">Calendar</h3>
        <div className="flex items-center space-x-2">
          <button 
            onClick={prevMonth}
            className="text-blue-300 hover:text-white transition-colors p-1"
          >
            <i className="fas fa-chevron-left"></i>
          </button>
          <span className="text-white font-medium">
            {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
          </span>
          <button 
            onClick={nextMonth}
            className="text-blue-300 hover:text-white transition-colors p-1"
          >
            <i className="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
      
      {/* Calendar Grid */}
      <div className="mb-4">
        {/* Days of week header */}
        <div className="grid grid-cols-7 mb-2">
          {daysOfWeek.map(day => (
            <div key={day} className="text-center text-blue-300 text-xs py-1">
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar days */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => {
            const dayEvents = getEventsForDay(day.date);
            return (
              <div 
                key={index} 
                className={`p-1 text-center text-sm rounded-md ${
                  day.currentMonth 
                    ? day.today
                      ? 'bg-blue-600/30 text-white' 
                      : 'bg-white/10 text-white'
                    : 'text-blue-300/50'
                } ${dayEvents.length > 0 ? 'border border-blue-500/50' : ''}`}
              >
                <div className="relative">
                  {day.day}
                  {dayEvents.length > 0 && (
                    <div className="absolute -top-1 -right-1 h-2 w-2 bg-blue-500 rounded-full"></div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Upcoming Events */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-white font-medium">Upcoming Events</h4>
          <button 
            onClick={() => onNavigate("meetings")}
            className="text-blue-300 hover:text-white transition-colors text-xs"
          >
            View All
          </button>
        </div>
        
        <div className="space-y-2 max-h-32 overflow-y-auto pr-1">
          {upcomingEvents.length > 0 ? (
            upcomingEvents.map(event => (
              <div 
                key={event.id} 
                className="flex items-center p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
              >
                <div className={`w-2 h-10 mr-3 rounded-sm ${
                  event.type === 'meeting' ? 'bg-blue-500' :
                  event.type === 'committee' ? 'bg-purple-500' :
                  event.type === 'finance' ? 'bg-green-500' : 
                  'bg-yellow-500'
                }`}></div>
                <div className="flex-1">
                  <p className="text-white text-sm">{event.title}</p>
                  <p className="text-blue-200 text-xs">
                    {new Date(event.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </p>
                </div>
                <button className="text-blue-300 hover:text-white p-1">
                  <i className="fas fa-eye"></i>
                </button>
              </div>
            ))
          ) : (
            <div className="text-center py-3 text-blue-200 text-sm">
              No upcoming events in the next 7 days
            </div>
          )}
        </div>
        
        <div className="text-center mt-4">
          <button
            onClick={() => onNavigate("schedule-meeting")}
            className="bg-blue-600/80 text-white px-4 py-2 rounded-lg hover:bg-blue-700/80 transition-colors text-sm font-medium inline-flex items-center"
          >
            <i className="fas fa-calendar-plus mr-2"></i>
            Schedule Event
          </button>
        </div>
      </div>
    </div>
  );
}

export default CalendarWidget; 