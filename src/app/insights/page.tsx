'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { apiCall } from '@/lib/utils'
import { Activity, Brain, Loader2, ArrowLeft, Upload, X, FileText } from 'lucide-react'
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
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [currentProgress, setCurrentProgress] = useState(0)
  const [isStreaming, setIsStreaming] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  const maxFiles = 3
  const router = useRouter()

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      addFiles(selectedFiles)
    }
  }

  const addFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => {
      if (!allowedTypes.includes(file.type)) {
        alert(`${file.name} is not a supported file type`)
        return false
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert(`${file.name} is too large (max 10MB)`)
        return false
      }
      return true
    })

    setFiles(prev => {
      const combined = [...prev, ...validFiles]
      return combined.slice(0, maxFiles)
    })
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/medical-reports/medical`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      })

      setFiles([])
      alert('Reports uploaded successfully!')
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const getFileIcon = (type: string) => {
    if (type.includes('image')) return '🖼️'
    if (type.includes('pdf')) return '📄'
    return '📝'
  }

  const fetchInsight = async () => {
    setLoading(true)
    setError(null)
    setInsight(null)
    setCurrentProgress(0)
    setIsStreaming(true)
    
    try {
      const currentDate = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        setIsStreaming(false);
        return;
      }

      // Generate session ID for SSE
      const sessionId = `insights-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/daily-activity/stream/generate-assessment?target_date=${currentDate}&token=${token}&sse_session_id=${sessionId}`
      );

      let fullResponse = '';

      eventSource.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
          case 'connected':
            console.log('SSE connection established');
            break;
            
          case 'progress':
            setCurrentProgress(message.progress || 0);
            break;
            
          case 'chunk':
            fullResponse += message.data;
            setInsight(fullResponse);
            break;
            
          case 'complete':
            setInsight(message.full_response);
            setCurrentProgress(100);
            eventSource.close();
            setLoading(false);
            setIsStreaming(false);
            break;
            
          case 'error':
            setError(message.message || 'Failed to generate insights');
            eventSource.close();
            setLoading(false);
            setIsStreaming(false);
            break;
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        setError('Connection error. Please try again.');
        setLoading(false);
        setIsStreaming(false);
        eventSource.close();
      };

    } catch (err) {
      console.error('Failed to fetch insight:', err);
      setError('Failed to load insights. Please try again.');
      setLoading(false);
      setIsStreaming(false);
    }
  }

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const endDate = new Date().toISOString().slice(0, 10);
        const startDate = new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().slice(0, 10); // Last month
        const data = await apiCall(`/api/daily-activity/assessments?start_date=${startDate}&end_date=${endDate}`);
        
        // Handle array response directly and filter out invalid entries
        if (Array.isArray(data)) {
          const validAssessments = data.filter(assessment =>
            assessment &&
            typeof assessment.summary === 'string' &&
            assessment.summary.trim() !== '' &&
            assessment.summary !== 'undefined'
          );
          setAssessments(validAssessments);
        } else {
          console.error('Invalid assessment data format:', data);
          setAssessments([]);
        }
      } catch (err) {
        console.error('Failed to fetch assessments:', err);
        setAssessments([]); // Reset to empty array on error
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
              <Button onClick={fetchInsight} disabled={loading || isStreaming}>
                {loading || isStreaming ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {isStreaming ? 'Streaming...' : 'Generating...'}
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Generate Insights
                  </>
                )}
              </Button>
            </div>

            {isStreaming && (
              <div className="space-y-2 mb-4">
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
              <div className="text-center text-red-500 py-4">
                <p>{error}</p>
              </div>
            )}

            {insight ? (
              <div className="prose max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{insight}</ReactMarkdown>
              </div>
            ) : (
              !loading && !error && !isStreaming && (
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
            {assessments?.length > 0 ? (
              <div className="space-y-4">
                {assessments.filter(a => a.summary).slice(0, 3).map((assessment) => (
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

        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Upload Medical Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-green-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Drop your files here or click to browse
                </h3>
                <p className="text-gray-500 mb-4">
                  Support: PDF, DOC, DOCX, TXT, MD, JPG, PNG, WEBP (Max 3 files, 10MB each)
                </p>
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={files.length >= maxFiles}
                >
                  Choose Files
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.md,.jpg,.jpeg,.png,.webp"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>

              {files.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">Selected Files ({files.length}/{maxFiles})</h4>
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{getFileIcon(file.type)}</span>
                        <div>
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end">
                <Button
                  onClick={handleUpload}
                  disabled={files.length === 0 || uploading}
                >
                  {uploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    'Upload Reports'
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}