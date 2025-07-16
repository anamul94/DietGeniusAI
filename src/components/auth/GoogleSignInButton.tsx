'use client'

import { Button } from '@/components/ui/button'
import GoogleSignInPopup from './GoogleSignInPopup'

interface GoogleSignInButtonProps {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  onSuccess?: (data: { token: string; userId: string; onboardingStatus: string }) => void
  onError?: (error: string) => void
  redirectAfterSuccess?: boolean
  customRedirectPath?: string
}

export default function GoogleSignInButton({
  variant = 'default',
  size = 'default',
  className = '',
  onSuccess,
  onError,
  redirectAfterSuccess = true,
  customRedirectPath
}: GoogleSignInButtonProps) {
  return (
    <GoogleSignInPopup
      onSuccess={onSuccess}
      onError={onError}
      redirectAfterSuccess={redirectAfterSuccess}
      customRedirectPath={customRedirectPath}
    />
  )
}