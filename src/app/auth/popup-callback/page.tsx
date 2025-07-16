'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'

export default function PopupCallback() {
  const searchParams = useSearchParams()
  const [status, setStatus] = useState('Processing authentication...')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const token = searchParams.get('token')
        const userId = searchParams.get('user_id')
        const onboardingStatus = searchParams.get('onboarding_status')
        
        console.log('Popup callback params:', { token, userId, onboardingStatus })
        
        if (!token || !userId) {
          throw new Error('Missing authentication parameters')
        }
        
        // Send success message to parent window
        if (window.opener) {
          window.opener.postMessage({
            type: 'GOOGLE_AUTH_SUCCESS',
            token,
            userId,
            onboardingStatus
          }, window.location.origin)
          
          // Close the popup
          window.close()
        } else {
          // Fallback: redirect to main callback page
          window.location.href = `/auth/callback?token=${token}&user_id=${userId}&onboarding_status=${onboardingStatus}`
        }
      } catch (error) {
        console.error('Popup callback error:', error)
        setStatus('Authentication failed')
        
        // Send error message to parent window
        if (window.opener) {
          window.opener.postMessage({
            type: 'GOOGLE_AUTH_ERROR',
            error: error instanceof Error ? error.message : 'Unknown error'
          }, window.location.origin)
          window.close()
        }
      }
    }

    if (searchParams.toString()) {
      handleCallback()
    }
  }, [searchParams])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">{status}</p>
      </div>
    </div>
  )
}