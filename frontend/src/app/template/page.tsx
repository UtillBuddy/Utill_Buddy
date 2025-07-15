"use client";

import { useState } from "react";
import axios from "axios";

export default function Template() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [cvLink, setCvLink] = useState("");

  const handleSaveTemplate = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "/api/setup-template",
        { subject, body, cv_link: cvLink },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("Template saved successfully!");
    } catch (error) {
      console.error(error);
      alert("Failed to save template.");
    }
  };

  return (
    <div>
      <h1>Setup Email Template</h1>
      <input
        type="text"
        placeholder="Subject"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />
      <textarea
        placeholder="Body"
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />
      <input
        type="text"
        placeholder="CV Link"
        value={cvLink}
        onChange={(e) => setCvLink(e.target.value)}
      />
      <button onClick={handleSaveTemplate}>Save Template</button>
    </div>
  );
}
