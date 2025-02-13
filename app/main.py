from telegram import Message, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from pathlib import Path
import sys
import subprocess
import os

from bot.commands import custom, project, utility
from utils import tools


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
    application.add_error_handler(error)

    for cmd, handler, _ in custom.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in project.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))

    for cmd, handler, _ in utility.HANDLERS:
        application.add_handler(CommandHandler(cmd, handler))


def init_scanner_bot():
    python_executable = sys.executable
    script_path = Path(__file__).parent / "scanner.py"

    if script_path.exists():
        command = [python_executable, str(script_path)]
        process = subprocess.Popen(command)
        return process
    else:
        print(f"Error: {script_path} not found")


application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


def start():
    init_main_bot()

    if not tools.is_local():
        print("✅ Bot Running on server")

        custom_commands, project_commands, utility_commands = (
            tools.update_bot_commands()
        )
        print(custom_commands)
        print(project_commands)
        print(utility_commands)

        init_scanner_bot()

    else:
        print("✅ Bot Running locally")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    start()
