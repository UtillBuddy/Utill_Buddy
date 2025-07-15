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
    <div>
      <h1>Custom SMTP Configuration</h1>
      <input
        type="text"
        placeholder="SMTP Server"
        value={server}
        onChange={(e) => setServer(e.target.value)}
      />
      <input
        type="number"
        placeholder="Port"
        value={port}
        onChange={(e) => setPort(parseInt(e.target.value))}
      />
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleSaveConfig}>Save Configuration</button>
    </div>
  );
}
