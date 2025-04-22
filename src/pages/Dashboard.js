import React, { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import DashboardContent from "../components/Dashboard/DashboardContent";

function Dashboard() {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [user] = useState({
    name: "Ukombozini",
    role: "Administrator",
    avatar: "https://ucarecdn.com/cbf234c5-42f6-4e86-8462-841e43f5506c/-/format/auto/",
  });

  const handleLogout = useCallback(() => {
    // Implement logout logic here
    console.log("Logout clicked");
  }, []);

  const handleNavigate = useCallback((sectionId) => {
    setActiveSection(sectionId);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-800 to-indigo-900">
      <Navbar user={user} onLogout={handleLogout} />
      <div className="flex">
        <Sidebar activeItem={activeSection} onNavigate={handleNavigate} />
        <main className="flex-1 p-8">
          <DashboardContent onNavigate={handleNavigate} />
        </main>
      </div>
    </div>
  );
}

export default Dashboard;

// "use client";
// import React from "react";

// function MainComponent() {
//   const [activeSection, setActiveSection] = useState("dashboard");
//   const [user] = useState({
//     name: "Ukombozini",
//     role: "Administrator",
//     avatar:
//       "https://ucarecdn.com/cbf234c5-42f6-4e86-8462-841e43f5506c/-/format/auto/",
//   });
//   const [kpiData, setKpiData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [timeRange, setTimeRange] = useState("3");
//   const [exportLoading, setExportLoading] = useState(false);
//   const [activeTab, setActiveTab] = useState("overview");
//   const [viewportSize, setViewportSize] = useState("desktop");
//   const handleLogout = useCallback(() => {
//     console.log("Logout clicked");
//   }, []);
//   const handleNavigate = useCallback((sectionId) => {
//     setActiveSection(sectionId);
//   }, []);
//   const handleExport = async (format) => {
//     setExportLoading(true);
//     try {
//       const response = await fetch("/api/dashboard-kp-is", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ timeRange, format }),
//       });

//       if (!response.ok) throw new Error("Export failed");

//       const blob = await response.blob();
//       const url = window.URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = url;
//       a.download = `table-banking-report.${format}`;
//       document.body.appendChild(a);
//       a.click();
//       window.URL.revokeObjectURL(url);
//     } catch (error) {
//       console.error("Export error:", error);
//     } finally {
//       setExportLoading(false);
//     }
//   };

//   useEffect(() => {
//     const handleResize = () => {
//       setViewportSize(window.innerWidth < 768 ? "mobile" : "desktop");
//     };

//     handleResize();
//     window.addEventListener("resize", handleResize);

//     return () => window.removeEventListener("resize", handleResize);
//   }, []);

//   useEffect(() => {
//     const fetchDashboardStats = async () => {
//       try {
//         const [kpiResponse, statsResponse] = await Promise.all([
//           fetch("/api/dashboard-kp-is", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ timeRange }),
//           }),
//           fetch("/api/dashboard-stats", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//               timeRange: "last_7_days",
//               filterCriteria: { status: "active" },
//             }),
//           }),
//         ]);

//         if (!kpiResponse.ok || !statsResponse.ok)
//           throw new Error("Failed to fetch dashboard data");

//         const [kpiData, statsData] = await Promise.all([
//           kpiResponse.json(),
//           statsResponse.json(),
//         ]);

//         if (kpiData.success && statsData.success) {
//           setKpiData({
//             ...kpiData.data,
//             ...statsData.data,
//           });
//         } else {
//           throw new Error(kpiData.error || statsData.error);
//         }
//       } catch (error) {
//         console.error("Error fetching dashboard data:", error);
//         setError(error.message);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchDashboardStats();

//     const updateInterval = setInterval(fetchDashboardStats, 300000);
//     return () => clearInterval(updateInterval);
//   }, [timeRange]);

//   return (
//     <div className="min-h-screen bg-gradient-to-r from-blue-800 to-indigo-900">
//       <></>
//       <div className="flex">
//         <></>
//         <main className="flex-1 p-8">
//           <div className="max-w-7xl mx-auto">
//             <div className="flex justify-between items-center mb-8">
//               <div>
//                 <h1 className="text-2xl font-bold text-white">Dashboard</h1>
//                 <p className="mt-1 text-sm text-blue-200">
//                   Comprehensive overview and analytics
//                 </p>
//               </div>
//               <div className="flex items-center space-x-4">
//                 <select
//                   value={timeRange}
//                   onChange={(e) => setTimeRange(e.target.value)}
//                   className="rounded-lg border-gray-300 text-sm bg-white/10 text-white backdrop-blur-sm"
//                 >
//                   <option value="1">Last Month</option>
//                   <option value="3">Last 3 Months</option>
//                   <option value="6">Last 6 Months</option>
//                   <option value="12">Last Year</option>
//                 </select>
//                 <></>
//               </div>
//             </div>
//             <div className="mb-8">
//               <nav className="flex space-x-4">
//                 {["overview", "loans", "savings", "groups", "members"].map(
//                   (tab) => (
//                     <button
//                       key={tab}
//                       onClick={() => setActiveTab(tab)}
//                       className={`px-4 py-2 rounded-lg text-sm font-medium ${
//                         activeTab === tab
//                           ? "bg-blue-600 text-white"
//                           : "bg-white/10 text-white backdrop-blur-sm hover:bg-white/20"
//                       }`}
//                     >
//                       {tab.charAt(0).toUpperCase() + tab.slice(1)}
//                     </button>
//                   )
//                 )}
//               </nav>
//             </div>

//             {error ? (
//               <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
//                 {error}
//               </div>
//             ) : (
//               <div className="space-y-8">
//                 <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
//                   <></>
//                   <></>
//                   <></>
//                   <></>
//                   <></>
//                   <></>
//                 </div>

//                 {activeTab === "overview" && (
//                   <>
//                     <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
//                       <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6">
//                         <h3 className="text-lg font-semibold text-white mb-4">
//                           Loan Performance Trend
//                         </h3>
//                         <></>
//                       </div>
//                       <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6">
//                         <h3 className="text-lg font-semibold text-white mb-4">
//                           Membership Growth
//                         </h3>
//                         <></>
//                       </div>
//                     </div>
//                   </>
//                 )}

//                 {activeTab === "loans" && (
//                   <div className="space-y-8">
//                     <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6">
//                       <h3 className="text-lg font-semibold text-white mb-4">
//                         Detailed Loan Analysis
//                       </h3>
//                       <></>
//                     </div>
//                   </div>
//                 )}

//                 {activeTab === "groups" && (
//                   <div className="space-y-8">
//                     <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6">
//                       <h3 className="text-lg font-semibold text-white mb-4">
//                         Group Activity Analysis
//                       </h3>
//                       <></>
//                     </div>
//                   </div>
//                 )}

//                 <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-6">
//                   <h3 className="text-lg font-semibold text-white mb-4">
//                     Recent Activities
//                   </h3>
//                   <></>
//                 </div>
//               </div>
//             )}
//           </div>
//         </main>
//       </div>
//       <style jsx global>{`
//         .stat-card {
//           backdrop-filter: blur(10px);
//           box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
//           border-radius: 24px;
//           border: 1px solid rgba(255, 255, 255, 0.2);
//           transition: all 0.3s ease;
//           transform-style: preserve-3d;
//         }

//         .stat-card:hover {
//           transform: translateY(-8px) perspective(1000px) rotateX(2deg);
//           box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
//         }

//         .stat-icon {
//           font-size: 2.5rem;
//           transition: all 0.3s ease;
//         }

//         .stat-card:hover .stat-icon {
//           transform: scale(1.1);
//         }

//         .glow-button {
//           box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
//           animation: pulse 2s infinite;
//         }

//         @keyframes pulse {
//           0% {
//             box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
//           }
//           50% {
//             box-shadow: 0 0 25px rgba(59, 130, 246, 0.8);
//           }
//           100% {
//             box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
//           }
//         }

//         .quick-action-btn {
//           position: relative;
//           overflow: hidden;
//         }

//         .quick-action-btn::after {
//           content: "";
//           position: absolute;
//           top: 0;
//           left: 0;
//           width: 100%;
//           height: 100%;
//           background: linear-gradient(
//             45deg,
//             transparent,
//             rgba(255, 255, 255, 0.1),
//             transparent
//           );
//           transform: translateX(-100%);
//         }

//         .quick-action-btn:hover::after {
//           transform: translateX(100%);
//           transition: transform 0.6s;
//         }

//         .custom-scrollbar {
//           scrollbar-width: thin;
//           scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
//         }

//         .custom-scrollbar::-webkit-scrollbar {
//           width: 6px;
//         }

//         .custom-scrollbar::-webkit-scrollbar-track {
//           background: transparent;
//         }

//         .custom-scrollbar::-webkit-scrollbar-thumb {
//           background-color: rgba(255, 255, 255, 0.2);
//           border-radius: 3px;
//         }

//         @keyframes float {
//           0% {
//             transform: translateY(0px);
//           }
//           50% {
//             transform: translateY(-10px);
//           }
//           100% {
//             transform: translateY(0px);
//           }
//         }

//         .floating-animation {
//           animation: float 3s ease-in-out infinite;
//         }
//       `}</style>
//     </div>
//   );
// }

// export default MainComponent;