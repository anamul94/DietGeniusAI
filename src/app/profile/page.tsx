'use client'

import ProfileForm from '@/components/onboarding/ProfileForm'
import { useRouter } from 'next/navigation'

export default function ProfilePage() {
  const router = useRouter()

  const handleComplete = () => {
    router.push('/dashboard')
  }

  return <ProfileForm onComplete={handleComplete} />
}