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
    <div>
      <h1>Select Job Region</h1>
      <select
        value={selectedRegion}
        onChange={(e) => setSelectedRegion(e.target.value)}
      >
        <option value="">Select a region</option>
        {regions.map((region) => (
          <option key={region} value={region}>
            {region}
          </option>
        ))}
      </select>
      <button onClick={handleSendEmails} disabled={!selectedRegion}>
        Send Emails
      </button>
    </div>
  );
}
