from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

from .models import Command, Result, ActionType
from ._connection import _WsConnection
from .exceptions import ScreenshotFailed


log = logging.getLogger("waypoint")
_DEFAULT_VIEWPORT = {"width": 1280, "height": 720}


class Waypoint:
    def __init__(
        self,
        token: str,
        *,
        url_template: str = "wss://api.tzafon.ai/ephemeral-tzafonwright?token={token}",
        connect_timeout: float = 10.0,
    ):
        if not token or not token.startswith("wpk_"):
            raise ValueError("token must look like 'wpk_…'")
        self._ws_url = url_template.format(token=token)
        self._timeout = connect_timeout
        self._ws: Optional[_WsConnection] = None

    async def __aenter__(self) -> "Waypoint":
        self._ws = _WsConnection(self._ws_url)
        await asyncio.wait_for(self._ws.connect(), timeout=self._timeout)
        # one-time only
        await self.set_viewport(**_DEFAULT_VIEWPORT)
        return self

    async def __aexit__(self, exc_t, exc, tb) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def goto(self, url: str, *, timeout: int = 5_000) -> Result:
        return await self._send(Command(ActionType.GOTO, url=url, timeout=timeout))

    async def click(self, x: float, y: float) -> Result:
        return await self._send(Command(ActionType.CLICK, x=x, y=y))

    async def type(self, text: str) -> Result:
        return await self._send(Command(ActionType.TYPE, text=text))

    async def scroll(self, dx: int = 0, dy: int = 100) -> Result:
        return await self._send(Command(ActionType.SCROLL, delta_x=dx, delta_y=dy))

    async def screenshot(
        self,
        path: str | os.PathLike | None = None,
        *,
        mkdir: bool = True,
    ) -> bytes:
        """
        Grab a **JPEG** screenshot.

        Parameters
        path:
            Optional file destination. If provided the image is written to disk
            *and* the raw bytes are still returned.
        mkdir:
            Automatically create parent folders if they do not exist.
        """
        res = await self._send(Command(ActionType.SCREENSHOT))
        if not (res.success and res.image):
            raise ScreenshotFailed(res.error_message or "unknown error")

        if path is not None:
            from pathlib import Path

            p = Path(path)
            if mkdir:
                p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(res.image)
        return res.image

    async def set_viewport(self, *, width: int, height: int) -> Result:
        return await self._send(
            Command(ActionType.SET_VIEWPORT_SIZE, width=width, height=height)
        )

    async def _send(self, cmd: Command) -> Result:
        if self._ws is None:
            raise RuntimeError("Waypoint must be used inside 'async with'")
        res = await self._ws.send(cmd)
        if not res.success:
            log.warning("Command %s failed: %s", cmd.action_type, res.error_message)
        return res
