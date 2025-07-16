"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { format, subDays } from 'date-fns';
import { ChevronLeft, Calendar } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AIAssessmentSummary {
  id: number;
  user_id: number;
  date_value: string;
  summary: string;
  created_at: string;
  updated_at: string;
}

export default function PreviousInsightsPage() {
  const [assessments, setAssessments] = useState<AIAssessmentSummary[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [loading, setLoading] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState<AIAssessmentSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }
    setIsAuthenticated(true);
    fetchPreviousAssessments();
  }, [router]);

  const fetchPreviousAssessments = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // Get date range for the last 30 days
      const endDate = new Date();
      const startDate = subDays(endDate, 30);
      
      const params = new URLSearchParams({
        start_date: format(startDate, 'yyyy-MM-dd'),
        end_date: format(endDate, 'yyyy-MM-dd')
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/daily-activity/assessments?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('access_token');
          router.push('/');
          return;
        }
        throw new Error('Failed to fetch assessments');
      }

      const data = await response.json();
      setAssessments(data);
      
      // If we have assessments, select the most recent one
      if (data.length > 0) {
        const latest = data[0];
        setSelectedAssessment(latest);
        setSelectedDate(new Date(latest.date_value));
      }
    } catch (error) {
      setError('Failed to load previous insights');
      console.error('Error fetching assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssessmentByDate = async (date: Date) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }

    try {
      const dateStr = format(date, 'yyyy-MM-dd');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/daily-activity/assessment/${dateStr}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSelectedAssessment(data);
      } else if (response.status === 401) {
        localStorage.removeItem('access_token');
        router.push('/');
      } else {
        setSelectedAssessment(null);
      }
    } catch (error) {
      setError('Failed to fetch assessment for selected date');
      console.error('Error fetching assessment:', error);
    }
  };

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      setSelectedDate(date);
      fetchAssessmentByDate(date);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-6">
        <button
          onClick={() => router.push('/dashboard')}
          className="mb-4 flex items-center px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Previous Health Insights</h1>
        <p className="text-gray-600">View your historical health assessments and insights</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Date Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Select Date</h3>
            <p className="text-sm text-gray-600 mb-4">Choose a date to view your health assessment</p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Assessments
                </label>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {loading ? (
                    <div className="text-center py-4">
                      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                      <p className="text-sm text-gray-500 mt-2">Loading assessments...</p>
                    </div>
                  ) : assessments.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">No assessments found</p>
                  ) : (
                    assessments.map((assessment) => (
                      <button
                        key={assessment.id}
                        onClick={() => {
                          const date = new Date(assessment.date_value);
                          setSelectedDate(date);
                          setSelectedAssessment(assessment);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                          selectedAssessment?.id === assessment.id
                            ? 'bg-blue-100 text-blue-900 border border-blue-200'
                            : 'hover:bg-gray-50 border border-gray-200'
                        }`}
                      >
                        <div className="font-medium">{format(new Date(assessment.date_value), 'MMMM d, yyyy')}</div>
                        <div className="text-xs text-gray-500">
                          Created: {format(new Date(assessment.created_at), 'MMM d, yyyy h:mm a')}
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Assessment Display */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Health Assessment</h3>
              <p className="text-sm text-gray-600">
                {selectedDate ? format(selectedDate, 'MMMM d, yyyy') : 'Select a date to view assessment'}
              </p>
            </div>
            
            <div className="p-6">
              {selectedAssessment ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedAssessment.summary}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Assessment Selected</h3>
                  <p className="text-gray-500">
                    {loading ? 'Loading assessments...' : 'Select a date from the left to view your health assessment'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}