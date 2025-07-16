'use client'

import { useRouter } from 'next/navigation'
import GoogleSignInPopup from './GoogleSignInPopup'

// Example 1: Basic usage with automatic redirect
export function BasicGoogleSignIn() {
  return (
    <GoogleSignInPopup />
  )
}

// Example 2: Custom success handler
export function CustomGoogleSignIn() {
  const handleSuccess = (data: { token: string; userId: string; onboardingStatus: string }) => {
    console.log('User authenticated:', data)
    // Custom logic here
  }

  const handleError = (error: string) => {
    console.error('Authentication failed:', error)
  }

  return (
    <GoogleSignInPopup 
      onSuccess={handleSuccess}
      onError={handleError}
    />
  )
}

// Example 3: Custom redirect
export function CustomRedirectGoogleSignIn() {
  return (
    <GoogleSignInPopup 
      customRedirectPath="/profile"
    />
  )
}

// Example 4: No redirect (manual handling)
export function ManualGoogleSignIn() {
  const router = useRouter()
  
  const handleSuccess = (data: { token: string; userId: string; onboardingStatus: string }) => {
    // Handle authentication manually
    if (data.onboardingStatus === 'PENDING') {
      router.push('/onboarding')
    } else {
      router.push('/dashboard')
    }
  }

  return (
    <GoogleSignInPopup 
      redirectAfterSuccess={false}
      onSuccess={handleSuccess}
    />
  )
}