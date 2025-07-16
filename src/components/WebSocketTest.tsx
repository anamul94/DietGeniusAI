'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface WebSocketTestProps {
  userId: string;
  token: string;
}

export function WebSocketTest({ userId, token }: WebSocketTestProps) {
  const [messages, setMessages] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');

  const { isConnected, lastMessage, sendMessage } = useWebSocket(
    userId,
    token,
    {
      onConnect: () => {
        console.log('Connected to WebSocket');
      },
      onDisconnect: () => {
        console.log('Disconnected from WebSocket');
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
      },
      onMessage: (message) => {
        console.log('Received message:', message);
        setMessages(prev => [...prev, JSON.stringify(message)]);
      },
    }
  );

  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [...prev, JSON.stringify(lastMessage)]);
    }
  }, [lastMessage]);

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      sendMessage({
        type: 'chat',
        data: inputMessage,
        timestamp: new Date().toISOString(),
      });
      setInputMessage('');
    }
  };

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold mb-2">WebSocket Test</h3>
      
      <div className="mb-4">
        <span className={`inline-block px-2 py-1 rounded text-sm ${
          isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type a message..."
            className="flex-1 px-3 py-2 border rounded"
            disabled={!isConnected}
          />
          <button
            onClick={handleSendMessage}
            disabled={!isConnected || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>

      <div className="border rounded p-2 h-48 overflow-y-auto">
        <h4 className="text-sm font-semibold mb-2">Messages:</h4>
        {messages.length === 0 ? (
          <p className="text-gray-500 text-sm">No messages yet</p>
        ) : (
          <div className="space-y-1">
            {messages.map((msg, index) => (
              <div key={index} className="text-xs bg-gray-100 p-1 rounded">
                {msg}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}