"use client";
import React from "react";

function MainComponent() {
  const [activeRoute, setActiveRoute] = useState("dashboard");
  const navigate = useNavigate();

  const routes = [
    {
      path: "/dashboard-v2",
      icon: "chart-line",
      label: "Enhanced Dashboard",
      color: "blue",
    },
    {
      path: "/members",
      icon: "user",
      label: "Member Management",
      color: "blue",
    },
    {
      path: "/loans",
      icon: "hand-holding-usd",
      label: "Loan Management",
      color: "green",
    },
    {
      path: "/savings",
      icon: "piggy-bank",
      label: "Savings Management",
      color: "yellow",
    },
    {
      path: "/groups",
      icon: "users",
      label: "Group Management",
      color: "purple",
    },
    {
      path: "/reports",
      icon: "file-alt",
      label: "Reports",
      color: "red",
    },
    {
      path: "/analytics",
      icon: "chart-bar",
      label: "Analytics",
      color: "indigo",
    },
    {
      path: "/officers",
      icon: "id-badge",
      label: "Field Officers",
      color: "pink",
    },
    {
      path: "/collections",
      icon: "money-bill-wave",
      label: "Loan Collections",
      color: "teal",
    },
    {
      path: "/dividends",
      icon: "percentage",
      label: "Dividends & Interest",
      color: "orange",
    },
    {
      path: "/accounting",
      icon: "calculator",
      label: "Accounting",
      color: "gray",
    },
  ];

  const handleNavigate = (path) => {
    setActiveRoute(path);
    navigate(path);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Navigation Routes
          </h1>
          <p className="mt-2 text-gray-600">Select a section to navigate to</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {routes.map((route) => (
            <button
              key={route.path}
              onClick={() => handleNavigate(route.path)}
              className={`p-6 rounded-xl shadow-sm border-2 transition-all duration-300 hover:-translate-y-1 hover:shadow-md
                ${
                  activeRoute === route.path
                    ? `bg-${route.color}-50 border-${route.color}-500`
                    : "bg-white border-gray-100"
                }`}
            >
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-lg bg-${route.color}-100`}>
                  <i
                    className={`fas fa-${route.icon} text-${route.color}-600 text-xl`}
                  ></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {route.label}
                  </h3>
                  <p className="text-sm text-gray-500">{route.path}</p>
                </div>
                <div className={`text-${route.color}-600`}>
                  <i className="fas fa-chevron-right"></i>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MainComponent;