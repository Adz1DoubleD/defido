
from telegram import *
from telegram.ext import *

from data import api, db, constants
import os
import time as t
from datetime import datetime, timedelta


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        db.clicks_reset()
        await update.message.reply_text(f"*{api.escape_markdown(constants.PROJECT_NAME)} Admin Commands*\n\n"
                                        f"/filters Filters\n"
                                        f"/addfilter `word` `reply` Adds filter\n"
                                        f"/deletefilter `word` Removes filter\n\n"
                                        f"/blacklist Blacklisted words\n"
                                        f"/addbl `word` Adds blacklisted word\n"
                                        f"/deletebl `word` Removes blacklisted word\n\n"
                                        f"/wen Next Click me time\n"
                                        f"/winners `number` Draw number of winners and reset\n"
                                        f"/reset  Reset leaderboard with no draw\n",
                                        parse_mode = "Markdownv2")


async def blacklist(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        words = db.blacklist_get_all()

        if words:
            word_list_str = "\n".join(words)
            await update.message.reply_text(f"All blacklisted words:\n{word_list_str}")
        else:
            await update.message.reply_text("The blacklist is empty.")


async def blacklist_add(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        args = context.args
        if not args:
            await update.message.reply_text("Please provide a word to add to the blacklist")
            return

        word = args[0]

        if db.blacklist_get(word):
            await update.message.reply_text(f"The word '{word}' is already in the blacklist")
            return

        db.blacklist_add(word)

        await update.message.reply_text(f"Word '{word}' added to the blacklist")


async def blacklist_delete(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        args = context.args
        if not args:
            await update.message.reply_text("Please provide a word to remove from the blacklist.")
            return

        word = args[0]
        
        if not db.blacklist_get(word):
            await update.message.reply_text(f"The word '{word}' is not in the blacklist.")
            return

        db.blacklist_delete(word)

        await update.message.reply_text(f"Word '{word}' removed from the blacklist.")


async def filter_add(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Please provide the filter and the reply")
            return

        word, reply = args

        if word.startswith('/'):
            await update.message.reply_text("Sorry, it's not possible to add a filter for a command")
            return

        existing_reply = db.filter_check(word)
        if existing_reply:
            await update.message.reply_text(f"The filter '{word}' already exists")
            return
        
        db.filter_add(word, reply)

        await update.message.reply_text(f"Filter '{word}' added")


async def filter_delete(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("Please provide the filter you want to delete")
            return

        word = args[0]

        existing_reply = db.filter_check(word)
        if not existing_reply:
            await update.message.reply_text(f"The filter '{word}' does not exist")
            return

        db.filter_delete(word)

        await update.message.reply_text(f"Filter '{word}' deleted")


async def reset_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        db.clicks_reset()
        await update.message.reply_text(f"Leaderboard reset!")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        if constants.BUTTON_TIME is not None:
            time = constants.BUTTON_TIME
        else:    
            time = constants.FIRST_BUTTON_TIME
        target_timestamp = constants.RESTART_TIME + time
        time_difference_seconds = target_timestamp - datetime.now().timestamp()
        time_difference = timedelta(seconds=time_difference_seconds)
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await update.message.reply_text(f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds")


async def winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = " ".join(context.args)
    user_id = update.effective_user.id
    if user_id in constants.ADMINS:
        if not number.isdigit():
            await update.message.reply_text("Winners is not a valid number, Follow /winners with the number of winners you need.")
            return 
        else:
            await update.message.reply_text(f"*{constants.PROJECT_NAME} Winners*\n\n"
                            f"The winners of the Click Me competition are:\n\n"
                            f'{db.clicks_get_leaderboard(limit=int(number))}\n'
                            f"Congratulations!\n\n"
                            f"Leaderboard has been reset",
                            parse_mode="Markdown")
            db.clicks_reset()