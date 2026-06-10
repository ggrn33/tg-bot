import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Commands ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"Я твой Telegram-бот. Вот что я умею:\n\n"
        f"📌 /start — показать это сообщение\n"
        f"❓ /help  — помощь\n\n"
        f"Просто напиши мне любое сообщение!"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📚 Помощь</b>\n\n"
        "Доступные команды:\n"
        "• /start — запустить бота\n"
        "• /help  — показать это сообщение\n\n"
        "Ты также можешь просто <b>написать любой текст</b> — я отвечу!"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = (
        f"💬 Ты написал:\n<i>{text}</i>\n\n"
        f"Эхо от бота! Используй /help чтобы увидеть команды."
    )
    await update.message.reply_text(reply, parse_mode="HTML")


async def unknown_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📎 Я получил твой файл/медиа, но пока умею обрабатывать только текст."
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден. Добавь его в переменные окружения.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(~filters.TEXT, unknown_media))

    print("🤖 Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
