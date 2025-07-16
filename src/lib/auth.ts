'use client'

// Authentication utilities for managing tokens and user sessions

export const AUTH_KEYS = {
  ACCESS_TOKEN: 'access_token',
  USER_INFO: 'user_info',
  REFRESH_TOKEN: 'refresh_token'
} as const

/**
 * Clear all authentication data from localStorage
 */
export function clearAuthData(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(AUTH_KEYS.USER_INFO)
    localStorage.removeItem(AUTH_KEYS.REFRESH_TOKEN)
  }
}

/**
 * Get current access token
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN)
  }
  return null
}

/**
 * Get current user info
 */
export function getUserInfo(): { id: string; onboarding_status: string } | null {
  if (typeof window !== 'undefined') {
    const userInfo = localStorage.getItem(AUTH_KEYS.USER_INFO)
    if (userInfo) {
      try {
        return JSON.parse(userInfo)
      } catch {
        return null
      }
    }
  }
  return null
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null
}

/**
 * Logout user and redirect to home page
 */
export function logout(redirect: boolean = true): void {
  clearAuthData()
  
  if (redirect && typeof window !== 'undefined') {
    window.location.href = '/'
  }
}

/**
 * Store authentication data after successful login
 */
export function storeAuthData(token: string, userId: string, onboardingStatus: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_KEYS.ACCESS_TOKEN, token)
    localStorage.setItem(AUTH_KEYS.USER_INFO, JSON.stringify({
      id: userId,
      onboarding_status: onboardingStatus
    }))
  }
}