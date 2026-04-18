import os
import sys
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPConnectionManager:
    """MCP vault over stdio: ``session = await mgr.connect()`` then ``await mgr.disconnect()``."""

    def __init__(self, notebook_path: Optional[str] = None) -> None:
        path = notebook_path if notebook_path is not None else os.getenv("NOTEBOOK_PATH")
        if not path:
            raise ValueError(
                "Set NOTEBOOK_PATH or pass notebook_path= to MCPConnectionManager."
            )
        self._server_params = StdioServerParameters(
            command="npx",
            args=["@bitbonsai/mcpvault", path],
        )
        self._stdio_cm = None
        self._session_cm = None

    async def connect(self) -> ClientSession:
        if self._stdio_cm is not None:
            raise RuntimeError("MCPConnectionManager is already connected.")
        self._stdio_cm = stdio_client(self._server_params)
        read, write = await self._stdio_cm.__aenter__()
        try:
            self._session_cm = ClientSession(read, write)
            return await self._session_cm.__aenter__()
        except BaseException:
            await self._stdio_cm.__aexit__(*sys.exc_info())
            self._stdio_cm = None
            self._session_cm = None
            raise

    async def disconnect(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: object | None = None,
    ) -> None:
        try:
            if self._session_cm is not None:
                await self._session_cm.__aexit__(exc_type, exc_val, exc_tb)
        finally:
            if self._stdio_cm is not None:
                await self._stdio_cm.__aexit__(exc_type, exc_val, exc_tb)
            self._session_cm = None
            self._stdio_cm = None

    async def __aenter__(self) -> ClientSession:
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        await self.disconnect(exc_type, exc_val, exc_tb)
