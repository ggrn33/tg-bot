import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

DIKIDI_URL = "https://dikidi.ru/1143469"
PHONE = "+79038322021"
MAPS_URL = "https://yandex.ru/maps/org/body_aesthetics_club/150933116041/?ll=42.049249%2C55.578045&z=16"
ADMIN_IDS = [7110293336]

# ─── Состояния для ConversationHandler ────────────────────────────────────────
WAIT_MASTER_NAME, WAIT_MASTER_ROLE, WAIT_DEL_MASTER = range(3)

# ─── Данные (загружаются из файла или дефолтные) ──────────────────────────────
DEFAULT_MASTERS = [
    {"name": "💆 Никотин Александр", "role": "Мастер ручного массажа"},
    {"name": "💅 Зайцева Юлия", "role": "Мастер по депиляции"},
    {"name": "💆 Устинова Анастасия", "role": "Мастер ручного и аппаратного массажа"},
    {"name": "⚡ Ткачёва Оксана", "role": "Мастер аппаратного массажа"},
    {"name": "✨ Лексина Анастасия", "role": "Мастер"},
    {"name": "🌸 Порхачёва Екатерина", "role": "Косметолог-эстетист"},
    {"name": "⭐ Гагаринская Марина", "role": "Старший мастер"},
]

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"masters": DEFAULT_MASTERS}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Клавиатуры ───────────────────────────────────────────────────────────────
main_keyboard = ReplyKeyboardMarkup(
    [["🛎 Услуги", "📅 Запись"],
     ["📞 Связаться с нами", "🗺 Как добраться?"]],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    [["👨‍💼 Мастера", "📊 Статистика"],
     ["🔙 Выйти из админки"]],
    resize_keyboard=True
)

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

# ─── Счётчик статистики ───────────────────────────────────────────────────────
stats = {"users": set(), "messages": 0}

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ─── Основные команды ─────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats["users"].add(update.effective_user.id)
    stats["messages"] += 1
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, <b>{name}</b>!\n\nДобро пожаловать в <b>Body Aesthetics Club</b>!\n\nВыбери что тебя интересует 👇",
        parse_mode="HTML", reply_markup=main_keyboard
    )

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ У тебя нет доступа к админ-панели.")
        return
    await update.message.reply_text(
        "🔐 <b>Админ-панель</b>\n\nДобро пожаловать! Выбери раздел 👇",
        parse_mode="HTML", reply_markup=admin_keyboard
    )

# ─── Обработка кнопок ─────────────────────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    stats["messages"] += 1
    stats["users"].add(user_id)

    # ── Админ-кнопки ──
    if text == "👨‍💼 Мастера" and is_admin(user_id):
        data = load_data()
        masters = data["masters"]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"❌ {m['name']}", callback_data=f"delmaster_{i}")]
             for i, m in enumerate(masters)] +
            [[InlineKeyboardButton("➕ Добавить мастера", callback_data="addmaster")]]
        )
        text_out = "<b>👨‍💼 Мастера</b>\n\nНажми ❌ чтобы удалить или добавь нового 👇\n\n"
        for m in masters:
            text_out += f"• {m['name']} — {m['role']}\n"
        await update.message.reply_text(text_out, parse_mode="HTML", reply_markup=keyboard)
        return

    if text == "📊 Статистика" and is_admin(user_id):
        await update.message.reply_text(
            f"📊 <b>Статистика бота</b>\n\n"
            f"👥 Уникальных пользователей: <b>{len(stats['users'])}</b>\n"
            f"💬 Всего сообщений: <b>{stats['messages']}</b>",
            parse_mode="HTML", reply_markup=admin_keyboard
        )
        return

    if text == "🔙 Выйти из админки" and is_admin(user_id):
        await update.message.reply_text("Вышел из админки 👋", reply_markup=main_keyboard)
        return

    # ── Обычные кнопки ──
    if text == "🛎 Услуги":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in SERVICES.items()
        ])
        await update.message.reply_text("Выбери категорию услуг 👇", reply_markup=keyboard)

    elif text == "📅 Запись":
        data = load_data()
        masters = data["masters"]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"{m['name']} — {m['role']}", callback_data=f"master_{i}")]
             for i, m in enumerate(masters)] +
            [[InlineKeyboardButton("📅 Записаться (выбрать самому)", url=DIKIDI_URL)]]
        )
        await update.message.reply_text(
            "📅 <b>Запись к мастеру</b>\n\nВыбери мастера или запишись самостоятельно 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif text == "📞 Связаться с нами":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✈️ Написать в Telegram", url="https://t.me/+79038322021")],
        ])
        await update.message.reply_text(
            "📞 <b>Связаться с нами</b>\n\n"
            "📱 Телефон: <b>8 903 832 20 21</b>\n\n"
            "Позвони нам или напиши в Telegram 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif text == "🗺 Как добраться?":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺 Открыть в Яндекс Картах", url=MAPS_URL)]
        ])
        await update.message.reply_text(
            "🗺 <b>Как добраться?</b>\n\nНажми кнопку ниже — откроется маршрут в Яндекс Картах 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    else:
        await update.message.reply_text("Используй кнопки внизу 👇", reply_markup=main_keyboard)

# ─── Callback обработчики ─────────────────────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("cat_"):
        key = data[4:]
        cat = SERVICES[key]
        lines = [f"<b>{cat['name']}</b>\n"]
        for name, duration, price in cat["items"]:
            lines.append(f"• {name}\n  ⏱ {duration} | 💰 {price} руб.")
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
            [InlineKeyboardButton("◀️ Назад к категориям", callback_data="back_cats")],
        ])
        await query.edit_message_text("\n".join(lines), parse_mode="HTML", reply_markup=back_keyboard)

    elif data == "back_cats":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in SERVICES.items()
        ])
        await query.edit_message_text("Выбери категорию услуг 👇", reply_markup=keyboard)

    elif data.startswith("master_"):
        idx = int(data[7:])
        masters = load_data()["masters"]
        m = masters[idx]
        await query.edit_message_text(
            f"<b>{m['name']}</b>\n{m['role']}\n\nНажми кнопку ниже чтобы записаться 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
                [InlineKeyboardButton("◀️ Назад к мастерам", callback_data="back_masters")]
            ])
        )

    elif data == "back_masters":
        masters = load_data()["masters"]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"{m['name']} — {m['role']}", callback_data=f"master_{i}")]
             for i, m in enumerate(masters)] +
            [[InlineKeyboardButton("📅 Записаться (выбрать самому)", url=DIKIDI_URL)]]
        )
        await query.edit_message_text(
            "📅 <b>Запись к мастеру</b>\n\nВыбери мастера 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif data == "addmaster" and is_admin(user_id):
        context.user_data["adding_master"] = True
        await query.edit_message_text(
            "➕ <b>Добавление мастера</b>\n\nВведи имя мастера (например: Иванова Мария):",
            parse_mode="HTML"
        )
        return WAIT_MASTER_NAME

    elif data.startswith("delmaster_") and is_admin(user_id):
        idx = int(data[10:])
        db = load_data()
        removed = db["masters"].pop(idx)
        save_data(db)
        await query.edit_message_text(
            f"✅ Мастер <b>{removed['name']}</b> удалён.",
            parse_mode="HTML"
        )

# ─── ConversationHandler для добавления мастера ───────────────────────────────
async def wait_master_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_master_name"] = update.message.text
    await update.message.reply_text("Теперь введи должность (например: Мастер ручного массажа):")
    return WAIT_MASTER_ROLE

async def wait_master_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("new_master_name", "")
    role = update.message.text
    db = load_data()
    db["masters"].append({"name": name, "role": role})
    save_data(db)
    await update.message.reply_text(
        f"✅ Мастер <b>{name}</b> — {role} добавлен!",
        parse_mode="HTML", reply_markup=admin_keyboard
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=admin_keyboard)
    return ConversationHandler.END

# ─── Запуск ───────────────────────────────────────────────────────────────────
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден.")

    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern="^addmaster$")],
        states={
            WAIT_MASTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, wait_master_name)],
            WAIT_MASTER_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wait_master_role)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("🤖 Бот запущен.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
