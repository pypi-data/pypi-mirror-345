import aiohttp
from loguru import logger
from typing import Any, Optional


class HTTPClient:
    """
    Handles all communication with the Discord REST API.
    
    Provides low-level access to endpoints via GET, POST, etc.
    """
    
    BASE_URL = "https://discord.com/api/v10"
    
    def __init__(self, token: str) -> None:
        """
        Initialize the HTTP client.

        Args:
            token (str): Discord bot token.
        """
        self.token = token
        self.session: aiohttp.ClientSession | None = None
        
    async def request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Optional[dict]:
        """
        Send an HTTP request to a Discord API endpoint.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): Endpoint path, e.g., "/users/@me"

        Returns:
            Optional[dict]: JSON response if available.
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bot {self.token}"}
            )
            
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as resp:
                if resp.status == 204:
                    return None # No content
                data = await resp.json()
                
                if 200 <= resp.status < 300:
                    return data
                else:
                    logger.warning(f"HTTP {resp.status}: {data}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            return None
        
    async def get(self, endpoint: str, **kwargs: Any) -> Optional[dict]:
        """Convenience method for GET requests."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs: Any) -> Optional[dict]:
        """Convenience method for POST requests."""
        return await self.request("POST", endpoint, **kwargs)
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()