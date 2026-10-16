import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKENINGIZNI_QOYING")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://renderdagi-sayt-manzili.onrender.com")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🦅 O‘yinga kirish (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum! Birds Invest WebApp botiga xush kelibsiz.\n\n"
        "Quyidagi tugmani bosing va o‘yinni boshlang:",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()
