'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/Card'
import { apiCall } from '@/lib/utils'
import { Send, Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import DynamicQuestion, { type Question } from './DynamicQuestion'

interface ChatMessage {
  question: string
  answer: string
}

interface OnboardingChatProps {
  onComplete: () => void
}

interface NutritionistQAResponse {
  questions: Question[]
  is_complete: boolean
  message_on_completion?: string
  count: number
}

export default function OnboardingChat({ onComplete }: OnboardingChatProps) {
  const router = useRouter()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentQuestions, setCurrentQuestions] = useState<Question[]>([])
  const [currentAnswers, setCurrentAnswers] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [count, setCount] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [showInitialLoadingMessage, setShowInitialLoadingMessage] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [questionKey, setQuestionKey] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const initialized = useRef(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentQuestions])

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
    setError(null)
    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({
          qa: [], // Empty array for initial request
          count: 0
        })
      })
      
      // Parse the response to handle both old and new formats
      let questions: Question[] = []
      if (response.questions && Array.isArray(response.questions)) {
        questions = response.questions
      } else if (response.question) {
        // Handle old format - convert to new format
        questions = [{
          question_text: response.question,
          input_type: 'textinput',
          placeholder: 'Type your answer...'
        }]
      }
      
      setCurrentQuestions(questions)
      setCount(response.count || 0)
      setIsComplete(response.is_complete || false)
    } catch (error) {
      console.error('Failed to initialize chat:', error)
      setError('Failed to initialize chat. Please try again.')
    } finally {
      setLoading(false)
      setShowInitialLoadingMessage(false)
    }
  }

  const handleAnswerChange = (questionText: string, answer: string) => {
    setCurrentAnswers(prev => ({
      ...prev,
      [questionText]: answer
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return

    // Check if all questions have answers
    const unanswered = currentQuestions.filter(q => !currentAnswers[q.question_text]?.trim())
    if (unanswered.length > 0) {
      setError('Please answer all questions before proceeding.')
      return
    }

    // Clear any previous errors
    setError(null)

    // Create QA array for submission
    const qaArray = currentQuestions.map(q => ({
      question: q.question_text,
      answer: currentAnswers[q.question_text] || ''
    }))

    // Create combined answers for display
    const combinedAnswers = qaArray.map(item => `${item.question}: ${item.answer}`).join('\n\n')

    const newMessage: ChatMessage = {
      question: currentQuestions.map(q => q.question_text).join('\n\n'),
      answer: combinedAnswers
    }

    const updatedHistory = [...messages, newMessage]
    setMessages(updatedHistory)
    setCurrentAnswers({})
    setQuestionKey(prev => prev + 1) // Force re-mount to clear inputs
    setLoading(true)

    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({
          qa: qaArray,
          count: count
        })
      })

      console.log('QA Response:', response)

      if (response.is_complete === true) {
        setIsComplete(true)
        setCurrentQuestions([])
        setCurrentAnswers({})
        // Redirect to dashboard when complete
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
      } else {
        // Increment count for next round
        const nextCount = count + 1
        setCount(nextCount)
        
        // Parse the response to handle both old and new formats
        let questions: Question[] = []
        if (response.questions && Array.isArray(response.questions)) {
          questions = response.questions
        } else if (response.question) {
          // Handle old format - convert to new format
          questions = [{
            question_text: response.question,
            input_type: 'textinput',
            placeholder: 'Type your answer...'
          }]
        }
        
        setCurrentQuestions(questions)
      }
    } catch (error: any) {
      console.error('Failed to send message:', error)
      setError(error?.message || 'Failed to send message. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDone = () => {
    router.push('/dashboard')
  }

  const allQuestionsAnswered = () => {
    return currentQuestions.every(q => currentAnswers[q.question_text]?.trim())
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
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                  <div className="flex items-center">
                    <div className="w-5 h-5 text-red-500 mr-2">
                      <svg fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="text-red-700 font-medium">{error}</p>
                  </div>
                </div>
              )}

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

              {currentQuestions.length > 0 && !isComplete && !showInitialLoadingMessage && (
                <div className="space-y-6">
                  {currentQuestions.map((question, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <DynamicQuestion
                          key={`${questionKey}-${index}`}
                          question={question}
                          onAnswerChange={(answer) => handleAnswerChange(question.question_text, answer)}
                        />
                      </div>
                    </div>
                  ))}
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
                  <p className="text-gray-600 mb-6">
                    {currentQuestions.length === 0 && "Thank you for completing the onboarding process!"}
                  </p>
                  <Button onClick={handleDone} size="lg">
                    Get Started
                  </Button>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {currentQuestions.length > 0 && !isComplete && (
              <div className="border-t border-gray-200 p-6">
                <form onSubmit={handleSubmit} className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={!allQuestionsAnswered() || loading}
                    loading={loading}
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Submit Answers
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