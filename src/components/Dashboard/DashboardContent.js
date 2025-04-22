import React, { useState, useEffect } from "react";
import StatsCard from "../StatsCard";
import MeetingCard from "./MeetingCard";
import FinancialOverview from "./FinancialOverview";
import MemberOverview from "./MemberOverview";
import ActionCenter from "./ActionCenter";
import CalendarWidget from "./CalendarWidget";

function DashboardContent({ onNavigate }) {
  const [timeRange, setTimeRange] = useState("month");
  const [showMenu, setShowMenu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState(2);
  
  // Sample dashboard data
  const dashboardData = {
    members: {
      total: 127,
      active: 118,
      new: 5,
      trend: "up",
      percentage: 8.2
    },
    loans: {
      total: 43,
      active: 36,
      amount: "KES 854,320",
      trend: "up",
      percentage: 12.4
    },
    savings: {
      total: "KES 1,625,450",
      contributions: "KES 78,500",
      trend: "up",
      percentage: 5.7
    },
    groups: {
      total: 4,
      active: 4,
      new: 1,
      trend: "stable",
      percentage: 0
    }
  };

  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  const handleAddNew = () => {
    setShowMenu(!showMenu);
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-wide"
            style={{ textShadow: "0 2px 4px rgba(0,0,0,0.3)" }}>
            Dashboard
        </h1>
          <p className="text-blue-200 mt-2">Welcome to Ukombozini Table Banking</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="relative">
              <button className="bg-white/20 p-2 rounded-full hover:bg-white/30 transition-colors text-white">
                <i className="fas fa-bell"></i>
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs">
                    {notifications}
                  </span>
                )}
              </button>
            </div>
            <div>
              <button className="bg-white/20 p-2 rounded-full hover:bg-white/30 transition-colors text-white">
                <i className="fas fa-cog"></i>
              </button>
            </div>
          </div>
          
          <select 
            className="bg-white/20 border border-blue-400/30 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          
          <div className="relative">
            <button 
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg shadow-lg transform transition hover:-translate-y-1 font-medium text-sm flex items-center"
              onClick={handleAddNew}
            >
          <i className="fas fa-plus mr-2"></i>
          Add New
        </button>
            
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-white z-10 py-2 border border-gray-200">
                <button 
                  className="w-full text-left px-4 py-2 hover:bg-blue-100 text-blue-800"
                  onClick={() => {
                    onNavigate("members");
                    setShowMenu(false);
                  }}
                >
                  <i className="fas fa-user mr-2"></i> New Member
                </button>
                <button 
                  className="w-full text-left px-4 py-2 hover:bg-blue-100 text-blue-800"
                  onClick={() => {
                    onNavigate("loans");
                    setShowMenu(false);
                  }}
                >
                  <i className="fas fa-hand-holding-usd mr-2"></i> New Loan
                </button>
                <button 
                  className="w-full text-left px-4 py-2 hover:bg-blue-100 text-blue-800"
                  onClick={() => {
                    onNavigate("schedule-meeting");
                    setShowMenu(false);
                  }}
                >
                  <i className="fas fa-calendar-plus mr-2"></i> New Meeting
                </button>
                <button 
                  className="w-full text-left px-4 py-2 hover:bg-blue-100 text-blue-800"
                  onClick={() => {
                    onNavigate("groups");
                    setShowMenu(false);
                  }}
                >
                  <i className="fas fa-users mr-2"></i> New Group
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {loading ? (
        // Loading state
        <div className="py-20 flex flex-col items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
          <p className="mt-4 text-blue-300">Loading dashboard data...</p>
        </div>
      ) : (
        <>
          {/* Stats Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          icon="users"
              title="Members"
              value={dashboardData.members.total.toString()}
              subtitle={`Active: ${dashboardData.members.active}`}
              trend={dashboardData.members.trend}
              percentage={dashboardData.members.percentage}
          color="blue"
          onClick={() => onNavigate("members")}
          linkText="See all members"
        />
        <StatsCard
          icon="money-bill-wave"
              title="Active Loans"
              value={dashboardData.loans.active.toString()}
              subtitle={dashboardData.loans.amount}
              trend={dashboardData.loans.trend}
              percentage={dashboardData.loans.percentage}
          color="green"
          onClick={() => onNavigate("loans")}
          linkText="View loans"
        />
        <StatsCard
              icon="piggy-bank"
              title="Total Savings"
              value={dashboardData.savings.total}
              subtitle={`This month: ${dashboardData.savings.contributions}`}
              trend={dashboardData.savings.trend}
              percentage={dashboardData.savings.percentage}
          color="yellow"
              onClick={() => onNavigate("savings")}
              linkText="View savings"
        />
        <StatsCard
              icon="layer-group"
              title="Active Groups"
              value={dashboardData.groups.total.toString()}
              subtitle={`New: ${dashboardData.groups.new}`}
              trend={dashboardData.groups.trend}
              percentage={dashboardData.groups.percentage}
          color="purple"
              onClick={() => onNavigate("groups")}
              linkText="View groups"
        />
      </div>

          {/* Main Dashboard Content */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            {/* First Column - 2 spans */}
            <div className="xl:col-span-2 space-y-6">
              {/* Financial Overview */}
              <FinancialOverview onNavigate={onNavigate} />
              
              {/* Member Overview */}
              <MemberOverview onNavigate={onNavigate} />
            </div>
            
            {/* Second Column - 1 span */}
            <div className="space-y-6">
              {/* Action Center */}
              <ActionCenter onNavigate={onNavigate} />
            </div>
            
            {/* Third Column - 1 span */}
            <div className="space-y-6">
              {/* Calendar */}
              <CalendarWidget onNavigate={onNavigate} />
              
              {/* Meeting Card (smaller version) */}
              <div className="hidden md:block">
                <MeetingCard onNavigate={onNavigate} />
              </div>
            </div>
          </div>
          
          {/* Footer Information */}
          <div className="flex flex-col md:flex-row justify-between items-center p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 mt-4">
            <div className="text-blue-200 text-sm">
              <p>Ukombozini Women Table Banking</p>
              <p>Last data update: {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}</p>
            </div>
            <div className="flex space-x-4 mt-4 md:mt-0">
              <button className="text-blue-300 hover:text-white transition-colors">
                <i className="fas fa-life-ring mr-1"></i> Support
              </button>
              <button className="text-blue-300 hover:text-white transition-colors">
                <i className="fas fa-question-circle mr-1"></i> Help
              </button>
              <button className="text-blue-300 hover:text-white transition-colors">
                <i className="fas fa-cog mr-1"></i> Settings
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardContent;
