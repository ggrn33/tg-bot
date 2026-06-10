import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

DIKIDI_URL = "https://dikidi.ru/1143469"

MAPS_URL = "https://yandex.ru/maps/org/body_aesthetics_club/150933116041/?ll=42.049249%2C55.578045&z=16"
PHONE = "+79038322021"

main_keyboard = ReplyKeyboardMarkup(
    [["🛎 Услуги", "📅 Запись"],
     ["📞 Связаться с нами", "🗺 Как добраться?"]],
    resize_keyboard=True
)

# ─── Категории услуг ──────────────────────────────────────────────────────────
SERVICES = {
    "massage": {
        "name": "💆 Ручной массаж",
        "items": [
            ("Классический массаж всего тела", "1 час", "2 000"),
            ("Классический массаж спины без ш/в зоны", "25 мин", "1 400"),
            ("Классический массаж спины с ш/в зоной", "40 мин", "1 600"),
            ("Расслабляющий массаж всего тела", "1 час", "1 800"),
            ("Расслабляющий массаж спины", "40 мин", "1 500"),
            ("Расслабляющий массаж тела + проработка стоп и головы", "1 ч 30 мин", "2 200"),
            ("Расслабляющий массаж тела + массаж лица (маска)", "2 ч 30 мин", "3 700"),
            ("Лечебный массаж всего тела", "1 час", "2 000"),
            ("Лечебный массаж спины с ш/в зоной", "40 мин", "1 500"),
            ("Массаж стоп и голеней", "45 мин", "1 000"),
            ("Массаж стоп", "30 мин", "700"),
            ("Индийский массаж с тёплыми маслами", "2 часа", "3 000"),
            ("Тайский массаж", "2 часа", "3 000"),
            ("Стоун-массаж тела", "1 час", "2 500"),
            ("Стоун-массаж тела и лица", "1 ч 30 мин", "3 000"),
            ("Лимфодренажный массаж всего тела", "1 ч 30 мин", "2 000"),
            ("Лечебный массаж лица", "30 мин", "1 000"),
        ]
    },
    "anticellulite": {
        "name": "🍊 Антицеллюлитный массаж",
        "items": [
            ("Антицеллюлитный массаж всего тела", "1 ч 20 мин", "2 000"),
            ("Антицеллюлитный массаж бёдра/ягодицы", "40 мин", "1 400"),
            ("Антицеллюлитный массаж живот/бока", "40 мин", "1 400"),
            ("Антицеллюлитный одной зоны + обёртывание", "1 час", "1 700"),
        ]
    },
    "hardware": {
        "name": "⚡ Аппаратный массаж",
        "items": [
            ("LPG все тело", "40 мин", "1 400"),
            ("LPG 1 зона", "25 мин", "1 000"),
            ("Вибромассаж все тело", "40 мин", "1 400"),
            ("Вибромассаж 1 зона", "25 мин", "1 000"),
            ("Вибро массаж по обёртыванию", "1 ч 10 мин", "2 000"),
            ("Массаж горячим вакуумом все тело", "1 час", "1 500"),
            ("Массаж горячим вакуумом 1 зона", "30 мин", "1 000"),
            ("Протокол", "1 ч 30 мин", "1 500"),
        ]
    },
    "spa": {
        "name": "🌿 SPA-программы",
        "items": [
            ("Расслабляющий массаж тела + массаж лица", "2 часа", "3 300"),
            ("Бандажное обёртывание", "1 час", "1 700"),
            ("Обёртывание", "1 час", "1 000"),
            ("Фитобочка", "25 мин", "700"),
            ("SPA-программа + массаж спины", "2 часа", "5 000"),
            ("SPA-программа + расслабляющий массаж всего тела", "2 ч 20 мин", "5 300"),
            ("Яркий цитрус", "1 ч 30 мин", "3 500"),
            ("Сочный манго", "1 ч 30 мин", "3 500"),
            ("Шоколадный соблазн", "1 ч 30 мин", "3 500"),
            ("Антицеллюлитная", "1 ч 30 мин", "3 500"),
        ]
    },
    "depilation": {
        "name": "🪷 Депиляция (сахара/воск)",
        "items": [
            ("Комплекс L (бикини, подмышки, ноги полн., руки полн.)", "2 ч 10 мин", "3 800"),
            ("Комплекс M (бикини, подмышки, ноги полностью)", "1 ч 40 мин", "3 000"),
            ("Комплекс S (бикини, подмышки, голени)", "1 ч 10 мин", "2 500"),
            ("Бёдра", "40 мин", "900"),
            ("Бикини глубокое", "40 мин", "1 400"),
            ("Классическое бикини", "30 мин", "600"),
            ("Бикини среднее", "40 мин", "900"),
            ("Ноги полностью", "1 ч 5 мин", "1 500"),
            ("Руки полностью", "40 мин", "800"),
            ("Руки до локтя", "25 мин", "600"),
            ("Подмышечные впадины", "20 мин", "400"),
            ("Зоны лица", "20 мин", "от 300"),
            ("Живот", "25 мин", "от 300"),
            ("Голени", "1 час", "900"),
        ]
    },
    "cosmetology": {
        "name": "✨ Косметология",
        "items": [
            ("Мезотерапия головы", "30 мин", "2 000"),
            ("Чистка лица Анти Акне с пилингом", "2 часа", "4 000"),
            ("Peach Peel (Персиковый пилинг)", "1 час", "3 500"),
            ("Pink Peel (Розовый пилинг)", "1 час", "2 700"),
            ("Моделирующий массаж 3D Эфлераж-Дренаж", "1 час", "2 300"),
            ("Альгинатная маска", "30 мин", "от 700"),
            ("Экспресс уход «Фарфоровая Куколка»", "1 ч 30 мин", "2 500"),
            ("Атравматическая чистка", "1 ч 30 мин", "2 500"),
            ("Атравматическая чистка с азелоиновым пилингом", "1 ч 30 мин", "3 500"),
            ("Массаж Гуа Ша", "1 час", "1 700"),
            ("Карбокситерапия", "1 ч 30 мин", "2 500"),
            ("Карбокситерапия+пилинг", "2 часа", "3 500"),
            ("Карбокситерапия+альгинатная маска", "2 часа", "3 000"),
            ("Пилинг Азелоиновый от Angiopharm", "45 мин", "2 500"),
            ("Феруловый пилинг от ANGIOPHARM", "40 мин", "2 500"),
            ("АНА-пилинг с пировиноградной кислотой от ANGIOPHARM", "40 мин", "2 500"),
            ("Всесезонный пилинг BioRePeel CL3", "40 мин", "2 500"),
            ("Уходовая программа «Лепесток лотоса»", "1 ч 30 мин", "2 500"),
            ("Уходовая программа «Дыхание кожи»", "1 ч 30 мин", "2 500"),
            ("Уходовая программа «Магия молодости»", "2 часа", "3 500"),
        ]
    },
    "hardware_cosmetology": {
        "name": "🔬 Аппаратная косметология",
        "items": [
            ("Микротоки", "1 час", "1 800"),
            ("LPG массаж лица", "1 час", "1 300"),
            ("Вакуумный массаж лица", "1 час", "1 600"),
            ("Микроигольчатый Rf-лифтинг (лицо)", "1 час", "от 7 000"),
            ("Микроигольчатый Rf-лифтинг (декольте)", "1 час", "6 000"),
            ("Микроигольчатый Rf-лифтинг (зона)", "40 мин", "4 000"),
            ("Микроигольчатый Rf-лифтинг (тело)", "1 час", "от 5 000"),
        ]
    },
}

MASTERS = [
    ("💆 Никотин Александр", "Мастер ручного массажа"),
    ("💅 Зайцева Юлия", "Мастер по депиляции"),
    ("💆 Устинова Анастасия", "Мастер ручного и аппаратного массажа"),
    ("⚡ Ткачёва Оксана", "Мастер аппаратного массажа"),
    ("✨ Лексина Анастасия", "Мастер"),
    ("🌸 Порхачёва Екатерина", "Косметолог-эстетист"),
    ("⭐ Гагаринская Марина", "Старший мастер"),
]

# ─── Команды ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"Добро пожаловать в <b>Body Aesthetics Club</b>!\n\n"
        f"Выбери что тебя интересует 👇"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>📚 Помощь</b>\n\n"
        "• 🛎 <b>Услуги</b> — каталог услуг по категориям\n"
        "• 📅 <b>Запись</b> — записаться к мастеру онлайн\n\n"
        "По любым вопросам пиши нам!",
        parse_mode="HTML", reply_markup=main_keyboard
    )

# ─── Кнопки ───────────────────────────────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛎 Услуги":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in SERVICES.items()
        ])
        await update.message.reply_text(
            "Выбери категорию услуг 👇",
            reply_markup=keyboard
        )

    elif text == "📅 Запись":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{name} — {role}", callback_data=f"master_{i}")]
            for i, (name, role) in enumerate(MASTERS)
        ] + [[InlineKeyboardButton("📅 Записаться (выбрать самому)", url=DIKIDI_URL)]])
        await update.message.reply_text(
            "📅 <b>Запись к мастеру</b>\n\nВыбери мастера или запишись самостоятельно 👇",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif text == "📞 Связаться с нами":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✈️ Написать в Telegram", url="https://t.me/+79038322021")],
        ])
        await update.message.reply_text(
            "📞 <b>Связаться с нами</b>\n\n"
            "📱 Телефон: <b>8 903 832 20 21</b>\n\n"
            "Позвони нам или напиши в Telegram 👇",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    elif text == "🗺 Как добраться?":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺 Открыть в Яндекс Картах", url=MAPS_URL)]
        ])
        await update.message.reply_text(
            "🗺 <b>Как добраться?</b>\n\nНажми кнопку ниже — откроется маршрут в Яндекс Картах 👇",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    else:
        await update.message.reply_text(
            "Используй кнопки внизу 👇",
            reply_markup=main_keyboard
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cat_"):
        key = data[4:]
        cat = SERVICES[key]
        lines = [f"<b>{cat['name']}</b>\n"]
        for name, duration, price in cat["items"]:
            lines.append(f"• {name}\n  ⏱ {duration} | 💰 {price} руб.")
        text = "\n".join(lines)
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
            [InlineKeyboardButton("◀️ Назад к категориям", callback_data="back_cats")],
        ])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard)

    elif data == "back_cats":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in SERVICES.items()
        ])
        await query.edit_message_text("Выбери категорию услуг 👇", reply_markup=keyboard)

    elif data.startswith("master_"):
        idx = int(data[7:])
        name, role = MASTERS[idx]
        await query.edit_message_text(
            f"<b>{name}</b>\n{role}\n\nНажми кнопку ниже чтобы записаться 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
                [InlineKeyboardButton("◀️ Назад к мастерам", callback_data="back_masters")]
            ])
        )

    elif data == "back_masters":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{name} — {role}", callback_data=f"master_{i}")]
            for i, (name, role) in enumerate(MASTERS)
        ] + [[InlineKeyboardButton("📅 Записаться (выбрать самому)", url=DIKIDI_URL)]])
        await query.edit_message_text(
            "📅 <b>Запись к мастеру</b>\n\nВыбери мастера 👇",
            parse_mode="HTML",
            reply_markup=keyboard
        )

# ─── Запуск ───────────────────────────────────────────────────────────────────
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Бот запущен.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
