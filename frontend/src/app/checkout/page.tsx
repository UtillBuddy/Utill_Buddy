"use client";

import { useState, useEffect } from "react";
import { loadStripe } from "@stripe/stripe-js";
import axios from "axios";

const stripePromise = loadStripe("your_stripe_public_key");

export default function Checkout() {
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const response = await axios.get("/api/plans");
        setPlan(response.data[0]);
      } catch (error) {
        console.error(error);
      }
    };

    fetchPlan();
  }, []);

  const handleCheckout = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "/api/create-checkout-session",
        { plan_id: plan._id },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const stripe = await stripePromise;
      await stripe.redirectToCheckout({ sessionId: response.data.id });
    } catch (error) {
      console.error(error);
    }
  };

  if (!plan) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center">Checkout</h1>
        <div className="p-4 text-center bg-gray-200 rounded-md">
          <h2 className="text-lg font-bold">{plan.name}</h2>
          <p className="text-gray-600">
            ${plan.price / 100} / {plan.emails} emails
          </p>
        </div>
        <button
          onClick={handleCheckout}
          className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Checkout
        </button>
      </div>
    </div>
  );
}
