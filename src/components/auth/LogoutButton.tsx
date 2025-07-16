'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { logout } from '@/lib/auth'

interface LogoutButtonProps {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  redirectAfterLogout?: boolean
  customRedirectPath?: string
  onLogout?: () => void
  children?: React.ReactNode
}

export default function LogoutButton({
  variant = 'outline',
  size = 'default',
  className = '',
  redirectAfterLogout = true,
  customRedirectPath,
  onLogout,
  children
}: LogoutButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleLogout = () => {
    setIsLoading(true)
    
    // Call custom logout handler if provided
    if (onLogout) {
      onLogout()
    }
    
    // Clear auth data
    logout(false) // Don't redirect immediately
    
    // Handle redirect
    if (redirectAfterLogout) {
      const redirectPath = customRedirectPath || '/'
      router.push(redirectPath)
    }
    
    setIsLoading(false)
  }

  return (
    <Button 
      onClick={handleLogout}
      disabled={isLoading}
      variant={variant}
      size={size}
      className={className}
    >
      {isLoading ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
          Logging out...
        </>
      ) : (
        children || 'Logout'
      )}
    </Button>
  )
}