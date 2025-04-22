import React, { useState } from "react";

function ActionCenter({ onNavigate }) {
  const [activeTab, setActiveTab] = useState("tasks");

  // Sample data
  const tasks = [
    { id: 1, title: "Review loan application for Mary Njoki", priority: "high", dueDate: "Today" },
    { id: 2, title: "Prepare for monthly group meeting", priority: "medium", dueDate: "Tomorrow" },
    { id: 3, title: "Collect overdue loan payment from Sarah", priority: "high", dueDate: "Overdue" },
    { id: 4, title: "Update quarterly financial report", priority: "low", dueDate: "Apr 30" },
  ];

  const notifications = [
    { id: 1, type: "loan", message: "New loan application from Lucy Wangari", time: "2 hours ago", read: false },
    { id: 2, type: "payment", message: "Jane Wambui made a loan payment of KES 2,500", time: "3 hours ago", read: false },
    { id: 3, type: "system", message: "System backup completed successfully", time: "Yesterday", read: true },
    { id: 4, type: "meeting", message: "Monthly meeting reminder for tomorrow", time: "Yesterday", read: true },
  ];

  const quickActions = [
    { id: 1, title: "Register Member", icon: "user-plus", route: "members", color: "bg-blue-500/60" },
    { id: 2, title: "Record Payment", icon: "money-bill-wave", route: "collections", color: "bg-green-500/60" },
    { id: 3, title: "Process Loan", icon: "hand-holding-usd", route: "loans", color: "bg-yellow-500/60" },
    { id: 4, title: "Schedule Meeting", icon: "calendar-plus", route: "schedule-meeting", color: "bg-purple-500/60" },
    { id: 5, title: "Generate Report", icon: "file-alt", route: "banking-reports", color: "bg-indigo-500/60" },
    { id: 6, title: "Add Savings", icon: "piggy-bank", route: "savings", color: "bg-teal-500/60" },
  ];

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-white">Action Center</h3>
        <div className="flex bg-white/20 rounded-lg p-1">
          {["tasks", "notifications", "actions"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "text-blue-100 hover:text-white"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {activeTab === "tasks" && (
        <div className="space-y-4">
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {tasks.map((task) => (
              <div 
                key={task.id} 
                className="bg-white/20 p-3 rounded-lg flex items-start justify-between hover:bg-white/30 transition-colors"
              >
                <div className="flex items-start">
                  <div 
                    className={`mt-1 h-4 w-4 rounded-full mr-3 flex-shrink-0 ${
                      task.priority === 'high' ? 'bg-red-500' : 
                      task.priority === 'medium' ? 'bg-yellow-500' : 
                      'bg-green-500'
                    }`}
                  ></div>
                  <div>
                    <p className="text-white text-sm font-medium">{task.title}</p>
                    <p className="text-blue-200 text-xs">Due: {task.dueDate}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="text-blue-300 hover:text-white transition-colors">
                    <i className="fas fa-check"></i>
                  </button>
                  <button className="text-blue-300 hover:text-white transition-colors">
                    <i className="fas fa-ellipsis-v"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end">
            <button 
              onClick={() => {}}
              className="bg-blue-600/80 text-white px-4 py-2 rounded-lg hover:bg-blue-700/80 transition-colors text-sm font-medium flex items-center"
            >
              <i className="fas fa-plus mr-2"></i>
              Add Task
            </button>
          </div>
        </div>
      )}

      {activeTab === "notifications" && (
        <div className="space-y-4">
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {notifications.map((notification) => (
              <div 
                key={notification.id} 
                className={`p-3 rounded-lg flex items-start justify-between transition-colors ${
                  notification.read ? 'bg-white/10' : 'bg-white/20 border-l-4 border-blue-500'
                }`}
              >
                <div className="flex items-start">
                  <div className={`p-2 rounded-full mr-3 flex-shrink-0 ${
                    notification.type === 'loan' ? 'bg-green-500/20 text-green-400' :
                    notification.type === 'payment' ? 'bg-blue-500/20 text-blue-400' :
                    notification.type === 'meeting' ? 'bg-purple-500/20 text-purple-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    <i className={`fas fa-${
                      notification.type === 'loan' ? 'hand-holding-usd' :
                      notification.type === 'payment' ? 'money-bill-wave' :
                      notification.type === 'meeting' ? 'calendar' :
                      'bell'
                    } text-sm`}></i>
                  </div>
                  <div>
                    <p className="text-white text-sm">{notification.message}</p>
                    <p className="text-blue-200 text-xs">{notification.time}</p>
                  </div>
                </div>
                <button className="text-blue-300 hover:text-white transition-colors">
                  <i className="fas fa-times"></i>
                </button>
              </div>
            ))}
          </div>

          <div className="flex justify-between">
            <button 
              onClick={() => {}}
              className="text-blue-300 hover:text-white transition-colors text-sm"
            >
              Mark all as read
            </button>
            <button 
              onClick={() => {}}
              className="text-blue-300 hover:text-white transition-colors text-sm"
            >
              View all notifications
            </button>
          </div>
        </div>
      )}

      {activeTab === "actions" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-1">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => onNavigate(action.route)}
                className={`${action.color} hover:opacity-90 transition-colors p-4 rounded-lg flex items-center`}
              >
                <div className="bg-white/20 p-2 rounded-lg mr-3">
                  <i className={`fas fa-${action.icon} text-white`}></i>
                </div>
                <span className="text-white text-sm font-medium">{action.title}</span>
              </button>
            ))}
          </div>

          <div className="bg-gradient-to-r from-blue-600/30 to-indigo-600/30 p-4 rounded-lg border border-blue-500/30">
            <div className="flex items-start">
              <div className="bg-blue-500/20 p-2 rounded-lg mr-3">
                <i className="fas fa-lightbulb text-yellow-400"></i>
              </div>
              <div>
                <p className="text-white text-sm font-medium">Quick Tip</p>
                <p className="text-blue-200 text-xs mt-1">
                  Use the "Record Payment" action to quickly add loan repayments or savings deposits without navigating through multiple screens.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ActionCenter; 