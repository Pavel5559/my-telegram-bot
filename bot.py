import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8946325168:AAHmlWyJmdMoQJdwCYhiXmTMrinPr19ROMc"
ADMIN_ID = 8146780387

users = {}
last_italia = {}
pending_requests = {}

# ───────── START ─────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users.setdefault(uid, {"points": 0})

    kb = [
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("💰 Заработать очки", callback_data="earn")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")],
    ]

    await update.message.reply_text("🇮🇹 Добро пожаловать!", reply_markup=InlineKeyboardMarkup(kb))


# ───────── КНОПКИ ─────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    users.setdefault(uid, {"points": 0})

    data = q.data

    # Профиль
    if data == "profile":
        await q.message.edit_text(
            f"👤 Профиль\n\nID: {uid}\n⭐ Очки: {users[uid]['points']}"
        )

    # Заработок
    elif data == "earn":
        await q.message.edit_text(
            "💰 Задание:\n\n"
            "Напишите 3 сообщения в чате\n"
            "Каждое должно содержать слово ITALIA 🇮🇹\n\n"
            "⏳ Можно раз в 4 часа"
        )

    # Магазин
    elif data == "shop":
        kb = [
            [InlineKeyboardButton("🎡 50⭐ Колесо фортуны", callback_data="wheel")],
            [InlineKeyboardButton("🎥 100⭐ Видео CoderX", callback_data="video")],
            [InlineKeyboardButton("🎁 200⭐ Приз", callback_data="prize")],
        ]
        await q.message.edit_text("🛒 Магазин:", reply_markup=InlineKeyboardMarkup(kb))

    # Колесо
    elif data == "wheel":
        if users[uid]["points"] < 50:
            await q.message.edit_text("❌ Нет очков")
            return

        users[uid]["points"] -= 50

        kb = [[InlineKeyboardButton("🎡 Крутить", callback_data="spin")]]
        await q.message.edit_text("🎡 Колесо куплено!", reply_markup=InlineKeyboardMarkup(kb))

    # Крутить колесо
    elif data == "spin":
        r = random.choice([
            "🎁 Сувенир из Италии",
            "❌ Ничего",
            "💎 Продукт до 4€"
        ])
        await q.message.edit_text(f"🎡 Результат:\n\n{r}")

    # Видео
    elif data == "video":
        if users[uid]["points"] < 100:
            await q.message.edit_text("❌ Нет очков")
            return

        users[uid]["points"] -= 100

        kb = [[InlineKeyboardButton("📩 Отправить заявку", callback_data="req")]]
        await q.message.edit_text(
            "🎥 Вы получили видео от CoderX",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # заявка админу
    elif data == "req":
        pending_requests[uid] = True
        await context.bot.send_message(
            ADMIN_ID,
            f"📩 Заявка от {uid}"
        )
        await q.message.edit_text("📨 Заявка отправлена")

    # приз
    elif data == "prize":
        if users[uid]["points"] < 200:
            await q.message.edit_text("❌ Нет очков")
            return

        users[uid]["points"] -= 200

        r = random.choice([
            "🎁 Продукт до 5€",
            "❌ Ничего"
        ])

        await q.message.edit_text(f"🎁 Результат:\n\n{r}")


# ───────── ГРУППА (ITALIA + COOLDOWN) ─────────
async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.lower()

    if "italia" not in text:
        return

    now = time.time()

    if uid in last_italia and now - last_italia[uid] < 14400:
        await update.message.reply_text("⏳ Подожди 4 часа")
        return

    last_italia[uid] = now

    users.setdefault(uid, {"points": 0})

    gained = random.randint(1, 10)
    users[uid]["points"] += gained

    await update.message.reply_text(f"⭐ +{gained} очков!")


# ───────── АДМИНКА ─────────
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = "👑 USERS:\n\n"

    for uid, data in users.items():
        text += f"ID: {uid} | ⭐ {data['points']}\n"

    text += "\n\nОтправь: ID СУММА"

    await update.message.reply_text(text)


# ───────── НАЧИСЛЕНИЕ ─────────
async def admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        uid, amount = map(int, update.message.text.split())
        users.setdefault(uid, {"points": 0})
        users[uid]["points"] += amount

        await update.message.reply_text("✅ Начислено")
    except:
        pass


# ───────── MAIN ─────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin_add))

    print("BOT STARTED")
    app.run_polling()


if __name__ == "__main__":
    main()