/**
 * Utility functions for handling authentication cookies
 */

const AUTH_COOKIE_NAME = 'access_token';

/**
 * Set authentication token in cookies
 */
export function setAuthToken(token: string, expiresInMinutes: number = 60): void {
  if (typeof document === 'undefined') return; // Server-side rendering
  
  const expires = new Date();
  expires.setTime(expires.getTime() + (expiresInMinutes * 60 * 1000));
  
  document.cookie = `${AUTH_COOKIE_NAME}=${token}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
}

/**
 * Get authentication token from cookies
 */
export function getAuthToken(): string | null {
  if (typeof document === 'undefined') return null; // Server-side rendering
  
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === AUTH_COOKIE_NAME) {
      return decodeURIComponent(value);
    }
  }
  return null;
}

/**
 * Remove authentication token from cookies
 */
export function removeAuthToken(): void {
  if (typeof document === 'undefined') return; // Server-side rendering
  
  document.cookie = `${AUTH_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}