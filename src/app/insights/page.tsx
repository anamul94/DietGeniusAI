"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import { CalendarIcon, FileText, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

interface AIAssessmentSummary {
  id: number;
  user_id: number;
  date_value: string;
  summary: string;
  created_at: string;
  updated_at: string;
}

export default function InsightsPage() {
  const [targetDate, setTargetDate] = useState<Date | undefined>(new Date());
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [assessment, setAssessment] = useState<AIAssessmentSummary | null>(null);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }
    setIsAuthenticated(true);
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, [router]);

  const startAssessment = async () => {
    const token = localStorage.getItem('access_token');
    if (!token || !targetDate || !sessionId) return;

    setIsGenerating(true);
    setError(null);
    setStreamingContent('');
    setAssessment(null);
    setCurrentProgress(0);

    try {
      const params = new URLSearchParams({
        target_date: format(targetDate, 'yyyy-MM-dd'),
        token: token,
        sse_session_id: sessionId
      });

      const es = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/daily-activity/stream/generate-assessment?${params}`
      );

      setEventSource(es);

      es.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleStreamMessage(message);
      };

      es.onerror = (error) => {
        console.error('EventSource error:', error);
        if (es.readyState === EventSource.CLOSED) {
          setError('Connection lost - please try again');
          setIsGenerating(false);
        }
      };

    } catch (error) {
      setError('Failed to start assessment generation');
      setIsGenerating(false);
    }
  };

  const handleStreamMessage = (message: any) => {
    switch (message.type) {
      case 'connected':
        console.log('SSE connection opened');
        break;
      
      case 'progress':
        setCurrentProgress(message.value);
        break;
      
      case 'chunk':
        setStreamingContent(prev => prev + message.data);
        break;
      
      case 'complete':
        setAssessment({
          id: Date.now(),
          user_id: 0,
          date_value: message.date_value,
          summary: message.full_response,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
        setStreamingContent('');
        setIsGenerating(false);
        setCurrentProgress(100);
        if (eventSource) {
          eventSource.close();
          setEventSource(null);
        }
        break;
      
      case 'error':
        setError(message.error || 'Error generating assessment');
        setIsGenerating(false);
        if (eventSource) {
          eventSource.close();
          setEventSource(null);
        }
        break;
    }
  };

  const resetAssessment = () => {
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
    }
    setIsGenerating(false);
    setCurrentProgress(0);
    setStreamingContent('');
    setAssessment(null);
    setError(null);
  };

  const getDisplayContent = () => {
    if (isGenerating && streamingContent) {
      return (
        <div className="prose prose-sm max-w-none">
          <div className="text-sm text-gray-500 mb-2">Generating assessment...</div>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {streamingContent}
          </ReactMarkdown>
        </div>
      );
    }
    
    if (assessment) {
      return (
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {assessment.summary}
          </ReactMarkdown>
        </div>
      );
    }
    
    return (
      <div className="text-center py-12">
        <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Assessment Generated</h3>
        <p className="text-gray-500">
          Select a date and click "Generate Assessment" to get your personalized health insights
        </p>
      </div>
    );
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Insights</h1>
        <p className="text-gray-600">Generate personalized health assessments based on your daily activity and nutrition data</p>
      </div>

      <div className="grid gap-6">
        {/* Generate Assessment Card */}
        <Card>
          <CardHeader>
            <CardTitle>Generate Daily Assessment</CardTitle>
            <CardDescription>
              Get AI-powered insights about your health based on your daily activity and nutrition data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Date
                  </label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-[240px] justify-start text-left font-normal"
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {targetDate ? format(targetDate, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={targetDate}
                        onSelect={setTargetDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                
                <div className="flex items-end space-x-2">
                  <Button
                    onClick={startAssessment}
                    disabled={!targetDate || isGenerating || !sessionId}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isGenerating ? 'Generating...' : 'Generate Assessment'}
                  </Button>
                  
                  {isGenerating && (
                    <Button
                      onClick={resetAssessment}
                      variant="outline"
                      className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </div>

              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{currentProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${currentProgress}%` }}
                    />
                  </div>
                  <div className="text-sm text-gray-500">
                    Status: {eventSource ? 'Connected' : 'Connecting...'}
                  </div>
                </div>
              )}

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Assessment Result */}
        <Card>
          <CardHeader>
            <CardTitle>Assessment Result</CardTitle>
            <CardDescription>
              {targetDate ? `Health insights for ${format(targetDate, 'MMMM d, yyyy')}` : 'Select a date to view assessment'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {getDisplayContent()}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Access other health features</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={() => router.push('/previous-insights')}
                variant="outline"
                className="w-full justify-start"
              >
                <FileText className="mr-2 h-4 w-4" />
                View Previous Insights
              </Button>
              <Button
                onClick={() => router.push('/dashboard')}
                variant="outline"
                className="w-full justify-start"
              >
                <Activity className="mr-2 h-4 w-4" />
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {sessionId && (
        <div className="text-xs text-gray-500 mt-4 text-center">
          Session ID: {sessionId}
        </div>
      )}
    </div>
  );
}