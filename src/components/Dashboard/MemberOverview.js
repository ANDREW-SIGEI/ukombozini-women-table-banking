import React, { useState } from "react";

function MemberOverview({ onNavigate }) {
  const [searchTerm, setSearchTerm] = useState("");
  
  // Sample member data
  const members = [
    { id: 1, name: "Jane Wambui", role: "Chairperson", group: "Main Ukombozini", loans: 1, savings: "KES 28,500", status: "active" },
    { id: 2, name: "Mary Njoki", role: "Secretary", group: "Main Ukombozini", loans: 2, savings: "KES 45,200", status: "active" },
    { id: 3, name: "Grace Muthoni", role: "Treasurer", group: "Main Ukombozini", loans: 0, savings: "KES 62,100", status: "active" },
    { id: 4, name: "Lucy Wangari", role: "Member", group: "Mwangaza Women", loans: 1, savings: "KES 12,800", status: "active" },
    { id: 5, name: "Sarah Akinyi", role: "Member", group: "Umoja Table Banking", loans: 1, savings: "KES 8,500", status: "inactive" },
  ];

  const filteredMembers = members.filter(
    member => member.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl shadow-xl p-6 border border-white/10">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 gap-4">
        <h3 className="text-xl font-semibold text-white">Member Overview</h3>
        <div className="flex gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search members..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white/20 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-blue-200"
            />
            <div className="absolute left-3 top-2.5">
              <i className="fas fa-search text-blue-200"></i>
            </div>
          </div>
          <button 
            onClick={() => onNavigate("members")}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center"
          >
            <i className="fas fa-user-plus mr-2"></i>
            Add Member
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-white/20 text-left">
              <th className="px-4 py-3 text-white font-medium text-sm rounded-tl-lg">Name</th>
              <th className="px-4 py-3 text-white font-medium text-sm">Role</th>
              <th className="px-4 py-3 text-white font-medium text-sm">Group</th>
              <th className="px-4 py-3 text-white font-medium text-sm">Loans</th>
              <th className="px-4 py-3 text-white font-medium text-sm">Savings</th>
              <th className="px-4 py-3 text-white font-medium text-sm rounded-tr-lg">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {filteredMembers.length > 0 ? (
              filteredMembers.map((member) => (
                <tr key={member.id} className="hover:bg-white/5">
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-blue-500/30 rounded-full flex items-center justify-center text-white mr-3">
                        {member.name.charAt(0)}
                      </div>
                      <div>
                        <p className="text-white">{member.name}</p>
                        <p className={`text-xs ${member.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                          {member.status === 'active' ? 'Active' : 'Inactive'}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-blue-200">{member.role}</td>
                  <td className="px-4 py-3 text-blue-200">{member.group}</td>
                  <td className="px-4 py-3 text-blue-200">
                    {member.loans > 0 ? (
                      <span className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full text-xs">
                        {member.loans} active
                      </span>
                    ) : "None"}
                  </td>
                  <td className="px-4 py-3 text-blue-200">{member.savings}</td>
                  <td className="px-4 py-3">
                    <div className="flex space-x-2">
                      <button className="text-blue-300 hover:text-white transition-colors">
                        <i className="fas fa-eye"></i>
                      </button>
                      <button className="text-yellow-300 hover:text-white transition-colors">
                        <i className="fas fa-edit"></i>
                      </button>
                      <button className="text-red-300 hover:text-white transition-colors">
                        <i className="fas fa-trash-alt"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-blue-200">
                  No members found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-4">
        <div className="text-blue-200 text-sm">
          Showing {filteredMembers.length} of {members.length} members
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => onNavigate("members")}
            className="bg-indigo-600/60 text-white px-4 py-2 rounded-lg hover:bg-indigo-700/60 transition-colors text-sm"
          >
            View All Members
          </button>
        </div>
      </div>
    </div>
  );
}

export default MemberOverview; 