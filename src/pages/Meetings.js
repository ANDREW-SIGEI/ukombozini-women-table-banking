import React from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Meetings from "../components/Meetings";

function MeetingsPage() {
  const [user] = React.useState({
    name: "Ukombozini",
    role: "Administrator",
    avatar: "https://ucarecdn.com/cbf234c5-42f6-4e86-8462-841e43f5506c/-/format/auto/",
  });

  const handleLogout = () => {
    // Implement logout logic here
    console.log("Logout clicked");
  };

  const handleNavigate = (sectionId) => {
    if (sectionId === "dashboard") {
      window.location.href = "/";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-800 to-indigo-900">
      <Navbar user={user} onLogout={handleLogout} />
      <div className="flex">
        <Sidebar activeItem="meetings" onNavigate={handleNavigate} />
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-6">Meeting Management</h1>
            <Meetings />
          </div>
        </main>
      </div>
    </div>
  );
}

export default MeetingsPage; 