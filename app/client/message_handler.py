from telegram import ReactionTypeEmoji
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelResponsePart,
    ThinkingPart,
    ToolCallPart,
    PartStartEvent,
    PartDeltaEvent,
    PartEndEvent,
    TextPart,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    FinalResultEvent,
)
from pydantic_ai.run import AgentRunResultEvent
from pydantic.dataclasses import dataclass
from telegram import Update
from telegram.ext import ContextTypes

from utilities.send_message import send_message
from client.helpers.restricted import restricted


@dataclass
class Buffer:
    type: ModelResponsePart | None
    text: str


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

        buffer = Buffer(
            type=None,
            text="",
        )
        async for event in agent_main.run_stream_events(user_message):

            # --- START ---
            if isinstance(event, PartStartEvent):
                text = ""
                if isinstance(event.part, ToolCallPart):
                    text = event.part.tool_name
                else:
                    text = event.part.content

                buffer.type = type(event.part)
                buffer.text = text

            # --- DELTA ---
            elif isinstance(event, PartDeltaEvent):
                buffer.text += event.delta.content_delta

            # --- END (THIS IS WHERE YOU PRINT) ---
            elif isinstance(event, PartEndEvent):

                if buffer.type is ThinkingPart:
                    await send_message(update, f"# THINKING\n\n{buffer.text}")

                elif buffer.type is TextPart:
                    await send_message(update, f"{buffer.text}")

                elif buffer.type is ToolCallPart:
                    await send_message(update, f"# TOOL\n\n{buffer.text}")

                else:
                    await send_message(update, "UNKNOWN PART")

            else:
                ignore_events = (
                    FunctionToolCallEvent,
                    FunctionToolResultEvent,
                    FinalResultEvent,
                    AgentRunResultEvent,
                )
                if not isinstance(event, ignore_events):
                    await send_message(update, f"UNKNOWN EVENT: {event}")

    except Exception as e:
        print(e)
        await send_message(update, str(e))
