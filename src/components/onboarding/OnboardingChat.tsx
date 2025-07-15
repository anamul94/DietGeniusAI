'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/Card'
import { apiCall } from '@/lib/utils'
import { Send, Bot, User, Mic, StopCircle, Play, Pause } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatMessage {
  question: string
  answer: string
}

interface OnboardingChatProps {
  onComplete: () => void
}

export default function OnboardingChat({ onComplete }: OnboardingChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [userAnswer, setUserAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [count, setCount] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [showInitialLoadingMessage, setShowInitialLoadingMessage] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const initialized = useRef(false)

  // Voice recording states
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentQuestion])

  useEffect(() => {
    // Initialize first question
    if (!initialized.current) {
      initialized.current = true
      initializeChat()
    }
  }, [])

  const initializeChat = async () => {
    setLoading(true)
    setShowInitialLoadingMessage(true)
    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({
          answer: '',
          count: 0,
          chat_history: []
        })
      })
      
      setCurrentQuestion(response.question)
      setCount(response.count)
    } catch (error) {
      console.error('Failed to initialize chat:', error)
    } finally {
      setLoading(false)
      setShowInitialLoadingMessage(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      setMediaRecorder(recorder)
      setIsRecording(true)
      setAudioBlob(null)
      setAudioUrl(null)

      const audioChunks: Blob[] = []
      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      recorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(track => track.stop())
      }

      recorder.start()
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not start recording. Please ensure microphone access is granted.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
    }
  }

  const playAudio = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play()
      setIsPlaying(true)
      audioRef.current.onended = () => setIsPlaying(false)
    }
  }

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      setIsPlaying(false)
    }
  }

  const transcribeAudio = async () => {
    if (!audioBlob) return

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')

      const response = await fetch(process.env.NEXT_PUBLIC_TRANSCRIPTION_API_URL as string, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let errorDetail = `Transcription API Error: ${response.status}`
        try {
          const errorData = await response.json()
          errorDetail += ` - ${errorData.detail || JSON.stringify(errorData)}`
        } catch (jsonError) {
          const errorText = await response.text()
          errorDetail += ` - Raw Response: ${errorText}`
        }
        console.error('Transcription API Error:', errorDetail)
        throw new Error(errorDetail)
      }

      const data = await response.json()
      setUserAnswer(data.transcription)
    } catch (error) {
      console.error('Error transcribing audio:', error)
      alert('Failed to transcribe audio. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const clearAudio = () => {
    setAudioBlob(null)
    setAudioUrl(null)
    setIsPlaying(false)
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userAnswer.trim() || loading) return

    const newMessage: ChatMessage = {
      question: currentQuestion,
      answer: userAnswer
    }

    const updatedHistory = [...messages, newMessage]
    setMessages(updatedHistory)
    setUserAnswer('')
    setLoading(true)
    setAudioBlob(null) // Clear audio after submission
    setAudioUrl(null)

    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({
          answer: userAnswer,
          count: count,
          chat_history: updatedHistory
        })
      })

      if (response.is_done === true) {
        setIsComplete(true)
        setCurrentQuestion(response.question || 'Thank you for completing the onboarding process!')
      } else {
        setCurrentQuestion(response.question)
        setCount(response.count)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDone = () => {
    onComplete()
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Assessment</h1>
          <p className="text-gray-600">Let's understand your health profile better</p>
          <div className="flex justify-center mt-4">
            <div className="flex space-x-2">
              {[1, 2, 3, 4].map((step) => (
                <div
                  key={step}
                  className={`w-3 h-3 rounded-full ${
                    step <= count ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        <Card className="h-[600px] flex flex-col">
          <CardContent className="flex-1 flex flex-col p-0">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              

              {showInitialLoadingMessage && loading && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
                    <p className="text-lg font-semibold text-gray-700">
                      Please wait while an AI Dietitian is assigned to you.
                    </p>
                    <p className="text-gray-500">
                      They are currently analyzing your data to provide personalized insights.
                    </p>
                  </div>
                </div>
              )}

              {currentQuestion && !isComplete && !showInitialLoadingMessage && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1 bg-green-50 rounded-lg p-4 prose max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{currentQuestion}</ReactMarkdown>
                  </div>
                </div>
              )}

              {isComplete && (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Assessment Complete!</h3>
                  <p className="text-gray-600 mb-6">{currentQuestion}</p>
                  <Button onClick={handleDone} size="lg">
                    Get Started
                  </Button>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {!isComplete && (
              <div className="border-t border-gray-200 p-6">
                <form onSubmit={handleSubmit} className="flex gap-4">
                  <input
                    type="text"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your answer..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                    disabled={loading}
                  />
                  {!isRecording && !audioUrl && (
                    <Button type="button" onClick={startRecording} disabled={loading}>
                      <Mic className="w-4 h-4" />
                    </Button>
                  )}
                  {isRecording && (
                    <Button type="button" onClick={stopRecording} disabled={loading}>
                      <StopCircle className="w-4 h-4" />
                    </Button>
                  )}
                  {audioUrl && !isRecording && (
                    <>
                      <Button type="button" onClick={isPlaying ? pauseAudio : playAudio} disabled={loading}>
                        {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </Button>
                      <Button type="button" onClick={transcribeAudio} disabled={loading}>
                        Transcribe
                      </Button>
                      <Button type="button" onClick={clearAudio} disabled={loading}>
                        Clear
                      </Button>
                      <audio ref={audioRef} src={audioUrl} hidden />
                    </>
                  )}
                  <Button
                    type="submit"
                    disabled={!userAnswer.trim() || loading}
                    loading={loading}
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}