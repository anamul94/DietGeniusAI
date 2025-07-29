"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/button";
import { CalendarIcon, Loader2, ArrowLeft, Brain } from "lucide-react";
import MarkdownRenderer from "@/components/ui/MarkdownRenderer";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { format } from "date-fns";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";

interface MealPlan {
  meal_plan: string;
  plan_date: string;
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

interface MealPlanStreamingProps {
  mode?: "generate" | "latest";
}

const MealPlanStreaming = ({ mode }: MealPlanStreamingProps) => {
  const [targetDate, setTargetDate] = useState<Date | undefined>(new Date());
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [connectionState, setConnectionState] = useState<{
    isConnected: boolean;
    reconnectAttempts: number;
    connectionDuration: number;
    isHealthy: boolean;
  }>({
    isConnected: false,
    reconnectAttempts: 0,
    connectionDuration: 0,
    isHealthy: false
  });
  
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }
    
    // Set token in cookies for SSE authentication
    import('@/lib/auth-cookies').then(({ setAuthToken }) => {
      setAuthToken(token, 60); // 60 minutes
    });
    
    setIsAuthenticated(true);
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, [router]);

  // Connection monitoring effect
  useEffect(() => {
    if (!isGenerating) return;

    const monitorConnection = setInterval(async () => {
      const { EnhancedSSEConnectionManager } = await import('@/lib/sse-manager-enhanced-v2');
      const manager = new EnhancedSSEConnectionManager();
      const state = manager.getConnectionState();
      
      setConnectionState({
        isConnected: state.isConnected,
        reconnectAttempts: state.reconnectAttempts,
        connectionDuration: manager.getConnectionDuration(),
        isHealthy: manager.isHealthy()
      });
    }, 5000); // Update every 5 seconds

    return () => clearInterval(monitorConnection);
  }, [isGenerating]);

  const handleStreamMessage = (message: any) => {
    switch (message.type) {
      case 'connection':
        console.log('SSE connection opened');
        break;
      case 'progress':
        setCurrentProgress(message.progress || message.value || 0);
        break;
      case 'chunk':
        setStreamingContent(prev => prev + (message.data || message.content || ''));
        break;
      case 'complete':
        setMealPlan({
          meal_plan: message.full_response || message.meal_plan?.meal_plan || '',
          plan_date: message.plan_date || new Date().toISOString(),
          id: message.meal_plan?.id || 0,
          user_id: message.meal_plan?.user_id || 0,
          created_at: message.meal_plan?.created_at || new Date().toISOString(),
          updated_at: message.meal_plan?.updated_at || new Date().toISOString()
        });
        setIsGenerating(false);
        break;
      case 'end':
        // Final event to close connection
        setIsGenerating(false);
        break;
      case 'error':
        setError(message.message || 'An error occurred');
        setIsGenerating(false);
        break;
    }
  };

  const startMealPlanGeneration = async () => {
    const token = localStorage.getItem('access_token');
    if (!token || !sessionId) return;

    setIsGenerating(true);
    setError(null);
    setStreamingContent('');
    setMealPlan(null);
    setCurrentProgress(0);

    // Import enhanced SSE manager
    const { EnhancedSSEConnectionManager } = await import('@/lib/sse-manager-enhanced-v2');
    const { setAuthToken } = await import('@/lib/auth-cookies');
    
    const manager = new EnhancedSSEConnectionManager();

    // Set token in cookies for backup authentication
    setAuthToken(token, 60);

    // Build URL with session_id (token will be added automatically from cookies)
    const params = new URLSearchParams({
      session_id: sessionId
    });

    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meal-entries/stream/generate-meal-plan?${params}`;

    console.log('Starting meal plan generation with session:', sessionId);

    const success = await manager.connect({
      url,
      onMessage: (message) => {
        console.log('Received SSE message:', message);
        handleStreamMessage(message);
      },
      onError: (errorMessage) => {
        console.error('SSE Error:', errorMessage);
        setError(errorMessage);
        setIsGenerating(false);
      },
      onOpen: () => {
        console.log('SSE connection established successfully');
        setError(null);
      },
      onClose: () => {
        console.log('SSE connection closed');
        setIsGenerating(false);
      },
      onReconnect: (attempt) => {
        console.log(`SSE reconnection attempt ${attempt}`);
        setError(`Reconnecting... (attempt ${attempt})`);
      },
      timeout: 30000,
      maxReconnectAttempts: 10,
      reconnectInterval: 5000,
      heartbeatInterval: 30000
    });

    if (!success) {
      setIsGenerating(false);
    }
  };

  const fetchLatestMealPlan = async () => {
    setIsGenerating(true);
    setError(null);
    setStreamingContent('');
    setMealPlan(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meal-entries/meal-plans/latest`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch latest meal plan');
      }
      
      const data = await response.json();
      setMealPlan(data);
    } catch (err: any) {
      console.error('Failed to fetch latest meal plan:', err);
      setError(err.message || 'Failed to fetch latest meal plan');
    } finally {
      setIsGenerating(false);
    }
  };

  const resetMealPlan = () => {
    setIsGenerating(false);
    setCurrentProgress(0);
    setStreamingContent('');
    setMealPlan(null);
    setError(null);
  };

  const getDisplayContent = () => {
    if (isGenerating) {
      if (streamingContent) {
        return (
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Generating Meal Plan...
            </h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <MarkdownRenderer
                content={streamingContent}
                cacheKey={`streaming-${sessionId}`}
                className="text-sm"
              />
            </div>
          </div>
        );
      }
      
      return (
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
                Progress: {currentProgress}%
              </p>
            </div>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center text-red-500 py-4">
          <p>{error}</p>
        </div>
      );
    }

    if (mealPlan) {
      return (
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Meal Plan for {format(new Date(mealPlan.plan_date), 'MMMM d, yyyy')}
          </h3>
          {typeof mealPlan.meal_plan === 'string' ? (
            <MarkdownRenderer
              content={mealPlan.meal_plan}
              cacheKey={`mealplan-${mealPlan.id}`}
            />
          ) : (
            <p className="text-red-500">Error: Invalid meal plan data</p>
          )}
        </div>
      );
    }

    return (
      <p className="text-gray-500 text-center py-8">
        Select a date and click "Generate New Meal Plan" to get your personalized diet plan.
      </p>
    );
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
            <div className="space-y-6">
              {/* Date Selection */}
              <div className="flex flex-col sm:flex-row gap-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Date
                  </label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
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
                
                <div className="flex gap-2">
                  <Button 
                    onClick={startMealPlanGeneration} 
                    disabled={isGenerating || !sessionId}
                  >
                    {isGenerating ? (
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
                  
                  <Button 
                    onClick={fetchLatestMealPlan} 
                    disabled={isGenerating} 
                    variant="outline"
                  >
                    {isGenerating ? (
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
              </div>

              {/* Progress Bar */}
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

              {/* Error Display */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Connection Status Display */}
              {isGenerating && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${connectionState.isHealthy ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                      <span className="text-blue-700">
                        {connectionState.isConnected ? 'Connected' : 'Connecting...'}
                      </span>
                    </div>
                    <div className="text-blue-600">
                      {connectionState.connectionDuration > 0 && (
                        <span>Duration: {Math.floor(connectionState.connectionDuration / 1000)}s</span>
                      )}
                      {connectionState.reconnectAttempts > 0 && (
                        <span className="ml-2">Reconnects: {connectionState.reconnectAttempts}</span>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Main Content */}
              {getDisplayContent()}

              {/* Back Button */}
              <div className="mt-6">
                <Button variant="outline" onClick={() => router.back()}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {sessionId && (
          <div className="text-xs text-gray-500 mt-4 text-center">
            Session ID: {sessionId}
          </div>
        )}
      </div>
    </div>
  );
};

export default MealPlanStreaming;