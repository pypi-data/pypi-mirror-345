import asyncio
import json
import time
import websockets
from typing import Callable, Awaitable
from botato.intents import Intents

from loguru import logger

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"


class GatewayConnection:
    """
    Handles connection to the Discord WebSocket Gateway.
    
    Responsible for:
    - Establishing and maintaining the WebSocket connection
    - Heartbeating
    - Receiving and parsing events
    """
    
    def __init__(self, 
                 token: str, 
                 event_callback: Callable[[str, dict], Awaitable[None]],
                 intents: Intents
    ) -> None:
        """
        Initialize the GatewayConnection.

        Args:
            token (str): Bot token for authentication.
            event_callback (Callable[[str, dict], Awaitable[None]]): Function to call with every event received.
            intents (Intents): Intents for the bot.
        """
        self.token = token
        self.event_callback = event_callback
        self.intents = intents
        
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._heartbeat_interval: float = 0
        self._last_heartbeat_ack: bool = True
        self._sequence: int | None = None
        self._session_id: str | None = None
        
        self._heartbeat_task: asyncio.Task | None = None
        
    async def connect(self) -> None:
        """
        Establish the WebSocket connection to Discord Gateway.
        """
        logger.info("Connecting to Discord Gateway...")
        
        self._ws = await websockets.connect(
            GATEWAY_URL,
            open_timeout=20,
            close_timeout=5,
            additional_headers=[
                ("User-Agent", "Botato (https://github.com/shivkun/botato, 0.1.0)")
            ]
        )
        
        async for message in self._ws:
            await self._handle_message(message)
            
    async def _send_json(self, payload: dict) -> None:
        """
        Send a JSON payload to the Gateway.

        Args:
            payload (dict): The data to send.
        """
        if self._ws:
            await self._ws.send(json.dumps(payload))
            
    async def _handle_message(self, raw_data: str) -> None:
        """
        Handle a single incoming message from the WebSocket.

        Args:
            raw_data (str): Raw JSON string.
        """
        data = json.loads(raw_data)
        op = data.get("op")
        t = data.get("t")
        d = data.get("d")
        s = data.get("s")
        
        if s is not None:
            self._sequence = s
            
        match op:
            case 10: # Hello
                self._heartbeat_interval = d["heartbeat_interval"] / 1000
                await self._identify()
                self._heartbeat_task = asyncio.create_task(self._start_heartbeating())
                
            case 11: # Heartbeat ACK
                self._last_heartbeat_ack = True
                
            case 0: # Dispatch
                if t:
                    await self.event_callback(t, d)
                    
            case _:
                logger.warning(f"Unhandled opcode: {op}")
                
    async def _identify(self) -> None:
        """
        Send the IDENTIFY payload to authenticate the bot.
        """
        logger.info("Sending IDENTIFY payload to Discord Gateway...")
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents.value,
                "properties": {
                    "os": "linux",
                    "browser": "botato",
                    "device": "botato"
                }
            }
        }
        await self._send_json(payload)
        
    async def _start_heartbeating(self) -> None:
        """
        Send heartbeats to keep the connection alive.
        """
        logger.debug(f"Starting heartbeat loop every {self._heartbeat_interval} seconds...")
        while True:
            if not self._last_heartbeat_ack:
                logger.warning("Did not receive heartbeat ACK, reconnecting may be required.")
                # TODO: Handle reconnection logic here
            self._last_heartbeat_ack = False
            await self._send_json({"op": 1, "d": self._sequence})
            await asyncio.sleep(self._heartbeat_interval)
            
    async def close(self) -> None:
        """
        Close the WebSocket connection and cancel heartbeats.
        """
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
        logger.info("Gateway connection closed.")