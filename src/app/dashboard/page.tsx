'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/button'
import { apiCall } from '@/lib/utils'
import { User, FileText, Activity, Settings, LogOut, Brain } from 'lucide-react'
import GoogleHealthLogin from '@/components/auth/GoogleHealthLogin'
import GoogleHealthDataFetcher from '@/components/google-health/GoogleHealthDataFetcher'
import GoogleHealthStatusAndRevoke from '@/components/google-health/GoogleHealthStatusAndRevoke'


interface UserProfile {
  email: string
  username: string
  age?: number
  profession?: string
  onboarding_status: string
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/')
      return
    }

    fetchUserProfile()
  }, [router])

  const fetchUserProfile = async () => {
    try {
      const userData = await apiCall('/api/users/me')
      setUser(userData)
      
      if (userData.onboarding_status?.toLowerCase() === 'pending') {
        router.push('/onboarding')
        return
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      router.push('/')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">NutriGenius</h1>
                <p className="text-sm text-gray-500">AI-Powered Diet Management</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-medium text-gray-900">{user?.username}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back, {user?.username}!</h2>
          <p className="text-gray-600">Your personalized nutrition dashboard</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Profile Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Age: {user?.age || 'Not specified'}</p>
                <p className="text-sm text-muted-foreground">Profession: {user?.profession || 'Not specified'}</p>
                <p className="text-sm text-muted-foreground">
                  Status: 
                  <span className={`ml-1 px-2 py-1 rounded-full text-xs ${
                    user?.onboarding_status?.toLowerCase() === 'completed' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {user?.onboarding_status}
                  </span>
                </p>
              </div>
              <Button variant="outline" size="sm" className="w-full mt-4" onClick={() => router.push('/profile')}>
                <Settings className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
            </CardContent>
          </Card>

          {/* Medical Reports Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Medical Reports
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Upload and manage your medical reports for personalized recommendations.
              </p>
              <Button variant="outline" size="sm" className="w-full" onClick={() => router.push('/reports')}>
                <FileText className="w-4 h-4 mr-2" />
                View Reports
              </Button>
            </CardContent>
          </Card>

          {/* Health Insights Card (Placeholder for general insights) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Health Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Get AI-powered insights based on your health profile and goals.
              </p>
              <Button variant="outline" size="sm" className="w-full" onClick={() => router.push('/insights')}>
                <Activity className="w-4 h-4 mr-2" />
                View Insights
              </Button>
            </CardContent>
          </Card>

          {/* Google Health Login Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Connect Google Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Connect your Google Health account to fetch and sync health data.
              </p>
              <GoogleHealthLogin />
            </CardContent>
          </Card>

          {/* Google Health Data Fetcher Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Fetch Health Data
              </CardTitle>
            </CardHeader>
            <CardContent>
              <GoogleHealthDataFetcher />
            </CardContent>
          </Card>

          {/* Google Health Status & Revoke Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Google Health Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <GoogleHealthStatusAndRevoke />
            </CardContent>
          </Card>

          {/* Food Nutrition Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Food Nutrition Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Analyze your food intake for detailed nutritional insights.
              </p>
              <Button variant="outline" size="sm" className="w-full" onClick={() => router.push('/food-nutrition-analysis')}>
                Analyze Food Nutrition
              </Button>
            </CardContent>
          </Card>

          {/* Meal Plan Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                Meal Plan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Generate and view your personalized AI-powered meal plans.
              </p>
              <Button variant="outline" size="sm" className="w-full" onClick={() => router.push('/meal-plan')}>
                Generate Meal Plan
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Welcome Message */}
        <Card>
          <CardContent>
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Congratulations on completing your setup!
              </h3>
              <p className="text-gray-600 mb-6">
                Your personalized nutrition journey starts here. Our AI will analyze your health profile and provide tailored recommendations.
              </p>
              <div className="flex justify-center gap-4">
                <Button>
                  Start Nutrition Plan
                </Button>
                <Button variant="outline">
                  Explore Features
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
