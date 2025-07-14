"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

const GoogleHealthDataFetcher = () => {
  const [dataTypes, setDataTypes] = useState<string[]>(["steps"]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setDataTypes((prev) =>
      checked ? [...prev, value] : prev.filter((type) => type !== value)
    );
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    setData(null);

    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No authentication token found.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8000/api/google-health/data/fetch-and-save",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            data_types: dataTypes,
            start_date: startDate ? new Date(startDate).toISOString() : undefined,
            end_date: endDate ? new Date(endDate).toISOString() : undefined,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch data");
      }

      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Fetch Google Health Data</h3>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Data Types:</label>
        <div className="mt-1 grid grid-cols-2 gap-2">
          {[ "steps", "heart_rate", "sleep", "weight", "nutrition" ].map((type) => (
            <label key={type} className="inline-flex items-center">
              <input
                type="checkbox"
                value={type}
                checked={dataTypes.includes(type)}
                onChange={handleCheckboxChange}
                className="form-checkbox"
              />
              <span className="ml-2 text-gray-700">{type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}</span>
            </label>
          ))}
        </div>
      </div>
      <div className="mb-4">
        <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">Start Date:</label>
        <input
          type="date"
          id="startDate"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">End Date:</label>
        <input
          type="date"
          id="endDate"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>
      <button
        onClick={fetchData}
        disabled={loading}
        className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-blue-300"
      >
        {loading ? "Fetching..." : "Fetch Health Data"}
      </button>

      {error && <p className="text-red-500 mt-4">Error: {error}</p>}

      {data && data.items && data.items.length > 0 && (
        <div className="mt-4">
          <h4 className="text-lg font-semibold mb-2">Fetched Data:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.items.map((item: any, index: number) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-md">{item.data_type.replace(/_/g, " ").replace(/\b\w/g, (l: string) => l.toUpperCase())}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm">
                  <p><strong>Start Time:</strong> {new Date(item.start_time).toLocaleString()}</p>
                  <p><strong>End Time:</strong> {new Date(item.end_time).toLocaleString()}</p>
                  <p><strong>Value:</strong> {JSON.stringify(item.value)}</p>
                  {item.source && <p><strong>Source:</strong> {item.source}</p>}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
      {data && data.items && data.items.length === 0 && (
        <p className="mt-4 text-gray-600">No data found for the selected criteria.</p>
      )}
    </div>
  );
};

export default GoogleHealthDataFetcher;
