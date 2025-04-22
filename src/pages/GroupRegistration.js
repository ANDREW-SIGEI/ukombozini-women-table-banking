"use client";
import React from "react";

function MainComponent() {
  const [formData, setFormData] = useState({
    group_name: "",
    registration_date: new Date().toISOString().split("T")[0],
    county: "",
    sub_county: "",
    constituency: "",
    ward: "",
    location: "",
    sub_location: "",
    village: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const counties = [
    "Nakuru",
    "Bomet",
    "Narok",
    "Kericho",
    "Nairobi",
    "Baringo",
  ];
  const subCounties = {
    Nakuru: [
      "Nakuru Town East",
      "Nakuru Town West",
      "Naivasha",
      "Gilgil",
      "Subukia",
      "Rongai",
      "Bahati",
      "Njoro",
      "Molo",
      "Kuresoi North",
      "Kuresoi South",
    ],
    Bomet: ["Bomet Central", "Bomet East", "Chepalungu", "Sotik", "Konoin"],
    Narok: [
      "Narok North",
      "Narok South",
      "Narok East",
      "Narok West",
      "Kilgoris",
      "Emurua Dikirr",
    ],
    Kericho: [
      "Ainamoi",
      "Belgut",
      "Bureti",
      "Kipkelion East",
      "Kipkelion West",
      "Sigowet/Soin",
    ],
    Nairobi: [
      "Dagoretti",
      "Embakasi",
      "Kamukunji",
      "Kasarani",
      "Langata",
      "Makadara",
      "Mathare",
      "Njiru",
      "Starehe",
      "Westlands",
    ],
    Baringo: [
      "Baringo Central",
      "Baringo North",
      "Baringo South",
      "Eldama Ravine",
      "Mogotio",
      "Tiaty",
    ],
  };
  const constituencies = {
    "Nakuru Town East": ["Biashara", "Kivumbini", "Menengai", "Nakuru East"],
    "Nakuru Town West": ["London", "Kaptembwo", "Rhoda", "Shaabab"],
    Naivasha: [
      "Biashara",
      "Hell's Gate",
      "Lake View",
      "Maiella",
      "Mai Mahiu",
      "Olkaria",
      "Viwandani",
    ],
    Gilgil: [
      "Gilgil",
      "Elementaita",
      "Mbaruk/Eburu",
      "Malewa West",
      "Murindat",
    ],
    Subukia: ["Subukia", "Waseges", "Kabazi"],
    Rongai: ["Menengai West", "Soin", "Visoi", "Mosop", "Solai"],
    Bahati: ["Bahati", "Kabatini", "Kiamaina", "Lanet/Umoja", "Dundori"],
    Njoro: ["Njoro", "Mau Narok", "Mauche", "Kihingo", "Nessuit", "Lare"],
    Molo: ["Molo", "Turi", "Mariashoni", "Elburgon"],
    "Kuresoi North": ["Kiptororo", "Nyota", "Sirikwa", "Kamara"],
    "Kuresoi South": ["Amalo", "Keringet", "Kiptagich", "Tinet"],
    "Bomet Central": [
      "Silibwet Township",
      "Ndaraweta",
      "Singorwet",
      "Chesoen",
      "Mutarakwa",
    ],
    "Bomet East": ["Merigi", "Kembu", "Longisa", "Kipreres", "Chemaner"],
    Chepalungu: ["Kongasis", "Siongiroi", "Chebunyo", "Nyangores"],
    Sotik: [
      "Ndanai/Abosi",
      "Chemagel",
      "Kipsonoi",
      "Kapletundo",
      "Rongena/Manaret",
    ],
    Konoin: ["Chepchabas", "Kimulot", "Mogogosiek", "Boito", "Embomos"],
    "Narok North": [
      "Olposimoru",
      "Olokurto",
      "Narok Town",
      "Nkareta",
      "Olorropil",
    ],
    "Narok South": ["Melili", "Loita", "Sogoo", "Sagamian", "Ololulung'a"],
    "Narok East": ["Keekonyokie", "Mosiro", "Ildamat", "Suswa"],
    "Narok West": ["Ilmotiok", "Mara", "Siana", "Naikarra"],
  };
  const [filteredSubCounties, setFilteredSubCounties] = useState([]);
  const [filteredConstituencies, setFilteredConstituencies] = useState([]);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    if (formData.county) {
      setFilteredSubCounties(subCounties[formData.county] || []);
      setFormData((prev) => ({ ...prev, sub_county: "", constituency: "" }));
    }
  }, [formData.county]);

  useEffect(() => {
    if (formData.sub_county) {
      setFilteredConstituencies(constituencies[formData.sub_county] || []);
      setFormData((prev) => ({ ...prev, constituency: "" }));
    }
  }, [formData.sub_county]);

  const validateForm = () => {
    if (!formData.group_name.trim()) {
      setError("Group name is required");
      return false;
    }
    if (!formData.county) {
      setError("County is required");
      return false;
    }
    if (!formData.sub_county) {
      setError("Sub County is required");
      return false;
    }
    if (!formData.constituency) {
      setError("Constituency is required");
      return false;
    }
    if (!formData.ward.trim()) {
      setError("Ward is required");
      return false;
    }
    return true;
  };
  const resetForm = () => {
    setFormData({
      group_name: "",
      registration_date: new Date().toISOString().split("T")[0],
      county: "",
      sub_county: "",
      constituency: "",
      ward: "",
      location: "",
      sub_location: "",
      village: "",
    });
    setError(null);
    setSuccessMessage(null);
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/groups/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (result.success) {
        setSuccessMessage("Group created successfully!");
        resetForm();
      } else {
        throw new Error(result.error || "Failed to create group");
      }
    } catch (error) {
      console.error("Error creating group:", error);
      setError(error.message || "Failed to create group. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
    setSuccessMessage(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6 transform transition-all hover:scale-[1.02]">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Register New Group
          </h2>

          {successMessage && (
            <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg flex items-center justify-between">
              <span>{successMessage}</span>
              <button
                onClick={() => setSuccessMessage(null)}
                className="text-green-700 hover:text-green-900"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-700 hover:text-red-900"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="rounded-xl bg-white p-6 shadow-sm border border-gray-100">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Group Name
                  </label>
                  <input
                    type="text"
                    name="group_name"
                    value={formData.group_name}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Registration Date
                  </label>
                  <input
                    type="date"
                    name="registration_date"
                    value={formData.registration_date}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    County
                  </label>
                  <select
                    name="county"
                    value={formData.county}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="">Select County</option>
                    {counties.map((county) => (
                      <option key={county} value={county}>
                        {county}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Sub County
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      name="sub_county"
                      value={formData.sub_county}
                      onChange={handleChange}
                      list="subCountyList"
                      required
                      className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="Type or select sub county"
                    />
                    <datalist id="subCountyList">
                      {filteredSubCounties.map((subCounty) => (
                        <option key={subCounty} value={subCounty} />
                      ))}
                    </datalist>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Constituency
                  </label>
                  <select
                    name="constituency"
                    value={formData.constituency}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="">Select Constituency</option>
                    {filteredConstituencies.map((constituency) => (
                      <option key={constituency} value={constituency}>
                        {constituency}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Ward
                  </label>
                  <input
                    type="text"
                    name="ward"
                    value={formData.ward}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Sub Location
                  </label>
                  <input
                    type="text"
                    name="sub_location"
                    value={formData.sub_location}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Village
                  </label>
                  <input
                    type="text"
                    name="village"
                    value={formData.village}
                    onChange={handleChange}
                    required
                    className="mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex justify-center py-3 px-6 border border-transparent shadow-sm text-base font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transform transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Registering..." : "Register Group"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default MainComponent;