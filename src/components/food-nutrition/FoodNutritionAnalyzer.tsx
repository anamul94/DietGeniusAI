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
  const [filePreviews, setFilePreviews] = useState<string[]>([])
  const [servingSize, setServingSize] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [nutritionResult, setNutritionResult] = useState<any>(null)
  const [resultImages, setResultImages] = useState<string[]>([])
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [mealType, setMealType] = useState<string>('')
  const [consumedAt, setConsumedAt] = useState<Date>(new Date())
  const [consumedAtTime, setConsumedAtTime] = useState<string>(format(new Date(), 'HH:mm'))
  const [mealTypes, setMealTypes] = useState<{ value: string; label: string }[]>([])
  const [loadingMealTypes, setLoadingMealTypes] = useState(true)
  const [expandedImage, setExpandedImage] = useState<string | null>(null)

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

    // Create preview URLs for new files
    validFiles.forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        setFilePreviews(prev => [...prev, e.target?.result as string].slice(0, maxFiles))
      }
      reader.readAsDataURL(file)
    })
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    setFilePreviews(prev => prev.filter((_, i) => i !== index))
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
      setNutritionResult(nutritionData.data) // Store the entire data array
      setResultImages([...filePreviews]) // Store images for results display
      setFiles([]) // Clear files after successful upload
      setFilePreviews([]) // Clear file previews after successful upload
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

    // Handle both single food and multiple foods
    const foods = Array.isArray(nutritionResult) ? nutritionResult : [nutritionResult]

    const formatNutrientName = (key: string) => {
      const nameMap: { [key: string]: string } = {
        'calories': 'Calories',
        'protein': 'Protein',
        'carbs': 'Carbohydrates',
        'fat': 'Total Fat',
        'fiber': 'Dietary Fiber',
        'sugar': 'Total Sugars',
        'cholesterol': 'Cholesterol',
        'sodium': 'Sodium',
        'potassium': 'Potassium',
        'vitamin_a': 'Vitamin A',
        'vitamin_c': 'Vitamin C',
        'vitamin_d': 'Vitamin D',
        'vitamin_e': 'Vitamin E',
        'vitamin_k': 'Vitamin K',
        'thiamin': 'Thiamin (B1)',
        'riboflavin': 'Riboflavin (B2)',
        'niacin': 'Niacin (B3)',
        'vitamin_b6': 'Vitamin B6',
        'folate': 'Folate',
        'vitamin_b12': 'Vitamin B12',
        'calcium': 'Calcium',
        'iron': 'Iron',
        'magnesium': 'Magnesium',
        'phosphorus': 'Phosphorus',
        'zinc': 'Zinc',
        'selenium': 'Selenium',
        'copper': 'Copper',
        'manganese': 'Manganese',
        'saturated_fat': 'Saturated Fat',
        'monounsaturated_fat': 'Monounsaturated Fat',
        'polyunsaturated_fat': 'Polyunsaturated Fat',
        'omega_3': 'Omega-3',
        'omega_6': 'Omega-6'
      }
      return nameMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatValue = (value: any) => {
      if (typeof value === 'number') return value.toFixed(1)
      if (value && value.value !== undefined) {
        const num = parseFloat(value.value)
        return isNaN(num) ? '0' : num.toFixed(1)
      }
      return '0'
    }

    const getUnit = (value: any) => {
      if (value && value.unit && value.unit !== '') return value.unit
      return 'g'
    }

    // Calculate totals
    const totals: { [key: string]: number } = {}
    foods.forEach(food => {
      const nutrients = food.nutrition || {}
      Object.entries(nutrients).forEach(([key, value]) => {
        let val = 0
        if (typeof value === 'number') {
          val = value
        } else if (value && typeof value === 'object' && value !== null && 'value' in value) {
          const valueStr = (value as any).value
          val = parseFloat(String(valueStr))
        }
        if (!isNaN(val)) {
          totals[key] = (totals[key] || 0) + val
        }
      })
    })

    const renderFoodNutrition = (food: any, index: number) => {
      const allNutrients = food.nutrition || {}
      const nonZeroNutrients = Object.entries(allNutrients).filter(([_, value]) => {
        if (typeof value === 'number') return value > 0
        if (value && typeof value === 'object' && 'value' in value) {
          const val = (value as any).value
          return parseFloat(val) > 0
        }
        return false
      })

      // Group nutrients for this food
      const macroNutrients = nonZeroNutrients.filter(([key]) =>
        ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar'].includes(key)
      )
      const vitamins = nonZeroNutrients.filter(([key]) =>
        key.includes('vitamin') || ['thiamin', 'riboflavin', 'niacin', 'folate', 'vitamin_b12', 'vitamin_b6'].includes(key)
      )
      const minerals = nonZeroNutrients.filter(([key]) =>
        ['calcium', 'iron', 'magnesium', 'phosphorus', 'potassium', 'zinc', 'selenium', 'copper', 'manganese', 'sodium'].includes(key)
      )
      const fats = nonZeroNutrients.filter(([key]) =>
        key.includes('fat') || key.includes('omega')
      )

      return (
        <div key={index} className="bg-white rounded-3xl shadow-2xl overflow-hidden border-2 border-emerald-100 hover:border-emerald-200 transition-all duration-300">
          <div className="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 px-8 py-6 relative">
            <div className="absolute top-4 right-4 text-4xl opacity-20">🍽️</div>
            <h3 className="text-3xl font-bold text-white capitalize">{food.food_name || 'Unknown Food'}</h3>
            <p className="text-lg text-white/90 mt-2 flex items-center">
              <span className="text-xl mr-2">📏</span>
              Serving Size: {food.serving_size || '1 serving'}
            </p>
          </div>

          {/* Food Image Display */}
          {resultImages[index] && (
            <div className="px-8 pt-6">
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-4 border-2 border-gray-200">
                <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-xl mr-2">📸</span>
                  Food Image
                </h4>
                <img
                  src={resultImages[index]}
                  alt={food.food_name || 'Food image'}
                  className="w-full max-w-md mx-auto h-64 object-cover rounded-xl shadow-lg cursor-pointer hover:shadow-xl transition-shadow"
                  onClick={() => setExpandedImage(resultImages[index])}
                />
              </div>
            </div>
          )}

          <div className="p-8">
            {/* Key Macronutrients - Highlighted */}
            {macroNutrients.length > 0 && (
              <div className="mb-8">
                <h4 className="text-2xl font-bold text-slate-800 mb-4 flex items-center">
                  <span className="text-2xl mr-3">⚡</span>
                  Key Nutrition Facts
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  {macroNutrients.slice(0, 4).map(([key, value]) => (
                    <div key={key} className="bg-gradient-to-br from-emerald-50 to-green-50 p-4 rounded-2xl border-2 border-emerald-100 text-center">
                      <div className="text-2xl font-bold text-emerald-700 mb-1">
                        {formatValue(value)}
                      </div>
                      <div className="text-xs text-emerald-600 font-medium mb-1">
                        {key === 'calories' ? 'kcal' : getUnit(value)}
                      </div>
                      <div className="text-sm text-slate-700 font-semibold">
                        {formatNutrientName(key)}
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Detailed Macronutrients Table */}
                {macroNutrients.length > 4 && (
                  <div className="bg-slate-50 rounded-2xl p-6">
                    <h5 className="text-lg font-semibold text-slate-800 mb-3">Additional Macronutrients</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {macroNutrients.slice(4).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center py-2 px-3 bg-white rounded-lg">
                          <span className="text-slate-700 font-medium">{formatNutrientName(key)}</span>
                          <span className="text-slate-900 font-bold">
                            {formatValue(value)} {getUnit(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Vitamins */}
            {vitamins.length > 0 && (
              <div className="mb-8">
                <h4 className="text-xl font-bold text-slate-800 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🌟</span>
                  Vitamins & B-Complex
                </h4>
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-100">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {vitamins.map(([key, value]) => (
                      <div key={key} className="bg-white p-4 rounded-xl shadow-sm border border-purple-100">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-700 font-medium text-sm">{formatNutrientName(key)}</span>
                          <span className="text-purple-700 font-bold">
                            {formatValue(value)} {getUnit(value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Minerals */}
            {minerals.length > 0 && (
              <div className="mb-8">
                <h4 className="text-xl font-bold text-slate-800 mb-4 flex items-center">
                  <span className="text-2xl mr-3">⛰️</span>
                  Essential Minerals
                </h4>
                <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 border-2 border-blue-100">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {minerals.map(([key, value]) => (
                      <div key={key} className="bg-white p-4 rounded-xl shadow-sm border border-blue-100">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-700 font-medium text-sm">{formatNutrientName(key)}</span>
                          <span className="text-blue-700 font-bold">
                            {formatValue(value)} {getUnit(value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Fats */}
            {fats.length > 0 && (
              <div className="mb-6">
                <h4 className="text-xl font-bold text-slate-800 mb-4 flex items-center">
                  <span className="text-2xl mr-3">🥑</span>
                  Fat Composition
                </h4>
                <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-6 border-2 border-orange-100">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {fats.map(([key, value]) => (
                      <div key={key} className="bg-white p-4 rounded-xl shadow-sm border border-orange-100">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-700 font-medium">{formatNutrientName(key)}</span>
                          <span className="text-orange-700 font-bold">
                            {formatValue(value)} {getUnit(value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )
    }

    return (
      <div className="mt-12 w-full mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-slate-900 mb-2">🍽️ Nutrition Analysis Results</h2>
          <p className="text-xl text-slate-600">Detailed breakdown of your food items</p>
          <Button
            onClick={() => {
              setNutritionResult(null)
              setResultImages([])
            }}
            variant="outline"
            className="mt-4"
          >
            Clear Results & Start New Analysis
          </Button>
        </div>

        {/* Uploaded Images Gallery */}
        {resultImages.length > 0 && (
          <div className="mb-12">
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-8 border-2 border-purple-200">
              <h3 className="text-2xl font-bold text-purple-900 mb-6 flex items-center">
                <span className="text-3xl mr-3">📸</span>
                Uploaded Food Images ({resultImages.length})
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {resultImages.map((image, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={image}
                      alt={`Food image ${index + 1}`}
                      className="w-full h-48 object-cover rounded-2xl shadow-lg cursor-pointer hover:shadow-xl transition-all duration-300"
                      onClick={() => setExpandedImage(image)}
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 rounded-2xl flex items-center justify-center">
                      <span className="text-white font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        Click to expand
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Individual Food Items */}
        <div className="space-y-8 mb-12">
          {foods.map((food, index) => renderFoodNutrition(food, index))}
        </div>

        {/* Totals Section - Only show if multiple foods */}
        {foods.length > 1 && (
          <div className="bg-gradient-to-br from-emerald-800 via-green-700 to-teal-800 text-white rounded-3xl shadow-2xl overflow-hidden border-4 border-emerald-200">
            <div className="bg-gradient-to-r from-emerald-600 to-green-600 px-8 py-6">
              <h3 className="text-3xl font-bold text-white flex items-center">
                <span className="text-4xl mr-3">🧮</span>
                Total Nutrition Summary
              </h3>
              <p className="text-lg text-white/90 mt-1">Combined nutritional values for all {foods.length} food items</p>
            </div>

            <div className="p-8">
              {/* Key Macronutrients Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                {['calories', 'protein', 'carbs', 'fat'].map(key => (
                  totals[key] > 0 && (
                    <div key={key} className="bg-white/15 backdrop-blur-sm p-6 rounded-2xl text-center border border-white/20">
                      <div className="text-3xl font-bold text-white mb-2">{totals[key].toFixed(1)}</div>
                      <div className="text-sm text-white/90 font-medium">{formatNutrientName(key)}</div>
                      <div className="text-xs text-white/70">
                        {key === 'calories' ? 'kcal' : 'g'}
                      </div>
                    </div>
                  )
                ))}
              </div>

              {/* All Other Nutrients */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(totals)
                  .filter(([key, value]) => value > 0 && !['calories', 'protein', 'carbs', 'fat'].includes(key))
                  .map(([key, value]) => (
                    <div key={key} className="bg-white/10 backdrop-blur-sm p-4 rounded-xl border border-white/10">
                      <div className="flex justify-between items-center">
                        <span className="text-white/90 text-sm font-medium">{formatNutrientName(key)}</span>
                        <span className="text-white font-bold">{value.toFixed(1)}g</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  const getFileIcon = (type: string) => {
    if (type.includes('image')) return '🖼️'
    return '📝' // Fallback, though only images are allowed
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 py-12">
      <div className="w-4/5 mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 mb-4 tracking-tight">
            Food Nutrition Analysis
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Get detailed nutritional insights from your food images with AI-powered analysis
          </p>
        </div>

        <Card className="shadow-2xl rounded-3xl border-0 overflow-hidden mx-auto">
          <CardHeader className="bg-gradient-to-r from-emerald-600 to-green-600 text-white px-8 py-6">
            <CardTitle className="flex items-center gap-4 text-3xl font-bold">
              <div className="p-3 bg-white/20 rounded-2xl">
                <FileText className="w-8 h-8" />
              </div>
              <div>
                <div className="text-3xl font-bold">Upload Food Images</div>
                <div className="text-lg opacity-90 mt-1">AI-powered nutritional analysis</div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="space-y-8">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <AlertCircle className="w-6 h-6 text-blue-500 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg text-blue-900">Privacy & Security</h4>
                    <p className="text-base text-blue-700 mt-2">
                      Your food images are securely processed for nutritional analysis using AI technology.
                    </p>
                  </div>
                </div>
              </div>

              <div
                className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 ${
                  dragActive ? 'border-green-500 bg-green-50 scale-105' : 'border-gray-300 hover:border-green-400 hover:bg-gray-50'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="w-16 h-16 text-gray-400 mx-auto mb-6" />
                <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                  Drop your food images here
                </h3>
                <p className="text-lg text-gray-600 mb-6">
                  or click to browse • JPG, PNG, WEBP (Max 3 files, 10MB each)
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
                  <div>
                    <label htmlFor="serving-size" className="block text-base font-medium text-gray-700 text-left mb-2">
                      Serving Size
                    </label>
                    <input
                      type="text"
                      id="serving-size"
                      className="block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-base"
                      placeholder="e.g., 1 bowl, 200g, 2 chicken wings"
                      value={servingSize}
                      onChange={(e) => setServingSize(e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="meal-type" className="block text-base font-medium text-gray-700 text-left mb-2">
                      Meal Type
                    </label>
                    <Select onValueChange={setMealType} value={mealType}>
                      <SelectTrigger className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-base">
                        <SelectValue placeholder="Select meal type" />
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
                  
                  <div>
                    <label htmlFor="consumed-at" className="block text-base font-medium text-gray-700 text-left mb-2">
                      Consumed Date
                    </label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant={"outline"}
                          className={cn(
                            "w-full justify-start text-left font-normal px-4 py-3 text-base",
                            !consumedAt && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-5 w-5" />
                          {consumedAt ? format(consumedAt, "PPP") : <span>Select date</span>}
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
                  
                  <div>
                    <label htmlFor="consumed-at-time" className="block text-base font-medium text-gray-700 text-left mb-2">
                      Consumed Time
                    </label>
                    <input
                      type="time"
                      id="consumed-at-time"
                      className="block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-base"
                      value={consumedAtTime}
                      onChange={(e) => setConsumedAtTime(e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="mt-8">
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={files.length >= maxFiles}
                    className="text-lg px-6 py-3"
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
              </div>

              {files.length > 0 && (
                <div className="space-y-6">
                  <h4 className="font-semibold text-xl text-gray-900">Selected Images ({files.length}/{maxFiles})</h4>
                  
                  {/* Image Gallery */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filePreviews.map((preview, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={preview}
                          alt={files[index]?.name || `Food image ${index + 1}`}
                          className="w-full h-48 object-cover rounded-xl border-2 border-gray-200 cursor-pointer hover:border-green-400 transition-all duration-200"
                          onClick={() => setExpandedImage(preview)}
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-200 rounded-xl flex items-center justify-center">
                          <span className="text-white font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                            Click to expand
                          </span>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                        <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                          {files[index]?.name}
                        </div>
                      </div>
                    ))}
                  </div>
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

      {/* Expanded Image Modal */}
      {expandedImage && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setExpandedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <img
              src={expandedImage}
              alt="Expanded food image"
              className="max-w-full max-h-full rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={() => setExpandedImage(null)}
              className="absolute -top-4 -right-4 bg-white text-black rounded-full p-2 shadow-lg hover:bg-gray-100"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}