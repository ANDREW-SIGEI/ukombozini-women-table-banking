import React, { useState } from "react";

function FinancialOverview({ onNavigate }) {
  const [activeTab, setActiveTab] = useState("overview");
  
  // Sample financial data
  const financialData = {
    loanPortfolio: "KES 854,320",
    totalDisbursed: "KES 1,235,000",
    repaymentRate: "92.4%",
    averageLoanSize: "KES 28,750",
    defaultRate: "3.2%",
    savingsBalance: "KES 1,625,450",
    interestEarned: "KES 145,210",
    liquidAssets: "KES 362,500"
  };
  
  // Chart data (for example purposes)
  const monthlyData = [
    { month: 'Jan', loans: 180000, savings: 290000 },
    { month: 'Feb', loans: 210000, savings: 320000 },
    { month: 'Mar', loans: 250000, savings: 380000 },
    { month: 'Apr', loans: 290000, savings: 450000 },
    { month: 'May', loans: 320000, savings: 495000 },
    { month: 'Jun', loans: 260000, savings: 520000 },
  ];

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-white">Financial Overview</h3>
        <div className="flex bg-white/20 rounded-lg p-1">
          {["overview", "loans", "savings"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "text-blue-100 hover:text-white"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {activeTab === "overview" && (
        <div className="space-y-4">
          {/* Quick stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Loan Portfolio</p>
              <p className="text-white text-lg font-bold">{financialData.loanPortfolio}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Savings Balance</p>
              <p className="text-white text-lg font-bold">{financialData.savingsBalance}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Interest Earned</p>
              <p className="text-white text-lg font-bold">{financialData.interestEarned}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Repayment Rate</p>
              <p className="text-white text-lg font-bold">{financialData.repaymentRate}</p>
            </div>
          </div>

          {/* Chart */}
          <div className="h-64 bg-gradient-to-r from-indigo-500/20 to-purple-600/20 rounded-lg p-4">
            <div className="flex justify-between h-full items-end">
              {monthlyData.map((item, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div className="relative h-48 w-12 flex flex-col justify-end space-y-1">
                    <div 
                      className="w-full bg-green-400/80 rounded-t-sm"
                      style={{ height: `${(item.savings / 600000) * 100}%` }}
                    ></div>
                    <div 
                      className="w-full bg-blue-500/80 rounded-t-sm"
                      style={{ height: `${(item.loans / 600000) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-white text-xs mt-2">{item.month}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-center mt-2">
            <div className="flex items-center mr-6">
              <div className="w-3 h-3 bg-blue-500/80 rounded-full mr-2"></div>
              <span className="text-white text-sm">Loans</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400/80 rounded-full mr-2"></div>
              <span className="text-white text-sm">Savings</span>
            </div>
          </div>

          <div className="flex justify-center mt-4">
            <button 
              onClick={() => onNavigate("banking-reports")}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center"
            >
              <i className="fas fa-chart-line mr-2"></i>
              View Detailed Reports
            </button>
          </div>
        </div>
      )}

      {activeTab === "loans" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Total Disbursed</p>
              <p className="text-white text-lg font-bold">{financialData.totalDisbursed}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Repayment Rate</p>
              <p className="text-white text-lg font-bold">{financialData.repaymentRate}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Avg. Loan Size</p>
              <p className="text-white text-lg font-bold">{financialData.averageLoanSize}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Default Rate</p>
              <p className="text-white text-lg font-bold">{financialData.defaultRate}</p>
            </div>
          </div>

          <div className="bg-white/20 rounded-lg p-4">
            <h4 className="text-white text-sm font-medium mb-3">Loan Types Distribution</h4>
            <div className="flex h-8 rounded-lg overflow-hidden">
              <div className="bg-blue-500 w-2/6 flex items-center justify-center text-white text-xs font-medium">
                Business (35%)
              </div>
              <div className="bg-green-500 w-1/4 flex items-center justify-center text-white text-xs font-medium">
                Agriculture (25%)
              </div>
              <div className="bg-yellow-500 w-1/5 flex items-center justify-center text-white text-xs font-medium">
                Education (20%)
              </div>
              <div className="bg-purple-500 w-1/5 flex items-center justify-center text-white text-xs font-medium">
                Emergency (20%)
              </div>
            </div>
          </div>

          <div className="flex justify-between gap-4">
            <button 
              onClick={() => onNavigate("loans")}
              className="flex-1 bg-indigo-600/60 text-white p-3 rounded-lg hover:bg-indigo-700/60 transition-colors text-sm font-medium"
            >
              <i className="fas fa-search-dollar mr-2"></i>
              View All Loans
            </button>
            <button 
              onClick={() => onNavigate("loans")}
              className="flex-1 bg-green-600/60 text-white p-3 rounded-lg hover:bg-green-700/60 transition-colors text-sm font-medium"
            >
              <i className="fas fa-plus mr-2"></i>
              Process New Loan
            </button>
          </div>
        </div>
      )}

      {activeTab === "savings" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Total Savings</p>
              <p className="text-white text-lg font-bold">{financialData.savingsBalance}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Interest Earned</p>
              <p className="text-white text-lg font-bold">{financialData.interestEarned}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Liquid Assets</p>
              <p className="text-white text-lg font-bold">{financialData.liquidAssets}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <p className="text-blue-200 text-xs">Active Savers</p>
              <p className="text-white text-lg font-bold">118</p>
            </div>
          </div>

          <div className="bg-white/20 rounded-lg p-4">
            <h4 className="text-white text-sm font-medium mb-2">Recent Savings Transactions</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-2 bg-white/10 rounded">
                <div>
                  <p className="text-white text-sm">Jane Wambui</p>
                  <p className="text-blue-200 text-xs">Today, 10:23 AM</p>
                </div>
                <div className="text-green-300 font-medium">+KES 2,500</div>
              </div>
              <div className="flex justify-between items-center p-2 bg-white/10 rounded">
                <div>
                  <p className="text-white text-sm">Mary Njoki</p>
                  <p className="text-blue-200 text-xs">Today, 09:45 AM</p>
                </div>
                <div className="text-green-300 font-medium">+KES 1,200</div>
              </div>
              <div className="flex justify-between items-center p-2 bg-white/10 rounded">
                <div>
                  <p className="text-white text-sm">Grace Muthoni</p>
                  <p className="text-blue-200 text-xs">Yesterday, 03:15 PM</p>
                </div>
                <div className="text-green-300 font-medium">+KES 5,000</div>
              </div>
            </div>
          </div>

          <div className="flex justify-between gap-4">
            <button 
              onClick={() => onNavigate("savings")}
              className="flex-1 bg-indigo-600/60 text-white p-3 rounded-lg hover:bg-indigo-700/60 transition-colors text-sm font-medium"
            >
              <i className="fas fa-list-alt mr-2"></i>
              View All Savings
            </button>
            <button 
              onClick={() => onNavigate("savings")}
              className="flex-1 bg-green-600/60 text-white p-3 rounded-lg hover:bg-green-700/60 transition-colors text-sm font-medium"
            >
              <i className="fas fa-plus mr-2"></i>
              Record Deposit
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default FinancialOverview; 