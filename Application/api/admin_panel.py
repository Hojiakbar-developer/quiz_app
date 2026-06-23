from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from quiz_app.service.user_service import (deactivate_user, reactivate_user,
                                           get_all_users, get_users_active,
                                           get_one_user_active, get_users_list,
                                           greet)
from quiz_app.service.profile_service import get_users_profiles
from quiz_app.service.game_service import (get_active_plays, view_user_answers,
                                           get_sessions_list, get_viewer_mode, user_answers_by_id)
from quiz_app.service.user_service import get_user_by_id, register_user

async def admin_start_command(update, context):
    admin_id = update.effective_user.id
    first_name = update.effective_user.first_name
    user_name = update.effective_user.username
    keyboards = main_keyboards()

    admin = get_user_by_id(admin_id)

    if not admin:
        register_user(admin_id, first_name, user_name, "en")

    await update.message.reply_text(text=f"{greet('en')}, Sir.\nWe are ready!",
                              reply_markup=ReplyKeyboardMarkup(keyboards,
                                                               resize_keyboard=True))

async def admin_keyboard_handler(update, context):
    data = update.message.text

    if data == "Control Users":
        users = get_users_list()
        buttons = control_users_buttons()

        await update.message.reply_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.delete()

    elif data == "🌐 Viewer Mode":
        active_players = get_viewer_mode()
        viewer_buttons = get_viewer_mode_buttons()

        await update.message.reply_text(text=active_players, reply_markup=InlineKeyboardMarkup(viewer_buttons))
        await update.message.delete()

    elif data == "📜 History":
        keyboards = history_buttons()

        await update.message.reply_text(text="📜 History", reply_markup=InlineKeyboardMarkup(keyboards))
        await update.message.delete()

    elif data == "👤 Profiles":
        close_button = [[InlineKeyboardButton(text="Close", callback_data="profile:close")]]

        await update.message.reply_text(text=get_users_profiles(), reply_markup=InlineKeyboardMarkup(close_button))
        await update.message.delete()

    else:
        await update.message.delete()

async def admin_query_router(update, context):
    query = update.callback_query

    parts = query.data.split(":")

    prefix = parts[0]
    data = parts[1]

    if prefix == "control":
        await control_users_query_handler(query, data)
        return

    elif prefix == "history":
        await history_query_handler(query, data)
        return

    elif prefix == "viewer_mode":
        await viewer_mode_query_handler(query, data)
        return

    elif prefix == "profile":
        await profiles_query_handler(query, data)
        return

async def control_users_query_handler(query, data):

    if data == "deactivate":
        users = get_users_list()
        buttons = control_users_id_buttons("control", "deactivate_")

        await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "reactivate":
        users = get_users_list()
        buttons = control_users_id_buttons("control", "reactivate_")

        await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif "deactivate_" in data:
        user_id = int(data.strip("deactivate_"))
        actives = get_users_active()

        for uid, active in actives:
            if user_id == uid:
                deactivate_user(user_id)

                users = get_users_list()
                buttons = control_users_id_buttons("control", "deactivate_")

                await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif "reactivate_" in data:
        user_id = int(data.strip("reactivate_"))
        inactives = get_users_active()

        for uid, active in inactives:
            if user_id == uid:
                reactivate_user(user_id)

                users = get_users_list()
                buttons = control_users_id_buttons("control", "reactivate_")

                await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "back":
        users = get_users_list()
        buttons = control_users_buttons()

        await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "close":
        await query.message.delete()

async def history_query_handler(query, data):

    if data == "all_users_sessions" or data == "refresh_sessions_list":
        sessions = get_sessions_list()
        back_button = [[InlineKeyboardButton(text="⬅️ Back", callback_data="history:back")]]

        await query.edit_message_text(text=sessions, reply_markup=InlineKeyboardMarkup(back_button))

    elif data == "one_user_answers":
        users = get_users_list()
        buttons = history_users_id_buttons()

        await query.message.reply_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))
        await query.message.delete()

    elif "one_user_answers_" in data:
        user_id = int(data.strip("one_user_answers_"))
        answers = user_answers_by_id(user_id)

        back_button = [[InlineKeyboardButton(text="⬅️ Back", callback_data="history:back_users_id")]]

        await query.edit_message_text(text=answers, reply_markup=InlineKeyboardMarkup(back_button))

    elif data == "back_users_id":
        users = get_users_list()
        buttons = history_users_id_buttons()

        await query.edit_message_text(text=users, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "back":
        buttons = history_buttons()

        await query.edit_message_text(text="📜 History", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "close":
        await query.message.delete()

async def viewer_mode_query_handler(query, data):

    if "view_" in data:
        session_id = int(data.strip("view_"))

        user_play = view_user_answers(session_id)
        buttons = viewer_user_answers_buttons(session_id)

        await query.edit_message_text(text=user_play, reply_markup=InlineKeyboardMarkup(buttons))

    elif "refresh_" in data:
        session_id = int(data.strip("refresh_"))
        user_play = view_user_answers(session_id)
        buttons = viewer_user_answers_buttons(session_id)

        await query.edit_message_text(text=user_play, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "back":
        active_players = get_viewer_mode()
        viewer_buttons = get_viewer_mode_buttons()

        await query.edit_message_text(text=active_players, reply_markup=InlineKeyboardMarkup(viewer_buttons))

    elif data == "close":
        await query.message.delete()

async def profiles_query_handler(query, data):

    if data == "close":
        await query.message.delete()

def main_keyboards():
    keyboards = [
        [KeyboardButton(text="Control Users"),
         KeyboardButton(text="📜 History")],
        [KeyboardButton(text="🌐 Viewer Mode"),
         KeyboardButton(text="👤 Profiles")]
    ]
    return keyboards

def control_users_buttons():
    buttons = [
        [InlineKeyboardButton(text="Deactivate", callback_data=f"control:deactivate"),
         InlineKeyboardButton(text="Reactivate", callback_data=f"control:reactivate")],
        [InlineKeyboardButton(text="Close", callback_data=f"control:close")]
    ]
    return buttons

def control_users_id_buttons(prefix, operation):
    users = get_all_users()

    inline_buttons = []
    row = []

    user = 0
    for uid, f_name, u_name, created_at in users:
        active = get_one_user_active(uid)[0]

        user += 1
        active = bool(active)

        if operation == "deactivate_":
            if active:
                row.append(InlineKeyboardButton(text=f"User {user}", callback_data=f"{prefix}:{operation}{uid}"))

        elif operation == "reactivate_":
            if not active:
                row.append(InlineKeyboardButton(text=f"User {user}", callback_data=f"{prefix}:{operation}{uid}"))

        if len(row) == 3:
            inline_buttons.append(row)
            row = []

    if row:
        inline_buttons.append(row)

    inline_buttons.append([InlineKeyboardButton(text="Back", callback_data=f"{prefix}:back")])

    return inline_buttons

def history_buttons():
    buttons = [
        [InlineKeyboardButton(text="Users Sessions", callback_data="history:all_users_sessions"),
         InlineKeyboardButton(text="Special User Answers", callback_data="history:one_user_answers")],
        [InlineKeyboardButton(text="Close", callback_data="history:close")]
    ]
    return buttons

def history_users_id_buttons():
    users = get_all_users()

    inline_buttons = []
    row = []

    user = 0
    for uid, f_name, u_name, created_at in users:

        user += 1

        row.append(InlineKeyboardButton(text=f"User {user}", callback_data=f"history:one_user_answers_{uid}"))

        if len(row) == 3:
            inline_buttons.append(row)
            row = []

    if row:
        inline_buttons.append(row)

    inline_buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data=f"history:back")])

    return inline_buttons

def get_viewer_mode_buttons():
    active_players = get_active_plays()

    buttons = []
    row = []

    for sess_id, us_id, r_name, u_name in active_players:

        row.append(InlineKeyboardButton(text=f"Session {sess_id}", callback_data=f"viewer_mode:view_{sess_id}"))

        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="Close", callback_data="viewer_mode:close")])

    return buttons

def viewer_user_answers_buttons(session_id):
    buttons = [
        [InlineKeyboardButton(text="🔄️ Refresh", callback_data=f"viewer_mode:refresh_{session_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="viewer_mode:back")]
    ]
    return buttons