"use client";
import React from "react";

function MainComponent({ widgets, onChange }) {
  const handleToggle = (widgetKey) => {
    onChange({
      ...widgets,
      [widgetKey]: !widgets[widgetKey],
    });
  };

  const widgetsList = [
    { key: "metrics", label: "Key Metrics", icon: "chart-pie" },
    { key: "charts", label: "Charts & Graphs", icon: "chart-line" },
    { key: "tables", label: "Data Tables", icon: "table" },
    { key: "notifications", label: "Notifications", icon: "bell" },
  ];

  return (
    <div className="space-y-6">
      <h4 className="text-white font-medium mb-4">Widget Settings</h4>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {widgetsList.map((widget) => (
          <div
            key={widget.key}
            className="bg-white/5 rounded-lg p-4 flex items-center justify-between"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center">
                <i className={`fas fa-${widget.icon} text-white`}></i>
              </div>
              <span className="text-white">{widget.label}</span>
            </div>
            <button
              onClick={() => handleToggle(widget.key)}
              className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 ${
                widgets[widget.key] ? "bg-blue-600" : "bg-gray-500"
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                  widgets[widget.key] ? "translate-x-6" : "translate-x-0"
                }`}
              ></div>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function StoryComponent() {
  const [defaultWidgets, setDefaultWidgets] = useState({
    metrics: true,
    charts: true,
    tables: false,
    notifications: true,
  });

  const [alternativeWidgets, setAlternativeWidgets] = useState({
    metrics: false,
    charts: false,
    tables: true,
    notifications: false,
  });

  return (
    <div className="p-8 space-y-8 bg-gray-900">
      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">Default Settings</h2>
        <MainComponent widgets={defaultWidgets} onChange={setDefaultWidgets} />
      </div>

      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">
          Alternative Settings
        </h2>
        <MainComponent
          widgets={alternativeWidgets}
          onChange={setAlternativeWidgets}
        />
      </div>
    </div>
  );
}

export default MainComponent;