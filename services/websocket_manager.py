"""
WebSocket Connection Manager for Real-Time Safety & Clinical Alerts.
Broadcasts instant Serious Adverse Event (SAE) notifications to connected dashboards.
"""

import json
from typing import List, Dict, Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, alert_type: str, data: Dict[str, Any]):
        """Broadcasts an alert payload to all connected WebSocket clients."""
        payload = json.dumps({
            "type": alert_type,
            "timestamp": data.get("timestamp"),
            "data": data
        })
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected.append(connection)
        for dead_conn in disconnected:
            self.disconnect(dead_conn)


ws_manager = ConnectionManager()
