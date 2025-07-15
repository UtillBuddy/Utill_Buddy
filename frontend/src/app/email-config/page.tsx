"use client";

import { useState } from "react";
import axios from "axios";

export default function EmailConfig() {
  const [provider, setProvider] = useState("gmail");
  const [credentials, setCredentials] = useState("");
  const [server, setServer] = useState("");
  const [port, setPort] = useState(587);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [yahooAppPassword, setYahooAppPassword] = useState("");
  const [zohoClientId, setZohoClientId] = useState("");
  const [zohoClientSecret, setZohoClientSecret] = useState("");

  const handleSaveGmailConfig = async () => {
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

  const handleSaveSmtpConfig = async () => {
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
        <h1 className="text-2xl font-bold text-center">Email Configuration</h1>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="gmail">Gmail</option>
          <option value="outlook">Outlook</option>
          <option value="yahoo">Yahoo</option>
          <option value="zoho">Zoho</option>
          <option value="smtp">Custom SMTP</option>
        </select>

        {provider === "gmail" && (
          <>
            <textarea
              placeholder='JSON credentials (e.g., {"credentials_base64": "...", "token_base64": "..."})'
              value={credentials}
              onChange={(e) => setCredentials(e.target.value)}
              className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSaveGmailConfig}
              className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Save Gmail Configuration
            </button>
          </>
        )}

        {provider === "outlook" && (
          <button
            onClick={() => (window.location.href = "/outlook/login")}
            className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Connect with Outlook
          </button>
        )}

        {provider === "yahoo" && (
          <>
            <input
              type="password"
              placeholder="Yahoo App Password"
              value={yahooAppPassword}
              onChange={(e) => setYahooAppPassword(e.target.value)}
              className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              // onClick={handleSaveYahooConfig}
              className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Save Yahoo Configuration
            </button>
          </>
        )}

        {provider === "zoho" && (
          <>
            <input
              type="text"
              placeholder="Zoho Client ID"
              value={zohoClientId}
              onChange={(e) => setZohoClientId(e.target.value)}
              className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Zoho Client Secret"
              value={zohoClientSecret}
              onChange={(e) => setZohoClientSecret(e.target.value)}
              className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              // onClick={handleSaveZohoConfig}
              className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Save Zoho Configuration
            </button>
          </>
        )}

        {provider === "smtp" && (
          <>
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
              onClick={handleSaveSmtpConfig}
              className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Save SMTP Configuration
            </button>
          </>
        )}
      </div>
    </div>
  );
}
