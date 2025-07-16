'use client';

import { useState } from 'react';
import { WebSocketTest } from '@/components/WebSocketTest';

export default function WebSocketTestPage() {
  const [userId, setUserId] = useState('1');
  const [token, setToken] = useState('');
  const [isConfigured, setIsConfigured] = useState(false);

  const handleConfigure = () => {
    if (userId && token) {
      setIsConfigured(true);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">WebSocket Test</h1>
      
      {!isConfigured ? (
        <div className="max-w-md mx-auto">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">User ID</label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                placeholder="Enter user ID"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Token</label>
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                placeholder="Enter JWT token"
              />
            </div>
            
            <button
              onClick={handleConfigure}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded"
            >
              Connect WebSocket
            </button>
          </div>
        </div>
      ) : (
        <WebSocketTest userId={userId} token={token} />
      )}
    </div>
  );
}