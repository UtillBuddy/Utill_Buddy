"use client";

import { useState } from "react";
import axios from "axios";

export default function Payment() {
  const [promoCode, setPromoCode] = useState("");

  const handleValidatePromoCode = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `/api/promo?promo_code=${promoCode}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert("Promo code validated successfully!");
    } catch (error) {
      console.error(error);
      alert("Invalid promo code.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Payment</h1>
        <input
          type="text"
          placeholder="Promo Code"
          value={promoCode}
          onChange={(e) => setPromoCode(e.target.value)}
          className="w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleValidatePromoCode}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Validate Promo Code
        </button>
      </div>
    </div>
  );
}
