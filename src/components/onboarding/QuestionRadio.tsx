'use client'

import { useState } from 'react'

interface QuestionRadioProps {
  question: string
  options: string[]
  onAnswerChange: (answer: string) => void
  placeholder?: string
}

export default function QuestionRadio({ question, options, onAnswerChange, placeholder }: QuestionRadioProps) {
  const [selectedValue, setSelectedValue] = useState('')

  const handleChange = (value: string) => {
    setSelectedValue(value)
    onAnswerChange(value)
  }

  return (
    <div className="space-y-4">
      <div className="prose max-w-none">
        <p className="text-lg font-medium">{question}</p>
        {placeholder && <p className="text-sm text-gray-600">{placeholder}</p>}
      </div>
      
      <div className="space-y-3">
        {options.map((option, index) => (
          <label key={index} className="flex items-center space-x-3 cursor-pointer">
            <input
              type="radio"
              name="question-radio"
              value={option}
              checked={selectedValue === option}
              onChange={(e) => handleChange(e.target.value)}
              className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
            />
            <span className="text-gray-700">{option}</span>
          </label>
        ))}
      </div>
    </div>
  )
}