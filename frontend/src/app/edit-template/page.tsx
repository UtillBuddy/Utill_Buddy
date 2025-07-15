"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function EditTemplate() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [cvLink, setCvLink] = useState("");

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("/api/template", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setSubject(response.data.subject);
        setBody(response.data.body);
        setCvLink(response.data.cv_link);
      } catch (error) {
        console.error(error);
      }
    };

    fetchTemplate();
  }, []);

  const handleUpdateTemplate = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.put(
        "/api/update-template",
        { subject, body, cv_link: cvLink },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("Template updated successfully!");
    } catch (error) {
      console.error(error);
      alert("Failed to update template.");
    }
  };

  return (
    <div>
      <h1>Edit Email Template</h1>
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
      <button onClick={handleUpdateTemplate}>Update Template</button>
    </div>
  );
}
