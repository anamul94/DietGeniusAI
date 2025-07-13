'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { apiCall } from '@/lib/utils'
import { Send, Bot, User } from 'lucide-react'

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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentQuestion])

  useEffect(() => {
    // Initialize first question
    initializeChat()
  }, [])

  const initializeChat = async () => {
    setLoading(true)
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

    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({
          answer: userAnswer,
          count: count,
          chat_history: updatedHistory
        })
      })

      if (response.count >= 4) {
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
              {messages.map((message, index) => (
                <div key={index} className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 bg-green-50 rounded-lg p-4">
                      <p className="text-gray-800">{message.question}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3 justify-end">
                    <div className="flex-1 max-w-md bg-blue-500 text-white rounded-lg p-4">
                      <p>{message.answer}</p>
                    </div>
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  </div>
                </div>
              ))}

              {currentQuestion && !isComplete && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1 bg-green-50 rounded-lg p-4">
                    <p className="text-gray-800">{currentQuestion}</p>
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