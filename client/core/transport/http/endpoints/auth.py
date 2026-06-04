from base64 import b64encode
from typing import Optional
from ..http_client import HttpClient

class AuthEndpoints:
    def __init__(self, http_client: HttpClient):
        self._http = http_client
    
    async def register(
        self,
        username: str,
        display_name: str,
        password: str,
        public_key: bytes
    ) -> bool:
        try:
            client = await self._http.open_cli()
            resp = await client.post(
                url = "api/auth/register",
                json = {
                    "username": username,
                    "display_name": display_name,
                    "public_key": b64encode(public_key).decode(),
                    "password": password
                }
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            return False
        
    async def login(self, username: str, password: str) -> Optional[str]:
        try:
            client = await self._http.open_cli()
            resp = await client.post(
                url = "api/auth/login",
                json = {
                    "username": username,
                    "password": password
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("token")
        except Exception:
            return None
