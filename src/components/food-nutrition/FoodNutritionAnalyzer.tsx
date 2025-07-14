'use client'

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Upload, X, FileText, AlertCircle } from 'lucide-react'

interface FoodNutritionAnalyzerProps {
  sessionId: string
}

export default function FoodNutritionAnalyzer({ sessionId }: FoodNutritionAnalyzerProps) {
  const [files, setFiles] = useState<File[]>([])
  const [servingSize, setServingSize] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [nutritionResult, setNutritionResult] = useState<any>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  const maxFiles = 3

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
      // Prepare form data for food nutrition API
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })
      formData.append('serving_size', servingSize)
      formData.append('session_id', sessionId)

      // Call food nutrition API
      const nutritionResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/medical-reports/food-nutrition`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      })

      if (!nutritionResponse.ok) {
        throw new Error(`Food nutrition analysis failed: ${nutritionResponse.statusText}`)
      }

      const nutritionData = await nutritionResponse.json()
      console.log('Food Nutrition Data:', nutritionData)
      setNutritionResult(nutritionData)
      setFiles([]) // Clear files after successful upload
      setServingSize('') // Clear serving size after successful upload

    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const renderNutritionResult = () => {
    if (!nutritionResult) return null

    return (
      <div className="mt-6 space-y-4">
        <h3 className="text-xl font-bold text-gray-900">Nutrition Analysis Results:</h3>
        {nutritionResult.foods && nutritionResult.foods.length > 0 ? (
          nutritionResult.foods.map((food: any, index: number) => (
            <Card key={index} className="p-4 border border-gray-200 rounded-lg shadow-sm">
              <h4 className="font-bold text-xl text-gray-900 mb-2">{food.food_name}</h4>
              <p className="text-sm text-gray-600 mb-4">Serving Size: {food.serving_size}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-2 text-sm">
                {Object.entries(food.nutrition).map(([key, value]: [string, any]) => (
                  value && value.value !== undefined && value.value !== null && (
                    <div key={key} className="flex justify-between items-center border-b border-gray-100 pb-1">
                      <span className="text-gray-700 capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className="font-medium text-gray-800">{value.value.toFixed(2)} {value.unit}</span>
                    </div>
                  )
                ))}
              </div>
            </Card>
          ))
        ) : (
          <p className="text-gray-600">No food items detected or nutrition data available.</p>
        )}
      </div>
    )
  }

  const getFileIcon = (type: string) => {
    if (type.includes('image')) return '🖼️'
    return '📝' // Fallback, though only images are allowed
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Images for Food Nutrition Analysis</h1>
          <p className="text-gray-600">Upload images of your food for detailed nutritional insights.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-500" />
              Food Images
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900">Privacy & Security</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Your food images are securely processed for nutritional analysis.
                    </p>
                  </div>
                </div>
              </div>

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
                  Support: JPG, PNG, WEBP (Max 3 files, 10MB each)
                </p>
                <div className="w-full mb-4">
                  <label htmlFor="serving-size" className="block text-sm font-medium text-gray-700 text-left mb-1">
                    Serving Size (e.g., "1 bowl", "200g", "2 chicken wings")
                  </label>
                  <input
                    type="text"
                    id="serving-size"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="e.g., 1 bowl"
                    value={servingSize}
                    onChange={(e) => setServingSize(e.target.value)}
                  />
                </div>
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
                  accept=".jpg,.jpeg,.png,.webp"
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

              <div className="flex justify-between pt-6">
                <Button
                  onClick={handleUpload}
                  loading={uploading}
                  disabled={files.length === 0 || !servingSize}
                >
                  Analyze Food
                </Button>
              </div>
              {renderNutritionResult()}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}