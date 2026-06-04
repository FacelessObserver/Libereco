from base64 import b64decode
from typing import Any, Optional
from ..http_client import HttpClient

class UsersEndpoints:
    def __init__(self, http_client: HttpClient):
        self._http = http_client
    
    async def search(self, query: str) -> Optional[list[dict]]:
        try:
            client = await self._http.open_cli()
            resp = await client.get(
                url = "api/users/search",
                params = {
                    "query": query
                }
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            None
    
    async def display_info(
        self,
        usernames: list[str]
    ) -> Optional[dict[str, dict[str, Any]]]:
        try:
            client = await self._http.open_cli()
            resp = await client.get(
                url = "api/users/display_info",
                params = {
                    "usernames": usernames,
                }
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
    
    async def public_key(self, username: str) -> Optional[bytes]:
        try:
            client = await self._http.open_cli()
            resp = await client.get(
                url = f"api/users/{username}/public_key",
                params = {
                    "username": username
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return b64decode(data.get("public_key"))
        except Exception:
            return None
    
    async def update_display_name(self, username: str, display_name: str) -> bool:
        try:
            client = await self._http.open_cli()
            resp = await client.post(
                url = f"api/users/{username}/update/display_name",
                json = {
                    "display_name": display_name
                }
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "ok":
                return True
            return False
        except Exception:
            return False
