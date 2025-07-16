'use client'

import { useState } from 'react'
import QuestionRadio from './QuestionRadio'
import QuestionCheckbox from './QuestionCheckbox'
import QuestionTextInput from './QuestionTextInput'

export type InputType = 'radio' | 'checkbox' | 'textinput'

export interface Question {
  question_text: string
  input_type: InputType
  options?: string[]
  placeholder?: string
  additional_context?: string
}

interface DynamicQuestionProps {
  question: Question
  onAnswerChange: (answer: string) => void
}

export default function DynamicQuestion({ question, onAnswerChange }: DynamicQuestionProps) {
  const [currentAnswer, setCurrentAnswer] = useState('')

  const handleAnswerChange = (answer: string) => {
    setCurrentAnswer(answer)
    onAnswerChange(answer)
  }

  const renderQuestion = () => {
    switch (question.input_type) {
      case 'radio':
        return (
          <QuestionRadio
            question={question.question_text}
            options={question.options || []}
            onAnswerChange={handleAnswerChange}
            placeholder={question.placeholder}
          />
        )
      
      case 'checkbox':
        return (
          <QuestionCheckbox
            question={question.question_text}
            options={question.options || []}
            onAnswerChange={handleAnswerChange}
            placeholder={question.placeholder}
          />
        )
      
      case 'textinput':
        return (
          <QuestionTextInput
            question={question.question_text}
            onAnswerChange={handleAnswerChange}
            placeholder={question.placeholder}
          />
        )
      
      default:
        return (
          <QuestionTextInput
            question={question.question_text}
            onAnswerChange={handleAnswerChange}
            placeholder={question.placeholder}
          />
        )
    }
  }

  return (
    <div className="w-full">
      {renderQuestion()}
    </div>
  )
}