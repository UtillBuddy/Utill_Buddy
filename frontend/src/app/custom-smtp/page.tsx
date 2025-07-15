"use client";

import { useState } from "react";
import axios from "axios";

export default function CustomSmtp() {
  const [server, setServer] = useState("");
  const [port, setPort] = useState(587);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSaveConfig = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "/api/verify-smtp-creds",
        { server, port, username, password },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("SMTP config saved successfully!");
    } catch (error) {
      console.error(error);
      alert("Failed to save SMTP config.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">
          Custom SMTP Configuration
        </h1>
        <input
          type="text"
          placeholder="SMTP Server"
          value={server}
          onChange={(e) => setServer(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="number"
          placeholder="Port"
          value={port}
          onChange={(e) => setPort(parseInt(e.target.value))}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSaveConfig}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
}
