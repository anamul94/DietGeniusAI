"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button"; // Import the Button component

const GoogleHealthLogin = () => {
  const [error, setError] = useState<string | null>(null);

  const handleLogin = () => {
    fetch("http://localhost:8000/api/google-health/auth-url")
      .then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          window.location.href = data.auth_url;
        } else {
          const errorData = await res.json();
          setError(errorData.detail || "Failed to get auth URL");
        }
      })
      .catch((err) => {
        setError("An error occurred during the login process.");
      });
  };

  return (
    <div className="p-2">
      <Button onClick={handleLogin} className="w-full">Connect to Google Health</Button>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>
  );
};

export default GoogleHealthLogin;
