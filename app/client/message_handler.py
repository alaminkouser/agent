from telegram import ReactionTypeEmoji
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ThinkingPart,
    ToolCallPart,
    PartStartEvent,
    PartDeltaEvent,
    PartEndEvent,
    TextPart,
    FunctionToolCallEvent,
)
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

        buffers = {}
        async for event in agent_main.run_stream_events(user_message):

            # --- START ---
            if isinstance(event, PartStartEvent):
                buffers[event.index] = {
                    "type": type(event.part),
                    "content": getattr(event.part, "content", "") or "",
                    "tool_name": getattr(event.part, "tool_name", None),
                }

            # --- DELTA ---
            elif isinstance(event, PartDeltaEvent):
                buf = buffers.get(event.index)
                if not buf:
                    continue

                delta = event.delta

                if hasattr(delta, "content_delta") and delta.content_delta:
                    buf["content"] += delta.content_delta

            # --- END (THIS IS WHERE YOU PRINT) ---
            elif isinstance(event, PartEndEvent):
                buf = buffers.pop(event.index, None)
                if not buf:
                    continue

                part_type = buf["type"]

                if part_type is ThinkingPart:
                    await send_message(update, f"# THINKING\n\n{buf["content"]}")

                elif part_type is TextPart:
                    await send_message(update, f"{buf["content"]}")

                elif part_type is ToolCallPart:
                    await send_message(update, f"# TOOL\n\n{buf["tool_name"]}")

                else:
                    await send_message(update, f"# UNKNOWN\n\n{str(event)}")

    except Exception as e:
        print(e)
        await send_message(update, str(e))
