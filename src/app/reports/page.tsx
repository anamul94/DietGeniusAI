'use client'

import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { apiCall, formatDate } from '@/lib/utils'
import { FileText, ChevronLeft, ChevronRight } from 'lucide-react'

interface MedicalReport {
  id: string
  medical_report: any
  uploaded_at: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<MedicalReport[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchReports = async (pageNum: number) => {
    setLoading(true)
    try {
      const data = await apiCall(`/api/medical-reports/medical?page=${pageNum}&limit=10`)
      setReports(data.data)
      setTotalPages(data.pagination.pages)
    } catch (error) {
      console.error('Failed to fetch reports:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReports(page)
  }, [page])

  const renderReportData = (reportData: any) => {
    if (!reportData || !Array.isArray(reportData)) return null
    
    return reportData.map((report, idx) => {
      const [filename, data] = report
      return (
        <div key={idx} className="border rounded-lg p-4 mb-4">
          <h4 className="font-medium text-gray-900 mb-2">{filename}</h4>
          {data['Patient Demographics'] && (
            <div className="mb-3">
              <h5 className="font-medium text-sm text-gray-700">Patient Info:</h5>
              <p className="text-sm">{data['Patient Demographics']['Full Name']}, Age {data['Patient Demographics']['Age']}</p>
            </div>
          )}
          {data['Vital Signs & Lab Results']?.['Lab Results'] && (
            <div>
              <h5 className="font-medium text-sm text-gray-700 mb-2">Lab Results:</h5>
              <div className="space-y-1">
                {data['Vital Signs & Lab Results']['Lab Results'].slice(0, 3).map((test: any, i: number) => (
                  <p key={i} className="text-sm">{test['Test Name']}: {test['Result Value']} ({test['Reference Range']})</p>
                ))}
              </div>
            </div>
          )}
        </div>
      )
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical Reports</h1>
          <p className="text-gray-600">View and manage your uploaded medical reports</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-500" />
              Your Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : reports.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No reports uploaded yet</p>
            ) : (
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="font-medium text-gray-900">Report #{report.id}</h3>
                      <span className="text-sm text-gray-500">{formatDate(report.uploaded_at)}</span>
                    </div>
                    {renderReportData(report.medical_report)}
                  </div>
                ))}
                
                {totalPages > 1 && (
                  <div className="flex justify-center items-center gap-4 mt-6">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-sm text-gray-600">Page {page} of {totalPages}</span>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}