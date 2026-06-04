from .config import SERVER_URL, VERIFY_SSL
from .endpoints.auth import AuthEndpoints
from .endpoints.sync import SyncEndpoints
from .endpoints.users import UsersEndpoints
from .http_client import HttpClient

class Api:
    def __init__(
        self,
        server_url: str = SERVER_URL,
        verify_ssl: bool = VERIFY_SSL
    ):
        self.http = HttpClient(server_url, verify_ssl)
        self.auth = AuthEndpoints(self.http)
        self.sync = SyncEndpoints(self.http)
        self.users = UsersEndpoints(self.http)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.http.close_cli()
