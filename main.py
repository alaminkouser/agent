import datetime
from utilities.mcp_connection_manager import MCPConnectionManager
import asyncio
import os
from google import genai

from dotenv import load_dotenv

load_dotenv()

CLIENT = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

grounding_tool = genai.types.Tool(
    google_search=genai.types.GoogleSearch()
)

def x():
    """
    I tell current time
    """
    print("current_time")
    return "5:00 AM"

def y():
    """
    I tell current temperature
    """
    print("current_temperature")
    return "25 degree Celsius"

def g(name: str, age: int | None = None):
    """
    I greet you, But you need to tell me your name first and age if you want.
    """
    print("greeting")
    return f"Hello {name}, you are {age} years old"

async def main():
    MCP = MCPConnectionManager()
    MCP_SESSION = await MCP.connect()

    # Example of Contents:
    # NAME AND AGE ONLY                       : "Greet me please, my name is Humpty Dumpty and I am 25 years old"
    # ONLY CURRENT TIME                       : "What is the current time?"
    # ONLY TEMPERATURE                        : "What is the current temperature?"
    # TIME THEN TEMPERATURE                   : "What is the current time and temperature?"
    # TIME THEN TEMPERATURE THEN NAME AND AGE : "What is the current time and temperature and greet me please, my name is Humpty Dumpty and I am 25 years old"
    # TEMPERATURE THEN TIME THEN NAME AND AGE : "What is the temperature and current time and greet me please, my name is Humpty Dumpty and I am 25 years old"
    # TIME THEN TEMPERATURE THEN NAME         : "What is the current time and temperature and greet me please, my name is Humpty Dumpty"
    res = await CLIENT.aio.models.generate_content(
        model="gemma-4-31b-it", contents="What is the current time and temperature and greet me please, my name is Humpty Dumpty and I am 25 years old",
        config=genai.types.GenerateContentConfig(
            temperature=0,
            tools=[MCP_SESSION, grounding_tool, x, y, g],
            tool_config=genai.types.ToolConfig(
                include_server_side_tool_invocations=True,
            ),
        ),
    )
    print("AI GENERATED: " + res.text)
    await MCP.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
