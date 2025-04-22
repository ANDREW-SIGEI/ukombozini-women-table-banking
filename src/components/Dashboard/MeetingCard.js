import React from "react";

function MeetingCard({ onNavigate }) {
  // Sample upcoming meetings data
  const upcomingMeetings = [
    {
      id: 1,
      title: "Monthly Group Meeting",
      date: "2024-04-15",
      time: "10:00 AM",
      location: "Community Hall"
    },
    {
      id: 2,
      title: "Executive Committee",
      date: "2024-04-20",
      time: "2:00 PM",
      location: "Chair Office"
    }
  ];

  // Get next meeting (first in the list)
  const nextMeeting = upcomingMeetings.length > 0 ? upcomingMeetings[0] : null;

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <div className="flex flex-col items-center space-y-4">
        <div className="p-4 bg-purple-100 rounded-full">
          <i className="fas fa-calendar text-purple-700 text-2xl"></i>
        </div>
        <div className="text-center">
          <p className="text-gray-700 text-sm font-bold mb-2">
            Upcoming Meetings
          </p>
          <h3 className="text-3xl font-bold text-purple-900">{upcomingMeetings.length}</h3>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={() => onNavigate("schedule-meeting")}
            className="text-purple-700 text-sm font-bold hover:text-purple-800 hover:underline"
          >
            Schedule
          </button>
          <button
            onClick={() => onNavigate("meetings")}
            className="text-purple-700 text-sm font-bold hover:text-purple-800 hover:underline"
          >
            View all
          </button>
        </div>
        <div className="w-full pt-4 mt-2 border-t border-gray-200">
          <div className="text-sm text-gray-800">
            <div className="flex justify-between items-center mb-3">
              <span className="font-bold">Next meeting:</span>
              {nextMeeting ? (
                <span className="text-gray-700">{new Date(nextMeeting.date).toLocaleDateString()}</span>
              ) : (
                <span className="text-gray-700">No meetings scheduled</span>
              )}
            </div>
            {nextMeeting && (
              <div className="bg-purple-50 p-3 rounded-lg mb-3">
                <p className="font-medium text-purple-800">{nextMeeting.title}</p>
                <p className="text-sm text-gray-600">Time: {nextMeeting.time}</p>
                <p className="text-sm text-gray-600">Location: {nextMeeting.location}</p>
              </div>
            )}
            <button
              onClick={() => onNavigate("schedule-meeting")}
              className="w-full py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-bold shadow-md"
            >
              <i className="fas fa-plus mr-2"></i>
              Schedule Meeting
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MeetingCard; 