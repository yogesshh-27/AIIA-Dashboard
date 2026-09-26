import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocketAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [latestAlert, setLatestAlert] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host || 'localhost:8000';
      const wsUrl = `${protocol}//${host}/ws/alerts`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      setConnectionStatus('connecting');

      ws.onopen = () => {
        setConnectionStatus('connected');
        // Heartbeat ping every 25 seconds
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          } else {
            clearInterval(pingInterval);
          }
        }, 25000);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'SAE_DETECTED') {
            const newAlert = {
              id: Date.now() + Math.random(),
              ...payload.data,
              receivedAt: new Date().toLocaleTimeString(),
            };
            setAlerts((prev) => [newAlert, ...prev.slice(0, 19)]);
            setLatestAlert(newAlert);
          }
        } catch (e) {
          // Non-JSON message (e.g. pong)
        }
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        // Auto-reconnect after 4s
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 4000);
      };

      ws.onerror = () => {
        setConnectionStatus('disconnected');
        ws.close();
      };
    } catch (err) {
      setConnectionStatus('disconnected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  const dismissLatest = () => {
    setLatestAlert(null);
  };

  const dismissAlert = (id) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
    if (latestAlert && latestAlert.id === id) {
      setLatestAlert(null);
    }
  };

  return {
    alerts,
    latestAlert,
    connectionStatus,
    dismissLatest,
    dismissAlert,
  };
}
