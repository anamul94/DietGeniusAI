'use client'

import { useState } from 'react'

interface QuestionCheckboxProps {
  question: string
  options: string[]
  onAnswerChange: (answer: string) => void
  placeholder?: string
}

export default function QuestionCheckbox({ question, options, onAnswerChange, placeholder }: QuestionCheckboxProps) {
  const [selectedValues, setSelectedValues] = useState<string[]>([])

  const handleChange = (option: string, checked: boolean) => {
    let newSelectedValues: string[]
    if (checked) {
      newSelectedValues = [...selectedValues, option]
    } else {
      newSelectedValues = selectedValues.filter(value => value !== option)
    }
    setSelectedValues(newSelectedValues)
    onAnswerChange(newSelectedValues.join(', '))
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
              type="checkbox"
              checked={selectedValues.includes(option)}
              onChange={(e) => handleChange(option, e.target.checked)}
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <span className="text-gray-700">{option}</span>
          </label>
        ))}
      </div>
    </div>
  )
}