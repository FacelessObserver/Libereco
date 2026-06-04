from base64 import b64decode
from fastapi import WebSocket
from auth.auth import Auth
from database.database import Database

class WebSocketHandler:
    """Управляет WebSocket соединениями"""
    def __init__(self, database: Database):
        self.db = database
        self.connections: dict[str, WebSocket] = {}
 
    async def connect(self, websocket: WebSocket, username: str, token: str) -> bool:
        """Регистрация WebSocket соединения"""
        if not Auth().verify_token(token, username):
            await websocket.close(code = 4001, reason = "you are not in 42 community")
            return False
        await websocket.accept()
        self.connections[username] = websocket
        await websocket.send_json({"type": "auth_success"})
        return True
    
    def disconnect(self, username: str) -> None:
        """Отключение WebSocket соединения с пользователем"""
        if username in self.connections:
            del self.connections[username]

    async def router(self, username: str, data: dict) -> None:
        """Маршрутизация сообщений"""
        message_type = data.get("type")
        if message_type == "message_to_user":
            await self.handle_message_to_user(username, data)
        elif message_type == "message_delivery_confirmation":
            await self.handle_message_delivery_confirmation(username, data)
        elif message_type == "create_chat":
            await self.handle_create_chat(username, data)
        elif message_type == "chat_delivery_confirmation":
            await self.handle_chat_delivery_confirmation(username, data)

    async def handle_message_to_user(self, username: str, data: dict) -> None:
        sender = username
        recipient = data.get("recipient")
        if sender == recipient or not recipient:
            return
        encrypted_content = data.get("encrypted_content")
        temp_id = data.get("temp_id")
        message_id, received_at = await self.save_message(sender, recipient, encrypted_content)
        status = message_id and received_at
        payload = {
        "type": "message_receive_status",
        "temp_id": temp_id,
        "received": status,
        "received_at": received_at
        }
        if sender in self.connections:
            try:
                await self.connections[sender].send_json(payload)
            except Exception:
                pass
        if status and recipient in self.connections:
            try:
                await self.send_message(message_id, sender, recipient, encrypted_content, received_at)
            except Exception:
                self.disconnect(recipient)
    
    async def save_message(self, sender: str, recipient: str, encrypted_content: str) -> tuple[int | None, str | None]:
        """Сохранение сообщения в базу данных сервера"""
        try:
            encrypted_bytes = b64decode(encrypted_content)
            return await self.db.messages.save(sender, recipient, encrypted_bytes)
        except Exception:
            return None, None
    
    async def send_message(self, message_id: int, sender: str, recipient: str, encrypted_content: str, received_at: str) -> None:
            payload = {
            "type": "message_from_user",
            "message_id": message_id,
            "sender": sender,
            "recipient": recipient,
            "encrypted_content": encrypted_content,
            "received_at": received_at
            }
            try:
                await self.connections[recipient].send_json(payload)
            except Exception:
                pass
        
    async def handle_message_delivery_confirmation(self, username: str, data: dict) -> None:
        message_id = data.get("message_id")
        try:
            await self.db.messages.delete([message_id], username)
        except Exception:
            pass
    
    async def handle_create_chat(self, username: str, data: dict) -> None:
        copycat = data.get("copycat")
        try:
            if await self.db.chats.exists(username, copycat):
                return
            await self.db.chats.create(username, copycat)
            if username in self.connections:
                try:
                    await self.connections[username].send_json({"type": "chat_created", "copycat": copycat})
                except Exception:
                    pass
            if copycat in self.connections:
                try:
                    await self.connections[copycat].send_json({"type": "new_chat", "initiator": username})
                except Exception:
                    pass
        except Exception:
            pass
        
    async def handle_chat_delivery_confirmation(self, username: str, data: dict) -> None:
        initiator = data.get("initiator")
        try:
            await self.db.chats.delete(username, [initiator])
        except Exception:
            pass
