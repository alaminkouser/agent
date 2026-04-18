import os
import sys
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

class MCPConnectionManager:
    def __init__(self, notebook_path: Optional[str] = None) -> None:
        transport = os.getenv("MCP_TRANSPORT", "http").strip().lower()
        self._use_stdio = transport == "stdio"

        if self._use_stdio:
            path = (
                notebook_path
                if notebook_path is not None
                else os.getenv("NOTEBOOK_PATH")
            )
            if not path:
                raise ValueError(
                    "Set NOTEBOOK_PATH or pass notebook_path= when MCP_TRANSPORT=stdio."
                )
            self._server_params = StdioServerParameters(
                command="npx",
                args=["@bitbonsai/mcpvault", path],
            )
            self._http_url: Optional[str] = None
        else:
            self._server_params = None
            self._http_url = "https://mcp.serpapi.com/" + os.getenv("SERP_API_KEY") + "/mcp"

        self._transport_cm = None
        self._session_cm = None

    async def connect(self) -> ClientSession:
        if self._transport_cm is not None:
            raise RuntimeError("MCPConnectionManager is already connected.")

        if self._use_stdio:
            self._transport_cm = stdio_client(self._server_params)
            read, write = await self._transport_cm.__aenter__()
        else:
            assert self._http_url is not None
            self._transport_cm = streamable_http_client(self._http_url)
            read, write, _ = await self._transport_cm.__aenter__()

        try:
            self._session_cm = ClientSession(read, write)
            return await self._session_cm.__aenter__()
        except BaseException:
            await self._transport_cm.__aexit__(*sys.exc_info())
            self._transport_cm = None
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
            if self._transport_cm is not None:
                await self._transport_cm.__aexit__(exc_type, exc_val, exc_tb)
            self._session_cm = None
            self._transport_cm = None

    async def __aenter__(self) -> ClientSession:
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        await self.disconnect(exc_type, exc_val, exc_tb)
