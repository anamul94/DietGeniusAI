import { useWebSocket as useBaseWebSocket } from '@/lib/websocket';

export function useWebSocket(userId: string, token: string, options: {
  onMessage?: (message: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}) {
  return useBaseWebSocket({
    userId,
    token,
    ...options,
  });
}