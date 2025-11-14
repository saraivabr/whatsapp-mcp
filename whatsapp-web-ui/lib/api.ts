/**
 * API client for communicating with the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ConnectionStatus {
  status: string;
  qr_code?: string;
  message?: string;
  timestamp: number;
}

export interface QRCodeResponse {
  success: boolean;
  status: string;
  qr_code?: string;
  message?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  success: boolean;
  tool_calls?: any[];
}

/**
 * Get QR code from backend
 */
export async function getQRCode(): Promise<QRCodeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/qrcode`);
  if (!response.ok) {
    throw new Error(`Failed to get QR code: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get WhatsApp connection status
 */
export async function getConnectionStatus(): Promise<ConnectionStatus> {
  const response = await fetch(`${API_BASE_URL}/api/connection-status`);
  if (!response.ok) {
    throw new Error(`Failed to get status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Send a chat message
 */
export async function sendChatMessage(
  message: string,
  history?: ChatMessage[]
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create WebSocket connection for WhatsApp status updates
 */
export function connectWhatsAppStatusWebSocket(
  onMessage: (data: any) => void,
  onError?: (error: Event) => void
): WebSocket {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/ws/whatsapp-status`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };

  return ws;
}

/**
 * Create WebSocket connection for chat
 */
export function connectChatWebSocket(
  onChunk: (chunk: string) => void,
  onEnd: () => void,
  onError?: (error: string) => void
): WebSocket {
  const wsUrl = API_BASE_URL.replace('http', 'ws');
  const ws = new WebSocket(`${wsUrl}/ws/chat`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === 'chunk') {
        onChunk(data.content);
      } else if (data.type === 'end') {
        onEnd();
      } else if (data.type === 'error') {
        if (onError) onError(data.message);
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError('WebSocket connection error');
  };

  ws.onclose = () => {
    console.log('Chat WebSocket connection closed');
  };

  return ws;
}

/**
 * Send message via WebSocket
 */
export function sendWebSocketMessage(
  ws: WebSocket,
  message: string,
  history?: ChatMessage[]
): void {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ message, history }));
  } else {
    throw new Error('WebSocket is not connected');
  }
}
