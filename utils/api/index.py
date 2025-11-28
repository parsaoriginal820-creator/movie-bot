import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# توکن و دامنه
TOKEN = os.environ["BOT_TOKEN"]
URL = "https://movie-bot-eosin-theta.vercel.app"

# ساخت اپلیکیشن
app = Application.builder().token(TOKEN).build()

# مسیر اسکریپر (چون الان داخل api هستیم)
import sys
sys.path.append('../')
from utils.scraper import search_psarips, get_links_from_page

# هندلرها
async def start(update: Update, context):
    await update.message.reply_text("🎬 سلام! اسم فیلم یا سریال بفرست تا لینک مستقیم بدم\nمثلاً: Oppenheimer")

async def search(update: Update, context):
    query = update.message.text
    await update.message.reply_chat_action("typing")
    results = search_psarips(query)
    if not results:
        await update.message.reply_text("چیزی پیدا نشد 😔")
        return
    keyboard = [[InlineKeyboardButton(r["title"][:60], callback_data=f"m_{r['link']}")] for r in results[:8]]
    await update.message.reply_text("نتایج جستجو:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("m_"):
        url = q.data[2:]
        await q.edit_message_text("در حال استخراج لینک‌ها... ⏳")
        links = get_links_from_page(url)
        if not links:
            await q.edit_message_text("لینک پیدا نشد 😢")
            return
        text = "لینک‌های دانلود مستقیم:\n\n"
        keyboard = []
        for i, l in enumerate(links, 1):
            text += f"{i}. {l}\n\n"
            keyboard.append([InlineKeyboardButton(f"لینک {i}", url=l)])
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(button))

# تابع اصلی ورسل
def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        update = Update.de_json(body, app.bot)
        app.process_update(update)
    except Exception as e:
        print("Error:", e)
    return {"statusCode": 200, "body": "ok"}
