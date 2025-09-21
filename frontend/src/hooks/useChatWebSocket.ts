import { useEffect, useRef, useState, useCallback } from 'react';
import { chatApi } from '@/lib/api';

export interface WebSocketMessage {
  type: string;
  payload?: any;
  timestamp: string;
  [key: string]: any;
}

export interface ChatWebSocketHookOptions {
  sessionId: string;
  onMessage?: (message: WebSocketMessage) => void;
  onUserJoined?: (userId: string) => void;
  onUserLeft?: (userId: string) => void;
  onTypingUpdate?: (userId: string, isTyping: boolean) => void;
  onAIResponse?: (content: string, metadata?: any) => void;
  onError?: (error: string) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface ChatWebSocketHook {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  activeUsers: string[];
  typingUsers: string[];
  sendMessage: (content: string, jurisdiction?: string) => void;
  sendTypingIndicator: (isTyping: boolean) => void;
  updateJurisdiction: (jurisdiction: string, confidence?: number) => void;
  requestContext: () => void;
  reconnect: () => void;
  disconnect: () => void;
}

export function useChatWebSocket(options: ChatWebSocketHookOptions): ChatWebSocketHook {
  const {
    sessionId,
    onMessage,
    onUserJoined,
    onUserLeft,
    onTypingUpdate,
    onAIResponse,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeUsers, setActiveUsers] = useState<string[]>([]);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualDisconnectRef = useRef(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setError(null);
    isManualDisconnectRef.current = false;

    try {
      const ws = chatApi.createWebSocketConnection(sessionId);
      
      if (!ws) {
        throw new Error('Failed to create WebSocket connection');
      }

      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        console.log(`WebSocket connected to session ${sessionId}`);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle different message types
          switch (message.type) {
            case 'session_joined':
              setActiveUsers(message.active_users || []);
              setTypingUsers(message.typing_users || []);
              break;
              
            case 'user_joined':
              if (message.user_id) {
                setActiveUsers(prev => [...prev, message.user_id]);
                onUserJoined?.(message.user_id);
              }
              break;
              
            case 'user_left':
              if (message.user_id) {
                setActiveUsers(prev => prev.filter(id => id !== message.user_id));
                setTypingUsers(prev => prev.filter(id => id !== message.user_id));
                onUserLeft?.(message.user_id);
              }
              break;
              
            case 'typing_update':
              if (message.user_id) {
                if (message.is_typing) {
                  setTypingUsers(prev => [...prev.filter(id => id !== message.user_id), message.user_id]);
                } else {
                  setTypingUsers(prev => prev.filter(id => id !== message.user_id));
                }
                onTypingUpdate?.(message.user_id, message.is_typing);
              }
              break;
              
            case 'ai_typing':
              if (message.is_typing) {
                setTypingUsers(prev => [...prev.filter(id => id !== 'ai'), 'ai']);
              } else {
                setTypingUsers(prev => prev.filter(id => id !== 'ai'));
              }
              break;
              
            case 'ai_message':
              setTypingUsers(prev => prev.filter(id => id !== 'ai'));
              onAIResponse?.(message.content, message.metadata);
              break;
              
            case 'session_context':
              setActiveUsers(message.active_users || []);
              setTypingUsers(message.typing_users || []);
              break;
              
            case 'error':
              setError(message.error || 'Unknown error');
              onError?.(message.error || 'Unknown error');
              break;
              
            default:
              // Pass through other message types
              break;
          }
          
          // Call general message handler
          onMessage?.(message);
          
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          setError('Failed to parse message');
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setIsConnecting(false);
        
        if (!isManualDisconnectRef.current) {
          console.log(`WebSocket disconnected from session ${sessionId}:`, event.code, event.reason);
          
          // Attempt to reconnect if enabled
          if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            setError(`Connection lost. Reconnecting... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
          } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
            setError('Connection failed after maximum retry attempts');
          }
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setIsConnecting(false);
      };

    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create connection');
      setIsConnecting(false);
    }
  }, [sessionId, autoReconnect, reconnectInterval, maxReconnectAttempts, onMessage, onUserJoined, onUserLeft, onTypingUpdate, onAIResponse, onError]);

  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
    setError(null);
    setActiveUsers([]);
    setTypingUsers([]);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  const sendMessage = useCallback((content: string, jurisdiction?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        content,
        jurisdiction,
        timestamp: new Date().toISOString()
      }));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping,
        timestamp: new Date().toISOString()
      }));
    }
  }, []);

  const updateJurisdiction = useCallback((jurisdiction: string, confidence = 1.0) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'jurisdiction_update',
        jurisdiction,
        confidence,
        timestamp: new Date().toISOString()
      }));
    }
  }, []);

  const requestContext = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'request_context',
        timestamp: new Date().toISOString()
      }));
    }
  }, []);

  // Connect on mount and when sessionId changes
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [sessionId]); // Only depend on sessionId to avoid reconnecting on every render

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    isConnecting,
    error,
    activeUsers,
    typingUsers,
    sendMessage,
    sendTypingIndicator,
    updateJurisdiction,
    requestContext,
    reconnect,
    disconnect
  };
}