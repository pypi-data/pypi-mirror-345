import os
from abc import ABC, abstractmethod
from contextlib import suppress
from datetime import timedelta
from typing import Any, Literal

from any_agent.config import AgentFramework, MCPSseParams, MCPStdioParams
from any_agent.tools.mcp.mcp_server import MCPServerBase

mcp_available = False
with suppress(ImportError):
    from langchain_mcp_adapters.tools import load_mcp_tools
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.sse import sse_client
    from mcp.client.stdio import stdio_client

    mcp_available = True


class LangchainMCPServerBase(MCPServerBase, ABC):
    client: Any | None = None
    framework: Literal[AgentFramework.LANGCHAIN] = AgentFramework.LANGCHAIN

    def _check_dependencies(self) -> None:
        """Check if the required dependencies for the MCP server are available."""
        self.libraries = "any-agent[mcp,langchain]"
        self.mcp_available = mcp_available
        super()._check_dependencies()

    @abstractmethod
    async def _setup_tools(self) -> None:
        """Set up the LangChain MCP server with the provided configuration."""
        if not self.client:
            msg = "MCP client is not set up. Please call `setup` from a concrete class."
            raise ValueError(msg)

        stdio, write = await self._exit_stack.enter_async_context(self.client)

        client_session = ClientSession(
            stdio,
            write,
            timedelta(seconds=self.mcp_tool.client_session_timeout_seconds)
            if self.mcp_tool.client_session_timeout_seconds
            else None,
        )
        session = await self._exit_stack.enter_async_context(client_session)

        await session.initialize()
        # List available tools
        self.tools = await load_mcp_tools(session)

        self.tools = self._filter_tools(self.tools)


class LangchainMCPServerStdio(LangchainMCPServerBase):
    mcp_tool: MCPStdioParams

    async def _setup_tools(self) -> None:
        server_params = StdioServerParameters(
            command=self.mcp_tool.command,
            args=list(self.mcp_tool.args),
            env={**os.environ},
        )

        self.client = stdio_client(server_params)

        await super()._setup_tools()


class LangchainMCPServerSse(LangchainMCPServerBase):
    mcp_tool: MCPSseParams

    async def _setup_tools(self) -> None:
        self.client = sse_client(
            url=self.mcp_tool.url,
            headers=dict(self.mcp_tool.headers or {}),
        )

        await super()._setup_tools()


LangchainMCPServer = LangchainMCPServerStdio | LangchainMCPServerSse
