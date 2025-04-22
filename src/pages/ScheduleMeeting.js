import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

function ScheduleMeeting() {
  const [user] = useState({
    name: "Ukombozini",
    role: "Administrator",
    avatar: "https://ucarecdn.com/cbf234c5-42f6-4e86-8462-841e43f5506c/-/format/auto/",
  });

  const [groups, setGroups] = useState([
    { id: 1, name: "Main Ukombozini Group" },
    { id: 2, name: "Mwangaza Women Group" },
    { id: 3, name: "Umoja Table Banking" },
    { id: 4, name: "Jikaze Women Initiative" },
  ]);

  const [formData, setFormData] = useState({
    title: "",
    groupId: "",
    date: "",
    time: "",
    location: "",
    agenda: "",
    inviteAll: true,
    notification: "email",
    reminder: "1day"
  });

  const [formSubmitted, setFormSubmitted] = useState(false);

  const handleLogout = () => {
    console.log("Logout clicked");
  };

  const handleNavigate = (sectionId) => {
    if (sectionId === "dashboard") {
      window.location.href = "/";
    } else if (sectionId === "meetings") {
      window.location.href = "/meetings";
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Meeting scheduled:", formData);
    setFormSubmitted(true);
    
    // In a real app, you would post this to an API endpoint
    setTimeout(() => {
      // Navigate to meetings page after success
      window.location.href = "/meetings";
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-800 to-indigo-900">
      <Navbar user={user} onLogout={handleLogout} />
      <div className="flex">
        <Sidebar activeItem="schedule-meeting" onNavigate={handleNavigate} />
        <main className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center mb-8">
              <button 
                onClick={() => handleNavigate("meetings")}
                className="text-blue-300 hover:text-white mr-4"
              >
                <i className="fas fa-arrow-left"></i>
              </button>
              <h1 className="text-3xl font-bold text-white">Schedule a New Meeting</h1>
            </div>

            {formSubmitted ? (
              <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-6 rounded-lg shadow-lg mb-8 animate-pulse">
                <div className="flex items-center">
                  <div className="text-green-500 mr-4">
                    <i className="fas fa-check-circle text-3xl"></i>
                  </div>
                  <div>
                    <h2 className="font-bold text-lg">Meeting Scheduled Successfully!</h2>
                    <p>All participants will be notified according to your settings.</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-xl overflow-hidden">
                <div className="bg-blue-600 p-4 text-white">
                  <h2 className="text-xl font-semibold">Meeting Details</h2>
                  <p className="text-blue-200 text-sm">All fields marked with * are required</p>
                </div>
                
                <form onSubmit={handleSubmit} className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Meeting Title *
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="E.g. Monthly Progress Review"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Select Group *
                      </label>
                      <select
                        name="groupId"
                        value={formData.groupId}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                      >
                        <option value="">Select a group</option>
                        {groups.map(group => (
                          <option key={group.id} value={group.id}>
                            {group.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Date *
                      </label>
                      <input
                        type="date"
                        name="date"
                        value={formData.date}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Time *
                      </label>
                      <input
                        type="time"
                        name="time"
                        value={formData.time}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Location *
                      </label>
                      <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="E.g. Community Hall, Zoom Meeting, etc."
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-gray-700 text-sm font-medium mb-2">
                        Notification Method
                      </label>
                      <select
                        name="notification"
                        value={formData.notification}
                        onChange={handleInputChange}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="email">Email</option>
                        <option value="sms">SMS</option>
                        <option value="both">Both Email & SMS</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-medium mb-2">
                      Agenda/Discussion Points *
                    </label>
                    <textarea
                      name="agenda"
                      value={formData.agenda}
                      onChange={handleInputChange}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows="4"
                      placeholder="List the main agenda items or discussion points for this meeting"
                      required
                    ></textarea>
                  </div>
                  
                  <div className="flex flex-col md:flex-row md:items-center justify-between bg-gray-50 p-4 rounded-lg mb-6">
                    <div className="mb-4 md:mb-0">
                      <label className="inline-flex items-center">
                        <input
                          type="checkbox"
                          name="inviteAll"
                          checked={formData.inviteAll}
                          onChange={handleInputChange}
                          className="form-checkbox h-5 w-5 text-blue-600"
                        />
                        <span className="ml-2 text-gray-700">Invite all group members</span>
                      </label>
                    </div>
                    
                    <div>
                      <label className="text-gray-700 text-sm font-medium mr-3">
                        Send reminder:
                      </label>
                      <select
                        name="reminder"
                        value={formData.reminder}
                        onChange={handleInputChange}
                        className="border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="1hour">1 hour before</option>
                        <option value="3hours">3 hours before</option>
                        <option value="1day">1 day before</option>
                        <option value="2days">2 days before</option>
                        <option value="1week">1 week before</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="flex justify-end space-x-4">
                    <button
                      type="button"
                      onClick={() => handleNavigate("meetings")}
                      className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center"
                    >
                      <i className="fas fa-calendar-check mr-2"></i>
                      Schedule Meeting
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default ScheduleMeeting; 