from utilities.template import template_env
from pydantic_ai import Agent
from telegram import Update
from telegram.ext import ContextTypes

from utilities.send_message import send_message
from client.helpers.restricted import restricted


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function is called when the user sends the /start command.

    It sends a message to the user with the agent's name and description.
    It also sends a mermaid diagram of the agent's workflow.
    """
    user_full_name = update.effective_user.full_name
    agent_main: Agent = context.bot_data["agent_main"]
    agent_name = agent_main.name
    agent_description = agent_main.description

    command_start_message = template_env.get_template("client_command_start.j2").render(
        user_full_name=user_full_name,
        agent_name=agent_name,
        agent_description=agent_description,
    )

    context.user_data["message_history"] = None

    await send_message(update, command_start_message)
