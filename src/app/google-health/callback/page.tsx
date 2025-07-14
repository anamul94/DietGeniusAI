"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function GoogleHealthCallbackContent() {
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const authCode = searchParams.get("code");
    const redirectUri = window.location.href.split("?")[0];

    if (authCode) {
        const token = localStorage.getItem("access_token");

      if (token) {
        fetch("http://localhost:8000/api/google-health/auth/callback", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            code: authCode,
            redirect_uri: redirectUri,
          }),
        })
          .then(async (res) => {
            if (res.ok) {
              window.location.href = "/dashboard";
            } else {
              const errorData = await res.json();
              setError(errorData.detail || "Failed to exchange auth code");
            }
          })
          .catch((err) => {
            setError("An error occurred during the callback process.");
          })
          .finally(() => {
            setLoading(false);
          });
      } else {
        setError("No authentication token found.");
        setLoading(false);
      }
    } else {
      setError("No authorization code found in the URL.");
      setLoading(false);
    }
  }, [searchParams]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return <div>Successfully authenticated! Redirecting...</div>;
};

export default function GoogleHealthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    }>
      <GoogleHealthCallbackContent />
    </Suspense>
  );
}