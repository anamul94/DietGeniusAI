'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import GoogleLogin from '@/components/auth/GoogleLogin'

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
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return <GoogleLogin />
}
