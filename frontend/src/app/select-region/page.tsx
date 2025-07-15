"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function SelectRegion() {
  const [regions, setRegions] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState("");

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("/api/regions", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setRegions(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchRegions();
  }, []);

  const handleSendEmails = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `/api/send-emails?region=${selectedRegion}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("Email sending process started!");
    } catch (error) {
      console.error(error);
      alert("Failed to start email sending process.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Select Job Region</h1>
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a region</option>
          {regions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
        <button
          onClick={handleSendEmails}
          disabled={!selectedRegion}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400"
        >
          Send Emails
        </button>
      </div>
    </div>
  );
}
