from ..http_client import HttpClient

class SyncEndpoints:
    def __init__(self, http_client: HttpClient):
        self._http = http_client

    async def sync(self, username: str): # Тут не доделал возвращаемые данные
        try:
            client = await self._http.open_cli()
            resp = await client.get(
                url = "/api/sync",
                params = {
                    "username": username
                }
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
    
    async def ack(
        self,
        username: str,
        message_ids: list[int],
        chat_initiators: list[str]
    ) -> bool:
        try:
            client = await self._http.open_cli()
            resp = await client.post(
                url = "api/sync/ack",
                params = {
                    "username": username
                },
                json = {
                    "messages": message_ids,
                    "chats": chat_initiators
                }
            )
            resp.raise_for_status()
            return True
        except Exception:
            return False
