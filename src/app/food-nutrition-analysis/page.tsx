'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import FoodNutritionAnalyzer from '@/components/food-nutrition/FoodNutritionAnalyzer'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { AlertCircle, ArrowLeft } from 'lucide-react'

export default function FoodNutritionAnalysisPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const fetchSessionId = async () => {
      try {
        const sessionResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/medical-reports/generate-session-id/`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        })

        if (!sessionResponse.ok) {
          throw new Error(`Failed to generate session ID: ${sessionResponse.statusText}`)
        }
        const sessionData = await sessionResponse.json()
        setSessionId(sessionData.session_id)
      } catch (err: any) {
        console.error('Error fetching session ID:', err)
        setError(err.message || 'Failed to generate session ID.')
      } finally {
        setLoading(false)
      }
    }

    fetchSessionId()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500">{error}</p>
            <p className="text-gray-600 mt-2">Please try again later or contact support.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-600">
              <AlertCircle className="w-5 h-5" />
              Session Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-yellow-500">Could not obtain a session ID. Please try refreshing the page.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-2xl">
        <div className="mb-8">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Food Nutrition Analysis</h1>
          <p className="text-gray-600">Upload images of your food for detailed nutritional insights.</p>
        </div>
        <FoodNutritionAnalyzer sessionId={sessionId} />
      </div>
    </div>
  )
}
