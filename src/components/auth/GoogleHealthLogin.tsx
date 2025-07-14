"use client";

import { useState } from "react";

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
    <div>
      <button onClick={handleLogin}>Connect to Google Health</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default GoogleHealthLogin;
