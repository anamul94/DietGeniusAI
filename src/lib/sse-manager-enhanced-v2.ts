/**
 * Enhanced SSE Connection Manager with Heartbeat, Reconnection, and Long-Running Support
 * Fixes timeout issues for connections lasting 45+ minutes
 */

import { getAuthToken } from './auth-cookies';

export interface SSEConnectionOptions {
  url: string;
  onMessage: (data: any) => void;
  onError: (error: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onReconnect?: (attempt: number) => void;
  timeout?: number;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

export interface ConnectionState {
  isConnected: boolean;
  hasAttempted: boolean;
  reconnectAttempts: number;
  lastHeartbeat: number;
  connectionStartTime: number;
}

export class EnhancedSSEConnectionManager {
  private eventSource: EventSource | null = null;
  private isConnected = false;
  private hasAttemptedConnection = false;
  private timeoutId: NodeJS.Timeout | null = null;
  private heartbeatId: NodeJS.Timeout | null = null;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000; // Start with 5 seconds
  private heartbeatInterval = 30000; // 30 seconds
  private lastHeartbeat = 0;
  private connectionStartTime = 0;
  private options: SSEConnectionOptions | null = null;
  private isManuallyDisconnected = false;

  async connect(options: SSEConnectionOptions): Promise<boolean> {
    // Store options for reconnection
    this.options = options;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.heartbeatInterval = options.heartbeatInterval || 30000;
    this.isManuallyDisconnected = false;

    // Prevent redundant connections
    if (this.hasAttemptedConnection && !this.isConnected && this.reconnectAttempts === 0) {
      options.onError('Connection already attempted. Please retry manually.');
      return false;
    }

    if (this.isConnected) {
      options.onError('Already connected. Close existing connection first.');
      return false;
    }

    this.hasAttemptedConnection = true;
    this.connectionStartTime = Date.now();

    // Check server health first
    const isServerAvailable = await this.checkServerHealth(options.url);
    if (!isServerAvailable) {
      const errorMsg = 'Backend server is not running. Please start the server on localhost:8000 and try again.';
      options.onError(errorMsg);
      this.resetConnectionState();
      return false;
    }

    return this.establishConnection(options);
  }

  private async establishConnection(options: SSEConnectionOptions): Promise<boolean> {
    try {
      // Build URL with authentication
      const url = new URL(options.url);
      url.searchParams.delete('token'); // Remove token from URL if present
      
      // Get token from cookies and add as query parameter
      const token = getAuthToken();
      if (token) {
        url.searchParams.set('token', token);
      }
      
      console.log(`[SSE] Establishing connection (attempt ${this.reconnectAttempts + 1}):`, 
                  url.toString().substring(0, 100) + '...');
      
      // Create EventSource
      this.eventSource = new EventSource(url.toString());
      
      // Set connection timeout
      this.timeoutId = setTimeout(() => {
        if (!this.isConnected) {
          this.handleConnectionTimeout(options);
        }
      }, options.timeout || 30000);

      // Setup event handlers
      this.setupEventHandlers(options);

      return true;
    } catch (error) {
      console.error('[SSE] Failed to create EventSource:', error);
      options.onError('Failed to establish connection. Please try again.');
      this.resetConnectionState();
      return false;
    }
  }

  private setupEventHandlers(options: SSEConnectionOptions): void {
    if (!this.eventSource) return;

    this.eventSource.onopen = (event) => {
      console.log('[SSE] Connection opened:', event);
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.lastHeartbeat = Date.now();
      
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
        this.timeoutId = null;
      }
      
      // Start heartbeat monitoring
      this.startHeartbeatMonitoring();
      
      options.onOpen?.();
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle heartbeat messages
        if (data.type === 'heartbeat') {
          this.lastHeartbeat = Date.now();
          console.log('[SSE] Heartbeat received');
          return;
        }
        
        // Update last heartbeat for any message
        this.lastHeartbeat = Date.now();
        options.onMessage(data);
      } catch (error) {
        console.error('[SSE] Failed to parse message:', error, 'Raw data:', event.data);
        options.onError('Invalid server response format');
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error);
      console.log('[SSE] EventSource readyState:', this.eventSource?.readyState);
      console.log('[SSE] EventSource URL:', this.eventSource?.url);
      
      this.handleConnectionError(options, error);
    };
  }

  private handleConnectionTimeout(options: SSEConnectionOptions): void {
    console.error('[SSE] Connection timeout');
    this.close();
    
    if (!this.isManuallyDisconnected && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.scheduleReconnection(options, 'Connection timeout');
    } else {
      options.onError('Connection timeout. Server not responding.');
      this.resetConnectionState();
    }
  }

  private handleConnectionError(options: SSEConnectionOptions, error: Event): void {
    const wasConnected = this.isConnected;
    this.close();
    
    // Don't attempt reconnection if manually disconnected
    if (this.isManuallyDisconnected) {
      return;
    }
    
    // Provide specific error messages
    let errorMessage = 'Connection failed. ';
    if (this.eventSource?.readyState === EventSource.CLOSED) {
      errorMessage += 'Connection was closed by the server.';
    } else if (this.eventSource?.readyState === EventSource.CONNECTING) {
      errorMessage += 'Unable to establish connection.';
    } else {
      errorMessage += 'Please check if the server is running.';
    }
    
    // Attempt reconnection if we were previously connected or haven't exceeded max attempts
    if ((wasConnected || this.reconnectAttempts === 0) && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.scheduleReconnection(options, errorMessage);
    } else {
      options.onError(errorMessage);
      this.resetConnectionState();
    }
  }

  private scheduleReconnection(options: SSEConnectionOptions, reason: string): void {
    this.reconnectAttempts++;
    
    // Exponential backoff with jitter
    const baseDelay = Math.min(this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1), 30000);
    const jitter = Math.random() * 1000;
    const delay = baseDelay + jitter;
    
    console.log(`[SSE] Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${Math.round(delay)}ms. Reason: ${reason}`);
    
    options.onReconnect?.(this.reconnectAttempts);
    
    this.reconnectTimeoutId = setTimeout(() => {
      if (!this.isManuallyDisconnected) {
        console.log(`[SSE] Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.establishConnection(options);
      }
    }, delay);
  }

  private startHeartbeatMonitoring(): void {
    this.stopHeartbeatMonitoring();
    
    this.heartbeatId = setInterval(() => {
      const now = Date.now();
      const timeSinceLastHeartbeat = now - this.lastHeartbeat;
      
      // If no heartbeat for 2x the heartbeat interval, consider connection stale
      if (timeSinceLastHeartbeat > this.heartbeatInterval * 2) {
        console.warn(`[SSE] No heartbeat for ${timeSinceLastHeartbeat}ms, connection may be stale`);
        
        // Force reconnection if connection seems dead
        if (this.options && !this.isManuallyDisconnected) {
          console.log('[SSE] Forcing reconnection due to stale connection');
          this.handleConnectionError(this.options, new Event('heartbeat_timeout'));
        }
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeatMonitoring(): void {
    if (this.heartbeatId) {
      clearInterval(this.heartbeatId);
      this.heartbeatId = null;
    }
  }

  close(): void {
    this.isManuallyDisconnected = true;
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    this.clearAllTimeouts();
    this.stopHeartbeatMonitoring();
    this.isConnected = false;
  }

  reset(): void {
    this.close();
    this.resetConnectionState();
  }

  private resetConnectionState(): void {
    this.hasAttemptedConnection = false;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.lastHeartbeat = 0;
    this.connectionStartTime = 0;
    this.isManuallyDisconnected = false;
  }

  private clearAllTimeouts(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }

  private async checkServerHealth(baseUrl: string): Promise<boolean> {
    try {
      const url = new URL(baseUrl);
      const healthUrl = `${url.protocol}//${url.host}/health`;
      
      const response = await fetch(healthUrl, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      
      return response.ok;
    } catch (error) {
      console.error('[SSE] Server health check failed:', error);
      return false;
    }
  }

  getConnectionState(): ConnectionState {
    return {
      isConnected: this.isConnected,
      hasAttempted: this.hasAttemptedConnection,
      reconnectAttempts: this.reconnectAttempts,
      lastHeartbeat: this.lastHeartbeat,
      connectionStartTime: this.connectionStartTime
    };
  }

  getConnectionDuration(): number {
    return this.connectionStartTime > 0 ? Date.now() - this.connectionStartTime : 0;
  }

  isHealthy(): boolean {
    if (!this.isConnected) return false;
    
    const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;
    return timeSinceLastHeartbeat < this.heartbeatInterval * 2;
  }
}

// Global instance for tracking connection attempts
const globalEnhancedSSEManager = new EnhancedSSEConnectionManager();

export function useEnhancedSSEConnection() {
  return globalEnhancedSSEManager;
}

// Export as default for easy replacement
export default EnhancedSSEConnectionManager;