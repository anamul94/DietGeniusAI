'use client'

import { useState, useRef } from 'react'
import { Mic, StopCircle, Play, Pause } from 'lucide-react'

interface QuestionTextInputProps {
  question: string
  onAnswerChange: (answer: string) => void
  placeholder?: string
}

export default function QuestionTextInput({ question, onAnswerChange, placeholder }: QuestionTextInputProps) {
  const [textValue, setTextValue] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleTextChange = (value: string) => {
    setTextValue(value)
    onAnswerChange(value)
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
      handleTextChange(data.transcription)
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

  return (
    <div className="space-y-4">
      <div className="prose max-w-none">
        <p className="text-lg font-medium">{question}</p>
        {placeholder && <p className="text-sm text-gray-600">{placeholder}</p>}
      </div>
      
      <div className="space-y-4">
        <textarea
          value={textValue}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder={placeholder || "Type your answer..."}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none resize-none"
          rows={4}
        />
        
        <div className="flex gap-2">
          {!isRecording && !audioUrl && (
            <button
              type="button"
              onClick={startRecording}
              disabled={loading}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Mic className="w-4 h-4" />
            </button>
          )}
          
          {isRecording && (
            <button
              type="button"
              onClick={stopRecording}
              disabled={loading}
              className="px-3 py-2 bg-red-100 hover:bg-red-200 rounded-lg transition-colors"
            >
              <StopCircle className="w-4 h-4 text-red-600" />
            </button>
          )}
          
          {audioUrl && !isRecording && (
            <>
              <button
                type="button"
                onClick={isPlaying ? pauseAudio : playAudio}
                disabled={loading}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              
              <button
                type="button"
                onClick={transcribeAudio}
                disabled={loading}
                className="px-3 py-2 bg-green-100 hover:bg-green-200 rounded-lg transition-colors text-sm"
              >
                Transcribe
              </button>
              
              <button
                type="button"
                onClick={clearAudio}
                disabled={loading}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm"
              >
                Clear
              </button>
              
              <audio ref={audioRef} src={audioUrl} hidden />
            </>
          )}
        </div>
      </div>
    </div>
  )
}