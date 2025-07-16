'use client';

import { useState, useEffect } from 'react';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface DailyAssessmentStreamingProps {
  apiUrl?: string;
}

export default function DailyAssessmentStreaming({ apiUrl = 'http://localhost:8000/api' }: DailyAssessmentStreamingProps) {
  const [targetDate, setTargetDate] = useState<Date | undefined>(new Date());
  const [sessionId, setSessionId] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [chunks, setChunks] = useState<string[]>([]);
  const [finalAssessment, setFinalAssessment] = useState<any>(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Generate unique session ID
  useEffect(() => {
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  const startAssessment = async () => {
    if (!targetDate || !sessionId) return;
    
    // Reset state
    setChunks([]);
    setFinalAssessment(null);
    setCurrentProgress(0);
    setError(null);
    setIsGenerating(true);
    
    // Check for authentication
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Please log in to generate assessments');
      setIsGenerating(false);
      return;
    }
    
    // Import SSE manager
    const { SSEConnectionManager } = await import('@/lib/sse-manager');
    const manager = new SSEConnectionManager();
    
    const url = `${apiUrl}/daily-activity-summary/stream/generate-assessment?sse_session_id=${sessionId}&target_date=${format(targetDate, 'yyyy-MM-dd')}&token=${token}`;
    
    const success = await manager.connect({
      url,
      onMessage: (message) => {
        console.log('Received message:', message.type);
        handleStreamMessage(message);
      },
      onError: (errorMessage) => {
        console.error('SSE Error:', errorMessage);
        setError(errorMessage);
        setIsGenerating(false);
      },
      onOpen: () => {
        console.log('SSE connection established');
        setError(null);
      },
      onClose: () => {
        console.log('SSE connection closed');
        setIsGenerating(false);
      },
      timeout: 8000
    });
    
    if (!success) {
      setIsGenerating(false);
    }
  };

  const handleStreamMessage = (message: any) => {
    console.log('Handling message:', message.type, message);
    switch (message.type) {
      case 'connected':
        setError(null);
        break;
      
      case 'progress':
        setCurrentProgress(message.progress || 0);
        break;
      
      case 'chunk':
        if (message.data && typeof message.data === 'string') {
          setChunks(prev => [...prev, message.data]);
        }
        break;
      
      case 'complete':
        console.log('Setting final assessment:', message);
        // Handle both direct data and nested data structure
        const assessmentData = message.data || message;
        setFinalAssessment(assessmentData);
        setIsGenerating(false);
        setCurrentProgress(100);
        setError(null); // Clear any previous errors
        setChunks([]); // Clear chunks to show only final response
        break;
      
      case 'error':
        setError(message.message || 'An error occurred');
        setIsGenerating(false);
        break;
    }
  };

  const resetAssessment = () => {
    setChunks([]);
    setFinalAssessment(null);
    setCurrentProgress(0);
    setError(null);
    setIsGenerating(false);
    
    // Generate new session ID
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  };

  const getDisplayContent = () => {
    if (finalAssessment) {
      console.log('Displaying final assessment:', finalAssessment);
      const dateValue = finalAssessment.date_value || format(new Date(), 'yyyy-MM-dd');
      const fullResponse = finalAssessment.summary || finalAssessment.full_response || 'No summary available';
      
      return (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Daily Health Assessment - {dateValue}</h3>
            <button
              onClick={resetAssessment}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              Generate New
            </button>
          </div>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{fullResponse}</ReactMarkdown>
          </div>
        </div>
      );
    }
    
    if (chunks.length > 0 && isGenerating) {
      return (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Generating Daily Health Assessment...</h3>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{chunks.join('')}</ReactMarkdown>
          </div>
        </div>
      );
    }
    
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Select a date and click "Generate Assessment" to start</p>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Daily Health Assessment Streaming</h2>
          <p className="text-sm text-gray-600">
            Generate AI-powered daily health assessments with real-time streaming
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Date</label>
              <Popover>
                <PopoverTrigger asChild>
                  <button
                    className={cn(
                      "w-[240px] justify-start text-left font-normal flex items-center px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50",
                      !targetDate && "text-muted-foreground"
                    )}
                    disabled={isGenerating}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {targetDate ? format(targetDate, "PPP") : "Pick a date"}
                  </button>
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
              <button
                onClick={startAssessment}
                disabled={!targetDate || isGenerating || !sessionId}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? 'Generating...' : 'Generate Assessment'}
              </button>
              
              {isGenerating && (
                <button
                  onClick={resetAssessment}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
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
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Assessment Result</h3>
        </div>
        {getDisplayContent()}
      </div>

      {sessionId && (
        <div className="text-xs text-gray-500">
          Session ID: {sessionId}
        </div>
      )}
    </div>
  );
}