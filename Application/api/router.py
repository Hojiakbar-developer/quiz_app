from quiz_app.service.user_service import is_admin
from admin_panel import admin_start_command, admin_keyboard_handler, admin_query_router
from handlers.commands import users_start_command
from handlers.messages import users_keyboard_handler
from handlers.queries import (game_query_handler, start_language_query_handler,
                              change_language_query_handler)

async def start_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        await admin_start_command(update, context)
        return

    await users_start_command(update, context)
    return

async def keyboard_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        await admin_keyboard_handler(update, context)
        return

    await users_keyboard_handler(update, context)
    return

async def query_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        await admin_query_router(update, context)
        return

    await users_query_router(update, context)
    return

async def users_query_router(update, context):
    query = update.callback_query
    user = update.effective_user

    parts = query.data.split(":")

    prefix = parts[0]
    data = parts[1]

    if prefix == "game":
        await game_query_handler(query, data, user, context)
        return

    elif prefix == "start_language":
        await start_language_query_handler(query, data, user)

    elif prefix == "change_language":
        await change_language_query_handler(query, data, user)