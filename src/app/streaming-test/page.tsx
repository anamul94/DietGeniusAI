import StreamingTest from '@/components/StreamingTest';

export default function StreamingTestPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Streaming API Test</h1>
        <StreamingTest />
      </div>
    </div>
  );
}