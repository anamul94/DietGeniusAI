'use client'

import MealPlanGenerator from "@/components/meal-plan/MealPlanGenerator";
import { useSearchParams } from "next/navigation";

export default function MealPlanClientPage() {
  const searchParams = useSearchParams();
  const mode = searchParams.get("mode") || "generate"; // Default to generate

  return <MealPlanGenerator mode={mode as "generate" | "latest"} />;
}