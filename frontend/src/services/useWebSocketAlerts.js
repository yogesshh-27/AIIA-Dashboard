import { useState, useEffect, useRef, useCallback } from 'react';

function getWebSocketUrl() {
  const apiUrl = import.meta.env.VITE_API_URL || localStorage.getItem('ayurctms_active_api_url') || '';
  if (apiUrl && !apiUrl.includes('workers.dev')) {
    const wsProto = apiUrl.startsWith('https') ? 'wss:' : 'ws:';
    const cleanHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/.*$/, '');
    return `${wsProto}//${cleanHost}/ws/alerts`;
  }
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'ws://127.0.0.1:8000/ws/alerts';
  }
  return 'wss://aiia-dashboard.onrender.com/ws/alerts';
}

export function useWebSocketAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [latestAlert, setLatestAlert] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);

  const connect = useCallback(() => {
    try {
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      if (retryCountRef.current < 2) {
        setConnectionStatus('connecting');
      }

      ws.onopen = () => {
        retryCountRef.current = 0;
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
        } catch {
          // Ignore ping/pong
        }
      };

      ws.onclose = () => {
        retryCountRef.current += 1;
        if (retryCountRef.current >= 2) {
          // Switch gracefully to local standby mode
          setConnectionStatus('standby');
        } else {
          setConnectionStatus('connecting');
        }

        // Try reconnecting with exponential backoff (max 30s)
        const delay = Math.min(30000, 4000 * Math.pow(1.5, retryCountRef.current));
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };

      ws.onerror = () => {
        if (retryCountRef.current >= 2) {
          setConnectionStatus('standby');
        }
        ws.close();
      };
    } catch {
      setConnectionStatus('standby');
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
