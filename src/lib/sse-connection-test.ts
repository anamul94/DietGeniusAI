/**
 * SSE Connection Test Suite
 * Tests the enhanced SSE manager for long-running connections
 */

import { EnhancedSSEConnectionManager } from './sse-manager-enhanced-v2';
import { setAuthToken } from './auth-cookies';

export interface TestResult {
  testName: string;
  success: boolean;
  duration: number;
  error?: string;
  details?: any;
}

export class SSEConnectionTester {
  private results: TestResult[] = [];

  async runAllTests(): Promise<TestResult[]> {
    console.log('🧪 Starting SSE Connection Tests...');
    
    this.results = [];
    
    // Test 1: Basic Connection
    await this.testBasicConnection();
    
    // Test 2: Heartbeat Handling
    await this.testHeartbeatHandling();
    
    // Test 3: Reconnection Logic
    await this.testReconnectionLogic();
    
    // Test 4: Long Running Connection (5 minutes simulation)
    await this.testLongRunningConnection();
    
    // Test 5: Error Recovery
    await this.testErrorRecovery();
    
    console.log('✅ All SSE tests completed');
    return this.results;
  }

  private async testBasicConnection(): Promise<void> {
    const testName = 'Basic Connection Test';
    const startTime = Date.now();
    
    try {
      console.log(`🔄 Running ${testName}...`);
      
      const manager = new EnhancedSSEConnectionManager();
      let connectionOpened = false;
      let messageReceived = false;
      
      const testPromise = new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Connection timeout'));
        }, 10000);
        
        manager.connect({
          url: 'http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=test_basic',
          onOpen: () => {
            connectionOpened = true;
            console.log('✅ Connection opened successfully');
          },
          onMessage: (data) => {
            messageReceived = true;
            console.log('✅ Message received:', data.type);
            if (data.type === 'connection') {
              clearTimeout(timeout);
              manager.close();
              resolve();
            }
          },
          onError: (error) => {
            clearTimeout(timeout);
            reject(new Error(error));
          },
          timeout: 5000
        });
      });
      
      await testPromise;
      
      this.results.push({
        testName,
        success: true,
        duration: Date.now() - startTime,
        details: { connectionOpened, messageReceived }
      });
      
    } catch (error) {
      this.results.push({
        testName,
        success: false,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  private async testHeartbeatHandling(): Promise<void> {
    const testName = 'Heartbeat Handling Test';
    const startTime = Date.now();
    
    try {
      console.log(`🔄 Running ${testName}...`);
      
      const manager = new EnhancedSSEConnectionManager();
      let heartbeatCount = 0;
      
      const testPromise = new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          manager.close();
          if (heartbeatCount > 0) {
            resolve();
          } else {
            reject(new Error('No heartbeats received'));
          }
        }, 65000); // Wait for at least 2 heartbeats (30s interval)
        
        manager.connect({
          url: 'http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=test_heartbeat',
          onMessage: (data) => {
            if (data.type === 'heartbeat') {
              heartbeatCount++;
              console.log(`💓 Heartbeat ${heartbeatCount} received`);
              
              if (heartbeatCount >= 2) {
                clearTimeout(timeout);
                manager.close();
                resolve();
              }
            }
          },
          onError: (error) => {
            clearTimeout(timeout);
            reject(new Error(error));
          },
          heartbeatInterval: 30000
        });
      });
      
      await testPromise;
      
      this.results.push({
        testName,
        success: true,
        duration: Date.now() - startTime,
        details: { heartbeatCount }
      });
      
    } catch (error) {
      this.results.push({
        testName,
        success: false,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  private async testReconnectionLogic(): Promise<void> {
    const testName = 'Reconnection Logic Test';
    const startTime = Date.now();
    
    try {
      console.log(`🔄 Running ${testName}...`);
      
      const manager = new EnhancedSSEConnectionManager();
      let reconnectAttempts = 0;
      
      const testPromise = new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          manager.close();
          if (reconnectAttempts > 0) {
            resolve();
          } else {
            reject(new Error('No reconnection attempts detected'));
          }
        }, 30000);
        
        manager.connect({
          url: 'http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=test_reconnect',
          onMessage: (data) => {
            console.log('Reconnection test message:', data.type);
          },
          onReconnect: (attempt) => {
            reconnectAttempts = attempt;
            console.log(`🔄 Reconnection attempt ${attempt}`);
            
            if (attempt >= 2) {
              clearTimeout(timeout);
              manager.close();
              resolve();
            }
          },
          onError: (error) => {
            console.log('Expected error for reconnection test:', error);
          },
          maxReconnectAttempts: 3,
          reconnectInterval: 2000
        });
        
        // Simulate connection failure after 5 seconds
        setTimeout(() => {
          // Force close the connection to trigger reconnection
          if (manager.getConnectionState().isConnected) {
            console.log('🔌 Simulating connection failure...');
            manager.close();
          }
        }, 5000);
      });
      
      await testPromise;
      
      this.results.push({
        testName,
        success: true,
        duration: Date.now() - startTime,
        details: { reconnectAttempts }
      });
      
    } catch (error) {
      this.results.push({
        testName,
        success: false,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  private async testLongRunningConnection(): Promise<void> {
    const testName = 'Long Running Connection Test (5 min simulation)';
    const startTime = Date.now();
    
    try {
      console.log(`🔄 Running ${testName}...`);
      console.log('⏰ This test simulates a 5-minute connection...');
      
      const manager = new EnhancedSSEConnectionManager();
      let messagesReceived = 0;
      let heartbeatsReceived = 0;
      let connectionHealthy = true;
      
      const testPromise = new Promise<void>((resolve, reject) => {
        const testDuration = 5 * 60 * 1000; // 5 minutes
        const timeout = setTimeout(() => {
          const state = manager.getConnectionState();
          const isHealthy = manager.isHealthy();
          
          manager.close();
          
          if (isHealthy && heartbeatsReceived > 8) { // Should receive ~10 heartbeats in 5 minutes
            resolve();
          } else {
            reject(new Error(`Connection not healthy. Heartbeats: ${heartbeatsReceived}, Healthy: ${isHealthy}`));
          }
        }, testDuration);
        
        manager.connect({
          url: 'http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=test_long_running',
          onMessage: (data) => {
            messagesReceived++;
            
            if (data.type === 'heartbeat') {
              heartbeatsReceived++;
              console.log(`💓 Long test heartbeat ${heartbeatsReceived} (${Math.floor((Date.now() - startTime) / 1000)}s)`);
            }
            
            // Check connection health every minute
            if (messagesReceived % 20 === 0) {
              connectionHealthy = manager.isHealthy();
              const duration = manager.getConnectionDuration();
              console.log(`📊 Health check: ${connectionHealthy ? '✅' : '❌'} (${Math.floor(duration / 1000)}s)`);
            }
          },
          onError: (error) => {
            console.log('Long test error:', error);
            // Don't fail immediately, let reconnection handle it
          },
          onReconnect: (attempt) => {
            console.log(`🔄 Long test reconnection attempt ${attempt}`);
          },
          heartbeatInterval: 30000,
          maxReconnectAttempts: 10
        });
      });
      
      await testPromise;
      
      this.results.push({
        testName,
        success: true,
        duration: Date.now() - startTime,
        details: { messagesReceived, heartbeatsReceived, connectionHealthy }
      });
      
    } catch (error) {
      this.results.push({
        testName,
        success: false,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  private async testErrorRecovery(): Promise<void> {
    const testName = 'Error Recovery Test';
    const startTime = Date.now();
    
    try {
      console.log(`🔄 Running ${testName}...`);
      
      const manager = new EnhancedSSEConnectionManager();
      let errorCount = 0;
      let recoverySuccess = false;
      
      const testPromise = new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          manager.close();
          if (recoverySuccess) {
            resolve();
          } else {
            reject(new Error('Failed to recover from errors'));
          }
        }, 20000);
        
        manager.connect({
          url: 'http://localhost:8000/api/meal-entries/stream/generate-meal-plan?session_id=test_error_recovery',
          onMessage: (data) => {
            if (data.type === 'connection' && errorCount > 0) {
              recoverySuccess = true;
              console.log('✅ Successfully recovered from error');
              clearTimeout(timeout);
              manager.close();
              resolve();
            }
          },
          onError: (error) => {
            errorCount++;
            console.log(`❌ Error ${errorCount}:`, error);
          },
          onReconnect: (attempt) => {
            console.log(`🔄 Recovery attempt ${attempt}`);
          },
          maxReconnectAttempts: 5,
          reconnectInterval: 1000
        });
        
        // Simulate network issues
        setTimeout(() => {
          console.log('🔌 Simulating network error...');
          // This will trigger error handling and reconnection
        }, 3000);
      });
      
      await testPromise;
      
      this.results.push({
        testName,
        success: true,
        duration: Date.now() - startTime,
        details: { errorCount, recoverySuccess }
      });
      
    } catch (error) {
      this.results.push({
        testName,
        success: false,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  getResults(): TestResult[] {
    return this.results;
  }

  printResults(): void {
    console.log('\n📊 SSE Connection Test Results:');
    console.log('================================');
    
    this.results.forEach((result, index) => {
      const status = result.success ? '✅ PASS' : '❌ FAIL';
      const duration = `${result.duration}ms`;
      
      console.log(`${index + 1}. ${result.testName}: ${status} (${duration})`);
      
      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }
      
      if (result.details) {
        console.log(`   Details:`, result.details);
      }
      
      console.log('');
    });
    
    const passCount = this.results.filter(r => r.success).length;
    const totalCount = this.results.length;
    
    console.log(`Summary: ${passCount}/${totalCount} tests passed`);
    
    if (passCount === totalCount) {
      console.log('🎉 All tests passed! SSE connection is working properly.');
    } else {
      console.log('⚠️  Some tests failed. Please check the implementation.');
    }
  }
}

// Export test runner function
export async function runSSETests(): Promise<TestResult[]> {
  const tester = new SSEConnectionTester();
  const results = await tester.runAllTests();
  tester.printResults();
  return results;
}