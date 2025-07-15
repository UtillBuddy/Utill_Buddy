"use client";

import { useState } from "react";
import axios from "axios";

export default function UploadCv() {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      await axios.post("/api/upload-cv", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
      alert("CV uploaded successfully!");
    } catch (error) {
      console.error(error);
      alert("Failed to upload CV.");
    }
  };

  return (
    <div>
      <h1>Upload CV</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
