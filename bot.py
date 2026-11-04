"""ESN Telegram bot starter (python-telegram-bot v21). MIT License. https://esnoffical.com"""
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)  # keeps your token out of the request logs
log = logging.getLogger("esn-telegram-bot")

HELP_TEXT = (
    "<b>Commands</b>\n"
    "/start - say hi and show the menu\n"
    "/help - this message\n"
    "/menu - inline keyboard example\n\n"
    "Send me any text and I'll echo it back."
)


def menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👋 Say hi", callback_data="hi"), InlineKeyboardButton("🎲 Roll a dice", callback_data="dice")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🌐 ESN Hosting", url="https://esnoffical.com")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name if update.effective_user else "there"
    await update.message.reply_text(f"Hey {name}! 👋 I'm your new bot. Pick something:", reply_markup=menu_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Here's the menu:", reply_markup=menu_keyboard())


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # stops the loading spinner on the button
    if query.data == "hi":
        await query.edit_message_text(f"Hi {query.from_user.first_name}! 😄", reply_markup=menu_keyboard())
    elif query.data == "dice":
        await context.bot.send_dice(chat_id=query.message.chat_id)
    elif query.data == "about":
        await query.edit_message_text(
            "Built with python-telegram-bot. Edit bot.py to add your own commands.",
            reply_markup=menu_keyboard(),
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Error while handling an update: %s", context.error)


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(on_error)
    return app


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env first.")
    log.info("Starting bot (long polling). Press Ctrl+C to stop.")
    build_app(TOKEN).run_polling(allowed_updates=Update.ALL_TYPES)
