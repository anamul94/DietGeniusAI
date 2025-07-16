'use client';

import { useState } from 'react';
import { useSSE } from '@/lib/sse-client';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/button';

interface StreamingTestProps {
  apiUrl?: string;
}

export default function StreamingTest({ apiUrl = 'http://localhost:8000/api' }: StreamingTestProps) {
  const [sessionId, setSessionId] = useState(`test-${Date.now()}`);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const {
    messages,
    isConnected,
    error,
    connect,
    disconnect,
    clearMessages,
  } = useSSE(`${apiUrl}/streaming/test-stream`, {
    autoConnect: false,
  });

  const startStreaming = () => {
    setIsGenerating(true);
    clearMessages();
    connect();
  };

  const stopStreaming = () => {
    setIsGenerating(false);
    disconnect();
  };

  const startMealPlanStream = () => {
    setIsGenerating(true);
    clearMessages();
    connect();
  };

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Streaming API Test</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Session ID</label>
              <input
                type="text"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Enter session ID"
              />
            </div>

            <div className="flex gap-4">
              <Button
                onClick={startStreaming}
                disabled={isConnected || isGenerating}
                variant="default"
              >
                Start Test Stream
              </Button>
              
              <Button
                onClick={startMealPlanStream}
                disabled={isConnected || isGenerating}
                variant="default"
              >
                Start Meal Plan Stream
              </Button>
              
              <Button
                onClick={stopStreaming}
                disabled={!isConnected}
                variant="destructive"
              >
                Stop Stream
              </Button>
              
              <Button
                onClick={clearMessages}
                variant="outline"
              >
                Clear Messages
              </Button>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {error && (
                <span className="text-sm text-red-600">{error}</span>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Stream Messages</h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-gray-500">No messages yet. Start a stream to see data.</p>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 rounded-md text-sm"
                >
                  <div className="flex justify-between items-start">
                    <span className="font-medium text-blue-600">{message.type}</span>
                    {message.timestamp && (
                      <span className="text-xs text-gray-500">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  
                  {message.message && (
                    <p className="mt-1 text-gray-700">{message.message}</p>
                  )}
                  
                  {message.progress !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{message.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${message.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {message.data && (
                    <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                      {JSON.stringify(message.data, null, 2)}
                    </pre>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}