'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { apiCall } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'
import { useRouter } from 'next/navigation'

interface ProfileData {
  gender: string
  dob: string
  phone: string
  address: string
  city: string
  country: string
  postal_code: string
  profession: string
  height: string
  weight: string
  dietary_preference: string[]
  purpose_of_joining: string[]
  bmi?: number
}

type ValidationError = string;

interface ProfileErrors {
  gender?: ValidationError
  dob?: ValidationError
  phone?: ValidationError
  address?: ValidationError
  city?: ValidationError
  country?: ValidationError
  postal_code?: ValidationError
  profession?: ValidationError
  height?: ValidationError
  weight?: ValidationError
  dietary_preference?: ValidationError
  purpose_of_joining?: ValidationError
}

interface ProfileFormProps {
  onComplete: () => void
}

interface UserProfile extends ProfileData {
  onboarding_status: string;
}

interface OnboardingQA {
  question: string;
  message: string;
  is_done: boolean;
  count: number;
}

export default function ProfileForm({ onComplete }: ProfileFormProps) {
  const router = useRouter()
  const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([])
  const [purposesOfJoining, setPurposesOfJoining] = useState<string[]>([])
  const [onboardingQA, setOnboardingQA] = useState<OnboardingQA | null>(null)
  const [userResponse, setUserResponse] = useState('')
  const [formData, setFormData] = useState<UserProfile>({
    gender: '',
    dob: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    postal_code: '',
    profession: '',
    height: '',
    weight: '',
    dietary_preference: [],
    purpose_of_joining: [],
    bmi: undefined,
    onboarding_status: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<ProfileErrors>({})
  const [progressMessage, setProgressMessage] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [profileData, dietaryPrefs, joiningPurposes] = await Promise.all([
          apiCall('/api/users/me'),
          apiCall('/api/users/dietary-preferences'),
          apiCall('/api/users/joining-purposes')
        ])

        // Check if this is a restart request
        const isRestart = window.location.search.includes('restart=true')
        
        if (profileData.onboarding_status === 'completed' && !isRestart) {
          router.push('/dashboard')
          return
        }

        setFormData({
          ...profileData,
          dietary_preference: profileData.dietary_preference ? profileData.dietary_preference.split(',') : [],
          purpose_of_joining: profileData.purpose_of_joining ? profileData.purpose_of_joining.split(',') : [],
        })

        setDietaryPreferences(dietaryPrefs.preferences)
        setPurposesOfJoining(joiningPurposes.purposes)
      } catch (error) {
        console.error('Failed to fetch data:', error)
        // Optionally, handle error display to the user
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [router])

  const handleChange = (field: keyof Omit<ProfileData, 'bmi'>, value: string | string[]) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value }
      
      // Calculate BMI when height or weight changes
      if (field === 'height' || field === 'weight') {
        const height = Number(field === 'height' ? value : prev.height)
        const weight = Number(field === 'weight' ? value : prev.weight)
        
        if (height > 0 && weight > 0) {
          // BMI = weight (kg) / (height (m))²
          const heightInMeters = height / 100
          const bmi = weight / (heightInMeters * heightInMeters)
          newData.bmi = Math.round(bmi * 10) / 10
        }
      }
      
      return newData
    })
    
    if (field in errors) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const handleMultiSelect = (field: 'dietary_preference' | 'purpose_of_joining', value: string) => {
    setFormData(prev => {
      const currentValues = prev[field]
      const newValues = Array.isArray(currentValues)
        ? currentValues.includes(value)
          ? currentValues.filter(v => v !== value)
          : [...currentValues, value]
        : [value]
      return { ...prev, [field]: newValues }
    })
  }

  const validateForm = (): boolean => {
    const validationErrors: ProfileErrors = {}
    
    // Basic field validations
    if (!formData.gender) validationErrors.gender = 'Gender is required'
    if (!formData.dob) validationErrors.dob = 'Date of birth is required'
    if (!formData.phone) validationErrors.phone = 'Phone number is required'
    if (!formData.profession) validationErrors.profession = 'Profession is required'
    
    // Height and weight validations
    const height = Number(formData.height)
    const weight = Number(formData.weight)
    if (!height || height <= 0) validationErrors.height = 'Valid height is required'
    if (!weight || weight <= 0) validationErrors.weight = 'Valid weight is required'
    
    // Multi-select validations
    if (!formData.dietary_preference || formData.dietary_preference.length === 0) {
      validationErrors.dietary_preference = 'Select at least one dietary preference'
    }
    if (!formData.purpose_of_joining || formData.purpose_of_joining.length === 0) {
      validationErrors.purpose_of_joining = 'Select at least one purpose'
    }

    setErrors(validationErrors)
    return Object.keys(validationErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    setProgressMessage("Our nutritionists are analyzing your data to create a personalized health profile...")
    try {
      // Update the profile
      await apiCall('/api/users/profile', {
        method: 'PUT',
        body: JSON.stringify({
          ...formData,
          dietary_preference: formData.dietary_preference.join(','),
          purpose_of_joining: formData.purpose_of_joining.join(',')
        })
      })

      setProgressMessage("Your health profile is ready! Preparing your personalized nutrition plan...")
      onComplete()
    } catch (error) {
      console.error('Profile update failed:', error)
      setProgressMessage("We encountered an issue while processing your data. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const fetchOnboardingQA = async () => {
    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa')
      setOnboardingQA(response)
    } catch (error) {
      console.error('Failed to fetch onboarding Q&A:', error)
    }
  }

  const handleQASubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!onboardingQA) return

    try {
      const response = await apiCall('/api/medical-reports/onboarding-qa', {
        method: 'POST',
        body: JSON.stringify({ answer: userResponse })
      })
      setOnboardingQA(response)
      setUserResponse('')

      if (response.is_done || (response.count > 3 && response.message !== '')) {
        onComplete()
      }
    } catch (error) {
      console.error('Failed to submit onboarding Q&A:', error)
    }
  }

  useEffect(() => {
    fetchOnboardingQA()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
          <p className="text-gray-600">Help us personalize your nutrition experience</p>
        </div>

        {onboardingQA ? (
          (onboardingQA.count <= 3 || onboardingQA.message === '') ? (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Quick Questions</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleQASubmit} className="space-y-4">
                  <div>
                    <ReactMarkdown>{onboardingQA.question ? (typeof onboardingQA.question === 'string' ? onboardingQA.question : JSON.stringify(onboardingQA.question)) : 'No question available'}</ReactMarkdown>
                  </div>
                  <Input
                    value={userResponse}
                    onChange={(e) => setUserResponse(e.target.value)}
                    placeholder="Your answer"
                    className="w-full px-4 py-3 text-lg"
                  />
                  <Button type="submit">Submit</Button>
                </form>
              </CardContent>
            </Card>
          ) : onboardingQA.message !== '' ? (
            <Card className="mb-8">
              <CardContent>
                <p>{onboardingQA.message}</p>
              </CardContent>
            </Card>
          ) : null
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => handleChange('gender', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="other">Other</option>
                  </select>
                  {errors.gender && <p className="text-sm text-red-600 mt-1">{errors.gender}</p>}
                </div>

                <Input
                  type="date"
                  label="Date of Birth"
                  value={formData.dob}
                  onChange={(e) => handleChange('dob', e.target.value)}
                  error={errors.dob}
                />

                <Input
                  type="tel"
                  label="Phone Number"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  error={errors.phone}
                  placeholder="+1 (555) 123-4567"
                />

                <Input
                  label="Profession"
                  value={formData.profession}
                  onChange={(e) => handleChange('profession', e.target.value)}
                  error={errors.profession}
                  placeholder="e.g., Software Engineer"
                />

                <Input
                  label="City"
                  value={formData.city}
                  onChange={(e) => handleChange('city', e.target.value)}
                  placeholder="Your city"
                />

                <Input
                  label="Country"
                  value={formData.country}
                  onChange={(e) => handleChange('country', e.target.value)}
                  placeholder="Your country"
                />

                <Input
                  label="Address"
                  value={formData.address}
                  onChange={(e) => handleChange('address', e.target.value)}
                  placeholder="Street address"
                  className="md:col-span-2"
                />

                <Input
                  label="Postal Code"
                  value={formData.postal_code}
                  onChange={(e) => handleChange('postal_code', e.target.value)}
                  placeholder="12345"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
                  <Input
                    type="number"
                    value={formData.height}
                    onChange={(e) => handleChange('height', e.target.value)}
                    error={errors.height}
                    placeholder="Height in centimeters"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
                  <Input
                    type="number"
                    value={formData.weight}
                    onChange={(e) => handleChange('weight', e.target.value)}
                    error={errors.weight}
                    placeholder="Weight in kilograms"
                  />
                </div>

                {formData.bmi !== undefined && formData.bmi > 0 && (
                  <div className="md:col-span-2">
                    <p className="text-sm text-gray-600">Your BMI: {formData.bmi}</p>
                  </div>
                )}

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Array.isArray(dietaryPreferences) ? dietaryPreferences.map((pref: string) => (
                      <div key={pref} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`diet-${pref}`}
                          checked={formData.dietary_preference.includes(pref)}
                          onChange={() => handleMultiSelect('dietary_preference', pref)}
                          className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`diet-${pref}`} className="ml-2 text-sm text-gray-600">
                          {pref}
                        </label>
                      </div>
                    )) : null}
                  </div>
                  {errors.dietary_preference && (
                    <p className="text-sm text-red-600 mt-1">{errors.dietary_preference}</p>
                  )}
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Purpose of Joining</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {purposesOfJoining.map((purpose: string) => (
                      <div key={purpose} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`purpose-${purpose}`}
                          checked={formData.purpose_of_joining.includes(purpose)}
                          onChange={() => handleMultiSelect('purpose_of_joining', purpose)}
                          className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`purpose-${purpose}`} className="ml-2 text-sm text-gray-600">
                          {purpose}
                        </label>
                      </div>
                    ))}
                  </div>
                  {errors.purpose_of_joining && (
                    <p className="text-sm text-red-600 mt-1">{errors.purpose_of_joining}</p>
                  )}
                </div>
              </div>

              <div className="flex flex-col items-center pt-6">
                {loading && (
                  <p className="text-green-600 mb-4">{progressMessage}</p>
                )}
                <Button type="submit" loading={loading} size="lg">
                  Continue
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}