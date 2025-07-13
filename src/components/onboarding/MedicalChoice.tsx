'use client'

import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { FileText, ArrowRight } from 'lucide-react'

interface MedicalChoiceProps {
  onUpload: () => void
  onSkip: () => void
}

export default function MedicalChoice({ onUpload, onSkip }: MedicalChoiceProps) {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Reports</h1>
          <p className="text-gray-600">Would you like to upload your medical reports for better recommendations?</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-500" />
              Upload Medical Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">Why upload medical reports?</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• Get personalized nutrition recommendations</li>
                  <li>• AI analysis of your health conditions</li>
                  <li>• Better dietary suggestions based on medical history</li>
                </ul>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button onClick={onUpload} className="flex-1">
                  <FileText className="w-4 h-4" />
                  Upload Reports
                </Button>
                <Button variant="outline" onClick={onSkip} className="flex-1">
                  <ArrowRight className="w-4 h-4" />
                  Skip for Now
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}