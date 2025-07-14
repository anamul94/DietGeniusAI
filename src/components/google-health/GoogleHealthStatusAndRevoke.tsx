"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const GoogleHealthStatusAndRevoke = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revoking, setRevoking] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No authentication token found.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/google-health/status", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch status");
      }

      const result = await response.json();
      setStatus(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async () => {
    setRevoking(true);
    setError(null);
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No authentication token found.");
      setRevoking(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/google-health/revoke", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to revoke permission");
      }

      setStatus(null); // Clear status after revoking
      alert("Permissions revoked successfully!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRevoking(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (loading) {
    return <p>Loading Google Health status...</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  return (
    <Card className="p-4 border rounded-lg shadow-sm mt-4">
      <CardHeader>
        <CardTitle className="text-lg font-semibold mb-2">Google Health Connection Status</CardTitle>
      </CardHeader>
      <CardContent>
        {status && status.connected ? (
          <div className="space-y-2">
            <p><strong>Status:</strong> Connected</p>
            <p><strong>Expires At:</strong> {new Date(status.expires_at).toLocaleString()}</p>
            <p><strong>Scopes:</strong></p>
            <ul className="list-disc list-inside ml-4">
              {status.scopes.map((scope: string, index: number) => (
                <li key={index}>{scope}</li>
              ))}
            </ul>
            <Button onClick={handleRevoke} disabled={revoking} className="mt-4 bg-red-500 hover:bg-red-600 text-white">
              {revoking ? "Revoking..." : "Revoke Permissions"}
            </Button>
          </div>
        ) : (
          <p>Not connected to Google Health.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default GoogleHealthStatusAndRevoke;
