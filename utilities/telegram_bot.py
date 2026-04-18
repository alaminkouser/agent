

async def handle_message(update, context):
    print(update.message.text)
    await update.message.reply_text(update.message.text)