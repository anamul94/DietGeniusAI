'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter } from 'next/navigation'

function AuthCallbackContent() {
  const router = useRouter()
  const [status, setStatus] = useState('Processing...')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token')
        const userId = urlParams.get('user_id')
        const onboardingStatus = urlParams.get('onboarding_status')
        
        console.log('Callback params:', { token, userId, onboardingStatus })
        
        if (!token || !userId) {
          throw new Error('Missing authentication parameters')
        }
        
        localStorage.setItem('access_token', token)
        localStorage.setItem('user_info', JSON.stringify({
          id: userId,
          onboarding_status: onboardingStatus
        }))
        
        console.log('Redirecting to:', onboardingStatus === 'PENDING' ? '/onboarding' : '/dashboard')
        
        if (onboardingStatus?.toLowerCase() === 'pending') {
          router.push('/onboarding')
        } else {
          router.push('/dashboard')
        }
      } catch (error) {
        console.error('Auth callback error:', error)
        setStatus('Authentication failed. Redirecting...')
        setTimeout(() => router.push('/'), 2000)
      }
    }

    handleCallback()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">{status}</p>
      </div>
    </div>
  )
}

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}