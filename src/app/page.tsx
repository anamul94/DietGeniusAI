'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import GoogleLogin from '@/components/auth/GoogleLogin'
import { PageWrapper, LoadingState } from '@/components/layout/PageWrapper'

export default function Home() {
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('access_token')
    const userInfo = localStorage.getItem('user_info')
    
    if (token && userInfo) {
      const user = JSON.parse(userInfo)
      if (user.onboarding_status === 'COMPLETED') {
        router.push('/dashboard')
      } else {
        router.push('/onboarding')
      }
    } else {
      setLoading(false)
    }
  }, [router])

  if (loading) {
    return (
      <PageWrapper background="gradient" showPattern>
        <LoadingState message="Checking authentication..." />
      </PageWrapper>
    )
  }

  return (
    <PageWrapper 
      background="gradient" 
      showPattern
      className="flex items-center justify-center"
    >
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-slate-50 mb-4">
            Welcome to <span className="gradient-text">NutriGenius</span>
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            AI-powered nutrition guidance tailored to your unique health profile
          </p>
        </div>
        <GoogleLogin />
      </div>
    </PageWrapper>
  )
}
