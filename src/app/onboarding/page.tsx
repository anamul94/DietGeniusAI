'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ProfileForm from '@/components/onboarding/ProfileForm'
import MedicalChoice from '@/components/onboarding/MedicalChoice'
import MedicalUpload from '@/components/onboarding/MedicalUpload'
import OnboardingChat from '@/components/onboarding/OnboardingChat'

type OnboardingStep = 'profile' | 'medical-choice' | 'medical-upload' | 'chat'

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('profile')
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/')
      return
    }

    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      if (user.onboarding_status?.toLowerCase() === 'completed') {
        router.push('/dashboard')
        return
      }
    }
  }, [router])

  const handleProfileComplete = () => {
    setCurrentStep('medical-choice')
  }

  const handleMedicalChoice = () => {
    setCurrentStep('medical-upload')
  }

  const handleMedicalComplete = () => {
    setCurrentStep('chat')
  }

  const handleMedicalSkip = () => {
    setCurrentStep('chat')
  }

  const handleOnboardingComplete = () => {
    // Update user info in localStorage
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      user.onboarding_status = 'COMPLETED'
      localStorage.setItem('user_info', JSON.stringify(user))
    }
    
    router.push('/dashboard')
  }

  const renderStep = () => {
    switch (currentStep) {
      case 'profile':
        return <ProfileForm onComplete={handleProfileComplete} />
      case 'medical-choice':
        return (
          <MedicalChoice 
            onUpload={handleMedicalChoice}
            onSkip={handleMedicalSkip}
          />
        )
      case 'medical-upload':
        return (
          <MedicalUpload 
            onComplete={handleMedicalComplete}
            onSkip={handleMedicalSkip}
          />
        )
      case 'chat':
        return <OnboardingChat onComplete={handleOnboardingComplete} />
      default:
        return null
    }
  }

  return renderStep()
}