import httpx
from typing import Optional

class HttpClient:
    def __init__(self, server_url: str, verify_ssl: bool):
        self.client: Optional[httpx.AsyncClient] = None 
        self.server_url = server_url.rstrip("/")
        self.verify_ssl = verify_ssl
    
    async def open_cli(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(
                base_url = self.server_url,
                verify = self.verify_ssl
            )
        return self.client
    
    async def close_cli(self) -> None:
        if self.client and not self.client.is_closed:
            await self.client.aclose()
            self.client = None
