'use client'

import { useState, useRef, useEffect } from 'react'
import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
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
  const [mealType, setMealType] = useState<string>('')
  const [consumedAt, setConsumedAt] = useState<Date>(new Date())
  const [consumedAtTime, setConsumedAtTime] = useState<string>(format(new Date(), 'HH:mm'))
  const [mealTypes, setMealTypes] = useState<{ value: string; label: string }[]>([])
  const [loadingMealTypes, setLoadingMealTypes] = useState(true)

  useEffect(() => {
    const fetchMealTypes = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meal-entries/meal-types`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        if (!response.ok) {
          throw new Error('Failed to fetch meal types')
        }
        const data = await response.json()
        setMealTypes(data.meal_types)
      } catch (error) {
        console.error('Error fetching meal types:', error)
      } finally {
        setLoadingMealTypes(false)
      }
    }
    fetchMealTypes()
  }, [])

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
      formData.append('meal_type', mealType)
      if (consumedAt && consumedAtTime) {
        const [hours, minutes] = consumedAtTime.split(':').map(Number)
        const combinedDateTime = new Date(consumedAt)
        combinedDateTime.setHours(hours, minutes, 0, 0)
        formData.append('consumed_at', combinedDateTime.toISOString())
      }

      // Call food nutrition API
      const nutritionResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meal-entries/food-nutrition`, {
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
      setNutritionResult(nutritionData.data[0]) // Access the single food object from the array
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
        {nutritionResult ? (
            <Card className="p-4 border border-gray-200 rounded-lg shadow-sm">
              <h4 className="font-bold text-xl text-gray-900 mb-2">{nutritionResult.food_name}</h4>
              <p className="text-sm text-gray-600 mb-4">Serving Size: {nutritionResult.serving_size}</p>

              <div className="space-y-4">
                {/* Key Nutrients */}
                <div>
                  <h5 className="font-semibold text-md text-gray-800 mb-2">Key Nutrients:</h5>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    {Object.entries(nutritionResult.nutrition).filter(([key]) => ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium', 'cholesterol'].includes(key)).map(([key, value]: [string, any]) => (
                      value && value.value !== undefined && value.value !== null && (
                        <div key={key} className="flex justify-between items-center border-b border-gray-100 pb-1">
                          <span className="text-gray-700 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-medium text-gray-800">{value.value.toFixed(2)} {value.unit}</span>
                        </div>
                      )
                    ))}
                  </div>
                </div>

                {/* Fat Breakdown */}
                <div>
                  <h5 className="font-semibold text-md text-gray-800 mb-2">Fat Breakdown:</h5>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    {Object.entries(nutritionResult.nutrition).filter(([key]) => ['saturated_fat', 'monounsaturated_fat', 'polyunsaturated_fat', 'omega_3', 'omega_6'].includes(key)).map(([key, value]: [string, any]) => (
                      value && value.value !== undefined && value.value !== null && (
                        <div key={key} className="flex justify-between items-center border-b border-gray-100 pb-1">
                          <span className="text-gray-700 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-medium text-gray-800">{value.value.toFixed(2)} {value.unit}</span>
                        </div>
                      )
                    ))}
                  </div>
                </div>

                {/* Other Nutrients (Collapsible) */}
                <details className="group">
                  <summary className="flex justify-between items-center cursor-pointer text-sm font-medium text-green-600 hover:text-green-700">
                    <span>Show All Nutrients</span>
                    <svg className="w-4 h-4 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                  </summary>
                  <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-2 text-sm">
                    {Object.entries(nutritionResult.nutrition).filter(([key]) => 
                      !['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium', 'cholesterol', 'saturated_fat', 'monounsaturated_fat', 'polyunsaturated_fat', 'omega_3', 'omega_6'].includes(key)
                    ).map(([key, value]: [string, any]) => (
                      value && value.value !== undefined && value.value !== null && (
                        <div key={key} className="flex justify-between items-center border-b border-gray-100 pb-1">
                          <span className="text-gray-700 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-medium text-gray-800">{value.value.toFixed(2)} {value.unit}</span>
                        </div>
                      )
                    ))}
                  </div>
                </details>
              </div>
            </Card>
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
                <div className="w-full mb-4">
                  <label htmlFor="meal-type" className="block text-sm font-medium text-gray-700 text-left mb-1">
                    Meal Type
                  </label>
                  <Select onValueChange={setMealType} value={mealType}>
                    <SelectTrigger className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm">
                      <SelectValue placeholder="Select a meal type" />
                    </SelectTrigger>
                    <SelectContent>
                      {loadingMealTypes ? (
                        <SelectItem value="loading" disabled>Loading...</SelectItem>
                      ) : (
                        mealTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>
                <div className="w-full mb-4">
                  <label htmlFor="consumed-at" className="block text-sm font-medium text-gray-700 text-left mb-1">
                    Consumed Date
                  </label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant={"outline"}
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !consumedAt && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {consumedAt ? format(consumedAt, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={consumedAt}
                        onSelect={setConsumedAt}
                        initialFocus
                        required
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                <div className="w-full mb-4">
                  <label htmlFor="consumed-at-time" className="block text-sm font-medium text-gray-700 text-left mb-1">
                    Consumed Time
                  </label>
                  <input
                    type="time"
                    id="consumed-at-time"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    value={consumedAtTime}
                    onChange={(e) => setConsumedAtTime(e.target.value)}
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
                  disabled={uploading || files.length === 0 || !servingSize || !mealType || !consumedAt || !consumedAtTime}
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