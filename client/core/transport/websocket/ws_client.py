import asyncio
import json
import websockets
from base64 import b64encode
from typing import Callable
from websockets.exceptions import ConnectionClosed

class WebSocketClient:
    """Асинхронный WebSocket для двустороннего общения с сервером"""

    def __init__(self, server_url: str = "ws://127.0.0.1:8000"):
        """Инициализация WebSocket"""
        self.server_url: str = server_url
        self.username: str | None = None
        self.auth_token: str | None = None
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.connected: bool = False
        self.authenticated: bool = False
        self.reconnect_enabled: bool = True
        self.reconnect_delay: float = 3.0

        self.on_connect_callback: Callable | None = None
        self.on_disconnect_callback: Callable | None = None
        self.on_error_callback: Callable | None = None
    
        self.on_message_callback: Callable | None = None
        self.on_message_status_callback: Callable | None = None
        self.on_new_chat_callback: Callable | None = None

        self.listen_task: asyncio.Task | None = None
        self.stop_event = asyncio.Event()
        self.auth_event = asyncio.Event()

    async def reset(self):
        """Остановка WebSocket подключения и фоновой задачи"""
        if self.ws and not self.ws.close_code:
            await self.ws.close()
        if self.listen_task and not self.listen_task.done():
            self.listen_task.cancel()
            try:
                await self.listen_task
            except:
                pass
        self.ws = None
        self.connected = False
        self.authenticated = False

    async def connect(self, username: str, auth_token: str | None = None) -> bool:
        """Подключение к серверу"""
        await self.reset()
        self.username = username
        self.auth_token = auth_token
        self.stop_event.clear()
        self.auth_event.clear()
        self.listen_task = asyncio.create_task(self.connection_loop())
        try:
            await asyncio.wait_for(self.auth_event.wait(), timeout = 10.0)
            return self.authenticated
        except:
            return False
        
    async def disconnect(self):
        """Остановка соединения с запретом на переподключение"""
        await self.reset()
        self.reconnect_enabled = False
        self.stop_event.set()

    async def connection_loop(self):
        """Поддержка соединения с автоматическим переподключением"""
        attempt = 0
        while not self.stop_event.is_set():
            try:
                async with websockets.connect(self.build_url(), ping_interval = 20, ping_timeout = 5) as ws:
                   self.ws = ws
                   self.connected = True
                   attempt = 0
                   self.on_open()
                   async for message in ws:
                       await self.process_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.on_error_callback:
                    self.safe_callback(self.on_error_callback, e)
                if self.on_disconnect_callback:
                    self.safe_callback(
                        self.on_disconnect_callback,
                        getattr(self.ws, "close_code", None),
                        getattr(self.ws, "close_reason", None)
                    )
                    self.connected = False
                    self.authenticated = False
                    if not self.reconnect_enabled or self.stop_event.is_set():
                        break
                    delay = min(self.reconnect_delay * (2**attempt), 60)
                    attempt += 1
                    await asyncio.sleep(delay)
    
    async def process_message(self, message: str):
        """Парсинг входящего JSON-сообщения"""
        try:
            data: dict = json.loads(message)
        except json.JSONDecodeError:
            return
        message_type = data.get("type")
        if message_type == "auth_success":
            self.authenticated = True
            self.auth_event.set()
        elif message_type == "message_from_user":
            if self.on_message_callback:
                self.safe_callback(self.on_message_callback, data)
        elif message_type == "message_receive_status":
            if self.on_message_status_callback:
                self.safe_callback(self.on_message_status_callback, data)
        elif message_type == "new_chat":
            if self.on_new_chat_callback:
                self.safe_callback(self.on_new_chat_callback, data)
        elif message_type == "chat_created":
            if self.on_new_chat_callback:
                self.safe_callback(self.on_new_chat_callback, data)
    
    async def send_json(self, data: dict) -> bool:
        """Отправка сообщения в JSON формате"""
        if not self.ws or not self.connected:
            return False
        try:
            await self.ws.send(json.dumps(data))
            return True
        except ConnectionClosed:
            self.connected = False
            return False
        
    async def send_message(self, temp_id: str, recipient: str, encrypted_content: bytes) -> bool:
        """Отправка сообщений на сервер"""
        payload = {
            "type": "message_to_user",
            "temp_id": temp_id,
            "recipient": recipient,
            "encrypted_content": b64encode(encrypted_content).decode()
        }
        return await self.send_json(payload)

    async def send_message_delivery_confirmation(self, message_id: int) -> None:
        """Подтверждение доставки сообщения"""
        payload = {
            "type": "message_delivery_confirmation",
            "message_id": message_id
        }
        return await self.send_json(payload)
    
    async def create_chat(self, copycat: str) -> bool:
        payload = {
            "type": "create_chat",
            "copycat": copycat
        }
        return await self.send_json(payload)
    
    async def chat_delivery_confirmation(self, initiator: str) -> bool:
        payload = {
            "type": "chat_delivery_confirmation",
            "initiator": initiator
        }
        return await self.send_json(payload)

    def safe_callback(self, callback: Callable, *args):
        """Безопасный вызов callback без блокировки event loop"""
        try:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                asyncio.ensure_future(result)
        except Exception:
            pass
    
    def build_url(self) -> str:
        """Формирование полного WebSocket URL с токеном"""
        url = f"{self.server_url}/ws/{self.username}"
        if self.auth_token:
            url = url + f"?token={self.auth_token}"
        return url
    
    def on_open(self):
        """Вызов при успешном открытии соединения для аутентификации"""
        if self.on_connect_callback:
            self.safe_callback(self.on_connect_callback)

    @property
    def is_connected(self) -> bool:
        return self.connected and self.ws is not None and not self.ws.close_code
    
    @property
    def is_authenticated(self) -> bool:
        return self.authenticated and self.is_connected
