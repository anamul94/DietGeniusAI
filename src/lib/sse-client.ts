/**
 * Server-Sent Events (SSE) client for streaming REST API endpoints
 */

export interface SSEMessage {
  type: string;
  data?: any;
  message?: string;
  progress?: number;
  timestamp?: string;
}

export interface SSEClientOptions {
  onMessage?: (message: SSEMessage) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  headers?: Record<string, string>;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private url: string;
  private options: SSEClientOptions;

  constructor(url: string, options: SSEClientOptions = {}) {
    this.url = url;
    this.options = options;
  }

  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    try {
      // For authenticated endpoints, add token to URL
      const token = localStorage.getItem('access_token');
      const urlWithAuth = token 
        ? `${this.url}${this.url.includes('?') ? '&' : '?'}token=${token}`
        : this.url;

      this.eventSource = new EventSource(urlWithAuth);

      this.eventSource.onopen = () => {
        this.options.onOpen?.();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.options.onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        this.options.onError?.(error);
      };

    } catch (error) {
      console.error('Failed to connect to SSE:', error);
      this.options.onError?.(error as Event);
    }
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.options.onClose?.();
    }
  }

  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

/**
 * React hook for SSE streaming
 */
import { useEffect, useRef, useState } from 'react';

export interface UseSSEOptions extends SSEClientOptions {
  autoConnect?: boolean;
}

export function useSSE(url: string, options: UseSSEOptions = {}) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<SSEClient | null>(null);

  useEffect(() => {
    const client = new SSEClient(url, {
      ...options,
      onMessage: (message) => {
        setMessages(prev => [...prev, message]);
        options.onMessage?.(message);
      },
      onOpen: () => {
        setIsConnected(true);
        setError(null);
        options.onOpen?.();
      },
      onError: (event) => {
        setError('Connection error');
        setIsConnected(false);
        options.onError?.(event);
      },
      onClose: () => {
        setIsConnected(false);
        options.onClose?.();
      },
    });

    clientRef.current = client;

    if (options.autoConnect !== false) {
      client.connect();
    }

    return () => {
      client.disconnect();
    };
  }, [url]);

  const connect = () => {
    clientRef.current?.connect();
  };

  const disconnect = () => {
    clientRef.current?.disconnect();
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    isConnected,
    error,
    connect,
    disconnect,
    clearMessages,
  };
}