/**
 * Test script for SSE connection with cookie-based authentication
 */

import { setAuthToken } from './auth-cookies';
import { useEnhancedSSEConnection } from './sse-manager-enhanced';

/**
 * Test SSE connection with the new cookie-based authentication
 */
export async function testSSEConnection() {
  const sseManager = useEnhancedSSEConnection();
  
  // Get token from localStorage (for testing purposes)
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('No access token found. Please login first.');
    return false;
  }
  
  // Set token in cookies
  setAuthToken(token, 60);
  
  // Generate a session ID
  const sessionId = `test_${Date.now()}`;
  
  // Test URL
  const url = `http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=${sessionId}`;
  
  console.log('Testing SSE connection...');
  console.log('URL:', url);
  console.log('Session ID:', sessionId);
  
  const success = await sseManager.connect({
    url,
    onMessage: (data) => {
      console.log('Received message:', data);
    },
    onError: (error) => {
      console.error('SSE Error:', error);
    },
    onOpen: () => {
      console.log('SSE connection established');
    },
    onClose: () => {
      console.log('SSE connection closed');
    },
    timeout: 10000
  });
  
  if (success) {
    console.log('SSE connection test started successfully');
    
    // Close connection after 30 seconds for testing
    setTimeout(() => {
      sseManager.close();
      console.log('Test connection closed');
    }, 30000);
  } else {
    console.error('Failed to start SSE connection test');
  }
  
  return success;
}

/**
 * Manual test function for browser console
 */
export function runSSETest() {
  // @ts-ignore
  window.testSSE = testSSEConnection;
  console.log('SSE test function available as window.testSSE()');
}