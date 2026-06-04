from fastapi import FastAPI, HTTPException, WebSocket, Query
from base64 import b64decode, b64encode
import bcrypt
import json
from typing import List
from database.database import Database
from ws_server import WebSocketHandler
from auth.auth import Auth
from contextlib import asynccontextmanager

db: Database | None = None
ws_handler: WebSocketHandler | None = None

@asynccontextmanager
async def lifespan(app: FastAPI): 
    """Инициализация и закрытие ресурсов"""
    global db, ws_handler
    if db is None:
        db = Database("Libereco.db")
        await db.init()
    if ws_handler is None:
        ws_handler = WebSocketHandler(database = db)
    yield
    if db:
        await db.close()

app = FastAPI(title = "Libereco Messenger API", lifespan = lifespan)

@app.post("/api/auth/register")
async def register(data: dict):
    username = data.get("username")
    password = data.get("password")
    display_name = data.get("display_name")
    public_key_b64 = data.get("public_key")
    if not all([username, password, display_name, public_key_b64]):
        raise HTTPException(400, "Missing fields")
    if await db.users.exists(username):
        raise HTTPException(409, "User already exists")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    public_key = b64decode(public_key_b64)
    if not await db.users.create(username, display_name, public_key, password_hash):
        raise HTTPException(500, "Failed to create user")
    return {"status": "ok"}

@app.post("/api/auth/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(400, "Missing fields")
    if not await db.users.exists(username):
        raise HTTPException(401, "Invalid username or password")
    if not await db.users.verify_password(username, password):
        raise HTTPException(401, "Invalid username or password")
    token = Auth().create_access_token(username)
    return {"token": token}

@app.get("/api/sync")
async def sync(username: str):
    """Получение чатов и оффлайн-сообщений"""
    if not username:
        raise HTTPException(400, "Username required")
    chats = await db.chats.get(username)
    messages = await db.messages.get(username)
    return {"chats": chats, "messages": messages}

@app.post("/api/sync/ack")
async def acknowledge_sync(username: str, ack: dict):
    """Подтверждение получения offline-данных"""
    if not username:
        raise HTTPException(400, "Username required")
    message_ids = ack.get("messages", [])
    chat_initiators = ack.get("chats", [])
    if message_ids:
        await db.messages.delete(message_ids, username)
    if chat_initiators:
        await db.chats.delete(username, chat_initiators)
    return {"status": "ok"}

@app.get("/api/users/search")
async def search_users(query: str = Query(..., min_length = 1), limit: int = 5):
    return await db.users.search(query, limit)

@app.get("/api/users/display_info")
async def get_display_info(usernames: List[str] = Query(...)):
    return await db.users.get_public_info(usernames)

@app.get("/api/users/{username}/public_key")
async def get_user_public_key(username: str):
    pk = await db.users.get_public_key(username)
    if pk is None:
        raise HTTPException(404, "User not found")
    return {"public_key": b64encode(pk).decode()}

@app.post("/api/users/{username}/update/display_name")
async def update_display_name(username: str, data: dict):
    new_name = data.get("display_name")
    if not new_name:
        raise HTTPException(400, "Missing display_name")
    if not await db.users.exists(username):
        raise HTTPException(404, "User not found")
    success = await db.users.update_display_name(username, new_name)
    if not success:
        raise HTTPException(500, "Failed to update")
    return {"status": "ok"}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, token: str = Query(None)):
    if not token:
        await websocket.close(code = 4001, reason = "Missing token")
        return
    if not await ws_handler.connect(websocket, username, token):
        return
    try:
        while True:
            raw_message = await websocket.receive_text()
            data = json.loads(raw_message)
            await ws_handler.router(username, data)
    except Exception:
        ws_handler.disconnect(username)
