'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import OnboardingFlow from '@/components/onboarding/OnboardingFlow'

export default function OnboardingPage() {
  const router = useRouter()

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/')
      return
    }

    // Check onboarding status
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      if (user.onboarding_status?.toLowerCase() === 'completed') {
        router.push('/dashboard')
        return
      }
    }
  }, [router])

  return <OnboardingFlow />
}