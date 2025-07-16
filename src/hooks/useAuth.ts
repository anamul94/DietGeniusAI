'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  getAccessToken, 
  getUserInfo, 
  isAuthenticated as checkAuth, 
  clearAuthData,
  storeAuthData
} from '@/lib/auth'

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<{ id: string; onboarding_status: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check authentication status on mount
    const token = getAccessToken()
    const userInfo = getUserInfo()
    
    setIsAuthenticated(!!token)
    setUser(userInfo)
    setLoading(false)
  }, [])

  const login = (token: string, userId: string, onboardingStatus: string) => {
    storeAuthData(token, userId, onboardingStatus)
    setIsAuthenticated(true)
    setUser({ id: userId, onboarding_status: onboardingStatus })
    
    // Redirect based on onboarding status
    if (onboardingStatus === 'PENDING') {
      router.push('/onboarding')
    } else {
      router.push('/dashboard')
    }
  }

  const logout = (redirectTo: string = '/') => {
    clearAuthData()
    setIsAuthenticated(false)
    setUser(null)
    router.push(redirectTo)
  }

  return {
    isAuthenticated,
    user,
    loading,
    login,
    logout
  }
}