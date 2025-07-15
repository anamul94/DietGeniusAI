"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/button";
import { apiCall } from "@/lib/utils";
import { Brain, Loader2, ArrowLeft } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useRouter } from "next/navigation";

interface MealPlan {
  meal_plan: string;
  plan_date: string;
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

const MealPlanGenerator = () => {
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchSessionId = async () => {
      try {
        const sessionResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/medical-reports/generate-session-id/`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );
        if (!sessionResponse.ok) {
          throw new Error(
            `Failed to generate session ID: ${sessionResponse.statusText}`
          );
        }
        const sessionData = await sessionResponse.json();
        setSessionId(sessionData.session_id);
      } catch (err: any) {
        console.error("Error fetching session ID:", err);
        setError(err.message || "Failed to generate session ID.");
      }
    };
    fetchSessionId();
  }, []);

  const generateMealPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!sessionId) {
        throw new Error("Session ID not available. Please try again.");
      }
      const response = await apiCall(
        `/api/meal-entries/meal-plans/generate?session_id=${sessionId}`,
        { method: "POST" }
      );
      setMealPlan(response);
    } catch (err: any) {
      console.error("Failed to generate meal plan:", err);
      setError("Failed to generate meal plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestMealPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall("/api/meal-entries/meal-plans/latest", {
        method: "GET",
      });
      setMealPlan(response);
    } catch (err: any) {
      console.error("Failed to fetch latest meal plan:", err);
      setError("Failed to fetch latest meal plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Meal Plan</h1>
          <p className="text-gray-600">Generate and view your personalized meal plans</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              Your Meal Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-6">
              <Button onClick={generateMealPlan} disabled={loading || !sessionId}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Generate New Meal Plan
                  </>
                )}
              </Button>
              <Button onClick={fetchLatestMealPlan} disabled={loading} variant="outline">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    View Latest Meal Plan
                  </>
                )}
              </Button>
            </div>

            {error && (
              <div className="text-center text-red-500 py-4">
                <p>{error}</p>
              </div>
            )}

            {mealPlan ? (
              <div className="prose max-w-none">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Meal Plan for {mealPlan.plan_date}
                </h3>
                <ReactMarkdown>{mealPlan.meal_plan}</ReactMarkdown>
              </div>
            ) : (
              !loading && !error && (
                <p className="text-gray-500 text-center py-8">
                  Click "Generate New Meal Plan" to get your personalized diet plan.
                </p>
              )
            )}
            <div className="mt-6">
              <Button variant="outline" onClick={() => router.back()}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MealPlanGenerator;
