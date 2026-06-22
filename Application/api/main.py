from telegram.ext import (
    Application, filters, MessageHandler,
    CallbackQueryHandler, CommandHandler)

from router import start_router, query_router, keyboard_router
from handlers.commands import change_lang_command_handler
from quiz_app.config import API_TOKEN

if not API_TOKEN:
    raise ValueError("Not found API KEY in .env file")

def main():
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start_router))
    app.add_handler(CommandHandler("changelang", change_lang_command_handler))
    app.add_handler(CallbackQueryHandler(query_router))
    app.add_handler(MessageHandler(filters.TEXT, keyboard_router))

    app.run_polling()

if __name__ == '__main__':
    main()