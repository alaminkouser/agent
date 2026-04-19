from telegram import BotCommand

from .mcp_connection_manager import create_mcp_client

_MCP_CLIENT_CM_KEY = "_mcp_client_cm"


async def telegram_post_init(application):
    await application.bot.set_my_commands(
        commands=[
            BotCommand(command="clear", description="Clear chat history"),
        ],
    )

    mcp_cm = create_mcp_client()
    mcp_client = await mcp_cm.__aenter__()
    application.bot_data["mcp_client"] = mcp_client
    application.bot_data[_MCP_CLIENT_CM_KEY] = mcp_cm


async def telegram_post_shutdown(application):
    mcp_cm = application.bot_data.pop(_MCP_CLIENT_CM_KEY, None)
    if mcp_cm is not None:
        await mcp_cm.__aexit__(None, None, None)
    application.bot_data.pop("mcp_client", None)
