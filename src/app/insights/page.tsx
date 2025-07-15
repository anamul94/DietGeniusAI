'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { apiCall } from '@/lib/utils'
import { Activity, Brain, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function InsightsPage() {
  const [insight, setInsight] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchInsight = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiCall('/api/medical-reports/memory-test?message=generate summary', { method: 'POST' })
      setInsight(response.response)
    } catch (err) {
      console.error('Failed to fetch insight:', err)
      setError('Failed to load insights. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Insights</h1>
          <p className="text-gray-600">AI-powered insights based on your health profile</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-orange-500" />
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
      </div>
    </div>
  )
}