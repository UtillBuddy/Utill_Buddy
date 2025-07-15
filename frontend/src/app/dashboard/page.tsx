"use client";

import { useState, useEffect } from "react";
import axios from "axios";

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
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total Emails: {stats.total}</p>
      <p>Sent Emails: {stats.sent}</p>
      <p>Pending Emails: {stats.pending}</p>
    </div>
  );
}
