import { useEffect, useRef, useState } from 'react';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

export interface UseWebSocketOptions {
  userId: string;
  token: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private url: string;
  private options: UseWebSocketOptions;

  constructor(url: string, options: UseWebSocketOptions) {
    this.url = url;
    this.options = options;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.options.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.options.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.options.onDisconnect?.();
        
        // Attempt reconnection if not intentionally closed
        if (event.code !== 1000 && event.code !== 1001) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.options.onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  send(message: WebSocketMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  private scheduleReconnect() {
    const {
      reconnectInterval = 3000,
      maxReconnectAttempts = 5
    } = this.options;

    if (this.reconnectAttempts < maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${maxReconnectAttempts})`);
      
      this.reconnectTimer = setTimeout(() => {
        this.connect();
      }, reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  get readyState() {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export function useWebSocket(options: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const clientRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    if (!options.userId || !options.token) {
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${options.userId}?token=${options.token}`;
    
    clientRef.current = new WebSocketClient(wsUrl, {
      ...options,
      onConnect: () => {
        setIsConnected(true);
        options.onConnect?.();
      },
      onDisconnect: () => {
        setIsConnected(false);
        options.onDisconnect?.();
      },
      onMessage: (message) => {
        setLastMessage(message);
        options.onMessage?.(message);
      },
      onError: (error) => {
        setIsConnected(false);
        options.onError?.(error);
      },
    });

    clientRef.current.connect();

    return () => {
      clientRef.current?.disconnect();
    };
  }, [options.userId, options.token]);

  const sendMessage = (message: WebSocketMessage) => {
    clientRef.current?.send(message);
  };

  return {
    isConnected,
    lastMessage,
    sendMessage,
    client: clientRef.current,
  };
}