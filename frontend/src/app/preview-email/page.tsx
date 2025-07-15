"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function PreviewEmail() {
  const [html, setHtml] = useState("");

  useEffect(() => {
    const fetchPreview = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("/api/preview-email", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setHtml(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchPreview();
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-4xl p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Email Preview</h1>
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </div>
  );
}
