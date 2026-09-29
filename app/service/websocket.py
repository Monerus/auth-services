from fastapi import FastAPI, WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
         self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket


    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


    async def send_to_user(self, user_id: str, data: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(data)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except Exception:
                # На случай, если какой-то сокет оборвался, но не успел удалиться
                pass

manager = ConnectionManager()