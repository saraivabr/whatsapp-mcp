'use client';

import { useEffect, useState } from 'react';
import { getQRCode, getConnectionStatus, connectWhatsAppStatusWebSocket, ConnectionStatus } from '@/lib/api';

export default function QRCodeScanner() {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let pollInterval: NodeJS.Timeout | null = null;

    // Initial status check
    const checkStatus = async () => {
      try {
        const statusData = await getConnectionStatus();
        setStatus(statusData);
        setLoading(false);

        // If QR code is needed but not available, try to get it
        if (statusData.status === 'qr_ready' && !statusData.qr_code) {
          const qrData = await getQRCode();
          if (qrData.qr_code) {
            setStatus({ ...statusData, qr_code: qrData.qr_code });
          }
        }
      } catch (err) {
        console.error('Failed to get status:', err);
        setError('Failed to connect to backend');
        setLoading(false);
      }
    };

    checkStatus();

    // Set up WebSocket for real-time updates
    try {
      ws = connectWhatsAppStatusWebSocket(
        (data) => {
          if (data.data) {
            try {
              const statusUpdate = JSON.parse(data.data);
              setStatus(statusUpdate);
            } catch (err) {
              console.error('Failed to parse status update:', err);
            }
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
          // Fall back to polling if WebSocket fails
          if (!pollInterval) {
            pollInterval = setInterval(checkStatus, 3000);
          }
        }
      );
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      // Fall back to polling
      pollInterval = setInterval(checkStatus, 3000);
    }

    // Cleanup
    return () => {
      if (ws) {
        ws.close();
      }
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Connecting to WhatsApp...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-red-50 to-orange-50 dark:from-gray-900 dark:to-gray-800">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md">
          <div className="text-red-600 dark:text-red-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-center mb-4 text-gray-800 dark:text-white">Connection Error</h2>
          <p className="text-center text-gray-600 dark:text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Show different UI based on status
  if (status?.status === 'connected') {
    return null; // Connection successful, main page will handle
  }

  if (status?.status === 'qr_ready' && status.qr_code) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-8 max-w-lg w-full">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-2">
              WhatsApp MCP
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Scan QR Code to Connect
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg mb-6 flex justify-center">
            <img
              src={status.qr_code}
              alt="WhatsApp QR Code"
              className="max-w-full h-auto"
              style={{ maxWidth: '300px' }}
            />
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
              How to scan:
            </h3>
            <ol className="text-sm text-blue-700 dark:text-blue-400 space-y-1 list-decimal list-inside">
              <li>Open WhatsApp on your phone</li>
              <li>Go to Settings → Linked Devices</li>
              <li>Tap "Link a Device"</li>
              <li>Point your phone at this screen to scan the code</li>
            </ol>
          </div>

          {status.message && (
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
              {status.message}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Default connecting state
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-300">
          {status?.message || 'Initializing...'}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Status: {status?.status || 'unknown'}
        </p>
      </div>
    </div>
  );
}
