from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_service import manager

router = APIRouter()


@router.websocket("/ws/{repo_id}")
async def repo_websocket(websocket: WebSocket, repo_id: UUID):
    await manager.connect(repo_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(repo_id, websocket)
