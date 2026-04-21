import os

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.mcp import MCPServerStdio, MCPServerStreamableHTTP


def agent_main() -> Agent:
    model = GoogleModel(
        "gemma-4-31b-it", provider=GoogleProvider(api_key=os.getenv("GEMINI_API_KEY"))
    )

    mcp_notebook = MCPServerStdio(
        command="npx",
        args=["@bitbonsai/mcpvault", os.getenv("NOTEBOOK_PATH")],
    )

    mcp_serpapi = MCPServerStreamableHTTP(
        url="https://mcp.serpapi.com/" + os.getenv("SERP_API_KEY", "") + "/mcp"
    )

    mcp_browser = MCPServerStdio(command="npx", args=["@playwright/mcp@latest"])

    return Agent(
        model,
        name="Agent Main",
        description="The Primary Agent",
        toolsets=[mcp_notebook, mcp_serpapi, mcp_browser],
    )
