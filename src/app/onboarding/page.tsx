'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import OnboardingFlow from '@/components/onboarding/OnboardingFlow'

export default function OnboardingPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/')
      return
    }

    // Check if this is a restart request
    const isRestart = searchParams.get('restart') === 'true'
    
    // Only redirect if not restarting and onboarding is completed
    if (!isRestart) {
      const userInfo = localStorage.getItem('user_info')
      if (userInfo) {
        const user = JSON.parse(userInfo)
        if (user.onboarding_status?.toLowerCase() === 'completed') {
          router.push('/dashboard')
          return
        }
      }
    }
  }, [router, searchParams])

  return <OnboardingFlow />
}