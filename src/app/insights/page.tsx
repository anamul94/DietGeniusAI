'use client'

import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { apiCall } from '@/lib/utils'
import { Activity, Brain, Loader2, ArrowLeft } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useRouter } from 'next/navigation'

interface Assessment {
  date_value: string;
  summary: string;
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export default function InsightsPage() {
  const [insight, setInsight] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const router = useRouter()

  const fetchInsight = async () => {
    setLoading(true)
    setError(null)
    try {
      const currentDate = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
      const response = await apiCall(`/api/daily-activity/generate-assessment?target_date=${currentDate}`, { method: 'POST' });
      setInsight(response.summary)
    } catch (err) {
      console.error('Failed to fetch insight:', err)
      setError('Failed to load insights. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const endDate = new Date().toISOString().slice(0, 10);
        const startDate = new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().slice(0, 10); // Last month
        const data = await apiCall(`/api/daily-activity/assessments?start_date=${startDate}&end_date=${endDate}`);
        setAssessments(data.results);
      } catch (err) {
        console.error('Failed to fetch assessments:', err);
      }
    };
    fetchAssessments();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl">
        <div className="mb-8">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Insights</h1>
          <p className="text-gray-600">AI-powered insights based on your health profile</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Your Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center mb-6">
              <Button onClick={fetchInsight} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Generate Insights
                  </>
                )}
              </Button>
            </div>

            {error && (
              <div className="text-center text-red-500 py-4">
                <p>{error}</p>
              </div>
            )}

            {insight ? (
              <div className="prose max-w-none">
                <ReactMarkdown>{insight}</ReactMarkdown>
              </div>
            ) : (
              !loading && !error && (
                <p className="text-gray-500 text-center py-8">Click "Generate Insights" to get your AI-powered health summary.</p>
              )
            )}
          </CardContent>
        </Card>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Previous Activity Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            {assessments.length > 0 ? (
              <div className="space-y-4">
                {assessments.slice(0, 3).map((assessment) => (
                  <div key={assessment.id} className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">{assessment.date_value}</h3>
                    <div className="prose max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{assessment.summary}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No previous activity insights found.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}