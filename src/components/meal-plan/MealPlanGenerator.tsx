"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/button";
import { apiCall } from "@/lib/utils";
import { Brain, Loader2, ArrowLeft } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useRouter } from "next/navigation";
import Image from "next/image";

interface MealPlan {
  meal_plan: string;
  plan_date: string;
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

interface MealPlanGeneratorProps {
  mode?: "generate" | "latest";
}

const MealPlanGenerator = ({ mode }: MealPlanGeneratorProps) => {
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

  useEffect(() => {
    if (sessionId) {
      if (mode === "generate") {
        generateMealPlan();
      } else if (mode === "latest") {
        fetchLatestMealPlan();
      }
    }
  }, [sessionId, mode]);

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

            {loading ? (
              <div className="relative h-64 bg-gray-100 rounded-lg overflow-hidden">
                <Image
                  src="/nutritionist-preparing-meal-plan.jpg"
                  alt="Nutritionist preparing meal plan"
                  layout="fill"
                  objectFit="cover"
                  className="opacity-50"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="bg-white bg-opacity-75 p-6 rounded-lg text-center">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                    <p className="text-lg font-semibold text-gray-800">
                      Our nutritionist is carefully preparing your personalized meal plan...
                    </p>
                    <p className="text-sm text-gray-600 mt-2">
                      This may take a few moments. Please wait.
                    </p>
                  </div>
                </div>
              </div>
            ) : mealPlan ? (
              <div className="prose max-w-none">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Meal Plan for {mealPlan.plan_date}
                </h3>
                {typeof mealPlan.meal_plan === 'string' ? (
                  <ReactMarkdown>{mealPlan.meal_plan}</ReactMarkdown>
                ) : (
                  <p className="text-red-500">Error: Invalid meal plan data</p>
                )}
              </div>
            ) : (
              !error && (
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
