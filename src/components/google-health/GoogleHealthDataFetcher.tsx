"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/button"; // Import the Button component
import { Input } from "@/components/ui/input"; // Import the Input component
import { Label } from "@/components/ui/label"; // Import the Label component
import { Checkbox } from "@/components/ui/checkbox"; // Assuming you have a Checkbox component

const GoogleHealthDataFetcher = () => {
  const [dataTypes, setDataTypes] = useState<string[]>(["steps"]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (type: string, checked: boolean) => {
    setDataTypes((prev) =>
      checked ? [...prev, type] : prev.filter((t) => t !== type)
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
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Fetch Google Health Data</h3>
      <div>
        <Label className="mb-2 block">Data Types:</Label>
        <div className="grid grid-cols-2 gap-2">
          {[ "steps", "heart_rate", "sleep", "weight", "nutrition" ].map((type) => (
            <div key={type} className="flex items-center space-x-2">
              <Checkbox
                id={type}
                checked={dataTypes.includes(type)}
                onCheckedChange={(checked: boolean) => handleCheckboxChange(type, checked)}
              />
              <Label htmlFor={type}>
                {type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
              </Label>
            </div>
          ))}
        </div>
      </div>
      <div>
        <Label htmlFor="startDate" className="mb-2 block">Start Date:</Label>
        <Input
          type="date"
          id="startDate"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="endDate" className="mb-2 block">End Date:</Label>
        <Input
          type="date"
          id="endDate"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
      </div>
      <Button
        onClick={fetchData}
        disabled={loading}
        className="w-full"
      >
        {loading ? "Fetching..." : "Fetch Health Data"}
      </Button>

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
