import React from "react";

function Navbar({ user, onLogout }) {
  const handleNavigateHome = () => {
    window.location.href = "/";
  };

  return (
    <nav className="bg-gradient-to-r from-blue-800 to-indigo-900 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <button
            onClick={handleNavigateHome}
            className="flex items-center hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-4 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300 border-2 border-blue-400/30 backdrop-blur-sm">
              <div className="flex flex-col">
                <span className="text-3xl font-extrabold text-white tracking-wider">
                  UKOMBOZINI
                </span>
                <span className="text-sm text-blue-200 font-medium">
                  Table Banking System
                </span>
              </div>
            </div>
          </button>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <button className="p-2 text-blue-200 hover:text-white transition-colors">
                <i className="fas fa-bell text-xl"></i>
              </button>
            </div>

            <div className="flex items-center space-x-3 bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2 rounded-lg border-2 border-blue-400/30">
              <img
                className="h-8 w-8 rounded-full border-2 border-white/50"
                src={user?.avatar}
                alt=""
              />
              <div className="text-sm">
                <p className="font-medium text-white">{user?.name}</p>
                <p className="text-blue-200">{user?.role}</p>
              </div>

              <button
                onClick={onLogout}
                className="ml-2 text-blue-200 hover:text-white transition-colors"
              >
                <i className="fas fa-sign-out-alt text-xl"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
