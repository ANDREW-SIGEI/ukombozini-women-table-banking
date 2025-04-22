import React from "react";

function StatsCard({ icon, title, value, subtitle, trend, percentage, color, onClick, linkText }) {
  const colorClasses = {
    blue: {
      bg: "bg-blue-100",
      text: "text-blue-700",
      hover: "group-hover:bg-blue-200",
      light: "bg-blue-500/20",
      border: "border-blue-400/30",
      linkText: "text-blue-700",
      linkHover: "hover:text-blue-800",
      trend: {
        up: "text-green-500",
        down: "text-red-500",
        stable: "text-gray-500"
      }
    },
    green: {
      bg: "bg-green-100",
      text: "text-green-700",
      hover: "group-hover:bg-green-200",
      light: "bg-green-500/20",
      border: "border-green-400/30",
      linkText: "text-green-700",
      linkHover: "hover:text-green-800",
      trend: {
        up: "text-green-500",
        down: "text-red-500",
        stable: "text-gray-500"
      }
    },
    yellow: {
      bg: "bg-yellow-100",
      text: "text-yellow-700",
      hover: "group-hover:bg-yellow-200",
      light: "bg-yellow-500/20",
      border: "border-yellow-400/30",
      linkText: "text-yellow-700",
      linkHover: "hover:text-yellow-800",
      trend: {
        up: "text-green-500",
        down: "text-red-500",
        stable: "text-gray-500"
      }
    },
    purple: {
      bg: "bg-purple-100",
      text: "text-purple-700",
      hover: "group-hover:bg-purple-200",
      light: "bg-purple-500/20",
      border: "border-purple-400/30",
      linkText: "text-purple-700",
      linkHover: "hover:text-purple-800",
      trend: {
        up: "text-green-500",
        down: "text-red-500",
        stable: "text-gray-500"
      }
    },
  };

  return (
    <button
      onClick={onClick}
      className="bg-white p-6 rounded-xl shadow-lg w-full hover:cursor-pointer group transition-all duration-300 hover:-translate-y-1 border border-gray-200"
    >
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-full transition-colors ${colorClasses[color].bg} ${colorClasses[color].text} ${colorClasses[color].hover}`}>
          <i className={`fas fa-${icon} text-xl`}></i>
        </div>
        
        {trend && (
          <div className="flex items-center">
            <i className={`fas fa-${trend === 'up' ? 'arrow-up' : trend === 'down' ? 'arrow-down' : 'equals'} ${colorClasses[color].trend[trend]} mr-1`}></i>
            <span className={`text-sm font-medium ${colorClasses[color].trend[trend]}`}>
              {percentage}%
            </span>
          </div>
        )}
        </div>
      
      <div className="mt-4">
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <h3 className="text-2xl font-bold text-gray-800 mt-1">{value}</h3>
        {subtitle && (
          <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
        )}
      </div>
      
      {linkText && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <span className={`${colorClasses[color].linkText} text-sm font-semibold ${colorClasses[color].linkHover} hover:underline`}>
            {linkText} <i className="fas fa-chevron-right ml-1 text-xs"></i>
          </span>
        </div>
      )}
    </button>
  );
}

export default StatsCard;
