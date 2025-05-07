import asyncio
import websockets

from .exceptions import LightspeedConnectionError
from .models import OrderSingle


class LightspeedClient:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.ws = None
        self.connected = False

    async def connect(self):
        """Connect to the Lightspeed WebSocket API."""
        try:
            self.ws = await websockets.connect(
                self.url, extra_headers={"Authorization": f"Bearer {self.api_key}"}
            )
            self.connected = True
            print("✅ WebSocket connection opened.")
            # Start message handler
            asyncio.create_task(self._message_handler())
        except Exception as e:
            raise LightspeedConnectionError(f"Failed to connect: {str(e)}")

    async def _message_handler(self):
        """Handle incoming messages."""
        try:
            async for message in self.ws:
                print(f"📩 Message received: {message}")
        except websockets.ConnectionClosed:
            self.connected = False
            print("❌ WebSocket connection closed.")
        except Exception as e:
            self.connected = False
            raise LightspeedConnectionError(f"Message handler error: {str(e)}")

    async def send_order(self, order: OrderSingle):
        """Send an order to the Lightspeed API."""
        if not self.connected:
            raise LightspeedConnectionError("WebSocket not connected.")
        try:
            await self.ws.send(order.to_json())
        except Exception as e:
            raise LightspeedConnectionError(f"Failed to send order: {str(e)}")

    async def close(self):
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.connected = False
