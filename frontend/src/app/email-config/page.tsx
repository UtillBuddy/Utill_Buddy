"use client";

import { useState } from "react";
import axios from "axios";

export default function EmailConfig() {
  const [provider, setProvider] = useState("gmail");
  const [credentials, setCredentials] = useState("");

  const handleSaveConfig = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "/api/verify-email-creds",
        { provider, credentials: JSON.parse(credentials) },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("Email config saved successfully!");
    } catch (error) {
      console.error(error);
      alert("Failed to save email config.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Email Configuration</h1>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="gmail">Gmail</option>
          <option value="outlook">Outlook</option>
          <option value="yahoo">Yahoo</option>
        </select>
        <textarea
          placeholder='JSON credentials (e.g., {"credentials_base64": "...", "token_base64": "..."})'
          value={credentials}
          onChange={(e) => setCredentials(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSaveConfig}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Save Configuration
        </button>
        <hr />
        <button
          onClick={() => (window.location.href = "/outlook/login")}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Connect with Outlook
        </button>
      </div>
    </div>
  );
}
