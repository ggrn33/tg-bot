import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes, ConversationHandler)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

DIKIDI_URL = "https://dikidi.ru/1143469"
PHONE = "+79038322021"
MAPS_URL = "https://yandex.ru/maps/org/body_aesthetics_club/150933116041/?ll=42.049249%2C55.578045&z=16"
ADMIN_IDS = [7110293336]

# ─── Состояния ────────────────────────────────────────────────────────────────
(WAIT_MASTER_NAME, WAIT_MASTER_ROLE,
 WAIT_SERVICE_NAME, WAIT_SERVICE_DURATION, WAIT_SERVICE_PRICE,
 WAIT_EDIT_CHOICE, WAIT_EDIT_VALUE) = range(7)

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "masters": [
        {"name": "💆 Никотин Александр", "role": "Мастер ручного массажа"},
        {"name": "💅 Зайцева Юлия", "role": "Мастер по депиляции"},
        {"name": "💆 Устинова Анастасия", "role": "Мастер ручного и аппаратного массажа"},
        {"name": "⚡ Ткачёва Оксана", "role": "Мастер аппаратного массажа"},
        {"name": "✨ Лексина Анастасия", "role": "Мастер"},
        {"name": "🌸 Порхачёва Екатерина", "role": "Косметолог-эстетист"},
        {"name": "⭐ Гагаринская Марина", "role": "Старший мастер"},
    ],
    "services": {
        "massage": {"name": "💆 Ручной массаж", "items": [
            ["Классический массаж всего тела", "1 час", "2 000"],
            ["Классический массаж спины без ш/в зоны", "25 мин", "1 400"],
            ["Классический массаж спины с ш/в зоной", "40 мин", "1 600"],
            ["Расслабляющий массаж всего тела", "1 час", "1 800"],
            ["Расслабляющий массаж спины", "40 мин", "1 500"],
            ["Расслабляющий массаж тела + проработка стоп и головы", "1 ч 30 мин", "2 200"],
            ["Расслабляющий массаж тела + массаж лица (маска)", "2 ч 30 мин", "3 700"],
            ["Лечебный массаж всего тела", "1 час", "2 000"],
            ["Лечебный массаж спины с ш/в зоной", "40 мин", "1 500"],
            ["Массаж стоп и голеней", "45 мин", "1 000"],
            ["Массаж стоп", "30 мин", "700"],
            ["Индийский массаж с тёплыми маслами", "2 часа", "3 000"],
            ["Тайский массаж", "2 часа", "3 000"],
            ["Стоун-массаж тела", "1 час", "2 500"],
            ["Стоун-массаж тела и лица", "1 ч 30 мин", "3 000"],
            ["Лимфодренажный массаж всего тела", "1 ч 30 мин", "2 000"],
            ["Лечебный массаж лица", "30 мин", "1 000"],
        ]},
        "anticellulite": {"name": "🍊 Антицеллюлитный массаж", "items": [
            ["Антицеллюлитный массаж всего тела", "1 ч 20 мин", "2 000"],
            ["Антицеллюлитный массаж бёдра/ягодицы", "40 мин", "1 400"],
            ["Антицеллюлитный массаж живот/бока", "40 мин", "1 400"],
            ["Антицеллюлитный одной зоны + обёртывание", "1 час", "1 700"],
        ]},
        "hardware": {"name": "⚡ Аппаратный массаж", "items": [
            ["LPG все тело", "40 мин", "1 400"],
            ["LPG 1 зона", "25 мин", "1 000"],
            ["Вибромассаж все тело", "40 мин", "1 400"],
            ["Вибромассаж 1 зона", "25 мин", "1 000"],
            ["Вибро массаж по обёртыванию", "1 ч 10 мин", "2 000"],
            ["Массаж горячим вакуумом все тело", "1 час", "1 500"],
            ["Массаж горячим вакуумом 1 зона", "30 мин", "1 000"],
            ["Протокол", "1 ч 30 мин", "1 500"],
        ]},
        "spa": {"name": "🌿 SPA-программы", "items": [
            ["Расслабляющий массаж тела + массаж лица", "2 часа", "3 300"],
            ["Бандажное обёртывание", "1 час", "1 700"],
            ["Обёртывание", "1 час", "1 000"],
            ["Фитобочка", "25 мин", "700"],
            ["SPA-программа + массаж спины", "2 часа", "5 000"],
            ["SPA-программа + расслабляющий массаж всего тела", "2 ч 20 мин", "5 300"],
            ["Яркий цитрус", "1 ч 30 мин", "3 500"],
            ["Сочный манго", "1 ч 30 мин", "3 500"],
            ["Шоколадный соблазн", "1 ч 30 мин", "3 500"],
            ["Антицеллюлитная", "1 ч 30 мин", "3 500"],
        ]},
        "depilation": {"name": "🪷 Депиляция (сахара/воск)", "items": [
            ["Комплекс L (бикини, подмышки, ноги полн., руки полн.)", "2 ч 10 мин", "3 800"],
            ["Комплекс M (бикини, подмышки, ноги полностью)", "1 ч 40 мин", "3 000"],
            ["Комплекс S (бикини, подмышки, голени)", "1 ч 10 мин", "2 500"],
            ["Бёдра", "40 мин", "900"],
            ["Бикини глубокое", "40 мин", "1 400"],
            ["Классическое бикини", "30 мин", "600"],
            ["Бикини среднее", "40 мин", "900"],
            ["Ноги полностью", "1 ч 5 мин", "1 500"],
            ["Руки полностью", "40 мин", "800"],
            ["Руки до локтя", "25 мин", "600"],
            ["Подмышечные впадины", "20 мин", "400"],
            ["Зоны лица", "20 мин", "от 300"],
            ["Живот", "25 мин", "от 300"],
            ["Голени", "1 час", "900"],
        ]},
        "cosmetology": {"name": "✨ Косметология", "items": [
            ["Мезотерапия головы", "30 мин", "2 000"],
            ["Чистка лица Анти Акне с пилингом", "2 часа", "4 000"],
            ["Peach Peel (Персиковый пилинг)", "1 час", "3 500"],
            ["Pink Peel (Розовый пилинг)", "1 час", "2 700"],
            ["Моделирующий массаж 3D Эфлераж-Дренаж", "1 час", "2 300"],
            ["Альгинатная маска", "30 мин", "от 700"],
            ["Экспресс уход «Фарфоровая Куколка»", "1 ч 30 мин", "2 500"],
            ["Атравматическая чистка", "1 ч 30 мин", "2 500"],
            ["Атравматическая чистка с азелоиновым пилингом", "1 ч 30 мин", "3 500"],
            ["Массаж Гуа Ша", "1 час", "1 700"],
            ["Карбокситерапия", "1 ч 30 мин", "2 500"],
            ["Карбокситерапия+пилинг", "2 часа", "3 500"],
            ["Карбокситерапия+альгинатная маска", "2 часа", "3 000"],
            ["Пилинг Азелоиновый от Angiopharm", "45 мин", "2 500"],
            ["Феруловый пилинг от ANGIOPHARM", "40 мин", "2 500"],
            ["АНА-пилинг с пировиноградной кислотой от ANGIOPHARM", "40 мин", "2 500"],
            ["Всесезонный пилинг BioRePeel CL3", "40 мин", "2 500"],
            ["Уходовая программа «Лепесток лотоса»", "1 ч 30 мин", "2 500"],
            ["Уходовая программа «Дыхание кожи»", "1 ч 30 мин", "2 500"],
            ["Уходовая программа «Магия молодости»", "2 часа", "3 500"],
        ]},
        "hardware_cosmetology": {"name": "🔬 Аппаратная косметология", "items": [
            ["Микротоки", "1 час", "1 800"],
            ["LPG массаж лица", "1 час", "1 300"],
            ["Вакуумный массаж лица", "1 час", "1 600"],
            ["Микроигольчатый Rf-лифтинг (лицо)", "1 час", "от 7 000"],
            ["Микроигольчатый Rf-лифтинг (декольте)", "1 час", "6 000"],
            ["Микроигольчатый Rf-лифтинг (зона)", "40 мин", "4 000"],
            ["Микроигольчатый Rf-лифтинг (тело)", "1 час", "от 5 000"],
        ]},
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id in ADMIN_IDS

main_keyboard = ReplyKeyboardMarkup(
    [["🛎 Услуги", "📅 Запись"],
     ["📞 Связаться с нами", "🗺 Как добраться?"]],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    [["👨‍💼 Мастера", "🛎 Услуги (админ)"],
     ["📊 Статистика", "🔙 Выйти из админки"]],
    resize_keyboard=True
)

stats = {"users": set(), "messages": 0}

# ─── Команды ──────────────────────────────────────────────────────────────────
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

# ─── Обработка текстовых кнопок ───────────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    stats["messages"] += 1
    stats["users"].add(user_id)

    # ── Админ-кнопки ──
    if text == "👨‍💼 Мастера" and is_admin(user_id):
        await show_masters_admin(update, context)
        return

    if text == "🛎 Услуги (админ)" and is_admin(user_id):
        await show_services_admin_cats(update, context)
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
        db = load_data()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in db["services"].items()
        ])
        await update.message.reply_text("Выбери категорию услуг 👇", reply_markup=keyboard)

    elif text == "📅 Запись":
        db = load_data()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"{m['name']} — {m['role']}", callback_data=f"master_{i}")]
             for i, m in enumerate(db["masters"])] +
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
            "📞 <b>Связаться с нами</b>\n\n📱 Телефон: <b>8 903 832 20 21</b>\n\nПозвони или напиши в Telegram 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif text == "🗺 Как добраться?":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺 Открыть в Яндекс Картах", url=MAPS_URL)]
        ])
        await update.message.reply_text(
            "🗺 <b>Как добраться?</b>\n\nНажми кнопку ниже 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    else:
        await update.message.reply_text("Используй кнопки внизу 👇", reply_markup=main_keyboard)

# ─── Вспомогательные функции админки ─────────────────────────────────────────
async def show_masters_admin(update, context):
    db = load_data()
    masters = db["masters"]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"❌ {m['name']}", callback_data=f"delmaster_{i}")]
         for i, m in enumerate(masters)] +
        [[InlineKeyboardButton("➕ Добавить мастера", callback_data="addmaster")]]
    )
    text = "<b>👨‍💼 Мастера</b>\n\n"
    for m in masters:
        text += f"• {m['name']} — {m['role']}\n"
    text += "\nНажми ❌ чтобы удалить или ➕ чтобы добавить"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def show_services_admin_cats(update, context):
    db = load_data()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(v["name"], callback_data=f"admcat_{k}")]
        for k, v in db["services"].items()
    ])
    await update.message.reply_text(
        "🛎 <b>Управление услугами</b>\n\nВыбери категорию 👇",
        parse_mode="HTML", reply_markup=keyboard
    )

# ─── Callback обработчик ──────────────────────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    db = load_data()

    # ── Клиентские callbacks ──
    if data.startswith("cat_"):
        key = data[4:]
        cat = db["services"][key]
        lines = [f"<b>{cat['name']}</b>\n"]
        for item in cat["items"]:
            lines.append(f"• {item[0]}\n  ⏱ {item[1]} | 💰 {item[2]} руб.")
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
            [InlineKeyboardButton("◀️ Назад к категориям", callback_data="back_cats")],
        ])
        await query.edit_message_text("\n".join(lines), parse_mode="HTML", reply_markup=back_keyboard)

    elif data == "back_cats":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"cat_{k}")]
            for k, v in db["services"].items()
        ])
        await query.edit_message_text("Выбери категорию услуг 👇", reply_markup=keyboard)

    elif data.startswith("master_"):
        idx = int(data[7:])
        m = db["masters"][idx]
        await query.edit_message_text(
            f"<b>{m['name']}</b>\n{m['role']}\n\nНажми кнопку ниже чтобы записаться 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Записаться онлайн", url=DIKIDI_URL)],
                [InlineKeyboardButton("◀️ Назад к мастерам", callback_data="back_masters")]
            ])
        )

    elif data == "back_masters":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"{m['name']} — {m['role']}", callback_data=f"master_{i}")]
             for i, m in enumerate(db["masters"])] +
            [[InlineKeyboardButton("📅 Записаться (выбрать самому)", url=DIKIDI_URL)]]
        )
        await query.edit_message_text(
            "📅 <b>Запись к мастеру</b>\n\nВыбери мастера 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    # ── Админ: мастера ──
    elif data == "addmaster" and is_admin(user_id):
        await query.edit_message_text("➕ Введи имя мастера (например: Иванова Мария):")
        context.user_data["state"] = WAIT_MASTER_NAME

    elif data.startswith("delmaster_") and is_admin(user_id):
        idx = int(data[10:])
        removed = db["masters"].pop(idx)
        save_data(db)
        await query.edit_message_text(f"✅ Мастер <b>{removed['name']}</b> удалён.", parse_mode="HTML")

    # ── Админ: категории услуг ──
    elif data.startswith("admcat_") and is_admin(user_id):
        key = data[7:]
        cat = db["services"][key]
        context.user_data["edit_cat"] = key
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"✏️ {item[0][:30]}...", callback_data=f"edititem_{i}"),
              InlineKeyboardButton("❌", callback_data=f"delitem_{i}")]
             for i, item in enumerate(cat["items"])] +
            [[InlineKeyboardButton("➕ Добавить услугу", callback_data="addservice")],
             [InlineKeyboardButton("◀️ Назад", callback_data="back_admcats")]]
        )
        text = f"<b>{cat['name']}</b>\n\nВыбери услугу для редактирования или удаления:\n\n"
        for i, item in enumerate(cat["items"]):
            text += f"{i+1}. {item[0]} — {item[2]} руб.\n"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)

    elif data == "back_admcats" and is_admin(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(v["name"], callback_data=f"admcat_{k}")]
            for k, v in db["services"].items()
        ])
        await query.edit_message_text(
            "🛎 <b>Управление услугами</b>\n\nВыбери категорию 👇",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif data.startswith("delitem_") and is_admin(user_id):
        idx = int(data[8:])
        key = context.user_data.get("edit_cat")
        removed = db["services"][key]["items"].pop(idx)
        save_data(db)
        await query.edit_message_text(f"✅ Услуга <b>{removed[0]}</b> удалена.", parse_mode="HTML")

    elif data.startswith("edititem_") and is_admin(user_id):
        idx = int(data[9:])
        key = context.user_data.get("edit_cat")
        item = db["services"][key]["items"][idx]
        context.user_data["edit_item_idx"] = idx
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ Название", callback_data="editfield_name")],
            [InlineKeyboardButton("⏱ Длительность", callback_data="editfield_duration")],
            [InlineKeyboardButton("💰 Цена", callback_data="editfield_price")],
        ])
        await query.edit_message_text(
            f"✏️ <b>Редактирование услуги:</b>\n\n"
            f"Название: {item[0]}\nДлительность: {item[1]}\nЦена: {item[2]} руб.\n\nЧто изменить?",
            parse_mode="HTML", reply_markup=keyboard
        )

    elif data.startswith("editfield_") and is_admin(user_id):
        field = data[10:]
        context.user_data["edit_field"] = field
        labels = {"name": "название", "duration": "длительность", "price": "цену"}
        await query.edit_message_text(f"Введи новое {labels[field]}:")
        context.user_data["state"] = WAIT_EDIT_VALUE

    elif data == "addservice" and is_admin(user_id):
        await query.edit_message_text("➕ Введи название новой услуги:")
        context.user_data["state"] = WAIT_SERVICE_NAME

# ─── ConversationHandler через state в user_data ──────────────────────────────
async def handle_state_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    text = update.message.text
    user_id = update.effective_user.id

    if not is_admin(user_id) or state is None:
        await handle_buttons(update, context)
        return

    db = load_data()

    if state == WAIT_MASTER_NAME:
        context.user_data["new_master_name"] = text
        context.user_data["state"] = WAIT_MASTER_ROLE
        await update.message.reply_text("Теперь введи должность мастера:")

    elif state == WAIT_MASTER_ROLE:
        name = context.user_data.get("new_master_name", "")
        db["masters"].append({"name": name, "role": text})
        save_data(db)
        context.user_data["state"] = None
        await update.message.reply_text(
            f"✅ Мастер <b>{name}</b> — {text} добавлен!",
            parse_mode="HTML", reply_markup=admin_keyboard
        )

    elif state == WAIT_SERVICE_NAME:
        context.user_data["new_service_name"] = text
        context.user_data["state"] = WAIT_SERVICE_DURATION
        await update.message.reply_text("Введи длительность (например: 1 час):")

    elif state == WAIT_SERVICE_DURATION:
        context.user_data["new_service_duration"] = text
        context.user_data["state"] = WAIT_SERVICE_PRICE
        await update.message.reply_text("Введи цену (например: 2 000):")

    elif state == WAIT_SERVICE_PRICE:
        key = context.user_data.get("edit_cat")
        name = context.user_data.get("new_service_name")
        duration = context.user_data.get("new_service_duration")
        db["services"][key]["items"].append([name, duration, text])
        save_data(db)
        context.user_data["state"] = None
        await update.message.reply_text(
            f"✅ Услуга <b>{name}</b> добавлена!",
            parse_mode="HTML", reply_markup=admin_keyboard
        )

    elif state == WAIT_EDIT_VALUE:
        key = context.user_data.get("edit_cat")
        idx = context.user_data.get("edit_item_idx")
        field = context.user_data.get("edit_field")
        field_map = {"name": 0, "duration": 1, "price": 2}
        db["services"][key]["items"][idx][field_map[field]] = text
        save_data(db)
        context.user_data["state"] = None
        await update.message.reply_text(
            f"✅ Услуга обновлена!", reply_markup=admin_keyboard
        )

# ─── Запуск ───────────────────────────────────────────────────────────────────
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_state_input))

    print("🤖 Бот запущен.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
