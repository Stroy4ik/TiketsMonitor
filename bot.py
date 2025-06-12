import os
from storage import load_subscriptions, save_subscriptions
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from playbill import get_playbill

# Загрузка підписок
user_subscriptions = load_subscriptions()

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Напиши /subscribe, щоб підписатися на виставу 🎭")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chamber = get_playbill("chamber")
    main = get_playbill("main")

    keyboard = []
    for title in (chamber + main):
        data = f"sub:{title[:50]}"
        if len(data.encode("utf-8")) <= 64:
            keyboard.append([InlineKeyboardButton(title, callback_data=data)])
        else:
            print(f"⚠️ Пропущено занадто довге callback_data: {title}")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть виставу:",
                                    reply_markup=reply_markup)


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    subs = user_subscriptions.get(user_id, [])

    if not subs:
        await update.message.reply_text("У вас немає підписок ❌")
        return

    keyboard = [[
        InlineKeyboardButton(f"❌ {title}", callback_data=f"unsub:{title}")
    ] for title in subs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть виставу для відписки:",
                                    reply_markup=reply_markup)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    uid = str(user_id)
    data = query.data

    if data.startswith("sub:"):
        title = data.split("sub:")[1]
        subs = user_subscriptions.setdefault(uid, [])
        if title not in subs:
            subs.append(title)
            save_subscriptions(user_subscriptions)
            await query.edit_message_text(f"✅ Ви підписались на '{title}'")
        else:
            await query.edit_message_text(f"🔔 Ви вже підписані на '{title}'")

    elif data.startswith("unsub:"):
        title = data.split("unsub:")[1]
        if uid in user_subscriptions and title in user_subscriptions[uid]:
            user_subscriptions[uid].remove(title)
            save_subscriptions(user_subscriptions)
            await query.edit_message_text(f"❎ Ви відписались від '{title}'")
        else:
            await query.edit_message_text(
                "⚠️ Ви не були підписані на цю виставу.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url="https://tiketsmonitor.onrender.com"  # 🔁 заміни на свій Render URL
    )
