from __future__ import annotations
import asyncio
import traceback
import websockets
from websockets.connection import State

from .models import Command, Result


class _WsConnection:
    def __init__(self, url: str, *, ping_interval: int = 20):
        if not url.startswith(("ws://", "wss://")):
            raise ValueError(f"Invalid websocket URL '{url}'")
        self._url = url
        self._conn: websockets.WebSocketClientProtocol | None = None
        self._ping = ping_interval

    async def connect(self) -> None:
        if self.is_open:
            return
        self._conn = await websockets.connect(
            self._url,
            max_size=2**24,  # 16 MiB
            ping_interval=self._ping,
            ping_timeout=self._ping,
        )

    async def close(self) -> None:
        if self._conn and self._conn.state is State.OPEN:
            try:
                await self._conn.close(code=1000, reason="Client shutting down")
                await asyncio.wait_for(self._conn.wait_closed(), timeout=5)
            except Exception:
                traceback.print_exc()
        self._conn = None

    async def send(self, cmd: Command) -> Result:
        if not self.is_open:
            raise RuntimeError("Websocket not connected")
        await self._conn.send(cmd.dump())
        raw = await self._conn.recv()
        if isinstance(raw, str):
            raw = raw.encode()
        return Result.load(raw)

    @property
    def is_open(self) -> bool:
        return (
            self._conn is not None and getattr(self._conn, "state", None) is State.OPEN
        )
