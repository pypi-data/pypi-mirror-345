# botato/client.py
# -*- coding: utf-8 -*-

from typing import Callable, Awaitable, Dict, List, TypeVar
from loguru import logger

from botato.gateway.connection import GatewayConnection
from botato.gateway.events import EventDispatcher
from botato.http.client import HTTPClient
from botato.intents import Intents

T = TypeVar('T', bound=Callable[..., Awaitable[None]])


class BotatoClient:
    """
    Main client class for interacting with the Discord API.
    
    This class handles Gateway connectivity, HTTP communication,
    and user-defined event registration and dispatching.
    """
    
    def __init__(self, token: str, intents: Intents) -> None:
        """
        Initialize the BotatoClient with the provided token.

        Args:
            token (str): Discord bot token used for authentication.
            intents (Intents): The intents for the bot's operations.
        """
        self.token: str = token.strip()
        self.intents: Intents = intents
        self.gateway: GatewayConnection | None = None
        self.http: HTTPClient | None = None
        self.dispatcher: EventDispatcher = EventDispatcher()
        
        logger.debug("BotatoClient initialized.")
        
    async def connect(self) -> None:
        """
        Connect to the Discord Gateway and start listening for events.
        """
        logger.info("Starting BotatoClient connection...")
        
        self.http = HTTPClient(self.token)
        self.gateway = GatewayConnection(self.token, self._handle_event, self.intents)
        await self.gateway.connect()
        
    def event(self, func: T) -> T:
        """
        Decorator to register an event handler.
        
        The function name should match the event name from Discord,
        e.g., 'on_message_create', 'on_ready';

        Args:
            func (Callable): The function to be registered as an event handler.
        Returns:
            Callable: The original function, now registered as an event handler.
        """
        return self.dispatcher.register(func)
    
    async def _handle_event(self, event_name: str, data: dict) -> None:
        """
        Internal method to dispatch an event to registered handlers;

        Args:
            event_name (str): Discord event name (e.g., 'MESSAGE_CREATE').
            data (dict): Raw event payload
        """
        await self.dispatcher.dispatch(event_name, data)
        
    async def close(self) -> None:
        """
        Close the connection to Discord and clean up resources.
        """
        logger.info("Closing BotatoClient...")
        if self.gateway:
            await self.gateway.close()
        if self.http:
            await self.http.close()