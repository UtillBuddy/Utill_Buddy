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
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="w-full max-w-md p-8 space-y-6 bg-surface rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-primary">Dashboard</h1>
        <div className="flex justify-between">
          <div className="p-4 text-center bg-background rounded-md">
            <p className="text-lg font-bold text-primary">{stats.total}</p>
            <p className="text-secondary">Total Emails</p>
          </div>
          <div className="p-4 text-center bg-background rounded-md">
            <p className="text-lg font-bold text-success">{stats.sent}</p>
            <p className="text-secondary">Sent Emails</p>
          </div>
          <div className="p-4 text-center bg-background rounded-md">
            <p className="text-lg font-bold text-error">{stats.pending}</p>
            <p className="text-secondary">Pending Emails</p>
          </div>
        </div>
      </div>
    </div>
  );
}
