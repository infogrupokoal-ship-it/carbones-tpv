from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
from ..utils.logger import logger

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket Client Connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket Client Disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/orders")
async def websocket_orders_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time order updates to the KDS (Kitchen Display System).
    Clients connect here and listen for new order events.
    """
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client in this use case,
            # but we keep the connection open and listen for close.
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def notify_new_order(order_data: dict):
    """
    Helper function to be called when a new order is created.
    """
    try:
        message = json.dumps({"type": "NEW_ORDER", "data": order_data})
        await manager.broadcast(message)
    except Exception as e:
        logger.error(f"Failed to notify new order via WS: {e}")
