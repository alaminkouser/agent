import os
from fastmcp import Client


def create_mcp_client() -> Client:
    config: dict = {
        "mcpServers": {
            "NOTEBOOK": {
                "command": "npx",
                "args": ["@bitbonsai/mcpvault", os.getenv("NOTEBOOK_PATH")],
            },
            "BROWSER": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
            },
            "SERPAPI": {
                "url": "https://mcp.serpapi.com/"
                + os.getenv("SERP_API_KEY", "")
                + "/mcp",
            },
        }
    }
    return Client(config)
