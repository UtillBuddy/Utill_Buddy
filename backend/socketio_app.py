import os
import socketio
from dotenv import load_dotenv

load_dotenv()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS").split(","),
)

app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)
