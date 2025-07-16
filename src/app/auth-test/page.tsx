'use client'

import { useState } from 'react'
import GoogleSignInPopup from '@/components/auth/GoogleSignInPopup'

export default function AuthTestPage() {
  const [authStatus, setAuthStatus] = useState<string>('')

  const handleSuccess = (data: { token: string; userId: string; onboardingStatus: string }) => {
    setAuthStatus(`Successfully authenticated! User ID: ${data.userId}`)
  }

  const handleError = (error: string) => {
    setAuthStatus(`Error: ${error}`)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Google Sign-In Popup Test</h1>
          <p className="text-gray-600">Click the button below to test Google Sign-In with popup</p>
        </div>

        <div className="card">
          <div className="mb-6">
            <GoogleSignInPopup 
              onSuccess={handleSuccess}
              onError={handleError}
            />
          </div>

          {authStatus && (
            <div className="mt-4 p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-700">{authStatus}</p>
            </div>
          )}

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              This is a test page for the Google Sign-In popup functionality
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}