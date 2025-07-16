import AssessmentStreaming from '@/components/AssessmentStreaming';

export default function AssessmentStreamingPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Daily Assessment Streaming</h1>
        <AssessmentStreaming />
      </div>
    </div>
  );
}