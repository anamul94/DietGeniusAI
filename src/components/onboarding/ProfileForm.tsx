'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { apiCall } from '@/lib/utils'

interface ProfileData {
  gender: string
  dob: string
  phone: string
  address: string
  city: string
  country: string
  postal_code: string
  profession: string
}

interface ProfileFormProps {
  onComplete: () => void
}

export default function ProfileForm({ onComplete }: ProfileFormProps) {
  const [formData, setFormData] = useState<ProfileData>({
    gender: '',
    dob: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    postal_code: '',
    profession: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Partial<ProfileData>>({})

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true)
      try {
        const data = await apiCall('/api/users/me')
        setFormData(prev => ({
          ...prev,
          gender: data.gender || '',
          dob: data.dob || '',
          phone: data.phone || '',
          address: data.address || '',
          city: data.city || '',
          country: data.country || '',
          postal_code: data.postal_code || '',
          profession: data.profession || '',
        }))
      } catch (error) {
        console.error('Failed to fetch user profile:', error)
        // Optionally, handle error display to the user
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  const handleChange = (field: keyof ProfileData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = () => {
    const newErrors: Partial<ProfileData> = {}
    
    if (!formData.gender) newErrors.gender = 'Gender is required'
    if (!formData.dob) newErrors.dob = 'Date of birth is required'
    if (!formData.phone) newErrors.phone = 'Phone number is required'
    if (!formData.profession) newErrors.profession = 'Profession is required'
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    try {
      await apiCall('/api/users/profile', {
        method: 'PUT',
        body: JSON.stringify(formData)
      })
      onComplete()
    } catch (error) {
      console.error('Profile update failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
          <p className="text-gray-600">Help us personalize your nutrition experience</p>
        </div>

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

              <div className="flex justify-end pt-6">
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