import dynamic from "next/dynamic";
import { Suspense } from "react";

const MealPlanClientPage = dynamic(() => import("./MealPlanClientPage"), {
  ssr: false,
});

export default function MealPlanPage() {
  return (
    <Suspense fallback={<div>Loading meal plan...</div>}>
      <MealPlanClientPage />
    </Suspense>
  );
}