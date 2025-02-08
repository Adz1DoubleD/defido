from telegram import Message, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from pathlib import Path
import sys, subprocess, os

from bot.commands import custom, project, utility


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


async def test(update: Update, context: CallbackContext) -> None:
    return


def run_scanner():
    python_executable = sys.executable
    script_path = Path(__file__).parent / "scanner.py"

    if script_path.exists():
        command = [python_executable, str(script_path)]
        process = subprocess.Popen(command)
        return process
    else:
        print(f"Error: {script_path} not found")


application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


if __name__ == "__main__":
    application.add_error_handler(error)
    application.add_handler(CommandHandler("test", test))

    application.add_handler(CommandHandler("burn", project.burn))
    application.add_handler(CommandHandler("buy", project.buy))
    application.add_handler(CommandHandler(["ca", "contract"], project.ca))
    application.add_handler(CommandHandler("chart", project.chart))
    application.add_handler(CommandHandler("compare", project.compare))
    application.add_handler(
        CommandHandler(["contact", "email", "proposal", "marketing"], project.contact)
    )
    application.add_handler(CommandHandler("convert", project.convert))
    application.add_handler(CommandHandler("daily", project.daily))
    application.add_handler(CommandHandler("discord", project.discord))
    application.add_handler(CommandHandler("holders", project.holders))
    application.add_handler(CommandHandler("launch", project.launch))
    application.add_handler(
        CommandHandler(["liquidity", "lp", "lock", "supply"], project.liquidity)
    )
    application.add_handler(CommandHandler(["media", "content"], project.media_command))
    application.add_handler(CommandHandler(["mcap", "marketcap"], project.mcap))
    application.add_handler(CommandHandler("nft", project.nft))
    application.add_handler(CommandHandler("price", project.price))
    application.add_handler(CommandHandler(["tax", "slippage"], project.tax))
    application.add_handler(CommandHandler("treasury", project.treasury))
    application.add_handler(CommandHandler("twitter", project.twitter))
    application.add_handler(CommandHandler("wallet", project.wallet))
    application.add_handler(CommandHandler(["website", "site"], project.website))

    application.add_handler(CommandHandler("ascii", utility.ascii))
    application.add_handler(CommandHandler("blocks", utility.blocks))
    application.add_handler(CommandHandler("coinflip", utility.coinflip))
    application.add_handler(CommandHandler("check", utility.check_input))
    application.add_handler(CommandHandler("fg", utility.fg))
    application.add_handler(CommandHandler("gas", utility.gas))
    application.add_handler(CommandHandler("joke", utility.joke))
    application.add_handler(CommandHandler("roll", utility.roll))
    application.add_handler(CommandHandler("say", utility.say))
    application.add_handler(CommandHandler("time", utility.time_command))
    application.add_handler(CommandHandler("timestamp", utility.timestamp_command))
    application.add_handler(CommandHandler("today", utility.today))
    application.add_handler(CommandHandler("wei", utility.wei))
    application.add_handler(CommandHandler("word", utility.word))

    application.add_handler(CommandHandler("guide", custom.guide))
    application.add_handler(CommandHandler("bridge", custom.bridge))
    application.add_handler(CommandHandler("rpc", custom.rpc))

    run_scanner()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
