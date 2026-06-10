import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Главная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    [["🛎 Услуги", "📅 Запись"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"Выбери что тебя интересует:"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📚 Помощь</b>\n\n"
        "Доступные команды:\n"
        "• /start — запустить бота\n"
        "• /help  — показать это сообщение\n\n"
        "Или используй кнопки внизу экрана."
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛎 Услуги":
        await update.message.reply_text(
            "🛎 <b>Наши услуги:</b>\n\n"
            "• Услуга 1\n"
            "• Услуга 2\n"
            "• Услуга 3\n\n"
            "Напиши нам для подробностей!",
            parse_mode="HTML",
            reply_markup=main_keyboard
        )

    elif text == "📅 Запись":
        await update.message.reply_text(
            "📅 <b>Запись:</b>\n\n"
            "Чтобы записаться, напиши своё имя и удобное время.\n\n"
            "Мы свяжемся с тобой в ближайшее время!",
            parse_mode="HTML",
            reply_markup=main_keyboard
        )

    else:
        await update.message.reply_text(
            f"💬 Ты написал: <i>{text}</i>\n\nИспользуй кнопки внизу 👇",
            parse_mode="HTML",
            reply_markup=main_keyboard
        )

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("🤖 Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
