"use client";
import React from "react";

function MainComponent({ theme, onChange }) {
  const colorOptions = [
    { name: "Blue", value: "#3B82F6" },
    { name: "Green", value: "#10B981" },
    { name: "Purple", value: "#8B5CF6" },
    { name: "Red", value: "#EF4444" },
    { name: "Orange", value: "#F97316" },
    { name: "Pink", value: "#EC4899" },
  ];

  const fontOptions = ["Inter", "Roboto", "Poppins", "Montserrat", "Open Sans"];

  const handleChange = (property, value) => {
    onChange({
      ...theme,
      [property]: value,
    });
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6">
      <h4 className="text-white font-medium mb-4">Theme Settings</h4>

      <div className="space-y-4">
        <div>
          <label className="text-white text-sm mb-2 block">Mode</label>
          <div className="flex space-x-4">
            <button
              onClick={() => handleChange("mode", "light")}
              className={`px-4 py-2 rounded-lg ${
                theme.mode === "light"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Light
            </button>
            <button
              onClick={() => handleChange("mode", "dark")}
              className={`px-4 py-2 rounded-lg ${
                theme.mode === "dark"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Dark
            </button>
          </div>
        </div>

        <div>
          <label className="text-white text-sm mb-2 block">Primary Color</label>
          <div className="grid grid-cols-6 gap-2">
            {colorOptions.map((color) => (
              <button
                key={color.value}
                onClick={() => handleChange("primary", color.value)}
                className={`w-8 h-8 rounded-full border-2 ${
                  theme.primary === color.value
                    ? "border-white"
                    : "border-transparent"
                }`}
                style={{ backgroundColor: color.value }}
                title={color.name}
              />
            ))}
          </div>
        </div>

        <div>
          <label className="text-white text-sm mb-2 block">Font Family</label>
          <select
            value={theme.fonts.heading}
            onChange={(e) =>
              handleChange("fonts", {
                ...theme.fonts,
                heading: e.target.value,
              })
            }
            className="w-full bg-white/20 rounded-lg px-3 py-2 text-white"
          >
            {fontOptions.map((font) => (
              <option key={font} value={font}>
                {font}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-white text-sm mb-2 block">
            Background Style
          </label>
          <select
            value={theme.background}
            onChange={(e) => handleChange("background", e.target.value)}
            className="w-full bg-white/20 rounded-lg px-3 py-2 text-white"
          >
            <option value="solid">Solid</option>
            <option value="gradient">Gradient</option>
            <option value="pattern">Pattern</option>
          </select>
        </div>
      </div>
    </div>
  );
}

function StoryComponent() {
  const [lightTheme, setLightTheme] = useState({
    mode: "light",
    primary: "#3B82F6",
    fonts: {
      heading: "Inter",
      body: "Inter",
    },
    background: "solid",
  });

  const [darkTheme, setDarkTheme] = useState({
    mode: "dark",
    primary: "#8B5CF6",
    fonts: {
      heading: "Poppins",
      body: "Poppins",
    },
    background: "gradient",
  });

  return (
    <div className="p-8 space-y-8 bg-gray-900">
      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">Light Theme</h2>
        <MainComponent theme={lightTheme} onChange={setLightTheme} />
      </div>

      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">Dark Theme</h2>
        <MainComponent theme={darkTheme} onChange={setDarkTheme} />
      </div>
    </div>
  );
}

export default MainComponent;