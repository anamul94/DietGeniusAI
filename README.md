# NutriGenius Frontend

A responsive Next.js frontend for the DietGeniusAI nutrition management application.

## Features

- **Google OAuth Authentication**: Secure login with Google
- **User Onboarding**: Complete profile setup with medical file upload
- **AI-Powered Q&A**: Interactive health assessment with AI agent
- **Responsive Design**: Mobile-first design with medical/diet theme
- **Medical File Upload**: Support for PDF, DOC, images (max 4 files)
- **Dashboard**: User profile and health insights overview

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS with custom medical theme
- **Icons**: Lucide React
- **Authentication**: Google OAuth via backend API
- **File Upload**: Drag-and-drop with validation

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Setup**:
   Create `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run Development Server**:
   ```bash
   npm run dev
   ```

4. **Build for Production**:
   ```bash
   npm run build
   npm start
   ```

## User Flow

1. **Login**: Google OAuth authentication
2. **Profile Setup**: Complete personal information
3. **Medical Upload**: Optional medical report upload (max 4 files)
4. **Health Assessment**: AI-powered Q&A session (4 rounds)
5. **Dashboard**: Access to personalized nutrition features

## API Integration

The frontend integrates with the DietGeniusAI backend API:

- `/api/auth/google-login` - Google OAuth initiation
- `/api/auth/google/callback` - OAuth callback handling
- `/api/users/me` - User profile management
- `/api/users/profile` - Profile updates
- `/api/medical-reports/medical` - Medical file upload
- `/api/medical-reports/onboarding-qa` - AI Q&A session

## Design System

### Colors
- **Primary Green**: #22c55e (health/nutrition theme)
- **Secondary Blue**: #3b82f6 (trust/medical theme)
- **Accent Orange**: #f97316 (energy/vitality)
- **Neutral Gray**: #6b7280 (text/backgrounds)

### Components
- Reusable UI components in `/src/components/ui/`
- Feature-specific components in `/src/components/`
- Responsive design with mobile-first approach

## File Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── auth/callback/      # OAuth callback handler
│   ├── onboarding/         # User onboarding flow
│   ├── dashboard/          # Main dashboard
│   └── page.tsx           # Home/login page
├── components/
│   ├── ui/                # Reusable UI components
│   ├── auth/              # Authentication components
│   └── onboarding/        # Onboarding flow components
└── lib/
    └── utils.ts           # Utility functions and API helpers
```

## Responsive Design

- **Mobile**: Optimized for touch interactions
- **Tablet**: Balanced layout with improved spacing
- **Desktop**: Full-featured layout with sidebar navigation

## Security Features

- JWT token storage in localStorage
- API request authentication
- File upload validation and size limits
- Secure OAuth flow handling