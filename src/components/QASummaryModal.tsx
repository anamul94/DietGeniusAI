'use client'

import { useState, useEffect } from 'react'
import { X, FileText, Calendar } from 'lucide-react'
import { apiCall } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'

interface QASummary {
  summary: string
  date: string
}

interface QASummaryModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function QASummaryModal({ isOpen, onClose }: QASummaryModalProps) {
  const [summary, setSummary] = useState<QASummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchQASummary()
    }
  }, [isOpen])

  const fetchQASummary = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await apiCall('/api/qa-summaries/latest')
      setSummary(data)
    } catch (err) {
      console.error('Failed to fetch QA summary:', err)
      setError('Failed to load QA summary. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">QA Session Summary</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchQASummary}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          )}

          {!loading && !error && !summary && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No QA summary found.</p>
              <p className="text-sm text-gray-500 mt-2">
                Complete your initial assessment to generate a summary.
              </p>
            </div>
          )}

          {!loading && !error && summary && (
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                <Calendar className="w-4 h-4" />
                <span>Generated on: {new Date(summary.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}</span>
              </div>
              
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{summary.summary}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t bg-gray-50">
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}