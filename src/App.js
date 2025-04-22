import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import MeetingsPage from "./pages/Meetings";
import ScheduleMeeting from "./pages/ScheduleMeeting";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/meetings" element={<MeetingsPage />} />
        <Route path="/schedule-meeting" element={<ScheduleMeeting />} />
      </Routes>
    </Router>
  );
}

export default App;
