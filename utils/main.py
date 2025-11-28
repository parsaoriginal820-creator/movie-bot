from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import os
from utils.scraper import search_psarips, get_links_from_page

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 سلام! اسم فیلم یا سریال رو بفرست تا برات لینک مستقیم دانلود بدم\n"
        "مثال: Breaking Bad S01E01 یا Inception 2024"
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_chat_action("typing")
    results = search_psarips(query)
    
    if not results:
        await update.message.reply_text("متأسفانه چیزی پیدا نشد 😔\nدوباره با اسم دقیق‌تر امتحان کن")
        return

    keyboard = []
    for res in results:
        btn = InlineKeyboardButton(res["title"][:50], callback_data=f"movie_{res['link']}")
        keyboard.append([btn])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("نتایج جستجو:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("movie_"):
        url = query.data.replace("movie_", "")
        await query.edit_message_text("در حال استخراج لینک‌های مستقیم... ⏳")
        
        links = get_links_from_page(url)
        
        if not links:
            await query.edit_message_text("لینک مستقیمی پیدا نشد 😢")
            return
            
        text = "لینک‌های دانلود مستقیم:\n\n"
        keyboard = []
        for i, link in enumerate(links, 1):
            text += f"{i}. {link}\n\n"
            btn = InlineKeyboardButton(f"لینک {i}", url=link)
            keyboard.append([btn])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

def main():
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # ورسل جدید: به جای VERCEL_URL از دامنه اصلی استفاده می‌کنیم
    webhook_url = f"https://movie-bot-eosin-theta.vercel.app"
    
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path=TOKEN,
        webhook_url=webhook_url + "/" + TOKEN
    )

if __name__ == "__main__":
    main()
