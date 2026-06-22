import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from quiz_app.Application.api.game import start_game
from quiz_app.service.user_service import get_one_user_active
from quiz_app.service.profile_service import get_user_lang, get_user_profile, get_rating

from quiz_app.locales.messages import msg

async def users_keyboard_handler(update, context):
    data = update.message.text
    user = update.effective_user
    lang = get_user_lang(user.id)

    status = get_one_user_active(user.id)[0]
    active_status = bool(status)

    if data == f"🎮 {msg(lang, 'start_game')}":
        if active_status:
            asyncio.create_task(start_game(update, user, context))

            await update.message.delete()

        else:
            await update.message.delete()
            mssg = await update.message.reply_text(text=f"🔴 {msg(lang, 'you_inactive')}!")
            await asyncio.sleep(3)
            await mssg.delete()

    elif data == f"🏆 {msg(lang, 'rating')}":
        close_button = [[InlineKeyboardButton(text=f"{msg(lang, 'close')}", callback_data="game:close")]]
        await update.message.reply_text(text=get_rating(user.id), reply_markup=InlineKeyboardMarkup(close_button))
        await update.message.delete()

    elif data == f"👤 {msg(lang, 'profile')}":
        close_button = [[InlineKeyboardButton(text=f"{msg(lang, 'close')}", callback_data="game:close")]]
        await update.message.reply_text(text=get_user_profile(user.id), reply_markup=InlineKeyboardMarkup(close_button))
        await update.message.delete()

    else:
        await update.message.delete()