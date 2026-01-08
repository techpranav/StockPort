"""
WebSocket Server

Real-time WebSocket server for UI updates.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from utils.debug_utils import DebugUtils
from backend.core.event_bus import EventBus
from backend.settings import get_settings_manager


class WebSocketServer:
    """
    WebSocket server for real-time UI updates.
    
    Features:
    - Real-time state updates
    - Event broadcasting
    - Client management
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize WebSocket server.
        
        Args:
            event_bus: Event bus instance
        """
        self.event_bus = event_bus or EventBus()
        self.app = FastAPI()
        self.active_connections: List[WebSocket] = []
        self.settings_manager = get_settings_manager()
        
        # Subscribe to settings changes for real-time updates
        self.settings_manager.subscribe("*", self._on_setting_changed)
        
        # Setup routes
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/")(self.get_home)
    
    async def websocket_endpoint(self, websocket: WebSocket):
        """
        WebSocket endpoint handler.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        DebugUtils.info("WebSocket client connected")
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client message
                await self.handle_client_message(websocket, message)
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
            DebugUtils.info("WebSocket client disconnected")
    
    async def handle_client_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Handle message from client.
        
        Args:
            websocket: WebSocket connection
            message: Message dictionary
        """
        message_type = message.get('type')
        
        if message_type == 'subscribe':
            # Subscribe to events
            channel = message.get('channel')
            # Would implement subscription logic
            await websocket.send_text(json.dumps({
                'type': 'subscribed',
                'channel': channel
            }))
        elif message_type == 'get_settings':
            # Send current settings
            settings = self.settings_manager.get_all()
            await websocket.send_text(json.dumps({
                'type': 'settings',
                'settings': settings
            }))
        elif message_type == 'ping':
            # Respond to ping
            await websocket.send_text(json.dumps({'type': 'pong'}))
    
    def _on_setting_changed(self, key: str, old_value: Any, new_value: Any):
        """
        Handle setting change and broadcast to clients.
        
        Args:
            key: Setting key
            old_value: Old value
            new_value: New value
        """
        asyncio.create_task(self.broadcast({
            'type': 'setting_changed',
            'key': key,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def broadcast(self, data: Dict[str, Any]):
        """
        Broadcast message to all connected clients.
        
        Args:
            data: Data dictionary to broadcast
        """
        message = json.dumps(data, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                DebugUtils.log_error(e, "Error broadcasting to WebSocket client")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    async def get_home(self):
        """Get home page (for testing)."""
        return HTMLResponse("""
        <html>
            <head>
                <title>Stockport v4 WebSocket Server</title>
            </head>
            <body>
                <h1>Stockport v4 WebSocket Server</h1>
                <p>WebSocket endpoint: ws://localhost:8000/ws</p>
            </body>
        </html>
        """)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run WebSocket server.
        
        Args:
            host: Host address
            port: Port number
        """
        import uvicorn
        DebugUtils.info(f"Starting WebSocket server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

