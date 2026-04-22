import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.mcp import MCPServerStdio, MCPServerStreamableHTTP
from pydantic_ai_skills import SkillsCapability

import logfire

from utilities.template import template_env

from .tools.status_put import status_put, StatusPutInput, StatusPutOutput

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()


def agent_main() -> Agent:
    """
    Creates the main agent with all the tools and instructions.
    """
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

    instructions = template_env.get_template("agent_main_instructions.j2").render(
        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    agent = Agent(
        model,
        name="Agent Main",
        description="The Primary Agent",
        instructions=instructions,
        toolsets=[
            mcp_notebook,
            mcp_serpapi,
            mcp_browser,
        ],
        capabilities=[
            SkillsCapability(
                directories=[
                    Path(Path(__file__).resolve().parent).joinpath("skills").resolve(),
                    Path(Path(__file__).resolve().parent)
                    .joinpath("..", "..", ".DATA", "skills")
                    .resolve(),
                ]
            )
        ],
    )

    @agent.tool_plain
    def tool_status_put(input: str) -> StatusPutOutput:
        """
        Updates the personal status message displayed on the website.

        Use this tool to share a short, human-readable update about the current
        personal situation (e.g., availability, focus, mood, or ongoing
        activities) on https://alaminkouser.com/status/.

        The input should be concise and clear, such as "Working deeply, limited
        availability", "Taking a break", or "Open to new opportunities". Avoid
        sensitive or overly detailed personal information. Keep messages brief,
        intentional, and appropriate for public visibility.
        """
        return status_put(StatusPutInput(status=input))

    return agent
