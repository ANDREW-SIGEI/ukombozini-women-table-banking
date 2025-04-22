"use client";
import React from "react";

function MainComponent({ layout, onChange }) {
  const handleChange = (property, value) => {
    onChange({
      ...layout,
      [property]: value,
    });
  };

  return (
    <div className="space-y-6">
      <h4 className="text-white font-medium mb-4">Layout Settings</h4>

      <div className="space-y-4">
        <div>
          <label className="text-white text-sm mb-2 block">Sidebar Style</label>
          <div className="flex space-x-4">
            <button
              onClick={() => handleChange("sidebar", "expanded")}
              className={`px-4 py-2 rounded-lg ${
                layout.sidebar === "expanded"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Expanded
            </button>
            <button
              onClick={() => handleChange("sidebar", "collapsed")}
              className={`px-4 py-2 rounded-lg ${
                layout.sidebar === "collapsed"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Collapsed
            </button>
          </div>
        </div>

        <div>
          <label className="text-white text-sm mb-2 block">Content Width</label>
          <div className="flex space-x-4">
            <button
              onClick={() => handleChange("content", "fluid")}
              className={`px-4 py-2 rounded-lg ${
                layout.content === "fluid"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Fluid
            </button>
            <button
              onClick={() => handleChange("content", "fixed")}
              className={`px-4 py-2 rounded-lg ${
                layout.content === "fixed"
                  ? "bg-white text-gray-900"
                  : "bg-white/10 text-white"
              }`}
            >
              Fixed
            </button>
          </div>
        </div>

        <div>
          <label className="text-white text-sm mb-2 block">Card Style</label>
          <select
            value={layout.cards}
            onChange={(e) => handleChange("cards", e.target.value)}
            className="w-full bg-white/20 rounded-lg px-3 py-2 text-white"
          >
            <option value="flat">Flat</option>
            <option value="elevated">Elevated</option>
            <option value="bordered">Bordered</option>
          </select>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-white text-sm">Enable Animations</span>
          <div
            className={`w-11 h-6 flex items-center rounded-full p-1 cursor-pointer ${
              layout.animations ? "bg-blue-600" : "bg-gray-500"
            }`}
            onClick={() => handleChange("animations", !layout.animations)}
          >
            <div
              className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                layout.animations ? "translate-x-5" : "translate-x-0"
              }`}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StoryComponent() {
  const [defaultLayout, setDefaultLayout] = useState({
    sidebar: "expanded",
    content: "fluid",
    cards: "flat",
    animations: true,
  });

  const [darkLayout, setDarkLayout] = useState({
    sidebar: "collapsed",
    content: "fixed",
    cards: "elevated",
    animations: false,
  });

  return (
    <div className="p-8 space-y-8 bg-gray-900">
      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">Default Layout</h2>
        <MainComponent layout={defaultLayout} onChange={setDefaultLayout} />
      </div>

      <div className="max-w-md">
        <h2 className="text-xl font-bold text-white mb-4">
          Alternative Layout
        </h2>
        <MainComponent layout={darkLayout} onChange={setDarkLayout} />
      </div>
    </div>
  );
}

export default MainComponent;