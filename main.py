import datetime
from utilities.mcp_connection_manager import MCPConnectionManager
import asyncio
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from google import genai

from dotenv import load_dotenv

load_dotenv()

CLIENT = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

TEMPLATE_ENVIRONMENT = Environment(
    loader=FileSystemLoader("utilities/templates"),
    autoescape=select_autoescape()
)

grounding_tool = genai.types.Tool(
    google_search=genai.types.GoogleSearch()
)

def current_time():
    print("current_time")
    return "5:00 AM"

async def main():
    mcp = MCPConnectionManager()
    session = await mcp.connect()

    res = await CLIENT.aio.models.generate_content(
        model="gemma-4-31b-it", contents='READ the PERSONS/al-amin-kouser.md file and tell about him. find about him using notebook, and tell me the current time, and what is the current temperature in dhaka now?',
        config=genai.types.GenerateContentConfig(
            temperature=0,
            tools=[session, grounding_tool],
            tool_config=genai.types.ToolConfig(
                include_server_side_tool_invocations=True,
            ),
        ),
    )
    print(res.text)
    await mcp.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
