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
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Checkout</h1>
      <h2>{plan.name}</h2>
      <p>
        ${plan.price / 100} / {plan.emails} emails
      </p>
      <button onClick={handleCheckout}>Checkout</button>
    </div>
  );
}
