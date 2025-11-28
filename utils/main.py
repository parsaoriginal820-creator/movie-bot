import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from utils.scraper import search_psarips, get_links_from_page

TOKEN = os.environ["BOT_TOKEN"]
URL = "https://movie-bot-eosin-theta.vercel.app"   # ← دامنه خودت

application = Application.builder().token(TOKEN).build()

# هندلرها
async def start(update: Update, context):
    await update.message.reply_text("🎬 سلام!\nاسم فیلم یا سریال رو بفرست تا لینک مستقیم بدم")

async def search(update: Update, context):
    query = update.message.text
    await update.message.reply_chat_action("typing")
    results = search_psarips(query)
    if not results:
        await update.message.reply_text("چیزی پیدا نشد 😔")
        return
    keyboard = [[InlineKeyboardButton(r["title"][:60], callback_data=f"sel_{r['link']}")] for r in results[:10]]
    await update.message.reply_text("نتایج:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("sel_"):
        page_url = q.data[4:]
        await q.edit_message_text("در حال گرفتن لینک‌ها... ⏳")
        links = get_links_from_page(page_url)
        if not links:
            await q.edit_message_text("لینک پیدا نشد 😢")
            return
        text = "لینک‌های دانلود:\n\n"
        keyboard = []
        for i, link in enumerate(links, 1):
            text += f"{i}. {link}\n\n"
            keyboard.append([InlineKeyboardButton(f"لینک {i}", url=link)])
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
application.add_handler(CallbackQueryHandler(button))

# این تابع دقیقاً همون چیزیه که ورسل می‌خواد
async def handler(event, context):
    body = json.loads(event["body"])
    update = Update.de_json(body, application.bot)
    await application.process_update(update)
    return {"statusCode": 200, "body": "ok"}

# ورسل این تابع رو صدا می‌زنه
def main(event, context):
    import asyncio
    return asyncio.get_event_loop().run_until_complete(handler(event, context))
