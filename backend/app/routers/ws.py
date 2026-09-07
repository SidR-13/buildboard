from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_service import manager

router = APIRouter()


@router.websocket("/ws/{repo_id}")
async def repo_websocket(websocket: WebSocket, repo_id: UUID) -> None:
    await manager.connect(repo_id, websocket)
    try:
        # Traffic is server -> client only; this read loop exists purely to notice disconnects.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(repo_id, websocket)
