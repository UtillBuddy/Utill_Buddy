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
    <div>
      <h1>Email Configuration</h1>
      <select value={provider} onChange={(e) => setProvider(e.target.value)}>
        <option value="gmail">Gmail</option>
        <option value="outlook">Outlook</option>
        <option value="yahoo">Yahoo</option>
      </select>
      <textarea
        placeholder='JSON credentials (e.g., {"credentials_base64": "...", "token_base64": "..."})'
        value={credentials}
        onChange={(e) => setCredentials(e.targe.value)}
      />
      <button onClick={handleSaveConfig}>Save Configuration</button>
      <hr />
      <button onClick={() => window.location.href = "/outlook/login"}>
        Connect with Outlook
      </button>
    </div>
  );
}
