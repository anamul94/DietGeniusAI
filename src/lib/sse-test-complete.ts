/**
 * Complete SSE test with proper authentication flow
 */

import { FixedSSEConnectionManager } from './sse-manager-fixed';
import { setAuthToken, getAuthToken } from './auth-cookies';

/**
 * Test SSE connection with proper authentication
 * This function should be called after user login
 */
export async function testCompleteSSEFlow() {
  console.log('=== Starting Complete SSE Test ===');
  
  // Step 1: Check if we have a valid token
  let token = localStorage.getItem('access_token');
  if (!token) {
    console.error('❌ No access token found in localStorage. Please login first.');
    return false;
  }
  
  console.log('✅ Found access token in localStorage');
  
  // Step 2: Set token in cookies
  setAuthToken(token, 60);
  console.log('✅ Token set in cookies');
  
  // Step 3: Verify token is in cookies
  const cookieToken = getAuthToken();
  if (!cookieToken) {
    console.error('❌ Failed to set token in cookies');
    return false;
  }
  console.log('✅ Token verified in cookies');
  
  // Step 4: Create SSE manager
  const manager = new FixedSSEConnectionManager();
  
  // Step 5: Generate session ID
  const sessionId = `test_${Date.now()}`;
  console.log('📋 Session ID:', sessionId);
  
  // Step 6: Build URL
  const url = `http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=${sessionId}`;
  console.log('🔗 SSE URL:', url);
  
  // Step 7: Test connection
  console.log('🔄 Attempting SSE connection...');
  
  const success = await manager.connect({
    url,
    onMessage: (data) => {
      console.log('📨 Received message:', data);
    },
    onError: (error) => {
      console.error('❌ SSE Error:', error);
    },
    onOpen: () => {
      console.log('✅ SSE connection established successfully!');
    },
    onClose: () => {
      console.log('🔐 SSE connection closed');
    },
    timeout: 15000
  });
  
  if (success) {
    console.log('✅ SSE connection test started successfully');
    
    // Close connection after 30 seconds
    setTimeout(() => {
      manager.close();
      console.log('🔚 Test connection closed after 30 seconds');
    }, 30000);
    
    return true;
  } else {
    console.error('❌ Failed to start SSE connection');
    return false;
  }
}

/**
 * Quick test function for browser console
 */
export function quickSSETest() {
  console.log('🚀 Starting Quick SSE Test...');
  testCompleteSSEFlow().then(success => {
    if (success) {
      console.log('🎉 SSE test completed successfully!');
    } else {
      console.log('💥 SSE test failed. Check the logs above.');
    }
  });
}

// Make available globally for browser console testing
if (typeof window !== 'undefined') {
  (window as any).testSSE = quickSSETest;
  (window as any).testCompleteSSE = testCompleteSSEFlow;
  console.log('🔧 SSE test functions available:');
  console.log('   - window.testSSE() - Quick test');
  console.log('   - window.testCompleteSSE() - Detailed test');
}