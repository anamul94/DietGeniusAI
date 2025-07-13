'use client'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Activity } from 'lucide-react'

export default function InsightsPage() {
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
            <p className="text-gray-500 text-center py-8">Complete your onboarding to see insights</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}