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
  const [connectionStatus, setConnectionStatus] = useState('standby');
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const connectTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);

  const connect = useCallback(() => {
    try {
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      // Fast timeout: If WebSocket does not connect in 1.5s, gracefully switch to standby
      if (connectTimeoutRef.current) clearTimeout(connectTimeoutRef.current);
      connectTimeoutRef.current = setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          try { ws.close(); } catch {}
          setConnectionStatus('standby');
        }
      }, 1500);

      ws.onopen = () => {
        if (connectTimeoutRef.current) clearTimeout(connectTimeoutRef.current);
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
        if (connectTimeoutRef.current) clearTimeout(connectTimeoutRef.current);
        setConnectionStatus('standby');
        retryCountRef.current += 1;

        // Try reconnecting in background with backoff without showing UI error
        const delay = Math.min(30000, 5000 * Math.pow(1.5, Math.min(retryCountRef.current, 4)));
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };

      ws.onerror = () => {
        if (connectTimeoutRef.current) clearTimeout(connectTimeoutRef.current);
        setConnectionStatus('standby');
        try { ws.close(); } catch {}
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
