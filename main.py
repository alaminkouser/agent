import os
import datetime
from utilities.mcp_connection_manager import MCPConnectionManager
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from utilities.telegram_bot import handle_message

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

async def main():
    MCP = MCPConnectionManager()
    MCP_SESSION = await MCP.connect()

    TELEGRAM_BOT.bot_data["mcp_session"] = MCP_SESSION

    TELEGRAM_BOT.add_handler(
        MessageHandler(
            filters.ALL,
            handle_message
        )
    )

    
    await MCP.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
    TELEGRAM_BOT.run_polling()
