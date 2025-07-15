"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import io from "socket.io-client";

export default function Dashboard() {
  const [stats, setStats] = useState({ total: 0, sent: 0, pending: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("/api/status", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setStats(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchStats();

    const socket = io("http://localhost:8000", { path: "/ws/socket.io" });
    socket.on("email_sent", (data) => {
      if (data.user_id === localStorage.getItem("user_id")) {
        fetchStats();
      }
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Dashboard</h1>
        <div className="flex justify-between">
          <div className="p-4 text-center bg-gray-200 rounded-md">
            <p className="text-lg font-bold">{stats.total}</p>
            <p className="text-gray-600">Total Emails</p>
          </div>
          <div className="p-4 text-center bg-gray-200 rounded-md">
            <p className="text-lg font-bold">{stats.sent}</p>
            <p className="text-gray-600">Sent Emails</p>
          </div>
          <div className="p-4 text-center bg-gray-200 rounded-md">
            <p className="text-lg font-bold">{stats.pending}</p>
            <p className="text-gray-600">Pending Emails</p>
          </div>
        </div>
      </div>
    </div>
  );
}
