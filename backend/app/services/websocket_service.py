from uuid import UUID

from fastapi import WebSocket


# One module-level instance is shared by every connection (each its own async task) because a
# broadcast has to reach every viewer of a repo, not just the socket that triggered it.
# Scaling limit: this registry is in-memory, so it is only correct while exactly one backend
# instance serves traffic. Behind a load balancer, viewers on other instances get nothing.
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, list[WebSocket]] = {}

    async def connect(self, repo_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(repo_id, []).append(websocket)

    def disconnect(self, repo_id: UUID, websocket: WebSocket):
        connections = self.active_connections.get(repo_id)
        if connections and websocket in connections:
            connections.remove(websocket)
            if not connections:
                del self.active_connections[repo_id]

    async def broadcast(self, repo_id: UUID, message: dict):
        for connection in self.active_connections.get(repo_id, []):
            await connection.send_json(message)


manager = ConnectionManager()
