import os
import subprocess

from utilities.template import template_env
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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


@restricted
async def notebook(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /notebook command by listing the root directory contents of the vault.

    This function:
    1. Initializes an MCP connection to `mcpvault` using the configured `NOTEBOOK_PATH`.
    2. Fetches the list of tools and identifies the `list_directory` tool.
    3. Retrieves the contents of the root directory (/).
    4. Filters out hidden files and directories.
    5. Presents the results as an interactive inline keyboard, allowing users to
       navigate into directories or view files.
    """
    await send_message(update, "RECEIVED")
    mcp_notebook = MCPServerStdio(
        command="npx",
        args=["@bitbonsai/mcpvault", os.getenv("NOTEBOOK_PATH")],
    )
    mcp_notebook_tools = await mcp_notebook.list_tools()
    mcp_notebook_tool_list_directory = None
    for tool in mcp_notebook_tools:
        if tool.name == "list_directory":
            mcp_notebook_tool_list_directory = tool
            break

    mcp_notebook_tool_list_directory_response = await mcp_notebook.call_tool(
        ctx=None,
        tool=mcp_notebook_tool_list_directory,
        name=mcp_notebook_tool_list_directory.name,
        tool_args={"path": "/"},
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
            [InlineKeyboardButton(text=dir, callback_data=f"notebook:d:/{dir}")]
        )
    for file in FILES:
        inline_keyboard_rows.append(
            [InlineKeyboardButton(text=file, callback_data=f"notebook:f:/{file}")]
        )

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_rows)
    await update.message.reply_text("NOTEBOOK", reply_markup=keyboard_markup)


@restricted
async def notebook_commit(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Triggers an automated Git commit workflow for the notebook project.

    This function calls the external `notebook` shell script with the `commit`
    command, which performs the following steps:

    1. Formats the codebase using Prettier.
    2. Checks for any changes using `git diff`.
    3. If changes are detected:
        - Generates an appropriate commit message automatically.
        - Creates a Git commit with the generated message.
    4. If no changes are found, no commit is created.

    All logic (formatting, diff checking, and commit message generation)
    is handled by the underlying notebook shell script.
    """
    await send_message(update, "# NOTEBOOK\n\nWorking.")
    subprocess.run(["notebook", "commit"])
    await send_message(update, "# NOTEBOOK\n\nCommit Done!")
