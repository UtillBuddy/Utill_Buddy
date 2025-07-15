"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";

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
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-2xl p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Edit Email Template</h1>
        <input
          type="text"
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <ReactQuill value={body} onChange={setBody} />
        <input
          type="text"
          placeholder="CV Link"
          value={cvLink}
          onChange={(e) => setCvLink(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleUpdateTemplate}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Update Template
        </button>
      </div>
    </div>
  );
}
