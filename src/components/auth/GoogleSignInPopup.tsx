'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { API_BASE_URL } from '@/lib/utils'

interface GoogleSignInPopupProps {
  onSuccess?: (data: { token: string; userId: string; onboardingStatus: string }) => void
  onError?: (error: string) => void
  redirectAfterSuccess?: boolean
  customRedirectPath?: string
}

export default function GoogleSignInPopup({ 
  onSuccess, 
  onError, 
  redirectAfterSuccess = true,
  customRedirectPath 
}: GoogleSignInPopupProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [popupWindow, setPopupWindow] = useState<Window | null>(null)
  const router = useRouter()

  useEffect(() => {
    // Listen for messages from the popup window
    const handleMessage = (event: MessageEvent) => {
      // Verify the origin
      if (event.origin !== window.location.origin) return
      
      if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
        const { token, userId, onboardingStatus } = event.data
        
        // Store authentication data using auth utilities
        import('@/lib/auth').then(({ storeAuthData }) => {
          storeAuthData(token, userId, onboardingStatus)
        })
        
        // Close popup if it's still open
        if (popupWindow && !popupWindow.closed) {
          popupWindow.close()
        }
        
        setIsLoading(false)
        
        // Call success callback if provided
        if (onSuccess) {
          onSuccess({ token, userId, onboardingStatus })
        }
        
        // Redirect if enabled
        if (redirectAfterSuccess) {
          const redirectPath = customRedirectPath || 
            (onboardingStatus === 'PENDING' ? '/onboarding' : '/dashboard')
          router.push(redirectPath)
        }
      } else if (event.data.type === 'GOOGLE_AUTH_ERROR') {
        setIsLoading(false)
        const errorMessage = event.data.error || 'Authentication failed'
        
        if (onError) {
          onError(errorMessage)
        } else {
          console.error('Google authentication error:', errorMessage)
        }
        
        // Close popup on error
        if (popupWindow && !popupWindow.closed) {
          popupWindow.close()
        }
      }
    }

    window.addEventListener('message', handleMessage)
    
    // Cleanup
    return () => {
      window.removeEventListener('message', handleMessage)
      if (popupWindow && !popupWindow.closed) {
        popupWindow.close()
      }
    }
  }, [popupWindow, onSuccess, onError, redirectAfterSuccess, customRedirectPath, router])

  const openGoogleSignInPopup = () => {
    setIsLoading(true)
    
    // Popup window dimensions
    const width = 500
    const height = 600
    const left = (window.screen.width - width) / 2
    const top = (window.screen.height - height) / 2
    
    // Open popup window
    const popup = window.open(
      `${API_BASE_URL}/api/auth/google-login-popup`,
      'google-signin',
      `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
    )
    
    if (!popup) {
      setIsLoading(false)
      const error = 'Failed to open popup. Please check your popup blocker settings.'
      if (onError) onError(error)
      return
    }
    
    setPopupWindow(popup)
    
    // Monitor popup closure
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed)
        setIsLoading(false)
        setPopupWindow(null)
      }
    }, 1000)
  }

  return (
    <Button 
      onClick={openGoogleSignInPopup}
      disabled={isLoading}
      className="w-full"
      size="lg"
    >
      {isLoading ? (
        <>
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          Processing...
        </>
      ) : (
        <>
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </>
      )}
    </Button>
  )
}