import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from utils.scraper import search_psarips, get_links_from_page

TOKEN = os.environ.get("BOT_TOKEN")
DOMAIN = "movie-bot-eosin-theta.vercel.app"  # ← دقیقاً همین دامنه خودت

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 سلام! اسم فیلم یا سریال رو بفرست تا لینک مستقیم بدم\n"
        "مثال: Breaking Bad S01E01 یا Oppenheimer"
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_chat_action("typing")
    results = search_psarips(query)
    
    if not results:
        await update.message.reply_text("چیزی پیدا نشد 😔\nبا اسم دقیق‌تر امتحان کن")
        return

    keyboard = [[InlineKeyboardButton(res["title"][:60], callback_data=f"movie_{res['link']}")] for res in results]
    await update.message.reply_text("نتایج جستجو:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("movie_"):
        url = query.data.replace("movie_", "")
        await query.edit_message_text("در حال گرفتن لینک‌ها... ⏳")
        links = get_links_from_page(url)
        
        if not links:
            await query.edit_message_text("لینک مستقیمی پیدا نشد 😢")
            return
            
        text = "لینک‌های دانلود:\n\n"
        keyboard = []
        for i, link in enumerate(links, 1):
            text += f"{i}. {link}\n\n"
            keyboard.append([InlineKeyboardButton(f"لینک {i}", url=link)])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

# این قسمت جدید و مخصوص ورسل هست
def handler(event, context=None):
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # وقتی ورسل درخواست می‌فرسته، این اجرا می‌شه
    return application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path=TOKEN,
        webhook_url=f"https://{DOMAIN}/{TOKEN}",
        event=event
    )
