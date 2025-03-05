from telegram import Message, Update
from telegram.ext import Application, CallbackContext, CommandHandler


import os

from bot.commands import custom, project, utility
from utils import tools

application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


async def error(update: Update, context: CallbackContext):
    if update is None:
        return
    if update.edited_message is not None:
        return
    else:
        message: Message = update.message
        if message is not None and message.text is not None:
            print(f"{message.text} caused error: {context.error}")

        else:
            print(f"Error occurred without a valid message: {context.error}")


def init_main_bot():
    print("🔄 Initializing main bot...")
    application.add_error_handler(error)

    for cmd, handler, _ in custom.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in project.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in utility.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    print("✅ Main bot initialized")


async def post_init(application: Application):
    if not tools.is_local():
        print("✅ Bot Running on server")
        print(await tools.update_bot_commands())

    else:
        print("✅ Bot Running locally")


if __name__ == "__main__":
    init_main_bot()
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)
