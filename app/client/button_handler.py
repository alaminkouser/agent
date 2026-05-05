import os

from pydantic_ai.mcp import MCPServerStdio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from client.helpers.restricted import restricted


@restricted
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    query_data = query.data

    mcp_notebook = MCPServerStdio(
        command="npx",
        args=["@bitbonsai/mcpvault", os.getenv("NOTEBOOK_PATH")],
    )
    mcp_notebook_tools = await mcp_notebook.list_tools()
    if query_data.startswith("notebook:d:"):
        mcp_notebook_tool_list_directory = None
        for tool in mcp_notebook_tools:
            if tool.name == "list_directory":
                mcp_notebook_tool_list_directory = tool
                break

        PATH = query_data.split(":")[2]
        mcp_notebook_tool_list_directory_response = await mcp_notebook.call_tool(
            ctx=None,
            tool=mcp_notebook_tool_list_directory,
            name=mcp_notebook_tool_list_directory.name,
            tool_args={"path": PATH},
        )

        DIRS: list[str] = []
        FILES: list[str] = []

        for dir in mcp_notebook_tool_list_directory_response["dirs"]:
            if str(dir).startswith(".") != True:
                DIRS.append(dir)

        for file in mcp_notebook_tool_list_directory_response["files"]:
            if str(file).startswith(".") != True:
                FILES.append(file)

        inline_keyboard_rows = []
        for dir in DIRS:
            inline_keyboard_rows.append(
                [
                    InlineKeyboardButton(
                        text=dir, callback_data=f"notebook:d:{PATH}/{dir}"
                    )
                ]
            )
        for file in FILES:
            inline_keyboard_rows.append(
                [
                    InlineKeyboardButton(
                        text=file, callback_data=f"notebook:f:{PATH}/{file}"
                    )
                ]
            )

        keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_rows)

        await query.edit_message_text(
            text=f"NOTEBOOK: {PATH}", reply_markup=keyboard_markup
        )

    if query_data.startswith("notebook:f:"):
        FILE_PATH = query_data.split(":")[2]

        if FILE_PATH.endswith(".md"):
            mcp_notebook_tool_read_note = None
            for tool in mcp_notebook_tools:
                if tool.name == "read_note":
                    mcp_notebook_tool_read_note = tool
                    break

            mcp_notebook_tool_read_note_response = await mcp_notebook.call_tool(
                ctx=None,
                tool=mcp_notebook_tool_read_note,
                name=mcp_notebook_tool_read_note.name,
                tool_args={"path": FILE_PATH},
            )
            await query.edit_message_text(
                text=f"```md\n{mcp_notebook_tool_read_note_response["content"].replace("-", "\\-").replace("`", "\\`")}\n```",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        else:
            await query.edit_message_text(text=f"FILE IS NOT MARKDOWN: {FILE_PATH}")
