import React from "react";

function Sidebar({ activeItem, onNavigate }) {
  const menuItems = [
    {
      title: "User & Group Management",
      icon: "users",
      items: [
        { id: "members", label: "Member Management", icon: "user" },
        { id: "groups", label: "Groups Registration", icon: "users" },
        { id: "officers", label: "Field Officers", icon: "id-badge" },
      ],
    },
    {
      title: "Financial Management",
      icon: "money-bill",
      items: [
        { id: "savings", label: "Savings Management", icon: "piggy-bank" },
        { id: "loans", label: "Loan Management", icon: "hand-holding-usd" },
        { id: "collections", label: "Loan Collections", icon: "money-bill-wave" },
        { id: "dividends", label: "Dividends & Interest", icon: "percentage" },
        { id: "accounting", label: "Accounting", icon: "calculator" },
      ],
    },
    {
      title: "Meetings & Activities",
      icon: "calendar",
      items: [
        { id: "meetings", label: "Meeting Management", icon: "calendar-alt" },
        { id: "schedule-meeting", label: "Schedule Meeting", icon: "calendar-plus" },
        { id: "attendance", label: "Meeting Attendance", icon: "clipboard-check" },
      ],
    },
    {
      title: "Reports & Analytics",
      icon: "chart-line",
      items: [
        { id: "banking-reports", label: "Table Banking Reports", icon: "file-alt" },
        { id: "loan-reports", label: "Loan Reports", icon: "file-invoice-dollar" },
        { id: "analytics", label: "Analytics Dashboard", icon: "chart-bar" },
      ],
    },
  ];

  const handleMenuItemClick = (itemId) => {
    if (itemId === "meetings") {
      window.location.href = "/meetings";
    } else {
      onNavigate(itemId);
    }
  };

  return (
    <div className="bg-[#1a365d] w-64 h-screen shadow-lg border-r border-white/10">
      <div className="p-4 border-b border-white/20">
        <h1 className="text-xl font-bold text-white">UKOMBOZINI</h1>
        <p className="text-sm text-blue-200">Table Banking System</p>
      </div>

      <div className="p-4 space-y-4">
        {menuItems.map((section) => (
          <div key={section.title} className="space-y-2">
            <div className="flex items-center text-sm font-medium text-white/80 mb-2">
              <i className={`fas fa-${section.icon} mr-2`}></i>
              {section.title}
            </div>

            {section.items.map((item) => (
              <button
                key={item.id}
                onClick={() => handleMenuItemClick(item.id)}
                className={`w-full flex items-center px-4 py-2 text-sm rounded-lg ${
                  activeItem === item.id
                    ? "bg-white/10 text-white"
                    : "text-white/70 hover:bg-white/5"
                }`}
              >
                <i className={`fas fa-${item.icon} w-5`}></i>
                <span className="ml-2">{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;

// "use client";
// import React from "react";

// function StatsCard({ icon, title, value, color, onClick, linkText }) {
//   const colorClasses = {
//     blue: "bg-blue-100 text-blue-700 group-hover:bg-blue-200",
//     green: "bg-green-100 text-green-700 group-hover:bg-green-200",
//     yellow: "bg-yellow-100 text-yellow-700 group-hover:bg-yellow-200",
//     purple: "bg-purple-100 text-purple-700 group-hover:bg-purple-200",
//   };

//   return (
//     <button
//       onClick={onClick}
//       className="bg-white p-8 rounded-xl shadow-lg text-center w-full hover:cursor-pointer group transition-all duration-300 hover:-translate-y-1"
//     >
//       <div className="flex flex-col items-center space-y-4">
//         <div
//           className={`p-4 rounded-full transition-colors ${colorClasses[color]}`}
//         >
//           <i className={`fas fa-${icon} text-2xl`}></i>
//         </div>
//         <div className="text-center">
//           <p className="text-gray-700 text-sm font-bold mb-2">{title}</p>
//           <h3 className="text-3xl font-bold text-blue-900">{value}</h3>
//         </div>
//         <span
//           className={`text-${color}-700 text-sm font-bold hover:text-${color}-800 hover:underline mt-4`}
//         >
//           {linkText}
//         </span>
//       </div>
//     </button>
//   );
// }

// function MeetingsCard({ onNavigate }) {
//   return (
//     <div className="bg-white p-8 rounded-xl shadow-lg">
//       <div className="flex flex-col items-center space-y-4">
//         <div className="p-4 bg-purple-100 rounded-full">
//           <i className="fas fa-calendar text-purple-700 text-2xl"></i>
//         </div>
//         <div className="text-center">
//           <p className="text-gray-700 text-sm font-bold mb-2">
//             Upcoming Meetings
//           </p>
//           <h3 className="text-3xl font-bold text-purple-900">0</h3>
//         </div>
//         <div className="flex space-x-4">
//           <button
//             onClick={() => onNavigate("schedule-meeting")}
//             className="text-purple-700 text-sm font-bold hover:text-purple-800 hover:underline"
//           >
//             Schedule
//           </button>
//           <button
//             onClick={() => onNavigate("meetings")}
//             className="text-purple-700 text-sm font-bold hover:text-purple-800 hover:underline"
//           >
//             View all
//           </button>
//         </div>
//         <div className="w-full pt-4 mt-2 border-t border-gray-200">
//           <div className="text-sm text-gray-800">
//             <div className="flex justify-between items-center mb-3">
//               <span className="font-bold">Next meeting:</span>
//               <span className="text-gray-700">No meetings scheduled</span>
//             </div>
//             <button
//               onClick={() => onNavigate("schedule-meeting")}
//               className="w-full py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-bold shadow-md"
//             >
//               <i className="fas fa-plus mr-2"></i>
//               Schedule Meeting
//             </button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// function MainComponent({ onNavigate }) {
//   return (
//     <div className="space-y-8">
//       <div className="flex justify-between items-center mb-8">
//         <h1
//           className="text-4xl font-bold text-white text-center flex-1 tracking-wide"
//           style={{ textShadow: "0 2px 4px rgba(0,0,0,0.3)" }}
//         >
//           Dashboard Overview
//         </h1>
//         <div className="flex items-center space-x-4">
//           <></>
//           <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 shadow-lg transform transition hover:-translate-y-1 font-bold text-lg">
//             <i className="fas fa-plus mr-2"></i>
//             Add New
//           </button>
//         </div>
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
//         <StatsCard
//           icon="users"
//           title="Total Members"
//           value="0"
//           color="blue"
//           onClick={() => onNavigate("members")}
//           linkText="See all members"
//         />
//         <StatsCard
//           icon="money-bill-wave"
//           title="Total Loans"
//           value="0"
//           color="green"
//           onClick={() => onNavigate("loans")}
//           linkText="View loans"
//         />
//         <StatsCard
//           icon="layer-group"
//           title="Active Groups"
//           value="0"
//           color="yellow"
//           onClick={() => onNavigate("groups")}
//           linkText="See all groups"
//         />
//         <MeetingsCard onNavigate={onNavigate} />
//       </div>
//     </div>
//   );
// }

// function StoryComponent() {
//   const handleNavigate = (route) => {
//     console.log(`Navigating to: ${route}`);
//   };

//   return (
//     <div>
//       <div className="bg-gray-900 p-8">
//         <h2 className="text-white text-xl mb-4">Default Dashboard</h2>
//         <MainComponent onNavigate={handleNavigate} />
//       </div>
//     </div>
//   );
// }

// export default MainComponent;