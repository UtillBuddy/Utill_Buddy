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
    <div>
      <h1>Payment</h1>
      <input
        type="text"
        placeholder="Promo Code"
        value={promoCode}
        onChange={(e) => setPromoCode(e.target.value)}
      />
      <button onClick={handleValidatePromoCode}>Validate Promo Code</button>
    </div>
  );
}
