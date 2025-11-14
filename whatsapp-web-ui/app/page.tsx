'use client';

import { useEffect, useState } from 'react';
import QRCodeScanner from '@/components/QRCodeScanner';
import ChatInterface from '@/components/ChatInterface';
import { getConnectionStatus } from '@/lib/api';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await getConnectionStatus();
        setIsConnected(status.status === 'connected');
      } catch (error) {
        console.error('Failed to check connection:', error);
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkConnection();

    // Poll for connection status
    const interval = setInterval(checkConnection, 3000);

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Loading...</p>
        </div>
      </div>
    );
  }

  // Show QR scanner if not connected, otherwise show chat interface
  if (!isConnected) {
    return <QRCodeScanner />;
  }

  return <ChatInterface />;
}
