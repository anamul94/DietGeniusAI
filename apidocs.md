# NutriGenius Application Documentation

## 1. Introduction

NutriGenius is an AI-powered diet management application designed to provide personalized nutrition plans and health insights based on user profiles and medical data. This document serves as a comprehensive guide to the application's features, user interactions, API integrations, and underlying technical architecture.

## 2. Features

NutriGenius offers a robust set of features to empower users in their health journey:

*   **User Authentication & Authorization**: Secure sign-up, login, and session management.
*   **User Profile Management**: Users can create and update their personal information, including age, profession, and onboarding status.
*   **Onboarding Process**: A guided initial setup for new users to collect essential medical and profile information.
*   **Medical Report Management**:
    *   **Upload**: Users can upload various medical reports (e.g., blood tests, diagnoses).
    *   **Dynamic Display**: Reports are dynamically rendered from structured JSON data, supporting Markdown content for rich text.
*   **AI-Powered Health Insights**:
    *   Generates personalized health insights and recommendations based on uploaded medical data and user profiles.
    *   Integrates with Google Health API for fetching and analyzing health data (e.g., steps, heart rate, sleep, weight, nutrition).
*   **Food Nutrition Analysis**: Allows users to analyze their food intake to get detailed nutritional breakdowns.
*   **Personalized Meal Plans**: (Implied by "AI-powered diet management" - details to be elaborated if implemented)
*   **Responsive Design**: Built with Next.js, Tailwind CSS, and Shadcn UI for a seamless experience across various devices.
*   **Dockerized Deployment**: Facilitates easy and consistent deployment across different environments.

## 3. User Flow

The typical user journey through the NutriGenius application is as follows:

1.  **Landing Page (`/`)**: Users arrive at the application's entry point.
2.  **Authentication (`/auth`)**:
    *   **Sign Up**: New users register for an account.
    *   **Login**: Existing users sign in.
3.  **Onboarding (`/onboarding`)**: (For new users or users with `onboarding_status: 'pending'`)
    *   Users provide initial medical information and complete their profile.
4.  **Dashboard (`/dashboard`)**: The central hub for users, displaying:
    *   User profile summary.
    *   Links to Medical Reports, Health Insights, Food Nutrition Analysis.
    *   Google Health integration options (Connect, Fetch Data, Status).
5.  **Profile Management (`/profile`)**: Users can edit their profile details.
6.  **Medical Reports (`/reports`)**: Users can view and manage their uploaded medical documents.
7.  **Health Insights (`/insights`)**: Displays AI-generated health insights and recommendations.
8.  **Food Nutrition Analysis (`/food-nutrition-analysis`)**: Interface for analyzing food intake.
9.  **Google Health Integration**:
    *   **Connect**: Initiates OAuth flow to connect with Google Health.
    *   **Fetch Data**: Allows users to fetch specific health data types (e.g., steps, heart rate) within a date range.
    *   **Status & Revoke**: Displays connection status and allows users to revoke permissions.

## 4. Technical Architecture

The NutriGenius application follows a client-server architecture, primarily consisting of a Next.js frontend and a Python FastAPI backend.

*   **Frontend**:
    *   **Framework**: Next.js (React)
    *   **Styling**: Tailwind CSS, Shadcn UI (for pre-built, accessible UI components)
    *   **State Management**: React's `useState` and `useEffect` hooks for local component state.
    *   **Routing**: Next.js App Router.
    *   **API Communication**: `fetch` API for interacting with the backend.
    *   **Authentication**: JWT (JSON Web Tokens) stored in `localStorage`.
*   **Backend**:
    *   **Framework**: FastAPI (Python)
    *   **Database**: (Assumed, likely PostgreSQL or similar, based on typical FastAPI setups)
    *   **Authentication**: Handles user registration, login, and token validation.
    *   **API Endpoints**: Provides RESTful APIs for user management, medical reports, health insights, and Google Health integration.
    *   **AI/ML Components**: (Details to be elaborated if specific models/services are used for insights and meal plans).
*   **Google Health API**: External API for fetching user health data.
*   **Deployment**: Docker containers for both frontend and backend.

## 5. API Integration

The frontend communicates with the backend API, which is expected to be running and accessible at `NEXT_PUBLIC_API_URL` (configured in `.env`).

### 5.1. Authentication

*   **Login**:
    *   **Endpoint**: `/api/auth/login` (POST)
    *   **Request**: `{ "username": "...", "password": "..." }`
    *   **Response**: `{ "access_token": "...", "token_type": "bearer" }`
    *   **Usage**: The `access_token` is stored in `localStorage` and used for subsequent authenticated requests.
*   **User Profile**:
    *   **Endpoint**: `/api/users/me` (GET)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Response**: User profile data (`UserProfile` interface).

### 5.2. Medical Reports

*   **Fetch Medical Reports**:
    *   **Endpoint**: `/api/medical-reports/medical` (GET)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Query Parameters**: (Assumed for pagination, e.g., `page`, `limit`)
    *   **Response**: List of medical reports.
*   **Generate Medical Insights**:
    *   **Endpoint**: `/api/medical-reports/memory-test` (POST)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Request**: (Specific to the data required for insight generation)
    *   **Response**: Generated health insights.

### 5.3. Google Health Integration

*   **Get Authorization URL**:
    *   **Endpoint**: `/api/google-health/auth-url` (GET)
    *   **Response**: `{ "auth_url": "..." }` (URL to redirect user for Google OAuth)
*   **Google Health Callback**:
    *   **Endpoint**: `/api/google-health/callback` (GET)
    *   **Query Parameters**: `code`, `state` (handled by backend after Google OAuth redirect)
    *   **Usage**: This endpoint is hit by Google after user grants permission.
*   **Fetch and Save Google Health Data**:
    *   **Endpoint**: `/api/google-health/data/fetch-and-save` (POST)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Request**:
        ```json
        {
          "data_types": ["steps", "heart_rate", "sleep", "weight", "nutrition"],
          "start_date": "YYYY-MM-DDTHH:MM:SSZ",
          "end_date": "YYYY-MM-DDTHH:MM:SSZ"
        }
        ```
    *   **Response**: Fetched and saved health data.
*   **Google Health Connection Status**:
    *   **Endpoint**: `/api/google-health/status` (GET)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Response**: `{ "connected": true/false, "expires_at": "...", "scopes": [...] }`
*   **Revoke Google Health Permissions**:
    *   **Endpoint**: `/api/google-health/revoke` (POST)
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Response**: Success message.

## 6. Data Models (Frontend Perspective)

*   **UserProfile**:
    ```typescript
    interface UserProfile {
      email: string;
      username: string;
      age?: number;
      profession?: string;
      onboarding_status: string; // e.g., 'PENDING', 'COMPLETED'
    }
    ```
*   **GoogleHealthDataItem**: (Example, based on `GoogleHealthDataFetcher` usage)
    ```typescript
    interface GoogleHealthDataItem {
      data_type: string; // e.g., "steps", "heart_rate"
      start_time: string; // ISO 8601 datetime string
      end_time: string;   // ISO 8601 datetime string
      value: any;         // Varies based on data_type (e.g., number for steps, object for nutrition)
      source?: string;
    }
    ```
*   **MedicalReport**: (Assumed structure, based on dynamic rendering)
    ```typescript
    interface MedicalReport {
      id: string;
      title: string;
      date: string;
      content_markdown: string; // Markdown content for display
      // ... other relevant fields
    }
    ```

## 7. Deployment

The application is designed for Dockerized deployment. Refer to the `README.md` for detailed instructions on building and running Docker images for both frontend and backend.

## 8. Contributing

Refer to the `README.md` for guidelines on contributing to the project.

---
*This document is subject to updates as the application evolves.*