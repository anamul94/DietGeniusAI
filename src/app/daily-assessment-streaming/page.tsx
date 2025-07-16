'use client';

import DailyAssessmentStreaming from '@/components/DailyAssessmentStreaming';

export default function DailyAssessmentStreamingPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Daily Health Assessment</h1>
        <DailyAssessmentStreaming />
      </div>
    </div>
  );
}