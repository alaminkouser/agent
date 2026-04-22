from telegram import ReactionTypeEmoji
from pydantic_ai import Agent
from telegram import Update
from telegram.ext import ContextTypes

from utilities.send_message import send_message
from utilities.template import template_env
from client.helpers.restricted import restricted


@restricted
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function is called when the user sends the /start command.

    It sends a message to the user with the agent's name and description.
    It also sends a mermaid diagram of the agent's workflow.
    """
    user_message = update.message.text

    agent_main: Agent = context.bot_data["agent_main"]

    try:
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reaction=[ReactionTypeEmoji(emoji="⚡")],
        )

        agent_run = await agent_main.run(user_message)

        await send_message(
            update,
            template_env.get_template("thinking.j2").render(
                thinking_text=agent_run.response.thinking
            ),
        )
        await send_message(update, agent_run.output)
    except Exception as e:
        print(e)
        await send_message(update, str(e))
