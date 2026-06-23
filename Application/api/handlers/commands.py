from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from quiz_app.service.user_service import get_user_by_id, greet
from quiz_app.service.profile_service import get_user_lang

from quiz_app.locales.messages import msg

async def users_start_command(update, context):
    user_id = update.effective_user.id
    real_name = update.effective_user.first_name

    user = get_user_by_id(user_id)

    if user:
        lang = get_user_lang(user_id)
        keyboards = main_keyboards(lang)

        await update.message.reply_text(text=f"{greet(lang)}, {real_name}", reply_markup=ReplyKeyboardMarkup(keyboards,
                                                                                                   resize_keyboard=True))
        return

    await update.message.reply_text(text=f"{greet('en')}, {real_name}"
                                         f"\nWhich language?",
                                    reply_markup=InlineKeyboardMarkup(language_buttons("start_language", "en")))

# async def change_lang_command_handler(update, context):
#     user = update.effective_user
#     lang = get_user_lang(user.id)
#
#     buttons = language_buttons("change_language", lang)
#
#     cancel_button = [InlineKeyboardButton(text=f"{msg(lang, 'cancel')}", callback_data="change_language:cancel")]
#     buttons.append(cancel_button)
#
#     await update.message.reply_text(text=f"{msg(lang, 'which_lang')}?", reply_markup=InlineKeyboardMarkup(buttons))
#     await update.message.delete()

def main_keyboards(lang):
    keyboards = [
        [KeyboardButton(text=f"🎮 {msg(lang, 'start_game')}"),
         KeyboardButton(text=f"🏆 {msg(lang, 'rating')}")],
        [KeyboardButton(text=f"👤 {msg(lang, 'profile')}"),
         KeyboardButton(text=f"⚙️ {msg(lang, 'settings')}")]
    ]
    return keyboards

def language_buttons(prefix, lang):
    buttons = [
        [InlineKeyboardButton(text=f"{msg(lang, 'english')}", callback_data=f"{prefix}:en"),
         InlineKeyboardButton(text=f"{msg(lang, 'uzbek')}", callback_data=f"{prefix}:uz")]
    ]
    return buttons