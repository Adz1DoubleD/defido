
from telegram import *
from telegram.ext import *
import os
from data import api, db, constants
import time as t
import random
from datetime import datetime
from media import index as media
from commands import admin, project, utility
from typing import Optional, Tuple


current_button_data = None
clicked_buttons = set()
first_user_clicked = False


RESTRICTIONS = {
    'can_send_messages': False,
    'can_send_media_messages': False,
    'can_send_other_messages': False,
    'can_add_web_page_previews': False,
}


async def auto_message_click(context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_button_data, first_user_clicked
    first_user_clicked = False
    if context.bot_data is None:
        context.bot_data = {}
    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = current_button_data
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"Click Me!", callback_data=current_button_data)]]
    )
    await context.bot.send_photo(
        photo=media.logo(),
        chat_id=constants.TELEGRAM_CHANNEL_ID,
        reply_markup=keyboard,
    )
    button_generation_timestamp = t.time()
    context.bot_data["button_generation_timestamp"] = button_generation_timestamp


async def clicks_function(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_button_data, first_user_clicked
    button_click_timestamp = t.time()

    if context.user_data is None:
        context.user_data = {}

    current_button_data = context.bot_data.get("current_button_data")
    button_generation_timestamp = context.bot_data.get("button_generation_timestamp")
    if not current_button_data:
        return

    button_data = update.callback_query.data
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"

    if button_data in clicked_buttons:
        return

    clicked_buttons.add(button_data)

    if button_data == current_button_data:
        
        time_taken = button_click_timestamp - button_generation_timestamp

        await db.clicks_update(user_info, time_taken)
    

        if not first_user_clicked:
            first_user_clicked = True

            user_data = db.clicks_get_by_name(user_info)
            clicks = user_data[0]
            total_click_count = db.clicks_get_total()
            if clicks == 1:
                click_message = f"🎉🎉 This is their first click! 🎉🎉"

            elif clicks % 10 == 0:
                click_message = f"🎉🎉 They have clicked {clicks} times! 🎉🎉"
                
            else:
                click_message = f"They have clicked {clicks} timess!"

            if db.clicks_check_is_fastest(time_taken) == True:
                click_message +=  f"\n\n🎉🎉 {time_taken:.3f} seconds is the new fastest clicker! 🎉🎉"

            
            message_text = (
                f"{db.escape_markdown(user_info)} clicked first in\n{time_taken:.3f} seconds!\n\n"
                f"{click_message}\n\n"
                f"use `/leaderboard` to see the fastest clickers!\n\n"
            )
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
                parse_mode="Markdown",
            )

                
        constants.RESTART_TIME = datetime.now().timestamp()        
        context.user_data["current_button_data"] = None
        button_time = constants.RANDOM_BUTTON_TIME()
        job_queue.run_once(
        auto_message_click,
        button_time,
        chat_id=constants.TELEGRAM_CHANNEL_ID,
        name="Click Message",
    )
        return button_time
    

async def handle_message(update: Update, context: CallbackContext) -> None:
        message_text = update.message.text.lower()

        if db.blacklist_check(message_text):
            await update.message.delete()
            return

        if db.filter_check(message_text):
            reply = db.filter_check(message_text)
            if reply:
                await update.message.reply_text(reply)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:

    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    new_member = update.chat_member.new_chat_member
    new_member_id = new_member.user.id
    if new_member.user.username:
        new_member_username = f"@{new_member.user.username}"
    else:
        if new_member.user.last_name:
            new_member_username = f"{new_member.user.first_name} {new_member.user.last_name}"
        else:
            new_member_username = new_member.user.first_name
  
    if not was_member and is_member:
        previous_welcome_message_id = context.bot_data.get('welcome_message_id')
        if previous_welcome_message_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=previous_welcome_message_id)
            except Exception:
                pass

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=new_member_id,
            permissions=RESTRICTIONS,
        )

        welcome_message = await update.effective_chat.send_photo(
            photo=media.logo(),
            caption=f"Welcome {api.escape_markdown(new_member_username)} to {constants.PROJECT_NAME}!\n\nClick the button below to prove you are human!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"I am human!",
                                    callback_data=f"unmute:{new_member_id}",
                                )
                            ],
                        ]
                    ),
                )
        context.bot_data['welcome_message_id'] = welcome_message.message_id
            

async def button_callback(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    action, _ = update.callback_query.data.split(":", 1)

    if action == "unmute":
        user_restrictions = {key: True for key in RESTRICTIONS}

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=user_restrictions,
        )


application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
job_queue = application.job_queue


if __name__ == "__main__":
#    application.add_handler(CallbackQueryHandler(button_callback, pattern=r"unmute:.+"))
#    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.add_handler(CallbackQueryHandler(clicks_function))

    application.add_handler(CommandHandler("admin", admin.command))
    application.add_handler(CommandHandler("addfilter", admin.filter_add))
    application.add_handler(CommandHandler("deletefilter", admin.filter_delete))
    application.add_handler(CommandHandler("blacklist", admin.blacklist))
    application.add_handler(CommandHandler("addbl", admin.blacklist_add))
    application.add_handler(CommandHandler("deletebl", admin.blacklist_delete))
    application.add_handler(CommandHandler("reset", admin.reset_leaderboard))
    application.add_handler(CommandHandler("wen", admin.wen))
    application.add_handler(CommandHandler("winners", admin.winners))

    application.add_handler(CommandHandler("filters", project.filters_list))
    application.add_handler(CommandHandler("leaderboard", project.leaderboard))
    application.add_handler(CommandHandler("me", project.me))

    application.add_handler(CommandHandler(["ca", "contract"], project.ca))
    application.add_handler(CommandHandler("compare", project.compare))
    application.add_handler(CommandHandler("chart", project.chart))
    application.add_handler(CommandHandler("holders", project.holders))
    application.add_handler(CommandHandler("liquidity", project.liquidity))
    application.add_handler(CommandHandler(["mcap", "marketcap"], project.mcap))
    application.add_handler(CommandHandler("price", project.price))
    application.add_handler(CommandHandler(["tax", "slippage"], project.tax))
    application.add_handler(CommandHandler("twitter", project.twitter))
    application.add_handler(CommandHandler("wallet", project.wallet))
    application.add_handler(CommandHandler(["website", "site"], project.website))

    application.add_handler(CommandHandler("ascii", utility.ascii))
    application.add_handler(CommandHandler("blocks", utility.blocks))
    application.add_handler(CommandHandler("bridge", utility.bridge))
    application.add_handler(CommandHandler("coinflip", utility.coinflip))
    application.add_handler(CommandHandler("check", utility.check_input))
    application.add_handler(CommandHandler("fact", utility.fact))
    application.add_handler(CommandHandler("fg", utility.fg))
    application.add_handler(CommandHandler("gas", utility.gas))
    application.add_handler(CommandHandler("joke", utility.joke))
    application.add_handler(CommandHandler("quote", utility.quote))
    application.add_handler(CommandHandler("roll", utility.roll))
    application.add_handler(CommandHandler("say", utility.say))
    application.add_handler(CommandHandler("time", utility.time))
    application.add_handler(CommandHandler("timestamp", utility.timestamp_command))
    application.add_handler(CommandHandler("today", utility.today))
    application.add_handler(CommandHandler("wei", utility.wei))
    application.add_handler(CommandHandler("word", utility.word))

#    job_queue.run_once(
#        auto_message_click,
#        constants.FIRST_BUTTON_TIME,
#        chat_id=constants.TELEGRAM_CHANNEL_ID,
#        name="Click Message",
#    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)