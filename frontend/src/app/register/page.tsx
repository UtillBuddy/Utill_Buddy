"use client";

import { useState } from "react";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/firebase";
import axios from "axios";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );
      const user = userCredential.user;
      const token = await user.getIdToken();

      await axios.post("/api/register", { email, password }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Redirect to login page
      window.location.href = "/login";
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="w-full max-w-md p-8 space-y-6 bg-surface rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-primary">Register</h1>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 text-secondary bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 text-secondary bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          onClick={handleRegister}
          className="w-full px-4 py-2 font-bold text-white bg-primary rounded-md hover:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-primary"
        >
          Register
        </button>
      </div>
    </div>
  );
}
