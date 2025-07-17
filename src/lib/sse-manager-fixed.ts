/**
 * Fixed SSE connection manager with proper cookie-based authentication
 * Addresses the EventSource withCredentials limitation
 */

import { getAuthToken } from './auth-cookies';

export interface SSEConnectionOptions {
  url: string;
  onMessage: (data: any) => void;
  onError: (error: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  timeout?: number;
}

export class FixedSSEConnectionManager {
  private eventSource: EventSource | null = null;
  private isConnected = false;
  private hasAttemptedConnection = false;
  private timeoutId: NodeJS.Timeout | null = null;

  async connect(options: SSEConnectionOptions): Promise<boolean> {
    // Prevent redundant connections
    if (this.hasAttemptedConnection && !this.isConnected) {
      options.onError('Connection already attempted. Please retry manually.');
      return false;
    }

    if (this.isConnected) {
      options.onError('Already connected. Close existing connection first.');
      return false;
    }

    this.hasAttemptedConnection = true;

    // Check server health first
    const isServerAvailable = await this.checkServerHealth(options.url);
    if (!isServerAvailable) {
      const errorMsg = 'Backend server is not running. Please start the server on localhost:8000 and try again.';
      options.onError(errorMsg);
      this.resetConnectionState();
      return false;
    }

    try {
      // Build URL without token parameter and include session_id only
      const url = new URL(options.url);
      url.searchParams.delete('token'); // Remove token from URL if present
      
      // Get token from cookies and add as query parameter as fallback
      const token = getAuthToken();
      if (token) {
        // For EventSource, we need to pass token in URL since cookies might not work
        url.searchParams.set('token', token);
      }
      
      console.log('Connecting to SSE URL:', url.toString().substring(0, 100) + '...');
      
      // Create EventSource - standard constructor without withCredentials
      this.eventSource = new EventSource(url.toString());
      
      // Set connection timeout
      this.timeoutId = setTimeout(() => {
        if (!this.isConnected) {
          this.close();
          options.onError('Connection timeout. Server not responding after 15 seconds.');
          this.resetConnectionState();
        }
      }, options.timeout || 15000);

      this.eventSource.onopen = (event) => {
        console.log('SSE connection opened:', event);
        this.isConnected = true;
        clearTimeout(this.timeoutId!);
        options.onOpen?.();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          options.onMessage(data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error, 'Raw data:', event.data);
          options.onError('Invalid server response format');
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        console.log('EventSource readyState:', this.eventSource?.readyState);
        console.log('EventSource URL:', this.eventSource?.url);
        
        this.close();
        
        // Provide more specific error messages based on readyState
        let errorMessage = 'Connection failed. ';
        if (this.eventSource?.readyState === EventSource.CLOSED) {
          errorMessage += 'Connection was closed by the server. Check authentication.';
        } else if (this.eventSource?.readyState === EventSource.CONNECTING) {
          errorMessage += 'Unable to establish connection. Check server status.';
        } else {
          errorMessage += 'Please check if the server is running and try again.';
        }
        
        options.onError(errorMessage);
        this.resetConnectionState();
      };

      return true;
    } catch (error) {
      console.error('Failed to create EventSource:', error);
      options.onError('Failed to establish connection. Please try again.');
      this.resetConnectionState();
      return false;
    }
  }

  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    this.isConnected = false;
  }

  reset(): void {
    this.close();
    this.resetConnectionState();
  }

  private resetConnectionState(): void {
    this.hasAttemptedConnection = false;
    this.isConnected = false;
  }

  private async checkServerHealth(baseUrl: string): Promise<boolean> {
    try {
      // Extract base URL without query parameters
      const url = new URL(baseUrl);
      const healthUrl = `${url.protocol}//${url.host}/health`;
      
      const response = await fetch(healthUrl, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache'
      });
      
      return response.ok;
    } catch (error) {
      console.error('Server health check failed:', error);
      return false;
    }
  }

  getConnectionState(): { isConnected: boolean; hasAttempted: boolean } {
    return {
      isConnected: this.isConnected,
      hasAttempted: this.hasAttemptedConnection
    };
  }
}

// Global instance for tracking connection attempts
const globalFixedSSEManager = new FixedSSEConnectionManager();

export function useFixedSSEConnection() {
  return globalFixedSSEManager;
}

// Export as default for easy replacement
export default FixedSSEConnectionManager;