'use client'

import GoogleSignInPopup from './GoogleSignInPopup'
import LogoutButton from './LogoutButton'
import { useAuth } from '@/hooks/useAuth'

export function AuthExample() {
  const { isAuthenticated, user, loading, logout } = useAuth()

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="p-4">
      {isAuthenticated ? (
        <div>
          <p>Welcome, user {user?.id}</p>
          <p>Status: {user?.onboarding_status}</p>
          <LogoutButton />
        </div>
      ) : (
        <GoogleSignInPopup />
      )}
    </div>
  )
}