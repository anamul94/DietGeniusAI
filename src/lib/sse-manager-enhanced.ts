/**
 * Enhanced SSE connection manager with cookie-based authentication
 * Solves the URL length limitation issue with JWT tokens
 */

import { getAuthToken } from './auth-cookies';

export interface SSEConnectionOptions {
  url: string;
  onMessage: (data: any) => void;
  onError: (error: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  timeout?: number;
  withCredentials?: boolean;
}

export class EnhancedSSEConnectionManager {
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
      // Build URL without token parameter
      const url = new URL(options.url);
      url.searchParams.delete('token'); // Remove token from URL if present
      
      // Use EventSource with credentials to send cookies
      this.eventSource = new EventSource(url.toString(), {
        withCredentials: options.withCredentials !== false
      });
      
      // Set connection timeout
      this.timeoutId = setTimeout(() => {
        if (!this.isConnected) {
          this.close();
          options.onError('Connection timeout. Server not responding.');
          this.resetConnectionState();
        }
      }, options.timeout || 10000); // Increased timeout for cookie auth

      this.eventSource.onopen = () => {
        this.isConnected = true;
        clearTimeout(this.timeoutId!);
        options.onOpen?.();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          options.onMessage(data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
          options.onError('Invalid server response format');
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        this.close();
        
        // Provide more specific error messages
        let errorMessage = 'Connection failed. ';
        if (error && (error as any).target) {
          const readyState = (error as any).target.readyState;
          if (readyState === EventSource.CLOSED) {
            errorMessage += 'Connection was closed by the server.';
          } else if (readyState === EventSource.CONNECTING) {
            errorMessage += 'Unable to establish connection.';
          }
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
        cache: 'no-cache',
        credentials: 'include' // Include cookies in health check
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
const globalEnhancedSSEManager = new EnhancedSSEConnectionManager();

export function useEnhancedSSEConnection() {
  return globalEnhancedSSEManager;
}

// Backward compatibility - use enhanced version as default
export const useSSEConnection = useEnhancedSSEConnection;