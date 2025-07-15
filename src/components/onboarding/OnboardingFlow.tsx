'use client'

import { useState } from 'react'
import ProfileForm from './ProfileForm'
import MedicalUpload from './MedicalUpload'
import OnboardingChat from './OnboardingChat'
import { useRouter } from 'next/navigation'

export default function OnboardingFlow() {
  const [step, setStep] = useState(1)
  const router = useRouter()

  const handleProfileComplete = () => {
    setStep(2)
  }

  const handleMedicalUploadComplete = () => {
    setStep(3)
  }

  const handleMedicalUploadSkip = () => {
    setStep(3)
  }

  const handleChatComplete = () => {
    // Update user info in localStorage
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      user.onboarding_status = 'COMPLETED'
      localStorage.setItem('user_info', JSON.stringify(user))
    }
    
    router.push('/dashboard')
  }

  return (
    <div>
      <div className="fixed top-0 left-0 right-0 h-2 bg-gray-200">
        <div 
          className="h-full bg-green-500 transition-all duration-500"
          style={{ width: `${(step / 3) * 100}%` }}
        />
      </div>

      {step === 1 && <ProfileForm onComplete={handleProfileComplete} />}
      {step === 2 && (
        <MedicalUpload 
          onComplete={handleMedicalUploadComplete}
          onSkip={handleMedicalUploadSkip}
        />
      )}
      {step === 3 && <OnboardingChat onComplete={handleChatComplete} />}
    </div>
  )
}